package com.orderservice.orderservice.order.infra.kafka;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.orderservice.orderservice.order.domain.model.OrderEntity;
import com.orderservice.orderservice.order.domain.repository.OrderRepository;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

import java.util.Optional;
import java.util.UUID;

@Component
public class InventoryStatusConsumer {

    private final OrderRepository orderRepository;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public InventoryStatusConsumer(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    @KafkaListener(topics = "inventory-status", groupId = "order-svc")
    public void onInventoryStatus(ConsumerRecord<String, String> record) {
        String key = record.key();      // orderId
        String payload = record.value();

        try {
            InventoryStatusEvent evt = objectMapper.readValue(payload, InventoryStatusEvent.class);
            UUID orderId = UUID.fromString(evt.orderId());

            Optional<OrderEntity> opt = orderRepository.findById(orderId);
            if (opt.isEmpty()) {
                System.out.println("[order-svc] inventory-status for unknown orderId=" + orderId);
                return;
            }

            OrderEntity order = opt.get();

            if ("RESERVED".equalsIgnoreCase(evt.status())) {
                order.setStatus("COMPLETED");     // ✅ final happy-path state
            } else if ("OUT_OF_STOCK".equalsIgnoreCase(evt.status())) {
                // Pick the semantics you want:
                // option A: keep as PAID but undeliverable
                // option B: mark FAILED
                order.setStatus("FAILED");
            }

            orderRepository.save(order);
            System.out.println("[order-svc] Updated order " + orderId + " -> " + order.getStatus());

        } catch (Exception e) {
            throw new RuntimeException("Failed to process inventory-status message", e);
        }
    }
}
