package com.orderservice.orderservice.order.domain.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.annotations.UuidGenerator;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;
import java.util.Date;
import java.util.UUID;

@Entity
@Table(name = "orders")
@Data
@NoArgsConstructor
public class OrderEntity {

    @Id
    @UuidGenerator
    @JdbcTypeCode(SqlTypes.UUID)
    @Column(columnDefinition = "uuid")
    private UUID id;

    private String userId;
    private String productId;

    @Column(precision = 12, scale = 2)
    private BigDecimal amount;

    private String status;

    @Temporal(TemporalType.TIMESTAMP)
    private Date createdAt = new Date();

    // Minimal convenience constructor (no id; Hibernate will generate it)
    public OrderEntity(String userId, String productId, BigDecimal amount, String status) {
        this.userId = userId;
        this.productId = productId;
        this.amount = amount;
        this.status = status;
    }
}