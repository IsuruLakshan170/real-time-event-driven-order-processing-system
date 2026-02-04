# Notification Service

Consumes `payment-status` and `inventory-status` Kafka topics and logs notifications.

## Run (local)
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8083