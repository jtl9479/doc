# 22장: 다중 데이터소스와 Master-Slave 구성 - PART 3

> **이 문서는 Part 2의 연속입니다.** Part 1-2에서 개념, 실습, 실전 프로젝트를 완료했습니다.

---

## ❓ FAQ

### Q1. Master-Slave 구성 시 트랜잭션이 2개 DB에 걸쳐서 실행되나요?

**답변**: 아니요, **하나의 트랜잭션은 하나의 DataSource에서만 실행**됩니다.

**상세 설명**:
```java
@Service
public class UserService {

    // 트랜잭션 1: Master에서만 실행
    @Transactional
    public void createUser(UserRequest request) {
        User user = userRepository.save(new User(request));
        // 이 트랜잭션 내 모든 쿼리는 Master에서만 실행
    }

    // 트랜잭션 2: Slave에서만 실행
    @Transactional(readOnly = true)
    public List<User> getAllUsers() {
        return userRepository.findAll();
        // 이 트랜잭션 내 모든 쿼리는 Slave에서만 실행
    }
}
```

**주의사항**:
- 하나의 트랜잭션 내에서 Master와 Slave를 섞어 쓸 수 없습니다
- @Transactional(readOnly = true/false) 선언 시점에 DataSource가 결정됩니다
- 트랜잭션이 시작되면 종료될 때까지 같은 DataSource를 사용합니다

**분산 트랜잭션이 필요한 경우**:
```java
// 여러 DB에 걸친 트랜잭션이 필요하면 JTA 사용
@Transactional(propagation = Propagation.REQUIRED)
public void processOrder() {
    // 주문 DB에 저장 (트랜잭션 1)
    orderRepository.save(order);

    // 상품 DB 재고 감소 (트랜잭션 2)
    productService.decreaseStock(productId);

    // 두 트랜잭션을 하나로 묶으려면 JTA 필요
}
```

---

### Q2. Replication Lag이 1초라면 생성 직후 조회 시 항상 실패하나요?

**답변**: 아니요, **같은 트랜잭션에서 조회하면 문제 없습니다**.

**상세 설명**:

**❌ 문제 발생 케이스** (다른 트랜잭션):
```java
@Service
public class OrderService {

    @Transactional
    public Long createOrder(OrderRequest request) {
        Order order = orderRepository.save(new Order(request));
        return order.getId();  // 트랜잭션 종료
    }

    @Transactional(readOnly = true)
    public Order getOrder(Long id) {
        // 새 트랜잭션, Slave에서 조회 → Replication Lag 문제!
        return orderRepository.findById(id).orElseThrow();
    }
}

// Controller에서
Long orderId = orderService.createOrder(request);  // 트랜잭션 1
Order order = orderService.getOrder(orderId);      // 트랜잭션 2 → 실패 가능!
```

**✅ 해결 방법 1** (같은 트랜잭션):
```java
@Service
public class OrderService {

    @Transactional
    public OrderResponse createOrderAndReturn(OrderRequest request) {
        // 1. 저장 (Master)
        Order order = orderRepository.save(new Order(request));

        // 2. 조회 (같은 트랜잭션, Master에서 조회)
        Order saved = orderRepository.findById(order.getId()).orElseThrow();

        return OrderResponse.from(saved);
        // 트랜잭션 종료
    }
}
```

**✅ 해결 방법 2** (저장 후 바로 반환):
```java
@Service
public class OrderService {

    @Transactional
    public OrderResponse createOrder(OrderRequest request) {
        Order order = orderRepository.save(new Order(request));

        // 저장한 엔티티를 바로 반환 (DB 재조회 불필요)
        return OrderResponse.from(order);
    }
}
```

**Replication Lag 특성**:
- 보통 0.5~1초 이내
- 네트워크 상태, DB 부하에 따라 최대 10초까지 가능
- 생성 후 1초 이후 조회는 대부분 안전

---

### Q3. Master DB가 장애나면 어떻게 되나요?

**답변**: **Master 장애 시 쓰기 작업은 불가능**하며, 수동 또는 자동 Failover 필요합니다.

**상세 설명**:

**장애 시나리오**:
```
1. Master DB 장애 발생
2. 읽기: Slave에서 계속 처리 (정상 동작)
3. 쓰기: Master에 접근 불가 → SQLException 발생
```

**해결책 1: 자동 Failover (MySQL Replication)**
```sql
-- Master 장애 시 Slave 중 하나를 Master로 승격

-- Slave1에서 실행 (새 Master가 됨)
STOP SLAVE;
RESET MASTER;
RESET SLAVE ALL;

-- Slave2, Slave3를 새 Master로 연결
CHANGE MASTER TO
  MASTER_HOST='slave1',
  MASTER_PORT=3307,
  MASTER_USER='replication',
  MASTER_PASSWORD='password';
START SLAVE;
```

**해결책 2: ProxySQL 사용**
```yaml
# ProxySQL이 Master 장애 감지 후 자동 Failover
# application.yml
spring:
  datasource:
    master:
      hikari:
        # ProxySQL을 통해 접근
        jdbc-url: jdbc:mysql://proxysql:6033/testdb
        # ProxySQL이 자동으로 정상 Master로 라우팅
```

**해결책 3: Kubernetes + StatefulSet**
```yaml
# Kubernetes가 Master Pod 재시작
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql-master
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        livenessProbe:  # 장애 감지
          tcpSocket:
            port: 3306
          initialDelaySeconds: 30
          periodSeconds: 10
```

**실무 권장 사항**:
- 💡 **Master는 이중화 필수** (Active-Standby)
- 💡 **자동 Failover 구성** (ProxySQL, Orchestrator 등)
- 💡 **Slave를 Read-Only Master로 승격** 가능하도록 설정
- 💡 **모니터링 시스템** 구축 (장애 즉시 알림)

---

### Q4. Slave가 3대인데 1대만 장애나면 어떻게 되나요?

**답변**: **나머지 2대의 Slave로 자동 분산**되며 서비스는 정상 운영됩니다.

**상세 설명**:

**정상 동작 (Slave 3대)**:
```java
// 읽기 요청 분산
요청 1 → slave1 (33.3%)
요청 2 → slave2 (33.3%)
요청 3 → slave3 (33.3%)
요청 4 → slave1 (33.3%)
...
```

**Slave2 장애 발생**:
```java
// Health Check가 slave2 장애 감지
2024-01-15 10:30:00 ERROR - slave2 장애 감지

// 나머지 2대로 분산
요청 1 → slave1 (50%)
요청 2 → slave3 (50%)
요청 3 → slave1 (50%)
요청 4 → slave3 (50%)
...

// 성능 영향: 각 Slave 부하 33% → 50% 증가
```

**자동 Failover 코드** (Part 2에서 구현):
```java
@Slf4j
public class LoadBalancedRoutingDataSource extends AbstractRoutingDataSource {

    private final Set<String> unavailableSlaves = ConcurrentHashMap.newKeySet();

    @Override
    protected Object determineCurrentLookupKey() {
        boolean isReadOnly = TransactionSynchronizationManager.isCurrentTransactionReadOnly();

        if (isReadOnly) {
            // 정상 Slave만 선택
            List<String> availableSlaves = SLAVES.stream()
                .filter(slave -> !unavailableSlaves.contains(slave))
                .collect(Collectors.toList());

            if (availableSlaves.isEmpty()) {
                // 모든 Slave 장애 시 Master로 폴백
                return "master";
            }

            // 라운드 로빈
            int index = counter.getAndIncrement() % availableSlaves.size();
            return availableSlaves.get(index);
        }

        return "master";
    }

    @Scheduled(fixedRate = 5000)
    public void checkSlavesHealth() {
        for (String slave : SLAVES) {
            try {
                DataSource ds = (DataSource) resolvedDataSources.get(slave);
                try (Connection conn = ds.getConnection()) {
                    if (conn.isValid(2)) {
                        unavailableSlaves.remove(slave);  // 복구
                    } else {
                        unavailableSlaves.add(slave);     // 장애
                    }
                }
            } catch (Exception e) {
                unavailableSlaves.add(slave);
            }
        }
    }
}
```

**Slave 복구 시**:
```java
// Health Check가 slave2 복구 감지
2024-01-15 10:35:00 INFO - slave2 복구됨!

// 다시 3대로 분산
요청 1 → slave1 (33.3%)
요청 2 → slave2 (33.3%)
요청 3 → slave3 (33.3%)
...
```

**실무 권장**:
- 💡 **Slave는 최소 3대 이상** 권장 (1대 장애 시에도 충분한 여유)
- 💡 **Health Check 주기 5~10초** (빠른 장애 감지)
- 💡 **모니터링 알림 설정** (Slave 장애 시 즉시 복구)

---

### Q5. 통계성 쿼리가 일반 조회를 느리게 만드는데 어떻게 해결하나요?

**답변**: **통계 전용 Slave를 별도로 구성**하여 격리합니다.

**문제 상황**:
```java
// 문제: 통계 쿼리가 일반 조회와 같은 Slave 사용
@Transactional(readOnly = true)
public DailySales calculateDailySales() {
    // 복잡한 집계 쿼리 (10초 소요)
    // → Slave의 CPU/메모리 점유
    // → 일반 조회 느려짐!
    return orderRepository.aggregateDailySales(...);
}

@Transactional(readOnly = true)
public Order getOrder(Long id) {
    // 일반 조회도 같은 Slave 사용
    // → 통계 쿼리 때문에 느려짐!
    return orderRepository.findById(id).orElseThrow();
}
```

