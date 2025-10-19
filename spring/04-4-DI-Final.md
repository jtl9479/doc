# 04장: DI (Dependency Injection) - Part 4-8 (통합본)

**[← 이전: Part 3](04-3-DI-Part3.md)** | **[다음: 05장 Bean 생명주기 →](../05-Bean-생명주기.md)**

---

## 🏢 실무 활용 사례

### 실제 기업 활용 사례

#### 사례 1: 쿠팡 - 다중 물류센터 배송 시스템

```java
// 사용 목적: 전국 물류센터별 배송 전략을 유연하게 적용
// 규모: 30개 물류센터, 일 500만 건 배송
// 효과: 물류 전략 변경 시 코드 수정 없이 설정만 변경

// 배송 전략 인터페이스
public interface DeliveryStrategy {
    int calculateDeliveryTime(String from, String to);
    int calculateDeliveryCost(int distance);
}

// 수도권 당일배송
@Service
@Profile("seoul")
public class SeoulSameDayDelivery implements DeliveryStrategy {
    @Override
    public int calculateDeliveryTime(String from, String to) {
        return 3;  // 3시간
    }

    @Override
    public int calculateDeliveryCost(int distance) {
        return distance < 10 ? 0 : 2500;  // 10km 이내 무료
    }
}

// 지방 익일배송
@Service
@Profile("regional")
public class RegionalNextDayDelivery implements DeliveryStrategy {
    @Override
    public int calculateDeliveryTime(String from, String to) {
        return 24;  // 24시간
    }

    @Override
    public int calculateDeliveryCost(int distance) {
        return 3000;  // 고정 3,000원
    }
}

// 배송 서비스 (DI 활용)
@Service
@RequiredArgsConstructor
public class DeliveryService {
    private final DeliveryStrategy strategy;

    public DeliveryInfo calculateDelivery(Order order) {
        int time = strategy.calculateDeliveryTime(
            order.getWarehouse(),
            order.getDestination()
        );
        int cost = strategy.calculateDeliveryCost(order.getDistance());

        return new DeliveryInfo(time, cost);
    }
}

// application.properties 설정만으로 전략 변경
// spring.profiles.active=seoul  ← 수도권 물류센터
// spring.profiles.active=regional  ← 지방 물류센터

// 성과:
// - 물류 전략 추가 시간: 2주 → 1일 (DI로 새 전략만 추가)
// - 배송 시간 최적화: 지역별 맞춤 전략으로 만족도 25% 향상
// - 배송 비용 절감: 지역별 최적화로 월 5억원 절감
```

#### 사례 2: 토스 - A/B 테스트 시스템

```java
// 사용 목적: 신규 기능을 일부 사용자에게만 제공 (카나리 배포)
// 규모: 2000만 사용자, 동시 실험 50개
// 효과: 실험 설정 변경으로 위험 없이 신기능 테스트

// 이자 계산 인터페이스
public interface InterestCalculator {
    double calculateInterest(double principal, int days);
}

// 기존 이자 계산 (A 그룹)
@Service
@ConditionalOnProperty(name = "experiment.interest", havingValue = "v1")
public class LegacyInterestCalculator implements InterestCalculator {
    @Override
    public double calculateInterest(double principal, int days) {
        return principal * 0.02 * (days / 365.0);  // 연 2%
    }
}

// 신규 이자 계산 (B 그룹)
@Service
@ConditionalOnProperty(name = "experiment.interest", havingValue = "v2")
public class NewInterestCalculator implements InterestCalculator {
    @Override
    public double calculateInterest(double principal, int days) {
        // 일별 복리 계산
        return principal * Math.pow(1 + 0.022 / 365, days) - principal;  // 연 2.2%
    }
}

// 계좌 서비스
@Service
@RequiredArgsConstructor
public class AccountService {
    private final InterestCalculator calculator;

    public double getInterest(String accountId) {
        Account account = findAccount(accountId);
        return calculator.calculateInterest(
            account.getBalance(),
            account.getDaysSinceLastInterest()
        );
    }
}

// 사용자별로 다른 설정 적용 (동적 설정)
// A 그룹 서버: experiment.interest=v1
// B 그룹 서버: experiment.interest=v2

// 성과:
// - A/B 테스트 구축 시간: 1개월 → 1일
// - 실험 리스크: 전체 롤백 → 특정 그룹만 롤백
// - 전환율 측정: v2가 15% 더 높은 전환율 확인 후 전체 적용
```

