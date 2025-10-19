# 20장: Spring JDBC

> **학습 목표**: Spring JDBC (JdbcTemplate)를 사용하여 데이터베이스에 효율적으로 접근하고, 복잡한 쿼리를 안전하게 실행할 수 있습니다.

**⏱️ 예상 학습 시간**: 2-3시간
**난이도**: ⭐⭐⭐☆☆ (3개/5개)

---

## 📚 목차
- [왜 Spring JDBC가 필요한가](#왜-spring-jdbc가-필요한가)
- [실생활 비유로 이해하기](#실생활-비유로-이해하기)
- [핵심 개념](#핵심-개념)
- [기본 실습](#기본-실습)
- [실무 활용 사례](#실무-활용-사례)
- [주니어 시나리오](#주니어-시나리오)
- [실전 프로젝트](#실전-프로젝트)
- [FAQ](#faq)
- [면접 질문](#면접-질문)
- [핵심 정리](#핵심-정리)

---

## 🤔 왜 Spring JDBC가 필요한가?

### 실무 배경

**순수 JDBC의 문제점**:
```java
// ❌ 순수 JDBC: 보일러플레이트 코드 과다
public List<User> findAll() {
    Connection conn = null;
    Statement stmt = null;
    ResultSet rs = null;
    List<User> users = new ArrayList<>();

    try {
        conn = dataSource.getConnection();
        stmt = conn.createStatement();
        rs = stmt.executeQuery("SELECT * FROM users");

        while (rs.next()) {
            User user = new User();
            user.setId(rs.getLong("id"));
            user.setName(rs.getString("name"));
            user.setEmail(rs.getString("email"));
            users.add(user);
        }
    } catch (SQLException e) {
        throw new RuntimeException(e);
    } finally {
        // 리소스 정리 (누락하면 메모리 누수!)
        try { if (rs != null) rs.close(); } catch (SQLException e) { }
        try { if (stmt != null) stmt.close(); } catch (SQLException e) { }
        try { if (conn != null) conn.close(); } catch (SQLException e) { }
    }

    return users;
}
```

**문제점**:
1. **보일러플레이트 코드**: Connection, Statement, ResultSet 관리 반복
2. **리소스 누수 위험**: finally 블록에서 수동으로 close() 호출 필수
3. **예외 처리**: Checked Exception (SQLException) 처리 번거로움
4. **코드 가독성**: 비즈니스 로직이 인프라 코드에 묻힘
5. **반복 작업**: 매번 동일한 패턴 코드 작성

### ✅ Spring JDBC (JdbcTemplate)로 해결

```java
// ✅ Spring JDBC: 간결하고 안전
@Repository
@RequiredArgsConstructor
public class UserRepository {

    private final JdbcTemplate jdbcTemplate;

    public List<User> findAll() {
        String sql = "SELECT * FROM users";

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            User user = new User();
            user.setId(rs.getLong("id"));
            user.setName(rs.getString("name"));
            user.setEmail(rs.getString("email"));
            return user;
        });
    }
}
```

**개선 효과**:
```
✅ 자동 리소스 관리: Connection, Statement, ResultSet 자동 close
✅ 예외 변환: SQLException → DataAccessException (Unchecked)
✅ 코드 간결화: 30줄 → 10줄 (67% 감소)
✅ 안정성: 리소스 누수 방지
✅ 생산성: 비즈니스 로직에 집중
```

### 📊 수치로 보는 효과

| 지표 | 순수 JDBC | Spring JDBC | 개선율 |
|------|----------|-------------|--------|
| 코드 라인 수 | 30줄 | 10줄 | **67%↓** |
| 리소스 누수 위험 | 높음 | 없음 | **100%↓** |
| 개발 시간 | 10분 | 3분 | **70%↓** |
| 예외 처리 복잡도 | 높음 (Checked) | 낮음 (Unchecked) | **매우 개선** |
| 유지보수성 | 낮음 | 높음 | **매우 개선** |

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 택배 배송 서비스

**상황**: 물건을 배송하는 두 가지 방법

```
┌──────────────┬─────────────────┬──────────────────┐
│ 택배 서비스  │ Spring JDBC     │ 역할             │
├──────────────┼─────────────────┼──────────────────┤
│ 고객         │ Service 계층    │ 요청자           │
│ 택배 기사    │ JdbcTemplate    │ 중간 담당자      │
│ 물류 창고    │ Database        │ 실제 저장소      │
│ 송장         │ SQL 쿼리        │ 작업 지시서      │
│ 포장         │ RowMapper       │ 데이터 변환      │
└──────────────┴─────────────────┴──────────────────┘

❌ 직접 배송 (순수 JDBC):
1. 직접 차량 운전
2. 주소 찾기
3. 물건 포장
4. 배송 후 차량 주차
→ 복잡하고 시간 소요

✅ 택배 서비스 (Spring JDBC):
1. 송장만 작성 (SQL만 작성)
2. 택배 기사에게 전달 (JdbcTemplate 호출)
3. 나머지는 자동 처리
→ 간단하고 빠름
```

**코드로 보면**:
```java
// ❌ 직접 배송: 모든 과정 수동 처리
public void deliverDirectly(Package pkg) {
    Car car = rentCar();  // 차량 대여
    try {
        startEngine(car);  // 시동
        drive(car, pkg.getAddress());  // 운전
        deliver(pkg);  // 배송
    } finally {
        parkCar(car);  // 주차
        returnCar(car);  // 차량 반납
    }
}

// ✅ 택배 서비스: 송장만 작성
public void deliverByService(Package pkg) {
    courierService.deliver(pkg);  // 간단!
}
```

---

### 비유 2: 음식점 주문

**상황**: 음식을 주문하는 과정

```
┌──────────────┬─────────────────┬──────────────────┐
│ 음식점       │ Spring JDBC     │ 역할             │
├──────────────┼─────────────────┼──────────────────┤
│ 손님         │ 개발자          │ 서비스 사용자    │
│ 웨이터       │ JdbcTemplate    │ 중간 처리자      │
│ 주방         │ Database        │ 실제 작업 공간   │
│ 주문서       │ SQL             │ 작업 지시        │
│ 요리사       │ JDBC Driver     │ 실제 실행자      │
│ 음식         │ ResultSet       │ 결과             │
│ 접시 담기    │ RowMapper       │ 결과 포장        │
└──────────────┴─────────────────┴──────────────────┘

순수 JDBC (주방에 직접 가서 요리):
1. 주방 문 열기 (Connection 생성)
2. 재료 꺼내기 (Statement 생성)
3. 요리하기 (쿼리 실행)
4. 접시에 담기 (ResultSet 처리)
5. 설거지 (리소스 정리)

Spring JDBC (웨이터에게 주문):
1. "비빔밥 주세요" (SQL 작성)
2. 웨이터가 주방에 전달 (JdbcTemplate 호출)
3. 완성된 음식 받기 (자동 변환)
```

**코드로 보면**:
```java
// ❌ 주방에 직접 가서 요리 (순수 JDBC)
public Food cookDirectly(String recipe) {
    Kitchen kitchen = openKitchen();  // 주방 문 열기
    try {
        Ingredients ingredients = getIngredients(kitchen);
        Food food = cook(ingredients, recipe);
        Dish dish = serveDish(food);
        return dish;
    } finally {
        cleanKitchen(kitchen);  // 설거지
        closeKitchen(kitchen);  // 주방 문 닫기
    }
}

// ✅ 웨이터에게 주문 (Spring JDBC)
public Food orderFood(String recipe) {
    return waiter.order(recipe);  // 간단!
}
```

---

### 비유 3: 자동차 vs 자율주행차

**상황**: 목적지로 이동하는 방법

```
수동 운전 (순수 JDBC):
✅ 모든 것을 제어 가능
❌ 시동, 기어 변속, 브레이크, 주차 모두 수동
❌ 집중력 필요, 피곤함

자율주행 (Spring JDBC):
✅ 목적지만 입력 (SQL만 작성)
✅ 자동으로 운전 (리소스 관리 자동)
✅ 편안하게 도착 (안전하게 결과 반환)
```

**코드로 보면**:
```java
// ❌ 수동 운전 (순수 JDBC)
public void driveManually(String destination) {
    Car car = new Car();
    car.startEngine();
    car.shiftGear(1);
    try {
        while (!arrived(destination)) {
            car.accelerate();
            car.brake();
            car.turn();
        }
        car.park();
    } finally {
        car.stopEngine();
    }
}

// ✅ 자율주행 (Spring JDBC)
public void driveAutonomously(String destination) {
    autonomousCar.driveTo(destination);  // 목적지만 입력
}
```

---

## 📖 핵심 개념

### 1️⃣ 초보자 수준 설명

**Spring JDBC란?**

JDBC의 번거로운 작업을 자동화하여 데이터베이스 접근을 쉽게 만들어주는 Spring의 기술

**JdbcTemplate의 3가지 핵심 역할**:

1. **리소스 관리 자동화**
   ```java
   // JdbcTemplate이 자동으로:
   // 1. Connection 획득
   // 2. PreparedStatement 생성
   // 3. 쿼리 실행
   // 4. ResultSet 처리
   // 5. 모든 리소스 자동 close
   ```

2. **예외 처리 간소화**
   ```java
   // SQLException (Checked) → DataAccessException (Unchecked)
   // try-catch 강제 안 함
   ```

3. **코드 간결화**
   ```java
   // 30줄의 JDBC 코드 → 5줄의 JdbcTemplate 코드
   ```

**기본 사용 예시**:

```java
@Repository
@RequiredArgsConstructor
public class UserRepository {

    private final JdbcTemplate jdbcTemplate;

    // 1. 조회 (단건)
    public User findById(Long id) {
        String sql = "SELECT * FROM users WHERE id = ?";

        return jdbcTemplate.queryForObject(sql, (rs, rowNum) -> {
            User user = new User();
            user.setId(rs.getLong("id"));
            user.setName(rs.getString("name"));
            user.setEmail(rs.getString("email"));
            return user;
        }, id);
    }

    // 2. 조회 (목록)
    public List<User> findAll() {
        String sql = "SELECT * FROM users";

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            User user = new User();
            user.setId(rs.getLong("id"));
            user.setName(rs.getString("name"));
            user.setEmail(rs.getString("email"));
            return user;
        });
    }

    // 3. 삽입
    public void save(User user) {
        String sql = "INSERT INTO users (name, email) VALUES (?, ?)";
        jdbcTemplate.update(sql, user.getName(), user.getEmail());
    }

    // 4. 수정
    public void update(User user) {
        String sql = "UPDATE users SET name = ?, email = ? WHERE id = ?";
        jdbcTemplate.update(sql, user.getName(), user.getEmail(), user.getId());
    }

    // 5. 삭제
    public void deleteById(Long id) {
        String sql = "DELETE FROM users WHERE id = ?";
        jdbcTemplate.update(sql, id);
    }

    // 6. 카운트
    public int count() {
        String sql = "SELECT COUNT(*) FROM users";
        return jdbcTemplate.queryForObject(sql, Integer.class);
    }
}
```

---

### 2️⃣ 중급자 수준 설명

**JdbcTemplate의 주요 메서드**

| 메서드 | 용도 | 반환 타입 | 예시 |
|--------|------|-----------|------|
| `query()` | 여러 행 조회 | `List<T>` | 사용자 목록 |
| `queryForObject()` | 단일 행 조회 | `T` | ID로 사용자 조회 |
| `queryForList()` | 단순 타입 목록 | `List<Map>` | 이름 목록 |
| `update()` | INSERT/UPDATE/DELETE | `int` | 영향받은 행 수 |
| `batchUpdate()` | 대량 INSERT/UPDATE | `int[]` | 1000건 삽입 |
| `execute()` | DDL 또는 프로시저 | `void` | 테이블 생성 |

**1. RowMapper 활용**

```java
@Repository
public class UserRepository {

    private final JdbcTemplate jdbcTemplate;
    private final RowMapper<User> userRowMapper;

    public UserRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;

        // RowMapper 재사용
        this.userRowMapper = (rs, rowNum) -> {
            User user = new User();
            user.setId(rs.getLong("id"));
            user.setName(rs.getString("name"));
            user.setEmail(rs.getString("email"));
            user.setCreatedAt(rs.getTimestamp("created_at").toLocalDateTime());
            return user;
        };
    }

    public User findById(Long id) {
        String sql = "SELECT * FROM users WHERE id = ?";
        return jdbcTemplate.queryForObject(sql, userRowMapper, id);
    }

    public List<User> findAll() {
        String sql = "SELECT * FROM users";
        return jdbcTemplate.query(sql, userRowMapper);
    }

    public List<User> findByName(String name) {
        String sql = "SELECT * FROM users WHERE name LIKE ?";
        return jdbcTemplate.query(sql, userRowMapper, "%" + name + "%");
    }
}
```

**2. ResultSetExtractor 활용 (복잡한 결과 처리)**

```java
@Repository
public class OrderRepository {

    private final JdbcTemplate jdbcTemplate;

    // 주문과 주문 항목을 한 번에 조회 (1:N 관계)
    public Order findByIdWithItems(Long orderId) {
        String sql = """
            SELECT o.id as order_id, o.total_amount, o.created_at,
                   oi.id as item_id, oi.product_id, oi.quantity, oi.unit_price
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.id = ?
        """;

        return jdbcTemplate.query(sql, rs -> {
            Order order = null;

            while (rs.next()) {
                if (order == null) {
                    // 첫 행에서 Order 생성
                    order = new Order();
                    order.setId(rs.getLong("order_id"));
                    order.setTotalAmount(rs.getBigDecimal("total_amount"));
                    order.setCreatedAt(rs.getTimestamp("created_at").toLocalDateTime());
                    order.setOrderItems(new ArrayList<>());
                }

                // 각 행에서 OrderItem 추가
                if (rs.getObject("item_id") != null) {
                    OrderItem item = new OrderItem();
                    item.setId(rs.getLong("item_id"));
                    item.setProductId(rs.getLong("product_id"));
                    item.setQuantity(rs.getInt("quantity"));
                    item.setUnitPrice(rs.getBigDecimal("unit_price"));

                    order.getOrderItems().add(item);
                }
            }

            return order;
        }, orderId);
    }
}
```

**3. NamedParameterJdbcTemplate (Named Parameters)**

```java
@Repository
@RequiredArgsConstructor
public class ProductRepository {

    private final NamedParameterJdbcTemplate namedJdbcTemplate;

    public List<Product> findByConditions(String name, BigDecimal minPrice, BigDecimal maxPrice) {
        String sql = """
            SELECT * FROM products
            WHERE (:name IS NULL OR name LIKE :name)
              AND (:minPrice IS NULL OR price >= :minPrice)
              AND (:maxPrice IS NULL OR price <= :maxPrice)
        """;

        MapSqlParameterSource params = new MapSqlParameterSource()
            .addValue("name", name != null ? "%" + name + "%" : null)
            .addValue("minPrice", minPrice)
            .addValue("maxPrice", maxPrice);

        return namedJdbcTemplate.query(sql, params, (rs, rowNum) -> {
            Product product = new Product();
            product.setId(rs.getLong("id"));
            product.setName(rs.getString("name"));
            product.setPrice(rs.getBigDecimal("price"));
            return product;
        });
    }

    // SqlParameterSource로 객체 매핑
    public void save(Product product) {
        String sql = "INSERT INTO products (name, price) VALUES (:name, :price)";

        SqlParameterSource params = new BeanPropertySqlParameterSource(product);

        namedJdbcTemplate.update(sql, params);
    }
}
```

**4. Batch Update (대량 처리)**

```java
@Repository
@RequiredArgsConstructor
public class UserRepository {

    private final JdbcTemplate jdbcTemplate;

    public void saveAll(List<User> users) {
        String sql = "INSERT INTO users (name, email) VALUES (?, ?)";

        jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
            @Override
            public void setValues(PreparedStatement ps, int i) throws SQLException {
                User user = users.get(i);
                ps.setString(1, user.getName());
                ps.setString(2, user.getEmail());
            }

            @Override
            public int getBatchSize() {
                return users.size();
            }
        });
    }

    // NamedParameterJdbcTemplate 사용 (더 간결)
    public void saveAllNamed(List<User> users) {
        String sql = "INSERT INTO users (name, email) VALUES (:name, :email)";

        SqlParameterSource[] batchParams = users.stream()
            .map(BeanPropertySqlParameterSource::new)
            .toArray(SqlParameterSource[]::new);

        namedJdbcTemplate.batchUpdate(sql, batchParams);
    }
}
```

---

### 3️⃣ 고급자 수준 설명

**SimpleJdbcInsert (자동 생성 키 반환)**

```java
@Repository
public class UserRepository {

    private final SimpleJdbcInsert simpleJdbcInsert;

    public UserRepository(DataSource dataSource) {
        this.simpleJdbcInsert = new SimpleJdbcInsert(dataSource)
            .withTableName("users")
            .usingGeneratedKeyColumns("id");  // Auto-increment 컬럼
    }

    public User save(User user) {
        Map<String, Object> parameters = new HashMap<>();
        parameters.put("name", user.getName());
        parameters.put("email", user.getEmail());

        // INSERT 후 생성된 ID 반환
        Number generatedId = simpleJdbcInsert.executeAndReturnKey(parameters);

        user.setId(generatedId.longValue());

        return user;
    }

    // BeanPropertySqlParameterSource 사용
    public User saveWithBean(User user) {
        SqlParameterSource params = new BeanPropertySqlParameterSource(user);

        Number generatedId = simpleJdbcInsert.executeAndReturnKey(params);

        user.setId(generatedId.longValue());

        return user;
    }
}
```

**SimpleJdbcCall (Stored Procedure 호출)**

```java
@Repository
public class OrderRepository {

    private final SimpleJdbcCall simpleJdbcCall;

    public OrderRepository(DataSource dataSource) {
        this.simpleJdbcCall = new SimpleJdbcCall(dataSource)
            .withProcedureName("calculate_order_total");  // 프로시저 이름
    }

    public BigDecimal calculateOrderTotal(Long orderId) {
        SqlParameterSource params = new MapSqlParameterSource()
            .addValue("order_id", orderId);

        Map<String, Object> result = simpleJdbcCall.execute(params);

        return (BigDecimal) result.get("total");
    }
}
```

**Custom RowMapper with Inheritance**

```java
public abstract class AbstractRowMapper<T> implements RowMapper<T> {

    protected Long getLong(ResultSet rs, String columnName) throws SQLException {
        long value = rs.getLong(columnName);
        return rs.wasNull() ? null : value;
    }

    protected LocalDateTime getLocalDateTime(ResultSet rs, String columnName) throws SQLException {
        Timestamp timestamp = rs.getTimestamp(columnName);
        return timestamp != null ? timestamp.toLocalDateTime() : null;
    }

    protected <E extends Enum<E>> E getEnum(ResultSet rs, String columnName, Class<E> enumType) throws SQLException {
        String value = rs.getString(columnName);
        return value != null ? Enum.valueOf(enumType, value) : null;
    }
}

public class UserRowMapper extends AbstractRowMapper<User> {

    @Override
    public User mapRow(ResultSet rs, int rowNum) throws SQLException {
        User user = new User();
        user.setId(getLong(rs, "id"));
        user.setName(rs.getString("name"));
        user.setEmail(rs.getString("email"));
        user.setCreatedAt(getLocalDateTime(rs, "created_at"));
        user.setStatus(getEnum(rs, "status", UserStatus.class));
        return user;
    }
}
```

**트랜잭션 관리와 통합**

```java
@Service
@RequiredArgsConstructor
@Transactional
public class OrderService {

    private final OrderRepository orderRepository;
    private final ProductRepository productRepository;
    private final JdbcTemplate jdbcTemplate;

    public Order createOrder(OrderRequest request) {
        // 1. 주문 생성 (JdbcTemplate)
        Order order = orderRepository.save(new Order(request));

        // 2. 재고 차감 (SQL 직접 실행)
        String sql = "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?";

        for (OrderItemRequest item : request.getItems()) {
            int updated = jdbcTemplate.update(sql, item.getQuantity(), item.getProductId());

            if (updated == 0) {
                throw new ProductNotFoundException("상품을 찾을 수 없습니다: " + item.getProductId());
            }
        }

        // 3. 주문 항목 저장 (Batch Insert)
        saveOrderItems(order.getId(), request.getItems());

        // 모두 성공 시 트랜잭션 커밋, 실패 시 롤백

        return order;
    }

    private void saveOrderItems(Long orderId, List<OrderItemRequest> items) {
        String sql = """
            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            VALUES (?, ?, ?, ?)
        """;

        jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
            @Override
            public void setValues(PreparedStatement ps, int i) throws SQLException {
                OrderItemRequest item = items.get(i);
                ps.setLong(1, orderId);
                ps.setLong(2, item.getProductId());
                ps.setInt(3, item.getQuantity());
                ps.setBigDecimal(4, item.getUnitPrice());
            }

            @Override
            public int getBatchSize() {
                return items.size();
            }
        });
    }
}
```

---

## 💻 기본 실습

### 실습 1: JdbcTemplate 기본 CRUD

**난이도**: ⭐⭐☆☆☆

#### 1. 의존성 추가 (build.gradle)

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-jdbc'
    runtimeOnly 'com.mysql:mysql-connector-j'
}
```

#### 2. 데이터베이스 설정 (application.yml)

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/testdb
    username: root
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver

    hikari:
      maximum-pool-size: 10
      minimum-idle: 5
```

#### 3. 테이블 생성 (schema.sql)

```sql
CREATE TABLE IF NOT EXISTS products (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. Entity 클래스

```java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Product {
    private Long id;
    private String name;
    private BigDecimal price;
    private Integer stockQuantity;
    private LocalDateTime createdAt;
}
```

#### 5. Repository 구현

```java
@Repository
@RequiredArgsConstructor
public class ProductRepository {

    private final JdbcTemplate jdbcTemplate;

    // RowMapper 정의
    private final RowMapper<Product> productRowMapper = (rs, rowNum) -> {
        Product product = new Product();
        product.setId(rs.getLong("id"));
        product.setName(rs.getString("name"));
        product.setPrice(rs.getBigDecimal("price"));
        product.setStockQuantity(rs.getInt("stock_quantity"));
        product.setCreatedAt(rs.getTimestamp("created_at").toLocalDateTime());
        return product;
    };

    // CREATE
    public Product save(Product product) {
        String sql = "INSERT INTO products (name, price, stock_quantity) VALUES (?, ?, ?)";

        KeyHolder keyHolder = new GeneratedKeyHolder();

        jdbcTemplate.update(connection -> {
            PreparedStatement ps = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setString(1, product.getName());
            ps.setBigDecimal(2, product.getPrice());
            ps.setInt(3, product.getStockQuantity());
            return ps;
        }, keyHolder);

        product.setId(keyHolder.getKey().longValue());

        return product;
    }

    // READ (단건)
    public Optional<Product> findById(Long id) {
        String sql = "SELECT * FROM products WHERE id = ?";

        try {
            Product product = jdbcTemplate.queryForObject(sql, productRowMapper, id);
            return Optional.ofNullable(product);
        } catch (EmptyResultDataAccessException e) {
            return Optional.empty();
        }
    }

    // READ (전체)
    public List<Product> findAll() {
        String sql = "SELECT * FROM products ORDER BY created_at DESC";
        return jdbcTemplate.query(sql, productRowMapper);
    }

    // READ (검색)
    public List<Product> findByNameContaining(String keyword) {
        String sql = "SELECT * FROM products WHERE name LIKE ?";
        return jdbcTemplate.query(sql, productRowMapper, "%" + keyword + "%");
    }

    // UPDATE
    public void update(Product product) {
        String sql = "UPDATE products SET name = ?, price = ?, stock_quantity = ? WHERE id = ?";

        jdbcTemplate.update(sql,
            product.getName(),
            product.getPrice(),
            product.getStockQuantity(),
            product.getId()
        );
    }

    // DELETE
    public void deleteById(Long id) {
        String sql = "DELETE FROM products WHERE id = ?";
        jdbcTemplate.update(sql, id);
    }

    // COUNT
    public int count() {
        String sql = "SELECT COUNT(*) FROM products";
        return jdbcTemplate.queryForObject(sql, Integer.class);
    }
}
```

#### 6. Service 구현

```java
@Service
@RequiredArgsConstructor
@Transactional
public class ProductService {

    private final ProductRepository productRepository;

    public Product createProduct(ProductRequest request) {
        Product product = new Product();
        product.setName(request.getName());
        product.setPrice(request.getPrice());
        product.setStockQuantity(request.getStockQuantity());

        return productRepository.save(product);
    }

    @Transactional(readOnly = true)
    public Product getProduct(Long id) {
        return productRepository.findById(id)
            .orElseThrow(() -> new ProductNotFoundException("상품을 찾을 수 없습니다: " + id));
    }

    @Transactional(readOnly = true)
    public List<Product> getAllProducts() {
        return productRepository.findAll();
    }

    @Transactional(readOnly = true)
    public List<Product> searchProducts(String keyword) {
        return productRepository.findByNameContaining(keyword);
    }

    public Product updateProduct(Long id, ProductRequest request) {
        Product product = getProduct(id);
        product.setName(request.getName());
        product.setPrice(request.getPrice());
        product.setStockQuantity(request.getStockQuantity());

        productRepository.update(product);

        return product;
    }

    public void deleteProduct(Long id) {
        productRepository.deleteById(id);
    }
}
```

#### 7. Controller 구현

```java
@RestController
@RequestMapping("/api/products")
@RequiredArgsConstructor
public class ProductController {

    private final ProductService productService;

    @PostMapping
    public ResponseEntity<Product> createProduct(@RequestBody @Valid ProductRequest request) {
        Product product = productService.createProduct(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(product);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Product> getProduct(@PathVariable Long id) {
        Product product = productService.getProduct(id);
        return ResponseEntity.ok(product);
    }

    @GetMapping
    public ResponseEntity<List<Product>> getAllProducts() {
        List<Product> products = productService.getAllProducts();
        return ResponseEntity.ok(products);
    }

    @GetMapping("/search")
    public ResponseEntity<List<Product>> searchProducts(@RequestParam String keyword) {
        List<Product> products = productService.searchProducts(keyword);
        return ResponseEntity.ok(products);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Product> updateProduct(
            @PathVariable Long id,
            @RequestBody @Valid ProductRequest request) {

        Product product = productService.updateProduct(id, request);
        return ResponseEntity.ok(product);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteProduct(@PathVariable Long id) {
        productService.deleteProduct(id);
        return ResponseEntity.noContent().build();
    }
}
```

---

### 실습 2: NamedParameterJdbcTemplate 활용

**난이도**: ⭐⭐⭐☆☆

#### 동적 쿼리 구현

```java
@Repository
@RequiredArgsConstructor
public class ProductSearchRepository {

    private final NamedParameterJdbcTemplate namedJdbcTemplate;

    public List<Product> search(ProductSearchCondition condition) {
        StringBuilder sql = new StringBuilder("""
            SELECT * FROM products
            WHERE 1=1
        """);

        MapSqlParameterSource params = new MapSqlParameterSource();

        // 동적 쿼리 조건 추가
        if (condition.getName() != null) {
            sql.append(" AND name LIKE :name");
            params.addValue("name", "%" + condition.getName() + "%");
        }

        if (condition.getMinPrice() != null) {
            sql.append(" AND price >= :minPrice");
            params.addValue("minPrice", condition.getMinPrice());
        }

        if (condition.getMaxPrice() != null) {
            sql.append(" AND price <= :maxPrice");
            params.addValue("maxPrice", condition.getMaxPrice());
        }

        if (condition.getMinStock() != null) {
            sql.append(" AND stock_quantity >= :minStock");
            params.addValue("minStock", condition.getMinStock());
        }

        sql.append(" ORDER BY created_at DESC");

        return namedJdbcTemplate.query(sql.toString(), params, (rs, rowNum) -> {
            Product product = new Product();
            product.setId(rs.getLong("id"));
            product.setName(rs.getString("name"));
            product.setPrice(rs.getBigDecimal("price"));
            product.setStockQuantity(rs.getInt("stock_quantity"));
            product.setCreatedAt(rs.getTimestamp("created_at").toLocalDateTime());
            return product;
        });
    }
}

@Data
public class ProductSearchCondition {
    private String name;
    private BigDecimal minPrice;
    private BigDecimal maxPrice;
    private Integer minStock;
}
```

---

## 🏢 실무 활용 사례

### 사례 1: 쿠팡 - 복잡한 통계 쿼리

**배경**:
쿠팡이 매출 통계와 리포팅을 위해 복잡한 SQL을 직접 제어해야 하는 상황

**요구사항**:
- 일별/월별/연도별 매출 통계
- 카테고리별 판매 순위
- 복잡한 GROUP BY, JOIN, 서브쿼리
- 성능 최적화를 위한 SQL 튜닝

**구현 코드**:

```java
@Repository
@RequiredArgsConstructor
@Slf4j
public class SalesStatisticsRepository {

    private final JdbcTemplate jdbcTemplate;

    // 일별 매출 통계
    public List<DailySalesStatistics> getDailySalesStatistics(
            LocalDate startDate, LocalDate endDate) {

        String sql = """
            SELECT
                DATE(o.created_at) as sales_date,
                COUNT(DISTINCT o.id) as order_count,
                COUNT(DISTINCT o.user_id) as customer_count,
                SUM(o.total_amount) as total_sales,
                AVG(o.total_amount) as avg_order_amount,
                SUM(oi.quantity) as total_quantity
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE o.created_at >= ?
              AND o.created_at < ?
              AND o.status = 'COMPLETED'
            GROUP BY DATE(o.created_at)
            ORDER BY sales_date DESC
        """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            DailySalesStatistics stats = new DailySalesStatistics();
            stats.setSalesDate(rs.getDate("sales_date").toLocalDate());
            stats.setOrderCount(rs.getInt("order_count"));
            stats.setCustomerCount(rs.getInt("customer_count"));
            stats.setTotalSales(rs.getBigDecimal("total_sales"));
            stats.setAvgOrderAmount(rs.getBigDecimal("avg_order_amount"));
            stats.setTotalQuantity(rs.getInt("total_quantity"));
            return stats;
        }, startDate, endDate.plusDays(1));
    }

    // 카테고리별 베스트셀러
    public List<CategoryBestseller> getCategoryBestsellers(int topN) {
        String sql = """
            SELECT
                c.id as category_id,
                c.name as category_name,
                p.id as product_id,
                p.name as product_name,
                SUM(oi.quantity) as total_quantity,
                SUM(oi.quantity * oi.unit_price) as total_sales,
                RANK() OVER (PARTITION BY c.id ORDER BY SUM(oi.quantity) DESC) as ranking
            FROM categories c
            JOIN products p ON c.id = p.category_id
            JOIN order_items oi ON p.id = oi.product_id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status = 'COMPLETED'
              AND o.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY c.id, c.name, p.id, p.name
            HAVING ranking <= ?
            ORDER BY c.id, ranking
        """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            CategoryBestseller bestseller = new CategoryBestseller();
            bestseller.setCategoryId(rs.getLong("category_id"));
            bestseller.setCategoryName(rs.getString("category_name"));
            bestseller.setProductId(rs.getLong("product_id"));
            bestseller.setProductName(rs.getString("product_name"));
            bestseller.setTotalQuantity(rs.getInt("total_quantity"));
            bestseller.setTotalSales(rs.getBigDecimal("total_sales"));
            bestseller.setRanking(rs.getInt("ranking"));
            return bestseller;
        }, topN);
    }

    // 시간대별 주문 분포 (피크 타임 분석)
    public List<HourlyOrderDistribution> getHourlyOrderDistribution() {
        String sql = """
            SELECT
                HOUR(created_at) as hour,
                COUNT(*) as order_count,
                AVG(total_amount) as avg_amount,
                SUM(total_amount) as total_amount
            FROM orders
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
              AND status = 'COMPLETED'
            GROUP BY HOUR(created_at)
            ORDER BY hour
        """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            HourlyOrderDistribution distribution = new HourlyOrderDistribution();
            distribution.setHour(rs.getInt("hour"));
            distribution.setOrderCount(rs.getInt("order_count"));
            distribution.setAvgAmount(rs.getBigDecimal("avg_amount"));
            distribution.setTotalAmount(rs.getBigDecimal("total_amount"));
            return distribution;
        });
    }

    // 고객 세그먼트 분석 (RFM 분석)
    public List<CustomerSegment> getCustomerSegments() {
        String sql = """
            SELECT
                user_id,
                DATEDIFF(NOW(), MAX(created_at)) as recency,
                COUNT(*) as frequency,
                SUM(total_amount) as monetary,
                CASE
                    WHEN DATEDIFF(NOW(), MAX(created_at)) <= 30 AND COUNT(*) >= 10 THEN 'VIP'
                    WHEN DATEDIFF(NOW(), MAX(created_at)) <= 60 AND COUNT(*) >= 5 THEN '우수'
                    WHEN DATEDIFF(NOW(), MAX(created_at)) <= 90 THEN '일반'
                    ELSE '휴면'
                END as segment
            FROM orders
            WHERE status = 'COMPLETED'
            GROUP BY user_id
            ORDER BY monetary DESC
        """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            CustomerSegment segment = new CustomerSegment();
            segment.setUserId(rs.getLong("user_id"));
            segment.setRecency(rs.getInt("recency"));
            segment.setFrequency(rs.getInt("frequency"));
            segment.setMonetary(rs.getBigDecimal("monetary"));
            segment.setSegment(rs.getString("segment"));
            return segment;
        });
    }
}
```

**성과**:
- 복잡한 SQL을 직접 작성하여 **성능 30% 향상**
- JPQL로는 불가능한 Window Function 활용
- 대용량 데이터 집계 시 **JPA 대비 5배 빠른 속도**

---

### 사례 2: 배달의민족 - 대량 데이터 배치 처리

**배경**:
매일 수백만 건의 주문 데이터를 배치로 처리하여 정산 시스템에 전달

**요구사항**:
- 대량 INSERT/UPDATE 성능 최적화
- 메모리 효율적 처리
- 트랜잭션 단위 처리
- 실패 시 재처리 가능

**구현 코드**:

```java
@Component
@RequiredArgsConstructor
@Slf4j
public class SettlementBatchProcessor {

    private final JdbcTemplate jdbcTemplate;
    private final NamedParameterJdbcTemplate namedJdbcTemplate;

    // 대량 INSERT (Batch)
    @Transactional
    public void processSettlement(LocalDate targetDate) {
        log.info("Starting settlement batch for date: {}", targetDate);

        // 1. 정산 대상 주문 조회
        List<Order> orders = getCompletedOrders(targetDate);
        log.info("Found {} orders to settle", orders.size());

        // 2. 정산 데이터 생성 (Batch Insert)
        insertSettlements(orders);

        // 3. 주문 상태 업데이트 (Batch Update)
        updateOrderStatus(orders);

        log.info("Settlement batch completed for {} orders", orders.size());
    }

    private List<Order> getCompletedOrders(LocalDate targetDate) {
        String sql = """
            SELECT id, user_id, restaurant_id, total_amount, delivery_fee
            FROM orders
            WHERE DATE(completed_at) = ?
              AND status = 'COMPLETED'
              AND settlement_id IS NULL
        """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            Order order = new Order();
            order.setId(rs.getLong("id"));
            order.setUserId(rs.getLong("user_id"));
            order.setRestaurantId(rs.getLong("restaurant_id"));
            order.setTotalAmount(rs.getBigDecimal("total_amount"));
            order.setDeliveryFee(rs.getBigDecimal("delivery_fee"));
            return order;
        }, targetDate);
    }

    private void insertSettlements(List<Order> orders) {
        String sql = """
            INSERT INTO settlements (
                order_id, restaurant_id, order_amount, delivery_fee,
                commission_rate, commission_amount, settlement_amount,
                settlement_date, status
            ) VALUES (
                :orderId, :restaurantId, :orderAmount, :deliveryFee,
                :commissionRate, :commissionAmount, :settlementAmount,
                :settlementDate, :status
            )
        """;

        SqlParameterSource[] batchParams = orders.stream()
            .map(order -> {
                BigDecimal commissionRate = BigDecimal.valueOf(0.15); // 15% 수수료
                BigDecimal commissionAmount = order.getTotalAmount().multiply(commissionRate);
                BigDecimal settlementAmount = order.getTotalAmount()
                    .subtract(commissionAmount)
                    .add(order.getDeliveryFee());

                return new MapSqlParameterSource()
                    .addValue("orderId", order.getId())
                    .addValue("restaurantId", order.getRestaurantId())
                    .addValue("orderAmount", order.getTotalAmount())
                    .addValue("deliveryFee", order.getDeliveryFee())
                    .addValue("commissionRate", commissionRate)
                    .addValue("commissionAmount", commissionAmount)
                    .addValue("settlementAmount", settlementAmount)
                    .addValue("settlementDate", LocalDate.now())
                    .addValue("status", "PENDING");
            })
            .toArray(SqlParameterSource[]::new);

        // Batch Insert 실행
        namedJdbcTemplate.batchUpdate(sql, batchParams);

        log.info("Inserted {} settlement records", orders.size());
    }

    private void updateOrderStatus(List<Order> orders) {
        String sql = """
            UPDATE orders
            SET settlement_id = (
                SELECT id FROM settlements WHERE order_id = ?
            )
            WHERE id = ?
        """;

        jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
            @Override
            public void setValues(PreparedStatement ps, int i) throws SQLException {
                Order order = orders.get(i);
                ps.setLong(1, order.getId());
                ps.setLong(2, order.getId());
            }

            @Override
            public int getBatchSize() {
                return orders.size();
            }
        });

        log.info("Updated {} order status", orders.size());
    }

    // 청크 단위 처리 (메모리 효율적)
    @Transactional
    public void processSettlementInChunks(LocalDate targetDate, int chunkSize) {
        int offset = 0;
        int processedCount = 0;

        while (true) {
            List<Order> chunk = getCompletedOrdersWithPaging(targetDate, offset, chunkSize);

            if (chunk.isEmpty()) {
                break;
            }

            insertSettlements(chunk);
            updateOrderStatus(chunk);

            processedCount += chunk.size();
            offset += chunkSize;

            log.info("Processed chunk: offset={}, count={}", offset, chunk.size());
        }

        log.info("Total processed: {} orders", processedCount);
    }

    private List<Order> getCompletedOrdersWithPaging(
            LocalDate targetDate, int offset, int limit) {

        String sql = """
            SELECT id, user_id, restaurant_id, total_amount, delivery_fee
            FROM orders
            WHERE DATE(completed_at) = ?
              AND status = 'COMPLETED'
              AND settlement_id IS NULL
            ORDER BY id
            LIMIT ? OFFSET ?
        """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            Order order = new Order();
            order.setId(rs.getLong("id"));
            order.setUserId(rs.getLong("user_id"));
            order.setRestaurantId(rs.getLong("restaurant_id"));
            order.setTotalAmount(rs.getBigDecimal("total_amount"));
            order.setDeliveryFee(rs.getBigDecimal("delivery_fee"));
            return order;
        }, targetDate, limit, offset);
    }
}
```

**스케줄러 설정**:

```java
@Component
@RequiredArgsConstructor
@Slf4j
public class SettlementScheduler {

