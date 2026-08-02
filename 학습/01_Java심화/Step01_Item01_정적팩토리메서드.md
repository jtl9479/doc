# Step 1 - Item 1: 생성자 대신 정적 팩토리 메서드를 고려하라

> **학습 상태**: 미시작
> **학습 일자**:
> **교재**: Effective Java 3rd Edition — 2장 Item 1
> **학습 목표**: 정적 팩토리 메서드의 장점 4가지·단점 2가지를 설명 가능. 네이밍 관례(`of`, `from`, `valueOf`, `getInstance` 등) 숙지. GoF 팩토리 메서드 패턴과의 차이 설명 가능.

---

## 1. 왜 써야 하는가 (안 쓰면 이런 문제)

### 실무 피해 시나리오

ERP에서 주문 DTO를 만들고 있다고 하자. 목록 조회용·상세 조회용·Entity 변환용으로 각각 다른 형태가 필요하다.

```java
// 생성자만 제공하는 경우
public class OrderDto {
    public OrderDto(String orderId, String customerName) { ... }
    public OrderDto(String orderId, String customerName, BigDecimal amount) { ... }
    public OrderDto(String orderId) { ... }  // 뭘 위한 것?
}

// 6개월 후, 신규 입사자가 이 코드를 본다면
OrderDto dto = new OrderDto("ORD-001");
// → "이게 뭐지? IDE에서 생성자 정의로 점프해서 확인해야 함"
```

**더 심각한 문제**: 매개변수 타입이 같은 용도 2개를 만들고 싶을 때.

```java
// "거래처 코드로 조회" vs "거래처명으로 조회" — 둘 다 String 1개
public User(String code) { ... }
public User(String name) { ... }  // 컴파일 에러! 시그니처 동일
```

생성자로는 이 2개를 구분할 방법이 없다. 강제로 `CustomerCode`, `CustomerName` 같은 래퍼 타입을 만들어야 한다. 오버엔지니어링.

### 면접에서 어떻게 나오는가

시니어 면접 단골 질문.

- "생성자 대신 정적 팩토리 메서드를 쓰는 이유는?"
- "정적 팩토리 메서드의 장점 4가지를 말해보세요"
- "`Integer.valueOf(127) == Integer.valueOf(127)`은 true인가 false인가? 이유는?"
- "정적 팩토리 메서드와 GoF의 Factory Method 패턴은 같은 것인가?"

모른다면 시니어 프레임에서 감점. 실무 코드 리뷰에서도 "왜 `new`로만 열었어요? `of`나 `from`으로 만들 수 있지 않아요?"라는 리뷰가 수시로 온다.

---

## 2. 비유로 직관 잡기

**생성자 = 주문할 때마다 요리를 새로 만드는 식당**

주문이 들어오면 무조건 처음부터 조리. 같은 요리 100번 주문하면 100번 조리. 메뉴판도 없고 요리 이름도 못 붙인다 — "요리"라는 단어만 쓸 수 있다(클래스 이름).

**정적 팩토리 메서드 = 메뉴판 있는 식당**

- 메뉴판에 이름이 있음 → `User.withEmail()`, `OrderDto.from(entity)` (장점 1: **이름**)
- 자주 나가는 메뉴는 미리 만들어둠 → `Boolean.valueOf()`는 `TRUE`/`FALSE` 재사용 (장점 2: **캐싱**)
- "파스타" 시키면 `크림파스타` 나올 수도, `토마토파스타` 나올 수도 — 상위 카테고리만 보장 (장점 3: **하위 타입 반환**)
- 주문 조건에 따라 다른 주방에서 조리 — `EnumSet.of()`는 원소 수에 따라 `RegularEnumSet` 또는 `JumboEnumSet` 반환 (장점 4: **조건부 클래스 선택**)

주방장(정적 팩토리 메서드)이 판단한다. 손님(호출자)은 "파스타 주세요"만 하면 된다.

---

## 3. 핵심 개념

### 장점 1 — 이름을 가질 수 있다

생성자는 클래스 이름과 동일해야 한다는 제약이 있다. **반환될 객체의 특성을 이름으로 표현할 수 없다.**

