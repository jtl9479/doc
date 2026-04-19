# Step 1. Effective Java — 객체 생성과 파괴

> **학습 상태**: 미시작
> **학습 일자**:

---

## Item 1: 생성자 대신 정적 팩토리 메서드를 고려하라

### 1. 도입 (이것은 무엇이고, 왜 배우는가)

**정적 팩토리 메서드란**: `new` 생성자 대신 **static 메서드로 객체를 생성하여 반환**하는 기법입니다.

```java
// 일반 생성자로 객체 생성
Boolean b1 = new Boolean(true);

// 정적 팩토리 메서드로 객체 생성
Boolean b2 = Boolean.valueOf(true);
```

둘 다 `Boolean` 객체를 만드는 것은 같지만, 정적 팩토리 메서드는 생성자가 할 수 없는 4가지를 할 수 있습니다.

시니어 면접에서 "생성자 대신 쓰는 이유"로 자주 나옵니다. 실무에서도 `List.of()`, `Optional.of()`, `ResponseEntity.ok()` 등 매일 쓰는 API가 전부 이 패턴입니다.

이걸 모르면 API를 설계할 때 항상 `new`로 생성자만 열게 되고, 유연성이 떨어집니다. 특히 ERP처럼 DTO가 많은 시스템에서 `of()` 메서드 하나만 제공해도 코드 가독성이 크게 달라집니다.

면접에서는 이렇게 물어봅니다:
- "정적 팩토리 메서드의 장점을 말해보세요"
- "생성자 대신 정적 팩토리를 쓰는 이유는?"

### 2. 핵심 개념

#### 장점 1: 이름을 가질 수 있다

생성자는 클래스 이름과 동일해야 한다는 제약이 있습니다. 그래서 **생성자만으로는 반환될 객체의 특성을 설명할 수 없습니다.** 매개변수의 타입과 개수만으로 어떤 객체가 만들어지는지 유추해야 합니다.

```java
// 생성자: 뭘 만드는 건지 시그니처를 봐야 앎
BigInteger bi = new BigInteger(int, int, Random);  // ???

// 정적 팩토리: 이름만 봐도 "소수를 만드는구나" 알 수 있음
BigInteger prime = BigInteger.probablePrime(int, Random);
```

이 차이는 코드 리뷰에서 극명하게 드러납니다. 생성자 호출을 본 리뷰어는 생성자 시그니처를 확인하러 클래스 정의로 이동해야 합니다. 정적 팩토리 메서드는 이름 자체가 문서입니다.

**더 중요한 문제**: 같은 시그니처의 생성자는 클래스에 하나만 존재할 수 있습니다. 하지만 정적 팩토리 메서드는 이름이 다르므로 시그니처가 같아도 여러 개를 만들 수 있습니다.

```java
// 생성자: 시그니처가 겹침 → 컴파일 에러
public User(String name) { ... }
public User(String email) { ... }  // 둘 다 String 1개 → 불가능!

// 정적 팩토리: 이름이 다르므로 가능
public static User withName(String name) { ... }
public static User withEmail(String email) { ... }
```

이 상황은 실무에서 자주 발생합니다. ERP에서 "거래처 코드로 조회"와 "거래처명으로 조회"가 모두 String 하나를 받지만, 생성자로는 구분이 안 됩니다. 정적 팩토리 메서드는 이 문제를 깔끔하게 해결합니다.

#### 장점 2: 호출할 때마다 인스턴스를 새로 생성하지 않아도 된다

생성자는 호출할 때마다 **반드시** 새 객체를 만듭니다. 이것은 생성자의 근본적인 제약입니다. 하지만 정적 팩토리 메서드는 메서드 내부에서 자유롭게 제어할 수 있으므로, 미리 만들어둔 인스턴스를 캐싱하여 재사용하거나, 특정 조건에서만 새 객체를 만들 수 있습니다.

```java
// Boolean.valueOf()의 실제 구현
public static Boolean valueOf(boolean b) {
    return b ? Boolean.TRUE : Boolean.FALSE;
    // Boolean.TRUE와 Boolean.FALSE는 미리 만들어둔 상수
    // new Boolean()을 절대 호출하지 않음 → 객체 생성 비용 제로
}
```

이 기법을 사용하면 같은 객체를 반복 요청해도 매번 새로 만들지 않으므로 **생성 비용이 큰 객체의 성능을 극적으로 개선**할 수 있습니다.

**인스턴스 통제(Instance-controlled) 클래스**: 이처럼 정적 팩토리 방식으로 인스턴스의 생성을 통제하는 클래스를 말합니다. 인스턴스를 통제하면:
- **싱글턴**(Item 3)을 만들 수 있음 — 항상 같은 인스턴스 반환
- **인스턴스화 불가**(Item 4)를 만들 수 있음 — 아예 인스턴스를 안 만듦
- **불변 값 클래스**(Item 17)에서 동치인 인스턴스가 하나뿐임을 보장 — `a == b`이면 `a.equals(b)`

비유하면: 생성자는 "주문할 때마다 요리를 새로 만드는 것"이고, 정적 팩토리는 "미리 만들어둔 메뉴에서 꺼내줄 수도 있고, 필요하면 새로 만들 수도 있는 것"입니다. 주방장(메서드)이 판단합니다.

**플라이웨이트(Flyweight) 패턴**이 이 기법을 활용한 대표적인 디자인 패턴입니다. Java의 `Integer.valueOf(int)`도 -128~127 범위는 캐싱합니다:

```java
Integer a = Integer.valueOf(127);
Integer b = Integer.valueOf(127);
System.out.println(a == b);  // true — 캐싱된 같은 객체

Integer c = Integer.valueOf(128);
Integer d = Integer.valueOf(128);
System.out.println(c == d);  // false — 캐시 범위 밖이므로 새 객체
```

#### 장점 3: 반환 타입의 하위 타입 객체를 반환할 수 있다

생성자는 해당 클래스의 인스턴스**만** 반환합니다. `new ArrayList()`를 호출하면 반드시 `ArrayList` 인스턴스가 만들어집니다. 다른 타입은 절대 반환할 수 없습니다.

하지만 정적 팩토리 메서드는 **반환 타입을 인터페이스나 상위 클래스로 선언**하고, 실제로는 그 하위 타입 객체를 반환할 수 있습니다. 이것이 API 설계에서 엄청난 유연성을 제공합니다.

```java
// List.of()는 List 인터페이스를 반환 타입으로 선언
// 하지만 내부적으로는 원소 수에 따라 최적의 구현체를 반환
List<String> list0 = List.of();           // ImmutableCollections.EMPTY_LIST
List<String> list1 = List.of("a");        // ImmutableCollections.List12
List<String> list2 = List.of("a", "b");   // ImmutableCollections.List12
List<String> listN = List.of("a","b","c"); // ImmutableCollections.ListN
```

**왜 이것이 중요한가?**

1. **구현체를 숨길 수 있다**: 호출하는 쪽은 `List` 인터페이스만 알면 됩니다. `ImmutableCollections.List12`같은 내부 클래스의 존재를 몰라도 됩니다. 이는 API 제공자가 **내부 구현을 자유롭게 바꿀 수 있다**는 의미입니다.

2. **API를 작게 유지할 수 있다**: `java.util.Collections` 클래스는 45개의 유틸리티 구현체를 제공하지만, 대부분이 정적 팩토리 메서드를 통해 반환됩니다. 45개의 public 클래스 대신 `Collections`라는 하나의 클래스에서 관리합니다. 프로그래머가 알아야 할 API의 크기가 줄어듭니다.

3. **다음 릴리스에서 구현체를 바꿔도 기존 코드에 영향이 없다**: Java 팀이 `List.of()`의 내부 구현을 더 빠른 구현체로 교체해도, `List.of()`를 호출하는 수억 줄의 코드는 한 줄도 수정할 필요가 없습니다.

Java 8 이전에는 인터페이스에 static 메서드를 선언할 수 없어서 `Collections`라는 동반 클래스(companion class)가 필요했습니다. Java 8부터 인터페이스에 static 메서드가 가능해지면서 `List.of()`, `Map.of()` 같은 인터페이스 직접 팩토리가 등장했습니다.

#### 장점 4: 입력 매개변수에 따라 매번 다른 클래스의 객체를 반환할 수 있다

장점 3의 확장입니다. 반환 타입의 하위 타입이기만 하면 매개변수에 따라 **매번 다른 클래스의 인스턴스를 반환**할 수 있습니다. 호출하는 쪽은 어떤 구현체가 반환되는지 전혀 신경 쓸 필요가 없습니다.

```java
// EnumSet.of()의 내부 구현 (OpenJDK)
public static <E extends Enum<E>> EnumSet<E> noneOf(Class<E> elementType) {
    Enum<?>[] universe = getUniverse(elementType);
    if (universe.length <= 64)
        return new RegularEnumSet<>(elementType, universe);
    else
        return new JumboEnumSet<>(elementType, universe);
}
```

