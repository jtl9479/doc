# 08장: AOP 개념과 활용 - Part 1

**[다음: Part 2 →](08-2-AOP개념활용-Part2.md)** | **[목차로 돌아가기](../README.md)**

---

## 📚 학습 목표

이 장을 마치면 다음을 할 수 있습니다:

- [ ] AOP가 무엇이고 왜 필요한지 설명할 수 있다
- [ ] 핵심 관심사와 횡단 관심사를 구분할 수 있다
- [ ] @Aspect, @Before, @After, @Around 어노테이션을 사용할 수 있다
- [ ] Pointcut 표현식을 작성하고 이해할 수 있다
- [ ] 실무에서 AOP를 활용하여 로깅, 트랜잭션, 성능 측정을 구현할 수 있다

**난이도**: ⭐⭐⭐⭐⭐ (고급)
**예상 소요 시간**: 4시간
**선행 학습**: 03장(IoC), 04장(DI), 07장(어노테이션)

---

## 🤔 왜 AOP가 필요한가?

### 문제 상황

**모든 메서드에 반복되는 코드 (로깅, 트랜잭션, 성능 측정 등)**:

```java
// ❌ AOP 없이: 모든 메서드에 반복 코드
@Service
public class UserService {

    public User createUser(UserDto dto) {
        // 로깅
        log.info("createUser 시작");
        long start = System.currentTimeMillis();

        try {
            // 트랜잭션 시작
            transactionManager.begin();

            // 핵심 비즈니스 로직 (5줄)
            User user = new User(dto);
            userRepository.save(user);

            // 트랜잭션 커밋
            transactionManager.commit();

            // 성능 측정
            long duration = System.currentTimeMillis() - start;
            log.info("createUser 완료: {}ms", duration);

            return user;

        } catch (Exception e) {
            // 트랜잭션 롤백
            transactionManager.rollback();

            // 에러 로깅
            log.error("createUser 실패", e);
            throw e;
        }
    }

    public void deleteUser(Long id) {
        // 위와 동일한 코드 또 작성... 😱
        log.info("deleteUser 시작");
        long start = System.currentTimeMillis();
        // ... 반복
    }

    // 100개 메서드가 있다면? 모든 메서드에 반복 코드! 😱😱😱
}
```

**측정 가능한 문제점**:
- ❌ **코드 중복**: 핵심 로직 5줄, 부가 로직 20줄 (400% 증가)
- ❌ **유지보수**: 로깅 형식 변경 시 100개 메서드 수정 필요
- ❌ **가독성**: 핵심 로직이 부가 로직에 묻힘
- ❌ **개발 시간**: 메서드 하나당 5분 추가 소요

### 해결책: AOP (Aspect-Oriented Programming)

```java
// ✅ AOP 사용: 부가 로직을 분리
@Service
public class UserService {

    public User createUser(UserDto dto) {
        // 핵심 비즈니스 로직만!
        User user = new User(dto);
        userRepository.save(user);
        return user;
    }

    public void deleteUser(Long id) {
        // 핵심 로직만!
        userRepository.deleteById(id);
    }
}

// 부가 로직은 Aspect로 분리
@Aspect
@Component
public class LoggingAspect {

    @Around("execution(* com.example.service.*.*(..))")
    public Object log(ProceedingJoinPoint joinPoint) throws Throwable {
        // 모든 Service 메서드에 자동 적용!
        log.info("{} 시작", joinPoint.getSignature().getName());
        long start = System.currentTimeMillis();

        try {
            Object result = joinPoint.proceed();  // 핵심 로직 실행

            long duration = System.currentTimeMillis() - start;
            log.info("{} 완료: {}ms", joinPoint.getSignature().getName(), duration);

            return result;
        } catch (Exception e) {
            log.error("{} 실패", joinPoint.getSignature().getName(), e);
            throw e;
        }
    }
}
```

