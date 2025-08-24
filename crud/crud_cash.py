from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta, timezone
import models
import schemas
from typing import Optional
from .crud_common import calculate_paid_date

# PaymentSource CRUD

def create_payment_source(db: Session, source: schemas.PaymentSourceCreate):
    db_source = models.PaymentSource(**source.model_dump())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

def get_payment_sources(db: Session):
    return db.query(models.PaymentSource).all()

def get_payment_source(db: Session, source_id: int) -> Optional[models.PaymentSource]:
    return db.query(models.PaymentSource).filter(models.PaymentSource.id == source_id).first()

def update_payment_source(db: Session, source_id: int, source: schemas.PaymentSourceCreate):
    db_source = get_payment_source(db, source_id)
    if db_source is None:
        return None

    # データベースのレコードを更新
    for field, value in source.model_dump().items():
        setattr(db_source, field, value)

    db.commit()
    db.refresh(db_source)
    return db_source

def delete_payment_source(db: Session, source_id: int):
    db_source = get_payment_source(db, source_id)
    if db_source is None:
        return False

    db.delete(db_source)
    db.commit()
    return True

# Budget CRUD

def create_budget(db: Session, budget: schemas.BudgetCreate):
    # 新規作成時は最後の順序に追加
    max_order = db.query(func.max(models.Budget.order_index)).filter(
        models.Budget.target_year == budget.target_year,
        models.Budget.target_month == budget.target_month
    ).scalar()

    if max_order is None:
        max_order = 0

    # order_indexを除外してからモデルを作成
    budget_data = budget.model_dump()
    budget_data.pop('order_index', None)  # order_indexを削除
    db_budget = models.Budget(**budget_data, order_index=max_order + 1)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def get_budgets_by_year_month(db: Session, target_year: int, target_month: int):
    return db.query(models.Budget).filter(
        models.Budget.target_year == target_year,
        models.Budget.target_month == target_month
    ).order_by(models.Budget.order_index).all()

def get_budget(db: Session, budget_id: int):
    return db.query(models.Budget).filter(models.Budget.id == budget_id).first()

def update_budget(db: Session, budget_id: int, budget: schemas.BudgetUpdate):
    db_budget = get_budget(db, budget_id)
    if db_budget is None:
        return None

    # 更新データを辞書に変換
    update_data = budget.model_dump(exclude_unset=True)

    # データベースのレコードを更新
    for field, value in update_data.items():
        setattr(db_budget, field, value)

    db.commit()
    db.refresh(db_budget)
    return db_budget

def delete_budget(db: Session, budget_id: int):
    db_budget = get_budget(db, budget_id)
    if db_budget is None:
        return False

    # 削除前に順序を調整
    target_year = db_budget.target_year
    target_month = db_budget.target_month
    deleted_order = db_budget.order_index

    db.delete(db_budget)
    db.commit()

    # 削除された順序より大きい順序を持つ予算の順序を1つずつ減らす
    db.query(models.Budget).filter(
        models.Budget.target_year == target_year,
        models.Budget.target_month == target_month,
        models.Budget.order_index > deleted_order
    ).update({models.Budget.order_index: models.Budget.order_index - 1})
    db.commit()

    return True

def move_budget_up(db: Session, budget_id: int):
    """予算を上に移動"""
    db_budget = get_budget(db, budget_id)
    if db_budget is None or db_budget.order_index <= 0:
        return None

    # 一つ上の予算を取得
    prev_budget = db.query(models.Budget).filter(
        models.Budget.target_year == db_budget.target_year,
        models.Budget.target_month == db_budget.target_month,
        models.Budget.order_index == db_budget.order_index - 1
    ).first()

    if prev_budget:
        # 順序を入れ替え
        prev_budget.order_index = db_budget.order_index
        db_budget.order_index = db_budget.order_index - 1

        db.commit()
        db.refresh(db_budget)
        db.refresh(prev_budget)

    return db_budget

def move_budget_down(db: Session, budget_id: int):
    """予算を下に移動"""
    db_budget = get_budget(db, budget_id)
    if db_budget is None:
        return None

    # 一つ下の予算を取得
    next_budget = db.query(models.Budget).filter(
        models.Budget.target_year == db_budget.target_year,
        models.Budget.target_month == db_budget.target_month,
        models.Budget.order_index == db_budget.order_index + 1
    ).first()

    if next_budget:
        # 順序を入れ替え
        next_budget.order_index = db_budget.order_index
        db_budget.order_index = db_budget.order_index + 1

        db.commit()
        db.refresh(db_budget)
        db.refresh(next_budget)

    return db_budget

