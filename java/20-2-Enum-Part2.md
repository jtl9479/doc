# 20-2. Enum (열거형) Part 2: 기업 사례 및 주니어 개발자 시나리오

## 📚 기업 사례 (Company Case Studies)

실제 기업과 프레임워크에서 Enum이 어떻게 활용되는지 살펴보겠습니다.

---

## 🏢 기업 사례 1: Java의 표준 Enum - HTTP Status Code

### 📖 개요

HTTP 상태 코드는 웹 통신에서 필수적입니다. Java의 HTTP 클라이언트 라이브러리들은 Enum을 사용하여 200개 이상의 HTTP 상태 코드를 체계적으로 관리합니다.

### 💡 왜 Enum을 사용했을까?

- **타입 안정성**: 잘못된 상태 코드 사용 방지
- **그룹화**: 1xx, 2xx, 3xx, 4xx, 5xx로 카테고리 분류
- **의미 전달**: 숫자 대신 의미 있는 이름 사용
- **메서드 추가**: is2xxSuccessful(), is4xxClientError() 등

### 💻 실제 코드 구현

```java
/**
 * HTTP 상태 코드 Enum (실제 Spring의 HttpStatus 참고)
 */
enum HttpStatus {
    // 2xx Success
    OK(200, "OK", "요청이 성공했습니다."),
    CREATED(201, "Created", "리소스가 생성되었습니다."),
    ACCEPTED(202, "Accepted", "요청이 수락되었습니다."),
    NO_CONTENT(204, "No Content", "응답 본문이 없습니다."),

    // 3xx Redirection
    MOVED_PERMANENTLY(301, "Moved Permanently", "영구적으로 이동했습니다."),
    FOUND(302, "Found", "일시적으로 이동했습니다."),
    NOT_MODIFIED(304, "Not Modified", "수정되지 않았습니다."),

    // 4xx Client Error
    BAD_REQUEST(400, "Bad Request", "잘못된 요청입니다."),
    UNAUTHORIZED(401, "Unauthorized", "인증이 필요합니다."),
    FORBIDDEN(403, "Forbidden", "권한이 없습니다."),
    NOT_FOUND(404, "Not Found", "리소스를 찾을 수 없습니다."),
    METHOD_NOT_ALLOWED(405, "Method Not Allowed", "허용되지 않은 메서드입니다."),
    CONFLICT(409, "Conflict", "리소스 충돌이 발생했습니다."),

    // 5xx Server Error
    INTERNAL_SERVER_ERROR(500, "Internal Server Error", "서버 오류가 발생했습니다."),
    NOT_IMPLEMENTED(501, "Not Implemented", "구현되지 않았습니다."),
    BAD_GATEWAY(502, "Bad Gateway", "잘못된 게이트웨이입니다."),
    SERVICE_UNAVAILABLE(503, "Service Unavailable", "서비스를 사용할 수 없습니다.");

    private final int code;
    private final String reasonPhrase;
    private final String koreanMessage;

    HttpStatus(int code, String reasonPhrase, String koreanMessage) {
        this.code = code;
        this.reasonPhrase = reasonPhrase;
        this.koreanMessage = koreanMessage;
    }

    public int getCode() {
        return code;
    }

    public String getReasonPhrase() {
        return reasonPhrase;
    }

    public String getKoreanMessage() {
        return koreanMessage;
    }

    // 상태 코드 카테고리 판별
    public boolean is1xxInformational() {
        return code >= 100 && code < 200;
    }

    public boolean is2xxSuccessful() {
        return code >= 200 && code < 300;
    }

    public boolean is3xxRedirection() {
        return code >= 300 && code < 400;
    }

    public boolean is4xxClientError() {
        return code >= 400 && code < 500;
    }

    public boolean is5xxServerError() {
        return code >= 500 && code < 600;
    }

    public boolean isError() {
        return is4xxClientError() || is5xxServerError();
    }

    // 상태 코드로 Enum 찾기
    public static HttpStatus valueOf(int statusCode) {
        for (HttpStatus status : values()) {
            if (status.code == statusCode) {
                return status;
            }
        }
        throw new IllegalArgumentException("No matching constant for [" + statusCode + "]");
    }

    // 카테고리별 조회
    public static HttpStatus[] getSuccessStatuses() {
        return java.util.Arrays.stream(values())
            .filter(HttpStatus::is2xxSuccessful)
            .toArray(HttpStatus[]::new);
    }

    @Override
    public String toString() {
        return code + " " + reasonPhrase;
    }
}

/**
 * HTTP 응답 클래스
 */
class HttpResponse {
    private HttpStatus status;
    private String body;
    private java.util.Map<String, String> headers;

    public HttpResponse(HttpStatus status, String body) {
        this.status = status;
        this.body = body;
        this.headers = new java.util.HashMap<>();
    }

    public void addHeader(String key, String value) {
        headers.put(key, value);
    }

    public void printResponse() {
        System.out.println("\n" + "=".repeat(60));
        System.out.println("HTTP Response");
        System.out.println("=".repeat(60));
        System.out.println("Status: " + status);
        System.out.println("Message: " + status.getKoreanMessage());

        if (!headers.isEmpty()) {
            System.out.println("\nHeaders:");
            headers.forEach((k, v) -> System.out.println("  " + k + ": " + v));
        }

        if (body != null && !body.isEmpty()) {
            System.out.println("\nBody:");
            System.out.println(body);
        }

        // 상태 분석
        System.out.println("\nAnalysis:");
        if (status.is2xxSuccessful()) {
            System.out.println("  ✅ 요청이 성공적으로 처리되었습니다.");
        } else if (status.is4xxClientError()) {
            System.out.println("  ⚠️  클라이언트 오류입니다. 요청을 확인하세요.");
        } else if (status.is5xxServerError()) {
            System.out.println("  ❌ 서버 오류입니다. 관리자에게 문의하세요.");
        } else if (status.is3xxRedirection()) {
            System.out.println("  🔄 리다이렉션이 필요합니다.");
        }
    }

    public HttpStatus getStatus() {
        return status;
    }
}

/**
 * REST API 컨트롤러 시뮬레이션
 */
class UserApiController {

    public HttpResponse getUser(int userId) {
        // 사용자 조회 시뮬레이션
        if (userId <= 0) {
            return new HttpResponse(
                HttpStatus.BAD_REQUEST,
                "{\"error\": \"Invalid user ID\"}"
            );
        }

        if (userId == 999) {
            return new HttpResponse(
                HttpStatus.NOT_FOUND,
                "{\"error\": \"User not found\"}"
            );
        }

        HttpResponse response = new HttpResponse(
            HttpStatus.OK,
            "{\"id\": " + userId + ", \"name\": \"홍길동\", \"email\": \"hong@example.com\"}"
        );
        response.addHeader("Content-Type", "application/json");
        return response;
    }

    public HttpResponse createUser(String name, String email) {
        // 사용자 생성 시뮬레이션
        if (name == null || name.isEmpty()) {
            return new HttpResponse(
                HttpStatus.BAD_REQUEST,
                "{\"error\": \"Name is required\"}"
            );
        }

        HttpResponse response = new HttpResponse(
            HttpStatus.CREATED,
            "{\"id\": 123, \"name\": \"" + name + "\", \"email\": \"" + email + "\"}"
        );
        response.addHeader("Location", "/users/123");
        response.addHeader("Content-Type", "application/json");
        return response;
    }

    public HttpResponse deleteUser(int userId) {
        // 사용자 삭제 시뮬레이션
        if (userId == 1) {
            return new HttpResponse(
                HttpStatus.FORBIDDEN,
                "{\"error\": \"Cannot delete admin user\"}"
            );
        }

        return new HttpResponse(HttpStatus.NO_CONTENT, "");
    }
}
```

### 🧪 테스트 코드

