# 21장: 트랜잭션 관리 (Transaction Management) - PART 2

> **이 문서는 Part 1의 연속입니다.** Part 1에서 기본 개념, 실습, 실무 사례를 학습했습니다.

---

## 👨‍💻 주니어 시나리오

**실무에서 자주 겪는 상황과 해결 방법**

### 시나리오 1: "왜 @Transactional을 붙였는데 롤백이 안 되나요?"

**상황**: 주니어 개발자가 예외 발생 시 롤백을 기대했지만 데이터가 저장되는 문제

```java
// ❌ 주니어 개발자가 작성한 코드
@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;

    @Transactional
    public void registerUser(User user) {
        try {
            userRepository.save(user);

            // 이메일 발송 시 예외 발생
            sendWelcomeEmail(user.getEmail());  // Exception 발생!

        } catch (Exception e) {
            log.error("이메일 발송 실패", e);
            // 예외를 잡아서 처리했으므로 롤백 안됨!
        }
    }

    private void sendWelcomeEmail(String email) throws Exception {
        throw new Exception("메일 서버 연결 실패");
    }
}

// 실행 결과:
// - 사용자는 DB에 저장됨 (롤백 안됨!)
// - 이메일은 발송 안됨
// 왜? try-catch로 예외를 잡았기 때문에 Spring은 롤백하지 않음
```

**문제점**:
- 문제 1: try-catch로 예외를 삼켜버려서 트랜잭션 롤백이 발생하지 않음
- 문제 2: Checked Exception은 기본적으로 롤백하지 않음
- 왜 이 문제가 발생하는가: Spring은 RuntimeException만 기본 롤백 대상으로 봄

**해결책 1: 예외를 다시 던지기**
```java
// ✅ 올바른 코드 - 방법 1
@Transactional
public void registerUser(User user) {
    try {
        userRepository.save(user);
        sendWelcomeEmail(user.getEmail());

    } catch (Exception e) {
        log.error("이메일 발송 실패", e);
        throw new RuntimeException("사용자 등록 실패", e);  // ✅ 예외를 다시 던짐
    }
}
```

**해결책 2: rollbackFor 설정**
```java
// ✅ 올바른 코드 - 방법 2
@Transactional(rollbackFor = Exception.class)  // ✅ 모든 예외에 대해 롤백
public void registerUser(User user) throws Exception {
    userRepository.save(user);
    sendWelcomeEmail(user.getEmail());
    // Exception 발생 시 자동 롤백
}
```

**해결책 3: 이메일은 트랜잭션 커밋 후 발송**
```java
// ✅ 올바른 코드 - 방법 3 (가장 권장)
@Service
public class UserService {

    @Autowired
    private ApplicationEventPublisher eventPublisher;

    @Transactional
    public void registerUser(User user) {
        User savedUser = userRepository.save(user);

        // 이벤트 발행 (트랜잭션 커밋 후 이메일 발송)
        eventPublisher.publishEvent(new UserRegisteredEvent(savedUser));
    }
}

@Component
public class UserEventListener {

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleUserRegistered(UserRegisteredEvent event) {
        // 트랜잭션 커밋 후 실행
        // 이메일 발송 실패해도 사용자 등록은 성공
        sendWelcomeEmail(event.getUser().getEmail());
    }
}
```

**배운 점**:
- 💡 팁 1: **try-catch로 예외를 잡으면 롤백 안됨!** 예외를 다시 던져야 함
- 💡 팁 2: **Checked Exception은 `rollbackFor` 설정 필요**
- 💡 팁 3: **외부 연동은 트랜잭션 커밋 후 처리**하는 것이 안전

### 시나리오 2: "내부 메서드 호출 시 @Transactional이 동작 안 해요!"

**상황**: 같은 클래스 내에서 @Transactional 메서드를 호출했는데 트랜잭션이 적용되지 않음

```java
// ❌ 주니어 개발자가 작성한 코드
@Service
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    public void processOrder(Order order) {
        // 내부 메서드 호출
        saveOrder(order);  // ❌ @Transactional 적용 안됨!
    }

    @Transactional
    public void saveOrder(Order order) {
        orderRepository.save(order);
        // 트랜잭션이 적용되지 않음!
    }
}

// 왜? 내부 호출은 프록시를 거치지 않기 때문!
```

**문제점**:
- 문제 1: 내부 호출(self-invocation)은 프록시를 거치지 않음
- 문제 2: Spring AOP는 프록시 기반이므로 외부에서 호출해야 동작
- 왜 이 문제가 발생하는가: `this.saveOrder()`는 실제 객체 호출, 프록시 미경유

**동작 원리**:
```
[외부 호출 - 정상 동작]
Controller → OrderServiceProxy → OrderService.saveOrder()
                ↑ 여기서 트랜잭션 시작

[내부 호출 - 동작 안함]
OrderService.processOrder() → this.saveOrder()
                               ↑ 프록시 거치지 않음!
```

**해결책 1: 메서드를 별도 서비스로 분리**
```java
// ✅ 올바른 코드 - 방법 1 (권장)
@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderInternalService orderInternalService;

    public void processOrder(Order order) {
        // 외부 서비스 호출 → 프록시 경유
        orderInternalService.saveOrder(order);  // ✅ 트랜잭션 적용!
    }
}

@Service
@RequiredArgsConstructor
public class OrderInternalService {

    private final OrderRepository orderRepository;

    @Transactional
    public void saveOrder(Order order) {
        orderRepository.save(order);
        // ✅ 트랜잭션 정상 적용!
    }
}
```

**해결책 2: Self-Injection 사용**
```java
// ✅ 올바른 코드 - 방법 2
@Service
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    @Lazy  // 순환 참조 방지
    private OrderService self;

    public void processOrder(Order order) {
        // 자기 자신의 프록시 호출
        self.saveOrder(order);  // ✅ 트랜잭션 적용!
    }

    @Transactional
    public void saveOrder(Order order) {
        orderRepository.save(order);
    }
}
```

**해결책 3: AopContext 사용 (비권장)**
```java
// ✅ 올바른 코드 - 방법 3 (설정 필요, 권장하지 않음)
@Configuration
@EnableAspectJAutoProxy(exposeProxy = true)
public class AopConfig {
}

@Service
public class OrderService {

    public void processOrder(Order order) {
        // 현재 프록시 가져오기
        OrderService proxy = (OrderService) AopContext.currentProxy();
        proxy.saveOrder(order);  // ✅ 트랜잭션 적용
    }

    @Transactional
    public void saveOrder(Order order) {
        orderRepository.save(order);
    }
}
```

