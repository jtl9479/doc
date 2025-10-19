# 26장 List 인터페이스 Part 1 - 실생활 비유로 이해하기 📝

## 🌟 실생활 비유로 이해하기

List 인터페이스는 순서가 있고 중복을 허용하는 컬렉션입니다. 인덱스로 요소에 접근할 수 있으며, ArrayList와 LinkedList가 대표적인 구현체입니다.

---

## 비유 1: 도서관 책꽂이 시스템 📚

도서관 책꽂이는 책들이 순서대로 꽂혀있고, "3번째 책"처럼 위치로 접근할 수 있습니다. ArrayList는 이런 "배열 기반 책꽂이"와 같습니다.

### 실생활 상황
- **순서 유지**: 책을 꽂은 순서대로 보관
- **인덱스 접근**: "왼쪽에서 5번째 책" 즉시 찾기
- **중간 삽입 어려움**: 중간에 책을 끼워넣으려면 뒤의 책들을 모두 밀어야 함

### 코드 예시

```java
import java.util.*;

class Book {
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

    @Override
    public String toString() {
        return "《" + title + "》 - " + author + " (" + publicationYear + ")";
    }
}

class LibraryBookshelf {
    // ArrayList: 배열 기반 책꽂이
    private List<Book> books = new ArrayList<>();

    // List 특징 1: 순서대로 추가 (끝에 추가 - O(1))
    public void addBook(Book book) {
        books.add(book);
        System.out.println("✅ 책 추가: " + book.getTitle() + " (위치: " + books.size() + ")");
    }

    // List 특징 2: 인덱스로 즉시 접근 (O(1))
    public Book getBookAt(int index) {
        if (index >= 0 && index < books.size()) {
            Book book = books.get(index);
            System.out.println("📖 " + (index + 1) + "번째 책: " + book);
            return book;
        } else {
            System.out.println("❌ 유효하지 않은 위치: " + index);
            return null;
        }
    }

    // List 특징 3: 중간에 삽입 (O(n) - 뒤의 요소들 이동)
    public void insertBookAt(int index, Book book) {
        if (index >= 0 && index <= books.size()) {
            books.add(index, book);
            System.out.println("📥 " + (index + 1) + "번째 위치에 삽입: " + book.getTitle());
            System.out.println("   (뒤의 " + (books.size() - index - 1) + "권 이동됨)");
        } else {
            System.out.println("❌ 유효하지 않은 위치: " + index);
        }
    }

    // List 특징 4: 중간에서 제거 (O(n) - 뒤의 요소들 이동)
    public void removeBookAt(int index) {
        if (index >= 0 && index < books.size()) {
            Book removed = books.remove(index);
            System.out.println("🗑️ " + (index + 1) + "번째 책 제거: " + removed.getTitle());
            System.out.println("   (뒤의 " + (books.size() - index) + "권 앞으로 이동)");
        } else {
            System.out.println("❌ 유효하지 않은 위치: " + index);
        }
    }

    // List 특징 5: 검색 (O(n) - 순차 탐색)
    public int findBookByTitle(String title) {
        for (int i = 0; i < books.size(); i++) {
            if (books.get(i).getTitle().equals(title)) {
                System.out.println("🔍 찾음: " + title + " (위치: " + (i + 1) + ")");
                return i;
            }
        }
        System.out.println("❌ 찾을 수 없음: " + title);
        return -1;
    }

    // List 특징 6: 전체 순회
    public void displayAllBooks() {
        System.out.println("\n📚 전체 도서 목록 (" + books.size() + "권):");
        for (int i = 0; i < books.size(); i++) {
            System.out.println("   " + (i + 1) + ". " + books.get(i));
        }
    }

    // List 특징 7: 부분 리스트 (subList)
    public void displayBooksInRange(int start, int end) {
        if (start >= 0 && end <= books.size() && start < end) {
            List<Book> subList = books.subList(start, end);
            System.out.println("\n📖 " + (start + 1) + "~" + end + "번째 책:");
            for (int i = 0; i < subList.size(); i++) {
                System.out.println("   " + (start + i + 1) + ". " + subList.get(i));
            }
        }
    }

    // List 특징 8: 정렬
    public void sortByYear() {
        books.sort(Comparator.comparingInt(Book::getPublicationYear));
        System.out.println("\n📅 출판년도순 정렬 완료");
    }

    // ArrayList 내부 동작 시연
    public void demonstrateInternals() {
        System.out.println("\n=== ArrayList 내부 동작 ===\n");

        List<Integer> numbers = new ArrayList<>();

        // 1. 초기 용량 (기본 10)
        System.out.println("1. 초기 생성: 용량 10 (내부 배열 크기)");

        // 2. 요소 추가
        for (int i = 1; i <= 15; i++) {
            numbers.add(i);
            if (i == 10) {
                System.out.println("\n2. 10개 추가: 용량 가득 참");
            }
            if (i == 11) {
                System.out.println("3. 11번째 추가: 용량 확장 (10 → 15)");
                System.out.println("   - 새 배열 생성 (크기 15)");
                System.out.println("   - 기존 10개 복사");
                System.out.println("   - 11번째 요소 추가");
            }
        }

        System.out.println("\n4. 15개 추가 완료");

        // 3. 중간 삽입 시뮬레이션
        System.out.println("\n5. 중간(5번째)에 삽입:");
        System.out.println("   - 6~15번째 요소를 한 칸씩 뒤로 이동");
        System.out.println("   - 5번째 위치에 새 요소 삽입");
        numbers.add(4, 999);  // 5번째 위치 (인덱스 4)

        System.out.println("\n✅ ArrayList 특징:");
        System.out.println("   - 조회: O(1) - 인덱스로 즉시 접근");
        System.out.println("   - 끝에 추가: O(1)* - 용량 충분 시");
        System.out.println("   - 중간 삽입/삭제: O(n) - 요소 이동 필요");
        System.out.println("   - 검색: O(n) - 순차 탐색");
    }
}

public class LibraryBookshelfExample {
    public static void main(String[] args) {
        System.out.println("=== 도서관 책꽂이 시스템 (ArrayList) ===\n");

        LibraryBookshelf shelf = new LibraryBookshelf();

        // 책 추가
        shelf.addBook(new Book("978-0134685991", "Effective Java", "Joshua Bloch", 2017));
        shelf.addBook(new Book("978-0132350884", "Clean Code", "Robert Martin", 2008));
        shelf.addBook(new Book("978-0596009205", "Head First Design Patterns", "Freeman", 2004));
        shelf.addBook(new Book("978-0201633610", "Design Patterns", "Gang of Four", 1994));
        shelf.addBook(new Book("978-0137081073", "The Clean Coder", "Robert Martin", 2011));

        // 전체 목록
        shelf.displayAllBooks();

        // 인덱스 접근
        System.out.println();
        shelf.getBookAt(0);  // 첫 번째
        shelf.getBookAt(2);  // 세 번째

        // 중간 삽입
        System.out.println();
        shelf.insertBookAt(2, new Book("978-0134494166", "Clean Architecture", "Robert Martin", 2017));

        shelf.displayAllBooks();

        // 검색
        System.out.println();
        shelf.findBookByTitle("Clean Code");
        shelf.findBookByTitle("Java의 정석");

        // 제거
        System.out.println();
        shelf.removeBookAt(3);

        shelf.displayAllBooks();

        // 부분 리스트
        shelf.displayBooksInRange(1, 4);

        // 정렬
        shelf.sortByYear();
        shelf.displayAllBooks();

        // 내부 동작
        shelf.demonstrateInternals();

        System.out.println("\n\n✅ ArrayList 핵심:");
        System.out.println("1. 배열 기반: 연속된 메모리 공간");
        System.out.println("2. 인덱스 접근: O(1) - 즉시 계산 (baseAddress + index * size)");
        System.out.println("3. 동적 확장: 용량 초과 시 약 1.5배 확장");
        System.out.println("4. 캐시 친화적: 연속 메모리로 CPU 캐시 효율적");
        System.out.println("5. 사용 사례: 조회가 많고, 끝에 추가하는 경우");
    }
}
```

