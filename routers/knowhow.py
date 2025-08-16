from fastapi import APIRouter
from fastapi import Depends, HTTPException, Request

from sqlalchemy.orm import Session
from sqlalchemy import text

import crud
import schemas

import os
import sys
sys.path.append(os.path.dirname(__file__))
from common import get_db, get_session_info

router = APIRouter()

# Knowhow API endpoints

@router.get("/knowhows", response_model=schemas.ListResponse[schemas.Knowhow])
def read_knowhows(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), request: Request = None):
    """KNOWHOW一覧を取得"""
    try:
        knowhows = crud.get_knowhows(db, skip=skip, limit=limit)
        session_info = get_session_info(request)
        return schemas.ListResponse(processing_result=True, session_info=session_info, data=knowhows)
    except Exception as e:
        print(f"KNOWHOW list error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/knowhows/test")
def test_knowhows(db: Session = Depends(get_db)):
    """KNOWHOWテーブルの存在確認"""
    try:
        # テーブルが存在するかチェック
        result = db.execute(text("SELECT COUNT(*) FROM knowhows"))
        count = result.scalar()
        return {"message": "KNOWHOW table exists", "count": count}
    except Exception as e:
        print(f"KNOWHOW test error: {e}")
        return {"message": "KNOWHOW table error", "error": str(e)}

@router.get("/knowhows/search")
def search_knowhows(
    major_category: str = None,
    middle_category: str = None,
    keywords: str = None,
    db: Session = Depends(get_db)
):
    """KNOWHOWを検索"""
    knowhows = crud.search_knowhows(
        db,
        major_category=major_category,
        middle_category=middle_category,
        keywords=keywords
    )
    return knowhows

@router.get("/knowhows/tree", response_model=schemas.BaseResponse[dict])
def get_knowhow_tree(db: Session = Depends(get_db), request: Request = None):
    """KNOWHOWのツリー構造を取得"""
    print("KNOWHOW tree endpoint called")
    try:
        print("Calling crud.get_knowhow_tree...")
        tree = crud.get_knowhow_tree(db)
        print(f"Tree result: {tree}")
        session_info = get_session_info(request)
        return schemas.BaseResponse(processing_result=True, session_info=session_info, data=tree)
    except Exception as e:
        print(f"KNOWHOW tree error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/knowhows/{knowhow_id}", response_model=schemas.BaseResponse[schemas.Knowhow])
def read_knowhow(knowhow_id: int, db: Session = Depends(get_db), request: Request = None):
    """特定のKNOWHOWを取得"""
    knowhow = crud.get_knowhow(db, knowhow_id=knowhow_id)
    if knowhow is None:
        raise HTTPException(status_code=404, detail="Knowhow not found")
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=knowhow)

@router.post("/knowhows", response_model=schemas.BaseResponse[schemas.Knowhow])
def create_knowhow(knowhow: schemas.KnowhowCreate, db: Session = Depends(get_db), request: Request = None):
    """新しいKNOWHOWを作成"""
    result = crud.create_knowhow(db=db, knowhow=knowhow)
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=result)

@router.put("/knowhows/{knowhow_id}", response_model=schemas.BaseResponse[schemas.Knowhow])
def update_knowhow(knowhow_id: int, knowhow: schemas.KnowhowUpdate, db: Session = Depends(get_db), request: Request = None):
    """KNOWHOWを更新"""
    db_knowhow = crud.update_knowhow(db, knowhow_id=knowhow_id, knowhow=knowhow)
    if db_knowhow is None:
        raise HTTPException(status_code=404, detail="Knowhow not found")
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=db_knowhow)

@router.delete("/knowhows/{knowhow_id}", response_model=schemas.SimpleResponse)
def delete_knowhow(knowhow_id: int, db: Session = Depends(get_db), request: Request = None):
    """KNOWHOWを削除（論理削除）"""
    success = crud.delete_knowhow(db, knowhow_id=knowhow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Knowhow not found")
    session_info = get_session_info(request)
    return schemas.SimpleResponse(processing_result=True, session_info=session_info, message="Knowhow deleted successfully")

@router.post("/knowhows/{knowhow_id}/move-up", response_model=schemas.SimpleResponse)
def move_knowhow_up(knowhow_id: int, db: Session = Depends(get_db), request: Request = None):
    """KNOWHOWを上に移動"""
    knowhow = crud.move_knowhow_up(db, knowhow_id=knowhow_id)
    if knowhow is None:
        raise HTTPException(status_code=404, detail="Knowhow not found")
    session_info = get_session_info(request)
    return schemas.SimpleResponse(processing_result=True, session_info=session_info, message="Knowhow moved up successfully")

@router.post("/knowhows/{knowhow_id}/move-down", response_model=schemas.SimpleResponse)
def move_knowhow_down(knowhow_id: int, db: Session = Depends(get_db), request: Request = None):
    """KNOWHOWを下に移動"""
    knowhow = crud.move_knowhow_down(db, knowhow_id=knowhow_id)
    if knowhow is None:
        raise HTTPException(status_code=404, detail="Knowhow not found")
    session_info = get_session_info(request)
    return schemas.SimpleResponse(processing_result=True, session_info=session_info, message="Knowhow moved down successfully")

# 大項目管理エンドポイント
@router.get("/major-categories", response_model=schemas.ListResponse[schemas.MajorCategory])
def read_major_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), request: Request = None):
    """大項目一覧を取得"""
    major_categories = crud.get_major_categories(db, skip=skip, limit=limit)
    session_info = get_session_info(request)
    return schemas.ListResponse(processing_result=True, session_info=session_info, data=major_categories)

