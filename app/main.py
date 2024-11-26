from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud, models, schemas, auth
from .database import engine, get_db
from datetime import timedelta
import os

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.post("/auth/register", response_model=schemas.UserInDB)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await crud.create_user(db=db, user=user)


@app.post("/auth/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = auth.create_refresh_token(data={"sub": user.username})
    auth.store_refresh_token(user.id, refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@app.post("/auth/refresh", response_model=schemas.Token)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    try:
        payload = auth.jwt.decode(refresh_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        user = await crud.get_user_by_username(db, username=username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        stored_refresh_token = auth.get_stored_refresh_token(user.id)
        if stored_refresh_token != refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        new_refresh_token = auth.create_refresh_token(data={"sub": user.username})
        auth.store_refresh_token(user.id, new_refresh_token)
        return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}
    except auth.JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@app.post("/tasks", response_model=schemas.Task)
async def create_task(
        task: schemas.TaskCreate,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    return await crud.create_task(db=db, task=task, user_id=current_user.id)


@app.get("/tasks", response_model=list[schemas.Task])
async def read_tasks(
        status: str = None,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    return await crud.get_tasks(db=db, user_id=current_user.id, status=status)


@app.put("/tasks/{task_id}", response_model=schemas.Task)
async def update_task(
        task_id: int,
        task: schemas.TaskCreate,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    db_task = await crud.update_task(db=db, task_id=task_id, task=task, user_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@app.delete("/tasks/{task_id}", response_model=schemas.Task)
async def delete_task(
        task_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    db_task = await crud.delete_task(db=db, task_id=task_id, user_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task
