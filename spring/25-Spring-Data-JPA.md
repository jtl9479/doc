# 25장: Spring Data JPA - Repository로 더 간편하게

> **"인터페이스만 정의하면 구현체는 Spring이 자동으로 만들어줍니다"**

---

## 📋 학습 목표

이 장을 학습하면 다음을 할 수 있습니다:

- Spring Data JPA의 개념과 장점을 이해합니다
- JpaRepository를 활용하여 CRUD를 간편하게 구현합니다
- 메서드 이름으로 쿼리를 자동 생성할 수 있습니다
- @Query를 사용하여 커스텀 쿼리를 작성합니다
- 페이징과 정렬을 효과적으로 처리합니다
- Auditing으로 생성/수정 시간을 자동 관리합니다

**예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐ (초중급)

---

## 🤔 왜 Spring Data JPA가 필요한가?

### 문제 상황: 반복되는 Repository 코드

```java
// JPA만 사용 - 모든 엔티티마다 반복
@Repository
public class UserRepository {
    @PersistenceContext
    private EntityManager em;

    public User save(User user) {
        em.persist(user);
        return user;
    }

    public User findById(Long id) {
        return em.find(User.class, id);
    }

    public List<User> findAll() {
        return em.createQuery("SELECT u FROM User u", User.class)
                 .getResultList();
    }

    public void delete(User user) {
        em.remove(user);
    }
    // 매번 동일한 패턴의 코드 작성...
}

// Product, Order, Comment... 모든 엔티티마다 동일한 코드 반복!
```

**개발자의 고민:**
- "CRUD는 어차피 비슷한데 매번 작성해야 하나요?"
- "findByName, findByEmail... 이런 간단한 조회도 JPQL을 작성해야 하나요?"
- "페이징 처리를 더 쉽게 할 수 없나요?"

### Spring Data JPA의 해결책

```java
// Spring Data JPA - 인터페이스만 정의
public interface UserRepository extends JpaRepository<User, Long> {
    // 구현체는 Spring이 자동 생성!

    // 메서드 이름만으로 쿼리 자동 생성
    List<User> findByName(String name);
    List<User> findByEmailAndStatus(String email, UserStatus status);
    List<User> findByCreatedAtAfter(LocalDateTime date);

    // 페이징도 간단히
    Page<User> findByStatus(UserStatus status, Pageable pageable);
}

// 사용
@Service
public class UserService {
    private final UserRepository userRepository;

    public List<User> getActiveUsers() {
        return userRepository.findByStatus(UserStatus.ACTIVE);
    }
}
```

**Spring Data JPA의 핵심 가치:**
- 보일러플레이트 코드 제거 → 생산성 대폭 향상
- 메서드 이름 기반 쿼리 생성 → 직관적이고 안전
- 페이징, 정렬 기본 제공 → 반복 작업 최소화

---

## 🌍 실생활 비유로 이해하는 Spring Data JPA

### 비유 1: 자판기 vs 맞춤 주문

**JPA EntityManager (맞춤 주문):**
```
점원에게 직접 주문:
"저기요, 아메리카노 한 잔 주세요. 얼음은 적게, 샷은 2개로..."
→ 모든 것을 상세히 지시해야 함
```

**Spring Data JPA (자판기):**
```
버튼만 누르면 됨:
[아메리카노] 버튼 클릭 → 자동으로 만들어짐
[카페라떼] 버튼 클릭 → 자동으로 만들어짐
→ 간단한 선택만으로 결과 획득
```

**코드로 표현:**
```java
// EntityManager (상세한 지시)
public User findByEmail(String email) {
    return em.createQuery(
        "SELECT u FROM User u WHERE u.email = :email", User.class)
        .setParameter("email", email)
        .getSingleResult();
}

// Spring Data JPA (간단한 선택)
User findByEmail(String email);  // 끝!
```

### 비유 2: 백과사전 vs 검색 엔진

**전통적 방식 (백과사전):**
```
1. 책장에서 올바른 책 찾기
2. 색인에서 키워드 찾기
3. 페이지 번호 확인
4. 해당 페이지로 이동
5. 내용 읽기
→ 복잡한 과정
```

**Spring Data JPA (검색 엔진):**
```
검색창에 "김철수" 입력 → Enter
→ 즉시 결과 제공
```

```java
// 백과사전 방식
public List<User> searchUsers(String keyword) {
    return em.createQuery(
        "SELECT u FROM User u WHERE u.name LIKE :keyword", User.class)
        .setParameter("keyword", "%" + keyword + "%")
        .getResultList();
}

// 검색 엔진 방식
List<User> findByNameContaining(String keyword);
```

### 비유 3: 수동 vs 자동 세탁기

**수동 세탁기 (JPA EntityManager):**
```
1. 물 온도 설정
2. 세제 투입량 계산
3. 세탁 시간 설정
4. 헹굼 횟수 지정
5. 탈수 강도 조절
→ 모든 것을 직접 제어
```

**자동 세탁기 (Spring Data JPA):**
```
[표준 세탁] 버튼 클릭
→ 알아서 최적의 설정으로 세탁
```

