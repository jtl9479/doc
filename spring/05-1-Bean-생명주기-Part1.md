# 05장: Bean 생명주기 (Bean Lifecycle)

> **학습 목표**: 이 장을 완료하면 Spring Bean의 생명주기를 이해하고, @PostConstruct, @PreDestroy로 초기화/소멸 로직을 관리할 수 있습니다.

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
**데이터베이스 연결 풀을 사용하는 서비스에서, 애플리케이션 시작 시 연결을 초기화하고 종료 시 정리해야 한다면?**

#### ❌ 이 기술을 모르면 발생하는 문제

```
문제 1: 리소스 누수
- 증상: DB 연결, 파일 핸들을 닫지 않고 종료
- 영향: 메모리 누수, 연결 고갈로 새 요청 처리 불가
- 비용: 서버 재시작 필요, 서비스 다운타임 발생

문제 2: 초기화 시점 불명확
- 증상: 생성자에서 DB 연결 시도 → 의존성 주입 전이라 NPE
- 영향: 애플리케이션 시작 실패, 디버깅 어려움
- 비용: 개발 시간 낭비, 장애 대응 지연

문제 3: 수동 관리 부담
- 증상: 개발자가 직접 초기화/소멸 메서드 호출
- 영향: 누락 가능성, 휴먼 에러
- 비용: 운영 부담 증가, 장애 발생률 높음
```

#### ✅ 이 기술을 사용하면

```
해결책 1: 자동 리소스 관리
- 방법: @PreDestroy로 종료 시 자동으로 연결 정리
- 효과: 메모리 누수 제로, 안정적인 종료
- 절감: 재시작 횟수 90% 감소, 다운타임 제로

해결책 2: 명확한 초기화 시점
- 방법: @PostConstruct로 의존성 주입 후 초기화
- 효과: NPE 방지, 안정적인 시작
- 절감: 초기화 버그 100% 제거

해결책 3: Spring이 자동 관리
- 방법: 생명주기 콜백을 Spring이 자동 호출
- 효과: 수동 관리 불필요, 누락 제로
- 절감: 운영 부담 70% 감소
```

### 📊 수치로 보는 효과

| 지표 | Before (수동 관리) | After (생명주기 관리) | 개선율 |
|------|-------------------|---------------------|--------|
| 메모리 누수 | 월 10건 | 0건 | **100%↓** |
| 초기화 실패 | 주 5건 | 0건 | **100%↓** |
| 서버 재시작 | 주 3회 | 월 0회 | **95%↓** |
| 다운타임 | 월 2시간 | 0분 | **100%↓** |

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 식당 영업

```
Bean 생명주기 = 식당의 하루

개업 준비 (생성):
- 건물 임대 계약 (Bean 객체 생성)
- 직원 고용 (의존성 주입)

오픈 준비 (초기화 - @PostConstruct):
- 냉장고 켜기, 재료 준비
- 테이블 세팅, 메뉴판 준비
- 주방 청소, 기구 점검

영업 중 (사용):
- 손님 맞이, 주문 받기
- 요리 제공

폐업 준비 (소멸 - @PreDestroy):
- 주방 정리, 냉장고 정리
- 테이블 청소
- 잠금 장치, 전등 끄기

┌─────────────────────────────────┐
│     Bean 생명주기               │
│                                 │
│  1. 생성 (건물 임대)            │
│        ↓                        │
│  2. 의존성 주입 (직원 고용)     │
│        ↓                        │
│  3. @PostConstruct (오픈 준비)  │
│        ↓                        │
│  4. 사용 (영업 중)              │
│        ↓                        │
│  5. @PreDestroy (폐업 정리)     │
│        ↓                        │
│  6. 소멸 (계약 종료)            │
└─────────────────────────────────┘

매핑:
식당 = Bean
오픈 준비 = @PostConstruct
영업 중 = Bean 사용
폐업 정리 = @PreDestroy
```

### 비유 2: 비행기 운항

```
Bean 생명주기 = 비행기 한 편의 운항

출발 전 (초기화):
- 기체 점검 (시스템 체크)
- 연료 주입 (리소스 로딩)
- 승무원 탑승 (의존성 주입 완료)
- 안전 점검 완료 (@PostConstruct)

비행 중 (사용):
- 이륙, 순항, 착륙
- 승객 서비스 제공

착륙 후 (소멸):
- 승객 하차
- 기내 청소 (@PreDestroy)
- 다음 운항 준비 또는 정비

┌──────────────────────────────┐
│    비행기 운항               │
│                              │
│  출발 전 점검 → 비행 → 정리 │
│  @PostConstruct → 사용 → @PreDestroy │
└──────────────────────────────┘
```

### 비유 3: 컴퓨터 부팅