**개선 효과**:
- ✅ **코드 중복 제거**: 100개 메서드에서 공통 코드 1곳으로 집중
- ✅ **유지보수 간편**: Aspect 1곳만 수정하면 전체 적용
- ✅ **가독성 향상**: 핵심 로직에만 집중 가능
- ✅ **개발 시간**: 메서드당 5분 → 10초 (95% 단축)

---

## 🌟 실생활 비유 5가지

### 비유 1: 공항 보안 검색대 ✈️

**AOP 없이**:
- 각 항공사 직원이 승객에게 "보안 검색하세요"라고 일일이 안내
- 탑승 수속마다 반복

**AOP 사용 (공항 보안 검색대)**:
- 모든 탑승구 앞에 보안 검색대 설치
- 어느 항공사든 자동으로 보안 검색 통과
- 항공사는 탑승 수속에만 집중

```java
@Aspect  // 보안 검색대
public class SecurityAspect {

    @Before("탑승구()")  // 탑승구 진입 전
    public void 보안검색() {
        System.out.println("보안 검색 실시");
    }
}
```

### 비유 2: 식당의 웨이터 🍽️

**AOP 없이**:
- 요리사가 요리 + 주문 받기 + 서빙 + 계산 모두 직접
- 요리에 집중 못함

**AOP 사용 (웨이터)**:
- 요리사는 요리만 집중
- 웨이터가 주문, 서빙, 계산 대행
- 횡단 관심사를 웨이터(Aspect)가 처리

```java
@Aspect  // 웨이터
public class WaiterAspect {

    @Before("요리()")  // 요리 전
    public void 주문받기() { }

    @After("요리()")  // 요리 후
    public void 서빙하기() { }
}

public class Chef {
    public void 요리() {
        // 요리에만 집중!
    }
}
```

### 비유 3: 배달의민족 배달 추적 🛵

**AOP 없이**:
- 모든 식당이 "주문 접수됨", "조리 시작", "배달 시작" 알림을 직접 구현
- 1만 개 식당이 각자 구현

**AOP 사용 (통합 추적 시스템)**:
- 배달의민족 플랫폼이 자동으로 추적
- 식당은 조리에만 집중
- 알림은 플랫폼(Aspect)이 자동 처리

```java
@Aspect  // 배달의민족 추적 시스템
public class DeliveryTrackingAspect {

    @Before("조리()")
    public void 알림_조리시작() {
        푸시알림.send("조리가 시작되었습니다");
    }

    @After("조리()")
    public void 알림_조리완료() {
        푸시알림.send("조리가 완료되었습니다");
    }
}
```

### 비유 4: 회사의 출퇴근 기록 시스템 🏢

**AOP 없이**:
- 각 부서가 직원 출퇴근 기록을 수동으로 관리
- 실수 빈번, 통합 어려움

**AOP 사용 (자동 출퇴근 기록)**:
- 출입문에 카드 리더기 설치
- 모든 직원 자동으로 기록
- 부서는 업무에만 집중

```java
@Aspect  // 출퇴근 기록 시스템
public class AttendanceAspect {

    @Before("출근()")
    public void 출근기록() {
        기록.save(직원, "출근", 현재시간);
    }

    @After("퇴근()")
    public void 퇴근기록() {
        기록.save(직원, "퇴근", 현재시간);
    }
}
```

### 비유 5: 카카오톡 읽음 표시 💬

**AOP 없이**:
- 각 대화방마다 "읽음 표시" 기능을 직접 구현
- 1억 개 대화방에 중복 코드

**AOP 사용 (통합 읽음 처리)**:
- 카카오톡 플랫폼이 자동으로 처리
- 메시지 읽으면 자동으로 "읽음" 표시
- 대화방은 메시지 전송에만 집중

```java
@Aspect  // 카카오톡 읽음 처리 시스템
public class ReadReceiptAspect {

    @After("메시지읽기()")
    public void 읽음처리() {
        상대방에게.전송("읽음");
        메시지상태.update("읽음");
    }
}
```

---

## 💡 핵심 개념

