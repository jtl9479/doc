# 12장-1: 컨트롤러와 요청 매핑 - 기본

> **학습 목표**: @RequestMapping의 다양한 속성을 이해하고, HTTP 메서드별 요청 매핑 및 파라미터 바인딩을 구현할 수 있습니다.

**⏱️ 예상 학습 시간**: 2-3시간
**난이도**: ⭐⭐⭐☆☆ (3개/5개)

---

## 📚 목차
- [왜 이 기술이 필요한가](#왜-이-기술이-필요한가)
- [실생활 비유로 이해하기](#실생활-비유로-이해하기)
- [핵심 개념](#핵심-개념)
- [기본 실습](#기본-실습)
- [핵심 정리](#핵심-정리)
- [다음 단계](#다음-단계)

---

## 🤔 왜 이 기술이 필요한가?

### 실무 배경
**RESTful API와 복잡한 URL 구조를 효율적으로 처리해야 하는 상황**

현대 웹 애플리케이션은 다음과 같은 다양한 URL 패턴을 처리해야 합니다:
- `/users/123` - 특정 사용자 조회
- `/api/v1/products?category=laptop&sort=price` - 검색 및 필터링
- `/orders/2024/01/15` - 날짜별 주문 조회
- `/files/download/report.pdf` - 파일 다운로드

#### ❌ 요청 매핑을 모르면 발생하는 문제

```
문제 1: 비효율적인 URL 처리
- 증상: if-else로 URL 파싱
- 영향: 코드 복잡도 증가, 유지보수 어려움
- 비용: URL 하나 추가에 30분 소요

문제 2: HTTP 메서드 구분 못함
- 증상: GET/POST 모두 같은 메서드 처리
- 영향: RESTful 원칙 위반, API 설계 혼란
- 비용: API 재설계로 1주일 소요

문제 3: 파라미터 처리 중복
- 증상: request.getParameter() 반복 호출
- 영향: 타입 변환 에러, Null 체크 누락
- 비용: 버그 수정에 2시간 소요
```

#### ✅ 요청 매핑을 사용하면

```
해결책 1: 선언적 URL 매핑
- 방법: @GetMapping("/users/{id}")
- 효과: 간결한 코드, 명확한 의도
- 절감: 개발 시간 80% 단축

해결책 2: HTTP 메서드 자동 구분
- 방법: @GetMapping, @PostMapping 등
- 효과: RESTful API 자동 구현
- 절감: API 설계 시간 70% 단축

해결책 3: 자동 파라미터 바인딩
- 방법: @PathVariable, @RequestParam
- 효과: 타입 안전, Null 처리 자동화
- 절감: 버그 발생률 90% 감소
```

### 📊 수치로 보는 효과

| 지표 | Servlet 직접 사용 | Spring MVC 매핑 | 개선율 |
|------|------------------|----------------|--------|
| URL 추가 시간 | 30분 | 5분 | **83%↓** |
| 코드 라인 수 | 50줄 | 10줄 | **80%↓** |
| 파라미터 에러 | 15% | 1% | **93%↓** |
| API 설계 시간 | 1주일 | 2일 | **71%↓** |

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 전화 교환원 시스템

```
@RequestMapping = 전화 교환원 시스템

고객이 전화 (HTTP 요청)
    ↓
교환원이 번호 확인 (URL 매핑)
    ↓
해당 부서로 연결 (Controller 메서드)

┌─────────────────────────────────────┐
│          회사 전화 시스템             │
│                                      │
│  1번: 영업부 (GET /sales)            │
│  2번: 고객센터 (GET /support)         │
│  3번: 기술지원 (GET /tech)            │
│  0번: 총무부 (GET /admin)            │
│                                      │
│  * 누르면 교환원 (DispatcherServlet)  │
└─────────────────────────────────────┘

@GetMapping("/sales")  // 1번 누르면
public String sales() {
    return "영업부입니다";
}

@GetMapping("/support")  // 2번 누르면
public String support() {
    return "고객센터입니다";
}
```

### 비유 2: 우편 배달 시스템

```
URL 매핑 = 우편물 주소 체계

주소 형식:
- /users/{id}        → 서울시 강남구 123번지 (고정 주소 + 번지)
- /products?page=2   → 부산시 + 2동 (주소 + 상세 정보)
- /api/v1/orders     → 대한민국 + 서울 + 강남구 + ... (계층 구조)

┌────────────────────────────────────┐
│         우편 배달 규칙              │
│                                     │
│  대한민국 (/)                        │
│   ├─ 서울시 (/users)                │
│   │   ├─ 강남구 (/users/123)        │
│   │   └─ 서초구 (/users/456)        │
│   └─ 부산시 (/products)             │
│       └─ 해운대 (/products/789)     │
└────────────────────────────────────┘

배달 규칙:
- @GetMapping: 우편물 받기
- @PostMapping: 등기 보내기
- @PutMapping: 주소 변경
- @DeleteMapping: 우편함 제거
```

### 비유 3: 식당 주문 시스템

```
HTTP 메서드 = 식당 주문 종류

GET    = 메뉴판 보기 (조회만)
POST   = 주문하기 (새로 생성)
PUT    = 주문 전체 변경 (다시 주문)
PATCH  = 주문 일부 변경 (맵빠 추가)
DELETE = 주문 취소 (삭제)

┌─────────────────────────────────┐
│         식당 주문 흐름           │
└─────────────────────────────────┘

손님: "메뉴판 주세요"
→ GET /menu
→ 서버: 메뉴판 보여줌 (데이터 조회)

손님: "짜장면 1개 주세요"
→ POST /orders { item: "짜장면", qty: 1 }
→ 서버: 주문 생성

손님: "짜장면을 짬뽕으로 바꿔주세요"
→ PUT /orders/123 { item: "짬뽕", qty: 1 }
→ 서버: 주문 전체 교체

손님: "짬뽕에 곱빼기로 해주세요"
→ PATCH /orders/123 { size: "large" }
→ 서버: 주문 일부 수정

손님: "주문 취소할게요"
→ DELETE /orders/123
→ 서버: 주문 삭제
```

### 비유 4: 음식 배달 앱 (라이더 배정)

```
@RequestMapping = 배달 앱 주문 처리 시스템

고객 주문 (HTTP Request)
    ↓
배달 앱 서버 (DispatcherServlet)
    ↓
주문 분류 (URL 매핑)
    ↓
라이더 배정 (Controller)
    ↓
픽업 & 배달 (Service)

┌─────────────────────────────────────┐
│         배달 앱 시스템               │
│                                      │
│  주문 타입별 처리:                   │
│  - 일반 배달: /orders/normal         │
│  - 빠른 배달: /orders/express        │
│  - 예약 배달: /orders/scheduled      │
│                                      │
│  지역별 라이더 자동 매칭:            │
│  - /orders?location=gangnam          │
│  → 강남 근처 라이더에게 배정         │
└─────────────────────────────────────┘

@GetMapping("/orders/{orderId}")
public String trackOrder(@PathVariable Long orderId) {
    // 주문 추적
}

@PostMapping("/orders")
public String createOrder(
    @RequestParam String location,
    @RequestParam String items
) {
    // 주문 생성 및 라이더 배정
}
```

### 비유 5: 도서관 대출 시스템

```
URL 매핑 = 도서관 자료 검색 및 대출

사서 (DispatcherServlet)
    ↓
분류 번호 확인 (URL 패턴)
    ↓
해당 서가로 안내 (Controller)

┌─────────────────────────────────────┐
│         도서관 분류 시스템           │
│                                      │
│  /books/{isbn}                       │
│  → 특정 도서 정보 (GET)              │
│                                      │
│  /books?category=science&available=true│
│  → 과학 분야 대출 가능 도서 검색     │
│                                      │
│  /books/{isbn}/borrow                │
│  → 도서 대출 (POST)                  │
│                                      │
│  /books/{isbn}/return                │
│  → 도서 반납 (POST)                  │
└─────────────────────────────────────┘

특징:
- ISBN(경로 변수)로 정확한 도서 식별
- 쿼리 파라미터로 다양한 검색 조건
- HTTP 메서드로 행위 구분 (조회/대출/반납)
```

### 🎯 종합 비교표

```
┌──────────────┬──────────┬──────────┬──────────┬──────────┐
│ 매핑 개념     │ 전화     │ 우편     │ 식당     │ 배달앱   │
├──────────────┼──────────┼──────────┼──────────┼──────────┤
│ URL          │ 전화번호 │ 주소     │ 메뉴     │ 주문정보 │
│ Controller   │ 담당부서 │ 수신인   │ 주방     │ 라이더   │
│ GET          │ 문의전화 │ 우편받기 │ 메뉴보기 │ 추적     │
│ POST         │ 주문전화 │ 등기발송 │ 주문하기 │ 주문생성 │
│ Parameter    │ 내선번호 │ 동/호수  │ 옵션     │ 위치     │
└──────────────┴──────────┴──────────┴──────────┴──────────┘
```

---

## 📖 핵심 개념

### @RequestMapping 속성

#### 1️⃣ value / path - URL 매핑

**기본 사용법**:

```java
@Controller
@RequestMapping("/users")  // 클래스 레벨: 기본 경로
public class UserController {

    // 메서드 레벨: /users + /list = /users/list
    @RequestMapping("/list")
    public String list() {
        return "users/list";
    }

    // 여러 URL을 하나의 메서드에 매핑
    @RequestMapping({"/", "/index", "/home"})
    public String home() {
        return "home";
    }

    // value 생략 가능 (첫 번째 속성일 경우)
    @RequestMapping("detail")  // value= 생략
    public String detail() {
        return "users/detail";
    }
}
```

**경로 패턴**:

```java
@Controller
public class PatternController {

    // ? : 한 글자 매칭
    // /user1, /user2 → 매칭
    // /user12 → 매칭 안 됨
    @GetMapping("/user?")
    public String singleChar() { return "user"; }

    // * : 0개 이상의 문자 매칭 (한 경로 내)
    // /users/list, /users/search → 매칭
    // /users/admin/list → 매칭 안 됨 (/ 포함)
    @GetMapping("/users/*")
    public String anyChars() { return "users"; }

    // ** : 0개 이상의 경로 매칭
    // /files/a, /files/a/b, /files/a/b/c → 모두 매칭
    @GetMapping("/files/**")
    public String anyPaths() { return "files"; }

    // 확장자 패턴
    // /download.pdf, /download.doc → 매칭
    @GetMapping("/download.*")
    public String anyExtension() { return "download"; }

    // 복합 패턴
    // /2024/01/report.pdf → 매칭
    @GetMapping("/{year}/{month}/*.pdf")
    public String complexPattern(
        @PathVariable int year,
        @PathVariable int month
    ) {
        return "report";
    }
}
```

#### 2️⃣ method - HTTP 메서드 지정

**방법 1: method 속성 사용**

```java
@Controller
@RequestMapping("/api/products")
public class ProductController {

    // GET 요청만 처리
    @RequestMapping(value = "/list", method = RequestMethod.GET)
    public String list() {
        return "products/list";
    }

    // POST 요청만 처리
    @RequestMapping(value = "/create", method = RequestMethod.POST)
    public String create() {
        return "redirect:/api/products/list";
    }

    // 여러 HTTP 메서드 허용
    @RequestMapping(
        value = "/search",
        method = {RequestMethod.GET, RequestMethod.POST}
    )
    public String search() {
        return "products/search";
    }
}
```

**방법 2: 축약 어노테이션 사용 (Spring 4.3+)**

```java
@Controller
@RequestMapping("/api/posts")
public class PostController {

    @GetMapping("/list")           // = @RequestMapping(method = GET)
    public String list() { return "posts/list"; }

    @PostMapping("/create")        // = @RequestMapping(method = POST)
    public String create() { return "redirect:/api/posts"; }

    @PutMapping("/{id}")           // = @RequestMapping(method = PUT)
    public String update(@PathVariable Long id) { return "redirect:/api/posts"; }

    @PatchMapping("/{id}/status")  // = @RequestMapping(method = PATCH)
    public String updateStatus(@PathVariable Long id) { return "redirect:/api/posts"; }

    @DeleteMapping("/{id}")        // = @RequestMapping(method = DELETE)
    public String delete(@PathVariable Long id) { return "redirect:/api/posts"; }
}
```

**RESTful 설계 예시**:

```java
@RestController
@RequestMapping("/api/v1/books")
public class BookApiController {

    @Autowired
    private BookService bookService;

    // GET /api/v1/books - 전체 조회
    @GetMapping
    public List<Book> getAll() {
        return bookService.findAll();
    }

    // GET /api/v1/books/123 - 단건 조회
    @GetMapping("/{id}")
    public Book getOne(@PathVariable Long id) {
        return bookService.findById(id);
    }

    // POST /api/v1/books - 생성
    @PostMapping
    public Book create(@RequestBody Book book) {
        return bookService.save(book);
    }

    // PUT /api/v1/books/123 - 전체 수정
    @PutMapping("/{id}")
    public Book update(@PathVariable Long id, @RequestBody Book book) {
        return bookService.update(id, book);
    }

    // PATCH /api/v1/books/123 - 부분 수정
    @PatchMapping("/{id}")
    public Book partialUpdate(@PathVariable Long id, @RequestBody Map<String, Object> updates) {
        return bookService.partialUpdate(id, updates);
    }

    // DELETE /api/v1/books/123 - 삭제
    @DeleteMapping("/{id}")
    public void delete(@PathVariable Long id) {
        bookService.delete(id);
    }
}
```

#### 3️⃣ params - 특정 파라미터 조건

**기본 사용법**:

```java
@Controller
@RequestMapping("/search")
public class SearchController {

    // ?type=user 파라미터가 있어야 매칭
    @GetMapping(params = "type=user")
    public String searchUser() {
        return "search/user";
    }

    // ?type=product 파라미터가 있어야 매칭
    @GetMapping(params = "type=product")
    public String searchProduct() {
        return "search/product";
    }

    // keyword 파라미터가 존재하면 매칭
    @GetMapping(params = "keyword")
    public String searchWithKeyword() {
        return "search/keyword";
    }

    // mode 파라미터가 없어야 매칭
    @GetMapping(params = "!mode")
    public String searchWithoutMode() {
        return "search/default";
    }

    // 여러 조건
    @GetMapping(params = {"type=advanced", "sort"})
    public String advancedSearch() {
        return "search/advanced";
    }
}
```

**실무 활용**:

```java
@Controller
@RequestMapping("/products")
public class ProductController {

    // /products?action=view → 조회
    @GetMapping(params = "action=view")
    public String view(@RequestParam Long id, Model model) {
        Product product = productService.findById(id);
        model.addAttribute("product", product);
        return "products/view";
    }

    // /products?action=edit → 수정 폼
    @GetMapping(params = "action=edit")
    public String editForm(@RequestParam Long id, Model model) {
        Product product = productService.findById(id);
        model.addAttribute("product", product);
        return "products/edit";
    }

    // /products?action=delete → 삭제 확인
    @GetMapping(params = "action=delete")
    public String deleteConfirm(@RequestParam Long id, Model model) {
        model.addAttribute("id", id);
        return "products/delete-confirm";
    }
}
```

#### 4️⃣ headers - HTTP 헤더 조건

```java
@Controller
public class HeaderController {

    // Content-Type이 application/json인 요청만 처리
    @PostMapping(value = "/api/data", headers = "Content-Type=application/json")
    public String jsonData() {
        return "json";
    }

    // 특정 헤더가 존재하는 경우
    @GetMapping(value = "/secure", headers = "X-API-KEY")
    public String secure() {
        return "secure";
    }

    // 헤더 값이 특정 조건을 만족하는 경우
    @GetMapping(value = "/mobile", headers = "User-Agent=Mobile")
    public String mobile() {
        return "mobile";
    }

    // 여러 헤더 조건
    @PostMapping(
        value = "/api/upload",
        headers = {"Content-Type=multipart/form-data", "X-Upload-Token"}
    )
    public String upload() {
        return "upload";
    }
}
```

#### 5️⃣ consumes - Content-Type 지정

```java
@RestController
@RequestMapping("/api")
public class ContentTypeController {

    // JSON 데이터만 처리
    @PostMapping(value = "/json", consumes = "application/json")
    public String handleJson(@RequestBody Map<String, Object> data) {
        return "JSON received";
    }

    // XML 데이터만 처리
    @PostMapping(value = "/xml", consumes = "application/xml")
    public String handleXml(@RequestBody String xmlData) {
        return "XML received";
    }

    // Form 데이터만 처리
    @PostMapping(value = "/form", consumes = "application/x-www-form-urlencoded")
    public String handleForm(@RequestParam String name) {
        return "Form received";
    }

    // 파일 업로드
    @PostMapping(value = "/upload", consumes = "multipart/form-data")
    public String handleUpload(@RequestParam("file") MultipartFile file) {
        return "File received";
    }

    // 여러 Content-Type 허용
    @PostMapping(
        value = "/data",
        consumes = {"application/json", "application/xml"}
    )
    public String handleMultiple() {
        return "Data received";
    }
}
```

#### 6️⃣ produces - Accept 지정 (응답 형식)

```java
@RestController
@RequestMapping("/api/users")
public class ResponseTypeController {

    // JSON 응답
    @GetMapping(value = "/{id}", produces = "application/json")
    public User getUserJson(@PathVariable Long id) {
        return userService.findById(id);
    }

    // XML 응답
    @GetMapping(value = "/{id}", produces = "application/xml")
    public User getUserXml(@PathVariable Long id) {
        return userService.findById(id);
    }

    // Plain Text 응답
    @GetMapping(value = "/name/{id}", produces = "text/plain")
    public String getUserName(@PathVariable Long id) {
        return userService.findById(id).getName();
    }

    // 이미지 응답
    @GetMapping(value = "/profile-image/{id}", produces = "image/jpeg")
    public byte[] getProfileImage(@PathVariable Long id) {
        return userService.getProfileImage(id);
    }

    // 클라이언트 Accept 헤더에 따라 자동 선택
    @GetMapping(
        value = "/{id}",
        produces = {"application/json", "application/xml"}
    )
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
        // Accept: application/json → JSON 반환
        // Accept: application/xml → XML 반환
    }
}
```

---

## 💻 기본 실습

### 실습 1: HTTP 메서드별 CRUD 구현

**난이도**: ⭐⭐☆☆☆

```java
@RestController
@RequestMapping("/api/v1/users")
public class UserRestController {

    private final Map<Long, User> users = new ConcurrentHashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(1);

    // DTO 클래스
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    static class User {
        private Long id;
        private String username;
        private String email;
        private int age;
    }

    // 1. GET - 전체 조회
    @GetMapping
    public ResponseEntity<List<User>> getAllUsers() {
        List<User> userList = new ArrayList<>(users.values());
        return ResponseEntity.ok(userList);
    }

    // 2. GET - 단건 조회
    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        User user = users.get(id);
        if (user == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(user);
    }

    // 3. POST - 생성
    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody User user) {
        Long id = idGenerator.getAndIncrement();
        user.setId(id);
        users.put(id, user);

        URI location = ServletUriComponentsBuilder
            .fromCurrentRequest()
            .path("/{id}")
            .buildAndExpand(id)
            .toUri();

        return ResponseEntity.created(location).body(user);
    }

    // 4. PUT - 전체 수정
    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(
        @PathVariable Long id,
        @RequestBody User user
    ) {
        if (!users.containsKey(id)) {
            return ResponseEntity.notFound().build();
        }

        user.setId(id);
        users.put(id, user);
        return ResponseEntity.ok(user);
    }

    // 5. PATCH - 부분 수정
    @PatchMapping("/{id}")
    public ResponseEntity<User> partialUpdateUser(
        @PathVariable Long id,
        @RequestBody Map<String, Object> updates
    ) {
        User user = users.get(id);
        if (user == null) {
            return ResponseEntity.notFound().build();
        }

        // 제공된 필드만 업데이트
        if (updates.containsKey("username")) {
            user.setUsername((String) updates.get("username"));
        }
        if (updates.containsKey("email")) {
            user.setEmail((String) updates.get("email"));
        }
        if (updates.containsKey("age")) {
            user.setAge((Integer) updates.get("age"));
        }

        users.put(id, user);
        return ResponseEntity.ok(user);
    }

    // 6. DELETE - 삭제
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        if (!users.containsKey(id)) {
            return ResponseEntity.notFound().build();
        }

        users.remove(id);
        return ResponseEntity.noContent().build();
    }

    // 7. GET - 검색 (쿼리 파라미터)
    @GetMapping("/search")
    public ResponseEntity<List<User>> searchUsers(
        @RequestParam(required = false) String username,
        @RequestParam(required = false) Integer minAge,
        @RequestParam(required = false) Integer maxAge
    ) {
        List<User> result = users.values().stream()
            .filter(u -> username == null || u.getUsername().contains(username))
            .filter(u -> minAge == null || u.getAge() >= minAge)
            .filter(u -> maxAge == null || u.getAge() <= maxAge)
            .collect(Collectors.toList());

        return ResponseEntity.ok(result);
    }
}
```

**테스트 (Postman/cURL)**:

```bash
# 1. 사용자 생성 (POST)
curl -X POST http://localhost:8080/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","age":25}'

# 응답: 201 Created
# Location: http://localhost:8080/api/v1/users/1
# Body: {"id":1,"username":"john","email":"john@example.com","age":25}

# 2. 전체 조회 (GET)
curl http://localhost:8080/api/v1/users

# 응답: 200 OK
# [{"id":1,"username":"john","email":"john@example.com","age":25}]

# 3. 단건 조회 (GET)
curl http://localhost:8080/api/v1/users/1

# 응답: 200 OK
# {"id":1,"username":"john","email":"john@example.com","age":25}

# 4. 전체 수정 (PUT)
curl -X PUT http://localhost:8080/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{"username":"john_updated","email":"new@example.com","age":26}'

# 응답: 200 OK
# {"id":1,"username":"john_updated","email":"new@example.com","age":26}

# 5. 부분 수정 (PATCH)
curl -X PATCH http://localhost:8080/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{"age":27}'

# 응답: 200 OK
# {"id":1,"username":"john_updated","email":"new@example.com","age":27}

# 6. 검색 (GET with Query Parameters)
curl "http://localhost:8080/api/v1/users/search?username=john&minAge=20&maxAge=30"

# 응답: 200 OK
# [{"id":1,"username":"john_updated","email":"new@example.com","age":27}]

# 7. 삭제 (DELETE)
curl -X DELETE http://localhost:8080/api/v1/users/1

# 응답: 204 No Content
```

### 실습 2: 경로 변수와 쿼리 파라미터 조합

**난이도**: ⭐⭐⭐☆☆

```java
@RestController
@RequestMapping("/api/v1/posts")
public class PostController {

    // 경로 변수 1개
    // GET /api/v1/posts/123
    @GetMapping("/{id}")
    public ResponseEntity<Post> getPost(@PathVariable Long id) {
        Post post = postService.findById(id);
        return ResponseEntity.ok(post);
    }

    // 경로 변수 2개
    // GET /api/v1/posts/2024/10
    @GetMapping("/{year}/{month}")
    public ResponseEntity<List<Post>> getPostsByMonth(
        @PathVariable int year,
        @PathVariable int month
    ) {
        List<Post> posts = postService.findByYearAndMonth(year, month);
        return ResponseEntity.ok(posts);
    }

    // 경로 변수 + 쿼리 파라미터
    // GET /api/v1/posts/123/comments?page=2&size=10
    @GetMapping("/{postId}/comments")
    public ResponseEntity<Page<Comment>> getComments(
        @PathVariable Long postId,
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size
    ) {
        Pageable pageable = PageRequest.of(page, size);
        Page<Comment> comments = commentService.findByPostId(postId, pageable);
        return ResponseEntity.ok(comments);
    }

    // 경로 변수 이름 명시
    // GET /api/v1/posts/user-123
    @GetMapping("/user-{userId}")
    public ResponseEntity<List<Post>> getPostsByUser(
        @PathVariable("userId") Long id  // 변수명과 경로 변수명이 다를 때
    ) {
        List<Post> posts = postService.findByUserId(id);
        return ResponseEntity.ok(posts);
    }

    // 정규표현식 사용
    // GET /api/v1/posts/2024-10-15 (날짜 형식만 매칭)
    @GetMapping("/{date:\\d{4}-\\d{2}-\\d{2}}")
    public ResponseEntity<List<Post>> getPostsByDate(
        @PathVariable String date
    ) {
        LocalDate localDate = LocalDate.parse(date);
        List<Post> posts = postService.findByDate(localDate);
        return ResponseEntity.ok(posts);
    }

    // Optional 파라미터
    // GET /api/v1/posts/search?keyword=spring&category=tech&sort=latest
    @GetMapping("/search")
    public ResponseEntity<List<Post>> search(
        @RequestParam(required = false) String keyword,
        @RequestParam(required = false) String category,
        @RequestParam(defaultValue = "latest") String sort,
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size
    ) {
        SearchCriteria criteria = SearchCriteria.builder()
            .keyword(keyword)
            .category(category)
            .sort(sort)
            .page(page)
            .size(size)
            .build();

        List<Post> posts = postService.search(criteria);
        return ResponseEntity.ok(posts);
    }

    // List 파라미터
    // GET /api/v1/posts/bulk?ids=1,2,3
    @GetMapping("/bulk")
    public ResponseEntity<List<Post>> bulkGet(
        @RequestParam List<Long> ids
    ) {
        List<Post> posts = postService.findByIds(ids);
        return ResponseEntity.ok(posts);
    }

    // Map 파라미터
    // GET /api/v1/posts/filter?status=published&author=john&tag=java
    @GetMapping("/filter")
    public ResponseEntity<List<Post>> filter(
        @RequestParam Map<String, String> filters
    ) {
        // filters = {status=published, author=john, tag=java}
        List<Post> posts = postService.filterByMultipleFields(filters);
        return ResponseEntity.ok(posts);
    }
}
```

### 실습 3: Content Negotiation (내용 협상)

**난이도**: ⭐⭐⭐☆☆

```java
@RestController
@RequestMapping("/api/v1/products")
public class ProductApiController {

    @Autowired
    private ProductService productService;

    // JSON과 XML 모두 지원
    @GetMapping(
        value = "/{id}",
        produces = {MediaType.APPLICATION_JSON_VALUE, MediaType.APPLICATION_XML_VALUE}
    )
    public ResponseEntity<Product> getProduct(@PathVariable Long id) {
        Product product = productService.findById(id);
        return ResponseEntity.ok(product);
        /*
        요청 헤더:
        - Accept: application/json → JSON 반환
        - Accept: application/xml → XML 반환
        - Accept: * /* → 기본값 (JSON) 반환
        */
    }

    // JSON 생성 전용
    @PostMapping(
        consumes = MediaType.APPLICATION_JSON_VALUE,
        produces = MediaType.APPLICATION_JSON_VALUE
    )
    public ResponseEntity<Product> createProductJson(@RequestBody Product product) {
        Product created = productService.save(product);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    // Form 데이터 생성
    @PostMapping(
        consumes = MediaType.APPLICATION_FORM_URLENCODED_VALUE,
        produces = MediaType.APPLICATION_JSON_VALUE
    )
    public ResponseEntity<Product> createProductForm(
        @RequestParam String name,
        @RequestParam BigDecimal price,
        @RequestParam(required = false) String description
    ) {
        Product product = Product.builder()
            .name(name)
            .price(price)
            .description(description)
            .build();

        Product created = productService.save(product);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    // PDF 다운로드
    @GetMapping(
        value = "/{id}/report",
        produces = MediaType.APPLICATION_PDF_VALUE
    )
    public ResponseEntity<byte[]> downloadReport(@PathVariable Long id) {
        byte[] pdfData = reportService.generatePdf(id);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_PDF);
        headers.setContentDispositionFormData("attachment", "product-" + id + ".pdf");

        return new ResponseEntity<>(pdfData, headers, HttpStatus.OK);
    }

    // 이미지 다운로드
    @GetMapping(
        value = "/{id}/image",
        produces = {MediaType.IMAGE_JPEG_VALUE, MediaType.IMAGE_PNG_VALUE}
    )
    public ResponseEntity<byte[]> getProductImage(@PathVariable Long id) {
        byte[] imageData = productService.getImage(id);
        return ResponseEntity.ok(imageData);
    }
}
```

**pom.xml 의존성 (XML 지원)**:

```xml
<!-- Jackson XML -->
<dependency>
    <groupId>com.fasterxml.jackson.dataformat</groupId>
    <artifactId>jackson-dataformat-xml</artifactId>
</dependency>
```

---

## 🏢 실무 활용 사례

### 사례 1: 네이버 쇼핑 - 상품 검색 API

**배경**: 네이버 쇼핑에서 복잡한 검색 조건을 처리하는 RESTful API 설계

**요구사항**:
```
1. 키워드 검색: /api/products/search?keyword=노트북
2. 카테고리 필터: /api/products?category=electronics&brand=삼성
3. 가격 범위: /api/products?minPrice=500000&maxPrice=1000000
4. 정렬 옵션: /api/products?sort=price_asc
5. 페이징: /api/products?page=2&size=20
```

**구현**:

```java
@RestController
@RequestMapping("/api/products")
public class NaverProductController {

    @Autowired
    private ProductSearchService searchService;

    // 복합 검색
    @GetMapping("/search")
    public ResponseEntity<SearchResponse> search(
        @RequestParam(required = false) String keyword,
        @RequestParam(required = false) String category,
        @RequestParam(required = false) String brand,
        @RequestParam(required = false) Integer minPrice,
        @RequestParam(required = false) Integer maxPrice,
        @RequestParam(defaultValue = "relevance") String sort,
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size
    ) {
        SearchCriteria criteria = SearchCriteria.builder()
            .keyword(keyword)
            .category(category)
            .brand(brand)
            .minPrice(minPrice)
            .maxPrice(maxPrice)
            .sort(sort)
            .build();

        Pageable pageable = PageRequest.of(page, size);
        Page<Product> products = searchService.search(criteria, pageable);

        SearchResponse response = SearchResponse.builder()
            .products(products.getContent())
            .totalCount(products.getTotalElements())
            .currentPage(page)
            .totalPages(products.getTotalPages())
            .build();

        return ResponseEntity.ok(response);
    }

    // 카테고리별 상품 조회
    @GetMapping("/category/{categoryId}")
    public ResponseEntity<List<Product>> getByCategory(
        @PathVariable Long categoryId,
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "40") int size
    ) {
        Pageable pageable = PageRequest.of(page, size);
        Page<Product> products = searchService.findByCategory(categoryId, pageable);
        return ResponseEntity.ok(products.getContent());
    }

    // 상품 상세
    @GetMapping("/{productId}")
    public ResponseEntity<ProductDetail> getProduct(@PathVariable Long productId) {
        ProductDetail detail = searchService.getProductDetail(productId);
        return ResponseEntity.ok(detail);
    }
}
```

**성과**:
- **검색 처리량**: 초당 10,000건 처리
- **응답 속도**: 평균 50ms
- **코드 간결성**: 기존 Servlet 대비 **75% 감소**

---

### 사례 2: 카카오뱅크 - RESTful API 버전 관리

**배경**: 카카오뱅크 모바일 앱 API의 하위 호환성 유지를 위한 버전 관리

**요구사항**:
```
1. v1 API: 기존 사용자 지원
2. v2 API: 신규 기능 추가
3. v3 API: 보안 강화 버전
4. 클라이언트별 API 분리 (모바일/웹)
```

**구현**:

```java
// v1 API - 기본 기능
@RestController
@RequestMapping("/api/v1/accounts")
public class AccountControllerV1 {

    @GetMapping("/{accountId}/balance")
    public ResponseEntity<BalanceResponse> getBalance(@PathVariable String accountId) {
        // 기본 잔액 조회
        BalanceResponse response = accountService.getBalance(accountId);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/transfer")
    public ResponseEntity<TransferResponse> transfer(@RequestBody TransferRequest request) {
        // 기본 이체
        TransferResponse response = accountService.transfer(request);
        return ResponseEntity.ok(response);
    }
}

// v2 API - 확장 기능
@RestController
@RequestMapping("/api/v2/accounts")
public class AccountControllerV2 {

    @GetMapping("/{accountId}/balance")
    public ResponseEntity<BalanceDetailResponse> getBalance(
        @PathVariable String accountId,
        @RequestParam(defaultValue = "false") boolean includeHistory
    ) {
        // 잔액 + 거래 내역 조회 (선택)
        BalanceDetailResponse response = accountService.getBalanceWithHistory(
            accountId,
            includeHistory
        );
        return ResponseEntity.ok(response);
    }

    @PostMapping("/transfer")
    public ResponseEntity<TransferDetailResponse> transfer(
        @RequestBody TransferRequestV2 request,
        @RequestHeader("X-Device-Id") String deviceId
    ) {
        // 이체 + 디바이스 검증
        TransferDetailResponse response = accountService.transferWithDeviceCheck(
            request,
            deviceId
        );
        return ResponseEntity.ok(response);
    }
}

// v3 API - 보안 강화
@RestController
@RequestMapping("/api/v3/accounts")
public class AccountControllerV3 {

    @PostMapping(
        value = "/transfer",
        consumes = MediaType.APPLICATION_JSON_VALUE,
        produces = MediaType.APPLICATION_JSON_VALUE
    )
    public ResponseEntity<TransferResponse> transfer(
        @RequestBody @Valid TransferRequestV3 request,
        @RequestHeader("Authorization") String token,
        @RequestHeader("X-Device-Id") String deviceId,
        @RequestHeader("X-Request-Signature") String signature
    ) {
        // 이체 + 디바이스 검증 + 전자서명 검증
        accountService.verifySignature(request, signature);
        TransferResponse response = accountService.secureTransfer(request, deviceId);
        return ResponseEntity.ok(response);
    }
}
```

**성과**:
- **API 버전 관리**: 3개 버전 동시 운영
- **하위 호환성**: 100% 유지
- **보안 강화**: v3에서 전자서명 추가로 **부정 거래 95% 감소**

---

### 사례 3: 쿠팡 - 주문 처리 시스템

**배경**: 쿠팡의 주문 처리 시스템에서 다양한 주문 타입과 상태 관리

**요구사항**:
```
1. 일반 주문, 로켓배송, 새벽배송 구분
2. 주문 상태 변경 (접수 → 처리중 → 배송중 → 완료)
3. 주문 취소/반품/교환 처리
4. 대량 주문 처리 (B2B)
```

**구현**:

```java
@RestController
@RequestMapping("/api/orders")
public class CoupangOrderController {

    @Autowired
    private OrderService orderService;

    // 1. 주문 생성
    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(
        @RequestBody @Valid OrderRequest request,
        @RequestHeader("X-User-Id") Long userId
    ) {
        Order order = orderService.createOrder(request, userId);

        URI location = ServletUriComponentsBuilder
            .fromCurrentRequest()
            .path("/{id}")
            .buildAndExpand(order.getId())
            .toUri();

        return ResponseEntity.created(location)
            .body(OrderResponse.from(order));
    }

    // 2. 주문 조회 (배송 타입별)
    @GetMapping(params = "deliveryType=rocket")
    public ResponseEntity<List<OrderSummary>> getRocketOrders(
        @RequestHeader("X-User-Id") Long userId,
        @RequestParam(defaultValue = "0") int page
    ) {
        List<OrderSummary> orders = orderService.findRocketOrders(userId, page);
        return ResponseEntity.ok(orders);
    }

    @GetMapping(params = "deliveryType=dawn")
    public ResponseEntity<List<OrderSummary>> getDawnOrders(
        @RequestHeader("X-User-Id") Long userId,
        @RequestParam(defaultValue = "0") int page
    ) {
        List<OrderSummary> orders = orderService.findDawnOrders(userId, page);
        return ResponseEntity.ok(orders);
    }

    // 3. 주문 상태 변경
    @PatchMapping("/{orderId}/status")
    public ResponseEntity<OrderResponse> updateStatus(
        @PathVariable Long orderId,
        @RequestBody StatusUpdateRequest request
    ) {
        Order order = orderService.updateStatus(orderId, request.getStatus());
        return ResponseEntity.ok(OrderResponse.from(order));
    }

    // 4. 주문 취소
    @PostMapping("/{orderId}/cancel")
    public ResponseEntity<CancelResponse> cancelOrder(
        @PathVariable Long orderId,
        @RequestBody CancelRequest request
    ) {
        CancelResponse response = orderService.cancelOrder(orderId, request);
        return ResponseEntity.ok(response);
    }

    // 5. 반품 요청
    @PostMapping("/{orderId}/return")
    public ResponseEntity<ReturnResponse> returnOrder(
        @PathVariable Long orderId,
        @RequestBody ReturnRequest request
    ) {
        ReturnResponse response = orderService.returnOrder(orderId, request);
        return ResponseEntity.ok(response);
    }

    // 6. 대량 주문 조회 (B2B)
    @GetMapping("/bulk")
    public ResponseEntity<List<OrderSummary>> bulkOrders(
        @RequestParam List<Long> orderIds
    ) {
        List<OrderSummary> orders = orderService.findByIds(orderIds);
        return ResponseEntity.ok(orders);
    }

    // 7. 날짜별 주문 조회
    @GetMapping("/{year}/{month}/{day}")
    public ResponseEntity<DailyOrderReport> getDailyOrders(
        @PathVariable int year,
        @PathVariable int month,
        @PathVariable int day,
        @RequestHeader("X-User-Id") Long userId
    ) {
        LocalDate date = LocalDate.of(year, month, day);
        DailyOrderReport report = orderService.getDailyReport(userId, date);
        return ResponseEntity.ok(report);
    }
}
```

**성과**:
- **주문 처리량**: 일 평균 **100만 건** 처리
- **응답 시간**: 주문 생성 평균 **200ms**
- **에러율**: **0.01% 미만** 유지
- **코드 유지보수**: 개발자 온보딩 시간 **70% 단축**

---

## 👨‍💻 주니어 개발자 시나리오

### 시나리오 1: "왜 GET으로는 생성이 안 될까요?"

**상황**:
주니어 개발자 김코딩이 게시글 작성 API를 개발하다가 GET 메서드를 사용했습니다.

```java
@GetMapping("/posts/create")  // ❌ 잘못된 방법
public String createPost(
    @RequestParam String title,
    @RequestParam String content
) {
    postService.save(new Post(title, content));
    return "redirect:/posts";
}
```

**문제점**:
```
1. RESTful 원칙 위반
   - GET은 조회 전용, 데이터 변경 X
   - 부작용(side effect) 있는 작업은 POST 사용

2. 보안 문제
   - URL에 데이터 노출: /posts/create?title=제목&content=내용
   - 브라우저 히스토리/로그에 남음
   - URL 길이 제한 (2048자)

3. 멱등성 문제
   - 새로고침 시 중복 생성
   - 크롤러가 URL 접근 시 자동 생성
```

**해결 방법**:

```java
// ✅ 올바른 방법 1: POST 사용
@PostMapping("/posts")
public ResponseEntity<Post> createPost(@RequestBody PostRequest request) {
    Post post = postService.save(request);

    URI location = ServletUriComponentsBuilder
        .fromCurrentRequest()
        .path("/{id}")
        .buildAndExpand(post.getId())
        .toUri();

    return ResponseEntity.created(location).body(post);
}

// ✅ 올바른 방법 2: Form 제출
@PostMapping("/posts/create")
public String createPost(
    @ModelAttribute PostForm form,
    RedirectAttributes redirectAttributes
) {
    Post post = postService.save(form);
    redirectAttributes.addFlashAttribute("message", "게시글이 작성되었습니다.");
    return "redirect:/posts/" + post.getId();
}
```

**교훈**:
- **GET**: 조회만 (안전, 멱등)
- **POST**: 생성 (비멱등)
- **PUT**: 전체 수정 (멱등)
- **PATCH**: 부분 수정
- **DELETE**: 삭제 (멱등)

---

### 시나리오 2: "@PathVariable vs @RequestParam, 뭘 써야 하죠?"

**상황**:
주니어 개발자 박초보가 사용자 조회 API를 설계하며 고민합니다.

```java
// 방법 1: PathVariable
@GetMapping("/users/{id}")
public User getUser1(@PathVariable Long id) {
    return userService.findById(id);
}

// 방법 2: RequestParam
@GetMapping("/users")
public User getUser2(@RequestParam Long id) {
    return userService.findById(id);
}
```

**차이점 분석**:

```
┌─────────────────┬──────────────────┬──────────────────┐
│ 구분            │ @PathVariable    │ @RequestParam    │
├─────────────────┼──────────────────┼──────────────────┤
│ URL 형식        │ /users/123       │ /users?id=123    │
│ 의미            │ 리소스 식별자     │ 필터/옵션        │
│ 필수 여부       │ 필수             │ 선택 가능        │
│ RESTful         │ ✅ 권장           │ 검색 조건에 사용 │
│ 예시            │ 특정 사용자       │ 검색/필터링      │
└─────────────────┴──────────────────┴──────────────────┘
```

**실전 가이드**:

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    // ✅ PathVariable: 리소스 식별
    @GetMapping("/{userId}")
    public User getUser(@PathVariable Long userId) {
        return userService.findById(userId);
    }

    @GetMapping("/{userId}/posts")
    public List<Post> getUserPosts(@PathVariable Long userId) {
        return postService.findByUserId(userId);
    }

    @GetMapping("/{userId}/posts/{postId}")
    public Post getUserPost(
        @PathVariable Long userId,
        @PathVariable Long postId
    ) {
        return postService.findByUserIdAndPostId(userId, postId);
    }

    // ✅ RequestParam: 검색/필터/옵션
    @GetMapping("/search")
    public List<User> searchUsers(
        @RequestParam(required = false) String name,
        @RequestParam(required = false) String email,
        @RequestParam(required = false) Integer age,
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size
    ) {
        return userService.search(name, email, age, page, size);
    }

    // ✅ 조합: 특정 사용자의 게시글 검색
    @GetMapping("/{userId}/posts/search")
    public List<Post> searchUserPosts(
        @PathVariable Long userId,              // 리소스 식별
        @RequestParam(required = false) String keyword,  // 검색어
        @RequestParam(defaultValue = "latest") String sort  // 정렬
    ) {
        return postService.searchByUser(userId, keyword, sort);
    }
}
```

**선택 기준**:
1. **@PathVariable**: `/users/123`, `/posts/456` - 리소스 식별
2. **@RequestParam**: `/users?age=25&city=서울` - 검색/필터

---

### 시나리오 3: "URL 패턴이 중복되는데 어떻게 구분하죠?"

**상황**:
주니어 개발자 이신입이 다음과 같은 코드를 작성했다가 에러가 발생했습니다.

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {

    // ❌ 충돌 발생!
    @GetMapping("/{id}")
    public Product getById(@PathVariable Long id) {
        return productService.findById(id);
    }

    @GetMapping("/{category}")  // ❌ 위와 구분 불가!
    public List<Product> getByCategory(@PathVariable String category) {
        return productService.findByCategory(category);
    }
}
```

**문제 원인**:
```
Spring이 /api/products/123을 보면:
- id=123인 상품?
- category="123"인 상품?
→ 구분 불가! Ambiguous mapping 에러 발생
```

**해결 방법**:

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {

    // ✅ 방법 1: URL 경로를 명확히 구분
    @GetMapping("/{id}")
    public Product getById(@PathVariable Long id) {
        return productService.findById(id);
    }

    @GetMapping("/category/{category}")  // 경로 추가
    public List<Product> getByCategory(@PathVariable String category) {
        return productService.findByCategory(category);
    }

    // ✅ 방법 2: 정규표현식으로 구분
    @GetMapping("/{id:\\d+}")  // 숫자만 매칭
    public Product getByIdRegex(@PathVariable Long id) {
        return productService.findById(id);
    }

    @GetMapping("/{category:[a-z]+}")  // 소문자만 매칭
    public List<Product> getByCategoryRegex(@PathVariable String category) {
        return productService.findByCategory(category);
    }

    // ✅ 방법 3: RequestParam 활용
    @GetMapping
    public ResponseEntity<?> get(
        @RequestParam(required = false) Long id,
        @RequestParam(required = false) String category
    ) {
        if (id != null) {
            return ResponseEntity.ok(productService.findById(id));
        } else if (category != null) {
            return ResponseEntity.ok(productService.findByCategory(category));
        } else {
            return ResponseEntity.ok(productService.findAll());
        }
    }

    // ✅ 방법 4: params 조건 사용
    @GetMapping(params = "id")
    public Product getByIdParam(@RequestParam Long id) {
        return productService.findById(id);
    }

    @GetMapping(params = "category")
    public List<Product> getByCategoryParam(@RequestParam String category) {
        return productService.findByCategory(category);
    }
}
```

**Best Practice**:
```java
// ✅ 가장 명확한 RESTful 설계
@RestController
@RequestMapping("/api")
public class RestfulProductController {

    // /api/products/123 - ID로 조회
    @GetMapping("/products/{id}")
    public Product getProduct(@PathVariable Long id) {
        return productService.findById(id);
    }

    // /api/categories/electronics/products - 카테고리로 조회
    @GetMapping("/categories/{category}/products")
    public List<Product> getProductsByCategory(@PathVariable String category) {
        return productService.findByCategory(category);
    }

    // /api/products/search?category=electronics&minPrice=10000 - 복합 검색
    @GetMapping("/products/search")
    public List<Product> searchProducts(
        @RequestParam(required = false) String category,
        @RequestParam(required = false) Integer minPrice,
        @RequestParam(required = false) Integer maxPrice
    ) {
        return productService.search(category, minPrice, maxPrice);
    }
}
```

---

## ❓ FAQ (자주 묻는 질문)

### Q1. @RequestMapping과 @GetMapping의 차이점은?

**A**: @GetMapping은 @RequestMapping의 축약형입니다.

```java
// 두 코드는 동일합니다
@RequestMapping(value = "/users", method = RequestMethod.GET)
public String list() { return "users/list"; }

@GetMapping("/users")  // 더 간결!
public String list() { return "users/list"; }
```

**비교표**:
```
┌─────────────────┬────────────────────────────────┬──────────────┐
│ 어노테이션       │ 동등한 표현                     │ Spring 버전  │
├─────────────────┼────────────────────────────────┼──────────────┤
│ @GetMapping     │ @RequestMapping(method = GET)  │ 4.3+         │
│ @PostMapping    │ @RequestMapping(method = POST) │ 4.3+         │
│ @PutMapping     │ @RequestMapping(method = PUT)  │ 4.3+         │
│ @DeleteMapping  │ @RequestMapping(method = DEL)  │ 4.3+         │
│ @PatchMapping   │ @RequestMapping(method = PATCH)│ 4.3+         │
└─────────────────┴────────────────────────────────┴──────────────┘
```

**언제 @RequestMapping을 사용하나요?**
```java
// 1. 여러 HTTP 메서드를 동시에 받을 때
@RequestMapping(value = "/search", method = {RequestMethod.GET, RequestMethod.POST})
public String search() { return "search"; }

// 2. 클래스 레벨에서 기본 경로 지정
@RequestMapping("/api/users")  // 클래스 레벨
public class UserController {
    @GetMapping("/{id}")  // 메서드 레벨
    public User getUser(@PathVariable Long id) { ... }
}
```

---

### Q2. PUT과 PATCH의 차이는 무엇인가요?

**A**: PUT은 **전체 교체**, PATCH는 **부분 수정**입니다.

```java
// 사용자 정보: { id: 1, name: "John", email: "john@example.com", age: 25 }

// PUT - 전체 교체 (보내지 않은 필드는 null이나 기본값으로 변경됨)
@PutMapping("/{id}")
public User update(@PathVariable Long id, @RequestBody User user) {
    return userService.replace(id, user);
}

// 요청: PUT /users/1
// Body: { "name": "Jane", "email": "jane@example.com", "age": 30 }
// 결과: { id: 1, name: "Jane", email: "jane@example.com", age: 30 }

// ─────────────────────────────────────────────────────

// PATCH - 부분 수정 (보낸 필드만 변경, 나머지는 유지)
@PatchMapping("/{id}")
public User partialUpdate(@PathVariable Long id, @RequestBody Map<String, Object> updates) {
    return userService.partialUpdate(id, updates);
}

// 요청: PATCH /users/1
// Body: { "age": 26 }
// 결과: { id: 1, name: "John", email: "john@example.com", age: 26 }
//       ↑ name, email은 그대로 유지!
```

**실무 예시**:
```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    // PUT - 사용자 정보 전체 수정
    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(
        @PathVariable Long id,
        @RequestBody @Valid UserUpdateRequest request
    ) {
        // 모든 필드가 필수!
        if (request.getName() == null || request.getEmail() == null) {
            return ResponseEntity.badRequest().build();
        }

        User updated = userService.update(id, request);
        return ResponseEntity.ok(updated);
    }

    // PATCH - 일부 필드만 수정
    @PatchMapping("/{id}")
    public ResponseEntity<User> patchUser(
        @PathVariable Long id,
        @RequestBody Map<String, Object> updates
    ) {
        // 제공된 필드만 업데이트
        User user = userService.findById(id);

        if (updates.containsKey("name")) {
            user.setName((String) updates.get("name"));
        }
        if (updates.containsKey("age")) {
            user.setAge((Integer) updates.get("age"));
        }

        User updated = userService.save(user);
        return ResponseEntity.ok(updated);
    }
}
```

---

### Q3. @PathVariable의 required 속성은 어떻게 사용하나요?

**A**: Spring 4.3.3부터 `required` 속성을 지원합니다.

```java
@RestController
@RequestMapping("/api/files")
public class FileController {

    // 1. 기본값: required = true (필수)
    @GetMapping("/{fileId}")
    public File getFile(@PathVariable Long fileId) {
        return fileService.findById(fileId);
    }
    // /api/files/123 → OK
    // /api/files/    → 404 에러

    // 2. required = false (선택)
    @GetMapping({"/", "/{category}"})
    public List<File> getFiles(
        @PathVariable(required = false) String category
    ) {
        if (category != null) {
            return fileService.findByCategory(category);
        } else {
            return fileService.findAll();
        }
    }
    // /api/files/           → 전체 조회
    // /api/files/documents  → 카테고리별 조회

    // 3. Optional 사용 (Java 8+)
    @GetMapping({"/", "/{category}"})
    public List<File> getFilesOptional(
        @PathVariable Optional<String> category
    ) {
        return category
            .map(fileService::findByCategory)
            .orElseGet(fileService::findAll);
    }
}
```

---

### Q4. URL에 특수문자가 포함되어 있으면 어떻게 처리하나요?

**A**: **URL 인코딩**이 필요하며, Spring이 자동으로 디코딩합니다.

```java
@RestController
@RequestMapping("/api/search")
public class SearchController {

    @GetMapping("/{keyword}")
    public List<Product> search(@PathVariable String keyword) {
        // Spring이 자동으로 URL 디코딩
        System.out.println("검색어: " + keyword);
        return productService.search(keyword);
    }
}

// 테스트:
// GET /api/search/스프링%20MVC
// → keyword = "스프링 MVC" (자동 디코딩됨)

// GET /api/search/price%3E1000
// → keyword = "price>1000"
```

**특수문자 인코딩 표**:
```
┌──────────┬──────────┬─────────────────┐
│ 문자     │ 인코딩   │ 용도            │
├──────────┼──────────┼─────────────────┤
│ 공백     │ %20      │ 띄어쓰기        │
│ /        │ %2F      │ 경로 구분자     │
│ ?        │ %3F      │ 쿼리 시작       │
│ &        │ %26      │ 파라미터 구분   │
│ =        │ %3D      │ 값 할당         │
│ #        │ %23      │ Fragment        │
│ @        │ %40      │ 이메일 등       │
└──────────┴──────────┴─────────────────┘
```

**클라이언트에서 인코딩**:
```javascript
// JavaScript
const keyword = "스프링 MVC";
const encoded = encodeURIComponent(keyword);
fetch(`/api/search/${encoded}`);
// → GET /api/search/%EC%8A%A4%ED%94%84%EB%A7%81%20MVC

// Java RestTemplate
String keyword = "스프링 MVC";
String url = UriComponentsBuilder
    .fromPath("/api/search/{keyword}")
    .buildAndExpand(keyword)
    .encode()
    .toUriString();
restTemplate.getForObject(url, List.class);
```

---

### Q5. 같은 URL에 대해 GET과 POST를 모두 처리하려면?

**A**: 방법은 3가지입니다.

```java
// 방법 1: @RequestMapping에 여러 메서드 지정
@RequestMapping(value = "/search", method = {RequestMethod.GET, RequestMethod.POST})
public String search(
    @RequestParam(required = false) String keyword,
    Model model
) {
    List<Product> products = productService.search(keyword);
    model.addAttribute("products", products);
    return "search/result";
}

// 방법 2: 별도 메서드로 분리 (권장)
@GetMapping("/search")
public String searchForm() {
    return "search/form";  // 검색 폼 표시
}

@PostMapping("/search")
public String searchSubmit(@RequestParam String keyword, Model model) {
    List<Product> products = productService.search(keyword);
    model.addAttribute("products", products);
    return "search/result";  // 검색 결과 표시
}

// 방법 3: 공통 로직 분리
@GetMapping("/search")
public String searchGet(@RequestParam(required = false) String keyword, Model model) {
    return performSearch(keyword, model);
}

@PostMapping("/search")
public String searchPost(@RequestParam String keyword, Model model) {
    return performSearch(keyword, model);
}

private String performSearch(String keyword, Model model) {
    if (keyword != null && !keyword.isEmpty()) {
        List<Product> products = productService.search(keyword);
        model.addAttribute("products", products);
    }
    return "search/result";
}
```

**언제 어떤 방식을 사용하나요?**
```
✅ GET: 검색 폼 표시, 검색 결과 조회 (북마크 가능)
✅ POST: 폼 제출, 민감한 데이터 전송 (북마크 불가)
```

---

### Q6. produces와 consumes의 차이는?

**A**: **consumes**는 요청, **produces**는 응답 Content-Type입니다.

```java
@RestController
@RequestMapping("/api/data")
public class ContentTypeController {

    // consumes: 이 API가 받을 수 있는 형식
    @PostMapping(
        value = "/upload",
        consumes = "application/json"  // JSON만 받음
    )
    public String uploadJson(@RequestBody Data data) {
        return "JSON 데이터 받음";
    }
    // ✅ Content-Type: application/json → OK
    // ❌ Content-Type: application/xml → 415 Unsupported Media Type

    // produces: 이 API가 반환하는 형식
    @GetMapping(
        value = "/download",
        produces = "application/json"  // JSON으로 반환
    )
    public Data download() {
        return new Data("example");
    }
    // ✅ Accept: application/json → OK
    // ❌ Accept: application/xml → 406 Not Acceptable

    // 둘 다 사용
    @PostMapping(
        value = "/process",
        consumes = "application/json",  // JSON 받고
        produces = "application/xml"    // XML로 반환
    )
    public XmlData process(@RequestBody JsonData data) {
        return converter.toXml(data);
    }

    // 여러 형식 지원
    @PostMapping(
        value = "/flexible",
        consumes = {"application/json", "application/xml"},
        produces = {"application/json", "application/xml"}
    )
    public Data flexible(@RequestBody Data data) {
        return data;
    }
    // 클라이언트의 Content-Type과 Accept에 따라 자동 변환
}
```

**정리**:
```
┌──────────┬──────────┬──────────────────────┐
│ 속성     │ 방향     │ HTTP 헤더            │
├──────────┼──────────┼──────────────────────┤
│ consumes │ 요청 →   │ Content-Type         │
│ produces │ ← 응답   │ Accept (요청 헤더)   │
└──────────┴──────────┴──────────────────────┘
```

---

### Q7. 컨트롤러에서 여러 개의 파라미터를 받을 때 베스트 프랙티스는?

**A**: 파라미터가 3개 이상이면 **DTO 객체**로 묶는 것이 좋습니다.

```java
// ❌ 나쁜 예: 파라미터가 너무 많음
@GetMapping("/search")
public List<Product> search(
    @RequestParam(required = false) String keyword,
    @RequestParam(required = false) String category,
    @RequestParam(required = false) Integer minPrice,
    @RequestParam(required = false) Integer maxPrice,
    @RequestParam(required = false) String brand,
    @RequestParam(required = false) String color,
    @RequestParam(defaultValue = "0") int page,
    @RequestParam(defaultValue = "20") int size,
    @RequestParam(defaultValue = "relevance") String sort
) {
    // 파라미터가 너무 많아 가독성 저하!
}

// ✅ 좋은 예: DTO로 묶기
@GetMapping("/search")
public List<Product> search(@ModelAttribute ProductSearchRequest request) {
    return productService.search(request);
}

@Data
public class ProductSearchRequest {
    private String keyword;
    private String category;
    private Integer minPrice;
    private Integer maxPrice;
    private String brand;
    private String color;

    @Builder.Default
    private int page = 0;

    @Builder.Default
    private int size = 20;

    @Builder.Default
    private String sort = "relevance";
}

// ✅ REST API: @RequestBody 사용
@PostMapping("/search")
public List<Product> searchPost(@RequestBody ProductSearchRequest request) {
    return productService.search(request);
}
```

**장점**:
```
1. 가독성 향상
2. 유효성 검증 추가 가능 (@Valid, @NotNull 등)
3. 재사용 가능
4. 테스트 용이
```

---

## 🎤 면접 질문 리스트

### 주니어 레벨 (5-7개)

1. **@RequestMapping과 @GetMapping의 차이점을 설명하고, 언제 각각 사용하는지 말해보세요.**

2. **RESTful API에서 HTTP 메서드(GET, POST, PUT, DELETE)는 각각 어떤 용도로 사용되나요?**

3. **@PathVariable과 @RequestParam의 차이점은 무엇이며, 각각 어떤 상황에 사용하나요?**

4. **URL 패턴 매칭에서 *, **, ? 와일드카드의 차이점을 설명해보세요.**

5. **PUT과 PATCH 메서드의 차이점은 무엇인가요?**

6. **@RequestMapping의 consumes와 produces 속성은 각각 무엇을 의미하나요?**

7. **Controller와 RestController의 차이점은 무엇인가요?**

### 중급 레벨 (3-5개)

1. **Spring MVC에서 요청 URL이 여러 핸들러 메서드와 매칭될 때, 어떤 우선순위로 선택되나요?**

2. **@RequestMapping의 params와 headers 속성을 사용하여 같은 URL에 대해 다른 핸들러를 매핑하는 방법과 실무 활용 사례를 설명해보세요.**

3. **Content Negotiation(내용 협상)이란 무엇이며, Spring에서 어떻게 구현하나요?**

4. **RESTful API 버전 관리 전략(URI versioning, Header versioning 등)에 대해 설명하고, 각각의 장단점을 말해보세요.**

5. **@PathVariable에서 정규표현식을 사용하는 방법과 실무에서의 활용 사례를 설명해보세요.**

---

## 💡 면접 질문 답안

### 주니어 레벨 답안

#### Q1. @RequestMapping과 @GetMapping의 차이점을 설명하고, 언제 각각 사용하는지 말해보세요.

**답변**:

@GetMapping은 @RequestMapping의 축약형으로, Spring 4.3부터 도입되었습니다.

```java
// 동일한 기능
@RequestMapping(value = "/users", method = RequestMethod.GET)
@GetMapping("/users")
```

**주요 차이점**:

1. **간결성**: @GetMapping이 더 짧고 읽기 쉽습니다
2. **의도 명확성**: HTTP 메서드가 어노테이션 이름에 명시되어 코드 가독성이 높습니다
3. **기능**: 동일한 기능을 수행하며, 내부적으로 @RequestMapping(method = GET)으로 변환됩니다

**사용 시기**:

```java
// @RequestMapping: 클래스 레벨에서 기본 경로 지정
@Controller
@RequestMapping("/api/users")
public class UserController {

    // @GetMapping: 메서드 레벨에서 GET 요청 처리
    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
    }

    // 여러 HTTP 메서드를 받을 때만 @RequestMapping 사용
    @RequestMapping(value = "/search", method = {RequestMethod.GET, RequestMethod.POST})
    public List<User> search() {
        return userService.search();
    }
}
```

**실무 권장**:
- 단일 HTTP 메서드: @GetMapping, @PostMapping 등 사용 (간결함)
- 여러 HTTP 메서드: @RequestMapping 사용
- 클래스 레벨: @RequestMapping으로 기본 경로 지정

---

#### Q2. RESTful API에서 HTTP 메서드(GET, POST, PUT, DELETE)는 각각 어떤 용도로 사용되나요?

**답변**:

RESTful API에서 HTTP 메서드는 **리소스에 대한 행위**를 나타냅니다.

```
┌─────────┬─────────┬──────────────┬─────────┬─────────┐
│ 메서드  │ 용도    │ 멱등성       │ 안전성  │ 예시    │
├─────────┼─────────┼──────────────┼─────────┼─────────┤
│ GET     │ 조회    │ ✅ 멱등      │ ✅ 안전 │ 목록    │
│ POST    │ 생성    │ ❌ 비멱등    │ ❌      │ 등록    │
│ PUT     │ 전체수정│ ✅ 멱등      │ ❌      │ 전체변경│
│ PATCH   │ 부분수정│ ❌ 비멱등    │ ❌      │ 일부변경│
│ DELETE  │ 삭제    │ ✅ 멱등      │ ❌      │ 제거    │
└─────────┴─────────┴──────────────┴─────────┴─────────┘
```

**실무 예시**:

```java
@RestController
@RequestMapping("/api/users")
public class UserApiController {

    // GET - 조회 (안전, 멱등)
    @GetMapping
    public List<User> getAll() {
        return userService.findAll();
    }

    @GetMapping("/{id}")
    public User getOne(@PathVariable Long id) {
        return userService.findById(id);
    }

    // POST - 생성 (비멱등: 호출할 때마다 새 리소스 생성)
    @PostMapping
    public ResponseEntity<User> create(@RequestBody User user) {
        User created = userService.save(user);
        return ResponseEntity.created(location).body(created);
    }

    // PUT - 전체 수정 (멱등: 같은 요청 반복 시 결과 동일)
    @PutMapping("/{id}")
    public User update(@PathVariable Long id, @RequestBody User user) {
        return userService.update(id, user);  // 전체 필드 교체
    }

    // PATCH - 부분 수정
    @PatchMapping("/{id}")
    public User partialUpdate(@PathVariable Long id, @RequestBody Map<String, Object> updates) {
        return userService.partialUpdate(id, updates);  // 제공된 필드만 수정
    }

    // DELETE - 삭제 (멱등: 한 번 삭제하면 재요청 시에도 결과 동일)
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        userService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

**멱등성 설명**:
- **멱등**: 같은 요청을 여러 번 해도 결과가 동일
  - GET /users/1 → 항상 같은 사용자 반환
  - DELETE /users/1 → 한 번 삭제 후 재요청 시 "이미 없음" (결과 동일)
- **비멱등**: 요청할 때마다 결과가 달라짐
  - POST /users → 호출할 때마다 새 사용자 생성

---

#### Q3. @PathVariable과 @RequestParam의 차이점은 무엇이며, 각각 어떤 상황에 사용하나요?

**답변**:

**@PathVariable**은 URL 경로의 일부로 값을 전달하고, **@RequestParam**은 쿼리 스트링으로 값을 전달합니다.

```java
// @PathVariable: URL 경로에 포함
@GetMapping("/users/{id}")
public User getUser(@PathVariable Long id) {
    return userService.findById(id);
}
// 호출: GET /users/123
// id = 123

// @RequestParam: 쿼리 스트링
@GetMapping("/users")
public List<User> searchUsers(@RequestParam String name) {
    return userService.findByName(name);
}
// 호출: GET /users?name=John
// name = "John"
```

**차이점 비교**:

```
┌──────────────────┬────────────────┬─────────────────┐
│ 구분             │ @PathVariable  │ @RequestParam   │
├──────────────────┼────────────────┼─────────────────┤
│ URL 형식         │ /users/123     │ /users?id=123   │
│ 의미             │ 리소스 식별자   │ 필터/옵션/조건  │
│ 필수 여부        │ 필수 (기본값)  │ 선택 가능       │
│ RESTful          │ ✅ 권장        │ 검색/필터에 사용│
│ 예시             │ 특정 리소스    │ 검색 조건       │
│ 여러 개 사용     │ 가능           │ 가능            │
└──────────────────┴────────────────┴─────────────────┘
```

**실무 사용 예시**:

```java
@RestController
@RequestMapping("/api")
public class RestfulExampleController {

    // @PathVariable: 리소스 식별
    @GetMapping("/users/{userId}")
    public User getUser(@PathVariable Long userId) {
        return userService.findById(userId);
    }

    // 중첩 리소스
    @GetMapping("/users/{userId}/posts/{postId}")
    public Post getUserPost(
        @PathVariable Long userId,
        @PathVariable Long postId
    ) {
        return postService.findByUserAndPost(userId, postId);
    }

    // @RequestParam: 검색/필터
    @GetMapping("/users/search")
    public List<User> searchUsers(
        @RequestParam(required = false) String name,
        @RequestParam(required = false) Integer age,
        @RequestParam(defaultValue = "0") int page
    ) {
        return userService.search(name, age, page);
    }

    // 조합: 특정 사용자의 게시글 검색
    @GetMapping("/users/{userId}/posts")
    public List<Post> getUserPosts(
        @PathVariable Long userId,                    // 리소스 식별
        @RequestParam(defaultValue = "latest") String sort,  // 정렬 옵션
        @RequestParam(defaultValue = "0") int page          // 페이징
    ) {
        return postService.findByUser(userId, sort, page);
    }
}
```

**선택 기준**:
- **@PathVariable**: `/users/123` - 특정 리소스를 명확히 식별할 때
- **@RequestParam**: `/users?age=25&city=서울` - 검색, 필터링, 옵션 지정할 때

---

#### Q4. URL 패턴 매칭에서 *, **, ? 와일드카드의 차이점을 설명해보세요.

**답변**:

```
┌────────┬────────────────────────┬──────────────────────────┐
│ 패턴   │ 의미                   │ 예시                      │
├────────┼────────────────────────┼──────────────────────────┤
│ ?      │ 정확히 1개 문자 매칭   │ /user? → /user1, /userA  │
│ *      │ 0개 이상 문자 (한 경로)│ /files/* → /files/a.txt  │
│ **     │ 0개 이상 경로          │ /files/** → /files/a/b/c │
└────────┴────────────────────────┴──────────────────────────┘
```

**상세 예시**:

```java
@RestController
public class WildcardController {

    // ? : 정확히 1개 문자
    @GetMapping("/user?")
    public String singleChar() {
        return "user";
    }
    // ✅ 매칭: /user1, /user2, /userA
    // ❌ 불일치: /user (문자 없음), /user12 (문자 2개)

    // * : 한 경로 내에서 0개 이상 문자
    @GetMapping("/files/*")
    public String anyChars() {
        return "files";
    }
    // ✅ 매칭: /files/a, /files/readme.txt, /files/report
    // ❌ 불일치: /files/docs/a.txt (/ 포함됨)

    // ** : 0개 이상의 전체 경로
    @GetMapping("/files/**")
    public String anyPaths() {
        return "files";
    }
    // ✅ 매칭:
    //   /files/a
    //   /files/docs/report.pdf
    //   /files/2024/01/15/data.csv
    //   /files/ (하위 경로 없음도 OK)

    // 확장자 매칭
    @GetMapping("/download.*")
    public String anyExtension() {
        return "download";
    }
    // ✅ 매칭: /download.pdf, /download.xlsx, /download.zip

    // 복합 패턴
    @GetMapping("/{year}/{month}/*.pdf")
    public String complexPattern(
        @PathVariable int year,
        @PathVariable int month
    ) {
        return "report";
    }
    // ✅ 매칭: /2024/10/report.pdf, /2024/01/summary.pdf
    // ❌ 불일치: /2024/10/docs/report.pdf (중첩 경로)
}
```

**실무 활용**:

```java
// 정적 리소스 처리
@GetMapping("/static/**")
public void handleStatic() {
    // /static/css/style.css
    // /static/js/app.js
    // /static/images/logo.png
}

// API 버전 관리
@GetMapping("/api/v*/users")
public List<User> getUsers() {
    // /api/v1/users
    // /api/v2/users
    // /api/v3/users
}

// 파일 다운로드
@GetMapping("/files/**/download")
public ResponseEntity<byte[]> download() {
    // /files/documents/download
    // /files/2024/10/reports/download
}
```

---

#### Q5. PUT과 PATCH 메서드의 차이점은 무엇인가요?

**답변**:

**PUT**은 리소스 **전체를 교체**하고, **PATCH**는 리소스의 **일부만 수정**합니다.

```java
// 기존 데이터
User user = {
    id: 1,
    name: "John",
    email: "john@example.com",
    age: 25,
    address: "서울"
};

// PUT - 전체 교체
@PutMapping("/users/{id}")
public User updateUser(@PathVariable Long id, @RequestBody User user) {
    return userService.replace(id, user);
}

// 요청: PUT /users/1
// Body: { "name": "Jane", "email": "jane@example.com", "age": 30 }
// 결과: { id: 1, name: "Jane", email: "jane@example.com", age: 30, address: null }
//                                                               ↑ 보내지 않은 필드는 null

// ─────────────────────────────────────────────────────

// PATCH - 부분 수정
@PatchMapping("/users/{id}")
public User partialUpdate(@PathVariable Long id, @RequestBody Map<String, Object> updates) {
    return userService.partialUpdate(id, updates);
}

// 요청: PATCH /users/1
// Body: { "age": 26 }
// 결과: { id: 1, name: "John", email: "john@example.com", age: 26, address: "서울" }
//       ↑ 보내지 않은 필드는 그대로 유지
```

**주요 차이점**:

```
┌───────────────┬─────────────────┬─────────────────┐
│ 구분          │ PUT             │ PATCH           │
├───────────────┼─────────────────┼─────────────────┤
│ 의미          │ 전체 교체       │ 부분 수정       │
│ 멱등성        │ ✅ 멱등         │ ❌ 비멱등       │
│ 전송 데이터   │ 전체 필드 필수  │ 수정할 필드만   │
│ 미전송 필드   │ null/기본값     │ 기존 값 유지    │
│ 실무 사용     │ 전체 수정 폼    │ 토글, 일부 변경 │
└───────────────┴─────────────────┴─────────────────┘
```

**실무 구현 예시**:

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    // PUT: 전체 수정 (모든 필드 필수)
    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(
        @PathVariable Long id,
        @RequestBody @Valid UserUpdateRequest request
    ) {
        // 요청에 모든 필드가 있는지 검증
        if (request.getName() == null || request.getEmail() == null) {
            return ResponseEntity.badRequest().build();
        }

        User user = User.builder()
            .id(id)
            .name(request.getName())
            .email(request.getEmail())
            .age(request.getAge())
            .address(request.getAddress())
            .build();

        User updated = userRepository.save(user);
        return ResponseEntity.ok(updated);
    }

    // PATCH: 부분 수정 (제공된 필드만 수정)
    @PatchMapping("/{id}")
    public ResponseEntity<User> patchUser(
        @PathVariable Long id,
        @RequestBody Map<String, Object> updates
    ) {
        User user = userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException());

        // 제공된 필드만 업데이트
        if (updates.containsKey("name")) {
            user.setName((String) updates.get("name"));
        }
        if (updates.containsKey("age")) {
            user.setAge((Integer) updates.get("age"));
        }
        if (updates.containsKey("address")) {
            user.setAddress((String) updates.get("address"));
        }

        User updated = userRepository.save(user);
        return ResponseEntity.ok(updated);
    }
}
```

**실무 사용 사례**:
- **PUT**: 프로필 전체 수정 폼에서 제출 시
- **PATCH**:
  - 사용자 활성화/비활성화 토글
  - 좋아요 수 증가
  - 특정 필드만 수정 (예: 비밀번호만 변경)

---

#### Q6. @RequestMapping의 consumes와 produces 속성은 각각 무엇을 의미하나요?

**답변**:

**consumes**는 컨트롤러가 **받을 수 있는 요청의 Content-Type**을 지정하고,
**produces**는 컨트롤러가 **반환하는 응답의 Content-Type**을 지정합니다.

```
┌──────────┬────────────┬──────────────────────┬──────────────┐
│ 속성     │ 방향       │ HTTP 헤더            │ 에러 코드    │
├──────────┼────────────┼──────────────────────┼──────────────┤
│ consumes │ 요청 →     │ Content-Type (요청)  │ 415 에러     │
│ produces │ ← 응답     │ Accept (요청)        │ 406 에러     │
└──────────┴────────────┴──────────────────────┴──────────────┘
```

**예시 코드**:

```java
@RestController
@RequestMapping("/api/data")
public class ContentTypeController {

    // 1. consumes: JSON만 받음
    @PostMapping(
        value = "/upload",
        consumes = "application/json"
    )
    public String uploadJson(@RequestBody Data data) {
        return "JSON 데이터를 받았습니다";
    }
    // ✅ Content-Type: application/json → 처리
    // ❌ Content-Type: application/xml → 415 Unsupported Media Type

    // 2. produces: JSON으로 반환
    @GetMapping(
        value = "/download",
        produces = "application/json"
    )
    public Data downloadJson() {
        return new Data("example");
    }
    // ✅ Accept: application/json → JSON 반환
    // ❌ Accept: application/xml → 406 Not Acceptable

    // 3. 둘 다 사용
    @PostMapping(
        value = "/process",
        consumes = "application/json",  // JSON 받고
        produces = "application/xml"    // XML로 반환
    )
    public XmlResponse process(@RequestBody JsonRequest request) {
        return converter.toXml(request);
    }

    // 4. 여러 형식 지원
    @PostMapping(
        value = "/flexible",
        consumes = {"application/json", "application/xml"},
        produces = {"application/json", "application/xml"}
    )
    public Data flexible(@RequestBody Data data) {
        return data;
    }
    // 클라이언트의 Content-Type과 Accept에 따라 자동 변환

    // 5. MediaType 상수 사용 (권장)
    @PostMapping(
        consumes = MediaType.APPLICATION_JSON_VALUE,
        produces = MediaType.APPLICATION_JSON_VALUE
    )
    public ResponseEntity<Data> createData(@RequestBody Data data) {
        Data saved = dataService.save(data);
        return ResponseEntity.ok(saved);
    }
}
```

**실무 활용**:

```java
// 파일 업로드
@PostMapping(
    value = "/upload",
    consumes = MediaType.MULTIPART_FORM_DATA_VALUE
)
public String uploadFile(@RequestParam("file") MultipartFile file) {
    fileService.save(file);
    return "업로드 완료";
}

// 이미지 다운로드
@GetMapping(
    value = "/image/{id}",
    produces = MediaType.IMAGE_JPEG_VALUE
)
public byte[] getImage(@PathVariable Long id) {
    return imageService.getImage(id);
}

// PDF 생성
@GetMapping(
    value = "/report/{id}",
    produces = MediaType.APPLICATION_PDF_VALUE
)
public ResponseEntity<byte[]> generateReport(@PathVariable Long id) {
    byte[] pdf = reportService.generatePdf(id);
    return ResponseEntity.ok()
        .header("Content-Disposition", "attachment; filename=report.pdf")
        .body(pdf);
}
```

---

#### Q7. Controller와 RestController의 차이점은 무엇인가요?

**답변**:

**@Controller**는 뷰를 반환하고, **@RestController**는 데이터(JSON/XML)를 반환합니다.

```java
// @Controller: 뷰 반환 (HTML 페이지)
@Controller
@RequestMapping("/users")
public class UserViewController {

    @GetMapping("/{id}")
    public String getUser(@PathVariable Long id, Model model) {
        User user = userService.findById(id);
        model.addAttribute("user", user);
        return "users/detail";  // → users/detail.jsp 또는 .html로 이동
    }

    // 데이터를 반환하려면 @ResponseBody 추가
    @GetMapping("/api/{id}")
    @ResponseBody  // 이 어노테이션을 추가해야 JSON 반환
    public User getUserApi(@PathVariable Long id) {
        return userService.findById(id);  // → JSON 반환
    }
}

// @RestController: 데이터 반환 (JSON/XML)
@RestController  // = @Controller + @ResponseBody (모든 메서드에 자동 적용)
@RequestMapping("/api/users")
public class UserApiController {

    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);  // → 자동으로 JSON 반환
    }

    @GetMapping
    public List<User> getAllUsers() {
        return userService.findAll();  // → 자동으로 JSON 반환
    }
}
```

**비교표**:

```
┌─────────────────┬─────────────────┬─────────────────────┐
│ 구분            │ @Controller     │ @RestController     │
├─────────────────┼─────────────────┼─────────────────────┤
│ 반환 타입       │ 뷰 이름(String) │ 데이터(객체)        │
│ 용도            │ HTML 렌더링     │ API (JSON/XML)      │
│ ViewResolver    │ ✅ 사용         │ ❌ 사용 안 함       │
│ @ResponseBody   │ 필요 시 추가    │ 모든 메서드에 자동  │
│ 프론트엔드      │ JSP, Thymeleaf  │ React, Vue, 모바일  │
└─────────────────┴─────────────────┴─────────────────────┘
```

**내부 동작 원리**:

```java
// @RestController 정의 (Spring 소스 코드)
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Controller
@ResponseBody  // 이 줄이 핵심!
public @interface RestController {
    @AliasFor(annotation = Controller.class)
    String value() default "";
}
```

**실무 사용**:

```java
// 1. 전통적인 웹 애플리케이션: @Controller
@Controller
public class WebController {

