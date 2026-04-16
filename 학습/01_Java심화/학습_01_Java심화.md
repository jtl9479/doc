# 학습 01. Java 심화 + Effective Java

## Step 목차

| Step | 항목 | 카테고리 |
|------|------|----------|
| Step 1 | Effective Java — 객체 생성과 파괴 | Effective Java |
| Step 2 | Effective Java — equals/hashCode/toString | Effective Java |
| Step 3 | Effective Java — 클래스 설계 원칙 | Effective Java |
| Step 4 | Effective Java — 제네릭 | Effective Java |
| Step 5 | Effective Java — 람다와 스트림 | Effective Java |
| Step 6 | Effective Java — 예외 | Effective Java |
| Step 7 | 동시성 — 스레드 기초 | 동시성 |
| Step 8 | 동시성 — synchronized와 가시성 | 동시성 |
| Step 9 | 동시성 — Lock과 Atomic | 동시성 |
| Step 10 | 동시성 — Executor와 동시성 컬렉션 | 동시성 |
| Step 11 | 동시성 — 데드락과 실전 패턴 | 동시성 |
| Step 12 | Virtual Thread + Java 21+ | 최신 기능 |
| Step 13 | JVM 메모리 + GC — 면접 대비 | JVM |
| Step 14 | 자료구조 — Java Collections 내부 구조 | 자료구조 |
| Step 15 | 병렬 — Parallel Stream + Fork/Join | 병렬 |
| Step 16 | I/O와 NIO 기본 개념 | I/O |

---

## 1. 개요

**현재 수준**: Java로 ERP 시스템 개발 중. 문법·API·Spring 연동은 실무 수준. 동시성·설계 원칙·JVM 내부는 깊이 부족.
**학습 목표**: Java 언어를 "쓸 수 있는" 수준에서 "왜 이렇게 써야 하는지 설명 가능한" 수준으로 끌어올린다.
**예상 시간**: 60시간
**분기 배정**: 1분기 (2026.04 ~ 2026.06)

---

## 2. 학습 순서 + 세부 항목

---

### Step 1. Effective Java — 객체 생성과 파괴

| 아이템 | 학습 목표 |
|--------|----------|
| Item 1: 생성자 대신 정적 팩토리 메서드를 고려하라 | 정적 팩토리 메서드의 장점 4가지(이름 부여, 인스턴스 캐싱, 하위 타입 반환, 입력 매개변수에 따른 다른 클래스 반환)를 설명 가능. 단점(상속 불가, 문서화 어려움)도 설명 가능. `of()`, `valueOf()`, `getInstance()` 등 네이밍 관례를 알고 사용 가능. |
| Item 2: 생성자에 매개변수가 많다면 빌더를 고려하라 | 점층적 생성자 패턴 → 자바빈즈 패턴 → 빌더 패턴의 진화 과정과 각각의 문제점을 설명 가능. 빌더 패턴을 직접 구현 가능. Lombok @Builder와의 관계 설명 가능. |
| Item 3: private 생성자나 열거 타입으로 싱글턴임을 보증하라 | 싱글턴 구현 3가지(public static final 필드, 정적 팩토리, enum) 방식과 각각의 트레이드오프(직렬화, 리플렉션 방어, 테스트 용이성) 설명 가능. |
| Item 5: 자원을 직접 명시하지 말고 의존 객체 주입을 사용하라 | 의존 객체 주입의 장점(유연성, 테스트 용이성)을 설명 가능. Spring DI와의 관계 설명 가능. |
| Item 7: 다 쓴 객체 참조를 해제하라 | 메모리 누수가 발생하는 3가지 상황(자기 메모리를 직접 관리하는 클래스, 캐시, 리스너/콜백)을 식별 가능. WeakReference/WeakHashMap의 역할 설명 가능. |

---

### Step 2. Effective Java — equals/hashCode/toString

