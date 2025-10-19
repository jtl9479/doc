# 16장: 예외 처리

> **학습 목표**: Spring MVC의 예외 처리 메커니즘을 이해하고, @ExceptionHandler, @ControllerAdvice를 활용하여 전역 예외 처리를 구현할 수 있습니다.

**⏱️ 예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐⭐☆ (4개/5개)

---

## 📚 목차
- [왜 예외 처리가 필요한가](#왜-예외-처리가-필요한가)
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

## 🤔 왜 예외 처리가 필요한가?

### 실무 배경

**웹 애플리케이션에서 발생하는 다양한 에러 상황**:
- 존재하지 않는 리소스 요청 (404 Not Found)
- 권한 없는 접근 (403 Forbidden)
- 잘못된 요청 데이터 (400 Bad Request)
- 서버 내부 에러 (500 Internal Server Error)
- 데이터베이스 연결 실패
- 외부 API 호출 실패

### ❌ 예외 처리를 하지 않으면 발생하는 문제

```
문제 1: 사용자에게 기술적 에러 노출
- 증상: 스택 트레이스가 그대로 화면에 표시
- 영향: 사용자 혼란, 보안 정보 노출
- 비용: 고객 이탈, 보안 위협

문제 2: 일관성 없는 에러 응답
- 증상: 에러마다 다른 형식의 응답
- 영향: 클라이언트가 에러 처리 어려움
- 비용: 프론트엔드 개발 시간 증가

문제 3: 에러 추적 불가
- 증상: 어떤 에러가 얼마나 발생하는지 모름
- 영향: 문제 원인 파악 불가
- 비용: 장애 대응 시간 증가

문제 4: 중복된 예외 처리 코드
- 증상: 모든 Controller에 try-catch
- 영향: 코드 중복, 유지보수 어려움
- 비용: 개발 시간 증가
```

### ✅ Spring의 예외 처리를 올바르게 사용하면

```
해결책 1: 사용자 친화적인 에러 메시지
- 방법: @ExceptionHandler로 에러 가공
- 효과: 이해하기 쉬운 메시지 제공
- 절감: 고객 문의 70% 감소

해결책 2: 일관된 에러 응답 형식
- 방법: @ControllerAdvice로 전역 처리
- 효과: 통일된 JSON 에러 응답
- 절감: 프론트엔드 개발 시간 50% 단축

해결책 3: 에러 로깅 및 모니터링
- 방법: 예외 처리 시 자동 로깅
- 효과: 실시간 에러 추적
- 절감: 장애 대응 시간 80% 단축

해결책 4: 코드 중복 제거
- 방법: 중앙 집중식 예외 처리
- 효과: Controller 코드 간결화
- 절감: 유지보수 비용 60% 절감
```

### 📊 수치로 보는 효과

| 지표 | Before | After | 개선율 |
|------|--------|-------|--------|
| 고객 문의 (에러 관련) | 100건/일 | 30건/일 | **70%↓** |
| 에러 응답 코드 라인 수 | 50줄 | 5줄 | **90%↓** |
| 장애 원인 파악 시간 | 4시간 | 30분 | **87%↓** |
| 보안 취약점 | 3개 | 0개 | **100%↓** |

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 병원 응급실

**상황**: 환자가 응급실에 왔을 때

```
┌─────────────┬─────────────────────┬──────────────────┐
│ 병원        │ Exception Handling  │ 역할             │
├─────────────┼─────────────────────┼──────────────────┤
│ 환자        │ Exception           │ 발생한 에러      │
│ 증상        │ Exception 종류      │ 에러 타입        │
│ 접수        │ @ExceptionHandler   │ 에러 받기        │
│ 트리아지    │ Exception 분류      │ 심각도 판단      │
│ 진료과 배정 │ 적절한 Handler      │ 처리 방법 선택   │
│ 처방전      │ 에러 응답           │ 사용자에게 전달  │
└─────────────┴─────────────────────┴──────────────────┘
```

**흐름**:
1. **환자 도착**: 에러 발생 (NullPointerException)
2. **접수**: @ExceptionHandler가 에러 받음
3. **트리아지**: 에러 심각도 판단 (경증/중증)
4. **진료과 배정**:
   - NullPointerException → 일반 진료 (400 Bad Request)
   - OutOfMemoryError → 중환자실 (500 Server Error)
5. **처방전 발급**: 에러 응답 JSON
6. **환자 귀가**: 사용자에게 에러 메시지 표시

**코드로 보면**:
```java
@ControllerAdvice  // 응급실
public class GlobalExceptionHandler {

    // 일반 진료 (경증)
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorResponse> handleIllegalArgument(IllegalArgumentException e) {
        // 처방전 발급
        return ResponseEntity
            .status(HttpStatus.BAD_REQUEST)
            .body(new ErrorResponse("잘못된 요청입니다: " + e.getMessage()));
    }

    // 중환자실 (중증)
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneral(Exception e) {
        // 입원 처치
        logger.error("심각한 에러 발생", e);
        return ResponseEntity
            .status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(new ErrorResponse("서버 에러가 발생했습니다"));
    }
}
```

---

### 비유 2: 콜센터 상담사

**상황**: 고객이 문제를 전화로 문의

```
┌──────────────┬─────────────────────┬──────────────────┐
│ 콜센터       │ Exception Handling  │ 역할             │
├──────────────┼─────────────────────┼──────────────────┤
│ 고객 문의    │ Exception           │ 에러 발생        │
│ ARS 분기     │ Exception 타입      │ 에러 분류        │
│ 상담사       │ @ExceptionHandler   │ 에러 처리        │
│ 매뉴얼       │ Handler 로직        │ 처리 방법        │
│ 응대 멘트    │ 에러 메시지         │ 사용자 응답      │
│ 상담 기록    │ 로그                │ 추적             │
└──────────────┴─────────────────────┴──────────────────┘
```

**시나리오**:
```
고객: "상품을 찾을 수 없다고 나와요!"
  ↓
ARS: "상품 관련 문의는 1번을 눌러주세요"
  ↓ (ProductNotFoundException 감지)
상담사: "고객님, 찾으시는 상품이 품절되었습니다. 비슷한 상품을 추천해드릴까요?"
  ↓
고객: "네, 부탁드려요"
  ↓
상담 기록: [2024-01-15 14:30] 상품 품절 문의 → 대체 상품 안내
```

**코드로 보면**:
```java
@ControllerAdvice  // 콜센터
public class CustomerServiceExceptionHandler {

    // 상품 찾을 수 없음 (1번)
    @ExceptionHandler(ProductNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleProductNotFound(ProductNotFoundException e) {
        // 매뉴얼에 따라 응대
        ErrorResponse response = ErrorResponse.builder()
            .message("죄송합니다. 해당 상품을 찾을 수 없습니다")
            .suggestion("비슷한 상품을 추천해드리겠습니다")
            .recommendedProducts(productService.findSimilar(e.getProductId()))
            .build();

        // 상담 기록
        logger.info("상품 없음: {}", e.getProductId());

        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(response);
    }

    // 결제 실패 (2번)
    @ExceptionHandler(PaymentFailedException.class)
    public ResponseEntity<ErrorResponse> handlePaymentFailed(PaymentFailedException e) {
        return ResponseEntity
            .status(HttpStatus.PAYMENT_REQUIRED)
            .body(new ErrorResponse("결제가 실패했습니다. 카드를 확인해주세요"));
    }
}
```

---

### 비유 3: 교통 관제센터

**상황**: 도로에서 사고 발생 시 관제

```
┌──────────────┬─────────────────────┬──────────────────┐
│ 교통 관제    │ Exception Handling  │ 역할             │
├──────────────┼─────────────────────┼──────────────────┤
│ 사고         │ Exception           │ 에러 발생        │
│ CCTV         │ Exception 감지      │ 에러 탐지        │
│ 관제사       │ @ExceptionHandler   │ 에러 처리자      │
│ 경중 판단    │ HTTP 상태 코드      │ 심각도           │
│ 우회 안내    │ 에러 응답           │ 대응 방법        │
│ 사고 기록    │ 로그                │ 추적             │
└──────────────┴─────────────────────┴──────────────────┘
```

**예시**:
```
경미한 접촉 사고 (IllegalArgumentException)
  ↓
관제센터: CCTV로 감지
  ↓
관제사: "경미한 사고입니다. 차량 이동 가능합니다"
  ↓
우회 안내: "잠시 서행해주세요"
  ↓
기록: [14:30] 1번 차로 접촉 사고 → 5분 후 정상화

vs

대형 사고 (OutOfMemoryError)
  ↓
관제센터: 긴급 상황 감지
  ↓
관제사: "도로 전면 통제! 119 출동!"
  ↓
우회 안내: "모든 차량 우회로 이용 바랍니다"
  ↓
기록: [14:30] 1번 차로 대형 사고 → 2시간 통제
```

**코드로 보면**:
```java
@ControllerAdvice
public class TrafficControlExceptionHandler {

    // 경미한 사고
    @ExceptionHandler(IllegalArgumentException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleMinorAccident(IllegalArgumentException e) {
        // 사고 기록
        logger.warn("경미한 사고: {}", e.getMessage());

        // 우회 안내
        return ErrorResponse.builder()
            .code("MINOR_ACCIDENT")
            .message("잠시 서행해주세요")
            .severity("LOW")
            .build();
    }

    // 대형 사고
    @ExceptionHandler(OutOfMemoryError.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ErrorResponse handleMajorAccident(OutOfMemoryError e) {
        // 긴급 기록
        logger.error("대형 사고 발생!", e);

        // 긴급 알림
        alertService.sendEmergencyAlert("OutOfMemoryError 발생");

        // 전면 통제
        return ErrorResponse.builder()
            .code("MAJOR_ACCIDENT")
            .message("서비스 점검 중입니다")
            .severity("CRITICAL")
            .estimatedRecovery("2시간")
            .build();
    }
}
```

---

### 비유 4: 레스토랑 주방

**상황**: 주방에서 문제 발생 시 대응

```
┌──────────────┬─────────────────────┬──────────────────┐
│ 레스토랑     │ Exception Handling  │ 역할             │
├──────────────┼─────────────────────┼──────────────────┤
│ 주문 실수    │ Exception           │ 에러             │
│ 메뉴판 확인  │ Exception 타입      │ 에러 종류        │
│ 홀 매니저    │ @ControllerAdvice   │ 전역 처리        │
│ 웨이터       │ @ExceptionHandler   │ 개별 처리        │
│ 사과 멘트    │ 에러 메시지         │ 응답             │
│ 쿠폰 발급    │ 보상 로직           │ 복구             │
└──────────────┴─────────────────────┴──────────────────┘
```

**시나리오**:
```java
@ControllerAdvice  // 홀 매니저
public class RestaurantExceptionHandler {

    // 품절 (ProductOutOfStockException)
    @ExceptionHandler(ProductOutOfStockException.class)
    public ResponseEntity<ErrorResponse> handleOutOfStock(ProductOutOfStockException e) {
        // 사과 멘트
        String apology = "죄송합니다. " + e.getProductName() + "이(가) 품절되었습니다";

        // 대체 메뉴 제안
        List<String> alternatives = menuService.findAlternatives(e.getProductId());

        ErrorResponse response = ErrorResponse.builder()
            .message(apology)
            .alternatives(alternatives)
            .coupon("10% 할인 쿠폰")  // 보상
            .build();

        return ResponseEntity.status(HttpStatus.CONFLICT).body(response);
    }

    // 조리 시간 초과 (TimeoutException)
    @ExceptionHandler(TimeoutException.class)
    public ResponseEntity<ErrorResponse> handleTimeout(TimeoutException e) {
        // 정중한 사과
        ErrorResponse response = ErrorResponse.builder()
            .message("주문이 지연되고 있습니다. 잠시만 기다려주세요")
            .estimatedTime("5분")
            .compensation("음료 서비스")
            .build();

        return ResponseEntity.status(HttpStatus.REQUEST_TIMEOUT).body(response);
    }
}
```

---

### 비유 5: 우체국 택배 배송

**상황**: 택배 배송 중 문제 발생

```
┌──────────────┬─────────────────────┬──────────────────┐
│ 택배         │ Exception Handling  │ 역할             │
├──────────────┼─────────────────────┼──────────────────┤
│ 배송 실패    │ Exception           │ 에러             │
│ 실패 사유    │ Exception 타입      │ 에러 타입        │
│ 고객센터     │ @ControllerAdvice   │ 전역 처리        │
│ 배송 기사    │ @ExceptionHandler   │ 개별 처리        │
│ 안내 문자    │ 에러 메시지         │ 응답             │
│ 재배송       │ 복구 로직           │ 재시도           │
└──────────────┴─────────────────────┴──────────────────┘
```

**예시**:
```java
@ControllerAdvice
public class DeliveryExceptionHandler {

    // 주소 오류
    @ExceptionHandler(AddressNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleAddressNotFound(AddressNotFoundException e) {
        // 안내 문자
        String message = "배송지 주소를 찾을 수 없습니다. 주소를 확인해주세요";

        // 고객에게 연락 요청
        notificationService.sendSMS(e.getCustomerId(), message);

        ErrorResponse response = ErrorResponse.builder()
            .code("ADDRESS_NOT_FOUND")
            .message(message)
            .action("주소 재확인 요청")
            .contactNumber("1588-1234")
            .build();

        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(response);
    }

    // 배송 지연
    @ExceptionHandler(DeliveryDelayException.class)
    public ResponseEntity<ErrorResponse> handleDeliveryDelay(DeliveryDelayException e) {
        ErrorResponse response = ErrorResponse.builder()
            .code("DELIVERY_DELAYED")
            .message("배송이 지연되고 있습니다")
            .reason(e.getReason())  // 교통 체증, 기상 악화 등
            .newEstimatedTime(e.getNewETA())
            .compensation("무료 배송권")
            .build();

        return ResponseEntity.status(HttpStatus.OK).body(response);
    }
}
```

---

### 🔄 종합 비교표

```
┌─────────────┬──────────────┬──────────────┬──────────────┐
│ 비유        │ Exception    │ Handler      │ 응답         │
├─────────────┼──────────────┼──────────────┼──────────────┤
│ 병원        │ 환자         │ 트리아지     │ 처방전       │
│ 콜센터      │ 고객 문의    │ 상담사       │ 응대 멘트    │
│ 교통 관제   │ 사고         │ 관제사       │ 우회 안내    │
│ 레스토랑    │ 주문 실수    │ 홀 매니저    │ 사과 멘트    │
│ 택배        │ 배송 실패    │ 고객센터     │ 안내 문자    │
└─────────────┴──────────────┴──────────────┴──────────────┘
```

**핵심 인사이트**:
1. **예외는 문제 상황**: 병원의 환자처럼 처리가 필요
2. **Handler는 전문가**: 상담사처럼 적절히 대응
3. **응답은 안내**: 사용자에게 친절한 설명
4. **로그는 기록**: 추후 분석을 위한 기록

---

## 📖 핵심 개념

### 1️⃣ 초보자 수준 설명

**예외 처리란?**

프로그램 실행 중 발생하는 에러를 잡아서 적절히 처리하는 것입니다.

**간단한 예시**:
```java
// ❌ 예외 처리 없음
@GetMapping("/users/{id}")
public User getUser(@PathVariable Long id) {
    User user = userService.findById(id);  // id가 없으면 Exception!
    return user;
}

// ✅ 예외 처리 있음
@GetMapping("/users/{id}")
public ResponseEntity<User> getUser(@PathVariable Long id) {
    try {
        User user = userService.findById(id);
        return ResponseEntity.ok(user);
    } catch (UserNotFoundException e) {
        return ResponseEntity.notFound().build();
    }
}
```

**Spring의 예외 처리 방법**:
1. **@ExceptionHandler**: Controller 내에서 처리
2. **@ControllerAdvice**: 모든 Controller에서 처리
3. **ResponseEntityExceptionHandler**: Spring이 제공하는 기본 처리

---

### 2️⃣ 중급자 수준 설명

**Spring MVC의 예외 처리 흐름**

```
1. Controller 메서드 실행
   ↓
2. Exception 발생
   ↓
3. Spring이 Exception을 잡음
   ↓
4. @ExceptionHandler 찾기 (같은 Controller)
   ↓
5. 없으면 @ControllerAdvice 찾기 (전역)
   ↓
6. 그래도 없으면 DefaultHandlerExceptionResolver
   ↓
7. 최종적으로 Servlet Container의 에러 페이지
```

**@ExceptionHandler 동작 원리**:

```java
@Controller
public class UserController {

    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);  // UserNotFoundException 발생 가능
    }

    // ✅ 같은 Controller 내에서 처리
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        ErrorResponse error = new ErrorResponse("사용자를 찾을 수 없습니다");
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
}
```

**@ControllerAdvice의 장점**:

```java
// ✅ 모든 Controller에 적용
@ControllerAdvice
public class GlobalExceptionHandler {

    // 모든 Controller에서 UserNotFoundException 발생 시 처리
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        return ResponseEntity
            .status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse(e.getMessage()));
    }

    // 모든 Controller에서 IllegalArgumentException 발생 시 처리
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorResponse> handleIllegalArgument(IllegalArgumentException e) {
        return ResponseEntity
            .status(HttpStatus.BAD_REQUEST)
            .body(new ErrorResponse(e.getMessage()));
    }
}
```

**HTTP 상태 코드 매핑**:

| Exception | HTTP 상태 코드 | 의미 |
|-----------|---------------|------|
| IllegalArgumentException | 400 Bad Request | 잘못된 요청 |
| UnauthorizedException | 401 Unauthorized | 인증 필요 |
| ForbiddenException | 403 Forbidden | 권한 없음 |
| NotFoundException | 404 Not Found | 리소스 없음 |
| ConflictException | 409 Conflict | 충돌 (중복 등) |
| Exception | 500 Internal Server Error | 서버 에러 |

---

### 3️⃣ 고급자 수준 설명

**ExceptionHandler 우선순위**

```java
@Controller
public class UserController {

    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) {
        throw new UserNotFoundException(id);
    }

    // 1순위: 구체적인 타입 (UserNotFoundException)
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("사용자 없음: " + e.getUserId()));
    }
}

@ControllerAdvice
public class GlobalExceptionHandler {

    // 2순위: 상위 타입 (RuntimeException)
    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<ErrorResponse> handleRuntimeException(RuntimeException e) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(new ErrorResponse("런타임 에러"));
    }

    // 3순위: 최상위 타입 (Exception)
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleException(Exception e) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(new ErrorResponse("서버 에러"));
    }
}
```

**우선순위 규칙**:
1. **Controller의 @ExceptionHandler** > @ControllerAdvice의 @ExceptionHandler
2. **구체적인 타입** > 상위 타입
3. **먼저 선언된 Handler** > 나중에 선언된 Handler

**ResponseEntityExceptionHandler 상속**:

```java
@ControllerAdvice
public class CustomExceptionHandler extends ResponseEntityExceptionHandler {

    // Spring이 제공하는 기본 예외 처리를 오버라이드
    @Override
    protected ResponseEntity<Object> handleMethodArgumentNotValid(
        MethodArgumentNotValidException ex,
        HttpHeaders headers,
        HttpStatusCode status,
        WebRequest request
    ) {
        // Validation 에러를 커스터마이징
        List<String> errors = ex.getBindingResult()
            .getFieldErrors()
            .stream()
            .map(error -> error.getField() + ": " + error.getDefaultMessage())
            .collect(Collectors.toList());

        ErrorResponse errorResponse = ErrorResponse.builder()
            .code("VALIDATION_ERROR")
            .message("입력값이 올바르지 않습니다")
            .errors(errors)
            .build();

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errorResponse);
    }

    // HTTP 메서드 불일치 (GET 요청을 POST로 보냄)
    @Override
    protected ResponseEntity<Object> handleHttpRequestMethodNotSupported(
        HttpRequestMethodNotSupportedException ex,
        HttpHeaders headers,
        HttpStatusCode status,
        WebRequest request
    ) {
        ErrorResponse errorResponse = ErrorResponse.builder()
            .code("METHOD_NOT_ALLOWED")
            .message(ex.getMethod() + " 메서드는 지원하지 않습니다")
            .supportedMethods(ex.getSupportedHttpMethods())
            .build();

        return ResponseEntity.status(HttpStatus.METHOD_NOT_ALLOWED).body(errorResponse);
    }
}
```

**커스텀 Exception 계층 구조**:

```java
// 최상위 비즈니스 예외
public abstract class BusinessException extends RuntimeException {
    private final ErrorCode errorCode;

    public BusinessException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
    }

    public ErrorCode getErrorCode() {
        return errorCode;
    }
}

// 리소스 관련 예외
public class ResourceNotFoundException extends BusinessException {
    public ResourceNotFoundException(Long id) {
        super(ErrorCode.RESOURCE_NOT_FOUND);
    }
}

// 인증 관련 예외
public class AuthenticationException extends BusinessException {
    public AuthenticationException() {
        super(ErrorCode.UNAUTHORIZED);
    }
}

// 권한 관련 예외
public class AuthorizationException extends BusinessException {
    public AuthorizationException() {
        super(ErrorCode.FORBIDDEN);
    }
}

// 에러 코드 enum
public enum ErrorCode {
    // 400
    INVALID_INPUT("C001", "입력값이 올바르지 않습니다", HttpStatus.BAD_REQUEST),

    // 401
    UNAUTHORIZED("C002", "인증이 필요합니다", HttpStatus.UNAUTHORIZED),

    // 403
    FORBIDDEN("C003", "권한이 없습니다", HttpStatus.FORBIDDEN),

    // 404
    RESOURCE_NOT_FOUND("C004", "리소스를 찾을 수 없습니다", HttpStatus.NOT_FOUND),

    // 409
    DUPLICATE_RESOURCE("C005", "이미 존재하는 리소스입니다", HttpStatus.CONFLICT),

    // 500
    INTERNAL_SERVER_ERROR("C999", "서버 에러가 발생했습니다", HttpStatus.INTERNAL_SERVER_ERROR);

    private final String code;
    private final String message;
    private final HttpStatus httpStatus;

    ErrorCode(String code, String message, HttpStatus httpStatus) {
        this.code = code;
        this.message = message;
        this.httpStatus = httpStatus;
    }

    // Getters
    public String getCode() { return code; }
    public String getMessage() { return message; }
    public HttpStatus getHttpStatus() { return httpStatus; }
}
```

**통일된 에러 응답 형식**:

```java
@Getter
@Builder
public class ErrorResponse {
    private final String code;           // 에러 코드 (C001, C002 등)
    private final String message;        // 사용자 메시지
    private final List<FieldError> errors;  // 필드 에러 (Validation)
    private final LocalDateTime timestamp;

    @Getter
    @Builder
    public static class FieldError {
        private final String field;
        private final String message;
        private final Object rejectedValue;
    }
}

// 사용 예시
@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusinessException(BusinessException e) {
        ErrorCode errorCode = e.getErrorCode();

        ErrorResponse response = ErrorResponse.builder()
            .code(errorCode.getCode())
            .message(errorCode.getMessage())
            .timestamp(LocalDateTime.now())
            .build();

        return ResponseEntity
            .status(errorCode.getHttpStatus())
            .body(response);
    }
}
```

**JSON 응답 예시**:
```json
{
  "code": "C004",
  "message": "리소스를 찾을 수 없습니다",
  "timestamp": "2024-01-15T14:30:00"
}
```

---

## 💻 기본 실습

### 실습 1: 기본 예외 처리

**난이도**: ⭐⭐☆☆☆

#### CustomException

```java
package com.example.exception;

public class UserNotFoundException extends RuntimeException {
    private final Long userId;

    public UserNotFoundException(Long userId) {
        super("사용자를 찾을 수 없습니다: " + userId);
        this.userId = userId;
    }

    public Long getUserId() {
        return userId;
    }
}
```

#### Controller

```java
package com.example.controller;

import com.example.entity.User;
import com.example.exception.UserNotFoundException;
import com.example.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        User user = userService.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));

        return ResponseEntity.ok(user);
    }

    // ✅ Controller 내에서 예외 처리
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        ErrorResponse error = new ErrorResponse(
            "USER_NOT_FOUND",
            e.getMessage()
        );

        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
}
```

#### ErrorResponse

```java
package com.example.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class ErrorResponse {
    private String code;
    private String message;
}
```

#### 테스트

```bash
# 존재하는 사용자
curl http://localhost:8080/api/users/1
# Response: {"id":1,"name":"John","email":"john@example.com"}

# 존재하지 않는 사용자
curl http://localhost:8080/api/users/999
# Response: {"code":"USER_NOT_FOUND","message":"사용자를 찾을 수 없습니다: 999"}
# Status: 404 Not Found
```

---

### 실습 2: @ControllerAdvice로 전역 예외 처리

**난이도**: ⭐⭐⭐☆☆

#### GlobalExceptionHandler

```java
package com.example.exception.handler;

import com.example.dto.ErrorResponse;
import com.example.exception.UserNotFoundException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;

import java.time.LocalDateTime;

@Slf4j
@ControllerAdvice
public class GlobalExceptionHandler {

    /**
     * UserNotFoundException 처리
     */
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        log.warn("사용자를 찾을 수 없음: {}", e.getUserId());

        ErrorResponse error = ErrorResponse.builder()
            .code("USER_NOT_FOUND")
            .message(e.getMessage())
            .timestamp(LocalDateTime.now())
            .build();

        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }

    /**
     * IllegalArgumentException 처리
     */
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorResponse> handleIllegalArgument(IllegalArgumentException e) {
        log.warn("잘못된 인자: {}", e.getMessage());

        ErrorResponse error = ErrorResponse.builder()
            .code("INVALID_ARGUMENT")
            .message("잘못된 요청입니다: " + e.getMessage())
            .timestamp(LocalDateTime.now())
            .build();

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
    }

    /**
     * 모든 예외 처리 (Fallback)
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneral(Exception e) {
        log.error("예상치 못한 에러 발생", e);

        ErrorResponse error = ErrorResponse.builder()
            .code("INTERNAL_SERVER_ERROR")
            .message("서버 에러가 발생했습니다")
            .timestamp(LocalDateTime.now())
            .build();

        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
}
```

#### Controller (예외 처리 코드 제거)

```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        // ✅ Exception 발생 시 GlobalExceptionHandler가 처리
        User user = userService.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));

        return ResponseEntity.ok(user);
    }

    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody UserRequest request) {
        // ✅ IllegalArgumentException 발생 시 GlobalExceptionHandler가 처리
        if (request.getName() == null || request.getName().isEmpty()) {
            throw new IllegalArgumentException("이름은 필수입니다");
        }

        User user = userService.create(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(user);
    }
}
```

---

### 실습 3: Validation 에러 처리

**난이도**: ⭐⭐⭐☆☆

#### 의존성 추가

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

#### DTO with Validation

```java
package com.example.dto;

import jakarta.validation.constraints.*;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class UserRequest {

    @NotBlank(message = "이름은 필수입니다")
    @Size(min = 2, max = 20, message = "이름은 2~20자여야 합니다")
    private String name;

    @NotBlank(message = "이메일은 필수입니다")
    @Email(message = "올바른 이메일 형식이 아닙니다")
    private String email;

    @NotNull(message = "나이는 필수입니다")
    @Min(value = 18, message = "18세 이상이어야 합니다")
    @Max(value = 100, message = "100세 이하여야 합니다")
    private Integer age;
}
```

#### Controller

```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @PostMapping
    public ResponseEntity<User> createUser(@Valid @RequestBody UserRequest request) {
        // @Valid가 UserRequest 검증 → 실패 시 MethodArgumentNotValidException 발생
        User user = userService.create(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(user);
    }
}
```

#### GlobalExceptionHandler

```java
@ControllerAdvice
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {

    /**
     * Validation 에러 처리
     */
    @Override
    protected ResponseEntity<Object> handleMethodArgumentNotValid(
        MethodArgumentNotValidException ex,
        HttpHeaders headers,
        HttpStatusCode status,
        WebRequest request
    ) {
        // 필드 에러 추출
        List<ErrorResponse.FieldError> fieldErrors = ex.getBindingResult()
            .getFieldErrors()
            .stream()
            .map(error -> ErrorResponse.FieldError.builder()
                .field(error.getField())
                .message(error.getDefaultMessage())
                .rejectedValue(error.getRejectedValue())
                .build())
            .collect(Collectors.toList());

        ErrorResponse errorResponse = ErrorResponse.builder()
            .code("VALIDATION_ERROR")
            .message("입력값이 올바르지 않습니다")
            .errors(fieldErrors)
            .timestamp(LocalDateTime.now())
            .build();

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errorResponse);
    }
}
```

#### 테스트

```bash
# 잘못된 요청
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "A",
    "email": "invalid",
    "age": 15
  }'

# Response:
{
  "code": "VALIDATION_ERROR",
  "message": "입력값이 올바르지 않습니다",
  "errors": [
    {
      "field": "name",
      "message": "이름은 2~20자여야 합니다",
      "rejectedValue": "A"
    },
    {
      "field": "email",
      "message": "올바른 이메일 형식이 아닙니다",
      "rejectedValue": "invalid"
    },
    {
      "field": "age",
      "message": "18세 이상이어야 합니다",
      "rejectedValue": 15
    }
  ],
  "timestamp": "2024-01-15T14:30:00"
}
```

---

## 🏢 실무 활용 사례

### 사례 1: 토스 - 결제 시스템 예외 처리

**배경**: 결제 과정에서 다양한 에러 발생 (카드 한도, 잔액 부족, 통신 오류)

**요구사항**:
- 에러 종류별로 다른 처리
- 사용자에게 명확한 안내
- 재시도 가능 여부 표시
- 고객센터 연결

**구현**:

#### Custom Exceptions

```java
// 결제 관련 최상위 예외
public abstract class PaymentException extends RuntimeException {
    private final PaymentErrorCode errorCode;
    private final boolean retryable;  // 재시도 가능 여부

    public PaymentException(PaymentErrorCode errorCode, boolean retryable) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
        this.retryable = retryable;
    }

    public PaymentErrorCode getErrorCode() {
        return errorCode;
    }

    public boolean isRetryable() {
        return retryable;
    }
}

// 카드 한도 초과
public class CardLimitExceededException extends PaymentException {
    private final long requestedAmount;
    private final long availableLimit;

    public CardLimitExceededException(long requestedAmount, long availableLimit) {
        super(PaymentErrorCode.CARD_LIMIT_EXCEEDED, false);  // 재시도 불가
        this.requestedAmount = requestedAmount;
        this.availableLimit = availableLimit;
    }

    public long getRequestedAmount() {
        return requestedAmount;
    }

    public long getAvailableLimit() {
        return availableLimit;
    }
}

// 잔액 부족
public class InsufficientBalanceException extends PaymentException {
    private final long balance;
    private final long required;

    public InsufficientBalanceException(long balance, long required) {
        super(PaymentErrorCode.INSUFFICIENT_BALANCE, false);
        this.balance = balance;
        this.required = required;
    }

    public long getBalance() {
        return balance;
    }

    public long getRequired() {
        return required;
    }
}

// 통신 오류
public class PaymentNetworkException extends PaymentException {
    public PaymentNetworkException() {
        super(PaymentErrorCode.NETWORK_ERROR, true);  // 재시도 가능
    }
}
```

#### Error Code Enum

```java
public enum PaymentErrorCode {
    CARD_LIMIT_EXCEEDED("P001", "카드 한도를 초과했습니다", HttpStatus.PAYMENT_REQUIRED),
    INSUFFICIENT_BALANCE("P002", "잔액이 부족합니다", HttpStatus.PAYMENT_REQUIRED),
    NETWORK_ERROR("P003", "통신 오류가 발생했습니다", HttpStatus.SERVICE_UNAVAILABLE),
    INVALID_CARD("P004", "유효하지 않은 카드입니다", HttpStatus.BAD_REQUEST),
    CARD_EXPIRED("P005", "카드가 만료되었습니다", HttpStatus.BAD_REQUEST);

    private final String code;
    private final String message;
    private final HttpStatus httpStatus;

    PaymentErrorCode(String code, String message, HttpStatus httpStatus) {
        this.code = code;
        this.message = message;
        this.httpStatus = httpStatus;
    }

    public String getCode() { return code; }
    public String getMessage() { return message; }
    public HttpStatus getHttpStatus() { return httpStatus; }
}
```

#### PaymentExceptionHandler

```java
@RestControllerAdvice
@Slf4j
public class PaymentExceptionHandler {

    @Autowired
    private CustomerService customerService;

    /**
     * 카드 한도 초과
     */
    @ExceptionHandler(CardLimitExceededException.class)
    public ResponseEntity<PaymentErrorResponse> handleCardLimitExceeded(
        CardLimitExceededException e
    ) {
        log.warn("카드 한도 초과: 요청 {}, 한도 {}", e.getRequestedAmount(), e.getAvailableLimit());

        PaymentErrorResponse response = PaymentErrorResponse.builder()
            .code(e.getErrorCode().getCode())
            .message("카드 한도를 초과했습니다")
            .detail(String.format("요청 금액: %,d원, 사용 가능 한도: %,d원",
                e.getRequestedAmount(), e.getAvailableLimit()))
            .retryable(false)
            .suggestions(Arrays.asList(
                "다른 카드를 사용해주세요",
                "한도를 늘려주세요"
            ))
            .contactNumber("1599-4905")
            .build();

        return ResponseEntity.status(HttpStatus.PAYMENT_REQUIRED).body(response);
    }

    /**
     * 잔액 부족
     */
    @ExceptionHandler(InsufficientBalanceException.class)
    public ResponseEntity<PaymentErrorResponse> handleInsufficientBalance(
        InsufficientBalanceException e
    ) {
        log.warn("잔액 부족: 잔액 {}, 필요 {}", e.getBalance(), e.getRequired());

        PaymentErrorResponse response = PaymentErrorResponse.builder()
            .code(e.getErrorCode().getCode())
            .message("잔액이 부족합니다")
            .detail(String.format("현재 잔액: %,d원, 필요 금액: %,d원",
                e.getBalance(), e.getRequired()))
            .retryable(false)
            .suggestions(Arrays.asList(
                "충전 후 다시 시도해주세요",
                "다른 결제 수단을 이용해주세요"
            ))
            .build();

        return ResponseEntity.status(HttpStatus.PAYMENT_REQUIRED).body(response);
    }

    /**
     * 통신 오류 (재시도 가능)
     */
    @ExceptionHandler(PaymentNetworkException.class)
    public ResponseEntity<PaymentErrorResponse> handleNetworkError(
        PaymentNetworkException e
    ) {
        log.error("결제 통신 오류", e);

        PaymentErrorResponse response = PaymentErrorResponse.builder()
            .code(e.getErrorCode().getCode())
            .message("일시적인 통신 오류가 발생했습니다")
            .detail("잠시 후 다시 시도해주세요")
            .retryable(true)  // ✅ 재시도 가능
            .retryAfter(3)  // 3초 후 재시도
            .suggestions(Arrays.asList(
                "잠시 후 다시 시도해주세요",
                "인터넷 연결을 확인해주세요"
            ))
            .build();

        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(response);
    }
}
```

#### Response DTO

```java
@Getter
@Builder
public class PaymentErrorResponse {
    private String code;              // 에러 코드 (P001, P002 등)
    private String message;           // 사용자 메시지
    private String detail;            // 상세 정보
    private boolean retryable;        // 재시도 가능 여부
    private Integer retryAfter;       // 재시도 권장 시간 (초)
    private List<String> suggestions; // 해결 방법 제안
    private String contactNumber;     // 고객센터 번호
    private LocalDateTime timestamp;

    public static class PaymentErrorResponseBuilder {
        private LocalDateTime timestamp = LocalDateTime.now();
    }
}
```

#### 프론트엔드 처리

```javascript
async function processPayment() {
    try {
        const response = await fetch('/api/payments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(paymentData)
        });

        if (!response.ok) {
            const error = await response.json();

            // 재시도 가능한 에러
            if (error.retryable) {
                showRetryButton(error.retryAfter);
                showMessage(error.message + ' (재시도 가능)');
            } else {
                // 재시도 불가능한 에러
                showSuggestions(error.suggestions);
                if (error.contactNumber) {
                    showContactButton(error.contactNumber);
                }
                showMessage(error.message);
            }
        }
    } catch (error) {
        showMessage('결제 중 오류가 발생했습니다');
    }
}
```

**성과**:
- **재시도 성공률**: 통신 오류 시 재시도로 **85% 성공**
- **고객 문의 감소**: 명확한 에러 메시지로 문의 **60% 감소**
- **결제 성공률**: 적절한 안내로 성공률 **15% 향상**

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: "예외가 먹히지 않아요!"

**상황**:
주니어 개발자 김코딩이 @ExceptionHandler를 작성했는데, 예외가 처리되지 않습니다.

```java
// ❌ 작동하지 않는 코드
@RestController
@RequestMapping("/api/products")
public class ProductController {

    @Autowired
    private ProductService productService;

    @GetMapping("/{id}")
    public Product getProduct(@PathVariable Long id) {
        return productService.findById(id);  // Exception 발생
    }

    // ❌ 예외가 잡히지 않음!
    @ExceptionHandler(ProductNotFoundException.class)
    public ResponseEntity<String> handleProductNotFound(ProductNotFoundException e) {
        return ResponseEntity.notFound().build();
    }
}
```

**문제점**:
1. **ProductService에서 다른 예외 발생**: EntityNotFoundException을 던지고 있음
2. **Checked Exception**: throws 선언되어 있어 @ExceptionHandler로 잡을 수 없음
3. **@RestController 없음**: 일반 @Controller라서 ResponseEntity 반환 안 됨

**해결책**:

```java
// ✅ Service 확인
@Service
public class ProductService {
    public Product findById(Long id) {
        return productRepository.findById(id)
            .orElseThrow(() -> new EntityNotFoundException("상품 없음"));
            // ❌ ProductNotFoundException이 아님!
    }
}

// ✅ 올바른 수정
@Service
public class ProductService {
    public Product findById(Long id) {
        return productRepository.findById(id)
            .orElseThrow(() -> new ProductNotFoundException(id));
            // ✅ ProductNotFoundException 발생
    }
}
```

**또 다른 문제: Checked Exception**

```java
// ❌ Checked Exception은 @ExceptionHandler로 못 잡음
public class ProductService {
    public Product findById(Long id) throws ProductNotFoundException {
        // throws 선언됨 → Checked Exception
        throw new ProductNotFoundException(id);
    }
}

// ✅ RuntimeException 상속
public class ProductNotFoundException extends RuntimeException {
    // Unchecked Exception으로 변경
}
```

**배운 점**:
- 💡 어떤 예외가 발생하는지 확인 (디버거 사용)
- 💡 @ExceptionHandler는 Unchecked Exception 권장
- 💡 Service 레이어의 예외 타입 확인

---

### 시나리오 2: "에러 응답이 HTML로 나와요!"

**상황**:
주니어 개발자 박초보가 @ExceptionHandler를 작성했는데, JSON 대신 HTML이 응답됩니다.

```java
// ❌ HTML 응답 나옴
@Controller  // @RestController가 아님!
public class UserController {

    @ExceptionHandler(UserNotFoundException.class)
    public ErrorResponse handleUserNotFound(UserNotFoundException e) {
        return new ErrorResponse("사용자 없음");
        // HTML 템플릿을 찾으려고 함!
    }
}
```

**문제점**:
1. **@Controller 사용**: @RestController가 아님
2. **@ResponseBody 없음**: JSON 변환 안 됨

**해결책**:

```java
// ✅ 방법 1: @RestController 사용
@RestController
public class UserController {

    @ExceptionHandler(UserNotFoundException.class)
    public ErrorResponse handleUserNotFound(UserNotFoundException e) {
        return new ErrorResponse("사용자 없음");
        // @RestController이므로 자동으로 JSON 변환
    }
}

// ✅ 방법 2: @ResponseBody 추가
@Controller
public class UserController {

    @ExceptionHandler(UserNotFoundException.class)
    @ResponseBody  // ✅ JSON 변환
    public ErrorResponse handleUserNotFound(UserNotFoundException e) {
        return new ErrorResponse("사용자 없음");
    }
}

// ✅ 방법 3: ResponseEntity 반환 (가장 명확)
@Controller
public class UserController {

    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        ErrorResponse error = new ErrorResponse("사용자 없음");
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
        // ResponseEntity는 자동으로 JSON 변환
    }
}
```

**배운 점**:
- 💡 REST API는 @RestController 사용
- 💡 ResponseEntity 사용이 가장 명확
- 💡 HTTP 상태 코드도 함께 설정

---

### 시나리오 3: "예외 처리가 중복돼요!"

**상황**:
주니어 개발자 이신입이 여러 Controller에서 같은 예외를 처리하고 있습니다.

```java
// ❌ UserController
@RestController
@RequestMapping("/api/users")
public class UserController {

    @ExceptionHandler(UnauthorizedException.class)
    public ResponseEntity<ErrorResponse> handleUnauthorized(UnauthorizedException e) {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
            .body(new ErrorResponse("인증 필요"));
    }
}

// ❌ ProductController에도 똑같은 코드
@RestController
@RequestMapping("/api/products")
public class ProductController {

    @ExceptionHandler(UnauthorizedException.class)
    public ResponseEntity<ErrorResponse> handleUnauthorized(UnauthorizedException e) {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
            .body(new ErrorResponse("인증 필요"));
    }
}

// ❌ OrderController에도 똑같은 코드...
```

**문제점**:
- 코드 중복
- 유지보수 어려움 (메시지 변경 시 모든 곳 수정)
- 일관성 없을 수 있음

**해결책: @ControllerAdvice 사용**

```java
// ✅ 전역 예외 처리
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(UnauthorizedException.class)
    public ResponseEntity<ErrorResponse> handleUnauthorized(UnauthorizedException e) {
        ErrorResponse error = ErrorResponse.builder()
            .code("UNAUTHORIZED")
            .message("인증이 필요합니다")
            .build();

        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
    }

    // 다른 공통 예외도 여기서 처리
    @ExceptionHandler(ForbiddenException.class)
    public ResponseEntity<ErrorResponse> handleForbidden(ForbiddenException e) {
        ErrorResponse error = ErrorResponse.builder()
            .code("FORBIDDEN")
            .message("권한이 없습니다")
            .build();

        return ResponseEntity.status(HttpStatus.FORBIDDEN).body(error);
    }
}

// ✅ Controller는 비즈니스 로직에만 집중
@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        // 예외 발생 시 GlobalExceptionHandler가 처리
        return userService.findById(id)
            .orElseThrow(() -> new UnauthorizedException());
    }
}
```

**배운 점**:
- 💡 공통 예외는 @ControllerAdvice로 처리
- 💡 Controller별 특수한 예외만 Controller에서 처리
- 💡 @RestControllerAdvice = @ControllerAdvice + @ResponseBody

---

## 🚀 실전 프로젝트: API 예외 처리 시스템

**프로젝트 개요**: 전자상거래 API의 체계적인 예외 처리 시스템 구현

### 요구사항

1. **비즈니스 예외 계층 구조**
   - 명확한 Exception 분류
   - ErrorCode enum 관리
   - 재시도 가능 여부 표시

2. **전역 예외 처리**
   - @ControllerAdvice로 통합 관리
   - Validation 에러 상세 처리
   - Spring 기본 예외 커스터마이징

3. **에러 응답 표준화**
   - 일관된 JSON 형식
   - 타임스탬프, 요청 경로 포함
   - 디버그 정보 (개발 환경에만)

4. **로깅 및 모니터링**
   - 에러 레벨별 로깅
   - Slack 알림 (Critical 에러)
   - 에러 통계 수집

---

### 프로젝트 구조

```
src/main/java/com/example/ecommerce/
├── exception/
│   ├── BusinessException.java              # 비즈니스 예외 최상위
│   ├── ErrorCode.java                       # 에러 코드 enum
│   ├── product/
│   │   ├── ProductNotFoundException.java
│   │   └── ProductOutOfStockException.java
│   ├── order/
│   │   ├── OrderNotFoundException.java
│   │   └── OrderCancellationException.java
│   ├── payment/
│   │   ├── PaymentFailedException.java
│   │   └── RefundFailedException.java
│   └── handler/
│       └── GlobalExceptionHandler.java      # 전역 예외 처리
├── dto/
│   └── ErrorResponse.java                   # 에러 응답 DTO
└── config/
    └── ErrorLoggingConfig.java              # 로깅 설정
```

---

### 1단계: 비즈니스 예외 계층 설계

#### ErrorCode Enum

```java
package com.example.ecommerce.exception;

import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
public enum ErrorCode {

    // 공통 (C)
    INVALID_INPUT("C001", "입력값이 올바르지 않습니다", HttpStatus.BAD_REQUEST, false),
    UNAUTHORIZED("C002", "인증이 필요합니다", HttpStatus.UNAUTHORIZED, false),
    FORBIDDEN("C003", "권한이 없습니다", HttpStatus.FORBIDDEN, false),
    INTERNAL_SERVER_ERROR("C999", "서버 에러가 발생했습니다", HttpStatus.INTERNAL_SERVER_ERROR, true),

    // 상품 (P)
    PRODUCT_NOT_FOUND("P001", "상품을 찾을 수 없습니다", HttpStatus.NOT_FOUND, false),
    PRODUCT_OUT_OF_STOCK("P002", "상품이 품절되었습니다", HttpStatus.CONFLICT, false),
    PRODUCT_ALREADY_EXISTS("P003", "이미 존재하는 상품입니다", HttpStatus.CONFLICT, false),

    // 주문 (O)
    ORDER_NOT_FOUND("O001", "주문을 찾을 수 없습니다", HttpStatus.NOT_FOUND, false),
    ORDER_ALREADY_CANCELLED("O002", "이미 취소된 주문입니다", HttpStatus.CONFLICT, false),
    ORDER_CANNOT_CANCEL("O003", "취소할 수 없는 주문입니다", HttpStatus.BAD_REQUEST, false),

    // 결제 (PAY)
    PAYMENT_FAILED("PAY001", "결제가 실패했습니다", HttpStatus.PAYMENT_REQUIRED, true),
    PAYMENT_NETWORK_ERROR("PAY002", "결제 통신 오류가 발생했습니다", HttpStatus.SERVICE_UNAVAILABLE, true),
    REFUND_FAILED("PAY003", "환불이 실패했습니다", HttpStatus.INTERNAL_SERVER_ERROR, true),

    // 재고 (S)
    STOCK_NOT_ENOUGH("S001", "재고가 부족합니다", HttpStatus.CONFLICT, false),
    STOCK_LOCK_FAILED("S002", "재고 잠금에 실패했습니다", HttpStatus.CONFLICT, true);

    private final String code;
    private final String message;
    private final HttpStatus httpStatus;
    private final boolean retryable;  // 재시도 가능 여부

    ErrorCode(String code, String message, HttpStatus httpStatus, boolean retryable) {
        this.code = code;
        this.message = message;
        this.httpStatus = httpStatus;
        this.retryable = retryable;
    }
}
```

#### BusinessException

```java
package com.example.ecommerce.exception;

import lombok.Getter;

@Getter
public class BusinessException extends RuntimeException {

    private final ErrorCode errorCode;
    private final Object[] args;  // 메시지 파라미터

    public BusinessException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
        this.args = null;
    }

    public BusinessException(ErrorCode errorCode, Object... args) {
        super(String.format(errorCode.getMessage(), args));
        this.errorCode = errorCode;
        this.args = args;
    }

    public BusinessException(ErrorCode errorCode, Throwable cause) {
        super(errorCode.getMessage(), cause);
        this.errorCode = errorCode;
        this.args = null;
    }

    public boolean isRetryable() {
        return errorCode.isRetryable();
    }
}
```

#### Product 예외

```java
package com.example.ecommerce.exception.product;

import com.example.ecommerce.exception.BusinessException;
import com.example.ecommerce.exception.ErrorCode;

public class ProductNotFoundException extends BusinessException {

    public ProductNotFoundException(Long productId) {
        super(ErrorCode.PRODUCT_NOT_FOUND);
        this.productId = productId;
    }

    private final Long productId;

    public Long getProductId() {
        return productId;
    }
}

public class ProductOutOfStockException extends BusinessException {

    private final Long productId;
    private final int requestedQuantity;
    private final int availableStock;

    public ProductOutOfStockException(Long productId, int requestedQuantity, int availableStock) {
        super(ErrorCode.PRODUCT_OUT_OF_STOCK);
        this.productId = productId;
        this.requestedQuantity = requestedQuantity;
        this.availableStock = availableStock;
    }

    public Long getProductId() { return productId; }
    public int getRequestedQuantity() { return requestedQuantity; }
    public int getAvailableStock() { return availableStock; }
}
```

#### Payment 예외

```java
package com.example.ecommerce.exception.payment;

import com.example.ecommerce.exception.BusinessException;
import com.example.ecommerce.exception.ErrorCode;

public class PaymentFailedException extends BusinessException {

    private final String paymentId;
    private final String reason;

    public PaymentFailedException(String paymentId, String reason) {
        super(ErrorCode.PAYMENT_FAILED);
        this.paymentId = paymentId;
        this.reason = reason;
    }

    public PaymentFailedException(String paymentId, String reason, Throwable cause) {
        super(ErrorCode.PAYMENT_FAILED, cause);
        this.paymentId = paymentId;
        this.reason = reason;
    }

    public String getPaymentId() { return paymentId; }
    public String getReason() { return reason; }
}

public class PaymentNetworkException extends BusinessException {

    public PaymentNetworkException(Throwable cause) {
        super(ErrorCode.PAYMENT_NETWORK_ERROR, cause);
    }
}
```

---

### 2단계: ErrorResponse 설계

```java
package com.example.ecommerce.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;
import java.util.List;

@Getter
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)  // null 필드는 JSON에 포함 안 함
public class ErrorResponse {

    private final String code;              // 에러 코드 (P001, O001 등)
    private final String message;           // 사용자 메시지
    private final String detail;            // 상세 설명
    private final List<FieldError> errors;  // 필드 에러 (Validation)
    private final boolean retryable;        // 재시도 가능 여부
    private final Integer retryAfter;       // 재시도 권장 시간 (초)
    private final String path;              // 요청 경로
    private final LocalDateTime timestamp;  // 발생 시각

    // 디버그 정보 (개발 환경에만)
    private final String exception;         // Exception 클래스명
    private final String trace;             // 스택 트레이스

    @Getter
    @Builder
    public static class FieldError {
        private final String field;          // 필드명
        private final String message;        // 에러 메시지
        private final Object rejectedValue;  // 거부된 값
    }
}
```

---

### 3단계: GlobalExceptionHandler 구현

```java
package com.example.ecommerce.exception.handler;

import com.example.ecommerce.dto.ErrorResponse;
import com.example.ecommerce.exception.BusinessException;
import com.example.ecommerce.exception.ErrorCode;
import com.example.ecommerce.exception.product.ProductNotFoundException;
import com.example.ecommerce.exception.product.ProductOutOfStockException;
import com.example.ecommerce.exception.payment.PaymentFailedException;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.ServletWebRequest;
import org.springframework.web.context.request.WebRequest;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {

    @Value("${app.debug:false}")
    private boolean debugMode;

    /**
     * 비즈니스 예외 처리 (공통)
     */
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusinessException(
        BusinessException e,
        HttpServletRequest request
    ) {
        ErrorCode errorCode = e.getErrorCode();

        // 로그 레벨 결정
        if (errorCode.getHttpStatus().is5xxServerError()) {
            log.error("비즈니스 예외 발생: code={}, message={}", errorCode.getCode(), e.getMessage(), e);
        } else {
            log.warn("비즈니스 예외 발생: code={}, message={}", errorCode.getCode(), e.getMessage());
        }

        ErrorResponse.ErrorResponseBuilder builder = ErrorResponse.builder()
            .code(errorCode.getCode())
            .message(errorCode.getMessage())
            .retryable(errorCode.isRetryable())
            .path(request.getRequestURI())
            .timestamp(LocalDateTime.now());

        // 디버그 정보 추가 (개발 환경에만)
        if (debugMode) {
            builder.exception(e.getClass().getSimpleName())
                   .trace(Arrays.stream(e.getStackTrace())
                       .limit(5)
                       .map(StackTraceElement::toString)
                       .collect(Collectors.joining("\n")));
        }

        return ResponseEntity
            .status(errorCode.getHttpStatus())
            .body(builder.build());
    }

    /**
     * 상품 없음 예외 (상세 정보 추가)
     */
    @ExceptionHandler(ProductNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleProductNotFound(
        ProductNotFoundException e,
        HttpServletRequest request
    ) {
        log.warn("상품을 찾을 수 없음: productId={}", e.getProductId());

        ErrorResponse response = ErrorResponse.builder()
            .code(e.getErrorCode().getCode())
            .message(e.getErrorCode().getMessage())
            .detail("상품 ID: " + e.getProductId())
            .retryable(false)
            .path(request.getRequestURI())
            .timestamp(LocalDateTime.now())
            .build();

        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(response);
    }

    /**
     * 재고 부족 예외 (상세 정보 추가)
     */
    @ExceptionHandler(ProductOutOfStockException.class)
    public ResponseEntity<ErrorResponse> handleProductOutOfStock(
        ProductOutOfStockException e,
        HttpServletRequest request
    ) {
        log.warn("재고 부족: productId={}, requested={}, available={}",
            e.getProductId(), e.getRequestedQuantity(), e.getAvailableStock());

        String detail = String.format(
            "요청 수량: %d개, 재고: %d개",
            e.getRequestedQuantity(),
            e.getAvailableStock()
        );

        ErrorResponse response = ErrorResponse.builder()
            .code(e.getErrorCode().getCode())
            .message(e.getErrorCode().getMessage())
            .detail(detail)
            .retryable(false)
            .path(request.getRequestURI())
            .timestamp(LocalDateTime.now())
            .build();

        return ResponseEntity.status(HttpStatus.CONFLICT).body(response);
    }

    /**
     * 결제 실패 예외 (재시도 정보 추가)
     */
    @ExceptionHandler(PaymentFailedException.class)
    public ResponseEntity<ErrorResponse> handlePaymentFailed(
        PaymentFailedException e,
        HttpServletRequest request
    ) {
        log.error("결제 실패: paymentId={}, reason={}", e.getPaymentId(), e.getReason(), e);

        ErrorResponse response = ErrorResponse.builder()
            .code(e.getErrorCode().getCode())
            .message(e.getErrorCode().getMessage())
            .detail(e.getReason())
            .retryable(e.isRetryable())
            .retryAfter(e.isRetryable() ? 5 : null)  // 5초 후 재시도
            .path(request.getRequestURI())
            .timestamp(LocalDateTime.now())
            .build();

        // Critical 에러 알림 (Slack 등)
        if (e.getCause() != null) {
            sendCriticalAlert(e);
        }

        return ResponseEntity.status(HttpStatus.PAYMENT_REQUIRED).body(response);
    }

    /**
     * Validation 에러 처리
     */
    @Override
    protected ResponseEntity<Object> handleMethodArgumentNotValid(
        MethodArgumentNotValidException ex,
        HttpHeaders headers,
        HttpStatusCode status,
        WebRequest request
    ) {
        log.warn("Validation 에러: {}", ex.getMessage());

        List<ErrorResponse.FieldError> fieldErrors = ex.getBindingResult()
            .getFieldErrors()
            .stream()
            .map(error -> ErrorResponse.FieldError.builder()
                .field(error.getField())
                .message(error.getDefaultMessage())
                .rejectedValue(error.getRejectedValue())
                .build())
            .collect(Collectors.toList());

        String path = ((ServletWebRequest) request).getRequest().getRequestURI();

        ErrorResponse errorResponse = ErrorResponse.builder()
            .code("C001")
            .message("입력값이 올바르지 않습니다")
            .errors(fieldErrors)
            .retryable(false)
            .path(path)
            .timestamp(LocalDateTime.now())
            .build();

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errorResponse);
    }

    /**
     * IllegalArgumentException 처리
     */
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorResponse> handleIllegalArgument(
        IllegalArgumentException e,
        HttpServletRequest request
    ) {
        log.warn("잘못된 인자: {}", e.getMessage());

        ErrorResponse response = ErrorResponse.builder()
            .code("C001")
            .message("잘못된 요청입니다")
            .detail(e.getMessage())
            .retryable(false)
            .path(request.getRequestURI())
            .timestamp(LocalDateTime.now())
            .build();

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * 모든 예외 처리 (Fallback)
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneral(
        Exception e,
        HttpServletRequest request
    ) {
        log.error("예상치 못한 에러 발생", e);

        // Critical 에러 알림
        sendCriticalAlert(e);

        ErrorResponse.ErrorResponseBuilder builder = ErrorResponse.builder()
            .code("C999")
            .message("서버 에러가 발생했습니다")
            .retryable(true)
            .path(request.getRequestURI())
            .timestamp(LocalDateTime.now());

        // 디버그 정보
        if (debugMode) {
            builder.exception(e.getClass().getSimpleName())
                   .detail(e.getMessage());
        }

        return ResponseEntity
            .status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(builder.build());
    }

    /**
     * Critical 에러 알림 (Slack, Email 등)
     */
    private void sendCriticalAlert(Exception e) {
        // TODO: Slack Webhook 호출
        log.error("🚨 CRITICAL ERROR: {}", e.getMessage());
        // slackClient.sendAlert("Critical Error: " + e.getMessage());
    }
}
```

---

### 4단계: Service에서 예외 발생

```java
package com.example.ecommerce.service;

import com.example.ecommerce.entity.Product;
import com.example.ecommerce.exception.product.ProductNotFoundException;
import com.example.ecommerce.exception.product.ProductOutOfStockException;
import com.example.ecommerce.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class ProductService {

    private final ProductRepository productRepository;

    @Transactional(readOnly = true)
    public Product findById(Long id) {
        return productRepository.findById(id)
            .orElseThrow(() -> new ProductNotFoundException(id));
    }

    @Transactional
    public void decreaseStock(Long productId, int quantity) {
        Product product = findById(productId);

        if (product.getStock() < quantity) {
            throw new ProductOutOfStockException(
                productId,
                quantity,
                product.getStock()
            );
        }

        product.decreaseStock(quantity);
    }
}
```

```java
package com.example.ecommerce.service;

import com.example.ecommerce.exception.payment.PaymentFailedException;
import com.example.ecommerce.exception.payment.PaymentNetworkException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

@Slf4j
@Service
@RequiredArgsConstructor
public class PaymentService {

    private final RestTemplate restTemplate;

    public void processPayment(String paymentId, long amount) {
        try {
            // 외부 결제 API 호출
            PaymentRequest request = new PaymentRequest(paymentId, amount);
            PaymentResponse response = restTemplate.postForObject(
                "https://api.payment.com/charge",
                request,
                PaymentResponse.class
            );

            if (response == null || !response.isSuccess()) {
                throw new PaymentFailedException(
                    paymentId,
                    response != null ? response.getFailureReason() : "알 수 없는 오류"
                );
            }

        } catch (RestClientException e) {
            // 네트워크 오류 (재시도 가능)
            log.error("결제 통신 오류: paymentId={}", paymentId, e);
            throw new PaymentNetworkException(e);
        }
    }
}
```

---

### 5단계: Controller

```java
package com.example.ecommerce.controller;

import com.example.ecommerce.dto.OrderRequest;
import com.example.ecommerce.dto.OrderResponse;
import com.example.ecommerce.service.OrderService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
public class OrderController {

    private final OrderService orderService;

    /**
     * 주문 생성
     * - 예외 발생 시 GlobalExceptionHandler가 처리
     */
    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(@Valid @RequestBody OrderRequest request) {
        // ProductNotFoundException, ProductOutOfStockException 등 발생 가능
        // → GlobalExceptionHandler가 처리
        OrderResponse response = orderService.createOrder(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<OrderResponse> getOrder(@PathVariable Long id) {
        // OrderNotFoundException 발생 가능
        OrderResponse response = orderService.findById(id);
        return ResponseEntity.ok(response);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> cancelOrder(@PathVariable Long id) {
        // OrderNotFoundException, OrderCancellationException 발생 가능
        orderService.cancelOrder(id);
        return ResponseEntity.noContent().build();
    }
}
```

---

### 6단계: 테스트

#### 통합 테스트

```java
package com.example.ecommerce.controller;

import com.example.ecommerce.dto.ErrorResponse;
import com.example.ecommerce.exception.ErrorCode;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class GlobalExceptionHandlerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    @DisplayName("존재하지 않는 상품 조회 시 404와 에러 응답 반환")
    void productNotFound() throws Exception {
        // When & Then
        MvcResult result = mockMvc.perform(get("/api/products/99999"))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.code").value("P001"))
            .andExpect(jsonPath("$.message").value("상품을 찾을 수 없습니다"))
            .andExpect(jsonPath("$.retryable").value(false))
            .andExpect(jsonPath("$.path").value("/api/products/99999"))
            .andExpect(jsonPath("$.timestamp").exists())
            .andReturn();

        String json = result.getResponse().getContentAsString();
        System.out.println("응답: " + json);
    }

    @Test
    @DisplayName("Validation 에러 시 400과 필드 에러 반환")
    void validationError() throws Exception {
        String invalidRequest = """
            {
                "name": "",
                "email": "invalid-email",
                "age": 15
            }
            """;

        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(invalidRequest))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.code").value("C001"))
            .andExpect(jsonPath("$.message").value("입력값이 올바르지 않습니다"))
            .andExpect(jsonPath("$.errors").isArray())
            .andExpect(jsonPath("$.errors[0].field").exists())
            .andExpect(jsonPath("$.errors[0].message").exists())
            .andReturn();
    }

    @Test
    @DisplayName("재고 부족 시 409와 상세 정보 반환")
    void productOutOfStock() throws Exception {
        // Given: 재고 10개인 상품
        Long productId = 1L;

        String orderRequest = """
            {
                "productId": 1,
                "quantity": 20
            }
            """;

        // When & Then
        mockMvc.perform(post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content(orderRequest))
            .andExpect(status().isConflict())
            .andExpect(jsonPath("$.code").value("P002"))
            .andExpect(jsonPath("$.message").value("상품이 품절되었습니다"))
            .andExpect(jsonPath("$.detail").value("요청 수량: 20개, 재고: 10개"))
            .andReturn();
    }
}
```

---

### 응답 예시

#### 1. 상품 없음 (404)

```bash
curl http://localhost:8080/api/products/99999
```

```json
{
  "code": "P001",
  "message": "상품을 찾을 수 없습니다",
  "detail": "상품 ID: 99999",
  "retryable": false,
  "path": "/api/products/99999",
  "timestamp": "2024-01-15T14:30:00"
}
```

#### 2. Validation 에러 (400)

```bash
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"","email":"invalid","age":15}'
```

```json
{
  "code": "C001",
  "message": "입력값이 올바르지 않습니다",
  "errors": [
    {
      "field": "name",
      "message": "이름은 필수입니다",
      "rejectedValue": ""
    },
    {
      "field": "email",
      "message": "올바른 이메일 형식이 아닙니다",
      "rejectedValue": "invalid"
    },
    {
      "field": "age",
      "message": "18세 이상이어야 합니다",
      "rejectedValue": 15
    }
  ],
  "retryable": false,
  "path": "/api/users",
  "timestamp": "2024-01-15T14:30:00"
}
```

#### 3. 결제 실패 (재시도 가능)

```json
{
  "code": "PAY002",
  "message": "결제 통신 오류가 발생했습니다",
  "detail": "Connection timeout",
  "retryable": true,
  "retryAfter": 5,
  "path": "/api/payments",
  "timestamp": "2024-01-15T14:30:00"
}
```

---

### 프로젝트 성과

| 지표 | 개선 효과 |
|------|-----------|
| 예외 처리 코드 라인 수 | **90% 감소** (Controller별 중복 제거) |
| 에러 응답 형식 통일 | **100% 일관성** |
| Critical 에러 대응 시간 | **80% 단축** (Slack 알림) |
| 클라이언트 에러 처리 개발 시간 | **50% 단축** (표준화된 응답) |

---

## ❓ FAQ

### Q1. @ExceptionHandler와 @ControllerAdvice의 차이는?

**A**: 적용 범위의 차이입니다.

```java
// @ExceptionHandler: 해당 Controller에만 적용
@RestController
public class UserController {

    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) {
        throw new UserNotFoundException(id);
    }

    // ✅ 이 Controller에서 발생한 UserNotFoundException만 처리
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse(e.getMessage()));
    }
}

// @ControllerAdvice: 모든 Controller에 적용
@RestControllerAdvice
public class GlobalExceptionHandler {

    // ✅ 모든 Controller에서 발생한 UserNotFoundException 처리
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse(e.getMessage()));
    }
}
```

**선택 기준**:
- 공통 예외 (모든 Controller에서 발생 가능): `@ControllerAdvice`
- Controller별 특수 예외: 해당 Controller의 `@ExceptionHandler`
- 우선순위: Controller의 @ExceptionHandler > @ControllerAdvice

---

### Q2. Exception을 RuntimeException으로 만들어야 하나요?

**A**: Spring에서는 **RuntimeException 권장**입니다.

**이유**:
1. **@Transactional 롤백**: RuntimeException만 자동 롤백
2. **코드 간결성**: throws 선언 불필요
3. **@ExceptionHandler 호환**: RuntimeException이 더 자연스럽게 처리

```java
// ❌ Checked Exception (비권장)
public class UserNotFoundException extends Exception {
    // 모든 메서드에 throws 선언 필요
}

@Service
public class UserService {
    // throws 선언 필수
    public User findById(Long id) throws UserNotFoundException {
        return userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));
    }
}

@RestController
public class UserController {
    // Controller도 throws 선언 필요
    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) throws UserNotFoundException {
        return userService.findById(id);
    }
}

// ✅ Unchecked Exception (권장)
public class UserNotFoundException extends RuntimeException {
    // throws 선언 불필요
}

@Service
public class UserService {
    public User findById(Long id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));
    }
}

@RestController
public class UserController {
    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
        // Exception 발생 시 GlobalExceptionHandler가 자동 처리
    }
}
```

**@Transactional 롤백**:
```java
@Transactional
public void createOrder(OrderRequest request) {
    Order order = orderRepository.save(new Order(request));

    // RuntimeException → 자동 롤백
    throw new PaymentFailedException("결제 실패");

    // Checked Exception → 롤백 안 됨 (rollbackFor 명시 필요)
    // throw new Exception("에러");
}
```

---

### Q3. ErrorCode를 enum으로 관리하는 이유는?

**A**: **중앙 집중식 관리**와 **타입 안전성** 때문입니다.

```java
// ❌ 문자열로 하드코딩 (비권장)
@ExceptionHandler(UserNotFoundException.class)
public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
    ErrorResponse error = new ErrorResponse("USER_NOT_FOUND", "사용자 없음");
    // 오타 가능: "USER_NOTFOUND", "USER_NOT_FOUN" 등
    return ResponseEntity.status(404).body(error);
    // 상태 코드도 하드코딩
}

// ✅ ErrorCode enum 사용 (권장)
@Getter
public enum ErrorCode {
    USER_NOT_FOUND("U001", "사용자를 찾을 수 없습니다", HttpStatus.NOT_FOUND),
    ORDER_NOT_FOUND("O001", "주문을 찾을 수 없습니다", HttpStatus.NOT_FOUND);

    private final String code;
    private final String message;
    private final HttpStatus httpStatus;

    ErrorCode(String code, String message, HttpStatus httpStatus) {
        this.code = code;
        this.message = message;
        this.httpStatus = httpStatus;
    }
}

@ExceptionHandler(UserNotFoundException.class)
public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
    ErrorCode errorCode = ErrorCode.USER_NOT_FOUND;
    ErrorResponse error = new ErrorResponse(errorCode.getCode(), errorCode.getMessage());
    return ResponseEntity.status(errorCode.getHttpStatus()).body(error);
    // 오타 불가능, 일관된 관리
}
```

**장점**:
1. **타입 안전성**: 컴파일 타임에 오타 검증
2. **중앙 관리**: 모든 에러 코드를 한 곳에서 관리
3. **일관성**: 같은 에러는 항상 같은 코드/메시지/상태 코드
4. **문서화**: enum만 보면 모든 에러 파악 가능

---

### Q4. Validation 에러와 비즈니스 에러를 구분해야 하나요?

**A**: 네, **명확히 구분**해야 합니다.

```java
// Validation 에러: 입력 형식 오류 (400 Bad Request)
@PostMapping("/users")
public ResponseEntity<User> createUser(@Valid @RequestBody UserRequest request) {
    // @Valid가 자동 검증
    // - 이메일 형식 오류
    // - 이름 길이 오류
    // - 필수 필드 누락
    // → MethodArgumentNotValidException 발생

    User user = userService.create(request);
    return ResponseEntity.ok(user);
}

// 비즈니스 에러: 비즈니스 규칙 위반 (409 Conflict 등)
@Service
public class UserService {
    public User create(UserRequest request) {
        // 이메일 중복 체크 (비즈니스 규칙)
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new DuplicateEmailException(request.getEmail());
            // 409 Conflict
        }

        return userRepository.save(new User(request));
    }
}
```

**구분 기준**:

| 구분 | Validation 에러 | 비즈니스 에러 |
|------|----------------|--------------|
| 발생 시점 | Controller 진입 전 | Service 로직 실행 중 |
| 검증 대상 | 입력 형식 | 비즈니스 규칙 |
| HTTP 상태 | 400 Bad Request | 409 Conflict, 404 Not Found 등 |
| 예시 | 이메일 형식, 필수 필드 | 중복 이메일, 재고 부족 |
| 처리 방법 | @Valid + MethodArgumentNotValidException | 커스텀 Exception |

---

### Q5. 스택 트레이스를 사용자에게 노출해도 되나요?

**A**: **절대 안 됩니다.** 보안 위협입니다.

```java
// ❌ 스택 트레이스 노출 (위험)
@ExceptionHandler(Exception.class)
public ResponseEntity<String> handleException(Exception e) {
    // 스택 트레이스를 그대로 반환
    StringWriter sw = new StringWriter();
    e.printStackTrace(new PrintWriter(sw));
    return ResponseEntity.status(500).body(sw.toString());
}
```

**문제점**:
1. **경로 노출**: 서버 디렉토리 구조 노출
2. **클래스명 노출**: 내부 구조 노출
3. **DB 정보 노출**: Connection String, 테이블명 등
4. **보안 취약점 발견**: 공격자에게 힌트 제공

```
예시 스택 트레이스:
java.sql.SQLException: Access denied for user 'admin'@'192.168.1.100'
    at com.mysql.jdbc.ConnectionImpl.connect(ConnectionImpl.java:123)
    at com.example.user.UserRepository.findById(UserRepository.java:45)
    at com.example.user.UserService.getUser(UserService.java:78)
↑ DB 계정, IP, 내부 경로 모두 노출!
```

**올바른 방법**:
```java
@ExceptionHandler(Exception.class)
public ResponseEntity<ErrorResponse> handleException(
    Exception e,
    HttpServletRequest request
) {
    // ✅ 로그에만 기록 (서버에서만 확인 가능)
    log.error("예상치 못한 에러 발생: path={}", request.getRequestURI(), e);

    // ✅ 사용자에게는 간단한 메시지만
    ErrorResponse response = ErrorResponse.builder()
        .code("C999")
        .message("서버 에러가 발생했습니다")  // 간단한 메시지
        .timestamp(LocalDateTime.now())
        .build();

    // 개발 환경에서만 스택 트레이스 추가
    if (debugMode) {
        response.setTrace(Arrays.stream(e.getStackTrace())
            .limit(5)
            .map(StackTraceElement::toString)
            .collect(Collectors.joining("\n")));
    }

    return ResponseEntity.status(500).body(response);
}
```

---

### Q6. 비동기 요청(@Async)에서 발생한 예외도 @ExceptionHandler로 처리되나요?

**A**: **아니요**, 별도 처리 필요합니다.

```java
// ❌ @Async 메서드의 예외는 @ExceptionHandler로 안 잡힘
@Service
public class EmailService {

    @Async
    public void sendEmail(String to, String content) {
        // 이 예외는 다른 스레드에서 발생
        throw new EmailSendException("이메일 전송 실패");
        // GlobalExceptionHandler로 안 잡힘!
    }
}
```

**해결책 1: AsyncUncaughtExceptionHandler 구현**

```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {

    @Override
    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
        return new CustomAsyncExceptionHandler();
    }
}

public class CustomAsyncExceptionHandler implements AsyncUncaughtExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(CustomAsyncExceptionHandler.class);

    @Override
    public void handleUncaughtException(Throwable ex, Method method, Object... params) {
        log.error("비동기 작업 실패: method={}, params={}", method.getName(), Arrays.toString(params), ex);

        // Slack 알림 등
        // slackClient.sendAlert("비동기 작업 실패: " + method.getName());
    }
}
```

**해결책 2: CompletableFuture로 예외 전파**

```java
@Service
public class EmailService {

    @Async
    public CompletableFuture<Void> sendEmail(String to, String content) {
        try {
            // 이메일 전송 로직
            return CompletableFuture.completedFuture(null);
        } catch (Exception e) {
            // 예외를 CompletableFuture에 담아 반환
            return CompletableFuture.failedFuture(e);
        }
    }
}

@RestController
public class UserController {

    @PostMapping("/users/register")
    public ResponseEntity<String> register(@RequestBody UserRequest request) {
        User user = userService.register(request);

        // 비동기 이메일 전송
        emailService.sendEmail(user.getEmail(), "환영합니다")
            .exceptionally(ex -> {
                // 여기서 예외 처리
                log.error("이메일 전송 실패", ex);
                return null;
            });

        return ResponseEntity.ok("가입 완료");
    }
}
```

---

### Q7. 로그 레벨을 어떻게 구분해야 하나요?

**A**: 에러의 **심각도**와 **대응 필요성**에 따라 구분합니다.

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        // WARN: 예상 가능한 에러, 비즈니스 로직상 정상
        log.warn("사용자를 찾을 수 없음: userId={}", e.getUserId());
        // 운영자 대응 불필요

        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse(e.getMessage()));
    }

    @ExceptionHandler(PaymentFailedException.class)
    public ResponseEntity<ErrorResponse> handlePaymentFailed(PaymentFailedException e) {
        // ERROR: 예상치 못한 에러, 대응 필요
        log.error("결제 실패: paymentId={}, reason={}", e.getPaymentId(), e.getReason(), e);
        // 운영자가 확인하고 대응해야 함

        // Critical 알림
        sendSlackAlert("결제 실패: " + e.getMessage());

        return ResponseEntity.status(HttpStatus.PAYMENT_REQUIRED)
            .body(new ErrorResponse(e.getMessage()));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneral(Exception e) {
        // ERROR: 예상치 못한 모든 에러
        log.error("예상치 못한 에러 발생", e);
        // 즉시 대응 필요

        sendSlackAlert("🚨 CRITICAL: " + e.getMessage());

        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(new ErrorResponse("서버 에러가 발생했습니다"));
    }
}
```

**로그 레벨 가이드**:

| 레벨 | 사용 시기 | 예시 | 대응 |
|------|-----------|------|------|
| DEBUG | 디버깅 정보 | 파라미터 값, 중간 계산 결과 | 대응 불필요 |
| INFO | 정상 흐름 | 주문 생성, 로그인 성공 | 대응 불필요 |
| WARN | 예상 가능한 에러 | 사용자 없음, 재고 부족 | 대응 불필요 (비즈니스상 정상) |
| ERROR | 예상치 못한 에러 | 결제 실패, DB 연결 오류 | 즉시 대응 필요 |

---

## 🎤 면접 질문

### 주니어 레벨 (5-7개)

1. **@ExceptionHandler와 @ControllerAdvice의 차이를 설명하세요.**
   - 힌트: 적용 범위, 사용 시기

2. **Spring MVC에서 예외 처리 흐름을 설명하세요.**
   - 힌트: Controller → @ExceptionHandler → @ControllerAdvice → DefaultHandlerExceptionResolver

3. **RuntimeException과 Checked Exception의 차이는 무엇인가요? Spring에서는 어떤 것을 권장하나요?**
   - 힌트: throws 선언, @Transactional 롤백

4. **HTTP 상태 코드 400, 401, 403, 404, 500의 의미를 설명하세요.**
   - 힌트: Bad Request, Unauthorized, Forbidden, Not Found, Internal Server Error

5. **@RestController와 @Controller에서 @ExceptionHandler의 반환 타입이 어떻게 다른가요?**
   - 힌트: @ResponseBody, JSON vs HTML

6. **MethodArgumentNotValidException은 언제 발생하나요?**
   - 힌트: @Valid, Bean Validation

7. **@ResponseStatus 어노테이션의 역할은 무엇인가요?**
   - 힌트: Exception 클래스에 고정 HTTP 상태 코드 지정

---

### 중급 레벨 (3-5개)

1. **@ExceptionHandler의 우선순위 규칙을 설명하세요.**
   - 힌트: Controller vs @ControllerAdvice, 구체적 타입 vs 상위 타입

2. **ResponseEntityExceptionHandler를 상속하는 이유는 무엇인가요?**
   - 힌트: Spring 기본 예외 커스터마이징

3. **비동기 메서드(@Async)에서 발생한 예외를 어떻게 처리하나요?**
   - 힌트: AsyncUncaughtExceptionHandler, CompletableFuture

4. **에러 응답에 스택 트레이스를 포함하면 안 되는 이유는?**
   - 힌트: 보안 위협, 경로 노출

5. **커스텀 Exception 계층 구조를 어떻게 설계하나요?**
   - 힌트: BusinessException, ErrorCode enum, retryable 플래그

---

## 🎯 면접 질문 답안

### 주니어 레벨

#### Q1. @ExceptionHandler와 @ControllerAdvice의 차이를 설명하세요.

**답변**:

@ExceptionHandler와 @ControllerAdvice의 가장 큰 차이는 **적용 범위**입니다.

**@ExceptionHandler**는 해당 Controller 클래스 내에서만 동작합니다. Controller 메서드에서 예외가 발생하면, 같은 클래스 안에 있는 @ExceptionHandler 메서드가 이를 처리합니다.

```java
@RestController
public class UserController {

    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) {
        throw new UserNotFoundException(id);
    }

    // ✅ 이 Controller에서만 처리
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("사용자 없음"));
    }
}
```

반면 **@ControllerAdvice**는 애플리케이션의 모든 Controller에 적용됩니다. 전역 예외 처리기로 동작하여, 어느 Controller에서 예외가 발생하든 처리할 수 있습니다.

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    // ✅ 모든 Controller에서 처리
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("사용자 없음"));
    }
}
```

