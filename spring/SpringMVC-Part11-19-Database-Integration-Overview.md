# 19장: 데이터베이스 연동 개요

> **학습 목표**: Spring에서 데이터베이스를 연동하는 다양한 방법을 이해하고, 각 기술의 특징과 사용 사례를 비교할 수 있습니다.

**⏱️ 예상 학습 시간**: 2-3시간
**난이도**: ⭐⭐⭐☆☆ (3개/5개)

---

## 📚 목차
- [왜 데이터베이스 연동이 필요한가](#왜-데이터베이스-연동이-필요한가)
- [실생활 비유로 이해하기](#실생활-비유로-이해하기)
- [핵심 개념](#핵심-개념)
- [기본 실습](#기본-실습)
- [실무 활용 사례](#실무-활용-사례)
- [주니어 시나리오](#주니어-시나리오)
- [실전 프로젝트](#실전-프로젝트)
- [FAQ](#faq)
- [면접 질문](#면접-질문)
- [핵심 정리](#핵심-정리)

---

## 🤔 왜 데이터베이스 연동이 필요한가?

### 실무 배경

**모든 애플리케이션의 핵심은 데이터**:
- 회원 정보, 주문 내역, 상품 데이터 등 영구 저장 필요
- 서버 재시작 후에도 데이터 유지
- 여러 사용자가 동시에 안전하게 접근
- 빠른 검색, 정렬, 집계 기능
- 데이터 무결성 보장 (트랜잭션)

### ❌ 데이터베이스 없이 메모리만 사용하면 발생하는 문제

```
문제 1: 데이터 소실
- 증상: 서버 재시작 시 모든 데이터 사라짐
- 영향: 회원 정보, 주문 내역 모두 삭제
- 비용: 비즈니스 중단

문제 2: 동시성 문제
- 증상: 여러 사용자가 동시에 수정 시 충돌
- 영향: 데이터 불일치, 재고 오류
- 비용: 고객 불만, 금전적 손실

문제 3: 확장성 부족
- 증상: 메모리 한계로 데이터 저장 제한
- 영향: 서비스 성장 불가능
- 비용: 기회 비용

문제 4: 검색 성능 저하
- 증상: 데이터 많아지면 선형 검색으로 느려짐
- 영향: 사용자 경험 악화
- 비용: 이탈률 증가
```

### ✅ Spring의 데이터베이스 연동을 올바르게 사용하면

```
해결책 1: 영구 저장소
- 방법: RDBMS (MySQL, PostgreSQL, Oracle)
- 효과: 데이터 영구 보존
- 절감: 데이터 손실 위험 0%

해결책 2: 트랜잭션 지원
- 방법: ACID 보장
- 효과: 데이터 무결성 유지
- 절감: 데이터 불일치 99% 감소

해결책 3: 고성능 검색
- 방법: 인덱스, 쿼리 최적화
- 효과: 밀리초 단위 응답
- 절감: 검색 시간 99% 단축

해결책 4: 동시성 제어
- 방법: 락, 격리 수준
- 효과: 안전한 동시 접근
- 절감: 충돌 98% 감소
```

### 📊 수치로 보는 효과

| 지표 | Before (메모리) | After (DB) | 개선율 |
|------|----------------|-----------|--------|
| 데이터 손실 위험 | 100% (재시작 시) | 0% | **100%↓** |
| 동시 사용자 처리 | 100명 | 10,000명 | **100배↑** |
| 검색 속도 (100만건) | 10초 | 10ms | **1000배↑** |
| 데이터 용량 | 8GB (메모리) | 무제한 (디스크) | **무한대** |

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 도서관 vs 책상

**상황**: 책을 보관하는 두 가지 방법

```
┌──────────────┬─────────────────┬──────────────────┐
│ 도서관       │ 데이터베이스    │ 역할             │
├──────────────┼─────────────────┼──────────────────┤
│ 책           │ 데이터 (Row)    │ 저장 단위        │
│ 책장         │ 테이블 (Table)  │ 데이터 분류      │
│ 카탈로그     │ 인덱스 (Index)  │ 빠른 검색        │
│ 사서         │ DBMS            │ 관리자           │
│ 대출 기록    │ 트랜잭션 로그   │ 변경 이력        │
└──────────────┴─────────────────┴──────────────────┘

책상 (메모리):
✅ 빠른 접근
❌ 한정된 공간
❌ 정리 안 하면 분실

도서관 (데이터베이스):
✅ 무제한 보관
✅ 체계적 분류
✅ 영구 보존
✅ 여러 사람 동시 이용
```

**코드로 보면**:
```java
// ❌ 메모리 (책상)
Map<Long, User> users = new HashMap<>();  // 서버 재시작 시 소실

// ✅ 데이터베이스 (도서관)
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    // 영구 저장, 빠른 검색, 동시성 지원
}
```

---

### 비유 2: 은행 금고 vs 지갑

**상황**: 돈을 보관하는 두 가지 방법

```
┌──────────────┬─────────────────┬──────────────────┐
│ 은행         │ 데이터베이스    │ 역할             │
├──────────────┼─────────────────┼──────────────────┤
│ 계좌         │ 레코드 (Record) │ 개별 데이터      │
│ 입출금 내역  │ 트랜잭션        │ 변경 작업        │
│ 잔액 확인    │ SELECT 쿼리     │ 조회             │
│ 이체         │ UPDATE 쿼리     │ 수정             │
│ CCTV/보안    │ 격리 수준/락    │ 동시성 제어      │
└──────────────┴─────────────────┴──────────────────┘
```

**예시 (은행 이체)**:
```java
@Transactional  // 은행의 "입출금 동시 처리"와 동일
public void transfer(Long fromId, Long toId, BigDecimal amount) {
    // 1. 출금 계좌에서 차감
    Account from = accountRepository.findById(fromId).orElseThrow();
    from.withdraw(amount);

    // 2. 입금 계좌에 추가
    Account to = accountRepository.findById(toId).orElseThrow();
    to.deposit(amount);

    // 둘 다 성공하거나, 둘 다 실패 (All or Nothing)
    // 중간에 실패하면 자동 롤백 (입금만 되는 일 없음!)
}
```

---

### 비유 3: 백과사전 vs 메모장

**상황**: 정보를 기록하고 찾는 두 가지 방법

```
┌──────────────┬─────────────────┬──────────────────┐
│ 백과사전     │ RDBMS           │ 역할             │
├──────────────┼─────────────────┼──────────────────┤
│ 가나다순 정렬│ ORDER BY        │ 정렬             │
│ 색인         │ INDEX           │ 빠른 검색        │
│ 교차 참조    │ JOIN            │ 관계 연결        │
│ 분류 체계    │ Schema          │ 데이터 구조      │
└──────────────┴─────────────────┴──────────────────┘
```

**예시 (검색)**:
```sql
-- ❌ 메모장: 처음부터 끝까지 읽기 (선형 검색, O(n))
-- 1,000,000개 중 1개 찾는데 1초 소요

-- ✅ 백과사전: 색인으로 바로 찾기 (인덱스 검색, O(log n))
SELECT * FROM users WHERE email = 'user@example.com';
-- 1,000,000개 중 1개 찾는데 10ms 소요
```

---

### 비유 4: 레고 블록

**상황**: Spring의 다양한 데이터베이스 연동 기술

```
┌──────────────┬─────────────────┬──────────────────┐
│ 레고 세트    │ Spring 기술     │ 특징             │
├──────────────┼─────────────────┼──────────────────┤
│ 기본 블록    │ JDBC            │ 가장 기초, 유연  │
│ 테크닉       │ Spring JDBC     │ JDBC 간소화      │
│ 레고 듀플로  │ JPA/Hibernate   │ 쉬운 사용        │
│ 레고 마인드  │ QueryDSL        │ 타입 안전 쿼리   │
│ 커스텀       │ MyBatis         │ SQL 직접 제어    │
└──────────────┴─────────────────┴──────────────────┘

필요에 따라 선택:
- 단순한 건물 (간단한 CRUD) → JPA
- 복잡한 구조물 (복잡한 쿼리) → MyBatis
- 정밀 제어 (성능 최적화) → JDBC
```

---

### 비유 5: 음식점 주문 시스템

**상황**: 주문을 처리하는 과정

```
┌──────────────┬─────────────────┬──────────────────┐
│ 음식점       │ Spring DB       │ 역할             │
├──────────────┼─────────────────┼──────────────────┤
│ 메뉴판       │ Entity/DTO      │ 데이터 구조      │
│ 주문서       │ SQL 쿼리        │ 요청             │
│ 주방         │ DBMS            │ 처리 엔진        │
│ 웨이터       │ Repository      │ 중개자           │
│ 영수증       │ Result Set      │ 결과             │
└──────────────┴─────────────────┴──────────────────┘
```

**코드로 보면**:
```java
// 고객: Controller
@PostMapping("/orders")
public Order createOrder(@RequestBody OrderRequest request) {
    // 웨이터: Service
    return orderService.createOrder(request);
}

// 웨이터: Service
@Transactional
public Order createOrder(OrderRequest request) {
    // 주문서 작성: Entity 생성
    Order order = new Order(request);

    // 주방에 전달: Repository 호출
    return orderRepository.save(order);
}

// 주방: Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    // DBMS가 실제 작업 수행
}
```

---

## 📖 핵심 개념

### 1️⃣ 초보자 수준 설명

**데이터베이스 연동이란?**

Spring 애플리케이션에서 데이터베이스에 데이터를 저장하고 조회하는 것을 의미합니다.

**간단한 예시**:
```java
// ❌ Before (메모리): 재시작 시 소실
public class UserService {
    private List<User> users = new ArrayList<>();

    public void saveUser(User user) {
        users.add(user);  // 메모리에만 저장
    }
}

// ✅ After (데이터베이스): 영구 저장
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;

    public void saveUser(User user) {
        userRepository.save(user);  // DB에 영구 저장
    }
}
```

**핵심 구성 요소**:
1. **DataSource**: 데이터베이스 연결 정보
2. **Entity**: 테이블과 매핑되는 Java 클래스
3. **Repository**: 데이터 접근 계층
4. **Service**: 비즈니스 로직 계층

**설정 예시 (application.yml)**:
```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb
    username: root
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver
```

---

### 2️⃣ 중급자 수준 설명

**Spring의 데이터 접근 기술 비교**

| 기술 | 추상화 수준 | SQL 제어 | 난이도 | 사용 사례 |
|------|-----------|---------|--------|----------|
| **JDBC** | 낮음 | 완전 제어 | 어려움 | 레거시, 성능 최적화 |
| **Spring JDBC** | 중간 | 직접 작성 | 보통 | 간단한 쿼리, 빠른 구현 |
| **JPA/Hibernate** | 높음 | 자동 생성 | 쉬움 | CRUD 중심, 도메인 모델 |
| **MyBatis** | 중간 | 직접 작성 | 보통 | 복잡한 쿼리, SQL 중심 |
| **QueryDSL** | 높음 | 타입 안전 | 보통 | 동적 쿼리, JPA 보완 |

**1. JDBC (Java Database Connectivity)**
```java
// Low-level, 모든 것을 직접 제어
public List<User> findAll() {
    List<User> users = new ArrayList<>();

    try (Connection conn = dataSource.getConnection();
         Statement stmt = conn.createStatement();
         ResultSet rs = stmt.executeQuery("SELECT * FROM users")) {

        while (rs.next()) {
            User user = new User();
            user.setId(rs.getLong("id"));
            user.setName(rs.getString("name"));
            user.setEmail(rs.getString("email"));
            users.add(user);
        }
    } catch (SQLException e) {
        throw new RuntimeException(e);
    }

    return users;
}
```

**장점**:
- 완전한 제어 가능
- 성능 최적화 용이
- 표준 API

**단점**:
- 보일러플레이트 코드 많음
- SQLException 처리 필요
- 반복 작업 많음

---

**2. Spring JDBC (JdbcTemplate)**
```java
// JDBC를 간소화한 버전
@Repository
public class UserRepository {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    public List<User> findAll() {
        String sql = "SELECT * FROM users";

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            User user = new User();
            user.setId(rs.getLong("id"));
            user.setName(rs.getString("name"));
            user.setEmail(rs.getString("email"));
            return user;
        });
    }

    public void save(User user) {
        String sql = "INSERT INTO users (name, email) VALUES (?, ?)";
        jdbcTemplate.update(sql, user.getName(), user.getEmail());
    }
}
```

**장점**:
- JDBC보다 간결한 코드
- 자동 리소스 관리 (Connection, Statement 자동 close)
- Exception 변환 (SQLException → DataAccessException)

**단점**:
- SQL을 직접 작성해야 함
- 객체-테이블 매핑 수동

---

**3. JPA/Hibernate (ORM)**
```java
// 객체 중심, SQL 자동 생성
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private String email;
}

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    // 메서드 이름으로 쿼리 자동 생성
    List<User> findByName(String name);
    List<User> findByEmailContaining(String keyword);
}

// 사용
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;

    public List<User> getAllUsers() {
        return userRepository.findAll();  // SQL 자동 생성
    }
}
```

**장점**:
- SQL 작성 불필요 (대부분)
- 객체 지향적 개발
- 생산성 높음
- 데이터베이스 독립적

**단점**:
- 학습 곡선 높음
- 복잡한 쿼리는 어려움
- 성능 튜닝 어려움 (N+1 문제 등)

---

**4. MyBatis (SQL Mapper)**
```java
// SQL 직접 제어, 객체 매핑 자동
@Mapper
public interface UserMapper {
    @Select("SELECT * FROM users WHERE name = #{name}")
    List<User> findByName(@Param("name") String name);

    @Insert("INSERT INTO users (name, email) VALUES (#{name}, #{email})")
    void insert(User user);
}
```

**XML 방식**:
```xml
<!-- UserMapper.xml -->
<mapper namespace="com.example.UserMapper">
    <select id="findByName" resultType="User">
        SELECT * FROM users
        WHERE name = #{name}
    </select>

    <insert id="insert">
        INSERT INTO users (name, email)
        VALUES (#{name}, #{email})
    </insert>
</mapper>
```

**장점**:
- SQL 완전 제어
- 복잡한 쿼리 작성 용이
- 기존 SQL 재사용 가능
- 동적 쿼리 지원

**단점**:
- SQL을 직접 작성해야 함
- XML 설정 필요 (또는 Annotation)
- JPA보다 생산성 낮음

---

**5. QueryDSL (타입 안전 쿼리)**
```java
// JPA + 타입 안전 쿼리
@Repository
@RequiredArgsConstructor
public class UserRepositoryCustom {

    private final JPAQueryFactory queryFactory;

    public List<User> findByConditions(String name, String email) {
        QUser user = QUser.user;

        return queryFactory
            .selectFrom(user)
            .where(
                nameEq(name),
                emailContains(email)
            )
            .fetch();
    }

    private BooleanExpression nameEq(String name) {
        return name != null ? QUser.user.name.eq(name) : null;
    }

    private BooleanExpression emailContains(String email) {
        return email != null ? QUser.user.email.contains(email) : null;
    }
}
```

**장점**:
- 컴파일 타임 오류 검출
- IDE 자동완성 지원
- 동적 쿼리 작성 용이
- 리팩토링 안전

**단점**:
- 초기 설정 복잡 (Q클래스 생성)
- 학습 곡선
- JPA 의존성

---

### 3️⃣ 고급자 수준 설명

**Spring의 데이터 접근 아키텍처**

```
┌─────────────────────────────────────────────────┐
│                  Controller                      │
│              (Presentation Layer)                │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│                  Service                         │
│              (Business Layer)                    │
│              @Transactional                      │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│                Repository                        │
│            (Data Access Layer)                   │
├──────────┬──────────┬──────────┬────────────────┤
│   JDBC   │  JdbcT.. │   JPA    │   MyBatis      │
└──────────┴──────────┴──────────┴────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              DataSource                          │
│          (Connection Pool)                       │
│         HikariCP, Tomcat JDBC                    │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│               Database                           │
│      MySQL, PostgreSQL, Oracle                   │
└──────────────────────────────────────────────────┘
```

**DataSource와 Connection Pool**

```java
// HikariCP 설정 (Spring Boot 기본)
@Configuration
public class DataSourceConfig {

    @Bean
    @ConfigurationProperties("spring.datasource.hikari")
    public HikariConfig hikariConfig() {
        HikariConfig config = new HikariConfig();

        // Connection Pool 설정
        config.setMaximumPoolSize(20);         // 최대 연결 수
        config.setMinimumIdle(5);              // 최소 유휴 연결
        config.setConnectionTimeout(30000);    // 연결 대기 시간 (30초)
        config.setIdleTimeout(600000);         // 유휴 연결 유지 시간 (10분)
        config.setMaxLifetime(1800000);        // 연결 최대 수명 (30분)

        // 성능 최적화
        config.setAutoCommit(true);
        config.setConnectionTestQuery("SELECT 1");
        config.setPoolName("HikariPool");

        return config;
    }

    @Bean
    public DataSource dataSource(HikariConfig hikariConfig) {
        return new HikariDataSource(hikariConfig);
    }
}
```

**application.yml**:
```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?useUnicode=true&characterEncoding=utf8
    username: root
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver

    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
      auto-commit: true
      pool-name: HikariPool
```

**Connection Pool 동작 원리**:
```
요청 1: DB 연결 요청
    → Pool에서 Connection 가져옴 (빠름, ~1ms)
    → 쿼리 실행
    → Connection을 Pool에 반환 (재사용)

요청 2: DB 연결 요청
    → 이미 있는 Connection 재사용 (새로 연결 안 함)
    → 쿼리 실행
    → Connection을 Pool에 반환

❌ Pool 없이:
    매 요청마다 새로운 Connection 생성 (~100ms)
    → 느림, 리소스 낭비

✅ Pool 사용:
    미리 생성된 Connection 재사용 (~1ms)
    → 빠름, 효율적
```

**트랜잭션 관리**

```java
@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;
    private final ProductRepository productRepository;
    private final PointRepository pointRepository;

    // ✅ 선언적 트랜잭션 (Declarative)
    @Transactional
    public Order createOrder(OrderRequest request) {
        // 1. 재고 확인 및 차감
        Product product = productRepository.findById(request.getProductId())
            .orElseThrow();
        product.decreaseStock(request.getQuantity());

        // 2. 주문 생성
        Order order = new Order(request);
        orderRepository.save(order);

        // 3. 포인트 차감
        Point point = pointRepository.findByUserId(request.getUserId())
            .orElseThrow();
        point.use(request.getUsePoints());

        // 모두 성공 → COMMIT
        // 하나라도 실패 → ROLLBACK (자동)

        return order;
    }

    // ✅ 프로그래밍 방식 트랜잭션 (Programmatic)
    @Autowired
    private TransactionTemplate transactionTemplate;

    public Order createOrderProgrammatic(OrderRequest request) {
        return transactionTemplate.execute(status -> {
            try {
                // 비즈니스 로직
                Order order = new Order(request);
                orderRepository.save(order);
                return order;
            } catch (Exception e) {
                status.setRollbackOnly();
                throw e;
            }
        });
    }
}
```

**트랜잭션 전파 (Propagation)**

```java
@Service
public class UserService {

    @Autowired
    private PointService pointService;

    // REQUIRED (기본값): 기존 트랜잭션 참여, 없으면 새로 생성
    @Transactional(propagation = Propagation.REQUIRED)
    public void registerUser(User user) {
        userRepository.save(user);
        pointService.giveWelcomePoints(user.getId());  // 같은 트랜잭션
    }

    // REQUIRES_NEW: 항상 새로운 트랜잭션 생성
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logActivity(String message) {
        activityRepository.save(new Activity(message));
        // 부모 트랜잭션과 독립적 (부모가 롤백되어도 로그는 저장됨)
    }

    // MANDATORY: 기존 트랜잭션 필수 (없으면 예외)
    @Transactional(propagation = Propagation.MANDATORY)
    public void updateUserPoints(Long userId, int points) {
        // 반드시 트랜잭션 안에서 호출되어야 함
    }
}
```

**격리 수준 (Isolation Level)**

```java
@Service
public class AccountService {

    // READ_UNCOMMITTED: 가장 낮은 격리 수준 (Dirty Read 발생 가능)
    @Transactional(isolation = Isolation.READ_UNCOMMITTED)
    public BigDecimal getBalance(Long accountId) {
        // 다른 트랜잭션의 커밋되지 않은 데이터도 읽음
    }

    // READ_COMMITTED: Oracle 기본값 (Dirty Read 방지)
    @Transactional(isolation = Isolation.READ_COMMITTED)
    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        // 커밋된 데이터만 읽음
        // Non-Repeatable Read 발생 가능
    }

    // REPEATABLE_READ: MySQL 기본값 (Non-Repeatable Read 방지)
    @Transactional(isolation = Isolation.REPEATABLE_READ)
    public void processOrder(Long orderId) {
        // 같은 쿼리를 여러 번 실행해도 같은 결과
        // Phantom Read 발생 가능 (MySQL은 Next-Key Lock으로 방지)
    }

    // SERIALIZABLE: 가장 높은 격리 수준 (완전한 격리)
    @Transactional(isolation = Isolation.SERIALIZABLE)
    public void criticalOperation() {
        // 완전한 격리, 동시성 가장 낮음
    }
}
```

---

## 💻 기본 실습

### 실습 1: Spring JDBC 기본 설정

**난이도**: ⭐⭐☆☆☆

#### 1. 의존성 추가 (build.gradle)

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-jdbc'
    runtimeOnly 'com.mysql:mysql-connector-j'

    // Connection Pool (Spring Boot 기본 포함)
    // implementation 'com.zaxxer:HikariCP'
}
```

#### 2. 데이터베이스 설정 (application.yml)

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/testdb?useUnicode=true&characterEncoding=utf8
    username: root
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver

    # HikariCP 설정 (옵션)
    hikari:
      maximum-pool-size: 10
      minimum-idle: 5
      connection-timeout: 30000
```

#### 3. 테이블 생성 (schema.sql)

**src/main/resources/schema.sql**:
```sql
CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. Repository 구현

```java
@Repository
@RequiredArgsConstructor
public class UserRepository {

    private final JdbcTemplate jdbcTemplate;

    public void save(User user) {
        String sql = "INSERT INTO users (name, email) VALUES (?, ?)";
        jdbcTemplate.update(sql, user.getName(), user.getEmail());
    }

    public User findById(Long id) {
        String sql = "SELECT * FROM users WHERE id = ?";
        return jdbcTemplate.queryForObject(sql, this::mapRow, id);
    }

    public List<User> findAll() {
        String sql = "SELECT * FROM users";
        return jdbcTemplate.query(sql, this::mapRow);
    }

    public void update(User user) {
        String sql = "UPDATE users SET name = ?, email = ? WHERE id = ?";
        jdbcTemplate.update(sql, user.getName(), user.getEmail(), user.getId());
    }

    public void deleteById(Long id) {
        String sql = "DELETE FROM users WHERE id = ?";
        jdbcTemplate.update(sql, id);
    }

    // RowMapper
    private User mapRow(ResultSet rs, int rowNum) throws SQLException {
        User user = new User();
        user.setId(rs.getLong("id"));
        user.setName(rs.getString("name"));
        user.setEmail(rs.getString("email"));
        user.setCreatedAt(rs.getTimestamp("created_at").toLocalDateTime());
        return user;
    }
}
```

#### 5. Service 구현

```java
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;

    @Transactional
    public void createUser(String name, String email) {
        User user = new User();
        user.setName(name);
        user.setEmail(email);

        userRepository.save(user);
    }

    public User getUser(Long id) {
        return userRepository.findById(id);
    }

    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
}
```

#### 6. Controller 구현

```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @PostMapping
    public ResponseEntity<Void> createUser(@RequestBody UserRequest request) {
        userService.createUser(request.getName(), request.getEmail());
        return ResponseEntity.status(HttpStatus.CREATED).build();
    }

    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        User user = userService.getUser(id);
        return ResponseEntity.ok(user);
    }

    @GetMapping
    public ResponseEntity<List<User>> getAllUsers() {
        List<User> users = userService.getAllUsers();
        return ResponseEntity.ok(users);
    }
}
```

#### 7. 테스트

```bash
# 사용자 생성
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"홍길동","email":"hong@example.com"}'

# 사용자 조회
curl http://localhost:8080/api/users/1

# 모든 사용자 조회
curl http://localhost:8080/api/users
```

---

### 실습 2: JPA 기본 설정

**난이도**: ⭐⭐☆☆☆

#### 1. 의존성 추가

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    runtimeOnly 'com.mysql:mysql-connector-j'
}
```

#### 2. 설정 (application.yml)

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/testdb
    username: root
    password: password

  jpa:
    hibernate:
      ddl-auto: update  # create, update, validate, none
    show-sql: true
    properties:
      hibernate:
        format_sql: true
        use_sql_comments: true
```

#### 3. Entity 정의

```java
@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(nullable = false, unique = true, length = 100)
    private String email;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
```

#### 4. Repository 정의

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    // 메서드 이름으로 쿼리 자동 생성
    Optional<User> findByEmail(String email);

    List<User> findByNameContaining(String keyword);

    @Query("SELECT u FROM User u WHERE u.email LIKE %:keyword%")
    List<User> searchByEmail(@Param("keyword") String keyword);
}
```

#### 5. Service 구현

```java
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;

    @Transactional
    public User createUser(String name, String email) {
        User user = new User();
        user.setName(name);
        user.setEmail(email);

        return userRepository.save(user);
    }

    public User getUser(Long id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));
    }

    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    @Transactional
    public User updateUser(Long id, String name, String email) {
        User user = getUser(id);
        user.setName(name);
        user.setEmail(email);

        return userRepository.save(user);
    }

    @Transactional
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }
}
```

---

## 🏢 실무 활용 사례

### 사례 1: 배달의민족 - 하이브리드 데이터 접근 전략

**배경**:
배달의민족이 수백만 주문을 처리하면서 JPA와 MyBatis를 함께 사용하여 성능과 생산성을 모두 잡은 사례

**요구사항**:
- 일반 CRUD: 빠른 개발 속도
- 복잡한 통계 쿼리: 높은 성능
- 대용량 배치 처리: 메모리 효율성
- 실시간 주문 처리: 트랜잭션 안정성

**구현 코드**:

```java
// 1. JPA로 간단한 CRUD (생산성 우선)
@Entity
@Table(name = "orders")
@Getter
@Setter
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long userId;

    @Column(nullable = false)
    private Long restaurantId;

    @Enumerated(EnumType.STRING)
    private OrderStatus status;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal totalAmount;

    @Column(name = "created_at")
    private LocalDateTime createdAt;
}

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByUserId(Long userId);
    List<Order> findByStatus(OrderStatus status);
}

// 2. MyBatis로 복잡한 통계 쿼리 (성능 우선)
@Mapper
public interface OrderStatisticsMapper {

    // 음식점별 일일 매출 통계 (복잡한 GROUP BY, JOIN)
    @Select("""
        SELECT
            r.id as restaurant_id,
            r.name as restaurant_name,
            DATE(o.created_at) as order_date,
            COUNT(o.id) as order_count,
            SUM(o.total_amount) as total_sales,
            AVG(o.total_amount) as avg_order_amount
        FROM orders o
        JOIN restaurants r ON o.restaurant_id = r.id
        WHERE o.created_at >= #{startDate}
          AND o.created_at < #{endDate}
          AND o.status = 'COMPLETED'
        GROUP BY r.id, r.name, DATE(o.created_at)
        ORDER BY total_sales DESC
    """)
    List<RestaurantDailySales> getDailySalesStatistics(
        @Param("startDate") LocalDateTime startDate,
        @Param("endDate") LocalDateTime endDate
    );

    // 시간대별 주문 분포 (동적 쿼리)
    List<HourlyOrderDistribution> getHourlyDistribution(
        @Param("restaurantId") Long restaurantId,
        @Param("dayOfWeek") String dayOfWeek
    );
}
```

**MyBatis XML (동적 쿼리)**:
```xml
<!-- OrderStatisticsMapper.xml -->
<mapper namespace="com.baemin.mapper.OrderStatisticsMapper">

    <select id="getHourlyDistribution" resultType="HourlyOrderDistribution">
        SELECT
            HOUR(created_at) as hour,
            COUNT(*) as order_count,
            AVG(total_amount) as avg_amount
        FROM orders
        WHERE 1=1
            <if test="restaurantId != null">
                AND restaurant_id = #{restaurantId}
            </if>
            <if test="dayOfWeek != null">
                AND DAYNAME(created_at) = #{dayOfWeek}
            </if>
            AND status = 'COMPLETED'
            AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        GROUP BY HOUR(created_at)
        ORDER BY hour
    </select>

</mapper>
```

**Service 계층 (두 가지 혼합 사용)**:
```java
@Service
@RequiredArgsConstructor
@Slf4j
public class OrderService {

    private final OrderRepository orderRepository;  // JPA
    private final OrderStatisticsMapper statisticsMapper;  // MyBatis

    // ✅ 간단한 CRUD는 JPA (빠른 개발)
    @Transactional
    public Order createOrder(OrderRequest request) {
        Order order = new Order();
        order.setUserId(request.getUserId());
        order.setRestaurantId(request.getRestaurantId());
        order.setTotalAmount(request.getTotalAmount());
        order.setStatus(OrderStatus.PENDING);
        order.setCreatedAt(LocalDateTime.now());

        return orderRepository.save(order);
    }

    public List<Order> getUserOrders(Long userId) {
        return orderRepository.findByUserId(userId);
    }

    // ✅ 복잡한 통계는 MyBatis (고성능)
    public List<RestaurantDailySales> getDailySalesReport(
            LocalDate startDate, LocalDate endDate) {

        LocalDateTime start = startDate.atStartOfDay();
        LocalDateTime end = endDate.plusDays(1).atStartOfDay();

        return statisticsMapper.getDailySalesStatistics(start, end);
    }

    public Map<Integer, OrderStatistics> getHourlyOrderPattern(
            Long restaurantId, String dayOfWeek) {

        List<HourlyOrderDistribution> distribution =
            statisticsMapper.getHourlyDistribution(restaurantId, dayOfWeek);

        return distribution.stream()
            .collect(Collectors.toMap(
                HourlyOrderDistribution::getHour,
                d -> new OrderStatistics(d.getOrderCount(), d.getAvgAmount())
            ));
    }
}
```

**대용량 배치 처리 (MyBatis로 메모리 효율적으로)**:
```java
@Component
@RequiredArgsConstructor
@Slf4j
public class OrderBatchProcessor {

    private final OrderStatisticsMapper statisticsMapper;
    private final SqlSessionFactory sqlSessionFactory;

    @Scheduled(cron = "0 0 2 * * *")  // 매일 새벽 2시
    public void processMonthlyStatistics() {
        log.info("Starting monthly statistics batch job");

        LocalDateTime startOfMonth = LocalDateTime.now()
            .withDayOfMonth(1)
            .withHour(0)
            .withMinute(0)
            .withSecond(0);

        // ✅ MyBatis의 Cursor를 사용한 메모리 효율적 대량 처리
        try (SqlSession session = sqlSessionFactory.openSession();
             Cursor<Order> cursor = session.selectCursor(
                 "com.baemin.mapper.OrderMapper.selectAllForMonth",
                 startOfMonth)) {

            int count = 0;
            for (Order order : cursor) {
                processOrder(order);

                if (++count % 1000 == 0) {
                    log.info("Processed {} orders", count);
                }
            }

            log.info("Monthly statistics completed. Total: {} orders", count);
        }
    }

    private void processOrder(Order order) {
        // 통계 처리 로직
    }
}
```

**성과**:
- JPA 사용으로 개발 속도 **50% 향상**
- MyBatis로 복잡한 쿼리 성능 **300% 개선**
- 배치 처리 메모리 사용량 **90% 감소** (Cursor 사용)
- 전체 시스템 안정성 **향상** (트랜잭션 관리 일원화)

---

### 사례 2: 토스 - Multi-DataSource 전략

**배경**:
토스가 읽기/쓰기 분리(Read/Write Splitting)로 데이터베이스 부하를 분산한 사례

**요구사항**:
- Master DB: 쓰기 작업 (INSERT, UPDATE, DELETE)
- Slave DB (복제본): 읽기 작업 (SELECT)
- 트랜잭션 내 쓰기 → Master로 라우팅
- 읽기 전용 → Slave로 라우팅
- Slave 장애 시 Master로 Failover

**구현 코드**:

```java
// 1. DataSource 설정
@Configuration
public class DataSourceConfig {

    @Bean
    @ConfigurationProperties("spring.datasource.master")
    public DataSource masterDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    @ConfigurationProperties("spring.datasource.slave")
    public DataSource slaveDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    @Primary
    public DataSource routingDataSource(
            @Qualifier("masterDataSource") DataSource master,
            @Qualifier("slaveDataSource") DataSource slave) {

        ReplicationRoutingDataSource routingDataSource =
            new ReplicationRoutingDataSource();

        Map<Object, Object> dataSourceMap = new HashMap<>();
        dataSourceMap.put(DataSourceType.MASTER, master);
        dataSourceMap.put(DataSourceType.SLAVE, slave);

        routingDataSource.setTargetDataSources(dataSourceMap);
        routingDataSource.setDefaultTargetDataSource(master);

        return routingDataSource;
    }
}

// 2. 동적 DataSource 라우팅
public class ReplicationRoutingDataSource extends AbstractRoutingDataSource {

    @Override
    protected Object determineCurrentLookupKey() {
        // 현재 요청이 읽기 전용인지 확인
        boolean isReadOnly = TransactionSynchronizationManager.isCurrentTransactionReadOnly();

        if (isReadOnly) {
            log.debug("Routing to SLAVE DataSource");
            return DataSourceType.SLAVE;
        } else {
            log.debug("Routing to MASTER DataSource");
            return DataSourceType.MASTER;
        }
    }
}

enum DataSourceType {
    MASTER, SLAVE
}

// 3. Service 계층에서 사용
@Service
@RequiredArgsConstructor
@Slf4j
public class PaymentService {

    private final PaymentRepository paymentRepository;

    // ✅ 쓰기 작업: Master DB 사용
    @Transactional
    public Payment createPayment(PaymentRequest request) {
        log.info("Creating payment - will use MASTER DB");

        Payment payment = new Payment();
        payment.setUserId(request.getUserId());
        payment.setAmount(request.getAmount());
        payment.setStatus(PaymentStatus.PENDING);

        return paymentRepository.save(payment);
    }

    // ✅ 읽기 전용: Slave DB 사용
    @Transactional(readOnly = true)
    public Payment getPayment(Long id) {
        log.info("Fetching payment - will use SLAVE DB");

        return paymentRepository.findById(id)
            .orElseThrow(() -> new PaymentNotFoundException(id));
    }

    // ✅ 읽기 전용 통계: Slave DB 사용
    @Transactional(readOnly = true)
    public PaymentStatistics getMonthlyStatistics(Long userId) {
        log.info("Fetching statistics - will use SLAVE DB");

        LocalDateTime startOfMonth = LocalDateTime.now()
            .withDayOfMonth(1)
            .withHour(0);

        List<Payment> payments = paymentRepository
            .findByUserIdAndCreatedAtAfter(userId, startOfMonth);

        return PaymentStatistics.from(payments);
    }

    // ✅ 쓰기 작업이 포함되면 Master DB 사용
    @Transactional
    public void processPayment(Long paymentId) {
        log.info("Processing payment - will use MASTER DB");

        Payment payment = paymentRepository.findById(paymentId)
            .orElseThrow();

        // 상태 변경 (쓰기 작업)
        payment.setStatus(PaymentStatus.COMPLETED);
        payment.setCompletedAt(LocalDateTime.now());

        paymentRepository.save(payment);
    }
}
```

**application.yml**:
```yaml
spring:
  datasource:
    master:
      jdbc-url: jdbc:mysql://master-db:3306/toss
      username: toss_master
      password: master_password
      driver-class-name: com.mysql.cj.jdbc.Driver
      hikari:
        maximum-pool-size: 20
        minimum-idle: 5

    slave:
      jdbc-url: jdbc:mysql://slave-db:3306/toss
      username: toss_slave
      password: slave_password
      driver-class-name: com.mysql.cj.jdbc.Driver
      hikari:
        maximum-pool-size: 30  # Slave는 더 많은 연결 허용
        minimum-idle: 10
```

**Slave 장애 시 Failover**:
```java
public class ReplicationRoutingDataSource extends AbstractRoutingDataSource {

    private final DataSource masterDataSource;
    private final DataSource slaveDataSource;
    private boolean slaveAvailable = true;

    @Override
    protected Object determineCurrentLookupKey() {
        boolean isReadOnly = TransactionSynchronizationManager.isCurrentTransactionReadOnly();

        if (isReadOnly && slaveAvailable) {
            try {
                // Slave 상태 확인
                testSlaveConnection();
                return DataSourceType.SLAVE;
            } catch (Exception e) {
                log.error("Slave DB is not available. Falling back to Master", e);
                slaveAvailable = false;
                scheduleSlaveHealthCheck();
                return DataSourceType.MASTER;
            }
        }

        return DataSourceType.MASTER;
    }

    private void testSlaveConnection() throws SQLException {
        try (Connection conn = slaveDataSource.getConnection();
             Statement stmt = conn.createStatement()) {
            stmt.execute("SELECT 1");
        }
    }

    @Scheduled(fixedDelay = 10000)  // 10초마다 확인
    public void scheduleSlaveHealthCheck() {
        if (!slaveAvailable) {
            try {
                testSlaveConnection();
                slaveAvailable = true;
                log.info("Slave DB is back online");
            } catch (Exception e) {
                log.debug("Slave DB still unavailable");
            }
        }
    }
}
```

**성과**:
- Master DB 부하 **70% 감소** (읽기를 Slave로 분산)
- 전체 시스템 처리량 **2배 향상**
- Slave 장애 시에도 **무중단 서비스** (자동 Failover)
- 피크 시간대 응답 시간 **50% 개선**

---

## 🎯 주니어 시나리오

### 시나리오 1: "DB 연결이 안 돼요!"

**상황**:
주니어 개발자 김코딩이 Spring Boot를 실행했는데 DB 연결 오류가 발생합니다.

**에러 메시지**:
```
com.mysql.cj.jdbc.exceptions.CommunicationsException:
Communications link failure

The last packet sent successfully to the server was 0 milliseconds ago.
The driver has not received any packets from the server.
```

**원인 분석**:

**원인 1: MySQL 서버가 실행되지 않음**
```bash
# MySQL 상태 확인
sudo systemctl status mysql

# 실행되지 않았다면 시작
sudo systemctl start mysql
```

**원인 2: 포트 번호 틀림**
```yaml
# ❌ 잘못된 포트
spring:
  datasource:
    url: jdbc:mysql://localhost:3307/mydb  # MySQL 기본 포트는 3306

# ✅ 올바른 포트
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb
```

**원인 3: 데이터베이스가 존재하지 않음**
```sql
-- MySQL에 접속하여 데이터베이스 생성
CREATE DATABASE mydb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**원인 4: 사용자 권한 문제**
```sql
-- 사용자 생성 및 권한 부여
CREATE USER 'myuser'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON mydb.* TO 'myuser'@'localhost';
FLUSH PRIVILEGES;
```

**원인 5: 방화벽 차단**
```bash
# 방화벽 상태 확인
sudo ufw status

# MySQL 포트 허용
sudo ufw allow 3306/tcp
```

**해결책 체크리스트**:
```
✅ MySQL 서버 실행 중인지 확인
✅ 포트 번호 확인 (기본: 3306)
✅ 데이터베이스 생성 여부 확인
✅ 사용자 이름/비밀번호 확인
✅ 사용자 권한 확인
✅ 방화벽 설정 확인
✅ application.yml 설정 확인
```

**검증 방법**:
```bash
# MySQL 직접 접속 테스트
mysql -h localhost -P 3306 -u myuser -p

# 연결되면 데이터베이스 선택
USE mydb;

# 테이블 목록 확인
SHOW TABLES;
```

---

### 시나리오 2: "트랜잭션이 롤백 안 돼요!"

**상황**:
예외가 발생해도 데이터가 그대로 저장됩니다.

**문제 코드**:
```java
@Service
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private PointService pointService;

    // ❌ @Transactional 누락!
    public void createOrder(OrderRequest request) {
        // 1. 주문 생성
        Order order = new Order(request);
        orderRepository.save(order);

        // 2. 포인트 차감 (여기서 예외 발생)
        pointService.deductPoints(request.getUserId(), request.getUsePoints());
        // → 예외가 발생해도 주문은 그대로 저장됨!
    }
}
```

**증상**:
```
1. 주문 생성: ✅ 성공 (DB에 저장됨)
2. 포인트 차감: ❌ 실패 (예외 발생)

결과: 주문은 저장되었지만 포인트는 차감 안 됨 → 데이터 불일치!
```

**해결책 1: @Transactional 추가**:
```java
@Service
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private PointService pointService;

    // ✅ @Transactional 추가
    @Transactional
    public void createOrder(OrderRequest request) {
        // 1. 주문 생성
        Order order = new Order(request);
        orderRepository.save(order);

        // 2. 포인트 차감
        pointService.deductPoints(request.getUserId(), request.getUsePoints());

        // 예외 발생 시 둘 다 롤백됨!
    }
}
```

**주의사항**:
```java
// ❌ Checked Exception은 기본적으로 롤백 안 됨
@Transactional
public void createOrder(OrderRequest request) throws Exception {
    orderRepository.save(new Order(request));
    throw new Exception("Error");  // 롤백 안 됨!
}

// ✅ RuntimeException은 자동 롤백
@Transactional
public void createOrder(OrderRequest request) {
    orderRepository.save(new Order(request));
    throw new RuntimeException("Error");  // 자동 롤백됨
}

// ✅ Checked Exception도 롤백하려면 명시
@Transactional(rollbackFor = Exception.class)
public void createOrder(OrderRequest request) throws Exception {
    orderRepository.save(new Order(request));
    throw new Exception("Error");  // 롤백됨
}
```

---

### 시나리오 3: "N+1 문제가 뭔가요?"

**상황**:
회원 목록과 각 회원의 주문을 조회하는데 쿼리가 수천 개 실행됩니다.

**문제 코드**:
```java
@Entity
public class User {
    @Id
    private Long id;
    private String name;

    @OneToMany(mappedBy = "user")
    private List<Order> orders;
}

@Service
public class UserService {

    public List<UserDTO> getAllUsersWithOrders() {
        List<User> users = userRepository.findAll();  // 1번 쿼리

        return users.stream()
            .map(user -> {
                UserDTO dto = new UserDTO(user);
                dto.setOrderCount(user.getOrders().size());  // N번 추가 쿼리!
                return dto;
            })
            .collect(Collectors.toList());
    }
}
```

**실행되는 쿼리**:
```sql
-- 1번: 모든 사용자 조회
SELECT * FROM users;  -- 결과: 100명

-- N번: 각 사용자의 주문 조회 (100번!)
SELECT * FROM orders WHERE user_id = 1;
SELECT * FROM orders WHERE user_id = 2;
SELECT * FROM orders WHERE user_id = 3;
...
SELECT * FROM orders WHERE user_id = 100;

-- 총 101번의 쿼리 실행! (1 + N)
```

**해결책 1: Fetch Join**:
```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    // ✅ Fetch Join으로 한 번에 조회
    @Query("SELECT u FROM User u JOIN FETCH u.orders")
    List<User> findAllWithOrders();
}
```

**실행되는 쿼리**:
```sql
-- 1번의 쿼리로 모든 데이터 조회
SELECT u.*, o.*
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
```

**해결책 2: @EntityGraph**:
```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    @EntityGraph(attributePaths = "orders")
    List<User> findAll();
}
```

**해결책 3: Batch Size 설정**:
```yaml
spring:
  jpa:
    properties:
      hibernate:
        default_batch_fetch_size: 100
```

**이렇게 하면**:
```sql
-- Orders를 IN 절로 한 번에 조회 (100개씩)
SELECT * FROM orders WHERE user_id IN (1, 2, 3, ..., 100);

-- 101번 → 2번으로 감소!
```

---

### 시나리오 4: "LazyInitializationException이 발생해요!"

**상황**:
Controller에서 연관 엔티티를 조회하려고 하니 예외가 발생합니다.

**문제 코드**:
```java
@Entity
public class User {
    @Id
    private Long id;

    @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)  // Lazy Loading
    private List<Order> orders;
}

