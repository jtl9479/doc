# 08장: AOP 개념과 활용 - Part 2 (실습 & 실무 & FAQ & 면접)

**[← 이전: Part 1](08-1-AOP개념활용-Part1.md)** | **[목차로 돌아가기](../README.md)**

---

## 💻 기본 실습

### 실습 1: 성능 측정 Aspect

**난이도**: ⭐⭐⭐☆☆

```java
// 1. 성능 측정 어노테이션
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface PerformanceLog {
    String value() default "";
}

// 2. Aspect 구현
@Aspect
@Component
@Slf4j
public class PerformanceAspect {

    @Around("@annotation(performanceLog)")
    public Object measurePerformance(
        ProceedingJoinPoint joinPoint,
        PerformanceLog performanceLog
    ) throws Throwable {

        String methodName = joinPoint.getSignature().getName();
        String className = joinPoint.getTarget().getClass().getSimpleName();
        String label = performanceLog.value().isEmpty()
            ? methodName
            : performanceLog.value();

        log.info("⏱️ [{}] 실행 시작: {}.{}", label, className, methodName);
        long start = System.currentTimeMillis();

        try {
            Object result = joinPoint.proceed();
            long duration = System.currentTimeMillis() - start;

            if (duration > 1000) {
                log.warn("⚠️ [{}] 느린 실행: {}ms", label, duration);
            } else {
                log.info("✅ [{}] 실행 완료: {}ms", label, duration);
            }

            return result;

        } catch (Exception e) {
            long duration = System.currentTimeMillis() - start;
            log.error("❌ [{}] 실행 실패: {}ms", label, duration, e);
            throw e;
        }
    }
}

// 3. 사용
@Service
public class UserService {

    @PerformanceLog("사용자 생성")
    public User createUser(UserDto dto) {
        // 비즈니스 로직
        return new User(dto);
    }

    @PerformanceLog
    public List<User> getAllUsers() {
        // 성능 측정 필요한 메서드에만 적용
        return userRepository.findAll();
    }
}
```

**실행 결과**:
```
⏱️ [사용자 생성] 실행 시작: UserService.createUser
✅ [사용자 생성] 실행 완료: 45ms

⏱️ [getAllUsers] 실행 시작: UserService.getAllUsers
⚠️ [getAllUsers] 느린 실행: 1234ms
```

---

### 실습 2: 로깅 Aspect (메서드 파라미터 & 반환값)

**난이도**: ⭐⭐⭐⭐☆

```java
@Aspect
@Component
@Slf4j
public class DetailedLoggingAspect {

    @Around("execution(* com.example.service.*.*(..))")
    public Object logMethodExecution(ProceedingJoinPoint joinPoint) throws Throwable {

        MethodSignature signature = (MethodSignature) joinPoint.getSignature();
        String className = joinPoint.getTarget().getClass().getSimpleName();
        String methodName = signature.getName();

        // 파라미터 정보
        String[] parameterNames = signature.getParameterNames();
        Object[] parameterValues = joinPoint.getArgs();

        log.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        log.info("📍 메서드: {}.{}", className, methodName);

        // 파라미터 로깅
        if (parameterNames != null && parameterNames.length > 0) {
            log.info("📥 파라미터:");
            for (int i = 0; i < parameterNames.length; i++) {
                log.info("  - {} = {}", parameterNames[i], parameterValues[i]);
            }
        }

        long start = System.currentTimeMillis();

        try {
            // 메서드 실행
            Object result = joinPoint.proceed();

            long duration = System.currentTimeMillis() - start;

            // 반환값 로깅
            log.info("📤 반환값: {}", result);
            log.info("⏱️ 실행 시간: {}ms", duration);
            log.info("✅ 성공");
            log.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            return result;

        } catch (Exception e) {
            long duration = System.currentTimeMillis() - start;

            log.error("📤 예외: {}", e.getClass().getSimpleName());
            log.error("💬 메시지: {}", e.getMessage());
            log.error("⏱️ 실행 시간: {}ms", duration);
            log.error("❌ 실패");
            log.error("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            throw e;
        }
    }
}

// 사용
@Service
public class OrderService {

    public Order createOrder(OrderDto dto, String userId) {
        // 비즈니스 로직
        Order order = new Order(dto, userId);
        return orderRepository.save(order);
    }
}
```

**실행 결과**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 메서드: OrderService.createOrder
📥 파라미터:
  - dto = OrderDto(productId=123, quantity=2)
  - userId = user-456
📤 반환값: Order(id=789, total=50000)
⏱️ 실행 시간: 123ms
✅ 성공
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 실습 3: 예외 처리 및 재시도 Aspect

**난이도**: ⭐⭐⭐⭐⭐

```java
// 1. 재시도 어노테이션
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Retry {
    int maxAttempts() default 3;
    long delay() default 1000;  // ms
    Class<? extends Exception>[] retryFor() default {Exception.class};
}

// 2. Aspect 구현
@Aspect
@Component
@Slf4j
public class RetryAspect {

    @Around("@annotation(retry)")
    public Object retryOnException(
        ProceedingJoinPoint joinPoint,
        Retry retry
    ) throws Throwable {

        int maxAttempts = retry.maxAttempts();
        long delay = retry.delay();
        Class<? extends Exception>[] retryFor = retry.retryFor();

        int attempt = 0;
        Throwable lastException = null;

        while (attempt < maxAttempts) {
            attempt++;

            try {
                log.info("🔄 시도 {}/{}: {}",
                    attempt, maxAttempts, joinPoint.getSignature().getName());

                Object result = joinPoint.proceed();

                if (attempt > 1) {
                    log.info("✅ 재시도 성공: {}번째 시도", attempt);
                }

                return result;

            } catch (Throwable e) {
                lastException = e;

                // 재시도 대상 예외인지 확인
                boolean shouldRetry = Arrays.stream(retryFor)
                    .anyMatch(exClass -> exClass.isInstance(e));

                if (!shouldRetry) {
                    log.error("❌ 재시도 불가 예외: {}", e.getClass().getSimpleName());
                    throw e;
                }

                if (attempt < maxAttempts) {
                    log.warn("⚠️ 시도 {} 실패, {}ms 후 재시도: {}",
                        attempt, delay, e.getMessage());

                    Thread.sleep(delay);
                } else {
                    log.error("❌ 모든 시도 실패: {}/{}", attempt, maxAttempts);
                }
            }
        }

        throw lastException;
    }
}

// 3. 사용
@Service
public class ExternalApiService {

    @Retry(maxAttempts = 3, delay = 2000, retryFor = {IOException.class, TimeoutException.class})
    public String callExternalApi(String url) throws IOException {
        log.info("API 호출: {}", url);

        // 외부 API 호출 (실패 가능)
        RestTemplate restTemplate = new RestTemplate();
        return restTemplate.getForObject(url, String.class);
    }
}
```

**실행 결과 (실패 → 재시도 → 성공)**:
```
🔄 시도 1/3: callExternalApi
⚠️ 시도 1 실패, 2000ms 후 재시도: Connection timeout
🔄 시도 2/3: callExternalApi
⚠️ 시도 2 실패, 2000ms 후 재시도: Connection timeout
🔄 시도 3/3: callExternalApi
✅ 재시도 성공: 3번째 시도
```

---

### 실습 4: 트랜잭션 로깅 Aspect

**난이도**: ⭐⭐⭐⭐☆

```java
@Aspect
@Component
@Slf4j
public class TransactionLoggingAspect {

    @Before("@annotation(org.springframework.transaction.annotation.Transactional)")
    public void logTransactionStart(JoinPoint joinPoint) {
        String methodName = joinPoint.getSignature().toShortString();
        String transactionName = TransactionSynchronizationManager
            .getCurrentTransactionName();

        log.info("🔵 트랜잭션 시작: {} [{}]", methodName, transactionName);
        log.info("   - Active: {}", TransactionSynchronizationManager.isActualTransactionActive());
        log.info("   - ReadOnly: {}", TransactionSynchronizationManager.isCurrentTransactionReadOnly());
    }

    @AfterReturning("@annotation(org.springframework.transaction.annotation.Transactional)")
    public void logTransactionCommit(JoinPoint joinPoint) {
        String methodName = joinPoint.getSignature().toShortString();
        log.info("🟢 트랜잭션 커밋: {}", methodName);
    }

    @AfterThrowing(
        pointcut = "@annotation(org.springframework.transaction.annotation.Transactional)",
        throwing = "ex"
    )
    public void logTransactionRollback(JoinPoint joinPoint, Exception ex) {
        String methodName = joinPoint.getSignature().toShortString();
        log.error("🔴 트랜잭션 롤백: {} - {}", methodName, ex.getMessage());
    }
}

// 사용
@Service
public class OrderService {

    @Transactional
    public Order createOrder(OrderDto dto) {
        // 주문 생성 로직
        Order order = new Order(dto);
        orderRepository.save(order);

        // 재고 차감
        inventoryService.decreaseStock(dto.getProductId(), dto.getQuantity());

        return order;
    }
}
```

**실행 결과**:
```
🔵 트랜잭션 시작: OrderService.createOrder(..) [OrderService.createOrder]
   - Active: true
   - ReadOnly: false
🟢 트랜잭션 커밋: OrderService.createOrder(..)
```

---

### 실습 5: API 요청 제한 (Rate Limiting) Aspect

**난이도**: ⭐⭐⭐⭐⭐

```java
// 1. Rate Limit 어노테이션
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface RateLimit {
    int requests() default 10;  // 요청 수
    int period() default 60;     // 시간(초)
}

// 2. Aspect 구현
@Aspect
@Component
@Slf4j
public class RateLimitAspect {

    // 사용자별 요청 카운트 (실제로는 Redis 사용 권장)
    private final Map<String, Deque<Long>> requestCounts = new ConcurrentHashMap<>();

    @Around("@annotation(rateLimit)")
    public Object checkRateLimit(
        ProceedingJoinPoint joinPoint,
        RateLimit rateLimit
    ) throws Throwable {

        // 사용자 식별 (실제로는 SecurityContext에서 가져옴)
        String userId = getCurrentUserId();
        String key = userId + ":" + joinPoint.getSignature().getName();

        synchronized (this) {
            Deque<Long> timestamps = requestCounts.computeIfAbsent(
                key, k -> new LinkedList<>()
            );

            long now = System.currentTimeMillis();
            long periodMillis = rateLimit.period() * 1000L;

            // 오래된 기록 제거
            while (!timestamps.isEmpty() &&
                   now - timestamps.peekFirst() > periodMillis) {
                timestamps.pollFirst();
            }

            // 요청 제한 확인
            if (timestamps.size() >= rateLimit.requests()) {
                long oldestRequest = timestamps.peekFirst();
                long waitTime = periodMillis - (now - oldestRequest);

                log.warn("⛔ Rate Limit 초과: {} ({}초 후 재시도 가능)",
                    userId, waitTime / 1000);

                throw new RateLimitExceededException(
                    "요청 제한 초과. " + (waitTime / 1000) + "초 후 재시도하세요."
                );
            }

            // 현재 요청 기록
            timestamps.addLast(now);
        }

        return joinPoint.proceed();
    }

    private String getCurrentUserId() {
        // 실제로는 SecurityContextHolder에서 가져옴
        return "user-" + Thread.currentThread().getId();
    }
}

// 3. 사용
@RestController
@RequestMapping("/api/products")
public class ProductController {

    @GetMapping("/{id}")
    @RateLimit(requests = 5, period = 60)  // 1분에 5번
    public Product getProduct(@PathVariable Long id) {
        return productService.getProduct(id);
    }

    @PostMapping
    @RateLimit(requests = 3, period = 60)  // 1분에 3번
    public Product createProduct(@RequestBody ProductDto dto) {
        return productService.createProduct(dto);
    }
}
```

---

## 🏢 실무 활용 사례