```java
// 수동 (모든 것을 직접)
@Repository
public class UserRepository {
    @PersistenceContext
    private EntityManager em;

    public User save(User user) { ... }
    public User findById(Long id) { ... }
    public List<User> findAll() { ... }
    // 100줄 이상의 반복 코드
}

// 자동 (인터페이스만 정의)
public interface UserRepository extends JpaRepository<User, Long> {
    // save, findById, findAll 자동 제공!
}
```

---

## 💡 Spring Data JPA 핵심 개념

### 1️⃣ 초급: JpaRepository 계층 구조

```
Repository<T, ID>
    ↑
CrudRepository<T, ID>
    ↑
PagingAndSortingRepository<T, ID>
    ↑
JpaRepository<T, ID>  ← 가장 많이 사용
```

**각 인터페이스의 역할:**

```java
// 1. CrudRepository - 기본 CRUD
public interface CrudRepository<T, ID> {
    <S extends T> S save(S entity);
    Optional<T> findById(ID id);
    Iterable<T> findAll();
    void deleteById(ID id);
    long count();
    boolean existsById(ID id);
}

// 2. PagingAndSortingRepository - 페이징과 정렬
public interface PagingAndSortingRepository<T, ID> extends CrudRepository<T, ID> {
    Iterable<T> findAll(Sort sort);
    Page<T> findAll(Pageable pageable);
}

// 3. JpaRepository - JPA 특화 기능
public interface JpaRepository<T, ID> extends PagingAndSortingRepository<T, ID> {
    List<T> findAll();
    List<T> findAllById(Iterable<ID> ids);
    <S extends T> List<S> saveAll(Iterable<S> entities);
    void flush();
    <S extends T> S saveAndFlush(S entity);
    void deleteInBatch(Iterable<T> entities);
}
```

**실무에서는 JpaRepository를 주로 사용:**

```java
public interface UserRepository extends JpaRepository<User, Long> {
    // 기본 메서드 모두 제공:
    // save, findById, findAll, delete, count 등
}

// 사용 예시
@Service
public class UserService {
    private final UserRepository userRepository;

    public void example() {
        // 저장
        User user = new User("홍길동");
        userRepository.save(user);

        // 조회
        Optional<User> found = userRepository.findById(1L);

        // 전체 조회
        List<User> allUsers = userRepository.findAll();

        // 개수
        long count = userRepository.count();

        // 존재 확인
        boolean exists = userRepository.existsById(1L);

        // 삭제
        userRepository.deleteById(1L);
    }
}
```

### 2️⃣ 중급: 쿼리 메서드 (Query Methods)

#### 메서드 이름으로 쿼리 자동 생성

Spring Data JPA는 메서드 이름을 분석하여 JPQL을 자동 생성합니다.

**기본 구조:**
```
find + (주체) + By + (조건) + (정렬/제한)
```

**주요 키워드:**

| 키워드 | 예시 | 생성되는 JPQL |
|-------|------|--------------|
| `findBy` | `findByName(String name)` | `WHERE name = ?1` |
| `And` | `findByNameAndEmail(...)` | `WHERE name = ?1 AND email = ?2` |
| `Or` | `findByNameOrEmail(...)` | `WHERE name = ?1 OR email = ?2` |
| `Between` | `findByAgeBetween(int start, int end)` | `WHERE age BETWEEN ?1 AND ?2` |
| `LessThan` | `findByAgeLessThan(int age)` | `WHERE age < ?1` |
| `GreaterThan` | `findByAgeGreaterThan(int age)` | `WHERE age > ?1` |
| `Like` | `findByNameLike(String name)` | `WHERE name LIKE ?1` |
| `Containing` | `findByNameContaining(String name)` | `WHERE name LIKE '%?1%'` |
| `StartingWith` | `findByNameStartingWith(String prefix)` | `WHERE name LIKE '?1%'` |
| `EndingWith` | `findByNameEndingWith(String suffix)` | `WHERE name LIKE '%?1'` |
| `In` | `findByIdIn(List<Long> ids)` | `WHERE id IN (?1)` |
| `NotNull` | `findByEmailNotNull()` | `WHERE email IS NOT NULL` |
| `OrderBy` | `findByNameOrderByAgeDesc(String name)` | `WHERE name = ?1 ORDER BY age DESC` |

**실전 예시:**

```java
public interface UserRepository extends JpaRepository<User, Long> {

    // 1. 단일 조건
    List<User> findByName(String name);
    // SELECT u FROM User u WHERE u.name = ?1

    // 2. 여러 조건 (AND)
    List<User> findByNameAndEmail(String name, String email);
    // SELECT u FROM User u WHERE u.name = ?1 AND u.email = ?2

    // 3. 여러 조건 (OR)
    List<User> findByNameOrEmail(String name, String email);
    // SELECT u FROM User u WHERE u.name = ?1 OR u.email = ?2

    // 4. 비교 연산
    List<User> findByAgeGreaterThan(int age);
    // SELECT u FROM User u WHERE u.age > ?1

    List<User> findByAgeBetween(int start, int end);
    // SELECT u FROM User u WHERE u.age BETWEEN ?1 AND ?2

    // 5. LIKE 검색
    List<User> findByNameContaining(String keyword);
    // SELECT u FROM User u WHERE u.name LIKE '%?1%'

    List<User> findByNameStartingWith(String prefix);
    // SELECT u FROM User u WHERE u.name LIKE '?1%'

    // 6. IN 절
    List<User> findByIdIn(List<Long> ids);
    // SELECT u FROM User u WHERE u.id IN (?1)

    // 7. NULL 체크
    List<User> findByEmailNotNull();
    // SELECT u FROM User u WHERE u.email IS NOT NULL

    // 8. 정렬
    List<User> findByStatusOrderByCreatedAtDesc(UserStatus status);
    // SELECT u FROM User u WHERE u.status = ?1 ORDER BY u.createdAt DESC

    // 9. Top/First (결과 제한)
    List<User> findTop5ByStatus(UserStatus status);
    User findFirstByOrderByCreatedAtDesc();

    // 10. 존재 확인
    boolean existsByEmail(String email);
    // SELECT COUNT(u) FROM User u WHERE u.email = ?1

    // 11. 카운트
    long countByStatus(UserStatus status);
    // SELECT COUNT(u) FROM User u WHERE u.status = ?1

    // 12. 삭제
    void deleteByStatus(UserStatus status);
    // DELETE FROM User u WHERE u.status = ?1
}
```

