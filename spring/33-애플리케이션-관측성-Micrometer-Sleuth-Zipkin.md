# 33장: 애플리케이션 관측성 (Micrometer, Sleuth, Zipkin)

> **"분산 시스템에서 요청의 흐름을 추적하고 성능을 측정하세요"**

---

## 📋 학습 목표

이 장을 학습하면 다음을 할 수 있습니다:

- 관측성(Observability)의 3가지 축을 이해합니다
- Micrometer로 메트릭을 수집하고 시각화합니다
- Spring Cloud Sleuth로 분산 추적을 구현합니다
- Zipkin으로 요청 흐름을 시각화합니다
- 프로메테우스와 그라파나를 연동합니다

**예상 학습 시간**: 4-5시간
**난이도**: ⭐⭐⭐⭐ (중고급)

---

## 🤔 왜 관측성이 필요한가?

### 문제 상황: 마이크로서비스의 블랙홀

#### 문제 1: 분산 추적 불가능

```
사용자: "주문이 30초나 걸렸어요!"
개발자: "어디가 느린 거지?"

[주문 서비스] → [재고 서비스] → [결제 서비스] → [배송 서비스]
    0.5초          ???초           ???초           ???초

→ 어느 서비스가 병목인지 알 수 없음
```

#### 문제 2: 로그 파편화

```
[주문 서비스 로그]
2025-01-15 10:00:00 INFO Order created: order-123

[결제 서비스 로그]
2025-01-15 10:00:05 INFO Payment processed

// 같은 요청인지 확인 불가능!
```

### 관측성의 해결책

```
[Zipkin 대시보드]
요청 ID: trace-abc123

주문 서비스    (500ms)  ━━━━━━━━
  ↓
재고 서비스    (200ms)    ━━
  ↓
결제 서비스    (5000ms)     ━━━━━━━━━━━━━━━ ← 병목 발견!
  ↓
배송 서비스    (300ms)      ━━━

총 소요 시간: 6초
```

---

## 🌍 실생활 비유로 이해하는 관측성

### 비유 1: 택배 추적

**관측성 없음:**
```
"택배가 언제 오나요?"
"모르겠어요. 기다려보세요."
```

**관측성 있음:**
```
[택배 추적]
1. 상품 준비 완료 (1시간)
2. 집화 완료 (30분)
3. 간선 상차 (2시간)
4. 배송 출발 (1시간)
5. 배송 완료
→ 현재 위치와 예상 시간 확인 가능
```

### 비유 2: 병원 진료 기록

**로그만 있는 경우:**
```
환자별로 따로 기록
→ 전체 진료 과정 파악 어려움
```

**관측성 (차트):**
```
환자 ID: P12345
10:00 접수 → 10:15 대기 → 10:30 진료 → 11:00 검사 → 11:30 수납
→ 전체 진료 흐름 한눈에 파악
```

### 비유 3: 공장 생산 라인

**전통 방식:**
```
각 공정별로 시간 측정
→ 전체 프로세스 최적화 어려움
```

**관측성:**
```
[생산 모니터링]
원자재 입고 (5분) → 1차 가공 (20분) → 조립 (15분) → 품질 검사 (30분)
→ 품질 검사가 병목 발견
→ 검사 프로세스 개선
```

---

## 💡 관측성 핵심 개념

### 1️⃣ 초급: 관측성의 3가지 축

```
┌─────────────────────────────────────┐
│         관측성 (Observability)       │
├─────────────────────────────────────┤
│ 1. Metrics (메트릭)                  │
│    - CPU, 메모리, 응답 시간          │
│    - Micrometer, Prometheus         │
│                                     │
│ 2. Logs (로그)                       │
│    - 애플리케이션 이벤트             │
│    - Logback, ELK Stack             │
│                                     │
│ 3. Traces (추적)                     │
│    - 분산 시스템 요청 흐름           │
│    - Sleuth, Zipkin, Jaeger         │
└─────────────────────────────────────┘
```

### 2️⃣ 중급: Micrometer - 메트릭 수집

#### 의존성

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-actuator'
    implementation 'io.micrometer:micrometer-registry-prometheus'
}
```

#### 기본 메트릭

```java
@RestController
@RequiredArgsConstructor
public class OrderController {

    private final MeterRegistry meterRegistry;

    @PostMapping("/orders")
    public Order createOrder(@RequestBody OrderRequest request) {
        // Timer - 실행 시간 측정
        return Timer.sample(meterRegistry)
                .record(() -> {
                    Order order = processOrder(request);

                    // Counter - 주문 수 카운트
                    meterRegistry.counter("orders.created",
                        "type", order.getType()).increment();

                    return order;
                });
    }

    @GetMapping("/orders/stats")
    public OrderStats getStats() {
        // Gauge - 실시간 값
        meterRegistry.gauge("orders.pending",
            getPendingOrderCount());

        return new OrderStats();
    }
}
```

#### 커스텀 메트릭

```java
@Component
public class BusinessMetrics {

