# 28장: MyBatis 연동 - SQL 중심 개발의 완성

> **"복잡한 SQL을 자유롭게, 그러나 체계적으로 관리하세요"**

---

## 📋 학습 목표

이 장을 학습하면 다음을 할 수 있습니다:

- MyBatis의 개념과 장점을 이해합니다
- Spring Boot에 MyBatis를 설정하고 연동할 수 있습니다
- Mapper XML과 Annotation을 활용하여 쿼리를 작성합니다
- 동적 SQL로 복잡한 조건을 처리합니다
- ResultMap으로 복잡한 객체 매핑을 구현합니다
- JPA와 MyBatis를 적절히 혼용하는 전략을 수립합니다

**예상 학습 시간**: 4-5시간
**난이도**: ⭐⭐⭐ (중급)

---

## 🤔 왜 MyBatis가 필요한가?

### 문제 상황: JPA의 한계

#### 문제 1: 복잡한 통계 쿼리

```java
// JPA로 작성하기 어려운 쿼리
// "월별 매출 통계를 카테고리별로 집계하고, 전월 대비 증감률 계산"

@Query(value = """
    SELECT
        DATE_FORMAT(o.created_at, '%Y-%m') as month,
        c.name as category,
        SUM(oi.price * oi.quantity) as total_sales,
        COUNT(DISTINCT o.id) as order_count,
        LAG(SUM(oi.price * oi.quantity)) OVER (
            PARTITION BY c.id ORDER BY DATE_FORMAT(o.created_at, '%Y-%m')
        ) as prev_month_sales
    FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    JOIN products p ON oi.product_id = p.id
    JOIN categories c ON p.category_id = c.id
    WHERE o.status = 'COMPLETED'
    GROUP BY DATE_FORMAT(o.created_at, '%Y-%m'), c.id
    ORDER BY month DESC, total_sales DESC
    """, nativeQuery = true)
List<Object[]> getMonthlySalesStatistics();
// → 복잡한 Native Query, Object[] 반환으로 타입 안정성 없음
```

#### 문제 2: 대용량 데이터 처리

```java
// JPA - 모든 데이터를 메모리에 로드
List<Order> orders = orderRepository.findAll();  // 100만 건이면?
for (Order order : orders) {
    // 처리 중 OutOfMemoryError 발생 가능
}
```

#### 문제 3: 레거시 SQL 활용

```
기존 시스템:
- 수년간 최적화된 복잡한 SQL 쿼리 보유
- 수백 개의 프로시저와 함수
- 특정 DB 기능에 의존 (Oracle CONNECT BY, MySQL FULLTEXT 등)

→ JPA로 재작성하기 어려움
```

### MyBatis의 해결책

```xml
<!-- MyBatis - SQL을 자유롭게 작성 -->
<select id="getMonthlySalesStatistics" resultType="MonthlySalesDto">
    SELECT
        DATE_FORMAT(o.created_at, '%Y-%m') as month,
        c.name as category,
        SUM(oi.price * oi.quantity) as totalSales,
        COUNT(DISTINCT o.id) as orderCount,
        LAG(SUM(oi.price * oi.quantity)) OVER (
            PARTITION BY c.id ORDER BY DATE_FORMAT(o.created_at, '%Y-%m')
        ) as prevMonthSales
    FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    JOIN products p ON oi.product_id = p.id
    JOIN categories c ON p.category_id = c.id
    WHERE o.status = 'COMPLETED'
    GROUP BY DATE_FORMAT(o.created_at, '%Y-%m'), c.id
    ORDER BY month DESC, totalSales DESC
</select>
```

```java
// Java 인터페이스 - 타입 안전하게 호출
List<MonthlySalesDto> statistics = salesMapper.getMonthlySalesStatistics();
```

**MyBatis의 핵심 가치:**
- SQL을 자유롭게 작성 → 복잡한 쿼리도 가능
- XML 분리로 가독성 향상 → 유지보수 용이
- 대용량 처리 지원 → 메모리 효율적
- 레거시 SQL 활용 → 기존 자산 재사용

---

## 🌍 실생활 비유로 이해하는 MyBatis

### 비유 1: 자동차 vs 오토바이

**JPA (자동차):**
```
- 편안하고 안전
- 정해진 도로(ORM 매핑)에서 운행
- 복잡한 지형(복잡한 쿼리)에서는 제약
```

**MyBatis (오토바이):**
```
- 좁은 길(복잡한 SQL)도 자유롭게 이동
- 운전자가 직접 제어
- 숙련도 필요하지만 유연함
```

