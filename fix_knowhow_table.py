import psycopg2
from database import DATABASE_URL

def fix_knowhow_table():
    """KNOWHOWテーブルを新しい構造に完全に更新"""

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    try:
        print("KNOWHOWテーブルを新しい構造に更新中...")

        # 古いカラムを削除
        print("古いカラムを削除中...")
        cursor.execute("ALTER TABLE knowhows DROP COLUMN IF EXISTS major_category")
        cursor.execute("ALTER TABLE knowhows DROP COLUMN IF EXISTS middle_category")

        # 新しいカラムが存在することを確認
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'knowhows'
            AND column_name = 'middle_category_id'
        """)

        if not cursor.fetchone():
            print("middle_category_idカラムを追加中...")
            cursor.execute("""
                ALTER TABLE knowhows
                ADD COLUMN middle_category_id INTEGER REFERENCES middle_categories(id)
            """)

        # テーブル構造を確認
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'knowhows'
            ORDER BY ordinal_position
        """)

        columns = cursor.fetchall()
        print("\n更新後のKNOWHOWテーブル構造:")
        for column in columns:
            print(f"  - {column[0]}: {column[1]} ({'NULL' if column[2] == 'YES' else 'NOT NULL'})")

        # データを確認
        cursor.execute("SELECT COUNT(*) FROM knowhows WHERE is_deleted = FALSE")
        knowhow_count = cursor.fetchone()[0]
        print(f"\n既存のKNOWHOW数: {knowhow_count}")

        cursor.execute("SELECT COUNT(*) FROM knowhows WHERE middle_category_id IS NOT NULL")
        updated_count = cursor.fetchone()[0]
        print(f"middle_category_idが設定されているKNOWHOW数: {updated_count}")

        # コミット
        conn.commit()
        print("\nKNOWHOWテーブルの更新が完了しました！")

    except Exception as e:
        conn.rollback()
        print(f"エラーが発生しました: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_knowhow_table()