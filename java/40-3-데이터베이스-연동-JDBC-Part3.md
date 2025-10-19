# 40장 데이터베이스 연동 (JDBC) - Part 3: 면접 질문

> **학습 목표**: JDBC 면접 질문에 답변하고 베스트 프랙티스를 이해한다

**⏱️ 예상 학습 시간**: 2-3시간
**난이도**: ⭐⭐⭐⭐☆ (4/5)

---

## 🎤 주니어 면접 질문 (Junior Level)

### Q1. JDBC란 무엇이고 왜 사용하나요?

**모범 답변**:
```
JDBC (Java Database Connectivity):
- Java에서 데이터베이스에 접근하기 위한 표준 API
- 다양한 데이터베이스를 동일한 방식으로 사용 가능
- JDBC Driver를 통해 DB 벤더 독립적

구조:
Java 애플리케이션
    ↓
JDBC API (java.sql 패키지)
    ↓
JDBC Driver (MySQL, Oracle, PostgreSQL 등)
    ↓
데이터베이스
```

**코드 예시**:
```java
// JDBC 기본 사용 예시
public class JDBCExample {
    public static void main(String[] args) {
        String url = "jdbc:mysql://localhost:3306/testdb";
        String user = "root";
        String password = "root1234";

        try (Connection conn = DriverManager.getConnection(url, user, password);
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT * FROM users")) {

            while (rs.next()) {
                System.out.println("ID: " + rs.getInt("id"));
                System.out.println("Name: " + rs.getString("name"));
            }

        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

**꼬리 질문**:
- Q: JDBC Driver는 어떻게 추가하나요?
- A: Maven/Gradle 의존성 또는 JAR 파일 직접 추가
  ```xml
  <dependency>
      <groupId>mysql</groupId>
      <artifactId>mysql-connector-java</artifactId>
      <version>8.0.33</version>
  </dependency>
  ```

**실무 연관**:
- Spring Boot는 내부적으로 JDBC를 사용
- JPA/Hibernate도 JDBC 위에 구축된 ORM
- 복잡한 쿼리나 성능 최적화 시 JDBC 직접 사용

---

### Q2. Connection, Statement, ResultSet의 역할은?

**모범 답변**:
```
1. Connection:
   - 데이터베이스와의 연결
   - Transaction 제어
   - Statement 생성

2. Statement / PreparedStatement:
   - SQL 실행
   - 쿼리 결과 반환

3. ResultSet:
   - 쿼리 결과 집합
   - 커서 이동 (next())
   - 데이터 추출

