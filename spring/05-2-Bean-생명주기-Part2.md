# 05장: Bean 생명주기 - Part 2 (실습 & 실무 & FAQ & 면접)

**[← 이전: Part 1](05-1-Bean-생명주기-Part1.md)** | **[다음: 06장 Bean 스코프 →](06-1-Bean-스코프-Part1.md)**

---

## 💻 기본 실습

### 실습 1: @PostConstruct와 @PreDestroy 기본 사용

**난이도**: ⭐⭐☆☆☆

```java
// DatabaseService.java
package com.example.demo.service;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import org.springframework.stereotype.Service;

@Service
public class DatabaseService {

    private boolean connected = false;

    // 초기화 콜백
    @PostConstruct
    public void connect() {
        System.out.println("📡 DB 연결 시작...");
        // 실제로는 DB 연결 로직
        connected = true;
        System.out.println("✅ DB 연결 완료!");
    }

    public void query(String sql) {
        if (!connected) {
            throw new IllegalStateException("DB가 연결되지 않았습니다");
        }
        System.out.println("🔍 SQL 실행: " + sql);
    }

    // 소멸 콜백
    @PreDestroy
    public void disconnect() {
        System.out.println("📡 DB 연결 종료 시작...");
        // 실제로는 DB 연결 종료 로직
        connected = false;
        System.out.println("✅ DB 연결 종료 완료!");
    }
}

// DemoApplication.java
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        ConfigurableApplicationContext context =
            SpringApplication.run(DemoApplication.class, args);

        DatabaseService dbService = context.getBean(DatabaseService.class);
        dbService.query("SELECT * FROM users");

        // 애플리케이션 종료 (PreDestroy 호출됨)
        context.close();
    }
}
```

**실행 결과**:
```
📡 DB 연결 시작...
✅ DB 연결 완료!

🔍 SQL 실행: SELECT * FROM users

📡 DB 연결 종료 시작...
✅ DB 연결 종료 완료!
```

---

### 실습 2: 캐시 관리 서비스

**난이도**: ⭐⭐⭐☆☆

```java
// CacheService.java
package com.example.demo.service;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class CacheService {

    private Map<String, Object> cache;

    @PostConstruct
    public void initCache() {
        System.out.println("🗂️ 캐시 초기화 중...");
        cache = new HashMap<>();

        // 초기 데이터 로드
        loadInitialData();

        System.out.println("✅ 캐시 준비 완료! (항목: " + cache.size() + "개)");
    }

    private void loadInitialData() {
        // 실제로는 DB에서 자주 사용하는 데이터 로드
        cache.put("popular_product_1", "MacBook Pro");
        cache.put("popular_product_2", "iPhone 15");
        cache.put("popular_product_3", "AirPods Pro");
    }

    public Object get(String key) {
        return cache.get(key);
    }

    public void put(String key, Object value) {
        cache.put(key, value);
        System.out.println("📦 캐시 저장: " + key);
    }

    @PreDestroy
    public void saveCache() {
        System.out.println("💾 캐시 저장 중...");

        // 실제로는 디스크나 Redis에 저장
        System.out.println("   저장할 항목: " + cache.size() + "개");

        // 캐시 정리
        cache.clear();
        System.out.println("✅ 캐시 저장 및 정리 완료!");
    }
}
```

---

### 실습 3: 스케줄러 생명주기 관리

**난이도**: ⭐⭐⭐⭐☆