    @GetMapping("/")
    public String home(Model model) {
        model.addAttribute("message", "Welcome!");
        return "index";  // → index.html 렌더링
    }

    @GetMapping("/users")
    public String userList(Model model) {
        List<User> users = userService.findAll();
        model.addAttribute("users", users);
        return "users/list";  // → users/list.html 렌더링
    }
}

// 2. RESTful API: @RestController
@RestController
@RequestMapping("/api")
public class ApiController {

    @GetMapping("/users")
    public List<User> getUsers() {
        return userService.findAll();  // → JSON 반환
    }

    @PostMapping("/users")
    public ResponseEntity<User> createUser(@RequestBody User user) {
        User created = userService.save(user);
        return ResponseEntity.created(location).body(created);
    }
}

// 3. 하이브리드: @Controller + @ResponseBody
@Controller
@RequestMapping("/hybrid")
public class HybridController {

    // 뷰 반환
    @GetMapping("/page")
    public String page() {
        return "hybrid/page";
    }

    // JSON 반환
    @GetMapping("/api/data")
    @ResponseBody
    public Map<String, Object> data() {
        return Map.of("status", "ok", "data", userService.findAll());
    }
}
```

**선택 기준**:
- **@Controller**: JSP, Thymeleaf 등 서버 사이드 렌더링
- **@RestController**: React, Vue, 모바일 앱을 위한 RESTful API

---

### 중급 레벨 답안

#### Q1. Spring MVC에서 요청 URL이 여러 핸들러 메서드와 매칭될 때, 어떤 우선순위로 선택되나요?

**답변**:

Spring MVC는 **가장 구체적인(specific) 매핑**을 우선 선택합니다. 우선순위는 다음과 같습니다:

**1. 정확한 매칭 > 패턴 매칭**

```java
@RestController
public class PriorityController {

