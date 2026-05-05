# Ordering service

FastAPI app for `[Tanya_Ordering]` (orders, items, reservations). Port **8002**. Calls **Inventory** over HTTP for ingredient names; optionally sends `order_created` / `order_submitted` events to Azure Service Bus.

Split from the [monorepo](../Azure/README.md). Related repos: [inventory-service](https://github.com/tatsiana-halaburda/inventory-service), [feedback-service](https://github.com/tatsiana-halaburda/feedback-service).

## Business logic

Pure rules live in [`services/ordering/domain.py`](services/ordering/domain.py): order totals with `Decimal` rounding, line-item quantity checks, and an order **status state machine** (`Draft` → `Submitted` → `Confirmed` / `Cancelled`, etc.). [`services/ordering/main.py`](services/ordering/main.py) uses `domain` when creating/updating orders and when submitting.

**New endpoint:** `POST /orders/{order_id}/submit` — moves a `Draft` order to `Submitted` (validates allowed transition) and emits an `order_submitted` Service Bus message when send credentials are configured.

`PUT /orders/{id}` validates `status` changes against the same transition rules (`409` on invalid transitions).

## Environment

Copy [`.env.example`](.env.example) → `.env`. Set `INVENTORY_SERVICE_URL` to your Inventory base URL (default `http://localhost:8001`). [`docker-compose.yml`](docker-compose.yml) documents `${VAR:-…}` substitution from `.env`.

| Variable | Required |
|----------|----------|
| `DB_*` or `AZURE_SQL_CONNECTION_STRING` | Yes |
| `INVENTORY_SERVICE_URL` | No — default localhost:8001 |
| `AZURE_SERVICEBUS_SEND_CONNECTION_STRING`, `AZURE_SERVICEBUS_QUEUE_NAME` | No — enqueue after `POST /orders` and `POST /orders/{id}/submit` |

## Azure SQL

Run `sql/01_schemas.sql` through `sql/05_seed.sql` in order (shared DB with Inventory/Feedback schemas).

## Run

Start Inventory first, then:

```bash
docker compose up --build -d
```

Set `INVENTORY_SERVICE_URL` in `.env` to a reachable Inventory URL (e.g. `http://host.docker.internal:8001` from Docker Desktop on Mac/Windows when Inventory runs on the host).

Local:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn services.ordering.main:app --host 127.0.0.1 --port 8002
```

OpenAPI: `http://127.0.0.1:8002/docs`

## Tests and lint (local)

```bash
pip install -r requirements.txt -r requirements-dev.txt
ruff check .
pytest tests/ -v --tb=short
```

- `tests/test_smoke.py` — OpenAPI smoke (no DB).
- `tests/test_domain.py` — unit tests for `services.ordering.domain`.

## CI (Azure Pipelines)

Pipeline definition: [`azure-pipelines.yml`](azure-pipelines.yml). On push or PR to `main` it runs **Ruff** then **Pytest**. In Azure DevOps, create a pipeline from this file at the repo root. Optional variables match `.env.example` for future integration tests.
