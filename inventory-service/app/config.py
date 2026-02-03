from pydantic import BaseModel
import os

class Settings(BaseModel):
    kafka_bootstrap_servers: str = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9093')
    kafka_group_id: str = os.getenv('KAFKA_GROUP_ID', 'inventory-svc')
    topic_payment_status: str = os.getenv('TOPIC_PAYMENT_STATUS', 'payment-status')
    topic_inventory_status: str = os.getenv('TOPIC_INVENTORY_STATUS', 'inventory-status')

    postgres_url: str = os.getenv('POSTGRES_URL', 'postgresql://orderflow:password@localhost:5433/orderflow')
    write_event_log: bool = os.getenv('WRITE_EVENT_LOG', 'true').lower() == 'true'

settings = Settings()
