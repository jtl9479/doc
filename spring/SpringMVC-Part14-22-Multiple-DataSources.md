# 22장: 다중 데이터소스와 Master-Slave 구성

> **학습 목표**: Spring에서 여러 데이터베이스를 동시에 사용하고, Read/Write 분리로 대용량 트래픽을 효율적으로 처리하는 방법을 완벽히 습득합니다.

**⏱️ 예상 학습 시간**: 4-5시간
**난이도**: ⭐⭐⭐⭐⭐ (5개/5개)

---

## 📚 목차
- [왜 다중 데이터소스가 필요한가](#왜-다중-데이터소스가-필요한가)
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

## 🤔 왜 다중 데이터소스가 필요한가?

### 실무 배경
**대규모 서비스에서는 하나의 데이터베이스로 모든 요청을 처리할 수 없습니다:**

```
일일 사용자: 1000만 명
동시 접속자: 10만 명
초당 쿼리: 50,000 QPS

하나의 MySQL 서버 한계:
- Read 쿼리: 최대 5,000 QPS
- Write 쿼리: 최대 1,000 QPS
→ 병목 현상 발생!
```

**실제 시나리오**:
- 네이버: 뉴스(읽기 95%) + 댓글(쓰기 5%)
- 배달의민족: 메뉴 조회(읽기 90%) + 주문(쓰기 10%)
- 쿠팡: 상품 검색(읽기 95%) + 구매(쓰기 5%)

#### ❌ 단일 데이터소스로 발생하는 문제

**문제 1: 읽기/쓰기 경합 (Read/Write Contention)**
```java
// 하나의 DB 서버에서 모든 요청 처리
@Service
public class ProductService {

    // 상품 조회 (초당 45,000건)
    public List<Product> searchProducts(String keyword) {
        return productRepository.findByNameContaining(keyword);
        // DB 부하 90%
    }

    // 주문 생성 (초당 5,000건)
    @Transactional
    public Order createOrder(OrderRequest request) {
        return orderRepository.save(new Order(request));
        // 조회 쿼리 때문에 대기 발생!
    }
}
```
- **증상**: 읽기 쿼리가 많아 쓰기 쿼리가 지연됨
- **영향**: 주문 생성 시간 100ms → 5초로 증가
- **비용**: 매출 감소 (고객 이탈율 30% 증가)

**문제 2: 단일 장애점 (Single Point of Failure)**
```
[단일 DB 서버]
     ↓
   장애 발생
     ↓
전체 서비스 중단!

다운타임: 평균 30분
매출 손실: 시간당 1억 원
고객 신뢰도 하락: 회복 불가
```
- **증상**: DB 서버 하나 다운 시 전체 서비스 중단
- **영향**: 복구 시간 동안 매출 손실
- **비용**: 시간당 1억 원 + 브랜드 이미지 타격

**문제 3: 확장성 한계 (Scalability Limit)**
```java
// 트래픽 증가에 대응
// ❌ 방법 1: 서버 스케일 업 (한계 있음)
DB 서버 사양:
- CPU 16코어 → 64코어 (4배)
- RAM 64GB → 256GB (4배)
- 성능 향상: 1.5배 (비효율적!)
- 비용: 월 300만 원 → 1200만 원

// ❌ 방법 2: 애플리케이션 서버만 늘림 (DB 병목)
App 서버: 10대 → 100대
DB 서버: 1대 (그대로)
→ DB가 병목, 성능 개선 없음!
```
- **증상**: 서버 스펙을 올려도 성능 향상 미미
- **영향**: 비용 대비 효과 낮음
- **비용**: ROI 50% 이하

#### ✅ 다중 데이터소스를 사용하면

**해결책 1: Read/Write 분리 (Master-Slave Replication)**
```java
// ✅ Master (쓰기 전용): 1대
// ✅ Slave (읽기 전용): 5대

@Service
public class ProductService {

    // Slave에서 조회 (부하 분산)
    @Transactional(readOnly = true)
    public List<Product> searchProducts(String keyword) {
        // 5대의 Slave 서버에 분산
        return productRepository.findByNameContaining(keyword);
    }

    // Master에서 쓰기
    @Transactional
    public Order createOrder(OrderRequest request) {
        // Master 서버에서만 처리
        return orderRepository.save(new Order(request));
    }
}
```
- **방법**: 읽기는 Slave, 쓰기는 Master로 분리
- **효과**: 읽기 처리량 5배 증가 (Slave 5대)
- **절감**: 응답 시간 80% 감소 (5초 → 1초)

**해결책 2: 데이터베이스 분리 (Database Sharding)**
```java
// ✅ 사용자 DB: MySQL
// ✅ 주문 DB: PostgreSQL
// ✅ 로그 DB: MongoDB

@Configuration
public class DataSourceConfig {

    @Bean
    @Primary
    public DataSource userDataSource() {
        // 사용자 정보: MySQL
        return DataSourceBuilder.create()
            .url("jdbc:mysql://user-db:3306/users")
            .build();
    }

    @Bean
    public DataSource orderDataSource() {
        // 주문 정보: PostgreSQL
        return DataSourceBuilder.create()
            .url("jdbc:postgresql://order-db:5432/orders")
            .build();
    }

    @Bean
    public DataSource logDataSource() {
        // 로그: MongoDB
        return new MongoDataSource("mongodb://log-db:27017/logs");
    }
}
```
- **방법**: 도메인별로 DB 분리
- **효과**: 도메인 간 영향도 제로, 독립적 확장
- **절감**: 장애 격리로 가용성 99.9% → 99.99%

**해결책 3: 동적 라우팅 (Dynamic Routing)**
```java
// ✅ 읽기/쓰기를 런타임에 자동 분기

public class RoutingDataSource extends AbstractRoutingDataSource {

    @Override
    protected Object determineCurrentLookupKey() {
        // 현재 트랜잭션이 읽기 전용인지 확인
        boolean isReadOnly = TransactionSynchronizationManager
            .isCurrentTransactionReadOnly();

        if (isReadOnly) {
            // Slave 서버 중 하나 선택 (라운드 로빈)
            return "slave" + (counter++ % 5);
        } else {
            // Master 서버 선택
            return "master";
        }
    }
}
```
- **방법**: @Transactional(readOnly=true)에 따라 자동 라우팅
- **효과**: 코드 변경 없이 DB 분산
- **절감**: 개발 비용 90% 절감

### 📊 수치로 보는 효과

| 지표 | Before (단일 DB) | After (다중 DB) | 개선율 |
|------|-----------------|----------------|--------|
| 처리량 (QPS) | 5,000 | 30,000 | **500%↑** |
| 평균 응답 시간 | 500ms | 50ms | **90%↓** |
| 최대 동시 접속 | 10,000명 | 100,000명 | **900%↑** |
| 장애 복구 시간 | 30분 | 0분 (자동) | **100%↓** |
| 가용성 | 99% | 99.99% | **0.99%p↑** |
| 인프라 비용 | 월 500만 원 | 월 400만 원 | **20%↓** |

**실제 사례 - 배달의민족**:
```
Master-Slave 도입 전:
- 점심 시간대 응답 시간: 3~5초
- 장애 발생 시 전체 서비스 중단

Master-Slave 도입 후:
- 점심 시간대 응답 시간: 0.5초 (83% 개선)
- Slave 1대 장애 시에도 서비스 정상 운영
- 트래픽 3배 증가해도 안정적 처리
```

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 대형 서점의 직원 배치

```
단일 데이터소스 = 직원 1명이 모든 업무 처리

┌─────────────────────────────────────┐
│         작은 서점 (직원 1명)         │
├─────────────────────────────────────┤
│                                     │
│  [직원 1명]                         │
│    ↓                                │
│  ① 책 찾아주기 (고객 10명 대기)     │
│  ② 계산하기 (고객 5명 대기)         │
│  ③ 재고 정리 (미뤄짐)               │
│  ④ 책 주문 (미뤄짐)                 │
│                                     │
│  문제: 계산하려는 고객이            │
│        책 찾는 고객 때문에 대기!    │
└─────────────────────────────────────┘

다중 데이터소스 = 역할별 직원 배치

┌─────────────────────────────────────┐
│      대형 서점 (직원 7명, 역할 분담)  │
├─────────────────────────────────────┤
│                                     │
│ [안내 직원 5명] ← 책 찾기 전담       │
│   → 고객 10명을 5명이 나눠서 처리   │
│   → 대기 시간 1/5로 감소!           │
│                                     │
│ [계산 직원 1명] ← 계산 전담          │
│   → 빠르게 계산만 처리              │
│                                     │
│ [관리 직원 1명] ← 재고/주문 전담     │
│   → 백엔드 업무 처리                │
│                                     │
│  효과: 역할 분담으로 효율 5배 증가!  │
└─────────────────────────────────────┘
```

**비유 설명**:
- **직원 1명 (단일 DB)** = 모든 업무 처리, 병목 발생
- **안내 직원 5명 (Slave 5대)** = 읽기 쿼리 분산 처리
- **계산 직원 1명 (Master 1대)** = 쓰기 쿼리 전담 처리
- **역할 분담** = Read/Write 분리로 효율 극대화

**핵심**: "찾기(읽기)"는 여러 명이, "계산(쓰기)"는 한 명이!

### 비유 2: 배달 앱의 음식점 배치

```
단일 데이터소스 = 한 음식점에서 모든 주문 처리

┌─────────────────────────────────────┐
│      단일 음식점 (주방 1개)          │
├─────────────────────────────────────┤
│                                     │
│  주문 접수:                         │
│  - 한식 100건                       │
│  - 중식 80건                        │
│  - 일식 70건                        │
│  - 양식 50건                        │
│    ↓                                │
│  [주방 1개]가 모든 요리!            │
│    ↓                                │
│  대기 시간: 평균 2시간              │
│  음식 식어서 배달 ❌                │
└─────────────────────────────────────┘

다중 데이터소스 = 음식 종류별 전문 음식점

┌─────────────────────────────────────┐
│    음식점 4개 (종류별 분산)          │
├─────────────────────────────────────┤
│                                     │
│ [한식집] → 한식 100건 처리           │
│   (전문화로 빠른 조리)              │
│                                     │
│ [중식집] → 중식 80건 처리            │
│                                     │
│ [일식집] → 일식 70건 처리            │
│                                     │
│ [양식집] → 양식 50건 처리            │
│                                     │
│  대기 시간: 평균 30분               │
│  따뜻한 음식 배달 ✅                │
└─────────────────────────────────────┘
```

**비유 설명**:
- **단일 음식점** = 하나의 DB가 모든 도메인 처리
- **음식 종류별 분리** = 도메인별 DB 분리 (User DB, Order DB 등)
- **전문화** = 각 DB가 특정 도메인에 최적화
- **병렬 처리** = 각 DB가 독립적으로 동시 처리

### 비유 3: 고속도로 톨게이트

```
단일 데이터소스 = 톨게이트 1개

┌─────────────────────────────────────┐
│       톨게이트 1개 (정체)            │
├─────────────────────────────────────┤
│                                     │
│  [차량 1000대]                      │
│        ↓                            │
│    [톨게이트 1개]                   │
│        ↓                            │
│  대기 시간: 30분                    │
│  통과 속도: 초당 10대               │
│                                     │
│  ❌ 병목 현상                       │
│  ❌ 하나 고장 시 전체 마비          │
└─────────────────────────────────────┘

다중 데이터소스 = 톨게이트 10개 + 하이패스

┌─────────────────────────────────────┐
│   톨게이트 10개 + 역할 분리          │
├─────────────────────────────────────┤
│                                     │
│ [하이패스 5개] ← 빠른 통과 (읽기)    │
│   → 정기권 차량 (읽기 전용 쿼리)    │
│   → 대기 없이 통과                  │
│   → 초당 50대 처리                  │
│                                     │
│ [일반 톨게이트 5개] ← 정확한 처리    │
│   → 일반 차량 (쓰기 쿼리)           │
│   → 정확한 요금 징수                │
│   → 초당 50대 처리                  │
│                                     │
│  대기 시간: 3분 (10배 감소)         │
│  통과 속도: 초당 100대 (10배 증가)  │
│                                     │
│  ✅ 병목 해소                       │
│  ✅ 하나 고장 시에도 9개 운영       │
└─────────────────────────────────────┘
```

**비유 설명**:
- **하이패스 (Slave)** = 읽기 전용 DB, 빠른 처리
- **일반 톨게이트 (Master)** = 쓰기 DB, 정확한 처리
- **다중 톨게이트** = 여러 Slave로 부하 분산
- **장애 대응** = 하나 고장 나도 나머지로 처리 가능

### 비유 4: 도서관의 자료 관리

```
단일 데이터소스 = 중앙 집중식 도서관

┌─────────────────────────────────────┐
│      중앙 도서관 1곳                 │
├─────────────────────────────────────┤
│                                     │
│  [서울]의 모든 시민 → [중앙 도서관]  │
│                                     │
│  문제점:                            │
│  1. 강남 주민이 책 빌리러 왕복 2시간│
│  2. 동시 접속자 많아 대출 지연      │
│  3. 도서관 휴관 시 전체 이용 불가   │
└─────────────────────────────────────┘

다중 데이터소스 = 지역별 도서관 + 중앙 관리

┌─────────────────────────────────────┐
│    지역 도서관 10곳 + 중앙 도서관     │
├─────────────────────────────────────┤
│                                     │
│ [읽기 = 지역 도서관 10곳]            │
│  → 강남 주민 → 강남 도서관 (5분)    │
│  → 강북 주민 → 강북 도서관 (5분)    │
│  → 부하 분산으로 대기 시간 감소     │
│                                     │
│ [쓰기 = 중앙 도서관 1곳]             │
│  → 신규 도서 구매 (중앙에서 관리)   │
│  → 도서 폐기 (중앙에서 관리)        │
│  → 일관성 보장                      │
│                                     │
│ [복제본 동기화]                     │
│  → 중앙 도서관의 신규 도서를        │
│     각 지역 도서관에 복사           │
│  → Master → Slave 복제              │
└─────────────────────────────────────┘
```

**비유 설명**:
- **지역 도서관 (Slave)** = 읽기 전용 복제본
- **중앙 도서관 (Master)** = 원본 데이터 관리
- **복제본 동기화** = Replication (마스터 → 슬레이브)
- **지역별 분산** = 사용자와 가까운 DB에서 조회

### 비유 5: 물류 창고 시스템

```
단일 데이터소스 = 메인 창고 1개

┌─────────────────────────────────────┐
│         메인 창고 1개                │
├─────────────────────────────────────┤
│                                     │
│  전국 배송 → [경기도 메인 창고]      │
│                                     │
│  문제:                              │
│  - 부산 고객 주문 → 경기도까지 왕복 │
│  - 배송 시간 3일                    │
│  - 창고 하나 화재 → 전국 배송 중단  │
└─────────────────────────────────────┘

다중 데이터소스 = 지역별 창고 + 메인 창고

┌─────────────────────────────────────┐
│  메인 창고 1개 + 지역 창고 5개       │
├─────────────────────────────────────┤
│                                     │
│ [읽기/배송 = 지역 창고 5개]          │
│  → 부산 주문 → 부산 창고 (1일)      │
│  → 서울 주문 → 서울 창고 (당일)     │
│  → 가까운 창고에서 빠른 배송        │
│                                     │
│ [쓰기/입고 = 메인 창고 1개]          │
│  → 신규 상품 입고 (메인 창고)       │
│  → 재고 관리 (중앙 집중)            │
│                                     │
│ [재고 동기화]                       │
│  → 메인 창고 입고 → 지역 창고 분배  │
│  → 야간 자동 동기화                 │
│  → Master-Slave Replication         │
│                                     │
│  효과:                              │
│  - 배송 시간 3일 → 1일              │
│  - 지역 창고 장애 시 다른 창고 활용 │
└─────────────────────────────────────┘
```

**비유 설명**:
- **메인 창고 (Master)** = 쓰기 DB, 원본 데이터
- **지역 창고 (Slave)** = 읽기 DB, 복제 데이터
- **재고 동기화** = 비동기 복제 (약간의 지연)
- **지역별 배송** = 가까운 Slave에서 빠른 응답

### 🎯 종합 비교표

| 비유 | 단일 데이터소스 | 다중 데이터소스 | 핵심 효과 |
|------|---------------|---------------|----------|
| **서점** | 직원 1명이 전부 처리 | 역할별 직원 배치 | 효율 5배↑ |
| **음식점** | 한 주방이 전부 요리 | 음식별 전문 음식점 | 대기 시간 75%↓ |
| **톨게이트** | 톨게이트 1개 | 톨게이트 10개 + 하이패스 | 처리량 10배↑ |
| **도서관** | 중앙 도서관 1곳 | 지역 도서관 10곳 | 접근 시간 90%↓ |
| **물류** | 메인 창고 1개 | 지역 창고 5개 | 배송 시간 67%↓ |

---

## 📖 핵심 개념

### 개념 설명 (3단계 깊이)

#### 1️⃣ 초보자 수준 설명

**다중 데이터소스란?**
> "하나의 Spring 애플리케이션에서 여러 개의 데이터베이스를 동시에 사용하는 것"

**쉬운 설명**:
```
데이터소스 = 데이터베이스 연결 정보

단일 데이터소스:
  Spring App → MySQL 1대

다중 데이터소스:
  Spring App → MySQL (사용자 정보)
            → PostgreSQL (주문 정보)
            → MongoDB (로그)
```

**Spring에서 사용법**:
```java
// 데이터소스 2개 설정
@Configuration
public class DataSourceConfig {

    // 첫 번째 DB (MySQL)
    @Bean
    @Primary  // 기본 데이터소스
    public DataSource userDataSource() {
        return DataSourceBuilder.create()
            .url("jdbc:mysql://localhost:3306/users")
            .username("root")
            .password("password")
            .build();
    }

    // 두 번째 DB (PostgreSQL)
    @Bean
    public DataSource orderDataSource() {
        return DataSourceBuilder.create()
            .url("jdbc:postgresql://localhost:5432/orders")
            .username("postgres")
            .password("password")
            .build();
    }
}
```

#### 2️⃣ 중급자 수준 설명

**Master-Slave Replication**

**개념**:
```
Master DB (쓰기 전용):
  - INSERT, UPDATE, DELETE 처리
  - 원본 데이터 보관
  - 1대만 운영

Slave DB (읽기 전용):
  - SELECT 처리
  - Master의 복제본
  - 여러 대 운영 가능 (부하 분산)

복제 (Replication):
  Master의 변경사항 → Slave로 자동 복사
  (비동기 복제, 약간의 지연 발생)
```

**동작 흐름**:
```
1. 쓰기 요청 (주문 생성)
   → Master DB에 INSERT
   → Binary Log 기록

2. 복제 프로세스
   → Slave가 Master의 Binary Log 읽기
   → Slave에 동일한 INSERT 실행
   → 약간의 지연 (보통 1초 이내)

3. 읽기 요청 (주문 조회)
   → Slave DB에서 SELECT
   → Master는 쓰기만 처리하므로 여유 있음
```

**AbstractRoutingDataSource로 구현**:
```java
public class ReplicationRoutingDataSource extends AbstractRoutingDataSource {

    private static final String MASTER = "master";
    private static final String SLAVE = "slave";

    @Override
    protected Object determineCurrentLookupKey() {
        // 현재 트랜잭션이 읽기 전용인지 확인
        boolean isReadOnly = TransactionSynchronizationManager
            .isCurrentTransactionReadOnly();

        return isReadOnly ? SLAVE : MASTER;
    }
}

// 사용
@Service
public class OrderService {

    @Transactional(readOnly = true)
    public Order getOrder(Long id) {
        // Slave DB에서 조회
        return orderRepository.findById(id).orElseThrow();
    }

    @Transactional
    public Order createOrder(OrderRequest request) {
        // Master DB에 저장
        return orderRepository.save(new Order(request));
    }
}
```

**복제 지연 (Replication Lag) 이해**:
```java
// 시나리오: 주문 생성 직후 조회
@Transactional
public Order createAndGetOrder(OrderRequest request) {
    // 1. Master에 저장
    Order order = orderRepository.save(new Order(request));
    // commit → Master의 데이터 확정

    return order;  // 이 시점에 Order 반환
}

// 즉시 조회 (다른 요청)
@Transactional(readOnly = true)
public Order getOrder(Long id) {
    // 2. Slave에서 조회
    // 문제: 아직 복제가 안 끝났을 수 있음!
    // Slave에 데이터 없음 → null 반환
    return orderRepository.findById(id).orElseThrow();
}

// ✅ 해결 방법 1: 생성 직후는 Master에서 조회
@Transactional  // readOnly=false (기본값)
public Order getOrderAfterCreate(Long id) {
    // Master에서 조회 (최신 데이터 보장)
    return orderRepository.findById(id).orElseThrow();
}

// ✅ 해결 방법 2: 강제로 Master 사용
@Transactional(readOnly = false)
public Order getOrderFromMaster(Long id) {
    return orderRepository.findById(id).orElseThrow();
}
```

#### 3️⃣ 고급자 수준 설명

**다중 DataSource의 트랜잭션 관리**

**JPA EntityManager 분리**:
```java
@Configuration
@EnableJpaRepositories(
    basePackages = "com.example.user.repository",
    entityManagerFactoryRef = "userEntityManagerFactory",
    transactionManagerRef = "userTransactionManager"
)
public class UserDataSourceConfig {

    @Bean
    @Primary
    public DataSource userDataSource() {
        return DataSourceBuilder.create()
            .url("jdbc:mysql://localhost:3306/users")
            .build();
    }

    @Bean
    @Primary
    public LocalContainerEntityManagerFactoryBean userEntityManagerFactory(
        EntityManagerFactoryBuilder builder) {
        return builder
            .dataSource(userDataSource())
            .packages("com.example.user.entity")
            .persistenceUnit("user")
            .build();
    }

    @Bean
    @Primary
    public PlatformTransactionManager userTransactionManager(
        @Qualifier("userEntityManagerFactory") EntityManagerFactory entityManagerFactory) {
        return new JpaTransactionManager(entityManagerFactory);
    }
}

@Configuration
@EnableJpaRepositories(
    basePackages = "com.example.order.repository",
    entityManagerFactoryRef = "orderEntityManagerFactory",
    transactionManagerRef = "orderTransactionManager"
)
public class OrderDataSourceConfig {

    @Bean
    public DataSource orderDataSource() {
        return DataSourceBuilder.create()
            .url("jdbc:postgresql://localhost:5432/orders")
            .build();
    }

    @Bean
    public LocalContainerEntityManagerFactoryBean orderEntityManagerFactory(
        EntityManagerFactoryBuilder builder) {
        return builder
            .dataSource(orderDataSource())
            .packages("com.example.order.entity")
            .persistenceUnit("order")
            .build();
    }

    @Bean
    public PlatformTransactionManager orderTransactionManager(
        @Qualifier("orderEntityManagerFactory") EntityManagerFactory entityManagerFactory) {
        return new JpaTransactionManager(entityManagerFactory);
    }
}
```

**분산 트랜잭션 (JTA)**:
```java
// JTA로 여러 DB에 걸친 트랜잭션 관리
@Configuration
public class JtaConfig {

    @Bean
    public JtaTransactionManager transactionManager() {
        UserTransaction userTransaction = new UserTransactionImp();
        TransactionManager transactionManager = new TransactionManagerImp();

        return new JtaTransactionManager(userTransaction, transactionManager);
    }
}

@Service
public class DistributedService {

    @Autowired
    private UserRepository userRepository;  // MySQL

    @Autowired
    private OrderRepository orderRepository;  // PostgreSQL

    @Transactional
    public void createUserAndOrder(User user, Order order) {
        // 두 개의 다른 DB에 대한 작업을 하나의 트랜잭션으로
        userRepository.save(user);      // MySQL
        orderRepository.save(order);     // PostgreSQL

        // 2-Phase Commit으로 원자성 보장
        // 하나라도 실패하면 둘 다 롤백
    }
}
```

**커넥션 풀 최적화**:
```java
@Bean
public DataSource masterDataSource() {
    HikariConfig config = new HikariConfig();
    config.setJdbcUrl("jdbc:mysql://master:3306/db");
    config.setUsername("root");
    config.setPassword("password");

    // 쓰기 전용이므로 작은 풀
    config.setMaximumPoolSize(10);
    config.setMinimumIdle(5);
    config.setConnectionTimeout(30000);

    return new HikariDataSource(config);
}

@Bean
public DataSource slaveDataSource() {
    HikariConfig config = new HikariConfig();
    config.setJdbcUrl("jdbc:mysql://slave:3306/db");
    config.setUsername("readonly");
    config.setPassword("password");

    // 읽기 전용이므로 큰 풀
    config.setMaximumPoolSize(50);
    config.setMinimumIdle(20);
    config.setReadOnly(true);  // 읽기 전용 힌트

    return new HikariDataSource(config);
}
```

**로드 밸런싱 (Multiple Slaves)**:
```java
public class LoadBalancedRoutingDataSource extends AbstractRoutingDataSource {

    private static final String MASTER = "master";
    private static final List<String> SLAVES = List.of("slave1", "slave2", "slave3");
    private final AtomicInteger counter = new AtomicInteger(0);

    @Override
    protected Object determineCurrentLookupKey() {
        boolean isReadOnly = TransactionSynchronizationManager
            .isCurrentTransactionReadOnly();

        if (isReadOnly) {
            // 라운드 로빈으로 Slave 선택
            int index = counter.getAndIncrement() % SLAVES.size();
            return SLAVES.get(index);
        } else {
            return MASTER;
        }
    }
}

// 설정
@Bean
public DataSource routingDataSource() {
    LoadBalancedRoutingDataSource routingDataSource =
        new LoadBalancedRoutingDataSource();

    Map<Object, Object> dataSourceMap = new HashMap<>();
    dataSourceMap.put("master", masterDataSource());
    dataSourceMap.put("slave1", slave1DataSource());
    dataSourceMap.put("slave2", slave2DataSource());
    dataSourceMap.put("slave3", slave3DataSource());

    routingDataSource.setTargetDataSources(dataSourceMap);
    routingDataSource.setDefaultTargetDataSource(masterDataSource());

    return routingDataSource;
}
```

### 주요 용어 정리

| 용어 | 영문 | 설명 | 예시 |
|------|------|------|------|
| 데이터소스 | DataSource | DB 연결 정보 및 커넥션 풀 | HikariDataSource |
| 마스터 | Master | 쓰기 전용 DB (원본) | INSERT, UPDATE, DELETE |
| 슬레이브 | Slave | 읽기 전용 DB (복제본) | SELECT |
| 복제 | Replication | Master → Slave 데이터 복사 | Binary Log 기반 |
| 복제 지연 | Replication Lag | Master와 Slave 간 시간차 | 보통 1초 이내 |
| 라우팅 | Routing | 요청에 따라 DB 선택 | 읽기 → Slave, 쓰기 → Master |
| 샤딩 | Sharding | 데이터를 여러 DB에 분산 | User 1~1000 → DB1, 1001~2000 → DB2 |
| 로드 밸런싱 | Load Balancing | 여러 Slave에 부하 분산 | 라운드 로빈, 랜덤 |
| 페일오버 | Failover | Master 장애 시 Slave 승격 | 자동 전환 |
| 커넥션 풀 | Connection Pool | DB 커넥션 재사용 | HikariCP |

### 기술 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│              Master-Slave Replication Architecture              │
└─────────────────────────────────────────────────────────────────┘

              [Spring Application]
                      │
                      │ @Transactional
                      ↓
         ┌────────────────────────┐
         │  RoutingDataSource     │
         │  (AbstractRouting...)  │
         └────────────────────────┘
                      │
       ┌──────────────┴──────────────┐
       │                             │
   readOnly=true              readOnly=false
       │                             │
       ↓                             ↓
┌─────────────┐              ┌─────────────┐
│ Slave Pool  │              │ Master Pool │
│ (Read Only) │              │ (Read/Write)│
└─────────────┘              └─────────────┘
       │                             │
   ┌───┴────┬────┬────┐             │
   ↓        ↓    ↓    ↓             ↓
┌──────┐ ┌──────┐  ...        ┌──────────┐
│Slave1│ │Slave2│             │  Master  │
│(읽기)│ │(읽기)│             │(쓰기/읽기)│
└──────┘ └──────┘             └──────────┘
   ↑        ↑    ↑                   │
   │        │    │                   │
   └────────┴────┴───────────────────┘
              Replication
         (Binary Log 기반 복제)

설명:
1. @Transactional(readOnly=true) → Slave Pool 선택
2. @Transactional (readOnly=false) → Master Pool 선택
3. Slave Pool은 라운드 로빈으로 부하 분산
4. Master의 변경사항은 자동으로 Slave로 복제
5. 복제 지연: 일반적으로 1초 이내
```

**다중 데이터베이스 아키텍처**:

```
┌─────────────────────────────────────────────────────────────────┐
│            Multiple Database Architecture                        │
└─────────────────────────────────────────────────────────────────┘

         [Spring Application]
                 │
    ┌────────────┼────────────┐
    │            │            │
    ↓            ↓            ↓
┌─────────┐ ┌─────────┐ ┌─────────┐
│  User   │ │  Order  │ │   Log   │
│Repository│ │Repository│ │Repository│
└─────────┘ └─────────┘ └─────────┘
    │            │            │
    ↓            ↓            ↓
┌─────────┐ ┌─────────┐ ┌─────────┐
│  User   │ │  Order  │ │   Log   │
│   EM    │ │   EM    │ │   EM    │
│ Factory │ │ Factory │ │ Factory │
└─────────┘ └─────────┘ └─────────┘
    │            │            │
    ↓            ↓            ↓
┌─────────┐ ┌─────────┐ ┌─────────┐
│  User   │ │  Order  │ │   Log   │
│   TX    │ │   TX    │ │   TX    │
│ Manager │ │ Manager │ │ Manager │
└─────────┘ └─────────┘ └─────────┘
    │            │            │
    ↓            ↓            ↓
┌─────────┐ ┌─────────┐ ┌─────────┐
│ MySQL   │ │Postgres │ │ MongoDB │
│ :3306   │ │ :5432   │ │ :27017  │
└─────────┘ └─────────┘ └─────────┘

특징:
- 각 도메인별로 독립적인 DB 사용
- EntityManagerFactory 분리
- TransactionManager 분리
- 독립적인 스케일링 가능
```

---

## 💻 기본 실습

### 📋 사전 체크리스트

```bash
# 1. Docker로 MySQL Master-Slave 환경 구성
# docker-compose.yml 생성
version: '3.8'
services:
  mysql-master:
    image: mysql:8.0
    container_name: mysql-master
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: testdb
    ports:
      - "3306:3306"
    command:
      - --server-id=1
      - --log-bin=mysql-bin
      - --binlog-format=ROW
    volumes:
      - master-data:/var/lib/mysql

  mysql-slave:
    image: mysql:8.0
    container_name: mysql-slave
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: testdb
    ports:
      - "3307:3306"
    command:
      - --server-id=2
    volumes:
      - slave-data:/var/lib/mysql
    depends_on:
      - mysql-master

volumes:
  master-data:
  slave-data:

# 실행
docker-compose up -d

# 2. 의존성 확인 (build.gradle)
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'com.zaxxer:HikariCP'
    runtimeOnly 'com.mysql:mysql-connector-j'
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}
```

### 실습 1: 기본 Master-Slave 구성

**난이도**: ⭐⭐⭐⭐☆

#### 시나리오
단순한 사용자 관리 시스템에서 읽기는 Slave, 쓰기는 Master로 분리합니다.

#### 1단계: DataSource 설정

```java
// DataSourceConfig.java
package com.example.demo.config;

