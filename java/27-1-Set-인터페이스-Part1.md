# 27장 Set 인터페이스 Part 1 - 실생활 비유로 이해하기 📝

## 🌟 실생활 비유로 이해하기

Set 인터페이스는 **중복을 허용하지 않는** 컬렉션입니다. 순서가 없거나(HashSet), 정렬되거나(TreeSet), 삽입 순서를 유지(LinkedHashSet)합니다.

---

## 비유 1: 학교 학생 명부 (HashSet) 🎓

학교 학생 명부는 학번으로 학생을 관리합니다. 같은 학번의 학생이 두 명일 수 없으며, 빠른 조회가 중요합니다.

### 실생활 상황
- **중복 불가**: 학번은 유일 (unique)
- **빠른 조회**: O(1) - 학번으로 즉시 찾기
- **순서 없음**: 학번 순서와 무관하게 저장

### 코드 예시

```java
import java.util.*;

class Student {
    private String studentId;
    private String name;
    private String major;
    private int grade;

    public Student(String studentId, String name, String major, int grade) {
        this.studentId = studentId;
        this.name = name;
        this.major = major;
        this.grade = grade;
    }

    public String getStudentId() { return studentId; }
    public String getName() { return name; }
    public String getMajor() { return major; }
    public int getGrade() { return grade; }

    // HashSet에서 중복 판단: equals()와 hashCode() 필수!
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Student student = (Student) o;
        return studentId.equals(student.studentId);  // 학번으로 비교
    }

    @Override
    public int hashCode() {
        return Objects.hash(studentId);  // 학번으로 해시 생성
    }

    @Override
    public String toString() {
        return studentId + " - " + name + " (" + major + ", " + grade + "학년)";
    }
}

class StudentRegistry {
    // HashSet: 중복 불가, O(1) 조회
    private Set<Student> students = new HashSet<>();

    // Set 특징 1: 중복 자동 제거
    public boolean registerStudent(Student student) {
        boolean added = students.add(student);

        if (added) {
            System.out.println("✅ 등록 성공: " + student);
        } else {
            System.out.println("❌ 등록 실패: 이미 존재하는 학번 " + student.getStudentId());
        }

        return added;
    }

    // Set 특징 2: O(1) 조회 (contains)
    public boolean isRegistered(String studentId) {
        // equals()를 사용하므로 studentId만 같으면 찾음
        Student dummy = new Student(studentId, "", "", 0);
        return students.contains(dummy);
    }

    // Set 특징 3: O(1) 제거
    public boolean removeStudent(String studentId) {
        Student dummy = new Student(studentId, "", "", 0);
        boolean removed = students.remove(dummy);

        if (removed) {
            System.out.println("🗑️ 제명: " + studentId);
        } else {
            System.out.println("⚠️ 학생 없음: " + studentId);
        }

        return removed;
    }

    // Set 특징 4: 순서 없음 (순회 시 무작위)
    public void displayAllStudents() {
        System.out.println("\n📋 전체 학생 명부 (" + students.size() + "명):");
        for (Student student : students) {
            System.out.println("   " + student);
        }
    }

    // Set 특징 5: 집합 연산 (합집합, 교집합, 차집합)
    public static void demonstrateSetOperations() {
        System.out.println("\n=== Set 집합 연산 ===\n");

        Set<String> computerScience = new HashSet<>(
            Arrays.asList("S001", "S002", "S003", "S004", "S005")
        );

        Set<String> mathematics = new HashSet<>(
            Arrays.asList("S003", "S004", "S006", "S007")
        );

        System.out.println("컴퓨터공학과: " + computerScience);
        System.out.println("수학과: " + mathematics);

        // 1. 합집합 (Union)
        Set<String> union = new HashSet<>(computerScience);
        union.addAll(mathematics);
        System.out.println("\n1. 합집합 (둘 중 하나라도 수강): " + union);

        // 2. 교집합 (Intersection)
        Set<String> intersection = new HashSet<>(computerScience);
        intersection.retainAll(mathematics);
        System.out.println("2. 교집합 (둘 다 수강): " + intersection);

        // 3. 차집합 (Difference)
        Set<String> difference = new HashSet<>(computerScience);
        difference.removeAll(mathematics);
        System.out.println("3. 차집합 (컴공만 수강): " + difference);

        // 4. 대칭 차집합 (Symmetric Difference)
        Set<String> symmetricDiff = new HashSet<>(union);
        symmetricDiff.removeAll(intersection);
        System.out.println("4. 대칭 차집합 (둘 중 하나만 수강): " + symmetricDiff);
    }

    // HashSet 내부 동작 시연
    public static void demonstrateHashSetInternals() {
        System.out.println("\n=== HashSet 내부 동작 ===\n");

        System.out.println("HashSet은 내부적으로 HashMap을 사용합니다.");
        System.out.println();
        System.out.println("구조:");
        System.out.println("   private transient HashMap<E, Object> map;");
        System.out.println("   private static final Object PRESENT = new Object();");
        System.out.println();

        System.out.println("add() 동작:");
        System.out.println("   public boolean add(E e) {");
        System.out.println("       return map.put(e, PRESENT) == null;");
        System.out.println("   }");
        System.out.println();

        System.out.println("과정:");
        System.out.println("   1. hashCode() 계산 → 해시값 생성");
        System.out.println("   2. 해시값 → 버킷(bucket) 위치 결정");
        System.out.println("   3. equals()로 기존 요소와 비교");
        System.out.println("   4. 중복이면 추가 안 함, 새로운 요소면 추가");
        System.out.println();

        System.out.println("예시:");
        System.out.println("   Student s1 = new Student(\"S001\", \"홍길동\", \"컴공\", 3);");
        System.out.println("   set.add(s1);");
        System.out.println();
        System.out.println("   1. s1.hashCode() 계산 → 예: 12345");
        System.out.println("   2. 12345 % 16 = 9 → 9번 버킷에 저장");
        System.out.println("   3. 9번 버킷에 기존 요소 없음 → 추가 ✅");
        System.out.println();

        System.out.println("   Student s2 = new Student(\"S001\", \"김철수\", \"수학\", 2);");
        System.out.println("   set.add(s2);  // 같은 학번!");
        System.out.println();
        System.out.println("   1. s2.hashCode() 계산 → 12345 (같은 학번)");
        System.out.println("   2. 12345 % 16 = 9 → 9번 버킷 확인");
        System.out.println("   3. s1.equals(s2) → true (학번 같음)");
        System.out.println("   4. 중복 → 추가 안 함 ❌");
        System.out.println();

        System.out.println("✅ HashSet 특징:");
        System.out.println("   - 추가: O(1) (해시 충돌 없을 때)");
        System.out.println("   - 조회: O(1)");
        System.out.println("   - 삭제: O(1)");
        System.out.println("   - 순서: 없음 (무작위)");
        System.out.println("   - null 허용: ✅ (1개만)");
    }

    // equals()와 hashCode()의 중요성
    public static void demonstrateEqualsHashCode() {
        System.out.println("\n=== equals()와 hashCode() 중요성 ===\n");

        // ❌ equals()와 hashCode() 미구현
        class BadStudent {
            String studentId;
            String name;

            BadStudent(String studentId, String name) {
                this.studentId = studentId;
                this.name = name;
            }

            @Override
            public String toString() {
                return studentId + " - " + name;
            }

            // equals()와 hashCode() 미구현 → Object의 기본 구현 사용
            // → 객체 참조로 비교 (같은 학번이어도 다른 객체면 다름!)
        }

        Set<BadStudent> badSet = new HashSet<>();
        badSet.add(new BadStudent("S001", "홍길동"));
        badSet.add(new BadStudent("S001", "홍길동"));  // 같은 학번인데도 추가됨!

        System.out.println("❌ equals()와 hashCode() 미구현:");
        System.out.println("   크기: " + badSet.size() + " (2개 - 중복 제거 안 됨!)");
        for (BadStudent s : badSet) {
            System.out.println("   " + s);
        }

        // ✅ equals()와 hashCode() 구현
        Set<Student> goodSet = new HashSet<>();
        goodSet.add(new Student("S001", "홍길동", "컴공", 3));
        goodSet.add(new Student("S001", "홍길동", "컴공", 3));  // 중복 제거됨!

        System.out.println("\n✅ equals()와 hashCode() 구현:");
        System.out.println("   크기: " + goodSet.size() + " (1개 - 중복 제거됨!)");
        for (Student s : goodSet) {
            System.out.println("   " + s);
        }

        System.out.println("\n📌 핵심:");
        System.out.println("   HashSet은 equals()와 hashCode()로 중복 판단");
        System.out.println("   → 반드시 둘 다 오버라이드해야 함!");
    }
}

public class StudentRegistryExample {
    public static void main(String[] args) {
        System.out.println("=== 학교 학생 명부 시스템 (HashSet) ===\n");

        StudentRegistry registry = new StudentRegistry();

        // 학생 등록
        registry.registerStudent(new Student("S001", "홍길동", "컴퓨터공학", 3));
        registry.registerStudent(new Student("S002", "김영희", "수학", 2));
        registry.registerStudent(new Student("S003", "이철수", "물리학", 4));

        // 중복 등록 시도
        System.out.println();
        registry.registerStudent(new Student("S001", "박민수", "화학", 1));  // 같은 학번!

        // 전체 출력
        registry.displayAllStudents();

        // 조회
        System.out.println();
        System.out.println("🔍 S002 등록 여부: " + registry.isRegistered("S002"));
        System.out.println("🔍 S999 등록 여부: " + registry.isRegistered("S999"));

        // 제거
        System.out.println();
        registry.removeStudent("S003");

        registry.displayAllStudents();

        // 집합 연산
        StudentRegistry.demonstrateSetOperations();

        // 내부 동작
        StudentRegistry.demonstrateHashSetInternals();

        // equals와 hashCode
        StudentRegistry.demonstrateEqualsHashCode();

        System.out.println("\n\n✅ HashSet 핵심:");
        System.out.println("1. 중복 불허 (equals + hashCode)");
        System.out.println("2. O(1) 추가/조회/삭제 (해시 테이블)");
        System.out.println("3. 순서 없음 (무작위)");
        System.out.println("4. null 허용 (1개만)");
        System.out.println("5. 집합 연산 가능 (합/교/차집합)");
    }
}
```