    // 우선순위 1: 정확한 매칭
    @GetMapping("/users/special")
    public String exact() {
        return "exact";
    }

    // 우선순위 2: 패턴 매칭
    @GetMapping("/users/{id}")
    public String pattern(@PathVariable String id) {
        return "pattern: " + id;
    }

    // GET /users/special → exact() 호출 (정확한 매칭 우선)
    // GET /users/123 → pattern() 호출
}
```

**2. 긴 경로 > 짧은 경로**

```java
// 우선순위 1: 더 긴 경로
@GetMapping("/api/v1/users/{id}/details")
public String detailed(@PathVariable Long id) {
    return "detailed";
}

// 우선순위 2: 짧은 경로
@GetMapping("/api/v1/users/{id}")
public String simple(@PathVariable Long id) {
    return "simple";
}

// GET /api/v1/users/123/details → detailed() 호출
// GET /api/v1/users/123 → simple() 호출
```

**3. 와일드카드 우선순위**

```
정확한 문자 > ? > * > **

예시:
1. /files/readme.txt    (정확한 매칭)
2. /files/readm?.txt    (? 패턴)
3. /files/*.txt         (* 패턴)
4. /files/**            (** 패턴)
```

```java
@GetMapping("/files/readme.txt")  // 우선순위 1
public String exact() { return "exact"; }

@GetMapping("/files/*.txt")       // 우선순위 2
public String star() { return "star"; }

@GetMapping("/files/**")          // 우선순위 3
public String doubleStar() { return "doubleStar"; }

// GET /files/readme.txt → exact() 호출
// GET /files/report.txt → star() 호출
// GET /files/docs/a.md → doubleStar() 호출
```

**4. HTTP 메서드 제약이 있는 것이 우선**

```java
// 우선순위 1: 구체적인 메서드
@GetMapping("/users/{id}")
public User getUser(@PathVariable Long id) {
    return userService.findById(id);
}

// 우선순위 2: 모든 메서드 허용
@RequestMapping("/users/{id}")
public User anyMethod(@PathVariable Long id) {
    return userService.findById(id);
}

// GET /users/123 → getUser() 호출 (GET이 명시된 것 우선)
```

**5. params, headers 조건이 있는 것이 우선**

```java
// 우선순위 1: params 조건 있음
@GetMapping(value = "/search", params = "type=advanced")
public String advancedSearch() {
    return "advanced";
}

// 우선순위 2: 조건 없음
@GetMapping("/search")
public String simpleSearch() {
    return "simple";
}

// GET /search?type=advanced → advancedSearch() 호출
// GET /search → simpleSearch() 호출
```

**종합 예시**:

```java
@RestController
@RequestMapping("/api/products")
public class ProductPriorityController {

    // 우선순위 1: 가장 구체적 (정확한 경로 + params)
    @GetMapping(value = "/search", params = "type=advanced")
    public String priority1() {
        return "1: advanced search";
    }

    // 우선순위 2: 정확한 경로
    @GetMapping("/search")
    public String priority2() {
        return "2: simple search";
    }

    // 우선순위 3: 긴 패턴
    @GetMapping("/{category}/{id}/details")
    public String priority3(@PathVariable String category, @PathVariable Long id) {
        return "3: detailed";
    }

    // 우선순위 4: 짧은 패턴
    @GetMapping("/{category}/{id}")
    public String priority4(@PathVariable String category, @PathVariable Long id) {
        return "4: simple";
    }

    // 우선순위 5: 와일드카드
    @GetMapping("/**")
    public String priority5() {
        return "5: catch-all";
    }
}
```

**실무 팁**:

1. **명확한 URL 설계**: 애매한 패턴은 피하기
```java
// ❌ 나쁜 예: 충돌 가능성 높음
@GetMapping("/users/{id}")
@GetMapping("/users/{name}")

// ✅ 좋은 예: 명확한 구분
@GetMapping("/users/{id:\\d+}")         // 숫자만
@GetMapping("/users/by-name/{name}")    // 문자열
```

2. **AmbiguousMappingException 방지**:
```java
// 충돌 발생 시 애플리케이션 시작 실패
// 정확한 매칭과 패턴 매칭을 명확히 분리
```

3. **로깅으로 확인**:
```yaml
logging:
  level:
    org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping: TRACE
```

---

#### Q2. @RequestMapping의 params와 headers 속성을 사용하여 같은 URL에 대해 다른 핸들러를 매핑하는 방법과 실무 활용 사례를 설명해보세요.

**답변**:

params와 headers 속성을 사용하면 **같은 URL이지만 요청 조건에 따라 다른 핸들러**를 호출할 수 있습니다.

**1. params 속성 활용**

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {

    // 조건 1: type=basic
    @GetMapping(params = "type=basic")
    public List<Product> getBasicProducts() {
        return productService.findBasic();
    }

    // 조건 2: type=premium
    @GetMapping(params = "type=premium")
    public List<Product> getPremiumProducts() {
        return productService.findPremium();
    }

    // 조건 3: sort 파라미터가 존재
    @GetMapping(params = "sort")
    public List<Product> getSortedProducts(@RequestParam String sort) {
        return productService.findAllSorted(sort);
    }

    // 조건 4: featured 파라미터가 없는 경우
    @GetMapping(params = "!featured")
    public List<Product> getRegularProducts() {
        return productService.findRegular();
    }

    // 조건 5: 여러 조건 조합
    @GetMapping(params = {"type=advanced", "sort=price"})
    public List<Product> getAdvancedSorted() {
        return productService.findAdvancedSortedByPrice();
    }

    // 기본 핸들러 (조건이 없는 경우)
    @GetMapping
    public List<Product> getAllProducts() {
        return productService.findAll();
    }
}

/*
요청 → 호출되는 핸들러:
GET /api/products?type=basic      → getBasicProducts()
GET /api/products?type=premium    → getPremiumProducts()
GET /api/products?sort=name       → getSortedProducts()
GET /api/products                 → getAllProducts()
GET /api/products?type=advanced&sort=price → getAdvancedSorted()
*/
```

**2. headers 속성 활용**

```java
@RestController
@RequestMapping("/api/data")
public class DataController {

