package com.orderservice.orderservice.order.infra.kafka;

import java.math.BigDecimal;
import java.time.Instant;

public record OrderCreatedEvent(
        String eventType,
        int eventVersion,
        String orderId,
        String userId,
        String productId,
        BigDecimal amount,
        Instant createdAt
) {}