```java
// 생성자: 시그니처로만 구분. "int, int, Random"이 뭘 만드는지 클래스 정의로 이동해야 앎
BigInteger bi = new BigInteger(32, 10, new Random());

// 정적 팩토리: 이름 자체가 문서
BigInteger prime = BigInteger.probablePrime(32, new Random());  // "소수구나"
```

**더 중요한 차이**: 같은 시그니처의 생성자는 하나만 존재 가능. 정적 팩토리는 이름만 다르면 여러 개 가능.

```java
// 생성자: 불가능
public User(String code) { ... }
public User(String name) { ... }  // 컴파일 에러

// 정적 팩토리: 가능
public static User withCode(String code) { ... }
public static User withName(String name) { ... }
```

### 장점 2 — 호출마다 인스턴스를 새로 생성하지 않아도 된다

생성자는 호출할 때마다 **반드시** 새 객체를 만든다. 정적 팩토리는 메서드 내부에서 자유롭게 제어 가능.

```java
// Boolean.valueOf()의 실제 구현 (OpenJDK)
public static Boolean valueOf(boolean b) {
    return b ? Boolean.TRUE : Boolean.FALSE;
    // 미리 만들어둔 상수 재사용. new Boolean() 호출 없음. 객체 생성 비용 0.
}
```

이것을 **인스턴스 통제(instance-controlled)** 클래스라 한다. 인스턴스를 통제하면:
- **싱글턴**(Item 3): 항상 같은 인스턴스 반환 가능
- **인스턴스화 불가**(Item 4): 아예 인스턴스를 안 만듦
- **불변 값 클래스**(Item 17): 동치인 인스턴스가 하나뿐임을 보장 (`a == b` ⇔ `a.equals(b)`)

**플라이웨이트 패턴**이 이 기법을 활용한 대표 디자인 패턴. `Integer.valueOf()`도 -128~127 범위는 캐싱한다.

```java
Integer a = Integer.valueOf(127);
Integer b = Integer.valueOf(127);
System.out.println(a == b);  // true — 캐시 범위 안

Integer c = Integer.valueOf(128);
Integer d = Integer.valueOf(128);
System.out.println(c == d);  // false — 캐시 범위 밖이라 새 객체
```

### 장점 3 — 반환 타입의 하위 타입 객체를 반환할 수 있다

생성자는 해당 클래스의 인스턴스**만** 반환. 정적 팩토리는 반환 타입을 **인터페이스나 상위 클래스**로 선언하고 실제로는 하위 타입을 반환 가능.

```java
// List.of()의 반환 타입은 List. 내부 구현은 원소 수에 따라 다름
List<String> list0 = List.of();                 // ImmutableCollections.EMPTY_LIST
List<String> list1 = List.of("a");              // ImmutableCollections.List12
List<String> list2 = List.of("a", "b");         // ImmutableCollections.List12
List<String> listN = List.of("a", "b", "c");    // ImmutableCollections.ListN
```

**왜 중요한가**:

1. **구현체를 숨길 수 있다** — 호출자는 `List` 인터페이스만 알면 됨. API 제공자는 내부 구현을 자유롭게 교체 가능.
2. **API를 작게 유지** — `java.util.Collections`는 45개 유틸리티 구현체를 숨기고 몇 개의 팩토리 메서드로만 노출.
3. **다음 릴리스에서 구현체 교체 자유** — `List.of()` 내부 구현을 바꿔도 호출 코드는 한 줄도 안 바뀜.

### 장점 4 — 입력 매개변수에 따라 매번 다른 클래스의 객체 반환 가능

장점 3의 확장.

```java
// EnumSet.noneOf()의 실제 구현 (OpenJDK)
public static <E extends Enum<E>> EnumSet<E> noneOf(Class<E> elementType) {
    Enum<?>[] universe = getUniverse(elementType);
    if (universe.length <= 64)
        return new RegularEnumSet<>(elementType, universe);   // long 1개로 비트 연산
    else
        return new JumboEnumSet<>(elementType, universe);     // long[] 배열로 비트 연산
}
```

