package com.orderservice.orderservice.order.api.dto;

public record CreateOrderResponse(
        String orderId,
        String status
) {}