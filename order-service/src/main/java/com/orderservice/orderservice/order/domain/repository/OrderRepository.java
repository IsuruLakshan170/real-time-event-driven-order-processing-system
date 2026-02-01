package com.orderservice.orderservice.order.domain.repository;

import com.orderservice.orderservice.order.domain.model.OrderEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;

public interface OrderRepository extends JpaRepository<OrderEntity, UUID> {}
