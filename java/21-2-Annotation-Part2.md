# 📝 Chapter 21-2: Annotation Part 2

## 🎯 학습 목표
- 실제 기업에서 Annotation을 어떻게 활용하는지 학습합니다
- Spring Framework의 핵심 Annotation 패턴을 이해합니다
- JPA/Hibernate의 ORM Annotation을 실습합니다
- 주니어 개발자가 자주 실수하는 Annotation 사용법을 배웁니다
- 실전에서 마주칠 수 있는 문제와 해결 방법을 익힙니다

---

## 🏢 기업 사례 연구

---

## 📘 Case Study 1: Spring Framework - Dependency Injection

### 배경
**네이버** 쇼핑 서비스 개발 팀은 수백 개의 클래스를 관리해야 합니다.
객체 생성과 의존성 관리를 수동으로 하면 코드가 복잡해지고 유지보수가 어려워집니다.

**해결책**: Spring의 DI (Dependency Injection) Annotation을 활용하여 객체 생성과 의존성 관리를 자동화합니다.

### 핵심 Annotation
- `@Component`: 스프링이 관리하는 빈(Bean)으로 등록
- `@Service`: 비즈니스 로직 계층
- `@Repository`: 데이터 접근 계층
- `@Controller` / `@RestController`: 웹 계층
- `@Autowired`: 의존성 자동 주입
- `@Qualifier`: 같은 타입의 빈이 여러 개일 때 구분
- `@Value`: 설정 파일의 값 주입

### 실제 코드

```java
// 📁 SpringDIExample.java

import java.lang.annotation.*;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.util.*;

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 1️⃣ Spring-like Annotations 정의
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@interface Component {
    String value() default "";
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@interface Service {
    String value() default "";
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@interface Repository {
    String value() default "";
}

@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.FIELD, ElementType.CONSTRUCTOR})
@interface Autowired {
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Qualifier {
    String value();
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 2️⃣ Simple DI Container (Spring IoC Container의 단순화 버전)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SimpleContainer {
    private Map<String, Object> beans = new HashMap<>();

    public void registerBean(Class<?> clazz) throws Exception {
        if (clazz.isAnnotationPresent(Component.class) ||
            clazz.isAnnotationPresent(Service.class) ||
            clazz.isAnnotationPresent(Repository.class)) {

            String beanName = getBeanName(clazz);
            Object instance = createInstance(clazz);
            beans.put(beanName, instance);

            System.out.println("✅ Bean 등록: " + beanName + " (" + clazz.getSimpleName() + ")");
        }
    }

    public void injectDependencies() throws Exception {
        for (Object bean : beans.values()) {
            for (Field field : bean.getClass().getDeclaredFields()) {
                if (field.isAnnotationPresent(Autowired.class)) {
                    field.setAccessible(true);

                    String beanName;
                    if (field.isAnnotationPresent(Qualifier.class)) {
                        beanName = field.getAnnotation(Qualifier.class).value();
                    } else {
                        beanName = field.getType().getSimpleName().substring(0, 1).toLowerCase() +
                                   field.getType().getSimpleName().substring(1);
                    }

                    Object dependency = beans.get(beanName);
                    if (dependency != null) {
                        field.set(bean, dependency);
                        System.out.println("💉 의존성 주입: " + bean.getClass().getSimpleName() +
                                         "." + field.getName() + " ← " + beanName);
                    }
                }
            }
        }
    }

    private Object createInstance(Class<?> clazz) throws Exception {
        Constructor<?> constructor = clazz.getDeclaredConstructor();
        constructor.setAccessible(true);
        return constructor.newInstance();
    }

    private String getBeanName(Class<?> clazz) {
        String simpleName = clazz.getSimpleName();
        return simpleName.substring(0, 1).toLowerCase() + simpleName.substring(1);
    }

    public <T> T getBean(String name) {
        return (T) beans.get(name);
    }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 3️⃣ 실제 비즈니스 로직: 네이버 쇼핑 서비스
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// Repository 계층 - 데이터베이스 접근
@Repository
class ProductRepository {
    public String findProductById(int productId) {
        System.out.println("  🗄️ DB에서 상품 조회: ID = " + productId);
        return "무선 이어폰 (89,000원)";
    }

    public void saveProduct(String productName) {
        System.out.println("  🗄️ DB에 상품 저장: " + productName);
    }
}

@Repository
class UserRepository {
    public String findUserById(int userId) {
        System.out.println("  🗄️ DB에서 사용자 조회: ID = " + userId);
        return "김철수 (VIP 회원)";
    }
}

// Service 계층 - 비즈니스 로직
@Service
class OrderService {

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PaymentService paymentService;

    public void createOrder(int userId, int productId) {
        System.out.println("\n📦 [주문 생성 프로세스 시작]");

        // 1. 사용자 조회
        String user = userRepository.findUserById(userId);
        System.out.println("  ✅ 사용자 확인: " + user);

        // 2. 상품 조회
        String product = productRepository.findProductById(productId);
        System.out.println("  ✅ 상품 확인: " + product);

        // 3. 결제 처리
        boolean paymentSuccess = paymentService.processPayment(userId, 89000);
        if (paymentSuccess) {
            System.out.println("  ✅ 주문 완료!");
        } else {
            System.out.println("  ❌ 결제 실패 - 주문 취소");
        }
    }
}

@Service
class PaymentService {
    public boolean processPayment(int userId, int amount) {
        System.out.println("  💳 결제 처리: 사용자 ID = " + userId + ", 금액 = " + amount + "원");
        return true;  // 결제 성공 가정
    }
}

// Component 계층 - 공통 유틸리티
@Component
class NotificationService {

    @Autowired
    private EmailSender emailSender;

    public void sendOrderConfirmation(int userId) {
        System.out.println("\n📧 [주문 확인 알림 발송]");
        emailSender.send("user" + userId + "@example.com", "주문이 완료되었습니다!");
    }
}

@Component
class EmailSender {
    public void send(String to, String message) {
        System.out.println("  📨 이메일 발송: " + to);
        System.out.println("  💬 메시지: " + message);
    }
}

public class SpringDIExample {
    public static void main(String[] args) throws Exception {
        System.out.println("=== Spring DI (Dependency Injection) 예제 ===");
        System.out.println("네이버 쇼핑 서비스 시뮬레이션\n");

        System.out.println("=".repeat(50));
        System.out.println("1️⃣ Spring Container 초기화 - Bean 등록");
        System.out.println("=".repeat(50) + "\n");

        SimpleContainer container = new SimpleContainer();

        // 모든 컴포넌트를 컨테이너에 등록
        container.registerBean(ProductRepository.class);
        container.registerBean(UserRepository.class);
        container.registerBean(OrderService.class);
        container.registerBean(PaymentService.class);
        container.registerBean(NotificationService.class);
        container.registerBean(EmailSender.class);

        System.out.println("\n" + "=".repeat(50));
        System.out.println("2️⃣ 의존성 주입 (Dependency Injection)");
        System.out.println("=".repeat(50) + "\n");

        container.injectDependencies();

        System.out.println("\n" + "=".repeat(50));
        System.out.println("3️⃣ 실제 비즈니스 로직 실행");
        System.out.println("=".repeat(50));

        // Bean 가져오기
        OrderService orderService = container.getBean("orderService");
        NotificationService notificationService = container.getBean("notificationService");

        // 주문 생성
        orderService.createOrder(1001, 5001);

        // 알림 발송
        notificationService.sendOrderConfirmation(1001);

        System.out.println("\n" + "=".repeat(50));
        System.out.println("\n💡 Spring DI의 핵심 가치:");
        System.out.println("\n1️⃣ 느슨한 결합 (Loose Coupling)");
        System.out.println("   - OrderService는 구체적인 Repository 구현을 몰라도 됨");
        System.out.println("   - 인터페이스만 의존 → 구현체 교체 용이");

        System.out.println("\n2️⃣ 테스트 용이성");
        System.out.println("   - Mock 객체로 쉽게 교체 가능");
        System.out.println("   - 단위 테스트 작성이 간편");

        System.out.println("\n3️⃣ 코드 재사용성");
        System.out.println("   - 같은 Bean을 여러 곳에서 공유");
        System.out.println("   - Singleton 패턴 자동 적용");

        System.out.println("\n4️⃣ 관심사 분리 (Separation of Concerns)");
        System.out.println("   - Repository: 데이터 접근만 담당");
        System.out.println("   - Service: 비즈니스 로직만 담당");
        System.out.println("   - Controller: HTTP 요청 처리만 담당");

        System.out.println("\n" + "=".repeat(50));
        System.out.println("\n🌟 실제 Spring에서 사용하는 Annotation:");
        System.out.println("  @Component - 일반 컴포넌트");
        System.out.println("  @Service - 비즈니스 로직 계층");
        System.out.println("  @Repository - 데이터 접근 계층");
        System.out.println("  @Controller - 웹 MVC 컨트롤러");
        System.out.println("  @RestController - REST API 컨트롤러");
        System.out.println("  @Autowired - 의존성 자동 주입");
        System.out.println("  @Qualifier - 같은 타입의 Bean 중 선택");
        System.out.println("  @Primary - 우선 순위 Bean 지정");
        System.out.println("  @Scope - Bean의 생명주기 설정 (singleton, prototype 등)");
    }
}
```

