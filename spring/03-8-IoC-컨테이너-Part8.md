# 03장: IoC 컨테이너 - Part 8 (면접 질문 & 핵심 정리)

**[← 이전: Part 7](03-7-IoC-컨테이너-Part7.md)** | **[다음: 04장 DI →](../04-DI.md)**

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용 (7개)

<details>
<summary><strong>1. Spring IoC 컨테이너가 무엇인지 설명해주세요</strong></summary>

**모범 답안 포인트**
- IoC = Inversion of Control (제어의 역전)
- 객체 생성과 생명주기를 개발자가 아닌 Spring이 관리
- ApplicationContext가 IoC 컨테이너의 대표적 구현체

**예시 답변**
> "Spring IoC 컨테이너는 객체의 생성, 초기화, 소멸 등 생명주기를 관리하는 컨테이너입니다. 개발자가 직접 new 키워드로 객체를 생성하는 대신, Spring이 설정 정보를 바탕으로 자동으로 객체를 생성하고 의존성을 주입합니다. 이를 통해 결합도를 낮추고 테스트 용이성을 높일 수 있습니다."

**꼬리 질문**
- Q: IoC의 장점은 무엇인가요?
- A: 결합도 감소, 테스트 용이성, 코드 재사용성 향상, 설정의 중앙 집중화

**실무 연관**
- @Service, @Repository 어노테이션을 붙이면 Spring이 자동으로 Bean으로 관리
- ApplicationContext.getBean()으로 필요한 Bean을 가져올 수 있음

</details>

<details>
<summary><strong>2. Bean이란 무엇이며, 어떻게 등록하나요?</strong></summary>

**모범 답안 포인트**
- Bean = Spring IoC 컨테이너가 관리하는 객체
- 등록 방법: @Component, @Service, @Repository, @Controller
- @Configuration + @Bean으로도 등록 가능

**예시 답변**
> "Bean은 Spring IoC 컨테이너가 생성하고 관리하는 객체를 의미합니다. Bean을 등록하는 방법은 크게 두 가지입니다. 첫째, 클래스에 @Component나 @Service 같은 어노테이션을 붙여서 Component Scan으로 자동 등록하는 방법이 있습니다. 둘째, @Configuration 클래스 내에서 @Bean 어노테이션을 사용한 메서드로 수동 등록할 수 있습니다."

**꼬리 질문**
- Q: @Component와 @Bean의 차이는?
- A: @Component는 클래스 레벨에서 사용하고, @Bean은 메서드 레벨에서 사용. @Bean은 외부 라이브러리도 등록 가능

</details>

<details>
<summary><strong>3. @Autowired는 어떻게 동작하나요?</strong></summary>

**모범 답안 포인트**
- 의존성 자동 주입 어노테이션
- 타입(Type) 기반으로 매칭
- 생성자, Setter, 필드 주입 모두 가능

**예시 답변**
> "@Autowired는 Spring이 자동으로 의존성을 주입하도록 하는 어노테이션입니다. IoC 컨테이너에서 해당 타입의 Bean을 찾아서 자동으로 주입해줍니다. 생성자, Setter 메서드, 필드에 모두 사용할 수 있지만, 불변성과 테스트 용이성을 위해 생성자 주입이 권장됩니다."

**꼬리 질문**
- Q: 같은 타입의 Bean이 2개 이상이면 어떻게 되나요?
- A: NoUniqueBeanDefinitionException 발생. @Qualifier나 @Primary로 해결

</details>

<details>
<summary><strong>4. 생성자 주입을 권장하는 이유는 무엇인가요?</strong></summary>

**모범 답안 포인트**
- 불변성 보장 (final 키워드)
- 순환 참조 조기 발견
- 테스트 용이성

**예시 답변**
> "생성자 주입을 권장하는 이유는 세 가지입니다. 첫째, final 키워드로 불변성을 보장할 수 있습니다. 둘째, 순환 참조가 있으면 애플리케이션 시작 시점에 에러가 발생하여 조기 발견이 가능합니다. 셋째, 테스트 시 new 키워드로 직접 객체를 생성할 수 있어 Spring 컨테이너 없이도 테스트할 수 있습니다."

