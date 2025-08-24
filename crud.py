from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta, timezone
import models
import schemas
from PIL import Image
import io

from typing import Optional
from typing import TypedDict

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

def calculate_payment_date_for_month(year: int, month: int, payment_source: models.PaymentSource) -> Optional[date]:
    """指定月の支払日を計算"""
    if payment_source.closing_day == 0:
        print(f"Debug: Payment source {payment_source.name} has closing_day = 0, returning None")
        return None

    # その月の締め日を基準に支払日を計算
    # 締め日が月末を超える場合は月末を使用
    import calendar
    last_day = calendar.monthrange(year, month)[1]
    closing_day = min(payment_source.closing_day, last_day)

    print(f"Debug: Processing {year}-{month}, closing_day: {closing_day}, last_day: {last_day}")

    # # 締め日を基準に支払日を計算
    # closing_date = date(year, month, closing_day)

    # 支払い月までの差分を加算
    result_month = month + payment_source.pay_month_diff
    result_year = year
    while result_month > 12:
        result_month -= 12
        result_year += 1

    print(f"Debug: Result month/year: {result_month}/{result_year}, pay_month_diff: {payment_source.pay_month_diff}")

    # 支払日の日付を決定
    if payment_source.pay_day > 0:
        # 指定された支払日を使用
        last_day = calendar.monthrange(result_year, result_month)[1]
        pay_day = min(payment_source.pay_day, last_day)
        payment_date = date(result_year, result_month, pay_day)
        print(f"Debug: Using pay_day {payment_source.pay_day}, final pay_day: {pay_day}, payment_date: {payment_date}")
    else:
        # 締め日と同じ日を使用
        last_day = calendar.monthrange(result_year, result_month)[1]
        pay_day = min(closing_day, last_day)
        payment_date = date(result_year, result_month, pay_day)
        print(f"Debug: Using closing_day {closing_day}, final pay_day: {pay_day}, payment_date: {payment_date}")

    return payment_date

# 画像リサイズ関数
def resize_image(image_data: bytes, max_size: int = 800) -> bytes:
    """画像をリサイズしてバイトデータを返す"""
    try:
        # 画像を開く
        image = Image.open(io.BytesIO(image_data))

        # アスペクト比を保ってリサイズ
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        # JPEG形式で保存
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=85, optimize=True)
        return output.getvalue()
    except Exception as e:
        print(f"画像リサイズエラー: {e}")
        return image_data

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

# MajorCategory CRUD

def create_major_category(db: Session, major_category: schemas.MajorCategoryCreate):
    """大項目を作成"""
    max_order = db.query(models.MajorCategory).filter(
        models.MajorCategory.is_deleted == False
    ).with_entities(func.max(models.MajorCategory.display_order)).scalar()

    display_order = (max_order or -1) + 1

    major_category_data = major_category.model_dump()
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

    update_data = major_category.model_dump(exclude_unset=True)
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

# MiddleCategory CRUD

def create_middle_category(db: Session, middle_category: schemas.MiddleCategoryCreate):
    """中項目を作成"""
    max_order = db.query(models.MiddleCategory).filter(
        models.MiddleCategory.major_category_id == middle_category.major_category_id,
        models.MiddleCategory.is_deleted == False
    ).with_entities(func.max(models.MiddleCategory.display_order)).scalar()

    display_order = (max_order or -1) + 1

    middle_category_data = middle_category.model_dump()
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

    update_data = middle_category.model_dump(exclude_unset=True)
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

# Knowhow CRUD

def create_knowhow(db: Session, knowhow: schemas.KnowhowCreate):
    # 新規作成時は同じ中項目内の最後の順序に追加
    max_order = db.query(models.Knowhow).filter(
        models.Knowhow.middle_category_id == knowhow.middle_category_id,
        models.Knowhow.is_deleted == False
    ).with_entities(func.max(models.Knowhow.display_order)).scalar()

    # max_orderがNoneの場合は0から開始、そうでなければ+1
    display_order = 0 if max_order is None else max_order + 1

    # display_orderを除外してからdict()を取得
    knowhow_data = knowhow.model_dump()
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

    update_data = knowhow.model_dump(exclude_unset=True)
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

def search_knowhows(db: Session, major_category: Optional[str] = None, middle_category: Optional[str] = None, keywords: Optional[str] = None):
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

# GOODS管理システム用のCRUD操作

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

# スケジュール管理用のCRUD操作

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
