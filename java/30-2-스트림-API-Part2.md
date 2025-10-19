# 30장 스트림 API - Part 2: 기업 사례 & 주니어 실수

## 📚 목차
1. [기업 사례](#기업-사례)
2. [주니어 실수 시나리오](#주니어-실수-시나리오)

---

## 🏢 기업 사례

### 🔷 카카오 - 대용량 로그 분석

```java
// 1억 건의 로그에서 에러 통계 추출
List<LogEntry> errors = logs.parallelStream()
    .filter(log -> log.getLevel() == Level.ERROR)
    .collect(Collectors.toList());

Map<String, Long> errorCounts = errors.stream()
    .collect(Collectors.groupingBy(
        LogEntry::getErrorCode,
        Collectors.counting()
    ));
```

### 🔷 쿠팡 - 추천 시스템

```java
// 사용자 구매 이력에서 추천 상품 생성
List<Product> recommendations = purchaseHistory.stream()
    .flatMap(purchase -> purchase.getProducts().stream())
    .collect(Collectors.groupingBy(
        Product::getCategory,
        Collectors.counting()
    ))
    .entrySet().stream()
    .sorted(Map.Entry.<String, Long>comparingByValue().reversed())
    .limit(5)
    .map(Map.Entry::getKey)
    .flatMap(category -> productCatalog.getByCategory(category).stream())
    .filter(product -> !purchaseHistory.contains(product))
    .limit(10)
    .collect(Collectors.toList());
```

### 🔷 토스 - 실시간 거래 모니터링

```java
// 실시간 거래에서 이상 거래 탐지
List<Transaction> suspicious = transactions.stream()
    .filter(tx -> tx.getAmount() > 1_000_000)
    .filter(tx -> tx.getTime().isAfter(LocalTime.of(0, 0)))
    .filter(tx -> tx.getTime().isBefore(LocalTime.of(6, 0)))
    .filter(tx -> !tx.getUser().isVerified())
    .collect(Collectors.toList());
```

---

## 🚨 주니어 실수 시나리오

### ❌ 실수 1: 스트림 재사용

```java
// ❌ 잘못된 코드
Stream<Integer> stream = numbers.stream();
long count = stream.count();  // OK
long sum = stream.mapToInt(n -> n).sum();  // IllegalStateException!

// ✅ 올바른 코드
long count = numbers.stream().count();
long sum = numbers.stream().mapToInt(n -> n).sum();
```

### ❌ 실수 2: 무한 스트림 limit 누락

```java
// ❌ 무한 루프
Stream.iterate(0, n -> n + 1)
    .forEach(System.out::println);  // 멈추지 않음!

// ✅ limit 사용
Stream.iterate(0, n -> n + 1)
    .limit(10)
    .forEach(System.out::println);
```

### ❌ 실수 3: 병렬 스트림 남용

```java
// ❌ 소량 데이터에 병렬 스트림 (오히려 느림)
List<Integer> small = Arrays.asList(1, 2, 3, 4, 5);
small.parallelStream()  // 오버헤드가 더 큼
    .map(n -> n * 2)
    .collect(Collectors.toList());

// ✅ 대량 데이터에만 병렬 스트림
List<Integer> large = IntStream.range(0, 1_000_000)
    .boxed()
    .collect(Collectors.toList());
large.parallelStream()  // 효과적
    .map(n -> n * 2)
    .collect(Collectors.toList());
```

### ❌ 실수 4: peek을 최종 연산처럼 사용

```java
// ❌ 아무것도 출력 안 됨 (최종 연산 없음)
numbers.stream()
    .filter(n -> n > 0)
    .peek(System.out::println);  // 실행 안 됨!

// ✅ 최종 연산 추가
numbers.stream()
    .filter(n -> n > 0)
    .peek(System.out::println)
    .collect(Collectors.toList());  // 이제 실행됨
```

---

## 🎓 핵심 요약

**스트림 3대 원칙**:
1. 스트림은 재사용 불가
2. 무한 스트림은 반드시 limit
3. 병렬 스트림은 대량 데이터에만

**다음 Part 3**: 성능 최적화 + 면접 질문
