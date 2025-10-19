# 09장: SpEL과 프로퍼티 - Part 2 (실습 & 실무 & FAQ & 면접)

**[← 이전: Part 1](09-1-SpEL프로퍼티-Part1.md)** | **[목차로 돌아가기](../README.md)**

---

## 💻 기본 실습

### 실습 1: @Value와 기본값 설정

**난이도**: ⭐⭐☆☆☆

```yaml
# application.yml
app:
  name: My Application
  timeout: 5000
  max-retry: 3
```

```java
@Service
public class AppService {

    // 1. 단순 주입
    @Value("${app.name}")
    private String appName;

    // 2. 기본값 설정 (프로퍼티가 없으면 기본값)
    @Value("${app.timeout:10000}")
    private int timeout;  // app.timeout이 없으면 10000

    @Value("${app.max-connections:100}")
    private int maxConnections;  // 설정 없으면 100

    // 3. null 허용
    @Value("${app.optional-value:#{null}}")
    private String optionalValue;  // 없으면 null

    // 4. 타입 변환
    @Value("${app.enabled:true}")
    private boolean enabled;

    @Value("${app.price:1000.50}")
    private double price;

    // 5. SpEL 표현식
    @Value("#{${app.max-retry} * 2}")
    private int maxRetryDouble;  // max-retry * 2

    // 6. 조건식
    @Value("#{${app.timeout} > 3000 ? 'long' : 'short'}")
    private String timeoutType;

    @PostConstruct
    public void print() {
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("App Name: " + appName);
        System.out.println("Timeout: " + timeout);
        System.out.println("Max Connections: " + maxConnections);
        System.out.println("Optional Value: " + optionalValue);
        System.out.println("Enabled: " + enabled);
        System.out.println("Price: " + price);
        System.out.println("Max Retry Double: " + maxRetryDouble);
        System.out.println("Timeout Type: " + timeoutType);
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━");
    }
}
```

**실행 결과**:
```
━━━━━━━━━━━━━━━━━━━━━━
App Name: My Application
Timeout: 5000
Max Connections: 100
Optional Value: null
Enabled: true
Price: 1000.5
Max Retry Double: 6
Timeout Type: long
━━━━━━━━━━━━━━━━━━━━━━
```

---

### 실습 2: @ConfigurationProperties로 타입 안전한 설정

**난이도**: ⭐⭐⭐☆☆

```yaml
# application.yml
server:
  host: localhost
  port: 8080
  ssl:
    enabled: true
    key-store: /path/to/keystore.jks
    key-store-password: secret
  thread-pool:
    core-size: 10
    max-size: 50
    queue-capacity: 100
  allowed-origins:
    - http://localhost:3000
    - http://localhost:8080
```

```java
// 1. Properties 클래스
@Component
@ConfigurationProperties(prefix = "server")
@Validated
@Data
public class ServerProperties {

    @NotBlank
    private String host;

    @Min(1024)
    @Max(65535)
    private int port;

    private Ssl ssl = new Ssl();
    private ThreadPool threadPool = new ThreadPool();
    private List<String> allowedOrigins = new ArrayList<>();

    @Data
    public static class Ssl {
        private boolean enabled;
        private String keyStore;
        private String keyStorePassword;
    }

    @Data
    public static class ThreadPool {
        @Min(1)
        private int coreSize;

        @Min(1)
        private int maxSize;

        @Min(0)
        private int queueCapacity;
    }
}

// 2. 사용
@Service
@RequiredArgsConstructor
public class ServerConfigService {

    private final ServerProperties serverProperties;

    @PostConstruct
    public void printConfig() {
        System.out.println("━━━━━━━━━━ Server Config ━━━━━━━━━━");
        System.out.println("Host: " + serverProperties.getHost());
        System.out.println("Port: " + serverProperties.getPort());

        System.out.println("\n📌 SSL:");
        System.out.println("  - Enabled: " + serverProperties.getSsl().isEnabled());
        System.out.println("  - KeyStore: " + serverProperties.getSsl().getKeyStore());

        System.out.println("\n📌 Thread Pool:");
        System.out.println("  - Core Size: " + serverProperties.getThreadPool().getCoreSize());
        System.out.println("  - Max Size: " + serverProperties.getThreadPool().getMaxSize());
        System.out.println("  - Queue Capacity: " + serverProperties.getThreadPool().getQueueCapacity());

        System.out.println("\n📌 Allowed Origins:");
        serverProperties.getAllowedOrigins().forEach(origin ->
            System.out.println("  - " + origin)
        );
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    }
}
```

**실행 결과**:
```
━━━━━━━━━━ Server Config ━━━━━━━━━━
Host: localhost
Port: 8080

📌 SSL:
  - Enabled: true
  - KeyStore: /path/to/keystore.jks

📌 Thread Pool:
  - Core Size: 10
  - Max Size: 50
  - Queue Capacity: 100

📌 Allowed Origins:
  - http://localhost:3000
  - http://localhost:8080
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 실습 3: Environment를 통한 동적 설정 읽기

**난이도**: ⭐⭐⭐☆☆

```java
@Service
public class DynamicConfigService {

    @Autowired
    private Environment env;

    public void printAllConfigs() {
        System.out.println("━━━━━━ Environment 정보 ━━━━━━");

        // 1. 활성 프로파일
        String[] activeProfiles = env.getActiveProfiles();
        System.out.println("📌 Active Profiles: " +
            (activeProfiles.length > 0 ? Arrays.toString(activeProfiles) : "default"));

        // 2. 기본 프로파일
        String[] defaultProfiles = env.getDefaultProfiles();
        System.out.println("📌 Default Profiles: " + Arrays.toString(defaultProfiles));

        // 3. 프로퍼티 읽기 (기본값 포함)
        System.out.println("\n📌 Application Properties:");
        System.out.println("  - app.name: " + env.getProperty("app.name", "Unknown"));
        System.out.println("  - app.version: " + env.getProperty("app.version", "1.0.0"));
        System.out.println("  - app.timeout: " + env.getProperty("app.timeout", Integer.class, 5000));

        // 4. 시스템 프로퍼티
        System.out.println("\n📌 System Properties:");
        System.out.println("  - user.name: " + env.getProperty("user.name"));
        System.out.println("  - user.home: " + env.getProperty("user.home"));
        System.out.println("  - java.version: " + env.getProperty("java.version"));

        // 5. 환경 변수
        System.out.println("\n📌 Environment Variables:");
        System.out.println("  - JAVA_HOME: " + env.getProperty("JAVA_HOME"));
        System.out.println("  - PATH: " + env.getProperty("PATH", "Not Set"));

        // 6. 프로파일 매칭
        System.out.println("\n📌 Profile Matching:");
        System.out.println("  - Is Dev? " + env.acceptsProfiles(Profiles.of("dev")));
        System.out.println("  - Is Prod? " + env.acceptsProfiles(Profiles.of("prod")));
        System.out.println("  - Is Dev or Staging? " +
            env.acceptsProfiles(Profiles.of("dev | staging")));

        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    }

    // 프로파일에 따라 다른 Bean 반환
    public DataSource getDataSource() {
        if (env.acceptsProfiles(Profiles.of("dev"))) {
            return createH2DataSource();
        } else if (env.acceptsProfiles(Profiles.of("prod"))) {
            return createMySQLDataSource();
        } else {
            return createDefaultDataSource();
        }
    }

    private DataSource createH2DataSource() {
        System.out.println("Creating H2 DataSource (Dev)");
        // H2 DataSource 생성
        return null;
    }

    private DataSource createMySQLDataSource() {
        System.out.println("Creating MySQL DataSource (Prod)");
        // MySQL DataSource 생성
        return null;
    }

    private DataSource createDefaultDataSource() {
        System.out.println("Creating Default DataSource");
        return null;
    }
}
```

---

### 실습 4: SpEL로 복잡한 계산

**난이도**: ⭐⭐⭐⭐☆

```yaml
# application.yml
pricing:
  base-price: 10000
  tax-rate: 0.1
  discount-rate: 0.2
  members:
    - name: John
      level: GOLD
    - name: Jane
      level: SILVER
```

```java
@Component
@ConfigurationProperties(prefix = "pricing")
@Data
public class PricingConfig {
    private int basePrice;
    private double taxRate;
    private double discountRate;
    private List<Member> members;

    @Data
    public static class Member {
        private String name;
        private String level;
    }
}

@Service
public class PricingService {

    @Autowired
    private PricingConfig pricingConfig;

    // 1. 계산 표현식
    @Value("#{${pricing.base-price} * (1 + ${pricing.tax-rate})}")
    private int priceWithTax;

    // 2. 할인 적용 가격
    @Value("#{${pricing.base-price} * (1 - ${pricing.discount-rate}) * (1 + ${pricing.tax-rate})}")
    private int discountedPrice;

    // 3. 조건부 가격
    @Value("#{${pricing.base-price} > 10000 ? 'Premium' : 'Standard'}")
    private String priceCategory;

    // 4. 회원 필터링 (GOLD 등급만)
    @Value("#{pricingConfig.members.?[level == 'GOLD']}")
    private List<PricingConfig.Member> goldMembers;

    // 5. 회원 이름 리스트
    @Value("#{pricingConfig.members.![name]}")
    private List<String> memberNames;

    // 6. 첫 번째 회원 이름
    @Value("#{pricingConfig.members[0].name}")
    private String firstMemberName;

    @PostConstruct
    public void printPricing() {
        System.out.println("━━━━━━ Pricing Info ━━━━━━");
        System.out.println("Base Price: " + pricingConfig.getBasePrice());
        System.out.println("Price with Tax: " + priceWithTax);
        System.out.println("Discounted Price: " + discountedPrice);
        System.out.println("Price Category: " + priceCategory);

        System.out.println("\n📌 Gold Members:");
        goldMembers.forEach(m ->
            System.out.println("  - " + m.getName() + " (" + m.getLevel() + ")")
        );

        System.out.println("\n📌 All Member Names:");
        System.out.println("  " + memberNames);

        System.out.println("\n📌 First Member: " + firstMemberName);
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━");
    }
}
```

---

### 실습 5: 커스텀 프로퍼티 소스

**난이도**: ⭐⭐⭐⭐⭐

```java
// 1. 커스텀 프로퍼티 파일
@Configuration
@PropertySource("classpath:custom.properties")
public class CustomPropertyConfig {
}