### 실행 결과
```
=== 학교 학생 명부 시스템 (HashSet) ===

✅ 등록 성공: S001 - 홍길동 (컴퓨터공학, 3학년)
✅ 등록 성공: S002 - 김영희 (수학, 2학년)
✅ 등록 성공: S003 - 이철수 (물리학, 4학년)

❌ 등록 실패: 이미 존재하는 학번 S001

📋 전체 학생 명부 (3명):
   S002 - 김영희 (수학, 2학년)
   S001 - 홍길동 (컴퓨터공학, 3학년)
   S003 - 이철수 (물리학, 4학년)

🔍 S002 등록 여부: true
🔍 S999 등록 여부: false

🗑️ 제명: S003

📋 전체 학생 명부 (2명):
   S002 - 김영희 (수학, 2학년)
   S001 - 홍길동 (컴퓨터공학, 3학년)

=== Set 집합 연산 ===

컴퓨터공학과: [S001, S002, S003, S004, S005]
수학과: [S003, S004, S006, S007]

1. 합집합 (둘 중 하나라도 수강): [S001, S002, S003, S004, S005, S006, S007]
2. 교집합 (둘 다 수강): [S003, S004]
3. 차집합 (컴공만 수강): [S001, S002, S005]
4. 대칭 차집합 (둘 중 하나만 수강): [S001, S002, S005, S006, S007]

=== HashSet 내부 동작 ===

HashSet은 내부적으로 HashMap을 사용합니다.

구조:
   private transient HashMap<E, Object> map;
   private static final Object PRESENT = new Object();

add() 동작:
   public boolean add(E e) {
       return map.put(e, PRESENT) == null;
   }

과정:
   1. hashCode() 계산 → 해시값 생성
   2. 해시값 → 버킷(bucket) 위치 결정
   3. equals()로 기존 요소와 비교
   4. 중복이면 추가 안 함, 새로운 요소면 추가

예시:
   Student s1 = new Student("S001", "홍길동", "컴공", 3);
   set.add(s1);

   1. s1.hashCode() 계산 → 예: 12345
   2. 12345 % 16 = 9 → 9번 버킷에 저장
   3. 9번 버킷에 기존 요소 없음 → 추가 ✅

   Student s2 = new Student("S001", "김철수", "수학", 2);
   set.add(s2);  // 같은 학번!

   1. s2.hashCode() 계산 → 12345 (같은 학번)
   2. 12345 % 16 = 9 → 9번 버킷 확인
   3. s1.equals(s2) → true (학번 같음)
   4. 중복 → 추가 안 함 ❌

✅ HashSet 특징:
   - 추가: O(1) (해시 충돌 없을 때)
   - 조회: O(1)
   - 삭제: O(1)
   - 순서: 없음 (무작위)
   - null 허용: ✅ (1개만)

=== equals()와 hashCode() 중요성 ===

❌ equals()와 hashCode() 미구현:
   크기: 2 (2개 - 중복 제거 안 됨!)
   S001 - 홍길동
   S001 - 홍길동

✅ equals()와 hashCode() 구현:
   크기: 1 (1개 - 중복 제거됨!)
   S001 - 홍길동 (컴공, 3학년)

📌 핵심:
   HashSet은 equals()와 hashCode()로 중복 판단
   → 반드시 둘 다 오버라이드해야 함!


✅ HashSet 핵심:
1. 중복 불허 (equals + hashCode)
2. O(1) 추가/조회/삭제 (해시 테이블)
3. 순서 없음 (무작위)
4. null 허용 (1개만)
5. 집합 연산 가능 (합/교/차집합)
```

### 핵심 정리
- **HashSet**: 해시 테이블 기반, O(1) 성능
- **중복 제거**: equals() + hashCode() 필수
- **순서 없음**: 저장 순서와 무관
- **집합 연산**: addAll, retainAll, removeAll
- **실생활 비유**: 학생 명부 = 중복 없는 HashSet

---

## 비유 2: 도서관 ISBN 관리 (TreeSet) 📚

도서관은 책을 ISBN(국제표준도서번호)으로 관리하며, **자동 정렬**된 상태로 보관합니다. TreeSet은 자동으로 요소를 정렬합니다.

### 실생활 상황
- **자동 정렬**: ISBN 순서로 자동 정렬
- **범위 검색**: "978-89로 시작하는 책" 빠르게 찾기
- **중복 불가**: 같은 ISBN의 책은 1권만

### 코드 예시

