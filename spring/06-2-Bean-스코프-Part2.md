# 06장: Bean 스코프 - Part 2 (실습 & 실무 & FAQ & 면접)

**[← 이전: Part 1](06-1-Bean-스코프-Part1.md)** | **[목차로 돌아가기](../README.md)**

---

## 💻 기본 실습

### 실습 1: Singleton vs Prototype 비교

**난이도**: ⭐⭐☆☆☆

```java
// SingletonBean.java
@Component
// @Scope("singleton") - 기본값이므로 생략 가능
public class SingletonBean {
    private int count = 0;

    public void increment() {
        count++;
    }

    public int getCount() {
        return count;
    }
}

// PrototypeBean.java
@Component
@Scope("prototype")
public class PrototypeBean {
    private int count = 0;

    public void increment() {
        count++;
    }

    public int getCount() {
        return count;
    }
}

// TestController.java
@RestController
public class ScopeTestController {

    @Autowired
    private ApplicationContext context;

    @Autowired
    private SingletonBean singletonBean;

    @GetMapping("/test-singleton")
    public String testSingleton() {
        SingletonBean bean1 = context.getBean(SingletonBean.class);
        SingletonBean bean2 = context.getBean(SingletonBean.class);

        bean1.increment();
        bean1.increment();

        return String.format(
            "bean1 count: %d, bean2 count: %d, same instance: %b",
            bean1.getCount(),  // 2
            bean2.getCount(),  // 2 (같은 인스턴스!)
            bean1 == bean2     // true
        );
    }

    @GetMapping("/test-prototype")
    public String testPrototype() {
        PrototypeBean bean1 = context.getBean(PrototypeBean.class);
        PrototypeBean bean2 = context.getBean(PrototypeBean.class);

        bean1.increment();
        bean1.increment();

        return String.format(
            "bean1 count: %d, bean2 count: %d, same instance: %b",
            bean1.getCount(),  // 2
            bean2.getCount(),  // 0 (다른 인스턴스!)
            bean1 == bean2     // false
        );
    }
}
```

**실행 결과**:
```
GET /test-singleton
→ bean1 count: 2, bean2 count: 2, same instance: true

GET /test-prototype
→ bean1 count: 2, bean2 count: 0, same instance: false
```

---

### 실습 2: Request Scope (웹 전용)

**난이도**: ⭐⭐⭐☆☆

```java
// RequestScopedBean.java
@Component
@Scope(value = "request", proxyMode = ScopedProxyMode.TARGET_CLASS)
public class RequestScopedBean {
    private String requestId;
    private LocalDateTime createdAt;

    @PostConstruct
    public void init() {
        this.requestId = UUID.randomUUID().toString();
        this.createdAt = LocalDateTime.now();
        System.out.println("✅ Request Bean 생성: " + requestId);
    }

    @PreDestroy
    public void destroy() {
        System.out.println("🗑️ Request Bean 소멸: " + requestId);
    }

    public String getRequestId() {
        return requestId;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
}

// RequestController.java
@RestController
public class RequestController {

    @Autowired
    private RequestScopedBean requestBean;  // Proxy 주입

    @GetMapping("/request-test")
    public Map<String, String> testRequest() {
        return Map.of(
            "requestId", requestBean.getRequestId(),
            "createdAt", requestBean.getCreatedAt().toString()
        );
    }
}
```

**테스트**:
```bash
# 요청 1
curl http://localhost:8080/request-test
# 출력: ✅ Request Bean 생성: abc-123
# 응답: {"requestId":"abc-123","createdAt":"2024-01-15T10:00:00"}
# 출력: 🗑️ Request Bean 소멸: abc-123

# 요청 2 (다른 ID)
curl http://localhost:8080/request-test
# 출력: ✅ Request Bean 생성: xyz-456
# 응답: {"requestId":"xyz-456","createdAt":"2024-01-15T10:00:05"}
# 출력: 🗑️ Request Bean 소멸: xyz-456
```

---

### 실습 3: Session Scope - 장바구니 구현

**난이도**: ⭐⭐⭐⭐☆

