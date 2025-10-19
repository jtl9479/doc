# 11장-2: Spring MVC 개요 - 설정과 실습

> **학습 목표**: Spring MVC 실무 활용 사례를 이해하고, 실전 프로젝트를 통해 CRUD 기능을 구현할 수 있습니다.

**⏱️ 예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐☆☆ (3개/5개)

---

## 📚 목차
- [실무 활용 사례](#실무-활용-사례)
- [주니어 시나리오](#주니어-시나리오)
- [실전 프로젝트](#실전-프로젝트)
- [FAQ](#faq)
- [면접 질문 리스트](#면접-질문-리스트)
- [면접 질문 리스트 답안](#면접-질문-리스트-답안)
- [핵심 정리](#핵심-정리)

---

## 🏢 실무 활용 사례

### 실제 기업 활용 사례

#### 사례 1: 네이버 (Naver)

```bash
# 사용 목적: 대규모 트래픽 처리 웹 서비스
# 규모: 일 방문자 수천만 명
# 효과: 안정적인 서비스 운영, 빠른 기능 개발

# 아키텍처 예시
┌─────────────────────────────────────┐
│         네이버 서비스 구조           │
├─────────────────────────────────────┤
│  Frontend (React/Vue)               │
│         ↕                            │
│  Spring MVC REST API                │
│         ↕                            │
│  Service Layer (비즈니스 로직)       │
│         ↕                            │
│  Data Access (MyBatis/JPA)          │
│         ↕                            │
│  Database (MySQL/Redis)             │
└─────────────────────────────────────┘

# 성과
- 응답 시간: 평균 50ms 이하
- 동시 접속: 100만+ 처리 가능
- 개발 생산성: 신규 API 개발 2-3일
```

#### 사례 2: 배달의민족 (Woowa Brothers)

```bash
# 사용 목적: 주문 처리 및 실시간 상태 관리
# 규모: 월 주문 건수 1억+ 건
# 효과: 안정적인 주문 처리, 빠른 배송 추적

# 구현 예시: 주문 처리 API
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    @Autowired
    private OrderService orderService;

    // 주문 생성
    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(
        @RequestBody @Valid OrderRequest request,
        @AuthenticationPrincipal User user
    ) {
        Order order = orderService.createOrder(user.getId(), request);
        return ResponseEntity.ok(OrderResponse.from(order));
    }

    // 주문 상태 조회
    @GetMapping("/{orderId}/status")
    public ResponseEntity<OrderStatus> getOrderStatus(
        @PathVariable Long orderId
    ) {
        OrderStatus status = orderService.getOrderStatus(orderId);
        return ResponseEntity.ok(status);
    }
}

# 성과
- 주문 처리 시간: 평균 200ms
- 에러율: 0.01% 이하
- 배송 추적 정확도: 99.9%
```

#### 사례 3: 카카오뱅크 (Kakao Bank)

```bash
# 사용 목적: 금융 거래 처리 및 보안
# 규모: 가입자 2천만+ 명
# 효과: 안전한 금융 거래, 24/7 서비스 가능

# 보안 강화 예시
@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf().csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
            .and()
            .authorizeRequests()
                .antMatchers("/api/account/**").authenticated()
                .antMatchers("/api/transfer/**").hasRole("USER")
            .and()
            .sessionManagement()
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS);
        return http.build();
    }
}

# 성과
- 거래 성공률: 99.99%
- 보안 사고: 0건 (2023년 기준)
- 서비스 가용성: 99.95%
```

### 일반적인 활용 패턴

#### 패턴 1: RESTful API 서버

**사용 시기**: SPA(React, Vue) + Backend API 구조

**구현 방법**:

```java
@RestController
@RequestMapping("/api/v1/users")
public class UserApiController {

    @Autowired
    private UserService userService;

    // 사용자 목록 조회 (페이징)
    @GetMapping
    public ResponseEntity<Page<UserDto>> getUsers(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size,
        @RequestParam(required = false) String keyword
    ) {
        Pageable pageable = PageRequest.of(page, size);
        Page<UserDto> users = userService.searchUsers(keyword, pageable);
        return ResponseEntity.ok(users);
    }

    // 사용자 상세 조회
    @GetMapping("/{id}")
    public ResponseEntity<UserDto> getUser(@PathVariable Long id) {
        UserDto user = userService.getUserById(id);
        return ResponseEntity.ok(user);
    }

    // 사용자 생성
    @PostMapping
    public ResponseEntity<UserDto> createUser(
        @RequestBody @Valid UserCreateRequest request
    ) {
        UserDto created = userService.createUser(request);
        URI location = ServletUriComponentsBuilder
            .fromCurrentRequest()
            .path("/{id}")
            .buildAndExpand(created.getId())
            .toUri();
        return ResponseEntity.created(location).body(created);
    }

    // 사용자 수정
    @PutMapping("/{id}")
    public ResponseEntity<UserDto> updateUser(
        @PathVariable Long id,
        @RequestBody @Valid UserUpdateRequest request
    ) {
        UserDto updated = userService.updateUser(id, request);
        return ResponseEntity.ok(updated);
    }

    // 사용자 삭제
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
        return ResponseEntity.noContent().build();
    }
}
```

**실무 주의사항**:
- ⚠️ **버전 관리**: URL에 API 버전 포함 (`/api/v1/`)
- ⚠️ **에러 처리**: 일관된 에러 응답 형식
- ⚠️ **페이징**: 대량 데이터는 반드시 페이징 처리
- ⚠️ **보안**: 인증/인가 적용
- ⚠️ **문서화**: Swagger/Spring REST Docs 사용

#### 패턴 2: 전통적인 웹 애플리케이션 (SSR)

**사용 시기**: SEO가 중요한 콘텐츠 사이트, 관리자 페이지

**구현 방법**:

```java
@Controller
@RequestMapping("/board")
public class BoardController {

    @Autowired
    private BoardService boardService;

    // 게시글 목록
    @GetMapping
    public String list(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(required = false) String keyword,
        Model model
    ) {
        Page<Board> boards = boardService.findAll(page, keyword);
        model.addAttribute("boards", boards);
        model.addAttribute("keyword", keyword);
        return "board/list";
    }

    // 게시글 상세
    @GetMapping("/{id}")
    public String detail(@PathVariable Long id, Model model) {
        Board board = boardService.findById(id);
        boardService.increaseViewCount(id);  // 조회수 증가
        model.addAttribute("board", board);
        return "board/detail";
    }

    // 게시글 작성 폼
    @GetMapping("/write")
    public String writeForm(Model model) {
        model.addAttribute("board", new Board());
        return "board/write";
    }

    // 게시글 작성 처리
    @PostMapping("/write")
    public String write(
        @Valid @ModelAttribute Board board,
        BindingResult result,
        RedirectAttributes redirectAttributes
    ) {
        if (result.hasErrors()) {
            return "board/write";
        }

        Board saved = boardService.save(board);
        redirectAttributes.addFlashAttribute("message", "게시글이 등록되었습니다.");
        return "redirect:/board/" + saved.getId();
    }
}
```

**실무 주의사항**:
- ⚠️ **PRG 패턴**: POST-Redirect-GET 패턴 사용
- ⚠️ **Flash Attribute**: 리다이렉트 시 메시지 전달
- ⚠️ **XSS 방지**: 사용자 입력 이스케이프 처리
- ⚠️ **CSRF 토큰**: Form에 CSRF 토큰 포함

### 성능 비교

| 구분 | 전통적 Servlet | Spring MVC | Spring Boot + MVC |
|------|---------------|------------|-------------------|
| 개발 시간 | 10일 | 5일 | 3일 |
| 코드 라인 | 1000줄 | 400줄 | 300줄 |
| 응답 시간 | 100ms | 80ms | 70ms |
| 유지보수성 | 낮음 | 높음 | 매우 높음 |
| 테스트 용이성 | 어려움 | 보통 | 쉬움 |

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: Controller에 비즈니스 로직 작성

**상황**: 주문 처리 기능을 Controller에 직접 구현

```java
// ❌ 주니어 개발자가 작성한 코드
@Controller
@RequestMapping("/orders")
public class OrderController {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private UserRepository userRepository;

    @PostMapping
    public String createOrder(
        @RequestParam Long userId,
        @RequestParam Long productId,
        @RequestParam int quantity,
        Model model
    ) {
        // ❌ Controller에 비즈니스 로직 직접 작성
        User user = userRepository.findById(userId).orElse(null);
        if (user == null) {
            model.addAttribute("error", "사용자를 찾을 수 없습니다.");
            return "error";
        }

        Product product = productRepository.findById(productId).orElse(null);
        if (product == null) {
            model.addAttribute("error", "상품을 찾을 수 없습니다.");
            return "error";
        }

        // ❌ 재고 확인 로직
        if (product.getStock() < quantity) {
            model.addAttribute("error", "재고가 부족합니다.");
            return "error";
        }

        // ❌ 주문 생성 로직
        Order order = new Order();
        order.setUser(user);
        order.setProduct(product);
        order.setQuantity(quantity);
        order.setTotalPrice(product.getPrice() * quantity);
        order.setStatus("PENDING");
        order.setOrderDate(LocalDateTime.now());

        // ❌ 재고 감소 로직
        product.setStock(product.getStock() - quantity);
        productRepository.save(product);

        orderRepository.save(order);

        model.addAttribute("message", "주문이 완료되었습니다.");
        return "order/success";
    }
}
```

**문제점**:
- **문제 1**: Controller가 비즈니스 로직을 처리하여 단일 책임 원칙 위배
- **문제 2**: 트랜잭션 처리 부재 (재고 감소 실패 시 주문은 생성됨)
- **문제 3**: 테스트 어려움 (웹 계층 없이 비즈니스 로직 테스트 불가)
- **문제 4**: 재사용 불가 (다른 Controller에서 같은 로직 사용 불가)
- **왜 이 문제가 발생하는가**: MVC 패턴의 역할 분리를 이해하지 못함

**해결책**:

```java
// ✅ Service 계층 분리
@Service
@Transactional
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private UserRepository userRepository;

    public Order createOrder(Long userId, Long productId, int quantity) {
        // 사용자 확인
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new UserNotFoundException("사용자를 찾을 수 없습니다."));

        // 상품 확인
        Product product = productRepository.findById(productId)
            .orElseThrow(() -> new ProductNotFoundException("상품을 찾을 수 없습니다."));

        // 재고 확인 및 감소
        if (!product.decreaseStock(quantity)) {
            throw new InsufficientStockException("재고가 부족합니다.");
        }

        // 주문 생성
        Order order = Order.builder()
            .user(user)
            .product(product)
            .quantity(quantity)
            .totalPrice(product.getPrice() * quantity)
            .status(OrderStatus.PENDING)
            .orderDate(LocalDateTime.now())
            .build();

        return orderRepository.save(order);
    }
}

// ✅ Controller는 요청/응답 처리만
@Controller
@RequestMapping("/orders")
public class OrderController {

    @Autowired
    private OrderService orderService;

    @PostMapping
    public String createOrder(
        @RequestParam Long userId,
        @RequestParam Long productId,
        @RequestParam int quantity,
        RedirectAttributes redirectAttributes
    ) {
        try {
            Order order = orderService.createOrder(userId, productId, quantity);
            redirectAttributes.addFlashAttribute("message", "주문이 완료되었습니다.");
            return "redirect:/orders/" + order.getId();
        } catch (UserNotFoundException | ProductNotFoundException e) {
            redirectAttributes.addFlashAttribute("error", e.getMessage());
            return "redirect:/orders/new";
        } catch (InsufficientStockException e) {
            redirectAttributes.addFlashAttribute("error", e.getMessage());
            return "redirect:/products/" + productId;
        }
    }
}
```

**배운 점**:
- 💡 **팁 1**: Controller는 HTTP 요청/응답만 처리
- 💡 **팁 2**: 비즈니스 로직은 Service 계층에 작성
- 💡 **팁 3**: Service에 @Transactional 적용하여 원자성 보장
- 💡 **팁 4**: 예외를 활용한 명확한 에러 처리

### 시나리오 2: @RequestParam vs @ModelAttribute 혼동

**상황**: 회원 가입 폼 데이터를 받아 처리

```java
// ❌ 주니어 개발자가 작성한 코드
@Controller
@RequestMapping("/users")
public class UserController {

    @PostMapping("/register")
    public String register(
        @RequestParam String username,
        @RequestParam String password,
        @RequestParam String email,
        @RequestParam String phone,
        @RequestParam String address,
        @RequestParam String city,
        @RequestParam String zipCode,
        Model model
    ) {
        // 파라미터가 너무 많아서 가독성 저하
        User user = new User();
        user.setUsername(username);
        user.setPassword(password);
        user.setEmail(email);
        user.setPhone(phone);
        user.setAddress(address);
        user.setCity(city);
        user.setZipCode(zipCode);

        userService.save(user);
        return "redirect:/users/login";
    }
}
```

**문제점**:
- **문제 1**: 파라미터가 많아지면 메서드 시그니처가 복잡해짐
- **문제 2**: 데이터 바인딩을 수동으로 처리
- **문제 3**: Validation 적용이 어려움

**해결책**:

```java
// ✅ DTO 객체 사용
@Data
@NoArgsConstructor
public class UserRegisterRequest {

    @NotBlank(message = "사용자명은 필수입니다.")
    @Size(min = 4, max = 20, message = "사용자명은 4-20자여야 합니다.")
    private String username;

    @NotBlank(message = "비밀번호는 필수입니다.")
    @Size(min = 8, message = "비밀번호는 최소 8자 이상이어야 합니다.")
    private String password;

    @NotBlank(message = "이메일은 필수입니다.")
    @Email(message = "올바른 이메일 형식이 아닙니다.")
    private String email;

    @Pattern(regexp = "\\d{3}-\\d{4}-\\d{4}", message = "전화번호 형식이 올바르지 않습니다.")
    private String phone;

    private String address;
    private String city;
    private String zipCode;
}

// ✅ @ModelAttribute 사용
@Controller
@RequestMapping("/users")
public class UserController {

    @Autowired
    private UserService userService;

    @PostMapping("/register")
    public String register(
        @Valid @ModelAttribute UserRegisterRequest request,
        BindingResult result,
        RedirectAttributes redirectAttributes
    ) {
        // Validation 에러 확인
        if (result.hasErrors()) {
            return "users/register";  // 에러와 함께 폼 다시 표시
        }

        try {
            userService.register(request);
            redirectAttributes.addFlashAttribute("message", "회원가입이 완료되었습니다.");
            return "redirect:/users/login";
        } catch (DuplicateUsernameException e) {
            result.rejectValue("username", "duplicate", "이미 사용 중인 사용자명입니다.");
            return "users/register";
        }
    }

    // 회원가입 폼 표시
    @GetMapping("/register")
    public String registerForm(Model model) {
        model.addAttribute("userRegisterRequest", new UserRegisterRequest());
        return "users/register";
    }
}
```

**배운 점**:
- 💡 **팁 1**: 여러 파라미터는 DTO 객체로 묶기
- 💡 **팁 2**: @Valid + BindingResult로 Validation 처리
- 💡 **팁 3**: GET 요청에서 빈 객체 제공하여 Thymeleaf 폼 바인딩
- 💡 **팁 4**: 비즈니스 예외는 BindingResult에 추가

### 시나리오 3: Redirect vs Forward 혼동

**상황**: 폼 제출 후 페이지 이동

```java
// ❌ 주니어 개발자가 작성한 코드
@Controller
@RequestMapping("/posts")
public class PostController {

    @PostMapping
    public String create(@ModelAttribute Post post, Model model) {
        postService.save(post);
        model.addAttribute("message", "게시글이 등록되었습니다.");
        return "posts/success";  // ❌ Forward: URL이 /posts로 유지됨
    }
}
```

**문제점**:
- **문제 1**: 새로고침 시 중복 제출 (F5 누르면 게시글 또 등록됨)
- **문제 2**: URL과 실제 화면이 일치하지 않음 (URL은 /posts, 화면은 success)
- **문제 3**: 메시지가 새로고침 시 사라짐

**해결책**:

```java
// ✅ PRG (Post-Redirect-Get) 패턴 사용
@Controller
@RequestMapping("/posts")
public class PostController {

    @Autowired
    private PostService postService;

    // POST 요청: 게시글 생성
    @PostMapping
    public String create(
        @Valid @ModelAttribute Post post,
        BindingResult result,
        RedirectAttributes redirectAttributes
    ) {
        if (result.hasErrors()) {
            return "posts/form";  // Validation 에러 시 폼으로 Forward
        }

        Post saved = postService.save(post);

        // RedirectAttributes: 리다이렉트 시에도 데이터 전달
        redirectAttributes.addFlashAttribute("message", "게시글이 등록되었습니다.");
        redirectAttributes.addAttribute("id", saved.getId());

        return "redirect:/posts/{id}";  // ✅ Redirect: 새 GET 요청
    }

    // GET 요청: 게시글 상세
    @GetMapping("/{id}")
    public String detail(@PathVariable Long id, Model model) {
        Post post = postService.findById(id);
        model.addAttribute("post", post);
        return "posts/detail";
    }
}
```

**PRG 패턴 흐름**:

```
1. 사용자가 폼 제출 (POST /posts)
   ↓
2. Controller가 데이터 저장
   ↓
3. Redirect 응답 (HTTP 302, Location: /posts/1)
   ↓
4. 브라우저가 새 GET 요청 (GET /posts/1)
   ↓
5. Controller가 상세 페이지 반환
   ↓
6. 사용자가 F5 눌러도 GET 요청만 반복 (중복 제출 방지)
```

**배운 점**:
- 💡 **팁 1**: POST 후에는 항상 Redirect 사용 (PRG 패턴)
- 💡 **팁 2**: RedirectAttributes로 리다이렉트 시 데이터 전달
- 💡 **팁 3**: Validation 에러는 Forward로 폼 다시 표시
- 💡 **팁 4**: Flash Attribute는 1회용 (리다이렉트 후 자동 삭제)

---

## 🛠️ 실전 프로젝트

### 프로젝트: 간단한 게시판 CRUD

**난이도**: ⭐⭐⭐☆☆
**예상 소요 시간**: 2-3시간
**학습 목표**: Spring MVC의 전체 흐름을 이해하고 CRUD 기능을 직접 구현

### 요구사항 분석

#### 기능 요구사항
- [ ] 게시글 목록 조회 (페이징)
- [ ] 게시글 상세 조회
- [ ] 게시글 작성
- [ ] 게시글 수정
- [ ] 게시글 삭제

#### 기술 요구사항
- [ ] Spring MVC 5.x
- [ ] Thymeleaf 템플릿 엔진
- [ ] H2 in-memory database
- [ ] Spring Data JPA

### 프로젝트 구조

```
board-project/
├── src/
│   └── main/
│       ├── java/
│       │   └── com/
│       │       └── example/
│       │           └── board/
│       │               ├── controller/
│       │               │   └── BoardController.java
│       │               ├── service/
│       │               │   ├── BoardService.java
│       │               │   └── BoardServiceImpl.java
│       │               ├── repository/
│       │               │   └── BoardRepository.java
│       │               ├── domain/
│       │               │   └── Board.java
│       │               └── config/
│       │                   └── WebConfig.java
│       └── resources/
│           ├── templates/
│           │   └── board/
│           │       ├── list.html
│           │       ├── detail.html
│           │       └── form.html
│           └── application.yml
└── pom.xml
```

### 단계별 구현 가이드

#### 1단계: 프로젝트 설정

**pom.xml**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.7.14</version>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>board-project</artifactId>
    <version>1.0.0</version>

    <dependencies>
        <!-- Spring Web MVC -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- Thymeleaf -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-thymeleaf</artifactId>
        </dependency>

        <!-- Spring Data JPA -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>

        <!-- H2 Database -->
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>

        <!-- Lombok -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>

        <!-- Validation -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
    </dependencies>
</project>
```

**application.yml**

```yaml
spring:
  datasource:
    url: jdbc:h2:mem:testdb
    driver-class-name: org.h2.Driver
    username: sa
    password:

  h2:
    console:
      enabled: true
      path: /h2-console

  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: true
    properties:
      hibernate:
        format_sql: true

  thymeleaf:
    cache: false
    prefix: classpath:/templates/
    suffix: .html
```

#### 2단계: 도메인 모델 작성

**Board.java**

```java
package com.example.board.domain;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import javax.persistence.*;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;
import java.time.LocalDateTime;

@Entity
@Table(name = "boards")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Board {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank(message = "제목은 필수입니다.")
    @Size(max = 200, message = "제목은 200자 이내여야 합니다.")
    @Column(nullable = false, length = 200)
    private String title;

    @NotBlank(message = "작성자는 필수입니다.")
    @Size(max = 50, message = "작성자는 50자 이내여야 합니다.")
    @Column(nullable = false, length = 50)
    private String author;

    @NotBlank(message = "내용은 필수입니다.")
    @Lob
    @Column(nullable = false)
    private String content;

    @Column(nullable = false)
    @Builder.Default
    private Integer viewCount = 0;

    @CreationTimestamp
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(nullable = false)
    private LocalDateTime updatedAt;

    // 조회수 증가
    public void increaseViewCount() {
        this.viewCount++;
    }
}
```

#### 3단계: Repository 작성

**BoardRepository.java**

```java
package com.example.board.repository;

import com.example.board.domain.Board;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface BoardRepository extends JpaRepository<Board, Long> {

    // 제목으로 검색 (페이징)
    Page<Board> findByTitleContaining(String keyword, Pageable pageable);

    // 작성자로 검색 (페이징)
    Page<Board> findByAuthorContaining(String author, Pageable pageable);

    // 제목 또는 내용으로 검색 (페이징)
    @Query("SELECT b FROM Board b WHERE b.title LIKE %:keyword% OR b.content LIKE %:keyword%")
    Page<Board> searchByKeyword(@Param("keyword") String keyword, Pageable pageable);
}
```

#### 4단계: Service 작성

**BoardService.java**

```java
package com.example.board.service;

import com.example.board.domain.Board;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

public interface BoardService {
    Page<Board> findAll(Pageable pageable);
    Page<Board> search(String keyword, Pageable pageable);
    Board findById(Long id);
    Board save(Board board);
    Board update(Long id, Board board);
    void delete(Long id);
    void increaseViewCount(Long id);
}
```

**BoardServiceImpl.java**

```java
package com.example.board.service;

import com.example.board.domain.Board;
import com.example.board.repository.BoardRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class BoardServiceImpl implements BoardService {

    private final BoardRepository boardRepository;

    @Override
    public Page<Board> findAll(Pageable pageable) {
        return boardRepository.findAll(pageable);
    }

    @Override
    public Page<Board> search(String keyword, Pageable pageable) {
        if (keyword == null || keyword.trim().isEmpty()) {
            return findAll(pageable);
        }
        return boardRepository.searchByKeyword(keyword, pageable);
    }

    @Override
    public Board findById(Long id) {
        return boardRepository.findById(id)
            .orElseThrow(() -> new IllegalArgumentException("게시글을 찾을 수 없습니다: " + id));
    }

    @Override
    @Transactional
    public Board save(Board board) {
        return boardRepository.save(board);
    }

    @Override
    @Transactional
    public Board update(Long id, Board board) {
        Board existing = findById(id);
        existing.setTitle(board.getTitle());
        existing.setContent(board.getContent());
        return existing;  // 변경 감지(Dirty Checking)로 자동 업데이트
    }

    @Override
    @Transactional
    public void delete(Long id) {
        Board board = findById(id);
        boardRepository.delete(board);
    }

    @Override
    @Transactional
    public void increaseViewCount(Long id) {
        Board board = findById(id);
        board.increaseViewCount();
    }
}
```

#### 5단계: Controller 작성

**BoardController.java**

```java
package com.example.board.controller;

import com.example.board.domain.Board;
import com.example.board.service.BoardService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import javax.validation.Valid;

@Controller
@RequestMapping("/board")
@RequiredArgsConstructor
public class BoardController {

    private final BoardService boardService;

    // 게시글 목록
    @GetMapping
    public String list(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size,
        @RequestParam(required = false) String keyword,
        Model model
    ) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        Page<Board> boards = boardService.search(keyword, pageable);

        model.addAttribute("boards", boards);
        model.addAttribute("keyword", keyword);
        model.addAttribute("currentPage", page);

        return "board/list";
    }

    // 게시글 상세
    @GetMapping("/{id}")
    public String detail(@PathVariable Long id, Model model) {
        Board board = boardService.findById(id);
        boardService.increaseViewCount(id);  // 조회수 증가
        model.addAttribute("board", board);
        return "board/detail";
    }

    // 게시글 작성 폼
    @GetMapping("/new")
    public String newForm(Model model) {
        model.addAttribute("board", new Board());
        return "board/form";
    }

    // 게시글 작성 처리
    @PostMapping
    public String create(
        @Valid @ModelAttribute Board board,
        BindingResult result,
        RedirectAttributes redirectAttributes
    ) {
        if (result.hasErrors()) {
            return "board/form";
        }

        Board saved = boardService.save(board);
        redirectAttributes.addFlashAttribute("message", "게시글이 등록되었습니다.");
        return "redirect:/board/" + saved.getId();
    }

    // 게시글 수정 폼
    @GetMapping("/{id}/edit")
    public String editForm(@PathVariable Long id, Model model) {
        Board board = boardService.findById(id);
        model.addAttribute("board", board);
        return "board/form";
    }

    // 게시글 수정 처리
    @PostMapping("/{id}")
    public String update(
        @PathVariable Long id,
        @Valid @ModelAttribute Board board,
        BindingResult result,
        RedirectAttributes redirectAttributes
    ) {
        if (result.hasErrors()) {
            board.setId(id);  // ID 설정 (폼에 전달하기 위해)
            return "board/form";
        }

        boardService.update(id, board);
        redirectAttributes.addFlashAttribute("message", "게시글이 수정되었습니다.");
        return "redirect:/board/" + id;
    }

    // 게시글 삭제
    @PostMapping("/{id}/delete")
    public String delete(@PathVariable Long id, RedirectAttributes redirectAttributes) {
        boardService.delete(id);
        redirectAttributes.addFlashAttribute("message", "게시글이 삭제되었습니다.");
        return "redirect:/board";
    }
}
```

#### 6단계: View 작성 (Thymeleaf)

**list.html** (게시글 목록)

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>게시판</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #4CAF50; color: white; }
        tr:hover { background-color: #f5f5f5; }
        .btn { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn:hover { background-color: #45a049; }
        .pagination { margin-top: 20px; text-align: center; }
        .pagination a { padding: 8px 16px; text-decoration: none; color: #4CAF50; margin: 0 4px; border: 1px solid #ddd; }
        .pagination a.active { background-color: #4CAF50; color: white; }
        .search-form { margin: 20px 0; }
        .search-form input { padding: 10px; width: 300px; }
        .message { padding: 10px; background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>게시판</h1>

    <!-- 메시지 표시 -->
    <div th:if="${message}" class="message" th:text="${message}"></div>

    <!-- 검색 폼 -->
    <form class="search-form" method="get" th:action="@{/board}">
        <input type="text" name="keyword" th:value="${keyword}" placeholder="제목 또는 내용 검색">
        <button type="submit" class="btn">검색</button>
        <a th:href="@{/board}" class="btn">전체보기</a>
    </form>

    <!-- 글쓰기 버튼 -->
    <div style="text-align: right; margin-bottom: 10px;">
        <a th:href="@{/board/new}" class="btn">글쓰기</a>
    </div>

    <!-- 게시글 목록 -->
    <table>
        <thead>
            <tr>
                <th style="width: 10%;">번호</th>
                <th style="width: 45%;">제목</th>
                <th style="width: 15%;">작성자</th>
                <th style="width: 10%;">조회수</th>
                <th style="width: 20%;">작성일</th>
            </tr>
        </thead>
        <tbody>
            <tr th:each="board : ${boards.content}">
                <td th:text="${board.id}">1</td>
                <td>
                    <a th:href="@{/board/{id}(id=${board.id})}" th:text="${board.title}">제목</a>
                </td>
                <td th:text="${board.author}">작성자</td>
                <td th:text="${board.viewCount}">0</td>
                <td th:text="${#temporals.format(board.createdAt, 'yyyy-MM-dd HH:mm')}">2024-01-01</td>
            </tr>
            <tr th:if="${boards.empty}">
                <td colspan="5" style="text-align: center;">게시글이 없습니다.</td>
            </tr>
        </tbody>
    </table>

    <!-- 페이징 -->
    <div class="pagination" th:if="${boards.totalPages > 0}">
        <!-- 이전 페이지 -->
        <a th:if="${boards.hasPrevious()}"
           th:href="@{/board(page=${boards.number - 1}, keyword=${keyword})}">이전</a>

        <!-- 페이지 번호 -->
        <span th:each="i : ${#numbers.sequence(0, boards.totalPages - 1)}">
            <a th:href="@{/board(page=${i}, keyword=${keyword})}"
               th:text="${i + 1}"
               th:classappend="${i == boards.number} ? 'active'">1</a>
        </span>

        <!-- 다음 페이지 -->
        <a th:if="${boards.hasNext()}"
           th:href="@{/board(page=${boards.number + 1}, keyword=${keyword})}">다음</a>
    </div>
</body>
</html>
```

**detail.html** (게시글 상세)

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title th:text="${board.title}">게시글 상세</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .board-detail { border: 1px solid #ddd; padding: 20px; }
        .board-header { border-bottom: 2px solid #4CAF50; padding-bottom: 10px; margin-bottom: 20px; }
        .board-title { font-size: 24px; font-weight: bold; margin-bottom: 10px; }
        .board-info { color: #666; font-size: 14px; }
        .board-content { line-height: 1.6; min-height: 200px; padding: 20px 0; white-space: pre-wrap; }
        .board-footer { margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; }
        .btn { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; cursor: pointer; text-decoration: none; display: inline-block; margin-right: 10px; }
        .btn:hover { background-color: #45a049; }
        .btn-secondary { background-color: #666; }
        .btn-danger { background-color: #f44336; }
    </style>
</head>
<body>
    <div class="board-detail">
        <div class="board-header">
            <div class="board-title" th:text="${board.title}">제목</div>
            <div class="board-info">
                <span>작성자: <strong th:text="${board.author}">작성자</strong></span> |
                <span>조회수: <strong th:text="${board.viewCount}">0</strong></span> |
                <span>작성일: <strong th:text="${#temporals.format(board.createdAt, 'yyyy-MM-dd HH:mm')}">2024-01-01</strong></span>
            </div>
        </div>

        <div class="board-content" th:text="${board.content}">
            내용
        </div>

        <div class="board-footer">
            <a th:href="@{/board}" class="btn btn-secondary">목록</a>
            <a th:href="@{/board/{id}/edit(id=${board.id})}" class="btn">수정</a>
            <form th:action="@{/board/{id}/delete(id=${board.id})}" method="post" style="display: inline;"
                  onsubmit="return confirm('정말 삭제하시겠습니까?');">
                <button type="submit" class="btn btn-danger">삭제</button>
            </form>
        </div>
    </div>
</body>
</html>
```

**form.html** (게시글 작성/수정 폼)

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title th:text="${board.id != null} ? '게시글 수정' : '게시글 작성'">게시글 작성</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #333; }
        form { margin-top: 20px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], textarea { width: 100%; padding: 10px; border: 1px solid #ddd; box-sizing: border-box; }
        textarea { min-height: 300px; resize: vertical; }
        .error { color: red; font-size: 14px; margin-top: 5px; }
        .btn { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; cursor: pointer; margin-right: 10px; }
        .btn:hover { background-color: #45a049; }
        .btn-secondary { background-color: #666; }
    </style>
</head>
<body>
    <h1 th:text="${board.id != null} ? '게시글 수정' : '게시글 작성'">게시글 작성</h1>

    <form th:action="${board.id != null} ? @{/board/{id}(id=${board.id})} : @{/board}"
          th:object="${board}" method="post">

        <div class="form-group">
            <label for="title">제목</label>
            <input type="text" id="title" th:field="*{title}" placeholder="제목을 입력하세요">
            <div class="error" th:if="${#fields.hasErrors('title')}" th:errors="*{title}">제목 에러</div>
        </div>

        <div class="form-group">
            <label for="author">작성자</label>
            <input type="text" id="author" th:field="*{author}" placeholder="작성자를 입력하세요"
                   th:readonly="${board.id != null}">
            <div class="error" th:if="${#fields.hasErrors('author')}" th:errors="*{author}">작성자 에러</div>
        </div>

        <div class="form-group">
            <label for="content">내용</label>
            <textarea id="content" th:field="*{content}" placeholder="내용을 입력하세요"></textarea>
            <div class="error" th:if="${#fields.hasErrors('content')}" th:errors="*{content}">내용 에러</div>
        </div>

        <div>
            <button type="submit" class="btn" th:text="${board.id != null} ? '수정' : '등록'">등록</button>
            <a th:href="@{/board}" class="btn btn-secondary">취소</a>
        </div>
    </form>
</body>
</html>
```

#### 7단계: 실행 및 검증

**Application.java**

```java
package com.example.board;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class BoardApplication {
    public static void main(String[] args) {
        SpringApplication.run(BoardApplication.class, args);
    }
}
```

**실행**

```bash
# Maven으로 실행
mvn spring-boot:run

# 또는 Java로 실행
mvn clean package
java -jar target/board-project-1.0.0.jar
```

**접속**

```
게시판: http://localhost:8080/board
H2 Console: http://localhost:8080/h2-console
```

**테스트 시나리오**

1. **게시글 작성**
   - http://localhost:8080/board/new 접속
   - 제목, 작성자, 내용 입력
   - "등록" 버튼 클릭
   - 상세 페이지로 리다이렉트 확인

2. **게시글 목록 조회**
   - http://localhost:8080/board 접속
   - 작성한 게시글 확인
   - 페이징 동작 확인

3. **게시글 수정**
   - 게시글 상세에서 "수정" 버튼 클릭
   - 내용 수정 후 "수정" 버튼 클릭
   - 변경사항 확인

4. **게시글 삭제**
   - 게시글 상세에서 "삭제" 버튼 클릭
   - 확인 대화상자에서 "확인" 클릭
   - 목록에서 삭제 확인

5. **검색 기능**
   - 검색어 입력 후 "검색" 버튼
   - 결과 확인

### 트러블슈팅

#### 문제 1: 404 Not Found

**증상**:
```
Whitelabel Error Page
This application has no explicit mapping for /error
```

**원인**: Controller 매핑 경로 오류

**해결 방법**:
```java
// URL 확인: http://localhost:8080/board (맨 뒤 슬래시 없음)
@GetMapping  // "/board/"가 아닌 "/board"로 매핑됨
public String list() { ... }
```

#### 문제 2: Validation 동작 안 함

**증상**: @NotBlank 등의 Validation이 동작하지 않음

**원인**: spring-boot-starter-validation 의존성 누락

**해결 방법**:
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

#### 문제 3: Thymeleaf 템플릿을 찾을 수 없음

**증상**:
```
org.thymeleaf.exceptions.TemplateInputException: Error resolving template "board/list"
```

**원인**: 템플릿 파일 위치 오류

**해결 방법**:
```
정확한 경로: src/main/resources/templates/board/list.html
Controller 반환값: "board/list"
```

---

## ❓ FAQ

<details>
<summary><strong>Q1: DispatcherServlet은 언제 초기화되나요?</strong></summary>

**A**: DispatcherServlet은 웹 애플리케이션 시작 시 또는 첫 번째 요청 시 초기화됩니다.

**상세 설명**:
- **즉시 로딩(Eager Loading)**: `load-on-startup` 설정 시 애플리케이션 시작 시 초기화
- **지연 로딩(Lazy Loading)**: 설정하지 않으면 첫 번째 요청 시 초기화

**Spring Boot에서는**:
```java
// 자동으로 즉시 로딩 설정됨
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
// DispatcherServlet이 애플리케이션 시작 시 자동 초기화됨
```

**전통적인 web.xml에서는**:
```xml
<servlet>
    <servlet-name>dispatcher</servlet-name>
    <servlet-class>org.springframework.web.servlet.DispatcherServlet</servlet-class>
    <load-on-startup>1</load-on-startup> <!-- 1: 즉시 로딩 -->
</servlet>
```

**실무 팁**:
💡 즉시 로딩 권장 - 첫 번째 사용자가 느린 응답을 경험하지 않도록

</details>

<details>
<summary><strong>Q2: @Controller vs @RestController 차이는 무엇인가요?</strong></summary>

**A**: @Controller는 View를 반환하고, @RestController는 데이터(JSON)를 반환합니다.

**상세 설명**:

**@Controller**:
```java
@Controller
public class HomeController {
    @GetMapping("/home")
    public String home(Model model) {
        model.addAttribute("message", "Hello");
        return "home";  // ✅ View 이름 반환 → home.jsp 렌더링
    }
}
```

**@RestController**:
```java
@RestController  // = @Controller + @ResponseBody
public class ApiController {
    @GetMapping("/api/home")
    public Map<String, String> home() {
        return Map.of("message", "Hello");  // ✅ JSON 반환: {"message":"Hello"}
    }
}
```

**비교표**:

| 특징 | @Controller | @RestController |
|------|------------|----------------|
| 반환 타입 | View 이름 (String) | 데이터 (Object) |
| 응답 형식 | HTML | JSON/XML |
| @ResponseBody | 메서드마다 필요 | 자동 적용 |
| 사용 사례 | 전통적 웹 (SSR) | RESTful API |

**실무 팁**:
💡 SPA(React/Vue) 백엔드라면 @RestController 사용
💡 SEO가 중요하면 @Controller로 SSR 구현

</details>

<details>
<summary><strong>Q3: Model vs ModelAndView는 어떻게 다른가요?</strong></summary>

**A**: Model은 데이터만 담고, ModelAndView는 데이터와 View 이름을 모두 담습니다.

**상세 설명**:

**Model 사용**:
```java
@Controller
public class UserController {
    @GetMapping("/users")
    public String list(Model model) {
        model.addAttribute("users", userService.findAll());
        return "users/list";  // View 이름은 별도로 반환
    }
}
```

**ModelAndView 사용**:
```java
@Controller
public class UserController {
    @GetMapping("/users")
    public ModelAndView list() {
        ModelAndView mav = new ModelAndView();
        mav.addObject("users", userService.findAll());  // 데이터 추가
        mav.setViewName("users/list");  // View 이름 설정
        return mav;  // 하나의 객체로 반환
    }
}
```

**비교표**:

| 특징 | Model | ModelAndView |
|------|-------|--------------|
| 데이터 저장 | ✅ | ✅ |
| View 이름 설정 | ❌ (별도 반환) | ✅ |
| 반환 타입 | String | ModelAndView |
| 코드 간결성 | 높음 | 낮음 |

**실무 팁**:
💡 최신 Spring에서는 Model + String 반환을 권장 (간결함)
💡 ModelAndView는 레거시 코드에서 주로 보임

</details>

<details>
<summary><strong>Q4: HandlerMapping은 어떻게 URL을 매칭하나요?</strong></summary>

**A**: @RequestMapping 어노테이션을 스캔하여 URL 패턴과 Controller 메서드를 매핑합니다.

**상세 설명**:

**매핑 우선순위**:
1. **정확한 경로 매핑**
2. **패턴 매칭** (와일드카드)
3. **확장자 매칭**

**예시**:
```java
@Controller
@RequestMapping("/products")
public class ProductController {

    // 1. 정확한 경로: /products/list
    @GetMapping("/list")
    public String list() { ... }

    // 2. 경로 변수: /products/123
    @GetMapping("/{id}")
    public String detail(@PathVariable Long id) { ... }

    // 3. 와일드카드: /products/images/logo.png
    @GetMapping("/images/**")
    public String images() { ... }

    // 4. 확장자: /products/download.pdf
    @GetMapping("/download.*")
    public String download() { ... }
}
```

**매칭 순서**:
```
요청: GET /products/list

1. RequestMappingHandlerMapping이 모든 @RequestMapping 스캔
2. URL 패턴 매칭: "/products" + "/list" = "/products/list"
3. HTTP 메서드 확인: GET ✅
4. 매칭된 메서드 반환: ProductController.list()
```

**실무 팁**:
💡 명확한 경로가 우선순위가 높음
💡 /**는 모든 하위 경로 매칭 (/*는 1단계만)

</details>

<details>
<summary><strong>Q5: Spring MVC에서 예외는 어떻게 처리하나요?</strong></summary>

**A**: @ExceptionHandler, @ControllerAdvice를 사용하여 전역 또는 개별 예외를 처리합니다.

**상세 설명**:

**방법 1: Controller 내에서 처리**
```java
@Controller
public class UserController {

    @GetMapping("/users/{id}")
    public String getUser(@PathVariable Long id, Model model) {
        User user = userService.findById(id);  // 예외 발생 가능
        model.addAttribute("user", user);
        return "users/detail";
    }

    // 이 Controller에서 발생한 UserNotFoundException 처리
    @ExceptionHandler(UserNotFoundException.class)
    public String handleUserNotFound(UserNotFoundException ex, Model model) {
        model.addAttribute("error", ex.getMessage());
        return "error/404";
    }
}
```

**방법 2: 전역 예외 처리 (@ControllerAdvice)**
```java
@ControllerAdvice  // 모든 Controller에 적용
public class GlobalExceptionHandler {

    // UserNotFoundException을 전역으로 처리
    @ExceptionHandler(UserNotFoundException.class)
    public String handleUserNotFound(UserNotFoundException ex, Model model) {
        model.addAttribute("error", ex.getMessage());
        return "error/404";
    }

    // 모든 예외를 처리
    @ExceptionHandler(Exception.class)
    public String handleException(Exception ex, Model model) {
        model.addAttribute("error", "서버 오류가 발생했습니다.");
        return "error/500";
    }

    // REST API용 예외 처리
    @ExceptionHandler(UserNotFoundException.class)
    @ResponseBody
    public ResponseEntity<ErrorResponse> handleUserNotFoundApi(UserNotFoundException ex) {
        ErrorResponse error = new ErrorResponse(404, ex.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
}
```

**방법 3: ResponseStatusException (Spring 5+)**
```java
@Controller
public class UserController {

    @GetMapping("/users/{id}")
    public String getUser(@PathVariable Long id, Model model) {
        User user = userService.findById(id)
            .orElseThrow(() -> new ResponseStatusException(
                HttpStatus.NOT_FOUND, "사용자를 찾을 수 없습니다."
            ));
        model.addAttribute("user", user);
        return "users/detail";
    }
}
```

**실무 팁**:
💡 @ControllerAdvice로 전역 예외 처리 권장
💡 비즈니스 예외는 커스텀 Exception 생성
💡 로깅 추가하여 예외 추적

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. Spring MVC의 동작 흐름을 설명해주세요.</strong></summary>

**모범 답안 포인트**
- DispatcherServlet이 모든 요청의 진입점
- HandlerMapping이 URL과 Controller 매핑
- Controller가 비즈니스 로직 실행
- ViewResolver가 View 결정
- View가 렌더링하여 응답

**예시 답변**
> "Spring MVC는 Front Controller 패턴을 사용합니다. 먼저 DispatcherServlet이 모든 HTTP 요청을 받습니다. 그 다음 HandlerMapping이 URL에 매핑된 Controller를 찾아줍니다. Controller는 Service를 호출하여 비즈니스 로직을 처리하고, 결과 데이터를 Model에 담아 View 이름과 함께 반환합니다. ViewResolver가 논리적 View 이름을 실제 JSP나 Thymeleaf 파일로 변환하고, 마지막으로 View가 Model 데이터를 사용하여 HTML을 생성해 사용자에게 응답합니다."

**꼬리 질문**
- Q: "DispatcherServlet은 어떻게 모든 요청을 받나요?"
- A: "web.xml이나 Java Config에서 url-pattern을 '/'로 설정하여 모든 요청을 DispatcherServlet이 처리하도록 매핑합니다."

**실무 연관**
- 이 흐름을 이해하면 디버깅 시 어느 계층에서 문제가 발생했는지 파악 가능

</details>

<details>
<summary><strong>2. @RequestMapping과 @GetMapping의 차이는 무엇인가요?</strong></summary>

**모범 답안 포인트**
- @RequestMapping은 모든 HTTP 메서드 처리 가능
- @GetMapping은 GET 요청만 처리 (축약형)
- @GetMapping = @RequestMapping(method = RequestMethod.GET)

**예시 답변**
> "@RequestMapping은 기본적으로 모든 HTTP 메서드(GET, POST, PUT, DELETE 등)를 처리할 수 있는 범용 어노테이션입니다. @GetMapping은 GET 요청만 처리하는 축약형으로, @RequestMapping(method = RequestMethod.GET)과 동일합니다. Spring 4.3부터 @GetMapping, @PostMapping 등의 특화된 어노테이션이 추가되어 코드 가독성이 향상되었습니다."

**꼬리 질문**
- Q: "왜 @GetMapping을 사용하는 게 좋을까요?"
- A: "코드가 더 간결하고 명확해지며, HTTP 메서드를 명시적으로 표현하여 RESTful API 설계 의도를 분명히 할 수 있습니다."

</details>

<details>
<summary><strong>3. Model, ModelMap, ModelAndView의 차이를 설명해주세요.</strong></summary>

**모범 답안 포인트**
- Model: 인터페이스, 데이터만 저장
- ModelMap: Map 구현체, 데이터만 저장
- ModelAndView: 데이터 + View 이름 저장

**예시 답변**
> "세 가지 모두 Controller에서 View로 데이터를 전달하는 역할을 합니다. Model은 인터페이스로 가장 간단하게 데이터를 저장할 수 있습니다. ModelMap은 Map을 구현한 클래스로 Model보다 더 많은 메서드를 제공합니다. ModelAndView는 데이터뿐만 아니라 View 이름도 함께 저장할 수 있어, 하나의 객체로 데이터와 화면 정보를 함께 반환할 수 있습니다. 최근에는 Model + String 반환 방식이 더 간결하여 주로 사용됩니다."

</details>

<details>
<summary><strong>4. @PathVariable과 @RequestParam의 차이는 무엇인가요?</strong></summary>

**모범 답안 포인트**
- @PathVariable: URL 경로의 일부를 변수로 추출
- @RequestParam: 쿼리 파라미터(?key=value) 추출
- RESTful API에서는 @PathVariable 선호

**예시 답변**
> "@PathVariable은 URL 경로의 일부분을 변수로 추출합니다. 예를 들어 /users/{id}에서 {id} 부분을 가져옵니다. @RequestParam은 쿼리 파라미터, 즉 ?name=John 형태의 데이터를 추출합니다. RESTful API 설계에서는 리소스 식별자는 @PathVariable로, 필터나 옵션은 @RequestParam으로 받는 것이 일반적입니다."

**예시 코드**:
```java
// @PathVariable: /users/123
@GetMapping("/users/{id}")
public String getUser(@PathVariable Long id) { ... }

// @RequestParam: /users?name=John&age=25
@GetMapping("/users")
public String searchUsers(
    @RequestParam String name,
    @RequestParam int age
) { ... }
```

</details>

<details>
<summary><strong>5. PRG (Post-Redirect-Get) 패턴이 무엇인가요?</strong></summary>

**모범 답안 포인트**
- POST 요청 처리 후 Redirect로 GET 요청 유도
- 중복 제출 방지
- 사용자 경험 향상

**예시 답변**
> "PRG 패턴은 POST 요청을 처리한 후 Redirect를 통해 GET 요청으로 유도하는 패턴입니다. 사용자가 폼을 제출(POST)하면 서버는 데이터를 처리한 후 302 Redirect 응답을 보내고, 브라우저는 자동으로 새로운 GET 요청을 보냅니다. 이렇게 하면 사용자가 F5(새로고침)를 눌러도 GET 요청만 반복되므로 중복 제출을 방지할 수 있습니다."

**실무 활용**:
```java
@PostMapping("/orders")
public String create(@ModelAttribute Order order, RedirectAttributes attrs) {
    Order saved = orderService.save(order);
    attrs.addFlashAttribute("message", "주문 완료");
    return "redirect:/orders/" + saved.getId();  // ✅ Redirect
}
```

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. DispatcherServlet의 초기화 과정을 상세히 설명해주세요.</strong></summary>

**모범 답안 포인트**
- WebApplicationContext 생성 및 초기화
- HandlerMapping, HandlerAdapter 등 전략 객체 초기화
- 기본 전략 vs 커스텀 전략

**예시 답변**
> "DispatcherServlet이 초기화될 때 먼저 WebApplicationContext를 생성합니다. 이 컨텍스트는 Root ApplicationContext를 부모로 가지며 웹 관련 빈들을 관리합니다. 그 다음 initStrategies() 메서드를 통해 HandlerMapping, HandlerAdapter, ViewResolver 등의 전략 객체들을 초기화합니다. 만약 사용자가 명시적으로 설정하지 않으면 DispatcherServlet.properties 파일에 정의된 기본 전략을 사용합니다. 예를 들어 RequestMappingHandlerMapping과 RequestMappingHandlerAdapter가 기본으로 등록됩니다."

**내부 구조**:
```java
protected void initStrategies(ApplicationContext context) {
    initMultipartResolver(context);
    initLocaleResolver(context);
    initThemeResolver(context);
    initHandlerMappings(context);
    initHandlerAdapters(context);
    initHandlerExceptionResolvers(context);
    initRequestToViewNameTranslator(context);
    initViewResolvers(context);
    initFlashMapManager(context);
}
```

</details>

<details>
<summary><strong>2. HandlerInterceptor와 Filter의 차이는 무엇인가요?</strong></summary>

**모범 답안 포인트**
- Filter: Servlet 레벨, Spring 컨텍스트 외부
- Interceptor: Spring MVC 레벨, 컨텍스트 내부
- 실행 시점과 접근 가능한 정보의 차이

**예시 답변**
> "Filter는 Servlet 스펙에 정의된 기능으로 Spring 컨텍스트 외부에서 동작합니다. 따라서 DispatcherServlet이 실행되기 전후에 작동하며, 모든 HTTP 요청에 적용할 수 있습니다. 반면 Interceptor는 Spring MVC의 구성 요소로 DispatcherServlet 내부에서 동작합니다. Controller 실행 전후, View 렌더링 전후에 작동하며, Spring Bean을 주입받아 사용할 수 있습니다. 인증/인가는 Filter로, 로깅이나 공통 Model 설정은 Interceptor로 처리하는 것이 일반적입니다."

**실행 순서**:
```
Request
  → Filter (before)
    → DispatcherServlet
      → Interceptor.preHandle()
        → Controller
      → Interceptor.postHandle()
      → View 렌더링
      → Interceptor.afterCompletion()
  → Filter (after)
Response
```

</details>

<details>
<summary><strong>3. ArgumentResolver는 무엇이며 어떻게 동작하나요?</strong></summary>

**모범 답안 포인트**
- Controller 메서드 파라미터를 자동으로 바인딩
- HandlerMethodArgumentResolver 인터페이스
- 커스텀 ArgumentResolver 구현 가능

**예시 답변**
> "ArgumentResolver는 Controller 메서드의 파라미터를 자동으로 바인딩해주는 역할을 합니다. 예를 들어 @RequestParam, @PathVariable, @RequestBody 등의 어노테이션이 붙은 파라미터를 HTTP 요청에서 추출하여 메서드 인자로 전달합니다. Spring은 30개 이상의 기본 ArgumentResolver를 제공하며, HandlerMethodArgumentResolver 인터페이스를 구현하여 커스텀 Resolver를 만들 수 있습니다. 실무에서는 인증된 사용자 정보를 자동으로 주입하는 @AuthUser 같은 커스텀 어노테이션을 만들 때 활용합니다."

**커스텀 예시**:
```java
// 커스텀 어노테이션
@Target(ElementType.PARAMETER)
@Retention(RetentionPolicy.RUNTIME)
public @interface CurrentUser {}

// ArgumentResolver 구현
public class CurrentUserArgumentResolver implements HandlerMethodArgumentResolver {
    @Override
    public boolean supportsParameter(MethodParameter parameter) {
        return parameter.hasParameterAnnotation(CurrentUser.class);
    }

    @Override
    public Object resolveArgument(...) {
        // 세션에서 사용자 정보 추출
        return getCurrentUserFromSession();
    }
}

// Controller에서 사용
@GetMapping("/profile")
public String profile(@CurrentUser User user) {
    // user 객체가 자동으로 주입됨
    return "profile";
}
```

</details>

---

## 💼 면접 질문 리스트 답안

### 📘 주니어/신입 개발자용 답안

#### Q1. Spring MVC의 동작 흐름을 설명해주세요.

**완벽한 답변 예시**:
```
"Spring MVC는 Front Controller 패턴을 기반으로 동작합니다.

1. 먼저 클라이언트의 모든 HTTP 요청은 DispatcherServlet으로 집중됩니다.
   DispatcherServlet은 Spring MVC의 중앙 처리기로서 단일 진입점 역할을 합니다.

2. DispatcherServlet은 HandlerMapping에게 요청 URL에 매핑된 Controller를 찾아달라고 요청합니다.
   HandlerMapping은 @RequestMapping 어노테이션 정보를 스캔하여 적절한 Controller를 반환합니다.

3. DispatcherServlet은 HandlerAdapter를 통해 실제 Controller 메서드를 실행합니다.
   이 과정에서 파라미터 바인딩, Validation 등이 수행됩니다.

4. Controller는 Service 계층을 호출하여 비즈니스 로직을 처리하고,
   결과 데이터를 Model에 담아 View 이름과 함께 ModelAndView 형태로 반환합니다.

5. DispatcherServlet은 ViewResolver에게 논리적 View 이름(예: "home")을
   실제 View 파일(예: "/WEB-INF/views/home.jsp")로 변환해달라고 요청합니다.

6. View는 Model에 담긴 데이터를 사용하여 최종 HTML을 렌더링합니다.

7. 마지막으로 DispatcherServlet은 렌더링된 HTML을 HTTP 응답으로 클라이언트에게 전송합니다.

이러한 구조 덕분에 개발자는 비즈니스 로직에만 집중할 수 있고,
HTTP 요청/응답 처리는 프레임워크가 자동으로 처리해줍니다."
```

**답변 구조 분석**:
1. **도입부 (10초)**: Front Controller 패턴 언급
2. **본론 (30초)**: 7단계 흐름을 순서대로 설명
3. **마무리 (10초)**: 장점 언급

**더 좋은 답변을 위한 추가 포인트**:
- ✅ 구체적인 클래스명 언급 (DispatcherServlet, HandlerMapping)
- ✅ 각 단계의 역할 명확히 구분
- ✅ 마지막에 이점 언급하여 이해도 표현

**피해야 할 답변 실수**:
- ❌ "요청이 들어오면 처리됩니다" 같은 추상적 표현
- ❌ 순서 뒤바뀜 (ViewResolver → Controller 순서로 설명)
- ❌ 용어 혼동 (Handler와 Controller를 다른 것처럼 설명)

**꼬리 질문 대응**:
- Q: "DispatcherServlet은 어떻게 모든 요청을 받나요?"
  - A: "web.xml이나 WebApplicationInitializer에서 url-pattern을 '/'로 설정하여 모든 요청을 DispatcherServlet으로 매핑합니다. Spring Boot에서는 자동 설정으로 이것이 처리됩니다."

---

#### Q2. @Controller와 @RestController의 차이는 무엇인가요?

**완벽한 답변 예시**:
```
"두 어노테이션 모두 웹 요청을 처리하는 Controller를 정의하지만, 응답 방식이 다릅니다.

@Controller는 전통적인 Spring MVC Controller로,
메서드가 View 이름(String)을 반환하면 ViewResolver가 실제 View 파일을 찾아 렌더링합니다.
주로 서버 사이드 렌더링(SSR)이 필요한 경우 사용합니다.
예를 들어 JSP나 Thymeleaf로 HTML을 생성하는 경우입니다.

@RestController는 @Controller와 @ResponseBody를 합친 것으로,
메서드의 반환값이 그대로 HTTP 응답 본문(Body)에 작성됩니다.
기본적으로 JSON 형태로 변환되며, RESTful API 서버를 만들 때 사용합니다.
SPA(React, Vue) 프론트엔드와 통신하는 백엔드 API에 적합합니다.

실무에서는 관리자 페이지처럼 SEO가 필요하면 @Controller를,
모바일 앱이나 SPA 백엔드라면 @RestController를 선택합니다."
```

**코드 예시로 보강**:
```java
// @Controller 예시
@Controller
public class PageController {
    @GetMapping("/home")
    public String home(Model model) {
        model.addAttribute("message", "Hello");
        return "home";  // → home.jsp 렌더링
    }
}

// @RestController 예시
@RestController
public class ApiController {
    @GetMapping("/api/home")
    public Map<String, String> home() {
        return Map.of("message", "Hello");  // → {"message":"Hello"} JSON 반환
    }
}
```

---

## 📝 핵심 정리

### 이 장에서 배운 핵심 개념

| 개념 | 설명 | 핵심 포인트 |
|------|------|------------|
| 실무 활용 | 네이버, 배민, 카카오뱅크의 Spring MVC 사용 사례 | RESTful API, SSR, 보안 |
| 레이어 분리 | Controller-Service-Repository 패턴 | 단일 책임, 테스트 용이성 |
| PRG 패턴 | Post-Redirect-Get 패턴으로 중복 제출 방지 | RedirectAttributes |
| DTO 활용 | @ModelAttribute로 폼 데이터 바인딩 | Validation, 가독성 향상 |
| 예외 처리 | @ControllerAdvice로 전역 예외 처리 | 일관된 에러 응답 |

### 실무 체크리스트

#### ✅ 해야 할 것
- [ ] Controller에서 비즈니스 로직 분리 (Service 계층 사용)
- [ ] POST 후 Redirect 사용 (PRG 패턴)
- [ ] DTO 객체로 파라미터 그룹화
- [ ] @Valid + BindingResult로 Validation
- [ ] @ControllerAdvice로 전역 예외 처리
- [ ] RESTful URL 설계 (/users/{id}, /posts/new)

#### ❌ 하지 말아야 할 것
- [ ] Controller에 DB 접근 로직 작성
- [ ] Forward로 POST 결과 표시
- [ ] 모든 요청을 GET으로 처리
- [ ] @RequestParam으로 10개 이상 파라미터 받기
- [ ] try-catch로 개별 예외 처리

---

## 🚀 다음 단계

### 다음 장 미리보기: 12장-1: 컨트롤러와 요청 매핑 - 기본

**배울 내용:**
- **요청 매핑 고급 기법**: 정규표현식, Ant 패턴, 매트릭스 변수
- **Content Negotiation**: JSON, XML 자동 변환
- **파라미터 바인딩**: @RequestBody, @ResponseBody, HttpEntity
- **파일 업로드**: MultipartFile 처리
- **실전 프로젝트**: 파일 업로드 게시판

### 준비하면 좋을 것들

```bash
# Jackson 라이브러리 (JSON 처리)
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
</dependency>

# Apache Commons FileUpload (파일 업로드)
<dependency>
    <groupId>commons-fileupload</groupId>
    <artifactId>commons-fileupload</artifactId>
    <version>1.4</version>
</dependency>
```

---

**다음 장으로 이동**: [다음: 12장-1: 컨트롤러와 요청 매핑 - 기본 →](SpringMVC-Part3-12-1-Controller-Basic.md)

**이전 장으로 돌아가기**: [← 이전: 11장-1: 기본 개념](SpringMVC-Part1-11-1-Overview-Concept.md)

**목차로 돌아가기**: [📚 전체 목차](README.md)
