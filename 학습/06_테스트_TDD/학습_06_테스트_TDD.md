# 학습 06. 테스트 (TDD/JUnit/Mockito/TestContainers)

## Step 목차

| Step | 항목 | 카테고리 |
|------|------|----------|
| Step 1 | 테스트 기초 — 왜 테스트하는가, 테스트 종류, 테스트 피라미드 | 기초 |
| Step 2 | JUnit 5 기본 — 어노테이션, 생명주기, Assertions | JUnit |
| Step 3 | JUnit 5 심화 — Parameterized, Nested, Dynamic Test | JUnit |
| Step 4 | 테스트 더블 — Stub, Mock, Fake, Spy 구분 | 테스트 원칙 |
| Step 5 | Mockito 기본 — Mock 생성, when/thenReturn, verify | Mockito |
| Step 6 | Mockito 심화 — ArgumentCaptor, BDD style, InOrder | Mockito |
| Step 7 | 테스트 가능한 설계 — 의존성 역전, 인터페이스 분리 | 테스트 원칙 |
| Step 8 | 좋은 테스트의 원칙 — FIRST, 테스트 냄새, 유지보수성 | 테스트 원칙 |
| Step 9 | TDD — Red → Green → Refactor 사이클 | TDD |
| Step 10 | TDD 실전 — 실제 기능을 TDD로 개발 | TDD |
| Step 11 | Spring 테스트 — @SpringBootTest, MockMvc, 슬라이스 테스트 | Spring 테스트 |
| Step 12 | TestContainers — 실제 DB/Redis/Kafka 통합 테스트 | 통합 테스트 |
| Step 13 | 테스트 전략 설계 — 어디까지 테스트할 것인가 | 전략 |
| Step 14 | 레거시 코드 테스트 — 테스트 없는 코드에 테스트 추가 | 실전 |

---

## 1. 개요

**현재 수준**: 기본 단위 테스트 작성 가능. TDD 경험 없음. 통합 테스트·테스트 전략 설계 경험 없음.
**학습 목표**: TDD로 새 기능을 개발하는 것이 자연스러움. 단위/통합/E2E 테스트 전략을 설계 가능. "이 코드는 왜 테스트하기 어려운가"를 식별하고 리팩토링 가능.
**분기 배정**: 2분기 (2026.07 ~ 2026.09)

---

## 2. 학습 순서 + 세부 항목

---

### Step 1. 테스트 기초 — 왜 테스트하는가, 테스트 종류, 테스트 피라미드

| 학습 항목 | 학습 목표 |
|----------|----------|
| 왜 테스트하는가 | 테스트가 주는 가치(버그 사전 발견, 리팩토링 안전망, 문서 역할, 설계 개선 유도)를 설명 가능. "테스트를 안 짜면 어떤 일이 벌어지는가"를 실무 관점에서 설명 가능. |
| 단위 테스트 (Unit Test) | 하나의 클래스/메서드를 외부 의존성 없이 테스트. 빠르고 격리됨. 가장 많이 작성해야 하는 이유를 설명 가능. |
| 통합 테스트 (Integration Test) | 여러 컴포넌트가 함께 동작하는지 검증. DB/외부 API 연동 포함. 단위 테스트보다 느리지만 실제 동작 검증에 필수인 이유를 설명 가능. |
| E2E 테스트 (End-to-End Test) | 전체 시스템을 사용자 관점에서 검증. 가장 느리고 유지보수 비용 높음. 최소한으로 유지해야 하는 이유를 설명 가능. |
| 테스트 피라미드 | 단위(많이) → 통합(적당히) → E2E(최소) 비율의 근거(속도, 비용, 안정성)를 설명 가능. "역피라미드(E2E가 많은 구조)"가 위험한 이유를 설명 가능. |

---

### Step 2. JUnit 5 기본 — 어노테이션, 생명주기, Assertions