#### 반환 타입

```java
public interface UserRepository extends JpaRepository<User, Long> {

    // 1. 단일 엔티티
    User findByEmail(String email);  // 없으면 null

    // 2. Optional (권장)
    Optional<User> findByEmail(String email);  // 없으면 Optional.empty()

    // 3. List
    List<User> findByName(String name);

    // 4. Stream (대용량 처리)
    Stream<User> findByStatus(UserStatus status);

    // 5. Page (페이징)
    Page<User> findByStatus(UserStatus status, Pageable pageable);

    // 6. Slice (더보기 방식)
    Slice<User> findByStatus(UserStatus status, Pageable pageable);

    // 7. 카운트
    long countByStatus(UserStatus status);

    // 8. 존재 여부
    boolean existsByEmail(String email);
}
```

### 3️⃣ 고급: @Query 애노테이션

복잡한 쿼리는 `@Query`로 직접 작성할 수 있습니다.

#### JPQL 쿼리

```java
public interface UserRepository extends JpaRepository<User, Long> {

    // 1. 기본 JPQL
    @Query("SELECT u FROM User u WHERE u.name = :name")
    List<User> findByNameCustom(@Param("name") String name);

    // 2. 여러 조건
    @Query("SELECT u FROM User u WHERE u.name = :name AND u.status = :status")
    List<User> findByNameAndStatus(
        @Param("name") String name,
        @Param("status") UserStatus status
    );

    // 3. LIKE 검색
    @Query("SELECT u FROM User u WHERE u.name LIKE %:keyword% OR u.email LIKE %:keyword%")
    List<User> searchUsers(@Param("keyword") String keyword);

    // 4. JOIN 쿼리
    @Query("SELECT u FROM User u JOIN FETCH u.orders WHERE u.id = :id")
    Optional<User> findByIdWithOrders(@Param("id") Long id);

    // 5. 집계 쿼리
    @Query("SELECT COUNT(u) FROM User u WHERE u.createdAt >= :date")
    long countNewUsers(@Param("date") LocalDateTime date);

    // 6. DTO 프로젝션
    @Query("SELECT new com.example.dto.UserDto(u.id, u.name, u.email) " +
           "FROM User u WHERE u.status = :status")
    List<UserDto> findUserDtos(@Param("status") UserStatus status);

    // 7. 정렬 (Sort 파라미터)
    @Query("SELECT u FROM User u WHERE u.status = :status")
    List<User> findByStatus(@Param("status") UserStatus status, Sort sort);

    // 8. 페이징
    @Query("SELECT u FROM User u WHERE u.status = :status")
    Page<User> findByStatus(@Param("status") UserStatus status, Pageable pageable);
}
```

#### Native Query

```java
public interface UserRepository extends JpaRepository<User, Long> {

    // 1. 기본 Native Query
    @Query(value = "SELECT * FROM users WHERE name = :name", nativeQuery = true)
    List<User> findByNameNative(@Param("name") String name);

    // 2. 복잡한 통계 쿼리
    @Query(value = """
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM users
        WHERE created_at >= :startDate
        GROUP BY DATE(created_at)
        ORDER BY date DESC
        """, nativeQuery = true)
    List<Object[]> getDailyUserStats(@Param("startDate") LocalDateTime startDate);

    // 3. 페이징 (Native Query)
    @Query(value = "SELECT * FROM users WHERE status = :status",
           countQuery = "SELECT COUNT(*) FROM users WHERE status = :status",
           nativeQuery = true)
    Page<User> findByStatusNative(@Param("status") String status, Pageable pageable);
}
```

#### 수정 쿼리 (@Modifying)

```java
public interface UserRepository extends JpaRepository<User, Long> {

    // 1. UPDATE
    @Modifying
    @Query("UPDATE User u SET u.status = :status WHERE u.id = :id")
    int updateStatus(@Param("id") Long id, @Param("status") UserStatus status);

    // 2. 벌크 UPDATE
    @Modifying
    @Query("UPDATE User u SET u.status = :newStatus WHERE u.status = :oldStatus")
    int bulkUpdateStatus(
        @Param("oldStatus") UserStatus oldStatus,
        @Param("newStatus") UserStatus newStatus
    );

    // 3. DELETE
    @Modifying
    @Query("DELETE FROM User u WHERE u.status = :status")
    int deleteByStatus(@Param("status") UserStatus status);

    // 4. Native UPDATE
    @Modifying
    @Query(value = "UPDATE users SET login_count = login_count + 1 WHERE id = :id",
           nativeQuery = true)
    int increaseLoginCount(@Param("id") Long id);
}

// 사용 시 주의사항
@Service
public class UserService {
    private final UserRepository userRepository;

    @Transactional
    public void updateUserStatus(Long id, UserStatus status) {
        userRepository.updateStatus(id, status);
        // 영속성 컨텍스트를 수동으로 clear 해야 할 수 있음
        entityManager.clear();
    }
}
```

