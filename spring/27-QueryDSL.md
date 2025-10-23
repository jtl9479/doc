# 27장: QueryDSL - 타입 안전한 동적 쿼리의 힘

> **"문자열 쿼리의 불안함을 컴파일 타임 체크로 해결하세요"**

---

## 📋 학습 목표

이 장을 학습하면 다음을 할 수 있습니다:

- QueryDSL의 개념과 필요성을 이해합니다
- QClass를 생성하고 활용할 수 있습니다
- 복잡한 동적 쿼리를 타입 안전하게 작성합니다
- BooleanExpression으로 재사용 가능한 조건을 만듭니다
- Projection으로 DTO를 직접 조회합니다
- 페이징, 정렬, 집계 쿼리를 작성합니다

**예상 학습 시간**: 4-5시간
**난이도**: ⭐⭐⭐⭐ (중고급)

---

## 🤔 왜 QueryDSL이 필요한가?

### 문제 상황: 문자열 기반 쿼리의 한계

#### 문제 1: JPQL의 타입 안정성 부재

```java
// ❌ JPQL - 오타나 잘못된 필드명은 런타임에만 발견
@Query("SELECT u FROM User u WHERE u.nmae = :name")  // nmae → name (오타!)
List<User> findByName(@Param("name") String name);
// 컴파일 시 오류 없음 → 런타임에 QuerySyntaxException 발생!
```

#### 문제 2: 동적 쿼리 작성의 어려움

```java
// 복잡한 검색 조건
public List<User> search(String name, String email, UserStatus status,
                         LocalDateTime startDate, LocalDateTime endDate) {

    // JPQL로 동적 쿼리 작성하려면?
    String jpql = "SELECT u FROM User u WHERE 1=1";

    if (name != null) {
        jpql += " AND u.name LIKE :name";
    }
    if (email != null) {
        jpql += " AND u.email = :email";
    }
    if (status != null) {
        jpql += " AND u.status = :status";
    }
    if (startDate != null) {
        jpql += " AND u.createdAt >= :startDate";
    }
    if (endDate != null) {
        jpql += " AND u.createdAt <= :endDate";
    }

    TypedQuery<User> query = em.createQuery(jpql, User.class);

    // 파라미터 바인딩도 조건부로...
    if (name != null) query.setParameter("name", "%" + name + "%");
    if (email != null) query.setParameter("email", email);
    // ... 복잡하고 오류 발생 가능성 높음!

    return query.getResultList();
}
```

#### 문제 3: 리팩토링의 어려움

```java
// User 엔티티에서 email → emailAddress로 변경
@Entity
public class User {
    // private String email;  // 삭제
    private String emailAddress;  // 추가
}

// JPQL은 문자열이라 자동 리팩토링 안 됨!
@Query("SELECT u FROM User u WHERE u.email = :email")  // 여전히 email!
List<User> findByEmail(@Param("email") String email);
// IDE가 감지 못함 → 런타임 에러
```

### QueryDSL의 해결책

```java
// ✅ QueryDSL - 타입 안전, 컴파일 타임 체크
QUser user = QUser.user;

List<User> result = queryFactory
    .selectFrom(user)
    .where(user.name.eq("홍길동"))  // 오타 시 컴파일 에러!
    .fetch();

// 동적 쿼리도 간결하게
BooleanBuilder builder = new BooleanBuilder();
if (name != null) builder.and(user.name.contains(name));
if (email != null) builder.and(user.email.eq(email));
if (status != null) builder.and(user.status.eq(status));

List<User> users = queryFactory
    .selectFrom(user)
    .where(builder)  // 조건 조합
    .fetch();

// 리팩토링 안전: email → emailAddress 변경 시
// IDE가 자동으로 user.email → user.emailAddress로 변경
```

**QueryDSL의 핵심 가치:**
- 컴파일 타임 타입 체크 → 런타임 에러 방지
- IDE 자동완성 지원 → 생산성 향상
- 동적 쿼리 간결하게 작성 → 유지보수성 향상
- 리팩토링 안전 → 필드명 변경 시 자동 반영

---

## 🌍 실생활 비유로 이해하는 QueryDSL

### 비유 1: 레고 블록 vs 찰흙

**JPQL (찰흙):**
```
"SELECT u FROM User u WHERE u.name = :name"
→ 자유롭게 만들 수 있지만, 모양이 정확한지 확인 어려움
→ 완성 후에야 잘못된 부분 발견
```

