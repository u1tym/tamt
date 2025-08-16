from fastapi import APIRouter
from fastapi import Depends, HTTPException, Request

import os
import sys
sys.path.append(os.path.dirname(__file__))
from common import get_db, get_session_info
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

import crud
import schemas

router = APIRouter()

# スケジュール管理用のAPIエンドポイント

# ActivityCategory API
@router.get("/activity-categories", response_model=schemas.ListResponse[schemas.ActivityCategory])
def read_activity_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), request: Request = None):
    """活動区分一覧を取得"""
    activity_categories = crud.get_activity_categories(db, skip=skip, limit=limit)
    session_info = get_session_info(request)
    return schemas.ListResponse(processing_result=True, session_info=session_info, data=activity_categories)

@router.get("/activity-categories/{activity_category_id}", response_model=schemas.ActivityCategory)
def read_activity_category(activity_category_id: int, db: Session = Depends(get_db)):
    """特定の活動区分を取得"""
    db_activity_category = crud.get_activity_category(db, activity_category_id=activity_category_id)
    if db_activity_category is None:
        raise HTTPException(status_code=404, detail="Activity category not found")
    return db_activity_category

@router.post("/activity-categories", response_model=schemas.BaseResponse[schemas.ActivityCategory])
def create_activity_category(activity_category: schemas.ActivityCategoryCreate, db: Session = Depends(get_db), request: Request = None):
    """活動区分を作成"""
    result = crud.create_activity_category(db=db, activity_category=activity_category)
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=result)

@router.put("/activity-categories/{activity_category_id}", response_model=schemas.BaseResponse[schemas.ActivityCategory])
def update_activity_category(activity_category_id: int, activity_category: schemas.ActivityCategoryUpdate, db: Session = Depends(get_db), request: Request = None):
    """活動区分を更新"""
    db_activity_category = crud.update_activity_category(db, activity_category_id=activity_category_id, activity_category=activity_category)
    if db_activity_category is None:
        raise HTTPException(status_code=404, detail="Activity category not found")
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=db_activity_category)

@router.delete("/activity-categories/{activity_category_id}", response_model=schemas.SimpleResponse)
def delete_activity_category(activity_category_id: int, db: Session = Depends(get_db), request: Request = None):
    """活動区分を削除"""
    success = crud.delete_activity_category(db, activity_category_id=activity_category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Activity category not found")
    session_info = get_session_info(request)
    return schemas.SimpleResponse(processing_result=True, session_info=session_info, message="Activity category deleted successfully")

# Schedule API
@router.get("/schedules", response_model=schemas.ListResponse[schemas.Schedule])
def read_schedules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), request: Request = None):
    """スケジュール一覧を取得"""
    schedules = crud.get_schedules(db, skip=skip, limit=limit)
    session_info = get_session_info(request)
    return schemas.ListResponse(processing_result=True, session_info=session_info, data=schedules)

@router.get("/schedules/month/{year}/{month}", response_model=schemas.ListResponse[schemas.ScheduleWithCategory])
def read_schedules_by_month(year: int, month: int, db: Session = Depends(get_db), request: Request = None):
    """指定月のスケジュールを取得"""
    schedules = crud.get_schedules_by_month(db, year=year, month=month)
    result = []
    for schedule in schedules:
        category = crud.get_activity_category(db, schedule.activity_category_id)
        schedule_dict = {
            'id': schedule.id,
            'title': schedule.title,
            'start_datetime': schedule.start_datetime,
            'duration': schedule.duration,
            'is_all_day': schedule.is_all_day,
            'activity_category_id': schedule.activity_category_id,
            'schedule_type': schedule.schedule_type,
            'location': schedule.location,
            'details': schedule.details,
            'is_todo_completed': schedule.is_todo_completed,
            'is_deleted': schedule.is_deleted,
            'created_at': schedule.created_at,
            'updated_at': schedule.updated_at,
            'activity_category': category
        }
        result.append(schedule_dict)
    session_info = get_session_info(request)
    return schemas.ListResponse(processing_result=True, session_info=session_info, data=result)