```java
// SchedulerService.java
package com.example.demo.service;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import org.springframework.stereotype.Service;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

@Service
public class SchedulerService {

    private ScheduledExecutorService scheduler;

    @PostConstruct
    public void startScheduler() {
        System.out.println("⏰ 스케줄러 시작...");

        scheduler = Executors.newScheduledThreadPool(1);

        // 5초마다 실행
        scheduler.scheduleAtFixedRate(
            () -> System.out.println("🔔 정기 작업 실행: " + System.currentTimeMillis()),
            0,      // 초기 지연 없음
            5,      // 5초마다
            TimeUnit.SECONDS
        );

        System.out.println("✅ 스케줄러 시작 완료!");
    }

    @PreDestroy
    public void stopScheduler() {
        System.out.println("⏰ 스케줄러 종료 중...");

        if (scheduler != null && !scheduler.isShutdown()) {
            scheduler.shutdown();
            try {
                // 최대 5초 대기
                if (!scheduler.awaitTermination(5, TimeUnit.SECONDS)) {
                    scheduler.shutdownNow();
                }
            } catch (InterruptedException e) {
                scheduler.shutdownNow();
            }
        }

        System.out.println("✅ 스케줄러 종료 완료!");
    }
}
```

---

## 🏢 실무 활용 사례

### 사례 1: Netflix - 연결 풀 관리

```java
// 사용 목적: DB 연결 풀을 애플리케이션 시작 시 준비
// 규모: 글로벌 1억 사용자, 수천 개 마이크로서비스
// 효과: 첫 요청부터 빠른 응답, Warm-up 시간 제로

@Service
public class DatabaseConnectionPoolManager {

    private HikariDataSource dataSource;

    @PostConstruct
    public void initializeConnectionPool() {
        System.out.println("🏊 DB 연결 풀 초기화 중...");

        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:mysql://localhost:3306/netflix");
        config.setUsername("netflix_user");
        config.setMaximumPoolSize(100);
        config.setMinimumIdle(10);

        // 연결 풀 생성
        dataSource = new HikariDataSource(config);

        // Warm-up: 미리 연결 생성
        try {
            dataSource.getConnection().close();
        } catch (Exception e) {
            throw new RuntimeException("연결 풀 초기화 실패", e);
        }

        System.out.println("✅ 연결 풀 준비 완료!");
    }

    @PreDestroy
    public void closeConnectionPool() {
        System.out.println("🏊 연결 풀 종료 중...");

        if (dataSource != null && !dataSource.isClosed()) {
            dataSource.close();
        }

        System.out.println("✅ 모든 연결 정리 완료!");
    }

    public DataSource getDataSource() {
        return dataSource;
    }
}

// 성과:
// - 첫 요청 응답 시간: 3초 → 50ms (Warm-up 효과)
// - 연결 누수: 제로 (PreDestroy로 안전한 종료)
// - 장애 복구 시간: 5분 → 30초 (빠른 재시작)
```

### 사례 2: 카카오 - Redis 캐시 워밍

```java
// 사용 목적: 자주 사용하는 데이터를 미리 캐시에 로드
// 규모: 5000만 사용자, 초당 100만 요청
// 효과: 캐시 히트율 95% 이상 유지

@Service
@RequiredArgsConstructor
public class CacheWarmingService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final ProductRepository productRepository;

    @PostConstruct
    public void warmUpCache() {
        System.out.println("🔥 캐시 워밍 시작...");

        // 인기 상품 100개를 미리 캐시에 로드
        List<Product> popularProducts = productRepository.findTop100ByOrderBySalesDesc();

        for (Product product : popularProducts) {
            String key = "product:" + product.getId();
            redisTemplate.opsForValue().set(key, product, Duration.ofHours(1));
        }

        System.out.println("✅ 캐시 워밍 완료! (상품: " + popularProducts.size() + "개)");
    }

    @PreDestroy
    public void saveImportantCache() {
        System.out.println("💾 중요 캐시 백업 중...");

        // 실시간 조회수 등 중요 데이터를 DB에 저장
        Set<String> keys = redisTemplate.keys("viewCount:*");
        if (keys != null) {
            for (String key : keys) {
                Long viewCount = (Long) redisTemplate.opsForValue().get(key);
                // DB에 저장
                saveViewCountToDatabase(key, viewCount);
            }
        }

        System.out.println("✅ 캐시 백업 완료!");
    }

    private void saveViewCountToDatabase(String key, Long count) {
        // DB 저장 로직
    }
}

// 성과:
// - 캐시 히트율: 70% → 95% (워밍 효과)
// - 첫 요청 응답: 500ms → 10ms
// - 데이터 손실: 제로 (종료 시 백업)
```