### 개념 1: AOP란 무엇인가?

#### 초등학생도 이해하는 설명
> "AOP는 '모든 요리에 소금을 뿌려주는 로봇'이에요. 요리사는 요리만 하면 로봇이 자동으로 소금을 뿌려줘요. 로깅, 트랜잭션 같은 걸 자동으로 해주는 기능이에요."

#### 중급 개발자를 위한 설명
> "AOP(Aspect-Oriented Programming)는 횡단 관심사(cross-cutting concerns)를 모듈화하는 프로그래밍 패러다임입니다. 로깅, 트랜잭션, 보안 등 여러 모듈에 걸쳐 공통으로 필요한 부가 기능을 핵심 비즈니스 로직에서 분리하여 Aspect로 정의하고, 런타임 시점에 동적으로 적용합니다."

#### 고급 개발자를 위한 설명
> "AOP는 Proxy 패턴을 기반으로 한 메타프로그래밍 기법입니다. Spring AOP는 JDK Dynamic Proxy 또는 CGLIB을 사용하여 런타임에 Proxy 객체를 생성하고, AspectJ 컴파일러의 Pointcut 표현식으로 Join Point를 선택하여 Advice를 적용합니다. Method Interceptor 체인으로 구현되며, @Around는 MethodInterceptor, @Before/@After는 MethodBeforeAdvice/AfterReturningAdvice로 변환됩니다."

---

### 개념 2: AOP 핵심 용어

```
Target (대상)
  ↓
Join Point (실행 지점)
  ↓
Pointcut (선택)
  ↓
Advice (부가 기능)
  ↓
Aspect (모듈)
```

#### 1. Target (타겟)

> 부가 기능을 적용할 대상 (보통 Service 클래스)

```java
@Service  // ← 이게 Target
public class UserService {

    public User createUser(UserDto dto) {
        // 이 메서드가 Target의 Join Point
    }
}
```

#### 2. Join Point (조인 포인트)

> 부가 기능이 적용될 수 있는 실행 지점 (Spring AOP는 메서드 실행 시점만 지원)

```java
public class UserService {

    public User createUser(UserDto dto) {
        // ← 이 메서드 실행이 Join Point
    }

    public void deleteUser(Long id) {
        // ← 이 메서드 실행도 Join Point
    }
}
```

#### 3. Pointcut (포인트컷)

> Join Point 중에서 Advice를 적용할 지점을 선택하는 표현식

```java
@Aspect
public class LoggingAspect {

    // Pointcut: UserService의 모든 public 메서드
    @Pointcut("execution(* com.example.service.UserService.*(..))")
    public void userServiceMethods() {
    }
}
```

#### 4. Advice (어드바이스)

> 실제로 실행될 부가 기능 (로깅, 트랜잭션 등)

```java
@Aspect
public class LoggingAspect {

    @Before("userServiceMethods()")  // ← Advice
    public void logBefore(JoinPoint joinPoint) {
        log.info("메서드 시작: {}", joinPoint.getSignature().getName());
    }
}
```

#### 5. Aspect (애스펙트)

> Pointcut + Advice를 모듈화한 것

```java
@Aspect  // ← Aspect
@Component
public class LoggingAspect {

    @Pointcut(...)  // Pointcut
    public void userServiceMethods() { }

    @Before(...)  // Advice
    public void logBefore() { }
}
```

#### 6. Advisor

> Aspect의 단순한 형태 (Pointcut 1개 + Advice 1개)

```java
@Bean
public Advisor loggingAdvisor() {
    AspectJExpressionPointcut pointcut = new AspectJExpressionPointcut();
    pointcut.setExpression("execution(* com.example.service.*.*(..))");

    DefaultPointcutAdvisor advisor = new DefaultPointcutAdvisor();
    advisor.setPointcut(pointcut);
    advisor.setAdvice(new LoggingAdvice());

    return advisor;
}
```

#### 7. Weaving (위빙)

> Aspect를 Target에 적용하는 과정 (Proxy 생성)