// custom.properties
// custom.message=Hello from custom properties
// custom.timeout=3000

// 2. 프로그래밍 방식으로 프로퍼티 소스 추가
@Configuration
public class DynamicPropertyConfig {

    @Bean
    public static PropertySourcesPlaceholderConfigurer propertyConfigurer() {
        PropertySourcesPlaceholderConfigurer configurer =
            new PropertySourcesPlaceholderConfigurer();

        // 프로그래밍 방식으로 프로퍼티 추가
        Properties properties = new Properties();
        properties.setProperty("dynamic.property", "Dynamic Value");
        properties.setProperty("dynamic.number", "999");

        configurer.setProperties(properties);
        return configurer;
    }
}

// 3. 환경 변수 우선순위 확인
@Service
public class PropertyPriorityService {

    // application.yml: test.value=from-yml
    // custom.properties: test.value=from-custom
    // 환경 변수: TEST_VALUE=from-env
    // Command Line: --test.value=from-cli

    @Value("${test.value}")
    private String testValue;

    @PostConstruct
    public void printPriority() {
        System.out.println("Test Value (우선순위 적용): " + testValue);
        // 우선순위: CLI > 환경변수 > custom.properties > application.yml
    }
}
```

---

## 🏢 실무 활용 사례

### 사례 1: 카카오 - 환경별 설정 관리

```java
// 사용 목적: Local/Dev/Staging/Prod 환경별 설정 완전 분리
// 규모: 100개 마이크로서비스
// 효과: 환경 설정 실수 제로, 보안 강화

// application.yml (공통)
spring:
  application:
    name: kakao-payment-service

logging:
  level:
    root: INFO

// application-local.yml (로컬)
datasource:
  url: jdbc:h2:mem:testdb
  username: sa
  password:

external-api:
  payment:
    url: http://localhost:9000/mock-payment
    timeout: 5000

// application-dev.yml (개발)
datasource:
  url: jdbc:mysql://dev-db:3306/payment
  username: dev_user
  password: ${DB_PASSWORD}  // 환경 변수

external-api:
  payment:
    url: https://test-payment.kakao.com
    timeout: 10000

// application-prod.yml (운영)
datasource:
  url: jdbc:mysql://prod-db:3306/payment
  username: ${DB_USERNAME}  // Secrets Manager
  password: ${DB_PASSWORD}

external-api:
  payment:
    url: https://payment.kakao.com
    timeout: 30000
    api-key: ${PAYMENT_API_KEY}

// Java 설정
@Component
@ConfigurationProperties(prefix = "datasource")
@Validated
@Data
public class DataSourceProperties {

    @NotBlank
    private String url;

    @NotBlank
    private String username;

    private String password;
}

@Component
@ConfigurationProperties(prefix = "external-api.payment")
@Validated
@Data
public class PaymentApiProperties {

    @NotBlank
    @URL
    private String url;

    @Min(1000)
    private int timeout;

    private String apiKey;
}

// 성과:
// - 환경별 설정 완전 분리 → 설정 실수 제로
// - 민감 정보 환경 변수 관리 → 보안 강화
// - 타입 안전성 → 컴파일 타임 오류 검증
```

### 사례 2: 네이버 - Feature Toggle 관리

```java
// 사용 목적: 신기능 활성화/비활성화를 코드 변경 없이 설정으로 제어
// 규모: 월 50개 신기능 출시
// 효과: 배포와 출시 분리, 안전한 롤아웃

// application.yml
features:
  new-search-ui:
    enabled: false
    rollout-percentage: 0
  ai-recommendation:
    enabled: true
    rollout-percentage: 100
  instant-messaging:
    enabled: true
    rollout-percentage: 50  # 50% 사용자에게만 활성화

// FeatureProperties.java
@Component
@ConfigurationProperties(prefix = "features")
@Data
public class FeatureProperties {

    private Feature newSearchUi = new Feature();
    private Feature aiRecommendation = new Feature();
    private Feature instantMessaging = new Feature();

    @Data
    public static class Feature {
        private boolean enabled;
        private int rolloutPercentage;
    }
}

// FeatureToggleService.java
@Service
@RequiredArgsConstructor
public class FeatureToggleService {

    private final FeatureProperties featureProperties;

    public boolean isEnabled(String featureName, String userId) {
        Feature feature = getFeature(featureName);

        if (!feature.isEnabled()) {
            return false;
        }

        // 사용자 ID 해시로 롤아웃 비율 결정
        int userHash = Math.abs(userId.hashCode() % 100);
        return userHash < feature.getRolloutPercentage();
    }

    private Feature getFeature(String featureName) {
        return switch (featureName) {
            case "new-search-ui" -> featureProperties.getNewSearchUi();
            case "ai-recommendation" -> featureProperties.getAiRecommendation();
            case "instant-messaging" -> featureProperties.getInstantMessaging();
            default -> new Feature();
        };
    }
}

// 사용
@RestController
public class SearchController {

    @Autowired
    private FeatureToggleService featureToggle;

    @GetMapping("/search")
    public SearchResult search(@RequestParam String query,
                              @RequestHeader String userId) {

        if (featureToggle.isEnabled("new-search-ui", userId)) {
            return newSearchService.search(query);  // 신규 UI
        } else {
            return legacySearchService.search(query);  // 기존 UI
        }
    }
}

// 성과:
// - 코드 변경 없이 Feature On/Off
// - 점진적 롤아웃 (5% → 50% → 100%)
// - 장애 발생 시 즉시 Feature Off (재배포 불필요)
```

### 사례 3: 쿠팡 - 다중 환경 프로퍼티 관리

```java
// 사용 목적: Config Server로 중앙 집중식 설정 관리
// 규모: 50개 마이크로서비스, 200개 설정 파일
// 효과: 설정 변경 시간 1시간 → 1분 (98% 단축)

// 1. Config Server 연동
// bootstrap.yml
spring:
  application:
    name: coupang-order-service
  cloud:
    config:
      uri: https://config-server.coupang.com
      profile: ${SPRING_PROFILES_ACTIVE:dev}
      label: main

// 2. Config Server의 설정 파일
// Git Repository: config-repo/coupang-order-service-dev.yml
database:
  master:
    url: jdbc:mysql://dev-master:3306/orders
    pool-size: 10
  slave:
    url: jdbc:mysql://dev-slave:3306/orders
    pool-size: 20

redis:
  host: dev-redis
  port: 6379

messaging:
  kafka:
    brokers: dev-kafka:9092
    topics:
      order-created: order.created.v1

// Git Repository: coupang-order-service-prod.yml
database:
  master:
    url: ${DB_MASTER_URL}
    pool-size: 100
  slave:
    url: ${DB_SLAVE_URL}
    pool-size: 200

redis:
  host: ${REDIS_HOST}
  port: 6379
  cluster:
    nodes: ${REDIS_CLUSTER_NODES}

messaging:
  kafka:
    brokers: ${KAFKA_BROKERS}
    topics:
      order-created: order.created.v1

// 3. 동적 설정 갱신 (@RefreshScope)
@RestController
@RefreshScope  // /actuator/refresh 호출 시 설정 재로드
public class OrderController {

    @Value("${order.max-items:100}")
    private int maxItems;

    @GetMapping("/config/max-items")
    public int getMaxItems() {
        return maxItems;  // 설정 변경 즉시 반영
    }
}

// 4. 설정 변경 자동화
// Config Server에서 설정 변경
// → Webhook으로 각 서비스에 /actuator/refresh 요청
// → 재시작 없이 설정 반영

// 성과:
// - 설정 중앙 관리 → 일관성 100%
// - 설정 변경 즉시 반영 (재배포 불필요)
// - Git으로 설정 이력 관리 → 롤백 쉬움
// - 설정 변경 시간: 1시간 → 1분
```

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: @Value 기본값 문법 실수로 애플리케이션 시작 실패

**상황**: 신입 개발자가 @Value에 기본값을 설정했는데 애플리케이션이 시작되지 않는 문제 발생

```java
// ❌ 주니어 개발자가 작성한 코드
@Service
public class EmailService {

    // ⚠️ 잘못된 기본값 문법
    @Value("${email.timeout=5000}")  // ❌ = 사용
    private int timeout;

    @Value("${email.host : 'localhost'}")  // ❌ 공백 포함, 작은따옴표
    private String host;

    @Value("${email.port:}")  // ❌ 빈 문자열 기본값
    private int port;

    @Value("${email.enabled}")  // ❌ 기본값 없음, 프로퍼티 누락 시 에러
    private boolean enabled;
}
```

**문제점**:
- **잘못된 구분자**: `=`를 사용했지만 올바른 구분자는 `:`
- **공백 포함**: `: 'localhost'`처럼 콜론 뒤에 공백이 있으면 " localhost"로 인식
- **잘못된 따옴표**: 기본값에 작은따옴표 사용 시 문자열로 인식 안 됨
- **빈 기본값**: 타입 변환 실패 (빈 문자열 → int 변환 불가)
- **기본값 누락**: 프로퍼티가 없으면 애플리케이션 시작 실패

**장애 상황**:
```
[에러 로그]
org.springframework.beans.factory.BeanCreationException:
  Error creating bean with name 'emailService':
  Injection of autowired dependencies failed

Caused by: java.lang.IllegalArgumentException:
  Could not resolve placeholder 'email.enabled' in value "${email.enabled}"

[증상]
- 애플리케이션 시작 시 즉시 종료
- 모든 프로퍼티가 정의되어 있어야만 시작 가능
- 에러 메시지만 보고는 원인 파악 어려움
```

**해결책**:
```java
// ✅ 올바른 코드
@Service
public class EmailService {

    // ✅ 올바른 기본값 문법: 콜론(:) 사용, 공백 없음
    @Value("${email.timeout:5000}")
    private int timeout;

    // ✅ 문자열은 그대로 작성 (따옴표 불필요)
    @Value("${email.host:localhost}")
    private String host;

    // ✅ int 타입은 숫자 기본값
    @Value("${email.port:25}")
    private int port;

    // ✅ boolean 타입은 true/false
    @Value("${email.enabled:true}")
    private boolean enabled;