@Service
public class UserService {

    public User getUser(Long id) {
        return userRepository.findById(id).orElseThrow();
        // Service 메서드 종료 → 트랜잭션 종료 → 영속성 컨텍스트 종료
    }
}

@RestController
public class UserController {

    @GetMapping("/users/{id}")
    public UserDTO getUser(@PathVariable Long id) {
        User user = userService.getUser(id);

        // ❌ 여기서 orders 접근 시 LazyInitializationException!
        return new UserDTO(user, user.getOrders());
    }
}
```

**에러 메시지**:
```
org.hibernate.LazyInitializationException:
failed to lazily initialize a collection of role: User.orders,
could not initialize proxy - no Session
```

**원인**:
```
1. Service 메서드 종료 → @Transactional 종료
2. 영속성 컨텍스트(Session) 종료
3. Controller에서 orders 접근 시도
4. 이미 Session이 없어서 Lazy Loading 불가능
5. Exception 발생!
```

**해결책 1: Service에서 명시적으로 로드**:
```java
@Service
public class UserService {

    @Transactional(readOnly = true)
    public User getUser(Long id) {
        User user = userRepository.findById(id).orElseThrow();

        // ✅ 트랜잭션 안에서 명시적으로 로드
        user.getOrders().size();  // Lazy Loading 강제 실행

        return user;
    }
}
```

**해결책 2: Fetch Join**:
```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    @Query("SELECT u FROM User u LEFT JOIN FETCH u.orders WHERE u.id = :id")
    Optional<User> findByIdWithOrders(@Param("id") Long id);
}

