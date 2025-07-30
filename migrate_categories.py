import psycopg2
from database import DATABASE_URL
import re

def migrate_categories():
    """カテゴリテーブルを作成し、既存のKNOWHOWデータを移行"""

    # データベース接続
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    try:
                # 既存のデータをクリア
        print("既存のカテゴリデータをクリア中...")
        cursor.execute("DELETE FROM middle_categories")
        cursor.execute("DELETE FROM major_categories")
        cursor.execute("ALTER TABLE knowhows DROP COLUMN IF EXISTS middle_category_id")
        cursor.execute("ALTER TABLE knowhows ADD COLUMN IF NOT EXISTS middle_category_id INTEGER REFERENCES middle_categories(id)")

                # ユニーク制約を追加（存在しない場合のみ）
        cursor.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'middle_categories'
            AND constraint_name = 'middle_categories_major_category_id_name_key'
        """)
        constraint_exists = cursor.fetchone()

        if not constraint_exists:
            cursor.execute("""
                ALTER TABLE middle_categories
                ADD CONSTRAINT middle_categories_major_category_id_name_key
                UNIQUE (major_category_id, name)
            """)
            print("ユニーク制約を追加しました")
        else:
            print("ユニーク制約は既に存在します")

        print("既存のデータを移行中...")

        # 既存のKNOWHOWから大項目と中項目を抽出
        cursor.execute("""
            SELECT DISTINCT major_category, middle_category
            FROM knowhows
            WHERE is_deleted = FALSE
            AND major_category IS NOT NULL
            AND middle_category IS NOT NULL
            AND major_category != ''
            AND middle_category != ''
        """)

        existing_categories = cursor.fetchall()
        print(f"移行対象のカテゴリ数: {len(existing_categories)}")

        # 大項目を追加
        major_category_map = {}  # 名前 -> ID
        for major_name, _ in existing_categories:
            if major_name not in major_category_map:
                cursor.execute("""
                    INSERT INTO major_categories (name, display_order, is_deleted)
                    VALUES (%s, %s, FALSE)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING id
                """, (major_name, len(major_category_map)))

                result = cursor.fetchone()
                if result:
                    major_category_map[major_name] = result[0]
                    print(f"大項目を追加: {major_name} (ID: {result[0]})")
                else:
                    # 既に存在する場合、IDを取得
                    cursor.execute("SELECT id FROM major_categories WHERE name = %s", (major_name,))
                    major_category_map[major_name] = cursor.fetchone()[0]
                    print(f"大項目が既に存在: {major_name} (ID: {major_category_map[major_name]})")

        # 中項目を追加
        middle_category_map = {}  # (大項目名, 中項目名) -> ID
        for major_name, middle_name in existing_categories:
            key = (major_name, middle_name)
            if key not in middle_category_map:
                major_id = major_category_map[major_name]
                cursor.execute("""
                    INSERT INTO middle_categories (major_category_id, name, display_order, is_deleted)
                    VALUES (%s, %s, %s, FALSE)
                    ON CONFLICT (major_category_id, name) DO NOTHING
                    RETURNING id
                """, (major_id, middle_name, len([k for k in middle_category_map.keys() if k[0] == major_name])))

                result = cursor.fetchone()
                if result:
                    middle_category_map[key] = result[0]
                    print(f"中項目を追加: {major_name} > {middle_name} (ID: {result[0]})")
                else:
                    # 既に存在する場合、IDを取得
                    cursor.execute("""
                        SELECT id FROM middle_categories
                        WHERE major_category_id = %s AND name = %s
                    """, (major_id, middle_name))
                    middle_category_map[key] = cursor.fetchone()[0]
                    print(f"中項目が既に存在: {major_name} > {middle_name} (ID: {middle_category_map[key]})")

        # KNOWHOWテーブルにmiddle_category_idカラムを追加（存在しない場合）
        cursor.execute("""
            ALTER TABLE knowhows ADD COLUMN IF NOT EXISTS middle_category_id INTEGER REFERENCES middle_categories(id);
        """)

        # KNOWHOWのmiddle_category_idを更新
        print("KNOWHOWのカテゴリIDを更新中...")
        cursor.execute("""
            SELECT id, major_category, middle_category
            FROM knowhows
            WHERE is_deleted = FALSE
            AND major_category IS NOT NULL
            AND middle_category IS NOT NULL
            AND major_category != ''
            AND middle_category != ''
        """)

        knowhows = cursor.fetchall()
        updated_count = 0
        for knowhow_id, major_name, middle_name in knowhows:
            key = (major_name, middle_name)
            if key in middle_category_map:
                cursor.execute("""
                    UPDATE knowhows
                    SET middle_category_id = %s
                    WHERE id = %s
                """, (middle_category_map[key], knowhow_id))
                updated_count += 1
                print(f"KNOWHOW更新: ID {knowhow_id} -> 中項目ID {middle_category_map[key]}")

        # コミット
        conn.commit()
        print("マイグレーションが完了しました！")

        # 結果を表示
        cursor.execute("SELECT COUNT(*) FROM major_categories WHERE is_deleted = FALSE")
        major_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM middle_categories WHERE is_deleted = FALSE")
        middle_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM knowhows WHERE is_deleted = FALSE AND middle_category_id IS NOT NULL")
        knowhow_count = cursor.fetchone()[0]

        print(f"\n移行結果:")
        print(f"  大項目: {major_count}件")
        print(f"  中項目: {middle_count}件")
        print(f"  KNOWHOW (更新済み): {knowhow_count}件")
        print(f"  更新されたKNOWHOW: {updated_count}件")

    except Exception as e:
        conn.rollback()
        print(f"エラーが発生しました: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate_categories()