**꼬리 질문**
- Q: 필드 주입의 단점은?
- A: final 사용 불가, 테스트 어려움, 순환 참조 늦게 발견

</details>

<details>
<summary><strong>5. Component Scan은 어떻게 동작하나요?</strong></summary>

**모범 답안 포인트**
- @ComponentScan이 지정한 패키지를 스캔
- @Component, @Service 등이 붙은 클래스를 Bean으로 등록
- Spring Boot는 @SpringBootApplication에 포함됨

**예시 답변**
> "Component Scan은 @ComponentScan 어노테이션이 지정한 패키지와 하위 패키지를 재귀적으로 탐색하여, @Component, @Service, @Repository, @Controller 어노테이션이 붙은 클래스를 찾아 자동으로 Bean으로 등록하는 기능입니다. Spring Boot의 @SpringBootApplication에는 @ComponentScan이 포함되어 있어서, 메인 클래스가 있는 패키지부터 자동으로 스캔합니다."

**꼬리 질문**
- Q: 스캔 범위를 제한하는 이유는?
- A: 성능 최적화. 불필요한 패키지를 스캔하면 애플리케이션 시작이 느려짐

</details>

<details>
<summary><strong>6. Bean의 기본 스코프는 무엇인가요?</strong></summary>

**모범 답안 포인트**
- 기본 스코프는 Singleton
- 애플리케이션 전체에서 인스턴스 1개만 존재
- 상태를 가지면 안 됨 (Stateless)

**예시 답변**
> "Bean의 기본 스코프는 Singleton입니다. 이는 IoC 컨테이너에서 Bean당 하나의 인스턴스만 생성하고, 모든 요청에 대해 같은 인스턴스를 재사용한다는 의미입니다. 따라서 Singleton Bean은 상태를 가지면 안 되며, Stateless하게 설계해야 합니다. 만약 상태가 필요하다면 Prototype 스코프를 사용해야 합니다."

**꼬리 질문**
- Q: Prototype 스코프는 언제 사용하나요?
- A: 각 요청마다 독립적인 상태를 가져야 할 때

</details>

<details>
<summary><strong>7. @PostConstruct와 @PreDestroy는 언제 사용하나요?</strong></summary>

**모범 답안 포인트**
- @PostConstruct: 초기화 작업 (의존성 주입 후)
- @PreDestroy: 정리 작업 (컨테이너 종료 전)
- DB 연결, 리소스 해제 등에 사용

**예시 답변**
> "@PostConstruct는 Bean의 의존성 주입이 완료된 직후에 실행되는 초기화 메서드를 지정하는 어노테이션입니다. DB 연결 초기화, 캐시 데이터 로드 등의 작업을 수행합니다. @PreDestroy는 컨테이너 종료 전에 실행되는 메서드로, DB 연결 종료, 파일 닫기 등 리소스 정리 작업을 수행합니다."

**꼬리 질문**
- Q: 생성자에서 초기화하면 안 되나요?
- A: 생성자는 의존성 주입 전에 실행되므로, 주입받은 Bean을 사용하는 초기화 로직은 @PostConstruct에 작성해야 함

</details>

---

### 📗 중급 개발자용 (5개)

<details>
<summary><strong>1. ApplicationContext의 계층 구조와 특징을 설명해주세요</strong></summary>

**모범 답안 포인트**
- BeanFactory → ApplicationContext 상속
- 국제화, 이벤트, 리소스 로딩 등 추가 기능
- Eager Loading vs Lazy Loading

**예시 답변**
> "ApplicationContext는 BeanFactory를 상속한 고급 컨테이너입니다. BeanFactory는 기본적인 Bean 생성과 관리만 담당하지만, ApplicationContext는 국제화(i18n), 이벤트 발행/구독, 리소스 로딩 등의 엔터프라이즈 기능을 추가로 제공합니다. 또한 BeanFactory는 Bean을 Lazy Loading 하지만, ApplicationContext는 컨테이너 시작 시 모든 Singleton Bean을 미리 생성하는 Eager Loading 방식을 사용합니다."