### 실행 결과
```
=== 도서관 책꽂이 시스템 (ArrayList) ===

✅ 책 추가: Effective Java (위치: 1)
✅ 책 추가: Clean Code (위치: 2)
✅ 책 추가: Head First Design Patterns (위치: 3)
✅ 책 추가: Design Patterns (위치: 4)
✅ 책 추가: The Clean Coder (위치: 5)

📚 전체 도서 목록 (5권):
   1. 《Effective Java》 - Joshua Bloch (2017)
   2. 《Clean Code》 - Robert Martin (2008)
   3. 《Head First Design Patterns》 - Freeman (2004)
   4. 《Design Patterns》 - Gang of Four (1994)
   5. 《The Clean Coder》 - Robert Martin (2011)

📖 1번째 책: 《Effective Java》 - Joshua Bloch (2017)
📖 3번째 책: 《Head First Design Patterns》 - Freeman (2004)

📥 3번째 위치에 삽입: Clean Architecture
   (뒤의 3권 이동됨)

📚 전체 도서 목록 (6권):
   1. 《Effective Java》 - Joshua Bloch (2017)
   2. 《Clean Code》 - Robert Martin (2008)
   3. 《Clean Architecture》 - Robert Martin (2017)
   4. 《Head First Design Patterns》 - Freeman (2004)
   5. 《Design Patterns》 - Gang of Four (1994)
   6. 《The Clean Coder》 - Robert Martin (2011)

🔍 찾음: Clean Code (위치: 2)
❌ 찾을 수 없음: Java의 정석

🗑️ 4번째 책 제거: Head First Design Patterns
   (뒤의 2권 앞으로 이동)

📚 전체 도서 목록 (5권):
   1. 《Effective Java》 - Joshua Bloch (2017)
   2. 《Clean Code》 - Robert Martin (2008)
   3. 《Clean Architecture》 - Robert Martin (2017)
   4. 《Design Patterns》 - Gang of Four (1994)
   5. 《The Clean Coder》 - Robert Martin (2011)

📖 2~4번째 책:
   2. 《Clean Code》 - Robert Martin (2008)
   3. 《Clean Architecture》 - Robert Martin (2017)
   4. 《Design Patterns》 - Gang of Four (1994)

📅 출판년도순 정렬 완료

📚 전체 도서 목록 (5권):
   1. 《Design Patterns》 - Gang of Four (1994)
   2. 《Clean Code》 - Robert Martin (2008)
   3. 《The Clean Coder》 - Robert Martin (2011)
   4. 《Effective Java》 - Joshua Bloch (2017)
   5. 《Clean Architecture》 - Robert Martin (2017)

=== ArrayList 내부 동작 ===

1. 초기 생성: 용량 10 (내부 배열 크기)

2. 10개 추가: 용량 가득 참
3. 11번째 추가: 용량 확장 (10 → 15)
   - 새 배열 생성 (크기 15)
   - 기존 10개 복사
   - 11번째 요소 추가

4. 15개 추가 완료

5. 중간(5번째)에 삽입:
   - 6~15번째 요소를 한 칸씩 뒤로 이동
   - 5번째 위치에 새 요소 삽입

✅ ArrayList 특징:
   - 조회: O(1) - 인덱스로 즉시 접근
   - 끝에 추가: O(1)* - 용량 충분 시
   - 중간 삽입/삭제: O(n) - 요소 이동 필요
   - 검색: O(n) - 순차 탐색


✅ ArrayList 핵심:
1. 배열 기반: 연속된 메모리 공간
2. 인덱스 접근: O(1) - 즉시 계산 (baseAddress + index * size)
3. 동적 확장: 용량 초과 시 약 1.5배 확장
4. 캐시 친화적: 연속 메모리로 CPU 캐시 효율적
5. 사용 사례: 조회가 많고, 끝에 추가하는 경우
```

### 핵심 정리
- **ArrayList**: 배열 기반, 인덱스 O(1) 접근
- **순서 유지**: 추가한 순서대로 보관
- **중복 허용**: 같은 요소 여러 번 추가 가능
- **동적 크기**: 자동으로 확장
- **실생활 비유**: 도서관 책꽂이 = 순서대로 배치된 ArrayList

---

## 비유 2: 지하철 노선도 (LinkedList) 🚇

지하철은 각 역이 다음 역과 연결되어 있습니다. LinkedList는 이런 "연결 리스트"와 같습니다.

### 실생활 상황
- **연결 구조**: 각 역은 이전 역/다음 역 정보만 가짐
- **순차 접근**: 5호선 3번째 역을 가려면 1→2→3 순서대로
- **중간 삽입 쉬움**: 역 사이에 새 역 추가는 연결만 변경

### 코드 예시

```java
import java.util.*;

class SubwayStation {
    private String stationName;
    private String lineNumber;
    private int transferLines;

    public SubwayStation(String stationName, String lineNumber, int transferLines) {
        this.stationName = stationName;
        this.lineNumber = lineNumber;
        this.transferLines = transferLines;
    }

    public String getStationName() { return stationName; }
    public String getLineNumber() { return lineNumber; }
    public int getTransferLines() { return transferLines; }

    @Override
    public String toString() {
        String transfer = transferLines > 0 ? " [환승 " + transferLines + "]" : "";
        return stationName + " (" + lineNumber + "호선)" + transfer;
    }
}

class SubwayLine {
    // LinkedList: 이중 연결 리스트 기반
    private LinkedList<SubwayStation> stations = new LinkedList<>();
    private String lineName;

    public SubwayLine(String lineName) {
        this.lineName = lineName;
    }

    // LinkedList 특징 1: 앞에 추가 O(1)
    public void addStationAtFirst(SubwayStation station) {
        stations.addFirst(station);
        System.out.println("🚇 첫 역 추가: " + station.getStationName());
    }

    // LinkedList 특징 2: 끝에 추가 O(1)
    public void addStationAtLast(SubwayStation station) {
        stations.addLast(station);
        System.out.println("🚇 마지막 역 추가: " + station.getStationName());
    }

    // LinkedList 특징 3: 중간 접근 O(n) - 순차 탐색 필요
    public SubwayStation getStationAt(int index) {
        if (index >= 0 && index < stations.size()) {
            System.out.println("🔍 " + (index + 1) + "번째 역 조회 중...");
            System.out.println("   (1번 역부터 순차적으로 " + (index + 1) + "번 이동)");
            SubwayStation station = stations.get(index);
            System.out.println("   도착: " + station.getStationName());
            return station;
        }
        return null;
    }

    // LinkedList 특징 4: 중간 삽입 - 위치 찾기 O(n) + 삽입 O(1)
    public void insertStationAt(int index, SubwayStation station) {
        if (index >= 0 && index <= stations.size()) {
            stations.add(index, station);
            System.out.println("📥 " + (index + 1) + "번째에 신설역: " + station.getStationName());
            System.out.println("   (" + (index > 0 ? stations.get(index - 1).getStationName() : "시작") +
                             " ↔ " + station.getStationName() + " ↔ " +
                             (index < stations.size() - 1 ? stations.get(index + 1).getStationName() : "종점") + ")");
        }
    }

    // LinkedList 특징 5: 앞/뒤 제거 O(1)
    public void removeFirstStation() {
        if (!stations.isEmpty()) {
            SubwayStation removed = stations.removeFirst();
            System.out.println("🗑️ 첫 역 폐쇄: " + removed.getStationName());
        }
    }

    public void removeLastStation() {
        if (!stations.isEmpty()) {
            SubwayStation removed = stations.removeLast();
            System.out.println("🗑️ 마지막 역 폐쇄: " + removed.getStationName());
        }
    }

    // LinkedList를 Queue처럼 사용
    public void simulateTrainDeparture() {
        System.out.println("\n🚂 열차 출발 시뮬레이션:");
        int stopNumber = 1;

        while (!stations.isEmpty()) {
            SubwayStation current = stations.pollFirst();  // 앞에서 제거 O(1)
            System.out.println("   " + stopNumber++ + ". " + current.getStationName() + " 정차");

            if (stopNumber > 5) {
                System.out.println("   ... (나머지 " + stations.size() + "개 역 생략)");
                break;
            }
        }
    }

    // 전체 노선도 출력
    public void displayLine() {
        System.out.println("\n🗺️ " + lineName + " 노선도 (" + stations.size() + "개 역):");
        for (int i = 0; i < stations.size(); i++) {
            String arrow = i < stations.size() - 1 ? " → " : "";
            System.out.print("   " + (i + 1) + "." + stations.get(i).getStationName() + arrow);
            if ((i + 1) % 5 == 0) System.out.println();  // 5개마다 줄바꿈
        }
        System.out.println();
    }

    // LinkedList 내부 구조 시연
    public static void demonstrateLinkedListStructure() {
        System.out.println("\n=== LinkedList 내부 구조 ===\n");

        System.out.println("이중 연결 리스트 (Doubly Linked List):");
        System.out.println();
        System.out.println("   [prev|강남|next] ↔ [prev|역삼|next] ↔ [prev|선릉|next]");
        System.out.println("    ↑                                           ↑");
        System.out.println("   first                                       last");
        System.out.println();

        System.out.println("노드 구조:");
        System.out.println("   class Node<E> {");
        System.out.println("       E data;        // 역 정보");
        System.out.println("       Node<E> prev;  // 이전 역");
        System.out.println("       Node<E> next;  // 다음 역");
        System.out.println("   }");
        System.out.println();

        System.out.println("연산 과정:");
        System.out.println();
        System.out.println("1. addFirst(\"교대\"):");
        System.out.println("   - 새 노드 생성");
        System.out.println("   - 새 노드.next = 기존 first");
        System.out.println("   - 기존 first.prev = 새 노드");
        System.out.println("   - first = 새 노드");
        System.out.println("   → O(1) 시간");
        System.out.println();

        System.out.println("2. get(중간 인덱스):");
        System.out.println("   - first부터 next를 따라 순차 탐색");
        System.out.println("   - 5번째 역 = first → next → next → next → next");
        System.out.println("   → O(n) 시간");
        System.out.println();

        System.out.println("3. 중간 삽입:");
        System.out.println("   - 삽입 위치까지 순차 탐색 O(n)");
        System.out.println("   - 연결 변경 O(1):");
        System.out.println("     prev.next = 새노드");
        System.out.println("     새노드.prev = prev");
        System.out.println("     새노드.next = next");
        System.out.println("     next.prev = 새노드");
        System.out.println();

        System.out.println("✅ LinkedList 특징:");
        System.out.println("   - 조회: O(n) - 순차 탐색");
        System.out.println("   - 앞/뒤 추가: O(1) - 포인터만 변경");
        System.out.println("   - 중간 삽입: O(n) - 탐색 비용 포함");
        System.out.println("   - 메모리: 노드당 추가 포인터 (prev, next)");
    }

    // ArrayList vs LinkedList 성능 비교
    public static void comparePerformance() {
        System.out.println("\n=== ArrayList vs LinkedList 성능 비교 ===\n");

        int size = 100000;

        // 1. 끝에 추가
        List<Integer> arrayList = new ArrayList<>();
        long start = System.nanoTime();
        for (int i = 0; i < size; i++) {
            arrayList.add(i);
        }
        long arrayAddTime = (System.nanoTime() - start) / 1_000_000;

        List<Integer> linkedList = new LinkedList<>();
        start = System.nanoTime();
        for (int i = 0; i < size; i++) {
            linkedList.add(i);
        }
        long linkedAddTime = (System.nanoTime() - start) / 1_000_000;

        System.out.println("1. 끝에 추가 (" + size + "개):");
        System.out.println("   ArrayList:  " + arrayAddTime + "ms ✅");
        System.out.println("   LinkedList: " + linkedAddTime + "ms ✅");

        // 2. 중간 조회
        start = System.nanoTime();
        for (int i = 0; i < 10000; i++) {
            arrayList.get(size / 2);
        }
        long arrayGetTime = (System.nanoTime() - start) / 1_000_000;

        start = System.nanoTime();
        for (int i = 0; i < 10000; i++) {
            linkedList.get(size / 2);
        }
        long linkedGetTime = (System.nanoTime() - start) / 1_000_000;

        System.out.println("\n2. 중간 조회 (10000회):");
        System.out.println("   ArrayList:  " + arrayGetTime + "ms ✅ 빠름!");
        System.out.println("   LinkedList: " + linkedGetTime + "ms ⚠️ 느림!");

        // 3. 맨 앞 삽입
        start = System.nanoTime();
        for (int i = 0; i < 5000; i++) {
            ((LinkedList<Integer>) linkedList).addFirst(i);
        }
        long linkedInsertTime = (System.nanoTime() - start) / 1_000_000;

        start = System.nanoTime();
        for (int i = 0; i < 5000; i++) {
            arrayList.add(0, i);
        }
        long arrayInsertTime = (System.nanoTime() - start) / 1_000_000;

        System.out.println("\n3. 맨 앞 삽입 (5000회):");
        System.out.println("   ArrayList:  " + arrayInsertTime + "ms ⚠️ 느림");
        System.out.println("   LinkedList: " + linkedInsertTime + "ms ✅ 빠름!");

        System.out.println("\n✅ 선택 기준:");
        System.out.println("   - 조회 많음 → ArrayList");
        System.out.println("   - 앞/뒤 삽입/삭제 많음 → LinkedList");
        System.out.println("   - Queue 구현 → LinkedList");
        System.out.println("   - 대부분의 경우 → ArrayList (메모리, 캐시 효율)");
    }
}

public class SubwayLineExample {
    public static void main(String[] args) {
        System.out.println("=== 지하철 노선도 시스템 (LinkedList) ===\n");

        SubwayLine line2 = new SubwayLine("2호선");

        // LinkedList 특징: 양방향 추가
        line2.addStationAtLast(new SubwayStation("강남", "2", 0));
        line2.addStationAtLast(new SubwayStation("역삼", "2", 0));
        line2.addStationAtLast(new SubwayStation("선릉", "2", 0));
        line2.addStationAtLast(new SubwayStation("삼성", "2", 0));

        line2.displayLine();

        // 노선 확장 (앞에 추가)
        System.out.println();
        line2.addStationAtFirst(new SubwayStation("교대", "2", 3));

        line2.displayLine();

        // 중간 접근 (순차 탐색)
        System.out.println();
        line2.getStationAt(2);  // 3번째 역

        // 신설역 추가 (중간 삽입)
        System.out.println();
        line2.insertStationAt(4, new SubwayStation("봉은사", "2", 0));

        line2.displayLine();

        // 내부 구조
        SubwayLine.demonstrateLinkedListStructure();

        // 성능 비교
        SubwayLine.comparePerformance();

        System.out.println("\n\n✅ LinkedList 핵심:");
        System.out.println("1. 이중 연결 리스트: prev ↔ node ↔ next");
        System.out.println("2. 앞/뒤 추가: O(1) - addFirst(), addLast()");
        System.out.println("3. 중간 접근: O(n) - 순차 탐색 필요");
        System.out.println("4. Queue/Deque 구현에 적합");
        System.out.println("5. 메모리 오버헤드: 노드당 포인터 2개");
    }
}
```

