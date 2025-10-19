# 28장 Map 인터페이스 - Part 3: 성능 최적화 & 고급 활용

## 📚 목차
1. [Map 성능 최적화 & 내부 동작 원리](#성능-최적화)
2. [고급 활용 기법](#고급-활용-기법)
3. [실전 Best Practices](#실전-best-practices)
4. [자주 묻는 면접 질문 TOP 10](#면접-질문)
5. [종합 정리](#종합-정리)

---

## 🚀 성능 최적화

### 📊 HashMap 내부 동작 원리

#### 🎯 Hash Table 구조

HashMap은 **배열 + 연결 리스트/트리**로 구성됩니다.

```
버킷 (Bucket Array)
┌─────────────────────────────────────┐
│ [0] → null                          │
│ [1] → Entry("apple", 100)           │
│ [2] → Entry("banana", 200) → Entry("orange", 150)  (충돌)
│ [3] → null                          │
│ [4] → Entry("grape", 300)           │
│ ...                                 │
│ [15] → null                         │
└─────────────────────────────────────┘
```

**핵심 개념**:
1. **Hash Function**: Key → Hash Code → Index
2. **Collision**: 서로 다른 Key가 같은 Index에 매핑
3. **Load Factor**: (저장된 Entry 수) / (버킷 크기)

#### 💻 HashMap 동작 원리 코드

```java
package map.optimization;

import java.util.*;

/**
 * HashMap 내부 동작 원리 시뮬레이션
 */
public class HashMapInternalsDemo {
    public static void main(String[] args) {
        System.out.println("=== HashMap 내부 동작 원리 ===\n");

        // 시나리오 1: Hash Code 계산
        System.out.println("📍 시나리오 1: Hash Code 계산");

        String key1 = "apple";
        String key2 = "banana";
        String key3 = "grape";

        System.out.println("\"apple\" hashCode: " + key1.hashCode());
        System.out.println("\"banana\" hashCode: " + key2.hashCode());
        System.out.println("\"grape\" hashCode: " + key3.hashCode());
        System.out.println();

        // 시나리오 2: Index 계산 (hashCode % bucketSize)
        System.out.println("📍 시나리오 2: Index 계산 (버킷 크기=16)");

        int bucketSize = 16;
        int index1 = Math.abs(key1.hashCode()) % bucketSize;
        int index2 = Math.abs(key2.hashCode()) % bucketSize;
        int index3 = Math.abs(key3.hashCode()) % bucketSize;

        System.out.println("\"apple\" → 버킷[" + index1 + "]");
        System.out.println("\"banana\" → 버킷[" + index2 + "]");
        System.out.println("\"grape\" → 버킷[" + index3 + "]");
        System.out.println("→ hashCode를 버킷 크기로 나눈 나머지");
        System.out.println();

        // 시나리오 3: Hash Collision 시뮬레이션
        System.out.println("📍 시나리오 3: Hash Collision (충돌)");

        // 작은 버킷으로 충돌 유도
        bucketSize = 4;
        Map<String, Integer> collisionMap = new HashMap<>();

        String[] keys = {"a", "e", "i", "m", "q"}; // 일부는 충돌 가능

        for (String key : keys) {
            int index = Math.abs(key.hashCode()) % bucketSize;
            collisionMap.put(key, key.hashCode());
            System.out.println("\"" + key + "\" → 버킷[" + index + "] (hashCode: " + key.hashCode() + ")");
        }

        System.out.println("→ 같은 버킷에 여러 Entry가 저장되면 연결 리스트로 관리");
        System.out.println();

        // 시나리오 4: Load Factor와 Resizing
        System.out.println("📍 시나리오 4: Load Factor와 Resizing");

        // 초기 용량 4, Load Factor 0.75
        Map<String, Integer> map = new HashMap<>(4, 0.75f);

        System.out.println("초기 버킷 크기: 4");
        System.out.println("Load Factor: 0.75");
        System.out.println("Threshold (리사이징 기준): 4 × 0.75 = 3\n");

        map.put("A", 1);
        System.out.println("A 추가 (크기: 1/4)");

        map.put("B", 2);
        System.out.println("B 추가 (크기: 2/4)");

        map.put("C", 3);
        System.out.println("C 추가 (크기: 3/4)");
        System.out.println("→ Threshold 도달! 다음 추가 시 리사이징\n");

        map.put("D", 4);
        System.out.println("D 추가 (크기: 4/8)");
        System.out.println("→ 버킷 크기가 4 → 8로 2배 증가 (리사이징)");
        System.out.println("→ 모든 Entry를 새 버킷에 재배치 (Rehashing)");
        System.out.println();

        // 시나리오 5: 성능 비교 (작은 용량 vs 적절한 용량)
        System.out.println("📍 시나리오 5: 초기 용량의 중요성");

        int elementCount = 10000;

        // 작은 초기 용량 (잦은 리사이징)
        long start1 = System.nanoTime();
        Map<Integer, Integer> smallMap = new HashMap<>(2); // 매우 작음
        for (int i = 0; i < elementCount; i++) {
            smallMap.put(i, i);
        }
        long end1 = System.nanoTime();

        // 적절한 초기 용량 (리사이징 최소화)
        long start2 = System.nanoTime();
        Map<Integer, Integer> largeMap = new HashMap<>(elementCount); // 충분함
        for (int i = 0; i < elementCount; i++) {
            largeMap.put(i, i);
        }
        long end2 = System.nanoTime();

        System.out.println("작은 초기 용량 (2): " + String.format("%.2f", (end1 - start1) / 1_000_000.0) + "ms");
        System.out.println("적절한 초기 용량 (" + elementCount + "): " + String.format("%.2f", (end2 - start2) / 1_000_000.0) + "ms");
        System.out.println("→ 초기 용량을 적절히 설정하면 리사이징 비용 절감");
        System.out.println();

        // 시나리오 6: Tree화 (Java 8+)
        System.out.println("📍 시나리오 6: Tree화 (Treeify)");

        System.out.println("한 버킷의 Entry가 8개 이상 → Red-Black Tree로 변환");
        System.out.println("→ 충돌이 많을 때 O(n) → O(log n) 성능 개선");
        System.out.println();

        System.out.println("연결 리스트 구조 (충돌 많음):");
        System.out.println("  버킷[5] → Entry1 → Entry2 → Entry3 → ... → Entry8");
        System.out.println("  조회 성능: O(n)");
        System.out.println();

        System.out.println("Tree 구조 (충돌 많음, Java 8+):");
        System.out.println("  버킷[5] → Red-Black Tree");
        System.out.println("            ├─ Entry1");
        System.out.println("            ├─ Entry2");
        System.out.println("            └─ ...");
        System.out.println("  조회 성능: O(log n)");
    }
}
```

#### 🎯 핵심 포인트

**1. HashMap의 put 과정**:
```java
// 1. hashCode() 호출
int hash = key.hashCode();

// 2. 버킷 인덱스 계산
int index = hash % bucketSize;

// 3. 버킷 위치에 저장
//    - 비어있으면: 새 Entry 생성
//    - 충돌이면: 연결 리스트에 추가 (또는 Tree)
```

**2. Load Factor 공식**:
```
Load Factor = (현재 Entry 수) / (버킷 크기)

기본값: 0.75
Threshold = 버킷 크기 × Load Factor

예: 버킷 크기 16, Load Factor 0.75
    → Threshold = 16 × 0.75 = 12
    → 12개 초과 시 리사이징 (16 → 32)
```

**3. 리사이징 비용**:
```
리사이징 시 모든 Entry를 재배치 (Rehashing)
→ O(n) 비용 발생

해결책: 초기 용량을 예상 크기로 설정
new HashMap<>(expectedSize)
```

**4. 좋은 hashCode() 조건**:
```java
// ✅ 좋은 hashCode: 고르게 분산
@Override
public int hashCode() {
    return Objects.hash(field1, field2, field3);
}

// ❌ 나쁜 hashCode: 항상 같은 값
@Override
public int hashCode() {
    return 1; // 모든 객체가 같은 버킷에 몰림 → O(n)
}
```

---

### 📊 초기 용량(Initial Capacity) 최적화

#### 🎯 문제 상황

```java
// ❌ 나쁜 예: 기본 용량(16) 사용
Map<String, Integer> map = new HashMap<>();

// 100,000개 추가
for (int i = 0; i < 100000; i++) {
    map.put("key" + i, i);
}

// 문제:
// - 16 → 32 → 64 → 128 → ... → 131072 (여러 번 리사이징)
// - 매번 모든 Entry 재배치
```

#### 💡 해결책

```java
package map.optimization;

import java.util.*;

/**
 * 초기 용량 최적화
 */
public class InitialCapacityOptimization {
    public static void main(String[] args) {
        int elementCount = 100000;

        System.out.println("=== 초기 용량 최적화 ===\n");

        // ❌ 방법 1: 기본 용량 (나쁨)
        long start1 = System.nanoTime();
        Map<Integer, String> map1 = new HashMap<>(); // 기본 용량 16

        for (int i = 0; i < elementCount; i++) {
            map1.put(i, "value" + i);
        }
        long end1 = System.nanoTime();

        // ✅ 방법 2: 정확한 초기 용량 (좋음)
        long start2 = System.nanoTime();
        // Load Factor 0.75 고려: elementCount / 0.75
        int initialCapacity = (int) (elementCount / 0.75) + 1;
        Map<Integer, String> map2 = new HashMap<>(initialCapacity);

        for (int i = 0; i < elementCount; i++) {
            map2.put(i, "value" + i);
        }
        long end2 = System.nanoTime();

        System.out.println("📊 성능 비교:");
        System.out.println("기본 용량 (16): " + String.format("%.2f", (end1 - start1) / 1_000_000.0) + "ms");
        System.out.println("최적 용량 (" + initialCapacity + "): " + String.format("%.2f", (end2 - start2) / 1_000_000.0) + "ms");
        System.out.println();

        double improvement = ((end1 - start1) - (end2 - start2)) / (double) (end1 - start1) * 100;
        System.out.println("성능 개선: " + String.format("%.1f", improvement) + "%");
        System.out.println();

        // 최적 초기 용량 계산 공식
        System.out.println("📐 최적 초기 용량 계산:");
        System.out.println("초기 용량 = (예상 크기 / Load Factor) + 1");
        System.out.println("         = (" + elementCount + " / 0.75) + 1");
        System.out.println("         = " + initialCapacity);
        System.out.println();

        // 실전 예시
        System.out.println("📍 실전 사용 예시:");
        System.out.println();

        System.out.println("// 예상 크기 1000개");
        System.out.println("int size = 1000;");
        System.out.println("Map<String, User> users = new HashMap<>((int)(size / 0.75) + 1);");
        System.out.println();

        System.out.println("// Collection 변환");
        System.out.println("List<User> userList = ...;");
        System.out.println("Map<String, User> userMap = new HashMap<>((int)(userList.size() / 0.75) + 1);");
        System.out.println("userList.forEach(user -> userMap.put(user.getId(), user));");
    }
}
```

#### 🎯 핵심 공식

```java
/**
 * 최적 초기 용량 계산
 */
public static int optimalInitialCapacity(int expectedSize) {
    return (int) (expectedSize / 0.75) + 1;
}

// 사용 예
Map<K, V> map = new HashMap<>(optimalInitialCapacity(1000));
```

---

### 📊 TreeMap 성능 최적화

#### 🎯 TreeMap vs HashMap 성능 비교

```java
package map.optimization;

import java.util.*;

/**
 * TreeMap vs HashMap 성능 비교
 */
public class TreeMapVsHashMapPerformance {
    public static void main(String[] args) {
        int elementCount = 100000;

        System.out.println("=== TreeMap vs HashMap 성능 비교 ===\n");

        // 1. 삽입 성능
        System.out.println("📍 1. 삽입 성능 (10만 개)");

        long start1 = System.nanoTime();
        Map<Integer, String> hashMap = new HashMap<>();
        for (int i = 0; i < elementCount; i++) {
            hashMap.put(i, "value" + i);
        }
        long end1 = System.nanoTime();

        long start2 = System.nanoTime();
        Map<Integer, String> treeMap = new TreeMap<>();
        for (int i = 0; i < elementCount; i++) {
            treeMap.put(i, "value" + i);
        }
        long end2 = System.nanoTime();

        System.out.println("HashMap: " + String.format("%.2f", (end1 - start1) / 1_000_000.0) + "ms (O(1))");
        System.out.println("TreeMap: " + String.format("%.2f", (end2 - start2) / 1_000_000.0) + "ms (O(log n))");
        System.out.println();

        // 2. 조회 성능
        System.out.println("📍 2. 조회 성능 (1만 번 조회)");

        Random random = new Random();

        start1 = System.nanoTime();
        for (int i = 0; i < 10000; i++) {
            hashMap.get(random.nextInt(elementCount));
        }
        end1 = System.nanoTime();

        start2 = System.nanoTime();
        for (int i = 0; i < 10000; i++) {
            treeMap.get(random.nextInt(elementCount));
        }
        end2 = System.nanoTime();

        System.out.println("HashMap: " + String.format("%.2f", (end1 - start1) / 1_000_000.0) + "ms (O(1))");
        System.out.println("TreeMap: " + String.format("%.2f", (end2 - start2) / 1_000_000.0) + "ms (O(log n))");
        System.out.println();

        // 3. 순회 성능
        System.out.println("📍 3. 순회 성능");

        start1 = System.nanoTime();
        for (Map.Entry<Integer, String> entry : hashMap.entrySet()) {
            // 아무것도 안 함
        }
        end1 = System.nanoTime();

        start2 = System.nanoTime();
        for (Map.Entry<Integer, String> entry : treeMap.entrySet()) {
            // 아무것도 안 함
        }
        end2 = System.nanoTime();

        System.out.println("HashMap: " + String.format("%.2f", (end1 - start1) / 1_000_000.0) + "ms");
        System.out.println("TreeMap: " + String.format("%.2f", (end2 - start2) / 1_000_000.0) + "ms (정렬된 순서)");
        System.out.println();

        // 4. 범위 검색 (TreeMap의 장점)
        System.out.println("📍 4. 범위 검색 (1000 ~ 2000)");

        start1 = System.nanoTime();
        // HashMap: 전체 순회 필요
        List<String> hashMapRange = new ArrayList<>();
        for (Map.Entry<Integer, String> entry : hashMap.entrySet()) {
            if (entry.getKey() >= 1000 && entry.getKey() <= 2000) {
                hashMapRange.add(entry.getValue());
            }
        }
        end1 = System.nanoTime();

        start2 = System.nanoTime();
        // TreeMap: subMap 활용
        Map<Integer, String> treeMapRange = ((TreeMap<Integer, String>) treeMap).subMap(1000, 2001);
        List<String> treeMapRangeList = new ArrayList<>(treeMapRange.values());
        end2 = System.nanoTime();

        System.out.println("HashMap (전체 순회): " + String.format("%.2f", (end1 - start1) / 1_000_000.0) + "ms");
        System.out.println("TreeMap (subMap): " + String.format("%.3f", (end2 - start2) / 1_000_000.0) + "ms");
        System.out.println("→ TreeMap이 범위 검색에서 압도적으로 빠름");
        System.out.println();

        // 결론
        System.out.println("📊 결론:");
        System.out.println("├─ 빠른 조회/삽입: HashMap (O(1))");
        System.out.println("├─ 정렬 필요: TreeMap (자동 정렬)");
        System.out.println("├─ 범위 검색: TreeMap (subMap, headMap, tailMap)");
        System.out.println("└─ 메모리 효율: HashMap (Tree 구조 오버헤드 없음)");
    }
}
```

---

## 💎 고급 활용 기법

### 🔷 기법 1: 다중 Key Map (Composite Key)

#### 🎯 문제 상황

```java
// 학생의 과목별 성적을 저장하고 싶음
// Key: 학생 ID + 과목 코드
// Value: 성적
```

#### 💡 해결책: Composite Key 사용

```java
package map.advanced;

import java.util.*;

/**
 * 복합 키 (Composite Key)
 */
class CompositeKey {
    private final String studentId;
    private final String subjectCode;

    public CompositeKey(String studentId, String subjectCode) {
        this.studentId = studentId;
        this.subjectCode = subjectCode;
    }

    public String getStudentId() { return studentId; }
    public String getSubjectCode() { return subjectCode; }

    /**
     * equals와 hashCode를 반드시 구현해야 함!
     */
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        CompositeKey that = (CompositeKey) o;

        if (!studentId.equals(that.studentId)) return false;
        return subjectCode.equals(that.subjectCode);
    }

    @Override
    public int hashCode() {
        int result = studentId.hashCode();
        result = 31 * result + subjectCode.hashCode();
        return result;
    }

    @Override
    public String toString() {
        return studentId + "-" + subjectCode;
    }
}

/**
 * 복합 키를 사용한 성적 관리
 */
public class CompositeKeyDemo {
    public static void main(String[] args) {
        System.out.println("=== 복합 키 (Composite Key) ===\n");

        Map<CompositeKey, Integer> scores = new HashMap<>();

        // 학생별 과목 성적 저장
        scores.put(new CompositeKey("S001", "MATH"), 85);
        scores.put(new CompositeKey("S001", "ENG"), 90);
        scores.put(new CompositeKey("S001", "SCI"), 88);

        scores.put(new CompositeKey("S002", "MATH"), 92);
        scores.put(new CompositeKey("S002", "ENG"), 87);
        scores.put(new CompositeKey("S002", "SCI"), 95);

        // 조회
        CompositeKey key = new CompositeKey("S001", "MATH");
        Integer score = scores.get(key);

        System.out.println("S001 학생의 수학 성적: " + score);
        System.out.println();

        // 전체 성적 출력
        System.out.println("📋 전체 성적:");
        scores.forEach((k, v) -> {
            System.out.println(k + " → " + v + "점");
        });
        System.out.println();

        // 특정 학생의 모든 성적 조회
        System.out.println("📍 S001 학생의 모든 성적:");
        scores.entrySet().stream()
            .filter(entry -> entry.getKey().getStudentId().equals("S001"))
            .forEach(entry -> {
                System.out.println("  " + entry.getKey().getSubjectCode() + ": " + entry.getValue() + "점");
            });
        System.out.println();

        // 대안: 중첩 Map
        System.out.println("📍 대안: 중첩 Map 구조");

        Map<String, Map<String, Integer>> nestedScores = new HashMap<>();

        // 학생 ID → (과목 코드 → 성적)
        nestedScores.put("S001", new HashMap<>());
        nestedScores.get("S001").put("MATH", 85);
        nestedScores.get("S001").put("ENG", 90);

        nestedScores.put("S002", new HashMap<>());
        nestedScores.get("S002").put("MATH", 92);
        nestedScores.get("S002").put("ENG", 87);

        // 조회
        Integer mathScore = nestedScores.get("S001").get("MATH");
        System.out.println("S001의 수학 성적: " + mathScore);
        System.out.println();

        // 비교
        System.out.println("📊 Composite Key vs 중첩 Map:");
        System.out.println("Composite Key:");
        System.out.println("  ✅ 단순한 구조 (Map<CompositeKey, Value>)");
        System.out.println("  ✅ 타입 안전성");
        System.out.println("  ❌ Key 클래스 작성 필요");
        System.out.println();

        System.out.println("중첩 Map:");
        System.out.println("  ✅ Key 클래스 불필요");
        System.out.println("  ✅ 특정 학생의 모든 데이터 조회 쉬움");
        System.out.println("  ❌ 복잡한 구조 (Map<K1, Map<K2, V>>)");
        System.out.println("  ❌ null 체크 필요");
    }
}
```

---

### 🔷 기법 2: 역방향 조회를 위한 BiMap (양방향 Map)

#### 🎯 문제 상황

```java
// Key → Value 조회: O(1)
// Value → Key 조회: O(n) (전체 순회 필요)

// 양방향 빠른 조회가 필요한 경우?
```

#### 💡 해결책: BiMap 구현

```java
package map.advanced;

import java.util.*;

/**
 * 양방향 Map (BiMap)
 */
class BiMap<K, V> {
    private Map<K, V> keyToValue;
    private Map<V, K> valueToKey;

    public BiMap() {
        this.keyToValue = new HashMap<>();
        this.valueToKey = new HashMap<>();
    }

    /**
     * Key-Value 추가
     */
    public void put(K key, V value) {
        // 기존 매핑 제거
        if (keyToValue.containsKey(key)) {
            V oldValue = keyToValue.get(key);
            valueToKey.remove(oldValue);
        }

        if (valueToKey.containsKey(value)) {
            K oldKey = valueToKey.get(value);
            keyToValue.remove(oldKey);
        }

        // 새 매핑 추가
        keyToValue.put(key, value);
        valueToKey.put(value, key);
    }

    /**
     * Key로 Value 조회 (O(1))
     */
    public V getValue(K key) {
        return keyToValue.get(key);
    }

    /**
     * Value로 Key 조회 (O(1)) ← 핵심!
     */
    public K getKey(V value) {
        return valueToKey.get(value);
    }

    /**
     * Key로 삭제
     */
    public V removeByKey(K key) {
        V value = keyToValue.remove(key);
        if (value != null) {
            valueToKey.remove(value);
        }
        return value;
    }

    /**
     * Value로 삭제
     */
    public K removeByValue(V value) {
        K key = valueToKey.remove(value);
        if (key != null) {
            keyToValue.remove(key);
        }
        return key;
    }

    /**
     * 크기
     */
    public int size() {
        return keyToValue.size();
    }

    /**
     * 출력
     */
    public void printAll() {
        System.out.println("Key → Value:");
        keyToValue.forEach((k, v) -> System.out.println("  " + k + " → " + v));
    }
}

/**
 * BiMap 데모
 */
public class BiMapDemo {
    public static void main(String[] args) {
        System.out.println("=== 양방향 Map (BiMap) ===\n");

        BiMap<String, String> countryCapital = new BiMap<>();

        // 국가 → 수도
        countryCapital.put("Korea", "Seoul");
        countryCapital.put("Japan", "Tokyo");
        countryCapital.put("USA", "Washington");
        countryCapital.put("France", "Paris");

        System.out.println("📍 시나리오 1: Key → Value 조회 (O(1))");
        String capital = countryCapital.getValue("Korea");
        System.out.println("Korea의 수도: " + capital);
        System.out.println();

        System.out.println("📍 시나리오 2: Value → Key 조회 (O(1))");
        String country = countryCapital.getKey("Tokyo");
        System.out.println("Tokyo는 어느 나라? " + country);
        System.out.println("→ 일반 Map은 O(n) 순회 필요, BiMap은 O(1)!");
        System.out.println();

        // 전체 출력
        System.out.println("📍 전체 매핑:");
        countryCapital.printAll();
        System.out.println();

        // 실용 예시
        System.out.println("📍 실용 예시:");
        System.out.println();

        // 사용자 ID ↔ 이메일
        BiMap<Integer, String> userIdEmail = new BiMap<>();
        userIdEmail.put(1, "user1@example.com");
        userIdEmail.put(2, "user2@example.com");
        userIdEmail.put(3, "user3@example.com");

        System.out.println("ID로 이메일 조회:");
        System.out.println("  ID 1 → " + userIdEmail.getValue(1));
        System.out.println();

        System.out.println("이메일로 ID 조회:");
        System.out.println("  user2@example.com → ID " + userIdEmail.getKey("user2@example.com"));
        System.out.println();

        // 메모리 트레이드오프
        System.out.println("📊 BiMap의 특징:");
        System.out.println("✅ Key → Value: O(1)");
        System.out.println("✅ Value → Key: O(1)");
        System.out.println("❌ 메모리: 2배 사용 (두 개의 Map)");
        System.out.println("❌ 동기화: 두 Map을 항상 일치시켜야 함");
        System.out.println();

        System.out.println("💡 사용 시기:");
        System.out.println("- 역방향 조회가 빈번한 경우");
        System.out.println("- 메모리보다 조회 속도가 중요한 경우");
        System.out.println("- 1:1 매핑이 보장되는 경우");
    }
}
```

---

### 🔷 기법 3: 그룹화 (Grouping)

#### 🎯 문제 상황

```java
// 학생 리스트를 학년별로 그룹화하고 싶음
// List<Student> → Map<Integer, List<Student>>
//                     (학년)    (학생 리스트)
```

#### 💡 해결책: Stream groupingBy 활용

```java
package map.advanced;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 학생 정보
 */
class Student {
    private String name;
    private int grade;      // 학년
    private String major;   // 전공
    private int score;      // 점수

    public Student(String name, int grade, String major, int score) {
        this.name = name;
        this.grade = grade;
        this.major = major;
        this.score = score;
    }

    public String getName() { return name; }
    public int getGrade() { return grade; }
    public String getMajor() { return major; }
    public int getScore() { return score; }

    @Override
    public String toString() {
        return String.format("%s (%d학년, %s, %d점)", name, grade, major, score);
    }
}

/**
 * 그룹화 기법
 */
public class GroupingDemo {
    public static void main(String[] args) {
        System.out.println("=== 그룹화 (Grouping) 기법 ===\n");

        List<Student> students = Arrays.asList(
            new Student("김철수", 1, "컴퓨터공학", 85),
            new Student("이영희", 2, "컴퓨터공학", 92),
            new Student("박민수", 1, "전자공학", 88),
            new Student("정지훈", 3, "컴퓨터공학", 90),
            new Student("최유리", 2, "전자공학", 87),
            new Student("한지민", 1, "컴퓨터공학", 91)
        );

        // 📍 1. 학년별 그룹화
        System.out.println("📍 1. 학년별 그룹화");

        Map<Integer, List<Student>> byGrade = students.stream()
            .collect(Collectors.groupingBy(Student::getGrade));

        byGrade.forEach((grade, studentList) -> {
            System.out.println(grade + "학년:");
            studentList.forEach(s -> System.out.println("  - " + s));
        });
        System.out.println();

        // 📍 2. 전공별 그룹화
        System.out.println("📍 2. 전공별 그룹화");

        Map<String, List<Student>> byMajor = students.stream()
            .collect(Collectors.groupingBy(Student::getMajor));

        byMajor.forEach((major, studentList) -> {
            System.out.println(major + ":");
            studentList.forEach(s -> System.out.println("  - " + s));
        });
        System.out.println();

        // 📍 3. 학년별 평균 점수
        System.out.println("📍 3. 학년별 평균 점수");

        Map<Integer, Double> avgScoreByGrade = students.stream()
            .collect(Collectors.groupingBy(
                Student::getGrade,
                Collectors.averagingInt(Student::getScore)
            ));

        avgScoreByGrade.forEach((grade, avg) -> {
            System.out.println(grade + "학년 평균: " + String.format("%.1f", avg) + "점");
        });
        System.out.println();

        // 📍 4. 학년별 학생 수
        System.out.println("📍 4. 학년별 학생 수");

        Map<Integer, Long> countByGrade = students.stream()
            .collect(Collectors.groupingBy(
                Student::getGrade,
                Collectors.counting()
            ));

        countByGrade.forEach((grade, count) -> {
            System.out.println(grade + "학년: " + count + "명");
        });
        System.out.println();

        // 📍 5. 전공별 최고 점수
        System.out.println("📍 5. 전공별 최고 점수");

        Map<String, Optional<Student>> topStudentByMajor = students.stream()
            .collect(Collectors.groupingBy(
                Student::getMajor,
                Collectors.maxBy(Comparator.comparingInt(Student::getScore))
            ));

        topStudentByMajor.forEach((major, optStudent) -> {
            optStudent.ifPresent(s -> {
                System.out.println(major + " 최고 점수: " + s.getName() + " (" + s.getScore() + "점)");
            });
        });
        System.out.println();

        // 📍 6. 다단계 그룹화 (학년 → 전공)
        System.out.println("📍 6. 다단계 그룹화 (학년 → 전공)");

        Map<Integer, Map<String, List<Student>>> multiLevel = students.stream()
            .collect(Collectors.groupingBy(
                Student::getGrade,
                Collectors.groupingBy(Student::getMajor)
            ));

        multiLevel.forEach((grade, majorMap) -> {
            System.out.println(grade + "학년:");
            majorMap.forEach((major, studentList) -> {
                System.out.println("  " + major + ":");
                studentList.forEach(s -> System.out.println("    - " + s.getName()));
            });
        });
        System.out.println();

        // 📍 7. 조건별 분할 (Partitioning)
        System.out.println("📍 7. 조건별 분할 (90점 이상/미만)");

        Map<Boolean, List<Student>> partitioned = students.stream()
            .collect(Collectors.partitioningBy(s -> s.getScore() >= 90));

        System.out.println("90점 이상:");
        partitioned.get(true).forEach(s -> System.out.println("  - " + s));

        System.out.println("\n90점 미만:");
        partitioned.get(false).forEach(s -> System.out.println("  - " + s));
    }
}
```

#### 🎯 핵심 정리

```java
// 1. 기본 그룹화
Map<K, List<T>> map = list.stream()
    .collect(Collectors.groupingBy(T::getKey));

// 2. 그룹별 집계
Map<K, Long> count = list.stream()
    .collect(Collectors.groupingBy(T::getKey, Collectors.counting()));

Map<K, Double> avg = list.stream()
    .collect(Collectors.groupingBy(T::getKey, Collectors.averagingInt(T::getValue)));

// 3. 다단계 그룹화
Map<K1, Map<K2, List<T>>> multiLevel = list.stream()
    .collect(Collectors.groupingBy(
        T::getKey1,
        Collectors.groupingBy(T::getKey2)
    ));

// 4. 조건별 분할
Map<Boolean, List<T>> partitioned = list.stream()
    .collect(Collectors.partitioningBy(condition));
```

---

## 🎯 실전 Best Practices

### ✅ 1. null 안전한 Map 사용

```java
package map.bestpractices;

import java.util.*;

public class NullSafeMapDemo {
    public static void main(String[] args) {
        System.out.println("=== null 안전한 Map 사용 ===\n");

        Map<String, Integer> map = new HashMap<>();

        // ❌ 나쁜 예: NullPointerException 가능
        /*
        Integer value = map.get("key");
        int result = value + 10; // NPE!
        */

        // ✅ 좋은 예 1: getOrDefault
        Integer value1 = map.getOrDefault("key", 0);
        int result1 = value1 + 10;
        System.out.println("getOrDefault: " + result1);

        // ✅ 좋은 예 2: Optional
        Optional<Integer> value2 = Optional.ofNullable(map.get("key"));
        int result2 = value2.orElse(0) + 10;
        System.out.println("Optional: " + result2);

        // ✅ 좋은 예 3: computeIfAbsent (지연 초기화)
        map.computeIfAbsent("key", k -> 0);
        int result3 = map.get("key") + 10;
        System.out.println("computeIfAbsent: " + result3);
        System.out.println();

        // 중첩 Map에서 안전한 접근
        System.out.println("📍 중첩 Map 안전한 접근:");

        Map<String, Map<String, Integer>> nested = new HashMap<>();

        // ❌ 나쁜 예
        /*
        Integer score = nested.get("student1").get("math"); // NPE!
        */

        // ✅ 좋은 예 1: containsKey 체크
        if (nested.containsKey("student1") && nested.get("student1").containsKey("math")) {
            Integer score = nested.get("student1").get("math");
            System.out.println("점수: " + score);
        } else {
            System.out.println("점수 없음");
        }

        // ✅ 좋은 예 2: Optional 체이닝
        Integer score = Optional.ofNullable(nested.get("student1"))
            .map(m -> m.get("math"))
            .orElse(0);
        System.out.println("Optional 체이닝: " + score);

        // ✅ 좋은 예 3: computeIfAbsent로 초기화
        nested.computeIfAbsent("student1", k -> new HashMap<>())
              .put("math", 85);
        System.out.println("computeIfAbsent: " + nested.get("student1").get("math"));
    }
}
```

---

### ✅ 2. 불변 Map 사용

```java
package map.bestpractices;

import java.util.*;

public class ImmutableMapDemo {
    public static void main(String[] args) {
        System.out.println("=== 불변 Map 사용 ===\n");

        // 1. Collections.unmodifiableMap
        Map<String, Integer> mutableMap = new HashMap<>();
        mutableMap.put("A", 1);
        mutableMap.put("B", 2);

        Map<String, Integer> unmodifiable = Collections.unmodifiableMap(mutableMap);

        System.out.println("📍 1. Collections.unmodifiableMap");
        System.out.println("unmodifiable.get(\"A\"): " + unmodifiable.get("A"));

        try {
            unmodifiable.put("C", 3);
        } catch (UnsupportedOperationException e) {
            System.out.println("❌ 수정 불가: " + e.getClass().getSimpleName());
        }
        System.out.println();

        // 2. Map.of (Java 9+)
        System.out.println("📍 2. Map.of (Java 9+)");

        Map<String, Integer> immutable1 = Map.of(
            "A", 1,
            "B", 2,
            "C", 3
        );

        System.out.println("immutable1: " + immutable1);

        try {
            immutable1.put("D", 4);
        } catch (UnsupportedOperationException e) {
            System.out.println("❌ 수정 불가: " + e.getClass().getSimpleName());
        }
        System.out.println();

        // 3. Map.ofEntries (10개 이상)
        System.out.println("📍 3. Map.ofEntries (10개 이상)");

        Map<String, Integer> immutable2 = Map.ofEntries(
            Map.entry("A", 1),
            Map.entry("B", 2),
            Map.entry("C", 3),
            Map.entry("D", 4),
            Map.entry("E", 5)
        );

        System.out.println("immutable2 크기: " + immutable2.size());
        System.out.println();

        // 4. Map.copyOf (Java 10+)
        System.out.println("📍 4. Map.copyOf (Java 10+)");

        Map<String, Integer> original = new HashMap<>();
        original.put("X", 10);
        original.put("Y", 20);

        Map<String, Integer> copy = Map.copyOf(original);

        original.put("Z", 30); // 원본 수정

        System.out.println("원본: " + original);
        System.out.println("복사본: " + copy);
        System.out.println("→ 원본 수정이 복사본에 영향 없음");
        System.out.println();

        // 사용 시기
        System.out.println("📊 불변 Map 사용 시기:");
        System.out.println("✅ 설정 값 (변경 불필요)");
        System.out.println("✅ 상수 데이터");
        System.out.println("✅ 멀티스레드 환경 (동기화 불필요)");
        System.out.println("✅ 메서드 반환값 (외부 수정 방지)");
    }
}
```

---

### ✅ 3. 동시성 안전한 Map (ConcurrentHashMap)

```java
package map.bestpractices;

import java.util.*;
import java.util.concurrent.*;

public class ConcurrentMapDemo {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== 동시성 안전한 Map ===\n");

        // ❌ 나쁜 예: HashMap (멀티스레드 환경에서 위험)
        Map<String, Integer> hashMap = new HashMap<>();

        // ✅ 좋은 예: ConcurrentHashMap
        Map<String, Integer> concurrentMap = new ConcurrentHashMap<>();

        // 시나리오: 여러 스레드가 동시에 카운터 증가
        System.out.println("📍 시나리오: 동시 카운터 증가 (10개 스레드, 각 1000번)");

        // HashMap 테스트 (동기화 없음)
        Map<String, Integer> unsafeMap = new HashMap<>();
        unsafeMap.put("counter", 0);

        ExecutorService executor1 = Executors.newFixedThreadPool(10);

        for (int i = 0; i < 10; i++) {
            executor1.submit(() -> {
                for (int j = 0; j < 1000; j++) {
                    // ❌ 동시성 문제 발생
                    Integer value = unsafeMap.get("counter");
                    unsafeMap.put("counter", value + 1);
                }
            });
        }

        executor1.shutdown();
        executor1.awaitTermination(10, TimeUnit.SECONDS);

        System.out.println("HashMap 결과 (동기화 없음): " + unsafeMap.get("counter"));
        System.out.println("예상값: 10000");
        System.out.println("→ 동시성 문제로 값이 누락됨!");
        System.out.println();

        // ConcurrentHashMap 테스트
        Map<String, Integer> safeMap = new ConcurrentHashMap<>();
        safeMap.put("counter", 0);

        ExecutorService executor2 = Executors.newFixedThreadPool(10);

        for (int i = 0; i < 10; i++) {
            executor2.submit(() -> {
                for (int j = 0; j < 1000; j++) {
                    // ✅ atomic 연산 사용
                    safeMap.compute("counter", (k, v) -> v == null ? 1 : v + 1);
                }
            });
        }

        executor2.shutdown();
        executor2.awaitTermination(10, TimeUnit.SECONDS);

        System.out.println("ConcurrentHashMap 결과: " + safeMap.get("counter"));
        System.out.println("예상값: 10000");
        System.out.println("→ 정확한 값 보장!");
        System.out.println();

        // ConcurrentHashMap의 atomic 메서드들
        System.out.println("📍 ConcurrentHashMap의 atomic 메서드:");

        ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

        // 1. putIfAbsent: 없을 때만 추가
        map.putIfAbsent("key1", 100);
        map.putIfAbsent("key1", 200); // 무시됨

        System.out.println("putIfAbsent: " + map.get("key1")); // 100

        // 2. replace: 기존 값이 있을 때만 교체
        map.replace("key1", 150);
        System.out.println("replace: " + map.get("key1")); // 150

        // 3. remove (값 확인)
        map.remove("key1", 150); // 값이 150일 때만 삭제
        System.out.println("remove: " + map.get("key1")); // null

        // 4. compute: atomic 계산
        map.put("counter", 10);
        map.compute("counter", (k, v) -> v + 5);
        System.out.println("compute: " + map.get("counter")); // 15

        System.out.println();

        // 성능 비교
        System.out.println("📊 ConcurrentHashMap vs Synchronized Map:");
        System.out.println("ConcurrentHashMap:");
        System.out.println("  ✅ 세그먼트 단위 락 (높은 동시성)");
        System.out.println("  ✅ 읽기 작업 락 없음");
        System.out.println("  ✅ atomic 메서드 제공");
        System.out.println();

        System.out.println("Collections.synchronizedMap:");
        System.out.println("  ❌ 전체 Map 락 (낮은 동시성)");
        System.out.println("  ❌ 읽기/쓰기 모두 락 필요");
        System.out.println("  ❌ atomic 메서드 없음");
    }
}
```

---

## 🎤 면접 질문

### ❓ Q1. HashMap과 TreeMap의 차이점은?

**답변**:
```
HashMap:
- 내부 구조: Hash Table (배열 + 연결 리스트/트리)
- 성능: put/get O(1)
- 순서: 없음 (입력 순서와 무관)
- null Key: 1개 허용
- 사용: 빠른 조회가 필요할 때

TreeMap:
- 내부 구조: Red-Black Tree (균형 이진 트리)
- 성능: put/get O(log n)
- 순서: Key 기준 정렬 (오름차순)
- null Key: 불가 (NullPointerException)
- 사용: 정렬된 순서, 범위 검색이 필요할 때

선택 기준:
- 정렬 필요 → TreeMap
- 빠른 조회 → HashMap
```

---

### ❓ Q2. HashMap의 초기 용량과 Load Factor는 무엇인가?

**답변**:
```
초기 용량 (Initial Capacity):
- HashMap 내부 배열(버킷)의 초기 크기
- 기본값: 16
- 지정 가능: new HashMap<>(100)

Load Factor:
- (저장된 Entry 수) / (버킷 크기) 비율
- 기본값: 0.75 (75%)
- 이 값 초과 시 리사이징 (버킷 크기 2배 증가)

예시:
버킷 크기 16, Load Factor 0.75
→ Threshold = 16 × 0.75 = 12
→ 12개 초과 시 버킷 크기 32로 증가

최적화:
예상 크기를 알면 초기 용량 지정
int capacity = (int)(expectedSize / 0.75) + 1;
Map<K, V> map = new HashMap<>(capacity);
→ 리사이징 비용 절감
```

---

### ❓ Q3. HashMap에서 Key로 사용할 객체의 조건은?

**답변**:
```
필수 조건:
1. equals()와 hashCode()를 올바르게 구현
2. equals()가 true이면 hashCode()도 같아야 함
3. 불변(immutable)이어야 함

이유:
- hashCode()로 버킷 위치 결정
- equals()로 동일한 Key 판별
- Key가 변경되면 버킷 위치가 달라져 조회 실패

예시:
class MyKey {
    private final String id; // final!

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        MyKey myKey = (MyKey) o;
        return Objects.equals(id, myKey.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}

주의:
- String, Integer 등은 이미 올바르게 구현됨
- 직접 만든 클래스는 반드시 구현 필요
```

---

### ❓ Q4. ConcurrentHashMap은 어떻게 동시성을 보장하나?

**답변**:
```
세그먼트(Segment) 기반 락:
- Map을 여러 세그먼트로 분할
- 각 세그먼트에 독립적인 락
- 다른 세그먼트는 동시 접근 가능

Java 8+ 개선:
- CAS (Compare-And-Swap) 연산 사용
- 노드 단위 락
- 읽기 작업은 락 없음

vs Collections.synchronizedMap:
synchronizedMap:
- 전체 Map에 하나의 락
- 읽기/쓰기 모두 락 필요
- 낮은 동시성

ConcurrentHashMap:
- 세그먼트/노드 단위 락
- 읽기는 락 없음
- 높은 동시성

사용:
// ❌ 나쁜 예
Map<K, V> map = Collections.synchronizedMap(new HashMap<>());

// ✅ 좋은 예
Map<K, V> map = new ConcurrentHashMap<>();
```

---

### ❓ Q5. HashMap에서 Hash Collision은 어떻게 처리하나?

**답변**:
```
Hash Collision: 서로 다른 Key가 같은 버킷에 매핑

처리 방법:
1. Separate Chaining (연결 리스트)
   - 같은 버킷의 Entry들을 연결 리스트로 관리
   - 조회 시 리스트 순회 (O(n))

2. Treeify (Java 8+)
   - 한 버킷의 Entry가 8개 이상 → Red-Black Tree로 변환
   - 조회 성능 O(n) → O(log n) 개선

예시:
버킷[5]:
- Entry 수 ≤ 7: 연결 리스트
  Entry1 → Entry2 → Entry3 → ...

- Entry 수 ≥ 8: Red-Black Tree
       Entry4
      /      \
  Entry2      Entry6
  /    \      /    \
Entry1 Entry3 Entry5 Entry7

좋은 hashCode() 필요:
- 고르게 분산 → 충돌 최소화
- Objects.hash() 사용 권장
```

---

### ❓ Q6. LinkedHashMap의 accessOrder는 무엇인가?

**답변**:
```
LinkedHashMap의 순서 유지 방식:

1. accessOrder = false (기본값)
   - 삽입 순서(insertion-order) 유지
   - put() 순서대로 순회

2. accessOrder = true
   - 접근 순서(access-order) 유지
   - get() 호출 시 해당 Entry를 맨 뒤로 이동
   - LRU 캐시 구현에 사용

예시:
LinkedHashMap<String, String> map =
    new LinkedHashMap<>(16, 0.75f, true); // accessOrder = true

map.put("A", "1");
map.put("B", "2");
map.put("C", "3");

// 순서: A, B, C

map.get("A"); // A 접근 → 맨 뒤로 이동

// 순서: B, C, A

LRU 캐시 구현:
@Override
protected boolean removeEldestEntry(Map.Entry<K,V> eldest) {
    return size() > maxSize; // 용량 초과 시 가장 오래된 Entry 제거
}
```

---

### ❓ Q7. Map.of()와 Collections.unmodifiableMap()의 차이는?

**답변**:
```
Map.of() (Java 9+):
- 진정한 불변 Map 생성
- null Key/Value 불가
- 컴파일 타임에 생성
- 메모리 효율적

Collections.unmodifiableMap():
- 기존 Map을 불변 뷰로 래핑
- 원본 Map이 변경되면 영향 받음
- null Key/Value 가능 (원본에 따라)

예시:
// Map.of()
Map<String, Integer> map1 = Map.of("A", 1, "B", 2);
// → 완전 불변, 원본 없음

// unmodifiableMap()
Map<String, Integer> original = new HashMap<>();
original.put("A", 1);
Map<String, Integer> map2 = Collections.unmodifiableMap(original);

original.put("B", 2); // 원본 변경
// → map2에도 반영됨! (뷰일 뿐)

사용:
- 완전 불변: Map.of() 또는 Map.copyOf()
- 읽기 전용 뷰: unmodifiableMap()
```

---

### ❓ Q8. getOrDefault()와 computeIfAbsent()의 차이는?

**답변**:
```
getOrDefault(key, defaultValue):
- Key가 없으면 defaultValue 반환
- Map에 추가하지 않음 (읽기 전용)

computeIfAbsent(key, mappingFunction):
- Key가 없으면 함수 실행 후 결과를 Map에 추가
- 지연 초기화에 유용

예시:
Map<String, Integer> map = new HashMap<>();

// getOrDefault
Integer value1 = map.getOrDefault("key", 0); // 0 반환
System.out.println(map.size()); // 0 (변화 없음)

// computeIfAbsent
Integer value2 = map.computeIfAbsent("key", k -> 0); // 0 반환 + 추가
System.out.println(map.size()); // 1 (추가됨)

중첩 Map 초기화:
Map<String, List<String>> map = new HashMap<>();

// ❌ 복잡
if (!map.containsKey("key")) {
    map.put("key", new ArrayList<>());
}
map.get("key").add("value");

// ✅ 간결
map.computeIfAbsent("key", k -> new ArrayList<>()).add("value");
```

---

### ❓ Q9. Map 순회 시 가장 효율적인 방법은?

**답변**:
```
1. entrySet() 사용 (✅ 가장 효율적)
for (Map.Entry<K, V> entry : map.entrySet()) {
    K key = entry.getKey();
    V value = entry.getValue();
}
→ 한 번의 순회로 Key와 Value 모두 접근

2. keySet() 사용 (❌ 비효율적)
for (K key : map.keySet()) {
    V value = map.get(key); // 추가 조회 발생!
}
→ 매번 get() 호출 (O(1)이지만 불필요)

3. forEach (Java 8+)
map.forEach((key, value) -> {
    // ...
});
→ entrySet()와 동일, 람다로 간결

4. Stream (Java 8+)
map.entrySet().stream()
   .filter(entry -> entry.getValue() > 10)
   .forEach(entry -> ...);
→ 복잡한 조건 처리에 유용

성능 비교:
entrySet(): O(n)
keySet() + get(): O(n) + n번의 get() 호출
→ entrySet()이 더 효율적
```

---

### ❓ Q10. WeakHashMap은 언제 사용하나?

**답답**:
```
WeakHashMap:
- Key를 Weak Reference로 보유
- Key가 GC되면 자동으로 Entry 제거
- 캐시 구현에 유용

일반 HashMap vs WeakHashMap:

HashMap:
Object key = new Object();
map.put(key, value);
key = null;
// → Entry가 남아있음 (GC 안 됨)

WeakHashMap:
Object key = new Object();
map.put(key, value);
key = null;
System.gc();
// → Entry가 자동 제거 (GC됨)

사용 사례:
1. 캐시
   - 객체가 살아있을 때만 캐싱
   - 메모리 부족 시 자동 제거

2. 리스너 등록
   - 리스너 객체가 GC되면 자동 해제

예시:
WeakHashMap<User, UserSession> sessions = new WeakHashMap<>();

User user = new User("kim");
sessions.put(user, new UserSession());

user = null; // User 객체 참조 제거
System.gc();
// → sessions에서도 자동 제거

주의:
- String, Integer 등은 캐싱되므로 효과 없음
- 명시적 제거가 필요하면 일반 HashMap 사용
```

---

## 🎓 종합 정리

### 📊 Map 구현체 선택 가이드

```
상황별 선택:

빠른 조회 (O(1))
└─ HashMap

정렬 필요
└─ TreeMap

삽입 순서 유지
└─ LinkedHashMap (accessOrder=false)

LRU 캐시
└─ LinkedHashMap (accessOrder=true)

멀티스레드
└─ ConcurrentHashMap

자동 메모리 관리
└─ WeakHashMap

불변
└─ Map.of() / Map.copyOf()
```

---

### 🎯 성능 최적화 체크리스트

```
✅ 초기 용량 설정
   int capacity = (int)(expectedSize / 0.75) + 1;
   new HashMap<>(capacity);

✅ Load Factor 조정 (필요시)
   - 0.75 (기본): 균형
   - 0.5: 충돌 감소, 메모리 증가
   - 1.0: 메모리 절약, 충돌 증가

✅ 좋은 hashCode() 구현
   @Override
   public int hashCode() {
       return Objects.hash(field1, field2);
   }

✅ 불변 Key 사용
   - String, Integer 등 (권장)
   - final 필드로 구성된 클래스

✅ 순회는 entrySet() 사용
   for (Map.Entry<K, V> entry : map.entrySet()) { ... }

✅ 동시성은 ConcurrentHashMap
   new ConcurrentHashMap<>();
```

---

### 💡 실전 코딩 패턴

```java
// 1. 중복 카운트
Map<String, Integer> count = new HashMap<>();
for (String word : words) {
    count.merge(word, 1, Integer::sum);
}

// 2. 그룹화
Map<String, List<User>> byCity = users.stream()
    .collect(Collectors.groupingBy(User::getCity));

// 3. null 안전 접근
Integer value = map.getOrDefault(key, 0);

// 4. 지연 초기화
map.computeIfAbsent(key, k -> new ArrayList<>()).add(value);

// 5. 조건부 업데이트
map.compute(key, (k, v) -> v == null ? 1 : v + 1);

// 6. 불변 Map 반환
public Map<String, User> getUsers() {
    return Map.copyOf(users);
}
```

---

### 🚀 다음 단계 학습

```
1. ConcurrentHashMap 심화
   - 내부 구조 (세그먼트, CAS)
   - 성능 측정 및 튜닝

2. 커스텀 Map 구현
   - AbstractMap 상속
   - 특수 목적 Map 제작

3. Guava, Apache Commons
   - Multimap, BiMap
   - 유틸리티 메서드

4. Redis, Ehcache
   - 분산 캐시
   - 대용량 처리
```

---

## 🎉 시리즈 완료!

**Part 1**: 5가지 실생활 비유로 Map 이해
**Part 2**: 3개 기업 사례 + 4개 주니어 실수
**Part 3**: 성능 최적화 + 고급 기법 + 면접 질문

Map 인터페이스를 완벽하게 마스터했습니다! 🎊

---

**참고 자료**:
- [Java HashMap 공식 문서](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html)
- [Effective Java 3rd Edition](https://www.oreilly.com/library/view/effective-java/9780134686097/)
- [Java Concurrency in Practice](https://jcip.net/)