import com.zaxxer.hikari.HikariDataSource;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.jdbc.DataSourceBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.jdbc.datasource.LazyConnectionDataSourceProxy;

import javax.sql.DataSource;
import java.util.HashMap;
import java.util.Map;

@Configuration
public class DataSourceConfig {

    private static final String MASTER = "master";
    private static final String SLAVE = "slave";

    /**
     * Master DataSource (쓰기 전용)
     */
    @Bean
    @ConfigurationProperties(prefix = "spring.datasource.master.hikari")
    public DataSource masterDataSource() {
        return DataSourceBuilder.create()
            .type(HikariDataSource.class)
            .build();
    }

    /**
     * Slave DataSource (읽기 전용)
     */
    @Bean
    @ConfigurationProperties(prefix = "spring.datasource.slave.hikari")
    public DataSource slaveDataSource() {
        HikariDataSource dataSource = DataSourceBuilder.create()
            .type(HikariDataSource.class)
            .build();

        dataSource.setReadOnly(true);  // 읽기 전용 힌트
        return dataSource;
    }

    /**
     * Routing DataSource (동적 라우팅)
     */
    @Bean
    public DataSource routingDataSource() {
        ReplicationRoutingDataSource routingDataSource =
            new ReplicationRoutingDataSource();

        Map<Object, Object> dataSourceMap = new HashMap<>();
        dataSourceMap.put(MASTER, masterDataSource());
        dataSourceMap.put(SLAVE, slaveDataSource());

        routingDataSource.setTargetDataSources(dataSourceMap);
        routingDataSource.setDefaultTargetDataSource(masterDataSource());

        return routingDataSource;
    }