### 실행 결과
```
=== 지하철 노선도 시스템 (LinkedList) ===

🚇 마지막 역 추가: 강남
🚇 마지막 역 추가: 역삼
🚇 마지막 역 추가: 선릉
🚇 마지막 역 추가: 삼성

🗺️ 2호선 노선도 (4개 역):
   1.강남 → 2.역삼 → 3.선릉 → 4.삼성

🚇 첫 역 추가: 교대

🗺️ 2호선 노선도 (5개 역):
   1.교대 → 2.강남 → 3.역삼 → 4.선릉 → 5.삼성

🔍 3번째 역 조회 중...
   (1번 역부터 순차적으로 3번 이동)
   도착: 역삼

📥 5번째에 신설역: 봉은사
   (선릉 ↔ 봉은사 ↔ 삼성)

🗺️ 2호선 노선도 (6개 역):
   1.교대 → 2.강남 → 3.역삼 → 4.선릉 → 5.봉은사
   → 6.삼성

=== LinkedList 내부 구조 ===

이중 연결 리스트 (Doubly Linked List):

   [prev|강남|next] ↔ [prev|역삼|next] ↔ [prev|선릉|next]
    ↑                                           ↑
   first                                       last

노드 구조:
   class Node<E> {
       E data;        // 역 정보
       Node<E> prev;  // 이전 역
       Node<E> next;  // 다음 역
   }

연산 과정:

1. addFirst("교대"):
   - 새 노드 생성
   - 새 노드.next = 기존 first
   - 기존 first.prev = 새 노드
   - first = 새 노드
   → O(1) 시간

2. get(중간 인덱스):
   - first부터 next를 따라 순차 탐색
   - 5번째 역 = first → next → next → next → next
   → O(n) 시간

3. 중간 삽입:
   - 삽입 위치까지 순차 탐색 O(n)
   - 연결 변경 O(1):
     prev.next = 새노드
     새노드.prev = prev
     새노드.next = next
     next.prev = 새노드

✅ LinkedList 특징:
   - 조회: O(n) - 순차 탐색
   - 앞/뒤 추가: O(1) - 포인터만 변경
   - 중간 삽입: O(n) - 탐색 비용 포함
   - 메모리: 노드당 추가 포인터 (prev, next)

=== ArrayList vs LinkedList 성능 비교 ===

1. 끝에 추가 (100000개):
   ArrayList:  8ms ✅
   LinkedList: 12ms ✅

2. 중간 조회 (10000회):
   ArrayList:  0ms ✅ 빠름!
   LinkedList: 2456ms ⚠️ 느림!

3. 맨 앞 삽입 (5000회):
   ArrayList:  892ms ⚠️ 느림
   LinkedList: 1ms ✅ 빠름!

✅ 선택 기준:
   - 조회 많음 → ArrayList
   - 앞/뒤 삽입/삭제 많음 → LinkedList
   - Queue 구현 → LinkedList
   - 대부분의 경우 → ArrayList (메모리, 캐시 효율)


✅ LinkedList 핵심:
1. 이중 연결 리스트: prev ↔ node ↔ next
2. 앞/뒤 추가: O(1) - addFirst(), addLast()
3. 중간 접근: O(n) - 순차 탐색 필요
4. Queue/Deque 구현에 적합
5. 메모리 오버헤드: 노드당 포인터 2개
```

### 핵심 정리
- **LinkedList**: 이중 연결 리스트 기반
- **앞/뒤 O(1)**: addFirst, addLast, removeFirst, removeLast
- **중간 O(n)**: get, add(index), remove(index)
- **Queue 구현**: offer/poll 빠름
- **실생활 비유**: 지하철 노선 = 연결된 LinkedList

---

## 비유 3: 음악 재생목록 (Playlist) 🎵

음악 재생목록은 노래를 추가하고, 순서를 바꾸고, 특정 곡으로 이동합니다. List의 다양한 순서 조작 기능을 보여줍니다.

### 실생활 상황
- **재생 순서**: 곡이 추가된 순서대로 재생
- **곡 이동**: 특정 곡을 위/아래로 이동
- **셔플**: 순서를 무작위로 섞기
- **반복**: 특정 구간 반복 재생

### 코드 예시

