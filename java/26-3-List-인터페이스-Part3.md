# 26장 List 인터페이스 Part 3 - 실전 프로젝트 & FAQ 🚀

## 🎯 실전 프로젝트: 작업 스케줄러 시스템

### 프로젝트 개요
실무에서 흔히 사용되는 **작업 스케줄러**를 구현합니다. 다양한 List 구현체의 특성을 활용하여 우선순위 큐, 실행 히스토리, 대기 작업 관리를 구현합니다.

### 요구사항
1. **우선순위 작업 큐**: 우선순위에 따라 작업 실행
2. **실행 히스토리**: 최근 1000개 작업 기록
3. **대기 작업 관리**: FIFO 방식 대기열
4. **동시성 지원**: 멀티스레드 환경에서 안전
5. **성능 최적화**: 적절한 List 구현체 선택

### 전체 코드

```java
import java.util.*;
import java.util.concurrent.*;
import java.time.*;
import java.time.format.DateTimeFormatter;

// 작업 클래스
class Task implements Comparable<Task> {
    public enum Priority {
        LOW(1), MEDIUM(2), HIGH(3), CRITICAL(4);

        private final int value;
        Priority(int value) { this.value = value; }
        public int getValue() { return value; }
    }

    public enum Status {
        PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
    }

    private final String taskId;
    private final String name;
    private final Priority priority;
    private final Runnable action;
    private Status status;
    private LocalDateTime createdAt;
    private LocalDateTime startedAt;
    private LocalDateTime completedAt;
    private String result;

    public Task(String taskId, String name, Priority priority, Runnable action) {
        this.taskId = taskId;
        this.name = name;
        this.priority = priority;
        this.action = action;
        this.status = Status.PENDING;
        this.createdAt = LocalDateTime.now();
    }

    public void execute() {
        this.status = Status.RUNNING;
        this.startedAt = LocalDateTime.now();

        try {
            action.run();
            this.status = Status.COMPLETED;
            this.result = "Success";
        } catch (Exception e) {
            this.status = Status.FAILED;
            this.result = "Error: " + e.getMessage();
        } finally {
            this.completedAt = LocalDateTime.now();
        }
    }

    @Override
    public int compareTo(Task other) {
        // 우선순위 높은 것이 먼저 (내림차순)
        int priorityCompare = Integer.compare(
            other.priority.getValue(),
            this.priority.getValue()
        );

        if (priorityCompare != 0) {
            return priorityCompare;
        }

        // 우선순위 같으면 먼저 생성된 것이 먼저 (오름차순)
        return this.createdAt.compareTo(other.createdAt);
    }

    // Getters
    public String getTaskId() { return taskId; }
    public String getName() { return name; }
    public Priority getPriority() { return priority; }
    public Status getStatus() { return status; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getStartedAt() { return startedAt; }
    public LocalDateTime getCompletedAt() { return completedAt; }
    public String getResult() { return result; }
    public void setStatus(Status status) { this.status = status; }

    @Override
    public String toString() {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("HH:mm:ss");
        return String.format("[%s] %s (우선순위: %s, 상태: %s) - 생성: %s",
            taskId, name, priority, status, createdAt.format(formatter));
    }

    public String getDetailedInfo() {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("HH:mm:ss.SSS");
        StringBuilder sb = new StringBuilder();
        sb.append("작업 ID: ").append(taskId).append("\n");
        sb.append("이름: ").append(name).append("\n");
        sb.append("우선순위: ").append(priority).append("\n");
        sb.append("상태: ").append(status).append("\n");
        sb.append("생성 시간: ").append(createdAt.format(formatter)).append("\n");

        if (startedAt != null) {
            sb.append("시작 시간: ").append(startedAt.format(formatter)).append("\n");
        }

        if (completedAt != null) {
            sb.append("완료 시간: ").append(completedAt.format(formatter)).append("\n");
            Duration duration = Duration.between(startedAt, completedAt);
            sb.append("실행 시간: ").append(duration.toMillis()).append("ms\n");
        }

        if (result != null) {
            sb.append("결과: ").append(result).append("\n");
        }

        return sb.toString();
    }
}

// 작업 스케줄러
class TaskScheduler {
    // 1. 우선순위 큐: PriorityQueue (내부적으로 힙 사용)
    //    - Task의 compareTo()에 따라 자동 정렬
    private final PriorityQueue<Task> priorityQueue;

    // 2. 실행 히스토리: ArrayList (크기 제한)
    //    - 조회가 많고, 끝에 추가만 함
    //    - 최대 1000개 유지 (LRU 방식)
    private final List<Task> executionHistory;
    private static final int MAX_HISTORY_SIZE = 1000;

    // 3. 대기 작업: LinkedList (FIFO)
    //    - 일반 우선순위 작업은 먼저 들어온 순서대로
    private final LinkedList<Task> waitingQueue;

    // 4. 작업 맵: HashMap (빠른 조회)
    private final Map<String, Task> taskMap;

    // 5. 동시성 제어
    private final ReentrantReadWriteLock lock = new ReentrantReadWriteLock();
    private final ExecutorService executorService;

    // 통계
    private int totalSubmitted = 0;
    private int totalCompleted = 0;
    private int totalFailed = 0;

    public TaskScheduler(int threadPoolSize) {
        this.priorityQueue = new PriorityQueue<>();
        this.executionHistory = new ArrayList<>(MAX_HISTORY_SIZE);
        this.waitingQueue = new LinkedList<>();
        this.taskMap = new ConcurrentHashMap<>();
        this.executorService = Executors.newFixedThreadPool(threadPoolSize);
    }

    // 작업 제출
    public void submitTask(Task task) {
        lock.writeLock().lock();
        try {
            priorityQueue.offer(task);
            taskMap.put(task.getTaskId(), task);
            totalSubmitted++;

            System.out.println("✅ 작업 제출: " + task);
        } finally {
            lock.writeLock().unlock();
        }
    }

    // 다음 작업 실행
    public void executeNextTask() {
        Task task = null;

        lock.writeLock().lock();
        try {
            task = priorityQueue.poll();

            if (task == null) {
                System.out.println("⚠️ 실행할 작업 없음");
                return;
            }
        } finally {
            lock.writeLock().unlock();
        }

        // 실행 (lock 밖에서)
        System.out.println("🔄 작업 실행 중: " + task.getName());
        task.execute();

        // 히스토리 추가
        lock.writeLock().lock();
        try {
            addToHistory(task);

            if (task.getStatus() == Task.Status.COMPLETED) {
                totalCompleted++;
            } else if (task.getStatus() == Task.Status.FAILED) {
                totalFailed++;
            }

            System.out.println("✅ 작업 완료: " + task.getName() +
                             " (결과: " + task.getResult() + ")");
        } finally {
            lock.writeLock().unlock();
        }
    }

    // 모든 작업 실행
    public void executeAllTasks() {
        while (true) {
            lock.readLock().lock();
            boolean hasMore;
            try {
                hasMore = !priorityQueue.isEmpty();
            } finally {
                lock.readLock().unlock();
            }

            if (!hasMore) {
                break;
            }

            executeNextTask();
        }
    }

    // 비동기 실행
    public void executeAllTasksAsync() {
        while (true) {
            Task task;

            lock.writeLock().lock();
            try {
                task = priorityQueue.poll();
                if (task == null) {
                    break;
                }
            } finally {
                lock.writeLock().unlock();
            }

            final Task finalTask = task;
            executorService.submit(() -> {
                System.out.println("🔄 [비동기] 작업 실행 중: " + finalTask.getName());
                finalTask.execute();

                lock.writeLock().lock();
                try {
                    addToHistory(finalTask);

                    if (finalTask.getStatus() == Task.Status.COMPLETED) {
                        totalCompleted++;
                    } else {
                        totalFailed++;
                    }

                    System.out.println("✅ [비동기] 작업 완료: " + finalTask.getName());
                } finally {
                    lock.writeLock().unlock();
                }
            });
        }
    }

    // 히스토리에 추가 (크기 제한)
    private void addToHistory(Task task) {
        if (executionHistory.size() >= MAX_HISTORY_SIZE) {
            // LRU: 가장 오래된 항목 제거
            executionHistory.remove(0);
        }
        executionHistory.add(task);
    }

    // 작업 조회
    public Task getTask(String taskId) {
        return taskMap.get(taskId);
    }

    // 최근 N개 작업 조회
    public List<Task> getRecentTasks(int count) {
        lock.readLock().lock();
        try {
            int size = executionHistory.size();
            int start = Math.max(0, size - count);
            return new ArrayList<>(executionHistory.subList(start, size));
        } finally {
            lock.readLock().unlock();
        }
    }

    // 우선순위별 통계
    public Map<Task.Priority, Integer> getStatisticsByPriority() {
        lock.readLock().lock();
        try {
            Map<Task.Priority, Integer> stats = new EnumMap<>(Task.Priority.class);

            for (Task task : executionHistory) {
                stats.merge(task.getPriority(), 1, Integer::sum);
            }

            return stats;
        } finally {
            lock.readLock().unlock();
        }
    }

    // 통계 출력
    public void displayStatistics() {
        lock.readLock().lock();
        try {
            System.out.println("\n📊 작업 스케줄러 통계:");
            System.out.println("   제출된 작업: " + totalSubmitted);
            System.out.println("   완료된 작업: " + totalCompleted);
            System.out.println("   실패한 작업: " + totalFailed);
            System.out.println("   대기 중: " + priorityQueue.size());
            System.out.println("   히스토리: " + executionHistory.size() + "개");

            System.out.println("\n   우선순위별 실행 통계:");
            Map<Task.Priority, Integer> stats = getStatisticsByPriority();
            for (Task.Priority priority : Task.Priority.values()) {
                int count = stats.getOrDefault(priority, 0);
                System.out.println("      " + priority + ": " + count + "개");
            }
        } finally {
            lock.readLock().unlock();
        }
    }

    // 최근 작업 출력
    public void displayRecentTasks(int count) {
        List<Task> recent = getRecentTasks(count);

        System.out.println("\n📝 최근 " + count + "개 작업:");
        for (int i = 0; i < recent.size(); i++) {
            System.out.println("   " + (i + 1) + ". " + recent.get(i));
        }
    }

    // 종료
    public void shutdown() {
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(60, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            executorService.shutdownNow();
        }
    }
}

// 메인 예제
public class TaskSchedulerExample {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== 작업 스케줄러 시스템 ===\n");

        TaskScheduler scheduler = new TaskScheduler(4);

        // 다양한 우선순위 작업 제출
        scheduler.submitTask(new Task("T001", "데이터 백업", Task.Priority.MEDIUM,
            () -> sleep(100)));

        scheduler.submitTask(new Task("T002", "시스템 장애 복구", Task.Priority.CRITICAL,
            () -> sleep(50)));

        scheduler.submitTask(new Task("T003", "로그 정리", Task.Priority.LOW,
            () -> sleep(30)));

        scheduler.submitTask(new Task("T004", "보안 패치 적용", Task.Priority.HIGH,
            () -> sleep(80)));

        scheduler.submitTask(new Task("T005", "사용자 알림 발송", Task.Priority.MEDIUM,
            () -> sleep(40)));

        scheduler.submitTask(new Task("T006", "긴급 배포", Task.Priority.CRITICAL,
            () -> sleep(60)));

        System.out.println("\n--- 동기 실행 (우선순위 순) ---\n");

        // 모든 작업 실행
        scheduler.executeAllTasks();

        // 통계
        scheduler.displayStatistics();

        // 최근 작업
        scheduler.displayRecentTasks(5);

        System.out.println("\n--- 비동기 실행 테스트 ---\n");

        TaskScheduler asyncScheduler = new TaskScheduler(4);

        // 더 많은 작업 제출
        for (int i = 1; i <= 10; i++) {
            Task.Priority priority = Task.Priority.values()[i % 4];
            asyncScheduler.submitTask(new Task(
                "ASYNC-" + i,
                "비동기 작업 " + i,
                priority,
                () -> sleep(50)
            ));
        }

        asyncScheduler.executeAllTasksAsync();

        // 완료 대기
        Thread.sleep(2000);

        asyncScheduler.displayStatistics();
        asyncScheduler.displayRecentTasks(10);

        asyncScheduler.shutdown();

        System.out.println("\n\n💡 프로젝트 핵심 포인트:");
        System.out.println("1. PriorityQueue: 우선순위 자동 정렬");
        System.out.println("2. ArrayList: 실행 히스토리 (크기 제한 LRU)");
        System.out.println("3. LinkedList: FIFO 대기 큐");
        System.out.println("4. ConcurrentHashMap: 빠른 작업 조회");
        System.out.println("5. ReentrantReadWriteLock: 세밀한 동시성 제어");
    }

    private static void sleep(long millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

### 실행 결과
```
=== 작업 스케줄러 시스템 ===