    // JSON 요청
    @PostMapping(headers = "Content-Type=application/json")
    public String handleJson(@RequestBody Map<String, Object> data) {
        return "JSON 데이터 처리";
    }

    // XML 요청
    @PostMapping(headers = "Content-Type=application/xml")
    public String handleXml(@RequestBody String xmlData) {
        return "XML 데이터 처리";
    }

    // 특정 API 키가 있는 경우
    @GetMapping(headers = "X-API-KEY")
    public SecureData getSecureData(@RequestHeader("X-API-KEY") String apiKey) {
        if (apiKeyService.validate(apiKey)) {
            return secureDataService.getData();
        }
        throw new UnauthorizedException();
    }

    // 모바일 클라이언트 전용
    @GetMapping(headers = "User-Agent=Mobile")
    public MobileResponse getMobileData() {
        return dataService.getMobileOptimized();
    }

    // 버전별 처리
    @GetMapping(headers = "API-Version=v1")
    public DataV1 getDataV1() {
        return dataService.getV1();
    }

    @GetMapping(headers = "API-Version=v2")
    public DataV2 getDataV2() {
        return dataService.getV2();
    }
}
```

**3. 실무 활용 사례**

**사례 1: 검색 모드 구분 (네이버 검색)**

```java
@RestController
@RequestMapping("/api/search")
public class NaverSearchController {