#### 사례 3: 네이버 - 다국어 메시지 서비스

```java
// 사용 목적: 한국어, 영어, 일본어 등 다국어 지원
// 규모: 20개 언어, 10만 개 메시지
// 효과: 언어 추가 시 기존 코드 수정 없음

// 메시지 서비스 인터페이스
public interface MessageService {
    String getMessage(String key);
}

// 한국어 메시지
@Service("koMessageService")
public class KoreanMessageService implements MessageService {
    @Override
    public String getMessage(String key) {
        Map<String, String> messages = Map.of(
            "welcome", "환영합니다",
            "goodbye", "안녕히 가세요",
            "error", "오류가 발생했습니다"
        );
        return messages.getOrDefault(key, key);
    }
}

// 영어 메시지
@Service("enMessageService")
public class EnglishMessageService implements MessageService {
    @Override
    public String getMessage(String key) {
        Map<String, String> messages = Map.of(
            "welcome", "Welcome",
            "goodbye", "Goodbye",
            "error", "An error occurred"
        );
        return messages.getOrDefault(key, key);
    }
}

// 사용자 서비스
@Service
public class UserService {
    private final Map<String, MessageService> messageServices;

    // Map으로 모든 MessageService Bean 주입
    @Autowired
    public UserService(Map<String, MessageService> messageServices) {
        this.messageServices = messageServices;
    }

    public String greetUser(String userId, String language) {
        // 사용자 언어에 따라 동적으로 MessageService 선택
        String beanName = language + "MessageService";  // "koMessageService"
        MessageService service = messageServices.get(beanName);

        if (service == null) {
            service = messageServices.get("enMessageService");  // 기본 영어
        }

        return service.getMessage("welcome");
    }
}

// 성과:
// - 다국어 추가 시간: 2주 → 1일 (새 MessageService만 추가)
// - 코드 중복: 80% 감소
// - 글로벌 서비스 확장: 6개월 만에 20개국 지원
```

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: 순환 참조 에러 발생

**상황**: UserService와 OrderService가 서로를 참조하다 애플리케이션 실패

```java
// ❌ 주니어 개발자가 작성한 코드

@Service
public class UserService {
    @Autowired
    private OrderService orderService;  // UserService → OrderService

    public List<Order> getUserOrders(String userId) {
        return orderService.findByUserId(userId);
    }
}

@Service
public class OrderService {
    @Autowired
    private UserService userService;  // OrderService → UserService (순환!)

    public User getOrderOwner(String orderId) {
        Order order = findOrder(orderId);
        return userService.findById(order.getUserId());
    }
}

// 에러:
// The dependencies of some of the beans form a cycle:
// ┌─────┐
// |  userService
// ↑     ↓
// |  orderService
// └─────┘
```

**해결책 1: @Lazy 사용 (임시)**:
```java
@Service
public class UserService {
    private final OrderService orderService;

    @Autowired
    public UserService(@Lazy OrderService orderService) {
        this.orderService = orderService;  // Proxy 주입
    }
}
```

**해결책 2: 설계 개선 (권장)**:
```java
// OrderQueryService로 분리
@Service
@RequiredArgsConstructor
public class OrderQueryService {
    private final UserService userService;
    private final OrderService orderService;

    public OrderWithUserDto getOrderWithUser(String orderId) {
        Order order = orderService.findOrder(orderId);
        User user = userService.findById(order.getUserId());
        return new OrderWithUserDto(order, user);
    }
}
```

**배운 점**:
- 💡 순환 참조는 설계 문제의 신호
- 💡 공통 로직을 별도 서비스로 추출
- 💡 단방향 의존성 유지

---

### 시나리오 2: @Qualifier 이름 오타

**상황**: Bean 이름을 잘못 입력해서 주입 실패

```java
// ❌ 주니어 개발자가 작성한 코드

@Component("emailService")  // "emailService"로 등록
public class EmailService implements NotificationService { }

@Service
public class UserService {
    @Autowired
    @Qualifier("emailservice")  // 소문자 오타!
    private NotificationService notificationService;

    // 에러:
    // No qualifying bean of type 'NotificationService' available:
    // expected at least 1 bean which qualifies as autowire candidate.
}
```

