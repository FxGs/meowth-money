# Architecture Decisions Log (ADR-lite)

## AD-001: Module-first delivery
**Decision:** Build expense tracker first; portfolio tracker later.
**Rationale:** Immediate utility, faster feedback loop, and cleaner transaction foundation for later investment analytics.

## AD-002: Canonical transaction ledger
**Decision:** Store expenses and income in one `transactions` ledger table with `type` discriminator.
**Rationale:** Simplifies reporting (inflow/outflow), filtering, imports, and future extensibility.

## AD-003: Manual + CSV as v1 ingestion
**Decision:** Support manual entries and CSV imports in v1; defer live sync.
**Rationale:** Delivers value quickly with lower integration/compliance complexity.

## AD-004: Explicit source tracking
**Decision:** Every transaction stores `source` and optional `source_ref`.
**Rationale:** Enables deduplication, import audits, and traceability.

## AD-005: Category system with defaults + user-defined
**Decision:** Seed default categories but allow user-created categories.
**Rationale:** Quick onboarding while preserving personalization.

## AD-006: Reporting computed from ledger
**Decision:** Compute inflow/outflow and breakdowns from transaction ledger, not denormalized counters.
**Rationale:** Avoids drift and keeps correctness straightforward for early versions.

## AD-007: Keep currency field even if INR-only at launch
**Decision:** Store currency per transaction; default INR.
**Rationale:** Future-proofs schema for multi-currency with minimal extra cost now.

## AD-008: Multi-bank-account support in expense module
**Decision:** Support multiple bank accounts in v1 data model, linked through account-aware transactions.
**Rationale:** Users commonly operate across salary, savings, and payment-linked accounts; account-level visibility improves reconciliation and reporting.