    // 통합 검색 (기본)
    @GetMapping
    public SearchResponse unifiedSearch(@RequestParam String query) {
        return searchService.searchAll(query);
    }

    // 블로그 전용 검색
    @GetMapping(params = "mode=blog")
    public BlogSearchResponse blogSearch(@RequestParam String query) {
        return searchService.searchBlogs(query);
    }

    // 이미지 전용 검색
    @GetMapping(params = "mode=image")
    public ImageSearchResponse imageSearch(@RequestParam String query) {
        return searchService.searchImages(query);
    }

    // 뉴스 전용 검색
    @GetMapping(params = "mode=news")
    public NewsSearchResponse newsSearch(
        @RequestParam String query,
        @RequestParam(defaultValue = "recent") String sort
    ) {
        return searchService.searchNews(query, sort);
    }

    // 고급 검색 (여러 필터)
    @GetMapping(params = {"mode=advanced", "filter"})
    public AdvancedSearchResponse advancedSearch(
        @RequestParam String query,
        @RequestParam String filter,
        @RequestParam(required = false) String dateRange
    ) {
        return searchService.advancedSearch(query, filter, dateRange);
    }
}
```

**사례 2: API 버전 관리 (카카오 API)**

```java
@RestController
@RequestMapping("/api/users")
public class KakaoUserApiController {

