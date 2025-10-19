# 03장: IoC 컨테이너 - Part 3 (기본 실습)

**[← 이전: Part 2](03-2-IoC-컨테이너-Part2.md)** | **[다음: Part 4 →](03-4-IoC-컨테이너-Part4.md)**

---

## 💻 기본 실습

### 📋 사전 체크리스트

```bash
# 1. Java 버전 확인 (11 이상)
java -version

# 2. Maven/Gradle 확인
mvn -v
# 또는
gradle -v

# 3. IDE 준비 (IntelliJ IDEA 또는 VS Code)
# IntelliJ IDEA Community Edition 설치 권장

# 4. Spring Boot CLI (선택사항)
spring --version
```

---

### 실습 1: 기본 IoC 컨테이너 생성 및 Bean 등록

**난이도**: ⭐☆☆☆☆

#### 프로젝트 생성

```bash
# Spring Initializr로 프로젝트 생성
# https://start.spring.io/
# - Project: Maven
# - Language: Java
# - Spring Boot: 3.2.x
# - Dependencies: Spring Web

# 또는 CLI로 생성
spring init --dependencies=web ioc-demo
cd ioc-demo
```

#### 코드 작성

**파일: src/main/java/com/example/demo/MessageService.java**
```java
package com.example.demo;

import org.springframework.stereotype.Component;

// @Component: 이 클래스를 Spring Bean으로 등록
@Component
public class MessageService {

    // 메시지를 반환하는 간단한 메서드
    public String getMessage() {
        return "Hello, IoC Container!";
    }

    // 생성자에서 로그 출력 (Bean 생성 확인용)
    public MessageService() {
        System.out.println("✅ MessageService Bean이 생성되었습니다!");
    }
}
```

**파일: src/main/java/com/example/demo/MessagePrinter.java**
```java
package com.example.demo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Component
public class MessagePrinter {

    // MessageService를 자동 주입받음
    @Autowired
    private MessageService messageService;

    // 주입받은 서비스를 사용
    public void printMessage() {
        String message = messageService.getMessage();
        System.out.println("📢 " + message);
    }

    public MessagePrinter() {
        System.out.println("✅ MessagePrinter Bean이 생성되었습니다!");
    }
}
```

**파일: src/main/java/com/example/demo/DemoApplication.java**
```java
package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ApplicationContext;

@SpringBootApplication  // @ComponentScan 포함
public class DemoApplication {

    public static void main(String[] args) {
        // Spring IoC 컨테이너 시작
        ApplicationContext context = SpringApplication.run(DemoApplication.class, args);

        // 컨테이너에서 Bean 가져오기
        MessagePrinter printer = context.getBean(MessagePrinter.class);

        // Bean 사용
        printer.printMessage();
    }
}
```

#### 실행

```bash
# Maven
./mvnw spring-boot:run

# Gradle
./gradlew bootRun
```

#### 예상 출력

```
✅ MessageService Bean이 생성되었습니다!
✅ MessagePrinter Bean이 생성되었습니다!

  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v3.2.0)

📢 Hello, IoC Container!
```

#### 코드 설명

- **라인 1-3 (MessageService.java)**: `@Component`로 Spring이 자동으로 Bean 등록
- **라인 10 (MessagePrinter.java)**: `@Autowired`로 MessageService를 자동 주입
- **라인 14 (DemoApplication.java)**: `SpringApplication.run()`이 IoC 컨테이너 생성
- **라인 17**: `getBean()`으로 컨테이너에서 Bean을 가져옴

---

### 실습 2: Java Configuration으로 Bean 등록

**난이도**: ⭐⭐⭐☆☆

#### 코드

**파일: src/main/java/com/example/demo/database/Database.java**
```java
package com.example.demo.database;

// 외부 라이브러리라고 가정 (@Component 사용 불가)
public class Database {
    private String url;
    private String username;

    public Database(String url, String username) {
        this.url = url;
        this.username = username;
        System.out.println("✅ Database 연결: " + url);
    }

    public void query(String sql) {
        System.out.println("🔍 SQL 실행: " + sql);
    }
}
```

**파일: src/main/java/com/example/demo/config/AppConfig.java**
```java
package com.example.demo.config;

import com.example.demo.database.Database;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

// @Configuration: 설정 클래스임을 선언
@Configuration
public class AppConfig {

    // @Bean: 메서드의 반환 객체를 Bean으로 등록
    @Bean
    public Database database() {
        // 외부 라이브러리 객체를 직접 생성하여 Bean으로 등록
        return new Database(
            "jdbc:mysql://localhost:3306/mydb",
            "root"
        );
    }

    // 다른 Bean을 의존하는 Bean
    @Bean
    public DatabaseService databaseService(Database database) {
        // 매개변수로 다른 Bean을 자동 주입받음
        return new DatabaseService(database);
    }
}
```

