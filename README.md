# Ordering service

FastAPI app for `[Tanya_Ordering]` (orders, items, reservations). Port **8002**. Calls **Inventory** over HTTP for ingredient names; optionally sends `order_created` to Azure Service Bus.

Split from the [monorepo](../Azure/README.md). Related repos: [inventory-service](https://github.com/tatsiana-halaburda/inventory-service), [feedback-service](https://github.com/tatsiana-halaburda/feedback-service).

## Environment

Copy `.env.example` → `.env`. Set `INVENTORY_SERVICE_URL` to your Inventory base URL (default `http://localhost:8001`).

| Variable | Required |
|----------|----------|
| `DB_*` or `AZURE_SQL_CONNECTION_STRING` | Yes |
| `INVENTORY_SERVICE_URL` | No — default localhost:8001 |
| `AZURE_SERVICEBUS_SEND_CONNECTION_STRING`, `AZURE_SERVICEBUS_QUEUE_NAME` | No — enqueue after `POST /orders` |

## Azure SQL

Run `sql/01_schemas.sql` through `sql/05_seed.sql` in order (shared DB with Inventory/Feedback schemas).

## Run

Start Inventory first, then:

```bash
docker compose up --build -d
```

Set `INVENTORY_SERVICE_URL` in `.env` to a reachable Inventory URL (e.g. `http://host.docker.internal:8001` from Docker Desktop on Mac/Windows when Inventory runs on the host).

Local: `uvicorn services.ordering.main:app --host 127.0.0.1 --port 8002` — OpenAPI `http://127.0.0.1:8002/docs`