**사용 시기**:
- 공통 예외 (모든 Controller에서 발생): @ControllerAdvice
- Controller별 특수 예외: @ExceptionHandler (Controller 내부)

**우선순위**: Controller의 @ExceptionHandler가 @ControllerAdvice보다 우선합니다.

---

#### Q2. Spring MVC에서 예외 처리 흐름을 설명하세요.

**답변**:

Spring MVC의 예외 처리는 다음과 같은 순서로 진행됩니다:

1. **Controller 메서드 실행 중 Exception 발생**
2. **DispatcherServlet이 Exception을 잡음**
3. **HandlerExceptionResolver 체인 시작**
   - ExceptionHandlerExceptionResolver: @ExceptionHandler 찾기
     - 먼저 같은 Controller의 @ExceptionHandler 검색
     - 없으면 @ControllerAdvice의 @ExceptionHandler 검색
   - ResponseStatusExceptionResolver: @ResponseStatus 어노테이션 확인
   - DefaultHandlerExceptionResolver: Spring 기본 예외 처리
4. **적절한 Handler를 찾으면 실행하여 응답 생성**
5. **Handler를 못 찾으면 Servlet Container의 에러 페이지로 전달**

```
Controller.method()
   ↓ (Exception 발생)
DispatcherServlet
   ↓
ExceptionHandlerExceptionResolver
   ├─ Controller의 @ExceptionHandler? → 있으면 실행
   └─ @ControllerAdvice의 @ExceptionHandler? → 있으면 실행
   ↓ (없으면)
ResponseStatusExceptionResolver
   └─ @ResponseStatus 있으면 실행
   ↓ (없으면)
DefaultHandlerExceptionResolver
   └─ Spring 기본 예외 처리
   ↓ (없으면)
Servlet Container 에러 페이지
```

