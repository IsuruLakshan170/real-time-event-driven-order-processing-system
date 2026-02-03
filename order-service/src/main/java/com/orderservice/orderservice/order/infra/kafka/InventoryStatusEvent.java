package com.orderservice.orderservice.order.infra.kafka;

public record InventoryStatusEvent(
        String eventType,
        int eventVersion,
        String orderId,
        String productId,
        String status,      // "RESERVED" or "OUT_OF_STOCK"
        String createdAt
) {}