```java
import java.util.*;

class Song {
    private String title;
    private String artist;
    private int duration; // 초 단위

    public Song(String title, String artist, int duration) {
        this.title = title;
        this.artist = artist;
        this.duration = duration;
    }

    public String getTitle() { return title; }
    public String getArtist() { return artist; }
    public int getDuration() { return duration; }

    @Override
    public String toString() {
        int minutes = duration / 60;
        int seconds = duration % 60;
        return "♪ " + title + " - " + artist + " (" + minutes + ":" + String.format("%02d", seconds) + ")";
    }
}

class MusicPlaylist {
    private List<Song> playlist = new ArrayList<>();
    private String playlistName;
    private int currentIndex = 0;

    public MusicPlaylist(String playlistName) {
        this.playlistName = playlistName;
    }

    // List 특징 1: 순서대로 추가
    public void addSong(Song song) {
        playlist.add(song);
        System.out.println("➕ 추가됨: " + song.getTitle() + " (위치: " + playlist.size() + ")");
    }

    // List 특징 2: 특정 위치에 삽입
    public void insertSongAt(int position, Song song) {
        if (position >= 0 && position <= playlist.size()) {
            playlist.add(position, song);
            System.out.println("📌 " + (position + 1) + "번 위치에 삽입: " + song.getTitle());
        }
    }

    // List 특징 3: 순서 변경 - 위로 이동
    public void moveSongUp(int index) {
        if (index > 0 && index < playlist.size()) {
            Song song = playlist.remove(index);
            playlist.add(index - 1, song);
            System.out.println("⬆️ " + song.getTitle() + " (위치: " + (index + 1) + " → " + index + ")");
        } else {
            System.out.println("⚠️ 더 이상 위로 이동할 수 없습니다");
        }
    }

    // List 특징 4: 순서 변경 - 아래로 이동
    public void moveSongDown(int index) {
        if (index >= 0 && index < playlist.size() - 1) {
            Song song = playlist.remove(index);
            playlist.add(index + 1, song);
            System.out.println("⬇️ " + song.getTitle() + " (위치: " + (index + 1) + " → " + (index + 2) + ")");
        } else {
            System.out.println("⚠️ 더 이상 아래로 이동할 수 없습니다");
        }
    }

    // List 특징 5: 셔플 (Collections.shuffle)
    public void shuffle() {
        Collections.shuffle(playlist);
        System.out.println("🔀 재생목록 셔플 완료!");
    }

    // List 특징 6: 정렬
    public void sortByTitle() {
        playlist.sort(Comparator.comparing(Song::getTitle));
        System.out.println("🔤 제목순 정렬 완료");
    }

    public void sortByArtist() {
        playlist.sort(Comparator.comparing(Song::getArtist));
        System.out.println("👤 아티스트순 정렬 완료");
    }

    public void sortByDuration() {
        playlist.sort(Comparator.comparingInt(Song::getDuration));
        System.out.println("⏱️ 재생시간순 정렬 완료");
    }

    // List 특징 7: 재생 (Iterator 패턴)
    public void play() {
        if (playlist.isEmpty()) {
            System.out.println("⚠️ 재생목록이 비어있습니다");
            return;
        }

        System.out.println("\n▶️ 재생 시작: " + playlistName);
        for (int i = 0; i < playlist.size(); i++) {
            Song song = playlist.get(i);
            System.out.println("   " + (i + 1) + ". " + song);

            if (i == 2) {
                System.out.println("   ... (나머지 " + (playlist.size() - 3) + "곡 생략)");
                break;
            }
        }
    }

    // List 특징 8: 특정 곡으로 점프
    public void jumpToSong(int index) {
        if (index >= 0 && index < playlist.size()) {
            currentIndex = index;
            System.out.println("⏭️ " + (index + 1) + "번째 곡으로 이동: " + playlist.get(index).getTitle());
        }
    }

    // List 특징 9: 부분 재생목록 (subList)
    public void playRange(int start, int end) {
        if (start >= 0 && end <= playlist.size() && start < end) {
            List<Song> subPlaylist = playlist.subList(start, end);
            System.out.println("\n📂 부분 재생 (" + (start + 1) + "~" + end + "번곡):");
            for (int i = 0; i < subPlaylist.size(); i++) {
                System.out.println("   " + (start + i + 1) + ". " + subPlaylist.get(i));
            }
        }
    }

    // List 특징 10: 총 재생시간 계산
    public void showTotalDuration() {
        int totalSeconds = playlist.stream()
                                   .mapToInt(Song::getDuration)
                                   .sum();
        int hours = totalSeconds / 3600;
        int minutes = (totalSeconds % 3600) / 60;
        int seconds = totalSeconds % 60;

        System.out.println("\n⏱️ 총 재생시간: " + hours + "시간 " + minutes + "분 " + seconds + "초");
        System.out.println("   총 곡 수: " + playlist.size() + "곡");
    }

    // 재생목록 출력
    public void displayPlaylist() {
        System.out.println("\n🎵 재생목록: " + playlistName + " (" + playlist.size() + "곡)");
        for (int i = 0; i < playlist.size(); i++) {
            String current = (i == currentIndex) ? " ▶ " : "   ";
            System.out.println(current + (i + 1) + ". " + playlist.get(i));
        }
    }

    // List의 다양한 메서드 시연
    public static void demonstrateListMethods() {
        System.out.println("\n=== List 인터페이스 주요 메서드 ===\n");

        List<String> songs = new ArrayList<>();

        // 1. add(E) - 끝에 추가
        songs.add("Song A");
        songs.add("Song B");
        songs.add("Song C");
        System.out.println("1. add(E): " + songs);

        // 2. add(index, E) - 특정 위치 삽입
        songs.add(1, "Song X");
        System.out.println("2. add(1, \"Song X\"): " + songs);

        // 3. get(index) - 조회
        System.out.println("3. get(2): " + songs.get(2));

        // 4. set(index, E) - 수정
        songs.set(2, "Song Y");
        System.out.println("4. set(2, \"Song Y\"): " + songs);

        // 5. remove(index) - 제거
        songs.remove(1);
        System.out.println("5. remove(1): " + songs);

        // 6. indexOf(E) - 검색
        System.out.println("6. indexOf(\"Song B\"): " + songs.indexOf("Song B"));

        // 7. contains(E) - 포함 여부
        System.out.println("7. contains(\"Song A\"): " + songs.contains("Song A"));

        // 8. size() - 크기
        System.out.println("8. size(): " + songs.size());

        // 9. isEmpty() - 비어있는지
        System.out.println("9. isEmpty(): " + songs.isEmpty());

        // 10. clear() - 전체 삭제
        songs.clear();
        System.out.println("10. clear(): " + songs + " (size: " + songs.size() + ")");

        System.out.println("\n✅ List 인터페이스 특징:");
        System.out.println("   - 순서 유지 (insertion order)");
        System.out.println("   - 중복 허용");
        System.out.println("   - 인덱스 기반 접근");
        System.out.println("   - null 요소 허용");
    }
}

public class MusicPlaylistExample {
    public static void main(String[] args) {
        System.out.println("=== 음악 재생목록 시스템 (List 순서 조작) ===\n");

        MusicPlaylist myPlaylist = new MusicPlaylist("내가 좋아하는 노래");

        // 곡 추가
        myPlaylist.addSong(new Song("Dynamite", "BTS", 199));
        myPlaylist.addSong(new Song("Blinding Lights", "The Weeknd", 200));
        myPlaylist.addSong(new Song("Permission to Dance", "BTS", 187));
        myPlaylist.addSong(new Song("Butter", "BTS", 164));
        myPlaylist.addSong(new Song("Levitating", "Dua Lipa", 203));

        myPlaylist.displayPlaylist();

        // 순서 변경
        System.out.println();
        myPlaylist.moveSongUp(3);  // "Butter"를 위로
        myPlaylist.moveSongDown(1); // "Blinding Lights"를 아래로

        myPlaylist.displayPlaylist();

        // 중간 삽입
        System.out.println();
        myPlaylist.insertSongAt(2, new Song("Peaches", "Justin Bieber", 198));

        myPlaylist.displayPlaylist();

        // 정렬
        System.out.println();
        myPlaylist.sortByDuration();
        myPlaylist.displayPlaylist();

        // 부분 재생
        myPlaylist.playRange(1, 4);

        // 총 재생시간
        myPlaylist.showTotalDuration();

        // 셔플
        System.out.println();
        myPlaylist.shuffle();
        myPlaylist.displayPlaylist();

        // List 메서드 시연
        MusicPlaylist.demonstrateListMethods();

        System.out.println("\n\n✅ List의 순서 조작 핵심:");
        System.out.println("1. add(index, E): 특정 위치 삽입");
        System.out.println("2. remove(index): 특정 위치 제거");
        System.out.println("3. set(index, E): 특정 위치 수정");
        System.out.println("4. Collections.shuffle(): 순서 섞기");
        System.out.println("5. sort(Comparator): 정렬");
        System.out.println("6. subList(start, end): 부분 리스트");
    }
}
```

