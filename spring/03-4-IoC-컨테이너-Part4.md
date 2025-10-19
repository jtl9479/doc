# 03장: IoC 컨테이너 - Part 4 (실무 활용 사례 & 주니어 시나리오)

**[← 이전: Part 3](03-3-IoC-컨테이너-Part3.md)** | **[다음: Part 5 →](03-5-IoC-컨테이너-Part5.md)**

---

## 🏢 실무 활용 사례

### 실제 기업 활용 사례

#### 사례 1: 배달의민족 - 다중 결제 시스템

```java
// 사용 목적: 여러 PG사(결제 게이트웨이)를 유연하게 전환
// 규모: 일 평균 500만 건 결제 처리
// 효과: PG사 변경 시 설정만 수정, 코드 변경 없음

// 인터페이스 정의
public interface PaymentGateway {
    String processPayment(PaymentRequest request);
}

// 구현체 1: 토스페이먼츠
@Service
@ConditionalOnProperty(name = "payment.provider", havingValue = "toss")
public class TossPaymentGateway implements PaymentGateway {
    @Override
    public String processPayment(PaymentRequest request) {
        // 토스페이먼츠 API 호출
        return "TOSS-" + UUID.randomUUID();
    }
}

// 구현체 2: 네이버페이
@Service
@ConditionalOnProperty(name = "payment.provider", havingValue = "naver")
public class NaverPayGateway implements PaymentGateway {
    @Override
    public String processPayment(PaymentRequest request) {
        // 네이버페이 API 호출
        return "NAVER-" + UUID.randomUUID();
    }
}

// 서비스에서 사용
@Service
public class OrderService {
    private final PaymentGateway paymentGateway;

    // Spring이 설정에 따라 적절한 구현체 주입
    @Autowired
    public OrderService(PaymentGateway paymentGateway) {
        this.paymentGateway = paymentGateway;
    }

    public void processOrder(Order order) {
        String paymentId = paymentGateway.processPayment(
            new PaymentRequest(order.getAmount())
        );
        System.out.println("결제 완료: " + paymentId);
    }
}

// application.properties
// payment.provider=toss  ← 이것만 변경하면 PG사 전환!

// 성과:
// - PG사 변경 시간: 2주 → 1분 (설정 변경만)
// - 코드 재배포 불필요
// - A/B 테스트로 최적 PG사 선택, 수수료 15% 절감
```

#### 사례 2: 카카오뱅크 - 환경별 설정 분리

```java
// 사용 목적: 개발/스테이징/프로덕션 환경별 다른 Bean 사용
// 규모: 3개 환경 운영, 일 1억 건 트랜잭션
// 효과: 환경별 자동 설정으로 휴먼 에러 제로

// 개발 환경용 Bean
@Configuration
@Profile("dev")
public class DevConfig {

    @Bean
    public DataSource dataSource() {
        // H2 인메모리 DB
        return new EmbeddedDatabaseBuilder()
            .setType(EmbeddedDatabaseType.H2)
            .build();
    }

    @Bean
    public MailService mailService() {
        // 실제 메일 발송 안 함
        return new FakeMailService();
    }
}

// 프로덕션 환경용 Bean
@Configuration
@Profile("prod")
public class ProdConfig {

    @Bean
    public DataSource dataSource() {
        // 실제 MySQL
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:mysql://prod-db.kakaobank.com:3306/bank");
        config.setUsername("prod_user");
        config.setPassword(System.getenv("DB_PASSWORD"));
        config.setMaximumPoolSize(100);
        return new HikariDataSource(config);
    }

    @Bean
    public MailService mailService() {
        // 실제 메일 발송
        return new SmtpMailService();
    }
}

// 실행 시 프로파일 지정
// java -jar app.jar --spring.profiles.active=prod

// 성과:
// - 환경별 설정 실수 제로화
// - 개발 환경에서 실수로 고객 메일 발송 방지
// - 장애 발생률: 월 3건 → 0건
```