    /**
     * 실제 사용할 DataSource (지연 로딩)
     */
    @Bean
    @Primary
    public DataSource dataSource() {
        return new LazyConnectionDataSourceProxy(routingDataSource());
    }
}
```

#### 2단계: RoutingDataSource 구현

```java
// ReplicationRoutingDataSource.java
package com.example.demo.config;

import lombok.extern.slf4j.Slf4j;
import org.springframework.jdbc.datasource.lookup.AbstractRoutingDataSource;
import org.springframework.transaction.support.TransactionSynchronizationManager;

@Slf4j
public class ReplicationRoutingDataSource extends AbstractRoutingDataSource {

    private static final String MASTER = "master";
    private static final String SLAVE = "slave";

    @Override
    protected Object determineCurrentLookupKey() {
        // 현재 트랜잭션이 읽기 전용인지 확인
        boolean isReadOnly = TransactionSynchronizationManager.isCurrentTransactionReadOnly();

        String dataSourceType = isReadOnly ? SLAVE : MASTER;

        log.debug("현재 DataSource: {}", dataSourceType);

        return dataSourceType;
    }
}
```

#### 3단계: application.yml 설정

```yaml
# application.yml
spring:
  datasource:
    master:
      hikari:
        jdbc-url: jdbc:mysql://localhost:3306/testdb
        username: root
        password: root
        driver-class-name: com.mysql.cj.jdbc.Driver
        maximum-pool-size: 10
        minimum-idle: 5
        connection-timeout: 30000

    slave:
      hikari:
        jdbc-url: jdbc:mysql://localhost:3307/testdb
        username: root
        password: root
        driver-class-name: com.mysql.cj.jdbc.Driver
        maximum-pool-size: 50
        minimum-idle: 20
        connection-timeout: 30000
        read-only: true

  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: true
    properties:
      hibernate:
        format_sql: true

