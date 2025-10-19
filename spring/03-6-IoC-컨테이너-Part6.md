# 03장: IoC 컨테이너 - Part 6 (프로젝트 테스트 & 확장)

**[← 이전: Part 5](03-5-IoC-컨테이너-Part5.md)** | **[다음: Part 7 →](03-7-IoC-컨테이너-Part7.md)**

---

## 🛠️ 실전 프로젝트 (계속)

### 단계별 구현 가이드 (계속)

#### 7단계: 단위 테스트 작성

```java
// 파일: src/test/java/com/example/library/service/LoanServiceTest.java
package com.example.library.service;

import com.example.library.domain.Book;
import com.example.library.domain.Loan;
import com.example.library.repository.BookRepository;
import com.example.library.repository.LoanRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@SpringBootTest
class LoanServiceTest {

    @Autowired
    private LoanService loanService;

    // Mock Bean 주입 (가짜 객체)
    @MockBean
    private BookRepository bookRepository;

    @MockBean
    private LoanRepository loanRepository;

    @MockBean
    private NotificationService notificationService;

    @BeforeEach
    void setUp() {
        // 각 테스트 전에 Mock 객체 초기화
        reset(bookRepository, loanRepository, notificationService);
    }

    @Test
    void 도서_대출_성공() {
        // Given: 테스트 데이터 준비
        Long memberId = 1L;
        Long bookId = 1L;

        Book book = new Book(bookId, "Clean Code", "Robert Martin", "123", true);

        // Mock 객체의 동작 정의
        when(bookRepository.findById(bookId)).thenReturn(Optional.of(book));
        when(loanRepository.save(any(Loan.class))).thenAnswer(invocation -> {
            Loan loan = invocation.getArgument(0);
            loan.setId(1L);
            return loan;
        });

        // When: 실제 테스트 실행
        Loan result = loanService.loanBook(memberId, bookId);

        // Then: 결과 검증
        assertNotNull(result);
        assertEquals(bookId, result.getBookId());
        assertEquals(memberId, result.getMemberId());
        assertFalse(result.isReturned());

        // Mock 객체 호출 검증
        verify(bookRepository, times(1)).findById(bookId);
        verify(bookRepository, times(1)).save(any(Book.class));
        verify(loanRepository, times(1)).save(any(Loan.class));
        verify(notificationService, times(1))
                .sendLoanNotification(memberId, "Clean Code");
    }

    @Test
    void 도서_대출_실패_이미_대출된_도서() {
        // Given
        Long memberId = 1L;
        Long bookId = 1L;

        // 이미 대출된 도서
        Book book = new Book(bookId, "Clean Code", "Robert Martin", "123", false);

        when(bookRepository.findById(bookId)).thenReturn(Optional.of(book));

        // When & Then: 예외 발생 검증
        IllegalStateException exception = assertThrows(
                IllegalStateException.class,
                () -> loanService.loanBook(memberId, bookId)
        );

        assertEquals("Book is not available", exception.getMessage());

        // 대출 기록 저장이 호출되지 않았는지 확인
        verify(loanRepository, never()).save(any(Loan.class));
        verify(notificationService, never()).sendLoanNotification(anyLong(), anyString());
    }

    @Test
    void 도서_대출_실패_존재하지_않는_도서() {
        // Given
        Long memberId = 1L;
        Long bookId = 999L;

        when(bookRepository.findById(bookId)).thenReturn(Optional.empty());

        // When & Then
        IllegalArgumentException exception = assertThrows(
                IllegalArgumentException.class,
                () -> loanService.loanBook(memberId, bookId)
        );

        assertEquals("Book not found", exception.getMessage());
    }

    @Test
    void 도서_반납_성공() {
        // Given
        Long loanId = 1L;
        Long bookId = 1L;
        Long memberId = 1L;

        Loan loan = new Loan(loanId, bookId, memberId, null, null, false);
        Book book = new Book(bookId, "Clean Code", "Robert Martin", "123", false);

        when(loanRepository.findById(loanId)).thenReturn(Optional.of(loan));
        when(bookRepository.findById(bookId)).thenReturn(Optional.of(book));
        when(loanRepository.save(any(Loan.class))).thenReturn(loan);

        // When
        Loan result = loanService.returnBook(loanId);

        // Then
        assertTrue(result.isReturned());
        assertNotNull(result.getReturnDate());

        verify(bookRepository, times(1)).save(argThat(b -> b.isAvailable()));
        verify(notificationService, times(1))
                .sendReturnNotification(memberId, "Clean Code");
    }
}
```

**실행**:
```bash
./mvnw test
```

**예상 출력**:
```
[INFO] Tests run: 4, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

**코드 설명**:
- **@SpringBootTest**: Spring IoC 컨테이너를 테스트에서 사용
- **@MockBean**: 실제 Bean 대신 Mock 객체 주입
- **when().thenReturn()**: Mock 객체의 동작 정의
- **verify()**: Mock 객체의 메서드 호출 여부 검증

---

### 확장 아이디어

#### 추가 기능 1: 이메일 알림 구현

**난이도**: ⭐⭐⭐⭐☆

**구현 힌트**:
```java
// 파일: src/main/java/com/example/library/service/EmailNotificationService.java
package com.example.library.service;

