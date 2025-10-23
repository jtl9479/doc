# 24장: JPA 소개와 설정 - 객체와 데이터베이스의 완벽한 조화

> **"SQL 작성에서 벗어나 객체로 데이터를 다루는 자유를 경험하세요"**

---

## 📋 학습 목표

이 장을 학습하면 다음을 할 수 있습니다:

- JPA의 개념과 필요성을 이해하고 설명할 수 있습니다
- Spring Boot 프로젝트에 JPA를 설정하고 구성할 수 있습니다
- Entity, EntityManager의 핵심 개념을 이해하고 활용할 수 있습니다
- 영속성 컨텍스트(Persistence Context)의 동작 원리를 이해합니다
- 실무 환경에서 JPA 설정을 최적화할 수 있습니다

**예상 학습 시간**: 4-5시간
**난이도**: ⭐⭐⭐ (중급)

---

## 🤔 왜 JPA가 필요한가?

### 문제 상황

전통적인 JDBC 개발 방식의 문제점:

```java
// 1. SQL 중복 코드
public User findById(Long id) {
    String sql = "SELECT id, name, email FROM users WHERE id = ?";
    // PreparedStatement 생성, 파라미터 설정, ResultSet 처리...
    // 100줄 이상의 보일러플레이트 코드
}

// 2. 객체-테이블 불일치
public class User {
    private Long id;
    private String name;
    private Team team;  // 연관관계는 어떻게 처리?
}

// 3. SQL 의존적 설계
// SQL을 변경하면 자바 코드도 모두 변경해야 함
```

**실제 개발자의 고민:**
- "CRUD마다 비슷한 SQL을 반복 작성하고 있어요"
- "객체의 연관관계를 DB에 어떻게 매핑해야 할까요?"
- "SQL 변경 시 자바 코드를 찾아 수정하는 게 너무 번거로워요"

### JPA의 해결책

```java
// JPA 사용 - 간결하고 객체지향적
@Entity
public class User {
    @Id @GeneratedValue
    private Long id;
    private String name;

    @ManyToOne
    private Team team;  // 연관관계 자동 처리
}

// Repository - SQL 작성 불필요
public interface UserRepository extends JpaRepository<User, Long> {
    // 메서드 이름만으로 쿼리 자동 생성
    List<User> findByName(String name);
}
```

**JPA의 핵심 가치:**
- SQL 자동 생성 → 생산성 향상
- 객체-테이블 매핑 자동화 → 유지보수성 향상
- 데이터베이스 독립성 → 이식성 향상

---

## 🌍 실생활 비유로 이해하는 JPA

### 비유 1: 번역기 (Translator)

**상황:** 한국인과 미국인이 대화를 나누는 상황

```
한국인 (Java 객체)  ←→  통역사 (JPA)  ←→  미국인 (Database)

"안녕하세요"        →    "Hello"         →   [이해]
                    ←    "Thank you"     ←   "감사합니다"
```

**JPA의 역할:**
- Java 객체 언어 ↔ SQL 언어를 자동으로 번역
- 개발자는 자바 코드만 작성, SQL은 JPA가 생성
- 방언(Dialect)을 통해 MySQL, PostgreSQL 등 자동 대응

### 비유 2: 자동 서류 작성 시스템

**전통적 방식 (JDBC):**
```
개발자: 직접 서류 양식을 작성하고 내용을 채워넣음
      → 매번 양식을 찾고, 규칙을 확인하고, 수정해야 함
```

**JPA 방식:**
```
개발자: "홍길동, 30세, 서울"이라고 말하면
JPA: 자동으로 양식을 찾아 서류를 완성
     → INSERT INTO person (name, age, city) VALUES (?, ?, ?)
```

### 비유 3: 도서관 사서 시스템

**당신(개발자):** "이름이 '홍길동'인 책을 찾아줘"
**사서(JPA):** 자동으로 서가를 뒤져서 해당 책을 찾아옴
**당신:** 책의 위치(SQL 쿼리)를 알 필요 없음

```java
// 당신이 하는 일 - 간단한 요청
userRepository.findByName("홍길동");

// JPA가 하는 일 - 복잡한 작업
// SELECT u FROM User u WHERE u.name = :name
// → 실제 SQL 생성 및 실행
```

---

## 💡 JPA 핵심 개념

### 1️⃣ 초급: JPA 기본 개념

#### ORM (Object-Relational Mapping)

```
┌─────────────┐         ┌──────────────┐
│ Java Class  │   ORM   │   DB Table   │
├─────────────┤  ←────→ ├──────────────┤
│ User        │         │ users        │
│ - id        │         │ - id         │
│ - name      │         │ - name       │
│ - email     │         │ - email      │
└─────────────┘         └──────────────┘
```