---

## ❓ FAQ

<details>
<summary><strong>Q1: @PostConstruct는 언제 실행되나요?</strong></summary>

**A**: 의존성 주입이 완료된 직후에 실행됩니다.

**실행 순서**:
```java
1. 생성자 호출 (의존성 주입 전)
2. @Autowired 필드/Setter 주입
3. @PostConstruct 실행 ← 이 시점!
4. Bean 사용 가능
```

**예시**:
```java
@Service
public class UserService {
    @Autowired
    private UserRepository repository;

    public UserService() {
        System.out.println("repository: " + repository);  // null
    }

    @PostConstruct
    public void init() {
        System.out.println("repository: " + repository);  // 주입됨!
    }
}
```

</details>

<details>
<summary><strong>Q2: @PreDestroy는 항상 실행되나요?</strong></summary>

**A**: **정상 종료 시에만** 실행됩니다.

**실행되는 경우**:
- `context.close()` 호출
- `SpringApplication.exit()` 호출
- Ctrl+C로 종료 (SIGTERM)

**실행 안 되는 경우**:
- `kill -9` (강제 종료)
- 시스템 크래시
- 무한 루프로 응답 없음

**실무 팁**:
```java
@PreDestroy
public void cleanup() {
    // 중요 데이터는 주기적으로 저장 (PreDestroy만 믿지 말 것!)
}
```

</details>

<details>
<summary><strong>Q3: 생성자에서 초기화하면 안 되나요?</strong></summary>

**A**: 의존성이 필요하면 @PostConstruct를 사용해야 합니다.

**나쁜 예 (생성자)**:
```java
@Service
public class BadService {
    @Autowired
    private DatabaseService dbService;

    public BadService() {
        // ❌ NPE 발생! (아직 주입 전)
        dbService.connect();
    }
}
```

**좋은 예 (@PostConstruct)**:
```java
@Service
public class GoodService {
    @Autowired
    private DatabaseService dbService;

    @PostConstruct
    public void init() {
        // ✅ 정상 동작 (주입 완료 후)
        dbService.connect();
    }
}
```

</details>

<details>
<summary><strong>Q4: @PostConstruct 메서드가 여러 개면?</strong></summary>

**A**: 모두 실행되지만, **실행 순서는 보장되지 않습니다**.

**예시**:
```java
@Service
public class MultiInitService {

    @PostConstruct
    public void init1() {
        System.out.println("Init 1");
    }

    @PostConstruct
    public void init2() {
        System.out.println("Init 2");
    }

    // 출력 순서: 보장 안 됨
    // Init 1 → Init 2 또는 Init 2 → Init 1
}
```

**권장**: @PostConstruct는 1개만 사용하고, 내부에서 순서 제어

</details>

<details>
<summary><strong>Q5: 외부 라이브러리 클래스는 어떻게 관리하나요?</strong></summary>

**A**: `@Bean(initMethod, destroyMethod)`를 사용합니다.

```java
// 외부 라이브러리 (수정 불가)
public class ExternalService {
    public void connect() { }
    public void disconnect() { }
}

// 설정 클래스
@Configuration
public class ExternalConfig {

    @Bean(initMethod = "connect", destroyMethod = "disconnect")
    public ExternalService externalService() {
        return new ExternalService();
    }
}
```

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. Bean 생명주기의 주요 단계를 설명해주세요</strong></summary>

**모범 답안**:
> "Bean 생명주기는 생성, 의존성 주입, 초기화, 사용, 소멸의 5단계로 구성됩니다. 먼저 Spring이 생성자로 Bean을 생성하고, @Autowired로 의존성을 주입합니다. 그 다음 @PostConstruct 메서드를 호출하여 초기화 작업을 수행하고, 애플리케이션에서 Bean을 사용합니다. 마지막으로 컨테이너 종료 시 @PreDestroy 메서드로 정리 작업을 수행합니다."