    private final SettlementBatchProcessor batchProcessor;

    // 매일 새벽 2시에 전날 정산 처리
    @Scheduled(cron = "0 0 2 * * *")
    public void runDailySettlement() {
        LocalDate yesterday = LocalDate.now().minusDays(1);

        try {
            log.info("Starting daily settlement for {}", yesterday);
            batchProcessor.processSettlementInChunks(yesterday, 1000);
            log.info("Daily settlement completed successfully");
        } catch (Exception e) {
            log.error("Daily settlement failed for {}", yesterday, e);
            // 알림 발송, 재처리 로직 등
        }
    }
}
```

**성과**:
- Batch Insert로 **처리 속도 10배 향상** (1000건/초 → 10000건/초)
- 메모리 사용량 **90% 감소** (청크 처리)
- 대량 데이터 처리 시 **JPA 대비 5배 빠름**

---

## 🎯 주니어 시나리오

### 시나리오 1: "queryForObject가 예외를 던져요!"

**상황**:
데이터가 없을 때 `EmptyResultDataAccessException`이 발생합니다.

**문제 코드**:
```java
@Repository
public class UserRepository {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    // ❌ 데이터가 없으면 예외 발생!
    public User findById(Long id) {
        String sql = "SELECT * FROM users WHERE id = ?";

        // EmptyResultDataAccessException 발생 가능
        return jdbcTemplate.queryForObject(sql, (rs, rowNum) -> {
            User user = new User();
            user.setId(rs.getLong("id"));
            user.setName(rs.getString("name"));
            return user;
        }, id);
    }
}
```

**문제 발생**:
```java
User user = userRepository.findById(999L);
// → EmptyResultDataAccessException: Incorrect result size: expected 1, actual 0
```

**해결책 1: Optional 반환**:
```java
public Optional<User> findById(Long id) {
    String sql = "SELECT * FROM users WHERE id = ?";

    try {
        User user = jdbcTemplate.queryForObject(sql, userRowMapper, id);
        return Optional.ofNullable(user);
    } catch (EmptyResultDataAccessException e) {
        return Optional.empty();
    }
}