**해결책 1: 이름 정확히 수정**:
```java
@Qualifier("emailService")  // 대소문자 일치
```

**해결책 2: 상수로 관리 (권장)**:
```java
// BeanNames.java
public class BeanNames {
    public static final String EMAIL_SERVICE = "emailService";
    public static final String SMS_SERVICE = "smsService";
}

// 사용
@Qualifier(BeanNames.EMAIL_SERVICE)  // 타입 안전
```

**배운 점**:
- 💡 Magic String 대신 상수 사용
- 💡 IDE 자동완성 활용
- 💡 컴파일 타임 체크 가능

---

### 시나리오 3: 테스트에서 Mock 주입 실패

**상황**: 필드 주입으로 인해 테스트가 어려움

```java
// ❌ 주니어 개발자가 작성한 코드

@Service
public class OrderService {
    @Autowired
    private PaymentService paymentService;  // 필드 주입

    public void createOrder(Order order) {
        paymentService.processPayment(order.getAmount());
    }
}

// 테스트
class OrderServiceTest {
    @Test
    void testCreateOrder() {
        // 문제: new로 생성 시 paymentService가 null
        OrderService service = new OrderService();
        service.createOrder(new Order());  // NullPointerException!
    }
}
```

**해결책: 생성자 주입으로 변경**:
```java
// ✅ 올바른 코드

@Service
@RequiredArgsConstructor
public class OrderService {
    private final PaymentService paymentService;  // 생성자 주입

    public void createOrder(Order order) {
        paymentService.processPayment(order.getAmount());
    }
}

// 테스트
class OrderServiceTest {
    @Test
    void testCreateOrder() {
        // Mock 객체 생성
        PaymentService mockPayment = mock(PaymentService.class);

        // 생성자로 주입 (쉬움!)
        OrderService service = new OrderService(mockPayment);

        // 테스트 실행
        service.createOrder(new Order(1000));

        // 검증
        verify(mockPayment).processPayment(1000);
    }
}
```

**배운 점**:
- 💡 생성자 주입이 테스트에 유리
- 💡 Spring 없이도 테스트 가능
- 💡 Mock 주입이 간편

---

## ❓ FAQ

<details>
<summary><strong>Q1: 생성자 주입, Setter 주입, 필드 주입 중 어떤 것을 써야 하나요?</strong></summary>

**A**: **생성자 주입**을 기본으로 사용하세요. (Spring 공식 권장)

**상세 비교**:

| 항목 | 생성자 주입 | Setter 주입 | 필드 주입 |
|------|-----------|-----------|----------|
| final 사용 | ✅ 가능 | ❌ 불가 | ❌ 불가 |
| 불변성 | ✅ 보장 | ❌ 변경 가능 | ❌ 변경 가능 |
| 테스트 | ✅ 쉬움 | ⚠️ 보통 | ❌ 어려움 |
| 순환 참조 | ✅ 조기 발견 | ⚠️ 늦게 발견 | ❌ 늦게 발견 |
| 선택적 의존성 | ⚠️ 복잡 | ✅ 쉬움 | ⚠️ required=false |
| 권장도 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |

**사용 가이드**:
- **필수 의존성**: 생성자 주입
- **선택적 의존성**: Setter 주입
- **필드 주입**: 사용 지양 (테스트, 레거시 코드만)

</details>

<details>
<summary><strong>Q2: @Autowired를 생략할 수 있나요?</strong></summary>

**A**: Spring 4.3부터 생성자가 1개면 `@Autowired` 생략 가능합니다.

**예시**:
```java
@Service
public class UserService {
    private final UserRepository repository;

    // @Autowired 생략 가능 (생성자 1개)
    public UserService(UserRepository repository) {
        this.repository = repository;
    }
}

// Lombok 사용 시
@Service
@RequiredArgsConstructor  // 생성자 자동 생성, @Autowired 불필요
public class UserService {
    private final UserRepository repository;
}
```

**생략 불가능한 경우**:
- 생성자가 2개 이상
- Setter 주입
- 필드 주입

</details>

<details>
<summary><strong>Q3: @Qualifier와 @Primary의 차이는 무엇인가요?</strong></summary>

**A**: `@Qualifier`는 명시적 선택, `@Primary`는 기본값 지정입니다.