**QueryDSL (레고 블록):**
```java
queryFactory.selectFrom(user).where(user.name.eq(name))
→ 블록이 맞지 않으면 끼워지지 않음 (컴파일 에러)
→ 조립 과정에서 오류 즉시 발견
```

### 비유 2: 수동 조립 vs 자동 완성 가구

**JPQL:**
```
"설명서를 보며 직접 조립"
나사 A를 구멍 B에... (오타 가능)
→ 완성 후 테스트해야 문제 발견
```

**QueryDSL:**
```java
IDE가 "여기에는 user.name이 들어갈 수 있어요" 자동 제시
→ 선택만 하면 됨 (오타 불가능)
→ 즉시 피드백
```

### 비유 3: 종이 지도 vs GPS 네비게이션

**JPQL (종이 지도):**
```sql
"SELECT u FROM User u WHERE u.name = '홍길동'"
→ 주소를 직접 적어야 함 (오타 위험)
→ 길이 변경되어도 모름
```

**QueryDSL (GPS):**
```java
user.name.eq("홍길동")
→ 자동완성으로 정확한 경로 제시
→ User 클래스 변경 시 자동 갱신
```

---

## 💡 QueryDSL 핵심 개념

### 1️⃣ 초급: QueryDSL 설정 및 기본 사용

#### 의존성 추가

```gradle
// build.gradle
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.2.0'
    id 'io.spring.dependency-management' version '1.1.4'
}

dependencies {
    // Spring Data JPA
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'

    // QueryDSL
    implementation 'com.querydsl:querydsl-jpa:5.0.0:jakarta'
    annotationProcessor "com.querydsl:querydsl-apt:5.0.0:jakarta"
    annotationProcessor "jakarta.annotation:jakarta.annotation-api"
    annotationProcessor "jakarta.persistence:jakarta.persistence-api"

    // Database
    runtimeOnly 'com.mysql.cj:mysql-connector-j'
}

// QueryDSL Q클래스 생성 경로 설정
def generatedDir = "$buildDir/generated/querydsl"

sourceSets {
    main.java.srcDirs += [generatedDir]
}

tasks.withType(JavaCompile) {
    options.generatedSourceOutputDirectory = file(generatedDir)
}

clean {
    delete file(generatedDir)
}
```

#### QClass 생성

```bash
# Gradle 빌드 시 자동 생성
./gradlew clean build

# 또는 compileJava만
./gradlew compileJava
```

**생성된 QClass:**
```
build/generated/querydsl/
└── com/example/demo/entity/
    ├── QUser.java
    ├── QPost.java
    └── QComment.java
```

#### JPAQueryFactory 설정

```java
@Configuration
public class QueryDslConfig {

    @PersistenceContext
    private EntityManager entityManager;

    @Bean
    public JPAQueryFactory jpaQueryFactory() {
        return new JPAQueryFactory(entityManager);
    }
}
```

#### 기본 쿼리 작성

```java
@Repository
@RequiredArgsConstructor
public class UserQueryRepository {

    private final JPAQueryFactory queryFactory;

    // 1. 단일 조회
    public User findById(Long id) {
        QUser user = QUser.user;

        return queryFactory
                .selectFrom(user)
                .where(user.id.eq(id))
                .fetchOne();  // 단일 결과 (없으면 null)
    }

    // 2. 리스트 조회
    public List<User> findByName(String name) {
        QUser user = QUser.user;

        return queryFactory
                .selectFrom(user)
                .where(user.name.eq(name))
                .fetch();  // 리스트 결과
    }

    // 3. 조건 조합
    public List<User> findActiveUsers(String name) {
        QUser user = QUser.user;

        return queryFactory
                .selectFrom(user)
                .where(
                    user.name.contains(name),  // LIKE %name%
                    user.status.eq(UserStatus.ACTIVE)
                )
                .orderBy(user.createdAt.desc())
                .fetch();
    }

    // 4. 페이징
    public List<User> findUsersWithPaging(int offset, int limit) {
        QUser user = QUser.user;

        return queryFactory
                .selectFrom(user)
                .orderBy(user.createdAt.desc())
                .offset(offset)
                .limit(limit)
                .fetch();
    }

    // 5. 카운트
    public long count() {
        QUser user = QUser.user;

        return queryFactory
                .selectFrom(user)
                .fetchCount();  // COUNT 쿼리
    }
}
```

### 2️⃣ 중급: 동적 쿼리와 BooleanExpression

#### BooleanBuilder 방식