**실무 예시**
```java
// AnnotationConfigApplicationContext 사용
ApplicationContext context = new AnnotationConfigApplicationContext(AppConfig.class);

// 이벤트 발행
context.publishEvent(new UserRegisteredEvent(userId));
```

**꼬리 질문**
- Q: BeanFactory를 직접 사용하는 경우는?
- A: 메모리가 매우 제한적인 환경 (IoT 디바이스 등), 실무에서는 거의 없음

</details>

<details>
<summary><strong>2. 순환 참조(Circular Dependency) 문제와 해결 방법을 설명해주세요</strong></summary>

**모범 답안 포인트**
- A가 B를 의존, B가 A를 의존하는 상황
- Spring이 어느 Bean을 먼저 생성할지 결정 불가
- 해결: @Lazy, Setter 주입, 설계 개선

**예시 답변**
> "순환 참조는 두 Bean이 서로를 의존하는 상황으로, Spring 컨테이너가 어느 Bean을 먼저 생성해야 할지 결정할 수 없어 BeanCurrentlyInCreationException이 발생합니다. 해결 방법은 세 가지입니다. 첫째, @Lazy로 지연 로딩을 사용해 Proxy 객체를 주입받습니다. 둘째, Setter 주입으로 전환합니다. 하지만 가장 좋은 방법은 셋째, 설계를 개선하여 공통 로직을 별도 서비스로 분리하는 것입니다."

**실무 경험**
> "실제 프로젝트에서 UserService와 OrderService가 순환 참조하는 문제가 있었습니다. 두 서비스의 공통 로직을 UserOrderService로 분리하여 단방향 의존성으로 변경했고, 코드 가독성도 개선되었습니다."

**꼬리 질문**
- Q: Spring Boot 2.6부터 순환 참조가 기본적으로 금지되는데, 왜 그런가요?
- A: 잘못된 설계를 조기에 발견하도록 유도. 순환 참조는 대부분 설계 문제의 신호

</details>

<details>
<summary><strong>3. @Configuration에서 CGLIB Proxy가 사용되는 이유를 설명해주세요</strong></summary>

**모범 답안 포인트**
- @Bean 메서드의 Singleton 보장
- CGLIB이 클래스를 상속받아 프록시 생성
- Bean 간 의존성에서 같은 인스턴스 반환

**예시 답변**
> "@Configuration 클래스는 CGLIB 프록시로 감싸져서, @Bean 메서드를 여러 번 호출해도 항상 같은 인스턴스를 반환하도록 Singleton을 보장합니다. CGLIB은 클래스를 상속받아 프록시를 생성하고, @Bean 메서드 호출을 가로채서 이미 생성된 Bean이 있으면 캐시에서 반환합니다. 이 때문에 Bean 간 의존성이 있을 때 @Configuration을 사용해야 합니다."

**내부 동작**
```java
// @Configuration 없이 @Component 사용 시
@Component
public class Config {
    @Bean
    public A a() { return new A(); }

    @Bean
    public B b() {
        return new B(a());  // a()를 호출할 때마다 새 인스턴스!
    }
}

// @Configuration 사용 시
@Configuration
public class Config {
    @Bean
    public A a() { return new A(); }

    @Bean
    public B b() {
        return new B(a());  // CGLIB이 캐시된 인스턴스 반환!
    }
}
```

**꼬리 질문**
- Q: Lite Mode(@Component + @Bean)의 장단점은?
- A: 장점: 성능 (프록시 오버헤드 없음), 단점: Singleton 보장 안 됨

</details>

<details>
<summary><strong>4. Bean 생명주기의 각 단계와 BeanPostProcessor의 역할을 설명해주세요</strong></summary>

**모범 답안 포인트**
- 생성 → 의존성 주입 → 초기화 → 사용 → 소멸
- BeanPostProcessor가 초기화 전후에 개입
- AOP, 트랜잭션 등이 이를 활용