    // v1 API: 헤더로 버전 구분
    @GetMapping(headers = "API-Version=v1")
    public UserResponseV1 getUserV1(@RequestParam Long id) {
        User user = userService.findById(id);
        return UserResponseV1.builder()
            .id(user.getId())
            .name(user.getName())
            .build();
    }

    // v2 API: 추가 필드 포함
    @GetMapping(headers = "API-Version=v2")
    public UserResponseV2 getUserV2(@RequestParam Long id) {
        User user = userService.findById(id);
        return UserResponseV2.builder()
            .id(user.getId())
            .name(user.getName())
            .email(user.getEmail())  // v2에서 추가
            .profileImage(user.getProfileImage())  // v2에서 추가
            .build();
    }

    // v3 API: 보안 강화
    @GetMapping(headers = {"API-Version=v3", "X-Auth-Token"})
    public UserResponseV3 getUserV3(
        @RequestParam Long id,
        @RequestHeader("X-Auth-Token") String token
    ) {
        authService.validateToken(token);
        User user = userService.findById(id);
        return UserResponseV3.from(user);  // 전체 정보 포함
    }
}
```

**사례 3: A/B 테스트 (쿠팡 상품 추천)**

```java
@RestController
@RequestMapping("/api/recommendations")
public class CoupangRecommendController {