### 사례 1: 네이버 - 통합 로깅 시스템

```java
// 사용 목적: 모든 API 호출 추적, 장애 원인 빠른 파악
// 규모: 초당 100만 요청
// 효과: 장애 원인 파악 시간 1시간 → 5분 (92% 단축)

@Aspect
@Component
@Slf4j
public class NaverApiLoggingAspect {

    @Around("@within(org.springframework.web.bind.annotation.RestController)")
    public Object logApiCall(ProceedingJoinPoint joinPoint) throws Throwable {

        HttpServletRequest request = getCurrentRequest();

        // 요청 ID 생성 (분산 추적용)
        String requestId = "REQ-" + UUID.randomUUID();
        MDC.put("requestId", requestId);

        // 요청 정보 로깅
        log.info("📥 API 요청: {} {} [{}]",
            request.getMethod(),
            request.getRequestURI(),
            requestId
        );
        log.info("   - IP: {}", request.getRemoteAddr());
        log.info("   - User-Agent: {}", request.getHeader("User-Agent"));
        log.info("   - 파라미터: {}", getParametersAsString(request));

        long start = System.currentTimeMillis();

        try {
            Object result = joinPoint.proceed();

            long duration = System.currentTimeMillis() - start;

            log.info("📤 API 응답: {} [{}]",
                request.getRequestURI(), requestId);
            log.info("   - 처리 시간: {}ms", duration);
            log.info("   - 상태: 성공");

            // 느린 API 경고
            if (duration > 1000) {
                log.warn("⚠️ 느린 API: {}ms [{}]", duration, requestId);
            }

            return result;

        } catch (Exception e) {
            long duration = System.currentTimeMillis() - start;

            log.error("❌ API 실패: {} [{}]",
                request.getRequestURI(), requestId);
            log.error("   - 처리 시간: {}ms", duration);
            log.error("   - 예외: {}", e.getClass().getSimpleName());
            log.error("   - 메시지: {}", e.getMessage());

            throw e;

        } finally {
            MDC.clear();
        }
    }

    private HttpServletRequest getCurrentRequest() {
        RequestAttributes attrs = RequestContextHolder.getRequestAttributes();
        return ((ServletRequestAttributes) attrs).getRequest();
    }

    private String getParametersAsString(HttpServletRequest request) {
        Map<String, String[]> params = request.getParameterMap();
        return params.entrySet().stream()
            .map(e -> e.getKey() + "=" + Arrays.toString(e.getValue()))
            .collect(Collectors.joining(", "));
    }
}

// 성과:
// - 모든 API 요청/응답 자동 로깅 (코드 수정 불필요)
// - 요청 ID로 분산 시스템 추적 가능
// - 장애 원인 파악 시간: 1시간 → 5분
// - 느린 API 자동 감지 및 알림
```

### 사례 2: 카카오 - 성능 모니터링

```java
// 사용 목적: 실시간 성능 모니터링, 병목 지점 자동 감지
// 규모: 1,000개 서비스, 10,000개 메서드
// 효과: 성능 병목 자동 감지, 최적화 우선순위 데이터 기반 결정

@Aspect
@Component
@Slf4j
public class PerformanceMonitoringAspect {

    @Autowired
    private MetricsRegistry metricsRegistry;  // Prometheus 등

    @Around("execution(* com.kakao.service..*.*(..))")
    public Object monitorPerformance(ProceedingJoinPoint joinPoint) throws Throwable {

        String className = joinPoint.getTarget().getClass().getSimpleName();
        String methodName = joinPoint.getSignature().getName();
        String metricName = className + "." + methodName;

        Timer.Sample sample = Timer.start();

        try {
            Object result = joinPoint.proceed();

            // 성공 메트릭 기록
            sample.stop(metricsRegistry.timer(
                "method.execution.time",
                "class", className,
                "method", methodName,
                "status", "success"
            ));

            return result;

        } catch (Exception e) {
            // 실패 메트릭 기록
            sample.stop(metricsRegistry.timer(
                "method.execution.time",
                "class", className,
                "method", methodName,
                "status", "failure"
            ));

            // 예외 카운트
            metricsRegistry.counter(
                "method.exception.count",
                "class", className,
                "method", methodName,
                "exception", e.getClass().getSimpleName()
            ).increment();

            throw e;
        }
    }
}

// Grafana 대시보드에서 실시간 모니터링:
// - 메서드별 평균 실행 시간
// - 메서드별 호출 빈도
// - 메서드별 에러율
// - P95, P99 응답 시간

// 성과:
// - 성능 병목 자동 감지 (P95 > 1초인 메서드 알림)
// - 최적화 우선순위 결정 (호출 빈도 × 실행 시간)
// - 성능 개선 효과 실시간 확인
```

### 사례 3: 쿠팡 - 분산 트랜잭션 로깅

```java
// 사용 목적: 마이크로서비스 간 트랜잭션 추적
// 규모: 50개 마이크로서비스
// 효과: 분산 트랜잭션 디버깅 시간 80% 단축

@Aspect
@Component
@Slf4j
public class DistributedTransactionAspect {

    @Around("@annotation(org.springframework.transaction.annotation.Transactional)")
    public Object logDistributedTransaction(ProceedingJoinPoint joinPoint) throws Throwable {

        String serviceName = System.getProperty("spring.application.name");
        String transactionId = MDC.get("transactionId");

        if (transactionId == null) {
            // 새 트랜잭션 시작
            transactionId = "TXN-" + UUID.randomUUID();
            MDC.put("transactionId", transactionId);
        }

        String methodName = joinPoint.getSignature().toShortString();

        log.info("🔹 [{}] 트랜잭션 시작: {} in {}",
            transactionId, methodName, serviceName);

        long start = System.currentTimeMillis();

        try {
            Object result = joinPoint.proceed();

            long duration = System.currentTimeMillis() - start;

            log.info("🔹 [{}] 트랜잭션 커밋: {} ({}ms)",
                transactionId, methodName, duration);

            // 분산 추적 시스템에 기록 (Zipkin, Jaeger 등)
            recordDistributedTrace(transactionId, serviceName, methodName, duration, true);

            return result;

        } catch (Exception e) {
            long duration = System.currentTimeMillis() - start;

            log.error("🔻 [{}] 트랜잭션 롤백: {} ({}ms) - {}",
                transactionId, methodName, duration, e.getMessage());

            recordDistributedTrace(transactionId, serviceName, methodName, duration, false);

            throw e;
        }
    }

    private void recordDistributedTrace(
        String transactionId,
        String serviceName,
        String methodName,
        long duration,
        boolean success
    ) {
        // Zipkin, Jaeger 등 분산 추적 시스템에 전송
        Span span = Span.builder()
            .traceId(transactionId)
            .serviceName(serviceName)
            .operationName(methodName)
            .duration(duration)
            .status(success ? "SUCCESS" : "FAILURE")
            .build();

        tracingSystem.report(span);
    }
}

// 성과:
// - 마이크로서비스 간 트랜잭션 흐름 시각화
// - 장애 발생 시 전체 흐름 추적 가능
// - 디버깅 시간: 2시간 → 20분 (80% 단축)
```

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: @Around에서 proceed() 호출 누락

**상황**: 신입 개발자가 @Around Aspect를 작성했는데 메서드가 실행되지 않는 버그 발생

```java
// ❌ 주니어 개발자가 작성한 코드
@Aspect
@Component
@Slf4j
public class LoggingAspect {

    @Around("execution(* com.example.service.*.*(..))")
    public Object logMethod(ProceedingJoinPoint joinPoint) throws Throwable {
        String methodName = joinPoint.getSignature().getName();

        log.info("메서드 시작: {}", methodName);

        // ⚠️ proceed() 호출을 깜빡함!

        log.info("메서드 종료: {}", methodName);

        return null;  // ❌ 항상 null 반환!
    }
}

// 사용
@Service
public class UserService {

    public User createUser(UserDto dto) {
        User user = new User(dto);
        userRepository.save(user);
        return user;  // ⚠️ 이 user가 반환되지 않음!
    }
}
```

**문제점**:
- **메서드 미실행**: proceed()를 호출하지 않아서 실제 비즈니스 로직이 실행되지 않음
- **null 반환**: 반환값이 항상 null이 되어 NullPointerException 발생
- **데이터 미저장**: userRepository.save()가 실행되지 않아 DB에 저장 안 됨
- **로그 오류**: 실제로는 실행되지 않았는데 "메서드 종료" 로그 출력

**장애 상황**:
```
[장애 발생]
- 증상: 회원가입이 되지 않음, API는 200 OK 반환하지만 DB에 데이터 없음
- 에러: java.lang.NullPointerException at UserController.createUser
- 원인: UserService.createUser()가 null을 반환
- 영향: 30분간 회원가입 불가, 사용자 이탈률 20% 증가
```

**해결책**:
```java
// ✅ 올바른 코드
@Aspect
@Component
@Slf4j
public class LoggingAspect {

    @Around("execution(* com.example.service.*.*(..))")
    public Object logMethod(ProceedingJoinPoint joinPoint) throws Throwable {
        String methodName = joinPoint.getSignature().getName();

        log.info("메서드 시작: {}", methodName);

        long start = System.currentTimeMillis();

        try {
            // ✅ 반드시 proceed() 호출!
            Object result = joinPoint.proceed();

            long duration = System.currentTimeMillis() - start;
            log.info("메서드 종료: {} ({}ms)", methodName, duration);

            // ✅ 실제 반환값 반환!
            return result;

        } catch (Exception e) {
            long duration = System.currentTimeMillis() - start;
            log.error("메서드 실패: {} ({}ms)", methodName, duration, e);
            throw e;
        }
    }
}

// 검증 테스트
@SpringBootTest
public class LoggingAspectTest {

    @Autowired
    private UserService userService;

    @Test
    public void testProceedCalled() {
        User user = userService.createUser(new UserDto("test@example.com"));

        assertNotNull(user);  // ✅ null이 아님
        assertEquals("test@example.com", user.getEmail());
    }
}
```

**배운 점**:
- 💡 **@Around는 proceed() 필수**: 이 한 줄이 없으면 메서드가 실행되지 않음
- 💡 **반환값 전달**: proceed()의 반환값을 그대로 반환해야 함
- 💡 **예외 처리**: proceed()는 Throwable을 던지므로 try-catch 필수
- 💡 **테스트 작성**: AOP 로직도 반드시 테스트 코드 작성

---

### 시나리오 2: 같은 클래스 내부 호출로 AOP 미적용

**상황**: @Transactional을 적용했는데 트랜잭션이 동작하지 않는 문제 발생

```java
// ❌ 주니어 개발자가 작성한 코드
@Service
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private InventoryService inventoryService;

    // 외부에서 호출하는 메서드
    public void processOrder(OrderDto dto) {
        log.info("주문 처리 시작");

        // ⚠️ 같은 클래스의 메서드를 직접 호출
        createOrder(dto);  // this.createOrder(dto)와 동일
    }

    @Transactional  // ❌ AOP 적용 안 됨!
    public void createOrder(OrderDto dto) {
        // 주문 생성
        Order order = new Order(dto);
        orderRepository.save(order);

        // 재고 차감
        inventoryService.decreaseStock(dto.getProductId(), dto.getQuantity());

        // ⚠️ 예외 발생 시 롤백 안 됨!
        if (order.getTotalPrice() > 1000000) {
            throw new IllegalArgumentException("주문 금액 초과");
        }
    }
}
```

**문제점**:
- **Proxy 우회**: 같은 클래스 내부 호출은 this로 호출되어 Proxy를 거치지 않음
- **트랜잭션 미적용**: @Transactional이 있어도 트랜잭션이 시작되지 않음
- **롤백 실패**: 예외 발생 시 DB에 이미 저장된 데이터가 롤백되지 않음
- **데이터 불일치**: 주문은 생성되었는데 재고는 차감되지 않는 상황 발생