- 원소가 64개 이하인 enum → `RegularEnumSet` 반환 (long 1개로 비트 연산, 매우 빠름)
- 원소가 64개 초과인 enum → `JumboEnumSet` 반환 (long 배열로 비트 연산)

호출하는 쪽은 `EnumSet`만 알면 됩니다. 내부적으로 어떤 클래스가 반환되는지 몰라도 되고, 알 필요도 없습니다. Java 팀이 다음 릴리스에서 `RegularEnumSet`을 삭제하거나 새로운 구현체를 추가해도, 기존 코드에는 영향이 없습니다.

이것이 **인터페이스 기반 프로그래밍**(Item 64)의 핵심입니다. "구현이 아닌 인터페이스에 프로그래밍하라"는 원칙이 정적 팩토리 메서드를 통해 자연스럽게 달성됩니다.

#### 단점 1: 상속하려면 public/protected 생성자가 필요하다

정적 팩토리만 제공하고 생성자를 private으로 하면 하위 클래스를 만들 수 없습니다. 예를 들어 `java.util.Collections`의 구현체들(UnmodifiableList, SynchronizedMap 등)은 직접 상속할 수 없습니다.

하지만 이것이 꼭 단점만은 아닙니다:
- **상속보다 컴포지션을 유도**하는 효과가 있습니다 (Item 18: 상속보다는 컴포지션을 사용하라)
- 불변 타입을 만들려면 오히려 이 제약이 필요합니다 (Item 17: 변경 가능성을 최소화하라)

상속의 위험성(상위 클래스 변경에 취약, 캡슐화 깨짐)을 생각하면, 이 "단점"은 오히려 좋은 설계로 가는 길잡이가 될 수 있습니다.

#### 단점 2: 프로그래머가 찾기 어렵다

생성자는 API 문서(Javadoc)에서 별도 섹션으로 명확히 드러납니다. 하지만 정적 팩토리 메서드는 다른 static 메서드와 섞여서 구분이 안 됩니다. 클래스의 인스턴스를 어떻게 얻는지를 사용자가 직접 찾아야 합니다.

이 문제를 완화하기 위해 **널리 알려진 네이밍 관례**를 따릅니다:

| 이름 | 의미 | 예시 |
|------|------|------|
| `from` | 매개변수 1개를 받아 **형변환** | `Date d = Date.from(instant)` |
| `of` | 매개변수 여러 개를 받아 **집계** | `Set<Color> s = EnumSet.of(RED, BLUE)` |
| `valueOf` | from/of의 더 자세한 버전 | `BigInteger bi = BigInteger.valueOf(100L)` |
| `getInstance` | 매개변수로 명시한 인스턴스 반환 (같은 인스턴스 보장 X) | `StackWalker sw = StackWalker.getInstance(option)` |
| `create` / `newInstance` | 매번 **새** 인스턴스 생성을 보장 | `Object arr = Array.newInstance(classObj, 10)` |
| `getType` | 팩토리가 **다른 클래스**에 있을 때. Type은 반환 타입 | `FileStore fs = Files.getFileStore(path)` |
| `newType` | 팩토리가 **다른 클래스**에 있을 때. 매번 새 인스턴스 | `BufferedReader br = Files.newBufferedReader(path)` |
| `type` | getType/newType의 간결한 버전 | `List<Complaint> list = Collections.list(legacy)` |

이 관례를 지키면 "이 메서드가 객체를 생성하는구나"라는 것을 이름만으로 알 수 있습니다. API를 설계할 때 반드시 이 관례를 따라야 합니다.

### 3. 코드 예제

**실무 시나리오: ERP 수주 DTO 생성**

```java
// Bad: 생성자만 제공 — 어떤 용도인지 불명확
public class OrderDto {
    public OrderDto(String orderId, String customerName, BigDecimal amount) { ... }
    public OrderDto(String orderId) { ... }  // 목록 조회용? 상세 조회용?
}

// 호출 코드
OrderDto dto1 = new OrderDto("ORD-001", "홍길동", new BigDecimal("10000"));
OrderDto dto2 = new OrderDto("ORD-001");  // 이게 뭐하는 건지 모름
```

```java
// Good: 정적 팩토리 메서드 — 용도가 명확
public class OrderDto {
    private final String orderId;
    private final String customerName;
    private final BigDecimal amount;

    // 생성자는 private — 외부에서 new 불가
    private OrderDto(String orderId, String customerName, BigDecimal amount) {
        this.orderId = orderId;
        this.customerName = customerName;
        this.amount = amount;
    }

    // 목록 조회용 (필요한 필드만)
    public static OrderDto forList(String orderId, String customerName) {
        return new OrderDto(orderId, customerName, null);
    }

    // 상세 조회용 (전체 필드)
    public static OrderDto forDetail(String orderId, String customerName, BigDecimal amount) {
        return new OrderDto(orderId, customerName, amount);
    }

    // Entity → DTO 변환 (from 관례)
    public static OrderDto from(Order entity) {
        return new OrderDto(
            entity.getId(),
            entity.getCustomer().getName(),
            entity.getAmount()
        );
    }
}

// 호출 코드 — 의도가 명확
OrderDto listDto = OrderDto.forList("ORD-001", "홍길동");
OrderDto detailDto = OrderDto.forDetail("ORD-001", "홍길동", BigDecimal.valueOf(10000));
OrderDto fromEntity = OrderDto.from(orderEntity);
```

**인스턴스 캐싱 예제**

```java
// 자주 사용되는 금액 단위를 캐싱하는 Money 클래스
public class Money {
    private static final Money ZERO = new Money(BigDecimal.ZERO, "KRW");

    private final BigDecimal amount;
    private final String currency;

    private Money(BigDecimal amount, String currency) {
        this.amount = amount;
        this.currency = currency;
    }

    // 캐싱된 인스턴스 반환 — 매번 new 하지 않음
    public static Money zero() {
        return ZERO;
    }

    // 새 인스턴스 생성이 필요한 경우
    public static Money of(BigDecimal amount, String currency) {
        if (amount.compareTo(BigDecimal.ZERO) == 0 && "KRW".equals(currency)) {
            return ZERO;  // 캐싱된 인스턴스 재사용
        }
        return new Money(amount, currency);
    }
}
```

### 4. 실무 연결

Spring에서 매일 쓰는 것들이 전부 정적 팩토리 패턴입니다:

```java
// Spring — ResponseEntity
ResponseEntity.ok(body)                           // 200 OK + 본문
ResponseEntity.notFound().build()                  // 404
ResponseEntity.status(HttpStatus.CREATED).body(result)  // 201 + 본문

// Java 표준 — Optional (null 처리의 표준)
Optional.of(value)          // null이면 NullPointerException
Optional.empty()            // 빈 Optional
Optional.ofNullable(value)  // null이면 empty, 아니면 of

// Java 표준 — 불변 컬렉션
List.of("a", "b", "c")                    // 불변 리스트
Map.of("key1", "val1", "key2", "val2")    // 불변 맵
Set.of(1, 2, 3)                           // 불변 셋
Collections.unmodifiableList(mutableList)  // 기존 리스트를 불변으로 래핑

// Java 표준 — 숫자 변환
BigDecimal.valueOf(10000)   // new BigDecimal(10000) 대신 — 캐싱 가능
Integer.valueOf(127)        // -128~127 캐싱
String.valueOf(123)         // int → String 변환
```

ERP에서의 활용:
```java
// Entity → DTO 변환에 from() 활용
OrderDto dto = OrderDto.from(orderEntity);

// 검색 조건 생성에 of() 활용
SearchCondition cond = SearchCondition.of(startDate, endDate, customerId);

// 상태 변환에 valueOf() 활용
OrderStatus status = OrderStatus.valueOf("CONFIRMED");
```

### 5. 오해하기 쉬운 부분

**오해 1**: "정적 팩토리 메서드를 쓰면 생성자를 아예 없애야 한다"
→ 사실은 둘 다 제공해도 됩니다. 다만 정적 팩토리만 제공하고 생성자를 private으로 감추는 것이 더 유연한 설계입니다. 어떤 방식이 적합한지는 상황에 따라 판단합니다.

**오해 2**: "정적 팩토리 메서드 = 팩토리 메서드 패턴(Factory Method Pattern)"
→ 이름은 비슷하지만 **완전히 다릅니다**. 디자인 패턴의 팩토리 메서드(Factory Method)는 **상속 기반**으로 하위 클래스에서 어떤 객체를 생성할지 결정하는 패턴이고, 여기서 말하는 정적 팩토리 메서드는 단순히 **static 메서드로 객체를 생성하는 기법**입니다. Effective Java의 정적 팩토리 메서드는 GoF 디자인 패턴에 대응하는 패턴이 없습니다.