| 학습 항목 | 학습 목표 |
|----------|----------|
| JUnit 5 구조 | JUnit Platform + JUnit Jupiter + JUnit Vintage 구조를 알고 있음. Jupiter가 실제 테스트 작성 API임을 이해. |
| 핵심 어노테이션 | @Test, @BeforeEach, @AfterEach, @BeforeAll, @AfterAll, @DisplayName, @Disabled 각각의 역할과 실행 순서를 설명 가능. |
| 생명주기 | 테스트 클래스 인스턴스가 메서드마다 새로 생성되는 이유(테스트 격리)를 설명 가능. @TestInstance(Lifecycle.PER_CLASS)로 변경 가능함을 알고 있음. |
| Assertions | assertEquals, assertNotNull, assertTrue, assertThrows, assertAll, assertTimeout 사용 가능. assertAll로 여러 검증을 묶는 이유(모든 실패를 한 번에 확인)를 설명 가능. |
| AssertJ | JUnit Assertions 대비 AssertJ의 장점(가독성, 체이닝, 풍부한 API)을 설명 가능. assertThat(actual).isEqualTo(expected) 패턴을 사용 가능. |

---

### Step 3. JUnit 5 심화 — Parameterized, Nested, Dynamic Test

| 학습 항목 | 학습 목표 |
|----------|----------|
| @ParameterizedTest | @ValueSource, @CsvSource, @MethodSource, @EnumSource로 여러 입력에 대해 같은 테스트를 반복 실행하는 방법. 중복 테스트 코드를 줄이는 효과를 설명 가능. |
| @Nested | 테스트를 계층적으로 구성하여 "상황(given) → 행동(when) → 결과(then)" 구조를 표현하는 패턴. BDD 스타일 테스트 구성을 적용 가능. |
| @Tag | 테스트를 그룹핑(unit, integration, slow 등)하여 선택적 실행하는 방법. CI/CD에서 빌드 속도 최적화에 활용 가능. |
| @Timeout | 성능 테스트 기본. 특정 시간 내 완료되지 않으면 실패로 처리하는 방법을 알고 있음. |

---

### Step 4. 테스트 더블 — Stub, Mock, Fake, Spy 구분

| 학습 항목 | 학습 목표 |
|----------|----------|
| 테스트 더블이란 | 실제 의존 객체를 대체하는 가짜 객체의 총칭. 왜 필요한지(외부 의존성 격리, 테스트 속도, 결정론적 테스트)를 설명 가능. |
| Dummy | 전달만 하고 실제 사용하지 않는 객체. 파라미터를 채우기 위한 용도임을 설명 가능. |
| Stub | 미리 정해진 값을 반환하는 객체. "이 메서드가 호출되면 항상 이 값을 리턴한다"는 동작을 제공. 상태 검증(state verification)에 사용. |
| Mock | 호출 여부·횟수·인자를 검증하는 객체. 행위 검증(behavior verification)에 사용. Stub과의 핵심 차이(Mock은 "무엇이 호출되었는가"를 검증)를 설명 가능. |
| Spy | 실제 객체를 감싸서 일부 메서드만 오버라이드. 나머지는 실제 동작. 실제 객체의 행동을 유지하면서 특정 호출을 감시할 때 사용. |
| Fake | 실제 동작하지만 단순화된 구현(예: InMemory DB). 프로덕션에는 부적합하지만 테스트에서 빠르고 가벼운 대체. |
| 상태 검증 vs 행위 검증 | Stub(상태 검증: 결과가 맞는지) vs Mock(행위 검증: 메서드가 호출되었는지)의 차이를 설명 가능. 어떤 상황에서 어느 쪽이 적합한지 판단 가능. |

---

### Step 5. Mockito 기본 — Mock 생성, when/thenReturn, verify

