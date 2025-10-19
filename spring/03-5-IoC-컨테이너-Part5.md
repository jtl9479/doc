# 03장: IoC 컨테이너 - Part 5 (실전 프로젝트)

**[← 이전: Part 4](03-4-IoC-컨테이너-Part4.md)** | **[다음: Part 6 →](03-6-IoC-컨테이너-Part6.md)**

---

## 🛠️ 실전 프로젝트

### 프로젝트: 도서 대출 관리 시스템

**난이도**: ⭐⭐⭐☆☆
**예상 소요 시간**: 2-3시간
**학습 목표**: IoC 컨테이너와 의존성 주입을 활용한 완전한 애플리케이션 구축

---

### 요구사항 분석

#### 기능 요구사항
- [ ] 도서 등록/조회/삭제
- [ ] 회원 등록/조회
- [ ] 도서 대출/반납
- [ ] 대출 가능 여부 확인
- [ ] 대출 현황 조회

#### 기술 요구사항
- [ ] Spring Boot 3.2+
- [ ] IoC 컨테이너 활용
- [ ] 계층별 Bean 분리 (Controller, Service, Repository)
- [ ] 인터페이스 기반 설계
- [ ] Java Configuration 활용

#### 비기능 요구사항
- [ ] 성능: 대출 처리 100ms 이하
- [ ] 테스트: 단위 테스트 커버리지 80% 이상
- [ ] 확장성: 알림 기능 추가 용이

---

### 프로젝트 구조

```
library-management/
├── src/
│   ├── main/
│   │   ├── java/com/example/library/
│   │   │   ├── LibraryApplication.java
│   │   │   ├── config/
│   │   │   │   └── AppConfig.java
│   │   │   ├── domain/
│   │   │   │   ├── Book.java
│   │   │   │   ├── Member.java
│   │   │   │   └── Loan.java
│   │   │   ├── repository/
│   │   │   │   ├── BookRepository.java
│   │   │   │   ├── MemberRepository.java
│   │   │   │   ├── LoanRepository.java
│   │   │   │   └── impl/
│   │   │   │       ├── MemoryBookRepository.java
│   │   │   │       ├── MemoryMemberRepository.java
│   │   │   │       └── MemoryLoanRepository.java
│   │   │   ├── service/
│   │   │   │   ├── BookService.java
│   │   │   │   ├── MemberService.java
│   │   │   │   ├── LoanService.java
│   │   │   │   └── NotificationService.java
│   │   │   └── controller/
│   │   │       └── LibraryController.java
│   │   └── resources/
│   │       └── application.properties
│   └── test/
│       └── java/com/example/library/
│           └── service/
│               └── LoanServiceTest.java
└── pom.xml
```

---

### 설계 의사결정

#### 왜 이렇게 설계했는가?

1. **결정 1: 인터페이스 기반 Repository**
   - 이유: 나중에 JPA, MyBatis 등으로 교체 용이
   - 대안: 구현 클래스에 직접 의존
   - 선택 근거: 유연성과 테스트 용이성

2. **결정 2: Service 계층 분리**
   - 이유: 비즈니스 로직을 Controller와 분리
   - 대안: Controller에 모든 로직 작성
   - 선택 근거: 재사용성, 테스트 용이성

3. **결정 3: NotificationService 인터페이스**
   - 이유: 이메일, SMS 등 다양한 알림 방식 지원
   - 대안: 구체적 알림 서비스에 의존
   - 선택 근거: Strategy 패턴으로 확장 용이

---

### 단계별 구현 가이드

#### 1단계: 프로젝트 초기 설정

```bash
# Spring Initializr로 프로젝트 생성
spring init \
  --dependencies=web,lombok \
  --type=maven-project \
  --java-version=17 \
  --artifact=library-management \
  --package-name=com.example.library \
  library-management

cd library-management
```

**체크포인트**:
- [ ] Spring Boot 프로젝트 생성 완료
- [ ] Lombok 의존성 추가 확인
- [ ] Maven 빌드 성공 확인