    // ✅ null 허용
    @Value("${email.username:#{null}}")
    private String username;

    // ✅ 빈 문자열 기본값 (문자열만 가능)
    @Value("${email.from-name:}")
    private String fromName;

    @PostConstruct
    public void validate() {
        log.info("Email Config: host={}, port={}, timeout={}ms, enabled={}",
            host, port, timeout, enabled);
    }
}
```

**배운 점**:
- 💡 **기본값 구분자는 콜론(:)**: `${property:defaultValue}` 형식
- 💡 **공백 주의**: 콜론 뒤에 공백 없이 바로 값 작성
- 💡 **타입별 기본값**: String은 그대로, int는 숫자, boolean은 true/false
- 💡 **null 기본값**: `#{null}` SpEL 표현식 사용
- 💡 **항상 기본값 설정**: 설정 누락으로 인한 시작 실패 방지

---

### 시나리오 2: @ConfigurationProperties에서 @Component 누락

**상황**: @ConfigurationProperties를 작성했는데 주입되지 않아 NullPointerException 발생

```java
// ❌ 주니어 개발자가 작성한 코드
@ConfigurationProperties(prefix = "database")
@Data
public class DatabaseProperties {  // ⚠️ @Component 누락!

    private String url;
    private String username;
    private String password;
    private int poolSize;
}

@Service
public class DataSourceService {

    @Autowired
    private DatabaseProperties dbProperties;  // ⚠️ null!

    public DataSource createDataSource() {
        // ❌ NullPointerException 발생!
        return DataSourceBuilder.create()
            .url(dbProperties.getUrl())
            .username(dbProperties.getUsername())
            .password(dbProperties.getPassword())
            .build();
    }
}
```

**문제점**:
- **Bean 등록 누락**: @ConfigurationProperties만 있고 @Component나 @EnableConfigurationProperties가 없음
- **Spring 컨테이너 미관리**: Bean으로 등록되지 않아 주입 불가
- **NullPointerException**: dbProperties가 null인 상태로 메서드 호출
- **런타임 에러**: 컴파일은 성공하지만 실행 시 에러 발생

**장애 상황**:
```
[에러 로그]
java.lang.NullPointerException: Cannot invoke "DatabaseProperties.getUrl()"
  because "this.dbProperties" is null

[증상]
- DataSource 생성 시 NPE 발생
- 애플리케이션 시작은 성공하지만 첫 DB 접속 시 에러
- @Autowired는 Optional이 아니므로 주입 실패 시 에러가 발생해야 하는데,
  @ConfigurationProperties Bean이 없어서 주입 자체가 실패
```

**해결책 1: @Component 추가 (가장 간단)**:
```java
// ✅ 해결 방법 1: @Component 추가
@Component
@ConfigurationProperties(prefix = "database")
@Validated
@Data
public class DatabaseProperties {

    @NotBlank
    private String url;

    @NotBlank
    private String username;

    private String password;

    @Min(1)
    @Max(100)
    private int poolSize = 10;
}
```

**해결책 2: @EnableConfigurationProperties 사용 (권장)**:
```java
// ✅ 해결 방법 2: @EnableConfigurationProperties
@ConfigurationProperties(prefix = "database")
@Validated
@Data
public class DatabaseProperties {  // @Component 없어도 OK

    @NotBlank
    private String url;

    @NotBlank
    private String username;

    private String password;

    @Min(1)
    @Max(100)
    private int poolSize = 10;
}

// Configuration 클래스에서 명시적으로 활성화
@Configuration
@EnableConfigurationProperties(DatabaseProperties.class)
public class DataSourceConfig {

    @Bean
    public DataSource dataSource(DatabaseProperties dbProperties) {
        return DataSourceBuilder.create()
            .url(dbProperties.getUrl())
            .username(dbProperties.getUsername())
            .password(dbProperties.getPassword())
            .build();
    }
}
```

**해결책 3: @ConfigurationPropertiesScan 사용 (Spring Boot 2.2+)**:
```java
// ✅ 해결 방법 3: @ConfigurationPropertiesScan
@SpringBootApplication
@ConfigurationPropertiesScan("com.example.config")
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}

// DatabaseProperties는 @Component 없이도 자동 스캔됨
@ConfigurationProperties(prefix = "database")
@Data
public class DatabaseProperties {
    private String url;
    private String username;
    private String password;
    private int poolSize;
}
```

**배운 점**:
- 💡 **@ConfigurationProperties는 Bean이 아님**: 반드시 @Component 추가 또는 @EnableConfigurationProperties로 활성화
- 💡 **권장 방법**: @EnableConfigurationProperties로 명시적 활성화 (의도 명확)
- 💡 **@Validated 활용**: @NotBlank, @Min 등으로 값 검증
- 💡 **기본값 설정**: `private int poolSize = 10;` 형식으로 필드에 기본값 지정

---

### 시나리오 3: SpEL 표현식 문법 오류로 파싱 실패

**상황**: SpEL을 사용했는데 애플리케이션 시작 시 파싱 에러 발생

```java
// ❌ 주니어 개발자가 작성한 코드
@Service
public class PricingService {

    // ⚠️ 잘못된 SpEL 문법들
    @Value("#{{pricing.base-price} * 1.1}")  // ❌ 이중 중괄호
    private int priceWithTax;

    @Value("#{pricing.base-price}")  // ❌ ${} 누락
    private int basePrice;

    @Value("${pricing.discount} > 0.5 ? 'high' : 'low'")  // ❌ #{} 누락
    private String discountLevel;

    @Value("#{${pricing.base-price * 1.1}}")  // ❌ 잘못된 중첩
    private int price;

    @Value("#{T(Math).max(${pricing.min}, ${pricing.max})}")  // ❌ 복잡한 중첩
    private int maxValue;
}
```

**문제점**:
- **이중 중괄호**: `#{{...}}`는 잘못된 문법
- **${} 누락**: 프로퍼티 값을 가져올 때는 반드시 `${}`
- **#{} 누락**: 조건식이나 연산은 SpEL `#{}` 필요
- **잘못된 중첩**: `#{${...}}` 안에 연산식 직접 작성
- **복잡한 표현식**: 가독성 저하 및 디버깅 어려움

**장애 상황**:
```
[에러 로그]
org.springframework.expression.spel.SpelParseException:
  EL1041E: After parsing a valid expression, there is still more data in the expression: 'lcurly({)'

Caused by: org.springframework.beans.factory.BeanCreationException:
  Error creating bean with name 'pricingService':
  Could not resolve placeholder 'pricing.base-price' in value "#{pricing.base-price}"

[증상]
- 애플리케이션 시작 시 즉시 실패
- SpEL 파싱 에러 메시지가 난해함
- 어떤 부분이 잘못됐는지 파악 어려움
```

**해결책**:
```java
// ✅ 올바른 코드
@Service
public class PricingService {

    // ✅ 프로퍼티 참조 후 SpEL 연산
    @Value("#{${pricing.base-price} * 1.1}")
    private double priceWithTax;

    // ✅ 단순 프로퍼티 참조는 ${}만 사용
    @Value("${pricing.base-price}")
    private int basePrice;

    // ✅ 조건식은 #{} 사용
    @Value("#{${pricing.discount} > 0.5 ? 'high' : 'low'}")
    private String discountLevel;

    // ✅ Bean 메서드 호출
    @Value("#{@pricingConfig.calculateFinalPrice(${pricing.base-price})}")
    private int finalPrice;

    // ✅ 정적 메서드 호출 (T() 연산자)
    @Value("#{T(Math).max(${pricing.min-price}, ${pricing.max-price})}")
    private int maxPrice;

    // ✅ 복잡한 로직은 별도 @Bean 메서드로 분리 (권장)
    @Bean
    public int calculatedPrice(@Value("${pricing.base-price}") int basePrice,
                              @Value("${pricing.tax-rate}") double taxRate,
                              @Value("${pricing.discount-rate}") double discountRate) {
        return (int) (basePrice * (1 + taxRate) * (1 - discountRate));
    }
}
```

**SpEL 문법 정리**:
```java
// 1. 프로퍼티 참조
@Value("${property.name}")             // ✅ 단순 프로퍼티
@Value("${property.name:defaultValue}") // ✅ 기본값 포함

// 2. SpEL 연산
@Value("#{10 + 20}")                   // ✅ 리터럴 연산
@Value("#{${price} * 1.1}")            // ✅ 프로퍼티 값으로 연산
@Value("#{${price} > 100 ? 'high' : 'low'}") // ✅ 조건식

// 3. Bean 참조
@Value("#{@myBean}")                   // ✅ Bean 자체
@Value("#{@myBean.property}")          // ✅ Bean의 프로퍼티
@Value("#{@myBean.method()}")          // ✅ Bean의 메서드

// 4. 정적 메서드/상수
@Value("#{T(Math).PI}")                // ✅ 상수
@Value("#{T(Math).max(10, 20)}")       // ✅ 정적 메서드

// 5. 컬렉션 연산
@Value("#{list[0]}")                   // ✅ 인덱스 접근
@Value("#{list.?[price > 100]}")       // ✅ 필터링
@Value("#{list.![name]}")              // ✅ 투영 (projection)
```

**배운 점**:
- 💡 **${} vs #{}**: `${}`는 프로퍼티 참조, `#{}`는 SpEL 표현식
- 💡 **중첩 규칙**: `#{${property} + 10}` 형식으로 프로퍼티를 SpEL에서 사용
- 💡 **복잡한 로직 분리**: SpEL이 복잡해지면 @Bean 메서드로 분리
- 💡 **가독성 우선**: 한 줄에 모든 것을 담으려 하지 말 것

---

### 시나리오 4: Profile별 설정 파일 로딩 실수

**상황**: application-prod.yml이 있는데 운영 환경에서 dev 설정이 적용되는 문제

```java
// ❌ 주니어 개발자의 실수

// 1. 잘못된 프로파일 활성화
// application.yml
spring:
  profiles:
    active: dev  // ⚠️ 기본 설정에 하드코딩!

// 2. 잘못된 파일명
// application-production.yml (❌ production)
// application-prod.yml (✅ 올바른 이름)

// 3. 환경 변수 설정 실수
// Dockerfile
ENV SPRING_PROFILE_ACTIVE=prod  // ❌ 오타! (PROFILE vs PROFILES)

// 4. @Profile 어노테이션 실수
@Configuration
@Profile("production")  // ❌ 파일은 prod인데 어노테이션은 production
public class ProductionConfig {
    // 이 설정이 적용되지 않음!
}
```