import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Service;

@Service
@Profile("prod")  // 프로덕션 환경에서만 사용
public class EmailNotificationService implements NotificationService {

    @Override
    public void sendLoanNotification(Long memberId, String bookTitle) {
        // 실제 이메일 발송 로직
        String email = getMemberEmail(memberId);
        sendEmail(email, "도서 대출 안내", "\"" + bookTitle + "\" 대출 완료!");
    }

    @Override
    public void sendReturnNotification(Long memberId, String bookTitle) {
        String email = getMemberEmail(memberId);
        sendEmail(email, "도서 반납 완료", "\"" + bookTitle + "\" 반납 완료!");
    }

    private String getMemberEmail(Long memberId) {
        // 회원 이메일 조회
        return "member" + memberId + "@example.com";
    }

    private void sendEmail(String to, String subject, String body) {
        // JavaMail 또는 SendGrid API 사용
        System.out.println("📧 이메일 발송: " + to);
        System.out.println("   제목: " + subject);
        System.out.println("   내용: " + body);
    }
}

// application.properties
// spring.profiles.active=dev  → ConsoleNotificationService 사용
// spring.profiles.active=prod → EmailNotificationService 사용
```

---

#### 추가 기능 2: 연체 관리 기능

**난이도**: ⭐⭐⭐⭐⭐

**구현 힌트**:
```java
// 파일: src/main/java/com/example/library/service/OverdueService.java
package com.example.library.service;

import com.example.library.domain.Loan;
import com.example.library.repository.LoanRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;

@Service
public class OverdueService {

    private static final int LOAN_PERIOD_DAYS = 14;  // 대출 기간 14일

    private final LoanRepository loanRepository;
    private final NotificationService notificationService;

    @Autowired
    public OverdueService(LoanRepository loanRepository,
                          NotificationService notificationService) {
        this.loanRepository = loanRepository;
        this.notificationService = notificationService;
    }

    // 매일 자정에 연체 확인 (스케줄링)
    @Scheduled(cron = "0 0 0 * * *")
    public void checkOverdueLoans() {
        List<Loan> activeLoans = loanRepository.findActiveLoans();

        for (Loan loan : activeLoans) {
            long daysSinceLoan = ChronoUnit.DAYS.between(
                    loan.getLoanDate(),
                    LocalDateTime.now()
            );

            if (daysSinceLoan > LOAN_PERIOD_DAYS) {
                // 연체된 대출
                long overdueDays = daysSinceLoan - LOAN_PERIOD_DAYS;
                System.out.println("⚠️ 연체 도서 발견: 대출ID " + loan.getId()
                        + ", " + overdueDays + "일 연체");

                // 알림 발송
                // notificationService.sendOverdueNotification(loan);
            }
        }
    }

    public int calculateFine(Long loanId) {
        Loan loan = loanRepository.findById(loanId)
                .orElseThrow(() -> new IllegalArgumentException("Loan not found"));

        long daysSinceLoan = ChronoUnit.DAYS.between(
                loan.getLoanDate(),
                loan.isReturned() ? loan.getReturnDate() : LocalDateTime.now()
        );

        if (daysSinceLoan <= LOAN_PERIOD_DAYS) {
            return 0;  // 연체 아님
        }

        long overdueDays = daysSinceLoan - LOAN_PERIOD_DAYS;
        return (int) (overdueDays * 100);  // 1일당 100원
    }
}
```

---

#### 추가 기능 3: 도서 예약 기능

**난이도**: ⭐⭐⭐⭐☆

**구현 힌트**:
```java
// 새 도메인 객체
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Reservation {
    private Long id;
    private Long bookId;
    private Long memberId;
    private LocalDateTime reservationDate;
    private boolean fulfilled;
}

// 새 Repository
public interface ReservationRepository {
    Reservation save(Reservation reservation);
    List<Reservation> findByBookId(Long bookId);
    List<Reservation> findByMemberId(Long memberId);
}

// 예약 서비스
@Service
public class ReservationService {
    @Autowired BookRepository bookRepository;
    @Autowired ReservationRepository reservationRepository;
    @Autowired NotificationService notificationService;

    public Reservation reserveBook(Long memberId, Long bookId) {
        Book book = bookRepository.findById(bookId)
                .orElseThrow(() -> new IllegalArgumentException("Book not found"));

        if (book.isAvailable()) {
            throw new IllegalStateException("Book is available, please loan directly");
        }

        Reservation reservation = new Reservation(
                null, bookId, memberId, LocalDateTime.now(), false
        );
        return reservationRepository.save(reservation);
    }

