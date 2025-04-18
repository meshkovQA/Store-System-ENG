# schemas.py
from pydantic import BaseModel
from pydantic import BaseModel, EmailStr
from pydantic.types import constr
from typing import Optional


class UserCreate(BaseModel):
    # Min and max length for name
    name: constr(min_length=3, max_length=60)
    email: EmailStr  # Email should be valid
    # Restrict password length
    password: constr(min_length=6)

    class Config:
        orm_mode = True  # For SQLAlchemy compatibility


class User(BaseModel):
    id: int
    name: str
    email: EmailStr


class Login(BaseModel):  # Model for login
    email: EmailStr
    password: str


# Model for token
class Token(BaseModel):
    access_token: str
    token_type: str


class UserUpdate(BaseModel):
    email: EmailStr  # allow to change email
    name: str   # allow to change name