**핵심 원리:**
- 객체 지향 프로그래밍과 관계형 데이터베이스의 패러다임 불일치 해결
- 클래스 → 테이블, 객체 → 행(Row), 필드 → 컬럼으로 자동 매핑

#### JPA vs Hibernate vs Spring Data JPA

```
┌────────────────────────────────────────┐
│      Spring Data JPA (편의성)          │ ← 가장 높은 추상화
├────────────────────────────────────────┤
│          Hibernate (구현체)            │ ← JPA 구현
├────────────────────────────────────────┤
│           JPA (표준 명세)              │ ← 인터페이스 정의
└────────────────────────────────────────┘
```

**관계 설명:**
- **JPA**: Java 표준 ORM 명세 (javax.persistence)
- **Hibernate**: JPA 구현체 (가장 많이 사용)
- **Spring Data JPA**: Hibernate를 더 쉽게 사용하도록 도와주는 Spring 모듈

### 2️⃣ 중급: 영속성 컨텍스트 (Persistence Context)

#### 영속성 컨텍스트란?

```
Application                Persistence Context              Database
    │                             │                             │
    │──① save(user)──────────────→│                             │
    │                             │──② INSERT──────────────────→│
    │                             │←─③ Result─────────────────┤
    │                             │                             │
    │──④ findById(1)─────────────→│                             │
    │←─⑤ Return from Cache───────│  (DB 조회 없이 반환)       │
```

**영속성 컨텍스트의 역할:**

1. **1차 캐시**: 조회한 엔티티를 메모리에 보관
2. **동일성 보장**: 같은 트랜잭션 내에서 같은 엔티티 반환
3. **변경 감지**: 엔티티 변경을 자동으로 감지하여 UPDATE
4. **지연 로딩**: 연관된 엔티티를 실제 사용 시점에 로딩

#### 엔티티의 생명주기

```java
// 1. 비영속 (new/transient)
User user = new User();
user.setName("홍길동");

// 2. 영속 (managed)
em.persist(user);  // 영속성 컨텍스트에 저장

// 3. 준영속 (detached)
em.detach(user);   // 영속성 컨텍스트에서 분리

// 4. 삭제 (removed)
em.remove(user);   // 삭제
```

**상태 전이도:**
```
   new()
     │
     ↓
[비영속] ──persist()─→ [영속] ──detach()─→ [준영속]
                         │
                         └──remove()─→ [삭제]
```

### 3️⃣ 고급: JPA 내부 동작 원리

#### 쓰기 지연 (Transactional Write-behind)

```java
EntityTransaction tx = em.getTransaction();
tx.begin();

em.persist(user1);  // SQL 저장 (실행 X)
em.persist(user2);  // SQL 저장 (실행 X)
em.persist(user3);  // SQL 저장 (실행 X)

tx.commit();        // ← 여기서 한 번에 실행 (Batch)
```

**동작 과정:**
```
┌─────────────────┐
│ Persistence     │
│ Context         │
├─────────────────┤
│ 1차 캐시        │
│ - user1         │
│ - user2         │
│ - user3         │
├─────────────────┤
│ SQL 저장소      │
│ - INSERT user1  │
│ - INSERT user2  │ ← commit() 시 한 번에 실행
│ - INSERT user3  │
└─────────────────┘
```

**장점:**
- 네트워크 왕복 횟수 감소
- Batch INSERT 최적화
- 트랜잭션 일관성 보장

#### 변경 감지 (Dirty Checking)

```java
// 조회
User user = em.find(User.class, 1L);

// 수정 - update() 메서드 호출 불필요!
user.setName("김철수");

// commit() 시 자동으로 UPDATE 실행
tx.commit();
```

**내부 메커니즘:**
```
1. 최초 조회 시 스냅샷 저장
   user: {id: 1, name: "홍길동"}  ← 스냅샷

2. 엔티티 수정
   user.setName("김철수")

3. commit() 시 비교
   스냅샷: {id: 1, name: "홍길동"}
   현재:   {id: 1, name: "김철수"}  ← 변경 감지!

4. UPDATE SQL 자동 생성 및 실행
   UPDATE users SET name = '김철수' WHERE id = 1
```

---

## 🛠️ 기본 실습

### 실습 1: Spring Boot JPA 프로젝트 설정

#### Step 1: 의존성 추가 (build.gradle)