**실행 결과:**
```
=== Spring DI (Dependency Injection) 예제 ===
네이버 쇼핑 서비스 시뮬레이션

==================================================
1️⃣ Spring Container 초기화 - Bean 등록
==================================================

✅ Bean 등록: productRepository (ProductRepository)
✅ Bean 등록: userRepository (UserRepository)
✅ Bean 등록: orderService (OrderService)
✅ Bean 등록: paymentService (PaymentService)
✅ Bean 등록: notificationService (NotificationService)
✅ Bean 등록: emailSender (EmailSender)

==================================================
2️⃣ 의존성 주입 (Dependency Injection)
==================================================

💉 의존성 주입: OrderService.productRepository ← productRepository
💉 의존성 주입: OrderService.userRepository ← userRepository
💉 의존성 주입: OrderService.paymentService ← paymentService
💉 의존성 주입: NotificationService.emailSender ← emailSender

==================================================
3️⃣ 실제 비즈니스 로직 실행
==================================================

📦 [주문 생성 프로세스 시작]
  🗄️ DB에서 사용자 조회: ID = 1001
  ✅ 사용자 확인: 김철수 (VIP 회원)
  🗄️ DB에서 상품 조회: ID = 5001
  ✅ 상품 확인: 무선 이어폰 (89,000원)
  💳 결제 처리: 사용자 ID = 1001, 금액 = 89000원
  ✅ 주문 완료!

📧 [주문 확인 알림 발송]
  📨 이메일 발송: user1001@example.com
  💬 메시지: 주문이 완료되었습니다!

==================================================

💡 Spring DI의 핵심 가치:

1️⃣ 느슨한 결합 (Loose Coupling)
   - OrderService는 구체적인 Repository 구현을 몰라도 됨
   - 인터페이스만 의존 → 구현체 교체 용이

2️⃣ 테스트 용이성
   - Mock 객체로 쉽게 교체 가능
   - 단위 테스트 작성이 간편

3️⃣ 코드 재사용성
   - 같은 Bean을 여러 곳에서 공유
   - Singleton 패턴 자동 적용

4️⃣ 관심사 분리 (Separation of Concerns)
   - Repository: 데이터 접근만 담당
   - Service: 비즈니스 로직만 담당
   - Controller: HTTP 요청 처리만 담당

==================================================

🌟 실제 Spring에서 사용하는 Annotation:
  @Component - 일반 컴포넌트
  @Service - 비즈니스 로직 계층
  @Repository - 데이터 접근 계층
  @Controller - 웹 MVC 컨트롤러
  @RestController - REST API 컨트롤러
  @Autowired - 의존성 자동 주입
  @Qualifier - 같은 타입의 Bean 중 선택
  @Primary - 우선 순위 Bean 지정
  @Scope - Bean의 생명주기 설정 (singleton, prototype 등)
```

---

## 📗 Case Study 2: JPA/Hibernate - ORM Mapping

### 배경
**배달의민족** 개발 팀은 수십 개의 테이블을 관리해야 합니다.
SQL을 직접 작성하면 오타, 중복 코드, 데이터베이스 종속성 등의 문제가 발생합니다.

**해결책**: JPA Annotation을 사용하여 Java 객체와 DB 테이블을 자동 매핑합니다.

### 핵심 Annotation
- `@Entity`: 이 클래스는 DB 테이블과 매핑되는 엔티티
- `@Table`: 테이블 이름, 스키마 등 지정
- `@Id`: 기본 키(Primary Key)
- `@GeneratedValue`: 기본 키 자동 생성 전략
- `@Column`: 컬럼 매핑 (이름, 길이, null 허용 여부 등)
- `@OneToMany`, `@ManyToOne`: 관계 매핑

### 실제 코드