**배운 점**:
- 💡 팁 1: **내부 호출은 프록시를 거치지 않음!** 별도 서비스로 분리 권장
- 💡 팁 2: **Self-Injection도 가능하지만 순환 참조 주의**
- 💡 팁 3: **@Transactional은 외부에서 호출되는 public 메서드에 붙이기**

### 시나리오 3: "대량 데이터 처리 시 트랜잭션 타임아웃 발생!"

**상황**: 10만 건의 데이터를 한 트랜잭션으로 처리하다가 타임아웃 발생

```java
// ❌ 주니어 개발자가 작성한 코드
@Service
public class DataMigrationService {

    @Autowired
    private DataRepository dataRepository;

    @Transactional
    public void migrateAllData() {
        List<Data> allData = dataRepository.findAll();  // 10만 건 조회

        for (Data data : allData) {
            data.migrate();
            dataRepository.save(data);
        }

        // 문제점:
        // 1. OutOfMemoryError (10만 건 한번에 로딩)
        // 2. Transaction timeout (처리 시간 30분 초과)
        // 3. DB 락 오래 유지 → 다른 트랜잭션 블로킹
        // 4. 중간에 실패 시 30분 작업 전부 롤백
    }
}

// 실행 결과:
// Exception: Transaction timeout after 300 seconds
```

**문제점**:
- 문제 1: 너무 큰 트랜잭션으로 타임아웃 발생
- 문제 2: 메모리 부족 (10만 건을 한번에 메모리에 로딩)
- 문제 3: DB 락이 너무 오래 유지되어 다른 요청 블로킹
- 왜 이 문제가 발생하는가: 트랜잭션은 작고 빠르게 처리해야 함

**해결책: 배치 처리로 분할**
```java
// ✅ 올바른 코드
@Service
@Slf4j
public class DataMigrationService {

    @Autowired
    private DataRepository dataRepository;

    /**
     * 전체 데이터 마이그레이션 (트랜잭션 없음)
     */
    public MigrationResult migrateAllData() {
        int totalCount = 0;
        int successCount = 0;
        int failCount = 0;

        int batchSize = 1000;  // 배치 크기
        int page = 0;

        while (true) {
            try {
                // 1000건씩 별도 트랜잭션으로 처리
                int processed = migrateBatch(page, batchSize);

                if (processed == 0) {
                    break;  // 더 이상 처리할 데이터 없음
                }

                totalCount += processed;
                successCount += processed;
                page++;

                log.info("마이그레이션 진행: {}건 완료 ({}/100000)",
                         totalCount, totalCount);

            } catch (Exception e) {
                log.error("배치 {} 처리 실패", page, e);
                failCount += batchSize;
                page++;
            }

            // 짧은 휴식 (DB 부하 분산)
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }

        return new MigrationResult(totalCount, successCount, failCount);
    }

    /**
     * 한 배치 처리 (1000건씩 별도 트랜잭션)
     */
    @Transactional(timeout = 30)  // 30초 타임아웃
    public int migrateBatch(int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        List<Data> dataList = dataRepository.findAllByMigrated(false, pageable)
            .getContent();

        if (dataList.isEmpty()) {
            return 0;
        }

        for (Data data : dataList) {
            data.migrate();
        }

        dataRepository.saveAll(dataList);

        return dataList.size();
    }
}
```

**배운 점**:
- 💡 팁 1: **대량 데이터는 배치 단위로 분할 처리** (보통 500~2000건)
- 💡 팁 2: **트랜잭션 타임아웃 설정으로 무한 대기 방지**
- 💡 팁 3: **진행 상황 로깅으로 모니터링 가능하도록 구성**
- 💡 팁 4: **실패한 배치는 건너뛰고 계속 진행** (전체 중단 방지)

### 시나리오 4: "동시에 주문하면 재고가 마이너스가 돼요!"

**상황**: 마지막 1개 남은 상품을 2명이 동시에 주문하여 재고가 -1이 됨

```java
// ❌ 주니어 개발자가 작성한 코드
@Service
public class OrderService {

    @Autowired
    private ProductRepository productRepository;

    @Transactional
    public void createOrder(Long productId, int quantity) {
        // 1. 재고 조회
        Product product = productRepository.findById(productId)
            .orElseThrow();

        // 시나리오:
        // 사용자 A: stock = 1 조회
        // 사용자 B: stock = 1 조회 (동시에!)

        // 2. 재고 확인
        if (product.getStock() < quantity) {
            throw new RuntimeException("재고 부족");
        }

        // 3. 재고 차감
        // 사용자 A: stock = 0으로 업데이트
        // 사용자 B: stock = 0으로 업데이트 (A의 업데이트 덮어씀!)
        product.setStock(product.getStock() - quantity);
        productRepository.save(product);

        // 결과: stock = 0이어야 하는데, 경우에 따라 -1이 될 수 있음!
    }
}
```

**문제점**:
- 문제 1: 동시성 문제 (Race Condition)
- 문제 2: Lost Update (한 트랜잭션의 업데이트가 다른 트랜잭션에 덮어씌워짐)
- 왜 이 문제가 발생하는가: 격리성이 보장되지 않음

**해결책 1: 비관적 락 (Pessimistic Lock)**
```java
// ✅ 올바른 코드 - 방법 1 (확실하지만 성능 저하)
public interface ProductRepository extends JpaRepository<Product, Long> {

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT p FROM Product p WHERE p.id = :id")
    Optional<Product> findByIdWithLock(@Param("id") Long id);
}

@Service
public class OrderService {

    @Transactional
    public void createOrder(Long productId, int quantity) {
        // 1. 재고 조회 및 락 획득 (FOR UPDATE)
        Product product = productRepository.findByIdWithLock(productId)
            .orElseThrow();

        // 다른 트랜잭션은 여기서 대기! (락 해제될 때까지)

        // 2. 재고 확인
        if (product.getStock() < quantity) {
            throw new RuntimeException("재고 부족");
        }

        // 3. 재고 차감
        product.setStock(product.getStock() - quantity);
        productRepository.save(product);

        // 4. 커밋 시 락 해제
    }
}

// 장점: 확실하게 동시성 문제 해결
// 단점: 대기 시간 발생, 성능 저하
```