```java
import java.util.*;

class Book implements Comparable<Book> {
    private String isbn;
    private String title;
    private String author;
    private int publicationYear;

    public Book(String isbn, String title, String author, int publicationYear) {
        this.isbn = isbn;
        this.title = title;
        this.author = author;
        this.publicationYear = publicationYear;
    }

    public String getIsbn() { return isbn; }
    public String getTitle() { return title; }
    public String getAuthor() { return author; }
    public int getPublicationYear() { return publicationYear; }

    // TreeSet의 정렬 기준: Comparable 구현
    @Override
    public int compareTo(Book other) {
        return this.isbn.compareTo(other.isbn);  // ISBN으로 정렬
    }

    // equals()와 hashCode()도 구현 (일관성)
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Book book = (Book) o;
        return isbn.equals(book.isbn);
    }

    @Override
    public int hashCode() {
        return Objects.hash(isbn);
    }

    @Override
    public String toString() {
        return isbn + " - 《" + title + "》 (" + author + ", " + publicationYear + ")";
    }
}

class LibraryISBN {
    // TreeSet: 자동 정렬, O(log n) 연산
    private TreeSet<Book> books = new TreeSet<>();

    // TreeSet 특징 1: 자동 정렬 (compareTo 기준)
    public void addBook(Book book) {
        boolean added = books.add(book);

        if (added) {
            System.out.println("✅ 추가됨: " + book.getTitle() + " (ISBN: " + book.getIsbn() + ")");
        } else {
            System.out.println("❌ 중복 ISBN: " + book.getIsbn());
        }
    }

    // TreeSet 특징 2: 정렬된 순서로 순회
    public void displayAllBooks() {
        System.out.println("\n📚 전체 도서 목록 (ISBN 순):");
        for (Book book : books) {
            System.out.println("   " + book);
        }
    }

    // TreeSet 특징 3: 범위 검색
    public void findBooksByISBNRange(String fromISBN, String toISBN) {
        Book fromBook = new Book(fromISBN, "", "", 0);
        Book toBook = new Book(toISBN, "", "", 0);

        // subSet: fromISBN(포함) ~ toISBN(불포함)
        SortedSet<Book> range = books.subSet(fromBook, toBook);

        System.out.println("\n🔍 ISBN 범위 검색 (" + fromISBN + " ~ " + toISBN + "):");
        for (Book book : range) {
            System.out.println("   " + book);
        }
    }

    // TreeSet 특징 4: first(), last()
    public void displayFirstAndLast() {
        if (!books.isEmpty()) {
            System.out.println("\n📖 가장 작은 ISBN: " + books.first());
            System.out.println("📖 가장 큰 ISBN: " + books.last());
        }
    }

    // TreeSet 특징 5: headSet, tailSet
    public void displayBooksBeforeISBN(String isbn) {
        Book book = new Book(isbn, "", "", 0);
        SortedSet<Book> head = books.headSet(book);  // isbn 미만

        System.out.println("\n📚 " + isbn + " 이전 도서:");
        for (Book b : head) {
            System.out.println("   " + b);
        }
    }

    public void displayBooksFromISBN(String isbn) {
        Book book = new Book(isbn, "", "", 0);
        SortedSet<Book> tail = books.tailSet(book);  // isbn 이상

        System.out.println("\n📚 " + isbn + " 이후 도서:");
        for (Book b : tail) {
            System.out.println("   " + b);
        }
    }

    // TreeSet 내부 구조 시연
    public static void demonstrateTreeSetInternals() {
        System.out.println("\n=== TreeSet 내부 동작 ===\n");

        System.out.println("TreeSet은 내부적으로 TreeMap(Red-Black Tree)을 사용합니다.");
        System.out.println();

        System.out.println("Red-Black Tree 특징:");
        System.out.println("   1. 이진 검색 트리 (Binary Search Tree)");
        System.out.println("   2. 자가 균형 트리 (Self-Balancing)");
        System.out.println("   3. 모든 연산 O(log n) 보장");
        System.out.println();

        System.out.println("구조:");
        System.out.println("           50");
        System.out.println("          /  \\");
        System.out.println("        30    70");
        System.out.println("       /  \\  /  \\");
        System.out.println("      20  40 60  80");
        System.out.println();

        System.out.println("add(25) 과정:");
        System.out.println("   1. 50과 비교 → 25 < 50 → 왼쪽");
        System.out.println("   2. 30과 비교 → 25 < 30 → 왼쪽");
        System.out.println("   3. 20과 비교 → 25 > 20 → 오른쪽");
        System.out.println("   4. 20의 오른쪽에 25 삽입");
        System.out.println("   5. Red-Black Tree 균형 조정");
        System.out.println("   → O(log n) 시간");
        System.out.println();

        System.out.println("✅ TreeSet 특징:");
        System.out.println("   - 추가: O(log n)");
        System.out.println("   - 조회: O(log n)");
        System.out.println("   - 삭제: O(log n)");
        System.out.println("   - 순서: 정렬됨 (Comparable 또는 Comparator)");
        System.out.println("   - null 허용: ❌ (NullPointerException)");
    }

    // Comparator 사용 예시
    public static void demonstrateComparator() {
        System.out.println("\n=== Comparator로 정렬 기준 변경 ===\n");

        // 1. ISBN 순 (기본 - Comparable)
        TreeSet<Book> byISBN = new TreeSet<>();
        byISBN.add(new Book("978-89-123", "자바의 정석", "남궁성", 2016));
        byISBN.add(new Book("978-89-456", "Effective Java", "Joshua Bloch", 2018));
        byISBN.add(new Book("978-89-789", "Clean Code", "Robert Martin", 2008));

        System.out.println("1. ISBN 순 (기본):");
        for (Book book : byISBN) {
            System.out.println("   " + book);
        }

        // 2. 제목 순 (Comparator)
        TreeSet<Book> byTitle = new TreeSet<>(Comparator.comparing(Book::getTitle));
        byTitle.addAll(byISBN);

        System.out.println("\n2. 제목 순 (Comparator):");
        for (Book book : byTitle) {
            System.out.println("   " + book);
        }

        // 3. 출판년도 순 (Comparator)
        TreeSet<Book> byYear = new TreeSet<>(Comparator.comparingInt(Book::getPublicationYear));
        byYear.addAll(byISBN);

        System.out.println("\n3. 출판년도 순 (Comparator):");
        for (Book book : byYear) {
            System.out.println("   " + book);
        }

        // 4. 복합 정렬 (저자 → 제목)
        TreeSet<Book> byAuthorThenTitle = new TreeSet<>(
            Comparator.comparing(Book::getAuthor)
                      .thenComparing(Book::getTitle)
        );
        byAuthorThenTitle.addAll(byISBN);

        System.out.println("\n4. 저자 → 제목 순:");
        for (Book book : byAuthorThenTitle) {
            System.out.println("   " + book);
        }
    }

    // HashSet vs TreeSet 성능 비교
    public static void comparePerformance() {
        System.out.println("\n=== HashSet vs TreeSet 성능 비교 ===\n");

        int size = 100000;

        // 1. HashSet
        Set<Integer> hashSet = new HashSet<>();
        long start = System.nanoTime();
        for (int i = 0; i < size; i++) {
            hashSet.add(i);
        }
        long hashAddTime = (System.nanoTime() - start) / 1_000_000;

        start = System.nanoTime();
        for (int i = 0; i < 10000; i++) {
            hashSet.contains(size / 2);
        }
        long hashContainsTime = (System.nanoTime() - start) / 1_000_000;

        // 2. TreeSet
        Set<Integer> treeSet = new TreeSet<>();
        start = System.nanoTime();
        for (int i = 0; i < size; i++) {
            treeSet.add(i);
        }
        long treeAddTime = (System.nanoTime() - start) / 1_000_000;

        start = System.nanoTime();
        for (int i = 0; i < 10000; i++) {
            treeSet.contains(size / 2);
        }
        long treeContainsTime = (System.nanoTime() - start) / 1_000_000;

        System.out.println("1. 추가 (" + size + "개):");
        System.out.println("   HashSet: " + hashAddTime + "ms (O(1))");
        System.out.println("   TreeSet: " + treeAddTime + "ms (O(log n))");

        System.out.println("\n2. 조회 (10000회):");
        System.out.println("   HashSet: " + hashContainsTime + "ms (O(1))");
        System.out.println("   TreeSet: " + treeContainsTime + "ms (O(log n))");

        System.out.println("\n✅ 선택 기준:");
        System.out.println("   - 성능 중시 → HashSet");
        System.out.println("   - 정렬 필요 → TreeSet");
        System.out.println("   - 범위 검색 → TreeSet");
    }
}

public class LibraryISBNExample {
    public static void main(String[] args) {
        System.out.println("=== 도서관 ISBN 관리 시스템 (TreeSet) ===\n");

        LibraryISBN library = new LibraryISBN();

        // 책 추가 (무작위 순서)
        library.addBook(new Book("978-89-456", "Effective Java", "Joshua Bloch", 2018));
        library.addBook(new Book("978-89-123", "자바의 정석", "남궁성", 2016));
        library.addBook(new Book("978-89-789", "Clean Code", "Robert Martin", 2008));
        library.addBook(new Book("978-89-234", "Head First Java", "Kathy Sierra", 2005));

        // 자동 정렬 확인
        library.displayAllBooks();

        // 중복 추가
        System.out.println();
        library.addBook(new Book("978-89-123", "다른 책", "다른 저자", 2020));

        // First, Last
        library.displayFirstAndLast();

        // 범위 검색
        library.findBooksByISBNRange("978-89-200", "978-89-500");

        // HeadSet, TailSet
        library.displayBooksBeforeISBN("978-89-500");
        library.displayBooksFromISBN("978-89-500");

        // 내부 동작
        LibraryISBN.demonstrateTreeSetInternals();

        // Comparator
        LibraryISBN.demonstrateComparator();

        // 성능 비교
        LibraryISBN.comparePerformance();

        System.out.println("\n\n✅ TreeSet 핵심:");
        System.out.println("1. 자동 정렬 (Comparable/Comparator)");
        System.out.println("2. O(log n) 추가/조회/삭제");
        System.out.println("3. 범위 검색 (subSet, headSet, tailSet)");
        System.out.println("4. Red-Black Tree 기반");
        System.out.println("5. null 불허");
    }
}
```