```java
// 📁 JPAExample.java

import java.lang.annotation.*;
import java.lang.reflect.Field;
import java.util.*;

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 1️⃣ JPA-like Annotations 정의
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@interface Entity {
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@interface Table {
    String name();
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Id {
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Column {
    String name();
    int length() default 255;
    boolean nullable() default true;
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface GeneratedValue {
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 2️⃣ Simple ORM Framework (JPA의 단순화 버전)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SimpleORM {

    // CREATE TABLE 문 생성
    public static String generateCreateTable(Class<?> clazz) {
        if (!clazz.isAnnotationPresent(Entity.class)) {
            throw new IllegalArgumentException(clazz.getName() + "은(는) @Entity가 아닙니다");
        }

        Table tableAnnotation = clazz.getAnnotation(Table.class);
        String tableName = tableAnnotation != null ? tableAnnotation.name() :
                          toSnakeCase(clazz.getSimpleName());

        StringBuilder sql = new StringBuilder();
        sql.append("CREATE TABLE ").append(tableName).append(" (\n");

        List<String> columns = new ArrayList<>();

        for (Field field : clazz.getDeclaredFields()) {
            StringBuilder columnDef = new StringBuilder();

            String columnName;
            if (field.isAnnotationPresent(Column.class)) {
                Column column = field.getAnnotation(Column.class);
                columnName = column.name();

                columnDef.append("  ").append(columnName);

                // 타입 추론
                if (field.getType() == String.class) {
                    columnDef.append(" VARCHAR(").append(column.length()).append(")");
                } else if (field.getType() == Integer.class || field.getType() == int.class) {
                    columnDef.append(" INT");
                } else if (field.getType() == Long.class || field.getType() == long.class) {
                    columnDef.append(" BIGINT");
                } else if (field.getType() == Boolean.class || field.getType() == boolean.class) {
                    columnDef.append(" BOOLEAN");
                }

                // Primary Key
                if (field.isAnnotationPresent(Id.class)) {
                    columnDef.append(" PRIMARY KEY");
                    if (field.isAnnotationPresent(GeneratedValue.class)) {
                        columnDef.append(" AUTO_INCREMENT");
                    }
                } else if (!column.nullable()) {
                    columnDef.append(" NOT NULL");
                }

                columns.add(columnDef.toString());
            }
        }

        sql.append(String.join(",\n", columns));
        sql.append("\n);");

        return sql.toString();
    }

    // INSERT 문 생성
    public static String generateInsert(Object entity) throws IllegalAccessException {
        Class<?> clazz = entity.getClass();
        Table tableAnnotation = clazz.getAnnotation(Table.class);
        String tableName = tableAnnotation != null ? tableAnnotation.name() :
                          toSnakeCase(clazz.getSimpleName());

        List<String> columnNames = new ArrayList<>();
        List<String> values = new ArrayList<>();

        for (Field field : clazz.getDeclaredFields()) {
            field.setAccessible(true);

            // @Id이면서 @GeneratedValue이면 제외 (자동 생성)
            if (field.isAnnotationPresent(Id.class) &&
                field.isAnnotationPresent(GeneratedValue.class)) {
                continue;
            }

            if (field.isAnnotationPresent(Column.class)) {
                Column column = field.getAnnotation(Column.class);
                columnNames.add(column.name());

                Object value = field.get(entity);
                if (value instanceof String) {
                    values.add("'" + value + "'");
                } else {
                    values.add(value != null ? value.toString() : "NULL");
                }
            }
        }

        return String.format("INSERT INTO %s (%s) VALUES (%s);",
                           tableName,
                           String.join(", ", columnNames),
                           String.join(", ", values));
    }

    private static String toSnakeCase(String camelCase) {
        return camelCase.replaceAll("([a-z])([A-Z])", "$1_$2").toLowerCase();
    }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 3️⃣ 실제 엔티티: 배달의민족 도메인 모델
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Entity
@Table(name = "restaurants")
class Restaurant {

    @Id
    @GeneratedValue
    @Column(name = "restaurant_id")
    private Long restaurantId;

    @Column(name = "name", length = 100, nullable = false)
    private String name;

    @Column(name = "category", length = 50, nullable = false)
    private String category;

    @Column(name = "min_order_amount", nullable = false)
    private Integer minOrderAmount;

    @Column(name = "delivery_fee", nullable = false)
    private Integer deliveryFee;

    @Column(name = "rating")
    private Integer rating;  // 1~5점

    @Column(name = "is_open", nullable = false)
    private Boolean isOpen;

    public Restaurant(Long restaurantId, String name, String category,
                     Integer minOrderAmount, Integer deliveryFee,
                     Integer rating, Boolean isOpen) {
        this.restaurantId = restaurantId;
        this.name = name;
        this.category = category;
        this.minOrderAmount = minOrderAmount;
        this.deliveryFee = deliveryFee;
        this.rating = rating;
        this.isOpen = isOpen;
    }

    @Override
    public String toString() {
        return String.format("%s [%s] - 최소주문: %,d원, 배달비: %,d원, 평점: %d점",
                           name, category, minOrderAmount, deliveryFee, rating);
    }
}

@Entity
@Table(name = "menu_items")
class MenuItem {

    @Id
    @GeneratedValue
    @Column(name = "menu_id")
    private Long menuId;

    @Column(name = "restaurant_id", nullable = false)
    private Long restaurantId;

    @Column(name = "name", length = 100, nullable = false)
    private String name;

    @Column(name = "description", length = 500)
    private String description;

    @Column(name = "price", nullable = false)
    private Integer price;

    @Column(name = "is_popular", nullable = false)
    private Boolean isPopular;

    @Column(name = "is_sold_out", nullable = false)
    private Boolean isSoldOut;

    public MenuItem(Long menuId, Long restaurantId, String name,
                   String description, Integer price,
                   Boolean isPopular, Boolean isSoldOut) {
        this.menuId = menuId;
        this.restaurantId = restaurantId;
        this.name = name;
        this.description = description;
        this.price = price;
        this.isPopular = isPopular;
        this.isSoldOut = isSoldOut;
    }

    @Override
    public String toString() {
        String popularTag = isPopular ? " 🔥인기" : "";
        String soldOutTag = isSoldOut ? " ❌품절" : "";
        return String.format("%s - %,d원%s%s", name, price, popularTag, soldOutTag);
    }
}

@Entity
@Table(name = "orders")
class Order {

    @Id
    @GeneratedValue
    @Column(name = "order_id")
    private Long orderId;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "restaurant_id", nullable = false)
    private Long restaurantId;

    @Column(name = "total_amount", nullable = false)
    private Integer totalAmount;

    @Column(name = "delivery_address", length = 200, nullable = false)
    private String deliveryAddress;

    @Column(name = "order_status", length = 20, nullable = false)
    private String orderStatus;  // PENDING, CONFIRMED, DELIVERED 등

    public Order(Long orderId, Long userId, Long restaurantId,
                Integer totalAmount, String deliveryAddress, String orderStatus) {
        this.orderId = orderId;
        this.userId = userId;
        this.restaurantId = restaurantId;
        this.totalAmount = totalAmount;
        this.deliveryAddress = deliveryAddress;
        this.orderStatus = orderStatus;
    }
}

public class JPAExample {
    public static void main(String[] args) throws Exception {
        System.out.println("=== JPA ORM Mapping 예제 ===");
        System.out.println("배달의민족 도메인 모델\n");

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 1. CREATE TABLE 문 자동 생성
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        System.out.println("=".repeat(60));
        System.out.println("1️⃣ CREATE TABLE 문 자동 생성 (DDL)");
        System.out.println("=".repeat(60) + "\n");

        System.out.println("📋 Restaurant 테이블:\n");
        System.out.println(SimpleORM.generateCreateTable(Restaurant.class));

        System.out.println("\n" + "─".repeat(60) + "\n");

        System.out.println("📋 MenuItem 테이블:\n");
        System.out.println(SimpleORM.generateCreateTable(MenuItem.class));

        System.out.println("\n" + "─".repeat(60) + "\n");

        System.out.println("📋 Order 테이블:\n");
        System.out.println(SimpleORM.generateCreateTable(Order.class));

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 2. 엔티티 생성 및 INSERT 문 자동 생성
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        System.out.println("\n" + "=".repeat(60));
        System.out.println("2️⃣ INSERT 문 자동 생성 (DML)");
        System.out.println("=".repeat(60) + "\n");

        // Restaurant 엔티티
        Restaurant restaurant = new Restaurant(
            null,  // @GeneratedValue이므로 null
            "홍콩반점",
            "중식",
            15000,
            3000,
            5,
            true
        );

        System.out.println("🏪 식당 정보: " + restaurant);
        System.out.println("\n생성된 SQL:");
        System.out.println(SimpleORM.generateInsert(restaurant));

        System.out.println("\n" + "─".repeat(60) + "\n");

        // MenuItem 엔티티
        MenuItem menu1 = new MenuItem(
            null,
            1L,
            "짜장면",
            "고소하고 진한 춘장 소스",
            6000,
            true,
            false
        );

        MenuItem menu2 = new MenuItem(
            null,
            1L,
            "짬뽕",
            "얼큰한 해물 짬뽕",
            7000,
            true,
            false
        );

        System.out.println("🍜 메뉴 1: " + menu1);
        System.out.println("\n생성된 SQL:");
        System.out.println(SimpleORM.generateInsert(menu1));

        System.out.println("\n" + "─".repeat(60) + "\n");

        System.out.println("🍜 메뉴 2: " + menu2);
        System.out.println("\n생성된 SQL:");
        System.out.println(SimpleORM.generateInsert(menu2));

        System.out.println("\n" + "─".repeat(60) + "\n");

        // Order 엔티티
        Order order = new Order(
            null,
            1001L,
            1L,
            16000,  // 짜장면 6000 + 짬뽕 7000 + 배달비 3000
            "서울시 강남구 테헤란로 123",
            "PENDING"
        );

        System.out.println("📦 주문 정보 생성");
        System.out.println("\n생성된 SQL:");
        System.out.println(SimpleORM.generateInsert(order));

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 3. JPA의 장점 설명
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        System.out.println("\n" + "=".repeat(60));
        System.out.println("\n💡 JPA Annotation의 핵심 가치:");

        System.out.println("\n1️⃣ 데이터베이스 독립성");
        System.out.println("   - MySQL, PostgreSQL, Oracle 등 DB 교체 시");
        System.out.println("   - SQL 문법 차이를 JPA가 자동 처리");
        System.out.println("   - Java 코드는 변경 없음");

        System.out.println("\n2️⃣ 생산성 향상");
        System.out.println("   - SQL을 직접 작성하지 않아도 됨");
        System.out.println("   - CREATE TABLE, INSERT, UPDATE, DELETE 자동 생성");
        System.out.println("   - 객체 중심 개발 가능");

        System.out.println("\n3️⃣ 유지보수성");
        System.out.println("   - 컬럼 추가 시 @Column만 추가하면 끝");
        System.out.println("   - SQL 오타로 인한 런타임 에러 감소");
        System.out.println("   - 컴파일 타임에 오류 발견 가능");

        System.out.println("\n4️⃣ 객체-관계 매핑");
        System.out.println("   - Java의 객체 지향과 DB의 관계형 모델 연결");
        System.out.println("   - @OneToMany, @ManyToOne으로 관계 표현");
        System.out.println("   - Lazy Loading, Eager Loading 지원");

        System.out.println("\n" + "=".repeat(60));
        System.out.println("\n🌟 실제 JPA/Hibernate에서 사용하는 Annotation:");
        System.out.println("  @Entity - 엔티티 클래스 표시");
        System.out.println("  @Table - 테이블 매핑");
        System.out.println("  @Id - 기본 키");
        System.out.println("  @GeneratedValue - 기본 키 자동 생성 전략");
        System.out.println("  @Column - 컬럼 매핑");
        System.out.println("  @OneToMany - 1:N 관계");
        System.out.println("  @ManyToOne - N:1 관계");
        System.out.println("  @ManyToMany - N:M 관계");
        System.out.println("  @JoinColumn - 외래 키 매핑");
        System.out.println("  @Transient - DB 컬럼에서 제외");
    }
}
```

