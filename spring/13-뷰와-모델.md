# 13장: 뷰와 모델

> **학습 목표**: ViewResolver, 다양한 View 기술(JSP, Thymeleaf), Model 데이터 전달 방법을 이해하고 활용할 수 있습니다.

**⏱️ 예상 학습 시간**: 2-3시간
**난이도**: ⭐⭐⭐☆☆ (3개/5개)

---

## 💡 왜 뷰와 모델을 분리해야 하는가?

### 문제 상황: JSP에 모든 것을 넣었을 때

```jsp
<%@ page import="java.sql.*" %>
<%
    // ❌ JSP에서 DB 접속
    Connection conn = DriverManager.getConnection("jdbc:mysql://localhost/mydb", "user", "pass");
    Statement stmt = conn.createStatement();
    ResultSet rs = stmt.executeQuery("SELECT * FROM users");
%>

<html>
<body>
    <h1>사용자 목록</h1>
    <table>
    <%
        // ❌ JSP에서 비즈니스 로직
        while (rs.next()) {
            String name = rs.getString("name");
            String email = rs.getString("email");

            // ❌ JSP에서 검증 로직
            if (name != null && !name.isEmpty()) {
    %>
        <tr>
            <td><%= name %></td>
            <td><%= email %></td>
        </tr>
    <%
            }
        }
    %>
    </table>
</body>
</html>
```

**문제점**:
1. **유지보수 지옥**: 디자이너가 HTML 수정 시 Java 코드 건드림 → 버그 발생
2. **테스트 불가**: JSP는 브라우저 없이 단독 실행 불가
3. **재사용 불가**: 같은 데이터를 JSON으로 보내려면 코드 전체 복사
4. **책임 혼재**: DB, 비즈니스 로직, 화면이 한 곳에

### 해결책: View와 Model 분리

```java
// Controller: 흐름 제어
@Controller
public class UserController {

    @Autowired
    private UserService userService;  // 비즈니스 로직

    @GetMapping("/users")
    public String list(Model model) {
        List<User> users = userService.findAll();  // 데이터 조회
        model.addAttribute("users", users);  // Model에 데이터 전달
        return "users/list";  // View 이름 반환
    }
}
```

```html
<!-- View: 순수 HTML (Thymeleaf) -->
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<body>
    <h1>사용자 목록</h1>
    <table>
        <tr th:each="user : ${users}">
            <td th:text="${user.name}">이름</td>
            <td th:text="${user.email}">이메일</td>
        </tr>
    </table>
</body>
</html>
```

**장점**:
1. **역할 분리**: Controller (흐름) / Service (비즈니스 로직) / View (화면)
2. **테스트 용이**: Controller는 단위 테스트, View는 브라우저 직접 열기 가능
3. **재사용**: 같은 데이터를 JSON, XML, Excel, PDF 등 다양한 형식으로 제공 가능
4. **협업**: 개발자는 Controller, 디자이너는 View만 수정

---

## 🎯 실생활 비유로 이해하기

### 비유 1: 레스토랑 주문 시스템

**상황**: 손님이 "스테이크 미디엄"을 주문

```
┌─────────────┬─────────────────┬──────────────────┐
│ 실제        │ Spring MVC      │ 역할             │
├─────────────┼─────────────────┼──────────────────┤
│ 웨이터      │ Controller      │ 주문 받아 전달   │
│ 주방        │ Service         │ 요리 (비즈니스)  │
│ 요리(음식)  │ Model (데이터)  │ 완성된 음식      │
│ 접시/플레이팅│ View           │ 예쁘게 담기      │
│ 손님에게 제공│ ViewResolver    │ 적절한 형태 선택 │
└─────────────┴─────────────────┴──────────────────┘
```

**흐름**:
1. **웨이터(Controller)**: "스테이크 미디엄 주문이요!"
2. **주방(Service)**: 스테이크를 미디엄으로 조리
3. **요리(Model)**: 완성된 스테이크
4. **접시(View)**: 스테이크를 예쁜 접시에 담기
5. **손님에게**: 멋지게 플레이팅된 스테이크 제공

**왜 분리?**
- 주방장이 직접 서빙하지 않음 (역할 분리)
- 같은 스테이크를 접시/도시락/샌드위치 등 다양하게 제공 가능 (View 다양화)
- 웨이터는 조리법 몰라도 됨 (관심사 분리)

**코드로 보면**:
```java
@Controller
public class OrderController {  // 웨이터

    @GetMapping("/order/steak")
    public String orderSteak(Model model) {
        Steak steak = kitchen.cook("medium");  // 주방에서 조리
        model.addAttribute("steak", steak);    // 접시에 담기
        return "steak/plate";  // 접시 선택
    }
}
```

---

### 비유 2: 택배 배송 시스템

**상황**: 온라인 쇼핑몰에서 물건 주문

```
┌──────────────┬─────────────────┬──────────────────┐
│ 택배 시스템  │ Spring MVC      │ 역할             │
├──────────────┼─────────────────┼──────────────────┤
│ 고객 주문    │ Controller      │ 요청 받기        │
│ 창고/재고    │ Service         │ 물건 준비        │
│ 물건         │ Model (데이터)  │ 배송할 상품      │
│ 포장/박스    │ View            │ 예쁘게 포장      │
│ 배송 방법    │ ViewResolver    │ 택배/직접배송 선택│
└──────────────┴─────────────────┴──────────────────┘
```

**예시**:
- **Model (물건)**: 노트북 (같은 제품)
- **View (포장)**:
  - 일반 배송: 박스에 담아서
  - 선물 포장: 리본 + 카드 + 고급 포장지
  - 해외 배송: 방수 포장 + 영문 라벨

```java
@Controller
public class ProductController {

    @GetMapping("/product/{id}")
    public String getProduct(@PathVariable Long id, Model model,
                            @RequestParam(defaultValue = "standard") String packaging) {
        Product product = productService.findById(id);  // 물건 준비
        model.addAttribute("product", product);

        // 포장 방법 선택
        if ("gift".equals(packaging)) {
            return "product/gift";  // 선물 포장
        } else if ("international".equals(packaging)) {
            return "product/international";  // 해외 배송용
        } else {
            return "product/standard";  // 일반 포장
        }
    }
}
```

---

### 비유 3: 도서관 대출 시스템

**상황**: 책을 빌리러 간 상황

```
┌──────────────┬─────────────────┬──────────────────┐
│ 도서관       │ Spring MVC      │ 역할             │
├──────────────┼─────────────────┼──────────────────┤
│ 사서         │ Controller      │ 요청 처리        │
│ 서가/검색    │ Service         │ 책 찾기          │
│ 책           │ Model (데이터)  │ 대출할 도서      │
│ 대출증/영수증│ View            │ 정보 표시        │
│ 출력 형식    │ ViewResolver    │ 종이/모바일 선택 │
└──────────────┴─────────────────┴──────────────────┘
```

**시나리오**:
1. "스프링 부트 책 찾아주세요" (요청)
2. 사서가 시스템에서 검색 (Controller)
3. 서가에서 책 찾기 (Service)
4. 책을 카운터로 가져옴 (Model)
5. 대출증을 프린터로 출력 or 모바일 앱으로 전송 (View/ViewResolver)

```java
@Controller
public class LibraryController {

    @GetMapping("/books/{isbn}")
    public String borrowBook(@PathVariable String isbn, Model model,
                            @RequestHeader("User-Agent") String userAgent) {
        Book book = libraryService.findByIsbn(isbn);  // 책 찾기
        model.addAttribute("book", book);

        // 모바일이면 앱용 화면, PC면 프린터 출력용
        if (userAgent.contains("Mobile")) {
            return "books/mobile";  // 모바일 화면
        } else {
            return "books/print";  // 프린터 출력용
        }
    }
}
```

---

### 비유 4: TV 방송국

**상황**: TV 프로그램 제작 및 방송

```
┌──────────────┬─────────────────┬──────────────────┐
│ TV 방송      │ Spring MVC      │ 역할             │
├──────────────┼─────────────────┼──────────────────┤
│ PD           │ Controller      │ 프로그램 기획    │
│ 취재팀       │ Service         │ 자료 수집        │
│ 영상/자료    │ Model (데이터)  │ 방송 소스        │
│ 편집/자막    │ View            │ 시청자용 편집    │
│ 방송 채널    │ ViewResolver    │ TV/유튜브/라디오 │
└──────────────┴─────────────────┴──────────────────┘
```

**예시**: 뉴스 프로그램
- **Model (영상 자료)**: 인터뷰, 현장 영상
- **View (편집)**:
  - TV 방송: 자막 + 효과음 + 앵커 멘트
  - 유튜브: 짧게 편집 + 썸네일
  - 라디오: 음성만 발췌

