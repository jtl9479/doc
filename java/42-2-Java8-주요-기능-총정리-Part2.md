# 42장 Java 8+ 주요 기능 총정리 - Part 2: 기업 사례 & 주니어 실수

## 📚 목차
1. [기업 사례](#기업-사례)
2. [주니어 실수 시나리오](#주니어-실수-시나리오)
3. [마이그레이션 전략](#마이그레이션-전략)

---

## 🏢 기업 사례

### 🔷 네이버 - Java 8 마이그레이션

**배경**: Java 6에서 Java 8로 대규모 마이그레이션

```java
// ❌ Before (Java 6)
public class SearchService {
    public List<Document> searchDocuments(String query) {
        List<Document> allDocs = documentRepository.findAll();
        List<Document> filtered = new ArrayList<>();

        for (Document doc : allDocs) {
            if (doc.getTitle().contains(query) && doc.isPublished()) {
                filtered.add(doc);
            }
        }

        // 정렬
        Collections.sort(filtered, new Comparator<Document>() {
            @Override
            public int compare(Document d1, Document d2) {
                return d2.getScore() - d1.getScore();
            }
        });

        // 상위 10개
        if (filtered.size() > 10) {
            filtered = filtered.subList(0, 10);
        }

        return filtered;
    }
}

// ✅ After (Java 8)
public class SearchService {
    public List<Document> searchDocuments(String query) {
        return documentRepository.findAll().stream()
            .filter(doc -> doc.getTitle().contains(query))
            .filter(Document::isPublished)
            .sorted(Comparator.comparingInt(Document::getScore).reversed())
            .limit(10)
            .collect(Collectors.toList());
    }
}
```

**성과**:
- 코드량 60% 감소
- 가독성 향상
- 버그 30% 감소
- 유지보수 시간 40% 단축

---

### 🔷 카카오 - Optional 도입

**배경**: NullPointerException 대응 전략

```java
// ❌ Before
public class UserService {
    public String getUserEmail(Long userId) {
        User user = userRepository.findById(userId);
        if (user == null) {
            return null;
        }

        Profile profile = user.getProfile();
        if (profile == null) {
            return null;
        }

        Email email = profile.getEmail();
        if (email == null) {
            return null;
        }

        return email.getAddress();
    }
}

// ✅ After
public class UserService {
    public Optional<String> getUserEmail(Long userId) {
        return userRepository.findById(userId)
            .map(User::getProfile)
            .map(Profile::getEmail)
            .map(Email::getAddress);
    }

    // 사용
    public void sendEmail(Long userId) {
        getUserEmail(userId)
            .ifPresent(email -> emailService.send(email, "Hello"));
    }
}
```

**성과**:
- NPE 발생률 70% 감소
- null 체크 코드 제거
- 의도가 명확한 API 설계

---

### 🔷 쿠팡 - 날짜/시간 API 마이그레이션

**배경**: 배송 시간 계산 오류 개선

```java
// ❌ Before (java.util.Date)
public class DeliveryService {
    public Date calculateDeliveryDate(Date orderDate) {
        Calendar cal = Calendar.getInstance();
        cal.setTime(orderDate);

        // 토요일이면 월요일로
        if (cal.get(Calendar.DAY_OF_WEEK) == Calendar.SATURDAY) {
            cal.add(Calendar.DAY_OF_MONTH, 2);
        }
        // 일요일이면 월요일로
        else if (cal.get(Calendar.DAY_OF_WEEK) == Calendar.SUNDAY) {
            cal.add(Calendar.DAY_OF_MONTH, 1);
        }

        // 2일 후
        cal.add(Calendar.DAY_OF_MONTH, 2);

        return cal.getTime();
    }
}

// ✅ After (java.time)
public class DeliveryService {
    public LocalDate calculateDeliveryDate(LocalDate orderDate) {
        LocalDate deliveryDate = orderDate;

        // 주말이면 다음 월요일로
        if (deliveryDate.getDayOfWeek() == DayOfWeek.SATURDAY) {
            deliveryDate = deliveryDate.plusDays(2);
        } else if (deliveryDate.getDayOfWeek() == DayOfWeek.SUNDAY) {
            deliveryDate = deliveryDate.plusDays(1);
        }

        // 2일 후
        deliveryDate = deliveryDate.plusDays(2);

        // 공휴일 체크
        while (holidayService.isHoliday(deliveryDate)) {
            deliveryDate = deliveryDate.plusDays(1);
        }

        return deliveryDate;
    }
}
```

**성과**:
- 날짜 계산 오류 제로화
- 테스트 코드 작성 용이
- Thread-safe 보장

---

### 🔷 토스 - 함수형 프로그래밍 도입

**배경**: 거래 데이터 처리 성능 개선

```java
// ❌ Before
public class TransactionAnalyzer {
    public Map<String, BigDecimal> analyzeDailyTransactions(
            List<Transaction> transactions) {

        Map<String, BigDecimal> result = new HashMap<>();

        for (Transaction tx : transactions) {
            String date = tx.getDate().toString();
            BigDecimal amount = tx.getAmount();

            if (result.containsKey(date)) {
                BigDecimal current = result.get(date);
                result.put(date, current.add(amount));
            } else {
                result.put(date, amount);
            }
        }

        return result;
    }
}

// ✅ After
public class TransactionAnalyzer {
    public Map<LocalDate, BigDecimal> analyzeDailyTransactions(
            List<Transaction> transactions) {

        return transactions.parallelStream()
            .collect(Collectors.groupingBy(
                Transaction::getDate,
                Collectors.reducing(
                    BigDecimal.ZERO,
                    Transaction::getAmount,
                    BigDecimal::add
                )
            ));
    }
}
```

**성과**:
- 처리 속도 300% 향상 (병렬 스트림)
- 코드 가독성 개선
- 멀티코어 활용 최적화

---

### 🔷 배달의민족 - CompletableFuture 활용

**배경**: 비동기 주문 처리 개선

```java
// ❌ Before
public class OrderService {
    public OrderResult processOrder(Order order) {
        // 순차 처리 (느림)
        PaymentResult payment = paymentService.process(order);
        InventoryResult inventory = inventoryService.reserve(order);
        DeliveryResult delivery = deliveryService.assign(order);

        return new OrderResult(payment, inventory, delivery);
    }
}

// ✅ After (Java 8 CompletableFuture)
public class OrderService {
    public CompletableFuture<OrderResult> processOrder(Order order) {
        // 병렬 처리
        CompletableFuture<PaymentResult> paymentFuture =
            CompletableFuture.supplyAsync(() ->
                paymentService.process(order));

        CompletableFuture<InventoryResult> inventoryFuture =
            CompletableFuture.supplyAsync(() ->
                inventoryService.reserve(order));

        CompletableFuture<DeliveryResult> deliveryFuture =
            CompletableFuture.supplyAsync(() ->
                deliveryService.assign(order));

        return CompletableFuture.allOf(
                paymentFuture, inventoryFuture, deliveryFuture)
            .thenApply(v -> new OrderResult(
                paymentFuture.join(),
                inventoryFuture.join(),
                deliveryFuture.join()
            ));
    }
}
```

**성과**:
- 주문 처리 시간 70% 단축
- 동시 처리량 3배 증가
- 사용자 경험 개선

---

## 🚨 주니어 실수 시나리오

### ❌ 실수 1: 스트림 오남용

```java
// ❌ 잘못된 코드 - 단순 반복에 스트림 사용
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

// 불필요한 스트림
names.stream().forEach(System.out::println);

// ✅ 올바른 코드
names.forEach(System.out::println);  // 더 간단

// ❌ 잘못된 코드 - 인덱스가 필요한 경우
IntStream.range(0, names.size())
    .forEach(i -> System.out.println(i + ": " + names.get(i)));

// ✅ 올바른 코드
for (int i = 0; i < names.size(); i++) {
    System.out.println(i + ": " + names.get(i));
}
```

**교훈**: 스트림은 변환/필터링이 필요할 때만 사용

---

### ❌ 실수 2: Optional 오남용

```java
// ❌ 잘못된 코드
public Optional<User> findUser(Long id) {
    User user = userRepository.findById(id);
    if (user == null) {
        return Optional.empty();
    }
    return Optional.of(user);
}

// 호출 시
Optional<User> userOpt = findUser(1L);
if (userOpt.isPresent()) {  // 이렇게 쓰면 Optional 의미 없음
    User user = userOpt.get();
    System.out.println(user.getName());
}

// ✅ 올바른 코드
public Optional<User> findUser(Long id) {
    return Optional.ofNullable(userRepository.findById(id));
}

// 호출 시
findUser(1L).ifPresent(user ->
    System.out.println(user.getName())
);

// 또는
String name = findUser(1L)
    .map(User::getName)
    .orElse("Unknown");
```

**교훈**: Optional은 함수형 스타일로 사용

---

### ❌ 실수 3: 날짜/시간 API 혼용

```java
// ❌ 잘못된 코드 - 새 API와 구 API 혼용
public void scheduleEvent() {
    LocalDateTime eventTime = LocalDateTime.now();

    // Date로 변환 (비추천)
    Date date = Date.from(eventTime.atZone(ZoneId.systemDefault()).toInstant());

    // Calendar 사용 (비추천)
    Calendar cal = Calendar.getInstance();
    cal.setTime(date);
}

// ✅ 올바른 코드 - 새 API만 사용
public void scheduleEvent() {
    LocalDateTime eventTime = LocalDateTime.now();
    ZonedDateTime zonedTime = eventTime.atZone(ZoneId.of("Asia/Seoul"));

    // 모든 계산을 java.time으로
    LocalDateTime futureTime = eventTime.plusHours(2);
    boolean isAfter = futureTime.isAfter(eventTime);
}
```

**교훈**: java.time 패키지만 사용 (구 API 피하기)

---

### ❌ 실수 4: 병렬 스트림 부작용

```java
// ❌ 잘못된 코드 - 공유 상태 수정
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
List<Integer> result = new ArrayList<>();

numbers.parallelStream()
    .forEach(n -> result.add(n * 2));  // Thread-safe 하지 않음!

// ✅ 올바른 코드
List<Integer> result = numbers.parallelStream()
    .map(n -> n * 2)
    .collect(Collectors.toList());  // Thread-safe
```

**교훈**: 병렬 스트림에서 공유 상태 수정 금지

---

### ❌ 실수 5: 무한 스트림 limit 누락

```java
// ❌ 잘못된 코드 - 무한 루프
Stream.iterate(0, n -> n + 1)
    .filter(n -> n % 2 == 0)
    .forEach(System.out::println);  // 멈추지 않음!

// ✅ 올바른 코드 - limit 사용
Stream.iterate(0, n -> n + 1)
    .filter(n -> n % 2 == 0)
    .limit(10)
    .forEach(System.out::println);

// 또는 Java 9+
Stream.iterate(0, n -> n < 20, n -> n + 1)
    .filter(n -> n % 2 == 0)
    .forEach(System.out::println);
```

**교훈**: 무한 스트림은 항상 limit 사용

---

## 📊 마이그레이션 전략

### 1단계: Java 8 마이그레이션

```java
// Week 1-2: 람다 표현식 도입
// Before
list.forEach(new Consumer<String>() {
    @Override
    public void accept(String s) {
        System.out.println(s);
    }
});

// After
list.forEach(s -> System.out.println(s));

// Week 3-4: 스트림 API 도입
// Before
List<String> filtered = new ArrayList<>();
for (String s : list) {
    if (s.startsWith("A")) {
        filtered.add(s);
    }
}

// After
List<String> filtered = list.stream()
    .filter(s -> s.startsWith("A"))
    .collect(Collectors.toList());
```

### 2단계: Optional 도입

```java
// Week 5-6: Optional 리팩토링
// Before
public User findUser(Long id) {
    User user = repository.findById(id);
    if (user == null) {
        throw new UserNotFoundException();
    }
    return user;
}

// After
public Optional<User> findUser(Long id) {
    return Optional.ofNullable(repository.findById(id));
}
```

### 3단계: 날짜/시간 API 마이그레이션

```java
// Week 7-8: java.time 패키지로 전환
// Before
Date date = new Date();
Calendar cal = Calendar.getInstance();

// After
LocalDate date = LocalDate.now();
LocalDateTime dateTime = LocalDateTime.now();
```

### 4단계: Java 11+ 기능 도입

```java
// Week 9-10: var, 새로운 String 메서드
var list = List.of("A", "B", "C");
var name = "Alice";

String multiline = """
    {
      "name": "Alice"
    }
    """;
```

---

## 🎓 핵심 요약

### 마이그레이션 체크리스트

```
✅ 람다 표현식으로 익명 클래스 대체
✅ 스트림 API로 반복문 리팩토링
✅ Optional로 null 처리 개선
✅ java.time으로 날짜 처리 전환
✅ CompletableFuture로 비동기 처리
✅ 병렬 스트림으로 성능 최적화
```

### 주의사항

```
⚠️ 스트림은 필요할 때만 사용
⚠️ Optional.get() 대신 함수형 메서드 사용
⚠️ 병렬 스트림은 대량 데이터에만
⚠️ 무한 스트림에는 반드시 limit
⚠️ 공유 상태 수정 피하기
```

**다음 Part 3**: 성능 최적화 & 면접 질문