**오해 3**: "항상 정적 팩토리가 생성자보다 좋다"
→ 매개변수가 1~2개이고 용도가 명확하면 생성자가 더 단순합니다. 정적 팩토리는 **"고려하라"**이지 **"항상 쓰라"**가 아닙니다. Effective Java의 Item 제목이 "고려하라(consider)"인 이유입니다.

**오해 4**: "정적 팩토리 메서드는 유틸리티 메서드와 같다"
→ 유틸리티 메서드(`Math.max()`, `Collections.sort()`)는 기존 객체에 대한 연산을 수행합니다. 정적 팩토리 메서드는 **새 인스턴스를 생성하여 반환**하는 것이 핵심입니다. 목적이 다릅니다.

### 6. 확인 질문

- [ ] 정적 팩토리 메서드의 장점 4가지를 각각 코드 예시와 함께 설명할 수 있는가?
- [ ] 단점 2가지를 말하고, 각 단점이 왜 치명적이지 않은지도 설명할 수 있는가?
- [ ] `of`, `from`, `valueOf`, `getInstance`, `create`, `newType`의 차이와 사용 시점을 구분할 수 있는가?
- [ ] 정적 팩토리 메서드와 GoF 팩토리 메서드 패턴의 차이를 설명할 수 있는가?
- [ ] `Integer.valueOf(127) == Integer.valueOf(127)`이 true인 이유를 장점 2로 설명할 수 있는가?
- [ ] Java 8 이전에 `Collections` 동반 클래스가 필요했던 이유를 장점 3으로 설명할 수 있는가?

---

## Item 2: 생성자에 매개변수가 많다면 빌더를 고려하라

### 1. 도입 (이것은 무엇이고, 왜 배우는가)

**빌더 패턴이란**: 매개변수가 많은 객체를 생성할 때, **별도의 Builder 객체에 값을 하나씩 설정한 뒤 `build()`로 최종 불변 객체를 만드는** 생성 패턴입니다.

```java
// 생성자: 각 숫자가 뭔지 모름
new NutritionFacts(240, 8, 100, 0, 35, 27);

// 빌더: 각 값이 뭔지 이름으로 명확
new NutritionFacts.Builder(240, 8)
    .calories(100)
    .sodium(35)
    .build();
```

ERP 시스템에서 수주, 거래처, 품목 같은 도메인 객체는 필드가 10개 이상인 경우가 흔합니다. 매개변수가 많은 객체를 생성할 때 "어떤 값이 어떤 필드에 들어가는지" 헷갈리는 경험이 있을 것입니다.

빌더 패턴은 이 문제를 해결합니다. Lombok `@Builder`를 쓰더라도 내부 원리를 알아야 커스터마이징이 가능하고, 면접에서 "빌더 패턴을 직접 구현해보세요"라는 질문에 답할 수 있습니다.

### 2. 핵심 개념

매개변수가 많은 객체를 생성하는 방법은 역사적으로 3가지가 있고, 순서대로 진화해왔습니다. 각 패턴의 **문제점**을 이해해야 빌더 패턴이 왜 최선인지 알 수 있습니다.

#### 패턴 1: 점층적 생성자 (Telescoping Constructor)

매개변수 조합마다 생성자를 하나씩 추가하는 방식입니다.

```java
public class NutritionFacts {
    private final int servingSize;   // 필수
    private final int servings;      // 필수
    private final int calories;      // 선택
    private final int fat;           // 선택
    private final int sodium;        // 선택
    private final int carbohydrate;  // 선택

    public NutritionFacts(int servingSize, int servings) {
        this(servingSize, servings, 0);
    }
    public NutritionFacts(int servingSize, int servings, int calories) {
        this(servingSize, servings, calories, 0);
    }
    public NutritionFacts(int servingSize, int servings, int calories, int fat) {
        this(servingSize, servings, calories, fat, 0);
    }
    public NutritionFacts(int servingSize, int servings, int calories,
                          int fat, int sodium) {
        this(servingSize, servings, calories, fat, sodium, 0);
    }
    public NutritionFacts(int servingSize, int servings, int calories,
                          int fat, int sodium, int carbohydrate) {
        this.servingSize  = servingSize;
        this.servings     = servings;
        this.calories     = calories;
        this.fat          = fat;
        this.sodium       = sodium;
        this.carbohydrate = carbohydrate;
    }
}
```

**문제점 1 — 읽기 어렵다**: 호출할 때 각 숫자가 무슨 의미인지 알 수 없습니다.

```java
// 240이 뭐고 8이 뭐고 100이 뭐고 0이 뭐지?
NutritionFacts nf = new NutritionFacts(240, 8, 100, 0, 35, 27);
```

**문제점 2 — 실수하기 쉽다**: 매개변수 순서를 바꿔도 컴파일러가 잡아주지 못합니다. `fat`과 `sodium`의 위치를 바꿔도 둘 다 `int`이므로 컴파일은 성공합니다. 런타임에서야 "나트륨이 왜 0이지?" 하고 발견합니다.

**문제점 3 — 확장이 어렵다**: 필드가 하나 추가될 때마다 생성자도 추가해야 합니다. 필드가 10개면 생성자가 10개 이상 필요합니다.

비유하면: 전화번호를 외우듯 매개변수 순서를 통째로 기억해야 합니다. 하나라도 순서가 바뀌면 버그인데, 컴파일러가 잡아주지 못합니다.

#### 패턴 2: 자바빈즈 (JavaBeans)

기본 생성자로 객체를 만들고, setter로 값을 하나씩 채웁니다.

```java
NutritionFacts nf = new NutritionFacts();
nf.setServingSize(240);
nf.setServings(8);
nf.setCalories(100);
nf.setSodium(35);
nf.setCarbohydrate(27);
```

점층적 생성자보다 읽기 좋아졌습니다. 각 값이 무슨 필드에 들어가는지 이름으로 알 수 있습니다. 하지만 **심각한 문제 2가지**가 있습니다:

**문제점 1 — 객체가 불완전한 상태로 존재할 수 있다**: `new NutritionFacts()` 시점에 객체는 만들어졌지만 필수 필드(servingSize, servings)가 설정되지 않은 상태입니다. setter를 빠뜨려도 컴파일 에러가 안 납니다. 이 불완전한 객체가 다른 메서드에 전달되면 런타임 에러가 터집니다.

비유하면: 자동차 공장에서 엔진도 안 달린 자동차 프레임을 출고한 뒤, "나중에 바퀴랑 엔진을 달아주세요"라고 하는 것입니다. 출고된 불완전한 자동차가 도로에 나가면 사고가 납니다.

**문제점 2 — 불변 객체를 만들 수 없다**: setter가 있으므로 객체 생성 후에도 누구든 값을 바꿀 수 있습니다. 즉 `final` 필드를 쓸 수 없습니다. 멀티스레드 환경에서 한 스레드가 setter로 값을 바꾸는 중에 다른 스레드가 읽으면 중간 상태(inconsistent state)를 볼 수 있습니다.

#### 패턴 3: 빌더 (Builder) — 최종 해결

점층적 생성자의 **안전성**(필수 매개변수 강제 + 불변)과 자바빈즈의 **가독성**(이름 있는 매개변수)을 모두 취한 패턴입니다.

동작 원리:
1. 필수 매개변수만으로 **Builder 객체**를 생성
2. Builder의 setter 메서드로 선택 매개변수를 설정 (각 setter가 Builder 자신을 반환 → **메서드 체이닝**)
3. `build()` 메서드가 **불변 객체**를 생성하여 반환

```java
NutritionFacts nf = new NutritionFacts.Builder(240, 8)  // 1. 필수 매개변수
    .calories(100)      // 2. 선택 매개변수 (체이닝)
    .sodium(35)         // 2. 선택 매개변수 (체이닝)
    .carbohydrate(27)   // 2. 선택 매개변수 (체이닝)
    .build();           // 3. 불변 객체 생성
```

**빌더 패턴이 해결하는 것**:
- **가독성**: 각 매개변수가 무엇인지 이름으로 명확 (자바빈즈의 장점)
- **안전성**: 필수 매개변수를 Builder 생성자에서 강제 (점층적 생성자의 장점)
- **불변성**: `build()` 시점에 `final` 필드를 가진 불변 객체가 만들어짐 → 스레드 안전
- **유연성**: 순서가 자유로움 → `sodium`을 먼저 넣어도 됨
- **검증**: `build()` 안에서 매개변수 유효성 검사 가능 (calories < 0이면 예외 등)

### 3. 코드 예제

**빌더 패턴 직접 구현 (전체 코드)**