```java
/**
 * HTTP Status Enum 테스트
 */
public class HttpStatusTest {

    public static void main(String[] args) {

        System.out.println("===================================================");
        System.out.println("HTTP Status Code Enum 테스트");
        System.out.println("===================================================");

        // 테스트 1: 상태 코드 카테고리
        test1_StatusCategories();

        // 테스트 2: REST API 시뮬레이션
        test2_RestApiSimulation();

        // 테스트 3: 에러 처리
        test3_ErrorHandling();

        // 테스트 4: 상태 코드로 Enum 찾기
        test4_ValueOfByCode();
    }

    static void test1_StatusCategories() {
        System.out.println("\n### 테스트 1: 상태 코드 카테고리 ###\n");

        HttpStatus[] statuses = {
            HttpStatus.OK,
            HttpStatus.CREATED,
            HttpStatus.MOVED_PERMANENTLY,
            HttpStatus.BAD_REQUEST,
            HttpStatus.INTERNAL_SERVER_ERROR
        };

        for (HttpStatus status : statuses) {
            System.out.println(status + ":");
            System.out.println("  Success: " + status.is2xxSuccessful());
            System.out.println("  Redirection: " + status.is3xxRedirection());
            System.out.println("  Client Error: " + status.is4xxClientError());
            System.out.println("  Server Error: " + status.is5xxServerError());
            System.out.println();
        }
    }

    static void test2_RestApiSimulation() {
        System.out.println("\n### 테스트 2: REST API 시뮬레이션 ###");

        UserApiController controller = new UserApiController();

        // 정상 조회
        System.out.println("\n[GET /users/1]");
        HttpResponse response1 = controller.getUser(1);
        response1.printResponse();

        // 사용자 생성
        System.out.println("\n[POST /users]");
        HttpResponse response2 = controller.createUser("김철수", "kim@example.com");
        response2.printResponse();

        // 사용자 삭제
        System.out.println("\n[DELETE /users/10]");
        HttpResponse response3 = controller.deleteUser(10);
        response3.printResponse();
    }

    static void test3_ErrorHandling() {
        System.out.println("\n### 테스트 3: 에러 처리 ###");

        UserApiController controller = new UserApiController();

        // 잘못된 요청
        System.out.println("\n[GET /users/0]");
        HttpResponse response1 = controller.getUser(0);
        response1.printResponse();

        // 리소스 없음
        System.out.println("\n[GET /users/999]");
        HttpResponse response2 = controller.getUser(999);
        response2.printResponse();

        // 권한 없음
        System.out.println("\n[DELETE /users/1]");
        HttpResponse response3 = controller.deleteUser(1);
        response3.printResponse();

        // 필수 필드 누락
        System.out.println("\n[POST /users] (name 누락)");
        HttpResponse response4 = controller.createUser("", "test@example.com");
        response4.printResponse();
    }

    static void test4_ValueOfByCode() {
        System.out.println("\n### 테스트 4: 상태 코드로 Enum 찾기 ###\n");

        int[] codes = {200, 201, 404, 500};

        for (int code : codes) {
            HttpStatus status = HttpStatus.valueOf(code);
            System.out.println(code + " → " + status.getReasonPhrase() +
                             " (" + status.getKoreanMessage() + ")");
        }

        // 잘못된 코드
        System.out.println("\n잘못된 코드 조회:");
        try {
            HttpStatus.valueOf(999);
        } catch (IllegalArgumentException e) {
            System.out.println("  에러: " + e.getMessage());
        }
    }
}
```

### 🎯 핵심 포인트

1. **실무 활용**: REST API에서 필수적으로 사용
2. **카테고리 메서드**: is2xxSuccessful() 등으로 쉽게 판별
3. **valueOf 오버로딩**: 이름뿐만 아니라 코드로도 조회
4. **풍부한 정보**: 코드, 이유, 메시지를 함께 관리

---

## 🏢 기업 사례 2: 로그 레벨 (Logging Level)

### 📖 개요

Log4j, SLF4J, Logback 등 모든 로깅 프레임워크는 로그 레벨을 Enum으로 정의합니다. 로그의 중요도를 구분하고, 레벨에 따라 출력 여부를 결정합니다.

### 💡 왜 Enum을 사용했을까?

- **계층 구조**: TRACE < DEBUG < INFO < WARN < ERROR
- **필터링**: 특정 레벨 이상만 출력
- **타입 안정성**: 잘못된 레벨 사용 방지
- **성능**: ordinal()로 빠른 비교

### 💻 실제 코드 구현

```java
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * 로그 레벨 Enum (실제 SLF4J의 Level 참고)
 */
enum LogLevel {
    TRACE(0, "TRACE", "🔍", "상세한 추적 정보"),
    DEBUG(1, "DEBUG", "🐛", "디버깅 정보"),
    INFO(2, "INFO", "ℹ️", "일반 정보"),
    WARN(3, "WARN", "⚠️", "경고"),
    ERROR(4, "ERROR", "❌", "오류"),
    FATAL(5, "FATAL", "💀", "치명적 오류");

    private final int severity;
    private final String name;
    private final String emoji;
    private final String description;

    LogLevel(int severity, String name, String emoji, String description) {
        this.severity = severity;
        this.name = name;
        this.emoji = emoji;
        this.description = description;
    }

    public int getSeverity() {
        return severity;
    }

    public String getEmoji() {
        return emoji;
    }

    public String getDescription() {
        return description;
    }

    // 레벨 비교
    public boolean isGreaterOrEqual(LogLevel other) {
        return this.severity >= other.severity;
    }

    public boolean isLessThan(LogLevel other) {
        return this.severity < other.severity;
    }

    // ANSI 색상 코드
    public String getColor() {
        switch (this) {
            case TRACE: return "\u001B[37m";  // White
            case DEBUG: return "\u001B[36m";  // Cyan
            case INFO: return "\u001B[32m";   // Green
            case WARN: return "\u001B[33m";   // Yellow
            case ERROR: return "\u001B[31m";  // Red
            case FATAL: return "\u001B[35m";  // Magenta
            default: return "\u001B[0m";      // Reset
        }
    }

    public static final String RESET = "\u001B[0m";
}

/**
 * 로그 메시지 클래스
 */
class LogMessage {
    private LogLevel level;
    private String message;
    private String loggerName;
    private LocalDateTime timestamp;
    private String threadName;
    private Throwable throwable;

    public LogMessage(LogLevel level, String loggerName, String message) {
        this.level = level;
        this.loggerName = loggerName;
        this.message = message;
        this.timestamp = LocalDateTime.now();
        this.threadName = Thread.currentThread().getName();
    }

    public LogMessage withThrowable(Throwable throwable) {
        this.throwable = throwable;
        return this;
    }

    public LogLevel getLevel() {
        return level;
    }

    public String format() {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS");

        StringBuilder sb = new StringBuilder();
        sb.append(level.getColor());
        sb.append(timestamp.format(formatter));
        sb.append(" ");
        sb.append(level.getEmoji()).append(" ");
        sb.append(String.format("%-5s", level.name()));
        sb.append(" [").append(threadName).append("]");
        sb.append(" ").append(loggerName);
        sb.append(" - ").append(message);
        sb.append(LogLevel.RESET);

        if (throwable != null) {
            sb.append("\n");
            sb.append(throwable.getClass().getName());
            sb.append(": ");
            sb.append(throwable.getMessage());
        }

        return sb.toString();
    }
}

/**
 * Logger 클래스
 */
class Logger {
    private String name;
    private LogLevel currentLevel;
    private List<LogMessage> logHistory;

    public Logger(String name) {
        this.name = name;
        this.currentLevel = LogLevel.INFO;  // 기본 레벨
        this.logHistory = new ArrayList<>();
    }

    public void setLevel(LogLevel level) {
        this.currentLevel = level;
        System.out.println("\n📝 로그 레벨 변경: " + name + " → " + level.name());
    }

    private void log(LogLevel level, String message) {
        // 현재 레벨보다 낮으면 무시
        if (level.isLessThan(currentLevel)) {
            return;
        }

        LogMessage logMessage = new LogMessage(level, name, message);
        logHistory.add(logMessage);
        System.out.println(logMessage.format());
    }

    private void log(LogLevel level, String message, Throwable throwable) {
        if (level.isLessThan(currentLevel)) {
            return;
        }

        LogMessage logMessage = new LogMessage(level, name, message).withThrowable(throwable);
        logHistory.add(logMessage);
        System.out.println(logMessage.format());
    }

    public void trace(String message) {
        log(LogLevel.TRACE, message);
    }

    public void debug(String message) {
        log(LogLevel.DEBUG, message);
    }

    public void info(String message) {
        log(LogLevel.INFO, message);
    }

    public void warn(String message) {
        log(LogLevel.WARN, message);
    }

    public void error(String message) {
        log(LogLevel.ERROR, message);
    }

    public void error(String message, Throwable throwable) {
        log(LogLevel.ERROR, message, throwable);
    }

    public void fatal(String message) {
        log(LogLevel.FATAL, message);
    }

    // 통계
    public void printStatistics() {
        System.out.println("\n" + "=".repeat(60));
        System.out.println("로그 통계: " + name);
        System.out.println("=".repeat(60));

        Map<LogLevel, Long> counts = new HashMap<>();
        for (LogMessage msg : logHistory) {
            counts.put(msg.getLevel(), counts.getOrDefault(msg.getLevel(), 0L) + 1);
        }

        for (LogLevel level : LogLevel.values()) {
            long count = counts.getOrDefault(level, 0L);
            if (count > 0) {
                System.out.println(level.getEmoji() + " " + level.name() + ": " + count + "건");
            }
        }

        System.out.println("\n총 로그: " + logHistory.size() + "건");
    }
}

/**
 * 애플리케이션 시뮬레이션
 */
class Application {
    private Logger logger;

    public Application() {
        this.logger = new Logger("com.example.Application");
    }

    public void start() {
        logger.info("애플리케이션 시작");

        logger.debug("설정 파일 로드 중...");
        loadConfiguration();

        logger.debug("데이터베이스 연결 중...");
        connectDatabase();

        logger.info("애플리케이션이 준비되었습니다.");
    }

    private void loadConfiguration() {
        logger.trace("config.properties 파일 읽기");
        logger.trace("환경 변수 로드");
        logger.debug("설정 로드 완료");
    }

    private void connectDatabase() {
        logger.trace("데이터베이스 드라이버 초기화");
        logger.debug("연결 풀 생성 (크기: 10)");
        logger.info("데이터베이스 연결 성공");
    }

    public void processRequest(int userId) {
        logger.info("사용자 요청 처리 시작: userId=" + userId);

        if (userId <= 0) {
            logger.warn("잘못된 사용자 ID: " + userId);
            return;
        }

        try {
            // 사용자 조회 시뮬레이션
            logger.debug("사용자 정보 조회: userId=" + userId);

            if (userId == 999) {
                logger.error("사용자를 찾을 수 없습니다: userId=" + userId);
                throw new RuntimeException("User not found");
            }

            logger.info("요청 처리 완료: userId=" + userId);

        } catch (Exception e) {
            logger.error("요청 처리 중 오류 발생", e);
        }
    }

    public void shutdown() {
        logger.info("애플리케이션 종료 중...");
        logger.debug("리소스 정리");
        logger.info("애플리케이션 종료 완료");
    }

    public Logger getLogger() {
        return logger;
    }
}
```

