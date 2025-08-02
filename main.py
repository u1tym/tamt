from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import base64
import io
from PIL import Image
import cv2
import numpy as np
import pytesseract
import re
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from database import SessionLocal, engine
import models
import crud
import schemas

# データベーステーブルを作成
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データベースセッションの依存関係
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 支払い期間の計算関数
def calculate_payment_periods():
    """現在日を基準に当月、翌月、翌々月の支払い期間を計算（23日～翌月22日）"""
    today = date.today()

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

    # 翌月の期間
    next_month_start = current_month_end + relativedelta(days=1)
    next_month_end = next_month_start + relativedelta(months=1) - relativedelta(days=1)

    # 翌々月の期間
    next_next_month_start = next_month_end + relativedelta(days=1)
    next_next_month_end = next_next_month_start + relativedelta(months=1) - relativedelta(days=1)

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

@app.get("/payment-summary")
def get_payment_summary(db: Session = Depends(get_db)):
    """支払い額の集計を取得"""
    try:
        # 支払い期間を計算
        periods = calculate_payment_periods()

        # 各期間の支払い額を集計
        summary = {}

        for period_name, period_data in periods.items():
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

        return summary

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"支払い集計の取得に失敗しました: {str(e)}")

# レシート解析関数
def parse_receipt(image_data: bytes) -> dict:
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

@app.post("/parse-receipt")
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
@app.get("/transactions", response_model=List[schemas.Transaction])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transactions = crud.get_transactions(db, skip=skip, limit=limit)
    return transactions

@app.post("/transactions", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db=db, tx=transaction)

@app.put("/transactions/{transaction_id}", response_model=schemas.Transaction)
def update_transaction(transaction_id: int, transaction: schemas.TransactionUpdate, db: Session = Depends(get_db)):
    db_transaction = crud.get_transaction(db, tx_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return crud.update_transaction(db=db, tx_id=transaction_id, tx=transaction)

@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    db_transaction = crud.get_transaction(db, tx_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    crud.delete_transaction(db=db, transaction_id=transaction_id)
    return {"message": "Transaction deleted successfully"}

@app.get("/payment_sources", response_model=List[schemas.PaymentSource])
def read_payment_sources(db: Session = Depends(get_db)):
    payment_sources = crud.get_payment_sources(db)
    return payment_sources

@app.post("/payment_sources", response_model=schemas.PaymentSource)
def create_payment_source(payment_source: schemas.PaymentSourceCreate, db: Session = Depends(get_db)):
    return crud.create_payment_source(db=db, source=payment_source)

@app.put("/payment_sources/{payment_source_id}", response_model=schemas.PaymentSource)
def update_payment_source(payment_source_id: int, payment_source: schemas.PaymentSourceCreate, db: Session = Depends(get_db)):
    db_payment_source = crud.get_payment_source(db, source_id=payment_source_id)
    if db_payment_source is None:
        raise HTTPException(status_code=404, detail="Payment source not found")
    return crud.update_payment_source(db=db, source_id=payment_source_id, source=payment_source)

@app.delete("/payment_sources/{payment_source_id}")
def delete_payment_source(payment_source_id: int, db: Session = Depends(get_db)):
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
    return {"message": "Payment source deleted successfully"}

# Budget API endpoints

@app.get("/budgets/{target_year}/{target_month}", response_model=List[schemas.Budget])
def read_budgets_by_year_month(target_year: int, target_month: int, db: Session = Depends(get_db)):
    """指定された年月の予算一覧を取得"""
    if target_month < 1 or target_month > 12:
        raise HTTPException(status_code=400, detail="月は1～12の範囲で指定してください")

    budgets = crud.get_budgets_by_year_month(db, target_year=target_year, target_month=target_month)
    return budgets

@app.post("/budgets", response_model=schemas.Budget)
def create_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_db)):
    """新規予算を作成"""
    if budget.target_month < 1 or budget.target_month > 12:
        raise HTTPException(status_code=400, detail="月は1～12の範囲で指定してください")

    return crud.create_budget(db=db, budget=budget)