```
Bean 생명주기 = 컴퓨터 부팅 프로세스

부팅 (생성 ~ 초기화):
1. 전원 켜기 (Bean 생성)
2. BIOS 로딩 (기본 설정)
3. OS 로딩 (의존성 주입)
4. 드라이버 로딩 (@PostConstruct)
5. 시작 프로그램 실행 (초기화 완료)

사용:
- 애플리케이션 실행
- 작업 수행

종료 (소멸):
1. 프로그램 저장 및 종료
2. 임시 파일 정리 (@PreDestroy)
3. 전원 끄기 (Bean 제거)

매핑:
부팅 = Bean 초기화
드라이버 로딩 = @PostConstruct
작업 = Bean 사용
종료 = @PreDestroy
```

### 비유 4: 수영장 운영

```
Bean 생명주기 = 수영장 하루

오픈 전 (초기화):
- 수질 검사 (시스템 체크)
- 물 온도 조절 (환경 설정)
- 청소 및 소독 (@PostConstruct)
- 안전 요원 배치

운영 중 (사용):
- 입장객 관리
- 안전 감독

마감 후 (소멸):
- 입장객 퇴장
- 락커룸 점검
- 시설 소독 (@PreDestroy)
- 잠금 장치
```

### 비유 5: 스마트폰 앱

```
Bean 생명주기 = 앱의 생명주기

앱 설치 (Bean 등록):
- 앱 다운로드
- 시스템에 등록

앱 시작 (초기화):
- 앱 아이콘 터치 (Bean 생성 트리거)
- 스플래시 화면 (로딩)
- 권한 확인, 설정 로드 (@PostConstruct)
- 메인 화면 표시

앱 사용:
- 기능 사용

앱 종료 (소멸):
- 데이터 저장 (@PreDestroy)
- 캐시 정리
- 메모리 해제

┌──────────────────────────────┐
│  앱 시작 → 사용 → 종료       │
│  @PostConstruct → Bean → @PreDestroy │
└──────────────────────────────┘
```

### 🎯 종합 비교표

```
┌──────────────┬────────────┬────────────┬────────────┐
│ 생명주기 단계│ 식당       │ 비행기     │ 컴퓨터     │
├──────────────┼────────────┼────────────┼────────────┤
│ 생성         │ 건물 임대  │ 기체 준비  │ 전원 켜기  │
│ 의존성 주입  │ 직원 고용  │ 승무원 탑승│ OS 로딩    │
│ @PostConstruct│ 오픈 준비 │ 안전 점검  │ 드라이버   │
│ 사용         │ 영업       │ 비행       │ 작업       │
│ @PreDestroy  │ 폐업 정리  │ 기내 청소  │ 종료       │
│ 소멸         │ 계약 종료  │ 정비       │ 전원 끄기  │
└──────────────┴────────────┴────────────┴────────────┘
```

---

## 📖 핵심 개념

### Bean 생명주기 전체 흐름

```
┌─────────────────────────────────────────────────────────┐
│              Spring Bean 생명주기 (상세)                │
└─────────────────────────────────────────────────────────┘

1️⃣ 인스턴스화 (Instantiation)
   - Spring이 Bean 클래스의 생성자 호출
   - new를 통해 객체 생성
   예: UserService service = new UserService();

2️⃣ 프로퍼티 설정 (Populate Properties)
   - 의존성 주입 (DI) 수행
   - @Autowired 필드/Setter에 Bean 주입
   예: service.setUserRepository(userRepository);

3️⃣ BeanNameAware의 setBeanName() 호출 (선택)
   - Bean 이름을 Bean에게 알림

4️⃣ BeanFactoryAware의 setBeanFactory() 호출 (선택)
   - BeanFactory를 Bean에게 전달

5️⃣ ApplicationContextAware의 setApplicationContext() 호출 (선택)
   - ApplicationContext를 Bean에게 전달

6️⃣ BeanPostProcessor의 postProcessBeforeInitialization() 호출
   - Bean 초기화 전 전처리
   - AOP 프록시 생성 등

7️⃣ @PostConstruct 어노테이션 메서드 호출 ⭐
   - 개발자가 정의한 초기화 로직 실행
   예: DB 연결 풀 생성, 캐시 로드

8️⃣ InitializingBean의 afterPropertiesSet() 호출 (레거시)
   - 구식 방법, @PostConstruct 사용 권장

9️⃣ @Bean(initMethod) 호출 (선택)
   - Java Config에서 지정한 초기화 메서드

🔟 BeanPostProcessor의 postProcessAfterInitialization() 호출
   - Bean 초기화 후 후처리
   - AOP 프록시 최종 처리

1️⃣1️⃣ Bean 사용 가능 상태 ✅
   - 애플리케이션에서 Bean 사용
   - 비즈니스 로직 실행

1️⃣2️⃣ 컨테이너 종료 시작

1️⃣3️⃣ @PreDestroy 어노테이션 메서드 호출 ⭐
   - 개발자가 정의한 정리 로직 실행
   예: DB 연결 종료, 파일 닫기

1️⃣4️⃣ DisposableBean의 destroy() 호출 (레거시)
   - 구식 방법, @PreDestroy 사용 권장

1️⃣5️⃣ @Bean(destroyMethod) 호출 (선택)
   - Java Config에서 지정한 소멸 메서드

1️⃣6️⃣ Bean 소멸
   - GC에 의해 메모리에서 제거
```

