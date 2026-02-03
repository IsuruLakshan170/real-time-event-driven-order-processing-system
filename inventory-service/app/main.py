from fastapi import FastAPI
from .consumers.payment_consumer import PaymentStatusConsumer
from .db import init_pool, close_pool

app = FastAPI(title="Inventory Service", version="0.1.0")
consumer = PaymentStatusConsumer()

@app.on_event("startup")
def on_startup():
    print("[inventory-svc] 🚀 startup: init pool + start consumer")
    init_pool()
    consumer.start()

@app.on_event("shutdown")
def on_shutdown():
    print("[inventory-svc] 🛑 shutdown: stop consumer + close pool")
    consumer.stop()
    close_pool()

@app.get("/health")
def health():
    return {"status": "ok"}