### 실행 결과
```
=== 도서관 ISBN 관리 시스템 (TreeSet) ===

✅ 추가됨: Effective Java (ISBN: 978-89-456)
✅ 추가됨: 자바의 정석 (ISBN: 978-89-123)
✅ 추가됨: Clean Code (ISBN: 978-89-789)
✅ 추가됨: Head First Java (ISBN: 978-89-234)

📚 전체 도서 목록 (ISBN 순):
   978-89-123 - 《자바의 정석》 (남궁성, 2016)
   978-89-234 - 《Head First Java》 (Kathy Sierra, 2005)
   978-89-456 - 《Effective Java》 (Joshua Bloch, 2018)
   978-89-789 - 《Clean Code》 (Robert Martin, 2008)

❌ 중복 ISBN: 978-89-123

📖 가장 작은 ISBN: 978-89-123 - 《자바의 정석》 (남궁성, 2016)
📖 가장 큰 ISBN: 978-89-789 - 《Clean Code》 (Robert Martin, 2008)

🔍 ISBN 범위 검색 (978-89-200 ~ 978-89-500):
   978-89-234 - 《Head First Java》 (Kathy Sierra, 2005)
   978-89-456 - 《Effective Java》 (Joshua Bloch, 2018)

📚 978-89-500 이전 도서:
   978-89-123 - 《자바의 정석》 (남궁성, 2016)
   978-89-234 - 《Head First Java》 (Kathy Sierra, 2005)
   978-89-456 - 《Effective Java》 (Joshua Bloch, 2018)

📚 978-89-500 이후 도서:
   978-89-789 - 《Clean Code》 (Robert Martin, 2008)

=== TreeSet 내부 동작 ===

TreeSet은 내부적으로 TreeMap(Red-Black Tree)을 사용합니다.

Red-Black Tree 특징:
   1. 이진 검색 트리 (Binary Search Tree)
   2. 자가 균형 트리 (Self-Balancing)
   3. 모든 연산 O(log n) 보장

구조:
           50
          /  \
        30    70
       /  \  /  \
      20  40 60  80

add(25) 과정:
   1. 50과 비교 → 25 < 50 → 왼쪽
   2. 30과 비교 → 25 < 30 → 왼쪽
   3. 20과 비교 → 25 > 20 → 오른쪽
   4. 20의 오른쪽에 25 삽입
   5. Red-Black Tree 균형 조정
   → O(log n) 시간

✅ TreeSet 특징:
   - 추가: O(log n)
   - 조회: O(log n)
   - 삭제: O(log n)
   - 순서: 정렬됨 (Comparable 또는 Comparator)
   - null 허용: ❌ (NullPointerException)

=== Comparator로 정렬 기준 변경 ===

1. ISBN 순 (기본):
   978-89-123 - 《자바의 정석》 (남궁성, 2016)
   978-89-456 - 《Effective Java》 (Joshua Bloch, 2018)
   978-89-789 - 《Clean Code》 (Robert Martin, 2008)

2. 제목 순 (Comparator):
   978-89-789 - 《Clean Code》 (Robert Martin, 2008)
   978-89-456 - 《Effective Java》 (Joshua Bloch, 2018)
   978-89-123 - 《자바의 정석》 (남궁성, 2016)

3. 출판년도 순 (Comparator):
   978-89-789 - 《Clean Code》 (Robert Martin, 2008)
   978-89-123 - 《자바의 정석》 (남궁성, 2016)
   978-89-456 - 《Effective Java》 (Joshua Bloch, 2018)

4. 저자 → 제목 순:
   978-89-456 - 《Effective Java》 (Joshua Bloch, 2018)
   978-89-789 - 《Clean Code》 (Robert Martin, 2008)
   978-89-123 - 《자바의 정석》 (남궁성, 2016)

=== HashSet vs TreeSet 성능 비교 ===

1. 추가 (100000개):
   HashSet: 45ms (O(1))
   TreeSet: 187ms (O(log n))

2. 조회 (10000회):
   HashSet: 0ms (O(1))
   TreeSet: 12ms (O(log n))

✅ 선택 기준:
   - 성능 중시 → HashSet
   - 정렬 필요 → TreeSet
   - 범위 검색 → TreeSet


✅ TreeSet 핵심:
1. 자동 정렬 (Comparable/Comparator)
2. O(log n) 추가/조회/삭제
3. 범위 검색 (subSet, headSet, tailSet)
4. Red-Black Tree 기반
5. null 불허
```

### 핵심 정리
- **TreeSet**: Red-Black Tree 기반, 자동 정렬
- **O(log n)**: 모든 연산이 로그 시간
- **정렬 기준**: Comparable 또는 Comparator
- **범위 검색**: subSet, headSet, tailSet
- **실생활 비유**: ISBN 관리 = 정렬된 TreeSet

---

## 비유 3: SNS 팔로워 목록 (LinkedHashSet) 👥

SNS 팔로워 목록은 **팔로우한 순서**를 기억하면서 중복을 제거합니다. LinkedHashSet은 삽입 순서를 유지합니다.

### 실생활 상황
- **중복 불가**: 같은 사람을 두 번 팔로우 불가
- **순서 유지**: 팔로우한 순서대로 표시
- **빠른 조회**: O(1) - 팔로우 여부 확인

### 코드 예시

```java
import java.util.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

class User {
    private String username;
    private String displayName;
    private LocalDateTime followedAt;

    public User(String username, String displayName) {
        this.username = username;
        this.displayName = displayName;
        this.followedAt = LocalDateTime.now();
    }

    public String getUsername() { return username; }
    public String getDisplayName() { return displayName; }
    public LocalDateTime getFollowedAt() { return followedAt; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        User user = (User) o;
        return username.equals(user.username);  // username으로 비교
    }

    @Override
    public int hashCode() {
        return Objects.hash(username);
    }

    @Override
    public String toString() {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        return "@" + username + " (" + displayName + ") - 팔로우: " +
               followedAt.format(formatter);
    }
}

class SocialMediaFollowers {
    // LinkedHashSet: 중복 불가 + 삽입 순서 유지
    private LinkedHashSet<User> followers = new LinkedHashSet<>();

    // LinkedHashSet 특징 1: 순서 유지 + 중복 제거
    public void follow(User user) {
        boolean added = followers.add(user);

        if (added) {
            System.out.println("✅ 팔로우: @" + user.getUsername() +
                             " (총 " + followers.size() + "명)");
        } else {
            System.out.println("❌ 이미 팔로우 중: @" + user.getUsername());
        }
    }

    // LinkedHashSet 특징 2: 순서대로 순회
    public void displayFollowers() {
        System.out.println("\n👥 팔로워 목록 (" + followers.size() + "명) - 팔로우 순:");
        int index = 1;
        for (User follower : followers) {
            System.out.println("   " + index++ + ". " + follower);
        }
    }

    // LinkedHashSet 특징 3: O(1) 조회
    public boolean isFollowing(String username) {
        User dummy = new User(username, "");
        return followers.contains(dummy);
    }

    // LinkedHashSet 특징 4: 순서 유지하며 제거
    public void unfollow(String username) {
        User dummy = new User(username, "");
        boolean removed = followers.remove(dummy);

        if (removed) {
            System.out.println("🗑️ 언팔로우: @" + username);
        } else {
            System.out.println("⚠️ 팔로우하지 않음: @" + username);
        }
    }

    // 첫 N명 팔로워
    public void displayFirstFollowers(int count) {
        System.out.println("\n🌟 최초 " + count + "명 팔로워:");
        int index = 1;
        for (User follower : followers) {
            if (index > count) break;
            System.out.println("   " + index++ + ". @" + follower.getUsername());
        }
    }

    // LinkedHashSet 내부 구조
    public static void demonstrateLinkedHashSetInternals() {
        System.out.println("\n=== LinkedHashSet 내부 동작 ===\n");

        System.out.println("LinkedHashSet = HashSet + 이중 연결 리스트");
        System.out.println();

        System.out.println("구조:");
        System.out.println("   HashMap + Doubly Linked List");
        System.out.println();
        System.out.println("   [prev] ← [A] → [next]");
        System.out.println("              ↓");
        System.out.println("   [prev] ← [B] → [next]");
        System.out.println("              ↓");
        System.out.println("   [prev] ← [C] → [next]");
        System.out.println();

        System.out.println("add(\"D\") 과정:");
        System.out.println("   1. HashMap에 추가 (O(1))");
        System.out.println("   2. 이중 연결 리스트의 끝에 추가 (O(1))");
        System.out.println("   3. 삽입 순서 유지");
        System.out.println();

        System.out.println("순회:");
        System.out.println("   - 이중 연결 리스트를 따라 순회");
        System.out.println("   - 삽입 순서대로 반환");
        System.out.println();

        System.out.println("✅ LinkedHashSet 특징:");
        System.out.println("   - 추가: O(1)");
        System.out.println("   - 조회: O(1)");
        System.out.println("   - 삭제: O(1)");
        System.out.println("   - 순서: 삽입 순서 유지");
        System.out.println("   - 메모리: HashSet보다 약간 더 사용 (링크)");
    }

    // HashSet vs LinkedHashSet vs TreeSet 비교
    public static void compareSetTypes() {
        System.out.println("\n=== Set 구현체 비교 ===\n");

        List<String> items = Arrays.asList("Banana", "Apple", "Cherry", "Date", "Elderberry");

        // 1. HashSet - 순서 없음
        Set<String> hashSet = new HashSet<>(items);
        System.out.println("1. HashSet (순서 없음):");
        System.out.println("   " + hashSet);

        // 2. LinkedHashSet - 삽입 순서
        Set<String> linkedHashSet = new LinkedHashSet<>(items);
        System.out.println("\n2. LinkedHashSet (삽입 순서):");
        System.out.println("   " + linkedHashSet);

        // 3. TreeSet - 정렬
        Set<String> treeSet = new TreeSet<>(items);
        System.out.println("\n3. TreeSet (정렬):");
        System.out.println("   " + treeSet);

        System.out.println("\n📊 비교 표:");
        System.out.println("┌──────────────────┬──────────┬────────┬──────────┐");
        System.out.println("│ 구현체           │ 순서     │ 성능   │ 사용 사례│");
        System.out.println("├──────────────────┼──────────┼────────┼──────────┤");
        System.out.println("│ HashSet          │ 없음     │ O(1)   │ 성능 중시│");
        System.out.println("│ LinkedHashSet    │ 삽입순서 │ O(1)   │ 순서필요 │");
        System.out.println("│ TreeSet          │ 정렬     │ O(logn)│ 정렬필요 │");
        System.out.println("└──────────────────┴──────────┴────────┴──────────┘");
    }

    // LRU 캐시 패턴 (LinkedHashSet 활용)
    public static void demonstrateLRUPattern() {
        System.out.println("\n=== LRU 캐시 패턴 (LinkedHashSet 활용) ===\n");

        class LRUCache<T> {
            private LinkedHashSet<T> cache;
            private int maxSize;

            public LRUCache(int maxSize) {
                this.cache = new LinkedHashSet<>();
                this.maxSize = maxSize;
            }

            public void access(T item) {
                // 이미 있으면 제거 후 맨 뒤로 (Most Recently Used)
                if (cache.contains(item)) {
                    cache.remove(item);
                }

                // 크기 초과 시 가장 오래된 항목 제거
                if (cache.size() >= maxSize) {
                    T oldest = cache.iterator().next();  // 첫 번째 = 가장 오래된 것
                    cache.remove(oldest);
                    System.out.println("   🗑️ 제거 (LRU): " + oldest);
                }

                cache.add(item);
                System.out.println("   ✅ 접근: " + item + " → " + cache);
            }
        }

        LRUCache<String> cache = new LRUCache<>(3);
        cache.access("A");
        cache.access("B");
        cache.access("C");
        cache.access("A");  // A를 맨 뒤로
        cache.access("D");  // B 제거됨 (가장 오래됨)

        System.out.println("\n💡 LinkedHashSet으로 LRU 캐시 구현 가능!");
    }
}

public class SocialMediaFollowersExample {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== SNS 팔로워 관리 시스템 (LinkedHashSet) ===\n");

        SocialMediaFollowers sns = new SocialMediaFollowers();

        // 팔로우
        sns.follow(new User("alice", "Alice Kim"));
        Thread.sleep(100);
        sns.follow(new User("bob", "Bob Lee"));
        Thread.sleep(100);
        sns.follow(new User("charlie", "Charlie Park"));
        Thread.sleep(100);
        sns.follow(new User("david", "David Choi"));

        // 중복 팔로우
        System.out.println();
        sns.follow(new User("alice", "Alice Kim"));  // 중복!

        // 팔로워 목록 (순서 유지)
        sns.displayFollowers();

        // 조회
        System.out.println();
        System.out.println("🔍 @alice 팔로우 중? " + sns.isFollowing("alice"));
        System.out.println("🔍 @eve 팔로우 중? " + sns.isFollowing("eve"));

        // 언팔로우
        System.out.println();
        sns.unfollow("bob");

        sns.displayFollowers();

        // 첫 N명
        sns.displayFirstFollowers(2);

        // 내부 동작
        SocialMediaFollowers.demonstrateLinkedHashSetInternals();

        // 구현체 비교
        SocialMediaFollowers.compareSetTypes();

        // LRU 패턴
        SocialMediaFollowers.demonstrateLRUPattern();

        System.out.println("\n\n✅ LinkedHashSet 핵심:");
        System.out.println("1. 중복 불허 + 삽입 순서 유지");
        System.out.println("2. O(1) 추가/조회/삭제 (HashSet과 동일)");
        System.out.println("3. 이중 연결 리스트로 순서 유지");
        System.out.println("4. LRU 캐시 구현에 활용");
        System.out.println("5. HashSet보다 약간 더 많은 메모리 사용");
    }
}
```

