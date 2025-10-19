# 04장: DI (Dependency Injection) - Part 3 (기본 실습)

**[← 이전: Part 2](04-2-DI-Part2.md)** | **[다음: Part 4 →](04-4-DI-Part4.md)**

---

## 💻 기본 실습

### 📋 사전 체크리스트

```bash
# 1. Java 버전 확인 (11 이상)
java -version

# 2. Spring Boot 프로젝트 준비
# 03장에서 만든 프로젝트 재사용 가능

# 3. IDE에서 Lombok 플러그인 설치 확인
# IntelliJ: Settings → Plugins → Lombok 검색
```

---

### 실습 1: 생성자 주입 (Constructor Injection) - 권장 방식

**난이도**: ⭐⭐☆☆☆

#### 코드

**파일: src/main/java/com/example/demo/service/EmailService.java**
```java
package com.example.demo.service;

import org.springframework.stereotype.Service;

@Service
public class EmailService {

    public void sendEmail(String to, String subject, String body) {
        // 실제로는 SMTP로 이메일 발송
        System.out.println("📧 이메일 발송");
        System.out.println("   To: " + to);
        System.out.println("   Subject: " + subject);
        System.out.println("   Body: " + body);
    }
}
```

**파일: src/main/java/com/example/demo/service/UserService.java**
```java
package com.example.demo.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class UserService {

    // final 키워드로 불변성 보장
    private final EmailService emailService;

    // 생성자 주입 (권장 방식)
    @Autowired  // Spring 4.3+ 생성자 1개면 생략 가능
    public UserService(EmailService emailService) {
        this.emailService = emailService;
        System.out.println("✅ UserService 생성 (생성자 주입)");
    }

    public void registerUser(String username, String email) {
        // 사용자 등록 로직
        System.out.println("👤 사용자 등록: " + username);

        // 이메일 발송
        emailService.sendEmail(
            email,
            "회원가입 완료",
            username + "님, 환영합니다!"
        );
    }
}
```

**파일: src/main/java/com/example/demo/DemoApplication.java**
```java
package com.example.demo;

import com.example.demo.service.UserService;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ApplicationContext;

@SpringBootApplication
public class DemoApplication {

    public static void main(String[] args) {
        ApplicationContext context = SpringApplication.run(DemoApplication.class, args);

        // UserService Bean 가져오기
        UserService userService = context.getBean(UserService.class);

        // 메서드 호출
        userService.registerUser("홍길동", "hong@example.com");
    }
}
```

#### 실행

```bash
./mvnw spring-boot:run
```

#### 예상 출력

```
✅ UserService 생성 (생성자 주입)

👤 사용자 등록: 홍길동
📧 이메일 발송
   To: hong@example.com
   Subject: 회원가입 완료
   Body: 홍길동님, 환영합니다!
```

#### 코드 설명

- **라인 11**: `final` 키워드로 불변성 보장, NPE 방지
- **라인 14**: 생성자 주입, `@Autowired`는 생략 가능
- **라인 24**: 주입받은 `emailService` 사용

---

### 실습 2: Lombok으로 생성자 주입 간편화

**난이도**: ⭐⭐☆☆☆

#### 코드

**pom.xml에 Lombok 추가**:
```xml
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <optional>true</optional>
</dependency>
```

**파일: src/main/java/com/example/demo/service/SmsService.java**
```java
package com.example.demo.service;

import org.springframework.stereotype.Service;

@Service
public class SmsService {

    public void sendSms(String phone, String message) {
        System.out.println("📱 SMS 발송");
        System.out.println("   To: " + phone);
        System.out.println("   Message: " + message);
    }
}
```

**파일: src/main/java/com/example/demo/service/NotificationService.java**
```java
package com.example.demo.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor  // final 필드로 생성자 자동 생성
public class NotificationService {

    // final 필드들
    private final EmailService emailService;
    private final SmsService smsService;

    // Lombok이 자동으로 생성자 생성:
    // public NotificationService(EmailService emailService, SmsService smsService) {
    //     this.emailService = emailService;
    //     this.smsService = smsService;
    // }

    public void notifyUser(String username, String email, String phone) {
        System.out.println("🔔 사용자 알림: " + username);

        // 이메일과 SMS 동시 발송
        emailService.sendEmail(email, "알림", username + "님께 알림이 있습니다.");
        smsService.sendSms(phone, username + "님께 알림이 있습니다.");
    }
}
```