**예시**:
```java
// UserController에서 예외 발생
throw new UserNotFoundException(1L);

// 처리 순서:
// 1. UserController의 @ExceptionHandler(UserNotFoundException.class) 찾기
// 2. 없으면 GlobalExceptionHandler의 @ExceptionHandler(UserNotFoundException.class) 찾기
// 3. 없으면 GlobalExceptionHandler의 @ExceptionHandler(RuntimeException.class) 찾기
// 4. 없으면 GlobalExceptionHandler의 @ExceptionHandler(Exception.class) 찾기
```

---

#### Q3. RuntimeException과 Checked Exception의 차이는 무엇인가요? Spring에서는 어떤 것을 권장하나요?

**답변**:

**RuntimeException** (Unchecked Exception)과 **Checked Exception**의 주요 차이는 **컴파일러의 예외 처리 강제 여부**입니다.

**Checked Exception**:
- Exception 클래스를 직접 상속
- 메서드 시그니처에 `throws` 선언 필수
- try-catch 또는 throws로 반드시 처리해야 함
- 예시: IOException, SQLException

```java
// Checked Exception
public class UserNotFoundException extends Exception {
    // ...
}

// throws 선언 필수
public User findById(Long id) throws UserNotFoundException {
    return userRepository.findById(id)
        .orElseThrow(() -> new UserNotFoundException(id));
}

// 호출하는 쪽도 처리 필요
try {
    User user = userService.findById(1L);
} catch (UserNotFoundException e) {
    // 처리
}
```

