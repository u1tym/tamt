#!/usr/bin/env python3
"""
スケジュール管理用テーブルのマイグレーションスクリプト
"""

from sqlalchemy import create_engine, text
from database import DATABASE_URL

def create_schedule_tables():
    """スケジュール管理用のテーブルを作成"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
                # 活動区分テーブルを作成
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS activity_categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR NOT NULL UNIQUE,
                is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # スケジュールテーブルを作成
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS schedules (
                id SERIAL PRIMARY KEY,
                title VARCHAR NOT NULL,
                start_datetime TIMESTAMP NOT NULL,
                duration INTEGER NOT NULL,
                is_all_day BOOLEAN NOT NULL DEFAULT FALSE,
                activity_category_id INTEGER NOT NULL,
                schedule_type VARCHAR NOT NULL,
                location VARCHAR,
                details TEXT,
                is_todo_completed BOOLEAN NOT NULL DEFAULT FALSE,
                is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (activity_category_id) REFERENCES activity_categories (id)
            )
        """))

        # インデックスを作成
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_schedules_start_datetime
            ON schedules (start_datetime)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_schedules_activity_category_id
            ON schedules (activity_category_id)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_schedules_is_deleted
            ON schedules (is_deleted)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_activity_categories_is_deleted
            ON activity_categories (is_deleted)
        """))

        conn.commit()
        print("スケジュール管理用テーブルの作成が完了しました。")

def insert_sample_activity_categories():
    """サンプルの活動区分を挿入"""
    engine = create_engine(DATABASE_URL)

    sample_categories = [
        "仕事",
        "プライベート",
        "勉強",
        "運動",
        "買い物",
        "家事",
        "趣味",
        "健康管理"
    ]

    with engine.connect() as conn:
        for category_name in sample_categories:
            conn.execute(text("""
                INSERT INTO activity_categories (name)
                VALUES (:name)
                ON CONFLICT (name) DO NOTHING
            """), {"name": category_name})

        conn.commit()
        print(f"{len(sample_categories)}個のサンプル活動区分を挿入しました。")

if __name__ == "__main__":
    print("スケジュール管理用テーブルの作成を開始します...")
    create_schedule_tables()
    insert_sample_activity_categories()
    print("マイグレーションが完了しました。")