# 01장: Spring이란? - Part 1: 핵심 개념 이해하기

> **학습 목표**: Spring Framework가 무엇이며 왜 필요한지 이해하고, IoC, DI, AOP, PSA 같은 핵심 개념을 실생활 비유로 쉽게 설명할 수 있다.

**⏱️ 예상 학습 시간**: 2-3시간
**난이도**: ⭐⭐☆☆☆ (2개/5개)

---

## 📚 목차
- [왜 Spring이 필요한가](#왜-spring이-필요한가)
- [실생활 비유로 이해하기](#실생활-비유로-이해하기)
- [핵심 개념](#핵심-개념)

---

## 🤔 왜 Spring이 필요한가?

### 실무 배경

**Java만으로 웹 애플리케이션을 만들면 너무 복잡하고 반복적인 코드가 많습니다.**

#### ❌ Spring 없이 개발하면 발생하는 문제

```java
// 문제 1: 객체 생성과 의존성 관리가 복잡
public class OrderService {
    // 수동으로 모든 의존 객체 생성
    private UserRepository userRepository = new UserRepository();
    private PaymentService paymentService = new PaymentService();
    private EmailService emailService = new EmailService();

    public void createOrder(Order order) {
        // 의존 객체들이 강하게 결합됨
        // 테스트하기 어렵고, 변경에 취약
    }
}

// 문제 2: 반복적인 코드 (JDBC)
public User findById(Long id) {
    Connection conn = null;
    PreparedStatement pstmt = null;
    ResultSet rs = null;

    try {
        conn = DriverManager.getConnection(url, user, password);
        pstmt = conn.prepareStatement("SELECT * FROM users WHERE id = ?");
        pstmt.setLong(1, id);
        rs = pstmt.executeQuery();

        if (rs.next()) {
            return new User(
                rs.getLong("id"),
                rs.getString("name"),
                rs.getString("email")
            );
        }
    } catch (SQLException e) {
        // 에러 처리
    } finally {
        // 자원 해제 (10줄 이상의 코드)
        try { if (rs != null) rs.close(); } catch (SQLException e) {}
        try { if (pstmt != null) pstmt.close(); } catch (SQLException e) {}
        try { if (conn != null) conn.close(); } catch (SQLException e) {}
    }
    return null;
}

// 문제 3: 트랜잭션 관리가 어렵고 실수하기 쉬움
public void transferMoney(Account from, Account to, int amount) {
    Connection conn = null;
    try {
        conn = getConnection();
        conn.setAutoCommit(false);  // 수동 트랜잭션 시작

        // 출금
        withdraw(conn, from, amount);
        // 입금
        deposit(conn, to, amount);

        conn.commit();  // 커밋
    } catch (Exception e) {
        if (conn != null) {
            try {
                conn.rollback();  // 롤백
            } catch (SQLException ex) {}
        }
    } finally {
        if (conn != null) {
            try {
                conn.close();
            } catch (SQLException e) {}
        }
    }
}
```

**문제점**:
- 증상: 객체 생성/관리 코드가 비즈니스 로직보다 많음
- 영향: 개발 속도 느림, 유지보수 어려움
- 비용: 개발 시간 3배 증가, 버그 발생률 높음

---

#### ✅ Spring을 사용하면

```java
// 해결책 1: Spring이 객체 생성과 의존성 주입을 자동으로!
@Service
public class OrderService {
    // Spring이 자동으로 주입
    private final UserRepository userRepository;
    private final PaymentService paymentService;
    private final EmailService emailService;

    // 생성자 주입 (권장)
    public OrderService(UserRepository userRepository,
                       PaymentService paymentService,
                       EmailService emailService) {
        this.userRepository = userRepository;
        this.paymentService = paymentService;
        this.emailService = emailService;
    }

    public void createOrder(Order order) {
        // 비즈니스 로직에만 집중!
    }
}

// 해결책 2: Spring Data JPA로 간단하게!
public interface UserRepository extends JpaRepository<User, Long> {
    // 메서드 선언만 하면 Spring이 자동 구현!
    Optional<User> findById(Long id);
    List<User> findByName(String name);
    // 10줄짜리 JDBC 코드 → 1줄!
}

// 해결책 3: @Transactional로 간단한 트랜잭션!
@Service
public class BankService {

    @Transactional  // 이것만 붙이면 자동 트랜잭션 관리!
    public void transferMoney(Account from, Account to, int amount) {
        // 비즈니스 로직만 작성
        withdraw(from, amount);
        deposit(to, amount);
        // 에러 발생 시 자동 롤백!
    }
}
```

**해결 효과**:
- 방법: Spring Framework 사용
- 효과: 코드량 70% 감소, 개발 속도 3배 향상
- 절감: 개발 시간 단축, 버그 80% 감소

---

### 📊 수치로 보는 효과

| 지표 | Spring 없이 | Spring 사용 | 개선율 |
|------|------------|------------|--------|
| 코드 라인 수 | 1000줄 | 300줄 | **70%↓** |
| 개발 시간 | 3개월 | 1개월 | **67%↓** |
| 버그 발생률 | 100건 | 20건 | **80%↓** |
| 테스트 작성 시간 | 5일 | 1일 | **80%↓** |
| 유지보수 비용 | $10,000 | $3,000 | **70%↓** |

---

## 🌟 실생활 비유로 이해하기

### 비유 1: Spring = 자동차 공장

```
Java만 사용 = 수제 자동차 제작
- 모든 부품을 직접 만듦
- 조립도 직접
- 시간 오래 걸림
- 에러 많음

Spring 사용 = 현대 자동차 공장
- 부품은 자동으로 공급 (IoC Container)
- 조립은 로봇이 자동 (DI)
- 품질 검사 자동 (AOP)
- 빠르고 정확함

┌────────────────────────────────────┐
│     🏭 Spring Container            │
│     (자동차 공장)                   │
│                                    │
│  📦 부품 창고 (Bean들)              │
│  ├─ 🔧 UserService                │
│  ├─ 🔩 OrderService               │
│  └─ ⚙️ PaymentService             │
│                                    │
│  🤖 조립 로봇 (DI)                 │
│  "자동으로 부품 조립"                │
│                                    │
│  ✅ 품질 검사 (AOP)                │
│  "로깅, 트랜잭션 자동 처리"          │
│                                    │
│  → 🚗 완성된 자동차 (Application)  │
└────────────────────────────────────┘
```

**핵심**: Spring은 자동차 공장처럼 모든 것을 자동화해줍니다!

---

### 비유 2: IoC = 배달 앱

```
전통적 방식 (내가 제어) = 직접 요리
- 장보러 가기
- 재료 준비
- 요리하기
- 설거지까지

IoC (제어의 역전) = 배달 앱
- 앱에서 주문만 하면
- 배달 앱이 알아서 음식 준비
- 배달까지 해줌
- 내가 제어하지 않음!

┌──────────────────────────────┐
│  전통적 방식 (내가 제어)       │
│                              │
│  나 → 장보기                  │
│    → 요리                     │
│    → 설거지                   │
│                              │
│  모든 것을 직접 제어!          │
└──────────────────────────────┘
         vs
┌──────────────────────────────┐
│  IoC (배달 앱이 제어)         │
│                              │
│  나 → "치킨 주문"             │
│                              │
│  배달앱 → 음식점 선택          │
│        → 요리 지시            │
│        → 배달 기사 배정        │
│        → 배달 완료            │
│                              │
│  제어권이 역전됨!              │
└──────────────────────────────┘
```

**Spring IoC**:
```java
// 전통적 방식 - 내가 객체 생성 제어
public class OrderService {
    private PaymentService paymentService = new PaymentService(); // 내가 생성
}

// IoC - Spring이 객체 생성 제어
@Service
public class OrderService {
    private final PaymentService paymentService;

    // Spring이 자동으로 주입해줌 (나는 선언만)
    public OrderService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }
}
```

---

### 비유 3: DI = 레고 블록

```
DI (Dependency Injection) = 레고 조립

각 블록(객체)은 독립적
블록들을 조합해서 큰 작품 완성
블록 교체도 쉬움

┌─────────────────────────────┐
│   🧱 레고 블록 (Bean)        │
│                             │
│   블록A (UserService)       │
│   블록B (OrderService)      │
│   블록C (PaymentService)    │
│                             │
│   각 블록은 독립적!          │
└─────────────────────────────┘
          ↓
   Spring이 자동 조립
          ↓
┌─────────────────────────────┐
│   🏰 완성된 성 (Application)│
│                             │
│   블록A                     │
│    ├─ 블록B                 │
│    └─ 블록C                 │
│                             │
│   의존성이 주입됨!           │
└─────────────────────────────┘
```

**DI의 장점**:
```java
// 강하게 결합 (Bad) - 블록이 접착제로 붙음
public class OrderService {
    private PaymentService paymentService = new PaymentService(); // 교체 불가
}

// 느슨하게 결합 (Good) - 레고처럼 끼웠다 뺐다
public class OrderService {
    private final PaymentService paymentService;

    // 어떤 PaymentService든 주입 가능 (카드, 현금, 페이팔...)
    public OrderService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }
}
```

---

### 비유 4: AOP = CCTV & 보안 시스템

```
AOP (Aspect-Oriented Programming) = 건물의 보안 시스템

각 방(메서드)에 들어갈 때마다:
- CCTV 자동 녹화 (로깅)
- 출입 기록 (모니터링)
- 도어락 체크 (보안)

각 방마다 일일이 설치할 필요 없음!

┌───────────────────────────────┐
│   🏢 건물 (Application)        │
│                               │
│   📹 CCTV (AOP)               │
│   "모든 입구를 자동 감시"       │
│                               │
│   방1: createOrder() ──┐      │
│   방2: payment()     ──┼─→ 📹 │
│   방3: sendEmail()   ──┘      │
│                               │
│   각 방마다 CCTV 코드 불필요!  │
└───────────────────────────────┘
```

**AOP의 위력**:
```java
// AOP 없이 - 모든 메서드에 로깅 코드 반복
public class OrderService {
    public void createOrder() {
        log.info("createOrder 시작");  // 반복!
        // 비즈니스 로직
        log.info("createOrder 끝");    // 반복!
    }

    public void payment() {
        log.info("payment 시작");      // 반복!
        // 비즈니스 로직
        log.info("payment 끝");        // 반복!
    }
}

// AOP 사용 - 로깅 코드를 한 곳에!
@Aspect
public class LoggingAspect {
    @Around("execution(* com.myapp..*(..))")  // 모든 메서드에 자동 적용
    public Object logAround(ProceedingJoinPoint joinPoint) {
        log.info("메서드 시작: " + joinPoint.getSignature());
        Object result = joinPoint.proceed();
        log.info("메서드 끝");
        return result;
    }
}

// OrderService는 비즈니스 로직만!
@Service
public class OrderService {
    public void createOrder() {
        // 비즈니스 로직만 작성
        // 로깅은 AOP가 자동으로!
    }
}
```

---

### 비유 5: PSA = 다국적 전원 어댑터

```
PSA (Portable Service Abstraction) = 범용 어댑터

여행 갈 때:
- 한국: 220V
- 미국: 110V
- 일본: 100V

다국적 어댑터 하나면 어디서든 OK!

┌──────────────────────────────┐
│   🔌 전자기기 (내 코드)       │
│   "그냥 플러그만 꽂으면 됨"    │
└──────────────────────────────┘
           ↓
┌──────────────────────────────┐
│   🔄 범용 어댑터 (PSA)        │
│   "전압 자동 변환"             │
└──────────────────────────────┘
           ↓
    어느 나라든 사용 가능
    ├─ 🇰🇷 한국 (220V)
    ├─ 🇺🇸 미국 (110V)
    └─ 🇯🇵 일본 (100V)
```

**Spring PSA**:
```java
// PSA 덕분에 구현체를 몰라도 사용 가능!

// 트랜잭션 - JDBC든 JPA든 똑같이 사용
@Transactional
public void transferMoney() {
    // JDBC든 JPA든 Hibernate든 상관없음!
}

// 캐싱 - Redis든 Ehcache든 똑같이 사용
@Cacheable("users")
public User findById(Long id) {
    // Redis든 Ehcache든 상관없음!
}

// 메시징 - Kafka든 RabbitMQ든 똑같이 사용
@JmsListener(destination = "orders")
public void receiveMessage(String message) {
    // Kafka든 RabbitMQ든 상관없음!
}
```

---

### 🎯 종합 비교표

```
┌──────────┬────────────┬────────────┬────────────┐
│ Spring   │ 자동차공장  │ 레고블록    │ CCTV      │
├──────────┼────────────┼────────────┼────────────┤
│ IoC      │ 자동화공장  │ 조립설명서  │ 중앙제어실 │
│ DI       │ 부품공급    │ 블록조립    │ 자동연결   │
│ AOP      │ 품질검사    │ 색칠하기    │ 감시카메라 │
│ PSA      │ 범용공구    │ 호환블록    │ 범용시스템 │
└──────────┴────────────┴────────────┴────────────┘
```

---

## 📖 핵심 개념

### 개념 설명 (3단계 깊이)

#### 1️⃣ 초보자 수준 설명

**Spring은 Java 웹 개발을 쉽게 해주는 도구 상자입니다.**

```
Spring = 만능 도구 상자

1. IoC Container (자동 객체 창고)
   - 객체를 자동으로 만들어줌
   - 필요할 때 꺼내 씀

2. DI (자동 조립)
   - 객체들을 자동으로 연결
   - new 키워드 안 써도 됨

3. AOP (자동 기능 추가)
   - 로깅, 트랜잭션을 자동으로
   - 반복 코드 제거

4. PSA (어댑터)
   - 기술 바꿔도 코드 안 바꿈
   - 호환성 UP
```

**초보자가 기억할 것**:
- Spring = 자동화 도구
- new 대신 @Component, @Service
- 어려운 일은 Spring이 대신
- 나는 비즈니스 로직만 집중

---

#### 2️⃣ 중급자 수준 설명

**Spring은 엔터프라이즈 애플리케이션 개발을 위한 포괄적 프레임워크입니다.**

```
Spring Framework Architecture:

┌─────────────────────────────────────────┐
│         Application Layer               │
│    (내가 작성하는 비즈니스 로직)           │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│          Spring Framework                │
│                                          │
│  ┌────────────────────────────────┐    │
│  │  Spring Core Container         │    │
│  │  - IoC Container               │    │
│  │  - BeanFactory                 │    │
│  │  - ApplicationContext          │    │
│  └────────────────────────────────┘    │
│                                          │
│  ┌────────────┬──────────┬───────────┐ │
│  │ Spring MVC │ Spring   │ Spring    │ │
│  │ (Web)      │ Data     │ Security  │ │
│  └────────────┴──────────┴───────────┘ │
│                                          │
│  ┌────────────────────────────────┐    │
│  │  AOP & Instrumentation         │    │
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│       Infrastructure (JDBC, JPA, etc)    │
└─────────────────────────────────────────┘
```

**핵심 모듈**:

1. **Spring Core (핵심)**
   - IoC Container: BeanFactory, ApplicationContext
   - Bean 생명주기 관리
   - 의존성 주입 (DI)

2. **Spring AOP**
   - 횡단 관심사 분리
   - 프록시 기반 (JDK Dynamic, CGLIB)
   - 트랜잭션, 로깅, 보안

3. **Spring MVC**
   - DispatcherServlet
   - Model-View-Controller
   - RESTful API

4. **Spring Data**
   - JPA, JDBC 추상화
   - Repository 패턴
   - Query 자동 생성

5. **Spring Security**
   - 인증(Authentication)
   - 인가(Authorization)
   - CSRF, CORS

---

#### 3️⃣ 고급자 수준 설명

**Spring은 POJO 기반의 엔터프라이즈 서비스 추상화 계층을 제공하는 경량 IoC 컨테이너입니다.**

```
Spring 내부 아키텍처 (심화):

┌────────────────────────────────────────────────────────┐
│                Application Context                      │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Bean Definition Registry                  │  │
│  │  - Bean 메타데이터 저장                            │  │
│  │  - @Component, @Bean 스캔 결과                    │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Bean Factory Post Processor               │  │
│  │  - Bean 정의 수정 (BeanFactoryPostProcessor)     │  │
│  │  - @Configuration 클래스 처리                     │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Bean Instantiation                        │  │
│  │  - Bean 인스턴스 생성                             │  │
│  │  - Constructor/Factory Method 호출                │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Bean Post Processor                       │  │
│  │  - postProcessBeforeInitialization()             │  │
│  │  - AOP Proxy 생성 (AnnotationAwareAspectJ...)   │  │
│  │  - @Autowired, @PostConstruct 처리               │  │
│  │  - postProcessAfterInitialization()              │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Fully Initialized Bean                    │  │
│  │  - 싱글톤 캐시에 저장 (singletonObjects)          │  │
│  │  - 애플리케이션에서 사용 가능                      │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

**고급 주제**:

1. **IoC Container 내부**
   - BeanFactory vs ApplicationContext
   - BeanDefinition과 메타데이터
   - BeanPostProcessor 체인
   - Circular Dependency 해결

2. **AOP 프록시 메커니즘**
   - JDK Dynamic Proxy (인터페이스 기반)
   - CGLIB Proxy (클래스 기반)
   - ProxyFactory와 Advisor
   - AspectJ Weaving (Compile/Load-time)

3. **Bean 생명주기 콜백**
   - InitializingBean, DisposableBean
   - @PostConstruct, @PreDestroy
   - Custom init-method, destroy-method
   - Lifecycle Processor

4. **Event 메커니즘**
   - ApplicationEvent
   - ApplicationListener
   - @EventListener
   - 비동기 이벤트 처리

5. **Resource 추상화**
   - Resource, ResourceLoader
   - ClassPathResource, FileSystemResource
   - PropertySource, Environment

---

### 주요 용어 정리

| 용어 | 영문 | 설명 | 예시 |
|------|------|------|------|
| IoC | Inversion of Control | 제어의 역전, Spring이 객체 생성 | @Component |
| DI | Dependency Injection | 의존성 주입, 객체 자동 연결 | @Autowired |
| AOP | Aspect-Oriented Programming | 관점 지향 프로그래밍, 횡단 관심사 | @Transactional |
| PSA | Portable Service Abstraction | 서비스 추상화, 기술 독립적 | @Cacheable |
| Bean | - | Spring이 관리하는 객체 | @Service, @Repository |
| Container | - | Bean을 담는 그릇 | ApplicationContext |
| POJO | Plain Old Java Object | 순수 Java 객체 | 특별한 인터페이스 없음 |

---

### Spring Framework 전체 구조

```
┌─────────────────────────────────────────────────────────┐
│                 Spring Framework                         │
│                    (전체 생태계)                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │          Spring Core Container                 │    │
│  │   (IoC, DI, Bean, Context, SpEL)              │    │
│  │                                                │    │
│  │   이것이 Spring의 심장!                        │    │
│  │   모든 것의 기반                               │    │
│  └────────────────────────────────────────────────┘    │
│                        ↓                                 │
│  ┌─────────────┬──────────────┬──────────────────┐    │
│  │             │              │                  │    │
│  │ Spring MVC  │ Spring Data  │ Spring Security  │    │
│  │ (Web)       │ (Database)   │ (보안)           │    │
│  │             │              │                  │    │
│  │ - Controller│ - JPA        │ - Authentication │    │
│  │ - REST API  │ - JDBC       │ - Authorization  │    │
│  │ - View      │ - Repository │ - JWT            │    │
│  │             │              │                  │    │
│  └─────────────┴──────────────┴──────────────────┘    │
│                                                          │
│  ┌──────────────────────────────────────────────┐      │
│  │               Spring Boot                     │      │
│  │   (자동 설정, 내장 서버, 편리한 개발)           │      │
│  │                                               │      │
│  │   Spring을 더 쉽게 사용하게 해주는 도구!       │      │
│  └──────────────────────────────────────────────┘      │
│                                                          │
└─────────────────────────────────────────────────────────┘

사용 흐름:
1. Spring Core로 기초 다지기 (IoC/DI)
2. Spring MVC로 웹 개발
3. Spring Data로 DB 연동
4. Spring Security로 보안
5. Spring Boot로 전체 통합
```

---

### Spring vs Spring Boot

| 비교 항목 | Spring Framework | Spring Boot |
|----------|-----------------|-------------|
| 설정 | XML or Java Config (복잡) | 자동 설정 (Auto Configuration) |
| 서버 | 외부 Tomcat 필요 | 내장 Tomcat (embedded) |
| 의존성 | 하나하나 추가 | Starter로 묶음 |
| 실행 | WAR 배포 | JAR 실행 (java -jar) |
| 개발 시간 | 느림 (설정 많음) | 빠름 (설정 최소) |
| 학습 곡선 | 가파름 | 완만함 |

**예시**:
```java
// Spring Framework (복잡)
@Configuration
@EnableWebMvc
@ComponentScan("com.myapp")
public class WebConfig implements WebMvcConfigurer {
    @Bean
    public ViewResolver viewResolver() {
        InternalResourceViewResolver resolver = new InternalResourceViewResolver();
        resolver.setPrefix("/WEB-INF/views/");
        resolver.setSuffix(".jsp");
        return resolver;
    }
    // 수십 줄의 설정...
}

// Spring Boot (간단)
@SpringBootApplication  // 이것만으로 끝!
public class MyApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}
// 설정 거의 없음, 자동으로 처리!
```

**결론**:
- Spring = 프레임워크의 뼈대
- Spring Boot = Spring을 쉽게 쓰게 해주는 도구
- 이 가이드는 Spring Boot 기반으로 학습!

---

### IoC (Inversion of Control) 상세

**제어의 역전**: 객체의 생성과 생명주기를 개발자가 아닌 Spring이 관리

```java
// 전통적 방식 - 개발자가 제어
public class OrderService {
    private PaymentService paymentService;

    public OrderService() {
        // 내가 직접 생성 (강한 결합)
        this.paymentService = new PaymentService();
    }
}

// IoC - Spring이 제어
@Service
public class OrderService {
    private final PaymentService paymentService;

    // Spring이 생성해서 주입 (느슨한 결합)
    @Autowired
    public OrderService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }
}
```

**IoC Container의 역할**:
1. Bean 정의 읽기 (@Component, @Service, @Repository, @Bean)
2. Bean 인스턴스 생성
3. Bean 의존성 주입
4. Bean 생명주기 관리
5. Bean 소멸 처리

---

### DI (Dependency Injection) 상세

**의존성 주입**: 객체가 필요로 하는 의존 객체를 외부에서 주입

**DI의 3가지 방법**:

```java
// 1. 생성자 주입 (권장 ⭐⭐⭐⭐⭐)
@Service
public class OrderService {
    private final PaymentService paymentService;  // final 가능

    public OrderService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }
}
// 장점: 불변성, 테스트 용이, NPE 방지