### 🧪 테스트 코드

```java
/**
 * 로그 레벨 Enum 테스트
 */
public class LogLevelTest {

    public static void main(String[] args) {

        System.out.println("===================================================");
        System.out.println("로그 레벨 (LogLevel) Enum 테스트");
        System.out.println("===================================================");

        // 테스트 1: 모든 로그 레벨
        test1_AllLogLevels();

        // 테스트 2: 레벨별 필터링
        test2_LevelFiltering();

        // 테스트 3: 실제 애플리케이션 로깅
        test3_ApplicationLogging();

        // 테스트 4: 로그 통계
        test4_LogStatistics();
    }

    static void test1_AllLogLevels() {
        System.out.println("\n### 테스트 1: 모든 로그 레벨 ###\n");

        Logger logger = new Logger("TestLogger");
        logger.setLevel(LogLevel.TRACE);  // 모든 레벨 출력

        logger.trace("이것은 TRACE 레벨 로그입니다.");
        logger.debug("이것은 DEBUG 레벨 로그입니다.");
        logger.info("이것은 INFO 레벨 로그입니다.");
        logger.warn("이것은 WARN 레벨 로그입니다.");
        logger.error("이것은 ERROR 레벨 로그입니다.");
        logger.fatal("이것은 FATAL 레벨 로그입니다.");
    }

    static void test2_LevelFiltering() {
        System.out.println("\n### 테스트 2: 레벨별 필터링 ###");

        // INFO 레벨로 설정 (TRACE, DEBUG는 출력 안 됨)
        System.out.println("\n[로그 레벨: INFO]");
        Logger logger = new Logger("FilterLogger");
        logger.setLevel(LogLevel.INFO);

        logger.trace("이 메시지는 출력되지 않습니다.");
        logger.debug("이 메시지도 출력되지 않습니다.");
        logger.info("이 메시지는 출력됩니다.");
        logger.warn("이 메시지도 출력됩니다.");
        logger.error("이 메시지도 출력됩니다.");

        // WARN 레벨로 변경
        System.out.println("\n[로그 레벨: WARN]");
        logger.setLevel(LogLevel.WARN);

        logger.info("이 메시지는 출력되지 않습니다.");
        logger.warn("이 메시지는 출력됩니다.");
        logger.error("이 메시지도 출력됩니다.");
    }

    static void test3_ApplicationLogging() {
        System.out.println("\n### 테스트 3: 실제 애플리케이션 로깅 ###");

        Application app = new Application();
        app.getLogger().setLevel(LogLevel.DEBUG);

        app.start();

        app.processRequest(1);
        app.processRequest(0);    // 경고
        app.processRequest(999);  // 오류

        app.shutdown();
    }

    static void test4_LogStatistics() {
        System.out.println("\n### 테스트 4: 로그 통계 ###");

        Application app = new Application();
        app.getLogger().setLevel(LogLevel.TRACE);

        app.start();
        app.processRequest(1);
        app.processRequest(2);
        app.processRequest(0);
        app.processRequest(999);
        app.shutdown();

        app.getLogger().printStatistics();
    }
}
```

### 🎯 핵심 포인트

1. **계층적 레벨**: TRACE < DEBUG < INFO < WARN < ERROR < FATAL
2. **필터링**: 현재 레벨 이상만 출력하여 성능 최적화
3. **ordinal() 활용**: 레벨 비교를 정수 비교로 빠르게 처리
4. **실전 활용**: 모든 로깅 프레임워크의 핵심

---

## 🏢 기업 사례 3: 결제 상태 관리 시스템

### 📖 개요

이커머스 플랫폼에서 결제는 복잡한 상태 전이를 거칩니다. Enum을 사용하여 결제 상태와 허용되는 전이를 명확하게 정의합니다.

### 💡 왜 Enum을 사용했을까?

- **상태 머신**: 명확한 상태 전이 규칙
- **검증**: 잘못된 상태 전이 방지
- **비즈니스 로직**: 상태별 처리 로직 캡슐화
- **감사**: 모든 상태 변화 추적

### 💻 실제 코드 구현