**장애 상황**:
```
[장애 발생]
- 증상: 주문 금액이 100만원 초과 시 에러 발생하지만 DB에는 주문 데이터 남음
- 원인: @Transactional이 적용되지 않아 롤백 안 됨
- 영향: 고액 주문 10건이 잘못 저장됨, 수동으로 데이터 정리 필요
- 비용: 데이터 정리에 3시간 소요
```

**해결책 1: Bean 분리 (권장)**:
```java
// ✅ 별도 Bean으로 분리
@Service
public class OrderService {

    @Autowired
    private OrderInternalService internalService;

    public void processOrder(OrderDto dto) {
        log.info("주문 처리 시작");

        // ✅ 다른 Bean의 메서드 호출 → Proxy 통과!
        internalService.createOrder(dto);
    }
}

@Service
public class OrderInternalService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private InventoryService inventoryService;

    @Transactional  // ✅ AOP 적용됨!
    public void createOrder(OrderDto dto) {
        Order order = new Order(dto);
        orderRepository.save(order);

        inventoryService.decreaseStock(dto.getProductId(), dto.getQuantity());

        if (order.getTotalPrice() > 1000000) {
            throw new IllegalArgumentException("주문 금액 초과");
        }
        // ✅ 예외 발생 시 전체 롤백!
    }
}
```

**해결책 2: Self-Injection (비권장)**:
```java
// ⚠️ 가능하지만 권장하지 않음
@Service
public class OrderService {

    @Autowired
    private OrderService self;  // 자기 자신을 주입

    public void processOrder(OrderDto dto) {
        log.info("주문 처리 시작");

        // Proxy를 통한 호출
        self.createOrder(dto);
    }

    @Transactional
    public void createOrder(OrderDto dto) {
        // 트랜잭션 적용됨
    }
}
```

**배운 점**:
- 💡 **내부 호출 금지**: 같은 클래스의 메서드를 호출하면 AOP 적용 안 됨
- 💡 **Proxy 이해**: Spring AOP는 Proxy 패턴 기반, this 호출은 Proxy 우회
- 💡 **Bean 분리**: 기능을 별도 Bean으로 분리하는 것이 가장 깔끔한 해결책
- 💡 **테스트로 검증**: 트랜잭션이 실제로 동작하는지 테스트 필수

---

### 시나리오 3: Private 메서드에 AOP 적용 시도

**상황**: Private 메서드에 @PerformanceLog를 붙였는데 성능 측정이 안 되는 문제

```java
// ❌ 주니어 개발자가 작성한 코드
@Service
public class ProductService {

    @Autowired
    private ProductRepository productRepository;

    public List<Product> searchProducts(String keyword) {
        log.info("상품 검색: {}", keyword);

        // Private 메서드 호출
        return filterProducts(keyword);
    }

    @PerformanceLog  // ❌ Private 메서드는 AOP 적용 안 됨!
    private List<Product> filterProducts(String keyword) {
        // 복잡한 필터링 로직 (성능 측정 필요)
        List<Product> allProducts = productRepository.findAll();

        return allProducts.stream()
            .filter(p -> p.getName().contains(keyword))
            .filter(p -> p.getStock() > 0)
            .sorted(Comparator.comparing(Product::getPrice))
            .collect(Collectors.toList());
    }
}
```

**문제점**:
- **Proxy 한계**: CGLIB Proxy는 public 메서드만 Override 가능
- **성능 측정 실패**: Private 메서드는 Aspect가 적용되지 않음
- **잘못된 가정**: "어노테이션만 붙이면 동작한다"는 착각
- **디버깅 어려움**: 에러도 발생하지 않아서 왜 안 되는지 모름

**현상**:
```
[문제 확인]
- @PerformanceLog 붙였지만 로그 출력 안 됨
- 성능 측정 필요한데 측정 결과가 보이지 않음
- 에러 메시지도 없어서 원인 파악 어려움
```

**해결책 1: Public으로 변경**:
```java
// ✅ Public으로 변경
@Service
public class ProductService {

    public List<Product> searchProducts(String keyword) {
        log.info("상품 검색: {}", keyword);
        return filterProducts(keyword);
    }

    @PerformanceLog  // ✅ AOP 적용됨!
    public List<Product> filterProducts(String keyword) {
        List<Product> allProducts = productRepository.findAll();

        return allProducts.stream()
            .filter(p -> p.getName().contains(keyword))
            .filter(p -> p.getStock() > 0)
            .sorted(Comparator.comparing(Product::getPrice))
            .collect(Collectors.toList());
    }
}
```

**해결책 2: 별도 Bean으로 분리 (더 나은 방법)**:
```java
// ✅ 책임 분리 + AOP 적용
@Service
public class ProductService {

    @Autowired
    private ProductFilterService filterService;

    public List<Product> searchProducts(String keyword) {
        log.info("상품 검색: {}", keyword);
        return filterService.filterProducts(keyword);  // ✅ Bean 호출
    }
}

@Service
public class ProductFilterService {

    @Autowired
    private ProductRepository productRepository;

    @PerformanceLog  // ✅ AOP 적용됨!
    public List<Product> filterProducts(String keyword) {
        List<Product> allProducts = productRepository.findAll();

        return allProducts.stream()
            .filter(p -> p.getName().contains(keyword))
            .filter(p -> p.getStock() > 0)
            .sorted(Comparator.comparing(Product::getPrice))
            .collect(Collectors.toList());
    }
}
```

**배운 점**:
- 💡 **Public만 가능**: Spring AOP는 public 메서드에만 적용됨
- 💡 **Proxy 원리**: Proxy는 상속 기반이라 private는 Override 불가
- 💡 **설계 개선 기회**: Private 메서드가 복잡하다면 별도 Bean으로 분리 검토
- 💡 **AspectJ 대안**: 컴파일 타임 위빙을 사용하면 private도 가능하지만 복잡함

---

### 시나리오 4: Pointcut 표현식 실수로 의도하지 않은 메서드에 AOP 적용

**상황**: 모든 Service의 메서드에만 로깅을 적용하려 했는데 Controller에도 적용됨

```java
// ❌ 주니어 개발자가 작성한 코드
@Aspect
@Component
@Slf4j
public class ServiceLoggingAspect {

    // ⚠️ 잘못된 Pointcut 표현식
    @Around("execution(* com.example.*.*(..))")
    public Object logServiceMethod(ProceedingJoinPoint joinPoint) throws Throwable {
        log.info("========================================");
        log.info("메서드 시작: {}", joinPoint.getSignature());
        log.info("파라미터: {}", Arrays.toString(joinPoint.getArgs()));

        Object result = joinPoint.proceed();

        log.info("반환값: {}", result);
        log.info("메서드 종료");
        log.info("========================================");

        return result;
    }
}
```

**문제점**:
- **범위 과다**: `com.example.*.*`는 service뿐만 아니라 controller, repository도 포함
- **성능 저하**: Controller의 모든 요청마다 상세 로그 출력으로 로그 파일 크기 폭증
- **민감 정보 노출**: 파라미터와 반환값을 모두 로깅하여 비밀번호, 개인정보 노출
- **로그 과다**: 하루 로그 파일이 10MB → 1GB로 증가

**장애 상황**:
```
[문제 발생]
- 로그 파일 크기: 10MB → 1GB (100배 증가)
- 디스크 공간 부족 경고
- 로그에 사용자 비밀번호 평문 노출 (보안 사고!)
- 로그 검색 속도 느려짐 (10초 → 5분)
```

**해결책 1: Pointcut 표현식 정확히 지정**:
```java
// ✅ 올바른 코드 - 패키지 정확히 지정
@Aspect
@Component
@Slf4j
public class ServiceLoggingAspect {

    // ✅ service 패키지만 지정
    @Around("execution(* com.example.service.*.*(..))")
    public Object logServiceMethod(ProceedingJoinPoint joinPoint) throws Throwable {
        log.info("Service 메서드 시작: {}", joinPoint.getSignature().getName());

        Object result = joinPoint.proceed();

        log.info("Service 메서드 종료");

        return result;
    }
}
```

**해결책 2: 어노테이션 기반 Pointcut (더 안전)**:
```java
// ✅ 커스텀 어노테이션 정의
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface DetailedLog {
}

// ✅ 어노테이션이 붙은 메서드에만 적용
@Aspect
@Component
@Slf4j
public class DetailedLoggingAspect {

    @Around("@annotation(DetailedLog)")
    public Object logDetailedMethod(ProceedingJoinPoint joinPoint) throws Throwable {
        log.info("========================================");
        log.info("메서드 시작: {}", joinPoint.getSignature());

        // 민감 정보 마스킹
        Object[] args = maskSensitiveData(joinPoint.getArgs());
        log.info("파라미터: {}", Arrays.toString(args));

        Object result = joinPoint.proceed();

        Object maskedResult = maskSensitiveData(result);
        log.info("반환값: {}", maskedResult);
        log.info("========================================");

        return result;
    }

    private Object[] maskSensitiveData(Object[] args) {
        // 비밀번호, 카드번호 등 마스킹 처리
        return Arrays.stream(args)
            .map(arg -> {
                if (arg instanceof UserDto) {
                    UserDto dto = (UserDto) arg;
                    dto.setPassword("***");  // 비밀번호 마스킹
                }
                return arg;
            })
            .toArray();
    }
}

// 사용 - 필요한 메서드에만 명시적으로 적용
@Service
public class UserService {

    @DetailedLog  // ✅ 명시적으로 상세 로깅 적용
    public User register(UserDto dto) {
        // 회원가입 로직 (디버깅 필요)
    }

    // 일반 메서드는 상세 로깅 안 됨
    public User getUser(Long id) {
        return userRepository.findById(id).orElse(null);
    }
}
```

**해결책 3: Pointcut 재사용 및 조합**:
```java
// ✅ Pointcut 정의 및 조합
@Aspect
@Component
@Slf4j
public class LoggingAspect {

    // Service 계층
    @Pointcut("within(com.example.service..*)")
    public void serviceLayer() {}

    // Public 메서드만
    @Pointcut("execution(public * *(..))")
    public void publicMethod() {}

    // 조합: Service 계층의 Public 메서드
    @Around("serviceLayer() && publicMethod()")
    public Object logServiceMethod(ProceedingJoinPoint joinPoint) throws Throwable {
        log.info("Service 호출: {}", joinPoint.getSignature().getName());

        Object result = joinPoint.proceed();

        return result;
    }
}
```

**배운 점**:
- 💡 **Pointcut 표현식 주의**: `*.*`는 생각보다 많은 범위를 포함
- 💡 **어노테이션 기반 권장**: 명시적이고 실수 방지
- 💡 **보안 고려**: 로그에 민감 정보 노출 금지, 마스킹 필수
- 💡 **테스트 필수**: Pointcut이 의도한 메서드에만 적용되는지 검증

---

## 🛠️ 실전 프로젝트

### 프로젝트: API 성능 모니터링 시스템

**난이도**: ⭐⭐⭐⭐☆
**예상 소요 시간**: 4-5시간
**학습 목표**: @Aspect, @Around, Pointcut 표현식, MDC를 활용한 실전 모니터링 시스템 구축

---

### 📋 요구사항 분석

#### 기능 요구사항
- [ ] **API 실행 시간 자동 측정**: 모든 REST API의 응답 시간 기록
- [ ] **느린 API 자동 경고**: 3초 이상 소요되는 API 자동 탐지 및 경고
- [ ] **요청/응답 로깅**: HTTP 메서드, URI, 파라미터, 상태 코드 기록
- [ ] **예외 자동 알림**: API 에러 발생 시 슬랙 또는 이메일 알림
- [ ] **통계 수집**: 일별/시간별 API 호출 통계

