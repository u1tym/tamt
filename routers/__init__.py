from fastapi import APIRouter
from . import account, login, cash, goods, holiday, knowhow, schedule

router = APIRouter()

router.include_router(account.router, prefix="/account", tags=["account"])
router.include_router(login.router, prefix="/login", tags=["login"])

router.include_router(knowhow.router, prefix="/knowhow", tags=["knowhow"])
router.include_router(goods.router, prefix="/goods", tags=["goods"])
router.include_router(cash.router, prefix="/cash", tags=["cash"])
router.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
router.include_router(holiday.router, prefix="/holiday", tags=["holiday"])
