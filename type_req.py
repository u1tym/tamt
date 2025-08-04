from typing import TypedDict
from datetime import date

from sqlalchemy import Column
from typing import Union
from typing import Literal
from typing import Optional


class rep_calculate_payment_periods_rec(TypedDict):
    start: date
    end: date
    label: str

class rep_calculate_payment_periods(TypedDict):
    current_month: rep_calculate_payment_periods_rec
    next_month: rep_calculate_payment_periods_rec
    next_next_month: rep_calculate_payment_periods_rec

class rep_get_payment_summary_rec(TypedDict):
    period: str
    start_date: str
    end_date: str
    total_amount: Union[Column[int], Literal[0]]
    transaction_count: int

class rep_parse_receipt_base(TypedDict):
    used_date: Optional[str]
    purpose: Optional[str]
    amount: Optional[int]
    raw_text: str
    confidence: float

class rep_parse_recipt(rep_parse_receipt_base, total=False):
    note: str
    error: str