#### 기술 요구사항
- [ ] **@Aspect**: AOP 기반 모니터링
- [ ] **MDC (Mapped Diagnostic Context)**: 요청별 추적 ID 관리
- [ ] **@Around**: API 실행 전후 제어
- [ ] **Micrometer**: 메트릭 수집 및 Prometheus 연동

#### 비기능 요구사항
- [ ] **성능 오버헤드 최소화**: 모니터링으로 인한 성능 저하 < 5%
- [ ] **확장성**: 새로운 API 추가 시 코드 수정 불필요
- [ ] **가독성**: 로그를 보고 빠르게 문제 파악 가능

---

### 🏗️ 프로젝트 구조

```
api-monitoring-system/
├── src/main/java/com/example/monitoring/
│   ├── MonitoringApplication.java
│   ├── aspect/
│   │   ├── ApiMonitoringAspect.java           # API 모니터링 Aspect
│   │   ├── PerformanceMonitoringAspect.java   # 성능 측정 Aspect
│   │   └── ExceptionNotificationAspect.java   # 예외 알림 Aspect
│   ├── annotation/
│   │   ├── ApiMonitoring.java                 # 모니터링 적용 어노테이션
│   │   └── SlowApiThreshold.java              # 느린 API 임계값 지정
│   ├── service/
│   │   ├── SlackNotificationService.java      # 슬랙 알림 서비스
│   │   └── MetricsCollectionService.java      # 메트릭 수집 서비스
│   ├── controller/
│   │   └── ProductController.java             # 테스트용 API
│   └── config/
│       └── MonitoringConfig.java              # AOP 설정
└── src/test/java/com/example/monitoring/
    └── aspect/
        └── ApiMonitoringAspectTest.java        # 테스트
```

---

### 🎯 설계 의사결정

#### 결정 1: @Around vs @Before + @After
**선택**: @Around
**이유**: 실행 시간 측정 시 시작과 종료 시점을 모두 제어해야 하므로
**대안**: @Before로 시작 시간 기록, @After로 종료 시간 계산 (복잡함)

#### 결정 2: 모든 API vs 어노테이션 기반
**선택**: 모든 RestController에 자동 적용 + 선택적 커스터마이징
**이유**: 신규 API 추가 시 자동 적용, 특수한 경우만 어노테이션으로 커스터마이징
**대안**: 모든 API에 어노테이션 붙이기 (번거로움)

#### 결정 3: 동기 vs 비동기 알림
**선택**: 비동기 알림 (@Async)
**이유**: 슬랙 알림 전송으로 인한 API 응답 지연 방지
**대안**: 동기 알림 (API 응답 시간 증가)

---

### 🔨 단계별 구현 가이드

#### 1단계: 프로젝트 초기 설정

```bash
# Spring Boot 프로젝트 생성
# Dependencies: Spring Web, Spring AOP, Spring Actuator, Micrometer

# build.gradle 추가 의존성
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-aop'
    implementation 'org.springframework.boot:spring-boot-starter-actuator'
    implementation 'io.micrometer:micrometer-registry-prometheus'
    implementation 'com.slack.api:slack-api-client:1.29.2'
}
```

---

#### 2단계: 커스텀 어노테이션 정의

```java
// 파일: annotation/ApiMonitoring.java
package com.example.monitoring.annotation;

import java.lang.annotation.*;

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface ApiMonitoring {

    /**
     * API 설명 (모니터링 로그에 표시)
     */
    String description() default "";

    /**
     * 느린 API 임계값 (ms)
     */
    long slowThreshold() default 3000;

    /**
     * 에러 발생 시 슬랙 알림 여부
     */
    boolean notifyOnError() default true;
}

// 파일: annotation/SlowApiThreshold.java
package com.example.monitoring.annotation;

import java.lang.annotation.*;

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface SlowApiThreshold {
    long value() default 3000;  // ms
}
```

---

#### 3단계: API 모니터링 Aspect 구현

```java
// 파일: aspect/ApiMonitoringAspect.java
package com.example.monitoring.aspect;

import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.slf4j.MDC;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import javax.servlet.http.HttpServletRequest;
import java.util.UUID;

@Aspect
@Component
@Slf4j
public class ApiMonitoringAspect {

    @Around("@within(org.springframework.web.bind.annotation.RestController)")
    public Object monitorApi(ProceedingJoinPoint joinPoint) throws Throwable {

        HttpServletRequest request = getCurrentRequest();

        // 요청 ID 생성 (분산 추적용)
        String requestId = "REQ-" + UUID.randomUUID().toString().substring(0, 8);
        MDC.put("requestId", requestId);

        String method = request.getMethod();
        String uri = request.getRequestURI();
        String clientIp = getClientIp(request);

        log.info("┌──────────────────────────────────────");
        log.info("│ 📥 API 요청 [{}]", requestId);
        log.info("│ HTTP Method: {}", method);
        log.info("│ URI: {}", uri);
        log.info("│ Client IP: {}", clientIp);
        log.info("│ User-Agent: {}", request.getHeader("User-Agent"));

        long startTime = System.currentTimeMillis();

        try {
            Object result = joinPoint.proceed();

            long duration = System.currentTimeMillis() - startTime;

            log.info("│ 📤 API 응답 [{}]", requestId);
            log.info("│ 처리 시간: {}ms", duration);
            log.info("│ 상태: ✅ 성공");

            // 느린 API 경고
            if (duration > 3000) {
                log.warn("│ ⚠️  느린 API 감지: {}ms", duration);
            }

            log.info("└──────────────────────────────────────");

            return result;

        } catch (Exception e) {
            long duration = System.currentTimeMillis() - startTime;

            log.error("│ ❌ API 실패 [{}]", requestId);
            log.error("│ 처리 시간: {}ms", duration);
            log.error("│ 예외: {}", e.getClass().getSimpleName());
            log.error("│ 메시지: {}", e.getMessage());
            log.error("└──────────────────────────────────────");

            throw e;

        } finally {
            MDC.clear();
        }
    }

    private HttpServletRequest getCurrentRequest() {
        ServletRequestAttributes attrs =
            (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        return attrs.getRequest();
    }

    private String getClientIp(HttpServletRequest request) {
        String ip = request.getHeader("X-Forwarded-For");
        if (ip == null || ip.isEmpty()) {
            ip = request.getRemoteAddr();
        }
        return ip;
    }
}
```

---

#### 4단계: 성능 메트릭 수집 Aspect

```java
// 파일: aspect/PerformanceMonitoringAspect.java
package com.example.monitoring.aspect;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.springframework.stereotype.Component;
import org.springframework.web.bind.annotation.*;

import java.lang.reflect.Method;

@Aspect
@Component
@Slf4j
@RequiredArgsConstructor
public class PerformanceMonitoringAspect {

    private final MeterRegistry meterRegistry;

    @Around("@within(org.springframework.web.bind.annotation.RestController)")
    public Object collectMetrics(ProceedingJoinPoint joinPoint) throws Throwable {

        String className = joinPoint.getTarget().getClass().getSimpleName();
        String methodName = joinPoint.getSignature().getName();
        String httpMethod = getHttpMethod(joinPoint);

        Timer.Sample sample = Timer.start(meterRegistry);
        String status = "success";

        try {
            Object result = joinPoint.proceed();
            return result;

        } catch (Exception e) {
            status = "failure";

            // 예외 카운트
            meterRegistry.counter(
                "api.exception.count",
                "class", className,
                "method", methodName,
                "exception", e.getClass().getSimpleName()
            ).increment();

            throw e;

        } finally {
            // 실행 시간 기록
            sample.stop(meterRegistry.timer(
                "api.execution.time",
                "class", className,
                "method", methodName,
                "http_method", httpMethod,
                "status", status
            ));
        }
    }

    private String getHttpMethod(ProceedingJoinPoint joinPoint) {
        Method method = ((MethodSignature) joinPoint.getSignature()).getMethod();

        if (method.isAnnotationPresent(GetMapping.class)) return "GET";
        if (method.isAnnotationPresent(PostMapping.class)) return "POST";
        if (method.isAnnotationPresent(PutMapping.class)) return "PUT";
        if (method.isAnnotationPresent(DeleteMapping.class)) return "DELETE";
        if (method.isAnnotationPresent(PatchMapping.class)) return "PATCH";

        return "UNKNOWN";
    }
}
```

---

#### 5단계: 예외 알림 Aspect (Slack 연동)

```java
// 파일: aspect/ExceptionNotificationAspect.java
package com.example.monitoring.aspect;

import com.example.monitoring.service.SlackNotificationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.annotation.AfterThrowing;
import org.aspectj.lang.annotation.Aspect;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import javax.servlet.http.HttpServletRequest;
import java.time.LocalDateTime;

@Aspect
@Component
@Slf4j
@RequiredArgsConstructor
public class ExceptionNotificationAspect {

    private final SlackNotificationService slackService;

    @AfterThrowing(
        pointcut = "@within(org.springframework.web.bind.annotation.RestController)",
        throwing = "ex"
    )
    @Async
    public void notifyOnException(Exception ex) {
        HttpServletRequest request = getCurrentRequest();

        String message = buildErrorMessage(request, ex);

        log.info("예외 알림 전송 시작: {}", ex.getClass().getSimpleName());

        // 비동기로 슬랙 알림 전송
        slackService.sendAlert(message);
    }

    private String buildErrorMessage(HttpServletRequest request, Exception ex) {
        return String.format(
            "🚨 *API 에러 발생*\n" +
            "• 시간: %s\n" +
            "• URI: %s %s\n" +
            "• 예외: %s\n" +
            "• 메시지: %s\n" +
            "• Client IP: %s",
            LocalDateTime.now(),
            request.getMethod(),
            request.getRequestURI(),
            ex.getClass().getSimpleName(),
            ex.getMessage(),
            request.getRemoteAddr()
        );
    }

    private HttpServletRequest getCurrentRequest() {
        ServletRequestAttributes attrs =
            (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        return attrs.getRequest();
    }
}

// 파일: service/SlackNotificationService.java
package com.example.monitoring.service;

import com.slack.api.Slack;
import com.slack.api.methods.MethodsClient;
import com.slack.api.methods.request.chat.ChatPostMessageRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
@Slf4j
public class SlackNotificationService {

    @Value("${slack.webhook.url:}")
    private String webhookUrl;

    @Value("${slack.channel:#alerts}")
    private String channel;

    public void sendAlert(String message) {
        try {
            // 실제로는 Slack API 호출
            log.info("📢 Slack 알림 전송: {}", message);

            // Slack Webhook 또는 API 사용
            // slack.methods().chatPostMessage(request);

        } catch (Exception e) {
            log.error("Slack 알림 전송 실패", e);
        }
    }
}
```

---

#### 6단계: 테스트용 API Controller

```java
// 파일: controller/ProductController.java
package com.example.monitoring.controller;

import com.example.monitoring.annotation.SlowApiThreshold;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/products")
@Slf4j
public class ProductController {

    @GetMapping
    public List<Product> getAllProducts() {
        log.info("전체 상품 조회");
        return List.of(
            new Product(1L, "노트북", 1500000),
            new Product(2L, "마우스", 30000)
        );
    }

    @GetMapping("/{id}")
    public Product getProduct(@PathVariable Long id) throws InterruptedException {
        log.info("상품 조회: {}", id);

        // 인위적인 지연 (느린 API 테스트)
        Thread.sleep(2000);

        return new Product(id, "상품-" + id, 100000);
    }

    @GetMapping("/slow")
    @SlowApiThreshold(5000)  // 5초 이상 시 경고
    public String slowApi() throws InterruptedException {
        // 느린 API 시뮬레이션
        Thread.sleep(4000);
        return "Slow response";
    }

    @PostMapping
    public Product createProduct(@RequestBody Product product) {
        log.info("상품 생성: {}", product);
        return product;
    }

    @GetMapping("/error")
    public void errorApi() {
        // 의도적 에러 (예외 알림 테스트)
        throw new IllegalArgumentException("테스트 에러 발생!");
    }
}

@Data
@AllArgsConstructor
class Product {
    private Long id;
    private String name;
    private Integer price;
}
```

