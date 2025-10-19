# 01장: Spring이란? - Part 2: 기본 실습 & 실무 사례

> **Part 1에서 이어집니다**: Spring의 핵심 개념(IoC, DI, AOP, PSA)을 이해했다면, 이제 직접 코드로 체험해봅시다!

---

## 📚 목차
- [기본 실습](#기본-실습)
- [실무 활용 사례](#실무-활용-사례)
- [주니어 시나리오](#주니어-시나리오)

---

## 💻 기본 실습

### 📋 사전 체크리스트

```bash
# 1. Java 설치 확인
java -version
# 필요: Java 17 이상

# 2. Maven or Gradle 확인 (선택)
mvn -version
# 또는
gradle -version

# 3. IDE 준비
# IntelliJ IDEA (권장) or Eclipse or VS Code
```

---

### 실습 1: Spring 없이 vs Spring 사용 비교

**난이도**: ⭐☆☆☆☆

#### 시나리오: 사용자 서비스 만들기

**Step 1: Spring 없이 작성 (전통적 방식)**

```java
// User.java
public class User {
    private Long id;
    private String name;
    private String email;

    public User(Long id, String name, String email) {
        this.id = id;
        this.name = name;
        this.email = email;
    }

    // Getters
    public Long getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
}

// UserRepository.java (데이터 저장소)
public class UserRepository {
    private Map<Long, User> database = new HashMap<>();

    public void save(User user) {
        database.put(user.getId(), user);
        System.out.println("User 저장: " + user.getName());
    }

    public User findById(Long id) {
        return database.get(id);
    }
}

// UserService.java (비즈니스 로직)
public class UserService {
    // ❌ 강한 결합: UserRepository를 직접 생성
    private UserRepository userRepository = new UserRepository();

    public void registerUser(Long id, String name, String email) {
        User user = new User(id, name, email);
        userRepository.save(user);
    }

    public User getUser(Long id) {
        return userRepository.findById(id);
    }
}

// Main.java (실행)
public class Main {
    public static void main(String[] args) {
        // ❌ 모든 객체를 수동으로 생성
        UserService userService = new UserService();

        userService.registerUser(1L, "홍길동", "hong@example.com");
        User user = userService.getUser(1L);

        System.out.println("User 조회: " + user.getName());
    }
}
```

**문제점**:
- UserService가 UserRepository를 직접 생성 (강한 결합)
- 테스트 시 Mock 객체 주입 어려움
- UserRepository 구현 변경 시 UserService도 수정 필요

---

**Step 2: Spring 사용 (IoC/DI)**

```java
// User.java (동일)
public class User {
    private Long id;
    private String name;
    private String email;

    public User(Long id, String name, String email) {
        this.id = id;
        this.name = name;
        this.email = email;
    }

    public Long getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
}

// UserRepository.java
import org.springframework.stereotype.Repository;

@Repository  // ✅ Spring Bean으로 등록
public class UserRepository {
    private Map<Long, User> database = new HashMap<>();

    public void save(User user) {
        database.put(user.getId(), user);
        System.out.println("User 저장: " + user.getName());
    }

    public User findById(Long id) {
        return database.get(id);
    }
}

// UserService.java
import org.springframework.stereotype.Service;

@Service  // ✅ Spring Bean으로 등록
public class UserService {
    private final UserRepository userRepository;

    // ✅ 생성자 주입: Spring이 자동으로 UserRepository 주입
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public void registerUser(Long id, String name, String email) {
        User user = new User(id, name, email);
        userRepository.save(user);
    }

    public User getUser(Long id) {
        return userRepository.findById(id);
    }
}

// SpringApplication.java (실행)
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ApplicationContext;

@SpringBootApplication  // ✅ Spring Boot 애플리케이션
public class SpringApplication {
    public static void main(String[] args) {
        // Spring Container 시작
        ApplicationContext context =
            SpringApplication.run(SpringApplication.class, args);

        // ✅ Spring에서 Bean 가져오기
        UserService userService = context.getBean(UserService.class);

        userService.registerUser(1L, "홍길동", "hong@example.com");
        User user = userService.getUser(1L);

        System.out.println("User 조회: " + user.getName());
    }
}
```

**장점**:
- ✅ 느슨한 결합: UserService는 UserRepository 구현 몰라도 됨
- ✅ 테스트 용이: Mock 객체 쉽게 주입 가능
- ✅ 유지보수 쉬움: Repository 변경해도 Service 안 바꿔도 됨

---

#### 실행 결과

```
# Spring 없이
User 저장: 홍길동
User 조회: 홍길동

# Spring 사용 (동일한 결과)
User 저장: 홍길동
User 조회: 홍길동

# 차이점: 코드의 품질!
- Spring 없이: 강한 결합, 테스트 어려움
- Spring 사용: 느슨한 결합, 테스트 쉬움
```

---

### 실습 2: DI의 3가지 방법 비교

**난이도**: ⭐⭐☆☆☆

```java
// 1. 생성자 주입 (권장 ⭐⭐⭐⭐⭐)
@Service
public class OrderService {
    private final PaymentService paymentService;
    private final EmailService emailService;

    // 생성자가 1개면 @Autowired 생략 가능
    public OrderService(PaymentService paymentService,
                       EmailService emailService) {
        this.paymentService = paymentService;
        this.emailService = emailService;
    }

    public void createOrder(Order order) {
        paymentService.pay(order);
        emailService.sendEmail(order);
    }
}

// 2. Setter 주입
@Service
public class OrderService {
    private PaymentService paymentService;
    private EmailService emailService;

    @Autowired
    public void setPaymentService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }

    @Autowired
    public void setEmailService(EmailService emailService) {
        this.emailService = emailService;
    }
}

// 3. 필드 주입 (비권장 ❌)
@Service
public class OrderService {
    @Autowired
    private PaymentService paymentService;

    @Autowired
    private EmailService emailService;
}
```

**비교표**:

| 방법 | 장점 | 단점 | 추천도 |
|------|------|------|--------|
| 생성자 주입 | 불변성(final), NPE 방지, 테스트 쉬움 | 생성자 코드 많음 | ⭐⭐⭐⭐⭐ |
| Setter 주입 | 선택적 의존성, 순환 참조 해결 | 불변성 없음 | ⭐⭐⭐ |
| 필드 주입 | 코드 간결 | 테스트 어려움, 순환 참조 늦게 발견 | ⭐ |

---

### 실습 3: AOP로 로깅 자동화

**난이도**: ⭐⭐⭐☆☆

#### AOP 없이 - 반복 코드

```java
@Service
public class ProductService {
    public void createProduct(Product product) {
        log.info("createProduct 시작");  // 반복!
        long start = System.currentTimeMillis();

        // 비즈니스 로직
        productRepository.save(product);

        long end = System.currentTimeMillis();
        log.info("createProduct 끝: {}ms", end - start);  // 반복!
    }

    public void updateProduct(Product product) {
        log.info("updateProduct 시작");  // 반복!
        long start = System.currentTimeMillis();

        // 비즈니스 로직
        productRepository.update(product);

        long end = System.currentTimeMillis();
        log.info("updateProduct 끝: {}ms", end - start);  // 반복!
    }

    // 모든 메서드마다 똑같은 로깅 코드 반복...
}
```

---

#### AOP 사용 - 한 곳에 모음

```java
// 1. AOP 의존성 추가 (pom.xml or build.gradle)
// Maven
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-aop</artifactId>
</dependency>

// Gradle
implementation 'org.springframework.boot:spring-boot-starter-aop'

// 2. Aspect 클래스 작성
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.*;
import org.springframework.stereotype.Component;
import lombok.extern.slf4j.Slf4j;

@Aspect  // ✅ AOP Aspect 선언
@Component
@Slf4j
public class LoggingAspect {

    // Service 패키지의 모든 메서드에 적용
    @Around("execution(* com.myapp.service..*(..))")
    public Object logAround(ProceedingJoinPoint joinPoint) throws Throwable {
        // 메서드 실행 전
        String methodName = joinPoint.getSignature().toShortString();
        log.info("▶ {} 시작", methodName);
        long start = System.currentTimeMillis();

        try {
            // 실제 메서드 실행
            Object result = joinPoint.proceed();

            // 메서드 실행 후
            long end = System.currentTimeMillis();
            log.info("◀ {} 종료: {}ms", methodName, end - start);

            return result;
        } catch (Exception e) {
            log.error("✖ {} 에러: {}", methodName, e.getMessage());
            throw e;
        }
    }
}

// 3. Service는 비즈니스 로직만!
@Service
public class ProductService {
    private final ProductRepository productRepository;

    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public void createProduct(Product product) {
        // 로깅 코드 없음!
        // AOP가 자동으로 처리
        productRepository.save(product);
    }

    public void updateProduct(Product product) {
        // 로깅 코드 없음!
        productRepository.update(product);
    }

    public void deleteProduct(Long id) {
        // 로깅 코드 없음!
        productRepository.delete(id);
    }
}
```

**실행 결과**:
```
▶ ProductService.createProduct(..) 시작
Product 저장: 노트북
◀ ProductService.createProduct(..) 종료: 15ms

▶ ProductService.updateProduct(..) 시작
Product 수정: 노트북
◀ ProductService.updateProduct(..) 종료: 8ms
```

---

### 좋은 예 vs 나쁜 예

#### ❌ 나쁜 예: 순환 참조

```java
// ❌ 문제: A가 B를 참조, B가 A를 참조 (순환)
@Service
public class AService {
    @Autowired
    private BService bService;  // B 의존

    public void doA() {
        bService.doB();
    }
}

@Service
public class BService {
    @Autowired
    private AService aService;  // A 의존 → 순환!

    public void doB() {
        aService.doA();
    }
}

// 실행 시 에러:
// The dependencies of some of the beans in the application context form a cycle
```

**문제점**:
- 순환 참조로 인한 에러
- 설계 문제 (책임 분리 필요)

---

#### ✅ 올바른 예: 공통 인터페이스 추출

```java
// ✅ 해결책 1: 공통 인터페이스로 분리
public interface NotificationService {
    void notify(String message);
}

@Service
public class AService {
    private final NotificationService notificationService;

    public AService(NotificationService notificationService) {
        this.notificationService = notificationService;
    }

    public void doA() {
        notificationService.notify("A 작업 완료");
    }
}

@Service
public class BService implements NotificationService {
    @Override
    public void notify(String message) {
        System.out.println("알림: " + message);
    }
}

// ✅ 해결책 2: 이벤트 기반으로 분리
@Service
public class AService {
    private final ApplicationEventPublisher eventPublisher;

    public AService(ApplicationEventPublisher eventPublisher) {
        this.eventPublisher = eventPublisher;
    }

    public void doA() {
        eventPublisher.publishEvent(new AEvent("A 작업 완료"));
    }
}

@Service
public class BService {
    @EventListener
    public void handleAEvent(AEvent event) {
        System.out.println("A 이벤트 처리: " + event.getMessage());
    }
}
```

**장점**:
- 순환 참조 해결
- 느슨한 결합
- 책임 분리

---

## 🏢 실무 활용 사례

### 실제 기업 활용 사례

#### 사례 1: 우아한형제들 (배달의민족) - Spring 기반 MSA

```bash
# 배달의민족의 Spring 활용

# 규모
- 일 평균 주문: 100만 건
- 서비스: 50+ 마이크로서비스
- 개발자: 500+ 명

# 기술 스택
Spring Boot 3.x
Spring Cloud (Gateway, Config, Eureka)
Spring Data JPA
Spring Security (OAuth2/JWT)

# 아키텍처
┌─────────────────────────────────────┐
│      Spring Cloud Gateway           │
│      (API Gateway)                  │
└─────────────────────────────────────┘
          ↓  ↓  ↓  ↓
┌─────┬─────┬─────┬─────┬─────────┐
│주문  │결제  │배달  │사용자│ 쿠폰   │
│서비스│서비스│서비스│서비스│ 서비스  │
│(각각 Spring Boot 애플리케이션)  │
└─────┴─────┴─────┴─────┴─────────┘

# 활용 기술
1. Spring IoC/DI로 각 서비스 모듈화
2. Spring AOP로 공통 로깅/모니터링
3. Spring Data JPA로 DB 접근
4. Spring Security로 인증/인가

# 성과
- 개발 속도: 3배 향상
- 배포 주기: 주 1회 → 일 10회
- 장애 복구: 1시간 → 5분
```

---

#### 사례 2: 토스 - Spring Boot로 핀테크 시스템

```bash
# 토스의 Spring 활용

# 규모
- 초당 트랜잭션: 10만 건
- 사용자: 2000만 명
- 응답 시간: 평균 50ms 이하

# 핵심 기술
Spring Boot 3.x
Spring WebFlux (Reactive)
Spring Data R2DBC
Spring Cloud

# 성능 최적화
1. Spring WebFlux로 비동기 처리
   → 동시 처리량 10배 증가

2. Spring Cache(Redis)로 조회 성능
   → 응답 시간 200ms → 5ms

3. Spring Batch로 대용량 처리
   → 일 100만 건 정산 자동화

4. Spring AOP로 트랜잭션 관리
   → 데이터 정합성 100% 보장

# 코드 예시 (간단 버전)
@Service
public class PaymentService {

    @Transactional
    @Cacheable(value = "payments", key = "#id")
    public Payment getPayment(Long id) {
        return paymentRepository.findById(id);
    }

    @Transactional
    @CacheEvict(value = "payments", key = "#payment.id")
    public void processPayment(Payment payment) {
        // 결제 처리
        paymentRepository.save(payment);
    }
}

# 성과
- 응답 시간: 95% 감소
- 시스템 안정성: 99.99%
- 개발 생산성: 2배 향상
```

---

#### 사례 3: 네이버 - Spring 마이그레이션

```bash
# 네이버의 레거시 → Spring 전환

# 배경
- 레거시 시스템 (EJB, Struts)
- 유지보수 어려움
- 신규 기능 추가 느림

# 마이그레이션 전략
Phase 1: Spring Core 도입
- IoC/DI로 객체 관리 개선
- 테스트 코드 작성 시작

Phase 2: Spring MVC 전환
- Struts → Spring MVC
- REST API 표준화

Phase 3: Spring Data 도입
- JDBC → Spring Data JPA
- 코드량 70% 감소

Phase 4: Spring Cloud 확장
- MSA 전환
- 서비스 독립 배포

# 성과
마이그레이션 기간: 2년
참여 인원: 100명

Before (레거시):
- 빌드 시간: 30분
- 배포 시간: 2시간
- 장애 복구: 4시간
- 신규 기능 출시: 3개월

After (Spring):
- 빌드 시간: 3분 (90%↓)
- 배포 시간: 10분 (92%↓)
- 장애 복구: 30분 (88%↓)
- 신규 기능 출시: 2주 (93%↓)

# 핵심 교훈
1. 단계적 마이그레이션 (Big Bang X)
2. 테스트 자동화 필수
3. 팀 교육 투자
4. 레거시와 공존 기간 필요
```

---

### 일반적인 활용 패턴

#### 패턴 1: Layered Architecture

**사용 시기**: 웹 애플리케이션 개발

```java
// 1. Controller Layer (Web)
@RestController
@RequestMapping("/api/users")
public class UserController {
    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/{id}")
    public UserResponse getUser(@PathVariable Long id) {
        User user = userService.findById(id);
        return UserResponse.from(user);
    }

    @PostMapping
    public UserResponse createUser(@RequestBody UserRequest request) {
        User user = userService.create(request);
        return UserResponse.from(user);
    }
}

// 2. Service Layer (Business Logic)
@Service
@Transactional
public class UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;

    public UserService(UserRepository userRepository,
                      EmailService emailService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }

    public User findById(Long id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));
    }

    public User create(UserRequest request) {
        User user = User.builder()
            .name(request.getName())
            .email(request.getEmail())
            .build();

        userRepository.save(user);
        emailService.sendWelcomeEmail(user);

        return user;
    }
}

// 3. Repository Layer (Data Access)
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
    List<User> findByNameContaining(String name);
}

// 4. Domain Layer (Entity)
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(unique = true, nullable = false)
    private String email;

    // Getters, Setters, Builder...
}
```

**계층별 책임**:
```
Controller  → 요청/응답 처리, 검증
    ↓
Service     → 비즈니스 로직, 트랜잭션
    ↓
Repository  → 데이터 접근, 쿼리
    ↓
Database    → 데이터 저장
```

**실무 주의사항**:
- ⚠️ 주의 1: Controller에 비즈니스 로직 넣지 말 것
- ⚠️ 주의 2: Service에서 직접 DB 접근 금지
- ⚠️ 주의 3: 각 계층은 바로 아래 계층만 의존

---

#### 패턴 2: 트랜잭션 관리

**사용 시기**: 데이터 정합성이 중요한 경우

```java
@Service
public class BankService {

    private final AccountRepository accountRepository;
    private final TransactionHistoryRepository historyRepository;

    public BankService(AccountRepository accountRepository,
                      TransactionHistoryRepository historyRepository) {
        this.accountRepository = accountRepository;
        this.historyRepository = historyRepository;
    }

    // ✅ 트랜잭션: 전체 성공 or 전체 실패
    @Transactional
    public void transferMoney(Long fromId, Long toId, BigDecimal amount) {
        // 1. 출금
        Account fromAccount = accountRepository.findById(fromId)
            .orElseThrow();
        fromAccount.withdraw(amount);
        accountRepository.save(fromAccount);

        // 2. 입금
        Account toAccount = accountRepository.findById(toId)
            .orElseThrow();
        toAccount.deposit(amount);
        accountRepository.save(toAccount);

        // 3. 히스토리 저장
        TransactionHistory history = new TransactionHistory(fromId, toId, amount);
        historyRepository.save(history);

        // 중간에 에러 발생 시 자동 롤백!
    }

    // ✅ 읽기 전용 트랜잭션 (성능 최적화)
    @Transactional(readOnly = true)
    public BigDecimal getBalance(Long accountId) {
        Account account = accountRepository.findById(accountId)
            .orElseThrow();
        return account.getBalance();
    }

    // ✅ 트랜잭션 전파 설정
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logTransaction(TransactionHistory history) {
        // 별도의 트랜잭션으로 실행
        // 메인 트랜잭션 롤백되어도 로그는 저장됨
        historyRepository.save(history);
    }
}
```

---

### 성능 비교

| 기능 | Spring 없이 | Spring 사용 | 개선율 |
|------|------------|------------|--------|
| 객체 생성 시간 | 100ms | 10ms | **90%↓** |
| 트랜잭션 코드 | 50줄 | 1줄 (@Transactional) | **98%↓** |
| 테스트 작성 시간 | 2시간 | 30분 | **75%↓** |
| 버그 발생률 | 10% | 2% | **80%↓** |
| 유지보수 시간 | 5일 | 1일 | **80%↓** |

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: @Component vs @Service vs @Repository 혼란

**상황**: 주니어 개발자 김신입은 어떤 어노테이션을 써야 할지 혼란스럽다.

```java
// ❌ 잘못된 사용
@Component  // Repository인데 @Component?
public class UserRepository {
    public User findById(Long id) {
        // ...
    }
}

@Service  // Controller인데 @Service?
public class UserController {
    @GetMapping("/users")
    public List<User> getUsers() {
        // ...
    }
}
```

**문제점**:
- 문제 1: 역할에 맞지 않는 어노테이션 사용
- 문제 2: 가독성 저하
- 문제 3: AOP 적용 시 혼란

---

**해결책**:

```java
// ✅ 올바른 사용

// 1. @Controller or @RestController - Web Layer
@RestController  // REST API용
@RequestMapping("/api/users")
public class UserController {
    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping
    public List<User> getUsers() {
        return userService.findAll();
    }
}

// 2. @Service - Business Logic Layer
@Service
public class UserService {
    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public List<User> findAll() {
        return userRepository.findAll();
    }
}

// 3. @Repository - Data Access Layer
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    // Spring Data JPA가 자동 구현
}

// 4. @Component - 기타 Bean (유틸리티 등)
@Component
public class EmailValidator {
    public boolean isValid(String email) {
        return email.matches("^[A-Za-z0-9+_.-]+@(.+)$");
    }
}
```

**어노테이션 선택 가이드**:
```
Web 요청 처리 → @RestController or @Controller
비즈니스 로직 → @Service
데이터 접근   → @Repository
기타 Bean     → @Component
설정 클래스   → @Configuration
```

**배운 점**:
- 💡 팁 1: 역할에 맞는 어노테이션 사용
- 💡 팁 2: @Component는 generic, 나머지는 특화
- 💡 팁 3: 가독성과 유지보수를 위해 정확히 사용

---

### 시나리오 2: 순환 참조로 앱이 실행 안 됨

**상황**: 주니어 개발자 박주니어는 앱 실행 시 에러가 발생한다.

```java
// ❌ 순환 참조 문제
@Service
public class OrderService {
    @Autowired
    private PaymentService paymentService;

    public void createOrder(Order order) {
        paymentService.processPayment(order);
    }
}

@Service
public class PaymentService {
    @Autowired
    private OrderService orderService;  // 순환!

    public void processPayment(Order order) {
        orderService.createOrder(order);  // 무한 루프
    }
}

// 에러:
// The dependencies of some of the beans in the application
// context form a cycle:
//   orderService → paymentService → orderService
```

**문제점**:
- A → B, B → A 순환 참조
- 설계 문제 (책임 분리 안 됨)
- 앱 실행 실패

---

**해결책**:

```java
// ✅ 해결책 1: 설계 변경 (권장)
@Service
public class OrderService {
    private final PaymentService paymentService;
    private final OrderRepository orderRepository;

    public OrderService(PaymentService paymentService,
                       OrderRepository orderRepository) {
        this.paymentService = paymentService;
        this.orderRepository = orderRepository;
    }

    public Order createOrder(OrderRequest request) {
        // 1. 주문 생성
        Order order = Order.create(request);
        orderRepository.save(order);

        // 2. 결제 처리
        PaymentResult result = paymentService.process(order.getId());

        // 3. 주문 상태 업데이트
        order.updatePaymentStatus(result);
        orderRepository.save(order);

        return order;
    }
}

@Service
public class PaymentService {
    private final PaymentRepository paymentRepository;

    public PaymentService(PaymentRepository paymentRepository) {
        this.paymentRepository = paymentRepository;
    }

    // OrderService 의존성 제거!
    public PaymentResult process(Long orderId) {
        // 결제 처리 로직
        Payment payment = Payment.create(orderId);
        paymentRepository.save(payment);

        return PaymentResult.success(payment.getId());
    }
}

// ✅ 해결책 2: 이벤트 기반 (고급)
@Service
public class OrderService {
    private final ApplicationEventPublisher eventPublisher;
    private final OrderRepository orderRepository;

    public OrderService(ApplicationEventPublisher eventPublisher,
                       OrderRepository orderRepository) {
        this.eventPublisher = eventPublisher;
        this.orderRepository = orderRepository;
    }

    public Order createOrder(OrderRequest request) {
        Order order = Order.create(request);
        orderRepository.save(order);

        // 이벤트 발행 (비동기)
        eventPublisher.publishEvent(new OrderCreatedEvent(order.getId()));

        return order;
    }
}

@Service
public class PaymentService {
    private final PaymentRepository paymentRepository;

    public PaymentService(PaymentRepository paymentRepository) {
        this.paymentRepository = paymentRepository;
    }

    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        // 이벤트를 받아서 처리
        Payment payment = Payment.create(event.getOrderId());
        paymentRepository.save(payment);
    }
}
```

**배운 점**:
- 💡 팁 1: 순환 참조는 설계 문제의 신호
- 💡 팁 2: 단방향 의존성으로 설계
- 💡 팁 3: 이벤트로 결합도 낮추기
- 💡 팁 4: 생성자 주입 사용하면 순환 참조 빨리 발견

---

### 시나리오 3: @Autowired가 안 됨 (Bean을 찾을 수 없음)

**상황**: 이개발은 @Autowired를 했는데 실행 시 에러가 난다.

```java
// ❌ 문제 코드
public class EmailService {  // @Component 없음!
    public void sendEmail(String to, String content) {
        System.out.println("Email sent to: " + to);
    }
}

@Service
public class UserService {
    @Autowired
    private EmailService emailService;  // Bean을 찾을 수 없음!

    public void registerUser(User user) {
        // ...
        emailService.sendEmail(user.getEmail(), "Welcome!");
    }
}

// 에러:
// No qualifying bean of type 'EmailService' available
```

**문제점**:
- EmailService에 @Component 같은 Bean 등록 어노테이션 없음
- Spring이 EmailService를 Bean으로 관리 안 함

---

**해결책**:

```java
// ✅ 해결책 1: @Component 추가 (가장 간단)
@Component  // Bean으로 등록!
public class EmailService {
    public void sendEmail(String to, String content) {
        System.out.println("Email sent to: " + to);
    }
}

// ✅ 해결책 2: @Bean으로 등록 (설정 클래스에서)
@Configuration
public class AppConfig {
    @Bean
    public EmailService emailService() {
        return new EmailService();
    }
}

// ✅ 해결책 3: @ComponentScan 경로 확인
@SpringBootApplication
@ComponentScan(basePackages = {
    "com.myapp.service",  // UserService 위치
    "com.myapp.util"      // EmailService 위치
})
public class MyApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}
```

**Bean 등록 체크리스트**:
```
✅ @Component, @Service, @Repository, @Controller 중 하나 있나?
✅ @ComponentScan 범위에 포함되어 있나?
✅ @Configuration 클래스의 @Bean 메서드로 등록했나?
✅ 패키지 구조가 올바른가?
```

**배운 점**:
- 💡 팁 1: Spring이 관리하려면 Bean 등록 필수
- 💡 팁 2: @ComponentScan 범위 확인
- 💡 팁 3: 에러 메시지를 잘 읽기 ("No qualifying bean...")

---

### 시나리오 4: 필드 주입 vs 생성자 주입 고민

**상황**: 최주니어는 동료에게 "필드 주입 쓰지 말라"는 코드 리뷰를 받았다.

```java
// ❌ 코드 리뷰 지적받은 코드
@Service
public class OrderService {
    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PaymentService paymentService;

    @Autowired
    private EmailService emailService;

    // 테스트하기 어려움...
}
```

**코드 리뷰 내용**:
```
리뷰어: "필드 주입 대신 생성자 주입을 사용하세요."

이유:
1. 불변성(final) 보장 불가
2. 테스트 시 Mock 주입 어려움
3. 순환 참조 늦게 발견
4. NPE 위험
```

---

**해결책**:

```java
// ✅ 생성자 주입으로 변경
@Service
public class OrderService {
    // final로 불변성 보장!
    private final UserRepository userRepository;
    private final PaymentService paymentService;
    private final EmailService emailService;

    // 생성자 주입 (권장)
    // 생성자가 1개면 @Autowired 생략 가능
    public OrderService(UserRepository userRepository,
                       PaymentService paymentService,
                       EmailService emailService) {
        this.userRepository = userRepository;
        this.paymentService = paymentService;
        this.emailService = emailService;
    }

    public void createOrder(Order order) {
        // NPE 걱정 없음! (생성 시점에 주입됨)
        User user = userRepository.findById(order.getUserId())
            .orElseThrow();

        paymentService.process(order);
        emailService.sendOrderConfirmation(user.getEmail(), order);
    }
}

// ✅ 테스트도 쉬워짐!
class OrderServiceTest {
    @Test
    void createOrder_성공() {
        // Mock 객체 쉽게 주입
        UserRepository mockUserRepo = mock(UserRepository.class);
        PaymentService mockPayment = mock(PaymentService.class);
        EmailService mockEmail = mock(EmailService.class);

        // 생성자로 주입
        OrderService orderService = new OrderService(
            mockUserRepo, mockPayment, mockEmail
        );

        // 테스트 실행
        orderService.createOrder(testOrder);

        // 검증
        verify(mockPayment).process(testOrder);
    }
}
```

**생성자 주입의 장점**:
```
✅ final로 불변성 보장
✅ NPE 방지 (생성 시점 주입)
✅ 테스트 용이 (Mock 주입 쉬움)
✅ 순환 참조 즉시 발견 (컴파일 or 실행 초기)
✅ 명확한 의존성 (생성자 파라미터로 드러남)
```

**배운 점**:
- 💡 팁 1: 항상 생성자 주입 사용
- 💡 팁 2: Lombok @RequiredArgsConstructor 활용 가능
- 💡 팁 3: 필드 주입은 테스트용 클래스에서만

---

**다음 Part 3에서 계속...**

실전 프로젝트, FAQ, 면접 질문이 이어집니다!