```
Target 객체 → (Weaving) → Proxy 객체 → (Advice 적용) → Target 실행
```

---

### 개념 3: Advice 종류

#### 1. @Before: 메서드 실행 전

```java
@Aspect
@Component
public class BeforeAspect {

    @Before("execution(* com.example.service.*.*(..))")
    public void logBefore(JoinPoint joinPoint) {
        log.info("메서드 시작: {}", joinPoint.getSignature().getName());
        log.info("파라미터: {}", Arrays.toString(joinPoint.getArgs()));
    }
}

// 실행 순서
// 1. @Before 실행
// 2. 실제 메서드 실행
// 3. 종료
```

#### 2. @After: 메서드 실행 후 (무조건 실행)

```java
@Aspect
@Component
public class AfterAspect {

    @After("execution(* com.example.service.*.*(..))")
    public void logAfter(JoinPoint joinPoint) {
        log.info("메서드 종료: {}", joinPoint.getSignature().getName());
        // 예외 발생 여부와 무관하게 항상 실행
    }
}

// 실행 순서
// 1. 실제 메서드 실행
// 2. @After 실행 (성공/실패 무관)
// 3. 종료
```

#### 3. @AfterReturning: 메서드가 정상 종료된 후

```java
@Aspect
@Component
public class AfterReturningAspect {

    @AfterReturning(
        pointcut = "execution(* com.example.service.*.*(..))",
        returning = "result"  // 반환값을 받을 파라미터 이름
    )
    public void logAfterReturning(JoinPoint joinPoint, Object result) {
        log.info("메서드 성공: {}", joinPoint.getSignature().getName());
        log.info("반환값: {}", result);
    }
}

// 실행 순서
// 1. 실제 메서드 실행
// 2. 성공 시에만 @AfterReturning 실행
// 3. 종료
```

#### 4. @AfterThrowing: 예외 발생 시

```java
@Aspect
@Component
public class AfterThrowingAspect {

    @AfterThrowing(
        pointcut = "execution(* com.example.service.*.*(..))",
        throwing = "ex"  // 예외를 받을 파라미터 이름
    )
    public void logAfterThrowing(JoinPoint joinPoint, Exception ex) {
        log.error("메서드 실패: {}", joinPoint.getSignature().getName());
        log.error("예외: ", ex);
    }
}

// 실행 순서
// 1. 실제 메서드 실행
// 2. 예외 발생 시에만 @AfterThrowing 실행
// 3. 예외 전파
```

#### 5. @Around: 메서드 실행 전후 (가장 강력)

```java
@Aspect
@Component
public class AroundAspect {

    @Around("execution(* com.example.service.*.*(..))")
    public Object logAround(ProceedingJoinPoint joinPoint) throws Throwable {
        log.info("⏰ 메서드 시작: {}", joinPoint.getSignature().getName());
        long start = System.currentTimeMillis();

        try {
            // 실제 메서드 실행
            Object result = joinPoint.proceed();

            long duration = System.currentTimeMillis() - start;
            log.info("✅ 메서드 성공: {}ms", duration);

            return result;  // 반환값 수정 가능

        } catch (Exception e) {
            log.error("❌ 메서드 실패", e);
            throw e;  // 예외 변환 가능
        }
    }
}

// 실행 순서
// 1. @Around 시작 부분 실행
// 2. joinPoint.proceed() → 실제 메서드 실행
// 3. @Around 종료 부분 실행
```

#### Advice 실행 순서 정리

```java
@Aspect
@Component
public class OrderTestAspect {

    @Around("execution(* com.example.service.*.*(..))")
    public Object around(ProceedingJoinPoint joinPoint) throws Throwable {
        System.out.println("1. @Around 시작");
        Object result = joinPoint.proceed();
        System.out.println("5. @Around 종료");
        return result;
    }

    @Before("execution(* com.example.service.*.*(..))")
    public void before() {
        System.out.println("2. @Before");
    }

    @AfterReturning("execution(* com.example.service.*.*(..))")
    public void afterReturning() {
        System.out.println("4. @AfterReturning");
    }

    @After("execution(* com.example.service.*.*(..))")
    public void after() {
        System.out.println("6. @After");
    }
}

// 실행 결과 (메서드 성공 시)
// 1. @Around 시작
// 2. @Before
// 3. [실제 메서드 실행]
// 4. @AfterReturning
// 5. @Around 종료
// 6. @After
```