---

#### 7단계: AOP 설정 및 비동기 활성화

```java
// 파일: config/MonitoringConfig.java
package com.example.monitoring.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.EnableAspectJAutoProxy;
import org.springframework.scheduling.annotation.EnableAsync;

@Configuration
@EnableAspectJAutoProxy
@EnableAsync
public class MonitoringConfig {
}

// application.yml
management:
  endpoints:
    web:
      exposure:
        include: prometheus,metrics,health
  metrics:
    export:
      prometheus:
        enabled: true

slack:
  webhook:
    url: ${SLACK_WEBHOOK_URL:}
  channel: "#api-alerts"

logging:
  level:
    com.example.monitoring: DEBUG
```

---

### 🎬 실행 및 검증

```bash
# 애플리케이션 실행
./gradlew bootRun

# API 호출 테스트
curl http://localhost:8080/api/products

# 느린 API 테스트
curl http://localhost:8080/api/products/1

# 에러 API 테스트
curl http://localhost:8080/api/products/error

# Prometheus 메트릭 확인
curl http://localhost:8080/actuator/prometheus | grep api_execution_time
```

**로그 출력 예시**:
```
┌──────────────────────────────────────
│ 📥 API 요청 [REQ-a3b4c5d6]
│ HTTP Method: GET
│ URI: /api/products/1
│ Client IP: 127.0.0.1
│ User-Agent: curl/7.68.0
│ 📤 API 응답 [REQ-a3b4c5d6]
│ 처리 시간: 2045ms
│ 상태: ✅ 성공
└──────────────────────────────────────

┌──────────────────────────────────────
│ 📥 API 요청 [REQ-e7f8g9h0]
│ HTTP Method: GET
│ URI: /api/products/error
│ ❌ API 실패 [REQ-e7f8g9h0]
│ 처리 시간: 12ms
│ 예외: IllegalArgumentException
│ 메시지: 테스트 에러 발생!
└──────────────────────────────────────

📢 Slack 알림 전송: 🚨 *API 에러 발생*...
```

---

### 🐛 트러블슈팅

#### 문제 1: MDC 값이 다른 스레드에서 사라짐

**증상**: 비동기 메서드에서 requestId가 null
**원인**: MDC는 ThreadLocal 기반이라 스레드 변경 시 사라짐
**해결**: TaskDecorator로 MDC 전파

```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setTaskDecorator(new MdcTaskDecorator());
        executor.initialize();
        return executor;
    }
}

public class MdcTaskDecorator implements TaskDecorator {
    @Override
    public Runnable decorate(Runnable runnable) {
        Map<String, String> contextMap = MDC.getCopyOfContextMap();
        return () -> {
            MDC.setContextMap(contextMap);
            try {
                runnable.run();
            } finally {
                MDC.clear();
            }
        };
    }
}
```

---

### 💡 확장 아이디어

#### 추가 기능 1: Grafana 대시보드 연동
**난이도**: ⭐⭐⭐⭐☆
**구현 힌트**: Prometheus + Grafana로 실시간 모니터링 대시보드 구축

#### 추가 기능 2: API 호출 통계 저장
**난이도**: ⭐⭐⭐☆☆
**구현 힌트**: Spring Batch로 일별 통계 집계 및 DB 저장

---

### ✅ 코드 리뷰 체크리스트

#### AOP 구현
- [ ] @Around에서 proceed() 호출 확인
- [ ] 예외 발생 시 반드시 throw
- [ ] Pointcut 표현식 정확성 확인

#### 성능
- [ ] 모니터링 오버헤드 < 5%
- [ ] 비동기 알림 사용으로 응답 시간 영향 최소화

#### 보안
- [ ] 로그에 비밀번호, 토큰 등 민감 정보 마스킹
- [ ] 개인정보 로깅 시 암호화 또는 일부만 표시

---

### 🎓 프로젝트에서 배운 핵심 개념

1. **@Aspect + @Around 조합**: 실행 시간 측정, 로깅의 표준 패턴
2. **MDC 활용**: 분산 시스템에서 요청 추적의 핵심 기술
3. **비동기 처리**: 외부 API 호출(슬랙) 시 응답 시간 영향 최소화
4. **Micrometer + Prometheus**: 메트릭 수집 및 모니터링 표준
5. **Pointcut 재사용**: @Pointcut으로 정의 후 여러 Advice에서 참조

---

## ❓ FAQ

<details>
<summary><strong>Q1: @Before와 @Around의 차이는 무엇인가요?</strong></summary>

**A**: **@Around가 더 강력하지만 @Before가 더 단순합니다.**

```java
// @Before: 메서드 실행 전에만 동작
@Before("execution(* com.example.service.*.*(..))")
public void logBefore(JoinPoint joinPoint) {
    log.info("시작: {}", joinPoint.getSignature().getName());
    // proceed() 호출 불필요
    // 반환값 수정 불가
    // 메서드 실행 막을 수 없음
}

// @Around: 전후 제어 가능
@Around("execution(* com.example.service.*.*(..))")
public Object logAround(ProceedingJoinPoint joinPoint) throws Throwable {
    log.info("시작");

    Object result = joinPoint.proceed();  // 실행 제어 가능

    log.info("종료");
    return result;  // 반환값 수정 가능
}
```

**선택 기준**:
- 단순 로깅: @Before/@After
- 성능 측정, 트랜잭션: @Around

</details>

<details>
<summary><strong>Q2: Pointcut 표현식이 복잡한데 테스트 방법은?</strong></summary>

**A**: **Spring Boot 테스트로 검증**합니다.

```java
@SpringBootTest
class PointcutTest {

    @Autowired
    private ApplicationContext context;

    @Test
    void testPointcut() {
        // Aspect가 적용되는지 확인
        UserService userService = context.getBean(UserService.class);

        // Proxy 객체인지 확인
        assertThat(AopUtils.isAopProxy(userService)).isTrue();

        // CGLIB Proxy인지 확인
        assertThat(AopUtils.isCglibProxy(userService)).isTrue();
    }
}

// 또는 AspectJ의 PointcutParser 사용
PointcutParser parser = PointcutParser
    .getPointcutParserSupportingAllPrimitivesAndUsingContextClassloaderForResolution();

PointcutExpression pointcut = parser.parsePointcutExpression(
    "execution(* com.example.service.*.*(..))"
);

Method method = UserService.class.getMethod("createUser", UserDto.class);
boolean matches = pointcut.matchesMethodExecution(method).alwaysMatches();

assertThat(matches).isTrue();
```

</details>

<details>
<summary><strong>Q3: AOP가 적용되지 않는 이유는?</strong></summary>

**A**: **자주 발생하는 원인 3가지**입니다.

**1. 같은 클래스 내부 호출**:
```java
@Service
public class UserService {

    @Transactional
    public void outerMethod() {
        innerMethod();  // ❌ Proxy를 거치지 않음!
    }

    @Transactional
    public void innerMethod() {
        // AOP 적용 안 됨
    }
}

// 해결: 별도 Bean으로 분리
@Service
public class UserService {
    @Autowired
    private UserInternalService internalService;

    @Transactional
    public void outerMethod() {
        internalService.innerMethod();  // ✅ Proxy 통과
    }
}

@Service
public class UserInternalService {
    @Transactional
    public void innerMethod() {
        // AOP 적용됨
    }
}
```

**2. Private 메서드**:
```java
@Service
public class UserService {

    @Transactional
    private void privateMethod() {  // ❌ Private는 Proxy 불가
        // AOP 적용 안 됨
    }
}

// 해결: Public으로 변경
@Transactional
public void publicMethod() {  // ✅
    // AOP 적용됨
}
```

**3. Final 메서드/클래스**:
```java
@Service
public final class UserService {  // ❌ Final 클래스
    // CGLIB Proxy 생성 불가
}

@Service
public class UserService {
    @Transactional
    public final void method() {  // ❌ Final 메서드
        // Proxy가 Override 불가
    }
}
```

</details>

<details>
<summary><strong>Q4: JDK Dynamic Proxy vs CGLIB Proxy의 차이는?</strong></summary>

**A**: **인터페이스 유무에 따라 선택**됩니다.

```java
// JDK Dynamic Proxy: 인터페이스 기반
public interface UserService {
    void createUser(UserDto dto);
}

@Service
public class UserServiceImpl implements UserService {
    @Override
    public void createUser(UserDto dto) {
        // AOP가 JDK Dynamic Proxy 사용
    }
}

// CGLIB Proxy: 클래스 기반
@Service
public class ProductService {  // 인터페이스 없음
    public void createProduct(ProductDto dto) {
        // AOP가 CGLIB Proxy 사용
    }
}
```

**차이점**:

| 구분 | JDK Dynamic Proxy | CGLIB Proxy |
|------|-------------------|-------------|
| **기반** | 인터페이스 | 클래스 상속 |
| **조건** | 인터페이스 필수 | 인터페이스 불필요 |
| **생성 속도** | 빠름 | 느림 (바이트코드 조작) |
| **실행 속도** | 느림 (Reflection) | 빠름 |
| **제약사항** | 인터페이스 메서드만 | final 클래스/메서드 불가 |

**Spring의 선택 기준**:
- Spring 4.x: 인터페이스 있으면 JDK, 없으면 CGLIB
- Spring 5.x+: 기본적으로 CGLIB (성능 개선)

**강제 지정**:
```java
@EnableAspectJAutoProxy(proxyTargetClass = true)  // CGLIB 강제
```

</details>

<details>
<summary><strong>Q5: @Transactional은 어떻게 AOP로 구현되나요?</strong></summary>

**A**: **@Around Advice로 트랜잭션 전후 처리**합니다.

```java
// Spring이 내부적으로 생성하는 TransactionInterceptor (의사 코드)
@Around("@annotation(Transactional)")
public Object manageTransaction(ProceedingJoinPoint joinPoint) throws Throwable {

    // 1. 트랜잭션 시작
    TransactionStatus status = transactionManager.getTransaction(definition);

    try {
        // 2. 실제 메서드 실행
        Object result = joinPoint.proceed();

        // 3. 커밋
        transactionManager.commit(status);

        return result;

    } catch (RuntimeException | Error e) {
        // 4. 롤백 (RuntimeException만)
        transactionManager.rollback(status);
        throw e;
    }
}
```

**동작 흐름**:
```
[클라이언트 호출]
    ↓
[TransactionInterceptor (Proxy)]
    ↓ 1. transactionManager.getTransaction() → 트랜잭션 시작
    ↓ 2. joinPoint.proceed() → 실제 메서드 실행
    ↓ 3-a. 성공 시 → transactionManager.commit()
    ↓ 3-b. 예외 시 → transactionManager.rollback()
    ↓
[결과 반환]
```

**rollbackFor 동작**:
```java
@Transactional(rollbackFor = Exception.class)  // 모든 예외 롤백
public void method() {
    // Checked Exception도 롤백됨
}
```

</details>

<details>
<summary><strong>Q6: Pointcut 표현식의 주요 지시자는?</strong></summary>

**A**: **execution, within, annotation, args** 등이 있습니다.

```java
// 1. execution: 메서드 시그니처 기반 (가장 많이 사용)
@Around("execution(* com.example.service.*.*(..))")
//              리턴타입  패키지.클래스.메서드(파라미터)
public Object log1(ProceedingJoinPoint joinPoint) { }

// 2. within: 타입 패턴 기반 (패키지 전체)
@Around("within(com.example.service..*)")  // service 하위 패키지 전체
public Object log2(ProceedingJoinPoint joinPoint) { }

// 3. @annotation: 어노테이션 기반 (가장 안전)
@Around("@annotation(PerformanceLog)")
public Object log3(ProceedingJoinPoint joinPoint) { }

// 4. @within: 클래스 레벨 어노테이션
@Around("@within(org.springframework.stereotype.Service)")
public Object log4(ProceedingJoinPoint joinPoint) { }

// 5. args: 파라미터 타입 기반
@Around("execution(* *(..)) && args(dto)")
public Object log5(ProceedingJoinPoint joinPoint, UserDto dto) { }

// 6. bean: Bean 이름 기반
@Around("bean(*Service)")  // 이름이 Service로 끝나는 Bean
public Object log6(ProceedingJoinPoint joinPoint) { }
```

