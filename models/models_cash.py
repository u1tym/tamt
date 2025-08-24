from .models_base import Base, Integer, String, Date, DateTime, func, Mapped, mapped_column, List, datetime, datetime_date

class PaymentSource(Base):
    __tablename__ = 'payment_sources'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    closing_day: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 締め日
    pay_month_diff: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 支払い月までの差分
    pay_day: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 支払い日
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="payment_source")

class Transaction(Base):
    __tablename__ = 'transactions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    used_date: Mapped[datetime_date] = mapped_column(Date, nullable=False)  # 使用日
    purpose: Mapped[str] = mapped_column(String, nullable=False)  # 用途
    memo: Mapped[str] = mapped_column(String)  # メモ
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # 金額
    payment_source_id: Mapped[int] = mapped_column(Integer, ForeignKey('payment_sources.id'), nullable=False)  # 支出元
    payment_source: Mapped[List["PaymentSource"]] = relationship("PaymentSource", back_populates="transactions")
    paid_date: Mapped[datetime_date] = mapped_column(Date, nullable=False)  # 支払日（自動計算）
    budget_name: Mapped[str] = mapped_column(String, nullable=False, default='未分類')  # 予算名称（追加）
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時

class Budget(Base):
    __tablename__ = 'budgets'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    target_year: Mapped[int] = mapped_column(Integer, nullable=False)  # 対象年
    target_month: Mapped[int] = mapped_column(Integer, nullable=False)  # 対象月
    name: Mapped[str] = mapped_column(String, nullable=False)  # 名称
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # 金額
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 表示順序
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