```java
@Repository
@RequiredArgsConstructor
public class UserSearchRepository {

    private final JPAQueryFactory queryFactory;

    public List<User> search(UserSearchCondition condition) {
        QUser user = QUser.user;

        BooleanBuilder builder = new BooleanBuilder();

        // 조건이 있을 때만 추가
        if (hasText(condition.getName())) {
            builder.and(user.name.contains(condition.getName()));
        }
        if (hasText(condition.getEmail())) {
            builder.and(user.email.eq(condition.getEmail()));
        }
        if (condition.getStatus() != null) {
            builder.and(user.status.eq(condition.getStatus()));
        }
        if (condition.getAgeGoe() != null) {
            builder.and(user.age.goe(condition.getAgeGoe()));  // >=
        }
        if (condition.getAgeLoe() != null) {
            builder.and(user.age.loe(condition.getAgeLoe()));  // <=
        }

        return queryFactory
                .selectFrom(user)
                .where(builder)
                .fetch();
    }

    private boolean hasText(String str) {
        return str != null && !str.isEmpty();
    }
}

// 검색 조건 DTO
@Data
public class UserSearchCondition {
    private String name;
    private String email;
    private UserStatus status;
    private Integer ageGoe;  // age >=
    private Integer ageLoe;  // age <=
}
```

#### BooleanExpression 방식 (권장)

```java
@Repository
@RequiredArgsConstructor
public class UserQueryRepository {

    private final JPAQueryFactory queryFactory;

    public List<User> search(UserSearchCondition condition) {
        QUser user = QUser.user;

        return queryFactory
                .selectFrom(user)
                .where(
                    nameContains(condition.getName()),
                    emailEq(condition.getEmail()),
                    statusEq(condition.getStatus()),
                    ageGoe(condition.getAgeGoe()),
                    ageLoe(condition.getAgeLoe())
                )
                .fetch();
    }

    // 재사용 가능한 조건 메서드
    private BooleanExpression nameContains(String name) {
        return hasText(name) ? QUser.user.name.contains(name) : null;
    }

    private BooleanExpression emailEq(String email) {
        return hasText(email) ? QUser.user.email.eq(email) : null;
    }

    private BooleanExpression statusEq(UserStatus status) {
        return status != null ? QUser.user.status.eq(status) : null;
    }

    private BooleanExpression ageGoe(Integer age) {
        return age != null ? QUser.user.age.goe(age) : null;
    }

    private BooleanExpression ageLoe(Integer age) {
        return age != null ? QUser.user.age.loe(age) : null;
    }

    // 조건 조합
    private BooleanExpression ageBetween(Integer ageGoe, Integer ageLoe) {
        return ageGoe(ageGoe).and(ageLoe(ageLoe));
    }

    private BooleanExpression activeUser() {
        return QUser.user.status.eq(UserStatus.ACTIVE);
    }

    private boolean hasText(String str) {
        return str != null && !str.isEmpty();
    }
}
```

**BooleanExpression의 장점:**
```java
// 재사용 가능
private BooleanExpression isAdult() {
    return QUser.user.age.goe(18);
}

private BooleanExpression isActive() {
    return QUser.user.status.eq(UserStatus.ACTIVE);
}

// 조합 가능
public List<User> findActiveAdults() {
    return queryFactory
            .selectFrom(QUser.user)
            .where(isActive(), isAdult())  // 조건 조합
            .fetch();
}
```

### 3️⃣ 고급: JOIN, Projection, 집계

#### JOIN 쿼리

```java
@Repository
@RequiredArgsConstructor
public class PostQueryRepository {

    private final JPAQueryFactory queryFactory;

    // 1. Inner Join
    public List<Post> findPostsWithUser() {
        QPost post = QPost.post;
        QUser user = QUser.user;

        return queryFactory
                .selectFrom(post)
                .join(post.user, user)  // Inner Join
                .where(user.status.eq(UserStatus.ACTIVE))
                .fetch();
    }

    // 2. Fetch Join (N+1 해결)
    public List<Post> findPostsWithUserFetch() {
        QPost post = QPost.post;
        QUser user = QUser.user;

        return queryFactory
                .selectFrom(post)
                .join(post.user, user).fetchJoin()  // Fetch Join
                .fetch();
    }

    // 3. Left Join
    public List<Post> findAllPostsWithUser() {
        QPost post = QPost.post;
        QUser user = QUser.user;

        return queryFactory
                .selectFrom(post)
                .leftJoin(post.user, user)  // Left Outer Join
                .fetch();
    }

    // 4. 복잡한 Join
    public List<Post> findPostsWithCommentsAndUsers() {
        QPost post = QPost.post;
        QUser user = QUser.user;
        QComment comment = QComment.comment;

        return queryFactory
                .selectFrom(post)
                .join(post.user, user).fetchJoin()
                .leftJoin(post.comments, comment).fetchJoin()
                .distinct()  // 중복 제거
                .fetch();
    }
}
```