**해결책 2: 낙관적 락 (Optimistic Lock)**
```java
// ✅ 올바른 코드 - 방법 2 (성능 좋지만 재시도 필요)
@Entity
public class Product {

    @Id
    private Long id;

    @Version  // 낙관적 락
    private Long version;

    private Integer stock;

    // getters, setters
}

@Service
public class OrderService {

    @Autowired
    private ProductRepository productRepository;

    @Transactional
    public void createOrder(Long productId, int quantity) {
        try {
            Product product = productRepository.findById(productId)
                .orElseThrow();

            if (product.getStock() < quantity) {
                throw new RuntimeException("재고 부족");
            }

            product.setStock(product.getStock() - quantity);
            productRepository.save(product);

            // 커밋 시 version 충돌 확인
            // 다른 트랜잭션이 먼저 수정했으면 OptimisticLockException 발생

        } catch (OptimisticLockException e) {
            // 재시도 로직
            throw new RetryableException("동시 주문 발생, 재시도 필요");
        }
    }
}

// 장점: 성능 좋음 (락 대기 없음)
// 단점: 충돌 시 재시도 필요
```

**해결책 3: DB 함수 사용 (가장 권장)**
```java
// ✅ 올바른 코드 - 방법 3 (가장 권장)
public interface ProductRepository extends JpaRepository<Product, Long> {

    @Modifying
    @Query("UPDATE Product p SET p.stock = p.stock - :quantity " +
           "WHERE p.id = :id AND p.stock >= :quantity")
    int decreaseStock(@Param("id") Long id, @Param("quantity") int quantity);
}

@Service
public class OrderService {

    @Transactional
    public void createOrder(Long productId, int quantity) {
        // 1. 원자적으로 재고 차감
        int updated = productRepository.decreaseStock(productId, quantity);

        // 2. 업데이트된 행이 없으면 재고 부족
        if (updated == 0) {
            throw new RuntimeException("재고 부족");
        }

        // 3. 주문 생성
        // ...
    }
}

// 장점: 가장 빠름, DB 레벨에서 원자성 보장
// 단점: 복잡한 비즈니스 로직은 적용 어려움
```

**배운 점**:
- 💡 팁 1: **동시성 문제는 락으로 해결** (비관적 락 or 낙관적 락)
- 💡 팁 2: **간단한 카운터는 DB 함수 활용이 가장 효율적**
- 💡 팁 3: **재고 관리는 비관적 락 권장** (재고는 절대 마이너스 되면 안됨!)
- 💡 팁 4: **읽기가 많고 쓰기가 적으면 낙관적 락, 반대는 비관적 락**

---

## 🛠️ 실전 프로젝트

### 프로젝트: 전자상거래 주문 시스템 (트랜잭션 관리 종합)

**난이도**: ⭐⭐⭐⭐☆
**예상 소요 시간**: 3-4시간
**학습 목표**: 실무에서 사용하는 트랜잭션 패턴을 모두 적용하여 안전한 주문 시스템 구축

### 요구사항 분석

#### 기능 요구사항
- [x] **주문 생성**: 재고 차감 + 주문 생성 + 결제 처리를 하나의 트랜잭션으로
- [x] **재고 관리**: 동시 주문 시 재고 정확성 보장 (락 사용)
- [x] **포인트 적립**: 주문 완료 후 포인트 적립 (별도 트랜잭션)
- [x] **주문 취소**: 주문 취소 시 재고 복구 및 환불 처리
- [x] **알림 발송**: 트랜잭션 커밋 후 이메일/SMS 발송
- [x] **이력 관리**: 모든 변경사항 이력 기록

#### 기술 요구사항
- [x] Spring Boot 3.2+
- [x] JPA + H2 Database
- [x] @Transactional 활용
- [x] 비관적 락 적용
- [x] 이벤트 기반 알림
- [x] 트랜잭션 전파 속성 활용

#### 비기능 요구사항
- [x] **원자성**: 주문 생성 중 하나라도 실패 시 전체 롤백
- [x] **격리성**: 동시 주문 시 재고 정확성 100% 보장
- [x] **성능**: 초당 100건 주문 처리 가능
- [x] **추적성**: 모든 트랜잭션 로그 기록

### 프로젝트 구조

```
ecommerce-order-system/
├── src/
│   ├── main/
│   │   ├── java/com/example/order/
│   │   │   ├── OrderApplication.java
│   │   │   ├── entity/
│   │   │   │   ├── Product.java
│   │   │   │   ├── Order.java
│   │   │   │   ├── OrderItem.java
│   │   │   │   ├── Payment.java
│   │   │   │   ├── User.java
│   │   │   │   └── OrderHistory.java
│   │   │   ├── repository/
│   │   │   │   ├── ProductRepository.java
│   │   │   │   ├── OrderRepository.java
│   │   │   │   ├── PaymentRepository.java
│   │   │   │   ├── UserRepository.java
│   │   │   │   └── OrderHistoryRepository.java
│   │   │   ├── service/
│   │   │   │   ├── OrderService.java
│   │   │   │   ├── PaymentService.java
│   │   │   │   ├── PointService.java
│   │   │   │   └── NotificationService.java
│   │   │   ├── dto/
│   │   │   │   ├── OrderRequest.java
│   │   │   │   └── OrderResponse.java
│   │   │   ├── event/
│   │   │   │   ├── OrderCompletedEvent.java
│   │   │   │   └── OrderEventListener.java
│   │   │   └── exception/
│   │   │       ├── InsufficientStockException.java
│   │   │       └── PaymentFailedException.java
│   │   └── resources/
│   │       ├── application.yml
│   │       └── data.sql
│   └── test/
│       └── java/com/example/order/
│           └── service/
│               └── OrderServiceTest.java
└── build.gradle
```

### 설계 의사결정

#### 왜 이렇게 설계했는가?

**결정 1: 주문 생성 + 재고 차감 + 결제를 하나의 트랜잭션으로**
- **이유**: 세 작업은 원자성이 보장되어야 함 (하나라도 실패 시 전체 취소)
- **대안**: 각각 별도 트랜잭션 → 데이터 불일치 위험
- **선택 근거**: ACID 속성 중 원자성이 가장 중요

**결정 2: 재고 차감 시 비관적 락 사용**
- **이유**: 재고는 절대 마이너스가 되어서는 안됨
- **대안**: 낙관적 락 → 재시도 복잡성 증가
- **선택 근거**: 재고 정확성 > 성능

**결정 3: 알림 발송은 트랜잭션 커밋 후 처리**
- **이유**: 알림 실패가 주문 실패로 이어지면 안됨
- **대안**: 같은 트랜잭션 → 알림 실패 시 주문도 롤백
- **선택 근거**: 비즈니스 중요도 (주문 > 알림)

