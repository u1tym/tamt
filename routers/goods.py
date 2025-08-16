from fastapi import APIRouter
from fastapi import Depends, HTTPException, Request

from sqlalchemy.orm import Session

import models
import crud
import schemas

import os
import sys
sys.path.append(os.path.dirname(__file__))
from common import get_db, get_session_info

router = APIRouter()

# GOODS管理システム用のAPIエンドポイント

# Person API
@router.get("/persons", response_model=schemas.ListResponse[schemas.Person])
def read_persons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), request: Request = None):
    persons = crud.get_persons(db, skip=skip, limit=limit)
    session_info = get_session_info(request)
    return schemas.ListResponse(processing_result=True, session_info=session_info, data=persons)

@router.get("/persons/{person_id}", response_model=schemas.BaseResponse[schemas.Person])
def read_person(person_id: int, db: Session = Depends(get_db), request: Request = None):
    person = crud.get_person(db, person_id=person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=person)

@router.post("/persons", response_model=schemas.BaseResponse[schemas.Person])
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db), request: Request = None):
    result = crud.create_person(db=db, person=person)
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=result)

@router.put("/persons/{person_id}", response_model=schemas.BaseResponse[schemas.Person])
def update_person(person_id: int, person: schemas.PersonUpdate, db: Session = Depends(get_db), request: Request = None):
    updated_person = crud.update_person(db=db, person_id=person_id, person=person)
    if updated_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=updated_person)

# Artist API
@router.get("/artists", response_model=schemas.ListResponse[schemas.Artist])
def read_artists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), request: Request = None):
    artists = crud.get_artists(db, skip=skip, limit=limit)
    session_info = get_session_info(request)
    return schemas.ListResponse(processing_result=True, session_info=session_info, data=artists)

@router.get("/artists/{artist_id}", response_model=schemas.BaseResponse[schemas.Artist])
def read_artist(artist_id: int, db: Session = Depends(get_db), request: Request = None):
    artist = crud.get_artist(db, artist_id=artist_id)
    if artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=artist)

@router.get("/artists/{artist_id}/with-persons", response_model=schemas.BaseResponse[schemas.ArtistWithPersons])
def read_artist_with_persons(artist_id: int, db: Session = Depends(get_db), request: Request = None):
    artist_with_persons = crud.get_artist_with_persons(db, artist_id=artist_id)
    if artist_with_persons is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=artist_with_persons)

@router.post("/artists", response_model=schemas.BaseResponse[schemas.Artist])
def create_artist(artist: schemas.ArtistCreate, db: Session = Depends(get_db), request: Request = None):
    result = crud.create_artist(db=db, artist=artist)
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=result)

@router.put("/artists/{artist_id}", response_model=schemas.BaseResponse[schemas.Artist])
def update_artist(artist_id: int, artist: schemas.ArtistUpdate, db: Session = Depends(get_db), request: Request = None):
    updated_artist = crud.update_artist(db=db, artist_id=artist_id, artist=artist)
    if updated_artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=updated_artist)

# Media API
@router.get("/media", response_model=schemas.ListResponse[schemas.Media])
def read_media_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), request: Request = None):
    media_list = crud.get_media_list(db, skip=skip, limit=limit)
    session_info = get_session_info(request)
    return schemas.ListResponse(processing_result=True, session_info=session_info, data=media_list)

@router.get("/media/{media_id}", response_model=schemas.BaseResponse[schemas.Media])
def read_media(media_id: int, db: Session = Depends(get_db), request: Request = None):
    media = crud.get_media(db, media_id=media_id)
    if media is None:
        raise HTTPException(status_code=404, detail="Media not found")
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=media)

@router.post("/media", response_model=schemas.BaseResponse[schemas.Media])
def create_media(media: schemas.MediaCreate, db: Session = Depends(get_db), request: Request = None):
    result = crud.create_media(db=db, media=media)
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=result)

@router.put("/media/{media_id}", response_model=schemas.BaseResponse[schemas.Media])
def update_media(media_id: int, media: schemas.MediaUpdate, db: Session = Depends(get_db), request: Request = None):
    updated_media = crud.update_media(db=db, media_id=media_id, media=media)
    if updated_media is None:
        raise HTTPException(status_code=404, detail="Media not found")
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=updated_media)

# Goods API
@router.get("/goods", response_model=schemas.ListResponse[schemas.Goods])
def read_goods_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), request: Request = None):
    goods = crud.get_goods_list(db, skip=skip, limit=limit)
    session_info = get_session_info(request)
    return schemas.ListResponse(processing_result=True, session_info=session_info, data=goods)

@router.get("/goods/{goods_id}", response_model=schemas.BaseResponse[schemas.Goods])
def read_goods(goods_id: int, db: Session = Depends(get_db), request: Request = None):
    goods = crud.get_goods(db, goods_id=goods_id)
    if goods is None:
        raise HTTPException(status_code=404, detail="Goods not found")
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=goods)

@router.get("/goods/{goods_id}/with-details")
def read_goods_with_details(goods_id: int, db: Session = Depends(get_db)):
    goods_with_details = crud.get_goods_with_details(db, goods_id=goods_id)
    if goods_with_details is None:
        raise HTTPException(status_code=404, detail="Goods not found")
    return goods_with_details

@router.post("/goods", response_model=schemas.BaseResponse[schemas.Goods])
def create_goods(goods: schemas.GoodsCreate, db: Session = Depends(get_db), request: Request = None):
    result = crud.create_goods(db=db, goods=goods)
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=result)

@router.put("/goods/{goods_id}", response_model=schemas.BaseResponse[schemas.Goods])
def update_goods(goods_id: int, goods: schemas.GoodsUpdate, db: Session = Depends(get_db), request: Request = None):
    updated_goods = crud.update_goods(db=db, goods_id=goods_id, goods=goods)
    if updated_goods is None:
        raise HTTPException(status_code=404, detail="Goods not found")
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=updated_goods)

@router.delete("/goods/{goods_id}", response_model=schemas.SimpleResponse)
def delete_goods(goods_id: int, db: Session = Depends(get_db), request: Request = None):
    success = crud.delete_goods(db=db, goods_id=goods_id)
    if not success:
        raise HTTPException(status_code=404, detail="Goods not found")
    session_info = get_session_info(request)
    return schemas.SimpleResponse(processing_result=True, session_info=session_info, message="Goods deleted successfully")

# 画像取得API
@router.get("/goods/{goods_id}/images/{image_id}")
def get_goods_image(goods_id: int, image_id: int, db: Session = Depends(get_db)):
    """GOODS画像を取得"""
    from fastapi.responses import Response
    from fastapi import HTTPException

    goods_image = db.query(models.GoodsImage).filter(
        models.GoodsImage.id == image_id,
        models.GoodsImage.goods_id == goods_id
    ).first()

    if not goods_image:
        raise HTTPException(status_code=404, detail="Image not found")

    return Response(content=goods_image.image_data, media_type=goods_image.image_type)