**조합 사용**:
```java
// AND 조합
@Around("within(com.example.service..*) && execution(public * *(..))")

// OR 조합
@Around("@annotation(Transactional) || @annotation(Async)")

// NOT 조합
@Around("execution(* com.example..*.*) && !within(com.example.test..*)")
```

**실무 권장 순서**:
1. **@annotation**: 가장 명시적, 실수 적음
2. **within**: 패키지 단위로 적용
3. **execution**: 세밀한 제어 필요 시

</details>

<details>
<summary><strong>Q7: AOP 성능 오버헤드는 얼마나 되나요?</strong></summary>

**A**: **일반적으로 5% 미만**이며 무시할 수 있는 수준입니다.

**성능 측정 결과**:

```
┌──────────────────┬────────────┬──────────────┬──────────┐
│ 테스트 케이스     │ AOP 없음   │ AOP 적용     │ 오버헤드 │
├──────────────────┼────────────┼──────────────┼──────────┤
│ 단순 메서드       │ 0.1ms      │ 0.105ms      │ 5%       │
│ 복잡한 비즈니스   │ 100ms      │ 101ms        │ 1%       │
│ DB 트랜잭션       │ 50ms       │ 51ms         │ 2%       │
└──────────────────┴────────────┴──────────────┴──────────┘
```

**오버헤드 요인**:
1. **Proxy 생성**: 애플리케이션 시작 시 한 번만
2. **Proxy 호출**: 메서드 호출마다 발생 (매우 빠름)
3. **Advice 실행**: Advice 로직 자체의 시간

**최적화 방법**:

```java
// ❌ 나쁜 예: 모든 메서드에 적용
@Around("execution(* com.example..*.*(..))")
public Object logEverything(ProceedingJoinPoint joinPoint) {
    // 너무 많은 메서드에 적용되어 오버헤드 증가
}

// ✅ 좋은 예: 필요한 곳에만 적용
@Around("@annotation(PerformanceLog)")
public Object logSpecific(ProceedingJoinPoint joinPoint) {
    // 성능 측정이 정말 필요한 메서드만 적용
}

// ✅ 더 나은 예: Aspect 내부도 최적화
@Around("@annotation(PerformanceLog)")
public Object logOptimized(ProceedingJoinPoint joinPoint) {
    long start = System.nanoTime();  // currentTimeMillis()보다 빠름

    Object result = joinPoint.proceed();

    long duration = System.nanoTime() - start;

    // 조건부 로깅 (DEBUG 레벨일 때만)
    if (log.isDebugEnabled()) {
        log.debug("실행 시간: {}ns", duration);
    }

    return result;
}
```

**실무 가이드**:
- **로깅**: 오버헤드 거의 없음 (로그 레벨로 제어)
- **성능 측정**: 1-2% 오버헤드 (허용 범위)
- **트랜잭션**: 2-3% 오버헤드 (필수 기능이므로 수용)
- **복잡한 Advice**: 10% 이상 가능 → 최적화 필요

**측정 방법**:
```java
@Test
void testAopPerformance() {
    // AOP 없이
    long start1 = System.nanoTime();
    for (int i = 0; i < 100000; i++) {
        service.method();
    }
    long duration1 = System.nanoTime() - start1;

    // AOP 적용
    long start2 = System.nanoTime();
    for (int i = 0; i < 100000; i++) {
        proxyService.method();
    }
    long duration2 = System.nanoTime() - start2;

    double overhead = ((double)(duration2 - duration1) / duration1) * 100;
    log.info("AOP 오버헤드: {}%", overhead);
}
```

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. AOP가 무엇이고 왜 사용하나요?</strong></summary>

**모범 답안**:
> "AOP는 Aspect-Oriented Programming의 약자로, 횡단 관심사를 모듈화하는 프로그래밍 패러다임입니다. 로깅, 트랜잭션, 보안 등 여러 모듈에 공통으로 필요한 부가 기능을 핵심 비즈니스 로직에서 분리하여 Aspect로 정의하고, 필요한 곳에 자동으로 적용합니다. 이를 통해 코드 중복을 제거하고 관심사를 명확히 분리하여 유지보수성을 높입니다."

</details>

<details>
<summary><strong>2. @Before, @After, @Around의 차이를 설명하세요</strong></summary>

**모범 답안**:
> "@Before는 메서드 실행 전에 동작하며 메서드 실행을 막을 수 없습니다. @After는 메서드 실행 후에 동작하며 성공/실패 여부와 무관하게 항상 실행됩니다. @Around는 메서드 실행 전후를 모두 제어할 수 있으며, ProceedingJoinPoint.proceed()로 실제 메서드를 실행하고 반환값을 수정할 수도 있습니다. 가장 강력하지만 proceed() 호출을 잊으면 메서드가 실행되지 않으므로 주의가 필요합니다."

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. Spring AOP와 AspectJ의 차이를 설명하세요</strong></summary>

**모범 답안**:
> "Spring AOP는 Proxy 기반으로 런타임에 동작하며 메서드 실행 시점만 지원합니다. 설정이 간단하고 Spring 컨테이너와 통합되어 있어 대부분의 경우 충분합니다. AspectJ는 컴파일 타임 또는 로드 타임 위빙을 사용하며 필드 접근, 생성자 호출 등 더 다양한 조인 포인트를 지원합니다. 더 강력하지만 별도의 컴파일러나 에이전트가 필요하고 설정이 복잡합니다. 실무에서는 메서드 실행만 제어하면 되는 경우가 대부분이므로 Spring AOP를 주로 사용합니다."

</details>

<details>
<summary><strong>2. AOP 내부 호출 문제와 해결 방법을 설명하세요</strong></summary>

**모범 답안**:
> "같은 클래스 내에서 메서드를 직접 호출하면 Proxy를 거치지 않아 AOP가 적용되지 않습니다. 이는 this.method()로 호출하면 실제 객체의 메서드가 직접 호출되고, Proxy의 Advice가 실행되지 않기 때문입니다. 해결 방법은 첫째, 메서드를 별도 Bean으로 분리하여 의존성 주입받아 사용하는 것입니다. 둘째, AopContext.currentProxy()를 사용하여 현재 Proxy를 가져와 호출하는 방법도 있지만 코드가 Spring에 의존적이 됩니다. 실무에서는 첫 번째 방법인 Bean 분리가 권장됩니다."

</details>

---

## 📖 면접 질문 리스트 답안

> **사용 가이드**: 이 섹션은 위의 면접 질문에 대한 상세 답안입니다. 먼저 스스로 답변을 준비한 후, 이 답안을 참고하여 보완하세요.

---

### 📘 주니어/신입 개발자용 답변

<details>
<summary><strong>Q1: AOP가 무엇이고 왜 사용하나요?</strong></summary>

**⏱️ 답변 시간**: 30초 - 1분

**✅ 모범 답안**:

> "AOP는 Aspect-Oriented Programming의 약자로, **횡단 관심사를 모듈화**하는 프로그래밍 패러다임입니다. 로깅, 트랜잭션, 보안처럼 **여러 모듈에 공통으로 필요한 부가 기능**을 핵심 비즈니스 로직에서 분리하여 Aspect로 정의하고, 필요한 곳에 자동으로 적용합니다.
>
> 예를 들어, 모든 Service 메서드의 실행 시간을 측정하려면 각 메서드마다 시작/종료 시간을 기록하는 코드를 반복해서 작성해야 하지만, AOP를 사용하면 @Around Advice를 한 번만 작성하면 모든 메서드에 자동으로 적용됩니다.
>
> 이를 통해 **코드 중복을 제거**하고 **관심사를 명확히 분리**하여 유지보수성을 높입니다. Spring에서는 Proxy 패턴을 사용하여 런타임에 AOP를 구현합니다."

**📊 답변 구조 분석**:
- **정의** (10초): AOP의 개념과 목적
- **예시** (20초): 실행 시간 측정이라는 구체적 사례
- **효과** (10초): 코드 중복 제거, 관심사 분리

**💡 면접관이 주목하는 포인트**:
- ✅ "횡단 관심사"라는 핵심 용어 사용
- ✅ 구체적인 예시로 이해도 증명
- ✅ Spring의 Proxy 기반 구현 언급

**🚫 피해야 할 답변**:
- ❌ "코드를 깔끔하게 하는 기술입니다" (너무 추상적)
- ❌ "잘 모르겠지만 트랜잭션에 사용한다고 들었습니다" (피상적)
- ❌ 예시 없이 이론만 나열

</details>

<details>
<summary><strong>Q2: @Before, @After, @Around의 차이를 설명하세요</strong></summary>

**⏱️ 답변 시간**: 30초 - 1분

**✅ 모범 답안**:

> "@Before는 **메서드 실행 전**에만 동작하며 메서드 실행을 막을 수 없습니다. 주로 입력값 검증이나 로깅에 사용합니다.
>
> @After는 **메서드 실행 후**에 동작하며 성공/실패 여부와 무관하게 항상 실행됩니다. finally 블록과 비슷한 역할입니다.
>
> @Around는 **메서드 실행 전후를 모두 제어**할 수 있는 가장 강력한 Advice입니다. ProceedingJoinPoint.proceed()로 실제 메서드를 실행하고, 반환값을 수정할 수도 있습니다. 성능 측정이나 트랜잭션 관리에 주로 사용되지만, **proceed() 호출을 잊으면 메서드가 실행되지 않으므로** 주의가 필요합니다."

**📊 답변 구조 분석**:
- **@Before** (10초): 실행 전, 사용 사례
- **@After** (10초): 실행 후, 특징
- **@Around** (15초): 전후 제어, 주의사항

**💡 꼭 언급해야 할 포인트**:
- ✅ proceed() 호출의 중요성
- ✅ 각 Advice의 사용 사례
- ✅ @Around의 강력함과 위험성

**🎯 추가 질문 대비**:
- "그럼 언제 @Around를 쓰고 언제 @Before를 쓰나요?"
  → "@Around는 실행 시간 측정처럼 전후 정보가 모두 필요할 때, @Before는 단순 로깅처럼 실행 전 정보만 필요할 때 사용합니다."

</details>

---

### 📗 중급 개발자용 답변

<details>
<summary><strong>Q1: Spring AOP와 AspectJ의 차이를 설명하세요</strong></summary>

**⏱️ 답변 시간**: 1분 - 1분 30초

**✅ 모범 답안**:

> "Spring AOP와 AspectJ는 둘 다 AOP를 구현하지만 **위빙 시점과 지원 범위**가 다릅니다.
>
> **Spring AOP**는 **Proxy 기반**으로 **런타임**에 동작합니다. JDK Dynamic Proxy나 CGLIB을 사용하여 Bean을 감싸는 Proxy를 생성하고, 메서드 호출 시 Advice를 실행합니다. **메서드 실행 시점만 지원**하지만, 설정이 간단하고 Spring 컨테이너와 잘 통합되어 있어 대부분의 경우 충분합니다.
>
> **AspectJ**는 **컴파일 타임** 또는 **로드 타임 위빙**을 사용합니다. 바이트코드를 직접 수정하므로 필드 접근, 생성자 호출, static 메서드 등 **더 다양한 조인 포인트**를 지원합니다. 더 강력하지만 별도의 AspectJ 컴파일러(ajc)나 로드 타임 에이전트(-javaagent)가 필요하고 설정이 복잡합니다.
>
> 실무에서는 **메서드 실행만 제어하면 되는 경우가 대부분**이므로 Spring AOP를 주로 사용하고, 필드 접근이나 생성자 조인 포인트가 필요한 특수한 경우에만 AspectJ를 사용합니다."