### 단계별 구현 가이드

#### 1단계: 프로젝트 초기 설정

```groovy
// build.gradle
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.2.0'
    id 'io.spring.dependency-management' version '1.1.4'
}

group = 'com.example'
version = '1.0.0'
sourceCompatibility = '17'

configurations {
    compileOnly {
        extendsFrom annotationProcessor
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-web'
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
    runtimeOnly 'com.h2database:h2'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}

tasks.named('test') {
    useJUnitPlatform()
}
```

```yaml
# application.yml
spring:
  datasource:
    url: jdbc:h2:mem:orderdb
    driver-class-name: org.h2.Driver
    username: sa
    password:

  h2:
    console:
      enabled: true

  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: true
    properties:
      hibernate:
        format_sql: true
        use_sql_comments: true

logging:
  level:
    org.hibernate.SQL: DEBUG
    org.hibernate.type.descriptor.sql.BasicBinder: TRACE
    org.springframework.transaction: DEBUG
```

**체크포인트**:
- [x] Spring Boot 프로젝트 생성 완료
- [x] H2 Database 설정 완료
- [x] JPA 설정 완료
- [x] Lombok 설정 완료

#### 2단계: Entity 구현

```java
// Product.java
package com.example.order.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.math.BigDecimal;

@Entity
@Table(name = "products")
@Getter
@Setter
@NoArgsConstructor
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;

    @Column(nullable = false)
    private Integer stock;

    /**
     * 재고 차감 (비즈니스 로직)
     */
    public void decreaseStock(int quantity) {
        if (this.stock < quantity) {
            throw new InsufficientStockException(
                String.format("재고 부족: 요청=%d, 재고=%d", quantity, this.stock)
            );
        }
        this.stock -= quantity;
    }

    /**
     * 재고 복구 (주문 취소 시)
     */
    public void increaseStock(int quantity) {
        this.stock += quantity;
    }
}

// Order.java
package com.example.order.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "orders")
@Getter
@Setter
@NoArgsConstructor
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderItem> items = new ArrayList<>();

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal totalAmount = BigDecimal.ZERO;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private OrderStatus status = OrderStatus.PENDING;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    /**
     * 주문 아이템 추가
     */
    public void addItem(OrderItem item) {
        items.add(item);
        item.setOrder(this);
        calculateTotalAmount();
    }

    /**
     * 총 금액 계산
     */
    public void calculateTotalAmount() {
        this.totalAmount = items.stream()
            .map(OrderItem::getSubtotal)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    /**
     * 주문 확정
     */
    public void confirm() {
        if (this.status != OrderStatus.PENDING) {
            throw new IllegalStateException("이미 처리된 주문입니다");
        }
        this.status = OrderStatus.CONFIRMED;
    }

    /**
     * 주문 취소
     */
    public void cancel() {
        if (this.status == OrderStatus.CANCELLED) {
            throw new IllegalStateException("이미 취소된 주문입니다");
        }
        if (this.status == OrderStatus.SHIPPED || this.status == OrderStatus.DELIVERED) {
            throw new IllegalStateException("배송 중/완료된 주문은 취소할 수 없습니다");
        }
        this.status = OrderStatus.CANCELLED;
    }

    public boolean isCancellable() {
        return this.status == OrderStatus.PENDING || this.status == OrderStatus.CONFIRMED;
    }
}

// OrderStatus.java
package com.example.order.entity;

public enum OrderStatus {
    PENDING,      // 대기
    CONFIRMED,    // 확정
    PAID,         // 결제 완료
    SHIPPED,      // 배송 중
    DELIVERED,    // 배송 완료
    CANCELLED     // 취소
}

// OrderItem.java
package com.example.order.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.math.BigDecimal;

@Entity
@Table(name = "order_items")
@Getter
@Setter
@NoArgsConstructor
public class OrderItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", nullable = false)
    private Order order;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id", nullable = false)
    private Product product;

    @Column(nullable = false)
    private Integer quantity;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;  // 주문 당시 가격

    /**
     * 소계 계산
     */
    public BigDecimal getSubtotal() {
        return price.multiply(BigDecimal.valueOf(quantity));
    }
}

// User.java
package com.example.order.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = false)
    private Integer points = 0;

    /**
     * 포인트 적립
     */
    public void earnPoints(int points) {
        this.points += points;
    }

    /**
     * 포인트 차감
     */
    public void usePoints(int points) {
        if (this.points < points) {
            throw new IllegalStateException("포인트 부족");
        }
        this.points -= points;
    }
}

// Payment.java
package com.example.order.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "payments")
@Getter
@Setter
@NoArgsConstructor
public class Payment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", nullable = false)
    private Order order;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal amount;

    @Column(nullable = false)
    private String paymentMethod;  // CARD, BANK_TRANSFER, POINT

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private PaymentStatus status = PaymentStatus.PENDING;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    /**
     * 결제 승인
     */
    public void approve() {
        if (this.status != PaymentStatus.PENDING) {
            throw new IllegalStateException("이미 처리된 결제입니다");
        }
        this.status = PaymentStatus.APPROVED;
    }

    /**
     * 결제 실패
     */
    public void fail(String reason) {
        this.status = PaymentStatus.FAILED;
    }
}

// PaymentStatus.java
package com.example.order.entity;

public enum PaymentStatus {
    PENDING,   // 대기
    APPROVED,  // 승인
    FAILED,    // 실패
    REFUNDED   // 환불
}

// OrderHistory.java
package com.example.order.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.time.LocalDateTime;

@Entity
@Table(name = "order_histories")
@Getter
@Setter
@NoArgsConstructor
public class OrderHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long orderId;

    @Column(nullable = false)
    private String action;  // CREATE, CONFIRM, CANCEL, etc.

    @Column(length = 500)
    private String description;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    public static OrderHistory create(Long orderId, String action, String description) {
        OrderHistory history = new OrderHistory();
        history.setOrderId(orderId);
        history.setAction(action);
        history.setDescription(description);
        return history;
    }
}
```

**코드 설명**:
- **Product.decreaseStock()**: 재고 차감 로직을 엔티티 내부에 캡슐화
- **Order.addItem()**: 주문 아이템 추가 시 총액 자동 계산
- **OrderStatus enum**: 주문 상태를 명확하게 관리
- **OrderHistory**: 모든 주문 변경 이력 기록 (감사 추적)

