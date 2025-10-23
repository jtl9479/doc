# 32장: Actuator - 운영 환경의 눈과 귀

> **"애플리케이션의 건강 상태를 실시간으로 확인하세요"**

---

## 📋 학습 목표

이 장을 학습하면 다음을 할 수 있습니다:

- Spring Boot Actuator의 개념과 필요성을 이해합니다
- 다양한 엔드포인트를 활용하여 애플리케이션을 모니터링합니다
- 커스텀 Health Indicator와 Metric을 생성할 수 있습니다
- 보안을 고려한 Actuator 설정을 구성합니다
- 프로메테우스와 연동하여 메트릭을 수집합니다

**예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐ (중급)

---

## 🤔 왜 Actuator가 필요한가?

### 문제 상황: 블랙박스 운영

#### 문제 1: 장애 감지 지연

```
새벽 3시...
사용자: "사이트가 안 열려요!"
개발자: "어? 서버가 살아있나?"
         "데이터베이스는 연결됐나?"
         "메모리는 괜찮나?"
→ 서버에 SSH 접속해서 일일이 확인
→ 장애 원인 파악까지 30분 소요
```

**개발자의 고통:**
- "서버가 죽었는지 살았는지 모르겠어요"
- "어느 부분이 느린지 확인할 방법이 없어요"
- "메모리 누수가 있는 것 같은데..."

#### 문제 2: 수동 모니터링

```bash
# 매번 서버 접속해서 확인
ssh server@prod
ps aux | grep java
free -m
df -h
tail -f /var/log/app.log
```

### Actuator의 해결책

```bash
# HTTP로 간편하게 확인
curl http://localhost:8080/actuator/health
{
  "status": "UP",
  "components": {
    "db": { "status": "UP" },
    "diskSpace": { "status": "UP" }
  }
}

curl http://localhost:8080/actuator/metrics/jvm.memory.used
{
  "name": "jvm.memory.used",
  "measurements": [{"value": 524288000}]
}
```

---

## 🌍 실생활 비유로 이해하는 Actuator

### 비유 1: 자동차 계기판

**Actuator 없는 상황 (옛날 차):**
```
운전 중...
"이상한 소리가 나네?"
→ 차 멈추고 보닛 열기
→ 엔진 확인
→ 문제 발견까지 1시간
```

**Actuator (최신 차):**
```
계기판 확인:
- 속도: 80km/h
- RPM: 2500
- 연료: 50%
- 엔진 온도: 정상
- 경고등: 없음
→ 실시간 상태 확인
```

### 비유 2: 병원 환자 모니터

**전통 방식:**
```
1시간마다 간호사가 확인
- 체온 측정
- 혈압 측정
- 심박수 확인
→ 급격한 변화 놓칠 수 있음
```

**Actuator (환자 모니터):**
```
실시간 모니터링:
- 심박수: 72 bpm
- 혈압: 120/80
- 산소포화도: 98%
경고: 이상 수치 시 알람
```

### 비유 3: 스마트 홈

**일반 집:**
```
"전기세가 많이 나왔네?"
→ 어디서 많이 쓰는지 모름
```

**스마트 홈 (Actuator):**
```
앱으로 확인:
- 에어컨: 3kW
- 냉장고: 0.5kW
- TV: 0.2kW
→ 실시간 사용량 확인
→ 이상 패턴 감지
```

---

## 💡 Actuator 핵심 개념

### 1️⃣ 초급: 기본 설정 및 엔드포인트

#### 의존성 추가

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-actuator'
}
```

#### 기본 설정

```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: always
```

#### 주요 엔드포인트

| 엔드포인트 | 용도 | 예시 |
|----------|------|------|
| `/health` | 헬스 체크 | 애플리케이션 상태 확인 |
| `/info` | 애플리케이션 정보 | 버전, 빌드 정보 |
| `/metrics` | 메트릭 | JVM, HTTP, DB 통계 |
| `/env` | 환경 변수 | 설정 정보 |
| `/loggers` | 로그 레벨 | 런타임 로그 변경 |
| `/threaddump` | 쓰레드 덤프 | 데드락 확인 |
| `/heapdump` | 힙 덤프 | 메모리 분석 |
| `/prometheus` | 프로메테우스 | 메트릭 수집 |

### 2️⃣ 중급: Health Indicator

#### 기본 Health Check

```bash
curl http://localhost:8080/actuator/health
```

```json
{
  "status": "UP",
  "components": {
    "db": {
      "status": "UP",
      "details": {
        "database": "MySQL",
        "validationQuery": "isValid()"
      }
    },
    "diskSpace": {
      "status": "UP",
      "details": {
        "total": 500000000000,
        "free": 250000000000,
        "threshold": 10485760
      }
    },
    "ping": {
      "status": "UP"
    }
  }
}
```

#### 커스텀 Health Indicator

```java
@Component
public class CustomHealthIndicator implements HealthIndicator {