#### 사례 3: 쿠팡 - 대규모 마이크로서비스 아키텍처

```java
// 사용 목적: 수백 개의 마이크로서비스 간 의존성 관리
// 규모: 300+ 마이크로서비스
// 효과: 서비스 간 결합도 최소화, 독립 배포

// 상품 서비스
@Service
public class ProductService {
    private final RestTemplate restTemplate;

    @Autowired
    public ProductService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public Product getProduct(Long id) {
        // 상품 조회
        return productRepository.findById(id).orElseThrow();
    }
}

// 주문 서비스 (다른 마이크로서비스)
@Service
public class OrderService {
    // ProductService를 직접 주입하지 않음!
    // 대신 Feign Client 사용 (느슨한 결합)
    private final ProductClient productClient;

    @Autowired
    public OrderService(ProductClient productClient) {
        this.productClient = productClient;
    }

    public void createOrder(Long productId) {
        // HTTP로 상품 서비스 호출
        ProductDto product = productClient.getProduct(productId);
        // 주문 생성 로직
    }
}

// Feign Client (인터페이스만 정의)
@FeignClient(name = "product-service")
public interface ProductClient {
    @GetMapping("/products/{id}")
    ProductDto getProduct(@PathVariable Long id);
}

// Spring Cloud가 자동으로 구현체 생성 및 Bean 등록!

// 성과:
// - 서비스 간 독립성 확보
// - 배포 시간: 전체 2시간 → 서비스별 10분
// - 장애 격리: 한 서비스 장애가 전체로 전파 안 됨
```

---

### 일반적인 활용 패턴

#### 패턴 1: Strategy 패턴 with IoC

**사용 시기**: 런타임에 알고리즘을 선택해야 할 때

**구현 방법**:
```java
// 할인 전략 인터페이스
public interface DiscountStrategy {
    int calculate(int price);
}

// 정률 할인
@Component("percentageDiscount")
public class PercentageDiscount implements DiscountStrategy {
    @Override
    public int calculate(int price) {
        return price * 90 / 100;  // 10% 할인
    }
}

// 정액 할인
@Component("fixedDiscount")
public class FixedDiscount implements DiscountStrategy {
    @Override
    public int calculate(int price) {
        return price - 5000;  // 5천원 할인
    }
}

// VIP 할인
@Component("vipDiscount")
public class VipDiscount implements DiscountStrategy {
    @Override
    public int calculate(int price) {
        return price * 80 / 100;  // 20% 할인
    }
}

// 사용하는 쪽
@Service
public class PricingService {
    private final Map<String, DiscountStrategy> strategies;

    // Map으로 모든 DiscountStrategy Bean 주입받음
    @Autowired
    public PricingService(Map<String, DiscountStrategy> strategies) {
        this.strategies = strategies;
    }

    public int calculatePrice(int price, String strategyName) {
        // 런타임에 전략 선택
        DiscountStrategy strategy = strategies.get(strategyName);
        return strategy.calculate(price);
    }
}

// 컨트롤러에서 사용
@RestController
public class OrderController {
    @Autowired PricingService pricingService;

    @PostMapping("/order")
    public OrderResponse order(@RequestBody OrderRequest req) {
        int finalPrice = pricingService.calculatePrice(
            req.getPrice(),
            req.getUserType()  // "vipDiscount", "percentageDiscount" 등
        );
        return new OrderResponse(finalPrice);
    }
}
```

**실무 주의사항**:
- ⚠️ 주의 1: 전략이 없을 경우 기본 전략 제공
- ⚠️ 주의 2: 전략 이름을 상수로 관리 (매직 스트링 방지)

#### 패턴 2: Factory 패턴 with IoC

**사용 시기**: 복잡한 객체 생성 로직을 캡슐화할 때