**파일: src/main/java/com/example/demo/config/DatabaseService.java**
```java
package com.example.demo.config;

import com.example.demo.database.Database;

public class DatabaseService {
    private final Database database;

    // 생성자 주입
    public DatabaseService(Database database) {
        this.database = database;
        System.out.println("✅ DatabaseService 생성됨");
    }

    public void executeQuery(String sql) {
        database.query(sql);
    }
}
```

**파일: src/main/java/com/example/demo/DemoApplication.java** (수정)
```java
package com.example.demo;

import com.example.demo.config.DatabaseService;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ApplicationContext;

@SpringBootApplication
public class DemoApplication {

    public static void main(String[] args) {
        ApplicationContext context = SpringApplication.run(DemoApplication.class, args);

        // Java Config로 등록한 Bean 사용
        DatabaseService dbService = context.getBean(DatabaseService.class);
        dbService.executeQuery("SELECT * FROM users");
    }
}
```

#### 실행

```bash
./mvnw spring-boot:run
```

#### 예상 출력

```
✅ Database 연결: jdbc:mysql://localhost:3306/mydb
✅ DatabaseService 생성됨
🔍 SQL 실행: SELECT * FROM users
```

#### 코드 설명

- **AppConfig**: `@Configuration` 클래스에서 `@Bean` 메서드로 Bean 등록
- **Database**: 외부 라이브러리처럼 `@Component`를 사용할 수 없는 경우
- **databaseService()**: 메서드 파라미터로 다른 Bean을 자동 주입받음

---

### 실습 3: Bean 생명주기 콜백 활용

**난이도**: ⭐⭐⭐⭐☆

#### 코드

**파일: src/main/java/com/example/demo/lifecycle/CacheManager.java**
```java
package com.example.demo.lifecycle;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

@Component
public class CacheManager {

    private Map<String, Object> cache;

    // 생성자: Bean 생성 시점
    public CacheManager() {
        System.out.println("1️⃣ CacheManager 생성자 호출");
        // 이 시점에는 아직 의존성 주입이 안 됨
    }

    // @PostConstruct: 의존성 주입 완료 후 실행
    @PostConstruct
    public void init() {
        System.out.println("2️⃣ @PostConstruct 실행 - 캐시 초기화");
        this.cache = new HashMap<>();
        // 초기 데이터 로드
        cache.put("config", loadConfiguration());
        System.out.println("✅ 캐시 준비 완료!");
    }

    private String loadConfiguration() {
        // 실제로는 파일이나 DB에서 로드
        return "application.properties";
    }

    public Object get(String key) {
        return cache.get(key);
    }

    public void put(String key, Object value) {
        cache.put(key, value);
        System.out.println("📦 캐시 저장: " + key);
    }

    // @PreDestroy: 컨테이너 종료 전 실행
    @PreDestroy
    public void cleanup() {
        System.out.println("3️⃣ @PreDestroy 실행 - 캐시 정리");
        if (cache != null) {
            cache.clear();
            System.out.println("🧹 캐시 정리 완료");
        }
    }
}
```

**파일: src/main/java/com/example/demo/DemoApplication.java** (수정)
```java
package com.example.demo;

import com.example.demo.lifecycle.CacheManager;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ConfigurableApplicationContext;

@SpringBootApplication
public class DemoApplication {

    public static void main(String[] args) {
        // ConfigurableApplicationContext로 받아야 close() 가능
        ConfigurableApplicationContext context =
            SpringApplication.run(DemoApplication.class, args);

        // CacheManager 사용
        CacheManager cacheManager = context.getBean(CacheManager.class);
        cacheManager.put("user1", "John Doe");
        System.out.println("📖 캐시 조회: " + cacheManager.get("user1"));

        // 컨테이너 종료 (PreDestroy 호출됨)
        System.out.println("\n🛑 애플리케이션 종료 시작...");
        context.close();
    }
}
```

#### 실행

```bash
./mvnw spring-boot:run
```

#### 예상 출력

```
1️⃣ CacheManager 생성자 호출
2️⃣ @PostConstruct 실행 - 캐시 초기화
✅ 캐시 준비 완료!

📦 캐시 저장: user1
📖 캐시 조회: John Doe

🛑 애플리케이션 종료 시작...
3️⃣ @PreDestroy 실행 - 캐시 정리
🧹 캐시 정리 완료
```

