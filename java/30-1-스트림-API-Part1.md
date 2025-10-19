# 30장 스트림 API - Part 1: 실생활 비유로 이해하기

## 📚 목차
1. [비유 1: 공장 생산 라인 (파이프라인)](#비유-1-공장-생산-라인)
2. [비유 2: 필터 커피 (filter)](#비유-2-필터-커피)
3. [비유 3: 변환 작업 (map)](#비유-3-변환-작업)
4. [비유 4: 그룹화와 집계 (collect)](#비유-4-그룹화와-집계)
5. [비유 5: 병렬 처리 (parallelStream)](#비유-5-병렬-처리)

---

## 🔍 스트림 API란?

스트림(Stream)은 **컬렉션 데이터를 함수형으로 처리**하는 API입니다.

**핵심 개념**:
```java
// 전통적인 방식
List<Integer> result = new ArrayList<>();
for (Integer n : numbers) {
    if (n % 2 == 0) {
        result.add(n * 2);
    }
}

// 스트림 방식
List<Integer> result = numbers.stream()
    .filter(n -> n % 2 == 0)
    .map(n -> n * 2)
    .collect(Collectors.toList());
```

**스트림의 특징**:
```
1. 선언형: "어떻게"가 아닌 "무엇을"
2. 파이프라인: 연산을 체이닝
3. 지연 연산: 필요할 때만 계산
4. 병렬 처리: parallelStream() 지원
```

---

## 📖 비유 1: 공장 생산 라인 (파이프라인)

### 🎯 실생활 비유

공장의 생산 라인은 여러 단계를 거쳐 원자재를 제품으로 만듭니다.

**생산 라인의 단계**:
```
원자재 → [세척] → [가공] → [조립] → [검사] → [포장] → 완제품
```

스트림도 마찬가지로 **여러 연산을 연결하여 파이프라인**을 구성합니다.

### 💻 Java 코드로 구현

```java
package stream.example1;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 제품 클래스
 */
class Product {
    private String name;
    private int price;
    private String category;
    private int stock;

    public Product(String name, int price, String category, int stock) {
        this.name = name;
        this.price = price;
        this.category = category;
        this.stock = stock;
    }

    public String getName() { return name; }
    public int getPrice() { return price; }
    public String getCategory() { return category; }
    public int getStock() { return stock; }

    @Override
    public String toString() {
        return String.format("%s (%s) - %,d원 (재고: %d)", name, category, price, stock);
    }
}

/**
 * 스트림 파이프라인 데모
 */
public class StreamPipelineDemo {
    public static void main(String[] args) {
        System.out.println("=== 스트림 파이프라인 (공장 생산 라인) ===\n");

        List<Product> products = Arrays.asList(
            new Product("노트북", 1500000, "전자기기", 10),
            new Product("마우스", 30000, "전자기기", 50),
            new Product("키보드", 80000, "전자기기", 30),
            new Product("의자", 200000, "가구", 5),
            new Product("책상", 350000, "가구", 3),
            new Product("스탠드", 45000, "가구", 15)
        );

        // 시나리오 1: 전통적인 방식 (명령형)
        System.out.println("📍 시나리오 1: 전통적인 방식 (명령형)");

        List<String> result1 = new ArrayList<>();
        for (Product p : products) {
            if (p.getPrice() > 50000) {                    // 필터
                if (p.getCategory().equals("전자기기")) {   // 필터
                    String name = p.getName().toUpperCase();  // 변환
                    result1.add(name);
                }
            }
        }

        System.out.println("5만원 이상 전자기기 (대문자):");
        result1.forEach(name -> System.out.println("  " + name));
        System.out.println();

        // 시나리오 2: 스트림 방식 (선언형)
        System.out.println("📍 시나리오 2: 스트림 방식 (선언형)");

        List<String> result2 = products.stream()
            .filter(p -> p.getPrice() > 50000)           // 필터 1
            .filter(p -> p.getCategory().equals("전자기기"))  // 필터 2
            .map(p -> p.getName().toUpperCase())         // 변환
            .collect(Collectors.toList());               // 수집

        System.out.println("5만원 이상 전자기기 (대문자):");
        result2.forEach(name -> System.out.println("  " + name));
        System.out.println();

        // 시나리오 3: 파이프라인 시각화
        System.out.println("📍 시나리오 3: 파이프라인 각 단계 확인");

        List<String> result3 = products.stream()
            .peek(p -> System.out.println("  [입력] " + p.getName()))
            .filter(p -> p.getPrice() > 50000)
            .peek(p -> System.out.println("  [필터1 통과] " + p.getName()))
            .filter(p -> p.getCategory().equals("전자기기"))
            .peek(p -> System.out.println("  [필터2 통과] " + p.getName()))
            .map(p -> p.getName().toUpperCase())
            .peek(name -> System.out.println("  [변환 후] " + name))
            .collect(Collectors.toList());

        System.out.println("\n최종 결과: " + result3);
        System.out.println();

        // 시나리오 4: 복잡한 파이프라인
        System.out.println("📍 시나리오 4: 복잡한 파이프라인");

        double avgPrice = products.stream()
            .filter(p -> p.getCategory().equals("전자기기"))  // 1. 전자기기만
            .filter(p -> p.getStock() > 20)                  // 2. 재고 20개 이상
            .mapToInt(Product::getPrice)                     // 3. 가격 추출
            .average()                                       // 4. 평균 계산
            .orElse(0.0);                                    // 5. 값 없으면 0

        System.out.println("전자기기 (재고 20+) 평균 가격: " + String.format("%,.0f", avgPrice) + "원");
        System.out.println();

        // 시나리오 5: 스트림 vs for문 비교
        System.out.println("📍 시나리오 5: 가독성 비교");

        System.out.println("for문 (7줄):");
        System.out.println("  List<String> result = new ArrayList<>();");
        System.out.println("  for (Product p : products) {");
        System.out.println("      if (조건1 && 조건2) {");
        System.out.println("          result.add(변환);");
        System.out.println("      }");
        System.out.println("  }");
        System.out.println();

        System.out.println("스트림 (4줄):");
        System.out.println("  List<String> result = products.stream()");
        System.out.println("      .filter(조건1).filter(조건2)");
        System.out.println("      .map(변환)");
        System.out.println("      .collect(Collectors.toList());");
        System.out.println();

        System.out.println("💡 스트림의 장점:");
        System.out.println("✅ 간결: 코드가 짧고 명확");
        System.out.println("✅ 가독성: 의도가 분명히 드러남");
        System.out.println("✅ 재사용: 연산을 변수로 저장 가능");
        System.out.println("✅ 병렬 처리: parallelStream() 한 줄로 가능");
    }
}
```

### 🎯 핵심 포인트

**1. 스트림 생성**:
```java
// 컬렉션에서
List<Integer> list = Arrays.asList(1, 2, 3);
Stream<Integer> stream = list.stream();

// 배열에서
int[] array = {1, 2, 3};
IntStream stream = Arrays.stream(array);

// 직접 생성
Stream<String> stream = Stream.of("a", "b", "c");

// 무한 스트림
Stream<Integer> infinite = Stream.iterate(0, n -> n + 1);
```

**2. 중간 연산 (Intermediate)**:
```java
// 필터링
.filter(n -> n > 0)

// 변환
.map(s -> s.toUpperCase())

// 정렬
.sorted()

// 중복 제거
.distinct()

// 제한
.limit(10)
```

**3. 최종 연산 (Terminal)**:
```java
// 수집
.collect(Collectors.toList())

// 개수
.count()

// 순회
.forEach(System.out::println)

// 축약
.reduce(0, Integer::sum)

// 검사
.anyMatch(n -> n > 0)
```

---

## 📖 비유 2: 필터 커피 (filter)

### 🎯 실생활 비유

필터 커피는 **원하는 것만 거르고 나머지는 버립니다**.

**필터의 역할**:
```
커피 원액 + 찌꺼기 → [필터] → 순수한 커피
     (전체)           (조건)      (결과)
```

### 💻 Java 코드로 구현

```java
package stream.example2;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 학생 정보
 */
class Student {
    private String name;
    private int age;
    private int score;
    private String major;

    public Student(String name, int age, int score, String major) {
        this.name = name;
        this.age = age;
        this.score = score;
        this.major = major;
    }

    public String getName() { return name; }
    public int getAge() { return age; }
    public int getScore() { return score; }
    public String getMajor() { return major; }

    @Override
    public String toString() {
        return String.format("%s (%d세, %s전공) - %d점", name, age, major, score);
    }
}

/**
 * 필터 데모
 */
public class FilterDemo {
    public static void main(String[] args) {
        System.out.println("=== 스트림 filter (필터 커피) ===\n");

        List<Student> students = Arrays.asList(
            new Student("김철수", 20, 85, "컴퓨터공학"),
            new Student("이영희", 22, 92, "컴퓨터공학"),
            new Student("박민수", 21, 78, "전자공학"),
            new Student("정지훈", 23, 88, "컴퓨터공학"),
            new Student("최유리", 20, 95, "전자공학"),
            new Student("한지민", 22, 82, "기계공학")
        );

        // 시나리오 1: 단일 조건 필터
        System.out.println("📍 시나리오 1: 90점 이상 학생");

        List<Student> highScorers = students.stream()
            .filter(s -> s.getScore() >= 90)
            .collect(Collectors.toList());

        highScorers.forEach(s -> System.out.println("  " + s));
        System.out.println();

        // 시나리오 2: 복수 조건 필터 (AND)
        System.out.println("📍 시나리오 2: 컴퓨터공학 + 85점 이상");

        List<Student> filtered = students.stream()
            .filter(s -> s.getMajor().equals("컴퓨터공학"))
            .filter(s -> s.getScore() >= 85)
            .collect(Collectors.toList());

        filtered.forEach(s -> System.out.println("  " + s));
        System.out.println();

        // 시나리오 3: 조건 조합 (OR)
        System.out.println("📍 시나리오 3: 90점 이상 또는 컴퓨터공학");

        List<Student> orFiltered = students.stream()
            .filter(s -> s.getScore() >= 90 || s.getMajor().equals("컴퓨터공학"))
            .collect(Collectors.toList());

        orFiltered.forEach(s -> System.out.println("  " + s));
        System.out.println();

        // 시나리오 4: 범위 필터
        System.out.println("📍 시나리오 4: 나이 21~22세");

        List<Student> ageRange = students.stream()
            .filter(s -> s.getAge() >= 21 && s.getAge() <= 22)
            .collect(Collectors.toList());

        ageRange.forEach(s -> System.out.println("  " + s));
        System.out.println();

        // 시나리오 5: 복잡한 조건
        System.out.println("📍 시나리오 5: 전자공학 또는 (컴퓨터공학 + 85점 이상)");

        List<Student> complex = students.stream()
            .filter(s ->
                s.getMajor().equals("전자공학") ||
                (s.getMajor().equals("컴퓨터공학") && s.getScore() >= 85)
            )
            .collect(Collectors.toList());

        complex.forEach(s -> System.out.println("  " + s));
        System.out.println();

        // 시나리오 6: 필터 통과율
        System.out.println("📍 시나리오 6: 필터 통과율");

        long total = students.size();
        long passed = students.stream()
            .filter(s -> s.getScore() >= 80)
            .count();

        double passRate = (double) passed / total * 100;
        System.out.println("전체 학생: " + total + "명");
        System.out.println("80점 이상: " + passed + "명");
        System.out.println("통과율: " + String.format("%.1f", passRate) + "%");
    }
}
```

### 🎯 핵심 포인트

**filter 메서드**:
```java
// Predicate<T> 사용
Stream<T> filter(Predicate<T> predicate)

// 예시
stream.filter(n -> n > 0)        // 양수만
stream.filter(s -> s.length() > 3)  // 길이 3 초과
stream.filter(Objects::nonNull)  // null이 아닌 것만
```

---

## 📖 비유 3: 변환 작업 (map)

### 🎯 실생활 비유

변환은 **하나의 형태를 다른 형태로 바꾸는 작업**입니다.

**변환 예시**:
```
사과 → [주스 기계] → 사과 주스
원자재 → [가공] → 제품
```

### 💻 Java 코드로 구현

```java
package stream.example3;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 주문 정보
 */
class Order {
    private String orderId;
    private String customerName;
    private int amount;

    public Order(String orderId, String customerName, int amount) {
        this.orderId = orderId;
        this.customerName = customerName;
        this.amount = amount;
    }

    public String getOrderId() { return orderId; }
    public String getCustomerName() { return customerName; }
    public int getAmount() { return amount; }

    @Override
    public String toString() {
        return String.format("[%s] %s - %,d원", orderId, customerName, amount);
    }
}

/**
 * 맵 변환 데모
 */
public class MapDemo {
    public static void main(String[] args) {
        System.out.println("=== 스트림 map (변환 작업) ===\n");

        List<Order> orders = Arrays.asList(
            new Order("ORD001", "김철수", 50000),
            new Order("ORD002", "이영희", 75000),
            new Order("ORD003", "박민수", 30000),
            new Order("ORD004", "정지훈", 120000)
        );

        // 시나리오 1: 객체 → 특정 필드 추출
        System.out.println("📍 시나리오 1: 고객 이름만 추출");

        List<String> customerNames = orders.stream()
            .map(Order::getCustomerName)
            .collect(Collectors.toList());

        System.out.println("고객 목록: " + customerNames);
        System.out.println();

        // 시나리오 2: 숫자 변환
        System.out.println("📍 시나리오 2: 금액에 VAT 10% 추가");

        List<Integer> withVAT = orders.stream()
            .map(Order::getAmount)
            .map(amount -> (int) (amount * 1.1))
            .collect(Collectors.toList());

        System.out.println("VAT 포함 금액: " + withVAT);
        System.out.println();

        // 시나리오 3: 문자열 변환
        System.out.println("📍 시나리오 3: 주문 ID를 대문자로");

        List<String> upperIds = orders.stream()
            .map(Order::getOrderId)
            .map(String::toUpperCase)
            .collect(Collectors.toList());

        System.out.println("대문자 ID: " + upperIds);
        System.out.println();

        // 시나리오 4: 객체 → 객체 변환
        System.out.println("📍 시나리오 4: Order → 요약 정보");

        List<String> summaries = orders.stream()
            .map(o -> String.format("%s님 주문: %,d원",
                o.getCustomerName(), o.getAmount()))
            .collect(Collectors.toList());

        summaries.forEach(s -> System.out.println("  " + s));
        System.out.println();

        // 시나리오 5: flatMap (중첩 구조 평탄화)
        System.out.println("📍 시나리오 5: flatMap으로 평탄화");

        List<List<Integer>> nested = Arrays.asList(
            Arrays.asList(1, 2, 3),
            Arrays.asList(4, 5),
            Arrays.asList(6, 7, 8, 9)
        );

        List<Integer> flattened = nested.stream()
            .flatMap(List::stream)
            .collect(Collectors.toList());

        System.out.println("중첩 리스트: " + nested);
        System.out.println("평탄화: " + flattened);
        System.out.println();

        // 시나리오 6: mapToInt (기본형 변환)
        System.out.println("📍 시나리오 6: mapToInt로 합계 계산");

        int totalAmount = orders.stream()
            .mapToInt(Order::getAmount)
            .sum();

        System.out.println("총 주문 금액: " + String.format("%,d", totalAmount) + "원");
    }
}
```

### 🎯 핵심 포인트

**map 계열 메서드**:
```java
// 일반 변환
<R> Stream<R> map(Function<T, R> mapper)

// 기본형 특화
IntStream mapToInt(ToIntFunction<T> mapper)
LongStream mapToLong(ToLongFunction<T> mapper)
DoubleStream mapToDouble(ToDoubleFunction<T> mapper)

// 평탄화
<R> Stream<R> flatMap(Function<T, Stream<R>> mapper)
```

---

## 📖 비유 4: 그룹화와 집계 (collect)

### 🎯 실생활 비유

데이터를 **특정 기준으로 그룹화하고 통계를 내는 작업**입니다.

**그룹화 예시**:
```
학생들 → [학년별로 그룹화] → 1학년: [...], 2학년: [...], 3학년: [...]
```

### 💻 Java 코드로 구현

```java
package stream.example4;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 판매 데이터
 */
class Sale {
    private String product;
    private String region;
    private int quantity;
    private int price;

    public Sale(String product, String region, int quantity, int price) {
        this.product = product;
        this.region = region;
        this.quantity = quantity;
        this.price = price;
    }

    public String getProduct() { return product; }
    public String getRegion() { return region; }
    public int getQuantity() { return quantity; }
    public int getPrice() { return price; }
    public int getTotalAmount() { return quantity * price; }

    @Override
    public String toString() {
        return String.format("%s (%s지역) - %d개 × %,d원", product, region, quantity, price);
    }
}

/**
 * 수집 및 집계 데모
 */
public class CollectDemo {
    public static void main(String[] args) {
        System.out.println("=== 스트림 collect (그룹화와 집계) ===\n");

        List<Sale> sales = Arrays.asList(
            new Sale("노트북", "서울", 5, 1500000),
            new Sale("노트북", "부산", 3, 1500000),
            new Sale("마우스", "서울", 20, 30000),
            new Sale("마우스", "대구", 15, 30000),
            new Sale("키보드", "서울", 10, 80000),
            new Sale("키보드", "부산", 8, 80000)
        );

        // 시나리오 1: 리스트로 수집
        System.out.println("📍 시나리오 1: 리스트로 수집");

        List<String> products = sales.stream()
            .map(Sale::getProduct)
            .distinct()
            .collect(Collectors.toList());

        System.out.println("상품 목록: " + products);
        System.out.println();

        // 시나리오 2: 지역별 그룹화
        System.out.println("📍 시나리오 2: 지역별 그룹화");

        Map<String, List<Sale>> byRegion = sales.stream()
            .collect(Collectors.groupingBy(Sale::getRegion));

        byRegion.forEach((region, saleList) -> {
            System.out.println(region + "지역: " + saleList.size() + "건");
            saleList.forEach(s -> System.out.println("  - " + s));
        });
        System.out.println();

        // 시나리오 3: 상품별 총 판매량
        System.out.println("📍 시나리오 3: 상품별 총 판매량");

        Map<String, Integer> totalByProduct = sales.stream()
            .collect(Collectors.groupingBy(
                Sale::getProduct,
                Collectors.summingInt(Sale::getQuantity)
            ));

        totalByProduct.forEach((product, total) -> {
            System.out.println(product + ": " + total + "개");
        });
        System.out.println();

        // 시나리오 4: 지역별 매출액
        System.out.println("📍 시나리오 4: 지역별 매출액");

        Map<String, Integer> revenueByRegion = sales.stream()
            .collect(Collectors.groupingBy(
                Sale::getRegion,
                Collectors.summingInt(Sale::getTotalAmount)
            ));

        revenueByRegion.forEach((region, revenue) -> {
            System.out.println(region + "지역: " + String.format("%,d", revenue) + "원");
        });
        System.out.println();

        // 시나리오 5: 총합 계산
        System.out.println("📍 시나리오 5: 전체 매출액");

        int totalRevenue = sales.stream()
            .mapToInt(Sale::getTotalAmount)
            .sum();

        System.out.println("총 매출: " + String.format("%,d", totalRevenue) + "원");
        System.out.println();

        // 시나리오 6: 평균 계산
        System.out.println("📍 시나리오 6: 상품별 평균 단가");

        Map<String, Double> avgPrice = sales.stream()
            .collect(Collectors.groupingBy(
                Sale::getProduct,
                Collectors.averagingInt(Sale::getPrice)
            ));

        avgPrice.forEach((product, avg) -> {
            System.out.println(product + ": " + String.format("%,.0f", avg) + "원");
        });
    }
}
```

### 🎯 핵심 포인트

**Collectors 주요 메서드**:
```java
// 리스트로 수집
Collectors.toList()

// Set으로 수집
Collectors.toSet()

// Map으로 수집
Collectors.toMap(keyMapper, valueMapper)

// 그룹화
Collectors.groupingBy(classifier)

// 집계
Collectors.summingInt(mapper)
Collectors.averagingInt(mapper)
Collectors.counting()
```

---

## 📖 비유 5: 병렬 처리 (parallelStream)

### 🎯 실생활 비유

**병렬 처리**는 여러 사람이 동시에 작업하는 것과 같습니다.

**순차 vs 병렬**:
```
순차: 1명이 100개 작업 → 100분 소요
병렬: 10명이 10개씩 작업 → 10분 소요
```

### 💻 Java 코드로 구현

```java
package stream.example5;

import java.util.*;
import java.util.stream.*;

/**
 * 병렬 스트림 데모
 */
public class ParallelStreamDemo {
    public static void main(String[] args) {
        System.out.println("=== 병렬 스트림 (parallelStream) ===\n");

        // 대량 데이터 생성
        List<Integer> numbers = IntStream.rangeClosed(1, 1_000_000)
            .boxed()
            .collect(Collectors.toList());

        // 시나리오 1: 순차 스트림
        System.out.println("📍 시나리오 1: 순차 스트림");

        long start1 = System.currentTimeMillis();
        long sum1 = numbers.stream()
            .filter(n -> n % 2 == 0)
            .mapToLong(n -> n * 2)
            .sum();
        long end1 = System.currentTimeMillis();

        System.out.println("짝수의 2배 합: " + sum1);
        System.out.println("소요 시간: " + (end1 - start1) + "ms");
        System.out.println();

        // 시나리오 2: 병렬 스트림
        System.out.println("📍 시나리오 2: 병렬 스트림");

        long start2 = System.currentTimeMillis();
        long sum2 = numbers.parallelStream()  // 병렬 처리!
            .filter(n -> n % 2 == 0)
            .mapToLong(n -> n * 2)
            .sum();
        long end2 = System.currentTimeMillis();

        System.out.println("짝수의 2배 합: " + sum2);
        System.out.println("소요 시간: " + (end2 - start2) + "ms");
        System.out.println("→ 병렬 처리로 " + String.format("%.1f", (double)(end1 - start1) / (end2 - start2)) + "배 빠름");
        System.out.println();

        // 시나리오 3: 병렬 처리 주의사항
        System.out.println("📍 시나리오 3: 병렬 처리 주의사항");

        System.out.println("✅ 병렬 처리가 유리한 경우:");
        System.out.println("  - 대량 데이터 (수십만 개 이상)");
        System.out.println("  - CPU 집약적 작업");
        System.out.println("  - 독립적인 연산");
        System.out.println();

        System.out.println("❌ 병렬 처리가 불리한 경우:");
        System.out.println("  - 소량 데이터 (오버헤드 더 큼)");
        System.out.println("  - I/O 작업");
        System.out.println("  - 순서 의존적인 작업");
    }
}
```

---

## 🎓 Part 1 종합 정리

### 📊 스트림 API 구조

```
[생성] → [중간 연산] → [최종 연산]
 ↓         ↓              ↓
Stream   filter          collect
         map             forEach
         sorted          count
         distinct        reduce
```

### 💡 중간 연산 vs 최종 연산

| 구분 | 중간 연산 | 최종 연산 |
|------|----------|----------|
| **반환** | Stream | 결과값 |
| **지연** | ✅ 지연 실행 | ❌ 즉시 실행 |
| **체이닝** | ✅ 가능 | ❌ 불가 |
| **예시** | filter, map, sorted | collect, forEach, count |

**다음 Part 2에서는**: 기업 사례 + 주니어 실수를 다룹니다.