| 아이템 | 학습 목표 |
|--------|----------|
| Item 10: equals는 일반 규약을 지켜 재정의하라 | equals 규약 4가지(반사성, 대칭성, 추이성, 일관성)를 각각 설명 + 위반 사례 코드를 보고 문제 식별 가능. equals를 재정의하지 않아도 되는 경우(인스턴스가 고유, 논리적 동치 불필요, 상위 클래스 equals가 적절) 판단 가능. |
| Item 11: equals를 재정의하려거든 hashCode도 재정의하라 | equals가 같은 두 객체는 hashCode도 같아야 하는 이유(HashMap/HashSet 정상 동작)를 설명 가능. hashCode 구현 방법(Objects.hash, 직접 계산)과 성능 트레이드오프 설명 가능. |
| Item 12: toString을 항상 재정의하라 | 디버깅·로깅에서 toString의 중요성을 설명 가능. 어떤 정보를 포함해야 하는지 판단 가능. |

---

### Step 3. Effective Java — 클래스 설계 원칙

| 아이템 | 학습 목표 |
|--------|----------|
| Item 15: 클래스와 멤버의 접근 권한을 최소화하라 | 정보 은닉의 장점(모듈 간 의존성 감소, 병렬 개발, 성능 최적화 여지)을 설명 가능. public 클래스의 인스턴스 필드는 왜 public이면 안 되는지 설명 가능. |
| Item 16: public 클래스에서는 public 필드가 아닌 접근자 메서드를 사용하라 | 캡슐화가 깨지는 구체적 사례를 설명 가능. |
| Item 17: 변경 가능성을 최소화하라 (불변 클래스) | 불변 클래스의 장점 5가지(단순성, 스레드 안전, 자유로운 공유, 실패 원자성, 방어적 복사 불필요)를 설명 가능. 불변 클래스를 만드는 5가지 규칙을 적용 가능. String이 불변인 이유를 설명 가능. |
| Item 18: 상속보다는 컴포지션을 사용하라 | 상속의 문제점(캡슐화 깨짐, 상위 클래스 변경에 취약)을 구체적 사례로 설명 가능. 컴포지션 + 전달(Forwarding) 방식으로 동일 기능을 구현 가능. 데코레이터 패턴과의 관계 설명 가능. |
| Item 20: 추상 클래스보다는 인터페이스를 우선하라 | 인터페이스의 장점(다중 구현, 믹스인, 타입 프레임워크)을 설명 가능. 인터페이스의 default 메서드 활용법과 제약사항을 설명 가능. 추상 골격 구현(skeletal implementation) 패턴을 설명 가능. |
| Item 22: 인터페이스는 타입을 정의하는 용도로만 사용하라 | 상수 인터페이스 안티패턴이 왜 나쁜지 설명 가능. |

---

### Step 4. Effective Java — 제네릭

| 아이템 | 학습 목표 |
|--------|----------|
| Item 26: 로 타입은 사용하지 말라 | `List`(로 타입) vs `List<Object>` vs `List<?>` 의 차이를 설명 가능. 로 타입을 쓰면 컴파일 시점에 타입 안전성을 잃는 이유를 설명 가능. |
| Item 28: 배열보다는 리스트를 사용하라 | 배열은 공변(covariant)이고 제네릭은 불공변(invariant)인 차이를 설명 가능. `Object[]`에 String을 넣는 것과 `List<Object>`에 String을 넣는 것의 차이를 설명 가능. |
| Item 29: 이왕이면 제네릭 타입으로 만들라 | 기존 클래스를 제네릭으로 변환하는 방법을 적용 가능. |
| Item 31: 한정적 와일드카드를 사용해 API 유연성을 높이라 | PECS(Producer-Extends, Consumer-Super) 원칙을 설명 + 실제 코드에 적용 가능. `<? extends E>` vs `<? super E>` 를 상황에 맞게 선택 가능. |

---

### Step 5. Effective Java — 람다와 스트림