---

#### 2단계: Domain 객체 생성

```java
// 파일: src/main/java/com/example/library/domain/Book.java
package com.example.library.domain;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Book {
    private Long id;
    private String title;
    private String author;
    private String isbn;
    private boolean available;  // 대출 가능 여부
}
```

```java
// 파일: src/main/java/com/example/library/domain/Member.java
package com.example.library.domain;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Member {
    private Long id;
    private String name;
    private String email;
}
```

```java
// 파일: src/main/java/com/example/library/domain/Loan.java
package com.example.library.domain;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Loan {
    private Long id;
    private Long bookId;
    private Long memberId;
    private LocalDateTime loanDate;
    private LocalDateTime returnDate;
    private boolean returned;
}
```

**코드 설명**:
- Lombok의 `@Data`로 getter/setter 자동 생성
- 도메인 객체는 Spring Bean이 아님 (데이터만 담는 객체)

---

#### 3단계: Repository 계층 구현

```java
// 파일: src/main/java/com/example/library/repository/BookRepository.java
package com.example.library.repository;

import com.example.library.domain.Book;
import java.util.List;
import java.util.Optional;

// 인터페이스로 정의 (구현체는 나중에 교체 가능)
public interface BookRepository {
    Book save(Book book);
    Optional<Book> findById(Long id);
    List<Book> findAll();
    List<Book> findAvailableBooks();
    void deleteById(Long id);
}
```

```java
// 파일: src/main/java/com/example/library/repository/MemberRepository.java
package com.example.library.repository;

import com.example.library.domain.Member;
import java.util.List;
import java.util.Optional;

public interface MemberRepository {
    Member save(Member member);
    Optional<Member> findById(Long id);
    List<Member> findAll();
}
```

```java
// 파일: src/main/java/com/example/library/repository/LoanRepository.java
package com.example.library.repository;

import com.example.library.domain.Loan;
import java.util.List;
import java.util.Optional;

public interface LoanRepository {
    Loan save(Loan loan);
    Optional<Loan> findById(Long id);
    List<Loan> findByMemberId(Long memberId);
    List<Loan> findActiveLoans();
}
```

```java
// 파일: src/main/java/com/example/library/repository/impl/MemoryBookRepository.java
package com.example.library.repository.impl;

import com.example.library.domain.Book;
import com.example.library.repository.BookRepository;
import org.springframework.stereotype.Repository;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

@Repository  // Spring Bean으로 등록
public class MemoryBookRepository implements BookRepository {

    // Thread-safe한 자료구조 사용
    private final Map<Long, Book> store = new ConcurrentHashMap<>();
    private final AtomicLong sequence = new AtomicLong(1);

    @Override
    public Book save(Book book) {
        if (book.getId() == null) {
            book.setId(sequence.getAndIncrement());
        }
        store.put(book.getId(), book);
        return book;
    }

    @Override
    public Optional<Book> findById(Long id) {
        return Optional.ofNullable(store.get(id));
    }

    @Override
    public List<Book> findAll() {
        return new ArrayList<>(store.values());
    }

    @Override
    public List<Book> findAvailableBooks() {
        return store.values().stream()
                .filter(Book::isAvailable)
                .collect(Collectors.toList());
    }

    @Override
    public void deleteById(Long id) {
        store.remove(id);
    }

    // 테스트용 초기화 메서드
    public void clear() {
        store.clear();
    }
}
```

```java
// 파일: src/main/java/com/example/library/repository/impl/MemoryMemberRepository.java
package com.example.library.repository.impl;

import com.example.library.domain.Member;
import com.example.library.repository.MemberRepository;
import org.springframework.stereotype.Repository;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

@Repository
public class MemoryMemberRepository implements MemberRepository {

    private final Map<Long, Member> store = new ConcurrentHashMap<>();
    private final AtomicLong sequence = new AtomicLong(1);

    @Override
    public Member save(Member member) {
        if (member.getId() == null) {
            member.setId(sequence.getAndIncrement());
        }
        store.put(member.getId(), member);
        return member;
    }

    @Override
    public Optional<Member> findById(Long id) {
        return Optional.ofNullable(store.get(id));
    }

    @Override
    public List<Member> findAll() {
        return new ArrayList<>(store.values());
    }
}
```

