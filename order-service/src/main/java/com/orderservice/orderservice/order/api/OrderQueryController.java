package com.orderservice.orderservice.order.api;

import com.orderservice.orderservice.order.domain.model.OrderEntity;
import com.orderservice.orderservice.order.domain.repository.OrderRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/orders")
public class OrderQueryController {

    private final OrderRepository orderRepository;

    public OrderQueryController(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> get(@PathVariable("id") String id) {
        try {
            UUID orderId = UUID.fromString(id);
            Optional<OrderEntity> opt = orderRepository.findById(orderId);
            if (opt.isEmpty()) {
                return ResponseEntity.notFound().build();
            }
            OrderEntity o = opt.get();
            // minimal JSON response (you can create a record DTO if you want)
            return ResponseEntity.ok(
                    java.util.Map.of(
                            "orderId", o.getId().toString(),
                            "userId", o.getUserId(),
                            "productId", o.getProductId(),
                            "amount", o.getAmount(),
                            "status", o.getStatus(),
                            "createdAt", o.getCreatedAt()
                    )
            );
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(java.util.Map.of("error", "Invalid UUID"));
        }
    }
}