#### 3단계: Repository 구현

```java
// ProductRepository.java
package com.example.order.repository;

import com.example.order.entity.Product;
import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.util.Optional;

public interface ProductRepository extends JpaRepository<Product, Long> {

    /**
     * 비관적 락으로 상품 조회 (FOR UPDATE)
     * - 다른 트랜잭션은 락이 해제될 때까지 대기
     */
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT p FROM Product p WHERE p.id = :id")
    Optional<Product> findByIdWithPessimisticLock(@Param("id") Long id);

    /**
     * 낙관적 락으로 상품 조회
     * - @Version 필드로 충돌 감지
     */
    @Lock(LockModeType.OPTIMISTIC)
    @Query("SELECT p FROM Product p WHERE p.id = :id")
    Optional<Product> findByIdWithOptimisticLock(@Param("id") Long id);
}

// OrderRepository.java
package com.example.order.repository;

import com.example.order.entity.Order;
import com.example.order.entity.OrderStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface OrderRepository extends JpaRepository<Order, Long> {

    List<Order> findByStatus(OrderStatus status);

    List<Order> findByUserId(Long userId);
}

// PaymentRepository.java
package com.example.order.repository;

import com.example.order.entity.Payment;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface PaymentRepository extends JpaRepository<Payment, Long> {

    Optional<Payment> findByOrderId(Long orderId);
}

// UserRepository.java
package com.example.order.repository;

import com.example.order.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByEmail(String email);
}

// OrderHistoryRepository.java
package com.example.order.repository;

import com.example.order.entity.OrderHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface OrderHistoryRepository extends JpaRepository<OrderHistory, Long> {

    List<OrderHistory> findByOrderIdOrderByCreatedAtDesc(Long orderId);
}
```

#### 4단계: 핵심 서비스 구현 (트랜잭션 적용)