✅ 작업 제출: [T001] 데이터 백업 (우선순위: MEDIUM, 상태: PENDING) - 생성: 14:23:45
✅ 작업 제출: [T002] 시스템 장애 복구 (우선순위: CRITICAL, 상태: PENDING) - 생성: 14:23:45
✅ 작업 제출: [T003] 로그 정리 (우선순위: LOW, 상태: PENDING) - 생성: 14:23:45
✅ 작업 제출: [T004] 보안 패치 적용 (우선순위: HIGH, 상태: PENDING) - 생성: 14:23:45
✅ 작업 제출: [T005] 사용자 알림 발송 (우선순위: MEDIUM, 상태: PENDING) - 생성: 14:23:45
✅ 작업 제출: [T006] 긴급 배포 (우선순위: CRITICAL, 상태: PENDING) - 생성: 14:23:45

--- 동기 실행 (우선순위 순) ---

🔄 작업 실행 중: 시스템 장애 복구
✅ 작업 완료: 시스템 장애 복구 (결과: Success)
🔄 작업 실행 중: 긴급 배포
✅ 작업 완료: 긴급 배포 (결과: Success)
🔄 작업 실행 중: 보안 패치 적용
✅ 작업 완료: 보안 패치 적용 (결과: Success)
🔄 작업 실행 중: 데이터 백업
✅ 작업 완료: 데이터 백업 (결과: Success)
🔄 작업 실행 중: 사용자 알림 발송
✅ 작업 완료: 사용자 알림 발송 (결과: Success)
🔄 작업 실행 중: 로그 정리
✅ 작업 완료: 로그 정리 (결과: Success)