logging:
  level:
    com.example.demo: DEBUG
    org.hibernate.SQL: DEBUG
```

#### 4단계: Entity 및 Repository

```java
// User.java
package com.example.demo.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, unique = true)
    private String email;

    public User(String name, String email) {
        this.name = name;
        this.email = email;
    }
}

// UserRepository.java
package com.example.demo.repository;

import com.example.demo.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface UserRepository extends JpaRepository<User, Long> {
    List<User> findByName(String name);
}
```

#### 5단계: Service 구현 (트랜잭션 분리)

```java
// UserService.java
package com.example.demo.service;

import com.example.demo.entity.User;
import com.example.demo.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class UserService {

    private final UserRepository userRepository;

    /**
     * 사용자 생성 (Master DB 사용)
     */
    @Transactional  // readOnly=false (기본값)
    public User createUser(String name, String email) {
        log.info("[쓰기] 사용자 생성: name={}, email={}", name, email);

        User user = new User(name, email);
        User savedUser = userRepository.save(user);

        log.info("[쓰기] 사용자 저장 완료: id={}", savedUser.getId());

        return savedUser;
    }

    /**
     * 사용자 조회 (Slave DB 사용)
     */
    @Transactional(readOnly = true)  // ✅ Slave로 라우팅
    public User getUser(Long id) {
        log.info("[읽기] 사용자 조회: id={}", id);

        User user = userRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("사용자 없음"));

        log.info("[읽기] 사용자 조회 완료: name={}", user.getName());

        return user;
    }

    /**
     * 전체 사용자 조회 (Slave DB 사용)
     */
    @Transactional(readOnly = true)
    public List<User> getAllUsers() {
        log.info("[읽기] 전체 사용자 조회");

        List<User> users = userRepository.findAll();

        log.info("[읽기] 조회 완료: count={}", users.size());

        return users;
    }

    /**
     * 사용자 수정 (Master DB 사용)
     */
    @Transactional
    public User updateUser(Long id, String name) {
        log.info("[쓰기] 사용자 수정: id={}, newName={}", id, name);

        User user = userRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("사용자 없음"));

        user.setName(name);
        User updatedUser = userRepository.save(user);

        log.info("[쓰기] 수정 완료: id={}", updatedUser.getId());

        return updatedUser;
    }

    /**
     * 사용자 삭제 (Master DB 사용)
     */
    @Transactional
    public void deleteUser(Long id) {
        log.info("[쓰기] 사용자 삭제: id={}", id);

        userRepository.deleteById(id);

        log.info("[쓰기] 삭제 완료");
    }
}
```

#### 6단계: 테스트 코드

```java
// UserServiceTest.java
package com.example.demo.service;

