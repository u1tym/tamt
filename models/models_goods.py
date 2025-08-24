from .models_base import Base, Integer, String, Text, Boolean, DateTime, Date, ForeignKey, LargeBinary, func, Mapped, mapped_column, List, datetime, datetime_date

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
