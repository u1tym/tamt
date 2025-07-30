import psycopg2
from database import DATABASE_URL

def check_python_category():
    """「プログラミング言語」と「Python」のカテゴリデータを確認"""

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    try:
        print("=== 大項目一覧 ===")
        cursor.execute("""
            SELECT id, name, display_order, is_deleted
            FROM major_categories
            WHERE is_deleted = FALSE
            ORDER BY display_order
        """)
        major_categories = cursor.fetchall()
        for cat in major_categories:
            print(f"  ID: {cat[0]}, 名前: {cat[1]}, 表示順: {cat[2]}")

        print("\n=== 中項目一覧 ===")
        cursor.execute("""
            SELECT mc.id, mc.name, mc.major_category_id, mc.display_order, mc.is_deleted,
                   maj.name as major_name
            FROM middle_categories mc
            JOIN major_categories maj ON mc.major_category_id = maj.id
            WHERE mc.is_deleted = FALSE
            ORDER BY maj.display_order, mc.display_order
        """)
        middle_categories = cursor.fetchall()
        for cat in middle_categories:
            print(f"  ID: {cat[0]}, 名前: {cat[1]}, 大項目: {cat[5]}, 表示順: {cat[3]}")

        print("\n=== KNOWHOW一覧 ===")
        cursor.execute("""
            SELECT k.id, k.title, k.middle_category_id, k.display_order, k.is_deleted,
                   mc.name as middle_name, maj.name as major_name
            FROM knowhows k
            JOIN middle_categories mc ON k.middle_category_id = mc.id
            JOIN major_categories maj ON mc.major_category_id = maj.id
            WHERE k.is_deleted = FALSE
            ORDER BY maj.display_order, mc.display_order, k.display_order
        """)
        knowhows = cursor.fetchall()
        for knowhow in knowhows:
            print(f"  ID: {knowhow[0]}, タイトル: {knowhow[1]}, カテゴリ: {knowhow[6]} > {knowhow[5]}, 表示順: {knowhow[3]}")

        # プログラミング言語 > PythonのKNOWHOWを確認
        print("\n=== プログラミング言語 > PythonのKNOWHOW ===")
        cursor.execute("""
            SELECT k.id, k.title, k.display_order
            FROM knowhows k
            JOIN middle_categories mc ON k.middle_category_id = mc.id
            JOIN major_categories maj ON mc.major_category_id = maj.id
            WHERE k.is_deleted = FALSE
            AND maj.name = 'プログラミング言語'
            AND mc.name = 'Python'
            ORDER BY k.display_order
        """)
        python_knowhows = cursor.fetchall()
        if python_knowhows:
            for knowhow in python_knowhows:
                print(f"  ID: {knowhow[0]}, タイトル: {knowhow[1]}, 表示順: {knowhow[2]}")
        else:
            print("  プログラミング言語 > PythonのKNOWHOWが見つかりません")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_python_category()