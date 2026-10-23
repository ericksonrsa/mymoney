# Sprint 02 — Financial Management

## Objective

Deliver the first complete functional layer of MyMoney for personal financial management, connecting authenticated users to their accounts, categories, transactions and financial summary.

## Scope

### Backend — Django + Django REST Framework

- `Account` model for checking accounts, savings, credit cards, cash and investments.
- `Category` model for income and expense categories.
- `Transaction` model supporting income, expenses and transfers.
- UUID identifiers for financial entities.
- User ownership and complete tenant isolation.
- Balance calculation per account.
- Validation preventing cross-user references.
- Validation of category type against transaction type.
- Transfer validation requiring a different destination account.
- Database indexes for user/date and user/transaction type queries.
- Unique constraints preventing duplicate account/category names within the same user scope.

### API

| Method | Endpoint | Purpose |
|---|---|---|
| GET/POST | `/api/finance/accounts/` | List/create accounts |
| GET/PUT/PATCH/DELETE | `/api/finance/accounts/<uuid>/` | Manage an account |
| GET/POST | `/api/finance/categories/` | List/create categories |
| GET/PUT/PATCH/DELETE | `/api/finance/categories/<uuid>/` | Manage a category |
| GET/POST | `/api/finance/transactions/` | List/create transactions |
| GET/PUT/PATCH/DELETE | `/api/finance/transactions/<uuid>/` | Manage a transaction |
| GET | `/api/finance/dashboard/` | Return the authenticated user's financial summary |

### Frontend — React + Vite + TypeScript

- Protected financial dashboard.
- Balance, income, expense and transaction metrics.
- Account listing.
- Recent transaction listing.
- Forms for account, category and transaction creation.
- Period filtering for dashboard and transactions.
- Automatic JWT access-token renewal retained in the authenticated API flow.

## Business Rules

1. Financial resources are always scoped to the authenticated user.
2. A transaction cannot reference another user's account or category.
3. Income transactions require an income category.
4. Expense transactions require an expense category.
5. Transfers require a destination account owned by the same user.
6. Transfer source and destination accounts must be different.
7. Transfers do not use categories.
8. Non-transfer transactions cannot specify a destination account.
9. Transaction amounts must be positive.

## Acceptance Criteria

- [x] Authenticated users can create and manage accounts.
- [x] Authenticated users can create and manage income/expense categories.
- [x] Authenticated users can create and manage financial transactions.
- [x] Account balances reflect opening balance plus financial movements.
- [x] Transfer movements affect source and destination accounts correctly.
- [x] Cross-user access is rejected.
- [x] Invalid category/transaction combinations are rejected.
- [x] Financial API endpoints require authentication.
- [x] Dashboard aggregates only the authenticated user's data.
- [x] Automated API tests cover ownership isolation and core transaction rules.

## Technical Notes

The implementation uses Django ORM constraints and DRF serializer validation rather than relying only on frontend validation. This keeps financial integrity enforced at the API boundary and protects the data model from clients other than the web frontend.

## Result

Sprint 02 establishes the financial domain on top of the authentication foundation delivered previously. Sprint 03 builds on this foundation with analytics and dashboard visualization.
