# 학습 05. Spring 내부

## Step 목차

| Step | 항목 | 카테고리 |
|------|------|----------|
| Step 1 | Spring 개요 — 왜 Spring인가, Spring vs Spring Boot | 기초 |
| Step 2 | 프로젝트 구조 — 레이어드 아키텍처, 핵심 어노테이션 | 기초 |
| Step 3 | Spring Boot 기본 — application.yml, 의존성 관리, 실행 원리 | 기초 |
| Step 4 | IoC 컨테이너 — BeanFactory, ApplicationContext, 빈 생명주기 | 핵심 원리 |
| Step 5 | 의존성 주입 — 생성자/필드/세터 주입, @Qualifier, @Primary | 핵심 원리 |
| Step 6 | 빈 스코프 — Singleton, Prototype, Request, Session | 핵심 원리 |
| Step 7 | AOP — 프록시, CGLIB, JDK Dynamic Proxy, self-invocation | 핵심 원리 고급 |
| Step 8 | 빈 후처리기 — BeanPostProcessor, @PostConstruct | 핵심 원리 고급 |
| Step 9 | Spring MVC 내부 — DispatcherServlet, HandlerMapping, 인터셉터 | MVC |
| Step 10 | Spring MVC 활용 — 요청 매핑, 응답 처리, 예외 처리, 검증 | MVC |
| Step 11 | 트랜잭션 원리 — @Transactional 내부 동작, 프록시 기반 | 트랜잭션 |
| Step 12 | 트랜잭션 전파 — REQUIRED, REQUIRES_NEW, NESTED | 트랜잭션 |
| Step 13 | 트랜잭션 실전 — 예외와 롤백, readOnly, 주의사항 | 트랜잭션 |
| Step 14 | Spring DB 접근 — DataSource, 커넥션 풀, 예외 추상화 | DB 접근 |
| Step 15 | Spring Boot 자동 설정 — Auto Configuration, Conditional | Boot |
| Step 16 | Spring Boot Actuator + 프로파일 관리 | Boot |
| Step 17 | Spring Security — Filter Chain, Authentication, Authorization | Security |
| Step 18 | Spring Security 실전 — JWT 인증, OAuth2, CORS, CSRF | Security |
| Step 19 | 이벤트 기반 처리 — ApplicationEventPublisher, @EventListener | 이벤트 |
| Step 20 | Spring WebFlux / Reactive 기초 | Reactive |
| Step 21 | Spring 테스트 — @SpringBootTest, MockMvc, 슬라이스 테스트 | 테스트 |

---

## 1. 개요

**현재 수준**: Spring Boot로 ERP 시스템 개발 중. 어노테이션 기반 사용은 가능하나 내부 동작 원리(프록시, AOP, 트랜잭션 전파 등)는 깊이 부족.
**학습 목표**: Spring의 동작 원리를 "왜 이렇게 동작하는가" 수준으로 설명 가능. 트러블슈팅 시 프레임워크 내부까지 추적 가능. 면접에서 Spring 관련 심화 질문에 즉시 답변 가능.
**분기 배정**: 1분기 120h + 2분기 60h (총 180h)

---

## 2. 학습 순서 + 세부 항목

---

### Step 1. Spring 개요 — 왜 Spring인가, Spring vs Spring Boot

| 학습 항목 | 학습 목표 |
|----------|----------|
| Spring Framework란 | Java 엔터프라이즈 애플리케이션 개발을 위한 프레임워크. 핵심 철학(IoC/DI, AOP, PSA)을 설명 가능. |
| 왜 Spring인가 | Spring 없이 순수 Java로 개발할 때의 문제(강한 결합, 중복 코드, 횡단 관심사 혼재)를 설명 가능. Spring이 이를 어떻게 해결하는지(DI로 결합도 감소, AOP로 횡단 관심사 분리, 추상화로 기술 독립성) 설명 가능. |
| Spring Framework vs Spring Boot | Spring Framework: 설정이 많음(XML/Java Config). Spring Boot: 자동 설정(Auto Configuration) + 내장 서버(Embedded Tomcat) + 스타터 의존성으로 설정 최소화. "Spring Boot는 Spring Framework를 편하게 쓰는 도구"임을 설명 가능. |
| Spring 생태계 | Spring MVC, Spring Data JPA, Spring Security, Spring Batch, Spring Cloud 등 주요 프로젝트의 역할을 개요 수준으로 설명 가능. |

---

### Step 2. 프로젝트 구조 — 레이어드 아키텍처, 핵심 어노테이션

