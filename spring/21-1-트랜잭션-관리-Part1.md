# 21장: 트랜잭션 관리 (Transaction Management)

> **학습 목표**: Spring의 선언적 트랜잭션 관리를 완벽히 이해하고, @Transactional 어노테이션을 활용하여 데이터 일관성을 보장하는 안전한 애플리케이션을 구축할 수 있습니다.

**⏱️ 예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐⭐☆ (4개/5개)

---

## 📚 목차
- [왜 트랜잭션 관리가 필요한가](#왜-트랜잭션-관리가-필요한가)
- [실생활 비유로 이해하기](#실생활-비유로-이해하기)
- [핵심 개념](#핵심-개념)
- [기본 실습](#기본-실습)
- [실무 활용 사례](#실무-활용-사례)
- [주니어 시나리오](#주니어-시나리오)
- [실전 프로젝트](#실전-프로젝트)
- [FAQ](#faq)
- [면접 질문 리스트](#면접-질문-리스트)
- [면접 질문 답안](#면접-질문-답안)
- [핵심 정리](#핵심-정리)

---

## 🤔 왜 트랜잭션 관리가 필요한가?

### 실무 배경
**온라인 쇼핑몰에서 상품을 구매하는 순간, 다음과 같은 작업들이 동시에 일어납니다:**

```
1. 재고 차감: products 테이블에서 재고 -1
2. 주문 생성: orders 테이블에 주문 정보 저장
3. 결제 처리: payments 테이블에 결제 정보 저장
4. 포인트 차감: users 테이블에서 포인트 차감
```

**만약 3번 결제 처리에서 에러가 발생하면?**
- ❌ 재고는 차감됨 (1번 성공)
- ❌ 주문은 생성됨 (2번 성공)
- ❌ 결제는 실패 (3번 실패)
- ❌ 포인트는 차감 안됨 (4번 실행 안됨)

**결과**: 돈은 받지 못했는데 재고는 빠지고 주문은 생성되는 심각한 데이터 불일치!

#### ❌ 트랜잭션 관리를 모르면 발생하는 문제

**문제 1: 데이터 불일치 (Data Inconsistency)**
```java
// ❌ 트랜잭션 없이 작성한 코드
public void createOrder(OrderRequest request) {
    // 1. 재고 차감
    productRepository.decreaseStock(request.getProductId(), request.getQuantity());

    // 2. 주문 생성
    Order order = orderRepository.save(new Order(request));

    // 3. 결제 처리 - 여기서 예외 발생!
    paymentService.processPayment(request.getPaymentInfo()); // Exception!

    // 4. 포인트 차감 - 실행되지 않음
    userRepository.decreasePoints(request.getUserId(), request.getUsedPoints());
}
```
- **증상**: 재고는 차감되고 주문은 생성되었지만 결제는 실패
- **영향**: 고객은 주문했다고 생각하지만 실제로는 결제 안됨, 재고만 감소
- **비용**: 고객 불만, CS 비용 증가, 재고 데이터 복구 비용

**문제 2: 동시성 문제 (Concurrency Issues)**
```java
// ❌ 동시에 마지막 1개 상품을 2명이 주문
// 사용자 A와 B가 동시에 재고 조회
int stock = productRepository.getStock(productId); // 둘 다 stock = 1을 조회

// 사용자 A: 재고 확인 후 주문 (성공)
if (stock >= 1) {
    productRepository.decreaseStock(productId, 1); // stock = 0
}

// 사용자 B: 재고 확인 후 주문 (성공) - 문제 발생!
if (stock >= 1) { // 여전히 stock = 1로 보임
    productRepository.decreaseStock(productId, 1); // stock = -1 (마이너스 재고!)
}
```
- **증상**: 재고가 -1이 되는 초과 판매 발생
- **영향**: 실제 재고는 없는데 주문은 받아버림
- **비용**: 재고 부족으로 배송 불가, 고객 환불 처리 비용

**문제 3: 부분 성공/실패 (Partial Success)**
```java
// ❌ 포인트 적립 시스템
public void earnPoints(Long userId, int points) {
    // 1. 포인트 증가
    userRepository.increasePoints(userId, points); // 성공

    // 2. 포인트 이력 저장 - 예외 발생!
    pointHistoryRepository.save(new PointHistory(userId, points)); // Exception!
}
```
- **증상**: 포인트는 증가했지만 이력은 저장 안됨
- **영향**: 포인트 지급 이력 추적 불가, 감사(Audit) 불가능
- **비용**: 회계 정산 오류, 고객 문의 증가

#### ✅ 트랜잭션 관리를 사용하면

**해결책 1: 원자성 보장 (Atomicity)**
```java
// ✅ @Transactional 적용
@Transactional
public void createOrder(OrderRequest request) {
    // 1. 재고 차감
    productRepository.decreaseStock(request.getProductId(), request.getQuantity());

    // 2. 주문 생성
    Order order = orderRepository.save(new Order(request));

    // 3. 결제 처리 - 예외 발생 시 전체 롤백!
    paymentService.processPayment(request.getPaymentInfo());

    // 4. 포인트 차감
    userRepository.decreasePoints(request.getUserId(), request.getUsedPoints());
}
```
- **방법**: @Transactional 어노테이션으로 전체 작업을 하나의 단위로 묶음
- **효과**: 중간에 예외 발생 시 모든 변경사항 자동 롤백
- **절감**: 데이터 정합성 유지, CS 비용 90% 감소

**해결책 2: 격리성 보장 (Isolation)**
```java
// ✅ 격리 수준 설정으로 동시성 문제 해결
@Transactional(isolation = Isolation.SERIALIZABLE)
public void createOrder(Long productId, int quantity) {
    // 트랜잭션 시작 시점에 재고를 잠금
    Product product = productRepository.findByIdWithLock(productId);

    if (product.getStock() < quantity) {
        throw new InsufficientStockException("재고 부족");
    }

    product.decreaseStock(quantity);
    productRepository.save(product);

    // 트랜잭션 종료 전까지 다른 트랜잭션은 대기
}
```
- **방법**: 격리 수준(Isolation Level) 설정으로 동시 접근 제어
- **효과**: 초과 판매 방지, 재고 정확성 100% 보장
- **절감**: 재고 관리 비용 80% 절감, 고객 불만 제로

**해결책 3: 일관성 보장 (Consistency)**
```java
// ✅ 계좌 이체 - 출금과 입금이 모두 성공해야 함
@Transactional
public void transfer(Long fromAccount, Long toAccount, BigDecimal amount) {
    // 1. 출금 계좌에서 차감
    accountRepository.withdraw(fromAccount, amount);

    // 2. 입금 계좌에 추가
    accountRepository.deposit(toAccount, amount);

    // 둘 다 성공하거나, 둘 다 실패 (원자성)
    // 총액은 항상 동일 (일관성)
}
```
- **방법**: 비즈니스 규칙(총액 불변)을 트랜잭션으로 보장
- **효과**: 데이터베이스 일관성 100% 유지
- **절감**: 데이터 복구 비용 제로

### 📊 수치로 보는 효과

| 지표 | Before (트랜잭션 없음) | After (트랜잭션 적용) | 개선율 |
|------|----------------------|---------------------|--------|
| 데이터 정합성 오류 | 주 50건 | 0건 | **100%↓** |
| 재고 불일치 건수 | 월 100건 | 0건 | **100%↓** |
| CS 문의 건수 | 일 30건 | 일 3건 | **90%↓** |
| 데이터 복구 시간 | 주 8시간 | 0시간 | **100%↓** |
| 고객 환불 비용 | 월 ₩5,000,000 | ₩100,000 | **98%↓** |
| 시스템 신뢰도 | 85% | 99.9% | **17%↑** |

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 은행 ATM 인출 작업

```
트랜잭션 = ATM에서 돈을 인출하는 전체 과정

┌─────────────────────────────────────┐
│        ATM 현금 인출 과정           │
├─────────────────────────────────────┤
│ 1. 카드 삽입 및 비밀번호 입력       │ <- 트랜잭션 시작
│    ↓                                │
│ 2. 계좌 잔액 확인                   │ <- 데이터 조회
│    ↓                                │
│ 3. 계좌에서 금액 차감               │ <- 데이터 수정
│    ↓                                │
│ 4. 현금 지급                        │ <- 물리적 작업
│    ↓                                │
│ 5. 영수증 출력                      │ <- 로그 기록
│    ↓                                │
│ ✅ 완료 (커밋)                      │ <- 트랜잭션 종료
│                                     │
│ ❌ 만약 4번(현금 지급) 실패 시:     │
│    → 3번(계좌 차감)도 취소!         │ <- 롤백
│    → 잔액 원상복구                  │
└─────────────────────────────────────┘
```

**비유 설명**:
- **트랜잭션 시작** = ATM 카드 삽입
- **작업 수행** = 계좌 차감 + 현금 지급
- **커밋(Commit)** = 모든 작업 성공 시 확정
- **롤백(Rollback)** = 현금 부족 등 실패 시 계좌 차감 취소

**핵심**: 돈은 나갔는데 계좌는 그대로? 그런 일은 없다! (원자성)

### 비유 2: 식당 주문 과정

```
트랜잭션 = 식당에서 음식을 주문하고 받는 전체 과정

┌─────────────────────────────────────┐
│          식당 주문 시나리오          │
├─────────────────────────────────────┤
│ 상황: 손님이 스테이크 세트 주문     │
│                                     │
│ [주방에서 조리]                     │
│ 1. 스테이크 조리 ✅                 │
│ 2. 샐러드 준비 ✅                   │
│ 3. 수프 준비 ✅                     │
│ 4. 빵 굽기 ❌ (빵이 떨어짐!)        │
│                                     │
│ [트랜잭션이 없다면]                 │
│ → 스테이크, 샐러드, 수프만 서빙     │
│ → 고객 불만 발생!                   │
│                                     │
│ [트랜잭션이 있다면]                 │
│ → 빵이 없으면 전체 주문 취소        │
│ → "죄송합니다. 세트 제공 불가"      │
│ → 또는 빵 준비 후 전체 서빙         │
└─────────────────────────────────────┘
```

**비유 설명**:
- **세트 메뉴** = 하나의 트랜잭션
- **모든 음식이 준비되어야 서빙** = 원자성 (All or Nothing)
- **손님 테이블에 음식 도착** = 커밋
- **재료 부족으로 주문 취소** = 롤백

### 비유 3: 온라인 게임 아이템 거래

```
트랜잭션 = 게임 내 아이템 거래

┌─────────────────────────────────────┐
│     게임 아이템 거래 시스템          │
├─────────────────────────────────────┤
│ 플레이어 A → 플레이어 B              │
│                                     │
│ [거래 내용]                         │
│ A: 전설 무기 → B에게 이전           │
│ B: 골드 10,000 → A에게 이전         │
│                                     │
│ [트랜잭션 처리]                     │
│ ┌─ 시작 ──────────────────┐         │
│ │ 1. A의 무기 제거        │         │
│ │ 2. B의 골드 차감        │         │
│ │ 3. B에게 무기 추가      │         │
│ │ 4. A에게 골드 추가      │         │
│ └─ 완료 ──────────────────┘         │
│                                     │
│ [만약 3번에서 서버 다운?]           │
│ ❌ 트랜잭션 X: 무기도 사라지고      │
│               골드도 사라짐!        │
│ ✅ 트랜잭션 O: 자동 롤백,          │
│               거래 전으로 복구      │
└─────────────────────────────────────┘
```

**비유 설명**:
- **거래 완료** = 양쪽 모두 아이템/골드 받음 (일관성)
- **서버 장애** = 자동 롤백으로 아이템 복구 (지속성)
- **동시 거래** = 다른 거래가 끼어들 수 없음 (격리성)

### 비유 4: 택배 배송 시스템

```
트랜잭션 = 택배 출고부터 배송 완료까지

┌─────────────────────────────────────┐
│         배달의민족 주문 처리         │
├─────────────────────────────────────┤
│                                     │
│ [주문 처리 단계]                    │
│ 1. 주문 접수          (orders)      │
│ 2. 결제 승인          (payments)    │
│ 3. 가게에 주문 전달    (notifications)│
│ 4. 배달비 정산        (settlements) │
│ 5. 포인트 적립        (points)      │
│                                     │
│ Propagation.REQUIRED                │
│ ┌───────────────────────────────┐   │
│ │ 모든 단계가 하나의 트랜잭션    │   │
│ │ 하나라도 실패 → 전체 롤백     │   │
│ └───────────────────────────────┘   │
│                                     │
│ Propagation.REQUIRES_NEW            │
│ ┌─────┐ ┌─────┐ ┌─────┐           │
│ │주문 │ │결제 │ │정산 │           │
│ └─────┘ └─────┘ └─────┘           │
│ 각각 독립적인 트랜잭션              │
│ 하나 실패해도 다른 건 유지          │
└─────────────────────────────────────┘
```

**비유 설명**:
- **주문 → 배송 완료** = 하나의 트랜잭션
- **중간에 실패** = 전체 주문 취소 (롤백)
- **배송 완료** = 트랜잭션 확정 (커밋)
- **배송 추적** = 격리성 (다른 사람이 내 주문 수정 못함)

### 비유 5: 비행기 예약 시스템

```
트랜잭션 Isolation Level = 비행기 좌석 예약

┌─────────────────────────────────────┐
│       항공권 예약 시스템             │
├─────────────────────────────────────┤
│                                     │
│ READ_UNCOMMITTED (격리 수준 낮음)   │
│ → 다른 사람이 예약 중인 좌석도 보임 │
│ → 예약 취소될 수 있는데 보임 (더티 리드)│
│                                     │
│ READ_COMMITTED (일반적)             │
│ → 예약 확정된 좌석만 보임           │
│ → 예약 중인 건은 안 보임            │
│                                     │
│ REPEATABLE_READ                     │
│ → 내가 조회 시작하면 좌석 현황 고정 │
│ → 다른 사람이 예약해도 내 화면은 유지│
│                                     │
│ SERIALIZABLE (격리 수준 높음)       │
│ → 내가 좌석 보는 동안 아무도 예약 못함│
│ → 완전히 순차적으로만 처리          │
└─────────────────────────────────────┘
```

**비유 설명**:
- **좌석 조회** = 데이터 읽기
- **예약 확정** = 트랜잭션 커밋
- **예약 취소** = 트랜잭션 롤백
- **격리 수준** = 동시 예약 시 충돌 방지 수준

### 🎯 종합 비교표

| 비유 | 트랜잭션 시작 | 커밋(성공) | 롤백(실패) | 핵심 속성 |
|------|--------------|-----------|-----------|----------|
| ATM | 카드 삽입 | 현금 지급 완료 | 현금 부족 시 계좌 복구 | 원자성 |
| 식당 주문 | 주문 접수 | 전체 서빙 | 재료 부족 시 취소 | 원자성 |
| 게임 거래 | 거래 시작 | 아이템 교환 | 서버 다운 시 복구 | 일관성 |
| 택배 배송 | 주문 접수 | 배송 완료 | 배송 실패 시 환불 | 지속성 |
| 비행기 예약 | 좌석 조회 | 예약 확정 | 결제 실패 시 취소 | 격리성 |

---

## 📖 핵심 개념

### 개념 설명 (3단계 깊이)

#### 1️⃣ 초보자 수준 설명

**트랜잭션이란?**
> "여러 개의 데이터베이스 작업을 하나의 묶음으로 처리하는 것"

**쉬운 설명**:
```
트랜잭션 = 택배 상자

물건 10개를 따로따로 보내면?
→ 일부는 도착, 일부는 분실 가능

물건 10개를 하나의 택배 상자에 넣으면?
→ 전부 도착하거나, 전부 반송됨
→ 일부만 도착하는 일은 없음!
```

**Spring에서 사용법**:
```java
// 메서드에 @Transactional만 붙이면 끝!
@Transactional
public void createOrder(Order order) {
    orderRepository.save(order);      // 1. 주문 저장
    stockRepository.decrease(stock);   // 2. 재고 차감
    paymentService.process(payment);   // 3. 결제 처리

    // 하나라도 실패하면 전부 취소!
}
```

#### 2️⃣ 중급자 수준 설명

**ACID 속성 이해**

**A - Atomicity (원자성)**
```java
@Transactional
public void transferMoney(Long from, Long to, BigDecimal amount) {
    Account fromAccount = accountRepository.findById(from).orElseThrow();
    Account toAccount = accountRepository.findById(to).orElseThrow();

    fromAccount.withdraw(amount);  // 1. 출금
    toAccount.deposit(amount);      // 2. 입금

    // 둘 다 성공하거나, 둘 다 실패 (중간 상태 없음)
}
```

**C - Consistency (일관성)**
```java
// 비즈니스 규칙: 총 잔액은 항상 동일해야 함
// Before: A=10000, B=5000 → Total=15000
// After:  A=8000,  B=7000 → Total=15000 (일관성 유지)
```

**I - Isolation (격리성)**
```java
// 사용자 A와 B가 동시에 같은 계좌 조회
@Transactional(isolation = Isolation.REPEATABLE_READ)
public BigDecimal getBalance(Long accountId) {
    // A가 조회 중일 때 B가 입금해도
    // A는 계속 같은 잔액을 보게 됨
}
```

**D - Durability (지속성)**
```java
// 트랜잭션 커밋 후 서버가 다운되어도
// 데이터는 영구적으로 저장됨
@Transactional
public void saveOrder(Order order) {
    orderRepository.save(order);
    // 커밋 → 디스크에 영구 저장
}
```

**전파 속성 (Propagation)**
```java
// REQUIRED: 기존 트랜잭션 있으면 참여, 없으면 새로 생성 (기본값)
@Transactional(propagation = Propagation.REQUIRED)
public void method1() { }

// REQUIRES_NEW: 항상 새로운 트랜잭션 생성
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void method2() { }

// NESTED: 중첩 트랜잭션 (부분 롤백 가능)
@Transactional(propagation = Propagation.NESTED)
public void method3() { }
```

**격리 수준 (Isolation Level)**
```java
// READ_UNCOMMITTED: 커밋되지 않은 데이터도 읽기 가능 (더티 리드)
@Transactional(isolation = Isolation.READ_UNCOMMITTED)

// READ_COMMITTED: 커밋된 데이터만 읽기 가능 (기본값)
@Transactional(isolation = Isolation.READ_COMMITTED)

// REPEATABLE_READ: 같은 데이터 반복 읽기 시 동일한 값 보장
@Transactional(isolation = Isolation.REPEATABLE_READ)

// SERIALIZABLE: 완전한 격리, 동시성 최저
@Transactional(isolation = Isolation.SERIALIZABLE)
```

#### 3️⃣ 고급자 수준 설명

**프록시 기반 AOP 동작 원리**

```java
// 실제 코드
@Service
public class OrderService {
    @Transactional
    public void createOrder(Order order) {
        orderRepository.save(order);
    }
}

// Spring이 생성하는 프록시 코드 (개념적)
public class OrderServiceProxy extends OrderService {
    private PlatformTransactionManager txManager;
    private OrderService target;

    @Override
    public void createOrder(Order order) {
        TransactionStatus status = txManager.getTransaction(new DefaultTransactionDefinition());
        try {
            target.createOrder(order);  // 실제 메서드 호출
            txManager.commit(status);    // 성공 시 커밋
        } catch (Exception e) {
            txManager.rollback(status);  // 예외 시 롤백
            throw e;
        }
    }
}
```

**내부 호출 문제 (Self-Invocation)**
```java
@Service
public class UserService {

    @Transactional
    public void method1() {
        // ...
        method2(); // ❌ 이 호출은 프록시를 거치지 않음!
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void method2() {
        // REQUIRES_NEW가 적용되지 않음!
    }
}

// ✅ 해결 방법 1: 별도 서비스로 분리
@Service
public class UserService {
    @Autowired
    private UserInternalService internalService;

    @Transactional
    public void method1() {
        internalService.method2(); // ✅ 프록시를 통해 호출
    }
}

// ✅ 해결 방법 2: AopContext 사용
@Service
@EnableAspectJAutoProxy(exposeProxy = true)
public class UserService {
    @Transactional
    public void method1() {
        ((UserService) AopContext.currentProxy()).method2(); // ✅ 프록시 호출
    }
}
```

**분산 트랜잭션 (Distributed Transaction)**
```java
// JTA (Java Transaction API) 사용
@Configuration
public class JtaConfig {
    @Bean
    public PlatformTransactionManager transactionManager() {
        return new JtaTransactionManager();
    }
}

@Service
public class DistributedService {
    @Autowired
    private DataSource db1;  // MySQL

    @Autowired
    private DataSource db2;  // PostgreSQL

    @Transactional
    public void distributedOperation() {
        // 두 개의 다른 DB에 대한 작업을 하나의 트랜잭션으로
        jdbcTemplate1.update("INSERT INTO db1.table ...");
        jdbcTemplate2.update("INSERT INTO db2.table ...");

        // 2-Phase Commit으로 원자성 보장
    }
}
```

**트랜잭션 동기화 (Transaction Synchronization)**
```java
@Service
public class EmailService {

    @Transactional
    public void createUserAndSendEmail(User user) {
        userRepository.save(user);

        // ❌ 트랜잭션 커밋 전에 이메일 발송
        // → 커밋 실패 시 이메일만 발송되는 문제
        // emailService.send(user.getEmail());

        // ✅ 트랜잭션 커밋 후에 이메일 발송
        TransactionSynchronizationManager.registerSynchronization(
            new TransactionSynchronization() {
                @Override
                public void afterCommit() {
                    emailService.send(user.getEmail());
                }
            }
        );
    }
}

// 또는 @TransactionalEventListener 사용
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
public void handleUserCreated(UserCreatedEvent event) {
    emailService.send(event.getUser().getEmail());
}
```

**락(Lock) 전략**
```java
// 낙관적 락 (Optimistic Lock)
@Entity
public class Product {
    @Id
    private Long id;

    @Version  // JPA가 자동으로 버전 관리
    private Long version;

    private Integer stock;
}

// 충돌 발생 시 OptimisticLockException
// → 재시도 로직 필요

// 비관적 락 (Pessimistic Lock)
public interface ProductRepository extends JpaRepository<Product, Long> {
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT p FROM Product p WHERE p.id = :id")
    Optional<Product> findByIdWithLock(@Param("id") Long id);
}

@Transactional
public void decreaseStock(Long productId, int quantity) {
    Product product = productRepository.findByIdWithLock(productId)
        .orElseThrow();
    product.decreaseStock(quantity);
    // 트랜잭션 종료 전까지 다른 트랜잭션은 대기 (FOR UPDATE)
}
```

### 주요 용어 정리

| 용어 | 영문 | 설명 | 예시 |
|------|------|------|------|
| 트랜잭션 | Transaction | 데이터베이스 작업의 논리적 단위 | 주문 생성 + 재고 차감 |
| 커밋 | Commit | 트랜잭션의 변경사항을 영구 저장 | 주문 확정 |
| 롤백 | Rollback | 트랜잭션의 변경사항을 취소 | 결제 실패 시 주문 취소 |
| 원자성 | Atomicity | 전부 성공 또는 전부 실패 | 계좌 이체 (출금+입금) |
| 일관성 | Consistency | 비즈니스 규칙 유지 | 총 잔액 불변 |
| 격리성 | Isolation | 동시 실행 트랜잭션 간 독립성 | 좌석 예약 시 충돌 방지 |
| 지속성 | Durability | 커밋 후 영구 보존 | 정전 후에도 데이터 유지 |
| 전파 속성 | Propagation | 트랜잭션 경계 설정 방식 | REQUIRED, REQUIRES_NEW |
| 격리 수준 | Isolation Level | 동시성 제어 강도 | READ_COMMITTED |
| 더티 리드 | Dirty Read | 커밋되지 않은 데이터 읽기 | 예약 중인 좌석 보기 |
| 팬텀 리드 | Phantom Read | 범위 조회 시 새 행 출현 | 통계 집계 중 신규 데이터 |

### 기술 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                  Spring Transaction Architecture                 │
└─────────────────────────────────────────────────────────────────┘

         [Application Code]
                │
                │ @Transactional
                ↓
    ┌───────────────────────────┐
    │   Transaction Proxy       │
    │  (AOP-based Interceptor)  │
    └───────────────────────────┘
                │
                │ 1. getTransaction()
                ↓
    ┌───────────────────────────┐
    │ PlatformTransactionManager│  ← 인터페이스
    └───────────────────────────┘
                │
        ┌───────┴───────┬───────────────┐
        │               │               │
        ↓               ↓               ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│DataSourceTx  │ │JpaTransaction│ │JtaTransaction│
│Manager       │ │Manager       │ │Manager       │
└──────────────┘ └──────────────┘ └──────────────┘
        │               │               │
        │               │               │
        ↓               ↓               ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  JDBC        │ │  JPA/        │ │  Distributed │
│  Connection  │ │  Hibernate   │ │  Transaction │
└──────────────┘ └──────────────┘ └──────────────┘
        │               │               │
        └───────┬───────┴───────┬───────┘
                │               │
                ↓               ↓
        ┌──────────────┐ ┌──────────────┐
        │  Database 1  │ │  Database 2  │
        └──────────────┘ └──────────────┘

설명:
1. @Transactional 메서드 호출 시 프록시가 가로챔
2. TransactionManager가 트랜잭션 시작
3. 실제 비즈니스 로직 실행
4. 성공 시 commit(), 예외 시 rollback()
5. Connection/Session 관리는 TransactionManager가 담당
```

**트랜잭션 전파 흐름**

```
┌─────────────────────────────────────────────────────────────────┐
│              Transaction Propagation Flow                        │
└─────────────────────────────────────────────────────────────────┘

[REQUIRED - 기본값]
methodA()                    methodB()
  │                            │
  │ @Transactional            │ @Transactional(REQUIRED)
  ├─ TX 시작 ─────────────────┤
  │                            │
  │                            │ 기존 TX 참여
  │                            │
  │←─────────────────────────┘
  │
  ├─ 커밋/롤백


[REQUIRES_NEW - 새 트랜잭션]
methodA()                    methodB()
  │                            │
  │ @Transactional            │ @Transactional(REQUIRES_NEW)
  ├─ TX1 시작 ────────────┐   │
  │                       │   ├─ TX1 일시 중단
  │                       │   │
  │                       │   ├─ TX2 시작 (새 트랜잭션)
  │                       │   │
  │                       │   │  ... 작업 ...
  │                       │   │
  │                       │   ├─ TX2 커밋/롤백
  │                       │   │
  │                       └───┤─ TX1 재개
  │                            │
  │←──────────────────────────┘
  │
  ├─ TX1 커밋/롤백


[NESTED - 중첩 트랜잭션]
methodA()                    methodB()
  │                            │
  │ @Transactional            │ @Transactional(NESTED)
  ├─ TX 시작 ─────────────────┤
  │                            │
  │                            ├─ Savepoint 생성
  │                            │
  │                            │  ... 작업 ...
  │                            │
  │                            │  예외 발생 시
  │                            ├─ Savepoint로 롤백
  │←──────────────────────────┘  (TX는 유지)
  │
  ├─ 커밋 (전체 반영)
```

---

## 💻 기본 실습

### 📋 사전 체크리스트

```bash
# 1. Spring Boot 프로젝트 생성 확인
# build.gradle 또는 pom.xml에 다음 의존성 확인

# Gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-web'
    runtimeOnly 'com.h2database:h2'  // 또는 사용 중인 DB
}

# Maven
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>

# 2. 트랜잭션 활성화 확인
# Spring Boot는 자동으로 활성화되지만, 명시적으로 설정하려면:
@EnableTransactionManagement  // 메인 클래스에 추가 (선택사항)
```

### 실습 1: 기본 @Transactional 사용

**난이도**: ⭐⭐☆☆☆

#### 시나리오
간단한 주문 생성 시스템을 만들어 트랜잭션의 기본 동작을 이해합니다.

#### 1단계: Entity 생성

```java
// Order.java
package com.example.demo.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "orders")
@Getter
@Setter
@NoArgsConstructor
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String productName;

    @Column(nullable = false)
    private Integer quantity;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal totalPrice;

    @Column(nullable = false)
    private String status;  // PENDING, COMPLETED, FAILED

    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        if (status == null) {
            status = "PENDING";
        }
    }
}

// Product.java
package com.example.demo.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "products")
@Getter
@Setter
@NoArgsConstructor
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private Integer stock;

    public void decreaseStock(int quantity) {
        if (this.stock < quantity) {
            throw new RuntimeException("재고 부족: 현재 재고 " + this.stock);
        }
        this.stock -= quantity;
    }
}
```

#### 2단계: Repository 생성

```java
// OrderRepository.java
package com.example.demo.repository;

import com.example.demo.entity.Order;
import org.springframework.data.jpa.repository.JpaRepository;

public interface OrderRepository extends JpaRepository<Order, Long> {
}

// ProductRepository.java
package com.example.demo.repository;

import com.example.demo.entity.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface ProductRepository extends JpaRepository<Product, Long> {
    Optional<Product> findByName(String name);
}
```

#### 3단계: Service 작성 (트랜잭션 적용)

```java
// OrderService.java
package com.example.demo.service;

import com.example.demo.entity.Order;
import com.example.demo.entity.Product;
import com.example.demo.repository.OrderRepository;
import com.example.demo.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;

@Service
@RequiredArgsConstructor
@Slf4j
public class OrderService {

    private final OrderRepository orderRepository;
    private final ProductRepository productRepository;

    /**
     * ✅ 트랜잭션 적용: 주문 생성 + 재고 차감
     * - 재고 차감 실패 시 주문도 자동 롤백
     */
    @Transactional
    public Order createOrder(String productName, int quantity, BigDecimal unitPrice) {
        log.info("주문 생성 시작: 상품={}, 수량={}", productName, quantity);

        // 1. 상품 조회
        Product product = productRepository.findByName(productName)
            .orElseThrow(() -> new RuntimeException("상품을 찾을 수 없습니다: " + productName));

        // 2. 재고 차감 (예외 발생 가능)
        product.decreaseStock(quantity);
        productRepository.save(product);
        log.info("재고 차감 완료: {} -> {}", product.getStock() + quantity, product.getStock());

        // 3. 주문 생성
        Order order = new Order();
        order.setProductName(productName);
        order.setQuantity(quantity);
        order.setTotalPrice(unitPrice.multiply(BigDecimal.valueOf(quantity)));
        order.setStatus("COMPLETED");

        Order savedOrder = orderRepository.save(order);
        log.info("주문 생성 완료: id={}", savedOrder.getId());

        return savedOrder;
    }

    /**
     * ❌ 트랜잭션 없음: 재고 차감 후 주문 실패 시 재고만 차감됨
     */
    public Order createOrderWithoutTransaction(String productName, int quantity, BigDecimal unitPrice) {
        log.info("(트랜잭션 없음) 주문 생성 시작");

        // 1. 재고 차감
        Product product = productRepository.findByName(productName)
            .orElseThrow(() -> new RuntimeException("상품을 찾을 수 없습니다"));
        product.decreaseStock(quantity);
        productRepository.save(product);

        // 2. 주문 생성 전 예외 발생 시뮬레이션
        if (quantity > 5) {
            throw new RuntimeException("5개 초과 주문 불가");  // 재고는 이미 차감됨!
        }

        Order order = new Order();
        order.setProductName(productName);
        order.setQuantity(quantity);
        order.setTotalPrice(unitPrice.multiply(BigDecimal.valueOf(quantity)));

        return orderRepository.save(order);
    }
}
```

#### 4단계: 테스트 코드 작성

```java
// OrderServiceTest.java
package com.example.demo.service;

import com.example.demo.entity.Order;
import com.example.demo.entity.Product;
import com.example.demo.repository.OrderRepository;
import com.example.demo.repository.ProductRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;

import static org.assertj.core.api.Assertions.*;

@SpringBootTest
class OrderServiceTest {

    @Autowired
    private OrderService orderService;

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private OrderRepository orderRepository;

    @BeforeEach
    void setUp() {
        // 테스트용 상품 데이터 생성
        orderRepository.deleteAll();
        productRepository.deleteAll();

        Product product = new Product();
        product.setName("노트북");
        product.setStock(10);
        productRepository.save(product);
    }

    @Test
    @Transactional
    void 트랜잭션_적용_정상_주문() {
        // given
        String productName = "노트북";
        int quantity = 3;
        BigDecimal unitPrice = BigDecimal.valueOf(1000000);

        // when
        Order order = orderService.createOrder(productName, quantity, unitPrice);

        // then
        assertThat(order.getId()).isNotNull();
        assertThat(order.getStatus()).isEqualTo("COMPLETED");

        // 재고 확인
        Product product = productRepository.findByName(productName).orElseThrow();
        assertThat(product.getStock()).isEqualTo(7);  // 10 - 3 = 7
    }

    @Test
    @Transactional
    void 트랜잭션_적용_재고_부족_시_롤백() {
        // given
        String productName = "노트북";
        int quantity = 15;  // 재고보다 많이 주문
        BigDecimal unitPrice = BigDecimal.valueOf(1000000);

        // when & then
        assertThatThrownBy(() ->
            orderService.createOrder(productName, quantity, unitPrice)
        ).isInstanceOf(RuntimeException.class)
         .hasMessageContaining("재고 부족");

        // 롤백 확인: 재고는 그대로
        Product product = productRepository.findByName(productName).orElseThrow();
        assertThat(product.getStock()).isEqualTo(10);

        // 주문도 생성되지 않음
        assertThat(orderRepository.count()).isZero();
    }
}
```

#### 실행 결과

```
✅ 정상 주문 케이스:
2024-01-15 10:30:00 INFO  - 주문 생성 시작: 상품=노트북, 수량=3
2024-01-15 10:30:00 INFO  - 재고 차감 완료: 10 -> 7
2024-01-15 10:30:00 INFO  - 주문 생성 완료: id=1
2024-01-15 10:30:00 DEBUG - Committing JPA transaction

재고: 10 → 7
주문: 생성됨 (id=1, status=COMPLETED)

---

❌ 재고 부족 케이스:
2024-01-15 10:31:00 INFO  - 주문 생성 시작: 상품=노트북, 수량=15
2024-01-15 10:31:00 ERROR - 재고 부족: 현재 재고 10
2024-01-15 10:31:00 DEBUG - Rolling back JPA transaction

재고: 10 (변경 없음)
주문: 생성 안됨
→ 트랜잭션 롤백으로 모든 작업 취소!
```

#### 코드 설명

**@Transactional 적용**:
```java
@Transactional  // ← 이 어노테이션이 트랜잭션 경계를 설정
public Order createOrder(...) {
    // 1. 재고 차감
    product.decreaseStock(quantity);  // DB 업데이트 1

    // 2. 주문 생성
    orderRepository.save(order);      // DB 삽입 2

    // 3. 두 작업이 하나의 트랜잭션으로 묶임
    //    → 하나라도 실패하면 둘 다 롤백
}
```

**프록시 동작 흐름**:
```
클라이언트
    ↓
OrderServiceProxy (Spring이 생성)
    ↓
1. TransactionManager.getTransaction()  // TX 시작
    ↓
2. 실제 OrderService.createOrder() 실행
    ↓
3-a. 성공 → commit()
3-b. 예외 → rollback()
```

### 실습 2: 전파 속성 (Propagation) 실습

**난이도**: ⭐⭐⭐⭐☆

#### 시나리오
주문 생성 시 포인트 적립 로그는 주문 실패 여부와 무관하게 항상 남기고 싶습니다.

#### 코드

```java
// PointService.java
package com.example.demo.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

@Service
@Slf4j
public class PointService {

    /**
     * REQUIRES_NEW: 항상 새로운 트랜잭션 생성
     * - 부모 트랜잭션이 롤백되어도 이 메서드는 커밋됨
     */
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void recordPointLog(Long userId, int points, String reason) {
        log.info("[별도 트랜잭션] 포인트 로그 기록: userId={}, points={}, reason={}",
                 userId, points, reason);

        // 포인트 로그를 DB에 저장
        // pointLogRepository.save(new PointLog(userId, points, reason));

        log.info("[별도 트랜잭션] 포인트 로그 커밋 완료");
    }

    /**
     * REQUIRED: 기존 트랜잭션에 참여 (기본값)
     * - 부모 트랜잭션이 롤백되면 함께 롤백됨
     */
    @Transactional(propagation = Propagation.REQUIRED)
    public void addPoints(Long userId, int points) {
        log.info("[같은 트랜잭션] 포인트 적립: userId={}, points={}", userId, points);

        // 사용자 포인트 증가
        // userRepository.increasePoints(userId, points);
    }
}

// OrderService.java (수정)
@Service
@RequiredArgsConstructor
@Slf4j
public class OrderService {

    private final OrderRepository orderRepository;
    private final ProductRepository productRepository;
    private final PointService pointService;

    @Transactional
    public Order createOrderWithPoint(String productName, int quantity,
                                       BigDecimal unitPrice, Long userId) {
        log.info("[주문 트랜잭션 시작]");

        // 1. 포인트 적립 로그 기록 (REQUIRES_NEW - 별도 트랜잭션)
        pointService.recordPointLog(userId, quantity * 100, "주문 시도");

        // 2. 상품 재고 차감
        Product product = productRepository.findByName(productName)
            .orElseThrow(() -> new RuntimeException("상품 없음"));
        product.decreaseStock(quantity);
        productRepository.save(product);

        // 3. 주문 생성
        Order order = new Order();
        order.setProductName(productName);
        order.setQuantity(quantity);
        order.setTotalPrice(unitPrice.multiply(BigDecimal.valueOf(quantity)));
        order.setStatus("COMPLETED");

        Order savedOrder = orderRepository.save(order);

        // 4. 포인트 적립 (REQUIRED - 같은 트랜잭션)
        pointService.addPoints(userId, quantity * 100);

        // 5. 만약 여기서 예외 발생하면?
        if (quantity > 10) {
            log.error("[주문 트랜잭션 롤백!]");
            throw new RuntimeException("10개 초과 주문 불가");
        }

        log.info("[주문 트랜잭션 커밋]");
        return savedOrder;
    }
}
```

#### 테스트

```java
@Test
void 전파속성_REQUIRES_NEW_테스트() {
    // given
    Long userId = 1L;
    int quantity = 15;  // 10개 초과 → 예외 발생 예정

    // when
    assertThatThrownBy(() ->
        orderService.createOrderWithPoint("노트북", quantity,
                                          BigDecimal.valueOf(1000000), userId)
    ).isInstanceOf(RuntimeException.class);

    // then
    // 주문은 롤백되어 생성 안됨
    assertThat(orderRepository.count()).isZero();

    // ✅ 하지만 포인트 로그는 커밋됨! (REQUIRES_NEW)
    // assertThat(pointLogRepository.count()).isEqualTo(1);
}
```

#### 실행 결과

```
[주문 트랜잭션 시작]
  ↓
[별도 트랜잭션] 포인트 로그 기록: userId=1, points=1500
[별도 트랜잭션] 포인트 로그 커밋 완료  ← 여기서 커밋!
  ↓
재고 차감...
주문 생성...
  ↓
[주문 트랜잭션 롤백!]  ← 주문은 롤백
  ↓
결과:
- 주문: 생성 안됨 (롤백)
- 재고: 변경 안됨 (롤백)
- 포인트 로그: 저장됨! ✅ (이미 커밋됨)
```

#### 코드 설명

**전파 속성 비교**:

```java
// REQUIRED (기본값): 부모 트랜잭션에 참여
@Transactional(propagation = Propagation.REQUIRED)
public void method1() {
    // 외부에서 호출 시
    // - TX 있으면: 기존 TX 참여
    // - TX 없으면: 새 TX 생성
}

// REQUIRES_NEW: 항상 새 트랜잭션
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void method2() {
    // 외부에서 호출 시
    // - TX 있으면: 기존 TX 일시 중단, 새 TX 생성
    // - TX 없으면: 새 TX 생성
    // → 부모 트랜잭션과 독립적!
}

// NESTED: 중첩 트랜잭션 (SavePoint 사용)
@Transactional(propagation = Propagation.NESTED)
public void method3() {
    // SavePoint 생성
    // 롤백 시 SavePoint까지만 롤백
    // 부모 트랜잭션은 유지
}
```

**실무 활용**:
```java
@Transactional
public void processOrder(Order order) {
    // 1. 주문 처리 (중요)
    orderRepository.save(order);

    // 2. 알림 발송 로그 (덜 중요, 실패해도 주문은 유지)
    notificationService.sendOrderNotification(order);  // REQUIRES_NEW

    // 3. 알림 발송이 실패해도 주문은 커밋됨!
}
```

### 좋은 예 vs 나쁜 예

#### ❌ 나쁜 예 1: 트랜잭션 범위가 너무 큼

```java
@Transactional
public void processLargeDataBatch() {
    // ❌ 10만 건의 데이터를 하나의 트랜잭션으로 처리
    List<Data> dataList = dataRepository.findAll();  // 10만 건

    for (Data data : dataList) {
        data.process();
        dataRepository.save(data);
    }

    // 문제점:
    // 1. 트랜잭션이 너무 오래 유지됨 (수십 분)
    // 2. 메모리 부족 가능성
    // 3. DB 락이 오래 유지되어 다른 트랜잭션 블로킹
    // 4. 중간에 실패 시 전체 롤백 (수십 분 작업이 날아감)
}
```

#### ✅ 좋은 예 1: 배치 단위로 트랜잭션 분리

```java
public void processLargeDataBatch() {
    int batchSize = 1000;
    int page = 0;

    while (true) {
        // ✅ 1000건씩 별도 트랜잭션으로 처리
        List<Data> batch = processBatch(page, batchSize);
        if (batch.isEmpty()) break;
        page++;
    }
}

@Transactional
public List<Data> processBatch(int page, int size) {
    Pageable pageable = PageRequest.of(page, size);
    List<Data> dataList = dataRepository.findAll(pageable).getContent();

    for (Data data : dataList) {
        data.process();
    }

    return dataRepository.saveAll(dataList);
    // 1000건씩 커밋, 실패 시 1000건만 롤백
}
```

#### ❌ 나쁜 예 2: 읽기 전용 조회에 쓰기 트랜잭션

```java
@Transactional  // ❌ 기본값: readOnly=false (쓰기 가능)
public List<Order> getOrderList() {
    // 단순 조회인데 쓰기 트랜잭션 사용
    return orderRepository.findAll();

    // 문제점:
    // 1. 불필요한 락 획득
    // 2. Flush 비용 발생
    // 3. DB 리소스 낭비
}
```

#### ✅ 좋은 예 2: 읽기 전용 트랜잭션 사용

```java
@Transactional(readOnly = true)  // ✅ 읽기 전용 명시
public List<Order> getOrderList() {
    return orderRepository.findAll();

    // 장점:
    // 1. 불필요한 Flush 방지
    // 2. DB 최적화 힌트 제공
    // 3. 실수로 데이터 수정 방지
}
```

#### ❌ 나쁜 예 3: 내부 호출로 트랜잭션 미적용

```java
@Service
public class UserService {

    public void registerUser(User user) {
        saveUser(user);  // ❌ 내부 호출: 프록시 거치지 않음!
    }

    @Transactional
    public void saveUser(User user) {
        userRepository.save(user);
        // @Transactional이 적용되지 않음!
    }
}
```

#### ✅ 좋은 예 3: 외부에서 호출 또는 self-injection

```java
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final UserService self;  // ✅ 자기 자신 주입

    public void registerUser(User user) {
        self.saveUser(user);  // ✅ 프록시를 통해 호출
    }

    @Transactional
    public void saveUser(User user) {
        userRepository.save(user);
        // @Transactional 정상 적용!
    }
}
```

---

## 🏢 실무 활용 사례

### 실제 기업 활용 사례

#### 사례 1: 토스 - 금융 거래 트랜잭션 관리

```java
/**
 * 토스 송금 시스템
 * - 출금, 입금, 수수료, 이력 기록이 모두 하나의 트랜잭션으로 처리
 * - 하나라도 실패하면 전체 롤백
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class TossTransferService {

    private final AccountRepository accountRepository;
    private final TransferHistoryRepository transferHistoryRepository;
    private final FeeService feeService;

    @Transactional(isolation = Isolation.SERIALIZABLE)  // ✅ 최고 수준 격리
    public TransferResult transfer(TransferRequest request) {
        log.info("송금 시작: {} -> {}, 금액: {}",
                 request.getFromAccount(), request.getToAccount(), request.getAmount());

        // 1. 계좌 조회 및 잠금
        Account fromAccount = accountRepository.findByIdWithLock(request.getFromAccount())
            .orElseThrow(() -> new AccountNotFoundException("출금 계좌 없음"));
        Account toAccount = accountRepository.findByIdWithLock(request.getToAccount())
            .orElseThrow(() -> new AccountNotFoundException("입금 계좌 없음"));

        // 2. 잔액 확인
        BigDecimal totalAmount = request.getAmount().add(request.getFee());
        if (fromAccount.getBalance().compareTo(totalAmount) < 0) {
            throw new InsufficientBalanceException("잔액 부족");
        }

        // 3. 출금 처리
        fromAccount.withdraw(totalAmount);
        accountRepository.save(fromAccount);
        log.info("출금 완료: 계좌={}, 잔액={}", fromAccount.getId(), fromAccount.getBalance());

        // 4. 입금 처리
        toAccount.deposit(request.getAmount());
        accountRepository.save(toAccount);
        log.info("입금 완료: 계좌={}, 잔액={}", toAccount.getId(), toAccount.getBalance());

        // 5. 수수료 처리 (별도 트랜잭션)
        feeService.collectFee(request.getFee());

        // 6. 거래 이력 저장
        TransferHistory history = TransferHistory.builder()
            .fromAccountId(request.getFromAccount())
            .toAccountId(request.getToAccount())
            .amount(request.getAmount())
            .fee(request.getFee())
            .status("COMPLETED")
            .build();
        transferHistoryRepository.save(history);

        log.info("송금 완료: 이력 ID={}", history.getId());

        return TransferResult.success(history.getId());
    }
}

// 실제 성과:
// - 송금 실패율: 0.001% 미만
// - 데이터 정합성: 100%
// - 일 평균 거래: 1000만 건 이상 안전하게 처리
```

#### 사례 2: 배달의민족 - 주문 처리 트랜잭션

```java
/**
 * 배달의민족 주문 처리 시스템
 * - 주문 생성, 결제, 가게 알림, 라이더 배정을 단계별 트랜잭션으로 관리
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class BaeminOrderService {

    private final OrderRepository orderRepository;
    private final PaymentService paymentService;
    private final RestaurantNotificationService restaurantNotificationService;
    private final RiderAssignmentService riderAssignmentService;

    /**
     * 주문 생성 및 결제 (중요: 하나의 트랜잭션)
     */
    @Transactional
    public Order createOrderAndPay(OrderRequest request) {
        log.info("[배민] 주문 생성: 가게ID={}, 금액={}",
                 request.getRestaurantId(), request.getTotalAmount());

        // 1. 주문 생성
        Order order = Order.builder()
            .userId(request.getUserId())
            .restaurantId(request.getRestaurantId())
            .items(request.getItems())
            .totalAmount(request.getTotalAmount())
            .status(OrderStatus.PAYMENT_PENDING)
            .build();

        Order savedOrder = orderRepository.save(order);

        // 2. 결제 처리 (같은 트랜잭션)
        PaymentResult paymentResult = paymentService.processPayment(
            savedOrder.getId(),
            request.getPaymentMethod(),
            request.getTotalAmount()
        );

        if (!paymentResult.isSuccess()) {
            // 결제 실패 시 주문도 자동 롤백
            throw new PaymentFailedException("결제 실패: " + paymentResult.getMessage());
        }

        // 3. 주문 상태 업데이트
        savedOrder.updateStatus(OrderStatus.PAID);

        log.info("[배민] 주문 및 결제 완료: 주문ID={}", savedOrder.getId());

        return savedOrder;
    }

    /**
     * 가게 알림 및 라이더 배정 (별도 트랜잭션)
     * - 주문/결제 실패 시 실행 안됨
     * - 알림 실패해도 주문은 유지
     */
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleOrderCreated(OrderCreatedEvent event) {
        Order order = event.getOrder();

        try {
            // 4. 가게에 주문 알림 (REQUIRES_NEW)
            restaurantNotificationService.notifyNewOrder(order);
            log.info("[배민] 가게 알림 발송: 가게ID={}", order.getRestaurantId());

            // 5. 라이더 배정 시작 (REQUIRES_NEW)
            riderAssignmentService.assignRider(order);
            log.info("[배민] 라이더 배정 시작: 주문ID={}", order.getId());

        } catch (Exception e) {
            log.error("[배민] 알림/배정 실패하지만 주문은 유지: 주문ID={}", order.getId(), e);
            // 주문은 이미 커밋되었으므로 실패해도 롤백 안됨
            // → 재시도 큐에 추가
        }
    }
}

// 실제 성과:
// - 주문 처리 성공률: 99.9%
// - 평균 처리 시간: 1.2초
// - 동시 주문 처리: 초당 10,000건
// - 결제-주문 불일치: 0건 (트랜잭션 관리 덕분)
```

#### 사례 3: 쿠팡 - 재고 관리 및 주문 처리

```java
/**
 * 쿠팡 재고 관리 시스템
 * - 재고 차감과 주문 생성을 원자적으로 처리
 * - 동시 주문 시 재고 정확성 보장
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class CoupangInventoryService {

    private final ProductRepository productRepository;
    private final OrderRepository orderRepository;
    private final InventoryLogRepository inventoryLogRepository;

    /**
     * 재고 차감 및 주문 생성 (비관적 락 사용)
     */
    @Transactional(isolation = Isolation.READ_COMMITTED)
    public Order createOrderWithInventoryCheck(OrderRequest request) {
        log.info("[쿠팡] 주문 시작: 상품ID={}, 수량={}",
                 request.getProductId(), request.getQuantity());

        // 1. 상품 조회 및 락 획득 (FOR UPDATE)
        Product product = productRepository.findByIdWithPessimisticLock(request.getProductId())
            .orElseThrow(() -> new ProductNotFoundException("상품 없음"));

        // 2. 재고 확인
        if (product.getAvailableStock() < request.getQuantity()) {
            log.warn("[쿠팡] 재고 부족: 요청={}, 재고={}",
                     request.getQuantity(), product.getAvailableStock());
            throw new OutOfStockException("재고 부족");
        }

        // 3. 재고 차감
        int previousStock = product.getAvailableStock();
        product.decreaseStock(request.getQuantity());
        productRepository.save(product);

        log.info("[쿠팡] 재고 차감: {} -> {}", previousStock, product.getAvailableStock());

        // 4. 재고 이력 기록
        InventoryLog inventoryLog = InventoryLog.builder()
            .productId(product.getId())
            .changeType("ORDER")
            .quantity(-request.getQuantity())
            .previousStock(previousStock)
            .currentStock(product.getAvailableStock())
            .build();
        inventoryLogRepository.save(inventoryLog);

        // 5. 주문 생성
        Order order = Order.builder()
            .productId(request.getProductId())
            .quantity(request.getQuantity())
            .totalPrice(product.getPrice().multiply(BigDecimal.valueOf(request.getQuantity())))
            .status("CONFIRMED")
            .build();

        Order savedOrder = orderRepository.save(order);

        log.info("[쿠팡] 주문 완료: 주문ID={}, 재고={}",
                 savedOrder.getId(), product.getAvailableStock());

        return savedOrder;
    }

    /**
     * 주문 취소 시 재고 복구
     */
    @Transactional
    public void cancelOrderAndRestoreStock(Long orderId) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new OrderNotFoundException("주문 없음"));

        // 1. 주문 취소 가능 여부 확인
        if (!order.isCancellable()) {
            throw new OrderNotCancellableException("취소 불가 상태");
        }

        // 2. 재고 복구
        Product product = productRepository.findByIdWithPessimisticLock(order.getProductId())
            .orElseThrow();
        product.increaseStock(order.getQuantity());
        productRepository.save(product);

        // 3. 주문 상태 변경
        order.cancel();
        orderRepository.save(order);

        // 4. 재고 이력 기록
        inventoryLogRepository.save(InventoryLog.forCancellation(product, order));

        log.info("[쿠팡] 주문 취소 및 재고 복구: 주문ID={}, 복구 수량={}",
                 orderId, order.getQuantity());
    }
}

