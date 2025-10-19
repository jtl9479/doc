# 09장: SpEL과 프로퍼티 - Part 1

**[다음: Part 2 →](09-2-SpEL프로퍼티-Part2.md)** | **[목차로 돌아가기](../README.md)**

---

## 📚 학습 목표

이 장을 마치면 다음을 할 수 있습니다:

- [ ] SpEL(Spring Expression Language)이 무엇인지 이해하고 사용할 수 있다
- [ ] @Value로 프로퍼티 값을 주입하고 기본값을 설정할 수 있다
- [ ] @ConfigurationProperties로 타입 안전한 설정을 관리할 수 있다
- [ ] Environment를 사용하여 프로그래밍 방식으로 프로퍼티를 읽을 수 있다
- [ ] 다양한 프로퍼티 소스(application.yml, 환경 변수 등)를 활용할 수 있다

**난이도**: ⭐⭐⭐☆☆ (중급)
**예상 소요 시간**: 2.5시간
**선행 학습**: 03장(IoC), 07장(어노테이션)

---

## 🤔 왜 SpEL과 프로퍼티가 필요한가?

### 문제 상황

**설정 값을 코드에 하드코딩**:

```java
// ❌ 하드코딩: 환경마다 재컴파일 필요
@Service
public class EmailService {

    private String host = "smtp.gmail.com";  // 하드코딩
    private int port = 587;
    private String username = "admin@example.com";
    private String password = "password123";  // 보안 위험!

    public void sendEmail(String to, String subject, String body) {
        // 이메일 전송
    }
}

// 개발/운영 환경마다 다른 값? → 매번 재컴파일! 😱
```

**측정 가능한 문제점**:
- ❌ **재컴파일**: 환경 전환 시 재빌드 필요 → 배포 시간 2배
- ❌ **보안 위험**: 비밀번호가 코드에 노출
- ❌ **유지보수**: 설정 변경 시 코드 수정 → 위험
- ❌ **유연성**: 환경별 다른 값 관리 어려움

### 해결책: @Value와 프로퍼티 파일

```java
// ✅ @Value 사용: 외부 설정 파일로 관리
@Service
public class EmailService {

    @Value("${email.host}")
    private String host;

    @Value("${email.port}")
    private int port;

    @Value("${email.username}")
    private String username;

    @Value("${email.password}")
    private String password;

    public void sendEmail(String to, String subject, String body) {
        // 이메일 전송
    }
}

// application-dev.yml
email:
  host: smtp.gmail.com
  port: 587
  username: dev@example.com
  password: dev_password

// application-prod.yml
email:
  host: smtp.production.com
  port: 465
  username: admin@production.com
  password: ${EMAIL_PASSWORD}  // 환경 변수에서 로드
```

**개선 효과**:
- ✅ **재컴파일 불필요**: 설정만 변경 → 배포 시간 50% 단축
- ✅ **보안 강화**: 비밀번호를 환경 변수로 관리
- ✅ **유지보수 간편**: 코드 수정 없이 설정만 변경
- ✅ **환경별 관리**: Profile별로 다른 설정 파일 사용

---

## 🌟 실생활 비유 5가지

### 비유 1: 리모컨의 채널 설정 📺

**하드코딩 (코드에 박혀있음)**:
- 리모컨에 채널이 고정되어 있음
- 채널 변경하려면 리모컨을 뜯어야 함

**프로퍼티 파일 (외부 설정)**:
- 리모컨 설정 메뉴에서 채널 변경
- 리모컨 자체는 그대로, 설정만 변경

```java
// 하드코딩
int channel = 7;  // 채널 변경하려면 코드 수정

// 프로퍼티
@Value("${tv.default-channel}")
int channel;  // 설정 파일만 변경
```

### 비유 2: 스마트폰 설정 📱

**하드코딩**:
- 화면 밝기, 알림음이 앱에 고정
- 변경하려면 앱 재설치

**프로퍼티**:
- 설정 메뉴에서 자유롭게 변경
- 앱은 설정값을 읽어서 사용

```yaml
# 설정 파일 (application.yml)
app:
  brightness: 80
  volume: 50
  notifications: true
```

### 비유 3: 카페 메뉴판 가격 ☕

**하드코딩**:
- 메뉴판에 가격이 인쇄되어 있음
- 가격 변경하려면 메뉴판 재인쇄

**프로퍼티**:
- 디지털 메뉴판
- 가격표(설정 파일)만 업데이트