```java
import java.time.LocalDateTime;
import java.util.*;

/**
 * 결제 상태 Enum
 */
enum PaymentStatus {
    READY("결제 준비", "결제가 준비되었습니다.") {
        @Override
        public Set<PaymentStatus> getAllowedTransitions() {
            return EnumSet.of(PENDING, CANCELLED);
        }

        @Override
        public boolean canCancel() {
            return true;
        }
    },

    PENDING("결제 대기", "결제 승인 대기 중입니다.") {
        @Override
        public Set<PaymentStatus> getAllowedTransitions() {
            return EnumSet.of(IN_PROGRESS, CANCELLED, FAILED);
        }

        @Override
        public boolean canCancel() {
            return true;
        }
    },

    IN_PROGRESS("결제 진행 중", "결제를 처리하고 있습니다.") {
        @Override
        public Set<PaymentStatus> getAllowedTransitions() {
            return EnumSet.of(COMPLETED, FAILED);
        }

        @Override
        public boolean canCancel() {
            return false;
        }
    },

    COMPLETED("결제 완료", "결제가 성공적으로 완료되었습니다.") {
        @Override
        public Set<PaymentStatus> getAllowedTransitions() {
            return EnumSet.of(REFUND_REQUESTED);
        }

        @Override
        public boolean canRefund() {
            return true;
        }
    },

    FAILED("결제 실패", "결제에 실패했습니다.") {
        @Override
        public Set<PaymentStatus> getAllowedTransitions() {
            return EnumSet.of(PENDING);  // 재시도 가능
        }
    },

    CANCELLED("결제 취소", "결제가 취소되었습니다.") {
        @Override
        public Set<PaymentStatus> getAllowedTransitions() {
            return EnumSet.noneOf(PaymentStatus.class);  // 최종 상태
        }

        @Override
        public boolean isFinalState() {
            return true;
        }
    },

    REFUND_REQUESTED("환불 요청", "환불이 요청되었습니다.") {
        @Override
        public Set<PaymentStatus> getAllowedTransitions() {
            return EnumSet.of(REFUND_IN_PROGRESS, REFUND_REJECTED);
        }
    },

    REFUND_IN_PROGRESS("환불 진행 중", "환불을 처리하고 있습니다.") {
        @Override
        public Set<PaymentStatus> getAllowedTransitions() {
            return EnumSet.of(REFUNDED, REFUND_FAILED);
        }
    },

    REFUNDED("환불 완료", "환불이 완료되었습니다.") {
        @Override
        public Set<PaymentStatus> getAllowedTransitions() {
            return EnumSet.noneOf(PaymentStatus.class);  // 최종 상태
        }

        @Override
        public boolean isFinalState() {
            return true;
        }
    },

    REFUND_REJECTED("환불 거부", "환불 요청이 거부되었습니다.") {
        @Override
        public Set<PaymentStatus> getAllowedTransitions() {
            return EnumSet.of(COMPLETED);  // 원래 상태로 복귀
        }
    },

    REFUND_FAILED("환불 실패", "환불 처리에 실패했습니다.") {
        @Override
        public Set<PaymentStatus> getAllowedTransitions() {
            return EnumSet.of(REFUND_IN_PROGRESS);  // 재시도 가능
        }
    };

    private final String koreanName;
    private final String message;

    PaymentStatus(String koreanName, String message) {
        this.koreanName = koreanName;
        this.message = message;
    }

    public String getKoreanName() {
        return koreanName;
    }

    public String getMessage() {
        return message;
    }

    // 각 상태는 허용되는 다음 상태들을 정의
    public abstract Set<PaymentStatus> getAllowedTransitions();

    // 상태 전이 가능 여부 확인
    public boolean canTransitionTo(PaymentStatus newStatus) {
        return getAllowedTransitions().contains(newStatus);
    }

    // 취소 가능 여부 (기본값: false)
    public boolean canCancel() {
        return false;
    }

    // 환불 가능 여부 (기본값: false)
    public boolean canRefund() {
        return false;
    }

    // 최종 상태 여부 (기본값: false)
    public boolean isFinalState() {
        return false;
    }

    // 상태 아이콘
    public String getIcon() {
        switch (this) {
            case READY: return "🆕";
            case PENDING: return "⏳";
            case IN_PROGRESS: return "⚙️";
            case COMPLETED: return "✅";
            case FAILED: return "❌";
            case CANCELLED: return "🚫";
            case REFUND_REQUESTED: return "📝";
            case REFUND_IN_PROGRESS: return "♻️";
            case REFUNDED: return "💰";
            case REFUND_REJECTED: return "⛔";
            case REFUND_FAILED: return "⚠️";
            default: return "❓";
        }
    }
}

/**
 * 결제 정보 클래스
 */
class Payment {
    private String paymentId;
    private String orderId;
    private int amount;
    private PaymentStatus status;
    private List<StatusTransition> history;
    private String paymentMethod;

    public Payment(String paymentId, String orderId, int amount, String paymentMethod) {
        this.paymentId = paymentId;
        this.orderId = orderId;
        this.amount = amount;
        this.paymentMethod = paymentMethod;
        this.status = PaymentStatus.READY;
        this.history = new ArrayList<>();
        addHistory(null, PaymentStatus.READY, "결제 생성");
    }

    // 상태 전이
    public boolean transitionTo(PaymentStatus newStatus, String reason) {
        if (!status.canTransitionTo(newStatus)) {
            System.out.println("⚠️  상태 전이 실패: " + status.getKoreanName() +
                             " → " + newStatus.getKoreanName());
            System.out.println("  허용되는 상태: " + status.getAllowedTransitions());
            return false;
        }

        PaymentStatus oldStatus = status;
        status = newStatus;
        addHistory(oldStatus, newStatus, reason);

        System.out.println("\n" + newStatus.getIcon() + " 결제 상태 변경");
        System.out.println("  " + oldStatus.getKoreanName() + " → " + newStatus.getKoreanName());
        System.out.println("  사유: " + reason);
        System.out.println("  " + newStatus.getMessage());

        return true;
    }

    private void addHistory(PaymentStatus from, PaymentStatus to, String reason) {
        history.add(new StatusTransition(from, to, reason, LocalDateTime.now()));
    }

    // 결제 취소
    public void cancel(String reason) {
        if (!status.canCancel()) {
            System.out.println("⚠️  현재 상태에서는 취소할 수 없습니다: " + status.getKoreanName());
            return;
        }

        transitionTo(PaymentStatus.CANCELLED, reason);
    }

    // 환불 요청
    public void requestRefund(String reason) {
        if (!status.canRefund()) {
            System.out.println("⚠️  현재 상태에서는 환불할 수 없습니다: " + status.getKoreanName());
            return;
        }

        transitionTo(PaymentStatus.REFUND_REQUESTED, reason);
    }

    // 결제 정보 출력
    public void printInfo() {
        System.out.println("\n" + "=".repeat(60));
        System.out.println("결제 정보");
        System.out.println("=".repeat(60));
        System.out.println("결제 ID: " + paymentId);
        System.out.println("주문 ID: " + orderId);
        System.out.println("금액: " + String.format("%,d원", amount));
        System.out.println("결제 수단: " + paymentMethod);
        System.out.println("현재 상태: " + status.getIcon() + " " + status.getKoreanName());
        System.out.println("취소 가능: " + (status.canCancel() ? "가능" : "불가능"));
        System.out.println("환불 가능: " + (status.canRefund() ? "가능" : "불가능"));
        System.out.println("최종 상태: " + (status.isFinalState() ? "예" : "아니오"));
    }

    // 상태 이력 출력
    public void printHistory() {
        System.out.println("\n상태 변경 이력:");
        for (int i = 0; i < history.size(); i++) {
            StatusTransition transition = history.get(i);
            System.out.println((i + 1) + ". " + transition);
        }
    }

    public PaymentStatus getStatus() {
        return status;
    }
}

/**
 * 상태 전이 기록
 */
class StatusTransition {
    private PaymentStatus from;
    private PaymentStatus to;
    private String reason;
    private LocalDateTime timestamp;

    public StatusTransition(PaymentStatus from, PaymentStatus to, String reason, LocalDateTime timestamp) {
        this.from = from;
        this.to = to;
        this.reason = reason;
        this.timestamp = timestamp;
    }

    @Override
    public String toString() {
        String fromStr = from == null ? "없음" : from.getKoreanName();
        return String.format("%s - %s → %s (%s)",
            timestamp.toString(), fromStr, to.getKoreanName(), reason);
    }
}
```

