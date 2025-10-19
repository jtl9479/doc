# 12장-2: 컨트롤러와 요청 매핑 - 고급

> **학습 목표**: @ModelAttribute, 파일 업로드, 세션 관리, 비동기 처리 등 고급 Controller 기능을 마스터합니다.

**⏱️ 예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐⭐☆ (4개/5개)

---

## 📚 목차
- [핵심 개념](#핵심-개념)
- [기본 실습](#기본-실습)
- [실전 프로젝트](#실전-프로젝트)
- [FAQ](#faq)
- [면접 질문 리스트](#면접-질문-리스트)
- [핵심 정리](#핵심-정리)

---

## 📖 핵심 개념

### 1. @ModelAttribute 상세

#### 메서드 레벨 @ModelAttribute

**모든 요청에서 실행되는 공통 데이터 준비**:

```java
@Controller
@RequestMapping("/products")
public class ProductController {

    @Autowired
    private CategoryService categoryService;

    // 모든 핸들러 메서드가 실행되기 전에 자동 실행
    // 모든 View에서 "categories" 사용 가능
    @ModelAttribute("categories")
    public List<Category> populateCategories() {
        return categoryService.findAll();
    }

    // 이 메서드도 categories를 사용 가능
    @GetMapping("/new")
    public String newProductForm(Model model) {
        model.addAttribute("product", new Product());
        // categories는 자동으로 추가됨
        return "products/form";
    }

    @GetMapping("/{id}/edit")
    public String editForm(@PathVariable Long id, Model model) {
        model.addAttribute("product", productService.findById(id));
        // categories는 자동으로 추가됨
        return "products/form";
    }
}
```

#### 파라미터 레벨 @ModelAttribute

**폼 데이터 자동 바인딩**:

```java
@Controller
@RequestMapping("/users")
public class UserController {

    // DTO 클래스
    @Data
    public static class UserForm {
        private String username;
        private String email;
        private String password;
        private int age;
        private String address;
    }

    // @ModelAttribute: 요청 파라미터 → 객체로 자동 바인딩
    @PostMapping("/register")
    public String register(@ModelAttribute UserForm userForm, Model model) {
        // userForm 객체에 자동으로 데이터가 채워짐
        // username=john&email=john@example.com&password=1234&age=25
        // → userForm.getUsername() = "john"

        User user = userService.register(userForm);
        model.addAttribute("user", user);
        return "users/success";
    }

    // @ModelAttribute 생략 가능 (Spring이 자동 인식)
    @PostMapping("/update")
    public String update(UserForm userForm) {  // @ModelAttribute 생략
        userService.update(userForm);
        return "redirect:/users";
    }

    // 이름 지정 가능
    @PostMapping("/create")
    public String create(@ModelAttribute("newUser") UserForm userForm) {
        // View에서 ${newUser.username} 으로 접근 가능
        return "users/confirm";
    }
}
```

#### 중첩 객체 바인딩

```java
@Data
public class OrderForm {
    private Long productId;
    private int quantity;
    private Address shippingAddress;  // 중첩 객체
    private PaymentInfo payment;      // 중첩 객체

    @Data
    public static class Address {
        private String street;
        private String city;
        private String zipCode;
    }

    @Data
    public static class PaymentInfo {
        private String cardNumber;
        private String cardHolder;
        private String expiryDate;
    }
}

@Controller
public class OrderController {

    @PostMapping("/orders")
    public String createOrder(@ModelAttribute OrderForm orderForm) {
        // 요청 파라미터:
        // productId=123
        // quantity=2
        // shippingAddress.street=123 Main St
        // shippingAddress.city=Seoul
        // shippingAddress.zipCode=12345
        // payment.cardNumber=1234-5678-9012-3456
        // payment.cardHolder=John Doe
        // payment.expiryDate=12/25

        // Spring이 자동으로 중첩 객체까지 바인딩
        System.out.println(orderForm.getShippingAddress().getCity());  // Seoul
        System.out.println(orderForm.getPayment().getCardHolder());    // John Doe

        return "orders/success";
    }
}
```

### 2. @SessionAttributes

**여러 요청에 걸쳐 데이터 유지**:

```java
@Controller
@RequestMapping("/checkout")
@SessionAttributes("cart")  // "cart"를 세션에 저장
public class CheckoutController {

    // Step 1: 장바구니 생성 (세션에 저장)
    @GetMapping("/start")
    public String startCheckout(Model model) {
        Cart cart = new Cart();
        model.addAttribute("cart", cart);  // 세션에 저장됨
        return "checkout/step1";
    }

    // Step 2: 배송 정보 입력 (세션의 cart 사용)
    @PostMapping("/shipping")
    public String addShippingInfo(
        @ModelAttribute("cart") Cart cart,  // 세션에서 가져옴
        @RequestParam String address
    ) {
        cart.setShippingAddress(address);
        return "checkout/step2";
    }

    // Step 3: 결제 정보 입력 (세션의 cart 사용)
    @PostMapping("/payment")
    public String addPaymentInfo(
        @ModelAttribute("cart") Cart cart,  // 세션에서 가져옴
        @RequestParam String cardNumber
    ) {
        cart.setCardNumber(cardNumber);
        return "checkout/step3";
    }

    // Step 4: 주문 완료 (세션 정리)
    @PostMapping("/complete")
    public String completeOrder(
        @ModelAttribute("cart") Cart cart,
        SessionStatus sessionStatus
    ) {
        orderService.createOrder(cart);
        sessionStatus.setComplete();  // 세션에서 cart 제거
        return "checkout/success";
    }
}
```

### 3. @InitBinder - 데이터 변환 커스터마이징

```java
@Controller
@RequestMapping("/events")
public class EventController {

    // 날짜 포맷 지정
    @InitBinder
    public void initBinder(WebDataBinder binder) {
        // String → LocalDate 변환
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
        binder.registerCustomEditor(LocalDate.class, new PropertyEditorSupport() {
            @Override
            public void setAsText(String text) {
                setValue(LocalDate.parse(text, formatter));
            }
        });

        // 특정 필드 바인딩 제외 (보안)
        binder.setDisallowedFields("id", "createdAt");

        // 빈 문자열을 null로 변환
        binder.registerCustomEditor(String.class, new StringTrimmerEditor(true));
    }

    @PostMapping
    public String createEvent(@ModelAttribute Event event) {
        // startDate는 "2024-10-15" 형태로 받아 LocalDate로 자동 변환됨
        // id, createdAt 필드는 바인딩되지 않음
        eventService.save(event);
        return "redirect:/events";
    }

    // 특정 컨트롤러에만 적용되는 InitBinder
    @InitBinder("eventForm")  // "eventForm"이라는 이름의 @ModelAttribute에만 적용
    public void initEventFormBinder(WebDataBinder binder) {
        binder.setValidator(new EventValidator());
    }
}
```

### 4. 파일 업로드

#### 단일 파일 업로드

```java
@Controller
@RequestMapping("/files")
public class FileUploadController {

    @Value("${file.upload.directory}")
    private String uploadDir;

    @PostMapping("/upload")
    public String uploadFile(
        @RequestParam("file") MultipartFile file,
        @RequestParam(required = false) String description,
        RedirectAttributes redirectAttributes
    ) {
        if (file.isEmpty()) {
            redirectAttributes.addFlashAttribute("error", "파일을 선택해주세요.");
            return "redirect:/files/upload-form";
        }

        try {
            // 파일 정보
            String originalFilename = file.getOriginalFilename();
            String contentType = file.getContentType();
            long size = file.getSize();

            // 파일명 중복 방지 (UUID 사용)
            String savedFilename = UUID.randomUUID().toString() + "_" + originalFilename;

            // 파일 저장
            Path uploadPath = Paths.get(uploadDir);
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }

            Path filePath = uploadPath.resolve(savedFilename);
            file.transferTo(filePath.toFile());

            // DB에 파일 정보 저장
            FileEntity fileEntity = FileEntity.builder()
                .originalFilename(originalFilename)
                .savedFilename(savedFilename)
                .contentType(contentType)
                .size(size)
                .description(description)
                .uploadPath(filePath.toString())
                .build();

            fileService.save(fileEntity);

            redirectAttributes.addFlashAttribute("message", "파일 업로드 성공: " + originalFilename);
            return "redirect:/files/list";

        } catch (IOException e) {
            redirectAttributes.addFlashAttribute("error", "파일 업로드 실패: " + e.getMessage());
            return "redirect:/files/upload-form";
        }
    }

    // 파일 다운로드
    @GetMapping("/download/{id}")
    public ResponseEntity<Resource> downloadFile(@PathVariable Long id) throws IOException {
        FileEntity fileEntity = fileService.findById(id);

        Path filePath = Paths.get(fileEntity.getUploadPath());
        Resource resource = new UrlResource(filePath.toUri());

        if (!resource.exists()) {
            throw new FileNotFoundException("파일을 찾을 수 없습니다.");
        }

        // 한글 파일명 처리
        String encodedFilename = URLEncoder.encode(fileEntity.getOriginalFilename(), StandardCharsets.UTF_8)
            .replaceAll("\\+", "%20");

        return ResponseEntity.ok()
            .contentType(MediaType.parseMediaType(fileEntity.getContentType()))
            .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + encodedFilename + "\"")
            .body(resource);
    }
}
```

#### 다중 파일 업로드

```java
@Controller
@RequestMapping("/gallery")
public class GalleryController {

    @PostMapping("/upload-multiple")
    public String uploadMultipleFiles(
        @RequestParam("files") List<MultipartFile> files,
        @RequestParam String albumName,
        RedirectAttributes redirectAttributes
    ) {
        if (files.isEmpty()) {
            redirectAttributes.addFlashAttribute("error", "파일을 선택해주세요.");
            return "redirect:/gallery/upload-form";
        }

        List<String> uploadedFiles = new ArrayList<>();
        List<String> failedFiles = new ArrayList<>();

        for (MultipartFile file : files) {
            if (file.isEmpty()) continue;

            try {
                String savedFilename = UUID.randomUUID().toString() + "_" + file.getOriginalFilename();
                Path filePath = Paths.get(uploadDir).resolve(savedFilename);
                file.transferTo(filePath.toFile());

                // DB 저장
                galleryService.savePhoto(albumName, file.getOriginalFilename(), savedFilename);

                uploadedFiles.add(file.getOriginalFilename());
            } catch (Exception e) {
                failedFiles.add(file.getOriginalFilename());
            }
        }

        redirectAttributes.addFlashAttribute("uploadedFiles", uploadedFiles);
        redirectAttributes.addFlashAttribute("failedFiles", failedFiles);

        return "redirect:/gallery/albums/" + albumName;
    }
}
```

**application.yml 설정**:

```yaml
spring:
  servlet:
    multipart:
      enabled: true
      max-file-size: 10MB       # 파일 하나당 최대 크기
      max-request-size: 50MB    # 요청 전체 최대 크기
      file-size-threshold: 2KB  # 메모리에 저장할 최소 크기

file:
  upload:
    directory: /var/uploads
```

### 5. @RequestBody와 @ResponseBody

#### JSON 요청/응답 처리

```java
@RestController
@RequestMapping("/api/products")
public class ProductApiController {

    // @RequestBody: JSON → 객체 자동 변환
    @PostMapping
    public ResponseEntity<ProductResponse> createProduct(
        @RequestBody @Valid ProductRequest request
    ) {
        // Content-Type: application/json
        // {"name":"Laptop","price":1000000,"category":"electronics"}
        // → ProductRequest 객체로 자동 변환

        Product product = productService.create(request);
        ProductResponse response = ProductResponse.from(product);

        // @RestController이므로 @ResponseBody 자동 적용
        // ProductResponse → JSON 자동 변환
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    // @ResponseBody: 객체 → JSON 자동 변환
    @GetMapping("/{id}")
    public ProductResponse getProduct(@PathVariable Long id) {
        Product product = productService.findById(id);
        return ProductResponse.from(product);
        // → {"id":1,"name":"Laptop","price":1000000,"category":"electronics"}
    }

    // ResponseEntity로 HTTP 상태 코드와 헤더 제어
    @PutMapping("/{id}")
    public ResponseEntity<ProductResponse> updateProduct(
        @PathVariable Long id,
        @RequestBody @Valid ProductRequest request
    ) {
        Product updated = productService.update(id, request);
        return ResponseEntity.ok(ProductResponse.from(updated));
    }

    // 에러 응답도 JSON으로
    @ExceptionHandler(ProductNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(ProductNotFoundException ex) {
        ErrorResponse error = new ErrorResponse(404, ex.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
}
```

### 6. HttpEntity와 ResponseEntity

```java
@RestController
@RequestMapping("/api/messages")
public class MessageApiController {

    // HttpEntity: 요청 본문 + 헤더
    @PostMapping
    public ResponseEntity<String> sendMessage(HttpEntity<MessageRequest> httpEntity) {
        // 헤더 접근
        HttpHeaders headers = httpEntity.getHeaders();
        String authToken = headers.getFirst("Authorization");

        // 본문 접근
        MessageRequest body = httpEntity.getBody();

        messageService.send(body, authToken);

        // ResponseEntity: 응답 본문 + 상태 코드 + 헤더
        HttpHeaders responseHeaders = new HttpHeaders();
        responseHeaders.add("X-Message-Id", "12345");

        return new ResponseEntity<>("메시지 전송 완료", responseHeaders, HttpStatus.CREATED);
    }

    // ResponseEntity로 상세한 HTTP 응답 제어
    @GetMapping("/{id}")
    public ResponseEntity<Message> getMessage(@PathVariable Long id) {
        Optional<Message> message = messageService.findById(id);

        return message
            .map(m -> ResponseEntity.ok()
                .header("X-Message-Type", m.getType())
                .cacheControl(CacheControl.maxAge(60, TimeUnit.SECONDS))
                .body(m))
            .orElse(ResponseEntity.notFound().build());
    }
}
```

---

## 💻 기본 실습

### 실습: 파일 업로드 게시판

**난이도**: ⭐⭐⭐⭐☆

**프로젝트 구조**:

```
file-board/
├── src/main/java/com/example/fileboard/
│   ├── controller/
│   │   └── BoardController.java
│   ├── service/
│   │   └── BoardService.java
│   ├── repository/
│   │   └── BoardRepository.java
│   ├── domain/
│   │   ├── Board.java
│   │   └── FileAttachment.java
│   └── dto/
│       └── BoardForm.java
└── src/main/resources/
    ├── templates/
    │   └── board/
    │       ├── list.html
    │       ├── detail.html
    │       └── form.html
    └── application.yml
```

**Entity 클래스**:

```java
@Entity
@Table(name = "boards")
@Data
@NoArgsConstructor
public class Board {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(nullable = false)
    private String author;

    @Lob
    @Column(nullable = false)
    private String content;

    @OneToMany(mappedBy = "board", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<FileAttachment> attachments = new ArrayList<>();

    @CreationTimestamp
    private LocalDateTime createdAt;

    public void addAttachment(FileAttachment attachment) {
        attachments.add(attachment);
        attachment.setBoard(this);
    }
}

@Entity
@Table(name = "file_attachments")
@Data
@NoArgsConstructor
public class FileAttachment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String originalFilename;

    @Column(nullable = false)
    private String savedFilename;

    @Column(nullable = false)
    private String contentType;

    @Column(nullable = false)
    private Long fileSize;

    @Column(nullable = false)
    private String filePath;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "board_id")
    private Board board;

    @CreationTimestamp
    private LocalDateTime uploadedAt;
}
```

**Controller**:

```java
@Controller
@RequestMapping("/board")
public class BoardController {

    @Autowired
    private BoardService boardService;

    @Value("${file.upload.directory}")
    private String uploadDir;

    // 게시글 작성 폼
    @GetMapping("/new")
    public String newForm(Model model) {
        model.addAttribute("board", new Board());
        return "board/form";
    }

    // 게시글 작성 (파일 첨부)
    @PostMapping
    public String create(
        @ModelAttribute Board board,
        @RequestParam(value = "files", required = false) List<MultipartFile> files,
        RedirectAttributes redirectAttributes
    ) {
        try {
            // 파일 업로드 처리
            if (files != null && !files.isEmpty()) {
                for (MultipartFile file : files) {
                    if (!file.isEmpty()) {
                        FileAttachment attachment = saveFile(file);
                        board.addAttachment(attachment);
                    }
                }
            }

            Board saved = boardService.save(board);
            redirectAttributes.addFlashAttribute("message", "게시글이 등록되었습니다.");
            return "redirect:/board/" + saved.getId();

        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("error", "게시글 등록 실패: " + e.getMessage());
            return "redirect:/board/new";
        }
    }

    // 게시글 상세
    @GetMapping("/{id}")
    public String detail(@PathVariable Long id, Model model) {
        Board board = boardService.findById(id);
        model.addAttribute("board", board);
        return "board/detail";
    }

    // 파일 다운로드
    @GetMapping("/download/{fileId}")
    public ResponseEntity<Resource> downloadFile(@PathVariable Long fileId) throws IOException {
        FileAttachment fileAttachment = boardService.findFileById(fileId);

        Path filePath = Paths.get(fileAttachment.getFilePath());
        Resource resource = new UrlResource(filePath.toUri());

        if (!resource.exists()) {
            throw new FileNotFoundException("파일을 찾을 수 없습니다.");
        }

        String encodedFilename = URLEncoder.encode(
            fileAttachment.getOriginalFilename(),
            StandardCharsets.UTF_8
        ).replaceAll("\\+", "%20");

        return ResponseEntity.ok()
            .contentType(MediaType.parseMediaType(fileAttachment.getContentType()))
            .header(HttpHeaders.CONTENT_DISPOSITION,
                    "attachment; filename=\"" + encodedFilename + "\"")
            .body(resource);
    }

    // 파일 저장 헬퍼 메서드
    private FileAttachment saveFile(MultipartFile file) throws IOException {
        String originalFilename = file.getOriginalFilename();
        String savedFilename = UUID.randomUUID().toString() + "_" + originalFilename;

        Path uploadPath = Paths.get(uploadDir);
        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }

        Path filePath = uploadPath.resolve(savedFilename);
        file.transferTo(filePath.toFile());

        FileAttachment attachment = new FileAttachment();
        attachment.setOriginalFilename(originalFilename);
        attachment.setSavedFilename(savedFilename);
        attachment.setContentType(file.getContentType());
        attachment.setFileSize(file.getSize());
        attachment.setFilePath(filePath.toString());

        return attachment;
    }
}
```

**Thymeleaf 템플릿 (form.html)**:

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>게시글 작성</title>
</head>
<body>
    <h1>게시글 작성</h1>

    <form th:action="@{/board}" method="post" enctype="multipart/form-data">
        <div>
            <label>제목</label>
            <input type="text" name="title" required>
        </div>

        <div>
            <label>작성자</label>
            <input type="text" name="author" required>
        </div>

        <div>
            <label>내용</label>
            <textarea name="content" rows="10" required></textarea>
        </div>

        <div>
            <label>파일 첨부</label>
            <input type="file" name="files" multiple>
            <small>여러 파일을 선택할 수 있습니다.</small>
        </div>

        <button type="submit">등록</button>
        <a th:href="@{/board}">취소</a>
    </form>
</body>
</html>
```

---

## ❓ FAQ

<details>
<summary><strong>Q1: @ModelAttribute와 @RequestBody의 차이는 무엇인가요?</strong></summary>

**A**: @ModelAttribute는 폼 데이터(application/x-www-form-urlencoded)를, @RequestBody는 JSON/XML 등을 처리합니다.

| 특징 | @ModelAttribute | @RequestBody |
|------|----------------|--------------|
| 데이터 형식 | Form Data (key=value) | JSON, XML |
| Content-Type | application/x-www-form-urlencoded | application/json |
| 사용 사례 | HTML 폼 제출 | REST API |
| 중첩 객체 | user.address.city 형태 | {"user":{"address":{"city":"Seoul"}}} |

</details>

<details>
<summary><strong>Q2: 파일 업로드 시 보안 주의사항은?</strong></summary>

**A**: 파일 확장자 검증, 크기 제한, 파일명 검증, 경로 검증이 필수입니다.

**보안 체크리스트**:
```java
// 1. 파일 확장자 화이트리스트
private static final List<String> ALLOWED_EXTENSIONS = Arrays.asList("jpg", "png", "pdf", "docx");

// 2. Content-Type 검증
private void validateFile(MultipartFile file) {
    String extension = FilenameUtils.getExtension(file.getOriginalFilename());
    if (!ALLOWED_EXTENSIONS.contains(extension.toLowerCase())) {
        throw new InvalidFileException("허용되지 않는 파일 형식입니다.");
    }

    // 3. 파일 크기 검증
    if (file.getSize() > 10 * 1024 * 1024) {  // 10MB
        throw new InvalidFileException("파일 크기가 너무 큽니다.");
    }

    // 4. 실제 Content-Type 검증 (확장자 속임수 방지)
    String contentType = file.getContentType();
    if (!contentType.startsWith("image/") && !contentType.equals("application/pdf")) {
        throw new InvalidFileException("허용되지 않는 파일 타입입니다.");
    }

    // 5. 파일명에서 경로 문자 제거
    String filename = file.getOriginalFilename();
    if (filename.contains("..") || filename.contains("/") || filename.contains("\\")) {
        throw new InvalidFileException("잘못된 파일명입니다.");
    }
}
```

</details>

<details>
<summary><strong>Q3: @SessionAttributes는 어떻게 동작하나요?</strong></summary>

**A**: @SessionAttributes는 Model에 추가된 특정 속성을 HTTP 세션에도 자동으로 저장합니다.

**동작 원리**:
```java
@Controller
@SessionAttributes("cart")  // Model의 "cart"를 세션에도 저장
public class CartController {

    @GetMapping("/cart/init")
    public String initCart(Model model) {
        Cart cart = new Cart();
        model.addAttribute("cart", cart);  // Model + 세션에 저장
        return "cart/view";
    }

    @PostMapping("/cart/add")
    public String addItem(@ModelAttribute("cart") Cart cart, @RequestParam Long productId) {
        // 세션에서 cart를 가져와 사용
        cart.addItem(productId);
        // 자동으로 세션에 다시 저장됨
        return "cart/view";
    }

    @PostMapping("/cart/checkout")
    public String checkout(@ModelAttribute("cart") Cart cart, SessionStatus sessionStatus) {
        orderService.createOrder(cart);
        sessionStatus.setComplete();  // 세션에서 cart 제거
        return "checkout/success";
    }
}
```

**주의사항**:
- SessionStatus.setComplete()를 호출해야 세션이 정리됩니다
- 여러 탭에서 동시 작업 시 데이터 충돌 가능
- 세션 만료 시간 고려 필요

</details>

<details>
<summary><strong>Q4: MultipartFile의 주요 메서드는?</strong></summary>

**A**: MultipartFile은 업로드된 파일에 대한 정보와 데이터를 제공합니다.

**주요 메서드**:
```java
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    // 1. 파일 정보 조회
    String originalFilename = file.getOriginalFilename();  // 원본 파일명
    String contentType = file.getContentType();            // MIME 타입
    long size = file.getSize();                            // 파일 크기(바이트)
    boolean empty = file.isEmpty();                        // 빈 파일 여부

    // 2. 파일 내용 읽기
    byte[] bytes = file.getBytes();                        // 전체 바이트 배열
    InputStream inputStream = file.getInputStream();       // InputStream

    // 3. 파일 저장
    file.transferTo(new File("/path/to/save/file.jpg"));  // 파일로 저장

    return "success";
}
```

**실무 활용**:
```java
private void validateAndSaveFile(MultipartFile file) throws IOException {
    // 검증
    if (file.isEmpty()) {
        throw new IllegalArgumentException("빈 파일입니다.");
    }

    if (file.getSize() > 10 * 1024 * 1024) {  // 10MB
        throw new IllegalArgumentException("파일이 너무 큽니다.");
    }

    String contentType = file.getContentType();
    if (!contentType.startsWith("image/")) {
        throw new IllegalArgumentException("이미지 파일만 업로드 가능합니다.");
    }

    // 저장
    String savedFilename = UUID.randomUUID() + "_" + file.getOriginalFilename();
    Path path = Paths.get(uploadDir, savedFilename);
    file.transferTo(path.toFile());
}
```

</details>

<details>
<summary><strong>Q5: @InitBinder는 언제 사용하나요?</strong></summary>

**A**: @InitBinder는 데이터 바인딩을 커스터마이징할 때 사용합니다.

**주요 사용 사례**:

**1. 날짜 포맷 지정**:
```java
@InitBinder
public void initBinder(WebDataBinder binder) {
    SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
    binder.registerCustomEditor(Date.class, new CustomDateEditor(dateFormat, true));
}
```

**2. 특정 필드 바인딩 제외 (보안)**:
```java
@InitBinder
public void initBinder(WebDataBinder binder) {
    // id, password 필드는 바인딩하지 않음
    binder.setDisallowedFields("id", "password", "createdAt");
}

@PostMapping("/users")
public String createUser(@ModelAttribute User user) {
    // 요청에 id=999가 있어도 user.getId()는 null
    // 보안상 중요한 필드를 클라이언트가 임의로 설정하는 것을 방지
}
```

**3. 빈 문자열을 null로 변환**:
```java
@InitBinder
public void initBinder(WebDataBinder binder) {
    binder.registerCustomEditor(String.class, new StringTrimmerEditor(true));
}
// 빈 문자열("")을 null로 변환하여 DB에 저장
```

**4. 커스텀 Validator 등록**:
```java
@InitBinder("userForm")
public void initUserFormBinder(WebDataBinder binder) {
    binder.setValidator(new UserFormValidator());
}
```

</details>

<details>
<summary><strong>Q6: 파일 다운로드 시 한글 파일명은 어떻게 처리하나요?</strong></summary>

**A**: URL 인코딩을 사용하여 한글 파일명을 처리합니다.

```java
@GetMapping("/download/{fileId}")
public ResponseEntity<Resource> downloadFile(@PathVariable Long fileId) throws IOException {
    FileEntity fileEntity = fileService.findById(fileId);

    // 파일 리소스 로드
    Path filePath = Paths.get(fileEntity.getFilePath());
    Resource resource = new UrlResource(filePath.toUri());

    // 한글 파일명 인코딩
    String originalFilename = fileEntity.getOriginalFilename();  // "한글파일.pdf"

    // UTF-8 URL 인코딩 + 공백을 %20으로 변환
    String encodedFilename = URLEncoder.encode(originalFilename, StandardCharsets.UTF_8)
        .replaceAll("\\+", "%20");

    // Content-Disposition 헤더 설정
    return ResponseEntity.ok()
        .contentType(MediaType.parseMediaType(fileEntity.getContentType()))
        .header(HttpHeaders.CONTENT_DISPOSITION,
                "attachment; filename=\"" + encodedFilename + "\"")
        .body(resource);
}
```

**브라우저별 차이**:
```java
// 더욱 호환성 높은 방법 (RFC 2231)
String encodedFilename = URLEncoder.encode(originalFilename, StandardCharsets.UTF_8)
    .replaceAll("\\+", "%20");

String contentDisposition = String.format(
    "attachment; filename=\"%s\"; filename*=UTF-8''%s",
    originalFilename,  // 일반 ASCII
    encodedFilename    // UTF-8 인코딩
);

return ResponseEntity.ok()
    .header(HttpHeaders.CONTENT_DISPOSITION, contentDisposition)
    .body(resource);
```

</details>

<details>
<summary><strong>Q7: @ModelAttribute는 언제 생략할 수 있나요?</strong></summary>

**A**: Spring이 자동으로 인식하는 경우 @ModelAttribute를 생략할 수 있습니다.

**생략 가능한 경우**:
```java
@Controller
public class UserController {

    // ✅ 생략 가능 - 커스텀 객체
    @PostMapping("/users")
    public String createUser(UserForm userForm) {  // @ModelAttribute 생략
        // Spring이 자동으로 @ModelAttribute로 인식
    }

    // ✅ 생략 불가 - 명확히 하기 위해
    @PostMapping("/users/v2")
    public String createUserV2(@ModelAttribute UserForm userForm) {
        // 코드 가독성을 위해 명시적으로 작성 권장
    }

    // ✅ 생략 불가 - 이름을 지정할 때
    @PostMapping("/users/v3")
    public String createUserV3(@ModelAttribute("newUser") UserForm userForm) {
        // View에서 ${newUser}로 접근
    }
}
```

**생략 규칙**:
```
1. 단순 타입 (String, int, Long 등) → @RequestParam으로 인식
2. 복합 객체 (커스텀 클래스) → @ModelAttribute로 인식
3. @RequestBody가 붙으면 → JSON/XML로 처리

예시:
- String name → @RequestParam String name
- UserForm form → @ModelAttribute UserForm form
- @RequestBody UserForm form → JSON 파싱
```

**실무 권장**:
```java
// ❌ 헷갈림
@PostMapping("/api/users")
public String create(UserForm form) {  // @ModelAttribute인지 @RequestBody인지 불명확
}

// ✅ 명확함
@PostMapping("/users")
public String create(@ModelAttribute UserForm form) {  // Form 데이터
}

@PostMapping("/api/users")
public ResponseEntity<User> createApi(@RequestBody UserForm form) {  // JSON
}
```

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. @ModelAttribute와 @RequestParam의 차이를 설명해주세요.</strong></summary>

**모범 답안**:
> "@RequestParam은 개별 파라미터를 하나씩 받는 반면, @ModelAttribute는 여러 파라미터를 객체로 묶어서 받습니다. 예를 들어 회원가입 폼에서 이름, 이메일, 비밀번호, 주소 등 10개의 필드가 있다면, @RequestParam으로는 10개의 파라미터를 일일이 선언해야 하지만, @ModelAttribute를 사용하면 UserForm 객체 하나로 받을 수 있습니다. 또한 @ModelAttribute는 자동으로 Model에 추가되어 View에서도 사용할 수 있습니다."

</details>

---

#### Q4. 대용량 파일 업로드를 처리할 때 고려해야 할 사항과 최적화 방법을 설명해주세요.

**답변**:

대용량 파일 업로드 시 **메모리, 네트워크, 시간**을 모두 고려해야 합니다.

**1. 스트리밍 방식으로 처리**:
```java
// ❌ 나쁜 예: 전체 파일을 메모리에 로드
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) throws IOException {
    byte[] bytes = file.getBytes();  // ⚠️ 대용량 파일이면 OutOfMemoryError
    // ...
}

// ✅ 좋은 예: 스트리밍으로 처리
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) throws IOException {
    Path uploadPath = Paths.get(uploadDir, file.getOriginalFilename());

    // 스트리밍으로 직접 파일에 쓰기 (메모리 절약)
    try (InputStream inputStream = file.getInputStream();
         OutputStream outputStream = Files.newOutputStream(uploadPath)) {

        byte[] buffer = new byte[8192];  // 8KB 버퍼
        int bytesRead;
        while ((bytesRead = inputStream.read(buffer)) != -1) {
            outputStream.write(buffer, 0, bytesRead);
        }
    }
}
```

**2. 청크 업로드 (Chunk Upload)**:
```javascript
// 프론트엔드: 파일을 작은 조각으로 나누어 업로드
const CHUNK_SIZE = 1024 * 1024;  // 1MB

async function uploadFile(file) {
    const totalChunks = Math.ceil(file.size / CHUNK_SIZE);

    for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
        const start = chunkIndex * CHUNK_SIZE;
        const end = Math.min(start + CHUNK_SIZE, file.size);
        const chunk = file.slice(start, end);

        const formData = new FormData();
        formData.append('chunk', chunk);
        formData.append('chunkIndex', chunkIndex);
        formData.append('totalChunks', totalChunks);
        formData.append('filename', file.name);

        await fetch('/api/upload/chunk', {
            method: 'POST',
            body: formData
        });
    }

    // 모든 청크 업로드 완료 후 병합 요청
    await fetch('/api/upload/merge', {
        method: 'POST',
        body: JSON.stringify({ filename: file.name })
    });
}
```

```java
// 백엔드: 청크 받아서 저장
@PostMapping("/upload/chunk")
public ResponseEntity<String> uploadChunk(
    @RequestParam("chunk") MultipartFile chunk,
    @RequestParam int chunkIndex,
    @RequestParam int totalChunks,
    @RequestParam String filename
) throws IOException {
    // 임시 디렉토리에 청크 저장
    Path chunkPath = Paths.get(tempDir, filename + ".part" + chunkIndex);
    chunk.transferTo(chunkPath.toFile());

    return ResponseEntity.ok("Chunk " + chunkIndex + " uploaded");
}

@PostMapping("/upload/merge")
public ResponseEntity<String> mergeChunks(@RequestBody MergeRequest request) throws IOException {
    String filename = request.getFilename();
    Path finalPath = Paths.get(uploadDir, filename);

    // 모든 청크를 하나의 파일로 병합
    try (OutputStream outputStream = Files.newOutputStream(finalPath)) {
        for (int i = 0; i < request.getTotalChunks(); i++) {
            Path chunkPath = Paths.get(tempDir, filename + ".part" + i);

            Files.copy(chunkPath, outputStream);
            Files.delete(chunkPath);  // 임시 청크 삭제
        }
    }

    return ResponseEntity.ok("File merged successfully");
}
```

**3. 진행률 표시 (Progress Tracking)**:
```java
@RestController
@RequestMapping("/api/upload")
public class UploadProgressController {

    private final ConcurrentHashMap<String, Integer> uploadProgress = new ConcurrentHashMap<>();

    @PostMapping("/chunk")
    public ResponseEntity<String> uploadChunk(
        @RequestParam("chunk") MultipartFile chunk,
        @RequestParam int chunkIndex,
        @RequestParam int totalChunks,
        @RequestParam String uploadId
    ) throws IOException {
        // 청크 저장
        saveChunk(chunk, chunkIndex, uploadId);

        // 진행률 계산 및 저장
        int progress = (int) (((chunkIndex + 1) / (double) totalChunks) * 100);
        uploadProgress.put(uploadId, progress);

        return ResponseEntity.ok("Chunk uploaded");
    }

    // SSE (Server-Sent Events)로 진행률 전송
    @GetMapping(value = "/progress/{uploadId}", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<Integer>> getProgress(@PathVariable String uploadId) {
        return Flux.interval(Duration.ofMillis(500))
            .map(tick -> ServerSentEvent.<Integer>builder()
                .data(uploadProgress.getOrDefault(uploadId, 0))
                .build())
            .takeWhile(event -> event.data() < 100);
    }
}
```

**4. 비동기 처리**:
```java
@RestController
@RequestMapping("/api/upload")
public class AsyncUploadController {

    @Autowired
    private AsyncUploadService uploadService;

    @PostMapping("/async")
    public ResponseEntity<UploadResponse> uploadAsync(
        @RequestParam("file") MultipartFile file
    ) throws IOException {
        // 파일을 임시 저장
        Path tempPath = Files.createTempFile("upload_", file.getOriginalFilename());
        file.transferTo(tempPath.toFile());

        // 비동기로 처리 (즉시 응답 반환)
        String uploadId = UUID.randomUUID().toString();
        uploadService.processAsync(tempPath, uploadId);

        UploadResponse response = new UploadResponse(uploadId, "Processing");
        return ResponseEntity.accepted().body(response);
    }

    @GetMapping("/status/{uploadId}")
    public ResponseEntity<UploadStatus> getStatus(@PathVariable String uploadId) {
        UploadStatus status = uploadService.getStatus(uploadId);
        return ResponseEntity.ok(status);
    }
}

@Service
public class AsyncUploadService {

    @Async
    public void processAsync(Path tempPath, String uploadId) {
        try {
            // 1. 바이러스 스캔
            virusScanService.scan(tempPath);

            // 2. 파일 처리 (압축, 썸네일 생성 등)
            processFile(tempPath);

            // 3. 영구 저장소로 이동
            Path finalPath = moveToStorage(tempPath);

            // 4. DB에 메타데이터 저장
            saveMetadata(finalPath, uploadId);

            // 5. 상태 업데이트
            updateStatus(uploadId, "COMPLETED");

        } catch (Exception e) {
            updateStatus(uploadId, "FAILED");
            log.error("Upload failed: " + uploadId, e);
        }
    }
}
```

**5. 설정 최적화**:
```yaml
# application.yml
spring:
  servlet:
    multipart:
      enabled: true
      max-file-size: 1GB          # 파일 최대 크기
      max-request-size: 1GB       # 요청 최대 크기
      file-size-threshold: 10MB   # 이 크기 이상은 디스크에 임시 저장
      location: /tmp/uploads      # 임시 저장 위치

server:
  tomcat:
    max-swallow-size: -1          # 업로드 크기 제한 없음
    connection-timeout: 600000    # 10분 (대용량 파일 업로드 시간 고려)
```

**6. 클라우드 스토리지 직접 업로드 (S3 등)**:
```java
@RestController
@RequestMapping("/api/upload")
public class S3DirectUploadController {

    @Autowired
    private AmazonS3 s3Client;

    // 1. 프론트엔드에게 pre-signed URL 제공
    @GetMapping("/presigned-url")
    public ResponseEntity<PresignedUrlResponse> getPresignedUrl(
        @RequestParam String filename
    ) {
        String key = "uploads/" + UUID.randomUUID() + "/" + filename;

        // Pre-signed URL 생성 (1시간 유효)
        Date expiration = new Date(System.currentTimeMillis() + 3600000);
        GeneratePresignedUrlRequest request = new GeneratePresignedUrlRequest(bucketName, key)
            .withMethod(HttpMethod.PUT)
            .withExpiration(expiration);

        URL presignedUrl = s3Client.generatePresignedUrl(request);

        PresignedUrlResponse response = new PresignedUrlResponse(
            presignedUrl.toString(),
            key
        );

        return ResponseEntity.ok(response);
    }

    // 2. 프론트엔드는 pre-signed URL로 직접 S3에 업로드
    // fetch(presignedUrl, { method: 'PUT', body: file })

    // 3. 업로드 완료 후 메타데이터만 서버에 저장
    @PostMapping("/complete")
    public ResponseEntity<FileEntity> complete(@RequestBody UploadCompleteRequest request) {
        FileEntity fileEntity = FileEntity.builder()
            .s3Key(request.getKey())
            .filename(request.getFilename())
            .build();

        fileService.save(fileEntity);
        return ResponseEntity.ok(fileEntity);
    }
}
```

**성능 비교**:
```
┌─────────────────────┬──────────┬─────────┬──────────┐
│ 방식                │ 메모리   │ 속도    │ 안정성   │
├─────────────────────┼──────────┼─────────┼──────────┤
│ 기본 업로드         │ ★★☆☆☆  │ ★★★☆☆ │ ★★☆☆☆  │
│ 스트리밍            │ ★★★★☆  │ ★★★☆☆ │ ★★★☆☆  │
│ 청크 업로드         │ ★★★★★  │ ★★★★☆ │ ★★★★☆  │
│ 비동기 처리         │ ★★★★☆  │ ★★★★★ │ ★★★★★  │
│ S3 직접 업로드      │ ★★★★★  │ ★★★★★ │ ★★★★★  │
└─────────────────────┴──────────┴─────────┴──────────┘
```

---

#### Q5. WebDataBinder의 역할과 실무에서의 활용 사례를 설명해주세요.

**답변**:

WebDataBinder는 **HTTP 요청 데이터를 Java 객체로 바인딩할 때 사용되는 핵심 컴포넌트**입니다.

**주요 역할**:

1. **데이터 타입 변환**: 문자열 → 객체
2. **필드 제한**: 특정 필드 바인딩 차단
3. **커스텀 Validator 등록**
4. **PropertyEditor 등록**

**기본 동작 원리**:
```java
// HTTP 요청: username=john&age=25&createdAt=2024-10-15

@PostMapping("/users")
public String create(@ModelAttribute User user) {
    // WebDataBinder가 자동으로:
    // 1. "john" → user.setUsername("john")
    // 2. "25" → user.setAge(25)  (String → int 변환)
    // 3. "2024-10-15" → user.setCreatedAt(LocalDate) (설정된 경우)
}
```

**실무 활용 사례 1: 보안 필드 차단**:
```java
@Controller
@RequestMapping("/users")
public class UserController {

    @InitBinder
    public void initBinder(WebDataBinder binder) {
        // ✅ 클라이언트가 임의로 설정하면 안 되는 필드 차단
        binder.setDisallowedFields("id", "createdAt", "updatedAt", "role", "enabled");
    }

    @PostMapping
    public String createUser(@ModelAttribute User user) {
        // 요청에 id=999&role=ADMIN이 있어도 무시됨
        // → Mass Assignment 공격 방지

        userService.save(user);
        return "redirect:/users";
    }
}
```

**실무 활용 사례 2: 날짜/시간 포맷 지정**:
```java
@InitBinder
public void initBinder(WebDataBinder binder) {
    // LocalDate 포맷 지정
    DateTimeFormatter dateFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
    binder.registerCustomEditor(LocalDate.class, new PropertyEditorSupport() {
        @Override
        public void setAsText(String text) {
            setValue(LocalDate.parse(text, dateFormatter));
        }

        @Override
        public String getAsText() {
            LocalDate value = (LocalDate) getValue();
            return value != null ? value.format(dateFormatter) : "";
        }
    });

    // LocalDateTime 포맷 지정
    DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");
    binder.registerCustomEditor(LocalDateTime.class, new PropertyEditorSupport() {
        @Override
        public void setAsText(String text) {
            setValue(LocalDateTime.parse(text, dateTimeFormatter));
        }
    });
}

@PostMapping("/events")
public String createEvent(@ModelAttribute Event event) {
    // startDate: "2024-10-15" → LocalDate
    // startTime: "2024-10-15 14:30" → LocalDateTime
}
```

**실무 활용 사례 3: 빈 문자열 처리**:
```java
@InitBinder
public void initBinder(WebDataBinder binder) {
    // ✅ 빈 문자열("")을 null로 변환
    binder.registerCustomEditor(String.class, new StringTrimmerEditor(true));

    // 장점:
    // - DB에 빈 문자열 대신 null 저장
    // - @NotNull 검증이 제대로 작동
}

@PostMapping("/products")
public String create(@ModelAttribute Product product) {
    // description="" → product.getDescription() == null
    // → DB에 NULL 저장
}
```

**실무 활용 사례 4: 커스텀 타입 변환**:
```java
// 커스텀 타입
@Data
public class Money {
    private BigDecimal amount;
    private Currency currency;

    public Money(String text) {
        // "1000 USD" → amount=1000, currency=USD
        String[] parts = text.split(" ");
        this.amount = new BigDecimal(parts[0]);
        this.currency = Currency.getInstance(parts[1]);
    }
}

@InitBinder
public void initBinder(WebDataBinder binder) {
    binder.registerCustomEditor(Money.class, new PropertyEditorSupport() {
        @Override
        public void setAsText(String text) {
            setValue(new Money(text));
        }
    });
}

@PostMapping("/orders")
public String create(@ModelAttribute Order order) {
    // totalPrice="1000 USD" → Money 객체로 자동 변환
}
```

**실무 활용 사례 5: 특정 컨트롤러/모델에만 적용**:
```java
@Controller
public class MultiFormController {

    // userForm에만 적용
    @InitBinder("userForm")
    public void initUserBinder(WebDataBinder binder) {
        binder.setDisallowedFields("id", "role");
        binder.setValidator(new UserFormValidator());
    }

    // productForm에만 적용
    @InitBinder("productForm")
    public void initProductBinder(WebDataBinder binder) {
        binder.setDisallowedFields("id", "createdAt");
        binder.setValidator(new ProductFormValidator());
    }

    @PostMapping("/users")
    public String createUser(@ModelAttribute("userForm") UserForm userForm) {
        // initUserBinder 적용됨
    }

    @PostMapping("/products")
    public String createProduct(@ModelAttribute("productForm") ProductForm productForm) {
        // initProductBinder 적용됨
    }
}
```

**실무 활용 사례 6: 전역 InitBinder (모든 컨트롤러에 적용)**:
```java
@ControllerAdvice
public class GlobalBindingInitializer {

    @InitBinder
    public void initBinder(WebDataBinder binder) {
        // ✅ 모든 컨트롤러에 적용

        // 1. 보안 필드 차단
        binder.setDisallowedFields("class.*", "Class.*", "*.class.*", "*.Class.*");

        // 2. 빈 문자열 → null
        binder.registerCustomEditor(String.class, new StringTrimmerEditor(true));

        // 3. 날짜 포맷
        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
        dateFormat.setLenient(false);
        binder.registerCustomEditor(Date.class, new CustomDateEditor(dateFormat, true));
    }
}
```

**고급 활용: DataBinder API 직접 사용**:
```java
@PostMapping("/complex")
public String complex(@RequestParam Map<String, String> params) {
    // WebDataBinder를 직접 생성하여 사용
    ComplexForm form = new ComplexForm();
    DataBinder binder = new DataBinder(form);

    // 커스텀 설정
    binder.setDisallowedFields("id");
    binder.setValidator(new ComplexFormValidator());

    // 바인딩 수행
    binder.bind(new MutablePropertyValues(params));

    // 검증
    binder.validate();
    if (binder.getBindingResult().hasErrors()) {
        // 에러 처리
    }

    // form 객체 사용
    complexService.process(form);
    return "success";
}
```

**정리**:
```
WebDataBinder의 핵심 기능:
1. setDisallowedFields() → 보안 (가장 중요!)
2. registerCustomEditor() → 타입 변환
3. setValidator() → 검증 로직 통합
4. setRequiredFields() → 필수 필드 지정
5. setAllowedFields() → 허용 필드만 지정 (화이트리스트)
```

---

## 📝 핵심 정리

### 고급 어노테이션 정리

| 어노테이션 | 용도 | 예시 |
|-----------|------|------|
| `@ModelAttribute` | 폼 데이터 바인딩 | `@ModelAttribute UserForm form` |
| `@SessionAttributes` | 세션 데이터 관리 | `@SessionAttributes("cart")` |
| `@InitBinder` | 데이터 변환 커스터마이징 | 날짜 포맷, 필드 제외 |
| `@RequestBody` | JSON/XML 바인딩 | REST API 요청 처리 |
| `@ResponseBody` | JSON/XML 응답 | REST API 응답 반환 |
| `MultipartFile` | 파일 업로드 | `@RequestParam MultipartFile file` |

---

## 🚀 다음 단계

### 다음 장: 13장 - 뷰와 모델

**다음 장으로 이동**: [다음: 13장 뷰와 모델 →](SpringMVC-Part5-13-View-Model.md)

**목차로 돌아가기**: [📚 전체 목차](README.md)
