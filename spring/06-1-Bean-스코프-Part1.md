# 06장: Bean 스코프 (Bean Scope)

> **학습 목표**: 이 장을 완료하면 Singleton, Prototype 등 Bean 스코프의 차이를 이해하고, 상황에 맞는 스코프를 선택할 수 있습니다.

**⏱️ 예상 학습 시간**: 2-3시간
**난이도**: ⭐⭐⭐☆☆ (3개/5개)

---

## 📚 목차
- [왜 이 기술이 필요한가](#왜-이-기술이-필요한가)
- [실생활 비유로 이해하기](#실생활-비유로-이해하기)
- [핵심 개념](#핵심-개념)
- [기본 실습](#기본-실습)
- [실무 활용 사례](#실무-활용-사례)
- [FAQ](#faq)
- [면접 질문 리스트](#면접-질문-리스트)
- [핵심 정리](#핵심-정리)

---

## 🤔 왜 이 기술이 필요한가?

### 실무 배경
**온라인 쇼핑몰에서 장바구니는 사용자마다 독립적이어야 하는데, 모든 사용자가 같은 장바구니를 공유한다면?**

#### ❌ 이 기술을 모르면 발생하는 문제

```
문제 1: 상태 공유로 인한 데이터 오염
- 증상: Singleton Bean에 사용자별 데이터 저장 → 모든 사용자가 공유
- 영향: A 사용자 장바구니에 B 사용자 상품이 보임
- 비용: 개인정보 유출, 서비스 신뢰도 추락

문제 2: 메모리 낭비
- 증상: 요청마다 새 Bean 생성 (Prototype) → 메모리 급증
- 영향: 단순 Util 클래스도 매번 생성 → 불필요한 GC
- 비용: 서버 메모리 부족, 성능 저하

문제 3: 동시성 문제
- 증상: Singleton Bean에 mutable 상태 저장
- 영향: Race Condition, 데이터 불일치
- 비용: 예측 불가능한 버그, 재현 어려움
```

#### ✅ 이 기술을 사용하면

```
해결책 1: 적절한 스코프 선택
- 방법: 사용자별 데이터는 Request/Session 스코프
- 효과: 사용자 간 데이터 격리, 안전한 상태 관리
- 절감: 데이터 오염 제로

해결책 2: 성능 최적화
- 방법: Stateless 서비스는 Singleton 유지
- 효과: 메모리 효율적, GC 부담 최소화
- 절감: 메모리 사용량 70% 감소

해결책 3: Thread-safe 보장
- 방법: Singleton은 Stateless, 상태는 별도 스코프
- 효과: 동시성 문제 원천 차단
- 절감: 동시성 버그 제로
```

### 📊 수치로 보는 효과

| 지표 | Before (잘못된 스코프) | After (적절한 스코프) | 개선율 |
|------|----------------------|---------------------|--------|
| 데이터 오염 | 월 50건 | 0건 | **100%↓** |
| 메모리 사용 | 4GB | 1.2GB | **70%↓** |
| 동시성 버그 | 월 10건 | 0건 | **100%↓** |
| GC 빈도 | 초당 10회 | 초당 2회 | **80%↓** |

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 공용 vs 개인 물품

```
Singleton Scope = 공용 프린터
- 사무실에 프린터 1대
- 모든 직원이 공유
- 상태를 가지면 안 됨 (Stateless)
- 메모리 효율적

Prototype Scope = 개인 컵
- 직원마다 자기 컵
- 각자 관리 (Spring이 관리 안 함)
- 상태를 가질 수 있음 (Stateful)
- 독립적

Request Scope = 일회용 컵
- 요청마다 새 컵
- 사용 후 자동 폐기
- HTTP 요청마다 새로 생성

Session Scope = 사물함
- 사용자마다 사물함 1개
- 로그인 동안 유지
- 로그아웃 시 정리

┌─────────────────────────────────┐
│     Singleton (공용 프린터)      │
│  [프린터] ← 모든 직원이 사용    │
│  → 상태 없음 (Stateless)        │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│     Prototype (개인 컵)         │
│  직원1 [컵1]                    │
│  직원2 [컵2]                    │
│  직원3 [컵3]                    │
│  → 각자 상태 관리               │
└─────────────────────────────────┘
```

### 비유 2: 도서관 시스템

```
Singleton = 도서관 건물
- 도서관은 1개만 존재
- 모든 회원이 공유
- 상태 없음 (도서관 자체는 데이터 저장 안 함)

Prototype = 대출 신청서
- 대출할 때마다 새 신청서
- 각 신청서는 독립적
- 작성 후 제출

Request = 임시 열람권
- 방문할 때마다 새 열람권
- 퇴실 시 반납
- 하루만 유효

Session = 회원증
- 회원마다 회원증 1개
- 유효 기간 동안 유지
- 갱신 또는 탈퇴 시 폐기

┌──────────────────────────────┐
│  도서관 (Singleton)          │
│  ┌────────────────────────┐  │
│  │ 회원1 → 대출 (Prototype)│  │
│  │ 회원2 → 대출 (Prototype)│  │
│  │ 회원3 → 대출 (Prototype)│  │
│  └────────────────────────┘  │
└──────────────────────────────┘
```

### 비유 3: 택시 vs 자가용

```
Singleton = 버스
- 버스 1대를 여러 승객이 공유
- 상태를 가지면 안 됨 (좌석 지정석 아님)
- 효율적 (1대로 많은 사람 수송)

Prototype = 택시
- 손님마다 새 택시
- 독립적 (다른 손님과 섞이지 않음)
- 비효율적 (승객 1명당 택시 1대)

Request = 대리운전
- 요청마다 새 기사
- 목적지 도착 후 종료
- 일회성

Session = 렌터카
- 대여 기간 동안 전용 차량
- 반납 시까지 유지
- 기간제

매핑:
버스 = Singleton Bean (공유, Stateless)
택시 = Prototype Bean (독립, Stateful 가능)
대리운전 = Request Scope (일회성)
렌터카 = Session Scope (기간제)
```

### 비유 4: 카페 좌석

```
Singleton = 공용 작업대
- 카페에 작업대 1개
- 모든 손님이 번갈아 사용
- 개인 물건 두면 안 됨

Prototype = 주문 번호표
- 주문마다 새 번호표
- 독립적으로 관리
- 받고 버림

Request = 일회용 컵
- 주문마다 새 컵
- 사용 후 버림

Session = 마일리지 카드
- 손님마다 카드 1개
- 방문 시마다 적립
- 손님별로 유지
```

### 비유 5: 호텔 객실

```
Singleton = 호텔 로비
- 로비 1개, 모든 투숙객 공유
- 개인 물건 두면 안 됨
- Stateless

Prototype = 일회용 칫솔
- 투숙객마다 새 칫솔
- 독립적
- 사용 후 버림

Request = 엘리베이터 탑승
- 탑승마다 독립적
- 목적지 도착 후 종료

Session = 객실 키카드
- 투숙객마다 키카드 1개
- 체크아웃 시까지 유지
- 객실 번호와 연결

┌──────────────────────────────┐
│  호텔 (애플리케이션)         │
│  ┌────────────────────────┐  │
│  │ 로비 (Singleton)       │  │
│  │  - 공용 공간           │  │
│  └────────────────────────┘  │
│  ┌────────────────────────┐  │
│  │ 객실 (Session)         │  │
│  │  - 투숙객 전용         │  │
│  └────────────────────────┘  │
└──────────────────────────────┘
```

### 🎯 종합 비교표

```
┌──────────────┬────────────┬────────────┬────────────┐
│ 스코프       │ 실생활     │ 생명주기   │ 사용 예    │
├──────────────┼────────────┼────────────┼────────────┤
│ Singleton    │ 버스       │ 컨테이너   │ Service    │
│ Prototype    │ 택시       │ 요청마다   │ Command    │
│ Request      │ 대리운전   │ HTTP 요청  │ 요청 정보  │
│ Session      │ 렌터카     │ HTTP 세션  │ 장바구니   │
│ Application  │ 건물       │ 서블릿 Ctx │ 설정       │
│ WebSocket    │ 전화 통화  │ WS 연결    │ 채팅방     │
└──────────────┴────────────┴────────────┴────────────┘
```

---

## 📖 핵심 개념

### Bean 스코프 종류

```
┌─────────────────────────────────────────────────────────┐
│              Spring Bean Scope 종류                     │
└─────────────────────────────────────────────────────────┘

1️⃣ Singleton (기본값) ⭐⭐⭐⭐⭐
   - 컨테이너당 Bean 인스턴스 1개
   - 모든 요청에 대해 같은 인스턴스 반환
   - Stateless 해야 함
   - 사용률: 95%

2️⃣ Prototype ⭐⭐⭐
   - 요청할 때마다 새 인스턴스 생성
   - 생명주기를 Spring이 관리 안 함 (생성만)
   - Stateful 가능
   - 사용률: 3%

3️⃣ Request (Web) ⭐⭐⭐⭐
   - HTTP 요청마다 Bean 인스턴스 1개
   - 요청 처리 완료 시 소멸
   - 웹 애플리케이션에서만 사용
   - 사용률: 1.5%

4️⃣ Session (Web) ⭐⭐⭐⭐
   - HTTP 세션마다 Bean 인스턴스 1개
   - 세션 종료 시 소멸
   - 로그인 정보, 장바구니 등
   - 사용률: 0.4%

5️⃣ Application (Web) ⭐
   - ServletContext당 Bean 인스턴스 1개
   - 웹 애플리케이션 전체에서 공유
   - Singleton과 유사하지만 범위가 ServletContext
   - 사용률: 0.1%

6️⃣ WebSocket ⭐
   - WebSocket 세션마다 Bean 인스턴스 1개
   - WebSocket 연결 종료 시 소멸
   - 사용률: < 0.1%
```

### Singleton Scope (기본값)

```java
// 기본값이므로 @Scope 생략 가능
@Service  // @Scope("singleton") 생략
public class UserService {
    // 애플리케이션 전체에서 1개 인스턴스만 존재
}

// 명시적으로 지정
@Service
@Scope("singleton")
public class ProductService {
    // ...
}

// 주의: Singleton은 Stateless 해야 함!
@Service
public class BadService {
    private int count = 0;  // ❌ 위험! 모든 요청이 공유

    public void increment() {
        count++;  // Race Condition 발생 가능
    }
}

// 올바른 Singleton (Stateless)
@Service
public class GoodService {
    // 상태 없음, 메서드만 제공
    public int calculate(int a, int b) {
        return a + b;
    }
}
```

### Prototype Scope

```java
@Component
@Scope("prototype")  // 또는 ConfigurableBeanFactory.SCOPE_PROTOTYPE
public class ShoppingCart {
    private List<Item> items = new ArrayList<>();

    // 상태를 가질 수 있음
    public void addItem(Item item) {
        items.add(item);
    }
}

// 사용
@Service
public class OrderService {
    @Autowired
    private ApplicationContext context;

    public void createOrder() {
        // 매번 새 ShoppingCart 생성
        ShoppingCart cart1 = context.getBean(ShoppingCart.class);
        ShoppingCart cart2 = context.getBean(ShoppingCart.class);

        System.out.println(cart1 == cart2);  // false (다른 인스턴스)
    }
}

// 주의: Prototype Bean은 Spring이 소멸 관리 안 함!
// @PreDestroy가 호출되지 않음
```

### Request Scope (Web)

```java
@Component
@Scope(value = WebApplicationContext.SCOPE_REQUEST,
       proxyMode = ScopedProxyMode.TARGET_CLASS)
public class RequestContext {
    private String requestId;
    private LocalDateTime requestTime;

    @PostConstruct
    public void init() {
        this.requestId = UUID.randomUUID().toString();
        this.requestTime = LocalDateTime.now();
    }

    // Getter/Setter
}

// 사용
@RestController
public class UserController {
    @Autowired
    private RequestContext requestContext;  // HTTP 요청마다 다른 인스턴스

    @GetMapping("/user")
    public String getUser() {
        String requestId = requestContext.getRequestId();
        return "Request ID: " + requestId;
    }
}

// proxyMode가 필요한 이유:
// Singleton Controller에 Request-scoped Bean 주입 시
// Proxy를 통해 현재 요청의 Bean을 참조
```

### Session Scope (Web)

```java
@Component
@Scope(value = WebApplicationContext.SCOPE_SESSION,
       proxyMode = ScopedProxyMode.TARGET_CLASS)
public class ShoppingCartSession {
    private List<Item> items = new ArrayList<>();
    private String userId;

    public void addItem(Item item) {
        items.add(item);
    }

    public List<Item> getItems() {
        return items;
    }
}

// 사용
@RestController
public class CartController {
    @Autowired
    private ShoppingCartSession cart;  // 세션마다 다른 인스턴스

    @PostMapping("/cart")
    public void addToCart(@RequestBody Item item) {
        cart.addItem(item);  // 현재 사용자의 장바구니에 추가
    }

    @GetMapping("/cart")
    public List<Item> getCart() {
        return cart.getItems();  // 현재 사용자의 장바구니 조회
    }
}
```

### 스코프 비교표

| 스코프 | 생명주기 | 인스턴스 수 | Stateful | Spring 관리 | 주요 용도 |
|--------|---------|------------|----------|------------|-----------|
| **Singleton** | 컨테이너 | 1개 | ❌ | ✅ | Service, Repository |
| **Prototype** | 요청마다 | 요청마다 | ✅ | ⚠️ (생성만) | Command, Builder |
| **Request** | HTTP 요청 | 요청마다 | ✅ | ✅ | 요청 정보, 로깅 |
| **Session** | HTTP 세션 | 세션마다 | ✅ | ✅ | 장바구니, 사용자 설정 |
| **Application** | ServletContext | 1개 | ❌ | ✅ | 전역 설정 |
| **WebSocket** | WS 연결 | 연결마다 | ✅ | ✅ | 채팅방, 실시간 |

---

**[다음: Part 2로 계속 →](06-2-Bean-스코프-Part2.md)**