| 아이템 | 학습 목표 |
|--------|----------|
| Item 42: 익명 클래스보다는 람다를 사용하라 | 람다가 적합한 경우와 익명 클래스가 여전히 필요한 경우(this 참조, 추상 클래스 구현)를 구분 가능. |
| Item 43: 람다보다는 메서드 참조를 사용하라 | 메서드 참조 5가지 유형(정적, 한정적 인스턴스, 비한정적 인스턴스, 클래스 생성자, 배열 생성자)을 설명 가능. |
| Item 45: 스트림은 주의해서 사용하라 | 스트림이 적합한 경우(변환, 필터링, 결합, 수집, 검색)와 부적합한 경우(반복문 안에서 변수 변경, break/continue, checked 예외)를 판단 가능. |
| Item 46: 스트림에서는 부작용 없는 함수를 사용하라 | forEach를 계산에 쓰면 안 되는 이유 설명 가능. Collectors(toList, toSet, toMap, groupingBy, joining)를 적절히 활용 가능. |
| Item 55: 옵셔널 반환은 신중히 하라 | Optional을 반환해야 하는 경우(결과 없음이 가능한 메서드)와 쓰면 안 되는 경우(컬렉션 반환, 필드, 맵 값, 기본 타입)를 판단 가능. `OptionalInt`, `OptionalLong` 의 존재 이유 설명 가능. |

---

### Step 6. Effective Java — 예외

| 아이템 | 학습 목표 |
|--------|----------|
| Item 69: 예외는 진짜 예외 상황에만 사용하라 | 예외를 흐름 제어에 사용하면 안 되는 이유(성능, 가독성, 버그 은폐)를 설명 가능. |
| Item 70: 복구할 수 있는 상황에는 검사 예외를, 프로그래밍 오류에는 런타임 예외를 사용하라 | checked vs unchecked 예외의 선택 기준을 설명 가능. |
| Item 73: 추상화 수준에 맞는 예외를 던져라 | 예외 번역(exception translation)과 예외 연쇄(exception chaining)의 개념 + 적용 가능. |
| Item 77: 예외를 무시하지 말라 | catch 블록을 비워두면 안 되는 이유를 설명 가능. 무시해도 되는 드문 경우(예: FileInputStream.close)의 판단 기준 설명 가능. |

---

### Step 7. 동시성 — 스레드 기초

**학습 수단**: 김영한 자바 고급 1 (멀티스레드와 동시성) 참고 + Claude 질의

| 학습 항목 | 학습 목표 |
|----------|----------|
| 스레드 생성 (Thread, Runnable) | Thread 상속 vs Runnable 구현의 차이와 왜 Runnable이 더 좋은지 설명 가능. |
| 스레드 생명주기 | NEW → RUNNABLE → (BLOCKED/WAITING/TIMED_WAITING) → TERMINATED 각 상태와 전이 조건을 설명 가능. |
| join, sleep, interrupt | 각 메서드의 동작과 InterruptedException 처리 방법을 설명 가능. interrupt 메커니즘(인터럽트 플래그)의 동작 원리 설명 가능. |
| 데몬 스레드 vs 사용자 스레드 | 차이점과 데몬 스레드의 용도를 설명 가능. |

---

### Step 8. 동시성 — synchronized와 가시성

| 학습 항목 | 학습 목표 |
|----------|----------|
| 공유 자원과 임계 영역 | race condition이 발생하는 3가지 조건(공유 자원 + 변경 + 동시 접근)을 설명 가능. 구체적 코드에서 race condition을 30초 내 식별 가능. |
| synchronized (메서드, 블록) | 모니터 락의 동작 원리(객체마다 모니터 1개)를 설명 가능. 메서드 동기화 vs 블록 동기화의 차이와 선택 기준 설명 가능. 재진입(reentrant) 가능한 이유 설명 가능. |
| volatile | CPU 캐시로 인한 가시성(visibility) 문제가 뭔지 설명 가능. volatile이 해결하는 것(가시성)과 해결 못 하는 것(원자성, 복합 연산)을 구분 가능. "volatile로 충분한 경우"와 "synchronized가 필요한 경우"를 판단 가능. |
| happens-before 관계 | Java Memory Model에서 happens-before의 의미를 개념 수준으로 설명 가능. |