### 비유 2: 기성복 vs 맞춤 정장

**JPA (기성복):**
```
- 빠르게 입을 수 있음
- 대부분의 상황에 적합
- 특수한 경우 맞지 않을 수 있음
```

**MyBatis (맞춤 정장):**
```
- 원하는 대로 디자인 가능
- 시간이 걸리지만 완벽한 핏
- 복잡한 요구사항 대응 가능
```

### 비유 3: 번역기 vs 통역사

**JPA (번역기):**
```
객체 → 자동 변환 → SQL
"User를 조회해줘" → "SELECT * FROM users"
→ 간단하지만 복잡한 표현은 제한적
```

**MyBatis (통역사):**
```
개발자가 직접 작성 → SQL 그대로 실행
"이 복잡한 통계 쿼리를 실행해줘" → 그대로 실행
→ 자유롭지만 개발자가 정확히 알아야 함
```

---

## 💡 MyBatis 핵심 개념

### 1️⃣ 초급: MyBatis 설정

#### 의존성 추가

```gradle
// build.gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.mybatis.spring.boot:mybatis-spring-boot-starter:3.0.3'

    // Database
    runtimeOnly 'com.mysql.cj:mysql-connector-j'

    // Lombok (선택)
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'

    // Test
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'org.mybatis.spring.boot:mybatis-spring-boot-starter-test:3.0.3'
}
```

#### application.yml 설정

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?serverTimezone=Asia/Seoul
    username: root
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver

mybatis:
  # Mapper XML 파일 위치
  mapper-locations: classpath:mybatis/mapper/**/*.xml

  # Type Alias 설정 (패키지 경로 생략 가능)
  type-aliases-package: com.example.demo.dto

  # 설정 파일 위치 (선택)
  config-location: classpath:mybatis/mybatis-config.xml

  configuration:
    # 카멜케이스 자동 변환 (user_name → userName)
    map-underscore-to-camel-case: true

    # 쿼리 로그 출력 레벨
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl

    # null 값 처리
    jdbc-type-for-null: NULL

    # 지연 로딩 설정
    lazy-loading-enabled: true
    aggressive-lazy-loading: false

# SQL 로그 (선택)
logging:
  level:
    com.example.demo.mapper: DEBUG
```

#### 디렉토리 구조

```
src/main/
├── java/
│   └── com/example/demo/
│       ├── controller/
│       ├── service/
│       ├── mapper/          ← Mapper 인터페이스
│       │   └── UserMapper.java
│       ├── dto/
│       │   └── UserDto.java
│       └── DemoApplication.java
└── resources/
    ├── mybatis/
    │   ├── mapper/          ← Mapper XML
    │   │   └── UserMapper.xml
    │   └── mybatis-config.xml (선택)
    └── application.yml
```

### 2️⃣ 중급: Mapper 인터페이스와 XML

#### Mapper 인터페이스

```java
package com.example.demo.mapper;

import com.example.demo.dto.UserDto;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper  // MyBatis Mapper 인터페이스 선언
public interface UserMapper {

    // 1. XML에 정의된 쿼리 매핑
    List<UserDto> findAll();

    UserDto findById(Long id);

    void insert(UserDto user);

    void update(UserDto user);

    void delete(Long id);

    // 2. Annotation 방식 (간단한 쿼리)
    @Select("SELECT * FROM users WHERE email = #{email}")
    UserDto findByEmail(String email);

    @Select("SELECT COUNT(*) FROM users WHERE status = #{status}")
    long countByStatus(String status);

