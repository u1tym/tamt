from fastapi import Request
import schemas

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import SessionLocal

# セッション情報を取得するヘルパー関数
def get_session_info(request: Request) -> schemas.SessionInfo:
    username = request.headers.get('X-Username', 'Unknown')
    session_token = request.headers.get('X-Session-Token', 'Unknown')
    return schemas.SessionInfo(username=username, session_token=session_token)

# データベースセッションの依存関係
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