### 실행 결과
```
=== SNS 팔로워 관리 시스템 (LinkedHashSet) ===

✅ 팔로우: @alice (총 1명)
✅ 팔로우: @bob (총 2명)
✅ 팔로우: @charlie (총 3명)
✅ 팔로우: @david (총 4명)

❌ 이미 팔로우 중: @alice

👥 팔로워 목록 (4명) - 팔로우 순:
   1. @alice (Alice Kim) - 팔로우: 2025-01-15 14:35:12
   2. @bob (Bob Lee) - 팔로우: 2025-01-15 14:35:12
   3. @charlie (Charlie Park) - 팔로우: 2025-01-15 14:35:12
   4. @david (David Choi) - 팔로우: 2025-01-15 14:35:12

🔍 @alice 팔로우 중? true
🔍 @eve 팔로우 중? false

🗑️ 언팔로우: @bob

👥 팔로워 목록 (3명) - 팔로우 순:
   1. @alice (Alice Kim) - 팔로우: 2025-01-15 14:35:12
   2. @charlie (Charlie Park) - 팔로우: 2025-01-15 14:35:12
   3. @david (David Choi) - 팔로우: 2025-01-15 14:35:12

🌟 최초 2명 팔로워:
   1. @alice
   2. @charlie

=== LinkedHashSet 내부 동작 ===

LinkedHashSet = HashSet + 이중 연결 리스트

구조:
   HashMap + Doubly Linked List

   [prev] ← [A] → [next]
              ↓
   [prev] ← [B] → [next]
              ↓
   [prev] ← [C] → [next]

add("D") 과정:
   1. HashMap에 추가 (O(1))
   2. 이중 연결 리스트의 끝에 추가 (O(1))
   3. 삽입 순서 유지

순회:
   - 이중 연결 리스트를 따라 순회
   - 삽입 순서대로 반환

✅ LinkedHashSet 특징:
   - 추가: O(1)
   - 조회: O(1)
   - 삭제: O(1)
   - 순서: 삽입 순서 유지
   - 메모리: HashSet보다 약간 더 사용 (링크)

=== Set 구현체 비교 ===

1. HashSet (순서 없음):
   [Apple, Banana, Cherry, Date, Elderberry]

2. LinkedHashSet (삽입 순서):
   [Banana, Apple, Cherry, Date, Elderberry]

3. TreeSet (정렬):
   [Apple, Banana, Cherry, Date, Elderberry]

📊 비교 표:
┌──────────────────┬──────────┬────────┬──────────┐
│ 구현체           │ 순서     │ 성능   │ 사용 사례│
├──────────────────┼──────────┼────────┼──────────┤
│ HashSet          │ 없음     │ O(1)   │ 성능 중시│
│ LinkedHashSet    │ 삽입순서 │ O(1)   │ 순서필요 │
│ TreeSet          │ 정렬     │ O(logn)│ 정렬필요 │
└──────────────────┴──────────┴────────┴──────────┘

=== LRU 캐시 패턴 (LinkedHashSet 활용) ===

   ✅ 접근: A → [A]
   ✅ 접근: B → [A, B]
   ✅ 접근: C → [A, B, C]
   ✅ 접근: A → [B, C, A]
   🗑️ 제거 (LRU): B
   ✅ 접근: D → [C, A, D]

💡 LinkedHashSet으로 LRU 캐시 구현 가능!


✅ LinkedHashSet 핵심:
1. 중복 불허 + 삽입 순서 유지
2. O(1) 추가/조회/삭제 (HashSet과 동일)
3. 이중 연결 리스트로 순서 유지
4. LRU 캐시 구현에 활용
5. HashSet보다 약간 더 많은 메모리 사용
```

### 핵심 정리
- **LinkedHashSet**: HashSet + 이중 연결 리스트
- **삽입 순서**: 추가한 순서대로 유지
- **O(1) 성능**: HashSet과 동일
- **LRU 캐시**: 순서 유지 특성 활용
- **실생활 비유**: SNS 팔로워 = 순서 유지하는 LinkedHashSet

---

## 비유 4: 로또 번호 추첨 (Set의 중복 제거) 🎰

로또 번호는 1-45 중 6개를 **중복 없이** 추첨합니다. Set의 중복 제거 특성을 활용합니다.

### 실생활 상황
- **중복 불가**: 같은 번호 두 번 나올 수 없음
- **랜덤 선택**: 무작위로 6개 선택
- **자동 정렬**: 작은 번호부터 표시

### 코드 예시

