from sqlalchemy import Integer, String, Date, DateTime, ForeignKey, func, Text, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from datetime import date as datetime_date

from sqlalchemy.orm import Mapped, mapped_column
from typing import List
from typing import Optional, Union

Base = declarative_base()

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

class MajorCategory(Base):
    __tablename__ = 'major_categories'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)  # 大項目名
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 表示順
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # 削除フラグ
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
    middle_categories: Mapped[List["MiddleCategory"]] = relationship("MiddleCategory", back_populates="major_category")

class MiddleCategory(Base):
    __tablename__ = 'middle_categories'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    major_category_id: Mapped[int] = mapped_column(Integer, ForeignKey('major_categories.id'), nullable=False)  # 大項目ID
    name: Mapped[str] = mapped_column(String, nullable=False)  # 中項目名
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 表示順
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # 削除フラグ
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
    major_category: Mapped[List["MajorCategory"]] = relationship("MajorCategory", back_populates="middle_categories")
    knowhows: Mapped[List["Knowhow"]] = relationship("Knowhow", back_populates="middle_category")

class Knowhow(Base):
    __tablename__ = 'knowhows'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    middle_category_id: Mapped[int] = mapped_column(Integer, ForeignKey('middle_categories.id'), nullable=False)  # 中項目ID
    title: Mapped[str] = mapped_column(String, nullable=False)  # タイトル
    keywords: Mapped[str] = mapped_column(String)  # キーワード
    content: Mapped[str] = mapped_column(Text, nullable=False)  # 本文
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 表示順
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # 削除フラグ
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
    middle_category: Mapped[List["MiddleCategory"]] = relationship("MiddleCategory", back_populates="knowhows")

# GOODS管理システム用のテーブル
class Person(Base):
    __tablename__ = 'persons'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)  # 名前
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
    # アーティストとの関係
    artist_persons: Mapped[List["ArtistPerson"]] = relationship("ArtistPerson", back_populates="person")

class Artist(Base):
    __tablename__ = 'artists'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)  # アーティスト名
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
    # パーソンとの関係
    artist_persons: Mapped[List["ArtistPerson"]] = relationship("ArtistPerson", back_populates="artist")
    # GOODSとの関係
    goods: Mapped[List["Goods"]] = relationship("Goods", back_populates="artist")

class ArtistPerson(Base):
    __tablename__ = 'artist_persons'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    artist_id: Mapped[int] = mapped_column(Integer, ForeignKey('artists.id'), nullable=False)  # アーティストID
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey('persons.id'), nullable=False)  # パーソンID
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    # 関係
    artist: Mapped[List["Artist"]] = relationship("Artist", back_populates="artist_persons")
    person: Mapped[List["Person"]] = relationship("Person", back_populates="artist_persons")

class Media(Base):
    __tablename__ = 'media'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)  # メディア名称
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
    # GOODSとの関係
    goods: Mapped[List["Goods"]] = relationship("Goods", back_populates="media")

class Goods(Base):
    __tablename__ = 'goods'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    media_id: Mapped[int] = mapped_column(Integer, ForeignKey('media.id'), nullable=False)  # メディアID
    artist_id: Mapped[int] = mapped_column(Integer, ForeignKey('artists.id'), nullable=False)  # アーティストID
    title: Mapped[str] = mapped_column(String, nullable=False)  # タイトル
    release_date: Mapped[datetime_date] = mapped_column(Date, nullable=False)  # リリース年月日
    memo: Mapped[str] = mapped_column(Text)  # メモ
    is_owned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # 所持フラグ
    code_number: Mapped[str] = mapped_column(String)  # コード番号
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # 削除フラグ
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
    # 関係
    media: Mapped[List["Media"]] = relationship("Media", back_populates="goods")
    artist: Mapped[List["Artist"]] = relationship("Artist", back_populates="goods")
    images: Mapped[List["GoodsImage"]] = relationship("GoodsImage", back_populates="goods", cascade="all, delete-orphan")

class GoodsImage(Base):
    __tablename__ = 'goods_images'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    goods_id: Mapped[int] = mapped_column(Integer, ForeignKey('goods.id'), nullable=False)  # GOODS ID
    image_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)  # 画像データ
    image_type: Mapped[str] = mapped_column(String, nullable=False)  # 画像タイプ（MIME type）
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 表示順序
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    # 関係
    goods: Mapped[List["Goods"]] = relationship("Goods", back_populates="images")

# スケジュール管理用のテーブル
class ActivityCategory(Base):
    __tablename__ = 'activity_categories'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)  # 活動区分名称
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # 削除フラグ
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
    # スケジュールとの関係
    schedules: Mapped[List["Schedule"]] = relationship("Schedule", back_populates="activity_category")

class Schedule(Base):
    __tablename__ = 'schedules'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)  # タイトル
    start_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # 開始日（時）
    duration: Mapped[int] = mapped_column(Integer, nullable=False)  # 所要時間（分または日）
    is_all_day: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # 終日フラグ
    activity_category_id: Mapped[int] = mapped_column(Integer, ForeignKey('activity_categories.id'), nullable=False)  # 活動区分ID
    schedule_type: Mapped[str] = mapped_column(String, nullable=False)  # スケジュールタイプ（予定/TODO）
    location: Mapped[str] = mapped_column(String)  # 場所
    details: Mapped[str] = mapped_column(Text)  # 詳細
    is_todo_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # TODO実施済み
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # 削除フラグ
    created_at: Mapped[bool] = mapped_column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
    # 活動区分との関係
    activity_category: Mapped[List["ActivityCategory"]] = relationship("ActivityCategory", back_populates="schedules")

class Holiday(Base):
    __tablename__ = "holidays"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[datetime_date] = mapped_column(Date, nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=(lambda: datetime.now(timezone.utc)))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=(lambda: datetime.now(timezone.utc)), onupdate=(lambda: datetime.now(timezone.utc)))

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)  # ユーザー名
    password: Mapped[str] = mapped_column(String, nullable=False)  # パスワード（ハッシュ化されたもの）
    session_info: Mapped[str] = mapped_column(Text)  # セッション情報（JSON形式で保存）
    last_access: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=(lambda: datetime.now(timezone.utc)))  # 最終アクセス日時
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # 削除フラグ
    random_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # ランダム数
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時