### 🧪 테스트 코드

```java
/**
 * 결제 상태 Enum 테스트
 */
public class PaymentStatusTest {

    public static void main(String[] args) {

        System.out.println("===================================================");
        System.out.println("결제 상태 관리 시스템 테스트");
        System.out.println("===================================================");

        // 테스트 1: 정상 결제 흐름
        test1_NormalPaymentFlow();

        // 테스트 2: 결제 취소
        test2_PaymentCancellation();

        // 테스트 3: 환불 프로세스
        test3_RefundProcess();

        // 테스트 4: 잘못된 상태 전이
        test4_InvalidTransitions();
    }

    static void test1_NormalPaymentFlow() {
        System.out.println("\n### 테스트 1: 정상 결제 흐름 ###");

        Payment payment = new Payment("PAY-001", "ORD-123", 50000, "신용카드");
        payment.printInfo();

        // READY → PENDING → IN_PROGRESS → COMPLETED
        payment.transitionTo(PaymentStatus.PENDING, "결제 승인 대기");
        payment.transitionTo(PaymentStatus.IN_PROGRESS, "결제 처리 시작");
        payment.transitionTo(PaymentStatus.COMPLETED, "결제 성공");

        payment.printInfo();
        payment.printHistory();
    }

    static void test2_PaymentCancellation() {
        System.out.println("\n\n### 테스트 2: 결제 취소 ###");

        // 시나리오 1: PENDING 상태에서 취소 (가능)
        System.out.println("\n[시나리오 1] PENDING 상태에서 취소");
        Payment payment1 = new Payment("PAY-002", "ORD-124", 30000, "카카오페이");
        payment1.transitionTo(PaymentStatus.PENDING, "결제 대기");
        payment1.cancel("사용자 요청");

        // 시나리오 2: IN_PROGRESS 상태에서 취소 시도 (불가능)
        System.out.println("\n[시나리오 2] IN_PROGRESS 상태에서 취소 시도");
        Payment payment2 = new Payment("PAY-003", "ORD-125", 40000, "네이버페이");
        payment2.transitionTo(PaymentStatus.PENDING, "결제 대기");
        payment2.transitionTo(PaymentStatus.IN_PROGRESS, "결제 처리 중");
        payment2.cancel("사용자 요청");  // 실패
    }

    static void test3_RefundProcess() {
        System.out.println("\n\n### 테스트 3: 환불 프로세스 ###");

        Payment payment = new Payment("PAY-004", "ORD-126", 100000, "신용카드");

        // 결제 완료까지
        payment.transitionTo(PaymentStatus.PENDING, "결제 승인 대기");
        payment.transitionTo(PaymentStatus.IN_PROGRESS, "결제 처리 중");
        payment.transitionTo(PaymentStatus.COMPLETED, "결제 완료");

        // 환불 프로세스
        payment.requestRefund("단순 변심");
        payment.transitionTo(PaymentStatus.REFUND_IN_PROGRESS, "환불 처리 시작");
        payment.transitionTo(PaymentStatus.REFUNDED, "환불 완료");

        payment.printInfo();
        payment.printHistory();
    }

    static void test4_InvalidTransitions() {
        System.out.println("\n\n### 테스트 4: 잘못된 상태 전이 ###");

        Payment payment = new Payment("PAY-005", "ORD-127", 60000, "토스페이");

        // READY → COMPLETED (직접 전이 불가)
        System.out.println("\n[시도 1] READY → COMPLETED (불가능)");
        payment.transitionTo(PaymentStatus.COMPLETED, "잘못된 전이");

        // 올바른 흐름
        payment.transitionTo(PaymentStatus.PENDING, "정상 전이");

        // PENDING → REFUNDED (직접 전이 불가)
        System.out.println("\n[시도 2] PENDING → REFUNDED (불가능)");
        payment.transitionTo(PaymentStatus.REFUNDED, "잘못된 전이");

        payment.printHistory();
    }
}
```

### 🎯 핵심 포인트

1. **상태 머신**: getAllowedTransitions()로 명확한 전이 규칙
2. **비즈니스 로직**: canCancel(), canRefund()로 도메인 규칙 표현
3. **검증**: canTransitionTo()로 잘못된 전이 방지
4. **감사 추적**: 모든 상태 변화를 이력으로 기록

---

## 👨‍💻 주니어 개발자 시나리오 (Junior Developer Scenarios)

실무에서 주니어 개발자들이 Enum을 사용할 때 자주 겪는 실수와 해결 방법을 알아보겠습니다.

---

## 🚫 시나리오 1: == vs equals() 혼동

### 📋 상황

주니어 개발자 김코드씨가 Enum을 비교할 때 언제 `==`를 쓰고 언제 `equals()`를 써야 할지 혼란스러워했습니다.

### ❓ 혼란스러운 상황

```java
enum Status {
    ACTIVE, INACTIVE, SUSPENDED
}

// 어느 것을 사용해야 할까?
Status status1 = Status.ACTIVE;
Status status2 = Status.ACTIVE;

// 방법 1: == 사용
if (status1 == status2) {
    System.out.println("같음");
}

// 방법 2: equals() 사용
if (status1.equals(status2)) {
    System.out.println("같음");
}

// 개발자의 고민:
// "둘 다 되는 것 같은데, 뭐가 정답인가요?"
// "String은 equals()를 쓰라고 배웠는데 Enum도 그래야 하나요?"
```

### ✅ 올바른 답변과 예제

```java
enum Status {
    ACTIVE, INACTIVE, SUSPENDED
}

/**
 * Enum 비교 방법 테스트
 */
public class EnumComparisonCorrect {

    public static void main(String[] args) {

        System.out.println("=== Enum 비교: == vs equals() ===\n");

        Status status1 = Status.ACTIVE;
        Status status2 = Status.ACTIVE;
        Status status3 = getStatusFromString("ACTIVE");

        // ✅ 권장: == 사용
        System.out.println("### 권장 방법: == 사용 ###\n");

        if (status1 == status2) {
            System.out.println("✓ status1 == status2: true");
        }

        if (status1 == status3) {
            System.out.println("✓ status1 == status3: true");
        }

        // ⚠️  가능하지만 불필요: equals() 사용
        System.out.println("\n### equals()도 작동은 함 (하지만 불필요) ###\n");

        if (status1.equals(status2)) {
            System.out.println("✓ status1.equals(status2): true");
        }

        // ❌ 위험: null 체크 없이 equals() 사용
        System.out.println("\n### equals()의 위험성 ###\n");

        Status nullStatus = null;

        try {
            if (nullStatus.equals(Status.ACTIVE)) {  // ❌ NullPointerException!
                System.out.println("같음");
            }
        } catch (NullPointerException e) {
            System.out.println("✗ NullPointerException 발생!");
        }

        // ✅ == 은 null-safe
        if (nullStatus == Status.ACTIVE) {  // ✅ 예외 없이 false 반환
            System.out.println("같음");
        } else {
            System.out.println("✓ null-safe: == 은 예외 없이 false 반환");
        }

        // 성능 비교
        performanceComparison();
    }

    static Status getStatusFromString(String name) {
        return Status.valueOf(name);
    }

    static void performanceComparison() {
        System.out.println("\n### 성능 비교 ###\n");

        Status status1 = Status.ACTIVE;
        Status status2 = Status.ACTIVE;

        // == 은 참조 비교 (매우 빠름)
        long start1 = System.nanoTime();
        for (int i = 0; i < 1000000; i++) {
            boolean result = status1 == status2;
        }
        long time1 = System.nanoTime() - start1;

        // equals()는 메서드 호출 (약간 느림)
        long start2 = System.nanoTime();
        for (int i = 0; i < 1000000; i++) {
            boolean result = status1.equals(status2);
        }
        long time2 = System.nanoTime() - start2;

        System.out.println("== 소요 시간: " + time1 + " ns");
        System.out.println("equals() 소요 시간: " + time2 + " ns");
        System.out.println("\n== 이 약 " + (time2 / time1) + "배 빠릅니다.");
    }
}
```