// 사용
User user = userRepository.findById(999L)
    .orElseThrow(() -> new UserNotFoundException("User not found: 999"));
```

**해결책 2: query() 사용 후 첫 번째 요소 반환**:
```java
public Optional<User> findById(Long id) {
    String sql = "SELECT * FROM users WHERE id = ?";

    List<User> users = jdbcTemplate.query(sql, userRowMapper, id);

    return users.isEmpty() ? Optional.empty() : Optional.of(users.get(0));
}
```

**해결책 3: Custom Exception Handler**:
```java
public User findById(Long id) {
    String sql = "SELECT * FROM users WHERE id = ?";

    try {
        return jdbcTemplate.queryForObject(sql, userRowMapper, id);
    } catch (EmptyResultDataAccessException e) {
        throw new UserNotFoundException("사용자를 찾을 수 없습니다: " + id);
    }
}
```

---

### 시나리오 2: "SQL Injection 취약점이 있어요!"

**상황**:
문자열 연결로 SQL을 만들어 SQL Injection 위험이 있습니다.

**문제 코드**:
```java
// ❌ SQL Injection 위험!
public List<User> findByName(String name) {
    String sql = "SELECT * FROM users WHERE name = '" + name + "'";

    return jdbcTemplate.query(sql, userRowMapper);
}

// 공격 예시
String maliciousName = "admin' OR '1'='1";
List<User> users = userRepository.findByName(maliciousName);
// 실행되는 SQL: SELECT * FROM users WHERE name = 'admin' OR '1'='1'
// → 모든 사용자 조회됨!
```

**해결책 1: PreparedStatement 사용 (권장)**:
```java
// ✅ PreparedStatement로 안전
public List<User> findByName(String name) {
    String sql = "SELECT * FROM users WHERE name = ?";

    return jdbcTemplate.query(sql, userRowMapper, name);
}