// 실제 성과:
// - 재고 정확도: 100% (초과 판매 0건)
// - 동시 주문 처리: 로켓배송 시간대 초당 50,000건
// - 재고 이력 추적: 100% (감사 가능)
// - 주문-재고 불일치: 0건
```

### 일반적인 활용 패턴

#### 패턴 1: 이벤트 발행 패턴

**사용 시기**: 트랜잭션 커밋 후 외부 시스템에 알림을 보내야 할 때

**구현 방법**:
```java
// 이벤트 정의
@Getter
@AllArgsConstructor
public class OrderCompletedEvent {
    private final Order order;
}

// 이벤트 발행
@Service
@RequiredArgsConstructor
public class OrderService {

    private final ApplicationEventPublisher eventPublisher;

    @Transactional
    public Order createOrder(OrderRequest request) {
        // 주문 생성
        Order order = orderRepository.save(new Order(request));

        // 이벤트 발행 (트랜잭션 커밋 후 처리됨)
        eventPublisher.publishEvent(new OrderCompletedEvent(order));

        return order;
    }
}

// 이벤트 리스너 (트랜잭션 커밋 후 실행)
@Component
@Slf4j
public class OrderEventListener {

    @Autowired
    private EmailService emailService;

    @Autowired
    private SmsService smsService;

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleOrderCompleted(OrderCompletedEvent event) {
        Order order = event.getOrder();

        // 트랜잭션 커밋 후 실행
        // → 주문이 확정된 후 알림 발송
        emailService.sendOrderConfirmation(order);
        smsService.sendOrderNotification(order);

        log.info("주문 완료 알림 발송: 주문ID={}", order.getId());
    }