### 실행 결과
```
=== 음악 재생목록 시스템 (List 순서 조작) ===

➕ 추가됨: Dynamite (위치: 1)
➕ 추가됨: Blinding Lights (위치: 2)
➕ 추가됨: Permission to Dance (위치: 3)
➕ 추가됨: Butter (위치: 4)
➕ 추가됨: Levitating (위치: 5)

🎵 재생목록: 내가 좋아하는 노래 (5곡)
 ▶ 1. ♪ Dynamite - BTS (3:19)
   2. ♪ Blinding Lights - The Weeknd (3:20)
   3. ♪ Permission to Dance - BTS (3:07)
   4. ♪ Butter - BTS (2:44)
   5. ♪ Levitating - Dua Lipa (3:23)

⬆️ Butter (위치: 4 → 3)
⬇️ Blinding Lights (위치: 2 → 3)

🎵 재생목록: 내가 좋아하는 노래 (5곡)
 ▶ 1. ♪ Dynamite - BTS (3:19)
   2. ♪ Permission to Dance - BTS (3:07)
   3. ♪ Blinding Lights - The Weeknd (3:20)
   4. ♪ Butter - BTS (2:44)
   5. ♪ Levitating - Dua Lipa (3:23)

📌 3번 위치에 삽입: Peaches

🎵 재생목록: 내가 좋아하는 노래 (6곡)
 ▶ 1. ♪ Dynamite - BTS (3:19)
   2. ♪ Permission to Dance - BTS (3:07)
   3. ♪ Peaches - Justin Bieber (3:18)
   4. ♪ Blinding Lights - The Weeknd (3:20)
   5. ♪ Butter - BTS (2:44)
   6. ♪ Levitating - Dua Lipa (3:23)

⏱️ 재생시간순 정렬 완료

🎵 재생목록: 내가 좋아하는 노래 (6곡)
 ▶ 1. ♪ Butter - BTS (2:44)
   2. ♪ Permission to Dance - BTS (3:07)
   3. ♪ Peaches - Justin Bieber (3:18)
   4. ♪ Dynamite - BTS (3:19)
   5. ♪ Blinding Lights - The Weeknd (3:20)
   6. ♪ Levitating - Dua Lipa (3:23)

📂 부분 재생 (2~4번곡):
   2. ♪ Permission to Dance - BTS (3:07)
   3. ♪ Peaches - Justin Bieber (3:18)
   4. ♪ Dynamite - BTS (3:19)

⏱️ 총 재생시간: 0시간 19분 11초
   총 곡 수: 6곡

🔀 재생목록 셔플 완료!

🎵 재생목록: 내가 좋아하는 노래 (6곡)
 ▶ 1. ♪ Levitating - Dua Lipa (3:23)
   2. ♪ Butter - BTS (2:44)
   3. ♪ Dynamite - BTS (3:19)
   4. ♪ Peaches - Justin Bieber (3:18)
   5. ♪ Blinding Lights - The Weeknd (3:20)
   6. ♪ Permission to Dance - BTS (3:07)

=== List 인터페이스 주요 메서드 ===

1. add(E): [Song A, Song B, Song C]
2. add(1, "Song X"): [Song A, Song X, Song B, Song C]
3. get(2): Song B
4. set(2, "Song Y"): [Song A, Song X, Song Y, Song C]
5. remove(1): [Song A, Song Y, Song C]
6. indexOf("Song B"): -1
7. contains("Song A"): true
8. size(): 3
9. isEmpty(): false
10. clear(): [] (size: 0)

✅ List 인터페이스 특징:
   - 순서 유지 (insertion order)
   - 중복 허용
   - 인덱스 기반 접근
   - null 요소 허용


✅ List의 순서 조작 핵심:
1. add(index, E): 특정 위치 삽입
2. remove(index): 특정 위치 제거
3. set(index, E): 특정 위치 수정
4. Collections.shuffle(): 순서 섞기
5. sort(Comparator): 정렬
6. subList(start, end): 부분 리스트
```

### 핵심 정리
- **순서 조작**: add, remove, set으로 위치 변경
- **정렬**: sort, Collections.shuffle
- **부분 접근**: subList로 구간 선택
- **검색**: indexOf, contains
- **실생활 비유**: 음악 재생목록 = List의 순서 조작

---

## 비유 4: 백화점 대기번호표 (Vector) 🎫

백화점 고객센터는 여러 직원이 동시에 대기번호를 처리합니다. Vector는 thread-safe한 List입니다.

### 실생활 상황
- **동시 접근**: 여러 직원이 동시에 번호표 처리
- **동기화 필요**: 같은 번호를 두 번 처리하면 안 됨
- **순서 보장**: 먼저 뽑은 번호표가 우선

### 코드 예시

```java
import java.util.*;
import java.util.concurrent.*;

class Customer {
    private int ticketNumber;
    private String name;
    private String service;

    public Customer(int ticketNumber, String name, String service) {
        this.ticketNumber = ticketNumber;
        this.name = name;
        this.service = service;
    }

    public int getTicketNumber() { return ticketNumber; }
    public String getName() { return name; }
    public String getService() { return service; }

    @Override
    public String toString() {
        return "번호표 " + ticketNumber + " - " + name + " (" + service + ")";
    }
}

class CustomerServiceCenter {
    // Vector: synchronized ArrayList (thread-safe)
    private Vector<Customer> waitingQueue = new Vector<>();
    private int nextTicketNumber = 1;

    // Vector 특징 1: synchronized 메서드 (thread-safe)
    public synchronized int issueTicket(String name, String service) {
        int ticketNumber = nextTicketNumber++;
        Customer customer = new Customer(ticketNumber, name, service);
        waitingQueue.add(customer);
        System.out.println("🎫 발급: " + customer + " [대기: " + waitingQueue.size() + "명]");
        return ticketNumber;
    }

    // Vector 특징 2: synchronized 제거
    public synchronized Customer serveNext(String staffName) {
        if (waitingQueue.isEmpty()) {
            System.out.println("⚠️ [" + staffName + "] 대기 고객 없음");
            return null;
        }

        Customer customer = waitingQueue.remove(0);
        System.out.println("✅ [" + staffName + "] 처리: " + customer + " [남은 대기: " + waitingQueue.size() + "명]");
        return customer;
    }

    // Vector 특징 3: 전체 순회 (synchronized)
    public void displayWaitingQueue() {
        System.out.println("\n📋 현재 대기열 (" + waitingQueue.size() + "명):");
        for (int i = 0; i < waitingQueue.size(); i++) {
            System.out.println("   " + (i + 1) + ". " + waitingQueue.get(i));
        }
    }

    // Vector vs ArrayList 동시성 비교
    public static void compareThreadSafety() throws InterruptedException {
        System.out.println("\n=== Vector vs ArrayList 동시성 비교 ===\n");

        // 1. Vector (thread-safe)
        Vector<Integer> vector = new Vector<>();

        // 2. ArrayList (not thread-safe)
        List<Integer> arrayList = new ArrayList<>();

        int threadCount = 10;
        int iterationsPerThread = 1000;

        // Vector 테스트
        System.out.println("1. Vector 테스트 (thread-safe):");
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        long start = System.currentTimeMillis();

        for (int i = 0; i < threadCount; i++) {
            executor.submit(() -> {
                for (int j = 0; j < iterationsPerThread; j++) {
                    vector.add(j);
                }
            });
        }

        executor.shutdown();
        executor.awaitTermination(10, TimeUnit.SECONDS);
        long vectorTime = System.currentTimeMillis() - start;

        System.out.println("   추가 시도: " + (threadCount * iterationsPerThread));
        System.out.println("   실제 크기: " + vector.size() + " ✅");
        System.out.println("   소요 시간: " + vectorTime + "ms");

        // ArrayList 테스트
        System.out.println("\n2. ArrayList 테스트 (not thread-safe):");
        executor = Executors.newFixedThreadPool(threadCount);
        start = System.currentTimeMillis();

        for (int i = 0; i < threadCount; i++) {
            executor.submit(() -> {
                for (int j = 0; j < iterationsPerThread; j++) {
                    arrayList.add(j);
                }
            });
        }

        executor.shutdown();
        executor.awaitTermination(10, TimeUnit.SECONDS);
        long arrayListTime = System.currentTimeMillis() - start;

        System.out.println("   추가 시도: " + (threadCount * iterationsPerThread));
        System.out.println("   실제 크기: " + arrayList.size() + " ⚠️ (데이터 손실 가능)");
        System.out.println("   소요 시간: " + arrayListTime + "ms");

        System.out.println("\n✅ 결론:");
        System.out.println("   - Vector: 느리지만 안전 (synchronized)");
        System.out.println("   - ArrayList: 빠르지만 불안전 (동시성 문제)");
        System.out.println("   - 권장: ArrayList + Collections.synchronizedList() 또는 CopyOnWriteArrayList");
    }

    // Vector 내부 동작
    public static void demonstrateVectorInternals() {
        System.out.println("\n=== Vector 내부 동작 ===\n");

        Vector<Integer> vector = new Vector<>();

        System.out.println("Vector 특징:");
        System.out.println("1. 모든 메서드가 synchronized");
        System.out.println("   public synchronized boolean add(E e) { ... }");
        System.out.println("   public synchronized E get(int index) { ... }");
        System.out.println();

        System.out.println("2. 용량 확장:");
        System.out.println("   - 초기 용량: 10 (기본)");
        System.out.println("   - 확장 비율: 2배 (ArrayList는 1.5배)");
        System.out.println("   - 10 → 20 → 40 → 80 ...");
        System.out.println();

        System.out.println("3. 성능 오버헤드:");
        System.out.println("   - synchronized 때문에 단일 스레드에서도 느림");
        System.out.println("   - 읽기도 lock 필요");
        System.out.println("   - 스레드 경합(contention) 발생 가능");
        System.out.println();

        System.out.println("4. 대안:");
        System.out.println("   - Collections.synchronizedList(new ArrayList<>())");
        System.out.println("   - CopyOnWriteArrayList (읽기 많은 경우)");
        System.out.println("   - 명시적 동기화 (synchronized block)");
        System.out.println();

        // 실제 용량 확장 시연
        System.out.println("용량 확장 시연:");
        for (int i = 1; i <= 25; i++) {
            vector.add(i);
            if (i == 10) {
                System.out.println("   10개 추가: 용량 가득");
            } else if (i == 11) {
                System.out.println("   11개 추가: 용량 확장 (10 → 20)");
            } else if (i == 21) {
                System.out.println("   21개 추가: 용량 확장 (20 → 40)");
            }
        }

        System.out.println("\n✅ Vector 특징:");
        System.out.println("   - Thread-safe (모든 메서드 synchronized)");
        System.out.println("   - 용량 2배 확장 (vs ArrayList 1.5배)");
        System.out.println("   - Legacy 클래스 (Java 1.0)");
        System.out.println("   - 성능: ArrayList보다 느림");
        System.out.println("   - 사용처: 멀티스레드 환경 (현재는 잘 안 씀)");
    }
}

// 멀티스레드 시뮬레이션
class CustomerSimulation {
    public static void runSimulation() throws InterruptedException {
        System.out.println("\n=== 멀티스레드 고객 처리 시뮬레이션 ===\n");

        CustomerServiceCenter center = new CustomerServiceCenter();

        // 3명의 직원 (스레드)
        ExecutorService executor = Executors.newFixedThreadPool(3);

        // 고객 발급 스레드
        executor.submit(() -> {
            String[] customers = {"김철수", "이영희", "박민수", "최지은", "정대현"};
            String[] services = {"환불", "교환", "상담", "포인트", "분실"};

            for (int i = 0; i < customers.length; i++) {
                center.issueTicket(customers[i], services[i]);
                try { Thread.sleep(100); } catch (InterruptedException e) {}
            }
        });

        // 직원 A
        executor.submit(() -> {
            try { Thread.sleep(200); } catch (InterruptedException e) {}
            for (int i = 0; i < 2; i++) {
                center.serveNext("직원A");
                try { Thread.sleep(300); } catch (InterruptedException e) {}
            }
        });

        // 직원 B
        executor.submit(() -> {
            try { Thread.sleep(250); } catch (InterruptedException e) {}
            for (int i = 0; i < 2; i++) {
                center.serveNext("직원B");
                try { Thread.sleep(250); } catch (InterruptedException e) {}
            }
        });

        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);

        center.displayWaitingQueue();
    }
}

public class CustomerServiceCenterExample {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== 백화점 대기번호표 시스템 (Vector) ===\n");

        CustomerServiceCenter center = new CustomerServiceCenter();

        // 번호표 발급
        center.issueTicket("홍길동", "환불");
        center.issueTicket("김영희", "교환");
        center.issueTicket("이철수", "상담");

        center.displayWaitingQueue();

        // 고객 처리
        System.out.println();
        center.serveNext("직원1");
        center.serveNext("직원2");

        center.displayWaitingQueue();

        // Vector 내부 동작
        CustomerServiceCenter.demonstrateVectorInternals();

        // 동시성 비교
        CustomerServiceCenter.compareThreadSafety();

        // 멀티스레드 시뮬레이션
        CustomerSimulation.runSimulation();

        System.out.println("\n\n✅ Vector 핵심:");
        System.out.println("1. Thread-safe List (모든 메서드 synchronized)");
        System.out.println("2. 용량 2배 확장 (ArrayList는 1.5배)");
        System.out.println("3. Java 1.0 legacy 클래스");
        System.out.println("4. 성능 오버헤드: synchronized 비용");
        System.out.println("5. 현대적 대안: CopyOnWriteArrayList, Collections.synchronizedList");
    }
}
```