| 학습 항목 | 학습 목표 |
|----------|----------|
| 레이어드 아키텍처 | Controller(표현) → Service(비즈니스) → Repository(데이터 접근) 3계층 구조의 역할과 의존 방향(상위 → 하위만 의존)을 설명 가능. 각 계층의 책임을 명확히 구분 가능. |
| @Controller / @RestController | @Controller(View 반환) vs @RestController(@Controller + @ResponseBody, JSON 반환)의 차이를 설명 가능. |
| @Service | 비즈니스 로직 계층. @Component와 기능상 차이 없지만 역할을 명시하는 이유를 설명 가능. |
| @Repository | 데이터 접근 계층. 스프링 예외 추상화(PersistenceExceptionTranslation) 자동 적용되는 이유를 설명 가능. |
| @Component | 범용 빈 등록. @Controller/@Service/@Repository 모두 @Component를 포함하는 메타 어노테이션임을 설명 가능. |
| @Configuration + @Bean | 수동 빈 등록. 외부 라이브러리 객체를 빈으로 등록할 때 사용하는 이유를 설명 가능. @Configuration의 CGLIB 프록시(싱글턴 보장)를 설명 가능. |
| DTO / Entity 분리 | 계층 간 데이터 전달(DTO)과 DB 매핑(Entity)을 분리해야 하는 이유(API 스펙 변경이 Entity에 영향 주지 않도록)를 설명 가능. |

---

### Step 3. Spring Boot 기본 — application.yml, 의존성 관리, 실행 원리

| 학습 항목 | 학습 목표 |
|----------|----------|
| Spring Initializr | start.spring.io에서 프로젝트 생성 시 선택하는 항목(Build Tool, Language, Dependencies)의 의미를 설명 가능. |
| 빌드 도구 (Gradle/Maven) | build.gradle 또는 pom.xml에서 의존성을 관리하는 방법. 스타터 의존성(spring-boot-starter-web 등)이 내부적으로 어떤 라이브러리를 포함하는지 설명 가능. |
| application.yml / properties | 설정 파일의 역할. server.port, spring.datasource, logging.level 등 기본 설정을 작성 가능. yml vs properties 형식 차이를 설명 가능. |
| @Value / @ConfigurationProperties | 설정 값을 코드에서 읽는 방법. @ConfigurationProperties가 @Value보다 타입 안전하고 묶음 관리에 유리한 이유를 설명 가능. |
| 내장 서버 | Spring Boot가 Tomcat을 내장하여 jar로 실행 가능한 이유를 설명 가능. 외부 Tomcat 배포(war)와의 차이를 설명 가능. |
| Spring Boot 실행 흐름 | main() → SpringApplication.run() → 자동 설정 로딩 → 내장 서버 기동 → 빈 등록 → 애플리케이션 시작 흐름을 설명 가능. |

---

### Step 4. IoC 컨테이너 — BeanFactory, ApplicationContext, 빈 생명주기

| 학습 항목 | 학습 목표 |
|----------|----------|
| IoC (Inversion of Control) 개념 | "제어의 역전"이 무엇인지, 개발자가 아닌 프레임워크가 객체 생명주기를 관리하는 이유(결합도 감소, 테스트 용이)를 설명 가능. |
| BeanFactory vs ApplicationContext | BeanFactory는 빈 생성/관리의 기본 인터페이스, ApplicationContext는 BeanFactory를 상속하며 메시지 소스, 이벤트 발행, AOP 등을 추가 제공하는 확장 인터페이스임을 설명 가능. 실무에서 ApplicationContext를 쓰는 이유를 설명 가능. |
| 빈 등록 방식 | @Component 스캔, @Bean 메서드, XML(레거시) 방식의 차이를 설명 가능. @ComponentScan의 동작 원리(basePackages부터 하위 패키지 탐색)를 설명 가능. |
| 빈 생명주기 | 스프링 컨테이너 생성 → 빈 생성 → 의존관계 주입 → 초기화 콜백(@PostConstruct) → 사용 → 소멸 콜백(@PreDestroy) → 컨테이너 종료 순서를 설명 가능. |
| 빈 생명주기 콜백 | @PostConstruct/@PreDestroy, InitializingBean/DisposableBean, @Bean(initMethod/destroyMethod) 3가지 방법의 차이와 권장 순서(@PostConstruct 우선)를 설명 가능. |

---

### Step 5. 의존성 주입 — 생성자/필드/세터 주입, @Qualifier, @Primary

