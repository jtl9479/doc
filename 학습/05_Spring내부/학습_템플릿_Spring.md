# Spring 내부 학습 템플릿

> 유형: **개념 + 코드 + 내부 동작 추적**
> 적용: 학습_05_Spring내부.md의 Step 1~21

## 공통 원칙

| 원칙 | 설명 |
|------|------|
| **왜 먼저** | "이 기능을 매일 쓰지만 내부를 모르면 이런 장애/버그가 발생한다" |
| **비유 먼저** | Spring 내부 동작을 일상 비유로 직관 잡기 |
| **트레이드오프** | 모든 설정/패턴에 트레이드오프 명시 |
| **버전 차이** | Spring Boot 2.x→3.x, Security 5→6, javax→jakarta 변경 언급 |

### 비유 예시
```
Spring Framework = "레고 조립 설명서. 부품(Bean)을 규칙대로 조립하면 완성품(앱)이 됨"
Spring Boot = "레고 완성 세트. 설명서 없이 뚜껑 열면 거의 조립되어 있음(Auto Configuration)"
레이어드 아키텍처 = "회사 조직도. 영업부(Controller) → 기획부(Service) → 자료실(Repository). 위에서 아래로만 지시"
IoC 컨테이너 = "가구 배달 서비스. 내가 직접 가구를 만들지(new) 않고, 주문하면(DI) 배달해줌"
생성자 주입 = "이사할 때 필수 가구를 계약서에 명시. 빠지면 이사 불가(컴파일 에러). 한번 배치하면 안 바꿈(final)"
필드 주입 = "이사 후 마음대로 가구 들여놓기. 편하지만 뭐가 필수인지 모르고, 테스트 시 가짜로 교체 어려움"
Singleton 빈 = "회사 공용 프린터. 1대를 모든 부서가 공유. 프린터에 '내 설정'을 저장하면 다른 부서가 피해(상태 문제)"
Prototype 빈 = "일회용 컵. 매번 새것. 하지만 Singleton이 Prototype을 주입받으면 처음 1개만 받고 끝"
AOP 프록시 = "비서. 사장(실제 객체)에게 전화가 오면 비서(프록시)가 먼저 받아서 스케줄 확인(Before) → 사장 연결 → 통화 후 기록(After)"
self-invocation = "비서를 거치지 않고 사장이 직접 자기 내선 전화를 걸면 비서(프록시)가 개입 못 함"
빈 후처리기 = "택배 검수 센터. 상품(빈)이 나가기 전에 검수(프록시 교체, 초기화 콜백)를 거침"
DispatcherServlet = "호텔 프론트 데스크. 모든 손님(요청)이 프론트를 거쳐 적절한 방(Controller)으로 안내"
Filter vs Interceptor = "건물 입구 경비(Filter, 서블릿 레벨) vs 사무실 입구 안내데스크(Interceptor, Spring 레벨)"
@Transactional = "은행 창구. 입금+출금을 하나의 처리로 묶음. 하나라도 실패하면 전부 취소"
REQUIRES_NEW = "은행 본거래 중 별도 창구에서 독립 처리. 본거래 취소되어도 별도 창구 기록은 유지. 단, 창구(커넥션) 추가 점유"
NESTED = "같은 창구에서 중간 저장(Savepoint). 실패하면 중간 저장 지점까지만 취소. 별도 창구 불필요"
DataSource = "수도관. 물(커넥션)을 미리 파이프(풀)에 준비해두고 필요할 때 즉시 사용"
예외 추상화 = "통역사. Oracle이 말하든(ORA-00001) MySQL이 말하든(1062) 같은 한국어(DataAccessException)로 번역"
Auto Configuration = "호텔 체크인. 이름만 말하면(의존성 추가) 방 배정+수건+어메니티가 자동 준비. 필요 없으면 '수건 빼주세요(exclude)'"
Actuator = "건강검진 키트. /health(심박), /metrics(체온), /loggers(시력). 운영 중 상태를 실시간 확인"
이벤트 = "사내 게시판. 공지(이벤트) 올리면 관심 있는 부서(리스너)가 알아서 확인. 공지자는 누가 볼지 모름(결합도↓)"
@TransactionalEventListener = "결재 완료 후 게시. 결재(커밋) 전에 게시하면 결재 취소 시 이미 공지된 문제"
WebFlux = "놀이공원 패스트패스. 줄 서지 않고(Non-blocking) 시간 되면 알림(콜백). 적은 직원(스레드)으로 많은 손님 처리"
MockMvc = "시뮬레이터. 실제 서버 안 띄우고 요청-응답 검증"
@WebMvcTest = "부분 시운전. 엔진(Controller)만 테스트. 바퀴(Service)는 가짜(Mock)"
```

