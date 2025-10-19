# 42장 Java 8+ 주요 기능 총정리 - Part 1: 실생활 비유로 이해하기

## 📚 목차
1. [Java 8+ 혁명](#java-8-혁명)
2. [주요 기능 개요](#주요-기능-개요)
3. [비유로 이해하기](#비유로-이해하기)
4. [버전별 핵심 기능](#버전별-핵심-기능)

---

## 🚀 Java 8+ 혁명

### Java의 진화

**Java 8**은 Java 역사상 가장 큰 변화를 가져온 버전입니다.

```java
// Java 7 이전
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
List<String> filtered = new ArrayList<>();
for (String name : names) {
    if (name.startsWith("A")) {
        filtered.add(name);
    }
}

// Java 8+ (함수형 프로그래밍)
List<String> filtered = names.stream()
    .filter(name -> name.startsWith("A"))
    .collect(Collectors.toList());
```

---

## 📋 주요 기능 개요

### Java 8 핵심 기능

```java
// 1. 람다 표현식
Runnable r = () -> System.out.println("Hello Lambda!");

// 2. 스트림 API
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
int sum = numbers.stream()
    .filter(n -> n % 2 == 0)
    .mapToInt(n -> n)
    .sum();

// 3. Optional
Optional<String> name = Optional.ofNullable(getName());
String result = name.orElse("Unknown");

// 4. 날짜/시간 API
LocalDate today = LocalDate.now();
LocalDateTime now = LocalDateTime.now();

// 5. 디폴트 메서드
interface Vehicle {
    default void start() {
        System.out.println("Starting...");
    }
}

// 6. 메서드 레퍼런스
List<String> names = Arrays.asList("Alice", "Bob");
names.forEach(System.out::println);
```

---

## 📖 비유 1: 레스토랑 주문 시스템

**전통적 방식 vs 모던 방식**

```java
// 🍽️ 전통적 방식 (Java 7)
class TraditionalRestaurant {
    public List<Order> processOrders(List<Order> orders) {
        List<Order> completedOrders = new ArrayList<>();

        for (Order order : orders) {
            if (order.isPaid()) {
                order.prepare();
                order.cook();
                order.serve();
                completedOrders.add(order);
            }
        }

        return completedOrders;
    }
}

// 🎯 모던 방식 (Java 8+)
class ModernRestaurant {
    public List<Order> processOrders(List<Order> orders) {
        return orders.stream()
            .filter(Order::isPaid)
            .peek(Order::prepare)
            .peek(Order::cook)
            .peek(Order::serve)
            .collect(Collectors.toList());
    }
}
```

**비유 설명:**
- **스트림**: 주문이 컨베이어 벨트를 타고 이동
- **filter**: 결제 완료된 주문만 통과
- **map**: 주문을 다른 형태로 변환
- **collect**: 최종 결과를 담는 트레이

---

## 📖 비유 2: 선물 포장

**Optional을 선물 상자로 이해하기**

```java
// 🎁 선물이 있을 수도, 없을 수도 있는 상자
class GiftBox {
    // 전통적 방식
    public String openTraditionalBox(String gift) {
        if (gift != null) {
            return gift.toUpperCase();
        } else {
            return "NO GIFT";
        }
    }

    // Optional 방식
    public String openModernBox(Optional<String> giftBox) {
        return giftBox
            .map(String::toUpperCase)
            .orElse("NO GIFT");
    }
}

// 사용 예시
GiftBox box = new GiftBox();

// 선물이 있는 경우
Optional<String> present = Optional.of("Toy Car");
System.out.println(box.openModernBox(present));  // "TOY CAR"

// 선물이 없는 경우
Optional<String> empty = Optional.empty();
System.out.println(box.openModernBox(empty));    // "NO GIFT"
```

---

## 📖 비유 3: 날짜 다이어리

**새로운 날짜/시간 API**

```java
// 📅 전통적 방식 (java.util.Date)
class OldDiary {
    public void writeEntry() {
        Date today = new Date();
        Calendar cal = Calendar.getInstance();
        cal.setTime(today);

        int year = cal.get(Calendar.YEAR);
        int month = cal.get(Calendar.MONTH) + 1;  // 0부터 시작!
        int day = cal.get(Calendar.DAY_OF_MONTH);

        System.out.println(year + "-" + month + "-" + day);
    }
}

// 🎯 모던 방식 (java.time.*)
class ModernDiary {
    public void writeEntry() {
        LocalDate today = LocalDate.now();
        System.out.println(today);  // 2025-10-12

        // 10일 후
        LocalDate future = today.plusDays(10);

        // 날짜 비교
        if (future.isAfter(today)) {
            System.out.println("미래 날짜입니다");
        }
    }
}
```

**개선점:**
- **불변성**: 날짜 객체가 변하지 않음 (Thread-safe)
- **명확성**: 월이 1부터 시작 (혼란 없음)
- **풍부한 API**: 날짜 계산이 쉬움

---

## 🔄 버전별 핵심 기능

### Java 8 (2014) - 혁명

```java
// 람다 + 스트림
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
names.stream()
    .filter(name -> name.length() > 3)
    .map(String::toUpperCase)
    .forEach(System.out::println);

// Optional
Optional<String> name = Optional.of("Alice");
name.ifPresent(System.out::println);

// 날짜/시간 API
LocalDateTime now = LocalDateTime.now();
ZonedDateTime tokyo = now.atZone(ZoneId.of("Asia/Tokyo"));
```

### Java 9 (2017) - 모듈화

```java
// 모듈 시스템
module com.myapp {
    requires java.sql;
    exports com.myapp.api;
}

// 컬렉션 팩토리 메서드
List<String> list = List.of("A", "B", "C");
Set<Integer> set = Set.of(1, 2, 3);
Map<String, Integer> map = Map.of("A", 1, "B", 2);
```

### Java 10 (2018) - 타입 추론

```java
// var 키워드
var name = "Alice";                    // String
var numbers = List.of(1, 2, 3);        // List<Integer>
var map = new HashMap<String, Integer>(); // HashMap<String, Integer>

// 로컬 변수에만 사용 가능
// var field;  ❌ 필드에는 사용 불가
// public var method() {}  ❌ 리턴 타입에 사용 불가
```

### Java 11 (2018) - LTS

```java
// String 메서드 추가
String str = "  Hello  ";
str.isBlank();              // 공백 체크
str.strip();                // 앞뒤 공백 제거 (Unicode 지원)
str.repeat(3);              // 반복
str.lines().count();        // 줄 수 세기

// HTTP Client (표준 API)
HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com"))
    .build();
HttpResponse<String> response = client.send(request,
    HttpResponse.BodyHandlers.ofString());
```

### Java 14 (2020) - Switch 표현식

```java
// 전통적 switch
String day = "MONDAY";
int numLetters = 0;
switch (day) {
    case "MONDAY":
    case "FRIDAY":
    case "SUNDAY":
        numLetters = 6;
        break;
    case "TUESDAY":
        numLetters = 7;
        break;
}

// 새로운 switch 표현식
int numLetters = switch (day) {
    case "MONDAY", "FRIDAY", "SUNDAY" -> 6;
    case "TUESDAY" -> 7;
    case "THURSDAY", "SATURDAY" -> 8;
    case "WEDNESDAY" -> 9;
    default -> throw new IllegalArgumentException();
};
```

### Java 15 (2020) - Text Blocks

```java
// 전통적 방식
String json = "{\n" +
              "  \"name\": \"Alice\",\n" +
              "  \"age\": 30\n" +
              "}";

// Text Blocks
String json = """
    {
      "name": "Alice",
      "age": 30
    }
    """;

// HTML
String html = """
    <html>
      <body>
        <h1>Hello World</h1>
      </body>
    </html>
    """;
```

### Java 16 (2021) - Records

```java
// 전통적 방식
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

// Record (1줄로 끝!)
public record Person(String name, int age) {}

// 사용
Person person = new Person("Alice", 30);
System.out.println(person.name());  // Alice
System.out.println(person.age());   // 30
```

### Java 17 (2021) - LTS

```java
// Sealed Classes (봉인된 클래스)
public sealed interface Shape
    permits Circle, Rectangle, Triangle {
    double area();
}

public final class Circle implements Shape {
    private final double radius;

    public Circle(double radius) { this.radius = radius; }

    public double area() {
        return Math.PI * radius * radius;
    }
}

// Pattern Matching for instanceof
if (obj instanceof String s) {
    System.out.println(s.toUpperCase());
}
```

### Java 21 (2023) - LTS

```java
// Virtual Threads (경량 스레드)
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i -> {
        executor.submit(() -> {
            Thread.sleep(Duration.ofSeconds(1));
            return i;
        });
    });
}

// Record Patterns
record Point(int x, int y) {}

Object obj = new Point(1, 2);
if (obj instanceof Point(int x, int y)) {
    System.out.println("x: " + x + ", y: " + y);
}

// Sequenced Collections
List<String> list = new ArrayList<>();
list.addFirst("First");
list.addLast("Last");
String first = list.getFirst();
String last = list.getLast();
```

---

## 🎯 Java 버전 선택 가이드

### LTS 버전 (장기 지원)

```
Java 8  (2014) - 2030년까지 지원 (Oracle)
Java 11 (2018) - 2026년까지 지원
Java 17 (2021) - 2029년까지 지원 ⭐ 추천
Java 21 (2023) - 2031년까지 지원 ⭐ 최신
```

### 실무 권장사항

```java
// 새 프로젝트 시작
✅ Java 17 또는 Java 21 사용

// 레거시 프로젝트
✅ Java 11 이상으로 업그레이드 고려

// Java 8
⚠️  점진적 업그레이드 계획 수립
```

---

## 💡 실전 활용 예시

### 전통적 vs 모던 코드 비교

```java
// 🔴 Java 7 스타일
public class OldStyle {
    public List<String> processData(List<User> users) {
        List<String> result = new ArrayList<>();

        for (User user : users) {
            if (user.getAge() >= 18) {
                String name = user.getName();
                if (name != null) {
                    result.add(name.toUpperCase());
                }
            }
        }

        Collections.sort(result);
        return result;
    }
}

// 🟢 Java 8+ 스타일
public class ModernStyle {
    public List<String> processData(List<User> users) {
        return users.stream()
            .filter(user -> user.getAge() >= 18)
            .map(User::getName)
            .filter(Objects::nonNull)
            .map(String::toUpperCase)
            .sorted()
            .collect(Collectors.toList());
    }
}
```

---

## 🎓 핵심 요약

### Java 8+ 3대 혁신

1. **함수형 프로그래밍**
   - 람다 표현식
   - 스트림 API
   - 메서드 레퍼런스

2. **타입 안전성 강화**
   - Optional
   - Record
   - Sealed Classes

3. **개발 생산성 향상**
   - var 키워드
   - Text Blocks
   - Switch 표현식

### 마이그레이션 전략

```java
// 단계적 마이그레이션
1. Java 8  → 람다 + 스트림 학습
2. Java 11 → LTS 업그레이드
3. Java 17 → Record + Sealed 활용
4. Java 21 → Virtual Threads 도입
```

**다음 Part 2**: 기업 사례 & 주니어 실수