```gradle
dependencies {
    // Spring Boot Starter Data JPA
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'

    // H2 Database (개발용)
    runtimeOnly 'com.h2database:h2'

    // MySQL (운영용)
    runtimeOnly 'com.mysql.cj:mysql-connector-j'

    // Lombok (선택)
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
}
```

#### Step 2: application.yml 설정

```yaml
spring:
  datasource:
    url: jdbc:h2:mem:testdb
    driver-class-name: org.h2.Driver
    username: sa
    password:

  h2:
    console:
      enabled: true  # H2 콘솔 활성화
      path: /h2-console

  jpa:
    hibernate:
      ddl-auto: create  # 옵션: create, update, validate, none
    properties:
      hibernate:
        format_sql: true  # SQL 포맷팅
        show_sql: true    # SQL 출력
    database-platform: org.hibernate.dialect.H2Dialect

logging:
  level:
    org.hibernate.SQL: DEBUG
    org.hibernate.type.descriptor.sql.BasicBinder: TRACE
```

**ddl-auto 옵션 설명:**
- `create`: 기존 테이블 삭제 후 재생성
- `create-drop`: create + 종료 시 삭제
- `update`: 변경된 스키마만 적용 (운영 위험)
- `validate`: 엔티티와 테이블 매핑 확인만
- `none`: 아무 작업도 하지 않음 (운영 권장)

#### Step 3: Entity 클래스 작성

```java
package com.example.demo.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "users")  // 테이블 명 지정
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 50)
    private String name;

    @Column(unique = true, nullable = false)
    private String email;

    @Column(name = "phone_number", length = 20)
    private String phoneNumber;

    @Enumerated(EnumType.STRING)
    private UserStatus status;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}

enum UserStatus {
    ACTIVE, INACTIVE, SUSPENDED
}
```

**주요 애노테이션 설명:**

| 애노테이션 | 설명 | 예시 |
|----------|------|------|
| `@Entity` | JPA 엔티티 클래스 지정 | `@Entity` |
| `@Table` | 테이블명 지정 | `@Table(name = "users")` |
| `@Id` | 기본키(PK) 지정 | `@Id` |
| `@GeneratedValue` | 자동 생성 전략 | `IDENTITY`, `SEQUENCE`, `AUTO` |
| `@Column` | 컬럼 속성 지정 | `nullable`, `unique`, `length` |
| `@Enumerated` | Enum 타입 매핑 | `EnumType.STRING` 권장 |
| `@PrePersist` | 저장 전 실행 | 생성일시 자동 설정 |
| `@PreUpdate` | 수정 전 실행 | 수정일시 자동 설정 |

#### Step 4: 애플리케이션 실행 및 확인

```java
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

**실행 후 확인:**
1. 콘솔에서 DDL 생성 확인
```sql
Hibernate:
    create table users (
        id bigint generated by default as identity,
        name varchar(50) not null,
        email varchar(255) not null,
        phone_number varchar(20),
        status varchar(255),
        created_at timestamp,
        updated_at timestamp,
        primary key (id)
    )
```

2. H2 콘솔 접속: `http://localhost:8080/h2-console`
3. JDBC URL: `jdbc:h2:mem:testdb`
4. users 테이블 생성 확인

---

### 실습 2: EntityManager를 이용한 CRUD

#### Step 1: EntityManager 기본 사용

```java
package com.example.demo.repository;

import com.example.demo.entity.User;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Repository
public class UserJpaRepository {

    @PersistenceContext
    private EntityManager em;

    // Create
    @Transactional
    public User save(User user) {
        em.persist(user);
        return user;
    }

    // Read
    public User findById(Long id) {
        return em.find(User.class, id);
    }

    // Update
    @Transactional
    public User update(Long id, String newName) {
        User user = em.find(User.class, id);
        user.setName(newName);  // 변경 감지 (Dirty Checking)
        return user;  // update() 메서드 호출 불필요!
    }

    // Delete
    @Transactional
    public void delete(Long id) {
        User user = em.find(User.class, id);
        em.remove(user);
    }

    // 전체 조회
    public List<User> findAll() {
        return em.createQuery("SELECT u FROM User u", User.class)
                 .getResultList();
    }

    // 이름으로 조회
    public List<User> findByName(String name) {
        return em.createQuery(
                "SELECT u FROM User u WHERE u.name = :name", User.class)
                 .setParameter("name", name)
                 .getResultList();
    }
}
```

#### Step 2: 테스트 코드 작성