**실행 결과:**
```
=== JPA ORM Mapping 예제 ===
배달의민족 도메인 모델

============================================================
1️⃣ CREATE TABLE 문 자동 생성 (DDL)
============================================================

📋 Restaurant 테이블:

CREATE TABLE restaurants (
  restaurant_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  category VARCHAR(50) NOT NULL,
  min_order_amount INT NOT NULL,
  delivery_fee INT NOT NULL,
  rating INT,
  is_open BOOLEAN NOT NULL
);

────────────────────────────────────────────────────────────

📋 MenuItem 테이블:

CREATE TABLE menu_items (
  menu_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  restaurant_id BIGINT NOT NULL,
  name VARCHAR(100) NOT NULL,
  description VARCHAR(500),
  price INT NOT NULL,
  is_popular BOOLEAN NOT NULL,
  is_sold_out BOOLEAN NOT NULL
);

────────────────────────────────────────────────────────────

📋 Order 테이블:

CREATE TABLE orders (
  order_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  restaurant_id BIGINT NOT NULL,
  total_amount INT NOT NULL,
  delivery_address VARCHAR(200) NOT NULL,
  order_status VARCHAR(20) NOT NULL
);

============================================================
2️⃣ INSERT 문 자동 생성 (DML)
============================================================

🏪 식당 정보: 홍콩반점 [중식] - 최소주문: 15,000원, 배달비: 3,000원, 평점: 5점

생성된 SQL:
INSERT INTO restaurants (name, category, min_order_amount, delivery_fee, rating, is_open) VALUES ('홍콩반점', '중식', 15000, 3000, 5, true);

────────────────────────────────────────────────────────────

🍜 메뉴 1: 짜장면 - 6,000원 🔥인기

생성된 SQL:
INSERT INTO menu_items (restaurant_id, name, description, price, is_popular, is_sold_out) VALUES (1, '짜장면', '고소하고 진한 춘장 소스', 6000, true, false);

────────────────────────────────────────────────────────────

🍜 메뉴 2: 짬뽕 - 7,000원 🔥인기

생성된 SQL:
INSERT INTO menu_items (restaurant_id, name, description, price, is_popular, is_sold_out) VALUES (1, '짬뽕', '얼큰한 해물 짬뽕', 7000, true, false);

────────────────────────────────────────────────────────────

📦 주문 정보 생성

생성된 SQL:
INSERT INTO orders (user_id, restaurant_id, total_amount, delivery_address, order_status) VALUES (1001, 1, 16000, '서울시 강남구 테헤란로 123', 'PENDING');

============================================================

💡 JPA Annotation의 핵심 가치:

1️⃣ 데이터베이스 독립성
   - MySQL, PostgreSQL, Oracle 등 DB 교체 시
   - SQL 문법 차이를 JPA가 자동 처리
   - Java 코드는 변경 없음

2️⃣ 생산성 향상
   - SQL을 직접 작성하지 않아도 됨
   - CREATE TABLE, INSERT, UPDATE, DELETE 자동 생성
   - 객체 중심 개발 가능

3️⃣ 유지보수성
   - 컬럼 추가 시 @Column만 추가하면 끝
   - SQL 오타로 인한 런타임 에러 감소
   - 컴파일 타임에 오류 발견 가능

4️⃣ 객체-관계 매핑
   - Java의 객체 지향과 DB의 관계형 모델 연결
   - @OneToMany, @ManyToOne으로 관계 표현
   - Lazy Loading, Eager Loading 지원

============================================================

🌟 실제 JPA/Hibernate에서 사용하는 Annotation:
  @Entity - 엔티티 클래스 표시
  @Table - 테이블 매핑
  @Id - 기본 키
  @GeneratedValue - 기본 키 자동 생성 전략
  @Column - 컬럼 매핑
  @OneToMany - 1:N 관계
  @ManyToOne - N:1 관계
  @ManyToMany - N:M 관계
  @JoinColumn - 외래 키 매핑
  @Transient - DB 컬럼에서 제외
```

---

## 📙 Case Study 3: Spring REST API - Controller Annotations

### 배경
**카카오톡** 메시지 API 서버는 수천 개의 HTTP 요청을 처리해야 합니다.
각 요청의 라우팅, 파라미터 바인딩, 응답 변환을 수동으로 처리하면 코드가 복잡해집니다.

**해결책**: Spring Web MVC Annotation을 사용하여 선언적으로 REST API를 구현합니다.

### 핵심 Annotation
- `@RestController`: REST API 컨트롤러
- `@RequestMapping`: 기본 경로 지정
- `@GetMapping`, `@PostMapping`, `@PutMapping`, `@DeleteMapping`: HTTP 메서드별 매핑
- `@PathVariable`: URL 경로에서 변수 추출
- `@RequestParam`: 쿼리 파라미터 추출
- `@RequestBody`: HTTP 요청 본문을 객체로 변환
- `@ResponseStatus`: HTTP 상태 코드 지정

### 실제 코드