// 공격 시도해도 안전
String maliciousName = "admin' OR '1'='1";
List<User> users = userRepository.findByName(maliciousName);
// 실행되는 SQL: SELECT * FROM users WHERE name = 'admin'' OR ''1''=''1'
// → name이 정확히 "admin' OR '1'='1"인 사용자만 조회 (없음)
```

**해결책 2: NamedParameterJdbcTemplate 사용**:
```java
@Repository
@RequiredArgsConstructor
public class UserRepository {

    private final NamedParameterJdbcTemplate namedJdbcTemplate;

    public List<User> findByName(String name) {
        String sql = "SELECT * FROM users WHERE name = :name";

        MapSqlParameterSource params = new MapSqlParameterSource()
            .addValue("name", name);

        return namedJdbcTemplate.query(sql, params, userRowMapper);
    }
}
```

**해결책 3: 입력 검증 추가**:
```java
public List<User> findByName(String name) {
    // 입력 검증
    if (name == null || name.contains("'") || name.contains("--")) {
        throw new IllegalArgumentException("Invalid name parameter");
    }

    String sql = "SELECT * FROM users WHERE name = ?";

    return jdbcTemplate.query(sql, userRowMapper, name);
}
```

**배운 점**:
```
✅ 항상 PreparedStatement 사용 (?, :name)
❌ 절대 문자열 연결로 SQL 생성 금지
✅ 입력 값 검증
✅ NamedParameterJdbcTemplate 활용
```

---

### 시나리오 3: "Batch Update가 느려요!"

**상황**:
1000건의 데이터를 삽입하는데 시간이 오래 걸립니다.

**문제 코드**:
```java
// ❌ 느림: 1000번의 DB 호출
@Transactional
public void saveAll(List<User> users) {
    String sql = "INSERT INTO users (name, email) VALUES (?, ?)";

    for (User user : users) {
        jdbcTemplate.update(sql, user.getName(), user.getEmail());
    }
    // 1000건 → 1000번 DB 호출 → 10초 소요
}
```

**해결책 1: batchUpdate 사용**:
```java
// ✅ 빠름: Batch로 한 번에 처리
@Transactional
public void saveAll(List<User> users) {
    String sql = "INSERT INTO users (name, email) VALUES (?, ?)";

    jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
        @Override
        public void setValues(PreparedStatement ps, int i) throws SQLException {
            User user = users.get(i);
            ps.setString(1, user.getName());
            ps.setString(2, user.getEmail());
        }

        @Override
        public int getBatchSize() {
            return users.size();
        }
    });
    // 1000건 → 1번 Batch 호출 → 1초 소요
}
```

**해결책 2: NamedParameterJdbcTemplate 사용 (더 간결)**:
```java
@Transactional
public void saveAll(List<User> users) {
    String sql = "INSERT INTO users (name, email) VALUES (:name, :email)";

    SqlParameterSource[] batchParams = users.stream()
        .map(user -> new MapSqlParameterSource()
            .addValue("name", user.getName())
            .addValue("email", user.getEmail()))
        .toArray(SqlParameterSource[]::new);

    namedJdbcTemplate.batchUpdate(sql, batchParams);
}
```

**성능 비교**:
```
1000건 INSERT:
- 개별 update(): ~10초
- batchUpdate(): ~1초
→ 10배 빠름!

10000건 INSERT:
- 개별 update(): ~100초
- batchUpdate(): ~5초
→ 20배 빠름!
```

---

### 시나리오 4: "트랜잭션이 적용 안 돼요!"

**상황**:
JdbcTemplate 사용 시 트랜잭션이 롤백되지 않습니다.

**문제 코드**:
```java
// ❌ @Transactional 누락
public void createOrderWithItems(Order order, List<OrderItem> items) {
    // 1. 주문 삽입
    String orderSql = "INSERT INTO orders (user_id, total_amount) VALUES (?, ?)";
    jdbcTemplate.update(orderSql, order.getUserId(), order.getTotalAmount());

    // 2. 주문 항목 삽입 (여기서 예외 발생)
    String itemSql = "INSERT INTO order_items (order_id, product_id) VALUES (?, ?)";

    for (OrderItem item : items) {
        jdbcTemplate.update(itemSql, order.getId(), item.getProductId());
        // → 예외 발생해도 주문은 그대로 저장됨! (트랜잭션 없음)
    }
}
```

**해결책 1: @Transactional 추가**:
```java
// ✅ @Transactional로 트랜잭션 관리
@Transactional
public void createOrderWithItems(Order order, List<OrderItem> items) {
    // 1. 주문 삽입
    String orderSql = "INSERT INTO orders (user_id, total_amount) VALUES (?, ?)";
    jdbcTemplate.update(orderSql, order.getUserId(), order.getTotalAmount());

    // 2. 주문 항목 삽입
    String itemSql = "INSERT INTO order_items (order_id, product_id) VALUES (?, ?)";

    for (OrderItem item : items) {
        jdbcTemplate.update(itemSql, order.getId(), item.getProductId());
    }

    // 예외 발생 시 모두 롤백됨!
}
```

**해결책 2: TransactionTemplate 사용**:
```java
@Autowired
private TransactionTemplate transactionTemplate;

public void createOrderWithItems(Order order, List<OrderItem> items) {
    transactionTemplate.execute(status -> {
        try {
            // 1. 주문 삽입
            String orderSql = "INSERT INTO orders (user_id, total_amount) VALUES (?, ?)";
            jdbcTemplate.update(orderSql, order.getUserId(), order.getTotalAmount());

            // 2. 주문 항목 삽입
            String itemSql = "INSERT INTO order_items (order_id, product_id) VALUES (?, ?)";

            for (OrderItem item : items) {
                jdbcTemplate.update(itemSql, order.getId(), item.getProductId());
            }

            return null;
        } catch (Exception e) {
            status.setRollbackOnly();
            throw e;
        }
    });
}
```

**배운 점**:
```
✅ JdbcTemplate 사용 시에도 @Transactional 필요
✅ 여러 쿼리가 하나의 작업 단위면 반드시 트랜잭션 사용
✅ Service 계층에서 트랜잭션 관리
```

---

## 🚀 실전 프로젝트: 전자상거래 주문 시스템 (계속)

이 부분은 Chapter 19에서 시작한 프로젝트를 Spring JDBC로 구현하는 버전입니다.

### JdbcTemplate 버전 Repository

```java
@Repository
@RequiredArgsConstructor
public class OrderJdbcRepository {

    private final JdbcTemplate jdbcTemplate;
    private final NamedParameterJdbcTemplate namedJdbcTemplate;

    public Order save(Order order) {
        String sql = """
            INSERT INTO orders (user_id, status, total_amount, order_date)
            VALUES (?, ?, ?, ?)
        """;

        KeyHolder keyHolder = new GeneratedKeyHolder();

        jdbcTemplate.update(connection -> {
            PreparedStatement ps = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setLong(1, order.getUserId());
            ps.setString(2, order.getStatus().name());
            ps.setBigDecimal(3, order.getTotalAmount());
            ps.setTimestamp(4, Timestamp.valueOf(order.getOrderDate()));
            return ps;
        }, keyHolder);

        order.setId(keyHolder.getKey().longValue());

        return order;
    }

    public Optional<Order> findByIdWithDetails(Long id) {
        String sql = """
            SELECT o.*, oi.id as item_id, oi.product_id, oi.quantity, oi.unit_price,
                   p.name as product_name
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            LEFT JOIN products p ON oi.product_id = p.id
            WHERE o.id = ?
        """;

        return jdbcTemplate.query(sql, rs -> {
            Order order = null;

            while (rs.next()) {
                if (order == null) {
                    order = new Order();
                    order.setId(rs.getLong("id"));
                    order.setUserId(rs.getLong("user_id"));
                    order.setStatus(OrderStatus.valueOf(rs.getString("status")));
                    order.setTotalAmount(rs.getBigDecimal("total_amount"));
                    order.setOrderDate(rs.getTimestamp("order_date").toLocalDateTime());
                    order.setOrderItems(new ArrayList<>());
                }

                if (rs.getObject("item_id") != null) {
                    OrderItem item = new OrderItem();
                    item.setId(rs.getLong("item_id"));
                    item.setProductId(rs.getLong("product_id"));
                    item.setQuantity(rs.getInt("quantity"));
                    item.setUnitPrice(rs.getBigDecimal("unit_price"));
                    item.setProductName(rs.getString("product_name"));

                    order.getOrderItems().add(item);
                }
            }

            return Optional.ofNullable(order);
        }, id);
    }

    public void saveOrderItems(Long orderId, List<OrderItem> items) {
        String sql = """
            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            VALUES (?, ?, ?, ?)
        """;

        jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
            @Override
            public void setValues(PreparedStatement ps, int i) throws SQLException {
                OrderItem item = items.get(i);
                ps.setLong(1, orderId);
                ps.setLong(2, item.getProductId());
                ps.setInt(3, item.getQuantity());
                ps.setBigDecimal(4, item.getUnitPrice());
            }

            @Override
            public int getBatchSize() {
                return items.size();
            }
        });
    }
}
```

---

## ❓ FAQ

### Q1: JdbcTemplate과 JPA를 함께 사용할 수 있나요?

**A**: 네, 함께 사용 가능하며 각각의 장점을 살릴 수 있습니다.

**사용 패턴**:
```java
@Service
@RequiredArgsConstructor
@Transactional
public class OrderService {

    // JPA: 일반 CRUD
    private final OrderRepository orderRepository;  // JpaRepository

    // JdbcTemplate: 복잡한 통계 쿼리
    private final JdbcTemplate jdbcTemplate;

    // ✅ 간단한 CRUD → JPA
    public Order createOrder(OrderRequest request) {
        return orderRepository.save(new Order(request));
    }

    // ✅ 복잡한 통계 → JdbcTemplate
    public List<DailySales> getDailySalesReport(LocalDate startDate, LocalDate endDate) {
        String sql = """
            SELECT DATE(o.created_at) as date,
                   SUM(o.total_amount) as sales
            FROM orders o
            WHERE o.created_at >= ? AND o.created_at < ?
            GROUP BY DATE(o.created_at)
        """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            DailySales sales = new DailySales();
            sales.setDate(rs.getDate("date").toLocalDate());
            sales.setSales(rs.getBigDecimal("sales"));
            return sales;
        }, startDate, endDate.plusDays(1));
    }
}
```

**주의사항**:
```java
// ❌ 같은 트랜잭션에서 JPA와 JdbcTemplate 혼용 시 문제 발생 가능
@Transactional
public void updateUser(Long id) {
    User user = userRepository.findById(id).orElseThrow();  // JPA
    user.setName("변경");  // Dirty Checking

    // JdbcTemplate로 직접 UPDATE
    jdbcTemplate.update("UPDATE users SET email = ? WHERE id = ?", "new@email.com", id);

    // → JPA의 Dirty Checking과 충돌 가능
}

// ✅ 명시적으로 flush() 호출
@Transactional
public void updateUser(Long id) {
    User user = userRepository.findById(id).orElseThrow();
    user.setName("변경");

    entityManager.flush();  // JPA 변경사항 먼저 반영

    jdbcTemplate.update("UPDATE users SET email = ? WHERE id = ?", "new@email.com", id);
}
```

---

### Q2: RowMapper는 어떻게 재사용하나요?

**A**: 인스턴스 변수나 static 메서드로 정의하여 재사용할 수 있습니다.

**방법 1: 인스턴스 변수로 정의**:
```java
@Repository
public class UserRepository {

    private final JdbcTemplate jdbcTemplate;

    // RowMapper를 인스턴스 변수로 정의
    private final RowMapper<User> userRowMapper = (rs, rowNum) -> {
        User user = new User();
        user.setId(rs.getLong("id"));
        user.setName(rs.getString("name"));
        user.setEmail(rs.getString("email"));
        return user;
    };

    public User findById(Long id) {
        String sql = "SELECT * FROM users WHERE id = ?";
        return jdbcTemplate.queryForObject(sql, userRowMapper, id);
    }

    public List<User> findAll() {
        String sql = "SELECT * FROM users";
        return jdbcTemplate.query(sql, userRowMapper);
    }
}
```

**방법 2: static 메서드로 정의**:
```java
public class UserRowMapper {

    public static RowMapper<User> create() {
        return (rs, rowNum) -> {
            User user = new User();
            user.setId(rs.getLong("id"));
            user.setName(rs.getString("name"));
            user.setEmail(rs.getString("email"));
            return user;
        };
    }
}

@Repository
public class UserRepository {

    private final JdbcTemplate jdbcTemplate;

    public User findById(Long id) {
        String sql = "SELECT * FROM users WHERE id = ?";
        return jdbcTemplate.queryForObject(sql, UserRowMapper.create(), id);
    }
}
```

**방법 3: 클래스로 정의**:
```java
public class UserRowMapper implements RowMapper<User> {

    @Override
    public User mapRow(ResultSet rs, int rowNum) throws SQLException {
        User user = new User();
        user.setId(rs.getLong("id"));
        user.setName(rs.getString("name"));
        user.setEmail(rs.getString("email"));
        return user;
    }
}

@Repository
public class UserRepository {

    private final JdbcTemplate jdbcTemplate;
    private final UserRowMapper userRowMapper = new UserRowMapper();

    public User findById(Long id) {
        String sql = "SELECT * FROM users WHERE id = ?";
        return jdbcTemplate.queryForObject(sql, userRowMapper, id);
    }
}
```

---

### Q3: EmptyResultDataAccessException은 어떻게 처리하나요?

**A**: try-catch로 잡아서 Optional로 변환하거나, query()를 사용합니다.

**방법 1: try-catch + Optional** (권장):
```java
public Optional<User> findById(Long id) {
    String sql = "SELECT * FROM users WHERE id = ?";

    try {
        User user = jdbcTemplate.queryForObject(sql, userRowMapper, id);
        return Optional.ofNullable(user);
    } catch (EmptyResultDataAccessException e) {
        return Optional.empty();
    }
}

// 사용
User user = userRepository.findById(999L)
    .orElseThrow(() -> new UserNotFoundException("User not found"));