**테스트**:
```java
// DemoApplication.java
public static void main(String[] args) {
    ApplicationContext context = SpringApplication.run(DemoApplication.class, args);

    NotificationService notificationService = context.getBean(NotificationService.class);
    notificationService.notifyUser("김철수", "kim@example.com", "010-1234-5678");
}
```

#### 예상 출력

```
🔔 사용자 알림: 김철수
📧 이메일 발송
   To: kim@example.com
   Subject: 알림
   Body: 김철수님께 알림이 있습니다.
📱 SMS 발송
   To: 010-1234-5678
   Message: 김철수님께 알림이 있습니다.
```

#### 코드 설명

- **라인 7**: `@RequiredArgsConstructor`가 final 필드로 생성자 자동 생성
- **라인 11-12**: final 필드 (불변성 보장)
- **라인 23-24**: 2개의 의존성을 모두 사용

---

### 실습 3: 인터페이스 기반 DI - Strategy 패턴

**난이도**: ⭐⭐⭐☆☆

#### 코드

**파일: src/main/java/com/example/demo/payment/PaymentGateway.java**
```java
package com.example.demo.payment;

// 결제 게이트웨이 인터페이스
public interface PaymentGateway {
    String processPayment(int amount);
    String getProviderName();
}
```

**파일: src/main/java/com/example/demo/payment/TossPaymentGateway.java**
```java
package com.example.demo.payment;

import org.springframework.stereotype.Component;

@Component
public class TossPaymentGateway implements PaymentGateway {

    @Override
    public String processPayment(int amount) {
        // 토스페이먼츠 API 호출
        System.out.println("💳 토스페이먼츠로 결제 처리: " + amount + "원");
        return "TOSS-" + System.currentTimeMillis();
    }

    @Override
    public String getProviderName() {
        return "토스페이먼츠";
    }
}
```

**파일: src/main/java/com/example/demo/payment/NaverPayGateway.java**
```java
package com.example.demo.payment;

import org.springframework.stereotype.Component;

@Component
public class NaverPayGateway implements PaymentGateway {

    @Override
    public String processPayment(int amount) {
        // 네이버페이 API 호출
        System.out.println("💳 네이버페이로 결제 처리: " + amount + "원");
        return "NAVER-" + System.currentTimeMillis();
    }

    @Override
    public String getProviderName() {
        return "네이버페이";
    }
}
```

**파일: src/main/java/com/example/demo/service/OrderService.java**
```java
package com.example.demo.service;

import com.example.demo.payment.PaymentGateway;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;

@Service
public class OrderService {

    private final PaymentGateway paymentGateway;

    // @Qualifier로 특정 구현체 선택
    public OrderService(@Qualifier("tossPaymentGateway") PaymentGateway paymentGateway) {
        this.paymentGateway = paymentGateway;
        System.out.println("✅ OrderService 생성 - 결제사: " + paymentGateway.getProviderName());
    }

    public void createOrder(String product, int amount) {
        System.out.println("🛒 주문 생성: " + product);

        // 결제 처리
        String paymentId = paymentGateway.processPayment(amount);
        System.out.println("✅ 결제 완료 - ID: " + paymentId);
    }
}
```

**테스트**:
```java
// DemoApplication.java
public static void main(String[] args) {
    ApplicationContext context = SpringApplication.run(DemoApplication.class, args);

    OrderService orderService = context.getBean(OrderService.class);
    orderService.createOrder("MacBook Pro", 2500000);
}
```

#### 예상 출력

```
✅ OrderService 생성 - 결제사: 토스페이먼츠
🛒 주문 생성: MacBook Pro
💳 토스페이먼츠로 결제 처리: 2500000원
✅ 결제 완료 - ID: TOSS-1234567890
```

#### 코드 설명

- **PaymentGateway**: 인터페이스로 추상화
- **TossPaymentGateway, NaverPayGateway**: 구체적인 구현체
- **@Qualifier("tossPaymentGateway")**: 여러 구현체 중 특정 Bean 선택
- **장점**: 결제사 변경 시 `@Qualifier` 값만 수정

