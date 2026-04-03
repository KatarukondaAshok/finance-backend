from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import SessionLocal, engine, Base
from models import TransactionDB
from schemas import TransactionCreate, TransactionResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "Finance API is running with SQLite database"}

# CREATE
@app.post("/transactions", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    new_transaction = TransactionDB(
        amount=transaction.amount,
        type=transaction.type,
        category=transaction.category,
        date=transaction.date,
        notes=transaction.notes
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction

# READ ALL
@app.get("/transactions", response_model=list[TransactionResponse])
def get_transactions(db: Session = Depends(get_db)):
    return db.query(TransactionDB).all()

# READ ONE
@app.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(TransactionDB).filter(TransactionDB.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

# UPDATE
@app.put("/transactions/{transaction_id}", response_model=TransactionResponse)
def update_transaction(transaction_id: int, updated_transaction: TransactionCreate, db: Session = Depends(get_db)):
    transaction = db.query(TransactionDB).filter(TransactionDB.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction.amount = updated_transaction.amount
    transaction.type = updated_transaction.type
    transaction.category = updated_transaction.category
    transaction.date = updated_transaction.date
    transaction.notes = updated_transaction.notes

    db.commit()
    db.refresh(transaction)
    return transaction

# DELETE
@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(TransactionDB).filter(TransactionDB.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(transaction)
    db.commit()
    return {"message": "Transaction deleted successfully"}

# FILTER
@app.get("/transactions/filter", response_model=list[TransactionResponse])
def filter_transactions(
    type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(TransactionDB)

    if type:
        query = query.filter(TransactionDB.type.ilike(type))
    if category:
        query = query.filter(TransactionDB.category.ilike(category))

    return query.all()

# SUMMARY
@app.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    transactions = db.query(TransactionDB).all()

    total_income = sum(t.amount for t in transactions if t.type.lower() == "income")
    total_expense = sum(t.amount for t in transactions if t.type.lower() == "expense")
    balance = total_income - total_expense

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance
    }