```

**방법 2: query() 사용**:
```java
public Optional<User> findById(Long id) {
    String sql = "SELECT * FROM users WHERE id = ?";

    List<User> users = jdbcTemplate.query(sql, userRowMapper, id);

    return users.isEmpty() ? Optional.empty() : Optional.of(users.get(0));
}
```

**방법 3: Custom Exception 변환**:
```java
public User findById(Long id) {
    String sql = "SELECT * FROM users WHERE id = ?";

    try {
        return jdbcTemplate.queryForObject(sql, userRowMapper, id);
    } catch (EmptyResultDataAccessException e) {
        throw new UserNotFoundException("사용자를 찾을 수 없습니다: " + id);
    }
}
```

---

### Q4: 대량 데이터 INSERT 시 성능은 어떻게 최적화하나요?

**A**: batchUpdate()를 사용하고, 적절한 배치 크기를 설정합니다.

**방법 1: batchUpdate() 사용**:
```java
public void saveAll(List<User> users) {
    String sql = "INSERT INTO users (name, email) VALUES (?, ?)";

    jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
        @Override
        public void setValues(PreparedStatement ps, int i) throws SQLException {
            User user = users.get(i);
            ps.setString(1, user.getName());
            ps.setString(2, user.getEmail());
        }

        @Override
        public int getBatchSize() {
            return users.size();
        }
    });
}
```

**방법 2: 배치 크기 조절** (매우 큰 데이터의 경우):
```java
public void saveAllInChunks(List<User> users, int chunkSize) {
    String sql = "INSERT INTO users (name, email) VALUES (?, ?)";

    for (int i = 0; i < users.size(); i += chunkSize) {
        int end = Math.min(i + chunkSize, users.size());
        List<User> chunk = users.subList(i, end);

        jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
            @Override
            public void setValues(PreparedStatement ps, int index) throws SQLException {
                User user = chunk.get(index);
                ps.setString(1, user.getName());
                ps.setString(2, user.getEmail());
            }

            @Override
            public int getBatchSize() {
                return chunk.size();
            }
        });

        log.info("Inserted chunk: {}-{}", i, end);
    }
}

// 사용
saveAllInChunks(users, 1000);  // 1000건씩 배치 처리
```

**성능 비교**:
```
10000건 INSERT:
- 개별 update(): ~100초
- batchUpdate() (전체): ~5초
- batchUpdate() (1000건씩): ~6초 (메모리 효율적)
```

---

### Q5: NamedParameterJdbcTemplate은 언제 사용하나요?

**A**: 파라미터가 많거나, 가독성이 중요한 경우에 사용합니다.

**JdbcTemplate (위치 기반 파라미터)**:
```java
// ❌ 파라미터 순서 헷갈림
public List<Product> search(String name, BigDecimal minPrice, BigDecimal maxPrice, Integer minStock) {
    String sql = """
        SELECT * FROM products
        WHERE name LIKE ?
          AND price >= ?
          AND price <= ?
          AND stock_quantity >= ?
    """;

    return jdbcTemplate.query(sql, productRowMapper,
        "%" + name + "%", minPrice, maxPrice, minStock);
    // → 파라미터 순서 틀리면 버그 발생!
}
```

**NamedParameterJdbcTemplate (이름 기반 파라미터)**:
```java
// ✅ 파라미터 이름으로 명확히 매핑
public List<Product> search(String name, BigDecimal minPrice, BigDecimal maxPrice, Integer minStock) {
    String sql = """
        SELECT * FROM products
        WHERE name LIKE :name
          AND price >= :minPrice
          AND price <= :maxPrice
          AND stock_quantity >= :minStock
    """;

    MapSqlParameterSource params = new MapSqlParameterSource()
        .addValue("name", "%" + name + "%")
        .addValue("minPrice", minPrice)
        .addValue("maxPrice", maxPrice)
        .addValue("minStock", minStock);

    return namedJdbcTemplate.query(sql, params, productRowMapper);
}
```

**BeanPropertySqlParameterSource 활용**:
```java
public void save(Product product) {
    String sql = """
        INSERT INTO products (name, price, stock_quantity)
        VALUES (:name, :price, :stockQuantity)
    """;

    // 객체의 필드 이름과 자동 매핑
    SqlParameterSource params = new BeanPropertySqlParameterSource(product);

    namedJdbcTemplate.update(sql, params);
}
```

**선택 기준**:
```
JdbcTemplate:
✅ 파라미터 2-3개
✅ 간단한 쿼리
✅ 성능이 매우 중요한 경우

NamedParameterJdbcTemplate:
✅ 파라미터 4개 이상
✅ 복잡한 쿼리
✅ 가독성이 중요한 경우
✅ 객체 매핑 필요한 경우
```

---

### Q6: SimpleJdbcInsert는 언제 사용하나요?

**A**: Auto-increment ID를 반환받아야 할 때 유용합니다.

**일반 JdbcTemplate (복잡)**:
```java
public Product save(Product product) {
    String sql = "INSERT INTO products (name, price) VALUES (?, ?)";

    KeyHolder keyHolder = new GeneratedKeyHolder();

    jdbcTemplate.update(connection -> {
        PreparedStatement ps = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
        ps.setString(1, product.getName());
        ps.setBigDecimal(2, product.getPrice());
        return ps;
    }, keyHolder);

    product.setId(keyHolder.getKey().longValue());

    return product;
}
```

**SimpleJdbcInsert (간결)**:
```java
private final SimpleJdbcInsert simpleJdbcInsert;

public ProductRepository(DataSource dataSource) {
    this.simpleJdbcInsert = new SimpleJdbcInsert(dataSource)
        .withTableName("products")
        .usingGeneratedKeyColumns("id");
}

public Product save(Product product) {
    Map<String, Object> params = new HashMap<>();
    params.put("name", product.getName());
    params.put("price", product.getPrice());

    Number id = simpleJdbcInsert.executeAndReturnKey(params);

    product.setId(id.longValue());

    return product;
}

// 또는 BeanPropertySqlParameterSource 사용
public Product saveWithBean(Product product) {
    SqlParameterSource params = new BeanPropertySqlParameterSource(product);

    Number id = simpleJdbcInsert.executeAndReturnKey(params);

    product.setId(id.longValue());

    return product;
}
```

---

### Q7: JdbcTemplate의 트랜잭션은 어떻게 관리하나요?

**A**: @Transactional 어노테이션을 사용하여 선언적으로 관리합니다.

**@Transactional 사용** (권장):
```java
@Service
@RequiredArgsConstructor
@Transactional
public class OrderService {

    private final JdbcTemplate jdbcTemplate;

    public void createOrder(Order order) {
        String orderSql = "INSERT INTO orders (user_id, total_amount) VALUES (?, ?)";
        jdbcTemplate.update(orderSql, order.getUserId(), order.getTotalAmount());

        String itemSql = "INSERT INTO order_items (order_id, product_id) VALUES (?, ?)";
        for (OrderItem item : order.getItems()) {
            jdbcTemplate.update(itemSql, order.getId(), item.getProductId());
        }

        // 모두 성공 시 커밋, 하나라도 실패 시 롤백
    }
}
```

**TransactionTemplate 사용** (프로그래밍 방식):
```java
@Service
@RequiredArgsConstructor
public class OrderService {

    private final JdbcTemplate jdbcTemplate;
    private final TransactionTemplate transactionTemplate;

    public void createOrder(Order order) {
        transactionTemplate.execute(status -> {
            try {
                String orderSql = "INSERT INTO orders (user_id, total_amount) VALUES (?, ?)";
                jdbcTemplate.update(orderSql, order.getUserId(), order.getTotalAmount());

                String itemSql = "INSERT INTO order_items (order_id, product_id) VALUES (?, ?)";
                for (OrderItem item : order.getItems()) {
                    jdbcTemplate.update(itemSql, order.getId(), item.getProductId());
                }

                return null;
            } catch (Exception e) {
                status.setRollbackOnly();
                throw e;
            }
        });
    }
}
```

---

## 📝 면접 질문

### 주니어 레벨 (5-7개)

1. **JdbcTemplate과 순수 JDBC의 차이점을 설명하고, JdbcTemplate의 장점을 말씀해주세요.**

2. **RowMapper는 무엇이고, 어떻게 사용하나요?**

3. **queryForObject()와 query()의 차이점은 무엇인가요?**

4. **JdbcTemplate에서 SQL Injection을 방지하는 방법은 무엇인가요?**

5. **EmptyResultDataAccessException은 왜 발생하며, 어떻게 처리해야 하나요?**

6. **JdbcTemplate에서 대량 INSERT를 효율적으로 처리하는 방법은 무엇인가요?**

7. **NamedParameterJdbcTemplate은 언제 사용하는 것이 좋은가요?**

---

### 중급 레벨 (3-5개)

1. **JdbcTemplate과 JPA를 함께 사용할 때 주의할 점은 무엇인가요?**

2. **SimpleJdbcInsert와 일반 JdbcTemplate의 insert 방식의 차이점을 설명하고, 각각의 사용 사례를 제시해주세요.**

3. **ResultSetExtractor와 RowMapper의 차이점은 무엇이며, 각각 어떤 상황에서 사용하나요?**

4. **대용량 데이터 배치 처리 시 JdbcTemplate을 사용하면 어떤 이점이 있나요? 메모리 관리는 어떻게 하나요?**

5. **JdbcTemplate에서 트랜잭션을 관리하는 방법과 @Transactional과의 통합에 대해 설명해주세요.**

---

## 💡 면접 질문 답안

### 주니어 레벨 답안

**Q1: JdbcTemplate과 순수 JDBC의 차이점을 설명하고, JdbcTemplate의 장점을 말씀해주세요.**

**A**:

**차이점**:

| 구분 | 순수 JDBC | JdbcTemplate |
|-----|----------|-------------|
| **리소스 관리** | 수동 (Connection, Statement, ResultSet close) | 자동 |
| **예외 처리** | Checked Exception (SQLException) | Unchecked (DataAccessException) |
| **코드 길이** | 30-40줄 | 5-10줄 |
| **보일러플레이트** | 많음 | 최소화 |
| **메모리 누수 위험** | 높음 | 없음 |

**순수 JDBC**:
```java
// ❌ 복잡하고 길음 (30줄)
public List<User> findAll() {
    Connection conn = null;
    Statement stmt = null;
    ResultSet rs = null;
    List<User> users = new ArrayList<>();

    try {
        conn = dataSource.getConnection();
        stmt = conn.createStatement();
        rs = stmt.executeQuery("SELECT * FROM users");

        while (rs.next()) {
            User user = new User();
            user.setId(rs.getLong("id"));
            user.setName(rs.getString("name"));
            user.setEmail(rs.getString("email"));
            users.add(user);
        }
    } catch (SQLException e) {
        throw new RuntimeException(e);
    } finally {
        try { if (rs != null) rs.close(); } catch (SQLException e) { }
        try { if (stmt != null) stmt.close(); } catch (SQLException e) { }
        try { if (conn != null) conn.close(); } catch (SQLException e) { }
    }

    return users;
}
```

**JdbcTemplate**:
```java
// ✅ 간결하고 안전 (8줄)
public List<User> findAll() {
    String sql = "SELECT * FROM users";

    return jdbcTemplate.query(sql, (rs, rowNum) -> {
        User user = new User();
        user.setId(rs.getLong("id"));
        user.setName(rs.getString("name"));
        user.setEmail(rs.getString("email"));
        return user;
    });
}
```

**JdbcTemplate의 장점**:

1. **자동 리소스 관리**:
   ```
   Connection, Statement, ResultSet을 자동으로 close
   → 메모리 누수 방지
   ```

2. **예외 변환**:
   ```
   SQLException (Checked) → DataAccessException (Unchecked)
   → try-catch 강제 안 함
   ```

3. **코드 간결화**:
   ```
   30줄 → 8줄 (73% 감소)
   → 가독성 향상, 유지보수 쉬움
   ```

4. **생산성 향상**:
   ```
   개발 시간: 10분 → 3분
   → 비즈니스 로직에 집중
   ```

5. **안정성**:
   ```
   리소스 누수 위험 0%
   → 프로덕션 안정성 향상
   ```

---

**Q2: RowMapper는 무엇이고, 어떻게 사용하나요?**

**A**:

**RowMapper란**:
ResultSet의 각 행(Row)을 Java 객체로 변환하는 인터페이스

**역할**:
```
ResultSet (데이터베이스 결과) → Java 객체 (User, Product 등)
```

**기본 사용법**:
```java
@Repository
public class UserRepository {

    private final JdbcTemplate jdbcTemplate;

    public List<User> findAll() {
        String sql = "SELECT * FROM users";

        // RowMapper를 람다식으로 정의
        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            User user = new User();
            user.setId(rs.getLong("id"));
            user.setName(rs.getString("name"));
            user.setEmail(rs.getString("email"));
            return user;
        });
    }
}
```

**재사용 패턴**:
```java
@Repository
public class UserRepository {

    private final JdbcTemplate jdbcTemplate;

    // RowMapper를 인스턴스 변수로 정의 (재사용)
    private final RowMapper<User> userRowMapper = (rs, rowNum) -> {
        User user = new User();
        user.setId(rs.getLong("id"));
        user.setName(rs.getString("name"));
        user.setEmail(rs.getString("email"));
        user.setCreatedAt(rs.getTimestamp("created_at").toLocalDateTime());
        return user;
    };

    public User findById(Long id) {
        String sql = "SELECT * FROM users WHERE id = ?";
        return jdbcTemplate.queryForObject(sql, userRowMapper, id);
    }

    public List<User> findAll() {
        String sql = "SELECT * FROM users";
        return jdbcTemplate.query(sql, userRowMapper);
    }

    public List<User> findByName(String name) {
        String sql = "SELECT * FROM users WHERE name LIKE ?";
        return jdbcTemplate.query(sql, userRowMapper, "%" + name + "%");
    }
}
```

**클래스로 정의** (복잡한 매핑):
```java
public class UserRowMapper implements RowMapper<User> {

    @Override
    public User mapRow(ResultSet rs, int rowNum) throws SQLException {
        User user = new User();
        user.setId(rs.getLong("id"));
        user.setName(rs.getString("name"));
        user.setEmail(rs.getString("email"));

        // Null 처리
        Timestamp timestamp = rs.getTimestamp("created_at");
        if (timestamp != null) {
            user.setCreatedAt(timestamp.toLocalDateTime());
        }

        // Enum 처리
        String status = rs.getString("status");
        if (status != null) {
            user.setStatus(UserStatus.valueOf(status));
        }

        return user;
    }
}

@Repository
public class UserRepository {

    private final JdbcTemplate jdbcTemplate;
    private final UserRowMapper userRowMapper = new UserRowMapper();