---

### 실습 4: @Primary로 기본 구현체 지정

**난이도**: ⭐⭐⭐☆☆

#### 코드

**파일: src/main/java/com/example/demo/payment/TossPaymentGateway.java** (수정)
```java
package com.example.demo.payment;

import org.springframework.context.annotation.Primary;
import org.springframework.stereotype.Component;

@Component
@Primary  // 기본 구현체로 지정
public class TossPaymentGateway implements PaymentGateway {

    @Override
    public String processPayment(int amount) {
        System.out.println("💳 토스페이먼츠로 결제 처리: " + amount + "원");
        return "TOSS-" + System.currentTimeMillis();
    }

    @Override
    public String getProviderName() {
        return "토스페이먼츠";
    }
}
```

**파일: src/main/java/com/example/demo/service/OrderService.java** (수정)
```java
package com.example.demo.service;

import com.example.demo.payment.PaymentGateway;
import org.springframework.stereotype.Service;

@Service
public class OrderService {

    private final PaymentGateway paymentGateway;

    // @Qualifier 없이도 @Primary가 붙은 Bean이 주입됨
    public OrderService(PaymentGateway paymentGateway) {
        this.paymentGateway = paymentGateway;
        System.out.println("✅ OrderService 생성 - 결제사: " + paymentGateway.getProviderName());
    }

    public void createOrder(String product, int amount) {
        System.out.println("🛒 주문 생성: " + product);
        String paymentId = paymentGateway.processPayment(amount);
        System.out.println("✅ 결제 완료 - ID: " + paymentId);
    }
}
```

#### 예상 출력

```
✅ OrderService 생성 - 결제사: 토스페이먼츠
🛒 주문 생성: iPhone 15
💳 토스페이먼츠로 결제 처리: 1500000원
✅ 결제 완료 - ID: TOSS-1234567890
```

#### 코드 설명

- **@Primary**: 같은 타입의 Bean이 여러 개일 때 기본으로 사용할 Bean 지정
- **@Qualifier vs @Primary**:
  - `@Qualifier`: 명시적 선택
  - `@Primary`: 기본값 지정, 코드 간결

---

### 실습 5: 모든 구현체를 List로 주입

**난이도**: ⭐⭐⭐⭐☆

#### 코드

**파일: src/main/java/com/example/demo/service/PaymentAggregatorService.java**
```java
package com.example.demo.service;

import com.example.demo.payment.PaymentGateway;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class PaymentAggregatorService {

    // 모든 PaymentGateway 구현체를 List로 주입
    private final List<PaymentGateway> paymentGateways;

    public void showAvailableGateways() {
        System.out.println("💳 사용 가능한 결제 수단:");
        for (PaymentGateway gateway : paymentGateways) {
            System.out.println("   - " + gateway.getProviderName());
        }
    }

    public void processWithBestGateway(int amount) {
        System.out.println("\n💡 최적의 결제 수단 선택 중...");

        // 예시: 금액에 따라 최적의 결제사 선택
        PaymentGateway selectedGateway;
        if (amount >= 1000000) {
            // 100만원 이상은 토스페이먼츠 (수수료가 더 저렴하다고 가정)
            selectedGateway = paymentGateways.stream()
                    .filter(g -> g.getProviderName().contains("토스"))
                    .findFirst()
                    .orElse(paymentGateways.get(0));
        } else {
            // 100만원 미만은 네이버페이
            selectedGateway = paymentGateways.stream()
                    .filter(g -> g.getProviderName().contains("네이버"))
                    .findFirst()
                    .orElse(paymentGateways.get(0));
        }

        System.out.println("✅ 선택된 결제사: " + selectedGateway.getProviderName());
        String paymentId = selectedGateway.processPayment(amount);
        System.out.println("✅ 결제 완료 - ID: " + paymentId);
    }
}
```

**테스트**:
```java
// DemoApplication.java
public static void main(String[] args) {
    ApplicationContext context = SpringApplication.run(DemoApplication.class, args);

    PaymentAggregatorService aggregator = context.getBean(PaymentAggregatorService.class);

    // 사용 가능한 결제 수단 출력
    aggregator.showAvailableGateways();

    // 금액별 최적 결제사 선택
    aggregator.processWithBestGateway(500000);   // 50만원
    aggregator.processWithBestGateway(1500000);  // 150만원
}
```

