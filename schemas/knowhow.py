from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

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