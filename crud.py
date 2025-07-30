from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
import models
import schemas

# 支払日自動計算
def calculate_paid_date(used_date: date, closing_day: int, pay_month_diff: int, pay_day: int) -> date:
    print(f"DEBUG: calculate_paid_date called with used_date: {used_date}, closing_day: {closing_day}, pay_month_diff: {pay_month_diff}, pay_day: {pay_day}")

    if closing_day == 0:
        # 現金などは使用日が支払日
        print(f"DEBUG: closing_day is 0, returning used_date: {used_date}")
        return used_date

    # 締め日をまたいでいるか判定
    if used_date.day > closing_day:
        # 翌月の支払い
        month = used_date.month + 1
        year = used_date.year
        if month > 12:
            month = 1
            year += 1
        print(f"DEBUG: Used date day ({used_date.day}) > closing_day ({closing_day}), using next month")
    else:
        month = used_date.month
        year = used_date.year
        print(f"DEBUG: Used date day ({used_date.day}) <= closing_day ({closing_day}), using current month")

    print(f"DEBUG: Initial month: {month}, year: {year}")

    # 支払い月までの差分を加算
    month += pay_month_diff
    while month > 12:
        month -= 12
        year += 1

    print(f"DEBUG: After adding pay_month_diff ({pay_month_diff}), month: {month}, year: {year}")

    paid_date = date(year, month, pay_day if pay_day > 0 else used_date.day)
    print(f"DEBUG: Final paid_date: {paid_date}")
    return paid_date

def calculate_payment_date(used_date: date, payment_source: models.PaymentSource) -> date:
    """PaymentSourceオブジェクトから支払日を計算"""
    print(f"DEBUG: calculate_payment_date called with used_date: {used_date}")
    print(f"DEBUG: payment_source: {payment_source.name}")
    print(f"DEBUG: closing_day: {payment_source.closing_day}, pay_month_diff: {payment_source.pay_month_diff}, pay_day: {payment_source.pay_day}")

    result = calculate_paid_date(
        used_date=used_date,
        closing_day=payment_source.closing_day,
        pay_month_diff=payment_source.pay_month_diff,
        pay_day=payment_source.pay_day
    )

    print(f"DEBUG: calculate_payment_date result: {result}")
    return result

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

def update_payment_source(db: Session, source_id: int, source: schemas.PaymentSourceCreate):
    db_source = get_payment_source(db, source_id)
    if db_source is None:
        return None

    # データベースのレコードを更新
    for field, value in source.dict().items():
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
    max_order = db.query(models.Budget).filter(
        models.Budget.target_year == budget.target_year,
        models.Budget.target_month == budget.target_month
    ).with_entities(func.max(models.Budget.order_index)).scalar()

    new_order = (max_order or -1) + 1

    budget_data = budget.dict()
    budget_data.pop("order_index", None)  # 既存の order_index を除外
    db_budget = models.Budget(**budget_data, order_index=new_order)
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
    update_data = budget.dict(exclude_unset=True)

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

def copy_budgets_from_year_month(db: Session, source_year: int, source_month: int, target_year: int, target_month: int):
    """指定された年月の予算を別の年月にコピー"""
    source_budgets = get_budgets_by_year_month(db, source_year, source_month)
    copied_budgets = []

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
        paid_date = calculate_paid_date(tx.used_date, source.closing_day, source.pay_month_diff, source.pay_day)
    else:
        paid_date = tx.paid_date

    db_tx = models.Transaction(**tx.dict(exclude={'paid_date', 'budget_name'}), paid_date=paid_date, budget_name=tx.budget_name or '未分類')
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).offset(skip).limit(limit).all()

def get_transaction(db: Session, tx_id: int):
    return db.query(models.Transaction).filter(models.Transaction.id == tx_id).first()

def update_transaction(db: Session, tx_id: int, tx: schemas.TransactionUpdate):
    db_tx = get_transaction(db, tx_id)
    if db_tx is None:
        return None

    # 更新データを辞書に変換
    update_data = tx.dict(exclude_unset=True)

    # 支払日の処理
    if 'paid_date' in update_data:
        # フロントエンドから支払日が送信された場合はそれを使用
        paid_date = update_data['paid_date']
    elif 'used_date' in update_data or 'payment_source_id' in update_data:
        # 使用日または支出元が変更された場合は再計算
        source = get_payment_source(db, update_data.get('payment_source_id', db_tx.payment_source_id))
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

# Knowhow CRUD

# 大項目管理
def create_major_category(db: Session, major_category: schemas.MajorCategoryCreate):
    """大項目を作成"""
    max_order = db.query(models.MajorCategory).filter(
        models.MajorCategory.is_deleted == False
    ).with_entities(func.max(models.MajorCategory.display_order)).scalar()

    display_order = (max_order or -1) + 1

    major_category_data = major_category.dict()
    major_category_data.pop('display_order', None)

    db_major_category = models.MajorCategory(**major_category_data, display_order=display_order)
    db.add(db_major_category)
    db.commit()
    db.refresh(db_major_category)
    return db_major_category