    private final MeterRegistry registry;
    private final Counter salesCounter;
    private final DistributionSummary orderAmount;

    public BusinessMetrics(MeterRegistry registry) {
        this.registry = registry;

        // 매출 카운터
        this.salesCounter = Counter.builder("sales.total")
                .description("Total sales amount")
                .tag("currency", "KRW")
                .register(registry);

        // 주문 금액 분포
        this.orderAmount = DistributionSummary.builder("order.amount")
                .description("Order amount distribution")
                .baseUnit("krw")
                .register(registry);
    }

    public void recordSale(double amount) {
        salesCounter.increment(amount);
        orderAmount.record(amount);
    }
}
```

### 3️⃣ 고급: Sleuth & Zipkin - 분산 추적

#### Sleuth 설정

```gradle
dependencies {
    implementation 'org.springframework.cloud:spring-cloud-starter-sleuth'
    implementation 'org.springframework.cloud:spring-cloud-sleuth-zipkin'
}
```

```yaml
spring:
  sleuth:
    sampler:
      probability: 1.0  # 100% 샘플링 (개발용)
  zipkin:
    base-url: http://localhost:9411
    enabled: true
```

#### 자동 추적

```java
// Sleuth가 자동으로 추적 ID 추가
@RestController
public class OrderController {

    private final RestTemplate restTemplate;

    @GetMapping("/orders/{id}")
    public Order getOrder(@PathVariable Long id) {
        // HTTP 헤더에 trace-id, span-id 자동 추가
        Product product = restTemplate.getForObject(
            "http://product-service/products/1",
            Product.class
        );

        return new Order(id, product);
    }
}
```

**로그 출력:**
```
[order-service] [trace-id: abc123, span-id: 001] Order requested
[product-service] [trace-id: abc123, span-id: 002] Product fetched
```

---

## 🛠️ 기본 실습

### 실습 1: Prometheus + Grafana 연동

#### Step 1: 의존성 추가

```gradle
dependencies {
    implementation 'io.micrometer:micrometer-registry-prometheus'
}
```

#### Step 2: Prometheus 설정

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'spring-boot'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets: ['localhost:8080']
```

#### Step 3: Docker Compose