@router.get("/major-categories/{major_category_id}", response_model=schemas.BaseResponse[schemas.MajorCategory])
def read_major_category(major_category_id: int, db: Session = Depends(get_db), request: Request = None):
    """特定の大項目を取得"""
    major_category = crud.get_major_category(db, major_category_id=major_category_id)
    if major_category is None:
        raise HTTPException(status_code=404, detail="Major category not found")
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=major_category)

@router.post("/major-categories", response_model=schemas.MajorCategory)
def create_major_category(major_category: schemas.MajorCategoryCreate, db: Session = Depends(get_db)):
    """新しい大項目を作成"""
    return crud.create_major_category(db=db, major_category=major_category)

@router.put("/major-categories/{major_category_id}", response_model=schemas.MajorCategory)
def update_major_category(major_category_id: int, major_category: schemas.MajorCategoryUpdate, db: Session = Depends(get_db)):
    """大項目を更新"""
    db_major_category = crud.update_major_category(db, major_category_id=major_category_id, major_category=major_category)
    if db_major_category is None:
        raise HTTPException(status_code=404, detail="Major category not found")
    return db_major_category

@router.delete("/major-categories/{major_category_id}")
def delete_major_category(major_category_id: int, db: Session = Depends(get_db)):
    """大項目を削除（論理削除）"""
    success = crud.delete_major_category(db, major_category_id=major_category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Major category not found")
    return {"message": "Major category deleted successfully"}

# 中項目管理エンドポイント
@router.get("/major-categories/{major_category_id}/middle-categories", response_model=schemas.ListResponse[schemas.MiddleCategory])
def read_middle_categories(major_category_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), request: Request = None):
    """中項目一覧を取得"""
    middle_categories = crud.get_middle_categories(db, major_category_id=major_category_id, skip=skip, limit=limit)
    session_info = get_session_info(request)
    return schemas.ListResponse(processing_result=True, session_info=session_info, data=middle_categories)

@router.get("/middle-categories", response_model=schemas.ListResponse[schemas.MiddleCategory])
def read_all_middle_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), request: Request = None):
    """全中項目一覧を取得"""
    middle_categories = crud.get_all_middle_categories(db, skip=skip, limit=limit)
    session_info = get_session_info(request)
    return schemas.ListResponse(processing_result=True, session_info=session_info, data=middle_categories)

@router.get("/middle-categories/{middle_category_id}", response_model=schemas.BaseResponse[schemas.MiddleCategory])
def read_middle_category(middle_category_id: int, db: Session = Depends(get_db), request: Request = None):
    """特定の中項目を取得"""
    middle_category = crud.get_middle_category(db, middle_category_id=middle_category_id)
    if middle_category is None:
        raise HTTPException(status_code=404, detail="Middle category not found")
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=middle_category)

@router.post("/middle-categories", response_model=schemas.MiddleCategory)
def create_middle_category(middle_category: schemas.MiddleCategoryCreate, db: Session = Depends(get_db)):
    """新しい中項目を作成"""
    return crud.create_middle_category(db=db, middle_category=middle_category)

@router.put("/middle-categories/{middle_category_id}", response_model=schemas.MiddleCategory)
def update_middle_category(middle_category_id: int, middle_category: schemas.MiddleCategoryUpdate, db: Session = Depends(get_db)):
    """中項目を更新"""
    db_middle_category = crud.update_middle_category(db, middle_category_id=middle_category_id, middle_category=middle_category)
    if db_middle_category is None:
        raise HTTPException(status_code=404, detail="Middle category not found")
    return db_middle_category

@router.delete("/middle-categories/{middle_category_id}")
def delete_middle_category(middle_category_id: int, db: Session = Depends(get_db)):
    """中項目を削除（論理削除）"""
    success = crud.delete_middle_category(db, middle_category_id=middle_category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Middle category not found")
    return {"message": "Middle category deleted successfully"}