def get_major_categories(db: Session, skip: int = 0, limit: int = 100):
    """大項目一覧を取得"""
    return db.query(models.MajorCategory).filter(
        models.MajorCategory.is_deleted == False
    ).order_by(models.MajorCategory.display_order).offset(skip).limit(limit).all()

def get_major_category(db: Session, major_category_id: int):
    """特定の大項目を取得"""
    return db.query(models.MajorCategory).filter(
        models.MajorCategory.id == major_category_id,
        models.MajorCategory.is_deleted == False
    ).first()

def update_major_category(db: Session, major_category_id: int, major_category: schemas.MajorCategoryUpdate):
    """大項目を更新"""
    db_major_category = get_major_category(db, major_category_id)
    if db_major_category is None:
        return None

    update_data = major_category.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_major_category, field, value)

    db.commit()
    db.refresh(db_major_category)
    return db_major_category

def delete_major_category(db: Session, major_category_id: int):
    """大項目を削除（論理削除）"""
    db_major_category = get_major_category(db, major_category_id)
    if db_major_category is None:
        return False

    db_major_category.is_deleted = True
    db.commit()
    return True

# 中項目管理
def create_middle_category(db: Session, middle_category: schemas.MiddleCategoryCreate):
    """中項目を作成"""
    max_order = db.query(models.MiddleCategory).filter(
        models.MiddleCategory.major_category_id == middle_category.major_category_id,
        models.MiddleCategory.is_deleted == False
    ).with_entities(func.max(models.MiddleCategory.display_order)).scalar()

    display_order = (max_order or -1) + 1

    middle_category_data = middle_category.dict()
    middle_category_data.pop('display_order', None)

    db_middle_category = models.MiddleCategory(**middle_category_data, display_order=display_order)
    db.add(db_middle_category)
    db.commit()
    db.refresh(db_middle_category)
    return db_middle_category

def get_middle_categories(db: Session, major_category_id: int, skip: int = 0, limit: int = 100):
    """中項目一覧を取得"""
    return db.query(models.MiddleCategory).filter(
        models.MiddleCategory.major_category_id == major_category_id,
        models.MiddleCategory.is_deleted == False
    ).order_by(models.MiddleCategory.display_order).offset(skip).limit(limit).all()

def get_all_middle_categories(db: Session, skip: int = 0, limit: int = 100):
    """全中項目一覧を取得"""
    return db.query(models.MiddleCategory).filter(
        models.MiddleCategory.is_deleted == False
    ).order_by(models.MiddleCategory.major_category_id, models.MiddleCategory.display_order).offset(skip).limit(limit).all()

def get_middle_category(db: Session, middle_category_id: int):
    """特定の中項目を取得"""
    return db.query(models.MiddleCategory).filter(
        models.MiddleCategory.id == middle_category_id,
        models.MiddleCategory.is_deleted == False
    ).first()

def update_middle_category(db: Session, middle_category_id: int, middle_category: schemas.MiddleCategoryUpdate):
    """中項目を更新"""
    db_middle_category = get_middle_category(db, middle_category_id)
    if db_middle_category is None:
        return None

    update_data = middle_category.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_middle_category, field, value)

    db.commit()
    db.refresh(db_middle_category)
    return db_middle_category

def delete_middle_category(db: Session, middle_category_id: int):
    """中項目を削除（論理削除）"""
    db_middle_category = get_middle_category(db, middle_category_id)
    if db_middle_category is None:
        return False

    db_middle_category.is_deleted = True
    db.commit()
    return True

def create_knowhow(db: Session, knowhow: schemas.KnowhowCreate):
    # 新規作成時は同じ中項目内の最後の順序に追加
    max_order = db.query(models.Knowhow).filter(
        models.Knowhow.middle_category_id == knowhow.middle_category_id,
        models.Knowhow.is_deleted == False
    ).with_entities(func.max(models.Knowhow.display_order)).scalar()

    # max_orderがNoneの場合は0から開始、そうでなければ+1
    display_order = 0 if max_order is None else max_order + 1

    # display_orderを除外してからdict()を取得
    knowhow_data = knowhow.dict()
    knowhow_data.pop('display_order', None)  # display_orderが存在する場合は削除

    db_knowhow = models.Knowhow(**knowhow_data, display_order=display_order)
    db.add(db_knowhow)
    db.commit()
    db.refresh(db_knowhow)
    return db_knowhow

def get_knowhows(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Knowhow).filter(
        models.Knowhow.is_deleted == False
    ).order_by(models.Knowhow.display_order).offset(skip).limit(limit).all()

def get_knowhow(db: Session, knowhow_id: int):
    """特定のKNOWHOWを取得（カテゴリ情報を含む）"""
    return db.query(models.Knowhow).join(
        models.MiddleCategory
    ).join(
        models.MajorCategory
    ).filter(
        models.Knowhow.id == knowhow_id,
        models.Knowhow.is_deleted == False
    ).first()