#### Projection (DTO 직접 조회)

```java
// DTO 클래스
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserDto {
    private Long id;
    private String name;
    private String email;
}

@Repository
@RequiredArgsConstructor
public class UserQueryRepository {

    private final JPAQueryFactory queryFactory;

    // 1. Projections.bean (Setter 사용)
    public List<UserDto> findUserDtos1() {
        QUser user = QUser.user;

        return queryFactory
                .select(Projections.bean(UserDto.class,
                    user.id,
                    user.name,
                    user.email))
                .from(user)
                .fetch();
    }

    // 2. Projections.fields (필드 직접 접근)
    public List<UserDto> findUserDtos2() {
        QUser user = QUser.user;

        return queryFactory
                .select(Projections.fields(UserDto.class,
                    user.id,
                    user.name,
                    user.email))
                .from(user)
                .fetch();
    }

    // 3. Projections.constructor (생성자 사용) - 권장
    public List<UserDto> findUserDtos3() {
        QUser user = QUser.user;

        return queryFactory
                .select(Projections.constructor(UserDto.class,
                    user.id,
                    user.name,
                    user.email))
                .from(user)
                .fetch();
    }

    // 4. @QueryProjection (컴파일 타임 체크) - 최고 권장
    public List<UserDto> findUserDtos4() {
        QUser user = QUser.user;

        return queryFactory
                .select(new QUserDto(user.id, user.name, user.email))
                .from(user)
                .fetch();
    }
}

// @QueryProjection 사용을 위한 DTO
@Data
public class UserDto {
    private Long id;
    private String name;
    private String email;

    @QueryProjection  // Q클래스 생성
    public UserDto(Long id, String name, String email) {
        this.id = id;
        this.name = name;
        this.email = email;
    }
}
```

#### 집계 쿼리

```java
@Repository
@RequiredArgsConstructor
public class UserStatRepository {

    private final JPAQueryFactory queryFactory;

    // 1. COUNT, SUM, AVG
    public UserStat getUserStatistics() {
        QUser user = QUser.user;

        return queryFactory
                .select(Projections.constructor(UserStat.class,
                    user.count(),
                    user.age.sum(),
                    user.age.avg(),
                    user.age.max(),
                    user.age.min()))
                .from(user)
                .fetchOne();
    }

    // 2. GROUP BY
    public List<UserCountByStatus> countByStatus() {
        QUser user = QUser.user;

        return queryFactory
                .select(Projections.constructor(UserCountByStatus.class,
                    user.status,
                    user.count()))
                .from(user)
                .groupBy(user.status)
                .fetch();
    }

    // 3. HAVING
    public List<UserCountByStatus> findStatusWithMoreThan10Users() {
        QUser user = QUser.user;

        return queryFactory
                .select(Projections.constructor(UserCountByStatus.class,
                    user.status,
                    user.count()))
                .from(user)
                .groupBy(user.status)
                .having(user.count().gt(10))  // COUNT(*) > 10
                .fetch();
    }
}

@Data
@AllArgsConstructor
class UserStat {
    private Long count;
    private Long sumAge;
    private Double avgAge;
    private Integer maxAge;
    private Integer minAge;
}

@Data
@AllArgsConstructor
class UserCountByStatus {
    private UserStatus status;
    private Long count;
}
```

---

## 🛠️ 기본 실습: 블로그 검색 시스템

### 요구사항

- 제목/내용으로 검색
- 작성자별 검색
- 날짜 범위 검색
- 조회수 정렬
- 페이징 처리

### Step 1: Entity

```java
@Entity
@Table(name = "posts")
@Getter @Setter
@NoArgsConstructor
public class Post extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    private User user;

    private String title;

    @Column(columnDefinition = "TEXT")
    private String content;

    private Integer viewCount = 0;

    @Enumerated(EnumType.STRING)
    private PostStatus status;

    @Builder
    public Post(User user, String title, String content, PostStatus status) {
        this.user = user;
        this.title = title;
        this.content = content;
        this.status = status;
        this.viewCount = 0;
    }
}
```

### Step 2: 검색 조건 DTO