@router.get("/schedules/filtered/{year}/{month}")
def read_schedules_by_activity_categories(year: int, month: int, category_ids: str, db: Session = Depends(get_db)):
    """指定された活動区分のスケジュールを取得"""
    if not category_ids:
        return []

    category_id_list = [int(id.strip()) for id in category_ids.split(',') if id.strip()]
    schedules = crud.get_schedules_by_activity_categories(db, category_id_list, year, month)
    result = []
    for schedule in schedules:
        category = crud.get_activity_category(db, schedule.activity_category_id)
        schedule_dict = {
            'id': schedule.id,
            'title': schedule.title,
            'start_datetime': schedule.start_datetime,
            'duration': schedule.duration,
            'is_all_day': schedule.is_all_day,
            'activity_category_id': schedule.activity_category_id,
            'schedule_type': schedule.schedule_type,
            'location': schedule.location,
            'details': schedule.details,
            'is_todo_completed': schedule.is_todo_completed,
            'is_deleted': schedule.is_deleted,
            'created_at': schedule.created_at,
            'updated_at': schedule.updated_at,
            'activity_category': category
        }
        result.append(schedule_dict)
    return result

@router.get("/schedules/week/{start_date}", response_model=schemas.ListResponse[schemas.ScheduleWithCategory])
def read_schedules_by_week(start_date: str, db: Session = Depends(get_db), request: Request = None):
    """指定週のスケジュールを取得"""
    try:
        # start_dateは "YYYY-MM-DD" 形式
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = start_datetime + timedelta(days=7)

        schedules = crud.get_schedules_by_date_range(db, start_datetime, end_datetime)
        result = []
        for schedule in schedules:
            category = crud.get_activity_category(db, schedule.activity_category_id)
            schedule_dict = {
                'id': schedule.id,
                'title': schedule.title,
                'start_datetime': schedule.start_datetime,
                'duration': schedule.duration,
                'is_all_day': schedule.is_all_day,
                'activity_category_id': schedule.activity_category_id,
                'schedule_type': schedule.schedule_type,
                'location': schedule.location,
                'details': schedule.details,
                'is_todo_completed': schedule.is_todo_completed,
                'is_deleted': schedule.is_deleted,
                'created_at': schedule.created_at,
                'updated_at': schedule.updated_at,
                'activity_category': category
            }
            result.append(schedule_dict)
        session_info = get_session_info(request)
        return schemas.ListResponse(processing_result=True, session_info=session_info, data=result)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

@router.get("/schedules/{schedule_id}", response_model=schemas.ScheduleWithCategory)
def read_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """特定のスケジュールを取得"""
    schedule = crud.get_schedule(db, schedule_id=schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")

    category = crud.get_activity_category(db, schedule.activity_category_id)
    return {
        'id': schedule.id,
        'title': schedule.title,
        'start_datetime': schedule.start_datetime,
        'duration': schedule.duration,
        'is_all_day': schedule.is_all_day,
        'activity_category_id': schedule.activity_category_id,
        'schedule_type': schedule.schedule_type,
        'location': schedule.location,
        'details': schedule.details,
        'is_todo_completed': schedule.is_todo_completed,
        'is_deleted': schedule.is_deleted,
        'created_at': schedule.created_at,
        'updated_at': schedule.updated_at,
        'activity_category': category
    }

@router.post("/schedules", response_model=schemas.BaseResponse[schemas.Schedule])
def create_schedule(schedule: schemas.ScheduleCreate, db: Session = Depends(get_db), request: Request = None):
    """スケジュールを作成"""
    result = crud.create_schedule(db=db, schedule=schedule)
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=result)

@router.put("/schedules/{schedule_id}", response_model=schemas.BaseResponse[schemas.Schedule])
def update_schedule(schedule_id: int, schedule: schemas.ScheduleUpdate, db: Session = Depends(get_db), request: Request = None):
    """スケジュールを更新"""
    db_schedule = crud.update_schedule(db, schedule_id=schedule_id, schedule=schedule)
    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=db_schedule)

@router.delete("/schedules/{schedule_id}", response_model=schemas.SimpleResponse)
def delete_schedule(schedule_id: int, db: Session = Depends(get_db), request: Request = None):
    """スケジュールを削除"""
    success = crud.delete_schedule(db, schedule_id=schedule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    session_info = get_session_info(request)
    return schemas.SimpleResponse(processing_result=True, session_info=session_info, message="Schedule deleted successfully")