    @Insert("INSERT INTO users (name, email, status) VALUES (#{name}, #{email}, #{status})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    void insertWithAnnotation(UserDto user);

    @Update("UPDATE users SET name = #{name}, email = #{email} WHERE id = #{id}")
    void updateWithAnnotation(UserDto user);

    @Delete("DELETE FROM users WHERE id = #{id}")
    void deleteWithAnnotation(Long id);
}
```

#### Mapper XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<mapper namespace="com.example.demo.mapper.UserMapper">

    <!-- 1. 기본 CRUD -->

    <!-- 전체 조회 -->
    <select id="findAll" resultType="UserDto">
        SELECT id, name, email, status, created_at, updated_at
        FROM users
        ORDER BY created_at DESC
    </select>

    <!-- ID로 조회 -->
    <select id="findById" parameterType="long" resultType="UserDto">
        SELECT id, name, email, status, created_at, updated_at
        FROM users
        WHERE id = #{id}
    </select>

    <!-- 삽입 -->
    <insert id="insert" parameterType="UserDto" useGeneratedKeys="true" keyProperty="id">
        INSERT INTO users (name, email, status, created_at)
        VALUES (#{name}, #{email}, #{status}, NOW())
    </insert>

    <!-- 수정 -->
    <update id="update" parameterType="UserDto">
        UPDATE users
        SET name = #{name},
            email = #{email},
            status = #{status},
            updated_at = NOW()
        WHERE id = #{id}
    </update>

    <!-- 삭제 -->
    <delete id="delete" parameterType="long">
        DELETE FROM users
        WHERE id = #{id}
    </delete>

</mapper>
```

#### DTO 클래스

```java
package com.example.demo.dto;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class UserDto {
    private Long id;
    private String name;
    private String email;
    private String status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
```

#### Service 계층

```java
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserMapper userMapper;

    public List<UserDto> getAllUsers() {
        return userMapper.findAll();
    }

    public UserDto getUser(Long id) {
        return userMapper.findById(id);
    }

    @Transactional
    public void createUser(UserDto user) {
        userMapper.insert(user);
        // user.getId()에 생성된 ID가 자동 설정됨
    }

    @Transactional
    public void updateUser(UserDto user) {
        userMapper.update(user);
    }

    @Transactional
    public void deleteUser(Long id) {
        userMapper.delete(id);
    }
}
```

### 3️⃣ 고급: 동적 SQL

#### if 태그

```xml
<select id="search" parameterType="UserSearchCondition" resultType="UserDto">
    SELECT * FROM users
    WHERE 1=1
    <if test="name != null and name != ''">
        AND name LIKE CONCAT('%', #{name}, '%')
    </if>
    <if test="email != null and email != ''">
        AND email = #{email}
    </if>
    <if test="status != null">
        AND status = #{status}
    </if>
    ORDER BY created_at DESC
</select>
```

#### choose, when, otherwise (switch-case)

```xml
<select id="searchWithSorting" resultType="UserDto">
    SELECT * FROM users
    WHERE status = #{status}
    ORDER BY
    <choose>
        <when test="sortBy == 'name'">
            name ASC
        </when>
        <when test="sortBy == 'email'">
            email ASC
        </when>
        <when test="sortBy == 'createdAt'">
            created_at DESC
        </when>
        <otherwise>
            id DESC
        </otherwise>
    </choose>
</select>
```

#### where 태그 (WHERE 1=1 제거)

```xml
<select id="searchAdvanced" resultType="UserDto">
    SELECT * FROM users
    <where>
        <if test="name != null">
            AND name LIKE CONCAT('%', #{name}, '%')
        </if>
        <if test="email != null">
            AND email = #{email}
        </if>
        <if test="status != null">
            AND status = #{status}
        </if>
    </where>
    ORDER BY created_at DESC
</select>
<!-- WHERE 절이 없으면 WHERE 키워드 생략, 첫 AND 자동 제거 -->
```

#### set 태그 (UPDATE 동적 생성)

```xml
<update id="updateSelective" parameterType="UserDto">
    UPDATE users
    <set>
        <if test="name != null">name = #{name},</if>
        <if test="email != null">email = #{email},</if>
        <if test="status != null">status = #{status},</if>
        updated_at = NOW()
    </set>
    WHERE id = #{id}
</update>
<!-- 마지막 쉼표 자동 제거 -->
```

#### foreach 태그 (IN 절)

```xml
<!-- 1. List 파라미터 -->
<select id="findByIds" resultType="UserDto">
    SELECT * FROM users
    WHERE id IN
    <foreach item="id" collection="list" open="(" separator="," close=")">
        #{id}
    </foreach>
</select>

<!-- 2. Batch Insert -->
<insert id="insertBatch">
    INSERT INTO users (name, email, status)
    VALUES
    <foreach item="user" collection="list" separator=",">
        (#{user.name}, #{user.email}, #{user.status})
    </foreach>
</insert>
```

**사용 예시:**
```java
// Mapper 인터페이스
List<UserDto> findByIds(@Param("list") List<Long> ids);
void insertBatch(@Param("list") List<UserDto> users);

// Service
List<UserDto> users = userMapper.findByIds(Arrays.asList(1L, 2L, 3L));
// SELECT * FROM users WHERE id IN (1, 2, 3)

userMapper.insertBatch(userList);
// INSERT INTO users (name, email, status) VALUES
// ('User1', 'user1@example.com', 'ACTIVE'),
// ('User2', 'user2@example.com', 'ACTIVE'),
// ...
```

#### trim 태그 (커스텀 접두사/접미사)

```xml
<select id="searchWithTrim" resultType="UserDto">
    SELECT * FROM users
    <trim prefix="WHERE" prefixOverrides="AND |OR ">
        <if test="name != null">
            AND name = #{name}
        </if>
        <if test="email != null">
            AND email = #{email}
        </if>
    </trim>
</select>
```

---

## 🛠️ 기본 실습: 게시판 시스템

### 요구사항

- 복잡한 검색 조건 (제목, 내용, 작성자, 날짜 범위)
- 조회수 TOP 10
- 작성자별 게시글 수 통계
- 댓글 수 포함 조회
- 대용량 데이터 배치 처리

### Step 1: DTO 클래스

```java
@Data
public class PostDto {
    private Long id;
    private Long userId;
    private String userName;  // JOIN 결과
    private String title;
    private String content;
    private Integer viewCount;
    private Integer commentCount;  // 서브쿼리 결과
    private String status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}

@Data
public class PostSearchCondition {
    private String keyword;      // 제목 또는 내용
    private String author;
    private String status;
    private LocalDateTime startDate;
    private LocalDateTime endDate;
    private Integer minViewCount;
    private String sortBy;
    private String sortOrder;
}

@Data
@AllArgsConstructor
public class PostStatDto {
    private String author;
    private Long postCount;
    private Long totalViewCount;
    private Double avgViewCount;
}
```

### Step 2: Mapper 인터페이스

```java
@Mapper
public interface PostMapper {

    // 기본 CRUD
    List<PostDto> findAll();
    PostDto findById(Long id);
    void insert(PostDto post);
    void update(PostDto post);
    void delete(Long id);

    // 복잡한 검색
    List<PostDto> search(PostSearchCondition condition);
    long countSearch(PostSearchCondition condition);

    // 인기 게시글
    List<PostDto> findPopularPosts(@Param("limit") int limit);

    // 통계
    List<PostStatDto> getPostStatsByAuthor();

    // 배치 처리
    void insertBatch(@Param("list") List<PostDto> posts);

    // 조회수 증가
    void increaseViewCount(Long id);

    // 댓글 수 업데이트
    void updateCommentCount(Long postId);
}
```

### Step 3: Mapper XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<mapper namespace="com.example.demo.mapper.PostMapper">

