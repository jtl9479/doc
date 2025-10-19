# 47장 Virtual Threads - Part 3: 성능 최적화 & 고급 활용

## 📚 목차
1. [성능 분석 & 최적화](#성능-분석-최적화)
2. [고급 활용 기법](#고급-활용-기법)
3. [자주 묻는 면접 질문 TOP 10](#면접-질문)
4. [종합 정리](#종합-정리)

---

## 🚀 성능 분석 & 최적화

### 📊 Virtual Thread 성능 측정

```java
package virtualthread.performance;

import java.util.concurrent.*;
import java.util.stream.IntStream;

/**
 * Virtual Thread 성능 벤치마크
 */
public class PerformanceBenchmark {
    private static final int TASK_COUNT = 100_000;

    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== Virtual Thread 성능 벤치마크 ===\n");

        // 1. 생성 비용
        System.out.println("📍 테스트 1: 스레드 생성 비용");
        testCreationCost();

        // 2. 메모리 사용량
        System.out.println("\n📍 테스트 2: 메모리 사용량");
        testMemoryUsage();

        // 3. 컨텍스트 스위칭
        System.out.println("\n📍 테스트 3: 컨텍스트 스위칭");
        testContextSwitching();
    }

    /**
     * 생성 비용 테스트
     */
    static void testCreationCost() {
        // Platform Thread
        long start1 = System.nanoTime();
        for (int i = 0; i < 10_000; i++) {
            Thread thread = new Thread(() -> {});
            // 실제 시작은 하지 않음 (생성 비용만 측정)
        }
        long end1 = System.nanoTime();
        double platformTime = (end1 - start1) / 1_000_000.0;

        // Virtual Thread
        long start2 = System.nanoTime();
        for (int i = 0; i < 10_000; i++) {
            Thread.ofVirtual().unstarted(() -> {});
        }
        long end2 = System.nanoTime();
        double virtualTime = (end2 - start2) / 1_000_000.0;

        System.out.println("Platform Thread: " +
            String.format("%.2f", platformTime) + "ms");
        System.out.println("Virtual Thread: " +
            String.format("%.2f", virtualTime) + "ms");
        System.out.println("→ Virtual Thread가 " +
            String.format("%.1f", platformTime / virtualTime) + "배 빠름");
    }

    /**
     * 메모리 사용량 테스트
     */
    static void testMemoryUsage() {
        Runtime runtime = Runtime.getRuntime();

        // GC 실행
        System.gc();
        long beforeMemory = runtime.totalMemory() - runtime.freeMemory();

        // Virtual Thread 10만 개 생성
        Thread[] threads = new Thread[TASK_COUNT];
        for (int i = 0; i < TASK_COUNT; i++) {
            threads[i] = Thread.ofVirtual().unstarted(() -> {
                try {
                    Thread.sleep(10000);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            });
            threads[i].start();
        }

        System.gc();
        long afterMemory = runtime.totalMemory() - runtime.freeMemory();
        long usedMemory = (afterMemory - beforeMemory) / 1024 / 1024;

        System.out.println("10만 개 Virtual Thread 메모리 사용:");
        System.out.println("  총 메모리: " + usedMemory + "MB");
        System.out.println("  평균: " + (usedMemory * 1024.0 / TASK_COUNT) + "KB per thread");

        // 정리
        for (var thread : threads) {
            thread.interrupt();
        }
    }

    /**
     * 컨텍스트 스위칭 테스트
     */
    static void testContextSwitching() throws InterruptedException {
        int iterations = 10_000;

        // Platform Thread Pool
        try (var executor = Executors.newFixedThreadPool(100)) {
            long start = System.currentTimeMillis();

            var futures = IntStream.range(0, iterations)
                .mapToObj(i -> executor.submit(() -> {
                    try {
                        Thread.sleep(1);
                    } catch (InterruptedException e) {
                        throw new RuntimeException(e);
                    }
                }))
                .toList();

            for (var future : futures) {
                try {
                    future.get();
                } catch (ExecutionException e) {
                    // 에러 처리
                }
            }

            long duration = System.currentTimeMillis() - start;
            System.out.println("Platform Thread Pool: " + duration + "ms");
        }

        // Virtual Thread
        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
            long start = System.currentTimeMillis();

            var futures = IntStream.range(0, iterations)
                .mapToObj(i -> executor.submit(() -> {
                    try {
                        Thread.sleep(1);
                    } catch (InterruptedException e) {
                        throw new RuntimeException(e);
                    }
                }))
                .toList();

            for (var future : futures) {
                try {
                    future.get();
                } catch (ExecutionException e) {
                    // 에러 처리
                }
            }

            long duration = System.currentTimeMillis() - start;
            System.out.println("Virtual Thread: " + duration + "ms");
        }
    }
}
```

---

## 💎 고급 활용 기법

### 🔷 기법 1: Structured Concurrency (Preview)

```java
package virtualthread.advanced;

import java.util.concurrent.*;

/**
 * Structured Concurrency (구조화된 동시성)
 * Java 21 Preview Feature
 */
public class StructuredConcurrencyDemo {

    /**
     * 여러 작업을 구조화하여 실행
     */
    static String fetchUserData(String userId) throws ExecutionException, InterruptedException {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {

            // 병렬로 여러 작업 실행
            Future<String> userInfo = scope.fork(() -> fetchUserInfo(userId));
            Future<String> orderHistory = scope.fork(() -> fetchOrderHistory(userId));
            Future<String> preferences = scope.fork(() -> fetchPreferences(userId));

            // 모든 작업 완료 대기
            scope.join();
            scope.throwIfFailed();

            // 결과 조합
            return String.format("User: %s, Orders: %s, Preferences: %s",
                userInfo.resultNow(),
                orderHistory.resultNow(),
                preferences.resultNow()
            );
        }
    }

    static String fetchUserInfo(String userId) {
        sleep(100);
        return "UserInfo-" + userId;
    }

    static String fetchOrderHistory(String userId) {
        sleep(150);
        return "OrderHistory-" + userId;
    }

    static String fetchPreferences(String userId) {
        sleep(80);
        return "Preferences-" + userId;
    }

    static void sleep(long millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }

    public static void main(String[] args) throws ExecutionException, InterruptedException {
        System.out.println("=== Structured Concurrency ===\n");

        long start = System.currentTimeMillis();
        String result = fetchUserData("USER123");
        long duration = System.currentTimeMillis() - start;

        System.out.println(result);
        System.out.println("소요 시간: " + duration + "ms");
        System.out.println("(순차 실행: 330ms, 병렬 실행: ~150ms)");
    }
}
```

### 🔷 기법 2: Scoped Values (Preview)

```java
package virtualthread.advanced;

/**
 * Scoped Values
 * ThreadLocal의 대안
 */
public class ScopedValuesDemo {

    // Scoped Value 선언
    private static final ScopedValue<String> USER_ID = ScopedValue.newInstance();
    private static final ScopedValue<String> REQUEST_ID = ScopedValue.newInstance();

    public static void main(String[] args) {
        System.out.println("=== Scoped Values ===\n");

        // Scoped Value 설정
        ScopedValue.where(USER_ID, "USER123")
            .where(REQUEST_ID, "REQ456")
            .run(() -> {
                processRequest();
            });
    }

    static void processRequest() {
        System.out.println("User ID: " + USER_ID.get());
        System.out.println("Request ID: " + REQUEST_ID.get());

        // 중첩 스코프
        ScopedValue.where(USER_ID, "ADMIN")
            .run(() -> {
                System.out.println("Admin User ID: " + USER_ID.get());
            });

        // 원래 값으로 복원됨
        System.out.println("User ID: " + USER_ID.get());
    }
}
```

---

## 🎤 면접 질문

### ❓ Q1. Virtual Thread란 무엇인가?

**답변**:
```
Virtual Thread는 Java 21에서 도입된 경량 스레드입니다.

특징:
1. 경량성
   - Platform Thread: ~1MB
   - Virtual Thread: ~1KB

2. 생성 비용
   - 매우 낮음
   - 수백만 개 생성 가능

3. 스케줄링
   - JVM이 관리
   - OS 스레드와 독립적

4. 블로킹 처리
   - I/O 대기 시 자동 양보
   - Platform Thread 효율적 사용

사용법:
Thread virtual = Thread.startVirtualThread(() -> {
    // 작업
});

장점:
- 높은 동시성
- 낮은 메모리 사용
- 간단한 코드 (Thread API 동일)

적합한 작업:
- HTTP 요청
- 데이터베이스 쿼리
- 파일 I/O
- 네트워크 통신
```

---

### ❓ Q2. Virtual Thread vs Platform Thread 차이?

**답변**:
```
핵심 차이점:

1. 메모리 사용
   Platform: ~1MB per thread
   Virtual: ~1KB per thread

2. 생성 비용
   Platform: 높음 (OS 스레드)
   Virtual: 낮음 (JVM 관리)

3. 최대 개수
   Platform: 수천 개
   Virtual: 수백만 개

4. 스케줄링
   Platform: OS 스케줄러
   Virtual: JVM 스케줄러 (ForkJoinPool)

5. 블로킹
   Platform: OS 스레드 블로킹
   Virtual: 자동 양보 (unmount)

6. 컨텍스트 스위칭
   Platform: 비용 높음 (OS 레벨)
   Virtual: 비용 낮음 (JVM 레벨)

언제 사용?
Platform Thread:
- CPU 집약적 작업
- 긴 계산
- 암호화

Virtual Thread:
- I/O 집약적 작업
- 네트워크 요청
- 데이터베이스 쿼리
```

---

### ❓ Q3. Virtual Thread는 어떻게 동작하나?

**답변**:
```
Virtual Thread 내부 동작:

1. 생성
   Thread.startVirtualThread(() -> {
       // 작업
   });

2. 마운팅 (Mounting)
   - Virtual Thread가 Platform Thread에 마운트됨
   - 실제 실행은 Platform Thread에서

3. 언마운팅 (Unmounting)
   - I/O 대기 시 자동으로 언마운트
   - Platform Thread는 다른 Virtual Thread 실행

4. 리마운팅 (Remounting)
   - I/O 완료 시 다시 마운트
   - 계속 실행

예시:
Virtual Thread 1 → Platform Thread A (실행)
Virtual Thread 1 → I/O 대기 (언마운트)
Virtual Thread 2 → Platform Thread A (실행)
Virtual Thread 1 → I/O 완료 (리마운트)

Carrier Thread:
- Virtual Thread를 실행하는 Platform Thread
- ForkJoinPool 사용
- 기본 개수: CPU 코어 수

핵심:
Virtual Thread ≠ Platform Thread
Virtual Thread는 논리적 스레드
Platform Thread는 물리적 스레드
```

---

### ❓ Q4. Virtual Thread 사용 시 주의사항?

**답변**:
```
주의사항:

1. ❌ synchronized 사용
   - Virtual Thread pinning 발생
   - Platform Thread에 고정됨
   - 성능 저하

   해결책:
   ✅ ReentrantLock 사용
   ✅ Atomic 클래스 사용

2. ❌ ThreadLocal 과용
   - Virtual Thread가 많으면 메모리 낭비
   - ThreadLocal도 많이 생성됨

   해결책:
   ✅ 명시적 컨텍스트 전달
   ✅ Scoped Values 사용 (Java 21+)

3. ❌ CPU 집약적 작업
   - Virtual Thread의 이점 없음
   - Platform Thread가 더 적합

   사용:
   ✅ I/O 작업에만 사용

4. ❌ Virtual Thread 풀링
   - 의미 없음 (생성 비용 낮음)
   - 오히려 복잡도만 증가

   권장:
   ✅ 필요할 때마다 생성

5. ❌ native 메서드
   - native 메서드는 pinning 발생
   - 예: Object.wait()

체크리스트:
✅ I/O 작업인가?
✅ synchronized 없는가?
✅ ThreadLocal 최소화?
✅ CPU 작업 아닌가?
```

---

### ❓ Q5. Virtual Thread의 스케줄링?

**답변**:
```
Virtual Thread 스케줄링:

1. Carrier Thread Pool
   - ForkJoinPool 사용
   - 기본 크기: CPU 코어 수
   - 설정 가능:
     jdk.virtualThreadScheduler.parallelism

2. Work-Stealing 알고리즘
   - 각 Carrier Thread는 작업 큐 보유
   - 유휴 스레드가 다른 큐에서 작업 가져옴
   - 부하 분산

3. FIFO 스케줄링
   - 먼저 제출된 작업 먼저 실행
   - 공평성 보장

4. Mounting/Unmounting
   Blocking 연산 시:
   - park(): Virtual Thread 언마운트
   - unpark(): Virtual Thread 리마운트

   예시:
   Thread.sleep(100);  // park → unmount
   // I/O 대기
   // unpark → remount

5. Pinning
   다음 상황에서 pinning 발생:
   - synchronized 블록
   - native 메서드
   - Object.wait()

   Pinning 효과:
   - Virtual Thread가 Carrier Thread에 고정
   - 다른 Virtual Thread 실행 불가
   - 동시성 감소

모니터링:
jdk.tracePinnedThreads

최적화:
- synchronized → ReentrantLock
- ThreadLocal → Scoped Values
- 긴 계산 → Platform Thread
```

---

### ❓ Q6. Virtual Thread 언제 사용?

**답변**:
```
✅ 사용하기 좋은 경우:

1. I/O 집약적 애플리케이션
   - 웹 서버
   - API Gateway
   - 마이크로서비스

2. 높은 동시성 필요
   - 수천~수만 개 동시 요청
   - 웹 크롤러
   - 채팅 서버

3. 블로킹 I/O
   - JDBC
   - HTTP Client
   - 파일 I/O

4. 간단한 코드 원하는 경우
   - 비동기 코드 → 동기 코드
   - CompletableFuture → Thread

5. 레거시 코드 마이그레이션
   - Thread Pool → Virtual Thread
   - 코드 변경 최소

❌ 사용하지 말아야 할 경우:

1. CPU 집약적 작업
   - 암호화/복호화
   - 이미지 처리
   - 비디오 인코딩

2. 짧은 작업
   - 단순 계산
   - 메모리 연산

3. synchronized 많은 코드
   - 레거시 코드
   - 동기화가 많은 경우

4. native 메서드 많은 경우
   - JNI 호출
   - 네이티브 라이브러리

실전 예시:
// ✅ 좋은 예
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    users.forEach(user ->
        executor.submit(() -> sendEmail(user))
    );
}

// ❌ 나쁜 예
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    numbers.forEach(n ->
        executor.submit(() -> calculatePrime(n))
    );
}
```

---

### ❓ Q7. Virtual Thread 성능 측정?

**답변**:
```
성능 측정 방법:

1. JFR (Java Flight Recorder)
   - Virtual Thread 이벤트 기록
   - Mounting/Unmounting 추적
   - Pinning 감지

   사용법:
   java -XX:StartFlightRecording MyApp

2. JVM 옵션
   - jdk.tracePinnedThreads
     Virtual Thread pinning 추적

   - jdk.virtualThreadScheduler.parallelism
     Carrier Thread 수 설정

3. 메트릭 수집
   // 스레드 수 모니터링
   Thread.getAllStackTraces().size()

   // Virtual Thread 수
   Thread.getAllStackTraces().values().stream()
       .filter(stack -> Thread.currentThread().isVirtual())
       .count()

4. 벤치마킹
   JMH (Java Microbenchmark Harness) 사용

   @Benchmark
   public void testVirtualThreads() {
       try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
           // 벤치마크 코드
       }
   }

5. 프로파일링
   - VisualVM
   - JProfiler
   - Async Profiler

주요 메트릭:
- 처리량 (Throughput)
- 응답 시간 (Latency)
- CPU 사용률
- 메모리 사용량
- Carrier Thread 활용도

최적화 가이드:
1. Pinning 제거
2. synchronized → ReentrantLock
3. ThreadLocal 최소화
4. I/O 작업에만 사용
```

---

### ❓ Q8. Structured Concurrency란?

**답변**:
```
Structured Concurrency는 동시 작업을 구조화하는 패턴입니다 (Java 21 Preview).

기존 방식 문제점:
CompletableFuture<String> f1 = CompletableFuture.supplyAsync(() -> task1());
CompletableFuture<String> f2 = CompletableFuture.supplyAsync(() -> task2());
// 작업이 언제 끝나는지?
// 에러 처리는?
// 취소는?

Structured Concurrency:
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Future<String> future1 = scope.fork(() -> task1());
    Future<String> future2 = scope.fork(() -> task2());

    scope.join();  // 모든 작업 완료 대기
    scope.throwIfFailed();  // 에러 발생 시 예외

    // 결과 사용
    String result1 = future1.resultNow();
    String result2 = future2.resultNow();
}

장점:
1. 명확한 생명주기
   - 스코프 시작/종료 명확
   - 리소스 자동 정리

2. 에러 처리
   - ShutdownOnFailure: 하나 실패 시 모두 취소
   - ShutdownOnSuccess: 하나 성공 시 모두 취소

3. 취소 전파
   - 부모 취소 시 자식도 취소

4. 가독성
   - try-with-resources 패턴
   - 구조화된 코드

사용 시나리오:
- 여러 API 병렬 호출
- 데이터베이스 다중 쿼리
- 마이크로서비스 호출

패턴:
// 모두 성공 필요
ShutdownOnFailure

// 하나만 성공하면 됨
ShutdownOnSuccess
```

---

### ❓ Q9. Virtual Thread 마이그레이션 전략?

**답변**:
```
단계적 마이그레이션:

1단계: 평가
- Java 21 이상 사용 가능한가?
- I/O 작업이 많은가?
- synchronized 사용 정도는?

2단계: 후보 선정
✅ 좋은 후보:
- HTTP 서버
- 데이터베이스 작업
- 외부 API 호출
- 파일 처리

❌ 나쁜 후보:
- CPU 집약적 서비스
- synchronized가 많은 코드
- 네이티브 라이브러리 의존

3단계: 변환
Before:
ExecutorService executor = Executors.newFixedThreadPool(100);

After:
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();

4단계: 테스트
- 부하 테스트
- 성능 벤치마크
- 메모리 프로파일링
- 에러 로그 모니터링

5단계: 최적화
- synchronized 제거
- ThreadLocal 최소화
- Pinning 확인

6단계: 모니터링
- JFR 활성화
- 메트릭 수집
- 로그 분석

주의사항:
1. 점진적 적용
   - 한 번에 전체 변경 X
   - 모듈별로 순차 적용

2. 롤백 계획
   - 문제 발생 시 되돌리기
   - 기존 코드 유지

3. 팀 교육
   - Virtual Thread 개념
   - Best Practices
   - 주의사항

체크리스트:
✅ Java 21+ 사용
✅ I/O 작업 위주
✅ synchronized 최소
✅ 테스트 충분
✅ 모니터링 준비
```

---

### ❓ Q10. Virtual Thread vs Reactive Programming?

**답변**:
```
비교:

1. 코드 스타일
   Virtual Thread: 동기 스타일
   Reactive: 비동기 스타일

   Virtual:
   String result = httpClient.send(request);
   process(result);

   Reactive:
   httpClient.sendAsync(request)
       .thenAccept(response -> process(response));

2. 학습 곡선
   Virtual: 낮음 (기존 Thread API)
   Reactive: 높음 (새로운 패러다임)

3. 디버깅
   Virtual: 쉬움 (스택 트레이스)
   Reactive: 어려움 (콜백 체인)

4. 성능
   둘 다 높은 동시성 가능
   I/O 집약적에서 비슷한 성능

5. 생태계
   Virtual: 기존 라이브러리 호환
   Reactive: Reactive 라이브러리 필요

언제 사용?
Virtual Thread:
✅ 간단한 코드 원함
✅ 기존 코드 마이그레이션
✅ 팀이 Thread에 익숙
✅ 동기 스타일 선호

Reactive:
✅ 백프레셔 필요
✅ 스트림 처리
✅ 이미 Reactive 사용 중
✅ 세밀한 제어 필요

조합 가능:
// Reactive + Virtual Thread
Flux.fromIterable(users)
    .flatMap(user -> Mono.fromCallable(() ->
        Thread.startVirtualThread(() -> processUser(user))
    ))
    .subscribe();

결론:
- Virtual Thread: 더 간단, 더 익숙
- Reactive: 더 강력, 더 복잡
- 상황에 맞게 선택
```

---

## 🎓 종합 정리

### 📊 Virtual Thread 체크리스트

```
✅ 사용하기 좋은 경우:
1. I/O 집약적 작업
2. 높은 동시성 필요
3. 간단한 코드 원함
4. 블로킹 I/O 많음

❌ 사용하지 말아야 할 경우:
1. CPU 집약적 작업
2. synchronized 많음
3. native 메서드 많음
4. 짧은 작업
```

### 💡 Best Practices

```java
// ✅ DO
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
ReentrantLock lock = new ReentrantLock();
AtomicInteger counter = new AtomicInteger();

// ❌ DON'T
ExecutorService executor = Executors.newFixedThreadPool(1000);
synchronized void method() { }
ThreadLocal<String> threadLocal = new ThreadLocal<>();
```

### 🎯 마이그레이션 로드맵

```
1. Java 21 업그레이드
2. I/O 작업 식별
3. Executor 변경
4. synchronized 제거
5. 테스트 & 모니터링
6. 점진적 확대
```

---

## 🎉 시리즈 완료!

**Part 1**: 5가지 실생활 비유로 Virtual Thread 이해
**Part 2**: 3개 기업 사례 + 4개 주니어 실수
**Part 3**: 성능 분석 + 고급 기법 + 면접 질문

**47장 완료! 모든 챕터 (45-47) 완성!**

축하합니다! var, Record/Sealed, Virtual Threads를 완벽하게 마스터했습니다!
