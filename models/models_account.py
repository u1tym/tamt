from .models_base import Base, Integer, String, Text, Boolean, DateTime, func, Mapped, mapped_column, Optional, datetime, timezone

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
