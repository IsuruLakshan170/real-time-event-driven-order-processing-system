package com.orderservice.orderservice.order;

import org.springframework.http.ResponseEntity;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {

    private final OrderRepository repo;
    private final KafkaTemplate<String, String> kafka;

    public OrderController(OrderRepository repo, KafkaTemplate<String, String> kafka) {
        this.repo = repo;
        this.kafka = kafka;
    }

    // Request body
    record OrderReq(String userId, String productId, BigDecimal amount) {}

    @PostMapping
    public ResponseEntity<?> create(@RequestBody OrderReq req) {
        // 1) Persist (Hibernate generates UUID via @UuidGenerator in OrderEntity)
        OrderEntity saved = repo.save(new OrderEntity(
                req.userId(), req.productId(), req.amount(), "PENDING"
        ));
        UUID orderId = saved.getId();

        // 2) Publish event
        String payload = String.format(
                "{\"orderId\":\"%s\",\"amount\":%s,\"productId\":\"%s\"}",
                orderId, saved.getAmount(), saved.getProductId()
        );
        kafka.send("order-created", orderId.toString(), payload);

        // 3) Respond
        return ResponseEntity.status(201).body(Map.of(
                "orderId", orderId.toString(),
                "status",  "PENDING"
        ));
    }
}