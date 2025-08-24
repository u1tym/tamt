from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta, timezone
import models
import schemas
from typing import Optional, TypedDict
from .crud_common import resize_image

class ArtistWithPerson(TypedDict):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    persons: list[models.Person]

class GoodsWithDetail(TypedDict):
    id: int
    media_id: int
    artist_id: int
    title: str
    release_date: date
    memo: str
    is_owned: bool
    code_number: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    media: models.Media
    artist: ArtistWithPerson
    images: list[models.GoodsImage]

# Person CRUD
def create_person(db: Session, person: schemas.PersonCreate):
    db_person = models.Person(**person.model_dump())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

def get_persons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Person).order_by(models.Person.name).offset(skip).limit(limit).all()

def get_person(db: Session, person_id: int):
    return db.query(models.Person).filter(models.Person.id == person_id).first()

def update_person(db: Session, person_id: int, person: schemas.PersonUpdate):
    db_person = get_person(db, person_id)
    if db_person is None:
        return None

    update_data = person.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_person, field, value)

    db.commit()
    db.refresh(db_person)
    return db_person

# Artist CRUD
def create_artist(db: Session, artist: schemas.ArtistCreate):
    db_artist = models.Artist(name=artist.name)
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)

    # パーソンの関連付け
    for person_id in artist.person_ids:
        artist_person = models.ArtistPerson(
            artist_id=db_artist.id,
            person_id=person_id
        )
        db.add(artist_person)

    db.commit()
    db.refresh(db_artist)
    return db_artist

def get_artists(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Artist).order_by(models.Artist.name).offset(skip).limit(limit).all()

def get_artist(db: Session, artist_id: int):
    return db.query(models.Artist).filter(models.Artist.id == artist_id).first()

def get_artist_with_persons(db: Session, artist_id: int) -> Optional[ArtistWithPerson]:
    """パーソン情報を含むアーティストを取得"""
    artist = get_artist(db, artist_id)
    if artist is None:
        return None

    # パーソン情報を取得
    persons = db.query(models.Person).join(models.ArtistPerson).filter(
        models.ArtistPerson.artist_id == artist_id
    ).all()

    result: ArtistWithPerson = {
        'id': artist.id,
        'name': artist.name,
        'created_at': artist.created_at,
        'updated_at': artist.updated_at,
        'persons': persons
    }
    return result

def update_artist(db: Session, artist_id: int, artist: schemas.ArtistUpdate):
    db_artist = get_artist(db, artist_id)
    if db_artist is None:
        return None

    update_data = artist.model_dump(exclude_unset=True)

    # 名前の更新
    if 'name' in update_data:
        db_artist.name = update_data['name']

    # パーソンの関連付けを更新
    if 'person_ids' in update_data:
        # 既存の関連付けを削除
        db.query(models.ArtistPerson).filter(
            models.ArtistPerson.artist_id == artist_id
        ).delete()

        # 新しい関連付けを作成
        for person_id in update_data['person_ids']:
            artist_person = models.ArtistPerson(
                artist_id=artist_id,
                person_id=person_id
            )
            db.add(artist_person)

    db.commit()
    db.refresh(db_artist)
    return db_artist

# Media CRUD
def create_media(db: Session, media: schemas.MediaCreate):
    db_media = models.Media(**media.model_dump())
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media

def get_media_list(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Media).order_by(models.Media.name).offset(skip).limit(limit).all()

def get_media(db: Session, media_id: int) -> Optional[models.Media]:
    return db.query(models.Media).filter(models.Media.id == media_id).first()

def update_media(db: Session, media_id: int, media: schemas.MediaUpdate):
    db_media = get_media(db, media_id)
    if db_media is None:
        return None

    update_data = media.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_media, field, value)

    db.commit()
    db.refresh(db_media)
    return db_media

# Goods CRUD
def create_goods(db: Session, goods: schemas.GoodsCreate):
    db_goods = models.Goods(
        media_id=goods.media_id,
        artist_id=goods.artist_id,
        title=goods.title,
        release_date=goods.release_date,
        memo=goods.memo,
        is_owned=goods.is_owned,
        code_number=goods.code_number
    )
    db.add(db_goods)
    db.commit()
    db.refresh(db_goods)

    # 画像の保存
    saved_images = []
    for i, image_data in enumerate(goods.images):
        # Base64デコードしてバイトデータに変換
        import base64
        decoded_image = base64.b64decode(image_data.image_data)
        # 画像をリサイズ
        resized_image = resize_image(decoded_image)

        goods_image = models.GoodsImage(
            goods_id=db_goods.id,
            image_data=resized_image,
            image_type=image_data.image_type,
            display_order=i
        )
        db.add(goods_image)
        saved_images.append(goods_image)

    db.commit()

    # 保存された画像をBase64エンコードして返す
    for img in saved_images:
        db.refresh(img)
        img.image_data = base64.b64encode(img.image_data).decode('utf-8')

    # GOODSオブジェクトに画像情報を追加
    db_goods.images = saved_images

    return db_goods