**예시 답변**
> "Bean 생명주기는 5단계로 구성됩니다. 1) 인스턴스 생성(Instantiation), 2) 의존성 주입(Dependency Injection), 3) 초기화(Initialization), 4) 사용, 5) 소멸(Destruction)입니다. 이 중 초기화 단계에서 BeanPostProcessor가 before와 after 메서드를 통해 Bean을 가공할 수 있습니다. AOP 프록시 생성, @Transactional 처리 등이 BeanPostProcessor를 통해 구현됩니다."

**상세 과정**
```
1. 생성자 호출
   ↓
2. Setter/Field 주입
   ↓
3. BeanPostProcessor.postProcessBeforeInitialization()
   ↓
4. @PostConstruct 실행
   ↓
5. InitializingBean.afterPropertiesSet()
   ↓
6. BeanPostProcessor.postProcessAfterInitialization()  ← AOP 프록시 생성
   ↓
7. Bean 사용 가능
   ↓
8. @PreDestroy 실행
   ↓
9. DisposableBean.destroy()
```

**실무 연관**
- @Transactional은 BeanPostProcessor가 프록시를 생성하여 트랜잭션 관리
- @Async도 동일하게 프록시로 비동기 실행

</details>

<details>
<summary><strong>5. Spring Container의 계층 구조(Parent-Child Context)는 언제 사용하나요?</strong></summary>

**모범 답안 포인트**
- Parent Context와 Child Context 분리
- 공통 Bean은 Parent, 웹 관련 Bean은 Child
- 웹 MVC에서 DispatcherServlet별로 Context 분리

**예시 답변**
> "Spring Container는 계층 구조를 가질 수 있어서, Parent Context와 Child Context로 분리할 수 있습니다. Parent Context에는 Service, Repository 등 비즈니스 로직을 담당하는 Bean을 등록하고, Child Context에는 Controller 등 웹 계층의 Bean을 등록합니다. Child는 Parent의 Bean을 참조할 수 있지만, 역은 불가능합니다. 이는 여러 DispatcherServlet을 사용할 때 각각 독립적인 웹 Context를 가지면서 공통 Service를 공유하는 데 유용합니다."

**사용 예시**
```java
// Root ApplicationContext (Parent)
@Configuration
@ComponentScan(basePackages = "com.example.service")
public class RootConfig {
    // Service, Repository 등록
}

// Web ApplicationContext (Child)
@Configuration
@ComponentScan(basePackages = "com.example.controller")
public class WebConfig {
    // Controller 등록
}
```

**실무 활용**
- 마이크로서비스에서 공통 모듈을 Parent Context로 분리
- 멀티 모듈 프로젝트에서 Core 모듈과 Web 모듈 분리

</details>

---

## 📝 핵심 정리

### 이 장에서 배운 핵심 개념

| 개념 | 설명 | 핵심 키워드 |
|------|------|-------------|
| IoC | 제어권이 개발자 → 프레임워크로 역전 | 제어의 역전, Inversion of Control |
| DI | 의존성을 외부에서 주입 | Dependency Injection, @Autowired |
| Bean | Spring이 관리하는 객체 | @Component, @Service, @Repository |
| ApplicationContext | IoC 컨테이너의 구현체 | Container, BeanFactory |
| Component Scan | @Component 탐색 및 Bean 등록 | @ComponentScan, 자동 등록 |
| Bean Scope | Bean의 생존 범위 | Singleton, Prototype |
| Bean Lifecycle | Bean의 생명주기 | @PostConstruct, @PreDestroy |

---

### 필수 어노테이션 정리

| 어노테이션 | 용도 | 예시 |
|-----------|------|------|
| `@Component` | 범용 Bean 등록 | `@Component class Util` |
| `@Service` | 서비스 계층 Bean | `@Service class UserService` |
| `@Repository` | 데이터 접근 계층 | `@Repository class UserRepo` |
| `@Controller` | 웹 컨트롤러 | `@Controller class UserCtrl` |
| `@Configuration` | 설정 클래스 | `@Configuration class Config` |
| `@Bean` | 메서드로 Bean 등록 | `@Bean ObjectMapper mapper()` |
| `@Autowired` | 의존성 자동 주입 | `@Autowired UserService svc` |
| `@Qualifier` | Bean 선택 | `@Qualifier("impl1")` |
| `@Primary` | 기본 Bean 지정 | `@Primary @Service class Impl` |
| `@Lazy` | 지연 로딩 | `@Lazy @Autowired Service svc` |
| `@Scope` | Bean 스코프 지정 | `@Scope("prototype")` |
| `@PostConstruct` | 초기화 콜백 | `@PostConstruct void init()` |
| `@PreDestroy` | 소멸 콜백 | `@PreDestroy void destroy()` |

