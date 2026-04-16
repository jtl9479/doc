# 학습 10. DDD / 클린 아키텍처

## Step 목차

| Step | 항목 | 카테고리 |
|------|------|----------|
| Step 1 | 소프트웨어 아키텍처 개요 — 왜 아키텍처가 중요한가 | 기초 |
| Step 2 | 레이어드 아키텍처와 그 한계 | 기초 |
| Step 3 | DDD 개요 — 왜 DDD인가, 핵심 철학 | DDD 기초 |
| Step 4 | 유비쿼터스 언어 (Ubiquitous Language) | DDD 전략 |
| Step 5 | Bounded Context와 Context Map | DDD 전략 |
| Step 6 | Entity와 Value Object | DDD 전술 |
| Step 7 | Aggregate와 Aggregate Root | DDD 전술 |
| Step 8 | Repository 패턴 | DDD 전술 |
| Step 9 | Domain Service와 Application Service | DDD 전술 |
| Step 10 | Domain Event | DDD 전술 |
| Step 11 | 헥사고날 아키텍처 (Port & Adapter) | 아키텍처 |
| Step 12 | 클린 아키텍처 (의존성 규칙, Use Case) | 아키텍처 |
| Step 13 | 레이어드 vs 헥사고날 vs 클린 — 비교와 선택 | 아키텍처 |
| Step 14 | 이벤트 소싱 + CQRS 개념 | 심화 |
| Step 15 | DDD 실전 — ERP 도메인에 DDD 적용 | 실전 |
| Step 16 | 안티패턴 — DDD를 잘못 적용하는 사례 | 실전 |

---

## 1. 개요

**현재 수준**: 레이어드 아키텍처(Controller → Service → Repository)로 ERP 개발 중. DDD/클린 아키텍처 적용 경험 없음.
**학습 목표**: 복잡한 도메인을 Bounded Context로 분리하고, Aggregate 경계를 설계하고, 헥사고날/클린 아키텍처로 코드를 구조화할 수 있음. "왜 이렇게 설계했는가"를 트레이드오프와 함께 설명 가능.
**분기 배정**: 3분기 (2026.10 ~ 2026.12)

---

## 2. 학습 순서 + 세부 항목

---

### Step 1. 소프트웨어 아키텍처 개요 — 왜 아키텍처가 중요한가

| 학습 항목 | 학습 목표 |
|----------|----------|
| 아키텍처란 | 시스템의 구조적 결정(컴포넌트 분리, 의존성 방향, 데이터 흐름). "변경 비용을 최소화하기 위한 구조"라는 정의를 설명 가능. |
| 왜 아키텍처가 중요한가 | 아키텍처 없이 개발하면 시간이 지날수록 변경 비용이 기하급수적으로 증가하는 이유(의존성 엉킴, 코드 이해 불가, 테스트 불가)를 설명 가능. |
| 좋은 아키텍처의 특성 | 변경 용이성, 테스트 용이성, 독립적 배포, 관심사 분리를 설명 가능. |
| 아키텍처 vs 디자인 패턴 | 아키텍처(시스템 수준 구조)와 디자인 패턴(코드 수준 구조)의 차이를 설명 가능. |

---

### Step 2. 레이어드 아키텍처와 그 한계

| 학습 항목 | 학습 목표 |
|----------|----------|
| 레이어드 아키텍처 | Presentation → Application(Service) → Domain → Infrastructure(Repository/DB) 4계층의 역할과 의존 방향(위 → 아래)을 설명 가능. |
| 장점 | 단순하고 익숙함. 관심사 분리가 기본적으로 됨. 대부분의 Spring 프로젝트가 이 구조. |
| 한계 — DB 중심 설계 | 레이어드 아키텍처에서 Domain 계층이 Infrastructure(DB)에 의존하게 되기 쉬운 이유를 설명 가능. "비즈니스 로직이 DB 스키마에 종속된다" 문제를 설명 가능. |
| 한계 — 도메인 빈혈 모델 | Service에 모든 로직이 몰리고 Entity는 getter/setter만 있는 "빈혈 도메인 모델(Anemic Domain Model)"의 문제점을 설명 가능. |
| 한계 — 외부 의존성 교체 어려움 | DB를 변경하거나 외부 API를 교체할 때 비즈니스 로직까지 수정해야 하는 구조적 문제를 설명 가능. |
| "이 한계를 어떻게 극복하는가?" | → DDD + 헥사고날/클린 아키텍처가 답. 이후 Step에서 학습. |