**해결책 1: 통계 전용 Slave 추가**
```java
@Configuration
public class DataSourceConfig {

    @Bean
    public DataSource masterDataSource() {
        // Master: 쓰기
    }

    @Bean
    public DataSource slave1DataSource() {
        // Slave1: 일반 읽기
    }

    @Bean
    public DataSource slave2DataSource() {
        // Slave2: 일반 읽기
    }

    @Bean
    public DataSource analyticsSlaveDataSource() {
        // Slave3: 통계 전용 (격리)
        HikariDataSource ds = createDataSource("slave3:3309");
        ds.setMaximumPoolSize(5);  // 작은 풀로 제한
        ds.setReadOnly(true);
        return ds;
    }

    @Bean
    public DataSource routingDataSource() {
        Map<Object, Object> dataSourceMap = new HashMap<>();
        dataSourceMap.put("master", masterDataSource());
        dataSourceMap.put("slave", slave1DataSource());
        dataSourceMap.put("analytics", analyticsSlaveDataSource());

        // 라우팅 로직 구현
        return new RoutingDataSource(dataSourceMap);
    }
}
```

**해결책 2: 커스텀 어노테이션 사용**
```java
// 통계 전용 어노테이션
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Transactional(readOnly = true)
public @interface AnalyticsQuery {
}

// AOP로 통계 Slave로 라우팅
@Aspect
@Component
public class AnalyticsAspect {

    @Around("@annotation(analyticsQuery)")
    public Object routeToAnalyticsSlave(ProceedingJoinPoint pjp, AnalyticsQuery analyticsQuery)
        throws Throwable {

        AnalyticsContextHolder.setAnalytics(true);

        try {
            return pjp.proceed();
        } finally {
            AnalyticsContextHolder.clear();
        }
    }
}

// 사용
@Service
public class StatisticsService {

    @AnalyticsQuery  // 통계 Slave 사용
    public DailySales calculateDailySales() {
        // 복잡한 집계 쿼리 (통계 Slave에서만 실행)
        return orderRepository.aggregateDailySales(...);
    }
}

@Service
public class OrderService {

    @Transactional(readOnly = true)  // 일반 Slave 사용
    public Order getOrder(Long id) {
        // 일반 조회 (일반 Slave에서 빠르게 실행)
        return orderRepository.findById(id).orElseThrow();
    }
}
```

**해결책 3: 배치 처리 + 캐싱**
```java
@Service
public class StatisticsService {

    @Cacheable(value = "dailySales", key = "#date")
    public DailySales getDailySales(LocalDate date) {
        // 캐시에서 조회 (DB 접근 최소화)
        return cachedDailySales.get(date);
    }

    @Scheduled(cron = "0 0 2 * * *")  // 새벽 2시에 실행
    @AnalyticsQuery
    public void calculateAndCacheDailySales() {
        // 야간 배치로 통계 계산
        // 결과를 캐시에 저장
        LocalDate yesterday = LocalDate.now().minusDays(1);
        DailySales sales = orderRepository.aggregateDailySales(yesterday);
        cache.put(yesterday, sales);
    }
}
```

**성능 비교**:

| 구성 | 일반 조회 응답 시간 | 통계 쿼리 영향 |
|------|----------------|-------------|
| **통계 Slave 없음** | 500ms | 통계 실행 시 2초↑ |
| **통계 Slave 격리** | 50ms | 영향 없음 |
| **배치 + 캐싱** | 10ms | 영향 없음 |

**실무 권장**:
- 💡 **통계 전용 Slave 격리**로 일반 조회 성능 보장
- 💡 **무거운 통계는 야간 배치**로 처리
- 💡 **결과는 캐시에 저장**하여 반복 조회 최적화

---

### Q6. 읽기:쓰기 비율이 50:50이면 Master-Slave가 필요한가요?

**답변**: 비율보다는 **절대적인 트래픽 양과 확장성**이 중요합니다.

**상세 분석**:

**케이스 1: 트래픽이 적은 경우 (50:50 비율)**
```
일일 사용자: 1,000명
읽기: 초당 50건
쓰기: 초당 50건

→ Master 1대로 충분
→ Master-Slave 불필요
```

**케이스 2: 트래픽이 많은 경우 (50:50 비율)**
```
일일 사용자: 100만명
읽기: 초당 10,000건
쓰기: 초당 10,000건

→ Master 1대로 부족
→ Master-Slave + Sharding 필요
```

**Master-Slave가 필요한 경우**:

1. **읽기 트래픽이 Master 성능 한계 초과**
   - Master CPU 90% 이상
   - 읽기 응답 시간 1초 이상

2. **가용성 향상 필요**
   - Master 장애 시 Slave를 Master로 승격
   - 읽기는 계속 Slave에서 처리

3. **지역별 분산 필요**
   - 서울, 부산, 대전 등 지역별 Slave
   - 낮은 레이턴시

4. **통계/분석 쿼리 격리 필요**
   - 무거운 쿼리를 별도 Slave에서 처리

**50:50 비율에서의 대안**:

**대안 1: Sharding (쓰기 분산)**
```java
// 사용자 ID 기반 Sharding
@Configuration
public class ShardingDataSourceConfig {

    @Bean
    public DataSource shard1DataSource() {
        // Shard 1: userId % 3 == 0
    }

    @Bean
    public DataSource shard2DataSource() {
        // Shard 2: userId % 3 == 1
    }

    @Bean
    public DataSource shard3DataSource() {
        // Shard 3: userId % 3 == 2
    }

    // 각 Shard마다 Master-Slave 구성
}
```

**대안 2: CQRS (읽기/쓰기 분리 아키텍처)**
```java
// Command (쓰기): Master DB
@Service
public class OrderCommandService {
    @Transactional
    public void createOrder(OrderCommand command) {
        Order order = orderRepository.save(new Order(command));
        eventPublisher.publish(new OrderCreatedEvent(order));
    }
}

// Query (읽기): Slave DB 또는 Read Model
@Service
public class OrderQueryService {
    @Transactional(readOnly = true)
    public OrderView getOrder(Long id) {
        return orderViewRepository.findById(id).orElseThrow();
    }
}
```

**의사결정 가이드**:

| 트래픽 | 읽기:쓰기 비율 | 권장 구성 |
|--------|------------|---------|
| 소규모 (< 1,000 QPS) | 모든 비율 | Master 1대 |
| 중규모 (1,000~10,000 QPS) | 70:30 이상 | Master 1 + Slave 2~3 |
| 대규모 (> 10,000 QPS) | 70:30 이상 | Master 1 + Slave 5+ |
| 대규모 (> 10,000 QPS) | 50:50 | Master 2+ (Sharding) + Slave |

---

### Q7. LazyConnectionDataSourceProxy가 정확히 어떻게 동작하나요?

**답변**: **실제 쿼리 실행 시점까지 Connection 획득을 지연**시킵니다.

**문제 상황 (LazyProxy 없을 때)**:
```java
@Service
public class UserService {

    @Transactional(readOnly = true)
    public List<User> getAllUsers() {
        // 1. @Transactional 시작
        //    → 트랜잭션 시작
        //    → 즉시 Connection 획득 시도
        //    → 이 시점에 DataSource 결정!

        // 2. 하지만 아직 readOnly 정보가 설정되지 않음
        //    → Master로 연결됨 (잘못된 동작!)

        // 3. 쿼리 실행
        return userRepository.findAll();
    }
}
```

**동작 순서 (LazyProxy 없을 때)**:
```
1. @Transactional(readOnly=true) 진입
2. 트랜잭션 매니저 시작
3. Connection 즉시 획득 시도
4. determineCurrentLookupKey() 호출
   → isCurrentTransactionReadOnly() = false (아직 설정 안됨!)
   → Master 선택 (잘못됨!)
5. readOnly 플래그 설정
6. 쿼리 실행 (Master에서 실행됨, 원래는 Slave여야 함)
```

**해결 (LazyProxy 사용)**:
```java
@Configuration
public class DataSourceConfig {

    @Bean
    public DataSource routingDataSource() {
        // 라우팅 DataSource 생성
        ReplicationRoutingDataSource routingDataSource =
            new ReplicationRoutingDataSource();

        Map<Object, Object> dataSourceMap = new HashMap<>();
        dataSourceMap.put("master", masterDataSource());
        dataSourceMap.put("slave", slaveDataSource());

        routingDataSource.setTargetDataSources(dataSourceMap);

        return routingDataSource;
    }

    @Bean
    @Primary
    public DataSource dataSource() {
        // 핵심: LazyConnectionDataSourceProxy로 감싸기!
        return new LazyConnectionDataSourceProxy(routingDataSource());
    }
}
```

**동작 순서 (LazyProxy 있을 때)**:
```
1. @Transactional(readOnly=true) 진입
2. 트랜잭션 매니저 시작
3. LazyProxy가 Connection 획득 지연 (획득하지 않음!)
4. readOnly 플래그 설정
5. 쿼리 실행 시점에 Connection 획득
6. determineCurrentLookupKey() 호출
   → isCurrentTransactionReadOnly() = true (올바르게 설정됨!)
   → Slave 선택 (올바름!)
7. 쿼리 실행 (Slave에서 실행됨)
```

**LazyConnectionDataSourceProxy 내부 동작**:
```java
// LazyConnectionDataSourceProxy의 간략한 구현
public class LazyConnectionDataSourceProxy extends DelegatingDataSource {

    @Override
    public Connection getConnection() {
        // 즉시 Connection을 반환하지 않고 Proxy 반환
        return (Connection) Proxy.newProxyInstance(
            ConnectionProxy.class.getClassLoader(),
            new Class<?>[] { ConnectionProxy.class },
            new LazyConnectionInvocationHandler()  // Lazy 핸들러
        );
    }

    private class LazyConnectionInvocationHandler implements InvocationHandler {

        private Connection target;

        @Override
        public Object invoke(Object proxy, Method method, Object[] args) {
            // 실제 메서드 호출 시점에 Connection 획득!
            if (target == null) {
                target = obtainTargetDataSource().getConnection();
            }
            return method.invoke(target, args);
        }
    }
}
```

**비교**:

| 구분 | LazyProxy 없음 | LazyProxy 있음 |
|------|-------------|-------------|
| **Connection 획득 시점** | 트랜잭션 시작 시 | 첫 쿼리 실행 시 |
| **readOnly 판단 시점** | Connection 획득 시 | 첫 쿼리 실행 시 |
| **DataSource 선택** | 잘못된 선택 가능 | 올바른 선택 보장 |
| **성능 영향** | 없음 | 미미함 (ns 단위) |

