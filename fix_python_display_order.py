import psycopg2
from database import DATABASE_URL

def fix_python_display_order():
    """PythonのKNOWHOWの表示順を正しく設定"""

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    try:
        print("PythonのKNOWHOWの表示順を修正中...")

        # Pythonの中項目IDを取得
        cursor.execute("""
            SELECT mc.id
            FROM middle_categories mc
            JOIN major_categories maj ON mc.major_category_id = maj.id
            WHERE maj.name = 'プログラミング言語'
            AND mc.name = 'python'
        """)
        python_middle_category = cursor.fetchone()

        if not python_middle_category:
            print("Pythonの中項目が見つかりません")
            return

        python_middle_id = python_middle_category[0]
        print(f"Pythonの中項目ID: {python_middle_id}")

        # PythonのKNOWHOWを取得
        cursor.execute("""
            SELECT id, title, display_order
            FROM knowhows
            WHERE middle_category_id = %s
            AND is_deleted = FALSE
            ORDER BY id
        """, (python_middle_id,))

        python_knowhows = cursor.fetchall()
        print(f"PythonのKNOWHOW数: {len(python_knowhows)}")

        # 表示順を0から順番に設定
        for i, knowhow in enumerate(python_knowhows):
            cursor.execute("""
                UPDATE knowhows
                SET display_order = %s
                WHERE id = %s
            """, (i, knowhow[0]))
            print(f"  ID {knowhow[0]} ({knowhow[1]}): 表示順 {knowhow[2]} → {i}")

        # コミット
        conn.commit()
        print("表示順の修正が完了しました！")

        # 修正後の確認
        print("\n=== 修正後のPythonのKNOWHOW ===")
        cursor.execute("""
            SELECT k.id, k.title, k.display_order
            FROM knowhows k
            JOIN middle_categories mc ON k.middle_category_id = mc.id
            JOIN major_categories maj ON mc.major_category_id = maj.id
            WHERE k.is_deleted = FALSE
            AND maj.name = 'プログラミング言語'
            AND mc.name = 'python'
            ORDER BY k.display_order
        """)
        updated_knowhows = cursor.fetchall()
        for knowhow in updated_knowhows:
            print(f"  ID: {knowhow[0]}, タイトル: {knowhow[1]}, 表示順: {knowhow[2]}")

    except Exception as e:
        conn.rollback()
        print(f"エラーが発生しました: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_python_display_order()