```java
// 하드코딩
int coffeePrice = 4500;  // 변경하려면 코드 수정

// 프로퍼티
@Value("${menu.coffee.price}")
int coffeePrice;  // 설정만 변경
```

### 비유 4: 배달의민족 배달비 설정 🛵

**하드코딩**:
- 각 음식점이 앱 코드에 배달비 하드코딩
- 변경하려면 앱 업데이트

**프로퍼티**:
- 음식점이 관리자 페이지에서 배달비 설정
- 실시간 반영

```yaml
# 음식점별 설정
restaurant:
  delivery-fee: 3000
  min-order: 15000
  free-delivery-threshold: 30000
```

### 비유 5: 회사 출퇴근 시간 설정 🏢

**하드코딩**:
- 출근 시간이 취업 규칙에 명시
- 변경하려면 규정 개정 (어려움)

**프로퍼티**:
- 유연근무제: 개인이 출근 시간 설정
- 상황에 맞게 변경 가능

```yaml
# 유연근무 설정
work:
  start-time: "09:00"
  end-time: "18:00"
  flexible: true
```

---

## 💡 핵심 개념

### 개념 1: SpEL (Spring Expression Language)이란?

#### 초등학생도 이해하는 설명
> "SpEL은 '계산기 언어'예요. `#{1 + 2}`라고 쓰면 3이 되고, `#{user.name}`이라고 쓰면 user의 이름을 가져와요."

#### 중급 개발자를 위한 설명
> "SpEL은 Spring에서 제공하는 강력한 표현식 언어로, `#{}` 안에 표현식을 작성하여 Bean 참조, 메서드 호출, 연산, 조건 판단 등을 할 수 있습니다. 런타임에 평가되며 @Value, @ConditionalOnExpression 등에서 사용됩니다."

#### 고급 개발자를 위한 설명
> "SpEL은 Expression 인터페이스를 기반으로 한 AST(Abstract Syntax Tree) 파서입니다. ExpressionParser가 문자열 표현식을 파싱하여 Expression 객체를 생성하고, EvaluationContext에서 변수와 함수를 resolve하여 getValue()로 최종값을 반환합니다. Reflection과 PropertyAccessor를 통해 객체 그래프를 탐색합니다."

#### SpEL 기본 문법

```java
// 1. 리터럴 값
@Value("#{100}")
private int number;  // 100

@Value("#{'Hello'}")
private String text;  // "Hello"

@Value("#{true}")
private boolean flag;  // true

// 2. 산술 연산
@Value("#{10 + 20}")
private int sum;  // 30

@Value("#{10 * 5}")
private int product;  // 50

@Value("#{10 / 3}")
private int division;  // 3

@Value("#{10 % 3}")
private int remainder;  // 1

// 3. 비교 연산
@Value("#{10 > 5}")
private boolean greater;  // true

@Value("#{10 == 10}")
private boolean equal;  // true

// 4. 논리 연산
@Value("#{true and false}")
private boolean and;  // false

@Value("#{true or false}")
private boolean or;  // true

@Value("#{!true}")
private boolean not;  // false

// 5. 조건 연산 (삼항 연산자)
@Value("#{10 > 5 ? 'Yes' : 'No'}")
private String result;  // "Yes"

// 6. 엘비스 연산자 (?:)
@Value("#{null ?: 'default'}")
private String elvis;  // "default"

// 7. 안전 탐색 연산자 (?.)
@Value("#{user?.name}")  // user가 null이면 null 반환 (NPE 방지)
private String userName;
```

---

### 개념 2: @Value로 프로퍼티 주입

#### 기본 사용법

```yaml
# application.yml
app:
  name: My Application
  version: 1.0.0
  admin:
    email: admin@example.com
    phone: 010-1234-5678
```

```java
@Service
public class AppService {

    // 1. 단순 값 주입
    @Value("${app.name}")
    private String appName;

    @Value("${app.version}")
    private String version;

    // 2. 중첩된 프로퍼티
    @Value("${app.admin.email}")
    private String adminEmail;

    // 3. 기본값 설정
    @Value("${app.timeout:5000}")  // timeout이 없으면 5000
    private int timeout;

    @Value("${app.max-retry:3}")
    private int maxRetry;

    // 4. 타입 변환
    @Value("${app.enabled:true}")
    private boolean enabled;

    @Value("${app.port:8080}")
    private int port;

    // 5. 리스트 주입
    @Value("${app.allowed-origins}")
    private List<String> allowedOrigins;

    // 6. SpEL과 프로퍼티 혼합
    @Value("#{${app.port} + 1000}")
    private int backupPort;  // port + 1000

    // 7. 환경 변수 사용
    @Value("${DB_PASSWORD}")
    private String dbPassword;  // 환경 변수에서 로드
}
```

