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


class TransactionUpdate(BaseModel):
    type: Optional[TransactionType] = None
    amount: Optional[Decimal] = Field(default=None, gt=0)
    mode: Optional[Mode] = None
    transaction_at: Optional[datetime] = None
    category_id: Optional[UUID] = None
    account_id: Optional[UUID] = None
    merchant: Optional[str] = None
    notes: Optional[str] = None


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


@app.put("/transactions/{transaction_id}", response_model=Transaction)
def update_transaction(transaction_id: UUID, payload: TransactionUpdate) -> Transaction:
    existing = transactions.get(transaction_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Transaction not found")

    update_data = payload.dict(exclude_unset=True)

    if "category_id" in update_data and update_data["category_id"] and update_data["category_id"] not in categories:
        raise HTTPException(status_code=400, detail="Unknown category_id")

    if "account_id" in update_data and update_data["account_id"] and update_data["account_id"] not in accounts:
        raise HTTPException(status_code=400, detail="Unknown account_id")

    updated = existing.copy(update=update_data)
    updated.updated_at = datetime.utcnow()
    transactions[transaction_id] = updated
    return updated


@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: UUID) -> dict[str, str]:
    if transaction_id not in transactions:
        raise HTTPException(status_code=404, detail="Transaction not found")

    del transactions[transaction_id]
    return {"status": "deleted"}


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


@app.get("/summary/mode-breakdown")
def mode_breakdown() -> dict[str, str]:
    totals: dict[str, Decimal] = {}
    for tx in transactions.values():
        if tx.type != TransactionType.expense:
            continue
        key = tx.mode.value
        totals[key] = totals.get(key, Decimal("0")) + tx.amount
    return {mode: str(amount) for mode, amount in totals.items()}


@app.get("/summary/account-breakdown")
def account_breakdown() -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, Decimal]] = {}
    for tx in transactions.values():
        if not tx.account_id or tx.account_id not in accounts:
            continue
        account_name = accounts[tx.account_id].name
        if account_name not in result:
            result[account_name] = {"inflow": Decimal("0"), "outflow": Decimal("0")}
        if tx.type == TransactionType.income:
            result[account_name]["inflow"] += tx.amount
        else:
            result[account_name]["outflow"] += tx.amount

    return {
        account: {
            "inflow": str(totals["inflow"]),
            "outflow": str(totals["outflow"]),
            "net_flow": str(totals["inflow"] - totals["outflow"]),
        }
        for account, totals in result.items()
    }