**문제점**:
- **프로파일 하드코딩**: application.yml에 활성 프로파일 고정
- **파일명 불일치**: application-production.yml vs @Profile("prod")
- **환경 변수 오타**: SPRING_PROFILE_ACTIVE (틀림) vs SPRING_PROFILES_ACTIVE (맞음)
- **Profile 불일치**: 설정 파일과 @Profile 어노테이션의 프로파일명 불일치

**장애 상황**:
```
[운영 환경 장애]
- 운영 서버인데 개발 DB에 접속
- 데이터 혼재 및 테스트 데이터 노출
- 로깅 레벨이 DEBUG로 설정되어 민감 정보 로그 출력
- 외부 API를 테스트 URL로 호출

[원인 파악 과정]
1. "왜 운영인데 dev 설정이 적용되지?"
2. Environment 확인: env.getActiveProfiles() → ["dev"]
3. 환경 변수 확인: SPRING_PROFILE_ACTIVE=prod (오타 발견!)
4. 긴급 재시작으로 30분 장애
```

**해결책**:
```yaml
# ✅ 올바른 설정

# 1. application.yml (공통 설정, 프로파일 지정 X)
spring:
  application:
    name: my-service
  # ⚠️ active 프로파일은 여기서 지정하지 않음!

logging:
  level:
    root: INFO

---

# 2. application-local.yml (로컬)
spring:
  config:
    activate:
      on-profile: local

datasource:
  url: jdbc:h2:mem:testdb
  username: sa
  password:

logging:
  level:
    root: DEBUG
    com.example: TRACE

---

# 3. application-dev.yml (개발)
spring:
  config:
    activate:
      on-profile: dev

datasource:
  url: jdbc:mysql://dev-db:3306/mydb
  username: dev_user
  password: ${DB_PASSWORD}

---

# 4. application-prod.yml (운영)
spring:
  config:
    activate:
      on-profile: prod

datasource:
  url: jdbc:mysql://prod-db:3306/mydb
  username: ${DB_USERNAME}  # 환경 변수에서 주입
  password: ${DB_PASSWORD}

logging:
  level:
    root: WARN  # 운영은 WARN 이상만
```

```java
// ✅ 올바른 @Profile 사용
@Configuration
@Profile("local")  // ✅ 파일명과 일치
public class LocalConfig {

    @Bean
    public DataSource dataSource() {
        return new EmbeddedDatabaseBuilder()
            .setType(EmbeddedDatabaseType.H2)
            .build();
    }
}

@Configuration
@Profile("prod")  // ✅ 파일명과 일치
public class ProdConfig {

    @Bean
    public DataSource dataSource() {
        // 운영 DataSource 설정
    }
}
```

**환경별 프로파일 활성화 방법**:
```bash
# ✅ 방법 1: 환경 변수 (권장)
export SPRING_PROFILES_ACTIVE=prod
java -jar app.jar

# ✅ 방법 2: Command Line
java -jar app.jar --spring.profiles.active=prod

# ✅ 방법 3: Dockerfile
ENV SPRING_PROFILES_ACTIVE=prod

# ✅ 방법 4: Kubernetes ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  SPRING_PROFILES_ACTIVE: "prod"
```

**프로파일 검증 코드**:
```java
@Component
@RequiredArgsConstructor
public class ProfileValidator {

    private final Environment env;

    @PostConstruct
    public void validateProfile() {
        String[] activeProfiles = env.getActiveProfiles();

        log.info("===========================================");
        log.info("Active Profiles: {}", Arrays.toString(activeProfiles));
        log.info("===========================================");

        // 운영 환경 검증
        if (env.acceptsProfiles(Profiles.of("prod"))) {
            // 운영 환경에서는 디버그 로깅 금지
            String logLevel = env.getProperty("logging.level.root");
            if ("DEBUG".equals(logLevel) || "TRACE".equals(logLevel)) {
                throw new IllegalStateException(
                    "Production profile must not have DEBUG/TRACE logging!"
                );
            }
        }

        // 프로파일이 없으면 경고
        if (activeProfiles.length == 0) {
            log.warn("⚠️  No active profile set! Using 'default' profile.");
        }
    }
}
```

**배운 점**:
- 💡 **프로파일 하드코딩 금지**: application.yml에 active 프로파일 지정하지 말 것
- 💡 **환경 변수 이름**: SPRING_PROFILES_ACTIVE (PROFILES가 복수형!)
- 💡 **파일명 일관성**: application-{profile}.yml과 @Profile("{profile}") 일치
- 💡 **운영 환경 검증**: 시작 시 프로파일과 설정 검증 로직 추가
- 💡 **민감 정보 분리**: 운영 설정은 환경 변수나 Secrets Manager 사용

---

## 🛠️ 실전 프로젝트

### 프로젝트: 다중 환경 설정 관리 시스템

**난이도**: ⭐⭐⭐⭐☆
**예상 소요 시간**: 4-5시간
**학습 목표**: @ConfigurationProperties, Profile, SpEL을 활용한 엔터프라이즈급 설정 관리 시스템 구축

---

### 📋 요구사항 분석

#### 기능 요구사항
- [ ] **환경별 설정 분리**: Local/Dev/Staging/Prod 4개 환경
- [ ] **타입 안전한 설정**: @ConfigurationProperties + @Validated
- [ ] **동적 설정 갱신**: @RefreshScope로 재시작 없이 설정 변경
- [ ] **Feature Toggle**: 기능을 코드 변경 없이 On/Off
- [ ] **민감 정보 암호화**: 비밀번호, API Key 등 환경 변수 관리

#### 기술 요구사항
- [ ] **@ConfigurationProperties**: 타입 안전한 설정 바인딩
- [ ] **Profile**: 환경별 설정 분리
- [ ] **SpEL**: 동적 값 계산 및 조건부 설정
- [ ] **Validation**: @Validated, @NotBlank, @Min 등으로 검증

---

### 🏗️ 프로젝트 구조

```
multi-env-config-system/
├── src/main/java/com/example/config/
│   ├── ConfigApplication.java
│   ├── properties/
│   │   ├── ApplicationProperties.java          # 애플리케이션 공통 설정
│   │   ├── DatabaseProperties.java             # 데이터베이스 설정
│   │   ├── CacheProperties.java                # 캐시 설정
│   │   ├── ExternalApiProperties.java          # 외부 API 설정
│   │   └── FeatureProperties.java              # Feature Toggle 설정
│   ├── config/
│   │   ├── DataSourceConfig.java               # DataSource 설정
│   │   ├── CacheConfig.java                    # Cache 설정
│   │   └── FeatureToggleConfig.java            # Feature Toggle 활성화
│   ├── service/
│   │   ├── ConfigService.java                  # 설정 조회 서비스
│   │   └── FeatureToggleService.java           # Feature Toggle 서비스
│   └── controller/
│       └── ConfigController.java               # 설정 확인 API
└── src/main/resources/
    ├── application.yml                          # 공통 설정
    ├── application-local.yml                    # 로컬 환경
    ├── application-dev.yml                      # 개발 환경
    ├── application-staging.yml                  # 스테이징 환경
    └── application-prod.yml                     # 운영 환경
```

---

### 🎯 설계 의사결정

#### 결정 1: @Value vs @ConfigurationProperties
**선택**: @ConfigurationProperties
**이유**: 타입 안전성, 검증, 중첩 구조 지원, IDE 자동완성
**대안**: @Value (단순 설정에만 사용)

#### 결정 2: Profile 명명 규칙
**선택**: local, dev, staging, prod (짧고 명확)
**이유**: 환경 변수, 파일명, @Profile에서 일관성 유지
**대안**: development, production (길고 타이핑 불편)

#### 결정 3: 민감 정보 관리
**선택**: 환경 변수 + Placeholder
**이유**: 코드/설정 파일에 평문 비밀번호 저장 방지
**대안**: Vault, AWS Secrets Manager (더 안전하지만 복잡)

---

### 🔨 단계별 구현 가이드

#### 1단계: 프로젝트 초기 설정

```gradle
// build.gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-validation'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-cache'

    implementation 'org.springframework.cloud:spring-cloud-starter-config'  // Config Server (Optional)
    implementation 'org.springframework.boot:spring-boot-starter-actuator'  // /actuator/refresh

    runtimeOnly 'com.h2database:h2'
    runtimeOnly 'com.mysql:mysql-connector-j'

    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
    annotationProcessor 'org.springframework.boot:spring-boot-configuration-processor'  // 자동완성
}
```

---

#### 2단계: 환경별 설정 파일 작성

```yaml
# application.yml (공통 설정)
spring:
  application:
    name: multi-env-config-system

logging:
  level:
    root: INFO
    com.example: DEBUG

management:
  endpoints:
    web:
      exposure:
        include: health,info,env,configprops,refresh

---

# application-local.yml (로컬)
spring:
  config:
    activate:
      on-profile: local

application:
  environment: local
  api-url: http://localhost:8080

database:
  url: jdbc:h2:mem:localdb
  username: sa
  password:
  pool-size: 5

cache:
  enabled: false
  ttl: 60

external-api:
  payment:
    url: http://localhost:9000/mock
    timeout: 5000
    api-key: local-test-key

features:
  new-ui:
    enabled: true
    rollout-percentage: 100
  ai-recommendation:
    enabled: false

---

# application-dev.yml (개발)
spring:
  config:
    activate:
      on-profile: dev

application:
  environment: dev
  api-url: https://dev.example.com

database:
  url: jdbc:mysql://dev-db:3306/mydb
  username: dev_user
  password: ${DB_PASSWORD}  # 환경 변수
  pool-size: 10

cache:
  enabled: true
  ttl: 300

external-api:
  payment:
    url: https://test-payment.example.com
    timeout: 10000
    api-key: ${PAYMENT_API_KEY}

features:
  new-ui:
    enabled: true
    rollout-percentage: 50  # 50% 롤아웃
  ai-recommendation:
    enabled: true
    rollout-percentage: 10  # 10% 테스트

---

# application-prod.yml (운영)
spring:
  config:
    activate:
      on-profile: prod

application:
  environment: prod
  api-url: https://api.example.com

database:
  url: ${DB_URL}  # 환경 변수 (RDS URL)
  username: ${DB_USERNAME}
  password: ${DB_PASSWORD}
  pool-size: 50

cache:
  enabled: true
  ttl: 3600

external-api:
  payment:
    url: ${PAYMENT_API_URL}
    timeout: 30000
    api-key: ${PAYMENT_API_KEY}

features:
  new-ui:
    enabled: true
    rollout-percentage: 100  # 전체 출시
  ai-recommendation:
    enabled: false  # 운영 출시 전
```

