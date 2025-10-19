# 46장 Record와 Sealed Classes - Part 2: 기업 사례 & 주니어 개발자 시나리오

## 📚 목차
1. [3개 기업 실전 사례](#기업-사례)
   - 쿠팡: 주문 데이터 처리
   - 라인: 메시지 타입 시스템
   - 토스: API 응답 표준화
2. [4개 주니어 개발자 실수 시나리오](#주니어-실수-시나리오)

---

## 🏢 기업 사례

### 🔷 기업 사례 1: 쿠팡 - 주문 데이터 처리

#### 📌 비즈니스 배경

쿠팡의 주문 시스템에서는 수많은 DTO(Data Transfer Object)를 사용합니다.

**문제 상황 (Before)**:
```java
// 보일러플레이트 코드가 많음
public class OrderDTO {
    private final String orderId;
    private final String customerId;
    private final List<OrderItem> items;
    // ... 30줄 이상의 생성자, getter, equals, hashCode, toString
}
```

#### 💡 Record를 활용한 해결책

```java
package com.coupang.order;

import java.time.LocalDateTime;
import java.util.*;

/**
 * 주문 아이템 (Record)
 */
record OrderItem(
    String productId,
    String productName,
    int quantity,
    int price
) {
    // 유효성 검증
    public OrderItem {
        if (quantity <= 0) {
            throw new IllegalArgumentException("수량은 1 이상이어야 합니다");
        }
        if (price < 0) {
            throw new IllegalArgumentException("가격은 0 이상이어야 합니다");
        }
    }

    // 계산된 속성
    public int totalPrice() {
        return quantity * price;
    }
}

/**
 * 주문 DTO (Record)
 */
record OrderDTO(
    String orderId,
    String customerId,
    String customerName,
    List<OrderItem> items,
    String address,
    LocalDateTime orderTime
) {
    // 방어적 복사
    public OrderDTO {
        items = List.copyOf(items);  // 불변 리스트로 변환
    }

    // 총 주문 금액
    public int totalAmount() {
        return items.stream()
            .mapToInt(OrderItem::totalPrice)
            .sum();
    }

    // 주문 항목 수
    public int itemCount() {
        return items.stream()
            .mapToInt(OrderItem::quantity)
            .sum();
    }
}

/**
 * 배송지 정보 (Record)
 */
record DeliveryAddress(
    String recipient,
    String phone,
    String zipCode,
    String address,
    String detailAddress
) {
    public DeliveryAddress {
        if (phone == null || !phone.matches("\\d{3}-\\d{4}-\\d{4}")) {
            throw new IllegalArgumentException("올바른 전화번호 형식이 아닙니다");
        }
    }

    public String fullAddress() {
        return String.format("[%s] %s %s", zipCode, address, detailAddress);
    }
}

/**
 * 쿠팡 주문 데모
 */
public class CoupangOrderDemo {
    public static void main(String[] args) {
        System.out.println("=== 쿠팡 주문 시스템 (Record) ===\n");

        // 시나리오 1: 주문 생성
        System.out.println("📍 시나리오 1: 주문 생성");

        var items = List.of(
            new OrderItem("P001", "노트북", 1, 1500000),
            new OrderItem("P002", "마우스", 2, 30000),
            new OrderItem("P003", "키보드", 1, 80000)
        );

        var order = new OrderDTO(
            "ORD-2024-001",
            "CUST-001",
            "김철수",
            items,
            "서울시 강남구",
            LocalDateTime.now()
        );

        System.out.println("주문 정보:");
        System.out.println("  주문번호: " + order.orderId());
        System.out.println("  고객명: " + order.customerName());
        System.out.println("  상품 수: " + order.itemCount() + "개");
        System.out.println("  총 금액: " + String.format("%,d", order.totalAmount()) + "원");
        System.out.println();

        // 시나리오 2: 불변성 보장
        System.out.println("📍 시나리오 2: 불변성 보장");

        // 원본 리스트 수정 시도
        var originalItems = new ArrayList<OrderItem>();
        originalItems.add(new OrderItem("P001", "노트북", 1, 1500000));

        var order2 = new OrderDTO(
            "ORD-2024-002",
            "CUST-002",
            "이영희",
            originalItems,
            "부산시 해운대구",
            LocalDateTime.now()
        );

        // 외부에서 리스트 수정 시도
        try {
            order2.items().add(new OrderItem("P002", "마우스", 1, 30000));
        } catch (UnsupportedOperationException e) {
            System.out.println("✅ 불변 리스트: 수정 불가");
        }
        System.out.println();

        // 성과 측정
        System.out.println("📊 Record 도입 효과:");
        System.out.println("✅ DTO 코드량 90% 감소 (40줄 → 4줄)");
        System.out.println("✅ equals/hashCode 버그 제거");
        System.out.println("✅ 불변성 자동 보장");
        System.out.println("✅ 유지보수성 향상");
    }
}
```

---

### 🔷 기업 사례 2: 라인 - 메시지 타입 시스템

#### 📌 비즈니스 배경

라인 메신저에서는 다양한 타입의 메시지가 있습니다.

**문제 상황**:
```java
// 메시지 타입을 구분하기 어려움
// instanceof 남발
// 새로운 타입 추가 시 누락 가능
```

#### 💡 Sealed Classes로 해결

```java
package com.line.messaging;

import java.time.LocalDateTime;

/**
 * Sealed Interface: 메시지
 */
public sealed interface Message
    permits TextMessage, ImageMessage, VideoMessage, StickerMessage, LocationMessage {

    String getMessageId();
    String getSenderId();
    LocalDateTime getTimestamp();
}

/**
 * 텍스트 메시지 (Record)
 */
record TextMessage(
    String messageId,
    String senderId,
    LocalDateTime timestamp,
    String content
) implements Message { }

/**
 * 이미지 메시지 (Record)
 */
record ImageMessage(
    String messageId,
    String senderId,
    LocalDateTime timestamp,
    String imageUrl,
    int width,
    int height
) implements Message { }

/**
 * 비디오 메시지 (Record)
 */
record VideoMessage(
    String messageId,
    String senderId,
    LocalDateTime timestamp,
    String videoUrl,
    int duration
) implements Message { }

/**
 * 스티커 메시지 (Record)
 */
record StickerMessage(
    String messageId,
    String senderId,
    LocalDateTime timestamp,
    String stickerId,
    String stickerPackId
) implements Message { }

/**
 * 위치 메시지 (Record)
 */
record LocationMessage(
    String messageId,
    String senderId,
    LocalDateTime timestamp,
    double latitude,
    double longitude,
    String address
) implements Message { }

/**
 * 메시지 처리기
 */
class MessageProcessor {
    public static String process(Message message) {
        // Pattern Matching: 모든 메시지 타입을 완전히 커버
        return switch (message) {
            case TextMessage text ->
                "텍스트: " + text.content();

            case ImageMessage image ->
                String.format("이미지: %s (%dx%d)",
                    image.imageUrl(), image.width(), image.height());

            case VideoMessage video ->
                String.format("비디오: %s (%d초)",
                    video.videoUrl(), video.duration());

            case StickerMessage sticker ->
                String.format("스티커: %s (팩: %s)",
                    sticker.stickerId(), sticker.stickerPackId());

            case LocationMessage location ->
                String.format("위치: %s (%.6f, %.6f)",
                    location.address(), location.latitude(), location.longitude());

            // default 불필요! (Sealed로 모든 타입 정의됨)
        };
    }

    public static int calculateSize(Message message) {
        return switch (message) {
            case TextMessage text -> text.content().length();
            case ImageMessage img -> 1024 * 1024;  // 1MB
            case VideoMessage video -> video.duration() * 100000;
            case StickerMessage sticker -> 5000;
            case LocationMessage loc -> 200;
        };
    }
}

/**
 * 라인 메시지 데모
 */
public class LineMessagingDemo {
    public static void main(String[] args) {
        System.out.println("=== 라인 메시지 타입 시스템 ===\n");

        var now = LocalDateTime.now();

        var messages = List.of(
            new TextMessage("M001", "USER001", now, "안녕하세요!"),
            new ImageMessage("M002", "USER002", now,
                "https://example.com/image.jpg", 1920, 1080),
            new VideoMessage("M003", "USER001", now,
                "https://example.com/video.mp4", 120),
            new StickerMessage("M004", "USER003", now, "S001", "PACK001"),
            new LocationMessage("M005", "USER002", now,
                37.5665, 126.9780, "서울 중구 세종대로")
        );

        System.out.println("📍 메시지 처리:");
        for (var message : messages) {
            System.out.println("[" + message.getMessageId() + "] " +
                MessageProcessor.process(message));
            System.out.println("  크기: " + MessageProcessor.calculateSize(message) + " bytes");
        }
        System.out.println();

        System.out.println("📊 Sealed Classes 효과:");
        System.out.println("✅ 타입 안전성 보장");
        System.out.println("✅ Pattern Matching 완전성");
        System.out.println("✅ 새 타입 추가 시 컴파일 에러로 누락 방지");
        System.out.println("✅ default 케이스 불필요");
    }
}
```

---

### 🔷 기업 사례 3: 토스 - API 응답 표준화

#### 📌 비즈니스 배경

토스 API에서는 성공/실패 응답을 명확히 구분해야 합니다.

#### 💡 Record + Sealed 조합

```java
package com.toss.api;

/**
 * Sealed Interface: API 응답
 */
public sealed interface ApiResponse<T>
    permits Success, ClientError, ServerError {

    boolean isSuccess();
    int statusCode();
}

/**
 * 성공 응답 (Record)
 */
record Success<T>(
    int statusCode,
    T data,
    String message
) implements ApiResponse<T> {
    public Success(T data) {
        this(200, data, "성공");
    }

    @Override
    public boolean isSuccess() {
        return true;
    }
}

/**
 * 클라이언트 에러 (Record)
 */
record ClientError<T>(
    int statusCode,
    String error,
    String message
) implements ApiResponse<T> {
    public ClientError(int statusCode, String message) {
        this(statusCode, "CLIENT_ERROR", message);
    }

    @Override
    public boolean isSuccess() {
        return false;
    }
}

/**
 * 서버 에러 (Record)
 */
record ServerError<T>(
    int statusCode,
    String error,
    String message
) implements ApiResponse<T> {
    public ServerError(String message) {
        this(500, "SERVER_ERROR", message);
    }

    @Override
    public boolean isSuccess() {
        return false;
    }
}

/**
 * 계좌 정보 (Record)
 */
record Account(String accountId, String accountNumber, long balance) { }

/**
 * 송금 서비스
 */
class TransferService {
    public static ApiResponse<Account> getAccount(String accountId) {
        if (accountId.equals("ACCT001")) {
            return new Success<>(
                new Account("ACCT001", "1234-5678-9012", 1000000L)
            );
        } else if (accountId.isEmpty()) {
            return new ClientError<>(400, "계좌 ID가 필요합니다");
        } else {
            return new ClientError<>(404, "계좌를 찾을 수 없습니다");
        }
    }

    public static ApiResponse<String> transfer(String from, String to, long amount) {
        if (amount <= 0) {
            return new ClientError<>(400, "금액은 0보다 커야 합니다");
        }
        if (amount > 10000000) {
            return new ClientError<>(400, "1회 송금 한도를 초과했습니다");
        }

        return new Success<>("송금이 완료되었습니다");
    }
}

/**
 * 토스 API 데모
 */
public class TossApiDemo {
    public static void main(String[] args) {
        System.out.println("=== 토스 API 응답 시스템 ===\n");

        // 시나리오 1: 성공 응답
        System.out.println("📍 시나리오 1: 계좌 조회 (성공)");
        var response1 = TransferService.getAccount("ACCT001");
        handleAccountResponse(response1);

        // 시나리오 2: 클라이언트 에러
        System.out.println("📍 시나리오 2: 계좌 조회 (실패)");
        var response2 = TransferService.getAccount("UNKNOWN");
        handleAccountResponse(response2);

        // 시나리오 3: 송금
        System.out.println("📍 시나리오 3: 송금");
        var response3 = TransferService.transfer("ACCT001", "ACCT002", 50000);
        handleTransferResponse(response3);

        // 시나리오 4: 송금 실패
        System.out.println("📍 시나리오 4: 송금 실패 (금액 초과)");
        var response4 = TransferService.transfer("ACCT001", "ACCT002", 20000000);
        handleTransferResponse(response4);

        System.out.println("📊 API 응답 표준화 효과:");
        System.out.println("✅ 일관된 응답 형식");
        System.out.println("✅ 타입 안전한 에러 처리");
        System.out.println("✅ null 사용 제거");
        System.out.println("✅ Pattern Matching 활용");
    }

    static void handleAccountResponse(ApiResponse<Account> response) {
        switch (response) {
            case Success<Account> success -> {
                System.out.println("✅ 성공 (코드: " + success.statusCode() + ")");
                var account = success.data();
                System.out.println("  계좌번호: " + account.accountNumber());
                System.out.println("  잔액: " + String.format("%,d", account.balance()) + "원");
            }
            case ClientError<Account> error -> {
                System.out.println("❌ 클라이언트 에러 (코드: " + error.statusCode() + ")");
                System.out.println("  메시지: " + error.message());
            }
            case ServerError<Account> error -> {
                System.out.println("❌ 서버 에러 (코드: " + error.statusCode() + ")");
                System.out.println("  메시지: " + error.message());
            }
        }
        System.out.println();
    }

    static void handleTransferResponse(ApiResponse<String> response) {
        var result = switch (response) {
            case Success<String> s -> "✅ " + s.message();
            case ClientError<String> e -> "❌ " + e.message();
            case ServerError<String> e -> "❌ 서버 오류: " + e.message();
        };
        System.out.println(result);
        System.out.println();
    }
}
```

---

## 🚨 주니어 실수 시나리오

### ❌ 실수 1: Record에 setter 추가 시도

#### 문제 코드

```java
// ❌ Record는 불변! setter 추가 불가
record Person(String name, int age) {
    // 컴파일 에러: Record는 setter를 가질 수 없음
    // public void setAge(int age) {
    //     this.age = age;
    // }
}
```

#### ✅ 올바른 해결책

```java
record Person(String name, int age) {
    // ✅ 새 객체를 반환하는 메서드
    public Person withAge(int newAge) {
        return new Person(this.name, newAge);
    }

    public Person withName(String newName) {
        return new Person(newName, this.age);
    }
}

class Solution {
    public static void main(String[] args) {
        var person1 = new Person("김철수", 25);

        // 나이를 변경하려면 새 객체 생성
        var person2 = person1.withAge(26);

        System.out.println("원본: " + person1);
        System.out.println("변경: " + person2);
        System.out.println();

        System.out.println("💡 핵심:");
        System.out.println("Record는 불변 객체");
        System.out.println("값 변경 = 새 객체 생성");
    }
}
```

---

### ❌ 실수 2: Record 상속 시도

#### 문제 코드

```java
// ❌ Record는 상속 불가
record Person(String name, int age) { }

// 컴파일 에러!
// class Employee extends Person { }
```

#### ✅ 올바른 해결책

```java
// ✅ 방법 1: 인터페이스 구현
interface Named {
    String name();
}

record Person(String name, int age) implements Named { }
record Company(String name, String address) implements Named { }

// ✅ 방법 2: 컴포지션 사용
record Employee(Person person, String employeeId, String department) {
    public String name() {
        return person.name();
    }

    public int age() {
        return person.age();
    }
}

class Solution {
    public static void main(String[] args) {
        System.out.println("=== Record 상속 대안 ===\n");

        // 인터페이스 구현
        Named person = new Person("김철수", 25);
        Named company = new Company("ABC회사", "서울");

        System.out.println("person.name(): " + person.name());
        System.out.println("company.name(): " + company.name());
        System.out.println();

        // 컴포지션
        var employee = new Employee(
            new Person("이영희", 30),
            "EMP001",
            "개발팀"
        );

        System.out.println("직원명: " + employee.name());
        System.out.println("부서: " + employee.department());
        System.out.println();

        System.out.println("💡 핵심:");
        System.out.println("Record는 final 클래스");
        System.out.println("상속 대신 인터페이스/컴포지션 사용");
    }
}
```

---

### ❌ 실수 3: Sealed에 non-sealed 누락

#### 문제 코드

```java
sealed class Shape permits Circle, Rectangle { }

// ❌ 컴파일 에러: final, sealed, non-sealed 중 하나 필요
// class Circle extends Shape { }
```

#### ✅ 올바른 해결책

```java
sealed class Shape permits Circle, Rectangle, Polygon { }

// ✅ 옵션 1: final (더 이상 상속 불가)
final class Circle extends Shape { }

// ✅ 옵션 2: sealed (추가 상속 허용)
sealed class Polygon extends Shape permits Triangle, Square { }

final class Triangle extends Polygon { }
final class Square extends Polygon { }

// ✅ 옵션 3: non-sealed (자유롭게 상속)
non-sealed class Rectangle extends Shape { }

class Solution {
    public static void main(String[] args) {
        System.out.println("=== Sealed 하위 클래스 수식어 ===\n");

        System.out.println("✅ 3가지 선택지:");
        System.out.println("1. final: 더 이상 상속 불가");
        System.out.println("2. sealed: 제한적 상속 허용 (permits 필요)");
        System.out.println("3. non-sealed: 자유롭게 상속 가능");
    }
}
```

---

### ❌ 실수 4: Record에 가변 컬렉션 사용

#### 문제 코드

```java
record Order(String id, List<String> items) { }

class Problem {
    public static void main(String[] args) {
        var items = new ArrayList<String>();
        items.add("상품1");

        var order = new Order("O001", items);

        // ❌ 외부에서 리스트 수정 가능!
        items.add("상품2");

        System.out.println(order);  // 상품2도 포함됨!
    }
}
```

#### ✅ 올바른 해결책

```java
record Order(String id, List<String> items) {
    // ✅ 방어적 복사 + 불변 리스트
    public Order {
        items = List.copyOf(items);
    }
}

class Solution {
    public static void main(String[] args) {
        System.out.println("=== Record 가변 컬렉션 처리 ===\n");

        var items = new ArrayList<String>();
        items.add("상품1");

        var order = new Order("O001", items);

        // 원본 리스트 수정
        items.add("상품2");

        System.out.println("원본 리스트: " + items);
        System.out.println("Order 리스트: " + order.items());
        System.out.println();

        // Record 리스트 수정 시도
        try {
            order.items().add("상품3");
        } catch (UnsupportedOperationException e) {
            System.out.println("✅ 불변 리스트: 수정 불가");
        }
        System.out.println();

        System.out.println("💡 핵심:");
        System.out.println("Compact Constructor에서 List.copyOf() 사용");
        System.out.println("완전한 불변성 보장");
    }
}
```

---

## 🎓 Part 2 종합 정리

### 📊 기업 도입 효과

| 항목 | 효과 |
|------|------|
| 코드량 | 80-90% 감소 |
| 버그 | equals/hashCode 버그 제거 |
| 유지보수 | 가독성 향상 |
| 타입 안전성 | Sealed로 완전성 보장 |

### 🚨 주니어 실수 요약

```
1. ❌ Record에 setter 추가 시도
   ✅ withXxx() 메서드로 새 객체 반환

2. ❌ Record 상속 시도
   ✅ 인터페이스 구현 또는 컴포지션

3. ❌ Sealed 하위 클래스 수식어 누락
   ✅ final, sealed, non-sealed 중 선택

4. ❌ Record에 가변 컬렉션
   ✅ Compact Constructor에서 List.copyOf()
```

**다음 Part 3에서는**: 성능 분석, 고급 패턴, 면접 질문을 다룹니다.
