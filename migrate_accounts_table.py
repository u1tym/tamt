import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# PostgreSQLデータベース接続設定
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "tamt")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)  # ユーザー名
    password = Column(String, nullable=False)  # パスワード（ハッシュ化されたもの）
    session_info = Column(Text)  # セッション情報（JSON形式で保存）
    last_access = Column(DateTime, nullable=False, default=datetime.utcnow)  # 最終アクセス日時
    is_deleted = Column(Boolean, nullable=False, default=False)  # 削除フラグ
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # 登録日時
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 更新日時

def create_accounts_table():
    """アカウントテーブルを作成する"""
    try:
        # テーブルが存在するかチェック
        inspector = engine.dialect.inspector(engine)
        existing_tables = inspector.get_table_names()
        
        if 'accounts' in existing_tables:
            print("accountsテーブルは既に存在します。")
            return
        
        # テーブルを作成
        Account.__table__.create(engine)
        print("accountsテーブルを作成しました。")
        
        # サンプルデータを挿入（テスト用）
        db = SessionLocal()
        try:
            # テスト用アカウントを作成
            test_account = Account(
                username="admin",
                password="admin123",  # 実際の運用ではハッシュ化する
                session_info="{}",
                last_access=datetime.utcnow()
            )
            db.add(test_account)
            db.commit()
            print("テスト用アカウント（admin/admin123）を作成しました。")
        except Exception as e:
            print(f"サンプルデータの挿入でエラーが発生しました: {e}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        print(f"テーブル作成でエラーが発生しました: {e}")

if __name__ == "__main__":
    create_accounts_table() 