```java
public class NutritionFacts {
    private final int servingSize;   // 필수
    private final int servings;      // 필수
    private final int calories;      // 선택 (기본값 0)
    private final int fat;           // 선택 (기본값 0)
    private final int sodium;        // 선택 (기본값 0)

    public static class Builder {
        // === 필수 매개변수 ===
        private final int servingSize;
        private final int servings;

        // === 선택 매개변수 — 기본값으로 초기화 ===
        private int calories = 0;
        private int fat = 0;
        private int sodium = 0;

        // 필수 매개변수만 받는 생성자
        public Builder(int servingSize, int servings) {
            this.servingSize = servingSize;
            this.servings = servings;
        }

        // 선택 매개변수 setter
        // 핵심: this(Builder 자신)를 반환 → .calories().fat().build() 체이닝 가능
        public Builder calories(int val) {
            calories = val;
            return this;
        }
        public Builder fat(int val) {
            fat = val;
            return this;
        }
        public Builder sodium(int val) {
            sodium = val;
            return this;
        }

        // 불변 객체 생성
        public NutritionFacts build() {
            // 여기서 유효성 검사 가능
            if (calories < 0) throw new IllegalArgumentException("calories < 0");
            return new NutritionFacts(this);
        }
    }

    // private 생성자 — Builder를 통해서만 생성 가능
    // 외부에서 new NutritionFacts(...) 불가
    private NutritionFacts(Builder builder) {
        servingSize = builder.servingSize;  // final 필드에 값 설정
        servings    = builder.servings;
        calories    = builder.calories;
        fat         = builder.fat;
        sodium      = builder.sodium;
    }
}
```

메서드 체이닝이 동작하는 원리를 자세히 보면:

```java
new NutritionFacts.Builder(240, 8)   // Builder 객체 생성
    .calories(100)                    // Builder 객체 반환 (return this)
    .sodium(35)                       // Builder 객체 반환 (return this)
    .build();                         // NutritionFacts 객체 반환

// 위 코드를 풀어쓰면:
Builder builder = new NutritionFacts.Builder(240, 8);
builder = builder.calories(100);  // 같은 builder 객체 (this)
builder = builder.sodium(35);     // 같은 builder 객체 (this)
NutritionFacts nf = builder.build();  // 최종 불변 객체
```

**Lombok @Builder 사용**

```java
@Builder
public class OrderDto {
    private final String orderId;
    private final String customerName;
    private final BigDecimal amount;
    private final LocalDate orderDate;
}

// 사용
OrderDto dto = OrderDto.builder()
    .orderId("ORD-001")
    .customerName("홍길동")
    .amount(BigDecimal.valueOf(10000))
    .orderDate(LocalDate.now())
    .build();
```

Lombok이 위의 전체 Builder 코드를 컴파일 시점에 자동 생성합니다. 하지만 **Lombok의 한계**가 있습니다:

```java
// Lombok @Builder는 모든 필드를 선택적으로 만듦
// 필수 필드(orderId)를 빠뜨려도 컴파일 에러가 안 남!
OrderDto broken = OrderDto.builder()
    .customerName("홍길동")  // orderId 빠짐 → null로 들어감
    .build();
```

필수값 검증이 필요하면 `build()` 메서드를 직접 오버라이드하거나, 빌더를 직접 구현해야 합니다.

### 4. 실무 연결

```java
// Spring — URI 빌더
URI uri = UriComponentsBuilder.fromPath("/api/orders")
    .queryParam("status", "confirmed")
    .queryParam("page", 1)
    .build()
    .toUri();

// Spring Security — 보안 설정
http.authorizeHttpRequests(auth -> auth
    .requestMatchers("/api/public/**").permitAll()
    .anyRequest().authenticated()
);

// ERP 실무 — 검색 조건 DTO
OrderSearchCondition condition = OrderSearchCondition.builder()
    .customerId("CUST-001")
    .fromDate(LocalDate.of(2026, 1, 1))
    .toDate(LocalDate.of(2026, 12, 31))
    .status(OrderStatus.CONFIRMED)
    .build();

// Java 표준 — Stream API도 빌더와 유사한 체이닝
List<String> result = orders.stream()
    .filter(o -> o.getAmount().compareTo(BigDecimal.ZERO) > 0)
    .map(Order::getCustomerName)
    .distinct()
    .collect(Collectors.toList());
```

### 5. 오해하기 쉬운 부분

**오해 1**: "Lombok @Builder를 쓰면 빌더 패턴을 알 필요 없다"
→ Lombok @Builder는 **모든 필드를 선택적**으로 만듭니다. 필수 매개변수를 강제할 수 없습니다. 필수값 검증이 필요하면 직접 빌더를 구현하거나, `@Builder` + 커스텀 `build()` 메서드를 조합해야 합니다. 원리를 모르면 커스터마이징이 불가능합니다.

**오해 2**: "매개변수가 2~3개여도 빌더를 써야 한다"
→ 매개변수가 적고 용도가 명확하면 생성자나 정적 팩토리가 더 단순합니다. 빌더는 **매개변수가 4개 이상이거나, 선택적 매개변수가 많을 때, 또는 같은 타입의 매개변수가 여러 개일 때** 고려합니다. 과한 빌더 사용은 오히려 복잡성만 증가시킵니다.

**오해 3**: "빌더 패턴은 성능이 나쁘다"
→ Builder 객체 생성 비용이 있지만, 대부분의 상황에서 무시할 수 있는 수준입니다. 성능 민감한 코드(초당 수백만 호출)에서만 고려하면 됩니다. 가독성과 안전성이 미미한 성능 비용보다 훨씬 중요합니다.

**오해 4**: "빌더의 setter도 자바빈즈의 setter와 같은 것 아닌가?"
→ 결정적 차이가 있습니다. 자바빈즈의 setter는 **이미 완성된 객체를 변경**하므로 불변을 깨뜨립니다. 빌더의 setter는 **아직 완성되지 않은 Builder 객체를 설정**하고, `build()` 시점에 불변 객체를 만듭니다. Builder는 임시 객체이고, 최종 결과물(NutritionFacts)은 불변입니다.

### 6. 확인 질문

- [ ] 점층적 생성자 패턴의 문제점 3가지를 설명할 수 있는가?
- [ ] 자바빈즈 패턴의 문제점 2가지(불완전 상태, 불변 불가)를 설명할 수 있는가?
- [ ] 빌더 패턴의 동작 원리(Builder 생성 → 체이닝 → build())를 코드로 작성할 수 있는가?
- [ ] 메서드 체이닝이 동작하는 이유(`return this`)를 설명할 수 있는가?
- [ ] Lombok @Builder의 한계(필수 매개변수 강제 불가)를 설명할 수 있는가?
- [ ] "빌더의 setter와 자바빈즈의 setter는 같다"는 주장에 반박할 수 있는가?

---

## Item 3: private 생성자나 열거 타입으로 싱글턴임을 보증하라

### 1. 도입 (이것은 무엇이고, 왜 배우는가)

**싱글턴(Singleton)이란**: 애플리케이션 전체에서 **인스턴스가 오직 1개만 존재하도록 보장**하는 클래스입니다. 설정 객체, 커넥션 풀, 캐시 매니저처럼 "하나만 있어야 하는 것"에 사용합니다.

```java
// 어디서 호출해도 같은 인스턴스
Elvis a = Elvis.INSTANCE;
Elvis b = Elvis.INSTANCE;
System.out.println(a == b);  // true — 같은 객체
```

면접에서 "싱글턴 구현 방법 3가지를 말해보세요"는 단골 질문입니다. Spring Bean이 기본 Singleton 스코프이므로, Spring이 내부적으로 싱글턴을 어떻게 보장하는지 이해하는 출발점이기도 합니다.

직접 싱글턴을 구현할 일은 드물지만, **왜 enum이 가장 안전한지**, **리플렉션과 직렬화에서 왜 깨지는지**를 이해해야 Spring의 빈 관리와 테스트 전략을 이해할 수 있습니다.

### 2. 핵심 개념

#### 방식 1: public static final 필드

```java
public class Elvis {
    public static final Elvis INSTANCE = new Elvis();

    private Elvis() { }  // private → 외부에서 new 불가

    public void leaveTheBuilding() { ... }
}

// 사용
Elvis elvis = Elvis.INSTANCE;
```

**동작 원리**: `private Elvis()` 생성자는 `public static final Elvis INSTANCE`를 초기화할 때 딱 한 번만 호출됩니다. public이나 protected 생성자가 없으므로 Elvis 인스턴스가 전체 시스템에서 하나뿐임이 보장됩니다.

**장점**: `public static final` 필드로 선언되어 있으므로 이 클래스가 싱글턴임이 **API에 명확히 드러납니다**. 간결합니다.

**취약점 — 리플렉션 공격**: Java의 리플렉션 API를 사용하면 private 생성자에 접근할 수 있습니다. `setAccessible(true)`로 접근 제한을 무력화하면 두 번째 인스턴스를 만들 수 있습니다.