```java
package com.example.demo;

import com.example.demo.entity.User;
import com.example.demo.entity.UserStatus;
import com.example.demo.repository.UserJpaRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import static org.assertj.core.api.Assertions.*;

@SpringBootTest
@Transactional
class UserJpaRepositoryTest {

    @Autowired
    private UserJpaRepository repository;

    @Test
    void 사용자_저장_테스트() {
        // Given
        User user = User.builder()
                .name("홍길동")
                .email("hong@example.com")
                .phoneNumber("010-1234-5678")
                .status(UserStatus.ACTIVE)
                .build();

        // When
        User saved = repository.save(user);

        // Then
        assertThat(saved.getId()).isNotNull();
        assertThat(saved.getName()).isEqualTo("홍길동");
        assertThat(saved.getCreatedAt()).isNotNull();
    }

    @Test
    void 사용자_조회_테스트() {
        // Given
        User user = repository.save(
            User.builder()
                .name("김철수")
                .email("kim@example.com")
                .status(UserStatus.ACTIVE)
                .build()
        );

        // When
        User found = repository.findById(user.getId());

        // Then
        assertThat(found).isNotNull();
        assertThat(found.getName()).isEqualTo("김철수");
    }

    @Test
    void 사용자_수정_테스트() {
        // Given
        User user = repository.save(
            User.builder()
                .name("이영희")
                .email("lee@example.com")
                .status(UserStatus.ACTIVE)
                .build()
        );

        // When
        User updated = repository.update(user.getId(), "이영희_수정");

        // Then
        assertThat(updated.getName()).isEqualTo("이영희_수정");
        assertThat(updated.getUpdatedAt()).isNotNull();
    }

    @Test
    void 영속성_컨텍스트_1차_캐시_테스트() {
        // Given
        User user = repository.save(
            User.builder()
                .name("박민수")
                .email("park@example.com")
                .status(UserStatus.ACTIVE)
                .build()
        );

        // When
        User found1 = repository.findById(user.getId());
        User found2 = repository.findById(user.getId());  // 캐시에서 조회

        // Then
        assertThat(found1).isSameAs(found2);  // 동일한 객체 참조
    }
}
```

---

### 실습 3: JPQL (Java Persistence Query Language)

#### JPQL이란?

- SQL과 유사하지만 **테이블이 아닌 객체**를 대상으로 쿼리
- 데이터베이스 독립적 (방언에 따라 자동 변환)

```java
@Repository
public class UserQueryRepository {

    @PersistenceContext
    private EntityManager em;

    // 기본 조회
    public List<User> findActiveUsers() {
        String jpql = "SELECT u FROM User u WHERE u.status = :status";
        return em.createQuery(jpql, User.class)
                 .setParameter("status", UserStatus.ACTIVE)
                 .getResultList();
    }

    // 페이징 처리
    public List<User> findUsersWithPaging(int page, int size) {
        return em.createQuery("SELECT u FROM User u ORDER BY u.id DESC", User.class)
                 .setFirstResult(page * size)  // offset
                 .setMaxResults(size)           // limit
                 .getResultList();
    }

    // 집계 함수
    public Long countActiveUsers() {
        return em.createQuery(
                "SELECT COUNT(u) FROM User u WHERE u.status = :status", Long.class)
                 .setParameter("status", UserStatus.ACTIVE)
                 .getSingleResult();
    }

    // JOIN 쿼리 (예시)
    public List<User> findUsersWithTeam() {
        String jpql = "SELECT u FROM User u JOIN FETCH u.team";
        return em.createQuery(jpql, User.class)
                 .getResultList();
    }

    // Native Query (특수한 경우)
    public List<User> findByNativeQuery(String name) {
        String sql = "SELECT * FROM users WHERE name LIKE ?1";
        return em.createNativeQuery(sql, User.class)
                 .setParameter(1, "%" + name + "%")
                 .getResultList();
    }
}
```

**JPQL vs SQL 비교:**

| 구분 | JPQL | SQL |
|-----|------|-----|
| 대상 | 엔티티 객체 | 테이블 |
| 예시 | `SELECT u FROM User u` | `SELECT * FROM users` |
| 컬럼 | 필드명 (`u.name`) | 컬럼명 (`name`) |
| 조인 | `JOIN u.team` | `JOIN teams ON ...` |
| 페이징 | `setFirstResult/setMaxResults` | `LIMIT, OFFSET` |

---

## 👨‍💻 주니어 개발자 실전 시나리오

### 시나리오: "게시판 시스템 개발"

**요구사항:**
- 게시글(Post) 엔티티 설계
- CRUD 기능 구현
- 제목으로 검색 기능
- 페이징 처리

#### Step 1: Entity 설계