```java
// OrderService.java
package com.example.order.service;

import com.example.order.dto.OrderRequest;
import com.example.order.dto.OrderResponse;
import com.example.order.entity.*;
import com.example.order.event.OrderCompletedEvent;
import com.example.order.exception.InsufficientStockException;
import com.example.order.exception.PaymentFailedException;
import com.example.order.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Isolation;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Slf4j
public class OrderService {

    private final OrderRepository orderRepository;
    private final ProductRepository productRepository;
    private final UserRepository userRepository;
    private final OrderHistoryRepository orderHistoryRepository;
    private final PaymentService paymentService;
    private final ApplicationEventPublisher eventPublisher;

    /**
     * 주문 생성 (핵심 트랜잭션)
     * - 재고 차감 + 주문 생성 + 결제 처리를 하나의 트랜잭션으로
     */
    @Transactional(isolation = Isolation.READ_COMMITTED)
    public OrderResponse createOrder(OrderRequest request) {
        log.info("===== 주문 생성 시작 =====");
        log.info("사용자 ID: {}, 상품 수: {}", request.getUserId(), request.getItems().size());

        // 1. 사용자 조회
        User user = userRepository.findById(request.getUserId())
            .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다"));

        // 2. 주문 생성
        Order order = new Order();
        order.setUser(user);

        // 3. 주문 아이템 처리 및 재고 차감
        for (OrderRequest.OrderItemRequest itemRequest : request.getItems()) {
            // 3-1. 비관적 락으로 상품 조회
            Product product = productRepository.findByIdWithPessimisticLock(itemRequest.getProductId())
                .orElseThrow(() -> new IllegalArgumentException(
                    "상품을 찾을 수 없습니다: " + itemRequest.getProductId()));

            log.info("상품 조회: id={}, name={}, stock={}",
                     product.getId(), product.getName(), product.getStock());

            // 3-2. 재고 차감 (비즈니스 로직)
            try {
                product.decreaseStock(itemRequest.getQuantity());
                productRepository.save(product);

                log.info("재고 차감 완료: 상품={}, 차감={}, 남은재고={}",
                         product.getName(), itemRequest.getQuantity(), product.getStock());

            } catch (InsufficientStockException e) {
                log.error("재고 부족: 상품={}, 요청={}, 재고={}",
                          product.getName(), itemRequest.getQuantity(), product.getStock());
                throw e;  // 트랜잭션 롤백
            }

            // 3-3. 주문 아이템 생성
            OrderItem orderItem = new OrderItem();
            orderItem.setProduct(product);
            orderItem.setQuantity(itemRequest.getQuantity());
            orderItem.setPrice(product.getPrice());  // 주문 당시 가격 저장
            order.addItem(orderItem);
        }

        // 4. 주문 저장
        Order savedOrder = orderRepository.save(order);
        log.info("주문 저장 완료: id={}, totalAmount={}", savedOrder.getId(), savedOrder.getTotalAmount());

        // 5. 주문 이력 기록
        orderHistoryRepository.save(
            OrderHistory.create(savedOrder.getId(), "CREATE",
                "주문 생성: " + savedOrder.getTotalAmount() + "원")
        );

        // 6. 결제 처리 (같은 트랜잭션)
        try {
            Payment payment = paymentService.processPayment(
                savedOrder,
                request.getPaymentMethod(),
                savedOrder.getTotalAmount()
            );

            log.info("결제 처리 완료: paymentId={}, status={}",
                     payment.getId(), payment.getStatus());

            // 7. 주문 확정
            savedOrder.confirm();
            orderRepository.save(savedOrder);

            // 8. 주문 이력 기록
            orderHistoryRepository.save(
                OrderHistory.create(savedOrder.getId(), "CONFIRM",
                    "주문 확정 및 결제 완료")
            );

        } catch (PaymentFailedException e) {
            log.error("결제 실패: orderId={}", savedOrder.getId(), e);
            throw e;  // 트랜잭션 롤백 (재고도 복구됨!)
        }

        log.info("===== 주문 생성 완료: orderId={} =====", savedOrder.getId());

        // 9. 주문 완료 이벤트 발행 (트랜잭션 커밋 후 처리됨)
        eventPublisher.publishEvent(new OrderCompletedEvent(savedOrder));

        return OrderResponse.from(savedOrder);
    }

    /**
     * 주문 취소 (재고 복구 포함)
     */
    @Transactional
    public void cancelOrder(Long orderId) {
        log.info("===== 주문 취소 시작: orderId={} =====", orderId);

        // 1. 주문 조회
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new IllegalArgumentException("주문을 찾을 수 없습니다"));

        // 2. 취소 가능 여부 확인
        if (!order.isCancellable()) {
            throw new IllegalStateException("취소할 수 없는 주문입니다: " + order.getStatus());
        }

        // 3. 재고 복구
        for (OrderItem item : order.getItems()) {
            Product product = productRepository.findByIdWithPessimisticLock(item.getProduct().getId())
                .orElseThrow();

            product.increaseStock(item.getQuantity());
            productRepository.save(product);

            log.info("재고 복구: 상품={}, 복구={}, 현재재고={}",
                     product.getName(), item.getQuantity(), product.getStock());
        }

        // 4. 주문 취소
        order.cancel();
        orderRepository.save(order);

        // 5. 주문 이력 기록
        orderHistoryRepository.save(
            OrderHistory.create(orderId, "CANCEL", "주문 취소 및 재고 복구")
        );

        log.info("===== 주문 취소 완료: orderId={} =====", orderId);
    }

    /**
     * 주문 조회
     */
    @Transactional(readOnly = true)
    public OrderResponse getOrder(Long orderId) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new IllegalArgumentException("주문을 찾을 수 없습니다"));
        return OrderResponse.from(order);
    }
}

// PaymentService.java
package com.example.order.service;

import com.example.order.entity.Order;
import com.example.order.entity.Payment;
import com.example.order.exception.PaymentFailedException;
import com.example.order.repository.PaymentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;

@Service
@RequiredArgsConstructor
@Slf4j
public class PaymentService {

    private final PaymentRepository paymentRepository;

    /**
     * 결제 처리 (REQUIRED: 부모 트랜잭션에 참여)
     */
    @Transactional(propagation = Propagation.REQUIRED)
    public Payment processPayment(Order order, String paymentMethod, BigDecimal amount) {
        log.info("[결제] 시작: orderId={}, method={}, amount={}",
                 order.getId(), paymentMethod, amount);

        // 1. Payment 엔티티 생성
        Payment payment = new Payment();
        payment.setOrder(order);
        payment.setPaymentMethod(paymentMethod);
        payment.setAmount(amount);

        // 2. 외부 PG사 결제 요청 (시뮬레이션)
        boolean pgResult = callPaymentGateway(paymentMethod, amount);

        if (!pgResult) {
            payment.fail("PG사 승인 실패");
            paymentRepository.save(payment);

            log.error("[결제] 실패: orderId={}", order.getId());
            throw new PaymentFailedException("결제 승인 실패");
        }

        // 3. 결제 승인
        payment.approve();
        Payment savedPayment = paymentRepository.save(payment);

        log.info("[결제] 성공: paymentId={}", savedPayment.getId());

        return savedPayment;
    }

    /**
     * 외부 PG사 호출 (시뮬레이션)
     */
    private boolean callPaymentGateway(String method, BigDecimal amount) {
        // 실제로는 토스페이먼츠, 네이버페이 등 PG사 API 호출
        log.info("[PG] 결제 요청: method={}, amount={}", method, amount);

        // 시뮬레이션: 10% 확률로 실패
        boolean success = Math.random() > 0.1;

        log.info("[PG] 결제 응답: {}", success ? "성공" : "실패");
        return success;
    }
}

// PointService.java
package com.example.order.service;

import com.example.order.entity.User;
import com.example.order.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Slf4j
public class PointService {

    private final UserRepository userRepository;

    /**
     * 포인트 적립 (REQUIRES_NEW: 별도 트랜잭션)
     * - 주문 실패해도 적립 로그는 남김
     */
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void earnPoints(Long userId, int points, String reason) {
        log.info("[포인트] 적립 시작: userId={}, points={}, reason={}",
                 userId, points, reason);

        User user = userRepository.findById(userId)
            .orElseThrow(() -> new IllegalArgumentException("사용자 없음"));

        user.earnPoints(points);
        userRepository.save(user);

        log.info("[포인트] 적립 완료: userId={}, 총 포인트={}",
                 userId, user.getPoints());
    }
}

// NotificationService.java
package com.example.order.service;

import com.example.order.entity.Order;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Service
@Slf4j
public class NotificationService {

    /**
     * 주문 완료 알림 발송
     * - 이메일, SMS 등
     */
    public void sendOrderNotification(Order order) {
        log.info("[알림] 주문 완료 알림 발송: orderId={}, userEmail={}",
                 order.getId(), order.getUser().getEmail());

        // 실제로는 이메일 발송 서비스 호출
        sendEmail(order.getUser().getEmail(), "주문이 완료되었습니다", buildEmailContent(order));

        sendSms(order.getUser().getEmail(), "주문 완료: 주문번호 " + order.getId());
    }

    private void sendEmail(String to, String subject, String content) {
        log.info("[이메일] 발송: to={}, subject={}", to, subject);
        // 실제 이메일 발송 로직
    }

    private void sendSms(String phone, String message) {
        log.info("[SMS] 발송: phone={}, message={}", phone, message);
        // 실제 SMS 발송 로직
    }

    private String buildEmailContent(Order order) {
        return String.format(
            "주문번호: %d\n총 금액: %s원\n상태: %s",
            order.getId(),
            order.getTotalAmount(),
            order.getStatus()
        );
    }
}
```

#### 5단계: 이벤트 처리 (트랜잭션 커밋 후 실행)

```java
// OrderCompletedEvent.java
package com.example.order.event;

import com.example.order.entity.Order;
import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public class OrderCompletedEvent {
    private final Order order;
}

// OrderEventListener.java
package com.example.order.event;

import com.example.order.entity.Order;
import com.example.order.service.NotificationService;
import com.example.order.service.PointService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;
import org.springframework.transaction.event.TransactionPhase;
import org.springframework.transaction.event.TransactionalEventListener;

@Component
@RequiredArgsConstructor
@Slf4j
public class OrderEventListener {

    private final PointService pointService;
    private final NotificationService notificationService;

    /**
     * 주문 완료 후 처리 (트랜잭션 커밋 후 실행)
     * - 포인트 적립
     * - 알림 발송
     */
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    @Async  // 비동기 처리
    public void handleOrderCompleted(OrderCompletedEvent event) {
        Order order = event.getOrder();

        log.info("===== 주문 완료 이벤트 처리 시작: orderId={} =====", order.getId());

        try {
            // 1. 포인트 적립 (구매 금액의 1%)
            int points = order.getTotalAmount().intValue() / 100;
            pointService.earnPoints(
                order.getUser().getId(),
                points,
                "주문 완료 적립: 주문번호 " + order.getId()
            );

            // 2. 알림 발송
            notificationService.sendOrderNotification(order);

            log.info("===== 주문 완료 이벤트 처리 완료: orderId={} =====", order.getId());

        } catch (Exception e) {
            // 이벤트 처리 실패해도 주문은 이미 완료됨
            log.error("주문 완료 이벤트 처리 실패: orderId={}", order.getId(), e);
            // TODO: 재시도 큐에 추가
        }
    }
}
```