#### 리스트와 맵 주입

```yaml
# application.yml
app:
  allowed-origins:
    - http://localhost:3000
    - http://localhost:8080
    - https://example.com

  database:
    master: jdbc:mysql://master:3306/db
    slave: jdbc:mysql://slave:3306/db

  properties:
    connection.timeout: 30000
    connection.max-pool-size: 20
```

```java
@Component
public class DatabaseConfig {

    // 리스트 주입
    @Value("${app.allowed-origins}")
    private List<String> allowedOrigins;

    // 또는 SpEL로
    @Value("#{${app.allowed-origins}}")
    private List<String> origins;

    // 맵 주입 (SpEL 필요)
    @Value("#{${app.database}}")
    private Map<String, String> databases;

    @PostConstruct
    public void print() {
        System.out.println("Allowed Origins: " + allowedOrigins);
        System.out.println("Databases: " + databases);
    }
}
```

---

### 개념 3: @ConfigurationProperties (권장)

#### @Value의 단점과 @ConfigurationProperties의 장점

```java
// ❌ @Value의 단점: 많아지면 관리 어려움
@Service
public class EmailService {

    @Value("${email.host}")
    private String host;

    @Value("${email.port}")
    private int port;

    @Value("${email.username}")
    private String username;

    @Value("${email.password}")
    private String password;

    @Value("${email.from}")
    private String from;

    @Value("${email.enable-ssl:true}")
    private boolean enableSsl;

    @Value("${email.timeout:5000}")
    private int timeout;

    // 10개, 20개... 계속 늘어남
}

// ✅ @ConfigurationProperties: 타입 안전, 자동완성, 검증
@Component
@ConfigurationProperties(prefix = "email")
@Validated
public class EmailProperties {

    @NotBlank
    private String host;

    @Min(1)
    @Max(65535)
    private int port;

    @Email
    private String username;

    private String password;

    @Email
    private String from;

    private boolean enableSsl = true;

    @Min(1000)
    private int timeout = 5000;

    // Getters and Setters (Lombok @Data 사용 가능)
}
```

#### 중첩된 Properties

```yaml
# application.yml
app:
  database:
    url: jdbc:mysql://localhost:3306/mydb
    username: root
    password: password
    pool:
      max-size: 20
      min-idle: 5
      timeout: 30000

  cache:
    type: redis
    redis:
      host: localhost
      port: 6379
      timeout: 3000

  security:
    jwt:
      secret: mySecretKey
      expiration: 86400
    cors:
      allowed-origins:
        - http://localhost:3000
        - https://example.com
```

```java
@Component
@ConfigurationProperties(prefix = "app")
@Data
public class AppProperties {

    private Database database;
    private Cache cache;
    private Security security;

    @Data
    public static class Database {
        private String url;
        private String username;
        private String password;
        private Pool pool;

        @Data
        public static class Pool {
            private int maxSize;
            private int minIdle;
            private int timeout;
        }
    }

    @Data
    public static class Cache {
        private String type;
        private Redis redis;

        @Data
        public static class Redis {
            private String host;
            private int port;
            private int timeout;
        }
    }

    @Data
    public static class Security {
        private Jwt jwt;
        private Cors cors;

        @Data
        public static class Jwt {
            private String secret;
            private long expiration;
        }

        @Data
        public static class Cors {
            private List<String> allowedOrigins;
        }
    }
}

// 사용
@Service
@RequiredArgsConstructor
public class AppService {

    private final AppProperties appProperties;

    public void printConfig() {
        System.out.println("DB URL: " + appProperties.getDatabase().getUrl());
        System.out.println("Max Pool Size: " + appProperties.getDatabase().getPool().getMaxSize());
        System.out.println("Cache Type: " + appProperties.getCache().getType());
        System.out.println("JWT Secret: " + appProperties.getSecurity().getJwt().getSecret());
    }
}
```

---

### 개념 4: Environment를 통한 프로그래밍 방식 접근