@Service
public class UserService {

    public User getUser(Long id) {
        return userRepository.findByIdWithOrders(id).orElseThrow();
    }
}
```

**해결책 3: DTO 변환 (가장 권장)**:
```java
@Service
public class UserService {

    @Transactional(readOnly = true)
    public UserDTO getUser(Long id) {
        User user = userRepository.findById(id).orElseThrow();

        // ✅ 트랜잭션 안에서 DTO 변환
        return new UserDTO(user, user.getOrders());
    }
}

@RestController
public class UserController {

    @GetMapping("/users/{id}")
    public UserDTO getUser(@PathVariable Long id) {
        return userService.getUser(id);  // 이미 DTO로 변환됨
    }
}
```

**배운 점**:
- Lazy Loading은 트랜잭션 안에서만 작동
- Controller에서는 엔티티 대신 DTO 사용
- 필요한 데이터는 Service에서 미리 로드

---

## 🚀 실전 프로젝트: 이커머스 주문 시스템

### 프로젝트 개요

**목표**: 실무 수준의 주문 관리 시스템 구축

**주요 기능**:
1. 회원 관리 (CRUD)
2. 상품 관리 (재고 관리)
3. 주문 처리 (트랜잭션)
4. 결제 연동
5. 주문 통계 (복잡한 쿼리)
6. 배치 처리 (정산)

**기술 스택**:
- Spring Boot 3.2
- JPA + QueryDSL
- MySQL 8.0
- Redis (캐시)
- HikariCP (Connection Pool)

---

### 1단계: 프로젝트 설정

**build.gradle**:
```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-validation'

    // QueryDSL
    implementation 'com.querydsl:querydsl-jpa:5.0.0:jakarta'
    annotationProcessor 'com.querydsl:querydsl-apt:5.0.0:jakarta'
    annotationProcessor 'jakarta.annotation:jakarta.annotation-api'
    annotationProcessor 'jakarta.persistence:jakarta.persistence-api'

    runtimeOnly 'com.mysql:mysql-connector-j'

    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'

    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}
```

**application.yml**:
```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/ecommerce?useUnicode=true&characterEncoding=utf8mb4
    username: ecommerce_user
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver

    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000

  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: true
    properties:
      hibernate:
        format_sql: true
        use_sql_comments: true
        default_batch_fetch_size: 100

  sql:
    init:
      mode: never  # 운영에서는 Flyway/Liquibase 사용
```

---

### 2단계: Domain 설계

**User Entity**:
```java
@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(nullable = false, unique = true, length = 100)
    private String email;

    @Column(nullable = false, length = 100)
    private String password;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
```

**Product Entity**:
```java
@Entity
@Table(name = "products")
@Getter
@Setter
@NoArgsConstructor
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String name;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;

    @Column(nullable = false)
    private Integer stockQuantity;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    // 재고 차감
    public void decreaseStock(int quantity) {
        if (this.stockQuantity < quantity) {
            throw new InsufficientStockException(
                "재고가 부족합니다. 현재 재고: " + this.stockQuantity);
        }
        this.stockQuantity -= quantity;
    }

    // 재고 증가
    public void increaseStock(int quantity) {
        this.stockQuantity += quantity;
    }
}
```

**Order Entity**:
```java
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

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private OrderStatus status;

    @Column(name = "total_amount", nullable = false, precision = 10, scale = 2)
    private BigDecimal totalAmount;

    @Column(name = "order_date", nullable = false)
    private LocalDateTime orderDate;

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderItem> orderItems = new ArrayList<>();

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        if (orderDate == null) {
            orderDate = LocalDateTime.now();
        }
        if (status == null) {
            status = OrderStatus.PENDING;
        }
    }

    // 연관관계 편의 메서드
    public void addOrderItem(OrderItem orderItem) {
        orderItems.add(orderItem);
        orderItem.setOrder(this);
    }

    // 총 금액 계산
    public void calculateTotalAmount() {
        this.totalAmount = orderItems.stream()
            .map(OrderItem::getTotalPrice)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}