    <!-- ResultMap 정의 -->
    <resultMap id="PostResultMap" type="PostDto">
        <id property="id" column="id"/>
        <result property="userId" column="user_id"/>
        <result property="userName" column="user_name"/>
        <result property="title" column="title"/>
        <result property="content" column="content"/>
        <result property="viewCount" column="view_count"/>
        <result property="commentCount" column="comment_count"/>
        <result property="status" column="status"/>
        <result property="createdAt" column="created_at"/>
        <result property="updatedAt" column="updated_at"/>
    </resultMap>

    <!-- 재사용 가능한 SQL 조각 -->
    <sql id="postColumns">
        p.id, p.user_id, p.title, p.content, p.view_count, p.status,
        p.created_at, p.updated_at,
        u.name as user_name
    </sql>

    <sql id="commentCountSubquery">
        (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id AND c.status = 'PUBLISHED') as comment_count
    </sql>

    <!-- 전체 조회 (JOIN + 서브쿼리) -->
    <select id="findAll" resultMap="PostResultMap">
        SELECT
            <include refid="postColumns"/>,
            <include refid="commentCountSubquery"/>
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.status = 'PUBLISHED'
        ORDER BY p.created_at DESC
    </select>

    <!-- ID로 조회 -->
    <select id="findById" parameterType="long" resultMap="PostResultMap">
        SELECT
            <include refid="postColumns"/>,
            <include refid="commentCountSubquery"/>
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = #{id}
    </select>