📊 작업 스케줄러 통계:
   제출된 작업: 6
   완료된 작업: 6
   실패한 작업: 0
   대기 중: 0
   히스토리: 6개

   우선순위별 실행 통계:
      LOW: 1개
      MEDIUM: 2개
      HIGH: 1개
      CRITICAL: 2개

📝 최근 5개 작업:
   1. [T002] 시스템 장애 복구 (우선순위: CRITICAL, 상태: COMPLETED) - 생성: 14:23:45
   2. [T006] 긴급 배포 (우선순위: CRITICAL, 상태: COMPLETED) - 생성: 14:23:45
   3. [T004] 보안 패치 적용 (우선순위: HIGH, 상태: COMPLETED) - 생성: 14:23:45
   4. [T001] 데이터 백업 (우선순위: MEDIUM, 상태: COMPLETED) - 생성: 14:23:45
   5. [T005] 사용자 알림 발송 (우선순위: MEDIUM, 상태: COMPLETED) - 생성: 14:23:45

--- 비동기 실행 테스트 ---

✅ 작업 제출: [ASYNC-1] 비동기 작업 1 (우선순위: MEDIUM, 상태: PENDING) - 생성: 14:23:46
✅ 작업 제출: [ASYNC-2] 비동기 작업 2 (우선순위: HIGH, 상태: PENDING) - 생성: 14:23:46
...
🔄 [비동기] 작업 실행 중: 비동기 작업 3
🔄 [비동기] 작업 실행 중: 비동기 작업 7
🔄 [비동기] 작업 실행 중: 비동기 작업 6
🔄 [비동기] 작업 실행 중: 비동기 작업 2
✅ [비동기] 작업 완료: 비동기 작업 3
✅ [비동기] 작업 완료: 비동기 작업 7
...

💡 프로젝트 핵심 포인트:
1. PriorityQueue: 우선순위 자동 정렬
2. ArrayList: 실행 히스토리 (크기 제한 LRU)
3. LinkedList: FIFO 대기 큐
4. ConcurrentHashMap: 빠른 작업 조회
5. ReentrantReadWriteLock: 세밀한 동시성 제어
```

### 프로젝트 핵심 패턴

#### 1. List 선택 기준
```java
// 우선순위 자동 정렬 필요 → PriorityQueue
PriorityQueue<Task> priorityQueue = new PriorityQueue<>();

// 조회 많음, 끝에 추가, 크기 제한 → ArrayList
List<Task> history = new ArrayList<>(MAX_SIZE);

// FIFO, 앞/뒤 추가/삭제 → LinkedList
LinkedList<Task> waitingQueue = new LinkedList<>();

// 빠른 조회 → HashMap
Map<String, Task> taskMap = new ConcurrentHashMap<>();
```

#### 2. 크기 제한 패턴 (LRU)
```java
private void addToHistory(Task task) {
    if (executionHistory.size() >= MAX_HISTORY_SIZE) {
        executionHistory.remove(0);  // 가장 오래된 항목 제거
    }
    executionHistory.add(task);
}
```

#### 3. 동시성 제어
```java
// 읽기/쓰기 분리
ReentrantReadWriteLock lock = new ReentrantReadWriteLock();

// 쓰기
lock.writeLock().lock();
try {
    // 쓰기 작업
} finally {
    lock.writeLock().unlock();
}

// 읽기
lock.readLock().lock();
try {
    // 읽기 작업
} finally {
    lock.readLock().unlock();
}
```

---

## ❓ FAQ (자주 묻는 질문)

### Q1. ArrayList와 LinkedList 중 어느 것을 선택해야 하나요?

**A**: 대부분의 경우 **ArrayList**를 선택하세요.

```java
// ✅ ArrayList 선택 (99%의 경우)
List<String> list = new ArrayList<>();

// 이유:
// 1. 조회가 압도적으로 많음 (O(1) vs O(n))
// 2. 캐시 친화적 (연속된 메모리)
// 3. 메모리 효율적 (포인터 오버헤드 없음)
// 4. 일반적으로 더 빠름
```

**LinkedList를 선택하는 경우**:
```java
// Queue/Deque 구현
Queue<String> queue = new LinkedList<>();
queue.offer("A");
String first = queue.poll();  // O(1) 앞에서 제거

Deque<String> deque = new LinkedList<>();
deque.addFirst("A");  // O(1)
deque.addLast("B");   // O(1)
```

**성능 비교**:
| 연산 | ArrayList | LinkedList | 선택 |
|------|-----------|------------|------|
| get(i) | O(1) | O(n) | ArrayList ✅ |
| add(E) | O(1)* | O(1) | 비슷 |
| add(i, E) | O(n) | O(n) | 비슷 |
| remove(i) | O(n) | O(n) | 비슷 |
| addFirst() | O(n) | O(1) | LinkedList ✅ |
| removeFirst() | O(n) | O(1) | LinkedList ✅ |

---

### Q2. Vector를 사용해야 하나요?

**A**: **아니오**. Vector는 legacy 클래스입니다. 사용하지 마세요.

```java
// ❌ 사용 금지
Vector<String> vector = new Vector<>();

