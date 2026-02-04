# app/main.py  (Notification Service)
import os
from fastapi import FastAPI
from threading import Thread, Event
from app.consumers import NotificationConsumers

app = FastAPI(title="Notification Service", version="1.0.0")
stop_event = Event()
workers: list[Thread] = []

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092")  # IPv4
GROUP_ID = os.getenv("NOTIF_GROUP_ID", "notification-svc-v5")       # fresh group

@app.on_event("startup")
def on_startup():
    global workers
    cons = NotificationConsumers(bootstrap_servers=BOOTSTRAP, group_id=GROUP_ID, stop_event=stop_event)
    workers = [
        Thread(target=cons.consume_payment_status, name="payment-consumer", daemon=True),
        Thread(target=cons.consume_inventory_status, name="inventory-consumer", daemon=True),
    ]
    for t in workers: t.start()

@app.on_event("shutdown")
def on_shutdown():
    stop_event.set()
    for t in workers: t.join(timeout=3)

@app.get("/health")
def health():
    return {"status": "ok", "bootstrap": BOOTSTRAP, "groupId": GROUP_ID}