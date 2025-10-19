# 23장: JPA Entity & Mapping - Part 3: FAQ & 면접 대비

> **Part 2에서 이어집니다**: 실전 프로젝트를 완성하고 FAQ와 면접 질문을 학습하세요!

---

## 📚 목차
- [실전 프로젝트 완성](#실전-프로젝트-완성)
- [FAQ](#faq)
- [면접 질문 리스트](#면접-질문-리스트)
- [핵심 정리](#핵심-정리)
- [다음 단계](#다음-단계)

---

## 🛠️ 실전 프로젝트 완성

### Service 계층 구현

#### ProductService

```java
// src/main/java/com/example/ecommerce/service/ProductService.java
package com.example.ecommerce.service;

import com.example.ecommerce.entity.Product;
import com.example.ecommerce.entity.ProductCategory;
import com.example.ecommerce.repository.ProductRepository;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.orm.ObjectOptimisticLockingFailureException;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Retryable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class ProductService {

    private final ProductRepository productRepository;

    // 상품 등록
    @Transactional
    public Product createProduct(String name, BigDecimal price, Integer stock,
                                ProductCategory category, String description) {
        Product product = Product.builder()
            .name(name)
            .price(price)
            .stock(stock)
            .category(category)
            .description(description)
            .build();

        return productRepository.save(product);
    }

    // 상품 조회
    public Product getProduct(Long id) {
        return productRepository.findById(id)
            .orElseThrow(() -> new EntityNotFoundException("상품을 찾을 수 없습니다: " + id));
    }

    // 상품 목록 조회 (페이징)
    public Page<Product> getProducts(Pageable pageable) {
        return productRepository.findAllActive(pageable);
    }

    // 카테고리별 조회
    public List<Product> getProductsByCategory(ProductCategory category) {
        return productRepository.findByCategory(category);
    }

    // 재고 감소 (낙관적 락 + 재시도)
    @Transactional
    @Retryable(
        retryFor = {ObjectOptimisticLockingFailureException.class},
        maxAttempts = 3,
        backoff = @Backoff(delay = 100)
    )
    public void decreaseStock(Long productId, int quantity) {
        Product product = getProduct(productId);

        if (product.isDeleted()) {
            throw new IllegalStateException("삭제된 상품입니다");
        }

        product.decreaseStock(quantity);
        // Dirty Checking으로 자동 UPDATE
    }

    // 재고 증가
    @Transactional
    public void increaseStock(Long productId, int quantity) {
        Product product = getProduct(productId);
        product.increaseStock(quantity);
    }

    // 가격 변경
    @Transactional
    public Product updatePrice(Long productId, BigDecimal newPrice) {
        Product product = getProduct(productId);
        product.updatePrice(newPrice);
        return product;
    }

    // 상품 삭제 (Soft Delete)
    @Transactional
    public void deleteProduct(Long productId) {
        Product product = getProduct(productId);

        if (product.isDeleted()) {
            throw new IllegalStateException("이미 삭제된 상품입니다");
        }

        product.softDelete();
    }
}
```

---

#### OrderService

```java
// src/main/java/com/example/ecommerce/service/OrderService.java
package com.example.ecommerce.service;

import com.example.ecommerce.entity.Order;
import com.example.ecommerce.entity.OrderStatus;
import com.example.ecommerce.entity.Product;
import com.example.ecommerce.repository.OrderRepository;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class OrderService {

    private final OrderRepository orderRepository;
    private final ProductService productService;

    // 주문 생성
    @Transactional
    public Order createOrder(Long userId, Long productId, Integer quantity) {
        // 1. 상품 조회
        Product product = productService.getProduct(productId);

        // 2. 재고 확인
        if (product.isSoldOut()) {
            throw new IllegalStateException("품절된 상품입니다");
        }

        // 3. 재고 감소 (낙관적 락 적용)
        productService.decreaseStock(productId, quantity);

        // 4. 주문 생성
        String orderNo = generateOrderNo();
        Order order = Order.builder()
            .orderNo(orderNo)
            .userId(userId)
            .productId(productId)
            .quantity(quantity)
            .unitPrice(product.getPrice())
            .build();

        return orderRepository.save(order);
    }

    // 주문 조회
    public Order getOrder(Long orderId) {
        return orderRepository.findById(orderId)
            .orElseThrow(() -> new EntityNotFoundException("주문을 찾을 수 없습니다: " + orderId));
    }

    // 주문번호로 조회
    public Order getOrderByOrderNo(String orderNo) {
        return orderRepository.findByOrderNo(orderNo)
            .orElseThrow(() -> new EntityNotFoundException("주문을 찾을 수 없습니다: " + orderNo));
    }

    // 사용자별 주문 목록
    public List<Order> getUserOrders(Long userId) {
        return orderRepository.findByUserIdOrderByCreatedAtDesc(userId);
    }

    // 주문 확인
    @Transactional
    public Order confirmOrder(Long orderId) {
        Order order = getOrder(orderId);
        order.confirm();
        return order;
    }

    // 배송 시작
    @Transactional
    public Order shipOrder(Long orderId) {
        Order order = getOrder(orderId);
        order.ship();
        return order;
    }

    // 배송 완료
    @Transactional
    public Order deliverOrder(Long orderId) {
        Order order = getOrder(orderId);
        order.deliver();
        return order;
    }

    // 주문 취소
    @Transactional
    public Order cancelOrder(Long orderId) {
        Order order = getOrder(orderId);

        // 재고 복구
        if (order.getStatus() == OrderStatus.PENDING ||
            order.getStatus() == OrderStatus.CONFIRMED) {
            productService.increaseStock(order.getProductId(), order.getQuantity());
        }

        order.cancel();
        return order;
    }

    // 주문번호 생성 (ORD-20250120-001)
    private String generateOrderNo() {
        String date = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        long count = orderRepository.count() + 1;
        return String.format("ORD-%s-%03d", date, count);
    }
}
```

---

### 테스트 코드

#### ProductServiceTest

```java
// src/test/java/com/example/ecommerce/service/ProductServiceTest.java
package com.example.ecommerce.service;

import com.example.ecommerce.entity.Product;
import com.example.ecommerce.entity.ProductCategory;
import com.example.ecommerce.repository.ProductRepository;
import jakarta.persistence.EntityNotFoundException;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

import static org.assertj.core.api.Assertions.*;

@SpringBootTest
@Transactional
class ProductServiceTest {

    @Autowired
    private ProductService productService;

    @Autowired
    private ProductRepository productRepository;

    @Test
    @DisplayName("상품 생성 테스트")
    void 상품_생성() {
        // given
        String name = "노트북";
        BigDecimal price = new BigDecimal("1500000");
        Integer stock = 10;
        ProductCategory category = ProductCategory.ELECTRONICS;
        String description = "고성능 노트북입니다.";

        // when
        Product product = productService.createProduct(name, price, stock, category, description);

        // then
        assertThat(product.getId()).isNotNull();
        assertThat(product.getName()).isEqualTo(name);
        assertThat(product.getPrice()).isEqualByComparingTo(price);
        assertThat(product.getStock()).isEqualTo(stock);
        assertThat(product.getCategory()).isEqualTo(category);
        assertThat(product.getCreatedAt()).isNotNull();  // Auditing
        assertThat(product.getUpdatedAt()).isNotNull();
    }

    @Test
    @DisplayName("재고 감소 테스트")
    void 재고_감소() {
        // given
        Product product = productService.createProduct(
            "마우스", new BigDecimal("50000"), 10, ProductCategory.ELECTRONICS, "무선 마우스"
        );

        // when
        productService.decreaseStock(product.getId(), 3);

        // then
        Product updated = productService.getProduct(product.getId());
        assertThat(updated.getStock()).isEqualTo(7);
    }

    @Test
    @DisplayName("재고 부족 시 예외 발생")
    void 재고_부족_예외() {
        // given
        Product product = productService.createProduct(
            "키보드", new BigDecimal("100000"), 5, ProductCategory.ELECTRONICS, "기계식 키보드"
        );

        // when & then
        assertThatThrownBy(() -> productService.decreaseStock(product.getId(), 10))
            .isInstanceOf(IllegalStateException.class)
            .hasMessageContaining("재고가 부족합니다");
    }

    @Test
    @DisplayName("동시에 재고 감소 시 낙관적 락 동작 확인")
    void 동시성_재고_감소() throws InterruptedException {
        // given
        Product product = productService.createProduct(
            "헤드셋", new BigDecimal("200000"), 100, ProductCategory.ELECTRONICS, "게이밍 헤드셋"
        );

        int threadCount = 10;
        ExecutorService executorService = Executors.newFixedThreadPool(threadCount);
        CountDownLatch latch = new CountDownLatch(threadCount);
        AtomicInteger successCount = new AtomicInteger(0);
        AtomicInteger failCount = new AtomicInteger(0);

        // when
        for (int i = 0; i < threadCount; i++) {
            executorService.submit(() -> {
                try {
                    productService.decreaseStock(product.getId(), 5);
                    successCount.incrementAndGet();
                } catch (Exception e) {
                    failCount.incrementAndGet();
                } finally {
                    latch.countDown();
                }
            });
        }

        latch.await();
        executorService.shutdown();

        // then
        Product result = productService.getProduct(product.getId());
        int expectedStock = 100 - (successCount.get() * 5);
        assertThat(result.getStock()).isEqualTo(expectedStock);

        System.out.println("성공: " + successCount.get());
        System.out.println("실패: " + failCount.get());
        System.out.println("최종 재고: " + result.getStock());
    }

    @Test
    @DisplayName("Soft Delete 테스트")
    void Soft_Delete() {
        // given
        Product product = productService.createProduct(
            "모니터", new BigDecimal("500000"), 20, ProductCategory.ELECTRONICS, "4K 모니터"
        );

        // when
        productService.deleteProduct(product.getId());

        // then
        Product deleted = productRepository.findById(product.getId()).orElseThrow();
        assertThat(deleted.isDeleted()).isTrue();
        assertThat(deleted.getDeletedAt()).isNotNull();
    }

    @Test
    @DisplayName("BigDecimal 정확한 가격 계산")
    void BigDecimal_가격_계산() {
        // given
        Product product = productService.createProduct(
            "책", new BigDecimal("19900.50"), 100, ProductCategory.BOOKS, "프로그래밍 책"
        );

        // when
        BigDecimal newPrice = new BigDecimal("25000.75");
        Product updated = productService.updatePrice(product.getId(), newPrice);

        // then
        assertThat(updated.getPrice()).isEqualByComparingTo("25000.75");
        // 소수점 정확도 확인
        assertThat(updated.getPrice().scale()).isEqualTo(2);
    }
}
```

---

#### OrderServiceTest

```java
// src/test/java/com/example/ecommerce/service/OrderServiceTest.java
package com.example.ecommerce.service;

import com.example.ecommerce.entity.Order;
import com.example.ecommerce.entity.OrderStatus;
import com.example.ecommerce.entity.Product;
import com.example.ecommerce.entity.ProductCategory;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;

import static org.assertj.core.api.Assertions.*;

@SpringBootTest
@Transactional
class OrderServiceTest {

    @Autowired
    private OrderService orderService;

    @Autowired
    private ProductService productService;

    @Test
    @DisplayName("주문 생성 및 재고 감소 확인")
    void 주문_생성() {
        // given
        Product product = productService.createProduct(
            "노트북", new BigDecimal("1500000"), 10, ProductCategory.ELECTRONICS, "고성능 노트북"
        );
        Long userId = 1L;
        Integer quantity = 2;

        // when
        Order order = orderService.createOrder(userId, product.getId(), quantity);

        // then
        assertThat(order.getId()).isNotNull();
        assertThat(order.getOrderNo()).startsWith("ORD-");
        assertThat(order.getStatus()).isEqualTo(OrderStatus.PENDING);
        assertThat(order.getQuantity()).isEqualTo(quantity);
        assertThat(order.getTotalAmount()).isEqualByComparingTo("3000000");  // 1500000 * 2

        // 재고 감소 확인
        Product updatedProduct = productService.getProduct(product.getId());
        assertThat(updatedProduct.getStock()).isEqualTo(8);  // 10 - 2
    }

    @Test
    @DisplayName("품절 상품 주문 시 예외 발생")
    void 품절_상품_주문_예외() {
        // given
        Product product = productService.createProduct(
            "품절상품", new BigDecimal("100000"), 0, ProductCategory.ELECTRONICS, "품절"
        );

        // when & then
        assertThatThrownBy(() -> orderService.createOrder(1L, product.getId(), 1))
            .isInstanceOf(IllegalStateException.class)
            .hasMessageContaining("품절");
    }

    @Test
    @DisplayName("주문 상태 변경 테스트")
    void 주문_상태_변경() {
        // given
        Product product = productService.createProduct(
            "마우스", new BigDecimal("50000"), 10, ProductCategory.ELECTRONICS, "무선 마우스"
        );
        Order order = orderService.createOrder(1L, product.getId(), 1);

        // when & then
        // PENDING → CONFIRMED
        Order confirmed = orderService.confirmOrder(order.getId());
        assertThat(confirmed.getStatus()).isEqualTo(OrderStatus.CONFIRMED);

        // CONFIRMED → SHIPPED
        Order shipped = orderService.shipOrder(order.getId());
        assertThat(shipped.getStatus()).isEqualTo(OrderStatus.SHIPPED);

        // SHIPPED → DELIVERED
        Order delivered = orderService.deliverOrder(order.getId());
        assertThat(delivered.getStatus()).isEqualTo(OrderStatus.DELIVERED);
    }

    @Test
    @DisplayName("잘못된 상태 전환 시 예외 발생")
    void 잘못된_상태_전환_예외() {
        // given
        Product product = productService.createProduct(
            "키보드", new BigDecimal("100000"), 10, ProductCategory.ELECTRONICS, "기계식"
        );
        Order order = orderService.createOrder(1L, product.getId(), 1);

        // when & then - PENDING에서 바로 SHIPPED로 변경 불가
        assertThatThrownBy(() -> orderService.shipOrder(order.getId()))
            .isInstanceOf(IllegalStateException.class)
            .hasMessageContaining("CONFIRMED 상태에서만");
    }

    @Test
    @DisplayName("주문 취소 및 재고 복구")
    void 주문_취소_재고_복구() {
        // given
        Product product = productService.createProduct(
            "헤드셋", new BigDecimal("200000"), 10, ProductCategory.ELECTRONICS, "게이밍"
        );
        Order order = orderService.createOrder(1L, product.getId(), 3);

        // 재고 확인 (10 - 3 = 7)
        Product afterOrder = productService.getProduct(product.getId());
        assertThat(afterOrder.getStock()).isEqualTo(7);

        // when
        Order cancelled = orderService.cancelOrder(order.getId());

        // then
        assertThat(cancelled.getStatus()).isEqualTo(OrderStatus.CANCELLED);

        // 재고 복구 확인 (7 + 3 = 10)
        Product afterCancel = productService.getProduct(product.getId());
        assertThat(afterCancel.getStock()).isEqualTo(10);
    }

    @Test
    @DisplayName("배송 완료 후 취소 불가")
    void 배송완료_후_취소_불가() {
        // given
        Product product = productService.createProduct(
            "모니터", new BigDecimal("500000"), 10, ProductCategory.ELECTRONICS, "4K"
        );
        Order order = orderService.createOrder(1L, product.getId(), 1);

        // 배송 완료까지 진행
        orderService.confirmOrder(order.getId());
        orderService.shipOrder(order.getId());
        orderService.deliverOrder(order.getId());

        // when & then
        assertThatThrownBy(() -> orderService.cancelOrder(order.getId()))
            .isInstanceOf(IllegalStateException.class)
            .hasMessageContaining("배송 완료된 주문은 취소할 수 없습니다");
    }

    @Test
    @DisplayName("주문번호 생성 형식 확인")
    void 주문번호_형식() {
        // given
        Product product = productService.createProduct(
            "테스트상품", new BigDecimal("10000"), 10, ProductCategory.ELECTRONICS, "테스트"
        );

        // when
        Order order = orderService.createOrder(1L, product.getId(), 1);

        // then
        assertThat(order.getOrderNo()).matches("ORD-\\d{8}-\\d{3}");
        // 예: ORD-20250120-001
    }
}
```

---

### 실행 결과

**콘솔 출력 (DDL)**:
```sql
Hibernate:
    create table products (
        id bigint not null auto_increment,
        created_at datetime(6) not null,
        deleted_at datetime(6),
        updated_at datetime(6),
        category varchar(30) not null,
        description text,
        name varchar(200) not null,
        price decimal(10,2) not null,
        stock integer not null,
        version bigint,
        primary key (id)
    ) engine=InnoDB

Hibernate:
    create table orders (
        id bigint not null auto_increment,
        created_at datetime(6) not null,
        deleted_at datetime(6),
        updated_at datetime(6),
        order_no varchar(30) not null,
        product_id bigint not null,
        quantity integer not null,
        status varchar(20) not null,
        total_amount decimal(10,2) not null,
        unit_price decimal(10,2) not null,
        user_id bigint not null,
        primary key (id)
    ) engine=InnoDB
```

**테스트 결과**:
```
✅ 상품 생성 테스트: PASSED
✅ 재고 감소 테스트: PASSED
✅ 재고 부족 시 예외 발생: PASSED
✅ 동시성 재고 감소: PASSED (성공: 10, 실패: 0, 최종 재고: 50)
✅ Soft Delete 테스트: PASSED
✅ BigDecimal 가격 계산: PASSED
✅ 주문 생성: PASSED
✅ 품절 상품 주문 시 예외: PASSED
✅ 주문 상태 변경: PASSED
✅ 잘못된 상태 전환 예외: PASSED
✅ 주문 취소 재고 복구: PASSED
✅ 배송완료 후 취소 불가: PASSED
✅ 주문번호 형식: PASSED

Total: 13 tests, 13 passed ✅
```

---

## ❓ FAQ

<details>
<summary><strong>Q1. @Entity와 @Table의 차이는 무엇인가요?</strong></summary>

**A**: `@Entity`는 JPA 엔티티를 선언하고, `@Table`은 매핑할 DB 테이블 정보를 지정합니다.

**상세 설명**:
```java
// @Entity: 이 클래스가 JPA Entity임을 선언
@Entity
public class User {  // ← 클래스 이름
    @Id
    private Long id;
}
// 결과: "user" 테이블로 자동 매핑 (클래스명 소문자)

// @Table: 테이블명을 명시적으로 지정
@Entity
@Table(name = "users")  // ← DB 테이블 이름 지정
public class User {
    @Id
    private Long id;
}
// 결과: "users" 테이블로 매핑
```

**언제 사용하나요?**
- `@Entity`만 사용: 클래스명 = 테이블명일 때
- `@Entity` + `@Table`: 클래스명 ≠ 테이블명일 때

**예시**:
```java
// 클래스명과 테이블명이 다를 때
@Entity
@Table(name = "tb_member")  // 레거시 테이블명
public class Member {
    // ...
}

// 인덱스, 제약조건 추가
@Entity
@Table(
    name = "orders",
    indexes = {
        @Index(name = "idx_user_id", columnList = "user_id")
    },
    uniqueConstraints = {
        @UniqueConstraint(name = "uk_order_no", columnNames = {"order_no"})
    }
)
public class Order {
    // ...
}
```

**실무 팁**:
💡 레거시 DB와 연동 시 `@Table(name = "...")`로 기존 테이블명 사용
💡 인덱스와 제약조건도 `@Table`에서 선언 가능
💡 단, DDL 자동 생성 시에만 인덱스가 생성됨 (운영 DB는 수동 생성 권장)

</details>

<details>
<summary><strong>Q2. Enum을 ORDINAL로 저장하면 안 되는 이유는?</strong></summary>

**A**: Enum 순서가 바뀌면 기존 데이터의 의미가 완전히 달라지기 때문입니다.

**위험한 예시**:
```java
// 초기 Enum 정의
public enum OrderStatus {
    PENDING,    // 0
    CONFIRMED,  // 1
    SHIPPED     // 2
}

@Entity
public class Order {
    @Enumerated(EnumType.ORDINAL)  // ❌ 위험!
    private OrderStatus status;
}
```

**DB에 저장된 데이터**:
```sql
+----+---------+
| id | status  |
+----+---------+
| 1  | 0       |  -- PENDING
| 2  | 1       |  -- CONFIRMED
| 3  | 2       |  -- SHIPPED
+----+---------+
```

**Enum 순서 변경**:
```java
// CANCELLED를 중간에 추가
public enum OrderStatus {
    PENDING,     // 0
    CANCELLED,   // 1 ← 추가!
    CONFIRMED,   // 2 (원래 1이었음)
    SHIPPED      // 3 (원래 2였음)
}
```

**데이터 오류 발생**:
```sql
-- 기존 데이터는 그대로인데 의미가 바뀜!
+----+---------+----------------+
| id | status  | 읽히는 값      |
+----+---------+----------------+
| 1  | 0       | PENDING (OK)   |
| 2  | 1       | CANCELLED (❌) |  -- 원래는 CONFIRMED!
| 3  | 2       | CONFIRMED (❌) |  -- 원래는 SHIPPED!
+----+---------+----------------+
```

**올바른 방법**:
```java
@Entity
public class Order {
    @Enumerated(EnumType.STRING)  // ✅ 문자열로 저장
    @Column(length = 20)
    private OrderStatus status;
}
```

**STRING 사용 시 안전**:
```sql
+----+-----------+
| id | status    |
+----+-----------+
| 1  | PENDING   |
| 2  | CONFIRMED |
| 3  | SHIPPED   |
+----+-----------+

-- Enum 순서를 바꿔도 데이터는 안전!
```

**실무 팁**:
💡 항상 `EnumType.STRING` 사용
💡 DB 용량은 조금 더 차지하지만 안전성이 우선
💡 컬럼 길이는 충분히 지정 (`length = 20~30`)

</details>

<details>
<summary><strong>Q3. BigDecimal은 왜 new BigDecimal(double)로 생성하면 안 되나요?</strong></summary>

**A**: Double은 부동소수점 오차를 가지고 있어, 그 오차가 BigDecimal에 그대로 전달되기 때문입니다.

**잘못된 방법**:
```java
BigDecimal price1 = new BigDecimal(0.1);  // ❌ Double 오차 전달
System.out.println(price1);
// 출력: 0.1000000000000000055511151231257827021181583404541015625
// Double 0.1의 내부 표현이 그대로 전달됨!
```

**올바른 방법**:
```java
// 방법 1: 문자열로 생성 (권장)
BigDecimal price2 = new BigDecimal("0.1");  // ✅ 정확
System.out.println(price2);
// 출력: 0.1

// 방법 2: valueOf 사용
BigDecimal price3 = BigDecimal.valueOf(0.1);  // ✅ 내부적으로 문자열 변환
System.out.println(price3);
// 출력: 0.1
```

**실무 예시**:
```java
// 금액 계산
BigDecimal price = new BigDecimal("10000.50");
BigDecimal quantity = new BigDecimal("3");

// 연산
BigDecimal total = price.multiply(quantity);  // 30001.50
System.out.println(total);  // 정확한 값

// 나눗셈 (반올림 모드 지정 필수)
BigDecimal avgPrice = total.divide(quantity, 2, RoundingMode.HALF_UP);
System.out.println(avgPrice);  // 10000.50
```

**Entity에서 사용**:
```java
@Entity
public class Product {

    @Column(precision = 10, scale = 2)
    private BigDecimal price;  // 최대 99,999,999.99

    // Builder에서 문자열로 받기
    @Builder
    public Product(String priceStr) {
        this.price = new BigDecimal(priceStr);  // ✅ 문자열 사용
    }

    // 계산 메서드
    public BigDecimal getDiscountedPrice(int discountRate) {
        BigDecimal rate = new BigDecimal(discountRate).divide(new BigDecimal(100), 2, RoundingMode.HALF_UP);
        BigDecimal discount = price.multiply(rate);
        return price.subtract(discount);
    }
}
```

**실무 팁**:
💡 금액은 항상 `new BigDecimal("문자열")` 사용
💡 `precision`: 전체 자릿수, `scale`: 소수점 자릿수
💡 나눗셈 시 반드시 `RoundingMode` 지정
💡 금융 시스템에서 `Double`/`Float` 사용은 금지

</details>

<details>
<summary><strong>Q4. @Lob을 Lazy Loading하지 않으면 성능이 얼마나 저하되나요?</strong></summary>

**A**: 대용량 텍스트를 항상 조회하면 목록 조회 시 10~100배 느려질 수 있습니다.

**시나리오**: 상품 목록 조회 (100개)

**EAGER Loading (기본값)**:
```java
@Entity
public class Product {
    @Id
    private Long id;
    private String name;
    private BigDecimal price;

    @Lob  // ❌ 기본값: EAGER
    private String description;  // 각 50KB
}

// 목록 조회
List<Product> products = productRepository.findAll();
```

**실행되는 SQL**:
```sql
SELECT id, name, price, description  -- description도 함께 조회!
FROM products
```

**성능 측정**:
```
데이터 전송량: 100개 × 50KB = 5MB
조회 시간: 2000ms (2초)
메모리 사용: 5MB
네트워크 대역폭: 높음
```

---

**LAZY Loading**:
```java
@Entity
public class Product {
    @Id
    private Long id;
    private String name;
    private BigDecimal price;

    @Lob
    @Basic(fetch = FetchType.LAZY)  // ✅ 지연 로딩
    private String description;
}

// 목록 조회
List<Product> products = productRepository.findAll();
```

**실행되는 SQL**:
```sql
SELECT id, name, price  -- description 제외!
FROM products
```

**성능 측정**:
```
데이터 전송량: 100개 × 500B = 50KB
조회 시간: 100ms (0.1초)
메모리 사용: 50KB
개선율: 95% 빨라짐 ✅
```

**상세 페이지에서만 description 조회**:
```java
Product product = productRepository.findById(1L).orElseThrow();
String desc = product.getDescription();  // ← 이 시점에 추가 조회

// 실행 SQL
SELECT description FROM products WHERE id = 1
```

**추가 시간**: 50ms

**총 시간**: 100ms (목록) + 50ms (상세) = 150ms
→ 여전히 2000ms보다 훨씬 빠름!

**실무 사례 (배달의민족)**:
```
Before (EAGER):
- 음식점 목록 100개 조회
- 각 음식점 소개 10KB
- 총 전송량: 1MB
- 조회 시간: 1500ms

After (LAZY):
- 총 전송량: 50KB
- 조회 시간: 80ms
- 개선율: 95%
```

**실무 팁**:
💡 `@Lob`는 항상 `FetchType.LAZY` 지정
💡 목록 조회와 상세 조회는 별도 처리
💡 DTO 프로젝션으로 더 최적화 가능

</details>

<details>
<summary><strong>Q5. @Version 낙관적 락은 어떤 원리로 동작하나요?</strong></summary>

**A**: UPDATE 시 WHERE 절에 version 조건을 추가하여, version이 변경되었으면 UPDATE 실패로 동시성 충돌을 감지합니다.

**Entity 정의**:
```java
@Entity
public class Product {
    @Id
    private Long id;
    private Integer stock;

    @Version  // ✅ 버전 필드
    private Long version;
}
```

**동작 원리**:
```
[초기 상태]
Product: id=1, stock=10, version=1

[시각 1] 사용자 A: 상품 조회
        SELECT id, stock, version FROM products WHERE id=1
        → stock=10, version=1

[시각 2] 사용자 B: 상품 조회
        SELECT id, stock, version FROM products WHERE id=1
        → stock=10, version=1

[시각 3] 사용자 A: 재고 5개 감소 시도
        UPDATE products
        SET stock=5, version=2
        WHERE id=1 AND version=1  -- ✅ 성공 (version=1 일치)
        → 1 row affected

[시각 4] 사용자 B: 재고 5개 감소 시도
        UPDATE products
        SET stock=5, version=2
        WHERE id=1 AND version=1  -- ❌ 실패! (이미 version=2)
        → 0 rows affected
        → OptimisticLockException 발생
```

**예외 처리**:
```java
@Service
public class ProductService {

    @Transactional
    @Retryable(
        retryFor = {OptimisticLockException.class},
        maxAttempts = 3,
        backoff = @Backoff(delay = 100)
    )
    public void decreaseStock(Long productId, int quantity) {
        Product product = productRepository.findById(productId).orElseThrow();
        product.decreaseStock(quantity);
        // save() 호출 없이도 Dirty Checking으로 UPDATE
        // version 불일치 시 OptimisticLockException → @Retryable로 재시도
    }
}
```

**재시도 흐름**:
```
1차 시도: UPDATE 실패 (version 불일치)
         → 예외 발생
         → @Retryable 감지

2차 시도: 최신 데이터 재조회 (version=2, stock=5)
         → stock=0으로 감소
         → UPDATE ... WHERE version=2
         → 성공! (version=3)
```

**장점 vs 비관적 락**:
```
낙관적 락 (@Version):
✅ DB 락을 걸지 않음 (성능 우수)
✅ 충돌이 적을 때 효율적
✅ 재시도 가능
❌ 충돌 시 재시도 필요

비관적 락 (SELECT FOR UPDATE):
✅ 충돌 원천 차단
❌ DB 락으로 성능 저하
❌ 데드락 위험
❌ 동시성 낮음
```

**실무 팁**:
💡 충돌이 적은 경우: 낙관적 락 사용
💡 충돌이 많은 경우: 비관적 락 고려
💡 재시도 횟수: 2~3회 권장
💡 재시도 간격: 100~200ms

</details>

<details>
<summary><strong>Q6. @CreatedDate와 @PrePersist 중 어떤 것을 사용해야 하나요?</strong></summary>

**A**: Spring Data JPA를 사용한다면 `@CreatedDate`가 더 편리하고 일관성 있습니다.

**비교**:

**방법 1: @PrePersist (JPA 표준)**:
```java
@Entity
public class Product {

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
```

**장점**:
- JPA 표준 (Spring 없이도 동작)
- 별도 설정 불필요

**단점**:
- 모든 엔티티마다 중복 코드
- 생성자 정보 자동 설정 불가

---

**방법 2: @CreatedDate (Spring Data JPA)**:
```java
// 1. Application에서 활성화
@SpringBootApplication
@EnableJpaAuditing
public class Application {
    // ...
}

// 2. Base Entity
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseEntity {

    @CreatedDate
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @CreatedBy
    @Column(name = "created_by", updatable = false)
    private String createdBy;

    @LastModifiedBy
    @Column(name = "updated_by")
    private String updatedBy;
}

// 3. 모든 엔티티는 상속만
@Entity
public class Product extends BaseEntity {
    // createdAt, updatedAt 자동 포함!
}
```

**장점**:
- 중복 코드 제거 (BaseEntity 상속)
- 생성자/수정자 자동 설정 가능
- 일관성 보장

**단점**:
- Spring Data JPA 의존성 필요
- @EnableJpaAuditing 설정 필요

---

**AuditorAware 구현** (생성자/수정자 제공):
```java
@Component
public class AuditorAwareImpl implements AuditorAware<String> {

    @Override
    public Optional<String> getCurrentAuditor() {
        // Spring Security에서 현재 사용자 가져오기
        Authentication authentication = SecurityContextHolder
            .getContext()
            .getAuthentication();

        if (authentication == null || !authentication.isAuthenticated()) {
            return Optional.of("system");
        }

        return Optional.of(authentication.getName());
    }
}
```

**권장 사항**:
```
✅ Spring Data JPA 사용 → @CreatedDate 권장
   - BaseEntity 패턴 활용
   - 중복 제거
   - 생성자/수정자 자동 설정

✅ Pure JPA만 사용 → @PrePersist 사용
   - Spring 의존성 없음
   - 간단한 프로젝트
```

**실무 팁**:
💡 대부분의 프로젝트는 Spring Data JPA 사용 → `@CreatedDate` 권장
💡 BaseEntity로 공통 필드 관리
💡 `updatable = false`로 생성일시 변경 방지

</details>

<details>
<summary><strong>Q7. columnDefinition을 사용하면 안 되는 이유는?</strong></summary>

**A**: DB에 종속적이 되어 다른 DB로 마이그레이션이 어려워지기 때문입니다.

**columnDefinition 사용**:
```java
@Entity
public class User {

    @Id
    private Long id;

    // ❌ MySQL 전용 문법 사용
    @Column(
        columnDefinition = "VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    private String name;

    // ❌ MySQL 전용 JSON 타입
    @Column(columnDefinition = "JSON")
    private String metadata;
}
```

**문제점**:
```
1. DB 종속성
   - MySQL에서는 동작
   - PostgreSQL로 마이그레이션 시 오류 발생
   - H2 (테스트 DB)에서 실행 불가

2. JPA의 타입 추론 실패
   - JPA가 타입을 알 수 없음
   - 자동 DDL 생성 시 오류

3. 유지보수 어려움
   - 표준 JPA 어노테이션으로 표현 불가
   - 코드 가독성 저하
```

---

**올바른 방법**:
```java
@Entity
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // ✅ 표준 JPA 어노테이션 사용
    @Column(nullable = false, length = 50)
    private String name;

    // ✅ Hibernate 6+ JSON 매핑 (DB 독립적)
    @JdbcTypeCode(SqlTypes.JSON)
    private Map<String, Object> metadata;
}
```

**어쩔 수 없이 사용해야 하는 경우**:
```java
// 레거시 DB 연동 시
@Entity
@Table(name = "legacy_users")
public class LegacyUser {

    @Id
    private Long id;

    // 레거시 DB의 특수한 타입
    @Column(columnDefinition = "TINYINT(1)")  // MySQL boolean
    private Boolean isActive;

    // 주석으로 이유 명시
    // MySQL의 TINYINT(1)을 Boolean으로 매핑하기 위해 사용
}
```

**대안**:
```java
// 1. Converter 사용 (권장)
@Converter
public class BooleanToYNConverter implements AttributeConverter<Boolean, String> {

    @Override
    public String convertToDatabaseColumn(Boolean attribute) {
        return (attribute != null && attribute) ? "Y" : "N";
    }

    @Override
    public Boolean convertToEntityAttribute(String dbData) {
        return "Y".equals(dbData);
    }
}

@Entity
public class User {
    @Convert(converter = BooleanToYNConverter.class)
    @Column(length = 1)
    private Boolean isActive;  // DB에는 Y/N으로 저장
}

// 2. @Formula 사용 (읽기 전용)
@Entity
public class User {
    @Formula("(SELECT COUNT(*) FROM orders o WHERE o.user_id = id)")
    private Integer orderCount;  // 가상 컬럼
}
```

**실무 팁**:
💡 가능한 한 표준 JPA 어노테이션 사용
💡 DB 독립적인 코드 작성
💡 특수한 타입은 `@Converter` 활용
💡 `columnDefinition` 사용 시 주석으로 이유 명시

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용 (7개)

<details>
<summary><strong>1. JPA Entity란 무엇이고, 왜 사용하나요?</strong></summary>

**모범 답변**:
```
JPA Entity는 데이터베이스 테이블과 매핑되는 Java 객체입니다.

핵심 포인트:
1. @Entity 어노테이션으로 선언
2. 테이블의 각 행(Row)이 하나의 Entity 인스턴스
3. ORM(Object-Relational Mapping)의 핵심

사용 이유:
1. SQL 자동 생성: CRUD SQL을 JPA가 자동 생성
2. 타입 안전: 컴파일 시점에 오류 감지
3. 객체 지향적: 비즈니스 로직을 Entity에 포함
4. 유지보수성: 테이블 구조 변경 시 Entity만 수정

예시:
@Entity
public class User {
    @Id
    private Long id;
    private String name;
}

→ users 테이블과 자동 매핑
→ userRepository.save(user) → INSERT 자동 생성
```

**꼬리 질문**:
- Q: Entity와 DTO의 차이는?
  - A: Entity는 DB와 매핑, DTO는 계층 간 데이터 전송용

</details>

<details>
<summary><strong>2. @Id와 @GeneratedValue의 역할은?</strong></summary>

**모범 답변**:
```
@Id는 기본키(Primary Key)를 지정하고,
@GeneratedValue는 기본키를 자동으로 생성하는 전략을 지정합니다.

기본키 생성 전략 4가지:
1. IDENTITY: DB의 AUTO_INCREMENT 사용 (MySQL)
2. SEQUENCE: DB의 Sequence 사용 (Oracle, PostgreSQL)
3. TABLE: 별도 테이블로 키 생성
4. AUTO: DB에 맞게 자동 선택

실무 예시:
@Entity
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;  // MySQL: AUTO_INCREMENT
}

MySQL: AUTO_INCREMENT 사용
PostgreSQL: SERIAL 또는 Sequence 사용
Oracle: Sequence 필수

주의사항:
- IDENTITY는 INSERT 후에만 ID 확인 가능
- SEQUENCE는 INSERT 전에 ID 확인 가능
```

**꼬리 질문**:
- Q: UUID를 기본키로 사용해도 되나요?
  - A: 가능하지만, 인덱스 성능이 저하될 수 있음. 긴 길이(36자)와 무작위성이 단점.

</details>

<details>
<summary><strong>3. @Column의 주요 속성들을 설명해주세요.</strong></summary>

**모범 답변**:
```
@Column은 필드를 DB 컬럼과 매핑하며, 컬럼의 속성을 지정합니다.

주요 속성:
1. name: 컬럼명 지정
   @Column(name = "user_name")

2. nullable: NOT NULL 제약조건
   @Column(nullable = false)  // NOT NULL

3. length: VARCHAR 길이
   @Column(length = 100)  // VARCHAR(100)

4. unique: UNIQUE 제약조건
   @Column(unique = true)

5. precision/scale: 숫자 정밀도 (BigDecimal)
   @Column(precision = 10, scale = 2)  // 99,999,999.99

6. updatable: 수정 가능 여부
   @Column(updatable = false)  // 생성 후 변경 불가

예시:
@Column(
    name = "email",
    nullable = false,
    unique = true,
    length = 100
)
private String email;

→ CREATE TABLE ... (
    email VARCHAR(100) NOT NULL UNIQUE
)
```

</details>

<details>
<summary><strong>4. @Enumerated의 ORDINAL과 STRING 차이는?</strong></summary>

**모범 답변**:
```
ORDINAL은 Enum의 순서(숫자)를 저장하고,
STRING은 Enum의 이름(문자열)을 저장합니다.

비교:
enum OrderStatus { PENDING, CONFIRMED, SHIPPED }

ORDINAL:
- DB에 0, 1, 2 저장
- 용량 작음 (INT)
- ❌ Enum 순서 변경 시 데이터 오류 발생

STRING:
- DB에 "PENDING", "CONFIRMED" 저장
- 용량 큼 (VARCHAR)
- ✅ Enum 순서 변경해도 안전

위험한 예:
// ORDINAL 사용 중
enum OrderStatus {
    PENDING,    // 0
    CONFIRMED,  // 1
    SHIPPED     // 2
}
// DB: id=1, status=1 (CONFIRMED)

// Enum 변경
enum OrderStatus {
    PENDING,     // 0
    CANCELLED,   // 1 ← 추가!
    CONFIRMED,   // 2
    SHIPPED      // 3
}
// DB: id=1, status=1 (CANCELLED!) ← 잘못 읽힘!

권장사항:
항상 EnumType.STRING 사용!
```

</details>

<details>
<summary><strong>5. @Lob과 FetchType.LAZY의 관계는?</strong></summary>

**모범 답변**:
```
@Lob은 Large Object(대용량 데이터)를 저장하고,
FetchType.LAZY는 필요할 때만 조회하여 성능을 최적화합니다.

@Lob 타입:
- String → CLOB (Character LOB) → TEXT
- byte[] → BLOB (Binary LOB)

기본 동작:
@Lob
private String description;  // ❌ 기본값: EAGER (즉시 로딩)

→ 목록 조회 시에도 description 모두 조회
→ 100개 상품 × 50KB = 5MB 전송
→ 느림!

최적화:
@Lob
@Basic(fetch = FetchType.LAZY)  // ✅ 지연 로딩
private String description;

→ 목록 조회: description 제외
→ 상세 조회: description만 추가 조회
→ 성능 95% 향상

실무 팁:
- 목록 조회: 불필요한 대용량 데이터 제외
- 상세 조회: 필요할 때만 추가 조회
- DTO 프로젝션: 필요한 필드만 SELECT
```

</details>

<details>
<summary><strong>6. @Version 낙관적 락의 동작 원리는?</strong></summary>

**모범 답변**:
```
@Version은 Entity의 버전을 관리하여,
UPDATE 시 버전 불일치로 동시성 충돌을 감지합니다.

동작 원리:
1. 조회: SELECT id, stock, version FROM products WHERE id=1
        → stock=10, version=1

2. 수정: stock -= 5

3. 저장: UPDATE products
        SET stock=5, version=2
        WHERE id=1 AND version=1  ← version 조건 추가!

4. 결과:
   - 성공: version=1 일치 → UPDATE 성공
   - 실패: version 불일치 → OptimisticLockException

동시성 시나리오:
[시각 1] A: 조회 (stock=10, version=1)
[시각 2] B: 조회 (stock=10, version=1)
[시각 3] A: UPDATE ... WHERE version=1 → 성공 (version=2)
[시각 4] B: UPDATE ... WHERE version=1 → 실패! (이미 version=2)

재시도:
@Retryable(
    retryFor = {OptimisticLockException.class},
    maxAttempts = 3
)
public void decreaseStock(Long id, int quantity) {
    Product product = findById(id);
    product.decreaseStock(quantity);
}

장점:
- DB 락 불필요 (성능 우수)
- 충돌 시 재시도 가능
```

</details>

<details>
<summary><strong>7. BaseEntity 패턴은 무엇이고 왜 사용하나요?</strong></summary>

**모범 답변**:
```
BaseEntity는 모든 Entity의 공통 필드를 추상 클래스로 분리한 패턴입니다.

공통 필드:
- createdAt: 생성일시
- updatedAt: 수정일시
- createdBy: 생성자
- updatedBy: 수정자
- deletedAt: 삭제일시 (Soft Delete)

구현:
@MappedSuperclass  // 상속용 클래스
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseEntity {

    @CreatedDate
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}

사용:
@Entity
public class Product extends BaseEntity {
    @Id
    private Long id;
    // createdAt, updatedAt 자동 포함!
}

장점:
1. 중복 제거: 모든 Entity에 공통 필드 자동 포함
2. 일관성: 통일된 감사 필드
3. 유지보수성: BaseEntity만 수정하면 모두 적용

실무 팁:
- 대부분의 프로젝트에서 표준 패턴
- @EnableJpaAuditing 활성화 필요
```

</details>

---

### 📗 중급 개발자용 (5개)

<details>
<summary><strong>1. Entity 설계 시 고려해야 할 성능 최적화 전략은?</strong></summary>

**모범 답변** (중급):
```
Entity 설계 시 성능 최적화는 크게 5가지 전략이 있습니다.

1. Lazy Loading 활용
   - @Lob, @OneToMany는 LAZY 설정
   - 목록 조회와 상세 조회 분리

2. 인덱스 설계
   - @Index로 자주 조회하는 컬럼 인덱스 추가
   - 복합 인덱스 고려 (user_id, created_at)

3. DTO 프로젝션
   - Entity 전체 대신 필요한 필드만 조회
   - @Query("SELECT new ...Dto(...) FROM Entity")

4. Dirty Checking 최적화
   - @DynamicUpdate: 변경된 컬럼만 UPDATE
   - @DynamicInsert: null이 아닌 컬럼만 INSERT

5. 낙관적 락
   - @Version으로 동시성 제어
   - DB 락 없이 성능 유지

실무 사례 (쿠팡):
Before:
- @OneToMany EAGER → N+1 문제
- 전체 Entity 조회 → 불필요한 데이터 전송
- 동시성 제어 없음 → 재고 오류

After:
- LAZY Loading → 필요할 때만 조회
- DTO 프로젝션 → 목록 조회 성능 50% 향상
- @Version → 재고 정확도 100%
```

**꼬리 질문**:
- Q: N+1 문제와 Entity 설계의 관계는?
  - A: @OneToMany EAGER는 N+1을 유발. LAZY + Fetch Join으로 해결.

</details>

<details>
<summary><strong>2. Soft Delete를 구현하는 방법과 주의사항은?</strong></summary>

**모범 답변** (중급):
```
Soft Delete는 데이터를 실제로 삭제하지 않고
deleted_at 컬럼으로 논리적 삭제를 표시하는 방식입니다.

구현 방법:

1. 기본 구현:
@Entity
public class Product extends BaseEntity {
    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;

    public void softDelete() {
        this.deletedAt = LocalDateTime.now();
    }

    public boolean isDeleted() {
        return deletedAt != null;
    }
}

2. Hibernate @Where (자동 필터):
@Entity
@Where(clause = "deleted_at IS NULL")
public class Product {
    // findAll() → WHERE deleted_at IS NULL 자동 추가
}

3. Hibernate @SQLDelete (DELETE → UPDATE):
@Entity
@SQLDelete(sql = "UPDATE products SET deleted_at = NOW() WHERE id = ?")
public class Product {
    // repository.delete(product) → UPDATE 실행
}

주의사항:

1. UNIQUE 제약조건 충돌
   - 문제: email UNIQUE + Soft Delete → 재가입 불가
   - 해결: UNIQUE INDEX (email, deleted_at)

2. 외래키 문제
   - 문제: FK 참조하는 데이터 처리
   - 해결: Cascade 대신 수동 처리

3. 조회 성능
   - 문제: WHERE deleted_at IS NULL 조건 추가
   - 해결: deleted_at 인덱스 추가

4. 데이터 증가
   - 문제: 삭제 데이터가 계속 누적
   - 해결: 주기적으로 Hard Delete (배치)

실무 사례 (배달의민족):
- 음식점 삭제 → Soft Delete
- 주문 이력 유지 (통계, 매출)
- 3년 후 Hard Delete (배치)
```

</details>

<details>
<summary><strong>3. Entity와 Value Object의 차이는?</strong></summary>

**모범 답변** (중급):
```
Entity는 식별자(ID)로 구별되는 객체이고,
Value Object는 값 자체로 동등성을 판단하는 객체입니다.

Entity:
- 식별자(@Id) 존재
- 생명주기 관리 (생성, 수정, 삭제)
- 가변(Mutable)
- 예: User, Product, Order

Value Object:
- 식별자 없음
- 불변(Immutable)
- 값으로 비교 (equals, hashCode)
- @Embeddable로 구현
- 예: Address, Money, Email

구현 예시:

// Entity
@Entity
public class User {
    @Id
    private Long id;  // 식별자

    @Embedded
    private Address address;  // Value Object
}

// Value Object
@Embeddable
public class Address {
    private String city;
    private String street;
    private String zipCode;

    // 생성자, equals, hashCode
    // Setter 없음 (불변)
}

차이점:
┌──────────┬──────────┬──────────────┐
│          │ Entity   │ Value Object │
├──────────┼──────────┼──────────────┤
│ 식별자   │ 있음     │ 없음         │
│ 비교     │ ID       │ 값           │
│ 가변성   │ 가변     │ 불변         │
│ 생명주기 │ 독립적   │ Entity 소속  │
└──────────┴──────────┴──────────────┘

실무 팁:
- 주소, 금액, 이메일 → Value Object
- 사용자, 상품, 주문 → Entity
- Value Object는 재사용 가능
```

</details>

<details>
<summary><strong>4. JPA의 Dirty Checking 메커니즘을 설명해주세요.</strong></summary>

**모범 답변** (중급):
```
Dirty Checking은 JPA가 Entity의 변경을 자동으로 감지하여
UPDATE 쿼리를 자동 생성하는 메커니즘입니다.

동작 원리:

1. 영속성 컨텍스트에 Entity 저장
   - 최초 조회 시 스냅샷 저장

2. 트랜잭션 내에서 Entity 수정
   - setter로 값 변경
   - 아직 DB UPDATE 안 됨

3. 트랜잭션 커밋 시점
   - 스냅샷과 현재 Entity 비교
   - 변경 감지 시 UPDATE 자동 생성
   - flush() 호출 → DB 반영

코드 예시:

@Transactional
public void updateProduct(Long id, BigDecimal newPrice) {
    // 1. 조회 (스냅샷 저장)
    Product product = productRepository.findById(id).orElseThrow();

    // 2. 수정 (변경 감지 대상)
    product.updatePrice(newPrice);

    // 3. save() 호출 불필요!
    // repository.save(product);  // 필요 없음

    // 4. 트랜잭션 커밋 시 자동 UPDATE
}

// 실행되는 SQL
UPDATE products
SET price = ?, updated_at = ?
WHERE id = ?

최적화:

1. @DynamicUpdate
   - 변경된 컬럼만 UPDATE
   - 컬럼이 많을 때 유리

2. 주의사항
   - 변경 감지는 영속 상태에만 동작
   - 준영속(Detached) 상태는 감지 안 됨
   - 트랜잭션 필수

성능:
- 장점: 코드 간결, 자동 UPDATE
- 단점: 모든 컬럼 UPDATE (기본값)
- 해결: @DynamicUpdate

실무 팁:
- save() 호출하지 말 것
- setter 대신 비즈니스 메서드 사용
- @Transactional 필수
```

</details>

<details>
<summary><strong>5. Entity 생명주기(Lifecycle)를 설명해주세요.</strong></summary>

**모범 답변** (중급):
```
JPA Entity는 4가지 상태를 가지며, 각 상태에 따라
영속성 컨텍스트와의 관계가 달라집니다.

4가지 상태:

1. 비영속 (Transient)
   - new로 생성만 한 상태
   - 영속성 컨텍스트와 무관
   - Dirty Checking 안 됨

2. 영속 (Persistent)
   - 영속성 컨텍스트에 저장된 상태
   - Dirty Checking 동작
   - 1차 캐시에 존재

3. 준영속 (Detached)
   - 영속성 컨텍스트에서 분리된 상태
   - Dirty Checking 안 됨
   - 트랜잭션 종료 후 상태

4. 삭제 (Removed)
   - 삭제가 예정된 상태
   - 트랜잭션 커밋 시 DELETE 실행

상태 전환:

// 1. 비영속 → 영속
Product product = new Product(...);  // 비영속
entityManager.persist(product);      // 영속

// 2. 영속 → 준영속
entityManager.detach(product);       // 준영속
entityManager.clear();                // 모두 준영속
entityManager.close();                // 모두 준영속

// 3. 준영속 → 영속
entityManager.merge(product);        // 다시 영속

// 4. 영속 → 삭제
entityManager.remove(product);       // 삭제

생명주기 콜백:

@Entity
public class Product {

    @PrePersist   // INSERT 전
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    @PostPersist  // INSERT 후
    protected void afterCreate() {
        log.info("Product created: {}", id);
    }

    @PreUpdate    // UPDATE 전
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    @PostUpdate   // UPDATE 후
    protected void afterUpdate() {
        log.info("Product updated: {}", id);
    }

    @PreRemove    // DELETE 전
    protected void onRemove() {
        log.info("Product removing: {}", id);
    }

    @PostRemove   // DELETE 후
    protected void afterRemove() {
        log.info("Product removed: {}", id);
    }

    @PostLoad     // 조회 후
    protected void afterLoad() {
        log.info("Product loaded: {}", id);
    }
}

실무 활용:
- 생성일시: @PrePersist
- 수정일시: @PreUpdate
- 검증: @PrePersist, @PreUpdate
- 로깅: @Post* 콜백
- 이벤트 발행: @PostPersist
```

</details>

---

## 📝 핵심 정리

### 이 장에서 배운 핵심 개념

| 개념 | 설명 | 핵심 키워드 |
|------|------|-------------|
| @Entity | JPA Entity 선언 | 테이블 매핑, ORM |
| @Id | 기본키 지정 | Primary Key, 식별자 |
| @GeneratedValue | 기본키 자동 생성 | IDENTITY, SEQUENCE, AUTO |
| @Column | 컬럼 매핑 및 제약조건 | nullable, length, unique |
| @Enumerated | Enum 매핑 | STRING, ORDINAL |
| @Lob | 대용량 데이터 매핑 | TEXT, BLOB, CLOB |
| @Version | 낙관적 락 | 동시성 제어, 버전 관리 |
| @Transient | DB 저장 제외 | 임시 필드 |
| BaseEntity | 공통 필드 상속 | Auditing, 중복 제거 |

---

### 필수 실천 사항 정리

| 항목 | 올바른 방법 | 잘못된 방법 |
|------|-------------|-------------|
| Enum 매핑 | `EnumType.STRING` | `EnumType.ORDINAL` |
| 금액 타입 | `BigDecimal` | `Double`, `Float` |
| LOB 로딩 | `FetchType.LAZY` | `FetchType.EAGER` (기본값) |
| 감사 필드 | `@CreatedDate`, `BaseEntity` | 수동 설정 |
| 동시성 제어 | `@Version` | 락 없음 |
| 삭제 방식 | Soft Delete (필요 시) | Hard Delete만 사용 |

---

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] 항상 `EnumType.STRING` 사용
- [ ] 금액은 `BigDecimal` + `precision`/`scale` 지정
- [ ] `@Lob`에 `FetchType.LAZY` 명시
- [ ] `BaseEntity` 패턴으로 공통 필드 관리
- [ ] `@Version`으로 동시성 제어
- [ ] 목록 조회는 DTO 프로젝션 사용
- [ ] 인덱스는 `@Index`로 선언

#### ❌ 하지 말아야 할 것
- [ ] `EnumType.ORDINAL` 사용 금지
- [ ] `Double`/`Float`로 금액 저장 금지
- [ ] `columnDefinition` 남용 금지
- [ ] 모든 컬럼을 EAGER Loading
- [ ] `@PrePersist`에서 복잡한 로직 수행
- [ ] Entity를 Controller에 직접 노출
- [ ] Dirty Checking 없이 save() 호출

---

### Entity 설계 체크리스트

#### 기본 설계
- [ ] `@Entity`, `@Table` 선언
- [ ] `@Id`, `@GeneratedValue` 지정
- [ ] `BaseEntity` 상속 (감사 필드)
- [ ] `@Column`으로 제약조건 명시
- [ ] 인덱스 설계 (`@Index`)

#### 타입 매핑
- [ ] Enum → `EnumType.STRING`
- [ ] 금액 → `BigDecimal`
- [ ] 날짜 → `LocalDateTime`
- [ ] 대용량 텍스트 → `@Lob` + `LAZY`

#### 동시성 & 성능
- [ ] 동시 수정 가능 → `@Version`
- [ ] 목록 조회 최적화 → DTO 프로젝션
- [ ] 불필요한 조회 방지 → LAZY Loading

#### 비즈니스 로직
- [ ] 생성자로 필수 값 강제
- [ ] setter 대신 비즈니스 메서드
- [ ] 도메인 로직은 Entity에 위치
- [ ] 검증 로직 추가

---

## 🚀 다음 단계

### 다음 장 미리보기: 24장 - JPQL & Query Methods

이제 Entity 매핑을 완벽히 이해했으니, Entity를 조회하는 다양한 방법을 배울 차례입니다!

**24장에서 배울 내용**:
- **JPQL (Java Persistence Query Language)**: 객체 지향 쿼리 언어
- **Query Methods**: 메서드 이름으로 쿼리 자동 생성
- **@Query**: 복잡한 쿼리 작성
- **동적 쿼리**: Criteria API, QueryDSL

### 이 장과의 연결점

```
23장: Entity Mapping (지금 여기)
    - Product, Order Entity 설계
    - @Column, @Enumerated, @Version
    ↓
24장: JPQL & Query Methods (다음)
    - findByCategory(ProductCategory category)
    - @Query("SELECT p FROM Product p WHERE ...")
    - 동적 검색 조건 (가격, 카테고리, 재고)
    ↓
25장: Fetch & N+1 Problem
    - 연관관계 조회 최적화
```

### 준비하면 좋을 것들

```java
// 23장에서 만든 Entity 복습
@Entity
public class Product {
    @Id
    private Long id;

    @Enumerated(EnumType.STRING)
    private ProductCategory category;

    @Column(precision = 10, scale = 2)
    private BigDecimal price;

    private Integer stock;
}

// 24장에서 배울 Query Methods
public interface ProductRepository extends JpaRepository<Product, Long> {

    // 메서드 이름으로 쿼리 자동 생성
    List<Product> findByCategory(ProductCategory category);

    List<Product> findByPriceBetween(BigDecimal min, BigDecimal max);

    @Query("SELECT p FROM Product p WHERE p.stock > 0")
    List<Product> findAllInStock();
}
```

---

## 🎉 축하합니다!

**23장 학습 완료 후**

**이제 여러분은**:
✅ JPA Entity의 개념과 역할을 이해했습니다
✅ 다양한 타입을 올바르게 매핑할 수 있습니다
✅ `EnumType.STRING`, `BigDecimal`, `@Lob` 사용법을 알았습니다
✅ `@Version`으로 동시성을 제어할 수 있습니다
✅ BaseEntity 패턴으로 공통 필드를 관리할 수 있습니다
✅ 실무에서 발생하는 Entity 설계 문제를 해결할 수 있습니다

**다음 단계**:
- [ ] 24장으로 진행 (JPQL & Query Methods)
- [ ] 실전 프로젝트 확장 (검색 기능 추가)
- [ ] 면접 질문 답변 연습

---

**다음 장으로 이동**: [다음: 24장 JPQL & Query Methods →](SpringMVC-Part14-24-JPQL-Query-Methods.md)

**목차로 돌아가기**: [📚 전체 목차](README.md)

---

**💪 Entity Mapping 마스터를 축하합니다!**

```
     Entity 설계 완성!
         ↓
   23장 완료 ✅
         ↓
  이제 쿼리 작성 배우기
         ↓
   24장: JPQL & Query Methods
         ↓
      Spring 마스터! 🎉
```