```java
// 파일: src/main/java/com/example/library/repository/impl/MemoryLoanRepository.java
package com.example.library.repository.impl;

import com.example.library.domain.Loan;
import com.example.library.repository.LoanRepository;
import org.springframework.stereotype.Repository;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

@Repository
public class MemoryLoanRepository implements LoanRepository {

    private final Map<Long, Loan> store = new ConcurrentHashMap<>();
    private final AtomicLong sequence = new AtomicLong(1);

    @Override
    public Loan save(Loan loan) {
        if (loan.getId() == null) {
            loan.setId(sequence.getAndIncrement());
        }
        store.put(loan.getId(), loan);
        return loan;
    }

    @Override
    public Optional<Loan> findById(Long id) {
        return Optional.ofNullable(store.get(id));
    }

    @Override
    public List<Loan> findByMemberId(Long memberId) {
        return store.values().stream()
                .filter(loan -> loan.getMemberId().equals(memberId))
                .collect(Collectors.toList());
    }

    @Override
    public List<Loan> findActiveLoans() {
        return store.values().stream()
                .filter(loan -> !loan.isReturned())
                .collect(Collectors.toList());
    }
}
```

**코드 설명**:
- **인터페이스 분리**: Repository 인터페이스와 구현체 분리
- **@Repository**: Spring이 Bean으로 등록, 예외 변환 기능 제공
- **Thread-safe**: ConcurrentHashMap과 AtomicLong으로 동시성 처리

---

#### 4단계: Service 계층 구현

```java
// 파일: src/main/java/com/example/library/service/BookService.java
package com.example.library.service;

import com.example.library.domain.Book;
import com.example.library.repository.BookRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class BookService {

    private final BookRepository bookRepository;

    // 생성자 주입 (권장)
    @Autowired
    public BookService(BookRepository bookRepository) {
        this.bookRepository = bookRepository;
    }

    public Book registerBook(String title, String author, String isbn) {
        Book book = new Book(null, title, author, isbn, true);
        return bookRepository.save(book);
    }

    public Book findBook(Long id) {
        return bookRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Book not found: " + id));
    }

    public List<Book> findAvailableBooks() {
        return bookRepository.findAvailableBooks();
    }

    public List<Book> findAllBooks() {
        return bookRepository.findAll();
    }
}
```

```java
// 파일: src/main/java/com/example/library/service/MemberService.java
package com.example.library.service;

import com.example.library.domain.Member;
import com.example.library.repository.MemberRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class MemberService {

    private final MemberRepository memberRepository;

    @Autowired
    public MemberService(MemberRepository memberRepository) {
        this.memberRepository = memberRepository;
    }

    public Member registerMember(String name, String email) {
        Member member = new Member(null, name, email);
        return memberRepository.save(member);
    }

    public Member findMember(Long id) {
        return memberRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Member not found: " + id));
    }

    public List<Member> findAllMembers() {
        return memberRepository.findAll();
    }
}
```

```java
// 파일: src/main/java/com/example/library/service/NotificationService.java
package com.example.library.service;

// 알림 서비스 인터페이스
public interface NotificationService {
    void sendLoanNotification(Long memberId, String bookTitle);
    void sendReturnNotification(Long memberId, String bookTitle);
}
```

```java
// 파일: src/main/java/com/example/library/service/ConsoleNotificationService.java
package com.example.library.service;

import org.springframework.context.annotation.Primary;
import org.springframework.stereotype.Service;

@Service
@Primary  // 기본 구현체로 지정
public class ConsoleNotificationService implements NotificationService {

    @Override
    public void sendLoanNotification(Long memberId, String bookTitle) {
        System.out.println("📚 [대출 알림] 회원 " + memberId + "님, \"" + bookTitle + "\" 대출 완료!");
    }

    @Override
    public void sendReturnNotification(Long memberId, String bookTitle) {
        System.out.println("📚 [반납 알림] 회원 " + memberId + "님, \"" + bookTitle + "\" 반납 완료!");
    }
}
```

