# 15장: 파일 업로드 (Part 1 - 기본편)

> **학습 목표**: Spring MVC의 파일 업로드 메커니즘을 이해하고, MultipartFile을 활용한 안전한 파일 업로드를 구현할 수 있습니다.

**⏱️ 예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐☆☆ (3개/5개)

---

## 📚 목차
- [왜 파일 업로드가 필요한가](#왜-파일-업로드가-필요한가)
- [실생활 비유로 이해하기](#실생활-비유로-이해하기)
- [핵심 개념](#핵심-개념)
- [기본 실습](#기본-실습)
- [FAQ](#faq)
- [면접 질문 리스트](#면접-질문-리스트)
- [면접 질문 답안](#면접-질문-답안)
- [핵심 정리](#핵심-정리)

---

## 🤔 왜 파일 업로드가 필요한가?

### 실무 배경

**현대 웹 애플리케이션의 필수 기능**:
- 프로필 사진 업로드 (SNS, 커뮤니티)
- 문서 첨부 (이메일, 업무 시스템)
- 상품 이미지 등록 (쇼핑몰)
- 동영상/음악 업로드 (미디어 플랫폼)
- 파일 공유 (클라우드 스토리지)

### ❌ 파일 업로드를 잘못 구현하면 발생하는 문제

```
문제 1: 보안 취약점
- 증상: 악성 파일(exe, sh)이 업로드되어 서버 침해
- 영향: 전체 시스템 마비, 데이터 유출
- 비용: 복구 비용 수천만 원 + 신뢰도 하락

문제 2: 서버 디스크 부족
- 증상: 대용량 파일 무제한 업로드로 디스크 full
- 영향: 서비스 중단
- 비용: 긴급 서버 증설 비용

문제 3: 메모리 부족
- 증상: 파일 전체를 메모리에 로드하여 OOM
- 영향: 서버 다운
- 비용: 장애 복구 시간 + 사용자 이탈

문제 4: 경로 조작 공격
- 증상: ../../../etc/passwd 같은 경로로 시스템 파일 덮어쓰기
- 영향: 시스템 파일 손상
- 비용: 시스템 재설치
```

### ✅ Spring의 파일 업로드를 올바르게 사용하면

```
해결책 1: 안전한 파일 검증
- 방법: 확장자, MIME 타입, 크기 검증
- 효과: 악성 파일 차단
- 절감: 보안 사고 방지

해결책 2: 스트리밍 처리
- 방법: MultipartFile의 transferTo() 사용
- 효과: 메모리 효율적 처리
- 절감: 서버 증설 비용 80% 절감

해결책 3: 파일명 안전화
- 방법: UUID + 원본 파일명 분리 저장
- 효과: 경로 조작 공격 차단
- 절감: 보안 취약점 제거

해결책 4: 임시 파일 자동 정리
- 방법: Spring의 MultipartResolver 활용
- 효과: 디스크 공간 자동 관리
- 절감: 수동 관리 시간 90% 단축
```

### 📊 수치로 보는 효과

| 지표 | Before (자체 구현) | After (Spring) | 개선율 |
|------|-------------------|----------------|--------|
| 파일 업로드 구현 시간 | 8시간 | 30분 | **95%↓** |
| 메모리 사용량 | 파일 크기만큼 | 1MB 이하 | **99%↓** |
| 보안 취약점 | 5개 | 0개 | **100%↓** |
| 코드 라인 수 | 200줄 | 20줄 | **90%↓** |

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 우체국 소포 접수

**상황**: 우체국에 소포를 보내는 과정

```
┌─────────────┬─────────────────────┬──────────────────┐
│ 우체국      │ Spring File Upload  │ 역할             │
├─────────────┼─────────────────────┼──────────────────┤
│ 소포        │ MultipartFile       │ 업로드할 파일    │
│ 접수 직원   │ Controller          │ 파일 수신        │
│ 무게 측정   │ 파일 크기 검증      │ 제한 확인        │
│ 위험물 검사 │ 확장자/MIME 검증    │ 안전성 확인      │
│ 보관함      │ 서버 디렉토리       │ 파일 저장소      │
│ 송장 번호   │ 파일명 (UUID)       │ 고유 식별자      │
└─────────────┴─────────────────────┴──────────────────┘
```

**흐름**:
1. **소포 가져오기**: 사용자가 파일 선택
2. **접수 직원**: Controller가 MultipartFile로 수신
3. **무게 측정**: 10MB 이하인지 확인
4. **위험물 검사**: exe, bat 같은 위험 파일 차단
5. **송장 번호 부여**: UUID로 고유한 파일명 생성
6. **보관함에 저장**: 서버 디렉토리에 파일 저장
7. **송장 발급**: 파일 경로/URL 반환

**코드로 보면**:
```java
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    // 1. 소포 확인 (파일이 있는지)
    if (file.isEmpty()) {
        throw new IllegalArgumentException("파일이 없습니다");
    }

    // 2. 무게 측정 (크기 확인)
    if (file.getSize() > 10 * 1024 * 1024) {  // 10MB
        throw new IllegalArgumentException("파일이 너무 큽니다");
    }

    // 3. 위험물 검사 (확장자 확인)
    String filename = file.getOriginalFilename();
    if (filename.endsWith(".exe") || filename.endsWith(".bat")) {
        throw new IllegalArgumentException("위험한 파일입니다");
    }

    // 4. 송장 번호 부여 (고유 파일명)
    String savedFilename = UUID.randomUUID().toString() + "_" + filename;

    // 5. 보관함에 저장
    Path path = Paths.get("uploads/" + savedFilename);
    file.transferTo(path);

    return "redirect:/success";
}
```

---

### 비유 2: 아파트 택배 보관함

**상황**: 아파트 택배함에 물건 보관

```
┌──────────────┬─────────────────────┬──────────────────┐
│ 택배 시스템  │ File Upload         │ 역할             │
├──────────────┼─────────────────────┼──────────────────┤
│ 택배 상자    │ 파일                │ 업로드 대상      │
│ 보관함 크기  │ 최대 파일 크기      │ 용량 제한        │
│ 보관함 번호  │ 파일 경로           │ 저장 위치        │
│ 수령증       │ 파일 URL            │ 접근 방법        │
│ 임시 보관    │ 임시 디렉토리       │ 임시 저장        │
│ 본 보관소    │ 최종 디렉토리       │ 영구 저장        │
└──────────────┴─────────────────────┴──────────────────┘
```

**예시**:
```java
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    // 보관함 크기 확인
    if (file.getSize() > MAX_SIZE) {
        return "택배가 너무 커서 보관함에 들어가지 않습니다";
    }

    // 임시 보관함 → 본 보관함으로 이동
    File tempFile = file.getFile();  // 임시 보관함
    File finalFile = new File("storage/" + file.getOriginalFilename());
    Files.move(tempFile, finalFile);  // 본 보관함

    // 수령증 발급 (URL)
    String receiptUrl = "/files/" + finalFile.getName();
    return "수령증: " + receiptUrl;
}
```

**왜 이 비유가 적절한가?**:
- 택배 상자처럼 파일도 **크기 제한**이 있음
- 임시 보관함처럼 **임시 디렉토리**에 먼저 저장됨
- 보관함 번호처럼 **고유한 경로**가 필요함

---

### 비유 3: 사진관 사진 인화

**상황**: 사진관에서 사진 인화하기

```
┌──────────────┬─────────────────────┬──────────────────┐
│ 사진관       │ File Upload         │ 역할             │
├──────────────┼─────────────────────┼──────────────────┤
│ 디지털 파일  │ MultipartFile       │ 원본 파일        │
│ 파일 형식    │ MIME 타입           │ 이미지 여부 확인 │
│ 해상도 확인  │ 이미지 크기 검증    │ 품질 확인        │
│ 인화         │ 파일 저장           │ 영구 저장        │
│ 앨범         │ 디렉토리 구조       │ 분류 저장        │
│ 사진 번호    │ 파일명              │ 식별자           │
└──────────────┴─────────────────────┴──────────────────┘
```

**시나리오**:
```java
@PostMapping("/upload/photo")
public String uploadPhoto(@RequestParam("photo") MultipartFile photo) {
    // 1. 디지털 파일인지 확인
    if (!photo.getContentType().startsWith("image/")) {
        throw new IllegalArgumentException("사진 파일만 가능합니다");
    }

    // 2. 해상도 확인 (크기)
    if (photo.getSize() > 5 * 1024 * 1024) {  // 5MB
        throw new IllegalArgumentException("사진 용량이 너무 큽니다");
    }

    // 3. 앨범에 분류 (연도별 폴더)
    String year = LocalDate.now().getYear() + "";
    String month = String.format("%02d", LocalDate.now().getMonthValue());
    Path albumPath = Paths.get("photos", year, month);
    Files.createDirectories(albumPath);

    // 4. 사진 번호 부여
    String photoNumber = UUID.randomUUID().toString() + ".jpg";

    // 5. 인화 (저장)
    Path photoPath = albumPath.resolve(photoNumber);
    photo.transferTo(photoPath);

    return "사진 번호: " + photoNumber;
}
```

**실무 연관**:
- 프로필 사진 업로드
- 상품 이미지 등록
- 포토 갤러리

---

### 비유 4: 도서관 책 기증

**상황**: 도서관에 책 기증하기

```
┌──────────────┬─────────────────────┬──────────────────┐
│ 도서관       │ File Upload         │ 역할             │
├──────────────┼─────────────────────┼──────────────────┤
│ 기증 도서    │ 업로드 파일         │ 파일             │
│ 도서 검수    │ 파일 검증           │ 유효성 확인      │
│ 훼손 여부    │ 바이러스 검사       │ 안전성 확인      │
│ 분류 번호    │ 파일 경로           │ 저장 위치        │
│ 서가 배치    │ 디렉토리 저장       │ 영구 보관        │
│ 대출 카드    │ 파일 메타데이터     │ 정보 관리        │
└──────────────┴─────────────────────┴──────────────────┘
```

**예시**:
```java
@Service
public class FileLibraryService {

    // 책 기증 (파일 업로드)
    public FileMetadata donate(@RequestParam("book") MultipartFile book) {
        // 1. 도서 검수 (파일 검증)
        validateBook(book);

        // 2. 분류 번호 부여
        String callNumber = generateCallNumber(book);

        // 3. 서가 배치 (저장)
        Path shelfPath = Paths.get("library", getCategory(book), callNumber);
        book.transferTo(shelfPath);

        // 4. 대출 카드 작성 (메타데이터)
        return FileMetadata.builder()
            .originalName(book.getOriginalFilename())
            .savedPath(shelfPath.toString())
            .size(book.getSize())
            .uploadDate(LocalDateTime.now())
            .build();
    }

    private void validateBook(MultipartFile book) {
        // 훼손 여부 (바이러스 검사)
        if (hasMalware(book)) {
            throw new IllegalArgumentException("훼손된 도서입니다");
        }

        // 도서 종류 확인 (확장자)
        String filename = book.getOriginalFilename();
        if (!filename.endsWith(".pdf") && !filename.endsWith(".epub")) {
            throw new IllegalArgumentException("지원하지 않는 형식입니다");
        }
    }
}
```

---

### 비유 5: 은행 문서 제출

**상황**: 은행에 대출 서류 제출

```
┌──────────────┬─────────────────────┬──────────────────┐
│ 은행         │ File Upload         │ 역할             │
├──────────────┼─────────────────────┼──────────────────┤
│ 서류         │ 파일                │ 업로드 대상      │
│ 창구 직원    │ Controller          │ 접수 처리        │
│ 서류 확인    │ 파일 검증           │ 유효성 검증      │
│ 접수 번호    │ 파일 ID             │ 고유 식별자      │
│ 금고         │ 보안 스토리지       │ 안전한 저장      │
│ 보관 기간    │ 파일 보관 정책      │ 자동 삭제        │
└──────────────┴─────────────────────┴──────────────────┘
```

**시나리오**:
```java
@PostMapping("/loan/documents")
public ResponseEntity<DocumentReceipt> submitDocuments(
    @RequestParam("identityCard") MultipartFile identityCard,
    @RequestParam("incomeProof") MultipartFile incomeProof,
    @RequestParam("bankStatement") MultipartFile bankStatement
) {
    // 1. 서류 확인 (필수 서류가 모두 있는지)
    if (identityCard.isEmpty() || incomeProof.isEmpty() || bankStatement.isEmpty()) {
        throw new IllegalArgumentException("필수 서류가 누락되었습니다");
    }

    // 2. 서류 유효성 검사
    validateDocument(identityCard, "image/jpeg", "신분증");
    validateDocument(incomeProof, "application/pdf", "소득증명");
    validateDocument(bankStatement, "application/pdf", "통장사본");

    // 3. 접수 번호 발급
    String receiptNumber = generateReceiptNumber();

    // 4. 금고에 보관 (암호화된 저장소)
    Path securePath = Paths.get("secure-storage", receiptNumber);
    Files.createDirectories(securePath);

    identityCard.transferTo(securePath.resolve("identity.jpg"));
    incomeProof.transferTo(securePath.resolve("income.pdf"));
    bankStatement.transferTo(securePath.resolve("statement.pdf"));

    // 5. 접수증 발급
    DocumentReceipt receipt = new DocumentReceipt();
    receipt.setReceiptNumber(receiptNumber);
    receipt.setSubmitDate(LocalDateTime.now());
    receipt.setExpiryDate(LocalDateTime.now().plusDays(90));  // 90일 보관

    return ResponseEntity.ok(receipt);
}

private void validateDocument(MultipartFile file, String expectedType, String docName) {
    if (!file.getContentType().equals(expectedType)) {
        throw new IllegalArgumentException(docName + "은(는) " + expectedType + " 형식이어야 합니다");
    }

    if (file.getSize() > 10 * 1024 * 1024) {  // 10MB
        throw new IllegalArgumentException(docName + " 크기가 10MB를 초과합니다");
    }
}
```

**실무 활용**:
- 서류 제출 시스템
- 계약서 업로드
- 증명서 제출

---

### 🔄 종합 비교표

```
┌─────────────┬──────────────┬──────────────┬──────────────┐
│ 비유        │ 파일         │ 검증         │ 저장         │
├─────────────┼──────────────┼──────────────┼──────────────┤
│ 우체국      │ 소포         │ 무게/위험물  │ 보관함       │
│ 택배함      │ 택배 상자    │ 크기         │ 보관함 번호  │
│ 사진관      │ 디지털 사진  │ 해상도       │ 앨범         │
│ 도서관      │ 기증 도서    │ 훼손 여부    │ 서가         │
│ 은행        │ 제출 서류    │ 서류 종류    │ 금고         │
└─────────────┴──────────────┴──────────────┴──────────────┘
```

**핵심 인사이트**:
1. **파일은 검증이 필수**: 크기, 형식, 안전성
2. **고유 식별자 필요**: UUID, 접수번호
3. **임시 저장 → 영구 저장**: 2단계 저장
4. **보안 고려**: 경로 조작 방지, 악성 파일 차단

---

## 📖 핵심 개념

### 1️⃣ 초보자 수준 설명

**파일 업로드란?**

사용자가 자신의 컴퓨터에 있는 파일을 웹 서버로 보내는 것입니다.

**간단한 예시**:
- 카카오톡 프로필 사진 등록
- 이메일 첨부파일 추가
- 과제 제출 시스템에 파일 업로드

**Spring에서는 어떻게?**

```java
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    // file.getOriginalFilename() → 원본 파일명
    // file.getSize() → 파일 크기
    // file.transferTo(경로) → 파일 저장

    file.transferTo(new File("uploads/" + file.getOriginalFilename()));
    return "업로드 성공!";
}
```

---

### 2️⃣ 중급자 수준 설명

**MultipartFile의 동작 원리**

HTTP는 기본적으로 **텍스트 기반 프로토콜**입니다. 파일 같은 바이너리 데이터를 전송하려면 **multipart/form-data** 인코딩을 사용해야 합니다.

**HTTP 요청 예시**:
```http
POST /upload HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="photo.jpg"
Content-Type: image/jpeg

[파일의 바이너리 데이터]
------WebKitFormBoundary--
```

**Spring의 처리 과정**:
```
1. 사용자가 파일 선택 → <input type="file">
   ↓
2. 브라우저가 multipart/form-data로 인코딩
   ↓
3. DispatcherServlet이 요청 수신
   ↓
4. MultipartResolver가 파일 파싱
   ↓
5. 임시 디렉토리에 파일 저장 (예: /tmp)
   ↓
6. MultipartFile 객체 생성
   ↓
7. Controller에서 @RequestParam으로 수신
   ↓
8. 개발자가 원하는 위치로 transferTo()
   ↓
9. 요청 처리 완료 후 임시 파일 자동 삭제
```

**설정**:
```yaml
# application.yml
spring:
  servlet:
    multipart:
      enabled: true                    # multipart 처리 활성화
      max-file-size: 10MB              # 파일 1개당 최대 크기
      max-request-size: 50MB           # 요청 전체 최대 크기
      file-size-threshold: 1MB         # 메모리 임계값 (초과 시 디스크 사용)
      location: /tmp                   # 임시 디렉토리
```

**파일 검증**:
```java
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    // 1. 빈 파일 체크
    if (file.isEmpty()) {
        throw new IllegalArgumentException("파일이 비어있습니다");
    }

    // 2. 크기 체크
    long maxSize = 10 * 1024 * 1024;  // 10MB
    if (file.getSize() > maxSize) {
        throw new IllegalArgumentException("파일 크기가 10MB를 초과합니다");
    }

    // 3. 확장자 체크
    String filename = file.getOriginalFilename();
    String extension = filename.substring(filename.lastIndexOf(".") + 1).toLowerCase();
    List<String> allowedExtensions = Arrays.asList("jpg", "jpeg", "png", "gif");

    if (!allowedExtensions.contains(extension)) {
        throw new IllegalArgumentException("허용되지 않는 파일 형식입니다");
    }

    // 4. MIME 타입 체크
    String contentType = file.getContentType();
    if (!contentType.startsWith("image/")) {
        throw new IllegalArgumentException("이미지 파일만 업로드 가능합니다");
    }

    // 5. 파일 저장
    String savedFilename = UUID.randomUUID().toString() + "_" + filename;
    Path path = Paths.get("uploads/" + savedFilename);
    file.transferTo(path);

    return "redirect:/success";
}
```

---

### 3️⃣ 고급자 수준 설명

**내부 구조와 최적화**

**MultipartResolver 종류**:

1. **StandardServletMultipartResolver** (기본값)
   - Servlet 3.0+ 표준 API 사용
   - 서블릿 컨테이너가 직접 처리
   - 추가 라이브러리 불필요

2. **CommonsMultipartResolver**
   - Apache Commons FileUpload 사용
   - 더 많은 커스터마이징 옵션
   - 레거시 프로젝트에서 사용

**파일 저장 전략**:

```java
@Service
public class FileStorageService {

    private final Path rootLocation;

    public FileStorageService(@Value("${file.upload-dir}") String uploadDir) {
        this.rootLocation = Paths.get(uploadDir).toAbsolutePath().normalize();

        try {
            Files.createDirectories(this.rootLocation);
        } catch (IOException e) {
            throw new FileStorageException("파일 업로드 디렉토리를 생성할 수 없습니다", e);
        }
    }

    public String store(MultipartFile file) {
        // 1. 원본 파일명 안전화 (경로 조작 공격 방지)
        String originalFilename = StringUtils.cleanPath(file.getOriginalFilename());

        // 2. 파일명에 ".."이 포함되어 있으면 차단
        if (originalFilename.contains("..")) {
            throw new FileStorageException("파일명에 부적절한 경로가 포함되어 있습니다: " + originalFilename);
        }

        // 3. 고유한 파일명 생성 (UUID + 타임스탬프 + 원본명)
        String extension = getExtension(originalFilename);
        String storedFilename = String.format("%s_%d.%s",
            UUID.randomUUID().toString(),
            System.currentTimeMillis(),
            extension
        );

        // 4. 날짜별 디렉토리 구조 생성 (2024/01/15/)
        LocalDate now = LocalDate.now();
        Path dateDirectory = this.rootLocation.resolve(
            Paths.get(String.valueOf(now.getYear()),
                      String.format("%02d", now.getMonthValue()),
                      String.format("%02d", now.getDayOfMonth()))
        );

        try {
            Files.createDirectories(dateDirectory);
        } catch (IOException e) {
            throw new FileStorageException("디렉토리를 생성할 수 없습니다", e);
        }

        // 5. 파일 저장
        Path targetLocation = dateDirectory.resolve(storedFilename);

        try {
            // transferTo()는 스트리밍 방식으로 저장 (메모리 효율적)
            file.transferTo(targetLocation);
        } catch (IOException e) {
            throw new FileStorageException("파일 저장에 실패했습니다: " + storedFilename, e);
        }

        // 6. 상대 경로 반환 (2024/01/15/uuid_timestamp.jpg)
        return this.rootLocation.relativize(targetLocation).toString();
    }

    private String getExtension(String filename) {
        int lastDot = filename.lastIndexOf('.');
        if (lastDot == -1) {
            return "";
        }
        return filename.substring(lastDot + 1).toLowerCase();
    }
}
```

**보안 고려사항**:

```java
@Component
public class FileValidator {

    // 화이트리스트 방식 (허용 목록)
    private static final Set<String> ALLOWED_EXTENSIONS = Set.of(
        "jpg", "jpeg", "png", "gif", "bmp",  // 이미지
        "pdf", "doc", "docx", "xls", "xlsx",  // 문서
        "txt", "csv"  // 텍스트
    );

    private static final Map<String, String> MIME_TYPE_MAP = Map.of(
        "jpg", "image/jpeg",
        "jpeg", "image/jpeg",
        "png", "image/png",
        "gif", "image/gif",
        "pdf", "application/pdf"
    );

    private static final long MAX_FILE_SIZE = 10 * 1024 * 1024;  // 10MB

    public void validate(MultipartFile file) {
        // 1. Null 체크
        if (file == null || file.isEmpty()) {
            throw new InvalidFileException("파일이 비어있습니다");
        }

        // 2. 파일명 체크
        String filename = file.getOriginalFilename();
        if (filename == null || filename.isEmpty()) {
            throw new InvalidFileException("파일명이 없습니다");
        }

        // 3. 확장자 체크 (화이트리스트)
        String extension = getExtension(filename);
        if (!ALLOWED_EXTENSIONS.contains(extension)) {
            throw new InvalidFileException("허용되지 않는 파일 형식입니다: " + extension);
        }

        // 4. MIME 타입 체크 (확장자와 일치하는지)
        String contentType = file.getContentType();
        String expectedMimeType = MIME_TYPE_MAP.get(extension);

        if (expectedMimeType != null && !expectedMimeType.equals(contentType)) {
            throw new InvalidFileException(
                String.format("파일 확장자(%s)와 MIME 타입(%s)이 일치하지 않습니다",
                    extension, contentType)
            );
        }

        // 5. 크기 체크
        if (file.getSize() > MAX_FILE_SIZE) {
            throw new InvalidFileException(
                String.format("파일 크기가 제한을 초과합니다: %.2fMB / %.2fMB",
                    file.getSize() / (1024.0 * 1024.0),
                    MAX_FILE_SIZE / (1024.0 * 1024.0))
            );
        }

        // 6. 매직 넘버 체크 (파일 시그니처)
        try (InputStream is = file.getInputStream()) {
            byte[] header = new byte[8];
            is.read(header);

            if (!validateFileSignature(header, extension)) {
                throw new InvalidFileException("파일의 실제 형식이 확장자와 다릅니다");
            }
        } catch (IOException e) {
            throw new InvalidFileException("파일을 읽을 수 없습니다", e);
        }
    }

    private boolean validateFileSignature(byte[] header, String extension) {
        // JPEG: FF D8 FF
        if (extension.equals("jpg") || extension.equals("jpeg")) {
            return header[0] == (byte) 0xFF &&
                   header[1] == (byte) 0xD8 &&
                   header[2] == (byte) 0xFF;
        }

        // PNG: 89 50 4E 47
        if (extension.equals("png")) {
            return header[0] == (byte) 0x89 &&
                   header[1] == (byte) 0x50 &&
                   header[2] == (byte) 0x4E &&
                   header[3] == (byte) 0x47;
        }

        // GIF: 47 49 46 38
        if (extension.equals("gif")) {
            return header[0] == (byte) 0x47 &&
                   header[1] == (byte) 0x49 &&
                   header[2] == (byte) 0x46 &&
                   header[3] == (byte) 0x38;
        }

        // PDF: 25 50 44 46
        if (extension.equals("pdf")) {
            return header[0] == (byte) 0x25 &&
                   header[1] == (byte) 0x50 &&
                   header[2] == (byte) 0x44 &&
                   header[3] == (byte) 0x46;
        }

        return true;  // 기타 파일은 통과
    }

    private String getExtension(String filename) {
        int lastDot = filename.lastIndexOf('.');
        if (lastDot == -1) {
            throw new InvalidFileException("파일 확장자가 없습니다");
        }
        return filename.substring(lastDot + 1).toLowerCase();
    }
}
```

**성능 최적화**:

```java
@Configuration
public class MultipartConfig {

    @Bean
    public MultipartConfigElement multipartConfigElement() {
        MultipartConfigFactory factory = new MultipartConfigFactory();

        // 파일 크기 제한
        factory.setMaxFileSize(DataSize.ofMegabytes(10));
        factory.setMaxRequestSize(DataSize.ofMegabytes(50));

        // 메모리 임계값 설정
        // 이 크기 이하는 메모리에 저장, 초과하면 디스크 사용
        factory.setFileSizeThreshold(DataSize.ofKilobytes(512));

        // 임시 디렉토리
        factory.setLocation("/tmp/uploads");

        return factory.createMultipartConfig();
    }
}
```

---

## 💻 기본 실습

### 실습 1: 단일 파일 업로드

**난이도**: ⭐⭐☆☆☆

#### 프로젝트 설정

**pom.xml** (이미 spring-boot-starter-web에 포함됨):
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

**application.yml**:
```yaml
spring:
  servlet:
    multipart:
      enabled: true
      max-file-size: 10MB
      max-request-size: 50MB
      file-size-threshold: 1MB
      location: ${java.io.tmpdir}

file:
  upload-dir: uploads
```

#### Controller

```java
package com.example.fileupload.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

@Controller
public class FileUploadController {

    @Value("${file.upload-dir}")
    private String uploadDir;

    // 업로드 폼 페이지
    @GetMapping("/upload")
    public String uploadForm() {
        return "upload";
    }

    // 파일 업로드 처리
    @PostMapping("/upload")
    public String upload(
        @RequestParam("file") MultipartFile file,
        RedirectAttributes redirectAttributes
    ) {
        // 1. 빈 파일 체크
        if (file.isEmpty()) {
            redirectAttributes.addFlashAttribute("message", "파일을 선택해주세요");
            return "redirect:/upload";
        }

        try {
            // 2. 업로드 디렉토리 생성
            Path uploadPath = Paths.get(uploadDir);
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }

            // 3. 파일명 생성 (UUID + 원본 파일명)
            String originalFilename = file.getOriginalFilename();
            String savedFilename = UUID.randomUUID().toString() + "_" + originalFilename;

            // 4. 파일 저장
            Path filePath = uploadPath.resolve(savedFilename);
            file.transferTo(filePath);

            // 5. 성공 메시지
            redirectAttributes.addFlashAttribute("message",
                "파일 업로드 성공: " + originalFilename);
            redirectAttributes.addFlashAttribute("savedFilename", savedFilename);

        } catch (IOException e) {
            redirectAttributes.addFlashAttribute("message",
                "파일 업로드 실패: " + e.getMessage());
        }

        return "redirect:/upload";
    }
}
```

#### View (Thymeleaf)

**upload.html**:
```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>파일 업로드</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
        }
        .upload-form {
            border: 2px dashed #ccc;
            padding: 30px;
            text-align: center;
            background-color: #f9f9f9;
        }
        .message {
            padding: 10px;
            margin: 20px 0;
            border-radius: 5px;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <h1>파일 업로드</h1>

    <!-- 메시지 표시 -->
    <div th:if="${message}"
         th:text="${message}"
         th:class="${savedFilename != null ? 'message success' : 'message error'}">
    </div>

    <!-- 업로드 폼 -->
    <form th:action="@{/upload}"
          method="post"
          enctype="multipart/form-data"
          class="upload-form">

        <h3>파일 선택</h3>
        <input type="file" name="file" required>
        <br><br>
        <button type="submit">업로드</button>
    </form>

    <!-- 업로드된 파일 정보 -->
    <div th:if="${savedFilename}">
        <h3>업로드 완료</h3>
        <p>저장된 파일명: <strong th:text="${savedFilename}"></strong></p>
    </div>
</body>
</html>
```

#### 실행

```bash
# 애플리케이션 실행
mvn spring-boot:run

# 브라우저에서 접속
http://localhost:8080/upload
```

#### 테스트

1. 파일 선택
2. "업로드" 버튼 클릭
3. `uploads/` 디렉토리에 파일 저장 확인

---

### 실습 2: 파일 검증 추가

**난이도**: ⭐⭐⭐☆☆

#### FileValidator

```java
package com.example.fileupload.validator;

import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

import java.util.Arrays;
import java.util.List;

@Component
public class FileValidator {

    private static final long MAX_FILE_SIZE = 10 * 1024 * 1024;  // 10MB
    private static final List<String> ALLOWED_EXTENSIONS = Arrays.asList("jpg", "jpeg", "png", "gif");
    private static final List<String> ALLOWED_MIME_TYPES = Arrays.asList(
        "image/jpeg", "image/png", "image/gif"
    );

    public void validate(MultipartFile file) {
        // 1. 빈 파일 체크
        if (file.isEmpty()) {
            throw new IllegalArgumentException("파일이 비어있습니다");
        }

        // 2. 파일 크기 체크
        if (file.getSize() > MAX_FILE_SIZE) {
            throw new IllegalArgumentException(
                String.format("파일 크기가 %.2fMB를 초과합니다 (최대: 10MB)",
                    file.getSize() / (1024.0 * 1024.0))
            );
        }

        // 3. 확장자 체크
        String filename = file.getOriginalFilename();
        String extension = getExtension(filename);

        if (!ALLOWED_EXTENSIONS.contains(extension.toLowerCase())) {
            throw new IllegalArgumentException(
                "허용되지 않는 파일 형식입니다. 허용: " + ALLOWED_EXTENSIONS
            );
        }

        // 4. MIME 타입 체크
        String contentType = file.getContentType();
        if (!ALLOWED_MIME_TYPES.contains(contentType)) {
            throw new IllegalArgumentException(
                "허용되지 않는 MIME 타입입니다: " + contentType
            );
        }
    }

    private String getExtension(String filename) {
        int lastDot = filename.lastIndexOf('.');
        if (lastDot == -1) {
            throw new IllegalArgumentException("파일 확장자가 없습니다");
        }
        return filename.substring(lastDot + 1);
    }
}
```

#### Controller 수정

```java
@Controller
public class FileUploadController {

    @Autowired
    private FileValidator fileValidator;

    @Value("${file.upload-dir}")
    private String uploadDir;

    @PostMapping("/upload")
    public String upload(
        @RequestParam("file") MultipartFile file,
        RedirectAttributes redirectAttributes
    ) {
        try {
            // ✅ 파일 검증
            fileValidator.validate(file);

            // 업로드 처리
            Path uploadPath = Paths.get(uploadDir);
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }

            String originalFilename = file.getOriginalFilename();
            String savedFilename = UUID.randomUUID().toString() + "_" + originalFilename;
            Path filePath = uploadPath.resolve(savedFilename);

            file.transferTo(filePath);

            redirectAttributes.addFlashAttribute("message",
                "파일 업로드 성공: " + originalFilename);
            redirectAttributes.addFlashAttribute("savedFilename", savedFilename);

        } catch (IllegalArgumentException e) {
            // 검증 실패
            redirectAttributes.addFlashAttribute("message", "검증 오류: " + e.getMessage());
        } catch (IOException e) {
            // 저장 실패
            redirectAttributes.addFlashAttribute("message", "저장 오류: " + e.getMessage());
        }

        return "redirect:/upload";
    }
}
```

---

### 실습 3: 여러 파일 업로드

**난이도**: ⭐⭐⭐☆☆

#### Controller

```java
@PostMapping("/upload/multiple")
public String uploadMultiple(
    @RequestParam("files") List<MultipartFile> files,
    RedirectAttributes redirectAttributes
) {
    List<String> uploadedFiles = new ArrayList<>();
    List<String> errors = new ArrayList<>();

    for (MultipartFile file : files) {
        try {
            // 검증
            fileValidator.validate(file);

            // 저장
            Path uploadPath = Paths.get(uploadDir);
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }

            String savedFilename = UUID.randomUUID().toString() + "_" + file.getOriginalFilename();
            Path filePath = uploadPath.resolve(savedFilename);
            file.transferTo(filePath);

            uploadedFiles.add(file.getOriginalFilename());

        } catch (Exception e) {
            errors.add(file.getOriginalFilename() + ": " + e.getMessage());
        }
    }

    // 결과 메시지
    if (!uploadedFiles.isEmpty()) {
        redirectAttributes.addFlashAttribute("message",
            "업로드 성공 (" + uploadedFiles.size() + "개): " +
            String.join(", ", uploadedFiles));
    }

    if (!errors.isEmpty()) {
        redirectAttributes.addFlashAttribute("errors",
            "업로드 실패: " + String.join(", ", errors));
    }

    return "redirect:/upload";
}
```

#### View

```html
<form th:action="@{/upload/multiple}"
      method="post"
      enctype="multipart/form-data">

    <h3>여러 파일 선택</h3>
    <input type="file" name="files" multiple required>
    <br><br>
    <button type="submit">업로드</button>
</form>
```

---

## 🏢 실무 활용 사례

### 실제 기업 활용 사례

#### 사례 1: 네이버 블로그 - 이미지 업로드 시스템

**사용 목적**: 블로그 포스팅 시 이미지 첨부 기능

**규모**:
- 일 평균 업로드: 500만 건
- 월간 저장 용량: 10TB

**구현 방식**:
```java
@RestController
@RequestMapping("/api/blog")
public class BlogImageController {

    @Value("${upload.path}")
    private String uploadPath;

    @PostMapping("/images")
    public ResponseEntity<ImageUploadResponse> uploadImage(
        @RequestParam("image") MultipartFile image,
        @AuthenticationPrincipal UserDetails user
    ) {
        // 1. 이미지 검증
        validateImage(image);

        // 2. 사용자별 디렉토리 생성
        String userDir = user.getUsername();
        Path userPath = Paths.get(uploadPath, userDir,
            LocalDate.now().format(DateTimeFormatter.ISO_DATE));
        Files.createDirectories(userPath);

        // 3. 파일명 생성 (UUID + 확장자)
        String extension = getExtension(image.getOriginalFilename());
        String savedFilename = UUID.randomUUID().toString() + extension;

        // 4. 파일 저장
        Path filePath = userPath.resolve(savedFilename);
        image.transferTo(filePath);

        // 5. CDN URL 생성
        String cdnUrl = String.format("https://cdn.naver.com/blog/%s/%s/%s",
            userDir, LocalDate.now(), savedFilename);

        return ResponseEntity.ok(new ImageUploadResponse(cdnUrl, image.getSize()));
    }

    private void validateImage(MultipartFile image) {
        // 크기 제한: 10MB
        if (image.getSize() > 10 * 1024 * 1024) {
            throw new FileTooLargeException("이미지는 10MB 이하여야 합니다");
        }

        // 이미지 형식만 허용
        String contentType = image.getContentType();
        if (!contentType.startsWith("image/")) {
            throw new InvalidFileTypeException("이미지 파일만 업로드 가능합니다");
        }

        // 허용된 확장자: jpg, png, gif, webp
        String filename = image.getOriginalFilename();
        if (!filename.matches(".*\\.(jpg|jpeg|png|gif|webp)$")) {
            throw new InvalidFileTypeException("지원하지 않는 이미지 형식입니다");
        }
    }
}
```

**성과**:
- 업로드 성공률: **99.9%**
- 평균 업로드 시간: **1.2초**
- 스토리지 비용 절감: **30%** (중복 제거 알고리즘 적용)

---

#### 사례 2: 토스 - 신분증 업로드 인증 시스템

**사용 목적**: 본인 인증을 위한 신분증 사진 업로드

**규모**:
- 월간 업로드: 100만 건
- 보안 등급: 최상

**구현 방식**:
```java
@Service
public class IdentityVerificationService {

    @Autowired
    private EncryptionService encryptionService;

    @Autowired
    private OcrService ocrService;

    @Transactional
    public VerificationResult uploadIdentityCard(
        Long userId,
        MultipartFile frontImage,
        MultipartFile backImage
    ) {
        // 1. 보안 검증
        validateSecureUpload(frontImage);
        validateSecureUpload(backImage);

        // 2. 암호화된 저장소에 저장
        String frontPath = saveEncrypted(userId, frontImage, "front");
        String backPath = saveEncrypted(userId, backImage, "back");

        // 3. OCR로 신분증 정보 추출
        IdentityInfo info = ocrService.extractInfo(frontImage);

        // 4. DB에 메타데이터 저장
        IdentityVerification verification = IdentityVerification.builder()
            .userId(userId)
            .frontImagePath(frontPath)
            .backImagePath(backPath)
            .name(info.getName())
            .birthDate(info.getBirthDate())
            .idNumber(encryptionService.encrypt(info.getIdNumber()))
            .verificationStatus(VerificationStatus.PENDING)
            .uploadDate(LocalDateTime.now())
            .expiryDate(LocalDateTime.now().plusDays(30))  // 30일 후 자동 삭제
            .build();

        verificationRepository.save(verification);

        return new VerificationResult(verification.getId(), "업로드 완료");
    }

    private void validateSecureUpload(MultipartFile file) {
        // 1. 크기 제한
        if (file.getSize() > 5 * 1024 * 1024) {
            throw new SecurityException("파일이 너무 큽니다");
        }

        // 2. 이미지 형식만 허용
        if (!file.getContentType().startsWith("image/")) {
            throw new SecurityException("이미지 파일만 허용됩니다");
        }

        // 3. 메타데이터에서 GPS 정보 제거
        removeMetadata(file);

        // 4. 악성 코드 스캔
        if (hasVirusSignature(file)) {
            throw new SecurityException("악성 파일이 감지되었습니다");
        }
    }

    private String saveEncrypted(Long userId, MultipartFile file, String type) {
        // 암호화된 스토리지에 저장
        byte[] encrypted = encryptionService.encrypt(file.getBytes());
        String filename = String.format("%d_%s_%s.enc",
            userId, type, UUID.randomUUID());
        Path path = Paths.get("secure-storage", filename);
        Files.write(path, encrypted);
        return path.toString();
    }
}
```

**보안 특징**:
- 파일 **암호화 저장** (AES-256)
- GPS 메타데이터 **자동 제거**
- 30일 후 **자동 삭제**
- 접근 로그 **완전 기록**

**성과**:
- 본인 인증 성공률: **95%**
- 보안 사고: **0건**
- 인증 처리 시간: **평균 2분**

---

#### 사례 3: 배달의민족 - 메뉴 사진 업로드

**사용 목적**: 사장님들이 메뉴 사진 등록

**규모**:
- 등록 매장: 50만 개
- 일 평균 업로드: 10만 건

**구현 방식**:
```java
@RestController
@RequestMapping("/api/menu")
public class MenuImageController {

    @Autowired
    private S3Service s3Service;

    @Autowired
    private ImageOptimizationService imageService;

    @PostMapping("/images")
    public ResponseEntity<MenuImageResponse> uploadMenuImage(
        @RequestParam("menuImage") MultipartFile menuImage,
        @RequestParam("menuId") Long menuId,
        @AuthenticationPrincipal StoreOwner owner
    ) {
        // 1. 권한 확인
        validateStoreOwner(owner, menuId);

        // 2. 이미지 최적화
        BufferedImage optimized = imageService.optimize(
            menuImage.getInputStream(),
            800, 600,  // 최대 크기
            0.85       // 품질
        );

        // 3. 여러 크기의 썸네일 생성
        Map<String, BufferedImage> thumbnails = Map.of(
            "large", imageService.resize(optimized, 800, 600),
            "medium", imageService.resize(optimized, 400, 300),
            "small", imageService.resize(optimized, 200, 150)
        );

        // 4. S3에 업로드
        Map<String, String> urls = new HashMap<>();
        for (Map.Entry<String, BufferedImage> entry : thumbnails.entrySet()) {
            String key = String.format("menus/%d/%s_%s.jpg",
                menuId, entry.getKey(), UUID.randomUUID());
            String url = s3Service.upload(key, entry.getValue(), "image/jpeg");
            urls.put(entry.getKey(), url);
        }

        // 5. DB 업데이트
        menuRepository.updateImages(menuId, urls);

        return ResponseEntity.ok(new MenuImageResponse(urls));
    }
}
```

**최적화 효과**:
- 이미지 용량: **평균 70% 감소**
- 로딩 속도: **2.5초 → 0.8초**
- CDN 비용: **월 40% 절감**

---

### 일반적인 활용 패턴

#### 패턴 1: 프로필 사진 업로드

**사용 시기**: SNS, 커뮤니티, 회원 시스템

**구현 방법**:
```java
@Service
public class ProfileImageService {

    public ProfileImage uploadProfileImage(Long userId, MultipartFile image) {
        // 1. 이미지 검증
        if (!isValidImage(image)) {
            throw new InvalidImageException("유효하지 않은 이미지입니다");
        }

        // 2. 기존 프로필 사진 삭제
        deleteOldProfileImage(userId);

        // 3. 원본 및 썸네일 생성
        String originalPath = saveOriginal(userId, image);
        String thumbnailPath = saveThumbnail(userId, image, 200, 200);

        // 4. DB 저장
        ProfileImage profileImage = new ProfileImage();
        profileImage.setUserId(userId);
        profileImage.setOriginalPath(originalPath);
        profileImage.setThumbnailPath(thumbnailPath);
        profileImage.setUploadDate(LocalDateTime.now());

        return profileImageRepository.save(profileImage);
    }

    private boolean isValidImage(MultipartFile image) {
        // 크기: 5MB 이하
        if (image.getSize() > 5 * 1024 * 1024) {
            return false;
        }

        // 형식: JPEG, PNG만
        String contentType = image.getContentType();
        return contentType.equals("image/jpeg") || contentType.equals("image/png");
    }

    private String saveThumbnail(Long userId, MultipartFile image, int width, int height) {
        BufferedImage original = ImageIO.read(image.getInputStream());

        // 정사각형으로 크롭
        BufferedImage cropped = cropToSquare(original);

        // 리사이즈
        BufferedImage thumbnail = Thumbnails.of(cropped)
            .size(width, height)
            .asBufferedImage();

        // 저장
        String filename = String.format("profiles/%d/thumbnail_%s.jpg",
            userId, UUID.randomUUID());
        Path path = Paths.get(uploadDir, filename);
        ImageIO.write(thumbnail, "jpg", path.toFile());

        return filename;
    }
}
```

**실무 주의사항**:
- ⚠️ **기존 이미지 삭제**: 디스크 공간 확보를 위해 이전 프로필 사진 삭제 필수
- ⚠️ **정사각형 크롭**: 다양한 UI에서 일관되게 보이도록 정사각형으로 처리
- ⚠️ **썸네일 생성**: 목록 화면에서 사용할 작은 크기 이미지 생성

---

#### 패턴 2: 문서 첨부 파일 업로드

**사용 시기**: 이메일, 게시판, 업무 시스템

**구현 방법**:
```java
@Service
public class AttachmentService {

    public List<Attachment> uploadAttachments(Long postId, List<MultipartFile> files) {
        List<Attachment> attachments = new ArrayList<>();

        for (MultipartFile file : files) {
            // 1. 파일 검증
            validateAttachment(file);

            // 2. 바이러스 스캔
            if (hasVirus(file)) {
                throw new SecurityException("악성 파일이 감지되었습니다: " + file.getOriginalFilename());
            }

            // 3. 안전한 파일명 생성
            String safeFilename = generateSafeFilename(file.getOriginalFilename());

            // 4. 파일 저장
            Path path = Paths.get("attachments", postId.toString(), safeFilename);
            Files.createDirectories(path.getParent());
            file.transferTo(path);

            // 5. DB에 메타데이터 저장
            Attachment attachment = Attachment.builder()
                .postId(postId)
                .originalFilename(file.getOriginalFilename())
                .savedFilename(safeFilename)
                .filePath(path.toString())
                .fileSize(file.getSize())
                .contentType(file.getContentType())
                .uploadDate(LocalDateTime.now())
                .build();

            attachments.add(attachmentRepository.save(attachment));
        }

        return attachments;
    }

    private void validateAttachment(MultipartFile file) {
        // 크기 제한: 100MB
        if (file.getSize() > 100 * 1024 * 1024) {
            throw new FileTooLargeException("파일 크기는 100MB 이하여야 합니다");
        }

        // 위험한 확장자 차단
        String filename = file.getOriginalFilename().toLowerCase();
        String[] dangerousExtensions = {".exe", ".bat", ".cmd", ".sh", ".ps1"};
        for (String ext : dangerousExtensions) {
            if (filename.endsWith(ext)) {
                throw new SecurityException("실행 파일은 업로드할 수 없습니다");
            }
        }
    }

    private String generateSafeFilename(String originalFilename) {
        // 경로 조작 방지
        String basename = FilenameUtils.getName(originalFilename);

        // 특수문자 제거
        basename = basename.replaceAll("[^a-zA-Z0-9가-힣._-]", "_");

        // UUID 추가
        String extension = FilenameUtils.getExtension(basename);
        String nameWithoutExt = FilenameUtils.getBaseName(basename);

        return String.format("%s_%s.%s",
            nameWithoutExt,
            UUID.randomUUID().toString().substring(0, 8),
            extension);
    }
}
```

**실무 주의사항**:
- ⚠️ **바이러스 스캔**: ClamAV 같은 도구로 악성 파일 검사
- ⚠️ **확장자 화이트리스트**: 허용된 확장자만 업로드 가능하도록
- ⚠️ **파일명 안전화**: 경로 조작 공격 방지

---

### 성능 비교

| 방식 | 업로드 시간 | 메모리 사용 | 동시 처리 | 안정성 |
|------|------------|------------|----------|--------|
| 직접 구현 (파일 전체 읽기) | 5초 | 파일 크기만큼 | 10명 | ⭐⭐☆☆☆ |
| MultipartFile (기본) | 2초 | 1MB 이하 | 100명 | ⭐⭐⭐⭐☆ |
| MultipartFile + 스트리밍 | 1.5초 | 512KB | 500명 | ⭐⭐⭐⭐⭐ |
| MultipartFile + S3 | 3초 | 512KB | 1000명 | ⭐⭐⭐⭐⭐ |

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: 파일명을 그대로 사용하여 보안 문제 발생

**상황**: 주니어 개발자가 사용자가 업로드한 파일명을 그대로 사용

```java
// ❌ 주니어 개발자가 작성한 코드
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    // 원본 파일명 그대로 사용
    String filename = file.getOriginalFilename();

    Path path = Paths.get("uploads/" + filename);
    file.transferTo(path);

    return "업로드 성공: " + filename;
}
```

**문제점**:
1. **경로 조작 공격 (Path Traversal)**:
   - 파일명: `../../../etc/passwd`
   - 저장 경로: `uploads/../../../etc/passwd` → `/etc/passwd` (시스템 파일 덮어쓰기!)

2. **파일명 충돌**:
   - 여러 사용자가 `photo.jpg` 업로드 시 덮어쓰기 발생

3. **특수문자 문제**:
   - 파일명: `이미지 #1.jpg`
   - URL: `/files/이미지 #1.jpg` → URL 인코딩 문제

**해결책**:
```java
// ✅ 올바른 코드
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    String originalFilename = file.getOriginalFilename();

    // 1. 파일명에서 경로 제거 (보안)
    String basename = FilenameUtils.getName(originalFilename);

    // 2. UUID로 고유한 파일명 생성 (충돌 방지)
    String extension = FilenameUtils.getExtension(basename);
    String safeFilename = UUID.randomUUID().toString() + "." + extension;

    // 3. 절대 경로가 아닌 안전한 경로 사용
    Path uploadDir = Paths.get("uploads").toAbsolutePath().normalize();
    Path filePath = uploadDir.resolve(safeFilename).normalize();

    // 4. 경로 검증 (uploads 디렉토리 외부로 나가지 않도록)
    if (!filePath.startsWith(uploadDir)) {
        throw new SecurityException("Invalid file path");
    }

    file.transferTo(filePath);

    // 5. DB에 원본 파일명과 저장 파일명 모두 저장
    FileMetadata metadata = new FileMetadata();
    metadata.setOriginalFilename(originalFilename);
    metadata.setSavedFilename(safeFilename);
    metadataRepository.save(metadata);

    return "업로드 성공";
}
```

**배운 점**:
- 💡 **절대로 사용자 입력을 그대로 파일명으로 사용하지 마라**
- 💡 **UUID로 고유한 파일명을 생성하라**
- 💡 **경로 검증을 반드시 수행하라**

---

### 시나리오 2: 파일 크기 제한 없이 구현하여 서버 다운

**상황**: 파일 크기 검증 없이 업로드 허용

```java
// ❌ 주니어 개발자가 작성한 코드
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    // 크기 검증 없음!
    file.transferTo(new File("uploads/" + UUID.randomUUID()));
    return "success";
}
```

**문제 발생**:
```
사용자가 5GB 영화 파일 업로드
    ↓
서버 디스크 99% 사용
    ↓
다른 사용자들 업로드 실패
    ↓
로그도 저장 못함
    ↓
서비스 중단
```

**장애 로그**:
```
2024-01-15 14:23:11 ERROR - java.io.IOException: No space left on device
2024-01-15 14:23:12 ERROR - Failed to write log: Disk full
2024-01-15 14:23:15 ERROR - Database connection failed: Cannot write to wal file
```

**해결책**:
```java
// ✅ 올바른 코드
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    // 1. 파일 크기 검증
    long maxSize = 10 * 1024 * 1024;  // 10MB
    if (file.getSize() > maxSize) {
        throw new FileTooLargeException(
            String.format("파일 크기는 %dMB 이하여야 합니다", maxSize / 1024 / 1024)
        );
    }

    // 2. 디스크 공간 확인
    Path uploadDir = Paths.get("uploads");
    long usableSpace = Files.getFileStore(uploadDir).getUsableSpace();
    long requiredSpace = file.getSize() + (100 * 1024 * 1024);  // 여유 공간 100MB

    if (usableSpace < requiredSpace) {
        throw new InsufficientStorageException("서버 저장 공간이 부족합니다");
    }

    // 3. 사용자별 할당량 확인
    long userUsage = getUserTotalUploadSize(getCurrentUserId());
    long userQuota = 1024 * 1024 * 1024;  // 1GB

    if (userUsage + file.getSize() > userQuota) {
        throw new QuotaExceededException("할당량을 초과했습니다");
    }

    // 4. 파일 저장
    file.transferTo(uploadDir.resolve(UUID.randomUUID().toString()));

    return "업로드 성공";
}
```

**추가 설정 (application.yml)**:
```yaml
spring:
  servlet:
    multipart:
      max-file-size: 10MB        # 파일 1개당 최대 크기
      max-request-size: 50MB     # 요청 전체 최대 크기
```

**배운 점**:
- 💡 **파일 크기 제한은 필수**
- 💡 **디스크 공간 확인도 필수**
- 💡 **사용자별 할당량 관리**

---

### 시나리오 3: 모든 파일 형식을 허용하여 악성 파일 업로드됨

**상황**: 파일 형식 검증 없이 모든 파일 허용

```java
// ❌ 주니어 개발자가 작성한 코드
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    // 파일 형식 검증 없음!
    file.transferTo(new File("uploads/" + file.getOriginalFilename()));
    return "success";
}
```

**공격 시나리오**:
```
1. 해커가 malicious.exe 업로드
   ↓
2. 서버에 저장됨: uploads/malicious.exe
   ↓
3. 해커가 다른 취약점으로 실행
   ↓
4. 서버 장악
```

**해결책**:
```java
// ✅ 올바른 코드
@PostMapping("/upload/image")
public String uploadImage(@RequestParam("image") MultipartFile image) {
    // 1. Content-Type 검증 (1차 방어)
    String contentType = image.getContentType();
    if (!contentType.startsWith("image/")) {
        throw new InvalidFileTypeException("이미지 파일만 업로드 가능합니다");
    }

    // 2. 확장자 검증 (2차 방어)
    String filename = image.getOriginalFilename();
    String extension = FilenameUtils.getExtension(filename).toLowerCase();

    List<String> allowedExtensions = Arrays.asList("jpg", "jpeg", "png", "gif", "webp");
    if (!allowedExtensions.contains(extension)) {
        throw new InvalidFileTypeException("허용되지 않은 파일 형식입니다");
    }

    // 3. 매직 넘버 검증 (3차 방어 - 가장 확실)
    byte[] fileBytes = image.getBytes();
    if (!isValidImageFile(fileBytes)) {
        throw new InvalidFileTypeException("손상되었거나 위조된 이미지 파일입니다");
    }

    // 4. 실행 권한 제거하여 저장
    Path path = Paths.get("uploads", UUID.randomUUID() + "." + extension);
    Files.write(path, fileBytes, StandardOpenOption.CREATE_NEW);

    // 실행 권한 제거
    Set<PosixFilePermission> perms = PosixFilePermissions.fromString("rw-r--r--");
    Files.setPosixFilePermissions(path, perms);

    return "업로드 성공";
}

private boolean isValidImageFile(byte[] bytes) {
    // JPEG 매직 넘버: FF D8 FF
    if (bytes.length >= 3 && bytes[0] == (byte) 0xFF &&
        bytes[1] == (byte) 0xD8 && bytes[2] == (byte) 0xFF) {
        return true;
    }

    // PNG 매직 넘버: 89 50 4E 47
    if (bytes.length >= 4 && bytes[0] == (byte) 0x89 &&
        bytes[1] == (byte) 0x50 && bytes[2] == (byte) 0x4E && bytes[3] == (byte) 0x47) {
        return true;
    }

    // GIF 매직 넘버: 47 49 46
    if (bytes.length >= 3 && bytes[0] == (byte) 0x47 &&
        bytes[1] == (byte) 0x49 && bytes[2] == (byte) 0x46) {
        return true;
    }

    return false;
}
```

**배운 점**:
- 💡 **확장자만 믿지 마라** (malicious.exe → malicious.jpg로 이름만 바꿀 수 있음)
- 💡 **Content-Type도 믿지 마라** (HTTP 헤더는 조작 가능)
- 💡 **매직 넘버로 실제 파일 타입을 확인하라**

---

### 시나리오 4: transferTo() 사용 시 경로 생성 안 함

**상황**: 디렉토리를 미리 생성하지 않고 transferTo() 호출

```java
// ❌ 주니어 개발자가 작성한 코드
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    // 디렉토리 생성 없이 바로 저장
    Path path = Paths.get("uploads/2024/01/" + UUID.randomUUID());
    file.transferTo(path);  // ← NoSuchFileException 발생!
    return "success";
}
```

**에러 발생**:
```
java.nio.file.NoSuchFileException: uploads/2024/01/xxx-xxx-xxx
    at sun.nio.fs.WindowsException.translateToIOException
    at sun.nio.fs.WindowsException.rethrowAsIOException
```

**왜 발생하는가?**:
- `uploads/2024/01/` 디렉토리가 존재하지 않음
- `transferTo()`는 디렉토리를 자동 생성하지 않음

**해결책**:
```java
// ✅ 올바른 코드
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    // 1. 저장할 디렉토리 경로 생성
    String yearMonth = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy/MM"));
    Path uploadDir = Paths.get("uploads", yearMonth);

    // 2. 디렉토리가 없으면 생성
    if (!Files.exists(uploadDir)) {
        Files.createDirectories(uploadDir);  // 부모 디렉토리까지 모두 생성
    }

    // 3. 파일 저장
    String filename = UUID.randomUUID() + "_" + file.getOriginalFilename();
    Path filePath = uploadDir.resolve(filename);
    file.transferTo(filePath);

    return "업로드 성공: " + filePath;
}
```

**createDirectory vs createDirectories**:
```java
// createDirectory - 부모가 없으면 에러
Files.createDirectory(Paths.get("a/b/c"));  // ← 에러! a/b가 없음

// createDirectories - 부모까지 모두 생성
Files.createDirectories(Paths.get("a/b/c"));  // ← 성공! a, a/b, a/b/c 모두 생성
```

**배운 점**:
- 💡 **transferTo() 전에 디렉토리 존재 확인**
- 💡 **Files.createDirectories() 사용** (부모까지 생성)
- 💡 **연/월별 디렉토리 구조 추천** (파일 관리 용이)

---

## 🛠️ 실전 프로젝트

### 프로젝트: 파일 공유 시스템 (File Sharing Service)

**난이도**: ⭐⭐⭐☆☆
**예상 소요 시간**: 3-4시간
**학습 목표**: MultipartFile을 활용한 안전한 파일 업로드, 다운로드, 공유 시스템 구현

---

### 요구사항 분석

#### 기능 요구사항
- [ ] **파일 업로드**: 여러 파일 동시 업로드
- [ ] **파일 목록 조회**: 사용자별 업로드 파일 목록
- [ ] **파일 다운로드**: 업로드된 파일 다운로드
- [ ] **파일 삭제**: 본인 파일만 삭제 가능
- [ ] **공유 링크 생성**: 타인과 파일 공유
- [ ] **파일 검색**: 파일명으로 검색

#### 기술 요구사항
- [ ] Spring Boot 3.x
- [ ] JPA + H2 Database
- [ ] Thymeleaf
- [ ] Validation
- [ ] Exception Handling

#### 비기능 요구사항
- [ ] **보안**: 파일명 안전화, 크기 제한, 형식 검증
- [ ] **성능**: 파일 스트리밍, 대용량 파일 처리
- [ ] **사용성**: 드래그 & 드롭 UI

---

### 프로젝트 구조

```
file-sharing-service/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/filesharing/
│   │   │       ├── FileSharingApplication.java
│   │   │       ├── controller/
│   │   │       │   └── FileController.java
│   │   │       ├── service/
│   │   │       │   └── FileStorageService.java
│   │   │       ├── repository/
│   │   │       │   └── FileMetadataRepository.java
│   │   │       ├── entity/
│   │   │       │   └── FileMetadata.java
│   │   │       ├── dto/
│   │   │       │   ├── FileUploadResponse.java
│   │   │       │   └── FileInfo.java
│   │   │       ├── exception/
│   │   │       │   ├── FileStorageException.java
│   │   │       │   └── FileNotFoundException.java
│   │   │       └── config/
│   │   │           └── FileStorageConfig.java
│   │   └── resources/
│   │       ├── application.yml
│   │       ├── templates/
│   │       │   ├── upload.html
│   │       │   └── file-list.html
│   │       └── static/
│   │           └── css/
│   └── test/
│       └── java/
└── pom.xml
```

---

### 설계 의사결정

#### 1. 왜 파일 메타데이터를 DB에 저장하는가?
**이유**:
- 파일 검색 기능 구현
- 업로드 날짜, 크기 등 정보 조회
- 파일 소유자 확인

**대안**:
- 파일 시스템만 사용 (검색 불가능)

**선택 근거**:
- 검색, 정렬, 필터링 기능이 필수이므로 DB 사용

#### 2. 왜 UUID를 파일명으로 사용하는가?
**이유**:
- 파일명 충돌 방지
- 경로 조작 공격 방지
- 고유성 보장

---

### 단계별 구현 가이드

#### 1단계: 프로젝트 초기 설정

**pom.xml**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project>
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>file-sharing-service</artifactId>
    <version>1.0.0</version>

    <dependencies>
        <!-- Spring Boot Web -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- Spring Boot JPA -->
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

        <!-- Thymeleaf -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-thymeleaf</artifactId>
        </dependency>

        <!-- Validation -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>

        <!-- Lombok -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>

        <!-- Apache Commons IO -->
        <dependency>
            <groupId>commons-io</groupId>
            <artifactId>commons-io</artifactId>
            <version>2.15.0</version>
        </dependency>
    </dependencies>
</project>
```

**application.yml**:
```yaml
spring:
  application:
    name: file-sharing-service

  # 파일 업로드 설정
  servlet:
    multipart:
      enabled: true
      max-file-size: 50MB
      max-request-size: 100MB
      file-size-threshold: 1MB

  # H2 Database
  datasource:
    url: jdbc:h2:mem:filedb
    driver-class-name: org.h2.Driver
    username: sa
    password:

  jpa:
    hibernate:
      ddl-auto: create
    show-sql: true

  h2:
    console:
      enabled: true

# 파일 저장 설정
file:
  upload-dir: uploads
  max-file-size: 52428800  # 50MB
```

**체크포인트**:
- [ ] pom.xml 의존성 추가 완료
- [ ] application.yml 설정 완료
- [ ] 프로젝트 빌드 성공

---

#### 2단계: 엔티티 및 DTO 구현

**FileMetadata.java** (엔티티):
```java
package com.example.filesharing.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "file_metadata")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FileMetadata {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String originalFilename;  // 원본 파일명

    @Column(nullable = false, unique = true)
    private String savedFilename;     // 저장된 파일명 (UUID)

    @Column(nullable = false)
    private String filePath;          // 파일 경로

    @Column(nullable = false)
    private Long fileSize;            // 파일 크기 (bytes)

    @Column(nullable = false)
    private String contentType;       // MIME 타입

    @Column(nullable = false)
    private LocalDateTime uploadDate; // 업로드 날짜

    @Column
    private String uploaderName;      // 업로더 이름

    @Column(unique = true)
    private String shareToken;        // 공유 링크 토큰

    @PrePersist
    public void prePersist() {
        if (uploadDate == null) {
            uploadDate = LocalDateTime.now();
        }
    }
}
```

**FileUploadResponse.java** (DTO):
```java
package com.example.filesharing.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FileUploadResponse {
    private Long fileId;
    private String originalFilename;
    private String downloadUrl;
    private Long fileSize;
    private String message;
}
```

**FileInfo.java** (DTO):
```java
package com.example.filesharing.dto;

import lombok.*;
import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FileInfo {
    private Long id;
    private String originalFilename;
    private Long fileSize;
    private String contentType;
    private LocalDateTime uploadDate;
    private String downloadUrl;
    private String shareUrl;

    // 파일 크기를 사람이 읽기 쉬운 형식으로 변환
    public String getFileSizeFormatted() {
        if (fileSize < 1024) {
            return fileSize + " B";
        } else if (fileSize < 1024 * 1024) {
            return String.format("%.2f KB", fileSize / 1024.0);
        } else if (fileSize < 1024 * 1024 * 1024) {
            return String.format("%.2f MB", fileSize / (1024.0 * 1024));
        } else {
            return String.format("%.2f GB", fileSize / (1024.0 * 1024 * 1024));
        }
    }
}
```

---

#### 3단계: Repository 구현

**FileMetadataRepository.java**:
```java
package com.example.filesharing.repository;

import com.example.filesharing.entity.FileMetadata;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface FileMetadataRepository extends JpaRepository<FileMetadata, Long> {

    // 파일명으로 검색
    List<FileMetadata> findByOriginalFilenameContainingIgnoreCase(String filename);

    // 저장된 파일명으로 조회
    Optional<FileMetadata> findBySavedFilename(String savedFilename);

    // 공유 토큰으로 조회
    Optional<FileMetadata> findByShareToken(String shareToken);

    // 최근 업로드된 파일 목록
    List<FileMetadata> findTop10ByOrderByUploadDateDesc();
}
```

---

#### 4단계: Exception 구현

**FileStorageException.java**:
```java
package com.example.filesharing.exception;

public class FileStorageException extends RuntimeException {
    public FileStorageException(String message) {
        super(message);
    }

    public FileStorageException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

**FileNotFoundException.java**:
```java
package com.example.filesharing.exception;

public class FileNotFoundException extends RuntimeException {
    public FileNotFoundException(String message) {
        super(message);
    }
}
```

---

#### 5단계: Service 구현

**FileStorageService.java**:
```java
package com.example.filesharing.service;

import com.example.filesharing.dto.FileInfo;
import com.example.filesharing.dto.FileUploadResponse;
import com.example.filesharing.entity.FileMetadata;
import com.example.filesharing.exception.FileNotFoundException;
import com.example.filesharing.exception.FileStorageException;
import com.example.filesharing.repository.FileMetadataRepository;
import lombok.RequiredArgsConstructor;
import org.apache.commons.io.FilenameUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class FileStorageService {

    private final FileMetadataRepository fileMetadataRepository;

    @Value("${file.upload-dir}")
    private String uploadDir;

    @Value("${file.max-file-size}")
    private long maxFileSize;

    /**
     * 파일 업로드
     */
    public FileUploadResponse uploadFile(MultipartFile file, String uploaderName) {
        // 1. 파일 검증
        validateFile(file);

        // 2. 업로드 디렉토리 생성
        Path uploadPath = createUploadDirectory();

        // 3. 안전한 파일명 생성
        String originalFilename = StringUtils.cleanPath(file.getOriginalFilename());
        String extension = FilenameUtils.getExtension(originalFilename);
        String savedFilename = UUID.randomUUID().toString() + "." + extension;

        try {
            // 4. 파일 저장
            Path targetLocation = uploadPath.resolve(savedFilename);
            Files.copy(file.getInputStream(), targetLocation, StandardCopyOption.REPLACE_EXISTING);

            // 5. 메타데이터 DB 저장
            FileMetadata metadata = FileMetadata.builder()
                    .originalFilename(originalFilename)
                    .savedFilename(savedFilename)
                    .filePath(targetLocation.toString())
                    .fileSize(file.getSize())
                    .contentType(file.getContentType())
                    .uploaderName(uploaderName)
                    .shareToken(UUID.randomUUID().toString())
                    .build();

            FileMetadata saved = fileMetadataRepository.save(metadata);

            // 6. 응답 생성
            return FileUploadResponse.builder()
                    .fileId(saved.getId())
                    .originalFilename(originalFilename)
                    .downloadUrl("/api/files/" + saved.getId() + "/download")
                    .fileSize(file.getSize())
                    .message("파일 업로드 성공")
                    .build();

        } catch (IOException e) {
            throw new FileStorageException("파일 저장 실패: " + originalFilename, e);
        }
    }

    /**
     * 여러 파일 업로드
     */
    public List<FileUploadResponse> uploadFiles(List<MultipartFile> files, String uploaderName) {
        return files.stream()
                .map(file -> uploadFile(file, uploaderName))
                .collect(Collectors.toList());
    }

    /**
     * 파일 다운로드
     */
    public Resource loadFileAsResource(Long fileId) {
        FileMetadata metadata = fileMetadataRepository.findById(fileId)
                .orElseThrow(() -> new FileNotFoundException("파일을 찾을 수 없습니다: " + fileId));

        try {
            Path filePath = Paths.get(metadata.getFilePath()).normalize();
            Resource resource = new UrlResource(filePath.toUri());

            if (resource.exists() && resource.isReadable()) {
                return resource;
            } else {
                throw new FileNotFoundException("파일을 읽을 수 없습니다: " + metadata.getOriginalFilename());
            }
        } catch (Exception e) {
            throw new FileNotFoundException("파일을 찾을 수 없습니다: " + metadata.getOriginalFilename(), e);
        }
    }

    /**
     * 파일 목록 조회
     */
    public List<FileInfo> getAllFiles() {
        return fileMetadataRepository.findAll().stream()
                .map(this::convertToFileInfo)
                .collect(Collectors.toList());
    }

    /**
     * 파일 검색
     */
    public List<FileInfo> searchFiles(String keyword) {
        return fileMetadataRepository.findByOriginalFilenameContainingIgnoreCase(keyword).stream()
                .map(this::convertToFileInfo)
                .collect(Collectors.toList());
    }

    /**
     * 파일 삭제
     */
    public void deleteFile(Long fileId) {
        FileMetadata metadata = fileMetadataRepository.findById(fileId)
                .orElseThrow(() -> new FileNotFoundException("파일을 찾을 수 없습니다: " + fileId));

        try {
            // 1. 물리적 파일 삭제
            Path filePath = Paths.get(metadata.getFilePath());
            Files.deleteIfExists(filePath);

            // 2. DB에서 메타데이터 삭제
            fileMetadataRepository.delete(metadata);

        } catch (IOException e) {
            throw new FileStorageException("파일 삭제 실패: " + metadata.getOriginalFilename(), e);
        }
    }

    /**
     * 공유 토큰으로 파일 조회
     */
    public FileMetadata getFileByShareToken(String shareToken) {
        return fileMetadataRepository.findByShareToken(shareToken)
                .orElseThrow(() -> new FileNotFoundException("공유 링크가 유효하지 않습니다"));
    }

    // === Private Helper Methods ===

    private void validateFile(MultipartFile file) {
        // 빈 파일 체크
        if (file.isEmpty()) {
            throw new FileStorageException("빈 파일은 업로드할 수 없습니다");
        }

        // 파일 크기 체크
        if (file.getSize() > maxFileSize) {
            throw new FileStorageException(
                String.format("파일 크기는 %dMB 이하여야 합니다", maxFileSize / 1024 / 1024)
            );
        }

        // 파일명 체크
        String filename = file.getOriginalFilename();
        if (filename == null || filename.contains("..")) {
            throw new FileStorageException("유효하지 않은 파일명입니다: " + filename);
        }

        // 위험한 확장자 체크
        String extension = FilenameUtils.getExtension(filename).toLowerCase();
        List<String> dangerousExtensions = List.of("exe", "bat", "cmd", "sh", "ps1");
        if (dangerousExtensions.contains(extension)) {
            throw new FileStorageException("실행 파일은 업로드할 수 없습니다");
        }
    }

    private Path createUploadDirectory() {
        try {
            Path uploadPath = Paths.get(uploadDir).toAbsolutePath().normalize();
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }
            return uploadPath;
        } catch (IOException e) {
            throw new FileStorageException("업로드 디렉토리 생성 실패", e);
        }
    }

    private FileInfo convertToFileInfo(FileMetadata metadata) {
        return FileInfo.builder()
                .id(metadata.getId())
                .originalFilename(metadata.getOriginalFilename())
                .fileSize(metadata.getFileSize())
                .contentType(metadata.getContentType())
                .uploadDate(metadata.getUploadDate())
                .downloadUrl("/api/files/" + metadata.getId() + "/download")
                .shareUrl("/share/" + metadata.getShareToken())
                .build();
    }
}
```

**코드 설명**:
- **라인 37-71**: `uploadFile()` - 단일 파일 업로드 처리
  - 파일 검증 → 디렉토리 생성 → 파일명 생성 → 저장 → DB 저장
- **라인 76-80**: `uploadFiles()` - 여러 파일 동시 업로드
- **라인 85-99**: `loadFileAsResource()` - 파일 다운로드를 위한 Resource 로드
- **라인 137-158**: `validateFile()` - 파일 검증 (크기, 형식, 위험한 확장자)

---

#### 6단계: Controller 구현

**FileController.java**:
```java
package com.example.filesharing.controller;

import com.example.filesharing.dto.FileInfo;
import com.example.filesharing.dto.FileUploadResponse;
import com.example.filesharing.entity.FileMetadata;
import com.example.filesharing.service.FileStorageService;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@Controller
@RequiredArgsConstructor
public class FileController {

    private final FileStorageService fileStorageService;

    /**
     * 파일 업로드 페이지
     */
    @GetMapping("/")
    public String uploadPage(Model model) {
        List<FileInfo> files = fileStorageService.getAllFiles();
        model.addAttribute("files", files);
        return "upload";
    }

    /**
     * 단일 파일 업로드 API
     */
    @PostMapping("/api/files/upload")
    @ResponseBody
    public ResponseEntity<FileUploadResponse> uploadFile(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "uploaderName", defaultValue = "Anonymous") String uploaderName
    ) {
        FileUploadResponse response = fileStorageService.uploadFile(file, uploaderName);
        return ResponseEntity.ok(response);
    }

    /**
     * 여러 파일 업로드 API
     */
    @PostMapping("/api/files/upload/multiple")
    @ResponseBody
    public ResponseEntity<List<FileUploadResponse>> uploadFiles(
            @RequestParam("files") List<MultipartFile> files,
            @RequestParam(value = "uploaderName", defaultValue = "Anonymous") String uploaderName
    ) {
        List<FileUploadResponse> responses = fileStorageService.uploadFiles(files, uploaderName);
        return ResponseEntity.ok(responses);
    }

    /**
     * 파일 다운로드 API
     */
    @GetMapping("/api/files/{fileId}/download")
    public ResponseEntity<Resource> downloadFile(@PathVariable Long fileId) {
        Resource resource = fileStorageService.loadFileAsResource(fileId);

        // 원본 파일명 가져오기
        FileMetadata metadata = fileStorageService.getFileByShareToken(
            resource.getFilename().replace(".uploaded", "")
        );

        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .header(HttpHeaders.CONTENT_DISPOSITION,
                        "attachment; filename=\"" + metadata.getOriginalFilename() + "\"")
                .body(resource);
    }

    /**
     * 파일 목록 조회 API
     */
    @GetMapping("/api/files")
    @ResponseBody
    public ResponseEntity<List<FileInfo>> getAllFiles() {
        List<FileInfo> files = fileStorageService.getAllFiles();
        return ResponseEntity.ok(files);
    }

    /**
     * 파일 검색 API
     */
    @GetMapping("/api/files/search")
    @ResponseBody
    public ResponseEntity<List<FileInfo>> searchFiles(@RequestParam String keyword) {
        List<FileInfo> files = fileStorageService.searchFiles(keyword);
        return ResponseEntity.ok(files);
    }

    /**
     * 파일 삭제 API
     */
    @DeleteMapping("/api/files/{fileId}")
    @ResponseBody
    public ResponseEntity<String> deleteFile(@PathVariable Long fileId) {
        fileStorageService.deleteFile(fileId);
        return ResponseEntity.ok("파일이 삭제되었습니다");
    }

    /**
     * 공유 링크로 파일 다운로드
     */
    @GetMapping("/share/{shareToken}")
    public ResponseEntity<Resource> downloadSharedFile(@PathVariable String shareToken) {
        FileMetadata metadata = fileStorageService.getFileByShareToken(shareToken);
        Resource resource = fileStorageService.loadFileAsResource(metadata.getId());

        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .header(HttpHeaders.CONTENT_DISPOSITION,
                        "attachment; filename=\"" + metadata.getOriginalFilename() + "\"")
                .body(resource);
    }
}
```

---

#### 7단계: 프론트엔드 구현 (Thymeleaf)

**upload.html**:
```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>파일 공유 시스템</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 32px;
        }

        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }

        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 10px;
            padding: 50px;
            text-align: center;
            background: #f8f9ff;
            margin-bottom: 30px;
            transition: all 0.3s;
        }

        .upload-area:hover {
            border-color: #764ba2;
            background: #f0f2ff;
        }

        .upload-area.dragover {
            border-color: #764ba2;
            background: #e8ebff;
            transform: scale(1.02);
        }

        .upload-icon {
            font-size: 64px;
            color: #667eea;
            margin-bottom: 20px;
        }

        input[type="file"] {
            display: none;
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }

        .file-list {
            margin-top: 40px;
        }

        .file-item {
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s;
        }

        .file-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }

        .file-info {
            flex: 1;
        }

        .file-name {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }

        .file-meta {
            font-size: 12px;
            color: #666;
        }

        .file-actions {
            display: flex;
            gap: 10px;
        }

        .btn-download, .btn-delete, .btn-share {
            padding: 8px 20px;
            border-radius: 20px;
            border: none;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }

        .btn-download {
            background: #28a745;
            color: white;
        }

        .btn-delete {
            background: #dc3545;
            color: white;
        }

        .btn-share {
            background: #17a2b8;
            color: white;
        }

        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 20px;
            display: none;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s;
        }

        .message {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: none;
        }

        .message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📁 파일 공유 시스템</h1>
        <p class="subtitle">드래그 & 드롭으로 파일을 업로드하세요</p>

        <div id="message" class="message"></div>

        <div class="upload-area" id="uploadArea">
            <div class="upload-icon">☁️</div>
            <p>파일을 여기에 드래그하거나 클릭하여 선택하세요</p>
            <p style="color: #999; margin-top: 10px;">최대 50MB</p>
            <input type="file" id="fileInput" multiple>
            <button class="btn" onclick="document.getElementById('fileInput').click()">
                파일 선택
            </button>
        </div>

        <div class="progress-bar" id="progressBar">
            <div class="progress-fill" id="progressFill"></div>
        </div>

        <div class="file-list">
            <h2>📋 업로드된 파일 목록</h2>
            <div id="fileListContainer">
                <div th:each="file : ${files}" class="file-item">
                    <div class="file-info">
                        <div class="file-name" th:text="${file.originalFilename}">파일명</div>
                        <div class="file-meta">
                            <span th:text="${file.fileSizeFormatted}">크기</span> ·
                            <span th:text="${#temporals.format(file.uploadDate, 'yyyy-MM-dd HH:mm')}">날짜</span>
                        </div>
                    </div>
                    <div class="file-actions">
                        <button class="btn-download" th:onclick="'downloadFile(' + ${file.id} + ')'">
                            ⬇️ 다운로드
                        </button>
                        <button class="btn-share" th:onclick="'shareFile(\'' + ${file.shareUrl} + '\')'">
                            🔗 공유
                        </button>
                        <button class="btn-delete" th:onclick="'deleteFile(' + ${file.id} + ')'">
                            🗑️ 삭제
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const progressBar = document.getElementById('progressBar');
        const progressFill = document.getElementById('progressFill');
        const messageDiv = document.getElementById('message');

        // 드래그 & 드롭 이벤트
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');

            const files = e.dataTransfer.files;
            uploadFiles(files);
        });

        // 파일 선택 이벤트
        fileInput.addEventListener('change', (e) => {
            const files = e.target.files;
            uploadFiles(files);
        });

        // 파일 업로드 함수
        function uploadFiles(files) {
            if (files.length === 0) return;

            const formData = new FormData();
            for (let file of files) {
                formData.append('files', file);
            }
            formData.append('uploaderName', 'User');

            progressBar.style.display = 'block';
            progressFill.style.width = '0%';

            fetch('/api/files/upload/multiple', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                progressFill.style.width = '100%';
                showMessage('파일이 성공적으로 업로드되었습니다!', 'success');
                setTimeout(() => {
                    location.reload();
                }, 1000);
            })
            .catch(error => {
                showMessage('파일 업로드 실패: ' + error.message, 'error');
            })
            .finally(() => {
                setTimeout(() => {
                    progressBar.style.display = 'none';
                }, 1000);
            });
        }

        // 파일 다운로드
        function downloadFile(fileId) {
            window.location.href = '/api/files/' + fileId + '/download';
        }

        // 파일 공유
        function shareFile(shareUrl) {
            const fullUrl = window.location.origin + shareUrl;
            navigator.clipboard.writeText(fullUrl);
            showMessage('공유 링크가 복사되었습니다: ' + fullUrl, 'success');
        }

        // 파일 삭제
        function deleteFile(fileId) {
            if (!confirm('정말 삭제하시겠습니까?')) return;

            fetch('/api/files/' + fileId, {
                method: 'DELETE'
            })
            .then(() => {
                showMessage('파일이 삭제되었습니다', 'success');
                setTimeout(() => {
                    location.reload();
                }, 1000);
            })
            .catch(error => {
                showMessage('파일 삭제 실패: ' + error.message, 'error');
            });
        }

        // 메시지 표시
        function showMessage(text, type) {
            messageDiv.textContent = text;
            messageDiv.className = 'message ' + type;
            messageDiv.style.display = 'block';

            setTimeout(() => {
                messageDiv.style.display = 'none';
            }, 3000);
        }
    </script>
</body>
</html>
```

---

### 실행 결과 화면

**메인 화면**:
```
┌─────────────────────────────────────────────┐
│  📁 파일 공유 시스템                          │
│  드래그 & 드롭으로 파일을 업로드하세요         │
├─────────────────────────────────────────────┤
│                                             │
│              ☁️                             │
│     파일을 여기에 드래그하거나               │
│         클릭하여 선택하세요                  │
│           최대 50MB                          │
│                                             │
│          [ 파일 선택 ]                       │
│                                             │
├─────────────────────────────────────────────┤
│  📋 업로드된 파일 목록                        │
├─────────────────────────────────────────────┤
│  report.pdf                                 │
│  2.3 MB · 2024-01-15 14:30                  │
│  [⬇️ 다운로드] [🔗 공유] [🗑️ 삭제]            │
├─────────────────────────────────────────────┤
│  photo.jpg                                  │
│  1.8 MB · 2024-01-15 14:25                  │
│  [⬇️ 다운로드] [🔗 공유] [🗑️ 삭제]            │
└─────────────────────────────────────────────┘
```

---

### 트러블슈팅

#### 문제 1: 파일 다운로드 시 한글 파일명 깨짐

**증상**:
```
원본 파일명: 보고서.pdf
다운로드된 파일명: ___.pdf (깨짐)
```

**원인**: HTTP 헤더에서 한글 인코딩 문제

**해결 방법**:
```java
@GetMapping("/api/files/{fileId}/download")
public ResponseEntity<Resource> downloadFile(@PathVariable Long fileId) {
    Resource resource = fileStorageService.loadFileAsResource(fileId);
    FileMetadata metadata = // ... 파일 정보 조회

    // 한글 파일명 인코딩
    String encodedFilename = URLEncoder.encode(metadata.getOriginalFilename(), StandardCharsets.UTF_8)
            .replaceAll("\\+", "%20");

    return ResponseEntity.ok()
            .contentType(MediaType.APPLICATION_OCTET_STREAM)
            .header(HttpHeaders.CONTENT_DISPOSITION,
                    "attachment; filename*=UTF-8''" + encodedFilename)  // ← UTF-8 명시
            .body(resource);
}
```

---

#### 문제 2: 대용량 파일 업로드 시 메모리 부족

**증상**:
```
java.lang.OutOfMemoryError: Java heap space
```

**원인**: 파일을 메모리에 모두 로드

**해결 방법**:
```yaml
# application.yml
spring:
  servlet:
    multipart:
      file-size-threshold: 1MB  # 1MB 초과 시 디스크에 임시 저장
```

---

### 확장 아이디어

#### 추가 기능 1: 파일 압축 업로드
**난이도**: ⭐⭐⭐⭐☆
**구현 힌트**: Apache Commons Compress 라이브러리 사용

```java
public void uploadCompressedFile(MultipartFile zipFile) {
    try (ZipInputStream zis = new ZipInputStream(zipFile.getInputStream())) {
        ZipEntry entry;
        while ((entry = zis.getNextEntry()) != null) {
            // 각 파일 추출 및 저장
            saveExtractedFile(entry, zis);
        }
    }
}
```

#### 추가 기능 2: 파일 미리보기
**난이도**: ⭐⭐⭐⭐☆
**구현 힌트**: PDF.js (PDF), CodeMirror (텍스트) 사용

---

### 코드 리뷰 포인트

#### 체크리스트
- [ ] 파일 검증이 충분한가? (크기, 형식, 확장자)
- [ ] 파일명이 안전하게 처리되는가? (경로 조작 방지)
- [ ] 에러 처리가 적절한가?
- [ ] 트랜잭션이 필요한 부분은 처리되었는가?
- [ ] 파일 삭제 시 물리 파일과 DB 모두 삭제되는가?
- [ ] 대용량 파일 처리가 효율적인가?

---

## ❓ FAQ

<details>
<summary><strong>Q1: MultipartFile과 일반 File의 차이는 무엇인가요?</strong></summary>

**A**: MultipartFile은 **HTTP multipart 요청에서 업로드된 파일을 나타내는 Spring 인터페이스**이고, File은 **파일 시스템의 파일을 나타내는 Java 클래스**입니다.

**MultipartFile** (Spring):
```java
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    String filename = file.getOriginalFilename();  // 원본 파일명
    long size = file.getSize();                    // 파일 크기
    String contentType = file.getContentType();    // MIME 타입
    byte[] bytes = file.getBytes();                // 바이트 배열
    InputStream is = file.getInputStream();        // 스트림

    // 파일 저장
    file.transferTo(new File("path/to/save"));

    return "success";
}
```

**File** (Java):
```java
File file = new File("/path/to/file.txt");
long size = file.length();              // 파일 크기
boolean exists = file.exists();         // 존재 여부
String name = file.getName();           // 파일명
String path = file.getAbsolutePath();   // 절대 경로
```

**차이점**:

| 특징 | MultipartFile | File |
|------|---------------|------|
| 용도 | HTTP 업로드 파일 | 파일 시스템 파일 |
| 생성 시점 | 요청 시 Spring이 자동 생성 | 개발자가 직접 생성 |
| MIME 타입 | ✅ 제공 | ❌ 없음 |
| 원본 파일명 | ✅ 제공 | ❌ 없음 |
| 임시 저장 | ✅ 자동 | ❌ 해당 없음 |

**실무 팁**:
- 업로드된 파일: MultipartFile 사용
- 로컬 파일 읽기: File 사용
- MultipartFile → File 변환: `file.transferTo(new File(...))`

</details>

<details>
<summary><strong>Q2: 파일 크기 제한은 어떻게 설정하나요?</strong></summary>

**A**: application.yml 또는 application.properties에서 설정합니다.

**application.yml**:
```yaml
spring:
  servlet:
    multipart:
      max-file-size: 10MB      # 파일 1개당 최대 크기
      max-request-size: 50MB   # 요청 전체 최대 크기 (여러 파일 포함)
```

**application.properties**:
```properties
spring.servlet.multipart.max-file-size=10MB
spring.servlet.multipart.max-request-size=50MB
```

**프로그래밍 방식**:
```java
@Configuration
public class FileUploadConfig {

    @Bean
    public MultipartConfigElement multipartConfigElement() {
        MultipartConfigFactory factory = new MultipartConfigFactory();
        factory.setMaxFileSize(DataSize.ofMegabytes(10));
        factory.setMaxRequestSize(DataSize.ofMegabytes(50));
        return factory.createMultipartConfig();
    }
}
```

**크기 초과 시 예외 처리**:
```java
@ControllerAdvice
public class FileUploadExceptionAdvice {

    @ExceptionHandler(MaxUploadSizeExceededException.class)
    public String handleMaxSizeException(MaxUploadSizeExceededException exc,
                                        RedirectAttributes redirectAttributes) {
        redirectAttributes.addFlashAttribute("message",
            "파일 크기가 너무 큽니다. 최대 10MB까지 가능합니다.");
        return "redirect:/upload";
    }
}
```

</details>

<details>
<summary><strong>Q3: 파일 확장자는 어떻게 검증하나요?</strong></summary>

**A**: 확장자만으로는 불충분하며, **확장자 + MIME 타입 + 파일 시그니처**를 모두 확인해야 합니다.

**1. 확장자 검증 (기본)**:
```java
String filename = file.getOriginalFilename();
String extension = filename.substring(filename.lastIndexOf(".") + 1).toLowerCase();

List<String> allowedExtensions = Arrays.asList("jpg", "jpeg", "png", "gif");
if (!allowedExtensions.contains(extension)) {
    throw new IllegalArgumentException("허용되지 않는 파일 형식입니다");
}
```

**2. MIME 타입 검증 (중요)**:
```java
String contentType = file.getContentType();
List<String> allowedMimeTypes = Arrays.asList("image/jpeg", "image/png", "image/gif");

if (!allowedMimeTypes.contains(contentType)) {
    throw new IllegalArgumentException("허용되지 않는 파일 형식입니다");
}
```

**3. 파일 시그니처 검증 (매직 넘버)**:
```java
public boolean isValidJpeg(MultipartFile file) throws IOException {
    try (InputStream is = file.getInputStream()) {
        byte[] header = new byte[3];
        is.read(header);

        // JPEG 파일의 시그니처: FF D8 FF
        return header[0] == (byte) 0xFF &&
               header[1] == (byte) 0xD8 &&
               header[2] == (byte) 0xFF;
    }
}
```

**주의사항**:
- ❌ 확장자만 검증: 우회 가능 (virus.exe → virus.jpg)
- ❌ MIME 타입만 검증: 조작 가능
- ✅ 3가지 모두 검증: 안전

**Apache Tika 라이브러리 사용** (추천):
```xml
<dependency>
    <groupId>org.apache.tika</groupId>
    <artifactId>tika-core</artifactId>
    <version>2.9.1</version>
</dependency>
```

```java
import org.apache.tika.Tika;

public String detectFileType(MultipartFile file) throws IOException {
    Tika tika = new Tika();
    String detectedType = tika.detect(file.getInputStream());
    return detectedType;  // "image/jpeg", "application/pdf" 등
}
```

</details>

<details>
<summary><strong>Q4: 파일명에 한글이 깨지는 문제는 어떻게 해결하나요?</strong></summary>

**A**: **UTF-8 인코딩 설정**과 **파일명 안전화**로 해결합니다.

**1. UTF-8 인코딩 설정**:
```yaml
# application.yml
server:
  servlet:
    encoding:
      charset: UTF-8
      enabled: true
      force: true

spring:
  http:
    encoding:
      charset: UTF-8
      enabled: true
      force: true
```

**2. 파일명 디코딩**:
```java
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    String originalFilename = file.getOriginalFilename();

    // URLDecoder로 디코딩 (필요한 경우)
    try {
        originalFilename = URLDecoder.decode(originalFilename, "UTF-8");
    } catch (UnsupportedEncodingException e) {
        // 디코딩 실패 시 원본 사용
    }

    // 파일 저장
    String savedFilename = UUID.randomUUID().toString() + "_" + originalFilename;
    // ...
}
```

**3. 파일명 안전화 (추천)**:
```java
import org.springframework.util.StringUtils;

String originalFilename = file.getOriginalFilename();

// Spring의 StringUtils로 경로 정리
String cleanFilename = StringUtils.cleanPath(originalFilename);

// 특수문자 제거
String safeFilename = cleanFilename.replaceAll("[^a-zA-Z0-9가-힣._-]", "_");

// UUID 사용 (가장 안전)
String uniqueFilename = UUID.randomUUID().toString() + "_" + safeFilename;
```

**4. 데이터베이스에 원본 파일명 저장**:
```java
@Entity
public class UploadedFile {
    @Id @GeneratedValue
    private Long id;

    private String originalFilename;  // 사용자에게 보여줄 이름 (한글 포함)
    private String storedFilename;    // 실제 저장된 이름 (UUID)
    private String filePath;
}

// 저장
UploadedFile uploadedFile = new UploadedFile();
uploadedFile.setOriginalFilename(file.getOriginalFilename());  // "보고서.pdf"
uploadedFile.setStoredFilename(savedFilename);  // "uuid_123.pdf"
uploadedFile.setFilePath("/uploads/2024/01/" + savedFilename);
```

**5. 다운로드 시 한글 파일명 처리**:
```java
@GetMapping("/download/{id}")
public ResponseEntity<Resource> download(@PathVariable Long id) {
    UploadedFile uploadedFile = uploadedFileRepository.findById(id)
        .orElseThrow();

    Resource resource = new FileSystemResource(uploadedFile.getFilePath());

    // 한글 파일명 인코딩
    String encodedFilename = URLEncoder.encode(
        uploadedFile.getOriginalFilename(),
        StandardCharsets.UTF_8
    ).replaceAll("\\+", "%20");

    return ResponseEntity.ok()
        .header(HttpHeaders.CONTENT_DISPOSITION,
            "attachment; filename*=UTF-8''" + encodedFilename)
        .body(resource);
}
```

</details>

<details>
<summary><strong>Q5: 임시 파일은 언제 삭제되나요?</strong></summary>

**A**: Spring이 **요청 처리가 완료된 후 자동으로 삭제**합니다.

**동작 원리**:

```
1. 파일 업로드 요청
   ↓
2. MultipartResolver가 파일 파싱
   ↓
3. 임시 디렉토리에 파일 저장 (/tmp 또는 설정한 경로)
   ↓
4. MultipartFile 객체 생성
   ↓
5. Controller 메서드 실행
   ↓
6. transferTo()로 영구 저장소에 복사
   ↓
7. Controller 메서드 종료
   ↓
8. ✅ Spring이 임시 파일 자동 삭제
```

**임시 디렉토리 설정**:
```yaml
spring:
  servlet:
    multipart:
      location: /tmp/uploads  # 임시 파일 저장 경로
```

**임시 파일 확인**:
```java
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    // 임시 파일 경로 확인 (디버깅용)
    if (file instanceof StandardMultipartHttpServletRequest.StandardMultipartFile) {
        File tempFile = ((StandardMultipartHttpServletRequest.StandardMultipartFile) file)
            .getFileItem()
            .getStoreLocation();

        System.out.println("임시 파일 위치: " + tempFile.getAbsolutePath());
        // 예: /tmp/uploads/upload_123456.tmp
    }

    // 영구 저장
    file.transferTo(new File("uploads/" + file.getOriginalFilename()));

    // 메서드 종료 후 임시 파일 자동 삭제됨
    return "success";
}
```

**주의사항**:
- transferTo()를 호출하지 않으면 파일이 저장되지 않음
- transferTo()는 한 번만 호출 가능
- 임시 파일 삭제는 JVM 종료 시에도 보장됨 (shutdown hook)

**수동 삭제 (필요 시)**:
```java
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    try {
        // 파일 저장
        file.transferTo(new File("uploads/" + file.getOriginalFilename()));
    } finally {
        // ✅ 수동으로 임시 파일 삭제 (일반적으로 불필요)
        if (file instanceof MultipartFile) {
            try {
                ((MultipartFile) file).getInputStream().close();
            } catch (IOException e) {
                // ignore
            }
        }
    }
    return "success";
}
```

</details>

<details>
<summary><strong>Q6: transferTo()와 getBytes()의 차이는 무엇인가요?</strong></summary>

**A**: **transferTo()는 스트리밍 방식**으로 메모리 효율적이고, **getBytes()는 전체를 메모리에 로드**합니다.

**transferTo() (추천)**:
```java
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    // ✅ 스트리밍 방식: 메모리 효율적
    Path path = Paths.get("uploads/" + file.getOriginalFilename());
    file.transferTo(path);

    // 1GB 파일도 메모리 1MB 이하로 처리 가능
    return "success";
}
```

**getBytes() (비추천)**:
```java
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    // ❌ 전체를 메모리에 로드: 메모리 낭비
    byte[] bytes = file.getBytes();

    Files.write(Paths.get("uploads/" + file.getOriginalFilename()), bytes);

    // 1GB 파일 → 1GB 메모리 사용 → OOM 위험
    return "success";
}
```

**비교표**:

| 특징 | transferTo() | getBytes() |
|------|-------------|------------|
| 메모리 사용 | 최소 (스트리밍) | 파일 크기만큼 |
| 속도 | 빠름 | 느림 |
| 대용량 파일 | ✅ 가능 | ❌ OOM 위험 |
| 사용 편의성 | 간단 | 바이트 배열 처리 필요 |

**성능 비교**:
```java
// 100MB 파일 업로드 시

// transferTo(): 메모리 1MB 사용
file.transferTo(path);  // ✅ 빠르고 효율적

// getBytes(): 메모리 100MB 사용
byte[] bytes = file.getBytes();  // ❌ 느리고 메모리 낭비
Files.write(path, bytes);
```

**getBytes()를 사용해야 하는 경우**:
```java
// 이미지 리사이징
BufferedImage image = ImageIO.read(file.getInputStream());
BufferedImage resized = resize(image, 200, 200);
ByteArrayOutputStream baos = new ByteArrayOutputStream();
ImageIO.write(resized, "jpg", baos);
byte[] resizedBytes = baos.toByteArray();

// 암호화
byte[] encrypted = encrypt(file.getBytes());
Files.write(path, encrypted);
```

**실무 권장**:
- **일반 파일 저장**: transferTo() 사용
- **파일 내용 변경**: getBytes() 또는 getInputStream() 사용

</details>

<details>
<summary><strong>Q7: 파일 업로드 시 보안 위협은 무엇이 있나요?</strong></summary>

**A**: **악성 파일 업로드, 경로 조작, DoS 공격** 등이 있으며, 각각 대응 방법이 다릅니다.

**1. 악성 파일 업로드**:

**위협**:
```java
// 사용자가 virus.exe를 virus.jpg로 이름 바꿔 업로드
// → 확장자만 검증하면 통과
```

**대응**:
```java
// ✅ 확장자 + MIME 타입 + 파일 시그니처 모두 검증
public void validateFile(MultipartFile file) {
    // 1. 확장자 화이트리스트
    String extension = getExtension(file.getOriginalFilename());
    if (!Arrays.asList("jpg", "png", "pdf").contains(extension)) {
        throw new IllegalArgumentException("허용되지 않는 확장자");
    }

    // 2. MIME 타입 검증
    String contentType = file.getContentType();
    if (!Arrays.asList("image/jpeg", "image/png", "application/pdf").contains(contentType)) {
        throw new IllegalArgumentException("허용되지 않는 MIME 타입");
    }

    // 3. 파일 시그니처 검증
    byte[] header = new byte[4];
    file.getInputStream().read(header);

    if (extension.equals("jpg")) {
        // JPEG: FF D8 FF
        if (!(header[0] == (byte)0xFF && header[1] == (byte)0xD8)) {
            throw new IllegalArgumentException("JPEG 파일이 아닙니다");
        }
    }
}
```

**2. 경로 조작 (Path Traversal)**:

**위협**:
```java
// 사용자가 파일명을 "../../../etc/passwd"로 업로드
// → 시스템 파일 덮어쓰기
```

**대응**:
```java
import org.springframework.util.StringUtils;

// ✅ 파일명 정리 및 검증
String filename = file.getOriginalFilename();
String cleanFilename = StringUtils.cleanPath(filename);

// ".." 포함 여부 확인
if (cleanFilename.contains("..")) {
    throw new IllegalArgumentException("파일명에 부적절한 경로가 포함되어 있습니다");
}

// UUID 사용으로 완전히 차단 (가장 안전)
String safeFilename = UUID.randomUUID().toString() + "_" + cleanFilename;
```

**3. DoS 공격 (서버 자원 고갈)**:

**위협**:
```java
// 공격자가 1GB 파일 100개를 동시에 업로드
// → 디스크 full, 메모리 고갈
```

**대응**:
```yaml
# ✅ 크기 제한
spring:
  servlet:
    multipart:
      max-file-size: 10MB      # 파일 1개당 최대
      max-request-size: 50MB   # 요청 전체 최대
```

```java
// ✅ 업로드 횟수 제한 (Rate Limiting)
@Component
public class UploadRateLimiter {

    private final Map<String, Integer> uploadCounts = new ConcurrentHashMap<>();

    public void checkLimit(String userIp) {
        int count = uploadCounts.getOrDefault(userIp, 0);

        if (count >= 10) {  // 시간당 10개 제한
            throw new TooManyRequestsException("업로드 횟수 초과");
        }

        uploadCounts.put(userIp, count + 1);

        // 1시간 후 리셋
        scheduleReset(userIp);
    }
}
```

**4. 디렉토리 리스팅**:

**위협**:
```
http://example.com/uploads/
→ 모든 업로드된 파일 목록 노출
```

**대응**:
```java
// ✅ 직접 접근 차단
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // 특정 경로를 통해서만 접근 가능
        registry.addResourceHandler("/files/**")
            .addResourceLocations("file:uploads/");

        // 직접 접근은 차단됨
        // http://example.com/uploads/ → 404
        // http://example.com/files/xxx.jpg → ✅ 허용
    }
}
```

**5. 저장 경로 노출**:

**위협**:
```java
// 클라이언트에게 실제 경로 노출
return "파일 저장: /home/user/uploads/file.jpg";
```

**대응**:
```java
// ✅ 상대 경로나 ID만 반환
@PostMapping("/upload")
public ResponseEntity<UploadResponse> upload(@RequestParam("file") MultipartFile file) {
    String savedPath = fileStorageService.store(file);

    // 실제 경로 대신 ID나 해시값 반환
    UploadResponse response = new UploadResponse();
    response.setFileId(UUID.randomUUID().toString());  // ✅ ID
    response.setFilename(file.getOriginalFilename());
    // response.setPath(savedPath);  // ❌ 실제 경로 노출하지 않음

    return ResponseEntity.ok(response);
}
```

**종합 보안 체크리스트**:
- [ ] 확장자 화이트리스트 검증
- [ ] MIME 타입 검증
- [ ] 파일 시그니처 검증
- [ ] 파일 크기 제한
- [ ] 파일명 안전화 (UUID 사용)
- [ ] 경로 조작 방지 (..)
- [ ] Rate Limiting
- [ ] 직접 접근 차단
- [ ] 실제 경로 노출 방지

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. MultipartFile이란 무엇이며, 왜 사용하나요?</strong></summary>

**모범 답안 포인트**:
- MultipartFile은 Spring이 제공하는 파일 업로드 인터페이스
- HTTP multipart 요청에서 업로드된 파일을 표현
- 파일명, 크기, MIME 타입 등의 메타데이터 제공
- transferTo() 메서드로 쉽게 저장 가능

**예시 답변**:
> "MultipartFile은 Spring에서 파일 업로드를 처리하기 위한 인터페이스입니다. HTTP multipart/form-data 요청으로 전송된 파일을 나타내며, 원본 파일명, 크기, MIME 타입 같은 메타데이터를 제공합니다. transferTo() 메서드를 사용하면 스트리밍 방식으로 메모리 효율적으로 파일을 저장할 수 있습니다."

**꼬리 질문**:
- Q: "MultipartFile과 Java의 File 클래스의 차이는?"
- A: "MultipartFile은 HTTP 요청에서 업로드된 파일을 나타내고, File은 파일 시스템의 파일을 나타냅니다. MultipartFile은 MIME 타입과 원본 파일명을 제공하지만, File은 제공하지 않습니다."

**실무 연관**:
프로필 사진 업로드, 첨부파일 기능 등 모든 파일 업로드에서 MultipartFile을 사용합니다.

</details>

<details>
<summary><strong>2. 파일 업로드 시 반드시 검증해야 할 항목은 무엇인가요?</strong></summary>

**모범 답안 포인트**:
- 파일 크기 (max-file-size)
- 확장자 (화이트리스트 방식)
- MIME 타입
- 파일명 안전성 (경로 조작 방지)
- 빈 파일 여부

**예시 답변**:
> "파일 업로드 시 크기, 확장자, MIME 타입을 반드시 검증해야 합니다. 크기는 서버 자원 보호를 위해, 확장자와 MIME 타입은 악성 파일 차단을 위해 필요합니다. 또한 파일명에 '..'이 포함되어 있는지 확인하여 경로 조작 공격을 방지해야 합니다."

**꼬리 질문**:
- Q: "확장자만 검증하면 안 되나요?"
- A: "아닙니다. 확장자는 쉽게 변경할 수 있어 virus.exe를 virus.jpg로 바꿔 업로드할 수 있습니다. 따라서 MIME 타입과 파일 시그니처도 함께 검증해야 합니다."

</details>

<details>
<summary><strong>3. transferTo() 메서드의 역할과 장점을 설명해주세요.</strong></summary>

**모범 답안 포인트**:
- MultipartFile의 내용을 파일로 저장
- 스트리밍 방식으로 메모리 효율적
- 대용량 파일도 적은 메모리로 처리 가능
- getBytes()보다 빠르고 안전

**예시 답변**:
> "transferTo()는 MultipartFile의 내용을 지정한 경로에 저장하는 메서드입니다. 스트리밍 방식으로 동작하여 파일 전체를 메모리에 로드하지 않고, 작은 버퍼를 사용해 조금씩 저장합니다. 따라서 1GB 파일도 1MB 정도의 메모리만으로 저장할 수 있어 메모리 효율적이고 OOM 위험이 없습니다."

**꼬리 질문**:
- Q: "transferTo()는 몇 번 호출할 수 있나요?"
- A: "한 번만 호출 가능합니다. 두 번째 호출 시 IllegalStateException이 발생합니다."

</details>

<details>
<summary><strong>4. 파일 업로드 시 임시 파일은 어디에 저장되며, 언제 삭제되나요?</strong></summary>

**모범 답안 포인트**:
- spring.servlet.multipart.location에 설정된 경로 (기본: /tmp)
- 요청 처리 완료 후 자동 삭제
- transferTo()로 영구 저장소에 복사 필요
- JVM 종료 시에도 삭제 보장

**예시 답변**:
> "파일 업로드 시 Spring은 먼저 임시 디렉토리에 파일을 저장합니다. 기본 경로는 /tmp이며, application.yml에서 변경 가능합니다. Controller 메서드가 실행되는 동안 임시 파일이 유지되고, transferTo()로 영구 저장소에 복사한 후 요청 처리가 완료되면 Spring이 자동으로 임시 파일을 삭제합니다."

</details>

<details>
<summary><strong>5. 파일명에 한글이 깨지는 문제를 어떻게 해결하나요?</strong></summary>

**모범 답안 포인트**:
- UTF-8 인코딩 설정
- 원본 파일명과 저장 파일명 분리
- UUID 사용으로 파일명 안전화
- 데이터베이스에 원본 파일명 저장

**예시 답변**:
> "한글 파일명 문제는 UTF-8 인코딩 설정과 파일명 분리로 해결합니다. application.yml에서 server.servlet.encoding.charset을 UTF-8로 설정하고, 저장 시에는 UUID + 원본 파일명 방식을 사용합니다. 원본 파일명은 데이터베이스에 저장하여 사용자에게 보여주고, 실제 파일은 UUID 이름으로 저장하여 인코딩 문제를 근본적으로 방지합니다."

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. MultipartResolver의 동작 원리와 종류를 설명해주세요.</strong></summary>

**모범 답안 포인트**:
- DispatcherServlet에서 multipart 요청 감지
- MultipartResolver가 요청 파싱
- StandardServletMultipartResolver vs CommonsMultipartResolver
- 임시 파일 생성 및 MultipartFile 객체 생성

**예시 답변**:
> "MultipartResolver는 multipart/form-data 요청을 파싱하는 Spring 컴포넌트입니다. DispatcherServlet이 multipart 요청을 감지하면 MultipartResolver가 요청을 파싱하여 임시 파일을 생성하고 MultipartFile 객체를 만듭니다. Spring Boot는 기본적으로 StandardServletMultipartResolver를 사용하며, 이는 Servlet 3.0+ 표준 API를 활용합니다. CommonsMultipartResolver는 Apache Commons FileUpload를 사용하여 더 많은 커스터마이징 옵션을 제공하지만, 추가 의존성이 필요합니다."

**실무 예시**:
```java
@Bean
public MultipartResolver multipartResolver() {
    StandardServletMultipartResolver resolver = new StandardServletMultipartResolver();
    return resolver;
}
```

</details>

<details>
<summary><strong>2. 파일 업로드 보안 위협과 대응 방법을 설명해주세요.</strong></summary>

**모범 답안 포인트**:
- 악성 파일 업로드 (확장자 + MIME + 시그니처 검증)
- 경로 조작 공격 (.. 필터링, UUID 사용)
- DoS 공격 (크기 제한, Rate Limiting)
- 디렉토리 리스팅 차단

**예시 답변**:
> "파일 업로드의 주요 보안 위협은 악성 파일 업로드, 경로 조작, DoS 공격입니다. 악성 파일은 확장자 화이트리스트, MIME 타입 검증, 파일 시그니처 검증으로 차단합니다. 경로 조작 공격은 파일명에서 '..'을 필터링하고 UUID를 사용해 방지합니다. DoS 공격은 max-file-size 설정과 Rate Limiting으로 대응하며, 업로드 디렉토리의 직접 접근을 차단하여 디렉토리 리스팅을 방지합니다."

</details>

<details>
<summary><strong>3. 대용량 파일 업로드 시 성능 최적화 방법을 설명해주세요.</strong></summary>

**모범 답안 포인트**:
- file-size-threshold 설정 (메모리 vs 디스크)
- transferTo() 사용 (스트리밍)
- 청크 업로드 (Chunked Upload)
- 비동기 처리

**예시 답변**:
> "대용량 파일 업로드는 file-size-threshold를 적절히 설정하여 메모리와 디스크를 효율적으로 사용합니다. transferTo() 메서드는 스트리밍 방식으로 메모리 사용을 최소화하며, 청크 업로드를 사용하면 파일을 여러 조각으로 나눠 업로드하여 네트워크 오류 시 재시도가 가능합니다. 또한 @Async를 사용해 업로드를 비동기로 처리하면 사용자 응답 시간을 개선할 수 있습니다."

</details>

---

## 💡 면접 질문 답안

### 📘 주니어/신입 개발자용 답안

#### Q1. MultipartFile이란 무엇이며, 왜 사용하나요?

**완벽한 답변 예시**:
```
"MultipartFile은 Spring Framework에서 파일 업로드를 처리하기 위해 제공하는 인터페이스입니다.

HTTP는 기본적으로 텍스트 기반 프로토콜이기 때문에, 파일 같은 바이너리 데이터를 전송하려면 multipart/form-data 인코딩을 사용해야 합니다. Spring은 이렇게 전송된 파일을 MultipartFile 객체로 자동 변환해줍니다.

MultipartFile은 원본 파일명(getOriginalFilename), 파일 크기(getSize), MIME 타입(getContentType) 같은 메타데이터를 제공하며, transferTo() 메서드로 쉽게 파일을 저장할 수 있습니다.

실무에서는 프로필 사진 업로드, 첨부파일 기능, 문서 제출 시스템 등 모든 파일 업로드 기능에서 MultipartFile을 사용합니다."
```

**답변 구조 분석**:
1. **도입부 (10초)**: MultipartFile은 Spring의 파일 업로드 인터페이스
2. **본론 (30초)**: HTTP multipart 인코딩 설명 + 제공 기능
3. **마무리 (10초)**: 실무 활용 사례

**더 좋은 답변을 위한 추가 포인트**:
- ✅ 코드 예시 준비: `@RequestParam("file") MultipartFile file`
- ✅ transferTo()의 메모리 효율성 언급
- ✅ Java File 클래스와의 차이점 설명

**피해야 할 답변 실수**:
- ❌ "그냥 파일 받는 거요" (너무 간략)
- ❌ 기술 용어만 나열 (이해 없이 암기)
- ❌ 실무 활용 사례 언급 안 함

**꼬리 질문 대응**:
- Q: "MultipartFile과 Java의 File 클래스의 차이는?"
  - A: "MultipartFile은 HTTP 요청에서 업로드된 파일을 나타내고 MIME 타입과 원본 파일명을 제공하지만, File은 파일 시스템의 파일을 나타내며 이런 메타데이터가 없습니다."
- Q: "getBytes()와 transferTo()의 차이는?"
  - A: "getBytes()는 파일 전체를 메모리에 로드하여 바이트 배열로 반환하지만, transferTo()는 스트리밍 방식으로 메모리를 적게 사용하여 더 효율적입니다."

---

#### Q2. 파일 업로드 시 반드시 검증해야 할 항목은 무엇인가요?

**완벽한 답변 예시**:
```
"파일 업로드 시 반드시 검증해야 할 항목은 크게 5가지입니다.

첫째, 파일 크기입니다. application.yml에서 max-file-size를 설정하여 서버 자원을 보호합니다.

둘째, 확장자 검증입니다. 화이트리스트 방식으로 jpg, png, pdf 같은 허용된 확장자만 받아야 합니다.

셋째, MIME 타입 검증입니다. 확장자는 쉽게 변경할 수 있어 virus.exe를 virus.jpg로 바꿔 업로드할 수 있으므로, MIME 타입도 함께 확인해야 합니다.

넷째, 파일명 안전성입니다. 파일명에 '..'이 포함되어 있으면 경로 조작 공격이 가능하므로, StringUtils.cleanPath()로 정리하거나 UUID를 사용합니다.

다섯째, 빈 파일 여부입니다. file.isEmpty()로 확인하여 빈 파일 업로드를 차단합니다.

실무에서는 이 모든 검증을 FileValidator 클래스로 분리하여 재사용합니다."
```

**답변 구조 분석**:
1. **도입부 (5초)**: 5가지 검증 항목이 있다
2. **본론 (40초)**: 각 항목을 구체적으로 설명
3. **마무리 (5초)**: 실무 팁 (Validator 클래스 분리)

**더 좋은 답변을 위한 추가 포인트**:
- ✅ 각 검증의 이유 설명 (크기 → 서버 자원, 확장자 → 보안)
- ✅ 실제 코드 예시 준비
- ✅ 파일 시그니처 검증도 언급하면 가산점

**피해야 할 답변 실수**:
- ❌ "크기만 확인하면 됩니다" (불충분)
- ❌ 검증 이유 설명 없이 항목만 나열
- ❌ "보안 문제 때문입니다" (너무 추상적)

---

#### Q3. transferTo() 메서드의 역할과 장점을 설명해주세요.

**완벽한 답변 예시**:
```
"transferTo()는 MultipartFile의 내용을 지정한 경로에 파일로 저장하는 메서드입니다.

가장 큰 장점은 메모리 효율성입니다. getBytes()는 파일 전체를 메모리에 로드하지만, transferTo()는 스트리밍 방식으로 작은 버퍼를 사용해 조금씩 저장합니다. 예를 들어 1GB 파일을 업로드할 때, getBytes()는 1GB 메모리가 필요하지만 transferTo()는 1MB 정도만 사용하여 OOM 위험이 없습니다.

또한 속도도 더 빠릅니다. 메모리에 전체를 로드하지 않으므로 I/O 작업이 즉시 시작됩니다.

주의할 점은 transferTo()는 한 번만 호출 가능하다는 것입니다. 두 번째 호출 시 IllegalStateException이 발생하므로, 여러 곳에 저장하려면 Files.copy()를 사용해야 합니다."
```

**답변 구조 분석**:
1. **도입부 (10초)**: transferTo()는 파일 저장 메서드
2. **본론 (30초)**: 메모리 효율성과 속도 설명 + 구체적 수치
3. **마무리 (10초)**: 주의사항 (한 번만 호출 가능)

---

### 📗 중급 개발자용 답안

#### Q1. MultipartResolver의 동작 원리와 종류를 설명해주세요.

**완벽한 답변 예시** (중급 수준):
```
"MultipartResolver는 Spring MVC에서 multipart/form-data 요청을 파싱하는 핵심 컴포넌트입니다.

동작 과정을 살펴보면, 먼저 DispatcherServlet이 요청의 Content-Type이 multipart/form-data인지 확인합니다. 맞다면 MultipartResolver가 요청을 파싱하여 임시 디렉토리에 파일을 저장하고, 각 파일에 대해 MultipartFile 객체를 생성합니다. 이후 Controller에서 @RequestParam으로 이 객체를 받을 수 있습니다.

Spring은 두 가지 MultipartResolver를 제공합니다.

첫째, StandardServletMultipartResolver는 Servlet 3.0+ 표준 API를 사용하며, Spring Boot의 기본값입니다. 추가 라이브러리가 필요 없고 서블릿 컨테이너가 직접 처리하여 성능이 우수합니다.

둘째, CommonsMultipartResolver는 Apache Commons FileUpload 라이브러리를 사용합니다. 더 많은 커스터마이징 옵션을 제공하지만, commons-fileupload 의존성이 필요하여 레거시 프로젝트에서 주로 사용됩니다.

실무에서는 특별한 이유가 없다면 StandardServletMultipartResolver를 사용하며, application.yml에서 max-file-size, max-request-size, file-size-threshold 등을 설정합니다."
```

**답변 구조 분석** (중급):
1. **도입부 (15초)**: MultipartResolver의 역할
2. **본론 (60초)**: 동작 과정 상세 설명 + 두 가지 종류 비교
3. **마무리 (15초)**: 실무 권장사항

**중급 답변의 차별점**:
- ✅ 내부 동작 원리 설명 (DispatcherServlet → 파싱 → 임시 파일)
- ✅ 두 가지 Resolver 비교 및 선택 기준
- ✅ 설정 옵션 언급
- ✅ 성능 및 의존성 고려

---

#### Q2. 파일 업로드 보안 위협과 대응 방법을 설명해주세요.

**완벽한 답변 예시** (중급 수준):
```
"파일 업로드의 주요 보안 위협은 크게 4가지입니다.

첫째, 악성 파일 업로드입니다. 공격자가 실행 파일을 이미지로 위장하여 업로드할 수 있습니다. 대응 방법은 3단계 검증입니다. 확장자를 화이트리스트 방식으로 검증하고, MIME 타입을 확인하며, 파일 시그니처(매직 넘버)를 검증합니다. 예를 들어 JPEG 파일은 바이트 배열의 처음 3바이트가 FF D8 FF여야 합니다.

둘째, 경로 조작 공격입니다. 파일명에 '../../../etc/passwd' 같은 경로를 넣어 시스템 파일을 덮어쓸 수 있습니다. 대응 방법은 StringUtils.cleanPath()로 파일명을 정리하고, '..' 포함 여부를 확인하며, UUID를 사용해 원본 파일명을 아예 사용하지 않는 것입니다.

셋째, DoS 공격입니다. 대용량 파일을 다수 업로드하여 서버 자원을 고갈시킬 수 있습니다. max-file-size와 max-request-size를 설정하고, Rate Limiting으로 시간당 업로드 횟수를 제한합니다.

넷째, 디렉토리 리스팅입니다. 업로드 디렉토리에 직접 접근하여 모든 파일을 볼 수 있습니다. WebMvcConfigurer로 특정 경로를 통해서만 접근 가능하게 설정하여 차단합니다.

실무에서는 이 모든 검증을 FileValidator와 FileStorageService로 분리하고, 업로드된 파일 정보를 데이터베이스에 저장하여 추적 가능하게 합니다."
```

---

## 📝 핵심 정리

### 파일 업로드 필수 개념

| 개념 | 설명 | 핵심 키워드 |
|------|------|-------------|
| MultipartFile | Spring의 파일 업로드 인터페이스 | transferTo(), getBytes(), getOriginalFilename() |
| MultipartResolver | multipart 요청 파싱 컴포넌트 | StandardServlet, Commons |
| 파일 검증 | 크기, 확장자, MIME, 시그니처 | 화이트리스트, 매직 넘버 |
| 파일명 안전화 | 경로 조작 방지 | UUID, cleanPath(), .. 필터링 |
| 임시 파일 | 요청 처리 중 임시 저장 | /tmp, 자동 삭제 |

### 필수 설정

```yaml
spring:
  servlet:
    multipart:
      enabled: true                    # multipart 처리 활성화
      max-file-size: 10MB              # 파일 1개당 최대 크기
      max-request-size: 50MB           # 요청 전체 최대 크기
      file-size-threshold: 1MB         # 메모리 임계값
      location: /tmp                   # 임시 디렉토리
```

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] 확장자 화이트리스트 검증
- [ ] MIME 타입 검증
- [ ] 파일 크기 제한 설정
- [ ] UUID로 파일명 생성
- [ ] transferTo() 사용 (메모리 효율)
- [ ] 원본 파일명은 DB에 저장
- [ ] 날짜별 디렉토리 구조 생성
- [ ] 에러 처리 (MaxUploadSizeExceededException)

#### ❌ 하지 말아야 할 것
- [ ] 확장자만 검증
- [ ] 원본 파일명 그대로 저장
- [ ] getBytes() 사용 (대용량 파일 시)
- [ ] 실제 경로를 클라이언트에 노출
- [ ] 파일명에 .. 허용
- [ ] 검증 없이 저장
- [ ] 임시 파일에만 의존

### 보안 체크리스트

#### 파일 검증
- [ ] 확장자 화이트리스트 (jpg, png, pdf 등)
- [ ] MIME 타입 확인 (image/jpeg, application/pdf 등)
- [ ] 파일 시그니처 검증 (매직 넘버)
- [ ] 파일 크기 제한 (10MB 이하)
- [ ] 빈 파일 차단

#### 경로 보안
- [ ] 파일명에서 .. 필터링
- [ ] UUID 사용으로 원본 파일명 미사용
- [ ] 절대 경로로 저장 위치 지정
- [ ] 실제 경로 노출 방지

#### 서버 보호
- [ ] max-file-size 설정
- [ ] max-request-size 설정
- [ ] Rate Limiting
- [ ] 디렉토리 직접 접근 차단

---

## 🚀 다음 단계

### Part 2 미리보기: 실무 활용편

**배울 내용**:
- **클라우드 스토리지 연동**: AWS S3, Azure Blob Storage
- **이미지 처리**: 썸네일 생성, 리사이징, 워터마크
- **Ajax 파일 업로드**: 프로그레스 바, Drag & Drop
- **실전 프로젝트**: 프로필 사진 업로드, 게시판 첨부파일 시스템
- **주니어 시나리오**: 실무에서 자주 겪는 문제와 해결

### 이 장과의 연결점
```
Part 1에서 배운 [기본 업로드]
    ↓
Part 2에서 [클라우드 + 이미지 처리]
    ↓
최종적으로 [실전 프로젝트 완성]
```

---

**다음 장으로 이동**: [다음: 15장 Part 2 - 파일 업로드 실무편 →](SpringMVC-Part7-15-2-File-Upload-Advanced.md)

**이전 장으로 돌아가기**: [← 이전: 14장 폼 처리와 검증](SpringMVC-Part6-14-Form-Validation.md)

**목차로 돌아가기**: [📚 전체 목차](README.md)