```java
import java.util.*;
import java.util.stream.Collectors;

class LottoNumber implements Comparable<LottoNumber> {
    private final int number;

    public LottoNumber(int number) {
        validateRange(number);
        this.number = number;
    }

    private void validateRange(int number) {
        if (number < 1 || number > 45) {
            throw new IllegalArgumentException("로또 번호는 1-45 사이여야 합니다: " + number);
        }
    }

    public int getNumber() { return number; }

    @Override
    public int compareTo(LottoNumber other) {
        return Integer.compare(this.number, other.number);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        LottoNumber that = (LottoNumber) o;
        return number == that.number;
    }

    @Override
    public int hashCode() {
        return Objects.hash(number);
    }

    @Override
    public String toString() {
        return String.format("%02d", number);
    }
}

class LottoMachine {
    private static final int TOTAL_NUMBERS = 45;
    private static final int PICK_COUNT = 6;
    private static final Random random = new Random();

    // Set 특징 1: 중복 자동 제거로 유니크한 번호 생성
    public Set<LottoNumber> generateNumbers() {
        // TreeSet 사용: 자동 정렬 + 중복 제거
        Set<LottoNumber> numbers = new TreeSet<>();

        System.out.println("🎰 로또 번호 추첨 중...");

        while (numbers.size() < PICK_COUNT) {
            int randomNumber = random.nextInt(TOTAL_NUMBERS) + 1;
            LottoNumber lottoNumber = new LottoNumber(randomNumber);

            boolean added = numbers.add(lottoNumber);
            if (added) {
                System.out.println("   추첨: " + lottoNumber + " (" + numbers.size() + "/6)");
            } else {
                System.out.println("   중복: " + lottoNumber + " → 재추첨");
            }
        }

        return numbers;
    }

    // Set을 사용하지 않으면?
    public List<Integer> generateNumbersWithoutSet() {
        List<Integer> numbers = new ArrayList<>();

        System.out.println("\n❌ Set 없이 구현 (비효율적):");

        while (numbers.size() < PICK_COUNT) {
            int randomNumber = random.nextInt(TOTAL_NUMBERS) + 1;

            // 중복 검사 (O(n) - 느림!)
            if (!numbers.contains(randomNumber)) {
                numbers.add(randomNumber);
                System.out.println("   추첨: " + randomNumber + " (" + numbers.size() + "/6)");
            } else {
                System.out.println("   중복: " + randomNumber + " → 재추첨");
            }
        }

        // 수동 정렬 필요
        Collections.sort(numbers);

        return numbers;
    }

    // 여러 게임 생성
    public void generateMultipleGames(int count) {
        System.out.println("\n🎫 로또 " + count + "게임 자동 생성:\n");

        for (int i = 1; i <= count; i++) {
            Set<LottoNumber> numbers = new TreeSet<>();

            // Set 사용으로 간단하게 생성
            while (numbers.size() < PICK_COUNT) {
                numbers.add(new LottoNumber(random.nextInt(TOTAL_NUMBERS) + 1));
            }

            System.out.printf("%c게임: %s%n",
                (char)('A' + i - 1),
                numbers.stream()
                       .map(LottoNumber::toString)
                       .collect(Collectors.joining(", ")));
        }
    }

    // 당첨 확인
    public int checkWinning(Set<LottoNumber> myNumbers, Set<LottoNumber> winningNumbers) {
        // Set 교집합 연산 활용
        Set<LottoNumber> matches = new HashSet<>(myNumbers);
        matches.retainAll(winningNumbers);  // 교집합

        int matchCount = matches.size();

        System.out.println("\n🎯 당첨 확인:");
        System.out.println("   내 번호: " + formatNumbers(myNumbers));
        System.out.println("   당첨 번호: " + formatNumbers(winningNumbers));
        System.out.println("   일치: " + formatNumbers(matches) + " (" + matchCount + "개)");

        // 등수 계산
        String prize = switch (matchCount) {
            case 6 -> "1등 🎉";
            case 5 -> "2등 🎊";
            case 4 -> "3등 🎁";
            case 3 -> "4등 🎈";
            default -> "낙첨 😢";
        };

        System.out.println("   결과: " + prize);

        return matchCount;
    }

    private String formatNumbers(Set<LottoNumber> numbers) {
        return numbers.stream()
                      .map(LottoNumber::toString)
                      .collect(Collectors.joining(", "));
    }

    // Set 활용 패턴 시연
    public static void demonstrateSetPatterns() {
        System.out.println("\n=== Set 중복 제거 패턴 ===\n");

        // 패턴 1: 중복 제거
        List<Integer> numbersWithDuplicates = Arrays.asList(1, 2, 3, 2, 4, 3, 5, 1);
        Set<Integer> uniqueNumbers = new HashSet<>(numbersWithDuplicates);

        System.out.println("1. 중복 제거:");
        System.out.println("   원본: " + numbersWithDuplicates);
        System.out.println("   중복 제거: " + uniqueNumbers);

        // 패턴 2: 유니크한 랜덤 번호 생성
        System.out.println("\n2. 유니크한 랜덤 번호 N개 생성:");
        Set<Integer> randomNumbers = new HashSet<>();
        Random rand = new Random();

        while (randomNumbers.size() < 5) {
            randomNumbers.add(rand.nextInt(10) + 1);  // 1-10
        }
        System.out.println("   " + new TreeSet<>(randomNumbers));  // 정렬하여 출력

        // 패턴 3: 리스트를 Set으로 변환 후 다시 리스트로
        List<String> words = Arrays.asList("apple", "banana", "apple", "cherry", "banana");
        List<String> uniqueWords = new ArrayList<>(new LinkedHashSet<>(words));  // 순서 유지

        System.out.println("\n3. 중복 제거 후 순서 유지:");
        System.out.println("   원본: " + words);
        System.out.println("   결과: " + uniqueWords);

        System.out.println("\n✅ Set 활용:");
        System.out.println("   - 중복 제거: new HashSet<>(list)");
        System.out.println("   - 유니크 랜덤: Set에 랜덤 추가");
        System.out.println("   - 순서 유지 중복 제거: LinkedHashSet");
    }

    // 통계 분석
    public static void analyzeFrequency(List<Set<LottoNumber>> games) {
        System.out.println("\n=== 번호 빈도 분석 ===\n");

        Map<Integer, Integer> frequency = new HashMap<>();

        // 모든 게임의 번호 수집
        for (Set<LottoNumber> game : games) {
            for (LottoNumber number : game) {
                frequency.merge(number.getNumber(), 1, Integer::sum);
            }
        }

        // 빈도순 정렬
        List<Map.Entry<Integer, Integer>> sorted = new ArrayList<>(frequency.entrySet());
        sorted.sort((a, b) -> b.getValue().compareTo(a.getValue()));

        System.out.println("Top 10 자주 나온 번호:");
        for (int i = 0; i < Math.min(10, sorted.size()); i++) {
            Map.Entry<Integer, Integer> entry = sorted.get(i);
            System.out.printf("   %2d번: %d회%n", entry.getKey(), entry.getValue());
        }
    }
}

public class LottoMachineExample {
    public static void main(String[] args) {
        System.out.println("=== 로또 번호 추첨 시스템 (Set 중복 제거) ===\n");

        LottoMachine machine = new LottoMachine();

        // 1개 게임 생성 (상세)
        Set<LottoNumber> myNumbers = machine.generateNumbers();

        System.out.println("\n✅ 생성된 번호: " + myNumbers);

        // Set 없이 구현 비교
        List<Integer> numbersWithoutSet = machine.generateNumbersWithoutSet();
        System.out.println("\n✅ 생성된 번호: " + numbersWithoutSet);

        // 여러 게임 생성
        machine.generateMultipleGames(5);

        // 당첨 확인
        Set<LottoNumber> winningNumbers = new TreeSet<>(Arrays.asList(
            new LottoNumber(7),
            new LottoNumber(14),
            new LottoNumber(21),
            new LottoNumber(28),
            new LottoNumber(35),
            new LottoNumber(42)
        ));

        machine.checkWinning(myNumbers, winningNumbers);

        // Set 패턴
        LottoMachine.demonstrateSetPatterns();

        // 통계 분석
        List<Set<LottoNumber>> manyGames = new ArrayList<>();
        for (int i = 0; i < 100; i++) {
            Set<LottoNumber> game = new TreeSet<>();
            Random rand = new Random();
            while (game.size() < 6) {
                game.add(new LottoNumber(rand.nextInt(45) + 1));
            }
            manyGames.add(game);
        }

        LottoMachine.analyzeFrequency(manyGames);

        System.out.println("\n\n✅ Set 중복 제거 핵심:");
        System.out.println("1. 자동 중복 제거 (add() 시)");
        System.out.println("2. TreeSet으로 정렬 + 중복 제거 동시에");
        System.out.println("3. 유니크한 랜덤 값 생성에 최적");
        System.out.println("4. 집합 연산으로 당첨 확인 간단");
        System.out.println("5. List contains()보다 빠름 (O(1) vs O(n))");
    }
}
```

### 실행 결과
```
=== 로또 번호 추첨 시스템 (Set 중복 제거) ===

🎰 로또 번호 추첨 중...
   추첨: 12 (1/6)
   중복: 12 → 재추첨
   추첨: 23 (2/6)
   추첨: 07 (3/6)
   추첨: 34 (4/6)
   중복: 23 → 재추첨
   추첨: 41 (5/6)
   추첨: 19 (6/6)

✅ 생성된 번호: [07, 12, 19, 23, 34, 41]

❌ Set 없이 구현 (비효율적):
   추첨: 15 (1/6)
   추첨: 28 (2/6)
   중복: 28 → 재추첨
   추첨: 09 (3/6)
   추첨: 37 (4/6)
   추첨: 05 (5/6)
   중복: 15 → 재추첨
   추첨: 42 (6/6)

✅ 생성된 번호: [5, 9, 15, 28, 37, 42]

🎫 로또 5게임 자동 생성:

A게임: 03, 11, 22, 29, 38, 44
B게임: 01, 14, 25, 31, 36, 40
C게임: 08, 17, 23, 30, 39, 45
D게임: 05, 12, 19, 26, 33, 41
E게임: 02, 15, 24, 28, 35, 43

🎯 당첨 확인:
   내 번호: 07, 12, 19, 23, 34, 41
   당첨 번호: 07, 14, 21, 28, 35, 42
   일치: 07 (1개)
   결과: 낙첨 😢

=== Set 중복 제거 패턴 ===

1. 중복 제거:
   원본: [1, 2, 3, 2, 4, 3, 5, 1]
   중복 제거: [1, 2, 3, 4, 5]

2. 유니크한 랜덤 번호 N개 생성:
   [2, 4, 6, 8, 9]

3. 중복 제거 후 순서 유지:
   원본: [apple, banana, apple, cherry, banana]
   결과: [apple, banana, cherry]

✅ Set 활용:
   - 중복 제거: new HashSet<>(list)
   - 유니크 랜덤: Set에 랜덤 추가
   - 순서 유지 중복 제거: LinkedHashSet

=== 번호 빈도 분석 ===

Top 10 자주 나온 번호:
   23번: 18회
   12번: 17회
   34번: 16회
   07번: 15회
   41번: 15회
   19번: 14회
   28번: 14회
   15번: 13회
   36번: 13회
   05번: 12회


✅ Set 중복 제거 핵심:
1. 자동 중복 제거 (add() 시)
2. TreeSet으로 정렬 + 중복 제거 동시에
3. 유니크한 랜덤 값 생성에 최적
4. 집합 연산으로 당첨 확인 간단
5. List contains()보다 빠름 (O(1) vs O(n))
```