---

### 개념 4: Pointcut 표현식

#### execution 표현식 (가장 많이 사용)

```java
execution(modifiers-pattern? return-type-pattern declaring-type-pattern?
          method-name-pattern(param-pattern) throws-pattern?)

// ? = 생략 가능
```

#### 상세 예제

```java
// 1. 모든 public 메서드
@Pointcut("execution(public * *(..))")

// 2. 이름이 "create"로 시작하는 메서드
@Pointcut("execution(* create*(..))")

// 3. Service 패키지의 모든 메서드
@Pointcut("execution(* com.example.service.*.*(..))")

// 4. Service 패키지와 하위 패키지의 모든 메서드
@Pointcut("execution(* com.example.service..*.*(..))")

// 5. UserService의 모든 메서드
@Pointcut("execution(* com.example.service.UserService.*(..))")

// 6. 파라미터가 없는 메서드
@Pointcut("execution(* com.example.service.*.*())")

// 7. 파라미터가 1개인 메서드
@Pointcut("execution(* com.example.service.*.*(*))")

// 8. 파라미터가 String 1개인 메서드
@Pointcut("execution(* com.example.service.*.*(String))")

// 9. 첫 번째 파라미터가 String이고 나머지는 임의
@Pointcut("execution(* com.example.service.*.*(String, ..))")

// 10. 반환 타입이 void인 메서드
@Pointcut("execution(void com.example.service.*.*(..))")

// 11. 반환 타입이 User인 메서드
@Pointcut("execution(com.example.domain.User com.example.service.*.*(..))")
```

#### within 표현식 (타입 기준)

```java
// 1. 특정 타입의 모든 메서드
@Pointcut("within(com.example.service.UserService)")

// 2. 패키지의 모든 타입
@Pointcut("within(com.example.service.*)")

// 3. 패키지와 하위 패키지의 모든 타입
@Pointcut("within(com.example.service..*)")
```

#### @annotation 표현식 (어노테이션 기준)

```java
// 커스텀 어노테이션
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface PerformanceLog {
}

// Pointcut
@Pointcut("@annotation(com.example.annotation.PerformanceLog)")
public void performanceLogMethods() {
}

// 사용
@Service
public class UserService {

    @PerformanceLog  // 이 메서드만 AOP 적용
    public User createUser(UserDto dto) {
        // ...
    }

    public void deleteUser(Long id) {
        // AOP 적용 안 됨
    }
}
```

#### bean 표현식 (Bean 이름 기준)

```java
// 1. 특정 Bean
@Pointcut("bean(userService)")

// 2. 이름이 "Service"로 끝나는 모든 Bean
@Pointcut("bean(*Service)")

// 3. 특정 Bean 제외
@Pointcut("bean(*Service) && !bean(adminService)")
```

#### 조합 표현식

```java
// 1. AND (&&)
@Pointcut("execution(* com.example.service.*.*(..)) && @annotation(Transactional)")

// 2. OR (||)
@Pointcut("execution(* com.example.service.*.*(..)) || execution(* com.example.repository.*.*(..))")

// 3. NOT (!)
@Pointcut("execution(* com.example.service.*.*(..)) && !execution(* com.example.service.Internal*.*(..))")

// 4. 복잡한 조합
@Pointcut("execution(* com.example..*.*(..)) && (within(com.example.service..*) || @annotation(Loggable))")
```

---

**[다음: Part 2 →](08-2-AOP개념활용-Part2.md)** | **[목차로 돌아가기](../README.md)**
