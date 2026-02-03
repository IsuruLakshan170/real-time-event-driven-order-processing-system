import threading, time, json
from datetime import datetime, timezone
from kafka import KafkaConsumer
from tenacity import retry, wait_exponential, stop_after_attempt
from ..config import settings
from ..db import get_conn
from ..models import PaymentStatusEvent, InventoryStatusEvent
from ..producers.inventory_producer import InventoryProducer

class PaymentStatusConsumer:
    def __init__(self):
        self._stop = threading.Event()
        self.thread: threading.Thread | None = None
        self.producer = InventoryProducer()

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._run_loop, name='payment-status-consumer', daemon=True)
        self.thread.start()

    def stop(self):
        self._stop.set()
        if self.thread:
            self.thread.join(timeout=5)

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(10))
    def _build_consumer(self):
        return KafkaConsumer(
            settings.topic_payment_status,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=settings.kafka_group_id,
            enable_auto_commit=True,
            auto_offset_reset='earliest',
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )

    def _run_loop(self):
        print("[inventory-svc] ⏳ starting payment-status consumer loop...")
        consumer = self._build_consumer()
        print("[inventory-svc] ✅ consumer connected to Kafka; subscribed to topic:", settings.topic_payment_status)

        while not self._stop.is_set():
            polled = consumer.poll(timeout_ms=1000, max_records=50)
            if not polled:
                # heartbeat to show the loop is alive
                print("[inventory-svc] (loop alive) no messages in the last second...")
            for tp, record_batch in polled.items():
                print(f"[inventory-svc] 📥 received batch from {tp.topic} partition={tp.partition} size={len(record_batch)}")
                for msg in record_batch:
                    if self._stop.is_set():
                        break
                    try:
                        key = msg.key  # orderId
                        print(f"[inventory-svc] 🔑 key(orderId)={key} raw={msg.value}")
                        evt = PaymentStatusEvent(**msg.value)
                        print(f"[inventory-svc] ✍ parsed payment-status: orderId={evt.orderId} status={evt.status}")

                        if evt.status != 'SUCCESS':
                            print("[inventory-svc] ⚠ ignoring non-success payment for orderId=", evt.orderId)
                            continue

                        product_id = evt.productId or 'p-42'
                        reserved = self._reserve_stock(product_id)
                        print(f"[inventory-svc] 🏪 reserve result for product={product_id}: {reserved}")

                        out = InventoryStatusEvent(
                            orderId=evt.orderId,
                            productId=product_id,
                            status='RESERVED' if reserved else 'OUT_OF_STOCK',
                            createdAt=datetime.now(timezone.utc).isoformat()
                        )
                        self._publish_and_maybe_log(key, out)
                        print(f"[inventory-svc] 📤 published inventory-status for orderId={evt.orderId} -> {out.status}")

                    except Exception as e:
                        print("[inventory-svc] ❌ error processing payment-status:", e)
            time.sleep(0.2)

    def _reserve_stock(self, product_id: str) -> bool:
        sql = """
        UPDATE inventory
           SET quantity = quantity - 1
         WHERE product_id = %s
           AND quantity >= 1
        RETURNING product_id, quantity;
        """
        with get_conn() as conn:
            with conn.cursor() as cur:
                conn.autocommit = True
                cur.execute(sql, (product_id,))
                row = cur.fetchone()
                return row is not None

    def _publish_and_maybe_log(self, key: str, out: InventoryStatusEvent):
        payload = out.model_dump()
        self.producer.publish_inventory_status(key, payload)
        if settings.write_event_log:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    conn.autocommit = True
                    cur.execute(
                        "INSERT INTO event_log(event_type, key, payload_json, created_at) VALUES (%s,%s,%s, now())",
                        (out.eventType, key, json.dumps(payload))
                    )