    public User findById(Long id) {
        String sql = "SELECT * FROM users WHERE id = ?";
        return jdbcTemplate.queryForObject(sql, userRowMapper, id);
    }
}
```

**장점**:
```
✅ 재사용 가능: 여러 메서드에서 동일한 RowMapper 사용
✅ 테스트 용이: RowMapper를 독립적으로 테스트
✅ 유지보수 쉬움: 매핑 로직 한 곳에서 관리
```

---

**Q3: queryForObject()와 query()의 차이점은 무엇인가요?**

**A**:

**차이점**:

| 메서드 | 반환 타입 | 결과 개수 | 사용 사례 |
|--------|----------|----------|----------|
| `queryForObject()` | `T` (단일 객체) | 정확히 1개 | ID로 조회 |
| `query()` | `List<T>` | 0개 이상 | 목록 조회 |

**queryForObject()** (단일 결과):
```java
public User findById(Long id) {
    String sql = "SELECT * FROM users WHERE id = ?";

    // 정확히 1개의 결과 기대
    return jdbcTemplate.queryForObject(sql, (rs, rowNum) -> {
        User user = new User();
        user.setId(rs.getLong("id"));
        user.setName(rs.getString("name"));
        return user;
    }, id);
}

// 사용
User user = userRepository.findById(1L);  // User 객체 반환
```

**예외 발생**:
```java
// 결과가 0개 → EmptyResultDataAccessException
User user = userRepository.findById(999L);  // 예외!

// 결과가 2개 이상 → IncorrectResultSizeDataAccessException
User user = userRepository.findById(1L);  // 예외!
```

**query()** (목록 결과):
```java
public List<User> findAll() {
    String sql = "SELECT * FROM users";

    // 0개 이상의 결과 반환
    return jdbcTemplate.query(sql, (rs, rowNum) -> {
        User user = new User();
        user.setId(rs.getLong("id"));
        user.setName(rs.getString("name"));
        return user;
    });
}

// 사용
List<User> users = userRepository.findAll();  // List<User> 반환 (비어있을 수 있음)

// 결과가 0개여도 예외 안 발생
List<User> empty = userRepository.findAll();  // 빈 리스트 반환
```

**queryForObject()를 안전하게 사용** (Optional):
```java
public Optional<User> findById(Long id) {
    String sql = "SELECT * FROM users WHERE id = ?";

    try {
        User user = jdbcTemplate.queryForObject(sql, userRowMapper, id);
        return Optional.ofNullable(user);
    } catch (EmptyResultDataAccessException e) {
        return Optional.empty();
    }
}

// 사용
User user = userRepository.findById(999L)
    .orElseThrow(() -> new UserNotFoundException("User not found"));
```

**query()로 단일 결과 조회** (안전한 방법):
```java
public Optional<User> findById(Long id) {
    String sql = "SELECT * FROM users WHERE id = ?";

    List<User> users = jdbcTemplate.query(sql, userRowMapper, id);

    // 첫 번째 요소 반환, 없으면 empty
    return users.isEmpty() ? Optional.empty() : Optional.of(users.get(0));
}
```

**사용 가이드**:
```
queryForObject():
✅ 정확히 1개의 결과가 확실할 때
✅ ID로 조회 (PK)
❌ 결과가 없을 수 있을 때 → query() 사용

query():
✅ 0개 이상의 결과
✅ 목록 조회
✅ 검색 결과
✅ 결과가 없을 수도 있을 때
```

---

**Q4: JdbcTemplate에서 SQL Injection을 방지하는 방법은 무엇인가요?**

**A**:

**SQL Injection이란**:
악의적인 SQL 코드를 주입하여 데이터베이스를 조작하는 공격

**문제 상황**:
```java
// ❌ SQL Injection 취약!
public List<User> findByName(String name) {
    String sql = "SELECT * FROM users WHERE name = '" + name + "'";

    return jdbcTemplate.query(sql, userRowMapper);
}

// 공격 예시
String maliciousName = "admin' OR '1'='1";
List<User> users = userRepository.findByName(maliciousName);

// 실행되는 SQL:
// SELECT * FROM users WHERE name = 'admin' OR '1'='1'
// → 모든 사용자 조회됨!
```

**해결책 1: PreparedStatement 사용** (권장):
```java
// ✅ PreparedStatement로 안전
public List<User> findByName(String name) {
    String sql = "SELECT * FROM users WHERE name = ?";  // ? 사용

    return jdbcTemplate.query(sql, userRowMapper, name);
}

// 공격 시도해도 안전
String maliciousName = "admin' OR '1'='1";
List<User> users = userRepository.findByName(maliciousName);

// 실행되는 SQL:
// SELECT * FROM users WHERE name = 'admin'' OR ''1''=''1'
// → name이 정확히 "admin' OR '1'='1"인 사용자만 조회 (없음)
// → SQL Injection 차단!
```

**동작 원리**:
```
PreparedStatement:
1. SQL 구문 먼저 컴파일
2. 파라미터는 값으로만 처리 (코드로 인식 안 함)
3. 특수문자 자동 이스케이프 (' → '')

문자열 연결:
1. SQL 전체를 하나의 문자열로 처리
2. 파라미터가 SQL 코드로 인식됨
3. 특수문자 그대로 실행
```

**해결책 2: NamedParameterJdbcTemplate 사용**:
```java
// ✅ Named Parameter도 안전
@Repository
@RequiredArgsConstructor
public class UserRepository {

    private final NamedParameterJdbcTemplate namedJdbcTemplate;

    public List<User> findByName(String name) {
        String sql = "SELECT * FROM users WHERE name = :name";  // :name 사용

        MapSqlParameterSource params = new MapSqlParameterSource()
            .addValue("name", name);

        return namedJdbcTemplate.query(sql, params, userRowMapper);
    }
}
```

**해결책 3: 입력 값 검증 추가** (추가 방어):
```java
public List<User> findByName(String name) {
    // 입력 검증
    if (name == null) {
        throw new IllegalArgumentException("Name cannot be null");
    }

    // 위험한 문자 체크
    if (name.contains("'") || name.contains("--") || name.contains(";")) {
        throw new IllegalArgumentException("Invalid name parameter");
    }

    String sql = "SELECT * FROM users WHERE name = ?";

    return jdbcTemplate.query(sql, userRowMapper, name);
}
```

**실무 권장 사항**:
```
✅ 항상 PreparedStatement 사용 (?, :name)
❌ 절대 문자열 연결로 SQL 생성 금지
✅ 입력 값 검증 (Whitelist 방식)
✅ 최소 권한 DB 계정 사용
✅ 정기적인 보안 감사
```

**안전한 예시들**:
```java
// ✅ PreparedStatement
String sql = "SELECT * FROM users WHERE id = ?";
jdbcTemplate.queryForObject(sql, userRowMapper, id);

// ✅ Named Parameter
String sql = "SELECT * FROM users WHERE name = :name AND age >= :age";
MapSqlParameterSource params = new MapSqlParameterSource()
    .addValue("name", name)
    .addValue("age", age);
namedJdbcTemplate.query(sql, params, userRowMapper);

// ✅ IN 절도 안전하게
String sql = "SELECT * FROM users WHERE id IN (:ids)";
Map<String, Object> params = Map.of("ids", List.of(1L, 2L, 3L));
namedJdbcTemplate.query(sql, params, userRowMapper);
```

---

**Q5: EmptyResultDataAccessException은 왜 발생하며, 어떻게 처리해야 하나요?**

**A**:

**발생 원인**:
`queryForObject()`는 정확히 1개의 결과를 기대하는데, 결과가 0개일 때 발생

**문제 상황**:
```java
public User findById(Long id) {
    String sql = "SELECT * FROM users WHERE id = ?";

    // 결과가 0개면 EmptyResultDataAccessException 발생!
    return jdbcTemplate.queryForObject(sql, userRowMapper, id);
}

// 사용
User user = userRepository.findById(999L);
// → EmptyResultDataAccessException: Incorrect result size: expected 1, actual 0
```

**해결책 1: try-catch + Optional** (권장):
```java
public Optional<User> findById(Long id) {
    String sql = "SELECT * FROM users WHERE id = ?";

    try {
        User user = jdbcTemplate.queryForObject(sql, userRowMapper, id);
        return Optional.ofNullable(user);
    } catch (EmptyResultDataAccessException e) {
        return Optional.empty();
    }
}

// 사용
User user = userRepository.findById(999L)
    .orElseThrow(() -> new UserNotFoundException("User not found: 999"));

// 또는
User user = userRepository.findById(999L)
    .orElse(null);

// 또는
User user = userRepository.findById(999L)
    .orElseGet(() -> new User());
```

**해결책 2: query() 사용 후 첫 번째 요소 반환**:
```java
public Optional<User> findById(Long id) {
    String sql = "SELECT * FROM users WHERE id = ?";

    List<User> users = jdbcTemplate.query(sql, userRowMapper, id);

    // 빈 리스트면 empty, 있으면 첫 번째 요소
    return users.isEmpty() ? Optional.empty() : Optional.of(users.get(0));
}
```

**해결책 3: Custom Exception 변환**:
```java
public User findById(Long id) {
    String sql = "SELECT * FROM users WHERE id = ?";

    try {
        return jdbcTemplate.queryForObject(sql, userRowMapper, id);
    } catch (EmptyResultDataAccessException e) {
        throw new UserNotFoundException("사용자를 찾을 수 없습니다: " + id);
    }
}

// 사용
try {
    User user = userRepository.findById(999L);
} catch (UserNotFoundException e) {
    // 명확한 예외 처리
}
```

**IncorrectResultSizeDataAccessException** (결과 2개 이상):
```java
public User findByEmail(String email) {
    String sql = "SELECT * FROM users WHERE email = ?";

    try {
        return jdbcTemplate.queryForObject(sql, userRowMapper, email);
    } catch (EmptyResultDataAccessException e) {
        throw new UserNotFoundException("User not found: " + email);
    } catch (IncorrectResultSizeDataAccessException e) {
        // 결과가 2개 이상
        throw new DuplicateUserException("Multiple users found: " + email);
    }
}
```

**실무 권장 패턴**:
```java
// ✅ Repository는 Optional 반환
public Optional<User> findById(Long id) {
    String sql = "SELECT * FROM users WHERE id = ?";

    try {
        User user = jdbcTemplate.queryForObject(sql, userRowMapper, id);
        return Optional.ofNullable(user);
    } catch (EmptyResultDataAccessException e) {
        return Optional.empty();
    }
}

// ✅ Service에서 예외 변환
@Service
public class UserService {

    public User getUser(Long id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException("사용자를 찾을 수 없습니다: " + id));
    }
}
```

---

**Q6: JdbcTemplate에서 대량 INSERT를 효율적으로 처리하는 방법은 무엇인가요?**

**A**:

**일반 INSERT** (비효율):
```java
// ❌ 느림: 1000번의 DB 호출
@Transactional
public void saveAll(List<User> users) {
    String sql = "INSERT INTO users (name, email) VALUES (?, ?)";

    for (User user : users) {
        jdbcTemplate.update(sql, user.getName(), user.getEmail());
    }
}

// 1000건 → 1000번 DB 호출 → 10초 소요
```

**Batch INSERT** (효율적):
```java
// ✅ 빠름: Batch로 한 번에 처리
@Transactional
public void saveAll(List<User> users) {
    String sql = "INSERT INTO users (name, email) VALUES (?, ?)";

    jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
        @Override
        public void setValues(PreparedStatement ps, int i) throws SQLException {
            User user = users.get(i);
            ps.setString(1, user.getName());
            ps.setString(2, user.getEmail());
        }

        @Override
        public int getBatchSize() {
            return users.size();
        }
    });
}

// 1000건 → 1번 Batch 호출 → 1초 소요
```

**NamedParameterJdbcTemplate 사용** (더 간결):
```java
@Transactional
public void saveAll(List<User> users) {
    String sql = "INSERT INTO users (name, email) VALUES (:name, :email)";

    SqlParameterSource[] batchParams = users.stream()
        .map(user -> new MapSqlParameterSource()
            .addValue("name", user.getName())
            .addValue("email", user.getEmail()))
        .toArray(SqlParameterSource[]::new);

    namedJdbcTemplate.batchUpdate(sql, batchParams);
}
```

**대용량 데이터 처리** (청크 단위):
```java
@Transactional
public void saveAllInChunks(List<User> users, int chunkSize) {
    String sql = "INSERT INTO users (name, email) VALUES (?, ?)";

    // 1000건씩 나눠서 처리
    for (int i = 0; i < users.size(); i += chunkSize) {
        int end = Math.min(i + chunkSize, users.size());
        List<User> chunk = users.subList(i, end);

        jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
            @Override
            public void setValues(PreparedStatement ps, int index) throws SQLException {
                User user = chunk.get(index);
                ps.setString(1, user.getName());
                ps.setString(2, user.getEmail());
            }

            @Override
            public int getBatchSize() {
                return chunk.size();
            }
        });

        log.info("Inserted chunk: {}-{}", i, end);
    }
}

// 사용
saveAllInChunks(users, 1000);  // 1000건씩 처리
```

**성능 비교**:
```
1000건 INSERT:
- 개별 update(): ~10초
- batchUpdate(): ~1초
→ 10배 빠름!

10000건 INSERT:
- 개별 update(): ~100초
- batchUpdate(): ~5초
→ 20배 빠름!

100000건 INSERT:
- 개별 update(): ~1000초 (16분)
- batchUpdate(): ~30초
→ 33배 빠름!
```

**추가 최적화** (MySQL):
```yaml
# application.yml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?rewriteBatchedStatements=true
```

**실무 권장**:
```
✅ 10건 이상: batchUpdate() 사용
✅ 10000건 이상: 청크 단위 처리 (1000건씩)
✅ 100000건 이상: 멀티 스레드 고려
✅ rewriteBatchedStatements=true 설정 (MySQL)
```

---

**Q7: NamedParameterJdbcTemplate은 언제 사용하는 것이 좋은가요?**

**A**:

**JdbcTemplate** (위치 기반 파라미터):
```java
// ❌ 파라미터 순서 헷갈림
public List<Product> search(String name, BigDecimal minPrice, BigDecimal maxPrice) {
    String sql = """
        SELECT * FROM products
        WHERE name LIKE ?
          AND price >= ?
          AND price <= ?
    """;

    return jdbcTemplate.query(sql, productRowMapper,
        "%" + name + "%", minPrice, maxPrice);
    // → 순서 틀리면 버그!
}
```

**NamedParameterJdbcTemplate** (이름 기반 파라미터):
```java
// ✅ 파라미터 이름으로 명확하게
public List<Product> search(String name, BigDecimal minPrice, BigDecimal maxPrice) {
    String sql = """
        SELECT * FROM products
        WHERE name LIKE :name
          AND price >= :minPrice
          AND price <= :maxPrice
    """;

    MapSqlParameterSource params = new MapSqlParameterSource()
        .addValue("name", "%" + name + "%")
        .addValue("minPrice", minPrice)
        .addValue("maxPrice", maxPrice);

    return namedJdbcTemplate.query(sql, params, productRowMapper);
}
```

**장점**:

1. **가독성**:
   ```
   ? ? ? (무엇인지 모름)
   vs
   :name :minPrice :maxPrice (명확함)
   ```

2. **유지보수**:
   ```
   파라미터 추가/삭제 시 순서 신경 안 써도 됨
   ```

3. **IN 절 처리**:
   ```java
   // ✅ IN 절 쉽게 처리
   String sql = "SELECT * FROM users WHERE id IN (:ids)";

   Map<String, Object> params = Map.of("ids", List.of(1L, 2L, 3L));

   namedJdbcTemplate.query(sql, params, userRowMapper);
   ```

4. **객체 매핑**:
   ```java
   // ✅ BeanPropertySqlParameterSource로 객체 자동 매핑
   public void save(Product product) {
       String sql = "INSERT INTO products (name, price) VALUES (:name, :price)";

       SqlParameterSource params = new BeanPropertySqlParameterSource(product);

       namedJdbcTemplate.update(sql, params);
   }
   ```

**사용 기준**:

```
JdbcTemplate:
✅ 파라미터 1-3개
✅ 간단한 쿼리
✅ 성능이 매우 중요

