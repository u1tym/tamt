from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Numeric, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class PaymentSource(Base):
    __tablename__ = 'payment_sources'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    closing_day = Column(Integer, nullable=False, default=0)  # 締め日
    pay_month_diff = Column(Integer, nullable=False, default=0)  # 支払い月までの差分
    pay_day = Column(Integer, nullable=False, default=0)  # 支払い日
    transactions = relationship("Transaction", back_populates="payment_source")

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, index=True)
    used_date = Column(Date, nullable=False)  # 使用日
    purpose = Column(String, nullable=False)  # 用途
    memo = Column(String)  # メモ
    amount = Column(Numeric, nullable=False)  # 金額
    payment_source_id = Column(Integer, ForeignKey('payment_sources.id'), nullable=False)  # 支出元
    payment_source = relationship("PaymentSource", back_populates="transactions")
    paid_date = Column(Date, nullable=False)  # 支払日（自動計算）
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時

class Budget(Base):
    __tablename__ = 'budgets'
    id = Column(Integer, primary_key=True, index=True)
    target_year = Column(Integer, nullable=False)  # 対象年
    target_month = Column(Integer, nullable=False)  # 対象月
    name = Column(String, nullable=False)  # 名称
    amount = Column(Numeric, nullable=False)  # 金額
    order_index = Column(Integer, nullable=False, default=0)  # 表示順序
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時