호출자는 `EnumSet`만 알면 된다. 내부적으로 어떤 클래스가 반환되는지 몰라도 되고 알 필요도 없다. 새 구현체(`JumboEnumSet`)가 추가되거나 삭제돼도 기존 코드는 영향 없음.

이것이 **인터페이스 기반 프로그래밍**(Item 64)의 핵심 — "구현이 아닌 인터페이스에 프로그래밍하라"가 정적 팩토리로 자연스럽게 달성된다.

### 단점 1 — 상속하려면 public/protected 생성자가 필요

정적 팩토리만 제공하고 생성자를 private으로 감추면 하위 클래스를 만들 수 없다. `Collections`의 구현체들(`UnmodifiableList`, `SynchronizedMap`)은 직접 상속 불가.

하지만 **이것이 단점만은 아니다**:
- **상속보다 컴포지션 유도** (Item 18)
- **불변 타입을 만들려면 오히려 이 제약이 필요** (Item 17)

상속의 위험성(상위 클래스 변경에 취약, 캡슐화 깨짐)을 생각하면 이 "단점"은 오히려 좋은 설계로 가는 길잡이.

### 단점 2 — 프로그래머가 찾기 어렵다

생성자는 Javadoc에서 별도 섹션으로 명확히 드러나지만, 정적 팩토리는 다른 static 메서드와 섞인다.

이 문제를 완화하기 위해 **널리 알려진 네이밍 관례**를 따른다.

| 이름 | 의미 | 예시 |
|------|------|------|
| `from` | 매개변수 1개로 **형변환** | `Date.from(instant)` |
| `of` | 매개변수 여러 개로 **집계** | `EnumSet.of(RED, BLUE)` |
| `valueOf` | from/of의 더 자세한 버전 | `BigInteger.valueOf(100L)` |
| `instance` / `getInstance` | 같은 인스턴스 보장은 X (매개변수로 명시한 인스턴스 반환) | `StackWalker.getInstance(option)` |
| `create` / `newInstance` | 매번 **새** 인스턴스 보장 | `Array.newInstance(classObj, 10)` |
| `getType` | 팩토리가 **다른 클래스**에 있을 때. Type은 반환 타입 | `Files.getFileStore(path)` |
| `newType` | 팩토리가 **다른 클래스**에 있을 때. 매번 새 인스턴스 | `Files.newBufferedReader(path)` |
| `type` | getType/newType의 간결한 버전 | `Collections.list(legacy)` |

---

## 4. Bad vs Good 코드 비교 + 트레이드오프

### 시나리오: ERP 수주 DTO

**Bad — 생성자만 제공**

```java
public class OrderDto {
    public OrderDto(String orderId, String customerName) { ... }
    public OrderDto(String orderId, String customerName, BigDecimal amount) { ... }
    public OrderDto(Order entity) { ... }
}

// 호출
OrderDto dto1 = new OrderDto("ORD-001", "홍길동");
OrderDto dto2 = new OrderDto(orderEntity);
```

**문제**:
- 용도가 이름으로 드러나지 않음 — 시그니처로만 유추
- 매개변수 타입이 같은 용도를 구분할 수 없음
- 인스턴스 캐싱·하위 타입 반환 불가

**Good — 정적 팩토리**

```java
public class OrderDto {
    private final String orderId;
    private final String customerName;
    private final BigDecimal amount;

    private OrderDto(String orderId, String customerName, BigDecimal amount) {
        this.orderId = orderId;
        this.customerName = customerName;
        this.amount = amount;
    }

    // 용도별 이름
    public static OrderDto forList(String orderId, String customerName) {
        return new OrderDto(orderId, customerName, null);
    }

    public static OrderDto forDetail(String orderId, String customerName, BigDecimal amount) {
        return new OrderDto(orderId, customerName, amount);
    }

    // Entity 변환 — from 관례
    public static OrderDto from(Order entity) {
        return new OrderDto(
            entity.getId(),
            entity.getCustomer().getName(),
            entity.getAmount()
        );
    }
}

// 호출 — 의도가 이름으로 드러남
OrderDto listDto = OrderDto.forList("ORD-001", "홍길동");
OrderDto detailDto = OrderDto.forDetail("ORD-001", "홍길동", BigDecimal.valueOf(10000));
OrderDto fromEntity = OrderDto.from(orderEntity);
```