import com.example.demo.entity.User;
import com.example.demo.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.List;

import static org.assertj.core.api.Assertions.*;

@SpringBootTest
class UserServiceTest {

    @Autowired
    private UserService userService;

    @Autowired
    private UserRepository userRepository;

    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
    }

    @Test
    void Master에서_쓰기_Slave에서_읽기() {
        // given: Master에 데이터 저장
        User createdUser = userService.createUser("홍길동", "hong@example.com");

        // when: Slave에서 조회
        User foundUser = userService.getUser(createdUser.getId());

        // then
        assertThat(foundUser.getName()).isEqualTo("홍길동");
        assertThat(foundUser.getEmail()).isEqualTo("hong@example.com");
    }

    @Test
    void 읽기_쿼리는_Slave에서_처리() {
        // given
        userService.createUser("사용자1", "user1@example.com");
        userService.createUser("사용자2", "user2@example.com");
        userService.createUser("사용자3", "user3@example.com");

        // when: Slave에서 전체 조회
        List<User> users = userService.getAllUsers();

        // then
        assertThat(users).hasSize(3);
    }

    @Test
    void 쓰기_쿼리는_Master에서_처리() {
        // given
        User user = userService.createUser("원본이름", "original@example.com");

        // when: Master에서 수정
        User updatedUser = userService.updateUser(user.getId(), "변경된이름");

        // then
        assertThat(updatedUser.getName()).isEqualTo("변경된이름");
    }
}
```

#### 실행 결과

```
===== 사용자 생성 (Master) =====
2024-01-15 10:30:00 DEBUG - 현재 DataSource: master
2024-01-15 10:30:00 INFO  - [쓰기] 사용자 생성: name=홍길동, email=hong@example.com
Hibernate: insert into users (email, name) values (?, ?)
2024-01-15 10:30:00 INFO  - [쓰기] 사용자 저장 완료: id=1