| 학습 항목 | 학습 목표 |
|----------|----------|
| Mock 생성 | @Mock, @InjectMocks, @ExtendWith(MockitoExtension.class)로 Mock을 생성하고 주입하는 방법을 적용 가능. |
| Stubbing | when(mock.method()).thenReturn(value), when(...).thenThrow(exception)으로 Mock의 반환값을 지정 가능. |
| Verify | verify(mock).method(), verify(mock, times(2)).method(), verify(mock, never()).method()로 호출 검증 가능. |
| any() matcher | any(), anyString(), anyLong(), eq() 등 Argument Matcher 사용 가능. Matcher 혼용 규칙(전부 Matcher이거나 전부 리터럴)을 알고 있음. |
| 주의사항 | Mock의 기본 반환값(null, 0, false, 빈 컬렉션)을 알고 있음. void 메서드 Stubbing(doNothing, doThrow)을 사용 가능. |

---

### Step 6. Mockito 심화 — ArgumentCaptor, BDD style, InOrder

| 학습 항목 | 학습 목표 |
|----------|----------|
| ArgumentCaptor | 메서드에 전달된 인자를 캡처하여 상세 검증하는 방법. capture() → getValue()로 캡처된 값 검증 가능. "이벤트 발행 시 전달된 DTO의 필드가 정확한지" 검증하는 실전 패턴을 적용 가능. |
| BDD style | given(mock.method()).willReturn(value), then(mock).should().method() 형태로 Given-When-Then 스타일의 가독성 높은 테스트 작성 가능. BDDMockito 사용법을 알고 있음. |
| InOrder | 메서드 호출 순서를 검증하는 방법. inOrder(mock1, mock2)로 여러 Mock의 호출 순서 검증 가능. |
| @Spy | 실제 객체를 부분적으로 Mocking. doReturn(...).when(spy).method() 패턴. @Mock과의 차이(Spy는 실제 메서드 호출, Mock은 기본 null 반환)를 설명 가능. |
| Mockito 한계 | static 메서드, final 클래스, 생성자 Mocking의 어려움을 설명 가능. mockStatic()(Mockito 3.4+)의 존재를 알고 있되, static Mocking은 설계 개선이 우선임을 이해. |

---

### Step 7. 테스트 가능한 설계 — 의존성 역전, 인터페이스 분리

| 학습 항목 | 학습 목표 |
|----------|----------|
| 테스트하기 어려운 코드 | new로 직접 객체 생성, static 메서드 호출, 전역 상태(Singleton), 현재 시간(LocalDateTime.now()), 랜덤 값 등이 테스트를 어렵게 만드는 이유를 설명 가능. |
| 의존성 역전 (DIP) | 구체 클래스가 아닌 인터페이스에 의존하도록 설계하면 Mock 주입이 가능해지는 원리를 설명 가능. "테스트하기 어려운 코드 → 인터페이스 추출 → DI → Mock 주입 → 테스트 가능" 리팩토링 과정을 적용 가능. |
| 시간/랜덤의 테스트 | Clock 인터페이스 주입, 또는 java.time.Clock을 DI하여 테스트에서 고정 시간을 사용하는 패턴을 적용 가능. |
| 순수 함수 지향 | 외부 상태에 의존하지 않는 순수 함수(같은 입력 → 항상 같은 출력)는 테스트가 쉬운 이유를 설명 가능. 비즈니스 로직을 순수 함수로 추출하는 리팩토링을 적용 가능. |
| 코드 리뷰에서 식별 | "이 코드는 왜 테스트하기 어려운가?"를 코드 리뷰에서 식별하고 개선 방향을 제안 가능. |
| 테스트가 설계를 강제하는 관점 (심화) | "Mocking이 너무 많이 필요하다 = 의존성이 너무 많다 = SRP(단일 책임 원칙) 위반"이라는 설계적 경고를 해석 가능. 테스트를 짜기 위해 코드를 고쳤다면 그것이 설계 개선임을 설명 가능. "테스트하기 어려운 코드는 사용하기도 어려운 코드"라는 원칙을 설명 가능. Mock이 5개 이상 필요한 테스트 → 클래스 분리/책임 분배를 고려해야 하는 신호로 해석 가능. |

---