```java
@Controller
public class NewsController {

    @GetMapping("/news/{id}")
    public String getNews(@PathVariable Long id, Model model,
                         @RequestParam String channel) {
        NewsContent content = newsService.getContent(id);  // 취재 자료
        model.addAttribute("news", content);

        // 채널별로 다른 View
        switch (channel) {
            case "tv": return "news/tv";  // TV 방송용
            case "youtube": return "news/youtube";  // 유튜브용
            case "radio": return "news/radio";  // 라디오용
            default: return "news/web";  // 웹사이트용
        }
    }
}
```

---

### 비유 5: 병원 진료 시스템

**상황**: 환자가 병원에서 진료받는 과정

```
┌──────────────┬─────────────────┬──────────────────┐
│ 병원         │ Spring MVC      │ 역할             │
├──────────────┼─────────────────┼──────────────────┤
│ 접수 직원    │ Controller      │ 환자 접수        │
│ 의사         │ Service         │ 진단/치료        │
│ 진단 결과    │ Model (데이터)  │ 검사 수치 등     │
│ 처방전/진단서│ View            │ 결과 전달 형식   │
│ 출력 방식    │ ViewResolver    │ 종이/모바일/이메일│
└──────────────┴─────────────────┴──────────────────┘
```

**시나리오**:
1. 환자가 "건강검진 결과 확인"
2. 접수 직원이 차트 확인 (Controller)
3. 의사가 검진 결과 해석 (Service)
4. 검사 수치, 진단 결과 (Model)
5. 결과지 출력 형식 선택 (View):
   - 병원용: 상세한 의학 용어
   - 환자용: 쉬운 설명 + 그래프
   - 보험사용: 공식 양식

```java
@Controller
public class MedicalController {

    @GetMapping("/checkup/{patientId}")
    public String getCheckupResult(@PathVariable Long patientId, Model model,
                                  @RequestParam String format) {
        CheckupResult result = medicalService.getResult(patientId);  // 검진 결과
        model.addAttribute("result", result);

        // 용도별로 다른 View
        switch (format) {
            case "medical": return "checkup/medical";  // 의료진용 (전문 용어)
            case "patient": return "checkup/patient";  // 환자용 (쉬운 설명)
            case "insurance": return "checkup/insurance";  // 보험사용 (공식 양식)
            default: return "checkup/summary";  // 요약본
        }
    }
}
```

---

### 🔄 종합 비교표

```
┌─────────────┬──────────────┬──────────────┬──────────────┐
│ 비유        │ Model        │ View         │ ViewResolver │
├─────────────┼──────────────┼──────────────┼──────────────┤
│ 레스토랑    │ 조리된 음식  │ 플레이팅     │ 접시 종류    │
│ 택배        │ 물건         │ 포장         │ 배송 방법    │
│ 도서관      │ 책           │ 대출증       │ 종이/모바일  │
│ TV 방송     │ 영상 자료    │ 편집         │ 방송 채널    │
│ 병원        │ 진단 결과    │ 결과지       │ 용도별 양식  │
└─────────────┴──────────────┴──────────────┴──────────────┘
```

**핵심 인사이트**:
1. **Model은 불변**: 같은 데이터 (음식, 물건, 책, 영상, 진단 결과)
2. **View는 가변**: 다양한 형태로 표현 (포장, 편집, 양식)
3. **ViewResolver는 선택**: 상황에 맞는 View 자동 선택

---