```java
@Entity
@Table(name = "posts")
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Post {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String content;

    @Column(nullable = false)
    private String author;

    @Column(name = "view_count")
    private Integer viewCount = 0;

    @Enumerated(EnumType.STRING)
    private PostStatus status = PostStatus.PUBLISHED;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        if (viewCount == null) {
            viewCount = 0;
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    // 비즈니스 메서드
    public void increaseViewCount() {
        this.viewCount++;
    }
}

enum PostStatus {
    PUBLISHED, DRAFT, DELETED
}
```

#### Step 2: Repository 구현

```java
@Repository
public class PostRepository {

    @PersistenceContext
    private EntityManager em;

    @Transactional
    public Post save(Post post) {
        em.persist(post);
        return post;
    }

    public Post findById(Long id) {
        return em.find(Post.class, id);
    }

    @Transactional
    public Post update(Long id, String title, String content) {
        Post post = findById(id);
        if (post != null) {
            post.setTitle(title);
            post.setContent(content);
        }
        return post;
    }

    @Transactional
    public void delete(Long id) {
        Post post = findById(id);
        if (post != null) {
            post.setStatus(PostStatus.DELETED);  // Soft Delete
        }
    }

    // 제목으로 검색
    public List<Post> searchByTitle(String keyword) {
        String jpql = "SELECT p FROM Post p " +
                      "WHERE p.title LIKE :keyword " +
                      "AND p.status = :status " +
                      "ORDER BY p.createdAt DESC";

        return em.createQuery(jpql, Post.class)
                 .setParameter("keyword", "%" + keyword + "%")
                 .setParameter("status", PostStatus.PUBLISHED)
                 .getResultList();
    }

    // 페이징 조회
    public List<Post> findAllWithPaging(int page, int size) {
        return em.createQuery(
                "SELECT p FROM Post p " +
                "WHERE p.status = :status " +
                "ORDER BY p.createdAt DESC", Post.class)
                 .setParameter("status", PostStatus.PUBLISHED)
                 .setFirstResult(page * size)
                 .setMaxResults(size)
                 .getResultList();
    }

    // 전체 개수 조회
    public Long count() {
        return em.createQuery(
                "SELECT COUNT(p) FROM Post p WHERE p.status = :status", Long.class)
                 .setParameter("status", PostStatus.PUBLISHED)
                 .getSingleResult();
    }

    // 조회수 증가
    @Transactional
    public void increaseViewCount(Long id) {
        Post post = findById(id);
        if (post != null) {
            post.increaseViewCount();
        }
    }
}
```

#### Step 3: Service 레이어

```java
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PostService {

    private final PostRepository postRepository;

    @Transactional
    public Post createPost(String title, String content, String author) {
        Post post = Post.builder()
                .title(title)
                .content(content)
                .author(author)
                .status(PostStatus.PUBLISHED)
                .build();

        return postRepository.save(post);
    }

    public Post getPost(Long id) {
        Post post = postRepository.findById(id);
        if (post == null) {
            throw new IllegalArgumentException("게시글을 찾을 수 없습니다.");
        }

        // 조회수 증가 (별도 트랜잭션)
        postRepository.increaseViewCount(id);

        return post;
    }

    @Transactional
    public Post updatePost(Long id, String title, String content) {
        return postRepository.update(id, title, content);
    }

    @Transactional
    public void deletePost(Long id) {
        postRepository.delete(id);
    }

    public List<Post> searchPosts(String keyword) {
        return postRepository.searchByTitle(keyword);
    }

    public List<Post> getPostsWithPaging(int page, int size) {
        return postRepository.findAllWithPaging(page, size);
    }

    public Long getTotalCount() {
        return postRepository.count();
    }
}
```

#### Step 4: Controller (REST API)

```java
@RestController
@RequestMapping("/api/posts")
@RequiredArgsConstructor
public class PostController {

    private final PostService postService;

    @PostMapping
    public ResponseEntity<Post> createPost(@RequestBody PostRequest request) {
        Post post = postService.createPost(
            request.getTitle(),
            request.getContent(),
            request.getAuthor()
        );
        return ResponseEntity.ok(post);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Post> getPost(@PathVariable Long id) {
        Post post = postService.getPost(id);
        return ResponseEntity.ok(post);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Post> updatePost(
            @PathVariable Long id,
            @RequestBody PostRequest request) {
        Post post = postService.updatePost(id, request.getTitle(), request.getContent());
        return ResponseEntity.ok(post);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deletePost(@PathVariable Long id) {
        postService.deletePost(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/search")
    public ResponseEntity<List<Post>> searchPosts(@RequestParam String keyword) {
        List<Post> posts = postService.searchPosts(keyword);
        return ResponseEntity.ok(posts);
    }

    @GetMapping
    public ResponseEntity<PostPageResponse> getPosts(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {

        List<Post> posts = postService.getPostsWithPaging(page, size);
        Long total = postService.getTotalCount();

        PostPageResponse response = new PostPageResponse(posts, total, page, size);
        return ResponseEntity.ok(response);
    }
}

// DTO 클래스
@Data
class PostRequest {
    private String title;
    private String content;
    private String author;
}

@Data
@AllArgsConstructor
class PostPageResponse {
    private List<Post> posts;
    private Long total;
    private int page;
    private int size;

    public int getTotalPages() {
        return (int) Math.ceil((double) total / size);
    }
}
```