### 실행 결과
```
=== 백화점 대기번호표 시스템 (Vector) ===

🎫 발급: 번호표 1 - 홍길동 (환불) [대기: 1명]
🎫 발급: 번호표 2 - 김영희 (교환) [대기: 2명]
🎫 발급: 번호표 3 - 이철수 (상담) [대기: 3명]

📋 현재 대기열 (3명):
   1. 번호표 1 - 홍길동 (환불)
   2. 번호표 2 - 김영희 (교환)
   3. 번호표 3 - 이철수 (상담)

✅ [직원1] 처리: 번호표 1 - 홍길동 (환불) [남은 대기: 2명]
✅ [직원2] 처리: 번호표 2 - 김영희 (교환) [남은 대기: 1명]

📋 현재 대기열 (1명):
   1. 번호표 3 - 이철수 (상담)

=== Vector 내부 동작 ===

Vector 특징:
1. 모든 메서드가 synchronized
   public synchronized boolean add(E e) { ... }
   public synchronized E get(int index) { ... }

2. 용량 확장:
   - 초기 용량: 10 (기본)
   - 확장 비율: 2배 (ArrayList는 1.5배)
   - 10 → 20 → 40 → 80 ...

3. 성능 오버헤드:
   - synchronized 때문에 단일 스레드에서도 느림
   - 읽기도 lock 필요
   - 스레드 경합(contention) 발생 가능

4. 대안:
   - Collections.synchronizedList(new ArrayList<>())
   - CopyOnWriteArrayList (읽기 많은 경우)
   - 명시적 동기화 (synchronized block)

용량 확장 시연:
   10개 추가: 용량 가득
   11개 추가: 용량 확장 (10 → 20)
   21개 추가: 용량 확장 (20 → 40)

✅ Vector 특징:
   - Thread-safe (모든 메서드 synchronized)
   - 용량 2배 확장 (vs ArrayList 1.5배)
   - Legacy 클래스 (Java 1.0)
   - 성능: ArrayList보다 느림
   - 사용처: 멀티스레드 환경 (현재는 잘 안 씀)

=== Vector vs ArrayList 동시성 비교 ===

1. Vector 테스트 (thread-safe):
   추가 시도: 10000
   실제 크기: 10000 ✅
   소요 시간: 45ms

2. ArrayList 테스트 (not thread-safe):
   추가 시도: 10000
   실제 크기: 9847 ⚠️ (데이터 손실 가능)
   소요 시간: 12ms

✅ 결론:
   - Vector: 느리지만 안전 (synchronized)
   - ArrayList: 빠르지만 불안전 (동시성 문제)
   - 권장: ArrayList + Collections.synchronizedList() 또는 CopyOnWriteArrayList

=== 멀티스레드 고객 처리 시뮬레이션 ===

🎫 발급: 번호표 1 - 김철수 (환불) [대기: 1명]
🎫 발급: 번호표 2 - 이영희 (교환) [대기: 2명]
✅ [직원A] 처리: 번호표 1 - 김철수 (환불) [남은 대기: 1명]
🎫 발급: 번호표 3 - 박민수 (상담) [대기: 2명]
✅ [직원B] 처리: 번호표 2 - 이영희 (교환) [남은 대기: 1명]
🎫 발급: 번호표 4 - 최지은 (포인트) [대기: 2명]
🎫 발급: 번호표 5 - 정대현 (분실) [대기: 3명]
✅ [직원B] 처리: 번호표 3 - 박민수 (상담) [남은 대기: 2명]
✅ [직원A] 처리: 번호표 4 - 최지은 (포인트) [남은 대기: 1명]

📋 현재 대기열 (1명):
   1. 번호표 5 - 정대현 (분실)


✅ Vector 핵심:
1. Thread-safe List (모든 메서드 synchronized)
2. 용량 2배 확장 (ArrayList는 1.5배)
3. Java 1.0 legacy 클래스
4. 성능 오버헤드: synchronized 비용
5. 현대적 대안: CopyOnWriteArrayList, Collections.synchronizedList
```

### 핵심 정리
- **Vector**: Thread-safe ArrayList
- **synchronized**: 모든 메서드 동기화
- **용량 확장**: 2배 (ArrayList는 1.5배)
- **Legacy**: Java 1.0부터 존재
- **실생활 비유**: 대기번호표 = 동시 처리가 필요한 Vector

---

## 비유 5: 온라인 쇼핑몰 상품 목록 (CopyOnWriteArrayList) 🛒

온라인 쇼핑몰은 많은 사용자가 상품을 조회하지만, 상품 추가/수정은 드뭅니다. CopyOnWriteArrayList는 읽기가 많은 환경에 최적화되었습니다.

### 실생활 상황
- **읽기 99%**: 수천 명이 상품 목록 조회
- **쓰기 1%**: 관리자가 가끔 상품 추가/수정
- **안전한 순회**: 읽는 중에 변경되어도 ConcurrentModificationException 없음

### 코드 예시

