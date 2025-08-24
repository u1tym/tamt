from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta, timezone
import models
import schemas
from typing import Optional

# アカウント管理用のCRUD操作
def create_account(db: Session, account: schemas.AccountCreate):
    db_account = models.Account(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_accounts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Account).filter(
        models.Account.is_deleted == False
    ).offset(skip).limit(limit).all()

def get_account(db: Session, account_id: int):
    return db.query(models.Account).filter(
        models.Account.id == account_id,
        models.Account.is_deleted == False
    ).first()

def get_account_by_username(db: Session, username: str):
    return db.query(models.Account).filter(
        models.Account.username == username,
        models.Account.is_deleted == False
    ).first()

def update_account(db: Session, account_id: int, account: schemas.AccountUpdate):
    db_account = get_account(db, account_id)
    if db_account is None:
        return None

    update_data = account.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_account, field, value)

    db.commit()
    db.refresh(db_account)
    return db_account

def delete_account(db: Session, account_id: int):
    db_account = get_account(db, account_id)
    if db_account is None:
        return False

    # 論理削除
    db_account.is_deleted = True
    db.commit()
    return True

def authenticate_user(db: Session, username: str, password: str):
    """ユーザー認証"""
    account = get_account_by_username(db, username)
    if account is None:
        return None

    # パスワードの検証（実際の運用ではハッシュ化して比較）
    if account.password == password:
        # 最終アクセス日時を更新
        account.last_access = datetime.now(timezone.utc)
        db.commit()
        return account

    return None

def update_session_info(db: Session, account_id: int, session_info: str):
    """セッション情報を更新"""
    db_account = get_account(db, account_id)
    if db_account is None:
        return False

    db_account.session_info = session_info
    db_account.last_access = datetime.now(timezone.utc)
    db.commit()
    return True

def update_random_number(db: Session, account_id: int, random_number: int):
    """ランダム数を更新"""
    db_account = get_account(db, account_id)
    if db_account is None:
        return False

    db_account.random_number = random_number
    db_account.last_access = datetime.now(timezone.utc)
    db.commit()
    return True