```java
// 파일: src/main/java/com/example/library/service/LoanService.java
package com.example.library.service;

import com.example.library.domain.Book;
import com.example.library.domain.Loan;
import com.example.library.domain.Member;
import com.example.library.repository.BookRepository;
import com.example.library.repository.LoanRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class LoanService {

    private final LoanRepository loanRepository;
    private final BookRepository bookRepository;
    private final NotificationService notificationService;

    // 여러 의존성 주입
    @Autowired
    public LoanService(LoanRepository loanRepository,
                       BookRepository bookRepository,
                       NotificationService notificationService) {
        this.loanRepository = loanRepository;
        this.bookRepository = bookRepository;
        this.notificationService = notificationService;
    }

    public Loan loanBook(Long memberId, Long bookId) {
        // 1. 도서 조회
        Book book = bookRepository.findById(bookId)
                .orElseThrow(() -> new IllegalArgumentException("Book not found"));

        // 2. 대출 가능 여부 확인
        if (!book.isAvailable()) {
            throw new IllegalStateException("Book is not available");
        }

        // 3. 대출 기록 생성
        Loan loan = new Loan(
                null,
                bookId,
                memberId,
                LocalDateTime.now(),
                null,
                false
        );
        loan = loanRepository.save(loan);

        // 4. 도서 상태 업데이트
        book.setAvailable(false);
        bookRepository.save(book);

        // 5. 알림 발송
        notificationService.sendLoanNotification(memberId, book.getTitle());

        return loan;
    }

    public Loan returnBook(Long loanId) {
        // 1. 대출 기록 조회
        Loan loan = loanRepository.findById(loanId)
                .orElseThrow(() -> new IllegalArgumentException("Loan not found"));

        if (loan.isReturned()) {
            throw new IllegalStateException("Already returned");
        }

        // 2. 반납 처리
        loan.setReturned(true);
        loan.setReturnDate(LocalDateTime.now());
        loan = loanRepository.save(loan);

        // 3. 도서 상태 업데이트
        Book book = bookRepository.findById(loan.getBookId())
                .orElseThrow(() -> new IllegalArgumentException("Book not found"));
        book.setAvailable(true);
        bookRepository.save(book);

        // 4. 알림 발송
        notificationService.sendReturnNotification(loan.getMemberId(), book.getTitle());

        return loan;
    }

    public List<Loan> findMemberLoans(Long memberId) {
        return loanRepository.findByMemberId(memberId);
    }

    public List<Loan> findActiveLoans() {
        return loanRepository.findActiveLoans();
    }
}
```

**코드 설명**:
- **라인 14-19**: 생성자 주입으로 3개의 의존성 주입
- **라인 23-42**: 대출 프로세스 (도서 조회 → 검증 → 대출 → 상태 업데이트 → 알림)
- **라인 44-63**: 반납 프로세스
- **NotificationService**: 인터페이스로 알림 방식 유연하게 교체 가능

---

#### 5단계: Controller 구현