**실무 필수**:
```java
// ✅ 반드시 LazyConnectionDataSourceProxy 사용!
@Bean
@Primary
public DataSource dataSource() {
    return new LazyConnectionDataSourceProxy(routingDataSource());
}

// ❌ 직접 사용하면 readOnly 동작 안 함
@Bean
@Primary
public DataSource dataSource() {
    return routingDataSource();  // 잘못됨!
}
```

---

## 📝 면접 질문

### 주니어 개발자 면접 질문

#### 질문 1. Master-Slave Replication이 무엇인지 설명해주세요.

**모범 답안**:

Master-Slave Replication은 **데이터베이스를 Master(쓰기 전용)와 Slave(읽기 전용)로 분리**하여 성능을 향상시키는 구조입니다.

**핵심 원리**:
1. **Master**: 모든 쓰기 작업(INSERT, UPDATE, DELETE)을 처리
2. **Slave**: Master의 데이터를 복제하여 읽기 작업(SELECT)을 처리
3. **Binary Log**: Master의 변경 사항을 Slave에 전달
4. **읽기/쓰기 분리**: 애플리케이션에서 @Transactional(readOnly = true/false)로 구분

**장점**:
- 읽기 처리량 증가 (Slave 개수만큼 확장 가능)
- Master 부하 감소 (읽기 작업을 Slave로 분산)
- 가용성 향상 (Master 장애 시 Slave를 Master로 승격 가능)

**단점**:
- Replication Lag (Master와 Slave 간 데이터 지연, 보통 1초 이내)
- 구성 복잡도 증가
- 일관성 문제 (생성 직후 조회 시 주의 필요)

**실무 사용**:
- 대부분의 서비스는 읽기가 80% 이상
- 배달의민족: 점심 시간대 초당 50,000건 조회를 Slave 10대로 처리
- 쿠팡: 상품 검색은 Slave, 주문은 Master에서 처리

---

#### 질문 2. @Transactional(readOnly = true)는 정확히 어떻게 동작하나요?

**모범 답안**:

@Transactional(readOnly = true)는 **트랜잭션을 읽기 전용으로 설정**하여 몇 가지 최적화를 활성화합니다.

**핵심 동작**:

1. **DataSource 라우팅**:
```java
public class ReplicationRoutingDataSource extends AbstractRoutingDataSource {
    @Override
    protected Object determineCurrentLookupKey() {
        boolean isReadOnly = TransactionSynchronizationManager.isCurrentTransactionReadOnly();
        return isReadOnly ? "slave" : "master";
    }
}
```

2. **Hibernate 최적화**:
```java
@Transactional(readOnly = true)
public List<User> getUsers() {
    // Hibernate가 스냅샷 저장 건너뜀
    // 더티 체킹 비활성화
    // flush 모드를 MANUAL로 변경
    return userRepository.findAll();
}
```

3. **JDBC 레벨 최적화**:
```java
// Connection에 readOnly 플래그 설정
connection.setReadOnly(true);

// 일부 JDBC 드라이버는 이를 활용하여 최적화
// - MySQL: Slave로 라우팅
// - PostgreSQL: 읽기 전용 최적화
```

**효과**:
- **DataSource 분리**: Master/Slave 자동 선택
- **성능 향상**: Hibernate 스냅샷/더티 체킹 생략 (약 10~20% 개선)
- **안전성**: 실수로 쓰기 작업 시도 시 예외 발생

**주의사항**:
```java
// ❌ readOnly 트랜잭션 내에서 쓰기 시도
@Transactional(readOnly = true)
public void updateUser(Long id) {
    User user = userRepository.findById(id).orElseThrow();
    user.updateName("새 이름");  // TransactionSystemException 발생!
}
```

---

#### 질문 3. Replication Lag이 무엇이고 어떻게 대응하나요?

**모범 답안**:

Replication Lag은 **Master에 쓴 데이터가 Slave에 복제되기까지의 시간 지연**입니다.

**발생 원인**:
1. **네트워크 지연**: Master와 Slave 간 물리적 거리
2. **Slave 부하**: Slave가 복제 처리보다 읽기 쿼리에 바쁨
3. **대량 쓰기**: Master의 대량 INSERT/UPDATE

**일반적인 Lag 시간**:
- 정상: 0.1~1초
- 부하 시: 1~5초
- 문제 상황: 10초 이상

**대응 방법**:

**방법 1: 같은 트랜잭션에서 처리**
```java
// ✅ 올바른 방법
@Transactional
public OrderResponse createOrderAndReturn(OrderRequest request) {
    Order order = orderRepository.save(new Order(request));
    // 같은 트랜잭션, Master에서 조회 → Lag 문제 없음
    return OrderResponse.from(order);
}
```

**방법 2: 생성 후 바로 반환**
```java
// ✅ 가장 권장
@Transactional
public OrderResponse createOrder(OrderRequest request) {
    Order order = orderRepository.save(new Order(request));
    // 저장한 엔티티를 바로 반환 (재조회 불필요)
    return OrderResponse.from(order);
}
```

**방법 3: Master에서 강제 조회**
```java
// ✅ 최신 데이터가 필수인 경우
@Transactional(readOnly = false)  // Master 사용
public Order getOrderFromMaster(Long id) {
    return orderRepository.findById(id).orElseThrow();
}
```

**방법 4: Retry 로직**
```java
// ✅ Slave에서 조회 실패 시 재시도
@Transactional(readOnly = true)
@Retryable(maxAttempts = 3, backoff = @Backoff(delay = 500))
public Order getOrder(Long id) {
    return orderRepository.findById(id)
        .orElseThrow(() -> new OrderNotFoundException("주문 없음"));
}
```

**모니터링**:
```sql
-- MySQL에서 Replication Lag 확인
SHOW SLAVE STATUS\G
-- Seconds_Behind_Master: 0이면 정상, 10 이상이면 문제
```

---

#### 질문 4. HikariCP의 커넥션 풀 크기는 어떻게 설정하나요?

**모범 답안**:

HikariCP 커넥션 풀 크기는 **트래픽 특성과 DB 리소스를 고려**하여 설정합니다.

**기본 공식**:
```
pool size = (core count * 2) + effective_spindle_count

예: CPU 4코어, HDD 1개
→ pool size = (4 * 2) + 1 = 9 → 10으로 설정
```

**Master-Slave 구성 시**:

**읽기:쓰기 = 95:5 비율**:
```yaml
spring:
  datasource:
    master:
      hikari:
        maximum-pool-size: 10   # 쓰기 5%
        minimum-idle: 5

    slave:
      hikari:
        maximum-pool-size: 50   # 읽기 95%
        minimum-idle: 20
```

**트래픽별 권장 설정**:

| 동시 사용자 | Master Pool | Slave Pool (1대) | Slave 개수 |
|----------|------------|---------------|----------|
| 100명 | 5 | 10 | 1개 |
| 1,000명 | 10 | 30 | 1~2개 |
| 10,000명 | 10 | 50 | 2~3개 |
| 100,000명 | 20 | 30 | 5~10개 |

**주요 설정**:
```yaml
spring:
  datasource:
    hikari:
      # 풀 크기
      maximum-pool-size: 10
      minimum-idle: 5

      # 타임아웃
      connection-timeout: 3000      # 커넥션 대기 시간 (ms)
      idle-timeout: 600000          # 유휴 커넥션 유지 시간 (10분)
      max-lifetime: 1800000         # 커넥션 최대 수명 (30분)

      # 검증
      connection-test-query: SELECT 1
      validation-timeout: 2000
```

**풀 크기 결정 팁**:
1. **적게 시작**: 10으로 시작하여 점진적 증가
2. **모니터링**: HikariCP MBean으로 실시간 확인
3. **대기 스레드 확인**: ThreadsAwaitingConnection > 0이면 풀 부족
4. **DB 리소스 고려**: DB의 max_connections 확인

**모니터링 코드**:
```java
@Component
@RequiredArgsConstructor
public class ConnectionPoolMonitor {

    private final HikariDataSource dataSource;

    @Scheduled(fixedRate = 60000)
    public void monitor() {
        HikariPoolMXBean pool = dataSource.getHikariPoolMXBean();

        log.info("Active: {}, Idle: {}, Total: {}, Waiting: {}",
            pool.getActiveConnections(),
            pool.getIdleConnections(),
            pool.getTotalConnections(),
            pool.getThreadsAwaitingConnection());

        if (pool.getThreadsAwaitingConnection() > 0) {
            log.warn("커넥션 풀 부족! 풀 크기 증가 고려");
        }
    }
}
```

---

#### 질문 5. Master-Slave 구성 시 트랜잭션 전파는 어떻게 되나요?

**모범 답안**:

트랜잭션 전파 시 **처음 시작된 트랜잭션의 DataSource를 그대로 사용**합니다.

**핵심 원리**:
- 하나의 트랜잭션은 하나의 DataSource에서만 실행
- 내부 메서드 호출 시 외부 트랜잭션의 DataSource 유지
- DataSource 변경이 필요하면 새 트랜잭션 시작 필요

**케이스 1: REQUIRED (기본 동작)**
```java
@Service
public class OrderService {

    @Autowired
    private ProductService productService;

    // 외부 트랜잭션 (Master 사용)
    @Transactional
    public void createOrder(OrderRequest request) {
        // 1. Master에서 주문 저장
        Order order = orderRepository.save(new Order(request));

        // 2. 내부 메서드 호출
        productService.checkStock(request.getProductId());
        // → 외부 트랜잭션 참여
        // → Master에서 실행됨!
    }
}

@Service
public class ProductService {

    // 내부 트랜잭션 (readOnly = true)
    @Transactional(readOnly = true)
    public void checkStock(Long productId) {
        // 외부가 Master 트랜잭션이므로 Master에서 실행
        // readOnly = true는 무시됨!
        Product product = productRepository.findById(productId).orElseThrow();

        if (product.getStock() < 1) {
            throw new OutOfStockException();
        }
    }
}
```

