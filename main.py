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
    allow_origins=["http://localhost:5173"],  # フロントのURL
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