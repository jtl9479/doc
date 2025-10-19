# 30장 스트림 API - Part 3: 성능 최적화 & 면접 질문

## 📚 목차
1. [성능 최적화](#성능-최적화)
2. [면접 질문 TOP 5](#면접-질문)

---

## 🚀 성능 최적화

### 1. Primitive Stream 사용

```java
// ❌ 박싱/언박싱 발생 (느림)
List<Integer> numbers = ...;
int sum = numbers.stream()
    .reduce(0, Integer::sum);

// ✅ Primitive Stream (빠름)
int sum = numbers.stream()
    .mapToInt(Integer::intValue)
    .sum();
```

### 2. 병렬 스트림 적절히 사용

```java
// 대량 데이터 (100만 건 이상) - 병렬 효과적
list.parallelStream()
    .filter(...)
    .collect(Collectors.toList());

// 소량 데이터 - 순차가 더 빠름
list.stream()  // 병렬 X
    .filter(...)
    .collect(Collectors.toList());
```

### 3. Short-Circuit 연산 활용

```java
// anyMatch는 하나만 찾으면 종료
boolean hasEven = numbers.stream()
    .anyMatch(n -> n % 2 == 0);  // 첫 짝수 발견 시 즉시 종료

// findFirst도 Short-Circuit
Optional<Integer> first = numbers.stream()
    .filter(n -> n > 100)
    .findFirst();  // 하나 찾으면 종료
```

---

## 🎤 면접 질문 TOP 5

### Q1. 스트림과 컬렉션의 차이는?

**답변**:
```
컬렉션:
- 데이터를 메모리에 저장
- 즉시 계산 (Eager)
- 재사용 가능
- 외부 반복 (for문)

스트림:
- 데이터를 처리하는 파이프라인
- 지연 계산 (Lazy)
- 일회용 (재사용 불가)
- 내부 반복 (라이브러리가 처리)
```

### Q2. 중간 연산과 최종 연산의 차이는?

**답변**:
```
중간 연산 (Intermediate):
- Stream 반환
- 지연 실행 (Lazy)
- 체이닝 가능
- 예: filter, map, sorted

최종 연산 (Terminal):
- 결과값 반환
- 즉시 실행
- 한 번만 호출 가능
- 예: collect, forEach, count
```

### Q3. 병렬 스트림의 동작 원리는?

**답변**:
```
Fork/Join Framework 사용:
1. 작업을 작은 단위로 분할 (Fork)
2. 각 스레드가 독립적으로 처리
3. 결과를 합침 (Join)

장점:
- 멀티코어 활용
- 대량 데이터 처리 빠름

주의사항:
- 소량 데이터는 오버헤드
- 공유 변수 사용 금지
- 순서가 중요한 작업은 부적합
```

### Q4. flatMap의 용도는?

**답변**:
```
중첩 구조를 평탄화:

List<List<Integer>> nested = [[1,2], [3,4], [5,6]];

// map: Stream<List<Integer>>
nested.stream().map(list -> list)

// flatMap: Stream<Integer>
nested.stream()
    .flatMap(List::stream)  // [1,2,3,4,5,6]
    .collect(Collectors.toList());

활용:
- 중첩 컬렉션 평탄화
- Optional 체이닝
- 일대다 관계 처리
```

### Q5. Collectors의 주요 메서드는?

**답변**:
```
// 1. 수집
toList(), toSet(), toMap()

// 2. 그룹화
groupingBy(classifier)
groupingBy(classifier, downstream)

// 3. 집계
summingInt(), averagingInt()
counting(), maxBy(), minBy()

// 4. 문자열 연결
joining(delimiter)

// 5. 분할
partitioningBy(predicate)

// 예시
Map<String, List<Student>> byMajor = students.stream()
    .collect(Collectors.groupingBy(Student::getMajor));
```

---

## 🎓 종합 정리

### 스트림 Best Practices

```java
// ✅ 좋은 예
list.stream()
    .filter(조건)          // 먼저 필터링으로 데이터 줄이기
    .map(변환)             // 필요한 데이터만 변환
    .collect(toList());    // 최종 수집

// ❌ 나쁜 예
list.stream()
    .map(변환)             // 불필요한 변환
    .filter(조건)          // 늦은 필터링
    .collect(toList());
```

### 성능 체크리스트

- [ ] Primitive Stream 사용 (IntStream, LongStream)
- [ ] filter를 map보다 먼저
- [ ] 병렬 스트림은 대량 데이터에만
- [ ] Short-Circuit 연산 활용
- [ ] 스트림 재사용 금지

**시리즈 완료**: 30장 스트림 API 마스터! 🎊