def normalize_order_indexes(db: Session, target_year: int, target_month: int):
    """指定年月の予算の順序インデックスを正規化（0から連続した番号に）"""
    budgets = db.query(models.Budget).filter(
        models.Budget.target_year == target_year,
        models.Budget.target_month == target_month
    ).order_by(models.Budget.order_index).all()

    for i, budget in enumerate(budgets):
        budget.order_index = i

    db.commit()
    return budgets

def copy_budgets_from_year_month(db: Session, source_year: int, source_month: int, target_year: int, target_month: int) -> list[models.Budget]:
    """指定された年月の予算を別の年月にコピー"""
    source_budgets = get_budgets_by_year_month(db, source_year, source_month)
    copied_budgets: list[models.Budget] = []

    # コピー先の最大順序を取得
    max_order = db.query(models.Budget).filter(
        models.Budget.target_year == target_year,
        models.Budget.target_month == target_month
    ).with_entities(func.max(models.Budget.order_index)).scalar()

    start_order = (max_order or -1) + 1

    for i, source_budget in enumerate(source_budgets):
        new_budget = models.Budget(
            target_year=target_year,
            target_month=target_month,
            name=source_budget.name,
            amount=source_budget.amount,
            order_index=start_order + i
        )
        db.add(new_budget)
        copied_budgets.append(new_budget)

    db.commit()

    # コピーされた予算のIDを設定
    for budget in copied_budgets:
        db.refresh(budget)

    return copied_budgets

# Transaction CRUD

def create_transaction(db: Session, tx: schemas.TransactionCreate):
    # フロントエンドから支払日が送信されていない場合は自動計算
    if tx.paid_date is None:
        source = get_payment_source(db, tx.payment_source_id)
        if source is None:
            return None
        paid_date = calculate_paid_date(tx.used_date, source.closing_day, source.pay_month_diff, source.pay_day)
    else:
        paid_date = tx.paid_date

    db_tx = models.Transaction(**tx.model_dump(exclude={'paid_date', 'budget_name'}), paid_date=paid_date, budget_name=tx.budget_name or '未分類')
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx

def get_transactions(db: Session, frdt: Optional[date] = None, todt: Optional[date] = None):
    # res = db.query(models.Transaction).offset(skip).limit(limit).all()
    query = db.query(models.Transaction)
    if frdt is not None:
        query = query.filter(models.Transaction.used_date >= frdt)
    if todt is not None:
        query = query.filter(models.Transaction.used_date <= todt)
    res = query.all()
    return res

def get_transaction(db: Session, tx_id: int):
    return db.query(models.Transaction).filter(models.Transaction.id == tx_id).first()

def update_transaction(db: Session, tx_id: int, tx: schemas.TransactionUpdate):
    db_tx = get_transaction(db, tx_id)
    if db_tx is None:
        return None

    # 更新データを辞書に変換
    update_data = tx.model_dump(exclude_unset=True)

    # 支払日の処理
    if 'paid_date' in update_data:
        # フロントエンドから支払日が送信された場合はそれを使用
        paid_date = update_data['paid_date']
    elif 'used_date' in update_data or 'payment_source_id' in update_data:
        # 使用日または支出元が変更された場合は再計算
        source = get_payment_source(db, update_data.get('payment_source_id', db_tx.payment_source_id))
        if source is None:
            return None
        used_date = update_data.get('used_date', db_tx.used_date)
        paid_date = calculate_paid_date(used_date, source.closing_day, source.pay_month_diff, source.pay_day)
        update_data['paid_date'] = paid_date

    # データベースのレコードを更新
    for field, value in update_data.items():
        setattr(db_tx, field, value)
    # budget_nameが未設定なら'未分類'に
    if not getattr(db_tx, 'budget_name', None):
        db_tx.budget_name = '未分類'

    db.commit()
    db.refresh(db_tx)
    return db_tx

def delete_transaction(db: Session, tx_id: int):
    db_tx = get_transaction(db, tx_id)
    if db_tx is None:
        return False

    db.delete(db_tx)
    db.commit()
    return True
