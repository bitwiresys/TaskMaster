from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas
from .auth import get_password_hash


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, password_hash=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).filter(models.User.username == username))
    return result.scalars().first()


async def create_task(db: AsyncSession, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(**task.dict(), user_id=user_id)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def get_tasks(db: AsyncSession, user_id: int, status: str = None):
    query = select(models.Task).filter(models.Task.user_id == user_id)
    if status:
        query = query.filter(models.Task.status == status)
    result = await db.execute(query)
    return result.scalars().all()


async def get_task(db: AsyncSession, task_id: int, user_id: int):
    result = await db.execute(select(models.Task).filter(models.Task.id == task_id, models.Task.user_id == user_id))
    return result.scalars().first()


async def update_task(db: AsyncSession, task_id: int, task: schemas.TaskCreate, user_id: int):
    db_task = await get_task(db, task_id, user_id)
    if db_task:
        for key, value in task.dict().items():
            setattr(db_task, key, value)
        await db.commit()
        await db.refresh(db_task)
    return db_task


async def delete_task(db: AsyncSession, task_id: int, user_id: int):
    db_task = await get_task(db, task_id, user_id)
    if db_task:
        await db.delete(db_task)
        await db.commit()
    return db_task