### 주요 생명주기 콜백 메서드

```java
@Component
public class LifecycleBean {

    private DataSource dataSource;

    // 1. 생성자 (가장 먼저 실행)
    public LifecycleBean() {
        System.out.println("1. 생성자 호출");
        // 주의: 이 시점에는 의존성이 주입되지 않음!
    }

    // 2. 의존성 주입
    @Autowired
    public void setDataSource(DataSource dataSource) {
        System.out.println("2. 의존성 주입");
        this.dataSource = dataSource;
    }

    // 3. 초기화 콜백 (@PostConstruct) ⭐ 가장 많이 사용
    @PostConstruct
    public void init() {
        System.out.println("3. @PostConstruct 실행");
        // 의존성이 모두 주입된 후 실행
        // DB 연결, 캐시 로드, 파일 열기 등
        if (dataSource != null) {
            System.out.println("   DB 연결 준비 완료");
        }
    }

    // 4. 비즈니스 로직 (Bean 사용)
    public void doSomething() {
        System.out.println("4. 비즈니스 로직 실행");
    }

    // 5. 소멸 콜백 (@PreDestroy) ⭐ 가장 많이 사용
    @PreDestroy
    public void cleanup() {
        System.out.println("5. @PreDestroy 실행");
        // 컨테이너 종료 전 정리 작업
        // DB 연결 종료, 파일 닫기, 스레드 정리 등
        if (dataSource != null) {
            System.out.println("   DB 연결 종료");
        }
    }
}
```

### 생명주기 콜백 3가지 방법 비교

```java
// 방법 1: @PostConstruct / @PreDestroy (권장 ⭐⭐⭐⭐⭐)
@Component
public class ModernBean {

    @PostConstruct
    public void init() {
        System.out.println("초기화");
    }

    @PreDestroy
    public void destroy() {
        System.out.println("정리");
    }
}
// 장점: 표준 JSR-250, 간결, IDE 지원 우수
// 단점: 외부 라이브러리에는 사용 불가

// 방법 2: InitializingBean, DisposableBean (레거시 ⭐⭐)
@Component
public class LegacyBean implements InitializingBean, DisposableBean {

    @Override
    public void afterPropertiesSet() throws Exception {
        System.out.println("초기화");
    }

    @Override
    public void destroy() throws Exception {
        System.out.println("정리");
    }
}
// 장점: Spring 초기 버전부터 지원
// 단점: Spring 인터페이스에 의존, 코드 침투적

// 방법 3: @Bean(initMethod, destroyMethod) (외부 라이브러리용 ⭐⭐⭐⭐)
@Configuration
public class ExternalLibraryConfig {

    @Bean(initMethod = "connect", destroyMethod = "disconnect")
    public DatabaseClient databaseClient() {
        return new DatabaseClient();
    }
}

// 외부 라이브러리 클래스 (수정 불가)
public class DatabaseClient {
    public void connect() {
        System.out.println("DB 연결");
    }

    public void disconnect() {
        System.out.println("DB 종료");
    }
}
// 장점: 외부 라이브러리에도 적용 가능
// 단점: 메서드 이름을 문자열로 지정 (오타 위험)
```

### 실행 순서 확인

```java
@Component
public class LifecycleDemo {

    private String name;

    public LifecycleDemo() {
        System.out.println("1. 생성자: name = " + name);  // null
    }

    @Autowired
    public void setName(@Value("MyBean") String name) {
        this.name = name;
        System.out.println("2. 의존성 주입: name = " + name);  // "MyBean"
    }

    @PostConstruct
    public void init() {
        System.out.println("3. @PostConstruct: name = " + name);  // "MyBean"
        // 이제 name을 사용해도 안전!
    }

    @PreDestroy
    public void destroy() {
        System.out.println("4. @PreDestroy: 정리 작업");
    }
}

// 출력:
// 1. 생성자: name = null
// 2. 의존성 주입: name = MyBean
// 3. @PostConstruct: name = MyBean
// (애플리케이션 종료 시)
// 4. @PreDestroy: 정리 작업
```

---

**[다음: Part 2로 계속 →](05-2-Bean-생명주기-Part2.md)**
