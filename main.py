from fastapi import FastAPI, Request, Depends
from routers import router as api_router
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

# import crud

import logging
import argparse

from log import Log

from typing import Any
from typing import Callable

from common import get_db
from models import Base
from database import engine

# コマンドライン引数の解析
parser = argparse.ArgumentParser()
parser.add_argument('--migration', action='store_true', help='データベーステーブルを作成する')
args, unknown = parser.parse_known_args()

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ulog = Log(0, "ulog")
ulog.debug_on()

# データベーステーブルを作成（--migrationオプションが指定された場合のみ）
if args.migration:
    logger.info("データベーステーブルを作成します...")
    Base.metadata.create_all(bind=engine)
    logger.info("データベーステーブルの作成が完了しました")
else:
    logger.info("--migrationオプションが指定されていないため、テーブル作成をスキップします")

app = FastAPI()
app.include_router(api_router)

app.state.ulog = ulog

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# セッション情報をログ出力するミドルウェア
@app.middleware("http")
async def log_session_info(request: Request, call_next: Callable[[Any], Any], db: Session = Depends(get_db)) -> Any:
    # cash、goods、holiday、knowhow、scheduleのAPIエンドポイントかチェック
    path = request.url.path
    ulog.output("INF", "path=[" + path + "]")

    if any(keyword in path for keyword in [
        '/cash', '/goods', '/holiday', '/knowhow', '/schedule',
        ]):
        username = request.headers.get('X-Username', 'Unknown')
        session_token = request.headers.get('X-Session-Token', 'Unknown')
        ulog.output("INF", "user=[" + username + "] session=[" + session_token + "]")

        # db_acc = crud.get_account_by_username()
        logger.info(f"API Request - Path: {path}, Method: {request.method}, Username: {username}, Session Token: {session_token}")

    response = await call_next(request)
    return response

if __name__ == "__main__":
    import uvicorn

    print("HTTPで起動します")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5902,
        reload=True
    )