#### 코드 설명

- **생성자**: 객체 생성 시점 (의존성 주입 전)
- **@PostConstruct**: 의존성 주입 완료 후, 초기화 작업 수행
- **@PreDestroy**: 컨테이너 종료 전, 정리 작업 수행
- **context.close()**: 명시적 종료로 PreDestroy 콜백 실행

---

### 좋은 예 vs 나쁜 예

#### ❌ 나쁜 예: 직접 객체 생성 (IoC 없이)

```java
// AntiPattern.java
public class OrderService {

    // 나쁜 예 1: new로 직접 생성
    private ProductService productService = new ProductService();
    private PaymentService paymentService = new PaymentService();

    public void createOrder(Order order) {
        // 문제: ProductService의 생성자가 변경되면?
        // → OrderService도 수정해야 함 (강한 결합)

        productService.checkStock(order.getProductId());
        paymentService.processPayment(order.getAmount());
    }
}

// 나쁜 예 2: 싱글톤 직접 구현
public class DatabaseConnection {
    private static DatabaseConnection instance;

    private DatabaseConnection() {
        // 문제: 테스트 시 Mock으로 교체 불가능
        // 문제: Thread-safe 하지 않음
    }

    public static DatabaseConnection getInstance() {
        if (instance == null) {
            instance = new DatabaseConnection();  // Race Condition!
        }
        return instance;
    }
}
```

**문제점**:
- 문제 1: **강한 결합** - 코드 변경 시 연쇄적 수정 필요
- 문제 2: **테스트 어려움** - Mock 객체로 교체 불가능
- 문제 3: **Thread 안전성** - 동시성 문제 발생 가능
- 문제 4: **유연성 부족** - 구현체 교체 어려움

#### ✅ 좋은 예: IoC 컨테이너 활용

```java
// GoodPattern.java
@Service
public class OrderService {

    // 좋은 예 1: 생성자 주입 (권장)
    private final ProductService productService;
    private final PaymentService paymentService;

    @Autowired  // Spring 4.3+에서는 생략 가능
    public OrderService(ProductService productService,
                        PaymentService paymentService) {
        this.productService = productService;
        this.paymentService = paymentService;
    }

    public void createOrder(Order order) {
        // Spring이 자동으로 주입한 Bean 사용
        productService.checkStock(order.getProductId());
        paymentService.processPayment(order.getAmount());
    }
}

// 인터페이스 기반 설계 (더 좋은 예)
@Service
public class BetterOrderService {

    private final ProductService productService;
    private final PaymentService paymentService;

    // 인터페이스로 의존
    public BetterOrderService(ProductService productService,
                              PaymentService paymentService) {
        this.productService = productService;
        this.paymentService = paymentService;
    }

    // 구현은 동일, 하지만 테스트 시 Mock 주입 가능!
}

// 테스트 코드
@SpringBootTest
class BetterOrderServiceTest {

    @MockBean  // Mock 객체로 쉽게 교체!
    private ProductService productService;

    @MockBean
    private PaymentService paymentService;

    @Autowired
    private BetterOrderService orderService;

    @Test
    void testCreateOrder() {
        // Given
        when(productService.checkStock(anyLong())).thenReturn(true);
        when(paymentService.processPayment(anyDouble())).thenReturn("SUCCESS");

        // When
        orderService.createOrder(new Order());

        // Then
        verify(productService).checkStock(anyLong());
    }
}
```

**장점**:
- 장점 1: **느슨한 결합** - 인터페이스 기반으로 유연성 확보
- 장점 2: **테스트 용이** - Mock 객체로 쉽게 교체 가능
- 장점 3: **Thread 안전** - Spring이 싱글톤 보장
- 장점 4: **유지보수성** - 구현체 변경 시 설정만 수정

#### 비교 표

| 항목 | 나쁜 예 (new) | 좋은 예 (IoC) |
|------|--------------|--------------|
| 객체 생성 | `new ProductService()` | `@Autowired ProductService` |
| 결합도 | 강한 결합 | 느슨한 결합 |
| 테스트 | 어려움 (실제 객체만) | 쉬움 (Mock 가능) |
| 생명주기 | 수동 관리 | 자동 관리 |
| Thread 안전성 | 직접 구현 필요 | Spring이 보장 |
| 유지보수 | 어려움 | 쉬움 |

---

**[← 이전: Part 2](03-2-IoC-컨테이너-Part2.md)** | **[다음: Part 4 →](03-4-IoC-컨테이너-Part4.md)**