NamedParameterJdbcTemplate:
✅ 파라미터 4개 이상
✅ 복잡한 쿼리
✅ IN 절 사용
✅ 객체 매핑 필요
✅ 가독성이 중요
```

---

### 중급 레벨 답안

**Q1: JdbcTemplate과 JPA를 함께 사용할 때 주의할 점은 무엇인가요?**

**A**:

**함께 사용하는 이유**:
```
JPA: 일반 CRUD (생산성)
JdbcTemplate: 복잡한 쿼리, 통계 (성능)
```

**주의사항 1: 영속성 컨텍스트와의 충돌**:

```java
// ❌ 문제 발생 가능
@Transactional
public void updateUser(Long id) {
    // JPA로 조회 (영속성 컨텍스트에 저장됨)
    User user = userRepository.findById(id).orElseThrow();
    user.setName("JPA 변경");  // Dirty Checking 대기 중

    // JdbcTemplate로 직접 UPDATE
    jdbcTemplate.update("UPDATE users SET email = ? WHERE id = ?", "new@email.com", id);

    // 트랜잭션 커밋 시:
    // 1. JdbcTemplate UPDATE 먼저 실행됨
    // 2. JPA Dirty Checking UPDATE 나중에 실행됨
    // → email 변경이 name 변경으로 덮어씌워질 수 있음!
}

// ✅ 해결: EntityManager.flush() 호출
@Transactional
public void updateUser(Long id) {
    User user = userRepository.findById(id).orElseThrow();
    user.setName("JPA 변경");

    entityManager.flush();  // JPA 변경사항 먼저 반영

    jdbcTemplate.update("UPDATE users SET email = ? WHERE id = ?", "new@email.com", id);
}
```

**주의사항 2: 1차 캐시 불일치**:

```java
// ❌ 1차 캐시와 DB 불일치
@Transactional
public void example(Long id) {
    // JPA로 조회 (1차 캐시에 저장)
    User user1 = userRepository.findById(id).orElseThrow();
    System.out.println(user1.getName());  // "홍길동"

    // JdbcTemplate로 직접 UPDATE
    jdbcTemplate.update("UPDATE users SET name = ? WHERE id = ?", "김철수", id);

    // JPA로 다시 조회 (1차 캐시에서 조회)
    User user2 = userRepository.findById(id).orElseThrow();
    System.out.println(user2.getName());  // "홍길동" (DB는 "김철수")
    // → 1차 캐시와 DB 불일치!
}

// ✅ 해결: EntityManager.clear() 또는 refresh()
@Transactional
public void example(Long id) {
    User user1 = userRepository.findById(id).orElseThrow();

    jdbcTemplate.update("UPDATE users SET name = ? WHERE id = ?", "김철수", id);

    // 영속성 컨텍스트 초기화
    entityManager.clear();

    // 다시 조회 (DB에서 조회)
    User user2 = userRepository.findById(id).orElseThrow();
    System.out.println(user2.getName());  // "김철수" (정확함)
}
```

**주의사항 3: 트랜잭션 일관성**:

```java
// ✅ 올바른 사용: Service 계층에서 트랜잭션 통합
@Service
@RequiredArgsConstructor
@Transactional
public class OrderService {

    private final OrderRepository orderRepository;  // JPA
    private final JdbcTemplate jdbcTemplate;

    public Order createOrder(OrderRequest request) {
        // 1. JPA로 주문 생성
        Order order = new Order(request);
        orderRepository.save(order);

        // 2. JdbcTemplate로 재고 차감
        String sql = "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?";
        jdbcTemplate.update(sql, request.getQuantity(), request.getProductId());

        // 3. JPA로 포인트 차감
        Point point = pointRepository.findByUserId(request.getUserId()).orElseThrow();
        point.use(request.getUsePoints());

        // 모두 같은 트랜잭션 안에서 실행
        // 하나라도 실패하면 전체 롤백

        return order;
    }
}
```

**실무 권장 패턴**:

```java
@Service
@RequiredArgsConstructor
@Transactional
public class ProductService {

    private final ProductRepository productRepository;  // JPA
    private final ProductStatisticsRepository statisticsRepository;  // JdbcTemplate

    // ✅ 간단한 CRUD → JPA
    public Product createProduct(ProductRequest request) {
        return productRepository.save(new Product(request));
    }

    // ✅ 복잡한 통계 → JdbcTemplate
    @Transactional(readOnly = true)
    public List<ProductSalesStatistics> getSalesStatistics(LocalDate startDate, LocalDate endDate) {
        // JPA로는 어려운 복잡한 집계 쿼리
        return statisticsRepository.getSalesStatistics(startDate, endDate);
    }
}
```

**정리**:
```
✅ Service 계층에서 트랜잭션 통합
✅ JPA 변경 후 JdbcTemplate 사용 시 flush() 호출
✅ JdbcTemplate 사용 후 JPA 조회 시 clear() 호출
✅ 읽기 전용은 @Transactional(readOnly = true)
✅ 각 기술의 장점을 살려서 사용
```

---

**Q2: SimpleJdbcInsert와 일반 JdbcTemplate의 insert 방식의 차이점을 설명하고, 각각의 사용 사례를 제시해주세요.**

**A**:

**일반 JdbcTemplate INSERT**:
```java
// 복잡한 코드
public Product save(Product product) {
    String sql = "INSERT INTO products (name, price, stock_quantity) VALUES (?, ?, ?)";

    KeyHolder keyHolder = new GeneratedKeyHolder();

    jdbcTemplate.update(connection -> {
        PreparedStatement ps = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
        ps.setString(1, product.getName());
        ps.setBigDecimal(2, product.getPrice());
        ps.setInt(3, product.getStockQuantity());
        return ps;
    }, keyHolder);

    product.setId(keyHolder.getKey().longValue());

    return product;
}
```

**SimpleJdbcInsert**:
```java
// 간결한 코드
private final SimpleJdbcInsert simpleJdbcInsert;

public ProductRepository(DataSource dataSource) {
    this.simpleJdbcInsert = new SimpleJdbcInsert(dataSource)
        .withTableName("products")
        .usingGeneratedKeyColumns("id");
}

public Product save(Product product) {
    Map<String, Object> params = new HashMap<>();
    params.put("name", product.getName());
    params.put("price", product.getPrice());
    params.put("stock_quantity", product.getStockQuantity());

    Number id = simpleJdbcInsert.executeAndReturnKey(params);

    product.setId(id.longValue());

    return product;
}
```

**차이점**:

| 구분 | JdbcTemplate | SimpleJdbcInsert |
|-----|--------------|------------------|
| **코드 길이** | 10-15줄 | 5줄 |
| **SQL 작성** | 필요 | 불필요 (자동 생성) |
| **컬럼 지정** | 수동 | 자동 (메타데이터 활용) |
| **복잡도** | 높음 | 낮음 |
| **유연성** | 높음 | 낮음 |

**SimpleJdbcInsert 장점**:

1. **간결함**:
   ```
   SQL 작성 불필요
   컬럼 자동 매핑
   코드 50% 감소
   ```

2. **BeanPropertySqlParameterSource 활용**:
   ```java
   public Product save(Product product) {
       SqlParameterSource params = new BeanPropertySqlParameterSource(product);

       Number id = simpleJdbcInsert.executeAndReturnKey(params);

       product.setId(id.longValue());

       return product;
   }
   ```

3. **다중 컬럼 생성 키**:
   ```java
   SimpleJdbcInsert simpleJdbcInsert = new SimpleJdbcInsert(dataSource)
       .withTableName("orders")
       .usingGeneratedKeyColumns("id", "order_number");

   Map<String, Object> keys = simpleJdbcInsert.executeAndReturnKeyHolder(params)
       .getKeys();

   Long id = (Long) keys.get("id");
   String orderNumber = (String) keys.get("order_number");
   ```

**JdbcTemplate 장점**:

1. **복잡한 SQL**:
   ```java
   String sql = """
       INSERT INTO orders (user_id, total_amount)
       SELECT u.id, ?
       FROM users u
       WHERE u.email = ?
   """;
   ```

2. **배치 처리**:
   ```java
   jdbcTemplate.batchUpdate(sql, batchParams);
   ```

3. **조건부 INSERT**:
   ```java
   String sql = "INSERT INTO logs (message) VALUES (?) ON DUPLICATE KEY UPDATE count = count + 1";
   ```

**사용 사례**:

```
SimpleJdbcInsert:
✅ 단순 INSERT
✅ Auto-increment ID 반환 필요
✅ 테이블 구조가 자주 변경
✅ 빠른 개발 필요

JdbcTemplate:
✅ 복잡한 INSERT (서브쿼리, JOIN)
✅ 배치 처리
✅ ON DUPLICATE KEY UPDATE
✅ 세밀한 제어 필요
```

---

**Q3: ResultSetExtractor와 RowMapper의 차이점은 무엇이며, 각각 어떤 상황에서 사용하나요?**

**A**:

**RowMapper** (각 행을 개별 객체로 변환):
```java
// 1:1 매핑 (각 행 → 하나의 객체)
public List<User> findAll() {
    String sql = "SELECT * FROM users";

    return jdbcTemplate.query(sql, (rs, rowNum) -> {
        User user = new User();
        user.setId(rs.getLong("id"));
        user.setName(rs.getString("name"));
        user.setEmail(rs.getString("email"));
        return user;
    });
}

// ResultSet의 각 행마다 mapRow() 호출
// 10개 행 → 10번 호출 → List<User>(10개)
```

**ResultSetExtractor** (전체 ResultSet을 처리):
```java
// 전체 ResultSet 처리 (복잡한 매핑)
public Order findByIdWithItems(Long orderId) {
    String sql = """
        SELECT o.id as order_id, o.total_amount,
               oi.id as item_id, oi.product_id, oi.quantity
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        WHERE o.id = ?
    """;

    return jdbcTemplate.query(sql, rs -> {
        Order order = null;

        while (rs.next()) {
            if (order == null) {
                // 첫 행에서 Order 생성
                order = new Order();
                order.setId(rs.getLong("order_id"));
                order.setTotalAmount(rs.getBigDecimal("total_amount"));
                order.setOrderItems(new ArrayList<>());
            }

            // 각 행에서 OrderItem 추가
            if (rs.getObject("item_id") != null) {
                OrderItem item = new OrderItem();
                item.setId(rs.getLong("item_id"));
                item.setProductId(rs.getLong("product_id"));
                item.setQuantity(rs.getInt("quantity"));

                order.getOrderItems().add(item);
            }
        }

        return order;
    }, orderId);
}

// extractData() 1번만 호출
// 전체 ResultSet을 직접 처리
```

**차이점**:

| 구분 | RowMapper | ResultSetExtractor |
|-----|-----------|-------------------|
| **호출 횟수** | 각 행마다 | 1번 (전체) |
| **반환 타입** | `T` (단일 객체) | 임의 타입 |
| **사용 메서드** | `query()`, `queryForObject()` | `query()` |
| **복잡도** | 낮음 | 높음 |
| **사용 사례** | 1:1 매핑 | 1:N 매핑, 집계 |

**RowMapper 사용 사례** (간단한 매핑):
```java
// ✅ 각 행이 독립적인 객체
public List<Product> findAll() {
    String sql = "SELECT id, name, price FROM products";

    return jdbcTemplate.query(sql, (rs, rowNum) -> {
        Product product = new Product();
        product.setId(rs.getLong("id"));
        product.setName(rs.getString("name"));
        product.setPrice(rs.getBigDecimal("price"));
        return product;
    });
}
```

**ResultSetExtractor 사용 사례 1** (1:N 관계):
```java
// ✅ 1개의 Order → N개의 OrderItem
public Order findOrderWithItems(Long orderId) {
    String sql = """
        SELECT o.*, oi.id as item_id, oi.product_id, oi.quantity
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        WHERE o.id = ?
    """;

    return jdbcTemplate.query(sql, rs -> {
        Order order = null;
        while (rs.next()) {
            if (order == null) {
                order = new Order();
                order.setId(rs.getLong("id"));
                order.setOrderItems(new ArrayList<>());
            }

            if (rs.getObject("item_id") != null) {
                OrderItem item = new OrderItem();
                item.setId(rs.getLong("item_id"));
                item.setProductId(rs.getLong("product_id"));
                item.setQuantity(rs.getInt("quantity"));
                order.getOrderItems().add(item);
            }
        }
        return order;
    }, orderId);
}
```

**ResultSetExtractor 사용 사례 2** (복잡한 집계):
```java
// ✅ 사용자별 주문 통계
public Map<Long, OrderStatistics> getUserOrderStatistics() {
    String sql = """
        SELECT user_id, COUNT(*) as order_count, SUM(total_amount) as total_sales
        FROM orders
        GROUP BY user_id
    """;

    return jdbcTemplate.query(sql, rs -> {
        Map<Long, OrderStatistics> result = new HashMap<>();

        while (rs.next()) {
            Long userId = rs.getLong("user_id");
            OrderStatistics stats = new OrderStatistics();
            stats.setOrderCount(rs.getInt("order_count"));
            stats.setTotalSales(rs.getBigDecimal("total_sales"));

            result.put(userId, stats);
        }

        return result;
    });
}
```

**선택 기준**:
```
RowMapper:
✅ 각 행이 독립적인 객체
✅ List<T> 반환
✅ 간단한 매핑
✅ 1:1 관계