#### Step 5: 테스트

```java
@SpringBootTest
@Transactional
class PostServiceTest {

    @Autowired
    private PostService postService;

    @Test
    void 게시글_생성_테스트() {
        // When
        Post post = postService.createPost(
            "JPA 학습하기",
            "JPA는 정말 유용합니다.",
            "홍길동"
        );

        // Then
        assertThat(post.getId()).isNotNull();
        assertThat(post.getTitle()).isEqualTo("JPA 학습하기");
        assertThat(post.getViewCount()).isEqualTo(0);
    }

    @Test
    void 게시글_조회수_증가_테스트() {
        // Given
        Post post = postService.createPost("테스트", "내용", "작성자");

        // When
        Post found1 = postService.getPost(post.getId());
        Post found2 = postService.getPost(post.getId());

        // Then
        assertThat(found2.getViewCount()).isEqualTo(2);
    }

    @Test
    void 게시글_검색_테스트() {
        // Given
        postService.createPost("Spring JPA", "내용1", "작성자1");
        postService.createPost("Spring Boot", "내용2", "작성자2");
        postService.createPost("Java 학습", "내용3", "작성자3");

        // When
        List<Post> results = postService.searchPosts("Spring");

        // Then
        assertThat(results).hasSize(2);
    }
}
```

---

## 🏢 기업 사례: 우아한형제들 (배달의민족)

### 배경

배달의민족은 초기 MyBatis로 개발했으나, 서비스 규모가 커지면서 다음 문제에 직면:

1. **중복 코드**: 비슷한 SQL 쿼리 반복 작성
2. **유지보수 어려움**: SQL 변경 시 자바 코드 전체 수정
3. **생산성 저하**: 단순 CRUD에 너무 많은 시간 소요

### JPA 도입 효과

```java
// Before (MyBatis) - 100줄 이상
@Mapper
public interface OrderMapper {
    @Select("SELECT * FROM orders WHERE id = #{id}")
    Order findById(Long id);

    @Insert("INSERT INTO orders (...) VALUES (...)")
    void insert(Order order);
    // ... 반복적인 SQL 작성
}

// After (JPA) - 단 1줄
public interface OrderRepository extends JpaRepository<Order, Long> {
    // 메서드 이름만으로 쿼리 자동 생성
    List<Order> findByCustomerId(Long customerId);
}
```

**결과:**
- 개발 시간 30% 단축
- 버그 발생률 40% 감소
- 신규 기능 개발 속도 2배 향상

### 핵심 전략

1. **점진적 전환**: 신규 도메인부터 JPA 적용
2. **혼합 사용**: 복잡한 쿼리는 QueryDSL 활용
3. **성능 최적화**: N+1 문제 해결 (Fetch Join, @BatchSize)

---

## ❓ FAQ

### Q1. JPA를 사용하면 무조건 빠른가요?

**A:** 아닙니다. JPA는 생산성 향상이 주 목적이며, 부적절한 사용 시 오히려 느려질 수 있습니다.

**느려지는 경우:**
```java
// N+1 문제
List<Order> orders = orderRepository.findAll();
for (Order order : orders) {
    order.getCustomer().getName();  // 각각 SELECT 쿼리 발생!
}
```

**최적화 방법:**
```java
// Fetch Join 사용
@Query("SELECT o FROM Order o JOIN FETCH o.customer")
List<Order> findAllWithCustomer();
```

### Q2. Entity에 비즈니스 로직을 넣어야 하나요?

**A:** 도메인 로직은 Entity에, 애플리케이션 로직은 Service에 넣는 것이 좋습니다.

```java
// ✅ Good - 도메인 로직은 Entity에
@Entity
public class Order {
    private OrderStatus status;

    public void cancel() {
        if (status == OrderStatus.DELIVERED) {
            throw new IllegalStateException("배송 완료된 주문은 취소할 수 없습니다.");
        }
        this.status = OrderStatus.CANCELLED;
    }
}

// ✅ Good - 애플리케이션 로직은 Service에
@Service
public class OrderService {
    public void cancelOrder(Long orderId) {
        Order order = orderRepository.findById(orderId);
        order.cancel();  // Entity의 메서드 호출

        // 부가 작업
        notificationService.sendCancelNotification(order);
        paymentService.refund(order);
    }
}
```