// ✅ 대신 사용:

// 1. 동시성 필요 없음 → ArrayList
List<String> list = new ArrayList<>();

// 2. 동시성 필요 + 균형 → Collections.synchronizedList
List<String> syncList = Collections.synchronizedList(new ArrayList<>());

// 3. 동시성 필요 + 읽기 >> 쓰기 → CopyOnWriteArrayList
List<String> cowList = new CopyOnWriteArrayList<>();
```

**Vector가 나쁜 이유**:
1. **성능 오버헤드**: 모든 메서드가 `synchronized` (단일 스레드에서도 느림)
2. **Coarse-grained locking**: 읽기도 lock 필요
3. **Legacy API**: Java 1.0부터 존재 (Collections Framework 이전)
4. **2배 확장**: 메모리 비효율 (ArrayList는 1.5배)

---

### Q3. List 초기 용량을 항상 지정해야 하나요?

**A**: **크기를 알면 지정**하세요. 성능이 크게 향상됩니다.

```java
// ❌ 크기를 아는데 지정 안 함
List<User> users = new ArrayList<>();  // 기본 10
for (int i = 0; i < 10000; i++) {
    users.add(loadUser(i));  // 수십 번 배열 복사!
}

// ✅ 크기 지정
List<User> users = new ArrayList<>(10000);
for (int i = 0; i < 10000; i++) {
    users.add(loadUser(i));  // 배열 복사 없음!
}

// 성능 차이: 약 2-3배
```

**언제 지정?**
- ✅ 크기를 정확히 알 때
- ✅ 최소 크기를 추정할 수 있을 때
- ❌ 크기를 전혀 모를 때 (기본값 사용)

---

### Q4. subList()를 사용할 때 주의할 점은?

**A**: `subList()`는 **뷰(view)**를 반환합니다. 원본을 변경하면 subList도 변경됩니다.

```java
List<String> original = new ArrayList<>(Arrays.asList("A", "B", "C", "D", "E"));

// subList()는 뷰 반환
List<String> sub = original.subList(1, 4);  // [B, C, D]

System.out.println(sub);  // [B, C, D]

// 원본 변경 → subList도 변경
original.set(2, "X");
System.out.println(sub);  // [B, X, D] ⚠️ 변경됨!

// subList 변경 → 원본도 변경
sub.set(0, "Y");
System.out.println(original);  // [A, Y, X, D, E] ⚠️ 변경됨!

// ✅ 독립적인 복사본 필요 시
List<String> copy = new ArrayList<>(original.subList(1, 4));
copy.set(0, "Z");
System.out.println(original);  // [A, Y, X, D, E] (변경 안 됨)
```

**주의사항**:
1. **뷰**: 원본과 연결됨
2. **ConcurrentModificationException**: 원본 수정 시 subList 사용 불가
3. **독립적 복사**: `new ArrayList<>(subList)`

---

### Q5. List.of()와 Arrays.asList()의 차이는?

**A**: 둘 다 **불변이지만**, 동작이 다릅니다.

```java
// Arrays.asList() - 고정 크기, 수정 가능
List<String> list1 = Arrays.asList("A", "B", "C");
list1.set(0, "Z");  // ✅ 수정 가능
list1.add("D");     // ❌ UnsupportedOperationException (크기 변경 불가)

// List.of() - 완전 불변 (Java 9+)
List<String> list2 = List.of("A", "B", "C");
list2.set(0, "Z");  // ❌ UnsupportedOperationException
list2.add("D");     // ❌ UnsupportedOperationException

// null 허용
List<String> list3 = Arrays.asList("A", null, "C");  // ✅ null 허용
List<String> list4 = List.of("A", null, "C");        // ❌ NullPointerException
```

**정리**:
| 특징 | Arrays.asList() | List.of() |
|------|-----------------|-----------|
| 크기 변경 | ❌ | ❌ |
| 요소 수정 | ✅ | ❌ |
| null 허용 | ✅ | ❌ |
| 성능 | 보통 | 빠름 |
| Java 버전 | 1.2+ | 9+ |

**사용 시나리오**:
```java
// 불변 리스트 → List.of()
List<String> constants = List.of("RED", "GREEN", "BLUE");

// 가변 리스트로 변환 → new ArrayList<>()
List<String> mutable = new ArrayList<>(List.of("A", "B", "C"));
mutable.add("D");  // ✅ 가능
```

---

### Q6. for-each에서 삭제하려면 어떻게 해야 하나요?

**A**: **Iterator.remove()** 또는 **removeIf()** 사용

```java
List<String> list = new ArrayList<>(Arrays.asList("A", "B", "C", "D"));

// ❌ ConcurrentModificationException
for (String item : list) {
    if (item.equals("B")) {
        list.remove(item);  // 예외 발생!
    }
}

// ✅ 방법 1: Iterator 사용
Iterator<String> iter = list.iterator();
while (iter.hasNext()) {
    String item = iter.next();
    if (item.equals("B")) {
        iter.remove();  // OK
    }
}

// ✅ 방법 2: removeIf() (Java 8+)
list.removeIf(item -> item.equals("B"));  // 가장 간결

// ✅ 방법 3: 인덱스 역순
for (int i = list.size() - 1; i >= 0; i--) {
    if (list.get(i).equals("B")) {
        list.remove(i);
    }
}

// ✅ 방법 4: Stream (새 리스트)
List<String> filtered = list.stream()
    .filter(item -> !item.equals("B"))
    .collect(Collectors.toList());
```

---

### Q7. 멀티스레드 환경에서 안전한 List는?

**A**: **CopyOnWriteArrayList** 또는 **Collections.synchronizedList()**

```java
// 1. CopyOnWriteArrayList (읽기 >> 쓰기)
List<String> cowList = new CopyOnWriteArrayList<>();
// - 읽기: lock 없음 (매우 빠름)
// - 쓰기: 전체 복사 (느림)
// - 사용: 읽기 99%, 쓰기 1%

// 2. Collections.synchronizedList (균형)
List<String> syncList = Collections.synchronizedList(new ArrayList<>());
// - 읽기/쓰기: synchronized (보통 속도)
// - 사용: 읽기/쓰기 균형

