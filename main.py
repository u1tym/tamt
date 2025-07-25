from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
import crud
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # localhost
        "http://127.0.0.1:5173",  # 127.0.0.1
        "http://0.0.0.0:5173",    # 0.0.0.0
        # 開発環境ではすべてのオリジンを許可（本番環境では削除することを推奨）
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello, world!"}

@app.post("/payment_sources", response_model=schemas.PaymentSource)
def create_payment_source(source: schemas.PaymentSourceCreate, db: Session = Depends(get_db)):
    return crud.create_payment_source(db, source)

@app.get("/payment_sources", response_model=list[schemas.PaymentSource])
def read_payment_sources(db: Session = Depends(get_db)):
    return crud.get_payment_sources(db)

@app.post("/transactions", response_model=schemas.Transaction)
def create_transaction(tx: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db, tx)

@app.get("/transactions", response_model=list[schemas.Transaction])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_transactions(db, skip=skip, limit=limit)

@app.get("/transactions/{tx_id}", response_model=schemas.Transaction)
def read_transaction(tx_id: int, db: Session = Depends(get_db)):
    db_tx = crud.get_transaction(db, tx_id)
    if db_tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_tx

@app.put("/transactions/{tx_id}", response_model=schemas.Transaction)
def update_transaction(tx_id: int, tx: schemas.TransactionUpdate, db: Session = Depends(get_db)):
    db_tx = crud.update_transaction(db, tx_id, tx)
    if db_tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_tx

@app.delete("/transactions/{tx_id}")
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    success = crud.delete_transaction(db, tx_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"}

# 開発サーバー起動用の設定
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # すべてのIPアドレスでアクセス可能
        port=8000,
        reload=True,     # 開発時の自動リロード
        log_level="info"
    )