---

### Step 3. DDD 개요 — 왜 DDD인가, 핵심 철학

| 학습 항목 | 학습 목표 |
|----------|----------|
| DDD란 | Domain-Driven Design. Eric Evans가 2003년 제안. 복잡한 소프트웨어의 핵심 복잡성은 "기술"이 아니라 "도메인(비즈니스)"에 있으므로, 도메인을 중심으로 설계해야 한다는 철학을 설명 가능. |
| 왜 DDD인가 | CRUD 앱에는 불필요. 비즈니스 규칙이 복잡한 도메인(금융, ERP, 물류, 보험 등)에서 가치가 큰 이유를 설명 가능. "모든 프로젝트에 DDD를 쓸 필요는 없다"는 판단 기준을 설명 가능. |
| 전략적 설계 vs 전술적 설계 | 전략적(큰 그림: Bounded Context, Context Map): "시스템을 어떤 경계로 나눌 것인가". 전술적(코드 레벨: Entity, VO, Aggregate): "코드를 어떻게 구조화할 것인가". 두 수준의 관계를 설명 가능. |
| DDD의 핵심 가치 | 도메인 전문가와 개발자가 **같은 언어**로 소통(유비쿼터스 언어). 코드가 비즈니스를 반영. 변경이 필요한 범위가 명확(Bounded Context). |

---

### Step 4. 유비쿼터스 언어 (Ubiquitous Language)

| 학습 항목 | 학습 목표 |
|----------|----------|
| 유비쿼터스 언어란 | 도메인 전문가(기획자, 현업)와 개발자가 동일하게 사용하는 용어 체계. 코드의 클래스명, 메서드명, 변수명이 이 언어를 반영해야 하는 이유를 설명 가능. |
| 왜 중요한가 | 같은 개념을 "주문"이라 부르다가 코드에서 "Order", DB에서 "TB_ORD", API에서 "purchase"로 달라지면 소통 비용이 폭증하는 문제를 설명 가능. |
| 실무 적용 | ERP 도메인에서 "수주(RcvOrd)", "출고(Dlivy)", "매출(Sa)" 같은 용어가 코드·DB·문서에서 일관되게 사용되어야 하는 이유를 본인 경험과 연결하여 설명 가능. |
| Bounded Context별 언어 | 같은 단어가 다른 Context에서 다른 의미를 가질 수 있음(예: "상품"이 주문 Context에서는 "주문 항목", 재고 Context에서는 "재고 품목"). 이를 분리해야 하는 이유를 설명 가능. |

---

### Step 5. Bounded Context와 Context Map