enum OrderStatus {
    PENDING,      // 대기
    CONFIRMED,    // 확인
    SHIPPED,      // 배송중
    DELIVERED,    // 배송완료
    CANCELLED     // 취소
}
```

**OrderItem Entity**:
```java
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

    @Column(name = "unit_price", nullable = false, precision = 10, scale = 2)
    private BigDecimal unitPrice;

    // 총 가격 계산
    public BigDecimal getTotalPrice() {
        return unitPrice.multiply(BigDecimal.valueOf(quantity));
    }
}
```

---

### 3단계: Repository 구현

**UserRepository**:
```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
}
```

**ProductRepository**:
```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT p FROM Product p WHERE p.id = :id")
    Optional<Product> findByIdWithLock(@Param("id") Long id);

    List<Product> findByStockQuantityLessThan(Integer threshold);
}
```

**OrderRepository**:
```java
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {

    @Query("SELECT o FROM Order o JOIN FETCH o.user WHERE o.id = :id")
    Optional<Order> findByIdWithUser(@Param("id") Long id);

    @Query("SELECT o FROM Order o " +
           "JOIN FETCH o.user " +
           "JOIN FETCH o.orderItems oi " +
           "JOIN FETCH oi.product " +
           "WHERE o.id = :id")
    Optional<Order> findByIdWithDetails(@Param("id") Long id);

    List<Order> findByUserIdOrderByOrderDateDesc(Long userId);

    List<Order> findByStatus(OrderStatus status);
}
```

---

### 4단계: Service 구현

**OrderService**:
```java
@Service
@RequiredArgsConstructor
@Slf4j
public class OrderService {

    private final OrderRepository orderRepository;
    private final ProductRepository productRepository;
    private final UserRepository userRepository;

    @Transactional
    public Order createOrder(Long userId, List<OrderItemRequest> items) {
        log.info("Creating order for user: {}", userId);

        // 1. 사용자 조회
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new UserNotFoundException("사용자를 찾을 수 없습니다: " + userId));

        // 2. 주문 생성
        Order order = new Order();
        order.setUser(user);
        order.setStatus(OrderStatus.PENDING);
        order.setOrderDate(LocalDateTime.now());

        // 3. 주문 항목 추가 및 재고 차감
        for (OrderItemRequest itemRequest : items) {
            // 비관적 락으로 재고 확보
            Product product = productRepository.findByIdWithLock(itemRequest.getProductId())
                .orElseThrow(() -> new ProductNotFoundException(
                    "상품을 찾을 수 없습니다: " + itemRequest.getProductId()));

            // 재고 차감 (부족하면 예외 발생)
            product.decreaseStock(itemRequest.getQuantity());

            // 주문 항목 생성
            OrderItem orderItem = new OrderItem();
            orderItem.setProduct(product);
            orderItem.setQuantity(itemRequest.getQuantity());
            orderItem.setUnitPrice(product.getPrice());

            order.addOrderItem(orderItem);
        }

        // 4. 총 금액 계산
        order.calculateTotalAmount();

        // 5. 주문 저장
        Order savedOrder = orderRepository.save(order);

        log.info("Order created successfully: {}", savedOrder.getId());

        return savedOrder;
    }

    @Transactional(readOnly = true)
    public Order getOrderDetails(Long orderId) {
        return orderRepository.findByIdWithDetails(orderId)
            .orElseThrow(() -> new OrderNotFoundException("주문을 찾을 수 없습니다: " + orderId));
    }

    @Transactional(readOnly = true)
    public List<Order> getUserOrders(Long userId) {
        return orderRepository.findByUserIdOrderByOrderDateDesc(userId);
    }

    @Transactional
    public Order cancelOrder(Long orderId) {
        Order order = orderRepository.findByIdWithDetails(orderId)
            .orElseThrow(() -> new OrderNotFoundException("주문을 찾을 수 없습니다: " + orderId));

        // 취소 가능 여부 확인
        if (order.getStatus() == OrderStatus.SHIPPED ||
            order.getStatus() == OrderStatus.DELIVERED) {
            throw new OrderCancellationException("배송 중이거나 완료된 주문은 취소할 수 없습니다.");
        }

        // 재고 복구
        for (OrderItem item : order.getOrderItems()) {
            Product product = item.getProduct();
            product.increaseStock(item.getQuantity());
        }

        // 주문 상태 변경
        order.setStatus(OrderStatus.CANCELLED);

        return orderRepository.save(order);
    }
}
```

---

### 5단계: Controller 구현

**OrderController**:
```java
@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
public class OrderController {

    private final OrderService orderService;

    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(
            @RequestBody @Valid CreateOrderRequest request) {

        Order order = orderService.createOrder(
            request.getUserId(),
            request.getItems()
        );

        OrderResponse response = OrderResponse.from(order);

        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/{orderId}")
    public ResponseEntity<OrderDetailResponse> getOrder(
            @PathVariable Long orderId) {

        Order order = orderService.getOrderDetails(orderId);

        return ResponseEntity.ok(OrderDetailResponse.from(order));
    }

    @GetMapping("/user/{userId}")
    public ResponseEntity<List<OrderResponse>> getUserOrders(
            @PathVariable Long userId) {

        List<Order> orders = orderService.getUserOrders(userId);

        List<OrderResponse> responses = orders.stream()
            .map(OrderResponse::from)
            .collect(Collectors.toList());

        return ResponseEntity.ok(responses);
    }

    @PostMapping("/{orderId}/cancel")
    public ResponseEntity<OrderResponse> cancelOrder(
            @PathVariable Long orderId) {

        Order order = orderService.cancelOrder(orderId);

        return ResponseEntity.ok(OrderResponse.from(order));
    }
}
```

---

### 6단계: 테스트

**통합 테스트**:
```java
@SpringBootTest
@Transactional
class OrderServiceTest {

    @Autowired
    private OrderService orderService;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private ProductRepository productRepository;

    @Test
    @DisplayName("주문 생성 - 성공")
    void createOrder_Success() {
        // Given
        User user = createUser("홍길동", "hong@example.com");
        Product product = createProduct("노트북", BigDecimal.valueOf(1000000), 10);

        List<OrderItemRequest> items = List.of(
            new OrderItemRequest(product.getId(), 2)
        );

        // When
        Order order = orderService.createOrder(user.getId(), items);

        // Then
        assertThat(order).isNotNull();
        assertThat(order.getTotalAmount()).isEqualTo(BigDecimal.valueOf(2000000));
        assertThat(order.getOrderItems()).hasSize(1);

        // 재고 확인
        Product updatedProduct = productRepository.findById(product.getId()).orElseThrow();
        assertThat(updatedProduct.getStockQuantity()).isEqualTo(8);
    }

    @Test
    @DisplayName("주문 생성 - 재고 부족 시 실패")
    void createOrder_InsufficientStock() {
        // Given
        User user = createUser("홍길동", "hong@example.com");
        Product product = createProduct("노트북", BigDecimal.valueOf(1000000), 5);

        List<OrderItemRequest> items = List.of(
            new OrderItemRequest(product.getId(), 10)  // 재고보다 많이 주문
        );

        // When & Then
        assertThatThrownBy(() -> orderService.createOrder(user.getId(), items))
            .isInstanceOf(InsufficientStockException.class);

        // 재고가 변경되지 않았는지 확인 (롤백)
        Product unchangedProduct = productRepository.findById(product.getId()).orElseThrow();
        assertThat(unchangedProduct.getStockQuantity()).isEqualTo(5);
    }

    @Test
    @DisplayName("주문 취소 - 재고 복구 확인")
    void cancelOrder_StockRestored() {
        // Given
        User user = createUser("홍길동", "hong@example.com");
        Product product = createProduct("노트북", BigDecimal.valueOf(1000000), 10);

        List<OrderItemRequest> items = List.of(
            new OrderItemRequest(product.getId(), 3)
        );

        Order order = orderService.createOrder(user.getId(), items);

        // When
        orderService.cancelOrder(order.getId());

        // Then
        Product restoredProduct = productRepository.findById(product.getId()).orElseThrow();
        assertThat(restoredProduct.getStockQuantity()).isEqualTo(10);  // 재고 복구됨
    }

    private User createUser(String name, String email) {
        User user = new User();
        user.setName(name);
        user.setEmail(email);
        user.setPassword("password");
        return userRepository.save(user);
    }

    private Product createProduct(String name, BigDecimal price, int stock) {
        Product product = new Product();
        product.setName(name);
        product.setPrice(price);
        product.setStockQuantity(stock);
        return productRepository.save(product);
    }
}
```

---

### 프로젝트 완성도 체크리스트

```
✅ Entity 설계 (User, Product, Order, OrderItem)
✅ 연관관계 매핑 (@ManyToOne, @OneToMany)
✅ Repository 구현 (JPQL, Fetch Join)
✅ Service 계층 트랜잭션 처리
✅ 동시성 제어 (비관적 락)
✅ 재고 관리 로직
✅ 예외 처리
✅ DTO 변환
✅ 통합 테스트
```

---

## ❓ FAQ

### Q1: JDBC와 JPA 중 무엇을 선택해야 하나요?

**A**: 프로젝트 특성에 따라 결정합니다.

**JPA 선택하는 경우**:
- 일반적인 CRUD 중심 애플리케이션
- 빠른 개발 속도 필요
- 도메인 모델 중심 설계
- 데이터베이스 독립성 필요
- 예: 관리자 페이지, 일반적인 웹 서비스

**JDBC/MyBatis 선택하는 경우**:
- 복잡한 통계 쿼리 많음
- 성능 최적화가 중요
- SQL 직접 제어 필요
- 레거시 DB 스키마 사용
- 예: 리포팅 시스템, 배치 처리, 대용량 데이터 처리

**하이브리드 접근** (권장):
```java
@Service
public class OrderService {
    private final OrderRepository orderRepository;  // JPA: 일반 CRUD
    private final OrderStatisticsMapper statisticsMapper;  // MyBatis: 복잡한 통계

    @Transactional
    public Order createOrder(OrderRequest request) {
        return orderRepository.save(new Order(request));  // JPA
    }

    public SalesReport getDailySalesReport(LocalDate date) {
        return statisticsMapper.getDailySalesStatistics(date);  // MyBatis
    }
}
```

---

### Q2: Connection Pool 크기는 어떻게 설정해야 하나요?

**A**: 공식과 모니터링을 통해 결정합니다.

**HikariCP 권장 공식**:
```
최적 Connection Pool 크기 = (CPU 코어 수 × 2) + 디스크 수
```

**예시**:
```yaml
spring:
  datasource:
    hikari:
      # 4코어 CPU, SSD 1개 → (4 × 2) + 1 = 9
      maximum-pool-size: 10
      minimum-idle: 5
```

**실무 가이드**:

1. **초기 설정**: 10-20개로 시작
2. **모니터링 지표**:
   - Connection 대기 시간 (`hikaricp.connections.pending`)
   - 활성 Connection 수 (`hikaricp.connections.active`)
   - Connection timeout 발생 횟수
3. **튜닝**:
   - Connection 부족 시 → `maximum-pool-size` 증가
   - Connection 남을 시 → 감소 (리소스 절약)

**주의사항**:
```
❌ Pool을 너무 크게 설정하면:
   - 데이터베이스 부하 증가
   - 메모리 낭비
   - Context Switching 증가

✅ 적절한 크기:
   - 실제 동시 요청 수에 맞춤
   - DB 서버 Connection limit 고려
   - 모니터링 후 조정
```

---

### Q3: @Transactional의 readOnly 옵션은 왜 사용하나요?

**A**: 성능 최적화와 데이터 안정성을 위해 사용합니다.

**readOnly = true 효과**:

1. **성능 최적화**:
```java
@Transactional(readOnly = true)
public List<User> getAllUsers() {
    return userRepository.findAll();
}
```
- Dirty Checking (변경 감지) 비활성화
- Flush 모드 최적화
- 메모리 사용량 감소

2. **Read/Write Splitting**:
```java
@Transactional(readOnly = true)
public User getUser(Long id) {
    // Slave DB로 자동 라우팅
    return userRepository.findById(id).orElseThrow();
}

@Transactional
public User createUser(User user) {
    // Master DB로 자동 라우팅
    return userRepository.save(user);
}
```

3. **데이터 무결성**:
```java
@Transactional(readOnly = true)
public User getUser(Long id) {
    User user = userRepository.findById(id).orElseThrow();
    user.setName("변경");  // ❌ readOnly이므로 DB에 반영 안 됨 (안전)
    return user;
}
```

**사용 가이드**:
```
✅ readOnly = true 사용:
   - 조회 전용 메서드
   - 통계, 리포팅
   - 검색 기능

❌ readOnly 사용하지 않음:
   - 생성, 수정, 삭제 작업
   - 상태 변경이 필요한 경우
```

---

### Q4: N+1 문제는 어떻게 해결하나요?

**A**: Fetch Join, EntityGraph, Batch Size 등으로 해결합니다.

**문제 상황**:
```java
// N+1 쿼리 발생!
List<User> users = userRepository.findAll();  // 1번 쿼리
for (User user : users) {
    user.getOrders().size();  // N번 쿼리 (각 사용자마다)
}
```

**해결책 1: Fetch Join**:
```java
@Query("SELECT u FROM User u JOIN FETCH u.orders")
List<User> findAllWithOrders();

// 1번의 쿼리로 모든 데이터 조회
List<User> users = userRepository.findAllWithOrders();
```

**해결책 2: @EntityGraph**:
```java
@EntityGraph(attributePaths = "orders")
List<User> findAll();

// Fetch Join과 동일한 효과
```

**해결책 3: Batch Fetch Size**:
```yaml
spring:
  jpa:
    properties:
      hibernate:
        default_batch_fetch_size: 100
```
```java
List<User> users = userRepository.findAll();  // 1번
// Orders를 IN 절로 한 번에 조회 (100개씩)
// SELECT * FROM orders WHERE user_id IN (1,2,3,...,100)
```

**해결책 4: DTO 프로젝션**:
```java
@Query("SELECT new com.example.dto.UserOrderDTO(u.id, u.name, COUNT(o)) " +
       "FROM User u LEFT JOIN u.orders o " +
       "GROUP BY u.id, u.name")
List<UserOrderDTO> findAllWithOrderCount();
```

**선택 가이드**:
```
Fetch Join: 연관 엔티티 전체 필요
EntityGraph: Annotation으로 간단히 설정
Batch Size: 애플리케이션 전역 설정
DTO 프로젝션: 특정 필드만 필요할 때
```

---

### Q5: LazyInitializationException은 왜 발생하나요?

**A**: 트랜잭션이 종료된 후 Lazy Loading을 시도해서 발생합니다.

**발생 원인**:
```java
@Service
public class UserService {

    @Transactional
    public User getUser(Long id) {
        return userRepository.findById(id).orElseThrow();
        // 메서드 종료 → 트랜잭션 종료 → 영속성 컨텍스트 종료
    }
}

@RestController
public class UserController {

    @GetMapping("/users/{id}")
    public UserDTO getUser(@PathVariable Long id) {
        User user = userService.getUser(id);

        // ❌ 여기서 Lazy Loading 시도 → 예외 발생!
        return new UserDTO(user, user.getOrders());
    }
}
```

**해결책 1: Service에서 DTO 변환** (권장):
```java
@Service
public class UserService {

    @Transactional(readOnly = true)
    public UserDTO getUser(Long id) {
        User user = userRepository.findById(id).orElseThrow();

        // 트랜잭션 안에서 DTO 변환
        return new UserDTO(user, user.getOrders());
    }
}
```

**해결책 2: Fetch Join**:
```java
@Query("SELECT u FROM User u LEFT JOIN FETCH u.orders WHERE u.id = :id")
Optional<User> findByIdWithOrders(@Param("id") Long id);
```

**해결책 3: OSIV (권장하지 않음)**:
```yaml
spring:
  jpa:
    open-in-view: true  # 기본값, 성능 문제 가능
```

**권장 패턴**:
```
1. Service에서 필요한 데이터 모두 로드
2. DTO로 변환하여 반환
3. Controller는 DTO만 사용
```

---

### Q6: 동시성 문제는 어떻게 해결하나요?

**A**: 낙관적 락, 비관적 락, 분산 락을 사용합니다.

**문제 상황**:
```java
// 동시에 두 사용자가 같은 상품 주문
// 재고: 1개
User A: 재고 확인 (1개) → 주문 → 재고 차감
User B: 재고 확인 (1개) → 주문 → 재고 차감
// 결과: 재고 -1개 (오류!)
```

**해결책 1: 비관적 락** (Pessimistic Lock):
```java
@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("SELECT p FROM Product p WHERE p.id = :id")
Optional<Product> findByIdWithLock(@Param("id") Long id);

@Transactional
public Order createOrder(Long productId, int quantity) {
    // DB 레벨에서 락 획득 (다른 트랜잭션은 대기)
    Product product = productRepository.findByIdWithLock(productId)
        .orElseThrow();

    product.decreaseStock(quantity);
    // ...
}
```

**해결책 2: 낙관적 락** (Optimistic Lock):
```java
@Entity
public class Product {
    @Id
    private Long id;

    @Version
    private Long version;  // 버전 관리