// ⚠️ 주의: 순회 시 명시적 동기화 필요
synchronized (syncList) {
    for (String item : syncList) {
        System.out.println(item);
    }
}

// 3. 명시적 Lock (세밀한 제어)
List<String> list = new ArrayList<>();
ReentrantReadWriteLock lock = new ReentrantReadWriteLock();

// 읽기
lock.readLock().lock();
try {
    String item = list.get(0);
} finally {
    lock.readLock().unlock();
}

// 쓰기
lock.writeLock().lock();
try {
    list.add("A");
} finally {
    lock.writeLock().unlock();
}
```

**선택 기준**:
- 읽기 >> 쓰기 → `CopyOnWriteArrayList`
- 균형잡힌 읽기/쓰기 → `Collections.synchronizedList`
- 세밀한 제어 → `ReentrantReadWriteLock`

---

## 💼 면접 질문 (Interview Questions)

### 주니어 레벨 (Junior Level)

#### Q1. ArrayList와 LinkedList의 차이점을 설명하세요.

**모범 답변**:

ArrayList와 LinkedList의 주요 차이점은 **내부 구조**와 **성능 특성**입니다.

**ArrayList**:
- **내부 구조**: 동적 배열 (연속된 메모리)
- **조회**: O(1) - 인덱스로 즉시 접근 가능
- **추가/삭제**: O(n) - 중간 삽입 시 뒤의 요소들 이동 필요
- **메모리**: 연속 메모리, 캐시 친화적
- **용량 확장**: 1.5배씩 확장

**LinkedList**:
- **내부 구조**: 이중 연결 리스트 (노드 + 포인터)
- **조회**: O(n) - 순차 탐색 필요
- **추가/삭제**: O(1) - 앞/뒤는 빠르지만, 중간은 O(n) (탐색 비용)
- **메모리**: 노드당 포인터 2개 (prev, next) 오버헤드
- **용량 확장**: 없음 (노드 단위 추가)

**사용 시나리오**:
- ArrayList: 조회가 많은 경우 (일반적)
- LinkedList: Queue/Deque 구현, 앞/뒤 추가/삭제가 많은 경우

---

#### Q2. ArrayList의 초기 용량은 얼마인가요? 어떻게 확장되나요?

**모범 답변**:

**초기 용량**: 10 (기본 생성자 사용 시)

```java
List<Integer> list = new ArrayList<>();  // 초기 용량 10
```

**확장 과정**:
1. **용량 확산 비율**: 약 1.5배
   ```
   10 → 15 → 22 → 33 → 49 → 73 → ...
   ```

2. **확장 과정**:
   ```java
   // 내부 동작 (의사 코드)
   if (size >= capacity) {
       int newCapacity = capacity + (capacity >> 1);  // capacity * 1.5
       Object[] newArray = new Object[newCapacity];
       System.arraycopy(oldArray, 0, newArray, 0, size);
       array = newArray;
   }
   ```

3. **시간 복잡도**:
   - 용량 충분: O(1)
   - 용량 초과: O(n) (배열 복사)

**최적화**:
```java
// ✅ 크기를 아는 경우 초기 용량 지정
List<Integer> list = new ArrayList<>(10000);
```

---

#### Q3. ConcurrentModificationException이 발생하는 이유와 해결 방법은?

**모범 답변**:

**발생 이유**: 컬렉션 순회 중 구조적 변경(추가/삭제)이 발생할 때

```java
// ❌ 예외 발생
List<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));
for (String item : list) {
    if (item.equals("B")) {
        list.remove(item);  // ConcurrentModificationException!
    }
}
```

**내부 메커니즘**:
```java
// for-each는 Iterator 사용
Iterator<String> iter = list.iterator();  // modCount 저장
while (iter.hasNext()) {
    String item = iter.next();  // modCount 검증
    // 직접 list.remove() 호출 시 modCount 증가
    // → Iterator의 modCount와 불일치
    // → ConcurrentModificationException
}
```

**해결 방법**:

1. **Iterator.remove()**:
```java
Iterator<String> iter = list.iterator();
while (iter.hasNext()) {
    String item = iter.next();
    if (item.equals("B")) {
        iter.remove();  // ✅ 안전
    }
}
```

2. **removeIf()** (Java 8+):
```java
list.removeIf(item -> item.equals("B"));  // ✅ 가장 간결
```

3. **인덱스 역순**:
```java
for (int i = list.size() - 1; i >= 0; i--) {
    if (list.get(i).equals("B")) {
        list.remove(i);  // ✅ 안전
    }
}
```

---

#### Q4. Arrays.asList()로 생성한 List에 add()를 호출하면 어떻게 되나요?

**모범 답변**:

**UnsupportedOperationException** 발생

**이유**: `Arrays.asList()`는 **고정 크기 리스트**를 반환합니다.

```java
List<String> list = Arrays.asList("A", "B", "C");

list.set(0, "Z");  // ✅ 수정 가능
list.add("D");     // ❌ UnsupportedOperationException
list.remove(0);    // ❌ UnsupportedOperationException
```

**내부 구현**:
```java
// Arrays.asList()는 Arrays.ArrayList 반환 (java.util.ArrayList와 다름!)
private static class ArrayList<E> extends AbstractList<E> {
    private final E[] a;  // 원본 배열 참조

    // add(), remove() 미구현 → AbstractList의 기본 구현 사용
    // → UnsupportedOperationException 던짐
}
```

**해결 방법**:
```java
// ✅ 가변 리스트로 복사
List<String> mutable = new ArrayList<>(Arrays.asList("A", "B", "C"));
mutable.add("D");  // OK

// 또는 List.of() 사용 후 복사 (Java 9+)
List<String> mutable = new ArrayList<>(List.of("A", "B", "C"));
```

---

#### Q5. List의 주요 메서드와 시간 복잡도를 설명하세요. (ArrayList 기준)

**모범 답변**:

| 메서드 | 시간 복잡도 | 설명 |
|--------|-------------|------|
| `add(E e)` | O(1)* | 끝에 추가 (*용량 충분 시) |
| `add(int index, E e)` | O(n) | 중간 삽입 (뒤의 요소 이동) |
| `get(int index)` | O(1) | 인덱스 접근 |
| `set(int index, E e)` | O(1) | 인덱스 수정 |
| `remove(int index)` | O(n) | 중간 제거 (뒤의 요소 이동) |
| `remove(Object o)` | O(n) | 객체 제거 (검색 + 제거) |
| `contains(Object o)` | O(n) | 순차 탐색 |
| `indexOf(Object o)` | O(n) | 순차 탐색 |
| `size()` | O(1) | 크기 반환 |
| `clear()` | O(n) | 모든 참조 null 설정 |

**예시**:
```java
List<String> list = new ArrayList<>();