def get_goods_list(db: Session, skip: int = 0, limit: int = 100):
    goods_list = db.query(models.Goods).filter(
        models.Goods.is_deleted == False
    ).order_by(models.Goods.release_date.desc()).offset(skip).limit(limit).all()

    # 各GOODSに画像情報を追加（Base64エンコード）
    import base64
    result = []
    for goods in goods_list:
        # 基本情報を辞書に変換
        goods_dict = {
            'id': goods.id,
            'media_id': goods.media_id,
            'artist_id': goods.artist_id,
            'title': goods.title,
            'release_date': goods.release_date,
            'memo': goods.memo,
            'is_owned': goods.is_owned,
            'code_number': goods.code_number,
            'is_deleted': goods.is_deleted,
            'created_at': goods.created_at,
            'updated_at': goods.updated_at,
            'images': []
        }

        # 画像情報を取得してBase64エンコード
        images = db.query(models.GoodsImage).filter(
            models.GoodsImage.goods_id == goods.id
        ).order_by(models.GoodsImage.display_order).all()

        for img in images:
            goods_dict['images'].append({
                'id': img.id,
                'goods_id': img.goods_id,
                'image_data': base64.b64encode(img.image_data).decode('utf-8'),
                'image_type': img.image_type,
                'display_order': img.display_order,
                'created_at': img.created_at
            })

        result.append(goods_dict)

    return result

def get_goods(db: Session, goods_id: int) -> Optional[models.Goods]:
    return db.query(models.Goods).filter(
        models.Goods.id == goods_id,
        models.Goods.is_deleted == False
    ).first()

def get_goods_with_details(db: Session, goods_id: int) -> Optional[GoodsWithDetail]:
    """詳細情報を含むGOODSを取得"""
    goods = get_goods(db, goods_id)
    if goods is None:
        return None

    # メディア情報を取得
    media = get_media(db, goods.media_id)
    if media is None:
        return None

    # アーティスト情報を取得（パーソン情報含む）
    artist_with_persons = get_artist_with_persons(db, goods.artist_id)
    if artist_with_persons is None:
        return None

    # 画像情報を取得
    images = db.query(models.GoodsImage).filter(
        models.GoodsImage.goods_id == goods_id
    ).order_by(models.GoodsImage.display_order).all()

    result: GoodsWithDetail = {
        'id': goods.id,
        'media_id': goods.media_id,
        'artist_id': goods.artist_id,
        'title': goods.title,
        'release_date': goods.release_date,
        'memo': goods.memo,
        'is_owned': goods.is_owned,
        'code_number': goods.code_number,
        'is_deleted': goods.is_deleted,
        'created_at': goods.created_at,
        'updated_at': goods.updated_at,
        'media': media,
        'artist': artist_with_persons,
        'images': images
    }
    return result

def update_goods(db: Session, goods_id: int, goods: schemas.GoodsUpdate):
    db_goods = get_goods(db, goods_id)
    if db_goods is None:
        return None

    update_data = goods.model_dump(exclude_unset=True)

    # 基本情報の更新
    for field in ['media_id', 'artist_id', 'title', 'release_date', 'memo', 'is_owned', 'code_number']:
        if field in update_data:
            setattr(db_goods, field, update_data[field])

    # 画像の更新
    saved_images: list[models.GoodsImage] = []
    if 'images' in update_data:
        # 既存の画像を削除
        db.query(models.GoodsImage).filter(
            models.GoodsImage.goods_id == goods_id
        ).delete()

        # 新しい画像を保存
        for i, image_data in enumerate(update_data['images']):
            # Base64デコードしてバイトデータに変換
            import base64
            decoded_image = base64.b64decode(image_data['image_data'])
            # 画像をリサイズ
            resized_image = resize_image(decoded_image)

            goods_image = models.GoodsImage(
                goods_id=goods_id,
                image_data=resized_image,
                image_type=image_data['image_type'],
                display_order=i
            )
            db.add(goods_image)
            saved_images.append(goods_image)

    db.commit()

    # 保存された画像をBase64エンコードして返す
    for img in saved_images:
        db.refresh(img)
        img.image_data = base64.b64encode(img.image_data).decode('utf-8')

    # GOODSオブジェクトに画像情報を追加
    db_goods.images = saved_images

    return db_goods

def delete_goods(db: Session, goods_id: int):
    db_goods = get_goods(db, goods_id)
    if db_goods is None:
        return False

    # 論理削除
    db_goods.is_deleted = True
    db.commit()
    return True
