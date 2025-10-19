# 04장: DI (Dependency Injection) - Part 2 (핵심 개념)

**[← 이전: Part 1](04-1-DI-Part1.md)** | **[다음: Part 3 →](04-3-DI-Part3.md)**

---

## 📖 핵심 개념

### 개념 설명 (3단계 깊이)

#### 1️⃣ 초보자 수준 설명

**초등학생도 이해할 수 있는 쉬운 언어**

```
DI (Dependency Injection) = 의존성 주입이란?

비유: 학교 준비물

DI 없이 (직접 준비):
- 수업마다 필요한 준비물을 혼자 직접 구매
- 크레파스 필요 → 문구점 가서 구매
- 자 필요 → 또 문구점 가서 구매
- 매번 직접 챙겨야 함

DI 사용 (엄마가 준비):
- 엄마에게 "내일 미술 시간이야" 라고 말함
- 엄마가 필요한 준비물 알아서 챙겨줌
- 나는 가방에서 꺼내 쓰기만 하면 됨

프로그래밍으로:
의존성 = 내가 필요한 것 (크레파스, 자 등)
주입 = 누군가 알아서 챙겨줌 (엄마, Spring)
```

**코드로 이해하기**:
```java
// DI 없이: 직접 준비
class 학생 {
    void 미술수업() {
        크레파스 crayon = new 크레파스();  // 직접 구매
        자 ruler = new 자();                // 직접 구매
        // 그림 그리기
    }
}

// DI 사용: 엄마가 준비 (Spring이 주입)
class 학생 {
    크레파스 crayon;  // 엄마가 준비
    자 ruler;        // 엄마가 준비

    // Spring(엄마)이 필요한 것을 알아서 챙겨줌
    학생(크레파스 crayon, 자 ruler) {
        this.crayon = crayon;
        this.ruler = ruler;
    }

    void 미술수업() {
        // 그냥 쓰기만 하면 됨!
    }
}
```

#### 2️⃣ 중급자 수준 설명

**기술적 용어 추가, 동작 원리 설명**

```
DI (Dependency Injection) = 의존성 주입

의존성(Dependency):
- A 클래스가 B 클래스를 사용하면, "A는 B에 의존한다"
- OrderService가 PaymentService를 사용 → 의존성

주입(Injection):
- 외부에서 의존 객체를 전달하는 것
- new로 직접 생성하지 않고, 외부에서 받음

의존성 주입의 3가지 방법:
1. 생성자 주입 (Constructor Injection)
2. Setter 주입 (Setter Injection)
3. 필드 주입 (Field Injection)
```

**의존성 주입 흐름**:
```java
// 1. 의존성 정의
public interface PaymentService {
    void pay(int amount);
}

// 2. 구현체
@Service
public class CardPaymentService implements PaymentService {
    public void pay(int amount) {
        System.out.println("카드 결제: " + amount);
    }
}

// 3. 의존성 주입 (생성자)
@Service
public class OrderService {
    private final PaymentService paymentService;

    // Spring이 CardPaymentService를 찾아서 주입
    @Autowired
    public OrderService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }

    public void order(int amount) {
        paymentService.pay(amount);
    }
}
```

**Spring이 하는 일**:
```
1. @Service가 붙은 클래스 스캔
   → CardPaymentService 발견
   → Bean으로 등록

2. OrderService 생성 시도
   → 생성자에 PaymentService 필요
   → IoC 컨테이너에서 PaymentService 타입 검색
   → CardPaymentService 찾음
   → 주입!

3. OrderService Bean 생성 완료
```

#### 3️⃣ 고급자 수준 설명

**내부 구조, 최적화, 고급 패턴**

**의존성 주입의 내부 동작 (Reflection)**:

```java
// Spring이 내부적으로 하는 일 (간소화된 버전)

public class SimpleDIContainer {
    private Map<Class<?>, Object> beans = new ConcurrentHashMap<>();

    public <T> T getBean(Class<T> clazz) {
        // 1. 이미 생성된 Bean 확인
        if (beans.containsKey(clazz)) {
            return (T) beans.get(clazz);
        }

        // 2. Bean 생성
        try {
            // 3. 생성자 찾기
            Constructor<?>[] constructors = clazz.getDeclaredConstructors();
            Constructor<?> constructor = constructors[0];

            // 4. 생성자 파라미터 타입 확인
            Class<?>[] paramTypes = constructor.getParameterTypes();

            // 5. 파라미터로 필요한 Bean들을 재귀적으로 생성
            Object[] params = new Object[paramTypes.length];
            for (int i = 0; i < paramTypes.length; i++) {
                params[i] = getBean(paramTypes[i]);
            }

            // 6. 생성자로 인스턴스 생성
            T instance = (T) constructor.newInstance(params);

            // 7. Bean 저장
            beans.put(clazz, instance);

            return instance;
        } catch (Exception e) {
            throw new RuntimeException("Bean 생성 실패", e);
        }
    }
}
```