```java
// Item.java
@Data
@AllArgsConstructor
public class Item {
    private String name;
    private int price;
}

// ShoppingCart.java (Session-scoped)
@Component
@Scope(value = "session", proxyMode = ScopedProxyMode.TARGET_CLASS)
public class ShoppingCart {
    private List<Item> items = new ArrayList<>();
    private String sessionId;

    @PostConstruct
    public void init() {
        this.sessionId = UUID.randomUUID().toString();
        System.out.println("🛒 장바구니 생성: " + sessionId);
    }

    public void addItem(Item item) {
        items.add(item);
        System.out.println("📦 상품 추가: " + item.getName() + " (세션: " + sessionId + ")");
    }

    public List<Item> getItems() {
        return items;
    }

    public int getTotalPrice() {
        return items.stream().mapToInt(Item::getPrice).sum();
    }

    @PreDestroy
    public void destroy() {
        System.out.println("🗑️ 장바구니 정리: " + sessionId);
    }
}

// CartController.java
@RestController
@RequestMapping("/cart")
public class CartController {

    @Autowired
    private ShoppingCart cart;  // Session-scoped (Proxy)

    @PostMapping("/add")
    public ResponseEntity<String> addItem(@RequestParam String name,
                                          @RequestParam int price) {
        cart.addItem(new Item(name, price));
        return ResponseEntity.ok("상품 추가 완료");
    }

    @GetMapping
    public ResponseEntity<Map<String, Object>> getCart() {
        return ResponseEntity.ok(Map.of(
            "items", cart.getItems(),
            "total", cart.getTotalPrice()
        ));
    }
}
```

**테스트 (브라우저 2개)**:
```bash
# 브라우저 1 (세션 A)
POST /cart/add?name=MacBook&price=2500000
# 출력: 🛒 장바구니 생성: session-aaa
# 출력: 📦 상품 추가: MacBook (세션: session-aaa)

GET /cart
# 응답: {"items":[{"name":"MacBook","price":2500000}],"total":2500000}

# 브라우저 2 (세션 B - 다른 장바구니!)
POST /cart/add?name=iPhone&price=1500000
# 출력: 🛒 장바구니 생성: session-bbb
# 출력: 📦 상품 추가: iPhone (세션: session-bbb)

GET /cart
# 응답: {"items":[{"name":"iPhone","price":1500000}],"total":1500000}
```

---

## 🏢 실무 활용 사례

### 사례 1: 네이버 쇼핑 - 장바구니 (Session Scope)

```java
// 사용 목적: 사용자별 장바구니 독립 관리
// 규모: 월 5000만 사용자, 동시 접속 100만
// 효과: 사용자 간 데이터 격리, 안전한 상태 관리

@Component
@Scope(value = "session", proxyMode = ScopedProxyMode.TARGET_CLASS)
public class NaverShoppingCart implements Serializable {

    private List<CartItem> items = new ArrayList<>();
    private String userId;

    @PostConstruct
    public void init() {
        // 세션 생성 시 로그
        log.info("장바구니 생성: userId={}", userId);
    }

    public void addItem(CartItem item) {
        // 동일 상품이면 수량 증가
        Optional<CartItem> existing = items.stream()
            .filter(i -> i.getProductId().equals(item.getProductId()))
            .findFirst();

        if (existing.isPresent()) {
            existing.get().increaseQuantity(item.getQuantity());
        } else {
            items.add(item);
        }

        // 실시간으로 Redis에 백업 (세션 공유용)
        saveToRedis();
    }

    @PreDestroy
    public void destroy() {
        // 세션 종료 시 최종 백업
        saveToRedis();
        log.info("장바구니 정리: userId={}", userId);
    }

    private void saveToRedis() {
        // Redis에 저장 (서버 재시작 시에도 유지)
    }
}

// 성과:
// - 사용자 간 장바구니 혼선: 제로
// - 세션 공유로 여러 서버에서 동일한 장바구니 접근
// - 전환율 15% 향상 (장바구니 유지율 증가)
```

### 사례 2: 토스 - 결제 트랜잭션 (Request Scope)

