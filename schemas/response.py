from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List, Any
from datetime import datetime

T = TypeVar('T')

class SessionInfo(BaseModel):
    username: str
    session_token: str

class BaseResponse(BaseModel, Generic[T]):
    processing_result: bool = True
    session_info: SessionInfo
    data: T

class ListResponse(BaseModel, Generic[T]):
    processing_result: bool = True
    session_info: SessionInfo
    data: List[T]

class SimpleResponse(BaseModel):
    processing_result: bool = True
    session_info: SessionInfo
    message: str 