    private Integer stockQuantity;
}

@Transactional
public Order createOrder(Long productId, int quantity) {
    Product product = productRepository.findById(productId).orElseThrow();
    product.decreaseStock(quantity);

    // 저장 시 version 체크
    // 다른 트랜잭션이 변경했으면 OptimisticLockException 발생
    productRepository.save(product);
}
```

**해결책 3: 분산 락** (Redis):
```java
@Transactional
public Order createOrder(Long productId, int quantity) {
    String lockKey = "product:" + productId;

    try (RLock lock = redissonClient.getLock(lockKey)) {
        boolean acquired = lock.tryLock(10, 3, TimeUnit.SECONDS);

        if (!acquired) {
            throw new LockAcquisitionException("락 획득 실패");
        }

        Product product = productRepository.findById(productId).orElseThrow();
        product.decreaseStock(quantity);
        // ...
    }
}
```

**선택 가이드**:
```
비관적 락: 충돌 많을 때, 단일 DB
낙관적 락: 충돌 적을 때, 재시도 가능
분산 락: 멀티 서버 환경, 복잡한 로직
```

---

### Q7: 트랜잭션 전파(Propagation)는 어떻게 동작하나요?

**A**: 메서드 간 트랜잭션 경계를 어떻게 설정할지 결정합니다.

**REQUIRED (기본값)**:
```java
@Service
public class UserService {
    @Autowired
    private PointService pointService;

    @Transactional  // Propagation.REQUIRED (기본값)
    public void registerUser(User user) {
        userRepository.save(user);

        // 같은 트랜잭션 참여
        pointService.giveWelcomePoints(user.getId());

        // 하나라도 실패하면 둘 다 롤백
    }
}

@Service
public class PointService {
    @Transactional
    public void giveWelcomePoints(Long userId) {
        // registerUser의 트랜잭션에 참여
        // 새로운 트랜잭션 생성 안 함
    }
}
```

**REQUIRES_NEW**:
```java
@Service
public class UserService {
    @Autowired
    private LogService logService;

    @Transactional
    public void registerUser(User user) {
        userRepository.save(user);

        // 새로운 트랜잭션으로 로그 저장
        logService.saveLog("User registered: " + user.getId());

        // 사용자 등록 실패해도 로그는 저장됨
    }
}

@Service
public class LogService {
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void saveLog(String message) {
        // 항상 새로운 트랜잭션 생성
        // 부모 트랜잭션과 독립적
    }
}
```

**MANDATORY**:
```java
@Transactional(propagation = Propagation.MANDATORY)
public void updatePoints(Long userId, int points) {
    // 반드시 기존 트랜잭션 안에서 호출되어야 함
    // 트랜잭션 없이 호출하면 예외 발생
}
```

**사용 예시**:
```
REQUIRED: 일반적인 비즈니스 로직 (기본값)
REQUIRES_NEW: 로그, 감사 기록 (독립적 저장)
MANDATORY: 반드시 트랜잭션 안에서 호출되어야 하는 메서드
SUPPORTS: 트랜잭션 있으면 참여, 없으면 없이 실행
NOT_SUPPORTED: 트랜잭션 없이 실행
```

---

## 📝 면접 질문

### 주니어 레벨 (5-7개)

1. **JDBC와 JPA의 차이점을 설명하고, 각각 어떤 상황에서 사용하는 것이 좋을까요?**

2. **Spring에서 DataSource란 무엇이며, Connection Pool은 왜 필요한가요?**

3. **@Transactional 어노테이션의 역할은 무엇이고, 어떤 원리로 동작하나요?**

4. **JPA에서 N+1 문제가 무엇인지 설명하고, 해결 방법을 제시해주세요.**

5. **LazyInitializationException은 왜 발생하며, 어떻게 해결할 수 있나요?**

6. **@Transactional에서 readOnly = true 옵션을 사용하는 이유는 무엇인가요?**

7. **Checked Exception과 Unchecked Exception 중 어떤 예외가 트랜잭션 롤백을 발생시키나요?**

---

### 중급 레벨 (3-5개)

1. **낙관적 락(Optimistic Lock)과 비관적 락(Pessimistic Lock)의 차이점을 설명하고, 각각의 사용 사례를 제시해주세요.**

2. **트랜잭션 격리 수준(Isolation Level)의 종류와 각 수준에서 발생할 수 있는 문제(Dirty Read, Non-Repeatable Read, Phantom Read)를 설명해주세요.**

3. **JPA의 영속성 컨텍스트(Persistence Context)는 무엇이며, 1차 캐시와 Dirty Checking의 동작 원리를 설명해주세요.**

4. **대용량 데이터를 처리할 때 JPA를 사용하면 메모리 문제가 발생할 수 있습니다. 이를 해결하기 위한 방법을 제시해주세요.**

5. **멀티 DataSource 환경에서 읽기/쓰기 분리(Read/Write Splitting)를 구현하는 방법을 설명해주세요.**

---

## 💡 면접 질문 답안

### 주니어 레벨 답안

**Q1: JDBC와 JPA의 차이점을 설명하고, 각각 어떤 상황에서 사용하는 것이 좋을까요?**

**A**:

**차이점**:
- **JDBC**:
  - Low-level API로 SQL을 직접 작성하고 실행
  - ResultSet을 수동으로 객체로 매핑
  - 모든 리소스(Connection, Statement, ResultSet)를 수동 관리
  - 보일러플레이트 코드가 많음

- **JPA**:
  - High-level ORM 기술로 객체 중심 개발
  - SQL을 자동 생성 (대부분의 경우)
  - 영속성 컨텍스트가 자동으로 객체 관리
  - 생산성이 높고 코드가 간결

**사용 상황**:
```
JDBC 사용:
✅ 복잡한 통계 쿼리 (GROUP BY, 복잡한 JOIN)
✅ 성능 최적화가 매우 중요
✅ 레거시 DB 스키마
✅ 배치 처리 (대용량 데이터)

JPA 사용:
✅ 일반적인 CRUD 애플리케이션
✅ 빠른 개발 속도 필요
✅ 도메인 모델 중심 설계
✅ 데이터베이스 독립성
```

**실무 예시**:
```java
// 일반 CRUD → JPA
@Service
public class UserService {
    public User createUser(User user) {
        return userRepository.save(user);  // 간단!
    }
}

// 복잡한 통계 → JDBC/MyBatis
@Mapper
public interface SalesMapper {
    @Select("""
        SELECT r.name, DATE(o.created_at) as date,
               SUM(o.total_amount) as sales
        FROM orders o JOIN restaurants r ON o.restaurant_id = r.id
        WHERE o.created_at >= #{startDate}
        GROUP BY r.id, DATE(o.created_at)
        ORDER BY sales DESC
    """)
    List<DailySales> getDailySales(@Param("startDate") LocalDate startDate);
}
```

---

**Q2: Spring에서 DataSource란 무엇이며, Connection Pool은 왜 필요한가요?**

**A**:

**DataSource**:
- 데이터베이스 연결 정보를 관리하는 객체
- JDBC Connection을 생성하는 팩토리
- Spring에서는 `javax.sql.DataSource` 인터페이스 사용

**Connection Pool**:
매번 새로운 Connection을 생성하는 대신, 미리 생성해둔 Connection을 재사용하는 기술

**필요한 이유**:
```
❌ Connection Pool 없이:
매 요청마다 새로운 Connection 생성
→ DB 연결 시간 ~100ms
→ 100 req/s → 10초 소요
→ 리소스 낭비

✅ Connection Pool 사용:
미리 생성된 Connection 재사용
→ Pool에서 가져오는 시간 ~1ms
→ 100 req/s → 0.1초 소요
→ 100배 빠름!
```

**실무 설정**:
```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb
    username: user
    password: password
    hikari:
      maximum-pool-size: 20      # 최대 Connection 수
      minimum-idle: 5            # 최소 유휴 Connection
      connection-timeout: 30000  # 연결 대기 시간 (30초)
      max-lifetime: 1800000      # Connection 최대 수명 (30분)
```

**동작 원리**:
```
1. 애플리케이션 시작 시 Connection Pool 생성
   → minimum-idle만큼 Connection 미리 생성

2. 요청 처리:
   - Connection 필요 → Pool에서 가져옴 (빠름)
   - 작업 완료 → Connection을 Pool에 반환 (재사용)

3. Pool이 가득 찬 경우:
   - connection-timeout만큼 대기
   - 시간 초과 → SQLException
```

---

**Q3: @Transactional 어노테이션의 역할은 무엇이고, 어떤 원리로 동작하나요?**

**A**:

**역할**:
데이터베이스 트랜잭션을 선언적으로 관리하여 데이터 무결성을 보장

**핵심 기능**:
1. **원자성(Atomicity)**: 모두 성공 또는 모두 실패
2. **일관성(Consistency)**: 데이터 무결성 유지
3. **격리성(Isolation)**: 동시 트랜잭션 간 간섭 방지
4. **지속성(Durability)**: 커밋된 데이터는 영구 보존

**동작 원리**:
```
1. Spring AOP 프록시 생성
   → UserService의 프록시 객체 생성

2. 메서드 호출 시:
   ① 프록시가 트랜잭션 시작 (TransactionManager.begin())
   ② 실제 비즈니스 로직 실행
   ③ 성공하면 COMMIT
   ④ 예외 발생하면 ROLLBACK
```

**코드 예시**:
```java
@Service
public class OrderService {

    @Transactional  // ← 트랜잭션 경계 설정
    public Order createOrder(OrderRequest request) {
        // 1. 주문 생성
        Order order = new Order(request);
        orderRepository.save(order);

        // 2. 재고 차감
        Product product = productRepository.findById(request.getProductId())
            .orElseThrow();
        product.decreaseStock(request.getQuantity());

        // 3. 포인트 차감
        Point point = pointRepository.findByUserId(request.getUserId())
            .orElseThrow();
        point.use(request.getUsePoints());

        // 모두 성공 → COMMIT
        // 하나라도 실패 → ROLLBACK (자동)

        return order;
    }
}
```

**내부 동작**:
```java
// Spring AOP가 생성한 프록시 (개념적 코드)
public class OrderServiceProxy extends OrderService {

    private TransactionManager txManager;
    private OrderService target;

    @Override
    public Order createOrder(OrderRequest request) {
        TransactionStatus status = txManager.getTransaction();

        try {
            // 실제 비즈니스 로직 실행
            Order order = target.createOrder(request);

            // 성공 → COMMIT
            txManager.commit(status);

            return order;
        } catch (RuntimeException e) {
            // 실패 → ROLLBACK
            txManager.rollback(status);
            throw e;
        }
    }
}
```

**주의사항**:
```java
// ❌ 같은 클래스 내부 호출은 트랜잭션 적용 안 됨
@Service
public class UserService {

    public void registerUser(User user) {
        this.saveUser(user);  // ❌ 프록시를 거치지 않음!
    }

    @Transactional
    private void saveUser(User user) {
        // 트랜잭션 적용 안 됨
    }
}

// ✅ 외부에서 호출해야 프록시 작동
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;

    @Transactional
    public void registerUser(User user) {
        userRepository.save(user);  // ✅ 트랜잭션 적용됨
    }
}
```

---

**Q4: JPA에서 N+1 문제가 무엇인지 설명하고, 해결 방법을 제시해주세요.**

**A**:

**N+1 문제란**:
연관된 엔티티를 조회할 때 추가 쿼리가 N번 더 실행되는 문제

**발생 상황**:
```java
@Entity
public class User {
    @Id
    private Long id;

    @OneToMany(mappedBy = "user")
    private List<Order> orders;  // Lazy Loading
}

// 서비스 코드
List<User> users = userRepository.findAll();  // 1번 쿼리

for (User user : users) {
    int orderCount = user.getOrders().size();  // N번 쿼리!
}
```

**실행되는 쿼리**:
```sql
-- 1번: 모든 사용자 조회
SELECT * FROM users;  -- 결과: 100명

-- N번: 각 사용자의 주문 조회
SELECT * FROM orders WHERE user_id = 1;
SELECT * FROM orders WHERE user_id = 2;
...
SELECT * FROM orders WHERE user_id = 100;

-- 총 101번 쿼리 실행! (1 + N)
```

**성능 영향**:
```
100명의 사용자 조회:
- 쿼리 횟수: 101번
- 응답 시간: ~1초 (각 쿼리 10ms)

1000명의 사용자 조회:
- 쿼리 횟수: 1001번
- 응답 시간: ~10초
→ 사용자 경험 악화!
```

**해결책 1: Fetch Join**:
```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    @Query("SELECT u FROM User u JOIN FETCH u.orders")
    List<User> findAllWithOrders();
}
```

**실행되는 쿼리**:
```sql
-- 1번의 쿼리로 모든 데이터 조회
SELECT u.*, o.*
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
```

**해결책 2: @EntityGraph**:
```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    @EntityGraph(attributePaths = "orders")
    List<User> findAll();
}
```

**해결책 3: Batch Fetch Size**:
```yaml
spring:
  jpa:
    properties:
      hibernate:
        default_batch_fetch_size: 100
```

**실행되는 쿼리**:
```sql
-- 1번: 사용자 조회
SELECT * FROM users;

-- 1번: Orders를 IN 절로 한 번에 조회
SELECT * FROM orders WHERE user_id IN (1, 2, 3, ..., 100);

-- 101번 → 2번으로 감소!
```

**해결책 4: DTO 프로젝션**:
```java
@Query("SELECT new com.example.dto.UserOrderCountDTO(u.id, u.name, COUNT(o)) " +
       "FROM User u LEFT JOIN u.orders o " +
       "GROUP BY u.id, u.name")
List<UserOrderCountDTO> findAllWithOrderCount();
```

**선택 기준**:
```
Fetch Join: 연관 엔티티 전체 데이터 필요
EntityGraph: Annotation 방식 선호
Batch Size: 애플리케이션 전역 적용
DTO 프로젝션: 특정 필드만 필요
```

---

**Q5: LazyInitializationException은 왜 발생하며, 어떻게 해결할 수 있나요?**

**A**:

**발생 원인**:
트랜잭션(영속성 컨텍스트)이 종료된 후 Lazy Loading을 시도할 때 발생

**구체적 상황**:
```java
@Service
public class UserService {

    @Transactional
    public User getUser(Long id) {
        User user = userRepository.findById(id).orElseThrow();
        return user;
        // ← 메서드 종료
        // → @Transactional 종료
        // → 영속성 컨텍스트(Session) 종료
    }
}

@RestController
public class UserController {

    @GetMapping("/users/{id}")
    public UserDTO getUser(@PathVariable Long id) {
        User user = userService.getUser(id);

        // ❌ 여기서 orders 접근 시 예외 발생!
        // → 이미 Session이 없어서 Lazy Loading 불가능
        return new UserDTO(user, user.getOrders());
    }
}
```

**에러 메시지**:
```
org.hibernate.LazyInitializationException:
failed to lazily initialize a collection of role: User.orders,
could not initialize proxy - no Session
```

**왜 발생하는가**:
```
1. Service 메서드 종료 → @Transactional 종료
2. 영속성 컨텍스트(Session) 종료
3. User 엔티티는 Detached 상태
4. Controller에서 user.getOrders() 호출
5. Lazy Loading 시도 → Session 없음 → 예외!
```

**해결책 1: Service에서 DTO 변환** (권장):
```java
@Service
public class UserService {

    @Transactional(readOnly = true)
    public UserDTO getUser(Long id) {
        User user = userRepository.findById(id).orElseThrow();

        // ✅ 트랜잭션 안에서 DTO 변환
        // → Lazy Loading 정상 작동
        return new UserDTO(user, user.getOrders());
    }
}

@RestController
public class UserController {

    @GetMapping("/users/{id}")
    public UserDTO getUser(@PathVariable Long id) {
        return userService.getUser(id);  // 이미 DTO
    }
}
```

**해결책 2: Fetch Join**:
```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    @Query("SELECT u FROM User u LEFT JOIN FETCH u.orders WHERE u.id = :id")
    Optional<User> findByIdWithOrders(@Param("id") Long id);
}

@Service
public class UserService {

    public User getUser(Long id) {
        // ✅ Orders가 이미 로드되어 있음
        return userRepository.findByIdWithOrders(id).orElseThrow();
    }
}
```

**해결책 3: Service에서 명시적 초기화**:
```java
@Service
public class UserService {

    @Transactional(readOnly = true)
    public User getUser(Long id) {
        User user = userRepository.findById(id).orElseThrow();

        // ✅ 트랜잭션 안에서 강제 로드
        user.getOrders().size();

        return user;
    }
}
```

**해결책 4: OSIV 활성화** (권장하지 않음):
```yaml
spring:
  jpa:
    open-in-view: true  # View 렌더링까지 영속성 컨텍스트 유지
```

**OSIV 사용하지 않는 이유**:
```
❌ OSIV (Open Session In View):
- DB Connection을 View까지 유지
- Connection Pool 고갈 위험
- 성능 저하
- 예상치 못한 쿼리 발생