| 학습 항목 | 학습 목표 |
|----------|----------|
| 서브도메인 유형 분류 (심화) | Bounded Context를 나누기 전에 비즈니스 가치에 따라 서브도메인을 분류: **Core**(핵심 경쟁력, 직접 개발, 최고 인력 투입. 예: ERP의 수주/생산 로직), **Supporting**(핵심은 아니지만 필요, 내부 개발 가능. 예: 출력물/라벨 관리), **Generic**(범용, 구매/외부 서비스 활용. 예: 인증, 로깅, 알림). "모든 곳에 DDD를 적용하는 것이 아니라 Core에 집중하고 Generic은 단순하게" 판단 가능. |
| Bounded Context란 | 도메인 모델이 유효한 경계. 같은 용어가 다른 의미를 가지는 지점에서 경계를 나눔. "하나의 모델로 모든 것을 표현하려 하면 모델이 오염된다"는 원칙을 설명 가능. |
| 경계 식별 기준 | 팀 구조(Conway's Law), 비즈니스 프로세스 경계, 용어 의미 변경 지점에서 Bounded Context를 나누는 기준을 설명 가능. |
| ERP 도메인 적용 | 수주(SM), 구매(PM), 생산(PD), 재고(IS), 회계(AC) 각각이 Bounded Context가 되는 이유. 같은 "품목"이 수주에서는 "판매 품목", 재고에서는 "재고 품목", 구매에서는 "발주 품목"인 이유를 설명 가능. |
| Context Map | Bounded Context 간 관계를 그림으로 표현. 관계 유형을 설명 가능: |
| — Shared Kernel | 두 Context가 모델 일부를 공유. 장점(코드 공유)과 위험(변경 전파)을 설명 가능. |
| — Customer-Supplier | 상류(Supplier)가 하류(Customer)에 데이터 제공. 하류의 요구를 상류가 수용하는 관계. |
| — Anticorruption Layer (ACL) | 외부 시스템의 모델이 내 도메인을 오염시키지 않도록 변환 계층을 두는 패턴. 레거시 시스템 통합에 필수인 이유를 설명 가능. |
| — Published Language | 공개된 API/이벤트 스키마로 통신. Context 간 결합도를 낮추는 방법. |

---

### Step 6. Entity와 Value Object

| 학습 항목 | 학습 목표 |
|----------|----------|
| Entity | 고유 식별자(ID)로 구분되는 객체. 생명주기가 있고 상태가 변할 수 있음. 같은 속성이라도 ID가 다르면 다른 Entity. 예: 주문(Order), 회원(Member). |
| Value Object (VO) | 식별자 없이 **값 자체**로 동일성 판단. 불변(Immutable). 예: Money(금액+통화), Address(우편번호+주소), DateRange(시작일+종료일). |
| Entity vs VO 구분 기준 | "이 객체를 식별자로 추적해야 하는가?" → YES = Entity, NO = VO. "금액 10,000원"은 다른 10,000원과 구분할 필요 없음 → VO. "주문 #1234"는 다른 주문과 구분 필요 → Entity. |
| VO의 장점 | 불변이므로 스레드 안전, 부작용 없음, 테스트 쉬움, equals/hashCode가 값 기반. Effective Java Item 17(불변 클래스)과 직결. |
| JPA에서의 VO | @Embeddable/@Embedded로 VO를 매핑. 별도 테이블이 아닌 Entity 테이블에 컬럼으로 포함. |
| 빈혈 모델 vs 풍부한 모델 | Entity에 비즈니스 로직을 넣는 "풍부한 도메인 모델" vs getter/setter만 있는 "빈혈 모델"의 차이. DDD에서 풍부한 모델을 지향하는 이유를 설명 가능. |

---

### Step 7. Aggregate와 Aggregate Root

| 학습 항목 | 학습 목표 |
|----------|----------|
| Aggregate란 | 관련된 Entity/VO의 묶음으로, 데이터 변경의 일관성 경계. "하나의 트랜잭션에서 함께 변경되어야 하는 객체 그룹"을 설명 가능. |
| Aggregate Root | Aggregate의 진입점. 외부에서 Aggregate 내부 객체에 직접 접근하지 않고 Root를 통해서만 접근. 예: Order(Root) → OrderItem(내부 Entity). 외부에서 OrderItem을 직접 수정하면 안 되는 이유를 설명 가능. |
| Aggregate 설계 규칙 | ① Root를 통해서만 내부 수정, ② Aggregate 간에는 ID로만 참조(객체 참조 X), ③ 하나의 트랜잭션에서 하나의 Aggregate만 수정, ④ Aggregate 크기는 작게(작은 Aggregate 원칙). 각 규칙의 이유를 설명 가능. |
| Aggregate 경계 잡기 | "왜 이 Aggregate 경계를 이렇게 잡았는가?"를 비즈니스 불변식(항상 참이어야 하는 규칙)으로 설명 가능. 예: "주문 총액 = 주문 항목 합계"는 Order Aggregate 내에서 보장 → OrderItem은 Order Aggregate 내부. |
| Aggregate 간 통신 | Aggregate 간에는 도메인 이벤트(Domain Event)로 통신. 직접 참조하지 않는 이유(결합도 감소, 독립적 배포/확장)를 설명 가능. |
| Factory 패턴 (심화) | 복잡한 Aggregate Root 생성 시 도메인 규칙을 보장하는 Factory의 역할을 설명 가능. 생성자만으로 부족한 경우(여러 불변식 검증, 다른 Aggregate 정보 참조, 복잡한 초기화)에 Factory를 사용하는 이유를 설명 가능. "불완전한 상태의 객체 생성을 원천 차단"하는 수단으로서 Factory가 도메인 정합성을 지키는 핵심 장치임을 설명 가능. Effective Java Item 1(정적 팩토리 메서드)과 DDD Factory의 관계를 설명 가능. |
| 잘못된 Aggregate | 너무 큰 Aggregate(모든 것을 한 트랜잭션에) → 성능 저하, 동시성 충돌. 너무 작은 Aggregate(Entity 1개짜리) → 비즈니스 불변식 깨짐. 적절한 크기 판단 기준을 설명 가능. |

---

### Step 8. Repository 패턴

| 학습 항목 | 학습 목표 |
|----------|----------|
| Repository란 | Aggregate의 영속성을 추상화하는 인터페이스. 도메인 계층이 DB 기술(JPA, MyBatis, JDBC)에 의존하지 않게 하는 역할을 설명 가능. |
| Repository는 Aggregate 단위 | Aggregate Root 하나당 Repository 하나. OrderRepository는 있지만 OrderItemRepository는 없음(OrderItem은 Order Aggregate 내부). 이 규칙의 이유를 설명 가능. |
| 인터페이스와 구현 분리 | 도메인 계층에 인터페이스(OrderRepository), 인프라 계층에 구현(JpaOrderRepository). 의존성 역전(DIP)이 적용되는 구조를 설명 가능. |
| Spring Data JPA와의 관계 | Spring Data JPA의 JpaRepository가 Repository 패턴을 쉽게 구현하게 해줌. 하지만 JpaRepository를 도메인 계층에 직접 노출하면 DDD가 깨지는 이유(JPA 의존성이 도메인에 침투)를 설명 가능. |

---

### Step 9. Domain Service와 Application Service

| 학습 항목 | 학습 목표 |
|----------|----------|
| Domain Service | 하나의 Entity/VO에 속하지 않는 도메인 로직을 담는 서비스. 예: 환율 계산(Money 변환), 재고 가용성 판단(여러 Aggregate 정보 필요). 상태를 가지지 않음(Stateless). |
| Application Service | 유스케이스를 조율(Orchestrate)하는 서비스. 도메인 로직은 없고 흐름 제어만: Repository 호출 → 도메인 객체에 비즈니스 위임 → 결과 반환 → 이벤트 발행. |
| Domain Service vs Application Service | Domain Service: 도메인 로직 포함, 도메인 계층. Application Service: 도메인 로직 없음, 어플리케이션 계층. "이 로직이 도메인 규칙인가, 유스케이스 흐름인가?"로 구분 가능. |
| Controller → Application Service → Domain | Controller(HTTP 처리) → Application Service(유스케이스 조율) → Domain Entity/Service(비즈니스 로직) → Repository(영속성)의 호출 흐름을 설명 가능. |
| 서비스 비대화 방지 | Application Service가 모든 로직을 가지면 빈혈 모델. "Service에서 if-else가 늘어나면 도메인 로직이 새고 있는 신호"를 식별 가능. |

---

### Step 10. Domain Event

| 학습 항목 | 학습 목표 |
|----------|----------|
| Domain Event란 | 도메인에서 발생한 사건. "주문이 생성되었다(OrderCreated)", "결제가 완료되었다(PaymentCompleted)". 과거형으로 네이밍하는 이유를 설명 가능. |
| 왜 필요한가 | Aggregate 간 직접 참조/호출 없이 느슨하게 연결. "주문 생성 → 재고 차감"을 Order가 Inventory를 직접 호출하지 않고 이벤트로 처리하는 이유(결합도 감소)를 설명 가능. |
| 이벤트 발행 방식 | Spring ApplicationEventPublisher(동기), Kafka/RabbitMQ(비동기)로 발행. 동기 vs 비동기의 트레이드오프(즉시 일관성 vs 최종 일관성)를 설명 가능. |
| @TransactionalEventListener | 트랜잭션 커밋 후 이벤트 처리. "주문 저장 실패 시 재고 차감 이벤트가 발행되면 안 된다" → AFTER_COMMIT이 필수인 이유를 설명 가능. (Spring 학습과 연계) |
| 이벤트와 Saga | 여러 Aggregate/서비스에 걸친 비즈니스 프로세스를 Domain Event + Saga로 처리하는 패턴. (MSA 학습과 연계) |

---

### Step 11. 헥사고날 아키텍처 (Port & Adapter)

| 학습 항목 | 학습 목표 |
|----------|----------|
| 헥사고날 아키텍처란 | Alistair Cockburn 제안. 도메인 로직을 중심(내부)에 두고, 외부(DB, API, UI)와의 통신을 Port(인터페이스)와 Adapter(구현)로 분리. "Ports and Adapters"라고도 불림. |
| 핵심 원칙 | 도메인은 외부를 모름. 외부가 도메인에 적응(Adapt). 의존성 방향이 항상 외부 → 내부. |
| Port | 도메인이 외부와 소통하는 인터페이스. Inbound Port(외부 → 도메인, 예: OrderUseCase), Outbound Port(도메인 → 외부, 예: OrderRepository 인터페이스). |
| Adapter | Port의 구현. Inbound Adapter(Controller, 메시지 리스너), Outbound Adapter(JPA Repository 구현, 외부 API 호출 구현). |
| 장점 | 도메인 로직이 프레임워크/DB에 독립. DB를 JPA→MyBatis로 교체해도 도메인 코드 변경 없음. 테스트 시 Adapter를 Mock으로 대체 용이. |
| 패키지 구조 | domain/(Entity, VO, Port 인터페이스), application/(UseCase 구현), adapter/in/(Controller), adapter/out/(JPA, 외부 API) 구조를 설명 가능. |

---

### Step 12. 클린 아키텍처 (의존성 규칙, Use Case)

| 학습 항목 | 학습 목표 |
|----------|----------|
| 클린 아키텍처란 | Robert C. Martin(Uncle Bob) 제안. 동심원 구조: Entity(가장 안쪽) → Use Case → Interface Adapter → Framework & Driver(가장 바깥). |
| 의존성 규칙 (Dependency Rule) | 의존성은 항상 바깥 → 안쪽. 안쪽 원은 바깥 원을 모름. Entity는 Use Case를 모르고, Use Case는 Controller를 모름. 이 규칙이 왜 중요한지(안쪽 변경이 바깥에 전파 안 됨)를 설명 가능. |
| Use Case | 하나의 비즈니스 유스케이스를 담는 클래스. "주문 생성(CreateOrderUseCase)", "주문 취소(CancelOrderUseCase)". Application Service와 유사하지만 더 명시적인 단일 책임. |
| 헥사고날과의 관계 | 클린 아키텍처와 헥사고날 아키텍처의 핵심 원칙(도메인 중심, 의존성 역전)은 동일. 표현 방식/용어가 다를 뿐. 실무에서는 혼합 적용이 일반적임을 설명 가능. |

---

### Step 13. 레이어드 vs 헥사고날 vs 클린 — 비교와 선택

| 학습 항목 | 학습 목표 |
|----------|----------|
| 3가지 아키텍처 비교 | 레이어드(단순, DB 중심, 소규모 적합), 헥사고날(도메인 중심, Port/Adapter로 외부 분리), 클린(의존성 규칙 엄격, Use Case 명시적). 각각의 장단점을 표로 비교 가능. |
| 선택 기준 | 단순 CRUD → 레이어드 충분. 비즈니스 복잡 + 외부 의존성 교체 가능성 → 헥사고날/클린. 팀 크기, 프로젝트 수명, 도메인 복잡도에 따른 판단 기준을 설명 가능. |
| 과도한 아키텍처 경계 | 단순 프로젝트에 헥사고날/클린을 적용하면 오히려 복잡성만 증가("over-engineering"). "이 프로젝트에 이 아키텍처가 필요한가?"를 판단하는 능력이 시니어임을 설명 가능. |
| 점진적 전환 | 레이어드 → 헥사고날/클린으로 한 번에 전환하지 않고, 핵심 도메인부터 점진적으로 적용하는 전략을 설명 가능. |
| 모듈러 모놀리스 (심화) | 레이어드(경계 없음)와 MSA(서비스 분리) 사이의 중간 지점. 하나의 배포 단위(모놀리스)이지만 Bounded Context에 따라 패키지/모듈을 엄격히 격리하는 구조를 설명 가능. 모듈 간 통신은 공개 API(인터페이스)만 허용, 내부 직접 참조 금지. ERP처럼 도메인이 복잡하지만 MSA로 가기엔 인프라/운영 비용이 큰 경우 가장 현실적인 대안인 이유를 설명 가능. 나중에 MSA로 전환할 때 모듈 경계가 그대로 서비스 경계가 되는 장점을 설명 가능. |

---

### Step 14. 이벤트 소싱 + CQRS 개념

| 학습 항목 | 학습 목표 |
|----------|----------|
| 이벤트 소싱 (Event Sourcing) | 현재 상태를 저장하는 대신 **상태 변경 이벤트 전체**를 저장. 이벤트를 순서대로 재생하면 현재 상태를 복원 가능. |
| 장점 | 완전한 변경 이력(감사 추적), 시간 여행 쿼리(특정 시점 상태 조회), 이벤트 재생으로 새로운 뷰 생성 가능. |
| 단점 | 복잡성 증가, 이벤트 스키마 진화 어려움, 스냅샷 필요(이벤트가 많아지면 재생 느림), 학습 곡선. |
| CQRS (Command Query Responsibility Segregation) | 쓰기(Command)와 읽기(Query)의 모델/저장소를 분리. 쓰기는 정규화된 모델, 읽기는 비정규화된 뷰. 각각 독립적으로 확장 가능. |
| 이벤트 소싱 + CQRS | 이벤트 소싱으로 쓰기 → 이벤트를 소비하여 읽기 전용 뷰 생성 → 읽기 최적화. "항상 필요한가?" → 아님. 복잡한 도메인 + 감사 요구 + 읽기/쓰기 패턴이 극단적으로 다를 때만 적합. |
| ERP 연결 | 회계의 "전표(분개)"가 이벤트 소싱과 유사한 구조임을 설명 가능. 차변/대변 기록이 이벤트이고, 잔액은 이벤트를 합산한 결과. |
| 이벤트 스키마 버전 관리 (심화) | 이벤트가 영구 저장되므로 스키마를 함부로 변경 못 하는 문제를 설명 가능. 필드 추가(Optional + 기본값), 필드 삭제(단계적 폐기), 타입 변경(새 이벤트 타입으로 분리)의 호환성 규칙을 설명 가능. 이벤트 Upcasting(구 버전 이벤트를 읽을 때 신 버전으로 변환)의 개념을 설명 가능. |
| 스냅샷 설계 (심화) | 이벤트가 수만 개 쌓이면 재생 속도가 느려지는 문제를 설명 가능. N번째 이벤트마다 현재 상태를 스냅샷으로 저장 → 복원 시 최신 스냅샷 + 이후 이벤트만 재생하여 속도를 개선하는 원리를 설명 가능. 스냅샷 주기(너무 자주 = 저장소 부담, 너무 드물 = 재생 느림)의 트레이드오프를 설명 가능. |

---

### Step 15. DDD 실전 — ERP 도메인에 DDD 적용

| 학습 항목 | 학습 목표 |
|----------|----------|
| ERP Bounded Context 식별 | 수주(SM), 구매(PM), 생산(PD), 재고(IS), 회계(AC), 기준정보(CO) 각각을 Bounded Context로 식별하고, Context Map(관계)을 그릴 수 있음. |
| 수주(SM) Aggregate 설계 | Order(Aggregate Root) → OrderItem(내부 Entity). "주문 총액 = 항목 합계"가 Aggregate 내 불변식. 거래처(Customer)는 다른 Aggregate이므로 ID 참조만. |
| 도메인 이벤트 흐름 | "수주 확정(OrderConfirmed)" → "재고 예약(InventoryReserved)" → "출고 지시(ShipmentCreated)" → "매출 반영(RevenueRecorded)" 이벤트 체인을 설계 가능. |
| 비즈니스 불변식 | "재고보다 많이 출고할 수 없다", "매출은 출고 완료 후에만 인식", "수주 취소 시 예약된 재고 복원" 같은 불변식을 코드로 표현하는 방법을 설명 가능. |
| 기존 레이어드 코드를 DDD로 전환 | ERP Service 클래스의 비즈니스 로직을 Entity/VO/Domain Service로 이동하는 리팩토링 과정을 설명 가능. |

---

### Step 16. 안티패턴 — DDD를 잘못 적용하는 사례

| 학습 항목 | 학습 목표 |
|----------|----------|
| 빈혈 도메인 모델 | Entity에 getter/setter만 있고 Service에 모든 로직. "DDD를 한다고 하면서 실제로는 CRUD"인 상태. 식별 기준을 설명 가능. |
| Aggregate가 너무 큼 | 하나의 Aggregate에 모든 관련 Entity를 넣음 → 트랜잭션 경합, 성능 저하. "주문 + 결제 + 배송을 하나의 Aggregate로" 같은 실수를 설명 가능. |
| Bounded Context 없이 전술 패턴만 적용 | Entity, VO, Repository 네이밍만 따르고 Context 분리 없음. "전략 없는 전술은 무의미"를 설명 가능. |
| 기술 주도 설계 | DB 스키마나 프레임워크에 맞춰 도메인 모델을 설계. "JPA 매핑이 편하게"가 아니라 "비즈니스가 표현되게"가 우선인 이유를 설명 가능. |
| 모든 프로젝트에 DDD 강제 | 단순 CRUD에 DDD를 적용하면 over-engineering. "DDD가 필요한가?"를 판단하는 것이 시니어의 역할임을 설명 가능. |

---

## 3. 자가 검증

### DDD 기초
- [ ] "DDD란?" → 핵심 철학(도메인 중심 설계)을 2분 설명 가능
- [ ] "유비쿼터스 언어란?" → 왜 중요하고 어떻게 적용하는지 설명 가능
- [ ] "DDD가 필요한 프로젝트와 불필요한 프로젝트" 판단 기준 설명 가능

### DDD 전략
- [ ] "Core/Supporting/Generic 서브도메인 차이" → ERP에서 예시 + 자원 집중 판단 기준 설명 가능
- [ ] "Bounded Context란?" → 경계 식별 기준 + ERP 도메인에서 예시 설명 가능
- [ ] "Context Map의 관계 유형" → ACL, Customer-Supplier 등 설명 가능
- [ ] ERP 시스템을 Bounded Context로 분리하여 Context Map 그릴 수 있음

### DDD 전술
- [ ] "Entity vs Value Object 구분 기준" → 식별자 필요 여부 설명 가능
- [ ] "Aggregate란?" → 일관성 경계 + Root를 통한 접근 설명 가능
- [ ] "왜 이 Aggregate 경계를 이렇게 잡았는가?" → 비즈니스 불변식으로 설명 가능
- [ ] "Aggregate 간에는 ID 참조만 하는 이유" 설명 가능
- [ ] "Aggregate 생성 시 Factory 패턴이 필요한 경우" 설명 가능
- [ ] "Domain Service vs Application Service 차이" 설명 가능
- [ ] "빈혈 도메인 모델의 문제점" 설명 가능

### 아키텍처
- [ ] "헥사고날 아키텍처란?" → Port/Adapter + 의존성 방향 설명 가능
- [ ] 헥사고날 구조로 외부 의존성(DB, API) 교체 가능한 설계 설명 가능
- [ ] "레이어드 vs 헥사고날 vs 클린 차이와 선택 기준" 설명 가능
- [ ] "모듈러 모놀리스란?" → MSA와의 차이 + ERP 같은 시스템에서 현실적 대안인 이유 설명 가능
- [ ] "클린 아키텍처의 의존성 규칙" 설명 가능

### 심화/실전
- [ ] "이벤트 소싱이란?" → 장단점 + ERP 회계(전표)와의 연결 설명 가능
- [ ] "CQRS란?" → 읽기/쓰기 분리 + 적합한 상황 설명 가능
- [ ] "이벤트 소싱에서 이벤트가 수만 개 쌓이면?" → 스냅샷 설계 + 트레이드오프 설명 가능
- [ ] "이벤트 스키마가 변경되면?" → 버전 관리 규칙 + Upcasting 설명 가능
- [ ] ERP 도메인에서 "수주→재고→출고→매출" 이벤트 흐름을 설계 가능
- [ ] "DDD 안티패턴 3가지" 즉시 답변 가능

---

## 4. 진행 상태

| Step | 항목 | 상태 |
|------|------|------|
| Step 1 | 소프트웨어 아키텍처 개요 | 미시작 |
| Step 2 | 레이어드 아키텍처와 한계 | 미시작 |
| Step 3 | DDD 개요 | 미시작 |
| Step 4 | 유비쿼터스 언어 | 미시작 |
| Step 5 | Bounded Context + Context Map | 미시작 |
| Step 6 | Entity + Value Object | 미시작 |
| Step 7 | Aggregate + Aggregate Root | 미시작 |
| Step 8 | Repository 패턴 | 미시작 |
| Step 9 | Domain Service + Application Service | 미시작 |
| Step 10 | Domain Event | 미시작 |
| Step 11 | 헥사고날 아키텍처 | 미시작 |
| Step 12 | 클린 아키텍처 | 미시작 |
| Step 13 | 아키텍처 비교와 선택 | 미시작 |
| Step 14 | 이벤트 소싱 + CQRS | 미시작 |
| Step 15 | DDD 실전 (ERP 적용) | 미시작 |
| Step 16 | 안티패턴 | 미시작 |

---

## 5. 참고 자료 (보조용)

| 자료 | 용도 |
|------|------|
| DDD Distilled (Vaughn Vernon) | Step 3~10 보조. DDD 입문 |
| Implementing Domain-Driven Design (Vaughn Vernon) | Step 3~10 보조. DDD 심화 |
| Clean Architecture (Robert C. Martin) | Step 11~13 보조. 아키텍처 원칙 |
| Get Your Hands Dirty on Clean Architecture (Tom Hombergs) | Step 11~13 보조. Spring 기반 헥사고날 실전 |

---

> 이 문서는 Claude가 미래 세션에서 읽고 학습을 안내하기 위한 가이드입니다.
> 사용자가 "DDD 공부하자" 또는 "Step N 하자"라고 하면, 진행 상태를 확인하고 다음 미시작 Step부터 학습_템플릿.md 형식으로 진행합니다.
> ERP 도메인 경험을 최대한 활용하여 설명합니다 (수주/구매/생산/재고/회계 예시).