**@Primary (기본값)**:
```java
@Service
@Primary  // 기본 구현체
public class TossPayment implements PaymentGateway { }

@Service
public class NaverPayment implements PaymentGateway { }

// 사용
@Service
public class OrderService {
    @Autowired
    PaymentGateway gateway;  // TossPayment 주입 (Primary)
}
```

**@Qualifier (명시적)**:
```java
@Service
@Qualifier("toss")
public class TossPayment implements PaymentGateway { }

@Service
@Qualifier("naver")
public class NaverPayment implements PaymentGateway { }

// 사용
@Service
public class OrderService {
    @Autowired
    @Qualifier("naver")  // 명시적으로 NaverPayment 선택
    PaymentGateway gateway;
}
```

**우선순위**: @Qualifier > @Primary > Bean 이름

</details>

<details>
<summary><strong>Q4: List로 모든 구현체를 주입받을 수 있나요?</strong></summary>

**A**: 네, `List<인터페이스>`로 모든 구현체를 주입받을 수 있습니다.

**예시**:
```java
public interface PaymentGateway {
    void pay(int amount);
}

@Service
public class TossPayment implements PaymentGateway { }

@Service
public class NaverPayment implements PaymentGateway { }

@Service
@RequiredArgsConstructor
public class PaymentAggregator {
    private final List<PaymentGateway> gateways;  // 2개 모두 주입

    public void showAll() {
        gateways.forEach(g -> System.out.println(g.getClass().getSimpleName()));
        // 출력: TossPayment, NaverPayment
    }
}
```

**Map으로도 가능**:
```java
@RequiredArgsConstructor
public class PaymentAggregator {
    private final Map<String, PaymentGateway> gateways;
    // Key: Bean 이름, Value: Bean 인스턴스
}
```

</details>

<details>
<summary><strong>Q5: 순환 참조는 왜 발생하고 어떻게 해결하나요?</strong></summary>

**A**: A가 B를 의존하고, B가 A를 의존할 때 발생합니다.

**발생 원인**: 잘못된 설계 (책임 분리 미흡)

**해결 방법**:

1. **@Lazy로 지연 로딩** (임시):
```java
@Service
public class A {
    @Lazy  // Proxy 주입
    @Autowired
    B b;
}
```

2. **Setter 주입** (비권장):
```java
@Service
public class A {
    private B b;

    @Autowired
    public void setB(B b) {
        this.b = b;
    }
}
```

3. **설계 개선** (가장 권장):
```java
// 공통 로직을 별도 서비스로 분리
@Service
public class CommonService {
    @Autowired A a;
    @Autowired B b;

    public void doSomething() {
        a.methodA();
        b.methodB();
    }
}
```

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. DI(Dependency Injection)가 무엇인지 설명해주세요</strong></summary>

**모범 답안**:
> "DI는 의존성 주입으로, 객체가 필요로 하는 의존 객체를 외부에서 주입하는 것을 의미합니다. 직접 new 키워드로 생성하지 않고, Spring이 자동으로 필요한 객체를 찾아서 주입해줍니다. 이를 통해 결합도를 낮추고, 테스트 용이성과 코드 재사용성을 높일 수 있습니다."

**예시 답변**:
```java
// DI 없이
public class OrderService {
    private PaymentService payment = new PaymentService();  // 강한 결합
}

// DI 사용
@Service
public class OrderService {
    private final PaymentService payment;

    @Autowired  // Spring이 자동 주입
    public OrderService(PaymentService payment) {
        this.payment = payment;
    }
}
```

</details>

<details>
<summary><strong>2. 생성자 주입을 권장하는 이유는 무엇인가요?</strong></summary>

**모범 답변**:
> "생성자 주입을 권장하는 이유는 세 가지입니다. 첫째, final 키워드로 불변성을 보장할 수 있어 NPE를 방지합니다. 둘째, 순환 참조가 있으면 애플리케이션 시작 시점에 에러가 발생하여 조기에 발견할 수 있습니다. 셋째, 테스트 시 new 키워드로 직접 객체를 생성할 수 있어 Spring 컨테이너 없이도 테스트할 수 있습니다."

</details>

<details>
<summary><strong>3. @Autowired는 어떻게 동작하나요?</strong></summary>