#### 예상 출력

```
💳 사용 가능한 결제 수단:
   - 토스페이먼츠
   - 네이버페이

💡 최적의 결제 수단 선택 중...
✅ 선택된 결제사: 네이버페이
💳 네이버페이로 결제 처리: 500000원
✅ 결제 완료 - ID: NAVER-1234567890

💡 최적의 결제 수단 선택 중...
✅ 선택된 결제사: 토스페이먼츠
💳 토스페이먼츠로 결제 처리: 1500000원
✅ 결제 완료 - ID: TOSS-1234567891
```

#### 코드 설명

- **라인 13**: `List<PaymentGateway>`로 모든 구현체 주입
- **라인 16-20**: 모든 결제사 출력
- **라인 22-43**: 비즈니스 로직에 따라 최적의 결제사 선택

---

### 좋은 예 vs 나쁜 예

#### ❌ 나쁜 예: 필드 주입 사용

```java
// AntiPattern.java
@Service
public class BadOrderService {

    // 나쁜 예 1: 필드 주입
    @Autowired
    private PaymentService paymentService;  // final 불가

    @Autowired
    private ProductService productService;

    // 나쁜 예 2: 테스트 어려움
    public void createOrder() {
        paymentService.pay(1000);
    }
}

// 테스트 코드
class BadOrderServiceTest {
    @Test
    void testCreateOrder() {
        // 문제: new로 직접 생성 시 의존성 주입 불가
        BadOrderService service = new BadOrderService();
        // paymentService가 null → NullPointerException!

        // Reflection으로 주입해야 함 (복잡)
        Field field = BadOrderService.class.getDeclaredField("paymentService");
        field.setAccessible(true);
        field.set(service, mockPaymentService);
    }
}
```

**문제점**:
- 문제 1: **final 불가** - 불변성 보장 안 됨
- 문제 2: **테스트 복잡** - Reflection 필요
- 문제 3: **순환 참조 늦게 발견** - 런타임에만 에러

#### ✅ 좋은 예: 생성자 주입 + Lombok

```java
// GoodPattern.java
@Service
@RequiredArgsConstructor  // Lombok으로 생성자 자동 생성
public class GoodOrderService {

    // 좋은 예: 생성자 주입
    private final PaymentService paymentService;  // final 가능!
    private final ProductService productService;

    // Lombok이 자동으로 생성:
    // public GoodOrderService(PaymentService payment, ProductService product) {
    //     this.paymentService = payment;
    //     this.productService = product;
    // }

    public void createOrder() {
        paymentService.pay(1000);
    }
}

// 테스트 코드
class GoodOrderServiceTest {
    @Test
    void testCreateOrder() {
        // 장점: new로 직접 생성 가능 (Spring 없이도 테스트)
        PaymentService mockPayment = mock(PaymentService.class);
        ProductService mockProduct = mock(ProductService.class);

        GoodOrderService service = new GoodOrderService(mockPayment, mockProduct);

        // 테스트 실행
        service.createOrder();

        // 검증
        verify(mockPayment).pay(1000);
    }
}
```

**장점**:
- 장점 1: **final 가능** - 불변성 보장, NPE 방지
- 장점 2: **테스트 쉬움** - new로 직접 생성 가능
- 장점 3: **순환 참조 조기 발견** - 컴파일 타임에 에러
- 장점 4: **코드 간결** - Lombok으로 보일러플레이트 제거

#### 비교 표

| 항목 | 필드 주입 | 생성자 주입 |
|------|----------|------------|
| 코드 | `@Autowired private Service svc;` | `private final Service svc;` |
| 불변성 | ❌ final 불가 | ✅ final 가능 |
| 테스트 | ❌ Reflection 필요 | ✅ new로 생성 가능 |
| 순환 참조 | ❌ 런타임 발견 | ✅ 컴파일 타임 발견 |
| 권장 여부 | ❌ 비권장 | ✅ **강력 권장** |

---

**[← 이전: Part 2](04-2-DI-Part2.md)** | **[다음: Part 4 →](04-4-DI-Part4.md)**