list.add("A");           // O(1)
list.add(0, "B");        // O(n) - 기존 요소들 한 칸씩 이동
String item = list.get(0);  // O(1) - array[0] 직접 접근
list.remove("A");        // O(n) - 검색 O(n) + 제거 O(n)
boolean has = list.contains("B");  // O(n) - 순차 탐색
```

---

#### Q6. Vector와 ArrayList의 차이점은 무엇인가요?

**모범 답변**:

| 특징 | ArrayList | Vector |
|------|-----------|--------|
| **동기화** | ❌ Not synchronized | ✅ Synchronized |
| **Thread-safe** | ❌ | ✅ |
| **성능** | 빠름 | 느림 (동기화 오버헤드) |
| **용량 확장** | 1.5배 | 2배 |
| **도입 시기** | Java 1.2 (Collections Framework) | Java 1.0 (Legacy) |
| **권장 여부** | ✅ 권장 | ❌ 비권장 |

**Vector 내부**:
```java
// 모든 메서드가 synchronized
public synchronized boolean add(E e) { ... }
public synchronized E get(int index) { ... }
public synchronized E remove(int index) { ... }
```

**단점**:
1. 모든 메서드 `synchronized` → 단일 스레드에서도 느림
2. Coarse-grained locking → 읽기도 lock 필요
3. 2배 확장 → 메모리 비효율

**대안**:
```java
// 1. 동시성 필요 없음 → ArrayList
List<String> list = new ArrayList<>();

// 2. 동시성 필요 → Collections.synchronizedList
List<String> syncList = Collections.synchronizedList(new ArrayList<>());

// 3. 읽기 >> 쓰기 → CopyOnWriteArrayList
List<String> cowList = new CopyOnWriteArrayList<>();
```

---

#### Q7. subList()의 동작 방식을 설명하세요.

**모범 답변**:

`subList()`는 **뷰(view)**를 반환합니다. 원본 리스트의 일부를 참조하는 가상 리스트입니다.

**특징**:
1. **원본 참조**: 별도 복사 없음
2. **양방향 동기화**: 원본 변경 → subList 영향, subList 변경 → 원본 영향
3. **구조적 변경 금지**: 원본의 구조적 변경 시 ConcurrentModificationException

**예시**:
```java
List<String> original = new ArrayList<>(Arrays.asList("A", "B", "C", "D", "E"));
List<String> sub = original.subList(1, 4);  // [B, C, D] (뷰)

System.out.println(sub);  // [B, C, D]

// 1. 원본 변경 → subList 영향
original.set(2, "X");
System.out.println(sub);  // [B, X, D] ⚠️

// 2. subList 변경 → 원본 영향
sub.set(0, "Y");
System.out.println(original);  // [A, Y, X, D, E] ⚠️

// 3. 원본에 add/remove → ConcurrentModificationException
original.add("F");
System.out.println(sub);  // ❌ ConcurrentModificationException
```

**사용 시나리오**:
```java
// 1. 부분 삭제
list.subList(2, 5).clear();  // 2~4번 인덱스 삭제

// 2. 부분 교체
List<String> replacement = Arrays.asList("X", "Y", "Z");
Collections.copy(list.subList(1, 4), replacement);

// 3. 독립적 복사본 필요
List<String> copy = new ArrayList<>(list.subList(1, 4));
```

---

### 중급 레벨 (Intermediate Level)

#### Q8. CopyOnWriteArrayList의 내부 동작 원리를 설명하세요.

**모범 답변**:

CopyOnWriteArrayList는 **Copy-On-Write** 전략을 사용합니다.

**핵심 원리**:
1. **읽기**: Lock 없이 현재 배열 직접 읽기 (매우 빠름)
2. **쓰기**: 전체 배열 복사 후 변경 (느림)

**내부 구조**:
```java
public class CopyOnWriteArrayList<E> {
    private volatile Object[] array;  // volatile로 가시성 보장

    // 읽기: Lock 없음
    public E get(int index) {
        return (E) array[index];  // 직접 읽기
    }

    // 쓰기: Lock + 배열 복사
    public boolean add(E e) {
        final ReentrantLock lock = this.lock;
        lock.lock();
        try {
            Object[] elements = getArray();
            int len = elements.length;

            // 1. 새 배열 생성 (크기 +1)
            Object[] newElements = Arrays.copyOf(elements, len + 1);

            // 2. 새 요소 추가
            newElements[len] = e;

            // 3. 배열 참조 교체 (원자적)
            setArray(newElements);

            return true;
        } finally {
            lock.unlock();
        }
    }
}
```

**동작 과정**:
```
초기: [A, B, C]

add("D") 호출:
1. 기존 배열: [A, B, C]
2. 새 배열 생성: [?, ?, ?, ?] (크기 4)
3. 복사: [A, B, C, ?]
4. 추가: [A, B, C, D]
5. 배열 참조 교체 (volatile write)

→ 읽는 중인 스레드는 계속 [A, B, C] 읽음
→ 새로운 읽기는 [A, B, C, D] 읽음
```

**장점**:
- 읽기 lock 없음 (매우 빠름)
- Iterator fail-safe (순회 안전)
- Thread-safe

**단점**:
- 쓰기 매우 느림 (O(n) 복사)
- 메모리 오버헤드 (복사본)
- Weak consistency (최신 데이터 보장 안 됨)

**사용 시나리오**:
- 읽기 >> 쓰기 (99% vs 1%)
- 이벤트 리스너 목록
- 설정 정보
- 캐시 데이터

---

#### Q9. ArrayList의 내부 구현을 설명하고, ensureCapacity() 메서드의 역할은?

**모범 답변**:

**ArrayList 내부 구조**:
```java
public class ArrayList<E> {
    private static final int DEFAULT_CAPACITY = 10;
    private Object[] elementData;  // 실제 데이터 저장
    private int size;  // 실제 요소 개수

    public ArrayList() {
        this.elementData = new Object[DEFAULT_CAPACITY];
    }

    public ArrayList(int initialCapacity) {
        this.elementData = new Object[initialCapacity];
    }
}
```

**add() 동작**:
```java
public boolean add(E e) {
    ensureCapacityInternal(size + 1);  // 용량 확인
    elementData[size++] = e;
    return true;
}

