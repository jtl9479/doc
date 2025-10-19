# 03장: IoC 컨테이너 - Part 2 (핵심 개념)

**[← 이전: Part 1](03-1-IoC-컨테이너-Part1.md)** | **[다음: Part 3 →](03-3-IoC-컨테이너-Part3.md)**

---

## 📖 핵심 개념

### 개념 설명 (3단계 깊이)

#### 1️⃣ 초보자 수준 설명

**초등학생도 이해할 수 있는 쉬운 언어**

```
IoC (Inversion of Control)란?

일반적인 프로그래밍: "내가 직접 다 할게!"
- 장난감이 필요하면 → 직접 만들기
- 친구가 필요하면 → 직접 찾아가기
- 모든 것을 내가 결정하고 실행

IoC 프로그래밍: "필요한 거 말하면 누가 알아서 줄게!"
- 장난감이 필요하면 → "장난감 주세요" → 부모님이 줌
- 친구가 필요하면 → "친구랑 놀래요" → 선생님이 연결해줌
- 필요한 것만 말하면 누군가 알아서 해줌

그 "누군가" = Spring IoC 컨테이너
```

**예시로 이해하기**:
```java
// IoC 없이: 내가 직접 다 만듦
class 어린이 {
    void 놀기() {
        장난감 toy = new 장난감();      // 직접 만들고
        친구 friend = new 친구();       // 직접 찾고
        간식 snack = new 간식();        // 직접 준비
        // 너무 많은 일을 혼자 해야 함!
    }
}

// IoC 사용: 필요한 것만 요청
@Component
class 어린이 {
    @Autowired 장난감 toy;          // 알아서 줌
    @Autowired 친구 friend;         // 알아서 연결
    @Autowired 간식 snack;          // 알아서 준비

    void 놀기() {
        // 놀기만 하면 됨!
    }
}
```

#### 2️⃣ 중급자 수준 설명

**기술적 용어 추가, 동작 원리 설명**

```
IoC (Inversion of Control) = 제어의 역전

전통적 프로그래밍 흐름:
개발자 코드 → 객체 생성 → 의존성 설정 → 메서드 호출
(개발자가 모든 흐름을 제어)

IoC 패턴:
Spring Container → 객체 생성 → 의존성 주입 → 개발자 코드 실행
(제어권이 Spring으로 역전됨)
```

**IoC 컨테이너의 역할**:
1. **Bean 관리**: 객체의 생성, 초기화, 소멸
2. **의존성 주입**: 필요한 객체를 자동으로 연결
3. **생명주기 관리**: 객체의 전체 수명 관리
4. **설정 관리**: 중앙집중식 설정

**핵심 구성 요소**:
```
┌─────────────────────────────────────┐
│      ApplicationContext             │
│    (IoC 컨테이너의 중심)            │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  BeanFactory                 │  │
│  │  (Bean 생성 및 관리)         │  │
│  │                              │  │
│  │  Bean1  Bean2  Bean3  Bean4  │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Configuration Metadata      │  │
│  │  (설정 정보)                 │  │
│  │  - XML                       │  │
│  │  - Annotation (@)            │  │
│  │  - Java Config               │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

**동작 과정**:
```java
// 1. Spring Boot 애플리케이션 시작
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
        // → IoC 컨테이너 생성 및 초기화
    }
}

// 2. Component Scan으로 Bean 탐색
@ComponentScan("com.example")  // 이 패키지 아래 @Component 찾기

// 3. Bean 등록
@Component
class UserService { }  // → IoC 컨테이너에 Bean으로 등록

// 4. 의존성 주입
@Component
class OrderService {
    @Autowired
    UserService userService;  // → IoC 컨테이너가 자동 주입
}
```

#### 3️⃣ 고급자 수준 설명

**내부 구조, 최적화, 고급 패턴**

**ApplicationContext의 계층 구조**:
```
BeanFactory (최상위 인터페이스)
    ↓
ListableBeanFactory
    ↓
HierarchicalBeanFactory
    ↓
ApplicationContext
    ↓
ConfigurableApplicationContext
    ↓
실제 구현체들:
- AnnotationConfigApplicationContext (Java Config)
- GenericWebApplicationContext (Spring Boot)
- XmlWebApplicationContext (XML 기반)
```

**Bean 생성 프로세스 (내부 동작)**:
```java
// 1. Bean Definition 파싱
BeanDefinitionReader reader = new AnnotatedBeanDefinitionReader();
reader.register(MyConfig.class);