    @Override
    public Health health() {
        // 비즈니스 로직으로 건강 상태 체크
        boolean isHealthy = checkExternalApi();

        if (isHealthy) {
            return Health.up()
                    .withDetail("externalApi", "Available")
                    .withDetail("responseTime", "120ms")
                    .build();
        } else {
            return Health.down()
                    .withDetail("externalApi", "Unavailable")
                    .withDetail("error", "Connection timeout")
                    .build();
        }
    }

    private boolean checkExternalApi() {
        // API 호출 로직
        return true;
    }
}
```

```java
// 더 간편한 방법
@Component
public class PaymentServiceHealthIndicator extends AbstractHealthIndicator {

    private final PaymentService paymentService;

    public PaymentServiceHealthIndicator(PaymentService paymentService) {
        this.paymentService = paymentService;
    }

    @Override
    protected void doHealthCheck(Health.Builder builder) throws Exception {
        boolean isAvailable = paymentService.checkConnection();

        if (isAvailable) {
            builder.up()
                    .withDetail("service", "payment")
                    .withDetail("status", "operational");
        } else {
            builder.down()
                    .withDetail("service", "payment")
                    .withDetail("status", "down");
        }
    }
}
```

### 3️⃣ 고급: Metrics와 Micrometer

#### 기본 Metrics

```bash
# 사용 가능한 메트릭 목록
curl http://localhost:8080/actuator/metrics

# JVM 메모리 사용량
curl http://localhost:8080/actuator/metrics/jvm.memory.used

# HTTP 요청 수
curl http://localhost:8080/actuator/metrics/http.server.requests
```

#### 커스텀 Metric

```java
@Service
public class OrderService {

    private final MeterRegistry meterRegistry;
    private final Counter orderCounter;
    private final Timer orderTimer;

    public OrderService(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;

        // Counter: 주문 수 카운트
        this.orderCounter = Counter.builder("orders.created")
                .description("Total orders created")
                .tag("type", "online")
                .register(meterRegistry);

        // Timer: 주문 처리 시간
        this.orderTimer = Timer.builder("orders.processing.time")
                .description("Order processing time")
                .register(meterRegistry);
    }

    public void createOrder(Order order) {
        orderTimer.record(() -> {
            // 주문 처리 로직
            processOrder(order);

            // 카운터 증가
            orderCounter.increment();
        });
    }

    // Gauge: 실시간 값
    @PostConstruct
    public void init() {
        Gauge.builder("orders.pending", this, OrderService::getPendingOrderCount)
                .description("Number of pending orders")
                .register(meterRegistry);
    }

    private long getPendingOrderCount() {
        // 실시간 대기 중인 주문 수
        return 42;
    }
}
```

---

## 🛠️ 기본 실습

### 실습 1: Actuator 기본 설정

```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: "*"  # 모든 엔드포인트 노출 (개발용)
      base-path: /actuator
  endpoint:
    health:
      show-details: always
      show-components: always
    shutdown:
      enabled: true  # 원격 종료 (주의!)

  info:
    env:
      enabled: true
    git:
      mode: full

spring:
  application:
    name: my-app

info:
  app:
    name: ${spring.application.name}
    description: My Spring Boot Application
    version: 1.0.0
    encoding: @project.build.sourceEncoding@
```

### 실습 2: 보안 설정

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-security'
    implementation 'org.springframework.boot:spring-boot-starter-actuator'
}
```

```java
@Configuration
public class ActuatorSecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health").permitAll()
                .requestMatchers("/actuator/info").permitAll()
                .requestMatchers("/actuator/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .httpBasic(withDefaults());

        return http.build();
    }
}
```

```yaml
spring:
  security:
    user:
      name: admin
      password: admin123
```

### 실습 3: 프로메테우스 연동

```gradle
dependencies {
    implementation 'io.micrometer:micrometer-registry-prometheus'
}
```

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  metrics:
    export:
      prometheus:
        enabled: true
```

```bash
# 프로메테우스 형식으로 메트릭 확인
curl http://localhost:8080/actuator/prometheus
```

---

## 👨‍💻 주니어 개발자 실전 시나리오

### 시나리오: "운영 장애 대응"

**3시간 전:**
```yaml
# 정상 상태
management:
  endpoint:
    health:
      show-details: always
```

**현재 상황:**
```
사용자 불만 급증
→ "사이트가 느려요"
→ "결제가 안 돼요"
```

**Actuator로 확인:**

```bash
# 1. 헬스 체크
curl http://localhost:8080/actuator/health

{
  "status": "DOWN",
  "components": {
    "db": { "status": "DOWN" },  # ← 문제 발견!
    "diskSpace": { "status": "UP" }
  }
}

# 2. 메트릭 확인
curl http://localhost:8080/actuator/metrics/jdbc.connections.active

{
  "name": "jdbc.connections.active",
  "measurements": [{"value": 50}]  # ← 커넥션 풀 고갈!
}