---

### Step 9. 동시성 — Lock과 Atomic

| 학습 항목 | 학습 목표 |
|----------|----------|
| ReentrantLock | synchronized와의 차이 5가지(tryLock, 타임아웃, 공정성, Condition, 인터럽트 가능)를 설명 가능. 언제 synchronized 대신 ReentrantLock을 선택하는지 판단 가능. lock/unlock을 try-finally로 감싸야 하는 이유 설명 가능. |
| ReadWriteLock | 읽기-읽기는 허용, 읽기-쓰기/쓰기-쓰기는 배타적인 동작을 설명 가능. 읽기가 많은 상황에서 성능 이점 설명 가능. |
| CAS (Compare-And-Swap) | CAS의 동작 원리(기대값 비교 → 일치하면 교체)를 설명 가능. 낙관적 락과의 관계 설명 가능. ABA 문제를 설명 가능. |
| AtomicInteger, AtomicReference 등 | Atomic 클래스의 내부 동작(CAS 기반)을 설명 가능. incrementAndGet vs getAndIncrement 차이 설명 가능. synchronized 대신 Atomic을 쓸 수 있는 조건(단일 변수의 원자적 연산) 설명 가능. |

---

### Step 10. 동시성 — Executor와 동시성 컬렉션

| 학습 항목 | 학습 목표 |
|----------|----------|
| Executor / ExecutorService | 스레드를 직접 생성하면 안 되는 이유(Effective Java Item 80)를 설명 가능. submit vs execute 차이 설명 가능. shutdown vs shutdownNow 차이 설명 가능. |
| 스레드 풀 종류 | FixedThreadPool, CachedThreadPool, ScheduledThreadPool, SingleThreadExecutor 각각의 특징과 선택 기준 설명 가능. 왜 Executors.newCachedThreadPool()이 프로덕션에서 위험한지 설명 가능. |
| Future / CompletableFuture | Future의 한계(블로킹 get, 조합 불가)를 설명 가능. CompletableFuture의 thenApply/thenCompose/thenCombine 차이 설명 가능. |
| ConcurrentHashMap | HashMap과의 차이(세그먼트/노드 단위 락), 왜 HashTable 대신 쓰는지 설명 가능. ConcurrentHashMap에서 복합 연산(putIfAbsent, computeIfAbsent)을 써야 하는 이유 설명 가능. |
| BlockingQueue | put/take의 블로킹 동작을 설명 가능. 프로듀서-컨슈머 패턴에서의 활용 설명 가능. |

---

### Step 11. 동시성 — 데드락과 실전 패턴

| 학습 항목 | 학습 목표 |
|----------|----------|
| 데드락 (Deadlock) | 발생 조건 4가지(상호배제, 점유대기, 비선점, 순환대기)를 설명 가능. 코드를 보고 데드락 가능성을 식별 가능. 데드락 방지 전략(락 순서 고정, tryLock 타임아웃, 락 계층화)을 설명 + 적용 가능. |
| 라이브락 / 기아 상태 | 데드락과의 차이를 설명 가능. |
| Effective Java Item 78~84 동시성 | Item 78: 공유 중인 가변 데이터는 동기화해 사용하라. Item 79: 과도한 동기화는 피하라 (동기화 블록 안에서 외부 메서드 호출 위험). Item 80: 스레드보다는 실행자, 태스크, 스트림을 애용하라. Item 81: wait/notify 대신 동시성 유틸리티를 애용하라. 각 아이템의 핵심 교훈을 설명 가능. |
| 스레드 안전한 설계 원칙 | 불변 객체 활용, 스레드 로컬(ThreadLocal), 동기화 범위 최소화 등 원칙을 설명 + 코드에 적용 가능. |

---

### Step 12. Virtual Thread + Java 21+