| 학습 항목 | 학습 목표 |
|----------|----------|
| 의존성 주입(DI) 개념 | 객체가 직접 의존 객체를 생성하지 않고 외부에서 주입받는 패턴. DI가 없으면(new로 직접 생성) 왜 결합도가 높아지는지 코드로 설명 가능. |
| 생성자 주입 (권장) | 불변성 보장(final 필드), 필수 의존성 누락 시 컴파일 오류, 테스트 용이(Mock 주입). 생성자가 1개면 @Autowired 생략 가능한 이유를 설명 가능. |
| 필드 주입의 문제점 | 테스트 시 Mock 주입 어려움, 불변성 보장 불가, 순환 참조 감지 어려움. 실무에서 쓰지 않는 이유를 설명 가능. |
| 세터 주입 | 선택적 의존성에 사용. 생성자 주입과의 차이를 설명 가능. |
| @Qualifier, @Primary | 같은 타입의 빈이 여러 개일 때 선택 방법. @Primary(기본값)와 @Qualifier(명시적 지정)의 우선순위를 설명 가능. |
| 순환 참조 (Circular Dependency) | A → B → A 의존 시 발생. Spring Boot 2.6+에서 기본 차단됨. 해결 방법(@Lazy, 설계 변경)과 근본 원인(설계 문제)을 설명 가능. |

---

### Step 6. 빈 스코프 — Singleton, Prototype, Request, Session

| 학습 항목 | 학습 목표 |
|----------|----------|
| Singleton (기본) | 스프링 컨테이너당 빈 인스턴스 1개. 상태를 가지면 안 되는 이유(동시성 문제)를 설명 가능. |
| Prototype | 요청할 때마다 새 인스턴스 생성. Singleton 빈이 Prototype 빈을 주입받으면 매번 같은 인스턴스가 주입되는 문제를 설명 가능. Provider/ObjectFactory로 해결하는 방법을 설명 가능. |
| Request / Session | 웹 요청/세션 단위 스코프. 프록시 모드(proxyMode = ScopedProxyMode.TARGET_CLASS)가 필요한 이유를 설명 가능. |
| Singleton 빈의 상태 주의 | Singleton 빈에 인스턴스 변수(상태)를 두면 멀티스레드 환경에서 race condition이 발생하는 이유를 설명 가능. ThreadLocal 또는 무상태 설계로 해결하는 방법을 설명 가능. |

---

### Step 7. AOP — 프록시, CGLIB, JDK Dynamic Proxy, self-invocation

| 학습 항목 | 학습 목표 |
|----------|----------|
| AOP 개념 | 횡단 관심사(Cross-Cutting Concerns: 로깅, 트랜잭션, 보안)를 비즈니스 로직에서 분리하는 이유를 설명 가능. |
| AOP 용어 | Aspect, Advice(Before/After/Around/AfterReturning/AfterThrowing), Pointcut, JoinPoint, Weaving 각각의 의미를 설명 가능. |
| 프록시 기반 AOP | Spring AOP는 프록시 패턴으로 구현됨을 설명 가능. 클라이언트 → 프록시 → 실제 객체 호출 흐름을 그림으로 그릴 수 있음. |
| JDK Dynamic Proxy vs CGLIB | JDK: 인터페이스 기반, Reflection. CGLIB: 클래스 상속 기반, 바이트코드 조작. Spring Boot는 기본 CGLIB 사용. 각각의 장단점과 선택 기준을 설명 가능. |
| self-invocation 문제 | 같은 클래스 내에서 this.method()로 호출하면 프록시를 거치지 않아 AOP가 적용 안 되는 이유를 설명 가능. 해결 방법(별도 빈 분리, AopContext.currentProxy(), @Lazy self 주입)을 설명 가능. |
| @Aspect 실전 | 커스텀 어노테이션 + AOP로 로깅/시간 측정/권한 체크를 구현하는 패턴을 적용 가능. |
| AOP와 순환 참조 | AOP 프록시가 적용된 빈에서 순환 참조가 발생하면, 프록시 생성 시점(BeanPostProcessor)과 의존성 주입 시점이 꼬여서 에러가 나는 메커니즘을 설명 가능. Spring Boot 2.6+에서 순환 참조가 기본 차단된 이유(프록시 + 순환 = 예측 불가능한 빈 상태)를 설명 가능. "AOP 적용 후 갑자기 순환 참조 에러가 났다면 내부에서 무슨 일이 벌어진 건가?"에 답변 가능. |

---

### Step 8. 빈 후처리기 — BeanPostProcessor, @PostConstruct

| 학습 항목 | 학습 목표 |
|----------|----------|
| BeanPostProcessor | 빈 생성 후 초기화 전/후에 가공하는 메커니즘. postProcessBeforeInitialization/postProcessAfterInitialization 호출 시점을 설명 가능. |
| 프록시 생성 시점 | Spring AOP의 프록시가 BeanPostProcessor(AnnotationAwareAspectJAutoProxyCreator)에 의해 생성되는 과정을 설명 가능. "빈이 등록될 때 프록시로 교체된다"는 핵심을 이해. |
| @PostConstruct 동작 원리 | CommonAnnotationBeanPostProcessor가 @PostConstruct를 처리하는 과정을 설명 가능. 빈 생명주기에서의 위치를 정확히 설명 가능. |

---

### Step 9. Spring MVC 내부 — DispatcherServlet, HandlerMapping, 인터셉터