---

## 🛠️ 기본 실습

### 실습 1: Repository 인터페이스 작성

#### Step 1: 기본 Repository

```java
package com.example.demo.repository;

import com.example.demo.entity.User;
import com.example.demo.entity.UserStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    // 1. 이메일로 조회
    Optional<User> findByEmail(String email);

    // 2. 이름으로 조회
    List<User> findByName(String name);

    // 3. 상태로 조회
    List<User> findByStatus(UserStatus status);

    // 4. 이름과 상태로 조회
    List<User> findByNameAndStatus(String name, UserStatus status);

    // 5. 이름 또는 이메일로 조회
    List<User> findByNameOrEmail(String name, String email);

    // 6. 이름 포함 검색
    List<User> findByNameContaining(String keyword);

    // 7. 생성일 이후 조회
    List<User> findByCreatedAtAfter(LocalDateTime date);

    // 8. 상태별 정렬 조회
    List<User> findByStatusOrderByCreatedAtDesc(UserStatus status);

    // 9. 상위 N개 조회
    List<User> findTop5ByStatusOrderByCreatedAtDesc(UserStatus status);

    // 10. 이메일 존재 확인
    boolean existsByEmail(String email);

    // 11. 상태별 카운트
    long countByStatus(UserStatus status);
}
```

#### Step 2: 테스트

```java
@SpringBootTest
@Transactional
class UserRepositoryTest {

    @Autowired
    private UserRepository userRepository;

    @BeforeEach
    void setUp() {
        // 테스트 데이터 준비
        userRepository.saveAll(List.of(
            User.builder().name("홍길동").email("hong@example.com")
                .status(UserStatus.ACTIVE).build(),
            User.builder().name("김철수").email("kim@example.com")
                .status(UserStatus.ACTIVE).build(),
            User.builder().name("이영희").email("lee@example.com")
                .status(UserStatus.INACTIVE).build()
        ));
    }

    @Test
    void 이메일로_조회() {
        // When
        Optional<User> user = userRepository.findByEmail("hong@example.com");

        // Then
        assertThat(user).isPresent();
        assertThat(user.get().getName()).isEqualTo("홍길동");
    }

    @Test
    void 상태로_조회() {
        // When
        List<User> activeUsers = userRepository.findByStatus(UserStatus.ACTIVE);

        // Then
        assertThat(activeUsers).hasSize(2);
    }

    @Test
    void 이름_포함_검색() {
        // When
        List<User> users = userRepository.findByNameContaining("철");

        // Then
        assertThat(users).hasSize(1);
        assertThat(users.get(0).getName()).isEqualTo("김철수");
    }

    @Test
    void 이메일_존재_확인() {
        // When
        boolean exists = userRepository.existsByEmail("hong@example.com");
        boolean notExists = userRepository.existsByEmail("notexist@example.com");

        // Then
        assertThat(exists).isTrue();
        assertThat(notExists).isFalse();
    }

    @Test
    void 상태별_카운트() {
        // When
        long activeCount = userRepository.countByStatus(UserStatus.ACTIVE);

        // Then
        assertThat(activeCount).isEqualTo(2);
    }
}
```

---

### 실습 2: 페이징과 정렬

#### Step 1: 페이징 Repository

```java
public interface UserRepository extends JpaRepository<User, Long> {

    // 페이징
    Page<User> findByStatus(UserStatus status, Pageable pageable);

    // Slice (더보기 방식)
    Slice<User> findByNameContaining(String keyword, Pageable pageable);
}
```

#### Step 2: Service에서 사용

```java
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;

    // 페이징 조회
    public Page<User> getUsers(int page, int size) {
        // 페이지는 0부터 시작
        Pageable pageable = PageRequest.of(page, size);
        return userRepository.findAll(pageable);
    }

    // 정렬 + 페이징
    public Page<User> getUsersSorted(int page, int size, String sortBy) {
        Pageable pageable = PageRequest.of(page, size, Sort.by(sortBy).descending());
        return userRepository.findAll(pageable);
    }

    // 복잡한 정렬
    public Page<User> getUsersComplexSort(int page, int size) {
        Sort sort = Sort.by(
            Sort.Order.desc("status"),
            Sort.Order.asc("name")
        );
        Pageable pageable = PageRequest.of(page, size, sort);
        return userRepository.findAll(pageable);
    }

    // 상태별 페이징
    public Page<User> getActiveUsers(int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        return userRepository.findByStatus(UserStatus.ACTIVE, pageable);
    }
}
```

#### Step 3: Controller