---

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] **생성자 주입 사용**: final + 불변성 보장
- [ ] **인터페이스 기반 설계**: 구현체 교체 용이
- [ ] **@ComponentScan 범위 최소화**: 성능 최적화
- [ ] **Singleton Bean은 Stateless**: 상태 제거
- [ ] **@PostConstruct로 초기화**: 의존성 주입 후 실행
- [ ] **의미 있는 Bean 이름**: 명확한 네이밍

#### ❌ 하지 말아야 할 것
- [ ] **필드 주입 사용**: 테스트 어려움, final 불가
- [ ] **순환 참조 방치**: 설계 개선 필요
- [ ] **Singleton에 상태 저장**: Thread-safety 위반
- [ ] **과도한 Bean 등록**: 메모리 낭비
- [ ] **new로 Bean 생성**: IoC의 이점 상실

---

### 성능/보안 체크리스트

#### 성능
- [ ] **Component Scan 범위**: 필요한 패키지만 스캔
- [ ] **Lazy Loading 활용**: 사용하지 않는 Bean은 @Lazy
- [ ] **Prototype 남발 금지**: 메모리 증가 주의
- [ ] **Bean 생성 비용 고려**: 무거운 Bean은 Singleton

#### 보안
- [ ] **민감 정보 분리**: DB 비밀번호 등은 외부 설정
- [ ] **Profile 활용**: dev/prod 환경 분리
- [ ] **Bean 접근 제한**: package-private 생성자

---

## 🔗 관련 기술

**이 기술과 함께 사용하는 기술들**

| 기술 | 관계 | 학습 우선순위 |
|------|------|---------------|
| Dependency Injection | IoC의 구현 방법 | ⭐⭐⭐ 필수 |
| AOP | Bean 후처리에 활용 | ⭐⭐⭐ 필수 |
| Spring Boot | IoC 자동 설정 | ⭐⭐⭐ 필수 |
| JPA | IoC로 Repository 관리 | ⭐⭐ 권장 |
| Transaction | IoC + AOP 활용 | ⭐⭐ 권장 |

---

## 🚀 다음 단계

### 다음 장 미리보기: 04장 DI (Dependency Injection)

- **배울 내용 1**: 생성자/Setter/필드 주입의 상세 비교
- **배울 내용 2**: @Qualifier, @Primary로 Bean 선택
- **배울 내용 3**: 조건부 Bean 등록 (@Conditional)
- **실전 프로젝트**: 다양한 결제 게이트웨이를 DI로 전환

### 이 장과의 연결점
```
03장: IoC 컨테이너
    ↓
04장: DI (의존성 주입)
    ↓
05장: Bean 생명주기
    ↓
최종적으로: Spring 애플리케이션 아키텍처 마스터
```

---

## 🎉 축하합니다!

**이제 여러분은**:
- ✅ IoC 컨테이너의 개념과 동작 원리를 이해할 수 있습니다
- ✅ Bean을 다양한 방식으로 등록하고 관리할 수 있습니다
- ✅ 의존성 주입의 기본을 실무에 적용할 수 있습니다
- ✅ 생명주기 콜백으로 리소스를 관리할 수 있습니다

**다음 단계**:
- [ ] 04장: DI (Dependency Injection)로 진행
- [ ] 실전 프로젝트를 직접 확장해보기
- [ ] 면접 질문을 스스로 답변해보고 정리하기

---

**[← 이전: Part 7](03-7-IoC-컨테이너-Part7.md)** | **[다음: 04장 DI →](../04-DI.md)**

**목차로 돌아가기**: [📚 Spring 전체 목차](../README.md)