```java
// 리플렉션으로 private 생성자를 강제 호출
Constructor<Elvis> constructor = Elvis.class.getDeclaredConstructor();
constructor.setAccessible(true);  // private 접근 제한 무시
Elvis evil = constructor.newInstance();  // 두 번째 인스턴스 생성!
System.out.println(Elvis.INSTANCE == evil);  // false — 싱글턴 깨짐
```

방어하려면 생성자에서 두 번째 호출을 감지하여 예외를 던져야 합니다:
```java
private Elvis() {
    if (INSTANCE != null) {
        throw new IllegalStateException("이미 인스턴스가 존재합니다");
    }
}
```

#### 방식 2: 정적 팩토리

```java
public class Elvis {
    private static final Elvis INSTANCE = new Elvis();

    private Elvis() { }

    public static Elvis getInstance() { return INSTANCE; }

    public void leaveTheBuilding() { ... }
}

// 사용
Elvis elvis = Elvis.getInstance();
```

**장점 1**: API를 바꾸지 않고도 내부 동작을 변경할 수 있습니다. 예를 들어 나중에 스레드별 다른 인스턴스를 반환하도록 바꿔도 호출 코드(`Elvis.getInstance()`)는 수정 불필요합니다.

**장점 2**: 메서드 참조를 supplier로 사용할 수 있습니다: `Elvis::getInstance`를 `Supplier<Elvis>`로 넘길 수 있습니다.

**취약점 1 — 리플렉션**: 방식 1과 동일.

**취약점 2 — 직렬화**: 싱글턴 클래스를 `Serializable`로 만들면, **역직렬화할 때마다 새 인스턴스가 생성**됩니다. 직렬화된 바이트를 읽어 객체를 복원하는 과정에서 생성자를 거치지 않고 새 객체가 만들어지기 때문입니다.

```java
// 직렬화
ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream("elvis.ser"));
out.writeObject(Elvis.getInstance());

// 역직렬화 → 새 인스턴스 생성!
ObjectInputStream in = new ObjectInputStream(new FileInputStream("elvis.ser"));
Elvis deserialized = (Elvis) in.readObject();
System.out.println(Elvis.getInstance() == deserialized);  // false — 싱글턴 깨짐!
```

해결하려면 `readResolve` 메서드를 추가해야 합니다:
```java
// 역직렬화 시 이 메서드가 호출됨
// 새로 만들어진 가짜 인스턴스 대신 기존 INSTANCE를 반환
private Object readResolve() {
    return INSTANCE;  // 가짜 Elvis는 가비지 컬렉터에 맡김
}
```

그리고 모든 인스턴스 필드를 `transient`로 선언해야 합니다. 그렇지 않으면 `readResolve`가 호출되기 전에 역직렬화된 객체의 참조를 빼돌릴 수 있는 정교한 공격이 가능합니다.

#### 방식 3: enum (권장)

```java
public enum Elvis {
    INSTANCE;

    public void leaveTheBuilding() { ... }
}

// 사용
Elvis elvis = Elvis.INSTANCE;
```

**왜 가장 안전한가?**

1. **직렬화 자동 보장**: enum의 직렬화/역직렬화는 JVM이 특별히 처리합니다. enum 상수는 이름으로 직렬화되고, 역직렬화 시 `Enum.valueOf()`로 기존 상수를 반환합니다. `readResolve`가 필요 없고, 추가 코드 없이 직렬화 안전이 보장됩니다.

2. **리플렉션 방어 자동**: JVM은 enum 생성자의 리플렉션 호출을 명시적으로 차단합니다. `Constructor.newInstance()`를 호출하면 `IllegalArgumentException: Cannot reflectively create enum objects`가 발생합니다. 별도 방어 코드가 필요 없습니다.

3. **코드가 간결**: 방식 1, 2에 필요한 방어 코드(리플렉션 차단, readResolve, transient)가 전부 불필요합니다.

**단점**: enum은 `Enum` 클래스를 이미 상속하고 있으므로 **다른 클래스를 상속할 수 없습니다**. 인터페이스 구현은 가능합니다. 상속이 필요한 싱글턴이라면 방식 1 또는 2를 써야 합니다.

#### 트레이드오프 정리

| 방식 | 직렬화 안전 | 리플렉션 방어 | 상속 가능 | 코드 간결 |
|------|:---------:|:-----------:|:--------:|:--------:|
| public 필드 | X (readResolve 필요) | X (방어 코드 필요) | O | O |
| 정적 팩토리 | X (readResolve 필요) | X (방어 코드 필요) | O | O |
| enum | O (자동) | O (자동) | X (Enum 상속) | O |

**결론**: 대부분의 상황에서 **enum 방식이 가장 좋습니다**. 상속이 필요한 드문 경우에만 방식 1, 2를 고려합니다.

### 3. 코드 예제

**실무에서의 싱글턴: Spring Bean**

```java
// 실무에서는 직접 싱글턴을 구현하지 않음
// Spring 컨테이너가 @Component 클래스를 Singleton으로 관리
@Service
public class OrderService {
    // Spring이 인스턴스를 1개만 생성하고 모든 곳에 같은 인스턴스를 주입
    // 하지만 Spring의 싱글턴은 enum이 아니라 HashMap에 빈을 캐싱하는 방식
}
```

직접 싱글턴을 구현해야 하는 드문 경우 (Spring 없는 환경):
```java
// 추천: enum 방식
public enum AppConfig {
    INSTANCE;

    private final String dbUrl;
    private final int maxConnections;

    AppConfig() {
        // 생성 시 설정 파일에서 읽기
        Properties props = loadProperties("config.properties");
        this.dbUrl = props.getProperty("db.url");
        this.maxConnections = Integer.parseInt(props.getProperty("db.maxConnections"));
    }

    public String getDbUrl() { return dbUrl; }
    public int getMaxConnections() { return maxConnections; }

    private Properties loadProperties(String filename) {
        // 파일에서 Properties 로드하는 로직
        ...
    }
}

// 사용
String url = AppConfig.INSTANCE.getDbUrl();
```

### 4. 실무 연결

- **Spring Bean**: 기본이 Singleton 스코프. `@Component`, `@Service`, `@Repository`로 등록하면 컨테이너가 싱글턴을 보장합니다. Spring은 enum이 아니라 **ApplicationContext 내부의 HashMap**에 빈 인스턴스를 캐싱합니다.

- **Singleton 빈의 상태 주의**: 싱글턴 빈에 인스턴스 변수(상태)를 두면 멀티스레드 환경에서 race condition이 발생합니다. 요청 A가 값을 쓰는 중에 요청 B가 읽으면 엉뚱한 값을 봅니다. **Singleton 빈은 무상태(Stateless)로 설계**해야 합니다. (Spring 학습 Step 6에서 상세)

- `Runtime.getRuntime()`: JVM 런타임 정보를 제공하는 싱글턴입니다.
- `Desktop.getDesktop()`: 데스크톱 환경 접근을 위한 싱글턴입니다.

### 5. 오해하기 쉬운 부분

**오해 1**: "싱글턴은 항상 좋은 패턴이다"
→ 싱글턴은 **전역 상태**를 만들어서 **테스트를 어렵게** 만듭니다. 싱글턴 클래스를 직접 참조하면 Mock으로 교체할 수 없습니다. 이것이 Spring이 DI(의존 객체 주입)를 사용하는 이유 중 하나입니다. Spring의 빈은 싱글턴이지만 **인터페이스 기반**이라 테스트 시 Mock으로 교체할 수 있습니다. 순수 싱글턴 패턴은 이것이 불가능합니다.

**오해 2**: "enum 싱글턴은 메서드를 가질 수 없다"
→ enum도 필드, 메서드, 인터페이스 구현이 모두 가능합니다. 다만 클래스 상속은 불가능합니다.

**오해 3**: "싱글턴은 멀티스레드에서 안전하다"
→ 싱글턴 **생성**은 안전합니다(JVM이 클래스 로딩 시점에 보장). 하지만 싱글턴 내부의 **상태(가변 필드)**는 안전하지 않습니다. 여러 스레드가 동시에 같은 인스턴스의 필드를 읽고 쓰면 race condition이 발생합니다.

### 6. 확인 질문

- [ ] 싱글턴 구현 3가지 방식을 코드로 작성할 수 있는가?
- [ ] enum 싱글턴이 가장 안전한 이유 2가지(직렬화, 리플렉션)를 각각 상세히 설명할 수 있는가?
- [ ] 리플렉션으로 private 생성자를 뚫는 공격 코드를 설명할 수 있는가?
- [ ] 직렬화/역직렬화 시 싱글턴이 깨지는 이유와 readResolve의 역할을 설명할 수 있는가?
- [ ] 싱글턴이 테스트를 어렵게 만드는 이유와 Spring DI가 이를 해결하는 방법을 설명할 수 있는가?

---