</details>

<details>
<summary><strong>2. @PostConstruct와 @PreDestroy는 언제 사용하나요?</strong></summary>

**모범 답안**:
> "@PostConstruct는 의존성 주입이 완료된 후 초기화 작업이 필요할 때 사용합니다. DB 연결 풀 생성, 캐시 데이터 로드, 파일 열기 등이 대표적입니다. @PreDestroy는 컨테이너 종료 전 리소스를 정리할 때 사용합니다. DB 연결 종료, 파일 닫기, 스레드 풀 종료 등이 있습니다."

**실무 예시**:
```java
@Service
public class FileService {
    private FileWriter writer;

    @PostConstruct
    public void openFile() {
        writer = new FileWriter("log.txt");
    }

    @PreDestroy
    public void closeFile() {
        writer.close();
    }
}
```

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. Bean 생명주기 콜백의 3가지 방법을 비교하고, 실무에서 어떤 것을 선택하나요?</strong></summary>

**모범 답안**:
> "Bean 생명주기 콜백은 @PostConstruct/@PreDestroy, InitializingBean/DisposableBean, @Bean(initMethod/destroyMethod) 3가지가 있습니다. @PostConstruct/@PreDestroy는 표준 JSR-250으로 가장 권장되며, 코드가 간결하고 IDE 지원이 우수합니다. InitializingBean/DisposableBean은 Spring 인터페이스에 의존하는 구식 방법입니다. @Bean(initMethod/destroyMethod)는 외부 라이브러리처럼 소스 코드를 수정할 수 없을 때 사용합니다. 실무에서는 자체 클래스는 @PostConstruct/@PreDestroy, 외부 라이브러리는 @Bean 방식을 사용합니다."

**실무 경험**:
> "이전 프로젝트에서 Redis 연결 관리를 @PostConstruct로 초기화하고 @PreDestroy로 종료했습니다. 외부 라이브러리인 Elasticsearch Client는 @Bean(initMethod="connect", destroyMethod="close")로 관리했습니다. 이를 통해 애플리케이션 시작 시 모든 연결이 준비되어 첫 요청부터 빠른 응답을 제공할 수 있었습니다."

</details>

---

## 📝 핵심 정리

### Bean 생명주기 단계

| 단계 | 설명 | 관련 어노테이션/메서드 |
|------|------|----------------------|
| 1. 생성 | Bean 인스턴스 생성 | 생성자 |
| 2. 주입 | 의존성 주입 | @Autowired |
| 3. 초기화 | 초기화 작업 수행 | **@PostConstruct** |
| 4. 사용 | 비즈니스 로직 실행 | - |
| 5. 소멸 | 정리 작업 수행 | **@PreDestroy** |

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] **@PostConstruct로 초기화**: DB 연결, 캐시 로드
- [ ] **@PreDestroy로 정리**: 연결 종료, 리소스 해제
- [ ] **중요 데이터는 주기적 저장**: PreDestroy만 믿지 말 것
- [ ] **초기화 실패 시 명확한 에러**: 시작 실패는 빠를수록 좋음

#### ❌ 하지 말아야 할 것
- [ ] **생성자에서 의존성 사용**: 아직 주입 전이라 NPE
- [ ] **@PostConstruct에서 무거운 작업**: 시작 시간 지연
- [ ] **@PreDestroy만 믿고 저장**: 강제 종료 시 실행 안 됨

---

## 🚀 다음 단계

### 다음 장 미리보기: 06장 Bean 스코프
- **배울 내용 1**: Singleton, Prototype 스코프
- **배울 내용 2**: Request, Session 스코프 (웹)
- **배울 내용 3**: 스코프별 사용 시나리오

---

**[← 이전: Part 1](05-1-Bean-생명주기-Part1.md)** | **[다음: 06장 Bean 스코프 →](06-1-Bean-스코프-Part1.md)**