**RuntimeException** (Unchecked Exception):
- RuntimeException 클래스를 상속
- throws 선언 불필요
- 처리하지 않아도 컴파일 에러 없음
- 예시: NullPointerException, IllegalArgumentException

```java
// Unchecked Exception
public class UserNotFoundException extends RuntimeException {
    // ...
}

// throws 선언 불필요
public User findById(Long id) {
    return userRepository.findById(id)
        .orElseThrow(() -> new UserNotFoundException(id));
}

// 호출하는 쪽도 간결
User user = userService.findById(1L);
// Exception 발생 시 GlobalExceptionHandler가 처리
```

**Spring에서는 RuntimeException을 권장합니다**. 이유는:

1. **@Transactional 롤백**: RuntimeException만 기본적으로 롤백합니다.
```java
@Transactional
public void createOrder(OrderRequest request) {
    orderRepository.save(new Order(request));

    // RuntimeException → 자동 롤백
    throw new PaymentFailedException("결제 실패");

    // Checked Exception → 롤백 안 됨 (rollbackFor 필요)
}
```

2. **코드 간결성**: throws 선언이 불필요하여 코드가 깔끔합니다.

3. **@ExceptionHandler 호환**: RuntimeException이 더 자연스럽게 처리됩니다.

---

#### Q4. HTTP 상태 코드 400, 401, 403, 404, 500의 의미를 설명하세요.

