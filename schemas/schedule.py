from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ActivityCategoryBase(BaseModel):
    name: str
    is_deleted: bool = False

class ActivityCategoryCreate(ActivityCategoryBase):
    pass

class ActivityCategoryUpdate(BaseModel):
    name: Optional[str] = None
    is_deleted: Optional[bool] = None

class ActivityCategory(ActivityCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class ScheduleBase(BaseModel):
    title: str
    start_datetime: datetime
    duration: int
    is_all_day: bool = False
    activity_category_id: int
    schedule_type: str  # 予定/TODO
    location: Optional[str] = None
    details: Optional[str] = None
    is_todo_completed: bool = False
    is_deleted: bool = False

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    title: Optional[str] = None
    start_datetime: Optional[datetime] = None
    duration: Optional[int] = None
    is_all_day: Optional[bool] = None
    activity_category_id: Optional[int] = None
    schedule_type: Optional[str] = None
    location: Optional[str] = None
    details: Optional[str] = None
    is_todo_completed: Optional[bool] = None
    is_deleted: Optional[bool] = None

class Schedule(ScheduleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class ScheduleWithCategory(Schedule):
    activity_category: ActivityCategory