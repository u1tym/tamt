from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

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
        orm_mode = True

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
        orm_mode = True

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
        orm_mode = True

class PaymentDateRequest(BaseModel):
    used_date: str
    payment_source_id: int

class KnowhowBase(BaseModel):
    major_category: str
    middle_category: str
    title: str
    keywords: Optional[str] = None
    content: str
    display_order: int = 0
    is_deleted: bool = False

class KnowhowCreate(KnowhowBase):
    pass

class KnowhowUpdate(BaseModel):
    major_category: Optional[str] = None
    middle_category: Optional[str] = None
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
        orm_mode = True

class KnowhowTreeItem(BaseModel):
    major_category: str
    middle_categories: list[dict]

class KnowhowSearchRequest(BaseModel):
    major_category: Optional[str] = None
    middle_category: Optional[str] = None
    keywords: Optional[str] = None