```java
// 파일: src/main/java/com/example/library/controller/LibraryController.java
package com.example.library.controller;

import com.example.library.domain.Book;
import com.example.library.domain.Loan;
import com.example.library.domain.Member;
import com.example.library.service.BookService;
import com.example.library.service.LoanService;
import com.example.library.service.MemberService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
public class LibraryController {

    private final BookService bookService;
    private final MemberService memberService;
    private final LoanService loanService;

    @Autowired
    public LibraryController(BookService bookService,
                             MemberService memberService,
                             LoanService loanService) {
        this.bookService = bookService;
        this.memberService = memberService;
        this.loanService = loanService;
    }

    // 도서 등록
    @PostMapping("/books")
    public Book registerBook(@RequestParam String title,
                             @RequestParam String author,
                             @RequestParam String isbn) {
        return bookService.registerBook(title, author, isbn);
    }

    // 도서 조회
    @GetMapping("/books/{id}")
    public Book getBook(@PathVariable Long id) {
        return bookService.findBook(id);
    }

    // 전체 도서 조회
    @GetMapping("/books")
    public List<Book> getAllBooks() {
        return bookService.findAllBooks();
    }

    // 대출 가능 도서 조회
    @GetMapping("/books/available")
    public List<Book> getAvailableBooks() {
        return bookService.findAvailableBooks();
    }

    // 회원 등록
    @PostMapping("/members")
    public Member registerMember(@RequestParam String name,
                                 @RequestParam String email) {
        return memberService.registerMember(name, email);
    }

    // 회원 조회
    @GetMapping("/members/{id}")
    public Member getMember(@PathVariable Long id) {
        return memberService.findMember(id);
    }

    // 도서 대출
    @PostMapping("/loans")
    public Loan loanBook(@RequestParam Long memberId,
                         @RequestParam Long bookId) {
        return loanService.loanBook(memberId, bookId);
    }

    // 도서 반납
    @PostMapping("/loans/{id}/return")
    public Loan returnBook(@PathVariable Long id) {
        return loanService.returnBook(id);
    }

    // 회원별 대출 현황
    @GetMapping("/members/{id}/loans")
    public List<Loan> getMemberLoans(@PathVariable Long id) {
        return loanService.findMemberLoans(id);
    }

    // 전체 대출 현황
    @GetMapping("/loans/active")
    public List<Loan> getActiveLoans() {
        return loanService.findActiveLoans();
    }
}
```

**코드 설명**:
- **@RestController**: JSON 자동 변환
- **@Autowired**: 3개의 Service 주입
- **REST API**: CRUD 작업을 HTTP 메서드로 매핑

---

#### 6단계: 메인 애플리케이션

```java
// 파일: src/main/java/com/example/library/LibraryApplication.java
package com.example.library;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication  // @ComponentScan 포함
public class LibraryApplication {

    public static void main(String[] args) {
        SpringApplication.run(LibraryApplication.class, args);
        System.out.println("📚 도서 대출 관리 시스템 시작!");
    }
}
```

---

### 실행 및 테스트

#### 실행

```bash
# Maven
./mvnw spring-boot:run

# Gradle
./gradlew bootRun
```

#### 수동 테스트 (Postman 또는 curl)

```bash
# 1. 도서 등록
curl -X POST "http://localhost:8080/api/books?title=Clean Code&author=Robert Martin&isbn=978-0132350884"

# 응답: {"id":1,"title":"Clean Code","author":"Robert Martin","isbn":"978-0132350884","available":true}

# 2. 회원 등록
curl -X POST "http://localhost:8080/api/members?name=홍길동&email=hong@example.com"

# 응답: {"id":1,"name":"홍길동","email":"hong@example.com"}

# 3. 도서 대출
curl -X POST "http://localhost:8080/api/loans?memberId=1&bookId=1"

# 콘솔 출력: 📚 [대출 알림] 회원 1님, "Clean Code" 대출 완료!
# 응답: {"id":1,"bookId":1,"memberId":1,"loanDate":"2024-01-15T10:30:00","returnDate":null,"returned":false}

# 4. 대출 가능 도서 조회
curl "http://localhost:8080/api/books/available"

# 응답: [] (대출되어 없음)

# 5. 도서 반납
curl -X POST "http://localhost:8080/api/loans/1/return"

# 콘솔 출력: 📚 [반납 알림] 회원 1님, "Clean Code" 반납 완료!
```

---

**[← 이전: Part 4](03-4-IoC-컨테이너-Part4.md)** | **[다음: Part 6 →](03-6-IoC-컨테이너-Part6.md)**
