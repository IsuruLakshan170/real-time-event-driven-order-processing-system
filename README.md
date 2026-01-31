
# OrderFlow (Starter)

**Tech:** Spring Boot (Order Service), Python FastAPI (Inventory), Kafka, PostgreSQL, Docker

## Quickstart
1. Start infra:
```bash
cd infra
docker compose up -d
```
2. Build and run order-service locally:
```bash
cd ../order-service
mvn spring-boot:run
```
3. Run inventory-service locally:
```bash
cd ../inventory-service
pip install -r requirements.txt
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
export DATABASE_URL=postgresql://orderflow:password@localhost:5432/orderflow
uvicorn main:app --host 0.0.0.0 --port 8082
```
4. Create order:
```bash
curl -X POST http://localhost:8080/api/v1/orders   -H 'Content-Type: application/json'   -d '{"userId":"u-1","productId":"p-42","amount":1499.00}'
```

> Next: add Payment Service, Notification Service, retries/DLT, and containerize services into compose.