```java
@Data
public class PostSearchCondition {
    private String keyword;        // 제목 또는 내용
    private String author;         // 작성자
    private PostStatus status;
    private LocalDateTime startDate;
    private LocalDateTime endDate;
    private Integer minViewCount;
    private Integer maxViewCount;
}
```

### Step 3: QueryDSL Repository

```java
@Repository
@RequiredArgsConstructor
public class PostQueryRepository {

    private final JPAQueryFactory queryFactory;

    /**
     * 복잡한 검색 조건으로 게시글 조회
     */
    public Page<Post> search(PostSearchCondition condition, Pageable pageable) {
        QPost post = QPost.post;
        QUser user = QUser.user;

        // 쿼리 실행
        List<Post> content = queryFactory
                .selectFrom(post)
                .join(post.user, user).fetchJoin()
                .where(
                    keywordContains(condition.getKeyword()),
                    authorEq(condition.getAuthor()),
                    statusEq(condition.getStatus()),
                    createdAtBetween(condition.getStartDate(), condition.getEndDate()),
                    viewCountBetween(condition.getMinViewCount(), condition.getMaxViewCount())
                )
                .orderBy(getOrderSpecifier(pageable))
                .offset(pageable.getOffset())
                .limit(pageable.getPageSize())
                .fetch();

        // 전체 개수 조회
        Long total = queryFactory
                .select(post.count())
                .from(post)
                .where(
                    keywordContains(condition.getKeyword()),
                    authorEq(condition.getAuthor()),
                    statusEq(condition.getStatus()),
                    createdAtBetween(condition.getStartDate(), condition.getEndDate()),
                    viewCountBetween(condition.getMinViewCount(), condition.getMaxViewCount())
                )
                .fetchOne();

        return new PageImpl<>(content, pageable, total);
    }

    /**
     * 인기 게시글 조회 (조회수 TOP N)
     */
    public List<Post> findPopularPosts(int limit) {
        QPost post = QPost.post;
        QUser user = QUser.user;

        return queryFactory
                .selectFrom(post)
                .join(post.user, user).fetchJoin()
                .where(post.status.eq(PostStatus.PUBLISHED))
                .orderBy(post.viewCount.desc(), post.createdAt.desc())
                .limit(limit)
                .fetch();
    }

    /**
     * 작성자별 게시글 수 통계
     */
    public List<PostCountByAuthor> countByAuthor() {
        QPost post = QPost.post;
        QUser user = QUser.user;

        return queryFactory
                .select(Projections.constructor(PostCountByAuthor.class,
                    user.name,
                    post.count()))
                .from(post)
                .join(post.user, user)
                .where(post.status.eq(PostStatus.PUBLISHED))
                .groupBy(user.name)
                .orderBy(post.count().desc())
                .fetch();
    }

    /**
     * 일별 게시글 수 통계
     */
    public List<PostCountByDate> countByDate(LocalDateTime startDate, LocalDateTime endDate) {
        QPost post = QPost.post;

        return queryFactory
                .select(Projections.constructor(PostCountByDate.class,
                    post.createdAt.date(),
                    post.count()))
                .from(post)
                .where(
                    post.createdAt.between(startDate, endDate),
                    post.status.eq(PostStatus.PUBLISHED)
                )
                .groupBy(post.createdAt.date())
                .orderBy(post.createdAt.date().desc())
                .fetch();
    }

    // ========== 재사용 가능한 조건 메서드 ==========

    private BooleanExpression keywordContains(String keyword) {
        if (!hasText(keyword)) return null;

        QPost post = QPost.post;
        return post.title.contains(keyword)
                .or(post.content.contains(keyword));
    }

    private BooleanExpression authorEq(String author) {
        if (!hasText(author)) return null;

        QUser user = QUser.user;
        return user.name.eq(author);
    }

    private BooleanExpression statusEq(PostStatus status) {
        return status != null ? QPost.post.status.eq(status) : null;
    }

    private BooleanExpression createdAtBetween(LocalDateTime start, LocalDateTime end) {
        if (start == null && end == null) return null;

        QPost post = QPost.post;

        if (start != null && end != null) {
            return post.createdAt.between(start, end);
        } else if (start != null) {
            return post.createdAt.goe(start);
        } else {
            return post.createdAt.loe(end);
        }
    }

    private BooleanExpression viewCountBetween(Integer min, Integer max) {
        if (min == null && max == null) return null;

        QPost post = QPost.post;

        if (min != null && max != null) {
            return post.viewCount.between(min, max);
        } else if (min != null) {
            return post.viewCount.goe(min);
        } else {
            return post.viewCount.loe(max);
        }
    }

    private OrderSpecifier<?>[] getOrderSpecifier(Pageable pageable) {
        QPost post = QPost.post;

        return pageable.getSort().stream()
                .map(order -> {
                    Order direction = order.isAscending() ? Order.ASC : Order.DESC;
                    String property = order.getProperty();

                    return switch (property) {
                        case "createdAt" -> new OrderSpecifier<>(direction, post.createdAt);
                        case "viewCount" -> new OrderSpecifier<>(direction, post.viewCount);
                        case "title" -> new OrderSpecifier<>(direction, post.title);
                        default -> new OrderSpecifier<>(direction, post.createdAt);
                    };
                })
                .toArray(OrderSpecifier[]::new);
    }

    private boolean hasText(String str) {
        return str != null && !str.isEmpty();
    }
}

// 통계 DTO
@Data
@AllArgsConstructor
class PostCountByAuthor {
    private String author;
    private Long count;
}

@Data
@AllArgsConstructor
class PostCountByDate {
    private LocalDate date;
    private Long count;
}
```