    // A그룹: 기존 알고리즘
    @GetMapping(headers = "X-Experiment-Group=A")
    public List<Product> recommendA(@RequestParam Long userId) {
        return recommendService.legacyAlgorithm(userId);
    }

    // B그룹: 신규 알고리즘
    @GetMapping(headers = "X-Experiment-Group=B")
    public List<Product> recommendB(@RequestParam Long userId) {
        return recommendService.newAlgorithm(userId);
    }

    // 기본: 랜덤 배정
    @GetMapping
    public List<Product> recommend(@RequestParam Long userId) {
        String group = abTestService.assignGroup(userId);
        if ("B".equals(group)) {
            return recommendService.newAlgorithm(userId);
        }
        return recommendService.legacyAlgorithm(userId);
    }
}
```

**사례 4: 클라이언트별 최적화 (배달의민족)**

```java
@RestController
@RequestMapping("/api/stores")
public class BaeminStoreController {

    // 모바일 앱: 경량화된 응답
    @GetMapping(headers = "User-Agent=BaeminApp")
    public MobileStoreResponse getStoresForApp(
        @RequestParam double lat,
        @RequestParam double lng
    ) {
        return storeService.findNearbyLight(lat, lng);
    }

    // 웹: 상세 정보 포함
    @GetMapping(headers = "User-Agent=Mozilla")
    public WebStoreResponse getStoresForWeb(
        @RequestParam double lat,
        @RequestParam double lng
    ) {
        return storeService.findNearbyDetailed(lat, lng);
    }

    // B2B 파트너: 추가 메타데이터
    @GetMapping(headers = {"X-Partner-Key", "X-Partner-Type=B2B"})
    public PartnerStoreResponse getStoresForPartner(
        @RequestParam double lat,
        @RequestParam double lng,
        @RequestHeader("X-Partner-Key") String partnerKey
    ) {
        partnerService.validate(partnerKey);
        return storeService.findNearbyWithMetadata(lat, lng);
    }
}
```

**장점**:
1. **URL 중복 방지**: 같은 URL로 다양한 기능 제공
2. **유연한 API 설계**: 조건에 따라 다른 로직 실행
3. **하위 호환성**: 버전 관리가 용이

**단점**:
1. **복잡도 증가**: 조건이 많아질수록 관리 어려움
2. **테스트 어려움**: 모든 조건 조합을 테스트해야 함
3. **문서화 필요**: API 문서에 조건을 명확히 기재

---

#### Q3. Content Negotiation(내용 협상)이란 무엇이며, Spring에서 어떻게 구현하나요?

**답변**:

**Content Negotiation**은 클라이언트가 원하는 응답 형식(JSON, XML, HTML 등)을 서버에 요청하고, 서버가 그에 맞는 형식으로 응답하는 메커니즘입니다.

**동작 원리**:

```
클라이언트 → Accept 헤더 전송 → 서버
   ↓
Accept: application/json
   ↓
서버 → JSON 형식으로 변환 → 응답
```

**1. Spring에서의 구현 방법**

```java
@RestController
@RequestMapping("/api/users")
public class UserContentNegotiationController {

    // 방법 1: produces 속성 사용
    @GetMapping(
        value = "/{id}",
        produces = {
            MediaType.APPLICATION_JSON_VALUE,
            MediaType.APPLICATION_XML_VALUE
        }
    )
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
    }
    /*
    요청 헤더 → 응답 형식:
    Accept: application/json → JSON 반환
    Accept: application/xml  → XML 반환
    Accept: * /*             → 기본값 (JSON)
    */

    // 방법 2: ResponseEntity 사용
    @GetMapping("/{id}/flexible")
    public ResponseEntity<User> getUserFlexible(
        @PathVariable Long id,
        @RequestHeader("Accept") String accept
    ) {
        User user = userService.findById(id);

        if (accept.contains("xml")) {
            return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_XML)
                .body(user);
        } else {
            return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_JSON)
                .body(user);
        }
    }
}
```

**2. XML 지원 설정**

```xml
<!-- pom.xml -->
<dependencies>
    <!-- Jackson XML 지원 -->
    <dependency>
        <groupId>com.fasterxml.jackson.dataformat</groupId>
        <artifactId>jackson-dataformat-xml</artifactId>
    </dependency>
</dependencies>
```

```java
// DTO에 JAXB 어노테이션 추가
@Data
@XmlRootElement(name = "user")
@XmlAccessorType(XmlAccessType.FIELD)
public class User {
    @XmlElement
    private Long id;

    @XmlElement
    private String name;

    @XmlElement
    private String email;
}
```

**3. 다양한 형식 지원**

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {

    // JSON, XML, CSV 지원
    @GetMapping(
        value = "/{id}",
        produces = {
            MediaType.APPLICATION_JSON_VALUE,
            MediaType.APPLICATION_XML_VALUE,
            "text/csv"
        }
    )
    public ResponseEntity<?> getProduct(
        @PathVariable Long id,
        @RequestHeader(value = "Accept", defaultValue = "application/json") String accept
    ) {
        Product product = productService.findById(id);

        if (accept.contains("xml")) {
            return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_XML)
                .body(product);
        } else if (accept.contains("csv")) {
            String csv = convertToCsv(product);
            return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType("text/csv"))
                .header("Content-Disposition", "attachment; filename=product.csv")
                .body(csv);
        } else {
            return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_JSON)
                .body(product);
        }
    }

    private String convertToCsv(Product product) {
        return String.format("%d,%s,%.2f",
            product.getId(),
            product.getName(),
            product.getPrice()
        );
    }
}
```

**4. URL 기반 협상 (쿼리 파라미터)**

```java
// application.yml
spring:
  mvc:
    contentnegotiation:
      favor-parameter: true  // 쿼리 파라미터 활성화
      parameter-name: format  // ?format=json

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void configureContentNegotiation(ContentNegotiationConfigurer configurer) {
        configurer
            .favorParameter(true)  // 쿼리 파라미터 우선
            .parameterName("format")
            .ignoreAcceptHeader(false)  // Accept 헤더도 사용
            .defaultContentType(MediaType.APPLICATION_JSON)
            .mediaType("json", MediaType.APPLICATION_JSON)
            .mediaType("xml", MediaType.APPLICATION_XML);
    }
}

// 사용 예시:
// GET /api/users/123?format=json → JSON 반환
// GET /api/users/123?format=xml  → XML 반환
```

**5. 실무 사례: 다국어 지원 + Content Negotiation**

```java
@RestController
@RequestMapping("/api/articles")
public class ArticleController {

    @GetMapping("/{id}")
    public ResponseEntity<ArticleResponse> getArticle(
        @PathVariable Long id,
        @RequestHeader(value = "Accept-Language", defaultValue = "ko") String language,
        @RequestHeader(value = "Accept", defaultValue = "application/json") String accept
    ) {
        Article article = articleService.findById(id);

        // 언어에 따라 번역
        ArticleResponse response;
        if (language.startsWith("en")) {
            response = ArticleResponse.fromEnglish(article);
        } else {
            response = ArticleResponse.fromKorean(article);
        }

        // 형식에 따라 변환
        if (accept.contains("xml")) {
            return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_XML)
                .body(response);
        } else {
            return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_JSON)
                .body(response);
        }
    }
}

/*
요청 예시:
GET /api/articles/123
Accept: application/json
Accept-Language: en
→ 영어 JSON 응답

GET /api/articles/123
Accept: application/xml
Accept-Language: ko
→ 한국어 XML 응답
*/
```

**6. 커스텀 메시지 컨버터**

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void configureMessageConverters(List<HttpMessageConverter<?>> converters) {
        // CSV 컨버터 추가
        converters.add(new CsvHttpMessageConverter());
    }
}

public class CsvHttpMessageConverter extends AbstractHttpMessageConverter<Product> {

    public CsvHttpMessageConverter() {
        super(new MediaType("text", "csv"));
    }

    @Override
    protected boolean supports(Class<?> clazz) {
        return Product.class.isAssignableFrom(clazz);
    }

    @Override
    protected Product readInternal(Class<? extends Product> clazz, HttpInputMessage inputMessage) {
        // CSV → Product 변환 로직
        return null;
    }

    @Override
    protected void writeInternal(Product product, HttpOutputMessage outputMessage) throws IOException {
        // Product → CSV 변환 로직
        String csv = String.format("%d,%s,%.2f",
            product.getId(),
            product.getName(),
            product.getPrice()
        );
        outputMessage.getBody().write(csv.getBytes());
    }
}
```

**정리**:

```
┌─────────────────────┬──────────────────────────────────┐
│ 협상 방식           │ 예시                              │
├─────────────────────┼──────────────────────────────────┤
│ Accept 헤더 (기본)  │ Accept: application/json         │
│ 쿼리 파라미터       │ ?format=json                     │
│ URL 확장자          │ /users/123.json (비권장)         │
│ 커스텀 헤더         │ X-Response-Format: json          │
└─────────────────────┴──────────────────────────────────┘
```

**실무 팁**:
1. **기본 형식 지정**: JSON을 기본으로
2. **에러 처리**: 지원하지 않는 형식 요청 시 406 반환
3. **버전 관리**: API 버전별로 다른 형식 지원 가능
4. **성능**: XML보다 JSON이 경량이므로 기본 권장

---

#### Q4. RESTful API 버전 관리 전략(URI versioning, Header versioning 등)에 대해 설명하고, 각각의 장단점을 말해보세요.

**답변**:

RESTful API 버전 관리는 **하위 호환성 유지**와 **API 진화**를 위해 필수적입니다. 주요 전략은 4가지입니다.

**1. URI 버전 관리 (가장 일반적)**

```java
// v1 API
@RestController
@RequestMapping("/api/v1/users")
public class UserControllerV1 {

    @GetMapping("/{id}")
    public UserV1 getUser(@PathVariable Long id) {
        return userService.findByIdV1(id);
    }
}

// v2 API
@RestController
@RequestMapping("/api/v2/users")
public class UserControllerV2 {

    @GetMapping("/{id}")
    public UserV2 getUser(@PathVariable Long id) {
        return userService.findByIdV2(id);
    }
}

/*
호출:
GET /api/v1/users/123 → v1 응답
GET /api/v2/users/123 → v2 응답
*/
```

**장점**:
- 명확하고 이해하기 쉬움
- 브라우저에서 직접 테스트 가능
- 문서화 용이
- 캐싱 전략 적용 쉬움

**단점**:
- URL이 길어짐
- REST 원칙 위배 (리소스가 아닌 버전이 URL에 포함)
- 버전별로 컨트롤러 클래스 분리 필요

---

**2. Header 버전 관리 (REST 원칙 준수)**

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    // v1
    @GetMapping(value = "/{id}", headers = "API-Version=1")
    public UserV1 getUserV1(@PathVariable Long id) {
        return userService.findByIdV1(id);
    }

    // v2
    @GetMapping(value = "/{id}", headers = "API-Version=2")
    public UserV2 getUserV2(@PathVariable Long id) {
        return userService.findByIdV2(id);
    }
}

/*
호출:
GET /api/users/123
Headers: API-Version: 1
→ v1 응답

GET /api/users/123
Headers: API-Version: 2
→ v2 응답
*/
```

