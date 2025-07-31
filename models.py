from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, func, Text, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

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
    amount = Column(Integer, nullable=False)  # 金額
    payment_source_id = Column(Integer, ForeignKey('payment_sources.id'), nullable=False)  # 支出元
    payment_source = relationship("PaymentSource", back_populates="transactions")
    paid_date = Column(Date, nullable=False)  # 支払日（自動計算）
    budget_name = Column(String, nullable=False, default='未分類')  # 予算名称（追加）
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時

class Budget(Base):
    __tablename__ = 'budgets'
    id = Column(Integer, primary_key=True, index=True)
    target_year = Column(Integer, nullable=False)  # 対象年
    target_month = Column(Integer, nullable=False)  # 対象月
    name = Column(String, nullable=False)  # 名称
    amount = Column(Integer, nullable=False)  # 金額
    order_index = Column(Integer, nullable=False, default=0)  # 表示順序
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時

class MajorCategory(Base):
    __tablename__ = 'major_categories'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)  # 大項目名
    display_order = Column(Integer, nullable=False, default=0)  # 表示順
    is_deleted = Column(Boolean, nullable=False, default=False)  # 削除フラグ
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
    middle_categories = relationship("MiddleCategory", back_populates="major_category")

class MiddleCategory(Base):
    __tablename__ = 'middle_categories'
    id = Column(Integer, primary_key=True, index=True)
    major_category_id = Column(Integer, ForeignKey('major_categories.id'), nullable=False)  # 大項目ID
    name = Column(String, nullable=False)  # 中項目名
    display_order = Column(Integer, nullable=False, default=0)  # 表示順
    is_deleted = Column(Boolean, nullable=False, default=False)  # 削除フラグ
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
    major_category = relationship("MajorCategory", back_populates="middle_categories")
    knowhows = relationship("Knowhow", back_populates="middle_category")

class Knowhow(Base):
    __tablename__ = 'knowhows'
    id = Column(Integer, primary_key=True, index=True)
    middle_category_id = Column(Integer, ForeignKey('middle_categories.id'), nullable=False)  # 中項目ID
    title = Column(String, nullable=False)  # タイトル
    keywords = Column(String)  # キーワード
    content = Column(Text, nullable=False)  # 本文
    display_order = Column(Integer, nullable=False, default=0)  # 表示順
    is_deleted = Column(Boolean, nullable=False, default=False)  # 削除フラグ
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
    middle_category = relationship("MiddleCategory", back_populates="knowhows")

# GOODS管理システム用のテーブル
class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # 名前
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
    # アーティストとの関係
    artist_persons = relationship("ArtistPerson", back_populates="person")

class Artist(Base):
    __tablename__ = 'artists'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # アーティスト名
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
    # パーソンとの関係
    artist_persons = relationship("ArtistPerson", back_populates="artist")
    # GOODSとの関係
    goods = relationship("Goods", back_populates="artist")

class ArtistPerson(Base):
    __tablename__ = 'artist_persons'
    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False)  # アーティストID
    person_id = Column(Integer, ForeignKey('persons.id'), nullable=False)  # パーソンID
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    # 関係
    artist = relationship("Artist", back_populates="artist_persons")
    person = relationship("Person", back_populates="artist_persons")

class Media(Base):
    __tablename__ = 'media'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # メディア名称
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
    # GOODSとの関係
    goods = relationship("Goods", back_populates="media")

class Goods(Base):
    __tablename__ = 'goods'
    id = Column(Integer, primary_key=True, index=True)
    media_id = Column(Integer, ForeignKey('media.id'), nullable=False)  # メディアID
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False)  # アーティストID
    title = Column(String, nullable=False)  # タイトル
    release_date = Column(Date, nullable=False)  # リリース年月日
    memo = Column(Text)  # メモ
    is_owned = Column(Boolean, nullable=False, default=False)  # 所持フラグ
    code_number = Column(String)  # コード番号
    is_deleted = Column(Boolean, nullable=False, default=False)  # 削除フラグ
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
    # 関係
    media = relationship("Media", back_populates="goods")
    artist = relationship("Artist", back_populates="goods")
    images = relationship("GoodsImage", back_populates="goods", cascade="all, delete-orphan")

class GoodsImage(Base):
    __tablename__ = 'goods_images'
    id = Column(Integer, primary_key=True, index=True)
    goods_id = Column(Integer, ForeignKey('goods.id'), nullable=False)  # GOODS ID
    image_data = Column(LargeBinary, nullable=False)  # 画像データ
    image_type = Column(String, nullable=False)  # 画像タイプ（MIME type）
    display_order = Column(Integer, nullable=False, default=0)  # 表示順序
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    # 関係
    goods = relationship("Goods", back_populates="images")

# スケジュール管理用のテーブル
class ActivityCategory(Base):
    __tablename__ = 'activity_categories'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # 活動区分名称
    is_deleted = Column(Boolean, nullable=False, default=False)  # 削除フラグ
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
    # スケジュールとの関係
    schedules = relationship("Schedule", back_populates="activity_category")

class Schedule(Base):
    __tablename__ = 'schedules'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)  # タイトル
    start_datetime = Column(DateTime, nullable=False)  # 開始日（時）
    duration = Column(Integer, nullable=False)  # 所要時間（分または日）
    is_all_day = Column(Boolean, nullable=False, default=False)  # 終日フラグ
    activity_category_id = Column(Integer, ForeignKey('activity_categories.id'), nullable=False)  # 活動区分ID
    schedule_type = Column(String, nullable=False)  # スケジュールタイプ（予定/TODO）
    location = Column(String)  # 場所
    details = Column(Text)  # 詳細
    is_todo_completed = Column(Boolean, nullable=False, default=False)  # TODO実施済み
    is_deleted = Column(Boolean, nullable=False, default=False)  # 削除フラグ
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時
    # 活動区分との関係
    activity_category = relationship("ActivityCategory", back_populates="schedules")

class Holiday(Base):
    __tablename__ = "holidays"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)