### 📚 배운 내용

**Enum 비교는 `==`을 사용하세요!**

**이유:**

1. **Enum은 싱글톤**
   - 각 Enum 상수는 JVM에서 딱 하나만 존재
   - 같은 상수는 항상 같은 객체

2. **null-safe**
   - `==`는 null이어도 예외가 발생하지 않음
   - `equals()`는 NullPointerException 위험

3. **성능**
   - `==`는 참조 비교로 매우 빠름
   - `equals()`는 메서드 호출 오버헤드

4. **가독성**
   - `==`가 더 간결하고 명확

**정리:**

| 구분 | == | equals() |
|------|-----|----------|
| Enum 비교 | ✅ 권장 | ⚠️  불필요 |
| null-safe | ✅ 안전 | ❌ NPE 위험 |
| 성능 | ⚡ 빠름 | 🐌 약간 느림 |
| 가독성 | ✅ 명확 | ⚠️  장황 |

---

## 🚫 시나리오 2: valueOf()와 예외 처리 누락

### 📋 상황

주니어 개발자 박자바씨가 사용자 입력을 Enum으로 변환하다가 예외가 발생하여 프로그램이 죽었습니다.

### ❌ 잘못된 코드

```java
enum OrderStatus {
    PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
}

public class OrderProcessorWrong {

    public static void main(String[] args) {

        // ❌ 문제: 예외 처리 없이 valueOf() 사용
        String userInput = "PENDNG";  // 오타!

        OrderStatus status = OrderStatus.valueOf(userInput);  // 💥 IllegalArgumentException!

        System.out.println("주문 상태: " + status);

        // 개발자의 생각:
        // "사용자가 정확히 입력할 거라고 생각했어요..."
        // "예외가 발생할 줄 몰랐습니다."
    }
}
```

### 💥 에러 메시지

```
Exception in thread "main" java.lang.IllegalArgumentException:
No enum constant OrderStatus.PENDNG
```

### ✅ 올바른 코드

```java
import java.util.Optional;

enum OrderStatus {
    PENDING("대기 중"),
    CONFIRMED("확인됨"),
    SHIPPED("배송 중"),
    DELIVERED("배송 완료"),
    CANCELLED("취소됨");

    private final String koreanName;

    OrderStatus(String koreanName) {
        this.koreanName = koreanName;
    }

    public String getKoreanName() {
        return koreanName;
    }

    // ✅ 방법 1: 안전한 valueOf (예외 처리)
    public static OrderStatus safeValueOf(String name) {
        try {
            return valueOf(name.toUpperCase());
        } catch (IllegalArgumentException e) {
            System.out.println("⚠️  잘못된 상태: " + name);
            return null;
        }
    }

    // ✅ 방법 2: Optional 반환
    public static Optional<OrderStatus> fromString(String name) {
        try {
            return Optional.of(valueOf(name.toUpperCase()));
        } catch (IllegalArgumentException e) {
            return Optional.empty();
        }
    }

    // ✅ 방법 3: 기본값 제공
    public static OrderStatus fromStringOrDefault(String name, OrderStatus defaultValue) {
        try {
            return valueOf(name.toUpperCase());
        } catch (IllegalArgumentException e) {
            System.out.println("⚠️  잘못된 상태 '" + name + "', 기본값 사용: " + defaultValue);
            return defaultValue;
        }
    }

    // ✅ 방법 4: 모든 가능한 값 표시
    public static String getAllValidValues() {
        StringBuilder sb = new StringBuilder();
        for (OrderStatus status : values()) {
            sb.append(status.name()).append(" (").append(status.koreanName).append("), ");
        }
        return sb.substring(0, sb.length() - 2);
    }
}

public class OrderProcessorCorrect {

    public static void main(String[] args) {

        System.out.println("=== Enum valueOf() 안전하게 사용하기 ===\n");

        // 테스트 케이스
        String[] inputs = {"PENDING", "pending", "PENDNG", "INVALID", ""};

        for (String input : inputs) {
            System.out.println("\n입력: \"" + input + "\"");
            System.out.println("-".repeat(40));

            // 방법 1: 예외 처리
            OrderStatus status1 = OrderStatus.safeValueOf(input);
            if (status1 != null) {
                System.out.println("방법 1 (safeValueOf): " + status1.getKoreanName());
            } else {
                System.out.println("방법 1 (safeValueOf): 변환 실패");
            }

            // 방법 2: Optional 사용
            Optional<OrderStatus> status2 = OrderStatus.fromString(input);
            status2.ifPresentOrElse(
                s -> System.out.println("방법 2 (Optional): " + s.getKoreanName()),
                () -> System.out.println("방법 2 (Optional): 변환 실패")
            );

            // 방법 3: 기본값 제공
            OrderStatus status3 = OrderStatus.fromStringOrDefault(input, OrderStatus.PENDING);
            System.out.println("방법 3 (기본값): " + status3.getKoreanName());
        }

        // 사용 가능한 모든 값 표시
        System.out.println("\n\n사용 가능한 상태:");
        System.out.println(OrderStatus.getAllValidValues());
    }
}
```

### 📚 배운 내용

1. **valueOf()의 위험성**
   - 잘못된 문자열 입력 시 `IllegalArgumentException` 발생
   - 사용자 입력은 항상 검증 필요

2. **안전한 변환 방법**
   ```java
   // ❌ 위험
   OrderStatus status = OrderStatus.valueOf(userInput);

   // ✅ 안전 - try-catch
   try {
       OrderStatus status = OrderStatus.valueOf(userInput);
   } catch (IllegalArgumentException e) {
       // 에러 처리
   }

   // ✅ 더 나은 방법 - Optional
   Optional<OrderStatus> status = OrderStatus.fromString(userInput);
   status.ifPresent(s -> process(s));

   // ✅ 기본값 제공
   OrderStatus status = OrderStatus.fromStringOrDefault(userInput, OrderStatus.PENDING);
   ```

3. **대소문자 처리**
   - Enum 상수는 대문자 관례
   - 입력값을 `toUpperCase()`로 변환

4. **사용자 친화적 에러 메시지**
   - 잘못된 입력 시 가능한 값 목록 제공
   - 한글 이름으로 안내

---

## 🚫 시나리오 3: ordinal() 잘못 사용하기

### 📋 상황

주니어 개발자 최개발씨가 Enum의 `ordinal()` 값을 데이터베이스에 저장했는데, 나중에 Enum 순서가 바뀌면서 데이터가 꼬였습니다.

### ❌ 잘못된 코드

```java
enum Priority {
    LOW, MEDIUM, HIGH, URGENT  // ordinal: 0, 1, 2, 3
}

class Task {
    private String name;
    private Priority priority;

    public Task(String name, Priority priority) {
        this.name = name;
        this.priority = priority;
    }

    // ❌ 나쁜 방법: ordinal()을 DB에 저장
    public int getPriorityForDB() {
        return priority.ordinal();  // 0, 1, 2, 3
    }

    // ❌ 나쁜 방법: ordinal()로 복원
    public static Priority getPriorityFromDB(int ordinal) {
        return Priority.values()[ordinal];
    }
}

// 문제 상황!
// 개발자가 나중에 Enum 순서를 변경함:
// enum Priority {
//     URGENT, HIGH, MEDIUM, LOW  // ordinal: 0, 1, 2, 3 (순서 바뀜!)
// }
//
// 기존에 DB에 0으로 저장된 값은 LOW였는데,
// 이제 0은 URGENT가 되어버림!
```

### ✅ 올바른 코드

