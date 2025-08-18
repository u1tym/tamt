from fastapi import APIRouter
from fastapi import Depends, HTTPException, Request, UploadFile, File

from sqlalchemy import func
from sqlalchemy.orm import Session

import re
import io
from PIL import Image
import cv2
import numpy as np
import pytesseract

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

import models
import crud
import schemas

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common import get_db, get_session_info

from type_req import rep_calculate_payment_periods_rec
from type_req import rep_calculate_payment_periods
from type_req import rep_get_payment_summary_rec
from type_req import rep_parse_recipt

from log import Log

from typing import cast
from typing import Any, Optional

router = APIRouter()

@router.get("/payment-summary", response_model=schemas.BaseResponse[dict[str, Any]])
def get_payment_summary(request: Request, db: Session = Depends(get_db)):
    """支払い額の集計を取得"""

    ulog = request.app.state.ulog
    ulog.output("INF", "[ST] get_payment_summary()")

    try:
        # 支払い期間を計算
        periods = calculate_payment_periods(ulog)

        # 各期間の支払い額を集計
        summary: dict[str, rep_get_payment_summary_rec] = {}

        for nm, vl in periods.items():
            period_name: str = nm
            period_data: rep_calculate_payment_periods_rec = cast(rep_calculate_payment_periods_rec, vl)

            # 該当期間の取引を取得
            transactions = db.query(models.Transaction).filter(
                models.Transaction.paid_date >= period_data['start'],
                models.Transaction.paid_date <= period_data['end']
            ).all()

            # 支払い額を集計
            total_amount = sum(tx.amount for tx in transactions)

            summary[period_name] = {
                'period': period_data['label'],
                'start_date': period_data['start'].isoformat(),
                'end_date': period_data['end'].isoformat(),
                'total_amount': total_amount,
                'transaction_count': len(transactions)
            }

        session_info = get_session_info(request)

        ulog.output("INF", "[ED] get_payment_summary()")

        return schemas.BaseResponse(processing_result=True, session_info=session_info, data=summary)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"支払い集計の取得に失敗しました: {str(e)}")

