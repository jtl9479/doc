# 28장 Map 인터페이스 - Part 1: 실생활 비유로 이해하기

## 📚 목차
1. [비유 1: 전화번호부 (HashMap)](#비유-1-전화번호부-hashmap)
2. [비유 2: 학생 성적표 (TreeMap)](#비유-2-학생-성적표-treemap)
3. [비유 3: LRU 캐시 (LinkedHashMap)](#비유-3-lru-캐시-linkedhashmap)
4. [비유 4: 단어 빈도수 계산 (HashMap)](#비유-4-단어-빈도수-계산-hashmap)
5. [비유 5: 다국어 지원 시스템 (Properties/HashMap)](#비유-5-다국어-지원-시스템-propertieshashmap)

---

## 🔍 Map 인터페이스란?

Map은 **Key-Value 쌍**으로 데이터를 저장하는 자료구조입니다.

**핵심 특징**:
```java
Map<String, Integer> map = new HashMap<>();

// Key → Value 매핑
map.put("사과", 1000);   // "사과" 키에 1000 값 저장
map.put("바나나", 1500); // "바나나" 키에 1500 값 저장

// Key로 Value 조회
int price = map.get("사과"); // 1000

// Key는 중복 불가, Value는 중복 가능
map.put("사과", 900); // "사과" 키의 값이 900으로 업데이트
```

**Map vs Set vs List**:
```
List:  [A, B, C, D]           → 순서 O, 중복 O, 인덱스 접근
Set:   {A, B, C, D}           → 중복 X, 순서는 구현체에 따라
Map:   {A→1, B→2, C→3, D→4}  → Key 중복 X, Key로 Value 접근
```

---

## 📖 비유 1: 전화번호부 (HashMap)

### 🎯 실생활 비유

전화번호부는 **이름(Key)과 전화번호(Value)를 매핑**하는 대표적인 예시입니다.

**전화번호부의 특징**:
```
이름         전화번호
────────────────────
김철수   →   010-1234-5678
이영희   →   010-2345-6789
박민수   →   010-3456-7890
```

- **이름(Key)은 유니크**: 동일한 이름은 하나만 존재
- **빠른 검색**: 이름으로 전화번호를 빠르게 찾기 (O(1))
- **순서 없음**: 가나다 순서로 저장되지 않음 (HashMap)

### 💻 Java 코드로 구현

```java
package map.example1;

import java.util.*;

/**
 * 연락처 정보
 */
class Contact {
    private String name;
    private String phoneNumber;
    private String email;
    private String address;

    public Contact(String name, String phoneNumber, String email, String address) {
        this.name = name;
        this.phoneNumber = phoneNumber;
        this.email = email;
        this.address = address;
    }

    public String getName() { return name; }
    public String getPhoneNumber() { return phoneNumber; }
    public String getEmail() { return email; }
    public String getAddress() { return address; }

    public void setPhoneNumber(String phoneNumber) { this.phoneNumber = phoneNumber; }
    public void setEmail(String email) { this.email = email; }
    public void setAddress(String address) { this.address = address; }

    @Override
    public String toString() {
        return String.format("%s: %s (이메일: %s, 주소: %s)",
            name, phoneNumber, email, address);
    }
}

/**
 * 전화번호부
 */
class PhoneBook {
    // HashMap: 이름(Key) → 연락처(Value)
    private Map<String, Contact> contacts;

    public PhoneBook() {
        this.contacts = new HashMap<>();
    }

    /**
     * 연락처 추가
     */
    public void addContact(Contact contact) {
        String name = contact.getName();

        if (contacts.containsKey(name)) {
            System.out.println("⚠️ 이미 존재하는 연락처입니다: " + name);

            // 덮어쓰기 확인
            System.out.println("기존: " + contacts.get(name));
            System.out.println("신규: " + contact);
        }

        contacts.put(name, contact);
        System.out.println("✅ 연락처 추가: " + name);
    }

    /**
     * 연락처 조회 (O(1))
     */
    public Contact findContact(String name) {
        Contact contact = contacts.get(name);

        if (contact == null) {
            System.out.println("❌ 연락처를 찾을 수 없습니다: " + name);
        }

        return contact;
    }

    /**
     * 연락처 존재 여부
     */
    public boolean hasContact(String name) {
        return contacts.containsKey(name);
    }

    /**
     * 연락처 삭제
     */
    public boolean removeContact(String name) {
        Contact removed = contacts.remove(name);

        if (removed != null) {
            System.out.println("✅ 연락처 삭제: " + name);
            return true;
        } else {
            System.out.println("❌ 삭제할 연락처가 없습니다: " + name);
            return false;
        }
    }

    /**
     * 전화번호 업데이트
     */
    public void updatePhoneNumber(String name, String newPhoneNumber) {
        Contact contact = contacts.get(name);

        if (contact != null) {
            String oldNumber = contact.getPhoneNumber();
            contact.setPhoneNumber(newPhoneNumber);
            System.out.println("✅ 전화번호 업데이트: " + name);
            System.out.println("   " + oldNumber + " → " + newPhoneNumber);
        } else {
            System.out.println("❌ 연락처를 찾을 수 없습니다: " + name);
        }
    }

    /**
     * 전체 연락처 출력
     */
    public void printAllContacts() {
        if (contacts.isEmpty()) {
            System.out.println("📭 저장된 연락처가 없습니다.");
            return;
        }

        System.out.println("\n📇 전체 연락처 (" + contacts.size() + "명):");
        System.out.println("─".repeat(60));

        for (Map.Entry<String, Contact> entry : contacts.entrySet()) {
            System.out.println(entry.getValue());
        }

        System.out.println("─".repeat(60));
    }

    /**
     * 이름으로 검색 (부분 일치)
     */
    public List<Contact> searchByName(String keyword) {
        List<Contact> results = new ArrayList<>();

        for (Contact contact : contacts.values()) {
            if (contact.getName().contains(keyword)) {
                results.add(contact);
            }
        }

        return results;
    }

    /**
     * 전화번호로 역방향 검색
     */
    public String findNameByPhoneNumber(String phoneNumber) {
        for (Map.Entry<String, Contact> entry : contacts.entrySet()) {
            if (entry.getValue().getPhoneNumber().equals(phoneNumber)) {
                return entry.getKey();
            }
        }
        return null;
    }

    /**
     * 통계 정보
     */
    public void printStatistics() {
        System.out.println("\n📊 통계:");
        System.out.println("  - 총 연락처 수: " + contacts.size() + "명");

        // 이메일 도메인별 통계
        Map<String, Integer> domainCount = new HashMap<>();

        for (Contact contact : contacts.values()) {
            String email = contact.getEmail();
            String domain = email.substring(email.indexOf('@') + 1);

            domainCount.put(domain, domainCount.getOrDefault(domain, 0) + 1);
        }

        System.out.println("  - 이메일 도메인 분포:");
        for (Map.Entry<String, Integer> entry : domainCount.entrySet()) {
            System.out.println("    " + entry.getKey() + ": " + entry.getValue() + "명");
        }
    }
}

/**
 * 전화번호부 데모
 */
public class PhoneBookDemo {
    public static void main(String[] args) {
        PhoneBook phoneBook = new PhoneBook();

        System.out.println("=== 전화번호부 시스템 (HashMap) ===\n");

        // 시나리오 1: 연락처 추가
        System.out.println("📍 시나리오 1: 연락처 추가");
        phoneBook.addContact(new Contact("김철수", "010-1234-5678", "kim@example.com", "서울시 강남구"));
        phoneBook.addContact(new Contact("이영희", "010-2345-6789", "lee@gmail.com", "서울시 서초구"));
        phoneBook.addContact(new Contact("박민수", "010-3456-7890", "park@naver.com", "경기도 성남시"));
        phoneBook.addContact(new Contact("정지훈", "010-4567-8901", "jung@example.com", "인천시 남동구"));
        System.out.println();

        // 전체 연락처 출력
        phoneBook.printAllContacts();

        // 시나리오 2: 연락처 조회 (O(1))
        System.out.println("\n📍 시나리오 2: 연락처 조회 (빠른 검색)");

        long start = System.nanoTime();
        Contact contact = phoneBook.findContact("이영희");
        long end = System.nanoTime();

        if (contact != null) {
            System.out.println("찾은 연락처: " + contact);
            System.out.println("조회 시간: " + String.format("%.3f", (end - start) / 1000.0) + "μs");
            System.out.println("→ HashMap의 O(1) 성능");
        }
        System.out.println();

        // 시나리오 3: 중복 키 처리
        System.out.println("📍 시나리오 3: 중복 키 처리 (덮어쓰기)");
        phoneBook.addContact(new Contact("김철수", "010-9999-9999", "kim_new@example.com", "부산시 해운대구"));
        System.out.println();

        Contact updated = phoneBook.findContact("김철수");
        System.out.println("업데이트된 연락처: " + updated);
        System.out.println("→ 동일한 Key는 Value를 덮어씀");
        System.out.println();

        // 시나리오 4: 전화번호 업데이트
        System.out.println("📍 시나리오 4: 전화번호 업데이트");
        phoneBook.updatePhoneNumber("박민수", "010-1111-2222");
        System.out.println();

        // 시나리오 5: 연락처 삭제
        System.out.println("📍 시나리오 5: 연락처 삭제");
        phoneBook.removeContact("정지훈");
        phoneBook.removeContact("없는사람"); // 존재하지 않는 연락처
        System.out.println();

        phoneBook.printAllContacts();

        // 시나리오 6: 이름으로 검색
        System.out.println("\n📍 시나리오 6: 이름 부분 검색");
        List<Contact> results = phoneBook.searchByName("김");
        System.out.println("'김'이 포함된 연락처: " + results.size() + "명");
        results.forEach(c -> System.out.println("  - " + c.getName()));
        System.out.println();

        // 시나리오 7: 전화번호로 역방향 검색
        System.out.println("📍 시나리오 7: 전화번호로 이름 찾기");
        String name = phoneBook.findNameByPhoneNumber("010-2345-6789");
        System.out.println("010-2345-6789의 주인: " + name);
        System.out.println("→ Value로 Key 찾기 (O(n) 순회 필요)");
        System.out.println();

        // 시나리오 8: 통계
        phoneBook.printStatistics();

        // 시나리오 9: Map의 주요 메서드
        System.out.println("\n📍 시나리오 9: Map 주요 메서드");

        // containsKey: Key 존재 여부
        System.out.println("containsKey('이영희'): " + phoneBook.hasContact("이영희"));

        // keySet: 모든 Key 조회
        System.out.print("모든 이름: ");
        for (String key : new HashMap<>(Map.of("A", 1, "B", 2)).keySet()) {
            System.out.print(key + " ");
        }
        System.out.println();

        // values: 모든 Value 조회
        System.out.println("→ keySet(), values(), entrySet() 제공");
        System.out.println();

        // 시나리오 10: 대량 데이터 성능 테스트
        System.out.println("📍 시나리오 10: 대량 데이터 성능 테스트");

        PhoneBook bigPhoneBook = new PhoneBook();

        // 10,000명 추가
        start = System.nanoTime();
        for (int i = 0; i < 10000; i++) {
            bigPhoneBook.addContact(new Contact(
                "사용자" + i,
                "010-" + String.format("%04d", i) + "-" + String.format("%04d", i),
                "user" + i + "@example.com",
                "주소" + i
            ));
        }
        end = System.nanoTime();

        System.out.println("10,000명 추가: " + String.format("%.2f", (end - start) / 1_000_000.0) + "ms");

        // 조회 성능
        start = System.nanoTime();
        Contact found = bigPhoneBook.findContact("사용자5000");
        end = System.nanoTime();

        System.out.println("조회 (10,000명 중): " + String.format("%.3f", (end - start) / 1000.0) + "μs");
        System.out.println("→ 데이터 양과 무관한 O(1) 성능");
    }
}
```

### 🎯 핵심 포인트

**1. HashMap의 Key-Value 구조**:
```java
Map<String, Contact> contacts = new HashMap<>();

// Key: 이름 (String)
// Value: 연락처 정보 (Contact 객체)

contacts.put("김철수", new Contact(...));
//       ───────       ───────────────
//         Key              Value
```

**2. O(1) 조회 성능**:
```java
// 10,000명 중에서도 즉시 찾기
Contact contact = contacts.get("김철수"); // O(1)

// vs List의 경우
// for (Contact c : list) {
//     if (c.getName().equals("김철수")) { ... }
// }
// → O(n) 성능
```

**3. 중복 Key 처리 (덮어쓰기)**:
```java
contacts.put("김철수", new Contact("010-1111-1111", ...));
contacts.put("김철수", new Contact("010-2222-2222", ...)); // 덮어씀

// 결과: "김철수" → Contact("010-2222-2222", ...)
```

**4. Key는 유니크, Value는 중복 가능**:
```java
contacts.put("김철수", new Contact("010-1234-5678", ...));
contacts.put("이영희", new Contact("010-1234-5678", ...)); // ✓ Value 중복 가능
```

---

## 📖 비유 2: 학생 성적표 (TreeMap)

### 🎯 실생활 비유

성적표는 **학번(Key)과 성적(Value)을 매핑**하되, **학번 순서대로 정렬**되어 있어야 합니다.

**성적표의 특징**:
```
학번          이름      점수
───────────────────────────
20210001  →  김철수     85
20210002  →  이영희     92
20210003  →  박민수     78
20210004  →  정지훈     88
```

- **학번순 정렬**: 항상 학번 오름차순으로 유지
- **범위 검색**: 2021학번만 조회, 상위 10%만 조회 등
- **자동 정렬**: 학생 추가 시 자동으로 정렬된 위치에 삽입

### 💻 Java 코드로 구현

```java
package map.example2;

import java.util.*;

/**
 * 학생 성적 정보
 */
class StudentScore {
    private String studentId;   // 학번
    private String name;        // 이름
    private int korean;         // 국어
    private int english;        // 영어
    private int math;           // 수학

    public StudentScore(String studentId, String name, int korean, int english, int math) {
        this.studentId = studentId;
        this.name = name;
        this.korean = korean;
        this.english = english;
        this.math = math;
    }

    public String getStudentId() { return studentId; }
    public String getName() { return name; }
    public int getKorean() { return korean; }
    public int getEnglish() { return english; }
    public int getMath() { return math; }

    /**
     * 총점
     */
    public int getTotalScore() {
        return korean + english + math;
    }

    /**
     * 평균
     */
    public double getAverageScore() {
        return getTotalScore() / 3.0;
    }

    @Override
    public String toString() {
        return String.format("[%s] %s: 국어=%d, 영어=%d, 수학=%d, 총점=%d, 평균=%.1f",
            studentId, name, korean, english, math, getTotalScore(), getAverageScore());
    }
}

/**
 * 성적 관리 시스템
 */
class ScoreManager {
    // TreeMap: 학번(Key)으로 자동 정렬
    private TreeMap<String, StudentScore> scores;

    public ScoreManager() {
        this.scores = new TreeMap<>();
    }

    /**
     * 성적 등록
     */
    public void addScore(StudentScore score) {
        String studentId = score.getStudentId();

        if (scores.containsKey(studentId)) {
            System.out.println("⚠️ 이미 등록된 학번입니다: " + studentId);
        }

        scores.put(studentId, score);
        System.out.println("✅ 성적 등록: " + score.getName() + " (" + studentId + ")");
    }

    /**
     * 성적 조회
     */
    public StudentScore getScore(String studentId) {
        return scores.get(studentId);
    }

    /**
     * 전체 성적표 출력 (학번순)
     */
    public void printAllScores() {
        if (scores.isEmpty()) {
            System.out.println("📭 등록된 성적이 없습니다.");
            return;
        }

        System.out.println("\n📋 전체 성적표 (학번순):");
        System.out.println("─".repeat(80));

        for (StudentScore score : scores.values()) {
            System.out.println(score);
        }

        System.out.println("─".repeat(80));
        System.out.println("→ TreeMap이 자동으로 학번순 정렬 유지");
    }

    /**
     * 범위 검색: 특정 학번 범위의 학생 조회
     */
    public List<StudentScore> getScoresByIdRange(String fromId, String toId) {
        // subMap: [fromId, toId) 범위의 Map 반환
        SortedMap<String, StudentScore> subMap = scores.subMap(fromId, toId + "Z");

        return new ArrayList<>(subMap.values());
    }

    /**
     * 학년별 성적 조회 (2021학번 = 2021로 시작)
     */
    public List<StudentScore> getScoresByYear(String year) {
        String fromId = year + "0000";
        String toId = year + "9999";

        return getScoresByIdRange(fromId, toId);
    }

    /**
     * 첫 번째 학생 (최소 학번)
     */
    public StudentScore getFirstStudent() {
        if (scores.isEmpty()) {
            return null;
        }

        Map.Entry<String, StudentScore> firstEntry = scores.firstEntry();
        return firstEntry.getValue();
    }

    /**
     * 마지막 학생 (최대 학번)
     */
    public StudentScore getLastStudent() {
        if (scores.isEmpty()) {
            return null;
        }

        Map.Entry<String, StudentScore> lastEntry = scores.lastEntry();
        return lastEntry.getValue();
    }

    /**
     * 특정 학번 이상의 첫 학생 (ceiling)
     */
    public StudentScore getCeilingStudent(String studentId) {
        Map.Entry<String, StudentScore> entry = scores.ceilingEntry(studentId);
        return entry != null ? entry.getValue() : null;
    }

    /**
     * 특정 학번 이하의 마지막 학생 (floor)
     */
    public StudentScore getFloorStudent(String studentId) {
        Map.Entry<String, StudentScore> entry = scores.floorEntry(studentId);
        return entry != null ? entry.getValue() : null;
    }

    /**
     * 상위 N명 조회 (총점 기준)
     */
    public List<StudentScore> getTopStudents(int n) {
        List<StudentScore> allScores = new ArrayList<>(scores.values());

        // 총점 내림차순 정렬
        allScores.sort((a, b) -> Integer.compare(b.getTotalScore(), a.getTotalScore()));

        return allScores.subList(0, Math.min(n, allScores.size()));
    }

    /**
     * 평균 계산
     */
    public double calculateClassAverage() {
        if (scores.isEmpty()) {
            return 0.0;
        }

        int totalSum = 0;
        for (StudentScore score : scores.values()) {
            totalSum += score.getTotalScore();
        }

        return (double) totalSum / scores.size() / 3.0;
    }

    /**
     * 통계 정보
     */
    public void printStatistics() {
        if (scores.isEmpty()) {
            System.out.println("📊 통계: 데이터 없음");
            return;
        }

        System.out.println("\n📊 성적 통계:");
        System.out.println("  - 총 학생 수: " + scores.size() + "명");
        System.out.println("  - 학급 평균: " + String.format("%.1f", calculateClassAverage()) + "점");

        StudentScore first = getFirstStudent();
        StudentScore last = getLastStudent();

        System.out.println("  - 최소 학번: " + first.getStudentId() + " (" + first.getName() + ")");
        System.out.println("  - 최대 학번: " + last.getStudentId() + " (" + last.getName() + ")");

        // 최고 점수
        List<StudentScore> topStudents = getTopStudents(1);
        if (!topStudents.isEmpty()) {
            StudentScore top = topStudents.get(0);
            System.out.println("  - 최고 점수: " + top.getName() + " (" +
                top.getTotalScore() + "점)");
        }
    }
}

/**
 * 성적 관리 시스템 데모
 */
public class ScoreManagerDemo {
    public static void main(String[] args) {
        ScoreManager manager = new ScoreManager();

        System.out.println("=== 학생 성적 관리 시스템 (TreeMap) ===\n");

        // 시나리오 1: 성적 등록 (순서 없이 추가)
        System.out.println("📍 시나리오 1: 성적 등록 (무작위 순서)");
        manager.addScore(new StudentScore("20210003", "박민수", 85, 78, 92));
        manager.addScore(new StudentScore("20210001", "김철수", 90, 85, 88));
        manager.addScore(new StudentScore("20210005", "최유리", 88, 92, 85));
        manager.addScore(new StudentScore("20210002", "이영희", 92, 88, 95));
        manager.addScore(new StudentScore("20210004", "정지훈", 78, 82, 80));
        System.out.println();

        // 자동 정렬 확인
        manager.printAllScores();

        // 시나리오 2: 범위 검색
        System.out.println("\n📍 시나리오 2: 범위 검색 (20210002 ~ 20210004)");
        List<StudentScore> rangeScores = manager.getScoresByIdRange("20210002", "20210004");

        System.out.println("조회된 학생: " + rangeScores.size() + "명");
        for (StudentScore score : rangeScores) {
            System.out.println("  - " + score);
        }
        System.out.println("→ TreeMap의 subMap() 활용");
        System.out.println();

        // 시나리오 3: 2022학번 추가
        System.out.println("📍 시나리오 3: 2022학번 추가");
        manager.addScore(new StudentScore("20220001", "한지민", 95, 90, 92));
        manager.addScore(new StudentScore("20220002", "강호동", 82, 85, 88));
        System.out.println();

        manager.printAllScores();

        // 시나리오 4: 학년별 조회
        System.out.println("\n📍 시나리오 4: 학년별 조회");

        List<StudentScore> year2021 = manager.getScoresByYear("2021");
        System.out.println("2021학번: " + year2021.size() + "명");
        year2021.forEach(s -> System.out.println("  - " + s.getName()));

        List<StudentScore> year2022 = manager.getScoresByYear("2022");
        System.out.println("2022학번: " + year2022.size() + "명");
        year2022.forEach(s -> System.out.println("  - " + s.getName()));
        System.out.println();

        // 시나리오 5: 첫/마지막 학생
        System.out.println("📍 시나리오 5: 첫/마지막 학생");

        StudentScore first = manager.getFirstStudent();
        StudentScore last = manager.getLastStudent();

        System.out.println("최소 학번: " + first);
        System.out.println("최대 학번: " + last);
        System.out.println("→ TreeMap의 firstEntry() / lastEntry()");
        System.out.println();

        // 시나리오 6: ceiling / floor
        System.out.println("📍 시나리오 6: ceiling / floor");

        StudentScore ceiling = manager.getCeilingStudent("20210002");
        System.out.println("20210002 이상 첫 학생 (ceiling): " + ceiling.getName());

        StudentScore floor = manager.getFloorStudent("20210004");
        System.out.println("20210004 이하 마지막 학생 (floor): " + floor.getName());
        System.out.println();

        // 시나리오 7: 상위 3명
        System.out.println("📍 시나리오 7: 상위 3명 (총점 기준)");
        List<StudentScore> topStudents = manager.getTopStudents(3);

        for (int i = 0; i < topStudents.size(); i++) {
            StudentScore student = topStudents.get(i);
            System.out.println((i + 1) + "위: " + student.getName() +
                " (" + student.getTotalScore() + "점)");
        }
        System.out.println();

        // 시나리오 8: 통계
        manager.printStatistics();

        // 시나리오 9: TreeMap vs HashMap 비교
        System.out.println("\n📍 시나리오 9: TreeMap vs HashMap");

        // HashMap: 순서 없음
        Map<String, String> hashMap = new HashMap<>();
        hashMap.put("20210003", "C");
        hashMap.put("20210001", "A");
        hashMap.put("20210002", "B");

        System.out.println("HashMap 출력 (순서 없음):");
        hashMap.forEach((k, v) -> System.out.print(k + " "));
        System.out.println();

        // TreeMap: 자동 정렬
        Map<String, String> treeMap = new TreeMap<>();
        treeMap.put("20210003", "C");
        treeMap.put("20210001", "A");
        treeMap.put("20210002", "B");

        System.out.println("TreeMap 출력 (정렬됨):");
        treeMap.forEach((k, v) -> System.out.print(k + " "));
        System.out.println();
        System.out.println("→ TreeMap은 항상 Key 정렬 순서 유지");
    }
}
```

### 🎯 핵심 포인트

**1. TreeMap의 자동 정렬**:
```java
TreeMap<String, StudentScore> scores = new TreeMap<>();

// 순서 없이 추가
scores.put("20210003", ...);
scores.put("20210001", ...);
scores.put("20210002", ...);

// 출력 시 자동 정렬
for (String key : scores.keySet()) {
    System.out.println(key); // 20210001, 20210002, 20210003
}
```

**2. 범위 검색 (subMap)**:
```java
// 20210002 ~ 20210004 범위 조회
SortedMap<String, StudentScore> subMap = scores.subMap("20210002", "20210005");

// O(log n + m) 성능 (m = 결과 크기)
// HashMap으로는 O(n) 전체 순회 필요
```

**3. TreeMap 특수 메서드**:
```java
// 최소/최대 Key
String firstKey = scores.firstKey();       // 20210001
String lastKey = scores.lastKey();         // 20220002

// Entry로 조회
Map.Entry<String, StudentScore> firstEntry = scores.firstEntry();
Map.Entry<String, StudentScore> lastEntry = scores.lastEntry();

// ceiling: key 이상의 최소 Key
String ceiling = scores.ceilingKey("20210002"); // 20210002

// floor: key 이하의 최대 Key
String floor = scores.floorKey("20210004"); // 20210004
```

**4. 성능 비교**:
| 연산 | HashMap | TreeMap |
|------|---------|---------|
| put | O(1) | O(log n) |
| get | O(1) | O(log n) |
| 순회 | O(n) | O(n) |
| 정렬 | ❌ | ✅ 자동 |
| 범위 검색 | O(n) | O(log n + m) |

---

## 📖 비유 3: LRU 캐시 (LinkedHashMap)

### 🎯 실생활 비유

LRU (Least Recently Used) 캐시는 **최근에 사용하지 않은 항목을 자동으로 제거**하는 시스템입니다.

**LRU 캐시의 동작**:
```
캐시 크기: 3
접근 순서: A → B → C → D

상태 변화:
1. A 접근   →  [A]
2. B 접근   →  [A, B]
3. C 접근   →  [A, B, C]
4. D 접근   →  [B, C, D]  ← A 제거 (가장 오래 미사용)
5. B 접근   →  [C, D, B]  ← B를 맨 뒤로 이동
```

- **용량 제한**: 최대 N개만 저장
- **자동 제거**: 용량 초과 시 가장 오래된 항목 제거
- **접근 시 업데이트**: 사용한 항목은 최신으로 갱신

### 💻 Java 코드로 구현

```java
package map.example3;

import java.util.*;

/**
 * LRU 캐시 (LinkedHashMap 활용)
 */
class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int maxSize;
    private int hitCount = 0;
    private int missCount = 0;

    /**
     * @param maxSize 최대 캐시 크기
     */
    public LRUCache(int maxSize) {
        // accessOrder = true: 접근 순서로 정렬
        super(16, 0.75f, true);
        this.maxSize = maxSize;
    }

    /**
     * 용량 초과 시 가장 오래된 Entry 제거
     */
    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        boolean shouldRemove = size() > maxSize;

        if (shouldRemove) {
            System.out.println("🗑️ LRU 제거: " + eldest.getKey());
        }

        return shouldRemove;
    }

    /**
     * 캐시 조회 (통계 포함)
     */
    public V getWithStats(K key) {
        V value = super.get(key);

        if (value != null) {
            hitCount++;
            System.out.println("✅ 캐시 HIT: " + key);
        } else {
            missCount++;
            System.out.println("❌ 캐시 MISS: " + key);
        }

        return value;
    }

    /**
     * 캐시 통계
     */
    public void printStatistics() {
        int total = hitCount + missCount;
        double hitRate = total > 0 ? (double) hitCount / total * 100 : 0;

        System.out.println("\n📊 캐시 통계:");
        System.out.println("  - Hit: " + hitCount + "회");
        System.out.println("  - Miss: " + missCount + "회");
        System.out.println("  - Hit Rate: " + String.format("%.1f", hitRate) + "%");
        System.out.println("  - 현재 크기: " + size() + "/" + maxSize);
    }

    /**
     * 현재 캐시 상태 출력
     */
    public void printCacheState() {
        System.out.print("캐시 상태 [");

        int index = 0;
        for (K key : keySet()) {
            System.out.print(key);
            if (index < size() - 1) {
                System.out.print(" → ");
            }
            index++;
        }

        System.out.println("] (오래된 순 → 최신 순)");
    }
}

/**
 * 페이지 정보
 */
class Page {
    private String url;
    private String title;
    private String content;
    private long loadTime;

    public Page(String url, String title, String content, long loadTime) {
        this.url = url;
        this.title = title;
        this.content = content;
        this.loadTime = loadTime;
    }

    public String getUrl() { return url; }
    public String getTitle() { return title; }
    public long getLoadTime() { return loadTime; }

    @Override
    public String toString() {
        return String.format("%s (%dms)", title, loadTime);
    }
}

/**
 * 웹 브라우저 캐시 시뮬레이터
 */
class WebBrowserCache {
    private LRUCache<String, Page> cache;

    public WebBrowserCache(int cacheSize) {
        this.cache = new LRUCache<>(cacheSize);
    }

    /**
     * 페이지 로드 (캐시 활용)
     */
    public Page loadPage(String url) {
        System.out.println("\n🌐 페이지 요청: " + url);

        // 1. 캐시 확인
        Page cachedPage = cache.getWithStats(url);

        if (cachedPage != null) {
            // 캐시 HIT
            System.out.println("→ 캐시에서 로드: " + cachedPage.getTitle() +
                " (0ms)");
            return cachedPage;
        }

        // 2. 캐시 MISS → 서버에서 로드
        Page page = fetchFromServer(url);

        // 3. 캐시에 저장
        cache.put(url, page);
        System.out.println("→ 서버에서 로드: " + page.getTitle() +
            " (" + page.getLoadTime() + "ms)");
        System.out.println("→ 캐시에 저장");

        return page;
    }

    /**
     * 서버에서 페이지 가져오기 (시뮬레이션)
     */
    private Page fetchFromServer(String url) {
        // 로딩 시간 시뮬레이션
        long loadTime = 100 + (long) (Math.random() * 200);

        try {
            Thread.sleep(loadTime);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        // 페이지 생성
        String title = "페이지: " + url;
        String content = "내용...";

        return new Page(url, title, content, loadTime);
    }

    /**
     * 캐시 상태 출력
     */
    public void printCacheState() {
        cache.printCacheState();
    }

    /**
     * 통계 출력
     */
    public void printStatistics() {
        cache.printStatistics();
    }
}

/**
 * LRU 캐시 데모
 */
public class LRUCacheDemo {
    public static void main(String[] args) {
        System.out.println("=== LRU 캐시 시스템 (LinkedHashMap) ===\n");

        // 시나리오 1: 기본 LRU 동작
        System.out.println("📍 시나리오 1: 기본 LRU 동작 (크기=3)");

        LRUCache<String, String> cache = new LRUCache<>(3);

        cache.put("A", "Page A");
        cache.printCacheState();

        cache.put("B", "Page B");
        cache.printCacheState();

        cache.put("C", "Page C");
        cache.printCacheState();

        System.out.println("\n용량 초과 → 가장 오래된 항목 제거:");
        cache.put("D", "Page D");
        cache.printCacheState();
        System.out.println("→ A 제거됨 (가장 오래 미사용)");

        // 시나리오 2: 접근 시 순서 변경
        System.out.println("\n📍 시나리오 2: 접근 시 순서 변경");

        System.out.println("\nB 접근:");
        cache.get("B");
        cache.printCacheState();
        System.out.println("→ B가 맨 뒤로 이동 (최근 사용)");

        System.out.println("\nE 추가:");
        cache.put("E", "Page E");
        cache.printCacheState();
        System.out.println("→ C 제거됨 (가장 오래 미사용)");

        // 시나리오 3: 웹 브라우저 캐시
        System.out.println("\n📍 시나리오 3: 웹 브라우저 캐시 시뮬레이션");

        WebBrowserCache browserCache = new WebBrowserCache(3);

        // 페이지 로드
        browserCache.loadPage("/home");
        browserCache.printCacheState();

        browserCache.loadPage("/about");
        browserCache.printCacheState();

        browserCache.loadPage("/contact");
        browserCache.printCacheState();

        // 캐시 HIT
        System.out.println("\n[캐시에 있는 페이지 재요청]");
        browserCache.loadPage("/home");
        browserCache.printCacheState();

        // 캐시 용량 초과
        System.out.println("\n[새 페이지 요청 → 용량 초과]");
        browserCache.loadPage("/products");
        browserCache.printCacheState();

        // 통계
        browserCache.printStatistics();

        // 시나리오 4: 성능 비교
        System.out.println("\n📍 시나리오 4: 캐시 성능 비교");

        WebBrowserCache perfCache = new WebBrowserCache(5);

        // 10번 요청 (5개 페이지를 반복)
        String[] urls = {"/page1", "/page2", "/page3", "/page4", "/page5"};

        long startWithCache = System.currentTimeMillis();

        for (int i = 0; i < 20; i++) {
            String url = urls[i % urls.length];
            perfCache.loadPage(url);
        }

        long endWithCache = System.currentTimeMillis();

        System.out.println("\n총 소요 시간: " + (endWithCache - startWithCache) + "ms");
        perfCache.printStatistics();

        System.out.println("\n→ 캐시 HIT 시 0ms, MISS 시 100~300ms");
        System.out.println("→ 캐시 덕분에 전체 로딩 시간 대폭 감소");
    }
}
```

### 🎯 핵심 포인트

**1. LinkedHashMap의 accessOrder**:
```java
// accessOrder = false (기본): 삽입 순서 유지
LinkedHashMap<String, String> insertionOrder = new LinkedHashMap<>();

// accessOrder = true: 접근 순서 유지
LinkedHashMap<String, String> accessOrder = new LinkedHashMap<>(16, 0.75f, true);

accessOrder.put("A", "1");
accessOrder.put("B", "2");
accessOrder.put("C", "3");

accessOrder.get("A"); // A 접근 → 맨 뒤로 이동

// 순회 순서: B, C, A
```

**2. removeEldestEntry 오버라이드**:
```java
@Override
protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
    return size() > maxSize;
    // true 반환 시 eldest (가장 오래된 Entry) 제거
}
```

**3. LRU 캐시 동작**:
```
초기: [A, B, C]  (용량=3)

D 추가:
  → 용량 초과 (4 > 3)
  → A 제거 (가장 오래된 항목)
  → [B, C, D]

B 접근:
  → B를 맨 뒤로 이동
  → [C, D, B]

E 추가:
  → 용량 초과
  → C 제거
  → [D, B, E]
```

**4. 캐시 적중률 (Hit Rate)**:
```java
Hit Rate = (Hit 횟수) / (전체 요청 횟수) × 100%

// 예시:
// Hit: 15회, Miss: 5회
// Hit Rate: 15 / 20 × 100% = 75%

// 높은 Hit Rate = 효율적인 캐시
```

---

## 📖 비유 4: 단어 빈도수 계산 (HashMap)

### 🎯 실생활 비유

문서에서 **각 단어가 몇 번 나타났는지 세는 작업**은 Map의 대표적인 활용 사례입니다.

**단어 빈도수 계산**:
```
텍스트: "apple banana apple orange banana apple"

결과:
apple  → 3
banana → 2
orange → 1
```

- **Key**: 단어
- **Value**: 출현 횟수
- **중복 Key 처리**: 기존 카운트에 +1

### 💻 Java 코드로 구현

```java
package map.example4;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 단어 빈도수 분석기
 */
class WordFrequencyAnalyzer {
    private Map<String, Integer> wordFrequency;

    public WordFrequencyAnalyzer() {
        this.wordFrequency = new HashMap<>();
    }

    /**
     * 텍스트 분석
     */
    public void analyze(String text) {
        // 1. 소문자 변환 및 특수문자 제거
        String cleanedText = text.toLowerCase()
            .replaceAll("[^a-z0-9\\s]", "");

        // 2. 단어 분리
        String[] words = cleanedText.split("\\s+");

        // 3. 빈도수 계산
        for (String word : words) {
            if (word.isEmpty()) {
                continue;
            }

            // ✅ getOrDefault: Key가 없으면 기본값 반환
            int count = wordFrequency.getOrDefault(word, 0);
            wordFrequency.put(word, count + 1);
        }
    }

    /**
     * 방법 2: compute 사용
     */
    public void analyzeWithCompute(String text) {
        String cleanedText = text.toLowerCase().replaceAll("[^a-z0-9\\s]", "");
        String[] words = cleanedText.split("\\s+");

        for (String word : words) {
            if (word.isEmpty()) {
                continue;
            }

            // ✅ compute: 기존 값을 기준으로 새 값 계산
            wordFrequency.compute(word, (k, v) -> v == null ? 1 : v + 1);
        }
    }

    /**
     * 방법 3: merge 사용
     */
    public void analyzeWithMerge(String text) {
        String cleanedText = text.toLowerCase().replaceAll("[^a-z0-9\\s]", "");
        String[] words = cleanedText.split("\\s+");

        for (String word : words) {
            if (word.isEmpty()) {
                continue;
            }

            // ✅ merge: Key가 없으면 값 추가, 있으면 함수 적용
            wordFrequency.merge(word, 1, Integer::sum);
        }
    }

    /**
     * 특정 단어 빈도 조회
     */
    public int getFrequency(String word) {
        return wordFrequency.getOrDefault(word.toLowerCase(), 0);
    }

    /**
     * 가장 많이 나온 단어 TOP N
     */
    public List<Map.Entry<String, Integer>> getTopWords(int n) {
        return wordFrequency.entrySet().stream()
            .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
            .limit(n)
            .collect(Collectors.toList());
    }

    /**
     * 빈도수가 N 이상인 단어
     */
    public List<String> getWordsWithMinFrequency(int minFrequency) {
        return wordFrequency.entrySet().stream()
            .filter(entry -> entry.getValue() >= minFrequency)
            .map(Map.Entry::getKey)
            .sorted()
            .collect(Collectors.toList());
    }

    /**
     * 전체 단어 수 (중복 포함)
     */
    public int getTotalWords() {
        return wordFrequency.values().stream()
            .mapToInt(Integer::intValue)
            .sum();
    }

    /**
     * 유니크 단어 수
     */
    public int getUniqueWords() {
        return wordFrequency.size();
    }

    /**
     * 결과 출력
     */
    public void printResults() {
        if (wordFrequency.isEmpty()) {
            System.out.println("📭 분석된 데이터가 없습니다.");
            return;
        }

        System.out.println("\n📊 단어 빈도수 분석 결과:");
        System.out.println("─".repeat(60));
        System.out.println("총 단어 수: " + getTotalWords() + "개");
        System.out.println("유니크 단어 수: " + getUniqueWords() + "개");
        System.out.println("─".repeat(60));

        // 빈도수순 정렬
        List<Map.Entry<String, Integer>> sortedEntries = new ArrayList<>(wordFrequency.entrySet());
        sortedEntries.sort(Map.Entry.<String, Integer>comparingByValue().reversed());

        int rank = 1;
        for (Map.Entry<String, Integer> entry : sortedEntries) {
            System.out.println(rank + ". " + entry.getKey() +
                " → " + entry.getValue() + "회");
            rank++;

            if (rank > 20) { // 상위 20개만
                System.out.println("...");
                break;
            }
        }

        System.out.println("─".repeat(60));
    }

    /**
     * 통계 정보
     */
    public void printStatistics() {
        if (wordFrequency.isEmpty()) {
            return;
        }

        System.out.println("\n📈 통계:");

        // 평균 빈도수
        double avgFrequency = (double) getTotalWords() / getUniqueWords();
        System.out.println("  - 평균 빈도수: " + String.format("%.2f", avgFrequency));

        // 최고/최저 빈도수
        int maxFrequency = wordFrequency.values().stream().mapToInt(Integer::intValue).max().orElse(0);
        int minFrequency = wordFrequency.values().stream().mapToInt(Integer::intValue).min().orElse(0);

        System.out.println("  - 최고 빈도수: " + maxFrequency);
        System.out.println("  - 최저 빈도수: " + minFrequency);

        // 1회만 나온 단어
        long onceCount = wordFrequency.values().stream().filter(v -> v == 1).count();
        System.out.println("  - 1회만 나온 단어: " + onceCount + "개");
    }

    /**
     * 초기화
     */
    public void clear() {
        wordFrequency.clear();
    }
}

/**
 * 단어 빈도수 분석 데모
 */
public class WordFrequencyDemo {
    public static void main(String[] args) {
        WordFrequencyAnalyzer analyzer = new WordFrequencyAnalyzer();

        System.out.println("=== 단어 빈도수 분석 시스템 (HashMap) ===\n");

        // 시나리오 1: 간단한 텍스트 분석
        System.out.println("📍 시나리오 1: 간단한 텍스트 분석");

        String text1 = "apple banana apple orange banana apple";
        analyzer.analyze(text1);

        System.out.println("입력: " + text1);
        analyzer.printResults();

        // 시나리오 2: getOrDefault 패턴
        System.out.println("\n📍 시나리오 2: getOrDefault vs compute vs merge");

        Map<String, Integer> map1 = new HashMap<>();
        Map<String, Integer> map2 = new HashMap<>();
        Map<String, Integer> map3 = new HashMap<>();

        String[] words = {"apple", "banana", "apple"};

        // 방법 1: getOrDefault
        for (String word : words) {
            int count = map1.getOrDefault(word, 0);
            map1.put(word, count + 1);
        }
        System.out.println("getOrDefault: " + map1);

        // 방법 2: compute
        for (String word : words) {
            map2.compute(word, (k, v) -> v == null ? 1 : v + 1);
        }
        System.out.println("compute: " + map2);

        // 방법 3: merge (가장 간결)
        for (String word : words) {
            map3.merge(word, 1, Integer::sum);
        }
        System.out.println("merge: " + map3);
        System.out.println("→ merge가 가장 간결하고 읽기 쉬움");

        // 시나리오 3: 실제 문장 분석
        System.out.println("\n📍 시나리오 3: 실제 문장 분석");

        analyzer.clear();

        String text2 = """
            Java is a powerful programming language.
            Java is widely used for enterprise applications.
            Programming in Java is fun and Java has a large community.
            """;

        analyzer.analyze(text2);
        analyzer.printResults();
        analyzer.printStatistics();

        // 시나리오 4: TOP 5 단어
        System.out.println("\n📍 시나리오 4: TOP 5 단어");

        List<Map.Entry<String, Integer>> topWords = analyzer.getTopWords(5);

        for (int i = 0; i < topWords.size(); i++) {
            Map.Entry<String, Integer> entry = topWords.get(i);
            System.out.println((i + 1) + ". " + entry.getKey() +
                " (" + entry.getValue() + "회)");
        }

        // 시나리오 5: 빈도수 필터링
        System.out.println("\n📍 시나리오 5: 2회 이상 나온 단어");

        List<String> frequentWords = analyzer.getWordsWithMinFrequency(2);
        System.out.println("2회 이상: " + frequentWords);

        // 시나리오 6: 대량 텍스트 성능 테스트
        System.out.println("\n📍 시나리오 6: 대량 텍스트 성능 테스트");

        WordFrequencyAnalyzer perfAnalyzer = new WordFrequencyAnalyzer();

        // 100만 단어 생성
        StringBuilder bigText = new StringBuilder();
        Random random = new Random();
        String[] vocabulary = {"apple", "banana", "orange", "grape", "melon",
            "java", "python", "javascript", "ruby", "go"};

        for (int i = 0; i < 1_000_000; i++) {
            bigText.append(vocabulary[random.nextInt(vocabulary.length)]).append(" ");
        }

        long start = System.nanoTime();
        perfAnalyzer.analyze(bigText.toString());
        long end = System.nanoTime();

        System.out.println("100만 단어 분석: " + String.format("%.2f", (end - start) / 1_000_000.0) + "ms");
        System.out.println("유니크 단어: " + perfAnalyzer.getUniqueWords() + "개");
        System.out.println("→ HashMap의 O(1) 연산으로 빠른 처리");

        // 특정 단어 조회 성능
        start = System.nanoTime();
        int appleCount = perfAnalyzer.getFrequency("apple");
        end = System.nanoTime();

        System.out.println("'apple' 빈도 조회: " + appleCount + "회 (" +
            String.format("%.3f", (end - start) / 1000.0) + "μs)");
        System.out.println("→ O(1) 조회 성능");
    }
}
```

### 🎯 핵심 포인트

**1. 중복 Key 업데이트 패턴**:
```java
// 방법 1: getOrDefault (전통적)
int count = map.getOrDefault(key, 0);
map.put(key, count + 1);

// 방법 2: compute (함수형)
map.compute(key, (k, v) -> v == null ? 1 : v + 1);

// 방법 3: merge (가장 간결) ✅
map.merge(key, 1, Integer::sum);
```

**2. Map의 함수형 메서드**:
```java
// compute: Key에 대한 값을 계산
map.compute("apple", (k, v) -> {
    return v == null ? 1 : v + 1;
});

// computeIfAbsent: Key가 없을 때만 계산
map.computeIfAbsent("apple", k -> 0);

// computeIfPresent: Key가 있을 때만 계산
map.computeIfPresent("apple", (k, v) -> v + 1);

// merge: 값 병합
map.merge("apple", 1, (oldValue, newValue) -> oldValue + newValue);
```

**3. Value로 정렬**:
```java
// Value 기준 내림차순 정렬
List<Map.Entry<String, Integer>> sorted =
    map.entrySet().stream()
        .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
        .collect(Collectors.toList());
```

**4. 실용 예시**:
```
단어 빈도수 분석 → 검색 엔진 인덱싱
로그 분석 → 에러 빈도 집계
사용자 행동 → 클릭 횟수 추적
```

---

## 📖 비유 5: 다국어 지원 시스템 (Properties/HashMap)

### 🎯 실생활 비유

다국어 지원 시스템은 **Key(메시지 코드)와 Value(번역된 텍스트)를 매핑**하여 여러 언어를 지원합니다.

**다국어 메시지 예시**:
```
한국어:
  greeting → "안녕하세요"
  welcome  → "환영합니다"

영어:
  greeting → "Hello"
  welcome  → "Welcome"

일본어:
  greeting → "こんにちは"
  welcome  → "ようこそ"
```

- **Key**: 메시지 코드 (언어 독립적)
- **Value**: 번역된 텍스트 (언어별)
- **런타임 언어 전환**: 사용자 설정에 따라 동적 변경

### 💻 Java 코드로 구현

```java
package map.example5;

import java.util.*;

/**
 * 언어 코드
 */
enum Language {
    KO("한국어"),
    EN("English"),
    JA("日本語"),
    ZH("中文");

    private final String displayName;

    Language(String displayName) {
        this.displayName = displayName;
    }

    public String getDisplayName() { return displayName; }
}

/**
 * 다국어 메시지 관리자
 */
class MessageManager {
    // 언어별 메시지 저장
    private Map<Language, Map<String, String>> messages;

    // 현재 언어
    private Language currentLanguage;

    public MessageManager() {
        this.messages = new HashMap<>();
        this.currentLanguage = Language.KO;

        // 각 언어별 메시지 맵 초기화
        for (Language lang : Language.values()) {
            messages.put(lang, new HashMap<>());
        }

        // 기본 메시지 로드
        loadDefaultMessages();
    }

    /**
     * 기본 메시지 로드
     */
    private void loadDefaultMessages() {
        // 한국어
        addMessage(Language.KO, "greeting", "안녕하세요");
        addMessage(Language.KO, "welcome", "환영합니다");
        addMessage(Language.KO, "goodbye", "안녕히 가세요");
        addMessage(Language.KO, "thankyou", "감사합니다");
        addMessage(Language.KO, "error", "오류가 발생했습니다");
        addMessage(Language.KO, "success", "성공적으로 완료되었습니다");

        // 영어
        addMessage(Language.EN, "greeting", "Hello");
        addMessage(Language.EN, "welcome", "Welcome");
        addMessage(Language.EN, "goodbye", "Goodbye");
        addMessage(Language.EN, "thankyou", "Thank you");
        addMessage(Language.EN, "error", "An error occurred");
        addMessage(Language.EN, "success", "Completed successfully");

        // 일본어
        addMessage(Language.JA, "greeting", "こんにちは");
        addMessage(Language.JA, "welcome", "ようこそ");
        addMessage(Language.JA, "goodbye", "さようなら");
        addMessage(Language.JA, "thankyou", "ありがとうございます");
        addMessage(Language.JA, "error", "エラーが発生しました");
        addMessage(Language.JA, "success", "正常に完了しました");

        // 중국어
        addMessage(Language.ZH, "greeting", "你好");
        addMessage(Language.ZH, "welcome", "欢迎");
        addMessage(Language.ZH, "goodbye", "再见");
        addMessage(Language.ZH, "thankyou", "谢谢");
        addMessage(Language.ZH, "error", "发生错误");
        addMessage(Language.ZH, "success", "成功完成");
    }

    /**
     * 메시지 추가
     */
    public void addMessage(Language language, String key, String value) {
        Map<String, String> langMessages = messages.get(language);
        langMessages.put(key, value);
    }

    /**
     * 메시지 조회 (현재 언어)
     */
    public String getMessage(String key) {
        return getMessage(currentLanguage, key);
    }

    /**
     * 메시지 조회 (특정 언어)
     */
    public String getMessage(Language language, String key) {
        Map<String, String> langMessages = messages.get(language);

        if (langMessages == null) {
            return "[Unknown Language]";
        }

        String message = langMessages.get(key);

        if (message == null) {
            // Fallback: 한국어 메시지
            message = messages.get(Language.KO).get(key);

            if (message == null) {
                return "[" + key + "]"; // Key를 그대로 반환
            }

            return message + " (Fallback)";
        }

        return message;
    }

    /**
     * 파라미터가 있는 메시지
     */
    public String getMessageWithParams(String key, Object... params) {
        String template = getMessage(key);

        // {0}, {1} 등을 파라미터로 치환
        for (int i = 0; i < params.length; i++) {
            template = template.replace("{" + i + "}", String.valueOf(params[i]));
        }

        return template;
    }

    /**
     * 언어 전환
     */
    public void setLanguage(Language language) {
        this.currentLanguage = language;
        System.out.println("🌐 언어 변경: " + language.getDisplayName());
    }

    /**
     * 현재 언어
     */
    public Language getCurrentLanguage() {
        return currentLanguage;
    }

    /**
     * 지원 언어 목록
     */
    public List<Language> getSupportedLanguages() {
        return new ArrayList<>(messages.keySet());
    }

    /**
     * 특정 언어의 메시지 개수
     */
    public int getMessageCount(Language language) {
        Map<String, String> langMessages = messages.get(language);
        return langMessages != null ? langMessages.size() : 0;
    }

    /**
     * 모든 메시지 출력 (현재 언어)
     */
    public void printAllMessages() {
        System.out.println("\n📋 모든 메시지 (" + currentLanguage.getDisplayName() + "):");
        System.out.println("─".repeat(50));

        Map<String, String> langMessages = messages.get(currentLanguage);

        for (Map.Entry<String, String> entry : langMessages.entrySet()) {
            System.out.println(entry.getKey() + " → " + entry.getValue());
        }

        System.out.println("─".repeat(50));
    }

    /**
     * 통계 정보
     */
    public void printStatistics() {
        System.out.println("\n📊 메시지 통계:");
        System.out.println("  - 현재 언어: " + currentLanguage.getDisplayName());
        System.out.println("  - 지원 언어: " + messages.size() + "개");

        for (Language lang : Language.values()) {
            System.out.println("    " + lang.getDisplayName() + ": " +
                getMessageCount(lang) + "개");
        }
    }
}

/**
 * 다국어 지원 데모
 */
public class MultiLanguageDemo {
    public static void main(String[] args) {
        MessageManager manager = new MessageManager();

        System.out.println("=== 다국어 지원 시스템 ===\n");

        // 시나리오 1: 기본 메시지 조회
        System.out.println("📍 시나리오 1: 기본 메시지 조회 (한국어)");

        System.out.println(manager.getMessage("greeting"));
        System.out.println(manager.getMessage("welcome"));
        System.out.println(manager.getMessage("thankyou"));
        System.out.println();

        // 시나리오 2: 언어 전환
        System.out.println("📍 시나리오 2: 언어 전환");

        manager.setLanguage(Language.EN);
        System.out.println(manager.getMessage("greeting"));
        System.out.println(manager.getMessage("welcome"));
        System.out.println();

        manager.setLanguage(Language.JA);
        System.out.println(manager.getMessage("greeting"));
        System.out.println(manager.getMessage("welcome"));
        System.out.println();

        manager.setLanguage(Language.ZH);
        System.out.println(manager.getMessage("greeting"));
        System.out.println(manager.getMessage("welcome"));
        System.out.println();

        // 시나리오 3: 모든 메시지 출력
        System.out.println("📍 시나리오 3: 모든 메시지 출력");
        manager.setLanguage(Language.KO);
        manager.printAllMessages();

        // 시나리오 4: 없는 메시지 키 조회 (Fallback)
        System.out.println("\n📍 시나리오 4: 없는 메시지 키 조회");

        manager.setLanguage(Language.EN);
        String unknownMessage = manager.getMessage("unknown_key");
        System.out.println("unknown_key: " + unknownMessage);
        System.out.println("→ 메시지가 없으면 [key] 형태로 반환");
        System.out.println();

        // 시나리오 5: 파라미터가 있는 메시지
        System.out.println("📍 시나리오 5: 파라미터가 있는 메시지");

        // 파라미터 메시지 추가
        manager.addMessage(Language.KO, "user.greeting", "안녕하세요, {0}님!");
        manager.addMessage(Language.EN, "user.greeting", "Hello, {0}!");
        manager.addMessage(Language.JA, "user.greeting", "こんにちは、{0}さん!");

        manager.addMessage(Language.KO, "item.count", "{0}개의 항목이 있습니다.");
        manager.addMessage(Language.EN, "item.count", "There are {0} items.");
        manager.addMessage(Language.JA, "item.count", "{0}個のアイテムがあります。");

        manager.setLanguage(Language.KO);
        System.out.println(manager.getMessageWithParams("user.greeting", "김철수"));
        System.out.println(manager.getMessageWithParams("item.count", 10));

        manager.setLanguage(Language.EN);
        System.out.println(manager.getMessageWithParams("user.greeting", "John"));
        System.out.println(manager.getMessageWithParams("item.count", 10));
        System.out.println();

        // 시나리오 6: 통계
        manager.printStatistics();

        // 시나리오 7: 대량 메시지 성능 테스트
        System.out.println("\n📍 시나리오 7: 대량 메시지 성능 테스트");

        // 1000개 메시지 추가
        for (int i = 0; i < 1000; i++) {
            manager.addMessage(Language.KO, "msg" + i, "메시지" + i);
        }

        long start = System.nanoTime();
        String msg = manager.getMessage("msg500");
        long end = System.nanoTime();

        System.out.println("1000개 메시지 중 조회: " + msg);
        System.out.println("조회 시간: " + String.format("%.3f", (end - start) / 1000.0) + "μs");
        System.out.println("→ HashMap의 O(1) 조회 성능");

        // 최종 통계
        manager.printStatistics();
    }
}
```

### 🎯 핵심 포인트

**1. 중첩 Map 구조**:
```java
// Map<언어, Map<키, 메시지>>
Map<Language, Map<String, String>> messages;

// 예시:
// KO → {greeting → "안녕하세요", welcome → "환영합니다"}
// EN → {greeting → "Hello", welcome → "Welcome"}
```

**2. 언어별 메시지 조회**:
```java
// 현재 언어 메시지
String message = manager.getMessage("greeting");

// 특정 언어 메시지
String enMessage = manager.getMessage(Language.EN, "greeting");
```

**3. Fallback 패턴**:
```java
public String getMessage(String key) {
    String message = currentLangMessages.get(key);

    if (message == null) {
        // Fallback: 기본 언어(한국어)로 대체
        message = koreanMessages.get(key);

        if (message == null) {
            return "[" + key + "]"; // Key를 그대로 반환
        }
    }

    return message;
}
```

**4. 파라미터 치환**:
```java
// 메시지 템플릿: "안녕하세요, {0}님! {1}개의 알림이 있습니다."
String template = getMessage("notification");

// 파라미터 치환
String message = template
    .replace("{0}", "김철수")
    .replace("{1}", "5");

// 결과: "안녕하세요, 김철수님! 5개의 알림이 있습니다."
```

**5. 실용 예시**:
```
글로벌 서비스 → 다국어 UI 지원
게임 → 언어별 대사/메뉴
관리 시스템 → 다국어 오류 메시지
```

---

## 🎓 Part 1 종합 정리

### 📊 Map 구현체 비교

| | HashMap | TreeMap | LinkedHashMap |
|---|---------|---------|---------------|
| **내부 구조** | Hash Table | Red-Black Tree | Hash Table + Linked List |
| **put/get** | O(1) | O(log n) | O(1) |
| **순서** | ❌ 없음 | ✅ Key 정렬 | ✅ 삽입 순서 |
| **null Key** | ✅ 1개 | ❌ 불가 | ✅ 1개 |
| **사용 예시** | 전화번호부, 빈도수 | 성적표, 범위 검색 | LRU 캐시 |

### 🎯 Map 선택 기준

```
정렬이 필요한가?
├─ YES → TreeMap
└─ NO  → 순서가 필요한가?
          ├─ YES → LinkedHashMap
          └─ NO  → HashMap (기본 선택)
```

### 🔑 Map 핵심 메서드

```java
// 기본 연산
V put(K key, V value)           // 추가
V get(Object key)               // 조회
V remove(Object key)            // 삭제
boolean containsKey(Object key) // Key 존재 확인

// 함수형 메서드 (Java 8+)
V getOrDefault(K key, V defaultValue)
V compute(K key, BiFunction remappingFunction)
V merge(K key, V value, BiFunction remappingFunction)

// 순회
Set<K> keySet()                 // 모든 Key
Collection<V> values()          // 모든 Value
Set<Map.Entry<K, V>> entrySet() // 모든 Entry
```

### 💡 실생활 활용 사례

1. **HashMap**: 전화번호부, 단어 빈도수, 캐시, 설정 관리
2. **TreeMap**: 성적표, 순위표, 시간순 이벤트, 범위 검색
3. **LinkedHashSet**: LRU 캐시, 접근 기록, 최근 사용 항목

**다음 Part 2에서는**: 3개 기업 사례 (카카오, 쿠팡, 라인) + 4개 주니어 실수 시나리오를 다룹니다.