### Step 8. 좋은 테스트의 원칙 — FIRST, 테스트 냄새, 유지보수성

| 학습 항목 | 학습 목표 |
|----------|----------|
| FIRST 원칙 | Fast(빠르게), Independent(독립적), Repeatable(반복 가능), Self-validating(자체 검증), Timely(적시에 작성) 각각을 설명 가능. |
| 테스트 냄새 (Test Smell) | 깨지기 쉬운 테스트(구현 세부사항에 의존), 느린 테스트(불필요한 통합 테스트), 의미 없는 테스트(항상 통과), 중복 테스트를 식별 가능. |
| 구현이 아닌 행위를 테스트 | "메서드 내부에서 A 메서드를 호출했는가"가 아니라 "주어진 입력에 대해 올바른 출력이 나오는가"를 테스트해야 하는 이유를 설명 가능. Mock의 과도한 행위 검증이 테스트를 깨지기 쉽게 만드는 이유를 설명 가능. |
| 테스트 명명 규칙 | @DisplayName 또는 메서드명으로 "어떤 상황에서 어떤 행동을 하면 어떤 결과가 나오는지"를 표현하는 방법. given_when_then 또는 should_when 패턴을 적용 가능. |
| AAA / Given-When-Then | Arrange-Act-Assert / Given-When-Then 구조로 테스트를 작성하는 패턴. 각 섹션을 명확히 분리하는 이유(가독성)를 설명 가능. |

---

### Step 9. TDD — Red → Green → Refactor 사이클

| 학습 항목 | 학습 목표 |
|----------|----------|
| TDD란 | 테스트를 먼저 작성하고(Red), 테스트를 통과하는 최소 코드를 작성한 뒤(Green), 리팩토링(Refactor)하는 사이클을 설명 가능. |
| Red 단계 | 실패하는 테스트를 먼저 작성. "아직 구현하지 않은 기능의 기대 동작"을 테스트로 표현하는 방법. 컴파일 에러가 나도 괜찮은 이유를 이해. |
| Green 단계 | 테스트를 통과시키기 위한 **최소한의** 코드만 작성. 완벽한 코드가 아니라 동작하는 코드가 목표. "일단 하드코딩으로 통과시키고 점진적으로 일반화"하는 전략을 적용 가능. |
| Refactor 단계 | 테스트가 통과하는 상태를 유지하며 코드 품질을 개선. 중복 제거, 네이밍 개선, 설계 개선. "테스트가 안전망이므로 자신 있게 리팩토링 가능"을 체험. |
| TDD의 이점 | 설계 개선(테스트하기 쉬운 코드 = 좋은 설계), 회귀 방지, 문서 역할, 개발 속도(장기적)를 설명 가능. |
| TDD의 한계 | 모든 코드에 TDD가 적합하지 않음(탐색적 코드, UI, 프로토타입). TDD가 적합한 영역(비즈니스 로직, 알고리즘, 유틸리티)을 판단 가능. |

---

### Step 10. TDD 실전 — 실제 기능을 TDD로 개발

| 학습 항목 | 학습 목표 |
|----------|----------|
| 간단한 도메인 로직 TDD | 계산기, 문자열 파서 같은 단순한 예제로 Red-Green-Refactor 사이클을 체험. |
| 서비스 레이어 TDD | Repository를 Mock으로 대체하고 Service 로직을 TDD로 개발하는 패턴. "외부 의존성을 Mock으로 격리 → 비즈니스 로직만 테스트" 패턴을 적용 가능. |
| 점진적 일반화 | 테스트 케이스를 하나씩 추가하면서 코드를 점진적으로 일반화하는 과정. "Triangulation(삼각 측량)" 기법을 설명 가능. |
| 경계값 테스트 | 0, null, 빈 문자열, 최대값, 음수 등 경계 조건을 TDD 사이클에서 자연스럽게 커버하는 방법. |
| ERP 도메인 적용 | 수주 금액 계산, 재고 차감 검증, 세금 계산 등 ERP 비즈니스 로직을 TDD로 개발하는 시나리오를 연습 가능. |

