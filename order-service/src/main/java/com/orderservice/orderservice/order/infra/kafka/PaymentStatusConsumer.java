package com.orderservice.orderservice.order.infra.kafka;

import com.orderservice.orderservice.order.domain.repository.OrderRepository;
import com.orderservice.orderservice.order.domain.model.OrderEntity;
import com.paymentservice.paymentservice.payment.infra.events.PaymentStatusEvent;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;
import tools.jackson.databind.ObjectMapper;

import java.util.Optional;
import java.util.UUID;

@Component
public class PaymentStatusConsumer {

    private final OrderRepository orderRepository;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public PaymentStatusConsumer(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    @KafkaListener(topics = "payment-status", groupId = "order-svc")
    public void onPaymentStatus(ConsumerRecord<String, String> record) {
        String key = record.key();      // orderId
        String payload = record.value();

        try {
            PaymentStatusEvent evt = objectMapper.readValue(payload, PaymentStatusEvent.class);
            UUID orderId = UUID.fromString(evt.orderId());

            Optional<OrderEntity> opt = orderRepository.findById(orderId);
            if (opt.isEmpty()) {
                System.out.println("[order-svc] payment-status for unknown orderId=" + orderId);
                return;
            }

            OrderEntity order = opt.get();
            if ("FAILED".equalsIgnoreCase(evt.status())) {
                order.setStatus("FAILED");
            } else if ("SUCCESS".equalsIgnoreCase(evt.status())) {
                order.setStatus("PAID"); // we will move to COMPLETED after inventory step
            }

            orderRepository.save(order);
            System.out.println("[order-svc] Updated order " + orderId + " -> " + order.getStatus());

        } catch (Exception e) {
            // keep it simple for now; we'll add retries/DLT later
            throw new RuntimeException("Failed to process payment-status message", e);
        }
    }
}