| 학습 항목 | 학습 목표 |
|----------|----------|
| DispatcherServlet | 모든 HTTP 요청의 진입점(Front Controller 패턴). 요청 → DispatcherServlet → HandlerMapping → HandlerAdapter → Controller → ViewResolver → View 전체 흐름을 그림으로 그릴 수 있음. |
| HandlerMapping | 요청 URL을 어떤 Controller 메서드에 매핑하는지 결정. RequestMappingHandlerMapping(@RequestMapping 기반)의 동작을 설명 가능. |
| HandlerAdapter | Controller 메서드를 실제 실행하는 역할. 다양한 Controller 형태(어노테이션 기반, HttpRequestHandler 등)를 통일적으로 처리하는 이유를 설명 가능. |
| ViewResolver | Controller가 반환한 뷰 이름을 실제 뷰로 변환. REST API에서는 @ResponseBody로 ViewResolver를 건너뛰는 이유를 설명 가능. |
| HandlerInterceptor | preHandle/postHandle/afterCompletion 각각의 호출 시점과 활용(인증 체크, 로깅, 시간 측정)을 설명 가능. Filter와의 차이(Filter는 서블릿 레벨, Interceptor는 Spring MVC 레벨)를 설명 가능. |
| ArgumentResolver | @RequestParam, @PathVariable, @RequestBody 등 파라미터를 자동 바인딩하는 메커니즘. HandlerMethodArgumentResolver의 역할을 설명 가능. 커스텀 ArgumentResolver를 구현하는 시나리오를 설명 가능. |

---

### Step 10. Spring MVC 활용 — 요청 매핑, 응답 처리, 예외 처리, 검증

| 학습 항목 | 학습 목표 |
|----------|----------|
| HTTP 메서드 매핑 | @GetMapping, @PostMapping, @PutMapping, @DeleteMapping, @PatchMapping 각각의 용도와 REST API 설계 원칙과의 관계를 설명 가능. |
| 요청 파라미터 | @RequestParam, @PathVariable, @ModelAttribute, @RequestBody의 차이와 사용 시점을 설명 가능. |
| HttpMessageConverter | @RequestBody → JSON을 객체로, @ResponseBody → 객체를 JSON으로 변환하는 메커니즘. Jackson ObjectMapper가 내부에서 사용됨을 설명 가능. |
| 예외 처리 | @ExceptionHandler, @ControllerAdvice, @RestControllerAdvice로 전역 예외 처리하는 패턴을 적용 가능. 예외 계층 설계(비즈니스 예외 vs 시스템 예외)를 설명 가능. |
| Bean Validation | @Valid, @NotNull, @Size, @Pattern + BindingResult로 요청 검증하는 방법. 검증 실패 시 적절한 에러 응답 설계를 적용 가능. |
| REST API 설계 원칙 | URI는 명사(리소스) 중심(/orders, /orders/{id}), HTTP 메서드로 행위 표현(GET=조회, POST=생성, PUT=전체수정, PATCH=부분수정, DELETE=삭제)하는 원칙을 설명 가능. HTTP 상태 코드 사용 기준(200 OK, 201 Created, 204 No Content, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 409 Conflict, 500 Internal Server Error)을 설명 가능. 응답 포맷 표준화(공통 응답 래퍼, 에러 응답 구조)를 설계 가능. |

---

### Step 11. 트랜잭션 원리 — @Transactional 내부 동작, 프록시 기반

| 학습 항목 | 학습 목표 |
|----------|----------|
| @Transactional 내부 동작 | 프록시가 메서드 호출을 가로채서 트랜잭션 시작 → 비즈니스 로직 실행 → 성공 시 커밋 / 예외 시 롤백하는 전체 흐름을 설명 가능. |
| 프록시 기반의 의미 | @Transactional이 프록시로 동작하기 때문에 self-invocation(같은 클래스 내부 호출)에서 트랜잭션이 안 걸리는 이유를 설명 가능. (Step 4 AOP와 동일 원리) |
| PlatformTransactionManager | 트랜잭션 관리의 추상화. DataSourceTransactionManager(JDBC), JpaTransactionManager(JPA) 등 구현체에 따라 DB별 트랜잭션을 통합 관리하는 구조를 설명 가능. |
| 트랜잭션 동기화 | 같은 트랜잭션 내에서 같은 커넥션을 사용하는 메커니즘(TransactionSynchronizationManager → ThreadLocal에 커넥션 보관)을 설명 가능. |

---

### Step 12. 트랜잭션 전파 — REQUIRED, REQUIRES_NEW, NESTED