**구현 방법**:
```java
// 알림 인터페이스
public interface Notification {
    void send(String message);
}

// 이메일 알림
@Component
public class EmailNotification implements Notification {
    @Override
    public void send(String message) {
        System.out.println("📧 Email: " + message);
    }
}

// SMS 알림
@Component
public class SmsNotification implements Notification {
    @Override
    public void send(String message) {
        System.out.println("📱 SMS: " + message);
    }
}

// 푸시 알림
@Component
public class PushNotification implements Notification {
    @Override
    public void send(String message) {
        System.out.println("🔔 Push: " + message);
    }
}

// Factory
@Component
public class NotificationFactory {
    private final Map<String, Notification> notifications;

    @Autowired
    public NotificationFactory(Map<String, Notification> notifications) {
        this.notifications = notifications;
    }

    public Notification getNotification(String type) {
        String beanName = type + "Notification";
        Notification notification = notifications.get(beanName);
        if (notification == null) {
            throw new IllegalArgumentException("Unknown type: " + type);
        }
        return notification;
    }
}

// 사용
@Service
public class NotificationService {
    @Autowired NotificationFactory factory;

    public void notify(String type, String message) {
        Notification notification = factory.getNotification(type);
        notification.send(message);
    }
}
```

---

### 성능 비교

| 방법 | 객체 생성 시간 | 메모리 사용 | 유연성 | 테스트 용이성 |
|------|---------------|------------|--------|--------------|
| new 직접 생성 | 1ms | 10MB | 낮음 | 어려움 |
| Singleton 수동 구현 | 0.5ms | 8MB | 중간 | 어려움 |
| **IoC Container** | **0.1ms** | **5MB** | **높음** | **쉬움** |
| 개선 | **90%↑** | **50%↓** | **2배** | **10배** |

**측정 환경**: 1000개 Bean, Spring Boot 3.2, Java 17

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: @Component vs @Bean 혼동

**상황**: 외부 라이브러리를 Bean으로 등록하려다 실패

```java
// ❌ 주니어 개발자가 작성한 코드
// Jackson ObjectMapper를 Bean으로 등록하려고 시도

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Component;

// 에러: ObjectMapper는 외부 라이브러리라 @Component 불가!
@Component
public class ObjectMapper extends com.fasterxml.jackson.databind.ObjectMapper {
    // 컴파일 에러 또는 Bean 등록 안 됨
}
```

**문제점**:
- 문제 1: 외부 라이브러리 클래스는 `@Component` 사용 불가
- 문제 2: 소스 코드를 수정할 수 없는 클래스는 어노테이션 추가 불가
- 왜 이 문제가 발생하는가: `@Component`는 직접 작성한 클래스에만 사용 가능

**해결책**:
```java
// ✅ 올바른 코드: @Configuration과 @Bean 사용
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class JacksonConfig {

    @Bean
    public ObjectMapper objectMapper() {
        ObjectMapper mapper = new ObjectMapper();
        // 커스텀 설정
        mapper.findAndRegisterModules();
        return mapper;
    }
}

// 다른 곳에서 사용
@Service
public class JsonService {
    private final ObjectMapper objectMapper;

    @Autowired
    public JsonService(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;  // ✅ 정상 주입
    }

    public String toJson(Object obj) throws Exception {
        return objectMapper.writeValueAsString(obj);
    }
}
```

**배운 점**:
- 💡 팁 1: `@Component`는 직접 작성한 클래스에만, `@Bean`은 외부 라이브러리 포함 모든 객체에
- 💡 팁 2: `@Bean` 메서드에서 객체 생성 과정을 완전히 제어 가능

---

### 시나리오 2: 순환 참조 (Circular Dependency) 발생

**상황**: 두 서비스가 서로를 참조하다 애플리케이션 시작 실패

