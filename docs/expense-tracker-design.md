# Expense Tracker v1 Design

## Objective
Build the first production-ready module of the personal finance app: an expense tracker focused on UPI and credit-card transactions, with support for income entries and multiple linked bank accounts to calculate inflow/outflow.

## Product Scope (v1)
- Add and manage expenses.
- Track payment mode: UPI or credit card.
- Track income entries.
- Support multiple bank accounts for account-level transaction attribution and reporting.
- Category-based reporting.
- Monthly inflow/outflow dashboard.
- Import transactions via CSV.

## Non-Goals (v1)
- Direct bank/API sync.
- SMS/email ingestion.
- Budget alerts.
- Portfolio tracking (deferred to next module).

## Core User Stories
1. As a user, I can quickly add an expense with amount, mode, category, and date.
2. As a user, I can add income so net cashflow is accurate.
3. As a user, I can browse and filter transactions by date, mode, and category.
4. As a user, I can upload CSV files to backfill transaction history.
5. As a user, I can view inflow/outflow and category spending trends.

## Domain Model
### Transaction
- id (UUID)
- type: `expense | income`
- amount (decimal)
- currency (`INR` default)
- mode: `UPI | CREDIT_CARD`
- account_id (nullable)
- category_id (nullable)
- merchant (nullable)
- notes (nullable)
- transaction_at (timestamp)
- source: `manual | csv_import`
- source_ref (nullable, raw external id/row hash)
- created_at / updated_at

### Category
- id (UUID)
- name
- parent_id (nullable)
- kind: `expense | income | both`
- is_default (bool)
- created_at / updated_at

### Account
- id (UUID)
- name (e.g., GPay, HDFC Millennia, HDFC Salary A/C)
- account_type: `BANK | UPI | CREDIT_CARD`
- bank_name (nullable, required when account_type is `BANK`)
- mode: `UPI | CREDIT_CARD | BANK_TRANSFER`
- provider (nullable)
- last4 (nullable, card only)
- upi_id (nullable, UPI accounts only)
- created_at / updated_at

### BankAccount
- id (UUID)
- account_id (FK -> Account.id)
- bank_name
- account_nickname
- masked_account_number
- ifsc (nullable)
- is_primary (bool)
- created_at / updated_at

### ImportJob
- id (UUID)
- status: `uploaded | parsed | validated | imported | failed`
- filename
- source_mode: `UPI | CREDIT_CARD`
- row_count
- imported_count
- skipped_count
- error_report (json, nullable)
- created_at / updated_at

## Reporting Definitions
- **Inflow**: sum of `income` transactions for a period.
- **Outflow**: sum of `expense` transactions for a period.
- **Net Flow**: inflow - outflow.
- **Category Spend**: grouped outflow by category.
- **Mode Split**: grouped outflow by mode.
- **Account Split**: grouped inflow/outflow by bank/account.

## Import Pipeline (CSV)
1. Upload CSV and choose source mode.
2. Map CSV columns to canonical fields.
3. Parse and normalize records.
4. Validate mandatory fields (amount, type inference, date).
5. Deduplicate via `source_ref` hash (date+amount+merchant+mode).
6. Preview results before commit.
7. Persist transactions and import audit metadata.

## Initial Default Categories
- Expense: Food, Transport, Utilities, Shopping, Entertainment, Health, Education, Rent, Subscriptions, Travel, Misc.
- Income: Salary, Interest, Refund, Gift, Misc Income.

## Open Decisions
- Whether to support transfer-type entries in v1.1.
- Whether to expose subcategory depth >1.
- Whether to allow negative amounts for corrections vs explicit reversal entries.