✅ 권장 패턴:
- Service에서 필요한 데이터 모두 로드
- DTO로 변환하여 반환
- Controller는 DTO만 사용
```

---

**Q6: @Transactional에서 readOnly = true 옵션을 사용하는 이유는 무엇인가요?**

**A**:

**사용 이유**:
성능 최적화와 데이터 안정성을 위해 조회 전용 트랜잭션임을 명시

**효과 1: Dirty Checking 비활성화**:
```java
@Transactional(readOnly = true)
public User getUser(Long id) {
    User user = userRepository.findById(id).orElseThrow();

    // readOnly = true이므로 Dirty Checking 안 함
    // → 변경 감지를 위한 스냅샷 생성 안 함
    // → 메모리 절약

    return user;
}
```

**일반 트랜잭션의 Dirty Checking**:
```
1. 엔티티 조회 시 스냅샷 생성
2. 트랜잭션 커밋 전 스냅샷과 현재 상태 비교
3. 변경 사항 있으면 UPDATE 쿼리 실행

readOnly = true:
1. 스냅샷 생성 안 함 → 메모리 절약
2. 변경 감지 안 함 → CPU 절약
```

**효과 2: Flush 모드 최적화**:
```java
@Transactional(readOnly = true)
public List<User> searchUsers(String keyword) {
    // Flush 모드가 MANUAL로 설정됨
    // → 불필요한 Flush 발생 안 함
    return userRepository.findByNameContaining(keyword);
}
```

**효과 3: Read/Write Splitting**:
```java
@Service
public class PaymentService {

    // ✅ readOnly = true → Slave DB로 라우팅
    @Transactional(readOnly = true)
    public Payment getPayment(Long id) {
        return paymentRepository.findById(id).orElseThrow();
    }

    // ✅ readOnly = false (기본값) → Master DB로 라우팅
    @Transactional
    public Payment createPayment(PaymentRequest request) {
        return paymentRepository.save(new Payment(request));
    }
}
```

**DataSource 라우팅 설정**:
```java
public class ReplicationRoutingDataSource extends AbstractRoutingDataSource {

    @Override
    protected Object determineCurrentLookupKey() {
        boolean isReadOnly = TransactionSynchronizationManager
            .isCurrentTransactionReadOnly();

        if (isReadOnly) {
            return DataSourceType.SLAVE;  // 읽기 → Slave
        } else {
            return DataSourceType.MASTER;  // 쓰기 → Master
        }
    }
}
```

**효과 4: 데이터 무결성 보장**:
```java
@Transactional(readOnly = true)
public User getUser(Long id) {
    User user = userRepository.findById(id).orElseThrow();

    // 실수로 수정해도 DB에 반영 안 됨
    user.setName("변경");  // ❌ readOnly이므로 무시됨

    return user;
}
```

**사용 가이드**:
```
✅ readOnly = true 사용:
- 조회 전용 메서드 (findById, findAll, search 등)
- 통계, 리포팅
- 대시보드, 검색 기능

❌ readOnly 사용하지 않음 (기본값):
- 생성, 수정, 삭제 작업
- 상태 변경이 필요한 비즈니스 로직
```

**성능 개선 효과**:
```
readOnly = false (기본):
- 100명 조회 시 100개의 스냅샷 생성
- 메모리 사용량: ~1MB
- Flush 시간: ~50ms

readOnly = true:
- 스냅샷 생성 안 함
- 메모리 사용량: ~100KB (90% 절감)
- Flush 생략: ~5ms (90% 개선)
```

---

**Q7: Checked Exception과 Unchecked Exception 중 어떤 예외가 트랜잭션 롤백을 발생시키나요?**

**A**:

**기본 동작**:
- **Unchecked Exception (RuntimeException)**: 자동 롤백 ✅
- **Checked Exception (Exception)**: 롤백 안 됨 ❌

**Unchecked Exception - 자동 롤백**:
```java
@Service
public class OrderService {

    @Transactional
    public Order createOrder(OrderRequest request) {
        Order order = new Order(request);
        orderRepository.save(order);

        // ✅ RuntimeException → 자동 롤백
        throw new IllegalArgumentException("잘못된 요청");

        // 결과: 주문 저장 안 됨 (롤백)
    }
}
```

**Checked Exception - 롤백 안 됨**:
```java
@Service
public class OrderService {

    @Transactional
    public Order createOrder(OrderRequest request) throws Exception {
        Order order = new Order(request);
        orderRepository.save(order);

        // ❌ Checked Exception → 롤백 안 됨!
        throw new Exception("에러 발생");

        // 결과: 주문 저장됨! (커밋)
    }
}
```

**이유**:
```
Spring의 기본 정책:
- RuntimeException: 프로그래밍 오류 → 롤백 필요
- Checked Exception: 비즈니스 예외 → 처리 가능 → 롤백 불필요

예:
RuntimeException:
  - NullPointerException (버그)
  - IllegalArgumentException (버그)
  → 데이터 저장하면 안 됨

Checked Exception:
  - IOException (파일 없음 - 처리 가능)
  - SQLException (일시적 오류 - 재시도 가능)
  → 일부 데이터는 저장할 수 있음
```

**Checked Exception도 롤백하려면**:
```java
// 방법 1: rollbackFor 속성 사용
@Transactional(rollbackFor = Exception.class)
public Order createOrder(OrderRequest request) throws Exception {
    orderRepository.save(new Order(request));
    throw new Exception("에러");  // ✅ 롤백됨
}

// 방법 2: noRollbackFor로 제외 (반대)
@Transactional(noRollbackFor = IllegalArgumentException.class)
public Order createOrder(OrderRequest request) {
    orderRepository.save(new Order(request));
    throw new IllegalArgumentException("에러");  // ❌ 롤백 안 됨
}
```

**실무 패턴**:
```java
// ✅ 권장: RuntimeException 상속한 커스텀 예외 사용
public class InsufficientStockException extends RuntimeException {
    public InsufficientStockException(String message) {
        super(message);
    }
}

@Service
public class OrderService {

    @Transactional
    public Order createOrder(OrderRequest request) {
        Product product = productRepository.findById(request.getProductId())
            .orElseThrow();

        if (product.getStockQuantity() < request.getQuantity()) {
            // ✅ RuntimeException → 자동 롤백
            throw new InsufficientStockException("재고 부족");
        }

        product.decreaseStock(request.getQuantity());
        return orderRepository.save(new Order(request));
    }
}
```

**정리**:
```
Unchecked Exception (RuntimeException):
✅ 자동 롤백
✅ 실무에서 주로 사용
✅ 예: IllegalArgumentException, NullPointerException

Checked Exception (Exception):
❌ 기본적으로 롤백 안 됨
✅ rollbackFor 속성으로 롤백 가능
❌ 실무에서 권장하지 않음

권장 패턴:
→ RuntimeException 상속한 커스텀 예외 사용
→ 비즈니스 예외도 RuntimeException으로 정의
```

---

### 중급 레벨 답안

**Q1: 낙관적 락(Optimistic Lock)과 비관적 락(Pessimistic Lock)의 차이점을 설명하고, 각각의 사용 사례를 제시해주세요.**

**A**:

**차이점**:

| 구분 | 낙관적 락 | 비관적 락 |
|-----|----------|----------|
| **가정** | 충돌이 거의 없을 것 | 충돌이 자주 발생할 것 |
| **락 시점** | 커밋 시점 | 조회 시점 |
| **구현** | Version 컬럼 | DB 락 (SELECT FOR UPDATE) |
| **동시성** | 높음 | 낮음 |
| **성능** | 읽기 많을 때 유리 | 쓰기 많을 때 유리 |
| **실패 처리** | 재시도 필요 | 대기 후 처리 |

**낙관적 락 (Optimistic Lock)**:

**구현**:
```java
@Entity
public class Product {
    @Id
    private Long id;

    @Version  // ← 낙관적 락 활성화
    private Long version;

    private String name;
    private Integer stockQuantity;
}

@Service
public class ProductService {

    @Transactional
    public void decreaseStock(Long productId, int quantity) {
        Product product = productRepository.findById(productId)
            .orElseThrow();

        product.decreaseStock(quantity);

        // 저장 시 version 체크
        // version이 다르면 OptimisticLockException 발생
        productRepository.save(product);
    }
}
```

**동작 원리**:
```
시나리오: 두 사용자가 동시에 재고 차감

사용자 A:
1. Product 조회 (id=1, version=5, stock=10)
2. 재고 차감 (stock=9)
3. 저장 시도:
   UPDATE product
   SET stock=9, version=6
   WHERE id=1 AND version=5  ← 성공!

사용자 B:
1. Product 조회 (id=1, version=5, stock=10)
2. 재고 차감 (stock=8)
3. 저장 시도:
   UPDATE product
   SET stock=8, version=6
   WHERE id=1 AND version=5  ← 실패! (A가 version을 6으로 변경함)
   → OptimisticLockException 발생
```

**재시도 로직**:
```java
@Service
public class ProductService {

    private static final int MAX_RETRIES = 3;

    public void decreaseStockWithRetry(Long productId, int quantity) {
        int attempts = 0;

        while (attempts < MAX_RETRIES) {
            try {
                decreaseStock(productId, quantity);
                return;  // 성공
            } catch (OptimisticLockException e) {
                attempts++;
                if (attempts >= MAX_RETRIES) {
                    throw new StockUpdateFailedException("재고 업데이트 실패");
                }
                // 잠시 대기 후 재시도
                try {
                    Thread.sleep(100);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                }
            }
        }
    }

    @Transactional
    private void decreaseStock(Long productId, int quantity) {
        Product product = productRepository.findById(productId).orElseThrow();
        product.decreaseStock(quantity);
        productRepository.save(product);
    }
}
```

**비관적 락 (Pessimistic Lock)**:

**구현**:
```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT p FROM Product p WHERE p.id = :id")
    Optional<Product> findByIdWithLock(@Param("id") Long id);
}

@Service
public class ProductService {

    @Transactional
    public void decreaseStock(Long productId, int quantity) {
        // DB 레벨에서 락 획득 (다른 트랜잭션은 대기)
        Product product = productRepository.findByIdWithLock(productId)
            .orElseThrow();

        product.decreaseStock(quantity);

        // 트랜잭션 커밋 시 락 해제
    }
}
```

**실행되는 쿼리**:
```sql
-- MySQL
SELECT * FROM product WHERE id = 1 FOR UPDATE;

-- PostgreSQL
SELECT * FROM product WHERE id = 1 FOR UPDATE;

-- Oracle
SELECT * FROM product WHERE id = 1 FOR UPDATE;
```

**동작 원리**:
```
시나리오: 두 사용자가 동시에 재고 차감

사용자 A:
1. Product 조회 + 락 획득 (FOR UPDATE)
2. 재고 차감
3. 저장
4. 트랜잭션 커밋 → 락 해제

사용자 B:
1. Product 조회 시도 (FOR UPDATE)
   → A가 락을 보유 중이므로 대기
2. A의 트랜잭션 커밋 후 락 획득
3. 재고 차감 (이미 A가 차감한 재고 기준)
4. 저장
5. 트랜잭션 커밋 → 락 해제
```

**사용 사례**:

**낙관적 락 사용**:
```
✅ 충돌이 드문 경우
✅ 읽기가 많고 쓰기가 적은 경우
✅ 응답 시간이 중요한 경우
✅ 대기 시간을 최소화하고 싶은 경우

예:
- 게시글 수정 (한 사용자만 수정)
- 사용자 프로필 업데이트
- 설정 변경
- 조회수 업데이트
```

**비관적 락 사용**:
```
✅ 충돌이 자주 발생하는 경우
✅ 데이터 정합성이 매우 중요한 경우
✅ 재시도 로직 구현이 어려운 경우
✅ 순차 처리가 필요한 경우

예:
- 재고 차감 (여러 사용자가 동시 주문)
- 예약 시스템 (좌석, 호텔)
- 계좌 이체
- 포인트 차감
```

**실무 예시**:
```java
// ✅ 낙관적 락: 게시글 수정
@Transactional
public Post updatePost(Long postId, PostUpdateRequest request) {
    Post post = postRepository.findById(postId).orElseThrow();
    post.update(request);
    return postRepository.save(post);  // version 체크
}

// ✅ 비관적 락: 티켓 예매
@Transactional
public Reservation reserveTicket(Long eventId, int quantity) {
    Event event = eventRepository.findByIdWithLock(eventId).orElseThrow();

    if (event.getAvailableTickets() < quantity) {
        throw new InsufficientTicketsException("티켓 부족");
    }

    event.decreaseTickets(quantity);
    return reservationRepository.save(new Reservation(event, quantity));
}
```

**성능 비교**:
```
낙관적 락:
- 100 req/s → 평균 응답 시간: 10ms
- 충돌률 1% → 재시도 필요
- 동시성 높음

비관적 락:
- 100 req/s → 평균 응답 시간: 50ms
- 충돌 없음 (순차 처리)
- 동시성 낮음
```

---

**Q2: 트랜잭션 격리 수준(Isolation Level)의 종류와 각 수준에서 발생할 수 있는 문제(Dirty Read, Non-Repeatable Read, Phantom Read)를 설명해주세요.**

**A**:

**격리 수준 종류**:

| 격리 수준 | Dirty Read | Non-Repeatable Read | Phantom Read |
|---------|-----------|---------------------|--------------|
| **READ_UNCOMMITTED** | ⭕ 발생 | ⭕ 발생 | ⭕ 발생 |
| **READ_COMMITTED** | ✅ 방지 | ⭕ 발생 | ⭕ 발생 |
| **REPEATABLE_READ** | ✅ 방지 | ✅ 방지 | ⭕ 발생 |
| **SERIALIZABLE** | ✅ 방지 | ✅ 방지 | ✅ 방지 |

**1. Dirty Read (더티 리드)**:

**문제**:
커밋되지 않은 데이터를 읽는 문제

**예시**:
```
시간 | 트랜잭션 A | 트랜잭션 B
-----|-----------|------------
T1   | BEGIN     |
T2   | 계좌 잔액 = 1000원
T3   | UPDATE account SET balance = 500  (커밋 안 함)
T4   |           | BEGIN
T5   |           | SELECT balance → 500원 읽음 (Dirty Read!)
T6   | ROLLBACK  |
T7   |           | 500원 기준으로 작업 → 잘못된 데이터!
```

**코드**:
```java
// 트랜잭션 A
@Transactional(isolation = Isolation.READ_UNCOMMITTED)
public void transferMoney() {
    Account account = accountRepository.findById(1L).orElseThrow();
    account.setBalance(500);  // 커밋 안 함
    // ...
    throw new RuntimeException();  // 롤백!
}

// 트랜잭션 B
@Transactional(isolation = Isolation.READ_UNCOMMITTED)
public void checkBalance() {
    Account account = accountRepository.findById(1L).orElseThrow();
    System.out.println(account.getBalance());  // 500원 (Dirty Read!)
}
```

---

**2. Non-Repeatable Read (반복 불가능 읽기)**:

**문제**:
같은 쿼리를 두 번 실행했을 때 다른 결과가 나오는 문제

**예시**:
```
시간 | 트랜잭션 A | 트랜잭션 B
-----|-----------|------------
T1   | BEGIN     |
T2   | SELECT balance → 1000원
T3   |           | BEGIN
T4   |           | UPDATE account SET balance = 500
T5   |           | COMMIT
T6   | SELECT balance → 500원 (다른 결과!)
```

**코드**:
```java
// 트랜잭션 A
@Transactional(isolation = Isolation.READ_COMMITTED)
public void processOrder() {
    Product product = productRepository.findById(1L).orElseThrow();
    int stock1 = product.getStockQuantity();  // 100

    // ... 다른 작업 ...

    // 다시 조회
    product = productRepository.findById(1L).orElseThrow();
    int stock2 = product.getStockQuantity();  // 50 (Non-Repeatable Read!)

    if (stock1 != stock2) {
        // 재고가 변경됨!
    }
}

// 트랜잭션 B
@Transactional
public void decreaseStock() {
    Product product = productRepository.findById(1L).orElseThrow();
    product.decreaseStock(50);
}
```

---

**3. Phantom Read (팬텀 리드)**:

**문제**:
같은 조건의 쿼리를 두 번 실행했을 때 새로운 행이 나타나거나 사라지는 문제

**예시**:
```
시간 | 트랜잭션 A | 트랜잭션 B
-----|-----------|------------
T1   | BEGIN     |
T2   | SELECT COUNT(*) WHERE age >= 20 → 10명
T3   |           | BEGIN
T4   |           | INSERT INTO users (age=25)
T5   |           | COMMIT
T6   | SELECT COUNT(*) WHERE age >= 20 → 11명 (Phantom Read!)
```

**코드**:
```java
// 트랜잭션 A
@Transactional(isolation = Isolation.REPEATABLE_READ)
public void calculateStatistics() {
    List<User> users1 = userRepository.findByAgeGreaterThanEqual(20);
    int count1 = users1.size();  // 10명

    // ... 다른 작업 ...

    List<User> users2 = userRepository.findByAgeGreaterThanEqual(20);
    int count2 = users2.size();  // 11명 (Phantom Read!)
}