### Step 4: Service

```java
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PostQueryService {

    private final PostQueryRepository postQueryRepository;

    public Page<PostDto> searchPosts(PostSearchCondition condition, Pageable pageable) {
        Page<Post> posts = postQueryRepository.search(condition, pageable);

        return posts.map(post -> PostDto.builder()
                .id(post.getId())
                .title(post.getTitle())
                .content(post.getContent())
                .author(post.getUser().getName())
                .viewCount(post.getViewCount())
                .createdAt(post.getCreatedAt())
                .build());
    }

    public List<PostDto> getPopularPosts(int limit) {
        return postQueryRepository.findPopularPosts(limit).stream()
                .map(post -> PostDto.builder()
                        .id(post.getId())
                        .title(post.getTitle())
                        .author(post.getUser().getName())
                        .viewCount(post.getViewCount())
                        .build())
                .collect(Collectors.toList());
    }

    public List<PostCountByAuthor> getPostCountByAuthor() {
        return postQueryRepository.countByAuthor();
    }

    public List<PostCountByDate> getPostCountByDate(LocalDateTime start, LocalDateTime end) {
        return postQueryRepository.countByDate(start, end);
    }
}
```

### Step 5: Controller

```java
@RestController
@RequestMapping("/api/posts")
@RequiredArgsConstructor
public class PostSearchController {

    private final PostQueryService postQueryService;

    @GetMapping("/search")
    public ResponseEntity<Page<PostDto>> searchPosts(
            @ModelAttribute PostSearchCondition condition,
            @PageableDefault(size = 10, sort = "createdAt", direction = Sort.Direction.DESC) Pageable pageable) {

        Page<PostDto> posts = postQueryService.searchPosts(condition, pageable);
        return ResponseEntity.ok(posts);
    }

    @GetMapping("/popular")
    public ResponseEntity<List<PostDto>> getPopularPosts(
            @RequestParam(defaultValue = "10") int limit) {

        List<PostDto> posts = postQueryService.getPopularPosts(limit);
        return ResponseEntity.ok(posts);
    }

    @GetMapping("/stats/by-author")
    public ResponseEntity<List<PostCountByAuthor>> getStatsByAuthor() {
        List<PostCountByAuthor> stats = postQueryService.getPostCountByAuthor();
        return ResponseEntity.ok(stats);
    }

    @GetMapping("/stats/by-date")
    public ResponseEntity<List<PostCountByDate>> getStatsByDate(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime start,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime end) {

        List<PostCountByDate> stats = postQueryService.getPostCountByDate(start, end);
        return ResponseEntity.ok(stats);
    }
}
```

### Step 6: 테스트

