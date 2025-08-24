from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta, timezone
import models
import schemas
from typing import Optional

# ActivityCategory CRUD
def create_activity_category(db: Session, activity_category: schemas.ActivityCategoryCreate):
    """活動区分を作成"""
    db_activity_category = models.ActivityCategory(**activity_category.model_dump())
    db.add(db_activity_category)
    db.commit()
    db.refresh(db_activity_category)
    return db_activity_category

def get_activity_categories(db: Session, skip: int = 0, limit: int = 100):
    """活動区分一覧を取得"""
    return db.query(models.ActivityCategory).filter(
        models.ActivityCategory.is_deleted == False
    ).order_by(models.ActivityCategory.name).offset(skip).limit(limit).all()

def get_activity_category(db: Session, activity_category_id: int):
    """特定の活動区分を取得"""
    return db.query(models.ActivityCategory).filter(
        models.ActivityCategory.id == activity_category_id,
        models.ActivityCategory.is_deleted == False
    ).first()

def update_activity_category(db: Session, activity_category_id: int, activity_category: schemas.ActivityCategoryUpdate):
    """活動区分を更新"""
    db_activity_category = get_activity_category(db, activity_category_id)
    if db_activity_category is None:
        return None

    update_data = activity_category.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_activity_category, field, value)

    db.commit()
    db.refresh(db_activity_category)
    return db_activity_category

def delete_activity_category(db: Session, activity_category_id: int):
    """活動区分を削除（論理削除）"""
    db_activity_category = get_activity_category(db, activity_category_id)
    if db_activity_category is None:
        return False

    # 活動区分を論理削除
    db_activity_category.is_deleted = True

    # 関連するスケジュールも論理削除
    db.query(models.Schedule).filter(
        models.Schedule.activity_category_id == activity_category_id
    ).update({models.Schedule.is_deleted: True})

    db.commit()
    return True

# Schedule CRUD
def create_schedule(db: Session, schedule: schemas.ScheduleCreate):
    """スケジュールを作成"""
    db_schedule = models.Schedule(**schedule.model_dump())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def get_schedules(db: Session, skip: int = 0, limit: int = 100):
    """スケジュール一覧を取得"""
    return db.query(models.Schedule).filter(
        models.Schedule.is_deleted == False
    ).order_by(models.Schedule.start_datetime).offset(skip).limit(limit).all()

def get_schedules_by_month(db: Session, year: int, month: int):
    """指定月のスケジュールを取得（指定年月の1日-7日前から指定年月の末日+7日後まで）"""
    from datetime import datetime, timedelta
    from calendar import monthrange

    # 指定月の最初の日と最後の日を取得
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, monthrange(year, month)[1], 23, 59, 59)

    # 期間を拡張：1日-7日前から末日+7日後まで
    start_date = first_day - timedelta(days=7)
    end_date = last_day + timedelta(days=7)

    return db.query(models.Schedule).filter(
        models.Schedule.is_deleted == False,
        models.Schedule.start_datetime >= start_date,
        models.Schedule.start_datetime <= end_date
    ).order_by(models.Schedule.start_datetime).all()

def get_schedules_by_date_range(db: Session, start_date: datetime, end_date: datetime) -> list[models.Schedule]:
    """指定期間のスケジュールを取得"""
    # まず、指定期間の終了時刻より前に開始するすべてのスケジュールを取得
    schedules = db.query(models.Schedule).filter(
        models.Schedule.is_deleted == False,
        models.Schedule.start_datetime < end_date
    ).order_by(models.Schedule.start_datetime).all()

    # Python側で重複判定を行う
    result: list[models.Schedule] = []
    for schedule in schedules:
        # 終日スケジュールの場合は常に含める
        if schedule.is_all_day:
            result.append(schedule)
            continue

        # 時間指定スケジュールの場合、終了時刻を計算
        end_datetime = schedule.start_datetime + timedelta(minutes=schedule.duration)

        # スケジュールの終了時刻が指定期間の開始時刻より後にある場合
        if end_datetime > start_date:
            result.append(schedule)

    return result

def get_schedule(db: Session, schedule_id: int):
    """特定のスケジュールを取得"""
    return db.query(models.Schedule).filter(
        models.Schedule.id == schedule_id,
        models.Schedule.is_deleted == False
    ).first()

def get_schedule_with_category(db: Session, schedule_id: int):
    """活動区分情報を含むスケジュールを取得"""
    return db.query(models.Schedule).join(
        models.ActivityCategory
    ).filter(
        models.Schedule.id == schedule_id,
        models.Schedule.is_deleted == False
    ).first()

def update_schedule(db: Session, schedule_id: int, schedule: schemas.ScheduleUpdate):
    """スケジュールを更新"""
    db_schedule = get_schedule(db, schedule_id)
    if db_schedule is None:
        return None

    update_data = schedule.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_schedule, field, value)

    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def delete_schedule(db: Session, schedule_id: int):
    """スケジュールを削除（論理削除）"""
    db_schedule = get_schedule(db, schedule_id)
    if db_schedule is None:
        return False

    db_schedule.is_deleted = True
    db.commit()
    return True

def get_schedules_by_activity_categories(db: Session, activity_category_ids: list[int], year: int, month: int):
    """指定された活動区分のスケジュールを取得（指定年月の1日-7日前から指定年月の末日+7日後まで）"""
    from datetime import datetime, timedelta
    from calendar import monthrange

    # 指定月の最初の日と最後の日を取得
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, monthrange(year, month)[1], 23, 59, 59)

    # 期間を拡張：1日-7日前から末日+7日後まで
    start_date = first_day - timedelta(days=7)
    end_date = last_day + timedelta(days=7)

    return db.query(models.Schedule).filter(
        models.Schedule.is_deleted == False,
        models.Schedule.activity_category_id.in_(activity_category_ids),
        models.Schedule.start_datetime >= start_date,
        models.Schedule.start_datetime <= end_date
    ).order_by(models.Schedule.start_datetime).all()