**3가지 주입 방식의 내부 메커니즘**:

```java
// 1. 생성자 주입 (권장)
@Service
public class UserService {
    private final UserRepository userRepository;

    // Spring이 내부적으로:
    // 1. UserService 클래스의 생성자 스캔
    // 2. 생성자 파라미터 타입(UserRepository) 확인
    // 3. IoC 컨테이너에서 UserRepository Bean 검색
    // 4. 생성자 호출: new UserService(userRepository)
    @Autowired
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
}

// 내부 동작:
Constructor<?> constructor = UserService.class.getConstructor(UserRepository.class);
UserRepository repo = container.getBean(UserRepository.class);
UserService service = (UserService) constructor.newInstance(repo);
```

```java
// 2. Setter 주입
@Service
public class OrderService {
    private PaymentService paymentService;

    // Spring이 내부적으로:
    // 1. 기본 생성자로 OrderService 생성
    // 2. @Autowired 붙은 Setter 메서드 찾기
    // 3. PaymentService Bean 검색
    // 4. Setter 호출: setPaymentService(paymentService)
    @Autowired
    public void setPaymentService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }
}

// 내부 동작:
OrderService service = new OrderService();  // 기본 생성자
Method setter = OrderService.class.getMethod("setPaymentService", PaymentService.class);
PaymentService payment = container.getBean(PaymentService.class);
setter.invoke(service, payment);
```

```java
// 3. 필드 주입
@Service
public class ProductService {
    // Spring이 내부적으로:
    // 1. 기본 생성자로 ProductService 생성
    // 2. @Autowired 붙은 필드 찾기
    // 3. Field.setAccessible(true)로 private 접근 허용
    // 4. ProductRepository Bean 검색
    // 5. Field.set()으로 값 주입
    @Autowired
    private ProductRepository productRepository;
}

// 내부 동작:
ProductService service = new ProductService();
Field field = ProductService.class.getDeclaredField("productRepository");
field.setAccessible(true);  // private 필드 접근 허용
ProductRepository repo = container.getBean(ProductRepository.class);
field.set(service, repo);
```

**의존성 해결 전략 (Dependency Resolution)**:

```java
// 1. 타입으로 매칭
public interface MessageService { }

@Service
public class EmailService implements MessageService { }

@Service
public class NotificationService {
    @Autowired
    MessageService messageService;  // EmailService 주입됨
}

// 2. 같은 타입이 2개 이상일 때
@Service("emailService")
public class EmailService implements MessageService { }

@Service("smsService")
public class SmsService implements MessageService { }

@Service
public class NotificationService {
    // 방법 1: @Qualifier로 지정
    @Autowired
    @Qualifier("emailService")
    MessageService messageService;

    // 방법 2: 필드명으로 매칭
    @Autowired
    MessageService emailService;  // 이름이 같으면 자동 매칭

    // 방법 3: @Primary 사용
    // EmailService에 @Primary 추가
}

// 3. Optional 의존성
@Service
public class ReportService {
    @Autowired(required = false)  // Bean이 없어도 에러 안 남
    EmailService emailService;

    // 또는 Optional 사용
    @Autowired
    Optional<EmailService> optionalEmail;
}
```

**순환 참조 해결 메커니즘**:

```java
// 순환 참조 문제
@Service
public class A {
    @Autowired B b;  // A → B
}

@Service
public class B {
    @Autowired A a;  // B → A (순환!)
}

// Spring의 해결 방법 (3-Level Cache)

// Level 1: Singleton Objects (완전히 초기화된 Bean)
Map<String, Object> singletonObjects;

// Level 2: Early Singleton Objects (초기화 중인 Bean)
Map<String, Object> earlySingletonObjects;

// Level 3: Singleton Factories (Bean Factory)
Map<String, ObjectFactory<?>> singletonFactories;

// 순환 참조 해결 과정:
1. A 생성 시작
2. A를 earlySingletonObjects에 저장 (미완성 상태)
3. A의 의존성 B 주입 시도
4. B 생성 시작
5. B의 의존성 A 주입 시도
6. earlySingletonObjects에서 A를 찾아 주입 (미완성이지만 주입 가능)
7. B 생성 완료
8. A에 B 주입
9. A 생성 완료

// @Lazy로 해결
@Service
public class A {
    @Lazy  // Proxy 객체 주입, 실제 사용 시점에 Bean 생성
    @Autowired B b;
}
```

---

### 주요 용어 정리

