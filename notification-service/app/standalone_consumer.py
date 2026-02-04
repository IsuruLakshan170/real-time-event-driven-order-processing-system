import os
import time
from threading import Event
from app.consumers import NotificationConsumers

if __name__ == "__main__":
    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092")  # IPv4 loopback
    stop = Event()
    cons = NotificationConsumers(bootstrap_servers=bootstrap, group_id="notification-svc-v4", stop_event=stop)

    # Start each loop in its own thread (non-daemon so the process stays alive)
    from threading import Thread
    t1 = Thread(target=cons.consume_payment_status, name="payment-consumer", daemon=False)
    t2 = Thread(target=cons.consume_inventory_status, name="inventory-consumer", daemon=False)
    t1.start(); t2.start()

    print(f"[runner] started with bootstrap={bootstrap} group=notification-svc-v4")
    print("[runner] press Ctrl+C to stop")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[runner] stopping...")
        stop.set()
        t1.join(timeout=3)
        t2.join(timeout=3)
        print("[runner] stopped.")