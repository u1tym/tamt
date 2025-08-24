from .models_base import Base, Integer, String, Text, Boolean, DateTime, Date, ForeignKey, func, Mapped, mapped_column, List, datetime, datetime_date, timezone, relationship

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
