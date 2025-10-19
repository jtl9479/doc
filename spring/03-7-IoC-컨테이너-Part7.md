# 03장: IoC 컨테이너 - Part 7 (FAQ)

**[← 이전: Part 6](03-6-IoC-컨테이너-Part6.md)** | **[다음: Part 8 →](03-8-IoC-컨테이너-Part8.md)**

---

## ❓ FAQ

<details>
<summary><strong>Q1: IoC와 DI의 차이점이 무엇인가요?</strong></summary>

**A**: IoC는 개념(Concept)이고, DI는 구현 방법(Implementation)입니다.

**상세 설명**:
- **IoC (Inversion of Control)**: 제어의 역전이라는 **설계 원칙**
  - "객체의 생성과 생명주기 관리를 프레임워크가 담당한다"
  - 개발자가 아닌 프레임워크가 제어권을 가짐

- **DI (Dependency Injection)**: IoC를 실현하는 **구체적인 기술**
  - "필요한 의존성을 외부에서 주입한다"
  - 생성자 주입, Setter 주입, 필드 주입 등

**예시**:
```java
// IoC 개념
// "Spring이 객체를 생성하고 관리한다" ← 이것이 IoC

@Service
public class UserService {
    // DI 구현
    // "Spring이 필요한 UserRepository를 주입한다" ← 이것이 DI
    @Autowired
    private UserRepository userRepository;
}
```

**비유**:
- **IoC**: "식당에서 요리사가 음식을 만든다" (전체 시스템 설계)
- **DI**: "주문한 음식을 테이블로 가져다준다" (구체적 구현 방법)

**실무 팁**:
💡 면접에서 "IoC가 뭔가요?"라고 물으면, DI 예시와 함께 설명하면 좋습니다.

</details>

---

<details>
<summary><strong>Q2: @Component, @Service, @Repository, @Controller의 차이는 무엇인가요?</strong></summary>

**A**: 기술적으로는 모두 동일하지만, **의미적 구분**과 **추가 기능**에서 차이가 있습니다.

**상세 설명**:

| 어노테이션 | 계층 | 역할 | 추가 기능 |
|-----------|------|------|----------|
| `@Component` | 일반 | Spring Bean (범용) | 없음 |
| `@Service` | Service | 비즈니스 로직 | 없음 (의미만) |
| `@Repository` | Data Access | 데이터 접근 | **예외 변환** |
| `@Controller` | Presentation | 웹 요청 처리 | **MVC 연동** |

**예시**:
```java
// 1. @Component: 범용 Bean
@Component
public class EmailValidator {
    public boolean validate(String email) { }
}

// 2. @Service: 비즈니스 로직 (트랜잭션 처리 등)
@Service
public class OrderService {
    public void createOrder() { }
}

// 3. @Repository: 데이터 접근 (예외 변환!)
@Repository
public class UserRepository {
    // SQLException → DataAccessException으로 자동 변환
    public User findById(Long id) { }
}

// 4. @Controller: 웹 요청 처리
@Controller
public class UserController {
    @GetMapping("/users")
    public String list() { return "users"; }
}
```

**@Repository의 특별한 기능**:
```java
@Repository
public class JdbcUserRepository {
    public User findById(Long id) {
        // JDBC 사용 시 SQLException 발생 가능
        // → Spring이 자동으로 DataAccessException으로 변환
        // → DB 종류에 관계없이 일관된 예외 처리 가능
    }
}
```

**실무 팁**:
💡 계층별로 명확히 구분하면 코드 가독성이 높아집니다.
💡 어느 걸 써야 할지 모르겠으면 `@Component` 사용 (나중에 변경 가능)

</details>

---

<details>
<summary><strong>Q3: 생성자 주입, Setter 주입, 필드 주입 중 어떤 것을 써야 하나요?</strong></summary>

**A**: **생성자 주입(Constructor Injection)**을 사용하세요 (Spring 공식 권장).

**상세 설명**:

#### 1️⃣ 생성자 주입 (권장 ✅)
```java
@Service
public class OrderService {
    private final ProductService productService;  // final 가능!

    @Autowired  // Spring 4.3+ 생성자 1개면 생략 가능
    public OrderService(ProductService productService) {
        this.productService = productService;
    }
}
```