```java
// 사용 목적: 요청별 트랜잭션 ID 추적, 로깅
// 규모: 일 500만 건 결제, 초당 2만 요청
// 효과: 분산 추적, 장애 원인 빠른 파악

@Component
@Scope(value = "request", proxyMode = ScopedProxyMode.TARGET_CLASS)
public class PaymentRequestContext {

    private String transactionId;
    private String userId;
    private LocalDateTime startTime;
    private Map<String, Object> metadata = new HashMap<>();

    @PostConstruct
    public void init() {
        this.transactionId = "TX-" + UUID.randomUUID();
        this.startTime = LocalDateTime.now();

        // MDC에 등록 (로그에 자동 포함)
        MDC.put("transactionId", transactionId);

        log.info("결제 요청 시작: {}", transactionId);
    }

    @PreDestroy
    public void destroy() {
        long duration = Duration.between(startTime, LocalDateTime.now()).toMillis();
        log.info("결제 요청 완료: {} (소요: {}ms)", transactionId, duration);

        // 성능 메트릭 수집
        collectMetrics(duration);

        MDC.clear();
    }

    public void addMetadata(String key, Object value) {
        metadata.put(key, value);
    }
}

@RestController
public class PaymentController {

    @Autowired
    private PaymentRequestContext requestContext;

    @PostMapping("/payment")
    public ResponseEntity<String> pay(@RequestBody PaymentRequest request) {
        // 요청 정보 저장
        requestContext.addMetadata("amount", request.getAmount());
        requestContext.addMetadata("method", request.getMethod());

        // 결제 처리
        String result = paymentService.process(request);

        // 결과 저장
        requestContext.addMetadata("result", result);

        return ResponseEntity.ok(result);
    }
}

// 성과:
// - 분산 추적으로 장애 원인 파악 시간: 1시간 → 5분
// - 모든 로그에 transactionId 자동 포함
// - 성능 병목 지점 실시간 모니터링
```

---

## ❓ FAQ

<details>
<summary><strong>Q1: Bean의 기본 스코프는 무엇인가요?</strong></summary>

**A**: **Singleton**이 기본 스코프입니다.

```java
// 명시 안 해도 Singleton
@Service
public class UserService { }

// 명시적으로 지정
@Service
@Scope("singleton")
public class ProductService { }
```

**이유**: 대부분의 Bean은 상태가 없고(Stateless), 재사용하는 것이 메모리 효율적이기 때문

</details>

<details>
<summary><strong>Q2: Singleton Bean에 상태를 저장하면 안 되는 이유는?</strong></summary>

**A**: 모든 요청이 같은 인스턴스를 공유하므로 **동시성 문제**가 발생합니다.

**나쁜 예**:
```java
@Service
public class BadService {
    private int count = 0;  // ❌ 위험!

    public void increment() {
        count++;  // Race Condition
    }
}

// 요청1: count = 0 → 1
// 요청2: count = 1 → 2 (요청1의 데이터 오염!)
```

**좋은 예**:
```java
@Service
public class GoodService {
    // 상태 없음 (Stateless)

    public int calculate(int input) {
        // 파라미터로 받아서 처리
        return input * 2;
    }
}
```

</details>

<details>
<summary><strong>Q3: Prototype Bean을 언제 사용하나요?</strong></summary>

**A**: **상태를 가져야 하는 Bean**에 사용합니다.

**사용 시나리오**:
1. **Command 패턴**: 각 명령마다 독립적인 상태
2. **Builder 패턴**: 빌더마다 독립적인 구성
3. **멀티스레드 작업**: 스레드마다 독립적인 객체

```java
@Component
@Scope("prototype")
public class ReportGenerator {
    private List<String> data = new ArrayList<>();

    public void addData(String item) {
        data.add(item);
    }

    public String generate() {
        return String.join("\n", data);
    }
}

// 사용
@Service
public class ReportService {
    @Autowired
    private ApplicationContext context;

    public String createReport() {
        // 매번 새 ReportGenerator
        ReportGenerator generator = context.getBean(ReportGenerator.class);
        generator.addData("Data 1");
        generator.addData("Data 2");
        return generator.generate();
    }
}
```

</details>

<details>
<summary><strong>Q4: Request/Session Scope에서 proxyMode가 필요한 이유는?</strong></summary>

**A**: Singleton Bean에 Request/Session-scoped Bean을 주입할 때 **Proxy**가 필요합니다.

**문제 상황**:
```java
@Service  // Singleton
public class UserService {
    @Autowired
    private RequestContext requestContext;  // Request-scoped

    // ❌ 에러!
    // Singleton Bean 생성 시점에는 Request가 없음
}
```

**해결 (Proxy 사용)**:
```java
@Component
@Scope(value = "request", proxyMode = ScopedProxyMode.TARGET_CLASS)
public class RequestContext {
    // proxyMode로 Proxy 객체 생성
}

@Service
public class UserService {
    @Autowired
    private RequestContext requestContext;  // Proxy 주입

    public void doSomething() {
        // Proxy가 현재 요청의 실제 Bean을 참조
        String id = requestContext.getRequestId();
    }
}
```

