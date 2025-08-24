from .models_base import Base, Integer, String, Text, Boolean, DateTime, ForeignKey, func, Mapped, mapped_column, List, datetime

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