```java
// 📁 RestAPIExample.java

import java.lang.annotation.*;
import java.lang.reflect.Method;
import java.lang.reflect.Parameter;
import java.util.*;

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 1️⃣ Spring Web MVC-like Annotations 정의
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@interface RestController {
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@interface RequestMapping {
    String value();
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface GetMapping {
    String value();
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface PostMapping {
    String value();
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.PARAMETER)
@interface PathVariable {
    String value();
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.PARAMETER)
@interface RequestParam {
    String value();
    boolean required() default true;
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.PARAMETER)
@interface RequestBody {
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 2️⃣ DTO 클래스 (Data Transfer Object)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Message {
    private Long id;
    private String sender;
    private String receiver;
    private String content;
    private String timestamp;

    public Message(Long id, String sender, String receiver, String content, String timestamp) {
        this.id = id;
        this.sender = sender;
        this.receiver = receiver;
        this.content = content;
        this.timestamp = timestamp;
    }

    @Override
    public String toString() {
        return String.format("[%s] %s → %s: %s", timestamp, sender, receiver, content);
    }

    public Long getId() { return id; }
    public String getSender() { return sender; }
    public String getReceiver() { return receiver; }
    public String getContent() { return content; }
}

class SendMessageRequest {
    private String sender;
    private String receiver;
    private String content;

    public SendMessageRequest(String sender, String receiver, String content) {
        this.sender = sender;
        this.receiver = receiver;
        this.content = content;
    }

    public String getSender() { return sender; }
    public String getReceiver() { return receiver; }
    public String getContent() { return content; }
}

class ApiResponse<T> {
    private boolean success;
    private String message;
    private T data;

    public ApiResponse(boolean success, String message, T data) {
        this.success = success;
        this.message = message;
        this.data = data;
    }

    @Override
    public String toString() {
        return String.format("ApiResponse{success=%s, message='%s', data=%s}",
                           success, message, data);
    }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 3️⃣ REST API Controller - 카카오톡 메시지 API
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@RestController
@RequestMapping("/api/messages")
class MessageController {

    private static Map<Long, Message> messageStorage = new HashMap<>();
    private static Long idCounter = 1L;

    static {
        // 초기 데이터
        messageStorage.put(1L, new Message(1L, "김철수", "이영희", "안녕하세요!", "2025-10-10 09:00:00"));
        messageStorage.put(2L, new Message(2L, "이영희", "김철수", "반갑습니다!", "2025-10-10 09:01:00"));
        idCounter = 3L;
    }

    // GET /api/messages - 모든 메시지 조회
    @GetMapping("/")
    public ApiResponse<List<Message>> getAllMessages() {
        System.out.println("📥 [GET] /api/messages - 모든 메시지 조회");
        List<Message> messages = new ArrayList<>(messageStorage.values());
        return new ApiResponse<>(true, "메시지 목록 조회 성공", messages);
    }

    // GET /api/messages/{id} - 특정 메시지 조회
    @GetMapping("/{id}")
    public ApiResponse<Message> getMessageById(@PathVariable("id") Long id) {
        System.out.println("📥 [GET] /api/messages/" + id + " - 메시지 조회");

        Message message = messageStorage.get(id);
        if (message != null) {
            return new ApiResponse<>(true, "메시지 조회 성공", message);
        } else {
            return new ApiResponse<>(false, "메시지를 찾을 수 없습니다", null);
        }
    }

    // GET /api/messages/search?sender=김철수 - 검색
    @GetMapping("/search")
    public ApiResponse<List<Message>> searchMessages(@RequestParam("sender") String sender) {
        System.out.println("📥 [GET] /api/messages/search?sender=" + sender + " - 메시지 검색");

        List<Message> results = new ArrayList<>();
        for (Message msg : messageStorage.values()) {
            if (msg.getSender().equals(sender)) {
                results.add(msg);
            }
        }

        return new ApiResponse<>(true, sender + "가 보낸 메시지 " + results.size() + "개", results);
    }

    // POST /api/messages - 새 메시지 전송
    @PostMapping("/")
    public ApiResponse<Message> sendMessage(@RequestBody SendMessageRequest request) {
        System.out.println("📤 [POST] /api/messages - 새 메시지 전송");
        System.out.println("   요청 본문: " + request.getSender() + " → " + request.getReceiver());

        Message newMessage = new Message(
            idCounter++,
            request.getSender(),
            request.getReceiver(),
            request.getContent(),
            "2025-10-10 10:00:00"
        );

        messageStorage.put(newMessage.getId(), newMessage);

        return new ApiResponse<>(true, "메시지 전송 성공", newMessage);
    }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 4️⃣ Simple Web Framework (Annotation 기반 라우팅)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SimpleWebFramework {

    public static void handleRequest(Object controller, String httpMethod, String path) throws Exception {
        Class<?> clazz = controller.getClass();

        if (!clazz.isAnnotationPresent(RestController.class)) {
            System.out.println("❌ @RestController가 아닙니다");
            return;
        }

        String basePath = "";
        if (clazz.isAnnotationPresent(RequestMapping.class)) {
            basePath = clazz.getAnnotation(RequestMapping.class).value();
        }

        for (Method method : clazz.getDeclaredMethods()) {
            String methodPath = null;
            String methodHttpMethod = null;

            if (method.isAnnotationPresent(GetMapping.class)) {
                methodHttpMethod = "GET";
                methodPath = method.getAnnotation(GetMapping.class).value();
            } else if (method.isAnnotationPresent(PostMapping.class)) {
                methodHttpMethod = "POST";
                methodPath = method.getAnnotation(PostMapping.class).value();
            }

            if (methodHttpMethod != null && methodHttpMethod.equals(httpMethod)) {
                String fullPath = basePath + methodPath;

                // 경로 매칭 (간단한 버전)
                if (pathMatches(fullPath, path)) {
                    System.out.println("✅ 매칭된 핸들러: " + method.getName() + "()");

                    // 파라미터 준비
                    Object[] args = prepareArguments(method, path);

                    // 메서드 실행
                    Object result = method.invoke(controller, args);

                    // 응답 출력
                    System.out.println("\n📨 응답:");
                    System.out.println(result);
                    return;
                }
            }
        }

        System.out.println("❌ 매칭되는 핸들러를 찾을 수 없습니다");
    }

    private static boolean pathMatches(String pattern, String path) {
        // 간단한 경로 매칭 (실제로는 더 복잡)
        if (pattern.equals(path)) return true;

        // {id} 같은 경로 변수 처리
        String[] patternParts = pattern.split("/");
        String[] pathParts = path.split("/");

        if (patternParts.length != pathParts.length) return false;

        for (int i = 0; i < patternParts.length; i++) {
            if (patternParts[i].startsWith("{") && patternParts[i].endsWith("}")) {
                continue;  // 경로 변수는 매칭
            }
            if (!patternParts[i].equals(pathParts[i])) {
                return false;
            }
        }

        return true;
    }

    private static Object[] prepareArguments(Method method, String path) {
        Parameter[] parameters = method.getParameters();
        Object[] args = new Object[parameters.length];

        for (int i = 0; i < parameters.length; i++) {
            Parameter param = parameters[i];

            if (param.isAnnotationPresent(PathVariable.class)) {
                // 경로에서 변수 추출 (예: /api/messages/1 → 1)
                String[] parts = path.split("/");
                args[i] = Long.parseLong(parts[parts.length - 1]);
            } else if (param.isAnnotationPresent(RequestParam.class)) {
                // 쿼리 파라미터 (예시: 하드코딩)
                args[i] = "김철수";
            } else if (param.isAnnotationPresent(RequestBody.class)) {
                // 요청 본문 (예시: 하드코딩)
                args[i] = new SendMessageRequest("박민수", "최지훈", "회의 시간 확인 부탁드립니다");
            }
        }

        return args;
    }
}

public class RestAPIExample {
    public static void main(String[] args) throws Exception {
        System.out.println("=== Spring REST API Controller 예제 ===");
        System.out.println("카카오톡 메시지 API 서버\n");

        MessageController controller = new MessageController();

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 시나리오 1: GET /api/messages - 모든 메시지 조회
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        System.out.println("=".repeat(60));
        System.out.println("시나리오 1: 모든 메시지 조회");
        System.out.println("=".repeat(60) + "\n");

        SimpleWebFramework.handleRequest(controller, "GET", "/api/messages/");

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 시나리오 2: GET /api/messages/1 - 특정 메시지 조회
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        System.out.println("\n" + "=".repeat(60));
        System.out.println("시나리오 2: 특정 메시지 조회 (ID = 1)");
        System.out.println("=".repeat(60) + "\n");

        SimpleWebFramework.handleRequest(controller, "GET", "/api/messages/1");

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 시나리오 3: GET /api/messages/search?sender=김철수
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        System.out.println("\n" + "=".repeat(60));
        System.out.println("시나리오 3: 메시지 검색 (sender = 김철수)");
        System.out.println("=".repeat(60) + "\n");

        SimpleWebFramework.handleRequest(controller, "GET", "/api/messages/search");

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 시나리오 4: POST /api/messages - 새 메시지 전송
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        System.out.println("\n" + "=".repeat(60));
        System.out.println("시나리오 4: 새 메시지 전송");
        System.out.println("=".repeat(60) + "\n");

        SimpleWebFramework.handleRequest(controller, "POST", "/api/messages/");

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // REST API Annotation의 가치
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        System.out.println("\n" + "=".repeat(60));
        System.out.println("\n💡 REST API Annotation의 핵심 가치:");

        System.out.println("\n1️⃣ 선언적 라우팅");
        System.out.println("   - @GetMapping, @PostMapping으로 HTTP 메서드와 경로 지정");
        System.out.println("   - if-else로 라우팅 분기할 필요 없음");
        System.out.println("   - 가독성 극대화");

        System.out.println("\n2️⃣ 자동 파라미터 바인딩");
        System.out.println("   - @PathVariable: URL에서 변수 추출");
        System.out.println("   - @RequestParam: 쿼리 파라미터 추출");
        System.out.println("   - @RequestBody: JSON → Java 객체 자동 변환");
        System.out.println("   - 수동 파싱 코드 불필요");

        System.out.println("\n3️⃣ 자동 응답 변환");
        System.out.println("   - Java 객체를 JSON으로 자동 변환 (Jackson 라이브러리)");
        System.out.println("   - Content-Type 헤더 자동 설정");

        System.out.println("\n4️⃣ HTTP 상태 코드 관리");
        System.out.println("   - @ResponseStatus로 명시적 지정");
        System.out.println("   - 성공: 200 OK, 201 Created");
        System.out.println("   - 오류: 400 Bad Request, 404 Not Found, 500 Internal Server Error");

        System.out.println("\n" + "=".repeat(60));
        System.out.println("\n🌟 실제 Spring Web MVC에서 사용하는 Annotation:");
        System.out.println("  @RestController - REST API 컨트롤러");
        System.out.println("  @RequestMapping - 기본 경로 매핑");
        System.out.println("  @GetMapping - HTTP GET 요청");
        System.out.println("  @PostMapping - HTTP POST 요청");
        System.out.println("  @PutMapping - HTTP PUT 요청");
        System.out.println("  @DeleteMapping - HTTP DELETE 요청");
        System.out.println("  @PatchMapping - HTTP PATCH 요청");
        System.out.println("  @PathVariable - URL 경로 변수");
        System.out.println("  @RequestParam - 쿼리 파라미터");
        System.out.println("  @RequestBody - HTTP 요청 본문");
        System.out.println("  @ResponseStatus - HTTP 상태 코드");
        System.out.println("  @CrossOrigin - CORS 설정");
    }
}
```