// 트랜잭션 B
@Transactional
public void createUser() {
    User user = new User("홍길동", 25);
    userRepository.save(user);
}
```

---

**격리 수준별 설명**:

**1. READ_UNCOMMITTED (레벨 0)**:
```java
@Transactional(isolation = Isolation.READ_UNCOMMITTED)
public void example() {
    // 커밋되지 않은 데이터도 읽음
    // 가장 낮은 격리 수준, 가장 높은 동시성
}
```

**특징**:
- Dirty Read, Non-Repeatable Read, Phantom Read 모두 발생
- 거의 사용하지 않음
- 데이터 정합성 보장 안 됨

---

**2. READ_COMMITTED (레벨 1)** - Oracle, PostgreSQL 기본값:
```java
@Transactional(isolation = Isolation.READ_COMMITTED)
public void example() {
    // 커밋된 데이터만 읽음
}
```

**특징**:
- Dirty Read 방지
- Non-Repeatable Read, Phantom Read 발생 가능
- 실무에서 많이 사용

**동작**:
```sql
-- 트랜잭션 A
BEGIN;
UPDATE account SET balance = 500 WHERE id = 1;
-- 아직 커밋 안 함

-- 트랜잭션 B (READ_COMMITTED)
SELECT balance FROM account WHERE id = 1;
-- → 1000원 반환 (커밋 안 된 500원은 안 읽음)

-- 트랜잭션 A
COMMIT;

-- 트랜잭션 B
SELECT balance FROM account WHERE id = 1;
-- → 500원 반환 (커밋된 데이터 읽음)
```

---

**3. REPEATABLE_READ (레벨 2)** - MySQL 기본값:
```java
@Transactional(isolation = Isolation.REPEATABLE_READ)
public void example() {
    // 같은 데이터를 여러 번 읽어도 동일한 결과
}
```

**특징**:
- Dirty Read, Non-Repeatable Read 방지
- Phantom Read는 발생 가능 (MySQL은 Next-Key Lock으로 방지)
- 트랜잭션 시작 시점의 스냅샷 사용

**동작**:
```sql
-- 트랜잭션 A (REPEATABLE_READ)
BEGIN;
SELECT balance FROM account WHERE id = 1;  -- 1000원

-- 트랜잭션 B
UPDATE account SET balance = 500 WHERE id = 1;
COMMIT;

-- 트랜잭션 A
SELECT balance FROM account WHERE id = 1;  -- 여전히 1000원!
-- (스냅샷 사용, Non-Repeatable Read 방지)
COMMIT;
```

---

**4. SERIALIZABLE (레벨 3)**:
```java
@Transactional(isolation = Isolation.SERIALIZABLE)
public void example() {
    // 완전한 격리, 순차 실행과 동일
}
```

**특징**:
- Dirty Read, Non-Repeatable Read, Phantom Read 모두 방지
- 가장 높은 격리 수준, 가장 낮은 동시성
- 성능 저하 심각

**동작**:
```sql
-- 트랜잭션 A (SERIALIZABLE)
BEGIN;
SELECT * FROM account WHERE balance > 1000;

-- 트랜잭션 B
INSERT INTO account (balance) VALUES (2000);
-- → 대기! (A가 끝날 때까지)

-- 트랜잭션 A
SELECT * FROM account WHERE balance > 1000;
-- 동일한 결과 (Phantom Read 방지)
COMMIT;

-- 트랜잭션 B
-- 이제 INSERT 실행됨
COMMIT;
```

---

**실무 선택 가이드**:

```java
// ✅ 일반적인 조회: READ_COMMITTED
@Transactional(isolation = Isolation.READ_COMMITTED, readOnly = true)
public List<User> getUsers() {
    return userRepository.findAll();
}

// ✅ 통계, 리포트: REPEATABLE_READ
@Transactional(isolation = Isolation.REPEATABLE_READ, readOnly = true)
public SalesReport generateReport() {
    // 일관된 데이터로 통계 생성
}

// ✅ 금융 거래: SERIALIZABLE (또는 비관적 락)
@Transactional(isolation = Isolation.SERIALIZABLE)
public void transferMoney(Long fromId, Long toId, BigDecimal amount) {
    // 완전한 격리 보장
}
```

**성능 vs 정합성**:
```
READ_UNCOMMITTED: 동시성 최고, 정합성 최저 (사용 비권장)
READ_COMMITTED: 동시성 높음, 정합성 보통 (일반적 사용)
REPEATABLE_READ: 동시성 보통, 정합성 높음 (통계, 리포트)
SERIALIZABLE: 동시성 최저, 정합성 최고 (금융, 중요 거래)
```

---

**Q3: JPA의 영속성 컨텍스트(Persistence Context)는 무엇이며, 1차 캐시와 Dirty Checking의 동작 원리를 설명해주세요.**

**A**:

**영속성 컨텍스트란**:
엔티티를 영구 저장하는 환경으로, 엔티티와 DB 사이의 중간 계층 역할

**구조**:
```
Application ↔ EntityManager ↔ Persistence Context ↔ Database
                                     ↓
                            - 1차 캐시
                            - 쓰기 지연 SQL 저장소
                            - 변경 감지 (Dirty Checking)
                            - 지연 로딩
```

**엔티티 생명주기**:
```
비영속 (New/Transient)
    ↓ persist()
영속 (Managed) ← 영속성 컨텍스트에서 관리
    ↓ detach(), clear(), close()
준영속 (Detached)
    ↓ remove()
삭제 (Removed)
```

---

**1차 캐시 (First Level Cache)**:

**구조**:
```
영속성 컨텍스트 내부:
┌─────────────────────────────────┐
│  1차 캐시 (Map<ID, Entity>)    │
├─────────────────────────────────┤
│  @Id(1) → User(id=1, name="홍길동") │
│  @Id(2) → User(id=2, name="김철수") │
│  @Id(3) → User(id=3, name="이영희") │
└─────────────────────────────────┘
```

**동작 원리**:
```java
@Transactional
public void example() {
    // 1. 최초 조회: DB에서 조회 후 1차 캐시에 저장
    User user1 = userRepository.findById(1L).orElseThrow();
    // SELECT * FROM users WHERE id = 1;

    // 2. 같은 ID 재조회: 1차 캐시에서 조회 (DB 접근 안 함!)
    User user2 = userRepository.findById(1L).orElseThrow();
    // 쿼리 실행 안 됨!

    // 3. 동일성 보장
    System.out.println(user1 == user2);  // true
}
```

**실제 예시**:
```java
@Service
@Transactional
public class UserService {

    @Autowired
    private UserRepository userRepository;

    public void processUser(Long userId) {
        // 1차 조회: DB 접근
        User user = userRepository.findById(userId).orElseThrow();
        System.out.println(user.getName());

        // 2차 조회: 1차 캐시에서 조회 (DB 접근 X)
        User sameUser = userRepository.findById(userId).orElseThrow();
        System.out.println(sameUser.getName());

        // 3차 조회: 1차 캐시에서 조회 (DB 접근 X)
        User againUser = userRepository.findById(userId).orElseThrow();
        System.out.println(againUser.getName());

        // 동일한 인스턴스
        System.out.println(user == sameUser);  // true
        System.out.println(user == againUser);  // true
    }
}
```

**실행되는 쿼리**:
```sql
-- 1번만 실행됨
SELECT * FROM users WHERE id = 1;
```

**장점**:
```
1. 성능 최적화:
   - 같은 엔티티 여러 번 조회 시 DB 접근 1번만
   - 네트워크 비용 절감

2. 동일성 보장:
   - 같은 ID의 엔티티는 같은 인스턴스
   - == 비교 가능

3. 트랜잭션 격리:
   - 트랜잭션 내에서 일관된 데이터
```

**한계**:
```
❌ 트랜잭션 범위:
   - 트랜잭션 종료 시 1차 캐시 삭제
   - 다른 트랜잭션과 공유 안 됨

❌ 애플리케이션 범위:
   - 같은 애플리케이션 인스턴스 내에서만
   - 분산 환경에서는 효과 없음
```

---

**Dirty Checking (변경 감지)**:

**동작 원리**:
```
1. 엔티티 최초 로드 시 스냅샷 생성
2. 트랜잭션 커밋 전 스냅샷과 현재 상태 비교
3. 변경 사항 있으면 UPDATE 쿼리 자동 생성
4. 쿼리 실행 후 커밋
```

**코드 예시**:
```java
@Transactional
public void updateUser(Long userId, String newName) {
    // 1. User 조회 → 영속 상태 + 스냅샷 생성
    User user = userRepository.findById(userId).orElseThrow();
    // 스냅샷: User(id=1, name="홍길동", email="hong@example.com")

    // 2. 엔티티 변경 (setter 호출)
    user.setName(newName);
    // 현재 상태: User(id=1, name="김철수", email="hong@example.com")

    // 3. 명시적 save() 호출 불필요!
    // userRepository.save(user);  // 필요 없음

    // 4. 트랜잭션 커밋 시:
    //    - 스냅샷과 현재 상태 비교
    //    - name이 변경됨 감지
    //    - UPDATE 쿼리 자동 생성 및 실행
}
```

**실행되는 쿼리**:
```sql
-- 1. 조회
SELECT * FROM users WHERE id = 1;

-- 2. 변경 감지 후 자동 UPDATE
UPDATE users
SET name = '김철수', updated_at = '2025-10-19 10:30:00'
WHERE id = 1;
```

**내부 동작 (개념적 코드)**:
```java
// EntityManager 내부
public class PersistenceContext {

    // 1차 캐시
    private Map<Object, Object> entityCache = new HashMap<>();

    // 스냅샷
    private Map<Object, Object> snapshots = new HashMap<>();

    public <T> T find(Class<T> entityClass, Object id) {
        // 1차 캐시 확인
        if (entityCache.containsKey(id)) {
            return (T) entityCache.get(id);
        }

        // DB에서 조회
        T entity = loadFromDatabase(entityClass, id);

        // 1차 캐시에 저장
        entityCache.put(id, entity);

        // 스냅샷 저장
        snapshots.put(id, clone(entity));

        return entity;
    }

    public void flush() {
        // 변경 감지
        for (Object id : entityCache.keySet()) {
            Object entity = entityCache.get(id);
            Object snapshot = snapshots.get(id);

            if (!equals(entity, snapshot)) {
                // 변경 감지됨 → UPDATE 쿼리 생성
                generateUpdateQuery(entity);
            }
        }
    }
}
```

**복잡한 예시**:
```java
@Transactional
public void updateMultipleFields(Long userId) {
    User user = userRepository.findById(userId).orElseThrow();
    // 스냅샷: User(id=1, name="홍길동", email="hong@example.com", age=20)

    // 여러 필드 변경
    user.setName("김철수");
    user.setEmail("kim@example.com");
    user.setAge(25);

    // 트랜잭션 커밋 시:
    // UPDATE users
    // SET name='김철수', email='kim@example.com', age=25
    // WHERE id=1;
}
```

**Dirty Checking 비활성화**:
```java
// readOnly = true → Dirty Checking 안 함
@Transactional(readOnly = true)
public User getUser(Long userId) {
    User user = userRepository.findById(userId).orElseThrow();

    // 변경해도 DB에 반영 안 됨 (스냅샷 생성 안 함)
    user.setName("변경");

    return user;
}
```

---

**쓰기 지연 (Transactional Write-Behind)**:

**동작**:
```java
@Transactional
public void saveMultipleUsers() {
    User user1 = new User("홍길동");
    userRepository.save(user1);
    // INSERT 쿼리 즉시 실행 안 함!

    User user2 = new User("김철수");
    userRepository.save(user2);
    // INSERT 쿼리 즉시 실행 안 함!

    User user3 = new User("이영희");
    userRepository.save(user3);
    // INSERT 쿼리 즉시 실행 안 함!

    // 트랜잭션 커밋 시 한 번에 실행
    // INSERT INTO users ... (user1)
    // INSERT INTO users ... (user2)
    // INSERT INTO users ... (user3)
}
```

**장점**:
```
1. 성능 최적화:
   - 쿼리를 모아서 한 번에 실행
   - 배치 처리 가능

2. 트랜잭션 무결성:
   - 모두 성공 또는 모두 실패
```

---

**실무 활용**:

```java
@Service
@Transactional
public class OrderService {

    public Order createOrder(OrderRequest request) {
        // 1. User 조회 (1차 캐시 활용)
        User user = userRepository.findById(request.getUserId())
            .orElseThrow();

        // 2. Order 생성 (쓰기 지연)
        Order order = new Order(user, request);
        orderRepository.save(order);  // 쿼리 즉시 실행 안 함

        // 3. 재고 차감 (Dirty Checking)
        Product product = productRepository.findById(request.getProductId())
            .orElseThrow();
        product.decreaseStock(request.getQuantity());  // save() 불필요

        // 4. 포인트 차감 (Dirty Checking)
        Point point = pointRepository.findByUserId(user.getId())
            .orElseThrow();
        point.use(request.getUsePoints());  // save() 불필요

        // 5. User 재조회 (1차 캐시에서 조회, DB 접근 안 함)
        User sameUser = userRepository.findById(request.getUserId())
            .orElseThrow();
        System.out.println(user == sameUser);  // true

        // 트랜잭션 커밋 시:
        // - INSERT order (쓰기 지연)
        // - UPDATE product (Dirty Checking)
        // - UPDATE point (Dirty Checking)

        return order;
    }
}
```

**정리**:
```
영속성 컨텍스트:
→ 엔티티와 DB 사이의 중간 계층

1차 캐시:
→ 같은 엔티티 여러 번 조회 시 성능 최적화
→ 동일성 보장 (== 비교 가능)
→ 트랜잭션 범위

Dirty Checking:
→ 엔티티 변경 시 자동 UPDATE
→ save() 호출 불필요
→ 스냅샷과 현재 상태 비교

쓰기 지연:
→ 쿼리를 모아서 한 번에 실행
→ 배치 처리, 트랜잭션 무결성
```

---

**Q4: 대용량 데이터를 처리할 때 JPA를 사용하면 메모리 문제가 발생할 수 있습니다. 이를 해결하기 위한 방법을 제시해주세요.**

**A**:

**문제 상황**:
```java
// ❌ 100만 건 조회 시 OutOfMemoryError!
@Transactional
public void processAllUsers() {
    List<User> users = userRepository.findAll();  // 100만 건

    for (User user : users) {
        processUser(user);
    }
    // 메모리: 100만 개 객체 + 100만 개 스냅샷 = OutOfMemoryError!
}
```

**원인**:
```
1. JPA는 모든 엔티티를 영속성 컨텍스트에 보관
2. Dirty Checking을 위한 스냅샷 생성
3. 메모리 사용량 = (엔티티 크기 × 2) × 개수

100만 건 × 2KB = 2GB
```

---

**해결책 1: 페이징 (Pagination)**:

```java
@Service
public class UserBatchService {

    @Autowired
    private UserRepository userRepository;

    @Transactional
    public void processAllUsers() {
        int pageSize = 1000;
        int pageNumber = 0;

        Page<User> page;
        do {
            // 1000건씩 처리
            Pageable pageable = PageRequest.of(pageNumber, pageSize);
            page = userRepository.findAll(pageable);

            for (User user : page.getContent()) {
                processUser(user);
            }

            pageNumber++;

            // 중요: 영속성 컨텍스트 초기화
            entityManager.clear();

        } while (page.hasNext());
    }

    private void processUser(User user) {
        // 처리 로직
    }
}
```

**장점**:
- 메모리 사용량 일정하게 유지
- 간단한 구현

**단점**:
- 페이지 번호 증가 시 OFFSET 성능 저하
- `OFFSET 999000 LIMIT 1000` → 느림

---

**해결책 2: Cursor 기반 페이징**:

```java
@Service
public class UserBatchService {

    @Autowired
    private UserRepository userRepository;

    @PersistenceContext
    private EntityManager entityManager;

    @Transactional
    public void processAllUsers() {
        Long lastId = 0L;
        int batchSize = 1000;

        while (true) {
            // Cursor 방식: id > lastId ORDER BY id LIMIT 1000
            List<User> users = userRepository.findUsersAfter(lastId, batchSize);

            if (users.isEmpty()) {
                break;
            }

            for (User user : users) {
                processUser(user);
            }

            // 마지막 ID 저장
            lastId = users.get(users.size() - 1).getId();

            // 영속성 컨텍스트 초기화
            entityManager.flush();
            entityManager.clear();
        }
    }
}

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    @Query("SELECT u FROM User u WHERE u.id > :lastId ORDER BY u.id")
    List<User> findUsersAfter(@Param("lastId") Long lastId,
                              @Param("limit") int limit);
}
```

**실행되는 쿼리**:
```sql
-- 1회차
SELECT * FROM users WHERE id > 0 ORDER BY id LIMIT 1000;

-- 2회차
SELECT * FROM users WHERE id > 1000 ORDER BY id LIMIT 1000;