| 학습 항목 | 학습 목표 |
|----------|----------|
| Virtual Thread 개요 | Platform Thread와의 차이(커널 스레드 vs 캐리어 스레드 위 경량 스레드)를 설명 가능. |
| Virtual Thread가 유리한 경우 | I/O bound 작업에서 처리량 향상 원리를 설명 가능. CPU bound에서는 효과 없는 이유 설명 가능. |
| Virtual Thread Pinning (심화) | Pinning이 발생하는 메커니즘(가상 스레드가 synchronized 진입 시 carrier thread에 고정 → carrier thread가 블로킹 → 다른 가상 스레드 스케줄링 불가 → 처리량 급락)을 설명 가능. ReentrantLock이 pinning을 유발하지 않는 이유(park/unpark 기반으로 carrier thread 해제 가능)를 설명 가능. 실무에서 synchronized → ReentrantLock 전환 판단 기준 설명 가능. |
| Virtual Thread 기타 주의점 | ThreadLocal 사용 시 주의점(가상 스레드 수백만 개 × ThreadLocal = 메모리 폭발)을 설명 가능. |
| Virtual Thread 사용법 | `Thread.ofVirtual().start()`, `Executors.newVirtualThreadPerTaskExecutor()` 사용 가능. |
| Record | DTO/값 객체에 적합한 이유, 일반 클래스와의 차이(자동 equals/hashCode/toString, final 필드), 제약사항(상속 불가, 필드 변경 불가)을 설명 가능. |
| Sealed Class | sealed/permits의 의미, 허용된 하위 클래스만 존재하는 패턴, switch 패턴 매칭과의 조합을 설명 가능. |
| Pattern Matching | instanceof 패턴 매칭, switch 식에서의 패턴 매칭 코드를 읽고 작성 가능. |

---

### Step 13. JVM 메모리 + GC — 면접 대비

| 학습 항목 | 학습 목표 |
|----------|----------|
| JVM 메모리 구조 | Heap(Young Generation: Eden + Survivor0 + Survivor1 / Old Generation), Stack(스레드별), Metaspace(클래스 메타데이터), PC Register를 그림으로 그리며 각 영역의 역할 설명 가능. |
| 객체 생명주기 | 객체 생성(Eden) → Minor GC로 Survivor 이동 → age 증가 → Old Generation 승격 과정 설명 가능. |
| GC 동작 원리 | Mark-Sweep(-Compact) 알고리즘의 동작을 설명 가능. STW(Stop-The-World)가 왜 발생하는지, 왜 줄여야 하는지 설명 가능. Minor GC vs Major GC(Full GC) 차이 설명 가능. |
| Serial GC | 단일 스레드, 작은 힙에 적합, STW 길다. 설명 가능. |
| Parallel GC | 멀티 스레드, 처리량(Throughput) 우선, STW 있음. 설명 가능. |
| G1 GC | Region 기반, 예측 가능한 STW 목표(-XX:MaxGCPauseMillis), Mixed GC 개념을 설명 가능. Java 9+ 기본 GC. |
| ZGC | Colored Pointer, Load Barrier, STW 거의 없음(수 ms 이내), 대용량 힙(TB급)에 적합. 설명 가능. G1과의 차이/선택 기준 설명 가능. |
| OOM 원인과 대응 | `java.lang.OutOfMemoryError: Java heap space` (힙 부족), `Metaspace` (클래스 메타 부족), `unable to create native thread` (스레드 생성 실패) 각각의 원인과 대응법(Heap Dump 분석, GC 로그 확인) 설명 가능. |
| JVM Safe Point (심화) | Safe Point의 정의(JVM이 모든 스레드를 안전하게 멈출 수 있는 지점)를 설명 가능. GC 외에 Safe Point가 발생하는 경우(Biased Locking Revocation, Deoptimization, Thread Dump 등)를 설명 가능. Safe Point 지연이 응답 시간 스파이크를 유발하는 메커니즘(Counted Loop 등에서 Safe Point 체크 안 함 → 다른 스레드 전부 대기)을 설명 가능. `-XX:+PrintSafepointStatistics`로 진단 가능함을 알고 있음. |