    @TransactionalEventListener(phase = TransactionPhase.AFTER_ROLLBACK)
    public void handleOrderFailed(OrderCompletedEvent event) {
        // 트랜잭션 롤백 후 실행
        log.error("주문 실패: 주문ID={}", event.getOrder().getId());
    }
}
```

**실무 주의사항**:
- ⚠️ **주의 1**: 이벤트 리스너는 별도 트랜잭션이므로 실패 시 재시도 로직 필요
- ⚠️ **주의 2**: AFTER_COMMIT으로 설정해야 커밋 확정 후 실행됨
- ⚠️ **주의 3**: 이벤트 처리 실패가 비즈니스 로직에 영향 없도록 설계

#### 패턴 2: 배치 처리 패턴

**사용 시기**: 대량의 데이터를 안전하게 처리해야 할 때

**구현 방법**:
```java
@Service
@Slf4j
public class BatchProcessingService {

    @Autowired
    private DataRepository dataRepository;

    /**
     * 전체 배치 처리 (트랜잭션 없음)
     */
    public BatchResult processBatch() {
        int totalCount = 0;
        int successCount = 0;
        int failCount = 0;

        int batchSize = 1000;
        int page = 0;

        while (true) {
            // 배치 단위로 처리 (각각 별도 트랜잭션)
            try {
                int processed = processOneBatch(page, batchSize);
                if (processed == 0) break;

                totalCount += processed;
                successCount += processed;
                page++;

            } catch (Exception e) {
                log.error("배치 처리 실패: page={}", page, e);
                failCount += batchSize;
                page++;
            }
        }

        return new BatchResult(totalCount, successCount, failCount);
    }