### Q3. ddl-auto는 무엇을 사용해야 하나요?

**A:** 환경에 따라 다릅니다.

| 환경 | 설정 | 이유 |
|-----|------|------|
| 로컬 개발 | `create` 또는 `update` | 빠른 테스트 |
| 테스트 | `create` | 깨끗한 상태로 시작 |
| 스테이징 | `validate` | 스키마 검증만 |
| 운영 | `none` 또는 `validate` | 절대 자동 변경 금지 |

**운영 환경 설정:**
```yaml
spring:
  jpa:
    hibernate:
      ddl-auto: none  # 또는 validate
    properties:
      hibernate:
        show_sql: false  # 운영에서는 false
```

### Q4. JPQL과 Native Query 중 무엇을 사용해야 하나요?

**A:** 우선순위: JPQL → QueryDSL → Native Query

```java
// 1순위: JPQL (객체지향, DB 독립적)
@Query("SELECT u FROM User u WHERE u.name = :name")
List<User> findByName(@Param("name") String name);

// 2순위: QueryDSL (타입 안전, 동적 쿼리)
QUser user = QUser.user;
queryFactory.selectFrom(user)
            .where(user.name.eq(name))
            .fetch();

// 3순위: Native Query (특수한 경우만)
@Query(value = "SELECT * FROM users WHERE name = ?1", nativeQuery = true)
List<User> findByNameNative(String name);
```

**Native Query가 필요한 경우:**
- DB 고유 기능 사용 (MySQL의 FULLTEXT 검색 등)
- 복잡한 통계 쿼리
- 성능 최적화가 필수적인 경우

### Q5. @Transactional은 언제 사용하나요?

**A:** 데이터 변경(CUD) 작업에는 필수, 조회(R)에는 readOnly 옵션 사용

```java
@Service
@Transactional(readOnly = true)  // 기본값: 읽기 전용
public class UserService {

    // 조회 - @Transactional(readOnly = true) 상속
    public User findById(Long id) {
        return userRepository.findById(id);
    }

    // 변경 - @Transactional 재정의
    @Transactional
    public User updateUser(Long id, String name) {
        User user = userRepository.findById(id);
        user.setName(name);  // 변경 감지 (Dirty Checking)
        return user;
    }
}
```

**@Transactional이 필요한 이유:**
1. **원자성 보장**: 모두 성공 or 모두 실패
2. **변경 감지**: 엔티티 수정 시 자동 UPDATE
3. **영속성 컨텍스트**: 1차 캐시, 지연 로딩 등

---

## 💼 면접 질문 TOP 5

### ⭐ 초급 1: JPA와 MyBatis의 차이는?

**예상 답변:**

| 구분 | JPA | MyBatis |
|-----|-----|---------|
| 패러다임 | ORM (객체지향) | SQL Mapper |
| SQL 작성 | 자동 생성 | 직접 작성 |
| 생산성 | 높음 (CRUD 자동) | 낮음 (모든 SQL 작성) |
| 학습 곡선 | 가파름 | 완만함 |
| 복잡한 쿼리 | QueryDSL 필요 | 자유롭게 작성 |
| 적합한 경우 | 도메인 중심 개발 | SQL 중심 개발 |

**실무 조언:**
- 신규 프로젝트: JPA 추천 (생산성)
- 레거시 시스템: MyBatis (기존 SQL 활용)
- 복잡한 통계: MyBatis 또는 Native Query

### ⭐ 초급 2: 영속성 컨텍스트란?

**핵심 답변:**
"엔티티를 메모리에 보관하는 1차 캐시입니다. 같은 트랜잭션 내에서 같은 엔티티를 조회하면 DB가 아닌 캐시에서 반환합니다."

**동작 예시:**
```java
User user1 = em.find(User.class, 1L);  // DB 조회
User user2 = em.find(User.class, 1L);  // 캐시에서 조회

assertThat(user1 == user2).isTrue();  // 동일한 객체
```

**주요 기능:**
1. **1차 캐시**: 조회 성능 향상
2. **동일성 보장**: 같은 ID → 같은 객체
3. **변경 감지**: 수정 시 자동 UPDATE
4. **쓰기 지연**: commit 시 일괄 실행

### ⭐⭐ 중급 1: N+1 문제와 해결 방법은?