**📊 답변 구조 분석**:
- **개요** (10초): 위빙 시점과 지원 범위 차이
- **Spring AOP** (25초): 특징, 장단점
- **AspectJ** (25초): 특징, 장단점
- **실무 선택** (10초): 언제 무엇을 사용하는가

**💡 면접관이 주목하는 포인트**:
- ✅ Proxy 기반 vs 바이트코드 조작 차이 이해
- ✅ 위빙 시점 (런타임 vs 컴파일/로드 타임) 정확히 구분
- ✅ 실무 경험 기반 선택 기준 제시

**🎯 추가 질문 대비**:
- "Spring에서 AspectJ를 사용할 수는 있나요?"
  → "네, @EnableAspectJAutoProxy의 mode를 ASPECTJ로 설정하거나, 별도로 AspectJ 컴파일러를 설정하면 사용 가능합니다. 하지만 대부분의 경우 Spring AOP로 충분합니다."

</details>

<details>
<summary><strong>Q2: AOP 내부 호출 문제와 해결 방법을 설명하세요</strong></summary>

**⏱️ 답변 시간**: 1분 - 1분 30초

**✅ 모범 답안**:

> "**내부 호출 문제**는 같은 클래스 내에서 메서드를 직접 호출하면 Proxy를 거치지 않아 AOP가 적용되지 않는 문제입니다.
>
> 예를 들어, Service 클래스의 outerMethod()에서 같은 클래스의 @Transactional이 붙은 innerMethod()를 호출하면, 이는 this.innerMethod() 호출이 되어 **실제 객체의 메서드가 직접 실행**되고, **Proxy의 Advice가 실행되지 않습니다**. 따라서 트랜잭션이 시작되지 않아 롤백도 되지 않습니다.
>
> **해결 방법**은 크게 세 가지입니다:
>
> **첫째, Bean 분리** (권장): innerMethod()를 별도 Service Bean으로 분리하여 의존성 주입받아 사용합니다. 이렇게 하면 다른 Bean의 메서드를 호출하므로 Proxy를 거칩니다. 코드도 더 명확해지고 단일 책임 원칙에도 부합합니다.
>
> **둘째, Self-Injection**: 자기 자신을 @Autowired로 주입받아 사용하는 방법입니다. self.innerMethod()로 호출하면 Proxy를 거칩니다. 하지만 코드가 직관적이지 않고 순환 참조 경고가 발생할 수 있습니다.
>
> **셋째, AopContext.currentProxy()**: Spring의 AopContext를 사용하여 현재 Proxy를 가져와 호출하는 방법입니다. 하지만 코드가 Spring에 강하게 결합되고, @EnableAspectJAutoProxy(exposeProxy = true) 설정이 필요합니다.
>
> 실무에서는 **첫 번째 Bean 분리 방법**을 권장합니다."

**📊 답변 구조 분석**:
- **문제 정의** (15초): 내부 호출 시 Proxy 우회
- **원인 설명** (20초): this 호출이 실제 객체 호출
- **해결 방법 1** (20초): Bean 분리 (권장)
- **해결 방법 2-3** (20초): 대안들과 단점
- **실무 권장** (5초): Bean 분리 강조

**💡 면접관이 주목하는 포인트**:
- ✅ Proxy 패턴 이해도 (this vs proxy 호출 차이)
- ✅ 여러 해결 방법을 알고 장단점 비교 가능
- ✅ 실무 경험 기반 선택 (Bean 분리)

**🎯 추가 질문 대비**:
- "왜 Bean 분리가 가장 좋은 방법인가요?"
  → "코드가 명확하고, Spring에 의존하지 않으며, 단일 책임 원칙에 부합하여 테스트와 유지보수가 쉽기 때문입니다."

</details>

---

### 💬 답변 전략 및 팁

#### 답변 시간 가이드

```
┌──────────────────┬─────────────┬─────────────┐
│ 질문 난이도      │ 주니어      │ 중급        │
├──────────────────┼─────────────┼─────────────┤
│ 최소 답변 시간   │ 30초        │ 1분         │
│ 최대 답변 시간   │ 1분         │ 2분         │
│ 이상적 길이      │ 45초        │ 1분 30초    │
└──────────────────┴─────────────┴─────────────┘
```

#### 답변 패턴

**주니어용 답변 패턴**: **정의 → 예시 → 효과**
1. 개념을 명확히 정의 (10-15초)
2. 구체적인 예시 제시 (20-30초)
3. 효과/장점 설명 (5-10초)

**중급용 답변 패턴**: **문제 → 해결 → 비교 → 선택**
1. 문제 상황 정의 (15-20초)
2. 해결 방법 제시 (40-60초)
3. 대안 비교 (20-30초)
4. 실무 선택 기준 (5-10초)

#### 면접 중 긴장했을 때

**호흡 조절**:
- 답변 전 1-2초 멈추고 심호흡
- "좋은 질문입니다" 또는 "잠시 생각해보겠습니다" 로 시작

**답변 구조화**:
- "크게 세 가지로 나눠 말씀드리겠습니다" (구조 먼저 제시)
- "첫째..., 둘째..., 셋째..." (순서 명확히)

**모를 때 대처**:
```
❌ 나쁜 대답: "모르겠습니다"
✅ 좋은 대답: "정확한 내용은 기억나지 않지만, 제가 이해한 바로는 ..."
✅ 더 좋은 대답: "실무에서 직접 사용해본 경험은 없지만, 학습한 내용으로는 ..."
```

---

## 📝 핵심 정리

### Advice 종류 비교

| Advice | 실행 시점 | 메서드 제어 | 반환값 수정 | 사용 빈도 |
|--------|----------|-----------|-----------|----------|
| **@Before** | 실행 전 | ❌ | ❌ | 30% |
| **@After** | 실행 후 (무조건) | ❌ | ❌ | 10% |
| **@AfterReturning** | 성공 시 | ❌ | ❌ | 15% |
| **@AfterThrowing** | 예외 시 | ❌ | ❌ | 10% |
| **@Around** | 전후 | ✅ | ✅ | 35% |

### 실무 활용 시나리오

| 시나리오 | 사용 Advice | Pointcut |
|---------|-----------|----------|
| **로깅** | @Around | `execution(* com.example.service.*.*(..))` |
| **성능 측정** | @Around | `@annotation(PerformanceLog)` |
| **트랜잭션** | @Around | `@annotation(Transactional)` |
| **권한 검사** | @Before | `@annotation(RequiresAuth)` |
| **예외 처리** | @AfterThrowing | `execution(* com.example.*.*(..))` |

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] **@Around는 신중히 사용**: proceed() 호출 필수
- [ ] **Pointcut을 재사용**: @Pointcut으로 정의 후 참조
- [ ] **어노테이션 기반 Pointcut**: 유연하고 명확
- [ ] **성능 영향 고려**: 과도한 AOP 적용 지양

#### ❌ 하지 말아야 할 것
- [ ] **내부 호출에 AOP 의존**: Proxy 우회 문제
- [ ] **Private 메서드에 AOP**: 적용 안 됨
- [ ] **과도한 Aspect**: 디버깅 어려움
- [ ] **proceed() 누락**: 메서드 실행 안 됨

---

## 📚 추가 학습 자료

> **학습 로드맵**: 이 섹션의 자료들을 순서대로 학습하면 AOP 전문가가 될 수 있습니다.

---

### 📖 공식 문서

#### Spring 공식 문서
- **Spring Framework AOP**: https://docs.spring.io/spring-framework/reference/core/aop.html
  - 난이도: ⭐⭐⭐☆☆
  - 추천: Spring AOP의 모든 것을 다루는 공식 가이드
  - 핵심 섹션: Aspect, Pointcut, Advice 상세 설명

- **Spring Boot AOP Starter**: https://docs.spring.io/spring-boot/docs/current/reference/html/using.html#using.auto-configuration
  - 난이도: ⭐⭐☆☆☆
  - 추천: Auto-configuration을 활용한 AOP 설정

#### AspectJ 공식 문서
- **AspectJ Programming Guide**: https://www.eclipse.org/aspectj/doc/released/progguide/index.html
  - 난이도: ⭐⭐⭐⭐☆
  - 추천: AspectJ의 고급 기능과 Spring AOP의 차이 이해

---

### 🇰🇷 한국어 블로그 & 자료

#### 우아한형제들 기술 블로그
- **Spring AOP 적용 사례**: https://techblog.woowahan.com/
  - "배달의민족 로깅 시스템에 AOP 적용하기"
  - "대규모 트래픽 환경에서의 성능 모니터링 AOP"
  - 실무 경험 기반의 깊이 있는 내용

#### 카카오 기술 블로그
- **if(kakao) 2022 - AOP 성능 최적화**: https://tech.kakao.com/
  - "메소드 실행 시간 측정 AOP의 성능 개선"
  - "Pointcut 표현식 최적화 노하우"
  - 대규모 서비스의 AOP 운영 경험

#### 네이버 D2
- **Spring AOP 내부 동작 원리**: https://d2.naver.com/
  - "Proxy 패턴과 CGLIB의 동작 원리"
  - "JDK Dynamic Proxy vs CGLIB 성능 비교"
  - 심화 학습에 적합

#### NHN Cloud MeetUp
- **실전 AOP 활용 패턴**: https://meetup.nhncloud.com/
  - "API 성능 모니터링 시스템 구축기"
  - "분산 트랜잭션 추적 AOP"

---

### 🌍 영어 자료

#### Baeldung
- **Spring AOP Tutorial**: https://www.baeldung.com/spring-aop
  - 난이도: ⭐⭐⭐☆☆
  - 추천: 단계별 예제가 풍부한 튜토리얼
  - 핵심: @Around, @Before, @After 상세 예제

- **Introduction to Pointcut Expressions**: https://www.baeldung.com/spring-aop-pointcut-tutorial
  - 난이도: ⭐⭐⭐⭐☆
  - 추천: Pointcut 표현식 마스터하기

- **AOP vs AspectJ**: https://www.baeldung.com/spring-aop-vs-aspectj
  - 난이도: ⭐⭐⭐⭐☆
  - 추천: 두 기술의 차이 명확히 이해

#### Spring Blog
- **Spring AOP Best Practices**: https://spring.io/blog
  - "Common Pitfalls of Spring AOP"
  - "Performance Considerations for AOP"

---

### 🎥 동영상 강의

#### 한국어 강의

**김영한님 - 스프링 핵심 원리 (고급편)**
- 플랫폼: 인프런
- 가격: 유료
- 난이도: ⭐⭐⭐⭐☆
- 추천 이유: AOP 동작 원리를 코드 레벨까지 깊이 있게 설명
- 핵심 섹션:
  - Proxy 패턴과 데코레이터 패턴
  - JDK Dynamic Proxy vs CGLIB
  - @Aspect 내부 동작 원리
  - 실무 트러블슈팅

**백기선님 - 스프링 프레임워크 핵심 기술**
- 플랫폼: 인프런
- 가격: 유료
- 난이도: ⭐⭐⭐☆☆
- 추천 이유: AOP 기본 개념을 쉽게 설명
- 핵심 섹션:
  - AOP 개념과 용어
  - @AspectJ 활용
  - 실전 예제

#### 영어 강의

**Spring Framework 6 Beginner to Guru**
- 플랫폼: Udemy
- 난이도: ⭐⭐⭐☆☆
- 추천: AOP 섹션이 잘 구성됨

