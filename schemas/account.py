from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AccountBase(BaseModel):
    username: str
    password: str
    session_info: Optional[str] = None
    last_access: Optional[datetime] = None
    is_deleted: bool = False
    random_number: Optional[int] = None

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    session_info: Optional[str] = None
    last_access: Optional[datetime] = None
    is_deleted: Optional[bool] = None
    random_number: Optional[int] = None

class Account(AccountBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    session_token: Optional[str] = None

class RandomNumberResponse(BaseModel):
    success: bool
    random_number: int
    message: str

class LoginVerifyRequest(BaseModel):
    username: str
    hash_value: str