ResultSetExtractor:
✅ 복잡한 결과 구조
✅ 1:N 관계 (JOIN)
✅ Map, Set 등 반환
✅ 집계 결과
✅ 커스텀 자료구조
```

---

**Q4: 대용량 데이터 배치 처리 시 JdbcTemplate을 사용하면 어떤 이점이 있나요? 메모리 관리는 어떻게 하나요?**

**A**:

**JdbcTemplate의 배치 처리 이점**:

1. **성능**:
   ```
   개별 INSERT: 1000건 → 10초
   Batch INSERT: 1000건 → 1초
   → 10배 빠름
   ```

2. **메모리 효율**:
   ```
   JPA: 모든 엔티티를 영속성 컨텍스트에 보관 → 메모리 2GB
   JdbcTemplate: 영속성 컨텍스트 없음 → 메모리 10MB
   → 200배 효율적
   ```

3. **트랜잭션 제어**:
   ```
   청크 단위로 트랜잭션 분리
   → 실패 시 부분 롤백 가능
   ```

**배치 처리 구현**:

```java
@Component
@RequiredArgsConstructor
@Slf4j
public class DataBatchProcessor {

    private final JdbcTemplate jdbcTemplate;

    // 방법 1: 전체 배치 처리
    @Transactional
    public void processAll(List<User> users) {
        String sql = "INSERT INTO users (name, email) VALUES (?, ?)";

        jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
            @Override
            public void setValues(PreparedStatement ps, int i) throws SQLException {
                User user = users.get(i);
                ps.setString(1, user.getName());
                ps.setString(2, user.getEmail());
            }

            @Override
            public int getBatchSize() {
                return users.size();
            }
        });
    }

    // 방법 2: 청크 단위 처리 (메모리 효율적)
    @Transactional
    public void processInChunks(List<User> users, int chunkSize) {
        String sql = "INSERT INTO users (name, email) VALUES (?, ?)";

        for (int i = 0; i < users.size(); i += chunkSize) {
            int end = Math.min(i + chunkSize, users.size());
            List<User> chunk = users.subList(i, end);

            jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
                @Override
                public void setValues(PreparedStatement ps, int index) throws SQLException {
                    User user = chunk.get(index);
                    ps.setString(1, user.getName());
                    ps.setString(2, user.getEmail());
                }

                @Override
                public int getBatchSize() {
                    return chunk.size();
                }
            });

            log.info("Processed chunk: {}-{}", i, end);
        }
    }

    // 방법 3: 스트림 처리 (메모리 최소화)
    public void processStream(Stream<User> userStream, int chunkSize) {
        AtomicInteger counter = new AtomicInteger(0);
        List<User> chunk = new ArrayList<>(chunkSize);

        userStream.forEach(user -> {
            chunk.add(user);

            if (chunk.size() >= chunkSize) {
                processBatch(chunk);
                chunk.clear();
            }
        });

        // 마지막 청크 처리
        if (!chunk.isEmpty()) {
            processBatch(chunk);
        }
    }

    @Transactional
    private void processBatch(List<User> users) {
        String sql = "INSERT INTO users (name, email) VALUES (?, ?)";

        jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
            @Override
            public void setValues(PreparedStatement ps, int i) throws SQLException {
                User user = users.get(i);
                ps.setString(1, user.getName());
                ps.setString(2, user.getEmail());
            }

            @Override
            public int getBatchSize() {
                return users.size();
            }
        });
    }
}
```

**메모리 관리 전략**:

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class LargeDataProcessor {

    private final JdbcTemplate jdbcTemplate;

    // ✅ Cursor 기반 처리 (메모리 효율 최고)
    public void processLargeDataset() {
        String sql = "SELECT * FROM users";

        jdbcTemplate.query(sql, rs -> {
            int count = 0;
            List<User> batch = new ArrayList<>(1000);

            while (rs.next()) {
                User user = new User();
                user.setId(rs.getLong("id"));
                user.setName(rs.getString("name"));
                user.setEmail(rs.getString("email"));

                batch.add(user);

                if (batch.size() >= 1000) {
                    processUsers(batch);
                    batch.clear();
                    count += 1000;
                    log.info("Processed {} users", count);
                }
            }

            // 마지막 배치 처리
            if (!batch.isEmpty()) {
                processUsers(batch);
            }
        });
    }

    private void processUsers(List<User> users) {
        // 비즈니스 로직 처리
    }
}
```

**JPA vs JdbcTemplate 배치 처리 비교**:

| 지표 | JPA | JdbcTemplate |
|------|-----|--------------|
| **100만 건 INSERT** | 60초 | 30초 |
| **메모리 사용** | 2GB | 10MB |
| **코드 복잡도** | 낮음 | 보통 |
| **성능 튜닝** | 어려움 | 쉬움 |

**실무 권장 패턴**:

```java
@Component
@RequiredArgsConstructor
public class OptimizedBatchProcessor {

    private final JdbcTemplate jdbcTemplate;

    // ✅ 최적화된 배치 처리
    public void processBatch(int batchSize) {
        String selectSql = "SELECT * FROM source_table WHERE processed = false LIMIT ?";
        String insertSql = "INSERT INTO target_table (name, email) VALUES (?, ?)";
        String updateSql = "UPDATE source_table SET processed = true WHERE id = ?";

        while (true) {
            // 1. 배치 크기만큼 조회
            List<SourceData> batch = jdbcTemplate.query(
                selectSql,
                (rs, rowNum) -> {
                    SourceData data = new SourceData();
                    data.setId(rs.getLong("id"));
                    data.setName(rs.getString("name"));
                    data.setEmail(rs.getString("email"));
                    return data;
                },
                batchSize
            );

            if (batch.isEmpty()) {
                break;
            }

            // 2. 배치 INSERT
            jdbcTemplate.batchUpdate(insertSql, new BatchPreparedStatementSetter() {
                @Override
                public void setValues(PreparedStatement ps, int i) throws SQLException {
                    SourceData data = batch.get(i);
                    ps.setString(1, data.getName());
                    ps.setString(2, data.getEmail());
                }

                @Override
                public int getBatchSize() {
                    return batch.size();
                }
            });

            // 3. 배치 UPDATE
            jdbcTemplate.batchUpdate(updateSql, new BatchPreparedStatementSetter() {
                @Override
                public void setValues(PreparedStatement ps, int i) throws SQLException {
                    ps.setLong(1, batch.get(i).getId());
                }

                @Override
                public int getBatchSize() {
                    return batch.size();
                }
            });

            log.info("Processed {} records", batch.size());
        }
    }
}
```

---

**Q5: JdbcTemplate에서 트랜잭션을 관리하는 방법과 @Transactional과의 통합에 대해 설명해주세요.**

**A**:

**JdbcTemplate은 Spring의 트랜잭션 관리와 완전히 통합됩니다.**

**@Transactional 사용** (선언적 트랜잭션):

```java
@Service
@RequiredArgsConstructor
@Transactional
public class OrderService {

    private final JdbcTemplate jdbcTemplate;

    public void createOrder(Order order) {
        // 1. 주문 생성
        String orderSql = "INSERT INTO orders (user_id, total_amount) VALUES (?, ?)";
        jdbcTemplate.update(orderSql, order.getUserId(), order.getTotalAmount());

        // 2. 주문 항목 생성
        String itemSql = "INSERT INTO order_items (order_id, product_id) VALUES (?, ?)";
        for (OrderItem item : order.getItems()) {
            jdbcTemplate.update(itemSql, order.getId(), item.getProductId());
        }

        // 3. 재고 차감
        String stockSql = "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?";
        for (OrderItem item : order.getItems()) {
            jdbcTemplate.update(stockSql, item.getQuantity(), item.getProductId());
        }

        // 모두 성공 → COMMIT
        // 하나라도 실패 → ROLLBACK (자동)
    }
}
```

**동작 원리**:
```
1. @Transactional 메서드 호출
2. Spring AOP가 프록시 생성
3. TransactionManager.begin() 호출
4. Connection 획득하고 트랜잭션 시작
5. JdbcTemplate은 같은 Connection 사용
6. 메서드 성공 → TransactionManager.commit()
7. 메서드 실패 → TransactionManager.rollback()
```

**TransactionTemplate 사용** (프로그래밍 방식):

```java
@Service
@RequiredArgsConstructor
public class OrderService {

    private final JdbcTemplate jdbcTemplate;
    private final TransactionTemplate transactionTemplate;

    public void createOrder(Order order) {
        transactionTemplate.execute(status -> {
            try {
                // 비즈니스 로직
                String orderSql = "INSERT INTO orders (user_id, total_amount) VALUES (?, ?)";
                jdbcTemplate.update(orderSql, order.getUserId(), order.getTotalAmount());

                String itemSql = "INSERT INTO order_items (order_id, product_id) VALUES (?, ?)";
                for (OrderItem item : order.getItems()) {
                    jdbcTemplate.update(itemSql, order.getId(), item.getProductId());
                }

                return null;
            } catch (Exception e) {
                status.setRollbackOnly();
                throw e;
            }
        });
    }
}
```

**중첩 트랜잭션**:

```java
@Service
@RequiredArgsConstructor
public class OrderService {

    private final JdbcTemplate jdbcTemplate;
    private final LogService logService;

    @Transactional
    public void createOrder(Order order) {
        // 주문 생성
        String sql = "INSERT INTO orders (user_id, total_amount) VALUES (?, ?)";
        jdbcTemplate.update(sql, order.getUserId(), order.getTotalAmount());

        // 로그 저장 (새로운 트랜잭션)
        logService.saveLog("Order created: " + order.getId());

        // 주문 생성 실패해도 로그는 저장됨
    }
}

@Service
@RequiredArgsConstructor
public class LogService {

    private final JdbcTemplate jdbcTemplate;

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void saveLog(String message) {
        String sql = "INSERT INTO logs (message) VALUES (?)";
        jdbcTemplate.update(sql, message);
        // 항상 새로운 트랜잭션
        // 부모 트랜잭션과 독립적
    }
}
```

**읽기 전용 트랜잭션**:

```java
@Service
@RequiredArgsConstructor
public class UserService {

    private final JdbcTemplate jdbcTemplate;

    // ✅ 읽기 전용 → Slave DB 라우팅 가능
    @Transactional(readOnly = true)
    public List<User> getAllUsers() {
        String sql = "SELECT * FROM users";

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            User user = new User();
            user.setId(rs.getLong("id"));
            user.setName(rs.getString("name"));
            return user;
        });
    }

    // ✅ 쓰기 작업 → Master DB
    @Transactional
    public void createUser(User user) {
        String sql = "INSERT INTO users (name, email) VALUES (?, ?)";
        jdbcTemplate.update(sql, user.getName(), user.getEmail());
    }
}
```

**트랜잭션 격리 수준**:

```java
@Service
public class PaymentService {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    // READ_COMMITTED: 일반적인 경우
    @Transactional(isolation = Isolation.READ_COMMITTED)
    public void processPayment(Payment payment) {
        String sql = "INSERT INTO payments (user_id, amount) VALUES (?, ?)";
        jdbcTemplate.update(sql, payment.getUserId(), payment.getAmount());
    }

    // SERIALIZABLE: 금융 거래 (완전한 격리)
    @Transactional(isolation = Isolation.SERIALIZABLE)
    public void transferMoney(Long fromId, Long toId, BigDecimal amount) {
        String debitSql = "UPDATE accounts SET balance = balance - ? WHERE id = ?";
        jdbcTemplate.update(debitSql, amount, fromId);

        String creditSql = "UPDATE accounts SET balance = balance + ? WHERE id = ?";
        jdbcTemplate.update(creditSql, amount, toId);
    }
}
```

**트랜잭션 롤백 제어**:

```java
@Service
public class OrderService {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    // RuntimeException만 롤백 (기본 동작)
    @Transactional
    public void createOrder1(Order order) {
        String sql = "INSERT INTO orders (user_id, total_amount) VALUES (?, ?)";
        jdbcTemplate.update(sql, order.getUserId(), order.getTotalAmount());

        throw new RuntimeException("Error");  // ✅ 롤백됨
    }

    // Checked Exception은 롤백 안 됨 (기본)
    @Transactional
    public void createOrder2(Order order) throws Exception {
        String sql = "INSERT INTO orders (user_id, total_amount) VALUES (?, ?)";
        jdbcTemplate.update(sql, order.getUserId(), order.getTotalAmount());

        throw new Exception("Error");  // ❌ 롤백 안 됨! (커밋됨)
    }

    // rollbackFor로 Checked Exception도 롤백
    @Transactional(rollbackFor = Exception.class)
    public void createOrder3(Order order) throws Exception {
        String sql = "INSERT INTO orders (user_id, total_amount) VALUES (?, ?)";
        jdbcTemplate.update(sql, order.getUserId(), order.getTotalAmount());

        throw new Exception("Error");  // ✅ 롤백됨
    }
}
```

**정리**:
```
✅ JdbcTemplate은 Spring 트랜잭션 관리와 완전 통합
✅ @Transactional 사용 권장 (선언적)
✅ 같은 트랜잭션 내에서 모든 JdbcTemplate 작업 공유
✅ 중첩 트랜잭션 지원 (Propagation 설정)
✅ 읽기 전용 최적화 (readOnly = true)
```

---

## 📝 핵심 정리

### Spring JDBC 핵심 개념

**JdbcTemplate의 주요 장점**:
1. 자동 리소스 관리 (Connection, Statement, ResultSet)
2. 예외 변환 (SQLException → DataAccessException)
3. 코드 간결화 (67% 감소)
4. 안정성 향상 (메모리 누수 방지)

**주요 메서드**:

| 메서드 | 용도 | 반환 타입 |
|--------|------|-----------|
| `query()` | 여러 행 조회 | `List<T>` |
| `queryForObject()` | 단일 행 조회 | `T` |
| `update()` | INSERT/UPDATE/DELETE | `int` |
| `batchUpdate()` | 대량 처리 | `int[]` |

**실무 권장**:
- 간단한 CRUD: JPA
- 복잡한 쿼리: JdbcTemplate
- 대량 처리: batchUpdate()
- 파라미터 많을 때: NamedParameterJdbcTemplate

---

**다음 장으로**: [→ 다음: 21장 - JPA 기본](SpringMVC-Part13-21-JPA-Basics.md)

**이전 장으로**: [← 이전: 19장 - 데이터베이스 연동 개요](SpringMVC-Part11-19-Database-Integration-Overview.md)

**목차로 돌아가기**: [📚 전체 목차](README.md)
