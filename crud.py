from sqlalchemy.orm import Session
from datetime import date, timedelta
import models
import schemas

# 支払日自動計算
def calculate_paid_date(used_date: date, closing_day: int, pay_month_diff: int, pay_day: int) -> date:
    if closing_day == 0:
        # 現金などは使用日が支払日
        return used_date
    # 締め日をまたいでいるか判定
    if used_date.day > closing_day:
        # 翌月の支払い
        month = used_date.month + 1
        year = used_date.year
        if month > 12:
            month = 1
            year += 1
    else:
        month = used_date.month
        year = used_date.year
    # 支払い月までの差分を加算
    month += pay_month_diff
    while month > 12:
        month -= 12
        year += 1
    paid_date = date(year, month, pay_day if pay_day > 0 else used_date.day)
    return paid_date

# PaymentSource CRUD

def create_payment_source(db: Session, source: schemas.PaymentSourceCreate):
    db_source = models.PaymentSource(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

def get_payment_sources(db: Session):
    return db.query(models.PaymentSource).all()

def get_payment_source(db: Session, source_id: int):
    return db.query(models.PaymentSource).filter(models.PaymentSource.id == source_id).first()

# Transaction CRUD

def create_transaction(db: Session, tx: schemas.TransactionCreate):
    source = get_payment_source(db, tx.payment_source_id)
    paid_date = calculate_paid_date(tx.used_date, source.closing_day, source.pay_month_diff, source.pay_day)
    db_tx = models.Transaction(**tx.dict(), paid_date=paid_date)
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).offset(skip).limit(limit).all()

def get_transaction(db: Session, tx_id: int):
    return db.query(models.Transaction).filter(models.Transaction.id == tx_id).first()