라이프사이클:
Connection 생성 → Statement 생성 → 쿼리 실행 → ResultSet 반환
→ ResultSet 닫기 → Statement 닫기 → Connection 닫기
```

**코드 예시**:
```java
public class JDBCLifecycle {
    public static void main(String[] args) {
        String url = "jdbc:mysql://localhost:3306/testdb";

        Connection conn = null;
        Statement stmt = null;
        ResultSet rs = null;

        try {
            // 1. Connection 생성
            conn = DriverManager.getConnection(url, "root", "root1234");
            System.out.println("✅ Connection 생성");

            // 2. Statement 생성
            stmt = conn.createStatement();
            System.out.println("✅ Statement 생성");

            // 3. 쿼리 실행
            rs = stmt.executeQuery("SELECT * FROM users");
            System.out.println("✅ 쿼리 실행");

            // 4. ResultSet 처리
            while (rs.next()) {
                System.out.println("User: " + rs.getString("name"));
            }

        } catch (SQLException e) {
            e.printStackTrace();
        } finally {
            // 5. 리소스 닫기 (역순!)
            try {
                if (rs != null) rs.close();      // ResultSet 먼저
                if (stmt != null) stmt.close();  // Statement 다음
                if (conn != null) conn.close();  // Connection 마지막
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }
}
```

**꼬리 질문**:
- Q: 왜 역순으로 닫아야 하나요?
- A: Connection이 닫히면 연관된 Statement와 ResultSet도 자동으로 닫히므로, 명시적으로 닫을 때는 역순이 안전합니다.

**실무 연관**:
- try-with-resources로 자동 닫기 권장
- Connection Pool 사용 시 Connection은 Pool에 반환됨
- 리소스 누수 → 메모리 부족 → 서비스 장애

---

### Q3. PreparedStatement를 사용해야 하는 이유는?

**모범 답변**:
```
PreparedStatement 장점:
1. SQL Injection 방어
   - 파라미터 자동 이스케이프
   - 보안 향상

2. 성능 향상
   - SQL 1번만 컴파일
   - 반복 실행 시 빠름

3. 코드 가독성
   - ?로 파라미터 명확히 표시
   - 유지보수 용이

실무에서는 거의 항상 PreparedStatement 사용!
```

**코드 예시**:
```java
public class PreparedStatementExample {
    // ❌ Statement (위험!)
    public void loginWithStatement(String username, String password) {
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             Statement stmt = conn.createStatement()) {

            // SQL Injection 취약!
            String sql = "SELECT * FROM users WHERE username = '" + username +
                         "' AND password = '" + password + "'";

            ResultSet rs = stmt.executeQuery(sql);

            if (rs.next()) {
                System.out.println("✅ 로그인 성공");
            }

        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    // ✅ PreparedStatement (안전!)
    public void loginWithPreparedStatement(String username, String password) {
        String sql = "SELECT * FROM users WHERE username = ? AND password = ?";

        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            pstmt.setString(1, username);  // 자동 이스케이프
            pstmt.setString(2, password);

            ResultSet rs = pstmt.executeQuery();

            if (rs.next()) {
                System.out.println("✅ 로그인 성공");
            }

        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    // SQL Injection 공격 시연
    public static void main(String[] args) {
        PreparedStatementExample example = new PreparedStatementExample();

        // 정상 입력
        example.loginWithStatement("admin", "1234");

        // 악의적 입력 (SQL Injection)
        // username = "admin' OR '1'='1"
        // password = "anything"
        // → 결과: SELECT * FROM users WHERE username = 'admin' OR '1'='1' AND password = 'anything'
        // → 항상 true! (보안 취약)

        // PreparedStatement는 안전!
        example.loginWithPreparedStatement("admin' OR '1'='1", "anything");
        // → 파라미터가 문자열로 처리되어 SQL Injection 불가
    }
}
```

**성능 비교**:
```java
// 성능 테스트
public void performanceTest() {
    // Statement: 매번 컴파일
    long start = System.currentTimeMillis();
    for (int i = 0; i < 1000; i++) {
        String sql = "SELECT * FROM users WHERE id = " + i;
        stmt.executeQuery(sql);  // 1000번 컴파일!
    }
    long statementTime = System.currentTimeMillis() - start;

    // PreparedStatement: 1번만 컴파일
    String sql = "SELECT * FROM users WHERE id = ?";
    PreparedStatement pstmt = conn.prepareStatement(sql);
    start = System.currentTimeMillis();
    for (int i = 0; i < 1000; i++) {
        pstmt.setInt(1, i);
        pstmt.executeQuery();  // 1번만 컴파일!
    }
    long preparedTime = System.currentTimeMillis() - start;

    System.out.println("Statement: " + statementTime + "ms");
    System.out.println("PreparedStatement: " + preparedTime + "ms");
    // 결과: PreparedStatement가 2-3배 빠름!
}
```

**꼬리 질문**:
- Q: PreparedStatement는 언제 컴파일되나요?
- A: `conn.prepareStatement(sql)` 호출 시 컴파일되며, 이후 `setXXX()`로 파라미터만 바꿔 재사용합니다.

**실무 연관**:
- 모든 사용자 입력은 PreparedStatement로 처리
- MyBatis, JPA도 내부적으로 PreparedStatement 사용
- 보안 감사에서 Statement 사용 시 취약점으로 지적

---

### Q4. Transaction이란 무엇인가요? (ACID)

**모범 답변**:
```
Transaction:
- 하나의 논리적 작업 단위
- 전부 성공 또는 전부 실패 (All or Nothing)

ACID 속성:
1. Atomicity (원자성)
   - 전부 성공 또는 전부 실패
   - 일부만 실행 불가

2. Consistency (일관성)
   - 데이터 무결성 유지
   - 제약 조건 만족

3. Isolation (격리성)
   - 동시 실행 간섭 없음
   - 각 트랜잭션 독립 실행

4. Durability (지속성)
   - 커밋 후 영구 저장
   - 시스템 장애 시에도 유지
```

**코드 예시**:
```java
public class TransactionExample {
    // 계좌 이체 (Transaction 필수!)
    public void transfer(int fromAccountId, int toAccountId, int amount) {
        Connection conn = null;

        try {
            conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);

            // 트랜잭션 시작
            conn.setAutoCommit(false);

            // 1. 출금
            String debitSQL = "UPDATE accounts SET balance = balance - ? WHERE id = ?";
            try (PreparedStatement pstmt = conn.prepareStatement(debitSQL)) {
                pstmt.setInt(1, amount);
                pstmt.setInt(2, fromAccountId);
                pstmt.executeUpdate();
                System.out.println("✅ 출금: -" + amount + "원");
            }

            // 시뮬레이션: 중간에 예외 발생
            // if (Math.random() < 0.5) throw new SQLException("네트워크 오류");

            // 2. 입금
            String creditSQL = "UPDATE accounts SET balance = balance + ? WHERE id = ?";
            try (PreparedStatement pstmt = conn.prepareStatement(creditSQL)) {
                pstmt.setInt(1, amount);
                pstmt.setInt(2, toAccountId);
                pstmt.executeUpdate();
                System.out.println("✅ 입금: +" + amount + "원");
            }

            // 트랜잭션 커밋
            conn.commit();
            System.out.println("✅ 트랜잭션 커밋 (이체 완료)");

        } catch (SQLException e) {
            // 트랜잭션 롤백
            try {
                if (conn != null) {
                    conn.rollback();
                    System.out.println("❌ 트랜잭션 롤백 (이체 취소)");
                }
            } catch (SQLException ex) {
                ex.printStackTrace();
            }
            e.printStackTrace();

        } finally {
            try {
                if (conn != null) {
                    conn.setAutoCommit(true);  // 원래대로 복구
                    conn.close();
                }
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }

    public static void main(String[] args) {
        TransactionExample example = new TransactionExample();

        System.out.println("=== 이체 전 ===");
        System.out.println("계좌 1: 100,000원");
        System.out.println("계좌 2: 50,000원");

        example.transfer(1, 2, 10000);

        System.out.println("\n=== 이체 후 ===");
        System.out.println("계좌 1: 90,000원");
        System.out.println("계좌 2: 60,000원");
    }
}
```

**ACID 위반 시나리오**:
```java
// ❌ Transaction 없이 이체 (위험!)
public void transferWithoutTransaction(int fromId, int toId, int amount) {
    // 출금
    stmt.executeUpdate("UPDATE accounts SET balance = balance - " + amount +
                       " WHERE id = " + fromId);

    // 여기서 서버 다운! → 출금만 되고 입금 안 됨!
    // → Atomicity 위반!

    // 입금
    stmt.executeUpdate("UPDATE accounts SET balance = balance + " + amount +
                       " WHERE id = " + toId);
}
```

**꼬리 질문**:
- Q: autoCommit은 기본값이 true인가요 false인가요?
- A: 기본값은 `true`입니다. Transaction을 사용하려면 `setAutoCommit(false)`로 변경해야 합니다.

**실무 연관**:
- 금융 거래, 주문 처리, 재고 관리 등 필수
- Spring의 `@Transactional`이 내부적으로 JDBC Transaction 사용
- 분산 트랜잭션(2PC)은 더 복잡

---

### Q5. try-with-resources를 왜 사용해야 하나요?

**모범 답변**:
```
try-with-resources:
- AutoCloseable 리소스 자동 닫기
- finally 블록 불필요
- 예외 발생 시에도 안전하게 닫힘

장점:
1. 코드 간결성
   - finally 블록 제거
   - 가독성 향상

2. 안전성
   - 예외 발생 시에도 자동 닫기
   - 리소스 누수 방지

3. 순서 보장
   - 역순으로 자동 닫기
   - 의존성 관리 자동
```

**코드 예시**:
```java
public class TryWithResourcesExample {
    // ❌ 전통적 방식 (복잡!)
    public void queryWithoutTryWithResources() {
        Connection conn = null;
        Statement stmt = null;
        ResultSet rs = null;

        try {
            conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
            stmt = conn.createStatement();
            rs = stmt.executeQuery("SELECT * FROM users");

            while (rs.next()) {
                System.out.println(rs.getString("name"));
            }

        } catch (SQLException e) {
            e.printStackTrace();

        } finally {
            // 역순으로 닫기 (복잡!)
            try {
                if (rs != null) rs.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }

            try {
                if (stmt != null) stmt.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }

            try {
                if (conn != null) conn.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }

    // ✅ try-with-resources (간결!)
    public void queryWithTryWithResources() {
        String sql = "SELECT * FROM users";

        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {

            while (rs.next()) {
                System.out.println(rs.getString("name"));
            }

        } catch (SQLException e) {
            e.printStackTrace();
        }
        // 자동으로 rs → stmt → conn 순서로 닫힘!
    }

    // 다중 리소스 처리
    public void multipleResources() {
        String selectSQL = "SELECT * FROM users WHERE id = ?";
        String updateSQL = "UPDATE users SET last_login = NOW() WHERE id = ?";

        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement selectStmt = conn.prepareStatement(selectSQL);
             PreparedStatement updateStmt = conn.prepareStatement(updateSQL)) {

            selectStmt.setInt(1, 1);
            ResultSet rs = selectStmt.executeQuery();

            if (rs.next()) {
                System.out.println("User: " + rs.getString("name"));

                updateStmt.setInt(1, 1);
                updateStmt.executeUpdate();
            }

        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

**예외 처리 비교**:
```java
// 예외 발생 시 동작
public void exceptionHandling() {
    // ❌ 전통적 방식: rs.close()에서 예외 발생 시 stmt, conn이 안 닫힐 수 있음
    finally {
        try {
            if (rs != null) rs.close();  // 예외 발생!
            if (stmt != null) stmt.close();  // 실행 안 됨!
            if (conn != null) conn.close();  // 실행 안 됨!
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    // ✅ try-with-resources: 모든 리소스가 안전하게 닫힘
    try (Connection conn = ...;
         Statement stmt = ...;
         ResultSet rs = ...) {
        // ...
    }
    // rs, stmt, conn 모두 역순으로 안전하게 닫힘
}
```

**꼬리 질문**:
- Q: try-with-resources는 어떤 인터페이스를 구현해야 하나요?
- A: `AutoCloseable` 또는 `Closeable` 인터페이스를 구현해야 합니다. JDBC의 Connection, Statement, ResultSet 모두 구현되어 있습니다.

**실무 연관**:
- Java 7 이후 권장 패턴
- 리소스 누수 방지 → 안정적인 서비스 운영
- Connection Pool 사용 시에도 필수

---

### Q6. SQL Injection이 무엇이고 어떻게 방지하나요?

**모범 답변**:
```
SQL Injection:
- 악의적인 SQL 코드를 삽입하는 공격
- 데이터 유출, 삭제, 조작 가능
- OWASP Top 10 보안 취약점

공격 예시:
입력: admin' OR '1'='1
SQL: SELECT * FROM users WHERE username = 'admin' OR '1'='1' AND password = '...'
결과: 항상 true → 인증 우회!

방어 방법:
1. PreparedStatement 사용 (필수!)
2. 입력값 검증
3. ORM 사용 (JPA, MyBatis)
```

**코드 예시**:
```java
public class SQLInjectionExample {
    // ❌ SQL Injection 취약 코드
    public boolean loginVulnerable(String username, String password) {
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             Statement stmt = conn.createStatement()) {

            // 문자열 연결 (위험!)
            String sql = "SELECT * FROM users WHERE username = '" + username +
                         "' AND password = '" + password + "'";

            System.out.println("실행 SQL: " + sql);

            ResultSet rs = stmt.executeQuery(sql);
            return rs.next();  // 데이터가 있으면 로그인 성공

        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    // ✅ SQL Injection 방어 코드
    public boolean loginSecure(String username, String password) {
        String sql = "SELECT * FROM users WHERE username = ? AND password = ?";

        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            pstmt.setString(1, username);  // 자동 이스케이프
            pstmt.setString(2, password);

            System.out.println("실행 SQL: " + sql);
            System.out.println("파라미터: username=" + username + ", password=" + password);

            ResultSet rs = pstmt.executeQuery();
            return rs.next();

        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    // SQL Injection 공격 시연
    public static void main(String[] args) {
        SQLInjectionExample example = new SQLInjectionExample();

        System.out.println("=== 정상 로그인 ===");
        boolean result1 = example.loginVulnerable("admin", "1234");
        System.out.println("결과: " + result1 + "\n");

        System.out.println("=== SQL Injection 공격 ===");
        String maliciousUsername = "admin' OR '1'='1";
        String maliciousPassword = "anything";

        // 취약한 코드
        boolean result2 = example.loginVulnerable(maliciousUsername, maliciousPassword);
        System.out.println("취약한 코드 결과: " + result2);
        // 실행 SQL: SELECT * FROM users WHERE username = 'admin' OR '1'='1' AND password = 'anything'
        // 결과: true (인증 우회 성공!)

        // 안전한 코드
        boolean result3 = example.loginSecure(maliciousUsername, maliciousPassword);
        System.out.println("안전한 코드 결과: " + result3);
        // 실행 SQL: SELECT * FROM users WHERE username = ? AND password = ?
        // 파라미터: username=admin' OR '1'='1, password=anything
        // 결과: false (공격 차단!)
    }
}
```

**다양한 SQL Injection 공격**:
```java
// 1. UNION 공격 (데이터 유출)
String malicious1 = "admin' UNION SELECT username, password FROM users WHERE '1'='1";
// → 모든 사용자의 비밀번호 유출!

// 2. DROP TABLE 공격 (데이터 삭제)
String malicious2 = "admin'; DROP TABLE users; --";
// → users 테이블 삭제!

// 3. Blind SQL Injection (시간 기반)
String malicious3 = "admin' AND (SELECT SLEEP(10)) --";
// → 응답 시간으로 데이터 추론

// PreparedStatement는 모두 방어!
pstmt.setString(1, malicious1);  // 단순 문자열로 처리
pstmt.setString(1, malicious2);  // 단순 문자열로 처리
pstmt.setString(1, malicious3);  // 단순 문자열로 처리
```

**꼬리 질문**:
- Q: PreparedStatement는 왜 SQL Injection을 방어하나요?
- A: 파라미터를 SQL 코드가 아닌 데이터로 처리하며, 특수문자를 자동으로 이스케이프하기 때문입니다.

**실무 연관**:
- 모든 외부 입력은 PreparedStatement로 처리 필수
- 보안 감사에서 Statement 사용 시 Critical 취약점
- 금융권에서는 SQL Injection 방어 필수 요구사항

---

### Q7. Connection Pool은 왜 필요한가요?

**모범 답변**:
```
Connection 생성 비용:
1. TCP 연결: 50-100ms
2. 인증: 20-50ms
3. 초기화: 10-30ms
→ 총 100-200ms (매우 느림!)

Connection Pool:
- 미리 Connection 생성하여 재사용
- Pool에서 가져오기: 0.1-1ms
- 성능 100-1000배 향상!

동작 원리:
┌─────────────────────────┐
│   Connection Pool       │
│  ┌────┐ ┌────┐ ┌────┐  │
│  │Conn│ │Conn│ │Conn│  │ → 미리 생성
│  └────┘ └────┘ └────┘  │
└─────────────────────────┘
     ↓ 빌려감  ↑ 반납
  애플리케이션
```

**코드 예시**:
```java
import com.zaxxer.hikari.*;

public class ConnectionPoolExample {
    private static HikariDataSource dataSource;

    // Connection Pool 초기화
    static {
        HikariConfig config = new HikariConfig();

        // 데이터베이스 설정
        config.setJdbcUrl("jdbc:mysql://localhost:3306/testdb");
        config.setUsername("root");
        config.setPassword("root1234");

        // Connection Pool 설정
        config.setMaximumPoolSize(10);        // 최대 10개
        config.setMinimumIdle(5);             // 최소 5개 유지
        config.setConnectionTimeout(30000);   // 30초 대기
        config.setIdleTimeout(600000);        // 10분 후 정리
        config.setMaxLifetime(1800000);       // 30분 후 재생성

        // 성능 최적화
        config.addDataSourceProperty("cachePrepStmts", "true");
        config.addDataSourceProperty("prepStmtCacheSize", "250");

        dataSource = new HikariDataSource(config);
        System.out.println("✅ Connection Pool 생성");
    }

    // Connection 가져오기
    public static Connection getConnection() throws SQLException {
        return dataSource.getConnection();
    }

    // 성능 비교
    public static void main(String[] args) throws Exception {
        System.out.println("=== Connection Pool 없이 ===");
        long start1 = System.currentTimeMillis();
        for (int i = 0; i < 100; i++) {
            // 매번 Connection 생성 (느림!)
            Connection conn = DriverManager.getConnection(
                "jdbc:mysql://localhost:3306/testdb", "root", "root1234");
            conn.close();
        }
        long time1 = System.currentTimeMillis() - start1;
        System.out.println("시간: " + time1 + "ms");

        System.out.println("\n=== Connection Pool 사용 ===");
        long start2 = System.currentTimeMillis();
        for (int i = 0; i < 100; i++) {
            // Pool에서 가져오기 (빠름!)
            Connection conn = getConnection();
            conn.close();  // Pool에 반환
        }
        long time2 = System.currentTimeMillis() - start2;
        System.out.println("시간: " + time2 + "ms");

        System.out.println("\n성능 향상: " + (time1 / time2) + "배");

        dataSource.close();
    }
}
```

**실행 결과**:
```
=== Connection Pool 없이 ===
시간: 15,234ms

=== Connection Pool 사용 ===
시간: 123ms

성능 향상: 123배
```

**Connection Pool 모니터링**:
```java
// HikariCP 상태 확인
public void monitorPool() {
    HikariPoolMXBean poolMXBean = dataSource.getHikariPoolMXBean();

    System.out.println("총 Connection: " + poolMXBean.getTotalConnections());
    System.out.println("활성 Connection: " + poolMXBean.getActiveConnections());
    System.out.println("대기 Connection: " + poolMXBean.getIdleConnections());
    System.out.println("대기 중인 스레드: " + poolMXBean.getThreadsAwaitingConnection());
}

// 출력:
// 총 Connection: 10
// 활성 Connection: 3
// 대기 Connection: 7
// 대기 중인 스레드: 0
```

**꼬리 질문**:
- Q: maximumPoolSize는 어떻게 설정하나요?
- A: `CPU 코어 수 × 2~4`가 일반적입니다. 예: 4코어 CPU → 10~20개. 너무 많으면 컨텍스트 스위칭 오버헤드가 발생합니다.

**실무 연관**:
- Spring Boot는 HikariCP를 기본 Connection Pool로 사용
- AWS RDS, Azure SQL은 Connection 수 제한이 있어 Pool 설정이 중요
- Connection Pool 고갈 → 서비스 장애 (타임아웃)

---

## 🎓 중급 면접 질문 (Intermediate Level)

### Q1. Isolation Level 종류와 각각의 문제점은?

**모범 답변**:
```
Isolation Level (낮음 → 높음):

1. READ UNCOMMITTED (Level 0)
   - 커밋되지 않은 데이터 읽기 가능
   - 문제: Dirty Read

2. READ COMMITTED (Level 1)
   - 커밋된 데이터만 읽기
   - 문제: Non-repeatable Read

3. REPEATABLE READ (Level 2)
   - 같은 쿼리는 항상 같은 결과
   - 문제: Phantom Read

4. SERIALIZABLE (Level 3)
   - 완전 격리 (순차 실행)
   - 문제: 성능 저하

MySQL 기본: REPEATABLE READ
Oracle 기본: READ COMMITTED
```

**코드 예시**:
```java
public class IsolationLevelExample {
    // 1. Dirty Read 예시 (READ UNCOMMITTED)
    public void dirtyReadExample() throws SQLException {
        // Transaction 1
        Thread t1 = new Thread(() -> {
            try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
                conn.setTransactionIsolation(Connection.TRANSACTION_READ_UNCOMMITTED);
                conn.setAutoCommit(false);

                // 잔액 업데이트 (아직 커밋 안 함)
                Statement stmt = conn.createStatement();
                stmt.executeUpdate("UPDATE accounts SET balance = 100000 WHERE id = 1");
                System.out.println("[T1] 잔액 업데이트 (커밋 전)");

                Thread.sleep(2000);  // 2초 대기

                // 롤백
                conn.rollback();
                System.out.println("[T1] 롤백");

            } catch (Exception e) {
                e.printStackTrace();
            }
        });

        // Transaction 2
        Thread t2 = new Thread(() -> {
            try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
                conn.setTransactionIsolation(Connection.TRANSACTION_READ_UNCOMMITTED);

                Thread.sleep(1000);  // 1초 후 읽기

                Statement stmt = conn.createStatement();
                ResultSet rs = stmt.executeQuery("SELECT balance FROM accounts WHERE id = 1");
                if (rs.next()) {
                    System.out.println("[T2] 읽은 잔액: " + rs.getInt("balance"));
                    // 100000 출력 (아직 커밋 안 된 데이터!)
                    // → Dirty Read 발생!
                }

            } catch (Exception e) {
                e.printStackTrace();
            }
        });

        t1.start();
        t2.start();
        t1.join();
        t2.join();

        // 결과: T2가 롤백된 데이터를 읽음 (Dirty Read)
    }

    // 2. Non-repeatable Read 예시 (READ COMMITTED)
    public void nonRepeatableReadExample() throws SQLException {
        // Transaction 1
        Thread t1 = new Thread(() -> {
            try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
                conn.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
                conn.setAutoCommit(false);

                Statement stmt = conn.createStatement();

                // 첫 번째 읽기
                ResultSet rs1 = stmt.executeQuery("SELECT balance FROM accounts WHERE id = 1");
                if (rs1.next()) {
                    System.out.println("[T1] 첫 번째 읽기: " + rs1.getInt("balance"));
                }

                Thread.sleep(2000);  // 2초 대기

                // 두 번째 읽기 (같은 트랜잭션)
                ResultSet rs2 = stmt.executeQuery("SELECT balance FROM accounts WHERE id = 1");
                if (rs2.next()) {
                    System.out.println("[T1] 두 번째 읽기: " + rs2.getInt("balance"));
                    // 값이 변경됨! → Non-repeatable Read
                }

            } catch (Exception e) {
                e.printStackTrace();
            }
        });

        // Transaction 2
        Thread t2 = new Thread(() -> {
            try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
                Thread.sleep(1000);  // 1초 후 업데이트

                Statement stmt = conn.createStatement();
                stmt.executeUpdate("UPDATE accounts SET balance = 200000 WHERE id = 1");
                conn.commit();
                System.out.println("[T2] 잔액 업데이트 및 커밋");

            } catch (Exception e) {
                e.printStackTrace();
            }
        });

        t1.start();
        t2.start();
        t1.join();
        t2.join();

        // 결과:
        // [T1] 첫 번째 읽기: 100000
        // [T2] 잔액 업데이트 및 커밋
        // [T1] 두 번째 읽기: 200000
        // → 같은 트랜잭션에서 다른 값 읽음!
    }

    // 3. Phantom Read 예시 (REPEATABLE READ)
    public void phantomReadExample() throws SQLException {
        // Transaction 1
        Thread t1 = new Thread(() -> {
            try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
                conn.setTransactionIsolation(Connection.TRANSACTION_REPEATABLE_READ);
                conn.setAutoCommit(false);

                Statement stmt = conn.createStatement();

                // 첫 번째 읽기
                ResultSet rs1 = stmt.executeQuery("SELECT COUNT(*) FROM users WHERE age > 20");
                if (rs1.next()) {
                    System.out.println("[T1] 첫 번째 COUNT: " + rs1.getInt(1));
                }

                Thread.sleep(2000);  // 2초 대기

                // 두 번째 읽기 (같은 트랜잭션)
                ResultSet rs2 = stmt.executeQuery("SELECT COUNT(*) FROM users WHERE age > 20");
                if (rs2.next()) {
                    System.out.println("[T1] 두 번째 COUNT: " + rs2.getInt(1));
                    // 개수가 변경될 수 있음! → Phantom Read (MySQL은 방지)
                }

            } catch (Exception e) {
                e.printStackTrace();
            }
        });

        // Transaction 2
        Thread t2 = new Thread(() -> {
            try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
                Thread.sleep(1000);  // 1초 후 INSERT

                Statement stmt = conn.createStatement();
                stmt.executeUpdate("INSERT INTO users (name, age) VALUES ('New User', 25)");
                conn.commit();
                System.out.println("[T2] 새 사용자 추가 및 커밋");

            } catch (Exception e) {
                e.printStackTrace();
            }
        });

        t1.start();
        t2.start();
        t1.join();
        t2.join();
    }

    // Isolation Level 설정 예시
    public void setIsolationLevel() throws SQLException {
        Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);

        // Level 설정
        conn.setTransactionIsolation(Connection.TRANSACTION_REPEATABLE_READ);

        // 현재 Level 확인
        int level = conn.getTransactionIsolation();
        String levelName = switch (level) {
            case Connection.TRANSACTION_READ_UNCOMMITTED -> "READ UNCOMMITTED";
            case Connection.TRANSACTION_READ_COMMITTED -> "READ COMMITTED";
            case Connection.TRANSACTION_REPEATABLE_READ -> "REPEATABLE READ";
            case Connection.TRANSACTION_SERIALIZABLE -> "SERIALIZABLE";
            default -> "UNKNOWN";
        };

        System.out.println("현재 Isolation Level: " + levelName);
    }
}
```

**문제점 요약**:
| Level | Dirty Read | Non-repeatable Read | Phantom Read | 성능 |
|-------|------------|---------------------|--------------|------|
| READ UNCOMMITTED | ❌ 발생 | ❌ 발생 | ❌ 발생 | ⭐⭐⭐⭐⭐ |
| READ COMMITTED | ✅ 방지 | ❌ 발생 | ❌ 발생 | ⭐⭐⭐⭐ |
| REPEATABLE READ | ✅ 방지 | ✅ 방지 | ❌ 발생* | ⭐⭐⭐ |
| SERIALIZABLE | ✅ 방지 | ✅ 방지 | ✅ 방지 | ⭐⭐ |

*MySQL InnoDB는 Next-Key Lock으로 Phantom Read도 방지

**꼬리 질문**:
- Q: 실무에서 어떤 Isolation Level을 사용하나요?
- A: 대부분 DB 기본값 사용 (MySQL: REPEATABLE READ, Oracle: READ COMMITTED). 특별한 요구사항이 있을 때만 변경합니다.

**실무 연관**:
- 금융권은 SERIALIZABLE 사용 (정확성 우선)
- SNS는 READ COMMITTED 사용 (성능 우선)
- Isolation Level 높을수록 동시성 낮아짐 (Deadlock 증가)

---

### Q2. Deadlock을 방지하는 방법은?

**모범 답변**:
```
Deadlock:
- 두 트랜잭션이 서로의 리소스를 기다리는 상태
- 영구 대기 (무한 대기)

예시:
Transaction 1: A 잠금 → B 잠금 대기
Transaction 2: B 잠금 → A 잠금 대기
→ Deadlock 발생!

방지 방법:
1. 잠금 순서 통일
   - 모든 트랜잭션이 같은 순서로 잠금

2. 타임아웃 설정
   - 일정 시간 후 롤백

3. Deadlock Detection & Retry
   - Deadlock 감지 후 재시도

4. 트랜잭션 최소화
   - 짧은 트랜잭션 유지
```

**코드 예시**:
```java
public class DeadlockExample {
    // ❌ Deadlock 발생 코드
    public void createDeadlock() throws InterruptedException {
        // Transaction 1
        Thread t1 = new Thread(() -> {
            try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
                conn.setAutoCommit(false);

                // A 잠금
                PreparedStatement pstmt1 = conn.prepareStatement(
                    "SELECT * FROM accounts WHERE id = 1 FOR UPDATE");
                pstmt1.executeQuery();
                System.out.println("[T1] Account 1 잠금");

                Thread.sleep(100);

                // B 잠금 시도 (대기!)
                PreparedStatement pstmt2 = conn.prepareStatement(
                    "SELECT * FROM accounts WHERE id = 2 FOR UPDATE");
                pstmt2.executeQuery();
                System.out.println("[T1] Account 2 잠금");

                conn.commit();

            } catch (Exception e) {
                System.out.println("[T1] Deadlock 발생: " + e.getMessage());
            }
        });

        // Transaction 2
        Thread t2 = new Thread(() -> {
            try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
                conn.setAutoCommit(false);

                // B 잠금
                PreparedStatement pstmt1 = conn.prepareStatement(
                    "SELECT * FROM accounts WHERE id = 2 FOR UPDATE");
                pstmt1.executeQuery();
                System.out.println("[T2] Account 2 잠금");

                Thread.sleep(100);

                // A 잠금 시도 (대기!)
                PreparedStatement pstmt2 = conn.prepareStatement(
                    "SELECT * FROM accounts WHERE id = 1 FOR UPDATE");
                pstmt2.executeQuery();
                System.out.println("[T2] Account 1 잠금");

                conn.commit();

            } catch (Exception e) {
                System.out.println("[T2] Deadlock 발생: " + e.getMessage());
            }
        });

        t1.start();
        t2.start();
        t1.join();
        t2.join();

        // 결과:
        // [T1] Account 1 잠금
        // [T2] Account 2 잠금
        // [T1] Deadlock 발생: Lock wait timeout exceeded
        // [T2] Deadlock 발생: Deadlock found when trying to get lock
    }

    // ✅ Deadlock 방지: 잠금 순서 통일
    public void preventDeadlockWithOrder() {
        // 송금 처리 (ID 순서로 잠금)
        public void transfer(int fromId, int toId, int amount) throws SQLException {
            Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
            conn.setAutoCommit(false);

            // ID 순서로 정렬 (작은 ID 먼저 잠금)
            int firstId = Math.min(fromId, toId);
            int secondId = Math.max(fromId, toId);

            try {
                // 첫 번째 계좌 잠금
                PreparedStatement pstmt1 = conn.prepareStatement(
                    "SELECT * FROM accounts WHERE id = ? FOR UPDATE");
                pstmt1.setInt(1, firstId);
                pstmt1.executeQuery();
                System.out.println("Account " + firstId + " 잠금");

                // 두 번째 계좌 잠금
                PreparedStatement pstmt2 = conn.prepareStatement(
                    "SELECT * FROM accounts WHERE id = ? FOR UPDATE");
                pstmt2.setInt(1, secondId);
                pstmt2.executeQuery();
                System.out.println("Account " + secondId + " 잠금");

                // 송금 처리
                // ...

                conn.commit();
                System.out.println("송금 완료");

            } catch (SQLException e) {
                conn.rollback();
                throw e;
            } finally {
                conn.close();
            }
        }
    }

    // ✅ Deadlock 방지: Retry 로직
    public void transferWithRetry(int fromId, int toId, int amount) {
        int maxRetry = 3;

        for (int attempt = 1; attempt <= maxRetry; attempt++) {
            try {
                transfer(fromId, toId, amount);
                System.out.println("송금 성공");
                return;

            } catch (SQLException e) {
                // Deadlock 감지
                if (e.getErrorCode() == 1213 || e.getMessage().contains("Deadlock")) {
                    System.out.println("Deadlock 발생, 재시도 " + attempt + "/" + maxRetry);

                    if (attempt < maxRetry) {
                        try {
                            Thread.sleep(100 * attempt);  // Exponential backoff
                        } catch (InterruptedException ie) {
                            Thread.currentThread().interrupt();
                        }
                    } else {
                        System.out.println("최대 재시도 횟수 초과");
                        throw new RuntimeException("송금 실패", e);
                    }
                } else {
                    throw new RuntimeException("송금 오류", e);
                }
            }
        }
    }

    // 타임아웃 설정
    public void setLockTimeout() throws SQLException {
        Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);

        // MySQL
        Statement stmt = conn.createStatement();
        stmt.execute("SET innodb_lock_wait_timeout = 10");  // 10초

        // 또는 JDBC 레벨
        // conn.setNetworkTimeout(executor, 10000);
    }
}
```

**Deadlock 감지 및 모니터링**:
```sql
-- MySQL Deadlock 확인
SHOW ENGINE INNODB STATUS;

-- 결과:
-- LATEST DETECTED DEADLOCK
-- ------------------------
-- Transaction 1:
--   WAITING FOR THIS LOCK TO BE GRANTED:
--   RECORD LOCKS space id 0 page no 3 n bits 72 index PRIMARY of table test.accounts
--   trx id 1234 lock_mode X locks rec but not gap waiting
--
-- Transaction 2:
--   HOLDS THE LOCK(S):
--   RECORD LOCKS space id 0 page no 3 n bits 72 index PRIMARY of table test.accounts
--   trx id 1235 lock_mode X locks rec but not gap
--
-- WE ROLL BACK TRANSACTION (2)
```

**꼬리 질문**:
- Q: Deadlock이 발생하면 어떻게 해결되나요?
- A: DB가 자동으로 감지하여 한 트랜잭션을 롤백합니다. 애플리케이션에서는 재시도 로직으로 처리합니다.

**실무 연관**:
- 은행 송금, 재고 관리 등에서 자주 발생
- 잠금 순서 통일이 가장 효과적인 방법
- 모니터링 필수 (Deadlock 빈도 추적)

---

### Q3. Batch 처리로 성능을 최적화하는 방법은?

**모범 답변**:
```
Batch 처리:
- 여러 SQL을 한 번에 실행
- 네트워크 왕복 횟수 감소
- 성능 10-100배 향상

사용 시기:
1. 대량 INSERT
2. 대량 UPDATE
3. 대량 DELETE

주의사항:
- executeBatch() 필수 호출
- Batch 크기 조절 (1000-10000)
- 트랜잭션과 함께 사용
```

**코드 예시**:
```java
public class BatchExample {
    // ❌ 일반 INSERT (느림)
    public void insertWithoutBatch(List<User> users) {
        String sql = "INSERT INTO users (name, email, age) VALUES (?, ?, ?)";

        long start = System.currentTimeMillis();

        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            for (User user : users) {
                pstmt.setString(1, user.getName());
                pstmt.setString(2, user.getEmail());
                pstmt.setInt(3, user.getAge());

                pstmt.executeUpdate();  // 매번 DB 호출!
            }

        } catch (SQLException e) {
            e.printStackTrace();
        }

        long elapsed = System.currentTimeMillis() - start;
        System.out.println("일반 INSERT: " + elapsed + "ms");
    }

    // ✅ Batch INSERT (빠름)
    public void insertWithBatch(List<User> users) {
        String sql = "INSERT INTO users (name, email, age) VALUES (?, ?, ?)";

        long start = System.currentTimeMillis();

        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            for (User user : users) {
                pstmt.setString(1, user.getName());
                pstmt.setString(2, user.getEmail());
                pstmt.setInt(3, user.getAge());

                pstmt.addBatch();  // Batch에 추가 (DB 호출 안 함)
            }

            int[] results = pstmt.executeBatch();  // 한 번에 실행!
            System.out.println("처리된 행 수: " + results.length);

        } catch (SQLException e) {
            e.printStackTrace();
        }

        long elapsed = System.currentTimeMillis() - start;
        System.out.println("Batch INSERT: " + elapsed + "ms");
    }

    // ✅ Batch + Transaction (더 빠름)
    public void insertWithBatchAndTransaction(List<User> users) {
        String sql = "INSERT INTO users (name, email, age) VALUES (?, ?, ?)";

        long start = System.currentTimeMillis();

        Connection conn = null;
        try {
            conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
            conn.setAutoCommit(false);  // Transaction 시작

            try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
                for (User user : users) {
                    pstmt.setString(1, user.getName());
                    pstmt.setString(2, user.getEmail());
                    pstmt.setInt(3, user.getAge());

                    pstmt.addBatch();
                }

                int[] results = pstmt.executeBatch();
                conn.commit();  // 한 번에 커밋!

                System.out.println("처리된 행 수: " + results.length);
            }

        } catch (SQLException e) {
            if (conn != null) {
                try {
                    conn.rollback();
                } catch (SQLException ex) {
                    ex.printStackTrace();
                }
            }
            e.printStackTrace();
        } finally {
            if (conn != null) {
                try {
                    conn.setAutoCommit(true);
                    conn.close();
                } catch (SQLException e) {
                    e.printStackTrace();
                }
            }
        }

        long elapsed = System.currentTimeMillis() - start;
        System.out.println("Batch + Transaction: " + elapsed + "ms");
    }

    // Batch 크기 조절 (대용량 처리)
    public void insertWithBatchSize(List<User> users, int batchSize) {
        String sql = "INSERT INTO users (name, email, age) VALUES (?, ?, ?)";

        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            conn.setAutoCommit(false);

            int count = 0;
            for (User user : users) {
                pstmt.setString(1, user.getName());
                pstmt.setString(2, user.getEmail());
                pstmt.setInt(3, user.getAge());

                pstmt.addBatch();
                count++;

                // batchSize마다 실행
                if (count % batchSize == 0) {
                    pstmt.executeBatch();
                    conn.commit();
                    System.out.println(count + "개 처리 완료");
                }
            }

            // 남은 데이터 처리
            if (count % batchSize != 0) {
                pstmt.executeBatch();
                conn.commit();
                System.out.println("총 " + count + "개 처리 완료");
            }

        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    // 성능 비교 테스트
    public static void main(String[] args) {
        BatchExample example = new BatchExample();

        // 10,000개 사용자 생성
        List<User> users = new ArrayList<>();
        for (int i = 0; i < 10000; i++) {
            users.add(new User("User" + i, "user" + i + "@example.com", 20 + (i % 50)));
        }

        System.out.println("=== 10,000개 데이터 INSERT 성능 비교 ===\n");

        example.insertWithoutBatch(users);
        // 결과: 15,234ms

        example.insertWithBatch(users);
        // 결과: 1,523ms (10배 빠름!)

        example.insertWithBatchAndTransaction(users);
        // 결과: 523ms (30배 빠름!)
    }
}
```

**실행 결과**:
```
=== 10,000개 데이터 INSERT 성능 비교 ===

일반 INSERT: 15,234ms
Batch INSERT: 1,523ms (10배 빠름!)
Batch + Transaction: 523ms (30배 빠름!)
```

**Batch UPDATE 예시**:
```java
// Batch UPDATE
public void updateWithBatch(List<User> users) {
    String sql = "UPDATE users SET email = ?, age = ? WHERE id = ?";

    try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
         PreparedStatement pstmt = conn.prepareStatement(sql)) {

        conn.setAutoCommit(false);

        for (User user : users) {
            pstmt.setString(1, user.getEmail());
            pstmt.setInt(2, user.getAge());
            pstmt.setInt(3, user.getId());

            pstmt.addBatch();
        }

        int[] results = pstmt.executeBatch();
        conn.commit();

        // 결과 확인
        int successCount = 0;
        for (int result : results) {
            if (result > 0) successCount++;
        }

        System.out.println("성공: " + successCount + "개, 실패: " + (results.length - successCount) + "개");

    } catch (SQLException e) {
        e.printStackTrace();
    }
}
```

**꼬리 질문**:
- Q: Batch 크기는 어떻게 정하나요?
- A: 일반적으로 1000-10000개가 적절합니다. 너무 크면 메모리 부족, 너무 작으면 성능 향상 미미합니다.

**실무 연관**:
- ETL 작업 (대량 데이터 이동)
- 통계 데이터 생성
- 로그 데이터 저장
- Spring Batch에서 Batch 처리 필수

---

### Q4. Connection Pool 설정을 어떻게 튜닝하나요?

**모범 답변**:
```
Connection Pool 튜닝:

1. maximumPoolSize (최대 Connection 수)
   - 권장: CPU 코어 수 × 2~4
   - 예: 4코어 → 10~20개

2. minimumIdle (최소 유지 Connection)
   - 권장: maximumPoolSize / 2
   - 예: 최대 20개 → 최소 10개

3. connectionTimeout (대기 시간)
   - 권장: 5000~30000ms
   - Connection 획득 실패 시 예외

4. idleTimeout (유휴 Connection 정리)
   - 권장: 300000ms (5분)
   - 사용하지 않는 Connection 정리

5. maxLifetime (Connection 재생성)
   - 권장: 1800000ms (30분)
   - 주기적으로 Connection 재생성
```

**코드 예시**:
```java
public class ConnectionPoolTuning {
    // ✅ 권장 설정 (웹 애플리케이션)
    public HikariDataSource createOptimalPool() {
        HikariConfig config = new HikariConfig();

        // 기본 설정
        config.setJdbcUrl("jdbc:mysql://localhost:3306/testdb");
        config.setUsername("root");
        config.setPassword("root1234");

        // Connection Pool 설정
        int cpuCores = Runtime.getRuntime().availableProcessors();
        config.setMaximumPoolSize(cpuCores * 2);    // CPU 코어 수 × 2
        config.setMinimumIdle(cpuCores);            // 최소 = 코어 수
        config.setConnectionTimeout(10000);         // 10초
        config.setIdleTimeout(300000);              // 5분
        config.setMaxLifetime(1800000);             // 30분

        // 성능 최적화
        config.addDataSourceProperty("cachePrepStmts", "true");
        config.addDataSourceProperty("prepStmtCacheSize", "250");
        config.addDataSourceProperty("prepStmtCacheSqlLimit", "2048");
        config.addDataSourceProperty("useServerPrepStmts", "true");

        // Connection 검증
        config.setConnectionTestQuery("SELECT 1");  // MySQL
        config.setValidationTimeout(3000);          // 3초

        // Leak Detection (개발 환경)
        config.setLeakDetectionThreshold(60000);    // 1분 이상 반환 안 하면 경고

        return new HikariDataSource(config);
    }

    // 트래픽에 따른 튜닝
    public HikariDataSource createPoolForTraffic(String trafficLevel) {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:mysql://localhost:3306/testdb");
        config.setUsername("root");
        config.setPassword("root1234");

        switch (trafficLevel) {
            case "LOW":  // 소규모 애플리케이션
                config.setMaximumPoolSize(5);
                config.setMinimumIdle(2);
                break;

            case "MEDIUM":  // 중규모 애플리케이션
                config.setMaximumPoolSize(20);
                config.setMinimumIdle(10);
                break;

            case "HIGH":  // 대규모 애플리케이션
                config.setMaximumPoolSize(50);
                config.setMinimumIdle(25);
                break;

            case "EXTREME":  // 초대규모 애플리케이션
                config.setMaximumPoolSize(100);
                config.setMinimumIdle(50);
                break;
        }

        config.setConnectionTimeout(5000);
        config.setIdleTimeout(300000);
        config.setMaxLifetime(1800000);

        return new HikariDataSource(config);
    }

    // Connection Pool 모니터링
    public void monitorPool(HikariDataSource dataSource) {
        HikariPoolMXBean poolMXBean = dataSource.getHikariPoolMXBean();

        System.out.println("=== Connection Pool 상태 ===");
        System.out.println("총 Connection: " + poolMXBean.getTotalConnections());
        System.out.println("활성 Connection: " + poolMXBean.getActiveConnections());
        System.out.println("대기 Connection: " + poolMXBean.getIdleConnections());
        System.out.println("대기 중인 스레드: " + poolMXBean.getThreadsAwaitingConnection());

        // 경고 조건
        int total = poolMXBean.getTotalConnections();
        int active = poolMXBean.getActiveConnections();
        double usage = (double) active / total * 100;

        if (usage > 80) {
            System.out.println("⚠️ 경고: Connection 사용률 " + String.format("%.1f", usage) + "%");
            System.out.println("→ maximumPoolSize 증가 권장");
        }

        if (poolMXBean.getThreadsAwaitingConnection() > 0) {
            System.out.println("⚠️ 경고: " + poolMXBean.getThreadsAwaitingConnection() + "개 스레드 대기 중");
            System.out.println("→ Connection Pool 고갈 위험");
        }
    }

    // Connection Leak Detection
    public void detectLeak(HikariDataSource dataSource) {
        // Connection을 반환하지 않는 경우 감지
        try {
            Connection conn = dataSource.getConnection();

            // 작업 수행
            Statement stmt = conn.createStatement();
            stmt.executeQuery("SELECT * FROM users");

            // ❌ conn.close() 누락!
            // → 1분 후 경고 로그 출력

        } catch (SQLException e) {
            e.printStackTrace();
        }

        // 출력:
        // WARN com.zaxxer.hikari.pool.ProxyLeakTask - Connection leak detection triggered for conn123, stack trace follows
    }

    public static void main(String[] args) {
        ConnectionPoolTuning tuning = new ConnectionPoolTuning();

        // 권장 설정으로 Pool 생성
        HikariDataSource dataSource = tuning.createOptimalPool();

        System.out.println("CPU 코어 수: " + Runtime.getRuntime().availableProcessors());
        System.out.println("maximumPoolSize: " + dataSource.getMaximumPoolSize());
        System.out.println("minimumIdle: " + dataSource.getMinimumIdle());

        // 모니터링
        tuning.monitorPool(dataSource);

        dataSource.close();
    }
}
```

**실행 결과**:
```
CPU 코어 수: 4
maximumPoolSize: 8
minimumIdle: 4

=== Connection Pool 상태 ===
총 Connection: 8
활성 Connection: 2
대기 Connection: 6
대기 중인 스레드: 0
```

**AWS RDS 연결 제한**:
```
RDS 인스턴스별 최대 Connection 수:
- db.t2.micro: 66개
- db.t2.small: 150개
- db.m5.large: 1000개

설정 예시:
// RDS 제한 고려
config.setMaximumPoolSize(50);  // RDS 최대 연결의 50% 사용
```

**꼬리 질문**:
- Q: maximumPoolSize를 너무 크게 설정하면 어떻게 되나요?
- A: DB 서버 리소스 고갈, 컨텍스트 스위칭 오버헤드 증가, RDS 연결 제한 초과 가능성이 있습니다.

**실무 연관**:
- Spring Boot는 기본 HikariCP 설정 사용 (maximumPoolSize=10)
- 트래픽 증가 시 Connection Pool 튜닝 필수
- 모니터링 도구 (Grafana, CloudWatch) 연동 권장

---

### Q5. JDBC vs JPA(ORM), 어떤 상황에서 JDBC를 사용하나요?

**모범 답변**:
```
JDBC:
- SQL을 직접 작성
- 성능 최적화 가능
- 학습 곡선 낮음

JPA (ORM):
- 객체 중심 개발
- SQL 자동 생성
- 생산성 높음

JDBC 사용 시기:
1. 복잡한 쿼리
   - 다중 JOIN, 서브쿼리
   - 집계 함수 (SUM, AVG, GROUP BY)

2. 성능 최적화
   - Batch 처리
   - Native Query

3. 레거시 시스템
   - 기존 JDBC 코드베이스
   - Stored Procedure 사용

4. 단순 작업
   - 일회성 스크립트
   - 데이터 마이그레이션
```

**비교 코드**:
```java
public class JDBCvsJPA {
    // ✅ JDBC: 복잡한 집계 쿼리
    public Map<String, Integer> getOrderStatisticsByCategory() {
        String sql = """
            SELECT c.name AS category,
                   COUNT(o.id) AS order_count,
                   SUM(o.total_amount) AS total_sales
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            WHERE o.order_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY c.id, c.name
            HAVING total_sales > 1000000
            ORDER BY total_sales DESC
            """;

        Map<String, Integer> stats = new HashMap<>();

        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {

            while (rs.next()) {
                String category = rs.getString("category");
                int totalSales = rs.getInt("total_sales");
                stats.put(category, totalSales);
            }

        } catch (SQLException e) {
            e.printStackTrace();
        }

        return stats;
        // JDBC: 50ms (직접 SQL)
    }

    // JPA: 같은 쿼리를 작성하기 어려움
    // → Native Query 사용 또는 여러 번의 쿼리 필요
    // → 성능 저하

    // ✅ JPA: CRUD 작업
    @Entity
    public class User {
        @Id
        @GeneratedValue(strategy = GenerationType.IDENTITY)
        private Long id;

        private String name;
        private String email;

        // getter, setter
    }

    @Repository
    public interface UserRepository extends JpaRepository<User, Long> {
        List<User> findByName(String name);  // 자동 쿼리 생성!
    }

    public void jpaExample() {
        // CRUD가 매우 간단!
        User user = new User();
        user.setName("John");
        user.setEmail("john@example.com");

        userRepository.save(user);  // INSERT
        User found = userRepository.findById(1L).get();  // SELECT
        found.setEmail("newemail@example.com");
        userRepository.save(found);  // UPDATE
        userRepository.deleteById(1L);  // DELETE
    }

    // ✅ JDBC: Batch 처리
    public void jdbcBatchInsert(List<User> users) {
        String sql = "INSERT INTO users (name, email) VALUES (?, ?)";

        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            conn.setAutoCommit(false);

            for (User user : users) {
                pstmt.setString(1, user.getName());
                pstmt.setString(2, user.getEmail());
                pstmt.addBatch();
            }

            pstmt.executeBatch();
            conn.commit();

        } catch (SQLException e) {
            e.printStackTrace();
        }
        // 10,000개: 500ms
    }

    // JPA: Batch 처리가 비효율적
    public void jpaBatchInsert(List<User> users) {
        for (User user : users) {
            userRepository.save(user);  // 각각 INSERT
        }
        // 10,000개: 15,000ms (30배 느림!)
    }
}
```

**선택 기준**:
| 상황 | JDBC | JPA |
|------|------|-----|
| **CRUD 중심** | ❌ | ✅ |
| **복잡한 쿼리** | ✅ | ❌ |
| **대량 Batch** | ✅ | ❌ |
| **빠른 개발** | ❌ | ✅ |
| **성능 최적화** | ✅ | △ |
| **유지보수성** | △ | ✅ |

**하이브리드 접근**:
```java
// Spring Data JPA + JDBC Template
@Service
public class HybridService {
    @Autowired
    private UserRepository userRepository;  // JPA

    @Autowired
    private JdbcTemplate jdbcTemplate;  // JDBC

    // CRUD는 JPA
    public User getUser(Long id) {
        return userRepository.findById(id).orElse(null);
    }

    // 복잡한 쿼리는 JDBC
    public List<Map<String, Object>> getComplexStatistics() {
        String sql = """
            SELECT ... (복잡한 SQL)
            """;

        return jdbcTemplate.queryForList(sql);
    }

    // Batch는 JDBC
    public void batchInsert(List<User> users) {
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

**꼬리 질문**:
- Q: Spring Data JPA의 Native Query와 JDBC의 차이는?
- A: Native Query도 내부적으로 JDBC를 사용하지만, 엔티티 매핑과 트랜잭션 관리가 자동입니다. 순수 JDBC는 더 세밀한 제어가 가능합니다.

**실무 연관**:
- 대부분의 프로젝트는 JPA 사용 (생산성)
- 성능 critical한 부분만 JDBC 사용
- Netflix, Uber 등 대규모 서비스는 JDBC 직접 사용

---

## 🎯 40장 완료!

**축하합니다!** JDBC를 완벽히 마스터했습니다!

**이제 여러분은**:
- ✅ JDBC로 DB 연결 및 조작
- ✅ PreparedStatement로 안전한 SQL
- ✅ Transaction 관리 (ACID, Isolation Level)
- ✅ Connection Pool 활용 및 튜닝
- ✅ Batch 처리로 성능 최적화
- ✅ Deadlock 방지 및 해결
- ✅ JDBC vs JPA 선택 기준 이해

**주요 베스트 프랙티스**:
1. 항상 PreparedStatement 사용 (SQL Injection 방어)
2. try-with-resources로 리소스 관리
3. Connection Pool 필수 (HikariCP)
4. Transaction 적절히 사용 (ACID 보장)
5. Batch 처리로 성능 최적화
6. Deadlock 방지 (잠금 순서 통일)
7. 모니터링 및 튜닝 (Connection Pool 상태 확인)

**다음 장으로**: [41장: 정규표현식 →](41-1-정규표현식-Part1.md)

**이전 Part**: [← 40-2: 트랜잭션과 Connection Pool](40-2-데이터베이스-연동-JDBC-Part2.md)

**목차로 돌아가기**: [📚 전체 목차](README.md)