**케이스 2: REQUIRES_NEW (새 트랜잭션)**
```java
@Service
public class OrderService {

    @Transactional
    public void createOrder(OrderRequest request) {
        // 외부 트랜잭션 (Master)
        Order order = orderRepository.save(new Order(request));

        // 새 트랜잭션 시작
        productService.checkStock(request.getProductId());
    }
}

@Service
public class ProductService {

    // 새 트랜잭션 생성
    @Transactional(readOnly = true, propagation = Propagation.REQUIRES_NEW)
    public void checkStock(Long productId) {
        // 새 트랜잭션 시작
        // → readOnly = true 적용
        // → Slave에서 실행됨!
        Product product = productRepository.findById(productId).orElseThrow();

        if (product.getStock() < 1) {
            throw new OutOfStockException();
        }
    }
}
```

**트랜잭션 전파별 DataSource 동작**:

| Propagation | 외부 트랜잭션 | 내부 설정 | 사용 DataSource | 비고 |
|------------|-----------|--------|---------------|-----|
| **REQUIRED** | Master | readOnly = true | Master | 외부 참여 |
| **REQUIRED** | Slave | readOnly = false | Slave | 외부 참여 (쓰기 불가) |
| **REQUIRES_NEW** | Master | readOnly = true | Slave | 새 트랜잭션 |
| **REQUIRES_NEW** | Slave | readOnly = false | Master | 새 트랜잭션 |
| **SUPPORTS** | 없음 | readOnly = true | Slave | 트랜잭션 없이 실행 |

**실무 주의사항**:
```java
// ❌ 잘못된 사용
@Transactional(readOnly = false)  // Master
public void method1() {
    // ...
    method2();  // 내부 메서드 호출
}

@Transactional(readOnly = true)  // Slave를 기대
public void method2() {
    // 하지만 method1의 Master 트랜잭션 참여
    // Master에서 실행됨!
}

// ✅ 올바른 사용 (새 트랜잭션 필요 시)
@Transactional(readOnly = true, propagation = Propagation.REQUIRES_NEW)
public void method2() {
    // 새 트랜잭션 시작
    // Slave에서 실행됨
}
```

---

#### 질문 6. LazyConnectionDataSourceProxy는 왜 필요한가요?

**모범 답안**:

LazyConnectionDataSourceProxy는 **Connection 획득을 실제 쿼리 실행 시점까지 지연**시켜 readOnly 플래그가 올바르게 설정되도록 합니다.

**문제 상황 (Proxy 없을 때)**:
```
1. @Transactional(readOnly=true) 시작
2. 트랜잭션 매니저가 Connection 즉시 획득 시도
3. AbstractRoutingDataSource.determineCurrentLookupKey() 호출
4. 하지만 아직 readOnly 플래그 설정 전!
   → isCurrentTransactionReadOnly() = false
   → Master 선택 (잘못됨!)
5. readOnly 플래그 설정
6. 쿼리 실행 (Master에서 실행, 원래는 Slave)
```

**해결 (Proxy 사용)**:
```java
@Configuration
public class DataSourceConfig {

    @Bean
    @Primary
    public DataSource dataSource() {
        // LazyProxy로 감싸기!
        return new LazyConnectionDataSourceProxy(routingDataSource());
    }
}

// 동작 순서:
// 1. @Transactional(readOnly=true) 시작
// 2. LazyProxy가 Connection 획득 지연 (Proxy 객체만 반환)
// 3. readOnly 플래그 설정
// 4. 쿼리 실행 시점에 실제 Connection 획득
// 5. determineCurrentLookupKey() 호출
//    → isCurrentTransactionReadOnly() = true (올바름!)
//    → Slave 선택
// 6. 쿼리 실행 (Slave에서 실행)
```

**Lazy Proxy의 동작 원리**:
```java
// 간략화된 구현
public class LazyConnectionDataSourceProxy extends DelegatingDataSource {

    @Override
    public Connection getConnection() {
        // 실제 Connection 대신 Proxy 반환
        return (Connection) Proxy.newProxyInstance(
            ConnectionProxy.class.getClassLoader(),
            new Class<?>[] { ConnectionProxy.class },
            new LazyConnectionInvocationHandler()
        );
    }

    private class LazyConnectionInvocationHandler implements InvocationHandler {

        private Connection target;  // 실제 Connection

        @Override
        public Object invoke(Object proxy, Method method, Object[] args) {
            // 메서드 호출 시점에 실제 Connection 획득!
            if (target == null) {
                target = obtainTargetDataSource().getConnection();
            }
            return method.invoke(target, args);
        }
    }
}
```

**성능 영향**:
- Proxy 오버헤드: 거의 없음 (나노초 단위)
- Connection 획득 지연: 실제 차이 없음 (어차피 첫 쿼리에서 획득)

**필수 사용**:
```java
// ✅ 반드시 사용
@Bean
@Primary
public DataSource dataSource() {
    return new LazyConnectionDataSourceProxy(routingDataSource());
}

// ❌ 직접 사용하면 readOnly 동작 안 함
@Bean
@Primary
public DataSource dataSource() {
    return routingDataSource();  // 잘못됨!
}
```

---

#### 질문 7. 여러 개의 DataSource를 사용할 때 트랜잭션 매니저는 어떻게 설정하나요?

**모범 답안**:

여러 DataSource 사용 시 **각 DataSource마다 별도의 TransactionManager를 설정**하거나, **AbstractRoutingDataSource를 사용**합니다.

**방법 1: 단일 TransactionManager (Master-Slave)**
```java
@Configuration
@EnableTransactionManagement
public class DataSourceConfig {

    @Bean
    public DataSource routingDataSource() {
        // Master-Slave 라우팅
        ReplicationRoutingDataSource routingDataSource =
            new ReplicationRoutingDataSource();

        Map<Object, Object> dataSourceMap = new HashMap<>();
        dataSourceMap.put("master", masterDataSource());
        dataSourceMap.put("slave", slaveDataSource());

        routingDataSource.setTargetDataSources(dataSourceMap);
        return routingDataSource;
    }

    @Bean
    @Primary
    public DataSource dataSource() {
        return new LazyConnectionDataSourceProxy(routingDataSource());
    }

    @Bean
    @Primary
    public PlatformTransactionManager transactionManager() {
        // 단일 트랜잭션 매니저로 Master/Slave 모두 관리
        return new DataSourceTransactionManager(dataSource());
    }
}

// 사용
@Service
public class UserService {

    @Transactional  // 기본 TransactionManager 사용
    public void createUser(UserRequest request) {
        // Master 사용
    }

    @Transactional(readOnly = true)  // 같은 TransactionManager
    public List<User> getUsers() {
        // Slave 사용
    }
}
```

**방법 2: 다중 TransactionManager (도메인별 DB 분리)**
```java
// 상품 DB 설정
@Configuration
@EnableJpaRepositories(
    basePackages = "com.example.product.repository",
    entityManagerFactoryRef = "productEntityManagerFactory",
    transactionManagerRef = "productTransactionManager"  // 전용 매니저
)
public class ProductDataSourceConfig {

    @Bean
    @Primary
    public DataSource productDataSource() {
        // 상품 DB (Master-Slave)
        return createRoutingDataSource(...);
    }

    @Bean
    @Primary
    public LocalContainerEntityManagerFactoryBean productEntityManagerFactory(
        EntityManagerFactoryBuilder builder) {
        return builder
            .dataSource(productDataSource())
            .packages("com.example.product.entity")
            .persistenceUnit("product")
            .build();
    }

    @Bean
    @Primary
    public PlatformTransactionManager productTransactionManager(
        @Qualifier("productEntityManagerFactory") EntityManagerFactory emf) {
        return new JpaTransactionManager(emf);
    }
}

// 주문 DB 설정
@Configuration
@EnableJpaRepositories(
    basePackages = "com.example.order.repository",
    entityManagerFactoryRef = "orderEntityManagerFactory",
    transactionManagerRef = "orderTransactionManager"  // 전용 매니저
)
public class OrderDataSourceConfig {

    @Bean
    public DataSource orderDataSource() {
        // 주문 DB
        return createDataSource(...);
    }

    @Bean
    public LocalContainerEntityManagerFactoryBean orderEntityManagerFactory(
        EntityManagerFactoryBuilder builder) {
        return builder
            .dataSource(orderDataSource())
            .packages("com.example.order.entity")
            .persistenceUnit("order")
            .build();
    }

    @Bean
    public PlatformTransactionManager orderTransactionManager(
        @Qualifier("orderEntityManagerFactory") EntityManagerFactory emf) {
        return new JpaTransactionManager(emf);
    }
}

// 사용
@Service
public class ProductService {

    @Transactional(value = "productTransactionManager")
    public void createProduct(ProductRequest request) {
        // 상품 DB 사용
        productRepository.save(new Product(request));
    }
}

@Service
public class OrderService {

    @Transactional(value = "orderTransactionManager")
    public void createOrder(OrderRequest request) {
        // 주문 DB 사용
        orderRepository.save(new Order(request));
    }
}
```

**방법 3: JTA (분산 트랜잭션)**
```java
// 여러 DB에 걸친 트랜잭션 필요 시
@Configuration
public class JtaConfig {

    @Bean
    public JtaTransactionManager jtaTransactionManager() {
        // Atomikos, Bitronix 등 사용
        return new JtaTransactionManager();
    }
}

@Service
public class ShoppingService {

    @Transactional  // JTA 사용
    public void processOrder(OrderRequest request) {
        // 1. 주문 DB에 저장
        orderRepository.save(new Order(request));

        // 2. 상품 DB 재고 감소
        productService.decreaseStock(request.getProductId());

        // 두 작업이 하나의 분산 트랜잭션으로 묶임
        // 하나라도 실패하면 모두 롤백
    }
}
```

**설정 비교**:

| 구성 | TransactionManager | 사용 시기 |
|------|------------------|---------|
| **Master-Slave** | 1개 | 같은 DB의 읽기/쓰기 분리 |
| **도메인별 DB** | 각 DB마다 1개 | 완전히 독립된 DB들 |
| **JTA** | 1개 (JTA) | 여러 DB 걸친 트랜잭션 필요 |

**실무 권장**:
- **Master-Slave**: 단일 TransactionManager + RoutingDataSource
- **도메인별 DB**: 각 DB마다 별도 TransactionManager
- **분산 트랜잭션**: 가능한 피하고, 이벤트 기반 Eventual Consistency 사용

---

### 중급 개발자 면접 질문

#### 질문 8. Master-Slave 구성에서 Slave Lag 모니터링은 어떻게 하나요?

**모범 답안**:

Slave Lag 모니터링은 **MySQL의 SHOW SLAVE STATUS 명령어와 모니터링 도구를 활용**합니다.

**1. MySQL 명령어로 확인**:
```sql
-- Slave 서버에서 실행
SHOW SLAVE STATUS\G

-- 주요 지표:
-- Seconds_Behind_Master: 0이면 정상, 1 이상이면 지연
-- Slave_IO_Running: Yes (Master로부터 binlog 수신)
-- Slave_SQL_Running: Yes (binlog 적용 중)

-- 예시 결과:
Seconds_Behind_Master: 2
Slave_IO_Running: Yes
Slave_SQL_Running: Yes
Last_Error:
```

**2. Spring Boot Actuator로 모니터링**:
```java
@Component
@RequiredArgsConstructor
public class ReplicationLagMonitor {

    private final DataSource slaveDataSource;

    @Scheduled(fixedRate = 10000)  // 10초마다 체크
    public void checkReplicationLag() {
        try (Connection conn = slaveDataSource.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SHOW SLAVE STATUS")) {

            if (rs.next()) {
                long secondsBehindMaster = rs.getLong("Seconds_Behind_Master");
                String slaveIoRunning = rs.getString("Slave_IO_Running");
                String slaveSqlRunning = rs.getString("Slave_SQL_Running");

                log.info("Replication Lag: {}초, IO: {}, SQL: {}",
                    secondsBehindMaster, slaveIoRunning, slaveSqlRunning);

                // 지연이 5초 이상이면 알림
                if (secondsBehindMaster > 5) {
                    log.error("Replication Lag 경고! {}초 지연", secondsBehindMaster);
                    sendAlert("Replication Lag: " + secondsBehindMaster + "초");
                }

                // Replication 중지 시 알림
                if (!"Yes".equals(slaveIoRunning) || !"Yes".equals(slaveSqlRunning)) {
                    log.error("Replication 중지됨! IO: {}, SQL: {}",
                        slaveIoRunning, slaveSqlRunning);
                    sendAlert("Replication 중지");
                }
            }
        } catch (SQLException e) {
            log.error("Replication 상태 확인 실패", e);
        }
    }

    private void sendAlert(String message) {
        // Slack, 이메일 등으로 알림 발송
    }
}
```

**3. Prometheus + Grafana 연동**:
```java
@Component
@RequiredArgsConstructor
public class ReplicationMetrics {

    private final DataSource slaveDataSource;
    private final MeterRegistry meterRegistry;

    @Scheduled(fixedRate = 5000)
    public void recordReplicationMetrics() {
        try (Connection conn = slaveDataSource.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SHOW SLAVE STATUS")) {

            if (rs.next()) {
                long lag = rs.getLong("Seconds_Behind_Master");

                // Prometheus 메트릭으로 기록
                meterRegistry.gauge("mysql.replication.lag", lag);

                // Grafana 대시보드에서 시각화:
                // - Lag 그래프 (시간별 추이)
                // - 알람 설정 (Lag > 5초)
            }
        } catch (SQLException e) {
            log.error("메트릭 수집 실패", e);
        }
    }
}
```

**4. MySQL Enterprise Monitor 사용**:
```
-- 상용 도구 사용 시
- MySQL Enterprise Monitor
- Percona Monitoring and Management (PMM)
- Datadog MySQL Integration

장점:
- 실시간 Lag 모니터링
- 자동 알림
- 상세 성능 분석
- 과거 데이터 조회
```

**Lag 임계값 설정**:

| Lag 시간 | 상태 | 조치 |
|---------|-----|-----|
| 0~1초 | 정상 | 모니터링 |
| 1~5초 | 주의 | 로그 기록 |
| 5~10초 | 경고 | 알림 발송 |
| 10초 이상 | 위험 | 즉시 대응 (Slave 추가 또는 최적화) |

**Lag 원인 분석**:
```java
@Component
public class LagAnalyzer {

    public void analyzeLagCause() {
        // 1. Slave 부하 확인
        // SELECT * FROM performance_schema.threads

        // 2. 대량 쓰기 확인
        // SHOW PROCESSLIST (Master)

        // 3. 네트워크 확인
        // ping, traceroute

        // 4. Binlog 크기 확인
        // SHOW BINARY LOGS
    }
}
```

**실무 Best Practice**:
- 💡 **10초 주기**로 Lag 모니터링
- 💡 **5초 이상 Lag 시 알림** 발송
- 💡 **Prometheus + Grafana**로 시각화
- 💡 **Lag 발생 시 자동 대응** (Slave 추가, 트래픽 제한 등)

---

#### 질문 9. 대규모 트래픽 환경에서 Master-Slave 구성의 한계는 무엇이고 어떻게 극복하나요?

**모범 답안**:

Master-Slave 구성의 한계는 **Master 쓰기 성능 병목**이며, **Sharding과 CQRS로 극복**합니다.

**한계점**:

**1. Master 쓰기 병목**:
```
문제:
- Master는 1대 → 쓰기 처리량 한계
- 초당 10,000 TPS 이상 어려움
- CPU/IO 병목 발생

현상:
- 쓰기 응답 시간 증가
- Replication Lag 증가 (Slave가 따라잡지 못함)
- Master CPU 90% 이상
```

**2. Single Point of Failure**:
```
문제:
- Master 장애 시 쓰기 불가
- Failover 시간 필요 (수초~수분)

현상:
- 주문, 결제 등 불가
- 서비스 중단
```

**3. 확장성 한계**:
```
문제:
- Slave 추가로 읽기는 확장 가능
- 하지만 쓰기는 확장 불가

현상:
- 읽기:쓰기 비율이 50:50이면 효과 제한적
```

**극복 방법**:

**방법 1: Sharding (쓰기 분산)**
```java
// 사용자 ID 기반 Sharding
@Configuration
public class ShardingDataSourceConfig {

    @Bean
    public DataSource routingDataSource() {
        return new ShardingRoutingDataSource();
    }
}

public class ShardingRoutingDataSource extends AbstractRoutingDataSource {

    @Override
    protected Object determineCurrentLookupKey() {
        Long userId = UserContextHolder.getCurrentUserId();

        // 사용자 ID로 Shard 결정
        int shardIndex = (int) (userId % 3);

        boolean isReadOnly = TransactionSynchronizationManager.isCurrentTransactionReadOnly();

        if (isReadOnly) {
            return "shard" + shardIndex + "_slave";
        } else {
            return "shard" + shardIndex + "_master";
        }
    }
}

// 효과:
// - Master 3대로 쓰기 처리량 3배
// - Slave 각 Shard당 3대씩 → 읽기 처리량 9배
```

**방법 2: CQRS (Command Query Responsibility Segregation)**
```java
// Command Model (쓰기)
@Service
public class OrderCommandService {

    @Transactional
    public void createOrder(OrderCommand command) {
        // Master DB에 저장
        Order order = orderRepository.save(new Order(command));

        // 이벤트 발행
        eventPublisher.publish(new OrderCreatedEvent(order));
    }
}

// Query Model (읽기)
@Service
public class OrderQueryService {

    @Transactional(readOnly = true)
    public OrderView getOrder(Long id) {
        // Read Model (ElasticSearch, MongoDB 등)에서 조회
        return orderViewRepository.findById(id).orElseThrow();
    }
}

// Event Handler (비동기 동기화)
@Component
public class OrderEventHandler {

    @EventListener
    @Async
    public void handle(OrderCreatedEvent event) {
        // Read Model 업데이트
        OrderView view = OrderView.from(event.getOrder());
        orderViewRepository.save(view);
    }
}

// 효과:
// - 쓰기: RDBMS (정합성 보장)
// - 읽기: NoSQL (빠른 조회)
// - 각각 독립적으로 확장 가능
```

**방법 3: Multi-Master Replication**
```
Master-Master 구성:
- Master 2대 이상이 서로 복제
- 쓰기를 여러 Master로 분산

장점:
- 쓰기 처리량 증가
- Failover 빠름

단점:
- 쓰기 충돌 가능 (conflict resolution 필요)
- 구성 복잡
```

**방법 4: NewSQL (TiDB, CockroachDB)**
```
특징:
- 자동 Sharding
- 수평 확장 (노드 추가로 쓰기 확장)
- 트랜잭션 보장

사용:
spring:
  datasource:
    url: jdbc:mysql://tidb-cluster:4000/testdb
    # TiDB가 자동으로 Sharding + Replication
```

**규모별 권장 구성**:

| 트래픽 규모 | 읽기 TPS | 쓰기 TPS | 권장 구성 |
|----------|---------|---------|---------|
| 소규모 | < 1,000 | < 100 | Master 1 + Slave 2 |
| 중규모 | 1,000~10,000 | 100~1,000 | Master 1 + Slave 5 |
| 대규모 | 10,000~100,000 | 1,000~10,000 | Sharding (Master 3) + Slave 각 3 |
| 초대규모 | > 100,000 | > 10,000 | CQRS + Sharding + NewSQL |

**실무 사례**:
- **배달의민족**: Sharding (지역별) + Master-Slave
- **쿠팡**: CQRS (쓰기 RDBMS, 읽기 ElasticSearch)
- **카카오톡**: Multi-Master + Sharding (사용자 ID)