===== 사용자 조회 (Slave) =====
2024-01-15 10:30:01 DEBUG - 현재 DataSource: slave
2024-01-15 10:30:01 INFO  - [읽기] 사용자 조회: id=1
Hibernate: select u1_0.id,u1_0.email,u1_0.name from users u1_0 where u1_0.id=?
2024-01-15 10:30:01 INFO  - [읽기] 사용자 조회 완료: name=홍길동

===== 전체 조회 (Slave) =====
2024-01-15 10:30:02 DEBUG - 현재 DataSource: slave
2024-01-15 10:30:02 INFO  - [읽기] 전체 사용자 조회
Hibernate: select u1_0.id,u1_0.email,u1_0.name from users u1_0
2024-01-15 10:30:02 INFO  - [읽기] 조회 완료: count=3

결과:
✅ 쓰기 → Master (port 3306)
✅ 읽기 → Slave (port 3307)
✅ 자동 라우팅 성공!
```

#### 코드 설명

**LazyConnectionDataSourceProxy의 역할**:
```java
@Bean
@Primary
public DataSource dataSource() {
    // ✅ LazyConnectionDataSourceProxy 사용
    return new LazyConnectionDataSourceProxy(routingDataSource());
}

// LazyConnectionDataSourceProxy가 없으면:
// 1. 트랜잭션 시작 시점에 DataSource 결정
// 2. determineCurrentLookupKey() 호출
// 3. 하지만 이때는 아직 @Transactional의 readOnly 정보가 설정되기 전!
// 4. 결과: 항상 Master 선택됨 ❌

// LazyConnectionDataSourceProxy가 있으면:
// 1. 트랜잭션 시작 (readOnly 정보 설정)
// 2. 실제 쿼리 실행 시점에 Connection 획득
// 3. 이때 determineCurrentLookupKey() 호출
// 4. 결과: readOnly에 따라 정확히 라우팅됨 ✅
```

**트랜잭션별 DataSource 선택**:
```
@Transactional(readOnly = true)
    ↓
TransactionSynchronizationManager.isCurrentTransactionReadOnly() == true
    ↓
ReplicationRoutingDataSource.determineCurrentLookupKey()
    ↓
return "slave"
    ↓
Slave DB 커넥션 사용


@Transactional  (readOnly = false, 기본값)
    ↓
TransactionSynchronizationManager.isCurrentTransactionReadOnly() == false
    ↓
ReplicationRoutingDataSource.determineCurrentLookupKey()
    ↓
return "master"
    ↓
Master DB 커넥션 사용
```

---

*(이 장은 매우 길므로 PART 2로 계속됩니다...)*