**실행 결과:**
```
=== Spring REST API Controller 예제 ===
카카오톡 메시지 API 서버

============================================================
시나리오 1: 모든 메시지 조회
============================================================

📥 [GET] /api/messages - 모든 메시지 조회
✅ 매칭된 핸들러: getAllMessages()

📨 응답:
ApiResponse{success=true, message='메시지 목록 조회 성공', data=[[2025-10-10 09:00:00] 김철수 → 이영희: 안녕하세요!, [2025-10-10 09:01:00] 이영희 → 김철수: 반갑습니다!]}

============================================================
시나리오 2: 특정 메시지 조회 (ID = 1)
============================================================

📥 [GET] /api/messages/1 - 메시지 조회
✅ 매칭된 핸들러: getMessageById()

📨 응답:
ApiResponse{success=true, message='메시지 조회 성공', data=[2025-10-10 09:00:00] 김철수 → 이영희: 안녕하세요!}

============================================================
시나리오 3: 메시지 검색 (sender = 김철수)
============================================================

📥 [GET] /api/messages/search?sender=김철수 - 메시지 검색
✅ 매칭된 핸들러: searchMessages()

📨 응답:
ApiResponse{success=true, message='김철수가 보낸 메시지 1개', data=[[2025-10-10 09:00:00] 김철수 → 이영희: 안녕하세요!]}

============================================================
시나리오 4: 새 메시지 전송
============================================================

📤 [POST] /api/messages - 새 메시지 전송
   요청 본문: 박민수 → 최지훈
✅ 매칭된 핸들러: sendMessage()

📨 응답:
ApiResponse{success=true, message='메시지 전송 성공', data=[2025-10-10 10:00:00] 박민수 → 최지훈: 회의 시간 확인 부탁드립니다}

============================================================

💡 REST API Annotation의 핵심 가치:

1️⃣ 선언적 라우팅
   - @GetMapping, @PostMapping으로 HTTP 메서드와 경로 지정
   - if-else로 라우팅 분기할 필요 없음
   - 가독성 극대화

2️⃣ 자동 파라미터 바인딩
   - @PathVariable: URL에서 변수 추출
   - @RequestParam: 쿼리 파라미터 추출
   - @RequestBody: JSON → Java 객체 자동 변환
   - 수동 파싱 코드 불필요

3️⃣ 자동 응답 변환
   - Java 객체를 JSON으로 자동 변환 (Jackson 라이브러리)
   - Content-Type 헤더 자동 설정

4️⃣ HTTP 상태 코드 관리
   - @ResponseStatus로 명시적 지정
   - 성공: 200 OK, 201 Created
   - 오류: 400 Bad Request, 404 Not Found, 500 Internal Server Error

============================================================

🌟 실제 Spring Web MVC에서 사용하는 Annotation:
  @RestController - REST API 컨트롤러
  @RequestMapping - 기본 경로 매핑
  @GetMapping - HTTP GET 요청
  @PostMapping - HTTP POST 요청
  @PutMapping - HTTP PUT 요청
  @DeleteMapping - HTTP DELETE 요청
  @PatchMapping - HTTP PATCH 요청
  @PathVariable - URL 경로 변수
  @RequestParam - 쿼리 파라미터
  @RequestBody - HTTP 요청 본문
  @ResponseStatus - HTTP 상태 코드
  @CrossOrigin - CORS 설정
```

---

## 👨‍💻 주니어 개발자 시나리오

---

## ❓ Scenario 1: @Override를 생략해서 발생한 오류

### 문제 상황
주니어 개발자가 부모 클래스의 메서드를 오버라이드하려고 했지만, `@Override`를 생략한 채로 메서드 이름에 오타를 냈습니다.

```java
// 📁 OverrideMistake.java

class Animal {
    public void makeSound() {
        System.out.println("동물이 소리를 냅니다");
    }
}

class Dog extends Animal {
    // ❌ 문제: @Override를 생략하고 메서드 이름에 오타
    // 개발자는 makeSound()를 오버라이드하려 했지만 makeSoung()로 오타
    public void makeSoung() {  // 오타: makeSound → makeSoung
        System.out.println("멍멍!");
    }
}

public class OverrideMistake {
    public static void main(String[] args) {
        System.out.println("=== @Override 생략으로 인한 문제 ===\n");

        Dog dog = new Dog();

        // ❌ 기대: "멍멍!" 출력
        // ✅ 실제: "동물이 소리를 냅니다" 출력 (부모 메서드가 호출됨!)
        dog.makeSound();

        System.out.println("\n💡 문제 분석:");
        System.out.println("- makeSoung()는 새로운 메서드로 추가됨 (오버라이드 X)");
        System.out.println("- makeSound()는 여전히 부모의 메서드를 사용");
        System.out.println("- 런타임에서야 문제를 발견할 수 있음");

        System.out.println("\n" + "=".repeat(50));
        System.out.println("\n✅ 올바른 코드:");
        System.out.println("```java");
        System.out.println("class Dog extends Animal {");
        System.out.println("    @Override  // ← 이 어노테이션을 추가!");
        System.out.println("    public void makeSound() {");
        System.out.println("        System.out.println(\"멍멍!\");");
        System.out.println("    }");
        System.out.println("}");
        System.out.println("```");

        System.out.println("\n💡 @Override의 역할:");
        System.out.println("- 컴파일 타임에 오타 발견");
        System.out.println("- makeSoung()에 @Override를 붙이면 컴파일 에러 발생");
        System.out.println("- \"부모에 makeSoung()가 없습니다\" 오류 메시지 표시");
    }
}
```

**실행 결과:**
```
=== @Override 생략으로 인한 문제 ===