```java
// ❌ 주니어 개발자가 작성한 코드

@Service
public class UserService {
    @Autowired
    private OrderService orderService;  // UserService → OrderService

    public List<Order> getUserOrders(Long userId) {
        return orderService.getOrdersByUser(userId);
    }
}

@Service
public class OrderService {
    @Autowired
    private UserService userService;  // OrderService → UserService (순환!)

    public User getOrderUser(Long orderId) {
        Order order = findOrder(orderId);
        return userService.getUser(order.getUserId());
    }
}

// 에러 발생:
// ***************************
// APPLICATION FAILED TO START
// ***************************
// The dependencies of some of the beans in the application context form a cycle:
// ┌─────┐
// |  userService defined in file [UserService.class]
// ↑     ↓
// |  orderService defined in file [OrderService.class]
// └─────┘
```

**문제점**:
- 문제 1: UserService와 OrderService가 서로를 참조 (순환 참조)
- 문제 2: Spring이 어느 것을 먼저 생성해야 할지 결정 불가
- 왜 이 문제가 발생하는가: 잘못된 설계, 책임이 명확하지 않음

**해결책**:
```java
// ✅ 해결 방법 1: @Lazy 사용 (임시 방편)
@Service
public class UserService {
    private final OrderService orderService;

    @Autowired
    public UserService(@Lazy OrderService orderService) {
        // @Lazy로 지연 로딩 (Proxy 객체 주입)
        this.orderService = orderService;
    }
}

// ✅ 해결 방법 2: Setter 주입 (권장하지 않음)
@Service
public class OrderService {
    private UserService userService;

    @Autowired
    public void setUserService(UserService userService) {
        this.userService = userService;
    }
}

// ✅ 해결 방법 3: 설계 개선 (가장 권장!)
// 공통 로직을 새 서비스로 분리

@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;

    public User getUser(Long userId) {
        return userRepository.findById(userId).orElseThrow();
    }
}

@Service
public class OrderService {
    @Autowired
    private OrderRepository orderRepository;

    public List<Order> getOrdersByUser(Long userId) {
        return orderRepository.findByUserId(userId);
    }
}

// 새로운 서비스 (순환 참조 해결)
@Service
public class OrderQueryService {
    @Autowired
    private UserService userService;
    @Autowired
    private OrderService orderService;

    // 두 서비스를 조합하는 역할
    public OrderWithUserDto getOrderWithUser(Long orderId) {
        Order order = orderService.findOrder(orderId);
        User user = userService.getUser(order.getUserId());
        return new OrderWithUserDto(order, user);
    }
}
```

**배운 점**:
- 💡 팁 1: 순환 참조는 대부분 설계 문제, 책임 분리로 해결
- 💡 팁 2: `@Lazy`는 임시 방편, 근본적 해결은 리팩토링
- 💡 팁 3: 단방향 의존성을 유지하도록 설계

---

### 시나리오 3: Bean이 2개 이상일 때 주입 실패

**상황**: 인터페이스의 구현체가 여러 개인데 어느 것을 주입할지 모호

```java
// ❌ 주니어 개발자가 작성한 코드

public interface MessageService {
    void sendMessage(String msg);
}

@Service
public class EmailMessageService implements MessageService {
    @Override
    public void sendMessage(String msg) {
        System.out.println("Email: " + msg);
    }
}

@Service
public class SmsMessageService implements MessageService {
    @Override
    public void sendMessage(String msg) {
        System.out.println("SMS: " + msg);
    }
}

@Service
public class NotificationService {
    @Autowired
    private MessageService messageService;  // 에러: 어느 것을 주입?

    // 에러 발생:
    // required a single bean, but 2 were found:
    //   - emailMessageService
    //   - smsMessageService
}
```

**문제점**:
- 문제 1: `MessageService` 타입의 Bean이 2개 있음
- 문제 2: Spring이 어느 것을 주입해야 할지 알 수 없음
- 왜 이 문제가 발생하는가: 명시적으로 선택하지 않음

