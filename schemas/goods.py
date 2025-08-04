from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

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