</details>

<details>
<summary><strong>Q5: Prototype Bean의 @PreDestroy가 실행 안 되는 이유는?</strong></summary>

**A**: Spring이 Prototype Bean의 **소멸을 관리하지 않기** 때문입니다.

```java
@Component
@Scope("prototype")
public class PrototypeBean {

    @PreDestroy
    public void destroy() {
        System.out.println("소멸");  // ❌ 실행 안 됨!
    }
}
```

**이유**:
- Prototype Bean은 요청마다 생성
- 생성 후 Spring이 참조를 유지하지 않음
- 클라이언트가 직접 관리해야 함

**해결**:
```java
@Service
public class ServiceUsingPrototype {
    @Autowired
    private ApplicationContext context;

    public void usePrototype() {
        PrototypeBean bean = context.getBean(PrototypeBean.class);

        try {
            // 사용
        } finally {
            // 직접 정리 (필요시)
            bean.destroy();
        }
    }
}
```

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. Bean 스코프가 무엇이고, 기본 스코프는 무엇인가요?</strong></summary>

**모범 답안**:
> "Bean 스코프는 Bean의 생존 범위를 결정하는 설정입니다. 기본 스코프는 Singleton으로, 컨테이너당 Bean 인스턴스가 1개만 생성되고 모든 요청에 대해 같은 인스턴스를 재사용합니다. Singleton 외에 Prototype, Request, Session 등이 있습니다."

</details>

<details>
<summary><strong>2. Singleton Bean에 상태를 저장하면 안 되는 이유는 무엇인가요?</strong></summary>

**모범 답안**:
> "Singleton Bean은 모든 요청이 같은 인스턴스를 공유하므로, 상태를 저장하면 동시성 문제가 발생합니다. 여러 스레드가 동시에 상태를 변경하면 Race Condition이 발생하고, 예측할 수 없는 결과가 나옵니다. 따라서 Singleton Bean은 Stateless하게 설계해야 합니다."

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. Singleton과 Prototype 스코프를 비교하고, 각각의 사용 시나리오를 설명해주세요</strong></summary>

**모범 답안**:
> "Singleton은 컨테이너당 인스턴스 1개로, 상태가 없는 Service, Repository 등에 사용합니다. 메모리 효율적이고 성능이 좋지만 Thread-safe 해야 합니다. Prototype은 요청마다 새 인스턴스를 생성하므로 상태를 가질 수 있어 Command 패턴, Builder 패턴 등에 사용합니다. 단, Spring이 소멸을 관리하지 않으므로 리소스 정리가 필요하면 직접 처리해야 합니다."

</details>

---

## 📝 핵심 정리

### Bean 스코프 비교

| 스코프 | 생명주기 | 인스턴스 수 | 주요 용도 | 사용 빈도 |
|--------|---------|------------|----------|-----------|
| **Singleton** | 컨테이너 | 1개 | Service, Repository | 95% |
| **Prototype** | 요청마다 | 매번 생성 | Command, Builder | 3% |
| **Request** | HTTP 요청 | 요청마다 | 요청 정보, 로깅 | 1.5% |
| **Session** | HTTP 세션 | 세션마다 | 장바구니, 로그인 정보 | 0.4% |

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] **Singleton은 Stateless**: 상태 저장 금지
- [ ] **Prototype은 신중히 사용**: 메모리 누수 주의
- [ ] **Session 스코프는 최소한으로**: Redis 등 외부 저장소 고려
- [ ] **Request 스코프로 로깅 컨텍스트 관리**: 분산 추적 용이

#### ❌ 하지 말아야 할 것
- [ ] **Singleton에 mutable 상태**: 동시성 버그
- [ ] **Prototype 남발**: 메모리 증가, GC 부담
- [ ] **Session에 대용량 데이터**: 메모리 부족
- [ ] **proxyMode 없이 Singleton에 Request Bean 주입**: 에러

---

## 🎉 축하합니다!

**이제 여러분은**:
- ✅ Bean 스코프의 종류와 차이를 이해할 수 있습니다
- ✅ 상황에 맞는 스코프를 선택할 수 있습니다
- ✅ Singleton의 Thread-safety를 보장할 수 있습니다
- ✅ Request/Session 스코프로 웹 애플리케이션 개발 가능

---

**[← 이전: Part 1](06-1-Bean-스코프-Part1.md)** | **[목차로 돌아가기](../README.md)**