---

### Step 11. Spring 테스트 — @SpringBootTest, MockMvc, 슬라이스 테스트

| 학습 항목 | 학습 목표 |
|----------|----------|
| @SpringBootTest | 전체 Application Context를 로딩하는 통합 테스트. webEnvironment(MOCK, RANDOM_PORT, DEFINED_PORT, NONE) 각 옵션의 차이를 설명 가능. |
| MockMvc | 서블릿 컨테이너 없이 Controller 테스트. perform(get/post) → andExpect(status/content/jsonPath) 패턴으로 API 검증 가능. |
| @WebMvcTest | Controller 레이어만 로딩하는 슬라이스 테스트. Service를 @MockBean으로 대체하여 컨트롤러 로직만 격리 테스트 가능. |
| @DataJpaTest | JPA Repository 레이어만 로딩. 내장 DB(H2) 또는 TestContainers로 쿼리 검증 가능. @Transactional 자동 롤백을 알고 있음. |
| @MockBean / @SpyBean | Spring Context의 빈을 Mock/Spy로 교체. @MockBean이 Context를 재생성하는 단점(테스트 속도 저하)을 설명 가능. Context 캐싱이 깨지는 이유를 설명 가능. |
| 슬라이스 테스트 선택 기준 | "어떤 계층을 테스트하는가"에 따라 @WebMvcTest / @DataJpaTest / @SpringBootTest를 선택하는 판단 기준을 설명 가능. |
| Context Caching 최적화 (심화) | Spring은 동일한 설정의 Context를 캐싱하여 재사용함을 설명 가능. @MockBean/@SpyBean/@DirtiesContext를 사용하면 Context 설정이 달라져 캐시 키가 변경 → 새 Context 생성 → 테스트 전체가 급격히 느려지는 메커니즘을 설명 가능. 대응 전략: ① 테스트용 공통 설정 클래스(Abstract 또는 @Import)를 만들어 @MockBean 정의를 통합 → 모든 테스트가 같은 Context를 공유, ② @MockBean 대신 Mockito.mock()으로 직접 생성 + 수동 주입하여 Context 오염 방지, ③ @DirtiesContext는 최후의 수단으로만 사용. "테스트가 수백 개일 때 빌드 속도를 어떻게 관리하는가?"에 답변 가능. |

---

### Step 12. TestContainers — 실제 DB/Redis/Kafka 통합 테스트

| 학습 항목 | 학습 목표 |
|----------|----------|
| TestContainers란 | Docker 컨테이너를 테스트 시 자동 생성/삭제하여 실제 인프라(DB, Redis, Kafka)로 통합 테스트하는 라이브러리임을 설명 가능. |
| H2 vs TestContainers | H2(인메모리 DB)는 빠르지만 실제 DB와 동작 차이 발생. TestContainers는 실제 DB(Oracle, MySQL, PostgreSQL)를 사용하므로 정확하지만 느림. 트레이드오프를 설명 가능. |
| DB 컨테이너 | @Container + @Testcontainers로 PostgreSQL/MySQL 컨테이너를 띄우고 Spring DataSource를 연결하는 방법을 적용 가능. |
| Redis/Kafka 컨테이너 | GenericContainer로 Redis, KafkaContainer로 Kafka를 테스트에서 사용하는 방법을 알고 있음. |
| 테스트 격리 | 테스트 간 데이터 오염 방지. @Transactional 롤백, @DirtiesContext, 테스트마다 데이터 초기화 전략을 설명 가능. |
| CI/CD 연동 | TestContainers가 CI 환경(GitHub Actions, Jenkins)에서 Docker-in-Docker 또는 Docker Socket 마운트로 동작하는 구조를 알고 있음. |

---

### Step 13. 테스트 전략 설계 — 어디까지 테스트할 것인가

