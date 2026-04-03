from pydantic import BaseModel, field_validator
from typing import Optional

class TransactionCreate(BaseModel):
    amount: float
    type: str
    category: str
    date: str
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    @field_validator("type")
    @classmethod
    def type_must_be_valid(cls, v):
        if v.lower() not in ["income", "expense"]:
            raise ValueError("Type must be either 'income' or 'expense'")
        return v

class TransactionResponse(TransactionCreate):
    id: int

    class Config:
        from_attributes = True