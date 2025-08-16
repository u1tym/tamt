from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request
from routers import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import io
from PIL import Image
import cv2
import numpy as np
import pytesseract
import re
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
import logging

from database import SessionLocal, engine
import models
import crud
import schemas

from log import Log

from type_req import rep_calculate_payment_periods_rec
from type_req import rep_calculate_payment_periods
from type_req import rep_get_payment_summary_rec
from type_req import rep_parse_recipt

from typing import cast

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ulog = Log(0, "ulog")
ulog.debug_on()

# # データベーステーブルを作成
# models.Base.metadata.create_all(bind=engine)

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
async def log_session_info(request: Request, call_next):
    # cash、goods、holiday、knowhow、scheduleのAPIエンドポイントかチェック
    path = request.url.path
    if any(keyword in path for keyword in [
            '/transactions',
            '/payment_sources',
            '/budgets',
            '/knowhows',
            '/persons',
            '/artists',
            '/media',
            '/goods',
            '/schedules',
            '/holidays',
        ]):
        username = request.headers.get('X-Username', 'Unknown')
        session_token = request.headers.get('X-Session-Token', 'Unknown')
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