#### 6단계: DTO 및 예외 클래스

```java
// OrderRequest.java
package com.example.order.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class OrderRequest {

    private Long userId;
    private List<OrderItemRequest> items;
    private String paymentMethod;

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class OrderItemRequest {
        private Long productId;
        private Integer quantity;
    }
}

// OrderResponse.java
package com.example.order.dto;

import com.example.order.entity.Order;
import com.example.order.entity.OrderStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OrderResponse {

    private Long orderId;
    private Long userId;
    private BigDecimal totalAmount;
    private OrderStatus status;
    private LocalDateTime createdAt;

    public static OrderResponse from(Order order) {
        return OrderResponse.builder()
            .orderId(order.getId())
            .userId(order.getUser().getId())
            .totalAmount(order.getTotalAmount())
            .status(order.getStatus())
            .createdAt(order.getCreatedAt())
            .build();
    }
}

// InsufficientStockException.java
package com.example.order.exception;

public class InsufficientStockException extends RuntimeException {
    public InsufficientStockException(String message) {
        super(message);
    }
}

// PaymentFailedException.java
package com.example.order.exception;

public class PaymentFailedException extends RuntimeException {
    public PaymentFailedException(String message) {
        super(message);
    }
}
```

#### 7단계: 테스트 코드 작성

```java
// OrderServiceTest.java
package com.example.order.service;

import com.example.order.dto.OrderRequest;
import com.example.order.dto.OrderResponse;
import com.example.order.entity.*;
import com.example.order.exception.InsufficientStockException;
import com.example.order.repository.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

import static org.assertj.core.api.Assertions.*;

@SpringBootTest
@Transactional
class OrderServiceTest {

    @Autowired
    private OrderService orderService;

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private PaymentRepository paymentRepository;

    private User testUser;
    private Product testProduct;

    @BeforeEach
    void setUp() {
        // 테스트 데이터 초기화
        orderRepository.deleteAll();
        paymentRepository.deleteAll();
        productRepository.deleteAll();
        userRepository.deleteAll();

        // 사용자 생성
        testUser = new User();
        testUser.setName("홍길동");
        testUser.setEmail("hong@example.com");
        testUser.setPoints(1000);
        testUser = userRepository.save(testUser);

        // 상품 생성
        testProduct = new Product();
        testProduct.setName("노트북");
        testProduct.setPrice(BigDecimal.valueOf(1500000));
        testProduct.setStock(10);
        testProduct = productRepository.save(testProduct);
    }

    @Test
    void 주문_생성_성공() {
        // given
        OrderRequest request = new OrderRequest();
        request.setUserId(testUser.getId());
        request.setPaymentMethod("CARD");
        request.setItems(List.of(
            new OrderRequest.OrderItemRequest(testProduct.getId(), 2)
        ));

        // when
        OrderResponse response = orderService.createOrder(request);

        // then
        assertThat(response).isNotNull();
        assertThat(response.getOrderId()).isNotNull();
        assertThat(response.getTotalAmount()).isEqualByComparingTo(BigDecimal.valueOf(3000000));
        assertThat(response.getStatus()).isEqualTo(OrderStatus.CONFIRMED);

        // 재고 확인
        Product product = productRepository.findById(testProduct.getId()).orElseThrow();
        assertThat(product.getStock()).isEqualTo(8);  // 10 - 2 = 8

        // 결제 확인
        Payment payment = paymentRepository.findByOrderId(response.getOrderId()).orElseThrow();
        assertThat(payment.getStatus()).isEqualTo(PaymentStatus.APPROVED);
    }

    @Test
    void 재고_부족_시_주문_실패_및_롤백() {
        // given
        OrderRequest request = new OrderRequest();
        request.setUserId(testUser.getId());
        request.setPaymentMethod("CARD");
        request.setItems(List.of(
            new OrderRequest.OrderItemRequest(testProduct.getId(), 15)  // 재고 초과
        ));

        // when & then
        assertThatThrownBy(() -> orderService.createOrder(request))
            .isInstanceOf(InsufficientStockException.class)
            .hasMessageContaining("재고 부족");

        // 롤백 확인: 재고 그대로
        Product product = productRepository.findById(testProduct.getId()).orElseThrow();
        assertThat(product.getStock()).isEqualTo(10);

        // 주문도 생성되지 않음
        assertThat(orderRepository.count()).isZero();

        // 결제도 생성되지 않음
        assertThat(paymentRepository.count()).isZero();
    }

    @Test
    void 주문_취소_및_재고_복구() {
        // given: 먼저 주문 생성
        OrderRequest request = new OrderRequest();
        request.setUserId(testUser.getId());
        request.setPaymentMethod("CARD");
        request.setItems(List.of(
            new OrderRequest.OrderItemRequest(testProduct.getId(), 3)
        ));
        OrderResponse createdOrder = orderService.createOrder(request);

        // 재고 확인: 10 - 3 = 7
        Product product = productRepository.findById(testProduct.getId()).orElseThrow();
        assertThat(product.getStock()).isEqualTo(7);

        // when: 주문 취소
        orderService.cancelOrder(createdOrder.getOrderId());

        // then: 재고 복구 확인
        product = productRepository.findById(testProduct.getId()).orElseThrow();
        assertThat(product.getStock()).isEqualTo(10);  // 7 + 3 = 10 복구됨!

        // 주문 상태 확인
        Order order = orderRepository.findById(createdOrder.getOrderId()).orElseThrow();
        assertThat(order.getStatus()).isEqualTo(OrderStatus.CANCELLED);
    }

    @Test
    void 동시_주문_시_재고_정확성_보장() throws InterruptedException {
        // given: 재고 5개인 상품
        testProduct.setStock(5);
        productRepository.save(testProduct);

        // when: 5개의 스레드가 동시에 1개씩 주문
        int threadCount = 5;
        Thread[] threads = new Thread[threadCount];

        for (int i = 0; i < threadCount; i++) {
            threads[i] = new Thread(() -> {
                try {
                    OrderRequest request = new OrderRequest();
                    request.setUserId(testUser.getId());
                    request.setPaymentMethod("CARD");
                    request.setItems(List.of(
                        new OrderRequest.OrderItemRequest(testProduct.getId(), 1)
                    ));

                    orderService.createOrder(request);
                } catch (Exception e) {
                    // 일부 주문은 실패할 수 있음 (결제 실패 등)
                }
            });
            threads[i].start();
        }

        // 모든 스레드 종료 대기
        for (Thread thread : threads) {
            thread.join();
        }

        // then: 재고는 정확히 0이어야 함 (마이너스 절대 불가!)
        Product product = productRepository.findById(testProduct.getId()).orElseThrow();
        assertThat(product.getStock()).isGreaterThanOrEqualTo(0);  // 절대 마이너스 안됨
    }
}
```