| 학습 항목 | 학습 목표 |
|----------|----------|
| 테스트 커버리지의 의미와 한계 | 라인/브랜치 커버리지의 의미를 설명 가능. 커버리지 100%가 목표가 아닌 이유(커버리지 ≠ 품질, 의미 없는 테스트 양산 위험)를 설명 가능. |
| 어디를 테스트하는가 | 비즈니스 로직(Service) → 단위 테스트 집중, DB 쿼리(Repository) → 통합 테스트, API(Controller) → MockMvc 또는 E2E, 외부 연동 → Mock 또는 TestContainers 전략을 설명 가능. |
| 테스트하지 않아도 되는 것 | 단순 getter/setter, 프레임워크 코드(Spring 내부), 써드파티 라이브러리를 직접 테스트하지 않는 이유를 설명 가능. |
| 테스트 비용-효과 판단 | "이 테스트를 작성하는 데 드는 시간 대비, 이 테스트가 잡아줄 버그의 가치"를 판단하는 사고를 설명 가능. |
| 팀 테스트 전략 수립 | 프로젝트에서 "단위 : 통합 : E2E = 7 : 2 : 1" 같은 비율을 정하고 팀 합의를 도출하는 과정을 설명 가능. |
| Mutation Testing (심화) | 뮤테이션 테스트의 개념(코드 로직을 살짝 변경(예: > → >=, return true → false)했을 때 테스트가 실패하는지 확인)을 설명 가능. 커버리지는 높지만 Assertion이 없거나 약한 테스트("커버만 하고 검증 안 하는 테스트")를 뮤테이션 테스트로 잡아낼 수 있는 이유를 설명 가능. "커버리지는 높은데 왜 버그가 나는가?" → "단순 호출이 아닌 비즈니스 검증(Assertion)의 밀도가 중요하다"는 답변 가능. PIT(pitest.org) 같은 Java 뮤테이션 테스트 도구의 존재를 알고 있음. |

---

### Step 14. 레거시 코드 테스트 — 테스트 없는 코드에 테스트 추가

| 학습 항목 | 학습 목표 |
|----------|----------|
| 레거시 코드의 정의 | Michael Feathers: "테스트가 없는 코드는 모두 레거시 코드"라는 관점을 설명 가능. |
| 특성화 테스트 (Characterization Test) | 기존 동작을 그대로 기록하는 테스트. "현재 이 코드가 이 입력에 이 결과를 반환한다"를 먼저 고정하고, 이후 리팩토링의 안전망으로 활용하는 방법을 설명 가능. |
| 이음새 (Seam) 찾기 | 테스트하기 어려운 코드에서 의존성을 끊을 수 있는 지점(이음새)을 찾아 Mock 주입이 가능하게 만드는 기법을 설명 가능. |
| 점진적 테스트 추가 | 전체를 한 번에 테스트하지 않고, 변경이 필요한 부분부터 테스트를 추가하는 전략. "버그 수정 시 해당 버그를 재현하는 테스트를 먼저 작성 → 수정 → 테스트 통과" 패턴을 적용 가능. |
| ERP 레거시 경험 연결 | 본인의 ERP 코드(테스트 없는 기존 코드)에 테스트를 추가한다면 어떤 전략을 쓸 것인지 설명 가능. |

---

## 3. 자가 검증

### JUnit / Mockito
- [ ] JUnit 5 생명주기(@BeforeEach, @AfterEach 등)와 테스트 격리 원리 설명 가능
- [ ] @ParameterizedTest로 여러 입력 테스트 작성 가능
- [ ] "Stub vs Mock 차이" → 상태 검증 vs 행위 검증으로 설명 가능
- [ ] Mockito when/thenReturn + verify 패턴 자유롭게 사용 가능
- [ ] ArgumentCaptor로 메서드 인자 캡처 + 검증 가능
- [ ] "Mockito로 static 메서드를 Mocking하기 어려운 이유" 설명 가능

