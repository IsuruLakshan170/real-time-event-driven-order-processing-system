# app/consumers.py
import json
import logging
import traceback
from typing import Any, Dict
from kafka import KafkaConsumer
from pythonjsonlogger import jsonlogger
from threading import Event

def _setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter("%(levelname)s %(message)s %(name)s")
    handler.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger

log = _setup_logger("notification-svc")

class NotificationConsumers:
    def __init__(self, bootstrap_servers: str, group_id: str, stop_event: Event):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.stop_event = stop_event


    def _build_consumer(self, topic: str) -> KafkaConsumer:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=[self.bootstrap_servers],
            group_id=self.group_id,
            enable_auto_commit=True,
            auto_offset_reset="earliest",
            value_deserializer=lambda b: json.loads(b.decode("utf-8")),
            key_deserializer=lambda b: b.decode("utf-8") if b else None,

            # --- Important: request_timeout_ms must be > session_timeout_ms ---
            session_timeout_ms=10000,         # 10s (default; explicit here for clarity)
            request_timeout_ms=45000,         # 45s (> 10s)  ✅ FIX
            heartbeat_interval_ms=3000,       # 3s (typical: ~1/3 of session timeout)

            api_version_auto_timeout_ms=5000,
            metadata_max_age_ms=5000,
            security_protocol="PLAINTEXT",
        )
        return consumer


    def _notify(self, event_type: str, payload: Dict[str, Any], key: str | None):
        order_id = payload.get("orderId") or key or "unknown"
        status = payload.get("status") or payload.get("state") or "UNKNOWN"
        log.info(
            "notification",
            extra={"eventType": event_type, "orderId": order_id, "status": status, "payload": payload},
        )

    def _run_loop(self, topic: str, label: str):
        log.info(f"consumer-started for topic '{topic}'", extra={"consumer": label, "bootstrap": self.bootstrap_servers})
        try:
            consumer = self._build_consumer(topic)
            log.info("consumer-created", extra={"consumer": label, "topic": topic})
            while not self.stop_event.is_set():
                records = consumer.poll(timeout_ms=1000)
                if not records:
                    log.info("listening...", extra={"consumer": label, "topic": topic})
                    continue
                for tp, msgs in records.items():
                    for m in msgs:
                        log.info(
                            "message",
                            extra={
                                "consumer": label,
                                "topic": tp.topic,
                                "partition": tp.partition,
                                "offset": m.offset,
                                "key": m.key,
                            },
                        )
                        self._notify(topic, m.value, m.key)
        except Exception as e:
            log.error("consumer-crashed", extra={"consumer": label, "error": str(e)})
            traceback.print_exc()
        finally:
            try:
                consumer.close()
            except Exception:
                pass
            log.info(f"consumer-stopped for topic '{topic}'", extra={"consumer": label})

    # Public entrypoints for threads
    def consume_payment_status(self):
        self._run_loop("payment-status", "payment")

    def consume_inventory_status(self):
        self._run_loop("inventory-status", "inventory")