**문제 상황:**
```java
// 1번 쿼리: Order 조회
List<Order> orders = orderRepository.findAll();

// N번 쿼리: 각 Order마다 Customer 조회
for (Order order : orders) {
    System.out.println(order.getCustomer().getName());
}
// 총 1 + N번의 쿼리 발생!
```

**해결 방법:**

1. **Fetch Join (JPQL)**
```java
@Query("SELECT o FROM Order o JOIN FETCH o.customer")
List<Order> findAllWithCustomer();
```

2. **@EntityGraph**
```java
@EntityGraph(attributePaths = {"customer"})
List<Order> findAll();
```

3. **@BatchSize**
```java
@Entity
public class Order {
    @ManyToOne
    @BatchSize(size = 100)
    private Customer customer;
}
```

### ⭐⭐ 중급 2: @Transactional의 전파 속성(Propagation)을 설명하세요

**핵심 개념:**
트랜잭션이 이미 있을 때 새 트랜잭션을 어떻게 처리할지 결정

**주요 속성:**

```java
// REQUIRED (기본값): 기존 트랜잭션 사용, 없으면 새로 생성
@Transactional(propagation = Propagation.REQUIRED)
public void method1() {
    method2();  // 같은 트랜잭션
}

// REQUIRES_NEW: 항상 새 트랜잭션 생성
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void method2() {
    // 독립적인 트랜잭션
}
```

**실무 사례:**
```java
@Service
public class OrderService {

    @Transactional
    public void createOrder(Order order) {
        orderRepository.save(order);

        // 로그는 주문 실패해도 저장되어야 함
        logService.saveLog(order);
    }
}

@Service
public class LogService {

    // 별도 트랜잭션으로 실행
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void saveLog(Order order) {
        logRepository.save(new Log(order));
    }
}
```

### ⭐⭐ 중급 3: JPA의 1차 캐시와 2차 캐시의 차이는?

**비교표:**

| 구분 | 1차 캐시 | 2차 캐시 |
|-----|---------|----------|
| 범위 | 트랜잭션 내 (EntityManager) | 애플리케이션 전체 |
| 생명주기 | 트랜잭션 종료 시 소멸 | 애플리케이션 종료까지 |
| 동시성 | 문제 없음 (격리) | 동시성 제어 필요 |
| 설정 | 기본 활성화 | 별도 설정 필요 |
| 용도 | 동일성 보장, 변경 감지 | 성능 최적화 |

**1차 캐시 (기본):**
```java
// 같은 트랜잭션 내
User user1 = em.find(User.class, 1L);  // DB 조회
User user2 = em.find(User.class, 1L);  // 캐시 조회
```

**2차 캐시 (설정 필요):**
```java
@Entity
@Cacheable
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
public class Product {
    // 자주 조회되고 변경이 적은 데이터
}
```

```yaml
spring:
  jpa:
    properties:
      hibernate:
        cache:
          use_second_level_cache: true
          region.factory_class: org.hibernate.cache.jcache.JCacheRegionFactory
```

---

## 🎯 다음 단계

JPA 기본 설정을 마쳤다면:

1. **25장: Spring Data JPA** - Repository 인터페이스로 더 간편하게
2. **26장: 데이터베이스 스키마 관리** - Flyway/Liquibase로 버전 관리
3. **27장: QueryDSL** - 타입 안전한 동적 쿼리 작성
4. **연관관계 매핑** - @OneToMany, @ManyToOne 마스터하기
5. **성능 최적화** - N+1 해결, 쿼리 최적화

---

## 📚 참고 자료

- **공식 문서**: [Spring Data JPA Reference](https://docs.spring.io/spring-data/jpa/docs/current/reference/html/)
- **Hibernate 문서**: [Hibernate ORM Documentation](https://hibernate.org/orm/documentation/)
- **추천 도서**:
  - "자바 ORM 표준 JPA 프로그래밍" - 김영한
  - "스프링 부트와 AWS로 혼자 구현하는 웹 서비스" - 이동욱

---

**🎓 학습 완료 체크리스트:**

- [ ] JPA, Hibernate, Spring Data JPA 차이 이해
- [ ] Entity 클래스 작성 및 애노테이션 활용
- [ ] EntityManager를 이용한 CRUD 구현
- [ ] 영속성 컨텍스트와 1차 캐시 이해
- [ ] JPQL 기본 쿼리 작성
- [ ] @Transactional 적절히 사용
- [ ] 게시판 시스템 실습 완료

**다음 장에서는 Spring Data JPA로 더 간편하게 데이터를 다루는 방법을 배웁니다!** 🚀
