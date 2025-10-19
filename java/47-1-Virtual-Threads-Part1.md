# 47장 Virtual Threads - Part 1: 실생활 비유로 이해하기

## 📚 목차
1. [비유 1: 식당 직원 vs 셀프 서비스 (경량 스레드)](#비유-1-식당-직원-vs-셀프-서비스)
2. [비유 2: 버스 좌석 vs 지하철 입석 (리소스 효율)](#비유-2-버스-좌석-vs-지하철-입석)
3. [비유 3: 전용 회의실 vs 공유 오피스 (컨텍스트 스위칭)](#비유-3-전용-회의실-vs-공유-오피스)
4. [비유 4: 고속도로 vs 골목길 (처리량)](#비유-4-고속도로-vs-골목길)
5. [비유 5: Platform Thread와의 비교](#비유-5-platform-thread와의-비교)

---

## 🔍 Virtual Threads란?

Virtual Threads는 Java 21에서 정식 도입된 **경량 스레드**입니다.

**핵심 개념**:
```java
// 전통적인 Platform Thread
Thread platformThread = new Thread(() -> {
    System.out.println("Platform Thread");
});
platformThread.start();

// Virtual Thread (Java 21+)
Thread virtualThread = Thread.startVirtualThread(() -> {
    System.out.println("Virtual Thread");
});
```

**Virtual Thread의 특징**:
```
1. 경량성: 수백만 개 생성 가능
2. 저비용: 메모리 사용량 극소
3. 블로킹 최적화: I/O 대기 시 자동으로 양보
4. 기존 코드 호환: Thread API 그대로 사용
```

---

## 📖 비유 1: 식당 직원 vs 셀프 서비스 (경량 스레드)

### 🎯 실생활 비유

**전통적인 식당 (Platform Thread)**:
```
- 직원 1명당 테이블 1개 전담
- 손님이 주문하고 기다리는 동안 직원은 대기
- 직원 수 = 동시에 서빙 가능한 테이블 수
- 제한: 직원은 비싸고, 공간도 필요
```

**셀프 서비스 식당 (Virtual Thread)**:
```
- 적은 수의 직원이 많은 테이블 관리
- 손님이 기다리는 동안 다른 테이블 서빙
- 손님 수 >> 직원 수
- 효율적: 직원이 항상 일함
```

### 💻 Java 코드로 구현

```java
package virtualthread.example1;

import java.time.Duration;
import java.time.Instant;
import java.util.stream.IntStream;

/**
 * Platform Thread vs Virtual Thread 기본 비교
 */
public class BasicComparisonDemo {
    private static final int TASK_COUNT = 10000;

    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== Platform Thread vs Virtual Thread ===\n");

        // 시나리오 1: Platform Thread
        System.out.println("📍 시나리오 1: Platform Thread (1만 개)");
        testPlatformThreads();

        // 시나리오 2: Virtual Thread
        System.out.println("\n📍 시나리오 2: Virtual Thread (1만 개)");
        testVirtualThreads();

        System.out.println("\n📊 결론:");
        System.out.println("✅ Virtual Thread가 훨씬 빠름");
        System.out.println("✅ 메모리 사용량도 적음");
        System.out.println("✅ 수백만 개 생성 가능");
    }

    /**
     * Platform Thread 테스트
     */
    static void testPlatformThreads() throws InterruptedException {
        var start = Instant.now();

        Thread[] threads = new Thread[TASK_COUNT];

        for (int i = 0; i < TASK_COUNT; i++) {
            threads[i] = new Thread(() -> {
                try {
                    Thread.sleep(100);  // I/O 시뮬레이션
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            });
            threads[i].start();
        }

        // 모든 스레드 종료 대기
        for (var thread : threads) {
            thread.join();
        }

        var duration = Duration.between(start, Instant.now());
        System.out.println("소요 시간: " + duration.toMillis() + "ms");
        System.out.println("(주의: 1만 개 Platform Thread는 시스템에 부담)");
    }

    /**
     * Virtual Thread 테스트
     */
    static void testVirtualThreads() throws InterruptedException {
        var start = Instant.now();

        Thread[] threads = new Thread[TASK_COUNT];

        for (int i = 0; i < TASK_COUNT; i++) {
            threads[i] = Thread.startVirtualThread(() -> {
                try {
                    Thread.sleep(100);  // I/O 시뮬레이션
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            });
        }

        // 모든 Virtual Thread 종료 대기
        for (var thread : threads) {
            thread.join();
        }

        var duration = Duration.between(start, Instant.now());
        System.out.println("소요 시간: " + duration.toMillis() + "ms");
        System.out.println("(Virtual Thread는 가볍고 빠름!)");
    }
}
```

### 🎯 핵심 포인트

**1. 생성 방법**:
```java
// Platform Thread
Thread platform = new Thread(() -> {
    // 작업
});
platform.start();

// Virtual Thread
Thread virtual = Thread.startVirtualThread(() -> {
    // 작업
});
```

**2. 리소스 비교**:
```
Platform Thread:
- 메모리: ~1MB per thread
- 생성 비용: 높음
- 최대 개수: 수천 개

Virtual Thread:
- 메모리: ~1KB per thread
- 생성 비용: 매우 낮음
- 최대 개수: 수백만 개
```

---

## 📖 비유 2: 버스 좌석 vs 지하철 입석 (리소스 효율)

### 🎯 실생활 비유

**버스 (Platform Thread)**:
```
- 좌석 수 = 승객 수
- 좌석당 1명만 앉음
- 빈 좌석도 공간 차지
- 제한된 수용 인원
```

**지하철 (Virtual Thread)**:
```
- 좌석 + 입석
- 훨씬 많은 승객 수용
- 공간 효율적 사용
- 대량 수송 가능
```

### 💻 Java 코드로 구현

```java
package virtualthread.example2;

import java.util.concurrent.*;

/**
 * Executor를 통한 Virtual Thread 사용
 */
public class ExecutorDemo {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== Executor with Virtual Threads ===\n");

        // 시나리오 1: 고정 크기 Thread Pool (Platform Thread)
        System.out.println("📍 시나리오 1: Fixed Thread Pool");
        testFixedThreadPool();

        // 시나리오 2: Virtual Thread Executor
        System.out.println("\n📍 시나리오 2: Virtual Thread Executor");
        testVirtualThreadExecutor();
    }

    /**
     * 고정 크기 Thread Pool
     */
    static void testFixedThreadPool() throws InterruptedException {
        ExecutorService executor = Executors.newFixedThreadPool(10);

        var start = System.currentTimeMillis();

        // 100개 작업 제출
        for (int i = 0; i < 100; i++) {
            final int taskId = i;
            executor.submit(() -> {
                try {
                    Thread.sleep(100);  // I/O 대기
                    System.out.println("Platform Task " + taskId);
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            });
        }

        executor.shutdown();
        executor.awaitTermination(1, TimeUnit.MINUTES);

        var duration = System.currentTimeMillis() - start;
        System.out.println("소요 시간: " + duration + "ms");
        System.out.println("(10개 스레드가 100개 작업을 순차 처리)");
    }

    /**
     * Virtual Thread Executor
     */
    static void testVirtualThreadExecutor() throws InterruptedException {
        // Virtual Thread용 Executor
        ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();

        var start = System.currentTimeMillis();

        // 100개 작업 제출
        for (int i = 0; i < 100; i++) {
            final int taskId = i;
            executor.submit(() -> {
                try {
                    Thread.sleep(100);  // I/O 대기
                    System.out.println("Virtual Task " + taskId);
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            });
        }

        executor.shutdown();
        executor.awaitTermination(1, TimeUnit.MINUTES);

        var duration = System.currentTimeMillis() - start;
        System.out.println("소요 시간: " + duration + "ms");
        System.out.println("(모든 작업이 거의 동시에 실행!)");
    }
}
```

### 🎯 핵심 포인트

**1. Executor 생성**:
```java
// Platform Thread Pool
ExecutorService platform = Executors.newFixedThreadPool(10);

// Virtual Thread Executor
ExecutorService virtual = Executors.newVirtualThreadPerTaskExecutor();
```

**2. 작업 제출**:
```java
// 둘 다 동일한 API 사용
executor.submit(() -> {
    // 작업
});
```

---

## 📖 비유 3: 전용 회의실 vs 공유 오피스 (컨텍스트 스위칭)

### 🎯 실생활 비유

**전용 회의실 (Platform Thread)**:
```
- 회의실 1개 = 팀 1개 전용
- 회의 없어도 방 차지
- 회의실 이동 시간 김 (컨텍스트 스위칭)
```

**공유 오피스 (Virtual Thread)**:
```
- 여러 팀이 공간 공유
- 필요할 때만 사용
- 빠른 전환
```

### 💻 Java 코드로 구현

```java
package virtualthread.example3;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.stream.IntStream;

/**
 * I/O 작업에서 Virtual Thread의 이점
 */
public class IODemo {
    private static final int REQUEST_COUNT = 100;

    public static void main(String[] args) {
        System.out.println("=== I/O 작업 성능 비교 ===\n");

        // 시나리오: HTTP 요청 100개
        System.out.println("📍 HTTP 요청 " + REQUEST_COUNT + "개 실행");

        System.out.println("\n1. Platform Thread Pool:");
        testWithPlatformThreads();

        System.out.println("\n2. Virtual Threads:");
        testWithVirtualThreads();
    }

    /**
     * Platform Thread로 HTTP 요청
     */
    static void testWithPlatformThreads() {
        try (ExecutorService executor = Executors.newFixedThreadPool(10)) {
            var start = System.currentTimeMillis();

            IntStream.range(0, REQUEST_COUNT)
                .forEach(i -> executor.submit(() -> {
                    makeHttpRequest("https://httpbin.org/delay/1");
                }));

            executor.shutdown();
            executor.awaitTermination(Duration.ofMinutes(5));

            var duration = System.currentTimeMillis() - start;
            System.out.println("소요 시간: " + duration + "ms");
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    /**
     * Virtual Thread로 HTTP 요청
     */
    static void testWithVirtualThreads() {
        try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
            var start = System.currentTimeMillis();

            IntStream.range(0, REQUEST_COUNT)
                .forEach(i -> executor.submit(() -> {
                    makeHttpRequest("https://httpbin.org/delay/1");
                }));

            executor.shutdown();
            executor.awaitTermination(Duration.ofMinutes(5));

            var duration = System.currentTimeMillis() - start;
            System.out.println("소요 시간: " + duration + "ms");
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    /**
     * HTTP 요청 수행
     */
    static void makeHttpRequest(String url) {
        try {
            var client = HttpClient.newHttpClient();
            var request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .build();

            var response = client.send(request, HttpResponse.BodyHandlers.ofString());
            // 응답 처리
        } catch (Exception e) {
            // 에러 처리
        }
    }
}
```

---

## 📖 비유 4: 고속도로 vs 골목길 (처리량)

### 🎯 실생활 비유

**골목길 (Platform Thread)**:
```
- 차선 수 제한
- 동시에 몇 대만 통과
- 대기 시간 발생
```

**고속도로 (Virtual Thread)**:
```
- 많은 차선
- 대량 차량 동시 통과
- 높은 처리량
```

### 💻 Java 코드로 구현

```java
package virtualthread.example4;

import java.util.concurrent.*;
import java.util.stream.IntStream;

/**
 * 처리량(Throughput) 비교
 */
public class ThroughputDemo {
    private static final int TASK_COUNT = 10000;

    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== 처리량 비교 ===\n");

        System.out.println("📍 1만 개 작업 처리");

        // Platform Thread Pool
        System.out.println("\n1. Platform Thread Pool (100 threads):");
        testThroughput(Executors.newFixedThreadPool(100));

        // Virtual Thread
        System.out.println("\n2. Virtual Thread Executor:");
        testThroughput(Executors.newVirtualThreadPerTaskExecutor());
    }

    static void testThroughput(ExecutorService executor) throws InterruptedException {
        var start = System.currentTimeMillis();

        // 1만 개 작업 제출
        var futures = IntStream.range(0, TASK_COUNT)
            .mapToObj(i -> executor.submit(() -> {
                try {
                    // CPU 작업
                    Thread.sleep(10);
                    return i * 2;
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            }))
            .toArray(Future[]::new);

        // 모든 작업 완료 대기
        for (var future : futures) {
            try {
                future.get();
            } catch (ExecutionException e) {
                e.printStackTrace();
            }
        }

        executor.shutdown();
        executor.awaitTermination(1, TimeUnit.MINUTES);

        var duration = System.currentTimeMillis() - start;
        var throughput = (TASK_COUNT * 1000.0) / duration;

        System.out.println("소요 시간: " + duration + "ms");
        System.out.println("처리량: " + String.format("%.0f", throughput) + " tasks/sec");
    }
}
```

---

## 📖 비유 5: Platform Thread와의 비교

### 🎯 종합 비교표

| 특성 | Platform Thread | Virtual Thread |
|------|----------------|----------------|
| 메모리 | ~1MB | ~1KB |
| 생성 비용 | 높음 | 낮음 |
| 최대 개수 | 수천 개 | 수백만 개 |
| 블로킹 | OS 스레드 블로킹 | 자동 양보 |
| 컨텍스트 스위칭 | 비용 높음 | 비용 낮음 |
| 사용 시나리오 | CPU 집약적 | I/O 집약적 |

### 💻 Java 코드로 확인

```java
package virtualthread.example5;

/**
 * Virtual Thread 특징 데모
 */
public class CharacteristicsDemo {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== Virtual Thread 특징 ===\n");

        // 특징 1: 경량성
        System.out.println("📍 특징 1: 경량성");
        System.out.println("수백만 개 생성 가능");
        testLightweight();

        // 특징 2: 자동 블로킹 처리
        System.out.println("\n📍 특징 2: 블로킹 최적화");
        System.out.println("I/O 대기 시 자동으로 다른 작업 수행");

        // 특징 3: 기존 API 호환
        System.out.println("\n📍 특징 3: 기존 API 호환");
        System.out.println("Thread API 그대로 사용");
    }

    static void testLightweight() throws InterruptedException {
        var start = System.currentTimeMillis();

        // 10만 개 Virtual Thread 생성!
        Thread[] threads = new Thread[100000];
        for (int i = 0; i < threads.length; i++) {
            threads[i] = Thread.startVirtualThread(() -> {
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            });
        }

        for (var thread : threads) {
            thread.join();
        }

        var duration = System.currentTimeMillis() - start;
        System.out.println("10만 개 Virtual Thread 실행 시간: " + duration + "ms");
        System.out.println("(Platform Thread로는 불가능!)");
    }
}
```

---

## 🎓 Part 1 종합 정리

### 📊 Virtual Thread 핵심

```
1. 경량성
   - Platform: ~1MB
   - Virtual: ~1KB

2. 생성 비용
   - Platform: 높음 (OS 스레드)
   - Virtual: 낮음 (JVM 관리)

3. 최대 개수
   - Platform: 수천 개
   - Virtual: 수백만 개

4. I/O 최적화
   - Platform: 블로킹 시 자원 낭비
   - Virtual: 자동 양보
```

### 💡 사용 시나리오

```java
// ✅ Virtual Thread 적합
- HTTP 요청 대량 처리
- 데이터베이스 쿼리
- 파일 I/O
- 네트워크 통신

// ❌ Platform Thread 적합
- CPU 집약적 작업
- 긴 계산
- 암호화/복호화
```

**다음 Part 2에서는**: 3개 기업 사례 (네이버, 카카오, 배민) + 4개 주니어 실수 시나리오를 다룹니다.
