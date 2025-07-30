from sqlalchemy import create_engine, text
from database import DATABASE_URL

def migrate_knowhows():
    """KNOWHOWテーブルを作成するマイグレーション"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as connection:
                # KNOWHOWテーブルが存在するかチェック
        result = connection.execute(text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'knowhows'
        """))

        if result.fetchone() is None:
            print("KNOWHOWテーブルを作成しています...")

            # KNOWHOWテーブルを作成
            connection.execute(text("""
                CREATE TABLE knowhows (
                    id SERIAL PRIMARY KEY,
                    major_category VARCHAR NOT NULL,
                    middle_category VARCHAR NOT NULL,
                    title VARCHAR NOT NULL,
                    keywords VARCHAR,
                    content TEXT NOT NULL,
                    display_order INTEGER NOT NULL DEFAULT 0,
                    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # インデックスを作成
            connection.execute(text("""
                CREATE INDEX idx_knowhows_major_category ON knowhows(major_category)
            """))

            connection.execute(text("""
                CREATE INDEX idx_knowhows_middle_category ON knowhows(middle_category)
            """))

            connection.execute(text("""
                CREATE INDEX idx_knowhows_display_order ON knowhows(display_order)
            """))

            connection.execute(text("""
                CREATE INDEX idx_knowhows_is_deleted ON knowhows(is_deleted)
            """))

            # サンプルデータを挿入
            sample_data = [
                {
                    'major_category': '技術',
                    'middle_category': 'プログラミング',
                    'title': 'Pythonでのファイル操作',
                    'keywords': 'Python, ファイル, 操作',
                    'content': 'Pythonでファイルを操作する基本的な方法：\n\n1. ファイルを開く\nwith open(\'filename.txt\', \'r\') as f:\n    content = f.read()\n\n2. ファイルに書き込む\nwith open(\'filename.txt\', \'w\') as f:\n    f.write(\'Hello, World!\')\n\n3. ファイルを追記する\nwith open(\'filename.txt\', \'a\') as f:\n    f.write(\'\\nNew line\')\n\n4. ファイルの存在確認\nimport os\nif os.path.exists(\'filename.txt\'):\n    print(\'ファイルが存在します\')',
                    'display_order': 0
                },
                {
                    'major_category': '技術',
                    'middle_category': 'データベース',
                    'title': 'SQLiteの基本操作',
                    'keywords': 'SQLite, データベース, SQL',
                    'content': 'SQLiteデータベースの基本的な操作方法：\n\n1. データベースに接続\nimport sqlite3\nconn = sqlite3.connect(\'database.db\')\ncursor = conn.cursor()\n\n2. テーブルを作成\ncursor.execute(\'\'\'\n    CREATE TABLE users (\n        id INTEGER PRIMARY KEY,\n        name TEXT NOT NULL,\n        email TEXT UNIQUE\n    )\n\'\'\')\n\n3. データを挿入\ncursor.execute(\'INSERT INTO users (name, email) VALUES (?, ?)\', (\'John\', \'john@example.com\'))\n\n4. データを取得\ncursor.execute(\'SELECT * FROM users\')\nusers = cursor.fetchall()\n\n5. 変更を保存して接続を閉じる\nconn.commit()\nconn.close()',
                    'display_order': 1
                },
                {
                    'major_category': '業務',
                    'middle_category': 'Excel',
                    'title': 'VLOOKUP関数の使い方',
                    'keywords': 'Excel, VLOOKUP, 関数',
                    'content': 'ExcelのVLOOKUP関数の基本的な使い方：\n\n1. 基本的な構文\n=VLOOKUP(検索値, 検索範囲, 列番号, [検索の型])\n\n2. 使用例\n=VLOOKUP(A2, B2:D10, 2, FALSE)\n\n3. パラメータの説明\n- 検索値: 検索したい値\n- 検索範囲: 検索対象の表\n- 列番号: 返したい値の列番号（左から数えて）\n- 検索の型: TRUE（近似値）またはFALSE（完全一致）\n\n4. 注意点\n- 検索範囲の左端の列で検索が行われる\n- 検索範囲は昇順にソートされている必要がある\n- 見つからない場合は#N/Aエラーが返される',
                    'display_order': 2
                },
                {
                    'major_category': '業務',
                    'middle_category': '会計',
                    'title': '仕訳の基本',
                    'keywords': '会計, 仕訳, 簿記',
                    'content': '仕訳の基本的なルール：\n\n1. 複式簿記の原則\n- 借方（左）と貸方（右）の金額は必ず一致する\n- 資産の増加は借方、減少は貸方\n- 負債・資本の増加は貸方、減少は借方\n\n2. 基本的な仕訳例\n現金で商品を購入した場合：\n借方：商品 100,000円\n貸方：現金 100,000円\n\n3. 勘定科目の分類\n- 資産：現金、預金、売掛金、商品など\n- 負債：買掛金、借入金、未払金など\n- 資本：資本金、利益剰余金など\n- 収益：売上、受取利息など\n- 費用：仕入、給料、水道光熱費など\n\n4. 仕訳の手順\n1) 取引の内容を理解する\n2) 影響を受ける勘定科目を特定する\n3) 各勘定科目の増減を判断する\n4) 借方・貸方に振り分ける\n5) 金額を記入する',
                    'display_order': 3
                }
            ]

            for data in sample_data:
                connection.execute(text("""
                    INSERT INTO knowhows (major_category, middle_category, title, keywords, content, display_order)
                    VALUES (:major_category, :middle_category, :title, :keywords, :content, :display_order)
                """), data)

            connection.commit()
            print("KNOWHOWテーブルの作成が完了しました")
            print(f"サンプルデータ {len(sample_data)} 件を挿入しました")
        else:
            print("KNOWHOWテーブルは既に存在します")

if __name__ == "__main__":
    migrate_knowhows()