```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping
    public ResponseEntity<PageResponse<User>> getUsers(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String sortBy) {

        Page<User> userPage;
        if (sortBy != null) {
            userPage = userService.getUsersSorted(page, size, sortBy);
        } else {
            userPage = userService.getUsers(page, size);
        }

        PageResponse<User> response = new PageResponse<>(
            userPage.getContent(),
            userPage.getNumber(),
            userPage.getSize(),
            userPage.getTotalElements(),
            userPage.getTotalPages(),
            userPage.isLast()
        );

        return ResponseEntity.ok(response);
    }
}

// Response DTO
@Data
@AllArgsConstructor
class PageResponse<T> {
    private List<T> content;
    private int page;
    private int size;
    private long totalElements;
    private int totalPages;
    private boolean last;
}
```

#### Step 4: 페이징 테스트

```java
@SpringBootTest
@Transactional
class UserPagingTest {

    @Autowired
    private UserRepository userRepository;

    @BeforeEach
    void setUp() {
        // 30개 데이터 생성
        for (int i = 1; i <= 30; i++) {
            userRepository.save(
                User.builder()
                    .name("User" + i)
                    .email("user" + i + "@example.com")
                    .status(UserStatus.ACTIVE)
                    .build()
            );
        }
    }

    @Test
    void 페이징_조회() {
        // Given
        Pageable pageable = PageRequest.of(0, 10);  // 첫 페이지, 10개씩

        // When
        Page<User> page = userRepository.findAll(pageable);

        // Then
        assertThat(page.getContent()).hasSize(10);
        assertThat(page.getTotalElements()).isEqualTo(30);
        assertThat(page.getTotalPages()).isEqualTo(3);
        assertThat(page.getNumber()).isEqualTo(0);  // 현재 페이지
        assertThat(page.isFirst()).isTrue();
        assertThat(page.isLast()).isFalse();
        assertThat(page.hasNext()).isTrue();
    }

    @Test
    void 정렬_페이징() {
        // Given
        Pageable pageable = PageRequest.of(0, 10, Sort.by("name").descending());

        // When
        Page<User> page = userRepository.findAll(pageable);

        // Then
        assertThat(page.getContent().get(0).getName()).isEqualTo("User9");
    }
}
```

---

### 실습 3: Auditing (생성/수정 시간 자동 관리)

#### Step 1: Auditing 활성화

```java
@SpringBootApplication
@EnableJpaAuditing  // Auditing 활성화
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

#### Step 2: BaseEntity 작성

```java
package com.example.demo.entity;

import jakarta.persistence.*;
import lombok.Getter;
import org.springframework.data.annotation.CreatedBy;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedBy;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
@Getter
public abstract class BaseEntity {

    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;

    @CreatedBy
    @Column(updatable = false, length = 50)
    private String createdBy;

    @LastModifiedBy
    @Column(length = 50)
    private String updatedBy;
}
```

#### Step 3: AuditorAware 구현 (생성자/수정자 설정)

```java
@Configuration
public class JpaAuditingConfig {

    @Bean
    public AuditorAware<String> auditorProvider() {
        return new AuditorAwareImpl();
    }
}

class AuditorAwareImpl implements AuditorAware<String> {

    @Override
    public Optional<String> getCurrentAuditor() {
        // Security Context에서 인증 정보 가져오기
        // 현재는 임시로 고정값 반환
        return Optional.of("system");

        // Spring Security 사용 시:
        // Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        // if (authentication == null || !authentication.isAuthenticated()) {
        //     return Optional.empty();
        // }
        // return Optional.of(authentication.getName());
    }
}
```

#### Step 4: Entity에 적용

```java
@Entity
@Table(name = "users")
@Getter @Setter
@NoArgsConstructor
public class User extends BaseEntity {  // BaseEntity 상속

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(unique = true, nullable = false)
    private String email;

    @Enumerated(EnumType.STRING)
    private UserStatus status;

    @Builder
    public User(String name, String email, UserStatus status) {
        this.name = name;
        this.email = email;
        this.status = status;
    }
}
```

#### Step 5: 테스트

```java
@SpringBootTest
@Transactional
class AuditingTest {

    @Autowired
    private UserRepository userRepository;

    @Test
    void Auditing_생성시간_자동_설정() {
        // Given
        User user = User.builder()
                .name("홍길동")
                .email("hong@example.com")
                .status(UserStatus.ACTIVE)
                .build();

        // When
        User saved = userRepository.save(user);

        // Then
        assertThat(saved.getCreatedAt()).isNotNull();
        assertThat(saved.getCreatedBy()).isEqualTo("system");
    }

    @Test
    void Auditing_수정시간_자동_갱신() throws InterruptedException {
        // Given
        User user = userRepository.save(
            User.builder()
                .name("홍길동")
                .email("hong@example.com")
                .status(UserStatus.ACTIVE)
                .build()
        );

        Thread.sleep(100);  // 시간 차이를 만들기 위해

        // When
        user.setName("김철수");
        User updated = userRepository.save(user);

        // Then
        assertThat(updated.getUpdatedAt()).isNotNull();
        assertThat(updated.getUpdatedAt()).isAfter(updated.getCreatedAt());
        assertThat(updated.getUpdatedBy()).isEqualTo("system");
    }
}
```

---

## 👨‍💻 주니어 개발자 실전 시나리오

### 시나리오: "블로그 시스템 Repository 구현"

**요구사항:**
- 게시글 CRUD
- 제목/내용 검색
- 페이징 처리
- 인기글 조회 (조회수 TOP 10)
- 최신글 조회
- 작성자별 게시글 조회

#### Step 1: Repository 인터페이스

```java
package com.example.blog.repository;