```java
enum Priority {
    LOW(1, "낮음", "#90EE90"),
    MEDIUM(2, "보통", "#FFD700"),
    HIGH(3, "높음", "#FFA500"),
    URGENT(4, "긴급", "#FF0000");

    // ✅ 명시적인 코드 사용 (ordinal 대신)
    private final int code;
    private final String koreanName;
    private final String colorCode;

    Priority(int code, String koreanName, String colorCode) {
        this.code = code;
        this.koreanName = koreanName;
        this.colorCode = colorCode;
    }

    public int getCode() {
        return code;
    }

    public String getKoreanName() {
        return koreanName;
    }

    public String getColorCode() {
        return colorCode;
    }

    // ✅ 코드로 Enum 찾기
    public static Priority fromCode(int code) {
        for (Priority priority : values()) {
            if (priority.code == code) {
                return priority;
            }
        }
        throw new IllegalArgumentException("Invalid priority code: " + code);
    }

    // ✅ 안전한 버전 (Optional)
    public static Optional<Priority> fromCodeSafe(int code) {
        for (Priority priority : values()) {
            if (priority.code == code) {
                return Optional.of(priority);
            }
        }
        return Optional.empty();
    }
}

class Task {
    private String name;
    private Priority priority;

    public Task(String name, Priority priority) {
        this.name = name;
        this.priority = priority;
    }

    // ✅ 좋은 방법: 명시적인 코드 사용
    public int getPriorityForDB() {
        return priority.getCode();  // 1, 2, 3, 4 (고정된 값)
    }

    // ✅ 좋은 방법: 코드로 복원
    public static Priority getPriorityFromDB(int code) {
        return Priority.fromCode(code);
    }

    public void printTask() {
        System.out.println("작업: " + name);
        System.out.println("우선순위: " + priority.getKoreanName() +
                         " (코드: " + priority.getCode() + ")");
        System.out.println("색상: " + priority.getColorCode());
    }
}

/**
 * ordinal() vs 명시적 코드 비교 테스트
 */
public class OrdinalProblemTest {

    public static void main(String[] args) {

        System.out.println("=== ordinal() 사용의 문제점 ===\n");

        // 현재 Enum 상태 출력
        System.out.println("### 현재 Enum 정의 ###\n");
        for (Priority p : Priority.values()) {
            System.out.println(p.name() + ":");
            System.out.println("  ordinal(): " + p.ordinal() + " (위험!)");
            System.out.println("  getCode(): " + p.getCode() + " (안전!)");
            System.out.println();
        }

        // 데이터베이스 시뮬레이션
        System.out.println("### 데이터베이스 저장 시뮬레이션 ###\n");

        Task task1 = new Task("긴급 버그 수정", Priority.URGENT);
        Task task2 = new Task("문서 작성", Priority.LOW);

        // DB에 저장
        System.out.println("[저장]");
        int code1 = task1.getPriorityForDB();
        int code2 = task2.getPriorityForDB();
        System.out.println("작업 1 우선순위 코드: " + code1);
        System.out.println("작업 2 우선순위 코드: " + code2);

        // DB에서 복원
        System.out.println("\n[복원]");
        Priority restored1 = Task.getPriorityFromDB(code1);
        Priority restored2 = Task.getPriorityFromDB(code2);
        System.out.println("작업 1 우선순위: " + restored1.getKoreanName());
        System.out.println("작업 2 우선순위: " + restored2.getKoreanName());

        // Enum 순서가 바뀌어도 안전함을 증명
        System.out.println("\n### 순서 변경에도 안전 ###");
        System.out.println("✅ 명시적 코드 사용 시:");
        System.out.println("  - Enum 순서를 바꿔도 코드 값은 그대로");
        System.out.println("  - 데이터 일관성 유지");
        System.out.println("\n❌ ordinal() 사용 시:");
        System.out.println("  - Enum 순서를 바꾸면 ordinal 값 변경");
        System.out.println("  - 기존 데이터와 불일치 발생");
    }
}
```

### 📚 배운 내용

1. **ordinal()을 절대 저장하지 마세요**
   - ordinal()은 Enum의 순서 (0, 1, 2, ...)
   - Enum 순서가 바뀌면 ordinal도 바뀜
   - 데이터베이스, 파일, API 응답 등에 사용 금지

2. **명시적인 코드 사용**
   ```java
   // ❌ 나쁨
   enum Status {
       ACTIVE, INACTIVE
   }
   int code = status.ordinal();  // 0 or 1

   // ✅ 좋음
   enum Status {
       ACTIVE(1), INACTIVE(2);
       private final int code;
       // ...
   }
   int code = status.getCode();  // 항상 1 or 2
   ```

3. **ordinal()의 유일한 용도**
   - EnumSet, EnumMap 내부 구현
   - 성능 최적화가 필요한 일부 경우
   - **일반 개발자는 거의 사용할 일 없음**

4. **실무 팁**
   - DB 저장: 명시적 코드 또는 name() 사용
   - API 응답: name() 또는 커스텀 필드 사용
   - 버전 관리: 코드 값은 절대 변경하지 않기

---

## 🚫 시나리오 4: 상수 클래스 대신 Enum 사용하지 않는 경우

### 📋 상황

주니어 개발자 정프로씨가 여전히 상수 클래스를 사용하고 있습니다. Enum의 장점을 모르고 있습니다.

### ❌ 잘못된 코드 (상수 클래스 사용)

```java
/**
 * ❌ 구식 방법: 상수 클래스
 */
class HttpStatusConstants {
    public static final int OK = 200;
    public static final int CREATED = 201;
    public static final int BAD_REQUEST = 400;
    public static final int NOT_FOUND = 404;
    public static final int INTERNAL_SERVER_ERROR = 500;

    // 문제점들:
    // 1. 타입 안정성 없음
    // 2. 그룹화 어려움
    // 3. 메서드 추가 불가
    // 4. 네임스페이스 오염
}

class ApiResponse {
    private int statusCode;
    private String body;

    public ApiResponse(int statusCode, String body) {
        this.statusCode = statusCode;
        this.body = body;
    }

    public void printResponse() {
        System.out.println("Status Code: " + statusCode);

        // ❌ 문제 1: 타입 안정성 없음
        // statusCode에 999 같은 잘못된 값이 들어갈 수 있음

        // ❌ 문제 2: 의미 전달 어려움
        if (statusCode == 200) {  // 숫자만 보고 의미 파악 어려움
            System.out.println("성공");
        } else if (statusCode >= 400 && statusCode < 500) {
            System.out.println("클라이언트 오류");
        } else if (statusCode >= 500) {
            System.out.println("서버 오류");
        }
    }
}

public class ConstantsClassProblem {
    public static void main(String[] args) {
        // ❌ 잘못된 값 허용
        ApiResponse response1 = new ApiResponse(999, "Invalid");

        // ❌ 오타 가능
        ApiResponse response2 = new ApiResponse(HttpStatusConstants.OK, "Success");

        // ❌ 매직 넘버
        ApiResponse response3 = new ApiResponse(200, "Success");

        response1.printResponse();
    }
}
```

### ✅ 올바른 코드 (Enum 사용)