    <!-- 복잡한 동적 검색 -->
    <select id="search" parameterType="PostSearchCondition" resultMap="PostResultMap">
        SELECT
            <include refid="postColumns"/>,
            <include refid="commentCountSubquery"/>
        FROM posts p
        JOIN users u ON p.user_id = u.id
        <where>
            <if test="keyword != null and keyword != ''">
                AND (p.title LIKE CONCAT('%', #{keyword}, '%')
                     OR p.content LIKE CONCAT('%', #{keyword}, '%'))
            </if>
            <if test="author != null and author != ''">
                AND u.name = #{author}
            </if>
            <if test="status != null">
                AND p.status = #{status}
            </if>
            <if test="startDate != null">
                AND p.created_at &gt;= #{startDate}
            </if>
            <if test="endDate != null">
                AND p.created_at &lt;= #{endDate}
            </if>
            <if test="minViewCount != null">
                AND p.view_count &gt;= #{minViewCount}
            </if>
        </where>
        ORDER BY
        <choose>
            <when test="sortBy == 'viewCount'">
                p.view_count
            </when>
            <when test="sortBy == 'commentCount'">
                comment_count
            </when>
            <when test="sortBy == 'title'">
                p.title
            </when>
            <otherwise>
                p.created_at
            </otherwise>
        </choose>
        <choose>
            <when test="sortOrder == 'ASC'">
                ASC
            </when>
            <otherwise>
                DESC
            </otherwise>
        </choose>
    </select>

    <!-- 검색 결과 카운트 -->
    <select id="countSearch" parameterType="PostSearchCondition" resultType="long">
        SELECT COUNT(*)
        FROM posts p
        JOIN users u ON p.user_id = u.id
        <where>
            <if test="keyword != null and keyword != ''">
                AND (p.title LIKE CONCAT('%', #{keyword}, '%')
                     OR p.content LIKE CONCAT('%', #{keyword}, '%'))
            </if>
            <if test="author != null and author != ''">
                AND u.name = #{author}
            </if>
            <if test="status != null">
                AND p.status = #{status}
            </if>
            <if test="startDate != null">
                AND p.created_at &gt;= #{startDate}
            </if>
            <if test="endDate != null">
                AND p.created_at &lt;= #{endDate}
            </if>
            <if test="minViewCount != null">
                AND p.view_count &gt;= #{minViewCount}
            </if>
        </where>
    </select>

    <!-- 인기 게시글 TOP N -->
    <select id="findPopularPosts" resultMap="PostResultMap">
        SELECT
            <include refid="postColumns"/>,
            <include refid="commentCountSubquery"/>
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.status = 'PUBLISHED'
        ORDER BY p.view_count DESC, p.created_at DESC
        LIMIT #{limit}
    </select>

    <!-- 작성자별 통계 -->
    <select id="getPostStatsByAuthor" resultType="PostStatDto">
        SELECT
            u.name as author,
            COUNT(p.id) as postCount,
            SUM(p.view_count) as totalViewCount,
            AVG(p.view_count) as avgViewCount
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.status = 'PUBLISHED'
        GROUP BY u.id, u.name
        HAVING COUNT(p.id) &gt; 0
        ORDER BY postCount DESC, totalViewCount DESC
    </select>

    <!-- 삽입 -->
    <insert id="insert" parameterType="PostDto" useGeneratedKeys="true" keyProperty="id">
        INSERT INTO posts (user_id, title, content, status, view_count, created_at)
        VALUES (#{userId}, #{title}, #{content}, #{status}, 0, NOW())
    </insert>

    <!-- 배치 삽입 -->
    <insert id="insertBatch">
        INSERT INTO posts (user_id, title, content, status, view_count, created_at)
        VALUES
        <foreach item="post" collection="list" separator=",">
            (#{post.userId}, #{post.title}, #{post.content}, #{post.status}, 0, NOW())
        </foreach>
    </insert>

    <!-- 선택적 업데이트 -->
    <update id="update" parameterType="PostDto">
        UPDATE posts
        <set>
            <if test="title != null">title = #{title},</if>
            <if test="content != null">content = #{content},</if>
            <if test="status != null">status = #{status},</if>
            updated_at = NOW()
        </set>
        WHERE id = #{id}
    </update>

    <!-- 조회수 증가 -->
    <update id="increaseViewCount" parameterType="long">
        UPDATE posts
        SET view_count = view_count + 1
        WHERE id = #{id}
    </update>

    <!-- 댓글 수 업데이트 -->
    <update id="updateCommentCount" parameterType="long">
        UPDATE posts
        SET comment_count = (
            SELECT COUNT(*)
            FROM comments
            WHERE post_id = #{postId} AND status = 'PUBLISHED'
        )
        WHERE id = #{postId}
    </update>

    <!-- 삭제 (Soft Delete) -->
    <update id="delete" parameterType="long">
        UPDATE posts
        SET status = 'DELETED'
        WHERE id = #{id}
    </update>

</mapper>
```

### Step 4: Service 계층

```java
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PostService {

    private final PostMapper postMapper;

    // 게시글 목록
    public List<PostDto> getAllPosts() {
        return postMapper.findAll();
    }

    // 게시글 상세 조회
    @Transactional
    public PostDto getPost(Long id) {
        PostDto post = postMapper.findById(id);
        if (post == null) {
            throw new IllegalArgumentException("게시글을 찾을 수 없습니다.");
        }

        // 조회수 증가
        postMapper.increaseViewCount(id);

        return post;
    }

    // 복잡한 검색
    public PostSearchResult search(PostSearchCondition condition, int page, int size) {
        // 페이징 계산
        int offset = page * size;

        // 검색
        List<PostDto> posts = postMapper.search(condition);
        List<PostDto> pagedPosts = posts.stream()
                .skip(offset)
                .limit(size)
                .collect(Collectors.toList());

        // 전체 개수
        long total = postMapper.countSearch(condition);

        return new PostSearchResult(pagedPosts, total, page, size);
    }

    // 인기 게시글
    public List<PostDto> getPopularPosts(int limit) {
        return postMapper.findPopularPosts(limit);
    }

    // 통계
    public List<PostStatDto> getStatistics() {
        return postMapper.getPostStatsByAuthor();
    }

    // 게시글 작성
    @Transactional
    public PostDto createPost(PostDto post) {
        post.setStatus("PUBLISHED");
        postMapper.insert(post);
        return post;
    }

    // 게시글 수정
    @Transactional
    public void updatePost(PostDto post) {
        postMapper.update(post);
    }

    // 게시글 삭제
    @Transactional
    public void deletePost(Long id) {
        postMapper.delete(id);
    }

    // 대량 생성 (배치)
    @Transactional
    public void createPostsBatch(List<PostDto> posts) {
        // 1000개씩 나눠서 삽입
        int batchSize = 1000;
        for (int i = 0; i < posts.size(); i += batchSize) {
            int end = Math.min(i + batchSize, posts.size());
            List<PostDto> batch = posts.subList(i, end);
            postMapper.insertBatch(batch);
        }
    }
}

@Data
@AllArgsConstructor
class PostSearchResult {
    private List<PostDto> posts;
    private long total;
    private int page;
    private int size;

    public int getTotalPages() {
        return (int) Math.ceil((double) total / size);
    }
}
```

### Step 5: Controller

```java
@RestController
@RequestMapping("/api/posts")
@RequiredArgsConstructor
public class PostController {

    private final PostService postService;

    @GetMapping
    public ResponseEntity<List<PostDto>> getAllPosts() {
        return ResponseEntity.ok(postService.getAllPosts());
    }

    @GetMapping("/{id}")
    public ResponseEntity<PostDto> getPost(@PathVariable Long id) {
        return ResponseEntity.ok(postService.getPost(id));
    }

    @GetMapping("/search")
    public ResponseEntity<PostSearchResult> search(
            @ModelAttribute PostSearchCondition condition,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {

        PostSearchResult result = postService.search(condition, page, size);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/popular")
    public ResponseEntity<List<PostDto>> getPopularPosts(
            @RequestParam(defaultValue = "10") int limit) {

        return ResponseEntity.ok(postService.getPopularPosts(limit));
    }

    @GetMapping("/stats")
    public ResponseEntity<List<PostStatDto>> getStatistics() {
        return ResponseEntity.ok(postService.getStatistics());
    }

    @PostMapping
    public ResponseEntity<PostDto> createPost(@RequestBody PostDto post) {
        return ResponseEntity.ok(postService.createPost(post));
    }

    @PutMapping("/{id}")
    public ResponseEntity<Void> updatePost(
            @PathVariable Long id,
            @RequestBody PostDto post) {

        post.setId(id);
        postService.updatePost(post);
        return ResponseEntity.ok().build();
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deletePost(@PathVariable Long id) {
        postService.deletePost(id);
        return ResponseEntity.noContent().build();
    }
}
```

---

## 🏢 기업 사례: 배달의민족

### 배경

배달의민족은 복잡한 주문 통계와 실시간 대시보드를 제공합니다.

**기술적 요구사항:**
- 시간대별/지역별 주문 통계
- 음식점별 매출 순위
- 실시간 배달 현황
- 복잡한 다차원 분석

### JPA + MyBatis 혼용 전략

```java
// JPA - 단순 CRUD, 도메인 로직
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByUserId(Long userId);
}

// MyBatis - 복잡한 통계 쿼리
@Mapper
public interface OrderStatMapper {

    @Select("""
        SELECT
            DATE_FORMAT(o.created_at, '%Y-%m-%d %H:00:00') as hour,
            r.region,
            COUNT(o.id) as order_count,
            SUM(o.total_price) as total_sales,
            AVG(o.delivery_time) as avg_delivery_time
        FROM orders o
        JOIN restaurants r ON o.restaurant_id = r.id
        WHERE o.created_at >= #{startDate}
          AND o.status = 'COMPLETED'
        GROUP BY DATE_FORMAT(o.created_at, '%Y-%m-%d %H:00:00'), r.region
        ORDER BY hour DESC, total_sales DESC
        """)
    List<OrderStatDto> getHourlyStatsByRegion(@Param("startDate") LocalDateTime startDate);
}
```

**효과:**
- 개발 속도 40% 향상
- 복잡한 쿼리 성능 최적화
- 팀원 간 역할 분담 명확 (도메인 vs 통계)

---

## ❓ FAQ

### Q1. JPA와 MyBatis 중 어떤 것을 선택해야 하나요?

**A:** 혼용 전략 권장

| 용도 | 추천 기술 | 이유 |
|-----|----------|------|
| 단순 CRUD | JPA/Spring Data JPA | 생산성 높음 |
| 도메인 로직 | JPA | 객체지향적 설계 |
| 복잡한 통계 | MyBatis | SQL 자유도 |
| 대용량 배치 | MyBatis | 메모리 효율적 |
| 레거시 SQL | MyBatis | 기존 자산 활용 |

```java
// 같은 프로젝트에서 혼용
@Service
public class OrderService {
    private final OrderRepository orderRepository;  // JPA
    private final OrderStatMapper orderStatMapper;  // MyBatis

    public Order createOrder(Order order) {
        return orderRepository.save(order);  // JPA
    }

    public List<OrderStat> getStatistics() {
        return orderStatMapper.getStats();  // MyBatis
    }
}
```

### Q2. XML과 Annotation 중 어떤 방식이 좋나요?

**A:**

| 상황 | 권장 방식 |
|-----|----------|
| 간단한 쿼리 (1~2줄) | Annotation |
| 복잡한 쿼리, 동적 SQL | XML |
| 여러 곳에서 재사용 | XML |

```java
// ✅ Good - 간단한 쿼리는 Annotation
@Select("SELECT * FROM users WHERE id = #{id}")
UserDto findById(Long id);

// ✅ Good - 복잡한 쿼리는 XML
List<UserDto> search(UserSearchCondition condition);  // XML에 정의
```

### Q3. MyBatis의 1차 캐시는 어떻게 작동하나요?

**A:** SqlSession 단위로 동작

```java
// 같은 SqlSession (트랜잭션) 내
UserDto user1 = userMapper.findById(1L);  // DB 조회
UserDto user2 = userMapper.findById(1L);  // 캐시에서 조회

// 다른 SqlSession
// → 각각 별도로 DB 조회 (캐시 공유 안 됨)
```

**주의사항:**
- 2차 캐시는 별도 설정 필요
- 일반적으로 캐시는 Redis 등 외부 솔루션 사용 권장

### Q4. #{} 와 ${} 의 차이는?

**A:**

```xml
<!-- ✅ #{} - PreparedStatement (권장) -->
<select id="findByName">
    SELECT * FROM users WHERE name = #{name}
</select>
<!-- SQL: SELECT * FROM users WHERE name = ? -->
<!-- SQL Injection 방지 -->

<!-- ⚠️ ${} - String Substitution -->
<select id="findByColumnName">
    SELECT ${columnName} FROM users
</select>
<!-- SQL: SELECT name FROM users -->
<!-- SQL Injection 위험! 동적 컬럼명/테이블명에만 사용 -->
```

**사용 원칙:**
- 파라미터 값: `#{}`
- 컬럼명, 테이블명, ORDER BY: `${}` (주의 필요)

### Q5. ResultMap은 언제 사용하나요?

**A:** 복잡한 매핑이 필요한 경우

```xml
<!-- 간단한 경우 - resultType으로 충분 -->
<select id="findAll" resultType="UserDto">
    SELECT id, name, email FROM users
</select>

<!-- 복잡한 경우 - ResultMap 필요 -->
<resultMap id="UserWithOrdersMap" type="UserDto">
    <id property="id" column="user_id"/>
    <result property="name" column="user_name"/>
    <collection property="orders" ofType="OrderDto">
        <id property="id" column="order_id"/>
        <result property="totalPrice" column="order_total"/>
    </collection>
</resultMap>

<select id="findUserWithOrders" resultMap="UserWithOrdersMap">
    SELECT u.id as user_id, u.name as user_name,
           o.id as order_id, o.total_price as order_total
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
</select>
```

---

## 💼 면접 질문 TOP 5

### ⭐ 초급 1: MyBatis의 장점은?

**답변:**
1. **SQL 완전 제어**: 복잡한 쿼리 작성 자유
2. **성능 최적화**: SQL 직접 튜닝 가능
3. **학습 곡선**: SQL만 알면 쉽게 시작
4. **레거시 통합**: 기존 SQL 자산 활용

### ⭐ 초급 2: JPA와 MyBatis의 차이는?

**답변:**

| 구분 | JPA | MyBatis |
|-----|-----|---------|
| 패러다임 | ORM (객체 중심) | SQL Mapper (SQL 중심) |
| SQL 작성 | 자동 생성 | 직접 작성 |
| 생산성 | 높음 (단순 CRUD) | 낮음 |
| 유연성 | 낮음 (복잡한 쿼리) | 높음 |

### ⭐⭐ 중급 1: 동적 SQL의 주요 태그는?

**답변:**
- `<if>`: 조건부 SQL
- `<choose>`, `<when>`, `<otherwise>`: switch-case
- `<where>`: WHERE 절 자동 생성
- `<set>`: UPDATE SET 절 자동 생성
- `<foreach>`: 반복 (IN 절, Batch)

### ⭐⭐ 중급 2: #{}와 ${}의 차이는?

**답변:**

```xml
<!-- #{} - PreparedStatement -->
WHERE name = #{name}  → WHERE name = ?
<!-- SQL Injection 방지, 파라미터 값에 사용 -->

<!-- ${} - String Substitution -->
ORDER BY ${columnName}  → ORDER BY created_at
<!-- SQL Injection 위험, 컬럼명/테이블명에만 사용 -->
```

### ⭐⭐ 중급 3: JPA와 MyBatis를 함께 사용할 수 있나요?

**답변:**
가능하며, 실무에서 자주 사용됩니다.

```java
@Service
public class OrderService {
    @Autowired
    private OrderRepository orderRepository;  // JPA

    @Autowired
    private OrderStatMapper orderStatMapper;  // MyBatis

    // 단순 CRUD → JPA
    public Order createOrder(Order order) {
        return orderRepository.save(order);
    }

    // 복잡한 통계 → MyBatis
    public List<OrderStat> getStatistics() {
        return orderStatMapper.getHourlyStats();
    }
}
```

**주의사항:**
- 트랜잭션 관리 통일 (`@Transactional`)
- 캐시 정합성 고려

---

## 🎯 다음 단계

MyBatis를 마쳤다면:

1. **성능 최적화** - 쿼리 튜닝, 인덱스 전략
2. **대용량 처리** - Batch 처리, Streaming
3. **캐싱 전략** - Redis 통합
4. **실전 프로젝트** - 대시보드 시스템 구축
5. **모니터링** - 쿼리 성능 측정

---

## 📚 참고 자료

- **MyBatis 공식 문서**: https://mybatis.org/mybatis-3/
- **Spring Boot + MyBatis**: https://mybatis.org/spring-boot-starter/mybatis-spring-boot-autoconfigure/

---

**🎓 학습 완료 체크리스트:**

- [ ] MyBatis 개념과 설정
- [ ] Mapper 인터페이스와 XML 작성
- [ ] 동적 SQL (if, choose, foreach)
- [ ] ResultMap으로 복잡한 매핑
- [ ] JPA와 MyBatis 혼용 전략
- [ ] 게시판 시스템 실습 완료

**축하합니다! Spring 데이터 접근 기술을 모두 마스터했습니다!** 🎉

---

## 🔄 JPA vs QueryDSL vs MyBatis 선택 가이드

```
단순 CRUD
└─→ Spring Data JPA Query Method

복잡한 동적 쿼리 (타입 안전성 필요)
└─→ QueryDSL

복잡한 통계/집계 (SQL 최적화 필요)
└─→ MyBatis

레거시 시스템 통합
└─→ MyBatis

대용량 배치 처리
└─→ MyBatis

실시간 도메인 로직
└─→ JPA
```

**실무 권장 조합:**
```
프로젝트 = JPA (80%) + QueryDSL (15%) + MyBatis (5%)
```

이제 상황에 맞는 최적의 기술을 선택할 수 있습니다! 🚀