### 트레이드오프 예시
```
생성자 주입: 불변+테스트 용이 ↔ 의존성 많으면 생성자 비대(→ SRP 위반 신호)
필드 주입: 간편 ↔ 테스트 어려움, 불변성 보장 안 됨, 순환 참조 감지 어려움
REQUIRES_NEW: 독립 트랜잭션 ↔ 새 커넥션 점유 → 커넥션 풀 고갈 위험
NESTED: 같은 커넥션 → 풀 고갈 없음 ↔ Savepoint 지원 필요 + 부모 롤백 시 자식도 롤백
readOnly=true: 성능↑(더티 체킹 스킵) ↔ 실수로 쓰기 로직이 있으면 무시됨
@Cacheable: 조회 성능↑ ↔ 데이터 불일치, 캐시 관리 비용
WebFlux: 처리량↑(적은 스레드) ↔ 코드 복잡↑, 디버깅 어려움, JDBC 사용 불가
Auto Configuration: 설정 간편 ↔ 내부 동작 파악 어려움, 의도치 않은 빈 등록
@MockBean: 테스트 간편 ↔ Context 캐싱 깨짐 → 전체 테스트 느려짐
OSIV on: 뷰에서 지연 로딩 가능 ↔ DB 커넥션 오래 점유
```

## 설명 흐름

1. **왜 써야/알아야 하는가**: "내부를 모르면 이 트러블슈팅을 못 한다"
2. **비유로 직관 잡기**: 위 비유 활용
3. **"겉으로 보이는 동작" 빠르게 복습** (이미 아는 수준)
4. **"내부에서 일어나는 일" 설명** (프록시, 빈 후처리, 필터 체인 등)
```
요청 → DispatcherServlet → HandlerMapping → HandlerAdapter → Controller
                                                                    ↓
View ← ViewResolver ← DispatcherServlet ← HandlerAdapter ← Controller
```
5. **코드 예제 + "이러면 어떻게 되는가" 시나리오 + 트레이드오프**
```java
// 이 코드가 실행되면 Spring 내부에서 무슨 일이?
@Transactional
public void createOrder() {
    this.validateOrder(); // ← self-invocation!
}
// 트레이드오프: "해결하려면 별도 빈 분리 → 클래스 증가"
```
6. **오해하기 쉬운 부분 + 버전 차이**:
```
"@Transactional을 붙이면 무조건 롤백된다" → CheckedException은 기본 롤백 안 됨
"Spring Bean은 스레드 안전하다" → Singleton 기본이므로 상태 가지면 위험
"AOP는 모든 메서드에 적용된다" → 프록시 기반이라 self-invocation에서 안 먹힘
"Spring Boot = Spring" → Boot는 설정 자동화 도구. Framework 위에 동작
"@MockBean은 편리하다" → Context 캐싱 깨져서 테스트 전체 느려짐
"OSIV를 켜두면 편하다" → DB 커넥션을 뷰 렌더링까지 점유 → 커넥션 고갈 위험
Boot 2→3: javax.persistence → jakarta.persistence 패키지 변경
Security 5→6: WebSecurityConfigurerAdapter 삭제 → SecurityFilterChain 빈 방식
```
7. **확인 질문 (면접 형태)**: 사용자 답변 → 피드백
```
Step 1: "Spring Framework vs Spring Boot 차이는?"
Step 4: "IoC란 무엇이고 왜 필요한가?"
Step 5: "생성자 주입을 권장하는 이유 3가지는?"
Step 6: "Singleton 빈에 상태를 두면 왜 위험한가?"
Step 7: "AOP가 프록시 기반이라는 것이 무슨 의미? self-invocation 문제는?"
Step 9: "DispatcherServlet → Controller 전체 흐름을 그려보세요"
Step 11: "@Transactional이 내부적으로 어떻게 동작하는지 설명해보세요"
Step 12: "REQUIRES_NEW와 NESTED의 차이를 실제 시나리오로 설명해보세요"
Step 13: "readOnly=true의 효과는?"
Step 15: "Auto Configuration이 동작하는 원리는?"
Step 17: "Spring Security Filter Chain 동작 순서를 설명해보세요"
Step 19: "@TransactionalEventListener를 쓰는 이유는?"
Step 20: "Spring MVC vs WebFlux 선택 기준은?"
Step 21: "@WebMvcTest vs @SpringBootTest 차이는?"
```
8. **정리 + 다음 안내**