**모범 답변**:
> "@Autowired는 Spring이 자동으로 의존성을 주입하도록 하는 어노테이션입니다. 타입(Type) 기반으로 IoC 컨테이너에서 일치하는 Bean을 찾아 주입합니다. 같은 타입의 Bean이 여러 개면 @Qualifier로 특정 Bean을 선택하거나, @Primary로 기본 Bean을 지정할 수 있습니다."

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. 의존성 주입의 3가지 방식을 비교하고, 각각의 사용 시나리오를 설명해주세요</strong></summary>

**모범 답안**:
> "의존성 주입은 생성자 주입, Setter 주입, 필드 주입 3가지가 있습니다. 생성자 주입은 final로 불변성을 보장하고 테스트가 쉬워서 필수 의존성에 사용합니다. Setter 주입은 선택적 의존성에 사용하며, 런타임에 의존성을 변경할 수 있습니다. 필드 주입은 코드가 간결하지만 테스트가 어렵고 불변성을 보장할 수 없어 사용을 지양합니다."

**실무 경험**:
> "실제 프로젝트에서 필수 의존성은 모두 생성자 주입으로, 선택적 기능(이메일 알림 등)은 Setter 주입으로 처리했습니다. Lombok의 @RequiredArgsConstructor로 보일러플레이트 코드를 제거하여 코드 가독성을 높였습니다."

</details>

<details>
<summary><strong>2. 순환 참조 문제를 해결하는 방법과 근본적인 해결책을 설명해주세요</strong></summary>

**모범 답안**:
> "순환 참조는 @Lazy로 지연 로딩하거나 Setter 주입으로 전환하여 해결할 수 있지만, 이는 임시 방편입니다. 근본적인 해결책은 설계를 개선하는 것입니다. 공통 로직을 별도 서비스로 추출하거나, 이벤트 기반으로 의존성을 제거하는 방법이 있습니다. 순환 참조는 대부분 책임 분리가 명확하지 않은 설계 문제의 신호입니다."

</details>

---

## 📝 핵심 정리

### 이 장에서 배운 핵심 개념

| 개념 | 설명 | 핵심 키워드 |
|------|------|-------------|
| DI | 의존성을 외부에서 주입 | Dependency Injection, @Autowired |
| 생성자 주입 | 생성자로 의존성 주입 (권장) | final, 불변성, 테스트 용이 |
| @Qualifier | 특정 Bean 선택 | 명시적 선택, 타입 안전 |
| @Primary | 기본 Bean 지정 | 기본값, 우선순위 |
| List 주입 | 모든 구현체 주입 | Strategy 패턴, 다형성 |

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] **생성자 주입 사용**: final + 불변성
- [ ] **Lombok 활용**: @RequiredArgsConstructor
- [ ] **인터페이스 기반 설계**: 구현체 교체 용이
- [ ] **@Qualifier 상수화**: Magic String 제거
- [ ] **테스트 코드 작성**: Mock 주입 검증

#### ❌ 하지 말아야 할 것
- [ ] **필드 주입**: 테스트 어려움
- [ ] **순환 참조 방치**: 설계 개선 필요
- [ ] **Magic String**: @Qualifier("문자열")
- [ ] **new로 생성**: DI 장점 상실

---

## 🚀 다음 단계

### 다음 장 미리보기: 05장 Bean 생명주기
- **배울 내용 1**: Bean 생성 → 초기화 → 소멸 과정
- **배울 내용 2**: @PostConstruct, @PreDestroy 활용
- **배울 내용 3**: BeanPostProcessor로 Bean 가공

---

## 🎉 축하합니다!

**이제 여러분은**:
- ✅ DI의 3가지 방식을 이해하고 적절히 선택할 수 있습니다
- ✅ 생성자 주입으로 안전한 코드를 작성할 수 있습니다
- ✅ @Qualifier, @Primary로 Bean을 선택할 수 있습니다
- ✅ 실무에서 DI를 활용한 유연한 설계를 할 수 있습니다

**다음 단계**:
- [ ] 05장: Bean 생명주기로 진행
- [ ] 실전 프로젝트에 DI 적용해보기
- [ ] 면접 질문을 스스로 답변해보기

---

**[← 이전: Part 3](04-3-DI-Part3.md)** | **[다음: 05장 Bean 생명주기 →](../05-Bean-생명주기.md)**

**목차로 돌아가기**: [📚 Spring 전체 목차](../README.md)
