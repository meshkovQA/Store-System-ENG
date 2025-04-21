# schemas.py
from pydantic import BaseModel
from pydantic import BaseModel, EmailStr, constr, validator, Field
import re
from typing import Optional
from uuid import UUID


class UserCreate(BaseModel):
    name: constr(min_length=3, max_length=50)
    email: EmailStr  # Email должен быть валидным
    password: constr(min_length=8)

    @validator("name")
    def validate_name(cls, value):
        pattern = r'^(?!\s*$)(?!\s).{3,50}$'
        if not re.match(pattern, value):
            raise ValueError("Name contains invalid characters.")
        return value

    @validator("password")
    def validate_name(cls, value):
        pattern = r'^(?!\s*$)(?!\s).{3,50}$'
        if not re.match(pattern, value):
            raise ValueError("Password contains invalid characters.")
        return value

    @validator("email")
    def validate_email(cls, value):
        local_part_pattern = (
            r"^(?!\.)(?!.*\.\.)([a-zA-Z0-9!#$%&'*+/=?^_`{|}~.-]+)(?<!\.)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$"
        )
        if not re.match(local_part_pattern, value):
            raise ValueError("Invalid email format.")
        return value.lower()

    class Config:
        orm_mode = True


class RegistrationResponse(BaseModel):
    message: str = Field("User successfully created",
                         example="User successfully created")
    user_id: str = Field(..., example="uuid-1234-5678-90ab-cdef")
    email: str = Field(..., example="john.doe@example.com")
    name: str = Field(..., example="John Doe")


class User(BaseModel):
    id: UUID
    name: str
    email: EmailStr


class Login(BaseModel):  #
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    message: str = Field("User successfully logged in")
    access_token: str = Field(..., example="your_access_token")
    token_type: str = Field("bearer", example="bearer")


class Token(BaseModel):
    access_token: str
    token_type: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr]

    name: Optional[constr(min_length=3, max_length=50)]

    @validator("name")
    def validate_name(cls, value):

        pattern = r'^(?!\s*$)(?!\s).{3,50}$'
        if not re.match(pattern, value):
            raise ValueError("Name contains invalid characters.")
        return value

    @validator("email")
    def validate_email(cls, value):

        local_part_pattern = (
            r"^(?!\.)(?!.*\.\.)([a-zA-Z0-9!#$%&'*+/=?^_`{|}~.-]+)(?<!\.)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$"
        )
        if not re.match(local_part_pattern, value):
            raise ValueError("Invalid email format.")
        return value.lower()

    class Config:
        orm_mode = True


class UserUpdateResponse(BaseModel):
    detail: str
    user: User


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str

    class Config:
        orm_mode = True
