import os
from sqlalchemy import create_engine, text
from database import DATABASE_URL

def migrate_goods_add_fields():
    """GOODSテーブルに所持フラグとコード番号のカラムを追加"""
    print("GOODSテーブルに所持フラグとコード番号のカラムを追加中...")
    
    # データベース接続
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # 所持フラグカラムを追加
            conn.execute(text("""
                ALTER TABLE goods 
                ADD COLUMN is_owned BOOLEAN NOT NULL DEFAULT FALSE
            """))
            print("✓ is_ownedカラムを追加しました")
            
            # コード番号カラムを追加
            conn.execute(text("""
                ALTER TABLE goods 
                ADD COLUMN code_number VARCHAR
            """))
            print("✓ code_numberカラムを追加しました")
            
            conn.commit()
            print("\n✅ GOODSテーブルのカラム追加が完了しました！")
            
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate_goods_add_fields() 