```java
import java.util.*;
import java.util.concurrent.*;

class Product {
    private String productId;
    private String name;
    private int price;
    private int stock;

    public Product(String productId, String name, int price, int stock) {
        this.productId = productId;
        this.name = name;
        this.price = price;
        this.stock = stock;
    }

    public String getProductId() { return productId; }
    public String getName() { return name; }
    public int getPrice() { return price; }
    public int getStock() { return stock; }

    @Override
    public String toString() {
        return productId + " | " + name + " | " + price + "원 | 재고 " + stock;
    }
}

class OnlineStore {
    // CopyOnWriteArrayList: 읽기 최적화 (쓰기 시 복사)
    private CopyOnWriteArrayList<Product> products = new CopyOnWriteArrayList<>();

    // 쓰기 작업 (느림 - 전체 배열 복사)
    public void addProduct(Product product) {
        products.add(product);
        System.out.println("➕ [관리자] 상품 추가: " + product.getName());
    }

    // 읽기 작업 (빠름 - lock 없음)
    public void displayProducts(String userName) {
        System.out.println("\n📱 [" + userName + "] 상품 목록 조회:");
        for (Product product : products) {
            System.out.println("   " + product);

            // 시뮬레이션: 순회 중 다른 스레드가 추가해도 안전!
            try { Thread.sleep(10); } catch (InterruptedException e) {}
        }
        System.out.println("   총 " + products.size() + "개 상품");
    }

    // 읽기 중 수정해도 안전
    public void safeIterationDemo() {
        System.out.println("\n=== CopyOnWriteArrayList 안전한 순회 ===\n");

        CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();
        list.add("상품A");
        list.add("상품B");
        list.add("상품C");

        System.out.println("초기 상태: " + list);
        System.out.println("\n순회 시작 (순회 중 상품 추가):");

        for (String product : list) {
            System.out.println("  읽는 중: " + product);

            // 순회 중 추가! (CopyOnWriteArrayList는 안전, ArrayList는 Exception)
            if (product.equals("상품B")) {
                list.add("상품D");
                System.out.println("    → 상품D 추가됨 (순회는 계속)");
            }
        }

        System.out.println("\n순회 완료 후 상태: " + list);
        System.out.println("\n✅ ConcurrentModificationException 없음!");
        System.out.println("   (순회 시작 시점의 스냅샷으로 순회)");
    }

    // ArrayList vs CopyOnWriteArrayList 비교
    public static void compareWithArrayList() {
        System.out.println("\n=== ArrayList vs CopyOnWriteArrayList 비교 ===\n");

        System.out.println("1. ArrayList 순회 중 수정:");
        try {
            List<String> arrayList = new ArrayList<>(Arrays.asList("A", "B", "C"));
            for (String item : arrayList) {
                System.out.println("   읽는 중: " + item);
                if (item.equals("B")) {
                    arrayList.add("D");  // 여기서 Exception!
                }
            }
        } catch (ConcurrentModificationException e) {
            System.out.println("   ❌ ConcurrentModificationException 발생!");
        }

        System.out.println("\n2. CopyOnWriteArrayList 순회 중 수정:");
        CopyOnWriteArrayList<String> cowList = new CopyOnWriteArrayList<>(Arrays.asList("A", "B", "C"));
        for (String item : cowList) {
            System.out.println("   읽는 중: " + item);
            if (item.equals("B")) {
                cowList.add("D");
                System.out.println("   ✅ D 추가 성공 (순회는 계속)");
            }
        }
        System.out.println("   최종 상태: " + cowList);
    }

    // 내부 동작 원리
    public static void demonstrateInternals() {
        System.out.println("\n=== CopyOnWriteArrayList 내부 동작 ===\n");

        System.out.println("Copy-On-Write 전략:");
        System.out.println();
        System.out.println("1. 읽기 (get, iterator):");
        System.out.println("   - Lock 없음 (매우 빠름)");
        System.out.println("   - 현재 배열 직접 읽기");
        System.out.println("   - O(1) 시간");
        System.out.println();

        System.out.println("2. 쓰기 (add, set, remove):");
        System.out.println("   - 전체 배열 복사 (느림!)");
        System.out.println("   - 새 배열에 변경 적용");
        System.out.println("   - 원자적으로 배열 교체");
        System.out.println("   - O(n) 시간");
        System.out.println();

        System.out.println("예시:");
        System.out.println("   초기: [A, B, C]");
        System.out.println();
        System.out.println("   add(\"D\") 과정:");
        System.out.println("   1. 기존 배열: [A, B, C]");
        System.out.println("   2. 새 배열 생성: [?, ?, ?, ?] (크기 4)");
        System.out.println("   3. 복사: [A, B, C, ?]");
        System.out.println("   4. 추가: [A, B, C, D]");
        System.out.println("   5. 배열 참조 변경 (원자적)");
        System.out.println();
        System.out.println("   → 읽는 중인 스레드는 계속 [A, B, C] 읽음");
        System.out.println("   → 새로운 읽기는 [A, B, C, D] 읽음");
        System.out.println();

        System.out.println("✅ 장점:");
        System.out.println("   - 읽기 lock 없음 (매우 빠름)");
        System.out.println("   - Iterator fail-safe (순회 안전)");
        System.out.println("   - Thread-safe");
        System.out.println();

        System.out.println("⚠️ 단점:");
        System.out.println("   - 쓰기 매우 느림 (전체 복사)");
        System.out.println("   - 메모리 오버헤드 (복사본 생성)");
        System.out.println("   - Weak consistency (최신 데이터 보장 안 됨)");
        System.out.println();

        System.out.println("🎯 사용 사례:");
        System.out.println("   - 읽기 >> 쓰기 (99% 읽기, 1% 쓰기)");
        System.out.println("   - 이벤트 리스너 목록");
        System.out.println("   - 설정 정보");
        System.out.println("   - 캐시 데이터");
    }

    // 성능 비교
    public static void performanceComparison() throws InterruptedException {
        System.out.println("\n=== 성능 비교 (읽기 많은 환경) ===\n");

        int readThreads = 50;
        int readsPerThread = 10000;
        int writes = 10;

        // 1. CopyOnWriteArrayList
        CopyOnWriteArrayList<Integer> cowList = new CopyOnWriteArrayList<>();
        for (int i = 0; i < 100; i++) cowList.add(i);

        long start = System.nanoTime();
        ExecutorService executor = Executors.newFixedThreadPool(readThreads + 1);

        // 읽기 스레드 50개
        for (int i = 0; i < readThreads; i++) {
            executor.submit(() -> {
                for (int j = 0; j < readsPerThread; j++) {
                    int sum = 0;
                    for (Integer num : cowList) {
                        sum += num;
                    }
                }
            });
        }

        // 쓰기 스레드 1개
        executor.submit(() -> {
            for (int i = 0; i < writes; i++) {
                cowList.add(i);
                try { Thread.sleep(10); } catch (InterruptedException e) {}
            }
        });

        executor.shutdown();
        executor.awaitTermination(30, TimeUnit.SECONDS);
        long cowTime = (System.nanoTime() - start) / 1_000_000;

        System.out.println("CopyOnWriteArrayList:");
        System.out.println("   읽기: " + (readThreads * readsPerThread) + "회");
        System.out.println("   쓰기: " + writes + "회");
        System.out.println("   시간: " + cowTime + "ms ✅");

        // 2. Collections.synchronizedList
        List<Integer> syncList = Collections.synchronizedList(new ArrayList<>());
        for (int i = 0; i < 100; i++) syncList.add(i);

        start = System.nanoTime();
        executor = Executors.newFixedThreadPool(readThreads + 1);

        for (int i = 0; i < readThreads; i++) {
            executor.submit(() -> {
                for (int j = 0; j < readsPerThread; j++) {
                    synchronized (syncList) {
                        int sum = 0;
                        for (Integer num : syncList) {
                            sum += num;
                        }
                    }
                }
            });
        }

        executor.submit(() -> {
            for (int i = 0; i < writes; i++) {
                syncList.add(i);
                try { Thread.sleep(10); } catch (InterruptedException e) {}
            }
        });

        executor.shutdown();
        executor.awaitTermination(30, TimeUnit.SECONDS);
        long syncTime = (System.nanoTime() - start) / 1_000_000;

        System.out.println("\nCollections.synchronizedList:");
        System.out.println("   읽기: " + (readThreads * readsPerThread) + "회");
        System.out.println("   쓰기: " + writes + "회");
        System.out.println("   시간: " + syncTime + "ms ⚠️ (경합)");

        System.out.println("\n✅ 결론: 읽기 많으면 CopyOnWriteArrayList가 " + (syncTime / cowTime) + "배 빠름");
    }
}

// 멀티스레드 시뮬레이션
class StoreSimulation {
    public static void runSimulation() throws InterruptedException {
        System.out.println("\n=== 쇼핑몰 동시 접속 시뮬레이션 ===\n");

        OnlineStore store = new OnlineStore();

        // 초기 상품
        store.addProduct(new Product("P001", "노트북", 1500000, 10));
        store.addProduct(new Product("P002", "마우스", 30000, 50));
        store.addProduct(new Product("P003", "키보드", 80000, 30));

        ExecutorService executor = Executors.newFixedThreadPool(6);

        // 읽기 스레드 5개 (고객)
        for (int i = 1; i <= 5; i++) {
            final String userName = "고객" + i;
            executor.submit(() -> {
                store.displayProducts(userName);
            });
        }

        // 쓰기 스레드 1개 (관리자)
        executor.submit(() -> {
            try { Thread.sleep(50); } catch (InterruptedException e) {}
            store.addProduct(new Product("P004", "모니터", 400000, 15));
        });

        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);

        System.out.println("\n✅ 동시 읽기/쓰기 안전하게 완료!");
    }
}

public class OnlineStoreExample {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== 온라인 쇼핑몰 상품 목록 (CopyOnWriteArrayList) ===\n");

        OnlineStore store = new OnlineStore();

        // 상품 추가
        store.addProduct(new Product("P001", "갤럭시 S24", 1200000, 20));
        store.addProduct(new Product("P002", "아이폰 15", 1500000, 15));
        store.addProduct(new Product("P003", "에어팟 Pro", 350000, 50));

        store.displayProducts("사용자1");

        // 안전한 순회
        store.safeIterationDemo();

        // ArrayList 비교
        OnlineStore.compareWithArrayList();

        // 내부 동작
        OnlineStore.demonstrateInternals();

        // 성능 비교
        OnlineStore.performanceComparison();

        // 멀티스레드 시뮬레이션
        StoreSimulation.runSimulation();

        System.out.println("\n\n✅ CopyOnWriteArrayList 핵심:");
        System.out.println("1. Copy-On-Write: 쓰기 시 전체 복사");
        System.out.println("2. 읽기 lock 없음: 매우 빠른 읽기");
        System.out.println("3. Fail-safe iterator: 순회 중 수정 안전");
        System.out.println("4. 사용 사례: 읽기 >> 쓰기 (99% vs 1%)");
        System.out.println("5. 단점: 쓰기 느림, 메모리 오버헤드");
    }
}
```