import com.example.blog.entity.Post;
import com.example.blog.entity.PostStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

public interface PostRepository extends JpaRepository<Post, Long> {

    // 1. 기본 조회 (Query Method)
    Page<Post> findByStatus(PostStatus status, Pageable pageable);

    Optional<Post> findByIdAndStatus(Long id, PostStatus status);

    // 2. 검색 기능
    @Query("SELECT p FROM Post p WHERE " +
           "(p.title LIKE %:keyword% OR p.content LIKE %:keyword%) " +
           "AND p.status = :status")
    Page<Post> searchPosts(
        @Param("keyword") String keyword,
        @Param("status") PostStatus status,
        Pageable pageable
    );

    // 3. 인기글 조회 (조회수 TOP 10)
    @Query("SELECT p FROM Post p WHERE p.status = :status " +
           "ORDER BY p.viewCount DESC, p.createdAt DESC")
    List<Post> findPopularPosts(@Param("status") PostStatus status, Pageable pageable);

    // 4. 최신글 조회
    List<Post> findTop10ByStatusOrderByCreatedAtDesc(PostStatus status);

    // 5. 작성자별 게시글
    Page<Post> findByAuthorAndStatus(String author, PostStatus status, Pageable pageable);

    // 6. 조회수 증가
    @Modifying
    @Query("UPDATE Post p SET p.viewCount = p.viewCount + 1 WHERE p.id = :id")
    void increaseViewCount(@Param("id") Long id);

    // 7. 일별 게시글 수
    @Query("SELECT COUNT(p) FROM Post p " +
           "WHERE p.createdAt >= :startDate AND p.createdAt < :endDate " +
           "AND p.status = :status")
    long countPostsByDateRange(
        @Param("startDate") LocalDateTime startDate,
        @Param("endDate") LocalDateTime endDate,
        @Param("status") PostStatus status
    );

    // 8. 태그별 게시글 (Native Query 예시)
    @Query(value = "SELECT p.* FROM posts p " +
                   "JOIN post_tags pt ON p.id = pt.post_id " +
                   "WHERE pt.tag = :tag AND p.status = :status",
           nativeQuery = true)
    List<Post> findByTag(@Param("tag") String tag, @Param("status") String status);
}
```

#### Step 2: Service 구현

```java
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PostService {

    private final PostRepository postRepository;

    // 게시글 목록 (페이징)
    public Page<Post> getPosts(int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        return postRepository.findByStatus(PostStatus.PUBLISHED, pageable);
    }

    // 게시글 상세 조회
    @Transactional
    public Post getPost(Long id) {
        Post post = postRepository.findByIdAndStatus(id, PostStatus.PUBLISHED)
                .orElseThrow(() -> new IllegalArgumentException("게시글을 찾을 수 없습니다."));

        // 조회수 증가
        postRepository.increaseViewCount(id);

        return post;
    }

    // 게시글 검색
    public Page<Post> searchPosts(String keyword, int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        return postRepository.searchPosts(keyword, PostStatus.PUBLISHED, pageable);
    }

    // 인기글 조회
    public List<Post> getPopularPosts() {
        Pageable pageable = PageRequest.of(0, 10);
        return postRepository.findPopularPosts(PostStatus.PUBLISHED, pageable);
    }

    // 최신글 조회
    public List<Post> getRecentPosts() {
        return postRepository.findTop10ByStatusOrderByCreatedAtDesc(PostStatus.PUBLISHED);
    }

    // 작성자별 게시글
    public Page<Post> getPostsByAuthor(String author, int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        return postRepository.findByAuthorAndStatus(author, PostStatus.PUBLISHED, pageable);
    }

    // 게시글 작성
    @Transactional
    public Post createPost(String title, String content, String author) {
        Post post = Post.builder()
                .title(title)
                .content(content)
                .author(author)
                .status(PostStatus.PUBLISHED)
                .viewCount(0)
                .build();

        return postRepository.save(post);
    }

    // 게시글 수정
    @Transactional
    public Post updatePost(Long id, String title, String content) {
        Post post = postRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("게시글을 찾을 수 없습니다."));

        post.setTitle(title);
        post.setContent(content);

        return post;  // 변경 감지 (Dirty Checking)
    }

    // 게시글 삭제 (Soft Delete)
    @Transactional
    public void deletePost(Long id) {
        Post post = postRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("게시글을 찾을 수 없습니다."));

        post.setStatus(PostStatus.DELETED);
    }

    // 오늘 작성된 게시글 수
    public long getTodayPostCount() {
        LocalDateTime startOfDay = LocalDateTime.now().toLocalDate().atStartOfDay();
        LocalDateTime endOfDay = startOfDay.plusDays(1);

        return postRepository.countPostsByDateRange(
            startOfDay,
            endOfDay,
            PostStatus.PUBLISHED
        );
    }
}
```

#### Step 3: Controller

```java
@RestController
@RequestMapping("/api/posts")
@RequiredArgsConstructor
public class PostController {

    private final PostService postService;

