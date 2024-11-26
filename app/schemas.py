from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str


class UserInDB(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