```java
@Service
public class ConfigService {

    @Autowired
    private Environment env;

    public void printConfig() {
        // 1. 단일 프로퍼티 읽기
        String appName = env.getProperty("app.name");
        System.out.println("App Name: " + appName);

        // 2. 기본값 지정
        String timeout = env.getProperty("app.timeout", "5000");
        System.out.println("Timeout: " + timeout);

        // 3. 타입 변환
        Integer port = env.getProperty("app.port", Integer.class, 8080);
        System.out.println("Port: " + port);

        Boolean enabled = env.getProperty("app.enabled", Boolean.class, true);
        System.out.println("Enabled: " + enabled);

        // 4. 필수 프로퍼티 (없으면 예외)
        String dbPassword = env.getRequiredProperty("DB_PASSWORD");

        // 5. 프로퍼티 존재 여부 확인
        if (env.containsProperty("app.feature.new-ui")) {
            System.out.println("New UI feature is configured");
        }

        // 6. 활성 프로파일 확인
        String[] activeProfiles = env.getActiveProfiles();
        System.out.println("Active Profiles: " + Arrays.toString(activeProfiles));

        // 7. 프로파일 매칭
        if (env.acceptsProfiles(Profiles.of("dev | staging"))) {
            System.out.println("개발/스테이징 환경입니다");
        }
    }
}
```

---

### 개념 5: 프로퍼티 소스 우선순위

```
1. Command Line Arguments (최고 우선순위)
   java -jar app.jar --server.port=9090

2. SPRING_APPLICATION_JSON
   SPRING_APPLICATION_JSON='{"server.port":9090}' java -jar app.jar

3. OS 환경 변수
   export SERVER_PORT=9090

4. Java System Properties
   System.setProperty("server.port", "9090")

5. application-{profile}.yml/properties
   application-prod.yml

6. application.yml/properties (기본)

7. @PropertySource로 추가한 파일

8. 기본값 (SpringApplication.setDefaultProperties)
```

#### 실제 예제

```yaml
# application.yml (기본)
server:
  port: 8080

# application-dev.yml
server:
  port: 8081  # dev 프로파일에서는 8081

# application-prod.yml
server:
  port: ${SERVER_PORT:8082}  # 환경 변수 또는 8082
```

```bash
# 1. 기본 (application.yml)
java -jar app.jar
# → port = 8080

# 2. Profile로 Override
java -jar app.jar --spring.profiles.active=dev
# → port = 8081

# 3. 환경 변수로 Override
export SERVER_PORT=9000
java -jar app.jar --spring.profiles.active=prod
# → port = 9000

# 4. Command Line으로 Override (최우선)
java -jar app.jar --spring.profiles.active=prod --server.port=9090
# → port = 9090
```

---

### 개념 6: SpEL 고급 기능

#### Bean 참조

```java
@Component("userValidator")
public class UserValidator {
    public boolean isValid(String username) {
        return username != null && username.length() >= 3;
    }
}

@Service
public class UserService {

    // Bean 참조
    @Value("#{userValidator}")
    private UserValidator validator;

    // Bean의 프로퍼티 참조
    @Value("#{systemProperties['user.home']}")
    private String userHome;

    // Bean의 메서드 호출
    @Value("#{userValidator.isValid('admin')}")
    private boolean isAdminValid;
}
```

#### 컬렉션 연산

```java
@Component
@ConfigurationProperties(prefix = "products")
public class ProductConfig {
    private List<String> names = Arrays.asList("Apple", "Banana", "Cherry");
    private Map<String, Integer> prices = Map.of("Apple", 1000, "Banana", 500);

    // Getters and Setters
}

@Service
public class ProductService {

    // 리스트 필터링
    @Value("#{productConfig.names.?[length() > 5]}")
    private List<String> longNames;  // ["Banana", "Cherry"]

    // 리스트 변환
    @Value("#{productConfig.names.![toUpperCase()]}")
    private List<String> upperNames;  // ["APPLE", "BANANA", "CHERRY"]

    // 첫 번째 요소
    @Value("#{productConfig.names[0]}")
    private String firstName;  // "Apple"

    // 맵에서 값 가져오기
    @Value("#{productConfig.prices['Apple']}")
    private int applePrice;  // 1000
}
```

#### 정규표현식

```java
@Service
public class ValidationService {

    // 이메일 검증
    @Value("#{T(java.util.regex.Pattern).matches('^[A-Za-z0-9+_.-]+@(.+)$', 'test@example.com')}")
    private boolean isValidEmail;  // true

    // 전화번호 검증
    @Value("#{T(java.util.regex.Pattern).matches('^\\d{3}-\\d{4}-\\d{4}$', '010-1234-5678')}")
    private boolean isValidPhone;  // true
}
```

---

**[다음: Part 2 →](09-2-SpEL프로퍼티-Part2.md)** | **[목차로 돌아가기](../README.md)**