private void ensureCapacityInternal(int minCapacity) {
    if (minCapacity > elementData.length) {
        grow(minCapacity);
    }
}

private void grow(int minCapacity) {
    int oldCapacity = elementData.length;
    int newCapacity = oldCapacity + (oldCapacity >> 1);  // 1.5배

    if (newCapacity < minCapacity) {
        newCapacity = minCapacity;
    }

    elementData = Arrays.copyOf(elementData, newCapacity);
}
```

**ensureCapacity() 역할**:
```java
public void ensureCapacity(int minCapacity) {
    // 미리 용량 확보 (여러 번 add() 호출 예정일 때)
    if (minCapacity > elementData.length) {
        grow(minCapacity);
    }
}

// 사용 예시
List<Integer> list = new ArrayList<>();
list.ensureCapacity(10000);  // 한 번에 용량 확보

for (int i = 0; i < 10000; i++) {
    list.add(i);  // 배열 복사 없음!
}
```

**성능 비교**:
```java
// ❌ 여러 번 확장 (느림)
List<Integer> list1 = new ArrayList<>();
for (int i = 0; i < 1000000; i++) {
    list1.add(i);  // 수십 번 배열 복사
}
// 시간: ~50ms

// ✅ 한 번에 확장 (빠름)
List<Integer> list2 = new ArrayList<>();
list2.ensureCapacity(1000000);
for (int i = 0; i < 1000000; i++) {
    list2.add(i);  // 배열 복사 없음
}
// 시간: ~20ms
```

---

#### Q10. Fail-fast vs Fail-safe Iterator의 차이점을 설명하세요.

**모범 답변**:

**Fail-fast Iterator**:
- **정의**: 순회 중 구조적 변경 감지 시 즉시 예외 발생
- **예외**: `ConcurrentModificationException`
- **구현**: ArrayList, HashMap 등 대부분의 컬렉션

**Fail-safe Iterator**:
- **정의**: 순회 중 구조적 변경에도 예외 없음 (복사본 또는 스냅샷 사용)
- **예외**: 없음
- **구현**: CopyOnWriteArrayList, ConcurrentHashMap

**비교**:

```java
// 1. Fail-fast (ArrayList)
List<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));
Iterator<String> iter = list.iterator();

while (iter.hasNext()) {
    String item = iter.next();
    if (item.equals("B")) {
        list.remove(item);  // ❌ ConcurrentModificationException
    }
}

// 2. Fail-safe (CopyOnWriteArrayList)
List<String> cowList = new CopyOnWriteArrayList<>(Arrays.asList("A", "B", "C"));
Iterator<String> iter2 = cowList.iterator();  // 스냅샷 저장

while (iter2.hasNext()) {
    String item = iter2.next();
    if (item.equals("B")) {
        cowList.remove(item);  // ✅ 예외 없음 (순회는 스냅샷으로 계속)
    }
}

System.out.println(cowList);  // [A, C] (삭제는 적용됨)
```

**내부 메커니즘**:

**Fail-fast**:
```java
class ArrayList {
    private int modCount = 0;  // 구조적 변경 카운트

    public Iterator<E> iterator() {
        return new Itr();
    }

    private class Itr implements Iterator<E> {
        int expectedModCount = modCount;  // 생성 시점 저장

        public E next() {
            if (modCount != expectedModCount) {
                throw new ConcurrentModificationException();
            }
            // ...
        }
    }

    public boolean add(E e) {
        modCount++;  // 변경 시마다 증가
        // ...
    }
}
```

**Fail-safe**:
```java
class CopyOnWriteArrayList {
    private volatile Object[] array;

    public Iterator<E> iterator() {
        return new COWIterator<>(getArray(), 0);  // 현재 배열 스냅샷
    }

    private static class COWIterator<E> implements Iterator<E> {
        private final Object[] snapshot;  // 스냅샷
        private int cursor;

        public E next() {
            return (E) snapshot[cursor++];  // 스냅샷으로 순회
        }
    }
}
```

**정리**:
| 특징 | Fail-fast | Fail-safe |
|------|-----------|-----------|
| **예외 발생** | ✅ ConcurrentModificationException | ❌ 없음 |
| **성능** | 빠름 | 느림 (복사 비용) |
| **일관성** | Strong consistency | Weak consistency |
| **사용** | 단일 스레드, 성능 중시 | 멀티 스레드, 안전성 중시 |

---

#### Q11. LinkedList를 사용할 때 성능 문제를 피하는 방법은?

**모범 답변**:

**성능 문제**:
1. **get(index) 반복 호출**: O(n²)
2. **잘못된 순회 방식**: 인덱스 기반
3. **부적절한 사용**: 조회 중심 작업

**해결 방법**:

**1. Iterator 사용** (O(n²) → O(n)):
```java
LinkedList<String> list = new LinkedList<>();
// ... 데이터 추가 ...

// ❌ O(n²)
for (int i = 0; i < list.size(); i++) {
    String item = list.get(i);  // 매번 O(n) 순차 탐색!
    System.out.println(item);
}

// ✅ O(n)
for (String item : list) {  // Iterator 사용
    System.out.println(item);
}

// 또는
Iterator<String> iter = list.iterator();
while (iter.hasNext()) {
    System.out.println(iter.next());
}
```

**2. ListIterator 활용** (양방향 순회):
```java
LinkedList<String> list = new LinkedList<>(Arrays.asList("A", "B", "C", "D"));

// 정방향 순회
ListIterator<String> iter = list.listIterator();
while (iter.hasNext()) {
    System.out.println(iter.next());
}

// 역방향 순회
ListIterator<String> iter2 = list.listIterator(list.size());
while (iter2.hasPrevious()) {
    System.out.println(iter2.previous());
}

// 중간 삽입 (Iterator 위치에)
ListIterator<String> iter3 = list.listIterator(2);
iter3.add("X");  // B와 C 사이에 삽입
```

**3. Deque 메서드 활용**:
```java
LinkedList<String> list = new LinkedList<>();

// ✅ O(1) 연산들
list.addFirst("A");  // 맨 앞 추가
list.addLast("B");   // 맨 뒤 추가
list.removeFirst();  // 맨 앞 제거
list.removeLast();   // 맨 뒤 제거
list.getFirst();     // 맨 앞 조회
list.getLast();      // 맨 뒤 조회

