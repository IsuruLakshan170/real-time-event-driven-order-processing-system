
OrderFlow — Current Completed Project (Status Doc)

1) Tech Stack (implemented)
- Order Service — Java 21, Spring Boot 4.0.2
- Payment Service — Java 21, Spring Boot 4.0.2
- Kafka broker (Confluent), PostgreSQL, Docker Compose

2) Services
- Order Service: POST /api/v1/orders, saves order, publishes order-created
- Payment Service: consumes order-created, simulates payment, writes payments, publishes payment-status

3) Database
- orders table
- payments table
- inventory table
- event_log table

4) Kafka Topics
- order-created, payment-status

5) How to run
- docker-compose up -d
- start order-service
- start payment-service
- POST /orders

6) Next steps
- Inventory Service, Notification Service, DTO event serialization