### Good 코드의 트레이드오프

- **상속 불가**: `private` 생성자 때문에 하위 클래스를 만들 수 없음. DTO는 상속할 이유가 없으므로 OK. 하지만 상속이 필요한 도메인 클래스라면 재고 필요.
- **API 문서에서 눈에 덜 띔**: 네이밍 관례(`of`, `from`, `valueOf` 등)를 반드시 지켜야 함. 관례를 어기면 사용자가 인스턴스 생성 방법을 못 찾음.
- **코드량 증가**: 생성자 1개보다 정적 팩토리 여러 개가 작성·유지 부담이 큼. 매개변수 1~2개뿐이고 용도가 하나라면 **그냥 생성자가 낫다**. Item 제목이 "**고려하라**"인 이유.

---

## 5. 실무 연결

Spring과 Java 표준에서 매일 쓰는 것들이 대부분 정적 팩토리.

```java
// Spring — ResponseEntity
ResponseEntity.ok(body)                                // 200 OK + 본문
ResponseEntity.notFound().build()                      // 404
ResponseEntity.status(HttpStatus.CREATED).body(result) // 201 + 본문

// Java 표준 — Optional
Optional.of(value)          // null이면 NullPointerException
Optional.empty()            // 빈 Optional
Optional.ofNullable(value)  // null이면 empty, 아니면 of

// Java 표준 — 불변 컬렉션
List.of("a", "b", "c")
Map.of("k1", "v1", "k2", "v2")
Set.of(1, 2, 3)
Collections.unmodifiableList(mutable)

// Java 표준 — 숫자 변환·캐싱
BigDecimal.valueOf(10000)   // new BigDecimal() 대신. 내부 캐싱 활용
Integer.valueOf(127)        // -128~127 캐싱
String.valueOf(123)         // int → String
```

ERP 패턴:

```java
// Entity → DTO 변환
OrderDto dto = OrderDto.from(orderEntity);

// 검색 조건 집계
SearchCondition cond = SearchCondition.of(startDate, endDate, customerId);

// 상태 변환
OrderStatus status = OrderStatus.valueOf("CONFIRMED");
```

Spring Data JPA의 `Pageable`, `Sort`도 같은 패턴.

```java
Pageable pageable = PageRequest.of(0, 20, Sort.by("createdAt").descending());
```

---

## 6. 오해하기 쉬운 부분 + Java 버전별 차이

### 오해 1 — "정적 팩토리 = GoF의 Factory Method 패턴"

**완전히 다르다.**

| 구분 | Effective Java의 정적 팩토리 메서드 | GoF의 Factory Method 패턴 |
|------|----------------------------------|-------------------------|
| 메커니즘 | **static 메서드**로 객체 생성 | **상속**으로 하위 클래스에서 객체 생성 결정 |
| 주 목적 | 생성자의 대안 (이름 부여, 캐싱, 하위 타입 반환) | 객체 생성 책임을 하위 클래스로 분리 |
| 예시 | `Integer.valueOf`, `List.of` | `Document.createPage()` → `WordDocument.createPage()`에서 Word 전용 Page 생성 |

이름이 비슷해서 헷갈리기 쉽다. **정적 팩토리 메서드는 GoF 패턴에 대응하는 디자인 패턴이 없다.**

### 오해 2 — "항상 정적 팩토리가 생성자보다 좋다"

Item 제목은 "**고려하라(consider)**"이지 "항상 쓰라"가 아니다. 매개변수가 1~2개이고 용도가 명확하면 생성자가 더 단순.

### 오해 3 — "정적 팩토리 = 유틸리티 메서드"

유틸리티 메서드(`Math.max()`, `Collections.sort()`)는 **기존 객체에 대한 연산**. 정적 팩토리는 **새 인스턴스 생성**. 목적이 다르다.

### 오해 4 — "정적 팩토리를 쓰면 생성자를 없애야 한다"

둘 다 제공해도 된다. 다만 정적 팩토리만 제공하고 생성자를 `private`로 감추는 것이 더 유연한 설계.

