# 01장: Spring이란? - Part 3: 실전 프로젝트 & 면접 대비

> **Part 2에서 이어집니다**: 기본 실습과 실무 사례를 학습했다면, 이제 실전 프로젝트로 완벽하게 마스터하세요!

---

## 📚 목차
- [실전 프로젝트](#실전-프로젝트)
- [FAQ](#faq)
- [면접 질문 리스트](#면접-질문-리스트)
- [면접 질문 리스트 답안](#면접-질문-리스트-답안)
- [핵심 정리](#핵심-정리)
- [다음 단계](#다음-단계)

---

## 🛠️ 실전 프로젝트

### 프로젝트: 도서 관리 시스템 (Spring 핵심 개념 종합)

**난이도**: ⭐⭐⭐☆☆
**예상 소요 시간**: 3-4시간
**학습 목표**: IoC, DI, AOP를 모두 사용하여 완전한 Spring 애플리케이션 구축

---

### 요구사항 분석

#### 기능 요구사항
- [ ] 도서 등록 (Create)
- [ ] 도서 조회 (Read)
- [ ] 도서 수정 (Update)
- [ ] 도서 삭제 (Delete)
- [ ] 모든 작업 로깅 (AOP)

#### 기술 요구사항
- [ ] Spring Boot 사용
- [ ] Layered Architecture (Controller-Service-Repository)
- [ ] 생성자 주입 (DI)
- [ ] AOP로 로깅

#### 비기능 요구사항
- [ ] 코드 간결성
- [ ] 테스트 가능성
- [ ] 유지보수 용이성

---

### 프로젝트 구조

```
book-management/
├── src/
│   ├── main/
│   │   ├── java/com/myapp/
│   │   │   ├── BookManagementApplication.java
│   │   │   ├── controller/
│   │   │   │   └── BookController.java
│   │   │   ├── service/
│   │   │   │   ├── BookService.java
│   │   │   │   └── BookServiceImpl.java
│   │   │   ├── repository/
│   │   │   │   └── BookRepository.java
│   │   │   ├── domain/
│   │   │   │   └── Book.java
│   │   │   └── aspect/
│   │   │       └── LoggingAspect.java
│   │   └── resources/
│   │       └── application.yml
│   └── test/
│       └── java/com/myapp/
│           └── service/
│               └── BookServiceTest.java
└── pom.xml
```

---

### 단계별 구현 가이드

#### 1단계: 프로젝트 초기 설정

**Spring Initializr 사용**:
```
https://start.spring.io/

Project: Maven
Language: Java
Spring Boot: 3.2.x
Packaging: Jar
Java: 17

Dependencies:
- Spring Web
- Spring Boot DevTools
- Lombok
- Spring AOP
```

**pom.xml**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project>
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
    </parent>

    <groupId>com.myapp</groupId>
    <artifactId>book-management</artifactId>
    <version>1.0.0</version>

    <dependencies>
        <!-- Spring Web -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- Spring AOP -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-aop</artifactId>
        </dependency>

        <!-- Lombok -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>

        <!-- Test -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

**체크포인트**:
- [ ] Spring Initializr로 프로젝트 생성
- [ ] IDE에서 프로젝트 열기
- [ ] Maven 의존성 다운로드 확인

---

#### 2단계: Domain 클래스 작성

```java
// src/main/java/com/myapp/domain/Book.java
package com.myapp.domain;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@ToString
public class Book {
    private Long id;
    private String title;
    private String author;
    private Integer price;

    // 비즈니스 로직
    public void updateInfo(String title, String author, Integer price) {
        this.title = title;
        this.author = author;
        this.price = price;
    }

    public boolean isExpensive() {
        return price > 30000;
    }
}
```

**코드 설명**:
- **@Getter, @Setter**: Lombok이 getter/setter 자동 생성
- **@NoArgsConstructor**: 기본 생성자
- **@AllArgsConstructor**: 모든 필드 생성자
- **@ToString**: toString() 메서드 자동 생성
- **비즈니스 로직**: 도메인 객체에 메서드 추가

---

#### 3단계: Repository Layer 구현

```java
// src/main/java/com/myapp/repository/BookRepository.java
package com.myapp.repository;

import com.myapp.domain.Book;
import org.springframework.stereotype.Repository;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

@Repository  // ✅ Spring Bean 등록
public class BookRepository {

    // 실제로는 DB 사용, 여기서는 메모리
    private final Map<Long, Book> database = new ConcurrentHashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(1);

    /**
     * 도서 저장
     */
    public Book save(Book book) {
        if (book.getId() == null) {
            // 새로운 도서: ID 자동 생성
            book.setId(idGenerator.getAndIncrement());
        }
        database.put(book.getId(), book);
        return book;
    }

    /**
     * ID로 도서 조회
     */
    public Optional<Book> findById(Long id) {
        return Optional.ofNullable(database.get(id));
    }

    /**
     * 모든 도서 조회
     */
    public List<Book> findAll() {
        return new ArrayList<>(database.values());
    }

    /**
     * 도서 삭제
     */
    public void deleteById(Long id) {
        database.remove(id);
    }

    /**
     * 도서 존재 여부
     */
    public boolean existsById(Long id) {
        return database.containsKey(id);
    }
}
```

**코드 설명**:
- **@Repository**: Data Access Layer를 나타내는 Bean
- **ConcurrentHashMap**: Thread-safe한 메모리 저장소
- **AtomicLong**: Thread-safe한 ID 생성
- **Optional**: null 안전성

---

#### 4단계: Service Layer 구현

```java
// src/main/java/com/myapp/service/BookService.java (인터페이스)
package com.myapp.service;

import com.myapp.domain.Book;
import java.util.List;

public interface BookService {
    Book registerBook(String title, String author, Integer price);
    Book getBook(Long id);
    List<Book> getAllBooks();
    Book updateBook(Long id, String title, String author, Integer price);
    void deleteBook(Long id);
}

// src/main/java/com/myapp/service/BookServiceImpl.java (구현체)
package com.myapp.service;

import com.myapp.domain.Book;
import com.myapp.repository.BookRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;

@Service  // ✅ Spring Bean 등록
@Slf4j
public class BookServiceImpl implements BookService {

    private final BookRepository bookRepository;

    // ✅ 생성자 주입 (DI)
    public BookServiceImpl(BookRepository bookRepository) {
        this.bookRepository = bookRepository;
        log.info("BookServiceImpl 생성됨");
    }

    @Override
    public Book registerBook(String title, String author, Integer price) {
        // 1. 유효성 검사
        validateBookInfo(title, author, price);

        // 2. 도서 생성
        Book book = new Book(null, title, author, price);

        // 3. 저장
        Book savedBook = bookRepository.save(book);

        log.info("도서 등록 완료: {}", savedBook);
        return savedBook;
    }

    @Override
    public Book getBook(Long id) {
        return bookRepository.findById(id)
            .orElseThrow(() -> new IllegalArgumentException(
                "도서를 찾을 수 없습니다. ID: " + id
            ));
    }

    @Override
    public List<Book> getAllBooks() {
        return bookRepository.findAll();
    }

    @Override
    public Book updateBook(Long id, String title, String author, Integer price) {
        // 1. 기존 도서 조회
        Book book = getBook(id);

        // 2. 정보 업데이트
        book.updateInfo(title, author, price);

        // 3. 저장
        Book updatedBook = bookRepository.save(book);

        log.info("도서 수정 완료: {}", updatedBook);
        return updatedBook;
    }

    @Override
    public void deleteBook(Long id) {
        // 1. 존재 여부 확인
        if (!bookRepository.existsById(id)) {
            throw new IllegalArgumentException(
                "도서를 찾을 수 없습니다. ID: " + id
            );
        }

        // 2. 삭제
        bookRepository.deleteById(id);

        log.info("도서 삭제 완료: ID={}", id);
    }

    // private 유효성 검사 메서드
    private void validateBookInfo(String title, String author, Integer price) {
        if (title == null || title.trim().isEmpty()) {
            throw new IllegalArgumentException("제목은 필수입니다.");
        }
        if (author == null || author.trim().isEmpty()) {
            throw new IllegalArgumentException("저자는 필수입니다.");
        }
        if (price == null || price < 0) {
            throw new IllegalArgumentException("가격은 0 이상이어야 합니다.");
        }
    }
}
```

**코드 설명**:
- **인터페이스 분리**: 추상화, 테스트 용이
- **생성자 주입**: final로 불변성, DI의 베스트 프랙티스
- **유효성 검사**: 비즈니스 로직에서 검증
- **Optional 활용**: null 안전성
- **로깅**: @Slf4j로 간편한 로깅

---

#### 5단계: Controller Layer 구현

```java
// src/main/java/com/myapp/controller/BookController.java
package com.myapp.controller;

import com.myapp.domain.Book;
import com.myapp.service.BookService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController  // ✅ REST API Controller
@RequestMapping("/api/books")
@Slf4j
public class BookController {

    private final BookService bookService;

    // ✅ 생성자 주입
    public BookController(BookService bookService) {
        this.bookService = bookService;
    }

    /**
     * 도서 등록
     * POST /api/books
     */
    @PostMapping
    public ResponseEntity<Book> createBook(@RequestBody Map<String, Object> request) {
        String title = (String) request.get("title");
        String author = (String) request.get("author");
        Integer price = (Integer) request.get("price");

        Book book = bookService.registerBook(title, author, price);

        return ResponseEntity
            .status(HttpStatus.CREATED)
            .body(book);
    }

    /**
     * 도서 조회
     * GET /api/books/{id}
     */
    @GetMapping("/{id}")
    public ResponseEntity<Book> getBook(@PathVariable Long id) {
        Book book = bookService.getBook(id);
        return ResponseEntity.ok(book);
    }

    /**
     * 모든 도서 조회
     * GET /api/books
     */
    @GetMapping
    public ResponseEntity<List<Book>> getAllBooks() {
        List<Book> books = bookService.getAllBooks();
        return ResponseEntity.ok(books);
    }

    /**
     * 도서 수정
     * PUT /api/books/{id}
     */
    @PutMapping("/{id}")
    public ResponseEntity<Book> updateBook(
        @PathVariable Long id,
        @RequestBody Map<String, Object> request
    ) {
        String title = (String) request.get("title");
        String author = (String) request.get("author");
        Integer price = (Integer) request.get("price");

        Book book = bookService.updateBook(id, title, author, price);

        return ResponseEntity.ok(book);
    }

    /**
     * 도서 삭제
     * DELETE /api/books/{id}
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteBook(@PathVariable Long id) {
        bookService.deleteBook(id);
        return ResponseEntity.noContent().build();
    }

    /**
     * 예외 처리
     */
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, String>> handleIllegalArgument(
        IllegalArgumentException e
    ) {
        return ResponseEntity
            .badRequest()
            .body(Map.of("error", e.getMessage()));
    }
}
```

**코드 설명**:
- **@RestController**: REST API 컨트롤러
- **@RequestMapping**: 기본 경로 설정
- **CRUD 메서드**: HTTP 메서드별 매핑
- **@ExceptionHandler**: 예외를 HTTP 응답으로 변환

---

#### 6단계: AOP로 로깅 자동화

```java
// src/main/java/com/myapp/aspect/LoggingAspect.java
package com.myapp.aspect;

import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.*;
import org.springframework.stereotype.Component;

import java.util.Arrays;

@Aspect  // ✅ AOP Aspect
@Component
@Slf4j
public class LoggingAspect {

    /**
     * Service Layer의 모든 메서드 실행 전후 로깅
     */
    @Around("execution(* com.myapp.service..*(..))")
    public Object logServiceMethods(ProceedingJoinPoint joinPoint) throws Throwable {
        String methodName = joinPoint.getSignature().toShortString();
        Object[] args = joinPoint.getArgs();

        // 실행 전 로깅
        log.info("▶ [SERVICE] {} 시작 | 파라미터: {}",
            methodName, Arrays.toString(args));
        long startTime = System.currentTimeMillis();

        try {
            // 실제 메서드 실행
            Object result = joinPoint.proceed();

            // 실행 후 로깅
            long endTime = System.currentTimeMillis();
            log.info("◀ [SERVICE] {} 종료 | 소요시간: {}ms | 결과: {}",
                methodName, endTime - startTime, result);

            return result;

        } catch (Exception e) {
            // 에러 로깅
            log.error("✖ [SERVICE] {} 에러 발생: {}",
                methodName, e.getMessage());
            throw e;
        }
    }

    /**
     * Controller Layer의 모든 메서드 실행 전후 로깅
     */
    @Around("execution(* com.myapp.controller..*(..))")
    public Object logControllerMethods(ProceedingJoinPoint joinPoint) throws Throwable {
        String methodName = joinPoint.getSignature().toShortString();

        log.info("▶ [CONTROLLER] {} 요청 시작", methodName);
        long startTime = System.currentTimeMillis();

        try {
            Object result = joinPoint.proceed();

            long endTime = System.currentTimeMillis();
            log.info("◀ [CONTROLLER] {} 요청 완료 | {}ms",
                methodName, endTime - startTime);

            return result;

        } catch (Exception e) {
            log.error("✖ [CONTROLLER] {} 에러: {}",
                methodName, e.getMessage());
            throw e;
        }
    }
}
```

**AOP 포인트컷 설명**:
```
execution(* com.myapp.service..*(..))
    │     │      │         │  │  │
    │     │      │         │  │  └─ 모든 파라미터
    │     │      │         │  └──── 모든 메서드
    │     │      │         └─────── service 패키지 및 하위 패키지
    │     │      └───────────────── com.myapp
    │     └──────────────────────── 모든 접근 제한자
    └────────────────────────────── 모든 리턴 타입
```

---

#### 7단계: Application 클래스

```java
// src/main/java/com/myapp/BookManagementApplication.java
package com.myapp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication  // ✅ Spring Boot 메인 클래스
public class BookManagementApplication {

    public static void main(String[] args) {
        SpringApplication.run(BookManagementApplication.class, args);
        System.out.println("\n📚 도서 관리 시스템 시작됨!\n");
    }
}
```

---

#### 8단계: 테스트 코드 작성

```java
// src/test/java/com/myapp/service/BookServiceTest.java
package com.myapp.service;

import com.myapp.domain.Book;
import com.myapp.repository.BookRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;

import static org.junit.jupiter.api.Assertions.*;

class BookServiceTest {

    private BookService bookService;
    private BookRepository bookRepository;

    @BeforeEach
    void setUp() {
        // Mock 대신 실제 구현체 사용 (단순화)
        bookRepository = new BookRepository();
        bookService = new BookServiceImpl(bookRepository);
    }

    @Test
    @DisplayName("도서 등록 성공")
    void registerBook_성공() {
        // given
        String title = "스프링 부트 완전 정복";
        String author = "김영한";
        Integer price = 35000;

        // when
        Book book = bookService.registerBook(title, author, price);

        // then
        assertNotNull(book.getId());
        assertEquals(title, book.getTitle());
        assertEquals(author, book.getAuthor());
        assertEquals(price, book.getPrice());
    }

    @Test
    @DisplayName("제목이 없으면 예외 발생")
    void registerBook_제목없음_예외() {
        // given
        String title = "";
        String author = "김영한";
        Integer price = 35000;

        // when & then
        assertThrows(IllegalArgumentException.class, () -> {
            bookService.registerBook(title, author, price);
        });
    }

    @Test
    @DisplayName("도서 조회 성공")
    void getBook_성공() {
        // given
        Book savedBook = bookService.registerBook("책 제목", "저자", 10000);

        // when
        Book foundBook = bookService.getBook(savedBook.getId());

        // then
        assertEquals(savedBook.getId(), foundBook.getId());
        assertEquals("책 제목", foundBook.getTitle());
    }

    @Test
    @DisplayName("없는 도서 조회 시 예외")
    void getBook_없는도서_예외() {
        // given
        Long invalidId = 999L;

        // when & then
        assertThrows(IllegalArgumentException.class, () -> {
            bookService.getBook(invalidId);
        });
    }

    @Test
    @DisplayName("도서 수정 성공")
    void updateBook_성공() {
        // given
        Book book = bookService.registerBook("원래 제목", "원래 저자", 10000);

        // when
        Book updatedBook = bookService.updateBook(
            book.getId(),
            "새 제목",
            "새 저자",
            20000
        );

        // then
        assertEquals("새 제목", updatedBook.getTitle());
        assertEquals("새 저자", updatedBook.getAuthor());
        assertEquals(20000, updatedBook.getPrice());
    }

    @Test
    @DisplayName("도서 삭제 성공")
    void deleteBook_성공() {
        // given
        Book book = bookService.registerBook("삭제할 책", "저자", 10000);

        // when
        bookService.deleteBook(book.getId());

        // then
        assertThrows(IllegalArgumentException.class, () -> {
            bookService.getBook(book.getId());
        });
    }
}
```

---

### 실행 결과

**1. 애플리케이션 실행**:
```bash
mvn spring-boot:run

# 또는
./mvnw spring-boot:run

# 출력:
📚 도서 관리 시스템 시작됨!
```

**2. API 테스트 (curl or Postman)**:

```bash
# 1. 도서 등록
curl -X POST http://localhost:8080/api/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "스프링 부트 완전 정복",
    "author": "김영한",
    "price": 35000
  }'

# 응답:
{
  "id": 1,
  "title": "스프링 부트 완전 정복",
  "author": "김영한",
  "price": 35000
}

# 2. 모든 도서 조회
curl http://localhost:8080/api/books

# 3. 특정 도서 조회
curl http://localhost:8080/api/books/1

# 4. 도서 수정
curl -X PUT http://localhost:8080/api/books/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "스프링 부트 완전 정복 (개정판)",
    "author": "김영한",
    "price": 40000
  }'

# 5. 도서 삭제
curl -X DELETE http://localhost:8080/api/books/1
```

**3. 콘솔 로그 (AOP)**:
```
▶ [CONTROLLER] BookController.createBook(..) 요청 시작
▶ [SERVICE] BookServiceImpl.registerBook(..) 시작 | 파라미터: [스프링 부트 완전 정복, 김영한, 35000]
도서 등록 완료: Book(id=1, title=스프링 부트 완전 정복, author=김영한, price=35000)
◀ [SERVICE] BookServiceImpl.registerBook(..) 종료 | 소요시간: 5ms | 결과: Book(...)
◀ [CONTROLLER] BookController.createBook(..) 요청 완료 | 8ms
```

---

### 확장 아이디어

#### 추가 기능 1: 도서 검색
**난이도**: ⭐⭐⭐☆☆

```java
// BookRepository에 추가
public List<Book> findByTitleContaining(String keyword) {
    return database.values().stream()
        .filter(book -> book.getTitle().contains(keyword))
        .toList();
}

// BookService에 추가
public List<Book> searchBooks(String keyword) {
    return bookRepository.findByTitleContaining(keyword);
}

// BookController에 추가
@GetMapping("/search")
public ResponseEntity<List<Book>> searchBooks(@RequestParam String keyword) {
    List<Book> books = bookService.searchBooks(keyword);
    return ResponseEntity.ok(books);
}
```

#### 추가 기능 2: 페이징
**난이도**: ⭐⭐⭐⭐☆

---

### 코드 리뷰 포인트

#### 체크리스트
- [ ] 모든 Layer가 명확히 분리되어 있는가?
- [ ] 생성자 주입을 사용했는가?
- [ ] AOP가 정상 작동하는가?
- [ ] 예외 처리가 적절한가?
- [ ] 테스트 코드가 있는가?
- [ ] 로깅이 충분한가?

---

## ❓ FAQ

<details>
<summary><strong>Q1: Spring과 Spring Boot의 차이는?</strong></summary>

**A**: Spring Boot는 Spring을 더 쉽게 사용하게 해주는 도구입니다.

**상세 비교**:

| 항목 | Spring Framework | Spring Boot |
|------|-----------------|-------------|
| 설정 | XML 또는 Java Config (복잡) | Auto Configuration (자동) |
| 서버 | 외부 Tomcat 필요 | 내장 Tomcat |
| 의존성 | 하나하나 추가 | Starter로 묶음 |
| 실행 | WAR 배포 | JAR 실행 |

**코드 비교**:
```java
// Spring Framework (복잡)
@Configuration
@EnableWebMvc
public class WebConfig implements WebMvcConfigurer {
    @Bean
    public ViewResolver viewResolver() {
        // 수십 줄의 설정...
    }
}

// Spring Boot (간단)
@SpringBootApplication
public class App {
    public static void main(String[] args) {
        SpringApplication.run(App.class, args);
    }
}
```

**실무 팁**:
💡 신규 프로젝트는 무조건 Spring Boot 사용. Spring Framework는 레거시 유지보수 시에만.

</details>

<details>
<summary><strong>Q2: IoC와 DI의 차이는?</strong></summary>

**A**: IoC는 개념, DI는 구현 방법입니다.

**IoC (Inversion of Control)**:
- 제어의 역전
- 객체 생성/관리를 프레임워크가 담당
- 개념/원칙

**DI (Dependency Injection)**:
- 의존성 주입
- IoC를 구현하는 구체적인 방법
- 실제 기술

**비유**:
```
IoC = "배달앱이 알아서 해줌" (개념)
DI = "배달기사가 직접 문 앞까지 배달" (구현)
```

**코드**:
```java
// IoC: Spring이 제어
@Service
public class OrderService {
    // DI: Spring이 주입
    private final PaymentService paymentService;

    public OrderService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }
}
```

</details>

<details>
<summary><strong>Q3: @Component, @Service, @Repository 차이는?</strong></summary>

**A**: 기능은 동일, 역할을 명시하기 위한 것입니다.

| 어노테이션 | 용도 | 계층 |
|-----------|------|------|
| @Component | 일반 Bean | 기타 |
| @Service | 비즈니스 로직 | Service |
| @Repository | 데이터 접근 | Repository |
| @Controller | 웹 요청 처리 | Controller |

**왜 구분하나?**
1. 가독성 (코드만 봐도 역할 파악)
2. AOP 적용 시 구분 용이
3. 예외 변환 (Repository는 DB 예외 변환)

**실무 팁**:
💡 항상 역할에 맞는 어노테이션 사용. @Component는 일반적인 Bean에만.

</details>

<details>
<summary><strong>Q4: 생성자 주입을 왜 권장하나?</strong></summary>

**A**: 불변성, 테스트 용이성, NPE 방지 때문입니다.

**장점**:
```java
@Service
public class OrderService {
    private final PaymentService paymentService;  // final!

    // 생성 시점에 주입 → NPE 불가능
    public OrderService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }

    // 테스트도 쉬움
    public void createOrder() {
        paymentService.process();  // NPE 걱정 없음
    }
}
```

**필드 주입의 문제**:
```java
@Service
public class OrderService {
    @Autowired
    private PaymentService paymentService;  // final 불가

    // paymentService가 null일 수도!
    public void createOrder() {
        paymentService.process();  // NPE 가능
    }
}
```

</details>

<details>
<summary><strong>Q5: AOP는 언제 사용하나?</strong></summary>

**A**: 여러 곳에 반복되는 코드(횡단 관심사)를 한 곳에 모을 때 사용합니다.

**횡단 관심사 (Cross-Cutting Concerns)**:
- 로깅
- 트랜잭션
- 보안 (인증/인가)
- 캐싱
- 성능 모니터링

**사용 예**:
```java
// AOP 없이 - 모든 메서드에 반복
public void method1() {
    log.info("시작");
    // 비즈니스 로직
    log.info("끝");
}

// AOP 사용 - 한 곳에 모음
@Aspect
@Component
public class LoggingAspect {
    @Around("execution(* com.myapp..*(..))")
    public Object logAround(ProceedingJoinPoint jp) {
        log.info("시작");
        Object result = jp.proceed();
        log.info("끝");
        return result;
    }
}
```

**실무 팁**:
💡 반복 코드 3번 이상 나오면 AOP 고려

</details>

<details>
<summary><strong>Q6: Spring은 무료인가?</strong></summary>

**A**: 네, 완전 무료이며 오픈소스입니다.

**라이선스**:
- Apache License 2.0
- 상업적 사용 가능
- 수정/배포 자유

**비용**:
- Spring Framework: 무료
- Spring Boot: 무료
- Spring Cloud: 무료
- Spring Security: 무료

**유료 서비스** (선택):
- Spring Academy (교육)
- VMware Tanzu (엔터프라이즈 지원)

**실무 팁**:
💡 무료로 모든 기능 사용 가능. 대기업도 무료 버전 사용.

</details>

<details>
<summary><strong>Q7: Spring 배우는 데 얼마나 걸리나?</strong></summary>

**A**: 기초는 2주, 실무 수준은 3-6개월입니다.

**학습 단계**:
```
1주차: IoC/DI 개념 이해
2주차: 기본 프로젝트 완성

1개월: MVC, JPA 학습
2개월: REST API, Security
3개월: 실무 프로젝트 완성

6개월: 고급 기능, MSA
```

**시간 투자**:
- 하루 1시간: 6개월
- 하루 2시간: 3개월
- 하루 4시간: 1.5개월

**실무 팁**:
💡 매일 조금씩 꾸준히 하는 것이 중요. 주말에 몰아서 하면 비효율적.

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. Spring Framework란 무엇인가요?</strong></summary>

**모범 답안 포인트**:
- Java 기반 엔터프라이즈 애플리케이션 프레임워크
- IoC/DI를 통한 느슨한 결합
- AOP로 횡단 관심사 분리
- 다양한 모듈 (MVC, Data, Security)

**예시 답변**:
> "Spring Framework는 Java 기반의 엔터프라이즈 애플리케이션 개발을 위한 프레임워크입니다. 핵심 기능인 IoC Container가 객체의 생성과 생명주기를 관리하고, DI를 통해 객체 간 느슨한 결합을 제공합니다. 또한 AOP를 통해 로깅, 트랜잭션 같은 횡단 관심사를 분리할 수 있으며, Spring MVC, Spring Data, Spring Security 등 다양한 모듈을 제공하여 생산적인 개발을 지원합니다."

**꼬리 질문**:
- Q: Spring과 Spring Boot의 차이는?
- A: Spring Boot는 Spring을 더 쉽게 사용하도록 자동 설정과 내장 서버를 제공하는 도구입니다.

</details>

<details>
<summary><strong>2. IoC(Inversion of Control)가 무엇인가요?</strong></summary>

**모범 답안 포인트**:
- 제어의 역전
- 객체 생성/관리를 프레임워크가 담당
- 개발자는 비즈니스 로직에 집중

**예시 답변**:
> "IoC는 Inversion of Control의 약자로 제어의 역전을 의미합니다. 전통적인 방식에서는 개발자가 new 키워드로 객체를 직접 생성하고 관리했지만, Spring에서는 IoC Container가 객체의 생성, 의존성 주입, 생명주기 관리를 담당합니다. 이를 통해 객체 간 결합도를 낮추고, 개발자는 비즈니스 로직에만 집중할 수 있습니다."

</details>

<details>
<summary><strong>3. DI(Dependency Injection)의 장점은?</strong></summary>

**모범 답안 포인트**:
- 느슨한 결합
- 테스트 용이성
- 코드 재사용성
- 유지보수 향상

</details>

<details>
<summary><strong>4. @Component, @Service, @Repository의 차이는?</strong></summary>

**모범 답안 포인트**:
- 모두 Bean 등록용
- 역할에 따른 구분
- 가독성과 AOP 적용

</details>

<details>
<summary><strong>5. 생성자 주입을 권장하는 이유는?</strong></summary>

**모범 답안 포인트**:
- 불변성 (final)
- NPE 방지
- 테스트 용이
- 순환 참조 즉시 발견

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. Spring Bean의 생명주기는?</strong></summary>

**모범 답안 포인트**:
- 인스턴스화
- 의존성 주입
- 초기화 콜백 (@PostConstruct)
- 사용
- 소멸 콜백 (@PreDestroy)

**예시 답변** (중급):
> "Spring Bean의 생명주기는 크게 5단계입니다. 첫째, ApplicationContext가 BeanDefinition을 읽어 Bean을 인스턴스화합니다. 둘째, Spring이 의존성을 주입합니다. 셋째, @PostConstruct나 InitializingBean의 afterPropertiesSet()으로 초기화 작업을 수행합니다. 넷째, Bean이 애플리케이션에서 사용됩니다. 마지막으로 ApplicationContext가 종료될 때 @PreDestroy나 DisposableBean의 destroy()로 정리 작업을 합니다. 실무에서는 DB Connection Pool 초기화나 파일 핸들 정리에 활용합니다."

</details>

<details>
<summary><strong>2. AOP의 핵심 개념 설명</strong></summary>

**모범 답안 포인트**:
- Aspect, Advice, Pointcut
- JoinPoint, Weaving
- 프록시 메커니즘

</details>

<details>
<summary><strong>3. Spring의 Bean Scope 종류는?</strong></summary>

**모범 답안 포인트**:
- Singleton (기본)
- Prototype
- Request, Session (Web)

</details>

---

## 💼 면접 질문 리스트 답안

### 📘 주니어/신입 개발자용 답안

#### Q1. Spring Framework란 무엇인가요?

**완벽한 답변 예시**:
```
"Spring Framework는 Java 기반의 엔터프라이즈 애플리케이션 개발을 위한
오픈소스 프레임워크입니다.

핵심 기능은 3가지입니다.

첫째, IoC Container입니다.
객체의 생성과 생명주기를 Spring이 관리하여,
개발자는 비즈니스 로직에만 집중할 수 있습니다.

둘째, DI(의존성 주입)입니다.
객체 간의 의존 관계를 Spring이 자동으로 연결해주어,
느슨한 결합과 테스트 용이성을 제공합니다.

셋째, AOP(관점 지향 프로그래밍)입니다.
로깅, 트랜잭션 같은 횡단 관심사를 분리하여,
코드 중복을 제거하고 유지보수성을 향상시킵니다.

실무에서는 Spring Boot와 함께 사용하여
REST API 서버, 웹 애플리케이션, 마이크로서비스 등을
빠르고 안정적으로 개발할 수 있습니다."
```

---

## 📝 핵심 정리

### 이 장에서 배운 핵심 개념

| 개념 | 설명 | 핵심 키워드 |
|------|------|-------------|
| Spring | Java 기반 프레임워크 | 엔터프라이즈, 오픈소스 |
| IoC | 제어의 역전 | Container, Bean |
| DI | 의존성 주입 | 생성자 주입, 느슨한 결합 |
| AOP | 관점 지향 프로그래밍 | 횡단 관심사, Aspect |
| PSA | 서비스 추상화 | 기술 독립, 호환성 |

---

### 필수 어노테이션 정리

| 어노테이션 | 용도 | 예시 |
|-----------|------|------|
| @SpringBootApplication | Spring Boot 시작점 | main 메서드 클래스 |
| @Component | 일반 Bean 등록 | 유틸리티 클래스 |
| @Service | 비즈니스 로직 Bean | Service 계층 |
| @Repository | 데이터 접근 Bean | Repository 계층 |
| @Controller | 웹 요청 처리 | MVC Controller |
| @RestController | REST API 처리 | REST API Controller |
| @Autowired | 의존성 주입 | 생성자, Setter |
| @Aspect | AOP Aspect | 로깅, 트랜잭션 |

---

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] 생성자 주입 사용 (final로 불변성)
- [ ] 역할에 맞는 어노테이션 (@Service, @Repository)
- [ ] Layered Architecture 준수
- [ ] 예외 처리 명확히
- [ ] 테스트 코드 작성
- [ ] 로깅 적절히

#### ❌ 하지 말아야 할 것
- [ ] 필드 주입 사용 (@Autowired on field)
- [ ] 순환 참조 만들기
- [ ] Controller에 비즈니스 로직
- [ ] Service에서 직접 DB 접근
- [ ] Bean 등록 없이 @Autowired
- [ ] 모든 클래스를 @Component로

---

## 🔗 관련 기술

**Spring과 함께 사용하는 기술들**

| 기술 | 관계 | 학습 우선순위 |
|------|------|---------------|
| Java | Spring의 기반 언어 | ⭐⭐⭐⭐⭐ |
| Maven/Gradle | 빌드 도구 | ⭐⭐⭐⭐⭐ |
| Lombok | 코드 간소화 | ⭐⭐⭐⭐ |
| JPA/Hibernate | ORM | ⭐⭐⭐⭐ |
| MySQL/PostgreSQL | 데이터베이스 | ⭐⭐⭐⭐ |

---

## 🚀 다음 단계

### 다음 장 미리보기: 02장 - 개발 환경 설정

이제 Spring이 무엇인지 이해했으니, 직접 개발 환경을 구축해봅시다!

**02장에서 배울 내용**:
- **JDK 설치**: Java 17 설치 및 설정
- **IDE 설치**: IntelliJ IDEA 또는 Eclipse
- **Spring Boot 프로젝트 생성**: Spring Initializr 사용
- **첫 번째 애플리케이션**: Hello World 실행

### 이 장과의 연결점

```
01장: Spring이란? (개념 이해)
    ↓
02장: 개발 환경 설정 (직접 설치)
    ↓
03장: IoC 컨테이너 (깊이 학습)
    ↓
최종 목표: Spring 마스터!
```

### 준비하면 좋을 것들

```bash
# 02장 학습 전 준비 사항

# 1. Java 17 다운로드 준비
# https://adoptium.net/

# 2. IDE 선택 (하나만)
# - IntelliJ IDEA Community (권장, 무료)
# - Eclipse IDE for Java EE

# 3. 브라우저
# - Chrome, Firefox, Edge 등

# 준비 완료! 02장으로 출발! 🚀
```

---

## 📚 추가 학습 자료

### 공식 문서
- [Spring Framework 공식 문서](https://spring.io/projects/spring-framework)
- [Spring Boot 공식 문서](https://spring.io/projects/spring-boot)
- [Spring Guides](https://spring.io/guides)

### 추천 블로그/아티클
- [백기선 - Spring 개념](https://www.youtube.com/@whiteship)
- [우아한형제들 기술 블로그](https://techblog.woowahan.com/)
- [토스 기술 블로그](https://toss.tech/)

### 영상 강의
- [김영한의 스프링 완전 정복 (인프런)](https://www.inflearn.com/)
- [백기선 스프링 프레임워크 핵심 기술](https://www.inflearn.com/)

---

## 🎉 축하합니다!

**01장 학습 완료!**

**이제 여러분은**:
✅ Spring이 무엇인지 이해했습니다
✅ IoC/DI/AOP/PSA 개념을 설명할 수 있습니다
✅ 실생활 비유로 Spring을 이해했습니다
✅ 간단한 Spring 애플리케이션을 만들 수 있습니다
✅ 면접 질문에 답변할 수 있습니다

**다음 단계**:
- [ ] 02장으로 진행 (개발 환경 설정)
- [ ] 실전 프로젝트 복습
- [ ] 면접 질문 암기

---

**다음 장으로 이동**: [다음: 02장 개발 환경 설정 →](02-1-개발-환경-설정-Part1.md)

**이전 장으로 돌아가기**: [← 이전: 00장 Spring 학습 로드맵](00-1-Spring-학습-로드맵-Part1.md)

**목차로 돌아가기**: [📚 전체 목차](README.md)

---

**💪 Spring 여정의 첫 걸음을 완주했습니다!**

```
     01장 완료! ✅
         ↓
   개념을 이해했다
         ↓
  이제 직접 만들 차례
         ↓
    02장에서 계속!
```