**답변**:

| 상태 코드 | 이름 | 의미 | 사용 예시 |
|-----------|------|------|-----------|
| **400** | Bad Request | 클라이언트의 잘못된 요청 | Validation 에러, 잘못된 파라미터 |
| **401** | Unauthorized | 인증 필요 | 로그인하지 않은 사용자 |
| **403** | Forbidden | 권한 없음 | 로그인했지만 권한 부족 |
| **404** | Not Found | 리소스 없음 | 존재하지 않는 사용자, 상품 |
| **500** | Internal Server Error | 서버 에러 | 예상치 못한 에러, DB 연결 실패 |

**Spring 예시**:

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    // 400 Bad Request
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(MethodArgumentNotValidException e) {
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)  // 400
            .body(new ErrorResponse("입력값이 올바르지 않습니다"));
    }

    // 401 Unauthorized
    @ExceptionHandler(UnauthorizedException.class)
    public ResponseEntity<ErrorResponse> handleUnauthorized(UnauthorizedException e) {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED)  // 401
            .body(new ErrorResponse("로그인이 필요합니다"));
    }

    // 403 Forbidden
    @ExceptionHandler(ForbiddenException.class)
    public ResponseEntity<ErrorResponse> handleForbidden(ForbiddenException e) {
        return ResponseEntity.status(HttpStatus.FORBIDDEN)  // 403
            .body(new ErrorResponse("권한이 없습니다"));
    }

    // 404 Not Found
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)  // 404
            .body(new ErrorResponse("사용자를 찾을 수 없습니다"));
    }

    // 500 Internal Server Error
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneral(Exception e) {
        log.error("예상치 못한 에러", e);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)  // 500
            .body(new ErrorResponse("서버 에러가 발생했습니다"));
    }
}
```

**구분 방법**:
- **4xx**: 클라이언트 잘못 (요청 수정 필요)
- **5xx**: 서버 잘못 (서버 수정 필요)

---

#### Q5. @RestController와 @Controller에서 @ExceptionHandler의 반환 타입이 어떻게 다른가요?

**답변**:

**@RestController**와 **@Controller**의 차이는 **응답 형식**입니다.

**@RestController**: 반환값이 자동으로 **JSON/XML**로 변환됩니다.
```java
@RestController
public class UserController {

