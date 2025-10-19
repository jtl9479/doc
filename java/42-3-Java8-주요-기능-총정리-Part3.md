# 42장 Java 8+ 주요 기능 총정리 - Part 3: 성능 최적화 & 면접 질문

## 📚 목차
1. [성능 최적화](#성능-최적화)
2. [베스트 프랙티스](#베스트-프랙티스)
3. [면접 질문](#면접-질문)

---

## ⚡ 성능 최적화

### 1. 스트림 vs 반복문 성능

```java
import java.util.*;
import java.util.stream.*;

public class PerformanceTest {
    public static void main(String[] args) {
        List<Integer> numbers = IntStream.range(0, 1_000_000)
            .boxed()
            .collect(Collectors.toList());

        // 1. 전통적 for문
        long start = System.currentTimeMillis();
        int sum = 0;
        for (int n : numbers) {
            sum += n;
        }
        System.out.println("For loop: " + (System.currentTimeMillis() - start) + "ms");

        // 2. 스트림
        start = System.currentTimeMillis();
        sum = numbers.stream()
            .mapToInt(n -> n)
            .sum();
        System.out.println("Stream: " + (System.currentTimeMillis() - start) + "ms");

        // 3. 병렬 스트림
        start = System.currentTimeMillis();
        sum = numbers.parallelStream()
            .mapToInt(n -> n)
            .sum();
        System.out.println("Parallel Stream: " + (System.currentTimeMillis() - start) + "ms");
    }
}

/* 결과 (100만 건)
For loop: 2ms
Stream: 5ms
Parallel Stream: 8ms (오버헤드)

결과 (1000만 건)
For loop: 20ms
Stream: 25ms
Parallel Stream: 10ms (효과적!)
*/
```

**가이드라인**:
- **소량 데이터 (< 10만)**: 전통적 for문
- **중간 데이터**: 스트림 (가독성)
- **대량 데이터 (> 100만)**: 병렬 스트림

---

### 2. Optional 성능 고려사항

```java
public class OptionalPerformance {
    // ❌ 느린 코드 - orElse는 항상 실행됨
    public String getUserName(Long id) {
        return findUser(id)
            .map(User::getName)
            .orElse(getDefaultName());  // 항상 실행!
    }

    // ✅ 빠른 코드 - orElseGet은 필요할 때만 실행
    public String getUserName(Long id) {
        return findUser(id)
            .map(User::getName)
            .orElseGet(this::getDefaultName);  // 필요할 때만 실행
    }

    private String getDefaultName() {
        // 무거운 연산이라고 가정
        return "Unknown";
    }
}
```

**성능 차이**:
```java
// 벤치마크
Optional<String> value = Optional.of("Alice");

// orElse - 22ns
value.orElse(expensiveOperation());

// orElseGet - 3ns (값이 있을 때)
value.orElseGet(() -> expensiveOperation());
```

---

### 3. 스트림 최적화 기법

```java
public class StreamOptimization {
    // ❌ 비효율적 - 중간 스트림 생성
    public List<String> inefficient(List<User> users) {
        return users.stream()
            .map(User::getName)
            .filter(name -> name != null)
            .filter(name -> name.length() > 3)
            .map(String::toUpperCase)
            .collect(Collectors.toList());
    }

    // ✅ 효율적 - 필터링 먼저
    public List<String> efficient(List<User> users) {
        return users.stream()
            .filter(user -> user.getName() != null)
            .filter(user -> user.getName().length() > 3)
            .map(User::getName)
            .map(String::toUpperCase)
            .collect(Collectors.toList());
    }

    // 🔥 더 효율적 - 메서드 레퍼런스
    public List<String> moreEfficient(List<User> users) {
        return users.stream()
            .map(User::getName)
            .filter(Objects::nonNull)
            .filter(name -> name.length() > 3)
            .map(String::toUpperCase)
            .collect(Collectors.toList());
    }
}
```

**최적화 원칙**:
1. **필터링을 먼저** (데이터 크기 줄이기)
2. **map 연산 최소화**
3. **메서드 레퍼런스 사용** (람다보다 빠름)

---

### 4. 컬렉션 팩토리 메서드 성능

```java
public class CollectionPerformance {
    // ❌ 느린 코드
    public List<String> slowWay() {
        List<String> list = new ArrayList<>();
        list.add("A");
        list.add("B");
        list.add("C");
        return Collections.unmodifiableList(list);
    }

    // ✅ 빠른 코드 (Java 9+)
    public List<String> fastWay() {
        return List.of("A", "B", "C");  // 불변, 더 작은 메모리
    }

    // 성능 비교
    public void benchmark() {
        // ArrayList: 176 bytes
        List<String> arrayList = new ArrayList<>(Arrays.asList("A", "B", "C"));

        // List.of: 88 bytes (50% 감소!)
        List<String> compactList = List.of("A", "B", "C");
    }
}
```

---

### 5. CompletableFuture 최적화

```java
public class AsyncOptimization {
    private ExecutorService executor = Executors.newFixedThreadPool(10);

    // ❌ 비효율적 - 순차 실행
    public CompletableFuture<Result> inefficient() {
        return CompletableFuture.supplyAsync(this::step1)
            .thenApply(r -> step2(r))
            .thenApply(r -> step3(r));
    }

    // ✅ 효율적 - 병렬 실행
    public CompletableFuture<Result> efficient() {
        CompletableFuture<String> cf1 = CompletableFuture.supplyAsync(
            this::step1, executor);
        CompletableFuture<String> cf2 = CompletableFuture.supplyAsync(
            this::step2, executor);
        CompletableFuture<String> cf3 = CompletableFuture.supplyAsync(
            this::step3, executor);

        return CompletableFuture.allOf(cf1, cf2, cf3)
            .thenApply(v -> combineResults(
                cf1.join(), cf2.join(), cf3.join()));
    }
}
```

---

## 🎯 베스트 프랙티스

### 1. 람다 표현식

```java
// ✅ DO
list.forEach(System.out::println);                    // 메서드 레퍼런스
list.stream().filter(s -> s.startsWith("A"));         // 간단한 람다

// ❌ DON'T
list.forEach(s -> {                                    // 복잡한 람다
    String upper = s.toUpperCase();
    String trimmed = upper.trim();
    if (trimmed.length() > 0) {
        System.out.println(trimmed);
    }
});
// → 별도 메서드로 분리

// ✅ 개선
list.forEach(this::processAndPrint);

private void processAndPrint(String s) {
    String processed = s.toUpperCase().trim();
    if (!processed.isEmpty()) {
        System.out.println(processed);
    }
}
```

---

### 2. 스트림 API

```java
// ✅ DO
List<String> result = users.stream()
    .filter(User::isActive)                            // 명확한 조건
    .map(User::getName)
    .collect(Collectors.toList());

// ❌ DON'T
users.stream()
    .forEach(user -> result.add(user.getName()));      // 외부 상태 수정

// ✅ DO - 적절한 컬렉터 사용
Map<String, List<User>> byCity = users.stream()
    .collect(Collectors.groupingBy(User::getCity));

// ❌ DON'T - 과도한 스트림 체이닝
users.stream()
    .map(User::getOrders)
    .flatMap(List::stream)
    .map(Order::getItems)
    .flatMap(List::stream)
    .map(Item::getPrice)
    .reduce(BigDecimal.ZERO, BigDecimal::add);
// → 가독성 떨어짐, 별도 메서드로 분리
```

---

### 3. Optional

```java
// ✅ DO
public Optional<User> findUser(Long id) {
    return Optional.ofNullable(repository.findById(id));
}

// ❌ DON'T
public Optional<User> findUser(Long id) {
    return Optional.of(repository.findById(id));       // null이면 NPE!
}

// ✅ DO - 함수형 스타일
String name = findUser(1L)
    .map(User::getName)
    .orElse("Unknown");

// ❌ DON'T - 절차적 스타일
Optional<User> userOpt = findUser(1L);
if (userOpt.isPresent()) {
    String name = userOpt.get().getName();
}

// ❌ DON'T - Optional을 필드로 사용
public class User {
    private Optional<String> middleName;  // 안 좋음!
}

// ✅ DO - nullable 필드
public class User {
    private String middleName;  // null 허용
}
```

---

### 4. 날짜/시간 API

```java
// ✅ DO
LocalDate today = LocalDate.now();
LocalDateTime now = LocalDateTime.now();
ZonedDateTime tokyo = ZonedDateTime.now(ZoneId.of("Asia/Tokyo"));

// ❌ DON'T
Date date = new Date();                                // 구 API 사용
Calendar cal = Calendar.getInstance();

// ✅ DO - 불변성 활용
LocalDate tomorrow = today.plusDays(1);                // today는 변하지 않음

// ❌ DON'T - 가변 객체
Calendar cal = Calendar.getInstance();
cal.add(Calendar.DAY_OF_MONTH, 1);                     // cal이 변경됨

// ✅ DO - 명확한 타입
public void scheduleEvent(LocalDateTime eventTime) {}  // 시간 포함

// ❌ DON'T - 모호한 타입
public void scheduleEvent(LocalDate eventDate) {}      // 몇 시?
```

---

## 💡 면접 질문

### Q1. Java 8의 주요 변화는 무엇인가요?

**답변**:
```
Java 8은 함수형 프로그래밍 패러다임을 도입한 획기적인 버전입니다.

주요 변화:
1. 람다 표현식 - 익명 함수를 간결하게 표현
2. 스트림 API - 선언적 데이터 처리
3. Optional - null 안전성 향상
4. 새로운 날짜/시간 API - Thread-safe하고 불변
5. 디폴트 메서드 - 인터페이스에 구현 추가 가능
6. 메서드 레퍼런스 - 람다 표현식 간소화

이를 통해 코드가 더 간결하고, 읽기 쉽고, 유지보수하기 좋아졌습니다.
```

---

### Q2. 스트림과 반복문의 차이는?

**답변**:
```java
// 반복문 (명령형)
List<String> result = new ArrayList<>();
for (User user : users) {
    if (user.getAge() >= 18) {
        result.add(user.getName());
    }
}

// 스트림 (선언형)
List<String> result = users.stream()
    .filter(user -> user.getAge() >= 18)
    .map(User::getName)
    .collect(Collectors.toList());
```

**차이점**:
1. **가독성**: 스트림이 더 선언적이고 의도가 명확
2. **병렬화**: 스트림은 parallelStream()으로 쉽게 병렬 처리
3. **성능**: 소량은 반복문이 빠르고, 대량은 병렬 스트림이 유리
4. **지연 실행**: 스트림은 필요할 때만 연산 수행

---

### Q3. Optional은 왜 사용하나요?

**답변**:
```java
// ❌ 전통적 방식
public String getUserEmail(Long id) {
    User user = findUser(id);
    if (user == null) return null;

    Email email = user.getEmail();
    if (email == null) return null;

    return email.getAddress();
}

// ✅ Optional 방식
public Optional<String> getUserEmail(Long id) {
    return findUser(id)
        .map(User::getEmail)
        .map(Email::getAddress);
}
```

**장점**:
1. **명시적**: 값이 없을 수 있음을 타입으로 표현
2. **안전성**: NPE 방지
3. **함수형**: 체이닝으로 처리
4. **의도 전달**: API 설계 의도가 명확

---

### Q4. 병렬 스트림을 사용할 때 주의사항은?

**답변**:
```java
// ❌ 잘못된 사용
List<Integer> result = new ArrayList<>();
numbers.parallelStream()
    .forEach(n -> result.add(n * 2));  // Thread-safe 하지 않음!

// ✅ 올바른 사용
List<Integer> result = numbers.parallelStream()
    .map(n -> n * 2)
    .collect(Collectors.toList());
```

**주의사항**:
1. **공유 상태 수정 금지** - Thread-safe 하지 않음
2. **대량 데이터에만 사용** - 소량은 오히려 느림
3. **순서가 중요하면 사용 금지** - 순서 보장 안 됨
4. **블로킹 I/O 피하기** - ForkJoinPool 고갈

---

### Q5. Java 8과 Java 11의 차이점은?

**답변**:
```java
// Java 11 추가 기능

// 1. var 키워드 (Java 10)
var name = "Alice";
var numbers = List.of(1, 2, 3);

// 2. String 메서드 개선
"  ".isBlank();           // true
"Hello".repeat(3);        // "HelloHelloHello"
"A\nB\nC".lines().count(); // 3

// 3. 컬렉션 팩토리 메서드 (Java 9)
List.of(1, 2, 3);
Set.of("A", "B");
Map.of("A", 1, "B", 2);

// 4. HTTP Client (표준 API)
HttpClient client = HttpClient.newHttpClient();
```

---

### Q6. Record가 일반 클래스와 다른 점은?

**답변**:
```java
// 일반 클래스 (보일러플레이트 코드)
public class Person {
    private final String name;
    private final int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public String getName() { return name; }
    public int getAge() { return age; }

    @Override
    public boolean equals(Object o) { /* ... */ }
    @Override
    public int hashCode() { /* ... */ }
    @Override
    public String toString() { /* ... */ }
}

// Record (Java 16+)
public record Person(String name, int age) {}
```

**차이점**:
1. **불변**: 모든 필드가 final
2. **간결성**: 보일러플레이트 자동 생성
3. **데이터 중심**: 순수 데이터 전달용
4. **상속 불가**: final 클래스

---

### Q7. Virtual Threads의 장점은?

**답변**:
```java
// 기존 Platform Thread
try (var executor = Executors.newFixedThreadPool(1000)) {
    for (int i = 0; i < 10_000; i++) {
        executor.submit(() -> {
            // 작업
        });
    }
}
// → OS 스레드 1000개 생성 (무거움)

// Virtual Thread (Java 21+)
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 10_000; i++) {
        executor.submit(() -> {
            // 작업
        });
    }
}
// → 경량 스레드 10,000개 생성 (가벼움)
```

**장점**:
1. **경량**: 메모리 사용량 1/100
2. **확장성**: 수백만 개 생성 가능
3. **간단성**: 동기 코드처럼 작성
4. **성능**: I/O 대기 시간 최소화

---

## 🎓 최종 정리

### Java 버전별 핵심 키워드

```
Java 8  (2014) → 람다, 스트림, Optional
Java 9  (2017) → 모듈, 컬렉션 팩토리
Java 10 (2018) → var
Java 11 (2018) → LTS, String 메서드
Java 14 (2020) → Switch 표현식
Java 15 (2020) → Text Blocks
Java 16 (2021) → Record
Java 17 (2021) → LTS, Sealed Classes
Java 21 (2023) → LTS, Virtual Threads
```

### 실무 추천 버전

```
🔥 신규 프로젝트: Java 17 or 21
✅ 안정적 운영: Java 11 or 17
⚠️  레거시: Java 8 → 11로 마이그레이션 권장
```

### 학습 순서

```
1. Java 8 (람다, 스트림, Optional) ← 필수!
2. Java 11 (var, String 메서드)
3. Java 17 (Record, Sealed Classes)
4. Java 21 (Virtual Threads)
```

---

**축하합니다! Java 8+ 주요 기능을 마스터했습니다!** 🎉