---

#### 질문 10. Slave 장애 시 자동 복구 메커니즘은 어떻게 구현하나요?

**모범 답안**:

Slave 자동 복구는 **Health Check + 자동 Failover + 알림**으로 구현합니다.

**전체 아키텍처**:
```
1. Health Check (5초 주기)
   → Slave 상태 확인

2. 장애 감지
   → 사용 가능한 Slave 목록에서 제외

3. 자동 Failover
   → 나머지 Slave로 트래픽 분산

4. 알림 발송
   → 개발팀에 Slack/이메일 알림

5. 자동 복구 시도
   → Slave 재시작 또는 재연결

6. 복구 확인
   → 정상 Slave 목록에 재추가
```

**구현 코드**:

**1. Health Check Scheduler**:
```java
@Component
@RequiredArgsConstructor
@Slf4j
public class SlaveHealthChecker {

    private final Map<String, DataSource> slaveDataSources;
    private final Set<String> unavailableSlaves = ConcurrentHashMap.newKeySet();
    private final AlertService alertService;

    @Scheduled(fixedRate = 5000)  // 5초마다 체크
    public void checkAllSlaves() {
        for (Map.Entry<String, DataSource> entry : slaveDataSources.entrySet()) {
            String slaveName = entry.getKey();
            DataSource dataSource = entry.getValue();

            if (isHealthy(dataSource)) {
                handleHealthy(slaveName);
            } else {
                handleUnhealthy(slaveName);
            }
        }
    }

    private boolean isHealthy(DataSource dataSource) {
        try (Connection conn = dataSource.getConnection()) {
            // 2초 내 응답 확인
            if (conn.isValid(2)) {
                // 간단한 쿼리 실행
                try (Statement stmt = conn.createStatement();
                     ResultSet rs = stmt.executeQuery("SELECT 1")) {
                    return rs.next();
                }
            }
            return false;
        } catch (Exception e) {
            log.error("Health check 실패", e);
            return false;
        }
    }

    private void handleHealthy(String slaveName) {
        if (unavailableSlaves.remove(slaveName)) {
            log.info("✅ {} 복구됨!", slaveName);
            alertService.sendRecoveryAlert(slaveName);
        }
    }

    private void handleUnhealthy(String slaveName) {
        if (unavailableSlaves.add(slaveName)) {
            log.error("❌ {} 장애 감지!", slaveName);
            alertService.sendFailureAlert(slaveName);
            tryAutoRecover(slaveName);
        }
    }

    private void tryAutoRecover(String slaveName) {
        // 자동 복구 시도 (예: 재연결)
        log.info("🔧 {} 자동 복구 시도...", slaveName);

        CompletableFuture.runAsync(() -> {
            try {
                Thread.sleep(10000);  // 10초 대기
                // 재연결 로직 (예: HikariCP 재시작)
                log.info("🔄 {} 재연결 시도", slaveName);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
    }

    public Set<String> getUnavailableSlaves() {
        return Collections.unmodifiableSet(unavailableSlaves);
    }
}
```

**2. Routing DataSource 연동**:
```java
@Slf4j
@RequiredArgsConstructor
public class LoadBalancedRoutingDataSource extends AbstractRoutingDataSource {

    private static final List<String> SLAVES = List.of("slave1", "slave2", "slave3");
    private final SlaveHealthChecker healthChecker;
    private final AtomicInteger counter = new AtomicInteger(0);

    @Override
    protected Object determineCurrentLookupKey() {
        boolean isReadOnly = TransactionSynchronizationManager.isCurrentTransactionReadOnly();

        if (isReadOnly) {
            // 정상 Slave 목록
            List<String> availableSlaves = SLAVES.stream()
                .filter(slave -> !healthChecker.getUnavailableSlaves().contains(slave))
                .collect(Collectors.toList());

            if (availableSlaves.isEmpty()) {
                log.warn("⚠️ 모든 Slave 장애, Master로 폴백");
                return "master";
            }

            // 라운드 로빈 선택
            int index = Math.abs(counter.getAndIncrement() % availableSlaves.size());
            String selectedSlave = availableSlaves.get(index);

            log.debug("📖 읽기 요청 → {} (가용: {}개)", selectedSlave, availableSlaves.size());

            return selectedSlave;
        }

        log.debug("✍️ 쓰기 요청 → master");
        return "master";
    }
}
```

**3. Alert Service**:
```java
@Service
@RequiredArgsConstructor
@Slf4j
public class AlertService {

    private final WebClient webClient;  // Slack Webhook

    public void sendFailureAlert(String slaveName) {
        String message = String.format(
            "🚨 *Database Alert*\n" +
            "Slave: `%s`\n" +
            "Status: ❌ DOWN\n" +
            "Time: %s\n" +
            "Action: 자동 Failover 실행됨",
            slaveName,
            LocalDateTime.now()
        );

        sendToSlack(message);
        sendEmail(message);
    }

    public void sendRecoveryAlert(String slaveName) {
        String message = String.format(
            "✅ *Database Recovery*\n" +
            "Slave: `%s`\n" +
            "Status: ✅ UP\n" +
            "Time: %s",
            slaveName,
            LocalDateTime.now()
        );

        sendToSlack(message);
    }

    private void sendToSlack(String message) {
        webClient.post()
            .uri("https://hooks.slack.com/services/YOUR/WEBHOOK/URL")
            .bodyValue(Map.of("text", message))
            .retrieve()
            .bodyToMono(Void.class)
            .subscribe();
    }

    private void sendEmail(String message) {
        // 이메일 발송 로직
    }
}
```

**4. 모니터링 대시보드**:
```java
@RestController
@RequiredArgsConstructor
public class HealthController {

    private final SlaveHealthChecker healthChecker;
    private final LoadBalancedRoutingDataSource routingDataSource;

    @GetMapping("/health/slaves")
    public ResponseEntity<SlaveHealthStatus> getSlaveHealth() {
        List<String> available = List.of("slave1", "slave2", "slave3").stream()
            .filter(slave -> !healthChecker.getUnavailableSlaves().contains(slave))
            .collect(Collectors.toList());

        List<String> unavailable = new ArrayList<>(healthChecker.getUnavailableSlaves());

        SlaveHealthStatus status = SlaveHealthStatus.builder()
            .availableSlaves(available)
            .unavailableSlaves(unavailable)
            .totalSlaves(3)
            .healthyCount(available.size())
            .checkTime(LocalDateTime.now())
            .build();

        return ResponseEntity.ok(status);
    }
}

// 응답 예시:
// {
//   "availableSlaves": ["slave1", "slave3"],
//   "unavailableSlaves": ["slave2"],
//   "totalSlaves": 3,
//   "healthyCount": 2,
//   "checkTime": "2024-01-15T10:30:00"
// }
```

**5. Kubernetes Health Check 연동** (선택):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql-slave
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        livenessProbe:  # 장애 감지
          exec:
            command:
            - /bin/sh
            - -c
            - "mysqladmin ping -h localhost"
          initialDelaySeconds: 30
          periodSeconds: 10
          failureThreshold: 3
        readinessProbe:  # 트래픽 차단
          exec:
            command:
            - /bin/sh
            - -c
            - "mysql -h localhost -e 'SELECT 1'"
          initialDelaySeconds: 5
          periodSeconds: 5
```

**복구 시나리오**:
```
1. slave2 장애 발생 (10:30:00)
   → Health Check 실패
   → unavailableSlaves에 추가
   → Slack 알림: "slave2 DOWN"

2. 트래픽 자동 전환 (10:30:05)
   → slave1, slave3으로만 분산
   → 각 Slave 부하 33% → 50% 증가

3. 자동 복구 시도 (10:30:10)
   → 재연결 시도
   → 또는 Kubernetes가 Pod 재시작

4. slave2 복구됨 (10:32:00)
   → Health Check 성공
   → unavailableSlaves에서 제거
   → Slack 알림: "slave2 UP"

5. 트래픽 재분산 (10:32:05)
   → slave1, slave2, slave3로 분산
   → 각 Slave 부하 50% → 33% 감소
```

**실무 Best Practice**:
- 💡 **Health Check 주기: 5~10초**
- 💡 **실패 3회 이상 시 장애로 판정** (false positive 방지)
- 💡 **자동 Failover + 알림 필수**
- 💡 **Kubernetes/Docker Health Check 활용**
- 💡 **복구 후 자동 트래픽 재분산**

---

#### 질문 11. 분산 트랜잭션이 필요한 경우 어떻게 처리하나요?

**모범 답안**:

분산 트랜잭션은 **가능한 피하고, 이벤트 기반 Eventual Consistency를 사용**합니다.

**문제 상황**:
```java
// 여러 DB에 걸친 트랜잭션이 필요한 경우
@Service
public class OrderService {

    private final OrderRepository orderRepository;      // 주문 DB
    private final ProductRepository productRepository;  // 상품 DB
    private final PaymentRepository paymentRepository;  // 결제 DB

    @Transactional
    public void processOrder(OrderRequest request) {
        // 1. 주문 생성 (주문 DB)
        Order order = orderRepository.save(new Order(request));

        // 2. 재고 감소 (상품 DB)
        productRepository.decreaseStock(request.getProductId());

        // 3. 결제 처리 (결제 DB)
        paymentRepository.save(new Payment(order));

        // 문제: 3개 DB에 걸친 트랜잭션
        // → 하나라도 실패하면 모두 롤백되어야 함
        // → 하지만 각 DB가 독립적이라 불가능!
    }
}
```

**해결 방법**:

**방법 1: Saga 패턴 (이벤트 기반)**
```java
// 각 단계를 독립적인 트랜잭션으로 처리
// 실패 시 보상 트랜잭션(Compensating Transaction) 실행

@Service
@RequiredArgsConstructor
public class OrderSagaOrchestrator {

    private final OrderService orderService;
    private final ProductService productService;
    private final PaymentService paymentService;
    private final ApplicationEventPublisher eventPublisher;