// 2. Bean Definition 저장
DefaultListableBeanFactory beanFactory = new DefaultListableBeanFactory();
beanFactory.registerBeanDefinition("myBean", beanDefinition);

// 3. Bean 인스턴스 생성 (Reflection 사용)
Class<?> beanClass = beanDefinition.getBeanClass();
Object bean = beanClass.getDeclaredConstructor().newInstance();

// 4. 의존성 주입 (Dependency Injection)
for (Field field : beanClass.getDeclaredFields()) {
    if (field.isAnnotationPresent(Autowired.class)) {
        Object dependency = beanFactory.getBean(field.getType());
        field.setAccessible(true);
        field.set(bean, dependency);
    }
}

// 5. Bean 후처리 (BeanPostProcessor)
for (BeanPostProcessor processor : beanPostProcessors) {
    bean = processor.postProcessBeforeInitialization(bean, beanName);
}

// 6. 초기화 메서드 실행
if (bean instanceof InitializingBean) {
    ((InitializingBean) bean).afterPropertiesSet();
}

// 7. Bean 등록 완료
beanFactory.registerSingleton(beanName, bean);
```

**Bean 스코프와 생명주기 관리**:
```java
// Singleton Scope (기본값)
@Scope("singleton")  // 컨테이너당 1개 인스턴스
public class SingletonBean {
    // Thread-safe 해야 함
    // 상태를 가지면 안 됨 (Stateless)
}

// Prototype Scope
@Scope("prototype")  // 요청마다 새 인스턴스
public class PrototypeBean {
    // 상태를 가질 수 있음 (Stateful)
    // 생명주기는 클라이언트가 관리
}

// Request Scope (Web)
@Scope("request")  // HTTP 요청마다 1개
public class RequestScopedBean { }

// Session Scope (Web)
@Scope("session")  // HTTP 세션마다 1개
public class SessionScopedBean { }
```

**Bean 생명주기 콜백**:
```java
@Component
public class LifecycleBean {

    // 1. 생성자 주입 (가장 먼저)
    public LifecycleBean(Dependency dep) {
        System.out.println("1. 생성자 실행");
    }

    // 2. 의존성 주입
    @Autowired
    private AnotherDependency another;

    // 3. @PostConstruct (초기화)
    @PostConstruct
    public void init() {
        System.out.println("3. @PostConstruct 실행");
        // 초기화 로직 (DB 연결, 캐시 로드 등)
    }

    // 4. 비즈니스 로직 실행
    public void doSomething() {
        System.out.println("4. 비즈니스 로직 실행");
    }

    // 5. @PreDestroy (소멸)
    @PreDestroy
    public void destroy() {
        System.out.println("5. @PreDestroy 실행");
        // 정리 로직 (연결 종료, 리소스 해제 등)
    }
}
```

**Circular Dependency 해결**:
```java
// 문제: 순환 참조
@Component
class A {
    @Autowired B b;  // A → B
}

@Component
class B {
    @Autowired A a;  // B → A (순환!)
}

// 해결책 1: Constructor Injection + @Lazy
@Component
class A {
    private final B b;

    @Autowired
    public A(@Lazy B b) {  // 지연 로딩
        this.b = b;
    }
}

// 해결책 2: Setter Injection
@Component
class A {
    private B b;

    @Autowired
    public void setB(B b) {
        this.b = b;
    }
}

// 해결책 3: 설계 개선 (권장)
// C를 만들어서 A와 B의 공통 로직 추출
```

**성능 최적화**:
```java
// 1. Lazy Initialization (필요할 때만 생성)
@Lazy
@Component
class HeavyBean {
    // 무거운 초기화 작업
}

// 2. Conditional Bean (조건부 등록)
@Component
@ConditionalOnProperty(name = "feature.enabled", havingValue = "true")
class FeatureBean {
    // feature.enabled=true일 때만 Bean 등록
}

// 3. Profile 분리 (환경별 Bean)
@Component
@Profile("prod")  // 프로덕션 환경에서만
class ProductionBean { }

