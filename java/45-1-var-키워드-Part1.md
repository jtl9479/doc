# 45장 var 키워드 - Part 1: 실생활 비유로 이해하기

## 📚 목차
1. [비유 1: 자동 라벨 부착 시스템 (타입 추론)](#비유-1-자동-라벨-부착-시스템)
2. [비유 2: 스마트 계산기 (복잡한 타입 간소화)](#비유-2-스마트-계산기)
3. [비유 3: 명찰 자동 생성 (제네릭 타입 간소화)](#비유-3-명찰-자동-생성)
4. [비유 4: 변수명으로 추론하기 (가독성)](#비유-4-변수명으로-추론하기)
5. [비유 5: var의 한계 (명확성이 필요한 경우)](#비유-5-var의-한계)

---

## 🔍 var 키워드란?

var는 Java 10에서 도입된 **지역 변수 타입 추론(Local Variable Type Inference)** 키워드입니다.

**핵심 개념**:
```java
// 전통적인 방식
String message = "Hello World";
ArrayList<String> list = new ArrayList<>();

// var 사용
var message = "Hello World";  // 컴파일러가 String으로 추론
var list = new ArrayList<String>();  // 컴파일러가 ArrayList<String>으로 추론
```

**var의 특징**:
```
1. 컴파일 타임에 타입 결정 (런타임 아님!)
2. 지역 변수에만 사용 가능
3. 초기화 필수 (타입 추론을 위해)
4. null로 초기화 불가
```

---

## 📖 비유 1: 자동 라벨 부착 시스템 (타입 추론)

### 🎯 실생활 비유

창고에서 물건을 보관할 때 라벨을 붙이는 상황을 생각해봅시다.

**전통적인 방식 (명시적 타입)**:
```
직원: "이건 '사과(Apple)' 라벨을 붙여주세요"
관리자: "네, '사과(Apple)' 라벨 부착했습니다"
→ 명시적으로 라벨 이름을 말함
```

**var 방식 (타입 추론)**:
```
직원: "이걸 보관해주세요" (사과를 건네줌)
관리자: "보니까 사과네요. '사과(Apple)' 라벨 부착했습니다"
→ 물건을 보고 자동으로 라벨 결정
```

### 💻 Java 코드로 구현

```java
package var.example1;

import java.util.*;

/**
 * var 타입 추론 기본
 */
public class TypeInferenceDemo {
    public static void main(String[] args) {
        System.out.println("=== var 타입 추론 기본 ===\n");

        // 시나리오 1: 기본 타입 추론
        System.out.println("📍 시나리오 1: 기본 타입 추론");

        // 전통적인 방식
        String name1 = "김철수";
        int age1 = 25;
        double price1 = 1500.50;
        boolean isActive1 = true;

        // var 사용
        var name2 = "김철수";        // String으로 추론
        var age2 = 25;               // int로 추론
        var price2 = 1500.50;        // double로 추론
        var isActive2 = true;        // boolean으로 추론

        System.out.println("name2의 타입: " + ((Object) name2).getClass().getSimpleName());
        System.out.println("age2의 타입: " + ((Object) age2).getClass().getSimpleName());
        System.out.println("price2의 타입: " + ((Object) price2).getClass().getSimpleName());
        System.out.println("isActive2의 타입: " + ((Object) isActive2).getClass().getSimpleName());
        System.out.println();

        // 시나리오 2: 컬렉션 타입 추론
        System.out.println("📍 시나리오 2: 컬렉션 타입 추론");

        // 전통적인 방식 (타입이 길고 반복적)
        ArrayList<String> list1 = new ArrayList<>();
        HashMap<String, Integer> map1 = new HashMap<>();
        HashSet<Long> set1 = new HashSet<>();

        // var 사용 (간결함)
        var list2 = new ArrayList<String>();
        var map2 = new HashMap<String, Integer>();
        var set2 = new HashSet<Long>();

        list2.add("사과");
        map2.put("바나나", 1000);
        set2.add(123L);

        System.out.println("list2의 타입: " + list2.getClass().getSimpleName());
        System.out.println("map2의 타입: " + map2.getClass().getSimpleName());
        System.out.println("set2의 타입: " + set2.getClass().getSimpleName());
        System.out.println();

        // 시나리오 3: 메서드 반환값 타입 추론
        System.out.println("📍 시나리오 3: 메서드 반환값 타입 추론");

        // 전통적인 방식
        StringBuilder builder1 = new StringBuilder();
        builder1.append("Hello");

        // var 사용
        var builder2 = new StringBuilder();
        builder2.append("World");

        // 메서드 체이닝
        var result = builder2.append(" ").append("Java");

        System.out.println("result의 타입: " + result.getClass().getSimpleName());
        System.out.println("result: " + result);
        System.out.println();

        // 시나리오 4: 타입 추론의 정확성
        System.out.println("📍 시나리오 4: 타입 추론의 정확성");

        var num1 = 10;        // int
        var num2 = 10L;       // long
        var num3 = 10.0;      // double
        var num4 = 10.0f;     // float

        System.out.println("num1 (10): " + ((Object) num1).getClass().getSimpleName());
        System.out.println("num2 (10L): " + ((Object) num2).getClass().getSimpleName());
        System.out.println("num3 (10.0): " + ((Object) num3).getClass().getSimpleName());
        System.out.println("num4 (10.0f): " + ((Object) num4).getClass().getSimpleName());
        System.out.println();

        // 시나리오 5: 타입이 명확한 경우
        System.out.println("📍 시나리오 5: var 사용이 적절한 경우");

        // 타입이 명확하고 우변이 길 때
        var customerList = new ArrayList<Customer>();
        var orderMap = new HashMap<String, List<Order>>();

        // 반복문에서
        var numbers = List.of(1, 2, 3, 4, 5);
        for (var number : numbers) {
            System.out.print(number + " ");
        }
        System.out.println();
    }

    static class Customer {
        String name;
    }

    static class Order {
        String id;
    }
}
```

### 🎯 핵심 포인트

**1. var는 컴파일 타임 기능**:
```java
var message = "Hello";  // 컴파일 시 String message = "Hello";로 변환

// 바이트코드에는 String으로 기록됨
// 런타임 성능에 영향 없음
```

**2. 초기화 필수**:
```java
// ❌ 컴파일 에러
var x;  // 타입을 추론할 수 없음
x = 10;

// ✅ 올바른 사용
var x = 10;  // int로 추론
```

**3. null 초기화 불가**:
```java
// ❌ 컴파일 에러
var name = null;  // 타입을 알 수 없음

// ✅ 명시적 타입 필요
String name = null;
```

---

## 📖 비유 2: 스마트 계산기 (복잡한 타입 간소화)

### 🎯 실생활 비유

복잡한 계산식을 계산기에 입력하는 상황입니다.

**전통적인 계산기**:
```
"((100 + 50) * 2) / 3"을 매번 전체 수식 입력
→ 길고 복잡함
```

**스마트 계산기 (var)**:
```
"이 계산 결과를 저장"
→ 계산기가 알아서 타입 결정
```

### 💻 Java 코드로 구현

```java
package var.example2;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 복잡한 타입 간소화
 */
public class ComplexTypeDemo {
    public static void main(String[] args) {
        System.out.println("=== 복잡한 타입 간소화 ===\n");

        // 시나리오 1: 제네릭 타입이 긴 경우
        System.out.println("📍 시나리오 1: 제네릭 타입이 긴 경우");

        // 전통적인 방식 (타입이 너무 김)
        Map<String, List<Map<String, Object>>> data1 = new HashMap<>();

        // var 사용 (간결함)
        var data2 = new HashMap<String, List<Map<String, Object>>>();

        // 데이터 추가
        var userList = new ArrayList<Map<String, Object>>();
        var user1 = new HashMap<String, Object>();
        user1.put("name", "김철수");
        user1.put("age", 25);
        userList.add(user1);
        data2.put("users", userList);

        System.out.println("✅ 복잡한 제네릭 타입을 var로 간소화");
        System.out.println("data2: " + data2);
        System.out.println();

        // 시나리오 2: Stream API 결과
        System.out.println("📍 시나리오 2: Stream API 결과");

        List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David");

        // 전통적인 방식
        Map<Integer, List<String>> grouped1 = names.stream()
            .collect(Collectors.groupingBy(String::length));

        // var 사용
        var grouped2 = names.stream()
            .collect(Collectors.groupingBy(String::length));

        System.out.println("✅ Stream 결과 타입을 var로 간소화");
        System.out.println("이름 길이별 그룹: " + grouped2);
        System.out.println();

        // 시나리오 3: 익명 클래스 반환
        System.out.println("📍 시나리오 3: 복잡한 익명 타입");

        // var를 사용하면 복잡한 익명 타입도 간단히 처리
        var calculator = new Object() {
            int add(int a, int b) { return a + b; }
            int multiply(int a, int b) { return a * b; }
        };

        System.out.println("calculator.add(10, 20) = " + calculator.add(10, 20));
        System.out.println("calculator.multiply(5, 6) = " + calculator.multiply(5, 6));
        System.out.println();

        // 시나리오 4: try-with-resources
        System.out.println("📍 시나리오 4: try-with-resources에서 var");

        // 전통적인 방식
        try (Scanner scanner1 = new Scanner(System.in)) {
            // scanner1 사용
        }

        // var 사용
        try (var scanner2 = new Scanner(System.in)) {
            // scanner2 사용
        }

        System.out.println("✅ try-with-resources에서도 var 사용 가능");
        System.out.println();

        // 시나리오 5: 반복문에서 var
        System.out.println("📍 시나리오 5: 반복문에서 var");

        var products = List.of(
            new Product("노트북", 1500000),
            new Product("마우스", 30000),
            new Product("키보드", 80000)
        );

        System.out.println("향상된 for문:");
        for (var product : products) {
            System.out.println("  " + product);
        }
        System.out.println();

        System.out.println("인덱스 for문:");
        for (var i = 0; i < products.size(); i++) {
            System.out.println("  [" + i + "] " + products.get(i));
        }
    }

    static class Product {
        String name;
        int price;

        Product(String name, int price) {
            this.name = name;
            this.price = price;
        }

        @Override
        public String toString() {
            return name + " - " + String.format("%,d", price) + "원";
        }
    }
}
```

### 🎯 핵심 포인트

**1. 제네릭 타입 간소화**:
```java
// Before
Map<String, List<CustomerOrder>> orders = new HashMap<String, List<CustomerOrder>>();

// After
var orders = new HashMap<String, List<CustomerOrder>>();
```

**2. Stream API와 var**:
```java
// 복잡한 Stream 결과 타입을 var로 간단히
var result = list.stream()
    .filter(x -> x > 10)
    .collect(Collectors.toList());
```

**3. 익명 클래스와 var**:
```java
var obj = new Object() {
    String name = "test";
    void hello() { System.out.println("Hello"); }
};

obj.hello();  // 익명 클래스의 메서드 호출 가능
```

---

## 📖 비유 3: 명찰 자동 생성 (제네릭 타입 간소화)

### 🎯 실생활 비유

회사에서 명찰을 만드는 상황입니다.

**전통적인 방식**:
```
직원: "제 명찰은 '개발팀 시니어 백엔드 개발자'로 해주세요"
→ 긴 직책을 전부 말해야 함
```

**var 방식**:
```
직원: "제 명찰 만들어주세요" (사원증을 보여줌)
관리자: "사원증 보니 '개발팀 시니어 백엔드 개발자'네요. 명찰 만들었습니다"
→ 자동으로 정보 파악
```

### 💻 Java 코드로 구현

```java
package var.example3;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 제네릭 타입 간소화
 */
public class GenericSimplificationDemo {
    public static void main(String[] args) {
        System.out.println("=== 제네릭 타입 간소화 ===\n");

        // 시나리오 1: 다이아몬드 연산자와 var
        System.out.println("📍 시나리오 1: 다이아몬드 연산자와 var");

        // 전통적인 방식
        List<String> list1 = new ArrayList<String>();

        // Java 7 다이아몬드 연산자
        List<String> list2 = new ArrayList<>();

        // var + 다이아몬드 (가장 간결)
        var list3 = new ArrayList<String>();

        list3.add("Apple");
        list3.add("Banana");

        System.out.println("✅ var는 우변에 제네릭 타입 명시 필요");
        System.out.println("list3: " + list3);
        System.out.println();

        // 시나리오 2: 중첩된 제네릭
        System.out.println("📍 시나리오 2: 중첩된 제네릭");

        // 전통적인 방식 (너무 김)
        Map<String, Map<String, List<String>>> nestedMap1 =
            new HashMap<String, Map<String, List<String>>>();

        // var 사용
        var nestedMap2 = new HashMap<String, Map<String, List<String>>>();

        var innerMap = new HashMap<String, List<String>>();
        innerMap.put("fruits", List.of("사과", "바나나"));
        nestedMap2.put("category1", innerMap);

        System.out.println("✅ 중첩된 제네릭도 var로 간소화");
        System.out.println("nestedMap2: " + nestedMap2);
        System.out.println();

        // 시나리오 3: Optional과 var
        System.out.println("📍 시나리오 3: Optional과 var");

        // 전통적인 방식
        Optional<String> optional1 = Optional.of("Hello");

        // var 사용
        var optional2 = Optional.of("World");

        optional2.ifPresent(value -> System.out.println("  값: " + value));
        System.out.println();

        // 시나리오 4: Stream Collectors
        System.out.println("📍 시나리오 4: Stream Collectors");

        List<Person> people = Arrays.asList(
            new Person("김철수", 25, "서울"),
            new Person("이영희", 30, "부산"),
            new Person("박민수", 25, "서울")
        );

        // 전통적인 방식
        Map<Integer, List<Person>> groupedByAge1 = people.stream()
            .collect(Collectors.groupingBy(Person::getAge));

        // var 사용
        var groupedByAge2 = people.stream()
            .collect(Collectors.groupingBy(Person::getAge));

        System.out.println("나이별 그룹:");
        groupedByAge2.forEach((age, persons) -> {
            System.out.println("  " + age + "세: " + persons);
        });
        System.out.println();

        // 시나리오 5: 다양한 컬렉션 타입
        System.out.println("📍 시나리오 5: 다양한 컬렉션 타입");

        var arrayList = new ArrayList<String>();
        var linkedList = new LinkedList<Integer>();
        var hashSet = new HashSet<Long>();
        var treeSet = new TreeSet<String>();
        var hashMap = new HashMap<String, Integer>();
        var linkedHashMap = new LinkedHashMap<String, String>();

        System.out.println("✅ 모든 컬렉션 타입에서 var 사용 가능");
        System.out.println("arrayList: " + arrayList.getClass().getSimpleName());
        System.out.println("linkedList: " + linkedList.getClass().getSimpleName());
        System.out.println("hashSet: " + hashSet.getClass().getSimpleName());
        System.out.println("treeSet: " + treeSet.getClass().getSimpleName());
        System.out.println("hashMap: " + hashMap.getClass().getSimpleName());
        System.out.println("linkedHashMap: " + linkedHashMap.getClass().getSimpleName());
    }

    static class Person {
        String name;
        int age;
        String city;

        Person(String name, int age, String city) {
            this.name = name;
            this.age = age;
            this.city = city;
        }

        String getName() { return name; }
        int getAge() { return age; }
        String getCity() { return city; }

        @Override
        public String toString() {
            return name + " (" + age + "세, " + city + ")";
        }
    }
}
```

### 🎯 핵심 포인트

**1. var와 다이아몬드 연산자**:
```java
// ❌ 타입을 추론할 수 없음
var list = new ArrayList<>();  // 컴파일 에러

// ✅ 우변에 제네릭 타입 명시 필요
var list = new ArrayList<String>();
```

**2. 중첩 제네릭**:
```java
// 긴 타입을 var로 간소화
var complex = new HashMap<String, Map<String, List<Integer>>>();
```

**3. Stream과 var**:
```java
// Stream 결과의 복잡한 타입을 var로 처리
var result = stream.collect(Collectors.groupingBy(...));
```

---

## 📖 비유 4: 변수명으로 추론하기 (가독성)

### 🎯 실생활 비유

식당에서 주문하는 상황입니다.

**명확한 변수명**:
```
손님: "아메리카노 주세요"
직원: "아메리카노 나왔습니다"
→ 음료 이름이 명확함
```

**모호한 변수명**:
```
손님: "저거 주세요"
직원: "뭘 드릴까요?"
→ 가리키는 것이 불명확
```

### 💻 Java 코드로 구현

```java
package var.example4;

import java.util.*;

/**
 * 가독성과 변수명
 */
public class ReadabilityDemo {
    public static void main(String[] args) {
        System.out.println("=== var 가독성 ===\n");

        // 시나리오 1: 변수명이 명확한 경우 (var 적합)
        System.out.println("📍 시나리오 1: 변수명이 명확한 경우");

        // ✅ 변수명으로 타입을 알 수 있음
        var customerList = new ArrayList<Customer>();
        var orderMap = new HashMap<String, Order>();
        var productCount = 10;
        var isActive = true;

        System.out.println("✅ 변수명이 명확하면 var 사용 적합");
        System.out.println("customerList: " + customerList.getClass().getSimpleName());
        System.out.println("orderMap: " + orderMap.getClass().getSimpleName());
        System.out.println();

        // 시나리오 2: 변수명이 모호한 경우 (var 부적합)
        System.out.println("📍 시나리오 2: 변수명이 모호한 경우");

        // ❌ 타입을 알기 어려움
        var data = getData();        // 무슨 타입인지?
        var result = process();      // 무슨 타입인지?
        var temp = calculate();      // 무슨 타입인지?

        System.out.println("❌ 변수명이 모호하면 var 사용 지양");
        System.out.println();

        // 시나리오 3: 우변이 명확한 경우
        System.out.println("📍 시나리오 3: 우변이 명확한 경우");

        // ✅ new로 생성 → 타입 명확
        var customers = new ArrayList<Customer>();
        var settings = new HashMap<String, String>();

        // ✅ 팩토리 메서드 → 이름으로 타입 유추
        var emptyList = Collections.emptyList();
        var singletonList = Collections.singletonList("item");

        System.out.println("✅ 우변이 명확하면 var 사용 적합");
        System.out.println();

        // 시나리오 4: 메서드 체이닝
        System.out.println("📍 시나리오 4: 메서드 체이닝");

        // ✅ 빌더 패턴과 var
        var person = new PersonBuilder()
            .setName("김철수")
            .setAge(25)
            .setCity("서울")
            .build();

        System.out.println("person: " + person);
        System.out.println();

        // 시나리오 5: 숫자 리터럴
        System.out.println("📍 시나리오 5: 숫자 리터럴 주의");

        var num1 = 10;        // int
        var num2 = 10L;       // long
        var num3 = 10.0;      // double
        var num4 = 10.0f;     // float

        System.out.println("✅ 숫자 리터럴은 접미사로 타입 결정");
        System.out.println("num1 (10): int");
        System.out.println("num2 (10L): long");
        System.out.println("num3 (10.0): double");
        System.out.println("num4 (10.0f): float");
    }

    static Object getData() {
        return new HashMap<String, String>();
    }

    static Object process() {
        return Arrays.asList(1, 2, 3);
    }

    static Object calculate() {
        return 42;
    }

    static class Customer {
        String name;
    }

    static class Order {
        String id;
    }

    static class Person {
        String name;
        int age;
        String city;

        @Override
        public String toString() {
            return name + " (" + age + "세, " + city + ")";
        }
    }

    static class PersonBuilder {
        private Person person = new Person();

        PersonBuilder setName(String name) {
            person.name = name;
            return this;
        }

        PersonBuilder setAge(int age) {
            person.age = age;
            return this;
        }

        PersonBuilder setCity(String city) {
            person.city = city;
            return this;
        }

        Person build() {
            return person;
        }
    }
}
```

### 🎯 핵심 포인트

**1. 명확한 변수명**:
```java
// ✅ 좋은 예
var customerList = new ArrayList<Customer>();
var orderCount = 10;

// ❌ 나쁜 예
var list = getList();  // 무슨 리스트?
var data = getData();  // 무슨 데이터?
```

**2. 우변의 명확성**:
```java
// ✅ 우변이 명확
var name = "김철수";
var list = new ArrayList<String>();
var builder = new StringBuilder();

// ❌ 우변이 불명확
var result = someMethod();  // 반환 타입이 뭐지?
```

**3. 가독성 우선**:
```java
// 명시적 타입이 더 명확한 경우
String userName = getUserName();  // var보다 명확

// var가 더 간결한 경우
var complexMap = new HashMap<String, List<Order>>();
```

---

## 📖 비유 5: var의 한계 (명확성이 필요한 경우)

### 🎯 실생활 비유

공항 세관에서 물품을 신고하는 상황입니다.

**명확한 신고 필요**:
```
세관원: "어떤 물품입니까?"
여행자: "이건요..." (가방만 가리킴)
세관원: "정확히 말씀해주세요"
→ 명시적 신고 필요
```

### 💻 Java 코드로 구현

```java
package var.example5;

import java.util.*;

/**
 * var의 한계와 제약사항
 */
public class VarLimitationsDemo {
    // ❌ 필드에는 var 사용 불가
    // var field = 10;  // 컴파일 에러

    private String field = "field";  // ✅ 명시적 타입 필요

    public static void main(String[] args) {
        System.out.println("=== var의 한계 ===\n");

        // 시나리오 1: var를 사용할 수 없는 경우
        System.out.println("📍 시나리오 1: var 사용 불가 케이스");

        // ❌ 초기화 없이 선언 불가
        // var x;  // 컴파일 에러
        // x = 10;

        // ❌ null로 초기화 불가
        // var name = null;  // 컴파일 에러

        // ❌ 람다 표현식에 직접 사용 불가
        // var lambda = () -> System.out.println("Hello");  // 컴파일 에러

        // ❌ 메서드 참조에 직접 사용 불가
        // var methodRef = String::length;  // 컴파일 에러

        System.out.println("❌ var는 지역 변수에만 사용 가능");
        System.out.println("❌ 초기화 필수");
        System.out.println("❌ null 초기화 불가");
        System.out.println();

        // 시나리오 2: 다이아몬드 연산자 단독 사용 불가
        System.out.println("📍 시나리오 2: 다이아몬드 연산자");

        // ❌ 타입을 추론할 수 없음
        // var list1 = new ArrayList<>();  // 컴파일 에러

        // ✅ 제네릭 타입 명시 필요
        var list2 = new ArrayList<String>();
        list2.add("Hello");

        System.out.println("✅ 우변에 제네릭 타입 명시 필요");
        System.out.println();

        // 시나리오 3: 배열 초기화
        System.out.println("📍 시나리오 3: 배열 초기화");

        // ❌ 배열 이니셜라이저 직접 사용 불가
        // var array1 = {1, 2, 3};  // 컴파일 에러

        // ✅ 명시적 배열 생성
        var array2 = new int[]{1, 2, 3};

        System.out.println("✅ 배열은 명시적 생성 필요");
        System.out.println();

        // 시나리오 4: 인터페이스 타입
        System.out.println("📍 시나리오 4: 인터페이스 타입");

        // var는 구현 타입으로 추론됨
        var list3 = new ArrayList<String>();  // ArrayList로 추론

        // 인터페이스 타입이 필요한 경우 명시적 타입 사용
        List<String> list4 = new ArrayList<>();  // List로 선언

        System.out.println("list3 타입: " + list3.getClass().getSimpleName());
        System.out.println("→ var는 구현 클래스 타입으로 추론");
        System.out.println();

        // 시나리오 5: 메서드 시그니처
        System.out.println("📍 시나리오 5: 메서드 시그니처");

        System.out.println("❌ var는 다음 위치에 사용 불가:");
        System.out.println("  - 메서드 매개변수");
        System.out.println("  - 메서드 반환 타입");
        System.out.println("  - 필드");
        System.out.println("  - 생성자 매개변수");
    }

    // ❌ 메서드 매개변수에 var 사용 불가
    // void method(var param) { }  // 컴파일 에러

    // ❌ 반환 타입에 var 사용 불가
    // var getValue() { return 10; }  // 컴파일 에러

    // ✅ 지역 변수에서만 사용
    void localVariableOnly() {
        var local = 10;  // OK
    }
}
```

### 🎯 핵심 포인트

**1. var 사용 가능 위치**:
```java
// ✅ 가능
void method() {
    var x = 10;  // 지역 변수
    for (var i = 0; i < 10; i++) { }  // for문
    for (var item : list) { }  // 향상된 for문
    try (var scanner = new Scanner(System.in)) { }  // try-with-resources
}

// ❌ 불가능
var field = 10;  // 필드
void method(var param) { }  // 매개변수
var method() { return 10; }  // 반환 타입
```

**2. 초기화 필수**:
```java
// ❌ 불가능
var x;
x = 10;

var y = null;  // null 불가

// ✅ 가능
var x = 10;
String y = null;  // 명시적 타입
```

**3. 제네릭 타입 명시**:
```java
// ❌ 불가능
var list = new ArrayList<>();

// ✅ 가능
var list = new ArrayList<String>();
```

---

## 🎓 Part 1 종합 정리

### 📊 var 사용 가이드

```java
// ✅ var 사용이 적합한 경우
var customerList = new ArrayList<Customer>();  // 타입이 길고 명확
var result = stream.collect(Collectors.toList());  // Stream 결과
for (var entry : map.entrySet()) { }  // 반복문

// ❌ var 사용을 피해야 하는 경우
var data = getData();  // 반환 타입 불명확
var x = 10;  // int인지 long인지 애매
List<String> list = new ArrayList<>();  // 인터페이스 타입 필요
```

---

### 🎯 var의 장단점

| 장점 | 단점 |
|------|------|
| 타입이 긴 경우 간결함 | 타입이 불명확할 수 있음 |
| 제네릭 타입 반복 제거 | 지역 변수에만 사용 가능 |
| 코드 유지보수 용이 | 초기화 필수 |
| 컴파일 시 타입 결정 | IDE 의존성 증가 |

---

### 💡 var 사용 원칙

```
1. 가독성 우선
   - 타입이 명확하지 않으면 명시적 타입 사용

2. 변수명 명확히
   - customerList, orderMap 등 타입을 유추할 수 있는 이름

3. 우변 명확성
   - new, 팩토리 메서드 등으로 타입이 드러나는 경우

4. 일관성 유지
   - 팀 코딩 컨벤션 따르기
```

**다음 Part 2에서는**: 3개 기업 사례 (카카오, 배민, 당근) + 4개 주니어 실수 시나리오를 다룹니다.