---

#### 3단계: Properties 클래스 작성

```java
// 1. ApplicationProperties.java
@Component
@ConfigurationProperties(prefix = "application")
@Validated
@Data
public class ApplicationProperties {

    @NotBlank
    private String environment;

    @NotBlank
    @URL
    private String apiUrl;
}

// 2. DatabaseProperties.java
@Component
@ConfigurationProperties(prefix = "database")
@Validated
@Data
public class DatabaseProperties {

    @NotBlank
    private String url;

    @NotBlank
    private String username;

    private String password;  // 민감 정보

    @Min(1)
    @Max(100)
    private int poolSize;

    // SpEL로 동적 계산
    @Value("#{databaseProperties.poolSize * 2}")
    private int maxPoolSize;
}

// 3. CacheProperties.java
@Component
@ConfigurationProperties(prefix = "cache")
@Data
public class CacheProperties {

    private boolean enabled;

    @Min(60)
    private int ttl;  // seconds

    // SpEL 조건식
    @Value("#{cacheProperties.enabled and cacheProperties.ttl > 300}")
    private boolean isLongTermCache;
}

// 4. ExternalApiProperties.java
@Component
@ConfigurationProperties(prefix = "external-api")
@Validated
@Data
public class ExternalApiProperties {

    private Payment payment;

    @Data
    @Validated
    public static class Payment {

        @NotBlank
        @URL
        private String url;

        @Min(1000)
        private int timeout;

        @NotBlank
        private String apiKey;
    }
}

// 5. FeatureProperties.java
@Component
@ConfigurationProperties(prefix = "features")
@Data
public class FeatureProperties {

    private Feature newUi = new Feature();
    private Feature aiRecommendation = new Feature();

    @Data
    public static class Feature {
        private boolean enabled;
        private int rolloutPercentage;
    }
}
```

---

#### 4단계: Configuration 클래스 작성

```java
// DataSourceConfig.java
@Configuration
@RequiredArgsConstructor
public class DataSourceConfig {

    private final DatabaseProperties dbProperties;

    @Bean
    public DataSource dataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(dbProperties.getUrl());
        config.setUsername(dbProperties.getUsername());
        config.setPassword(dbProperties.getPassword());
        config.setMaximumPoolSize(dbProperties.getPoolSize());

        return new HikariDataSource(config);
    }
}

// CacheConfig.java
@Configuration
@EnableCaching
@RequiredArgsConstructor
public class CacheConfig {

    private final CacheProperties cacheProperties;

    @Bean
    @ConditionalOnProperty(name = "cache.enabled", havingValue = "true")
    public CacheManager cacheManager() {
        SimpleCacheManager cacheManager = new SimpleCacheManager();

        ConcurrentMapCache cache = new ConcurrentMapCache("default");
        cacheManager.setCaches(Arrays.asList(cache));

        return cacheManager;
    }

    @PostConstruct
    public void printCacheConfig() {
        log.info("━━━━━━━━ Cache Config ━━━━━━━━");
        log.info("Enabled: {}", cacheProperties.isEnabled());
        log.info("TTL: {} seconds", cacheProperties.getTtl());
        log.info("Long-term cache: {}", cacheProperties.isLongTermCache());
        log.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    }
}
```

---

#### 5단계: Service 계층 구현

```java
// ConfigService.java
@Service
@RequiredArgsConstructor
public class ConfigService {

    private final Environment env;
    private final ApplicationProperties appProperties;
    private final DatabaseProperties dbProperties;
    private final CacheProperties cacheProperties;
    private final ExternalApiProperties apiProperties;

    public Map<String, Object> getAllConfigs() {
        Map<String, Object> configs = new LinkedHashMap<>();

        // 환경 정보
        configs.put("environment", appProperties.getEnvironment());
        configs.put("activeProfiles", env.getActiveProfiles());

        // 데이터베이스 (비밀번호 마스킹)
        Map<String, Object> dbConfig = new LinkedHashMap<>();
        dbConfig.put("url", dbProperties.getUrl());
        dbConfig.put("username", dbProperties.getUsername());
        dbConfig.put("password", maskPassword(dbProperties.getPassword()));
        dbConfig.put("poolSize", dbProperties.getPoolSize());
        configs.put("database", dbConfig);

        // 캐시
        Map<String, Object> cacheConfig = new LinkedHashMap<>();
        cacheConfig.put("enabled", cacheProperties.isEnabled());
        cacheConfig.put("ttl", cacheProperties.getTtl());
        configs.put("cache", cacheConfig);

        // 외부 API (API Key 마스킹)
        Map<String, Object> apiConfig = new LinkedHashMap<>();
        apiConfig.put("url", apiProperties.getPayment().getUrl());
        apiConfig.put("timeout", apiProperties.getPayment().getTimeout());
        apiConfig.put("apiKey", maskApiKey(apiProperties.getPayment().getApiKey()));
        configs.put("externalApi", apiConfig);

        return configs;
    }

    private String maskPassword(String password) {
        if (password == null || password.isEmpty()) {
            return "****";
        }
        return "****" + password.substring(Math.max(0, password.length() - 2));
    }

    private String maskApiKey(String apiKey) {
        if (apiKey == null || apiKey.length() < 8) {
            return "****";
        }
        return apiKey.substring(0, 4) + "****" + apiKey.substring(apiKey.length() - 4);
    }
}

// FeatureToggleService.java
@Service
@RequiredArgsConstructor
public class FeatureToggleService {

    private final FeatureProperties featureProperties;

    public boolean isEnabled(String featureName, String userId) {
        Feature feature = getFeature(featureName);

        if (!feature.isEnabled()) {
            return false;
        }

        // 롤아웃 비율에 따라 활성화
        int userHash = Math.abs(userId.hashCode() % 100);
        boolean enabled = userHash < feature.getRolloutPercentage();

        log.debug("Feature '{}' for user '{}': {} (hash={}, rollout={}%)",
            featureName, userId, enabled, userHash, feature.getRolloutPercentage());

        return enabled;
    }

    private Feature getFeature(String featureName) {
        return switch (featureName) {
            case "new-ui" -> featureProperties.getNewUi();
            case "ai-recommendation" -> featureProperties.getAiRecommendation();
            default -> {
                log.warn("Unknown feature: {}", featureName);
                yield new Feature();  // 비활성화된 기본값
            }
        };
    }
}
```

---

#### 6단계: Controller 구현

```java
@RestController
@RequestMapping("/api/config")
@RequiredArgsConstructor
public class ConfigController {

    private final ConfigService configService;
    private final FeatureToggleService featureToggleService;
    private final ApplicationProperties appProperties;

    @GetMapping
    public Map<String, Object> getAllConfigs() {
        return configService.getAllConfigs();
    }

    @GetMapping("/environment")
    public String getEnvironment() {
        return appProperties.getEnvironment();
    }

    @GetMapping("/feature/{featureName}")
    public boolean checkFeature(
        @PathVariable String featureName,
        @RequestHeader(value = "User-Id", defaultValue = "anonymous") String userId
    ) {
        return featureToggleService.isEnabled(featureName, userId);
    }
}
```

---

### 🎬 실행 및 검증

```bash
# 로컬 환경 실행
./gradlew bootRun --args='--spring.profiles.active=local'

# 개발 환경 실행 (환경 변수 포함)
export DB_PASSWORD=dev123
export PAYMENT_API_KEY=test-key-123
./gradlew bootRun --args='--spring.profiles.active=dev'

# 설정 확인
curl http://localhost:8080/api/config

# 환경 확인
curl http://localhost:8080/api/config/environment

# Feature Toggle 확인
curl -H "User-Id: user123" http://localhost:8080/api/config/feature/new-ui
```

**실행 결과**:
```json
{
  "environment": "local",
  "activeProfiles": ["local"],
  "database": {
    "url": "jdbc:h2:mem:localdb",
    "username": "sa",
    "password": "****",
    "poolSize": 5
  },
  "cache": {
    "enabled": false,
    "ttl": 60
  },
  "externalApi": {
    "url": "http://localhost:9000/mock",
    "timeout": 5000,
    "apiKey": "loca****-key"
  }
}
```

---

### ✅ 프로젝트 완성 체크리스트

- [ ] 4개 환경 설정 파일 작성 (local, dev, staging, prod)
- [ ] @ConfigurationProperties로 타입 안전한 설정
- [ ] @Validated로 값 검증
- [ ] 민감 정보 환경 변수 처리
- [ ] Feature Toggle 구현
- [ ] 설정 조회 API 구현
- [ ] 각 환경에서 실행 테스트

---

### 🎓 프로젝트에서 배운 핵심 개념

1. **@ConfigurationProperties의 강력함**: 타입 안전성, 검증, 중첩 구조
2. **Profile 활용**: 환경별 설정 완전 분리
3. **환경 변수 활용**: 민감 정보 보호
4. **Feature Toggle**: 코드 변경 없이 기능 제어
5. **SpEL 활용**: 동적 값 계산 및 조건부 설정

---

## ❓ FAQ

<details>
<summary><strong>Q1: @Value와 @ConfigurationProperties 중 어떤 것을 사용해야 하나요?</strong></summary>

**A**: **2개 이상의 관련 설정은 @ConfigurationProperties 권장**합니다.