@app.put("/budgets/{budget_id}", response_model=schemas.Budget)
def update_budget(budget_id: int, budget: schemas.BudgetUpdate, db: Session = Depends(get_db)):
    """予算を更新"""
    db_budget = crud.get_budget(db, budget_id=budget_id)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")

    # 月の範囲チェック
    if budget.target_month is not None and (budget.target_month < 1 or budget.target_month > 12):
        raise HTTPException(status_code=400, detail="月は1～12の範囲で指定してください")

    return crud.update_budget(db=db, budget_id=budget_id, budget=budget)

@app.delete("/budgets/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    """予算を削除"""
    db_budget = crud.get_budget(db, budget_id=budget_id)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")

    crud.delete_budget(db=db, budget_id=budget_id)
    return {"message": "Budget deleted successfully"}

@app.post("/budgets/copy")
def copy_budgets(source_year: int, source_month: int, target_year: int, target_month: int, db: Session = Depends(get_db)):
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

    return {
        "message": f"{source_year}年{source_month}月の予算を{target_year}年{target_month}月にコピーしました",
        "copied_count": len(copied_budgets)
    }

@app.post("/budgets/{budget_id}/move-up")
def move_budget_up(budget_id: int, db: Session = Depends(get_db)):
    """予算を上に移動"""
    db_budget = crud.get_budget(db, budget_id=budget_id)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")

    updated_budget = crud.move_budget_up(db=db, budget_id=budget_id)
    if updated_budget is None:
        raise HTTPException(status_code=400, detail="既に最上部にあります")

    return {"message": "予算を上に移動しました"}

@app.post("/budgets/{budget_id}/move-down")
def move_budget_down(budget_id: int, db: Session = Depends(get_db)):
    """予算を下に移動"""
    db_budget = crud.get_budget(db, budget_id=budget_id)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")

    updated_budget = crud.move_budget_down(db=db, budget_id=budget_id)
    if updated_budget is None:
        raise HTTPException(status_code=400, detail="既に最下部にあります")

    return {"message": "予算を下に移動しました"}

@app.post("/calculate-payment-date")
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

@app.get("/budget-names")
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

@app.get("/budgets/{year}/{month}/summary")
def get_budget_summaries(year: int, month: int, db: Session = Depends(get_db)):
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
    return [{"name": r.budget_name, "total": float(r.total or 0)} for r in results]

@app.get("/debit-summary")
def get_debit_summary(db: Session = Depends(get_db)):
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
        return result
        
    except Exception as e:
        print(f"Error in get_debit_summary: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Knowhow API endpoints

@app.get("/knowhows", response_model=List[schemas.Knowhow])
def read_knowhows(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """KNOWHOW一覧を取得"""
    try:
        knowhows = crud.get_knowhows(db, skip=skip, limit=limit)
        return knowhows
    except Exception as e:
        print(f"KNOWHOW list error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/knowhows/test")
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

@app.get("/knowhows/search")
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

@app.get("/knowhows/tree")
def get_knowhow_tree(db: Session = Depends(get_db)):
    """KNOWHOWのツリー構造を取得"""
    print("KNOWHOW tree endpoint called")
    try:
        print("Calling crud.get_knowhow_tree...")
        tree = crud.get_knowhow_tree(db)
        print(f"Tree result: {tree}")
        return tree
    except Exception as e:
        print(f"KNOWHOW tree error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/knowhows/{knowhow_id}", response_model=schemas.Knowhow)
def read_knowhow(knowhow_id: int, db: Session = Depends(get_db)):
    """特定のKNOWHOWを取得"""
    knowhow = crud.get_knowhow(db, knowhow_id=knowhow_id)
    if knowhow is None:
        raise HTTPException(status_code=404, detail="Knowhow not found")
    return knowhow

@app.post("/knowhows", response_model=schemas.Knowhow)
def create_knowhow(knowhow: schemas.KnowhowCreate, db: Session = Depends(get_db)):
    """新しいKNOWHOWを作成"""
    return crud.create_knowhow(db=db, knowhow=knowhow)

@app.put("/knowhows/{knowhow_id}", response_model=schemas.Knowhow)
def update_knowhow(knowhow_id: int, knowhow: schemas.KnowhowUpdate, db: Session = Depends(get_db)):
    """KNOWHOWを更新"""
    db_knowhow = crud.update_knowhow(db, knowhow_id=knowhow_id, knowhow=knowhow)
    if db_knowhow is None:
        raise HTTPException(status_code=404, detail="Knowhow not found")
    return db_knowhow

@app.delete("/knowhows/{knowhow_id}")
def delete_knowhow(knowhow_id: int, db: Session = Depends(get_db)):
    """KNOWHOWを削除（論理削除）"""
    success = crud.delete_knowhow(db, knowhow_id=knowhow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Knowhow not found")
    return {"message": "Knowhow deleted successfully"}

@app.post("/knowhows/{knowhow_id}/move-up")
def move_knowhow_up(knowhow_id: int, db: Session = Depends(get_db)):
    """KNOWHOWを上に移動"""
    knowhow = crud.move_knowhow_up(db, knowhow_id=knowhow_id)
    if knowhow is None:
        raise HTTPException(status_code=404, detail="Knowhow not found")
    return {"message": "Knowhow moved up successfully"}

@app.post("/knowhows/{knowhow_id}/move-down")
def move_knowhow_down(knowhow_id: int, db: Session = Depends(get_db)):
    """KNOWHOWを下に移動"""
    knowhow = crud.move_knowhow_down(db, knowhow_id=knowhow_id)
    if knowhow is None:
        raise HTTPException(status_code=404, detail="Knowhow not found")
    return {"message": "Knowhow moved down successfully"}

# 大項目管理エンドポイント
@app.get("/major-categories", response_model=List[schemas.MajorCategory])
def read_major_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """大項目一覧を取得"""
    return crud.get_major_categories(db, skip=skip, limit=limit)

@app.get("/major-categories/{major_category_id}", response_model=schemas.MajorCategory)
def read_major_category(major_category_id: int, db: Session = Depends(get_db)):
    """特定の大項目を取得"""
    major_category = crud.get_major_category(db, major_category_id=major_category_id)
    if major_category is None:
        raise HTTPException(status_code=404, detail="Major category not found")
    return major_category

@app.post("/major-categories", response_model=schemas.MajorCategory)
def create_major_category(major_category: schemas.MajorCategoryCreate, db: Session = Depends(get_db)):
    """新しい大項目を作成"""
    return crud.create_major_category(db=db, major_category=major_category)

@app.put("/major-categories/{major_category_id}", response_model=schemas.MajorCategory)
def update_major_category(major_category_id: int, major_category: schemas.MajorCategoryUpdate, db: Session = Depends(get_db)):
    """大項目を更新"""
    db_major_category = crud.update_major_category(db, major_category_id=major_category_id, major_category=major_category)
    if db_major_category is None:
        raise HTTPException(status_code=404, detail="Major category not found")
    return db_major_category

@app.delete("/major-categories/{major_category_id}")
def delete_major_category(major_category_id: int, db: Session = Depends(get_db)):
    """大項目を削除（論理削除）"""
    success = crud.delete_major_category(db, major_category_id=major_category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Major category not found")
    return {"message": "Major category deleted successfully"}

# 中項目管理エンドポイント
@app.get("/major-categories/{major_category_id}/middle-categories", response_model=List[schemas.MiddleCategory])
def read_middle_categories(major_category_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """中項目一覧を取得"""
    return crud.get_middle_categories(db, major_category_id=major_category_id, skip=skip, limit=limit)

@app.get("/middle-categories", response_model=List[schemas.MiddleCategory])
def read_all_middle_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """全中項目一覧を取得"""
    return crud.get_all_middle_categories(db, skip=skip, limit=limit)

@app.get("/middle-categories/{middle_category_id}", response_model=schemas.MiddleCategory)
def read_middle_category(middle_category_id: int, db: Session = Depends(get_db)):
    """特定の中項目を取得"""
    middle_category = crud.get_middle_category(db, middle_category_id=middle_category_id)
    if middle_category is None:
        raise HTTPException(status_code=404, detail="Middle category not found")
    return middle_category

@app.post("/middle-categories", response_model=schemas.MiddleCategory)
def create_middle_category(middle_category: schemas.MiddleCategoryCreate, db: Session = Depends(get_db)):
    """新しい中項目を作成"""
    return crud.create_middle_category(db=db, middle_category=middle_category)

@app.put("/middle-categories/{middle_category_id}", response_model=schemas.MiddleCategory)
def update_middle_category(middle_category_id: int, middle_category: schemas.MiddleCategoryUpdate, db: Session = Depends(get_db)):
    """中項目を更新"""
    db_middle_category = crud.update_middle_category(db, middle_category_id=middle_category_id, middle_category=middle_category)
    if db_middle_category is None:
        raise HTTPException(status_code=404, detail="Middle category not found")
    return db_middle_category

@app.delete("/middle-categories/{middle_category_id}")
def delete_middle_category(middle_category_id: int, db: Session = Depends(get_db)):
    """中項目を削除（論理削除）"""
    success = crud.delete_middle_category(db, middle_category_id=middle_category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Middle category not found")
    return {"message": "Middle category deleted successfully"}

# GOODS管理システム用のAPIエンドポイント

# Person API
@app.get("/persons", response_model=List[schemas.Person])
def read_persons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_persons(db, skip=skip, limit=limit)

@app.get("/persons/{person_id}", response_model=schemas.Person)
def read_person(person_id: int, db: Session = Depends(get_db)):
    person = crud.get_person(db, person_id=person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

@app.post("/persons", response_model=schemas.Person)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    return crud.create_person(db=db, person=person)

@app.put("/persons/{person_id}", response_model=schemas.Person)
def update_person(person_id: int, person: schemas.PersonUpdate, db: Session = Depends(get_db)):
    updated_person = crud.update_person(db=db, person_id=person_id, person=person)
    if updated_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return updated_person

# Artist API
@app.get("/artists", response_model=List[schemas.Artist])
def read_artists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_artists(db, skip=skip, limit=limit)

@app.get("/artists/{artist_id}", response_model=schemas.Artist)
def read_artist(artist_id: int, db: Session = Depends(get_db)):
    artist = crud.get_artist(db, artist_id=artist_id)
    if artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist

@app.get("/artists/{artist_id}/with-persons")
def read_artist_with_persons(artist_id: int, db: Session = Depends(get_db)):
    artist_with_persons = crud.get_artist_with_persons(db, artist_id=artist_id)
    if artist_with_persons is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist_with_persons

@app.post("/artists", response_model=schemas.Artist)
def create_artist(artist: schemas.ArtistCreate, db: Session = Depends(get_db)):
    return crud.create_artist(db=db, artist=artist)

@app.put("/artists/{artist_id}", response_model=schemas.Artist)
def update_artist(artist_id: int, artist: schemas.ArtistUpdate, db: Session = Depends(get_db)):
    updated_artist = crud.update_artist(db=db, artist_id=artist_id, artist=artist)
    if updated_artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    return updated_artist

# Media API
@app.get("/media", response_model=List[schemas.Media])
def read_media_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_media_list(db, skip=skip, limit=limit)

@app.get("/media/{media_id}", response_model=schemas.Media)
def read_media(media_id: int, db: Session = Depends(get_db)):
    media = crud.get_media(db, media_id=media_id)
    if media is None:
        raise HTTPException(status_code=404, detail="Media not found")
    return media

@app.post("/media", response_model=schemas.Media)
def create_media(media: schemas.MediaCreate, db: Session = Depends(get_db)):
    return crud.create_media(db=db, media=media)

@app.put("/media/{media_id}", response_model=schemas.Media)
def update_media(media_id: int, media: schemas.MediaUpdate, db: Session = Depends(get_db)):
    updated_media = crud.update_media(db=db, media_id=media_id, media=media)
    if updated_media is None:
        raise HTTPException(status_code=404, detail="Media not found")
    return updated_media

# Goods API
@app.get("/goods", response_model=List[schemas.Goods])
def read_goods_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_goods_list(db, skip=skip, limit=limit)

@app.get("/goods/{goods_id}", response_model=schemas.Goods)
def read_goods(goods_id: int, db: Session = Depends(get_db)):
    goods = crud.get_goods(db, goods_id=goods_id)
    if goods is None:
        raise HTTPException(status_code=404, detail="Goods not found")
    return goods

@app.get("/goods/{goods_id}/with-details")
def read_goods_with_details(goods_id: int, db: Session = Depends(get_db)):
    goods_with_details = crud.get_goods_with_details(db, goods_id=goods_id)
    if goods_with_details is None:
        raise HTTPException(status_code=404, detail="Goods not found")
    return goods_with_details

@app.post("/goods", response_model=schemas.Goods)
def create_goods(goods: schemas.GoodsCreate, db: Session = Depends(get_db)):
    return crud.create_goods(db=db, goods=goods)

@app.put("/goods/{goods_id}", response_model=schemas.Goods)
def update_goods(goods_id: int, goods: schemas.GoodsUpdate, db: Session = Depends(get_db)):
    updated_goods = crud.update_goods(db=db, goods_id=goods_id, goods=goods)
    if updated_goods is None:
        raise HTTPException(status_code=404, detail="Goods not found")
    return updated_goods

@app.delete("/goods/{goods_id}")
def delete_goods(goods_id: int, db: Session = Depends(get_db)):
    success = crud.delete_goods(db=db, goods_id=goods_id)
    if not success:
        raise HTTPException(status_code=404, detail="Goods not found")
    return {"message": "Goods deleted successfully"}

# 画像取得API
@app.get("/goods/{goods_id}/images/{image_id}")
def get_goods_image(goods_id: int, image_id: int, db: Session = Depends(get_db)):
    """GOODS画像を取得"""
    from fastapi.responses import Response
    from fastapi import HTTPException

    goods_image = db.query(models.GoodsImage).filter(
        models.GoodsImage.id == image_id,
        models.GoodsImage.goods_id == goods_id
    ).first()

    if not goods_image:
        raise HTTPException(status_code=404, detail="Image not found")

    return Response(content=goods_image.image_data, media_type=goods_image.image_type)

# スケジュール管理用のAPIエンドポイント

# ActivityCategory API
@app.get("/activity-categories", response_model=List[schemas.ActivityCategory])
def read_activity_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """活動区分一覧を取得"""
    return crud.get_activity_categories(db, skip=skip, limit=limit)

@app.get("/activity-categories/{activity_category_id}", response_model=schemas.ActivityCategory)
def read_activity_category(activity_category_id: int, db: Session = Depends(get_db)):
    """特定の活動区分を取得"""
    db_activity_category = crud.get_activity_category(db, activity_category_id=activity_category_id)
    if db_activity_category is None:
        raise HTTPException(status_code=404, detail="Activity category not found")
    return db_activity_category

@app.post("/activity-categories", response_model=schemas.ActivityCategory)
def create_activity_category(activity_category: schemas.ActivityCategoryCreate, db: Session = Depends(get_db)):
    """活動区分を作成"""
    return crud.create_activity_category(db=db, activity_category=activity_category)

@app.put("/activity-categories/{activity_category_id}", response_model=schemas.ActivityCategory)
def update_activity_category(activity_category_id: int, activity_category: schemas.ActivityCategoryUpdate, db: Session = Depends(get_db)):
    """活動区分を更新"""
    db_activity_category = crud.update_activity_category(db, activity_category_id=activity_category_id, activity_category=activity_category)
    if db_activity_category is None:
        raise HTTPException(status_code=404, detail="Activity category not found")
    return db_activity_category

@app.delete("/activity-categories/{activity_category_id}")
def delete_activity_category(activity_category_id: int, db: Session = Depends(get_db)):
    """活動区分を削除"""
    success = crud.delete_activity_category(db, activity_category_id=activity_category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Activity category not found")
    return {"message": "Activity category deleted successfully"}

# Schedule API
@app.get("/schedules", response_model=List[schemas.Schedule])
def read_schedules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """スケジュール一覧を取得"""
    return crud.get_schedules(db, skip=skip, limit=limit)

@app.get("/schedules/month/{year}/{month}", response_model=List[schemas.ScheduleWithCategory])
def read_schedules_by_month(year: int, month: int, db: Session = Depends(get_db)):
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
    return result

@app.get("/schedules/filtered/{year}/{month}")
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

@app.get("/schedules/week/{start_date}")
def read_schedules_by_week(start_date: str, db: Session = Depends(get_db)):
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
        return result
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

@app.get("/schedules/{schedule_id}", response_model=schemas.ScheduleWithCategory)
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

@app.post("/schedules", response_model=schemas.Schedule)
def create_schedule(schedule: schemas.ScheduleCreate, db: Session = Depends(get_db)):
    """スケジュールを作成"""
    return crud.create_schedule(db=db, schedule=schedule)

@app.put("/schedules/{schedule_id}", response_model=schemas.Schedule)
def update_schedule(schedule_id: int, schedule: schemas.ScheduleUpdate, db: Session = Depends(get_db)):
    """スケジュールを更新"""
    db_schedule = crud.update_schedule(db, schedule_id=schedule_id, schedule=schedule)
    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule

@app.delete("/schedules/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """スケジュールを削除"""
    success = crud.delete_schedule(db, schedule_id=schedule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"message": "Schedule deleted successfully"}

# 休日管理のエンドポイント
@app.get("/holidays", response_model=List[schemas.Holiday])
def get_holidays(db: Session = Depends(get_db)):
    holidays = db.query(models.Holiday).order_by(models.Holiday.date).all()
    return holidays

@app.get("/holidays/month/{year}/{month}", response_model=List[schemas.Holiday])
def get_holidays_by_month(year: int, month: int, db: Session = Depends(get_db)):
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    holidays = db.query(models.Holiday).filter(
        models.Holiday.date >= start_date,
        models.Holiday.date <= end_date
    ).order_by(models.Holiday.date).all()
    return holidays

@app.post("/holidays", response_model=schemas.Holiday)
def create_holiday(holiday: schemas.HolidayCreate, db: Session = Depends(get_db)):
    db_holiday = models.Holiday(**holiday.dict())
    db.add(db_holiday)
    try:
        db.commit()
        db.refresh(db_holiday)
        return db_holiday
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="この日付は既に休日として登録されています")

@app.put("/holidays/{holiday_id}", response_model=schemas.Holiday)
def update_holiday(holiday_id: int, holiday: schemas.HolidayUpdate, db: Session = Depends(get_db)):
    db_holiday = db.query(models.Holiday).filter(models.Holiday.id == holiday_id).first()
    if not db_holiday:
        raise HTTPException(status_code=404, detail="休日が見つかりません")

    for key, value in holiday.dict().items():
        setattr(db_holiday, key, value)

    try:
        db.commit()
        db.refresh(db_holiday)
        return db_holiday
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="この日付は既に休日として登録されています")

@app.delete("/holidays/{holiday_id}")
def delete_holiday(holiday_id: int, db: Session = Depends(get_db)):
    db_holiday = db.query(models.Holiday).filter(models.Holiday.id == holiday_id).first()
    if not db_holiday:
        raise HTTPException(status_code=404, detail="休日が見つかりません")

    db.delete(db_holiday)
    db.commit()
    return {"message": "休日を削除しました"}

if __name__ == "__main__":
    import uvicorn
    import ssl
    import os

    # 現在のディレクトリを取得
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cert_file = os.path.join(current_dir, "frontend", "localhost.pem")
    key_file = os.path.join(current_dir, "frontend", "localhost-key.pem")

    # 証明書ファイルの存在確認
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("HTTPS証明書を読み込みました")
        print(f"証明書: {cert_file}")
        print(f"鍵: {key_file}")
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8001,
            reload=True,
            ssl_certfile=cert_file,
            ssl_keyfile=key_file
        )
    else:
        print("HTTPS証明書が見つかりません")
        print(f"証明書ファイル: {cert_file}")
        print(f"鍵ファイル: {key_file}")
        print("HTTPで起動します")
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8001,
            reload=True
        )