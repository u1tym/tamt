from fastapi import APIRouter
from fastapi import Depends, HTTPException, Request

from sqlalchemy.orm import Session

import crud
import schemas

from datetime import datetime, timezone

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common import get_db
from log import Log

router = APIRouter()


@router.post("/request-random", response_model=schemas.RandomNumberResponse)
def request_random_number(request_data: schemas.LoginRequest, request: Request, db: Session = Depends(get_db)):
    """ログイン時のランダム数要求"""

    meth = "request_random_number"

    ulog: Log = request.app.state.ulog
    ulog.output("ST ", meth + " username=[" + request_data.username + "]")

    # ユーザー名でアカウントを検索
    account = crud.get_account_by_username(db, username=request_data.username)
    if account is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

    # ランダム数を生成（1-1000の範囲）
    import random
    random_number = random.randint(1, 1000)

    ulog.output("INF", "random_number = " + str(random_number))

    # アカウント情報を更新
    crud.update_random_number(db, account.id, random_number)

    ulog.output("END", meth)
    return schemas.RandomNumberResponse(
        success=True,
        random_number=random_number,
        message="ランダム数を生成しました"
    )

@router.post("/verify", response_model=schemas.LoginResponse)
def verify_login(verify_request: schemas.LoginVerifyRequest, request: Request, db: Session = Depends(get_db)):
    """ログイン認証"""

    meth = "verify_login"

    ulog: Log = request.app.state.ulog
    ulog.output("ST ", meth)

    # ユーザー名でアカウントを検索

    account = crud.get_account_by_username(db, username=verify_request.username)
    if account is None:
        return schemas.LoginResponse(
            success=False,
            message="ユーザーが見つかりません"
        )

    # ハッシュ値を生成して比較（データベースから取得したパスワードを使用）
    import hashlib
    expected_hash = hashlib.sha256(
        (verify_request.username + account.password + str(account.random_number)).encode()
    ).hexdigest()

    if expected_hash != verify_request.hash_value:
        return schemas.LoginResponse(
            success=False,
            message="パスワードが正しくありません"
        )

    # セッショントークンを生成
    import secrets
    session_token = secrets.token_urlsafe(32)

    # セッション情報を更新
    session_info = {"token": session_token, "login_time": datetime.now(timezone.utc).isoformat()}
    crud.update_session_info(db, account.id, str(session_info))

    ulog.output("END", meth)
    return schemas.LoginResponse(
        success=True,
        message="ログインに成功しました",
        session_token=session_token
    )
