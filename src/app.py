from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Meowth Money Expense Tracker", version="0.1.0")


class TransactionType(str, Enum):
    expense = "expense"
    income = "income"


class Mode(str, Enum):
    upi = "UPI"
    credit_card = "CREDIT_CARD"
    bank_transfer = "BANK_TRANSFER"


class AccountType(str, Enum):
    bank = "BANK"
    upi = "UPI"
    credit_card = "CREDIT_CARD"


class Category(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    kind: str = "both"


class Account(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    account_type: AccountType
    bank_name: Optional[str] = None
    mode: Mode
    provider: Optional[str] = None
    last4: Optional[str] = None
    upi_id: Optional[str] = None


class TransactionCreate(BaseModel):
    type: TransactionType
    amount: Decimal = Field(gt=0)
    mode: Mode
    transaction_at: datetime
    category_id: Optional[UUID] = None
    account_id: Optional[UUID] = None
    merchant: Optional[str] = None
    notes: Optional[str] = None


class Transaction(TransactionCreate):
    id: UUID = Field(default_factory=uuid4)
    currency: str = "INR"
    source: str = "manual"
    source_ref: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


categories: dict[UUID, Category] = {}
accounts: dict[UUID, Account] = {}
transactions: dict[UUID, Transaction] = {}


def seed_defaults() -> None:
    if categories:
        return
    for name in [
        "Food",
        "Transport",
        "Utilities",
        "Shopping",
        "Salary",
        "Interest",
    ]:
        kind = "income" if name in {"Salary", "Interest"} else "expense"
        category = Category(name=name, kind=kind)
        categories[category.id] = category


@app.on_event("startup")
def on_startup() -> None:
    seed_defaults()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/categories", response_model=list[Category])
def list_categories() -> list[Category]:
    return list(categories.values())


@app.post("/accounts", response_model=Account)
def create_account(account: Account) -> Account:
    accounts[account.id] = account
    return account


@app.get("/accounts", response_model=list[Account])
def list_accounts() -> list[Account]:
    return list(accounts.values())


@app.post("/transactions", response_model=Transaction)
def create_transaction(payload: TransactionCreate) -> Transaction:
    if payload.category_id and payload.category_id not in categories:
        raise HTTPException(status_code=400, detail="Unknown category_id")
    if payload.account_id and payload.account_id not in accounts:
        raise HTTPException(status_code=400, detail="Unknown account_id")

    tx = Transaction(**payload.dict())
    transactions[tx.id] = tx
    return tx


@app.get("/transactions", response_model=list[Transaction])
def list_transactions(
    from_date: Optional[datetime] = Query(default=None),
    to_date: Optional[datetime] = Query(default=None),
    mode: Optional[Mode] = Query(default=None),
    category_id: Optional[UUID] = Query(default=None),
) -> list[Transaction]:
    result = list(transactions.values())

    if from_date:
        result = [tx for tx in result if tx.transaction_at >= from_date]
    if to_date:
        result = [tx for tx in result if tx.transaction_at <= to_date]
    if mode:
        result = [tx for tx in result if tx.mode == mode]
    if category_id:
        result = [tx for tx in result if tx.category_id == category_id]

    return sorted(result, key=lambda x: x.transaction_at, reverse=True)


@app.get("/summary/monthly")
def monthly_summary() -> dict[str, str]:
    inflow = sum(tx.amount for tx in transactions.values() if tx.type == TransactionType.income)
    outflow = sum(tx.amount for tx in transactions.values() if tx.type == TransactionType.expense)
    return {
        "currency": "INR",
        "inflow": str(inflow),
        "outflow": str(outflow),
        "net_flow": str(inflow - outflow),
    }