    @ExceptionHandler(UserNotFoundException.class)
    public ErrorResponse handleUserNotFound(UserNotFoundException e) {
        // ✅ ErrorResponse 객체가 자동으로 JSON으로 변환
        return new ErrorResponse("사용자 없음");
    }
}

// 응답 (JSON):
// {"code":"USER_NOT_FOUND","message":"사용자 없음"}
```

**@Controller**: 반환값이 **View 이름**으로 해석되어 HTML 템플릿을 찾습니다.
```java
@Controller
public class UserController {

    @ExceptionHandler(UserNotFoundException.class)
    public String handleUserNotFound(UserNotFoundException e, Model model) {
        model.addAttribute("error", "사용자 없음");
        // ✅ "error/404" 라는 이름의 HTML 템플릿을 찾음
        return "error/404";
    }
}

// 응답: error/404.html 페이지 렌더링
```

**@Controller에서 JSON 응답하려면**:
```java
@Controller
public class UserController {

    @ExceptionHandler(UserNotFoundException.class)
    @ResponseBody  // ✅ JSON 변환
    public ErrorResponse handleUserNotFound(UserNotFoundException e) {
        return new ErrorResponse("사용자 없음");
    }

    // 또는 ResponseEntity 사용
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound2(UserNotFoundException e) {
        // ResponseEntity는 자동으로 JSON 변환
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("사용자 없음"));
    }
}
```

**정리**:
- `@RestController` = `@Controller` + `@ResponseBody`
- REST API는 @RestController 사용
- HTML 페이지는 @Controller 사용

---

#### Q6. MethodArgumentNotValidException은 언제 발생하나요?

**답변**:

**MethodArgumentNotValidException**은 **@Valid 검증에 실패했을 때** 발생합니다.

Spring은 Controller 메서드에 `@Valid` 어노테이션이 있으면, 요청 데이터를 **Bean Validation**으로 자동 검증합니다. 검증 실패 시 MethodArgumentNotValidException이 발생합니다.

**발생 과정**:

```java
// 1. DTO에 Validation 규칙 정의
@Getter
@Setter
public class UserRequest {