# レシート解析関数
def parse_receipt(image_data: bytes) -> rep_parse_recipt:
    """
    レシート画像を解析して取引情報を抽出
    """
    try:
        # Tesseractが利用可能かチェック
        try:
            # Tesseractのパスを明示的に指定
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            # テスト実行
            version = pytesseract.get_tesseract_version()
            print(f"Tesseractバージョン: {version}")

            # 利用可能な言語を確認
            try:
                langs = pytesseract.get_languages()
                print(f"利用可能な言語: {langs}")
            except Exception as lang_error:
                print(f"言語確認エラー: {lang_error}")
        except Exception as e:
            print(f"Tesseractエラー: {e}")
            # モックデータを返す
            return {
                'used_date': '2024-07-26',
                'purpose': 'テスト店舗',
                'amount': 1000,
                'raw_text': 'テストレシート\n2024年7月26日\nテスト店舗\n合計: ¥1,000',
                'confidence': 0.8,
                'note': 'Tesseractがインストールされていないため、モックデータを返しています'
            }

        # 画像をPILで読み込み
        image = Image.open(io.BytesIO(image_data))

        # OpenCVで処理するためにnumpy配列に変換
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # グレースケールに変換
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        # ノイズ除去
        denoised = cv2.medianBlur(gray, 3)

        # コントラスト改善
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)

        # OCRでテキスト抽出
        text = pytesseract.image_to_string(enhanced, lang='jpn+eng')

        # 解析結果
        result = {
            'used_date': None,
            'purpose': None,
            'amount': None,
            'raw_text': text,
            'confidence': 0.0
        }

        # 日付の抽出（レシート上部を優先的に検索）
        date_patterns = [
            # 日本語形式
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',  # 2024年1月1日
            r'(\d{1,2})月(\d{1,2})日',  # 1月1日
            r'(\d{4})年(\d{1,2})月(\d{1,2})',  # 2024年1月1

            # スラッシュ形式
            r'(\d{4})/(\d{1,2})/(\d{1,2})',  # 2024/01/01
            r'(\d{1,2})/(\d{1,2})',  # 01/01

            # ハイフン形式
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # 2024-01-01
            r'(\d{1,2})-(\d{1,2})',  # 01-01

            # ドット形式
            r'(\d{4})\.(\d{1,2})\.(\d{1,2})',  # 2024.01.01
            r'(\d{1,2})\.(\d{1,2})',  # 01.01

            # スペース区切り
            r'(\d{4})\s+(\d{1,2})\s+(\d{1,2})',  # 2024 01 01

            # より柔軟なパターン
            r'(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2,4})',  # 1/1/24, 1-1-2024
            r'(\d{2,4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,2})',  # 24/1/1, 2024/1/1

            # 日本語の日付表現
            r'(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日',  # 2024年 1月 1日
            r'(\d{1,2})月\s*(\d{1,2})日',  # 1月 1日

            # 英語形式
            r'(\d{1,2})/(\d{1,2})/(\d{2,4})',  # 1/1/24, 1/1/2024
            r'(\d{2,4})/(\d{1,2})/(\d{1,2})',  # 24/1/1, 2024/1/1
        ]

        # レシートの上部部分（最初の15行）を優先的に検索
        lines = text.split('\n')
        upper_text = '\n'.join(lines[:15])  # 最初の15行

        print(f"OCR結果の上部15行: {upper_text}")

        # 上部部分で日付を検索
        for i, pattern in enumerate(date_patterns):
            match = re.search(pattern, upper_text)
            if match:
                print(f"日付パターン {i+1} でマッチ: {match.group()}")
                if len(match.groups()) == 3:
                    year, month, day = match.groups()
                    if len(year) == 2:  # 2桁の年の場合
                        year = '20' + year
                    result['used_date'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    print(f"3グループ日付抽出: {result['used_date']}")
                elif len(match.groups()) == 2:
                    month, day = match.groups()
                    # 現在の年を使用
                    current_year = datetime.now().year
                    result['used_date'] = f"{current_year}-{month.zfill(2)}-{day.zfill(2)}"
                    print(f"2グループ日付抽出: {result['used_date']}")
                break

        # 上部で見つからない場合は全体を検索
        if not result['used_date']:
            print("上部で日付が見つからないため、全体を検索")
            for i, pattern in enumerate(date_patterns):
                match = re.search(pattern, text)
                if match:
                    print(f"全体検索で日付パターン {i+1} でマッチ: {match.group()}")
                    if len(match.groups()) == 3:
                        year, month, day = match.groups()
                        if len(year) == 2:  # 2桁の年の場合
                            year = '20' + year
                        result['used_date'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        print(f"全体検索3グループ日付抽出: {result['used_date']}")
                    elif len(match.groups()) == 2:
                        month, day = match.groups()
                        # 現在の年を使用
                        current_year = datetime.now().year
                        result['used_date'] = f"{current_year}-{month.zfill(2)}-{day.zfill(2)}"
                        print(f"全体検索2グループ日付抽出: {result['used_date']}")
                    break

        if not result['used_date']:
            print("日付が見つかりませんでした")
            print(f"OCR結果全体: {text}")

        # 金額の抽出
        amount_patterns = [
            r'合計[：:]\s*¥?([0-9,]+)',  # 合計: ¥1,000
            r'税込[：:]\s*¥?([0-9,]+)',  # 税込: ¥1,000
            r'小計[：:]\s*¥?([0-9,]+)',  # 小計: ¥1,000
            r'¥([0-9,]+)',  # ¥1,000
            r'([0-9,]+)円',  # 1,000円
            r'([0-9,]+)\s*円',  # 1,000 円
            r'([0-9,]+)',  # 1,000（単独の数字）
        ]

        print(f"金額抽出開始 - テキスト: {text}")

        for i, pattern in enumerate(amount_patterns):
            matches = re.findall(pattern, text)
            if matches:
                print(f"金額パターン {i+1} でマッチ: {matches}")
                for match in matches:
                    amount_str = match.replace(',', '')
                    try:
                        amount = int(amount_str)
                        # 妥当な金額範囲かチェック（100円〜100万円）
                        if 100 <= amount <= 1000000:
                            result['amount'] = amount
                            print(f"金額抽出成功: {amount}")
                            break
                    except ValueError:
                        continue
                if result['amount']:
                    break



        # 店舗名/用途の抽出
        lines = text.split('\n')
        print(f"店舗名抽出開始 - 行数: {len(lines)}")

        for i, line in enumerate(lines):
            line = line.strip()
            print(f"行 {i+1}: '{line}'")

            # 店舗名らしき文字列を探す（長すぎず短すぎない行）
            if 3 <= len(line) <= 30 and not re.search(r'[0-9]', line):
                # 一般的なレシートの除外語
                exclude_words = ['レシート', '領収書', '合計', '税込', '小計', '消費税', 'お釣り', '現金', 'カード', 'TAF', 'GS', 'DST']
                if not any(word in line for word in exclude_words):
                    result['purpose'] = line
                    print(f"店舗名抽出成功: {line}")
                    break

        # 信頼度の計算（抽出できた項目数で判定）
        extracted_count = sum(1 for v in [result['used_date'], result['purpose'], result['amount']] if v is not None)
        result['confidence'] = extracted_count / 3.0

        return result

    except Exception as e:
        return {
            'used_date': None,
            'purpose': None,
            'amount': None,
            'raw_text': '',
            'confidence': 0.0,
            'error': str(e)
        }

@router.post("/parse-receipt")
async def parse_receipt_endpoint(file: UploadFile = File(...)):
    """
    レシート画像をアップロードして解析
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="画像ファイルをアップロードしてください")

    try:
        # 画像データを読み込み
        image_data = await file.read()

        # レシート解析
        result = parse_receipt(image_data)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"レシート解析中にエラーが発生しました: {str(e)}")

# 既存のエンドポイント
@router.get("/transactions", response_model=schemas.ListResponse[schemas.Transaction])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), request: Request = None):

    ulog = request.app.state.ulog
    ulog.output("INF", "[ST] transaction()")

    now: date = date.today()
    frdt = now + timedelta(days = -45)
    todt = now + timedelta(days = 1)

    ulog.output("DBG", "検索対象期間 " + str(frdt) + "～" + str(todt))
    transactions = crud.get_transactions(db, frdt, todt)

    session_info = get_session_info(request)

    res = schemas.ListResponse(processing_result=True, session_info=session_info, data=transactions)

    ulog.output("INF", "[ED] transaction()")
    return res

@router.post("/transactions", response_model=schemas.BaseResponse[schemas.Transaction])
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db), request: Request = None):
    result = crud.create_transaction(db=db, tx=transaction)
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=result)

@router.put("/transactions/{transaction_id}", response_model=schemas.BaseResponse[schemas.Transaction])
def update_transaction(transaction_id: int, transaction: schemas.TransactionUpdate, db: Session = Depends(get_db), request: Request = None):
    db_transaction = crud.get_transaction(db, tx_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    result = crud.update_transaction(db=db, tx_id=transaction_id, tx=transaction)
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=result)

@router.delete("/transactions/{transaction_id}", response_model=schemas.SimpleResponse)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db), request: Request = None):
    try:
        db_transaction = crud.get_transaction(db, tx_id=transaction_id)
        if db_transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        crud.delete_transaction(db=db, tx_id=transaction_id)
        session_info = get_session_info(request)
        return schemas.SimpleResponse(processing_result=True, session_info=session_info, message="Transaction deleted successfully")
    except Exception as e:
        print(f"Error deleting transaction {transaction_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete transaction: {str(e)}")

@router.get("/payment_sources", response_model=schemas.ListResponse[schemas.PaymentSource])
def read_payment_sources(db: Session = Depends(get_db), request: Request = None):
    payment_sources = crud.get_payment_sources(db)
    session_info = get_session_info(request)
    return schemas.ListResponse(processing_result=True, session_info=session_info, data=payment_sources)

@router.post("/payment_sources", response_model=schemas.BaseResponse[schemas.PaymentSource])
def create_payment_source(payment_source: schemas.PaymentSourceCreate, db: Session = Depends(get_db), request: Request = None):
    result = crud.create_payment_source(db=db, source=payment_source)
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=result)

@router.put("/payment_sources/{payment_source_id}", response_model=schemas.BaseResponse[schemas.PaymentSource])
def update_payment_source(payment_source_id: int, payment_source: schemas.PaymentSourceCreate, db: Session = Depends(get_db), request: Request = None):
    db_payment_source = crud.get_payment_source(db, source_id=payment_source_id)
    if db_payment_source is None:
        raise HTTPException(status_code=404, detail="Payment source not found")
    result = crud.update_payment_source(db=db, source_id=payment_source_id, source=payment_source)
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=result)

@router.delete("/payment_sources/{payment_source_id}", response_model=schemas.SimpleResponse)
def delete_payment_source(payment_source_id: int, db: Session = Depends(get_db), request: Request = None):
    db_payment_source = crud.get_payment_source(db, source_id=payment_source_id)
    if db_payment_source is None:
        raise HTTPException(status_code=404, detail="Payment source not found")

    # 関連する取引があるかチェック
    related_transactions = db.query(models.Transaction).filter(
        models.Transaction.payment_source_id == payment_source_id
    ).first()

    if related_transactions:
        raise HTTPException(
            status_code=400,
            detail="この支出元に関連する取引が存在するため削除できません。先に関連する取引を削除してください。"
        )

    crud.delete_payment_source(db=db, source_id=payment_source_id)
    session_info = get_session_info(request)
    return schemas.SimpleResponse(processing_result=True, session_info=session_info, message="Payment source deleted successfully")

# Budget API endpoints

@router.get("/budgets/{target_year}/{target_month}", response_model=schemas.ListResponse[schemas.Budget])
def read_budgets_by_year_month(target_year: int, target_month: int, db: Session = Depends(get_db), request: Request = None):
    """指定された年月の予算一覧を取得"""
    if target_month < 1 or target_month > 12:
        raise HTTPException(status_code=400, detail="月は1～12の範囲で指定してください")

    budgets = crud.get_budgets_by_year_month(db, target_year=target_year, target_month=target_month)
    session_info = get_session_info(request)
    return schemas.ListResponse(processing_result=True, session_info=session_info, data=budgets)

@router.post("/budgets", response_model=schemas.BaseResponse[schemas.Budget])
def create_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_db), request: Request = None):
    """新規予算を作成"""
    if budget.target_month < 1 or budget.target_month > 12:
        raise HTTPException(status_code=400, detail="月は1～12の範囲で指定してください")

    result = crud.create_budget(db=db, budget=budget)
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=result)

@router.put("/budgets/{budget_id}", response_model=schemas.BaseResponse[schemas.Budget])
def update_budget(budget_id: int, budget: schemas.BudgetUpdate, db: Session = Depends(get_db), request: Request = None):
    """予算を更新"""
    db_budget = crud.get_budget(db, budget_id=budget_id)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")

    # 月の範囲チェック
    if budget.target_month is not None and (budget.target_month < 1 or budget.target_month > 12):
        raise HTTPException(status_code=400, detail="月は1～12の範囲で指定してください")

    result = crud.update_budget(db=db, budget_id=budget_id, budget=budget)
    session_info = get_session_info(request)
    return schemas.BaseResponse(processing_result=True, session_info=session_info, data=result)

@router.delete("/budgets/{budget_id}", response_model=schemas.SimpleResponse)
def delete_budget(budget_id: int, db: Session = Depends(get_db), request: Request = None):
    """予算を削除"""
    db_budget = crud.get_budget(db, budget_id=budget_id)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")

    crud.delete_budget(db=db, budget_id=budget_id)
    session_info = get_session_info(request)
    return schemas.SimpleResponse(processing_result=True, session_info=session_info, message="Budget deleted successfully")

@router.post("/budgets/copy", response_model=schemas.SimpleResponse)
def copy_budgets(source_year: int, source_month: int, target_year: int, target_month: int, db: Session = Depends(get_db), request: Request = None):
    """指定された年月の予算を別の年月にコピー"""
    if source_month < 1 or source_month > 12 or target_month < 1 or target_month > 12:
        raise HTTPException(status_code=400, detail="月は1～12の範囲で指定してください")

    copied_budgets = crud.copy_budgets_from_year_month(
        db=db,
        source_year=source_year,
        source_month=source_month,
        target_year=target_year,
        target_month=target_month
    )

    session_info = get_session_info(request)
    message = f"{source_year}年{source_month}月の予算を{target_year}年{target_month}月にコピーしました"
    return schemas.SimpleResponse(processing_result=True, session_info=session_info, message=message)

@router.post("/budgets/{budget_id}/move-up", response_model=schemas.SimpleResponse)
def move_budget_up(budget_id: int, db: Session = Depends(get_db), request: Request = None):
    """予算を上に移動"""
    db_budget = crud.get_budget(db, budget_id=budget_id)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")

    updated_budget = crud.move_budget_up(db=db, budget_id=budget_id)
    if updated_budget is None:
        raise HTTPException(status_code=400, detail="既に最上部にあります")

    session_info = get_session_info(request)
    return schemas.SimpleResponse(processing_result=True, session_info=session_info, message="予算を上に移動しました")

@router.post("/budgets/{budget_id}/move-down", response_model=schemas.SimpleResponse)
def move_budget_down(budget_id: int, db: Session = Depends(get_db), request: Request = None):
    """予算を下に移動"""
    db_budget = crud.get_budget(db, budget_id=budget_id)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")

    updated_budget = crud.move_budget_down(db=db, budget_id=budget_id)
    if updated_budget is None:
        raise HTTPException(status_code=400, detail="既に最下部にあります")

    session_info = get_session_info(request)
    return schemas.SimpleResponse(processing_result=True, session_info=session_info, message="予算を下に移動しました")

@router.post("/calculate-payment-date")
def calculate_payment_date(request: schemas.PaymentDateRequest, db: Session = Depends(get_db)):
    """使用日と支出元から支払日を計算"""
    try:
        print(f"DEBUG: Received request - used_date: {request.used_date}, payment_source_id: {request.payment_source_id}")

        # 支出元を取得
        payment_source = crud.get_payment_source(db, source_id=request.payment_source_id)
        if not payment_source:
            print(f"DEBUG: Payment source not found for ID: {request.payment_source_id}")
            raise HTTPException(status_code=404, detail="Payment source not found")

        print(f"DEBUG: Found payment source: {payment_source.name}")
        print(f"DEBUG: Payment source details - closing_day: {payment_source.closing_day}, pay_month_diff: {payment_source.pay_month_diff}, pay_day: {payment_source.pay_day}")

        # 使用日をdateオブジェクトに変換
        used_date_obj = datetime.strptime(request.used_date, "%Y-%m-%d").date()
        print(f"DEBUG: Parsed used_date: {used_date_obj}")

        # 支払日を計算
        paid_date = crud.calculate_payment_date(used_date_obj, payment_source)
        print(f"DEBUG: Calculated paid_date: {paid_date}")

        return {"paid_date": paid_date.strftime("%Y-%m-%d")}
    except ValueError as e:
        print(f"DEBUG: ValueError occurred: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        print(f"DEBUG: Unexpected error occurred: {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error calculating payment date: {e}")

from datetime import date

@router.get("/budget-names")
def get_budget_names(date_str: str, db: Session = Depends(get_db)):
    """指定日が属する予算名称一覧を取得"""
    target_date = date.fromisoformat(date_str)
    # その日が属する予算期間（23日～翌月22日）を計算
    if target_date.day >= 23:
        target_year = target_date.year
        target_month = target_date.month
    else:
        if target_date.month == 1:
            target_year = target_date.year - 1
            target_month = 12
        else:
            target_year = target_date.year
            target_month = target_date.month - 1
    budgets = crud.get_budgets_by_year_month(db, target_year=target_year, target_month=target_month)
    names = [b.name for b in budgets]
    return {"names": names}

@router.get("/budgets/{year}/{month}/summary", response_model=schemas.ListResponse[dict])
def get_budget_summaries(year: int, month: int, db: Session = Depends(get_db), request: Request = None):
    """指定年月の各予算名称ごとに支払日が対象期間内の取引合計金額を返す"""
    # 期間計算（23日～翌月22日）
    from datetime import date
    from dateutil.relativedelta import relativedelta
    start_date = date(year, month, 23)
    if month == 12:
        end_date = date(year + 1, 1, 22)
    else:
        end_date = date(year, month + 1, 22)
    # 取引を集計
    results = db.query(
        models.Transaction.budget_name,
        func.sum(models.Transaction.amount).label('total')
    ).filter(
        models.Transaction.paid_date >= start_date,
        models.Transaction.paid_date <= end_date
    ).group_by(models.Transaction.budget_name).all()
    # 返却形式を整形
    data = [{"name": r.budget_name, "total": float(r.total or 0)} for r in results]
    session_info = get_session_info(request)
    return schemas.ListResponse(processing_result=True, session_info=session_info, data=data)

@router.get("/debit-summary", response_model=schemas.ListResponse[dict])
def get_debit_summary(db: Session = Depends(get_db), request: Request = None):
    """支払日毎の取引金額合計を取得"""
    try:
        from datetime import date
        from dateutil.relativedelta import relativedelta

        # 現在日を基準に期間を設定
        today = date.today()

        # 対象期間: 前月、当月、翌月、翌々月、さらに次の月
        target_months = []
        for i in range(-1, 4):  # -1, 0, 1, 2, 3
            target_date = today + relativedelta(months=i)
            target_months.append((target_date.year, target_date.month))

        print(f"Debug: Target months: {target_months}")

        # 締め日が0日ではない支払元を取得
        payment_sources = db.query(models.PaymentSource).filter(
            models.PaymentSource.closing_day > 0
        ).all()

        print(f"Debug: Found {len(payment_sources)} payment sources with closing_day > 0")

        # 各支払元の支払日を計算
        payment_dates = []
        for source in payment_sources:
            print(f"Debug: Processing payment source: {source.name} (closing_day: {source.closing_day}, pay_month_diff: {source.pay_month_diff}, pay_day: {source.pay_day})")
            for year, month in target_months:
                # その月の支払日を計算
                payment_date = crud.calculate_payment_date_for_month(
                    year, month, source
                )
                if payment_date:
                    print(f"Debug: Calculated payment date for {year}-{month}: {payment_date}")
                    payment_dates.append({
                        'date': payment_date,
                        'source_name': source.name,
                        'source_id': source.id
                    })
                else:
                    print(f"Debug: No payment date calculated for {year}-{month}")

        print(f"Debug: Total payment dates calculated: {len(payment_dates)}")

        # 重複を除去してソート
        unique_dates = {}
        for item in payment_dates:
            date_key = item['date'].strftime('%Y-%m-%d')
            if date_key not in unique_dates:
                unique_dates[date_key] = item

        sorted_dates = sorted(unique_dates.values(), key=lambda x: x['date'])

        print(f"Debug: Unique payment dates after deduplication: {len(sorted_dates)}")
        for item in sorted_dates:
            print(f"Debug: Payment date: {item['date']}, Source: {item['source_name']}")

        # 各支払日の取引金額を集計
        result = []
        for item in sorted_dates:
            payment_date = item['date']

            # その支払日に関連する取引を取得
            transactions = db.query(models.Transaction).filter(
                models.Transaction.payment_source_id == item['source_id'],
                models.Transaction.paid_date == payment_date
            ).all()

            total_amount = sum(tx.amount for tx in transactions)

            result.append({
                'payment_date': payment_date.strftime('%Y-%m-%d'),
                'source_name': item['source_name'],
                'total_amount': float(total_amount),
                'transaction_count': len(transactions)
            })

        print(f"Debug: Final result count: {len(result)}")
        session_info = get_session_info(request)
        return schemas.ListResponse(processing_result=True, session_info=session_info, data=result)

    except Exception as e:
        print(f"Error in get_debit_summary: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



# 支払い期間の計算関数
def calculate_payment_periods(ulog: Log) -> rep_calculate_payment_periods:
    """現在日を基準に当月、翌月、翌々月の支払い期間を計算（23日～翌月22日）"""

    ulog.output("INF", "[ST] calculate_payment_periods()")

    today = date.today()
    ulog.output("DBG", "基準日=" + str(today))

    # 当月の期間（直近の過去の23日から直近の次の22日まで）
    if today.day >= 23:
        # 今月の23日から来月の22日まで
        current_month_start = date(today.year, today.month, 23)
        if today.month == 12:
            current_month_end = date(today.year + 1, 1, 22)
        else:
            current_month_end = date(today.year, today.month + 1, 22)
    else:
        # 先月の23日から今月の22日まで
        if today.month == 1:
            current_month_start = date(today.year - 1, 12, 23)
        else:
            current_month_start = date(today.year, today.month - 1, 23)
        current_month_end = date(today.year, today.month, 22)

    ulog.output("DBG", "基準期間 " + str(current_month_start) + "～" + str(current_month_end))

    # 翌月の期間
    next_month_start = current_month_end + relativedelta(days=1)
    next_month_end = next_month_start + relativedelta(months=1) - relativedelta(days=1)

    ulog.output("DBG", "翌月期間 " + str(next_month_start) + "～" + str(next_month_end))

    # 翌々月の期間
    next_next_month_start = next_month_end + relativedelta(days=1)
    next_next_month_end = next_next_month_start + relativedelta(months=1) - relativedelta(days=1)

    ulog.output("DBG", "翌々月期間 " + str(next_next_month_start) + "～" + str(next_next_month_end))


    ulog.output("INF", "[ED] calculate_payment_periods()")

    return {
        'current_month': {
            'start': current_month_start,
            'end': current_month_end,
            'label': f'{current_month_start.strftime("%m/%d")}～{current_month_end.strftime("%m/%d")}'
        },
        'next_month': {
            'start': next_month_start,
            'end': next_month_end,
            'label': f'{next_month_start.strftime("%m/%d")}～{next_month_end.strftime("%m/%d")}'
        },
        'next_next_month': {
            'start': next_next_month_start,
            'end': next_next_month_end,
            'label': f'{next_next_month_start.strftime("%m/%d")}～{next_next_month_end.strftime("%m/%d")}'
        }
    }