동물이 소리를 냅니다

💡 문제 분석:
- makeSoung()는 새로운 메서드로 추가됨 (오버라이드 X)
- makeSound()는 여전히 부모의 메서드를 사용
- 런타임에서야 문제를 발견할 수 있음

==================================================

✅ 올바른 코드:
```java
class Dog extends Animal {
    @Override  // ← 이 어노테이션을 추가!
    public void makeSound() {
        System.out.println("멍멍!");
    }
}
```

💡 @Override의 역할:
- 컴파일 타임에 오타 발견
- makeSoung()에 @Override를 붙이면 컴파일 에러 발생
- "부모에 makeSoung()가 없습니다" 오류 메시지 표시
```

### 해결 방법
**항상 오버라이드 시 `@Override`를 명시**하여 컴파일러가 실수를 잡아주도록 합니다.

---

## ❓ Scenario 2: @Retention을 잘못 설정한 Custom Annotation

### 문제 상황
주니어 개발자가 런타임에 리플렉션으로 처리해야 하는 Annotation에 `@Retention(RetentionPolicy.SOURCE)`를 설정했습니다.

```java
// 📁 RetentionMistake.java

import java.lang.annotation.*;
import java.lang.reflect.Field;

// ❌ 문제: @Retention(SOURCE)로 설정
// 런타임에 리플렉션으로 읽어야 하는데, SOURCE는 컴파일 후 사라짐!
@Retention(RetentionPolicy.SOURCE)  // ← 여기가 문제!
@Target(ElementType.FIELD)
@interface ValidateNotNull {
    String message() default "이 필드는 null이어서는 안 됩니다";
}

class User {
    @ValidateNotNull
    private String username;

    @ValidateNotNull
    private String email;

    public User(String username, String email) {
        this.username = username;
        this.email = email;
    }
}

class Validator {
    public static void validate(Object obj) {
        Class<?> clazz = obj.getClass();

        for (Field field : clazz.getDeclaredFields()) {
            // ❌ @Retention(SOURCE)이므로 런타임에 어노테이션이 없음!
            if (field.isAnnotationPresent(ValidateNotNull.class)) {
                System.out.println("✅ " + field.getName() + "에 @ValidateNotNull 발견");
            } else {
                System.out.println("❌ " + field.getName() + "에 @ValidateNotNull 없음");
            }
        }
    }
}

public class RetentionMistake {
    public static void main(String[] args) {
        System.out.println("=== @Retention 잘못 설정으로 인한 문제 ===\n");

        User user = new User(null, null);

        System.out.println("📋 검증 시도:");
        Validator.validate(user);

        System.out.println("\n💡 문제 분석:");
        System.out.println("- @Retention(SOURCE): 컴파일 후 .class 파일에 포함되지 않음");
        System.out.println("- 런타임에 리플렉션으로 읽을 수 없음");
        System.out.println("- isAnnotationPresent()가 항상 false 반환");

        System.out.println("\n" + "=".repeat(50));
        System.out.println("\n✅ 올바른 코드:");
        System.out.println("```java");
        System.out.println("@Retention(RetentionPolicy.RUNTIME)  // ← RUNTIME으로 변경!");
        System.out.println("@Target(ElementType.FIELD)");
        System.out.println("@interface ValidateNotNull {");
        System.out.println("    String message() default \"...\";");
        System.out.println("}");
        System.out.println("```");

        System.out.println("\n💡 @Retention 정책:");
        System.out.println("- SOURCE: 소스코드에만 유지 (컴파일 후 사라짐)");
        System.out.println("  예: @Override, @SuppressWarnings");
        System.out.println("- CLASS: .class 파일까지 유지 (기본값, 런타임 X)");
        System.out.println("- RUNTIME: 런타임까지 유지 (리플렉션 가능) ✅");
        System.out.println("  예: @Entity, @Autowired, Custom Validation");
    }
}
```

**실행 결과:**
```
=== @Retention 잘못 설정으로 인한 문제 ===

📋 검증 시도:
❌ username에 @ValidateNotNull 없음
❌ email에 @ValidateNotNull 없음

💡 문제 분석:
- @Retention(SOURCE): 컴파일 후 .class 파일에 포함되지 않음
- 런타임에 리플렉션으로 읽을 수 없음
- isAnnotationPresent()가 항상 false 반환

==================================================

✅ 올바른 코드:
```java
@Retention(RetentionPolicy.RUNTIME)  // ← RUNTIME으로 변경!
@Target(ElementType.FIELD)
@interface ValidateNotNull {
    String message() default "...";
}
```

💡 @Retention 정책:
- SOURCE: 소스코드에만 유지 (컴파일 후 사라짐)
  예: @Override, @SuppressWarnings
- CLASS: .class 파일까지 유지 (기본값, 런타임 X)
- RUNTIME: 런타임까지 유지 (리플렉션 가능) ✅
  예: @Entity, @Autowired, Custom Validation
```

### 해결 방법
런타임에 리플렉션으로 처리할 Annotation은 **반드시 `@Retention(RetentionPolicy.RUNTIME)`**으로 설정합니다.

---

## ❓ Scenario 3: @Target을 잘못 설정해서 컴파일 에러

### 문제 상황
메서드에만 적용되어야 하는 Annotation을 클래스에 붙이려고 시도했습니다.

```java
// 📁 TargetMistake.java

import java.lang.annotation.*;

// ✅ @Target을 METHOD로 설정 - 메서드에만 사용 가능
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface Transactional {
}

// ❌ 컴파일 에러 발생!
// @Transactional은 METHOD에만 적용 가능한데 TYPE에 사용
/*
@Transactional  // ← 컴파일 에러!
class UserService {
}
*/

class UserService {

    // ✅ 올바른 사용 - 메서드에 적용
    @Transactional
    public void saveUser() {
        System.out.println("사용자 저장 (트랜잭션 적용)");
    }

    // ❌ 필드에는 적용 불가 (컴파일 에러)
    /*
    @Transactional  // ← 컴파일 에러!
    private String username;
    */
}

public class TargetMistake {
    public static void main(String[] args) {
        System.out.println("=== @Target 잘못 설정으로 인한 컴파일 에러 ===\n");

        UserService service = new UserService();
        service.saveUser();

        System.out.println("\n💡 @Target의 역할:");
        System.out.println("- Annotation을 어디에 적용할 수 있는지 제한");
        System.out.println("- 잘못된 위치에 사용하면 컴파일 에러 발생");

        System.out.println("\n🎯 @Target 옵션:");
        System.out.println("- ElementType.TYPE: 클래스, 인터페이스, enum");
        System.out.println("- ElementType.FIELD: 필드 (멤버 변수)");
        System.out.println("- ElementType.METHOD: 메서드");
        System.out.println("- ElementType.PARAMETER: 메서드 파라미터");
        System.out.println("- ElementType.CONSTRUCTOR: 생성자");
        System.out.println("- ElementType.LOCAL_VARIABLE: 지역 변수");
        System.out.println("- ElementType.ANNOTATION_TYPE: Annotation");
        System.out.println("- ElementType.PACKAGE: 패키지");

        System.out.println("\n✅ 여러 위치에 적용 가능하게 하려면:");
        System.out.println("```java");
        System.out.println("@Target({ElementType.TYPE, ElementType.METHOD})");
        System.out.println("@interface MyAnnotation {");
        System.out.println("}");
        System.out.println("```");
    }
}
```

**실행 결과:**
```
=== @Target 잘못 설정으로 인한 컴파일 에러 ===