    @NotBlank(message = "이름은 필수입니다")
    @Size(min = 2, max = 20, message = "이름은 2~20자여야 합니다")
    private String name;

    @NotBlank(message = "이메일은 필수입니다")
    @Email(message = "올바른 이메일 형식이 아닙니다")
    private String email;

    @NotNull(message = "나이는 필수입니다")
    @Min(value = 18, message = "18세 이상이어야 합니다")
    private Integer age;
}

// 2. Controller에서 @Valid로 검증
@RestController
@RequestMapping("/api/users")
public class UserController {

    @PostMapping
    public ResponseEntity<User> createUser(@Valid @RequestBody UserRequest request) {
        // @Valid가 UserRequest 검증
        // → 실패 시 MethodArgumentNotValidException 발생
        User user = userService.create(request);
        return ResponseEntity.ok(user);
    }
}

// 3. GlobalExceptionHandler에서 처리
@RestControllerAdvice
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {

    @Override
    protected ResponseEntity<Object> handleMethodArgumentNotValid(
        MethodArgumentNotValidException ex,
        HttpHeaders headers,
        HttpStatusCode status,
        WebRequest request
    ) {
        // 필드 에러 추출
        List<FieldError> fieldErrors = ex.getBindingResult()
            .getFieldErrors()
            .stream()
            .map(error -> new FieldError(
                error.getField(),
                error.getDefaultMessage(),
                error.getRejectedValue()
            ))
            .collect(Collectors.toList());

        ErrorResponse errorResponse = new ErrorResponse(
            "VALIDATION_ERROR",
            "입력값이 올바르지 않습니다",
            fieldErrors
        );

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errorResponse);
    }
}
```

**테스트**:
```bash
# 잘못된 요청
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"A","email":"invalid","age":15}'

# 응답 (400 Bad Request):
{
  "code": "VALIDATION_ERROR",
  "message": "입력값이 올바르지 않습니다",
  "errors": [
    {
      "field": "name",
      "message": "이름은 2~20자여야 합니다",
      "rejectedValue": "A"
    },
    {
      "field": "email",
      "message": "올바른 이메일 형식이 아닙니다",
      "rejectedValue": "invalid"
    },
    {
      "field": "age",
      "message": "18세 이상이어야 합니다",
      "rejectedValue": 15
    }
  ]
}
```

---

#### Q7. @ResponseStatus 어노테이션의 역할은 무엇인가요?

**답변**:

**@ResponseStatus**는 특정 Exception에 **고정된 HTTP 상태 코드**를 지정하는 어노테이션입니다.

Exception 클래스에 @ResponseStatus를 붙이면, 해당 예외 발생 시 지정한 상태 코드로 자동 응답됩니다.

**사용 예시**:

```java
// Exception 클래스에 상태 코드 지정
@ResponseStatus(HttpStatus.NOT_FOUND)  // 404
public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(Long userId) {
        super("사용자를 찾을 수 없습니다: " + userId);
    }
}

@ResponseStatus(HttpStatus.CONFLICT)  // 409
public class DuplicateEmailException extends RuntimeException {
    public DuplicateEmailException(String email) {
        super("이미 사용 중인 이메일입니다: " + email);
    }
}

// Controller에서 발생
@RestController
public class UserController {

    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) {
        // UserNotFoundException 발생 시 자동으로 404 응답
        throw new UserNotFoundException(id);
    }
}
```

**장점**:
- 간단한 예외 처리 (별도 @ExceptionHandler 불필요)
- Exception 클래스에 상태 코드가 명시됨

**단점**:
- 응답 메시지 커스터마이징 어려움
- 항상 고정된 상태 코드만 사용 가능

**@ExceptionHandler와 비교**:

```java
// @ResponseStatus: 간단하지만 제한적
@ResponseStatus(HttpStatus.NOT_FOUND)
public class UserNotFoundException extends RuntimeException {
    // 항상 404만 응답, 메시지 커스터마이징 어려움
}

// @ExceptionHandler: 복잡하지만 유연
@ExceptionHandler(UserNotFoundException.class)
public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
    // 상황에 따라 상태 코드 변경 가능
    // 메시지, 상세 정보 자유롭게 구성
    ErrorResponse error = ErrorResponse.builder()
        .code("USER_NOT_FOUND")
        .message("사용자를 찾을 수 없습니다")
        .detail("userId: " + e.getUserId())
        .build();

    return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
}
```

**권장 사용**:
- 단순한 예외: @ResponseStatus
- 복잡한 응답 필요: @ExceptionHandler

---

### 중급 레벨

#### Q1. @ExceptionHandler의 우선순위 규칙을 설명하세요.

**답변**:

@ExceptionHandler의 우선순위는 **3가지 규칙**에 따라 결정됩니다.

**규칙 1: 위치 (Controller vs @ControllerAdvice)**

Controller 내부의 @ExceptionHandler가 @ControllerAdvice의 @ExceptionHandler보다 우선합니다.

```java
@RestController
public class UserController {

    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) {
        throw new UserNotFoundException(id);
    }

    // ✅ 1순위: Controller의 @ExceptionHandler
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("Controller에서 처리"));
    }
}

@RestControllerAdvice
public class GlobalExceptionHandler {

    // 2순위: @ControllerAdvice의 @ExceptionHandler
    // (Controller에 없을 때만 실행)
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("GlobalExceptionHandler에서 처리"));
    }
}

// 결과: "Controller에서 처리" 응답
```

**규칙 2: Exception 타입 (구체적 vs 상위 타입)**

더 구체적인 타입의 @ExceptionHandler가 상위 타입보다 우선합니다.

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    // 1순위: 구체적 타입 (UserNotFoundException)
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("사용자 없음"));
    }

    // 2순위: 상위 타입 (BusinessException)
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusiness(BusinessException e) {
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
            .body(new ErrorResponse("비즈니스 에러"));
    }

    // 3순위: 최상위 타입 (RuntimeException)
    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<ErrorResponse> handleRuntime(RuntimeException e) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(new ErrorResponse("런타임 에러"));
    }

    // 4순위: Exception
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneral(Exception e) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(new ErrorResponse("서버 에러"));
    }
}

// 계층 구조:
// Exception
//   └─ RuntimeException
//        └─ BusinessException
//             └─ UserNotFoundException

// UserNotFoundException 발생 시:
// → handleUserNotFound() 실행 (가장 구체적)
```

**규칙 3: 선언 순서**

같은 레벨의 Handler가 여러 개면 먼저 선언된 것이 우선합니다 (일반적으로는 발생하지 않음).

**실전 예시**:

```java
@RestController
public class ProductController {

    @GetMapping("/products/{id}")
    public Product getProduct(@PathVariable Long id) {
        throw new ProductNotFoundException(id);
        // ProductNotFoundException extends BusinessException extends RuntimeException
    }

    // Controller의 BusinessException Handler
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusiness(BusinessException e) {
        return ResponseEntity.badRequest().body(new ErrorResponse("Controller 비즈니스 에러"));
    }
}

@RestControllerAdvice
public class GlobalExceptionHandler {

    // Global의 ProductNotFoundException Handler
    @ExceptionHandler(ProductNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleProductNotFound(ProductNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("Global 상품 없음"));
    }

    // Global의 BusinessException Handler
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusiness(BusinessException e) {
        return ResponseEntity.badRequest().body(new ErrorResponse("Global 비즈니스 에러"));
    }
}

// 결과:
// ProductNotFoundException 발생
// → Controller의 BusinessException Handler 실행
//    (위치 우선: Controller > Global)
// → "Controller 비즈니스 에러" 응답
```

**우선순위 요약**:
1. **위치**: Controller > @ControllerAdvice
2. **타입**: 구체적 > 상위
3. **순서**: 먼저 선언된 것 우선

---

#### Q2. ResponseEntityExceptionHandler를 상속하는 이유는 무엇인가요?

**답변**:

**ResponseEntityExceptionHandler**를 상속하는 이유는 **Spring이 제공하는 기본 예외를 커스터마이징**하기 위해서입니다.

Spring MVC는 다양한 내부 예외를 발생시킵니다 (MethodArgumentNotValidException, HttpRequestMethodNotSupportedException 등). ResponseEntityExceptionHandler를 상속하면 이러한 예외들을 쉽게 커스터마이징할 수 있습니다.

**상속하지 않으면**:

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    // ❌ Validation 에러를 직접 처리해야 함
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(MethodArgumentNotValidException ex) {
        // 복잡한 필드 에러 추출 로직 필요
        List<FieldError> errors = ex.getBindingResult()
            .getFieldErrors()
            .stream()
            .map(error -> new FieldError(error.getField(), error.getDefaultMessage()))
            .collect(Collectors.toList());

        return ResponseEntity.badRequest().body(new ErrorResponse("Validation 에러", errors));
    }

    // ❌ HTTP 메서드 불일치도 직접 처리
    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    public ResponseEntity<ErrorResponse> handleMethodNotSupported(
        HttpRequestMethodNotSupportedException ex
    ) {
        return ResponseEntity.status(HttpStatus.METHOD_NOT_ALLOWED)
            .body(new ErrorResponse(ex.getMethod() + " 메서드는 지원하지 않습니다"));
    }

    // 더 많은 Spring 예외들...
}
```

**상속하면**:

```java
@RestControllerAdvice
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {

    // ✅ Spring 기본 예외를 오버라이드하여 커스터마이징
    @Override
    protected ResponseEntity<Object> handleMethodArgumentNotValid(
        MethodArgumentNotValidException ex,
        HttpHeaders headers,
        HttpStatusCode status,
        WebRequest request
    ) {
        // ResponseEntityExceptionHandler가 이미 기본 처리 제공
        // 필요한 부분만 커스터마이징
        List<ErrorResponse.FieldError> fieldErrors = ex.getBindingResult()
            .getFieldErrors()
            .stream()
            .map(error -> ErrorResponse.FieldError.builder()
                .field(error.getField())
                .message(error.getDefaultMessage())
                .rejectedValue(error.getRejectedValue())
                .build())
            .collect(Collectors.toList());

        ErrorResponse errorResponse = ErrorResponse.builder()
            .code("VALIDATION_ERROR")
            .message("입력값이 올바르지 않습니다")
            .errors(fieldErrors)
            .timestamp(LocalDateTime.now())
            .build();

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errorResponse);
    }

    @Override
    protected ResponseEntity<Object> handleHttpRequestMethodNotSupported(
        HttpRequestMethodNotSupportedException ex,
        HttpHeaders headers,
        HttpStatusCode status,
        WebRequest request
    ) {
        ErrorResponse errorResponse = ErrorResponse.builder()
            .code("METHOD_NOT_ALLOWED")
            .message(ex.getMethod() + " 메서드는 지원하지 않습니다")
            .supportedMethods(ex.getSupportedHttpMethods())
            .build();

        return ResponseEntity.status(HttpStatus.METHOD_NOT_ALLOWED).body(errorResponse);
    }

    // 필요한 메서드만 오버라이드
}
```

**ResponseEntityExceptionHandler가 처리하는 Spring 예외들**:

| 예외 | 발생 시점 | HTTP 상태 |
|------|-----------|-----------|
| MethodArgumentNotValidException | @Valid 검증 실패 | 400 |
| HttpRequestMethodNotSupportedException | HTTP 메서드 불일치 (GET 대신 POST) | 405 |
| HttpMediaTypeNotSupportedException | Content-Type 불일치 | 415 |
| MissingServletRequestParameterException | 필수 파라미터 누락 | 400 |
| TypeMismatchException | 타입 변환 실패 | 400 |
| HttpMessageNotReadableException | JSON 파싱 실패 | 400 |

**장점**:
1. **일관성**: Spring 예외도 커스텀 ErrorResponse 형식으로 통일
2. **간편함**: 필요한 메서드만 오버라이드
3. **유지보수**: Spring이 내부 처리 로직 관리

**정리**:
- Spring 기본 예외를 커스터마이징하려면 **ResponseEntityExceptionHandler 상속**
- 비즈니스 예외만 처리한다면 상속 불필요

---

#### Q3. 비동기 메서드(@Async)에서 발생한 예외를 어떻게 처리하나요?

**답변**:

@Async 메서드에서 발생한 예외는 **다른 스레드**에서 발생하기 때문에 **@ExceptionHandler로 잡을 수 없습니다**. 별도의 처리 방법이 필요합니다.

**문제 상황**:

```java
@Service
public class EmailService {

    @Async
    public void sendEmail(String to, String content) {
        // 이 예외는 비동기 스레드에서 발생
        throw new EmailSendException("이메일 전송 실패");
        // GlobalExceptionHandler로 잡히지 않음!
    }
}

@RestController
public class UserController {

    @PostMapping("/users/register")
    public ResponseEntity<String> register(@RequestBody UserRequest request) {
        User user = userService.register(request);
        emailService.sendEmail(user.getEmail(), "환영합니다");
        // 이메일 전송 실패해도 모름

        return ResponseEntity.ok("가입 완료");
    }
}
```

**해결책 1: AsyncUncaughtExceptionHandler 구현**

비동기 스레드의 예외를 처리하는 전역 핸들러를 등록합니다.

```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(10);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("async-");
        executor.initialize();
        return executor;
    }

    @Override
    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
        return new CustomAsyncExceptionHandler();
    }
}

