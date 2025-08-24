from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta, timezone
import models
import schemas
from typing import Optional

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