```java
// ❌ @Value: 설정이 많으면 관리 어려움
@Value("${email.host}")
private String host;

@Value("${email.port}")
private int port;

@Value("${email.username}")
private String username;
// ... 10개, 20개 계속 증가

// ✅ @ConfigurationProperties: 타입 안전, 검증, 자동완성
@ConfigurationProperties(prefix = "email")
@Validated
@Data
public class EmailProperties {
    @NotBlank
    private String host;

    @Min(1)
    private int port;

    @Email
    private String username;
}
```

**선택 기준**:
- 단일 값, 간단한 설정 → @Value
- 2개 이상 관련 설정, 검증 필요 → @ConfigurationProperties

</details>

<details>
<summary><strong>Q2: SpEL에서 null-safe 처리는 어떻게 하나요?</strong></summary>

**A**: **안전 탐색 연산자(?.)와 엘비스 연산자(?:)** 사용합니다.

```java
// 안전 탐색 연산자 (?.)
@Value("#{user?.name}")  // user가 null이면 null 반환 (NPE 방지)
private String userName;

// 엘비스 연산자 (?:)
@Value("#{user?.name ?: 'Guest'}")  // user.name이 null이면 'Guest'
private String userNameWithDefault;

// 조합
@Value("#{user?.address?.city ?: 'Unknown'}")
private String city;
```

</details>

<details>
<summary><strong>Q3: 프로퍼티에 리스트와 맵을 어떻게 주입하나요?</strong></summary>

**A**: **YAML 형식과 SpEL 사용**합니다.

```yaml
# 리스트
app:
  allowed-origins:
    - http://localhost:3000
    - http://localhost:8080

# 맵
app:
  database:
    master: jdbc:mysql://master:3306/db
    slave: jdbc:mysql://slave:3306/db
```

```java
// 리스트 주입
@Value("${app.allowed-origins}")
private List<String> allowedOrigins;

// 맵 주입 (SpEL 필요)
@Value("#{${app.database}}")
private Map<String, String> databases;

// 또는 @ConfigurationProperties (권장)
@ConfigurationProperties(prefix = "app")
@Data
public class AppProperties {
    private List<String> allowedOrigins;
    private Map<String, String> database;
}
```

</details>

<details>
<summary><strong>Q4: SpEL에서 컬렉션을 어떻게 처리하나요?</strong></summary>

**A**: **필터링(?[]), 투영(!![]), 인덱스 접근** 등을 사용합니다.

```java
@Component
@ConfigurationProperties(prefix = "products")
@Data
public class ProductConfig {
    private List<Product> items;

    @Data
    public static class Product {
        private String name;
        private int price;
        private String category;
    }
}

@Service
public class ProductService {

    // 필터링: ?[조건]
    @Value("#{productConfig.items.?[price > 10000]}")
    private List<Product> expensiveProducts;

    // 투영: ![필드]
    @Value("#{productConfig.items.![name]}")
    private List<String> productNames;

    // 인덱스 접근
    @Value("#{productConfig.items[0]}")
    private Product firstProduct;

    // 조합: 비싼 상품의 이름만
    @Value("#{productConfig.items.?[price > 10000].![name]}")
    private List<String> expensiveProductNames;

    // 선택: ^[조건] (첫 번째), $[조건] (마지막)
    @Value("#{productConfig.items.^[category == 'FOOD']}")
    private Product firstFood;
}
```

</details>

<details>
<summary><strong>Q5: 환경 변수와 시스템 프로퍼티의 우선순위는?</strong></summary>

**A**: **Command Line > 환경 변수 > application.yml** 순입니다.

```bash
# 우선순위 테스트
# 1. application.yml
server.port=8080

# 2. 환경 변수 (우선순위 높음)
export SERVER_PORT=9090

# 3. Command Line (최우선)
java -jar app.jar --server.port=7070
# → 7070이 적용됨

# 실제 우선순위 (높음 → 낮음)
# 1. Command Line Arguments
# 2. SPRING_APPLICATION_JSON (환경 변수)
# 3. OS 환경 변수
# 4. Java System Properties (System.setProperty)
# 5. RandomValuePropertySource
# 6. application-{profile}.yml
# 7. application.yml
# 8. @PropertySource
# 9. 기본값
```

**확인 방법**:
```java
@Component
public class PropertyPriorityChecker {

    @Value("${server.port}")
    private int port;

    @Autowired
    private Environment env;

    @PostConstruct
    public void check() {
        log.info("Server Port: {}", port);
        log.info("From Environment: {}", env.getProperty("server.port"));
        log.info("System Property: {}", System.getProperty("server.port"));
        log.info("Env Variable: {}", System.getenv("SERVER_PORT"));
    }
}
```

</details>

<details>
<summary><strong>Q6: @RefreshScope는 무엇이고 언제 사용하나요?</strong></summary>

**A**: **설정을 재시작 없이 갱신**할 때 사용합니다.

```java
// 1. @RefreshScope Bean
@RestController
@RefreshScope  // 이 Bean은 /actuator/refresh 호출 시 재생성됨
public class DynamicConfigController {

    @Value("${feature.enabled:false}")
    private boolean featureEnabled;

    @GetMapping("/feature/status")
    public boolean getFeatureStatus() {
        return featureEnabled;  // 갱신된 값 반환
    }
}

// 2. application.yml
management:
  endpoints:
    web:
      exposure:
        include: refresh

feature:
  enabled: false

// 3. 설정 변경 후 갱신
# 외부에서 feature.enabled를 true로 변경 (Config Server, K8s ConfigMap 등)
# POST 요청으로 갱신
curl -X POST http://localhost:8080/actuator/refresh

# 응답
["feature.enabled"]  # 갱신된 프로퍼티 목록

// 4. 갱신 확인
curl http://localhost:8080/feature/status
# → true (재시작 없이 변경됨!)
```

**주의사항**:
- @RefreshScope Bean은 매번 새로 생성되므로 상태를 가지면 안 됨
- @ConfigurationProperties는 @RefreshScope 없이도 자동 갱신됨
- 모든 인스턴스에 갱신 요청을 보내야 함 (Spring Cloud Bus 사용 권장)

</details>

<details>
<summary><strong>Q7: Relaxed Binding이란 무엇인가요?</strong></summary>

**A**: **프로퍼티 이름을 유연하게 매칭**하는 기능입니다.

```java
@ConfigurationProperties(prefix = "my-app")
@Data
public class MyAppProperties {
    private String userName;  // camelCase
}

// 모두 userName에 바인딩됨 (Relaxed Binding)
my-app.userName=John       // ✅ camelCase
my-app.username=John       // ✅ lowercase
my-app.user-name=John      // ✅ kebab-case (권장)
my-app.user_name=John      // ✅ snake_case
MY_APP_USERNAME=John       // ✅ 환경 변수 (대문자 + 언더스코어)
```

**규칙**:
- **application.yml**: kebab-case 권장 (`user-name`)
- **환경 변수**: 대문자 + 언더스코어 (`USER_NAME`)
- **Java 필드**: camelCase (`userName`)

**@Value는 Relaxed Binding 미지원**:
```java
// ❌ @Value는 정확한 이름만 가능
@Value("${my-app.user-name}")  // user-name만 가능
private String userName;

// ✅ @ConfigurationProperties는 유연
@ConfigurationProperties(prefix = "my-app")
class Props {
    private String userName;  // user-name, username, user_name 모두 OK
}
```

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. @Value의 기본값은 어떻게 설정하나요?</strong></summary>

**모범 답안**:
> "@Value 어노테이션에서 콜론(:)을 사용하여 기본값을 설정할 수 있습니다. `@Value(\"${app.timeout:5000}\")`처럼 작성하면 app.timeout 프로퍼티가 없을 때 5000이 기본값으로 사용됩니다. null을 기본값으로 하려면 `@Value(\"${app.value:#{null}}\")`처럼 SpEL 표현식을 사용합니다."

</details>

<details>
<summary><strong>2. @ConfigurationProperties의 장점은 무엇인가요?</strong></summary>

**모범 답안**:
> "@ConfigurationProperties는 @Value에 비해 여러 장점이 있습니다. 첫째, 타입 안전성을 제공하여 컴파일 타임에 오류를 발견할 수 있습니다. 둘째, @Validated와 함께 사용하여 값 검증이 가능합니다. 셋째, 중첩된 구조를 쉽게 표현할 수 있습니다. 넷째, IDE의 자동완성을 지원하여 개발 편의성이 높습니다. 따라서 2개 이상의 관련된 설정은 @ConfigurationProperties로 관리하는 것이 권장됩니다."

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. 프로퍼티 소스의 우선순위를 설명하세요</strong></summary>

**모범 답안**:
> "Spring의 프로퍼티 소스는 우선순위가 있습니다. 가장 높은 것부터 1) Command Line Arguments, 2) SPRING_APPLICATION_JSON, 3) OS 환경 변수, 4) Java System Properties, 5) application-{profile}.yml, 6) application.yml, 7) @PropertySource로 추가한 파일, 8) 기본값 순입니다. 이를 통해 환경에 따라 설정을 유연하게 Override할 수 있으며, 운영 환경에서는 환경 변수나 Command Line으로 중요한 설정을 주입하여 보안을 강화할 수 있습니다."

</details>

<details>
<summary><strong>2. SpEL의 실무 활용 사례를 설명하세요</strong></summary>

**모범 답안**:
> "SpEL은 실무에서 다양하게 활용됩니다. 첫째, 조건부 Bean 등록에 사용되며 `@ConditionalOnExpression(\"#{environment['app.feature.enabled'] == 'true'}\")`처럼 동적으로 Bean 생성 여부를 결정할 수 있습니다. 둘째, @Cacheable의 key 생성에 사용되어 `@Cacheable(key = \"#user.id + '-' + #type\")`처럼 복잡한 캐시 키를 생성합니다. 셋째, @PreAuthorize에서 권한 검사에 사용되며 `@PreAuthorize(\"hasRole('ADMIN') or #userId == principal.id\")`처럼 세밀한 권한 제어가 가능합니다. 넷째, 프로퍼티 값 계산에 사용되어 동적으로 값을 조합하거나 변환할 수 있습니다."

</details>

---

## 📖 면접 질문 리스트 답안

> **사용 가이드**: 이 섹션은 위의 면접 질문에 대한 상세 답안입니다. 먼저 스스로 답변을 준비한 후, 이 답안을 참고하여 보완하세요.

---

### 📘 주니어/신입 개발자용 답변

