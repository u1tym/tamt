from pydantic import BaseModel
from datetime import datetime, date

class HolidayBase(BaseModel):
    date: date
    name: str

class HolidayCreate(HolidayBase):
    pass

class HolidayUpdate(HolidayBase):
    pass

class Holiday(HolidayBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