| 학습 항목 | 학습 목표 |
|----------|----------|
| REQUIRED (기본) | 진행 중인 트랜잭션이 있으면 참여, 없으면 새로 생성. 대부분의 상황에서 적합한 이유를 설명 가능. 내부 메서드에서 예외 발생 시 전체 롤백되는 이유를 설명 가능. |
| REQUIRES_NEW | 항상 새 트랜잭션 생성. 기존 트랜잭션은 일시 중단. "감사 로그는 메인 트랜잭션 롤백과 무관하게 저장해야 한다"는 실무 시나리오에서 사용하는 이유를 설명 가능. |
| REQUIRES_NEW 커넥션 풀 고갈 (심화) | REQUIRES_NEW는 새 커넥션을 점유하므로, 1개 HTTP 요청이 2개+ 커넥션을 동시 사용하게 됨을 설명 가능. maximumPoolSize=10인 상태에서 동시 요청 10개가 각각 REQUIRES_NEW를 호출하면 → 10개 커넥션이 부모 트랜잭션에 점유 + 자식 트랜잭션이 새 커넥션을 요청하지만 풀이 비어있어 대기 → **전체 데드락** 발생하는 시나리오를 설명 가능. 대응(풀 크기 여유 확보, REQUIRES_NEW 남용 금지, NESTED로 대체 검토)을 설명 가능. |
| NESTED | 부모 트랜잭션 내에 세이브포인트(Savepoint) 생성. 자식 롤백 시 세이브포인트까지만 롤백되고 부모는 유지. REQUIRES_NEW와의 차이(NESTED는 같은 커넥션, REQUIRES_NEW는 별도 커넥션)를 설명 가능. |
| SUPPORTS / NOT_SUPPORTED / MANDATORY / NEVER | 각 전파 옵션의 의미를 설명 가능. 실무에서 드물게 사용됨을 알고 있음. |
| 전파 옵션 선택 실전 | "이 비즈니스 로직에서 어떤 전파 옵션을 쓸 것인가?"를 트랜잭션 경계 + 롤백 범위 + 커넥션 사용량을 고려하여 판단 가능. |

---

### Step 13. 트랜잭션 실전 — 예외와 롤백, readOnly, 주의사항

| 학습 항목 | 학습 목표 |
|----------|----------|
| 예외와 롤백 규칙 | 기본: RuntimeException(Unchecked) → 롤백, CheckedException → 커밋. 이 규칙이 직관적이지 않은 이유와, rollbackFor/noRollbackFor로 커스터마이징하는 방법을 설명 가능. |
| readOnly = true | 읽기 전용 트랜잭션의 의미. JPA에서 더티 체킹 스킵으로 성능 향상, DB에서 읽기 전용 힌트로 최적화 가능. "조회 메서드에 readOnly=true 붙여야 하는가?"에 근거 있게 답변 가능. |
| @Transactional 위치 | 클래스 레벨 vs 메서드 레벨. 인터페이스에 붙이면 안 되는 이유(CGLIB 프록시에서 인터페이스 어노테이션을 못 읽는 경우)를 설명 가능. |
| 트랜잭션 로그 확인 | `logging.level.org.springframework.transaction.interceptor=TRACE` 설정으로 트랜잭션 시작/커밋/롤백을 확인하는 방법을 알고 있음. |
| 실무 주의사항 | 긴 트랜잭션의 위험(커넥션 장기 점유, 락 경합), @Transactional + 외부 API 호출(API 실패 시 이미 DB 변경 완료) 문제를 설명 가능. |

---

### Step 14. Spring DB 접근 — DataSource, 커넥션 풀, 예외 추상화

| 학습 항목 | 학습 목표 |
|----------|----------|
| DataSource | DB 커넥션을 제공하는 표준 인터페이스. DriverManager(매번 새 커넥션) vs DataSource(풀 기반 재사용)의 차이를 설명 가능. |
| 커넥션 풀 연동 | Spring Boot에서 HikariCP가 기본인 이유(성능). application.yml 설정 방법. (학습_02 Step 12와 연계) |
| 스프링 예외 추상화 | DB별 예외(ORA-00001, MySQL 1062)를 스프링 공통 예외(DataAccessException 계층)로 변환하는 이유(DB 벤더 독립성)를 설명 가능. SQLExceptionTranslator의 역할을 설명 가능. |
| JdbcTemplate | 순수 JDBC의 반복 코드(커넥션 획득 → SQL 실행 → ResultSet 매핑 → 자원 반환)를 줄여주는 템플릿 패턴. JPA 이전 또는 JPA로 해결 안 되는 경우 사용 이유를 설명 가능. |

---

### Step 15. Spring Boot 자동 설정 — Auto Configuration, Conditional