**장점**:
- RESTful 원칙 준수 (URL은 리소스만 표현)
- URL이 깔끔함
- 같은 컨트롤러에서 관리 가능

**단점**:
- 브라우저에서 테스트 어려움
- 클라이언트가 헤더를 설정해야 함
- 문서화가 복잡함

---

**3. Accept 헤더 버전 관리 (Content Negotiation)**

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    // v1
    @GetMapping(
        value = "/{id}",
        produces = "application/vnd.company.v1+json"
    )
    public UserV1 getUserV1(@PathVariable Long id) {
        return userService.findByIdV1(id);
    }

    // v2
    @GetMapping(
        value = "/{id}",
        produces = "application/vnd.company.v2+json"
    )
    public UserV2 getUserV2(@PathVariable Long id) {
        return userService.findByIdV2(id);
    }
}

/*
호출:
GET /api/users/123
Accept: application/vnd.company.v1+json
→ v1 응답

GET /api/users/123
Accept: application/vnd.company.v2+json
→ v2 응답
*/
```

**장점**:
- HTTP 표준에 가장 부합
- Content Negotiation 활용
- 버전 + 형식을 동시에 지정 가능

**단점**:
- Accept 헤더 형식이 복잡함
- 클라이언트 구현이 까다로움
- 디버깅 어려움

---

**4. 쿼리 파라미터 버전 관리**

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping("/{id}")
    public ResponseEntity<?> getUser(
        @PathVariable Long id,
        @RequestParam(defaultValue = "1") int version
    ) {
        if (version == 2) {
            return ResponseEntity.ok(userService.findByIdV2(id));
        } else {
            return ResponseEntity.ok(userService.findByIdV1(id));
        }
    }
}

/*
호출:
GET /api/users/123?version=1 → v1 응답
GET /api/users/123?version=2 → v2 응답
GET /api/users/123           → v1 응답 (기본값)
*/
```

**장점**:
- 구현이 간단함
- 브라우저에서 테스트 용이
- 기본 버전 설정 가능

**단점**:
- REST 원칙 위배
- 쿼리 파라미터가 많아지면 복잡함
- 캐싱 전략 적용 어려움

---

**비교표**:

```
┌────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│ 전략       │ URI         │ Header      │ Accept      │ Query Param │
├────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ 명확성     │ ★★★★★      │ ★★★☆☆      │ ★★☆☆☆      │ ★★★★☆      │
│ REST 준수  │ ★★☆☆☆      │ ★★★★☆      │ ★★★★★      │ ★★☆☆☆      │
│ 구현 용이  │ ★★★★☆      │ ★★★☆☆      │ ★★☆☆☆      │ ★★★★★      │
│ 테스트     │ ★★★★★      │ ★★★☆☆      │ ★★☆☆☆      │ ★★★★★      │
│ 문서화     │ ★★★★★      │ ★★★☆☆      │ ★★☆☆☆      │ ★★★★☆      │
│ 캐싱       │ ★★★★★      │ ★★★☆☆      │ ★★★☆☆      │ ★★☆☆☆      │
└────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

---

**실무 권장 사항**:

```java
// ✅ 추천: URI 버전 관리 (대부분의 경우)
// 이유: 명확성, 테스트 용이, 문서화 간편

@RestController
@RequestMapping("/api/v1/users")
public class UserControllerV1 { }

@RestController
@RequestMapping("/api/v2/users")
public class UserControllerV2 { }

// ✅ 추천: 공통 인터페이스로 코드 재사용
public interface UserService {
    UserDTO findById(Long id);
}

@Service
public class UserServiceV1 implements UserService {
    public UserDTO findById(Long id) {
        // v1 로직
    }
}

@Service
public class UserServiceV2 implements UserService {
    public UserDTO findById(Long id) {
        // v2 로직 (v1 로직 재사용 + 추가 기능)
    }
}
```

---

**주요 회사들의 실제 전략**:

```
┌──────────┬─────────────────┬──────────────────────┐
│ 회사     │ 전략            │ 예시                  │
├──────────┼─────────────────┼──────────────────────┤
│ Twitter  │ URI             │ /1.1/users/show.json │
│ GitHub   │ Header + Accept │ Accept: v3+json      │
│ Stripe   │ Header          │ Stripe-Version: 2023 │
│ Google   │ URI             │ /v1/users            │
│ Facebook │ URI             │ /v12.0/me            │
└──────────┴─────────────────┴──────────────────────┘
```

---

#### Q5. @PathVariable에서 정규표현식을 사용하는 방법과 실무에서의 활용 사례를 설명해보세요.

**답변**:

@PathVariable에서 **정규표현식을 사용하면 경로 변수의 형식을 제한**할 수 있습니다.

**기본 문법**:

```java
@GetMapping("/{variable:정규표현식}")
public String method(@PathVariable String variable) { }
```

**1. 숫자만 허용 (ID 값)**

```java
@RestController
@RequestMapping("/api")
public class RegexController {

    // 숫자만 허용
    @GetMapping("/users/{id:\\d+}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
    }

    // 문자만 허용
    @GetMapping("/users/by-name/{name:[a-zA-Z]+}")
    public User getUserByName(@PathVariable String name) {
        return userService.findByName(name);
    }

    /*
    결과:
    GET /api/users/123      → getUser() 호출 (숫자)
    GET /api/users/john     → getUserByName() 호출 (문자)
    GET /api/users/john123  → 404 (어느 쪽도 매칭 안 됨)
    */
}
```

**2. 날짜 형식 검증**

```java
@RestController
@RequestMapping("/api/reports")
public class ReportController {

    // YYYY-MM-DD 형식만 허용
    @GetMapping("/{date:\\d{4}-\\d{2}-\\d{2}}")
    public DailyReport getReport(@PathVariable String date) {
        LocalDate localDate = LocalDate.parse(date);
        return reportService.getReportByDate(localDate);
    }

    // YYYY/MM 형식 (월별 리포트)
    @GetMapping("/{yearMonth:\\d{4}/\\d{2}}")
    public MonthlyReport getMonthlyReport(@PathVariable String yearMonth) {
        YearMonth ym = YearMonth.parse(yearMonth, DateTimeFormatter.ofPattern("yyyy/MM"));
        return reportService.getMonthlyReport(ym);
    }

    /*
    결과:
    GET /api/reports/2024-10-15  → getReport() 호출
    GET /api/reports/2024/10     → getMonthlyReport() 호출
    GET /api/reports/2024-1-5    → 404 (형식 불일치)
    */
}
```

**3. 이메일 형식 검증**

```java
@RestController
@RequestMapping("/api/users")
public class UserEmailController {

    // 이메일 형식
    @GetMapping("/by-email/{email:[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}}")
    public User getUserByEmail(@PathVariable String email) {
        return userService.findByEmail(email);
    }

    /*
    결과:
    GET /api/users/by-email/john@example.com  → 호출 성공
    GET /api/users/by-email/john              → 404 (이메일 형식 아님)
    */
}
```

**4. 파일 확장자 제한**

```java
@RestController
@RequestMapping("/api/files")
public class FileController {

    // 이미지 파일만 허용 (jpg, png, gif)
    @GetMapping("/{filename:.+\\.(jpg|png|gif)}")
    public ResponseEntity<byte[]> getImage(@PathVariable String filename) {
        byte[] image = fileService.loadImage(filename);
        return ResponseEntity.ok()
            .contentType(MediaType.IMAGE_JPEG)
            .body(image);
    }

    // PDF 파일만 허용
    @GetMapping("/documents/{filename:.+\\.pdf}")
    public ResponseEntity<byte[]> getPdf(@PathVariable String filename) {
        byte[] pdf = fileService.loadPdf(filename);
        return ResponseEntity.ok()
            .contentType(MediaType.APPLICATION_PDF)
            .body(pdf);
    }

    /*
    결과:
    GET /api/files/photo.jpg       → getImage() 호출
    GET /api/files/report.pdf      → getPdf() 호출
    GET /api/files/document.docx   → 404 (매칭 없음)
    */
}
```

**5. UUID 형식 검증**

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    // UUID 형식 (8-4-4-4-12)
    @GetMapping("/{orderId:[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}}")
    public Order getOrder(@PathVariable String orderId) {
        UUID uuid = UUID.fromString(orderId);
        return orderService.findByUuid(uuid);
    }

    /*
    결과:
    GET /api/orders/550e8400-e29b-41d4-a716-446655440000  → 성공
    GET /api/orders/123                                    → 404
    */
}
```

**6. 실무 활용 사례: 충돌 방지**

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {

    // 숫자 ID
    @GetMapping("/{id:\\d+}")
    public Product getById(@PathVariable Long id) {
        return productService.findById(id);
    }

    // 문자열 슬러그 (URL 친화적 이름)
    @GetMapping("/{slug:[a-z0-9-]+}")
    public Product getBySlug(@PathVariable String slug) {
        return productService.findBySlug(slug);
    }

    // 특별한 액션 (정확한 매칭)
    @GetMapping("/featured")
    public List<Product> getFeatured() {
        return productService.findFeatured();
    }

    /*
    결과:
    GET /api/products/123           → getById(123)
    GET /api/products/macbook-pro   → getBySlug("macbook-pro")
    GET /api/products/featured      → getFeatured()
    */
}
```

**7. 복합 정규표현식**

```java
@RestController
@RequestMapping("/api/archive")
public class ArchiveController {

    // 연도/월/일/파일명 형식
    @GetMapping("/{year:\\d{4}}/{month:\\d{2}}/{day:\\d{2}}/{filename:.+}")
    public ResponseEntity<byte[]> getArchivedFile(
        @PathVariable int year,
        @PathVariable int month,
        @PathVariable int day,
        @PathVariable String filename
    ) {
        LocalDate date = LocalDate.of(year, month, day);
        byte[] file = archiveService.getFile(date, filename);
        return ResponseEntity.ok(file);
    }

    /*
    GET /api/archive/2024/10/15/report.pdf
    → year=2024, month=10, day=15, filename=report.pdf
    */
}
```

**정규표현식 패턴 모음**:

```java
/*
┌───────────────┬────────────────────────────┬─────────────────┐
│ 패턴          │ 정규표현식                  │ 예시            │
├───────────────┼────────────────────────────┼─────────────────┤
│ 숫자만        │ \\d+                       │ 123             │
│ 문자만        │ [a-zA-Z]+                  │ John            │
│ 영숫자        │ [a-zA-Z0-9]+               │ user123         │
│ 날짜(YYYYMMDD)│ \\d{4}-\\d{2}-\\d{2}       │ 2024-10-15      │
│ 이메일        │ [^@]+@[^@]+\\.[^@]+        │ test@email.com  │
│ UUID          │ [a-f0-9-]{36}              │ 550e8400-e29b...│
│ IP 주소       │ \\d{1,3}(\\.\\d{1,3}){3}   │ 192.168.1.1     │
│ 전화번호      │ \\d{2,3}-\\d{3,4}-\\d{4}   │ 010-1234-5678   │
└───────────────┴────────────────────────────┴─────────────────┘
*/
```

**주의사항**:

1. **역슬래시 이스케이프**: Java 문자열에서 `\\d`로 작성
2. **복잡도 제한**: 너무 복잡한 정규표현식은 피하기
3. **검증 분리**: 형식 검증은 @Valid와 Bean Validation 사용 권장

```java
// ✅ 권장: 정규표현식 + Bean Validation 조합
@GetMapping("/{date:\\d{4}-\\d{2}-\\d{2}}")
public DailyReport getReport(
    @PathVariable @DateTimeFormat(pattern = "yyyy-MM-dd") LocalDate date
) {
    return reportService.getReport(date);
}
```

---

## 📝 핵심 정리

### @RequestMapping 주요 속성

| 속성 | 설명 | 예시 |
|------|------|------|
| value/path | URL 패턴 지정 | `@GetMapping("/users/{id}")` |
| method | HTTP 메서드 지정 | `method = RequestMethod.GET` |
| params | 파라미터 조건 | `params = "type=user"` |
| headers | 헤더 조건 | `headers = "Content-Type=application/json"` |
| consumes | 요청 Content-Type | `consumes = "application/json"` |
| produces | 응답 Content-Type | `produces = "application/json"` |

### HTTP 메서드별 사용 목적

| 메서드 | 목적 | 예시 URL | 특징 |
|--------|------|----------|------|
| GET | 조회 | `/users`, `/users/123` | 안전, 멱등성 |
| POST | 생성 | `/users` | 비멱등성 |
| PUT | 전체 수정 | `/users/123` | 멱등성 |
| PATCH | 부분 수정 | `/users/123` | 비멱등성 |
| DELETE | 삭제 | `/users/123` | 멱등성 |

### 파라미터 바인딩 어노테이션

| 어노테이션 | 용도 | 예시 |
|-----------|------|------|
| `@PathVariable` | URL 경로 변수 | `/users/{id}` |
| `@RequestParam` | 쿼리 파라미터 | `?name=John&age=25` |
| `@RequestBody` | HTTP Body (JSON/XML) | POST/PUT 요청의 본문 |
| `@RequestHeader` | HTTP 헤더 | `Authorization: Bearer token` |
| `@CookieValue` | 쿠키 값 | `JSESSIONID=...` |

---

## 🚀 다음 단계

### 다음 장 미리보기: 12장-2: 컨트롤러와 요청 매핑 - 고급

**배울 내용:**
- **@ModelAttribute**: 폼 데이터 자동 바인딩
- **@SessionAttributes**: 세션 관리
- **@InitBinder**: 데이터 변환 커스터마이징
- **파일 업로드**: MultipartFile 처리
- **비동기 요청**: @Async, DeferredResult
- **실전 프로젝트**: 파일 업로드 게시판

---

**다음 장으로 이동**: [다음: 12장-2: 고급 매핑 →](SpringMVC-Part4-12-2-Controller-Advanced.md)

**이전 장으로 돌아가기**: [← 이전: 11장-2: 설정과 실습](SpringMVC-Part2-11-2-Overview-Practice.md)

**목차로 돌아가기**: [📚 전체 목차](README.md)