```yaml
version: '3'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

```bash
docker-compose up -d
```

#### Step 4: Grafana 대시보드

```
1. http://localhost:3000 접속
2. admin/admin 로그인
3. Data Source 추가: Prometheus (http://prometheus:9090)
4. Dashboard Import: JVM Dashboard (ID: 4701)
```

---

### 실습 2: Zipkin 분산 추적

#### Step 1: Zipkin 실행

```bash
docker run -d -p 9411:9411 openzipkin/zipkin
```

#### Step 2: 서비스 구성

**Order Service:**
```yaml
# application.yml
spring:
  application:
    name: order-service
  zipkin:
    base-url: http://localhost:9411
  sleuth:
    sampler:
      probability: 1.0
```

```java
@RestController
@RequiredArgsConstructor
public class OrderController {

    private final RestTemplate restTemplate;

    @GetMapping("/orders")
    public String createOrder() {
        // Product Service 호출
        String product = restTemplate.getForObject(
            "http://localhost:8081/products", String.class);

        // Payment Service 호출
        String payment = restTemplate.getForObject(
            "http://localhost:8082/payments", String.class);

        return "Order: " + product + " " + payment;
    }
}

@Configuration
class RestTemplateConfig {
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
```

**Product Service:**
```yaml
spring:
  application:
    name: product-service
server:
  port: 8081
```

```java
@RestController
public class ProductController {

    @GetMapping("/products")
    public String getProduct() throws InterruptedException {
        Thread.sleep(200);  // 시뮬레이션
        return "Product-123";
    }
}
```

**Payment Service:**
```yaml
spring:
  application:
    name: payment-service
server:
  port: 8082
```

```java
@RestController
public class PaymentController {

    @GetMapping("/payments")
    public String processPayment() throws InterruptedException {
        Thread.sleep(500);  // 시뮬레이션
        return "Payment-OK";
    }
}
```

#### Step 3: 확인

```bash
# 요청 실행
curl http://localhost:8080/orders

# Zipkin 대시보드 확인
http://localhost:9411
```

**Zipkin UI에서 확인:**
```
Timeline:
├─ order-service (800ms)
│  ├─ product-service (200ms)
│  └─ payment-service (500ms)
```

---

### 실습 3: 커스텀 Span

```java
@Service
@RequiredArgsConstructor
public class OrderService {

    private final Tracer tracer;

    public Order processOrder(OrderRequest request) {
        // 커스텀 Span 생성
        Span span = tracer.nextSpan().name("validate-order").start();
        try (Tracer.SpanInScope ws = tracer.withSpan(span)) {
            span.tag("order.id", request.getId().toString());
            span.tag("order.amount", String.valueOf(request.getAmount()));

            validateOrder(request);

            return createOrder(request);
        } catch (Exception e) {
            span.tag("error", e.getMessage());
            throw e;
        } finally {
            span.end();
        }
    }
}
```

---

## 👨‍💻 주니어 개발자 실전 시나리오

### 시나리오: "느린 API 원인 찾기"

**문제:**
```
사용자: "주문이 너무 느려요 (10초)"
```

**Zipkin으로 추적:**

```
[Zipkin Timeline]
order-service (10.5초)
├─ validate-order (0.1초)
├─ product-service (0.2초)
├─ inventory-service (9.8초) ← 병목!
│  ├─ check-stock (0.1초)
│  └─ database-query (9.7초) ← 원인 발견!
└─ payment-service (0.3초)
```

**해결:**
```java
// 느린 쿼리 최적화
@Query("SELECT i FROM Inventory i WHERE i.productId = :id")
Inventory findByProductId(@Param("id") Long id);

// 인덱스 추가
CREATE INDEX idx_product_id ON inventory(product_id);
```

---

## 🏢 기업 사례: Uber

### 배경

Uber는 2000+ 마이크로서비스를 운영하며 분산 추적이 필수였습니다.

**도입 전:**
- 장애 원인 파악: 4시간
- 성능 병목 발견: 불가능

**Jaeger (Zipkin과 유사) 도입 후:**
```yaml
uber:
  tracing:
    enabled: true
    sampler:
      type: probabilistic
      param: 0.001  # 0.1% 샘플링
```

**효과:**
- 장애 원인 파악: 4시간 → 10분
- 성능 병목 자동 감지
- 서비스 의존성 시각화

---

## ❓ FAQ

### Q1. 샘플링 비율은 어떻게 설정하나요?

**A:** 환경에 따라 다릅니다.

```yaml
spring:
  sleuth:
    sampler:
      probability: 1.0    # 개발: 100%
      probability: 0.1    # 스테이징: 10%
      probability: 0.01   # 운영: 1%
```

### Q2. Zipkin vs Jaeger 차이는?

**A:**

| 특징 | Zipkin | Jaeger |
|-----|--------|--------|
| 개발사 | Twitter | Uber |
| 저장소 | Cassandra, ES | Cassandra, ES |
| UI | 간단 | 풍부 |
| 성능 | 보통 | 우수 |

### Q3. 추적 ID를 로그에 포함하려면?

**A:** Logback 설정

```xml
<pattern>
  %d{yyyy-MM-dd HH:mm:ss} [%X{traceId}/%X{spanId}] %msg%n
</pattern>
```

### Q4. Micrometer vs Prometheus Client?

**A:** Micrometer 권장 (벤더 중립)

```
Micrometer = 메트릭의 SLF4J
→ Prometheus, Datadog, New Relic 등 모두 지원
```

### Q5. 성능 오버헤드는?

**A:** 샘플링으로 최소화

```yaml
# 1% 샘플링 시 오버헤드 < 1%
spring:
  sleuth:
    sampler:
      probability: 0.01
```

---

## 💼 면접 질문 TOP 5

### ⭐ 초급 1: 관측성의 3가지 축은?

**답변:**
1. **Metrics**: 수치 데이터 (CPU, 메모리)
2. **Logs**: 이벤트 기록
3. **Traces**: 분산 추적

### ⭐ 초급 2: Trace ID와 Span ID란?

**답변:**
- **Trace ID**: 전체 요청 흐름 식별
- **Span ID**: 각 서비스 호출 식별

```
Trace: abc123
├─ Span: 001 (order-service)
├─ Span: 002 (product-service)
└─ Span: 003 (payment-service)
```

### ⭐⭐ 중급 1: Micrometer의 메트릭 타입은?

**답변:**
```java
Counter      // 누적 값
Gauge        // 실시간 값
Timer        // 시간 측정
Summary      // 분포 측정
```

### ⭐⭐ 중급 2: 분산 추적 구현 방법은?

**답변:**

```gradle
// 1. 의존성
implementation 'org.springframework.cloud:spring-cloud-starter-sleuth'
implementation 'org.springframework.cloud:spring-cloud-sleuth-zipkin'

// 2. 설정
spring:
  zipkin:
    base-url: http://localhost:9411

// 3. 자동 추적 (코드 수정 불필요)
```

### ⭐⭐ 중급 3: Prometheus와 연동하는 이유는?

**답변:**
- 시계열 데이터베이스
- 강력한 쿼리 언어 (PromQL)
- Grafana 시각화
- 알람 기능

```yaml
management:
  metrics:
    export:
      prometheus:
        enabled: true
```

---

## 🎯 다음 단계

관측성을 마쳤다면:

1. **34장: 로깅** - 효과적인 로그 관리
2. **ELK Stack** - 로그 수집/분석
3. **APM 도구** - New Relic, Datadog

---

**🎓 학습 완료 체크리스트:**

- [ ] Micrometer 메트릭 수집
- [ ] Prometheus 연동
- [ ] Sleuth 분산 추적
- [ ] Zipkin 시각화
- [ ] 커스텀 메트릭 생성
- [ ] 병목 지점 분석

**다음 장에서는 효과적인 로깅 전략을 배웁니다!** 🚀
