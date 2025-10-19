# 45장 var 키워드 - Part 3: 성능 최적화 & 고급 활용

## 📚 목차
1. [var 성능 분석](#성능-분석)
2. [바이트코드 비교](#바이트코드-비교)
3. [고급 활용 기법](#고급-활용-기법)
4. [자주 묻는 면접 질문 TOP 10](#면접-질문)
5. [종합 정리](#종합-정리)

---

## 🚀 성능 분석

### 📊 var vs 명시적 타입 성능 비교

```java
package var.performance;

import java.util.*;

/**
 * var 성능 테스트
 */
public class VarPerformanceTest {
    private static final int ITERATIONS = 10_000_000;

    public static void main(String[] args) {
        System.out.println("=== var vs 명시적 타입 성능 비교 ===\n");

        // 테스트 1: 변수 선언 및 초기화
        long start1 = System.nanoTime();
        for (int i = 0; i < ITERATIONS; i++) {
            String str1 = "Hello";
            int num1 = 42;
            List<String> list1 = new ArrayList<>();
        }
        long end1 = System.nanoTime();

        long start2 = System.nanoTime();
        for (int i = 0; i < ITERATIONS; i++) {
            var str2 = "Hello";
            var num2 = 42;
            var list2 = new ArrayList<String>();
        }
        long end2 = System.nanoTime();

        System.out.println("1000만 번 변수 선언:");
        System.out.println("명시적 타입: " +
            String.format("%.2f", (end1 - start1) / 1_000_000.0) + "ms");
        System.out.println("var 사용: " +
            String.format("%.2f", (end2 - start2) / 1_000_000.0) + "ms");
        System.out.println("→ 성능 차이: 없음 (컴파일 타임에 동일하게 변환)\n");

        // 테스트 2: 컬렉션 연산
        List<Integer> numbers = new ArrayList<>();
        for (int i = 0; i < 1000; i++) {
            numbers.add(i);
        }

        long start3 = System.nanoTime();
        for (int i = 0; i < 10000; i++) {
            Map<Boolean, List<Integer>> grouped1 = new HashMap<>();
            for (Integer num : numbers) {
                grouped1.computeIfAbsent(num % 2 == 0, k -> new ArrayList<>()).add(num);
            }
        }
        long end3 = System.nanoTime();

        long start4 = System.nanoTime();
        for (int i = 0; i < 10000; i++) {
            var grouped2 = new HashMap<Boolean, List<Integer>>();
            for (var num : numbers) {
                grouped2.computeIfAbsent(num % 2 == 0, k -> new ArrayList<>()).add(num);
            }
        }
        long end4 = System.nanoTime();

        System.out.println("1만 번 컬렉션 연산:");
        System.out.println("명시적 타입: " +
            String.format("%.2f", (end3 - start3) / 1_000_000.0) + "ms");
        System.out.println("var 사용: " +
            String.format("%.2f", (end4 - start4) / 1_000_000.0) + "ms");
        System.out.println();

        System.out.println("📊 결론:");
        System.out.println("✅ var는 컴파일 타임 기능 → 런타임 성능 영향 없음");
        System.out.println("✅ 바이트코드는 완전히 동일");
        System.out.println("✅ 성능보다는 가독성과 유지보수성 향상이 목적");
    }
}
```

### 🎯 핵심 포인트

**1. var는 컴파일 타임 기능**:
```java
// 소스 코드
var message = "Hello";

// 컴파일 후 바이트코드
String message = "Hello";  // 완전히 동일
```

**2. 성능 영향 없음**:
```
- 컴파일 시 명시적 타입으로 변환
- 바이트코드 동일
- 런타임 오버헤드 없음
```

---

## 🔍 바이트코드 비교

### 📊 컴파일 결과 분석

```java
package var.bytecode;

import java.util.*;

/**
 * 바이트코드 비교
 */
public class BytecodeComparison {

    // 명시적 타입
    public void explicitType() {
        String name = "김철수";
        int age = 25;
        List<String> items = new ArrayList<>();
    }

    // var 사용
    public void varType() {
        var name = "김철수";
        var age = 25;
        var items = new ArrayList<String>();
    }
}
```

**javap -c 결과 (바이트코드)**:
```
// explicitType() 메서드
0: ldc           #7   // String 김철수
2: astore_1
3: bipush        25
5: istore_2
6: new           #9   // class java/util/ArrayList
...

// varType() 메서드
0: ldc           #7   // String 김철수
2: astore_1
3: bipush        25
5: istore_2
6: new           #9   // class java/util/ArrayList
...
```

**결론**: 바이트코드가 완전히 동일!

---

## 💎 고급 활용 기법

### 🔷 기법 1: var와 익명 클래스

```java
package var.advanced;

/**
 * var와 익명 클래스
 */
public class VarAnonymousClass {
    public static void main(String[] args) {
        System.out.println("=== var와 익명 클래스 ===\n");

        // 익명 클래스의 타입을 var로 받기
        var calculator = new Object() {
            int add(int a, int b) {
                return a + b;
            }

            int multiply(int a, int b) {
                return a * b;
            }

            double divide(int a, int b) {
                return (double) a / b;
            }
        };

        System.out.println("10 + 20 = " + calculator.add(10, 20));
        System.out.println("10 * 20 = " + calculator.multiply(10, 20));
        System.out.println("10 / 3 = " + calculator.divide(10, 3));
        System.out.println();

        // 상태를 가진 익명 객체
        var counter = new Object() {
            private int count = 0;

            void increment() {
                count++;
            }

            int getCount() {
                return count;
            }
        };

        counter.increment();
        counter.increment();
        System.out.println("Count: " + counter.getCount());
    }
}
```

### 🔷 기법 2: var와 제네릭 메서드

```java
package var.advanced;

import java.util.*;

/**
 * var와 제네릭 메서드
 */
public class VarGenericMethods {
    public static void main(String[] args) {
        System.out.println("=== var와 제네릭 메서드 ===\n");

        // 제네릭 메서드 반환값을 var로 받기
        var list1 = createList("A", "B", "C");
        var list2 = createList(1, 2, 3);

        System.out.println("list1: " + list1);
        System.out.println("list2: " + list2);
        System.out.println();

        // 복잡한 제네릭 메서드
        var pair1 = createPair("Name", 25);
        var pair2 = createPair(1, "First");

        System.out.println("pair1: " + pair1);
        System.out.println("pair2: " + pair2);
    }

    @SafeVarargs
    static <T> List<T> createList(T... elements) {
        return Arrays.asList(elements);
    }

    static <K, V> Map<K, V> createPair(K key, V value) {
        var map = new HashMap<K, V>();
        map.put(key, value);
        return map;
    }
}
```

### 🔷 기법 3: var와 Stream API 고급 활용

```java
package var.advanced;

import java.util.*;
import java.util.stream.Collectors;

/**
 * var와 Stream API 고급 활용
 */
public class VarStreamAdvanced {
    public static void main(String[] args) {
        System.out.println("=== var와 Stream API 고급 ===\n");

        var products = List.of(
            new Product("노트북", 1500000, "전자"),
            new Product("마우스", 30000, "전자"),
            new Product("책상", 200000, "가구"),
            new Product("의자", 150000, "가구")
        );

        // 복잡한 grouping 연산
        var grouped = products.stream()
            .collect(Collectors.groupingBy(
                Product::getCategory,
                Collectors.mapping(
                    Product::getName,
                    Collectors.toList()
                )
            ));

        System.out.println("카테고리별 상품명:");
        grouped.forEach((category, names) -> {
            System.out.println(category + ": " + names);
        });
        System.out.println();

        // 다단계 통계
        var statistics = products.stream()
            .collect(Collectors.groupingBy(
                Product::getCategory,
                Collectors.teeing(
                    Collectors.counting(),
                    Collectors.summingInt(Product::getPrice),
                    (count, sum) -> Map.of(
                        "count", count,
                        "total", sum,
                        "average", sum / count
                    )
                )
            ));

        System.out.println("카테고리별 통계:");
        statistics.forEach((category, stats) -> {
            System.out.println(category + ": " + stats);
        });
    }

    static class Product {
        String name;
        int price;
        String category;

        Product(String name, int price, String category) {
            this.name = name;
            this.price = price;
            this.category = category;
        }

        String getName() { return name; }
        int getPrice() { return price; }
        String getCategory() { return category; }
    }
}
```

---

## 🎤 면접 질문

### ❓ Q1. var 키워드란 무엇인가?

**답변**:
```
var는 Java 10에서 도입된 지역 변수 타입 추론(Local Variable Type Inference) 키워드입니다.

특징:
1. 컴파일 타임에 타입 결정
2. 지역 변수에만 사용 가능
3. 초기화 필수
4. 런타임 성능 영향 없음

예시:
var message = "Hello";  // String으로 추론
var numbers = List.of(1, 2, 3);  // List<Integer>로 추론

장점:
- 긴 제네릭 타입 간소화
- 코드 가독성 향상
- 타입 변경 시 유지보수 용이

주의사항:
- null 초기화 불가
- 다이아몬드만 사용 불가
- 필드, 매개변수, 반환 타입에 사용 불가
```

---

### ❓ Q2. var는 동적 타입인가?

**답변**:
```
아니요, var는 정적 타입입니다.

차이점:
동적 타입 (JavaScript):
- 런타임에 타입 결정
- 타입 변경 가능
  var x = 10;
  x = "문자열";  // OK

정적 타입 (Java var):
- 컴파일 타임에 타입 결정
- 타입 변경 불가
  var x = 10;     // int로 고정
  x = "문자열";  // 컴파일 에러!

var의 동작:
1. 컴파일러가 우변을 분석
2. 타입을 추론하여 결정
3. 바이트코드에 명시적 타입으로 기록
4. 이후 타입 변경 불가

결론: var는 타입 추론일 뿐, 여전히 강타입(strongly-typed)
```

---

### ❓ Q3. var를 사용하면 성능에 영향이 있나?

**답변**:
```
아니요, 성능 영향이 전혀 없습니다.

이유:
1. 컴파일 타임 기능
   - 소스 코드: var message = "Hello";
   - 바이트코드: String message = "Hello";
   → 완전히 동일

2. 런타임 오버헤드 없음
   - JVM은 var를 모름
   - 실행 시에는 명시적 타입과 동일

3. 바이트코드 비교
   명시적:
   0: ldc #7  // String "Hello"
   2: astore_1

   var:
   0: ldc #7  // String "Hello"
   2: astore_1
   → 완전히 동일

성능 측정 결과:
- 변수 선언: 차이 없음
- 메서드 호출: 차이 없음
- 컬렉션 연산: 차이 없음

결론: var는 가독성 향상을 위한 syntactic sugar
```

---

### ❓ Q4. var를 어디에 사용할 수 있나?

**답변**:
```
var는 지역 변수에만 사용 가능합니다.

✅ 사용 가능:
1. 지역 변수
   void method() {
       var x = 10;
   }

2. for문
   for (var i = 0; i < 10; i++) { }
   for (var item : list) { }

3. try-with-resources
   try (var scanner = new Scanner(System.in)) { }

❌ 사용 불가:
1. 필드
   class MyClass {
       var field = 10;  // 컴파일 에러
   }

2. 메서드 매개변수
   void method(var param) { }  // 컴파일 에러

3. 메서드 반환 타입
   var getValue() { return 10; }  // 컴파일 에러

4. 생성자 매개변수
   MyClass(var param) { }  // 컴파일 에러

제약 이유:
- 필드: 여러 메서드에서 사용, 타입 명확성 필요
- 매개변수: API 명세, 타입 명시 필수
- 반환 타입: 호출자가 알아야 함
```

---

### ❓ Q5. var와 다이아몬드 연산자를 같이 쓸 수 있나?

**답변**:
```
제한적으로 가능하지만, 주의가 필요합니다.

❌ 안 되는 경우:
var list = new ArrayList<>();  // 컴파일 에러
// 이유: 제네릭 타입을 추론할 수 없음

✅ 되는 경우:
var list = new ArrayList<String>();  // OK
// 이유: 우변에 제네릭 타입 명시

List<String> list = new ArrayList<>();  // OK
// 이유: 좌변에 타입 명시

해결 방법:
1. 우변에 제네릭 타입 명시
   var list = new ArrayList<String>();

2. 좌변에 명시적 타입
   List<String> list = new ArrayList<>();

3. 팩토리 메서드 사용
   var list = List.of("A", "B", "C");
   var set = Set.of(1, 2, 3);

권장사항:
- var 사용 시: 우변에 제네릭 타입 명시
- 다이아몬드 사용 시: 좌변에 인터페이스 타입
```

---

### ❓ Q6. var를 사용하면 가독성이 떨어지지 않나?

**답변**:
```
상황에 따라 다릅니다.

✅ 가독성이 좋아지는 경우:
1. 타입이 명확한 경우
   var customerList = new ArrayList<Customer>();
   var orderDate = LocalDate.now();
   var builder = new StringBuilder();

2. 제네릭 타입이 긴 경우
   // Before
   Map<String, List<Order>> orders = new HashMap<>();

   // After
   var orders = new HashMap<String, List<Order>>();

3. 변수명으로 타입 유추 가능
   var totalPrice = 10000;
   var isActive = true;

❌ 가독성이 나빠지는 경우:
1. 타입이 불명확한 경우
   var data = getData();  // 뭐가 반환되는지?
   var result = process();  // 알 수 없음

2. 변수명이 모호한 경우
   var temp = calculate();
   var x = getValue();

3. 메서드 체이닝
   var result = list.stream()
       .filter(...)
       .map(...)
       .collect(...);  // 반환 타입이 뭐지?

가이드라인:
1. 우변이 명확하면 var 사용
2. 변수명으로 타입 유추 가능하게
3. 팀 코딩 컨벤션 따르기
4. 의심스러우면 명시적 타입 사용
```

---

### ❓ Q7. var는 왜 지역 변수에만 사용 가능한가?

**답변**:
```
설계상의 이유와 실용적 이유가 있습니다.

1. 필드에 불가능한 이유:
   class MyClass {
       var field = 10;  // 불가
   }

   문제점:
   - 필드는 여러 메서드에서 접근
   - 클래스 API의 일부
   - 타입이 명확해야 함
   - 리플렉션 API 고려

2. 매개변수에 불가능한 이유:
   void method(var param) { }  // 불가

   문제점:
   - 메서드 시그니처의 일부
   - 오버로딩 판단 필요
   - API 문서화
   - 호출자가 타입을 알아야 함

3. 반환 타입에 불가능한 이유:
   var getValue() { return 10; }  // 불가

   문제점:
   - 메서드 시그니처
   - 호출자가 반환 타입을 알아야 함
   - 오버라이딩 고려

지역 변수만 가능한 이유:
- 스코프가 제한적
- 초기화와 사용이 가까움
- 타입이 명확히 드러남
- API 영향 없음

결론: var는 편의를 위한 기능이지, 타입 시스템을 약화시키지 않음
```

---

### ❓ Q8. var와 final을 같이 쓸 수 있나?

**답변**:
```
네, 가능하고 권장됩니다.

사용 방법:
final var message = "Hello";
final var list = new ArrayList<String>();

list.add("item");  // OK (컬렉션 수정)
// list = new ArrayList<>();  // 컴파일 에러 (재할당 불가)

장점:
1. 불변성 보장
   final var value = 10;
   // value = 20;  // 컴파일 에러

2. 실수 방지
   final var config = loadConfig();
   // config = null;  // 컴파일 에러

3. 함수형 프로그래밍
   final var result = stream
       .filter(x -> x > 10)
       .collect(toList());

effectively final:
// final 키워드 없어도 effectively final
var x = 10;
// x를 재할당하지 않으면 effectively final
Runnable r = () -> System.out.println(x);

권장사항:
- 재할당이 필요 없으면 final 사용
- 람다에서 캡처할 변수는 final
- 불변성 원칙 따르기
```

---

### ❓ Q9. var를 사용하면 리팩토링이 쉬운가?

**답변**:
```
네, 특정 경우에 리팩토링이 쉬워집니다.

✅ 리팩토링이 쉬운 경우:

1. 구현 클래스 변경
   // Before
   ArrayList<String> list = new ArrayList<>();

   // 구현 변경 시
   LinkedList<String> list = new LinkedList<>();
   // 여러 곳을 수정해야 함

   // var 사용
   var list = new ArrayList<String>();
   // 한 곳만 수정
   var list = new LinkedList<String>();

2. 복잡한 제네릭 타입 변경
   // Before
   Map<String, List<Order>> orders = factory.createOrders();

   // 팩토리 반환 타입 변경 시
   Map<String, Set<Order>> orders = factory.createOrders();
   // 여러 곳 수정 필요

   // var 사용
   var orders = factory.createOrders();
   // 팩토리만 수정하면 됨

❌ 리팩토링이 어려운 경우:

1. 인터페이스 → 구현 변경
   List<String> list = new ArrayList<>();
   list.add("item");  // List 메서드

   var list = new ArrayList<String>();
   list.ensureCapacity(100);  // ArrayList 전용 메서드
   // 나중에 구현 변경 시 문제

주의사항:
- 인터페이스 프로그래밍 원칙
- API에 의존하지 말고 추상화에 의존
- var는 도구일 뿐, 설계 원칙 우선

결론:
var는 리팩토링을 쉽게 만들 수 있지만,
올바른 설계 원칙과 함께 사용해야 함
```

---

### ❓ Q10. var 사용 시 베스트 프랙티스는?

**답변**:
```
var 사용 가이드라인:

1. ✅ 타입이 명확한 경우
   var customerList = new ArrayList<Customer>();
   var now = LocalDate.now();
   var pattern = Pattern.compile("\\d+");

2. ✅ 제네릭 타입이 긴 경우
   var data = new HashMap<String, List<Order>>();

3. ✅ 변수명으로 타입 유추 가능
   var totalPrice = calculatePrice();
   var isValid = validate();

4. ❌ 타입이 불명확한 경우
   var data = getData();  // 뭐가 반환되는지?
   String data = getData();  // 명시적 타입 사용

5. ❌ null 초기화
   // var name = null;  // 불가능
   String name = null;  // 명시적 타입

6. ❌ 다이아몬드만 사용
   // var list = new ArrayList<>();  // 불가능
   var list = new ArrayList<String>();

7. ✅ for문에서 활용
   for (var item : collection) { }
   for (var i = 0; i < 10; i++) { }

8. ✅ try-with-resources
   try (var scanner = new Scanner(file)) { }

9. ✅ Stream API 결과
   var filtered = list.stream()
       .filter(x -> x > 10)
       .collect(toList());

10. ❌ API 경계
    // 메서드 시그니처에는 명시적 타입
    public List<Order> getOrders() {
        var orders = fetchOrders();  // 내부에서는 var OK
        return orders;
    }

팀 가이드라인:
- 일관성 유지
- 코드 리뷰에서 확인
- 가독성 우선
- 의심스러우면 명시적 타입
```

---

## 🎓 종합 정리

### 📊 var 체크리스트

```
✅ 사용하기 좋은 경우:
1. 복잡한 제네릭 타입
2. Stream API 결과
3. 빌더 패턴
4. for문
5. try-with-resources

❌ 사용을 피할 경우:
1. 타입이 불명확한 메서드 반환
2. null 초기화
3. 다이아몬드만 사용
4. API 경계 (매개변수, 반환 타입)
5. 짧고 명확한 타입 (int, String 등은 선택적)
```

---

### 💡 var 사용 원칙

```java
// 1. 가독성 우선
var customerList = new ArrayList<Customer>();  // ✅ 명확
var data = getData();  // ❌ 불명확

// 2. 변수명 명확히
var totalPrice = 10000;  // ✅ 의미 명확
var x = 10000;  // ❌ 의미 불명확

// 3. 우변 명확성
var list = new ArrayList<String>();  // ✅ 타입 명확
var list = createList();  // ❌ 반환 타입 불명확

// 4. 인터페이스 vs 구현
List<String> list = new ArrayList<>();  // ✅ 인터페이스 필요
var list = new ArrayList<String>();  // ✅ 구현 명확

// 5. final 고려
final var config = loadConfig();  // ✅ 불변성
```

---

## 🚀 다음 단계 학습

```
1. Records (Java 14+)
   - 데이터 클래스 간소화
   - var와 함께 사용

2. Pattern Matching (Java 16+)
   - instanceof와 var
   - switch 표현식

3. Text Blocks (Java 15+)
   - 여러 줄 문자열
   - var와 조합
```

---

## 🎉 시리즈 완료!

**Part 1**: 5가지 실생활 비유로 var 이해
**Part 2**: 3개 기업 사례 + 4개 주니어 실수
**Part 3**: 성능 분석 + 바이트코드 + 면접 질문

var 키워드를 완벽하게 마스터했습니다!