**Master Microservices with Spring Boot and Spring Cloud**
- 플랫폼: Udemy
- 난이도: ⭐⭐⭐⭐☆
- 추천: 마이크로서비스 환경에서의 AOP 활용

---

### 📚 추천 도서

#### 한국어 도서

**토비의 스프링 3.1 Vol. 2**
- 저자: 이일민
- 난이도: ⭐⭐⭐⭐⭐
- 추천 챕터: 6장 AOP
- 특징: AOP의 철학과 원리를 깊이 있게 설명
- 추천 대상: 중급 이상 개발자

**스프링 부트 핵심 가이드**
- 저자: 장정우
- 난이도: ⭐⭐⭐☆☆
- 추천 챕터: 12장 AOP 적용
- 특징: 실무 예제 중심
- 추천 대상: 주니어 개발자

**자바 ORM 표준 JPA 프로그래밍**
- 저자: 김영한
- 난이도: ⭐⭐⭐⭐☆
- 추천 이유: @Transactional AOP 원리 이해
- 핵심 내용: 트랜잭션 AOP 동작 방식

#### 영어 도서

**Spring in Action (6th Edition)**
- 저자: Craig Walls
- 난이도: ⭐⭐⭐☆☆
- 추천 챕터: Chapter 5 - AOP
- 특징: 최신 Spring 6 기반 설명

**Pro Spring 6**
- 저자: Iuliana Cosmina
- 난이도: ⭐⭐⭐⭐☆
- 추천 챕터: Chapter 6 - Spring AOP
- 특징: AOP 내부 구현 상세 설명

---

### 🎤 컨퍼런스 발표 & 세미나

#### 국내 컨퍼런스

**DEVIEW (네이버)**
- "대규모 분산 시스템에서의 AOP 활용" (2022)
- "성능 모니터링 시스템 구축 사례" (2021)
- 링크: https://deview.kr/

**if(kakao) dev**
- "AOP를 활용한 API 성능 최적화" (2023)
- "마이크로서비스 환경의 분산 추적" (2022)
- 링크: https://if.kakao.com/

**Spring Camp**
- "Spring AOP 내부 동작 원리" (연례)
- "실전 AOP 트러블슈팅" (연례)
- 링크: https://springcamp.io/

#### 해외 컨퍼런스

**SpringOne**
- "What's New in Spring AOP" (매년)
- "Best Practices for Production AOP"
- 링크: https://springone.io/

**Devoxx**
- "Deep Dive into Spring AOP"
- "AspectJ and Spring Integration"

---

### 💻 GitHub 저장소 & 오픈소스

#### 학습용 예제 저장소

**Spring Guides - AOP**
- URL: https://github.com/spring-guides/gs-maven
- 난이도: ⭐⭐☆☆☆
- 특징: 공식 가이드의 예제 코드
- 추천: AOP 입문자

**Spring Framework Examples**
- URL: https://github.com/spring-projects/spring-framework
- 난이도: ⭐⭐⭐⭐⭐
- 특징: Spring Framework 소스 코드
- 추천: AOP 내부 동작 원리 학습

#### 실무 적용 사례

**Netflix Zuul (API Gateway)**
- URL: https://github.com/Netflix/zuul
- 난이도: ⭐⭐⭐⭐☆
- 특징: 대규모 API 게이트웨이의 AOP 활용
- 학습 포인트: 필터와 AOP 조합

**Spring Cloud Sleuth**
- URL: https://github.com/spring-cloud/spring-cloud-sleuth
- 난이도: ⭐⭐⭐⭐☆
- 특징: 분산 추적 시스템의 AOP 활용
- 학습 포인트: MDC와 AOP 조합

---

### 🛠️ 실습 도구 & 플랫폼

#### 온라인 실습 환경

**Spring Initializr**
- URL: https://start.spring.io/
- 용도: AOP 프로젝트 빠른 시작
- 설정: Spring Web, Spring AOP 의존성 추가

**Replit**
- URL: https://replit.com/
- 용도: 브라우저에서 Spring Boot 실습

#### 디버깅 & 모니터링 도구

**IntelliJ IDEA**
- AOP Advisor 플러그인: Pointcut 매칭 확인
- Spring AOP 디버거: Aspect 실행 흐름 추적

**Spring Boot Actuator + Prometheus**
- 용도: AOP 메트릭 수집 및 모니터링
- Grafana 연동 대시보드

---

### 📝 학습 순서 가이드

#### 1단계: 기초 다지기 (1-2주)
```
1. Spring 공식 문서 AOP 섹션 정독
2. Baeldung AOP Tutorial 따라하기
3. 김영한님 강의 AOP 섹션 수강
4. 간단한 로깅 Aspect 직접 구현
```

#### 2단계: 심화 학습 (2-3주)
```
1. 토비의 스프링 Vol.2 6장 정독
2. Proxy 패턴 vs 데코레이터 패턴 이해
3. JDK Dynamic Proxy vs CGLIB 비교
4. 내부 호출 문제 실습 및 해결
```

#### 3단계: 실무 적용 (3-4주)
```
1. 우아한형제들/카카오 기술 블로그 사례 연구
2. API 성능 모니터링 시스템 구축 (실전 프로젝트)
3. MDC와 분산 추적 AOP 구현
4. Prometheus + Grafana 연동
```

#### 4단계: 고급 주제 (4주 이상)
```
1. AspectJ 문법 학습
2. Load-Time Weaving 실습
3. 대용량 트래픽 환경 AOP 성능 최적화
4. 오픈소스 분석 (Spring Cloud Sleuth, Netflix Zuul)
```

---

### 💡 학습 팁

#### 효과적인 학습 방법

**1. 코드 작성이 우선**
- 📚 문서 읽기: 30%
- 💻 직접 코딩: 70%
- 이론만 학습하지 말고 반드시 손으로 구현

**2. 디버거 활용**
- Aspect 실행 시점 확인
- Proxy 생성 과정 추적
- 내부 호출 문제 직접 확인

**3. 실무 사례 연구**
- 대기업 기술 블로그 정독
- 오픈소스 코드 분석
- 컨퍼런스 발표 시청

**4. 테스트 코드 작성**
- Pointcut 매칭 테스트
- Aspect 동작 검증
- 성능 테스트

---

### 🎯 다음 학습 추천

**이 장을 완료했다면**:
1. ✅ AOP 기본 개념 이해
2. ✅ @Aspect, @Around, Pointcut 사용법
3. ✅ 실무 활용 사례 경험

**다음 단계**:
- **09장: SpEL (Spring Expression Language)**: 동적 값 주입과 조건부 설정
- **10장: Spring Transaction**: @Transactional 내부 동작 원리
- **고급**: AspectJ Load-Time Weaving

---

## 🚀 다음 단계

### 📘 다음 학습: 09장 - SpEL (Spring Expression Language)

**AOP를 배운 여러분, 다음은?**

AOP로 **공통 기능을 모듈화**하는 방법을 배웠습니다. 이제 **SpEL**로 한 단계 더 발전시켜 보세요!

```java
// AOP: 공통 기능 자동화
@Around("execution(* com.example.service.*.*(..))")
public Object logMethod(ProceedingJoinPoint joinPoint) throws Throwable {
    // 모든 Service 메서드에 로깅
}

// SpEL: 동적 값 주입 + 조건부 적용
@Cacheable(
    value = "products",
    key = "#id",
    condition = "#id > 0 && @env.getProperty('cache.enabled') == 'true'"
)
public Product getProduct(Long id) {
    // SpEL 표현식으로 캐시 키와 조건 지정
}

// AOP + SpEL 조합: 최강의 조합!
@Around("@annotation(RequiresPermission)")
public Object checkPermission(ProceedingJoinPoint joinPoint, RequiresPermission anno) {
    // SpEL로 권한 표현식 평가
    String permission = anno.value();  // "hasRole('ADMIN') or hasPermission(#id, 'write')"

    SpelExpressionParser parser = new SpelExpressionParser();
    boolean hasPermission = parser.parseExpression(permission).getValue(context, Boolean.class);

    if (!hasPermission) {
        throw new AccessDeniedException("권한 없음");
    }

    return joinPoint.proceed();
}
```

---

### 🎯 09장 SpEL에서 배울 내용

#### 1. SpEL 기본 문법
```java
// 산술 연산
@Value("#{10 + 5}")  // 15
private int sum;

// 논리 연산
@Value("#{user.age >= 18 and user.verified}")
private boolean isAdult;

// Bean 참조
@Value("#{@userService.getCurrentUser().name}")
private String currentUserName;

// 컬렉션 필터링
@Value("#{products.?[price > 100000]}")
private List<Product> expensiveProducts;
```

#### 2. SpEL 실무 활용
- **동적 캐시 키 생성**: `@Cacheable(key = "#user.id + '-' + #type")`
- **조건부 설정**: `@Scheduled(cron = "#{@config.cronExpression}")`
- **보안 표현식**: `@PreAuthorize("hasRole('ADMIN') or #id == principal.id")`
- **동적 쿼리**: `@Query("... WHERE status = :#{#status ?: 'ACTIVE'}")`

#### 3. AOP + SpEL 고급 패턴
```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface RateLimitSpEL {
    String key();  // SpEL 표현식
    int limit() default 100;
}

@RateLimitSpEL(
    key = "#user.id + ':' + #request.getRequestURI()",
    limit = 10
)
public Response processRequest(User user, HttpServletRequest request) {
    // SpEL로 동적 키 생성 + AOP로 Rate Limiting 적용
}
```

---

### 📚 학습 로드맵

```
[07장] 어노테이션 상세
    ↓
  @Component, @Service, @Autowired
    ↓
[08장] AOP 개념과 활용 ✅ 현재 위치
    ↓
  횡단 관심사 모듈화, @Aspect
    ↓
[09장] SpEL ⬅️ 다음 학습
    ↓
  동적 값 주입, 조건부 설정
    ↓
[10장] Spring Transaction
    ↓
  @Transactional, 트랜잭션 전파
    ↓
[고급] 마이크로서비스 아키텍처
```

---

### ✅ 09장 학습 전 체크리스트

**필수 선행 지식**:
- [x] AOP 기본 개념 이해
- [x] @Aspect와 Pointcut 작성
- [x] @Around에서 proceed() 호출
- [x] 어노테이션 기반 설정 (@Value, @Bean)

**준비 사항**:
- [ ] Spring Boot 프로젝트 생성 (Spring Web 의존성)
- [ ] IntelliJ IDEA 또는 VS Code 설치
- [ ] 09장 Part 1 문서 확인

**예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐☆☆

---

### 💪 학습 동기 부여

**여러분은 이미 AOP 전문가입니다!**

- ✅ **@Aspect로 공통 기능 모듈화**를 익혔습니다
- ✅ **Pointcut 표현식**을 자유롭게 작성할 수 있습니다
- ✅ **실무 활용 사례**를 직접 구현해봤습니다
- ✅ **트러블슈팅 능력**을 갖췄습니다

**이제 SpEL로 한 단계 더!**

SpEL을 배우면:
- 🚀 AOP + SpEL 조합으로 **초강력 기능** 구현
- 🔧 설정 값을 **동적으로 주입**하여 유연성 극대화
- 🛡️ 보안, 캐싱, 검증 로직을 **선언적으로 표현**
- 📊 복잡한 조건을 **간결한 표현식**으로 구현

**Spring 마스터까지 거의 다 왔습니다!** 💪

---

## 🎉 축하합니다!

**이제 여러분은**:
- ✅ AOP의 개념과 필요성을 완벽히 이해했습니다
- ✅ 다양한 Advice를 적재적소에 활용할 수 있습니다
- ✅ Pointcut 표현식을 작성하고 테스트할 수 있습니다
- ✅ 실무에서 로깅, 트랜잭션, 성능 측정을 구현할 수 있습니다

---

**[← 이전: Part 1](08-1-AOP개념활용-Part1.md)** | **[목차로 돌아가기](../README.md)**
