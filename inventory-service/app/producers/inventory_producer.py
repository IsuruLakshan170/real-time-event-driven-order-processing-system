from kafka import KafkaProducer
from ..config import settings
import json

class InventoryProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            key_serializer=lambda k: k.encode('utf-8'),
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def publish_inventory_status(self, key: str, payload: dict):
        self.producer.send(settings.topic_inventory_status, key=key, value=payload)
        self.producer.flush()