| 학습 항목 | 학습 목표 |
|----------|----------|
| Spring Boot의 핵심 가치 | "설정보다 관례(Convention over Configuration)". 자동 설정 덕분에 설정 파일 최소화로 애플리케이션을 기동할 수 있는 이유를 설명 가능. |
| @SpringBootApplication 분해 | @SpringBootConfiguration + @EnableAutoConfiguration + @ComponentScan 3개의 역할을 각각 설명 가능. |
| Auto Configuration 동작 | META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports 파일에 등록된 설정 클래스를 조건에 따라 자동 로딩하는 과정을 설명 가능. |
| @Conditional 어노테이션 | @ConditionalOnClass(클래스 존재 시), @ConditionalOnMissingBean(빈 없을 시), @ConditionalOnProperty(설정 값 존재 시) 등 조건부 빈 등록의 동작을 설명 가능. |
| 자동 설정 디버깅 | `--debug` 옵션 또는 `spring.autoconfigure.exclude`로 어떤 자동 설정이 적용/제외되었는지 확인하는 방법을 알고 있음. |
| 자동 설정 exclude 실무 | 자동 설정이 오히려 방해되는 사례(예: SecurityAutoConfiguration이 불필요한 인증을 강제, DataSourceAutoConfiguration이 테스트 시 불필요한 DB 연결 시도)를 설명 가능. @SpringBootApplication(exclude = ...) 또는 application.yml의 spring.autoconfigure.exclude로 제외하는 방법을 적용 가능. "자동 설정을 무조건 믿지 말고 프로젝트에 맞게 제어할 수 있어야 한다"는 원칙을 설명 가능. |
| Custom Starter 개념 | 팀/회사 공통 설정(로깅, 모니터링, 예외 처리 등)을 spring-boot-starter-xxx로 패키징하여 표준을 배포하는 패턴을 개념 수준 설명 가능. autoconfigure 모듈 + starter 모듈 2개로 구성되는 구조를 설명 가능. |

---

### Step 16. Spring Boot Actuator + 프로파일 관리

| 학습 항목 | 학습 목표 |
|----------|----------|
| Actuator 개요 | /actuator/health, /actuator/info, /actuator/metrics 등 운영 모니터링 엔드포인트의 역할을 설명 가능. |
| 주요 엔드포인트 | health(헬스 체크), metrics(메트릭), beans(빈 목록), env(환경 변수), loggers(로그 레벨 동적 변경)를 설명 가능. |
| Micrometer 연동 | Actuator + Micrometer로 Prometheus/Grafana에 메트릭을 노출하는 구조를 설명 가능. (학습_07 관찰성과 연계) |
| 프로파일 (Profile) | application-dev.yml, application-prod.yml로 환경별 설정 분리하는 방법. @Profile로 환경별 빈 등록하는 방법을 적용 가능. |
| 외부 설정 우선순위 | 커맨드라인 > 환경 변수 > application.yml > 기본값 우선순위를 설명 가능. |

---

### Step 17. Spring Security — Filter Chain, Authentication, Authorization

| 학습 항목 | 학습 목표 |
|----------|----------|
| Spring Security 아키텍처 | DelegatingFilterProxy → FilterChainProxy → SecurityFilterChain → 각 필터 순서로 요청이 처리되는 전체 흐름을 그림으로 그릴 수 있음. |
| 핵심 필터 | UsernamePasswordAuthenticationFilter(폼 로그인), BasicAuthenticationFilter(HTTP Basic), SecurityContextPersistenceFilter(SecurityContext 유지), ExceptionTranslationFilter(인증/인가 예외 처리), FilterSecurityInterceptor(인가 결정) 각각의 역할을 설명 가능. |
| Authentication (인증) | AuthenticationManager → AuthenticationProvider → UserDetailsService → PasswordEncoder 인증 처리 흐름을 설명 가능. |
| Authorization (인가) | URL 기반(@RequestMapping + SecurityFilterChain), 메서드 기반(@PreAuthorize, @Secured)의 차이를 설명 가능. 역할(ROLE) vs 권한(AUTHORITY) 차이를 설명 가능. |
| SecurityContext | SecurityContextHolder → SecurityContext → Authentication 구조. ThreadLocal 기반으로 현재 사용자 정보를 저장하는 원리를 설명 가능. |

---

### Step 18. Spring Security 실전 — JWT 인증, OAuth2, CORS, CSRF

| 학습 항목 | 학습 목표 |
|----------|----------|
| JWT 인증 구현 | 로그인 → JWT 발급 → 요청마다 Authorization 헤더에 JWT 포함 → 필터에서 검증 + SecurityContext 설정 흐름을 구현 가능. Access Token / Refresh Token 전략을 설명 가능. |
| OAuth2 개념 | Authorization Code Grant 흐름(클라이언트 → 인증 서버 → 리소스 서버)을 설명 가능. Spring Security OAuth2 Client/Resource Server의 역할을 설명 가능. |
| CORS (Cross-Origin Resource Sharing) | 브라우저의 동일 출처 정책(Same-Origin Policy)이 뭔지, Preflight 요청(OPTIONS)이 왜 발생하는지, @CrossOrigin 또는 CorsConfigurationSource로 설정하는 방법을 설명 가능. |
| CSRF (Cross-Site Request Forgery) | CSRF 공격 원리(사용자의 인증된 세션을 악용)를 설명 가능. 세션 기반에서는 CSRF 토큰이 필요하지만, JWT(Stateless)에서는 CSRF를 비활성화하는 이유를 설명 가능. |

