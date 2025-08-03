import os
from sqlalchemy import create_engine, text
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

def add_random_number_column():
    """accountsテーブルにrandom_numberカラムを追加する"""
    try:
        with engine.connect() as connection:
            # カラムが既に存在するかチェック
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'accounts' AND column_name = 'random_number'
            """))
            
            if result.fetchone():
                print("random_numberカラムは既に存在します。")
                return
            
            # カラムを追加
            connection.execute(text("""
                ALTER TABLE accounts 
                ADD COLUMN random_number INTEGER
            """))
            
            connection.commit()
            print("random_numberカラムを追加しました。")
            
            # 既存のレコードにランダムな値を設定
            connection.execute(text("""
                UPDATE accounts 
                SET random_number = FLOOR(RANDOM() * 1000) + 1 
                WHERE random_number IS NULL
            """))
            
            connection.commit()
            print("既存のレコードにランダムな値を設定しました。")
            
    except Exception as e:
        print(f"カラム追加でエラーが発生しました: {e}")

if __name__ == "__main__":
    add_random_number_column() 