    // 반납 시 자동으로 다음 예약자에게 알림
    public void notifyNextReserver(Long bookId) {
        List<Reservation> reservations = reservationRepository.findByBookId(bookId);

        reservations.stream()
                .filter(r -> !r.isFulfilled())
                .min((r1, r2) -> r1.getReservationDate().compareTo(r2.getReservationDate()))
                .ifPresent(next -> {
                    notificationService.sendLoanNotification(
                            next.getMemberId(),
                            "예약하신 도서가 대출 가능합니다!"
                    );
                });
    }
}
```

---

### 트러블슈팅

#### 문제 1: Bean을 찾을 수 없음

**증상**:
```
***************************
APPLICATION FAILED TO START
***************************

Description:

Field bookRepository in com.example.library.service.BookService
required a bean of type 'com.example.library.repository.BookRepository'
that could not be found.
```

**원인**: Repository 구현체에 `@Repository` 어노테이션 누락

**해결 방법**:
```java
// MemoryBookRepository에 @Repository 추가
@Repository  // ← 이것 추가!
public class MemoryBookRepository implements BookRepository {
    // ...
}
```

---

#### 문제 2: 순환 참조 발생

**증상**:
```
The dependencies of some of the beans in the application context form a cycle:

┌─────┐
|  bookService (field private BookRepository)
↑     ↓
|  loanService (field private BookService)
└─────┘
```

**원인**: 서로를 의존하는 설계

**해결 방법**:
```java
// 방법 1: @Lazy 사용
@Service
public class BookService {
    @Autowired
    @Lazy
    private LoanService loanService;
}

// 방법 2: 리팩토링 (권장)
// 공통 로직을 새 서비스로 분리
```

---

#### 문제 3: NullPointerException 발생

**증상**:
```java
java.lang.NullPointerException: Cannot invoke "BookRepository.findById()"
```

**원인**: `@Autowired`가 동작하지 않음 (new로 직접 생성한 경우)

**해결 방법**:
```java
// ❌ 잘못된 코드
BookService service = new BookService();  // Spring Bean 아님!
service.findBook(1L);  // NPE 발생

// ✅ 올바른 코드
@RestController
public class MyController {
    @Autowired
    private BookService service;  // Spring이 주입

    public void doSomething() {
        service.findBook(1L);  // 정상 동작
    }
}
```

---

### 코드 리뷰 포인트

#### 체크리스트

- [ ] **변수명이 의미 있는가?**
  - ✅ `bookRepository` (명확)
  - ❌ `br` (불명확)

- [ ] **생성자 주입을 사용하는가?**
  - ✅ `public LoanService(BookRepository repo) { }`
  - ❌ `@Autowired private BookRepository repo;` (필드 주입)

- [ ] **인터페이스 기반 설계인가?**
  - ✅ `BookRepository` 인터페이스 → 구현체 교체 가능
  - ❌ `MemoryBookRepository` 직접 의존 → 교체 어려움

- [ ] **예외 처리가 적절한가?**
  - ✅ `orElseThrow(() -> new IllegalArgumentException(...))`
  - ❌ `get()` 직접 호출 (NoSuchElementException)

- [ ] **트랜잭션이 필요한가?**
  - ✅ 대출 시 도서 상태 변경 + 대출 기록 생성 → `@Transactional`
  - (현재는 메모리 저장소라 불필요, DB 사용 시 필수)

- [ ] **테스트 커버리지가 충분한가?**
  - ✅ 정상 케이스 + 예외 케이스 모두 테스트
  - ❌ 정상 케이스만 테스트

- [ ] **보안 취약점은 없는가?**
  - ✅ 입력 검증 (`Optional.orElseThrow`)
  - ❌ 검증 없이 바로 사용

---

### 전체 소스 코드 정리

**프로젝트 구조 요약**:
```
library-management/
├── domain/           # 도메인 객체 (Book, Member, Loan)
├── repository/       # 데이터 접근 계층 (인터페이스 + 구현)
├── service/          # 비즈니스 로직 (BookService, LoanService 등)
├── controller/       # REST API (LibraryController)
└── config/           # 설정 (필요 시)
```

**IoC 컨테이너 활용 포인트**:
1. **자동 Bean 등록**: `@Service`, `@Repository`
2. **의존성 주입**: 생성자 주입으로 느슨한 결합
3. **인터페이스 기반**: 구현체 교체 용이
4. **테스트 용이**: `@MockBean`으로 쉽게 테스트

---

### 학습 성과

이 프로젝트를 완료하면:
- ✅ IoC 컨테이너의 동작 원리 이해
- ✅ Component Scan과 Bean 등록 방식 숙지
- ✅ 생성자 주입의 장점 체득
- ✅ 계층 분리와 인터페이스 설계 경험
- ✅ Spring Boot 애플리케이션 개발 능력

---

**[← 이전: Part 5](03-5-IoC-컨테이너-Part5.md)** | **[다음: Part 7 →](03-7-IoC-컨테이너-Part7.md)**