---

### Step 14. 자료구조 — Java Collections 내부 구조

| 학습 항목 | 학습 목표 |
|----------|----------|
| **HashMap 내부 구조** | 버킷 배열 + 해시 함수 → 인덱스 계산 과정을 설명 가능. 해시 충돌 해결(체이닝)을 설명 가능. Java 8에서 버킷 내 노드 8개 초과 시 LinkedList → Red-Black Tree로 변환되는 이유(성능: O(n)→O(log n))를 설명 가능. load factor(0.75)와 rehashing(용량 2배 확장) 동작을 설명 가능. |
| **HashMap vs HashTable vs ConcurrentHashMap** | HashTable은 왜 쓰지 않는지(전체 락, 성능 저하), ConcurrentHashMap의 동시성 전략(노드 단위 락)과의 차이를 설명 가능. |
| **ArrayList 내부** | Object[] 배열 기반, 기본 용량(10), 확장 시 1.5배 복사, 인덱스 접근 O(1), 삽입/삭제 O(n)을 설명 가능. |
| **LinkedList 내부** | 이중 연결 리스트 구조, 삽입/삭제 O(1)(노드 접근 후), 인덱스 접근 O(n)을 설명 가능. |
| **ArrayList vs LinkedList 선택 기준** | 대부분의 경우 ArrayList가 유리한 이유를 설명 가능. LinkedList가 적합한 드문 경우(앞/뒤 삽입 삭제만 반복)를 설명 가능. |
| **CPU Cache Locality (심화)** | CPU L1/L2/L3 캐시의 동작 원리(캐시 라인 64바이트 단위 로드)를 설명 가능. ArrayList가 연속 메모리 할당(Object[] 배열)이므로 순차 접근 시 캐시 히트율이 높은 이유를 설명 가능. LinkedList는 노드가 힙 전체에 흩어져 있어 포인터를 따라갈 때마다 캐시 미스가 발생하는 이유를 설명 가능. 이론적 시간 복잡도(O(1) 삽입)보다 실제 성능에서 ArrayList가 우수한 이유를 하드웨어 관점에서 설명 가능. |
| **TreeMap** | Red-Black Tree 기반, 키 정렬 보장, 시간 복잡도 O(log n), 언제 HashMap 대신 쓰는지(범위 검색, 정렬 필요) 설명 가능. |
| **LinkedHashMap** | 삽입 순서 또는 접근 순서 보장, LRU 캐시 구현에 활용 가능한 이유를 설명 가능. |
| **HashSet 내부** | HashMap을 내부적으로 사용(value는 더미 객체)하는 구조를 설명 가능. |
| **PriorityQueue** | 힙(Heap) 기반, 최소값/최대값 빠른 추출 O(log n), 정렬이 아닌 우선순위 보장임을 설명 가능. |
| **ArrayDeque** | 양방향 큐, Stack/Queue 대체 가능, LinkedList보다 성능 우수한 이유를 설명 가능. |
| **불변 컬렉션** | `List.of()`, `Map.of()`, `Collections.unmodifiableList()`의 차이와 방어적 복사와의 관계를 설명 가능. |

---

### Step 15. 병렬 — Parallel Stream + Fork/Join

| 학습 항목 | 학습 목표 |
|----------|----------|
| **Concurrency vs Parallelism** | 동시성(하나의 코어에서 번갈아 실행)과 병렬성(여러 코어에서 동시 실행)의 차이를 설명 가능. |
| **Parallel Stream** | `parallelStream()`의 내부 동작(ForkJoinPool.commonPool 사용)을 설명 가능. |
| **Parallel Stream 주의사항** | 공유 가변 상태에서의 위험(race condition), 순서 보장 안 됨, 작은 데이터에서 오히려 느린 이유(스레드 생성 오버헤드), I/O 작업에 부적합한 이유를 설명 가능. |
| **Parallel Stream을 써야 할 때 / 쓰지 말아야 할 때** | 데이터가 충분히 크고 + 순수 CPU 연산이고 + 순서가 중요하지 않은 경우에 유리함을 판단 가능. |
| **Fork/Join Framework** | ForkJoinPool, RecursiveTask, RecursiveAction의 역할을 설명 가능. work-stealing 알고리즘의 동작 원리를 설명 가능. |
| **커스텀 ForkJoinPool** | commonPool 대신 별도 ForkJoinPool을 만들어야 하는 경우(다른 병렬 작업에 영향 방지)를 설명 가능. |