# 3. 쓰레드 덤프
curl http://localhost:8080/actuator/threaddump
# → DB 커넥션 대기 중인 쓰레드 다수 발견
```

**해결:**
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 50  # 20 → 50 증가
      connection-timeout: 3000
```

---

## 🏢 기업 사례: Netflix

### 배경

Netflix는 수천 개의 마이크로서비스를 모니터링해야 했습니다.

**해결책:**
- 모든 서비스에 Actuator 표준화
- 중앙 모니터링 시스템 구축
- 자동 알람 설정

```yaml
# Netflix 표준 설정
management:
  endpoints:
    web:
      exposure:
        include: health,metrics,prometheus
  metrics:
    tags:
      service: ${spring.application.name}
      env: ${ENVIRONMENT}
      region: ${AWS_REGION}
```

**효과:**
- 장애 감지 시간: 10분 → 30초
- MTTR (평균 복구 시간) 70% 단축
- 운영 인력 30% 절감

---

## ❓ FAQ

### Q1. 운영 환경에서 모든 엔드포인트를 노출해도 되나요?

**A:** 절대 안 됩니다! 보안 필수

```yaml
# ❌ 위험
management:
  endpoints:
    web:
      exposure:
        include: "*"

# ✅ 안전
management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus
```

### Q2. /actuator 경로를 변경할 수 있나요?

**A:** 네, 가능합니다.

```yaml
management:
  endpoints:
    web:
      base-path: /manage  # /actuator → /manage
```

### Q3. Health 상태에 따라 로드밸런서가 제외하나요?

**A:** 네, 쿠버네티스 등에서 활용합니다.

```yaml
# Kubernetes Liveness Probe
livenessProbe:
  httpGet:
    path: /actuator/health/liveness
    port: 8080

# Readiness Probe
readinessProbe:
  httpGet:
    path: /actuator/health/readiness
    port: 8080
```

### Q4. 메트릭을 데이터베이스에 저장할 수 있나요?

**A:** 직접 저장보다는 모니터링 시스템 사용 권장

```
Actuator → Prometheus → Grafana
         → InfluxDB → Grafana
         → Datadog
```

### Q5. 런타임에 로그 레벨을 변경하려면?

**A:** `/actuator/loggers` 사용

```bash
# 현재 로그 레벨 확인
curl http://localhost:8080/actuator/loggers/com.example

# 로그 레벨 변경
curl -X POST http://localhost:8080/actuator/loggers/com.example \
  -H "Content-Type: application/json" \
  -d '{"configuredLevel":"DEBUG"}'
```

---

## 💼 면접 질문 TOP 5

### ⭐ 초급 1: Actuator란 무엇인가요?

**답변:**
Spring Boot 애플리케이션의 모니터링과 관리를 위한 프로덕션 레디 기능입니다.

- Health Check
- Metrics 수집
- 환경 정보 확인
- 로그 레벨 변경

### ⭐ 초급 2: 주요 엔드포인트는?

**답변:**
```
/actuator/health   - 헬스 체크
/actuator/metrics  - 메트릭
/actuator/info     - 앱 정보
/actuator/env      - 환경 변수
/actuator/loggers  - 로그 설정
```

### ⭐⭐ 중급 1: 커스텀 Health Indicator를 만드는 방법은?

**답변:**

```java
@Component
public class CustomHealthIndicator implements HealthIndicator {
    @Override
    public Health health() {
        boolean healthy = checkSomething();
        if (healthy) {
            return Health.up().build();
        } else {
            return Health.down().withDetail("error", "Failed").build();
        }
    }
}
```

### ⭐⭐ 중급 2: 보안을 적용하는 방법은?

**답변:**

```yaml
# 1. 필요한 엔드포인트만 노출
management:
  endpoints:
    web:
      exposure:
        include: health,info

# 2. Spring Security 적용
@Configuration
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) {
        http.authorizeHttpRequests(auth -> auth
            .requestMatchers("/actuator/**").hasRole("ADMIN")
        );
        return http.build();
    }
}
```

### ⭐⭐ 중급 3: 프로메테우스와 연동하려면?

**답변:**

```gradle
implementation 'io.micrometer:micrometer-registry-prometheus'
```

```yaml
management:
  endpoints:
    web:
      exposure:
        include: prometheus
  metrics:
    export:
      prometheus:
        enabled: true
```

---

## 🎯 다음 단계

Actuator를 마쳤다면:

1. **33장: 애플리케이션 관측성** - Micrometer, Sleuth, Zipkin
2. **그라파나 대시보드** - 시각화
3. **알람 설정** - 장애 자동 감지

---

**🎓 학습 완료 체크리스트:**

- [ ] Actuator 설정 및 활성화
- [ ] 주요 엔드포인트 활용
- [ ] 커스텀 Health Indicator 작성
- [ ] 보안 설정 적용
- [ ] 메트릭 수집 및 모니터링
- [ ] 프로메테우스 연동

**다음 장에서는 분산 추적과 관측성을 마스터합니다!** 🚀
