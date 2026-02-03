from pydantic import BaseModel
from typing import Literal

class PaymentStatusEvent(BaseModel):
    eventType: str
    eventVersion: int
    orderId: str
    status: Literal['SUCCESS','FAILED']
    txnRef: str | None = None
    createdAt: str | None = None
    # Optional: include productId if producer provides it
    productId: str | None = None

class InventoryStatusEvent(BaseModel):
    eventType: str = 'InventoryStatus'
    eventVersion: int = 1
    orderId: str
    productId: str
    status: Literal['RESERVED','OUT_OF_STOCK']
    createdAt: str