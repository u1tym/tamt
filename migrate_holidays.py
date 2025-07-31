from sqlalchemy import create_engine, text
from database import DATABASE_URL

def migrate_holidays():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 休日テーブルを作成
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS holidays (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL UNIQUE,
                name VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # インデックスを作成
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_holidays_date ON holidays(date)"))
        
        conn.commit()
        print("休日テーブルの作成が完了しました")

if __name__ == "__main__":
    migrate_holidays() 