**장점**:
- ✅ 불변성 보장 (`final` 키워드 사용 가능)
- ✅ 순환 참조 조기 발견 (컴파일 타임)
- ✅ 테스트 용이 (new로 직접 생성 가능)
- ✅ NPE 방지 (객체 생성 시점에 의존성 주입)

#### 2️⃣ Setter 주입 (선택적 의존성에만)
```java
@Service
public class ReportService {
    private EmailService emailService;

    @Autowired(required = false)  // 선택적
    public void setEmailService(EmailService emailService) {
        this.emailService = emailService;
    }
}
```

**사용 시기**: 선택적 의존성 (없어도 동작하는 경우)

#### 3️⃣ 필드 주입 (비권장 ❌)
```java
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;  // 비권장!
}
```

**단점**:
- ❌ final 사용 불가 (불변성 보장 안 됨)
- ❌ 테스트 어려움 (Reflection 필요)
- ❌ 순환 참조 늦게 발견 (런타임)

**실무 팁**:
💡 **원칙**: 생성자 주입 > Setter 주입 > 필드 주입
💡 Lombok의 `@RequiredArgsConstructor`로 생성자 주입 간편화

```java
@Service
@RequiredArgsConstructor  // final 필드로 생성자 자동 생성
public class OrderService {
    private final ProductService productService;
    // 생성자 자동 생성됨!
}
```

</details>

---

<details>
<summary><strong>Q4: Bean의 기본 스코프는 무엇이고, 언제 변경하나요?</strong></summary>

**A**: 기본 스코프는 **Singleton**이며, 대부분의 경우 그대로 사용합니다.

**상세 설명**:

#### Singleton Scope (기본값)
```java
@Service  // 기본적으로 Singleton
public class UserService {
    // 애플리케이션 전체에서 1개 인스턴스만 존재
}
```

**특징**:
- ✅ 메모리 효율적 (인스턴스 1개만)
- ✅ 성능 우수 (객체 재사용)
- ⚠️ **주의**: 상태를 가지면 안 됨 (Stateless)

**잘못된 예**:
```java
@Service
public class OrderService {
    private int orderCount = 0;  // ❌ 위험!

    public void createOrder() {
        orderCount++;  // 모든 요청이 공유 → 동시성 문제!
    }
}
```

#### Prototype Scope (요청마다 새 인스턴스)
```java
@Service
@Scope("prototype")  // 매번 새로운 인스턴스
public class ReportGenerator {
    private String reportData;  // ✅ 상태 가능

    public void generateReport() {
        // 각 요청마다 독립적
    }
}
```

**사용 시기**:
- 상태를 가져야 하는 Bean
- 각 요청마다 독립적인 인스턴스 필요

#### 웹 스코프

```java
// Request Scope: HTTP 요청마다 1개
@Component
@Scope(value = "request", proxyMode = ScopedProxyMode.TARGET_CLASS)
public class RequestContext {
    private String requestId;
}

// Session Scope: HTTP 세션마다 1개
@Component
@Scope(value = "session", proxyMode = ScopedProxyMode.TARGET_CLASS)
public class ShoppingCart {
    private List<Item> items = new ArrayList<>();
}
```

**비교표**:

| 스코프 | 생명주기 | 사용 시기 |
|--------|---------|----------|
| Singleton | 컨테이너와 동일 | **대부분의 경우** (99%) |
| Prototype | 요청마다 생성 | 상태를 가져야 할 때 |
| Request | HTTP 요청마다 | 요청별 컨텍스트 저장 |
| Session | HTTP 세션마다 | 사용자별 데이터 (장바구니 등) |

**실무 팁**:
💡 성능이 중요하면 Singleton 유지
💡 상태가 필요하면 Prototype 또는 Request 스코프

</details>

---

<details>
<summary><strong>Q5: ApplicationContext와 BeanFactory의 차이는 무엇인가요?</strong></summary>

**A**: `ApplicationContext`는 `BeanFactory`의 확장 버전으로, 실무에서는 `ApplicationContext`를 사용합니다.

**상세 설명**:

#### BeanFactory (기본 컨테이너)
```java
BeanFactory factory = new XmlBeanFactory(new FileSystemResource("beans.xml"));
MyBean bean = (MyBean) factory.getBean("myBean");
```

**기능**:
- Bean 생성 및 관리
- 의존성 주입
- **지연 로딩** (Lazy Loading)