@Slf4j
public class CustomAsyncExceptionHandler implements AsyncUncaughtExceptionHandler {

    @Override
    public void handleUncaughtException(Throwable ex, Method method, Object... params) {
        log.error("비동기 작업 실패: method={}, params={}",
            method.getName(),
            Arrays.toString(params),
            ex);

        // Slack 알림 등
        // slackClient.sendAlert("비동기 작업 실패: " + method.getName());
    }
}
```

**해결책 2: CompletableFuture로 예외 전파**

비동기 메서드가 CompletableFuture를 반환하도록 하여 예외를 호출자에게 전달합니다.

```java
@Service
public class EmailService {

    @Async
    public CompletableFuture<Void> sendEmail(String to, String content) {
        try {
            // 이메일 전송 로직
            mailSender.send(to, content);
            return CompletableFuture.completedFuture(null);
        } catch (Exception e) {
            // 예외를 CompletableFuture에 담아 반환
            return CompletableFuture.failedFuture(e);
        }
    }
}

@RestController
public class UserController {

    @PostMapping("/users/register")
    public ResponseEntity<String> register(@RequestBody UserRequest request) {
        User user = userService.register(request);

        // 비동기 이메일 전송
        emailService.sendEmail(user.getEmail(), "환영합니다")
            .exceptionally(ex -> {
                // ✅ 예외 처리
                log.error("이메일 전송 실패: email={}", user.getEmail(), ex);
                // 사용자에게 알림 (WebSocket, SSE 등)
                notificationService.sendNotification(user.getId(), "이메일 전송 실패");
                return null;
            });

        return ResponseEntity.ok("가입 완료");
    }
}
```

**해결책 3: try-catch 내부 처리**

비동기 메서드 내부에서 직접 예외를 처리합니다.

```java
@Service
@Slf4j
public class EmailService {

    @Async
    public void sendEmail(String to, String content) {
        try {
            mailSender.send(to, content);
            log.info("이메일 전송 성공: {}", to);
        } catch (Exception e) {
            // ✅ 내부에서 예외 처리
            log.error("이메일 전송 실패: to={}", to, e);

            // Slack 알림
            slackClient.sendAlert("이메일 전송 실패: " + to);

            // 재시도 큐에 추가
            retryQueue.add(new EmailTask(to, content));
        }
    }
}
```

**권장 방법**:
- **fire-and-forget 방식**: AsyncUncaughtExceptionHandler (로깅만)
- **결과 확인 필요**: CompletableFuture (예외 전파)
- **재시도 필요**: 내부 try-catch (재시도 로직)

---

#### Q4. 에러 응답에 스택 트레이스를 포함하면 안 되는 이유는?

**답변**:

에러 응답에 스택 트레이스를 포함하면 **심각한 보안 위협**이 됩니다.

**문제점 1: 내부 경로 노출**

스택 트레이스는 서버의 디렉토리 구조를 노출합니다.

```
java.lang.NullPointerException: Cannot invoke "User.getName()"
    at com.example.service.UserService.updateUser(UserService.java:78)
    at com.example.controller.UserController.updateUser(UserController.java:45)
    at /app/backend/src/main/java/com/example/
↑ 서버 경로 노출!
```

**문제점 2: 데이터베이스 정보 노출**

DB 연결 실패 시 계정, IP, 테이블명 등이 노출됩니다.

```
java.sql.SQLException: Access denied for user 'admin'@'192.168.1.100' (using password: YES)
    at com.mysql.cj.jdbc.exceptions.SQLError.createSQLException
    at com.mysql.cj.jdbc.ConnectionImpl.connectOneTryOnly
↑ DB 계정, IP, DB 엔진 노출!
```

**문제점 3: 비즈니스 로직 노출**

메서드명과 클래스 구조로 비즈니스 로직을 유추할 수 있습니다.

```
at com.example.payment.TossPaymentGateway.processPayment
at com.example.payment.PaymentService.chargeCard
at com.example.order.OrderService.confirmOrder
↑ 결제 프로세스 흐름 노출!
```

**올바른 방법**:

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @Value("${app.debug:false}")
    private boolean debugMode;

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleException(
        Exception e,
        HttpServletRequest request
    ) {
        // ✅ 로그에만 기록 (서버 내부)
        log.error("예상치 못한 에러 발생: path={}, user={}",
            request.getRequestURI(),
            request.getRemoteUser(),
            e  // 로그에는 전체 스택 트레이스 포함
        );

        ErrorResponse.ErrorResponseBuilder builder = ErrorResponse.builder()
            .code("C999")
            .message("서버 에러가 발생했습니다")  // ✅ 간단한 메시지만
            .path(request.getRequestURI())
            .timestamp(LocalDateTime.now());

        // ✅ 개발 환경에서만 스택 트레이스 추가
        if (debugMode) {
            builder.exception(e.getClass().getSimpleName())
                   .trace(Arrays.stream(e.getStackTrace())
                       .limit(5)  // 최대 5줄
                       .map(StackTraceElement::toString)
                       .collect(Collectors.joining("\n")));
        }

        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(builder.build());
    }
}
```

**개발 환경 vs 운영 환경**:

```yaml
# application-dev.yml (개발 환경)
app:
  debug: true  # 스택 트레이스 포함

# application-prod.yml (운영 환경)
app:
  debug: false  # 스택 트레이스 제외
```

**응답 예시**:

```json
// 운영 환경 (안전)
{
  "code": "C999",
  "message": "서버 에러가 발생했습니다",
  "path": "/api/users/123",
  "timestamp": "2024-01-15T14:30:00"
}

// 개발 환경 (디버깅용)
{
  "code": "C999",
  "message": "서버 에러가 발생했습니다",
  "exception": "NullPointerException",
  "trace": "com.example.UserService.updateUser(UserService.java:78)\ncom.example.UserController.updateUser(UserController.java:45)",
  "path": "/api/users/123",
  "timestamp": "2024-01-15T14:30:00"
}
```

**정리**:
- **운영 환경**: 스택 트레이스 절대 노출 금지
- **개발 환경**: 디버깅을 위해 제한적으로 포함 가능
- **로그**: 서버 로그에는 전체 스택 트레이스 기록

---

#### Q5. 커스텀 Exception 계층 구조를 어떻게 설계하나요?

**답변**:

커스텀 Exception 계층 구조는 **도메인별 분류**와 **공통 속성 추상화**를 기반으로 설계합니다.

**설계 원칙**:
1. **최상위 비즈니스 예외 추상 클래스** 생성
2. **도메인별로 예외 그룹화** (Product, Order, Payment 등)
3. **ErrorCode enum으로 에러 코드 관리**
4. **재시도 가능 여부 등 공통 속성** 정의

**1단계: 최상위 비즈니스 예외**

```java
@Getter
public abstract class BusinessException extends RuntimeException {

    private final ErrorCode errorCode;

    public BusinessException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
    }

    public BusinessException(ErrorCode errorCode, Throwable cause) {
        super(errorCode.getMessage(), cause);
        this.errorCode = errorCode;
    }

    public boolean isRetryable() {
        return errorCode.isRetryable();
    }

    public HttpStatus getHttpStatus() {
        return errorCode.getHttpStatus();
    }
}
```

**2단계: ErrorCode enum**

```java
@Getter
public enum ErrorCode {

    // 공통 (C)
    INVALID_INPUT("C001", "입력값이 올바르지 않습니다", HttpStatus.BAD_REQUEST, false),
    UNAUTHORIZED("C002", "인증이 필요합니다", HttpStatus.UNAUTHORIZED, false),
    FORBIDDEN("C003", "권한이 없습니다", HttpStatus.FORBIDDEN, false),

    // 상품 (P)
    PRODUCT_NOT_FOUND("P001", "상품을 찾을 수 없습니다", HttpStatus.NOT_FOUND, false),
    PRODUCT_OUT_OF_STOCK("P002", "상품이 품절되었습니다", HttpStatus.CONFLICT, false),

    // 주문 (O)
    ORDER_NOT_FOUND("O001", "주문을 찾을 수 없습니다", HttpStatus.NOT_FOUND, false),
    ORDER_ALREADY_CANCELLED("O002", "이미 취소된 주문입니다", HttpStatus.CONFLICT, false),

    // 결제 (PAY)
    PAYMENT_FAILED("PAY001", "결제가 실패했습니다", HttpStatus.PAYMENT_REQUIRED, true),
    PAYMENT_NETWORK_ERROR("PAY002", "결제 통신 오류", HttpStatus.SERVICE_UNAVAILABLE, true);

    private final String code;
    private final String message;
    private final HttpStatus httpStatus;
    private final boolean retryable;

    ErrorCode(String code, String message, HttpStatus httpStatus, boolean retryable) {
        this.code = code;
        this.message = message;
        this.httpStatus = httpStatus;
        this.retryable = retryable;
    }
}
```

**3단계: 도메인별 예외 클래스**

```java
// 상품 도메인
public class ProductNotFoundException extends BusinessException {

    private final Long productId;

    public ProductNotFoundException(Long productId) {
        super(ErrorCode.PRODUCT_NOT_FOUND);
        this.productId = productId;
    }

    public Long getProductId() {
        return productId;
    }
}

public class ProductOutOfStockException extends BusinessException {

    private final Long productId;
    private final int requestedQuantity;
    private final int availableStock;

    public ProductOutOfStockException(Long productId, int requestedQuantity, int availableStock) {
        super(ErrorCode.PRODUCT_OUT_OF_STOCK);
        this.productId = productId;
        this.requestedQuantity = requestedQuantity;
        this.availableStock = availableStock;
    }

    public Long getProductId() { return productId; }
    public int getRequestedQuantity() { return requestedQuantity; }
    public int getAvailableStock() { return availableStock; }
}

// 결제 도메인
public class PaymentFailedException extends BusinessException {

    private final String paymentId;
    private final String reason;

    public PaymentFailedException(String paymentId, String reason) {
        super(ErrorCode.PAYMENT_FAILED);
        this.paymentId = paymentId;
        this.reason = reason;
    }

    public PaymentFailedException(String paymentId, String reason, Throwable cause) {
        super(ErrorCode.PAYMENT_FAILED, cause);
        this.paymentId = paymentId;
        this.reason = reason;
    }

    public String getPaymentId() { return paymentId; }
    public String getReason() { return reason; }
}
```

**계층 구조**:

```
Exception
  └─ RuntimeException
       └─ BusinessException (추상 클래스)
            ├─ ProductNotFoundException
            ├─ ProductOutOfStockException
            ├─ OrderNotFoundException
            ├─ OrderCancellationException
            ├─ PaymentFailedException
            └─ PaymentNetworkException
```

**ExceptionHandler 활용**:

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    // ✅ 공통 처리 (모든 비즈니스 예외)
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusinessException(
        BusinessException e,
        HttpServletRequest request
    ) {
        ErrorCode errorCode = e.getErrorCode();

        ErrorResponse response = ErrorResponse.builder()
            .code(errorCode.getCode())
            .message(errorCode.getMessage())
            .retryable(errorCode.isRetryable())
            .path(request.getRequestURI())
            .timestamp(LocalDateTime.now())
            .build();

        return ResponseEntity
            .status(errorCode.getHttpStatus())
            .body(response);
    }

    // ✅ 특정 예외만 상세 처리
    @ExceptionHandler(ProductOutOfStockException.class)
    public ResponseEntity<ErrorResponse> handleProductOutOfStock(
        ProductOutOfStockException e,
        HttpServletRequest request
    ) {
        String detail = String.format(
            "요청 수량: %d개, 재고: %d개",
            e.getRequestedQuantity(),
            e.getAvailableStock()
        );

        ErrorResponse response = ErrorResponse.builder()
            .code(e.getErrorCode().getCode())
            .message(e.getErrorCode().getMessage())
            .detail(detail)
            .retryable(false)
            .path(request.getRequestURI())
            .timestamp(LocalDateTime.now())
            .build();

        return ResponseEntity.status(HttpStatus.CONFLICT).body(response);
    }
}
```

**장점**:
1. **일관성**: 모든 비즈니스 예외를 통일된 방식으로 처리
2. **확장성**: 새 도메인 예외 추가 용이
3. **타입 안전성**: ErrorCode enum으로 오타 방지
4. **유지보수**: 에러 코드 중앙 관리

---

## 📝 핵심 정리

### Spring MVC 예외 처리 방법

| 방법 | 범위 | 사용 시기 |
|------|------|-----------|
| @ExceptionHandler (Controller) | 해당 Controller만 | Controller별 특수 처리 |
| @ControllerAdvice | 전역 (모든 Controller) | 공통 예외 처리 |
| ResponseEntityExceptionHandler | Spring 기본 예외 | Spring 예외 커스터마이징 |
| @ResponseStatus | 특정 예외에 고정 상태 | 간단한 예외 |

### HTTP 상태 코드 가이드

| 상태 코드 | 의미 | 예시 Exception |
|-----------|------|----------------|
| 400 Bad Request | 잘못된 요청 | IllegalArgumentException, MethodArgumentNotValidException |
| 401 Unauthorized | 인증 필요 | UnauthorizedException |
| 403 Forbidden | 권한 없음 | ForbiddenException |
| 404 Not Found | 리소스 없음 | ResourceNotFoundException |
| 409 Conflict | 충돌 | DuplicateResourceException |
| 500 Internal Server Error | 서버 에러 | Exception |

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] @ControllerAdvice로 전역 예외 처리
- [ ] 커스텀 Exception 계층 구조 설계
- [ ] ErrorCode enum으로 에러 코드 관리
- [ ] 통일된 ErrorResponse 형식
- [ ] 적절한 HTTP 상태 코드 사용
- [ ] 에러 로깅 (warn, error 레벨 구분)
- [ ] 재시도 가능 여부 표시

#### ❌ 하지 말아야 할 것
- [ ] Controller마다 중복된 예외 처리
- [ ] 기술적 에러 메시지 노출 (스택 트레이스)
- [ ] 모든 예외를 500으로 처리
- [ ] 예외 무시 (빈 catch 블록)
- [ ] Checked Exception 남발

---

**다음 장으로 이동**: [다음: 17장 - 인터셉터와 필터 →](SpringMVC-Part9-17-Interceptor-Filter.md)

**이전 장으로 돌아가기**: [← 이전: 15장 Part 2 - 파일 업로드 실무편](SpringMVC-Part7-15-2-File-Upload-Advanced.md)

**목차로 돌아가기**: [📚 전체 목차](README.md)