// 2. Setter 주입 (선택적 의존성)
@Service
public class OrderService {
    private PaymentService paymentService;

    @Autowired
    public void setPaymentService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }
}
// 장점: 선택적 의존성, 순환 참조 해결

// 3. 필드 주입 (비권장 ❌)
@Service
public class OrderService {
    @Autowired
    private PaymentService paymentService;
}
// 단점: 테스트 어려움, 불변성 없음, 순환 참조 늦게 발견
```

**왜 생성자 주입을 권장하나?**
- 불변성(final)
- NPE 방지 (생성 시점 주입)
- 테스트 용이 (Mock 주입 쉬움)
- 순환 참조 즉시 발견

---

### AOP (Aspect-Oriented Programming) 상세

**관점 지향 프로그래밍**: 횡단 관심사를 모듈화

**횡단 관심사 (Cross-Cutting Concerns)**:
- 로깅
- 트랜잭션
- 보안
- 캐싱
- 모니터링

```java
// AOP 없이 - 모든 곳에 반복
public class OrderService {
    public void createOrder() {
        log.info("createOrder 시작");     // 반복
        checkPermission();                // 반복
        try {
            // 비즈니스 로직
            beginTransaction();           // 반복
            // ...
            commit();                     // 반복
        } catch (Exception e) {
            rollback();                   // 반복
        }
        log.info("createOrder 끝");       // 반복
    }
}

