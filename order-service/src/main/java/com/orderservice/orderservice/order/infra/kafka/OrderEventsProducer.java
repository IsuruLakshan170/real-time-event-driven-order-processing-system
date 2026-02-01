package com.orderservice.orderservice.order.infra.kafka;

import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

@Component
public class OrderEventsProducer {

    private final KafkaTemplate<String, String> kafka;

    public OrderEventsProducer(KafkaTemplate<String, String> kafka) {
        this.kafka = kafka;
    }

    public void publishOrderCreated(String key, String payload) {
        kafka.send("order-created", key, payload);
    }
}