    public void processOrder(OrderRequest request) {
        Long orderId = null;
        try {
            // Step 1: 주문 생성 (주문 DB)
            orderId = orderService.createOrder(request);
            eventPublisher.publishEvent(new OrderCreatedEvent(orderId));

            // Step 2: 재고 감소 (상품 DB)
            productService.decreaseStock(request.getProductId(), request.getQuantity());
            eventPublisher.publishEvent(new StockDecreasedEvent(orderId, request.getProductId()));

            // Step 3: 결제 처리 (결제 DB)
            paymentService.processPayment(orderId, request.getAmount());
            eventPublisher.publishEvent(new PaymentCompletedEvent(orderId));

            // 모든 단계 성공
            orderService.completeOrder(orderId);

        } catch (Exception e) {
            log.error("주문 처리 실패, 롤백 시작", e);

            // 보상 트랜잭션 (역순으로 롤백)
            if (orderId != null) {
                try {
                    paymentService.cancelPayment(orderId);         // 결제 취소
                    productService.increaseStock(request.getProductId(), request.getQuantity());  // 재고 복구
                    orderService.cancelOrder(orderId);             // 주문 취소
                } catch (Exception rollbackError) {
                    log.error("롤백 실패! 수동 대응 필요", rollbackError);
                    // 수동 대응이 필요한 경우 알림 발송
                }
            }

            throw new OrderProcessingException("주문 처리 실패", e);
        }
    }
}

// 각 서비스는 독립적인 트랜잭션
@Service
public class OrderService {

    @Transactional(value = "orderTransactionManager")
    public Long createOrder(OrderRequest request) {
        Order order = orderRepository.save(new Order(request));
        return order.getId();
    }

    @Transactional(value = "orderTransactionManager")
    public void cancelOrder(Long orderId) {
        Order order = orderRepository.findById(orderId).orElseThrow();
        order.cancel();
    }
}

@Service
public class ProductService {

    @Transactional(value = "productTransactionManager")
    public void decreaseStock(Long productId, int quantity) {
        Product product = productRepository.findById(productId).orElseThrow();
        product.decreaseStock(quantity);
    }

    @Transactional(value = "productTransactionManager")
    public void increaseStock(Long productId, int quantity) {
        Product product = productRepository.findById(productId).orElseThrow();
        product.increaseStock(quantity);
    }
}
```

**방법 2: 이벤트 소싱 + CQRS**
```java
// 이벤트를 저장하고 이벤트를 재생하여 상태 복원

@Service
@RequiredArgsConstructor
public class OrderEventHandler {

    private final EventStore eventStore;

    @EventListener
    @Async
    @Transactional(value = "productTransactionManager")
    public void handleOrderCreated(OrderCreatedEvent event) {
        // 비동기로 상품 재고 감소
        try {
            productService.decreaseStock(event.getProductId(), event.getQuantity());
            eventStore.save(new StockDecreasedEvent(event.getOrderId()));
        } catch (Exception e) {
            // 실패 시 보상 이벤트 발행
            eventStore.save(new StockDecreaseFailed(event.getOrderId(), e.getMessage()));
        }
    }

    @EventListener
    @Async
    @Transactional(value = "paymentTransactionManager")
    public void handleStockDecreased(StockDecreasedEvent event) {
        // 비동기로 결제 처리
        try {
            paymentService.processPayment(event.getOrderId());
            eventStore.save(new PaymentCompletedEvent(event.getOrderId()));
        } catch (Exception e) {
            // 실패 시 보상 이벤트 발행
            eventStore.save(new PaymentFailed(event.getOrderId(), e.getMessage()));
        }
    }

    @EventListener
    @Async
    @Transactional(value = "orderTransactionManager")
    public void handlePaymentCompleted(PaymentCompletedEvent event) {
        // 주문 완료 처리
        orderService.completeOrder(event.getOrderId());
    }

    @EventListener
    @Async
    public void handleFailure(FailureEvent event) {
        // 실패 시 보상 트랜잭션 실행
        compensationService.compensate(event);
    }
}
```

**방법 3: JTA (분산 트랜잭션) - 비권장**
```java
// JTA (Java Transaction API) 사용
// 2-Phase Commit Protocol

@Configuration
public class JtaConfig {

    @Bean
    public JtaTransactionManager jtaTransactionManager() {
        // Atomikos, Bitronix 등 사용
        AtomikosJtaPlatform jtaPlatform = new AtomikosJtaPlatform();
        return new JtaTransactionManager(jtaPlatform);
    }

    @Bean
    public DataSource orderDataSource() {
        AtomikosDataSourceBean ds = new AtomikosDataSourceBean();
        ds.setXaDataSourceClassName("com.mysql.cj.jdbc.MysqlXADataSource");
        ds.setUniqueResourceName("orderDS");
        // ... 설정
        return ds;
    }

    @Bean
    public DataSource productDataSource() {
        AtomikosDataSourceBean ds = new AtomikosDataSourceBean();
        ds.setXaDataSourceClassName("com.mysql.cj.jdbc.MysqlXADataSource");
        ds.setUniqueResourceName("productDS");
        // ... 설정
        return ds;
    }
}

@Service
public class OrderService {

    @Transactional  // JTA 트랜잭션
    public void processOrder(OrderRequest request) {
        // 1. 주문 생성 (주문 DB)
        orderRepository.save(new Order(request));

        // 2. 재고 감소 (상품 DB)
        productRepository.decreaseStock(request.getProductId());

        // JTA가 2-Phase Commit으로 보장
        // Phase 1: 모든 DB에 prepare
        // Phase 2: 모두 성공하면 commit, 하나라도 실패하면 rollback
    }
}

// 단점:
// - 성능 저하 (2-Phase Commit 오버헤드)
// - 복잡도 증가
// - 확장성 제한
// - 일부 DB는 XA 트랜잭션 미지원
```

**방식 비교**:

| 방식 | 일관성 | 성능 | 복잡도 | 권장 |
|------|-------|-----|-------|-----|
| **Saga 패턴** | Eventual | 높음 | 중간 | ✅ 권장 |
| **이벤트 소싱** | Eventual | 높음 | 높음 | ✅ 대규모 |
| **JTA** | Strong | 낮음 | 높음 | ❌ 비권장 |

**실무 사례**:
- **배달의민족**: Saga 패턴 (주문 → 결제 → 배달)
- **쿠팡**: 이벤트 소싱 (주문 이벤트 저장)
- **토스**: Eventual Consistency (비동기 이벤트)

**실무 Best Practice**:
- 💡 **가능한 분산 트랜잭션 피하기** (단일 DB 사용)
- 💡 **Saga 패턴 활용** (이벤트 + 보상 트랜잭션)
- 💡 **Eventual Consistency 수용** (약간의 지연 허용)
- 💡 **JTA는 최후의 수단** (성능/복잡도 문제)

---

#### 질문 12. Master-Slave 구성에서 데이터 정합성은 어떻게 보장하나요?

**모범 답안**:

데이터 정합성은 **Replication 메커니즘과 애플리케이션 레벨 전략**으로 보장합니다.

**정합성 수준**:

**1. Strong Consistency (강한 일관성)**:
```
정의: 쓰기 직후 모든 읽기에서 최신 값 보장

구현: Master에서만 읽기/쓰기
→ Master-Slave 사용 안 함

사용 사례:
- 금융 거래 (잔액 조회)
- 결제 처리
- 재고 관리 (중요 상품)
```

**2. Eventual Consistency (최종 일관성)**:
```
정의: 일정 시간 후 모든 복제본이 동일한 값 보장
      (Replication Lag 허용)

구현: Master-Slave 사용

사용 사례:
- SNS 피드 조회
- 상품 목록 조회
- 조회수, 좋아요 수
```

**보장 전략**:

**전략 1: 중요한 데이터는 Master에서 조회**:
```java
@Service
public class PaymentService {

    // 결제 정보는 Strong Consistency 필요
    @Transactional(readOnly = false)  // Master 사용
    public BigDecimal getBalance(Long userId) {
        // Master에서 조회하여 최신 잔액 보장
        return userRepository.findById(userId)
            .orElseThrow()
            .getBalance();
    }

    @Transactional
    public void withdraw(Long userId, BigDecimal amount) {
        // Master에서 조회 + 수정
        User user = userRepository.findById(userId).orElseThrow();

        if (user.getBalance().compareTo(amount) < 0) {
            throw new InsufficientBalanceException();
        }

        user.decreaseBalance(amount);
    }
}
```

**전략 2: 일반 데이터는 Eventual Consistency 허용**:
```java
@Service
public class PostService {

    // 게시글 조회는 약간의 지연 허용
    @Transactional(readOnly = true)  // Slave 사용
    public PostResponse getPost(Long postId) {
        // Slave에서 조회
        // 최신 좋아요/댓글 수가 약간 지연될 수 있음 (허용)
        Post post = postRepository.findById(postId).orElseThrow();
        return PostResponse.from(post);
    }

    @Transactional
    public PostResponse createPost(PostRequest request) {
        Post post = postRepository.save(new Post(request));

        // 생성한 엔티티를 바로 반환 (Replication Lag 방지)
        return PostResponse.from(post);
    }
}
```

**전략 3: Write-Through Cache**:
```java
@Service
public class ProductService {

    @Transactional
    @CacheEvict(value = "products", key = "#productId")
    public void updatePrice(Long productId, BigDecimal newPrice) {
        // Master에 업데이트
        Product product = productRepository.findById(productId).orElseThrow();
        product.updatePrice(newPrice);

        // 캐시 무효화 → 다음 조회 시 최신 데이터
    }

    @Transactional(readOnly = true)
    @Cacheable(value = "products", key = "#productId")
    public Product getProduct(Long productId) {
        // 캐시에서 조회 (빠름)
        // 캐시 없으면 Slave에서 조회
        return productRepository.findById(productId).orElseThrow();
    }
}
```

**전략 4: Read-Your-Writes Consistency**:
```java
// 사용자가 쓴 데이터는 본인이 바로 조회 가능하도록