// AOP 사용 - 한 곳에 모아서
@Aspect
@Component
public class LoggingAspect {
    @Around("@annotation(org.springframework.transaction.annotation.Transactional)")
    public Object logAround(ProceedingJoinPoint joinPoint) throws Throwable {
        log.info("메서드 시작: {}", joinPoint.getSignature());

        long start = System.currentTimeMillis();
        try {
            Object result = joinPoint.proceed();
            long end = System.currentTimeMillis();
            log.info("메서드 끝: {} ({}ms)", joinPoint.getSignature(), end - start);
            return result;
        } catch (Exception e) {
            log.error("메서드 에러: {}", e.getMessage());
            throw e;
        }
    }
}

// 비즈니스 로직은 깔끔!
@Service
public class OrderService {
    @Transactional
    public void createOrder() {
        // 비즈니스 로직만!
        // 로깅, 트랜잭션은 AOP가 자동 처리
    }
}
```

---

### PSA (Portable Service Abstraction) 상세

**서비스 추상화**: 기술 구현체가 바뀌어도 코드는 그대로

```java
// 1. 트랜잭션 PSA
@Transactional  // JDBC든 JPA든 Hibernate든 똑같이 사용
public void transferMoney() {
    // 구현체가 바뀌어도 이 코드는 동일
}

// 2. 캐싱 PSA
@Cacheable("users")  // Redis든 Ehcache든 Caffeine이든 똑같이
public User findById(Long id) {
    return userRepository.findById(id);
}

// 3. 웹 PSA
@GetMapping("/users")  // Servlet이든 Reactive든 똑같이
public List<User> getUsers() {
    return userService.findAll();
}
```

**추상화 계층**:
```
내 코드 (@Transactional)
      ↓
Spring 추상화 계층 (PlatformTransactionManager)
      ↓
구현체 선택 (DataSourceTransactionManager, JpaTransactionManager...)
```

---

**다음 Part 2에서 계속...**

기본 실습, 주니어 시나리오가 이어집니다!
