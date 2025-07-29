from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import base64
import io
from PIL import Image
import cv2
import numpy as np
import pytesseract
import re
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import func

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
    """現在日を基準に当月、翌月、翌々月の支払い期間を計算"""
    today = date.today()

    # 当月の期間（直近の過去の24日から直近の次の23日まで）
    if today.day >= 24:
        # 今月の24日から来月の23日まで
        current_month_start = date(today.year, today.month, 24)
        if today.month == 12:
            current_month_end = date(today.year + 1, 1, 23)
        else:
            current_month_end = date(today.year, today.month + 1, 23)
    else:
        # 先月の24日から今月の23日まで
        if today.month == 1:
            current_month_start = date(today.year - 1, 12, 24)
        else:
            current_month_start = date(today.year, today.month - 1, 24)
        current_month_end = date(today.year, today.month, 23)

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

@app.get("/budget-names")
def get_budget_names(year: int, month: int, db: Session = Depends(get_db)):
    """指定年月の予算名称一覧を取得"""
    budgets = crud.get_budgets_by_year_month(db, target_year=year, target_month=month)
    names = [b.name for b in budgets]
    return {"names": names}

@app.get("/budgets/{year}/{month}/summary")
def get_budget_summaries(year: int, month: int, db: Session = Depends(get_db)):
    """指定年月の各予算名称ごとに支払日が対象期間内の取引合計金額を返す"""
    # 期間計算（24日～翌月23日）
    from datetime import date
    from dateutil.relativedelta import relativedelta
    start_date = date(year, month, 24)
    if month == 12:
        end_date = date(year + 1, 1, 23)
    else:
        end_date = date(year, month + 1, 23)
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