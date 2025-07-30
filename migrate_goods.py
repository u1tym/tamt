#!/usr/bin/env python3
"""
GOODS管理システム用のデータベースマイグレーション
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from database import DATABASE_URL

def migrate_goods():
    """GOODS管理システム用のテーブルを作成"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("GOODS管理システム用のテーブルを作成中...")
        
        # personsテーブル
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS persons (
                id SERIAL PRIMARY KEY,
                name VARCHAR NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✓ personsテーブルを作成しました")
        
        # artistsテーブル
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS artists (
                id SERIAL PRIMARY KEY,
                name VARCHAR NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✓ artistsテーブルを作成しました")
        
        # artist_personsテーブル（中間テーブル）
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS artist_persons (
                id SERIAL PRIMARY KEY,
                artist_id INTEGER NOT NULL,
                person_id INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (artist_id) REFERENCES artists (id),
                FOREIGN KEY (person_id) REFERENCES persons (id)
            )
        """))
        print("✓ artist_personsテーブルを作成しました")
        
        # mediaテーブル
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS media (
                id SERIAL PRIMARY KEY,
                name VARCHAR NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✓ mediaテーブルを作成しました")
        
        # goodsテーブル
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS goods (
                id SERIAL PRIMARY KEY,
                media_id INTEGER NOT NULL,
                artist_id INTEGER NOT NULL,
                title VARCHAR NOT NULL,
                release_date DATE NOT NULL,
                memo TEXT,
                is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (media_id) REFERENCES media (id),
                FOREIGN KEY (artist_id) REFERENCES artists (id)
            )
        """))
        print("✓ goodsテーブルを作成しました")
        
        # goods_imagesテーブル
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS goods_images (
                id SERIAL PRIMARY KEY,
                goods_id INTEGER NOT NULL,
                image_data BYTEA NOT NULL,
                image_type VARCHAR NOT NULL,
                display_order INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (goods_id) REFERENCES goods (id)
            )
        """))
        print("✓ goods_imagesテーブルを作成しました")
        
        # インデックスの作成
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_persons_name ON persons (name)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_artists_name ON artists (name)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_artist_persons_artist_id ON artist_persons (artist_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_artist_persons_person_id ON artist_persons (person_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_media_name ON media (name)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_goods_media_id ON goods (media_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_goods_artist_id ON goods (artist_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_goods_release_date ON goods (release_date)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_goods_is_deleted ON goods (is_deleted)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_goods_images_goods_id ON goods_images (goods_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_goods_images_display_order ON goods_images (display_order)"))
        print("✓ インデックスを作成しました")
        
        conn.commit()
        print("\n✅ GOODS管理システム用のテーブル作成が完了しました！")

if __name__ == "__main__":
    migrate_goods() 