---

### Step 19. 이벤트 기반 처리 — ApplicationEventPublisher, @EventListener

| 학습 항목 | 학습 목표 |
|----------|----------|
| 스프링 이벤트 개념 | 이벤트 발행(publish) → 이벤트 리스너(listen) 패턴으로 컴포넌트 간 결합도를 낮추는 이유를 설명 가능. |
| ApplicationEventPublisher | 이벤트 발행 방법. 커스텀 이벤트 클래스 생성 + publishEvent() 호출 패턴을 적용 가능. |
| @EventListener | 이벤트 수신 방법. 동기 처리(기본)와 @Async 비동기 처리의 차이를 설명 가능. |
| @TransactionalEventListener | 트랜잭션 커밋 후에 이벤트를 처리하는 패턴. phase(AFTER_COMMIT, AFTER_ROLLBACK)의 의미를 설명 가능. "주문 완료 후 알림 발송"에 AFTER_COMMIT이 적합한 이유를 설명 가능. |
| 이벤트 활용 실전 | 도메인 이벤트(DDD)와의 관계. 서비스 간 결합도를 낮추는 패턴(예: OrderService → 이벤트 발행 → InventoryListener, NotificationListener)을 설명 가능. |

---

### Step 20. Spring WebFlux / Reactive 기초

| 학습 항목 | 학습 목표 |
|----------|----------|
| Reactive 프로그래밍 개념 | 논블로킹 I/O + 이벤트 루프 기반. 적은 스레드로 많은 요청을 처리하는 원리를 설명 가능. |
| Spring MVC vs WebFlux | MVC: 요청당 스레드(블로킹), WebFlux: 이벤트 루프(논블로킹)의 차이를 설명 가능. "언제 WebFlux를 선택하는가?"(I/O Heavy + 높은 동시성)를 판단 가능. |
| Mono / Flux | Mono(0~1개 결과), Flux(0~N개 결과)의 차이를 설명 가능. 간단한 WebFlux 엔드포인트 코드를 읽을 수 있음. |
| WebFlux를 쓰면 안 되는 경우 | JDBC(블로킹 드라이버) 사용 시 WebFlux의 이점이 사라지는 이유를 설명 가능. R2DBC(리액티브 DB 드라이버)의 존재를 알고 있음. |

---

### Step 21. Spring 테스트 — @SpringBootTest, MockMvc, 슬라이스 테스트

| 학습 항목 | 학습 목표 |
|----------|----------|
| @SpringBootTest | 전체 컨텍스트를 로딩하는 통합 테스트. 느리지만 실제 환경에 가까운 테스트. webEnvironment 옵션(MOCK, RANDOM_PORT)을 설명 가능. |
| MockMvc | 서블릿 컨테이너 없이 MVC 테스트. perform().andExpect() 패턴으로 요청/응답 검증 가능. |
| 슬라이스 테스트 | @WebMvcTest(컨트롤러만), @DataJpaTest(JPA만), @WebFluxTest(WebFlux만) 등 필요한 계층만 로딩하여 빠른 테스트. 각각의 용도와 차이를 설명 가능. |
| @MockBean / @SpyBean | 특정 빈을 Mock/Spy로 교체하여 테스트하는 방법. @MockBean이 ApplicationContext를 재생성하는 단점(테스트 속도 저하)을 설명 가능. |
| TestContainers 연동 | 실제 DB/Redis를 Docker 컨테이너로 띄워 통합 테스트하는 방법. (학습_05 테스트와 연계) |

---

## 3. 자가 검증

### 기초
- [ ] "Spring Framework vs Spring Boot 차이" 설명 가능
- [ ] "레이어드 아키텍처(Controller → Service → Repository)의 역할과 의존 방향" 설명 가능
- [ ] "@Component vs @Configuration + @Bean 차이" 설명 가능
- [ ] "Spring Boot 실행 흐름(main → run → 자동 설정 → 서버 기동)" 설명 가능

### IoC / DI
- [ ] "IoC란 무엇이고 왜 필요한가?" 2분 설명 가능
- [ ] "생성자 주입을 권장하는 이유 3가지" 즉시 답변 가능
- [ ] "Singleton 빈에 상태를 두면 왜 위험한가?" 설명 가능
- [ ] 빈 생명주기 순서를 처음부터 끝까지 설명 가능