<details>
<summary><strong>Q1: @Value의 기본값은 어떻게 설정하나요?</strong></summary>

**⏱️ 답변 시간**: 30초 - 1분

**✅ 모범 답안**:

> "@Value 어노테이션에서 **콜론(:)을 사용하여 기본값을 설정**할 수 있습니다. `@Value(\"${app.timeout:5000}\")`처럼 작성하면 app.timeout 프로퍼티가 없을 때 5000이 기본값으로 사용됩니다.
>
> 타입에 따라 기본값 형식이 다릅니다. 문자열은 그대로 작성하고, 숫자는 숫자로, boolean은 true/false로 작성합니다. null을 기본값으로 하려면 SpEL 표현식 `#{null}`을 사용해야 합니다.
>
> 기본값 설정은 매우 중요한데, 프로퍼티가 누락되었을 때 애플리케이션 시작 실패를 방지할 수 있기 때문입니다."

**📊 답변 구조 분석**:
- **방법** (15초): 콜론(:) 사용법
- **예시** (20초): 타입별 기본값
- **중요성** (10초): 시작 실패 방지

**💡 추가 질문 대비**:
- "기본값 없이 프로퍼티가 없으면 어떻게 되나요?"
  → "IllegalArgumentException이 발생하며 애플리케이션이 시작되지 않습니다. 따라서 Optional한 설정은 반드시 기본값을 설정해야 합니다."

</details>

<details>
<summary><strong>Q2: @ConfigurationProperties의 장점은 무엇인가요?</strong></summary>

**⏱️ 답변 시간**: 45초 - 1분

**✅ 모범 답안**:

> "@ConfigurationProperties는 @Value에 비해 여러 장점이 있습니다.
>
> 첫째, **타입 안전성**을 제공하여 컴파일 타임에 오류를 발견할 수 있습니다. 문자열 타이핑 실수가 없고, IDE의 자동완성도 지원됩니다.
>
> 둘째, **@Validated와 함께 사용하여 값 검증**이 가능합니다. @NotBlank, @Min, @Max 등으로 잘못된 설정을 애플리케이션 시작 시점에 검증할 수 있습니다.
>
> 셋째, **중첩된 구조를 쉽게 표현**할 수 있습니다. database.master.url처럼 복잡한 설정도 계층 구조로 깔끔하게 관리됩니다.
>
> 넷째, **Relaxed Binding**을 지원하여 user-name, userName, user_name 등 다양한 형식의 프로퍼티 이름을 모두 매칭할 수 있습니다.
>
> 따라서 2개 이상의 관련된 설정은 @ConfigurationProperties로 관리하는 것이 권장됩니다."

**📊 답변 구조 분석**:
- **개요** (5초): @Value 대비 장점 강조
- **장점 1** (10초): 타입 안전성
- **장점 2** (10초): 검증
- **장점 3** (5초): 중첩 구조
- **장점 4** (10초): Relaxed Binding
- **결론** (5초): 사용 권장 시나리오

</details>

---

### 📗 중급 개발자용 답변

<details>
<summary><strong>Q1: 프로퍼티 소스의 우선순위를 설명하세요</strong></summary>

**⏱️ 답변 시간**: 1분 - 1분 30초

**✅ 모범 답안**:

> "Spring의 프로퍼티 소스는 **명확한 우선순위**가 있어 환경에 따라 설정을 유연하게 Override할 수 있습니다.
>
> 가장 높은 우선순위는 **Command Line Arguments**입니다. `--server.port=8080`처럼 실행 시 지정하는 값이 모든 설정을 덮어씁니다.
>
> 그 다음은 **SPRING_APPLICATION_JSON** 환경 변수, **OS 환경 변수**, **Java System Properties** 순입니다. 이를 통해 코드나 설정 파일 변경 없이 환경별로 다른 값을 주입할 수 있습니다.
>
> 그 다음이 **application-{profile}.yml**이고, 마지막이 **application.yml**입니다. 프로파일별 설정이 공통 설정을 덮어쓰는 구조입니다.
>
> **@PropertySource로 추가한 파일**은 우선순위가 낮아서 다른 모든 소스에 의해 덮어써집니다.
>
> 실무에서는 이 우선순위를 활용하여, **공통 설정은 application.yml에**, **환경별 차이는 Profile로**, **민감 정보는 환경 변수로** 관리하여 보안을 강화합니다."

**📊 답변 구조 분석**:
- **개요** (10초): 우선순위 존재 및 목적
- **최우선** (15초): Command Line
- **중간** (20초): 환경 변수, System Properties
- **파일 기반** (20초): Profile vs 기본 설정
- **실무 활용** (15초): 보안 및 환경 관리

**💡 면접관이 주목하는 포인트**:
- ✅ 우선순위 정확한 순서 암기
- ✅ 실무에서 어떻게 활용하는지
- ✅ 보안 관점 (민감 정보는 환경 변수)

</details>

<details>
<summary><strong>Q2: SpEL의 실무 활용 사례를 설명하세요</strong></summary>

**⏱️ 답변 시간**: 1분 - 1분 30초

**✅ 모범 답안**:

> "SpEL은 실무에서 **동적이고 유연한 설정**이 필요한 다양한 상황에 활용됩니다.
>
> 첫째, **조건부 Bean 등록**입니다. `@ConditionalOnExpression(\"#{environment['app.feature.enabled'] == 'true'}\")`처럼 환경 변수나 프로퍼티 값에 따라 Bean 생성 여부를 동적으로 결정할 수 있습니다.
>
> 둘째, **@Cacheable의 동적 키 생성**입니다. `@Cacheable(key = \"#user.id + '-' + #type\")`처럼 메서드 파라미터를 조합하여 복잡한 캐시 키를 생성할 수 있습니다.
>
> 셋째, **@PreAuthorize에서 세밀한 권한 검사**입니다. `@PreAuthorize(\"hasRole('ADMIN') or #userId == principal.id\")`처럼 역할 기반 권한과 소유권 검사를 조합할 수 있습니다.
>
> 넷째, **프로퍼티 값의 동적 계산**입니다. `@Value(\"#{${base.price} * 1.1}\")`처럼 설정 값을 기반으로 계산된 값을 주입할 수 있습니다.
>
> 다섯째, **컬렉션 필터링과 투영**입니다. `@Value(\"#{products.?[price > 10000].![name]}\")`처럼 복잡한 컬렉션 연산을 선언적으로 표현할 수 있습니다.
>
> SpEL은 강력하지만 복잡해지면 가독성이 떨어지므로, **복잡한 로직은 별도 @Bean 메서드로 분리**하는 것이 좋습니다."

**📊 답변 구조 분석**:
- **개요** (5초): SpEL의 목적
- **사례 1** (15초): 조건부 Bean
- **사례 2** (15초): 캐시 키 생성
- **사례 3** (15초): 권한 검사
- **사례 4** (10초): 동적 계산
- **사례 5** (10초): 컬렉션 연산
- **주의사항** (10초): 가독성 유지

**🎯 추가 질문 대비**:
- "SpEL의 성능은 어떤가요?"
  → "SpEL은 파싱과 평가 비용이 있지만, 애플리케이션 시작 시 한 번만 실행되는 경우가 대부분이라 성능 영향은 미미합니다. 런타임에 반복 실행되는 경우라면 캐싱을 고려해야 합니다."

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

**주니어용 답변 패턴**: **방법 → 예시 → 이유**
1. 어떻게 하는지 설명 (15초)
2. 구체적인 예시 제시 (20초)
3. 왜 중요한지 설명 (10초)

**중급용 답변 패턴**: **개념 → 다양한 활용 → 주의사항**
1. 핵심 개념 정의 (10초)
2. 여러 실무 사례 (60-80초)
3. 주의사항이나 Best Practice (10-20초)

#### SpEL/Properties 관련 키워드

**반드시 언급할 용어**:
- ✅ @Value vs @ConfigurationProperties
- ✅ 콜론(:) 기본값 구문
- ✅ SpEL #{} vs Property ${}
- ✅ Profile 활용
- ✅ 환경 변수 우선순위
- ✅ Relaxed Binding
- ✅ @Validated 검증

---

## 📝 핵심 정리

### @Value vs @ConfigurationProperties

| 구분 | @Value | @ConfigurationProperties |
|-----|--------|-------------------------|
| **타입 안전** | ❌ | ✅ |
| **검증** | ❌ | ✅ (@Validated) |
| **중첩 구조** | 어려움 | ✅ 쉬움 |
| **자동완성** | ❌ | ✅ |
| **Relaxed Binding** | ❌ | ✅ |
| **사용 시나리오** | 단일 값, 간단한 설정 | 2개 이상 관련 설정 |

### 프로퍼티 소스 우선순위

| 우선순위 | 소스 | 예시 |
|---------|------|-----|
| 1 (최고) | Command Line | `--server.port=9090` |
| 2 | 환경 변수 | `SERVER_PORT=9090` |
| 3 | Java System | `System.setProperty()` |
| 4 | application-{profile} | `application-prod.yml` |
| 5 | application.yml | 기본 설정 |
| 6 (최저) | @PropertySource | 커스텀 프로퍼티 |

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] **@ConfigurationProperties 사용**: 타입 안전, 검증
- [ ] **민감 정보는 환경 변수**: 보안 강화
- [ ] **Profile별 설정 분리**: 환경별 관리
- [ ] **기본값 설정**: 설정 누락 방지

#### ❌ 하지 말아야 할 것
- [ ] **하드코딩**: 재컴파일 필요
- [ ] **비밀번호 평문 저장**: 보안 위험
- [ ] **@Value 남발**: 관리 어려움
- [ ] **복잡한 SpEL**: 가독성 저하

---

## 📚 추가 학습 자료

> **학습 로드맵**: 이 섹션의 자료들을 순서대로 학습하면 SpEL과 Properties 전문가가 될 수 있습니다.

---

### 📖 공식 문서

#### Spring 공식 문서
- **Spring Expression Language (SpEL)**: https://docs.spring.io/spring-framework/reference/core/expressions.html
  - 난이도: ⭐⭐⭐⭐☆
  - 추천: SpEL 문법의 모든 것
  - 핵심: 컬렉션 연산, Bean 참조, 타입 연산자

