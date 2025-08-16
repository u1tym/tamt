from fastapi import APIRouter
from fastapi import Depends, HTTPException, Request

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from datetime import date, timedelta

import models
import schemas

import os
import sys
sys.path.append(os.path.dirname(__file__))
from common import get_db, get_session_info

router = APIRouter()

# 休日管理のエンドポイント
@router.get("/holidays", response_model=schemas.ListResponse[schemas.Holiday])
def get_holidays(db: Session = Depends(get_db), request: Request = None):
    holidays = db.query(models.Holiday).order_by(models.Holiday.date).all()
    session_info = get_session_info(request)
    return schemas.ListResponse(processing_result=True, session_info=session_info, data=holidays)

@router.get("/holidays/month/{year}/{month}", response_model=schemas.ListResponse[schemas.Holiday])
def get_holidays_by_month(year: int, month: int, db: Session = Depends(get_db), request: Request = None):
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    holidays = db.query(models.Holiday).filter(
        models.Holiday.date >= start_date,
        models.Holiday.date <= end_date
    ).order_by(models.Holiday.date).all()
    session_info = get_session_info(request)
    return schemas.ListResponse(processing_result=True, session_info=session_info, data=holidays)

@router.post("/holidays", response_model=schemas.BaseResponse[schemas.Holiday])
def create_holiday(holiday: schemas.HolidayCreate, db: Session = Depends(get_db), request: Request = None):
    db_holiday = models.Holiday(**holiday.dict())
    db.add(db_holiday)
    try:
        db.commit()
        db.refresh(db_holiday)
        session_info = get_session_info(request)
        return schemas.BaseResponse(processing_result=True, session_info=session_info, data=db_holiday)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="この日付は既に休日として登録されています")

@router.put("/holidays/{holiday_id}", response_model=schemas.BaseResponse[schemas.Holiday])
def update_holiday(holiday_id: int, holiday: schemas.HolidayUpdate, db: Session = Depends(get_db), request: Request = None):
    db_holiday = db.query(models.Holiday).filter(models.Holiday.id == holiday_id).first()
    if not db_holiday:
        raise HTTPException(status_code=404, detail="休日が見つかりません")

    for key, value in holiday.dict().items():
        setattr(db_holiday, key, value)

    try:
        db.commit()
        db.refresh(db_holiday)
        session_info = get_session_info(request)
        return schemas.BaseResponse(processing_result=True, session_info=session_info, data=db_holiday)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="この日付は既に休日として登録されています")

@router.delete("/holidays/{holiday_id}", response_model=schemas.SimpleResponse)
def delete_holiday(holiday_id: int, db: Session = Depends(get_db), request: Request = None):
    db_holiday = db.query(models.Holiday).filter(models.Holiday.id == holiday_id).first()
    if not db_holiday:
        raise HTTPException(status_code=404, detail="休日が見つかりません")

    db.delete(db_holiday)
    db.commit()
    session_info = get_session_info(request)
    return schemas.SimpleResponse(processing_result=True, session_info=session_info, message="休日を削除しました")