## Item 5: 자원을 직접 명시하지 말고 의존 객체 주입을 사용하라

### 1. 도입 (이것은 무엇이고, 왜 배우는가)

**의존 객체 주입(Dependency Injection)이란**: 클래스가 사용하는 의존 객체를 **내부에서 직접 생성(`new`)하지 않고, 외부에서 생성자를 통해 전달받는** 설계 기법입니다.

```java
// Bad: 내부에서 직접 생성 — 교체 불가, 테스트 불가
private final Lexicon dictionary = new KoreanDictionary();

// Good: 외부에서 주입 — 교체 가능, 테스트 가능
public SpellChecker(Lexicon dictionary) {
    this.dictionary = dictionary;
}
```

이 아이템은 **Spring DI의 이론적 근거**입니다. "왜 `new`로 직접 만들면 안 되는가?", "왜 Spring이 객체를 대신 생성해서 주입하는가?"에 대한 원칙적 답변이 여기 있습니다.

면접에서 "DI란 무엇이고 왜 필요한가?"라고 물었을 때, 이 아이템의 내용으로 답변하면 원리를 이해하고 있다는 인상을 줄 수 있습니다.

### 2. 핵심 개념

많은 클래스가 하나 이상의 자원(다른 객체)에 의존합니다. 예를 들어 맞춤법 검사기(SpellChecker)는 사전(Lexicon)에 의존합니다. 이 의존 관계를 코드로 어떻게 표현하느냐가 설계의 유연성을 결정합니다.

#### Bad 1: 정적 유틸리티 클래스로 구현

```java
public class SpellChecker {
    private static final Lexicon dictionary = new KoreanDictionary();  // 고정!

    private SpellChecker() { }  // 인스턴스화 방지

    public static boolean isValid(String word) {
        return dictionary.contains(word);
    }

    public static List<String> suggestions(String typo) {
        return dictionary.getSuggestions(typo);
    }
}
```

#### Bad 2: 싱글턴으로 구현

```java
public class SpellChecker {
    private final Lexicon dictionary = new KoreanDictionary();  // 여전히 고정!

    public static SpellChecker INSTANCE = new SpellChecker();
    private SpellChecker() { }

    public boolean isValid(String word) {
        return dictionary.contains(word);
    }
}
```

두 방식 모두 **사전을 단 하나만 사용한다고 가정**합니다. 하지만 현실에서는:
- 한국어 사전, 영어 사전, 일본어 사전이 각각 필요할 수 있음
- 테스트 시 가벼운 테스트용 사전을 쓰고 싶음
- 특수 사전(의학 용어, 법률 용어)이 추가될 수 있음

`KoreanDictionary`가 하드코딩되어 있으므로 **코드를 수정하지 않고는 다른 사전으로 교체할 수 없습니다**. 이것이 핵심 문제입니다.

"그러면 setter로 사전을 바꿀 수 있게 하면 되지 않나?" → `dictionary` 필드를 final이 아니게 만들고 setter를 제공하면 멀티스레드 환경에서 불안전해집니다. 한 스레드가 사전을 바꾸는 중에 다른 스레드가 검사를 하면 엉뚱한 결과가 나올 수 있습니다.

#### Good: 의존 객체 주입 (생성자 주입)

```java
public class SpellChecker {
    private final Lexicon dictionary;  // 인터페이스에 의존, final로 불변

    // 생성자에서 외부로부터 주입받음
    public SpellChecker(Lexicon dictionary) {
        this.dictionary = Objects.requireNonNull(dictionary);
    }

    public boolean isValid(String word) {
        return dictionary.contains(word);
    }

    public List<String> suggestions(String typo) {
        return dictionary.getSuggestions(typo);
    }
}
```

이제 사용하는 쪽에서 원하는 구현체를 자유롭게 주입할 수 있습니다:

```java
// 프로덕션: 한국어 사전
SpellChecker korean = new SpellChecker(new KoreanDictionary());

// 프로덕션: 영어 사전
SpellChecker english = new SpellChecker(new EnglishDictionary());

// 테스트: Mock 사전 — 특정 단어만 유효하게 설정
Lexicon mockDict = mock(Lexicon.class);
when(mockDict.contains("hello")).thenReturn(true);
SpellChecker testChecker = new SpellChecker(mockDict);
```

**핵심 원리 정리**:
1. 클래스가 의존하는 자원을 **직접 만들지 않는다** (`new` 금지)
2. 의존 자원을 **인터페이스 타입**으로 선언한다 (구현체가 아닌 추상에 의존)
3. 의존 자원을 **생성자 매개변수로 전달받는다** (외부에서 주입)
4. 주입받은 필드를 **final로 선언**하여 불변성을 보장한다

이 패턴은 **생성자, 정적 팩토리(Item 1), 빌더(Item 2)** 모두에 동일하게 적용됩니다.

#### 변형: 팩토리를 주입받는 패턴

자원 자체가 아니라 **자원을 생성하는 팩토리**를 주입받는 변형도 유용합니다. Java 8의 `Supplier<T>` 인터페이스가 이 패턴에 적합합니다.

```java
// 타일을 생성하는 팩토리를 주입받음
Mosaic create(Supplier<? extends Tile> tileFactory) {
    // tileFactory.get()을 호출할 때마다 새 Tile을 생성
}
```

이것이 바로 **Spring의 핵심 동작 원리**입니다:

```java
@Service
public class OrderService {
    private final OrderRepository orderRepository;

    // Spring 컨테이너가 OrderRepository 구현체(JpaOrderRepository)를 자동으로 주입
    public OrderService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }
}
```

Spring은 `new OrderService(new JpaOrderRepository(entityManager))`를 개발자 대신 해줍니다. 어떤 구현체를 주입할지는 설정(`@Component` 스캔, `@Bean` 정의)으로 결정합니다.

비유하면: 레스토랑(SpellChecker)이 식재료(Dictionary)를 직접 농사짓는(new) 대신, 공급업체(Spring 컨테이너)로부터 배달받는(주입) 것입니다. 공급업체만 바꾸면 식재료가 바뀌지만 레스토랑 운영 방식(코드)은 그대로입니다.

### 3. 코드 예제

**ERP 실무 예시**

```java
// Bad: 직접 명시 — DAO를 교체하거나 테스트 불가
@Service
public class OrderService {
    private final OrderDao dao = new OracleOrderDao();  // Oracle에 고정!

    public Order findOrder(String id) {
        return dao.findById(id);
    }
}
// 문제: DB를 MySQL로 바꾸면 이 코드를 수정해야 함
// 문제: 테스트에서 실제 Oracle 없이 테스트 불가
```

```java
// Good: 의존 객체 주입 — DAO 교체 가능, 테스트 가능
@Service
public class OrderService {
    private final OrderDao dao;

    public OrderService(OrderDao dao) {  // 인터페이스로 주입
        this.dao = dao;
    }

    public Order findOrder(String id) {
        return dao.findById(id);
    }
}

// 프로덕션: Spring이 OracleOrderDao를 주입
// 테스트: MockOrderDao를 직접 주입
// DB 변경: MySqlOrderDao 빈을 등록하면 OrderService 코드 변경 없음
```

### 4. 실무 연결

- **Spring `@Autowired` 생성자 주입**: 이 아이템의 패턴 그 자체. 생성자가 1개면 `@Autowired` 생략 가능
- **Spring Boot 테스트에서 `@MockBean`**: DI 덕분에 특정 빈을 Mock으로 교체할 수 있음
- **Repository 인터페이스를 쓰는 이유**: 구현체(JPA, MyBatis, JDBC)를 교체해도 Service 코드가 안 바뀜
- **OCP(개방-폐쇄 원칙)**: 확장(새 구현체 추가)에는 열려 있고, 수정(기존 코드 변경)에는 닫혀 있음

### 5. 오해하기 쉬운 부분

**오해 1**: "DI는 Spring에서만 쓰는 개념이다"
→ DI는 **설계 원칙**이고, Spring은 그것을 편리하게 해주는 **프레임워크**입니다. Spring 없이도 생성자로 객체를 넘기면 DI입니다. Spring이 하는 일은 "어떤 구현체를 주입할지"를 설정으로 관리하고, 객체 생성을 자동화하는 것입니다.

**오해 2**: "의존 객체 주입은 생성자 주입만 가능하다"
→ 필드 주입(`@Autowired` 필드), 세터 주입(setter 메서드)도 가능합니다. 하지만 **생성자 주입이 권장**됩니다:
- `final` 필드 → 불변 보장
- 필수 의존성 누락 시 **컴파일 에러** (필드/세터 주입은 런타임에야 발견)
- 테스트 시 **new로 직접 주입 가능** (필드 주입은 리플렉션 필요)
- 순환 참조를 **조기 감지** (애플리케이션 기동 시 실패)

