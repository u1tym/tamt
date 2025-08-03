from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

class PaymentSourceBase(BaseModel):
    name: str
    closing_day: int
    pay_month_diff: int
    pay_day: int

class PaymentSourceCreate(PaymentSourceBase):
    pass

class PaymentSource(PaymentSourceBase):
    id: int
    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    used_date: date
    purpose: str
    memo: Optional[str] = None
    amount: float
    payment_source_id: int
    budget_name: Optional[str] = '未分類'

class TransactionCreate(TransactionBase):
    paid_date: Optional[date] = None

class TransactionUpdate(BaseModel):
    used_date: Optional[date] = None
    purpose: Optional[str] = None
    memo: Optional[str] = None
    amount: Optional[float] = None
    payment_source_id: Optional[int] = None
    paid_date: Optional[date] = None
    budget_name: Optional[str] = '未分類'

class Transaction(TransactionBase):
    id: int
    paid_date: date
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class BudgetBase(BaseModel):
    target_year: int
    target_month: int
    name: str
    amount: float
    order_index: int = 0

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    target_year: Optional[int] = None
    target_month: Optional[int] = None
    name: Optional[str] = None
    amount: Optional[float] = None
    order_index: Optional[int] = None

class Budget(BudgetBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class PaymentDateRequest(BaseModel):
    used_date: str
    payment_source_id: int

class MajorCategoryBase(BaseModel):
    name: str
    display_order: int = 0
    is_deleted: bool = False

class MajorCategoryCreate(MajorCategoryBase):
    pass

class MajorCategoryUpdate(BaseModel):
    name: Optional[str] = None
    display_order: Optional[int] = None
    is_deleted: Optional[bool] = None

class MajorCategory(MajorCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class MiddleCategoryBase(BaseModel):
    major_category_id: int
    name: str
    display_order: int = 0
    is_deleted: bool = False

class MiddleCategoryCreate(MiddleCategoryBase):
    pass

class MiddleCategoryUpdate(BaseModel):
    major_category_id: Optional[int] = None
    name: Optional[str] = None
    display_order: Optional[int] = None
    is_deleted: Optional[bool] = None

class MiddleCategory(MiddleCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class KnowhowBase(BaseModel):
    middle_category_id: int
    title: str
    keywords: Optional[str] = None
    content: str
    display_order: int = 0
    is_deleted: bool = False

class KnowhowCreate(KnowhowBase):
    pass

class KnowhowUpdate(BaseModel):
    middle_category_id: Optional[int] = None
    title: Optional[str] = None
    keywords: Optional[str] = None
    content: Optional[str] = None
    display_order: Optional[int] = None
    is_deleted: Optional[bool] = None

class Knowhow(KnowhowBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class KnowhowTreeItem(BaseModel):
    major_category: str
    middle_categories: list[dict]

class KnowhowSearchRequest(BaseModel):
    major_category: Optional[str] = None
    middle_category: Optional[str] = None
    keywords: Optional[str] = None

class UpdateMajorCategoryRequest(BaseModel):
    old_major_category: str
    new_major_category: str

class UpdateMiddleCategoryRequest(BaseModel):
    major_category: str
    old_middle_category: str
    new_middle_category: str

class AddMajorCategoryRequest(BaseModel):
    major_category: str

class AddMiddleCategoryRequest(BaseModel):
    major_category: str
    middle_category: str

# GOODS管理システム用のスキーマ
class PersonBase(BaseModel):
    name: str

class PersonCreate(PersonBase):
    pass

class PersonUpdate(BaseModel):
    name: Optional[str] = None

class Person(PersonBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class ArtistBase(BaseModel):
    name: str

class ArtistCreate(ArtistBase):
    person_ids: List[int] = []  # 所属パーソンのIDリスト

class ArtistUpdate(BaseModel):
    name: Optional[str] = None
    person_ids: Optional[List[int]] = None

class Artist(ArtistBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class ArtistWithPersons(Artist):
    persons: List[Person] = []

class ArtistPersonBase(BaseModel):
    artist_id: int
    person_id: int

class ArtistPersonCreate(ArtistPersonBase):
    pass

class ArtistPerson(ArtistPersonBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class MediaBase(BaseModel):
    name: str

class MediaCreate(MediaBase):
    pass

class MediaUpdate(BaseModel):
    name: Optional[str] = None

class Media(MediaBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class GoodsImageBase(BaseModel):
    image_data: str  # Base64エンコードされた文字列
    image_type: str
    display_order: int = 0

class GoodsImageCreate(GoodsImageBase):
    pass

class GoodsImageUpdate(BaseModel):
    image_data: Optional[str] = None  # Base64エンコードされた文字列
    image_type: Optional[str] = None
    display_order: Optional[int] = None

class GoodsImage(GoodsImageBase):
    id: int
    goods_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class GoodsBase(BaseModel):
    media_id: int
    artist_id: int
    title: str
    release_date: date
    memo: Optional[str] = None
    is_owned: bool = False
    code_number: Optional[str] = None

class GoodsCreate(GoodsBase):
    images: List[GoodsImageCreate] = []

class GoodsUpdate(BaseModel):
    media_id: Optional[int] = None
    artist_id: Optional[int] = None
    title: Optional[str] = None
    release_date: Optional[date] = None
    memo: Optional[str] = None
    is_owned: Optional[bool] = None
    code_number: Optional[str] = None
    images: Optional[List[GoodsImageCreate]] = None

class Goods(GoodsBase):
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    images: List[GoodsImage] = []
    class Config:
        from_attributes = True

class GoodsWithDetails(Goods):
    media: Media
    artist: ArtistWithPersons
    images: List[GoodsImage] = []

# スケジュール管理用のスキーマ
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

# アカウント管理用のスキーマ
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