    // 게시글 목록
    @GetMapping
    public ResponseEntity<Page<Post>> getPosts(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {

        Page<Post> posts = postService.getPosts(page, size);
        return ResponseEntity.ok(posts);
    }

    // 게시글 상세
    @GetMapping("/{id}")
    public ResponseEntity<Post> getPost(@PathVariable Long id) {
        Post post = postService.getPost(id);
        return ResponseEntity.ok(post);
    }

    // 게시글 검색
    @GetMapping("/search")
    public ResponseEntity<Page<Post>> searchPosts(
            @RequestParam String keyword,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {

        Page<Post> posts = postService.searchPosts(keyword, page, size);
        return ResponseEntity.ok(posts);
    }

    // 인기글
    @GetMapping("/popular")
    public ResponseEntity<List<Post>> getPopularPosts() {
        List<Post> posts = postService.getPopularPosts();
        return ResponseEntity.ok(posts);
    }

    // 최신글
    @GetMapping("/recent")
    public ResponseEntity<List<Post>> getRecentPosts() {
        List<Post> posts = postService.getRecentPosts();
        return ResponseEntity.ok(posts);
    }

    // 작성자별 게시글
    @GetMapping("/author/{author}")
    public ResponseEntity<Page<Post>> getPostsByAuthor(
            @PathVariable String author,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {

        Page<Post> posts = postService.getPostsByAuthor(author, page, size);
        return ResponseEntity.ok(posts);
    }

    // 게시글 작성
    @PostMapping
    public ResponseEntity<Post> createPost(@RequestBody PostRequest request) {
        Post post = postService.createPost(
            request.getTitle(),
            request.getContent(),
            request.getAuthor()
        );
        return ResponseEntity.ok(post);
    }

    // 게시글 수정
    @PutMapping("/{id}")
    public ResponseEntity<Post> updatePost(
            @PathVariable Long id,
            @RequestBody PostRequest request) {

        Post post = postService.updatePost(id, request.getTitle(), request.getContent());
        return ResponseEntity.ok(post);
    }

    // 게시글 삭제
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deletePost(@PathVariable Long id) {
        postService.deletePost(id);
        return ResponseEntity.noContent().build();
    }

    // 통계
    @GetMapping("/stats/today")
    public ResponseEntity<Long> getTodayPostCount() {
        long count = postService.getTodayPostCount();
        return ResponseEntity.ok(count);
    }
}
```

---

## 🏢 기업 사례: 카카오

### 배경

카카오는 대용량 서비스에서 복잡한 도메인 로직을 다뤄야 했습니다.

**문제점:**
- 복잡한 쿼리 작성의 어려움
- 페이징 처리의 반복 코드
- 테스트 코드 작성의 번거로움

### Spring Data JPA 도입 효과

```java
// Before - 복잡한 구현체 작성
public class UserRepositoryImpl {
    // 100줄 이상의 JPQL 및 페이징 코드
}

// After - 간결한 인터페이스
public interface UserRepository extends JpaRepository<User, Long> {
    Page<User> findByStatus(UserStatus status, Pageable pageable);
}
```

**결과:**
- 코드량 70% 감소
- 테스트 작성 시간 50% 단축
- 신규 기능 개발 속도 3배 향상

---

## ❓ FAQ

### Q1. Query Method와 @Query 중 어떤 것을 사용해야 하나요?

**A:** 우선순위: Query Method → @Query (JPQL) → Native Query

```java
// 1순위: Query Method (간단한 쿼리)
List<User> findByName(String name);

// 2순위: @Query (복잡한 쿼리, JOIN 등)
@Query("SELECT u FROM User u JOIN FETCH u.orders WHERE u.id = :id")
Optional<User> findByIdWithOrders(@Param("id") Long id);

// 3순위: Native Query (DB 특화 기능)
@Query(value = "SELECT * FROM users USE INDEX (idx_name)", nativeQuery = true)
List<User> findWithIndex();
```

### Q2. Page와 Slice의 차이는?

**A:**

| 구분 | Page | Slice |
|-----|------|-------|
| 전체 개수 조회 | O (COUNT 쿼리 실행) | X |
| 사용 용도 | 페이지 번호 네비게이션 | 더보기 버튼 |
| 성능 | 느림 (COUNT 쿼리 추가) | 빠름 |
| 마지막 페이지 확인 | `isLast()` | `hasNext()` |

```java
// Page - 전체 페이지 수 필요
Page<User> page = userRepository.findAll(pageable);
int totalPages = page.getTotalPages();  // COUNT 쿼리 실행

// Slice - 다음 페이지 존재 여부만 확인
Slice<User> slice = userRepository.findAll(pageable);
boolean hasNext = slice.hasNext();  // COUNT 쿼리 없음
```

### Q3. @Modifying 쿼리 사용 시 주의사항은?

**A:** 영속성 컨텍스트와 DB의 불일치 문제

```java
@Modifying
@Query("UPDATE User u SET u.name = :name WHERE u.id = :id")
int updateName(@Param("id") Long id, @Param("name") String name);

// 문제 상황
@Transactional
public void updateUser(Long id) {
    User user = userRepository.findById(id).get();  // 영속성 컨텍스트에 로드
    System.out.println(user.getName());  // "홍길동"

    userRepository.updateName(id, "김철수");  // DB만 변경

    System.out.println(user.getName());  // 여전히 "홍길동" (캐시)
}

// 해결 방법 1: clearAutomatically 옵션
@Modifying(clearAutomatically = true)
@Query("UPDATE User u SET u.name = :name WHERE u.id = :id")
int updateName(@Param("id") Long id, @Param("name") String name);

// 해결 방법 2: 수동 clear
@Transactional
public void updateUser(Long id) {
    userRepository.updateName(id, "김철수");
    entityManager.clear();  // 영속성 컨텍스트 비우기
}
```

### Q4. Stream 반환 타입은 언제 사용하나요?

**A:** 대용량 데이터 처리 시 메모리 절약

```java
// List - 모든 데이터를 메모리에 로드
List<User> users = userRepository.findAll();  // 100만 건이면 OOM 위험

// Stream - 필요한 만큼만 로드
@Query("SELECT u FROM User u")
Stream<User> streamAll();

// 사용
@Transactional(readOnly = true)
public void processAllUsers() {
    try (Stream<User> stream = userRepository.streamAll()) {
        stream.forEach(user -> {
            // 한 건씩 처리
            processUser(user);
        });
    }
}
```

### Q5. Optional 반환 타입을 사용해야 하나요?

**A:** 단일 엔티티 조회 시 Optional 사용 권장

```java
// ❌ Bad - NullPointerException 위험
User user = userRepository.findByEmail(email);
user.getName();  // user가 null이면 NPE 발생

// ✅ Good - Optional로 안전하게 처리
Optional<User> userOpt = userRepository.findByEmail(email);
userOpt.ifPresent(user -> System.out.println(user.getName()));

// 또는
User user = userRepository.findByEmail(email)
        .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다."));
```

---

## 💼 면접 질문 TOP 5

### ⭐ 초급 1: Spring Data JPA의 장점은?

**핵심 답변:**
1. **보일러플레이트 코드 제거**: 인터페이스만 정의하면 구현체 자동 생성
2. **메서드 이름 기반 쿼리**: `findByName` 같은 메서드명으로 쿼리 자동 생성
3. **페이징/정렬 기본 제공**: `Pageable`, `Sort` 파라미터로 간편 처리
4. **타입 안전성**: 컴파일 타임에 오류 검출

### ⭐ 초급 2: JpaRepository를 상속하면 어떤 메서드를 사용할 수 있나요?

**답변:**
```java
// 저장/수정
save(entity)
saveAll(entities)

// 조회
findById(id)
findAll()
findAllById(ids)

// 삭제
delete(entity)
deleteById(id)
deleteAll()

// 기타
count()
existsById(id)
```

### ⭐⭐ 중급 1: Query Method의 메서드 이름 규칙은?

**답변:**
```
[주어] + By + [조건] + [정렬/제한]

예시:
- findByName → WHERE name = ?
- findByNameAndEmail → WHERE name = ? AND email = ?
- findByAgeGreaterThan → WHERE age > ?
- findByNameContaining → WHERE name LIKE %?%
- findByStatusOrderByCreatedAtDesc → WHERE status = ? ORDER BY created_at DESC
```

### ⭐⭐ 중급 2: Page와 Slice의 차이를 설명하세요

**답변:**
- **Page**: 전체 개수 조회 (COUNT 쿼리 실행), 페이지 번호 네비게이션에 적합
- **Slice**: 다음 페이지 존재 여부만 확인, 더보기 버튼에 적합, 성능 우수

```java
// Page - 2개 쿼리 실행
// 1. SELECT * FROM users LIMIT 10
// 2. SELECT COUNT(*) FROM users

// Slice - 1개 쿼리 실행
// 1. SELECT * FROM users LIMIT 11 (size+1 조회)
```

### ⭐⭐ 중급 3: @Modifying 애노테이션은 왜 필요한가요?

**답변:**
SELECT가 아닌 UPDATE/DELETE 쿼리임을 명시하기 위해 필요합니다.

```java
@Modifying
@Transactional
@Query("UPDATE User u SET u.name = :name WHERE u.id = :id")
int updateName(@Param("id") Long id, @Param("name") String name);
```

**주의사항:**
- 영속성 컨텍스트를 거치지 않고 DB에 직접 쿼리 실행
- `clearAutomatically = true` 옵션으로 영속성 컨텍스트 동기화

---

## 🎯 다음 단계

Spring Data JPA를 마쳤다면:

1. **26장: 데이터베이스 스키마 관리** - Flyway/Liquibase
2. **27장: QueryDSL** - 타입 안전한 동적 쿼리
3. **28장: MyBatis 연동** - 복잡한 쿼리 처리
4. **연관관계 매핑 심화** - 양방향 매핑, Fetch 전략
5. **성능 최적화** - N+1 해결, Batch 처리

---

**🎓 학습 완료 체크리스트:**

- [ ] JpaRepository 인터페이스 작성 및 기본 메서드 활용
- [ ] Query Method로 다양한 조회 쿼리 구현
- [ ] @Query로 복잡한 쿼리 작성
- [ ] 페이징과 정렬 처리
- [ ] Auditing으로 생성/수정 시간 자동 관리
- [ ] @Modifying으로 수정/삭제 쿼리 구현
- [ ] 블로그 시스템 Repository 실습 완료

**다음 장에서는 Flyway와 Liquibase로 데이터베이스 스키마를 버전 관리하는 방법을 배웁니다!** 🚀