@Component
@Profile("dev")  // 개발 환경에서만
class DevelopmentBean { }
```

---

### 주요 용어 정리

| 용어 | 영문 | 설명 | 예시 |
|------|------|------|------|
| IoC | Inversion of Control | 제어권이 개발자 → 프레임워크로 역전 | Spring이 객체 생성 관리 |
| DI | Dependency Injection | 의존성을 외부에서 주입 | @Autowired로 자동 주입 |
| Bean | Spring Bean | Spring이 관리하는 객체 | @Component 클래스 |
| Container | IoC Container | Bean을 관리하는 컨테이너 | ApplicationContext |
| Metadata | Configuration Metadata | Bean 설정 정보 | @Configuration, XML |
| Scope | Bean Scope | Bean의 생존 범위 | singleton, prototype |
| Lifecycle | Bean Lifecycle | Bean의 생명주기 | 생성 → 초기화 → 소멸 |
| Callback | Lifecycle Callback | 생명주기 이벤트 처리 | @PostConstruct, @PreDestroy |

---

### 기술 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Spring IoC Container                     │
│                  (ApplicationContext)                       │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │            Configuration Phase (설정)                 │ │
│  │                                                       │ │
│  │  @ComponentScan → 패키지 스캔                         │ │
│  │         ↓                                             │ │
│  │  @Component 발견 → BeanDefinition 생성                │ │
│  │         ↓                                             │ │
│  │  BeanDefinitionRegistry에 등록                        │ │
│  └───────────────────────────────────────────────────────┘ │
│                          ↓                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │         Instantiation Phase (인스턴스 생성)           │ │
│  │                                                       │ │
│  │  Reflection으로 객체 생성                             │ │
│  │         ↓                                             │ │
│  │  생성자 주입 실행                                      │ │
│  │         ↓                                             │ │
│  │  필드/Setter 주입 실행                                │ │
│  └───────────────────────────────────────────────────────┘ │
│                          ↓                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │        Initialization Phase (초기화)                  │ │
│  │                                                       │ │
│  │  BeanPostProcessor.before                             │ │
│  │         ↓                                             │ │
│  │  @PostConstruct 실행                                  │ │
│  │         ↓                                             │ │
│  │  InitializingBean.afterPropertiesSet()                │ │
│  │         ↓                                             │ │
│  │  BeanPostProcessor.after                              │ │
│  └───────────────────────────────────────────────────────┘ │
│                          ↓                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              Ready Phase (사용 가능)                  │ │
│  │                                                       │ │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐             │ │
│  │  │Bean1 │  │Bean2 │  │Bean3 │  │Bean4 │             │ │
│  │  └──────┘  └──────┘  └──────┘  └──────┘             │ │
│  │     ↑         ↑         ↑         ↑                  │ │
│  │     └─────────┴─────────┴─────────┘                  │ │
│  │          Dependency Injection 완료                    │ │
│  └───────────────────────────────────────────────────────┘ │
│                          ↓                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │         Destruction Phase (소멸)                      │ │
│  │                                                       │ │
│  │  컨테이너 종료 시작                                    │ │
│  │         ↓                                             │ │
│  │  @PreDestroy 실행                                     │ │
│  │         ↓                                             │ │
│  │  DisposableBean.destroy()                             │ │
│  │         ↓                                             │ │
│  │  Bean 제거                                            │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

설명:
- Configuration Phase: Bean 정의 수집 및 등록
- Instantiation Phase: 실제 객체 생성 및 의존성 주입
- Initialization Phase: 초기화 콜백 실행
- Ready Phase: 애플리케이션에서 사용 가능
- Destruction Phase: 종료 시 정리 작업
```

**Bean 등록 방법 3가지**:

```
┌──────────────────────────────────────────────────────┐
│              Bean 등록 방법 비교                      │
└──────────────────────────────────────────────────────┘

1️⃣ Component Scanning (자동 등록)
   ┌─────────────────────────────┐
   │ @Component                  │
   │ @Service                    │
   │ @Repository                 │
   │ @Controller                 │
   └─────────────────────────────┘
   장점: 간편, 자동화
   단점: 외부 라이브러리는 불가능

2️⃣ Java Configuration (수동 등록)
   ┌─────────────────────────────┐
   │ @Configuration              │
   │ @Bean                       │
   └─────────────────────────────┘
   장점: 세밀한 제어, 외부 라이브러리 등록 가능
   단점: 수동 작성 필요

3️⃣ XML Configuration (레거시)
   ┌─────────────────────────────┐
   │ <beans>                     │
   │   <bean id="..." />         │
   │ </beans>                    │
   └─────────────────────────────┘
   장점: 코드 변경 없이 설정 변경
   단점: 타입 안정성 부족, 복잡함
```

---

**[← 이전: Part 1](03-1-IoC-컨테이너-Part1.md)** | **[다음: Part 3 →](03-3-IoC-컨테이너-Part3.md)**