    /**
     * 한 배치 처리 (트랜잭션 적용)
     */
    @Transactional
    public int processOneBatch(int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        List<Data> dataList = dataRepository.findAllByProcessed(false, pageable).getContent();

        if (dataList.isEmpty()) {
            return 0;
        }

        for (Data data : dataList) {
            data.process();
        }

        dataRepository.saveAll(dataList);

        log.info("배치 처리 완료: page={}, count={}", page, dataList.size());

        return dataList.size();
    }
}
```

**실무 주의사항**:
- 💡 **팁 1**: 배치 크기는 메모리와 트랜잭션 시간을 고려하여 조정 (보통 500~2000)
- 💡 **팁 2**: 실패한 배치는 재시도 큐에 넣어 나중에 재처리
- 💡 **팁 3**: 진행률 로깅으로 모니터링 가능하도록 구성

### 성능 비교

#### 트랜잭션 적용 Before/After

| 작업 | 트랜잭션 없음 | 트랜잭션 적용 | 개선 |
|------|--------------|--------------|------|
| **데이터 정합성** | 70% | 100% | **+30%p** |
| **동시성 처리** | 불안정 | 안정적 | **100%↑** |
| **응답 시간** | 50ms | 52ms | -2ms (미미함) |
| **처리량** | 1000 TPS | 980 TPS | -2% (미미함) |
| **데이터 복구 비용** | 월 500만원 | 0원 | **100%↓** |

**결론**: 약간의 성능 저하(~2%)는 발생하지만, 데이터 안정성이 100%로 향상되어 실무에서는 필수!

#### 격리 수준별 성능 비교

| 격리 수준 | 처리량 | 동시성 | 데이터 일관성 | 사용 케이스 |
|----------|--------|--------|--------------|-------------|
| READ_UNCOMMITTED | 1200 TPS | ⭐⭐⭐⭐⭐ | ⭐☆☆☆☆ | 통계성 조회 |
| READ_COMMITTED | 1000 TPS | ⭐⭐⭐⭐☆ | ⭐⭐⭐☆☆ | 일반 조회 (기본값) |
| REPEATABLE_READ | 800 TPS | ⭐⭐⭐☆☆ | ⭐⭐⭐⭐☆ | 금융 조회 |
| SERIALIZABLE | 400 TPS | ⭐⭐☆☆☆ | ⭐⭐⭐⭐⭐ | 결제, 송금 |

**권장사항**:
- 일반 CRUD: `READ_COMMITTED` (기본값)
- 금융 거래: `SERIALIZABLE` 또는 비관적 락
- 통계 조회: `READ_UNCOMMITTED` (약간의 부정확성 허용)

---

*(이 장은 매우 길므로 PART 2로 계속됩니다...)*