**오해 3**: "DI를 쓰면 코드가 복잡해진다"
→ 클래스 하나만 보면 생성자 매개변수가 늘어나서 복잡해 보일 수 있습니다. 하지만 **시스템 전체**로 보면 결합도가 낮아져서 변경/테스트/확장이 쉬워집니다. 초기 비용은 있지만 장기적 이득이 압도적입니다.

### 6. 확인 질문

- [ ] 자원을 직접 명시하면(`new`로 생성) 발생하는 문제 2가지(유연성, 테스트)를 설명할 수 있는가?
- [ ] "setter로 교체하면 되지 않나?"에 대해 왜 안 되는지(멀티스레드 불안전, 불변 깨짐) 설명할 수 있는가?
- [ ] 의존 객체 주입의 핵심 원리 4가지(직접 생성 금지, 인터페이스 의존, 생성자 주입, final 불변)를 설명할 수 있는가?
- [ ] 이 아이템과 Spring DI의 관계를 설명할 수 있는가?
- [ ] 생성자 주입이 필드 주입보다 권장되는 이유 4가지를 설명할 수 있는가?
- [ ] `Supplier<T>`를 팩토리로 주입하는 변형 패턴을 설명할 수 있는가?

---

## Item 7: 다 쓴 객체 참조를 해제하라

### 1. 도입 (이것은 무엇이고, 왜 배우는가)

**"다 쓴 객체 참조 해제"란**: 더 이상 사용하지 않는 객체에 대한 참조를 `null`로 설정하거나 자료구조에서 제거하여, **GC(Garbage Collector)가 해당 객체의 메모리를 수거할 수 있게 만드는** 것입니다.

```java
// 배열에서 꺼냈지만 참조가 남아있는 상태 → GC가 수거 못 함 → 누수
Object result = elements[--size];

// 참조를 해제하면 → GC가 수거 가능
Object result = elements[--size];
elements[size] = null;  // 참조 해제
```

"Java는 GC가 알아서 메모리를 관리해주니까 메모리 누수가 없다"고 생각하기 쉽지만, **틀렸습니다**. GC는 **참조가 남아있는 객체는 수거하지 않습니다**. 프로그래머가 참조를 유지하는 한 GC도 어쩔 수 없습니다.

ERP 같은 장시간 운영 시스템에서 메모리 누수가 조금씩 쌓이면, 며칠 후에 갑자기 OOM(OutOfMemoryError)이 터집니다. 면접에서 "Java에서 메모리 누수가 발생하는 경우를 말해보세요"는 시니어 단골 질문입니다.

### 2. 핵심 개념

GC의 동작 원리부터 이해해야 합니다. GC는 **도달 가능성(reachability)**으로 수거 여부를 판단합니다. GC Root(스택 변수, static 변수, JNI 참조 등)에서 참조 체인을 따라갈 수 있는 객체는 "살아있다"고 판단하고, 따라갈 수 없는 객체만 "쓰레기"로 수거합니다.

문제는 **프로그래머의 의도와 GC의 판단이 다를 때** 발생합니다. 프로그래머는 "이 객체는 더 이상 안 쓴다"고 생각하지만, 코드 어딘가에 참조가 남아있으면 GC는 "아직 쓰고 있다"고 판단합니다. 이것이 Java에서의 메모리 누수입니다.

#### 누수 상황 1: 자기 메모리를 직접 관리하는 클래스

가장 대표적인 예가 **Stack**입니다. Stack은 내부에 `Object[]` 배열을 가지고, `size` 변수로 "활성 영역"과 "비활성 영역"을 구분합니다.

```java
public class Stack {
    private Object[] elements;
    private int size = 0;
    private static final int DEFAULT_INITIAL_CAPACITY = 16;

    public Stack() {
        elements = new Object[DEFAULT_INITIAL_CAPACITY];
    }

    public void push(Object e) {
        ensureCapacity();
        elements[size++] = e;
    }

    // 메모리 누수가 있는 pop()
    public Object pop() {
        if (size == 0) throw new EmptyStackException();
        return elements[--size];
        // size는 줄었지만 elements[size]에 여전히 객체 참조가 남아있음!
        // 이 참조는 Stack이 GC Root에서 도달 가능하므로 GC가 수거 못 함
    }
}
```

구체적으로 무슨 일이 벌어지는지 봅시다:

```
push(A), push(B), push(C) 후:
elements = [A, B, C, null, null, ...]
size = 3

pop() 호출 후:  (C를 꺼냄)
elements = [A, B, C, null, null, ...]  ← C 참조가 여전히 남아있음!
size = 2

프로그래머의 의도: elements[2]는 비활성 영역 → C는 더 이상 안 씀
GC의 판단: Stack → elements 배열 → C 로 참조 체인이 있음 → C는 살아있음
결과: C 객체가 GC 대상이 아님 → 메모리 누수
```

이 Stack을 오래 쓰면 pop된 객체들이 전부 메모리에 남아서, 결국 OOM이 발생합니다. 더 심각한 것은, pop된 객체가 참조하는 **다른 모든 객체들도** 함께 GC 대상에서 제외된다는 점입니다. 하나의 참조가 대량의 객체를 GC에서 차단할 수 있습니다.

**해결**: 다 쓴 참조를 null로 해제

```java
public Object pop() {
    if (size == 0) throw new EmptyStackException();
    Object result = elements[--size];
    elements[size] = null;  // 다 쓴 참조 해제 → GC가 수거 가능
    return result;
}
```

`null`을 대입하면 elements[2] → C의 참조 체인이 끊기므로, C가 다른 곳에서도 참조되지 않는다면 GC 수거 대상이 됩니다.

**추가 이점**: null로 해제한 참조를 실수로 사용하면 `NullPointerException`이 발생합니다. 프로그램이 잘못된 일을 하는 것보다 **빨리 실패하는 것**이 훨씬 낫습니다.

**그렇다면 모든 변수를 null로 해제해야 하는가?** → 아닙니다. 일반적인 지역 변수는 메서드가 끝나면 스택 프레임과 함께 자동으로 사라지므로 null 해제가 필요 없습니다. null 해제는 **예외적인 경우**에만 필요합니다. 그 예외가 바로 **"자기 메모리를 직접 관리하는 클래스"**입니다.

비유하면: 호텔 체크아웃 후에도 방 열쇠를 반납하지 않으면, 호텔은 그 방을 다른 손님에게 줄 수 없습니다. `null` 대입은 열쇠를 반납하는 것입니다. 하지만 호텔 밖에서 쓰는 개인 열쇠(지역 변수)는 본인이 버리면 자동으로 사라집니다.

**원칙**: 클래스가 **자기 메모리를 직접 관리**하면(배열 기반 자료구조, 객체 풀 등), GC는 어떤 원소가 활성이고 비활성인지 알 수 없습니다. 이런 경우 프로그래머가 원소를 다 쓰면 null로 해제하여 GC에 알려줘야 합니다.

#### 누수 상황 2: 캐시

캐시에 객체를 넣고 **정리하는 것을 잊으면** 무한히 증가합니다. 이것은 실무에서 가장 흔한 메모리 누수 원인 중 하나입니다.

```java
// Bad: HashMap 캐시에 넣기만 하고 제거하지 않음
public class OrderCache {
    private static final Map<String, OrderDto> cache = new HashMap<>();

    public OrderDto getOrder(String orderId) {
        if (!cache.containsKey(orderId)) {
            OrderDto order = orderRepository.findById(orderId);
            cache.put(orderId, order);  // 계속 쌓임 → 메모리 무한 증가
        }
        return cache.get(orderId);
    }
    // 제거하는 코드가 없음!
}
```

**해결 방법 1 — WeakHashMap**: 키가 외부에서 더 이상 참조되지 않으면 엔트리가 자동 제거됩니다.

```java
Map<Key, Value> cache = new WeakHashMap<>();
```

**동작 원리**: WeakHashMap의 키는 **WeakReference**로 저장됩니다. WeakReference란 "다른 곳에서 강한 참조(Strong Reference)가 없으면 GC가 수거해도 된다"는 약한 참조입니다.

```
Strong Reference: Object obj = new Object();     → GC 수거 불가
Weak Reference:   WeakReference<Object> ref = ...; → 다른 강한 참조 없으면 GC 수거 가능
```

WeakHashMap은 키 객체가 GC에 의해 수거되면 해당 엔트리도 자동으로 제거됩니다. 캐시의 키가 외부에서 참조되는 동안만 유효한 캐시를 구현할 때 적합합니다.

**주의**: WeakHashMap은 **키**가 WeakReference입니다. 값(Value)이 아닙니다. 그리고 String 리터럴(`"abc"`)은 String Pool에 의해 항상 강한 참조가 유지되므로 WeakHashMap의 키로 쓰면 GC가 안 됩니다.

**해결 방법 2 — TTL(Time-To-Live)**: 일정 시간 후 자동 만료

