# Meowth Money

Expense tracker implementation scaffold (v0.1) using FastAPI.

## Run

```bash
./scripts/setup_env.sh
source .venv/bin/activate
uvicorn src.app:app --reload
```

## Network-restricted environments

If your environment blocks the default package index, set a reachable mirror before install:

```bash
export PIP_INDEX_URL="https://pypi.org/simple"
./scripts/setup_env.sh
```

You can also set `PIP_EXTRA_INDEX_URL` if your organization provides an internal mirror.

## Endpoints

- `GET /health`
- `GET /categories`
- `POST /accounts`
- `GET /accounts`
- `POST /transactions`
- `GET /transactions`
- `PUT /transactions/{transaction_id}`
- `DELETE /transactions/{transaction_id}`
- `GET /summary/monthly`
- `GET /summary/mode-breakdown`
- `GET /summary/account-breakdown`