def update_knowhow(db: Session, knowhow_id: int, knowhow: schemas.KnowhowUpdate):
    db_knowhow = get_knowhow(db, knowhow_id)
    if db_knowhow is None:
        return None

    update_data = knowhow.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_knowhow, field, value)

    db.commit()
    db.refresh(db_knowhow)
    return db_knowhow

def delete_knowhow(db: Session, knowhow_id: int):
    db_knowhow = get_knowhow(db, knowhow_id)
    if db_knowhow is None:
        return False

    # 論理削除
    db_knowhow.is_deleted = True
    db.commit()
    return True

def search_knowhows(db: Session, major_category: str = None, middle_category: str = None, keywords: str = None):
    query = db.query(models.Knowhow).filter(models.Knowhow.is_deleted == False)

    if major_category:
        query = query.filter(models.Knowhow.major_category == major_category)

    if middle_category:
        query = query.filter(models.Knowhow.middle_category == middle_category)

    if keywords:
        query = query.filter(
            models.Knowhow.keywords.contains(keywords) |
            models.Knowhow.title.contains(keywords) |
            models.Knowhow.content.contains(keywords)
        )

    return query.order_by(models.Knowhow.display_order).all()

def get_knowhow_tree(db: Session):
    """大項目・中項目のツリー構造を取得"""
    print("get_knowhow_tree called")
    try:
        # 大項目を取得
        major_categories = db.query(models.MajorCategory).filter(
            models.MajorCategory.is_deleted == False
        ).order_by(models.MajorCategory.display_order).all()

        tree = {}
        for major_category in major_categories:
            tree[major_category.name] = {}

            # 中項目を取得
            middle_categories = db.query(models.MiddleCategory).filter(
                models.MiddleCategory.major_category_id == major_category.id,
                models.MiddleCategory.is_deleted == False
            ).order_by(models.MiddleCategory.display_order).all()

            for middle_category in middle_categories:
                tree[major_category.name][middle_category.name] = []

                # KNOWHOWを取得
                knowhows = db.query(models.Knowhow).filter(
                    models.Knowhow.middle_category_id == middle_category.id,
                    models.Knowhow.is_deleted == False
                ).order_by(models.Knowhow.display_order).all()

                for knowhow in knowhows:
                    tree[major_category.name][middle_category.name].append({
                        'id': knowhow.id,
                        'title': knowhow.title,
                        'keywords': knowhow.keywords,
                        'display_order': knowhow.display_order,
                        'middle_category_id': knowhow.middle_category_id
                    })

        print(f"Tree structure: {tree}")
        return tree
    except Exception as e:
        print(f"Error in get_knowhow_tree: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise

def move_knowhow_up(db: Session, knowhow_id: int):
    """KNOWHOWを上に移動"""
    db_knowhow = get_knowhow(db, knowhow_id)
    if db_knowhow is None:
        return None

    # 同じ中項目内で一つ前のKNOWHOWを取得
    prev_knowhow = db.query(models.Knowhow).filter(
        models.Knowhow.is_deleted == False,
        models.Knowhow.middle_category_id == db_knowhow.middle_category_id,
        models.Knowhow.display_order < db_knowhow.display_order
    ).order_by(models.Knowhow.display_order.desc()).first()

    if prev_knowhow is None:
        return db_knowhow  # 既に最上位

    # 順序を入れ替え
    temp_order = db_knowhow.display_order
    db_knowhow.display_order = prev_knowhow.display_order
    prev_knowhow.display_order = temp_order

    db.commit()
    db.refresh(db_knowhow)
    return db_knowhow

def move_knowhow_down(db: Session, knowhow_id: int):
    """KNOWHOWを下に移動"""
    db_knowhow = get_knowhow(db, knowhow_id)
    if db_knowhow is None:
        return None

    # 同じ中項目内で一つ後のKNOWHOWを取得
    next_knowhow = db.query(models.Knowhow).filter(
        models.Knowhow.is_deleted == False,
        models.Knowhow.middle_category_id == db_knowhow.middle_category_id,
        models.Knowhow.display_order > db_knowhow.display_order
    ).order_by(models.Knowhow.display_order).first()

    if next_knowhow is None:
        return db_knowhow  # 既に最下位

    # 順序を入れ替え
    temp_order = db_knowhow.display_order
    db_knowhow.display_order = next_knowhow.display_order
    next_knowhow.display_order = temp_order

    db.commit()
    db.refresh(db_knowhow)
    return db_knowhow

def normalize_knowhow_order_indexes(db: Session):
    """KNOWHOWの表示順序を正規化"""
    knowhows = db.query(models.Knowhow).filter(
        models.Knowhow.is_deleted == False
    ).order_by(models.Knowhow.display_order).all()

    for i, knowhow in enumerate(knowhows):
        knowhow.display_order = i

    db.commit()
    return knowhows