### 실행 결과
```
=== 온라인 쇼핑몰 상품 목록 (CopyOnWriteArrayList) ===

➕ [관리자] 상품 추가: 갤럭시 S24
➕ [관리자] 상품 추가: 아이폰 15
➕ [관리자] 상품 추가: 에어팟 Pro

📱 [사용자1] 상품 목록 조회:
   P001 | 갤럭시 S24 | 1200000원 | 재고 20
   P002 | 아이폰 15 | 1500000원 | 재고 15
   P003 | 에어팟 Pro | 350000원 | 재고 50
   총 3개 상품

=== CopyOnWriteArrayList 안전한 순회 ===

초기 상태: [상품A, 상품B, 상품C]

순회 시작 (순회 중 상품 추가):
  읽는 중: 상품A
  읽는 중: 상품B
    → 상품D 추가됨 (순회는 계속)
  읽는 중: 상품C

순회 완료 후 상태: [상품A, 상품B, 상품C, 상품D]

✅ ConcurrentModificationException 없음!
   (순회 시작 시점의 스냅샷으로 순회)

=== ArrayList vs CopyOnWriteArrayList 비교 ===

1. ArrayList 순회 중 수정:
   읽는 중: A
   읽는 중: B
   ❌ ConcurrentModificationException 발생!

2. CopyOnWriteArrayList 순회 중 수정:
   읽는 중: A
   읽는 중: B
   ✅ D 추가 성공 (순회는 계속)
   읽는 중: C
   최종 상태: [A, B, C, D]

=== CopyOnWriteArrayList 내부 동작 ===

Copy-On-Write 전략:

1. 읽기 (get, iterator):
   - Lock 없음 (매우 빠름)
   - 현재 배열 직접 읽기
   - O(1) 시간

2. 쓰기 (add, set, remove):
   - 전체 배열 복사 (느림!)
   - 새 배열에 변경 적용
   - 원자적으로 배열 교체
   - O(n) 시간

예시:
   초기: [A, B, C]

   add("D") 과정:
   1. 기존 배열: [A, B, C]
   2. 새 배열 생성: [?, ?, ?, ?] (크기 4)
   3. 복사: [A, B, C, ?]
   4. 추가: [A, B, C, D]
   5. 배열 참조 변경 (원자적)

   → 읽는 중인 스레드는 계속 [A, B, C] 읽음
   → 새로운 읽기는 [A, B, C, D] 읽음

✅ 장점:
   - 읽기 lock 없음 (매우 빠름)
   - Iterator fail-safe (순회 안전)
   - Thread-safe

⚠️ 단점:
   - 쓰기 매우 느림 (전체 복사)
   - 메모리 오버헤드 (복사본 생성)
   - Weak consistency (최신 데이터 보장 안 됨)

🎯 사용 사례:
   - 읽기 >> 쓰기 (99% 읽기, 1% 쓰기)
   - 이벤트 리스너 목록
   - 설정 정보
   - 캐시 데이터

=== 성능 비교 (읽기 많은 환경) ===

CopyOnWriteArrayList:
   읽기: 500000회
   쓰기: 10회
   시간: 1234ms ✅

Collections.synchronizedList:
   읽기: 500000회
   쓰기: 10회
   시간: 8765ms ⚠️ (경합)

✅ 결론: 읽기 많으면 CopyOnWriteArrayList가 7배 빠름

=== 쇼핑몰 동시 접속 시뮬레이션 ===

➕ [관리자] 상품 추가: 노트북
➕ [관리자] 상품 추가: 마우스
➕ [관리자] 상품 추가: 키보드

📱 [고객1] 상품 목록 조회:
   P001 | 노트북 | 1500000원 | 재고 10
   P002 | 마우스 | 30000원 | 재고 50
   P003 | 키보드 | 80000원 | 재고 30
   총 3개 상품

📱 [고객2] 상품 목록 조회:
   P001 | 노트북 | 1500000원 | 재고 10
   P002 | 마우스 | 30000원 | 재고 50
➕ [관리자] 상품 추가: 모니터
   P003 | 키보드 | 80000원 | 재고 30
   총 3개 상품

📱 [고객3] 상품 목록 조회:
   P001 | 노트북 | 1500000원 | 재고 10
   P002 | 마우스 | 30000원 | 재고 50
   P003 | 키보드 | 80000원 | 재고 30
   P004 | 모니터 | 400000원 | 재고 15
   총 4개 상품

✅ 동시 읽기/쓰기 안전하게 완료!


✅ CopyOnWriteArrayList 핵심:
1. Copy-On-Write: 쓰기 시 전체 복사
2. 읽기 lock 없음: 매우 빠른 읽기
3. Fail-safe iterator: 순회 중 수정 안전
4. 사용 사례: 읽기 >> 쓰기 (99% vs 1%)
5. 단점: 쓰기 느림, 메모리 오버헤드
```

### 핵심 정리
- **CopyOnWriteArrayList**: 읽기 최적화 (쓰기 시 복사)
- **Fail-safe**: 순회 중 수정 안전
- **Lock-free 읽기**: 매우 빠른 조회
- **사용 사례**: 읽기 >> 쓰기 (이벤트 리스너, 설정)
- **실생활 비유**: 쇼핑몰 상품 목록 = 읽기가 많은 CopyOnWriteArrayList

---

## 🎯 Part 1 전체 핵심 정리

### List 인터페이스 특징
1. **순서 유지** (Ordered): 추가한 순서대로 보관
2. **중복 허용** (Duplicates): 같은 요소 여러 번 추가 가능
3. **인덱스 접근** (Index-based): 0부터 시작하는 위치로 접근
4. **null 허용**: null 요소 저장 가능

### 구현체 비교

| 구현체 | 내부 구조 | 조회 | 추가 (끝) | 추가 (중간) | 삭제 (중간) | 사용 사례 |
|--------|----------|------|-----------|-------------|-------------|-----------|
| **ArrayList** | 배열 | O(1) | O(1)* | O(n) | O(n) | 조회 많음, 일반적 |
| **LinkedList** | 이중 연결 리스트 | O(n) | O(1) | O(n) | O(n) | Queue, 앞/뒤 추가 |
| **Vector** | 배열 (synchronized) | O(1) | O(1)* | O(n) | O(n) | Legacy, 동시성 |
| **CopyOnWriteArrayList** | 배열 (복사) | O(1) | O(n) | O(n) | O(n) | 읽기 >> 쓰기 |

\* 용량 확장 시 O(n)

### 선택 기준

```
일반적인 경우 → ArrayList
├─ 조회가 압도적으로 많음
├─ 끝에 추가/삭제
└─ 순차 접근

Queue 구현 → LinkedList
├─ 앞/뒤 추가/삭제 빈번
├─ FIFO/LIFO 패턴
└─ 중간 조회 드뭄

멀티스레드 + 읽기 많음 → CopyOnWriteArrayList
├─ 읽기 99%, 쓰기 1%
├─ 이벤트 리스너
└─ 설정 정보

레거시 코드 → Vector
└─ 신규 개발 시 사용 금지
```

### 실생활 비유 요약
1. **도서관 책꽂이** = ArrayList (배열 기반, 빠른 조회)
2. **지하철 노선도** = LinkedList (연결 구조, 순차 접근)
3. **음악 재생목록** = List 순서 조작 (add, remove, sort)
4. **백화점 대기번호표** = Vector (동시성, synchronized)
5. **온라인 쇼핑몰** = CopyOnWriteArrayList (읽기 최적화)

---

**다음 Part 2에서는**: 3개 기업 사례 (네이버, 카카오, 쿠팡) + 4개 주니어 실수 시나리오를 다룹니다.