## 📚 목차
- [핵심 개념](#핵심-개념)
- [기본 실습](#기본-실습)
- [실무 활용](#실무-활용)
- [FAQ](#faq)
- [면접 질문](#면접-질문)
- [핵심 정리](#핵심-정리)

---

## 📖 핵심 개념

### 1. ViewResolver 종류

#### InternalResourceViewResolver (JSP)

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Bean
    public InternalResourceViewResolver viewResolver() {
        InternalResourceViewViewResolver resolver = new InternalResourceViewResolver();
        resolver.setPrefix("/WEB-INF/views/");
        resolver.setSuffix(".jsp");
        resolver.setViewClass(JstlView.class);
        return resolver;
    }
}

// Controller에서 "home" 반환 → /WEB-INF/views/home.jsp로 해석
```

#### ThymeleafViewResolver

```java
@Configuration
public class ThymeleafConfig {

    @Bean
    public SpringTemplateEngine templateEngine() {
        SpringTemplateEngine engine = new SpringTemplateEngine();
        engine.setTemplateResolver(templateResolver());
        return engine;
    }

    @Bean
    public SpringResourceTemplateResolver templateResolver() {
        SpringResourceTemplateResolver resolver = new SpringResourceTemplateResolver();
        resolver.setPrefix("classpath:/templates/");
        resolver.setSuffix(".html");
        resolver.setTemplateMode(TemplateMode.HTML);
        resolver.setCharacterEncoding("UTF-8");
        resolver.setCacheable(false);  // 개발 시에는 false
        return resolver;
    }

    @Bean
    public ThymeleafViewResolver thymeleafViewResolver() {
        ThymeleafViewResolver resolver = new ThymeleafViewResolver();
        resolver.setTemplateEngine(templateEngine());
        resolver.setCharacterEncoding("UTF-8");
        return resolver;
    }
}
```

#### BeanNameViewResolver

```java
@Configuration
public class ViewConfig {

    // 커스텀 View를 Bean으로 등록
    @Bean
    public View excelView() {
        return new ExcelView();
    }

    @Bean
    public View pdfView() {
        return new PdfView();
    }

    @Bean
    public BeanNameViewResolver beanNameViewResolver() {
        BeanNameViewResolver resolver = new BeanNameViewResolver();
        resolver.setOrder(1);  // 우선순위 설정
        return resolver;
    }
}

@Controller
public class ReportController {

    @GetMapping("/report/excel")
    public String excelReport(Model model) {
        model.addAttribute("data", reportService.getData());
        return "excelView";  // Bean 이름으로 View 찾기
    }

    @GetMapping("/report/pdf")
    public String pdfReport(Model model) {
        model.addAttribute("data", reportService.getData());
        return "pdfView";
    }
}
```

### 2. Model 데이터 전달

#### Model 인터페이스

```java
@Controller
@RequestMapping("/users")
public class UserController {

    // 1. Model 사용
    @GetMapping("/{id}")
    public String getUser(@PathVariable Long id, Model model) {
        User user = userService.findById(id);
        model.addAttribute("user", user);
        model.addAttribute("pageTitle", "사용자 상세");
        return "users/detail";
    }

    // 2. ModelMap 사용 (Map 기능 추가)
    @GetMapping("/list")
    public String list(ModelMap model) {
        List<User> users = userService.findAll();
        model.addAttribute("users", users);
        model.put("total", users.size());  // Map처럼 사용
        return "users/list";
    }

    // 3. Map 직접 사용
    @GetMapping("/search")
    public String search(@RequestParam String keyword, Map<String, Object> model) {
        List<User> results = userService.search(keyword);
        model.put("results", results);
        model.put("keyword", keyword);
        return "users/search";
    }

    // 4. ModelAndView 사용
    @GetMapping("/stats")
    public ModelAndView stats() {
        ModelAndView mav = new ModelAndView("users/stats");
        mav.addObject("totalUsers", userService.count());
        mav.addObject("activeUsers", userService.countActive());
        return mav;
    }
}
```

#### @ModelAttribute 메서드 레벨

```java
@Controller
@RequestMapping("/products")
public class ProductController {

    // 모든 핸들러 메서드 실행 전 자동 실행
    @ModelAttribute("categories")
    public List<Category> categories() {
        return categoryService.findAll();
    }

    @ModelAttribute("brands")
    public List<Brand> brands() {
        return brandService.findAll();
    }

    // 모든 메서드에서 categories, brands 사용 가능
    @GetMapping("/new")
    public String newForm(Model model) {
        model.addAttribute("product", new Product());
        // categories, brands는 자동으로 추가됨
        return "products/form";
    }

    @GetMapping("/{id}/edit")
    public String editForm(@PathVariable Long id, Model model) {
        model.addAttribute("product", productService.findById(id));
        // categories, brands는 자동으로 추가됨
        return "products/form";
    }
}
```

### 3. Thymeleaf 템플릿

#### 기본 문법

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title th:text="${pageTitle}">제목</title>
</head>
<body>
    <!-- 텍스트 출력 -->
    <h1 th:text="${user.name}">홍길동</h1>

    <!-- HTML 출력 (이스케이프 안함) -->
    <div th:utext="${htmlContent}"></div>

    <!-- 속성 설정 -->
    <img th:src="@{/images/logo.png}" th:alt="${product.name}">

    <!-- 조건문 -->
    <div th:if="${user.role == 'ADMIN'}">
        관리자 메뉴
    </div>
    <div th:unless="${user.role == 'ADMIN'}">
        일반 사용자 메뉴
    </div>

    <!-- 반복문 -->
    <table>
        <tr th:each="user : ${users}">
            <td th:text="${user.id}">1</td>
            <td th:text="${user.name}">이름</td>
            <td th:text="${user.email}">이메일</td>
        </tr>
    </table>

    <!-- 인덱스 사용 -->
    <div th:each="item, stat : ${items}">
        <span th:text="${stat.index}">0</span>
        <span th:text="${stat.count}">1</span>
        <span th:text="${item.name}">아이템</span>
        <span th:if="${stat.first}">첫번째</span>
        <span th:if="${stat.last}">마지막</span>
    </div>

    <!-- URL 생성 -->
    <a th:href="@{/users/{id}(id=${user.id})}">상세보기</a>
    <a th:href="@{/search(keyword=${keyword}, page=${page})}">검색</a>

    <!-- 폼 -->
    <form th:action="@{/users}" th:object="${user}" method="post">
        <input type="text" th:field="*{name}" />
        <input type="email" th:field="*{email}" />
        <button type="submit">저장</button>
    </form>

    <!-- 날짜 포맷 -->
    <span th:text="${#temporals.format(user.createdAt, 'yyyy-MM-dd HH:mm')}"></span>

    <!-- 숫자 포맷 -->
    <span th:text="${#numbers.formatDecimal(product.price, 0, 'COMMA', 0, 'POINT')}"></span>

    <!-- 문자열 처리 -->
    <span th:text="${#strings.toUpperCase(user.name)}"></span>
    <span th:text="${#strings.substring(user.name, 0, 10)}"></span>

    <!-- 삼항 연산자 -->
    <span th:text="${user.age >= 18} ? '성인' : '미성년'"></span>

    <!-- Elvis 연산자 (null 대체) -->
    <span th:text="${user.nickname} ?: '닉네임 없음'"></span>

    <!-- Fragment (재사용 가능한 템플릿 조각) -->
    <div th:replace="~{fragments/header :: header}"></div>
    <div th:replace="~{fragments/footer :: footer}"></div>
</body>
</html>
```

#### Layout (레이아웃)

**layout.html** (공통 레이아웃):

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org"
      xmlns:layout="http://www.ultraq.net.nz/thymeleaf/layout">
<head>
    <meta charset="UTF-8">
    <title layout:title-pattern="$CONTENT_TITLE - $LAYOUT_TITLE">사이트 제목</title>
    <link rel="stylesheet" th:href="@{/css/common.css}">
    <th:block layout:fragment="css"></th:block>
</head>
<body>
    <header th:replace="~{fragments/header :: header}"></header>

    <main layout:fragment="content">
        <!-- 페이지별 컨텐츠가 여기에 삽입됨 -->
    </main>

    <footer th:replace="~{fragments/footer :: footer}"></footer>

    <script th:src="@{/js/common.js}"></script>
    <th:block layout:fragment="script"></th:block>
</body>
</html>
```

**users/list.html** (레이아웃 사용):

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org"
      xmlns:layout="http://www.ultraq.net.nz/thymeleaf/layout"
      layout:decorate="~{layout/layout}">
<head>
    <title>사용자 목록</title>
    <th:block layout:fragment="css">
        <link rel="stylesheet" th:href="@{/css/users.css}">
    </th:block>
</head>
<body>
    <div layout:fragment="content">
        <h1>사용자 목록</h1>
        <table>
            <tr th:each="user : ${users}">
                <td th:text="${user.name}"></td>
                <td th:text="${user.email}"></td>
            </tr>
        </table>
    </div>

    <th:block layout:fragment="script">
        <script th:src="@{/js/users.js}"></script>
    </th:block>
</body>
</html>
```

---

## 💻 기본 실습

### 실습: Thymeleaf 레이아웃 적용

**난이도**: ⭐⭐⭐☆☆

**pom.xml 의존성**:

```xml
<!-- Thymeleaf -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-thymeleaf</artifactId>
</dependency>

<!-- Thymeleaf Layout Dialect -->
<dependency>
    <groupId>nz.net.ultraq.thymeleaf</groupId>
    <artifactId>thymeleaf-layout-dialect</artifactId>
</dependency>
```

**fragments/header.html**:

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<header th:fragment="header">
    <nav>
        <a th:href="@{/}">홈</a>
        <a th:href="@{/products}">상품</a>
        <a th:href="@{/board}">게시판</a>
        <a th:href="@{/users}">회원</a>
    </nav>
</header>
</html>
```

**fragments/footer.html**:

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<footer th:fragment="footer">
    <p>&copy; 2024 My Company. All rights reserved.</p>
</footer>
</html>
```

---

## 🏢 실무 활용 사례

### 사례 1: 네이버 쇼핑 - 다양한 클라이언트 대응

**배경**: 같은 상품 데이터를 웹, 모바일 앱, Open API로 제공

```java
@Controller
@RequestMapping("/api/products")
public class NaverProductController {

    @Autowired
    private ProductService productService;

    @GetMapping("/{id}")
    public Object getProduct(
        @PathVariable Long id,
        @RequestHeader(value = "Accept", defaultValue = "text/html") String accept,
        @RequestHeader(value = "User-Agent", defaultValue = "") String userAgent,
        Model model
    ) {
        // ✅ 비즈니스 로직은 한 번만 (Model 준비)
        Product product = productService.findById(id);
        ProductDetail detail = productService.getDetail(id);
        List<Review> reviews = reviewService.findByProductId(id);

        model.addAttribute("product", product);
        model.addAttribute("detail", detail);
        model.addAttribute("reviews", reviews);

        // ✅ 클라이언트에 따라 다른 View 선택
        if (accept.contains("application/json")) {
            // Open API: JSON 형태로
            return ResponseEntity.ok(ProductApiResponse.from(product, detail, reviews));
        } else if (userAgent.contains("NaverApp")) {
            // 네이버 앱: 모바일 최적화 HTML
            return "products/mobile";
        } else {
            // 웹 브라우저: 데스크톱 HTML
            return "products/detail";
        }
    }
}
```

**View 예시**:

**products/detail.html** (웹용):
```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<body>
    <!-- 큰 화면용: 상세한 정보 + 이미지 크게 -->
    <div class="product-detail-desktop">
        <div class="image-gallery">
            <img th:each="img : ${product.images}"
                 th:src="${img.url}"
                 style="width: 500px">
        </div>
        <div class="product-info">
            <h1 th:text="${product.name}"></h1>
            <div class="price" th:text="${product.price}"></div>
            <div class="reviews">
                <div th:each="review : ${reviews}" class="review-card">
                    <!-- 상세한 리뷰 표시 -->
                </div>
            </div>
        </div>
    </div>
</body>
</html>
```

**products/mobile.html** (모바일 앱용):
```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<body>
    <!-- 작은 화면용: 간결한 정보 + 빠른 로딩 -->
    <div class="product-detail-mobile">
        <img th:src="${product.mainImage}" style="width: 100%">
        <h2 th:text="${product.name}"></h2>
        <div class="price" th:text="${product.price}"></div>
        <!-- 리뷰는 "더보기" 버튼으로 -->
        <a href="#" class="load-reviews">리뷰 더보기</a>
    </div>
</body>
</html>
```

**성과**:
- **코드 재사용**: 비즈니스 로직 1벌, View 3벌로 모든 클라이언트 지원
- **유지보수 용이**: 가격 계산 로직 변경 시 Controller만 수정
- **성능**: 모바일 View는 이미지 크기 최적화로 로딩 **50% 단축**

---

### 사례 2: 카카오뱅크 - Content Negotiation으로 다중 형식 지원

**배경**: 관리자는 Excel, 일반 사용자는 HTML, 외부 시스템은 JSON

```java
@Controller
@RequestMapping("/reports/transactions")
public class TransactionReportController {

    @Autowired
    private TransactionService transactionService;

    @GetMapping
    public Object getTransactionReport(
        @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd") LocalDate startDate,
        @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd") LocalDate endDate,
        @RequestParam(required = false) String format,
        Model model
    ) {
        // ✅ 데이터 조회 (Model 준비)
        List<Transaction> transactions = transactionService.findByDateRange(startDate, endDate);
        TransactionSummary summary = transactionService.getSummary(transactions);

        model.addAttribute("transactions", transactions);
        model.addAttribute("summary", summary);
        model.addAttribute("startDate", startDate);
        model.addAttribute("endDate", endDate);

        // ✅ 형식에 따라 다른 View
        if ("excel".equals(format)) {
            // Excel 다운로드
            return new ModelAndView("transactionExcelView", model.asMap());
        } else if ("json".equals(format)) {
            // JSON API
            return ResponseEntity.ok(TransactionReportDto.from(transactions, summary));
        } else if ("pdf".equals(format)) {
            // PDF 다운로드
            return new ModelAndView("transactionPdfView", model.asMap());
        } else {
            // HTML 화면
            return "reports/transactions";
        }
    }
}
```

**Excel View 구현**:
```java
public class TransactionExcelView extends AbstractXlsxView {

    @Override
    protected void buildExcelDocument(
        Map<String, Object> model,
        Workbook workbook,
        HttpServletRequest request,
        HttpServletResponse response
    ) throws Exception {
        // 파일명 설정
        response.setHeader("Content-Disposition",
            "attachment; filename=transactions.xlsx");

        Sheet sheet = workbook.createSheet("거래 내역");

        // 헤더
        Row headerRow = sheet.createRow(0);
        headerRow.createCell(0).setCellValue("거래일시");
        headerRow.createCell(1).setCellValue("구분");
        headerRow.createCell(2).setCellValue("금액");
        headerRow.createCell(3).setCellValue("잔액");

        // 데이터
        List<Transaction> transactions =
            (List<Transaction>) model.get("transactions");

        int rowNum = 1;
        for (Transaction tx : transactions) {
            Row row = sheet.createRow(rowNum++);
            row.createCell(0).setCellValue(tx.getTransactionDate().toString());
            row.createCell(1).setCellValue(tx.getType());
            row.createCell(2).setCellValue(tx.getAmount());
            row.createCell(3).setCellValue(tx.getBalance());
        }
    }
}
```

**성과**:
- **비즈니스 로직 통일**: 거래 내역 조회 로직을 한 곳에서 관리
- **다양한 형식**: HTML, Excel, PDF, JSON을 하나의 Controller로 제공
- **관리자 만족도**: Excel 다운로드 기능으로 업무 효율 **80% 향상**

---

### 사례 3: 쿠팡 - Thymeleaf Fragment로 공통 UI 재사용

**배경**: 상품, 주문, 배송 화면에서 헤더/푸터/검색바를 공통으로 사용

**프로젝트 구조**:
```
templates/
├── fragments/
│   ├── header.html
│   ├── footer.html
│   ├── searchBar.html
│   └── userMenu.html
├── products/
│   ├── list.html
│   └── detail.html
├── orders/
│   ├── list.html
│   └── detail.html
└── layout.html
```

**fragments/header.html**:
```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<header th:fragment="header">
    <nav class="navbar">
        <a th:href="@{/}">
            <img th:src="@{/images/coupang-logo.png}" alt="쿠팡">
        </a>
        <div th:replace="~{fragments/searchBar :: searchBar}"></div>
        <div th:replace="~{fragments/userMenu :: userMenu}"></div>
    </nav>
</header>
</html>
```

**fragments/searchBar.html** (파라미터 전달):
```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<div th:fragment="searchBar(placeholder, action)">
    <form th:action="${action}" method="get" class="search-form">
        <input type="text"
               name="keyword"
               th:placeholder="${placeholder}"
               th:value="${param.keyword}">
        <button type="submit">검색</button>
    </form>
</div>
</html>
```

**products/list.html** (Fragment 사용):
```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <title>상품 목록 - 쿠팡</title>
</head>
<body>
    <!-- ✅ Fragment 재사용 -->
    <div th:replace="~{fragments/header :: header}"></div>

    <!-- ✅ 파라미터를 전달하는 Fragment -->
    <div th:replace="~{fragments/searchBar :: searchBar(
        placeholder='상품을 검색하세요',
        action='/products/search'
    )}"></div>

    <main>
        <h1>상품 목록</h1>
        <div class="product-grid">
            <div th:each="product : ${products}" class="product-card">
                <img th:src="${product.imageUrl}">
                <h3 th:text="${product.name}"></h3>
                <div class="price" th:text="${product.price}"></div>
            </div>
        </div>
    </main>

    <!-- ✅ Footer도 재사용 -->
    <div th:replace="~{fragments/footer :: footer}"></div>
</body>
</html>
```

**Layout 적용** (layout.html):
```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org"
      xmlns:layout="http://www.ultraq.net.nz/thymeleaf/layout">
<head>
    <meta charset="UTF-8">
    <title layout:title-pattern="$CONTENT_TITLE - 쿠팡">쿠팡</title>
    <link rel="stylesheet" th:href="@{/css/common.css}">
    <th:block layout:fragment="css"></th:block>
</head>
<body>
    <div th:replace="~{fragments/header :: header}"></div>

    <!-- ✅ 페이지별 컨텐츠 -->
    <main layout:fragment="content">
        <!-- 여기에 각 페이지의 내용이 들어감 -->
    </main>

    <div th:replace="~{fragments/footer :: footer}"></div>

    <script th:src="@{/js/common.js}"></script>
    <th:block layout:fragment="script"></th:block>
</body>
</html>
```

**페이지에서 Layout 사용**:
```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org"
      xmlns:layout="http://www.ultraq.net.nz/thymeleaf/layout"
      layout:decorate="~{layout}">
<head>
    <title>상품 상세</title>
    <th:block layout:fragment="css">
        <link rel="stylesheet" th:href="@{/css/product-detail.css}">
    </th:block>
</head>
<body>
    <!-- ✅ content Fragment만 작성하면 됨 -->
    <div layout:fragment="content">
        <div class="product-detail">
            <h1 th:text="${product.name}"></h1>
            <div class="price" th:text="${product.price}"></div>
            <!-- 상품 상세 내용 -->
        </div>
    </div>

    <th:block layout:fragment="script">
        <script th:src="@{/js/product-detail.js}"></script>
    </th:block>
</body>
</html>
```

**성과**:
- **코드 중복 제거**: 헤더/푸터 코드를 50개 페이지에서 재사용
- **유지보수 시간**: 디자인 변경 시 Fragment 파일 하나만 수정 → **90% 단축**
- **신규 페이지 개발**: Layout 사용으로 개발 속도 **3배 향상**

---

## 👨‍💻 주니어 개발자 시나리오

### 시나리오 1: "Model과 ModelMap, 뭘 써야 하죠?"

**상황**:
주니어 개발자 김코딩이 사용자 목록을 보여주는 Controller를 작성하다가 고민합니다.

```java
// 방법 1: Model
@GetMapping("/users")
public String list1(Model model) {
    List<User> users = userService.findAll();
    model.addAttribute("users", users);
    return "users/list";
}

// 방법 2: ModelMap
@GetMapping("/users")
public String list2(ModelMap modelMap) {
    List<User> users = userService.findAll();
    modelMap.addAttribute("users", users);
    return "users/list";
}

// 방법 3: Map
@GetMapping("/users")
public String list3(Map<String, Object> map) {
    List<User> users = userService.findAll();
    map.put("users", users);
    return "users/list";
}

// 방법 4: ModelAndView
@GetMapping("/users")
public ModelAndView list4() {
    ModelAndView mav = new ModelAndView("users/list");
    List<User> users = userService.findAll();
    mav.addObject("users", users);
    return mav;
}
```

**멘토의 답변**:

**99%는 Model을 사용하세요!**

```java
// ✅ 추천: Model (가장 간결하고 명확함)
@GetMapping("/users")
public String list(Model model) {
    model.addAttribute("users", userService.findAll());
    model.addAttribute("pageTitle", "사용자 목록");
    model.addAttribute("totalCount", userService.count());
    return "users/list";
}
```

**특수한 경우만 다른 것 사용**:

```java
// ModelMap: Map 연산이 필요할 때
@GetMapping("/stats")
public String stats(ModelMap model) {
    model.addAttribute("users", userService.findAll());
    model.addAttribute("total", model.get("users").size());  // Map처럼 get() 가능
    model.mergeAttributes(otherMap);  // 다른 Map과 병합
    return "stats";
}

// ModelAndView: View 이름을 조건부로 선택할 때
@GetMapping("/report")
public ModelAndView report(@RequestParam String format) {
    ModelAndView mav = new ModelAndView();
    mav.addObject("data", reportService.getData());

    if ("pdf".equals(format)) {
        mav.setViewName("pdfView");
    } else {
        mav.setViewName("htmlView");
    }

    return mav;
}
```

**정리**:
- **기본**: Model
- **Map 연산 필요**: ModelMap
- **View 이름을 동적으로**: ModelAndView

---

### 시나리오 2: "Thymeleaf 문법이 너무 많아요!"

**상황**:
주니어 개발자 박초보가 Thymeleaf 템플릿을 작성하다가 문법이 너무 많아 혼란스럽습니다.

**멘토의 조언: 실무에서 자주 쓰는 5가지만 외우세요!**

**1. 텍스트 출력: `th:text`**
```html
<h1 th:text="${user.name}">홍길동</h1>
<!-- 결과: <h1>홍길동</h1> -->
```

**2. 반복문: `th:each`**
```html
<tr th:each="user : ${users}">
    <td th:text="${user.id}">1</td>
    <td th:text="${user.name}">이름</td>
</tr>
<!-- users 리스트를 반복하며 테이블 생성 -->
```

**3. 조건문: `th:if`**
```html
<div th:if="${user.role == 'ADMIN'}">
    관리자 메뉴
</div>
<div th:unless="${user.role == 'ADMIN'}">
    일반 사용자 메뉴
</div>
```

**4. URL 생성: `th:href="@{...}"`**
```html
<a th:href="@{/users/{id}(id=${user.id})}">상세보기</a>
<!-- 결과: <a href="/users/123">상세보기</a> -->

<a th:href="@{/search(keyword=${keyword}, page=${page})}">검색</a>
<!-- 결과: <a href="/search?keyword=spring&page=1">검색</a> -->
```

**5. 폼 바인딩: `th:object`와 `th:field`**
```html
<form th:action="@{/users}" th:object="${user}" method="post">
    <input type="text" th:field="*{name}" />
    <!-- name="name" value="..." id="name" 자동 생성 -->

    <input type="email" th:field="*{email}" />
    <button type="submit">저장</button>
</form>
```

**실무 템플릿 예시**:
```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<body>
    <h1>사용자 목록</h1>

    <!-- ✅ 1. 조건문 -->
    <div th:if="${users.isEmpty()}">
        등록된 사용자가 없습니다.
    </div>

    <!-- ✅ 2. 반복문 + 3. 텍스트 출력 + 4. URL -->
    <table th:unless="${users.isEmpty()}">
        <tr th:each="user, stat : ${users}">
            <td th:text="${stat.count}">1</td>
            <td th:text="${user.name}">이름</td>
            <td>
                <a th:href="@{/users/{id}(id=${user.id})}">상세</a>
                <a th:href="@{/users/{id}/edit(id=${user.id})}">수정</a>
            </td>
        </tr>
    </table>

    <!-- ✅ 5. 폼 -->
    <form th:action="@{/users}" th:object="${userForm}" method="post">
        <input type="text" th:field="*{name}" placeholder="이름">
        <input type="email" th:field="*{email}" placeholder="이메일">
        <button type="submit">등록</button>
    </form>
</body>
</html>
```

**꿀팁**:
- 나머지 문법은 필요할 때 공식 문서에서 찾아보기
- IntelliJ는 `th:` 입력 시 자동 완성 지원

---

### 시나리오 3: "Fragment를 어떻게 나눠야 하나요?"

**상황**:
주니어 개발자 이신입이 화면을 Fragment로 나누려고 하는데, 어디까지 나눠야 할지 모르겠습니다.

**멘토의 가이드**:

**❌ 나쁜 예: 너무 세세하게 나눔**
```
fragments/
├── logo.html
├── loginButton.html
├── searchInput.html
├── searchButton.html
├── userIcon.html
├── cartIcon.html
└── ... (너무 많음)
```

**✅ 좋은 예: 재사용 단위로 나눔**
```
fragments/
├── header.html      (로고 + 검색바 + 사용자 메뉴)
├── footer.html      (회사 정보 + 링크)
├── userMenu.html    (로그인/로그아웃/마이페이지)
└── pagination.html  (페이지네이션)
```

**Fragment 분리 기준**:

**1. 여러 페이지에서 재사용되는 것**:
```html
<!-- ✅ 헤더는 모든 페이지에서 사용 → Fragment로 분리 -->
<header th:fragment="header">
    <!-- 헤더 내용 -->
</header>
```

**2. 독립적으로 동작하는 UI 컴포넌트**:
```html
<!-- ✅ 페이지네이션은 독립적 → Fragment로 분리 -->
<nav th:fragment="pagination(page, totalPages)">
    <a th:if="${page > 0}"
       th:href="@{(page=${page - 1})}">이전</a>

    <span th:text="|${page + 1} / ${totalPages}|"></span>

    <a th:if="${page < totalPages - 1}"
       th:href="@{(page=${page + 1})}">다음</a>
</nav>
```

**3. 복잡한 로직이 담긴 부분**:
```html
<!-- ✅ 상품 카드는 복잡하고 재사용됨 → Fragment로 분리 -->
<div th:fragment="productCard(product)">
    <div class="product-card">
        <img th:src="${product.imageUrl}">
        <h3 th:text="${product.name}"></h3>
        <div class="price" th:text="${#numbers.formatDecimal(product.price, 0, 'COMMA', 0, 'POINT')}"></div>

        <!-- 할인율 계산 -->
        <span th:if="${product.discount > 0}"
              th:text="|${product.discount}% 할인|"
              class="discount-badge"></span>

        <!-- 평점 표시 -->
        <div class="rating">
            <span th:each="i : ${#numbers.sequence(1, 5)}">
                <i th:class="${i <= product.rating} ? 'star-filled' : 'star-empty'"></i>
            </span>
        </div>
    </div>
</div>
```

**사용 예시**:
```html
<!-- 상품 목록 페이지 -->
<div th:each="product : ${products}">
    <div th:replace="~{fragments/productCard :: productCard(${product})}"></div>
</div>
```

**정리**:
- **너무 세세하게 나누지 마세요**: 관리 오버헤드
- **재사용되는 단위로 나누세요**: header, footer, 카드 등
- **파라미터 전달**: Fragment에 데이터를 넘길 수 있음

---

## 🏢 실무 활용

### Content Negotiation (JSON/XML/HTML 자동 선택)

```java
@Controller
@RequestMapping("/api/products")
public class ProductController {

    @GetMapping(value = "/{id}", produces = {
        MediaType.APPLICATION_JSON_VALUE,
        MediaType.APPLICATION_XML_VALUE,
        MediaType.TEXT_HTML_VALUE
    })
    public Object getProduct(@PathVariable Long id, @RequestHeader("Accept") String accept) {
        Product product = productService.findById(id);

        // Accept 헤더에 따라 다른 View 반환
        if (accept.contains("application/json")) {
            return ResponseEntity.ok(product);  // JSON
        } else if (accept.contains("application/xml")) {
            return ResponseEntity.ok(product);  // XML
        } else {
            return "products/detail";  // HTML
        }
    }
}
```

---

## ❓ FAQ

<details>
<summary><strong>Q1: JSP와 Thymeleaf 중 무엇을 선택해야 하나요?</strong></summary>

**A**: 신규 프로젝트는 Thymeleaf, 레거시는 JSP를 사용합니다.

| 특징 | JSP | Thymeleaf |
|------|-----|-----------|
| 문법 | Java 코드 혼재 | HTML 유사 |
| 브라우저 직접 열기 | 불가능 | 가능 (Natural Template) |
| Spring Boot | 권장 안함 | 기본 지원 |
| 성능 | 빠름 | 약간 느림 (캐싱 가능) |
| 테스트 | 어려움 | 쉬움 |

**추천**:
- ✅ 신규 프로젝트: Thymeleaf
- ✅ 레거시 유지보수: JSP
- ✅ API 서버: JSON (View 없음)

</details>

<details>
<summary><strong>Q2: Model, ModelMap, ModelAndView의 차이는?</strong></summary>

**A**: 모두 View로 데이터 전달하지만 기능과 용도가 다릅니다.

**Model (인터페이스)**:
```java
@GetMapping("/users")
public String list(Model model) {
    model.addAttribute("users", userService.findAll());
    return "users/list";  // View 이름만 반환
}
```

**ModelMap (Map 구현체)**:
```java
@GetMapping("/users")
public String list(ModelMap model) {
    model.addAttribute("users", userService.findAll());
    model.put("total", 100);  // Map처럼 사용 가능
    return "users/list";
}
```

**ModelAndView (데이터 + View 이름)**:
```java
@GetMapping("/users")
public ModelAndView list() {
    ModelAndView mav = new ModelAndView("users/list");
    mav.addObject("users", userService.findAll());
    return mav;  // View 이름도 함께 반환
}
```

**실무 권장**: Model + String 반환 (가장 간결)

</details>

<details>
<summary><strong>Q3: Thymeleaf의 Natural Template이란 무엇인가요?</strong></summary>

**A**: Natural Template은 **서버 없이 브라우저에서 직접 열어도 디자인을 확인할 수 있는 템플릿**입니다.

**JSP와 비교**:
```jsp
<!-- JSP: 브라우저에서 직접 열면 깨짐 -->
<h1><%= user.getName() %></h1>
<c:forEach items="${users}" var="user">
    <tr>
        <td>${user.name}</td>
    </tr>
</c:forEach>
```

**Thymeleaf: 브라우저에서 직접 열어도 OK**:
```html
<!-- Thymeleaf: 브라우저에서 직접 열면 "홍길동" 표시, 서버에서는 실제 데이터 표시 -->
<h1 th:text="${user.name}">홍길동</h1>  <!-- 기본값 "홍길동" -->

<table>
    <tr th:each="user : ${users}">
        <td th:text="${user.name}">샘플 이름</td>
        <td th:text="${user.email}">sample@email.com</td>
    </tr>
</table>
```

**장점**:
- 디자이너가 서버 없이 HTML 파일만으로 디자인 확인 가능
- 프로토타입을 그대로 템플릿으로 전환 가능
- 협업 효율 향상

</details>

<details>
<summary><strong>Q4: @ModelAttribute 메서드 레벨은 언제 사용하나요?</strong></summary>

**A**: 모든 핸들러 메서드에서 **공통으로 필요한 데이터를 자동으로 추가**할 때 사용합니다.

```java
@Controller
@RequestMapping("/products")
public class ProductController {

    // ✅ 이 컨트롤러의 모든 메서드 실행 전에 자동 호출
    @ModelAttribute("categories")
    public List<Category> categories() {
        return categoryService.findAll();
    }

    @ModelAttribute("brands")
    public List<Brand> brands() {
        return brandService.findAll();
    }

    // 모든 메서드에서 categories, brands 자동으로 사용 가능
    @GetMapping("/new")
    public String newForm(Model model) {
        model.addAttribute("product", new Product());
        // categories, brands는 이미 Model에 있음!
        return "products/form";
    }

    @GetMapping("/{id}/edit")
    public String editForm(@PathVariable Long id, Model model) {
        model.addAttribute("product", productService.findById(id));
        // categories, brands는 이미 Model에 있음!
        return "products/form";
    }
}
```

**주의점**:
- 모든 메서드에서 실행되므로 성능 영향 고려
- 특정 메서드에만 필요하면 해당 메서드 내에서 직접 추가

</details>

<details>
<summary><strong>Q5: ViewResolver의 우선순위는 어떻게 설정하나요?</strong></summary>

**A**: `order` 속성으로 우선순위를 설정합니다. **숫자가 작을수록 우선순위가 높습니다.**

```java
@Configuration
public class ViewResolverConfig {

    // 우선순위 1: BeanName으로 먼저 찾기
    @Bean
    public BeanNameViewResolver beanNameViewResolver() {
        BeanNameViewResolver resolver = new BeanNameViewResolver();
        resolver.setOrder(1);  // 가장 높은 우선순위
        return resolver;
    }

    // 우선순위 2: Thymeleaf로 찾기
    @Bean
    public ThymeleafViewResolver thymeleafViewResolver() {
        ThymeleafViewResolver resolver = new ThymeleafViewResolver();
        resolver.setTemplateEngine(templateEngine());
        resolver.setOrder(2);  // 두 번째 우선순위
        return resolver;
    }

    // 우선순위 3: JSP로 찾기 (마지막 수단)
    @Bean
    public InternalResourceViewResolver jspViewResolver() {
        InternalResourceViewViewResolver resolver = new InternalResourceViewResolver();
        resolver.setPrefix("/WEB-INF/views/");
        resolver.setSuffix(".jsp");
        resolver.setOrder(3);  // 가장 낮은 우선순위
        return resolver;
    }
}
```

**동작 순서**:
```
Controller가 "excelView" 반환
↓
1. BeanNameViewResolver: "excelView" Bean 찾기 → 있으면 반환
↓ (없으면 다음)
2. ThymeleafViewResolver: classpath:/templates/excelView.html 찾기 → 있으면 반환
↓ (없으면 다음)
3. InternalResourceViewResolver: /WEB-INF/views/excelView.jsp 찾기 → 있으면 반환
↓ (없으면)
404 에러
```

</details>

<details>
<summary><strong>Q6: Fragment에 여러 파라미터를 전달하려면?</strong></summary>

**A**: Fragment 호출 시 **괄호 안에 파라미터를 나열**합니다.

```html
<!-- Fragment 정의 -->
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<div th:fragment="userCard(user, showEmail, showPhone)">
    <div class="user-card">
        <h3 th:text="${user.name}">이름</h3>

        <!-- showEmail이 true일 때만 표시 -->
        <div th:if="${showEmail}">
            <span th:text="${user.email}">이메일</span>
        </div>

        <!-- showPhone이 true일 때만 표시 -->
        <div th:if="${showPhone}">
            <span th:text="${user.phone}">전화번호</span>
        </div>
    </div>
</div>
</html>
```

```html
<!-- Fragment 사용 -->
<div th:each="user : ${users}">
    <!-- 이메일만 표시 -->
    <div th:replace="~{fragments/userCard :: userCard(${user}, true, false)}"></div>
</div>

<div>
    <!-- 이메일과 전화번호 모두 표시 -->
    <div th:replace="~{fragments/userCard :: userCard(${user}, true, true)}"></div>
</div>
```

**명시적 파라미터명 사용** (더 명확함):
```html
<div th:replace="~{fragments/userCard :: userCard(
    user=${user},
    showEmail=true,
    showPhone=false
)}"></div>
```

</details>

<details>
<summary><strong>Q7: View에서 어떻게 성능을 최적화하나요?</strong></summary>

**A**: Thymeleaf에서 **캐싱, 템플릿 모드 설정, Fragment 최적화**로 성능을 향상시킬 수 있습니다.

**1. 프로덕션 환경에서 캐싱 활성화**:
```yaml
# application-prod.yml
spring:
  thymeleaf:
    cache: true  # ✅ 프로덕션에서는 true
    mode: HTML   # HTML5 대신 HTML (더 빠름)

# application-dev.yml
spring:
  thymeleaf:
    cache: false  # ✅ 개발에서는 false (변경사항 즉시 반영)
```

**2. Fragment 캐싱**:
```java
@Configuration
public class ThymeleafConfig {

    @Bean
    public SpringTemplateEngine templateEngine() {
        SpringTemplateEngine engine = new SpringTemplateEngine();
        engine.setTemplateResolver(templateResolver());

        // ✅ Fragment 캐싱 활성화
        engine.setEnableSpringELCompiler(true);  // SpEL 컴파일러 활성화

        return engine;
    }
}
```

**3. 불필요한 데이터 전달 최소화**:
```java
// ❌ 나쁜 예: 전체 엔티티 전달
@GetMapping("/users")
public String list(Model model) {
    List<User> users = userRepository.findAll();  // 모든 필드 로드
    model.addAttribute("users", users);
    return "users/list";
}

// ✅ 좋은 예: 필요한 필드만 DTO로 전달
@GetMapping("/users")
public String list(Model model) {
    List<UserListDto> users = userService.findAllForList();  // 이름, 이메일만
    model.addAttribute("users", users);
    return "users/list";
}
```

**4. 조건부 렌더링 최적화**:
```html
<!-- ❌ 나쁜 예: 모든 항목에 대해 복잡한 연산 -->
<div th:each="product : ${products}">
    <span th:text="${#numbers.formatDecimal(product.price * 1.1 * exchangeRate, 2, 'COMMA', 2, 'POINT')}"></span>
</div>

<!-- ✅ 좋은 예: Controller에서 미리 계산 -->
<div th:each="product : ${products}">
    <span th:text="${product.displayPrice}"></span>
</div>
```

</details>

---

## 💼 면접 질문 리스트

### 주니어 레벨 (5-7개)

1. **Model, ModelMap, ModelAndView의 차이점을 설명하고, 각각 언제 사용하는지 말해보세요.**

2. **ViewResolver의 역할과 동작 원리를 설명해주세요.**

3. **Thymeleaf의 th:text와 th:utext의 차이점은 무엇인가요?**

4. **Thymeleaf Fragment는 무엇이며, 왜 사용하나요?**

5. **@ModelAttribute를 메서드 레벨에 사용하는 경우와 파라미터 레벨에 사용하는 경우의 차이를 설명해주세요.**

6. **JSP와 Thymeleaf의 장단점을 비교해주세요.**

7. **th:object와 th:field는 어떻게 함께 사용되나요?**

### 중급 레벨 (3-5개)

1. **여러 ViewResolver를 동시에 사용할 때 우선순위는 어떻게 결정되며, 이를 어떻게 설정하나요?**

2. **Thymeleaf의 Layout Dialect를 사용하는 이유와 구현 방법을 설명해주세요.**

3. **Content Negotiation을 통해 같은 데이터를 HTML, JSON, XML로 제공하는 방법을 설명해주세요.**

4. **Thymeleaf의 성능을 최적화하는 방법을 설명해주세요.**

5. **Custom View를 만들어 Excel이나 PDF를 생성하는 방법을 설명해주세요.**

---

## 💡 면접 질문 답안

### 주니어 레벨 답안

#### Q1. Model, ModelMap, ModelAndView의 차이점을 설명하고, 각각 언제 사용하는지 말해보세요.

**답변**:

세 가지 모두 Controller에서 View로 데이터를 전달하는 데 사용되지만, 기능과 사용 방식이 다릅니다.

**Model (인터페이스)**:
- 가장 기본적이고 간결한 방식
- `addAttribute()` 메서드로 데이터 추가
- View 이름은 메서드 반환값으로 별도 지정

```java
@GetMapping("/users")
public String list(Model model) {
    model.addAttribute("users", userService.findAll());
    return "users/list";  // View 이름
}
```

**ModelMap (구현 클래스)**:
- Model의 구현체로 Map 인터페이스도 구현
- Map처럼 `get()`, `put()` 등의 메서드 사용 가능
- Model보다 더 많은 기능 제공

```java
@GetMapping("/stats")
public String stats(ModelMap model) {
    List<User> users = userService.findAll();
    model.addAttribute("users", users);
    model.put("total", users.size());  // Map처럼 사용
    return "stats";
}
```

**ModelAndView (데이터 + View 이름 포함)**:
- Model 데이터와 View 이름을 하나의 객체에 담음
- View 이름을 조건부로 선택할 때 유용

```java
@GetMapping("/report")
public ModelAndView report(@RequestParam String format) {
    ModelAndView mav = new ModelAndView();
    mav.addObject("data", reportService.getData());

    // 조건에 따라 다른 View 선택
    if ("pdf".equals(format)) {
        mav.setViewName("pdfView");
    } else {
        mav.setViewName("htmlView");
    }

    return mav;
}
```

**실무 권장**:
- **일반적인 경우**: Model 사용 (가장 간결)
- **Map 연산 필요**: ModelMap 사용
- **View 이름을 동적으로 선택**: ModelAndView 사용

---

#### Q2. ViewResolver의 역할과 동작 원리를 설명해주세요.

**답변**:

ViewResolver는 **Controller가 반환한 논리적 View 이름을 실제 View 객체로 변환**하는 역할을 합니다.

**동작 과정**:

```
1. Controller가 "users/list" 반환
   ↓
2. ViewResolver가 prefix + viewName + suffix 조합
   ↓
3. 실제 파일 경로로 변환
   /WEB-INF/views/users/list.jsp (JSP의 경우)
   classpath:/templates/users/list.html (Thymeleaf의 경우)
   ↓
4. 해당 View 객체 생성 및 반환
   ↓
5. DispatcherServlet이 View에게 렌더링 요청
```

**예시 (Thymeleaf)**:

```java
@Bean
public ThymeleafViewResolver thymeleafViewResolver() {
    ThymeleafViewResolver resolver = new ThymeleafViewResolver();
    resolver.setTemplateEngine(templateEngine());
    resolver.setCharacterEncoding("UTF-8");
    return resolver;
}

@Bean
public SpringResourceTemplateResolver templateResolver() {
    SpringResourceTemplateResolver resolver = new SpringResourceTemplateResolver();
    resolver.setPrefix("classpath:/templates/");  // prefix
    resolver.setSuffix(".html");                  // suffix
    return resolver;
}
```

```java
@Controller
public class UserController {
    @GetMapping("/users")
    public String list(Model model) {
        return "users/list";  // "users/list" → classpath:/templates/users/list.html
    }
}
```

**여러 ViewResolver 사용 시**:

```java
@Bean
public BeanNameViewResolver beanNameViewResolver() {
    BeanNameViewResolver resolver = new BeanNameViewResolver();
    resolver.setOrder(1);  // 우선순위 1
    return resolver;
}

@Bean
public InternalResourceViewResolver jspViewResolver() {
    InternalResourceViewViewResolver resolver = new InternalResourceViewResolver();
    resolver.setPrefix("/WEB-INF/views/");
    resolver.setSuffix(".jsp");
    resolver.setOrder(2);  // 우선순위 2
    return resolver;
}
```

**우선순위에 따라 순차적으로 View를 찾으며**, 첫 번째로 View를 반환한 Resolver가 사용됩니다.

---

#### Q3. Thymeleaf의 th:text와 th:utext의 차이점은 무엇인가요?

**답변**:

**th:text**는 HTML을 **이스케이프(escape)**하고, **th:utext**는 HTML을 **그대로 렌더링**합니다.

```html
<!-- Controller에서 전달된 데이터 -->
<!-- content = "<strong>중요</strong> 공지사항" -->

<!-- th:text: HTML 태그가 문자열로 표시됨 (보안) -->
<div th:text="${content}">내용</div>
<!-- 결과: <strong>중요</strong> 공지사항 (화면에 태그가 그대로 보임) -->

<!-- th:utext: HTML 태그가 렌더링됨 (위험) -->
<div th:utext="${content}">내용</div>
<!-- 결과: 중요 공지사항 ("중요"가 굵은 글씨로 표시됨) -->
```

**보안 이슈**:

```java
// ❌ 위험: 사용자 입력을 th:utext로 표시
@GetMapping("/comment/{id}")
public String comment(@PathVariable Long id, Model model) {
    Comment comment = commentService.findById(id);
    model.addAttribute("content", comment.getContent());  // 사용자가 입력한 내용
    return "comment/detail";
}
```

```html
<!-- ❌ XSS 공격 가능 -->
<div th:utext="${content}"></div>
<!-- 사용자가 <script>alert('해킹!')</script> 입력 시 스크립트 실행됨 -->

<!-- ✅ 안전 -->
<div th:text="${content}"></div>
<!-- <script>alert('해킹!')</script>가 문자열로 표시됨 -->
```

**실무 권장**:
- **기본**: `th:text` 사용 (안전)
- **신뢰할 수 있는 HTML**: `th:utext` 사용 (에디터로 작성한 게시글 등)
- **사용자 입력**: 절대 `th:utext` 사용 금지

---

#### Q4. Thymeleaf Fragment는 무엇이며, 왜 사용하나요?

**답변**:

Fragment는 **재사용 가능한 템플릿 조각**으로, 헤더, 푸터 같은 공통 UI를 여러 페이지에서 재사용할 때 사용합니다.

**Fragment 정의**:
```html
<!-- fragments/header.html -->
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<header th:fragment="header">
    <nav>
        <a th:href="@{/}">홈</a>
        <a th:href="@{/products}">상품</a>
        <a th:href="@{/users}">회원</a>
    </nav>
</header>
</html>
```

**Fragment 사용**:
```html
<!-- users/list.html -->
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<body>
    <!-- ✅ Fragment 재사용 -->
    <div th:replace="~{fragments/header :: header}"></div>

    <main>
        <h1>사용자 목록</h1>
        <!-- 내용 -->
    </main>
</body>
</html>
```

**왜 사용하나요?**

1. **코드 중복 제거**: 헤더를 50개 페이지에서 재사용
2. **유지보수 용이**: 헤더 수정 시 Fragment 파일 하나만 변경
3. **일관성 유지**: 모든 페이지에서 동일한 헤더 표시

**파라미터 전달도 가능**:
```html
<!-- Fragment 정의 -->
<div th:fragment="userCard(user, showEmail)">
    <h3 th:text="${user.name}"></h3>
    <div th:if="${showEmail}">
        <span th:text="${user.email}"></span>
    </div>
</div>

<!-- Fragment 사용 -->
<div th:replace="~{fragments/userCard :: userCard(${user}, true)}"></div>
```

---

#### Q5. @ModelAttribute를 메서드 레벨에 사용하는 경우와 파라미터 레벨에 사용하는 경우의 차이를 설명해주세요.

**답변**:

**파라미터 레벨**: 요청 데이터를 객체로 바인딩
**메서드 레벨**: 모든 핸들러 메서드에서 공통으로 사용할 데이터 자동 추가

**파라미터 레벨**:
```java
@Controller
public class UserController {

    // ✅ 폼 데이터를 UserForm 객체로 자동 바인딩
    @PostMapping("/users")
    public String create(@ModelAttribute UserForm userForm) {
        // username=john&email=john@example.com
        // → userForm.getUsername() = "john"
        //   userForm.getEmail() = "john@example.com"

        userService.save(userForm);
        return "redirect:/users";
    }
}
```

**메서드 레벨**:
```java
@Controller
@RequestMapping("/products")
public class ProductController {

    // ✅ 모든 핸들러 메서드 실행 전에 자동 실행
    @ModelAttribute("categories")
    public List<Category> categories() {
        return categoryService.findAll();
    }

    @GetMapping("/new")
    public String newForm(Model model) {
        model.addAttribute("product", new Product());
        // categories는 자동으로 Model에 추가됨!
        return "products/form";
    }

    @GetMapping("/{id}/edit")
    public String editForm(@PathVariable Long id, Model model) {
        model.addAttribute("product", productService.findById(id));
        // categories는 자동으로 Model에 추가됨!
        return "products/form";
    }
}
```

**View에서 사용**:
```html
<!-- products/form.html -->
<form th:action="@{/products}" th:object="${product}" method="post">
    <select th:field="*{categoryId}">
        <!-- ✅ categories는 @ModelAttribute 메서드에서 자동 추가됨 -->
        <option th:each="category : ${categories}"
                th:value="${category.id}"
                th:text="${category.name}"></option>
    </select>
</form>
```

**정리**:
- **파라미터 레벨**: 요청 데이터 → 객체 바인딩
- **메서드 레벨**: 공통 데이터를 모든 핸들러에 자동 추가

---

### 중급 레벨 답안

#### Q1. 여러 ViewResolver를 동시에 사용할 때 우선순위는 어떻게 결정되며, 이를 어떻게 설정하나요?

**답변**:

여러 ViewResolver가 등록된 경우 **order 값이 작을수록 높은 우선순위**를 가지며, 순차적으로 View를 찾습니다.

**설정 예시**:
```java
@Configuration
public class ViewResolverConfig {

    // 우선순위 1: BeanName으로 먼저 찾기
    @Bean
    public BeanNameViewResolver beanNameViewResolver() {
        BeanNameViewResolver resolver = new BeanNameViewResolver();
        resolver.setOrder(1);
        return resolver;
    }

    // 우선순위 2: Thymeleaf
    @Bean
    public ThymeleafViewResolver thymeleafViewResolver() {
        ThymeleafViewResolver resolver = new ThymeleafViewResolver();
        resolver.setTemplateEngine(templateEngine());
        resolver.setOrder(2);
        return resolver;
    }

    // 우선순위 3: JSP (fallback)
    @Bean
    public InternalResourceViewResolver jspViewResolver() {
        InternalResourceViewResolver resolver = new InternalResourceViewResolver();
        resolver.setPrefix("/WEB-INF/views/");
        resolver.setSuffix(".jsp");
        resolver.setOrder(3);
        return resolver;
    }

    // Custom View Bean 등록
    @Bean
    public View excelView() {
        return new ExcelReportView();
    }
}
```

**동작 흐름**:
```
Controller가 "excelView" 반환
↓
1. BeanNameViewResolver (order=1)
   → "excelView" Bean 찾기
   → ✅ 있으면 반환, 없으면 다음으로
↓
2. ThymeleafViewResolver (order=2)
   → classpath:/templates/excelView.html 찾기
   → ✅ 있으면 반환, 없으면 다음으로
↓
3. InternalResourceViewResolver (order=3)
   → /WEB-INF/views/excelView.jsp 찾기
   → ✅ 있으면 반환, 없으면 404
```

**실무 활용**:
```java
@Controller
public class ReportController {

    // BeanNameViewResolver가 우선 처리 (Excel View Bean)
    @GetMapping("/report/excel")
    public String excelReport(Model model) {
        model.addAttribute("data", reportService.getData());
        return "excelView";  // → Excel View Bean 사용
    }

    // ThymeleafViewResolver가 처리 (HTML 템플릿)
    @GetMapping("/report/html")
    public String htmlReport(Model model) {
        model.addAttribute("data", reportService.getData());
        return "report/html";  // → templates/report/html.html 사용
    }
}
```

**장점**:
- 같은 Controller에서 HTML, Excel, PDF 등 다양한 형식 제공 가능
- Custom View와 템플릿을 유연하게 조합

---

#### Q2. Content Negotiation을 통해 같은 데이터를 HTML, JSON, XML로 제공하는 방법을 설명해주세요.

**답변**:

Content Negotiation은 **클라이언트의 Accept 헤더에 따라 자동으로 적절한 형식으로 응답**하는 메커니즘입니다.

**Spring Boot 설정**:
```yaml
spring:
  mvc:
    contentnegotiation:
      favor-parameter: true  # 쿼리 파라미터(?format=json) 사용 가능
      parameter-name: format
      media-types:
        json: application/json
        xml: application/xml
```

**Controller 구현**:
```java
@Controller
@RequestMapping("/api/users")
public class UserContentNegotiationController {

    @GetMapping("/{id}")
    public Object getUser(
        @PathVariable Long id,
        @RequestHeader(value = "Accept", defaultValue = "text/html") String accept,
        Model model
    ) {
        User user = userService.findById(id);

        // 클라이언트가 원하는 형식에 따라 분기
        if (accept.contains("application/json")) {
            // JSON 응답
            return ResponseEntity.ok(UserDto.from(user));
        } else if (accept.contains("application/xml")) {
            // XML 응답
            return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_XML)
                .body(UserDto.from(user));
        } else {
            // HTML 응답
            model.addAttribute("user", user);
            return "users/detail";
        }
    }
}
```

**사용 예시**:
```bash
# HTML 요청
curl http://localhost:8080/api/users/1
# → HTML 페이지 반환

# JSON 요청
curl -H "Accept: application/json" http://localhost:8080/api/users/1
# → {"id":1,"name":"John","email":"john@example.com"}

# XML 요청
curl -H "Accept: application/xml" http://localhost:8080/api/users/1
# → <user><id>1</id><name>John</name><email>john@example.com</email></user>

# 쿼리 파라미터로도 가능
curl http://localhost:8080/api/users/1?format=json
```

**자동 Content Negotiation (Spring MVC 내장)**:
```java
@RestController
@RequestMapping("/api/products")
public class ProductApiController {

    @GetMapping(
        value = "/{id}",
        produces = {
            MediaType.APPLICATION_JSON_VALUE,
            MediaType.APPLICATION_XML_VALUE
        }
    )
    public Product getProduct(@PathVariable Long id) {
        return productService.findById(id);
        // Spring이 Accept 헤더를 보고 자동으로 JSON/XML 변환
    }
}
```

**실무 활용**:
- **웹 브라우저**: HTML
- **모바일 앱**: JSON
- **레거시 시스템**: XML
- **관리자**: Excel (Custom View)

---

## 💼 면접 질문

<details>
<summary><strong>Q1: ViewResolver의 동작 원리를 설명해주세요.</strong></summary>

**모범 답안**:
> "ViewResolver는 Controller가 반환한 논리적 View 이름을 실제 View 객체로 변환하는 역할을 합니다. 예를 들어 Controller에서 'home'이라는 문자열을 반환하면, InternalResourceViewResolver는 prefix('/WEB-INF/views/')와 suffix('.jsp')를 붙여 '/WEB-INF/views/home.jsp'로 변환합니다. 여러 ViewResolver가 등록된 경우 우선순위(order)에 따라 순차적으로 시도하며, 가장 먼저 View를 찾은 Resolver가 해당 View를 반환합니다."

**꼬리 질문**:
- Q: "여러 ViewResolver를 동시에 사용할 수 있나요?"
- A: "네, 가능합니다. order 속성으로 우선순위를 지정하면 BeanNameViewResolver로 먼저 찾고, 없으면 InternalResourceViewResolver로 찾는 식으로 구성할 수 있습니다."

</details>

---

## 📝 핵심 정리

### ViewResolver 종류

| ViewResolver | 용도 | 예시 |
|-------------|------|------|
| InternalResourceViewResolver | JSP | "home" → /WEB-INF/views/home.jsp |
| ThymeleafViewResolver | Thymeleaf | "home" → classpath:/templates/home.html |
| BeanNameViewResolver | 커스텀 View | "excelView" → excelView Bean |
| ContentNegotiatingViewResolver | 자동 선택 | Accept 헤더에 따라 JSON/XML/HTML |

### Model 데이터 전달 방법

| 방법 | 장점 | 단점 |
|------|------|------|
| Model | 간결함 | 기본 기능만 |
| ModelMap | Map 기능 사용 | 복잡함 |
| ModelAndView | View 이름도 포함 | 장황함 |
| @ModelAttribute | 자동 실행 | 성능 오버헤드 |

---

## 🚀 다음 단계

### 다음 장: 14장 - 폼 처리와 검증

**다음 장으로 이동**: [다음: 14장 폼 처리와 검증 →](SpringMVC-Part6-14-Form-Validation.md)

**목차로 돌아가기**: [📚 전체 목차](README.md)