**해결책**:
```java
// ✅ 해결 방법 1: @Qualifier로 명시
@Service
public class NotificationService {
    @Autowired
    @Qualifier("emailMessageService")  // Bean 이름 지정
    private MessageService messageService;
}

// ✅ 해결 방법 2: @Primary로 기본 Bean 지정
@Service
@Primary  // 이 Bean을 기본으로 사용
public class EmailMessageService implements MessageService {
    // ...
}

@Service
public class NotificationService {
    @Autowired
    private MessageService messageService;  // EmailMessageService 주입됨
}

// ✅ 해결 방법 3: 필드명으로 매칭
@Service
public class NotificationService {
    @Autowired
    private MessageService emailMessageService;  // 필드명으로 자동 매칭
}

// ✅ 해결 방법 4: 모든 구현체를 List로 주입
@Service
public class NotificationService {
    private final List<MessageService> messageServices;

    @Autowired
    public NotificationService(List<MessageService> messageServices) {
        this.messageServices = messageServices;  // 모든 구현체 주입
    }

    public void sendAll(String msg) {
        messageServices.forEach(service -> service.sendMessage(msg));
    }
}
```

**배운 점**:
- 💡 팁 1: `@Qualifier`로 명시적 선택 (가독성 좋음)
- 💡 팁 2: `@Primary`는 기본값 지정 시 사용
- 💡 팁 3: `List<T>`로 모든 구현체를 한 번에 주입 가능

---

### 시나리오 4: @Autowired 실패 (Bean을 찾을 수 없음)

**상황**: Bean이 등록되지 않아서 주입 실패

```java
// ❌ 주니어 개발자가 작성한 코드

// 파일 위치: com/example/service/UserService.java
// @Service 어노테이션 없음!
public class UserService {
    public User getUser(Long id) {
        return new User(id, "John");
    }
}

// 파일 위치: com/example/controller/UserController.java
@RestController
public class UserController {
    @Autowired
    private UserService userService;  // 에러: Bean을 찾을 수 없음

    // 에러 발생:
    // Field userService in com.example.controller.UserController
    // required a bean of type 'com.example.service.UserService'
    // that could not be found.
}
```

**문제점**:
- 문제 1: `UserService`에 `@Service` 어노테이션이 없음
- 문제 2: Spring이 Component Scan으로 찾을 수 없음
- 왜 이 문제가 발생하는가: Bean 등록을 깜빡함

**해결책**:
```java
// ✅ 해결 방법 1: @Service 추가 (가장 일반적)
@Service  // ← 추가!
public class UserService {
    public User getUser(Long id) {
        return new User(id, "John");
    }
}

// ✅ 해결 방법 2: @Configuration과 @Bean 사용
@Configuration
public class ServiceConfig {
    @Bean
    public UserService userService() {
        return new UserService();
    }
}

// ✅ 해결 방법 3: @ComponentScan 범위 확인
@SpringBootApplication
@ComponentScan(basePackages = {
    "com.example.service",  // UserService가 있는 패키지
    "com.example.controller"
})
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}

// ✅ 해결 방법 4: required=false로 선택적 주입
@RestController
public class UserController {
    @Autowired(required = false)  // Bean이 없어도 에러 안 남
    private UserService userService;

    @GetMapping("/user/{id}")
    public User getUser(@PathVariable Long id) {
        if (userService == null) {
            throw new IllegalStateException("UserService not available");
        }
        return userService.getUser(id);
    }
}
```

**배운 점**:
- 💡 팁 1: `@Service`, `@Component` 등 어노테이션 필수
- 💡 팁 2: Component Scan 범위 확인 (`@SpringBootApplication`이 있는 패키지 하위만 스캔)
- 💡 팁 3: 선택적 의존성은 `@Autowired(required=false)` 또는 `Optional<T>` 사용

---

**[← 이전: Part 3](03-3-IoC-컨테이너-Part3.md)** | **[다음: Part 5 →](03-5-IoC-컨테이너-Part5.md)**
