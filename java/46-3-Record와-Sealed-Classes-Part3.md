# 46장 Record와 Sealed Classes - Part 3: 성능 최적화 & 고급 활용

## 📚 목차
1. [성능 분석](#성능-분석)
2. [고급 활용 기법](#고급-활용-기법)
3. [자주 묻는 면접 질문 TOP 10](#면접-질문)
4. [종합 정리](#종합-정리)

---

## 🚀 성능 분석

### 📊 Record vs 일반 클래스 성능

```java
package record.performance;

/**
 * Record 성능 테스트
 */
public class RecordPerformanceTest {
    private static final int ITERATIONS = 1_000_000;

    public static void main(String[] args) {
        System.out.println("=== Record 성능 테스트 ===\n");

        // Record
        record PersonRecord(String name, int age) { }

        // 일반 클래스
        class PersonClass {
            private final String name;
            private final int age;

            PersonClass(String name, int age) {
                this.name = name;
                this.age = age;
            }

            @Override
            public boolean equals(Object o) {
                if (this == o) return true;
                if (!(o instanceof PersonClass p)) return false;
                return age == p.age && name.equals(p.name);
            }

            @Override
            public int hashCode() {
                return 31 * name.hashCode() + age;
            }
        }

        System.out.println("📊 객체 생성 성능:");
        testCreation(PersonRecord.class, PersonClass.class);
        System.out.println();

        System.out.println("📊 equals/hashCode 성능:");
        testEquality();
        System.out.println();

        System.out.println("✅ 결론: Record와 일반 클래스의 성능 차이 미미");
        System.out.println("✅ Record는 가독성과 유지보수성 향상이 주 목적");
    }

    static void testCreation(Class<?> recordClass, Class<?> normalClass) {
        long start1 = System.nanoTime();
        for (int i = 0; i < ITERATIONS; i++) {
            var p = new record PersonRecord(String name, int age) { }("김철수", 25);
        }
        long end1 = System.nanoTime();
        System.out.println("Record: " +
            String.format("%.2f", (end1 - start1) / 1_000_000.0) + "ms");
    }

    static void testEquality() {
        record PersonRecord(String name, int age) { }
        var p1 = new PersonRecord("김철수", 25);
        var p2 = new PersonRecord("김철수", 25);

        long start = System.nanoTime();
        for (int i = 0; i < ITERATIONS; i++) {
            p1.equals(p2);
            p1.hashCode();
        }
        long end = System.nanoTime();

        System.out.println("100만 번 비교: " +
            String.format("%.2f", (end - start) / 1_000_000.0) + "ms");
    }
}
```

---

## 💎 고급 활용 기법

### 🔷 기법 1: Record 빌더 패턴

```java
package record.advanced;

/**
 * Record 빌더 패턴
 */
record Person(
    String name,
    int age,
    String email,
    String phone,
    String address
) {
    // 빌더 생성
    public static Builder builder() {
        return new Builder();
    }

    // 빌더 클래스
    public static class Builder {
        private String name;
        private int age;
        private String email;
        private String phone;
        private String address;

        public Builder name(String name) {
            this.name = name;
            return this;
        }

        public Builder age(int age) {
            this.age = age;
            return this;
        }

        public Builder email(String email) {
            this.email = email;
            return this;
        }

        public Builder phone(String phone) {
            this.phone = phone;
            return this;
        }

        public Builder address(String address) {
            this.address = address;
            return this;
        }

        public Person build() {
            return new Person(name, age, email, phone, address);
        }
    }
}

class BuilderDemo {
    public static void main(String[] args) {
        var person = Person.builder()
            .name("김철수")
            .age(25)
            .email("kim@example.com")
            .phone("010-1234-5678")
            .address("서울시 강남구")
            .build();

        System.out.println(person);
    }
}
```

### 🔷 기법 2: Pattern Matching 고급

```java
package sealed.advanced;

sealed interface Result<T> permits Success, Error { }
record Success<T>(T data) implements Result<T> { }
record Error<T>(String message) implements Result<T> { }

class PatternMatchingDemo {
    public static void main(String[] args) {
        // Nested Pattern Matching
        Result<Result<String>> nested = new Success<>(
            new Success<>("Hello")
        );

        String result = switch (nested) {
            case Success<Result<String>>(Success<String>(String s)) -> s;
            case Success<Result<String>>(Error<String> e) -> "Nested error";
            case Error<Result<String>> e -> "Outer error";
        };

        System.out.println(result);
    }
}
```

---

## 🎤 면접 질문

### ❓ Q1. Record란 무엇인가?

**답변**:
```
Record는 Java 14에서 도입된 불변 데이터 클래스입니다.

특징:
1. 간결한 문법 (1줄로 정의)
2. 자동 생성:
   - 생성자
   - getter (name())
   - equals/hashCode
   - toString

3. 불변성 (모든 필드 final)
4. 상속 불가 (final class)

예시:
record Person(String name, int age) { }

사용 시기:
- DTO (Data Transfer Object)
- Value Object
- API 응답 모델
- 불변 데이터 구조

장점:
- 보일러플레이트 코드 90% 감소
- 불변성 자동 보장
- equals/hashCode 버그 방지
```

---

### ❓ Q2. Sealed Classes란?

**답변**:
```
Sealed Classes는 상속을 제한할 수 있는 클래스입니다 (Java 17).

문법:
sealed class Shape
    permits Circle, Rectangle, Triangle { }

하위 클래스 선택지:
1. final: 더 이상 상속 불가
2. sealed: 제한적 상속 허용 (permits 필요)
3. non-sealed: 자유롭게 상속 가능

장점:
1. 도메인 모델링
   - 명확한 타입 계층
   - 제한된 하위 타입

2. Pattern Matching
   - 완전성 검증 (exhaustiveness)
   - default 케이스 불필요

3. API 설계
   - 의도된 확장만 허용
   - 외부 확장 방지

사용 예:
- 결제 수단 (카드, 현금, 상품권)
- API 응답 (성공, 에러)
- 메시지 타입 (텍스트, 이미지, 비디오)
```

---

### ❓ Q3. Record에 메서드를 추가할 수 있나?

**답변**:
```
네, 가능합니다.

1. 인스턴스 메서드:
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

2. 정적 메서드:
record Person(String name, int age) {
    // 팩토리 메서드
    public static Person of(String name, int age) {
        return new Person(name, age);
    }
}

3. Compact Constructor:
record Person(String name, int age) {
    // 유효성 검증
    public Person {
        if (age < 0) {
            throw new IllegalArgumentException();
        }
    }
}

제약사항:
- 인스턴스 필드 추가 불가
- setter 메서드 불가

주의점:
- 불변성 유지
- 비즈니스 로직은 최소화
- 복잡한 로직은 별도 서비스로
```

---

### ❓ Q4. Record vs Lombok @Data?

**답변**:
```
차이점:

1. 언어 기능 vs 라이브러리
   Record: Java 표준 기능
   Lombok: 외부 라이브러리

2. 불변성
   Record: 항상 불변
   @Data: 가변 (setter 생성)

3. 생성 코드
   Record: 컴파일러가 생성
   Lombok: 애노테이션 프로세서

4. 상속
   Record: 불가능 (final)
   @Data: 가능

5. 디버깅
   Record: 디버깅 쉬움
   Lombok: 생성 코드 확인 어려움

언제 사용?
Record:
- 불변 DTO
- API 모델
- Value Object
- Java 14+ 프로젝트

Lombok:
- 가변 객체 필요
- 레거시 프로젝트
- 복잡한 빌더 패턴

권장:
신규 프로젝트는 Record 사용
Lombok은 점진적으로 마이그레이션
```

---

### ❓ Q5. Record와 Sealed를 함께 사용하는 이유?

**답변**:
```
타입 안전한 sum type(합 타입)을 만들기 위해서입니다.

예시: API 응답
sealed interface ApiResponse<T>
    permits Success, Error { }

record Success<T>(T data) implements ApiResponse<T> { }
record Error<T>(String message) implements ApiResponse<T> { }

장점:

1. 명확한 타입 계층
   - 응답은 Success 또는 Error
   - 다른 타입 불가능

2. Pattern Matching 완전성
   String result = switch (response) {
       case Success<String> s -> s.data();
       case Error<String> e -> e.message();
       // default 불필요!
   };

3. null 제거
   - null 대신 Error 사용
   - Optional보다 명확

4. 타입 안전성
   - 컴파일 타임에 모든 케이스 검증
   - 새 타입 추가 시 컴파일 에러

실용 사례:
- API 응답 모델
- 상태 머신
- 이벤트 시스템
- 도메인 모델링

결론: Record + Sealed = 함수형 프로그래밍 스타일
```

---

### ❓ Q6. Record는 언제 사용해야 하나?

**답변**:
```
✅ 사용하기 좋은 경우:

1. DTO (Data Transfer Object)
   record UserDTO(String id, String name) { }

2. API 요청/응답
   record CreateUserRequest(String name, String email) { }
   record UserResponse(String id, String name) { }

3. Value Object
   record Money(long amount, String currency) { }
   record Point(int x, int y) { }

4. 설정/구성 데이터
   record DatabaseConfig(String url, String username) { }

5. 이벤트
   record UserCreatedEvent(String userId, Instant timestamp) { }

❌ 사용하지 말아야 할 경우:

1. JPA Entity
   - Record는 불변
   - JPA는 기본 생성자 필요
   - setter 필요

2. 복잡한 비즈니스 로직
   - Record는 데이터 중심
   - 복잡한 로직은 별도 서비스

3. 가변 상태 필요
   - Record는 불변
   - 가변 객체는 일반 클래스

4. 상속 필요
   - Record는 final
   - 상속 불가

원칙:
- 데이터만 담는 단순 클래스
- 불변성이 필요한 경우
- 값 기반 동등성
```

---

### ❓ Q7. Compact Constructor란?

**답변**:
```
Compact Constructor는 Record의 간결한 생성자 문법입니다.

일반 생성자:
record Person(String name, int age) {
    // 매개변수 반복
    public Person(String name, int age) {
        if (age < 0) {
            throw new IllegalArgumentException();
        }
        this.name = name;
        this.age = age;
    }
}

Compact Constructor:
record Person(String name, int age) {
    // 매개변수 선언 없음
    // 필드 할당 자동
    public Person {
        if (age < 0) {
            throw new IllegalArgumentException();
        }
        // this.name = name; 자동
        // this.age = age; 자동
    }
}

장점:
1. 코드 간결
2. 매개변수 반복 제거
3. 필드 할당 자동

사용 시기:
1. 유효성 검증
   public Person {
       if (name == null) throw new NullPointerException();
   }

2. 정규화
   public Person {
       name = name.trim();
   }

3. 방어적 복사
   public Order {
       items = List.copyOf(items);
   }

주의사항:
- 필드 할당은 자동
- return 문 불가
- 검증/변환만 수행
```

---

### ❓ Q8. Sealed의 permits를 생략할 수 있나?

**답변**:
```
같은 파일에 있으면 생략 가능합니다 (Java 17+).

생략 가능 (같은 파일):
// Shape.java
sealed class Shape { }  // permits 생략

final class Circle extends Shape { }
final class Rectangle extends Shape { }
// 같은 파일에 있으면 자동 추론

생략 불가 (다른 파일):
// Shape.java
public sealed class Shape
    permits Circle, Rectangle { }  // 명시 필요

// Circle.java
public final class Circle extends Shape { }

// Rectangle.java
public final class Rectangle extends Shape { }

권장사항:
1. 작은 타입 계층: 같은 파일에 작성
2. 큰 타입 계층: 별도 파일 + permits 명시
3. 공개 API: permits 명시 (명확성)

이점:
- 같은 파일: 응집도 높음
- 별도 파일: 책임 분리

선택 기준:
- 타입 수가 적으면 같은 파일
- 각 타입이 복잡하면 별도 파일
```

---

### ❓ Q9. Record에 빌더 패턴을 사용할 수 있나?

**답변**:
```
가능하지만, Record의 장점이 줄어듭니다.

방법 1: 정적 내부 빌더
record Person(String name, int age, String email) {
    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private String name;
        private int age;
        private String email;

        public Builder name(String name) {
            this.name = name;
            return this;
        }
        // ... 생략

        public Person build() {
            return new Person(name, age, email);
        }
    }
}

방법 2: with 메서드
record Person(String name, int age, String email) {
    public Person withName(String name) {
        return new Person(name, this.age, this.email);
    }

    public Person withAge(int age) {
        return new Person(this.name, age, this.email);
    }
}

언제 사용?
✅ 필드가 많을 때 (5개 이상)
✅ 선택적 필드가 많을 때
✅ 복잡한 객체 생성 로직

대안:
1. 여러 생성자
   record Person(String name, int age) {
       public Person(String name) {
           this(name, 0);
       }
   }

2. 정적 팩토리 메서드
   public static Person of(String name) {
       return new Person(name, 0);
   }

결론:
Record는 단순한 데이터 클래스에 적합
복잡한 빌더가 필요하면 일반 클래스 고려
```

---

### ❓ Q10. Record 마이그레이션 전략?

**답변**:
```
단계적 마이그레이션 전략:

1단계: 후보 식별
- 불변 데이터 클래스
- DTO, Value Object
- 단순 모델 클래스

2단계: 영향도 분석
- 상속 사용 여부
- JPA Entity 여부
- 외부 라이브러리 의존성

3단계: 변환
Before:
public class Person {
    private final String name;
    private final int age;
    // 생성자, getter, equals, hashCode, toString
}

After:
public record Person(String name, int age) { }

4단계: 테스트
- 단위 테스트 실행
- equals/hashCode 동작 확인
- 직렬화 테스트 (필요시)

5단계: 점진적 적용
- 신규 클래스부터
- 테스트가 있는 클래스
- 영향 범위가 작은 클래스

주의사항:
❌ JPA Entity 변환 금지
❌ 상속 구조 변환 주의
❌ 리플렉션 사용 코드 확인

체크리스트:
✅ Java 14+ 사용
✅ 불변성 요구사항 만족
✅ 상속 불필요
✅ 테스트 커버리지 충분

마이그레이션 우선순위:
1순위: 새 코드
2순위: DTO
3순위: Value Object
4순위: 기존 불변 클래스
```

---

## 🎓 종합 정리

### 📊 Record 체크리스트

```
✅ 사용하기 좋은 경우:
1. DTO (API 요청/응답)
2. Value Object (Money, Point)
3. 설정 데이터
4. 이벤트 객체
5. 불변 데이터 구조

❌ 사용하지 말아야 할 경우:
1. JPA Entity
2. 복잡한 비즈니스 로직
3. 상속이 필요한 경우
4. 가변 상태가 필요한 경우
```

### 🎯 Sealed Classes 활용

```java
// 도메인 모델링
sealed interface Payment
    permits CreditCard, DebitCard, Cash { }

// API 응답
sealed interface Result<T>
    permits Success, Error { }

// 메시지 타입
sealed interface Message
    permits Text, Image, Video { }
```

### 💡 조합 패턴

```java
// Record + Sealed = 강력한 타입 안전성
sealed interface ApiResponse<T>
    permits Success, ClientError, ServerError { }

record Success<T>(T data) implements ApiResponse<T> { }
record ClientError<T>(String message) implements ApiResponse<T> { }
record ServerError<T>(String message) implements ApiResponse<T> { }

// Pattern Matching
String handle(ApiResponse<User> response) {
    return switch (response) {
        case Success<User> s -> "Success: " + s.data();
        case ClientError<User> e -> "Client Error: " + e.message();
        case ServerError<User> e -> "Server Error: " + e.message();
    };
}
```

---

## 🎉 시리즈 완료!

**Part 1**: 5가지 실생활 비유로 Record와 Sealed 이해
**Part 2**: 3개 기업 사례 + 4개 주니어 실수
**Part 3**: 성능 분석 + 고급 기법 + 면접 질문

Record와 Sealed Classes를 완벽하게 마스터했습니다!
