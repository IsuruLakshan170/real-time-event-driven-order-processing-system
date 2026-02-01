package com.orderservice.orderservice.order.api.dto;

import java.math.BigDecimal;

public record CreateOrderRequest(
        String userId,
        String productId,
        BigDecimal amount
) {}