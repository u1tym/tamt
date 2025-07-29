#!/usr/bin/env python3
"""
予算テーブルのマイグレーションスクリプト
order_indexカラムを追加します
"""

import os
from sqlalchemy import create_engine, text
from database import DATABASE_URL

def migrate_budgets_table():
    """budgetsテーブルにorder_indexカラムを追加"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        try:
            # order_indexカラムが存在するかチェック
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'budgets' AND column_name = 'order_index'
            """))

            if result.fetchone():
                print("order_indexカラムは既に存在します")
                return

            # order_indexカラムを追加
            conn.execute(text("""
                ALTER TABLE budgets
                ADD COLUMN order_index INTEGER DEFAULT 0
            """))

            # 既存のデータに順序を設定
            conn.execute(text("""
                UPDATE budgets
                SET order_index = id
                WHERE order_index = 0
            """))

            conn.commit()
            print("order_indexカラムを正常に追加しました")

        except Exception as e:
            print(f"マイグレーションエラー: {e}")
            conn.rollback()
            raise

def migrate_transactions_table():
    """transactionsテーブルにbudget_nameカラムを追加"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        try:
            # budget_nameカラムが存在するかチェック
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'transactions' AND column_name = 'budget_name'
            """))

            if result.fetchone():
                print("budget_nameカラムは既に存在します")
                return

            # budget_nameカラムを追加
            conn.execute(text("""
                ALTER TABLE transactions
                ADD COLUMN budget_name VARCHAR NOT NULL DEFAULT '未分類'
            """))

            conn.commit()
            print("budget_nameカラムを正常に追加しました")

        except Exception as e:
            print(f"マイグレーションエラー: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate_budgets_table()
    migrate_transactions_table()