### 테스트 원칙
- [ ] "이 코드는 왜 테스트하기 어려운가?" → 구체적 원인(new, static, 전역 상태 등) 식별 가능
- [ ] "테스트하기 쉬운 코드로 리팩토링하는 방법" → DIP, 인터페이스 추출 설명 가능
- [ ] FIRST 원칙 5가지 설명 가능
- [ ] "구현이 아닌 행위를 테스트해야 하는 이유" 설명 가능
- [ ] "Mock이 5개 이상 필요한 테스트가 주는 설계적 경고는?" → SRP 위반, 클래스 분리 필요 설명 가능
- [ ] Given-When-Then 구조로 테스트 작성 가능

### TDD
- [ ] Red → Green → Refactor 사이클을 실제 코드에 적용 가능
- [ ] "TDD로 새 기능 개발" 시연 가능 (테스트 먼저 → 최소 코드 → 리팩토링)
- [ ] "TDD가 적합한 영역과 부적합한 영역" 판단 가능

### Spring 테스트 / 통합 테스트
- [ ] @WebMvcTest vs @DataJpaTest vs @SpringBootTest 선택 기준 설명 가능
- [ ] MockMvc로 API 테스트 작성 가능
- [ ] TestContainers로 실제 DB 통합 테스트 구축 가능
- [ ] "@MockBean이 Context 캐싱을 깨뜨리는 이유" 설명 가능
- [ ] "테스트가 수백 개일 때 빌드 속도를 어떻게 관리하는가?" → Context 통합 전략 설명 가능

### 전략
- [ ] "테스트 커버리지 100%가 목표가 아닌 이유" 설명 가능
- [ ] "단위 : 통합 : E2E 비율을 어떻게 정하는가?" 설명 가능
- [ ] "커버리지는 높은데 왜 버그가 나는가?" → Assertion 밀도 + Mutation Testing 개념으로 설명 가능
- [ ] "레거시 코드에 테스트를 추가하는 전략" → 특성화 테스트 + 이음새 설명 가능

---

## 4. 진행 상태

| Step | 항목 | 상태 |
|------|------|------|
| Step 1 | 테스트 기초 | 미시작 |
| Step 2 | JUnit 5 기본 | 미시작 |
| Step 3 | JUnit 5 심화 | 미시작 |
| Step 4 | 테스트 더블 | 미시작 |
| Step 5 | Mockito 기본 | 미시작 |
| Step 6 | Mockito 심화 | 미시작 |
| Step 7 | 테스트 가능한 설계 | 미시작 |
| Step 8 | 좋은 테스트의 원칙 | 미시작 |
| Step 9 | TDD 사이클 | 미시작 |
| Step 10 | TDD 실전 | 미시작 |
| Step 11 | Spring 테스트 | 미시작 |
| Step 12 | TestContainers | 미시작 |
| Step 13 | 테스트 전략 설계 | 미시작 |
| Step 14 | 레거시 코드 테스트 | 미시작 |

---

## 5. 참고 자료 (보조용)

| 자료 | 용도 |
|------|------|
| Unit Testing (Vladimir Khorikov) | Step 4, 7, 8, 13 보조. 테스트 원칙/전략 |
| TDD By Example (Kent Beck) | Step 9~10 보조. TDD 실전 |
| Working Effectively with Legacy Code (Michael Feathers) | Step 14 보조. 레거시 테스트 |
| Mockito 공식 문서 | Step 5~6 보조. API 레퍼런스 |
| TestContainers 공식 문서 | Step 12 보조. 설정/연동 참고 |

---

> 이 문서는 Claude가 미래 세션에서 읽고 학습을 안내하기 위한 가이드입니다.
> 사용자가 "테스트 공부하자" 또는 "Step N 하자"라고 하면, 진행 상태를 확인하고 다음 미시작 Step부터 학습_템플릿.md 형식으로 진행합니다.
> TDD Step(9~10)은 설명보다 **실습 중심**입니다. Claude가 문제를 제시 → 사용자가 테스트를 먼저 작성 → 코드 구현 → Claude가 리뷰하는 방식으로 진행합니다.