-- 3회차
SELECT * FROM users WHERE id > 2000 ORDER BY id LIMIT 1000;
```

**장점**:
- OFFSET 없이 인덱스만 사용 → 빠름
- 페이지 번호와 무관하게 일정한 성능

---

**해결책 3: Scroll (Stream) API**:

```java
@Service
public class UserBatchService {

    @PersistenceContext
    private EntityManager entityManager;

    @Transactional(readOnly = true)
    public void processAllUsers() {
        Session session = entityManager.unwrap(Session.class);

        ScrollableResults scroll = session.createQuery(
            "SELECT u FROM User u", User.class)
            .setFetchSize(1000)  // DB에서 가져올 크기
            .scroll(ScrollMode.FORWARD_ONLY);

        int count = 0;
        while (scroll.next()) {
            User user = (User) scroll.get(0);
            processUser(user);

            if (++count % 1000 == 0) {
                // 1000건마다 영속성 컨텍스트 초기화
                entityManager.flush();
                entityManager.clear();
            }
        }

        scroll.close();
    }
}
```

---

**해결책 4: Native Query + JDBC Batch**:

```java
@Service
public class UserBatchService {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    public void processAllUsers() {
        jdbcTemplate.query(
            "SELECT * FROM users",
            rs -> {
                while (rs.next()) {
                    User user = mapRowToUser(rs);
                    processUser(user);
                }
            }
        );
    }

    private User mapRowToUser(ResultSet rs) throws SQLException {
        User user = new User();
        user.setId(rs.getLong("id"));
        user.setName(rs.getString("name"));
        user.setEmail(rs.getString("email"));
        return user;
    }
}
```

**장점**:
- JPA 없이 순수 JDBC → 메모리 효율적
- 영속성 컨텍스트 사용 안 함

**단점**:
- 수동 매핑 필요
- JPA 기능 사용 불가 (Dirty Checking 등)

---

**해결책 5: @Modifying with Bulk Update**:

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    @Modifying
    @Query("UPDATE User u SET u.status = :status WHERE u.lastLoginDate < :date")
    int bulkUpdateStatus(@Param("status") UserStatus status,
                         @Param("date") LocalDateTime date);
}

@Service
public class UserBatchService {

    @Transactional
    public void deactivateInactiveUsers() {
        LocalDateTime threshold = LocalDateTime.now().minusMonths(6);

        // 한 번의 쿼리로 대량 업데이트
        int count = userRepository.bulkUpdateStatus(
            UserStatus.INACTIVE,
            threshold
        );

        log.info("Deactivated {} users", count);
    }
}
```

**실행되는 쿼리**:
```sql
-- 한 번에 수백만 건 UPDATE
UPDATE users
SET status = 'INACTIVE'
WHERE last_login_date < '2024-04-19';
```

**주의사항**:
```java
@Modifying(clearAutomatically = true)  // 영속성 컨텍스트 자동 초기화
@Query("UPDATE User u SET u.status = :status WHERE u.id = :id")
int updateStatus(@Param("id") Long id, @Param("status") UserStatus status);
```

---

**해결책 6: 배치 처리 + 멀티 스레드**:

```java
@Service
public class UserBatchService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private ThreadPoolTaskExecutor taskExecutor;

    public void processAllUsersInParallel() {
        long totalCount = userRepository.count();
        int batchSize = 10000;
        int threads = 10;
        int partitionSize = (int) (totalCount / threads);

        List<CompletableFuture<Void>> futures = new ArrayList<>();

        for (int i = 0; i < threads; i++) {
            final int start = i * partitionSize;
            final int end = (i == threads - 1) ?
                (int) totalCount : (i + 1) * partitionSize;

            CompletableFuture<Void> future = CompletableFuture.runAsync(
                () -> processBatch(start, end, batchSize),
                taskExecutor
            );

            futures.add(future);
        }

        // 모든 스레드 완료 대기
        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
            .join();
    }

    @Transactional
    public void processBatch(int start, int end, int batchSize) {
        for (int offset = start; offset < end; offset += batchSize) {
            List<User> users = userRepository.findUsers(offset, batchSize);

            for (User user : users) {
                processUser(user);
            }

            entityManager.flush();
            entityManager.clear();
        }
    }
}
```

---

**성능 비교**:

| 방법 | 100만 건 처리 시간 | 메모리 사용 | 난이도 |
|-----|-------------------|-----------|--------|
| **findAll()** | 60초 | 2GB | 쉬움 |
| **Pagination** | 45초 | 20MB | 쉬움 |
| **Cursor** | 30초 | 10MB | 보통 |
| **Scroll API** | 25초 | 10MB | 보통 |
| **JDBC Batch** | 20초 | 5MB | 어려움 |
| **Bulk Update** | 5초 | 1MB | 쉬움 |
| **멀티 스레드** | 10초 | 50MB | 어려움 |

---

**실무 권장 패턴**:

```java
@Service
public class UserBatchService {

    // ✅ 대량 조회 + 처리: Cursor 방식
    @Transactional(readOnly = true)
    public void exportAllUsers() {
        Long lastId = 0L;
        int batchSize = 1000;

        while (true) {
            List<User> users = userRepository.findUsersAfter(lastId, batchSize);
            if (users.isEmpty()) break;

            exportToFile(users);

            lastId = users.get(users.size() - 1).getId();
            entityManager.clear();  // 메모리 정리
        }
    }

    // ✅ 대량 업데이트: Bulk Update
    @Transactional
    public void deactivateInactiveUsers() {
        userRepository.bulkUpdateInactiveUsers();
    }

    // ✅ 복잡한 처리: 페이징 + 명시적 초기화
    @Transactional
    public void processComplexLogic() {
        int pageNumber = 0;
        int pageSize = 100;
        Page<User> page;

        do {
            page = userRepository.findAll(PageRequest.of(pageNumber++, pageSize));

            for (User user : page) {
                // 복잡한 비즈니스 로직
                complexProcessing(user);
            }

            entityManager.flush();
            entityManager.clear();

        } while (page.hasNext());
    }
}
```

---

**Q5: 멀티 DataSource 환경에서 읽기/쓰기 분리(Read/Write Splitting)를 구현하는 방법을 설명해주세요.**

**A**:

**아키텍처**:
```
Application
    ↓
RoutingDataSource (동적 라우팅)
    ↓
    ├─→ Master DB (쓰기)
    └─→ Slave DB (읽기)
```

**구현 단계**:

**1단계: DataSource 설정**:

```yaml
# application.yml
spring:
  datasource:
    master:
      jdbc-url: jdbc:mysql://master-db:3306/mydb
      username: master_user
      password: master_password
      driver-class-name: com.mysql.cj.jdbc.Driver
      hikari:
        maximum-pool-size: 20
        minimum-idle: 5

    slave:
      jdbc-url: jdbc:mysql://slave-db:3306/mydb
      username: slave_user
      password: slave_password
      driver-class-name: com.mysql.cj.jdbc.Driver
      hikari:
        maximum-pool-size: 30  # Slave는 읽기가 많으므로 Pool 크기 크게
        minimum-idle: 10
```

**2단계: DataSource Configuration**:

```java
@Configuration
public class DataSourceConfig {

    @Bean
    @ConfigurationProperties("spring.datasource.master")
    public DataSource masterDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    @ConfigurationProperties("spring.datasource.slave")
    public DataSource slaveDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    @Primary
    public DataSource routingDataSource(
            @Qualifier("masterDataSource") DataSource master,
            @Qualifier("slaveDataSource") DataSource slave) {

        ReplicationRoutingDataSource routingDataSource =
            new ReplicationRoutingDataSource();

        Map<Object, Object> dataSourceMap = new HashMap<>();
        dataSourceMap.put(DataSourceType.MASTER, master);
        dataSourceMap.put(DataSourceType.SLAVE, slave);

        routingDataSource.setTargetDataSources(dataSourceMap);
        routingDataSource.setDefaultTargetDataSource(master);

        return routingDataSource;
    }

    @Bean
    public DataSource dataSource(
            @Qualifier("routingDataSource") DataSource routingDataSource) {

        // LazyConnectionDataSourceProxy로 래핑
        // → 트랜잭션 시작 후 실제 Connection 획득 시점에 라우팅 결정
        return new LazyConnectionDataSourceProxy(routingDataSource);
    }
}
```

**3단계: 동적 라우팅 DataSource**:

```java
public class ReplicationRoutingDataSource extends AbstractRoutingDataSource {

    @Override
    protected Object determineCurrentLookupKey() {
        // 현재 트랜잭션이 readOnly인지 확인
        boolean isReadOnly = TransactionSynchronizationManager
            .isCurrentTransactionReadOnly();

        if (isReadOnly) {
            log.debug("Routing to SLAVE DataSource (readOnly=true)");
            return DataSourceType.SLAVE;
        } else {
            log.debug("Routing to MASTER DataSource (readOnly=false)");
            return DataSourceType.MASTER;
        }
    }
}

enum DataSourceType {
    MASTER,
    SLAVE
}
```

**4단계: Service 계층에서 사용**:

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class UserService {

    private final UserRepository userRepository;

    // ✅ 쓰기 작업 → Master DB
    @Transactional
    public User createUser(UserRequest request) {
        log.info("Creating user - will use MASTER DB");

        User user = new User();
        user.setName(request.getName());
        user.setEmail(request.getEmail());

        return userRepository.save(user);
    }

    // ✅ 읽기 작업 → Slave DB
    @Transactional(readOnly = true)
    public User getUser(Long id) {
        log.info("Fetching user - will use SLAVE DB");

        return userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));
    }

    // ✅ 읽기 작업 → Slave DB
    @Transactional(readOnly = true)
    public List<User> searchUsers(String keyword) {
        log.info("Searching users - will use SLAVE DB");

        return userRepository.findByNameContaining(keyword);
    }

    // ✅ 쓰기 작업 → Master DB
    @Transactional
    public User updateUser(Long id, UserUpdateRequest request) {
        log.info("Updating user - will use MASTER DB");

        User user = userRepository.findById(id).orElseThrow();
        user.setName(request.getName());
        user.setEmail(request.getEmail());

        return userRepository.save(user);
    }

    // ✅ 쓰기 포함 → Master DB
    @Transactional
    public void processOrder(OrderRequest request) {
        log.info("Processing order - will use MASTER DB");

        // 읽기 작업도 Master에서 수행 (같은 트랜잭션)
        User user = userRepository.findById(request.getUserId())
            .orElseThrow();

        // 쓰기 작업
        Order order = new Order(user, request);
        orderRepository.save(order);
    }
}
```

**실행되는 쿼리**:

```sql
-- @Transactional(readOnly = true) → Slave DB
SELECT * FROM users WHERE id = 1;

-- @Transactional → Master DB
INSERT INTO users (name, email) VALUES ('홍길동', 'hong@example.com');
UPDATE users SET name = '김철수' WHERE id = 1;
DELETE FROM users WHERE id = 1;
```

---

**고급 기능: Slave 장애 시 Failover**:

```java
public class ReplicationRoutingDataSource extends AbstractRoutingDataSource {

    private final DataSource masterDataSource;
    private final DataSource slaveDataSource;
    private volatile boolean slaveAvailable = true;

    @Override
    protected Object determineCurrentLookupKey() {
        boolean isReadOnly = TransactionSynchronizationManager
            .isCurrentTransactionReadOnly();

        if (isReadOnly && slaveAvailable) {
            try {
                testSlaveConnection();
                return DataSourceType.SLAVE;
            } catch (Exception e) {
                log.error("Slave DB is unavailable. Falling back to Master", e);
                slaveAvailable = false;
                scheduleHealthCheck();
                return DataSourceType.MASTER;
            }
        }

        return DataSourceType.MASTER;
    }

    private void testSlaveConnection() throws SQLException {
        try (Connection conn = slaveDataSource.getConnection();
             Statement stmt = conn.createStatement()) {
            stmt.execute("SELECT 1");
        }
    }

    @Scheduled(fixedDelay = 10000)  // 10초마다 확인
    public void healthCheck() {
        if (!slaveAvailable) {
            try {
                testSlaveConnection();
                slaveAvailable = true;
                log.info("Slave DB is back online");
            } catch (Exception e) {
                log.debug("Slave DB still unavailable");
            }
        }
    }
}
```

---

**다중 Slave 지원 (Round-Robin)**:

```java
public class ReplicationRoutingDataSource extends AbstractRoutingDataSource {

    private final List<DataSource> slaveDataSources;
    private final AtomicInteger counter = new AtomicInteger(0);

    @Override
    protected Object determineCurrentLookupKey() {
        boolean isReadOnly = TransactionSynchronizationManager
            .isCurrentTransactionReadOnly();

        if (isReadOnly) {
            // Round-Robin으로 Slave 선택
            int index = counter.getAndIncrement() % slaveDataSources.size();
            return "SLAVE_" + index;
        }

        return DataSourceType.MASTER;
    }
}

@Configuration
public class DataSourceConfig {

    @Bean
    public DataSource routingDataSource() {
        ReplicationRoutingDataSource routingDataSource =
            new ReplicationRoutingDataSource();

        Map<Object, Object> dataSourceMap = new HashMap<>();
        dataSourceMap.put(DataSourceType.MASTER, masterDataSource());
        dataSourceMap.put("SLAVE_0", slave1DataSource());
        dataSourceMap.put("SLAVE_1", slave2DataSource());
        dataSourceMap.put("SLAVE_2", slave3DataSource());

        routingDataSource.setTargetDataSources(dataSourceMap);
        routingDataSource.setDefaultTargetDataSource(masterDataSource());

        return routingDataSource;
    }
}
```

---

**모니터링**:

```java
@Component
@Slf4j
public class DataSourceMonitor {

    @Autowired
    @Qualifier("masterDataSource")
    private HikariDataSource masterDataSource;

    @Autowired
    @Qualifier("slaveDataSource")
    private HikariDataSource slaveDataSource;

    @Scheduled(fixedDelay = 60000)  // 1분마다
    public void logConnectionPoolStats() {
        HikariPoolMXBean masterPool = masterDataSource.getHikariPoolMXBean();
        HikariPoolMXBean slavePool = slaveDataSource.getHikariPoolMXBean();

        log.info("Master - Active: {}, Idle: {}, Total: {}, Waiting: {}",
            masterPool.getActiveConnections(),
            masterPool.getIdleConnections(),
            masterPool.getTotalConnections(),
            masterPool.getThreadsAwaitingConnection());

        log.info("Slave - Active: {}, Idle: {}, Total: {}, Waiting: {}",
            slavePool.getActiveConnections(),
            slavePool.getIdleConnections(),
            slavePool.getTotalConnections(),
            slavePool.getThreadsAwaitingConnection());
    }
}
```

---

**주의사항**:

```java
// ❌ 잘못된 사용: readOnly 없이 읽기만
@Transactional  // readOnly = false (기본값)
public User getUser(Long id) {
    // Master DB 사용! (Slave 사용 안 됨)
    return userRepository.findById(id).orElseThrow();
}

// ✅ 올바른 사용: readOnly = true
@Transactional(readOnly = true)
public User getUser(Long id) {
    // Slave DB 사용 ✅
    return userRepository.findById(id).orElseThrow();
}
```

**Replication Lag 고려**:

```java
@Service
public class OrderService {

    // ❌ 문제: Replication Lag으로 인한 데이터 불일치
    @Transactional
    public void createOrder(OrderRequest request) {
        // Master에 저장
        Order order = orderRepository.save(new Order(request));
    }

    @Transactional(readOnly = true)
    public Order getRecentOrder(Long orderId) {
        // Slave에서 조회 → 아직 복제 안 됨! (Replication Lag)
        return orderRepository.findById(orderId).orElseThrow();
    }

    // ✅ 해결: 최신 데이터 필요 시 Master에서 조회
    @Transactional  // readOnly = false → Master 사용
    public Order getRecentOrderFromMaster(Long orderId) {
        return orderRepository.findById(orderId).orElseThrow();
    }
}
```

---

## 📝 핵심 정리

### 데이터 접근 기술 비교

| 기술 | 추상화 | SQL 제어 | 난이도 | 사용 사례 |
|------|--------|---------|--------|----------|
| JDBC | 낮음 | 완전 | 어려움 | 레거시, 성능 최적화 |
| Spring JDBC | 중간 | 직접 | 보통 | 간단한 쿼리 |
| JPA | 높음 | 자동 | 쉬움 | CRUD 중심 |
| MyBatis | 중간 | 직접 | 보통 | 복잡한 쿼리 |
| QueryDSL | 높음 | 타입 안전 | 보통 | 동적 쿼리 |

### 주요 개념

**DataSource**: 데이터베이스 연결 관리
**Transaction**: 데이터 무결성 보장
**Connection Pool**: 성능 최적화
**Repository**: 데이터 접근 계층 추상화

---

**다음 장으로**: [→ 다음: 20장 - Spring JDBC](SpringMVC-Part12-20-Spring-JDBC.md)

**목차로 돌아가기**: [📚 전체 목차](README.md)