사용자 저장 (트랜잭션 적용)

💡 @Target의 역할:
- Annotation을 어디에 적용할 수 있는지 제한
- 잘못된 위치에 사용하면 컴파일 에러 발생

🎯 @Target 옵션:
- ElementType.TYPE: 클래스, 인터페이스, enum
- ElementType.FIELD: 필드 (멤버 변수)
- ElementType.METHOD: 메서드
- ElementType.PARAMETER: 메서드 파라미터
- ElementType.CONSTRUCTOR: 생성자
- ElementType.LOCAL_VARIABLE: 지역 변수
- ElementType.ANNOTATION_TYPE: Annotation
- ElementType.PACKAGE: 패키지

✅ 여러 위치에 적용 가능하게 하려면:
```java
@Target({ElementType.TYPE, ElementType.METHOD})
@interface MyAnnotation {
}
```
```

### 해결 방법
Annotation의 용도에 맞게 **`@Target`을 올바르게 설정**합니다.

---

## ❓ Scenario 4: Reflection 사용 시 주의사항 - 성능 문제

### 문제 상황
주니어 개발자가 Annotation을 처리하기 위해 리플렉션을 과도하게 사용하여 성능 문제가 발생했습니다.

```java
// 📁 ReflectionPerformance.java

import java.lang.annotation.*;
import java.lang.reflect.Field;

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Validate {
}

class User {
    @Validate
    private String username;

    @Validate
    private String email;

    public User(String username, String email) {
        this.username = username;
        this.email = email;
    }
}

class SlowValidator {
    // ❌ 나쁜 예: 매번 리플렉션 수행
    public static void validateSlow(Object obj) {
        Class<?> clazz = obj.getClass();
        for (Field field : clazz.getDeclaredFields()) {  // 매번 호출!
            if (field.isAnnotationPresent(Validate.class)) {
                field.setAccessible(true);
                // 검증 로직...
            }
        }
    }
}

class FastValidator {
    private static final java.util.Map<Class<?>, Field[]> fieldCache = new java.util.HashMap<>();

    // ✅ 좋은 예: 리플렉션 결과를 캐싱
    public static void validateFast(Object obj) {
        Class<?> clazz = obj.getClass();

        // 캐시에서 먼저 찾기
        Field[] fields = fieldCache.get(clazz);
        if (fields == null) {
            fields = clazz.getDeclaredFields();
            fieldCache.put(clazz, fields);  // 캐싱!
        }

        for (Field field : fields) {
            if (field.isAnnotationPresent(Validate.class)) {
                field.setAccessible(true);
                // 검증 로직...
            }
        }
    }
}

public class ReflectionPerformance {
    public static void main(String[] args) {
        System.out.println("=== Reflection 성능 문제 ===\n");

        User user = new User("김철수", "kim@example.com");

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 성능 비교: Slow vs Fast
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        int iterations = 100_000;

        // Slow 방식
        long startSlow = System.nanoTime();
        for (int i = 0; i < iterations; i++) {
            SlowValidator.validateSlow(user);
        }
        long endSlow = System.nanoTime();
        long slowTime = endSlow - startSlow;

        // Fast 방식
        long startFast = System.nanoTime();
        for (int i = 0; i < iterations; i++) {
            FastValidator.validateFast(user);
        }
        long endFast = System.nanoTime();
        long fastTime = endFast - startFast;

        System.out.println("📊 성능 비교 (" + iterations + "회 검증):");
        System.out.println("=".repeat(50));
        System.out.println("❌ Slow (캐싱 없음): " + slowTime / 1_000_000 + "ms");
        System.out.println("✅ Fast (캐싱 적용): " + fastTime / 1_000_000 + "ms");
        System.out.println("\n⚡ 성능 향상: " + (slowTime / fastTime) + "배");

        System.out.println("\n" + "=".repeat(50));
        System.out.println("\n💡 Reflection 최적화 방법:");

        System.out.println("\n1️⃣ 리플렉션 결과 캐싱");
        System.out.println("   - getDeclaredFields(), getMethods() 결과를 Map에 저장");
        System.out.println("   - 같은 클래스는 한 번만 분석");

        System.out.println("\n2️⃣ 애플리케이션 시작 시점에 초기화");
        System.out.println("   - 런타임이 아니라 시작 시 모든 Annotation 분석");
        System.out.println("   - Spring은 ApplicationContext 초기화 시 Bean 분석");

        System.out.println("\n3️⃣ Annotation Processor 사용");
        System.out.println("   - 컴파일 타임에 코드 생성");
        System.out.println("   - 런타임 리플렉션 불필요");
        System.out.println("   - 예: Lombok, Dagger");

        System.out.println("\n4️⃣ MethodHandle 사용 (Java 7+)");
        System.out.println("   - Reflection보다 빠른 메서드 호출");

        System.out.println("\n" + "=".repeat(50));
        System.out.println("\n🎯 주의사항:");
        System.out.println("- Reflection은 편리하지만 느리다");
        System.out.println("- 반복적으로 호출되는 곳에서는 캐싱 필수");
        System.out.println("- 가능하면 Annotation Processor 사용 고려");
    }
}
```

**실행 결과 (예시):**
```
=== Reflection 성능 문제 ===

📊 성능 비교 (100000회 검증):
==================================================
❌ Slow (캐싱 없음): 245ms
✅ Fast (캐싱 적용): 12ms

⚡ 성능 향상: 20배

==================================================

💡 Reflection 최적화 방법:

1️⃣ 리플렉션 결과 캐싱
   - getDeclaredFields(), getMethods() 결과를 Map에 저장
   - 같은 클래스는 한 번만 분석

2️⃣ 애플리케이션 시작 시점에 초기화
   - 런타임이 아니라 시작 시 모든 Annotation 분석
   - Spring은 ApplicationContext 초기화 시 Bean 분석

3️⃣ Annotation Processor 사용
   - 컴파일 타임에 코드 생성
   - 런타임 리플렉션 불필요
   - 예: Lombok, Dagger

4️⃣ MethodHandle 사용 (Java 7+)
   - Reflection보다 빠른 메서드 호출

==================================================

🎯 주의사항:
- Reflection은 편리하지만 느리다
- 반복적으로 호출되는 곳에서는 캐싱 필수
- 가능하면 Annotation Processor 사용 고려
```

### 해결 방법
1. **리플렉션 결과를 캐싱**하여 중복 호출 방지
2. 애플리케이션 시작 시점에 초기화
3. Annotation Processor로 컴파일 타임 코드 생성 고려

---

## 🎓 전체 요약

### 기업 사례 핵심
1. **Spring DI**: `@Component`, `@Autowired`로 의존성 자동 주입
2. **JPA ORM**: `@Entity`, `@Column`으로 DB 자동 매핑
3. **REST API**: `@GetMapping`, `@PostMapping`으로 선언적 라우팅

### 주니어 시나리오 핵심
1. **@Override 생략**: 오타 발견 못함 → 항상 명시
2. **@Retention 실수**: 리플렉션용은 RUNTIME 필수
3. **@Target 오류**: 용도에 맞게 설정
4. **Reflection 성능**: 결과 캐싱 필수

---

**📌 다음 Part 3에서는**
실전 프로젝트로 Custom Annotation 기반 **Validation Framework**를 직접 구축합니다!