#### ApplicationContext (고급 컨테이너)
```java
ApplicationContext context = new AnnotationConfigApplicationContext(AppConfig.class);
MyBean bean = context.getBean(MyBean.class);
```

**추가 기능**:
- ✅ 국제화 (i18n) 지원
- ✅ 이벤트 발행/구독
- ✅ 리소스 로딩
- ✅ **즉시 로딩** (Eager Loading)

**비교 예시**:

```java
// BeanFactory: Bean을 사용할 때 생성 (Lazy)
BeanFactory factory = ...;
// 여기까지는 Bean 생성 안 됨
MyBean bean = factory.getBean(MyBean.class);  // 이제 생성!

// ApplicationContext: 컨테이너 시작 시 모든 Bean 생성 (Eager)
ApplicationContext context = ...;
// 여기서 이미 모든 Singleton Bean 생성됨!
MyBean bean = context.getBean(MyBean.class);  // 이미 생성된 것 반환
```

**계층 구조**:
```
BeanFactory (최상위 인터페이스)
    ↓
ApplicationContext (확장)
    ↓
ConfigurableApplicationContext (설정 가능)
    ↓
WebApplicationContext (웹 환경)
```

**실무 선택**:

| 상황 | 선택 |
|------|------|
| 일반 애플리케이션 | **ApplicationContext** (권장) |
| 메모리 제약 심한 환경 (IoT 등) | BeanFactory (드묾) |
| Spring Boot | **자동으로 ApplicationContext** |

**Spring Boot에서**:
```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        ApplicationContext context = SpringApplication.run(Application.class, args);
        // Spring Boot가 자동으로 ApplicationContext 생성
    }
}
```

**실무 팁**:
💡 99.9%의 경우 `ApplicationContext` 사용
💡 면접에서 차이를 물어보면 "BeanFactory는 기본, ApplicationContext는 확장"으로 답변

</details>

---

<details>
<summary><strong>Q6: @Configuration과 @Component의 차이는 무엇인가요?</strong></summary>

**A**: `@Configuration`은 **CGLIB Proxy**를 통해 Singleton을 보장하지만, `@Component`는 보장하지 않습니다.

**상세 설명**:

#### @Component로 Bean 등록
```java
@Component
public class AppConfig {

    @Bean
    public ServiceA serviceA() {
        return new ServiceA();
    }

    @Bean
    public ServiceB serviceB() {
        return new ServiceB(serviceA());  // serviceA() 직접 호출
        // ⚠️ 문제: serviceA()를 호출할 때마다 새 인스턴스 생성!
    }
}
```

**문제점**: `serviceA()`를 호출할 때마다 **새로운 인스턴스** 생성

#### @Configuration으로 Bean 등록
```java
@Configuration
public class AppConfig {

    @Bean
    public ServiceA serviceA() {
        return new ServiceA();
    }

    @Bean
    public ServiceB serviceB() {
        return new ServiceB(serviceA());  // serviceA() 호출
        // ✅ CGLIB Proxy가 가로채서 이미 생성된 Bean 반환!
    }
}
```

**장점**: `serviceA()`를 여러 번 호출해도 **같은 인스턴스** 반환 (Singleton)

#### 내부 동작 원리

```java
// Spring이 CGLIB로 @Configuration 클래스를 프록시로 감싸서
// 실제로는 이런 식으로 동작:

public class AppConfig$$EnhancerBySpringCGLIB extends AppConfig {
    private Map<String, Object> beanCache = new HashMap<>();

    @Override
    public ServiceA serviceA() {
        if (beanCache.containsKey("serviceA")) {
            return (ServiceA) beanCache.get("serviceA");  // 캐시 반환
        }
        ServiceA bean = super.serviceA();  // 실제 메서드 호출
        beanCache.put("serviceA", bean);
        return bean;
    }
}
```

#### 사용 시나리오

```java
// 시나리오 1: Bean들이 서로 의존하는 경우
@Configuration  // ← @Configuration 필수!
public class DatabaseConfig {

    @Bean
    public DataSource dataSource() {
        return new HikariDataSource();
    }

    @Bean
    public JdbcTemplate jdbcTemplate() {
        return new JdbcTemplate(dataSource());  // dataSource() 재호출
        // CGLIB이 같은 인스턴스 반환 보장!
    }
}

// 시나리오 2: Bean들이 독립적인 경우
@Component  // @Component도 OK
public class UtilConfig {

    @Bean
    public ObjectMapper objectMapper() {
        return new ObjectMapper();  // 독립적
    }

    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();  // 독립적
    }
}
```