```java
// Caffeine 캐시 라이브러리
Cache<String, OrderDto> cache = Caffeine.newBuilder()
    .expireAfterWrite(10, TimeUnit.MINUTES)  // 10분 후 만료
    .maximumSize(1000)                        // 최대 1000개
    .build();

// 사용
OrderDto order = cache.get(orderId, key -> orderRepository.findById(key));
// 캐시에 있으면 반환, 없으면 lambda 실행 후 캐시에 저장
```

**해결 방법 3 — 크기 제한 (LRU 캐시)**: `LinkedHashMap`의 `removeEldestEntry`를 오버라이드하여 LRU(Least Recently Used) 캐시를 구현합니다.

```java
// 최대 MAX_SIZE를 초과하면 가장 오래 안 쓴 항목을 자동 제거
Map<String, Object> cache = new LinkedHashMap<>(16, 0.75f, true) {
    // 세 번째 매개변수 true = 접근 순서(access-order) 모드
    // get()으로 접근한 항목이 맨 뒤로 이동 → 맨 앞이 가장 오래 안 쓴 항목
    @Override
    protected boolean removeEldestEntry(Map.Entry<String, Object> eldest) {
        return size() > MAX_SIZE;  // 최대 크기 초과 시 가장 오래된 항목 제거
    }
};
```

#### 누수 상황 3: 리스너와 콜백

리스너/콜백을 등록만 하고 **해제하지 않으면** 누적됩니다. GUI 프로그래밍이나 이벤트 기반 시스템에서 흔합니다.

```java
// Bad: 등록만 하고 해제 안 함
eventManager.addListener(myListener);
// ... 시간이 지나 myListener가 더 이상 필요 없어도 참조가 남아있음
// eventManager가 myListener를 강한 참조로 유지 → GC 수거 불가

// Good: 명시적 해제
eventManager.removeListener(myListener);
```

리스너를 확실히 해제하기 어려운 상황에서는 **WeakReference로 저장**하여 콜백이 GC 대상이 되면 자동으로 정리되게 할 수 있습니다.

### 3. 코드 예제

**ERP에서 발생할 수 있는 메모리 누수**

```java
// Bad: 수주 조회 결과를 static 캐시에 무한 적재
public class OrderCache {
    private static final Map<String, OrderDto> cache = new HashMap<>();
    // static → 애플리케이션 종료까지 살아있음
    // HashMap → 크기 제한 없음, 만료 없음

    public OrderDto getOrder(String orderId) {
        if (!cache.containsKey(orderId)) {
            OrderDto order = orderRepository.findById(orderId);
            cache.put(orderId, order);  // 계속 쌓임
        }
        return cache.get(orderId);
    }
    // 하루에 수주 1000건 × 365일 = 365,000건이 메모리에 영구 적재
    // 각 OrderDto가 1KB라면 → 356MB가 GC 불가 상태로 점유
}
```

```java
// Good: 크기 제한 + TTL 적용
public class OrderCache {
    private final Cache<String, OrderDto> cache = Caffeine.newBuilder()
        .expireAfterWrite(30, TimeUnit.MINUTES)  // 30분 후 만료
        .maximumSize(10000)                       // 최대 10,000건
        .build();

    public OrderDto getOrder(String orderId) {
        return cache.get(orderId, key -> orderRepository.findById(key));
    }
    // 30분 지나면 자동 만료, 10,000건 초과 시 LRU로 자동 제거
    // 메모리 사용량이 제한됨
}
```

### 4. 실무 연결

- **Spring `@Cacheable`**: 내부적으로 CacheManager(EhCache, Caffeine, Redis)를 사용하여 캐시 크기/TTL을 관리. 직접 HashMap 캐시를 만들면 안 되는 이유
- **HikariCP `leakDetectionThreshold`**: DB 커넥션을 반환하지 않으면(close() 누락) 경고 로그 출력. 커넥션도 일종의 자원 누수
- **ERP 대량 조회**: `SELECT * FROM 수주 WHERE ...`로 10만 건을 List에 담으면 해당 List가 GC 안 됨. 페이징 또는 스트림 처리(`ResultSet` 커서)로 해결
- **ThreadLocal 누수**: `ThreadLocal`에 값을 넣고 `remove()`를 안 하면, 스레드 풀 환경에서 스레드가 재사용될 때 이전 요청의 데이터가 남아있음. Spring의 `@RequestScope`가 이 문제를 자동 관리

### 5. 오해하기 쉬운 부분

**오해 1**: "Java는 GC가 있으니까 메모리 누수가 없다"
→ GC는 **도달 불가능한 객체만** 수거합니다. 프로그래머가 참조를 유지하면(배열에 남아있으면, 캐시에 들어있으면, 리스너 목록에 등록되어 있으면) GC도 수거할 수 없습니다. C/C++의 메모리 누수(free 안 함)와 형태는 다르지만 결과(메모리 고갈)는 동일합니다.

**오해 2**: "모든 변수를 쓴 후에 null로 해제해야 한다"
→ **지역 변수는 메서드가 끝나면 자동으로 참조가 사라집니다.** 모든 변수를 null로 해제하는 것은 오히려 코드를 지저분하게 만듭니다. null 해제가 필요한 경우는 오직 **"자기 메모리를 직접 관리하는 클래스"**(배열 기반 자료구조, 캐시, 객체 풀)에서 비활성 영역의 참조를 끊을 때뿐입니다.

**오해 3**: "WeakReference를 쓰면 모든 메모리 누수가 해결된다"
→ WeakReference는 **"다른 곳에서 강한 참조가 없을 때만"** GC 대상이 됩니다. 다른 곳에서 강한 참조를 유지하면 WeakReference를 써도 GC 안 됩니다. 또한 String 리터럴은 String Pool이 항상 강한 참조를 유지하므로 WeakHashMap의 키로 쓸 수 없습니다.

**오해 4**: "메모리 누수는 GC를 더 자주 돌리면 해결된다"
→ GC는 **도달 가능한 객체를 수거하지 않습니다**. 아무리 자주 돌려도 참조가 남아있는 객체는 수거 안 됩니다. 오히려 GC가 더 자주 돌면 STW(Stop-The-World)가 빈번해져서 성능만 나빠집니다. 근본 원인(불필요한 참조)을 제거해야 합니다.

### 6. 확인 질문

- [ ] Java에서 메모리 누수가 발생하는 3가지 상황을 각각 코드와 함께 설명할 수 있는가?
- [ ] Stack 예제에서 메모리 누수가 발생하는 **구체적 메커니즘**(GC Root → 참조 체인 → 비활성 원소)을 설명할 수 있는가?
- [ ] "모든 변수를 null로 해제해야 한다"가 왜 틀린 말인지, 언제만 필요한지 설명할 수 있는가?
- [ ] WeakReference와 Strong Reference의 차이를 설명할 수 있는가?
- [ ] WeakHashMap의 키로 String 리터럴을 쓰면 안 되는 이유를 설명할 수 있는가?
- [ ] 캐시 메모리 누수를 방지하는 방법 3가지(WeakHashMap, TTL, 크기 제한)를 각각 언제 사용하는지 설명할 수 있는가?

---

## Step 1 자가 검증

- [ ] 정적 팩토리 메서드의 장점 4가지 + 단점 2가지를 **코드 예시와 함께** 즉시 답변 가능
- [ ] 점층적 생성자 → 자바빈즈 → 빌더의 진화 과정과 **각각의 문제점**을 설명 가능
- [ ] 빌더 패턴을 **직접 구현**(Builder 내부 클래스 + 체이닝 + build() + private 생성자) 가능
- [ ] 싱글턴 구현 3가지와 enum이 가장 안전한 이유를 **직렬화/리플렉션 관점에서** 설명 가능
- [ ] 의존 객체 주입이 필요한 이유와 **Spring DI와의 관계**를 설명 가능
- [ ] 메모리 누수 3가지 상황을 식별하고 **각각의 해결책과 원리**를 설명 가능
- [ ] 위 6가지를 각각 **1분 이내로** 설명 가능

---

## 정리

Step 1 (객체 생성과 파괴)에서 배운 핵심:

| Item | 한 줄 정리 |
|------|----------|
| Item 1 | 생성자 대신 정적 팩토리 메서드로 이름/캐싱/하위 타입 반환의 유연성을 얻을 수 있다 |
| Item 2 | 매개변수가 많으면 빌더 패턴으로 가독성 + 불변성을 확보한다 |
| Item 3 | 싱글턴은 enum이 가장 안전하다. 실무에서는 Spring이 관리한다 |
| Item 5 | 자원을 직접 만들지 말고 생성자로 주입받아라 = Spring DI의 원리 |
| Item 7 | GC가 있어도 메모리 누수는 발생한다. 캐시/리스너에 주의하라 |

다음은 **Step 2. Effective Java — equals/hashCode/toString** 입니다.