```java
/**
 * ✅ 현대적 방법: Enum 사용
 */
enum HttpStatus {
    // 2xx Success
    OK(200, "OK") {
        @Override
        public String getAdvice() {
            return "요청이 성공적으로 처리되었습니다.";
        }
    },
    CREATED(201, "Created") {
        @Override
        public String getAdvice() {
            return "리소스가 성공적으로 생성되었습니다.";
        }
    },

    // 4xx Client Error
    BAD_REQUEST(400, "Bad Request") {
        @Override
        public String getAdvice() {
            return "요청이 잘못되었습니다. 입력값을 확인하세요.";
        }
    },
    NOT_FOUND(404, "Not Found") {
        @Override
        public String getAdvice() {
            return "요청한 리소스를 찾을 수 없습니다.";
        }
    },

    // 5xx Server Error
    INTERNAL_SERVER_ERROR(500, "Internal Server Error") {
        @Override
        public String getAdvice() {
            return "서버 오류입니다. 관리자에게 문의하세요.";
        }
    };

    private final int code;
    private final String message;

    HttpStatus(int code, String message) {
        this.code = code;
        this.message = message;
    }

    public int getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }

    // ✅ 추상 메서드 - 각 상태별 조언
    public abstract String getAdvice();

    // ✅ 카테고리 판별 메서드
    public boolean isSuccess() {
        return code >= 200 && code < 300;
    }

    public boolean isClientError() {
        return code >= 400 && code < 500;
    }

    public boolean isServerError() {
        return code >= 500 && code < 600;
    }

    // ✅ 상태 코드로 Enum 찾기
    public static HttpStatus fromCode(int code) {
        for (HttpStatus status : values()) {
            if (status.code == code) {
                return status;
            }
        }
        throw new IllegalArgumentException("Unknown status code: " + code);
    }

    @Override
    public String toString() {
        return code + " " + message;
    }
}

class ModernApiResponse {
    private HttpStatus status;  // ✅ int 대신 Enum
    private String body;

    public ModernApiResponse(HttpStatus status, String body) {
        this.status = status;
        this.body = body;
    }

    public void printResponse() {
        System.out.println("\n" + "=".repeat(50));
        System.out.println("API Response");
        System.out.println("=".repeat(50));
        System.out.println("Status: " + status);
        System.out.println("Body: " + body);

        // ✅ 가독성 높은 조건문
        if (status.isSuccess()) {
            System.out.println("✅ " + status.getAdvice());
        } else if (status.isClientError()) {
            System.out.println("⚠️  " + status.getAdvice());
        } else if (status.isServerError()) {
            System.out.println("❌ " + status.getAdvice());
        }
    }

    public HttpStatus getStatus() {
        return status;
    }
}

/**
 * 상수 클래스 vs Enum 비교
 */
public class EnumVsConstantsTest {

    public static void main(String[] args) {

        System.out.println("=================================================");
        System.out.println("상수 클래스 vs Enum 비교");
        System.out.println("=================================================");

        // ✅ Enum의 장점 1: 타입 안정성
        System.out.println("\n### 장점 1: 타입 안정성 ###");

        // ✅ 정해진 값만 허용
        ModernApiResponse response1 = new ModernApiResponse(HttpStatus.OK, "Success");
        // ❌ 컴파일 에러! 잘못된 값 불가
        // ModernApiResponse response2 = new ModernApiResponse(999, "Invalid");

        // ✅ Enum의 장점 2: 의미 있는 이름
        System.out.println("\n### 장점 2: 의미 있는 이름 ###");

        ModernApiResponse response2 = new ModernApiResponse(HttpStatus.NOT_FOUND, "User not found");
        response2.printResponse();

        // ✅ Enum의 장점 3: 메서드 추가
        System.out.println("\n### 장점 3: 메서드 추가 가능 ###");

        for (HttpStatus status : HttpStatus.values()) {
            System.out.println(status + " → " + status.getAdvice());
        }

        // ✅ Enum의 장점 4: switch 문과 완벽한 호환
        System.out.println("\n### 장점 4: switch 문 ###");

        HttpStatus testStatus = HttpStatus.BAD_REQUEST;
        handleResponse(testStatus);

        // ✅ Enum의 장점 5: 모든 값 순회
        System.out.println("\n### 장점 5: 모든 값 순회 ###");

        System.out.println("사용 가능한 모든 HTTP 상태:");
        for (HttpStatus status : HttpStatus.values()) {
            System.out.println("  - " + status);
        }

        // 비교 요약
        printComparison();
    }

    static void handleResponse(HttpStatus status) {
        switch (status) {
            case OK:
            case CREATED:
                System.out.println("✅ 성공 처리");
                break;
            case BAD_REQUEST:
                System.out.println("⚠️  잘못된 요청 처리");
                break;
            case NOT_FOUND:
                System.out.println("⚠️  리소스 없음 처리");
                break;
            case INTERNAL_SERVER_ERROR:
                System.out.println("❌ 서버 오류 처리");
                break;
        }
    }

    static void printComparison() {
        System.out.println("\n" + "=".repeat(60));
        System.out.println("비교 요약");
        System.out.println("=".repeat(60));

        System.out.println("\n상수 클래스의 문제점:");
        System.out.println("  ❌ 타입 안정성 없음 (int에 999 같은 값 가능)");
        System.out.println("  ❌ 의미 전달 어려움 (숫자만 보면 의미 불명확)");
        System.out.println("  ❌ 메서드 추가 불가 (단순 상수)");
        System.out.println("  ❌ 그룹화 어려움");
        System.out.println("  ❌ switch 문에서 실수 가능");

        System.out.println("\nEnum의 장점:");
        System.out.println("  ✅ 타입 안정성 (정해진 값만 허용)");
        System.out.println("  ✅ 의미 명확 (이름으로 의도 표현)");
        System.out.println("  ✅ 메서드 추가 가능");
        System.out.println("  ✅ 자연스러운 그룹화");
        System.out.println("  ✅ switch 문 완벽 지원");
        System.out.println("  ✅ values()로 모든 값 순회");
        System.out.println("  ✅ 싱글톤 보장");
    }
}
```

### 📚 배운 내용

**Enum을 사용해야 하는 이유:**

| 기능 | 상수 클래스 | Enum |
|------|-------------|------|
| **타입 안정성** | ❌ int로 아무 값이나 | ✅ 정해진 값만 |
| **의미 전달** | ❌ 숫자로만 | ✅ 명확한 이름 |
| **메서드** | ❌ 불가능 | ✅ 추가 가능 |
| **그룹화** | ❌ 어려움 | ✅ 자연스러움 |
| **switch** | ⚠️  가능하지만 위험 | ✅ 완벽 지원 |
| **모든 값 순회** | ❌ 불가능 | ✅ values() |
| **null 체크** | ❌ NPE 위험 | ✅ == 안전 |

**언제 Enum을 사용해야 하나?**

1. **고정된 상수 집합**
   ```java
   // ❌ 상수 클래스
   class Days {
       static final int MONDAY = 0;
       static final int TUESDAY = 1;
   }

   // ✅ Enum
   enum Day {
       MONDAY, TUESDAY, WEDNESDAY, ...
   }
   ```

2. **상태 또는 타입 표현**
   ```java
   enum OrderStatus { PENDING, CONFIRMED, SHIPPED }
   enum UserRole { ADMIN, USER, GUEST }
   enum PaymentMethod { CARD, CASH, PAYPAL }
   ```

3. **카테고리 분류**
   ```java
   enum Category { FOOD, ELECTRONICS, CLOTHING }
   enum Priority { LOW, MEDIUM, HIGH }
   ```

---

## 🎯 Part 2 핵심 정리

### 기업 사례에서 배운 점

1. **HTTP Status Code**
   - 카테고리별 그룹화 (2xx, 4xx, 5xx)
   - 의미 있는 이름과 메시지
   - is2xxSuccessful() 같은 편의 메서드

2. **로그 레벨**
   - 계층적 레벨 구조
   - ordinal()로 빠른 비교
   - 필터링 기능

3. **결제 상태 관리**
   - 상태 머신 구현
   - 허용된 전이만 가능
   - 감사 추적

### 주니어 개발자 주의사항

1. **== vs equals()**
   - Enum 비교는 `==` 사용
   - null-safe하고 빠름

2. **valueOf() 사용**
   - 항상 예외 처리
   - Optional 또는 기본값 고려

3. **ordinal() 금지**
   - DB, 파일, API에 절대 저장 금지
   - 명시적 코드 사용

4. **상수 클래스 대신 Enum**
   - 타입 안정성
   - 풍부한 기능

다음 Part 3에서는 **실전 프로젝트**, **FAQ**, **면접 질문**을 다루겠습니다! 🚀