**비교표**:

| 항목 | @Configuration | @Component |
|------|---------------|-----------|
| Singleton 보장 | ✅ CGLIB Proxy | ❌ 보장 안 됨 |
| 성능 | 약간 느림 (Proxy) | 빠름 |
| Bean 간 의존성 | ✅ 권장 | ❌ 주의 필요 |
| 사용 시기 | **Java Config** | 일반 Bean |

**실무 팁**:
💡 **설정 클래스**는 반드시 `@Configuration` 사용
💡 Bean 간 의존성이 있으면 `@Configuration` 필수
💡 Lite Mode (`@Component + @Bean`)는 성능이 중요한 경우에만

</details>

---

<details>
<summary><strong>Q7: @ComponentScan은 어떻게 동작하나요?</strong></summary>

**A**: `@ComponentScan`은 지정한 패키지를 재귀적으로 탐색하여 `@Component`가 붙은 클래스를 자동으로 Bean으로 등록합니다.

**상세 설명**:

#### 기본 동작
```java
@Configuration
@ComponentScan(basePackages = "com.example.myapp")
public class AppConfig {
    // "com.example.myapp" 패키지와 하위 패키지를 모두 스캔
}
```

**스캔 대상**:
- `@Component`
- `@Service` (내부에 `@Component` 포함)
- `@Repository`
- `@Controller`
- `@Configuration`

#### Spring Boot의 @SpringBootApplication

```java
@SpringBootApplication  // 이 안에 @ComponentScan 포함!
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}

// @SpringBootApplication은 다음과 동일:
@Configuration
@EnableAutoConfiguration
@ComponentScan  // 현재 패키지부터 하위 스캔
public @interface SpringBootApplication { }
```

**스캔 범위 예시**:
```
프로젝트 구조:
com/
└── example/
    ├── Application.java          ← @SpringBootApplication
    ├── controller/
    │   └── UserController.java   ✅ 스캔됨
    ├── service/
    │   └── UserService.java      ✅ 스캔됨
    └── repository/
        └── UserRepository.java   ✅ 스캔됨

com/other/
└── SomeService.java              ❌ 스캔 안 됨 (다른 패키지)
```

#### 커스터마이징

```java
// 1. 여러 패키지 스캔
@ComponentScan(basePackages = {"com.example.app", "com.example.common"})

// 2. 클래스 기준 스캔 (타입 안전)
@ComponentScan(basePackageClasses = {Application.class, CommonConfig.class})

// 3. 필터 사용
@ComponentScan(
    basePackages = "com.example",
    includeFilters = @Filter(type = FilterType.ANNOTATION, classes = MyCustomAnnotation.class),
    excludeFilters = @Filter(type = FilterType.REGEX, pattern = ".*Test.*")
)

// 4. 특정 Bean 제외
@ComponentScan(
    basePackages = "com.example",
    excludeFilters = @Filter(type = FilterType.ASSIGNABLE_TYPE, classes = LegacyService.class)
)
```

#### 내부 동작 과정

```
1. ClassPathScanningCandidateComponentProvider가 클래스 파일 탐색
   ↓
2. ASM (바이트코드 리더)로 클래스 메타데이터 읽기
   ↓
3. @Component 어노테이션 확인
   ↓
4. BeanDefinition 생성
   ↓
5. BeanFactory에 등록
```

**성능 고려사항**:
```java
// ❌ 나쁜 예: 너무 넓은 범위 스캔
@ComponentScan(basePackages = "com")  // 전체 com 패키지 스캔 (느림)

// ✅ 좋은 예: 필요한 패키지만 스캔
@ComponentScan(basePackages = "com.example.myapp")
```

**실무 팁**:
💡 Spring Boot 사용 시 `@SpringBootApplication`이 있는 패키지를 **루트**로 설정
💡 테스트 클래스는 자동으로 제외됨 (src/test 폴더)
💡 스캔 범위가 넓으면 애플리케이션 시작이 느려짐

</details>

---