---

### Step 16. I/O와 NIO 기본 개념

| 학습 항목 | 학습 목표 |
|----------|----------|
| **Java I/O 기본** | InputStream/OutputStream(바이트 기반), Reader/Writer(문자 기반)의 차이를 설명 가능. try-with-resources를 사용하는 이유(자원 누수 방지)를 설명 가능. |
| **Buffered I/O** | BufferedReader/BufferedWriter를 쓰는 이유(시스템 콜 횟수 감소, 성능 향상)를 설명 가능. |
| **NIO 핵심 개념** | Buffer, Channel, Selector의 역할과 기존 I/O와의 차이를 설명 가능. |
| **Blocking I/O vs Non-blocking I/O** | 블로킹 모델(스레드가 I/O 완료까지 대기)과 논블로킹 모델(즉시 반환, 준비되면 알림)의 차이를 설명 가능. Spring MVC(블로킹) vs Spring WebFlux(논블로킹)의 내부 차이와 연결하여 설명 가능. |
| **NIO.2 (Path, Files)** | `Path`, `Files.readAllLines()`, `Files.walk()` 등 현대 Java 파일 처리 API 사용 가능. 기존 `File` 클래스 대비 장점을 설명 가능. |
| **직렬화** | Java Serialization의 문제점(보안, 호환성, Effective Java Item 85~90)을 설명 가능. JSON 직렬화(Jackson ObjectMapper)를 대안으로 설명 가능. |

---

## 3. 자가 검증

### Effective Java
- [ ] 핵심 아이템 20개+ 각각 "왜 이렇게 해야 하는가" 1분 이내 설명 가능
- [ ] 자기 코드에서 해당 패턴 적용 사례 10건+ 식별 또는 리팩토링 완료
- [ ] "정적 팩토리 메서드의 장점 4가지" 즉시 답변 가능
- [ ] "상속 대신 컴포지션을 쓰는 이유" 구체적 사례로 설명 가능
- [ ] "PECS 원칙이란?" 설명 + 코드 적용 가능

### 동시성
- [ ] "synchronized vs ReentrantLock 차이와 선택 기준" 3분 설명 가능
- [ ] "volatile은 왜 원자성을 보장하지 못하는가" 설명 가능
- [ ] race condition이 있는 코드를 주면 30초 내 식별 가능
- [ ] deadlock 발생 조건 4가지 즉시 답변 가능
- [ ] "ConcurrentHashMap은 왜 HashMap보다 스레드 안전한가" 설명 가능
- [ ] CompletableFuture의 thenApply vs thenCompose 차이 설명 가능

### Virtual Thread + Java 21+
- [ ] "Virtual Thread와 Platform Thread의 차이" 3분 설명 가능
- [ ] "가상 스레드에서 synchronized를 쓰면 왜 문제인가?" → carrier thread 고정 → 처리량 급락 메커니즘 답변 가능
- [ ] "ReentrantLock은 왜 pinning이 안 되는가?" → park/unpark 기반 carrier thread 해제 설명 가능
- [ ] "Record를 언제 쓰고 안 쓰는가" 설명 가능
- [ ] Sealed Class + Pattern Matching 코드를 읽고 이해 가능

