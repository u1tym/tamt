from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta, timezone
import models
import schemas
from PIL import Image
import io

from typing import Optional

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

    # 締め日を基準に支払日を計算
    closing_date = date(year, month, closing_day)
    paid_date = calculate_paid_date(
        used_date=closing_date,
        closing_day=payment_source.closing_day,
        pay_month_diff=payment_source.pay_month_diff,
        pay_day=payment_source.pay_day
    )

    print(f"Debug: Closing date: {closing_date}, paid_date: {paid_date}")
    return paid_date

def resize_image(image_data: bytes, max_size: int = 800) -> bytes:
    """画像をリサイズする"""
    try:
        # 画像を開く
        image = Image.open(io.BytesIO(image_data))

        # アスペクト比を保ってリサイズ
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        # バイトデータに変換
        output = io.BytesIO()
        image.save(output, format=image.format or 'JPEG', quality=85)
        return output.getvalue()
    except Exception as e:
        print(f"画像リサイズエラー: {e}")
        return image_data