| 용어 | 영문 | 설명 | 예시 |
|------|------|------|------|
| 의존성 | Dependency | 한 클래스가 다른 클래스를 사용하는 관계 | OrderService → PaymentService |
| 주입 | Injection | 의존 객체를 외부에서 전달 | @Autowired로 자동 주입 |
| 생성자 주입 | Constructor Injection | 생성자를 통한 의존성 주입 | `public A(B b)` |
| Setter 주입 | Setter Injection | Setter 메서드를 통한 주입 | `setB(B b)` |
| 필드 주입 | Field Injection | 필드에 직접 주입 | `@Autowired B b;` |
| 결합도 | Coupling | 클래스 간 의존 정도 | 낮을수록 좋음 |
| 인터페이스 | Interface | 구현체의 계약 | `PaymentService` |
| 구현체 | Implementation | 인터페이스의 실제 구현 | `CardPaymentService` |

---

### 기술 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│             Dependency Injection 동작 과정                  │
│                                                             │
│  1️⃣ Component Scan Phase                                   │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ @ComponentScan이 패키지 스캔                          │ │
│  │      ↓                                                │ │
│  │ @Service, @Repository 클래스 발견                     │ │
│  │      ↓                                                │ │
│  │ BeanDefinition 생성                                   │ │
│  └───────────────────────────────────────────────────────┘ │
│                          ↓                                  │
│  2️⃣ Bean Creation Phase                                    │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Bean 생성 순서 결정 (의존성 그래프 분석)             │ │
│  │      ↓                                                │ │
│  │ 의존성 없는 Bean부터 생성                             │ │
│  │      ↓                                                │ │
│  │ Reflection으로 생성자/Setter/필드 분석                │ │
│  └───────────────────────────────────────────────────────┘ │
│                          ↓                                  │
│  3️⃣ Dependency Resolution Phase                            │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 필요한 의존성 타입 확인                               │ │
│  │      ↓                                                │ │
│  │ IoC 컨테이너에서 해당 타입 Bean 검색                 │ │
│  │      ↓                                                │ │
│  │ @Qualifier, @Primary로 우선순위 결정                  │ │
│  │      ↓                                                │ │
│  │ Bean 주입 (생성자/Setter/필드)                        │ │
│  └───────────────────────────────────────────────────────┘ │
│                          ↓                                  │
│  4️⃣ Initialization Phase                                   │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ @PostConstruct 실행                                   │ │
│  │      ↓                                                │ │
│  │ Bean 사용 가능 상태                                   │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

의존성 그래프 예시:

    OrderService
        ↓
    ┌───┴───┐
    ↓       ↓
PaymentSvc ProductSvc
    ↓       ↓
PaymentRepo ProductRepo

생성 순서:
1. PaymentRepo (의존성 없음)
2. ProductRepo (의존성 없음)
3. PaymentService (PaymentRepo 의존)
4. ProductService (ProductRepo 의존)
5. OrderService (PaymentService, ProductService 의존)
```

**3가지 주입 방식 비교**:

```
┌──────────────────────────────────────────────────────────┐
│          생성자 주입 (Constructor Injection)             │
│                                                          │
│  @Service                                                │
│  public class OrderService {                             │
│      private final PaymentService payment;  // final!    │
│                                                          │
│      @Autowired                                          │
│      public OrderService(PaymentService payment) {       │
│          this.payment = payment;                         │
│      }                                                   │
│  }                                                       │
│                                                          │
│  ✅ 장점: 불변성, 순환참조 조기발견, 테스트 용이         │
│  ❌ 단점: 선택적 의존성 처리 복잡                        │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│          Setter 주입 (Setter Injection)                  │
│                                                          │
│  @Service                                                │
│  public class ReportService {                            │
│      private EmailService email;                         │
│                                                          │
│      @Autowired(required = false)  // 선택적            │
│      public void setEmailService(EmailService email) {   │
│          this.email = email;                             │
│      }                                                   │
│  }                                                       │
│                                                          │
│  ✅ 장점: 선택적 의존성 처리 편리                        │
│  ❌ 단점: 불변성 없음, 순환참조 늦게 발견                │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│          필드 주입 (Field Injection)                     │
│                                                          │
│  @Service                                                │
│  public class UserService {                              │
│      @Autowired                                          │
│      private UserRepository repo;  // 간결!              │
│  }                                                       │
│                                                          │
│  ✅ 장점: 코드 간결                                      │
│  ❌ 단점: 테스트 어려움, final 불가, 순환참조 늦게발견   │
└──────────────────────────────────────────────────────────┘

권장 우선순위:
1순위: 생성자 주입 (필수 의존성)
2순위: Setter 주입 (선택적 의존성)
3순위: 필드 주입 (사용 지양)
```

---

**[← 이전: Part 1](04-1-DI-Part1.md)** | **[다음: Part 3 →](04-3-DI-Part3.md)**
