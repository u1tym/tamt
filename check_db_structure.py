import psycopg2
from database import DATABASE_URL

def check_db_structure():
    """現在のデータベース構造を確認"""

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    try:
        # テーブル一覧を取得
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print("存在するテーブル:")
        for table in tables:
            print(f"  - {table[0]}")

        # KNOWHOWテーブルの構造を確認
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'knowhows'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print("\nKNOWHOWテーブルの構造:")
        for column in columns:
            print(f"  - {column[0]}: {column[1]} ({'NULL' if column[2] == 'YES' else 'NOT NULL'})")

        # 既存のデータを確認
        cursor.execute("SELECT COUNT(*) FROM knowhows WHERE is_deleted = FALSE")
        knowhow_count = cursor.fetchone()[0]
        print(f"\n既存のKNOWHOW数: {knowhow_count}")

        if knowhow_count > 0:
            cursor.execute("SELECT * FROM knowhows WHERE is_deleted = FALSE LIMIT 3")
            sample_data = cursor.fetchall()
            print("\nサンプルデータ:")
            for row in sample_data:
                print(f"  {row}")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_db_structure()