```java
@SpringBootTest
@Transactional
class PostQueryRepositoryTest {

    @Autowired
    private PostQueryRepository postQueryRepository;

    @Autowired
    private EntityManager em;

    @BeforeEach
    void setUp() {
        // 테스트 데이터 준비
        User user1 = User.builder().name("홍길동").email("hong@example.com").build();
        User user2 = User.builder().name("김철수").email("kim@example.com").build();
        em.persist(user1);
        em.persist(user2);

        for (int i = 1; i <= 20; i++) {
            Post post = Post.builder()
                    .user(i % 2 == 0 ? user1 : user2)
                    .title("제목 " + i)
                    .content("내용 " + i)
                    .status(PostStatus.PUBLISHED)
                    .build();
            post.setViewCount(i * 10);
            em.persist(post);
        }

        em.flush();
        em.clear();
    }

    @Test
    void 키워드_검색() {
        // Given
        PostSearchCondition condition = new PostSearchCondition();
        condition.setKeyword("제목 1");

        // When
        Page<Post> result = postQueryRepository.search(condition, PageRequest.of(0, 10));

        // Then
        assertThat(result.getContent()).hasSize(10);  // 제목 1, 10, 11, ..., 19
    }

    @Test
    void 조회수_범위_검색() {
        // Given
        PostSearchCondition condition = new PostSearchCondition();
        condition.setMinViewCount(50);
        condition.setMaxViewCount(150);

        // When
        Page<Post> result = postQueryRepository.search(condition, PageRequest.of(0, 10));

        // Then
        assertThat(result.getContent())
                .allMatch(post -> post.getViewCount() >= 50 && post.getViewCount() <= 150);
    }

    @Test
    void 인기_게시글_조회() {
        // When
        List<Post> result = postQueryRepository.findPopularPosts(5);

        // Then
        assertThat(result).hasSize(5);
        assertThat(result.get(0).getViewCount()).isGreaterThanOrEqualTo(result.get(1).getViewCount());
    }

    @Test
    void 작성자별_통계() {
        // When
        List<PostCountByAuthor> result = postQueryRepository.countByAuthor();

        // Then
        assertThat(result).hasSize(2);
        assertThat(result.get(0).getCount() + result.get(1).getCount()).isEqualTo(20);
    }
}
```

---

## 🏢 기업 사례: 쿠팡

### 배경

쿠팡은 복잡한 상품 검색 시스템을 운영합니다.

**요구사항:**
- 다양한 필터 조건 (카테고리, 가격, 배송, 리뷰 등)
- 정렬 옵션 (인기도, 가격, 최신순)
- 실시간 재고 반영
- 성능 최적화 필수

### QueryDSL 활용

```java
public Page<Product> searchProducts(ProductSearchCondition condition, Pageable pageable) {
    QProduct product = QProduct.product;
    QCategory category = QCategory.category;

    return queryFactory
            .selectFrom(product)
            .join(product.category, category).fetchJoin()
            .where(
                categoryIn(condition.getCategories()),
                priceBetween(condition.getMinPrice(), condition.getMaxPrice()),
                ratingGoe(condition.getMinRating()),
                rocketDeliveryEq(condition.isRocketDelivery()),
                inStock()
            )
            .orderBy(getOrderSpecifier(condition.getSortBy()))
            .offset(pageable.getOffset())
            .limit(pageable.getPageSize())
            .fetch();
}
```

**성과:**
- 검색 쿼리 성능 30% 향상
- 코드 유지보수성 50% 개선
- 신규 필터 추가 시간 70% 단축

---

## ❓ FAQ

### Q1. QueryDSL은 언제 사용해야 하나요?

**A:**

| 상황 | 권장 기술 |
|-----|----------|
| 단순 CRUD | Spring Data JPA Query Method |
| 동적 쿼리, 복잡한 조건 | QueryDSL |
| 복잡한 통계, 네이티브 기능 | Native Query 또는 MyBatis |

```java
// Simple → Query Method
List<User> findByNameAndEmail(String name, String email);

// Complex → QueryDSL
public List<User> searchUsers(UserSearchCondition condition) {
    return queryFactory
            .selectFrom(user)
            .where(/* 10개 이상의 동적 조건 */)
            .fetch();
}
```

### Q2. Fetch Join vs일반 Join의 차이는?

**A:**

```java
// ❌ 일반 Join - N+1 문제 발생
List<Post> posts = queryFactory
        .selectFrom(post)
        .join(post.user, user)  // User는 로드되지 않음
        .fetch();

for (Post p : posts) {
    p.getUser().getName();  // 각각 SELECT 쿼리 발생!
}

// ✅ Fetch Join - 한 번에 로드
List<Post> posts = queryFactory
        .selectFrom(post)
        .join(post.user, user).fetchJoin()  // User도 함께 로드
        .fetch();

for (Post p : posts) {
    p.getUser().getName();  // 추가 쿼리 없음
}
```

### Q3. Projection 방식 중 어떤 것을 선택해야 하나요?

**A:**

```java
// 1. Projections.constructor - 범용적
queryFactory.select(Projections.constructor(UserDto.class, user.id, user.name))

// 2. @QueryProjection - 타입 안전 (권장!)
queryFactory.select(new QUserDto(user.id, user.name))

// 장점: 컴파일 타임 체크
// 단점: DTO가 QueryDSL에 의존
```