@Service
public class CommentService {

    @Transactional
    public CommentResponse createComment(CommentRequest request) {
        Comment comment = commentRepository.save(new Comment(request));

        // 쓴 데이터를 즉시 반환 (Master에서)
        // → 사용자는 본인 댓글을 바로 볼 수 있음
        return CommentResponse.from(comment);
    }

    @Transactional(readOnly = true)
    public List<CommentResponse> getComments(Long postId, Long currentUserId) {
        // 다른 사용자 댓글은 Slave에서 조회 (약간 지연 허용)
        List<Comment> comments = commentRepository.findByPostId(postId);

        // 현재 사용자가 방금 쓴 댓글은 포함되어 있음 (Write-Through)
        return comments.stream()
            .map(CommentResponse::from)
            .collect(Collectors.toList());
    }
}
```

**전략 5: Version 관리 (Optimistic Lock)**:
```java
@Entity
public class Product {

    @Id
    private Long id;

    private String name;
    private BigDecimal price;

    @Version
    private Long version;  // 버전 관리

    // Slave에서 조회한 데이터로 업데이트 시도 시
    // 버전이 다르면 예외 발생 → 재시도
}

@Service
public class ProductService {

    @Transactional
    @Retryable(maxAttempts = 3, value = OptimisticLockException.class)
    public void updateProduct(Long productId, ProductUpdateRequest request) {
        // Slave에서 조회한 데이터로 업데이트 시도
        Product product = productRepository.findById(productId).orElseThrow();
        product.update(request);

        // 버전이 다르면 OptimisticLockException 발생 → 재시도
    }
}
```

**정합성 보장 레벨**:

| 데이터 종류 | 정합성 요구 | 전략 | DataSource |
|----------|----------|-----|-----------|
| **결제/잔액** | Strong | Master에서만 조회 | Master |
| **재고 (중요)** | Strong | Master + Pessimistic Lock | Master |
| **주문 정보** | Strong | 생성 후 바로 반환 | Master |
| **상품 목록** | Eventual | Slave 조회 + 캐시 | Slave |
| **SNS 피드** | Eventual | Slave 조회 | Slave |
| **조회수** | Eventual | Slave 조회 + 비동기 업데이트 | Slave |

**Replication 메커니즘**:
```sql
-- MySQL Replication 설정

-- Master 설정
[mysqld]
server-id=1
log-bin=mysql-bin
binlog-format=ROW  # 안전한 복제

-- Slave 설정
[mysqld]
server-id=2
relay-log=mysql-relay-bin
read-only=1  # 읽기 전용

-- Replication 시작
CHANGE MASTER TO
  MASTER_HOST='master-host',
  MASTER_USER='replication',
  MASTER_PASSWORD='password',
  MASTER_LOG_FILE='mysql-bin.000001',
  MASTER_LOG_POS=107;
START SLAVE;
```

**정합성 모니터링**:
```java
@Component
public class ConsistencyMonitor {

    @Scheduled(fixedRate = 60000)
    public void checkConsistency() {
        // Master와 Slave 데이터 비교
        long masterCount = masterRepository.count();
        long slaveCount = slaveRepository.count();

        if (masterCount != slaveCount) {
            log.warn("데이터 불일치! Master: {}, Slave: {}",
                masterCount, slaveCount);
        }
    }
}
```

**실무 Best Practice**:
- 💡 **중요 데이터는 Master에서 조회** (결제, 재고 등)
- 💡 **일반 데이터는 Eventual Consistency 허용**
- 💡 **Write-Through 패턴** (쓴 데이터 즉시 반환)
- 💡 **캐시 활용**으로 Replication Lag 완화
- 💡 **Optimistic Lock**으로 동시성 제어

---

## 📋 핵심 정리

### Master-Slave Replication 구성 체크리스트

#### ✅ 필수 구성
- [ ] Master DataSource 설정
- [ ] Slave DataSource 설정 (1개 이상)
- [ ] AbstractRoutingDataSource 구현
- [ ] LazyConnectionDataSourceProxy 적용
- [ ] @Transactional(readOnly = true/false) 구분

#### ⚙️ 최적화
- [ ] HikariCP 커넥션 풀 크기 최적화
  - Master: 쓰기 비율에 맞춤 (보통 10~20)
  - Slave: 읽기 비율에 맞춤 (보통 30~50)
- [ ] 여러 Slave로 로드 밸런싱 (라운드 로빈)
- [ ] Health Check 구현 (5~10초 주기)
- [ ] Failover 메커니즘 구현

#### 🔍 모니터링
- [ ] Replication Lag 모니터링
- [ ] Slave 상태 확인 (SHOW SLAVE STATUS)
- [ ] 커넥션 풀 사용률 모니터링
- [ ] 장애 알림 설정 (Slack, 이메일)

#### ⚠️ 주의사항
- [ ] Replication Lag 대응 (생성 후 즉시 반환)
- [ ] 중요 데이터는 Master에서 조회
- [ ] 트랜잭션 전파 레벨 이해
- [ ] Self-invocation 문제 인지

### 핵심 개념 요약

| 개념 | 설명 | 핵심 포인트 |
|------|------|----------|
| **Master-Slave** | 쓰기는 Master, 읽기는 Slave로 분리 | 읽기 처리량 증가, Master 부하 감소 |
| **AbstractRoutingDataSource** | readOnly 플래그로 Master/Slave 선택 | determineCurrentLookupKey() 구현 |
| **LazyConnectionDataSourceProxy** | Connection 획득 지연 | readOnly 플래그가 올바르게 설정되도록 |
| **Replication Lag** | Master→Slave 복제 지연 (0.5~1초) | 생성 직후 조회 시 주의 |
| **Health Check** | Slave 상태 주기적 확인 | 장애 시 자동 Failover |
| **HikariCP** | 커넥션 풀 관리 | 읽기:쓰기 비율에 맞춘 설정 |

### 성능 지표

#### Master-Slave 도입 효과

| 지표 | Before | After | 개선율 |
|------|--------|-------|-------|
| **읽기 처리량** | 5,000 QPS | 30,000 QPS | **500%↑** |
| **평균 응답 시간** | 500ms | 50ms | **90%↓** |
| **CPU 사용률** | 90% (병목) | 40% (여유) | **55%↓** |
| **가용성** | 99% | 99.95% | **0.95%p↑** |

#### 트래픽별 권장 구성

| 일일 사용자 | 읽기 QPS | 쓰기 TPS | Master | Slave | 총 Pool Size |
|----------|---------|---------|--------|-------|------------|
| **1,000명** | < 100 | < 10 | 1대 (10) | 1대 (20) | 30 |
| **10,000명** | 100~1,000 | 10~100 | 1대 (10) | 2대 (각 30) | 70 |
| **100,000명** | 1,000~10,000 | 100~1,000 | 1대 (20) | 3대 (각 30) | 110 |
| **1,000,000명** | > 10,000 | > 1,000 | 2대 (각 20) | 5대 (각 30) | 190 |

### 일반적인 실수와 해결책

| 실수 | 문제 | 해결책 |
|------|-----|-------|
| **LazyProxy 미사용** | readOnly 동작 안 함 | LazyConnectionDataSourceProxy 필수 |
| **생성 직후 조회** | Replication Lag | 같은 트랜잭션에서 처리 또는 바로 반환 |
| **동일한 풀 크기** | 읽기 병목 | 읽기:쓰기 비율에 맞춰 설정 |
| **Health Check 없음** | Slave 장애 시 서비스 중단 | 5~10초 주기 Health Check |
| **통계 쿼리 격리 안 함** | 일반 조회 느려짐 | 통계 전용 Slave 분리 |

---

## 🎯 다음 단계

### 학습한 내용
✅ Master-Slave Replication 개념과 원리
✅ AbstractRoutingDataSource로 읽기/쓰기 분리
✅ LazyConnectionDataSourceProxy의 필요성
✅ Replication Lag 대응 전략
✅ Health Check와 Failover 구현
✅ HikariCP 커넥션 풀 최적화
✅ 실전 프로젝트: SNS 시스템 구현

### 다음 학습 주제
1. **샤딩 (Sharding)**: 쓰기 확장을 위한 수평 분할
2. **캐싱 전략**: Redis, Memcached를 활용한 성능 최적화
3. **NoSQL 통합**: MongoDB, ElasticSearch 연동
4. **이벤트 기반 아키텍처**: Kafka, RabbitMQ를 활용한 비동기 처리

### 추가 학습 자료
- **공식 문서**:
  - [MySQL Replication](https://dev.mysql.com/doc/refman/8.0/en/replication.html)
  - [HikariCP Documentation](https://github.com/brettwooldridge/HikariCP)
  - [Spring Transaction Management](https://docs.spring.io/spring-framework/docs/current/reference/html/data-access.html#transaction)

- **추천 도서**:
  - "가상 면접 사례로 배우는 대규모 시스템 설계 기초" (데이터베이스 확장 파트)
  - "Real MySQL 8.0" (Replication 파트)

---

**🎓 축하합니다!**

22장 "다중 데이터소스와 Master-Slave 구성"을 완료했습니다!

이제 여러분은:
- ✅ 대규모 트래픽을 처리할 수 있는 DB 구조를 설계할 수 있습니다
- ✅ 읽기/쓰기 분리로 성능을 10배 향상시킬 수 있습니다
- ✅ Slave 장애에도 안정적으로 동작하는 시스템을 구축할 수 있습니다
- ✅ 실무에서 바로 적용 가능한 Master-Slave 구성을 이해했습니다

다음 장에서는 더 고급 주제인 **샤딩**과 **분산 데이터베이스**를 다룰 예정입니다!

---

<div align="center">

**📚 Spring MVC 마스터 과정 - Chapter 22 완료! 📚**

[← 이전: 21장 트랜잭션 관리](SpringMVC-Part13-21-Transaction-Management.md) | [다음: 23장 샤딩과 분산 DB →](SpringMVC-Part15-23-Sharding.md)

</div>