- **Spring Boot Externalized Configuration**: https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.external-config
  - 난이도: ⭐⭐⭐☆☆
  - 추천: 프로퍼티 소스 우선순위 공식 가이드
  - 핵심: @ConfigurationProperties, Profile, Validation

- **Spring Boot Configuration Metadata**: https://docs.spring.io/spring-boot/docs/current/reference/html/configuration-metadata.html
  - 난이도: ⭐⭐⭐☆☆
  - 추천: IDE 자동완성을 위한 메타데이터 작성법

---

### 🇰🇷 한국어 블로그 & 자료

#### 우아한형제들 기술 블로그
- **Spring Boot 설정 관리 전략**: https://techblog.woowahan.com/
  - "배달의민족 마이크로서비스 환경 설정 관리"
  - "Profile 전략과 Feature Toggle 실전 활용"

#### 카카오 기술 블로그
- **대규모 서비스 설정 관리**: https://tech.kakao.com/
  - "100개 마이크로서비스의 설정 중앙화"
  - "Spring Cloud Config Server 운영 노하우"

#### 네이버 D2
- **SpEL 활용 고급 패턴**: https://d2.naver.com/
  - "Spring Security의 SpEL 활용"
  - "@PreAuthorize 고급 사용법"

---

### 🌍 영어 자료

#### Baeldung
- **Spring @Value Tutorial**: https://www.baeldung.com/spring-value-annotation
  - 난이도: ⭐⭐⭐☆☆
  - 추천: @Value의 모든 사용법

- **Guide to @ConfigurationProperties**: https://www.baeldung.com/configuration-properties-in-spring-boot
  - 난이도: ⭐⭐⭐☆☆
  - 추천: 타입 안전한 설정 관리

- **Spring Expression Language Guide**: https://www.baeldung.com/spring-expression-language
  - 난이도: ⭐⭐⭐⭐☆
  - 추천: SpEL 고급 문법

#### Spring Blog
- **Configuration Best Practices**: https://spring.io/blog
  - "12-Factor App Configuration"
  - "Secrets Management in Spring Boot"

---

### 🎥 동영상 강의

#### 한국어 강의

**김영한님 - 스프링 부트 핵심 원리와 활용**
- 플랫폼: 인프런
- 난이도: ⭐⭐⭐☆☆
- 추천 섹션:
  - 외부 설정과 프로필
  - @ConfigurationProperties 활용
  - 환경별 설정 분리 전략

**백기선님 - 스프링 프레임워크 핵심 기술**
- 플랫폼: 인프런
- 난이도: ⭐⭐⭐☆☆
- 추천 섹션:
  - SpEL 완벽 가이드
  - Environment Abstraction

---

### 📚 추천 도서

#### 한국어 도서

**스프링 부트 핵심 가이드**
- 저자: 장정우
- 난이도: ⭐⭐⭐☆☆
- 추천 챕터: 7장 설정 관리
- 특징: 실무 중심 설명

**스프링 부트 실전 활용 마스터**
- 저자: 그렉 턴키스트
- 난이도: ⭐⭐⭐⭐☆
- 추천 챕터: Configuration 고급 패턴

#### 영어 도서

**Spring Boot in Action**
- 저자: Craig Walls
- 추천 챕터: Chapter 3 - Customizing Configuration

---

### 💻 GitHub 저장소 & 오픈소스

#### 학습용 예제

**Spring Boot Samples - Configuration**
- URL: https://github.com/spring-projects/spring-boot/tree/main/spring-boot-samples
- 특징: 공식 예제 코드

**Spring Cloud Config**
- URL: https://github.com/spring-cloud/spring-cloud-config
- 특징: 중앙 설정 서버 구현

---

### 🛠️ 실습 도구

#### Configuration Processor
```gradle
annotationProcessor 'org.springframework.boot:spring-boot-configuration-processor'
```
- IDE 자동완성 지원
- 메타데이터 자동 생성

#### Spring Boot Actuator
```yaml
management:
  endpoints:
    web:
      exposure:
        include: env,configprops
```
- `/actuator/env`: 모든 프로퍼티 확인
- `/actuator/configprops`: @ConfigurationProperties 확인

---

### 📝 학습 순서 가이드

#### 1단계: 기초 (1주)
1. Spring 공식 문서 @Value, @ConfigurationProperties
2. Baeldung 튜토리얼 따라하기
3. 간단한 설정 클래스 작성 실습

#### 2단계: 심화 (2주)
1. SpEL 문법 완전 정복
2. Profile 전략 수립
3. 환경 변수 우선순위 실습

#### 3단계: 실무 (2-3주)
1. 실전 프로젝트 완성 (다중 환경 설정)
2. Feature Toggle 구현
3. Config Server 연동 (Optional)

---

## 🚀 다음 단계

### 📘 다음 학습: 10장 - Spring Transaction

**SpEL과 Properties를 마스터한 여러분, 다음은?**

설정 관리를 완벽하게 배웠습니다. 이제 **Transaction**으로 데이터 일관성을 보장하는 방법을 배워보세요!

```java
// SpEL + Properties: 환경별 설정 관리
@ConfigurationProperties(prefix = "database")
public class DatabaseProperties {
    private String url;
    private int poolSize;
}

// Transaction: 데이터 일관성 보장
@Transactional(isolation = Isolation.READ_COMMITTED, propagation = Propagation.REQUIRED)
public Order createOrder(OrderDto dto) {
    // 주문 생성 + 재고 차감 + 포인트 적립
    // → 하나라도 실패하면 모두 롤백!
}

// Properties + Transaction 조합
@Value("${transaction.timeout:30}")
private int txTimeout;

@Transactional(timeout = txTimeout)  // 설정 값으로 timeout 지정
public void processLongRunningTask() {
    // ...
}
```

---

### 🎯 10장 Transaction에서 배울 내용

#### 1. @Transactional 완벽 이해
```java
// 전파 속성 (Propagation)
@Transactional(propagation = Propagation.REQUIRED)  // 기본값
public void outerMethod() {
    innerMethod();  // 같은 트랜잭션에서 실행
}

@Transactional(propagation = Propagation.REQUIRES_NEW)
public void innerMethod() {
    // 새로운 트랜잭션 시작 (독립적)
}

// 격리 수준 (Isolation)
@Transactional(isolation = Isolation.READ_COMMITTED)
public Order getOrder(Long id) {
    // Dirty Read 방지
}

// 롤백 조건
@Transactional(rollbackFor = Exception.class)
public void method() {
    // Checked Exception도 롤백
}
```

#### 2. 트랜잭션 전파 (Propagation)
- REQUIRED: 기존 트랜잭션 사용, 없으면 생성
- REQUIRES_NEW: 항상 새 트랜잭션 생성
- NESTED: 중첩 트랜잭션 (SavePoint 활용)
- MANDATORY: 트랜잭션 필수 (없으면 에러)
- SUPPORTS: 트랜잭션 있으면 참여, 없어도 OK
- NOT_SUPPORTED: 트랜잭션 없이 실행
- NEVER: 트랜잭션 있으면 에러

#### 3. 실무 트랜잭션 패턴
```java
// 패턴 1: 읽기 전용 최적화
@Transactional(readOnly = true)
public List<Product> getProducts() {
    // 쓰기 잠금 방지, 성능 최적화
}

// 패턴 2: 타임아웃 설정
@Transactional(timeout = 10)
public void importData() {
    // 10초 내 완료 안 되면 롤백
}

// 패턴 3: 선택적 롤백
@Transactional(noRollbackFor = NotFoundException.class)
public void processOrder(Long id) {
    // NotFoundException은 롤백하지 않음
}
```

---

### 📚 학습 로드맵

```
[07장] 어노테이션 상세
    ↓
  @Component, @Autowired
    ↓
[08장] AOP 개념과 활용
    ↓
  횡단 관심사 모듈화
    ↓
[09장] SpEL과 프로퍼티 ✅ 현재 위치
    ↓
  동적 설정, 환경 관리
    ↓
[10장] Spring Transaction ⬅️ 다음 학습
    ↓
  @Transactional, ACID
    ↓
[고급] JPA + QueryDSL
```

---

### ✅ 10장 학습 전 체크리스트

**필수 선행 지식**:
- [x] @Value와 @ConfigurationProperties 차이
- [x] Profile별 설정 분리
- [x] SpEL 기본 문법
- [x] AOP 개념 (8장)

**준비 사항**:
- [ ] Spring Data JPA 의존성 추가
- [ ] 데이터베이스 설정 (H2 또는 MySQL)
- [ ] 10장 Part 1 문서 확인

**예상 학습 시간**: 4-5시간
**난이도**: ⭐⭐⭐⭐☆

---

### 💪 학습 동기 부여

**여러분은 이미 설정 관리 전문가입니다!**

- ✅ **@ConfigurationProperties로 타입 안전한 설정** 관리
- ✅ **Profile로 환경별 분리** 완벽 구현
- ✅ **SpEL로 동적 값 계산** 및 조건부 설정
- ✅ **Feature Toggle로 코드 변경 없이 기능 제어**

**이제 Transaction으로 한 단계 더!**

Transaction을 배우면:
- 🔒 **데이터 일관성 보장**: 주문 생성 + 재고 차감이 원자적으로 처리
- 🛡️ **동시성 제어**: 여러 사용자가 동시에 접근해도 안전
- 🔄 **롤백 자동화**: 에러 발생 시 자동으로 이전 상태로 복원
- 📊 **성능 최적화**: readOnly로 불필요한 쓰기 잠금 방지

**Spring 마스터까지 한 걸음 남았습니다!** 💪

---

## 🎉 축하합니다!

**이제 여러분은**:
- ✅ SpEL을 활용하여 동적 값 계산을 할 수 있습니다
- ✅ @Value와 @ConfigurationProperties를 적재적소에 사용할 수 있습니다
- ✅ 환경별 프로퍼티를 안전하게 관리할 수 있습니다
- ✅ 프로퍼티 소스 우선순위를 이해하고 활용할 수 있습니다
- ✅ Feature Toggle로 기능을 동적으로 제어할 수 있습니다

---

**[← 이전: Part 1](09-1-SpEL프로퍼티-Part1.md)** | **[목차로 돌아가기](../README.md)**