**권장 전략:**
- 내부 DTO: `@QueryProjection` 사용
- API 응답 DTO: `Projections.constructor` 사용

### Q4. BooleanBuilder vs BooleanExpression?

**A:**

```java
// BooleanBuilder - 간단하지만 재사용 어려움
BooleanBuilder builder = new BooleanBuilder();
if (name != null) builder.and(user.name.eq(name));
if (email != null) builder.and(user.email.eq(email));

// BooleanExpression - 재사용 가능 (권장!)
private BooleanExpression nameEq(String name) {
    return name != null ? user.name.eq(name) : null;
}

// 조합 가능
private BooleanExpression isActiveAdult() {
    return isActive().and(isAdult());
}
```

### Q5. QueryDSL과 Hibernate 캐시는 어떻게 작동하나요?

**A:**

```java
// 1차 캐시 (영속성 컨텍스트)는 정상 작동
User user1 = queryFactory.selectFrom(QUser.user).where(QUser.user.id.eq(1L)).fetchOne();
User user2 = em.find(User.class, 1L);
assertThat(user1 == user2).isTrue();  // 동일한 객체

// 2차 캐시 사용 시 설정 필요
queryFactory.selectFrom(QUser.user)
        .where(QUser.user.id.eq(1L))
        .setHint("org.hibernate.cacheable", true)
        .fetchOne();
```

---

## 💼 면접 질문 TOP 5

### ⭐ 초급 1: QueryDSL의 장점은?

**답변:**
1. **타입 안전성**: 컴파일 타임에 오류 검출
2. **IDE 지원**: 자동완성으로 생산성 향상
3. **동적 쿼리**: 조건에 따라 쿼리 동적 생성
4. **리팩토링 안전**: 필드명 변경 시 자동 반영

### ⭐ 초급 2: QClass는 무엇이고 어떻게 생성되나요?

**답변:**
Entity 클래스를 기반으로 자동 생성되는 쿼리 타입 클래스입니다.

```bash
./gradlew compileJava
→ build/generated/querydsl/QUser.java 생성
```

### ⭐⭐ 중급 1: BooleanExpression의 장점은?

**답변:**
재사용 가능하고 조합 가능한 조건식을 만들 수 있습니다.

```java
private BooleanExpression isActive() {
    return user.status.eq(ACTIVE);
}

private BooleanExpression isAdult() {
    return user.age.goe(18);
}

// 조합
queryFactory.selectFrom(user)
        .where(isActive(), isAdult())
```

### ⭐⭐ 중급 2: Fetch Join을 사용하는 이유는?

**답변:**
N+1 문제를 해결하기 위함입니다.

```java
// N+1 발생
queryFactory.selectFrom(post).fetch();
for (Post p : posts) {
    p.getUser().getName();  // N번 SELECT
}

// 해결
queryFactory.selectFrom(post)
        .join(post.user, user).fetchJoin()  // 1번 SELECT
        .fetch();
```

### ⭐⭐ 중급 3: 동적 쿼리에서 null 조건은 어떻게 처리하나요?

**답변:**
null을 반환하면 where 절에서 자동으로 무시됩니다.

```java
private BooleanExpression nameEq(String name) {
    return name != null ? user.name.eq(name) : null;
}

queryFactory.selectFrom(user)
        .where(nameEq(null))  // WHERE 절에 조건 추가 안 됨
        .fetch();
```

---

## 🎯 다음 단계

QueryDSL을 마쳤다면:

1. **28장: MyBatis 연동** - 복잡한 SQL 처리
2. **성능 최적화** - 쿼리 성능 튜닝
3. **QueryDSL SQL** - Native Query를 타입 안전하게
4. **동적 정렬/페이징** - 고급 기법
5. **실전 프로젝트** - 대용량 검색 시스템 구축

---

**🎓 학습 완료 체크리스트:**

- [ ] QueryDSL 개념과 설정
- [ ] QClass 생성 및 활용
- [ ] 동적 쿼리 작성 (BooleanExpression)
- [ ] JOIN 및 Fetch Join
- [ ] Projection으로 DTO 조회
- [ ] 집계 쿼리 작성
- [ ] 블로그 검색 시스템 실습 완료

**다음 장에서는 MyBatis로 복잡한 SQL을 효과적으로 관리하는 방법을 배웁니다!** 🚀