<details>
<summary><strong>Q8: Bean의 생명주기 콜백을 사용하는 이유는 무엇인가요?</strong></summary>

**A**: Bean 초기화 시 **리소스 할당**(DB 연결, 캐시 로드 등)과 소멸 시 **리소스 해제**(연결 종료, 파일 닫기 등)를 자동화하기 위해 사용합니다.

**상세 설명**:

#### 생명주기 단계

```
1. Bean 생성 (Instantiation)
   ↓
2. 의존성 주입 (Dependency Injection)
   ↓
3. 초기화 콜백 ← @PostConstruct
   ↓
4. 사용 (Bean 사용 가능)
   ↓
5. 소멸 콜백 ← @PreDestroy
   ↓
6. Bean 제거
```

#### 초기화 콜백 (@PostConstruct)

```java
@Service
public class DatabaseService {

    @Autowired
    private DataSource dataSource;

    private Connection connection;

    // 의존성 주입 완료 후 실행
    @PostConstruct
    public void init() {
        try {
            // DB 연결 초기화
            connection = dataSource.getConnection();
            System.out.println("✅ DB 연결 성공");

            // 초기 데이터 로드
            loadInitialData();
        } catch (SQLException e) {
            throw new RuntimeException("DB 연결 실패", e);
        }
    }

    private void loadInitialData() {
        // 캐시 데이터 로드 등
    }
}
```

#### 소멸 콜백 (@PreDestroy)

```java
@Service
public class DatabaseService {

    private Connection connection;

    // 컨테이너 종료 전 실행
    @PreDestroy
    public void cleanup() {
        try {
            if (connection != null && !connection.isClosed()) {
                connection.close();
                System.out.println("🧹 DB 연결 종료");
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

#### 실무 사용 예시

**1. 외부 API 클라이언트**:
```java
@Service
public class PaymentApiClient {

    private HttpClient httpClient;

    @PostConstruct
    public void init() {
        // API 클라이언트 초기화
        httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .build();
        System.out.println("✅ Payment API 클라이언트 준비 완료");
    }

    @PreDestroy
    public void cleanup() {
        // 리소스 정리
        if (httpClient != null) {
            // 연결 풀 종료 등
            System.out.println("🧹 Payment API 클라이언트 종료");
        }
    }
}
```

**2. 스케줄러**:
```java
@Service
public class ReportScheduler {

    private ScheduledExecutorService scheduler;

    @PostConstruct
    public void start() {
        scheduler = Executors.newScheduledThreadPool(1);
        scheduler.scheduleAtFixedRate(
                this::generateReport,
                0, 1, TimeUnit.HOURS
        );
        System.out.println("✅ 리포트 스케줄러 시작");
    }

    @PreDestroy
    public void stop() {
        if (scheduler != null) {
            scheduler.shutdown();
            System.out.println("🧹 리포트 스케줄러 종료");
        }
    }

    private void generateReport() {
        // 리포트 생성 로직
    }
}
```

#### 생명주기 콜백 3가지 방법

```java
// 방법 1: @PostConstruct / @PreDestroy (권장 ✅)
@PostConstruct
public void init() { }

@PreDestroy
public void destroy() { }

// 방법 2: InitializingBean / DisposableBean (구식)
public class MyBean implements InitializingBean, DisposableBean {
    @Override
    public void afterPropertiesSet() { }  // 초기화

    @Override
    public void destroy() { }  // 소멸
}

// 방법 3: @Bean의 initMethod / destroyMethod
@Bean(initMethod = "init", destroyMethod = "cleanup")
public MyService myService() {
    return new MyService();
}
```

**권장 순서**:
1. **@PostConstruct / @PreDestroy** ← 가장 권장
2. @Bean(initMethod/destroyMethod)
3. InitializingBean / DisposableBean ← 레거시

**실무 팁**:
💡 생성자에서는 의존성이 주입되기 전이므로, 초기화 로직은 `@PostConstruct`에 작성
💡 `@PreDestroy`는 정상 종료 시에만 호출 (kill -9 같은 강제 종료 시에는 호출 안 됨)
💡 테스트에서 `@PostConstruct` 실행 확인 필요 (초기화 로직 버그 방지)

</details>

---

**[← 이전: Part 6](03-6-IoC-컨테이너-Part6.md)** | **[다음: Part 8 →](03-8-IoC-컨테이너-Part8.md)**