### AOP
- [ ] "AOP가 프록시 기반이라는 것이 무슨 의미인가?" 그림 포함 설명 가능
- [ ] "CGLIB vs JDK Dynamic Proxy 차이" 설명 가능
- [ ] "self-invocation에서 AOP가 안 먹히는 이유 + 해결법" 설명 가능
- [ ] "AOP 적용 후 순환 참조 에러가 발생한 원인" → 프록시 생성 시점 + 의존성 주입 시점 충돌로 설명 가능

### MVC
- [ ] DispatcherServlet → Controller → View 전체 흐름을 그림으로 그릴 수 있음
- [ ] "Filter vs Interceptor 차이" 설명 가능
- [ ] "@ExceptionHandler와 @ControllerAdvice의 관계" 설명 가능
- [ ] "RESTful API 설계 원칙" → URI 설계 + HTTP 메서드 + 상태 코드 기준 설명 가능

### 트랜잭션
- [ ] "@Transactional이 내부적으로 어떻게 동작하는지" 5분 설명 가능
- [ ] "REQUIRED vs REQUIRES_NEW vs NESTED 차이" 실제 시나리오로 설명 가능
- [ ] "REQUIRES_NEW를 남용하면 커넥션 풀 데드락이 발생하는 시나리오" 설명 가능
- [ ] "CheckedException은 왜 기본 롤백이 안 되는가?" 설명 가능
- [ ] "readOnly=true의 효과" 설명 가능

### Security
- [ ] Spring Security Filter Chain 동작 순서를 그림으로 그릴 수 있음
- [ ] "JWT 인증 흐름" 전체 설명 가능
- [ ] "CSRF를 JWT에서는 꺼도 되는 이유" 설명 가능

### Boot / 기타
- [ ] "@SpringBootApplication을 분해하면?" 3개 어노테이션 설명 가능
- [ ] "Auto Configuration 동작 원리" 설명 가능
- [ ] "자동 설정을 exclude해야 하는 실무 사례" 설명 가능
- [ ] "Custom Starter란 무엇이고 왜 만드는가" 설명 가능
- [ ] "@TransactionalEventListener를 쓰는 이유" 설명 가능
- [ ] "Spring MVC vs WebFlux 선택 기준" 설명 가능
- [ ] "스프링 예외 추상화(DataAccessException)의 목적" 설명 가능
- [ ] "@WebMvcTest vs @SpringBootTest 차이와 선택 기준" 설명 가능

---

## 4. 진행 상태

| Step | 항목 | 상태 |
|------|------|------|
| Step 1 | Spring 개요 | 미시작 |
| Step 2 | 프로젝트 구조 + 핵심 어노테이션 | 미시작 |
| Step 3 | Spring Boot 기본 | 미시작 |
| Step 4 | IoC 컨테이너 | 미시작 |
| Step 5 | 의존성 주입 | 미시작 |
| Step 6 | 빈 스코프 | 미시작 |
| Step 7 | AOP | 미시작 |
| Step 8 | 빈 후처리기 | 미시작 |
| Step 9 | Spring MVC 내부 | 미시작 |
| Step 10 | Spring MVC 활용 | 미시작 |
| Step 11 | 트랜잭션 원리 | 미시작 |
| Step 12 | 트랜잭션 전파 | 미시작 |
| Step 13 | 트랜잭션 실전 | 미시작 |
| Step 14 | Spring DB 접근 | 미시작 |
| Step 15 | Spring Boot 자동 설정 | 미시작 |
| Step 16 | Actuator + 프로파일 | 미시작 |
| Step 17 | Security 기초 | 미시작 |
| Step 18 | Security 실전 | 미시작 |
| Step 19 | 이벤트 기반 처리 | 미시작 |
| Step 20 | WebFlux / Reactive | 미시작 |
| Step 21 | Spring 테스트 | 미시작 |

---

## 5. 참고 자료 (보조용)

| 자료 | 용도 |
|------|------|
| 김영한 스프링 핵심 원리 (기본+고급) | Step 1~8 보조 |
| 김영한 스프링 MVC 1, 2편 | Step 9~10 보조 |
| 김영한 스프링 DB 1, 2편 | Step 11~14 보조 |
| 김영한 JPA 기본편 + 활용편 | 학습_02 JPA와 연계 |
| Spring 공식 Reference | 전 Step 필요 시 발췌 |
| Spring Security 공식 문서 | Step 14~15 보조 |

---

> 이 문서는 Claude가 미래 세션에서 읽고 학습을 안내하기 위한 가이드입니다.
> 사용자가 "Spring 공부하자" 또는 "Step N 하자"라고 하면, 진행 상태를 확인하고 다음 미시작 Step부터 학습_템플릿.md 형식으로 진행합니다.