### 핵심 정리
- **중복 제거**: Set의 핵심 특성 활용
- **TreeSet**: 정렬 + 중복 제거 동시에
- **랜덤 생성**: while + Set.add()로 유니크 보장
- **집합 연산**: retainAll로 당첨 확인
- **실생활 비유**: 로또 추첨 = 중복 없는 Set

---

## 비유 5: 회의실 예약 시스템 (TreeSet 시간 정렬) 📅

회의실 예약은 **시간순으로 정렬**되어야 하며, **겹치는 예약**을 방지해야 합니다. TreeSet의 자동 정렬을 활용합니다.

### 실생활 상황
- **시간순 정렬**: 예약이 시간순으로 자동 정렬
- **겹침 방지**: 같은 시간에 두 예약 불가
- **다음 예약 조회**: 현재 이후 첫 예약 찾기

### 코드 예시

```java
import java.util.*;
import java.time.*;
import java.time.format.DateTimeFormatter;

class Reservation implements Comparable<Reservation> {
    private String roomName;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private String organizer;
    private String purpose;

    public Reservation(String roomName, LocalDateTime startTime, LocalDateTime endTime,
                      String organizer, String purpose) {
        validateTimes(startTime, endTime);
        this.roomName = roomName;
        this.startTime = startTime;
        this.endTime = endTime;
        this.organizer = organizer;
        this.purpose = purpose;
    }

    private void validateTimes(LocalDateTime start, LocalDateTime end) {
        if (start.isAfter(end) || start.equals(end)) {
            throw new IllegalArgumentException("시작 시간이 종료 시간보다 늦거나 같습니다");
        }
    }

    public String getRoomName() { return roomName; }
    public LocalDateTime getStartTime() { return startTime; }
    public LocalDateTime getEndTime() { return endTime; }
    public String getOrganizer() { return organizer; }
    public String getPurpose() { return purpose; }

    // TreeSet 정렬 기준: 시작 시간순
    @Override
    public int compareTo(Reservation other) {
        int timeCompare = this.startTime.compareTo(other.startTime);
        if (timeCompare != 0) {
            return timeCompare;
        }
        // 시작 시간이 같으면 종료 시간으로 비교
        return this.endTime.compareTo(other.endTime);
    }

    // 예약 시간 겹침 확인
    public boolean overlaps(Reservation other) {
        // 시작이 다른 예약의 시작~종료 사이
        // 또는 종료가 다른 예약의 시작~종료 사이
        return this.startTime.isBefore(other.endTime) &&
               this.endTime.isAfter(other.startTime);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Reservation that = (Reservation) o;
        return startTime.equals(that.startTime) && endTime.equals(that.endTime);
    }

    @Override
    public int hashCode() {
        return Objects.hash(startTime, endTime);
    }

    @Override
    public String toString() {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MM/dd HH:mm");
        return String.format("[%s ~ %s] %s - %s (%s)",
            startTime.format(formatter),
            endTime.format(formatter),
            roomName,
            purpose,
            organizer);
    }
}

class MeetingRoomScheduler {
    // TreeSet: 시간순 자동 정렬
    private TreeSet<Reservation> reservations = new TreeSet<>();

    // TreeSet 특징 1: 자동 시간순 정렬
    public boolean addReservation(Reservation reservation) {
        // 겹치는 예약 확인
        for (Reservation existing : reservations) {
            if (existing.overlaps(reservation)) {
                System.out.println("❌ 예약 실패: 시간이 겹침");
                System.out.println("   기존: " + existing);
                System.out.println("   신규: " + reservation);
                return false;
            }
        }

        boolean added = reservations.add(reservation);
        if (added) {
            System.out.println("✅ 예약 완료: " + reservation);
        }

        return added;
    }

    // TreeSet 특징 2: 정렬된 순서로 출력
    public void displaySchedule() {
        System.out.println("\n📅 회의실 예약 현황 (시간순):");
        System.out.println("=" .repeat(70));

        for (Reservation reservation : reservations) {
            System.out.println(reservation);
        }

        System.out.println("=" .repeat(70));
        System.out.println("총 " + reservations.size() + "건의 예약");
    }

    // TreeSet 특징 3: ceiling() - 다음 예약 찾기
    public Reservation findNextReservation(LocalDateTime currentTime) {
        // 현재 시간 이후 첫 예약 찾기
        Reservation dummy = new Reservation(
            "",
            currentTime,
            currentTime.plusMinutes(1),
            "",
            ""
        );

        Reservation next = reservations.ceiling(dummy);

        if (next != null) {
            System.out.println("\n🔔 다음 예약: " + next);
            Duration until = Duration.between(currentTime, next.getStartTime());
            System.out.println("   " + until.toMinutes() + "분 후 시작");
        } else {
            System.out.println("\n⚠️ 다음 예약 없음");
        }

        return next;
    }

    // TreeSet 특징 4: floor() - 이전 예약 찾기
    public Reservation findPreviousReservation(LocalDateTime currentTime) {
        Reservation dummy = new Reservation(
            "",
            currentTime,
            currentTime.plusMinutes(1),
            "",
            ""
        );

        Reservation previous = reservations.floor(dummy);

        if (previous != null) {
            System.out.println("\n📋 이전 예약: " + previous);
        } else {
            System.out.println("\n⚠️ 이전 예약 없음");
        }

        return previous;
    }

    // TreeSet 특징 5: subSet() - 특정 시간대 예약 조회
    public void displayReservationsInRange(LocalDateTime from, LocalDateTime to) {
        Reservation fromDummy = new Reservation("", from, from.plusMinutes(1), "", "");
        Reservation toDummy = new Reservation("", to, to.plusMinutes(1), "", "");

        SortedSet<Reservation> range = reservations.subSet(fromDummy, toDummy);

        System.out.println("\n📅 " + from.toLocalDate() + " 예약:");
        for (Reservation r : range) {
            System.out.println("   " + r);
        }
    }

    // 현재 진행 중인 회의
    public void findCurrentMeeting(LocalDateTime currentTime) {
        System.out.println("\n🏢 " + currentTime.format(DateTimeFormatter.ofPattern("MM/dd HH:mm")) +
                         " 현재 진행 중인 회의:");

        boolean found = false;
        for (Reservation r : reservations) {
            if (currentTime.isAfter(r.getStartTime()) && currentTime.isBefore(r.getEndTime())) {
                System.out.println("   " + r);
                found = true;
            }
        }

        if (!found) {
            System.out.println("   없음");
        }
    }

    // TreeSet 활용 통계
    public void displayStatistics() {
        if (reservations.isEmpty()) {
            System.out.println("\n📊 예약 없음");
            return;
        }

        System.out.println("\n📊 예약 통계:");

        // first(), last() 사용
        Reservation first = reservations.first();
        Reservation last = reservations.last();

        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MM/dd HH:mm");
        System.out.println("   최초 예약: " + first.getStartTime().format(formatter));
        System.out.println("   마지막 예약: " + last.getStartTime().format(formatter));

        // 총 예약 시간 계산
        long totalMinutes = reservations.stream()
            .mapToLong(r -> Duration.between(r.getStartTime(), r.getEndTime()).toMinutes())
            .sum();

        System.out.println("   총 예약 시간: " + totalMinutes + "분 (" +
                         (totalMinutes / 60) + "시간 " + (totalMinutes % 60) + "분)");

        // 주최자별 통계
        Map<String, Long> byOrganizer = new HashMap<>();
        for (Reservation r : reservations) {
            byOrganizer.merge(r.getOrganizer(), 1L, Long::sum);
        }

        System.out.println("   주최자별 예약:");
        byOrganizer.forEach((name, count) ->
            System.out.println("      " + name + ": " + count + "건"));
    }

    // TreeSet 내부 동작
    public static void demonstrateTreeSetForScheduling() {
        System.out.println("\n=== TreeSet으로 스케줄 관리 ===\n");

        System.out.println("TreeSet 장점:");
        System.out.println("   1. 자동 시간순 정렬 (Comparable)");
        System.out.println("   2. ceiling/floor로 다음/이전 예약 O(log n)");
        System.out.println("   3. subSet으로 특정 기간 예약 조회");
        System.out.println("   4. first/last로 최초/마지막 예약 즉시 조회");
        System.out.println();

        System.out.println("ArrayList 대비:");
        System.out.println("   - ArrayList: 정렬 필요 (O(n log n))");
        System.out.println("   - TreeSet: 자동 정렬 (O(log n) 삽입)");
        System.out.println();

        System.out.println("✅ 시간 기반 데이터는 TreeSet 추천");
    }
}

public class MeetingRoomSchedulerExample {
    public static void main(String[] args) {
        System.out.println("=== 회의실 예약 시스템 (TreeSet 시간 정렬) ===\n");

        MeetingRoomScheduler scheduler = new MeetingRoomScheduler();

        LocalDate today = LocalDate.now();

        // 예약 추가 (무작위 순서)
        scheduler.addReservation(new Reservation(
            "대회의실",
            LocalDateTime.of(today, LocalTime.of(14, 0)),
            LocalDateTime.of(today, LocalTime.of(15, 30)),
            "김팀장",
            "프로젝트 킥오프"
        ));

        scheduler.addReservation(new Reservation(
            "소회의실",
            LocalDateTime.of(today, LocalTime.of(10, 0)),
            LocalDateTime.of(today, LocalTime.of(11, 0)),
            "이과장",
            "주간 회의"
        ));

        scheduler.addReservation(new Reservation(
            "대회의실",
            LocalDateTime.of(today, LocalTime.of(16, 0)),
            LocalDateTime.of(today, LocalTime.of(17, 0)),
            "박대리",
            "코드 리뷰"
        ));

        // 겹치는 예약 시도
        System.out.println();
        scheduler.addReservation(new Reservation(
            "대회의실",
            LocalDateTime.of(today, LocalTime.of(14, 30)),  // 14:00~15:30와 겹침!
            LocalDateTime.of(today, LocalTime.of(15, 0)),
            "최사원",
            "1:1 미팅"
        ));

        // 전체 스케줄 (자동 정렬)
        scheduler.displaySchedule();

        // 다음 예약 찾기
        LocalDateTime now = LocalDateTime.of(today, LocalTime.of(12, 30));
        scheduler.findNextReservation(now);

        // 이전 예약 찾기
        scheduler.findPreviousReservation(now);

        // 특정 시간대 조회
        scheduler.displayReservationsInRange(
            LocalDateTime.of(today, LocalTime.of(13, 0)),
            LocalDateTime.of(today, LocalTime.of(18, 0))
        );

        // 현재 진행 중인 회의
        LocalDateTime currentTime = LocalDateTime.of(today, LocalTime.of(14, 30));
        scheduler.findCurrentMeeting(currentTime);

        // 통계
        scheduler.displayStatistics();

        // TreeSet 활용법
        MeetingRoomScheduler.demonstrateTreeSetForScheduling();

        System.out.println("\n\n✅ TreeSet 시간 정렬 핵심:");
        System.out.println("1. Comparable로 시간순 자동 정렬");
        System.out.println("2. ceiling/floor로 다음/이전 조회");
        System.out.println("3. subSet으로 기간 검색");
        System.out.println("4. first/last로 최초/마지막 즉시 조회");
        System.out.println("5. 스케줄 관리에 최적화");
    }
}
```