## Step별 특이사항

### 기초 (Step 1~3)
- Step 1 (Spring 개요): 레고 세트 비유. "왜 Spring인가" + Spring vs Boot 차이. 이미 아는 내용 빠르게
- Step 2 (프로젝트 구조): 회사 조직도(레이어드) 비유. @Controller/@Service/@Repository 역할 + DTO/Entity 분리
- Step 3 (Boot 기본): 호텔 체크인 비유. application.yml, 내장 서버, 실행 흐름

### 핵심 원리 (Step 4~8)
- Step 4 (IoC): 가구 배달 비유. **"왜 new 하면 안 되는가?"** → 결합도↑ 테스트 어려움
- Step 5 (DI): 이사 계약서(생성자) vs 마음대로(필드) 비유. **"생성자 주입을 권장하는 이유"가 면접 단골**
- Step 6 (빈 스코프): 공용 프린터(Singleton) 비유. **"Singleton에 상태를 두면?"** 시나리오 중심
- Step 7 (AOP): 비서(프록시) 비유. **self-invocation이 핵심**. "이 코드에서 @Transactional이 안 먹히는 이유" 시나리오. 순환 참조 + AOP 연계
- Step 8 (빈 후처리기): 택배 검수 센터 비유. "AOP 프록시가 여기서 생성된다"

### MVC (Step 9~10)
- Step 9 (MVC 내부): 호텔 프론트 데스크 비유. **DispatcherServlet 흐름 그림이 핵심**. ArgumentResolver, Filter vs Interceptor
- Step 10 (MVC 활용): REST API 설계 원칙(URI/HTTP 메서드/상태 코드). 예외 처리(@ControllerAdvice). Bean Validation

### 트랜잭션 (Step 11~13)
- Step 11 (원리): 은행 창구 비유. **"프록시가 트랜잭션을 감싸는 구조"** 그림. self-invocation과 동일 원리
- Step 12 (전파): REQUIRES_NEW(별도 창구) vs NESTED(중간 저장) 비유. **커넥션 풀 고갈 데드락 시나리오** 필수
- Step 13 (실전): "CheckedException이 왜 롤백 안 되는가?", readOnly, 긴 트랜잭션 위험, @Transactional + 외부 API 호출 주의

### DB 접근 (Step 14)
- Step 14: 수도관(DataSource) + 통역사(예외 추상화) 비유. HikariCP 설정. JdbcTemplate

### Boot (Step 15~16)
- Step 15 (Auto Configuration): 호텔 체크인 비유. @SpringBootApplication 분해. **exclude 실무 사례** (SecurityAutoConfiguration). Custom Starter 개념
- Step 16 (Actuator): 건강검진 키트 비유. /health, /metrics, /loggers. Micrometer + Prometheus 연동. 프로파일(dev/prod) 관리

### Security (Step 17~18)
- Step 17 (기초): **Filter Chain 흐름 그림이 핵심**. Authentication(인증) → Authorization(인가). SecurityContext(ThreadLocal)
- Step 18 (실전): JWT 발급→검증→갱신 전체 흐름. OAuth2 Authorization Code Grant. CORS(왜 Preflight?)/CSRF(JWT에서 왜 끄는가?)

### 이벤트 (Step 19)
- Step 19: 사내 게시판(이벤트) 비유. **@TransactionalEventListener(AFTER_COMMIT)이 왜 필요한가** = "결재 완료 전에 공지하면 안 됨". DDD 도메인 이벤트와 연결

### Reactive (Step 20)
- Step 20: 놀이공원 패스트패스(WebFlux) 비유. MVC(줄 서기, Blocking) vs WebFlux(패스트패스, Non-blocking). **"언제 WebFlux를 선택?"** → I/O Heavy + 높은 동시성. JDBC 사용 불가 제약

### 테스트 (Step 21)
- Step 21: 시뮬레이터(MockMvc) + 부분 시운전(@WebMvcTest) 비유. **@MockBean이 Context 캐싱을 깨뜨리는 이유**. 슬라이스 테스트 선택 기준. (테스트 학습 Step 11과 연계)

## 학습 방식 원칙
- 김영한 인프런 강의 참고 시: 강의 내용을 **보충/심화**하는 방향으로 설명 (중복 X)
- Spring 내부 코드를 직접 읽는 연습 유도 ("이 어노테이션의 소스를 열어보면?")
- 모든 Step에서 **"이러면 어떻게 되는가?"** 시나리오를 통해 내부 동작 체감
