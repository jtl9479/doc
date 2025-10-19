# 46장 Record와 Sealed Classes - Part 1: 실생활 비유로 이해하기

## 📚 목차
1. [비유 1: 신분증 카드 (Record 기본)](#비유-1-신분증-카드)
2. [비유 2: 계약서 양식 (불변 데이터)](#비유-2-계약서-양식)
3. [비유 3: 제한된 상속 (Sealed Classes)](#비유-3-제한된-상속)
4. [비유 4: 허가된 자격증 종류 (Permits)](#비유-4-허가된-자격증-종류)
5. [비유 5: Record와 Sealed 조합](#비유-5-record와-sealed-조합)

---

## 🔍 Record와 Sealed Classes란?

### Record (Java 14+)
**불변 데이터를 위한 간결한 클래스**입니다.

```java
// 전통적인 방식 (많은 보일러플레이트 코드)
public class Person {
    private final String name;
    private final int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public String name() { return name; }
    public int age() { return age; }

    @Override
    public boolean equals(Object o) { /* ... */ }
    @Override
    public int hashCode() { /* ... */ }
    @Override
    public String toString() { /* ... */ }
}

// Record 사용 (한 줄!)
public record Person(String name, int age) { }
```

### Sealed Classes (Java 17+)
**상속을 제한할 수 있는 클래스**입니다.

```java
// 지정된 클래스만 상속 가능
public sealed class Shape
    permits Circle, Rectangle, Triangle { }

public final class Circle extends Shape { }
public final class Rectangle extends Shape { }
public final class Triangle extends Shape { }
```

---

## 📖 비유 1: 신분증 카드 (Record 기본)

### 🎯 실생활 비유

신분증은 **수정할 수 없는 고정된 정보**를 담고 있습니다.

**신분증의 특징**:
```
1. 정보 변경 불가 (불변성)
2. 이름, 생년월일 등 기본 정보
3. 비교 가능 (같은 사람인지 확인)
4. 문자열로 출력 가능
```

**전통적인 클래스**는 신분증을 만들기 위해 많은 작업이 필요합니다.
**Record**는 신분증을 간단히 생성할 수 있습니다!

### 💻 Java 코드로 구현

```java
package record.example1;

/**
 * 전통적인 방식의 불변 클래스
 */
class PersonOld {
    private final String name;
    private final int age;
    private final String address;

    public PersonOld(String name, int age, String address) {
        this.name = name;
        this.age = age;
        this.address = address;
    }

    public String getName() { return name; }
    public int getAge() { return age; }
    public String getAddress() { return address; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        PersonOld person = (PersonOld) o;
        return age == person.age &&
               name.equals(person.name) &&
               address.equals(person.address);
    }

    @Override
    public int hashCode() {
        return java.util.Objects.hash(name, age, address);
    }

    @Override
    public String toString() {
        return "PersonOld{name='" + name + "', age=" + age +
               ", address='" + address + "'}";
    }
}

/**
 * Record 방식 (간결!)
 */
record PersonNew(String name, int age, String address) { }

/**
 * Record 기본 데모
 */
public class RecordBasicDemo {
    public static void main(String[] args) {
        System.out.println("=== Record 기본 ===\n");

        // 시나리오 1: 객체 생성
        System.out.println("📍 시나리오 1: 객체 생성");

        var personOld = new PersonOld("김철수", 25, "서울");
        var personNew = new PersonNew("김철수", 25, "서울");

        System.out.println("전통적인 방식: " + personOld);
        System.out.println("Record 방식: " + personNew);
        System.out.println();

        // 시나리오 2: 필드 접근
        System.out.println("📍 시나리오 2: 필드 접근");

        System.out.println("전통적인 방식:");
        System.out.println("  이름: " + personOld.getName());
        System.out.println("  나이: " + personOld.getAge());

        System.out.println("Record 방식:");
        System.out.println("  이름: " + personNew.name());  // getter 없이 직접 접근
        System.out.println("  나이: " + personNew.age());
        System.out.println();

        // 시나리오 3: equals와 hashCode 자동 생성
        System.out.println("📍 시나리오 3: equals와 hashCode");

        var person1 = new PersonNew("이영희", 30, "부산");
        var person2 = new PersonNew("이영희", 30, "부산");
        var person3 = new PersonNew("박민수", 28, "인천");

        System.out.println("person1.equals(person2): " + person1.equals(person2));
        System.out.println("person1.equals(person3): " + person1.equals(person3));
        System.out.println("person1.hashCode(): " + person1.hashCode());
        System.out.println("person2.hashCode(): " + person2.hashCode());
        System.out.println();

        // 시나리오 4: 불변성
        System.out.println("📍 시나리오 4: 불변성 (Immutability)");

        // Record는 수정 불가
        // person1.name = "변경";  // 컴파일 에러!

        System.out.println("✅ Record는 모든 필드가 final");
        System.out.println("✅ setter 메서드 없음");
        System.out.println("✅ 한 번 생성하면 변경 불가");
        System.out.println();

        // 시나리오 5: 코드 비교
        System.out.println("📍 시나리오 5: 코드량 비교");

        System.out.println("전통적인 방식: ~40줄");
        System.out.println("Record 방식: 1줄!");
        System.out.println("→ 97% 코드 감소!");
    }
}
```

### 🎯 핵심 포인트

**1. Record가 자동 생성하는 것들**:
```java
public record Person(String name, int age) { }

// 컴파일러가 자동 생성:
// 1. private final 필드
// 2. public 생성자
// 3. public 접근자 메서드 (name(), age())
// 4. equals() 메서드
// 5. hashCode() 메서드
// 6. toString() 메서드
```

**2. Record의 특징**:
```
1. 불변성 (Immutability)
   - 모든 필드는 final
   - setter 없음

2. 간결성
   - 보일러플레이트 코드 제거
   - 한 줄로 정의

3. 데이터 중심
   - 데이터 전달 객체 (DTO)에 적합
   - 값 기반 동등성
```

---

## 📖 비유 2: 계약서 양식 (불변 데이터)

### 🎯 실생활 비유

계약서는 한 번 작성하면 **수정할 수 없습니다**.

**계약서의 특징**:
```
1. 서명 후 변경 불가
2. 모든 정보가 고정됨
3. 복사본도 동일한 내용
4. 위조 방지를 위한 해시값
```

### 💻 Java 코드로 구현

```java
package record.example2;

import java.time.LocalDate;

/**
 * 계약서 Record
 */
record Contract(
    String contractId,
    String partyA,
    String partyB,
    LocalDate signedDate,
    int amount
) {
    // Compact Constructor (유효성 검증)
    public Contract {
        if (amount < 0) {
            throw new IllegalArgumentException("금액은 0 이상이어야 합니다");
        }
        if (partyA == null || partyB == null) {
            throw new IllegalArgumentException("계약 당사자는 필수입니다");
        }
    }

    // 추가 메서드 정의 가능
    public boolean isExpired(LocalDate today) {
        return signedDate.plusYears(1).isBefore(today);
    }

    public String summary() {
        return String.format("%s ↔ %s: %,d원", partyA, partyB, amount);
    }
}

/**
 * 주문 Record
 */
record Order(
    String orderId,
    String productName,
    int quantity,
    int unitPrice
) {
    // Canonical Constructor 오버라이드
    public Order {
        if (quantity <= 0) {
            throw new IllegalArgumentException("수량은 1 이상이어야 합니다");
        }
    }

    // 계산된 속성
    public int totalPrice() {
        return quantity * unitPrice;
    }
}

/**
 * 불변 데이터 데모
 */
public class ImmutableDataDemo {
    public static void main(String[] args) {
        System.out.println("=== 불변 데이터 (Record) ===\n");

        // 시나리오 1: 계약서 생성
        System.out.println("📍 시나리오 1: 계약서 생성");

        var contract = new Contract(
            "C001",
            "회사A",
            "회사B",
            LocalDate.of(2024, 1, 1),
            10000000
        );

        System.out.println(contract);
        System.out.println("요약: " + contract.summary());
        System.out.println();

        // 시나리오 2: 유효성 검증
        System.out.println("📍 시나리오 2: 유효성 검증");

        try {
            var invalidContract = new Contract(
                "C002",
                "회사A",
                null,  // 잘못된 입력
                LocalDate.now(),
                5000000
            );
        } catch (IllegalArgumentException e) {
            System.out.println("❌ 오류: " + e.getMessage());
        }
        System.out.println();

        // 시나리오 3: 주문 처리
        System.out.println("📍 시나리오 3: 주문 처리");

        var order1 = new Order("O001", "노트북", 2, 1500000);
        var order2 = new Order("O002", "마우스", 5, 30000);

        System.out.println(order1);
        System.out.println("  총액: " + String.format("%,d", order1.totalPrice()) + "원");
        System.out.println(order2);
        System.out.println("  총액: " + String.format("%,d", order2.totalPrice()) + "원");
        System.out.println();

        // 시나리오 4: 불변성의 장점
        System.out.println("📍 시나리오 4: 불변성의 장점");

        var originalOrder = new Order("O003", "키보드", 3, 80000);

        // 값을 변경하려면 새 객체 생성
        var updatedOrder = new Order(
            originalOrder.orderId(),
            originalOrder.productName(),
            5,  // 수량만 변경
            originalOrder.unitPrice()
        );

        System.out.println("원본: " + originalOrder);
        System.out.println("수정: " + updatedOrder);
        System.out.println("✅ 원본 데이터는 안전하게 보존");
    }
}
```

### 🎯 핵심 포인트

**1. Compact Constructor**:
```java
record Person(String name, int age) {
    // Compact Constructor (간결한 생성자)
    public Person {
        if (age < 0) {
            throw new IllegalArgumentException("나이는 0 이상");
        }
        // 필드 할당은 자동으로 수행됨
    }
}
```

**2. 추가 메서드**:
```java
record Order(String id, int quantity, int price) {
    // 계산된 속성
    public int total() {
        return quantity * price;
    }

    // 비즈니스 로직
    public boolean isLargeOrder() {
        return quantity > 100;
    }
}
```

---

## 📖 비유 3: 제한된 상속 (Sealed Classes)

### 🎯 실생활 비유

특정 **자격증은 정해진 종류만** 있습니다.

**운전면허 종류**:
```
- 1종 대형
- 1종 보통
- 2종 보통
- 2종 소형
→ 이 외의 종류는 없음!
```

**Sealed Class**는 상속할 수 있는 클래스를 제한합니다.

### 💻 Java 코드로 구현

```java
package sealed.example1;

/**
 * Sealed Class: 도형
 * Circle, Rectangle, Triangle만 상속 가능
 */
public sealed class Shape
    permits Circle, Rectangle, Triangle {

    private final String name;

    protected Shape(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public abstract double area();
}

/**
 * 원 (Circle)
 * final: 더 이상 상속 불가
 */
final class Circle extends Shape {
    private final double radius;

    public Circle(double radius) {
        super("원");
        this.radius = radius;
    }

    @Override
    public double area() {
        return Math.PI * radius * radius;
    }
}

/**
 * 직사각형 (Rectangle)
 */
final class Rectangle extends Shape {
    private final double width;
    private final double height;

    public Rectangle(double width, double height) {
        super("직사각형");
        this.width = width;
        this.height = height;
    }

    @Override
    public double area() {
        return width * height;
    }
}

/**
 * 삼각형 (Triangle)
 */
final class Triangle extends Shape {
    private final double base;
    private final double height;

    public Triangle(double base, double height) {
        super("삼각형");
        this.base = base;
        this.height = height;
    }

    @Override
    public double area() {
        return 0.5 * base * height;
    }
}

// ❌ 컴파일 에러: Shape는 sealed이므로 임의로 상속 불가
// class Pentagon extends Shape { }

/**
 * Sealed Class 데모
 */
class SealedClassDemo {
    public static void main(String[] args) {
        System.out.println("=== Sealed Classes ===\n");

        // 시나리오 1: 허용된 하위 클래스만 생성 가능
        System.out.println("📍 시나리오 1: 정의된 도형만 생성");

        Shape circle = new Circle(5.0);
        Shape rectangle = new Rectangle(4.0, 6.0);
        Shape triangle = new Triangle(3.0, 4.0);

        System.out.println(circle.getName() + " 넓이: " +
            String.format("%.2f", circle.area()));
        System.out.println(rectangle.getName() + " 넓이: " +
            String.format("%.2f", rectangle.area()));
        System.out.println(triangle.getName() + " 넓이: " +
            String.format("%.2f", triangle.area()));
        System.out.println();

        // 시나리오 2: Pattern Matching과 함께 사용
        System.out.println("📍 시나리오 2: Pattern Matching");

        System.out.println(getShapeInfo(circle));
        System.out.println(getShapeInfo(rectangle));
        System.out.println(getShapeInfo(triangle));
    }

    /**
     * Pattern Matching for Switch (Java 17+)
     */
    static String getShapeInfo(Shape shape) {
        return switch (shape) {
            case Circle c -> "원 (반지름: " + c.area() + ")";
            case Rectangle r -> "직사각형 (넓이: " + r.area() + ")";
            case Triangle t -> "삼각형 (넓이: " + t.area() + ")";
            // default 불필요! 모든 경우를 다룸
        };
    }
}
```

### 🎯 핵심 포인트

**1. Sealed 키워드**:
```java
// 상속을 제한
public sealed class Parent
    permits Child1, Child2, Child3 { }

// 허용된 하위 클래스
public final class Child1 extends Parent { }
public final class Child2 extends Parent { }
public sealed class Child3 extends Parent
    permits GrandChild { }  // 추가 상속 허용
```

**2. 하위 클래스 수식어**:
```java
// 3가지 선택지:
// 1. final: 더 이상 상속 불가
final class Circle extends Shape { }

// 2. sealed: 추가 상속 허용 (permits 필요)
sealed class Polygon extends Shape
    permits Square, Pentagon { }

// 3. non-sealed: 자유롭게 상속 가능
non-sealed class FlexibleShape extends Shape { }
```

---

## 📖 비유 4: 허가된 자격증 종류 (Permits)

### 🎯 실생활 비유

**결제 수단은 정해진 종류만** 있습니다.

```
결제 수단:
- 신용카드
- 체크카드
- 현금
- 상품권
→ 이 외의 수단은 허용하지 않음!
```

### 💻 Java 코드로 구현

```java
package sealed.example2;

/**
 * Sealed Interface: 결제 수단
 */
public sealed interface Payment
    permits CreditCard, DebitCard, Cash, Voucher {

    double getAmount();
    String getMethod();
}

/**
 * 신용카드
 */
record CreditCard(String cardNumber, double amount, int installment)
    implements Payment {

    @Override
    public double getAmount() {
        return amount;
    }

    @Override
    public String getMethod() {
        return "신용카드 (" + installment + "개월)";
    }
}

/**
 * 체크카드
 */
record DebitCard(String cardNumber, double amount)
    implements Payment {

    @Override
    public double getAmount() {
        return amount;
    }

    @Override
    public String getMethod() {
        return "체크카드";
    }
}

/**
 * 현금
 */
record Cash(double amount) implements Payment {
    @Override
    public String getMethod() {
        return "현금";
    }
}

/**
 * 상품권
 */
record Voucher(String voucherCode, double amount)
    implements Payment {

    @Override
    public double getAmount() {
        return amount;
    }

    @Override
    public String getMethod() {
        return "상품권";
    }
}

/**
 * 결제 처리 시스템
 */
class PaymentProcessor {
    public static void process(Payment payment) {
        System.out.println("결제 수단: " + payment.getMethod());
        System.out.println("결제 금액: " + String.format("%,.0f", payment.getAmount()) + "원");

        // Pattern Matching
        String message = switch (payment) {
            case CreditCard c -> "신용카드 결제 승인 (할부: " + c.installment() + "개월)";
            case DebitCard d -> "체크카드 결제 승인";
            case Cash c -> "현금 결제 완료";
            case Voucher v -> "상품권 사용 (코드: " + v.voucherCode() + ")";
        };

        System.out.println("→ " + message);
        System.out.println();
    }
}

/**
 * 결제 데모
 */
class PaymentDemo {
    public static void main(String[] args) {
        System.out.println("=== Sealed Interface (결제 시스템) ===\n");

        // 다양한 결제 수단
        Payment[] payments = {
            new CreditCard("1234-****-****-5678", 150000, 3),
            new DebitCard("9876-****-****-4321", 50000),
            new Cash(20000),
            new Voucher("GIFT-2024-001", 100000)
        };

        for (var payment : payments) {
            PaymentProcessor.process(payment);
        }

        System.out.println("📊 Sealed의 장점:");
        System.out.println("✅ 허용된 구현만 가능");
        System.out.println("✅ Pattern Matching 완전성 보장");
        System.out.println("✅ 타입 안전성");
    }
}
```

---

## 📖 비유 5: Record와 Sealed 조합

### 🎯 실생활 비유

**API 응답은 성공 또는 실패** 중 하나입니다.

```
API 응답:
- Success (데이터 포함)
- Error (에러 메시지 포함)
→ 이 두 가지만 가능!
```

### 💻 Java 코드로 구현

```java
package record.sealed;

/**
 * Sealed Interface + Record 조합
 */
public sealed interface Result<T>
    permits Success, Error {

    boolean isSuccess();
}

/**
 * 성공 응답 (Record)
 */
record Success<T>(T data) implements Result<T> {
    @Override
    public boolean isSuccess() {
        return true;
    }
}

/**
 * 실패 응답 (Record)
 */
record Error<T>(String message, int code) implements Result<T> {
    @Override
    public boolean isSuccess() {
        return false;
    }
}

/**
 * 사용자 데이터
 */
record User(String id, String name, String email) { }

/**
 * API 서비스
 */
class UserService {
    public static Result<User> getUser(String userId) {
        if (userId.equals("USER001")) {
            return new Success<>(
                new User("USER001", "김철수", "kim@example.com")
            );
        } else {
            return new Error<>("사용자를 찾을 수 없습니다", 404);
        }
    }
}

/**
 * Record + Sealed 조합 데모
 */
class RecordSealedDemo {
    public static void main(String[] args) {
        System.out.println("=== Record + Sealed 조합 ===\n");

        // 시나리오 1: 성공 응답
        System.out.println("📍 시나리오 1: 성공 응답");

        var result1 = UserService.getUser("USER001");
        handleResult(result1);

        // 시나리오 2: 실패 응답
        System.out.println("📍 시나리오 2: 실패 응답");

        var result2 = UserService.getUser("UNKNOWN");
        handleResult(result2);

        System.out.println("📊 조합의 장점:");
        System.out.println("✅ 타입 안전한 에러 처리");
        System.out.println("✅ null 대신 명시적 결과");
        System.out.println("✅ Pattern Matching 활용");
    }

    static void handleResult(Result<User> result) {
        switch (result) {
            case Success<User> success -> {
                System.out.println("✅ 성공!");
                System.out.println("  사용자: " + success.data().name());
                System.out.println("  이메일: " + success.data().email());
            }
            case Error<User> error -> {
                System.out.println("❌ 실패!");
                System.out.println("  오류: " + error.message());
                System.out.println("  코드: " + error.code());
            }
        }
        System.out.println();
    }
}
```

---

## 🎓 Part 1 종합 정리

### 📊 Record vs 전통적인 클래스

| 특징 | 전통적인 클래스 | Record |
|------|----------------|--------|
| 코드량 | 많음 (30-50줄) | 적음 (1줄) |
| 불변성 | 수동 구현 | 자동 보장 |
| equals/hashCode | 수동 구현 | 자동 생성 |
| toString | 수동 구현 | 자동 생성 |
| 상속 | 가능 | 불가 |

### 🎯 Sealed Classes 핵심

```java
// 상속 제한
sealed class Parent permits Child1, Child2 { }

// 하위 클래스 선택지:
final class Child1 extends Parent { }           // 더 이상 상속 X
sealed class Child2 extends Parent permits ... { }  // 추가 상속 O
non-sealed class Child3 extends Parent { }      // 자유 상속
```

**다음 Part 2에서는**: 3개 기업 사례 (쿠팡, 라인, 토스) + 4개 주니어 실수 시나리오를 다룹니다.