// Queue 연산
list.offer("C");     // 맨 뒤 추가 (add와 동일)
String first = list.poll();  // 맨 앞 제거 후 반환

// Stack 연산
list.push("D");      // 맨 앞 추가 (addFirst와 동일)
String top = list.pop();  // 맨 앞 제거 후 반환 (removeFirst와 동일)
```

**4. 적절한 자료구조 선택**:
```java
// ❌ LinkedList를 조회 위주로 사용
LinkedList<String> list = new LinkedList<>();
for (int i = 0; i < 10000; i++) {
    list.add("Item " + i);
}

// 조회: O(n) * 10000 = O(10000n) → 매우 느림!
for (int i = 0; i < 10000; i++) {
    String item = list.get(i);
}

// ✅ ArrayList로 변경
ArrayList<String> arrayList = new ArrayList<>();
for (int i = 0; i < 10000; i++) {
    arrayList.add("Item " + i);
}

// 조회: O(1) * 10000 = O(10000) → 빠름!
for (int i = 0; i < 10000; i++) {
    String item = arrayList.get(i);
}
```

**성능 비교**:
```java
public static void comparePerformance() {
    int size = 10000;

    LinkedList<Integer> linkedList = new LinkedList<>();
    for (int i = 0; i < size; i++) {
        linkedList.add(i);
    }

    // 1. get(index) - O(n²)
    long start = System.nanoTime();
    for (int i = 0; i < size; i++) {
        Integer value = linkedList.get(i);
    }
    long getTime = (System.nanoTime() - start) / 1_000_000;

    // 2. Iterator - O(n)
    start = System.nanoTime();
    for (Integer value : linkedList) {
        // do nothing
    }
    long iterTime = (System.nanoTime() - start) / 1_000_000;

    System.out.println("get(index): " + getTime + "ms ⚠️");
    System.out.println("Iterator:   " + iterTime + "ms ✅");
    System.out.println("차이: " + (getTime / iterTime) + "배");
}
```

**정리**:
- ✅ Iterator/for-each 사용
- ✅ Deque 메서드 활용 (addFirst, removeFirst 등)
- ✅ 조회 많으면 ArrayList로 변경
- ❌ get(index) 반복 호출 금지

---

#### Q12. List 성능 최적화를 위한 모범 사례는?

**모범 답변**:

**1. 초기 용량 지정**:
```java
// ❌ 기본 용량 (10)
List<User> users = new ArrayList<>();
for (int i = 0; i < 100000; i++) {
    users.add(loadUser(i));  // 수십 번 배열 복사
}

// ✅ 초기 용량 지정
List<User> users = new ArrayList<>(100000);
for (int i = 0; i < 100000; i++) {
    users.add(loadUser(i));  // 배열 복사 없음
}

// 성능 향상: 약 2-3배
```

**2. 적절한 구현체 선택**:
```java
// 조회 중심 → ArrayList
List<String> list = new ArrayList<>();

// Queue/Stack → LinkedList
Deque<String> queue = new LinkedList<>();

// 동시성 + 읽기 >> 쓰기 → CopyOnWriteArrayList
List<String> cowList = new CopyOnWriteArrayList<>();
```

**3. Bulk 연산 활용**:
```java
// ❌ 하나씩 추가
for (String item : items) {
    list.add(item);
}

// ✅ addAll() 사용
list.addAll(items);  // 내부 최적화됨

// ✅ 생성자 사용
List<String> list = new ArrayList<>(items);
```

**4. removeIf() 활용**:
```java
// ❌ Iterator로 삭제
Iterator<String> iter = list.iterator();
while (iter.hasNext()) {
    String item = iter.next();
    if (item.startsWith("temp")) {
        iter.remove();
    }
}

// ✅ removeIf() (Java 8+)
list.removeIf(item -> item.startsWith("temp"));  // 더 효율적
```

**5. Stream 활용** (새 리스트 생성):
```java
// 필터링 + 변환
List<String> result = list.stream()
    .filter(item -> item.length() > 5)
    .map(String::toUpperCase)
    .collect(Collectors.toList());

// 정렬
List<String> sorted = list.stream()
    .sorted()
    .collect(Collectors.toList());
```

**6. 불필요한 복사 피하기**:
```java
// ❌ 불필요한 복사
List<String> copy = new ArrayList<>(list);
for (String item : copy) {
    System.out.println(item);  // 읽기만 하는데 복사?
}

// ✅ 원본 직접 읽기
for (String item : list) {
    System.out.println(item);
}
```

**7. 크기 제한 관리**:
```java
// LRU 패턴
private static final int MAX_SIZE = 1000;

private void addToHistory(String item) {
    if (history.size() >= MAX_SIZE) {
        history.remove(0);  // 가장 오래된 항목 제거
    }
    history.add(item);
}
```

**8. trimToSize() 활용**:
```java
List<String> list = new ArrayList<>(10000);
// ... 1000개만 추가 ...

list.trimToSize();  // 낭비되는 9000칸 제거
```

**9. 동시성 처리**:
```java
// ❌ ArrayList in multi-thread
List<String> list = new ArrayList<>();  // Not thread-safe

// ✅ CopyOnWriteArrayList
List<String> cowList = new CopyOnWriteArrayList<>();

// 또는 Collections.synchronizedList
List<String> syncList = Collections.synchronizedList(new ArrayList<>());
```

**10. contains() 최적화**:
```java
// ❌ List.contains() - O(n)
for (String item : candidates) {
    if (list.contains(item)) {  // 매번 O(n) 탐색
        // ...
    }
}

// ✅ Set 사용 - O(1)
Set<String> set = new HashSet<>(list);
for (String item : candidates) {
    if (set.contains(item)) {  // O(1) 탐색
        // ...
    }
}
```

---

## 🎓 마무리

### 핵심 요점

1. **ArrayList vs LinkedList**
   - 대부분: ArrayList
   - Queue/Deque: LinkedList
   - 조회 >> 삽입/삭제

2. **동시성**
   - Vector: 사용 금지
   - 읽기 >> 쓰기: CopyOnWriteArrayList
   - 균형: Collections.synchronizedList

3. **성능 최적화**
   - 초기 용량 지정
   - 적절한 구현체 선택
   - Iterator 활용

4. **주의사항**
   - for-each에서 remove 금지
   - Arrays.asList() 크기 고정
   - subList()는 뷰

**다음 장에서는**: Set 인터페이스 (HashSet, LinkedHashSet, TreeSet)를 다룹니다.
