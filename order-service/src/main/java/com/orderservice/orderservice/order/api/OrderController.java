package com.orderservice.orderservice.order.api;

import com.orderservice.orderservice.order.api.dto.CreateOrderRequest;
import com.orderservice.orderservice.order.api.dto.CreateOrderResponse;
import com.orderservice.orderservice.order.domain.model.OrderEntity;
import com.orderservice.orderservice.order.domain.service.OrderService;
import com.orderservice.orderservice.order.infra.kafka.OrderEventsProducer;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import tools.jackson.databind.ObjectMapper;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {

    private final OrderService orderService;
    private final OrderEventsProducer producer;
    private final ObjectMapper objectMapper;

    public OrderController(OrderService orderService, OrderEventsProducer producer, ObjectMapper objectMapper) {
        this.orderService = orderService;
        this.producer = producer;
        this.objectMapper = objectMapper;
    }


    @PostMapping
    public ResponseEntity<CreateOrderResponse> create(@RequestBody CreateOrderRequest req) {
        // 1) Persist via domain service
        OrderEntity saved = orderService.create(req.userId(), req.productId(), req.amount());
        UUID orderId = saved.getId();

        // 2) Publish event via infra adapter
        String payload = String.format(
                "{\"orderId\":\"%s\",\"amount\":%s,\"productId\":\"%s\"}",
                orderId, saved.getAmount(), saved.getProductId()
        );
        producer.publishOrderCreated(orderId.toString(), payload);

        // 3) Return DTO
        return ResponseEntity.status(201)
                .body(new CreateOrderResponse(orderId.toString(), "PENDING"));
    }
}