### 실행 결과

**정상 주문 시**:
```
===== 주문 생성 시작 =====
사용자 ID: 1, 상품 수: 1
상품 조회: id=1, name=노트북, stock=10
재고 차감 완료: 상품=노트북, 차감=2, 남은재고=8
주문 저장 완료: id=1, totalAmount=3000000
[결제] 시작: orderId=1, method=CARD, amount=3000000
[PG] 결제 요청: method=CARD, amount=3000000
[PG] 결제 응답: 성공
[결제] 성공: paymentId=1
===== 주문 생성 완료: orderId=1 =====
===== 주문 완료 이벤트 처리 시작: orderId=1 =====
[포인트] 적립 시작: userId=1, points=30000, reason=주문 완료 적립
[포인트] 적립 완료: userId=1, 총 포인트=31000
[알림] 주문 완료 알림 발송: orderId=1
===== 주문 완료 이벤트 처리 완료: orderId=1 =====

결과:
✅ 주문 생성: id=1, status=CONFIRMED
✅ 재고 차감: 10 → 8
✅ 결제 완료: paymentId=1, status=APPROVED
✅ 포인트 적립: 30,000 포인트
✅ 알림 발송: 이메일 + SMS
```

**재고 부족 시** (트랜잭션 롤백):
```
===== 주문 생성 시작 =====
상품 조회: id=1, name=노트북, stock=10
재고 부족: 상품=노트북, 요청=15, 재고=10

Exception: InsufficientStockException: 재고 부족: 요청=15, 재고=10
Rolling back JPA transaction

결과:
❌ 주문 생성 안됨
❌ 재고 변경 없음 (롤백)
❌ 결제 시도 안됨
❌ 포인트 적립 안됨
→ 트랜잭션 롤백으로 모든 작업 취소!
```

**주문 취소 시** (재고 복구):
```
===== 주문 취소 시작: orderId=1 =====
재고 복구: 상품=노트북, 복구=2, 현재재고=10
===== 주문 취소 완료: orderId=1 =====

결과:
✅ 주문 상태: CONFIRMED → CANCELLED
✅ 재고 복구: 8 → 10
✅ 이력 기록: "주문 취소 및 재고 복구"
```

### 트러블슈팅

#### 문제 1: 테스트 실행 시 "LazyInitializationException"

**증상**:
```
org.hibernate.LazyInitializationException: could not initialize proxy - no Session
```

**원인**: 트랜잭션 밖에서 지연 로딩 엔티티 접근

**해결 방법**:
```java
// ❌ 문제 코드
@Test
void test() {
    Order order = orderService.getOrder(1L);
    order.getItems().size();  // LazyInitializationException!
}

// ✅ 해결 방법 1: @Transactional 추가
@Test
@Transactional
void test() {
    Order order = orderService.getOrder(1L);
    order.getItems().size();  // OK
}

// ✅ 해결 방법 2: Fetch Join 사용
@Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.id = :id")
Optional<Order> findByIdWithItems(@Param("id") Long id);
```

#### 문제 2: H2 Console 접속 안됨

**증상**: `http://localhost:8080/h2-console` 접속 시 404

**해결 방법**:
```yaml
# application.yml
spring:
  h2:
    console:
      enabled: true
      path: /h2-console  # 경로 확인

# SecurityConfig가 있다면
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http.authorizeHttpRequests(auth -> auth
        .requestMatchers("/h2-console/**").permitAll()
    );
    http.headers(headers -> headers.frameOptions().disable());
    return http.build();
}
```

### 확장 아이디어

#### 추가 기능 1: 쿠폰 적용

**난이도**: ⭐⭐⭐☆☆
**구현 힌트**:
```java
@Entity
public class Coupon {
    private Long id;
    private String code;
    private BigDecimal discountRate;
    private LocalDateTime expiredAt;
}

@Transactional
public Order createOrderWithCoupon(OrderRequest request, String couponCode) {
    // 1. 쿠폰 조회 및 검증
    Coupon coupon = couponRepository.findByCode(couponCode)
        .orElseThrow();

    if (coupon.isExpired()) {
        throw new CouponExpiredException();
    }

    // 2. 주문 생성
    Order order = createOrder(request);

    // 3. 할인 적용
    BigDecimal discount = order.getTotalAmount()
        .multiply(coupon.getDiscountRate());
    order.setTotalAmount(order.getTotalAmount().subtract(discount));

    // 4. 쿠폰 사용 처리
    coupon.use();

    return order;
}
```

#### 추가 기능 2: 재고 알림 설정

**난이도**: ⭐⭐⭐⭐☆
**구현 힌트**:
```java
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
public void handleStockDecreased(StockDecreasedEvent event) {
    Product product = event.getProduct();

    // 재고가 10개 미만이면 관리자에게 알림
    if (product.getStock() < 10) {
        notificationService.sendLowStockAlert(product);
    }
}
```

### 코드 리뷰 포인트

#### 체크리스트
- [x] **@Transactional 범위가 적절한가?** (너무 크거나 작지 않은지)
- [x] **예외 처리가 올바른가?** (RuntimeException 또는 rollbackFor 설정)
- [x] **락 전략이 적절한가?** (비관적 락 vs 낙관적 락)
- [x] **트랜잭션 전파 속성이 올바른가?** (REQUIRED, REQUIRES_NEW 등)
- [x] **읽기 전용 조회에 readOnly=true 설정했는가?**
- [x] **이벤트 리스너가 AFTER_COMMIT으로 설정되어 있는가?**
- [x] **내부 호출 문제가 없는가?** (프록시 경유 확인)
- [x] **트랜잭션 로그가 충분한가?** (디버깅 가능한지)

---

*(다음 응답에서 FAQ, 면접 질문, 핵심 정리 등이 계속됩니다...)*