### JVM / GC
- [ ] "JVM 메모리 구조를 그려보세요" → 30초 내 그림 + 1분 설명 가능
- [ ] "G1GC와 ZGC의 차이" → 핵심 차이 3가지 즉시 답변 가능
- [ ] "OOM이 발생하면 어떻게 대응하나요?" → Heap Dump 분석 → GC 로그 → 메모리 누수 추적 순서 답변 가능
- [ ] "Minor GC와 Major GC의 차이" 설명 가능
- [ ] "GC 외에 응답 시간이 튀는 JVM 내부 원인은?" → Safe Point 지연 답변 가능

### 자료구조
- [ ] "HashMap의 내부 구조를 설명하라" → 버킷 + 해시 함수 + 충돌 해결 + Java 8 트리화 즉시 답변 가능
- [ ] "HashMap의 load factor가 0.75인 이유" 설명 가능
- [ ] "이론상 LinkedList 삽입이 O(1)인데 실무에서 ArrayList가 더 빠른 이유는?" → 캐시 라인, 연속 메모리, 캐시 미스 답변 가능
- [ ] "ArrayList vs LinkedList 어떤 걸 선택하는가?" → 대부분 ArrayList, 하드웨어 관점 근거 포함 답변 가능
- [ ] "TreeMap은 언제 쓰는가?" 설명 가능
- [ ] "LinkedHashMap으로 LRU 캐시를 어떻게 구현하는가?" 설명 가능

### 병렬
- [ ] "Concurrency와 Parallelism의 차이" 즉시 답변 가능
- [ ] "Parallel Stream을 쓰면 안 되는 경우 3가지" 즉시 답변 가능
- [ ] "Fork/Join의 work-stealing 알고리즘" 설명 가능

### I/O / NIO
- [ ] "Blocking I/O와 Non-blocking I/O의 차이" 설명 가능
- [ ] "NIO의 Buffer, Channel, Selector 역할" 각각 설명 가능
- [ ] "Java Serialization의 문제점과 대안" 설명 가능

---

## 4. 진행 상태

| Step | 항목 | 상태 |
|------|------|------|
| Step 1 | Effective Java — 객체 생성과 파괴 | 미시작 |
| Step 2 | Effective Java — equals/hashCode/toString | 미시작 |
| Step 3 | Effective Java — 클래스 설계 원칙 | 미시작 |
| Step 4 | Effective Java — 제네릭 | 미시작 |
| Step 5 | Effective Java — 람다와 스트림 | 미시작 |
| Step 6 | Effective Java — 예외 | 미시작 |
| Step 7 | 동시성 — 스레드 기초 | 미시작 |
| Step 8 | 동시성 — synchronized와 가시성 | 미시작 |
| Step 9 | 동시성 — Lock과 Atomic | 미시작 |
| Step 10 | 동시성 — Executor와 동시성 컬렉션 | 미시작 |
| Step 11 | 동시성 — 데드락과 실전 패턴 | 미시작 |
| Step 12 | Virtual Thread + Java 21+ | 미시작 |
| Step 13 | JVM 메모리 + GC — 면접 대비 | 미시작 |
| Step 14 | 자료구조 — Java Collections 내부 구조 | 미시작 |
| Step 15 | 병렬 — Parallel Stream + Fork/Join | 미시작 |
| Step 16 | I/O와 NIO 기본 개념 | 미시작 |

---

## 5. 참고 자료 (보조용)

| 자료 | 용도 |
|------|------|
| Effective Java 3rd Edition (Joshua Bloch) | Step 1~6 보조. 해당 아이템 원문 참조 시 |
| 김영한 자바 고급 1 (인프런) | Step 7~11 보조. 동시성 강의 참고 시 |
| Oracle Java Documentation | Virtual Thread, Record 등 최신 기능 공식 문서 |
| Baeldung (baeldung.com) | 항목별 실습 예제 참고 시 |

---

> 이 문서는 Claude가 미래 세션에서 읽고 학습을 안내하기 위한 가이드입니다.
> 사용자가 "Java 공부하자"라고 하면, 진행 상태를 확인하고 다음 미시작 Step부터 진행합니다.
> 각 Step의 학습 목표를 기준으로 설명하고, 자가 검증 질문으로 이해도를 확인합니다.
