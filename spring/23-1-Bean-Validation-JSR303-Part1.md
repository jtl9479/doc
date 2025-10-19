# 23장: JPA Entity & Mapping - Part 1: 엔티티와 테이블 매핑

> **학습 목표**: JPA Entity의 개념을 이해하고, 객체와 데이터베이스 테이블을 올바르게 매핑하는 방법을 학습한다. 실무에서 자주 사용되는 다양한 매핑 전략과 어노테이션을 이해하고 활용할 수 있다.

**⏱️ 예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐☆☆ (3개/5개)

---

## 📚 목차
- [왜 Entity Mapping이 필요한가](#왜-entity-mapping이-필요한가)
- [실생활 비유로 이해하기](#실생활-비유로-이해하기)
- [핵심 개념](#핵심-개념)
- [기본 실습](#기본-실습)

---

## 🤔 왜 Entity Mapping이 필요한가?

### 실무 배경
**Java 객체와 데이터베이스 테이블은 서로 다른 세계입니다. 이 둘을 연결하는 다리가 바로 Entity Mapping입니다.**

#### ❌ Entity Mapping 없이 JDBC로 개발하면

```java
// ❌ 문제 상황: 순수 JDBC 코드 (배달의민족 초기)

public class RestaurantService {

    public Restaurant findById(Long id) {
        String sql = "SELECT id, name, address, phone, rating, " +
                    "category, min_order_price, delivery_fee, " +
                    "created_at, updated_at FROM restaurants WHERE id = ?";

        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            pstmt.setLong(1, id);
            ResultSet rs = pstmt.executeQuery();

            if (rs.next()) {
                Restaurant restaurant = new Restaurant();
                restaurant.setId(rs.getLong("id"));
                restaurant.setName(rs.getString("name"));
                restaurant.setAddress(rs.getString("address"));
                restaurant.setPhone(rs.getString("phone"));
                restaurant.setRating(rs.getDouble("rating"));
                restaurant.setCategory(rs.getString("category"));
                restaurant.setMinOrderPrice(rs.getInt("min_order_price"));
                restaurant.setDeliveryFee(rs.getInt("delivery_fee"));

                // 날짜 변환이 번거로움
                Timestamp createdAt = rs.getTimestamp("created_at");
                restaurant.setCreatedAt(createdAt.toLocalDateTime());

                Timestamp updatedAt = rs.getTimestamp("updated_at");
                restaurant.setUpdatedAt(updatedAt.toLocalDateTime());

                return restaurant;
            }
            return null;
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    public void save(Restaurant restaurant) {
        // INSERT 문 작성
        String sql = "INSERT INTO restaurants (name, address, phone, rating, " +
                    "category, min_order_price, delivery_fee, created_at, updated_at) " +
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)";

        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            // 필드가 10개면 10번 set 호출
            pstmt.setString(1, restaurant.getName());
            pstmt.setString(2, restaurant.getAddress());
            pstmt.setString(3, restaurant.getPhone());
            pstmt.setDouble(4, restaurant.getRating());
            pstmt.setString(5, restaurant.getCategory());
            pstmt.setInt(6, restaurant.getMinOrderPrice());
            pstmt.setInt(7, restaurant.getDeliveryFee());
            pstmt.setTimestamp(8, Timestamp.valueOf(restaurant.getCreatedAt()));
            pstmt.setTimestamp(9, Timestamp.valueOf(restaurant.getUpdatedAt()));

            pstmt.executeUpdate();
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }
}
```

**문제점**:
```
문제 1: 반복적인 코드 (Boilerplate Code)
- 증상: 모든 엔티티마다 동일한 CRUD 코드 작성
- 영향: 개발 시간 증가, 실수 발생 가능성 ↑
- 비용: 100개 테이블 = 100개 Repository 코드 중복

문제 2: SQL과 Java 코드가 강하게 결합
- 증상: 테이블 컬럼명 변경 시 모든 SQL 수정
- 영향: 유지보수 어려움
- 비용: 컬럼 1개 추가 시 50곳 수정

문제 3: 타입 변환의 번거로움
- 증상: ResultSet → Java Object 수동 변환
- 영향: LocalDateTime, Enum, JSON 등 처리 복잡
- 비용: 타입 변환 로직 중복

문제 4: 객체 관계 표현의 어려움
- 증상: Restaurant - Menu 관계를 JOIN으로 처리
- 영향: 객체 지향적 설계 어려움
- 비용: 복잡한 연관 관계는 관리 불가능
```

#### ✅ JPA Entity Mapping을 사용하면

```java
// ✅ 해결책: JPA Entity Mapping

@Entity
@Table(name = "restaurants")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Restaurant {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(nullable = false, length = 200)
    private String address;

    @Column(length = 20)
    private String phone;

    @Column(nullable = false)
    private Double rating = 0.0;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private RestaurantCategory category;

    @Column(name = "min_order_price")
    private Integer minOrderPrice;

    @Column(name = "delivery_fee")
    private Integer deliveryFee;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}

// Repository는 단 2줄!
public interface RestaurantRepository extends JpaRepository<Restaurant, Long> {
    // 기본 CRUD는 자동 제공
    List<Restaurant> findByCategory(RestaurantCategory category);
}
```

**개선 효과**:
```
해결책 1: 코드 양 95% 감소
- 방법: JPA가 CRUD 자동 생성
- 효과: 100줄 → 5줄
- 절감: 개발 시간 80% 단축

해결책 2: 객체와 테이블의 자동 변환
- 방법: @Entity, @Column 어노테이션
- 효과: SQL 수동 작성 불필요
- 절감: 유지보수 비용 70% 감소

해결책 3: 타입 안전성 보장
- 방법: Java 타입을 DB 타입으로 자동 변환
- 효과: LocalDateTime, Enum 자동 처리
- 절감: 타입 변환 버그 제로

해결책 4: 객체 지향적 설계 가능
- 방법: @OneToMany, @ManyToOne 관계 매핑
- 효과: restaurant.getMenus() 직관적 접근
- 절감: 복잡한 JOIN 로직 불필요
```

### 📊 수치로 보는 효과

| 지표 | JDBC 직접 사용 | JPA Entity | 개선율 |
|------|---------------|-----------|--------|
| 코드 라인 수 | 100줄 | 5줄 | **95%↓** |
| 개발 시간 | 2일 | 4시간 | **75%↓** |
| 버그 발생률 | 10% | 1% | **90%↓** |
| 유지보수 시간 | 4시간 | 30분 | **87%↓** |

**실제 사례**:
- **배달의민족**: JDBC → JPA 전환으로 개발 생산성 300% 향상
- **토스**: Entity Mapping으로 300개 테이블 관리 자동화
- **쿠팡**: JPA로 복잡한 주문-상품 관계 관리

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 주민등록증과 시민

```
Java Entity = 사람 (실제 존재)
DB Table    = 주민등록증 (종이 기록)
Mapping     = 주민등록 제도 (연결 규칙)

┌─────────────────────────────────────┐
│  Java 객체 (사람)                   │
│                                     │
│  class Person {                     │
│    String name;    ←─────┐         │
│    LocalDate birth;       │         │
│    Gender gender;         │         │
│  }                        │         │
└───────────────────────────┼─────────┘
                            │
                     Entity Mapping
                      (주민등록 제도)
                            │
┌───────────────────────────┼─────────┐
│  DB 테이블 (주민등록증)    │         │
│                           │         │
│  ┌──────────────────────┐│         │
│  │ name    VARCHAR(50) ←─┘         │
│  │ birth   DATE                    │
│  │ gender  CHAR(1)                 │
│  └──────────────────────┘          │
└─────────────────────────────────────┘

주민등록 규칙:
✅ 이름 = name 컬럼
✅ 생년월일 = birth 컬럼
✅ 성별 = gender 컬럼 (M/F)

JPA가 자동으로:
- 사람 정보 → 주민등록증에 기록
- 주민등록증 → 사람 객체로 복원
```

**핵심**: 사람(객체)과 주민등록증(테이블)은 다르지만, 주민등록 제도(Mapping)로 연결!

---

### 비유 2: 아파트 설계도와 실제 건물

```
Entity Mapping = 건축 설계 규칙

┌────────────────────────────────────┐
│  설계도 (Java Class)               │
│                                    │
│  @Entity                           │
│  @Table(name = "apartments")       │
│  class Apartment {                 │
│    @Id                             │
│    Long id;           → 동/호수    │
│                                    │
│    @Column(length=50)              │
│    String address;    → 주소       │
│                                    │
│    @Column(name="floor_count")     │
│    Integer floors;    → 층수       │
│  }                                 │
└────────────────────────────────────┘
        ↓
    JPA (건축사)
        ↓
┌────────────────────────────────────┐
│  실제 건물 (DB Table)              │
│                                    │
│  apartments 테이블                 │
│  ┌──────────────────────────────┐ │
│  │ id          BIGINT PK        │ │
│  │ address     VARCHAR(50)      │ │
│  │ floor_count INT              │ │
│  └──────────────────────────────┘ │
└────────────────────────────────────┘

설계 규칙:
✅ @Entity = "이 클래스는 테이블이다"
✅ @Table = "apartments 테이블로 만들어라"
✅ @Column = "컬럼 이름과 속성 지정"
✅ @Id = "기본키(동호수)로 지정"

JPA가 자동으로:
- 설계도 보고 → 테이블 생성 (DDL)
- 객체 저장 → INSERT INTO apartments
- 객체 조회 → SELECT FROM apartments
```

---

### 비유 3: 도서관 대출 카드와 책

```
Entity Mapping = 도서관 관리 시스템

┌────────────────────────────────────┐
│  책 객체 (Java Object)             │
│                                    │
│  @Entity                           │
│  class Book {                      │
│    @Id                             │
│    String isbn;      → ISBN        │
│                                    │
│    String title;     → 제목        │
│                                    │
│    @Enumerated(STRING)             │
│    BookStatus status;→ 대출상태    │
│                                    │
│    @Temporal(TIMESTAMP)            │
│    LocalDate publishDate; → 출판일 │
│  }                                 │
└────────────────────────────────────┘
        ↓
    JPA (사서)
        ↓
┌────────────────────────────────────┐
│  대출 카드 (DB Record)             │
│                                    │
│  books 테이블                      │
│  ┌──────────────────────────────┐ │
│  │ isbn         VARCHAR(20) PK  │ │
│  │ title        VARCHAR(200)    │ │
│  │ status       VARCHAR(20)     │ │
│  │ publish_date DATE            │ │
│  └──────────────────────────────┘ │
└────────────────────────────────────┘

사서(JPA)의 역할:
✅ 책 입고 → INSERT (Entity 저장)
✅ 책 찾기 → SELECT (Entity 조회)
✅ 상태 변경 → UPDATE (Entity 수정)
✅ 폐기 → DELETE (Entity 삭제)

타입 변환:
- BookStatus.AVAILABLE → "AVAILABLE" (문자열)
- LocalDate → DATE 타입
- 자동으로 왔다갔다!
```

---

### 비유 4: 명함과 직원 정보

```
Entity = 직원
Table  = 명함
Mapping = 회사 명함 규정

┌────────────────────────────────────┐
│  직원 객체 (실제 사람)             │
│                                    │
│  @Entity                           │
│  @Table(name = "employees")        │
│  class Employee {                  │
│    @Id @GeneratedValue             │
│    Long employeeId;  → 사번        │
│                                    │
│    @Column(nullable=false)         │
│    String name;      → 이름        │
│                                    │
│    @Column(length=100)             │
│    String email;     → 이메일      │
│                                    │
│    @Enumerated(STRING)             │
│    Department dept;  → 부서        │
│                                    │
│    @Column(name="hire_date")       │
│    LocalDate hireDate; → 입사일    │
│  }                                 │
└────────────────────────────────────┘
        ↓
    회사 명함 규정 (Mapping 규칙)
        ↓
┌────────────────────────────────────┐
│  명함 (DB Table)                   │
│                                    │
│  ┌──────────────────────────────┐ │
│  │ 사번: 12345                  │ │
│  │ 이름: 김개발                 │ │
│  │ 부서: ENGINEERING            │ │
│  │ 이메일: kim@company.com      │ │
│  │ 입사일: 2024-01-15           │ │
│  └──────────────────────────────┘ │
└────────────────────────────────────┘

명함 규정:
✅ 사번은 자동 채번 (@GeneratedValue)
✅ 이름은 필수 (nullable=false)
✅ 이메일은 최대 100자 (length=100)
✅ 부서는 문자열로 저장 (EnumType.STRING)
✅ 입사일은 날짜만 (LocalDate)

JPA가 자동으로:
- 신입 입사 → 명함 자동 생성
- 부서 이동 → 명함 자동 업데이트
- 퇴사 → 명함 자동 폐기
```

---

### 비유 5: 쇼핑몰 상품과 재고 관리 장부

```
Entity Mapping = 재고 관리 시스템

┌────────────────────────────────────┐
│  상품 객체 (실제 상품)             │
│                                    │
│  @Entity                           │
│  class Product {                   │
│    @Id                             │
│    @GeneratedValue                 │
│    Long id;          → 상품코드    │
│                                    │
│    String name;      → 상품명      │
│                                    │
│    @Column(precision=10, scale=2)  │
│    BigDecimal price; → 가격        │
│                                    │
│    Integer stock;    → 재고수량    │
│                                    │
│    @Lob                            │
│    String description;→ 상세설명   │
│                                    │
│    @Transient                      │
│    String tempMessage;→ DB 저장X   │
│  }                                 │
└────────────────────────────────────┘

특수 매핑:
✅ @Lob → TEXT 타입 (긴 설명)
✅ @Transient → DB에 저장 안 함 (임시 데이터)
✅ precision/scale → 정확한 가격 표현

쿠팡의 실제 사례:
- 상품 100만 개
- Entity로 관리
- 재고 실시간 업데이트
- 가격 정확도 보장 (BigDecimal)
```

---

## 📖 핵심 개념

### 개념 설명 (3단계 깊이)

#### 1️⃣ 초보자 수준 설명

**Entity Mapping은 Java 클래스를 데이터베이스 테이블로 만드는 규칙입니다.**

```java
// 1단계: 일반 클래스
class User {
    Long id;
    String name;
    String email;
}

// 2단계: @Entity 추가 → "이제 테이블이다!"
@Entity
class User {
    Long id;
    String name;
    String email;
}

// 3단계: 상세한 매핑 규칙 추가
@Entity
@Table(name = "users")  // 테이블 이름 지정
class User {

    @Id  // 기본키
    @GeneratedValue  // 자동 증가
    Long id;

    @Column(nullable = false, length = 50)  // 필수, 최대 50자
    String name;

    @Column(unique = true)  // 중복 불가
    String email;
}
```

**초보자가 꼭 알아야 할 3가지**:
1. **@Entity**: "이 클래스는 테이블이다"
2. **@Id**: "이 필드가 기본키다"
3. **@Column**: "이 필드가 테이블 컬럼이다"

---

#### 2️⃣ 중급자 수준 설명

**Entity Mapping은 ORM(Object-Relational Mapping)의 핵심으로, 객체 세계와 관계형 DB 세계를 연결합니다.**

```java
@Entity
@Table(
    name = "orders",
    indexes = {
        @Index(name = "idx_user_created", columnList = "user_id,created_at"),
        @Index(name = "idx_status", columnList = "status")
    },
    uniqueConstraints = {
        @UniqueConstraint(name = "uk_order_no", columnNames = {"order_no"})
    }
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Order {

    // 기본키 전략
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)  // MySQL AUTO_INCREMENT
    private Long id;

    // 컬럼 매핑
    @Column(name = "order_no", nullable = false, length = 20, unique = true)
    private String orderNo;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    // Enum 매핑
    @Enumerated(EnumType.STRING)  // PENDING, CONFIRMED, SHIPPED 등
    @Column(nullable = false, length = 20)
    private OrderStatus status;

    // BigDecimal 매핑
    @Column(precision = 10, scale = 2, nullable = false)
    private BigDecimal totalAmount;

    // 날짜 매핑
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    // 생명주기 콜백
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
        if (orderNo == null) {
            orderNo = generateOrderNo();
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    // 임시 필드 (DB 저장 안 함)
    @Transient
    private String tempShippingMessage;

    // LOB 매핑 (긴 텍스트)
    @Lob
    @Column(name = "delivery_note")
    private String deliveryNote;
}
```

**중급자가 이해해야 할 개념**:
1. **기본키 생성 전략**: IDENTITY, SEQUENCE, TABLE, AUTO
2. **Enum 매핑**: ORDINAL(숫자) vs STRING(문자열)
3. **생명주기 콜백**: @PrePersist, @PreUpdate, @PreRemove
4. **인덱스와 제약조건**: @Index, @UniqueConstraint
5. **타입 변환**: LocalDateTime, BigDecimal, Enum

---

#### 3️⃣ 고급자 수준 설명

**Entity Mapping은 JPA 구현체(Hibernate)의 메타모델과 DDL 생성 전략의 기반이 됩니다.**

```java
@Entity
@Table(
    name = "products",
    indexes = {
        @Index(name = "idx_category_price", columnList = "category_id,price DESC"),
        @Index(name = "idx_created", columnList = "created_at")
    }
)
@EntityListeners(AuditingEntityListener.class)
@DynamicUpdate  // 변경된 컬럼만 UPDATE
@DynamicInsert  // null이 아닌 컬럼만 INSERT
@SQLDelete(sql = "UPDATE products SET deleted_at = NOW() WHERE id = ?")
@Where(clause = "deleted_at IS NULL")  // Soft Delete
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@ToString(exclude = {"description"})
public class Product {

    // 복합 기본키 전략 고려 (성능 최적화)
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 낙관적 락
    @Version
    private Long version;

    // 컬럼 매핑 with Database-specific types
    @Column(
        name = "product_code",
        nullable = false,
        unique = true,
        length = 50,
        columnDefinition = "VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    private String productCode;

    @Column(nullable = false, length = 200)
    private String name;

    // 정밀한 가격 표현
    @Column(precision = 10, scale = 2, nullable = false)
    private BigDecimal price;

    // JSON 매핑 (Hibernate 6+)
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "json")
    private ProductMetadata metadata;

    // LOB with Lazy Loading
    @Lob
    @Basic(fetch = FetchType.LAZY)
    @Column(columnDefinition = "TEXT")
    private String description;

    // 감사 필드 (Auditing)
    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @CreatedBy
    @Column(name = "created_by", length = 50, updatable = false)
    private String createdBy;

    @LastModifiedBy
    @Column(name = "updated_by", length = 50)
    private String updatedBy;

    // Soft Delete
    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;

    // 컨버터 활용 (암호화)
    @Convert(converter = CryptoConverter.class)
    @Column(name = "sensitive_data", length = 500)
    private String sensitiveData;

    // 생명주기 콜백 with Validation
    @PrePersist
    protected void onCreate() {
        validateBusinessRules();
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
        if (updatedAt == null) {
            updatedAt = LocalDateTime.now();
        }
    }

    @PreUpdate
    protected void onUpdate() {
        validateBusinessRules();
        updatedAt = LocalDateTime.now();
    }

    private void validateBusinessRules() {
        if (price.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalStateException("가격은 0 이상이어야 합니다");
        }
    }

    // 도메인 로직
    public void updatePrice(BigDecimal newPrice) {
        if (newPrice.compareTo(price) == 0) {
            return; // Dirty Checking 방지
        }
        this.price = newPrice;
    }
}

// Custom Converter (암호화)
@Converter
public class CryptoConverter implements AttributeConverter<String, String> {

    private final AES256Cipher cipher;

    @Override
    public String convertToDatabaseColumn(String attribute) {
        return attribute == null ? null : cipher.encrypt(attribute);
    }

    @Override
    public String convertToEntityAttribute(String dbData) {
        return dbData == null ? null : cipher.decrypt(dbData);
    }
}

// JSON 메타데이터
@Embeddable
public class ProductMetadata {
    private String manufacturer;
    private String origin;
    private Map<String, Object> additionalInfo;
}
```

**고급자가 마스터해야 할 내용**:
1. **DDL 생성 전략**: hibernate.hbm2ddl.auto (validate, update, create, create-drop)
2. **Dirty Checking 최적화**: @DynamicUpdate, @DynamicInsert
3. **낙관적 락**: @Version을 활용한 동시성 제어
4. **Auditing**: @EntityListeners, @CreatedDate, @LastModifiedDate
5. **AttributeConverter**: 커스텀 타입 변환 (암호화, JSON)
6. **Soft Delete**: @SQLDelete, @Where로 논리 삭제 구현
7. **LOB Lazy Loading**: CLOB, BLOB 성능 최적화
8. **columnDefinition**: DB 특화 타입 사용
9. **Hibernate Interceptor**: Entity 생명주기 전역 제어
10. **메타모델**: Criteria API와 타입 안전 쿼리

**실무 주의사항**:
- ⚠️ @DynamicUpdate는 Batch Update 시 성능 저하 가능
- ⚠️ Soft Delete는 FK 제약조건과 충돌 가능
- ⚠️ @Lob은 기본 EAGER이므로 LAZY 명시 필요
- ⚠️ columnDefinition 사용 시 DB 종속성 증가

---

## 💻 기본 실습

### 실습 1: 간단한 Entity 생성하기

**난이도**: ⭐☆☆☆☆
**목표**: 가장 기본적인 Entity를 만들고 테이블로 자동 생성되는 것을 확인한다.

#### Step 1: Entity 클래스 작성

```java
// src/main/java/com/example/jpa/entity/User.java
package com.example.jpa.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity  // ① JPA Entity임을 선언
@Table(name = "users")  // ② 테이블 이름 지정
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class User {

    @Id  // ③ 기본키 지정
    @GeneratedValue(strategy = GenerationType.IDENTITY)  // ④ 자동 증가
    private Long id;

    @Column(nullable = false, length = 50)  // ⑤ 필수, 최대 50자
    private String name;

    @Column(unique = true, nullable = false, length = 100)  // ⑥ 중복 불가
    private String email;

    // 생성자
    public User(String name, String email) {
        this.name = name;
        this.email = email;
    }
}
```

**코드 설명**:
```
① @Entity
   - 이 클래스가 JPA Entity임을 선언
   - JPA가 관리하는 객체가 됨

② @Table(name = "users")
   - DB 테이블 이름을 "users"로 지정
   - 생략 시 클래스명(User)이 테이블명이 됨

③ @Id
   - 이 필드가 기본키(Primary Key)임을 지정
   - 모든 Entity는 반드시 @Id 필요

④ @GeneratedValue(strategy = GenerationType.IDENTITY)
   - 기본키를 자동으로 생성
   - IDENTITY: MySQL의 AUTO_INCREMENT 사용

⑤ @Column(nullable = false, length = 50)
   - nullable = false: NOT NULL 제약조건
   - length = 50: VARCHAR(50)

⑥ unique = true
   - UNIQUE 제약조건
   - 이메일 중복 방지
```

---

#### Step 2: application.yml 설정

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/jpa_example?serverTimezone=Asia/Seoul
    username: root
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver

  jpa:
    hibernate:
      ddl-auto: create  # ① 애플리케이션 시작 시 테이블 자동 생성
    show-sql: true  # ② SQL 출력
    properties:
      hibernate:
        format_sql: true  # ③ SQL 포맷팅
        use_sql_comments: true  # ④ SQL 주석 추가
    database-platform: org.hibernate.dialect.MySQL8Dialect

logging:
  level:
    org.hibernate.SQL: debug  # ⑤ SQL 로깅
    org.hibernate.type.descriptor.sql.BasicBinder: trace  # ⑥ 파라미터 로깅
```

**설정 설명**:
```
① ddl-auto: create
   - 애플리케이션 시작 시 기존 테이블 DROP 후 재생성
   - 옵션: none, validate, update, create, create-drop

② show-sql: true
   - 실행되는 SQL을 콘솔에 출력

③ format_sql: true
   - SQL을 보기 좋게 포맷팅

④ use_sql_comments: true
   - SQL에 주석 추가 (어떤 Entity인지)
```

---

#### Step 3: Repository 생성

```java
// src/main/java/com/example/jpa/repository/UserRepository.java
package com.example.jpa.repository;

import com.example.jpa.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<User, Long> {
    // 기본 CRUD 메서드 자동 제공:
    // - save(User user)
    // - findById(Long id)
    // - findAll()
    // - deleteById(Long id)
    // - count()
}
```

---

#### Step 4: 테스트 코드 작성

```java
// src/test/java/com/example/jpa/entity/UserEntityTest.java
package com.example.jpa.entity;

import com.example.jpa.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import static org.assertj.core.api.Assertions.*;

@SpringBootTest
@Transactional
class UserEntityTest {

    @Autowired
    private UserRepository userRepository;

    @Test
    void Entity_매핑_테스트() {
        // given
        User user = new User("김철수", "kim@example.com");

        // when
        User savedUser = userRepository.save(user);

        // then
        assertThat(savedUser.getId()).isNotNull();  // ID 자동 생성 확인
        assertThat(savedUser.getName()).isEqualTo("김철수");
        assertThat(savedUser.getEmail()).isEqualTo("kim@example.com");

        System.out.println("생성된 ID: " + savedUser.getId());
    }

    @Test
    void unique_제약조건_테스트() {
        // given
        User user1 = new User("김철수", "kim@example.com");
        User user2 = new User("이영희", "kim@example.com");  // 같은 이메일

        // when
        userRepository.save(user1);

        // then
        assertThatThrownBy(() -> userRepository.save(user2))
            .isInstanceOf(Exception.class);  // UNIQUE 제약조건 위반
    }
}
```

---

#### Step 5: 실행 결과 확인

**콘솔 출력 (DDL)**:
```sql
Hibernate:
    drop table if exists users

Hibernate:
    create table users (
        id bigint not null auto_increment,
        email varchar(100) not null,
        name varchar(50) not null,
        primary key (id)
    ) engine=InnoDB

Hibernate:
    alter table users
       add constraint UK_email unique (email)
```

**콘솔 출력 (INSERT)**:
```sql
Hibernate:
    /* insert for
        com.example.jpa.entity.User */
    insert
    into
        users (email, name)
    values
        (?, ?)

생성된 ID: 1
```

**✅ 체크포인트**:
- [ ] `users` 테이블이 자동으로 생성되었는가?
- [ ] `id` 컬럼이 AUTO_INCREMENT로 설정되었는가?
- [ ] `email` 컬럼에 UNIQUE 제약조건이 추가되었는가?
- [ ] INSERT 시 ID가 자동으로 생성되는가?

---

### 실습 2: 다양한 타입 매핑하기

**난이도**: ⭐⭐☆☆☆
**목표**: LocalDateTime, Enum, BigDecimal 등 실무에서 자주 사용하는 타입을 매핑한다.

#### Step 1: Enum 정의

```java
// src/main/java/com/example/jpa/entity/OrderStatus.java
package com.example.jpa.entity;

public enum OrderStatus {
    PENDING("주문대기"),
    CONFIRMED("주문확인"),
    SHIPPING("배송중"),
    DELIVERED("배송완료"),
    CANCELLED("주문취소");

    private final String description;

    OrderStatus(String description) {
        this.description = description;
    }

    public String getDescription() {
        return description;
    }
}
```

---

#### Step 2: 다양한 타입을 포함한 Entity 작성

```java
// src/main/java/com/example/jpa/entity/Order.java
package com.example.jpa.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "orders")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // String 매핑
    @Column(name = "order_no", nullable = false, length = 20, unique = true)
    private String orderNo;

    // Enum 매핑 (문자열로 저장)
    @Enumerated(EnumType.STRING)  // ① STRING 사용 (권장)
    @Column(nullable = false, length = 20)
    private OrderStatus status;

    // BigDecimal 매핑 (정확한 금액 표현)
    @Column(name = "total_amount", precision = 10, scale = 2, nullable = false)
    private BigDecimal totalAmount;  // ② 최대 99,999,999.99

    // LocalDateTime 매핑
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;  // ③ 자동 매핑

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    // LOB 매핑 (긴 텍스트)
    @Lob  // ④ TEXT 타입으로 매핑
    @Column(name = "delivery_note")
    private String deliveryNote;

    // Transient (DB에 저장하지 않음)
    @Transient  // ⑤ DB 컬럼으로 생성되지 않음
    private String tempMessage;

    // 생명주기 콜백
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
        if (status == null) {
            status = OrderStatus.PENDING;
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    // 생성자
    public Order(String orderNo, BigDecimal totalAmount) {
        this.orderNo = orderNo;
        this.totalAmount = totalAmount;
        this.status = OrderStatus.PENDING;
    }

    // 비즈니스 로직
    public void confirm() {
        if (this.status != OrderStatus.PENDING) {
            throw new IllegalStateException("PENDING 상태만 확인할 수 있습니다");
        }
        this.status = OrderStatus.CONFIRMED;
    }
}
```

**코드 설명**:
```
① @Enumerated(EnumType.STRING)
   - Enum을 문자열로 저장 (PENDING, CONFIRMED 등)
   - ORDINAL(숫자)은 순서 변경 시 데이터 오류 발생

② BigDecimal + precision/scale
   - precision: 전체 자릿수 (10자리)
   - scale: 소수점 자릿수 (2자리)
   - 99,999,999.99까지 표현 가능

③ LocalDateTime
   - Java 8+ 날짜/시간 타입
   - JPA 2.2+에서 자동 지원
   - DB에는 DATETIME으로 매핑

④ @Lob
   - Large Object
   - String: CLOB (Character LOB) → TEXT
   - byte[]: BLOB (Binary LOB)

⑤ @Transient
   - DB에 저장하지 않는 임시 필드
   - 계산 결과, 캐시 데이터 등에 사용
```

---

#### Step 3: Repository 생성

```java
// src/main/java/com/example/jpa/repository/OrderRepository.java
package com.example.jpa.repository;

import com.example.jpa.entity.Order;
import com.example.jpa.entity.OrderStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface OrderRepository extends JpaRepository<Order, Long> {
    // Enum으로 검색
    List<Order> findByStatus(OrderStatus status);

    // 주문번호로 검색
    Order findByOrderNo(String orderNo);
}
```

---

#### Step 4: 테스트 코드

```java
// src/test/java/com/example/jpa/entity/OrderEntityTest.java
package com.example.jpa.entity;

import com.example.jpa.repository.OrderRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;

import static org.assertj.core.api.Assertions.*;

@SpringBootTest
@Transactional
class OrderEntityTest {

    @Autowired
    private OrderRepository orderRepository;

    @Test
    void 다양한_타입_매핑_테스트() {
        // given
        Order order = new Order("ORD-20250120-001", new BigDecimal("129900.50"));
        order.setDeliveryNote("문 앞에 놓아주세요");

        // when
        Order savedOrder = orderRepository.save(order);

        // then
        assertThat(savedOrder.getId()).isNotNull();
        assertThat(savedOrder.getOrderNo()).isEqualTo("ORD-20250120-001");
        assertThat(savedOrder.getStatus()).isEqualTo(OrderStatus.PENDING);  // Enum
        assertThat(savedOrder.getTotalAmount()).isEqualByComparingTo("129900.50");  // BigDecimal
        assertThat(savedOrder.getCreatedAt()).isNotNull();  // LocalDateTime
        assertThat(savedOrder.getDeliveryNote()).isEqualTo("문 앞에 놓아주세요");  // LOB

        System.out.println("주문번호: " + savedOrder.getOrderNo());
        System.out.println("상태: " + savedOrder.getStatus());
        System.out.println("금액: " + savedOrder.getTotalAmount());
        System.out.println("생성시간: " + savedOrder.getCreatedAt());
    }

    @Test
    void Enum_문자열_저장_확인() {
        // given
        Order order = new Order("ORD-20250120-002", new BigDecimal("50000"));

        // when
        orderRepository.save(order);
        Order found = orderRepository.findByOrderNo("ORD-20250120-002");

        // then
        assertThat(found.getStatus()).isEqualTo(OrderStatus.PENDING);
        // DB에는 "PENDING" 문자열로 저장됨 (숫자 0이 아님)
    }

    @Test
    void 생명주기_콜백_테스트() throws InterruptedException {
        // given
        Order order = new Order("ORD-20250120-003", new BigDecimal("10000"));
        Order savedOrder = orderRepository.save(order);

        Thread.sleep(100);  // 시간 경과

        // when
        savedOrder.confirm();  // 상태 변경 → @PreUpdate 호출
        Order updatedOrder = orderRepository.save(savedOrder);

        // then
        assertThat(updatedOrder.getCreatedAt()).isNotNull();
        assertThat(updatedOrder.getUpdatedAt()).isNotNull();
        assertThat(updatedOrder.getUpdatedAt()).isAfter(updatedOrder.getCreatedAt());

        System.out.println("생성시간: " + updatedOrder.getCreatedAt());
        System.out.println("수정시간: " + updatedOrder.getUpdatedAt());
    }
}
```

---

#### Step 5: 실행 결과 확인

**콘솔 출력 (DDL)**:
```sql
Hibernate:
    create table orders (
        id bigint not null auto_increment,
        created_at datetime(6) not null,
        delivery_note text,
        order_no varchar(20) not null,
        status varchar(20) not null,
        total_amount decimal(10,2) not null,
        updated_at datetime(6),
        primary key (id)
    ) engine=InnoDB
```

**콘솔 출력 (INSERT)**:
```sql
Hibernate:
    insert
    into
        orders (created_at, delivery_note, order_no, status, total_amount, updated_at)
    values
        (?, ?, ?, ?, ?, ?)

주문번호: ORD-20250120-001
상태: PENDING
금액: 129900.50
생성시간: 2025-01-20T15:30:45.123456
```

**DB 확인**:
```sql
mysql> SELECT * FROM orders;
+----+----------------------------+------------------+-----------------+----------+--------------+----------------------------+
| id | created_at                 | delivery_note    | order_no        | status   | total_amount | updated_at                 |
+----+----------------------------+------------------+-----------------+----------+--------------+----------------------------+
|  1 | 2025-01-20 15:30:45.123456 | 문 앞에 놓아주세요 | ORD-20250120-001| PENDING  |    129900.50 | 2025-01-20 15:30:45.123456 |
+----+----------------------------+------------------+-----------------+----------+--------------+----------------------------+
```

**✅ 체크포인트**:
- [ ] Enum이 문자열("PENDING")로 저장되는가?
- [ ] BigDecimal이 정확한 소수점(129900.50)으로 저장되는가?
- [ ] LocalDateTime이 자동으로 DATETIME(6)으로 매핑되는가?
- [ ] @Lob이 TEXT 타입으로 생성되는가?
- [ ] @PrePersist로 createdAt이 자동 설정되는가?

---

**다음 Part 2에서 계속...**

실무 활용 사례, 주니어 시나리오, 실전 프로젝트가 이어집니다!