### Java 버전별 차이

| 버전 | 변화 | 영향 |
|------|------|------|
| Java 5 | 제네릭 도입 | 정적 팩토리의 타입 추론 편의 증가. `Map<String, List<String>> m = new HashMap<String, List<String>>()` 대신 `HashMap.newInstance()` 같은 팩토리 가치 ↑ |
| Java 7 | 다이아몬드 연산자 `<>` | `new HashMap<>()`로 타입 추론 가능. "제네릭 타입 추론" 목적의 정적 팩토리 **필요성 감소** |
| Java 8 | **인터페이스에 static 메서드** 가능 | `Collections.xxx()` 같은 동반 클래스(companion class) 불필요. 인터페이스에 직접 팩토리 선언 가능 |
| Java 9 | `List.of`, `Map.of`, `Set.of` 인터페이스 팩토리 | 불변 컬렉션 생성 표준화. Java 8 인터페이스 static 메서드의 수혜 |
| Java 16 | `Stream.toList()` | 최종 연산에 팩토리 통합 |

**레거시 전환 관점**:
- Java 8 이전 코드에서 `Collections.unmodifiableList(Arrays.asList(...))` → Java 9+에서 `List.of(...)`로 간결화 가능
- `HashMap<>()` 이후라면 타입 추론만 목적이던 팩토리는 불필요해졌지만, **이름/캐싱/하위 타입 반환** 목적의 팩토리는 여전히 유효

---

## 7. 확인 질문 (자가 검증)

- [ ] 정적 팩토리 메서드의 **장점 4가지**를 각각 코드 예시와 함께 설명할 수 있는가?
- [ ] **단점 2가지**를 말하고, 각 단점이 왜 치명적이지 않은지도 설명할 수 있는가?
- [ ] `of`, `from`, `valueOf`, `getInstance`, `create`, `newInstance`, `getType`, `newType`, `type`의 차이와 사용 시점을 구분할 수 있는가?
- [ ] 정적 팩토리 메서드와 **GoF 팩토리 메서드 패턴의 차이**를 표로 설명할 수 있는가?
- [ ] `Integer.valueOf(127) == Integer.valueOf(127)`이 true인 이유를 **장점 2(인스턴스 통제)**로 설명할 수 있는가?
- [ ] `Integer.valueOf(128) == Integer.valueOf(128)`이 false인 이유를 설명할 수 있는가?
- [ ] Java 8 이전에 `Collections` 동반 클래스가 필요했던 이유를 **장점 3(하위 타입 반환)**과 연결하여 설명할 수 있는가?
- [ ] Java 7 이후 `new HashMap<>()` 다이아몬드 연산자가 생겼는데도 `List.of()` 같은 팩토리가 여전히 유효한 이유를 설명할 수 있는가?

---

## 8. 정리 + 다음 안내

### 한 줄 정리
정적 팩토리 메서드는 **이름·인스턴스 통제·하위 타입 반환·조건부 클래스 선택**이라는 4가지 무기를 주지만, **상속 불가**와 **찾기 어려움**이라는 비용이 있으므로 "항상 쓰라"가 아닌 "**먼저 고려하라**".

### 핵심만 가져가기
1. 생성자 먼저 쓰지 말고 정적 팩토리를 **먼저 고려**한다
2. 이름은 **관례**를 지킨다 — `of`, `from`, `valueOf`, `getInstance` 등
3. 인스턴스 통제가 필요하면 **생성자를 private**으로 감춘다
4. GoF Factory Method 패턴과 **혼동하지 말 것**

### 다음 항목
- **Item 2 — 빌더 패턴**: 매개변수가 4개 이상이거나 선택적 매개변수가 많을 때 정적 팩토리보다 빌더가 유리. Item 1의 "이름 부여" 장점을 매개변수 수준에서 확장한 패턴.
- Item 1과 Item 2는 "객체를 어떻게 생성하는가"의 기본기. Step 1의 나머지 아이템(3 싱글턴 / 5 DI / 7 메모리 누수)은 "생성 이후의 생명주기"를 다룬다.