### 실행 결과
```
=== 회의실 예약 시스템 (TreeSet 시간 정렬) ===

✅ 예약 완료: [01/15 14:00 ~ 01/15 15:30] 대회의실 - 프로젝트 킥오프 (김팀장)
✅ 예약 완료: [01/15 10:00 ~ 01/15 11:00] 소회의실 - 주간 회의 (이과장)
✅ 예약 완료: [01/15 16:00 ~ 01/15 17:00] 대회의실 - 코드 리뷰 (박대리)

❌ 예약 실패: 시간이 겹침
   기존: [01/15 14:00 ~ 01/15 15:30] 대회의실 - 프로젝트 킥오프 (김팀장)
   신규: [01/15 14:30 ~ 01/15 15:00] 대회의실 - 1:1 미팅 (최사원)

📅 회의실 예약 현황 (시간순):
======================================================================
[01/15 10:00 ~ 01/15 11:00] 소회의실 - 주간 회의 (이과장)
[01/15 14:00 ~ 01/15 15:30] 대회의실 - 프로젝트 킥오프 (김팀장)
[01/15 16:00 ~ 01/15 17:00] 대회의실 - 코드 리뷰 (박대리)
======================================================================
총 3건의 예약

🔔 다음 예약: [01/15 14:00 ~ 01/15 15:30] 대회의실 - 프로젝트 킥오프 (김팀장)
   90분 후 시작

📋 이전 예약: [01/15 10:00 ~ 01/15 11:00] 소회의실 - 주간 회의 (이과장)

📅 2025-01-15 예약:
   [01/15 14:00 ~ 01/15 15:30] 대회의실 - 프로젝트 킥오프 (김팀장)
   [01/15 16:00 ~ 01/15 17:00] 대회의실 - 코드 리뷰 (박대리)

🏢 01/15 14:30 현재 진행 중인 회의:
   [01/15 14:00 ~ 01/15 15:30] 대회의실 - 프로젝트 킥오프 (김팀장)

📊 예약 통계:
   최초 예약: 01/15 10:00
   마지막 예약: 01/15 16:00
   총 예약 시간: 210분 (3시간 30분)
   주최자별 예약:
      이과장: 1건
      김팀장: 1건
      박대리: 1건

=== TreeSet으로 스케줄 관리 ===

TreeSet 장점:
   1. 자동 시간순 정렬 (Comparable)
   2. ceiling/floor로 다음/이전 예약 O(log n)
   3. subSet으로 특정 기간 예약 조회
   4. first/last로 최초/마지막 예약 즉시 조회

ArrayList 대비:
   - ArrayList: 정렬 필요 (O(n log n))
   - TreeSet: 자동 정렬 (O(log n) 삽입)

✅ 시간 기반 데이터는 TreeSet 추천


✅ TreeSet 시간 정렬 핵심:
1. Comparable로 시간순 자동 정렬
2. ceiling/floor로 다음/이전 조회
3. subSet으로 기간 검색
4. first/last로 최초/마지막 즉시 조회
5. 스케줄 관리에 최적화
```

### 핵심 정리
- **TreeSet**: 시간순 자동 정렬
- **ceiling/floor**: 다음/이전 예약 빠르게 찾기
- **subSet**: 특정 기간 조회
- **겹침 방지**: 삽입 전 검증
- **실생활 비유**: 회의실 예약 = 시간 정렬 TreeSet

---

## 🎯 Part 1 전체 핵심 정리

### Set 인터페이스 특징
1. **중복 불허** (No Duplicates): 같은 요소 추가 불가
2. **equals()와 hashCode()**: 중복 판단 기준
3. **순서**: 구현체에 따라 다름
4. **null 허용**: 구현체에 따라 다름

### 구현체 비교

| 구현체 | 내부 구조 | 순서 | 추가 | 조회 | 삭제 | null 허용 | 사용 사례 |
|--------|----------|------|------|------|------|----------|-----------|
| **HashSet** | HashMap | 없음 | O(1) | O(1) | O(1) | ✅ (1개) | 일반적, 성능 중시 |
| **LinkedHashSet** | HashMap + 링크 | 삽입순 | O(1) | O(1) | O(1) | ✅ (1개) | 순서 유지 필요 |
| **TreeSet** | Red-Black Tree | 정렬 | O(log n) | O(log n) | O(log n) | ❌ | 정렬, 범위 검색 |

### 선택 기준

```
성능 중시 → HashSet
├─ 중복 제거
├─ 빠른 조회/추가/삭제
└─ 순서 필요 없음

순서 유지 필요 → LinkedHashSet
├─ 삽입 순서 기억
├─ LRU 캐시
└─ HashSet 성능 + 순서

정렬 필요 → TreeSet
├─ 자동 정렬
├─ 범위 검색
└─ 스케줄/시간 관리
```

### 주요 메서드

```java
// 기본 연산
boolean add(E e)           // 추가
boolean remove(Object o)   // 제거
boolean contains(Object o) // 포함 여부
int size()                 // 크기
void clear()               // 전체 삭제

// 집합 연산
addAll(Collection c)       // 합집합
retainAll(Collection c)    // 교집합
removeAll(Collection c)    // 차집합

// TreeSet 전용
E first()                  // 최소 요소
E last()                   // 최대 요소
E ceiling(E e)             // e 이상 최소
E floor(E e)               // e 이하 최대
SortedSet<E> subSet(E from, E to)  // 범위 조회
```

### 실생활 비유 요약
1. **학생 명부** = HashSet (중복 불가, O(1))
2. **ISBN 관리** = TreeSet (자동 정렬, 범위 검색)
3. **SNS 팔로워** = LinkedHashSet (순서 유지)
4. **로또 추첨** = Set (중복 제거)
5. **회의실 예약** = TreeSet (시간 정렬)

---

**다음 Part 2에서는**: 3개 기업 사례 (토스, 배민, 네이버) + 4개 주니어 실수 시나리오를 다룹니다.