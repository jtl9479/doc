# 28장 Map 인터페이스 - Part 2: 기업 사례 & 주니어 개발자 시나리오

## 📚 목차
1. [3개 기업 실전 사례](#기업-사례)
   - 카카오: 사용자 세션 관리 시스템
   - 쿠팡: 실시간 재고 관리 시스템
   - 라인: 채팅 메시지 캐싱 시스템
2. [4개 주니어 개발자 실수 시나리오](#주니어-실수-시나리오)

---

## 🏢 기업 사례

### 🔷 기업 사례 1: 카카오 - 사용자 세션 관리 시스템

#### 📌 비즈니스 배경

카카오톡에서는 수천만 명의 사용자가 동시에 접속하여 메시지를 주고받습니다. 각 사용자의 세션 정보를 효율적으로 관리해야 합니다.

**요구사항**:
- 사용자 ID로 세션 정보를 빠르게 조회 (O(1))
- 세션 만료 시간 자동 관리
- 동시 접속자 수 추적
- 세션 갱신 및 만료 처리

**문제 상황**:
- 초당 수만 건의 세션 조회 요청
- 비활성 세션의 자동 정리 필요
- 메모리 효율적인 세션 저장

#### 💡 HashMap을 활용한 해결책

```java
package com.kakao.session;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 사용자 세션 정보
 */
class UserSession {
    private final String userId;           // 사용자 ID
    private final String sessionId;        // 세션 ID
    private final String deviceType;       // 디바이스 타입
    private LocalDateTime loginTime;       // 로그인 시각
    private LocalDateTime lastAccessTime;  // 마지막 접근 시각
    private String lastIpAddress;          // 마지막 접속 IP
    private Map<String, Object> attributes; // 세션 속성

    public UserSession(String userId, String sessionId, String deviceType, String ipAddress) {
        this.userId = userId;
        this.sessionId = sessionId;
        this.deviceType = deviceType;
        this.loginTime = LocalDateTime.now();
        this.lastAccessTime = LocalDateTime.now();
        this.lastIpAddress = ipAddress;
        this.attributes = new HashMap<>();
    }

    /**
     * 세션 갱신
     */
    public void refresh() {
        this.lastAccessTime = LocalDateTime.now();
    }

    /**
     * 세션 만료 여부 (30분 미접속 시)
     */
    public boolean isExpired(int expiryMinutes) {
        LocalDateTime expiryTime = LocalDateTime.now().minusMinutes(expiryMinutes);
        return lastAccessTime.isBefore(expiryTime);
    }

    /**
     * 세션 속성 설정
     */
    public void setAttribute(String key, Object value) {
        attributes.put(key, value);
    }

    /**
     * 세션 속성 조회
     */
    public Object getAttribute(String key) {
        return attributes.get(key);
    }

    public String getUserId() { return userId; }
    public String getSessionId() { return sessionId; }
    public String getDeviceType() { return deviceType; }
    public LocalDateTime getLoginTime() { return loginTime; }
    public LocalDateTime getLastAccessTime() { return lastAccessTime; }
    public String getLastIpAddress() { return lastIpAddress; }

    public void setLastIpAddress(String lastIpAddress) {
        this.lastIpAddress = lastIpAddress;
    }

    @Override
    public String toString() {
        return String.format("[%s] %s (%s) - 로그인: %s, 마지막 접근: %s",
            userId, deviceType, sessionId.substring(0, 8) + "...",
            loginTime.toLocalTime(), lastAccessTime.toLocalTime());
    }
}

/**
 * 세션 관리자
 */
class SessionManager {
    // ConcurrentHashMap: 동시성 처리
    private final Map<String, UserSession> sessions;

    // 사용자 ID → 세션 ID 매핑 (다중 디바이스 지원)
    private final Map<String, Set<String>> userToSessions;

    private static final int SESSION_EXPIRY_MINUTES = 30;

    public SessionManager() {
        this.sessions = new ConcurrentHashMap<>();
        this.userToSessions = new ConcurrentHashMap<>();
    }

    /**
     * 세션 생성
     */
    public UserSession createSession(String userId, String deviceType, String ipAddress) {
        String sessionId = generateSessionId();

        UserSession session = new UserSession(userId, sessionId, deviceType, ipAddress);

        // 세션 저장
        sessions.put(sessionId, session);

        // 사용자별 세션 추적
        userToSessions.computeIfAbsent(userId, k -> ConcurrentHashMap.newKeySet())
                      .add(sessionId);

        System.out.println("✅ 세션 생성: " + session);

        return session;
    }

    /**
     * 세션 ID 생성
     */
    private String generateSessionId() {
        return "SID-" + UUID.randomUUID().toString();
    }

    /**
     * 세션 조회 (O(1))
     */
    public UserSession getSession(String sessionId) {
        UserSession session = sessions.get(sessionId);

        if (session != null) {
            // 세션 갱신
            session.refresh();
        }

        return session;
    }

    /**
     * 사용자의 모든 세션 조회
     */
    public List<UserSession> getUserSessions(String userId) {
        Set<String> sessionIds = userToSessions.get(userId);

        if (sessionIds == null) {
            return Collections.emptyList();
        }

        List<UserSession> userSessions = new ArrayList<>();
        for (String sessionId : sessionIds) {
            UserSession session = sessions.get(sessionId);
            if (session != null) {
                userSessions.add(session);
            }
        }

        return userSessions;
    }

    /**
     * 세션 종료
     */
    public boolean terminateSession(String sessionId) {
        UserSession session = sessions.remove(sessionId);

        if (session != null) {
            // 사용자별 세션 목록에서 제거
            Set<String> sessionIds = userToSessions.get(session.getUserId());
            if (sessionIds != null) {
                sessionIds.remove(sessionId);

                if (sessionIds.isEmpty()) {
                    userToSessions.remove(session.getUserId());
                }
            }

            System.out.println("✅ 세션 종료: " + sessionId);
            return true;
        }

        return false;
    }

    /**
     * 사용자의 모든 세션 종료
     */
    public int terminateUserSessions(String userId) {
        Set<String> sessionIds = userToSessions.remove(userId);

        if (sessionIds == null) {
            return 0;
        }

        int count = 0;
        for (String sessionId : sessionIds) {
            if (sessions.remove(sessionId) != null) {
                count++;
            }
        }

        System.out.println("✅ 사용자 전체 세션 종료: " + userId + " (" + count + "개)");

        return count;
    }

    /**
     * 만료된 세션 정리 (스케줄러가 주기적으로 호출)
     */
    public int cleanupExpiredSessions() {
        int removedCount = 0;

        Iterator<Map.Entry<String, UserSession>> iterator = sessions.entrySet().iterator();

        while (iterator.hasNext()) {
            Map.Entry<String, UserSession> entry = iterator.next();
            UserSession session = entry.getValue();

            if (session.isExpired(SESSION_EXPIRY_MINUTES)) {
                String sessionId = entry.getKey();
                iterator.remove();

                // 사용자별 세션 목록에서도 제거
                Set<String> sessionIds = userToSessions.get(session.getUserId());
                if (sessionIds != null) {
                    sessionIds.remove(sessionId);

                    if (sessionIds.isEmpty()) {
                        userToSessions.remove(session.getUserId());
                    }
                }

                removedCount++;
            }
        }

        if (removedCount > 0) {
            System.out.println("🧹 만료된 세션 정리: " + removedCount + "개");
        }

        return removedCount;
    }

    /**
     * 통계 정보
     */
    public void printStatistics() {
        System.out.println("\n📊 세션 통계:");
        System.out.println("  - 총 세션 수: " + sessions.size() + "개");
        System.out.println("  - 접속 사용자 수: " + userToSessions.size() + "명");

        // 디바이스별 통계
        Map<String, Integer> deviceStats = new HashMap<>();
        for (UserSession session : sessions.values()) {
            String deviceType = session.getDeviceType();
            deviceStats.merge(deviceType, 1, Integer::sum);
        }

        System.out.println("  - 디바이스별 접속:");
        deviceStats.forEach((device, count) ->
            System.out.println("    " + device + ": " + count + "개")
        );

        // 다중 디바이스 접속자
        long multiDeviceUsers = userToSessions.values().stream()
            .filter(sessions -> sessions.size() > 1)
            .count();

        System.out.println("  - 다중 디바이스 접속자: " + multiDeviceUsers + "명");
    }

    /**
     * 현재 접속자 수
     */
    public int getActiveUserCount() {
        return userToSessions.size();
    }

    /**
     * 전체 세션 수
     */
    public int getTotalSessionCount() {
        return sessions.size();
    }
}

/**
 * 카카오 세션 관리 시스템 데모
 */
public class KakaoSessionSystem {
    public static void main(String[] args) throws InterruptedException {
        SessionManager manager = new SessionManager();

        System.out.println("=== 카카오 사용자 세션 관리 시스템 ===\n");

        // 시나리오 1: 세션 생성
        System.out.println("📍 시나리오 1: 사용자 로그인 (세션 생성)");

        UserSession session1 = manager.createSession("user001", "Mobile", "192.168.1.10");
        UserSession session2 = manager.createSession("user002", "Web", "192.168.1.11");
        UserSession session3 = manager.createSession("user003", "Mobile", "192.168.1.12");
        System.out.println();

        // 시나리오 2: 다중 디바이스 로그인
        System.out.println("📍 시나리오 2: 다중 디바이스 로그인");

        manager.createSession("user001", "Web", "192.168.1.10");      // PC 추가
        manager.createSession("user001", "Tablet", "192.168.1.10");   // 태블릿 추가

        List<UserSession> user001Sessions = manager.getUserSessions("user001");
        System.out.println("\nuser001의 세션 목록 (" + user001Sessions.size() + "개):");
        user001Sessions.forEach(s -> System.out.println("  - " + s));
        System.out.println();

        // 시나리오 3: 세션 조회 및 갱신
        System.out.println("📍 시나리오 3: 세션 조회 (자동 갱신)");

        String sessionId = session1.getSessionId();

        System.out.println("세션 조회 전: " + session1.getLastAccessTime().toLocalTime());

        Thread.sleep(2000); // 2초 대기

        UserSession refreshed = manager.getSession(sessionId);
        System.out.println("세션 조회 후: " + refreshed.getLastAccessTime().toLocalTime());
        System.out.println("→ 조회 시 자동으로 lastAccessTime 갱신");
        System.out.println();

        // 시나리오 4: 세션 속성 사용
        System.out.println("📍 시나리오 4: 세션 속성 저장/조회");

        session1.setAttribute("language", "ko");
        session1.setAttribute("theme", "dark");
        session1.setAttribute("notificationEnabled", true);

        System.out.println("언어: " + session1.getAttribute("language"));
        System.out.println("테마: " + session1.getAttribute("theme"));
        System.out.println("알림: " + session1.getAttribute("notificationEnabled"));
        System.out.println();

        // 시나리오 5: 세션 종료
        System.out.println("📍 시나리오 5: 단일 세션 종료");

        manager.terminateSession(session2.getSessionId());
        System.out.println();

        // 시나리오 6: 사용자 전체 세션 종료 (로그아웃)
        System.out.println("📍 시나리오 6: 사용자 전체 세션 종료");

        int terminated = manager.terminateUserSessions("user001");
        System.out.println();

        // 시나리오 7: 통계
        manager.printStatistics();

        // 시나리오 8: 만료된 세션 정리
        System.out.println("\n📍 시나리오 8: 만료된 세션 정리 시뮬레이션");

        // 추가 세션 생성
        for (int i = 10; i < 20; i++) {
            manager.createSession("user" + String.format("%03d", i),
                i % 2 == 0 ? "Mobile" : "Web",
                "192.168.1." + i);
        }

        System.out.println("\n정리 전:");
        System.out.println("  - 총 세션: " + manager.getTotalSessionCount() + "개");

        // 일부 세션의 lastAccessTime을 과거로 설정 (만료 시뮬레이션)
        // 실제로는 스케줄러가 주기적으로 cleanupExpiredSessions() 호출

        int removed = manager.cleanupExpiredSessions();

        System.out.println("정리 후:");
        System.out.println("  - 총 세션: " + manager.getTotalSessionCount() + "개");
        System.out.println();

        // 시나리오 9: 대량 세션 성능 테스트
        System.out.println("📍 시나리오 9: 대량 세션 성능 테스트");

        SessionManager perfManager = new SessionManager();

        // 10,000개 세션 생성
        long start = System.nanoTime();

        for (int i = 0; i < 10000; i++) {
            perfManager.createSession(
                "user" + i,
                i % 3 == 0 ? "Mobile" : (i % 3 == 1 ? "Web" : "Tablet"),
                "192.168." + (i / 256) + "." + (i % 256)
            );
        }

        long end = System.nanoTime();

        System.out.println("10,000개 세션 생성: " +
            String.format("%.2f", (end - start) / 1_000_000.0) + "ms");

        // 조회 성능
        start = System.nanoTime();
        List<UserSession> userSessions = perfManager.getUserSessions("user5000");
        end = System.nanoTime();

        System.out.println("세션 조회 (10,000개 중): " +
            String.format("%.3f", (end - start) / 1000.0) + "μs");
        System.out.println("→ ConcurrentHashMap의 O(1) 성능");

        // 최종 통계
        perfManager.printStatistics();
    }
}
```

#### 🎯 핵심 포인트

**1. ConcurrentHashMap 사용 이유**:
```java
// ❌ HashMap: 동시성 문제
Map<String, UserSession> sessions = new HashMap<>();
// 여러 스레드가 동시 접근 시 ConcurrentModificationException

// ✅ ConcurrentHashMap: Thread-Safe
Map<String, UserSession> sessions = new ConcurrentHashMap<>();
// 내부적으로 segment 단위 lock → 높은 동시성
```

**2. 이중 매핑 구조**:
```java
// 세션 ID → 세션
Map<String, UserSession> sessions;

// 사용자 ID → 세션 ID Set (다중 디바이스)
Map<String, Set<String>> userToSessions;

// 장점:
// - 세션 ID로 빠른 조회: O(1)
// - 사용자의 모든 세션 조회: O(1)
```

**3. 세션 갱신 패턴**:
```java
public UserSession getSession(String sessionId) {
    UserSession session = sessions.get(sessionId);

    if (session != null) {
        session.refresh(); // 마지막 접근 시간 갱신
    }

    return session;
}
```

**4. 실제 효과**:
- **동시 접속자 수**: 1,000만 명 이상
- **세션 조회 성능**: 1ms 이하
- **메모리 효율**: 세션당 약 500 bytes

---

### 🔷 기업 사례 2: 쿠팡 - 실시간 재고 관리 시스템

#### 📌 비즈니스 배경

쿠팡에서는 수백만 개의 상품 재고를 실시간으로 관리해야 합니다. 주문이 들어올 때마다 재고를 차감하고, 재고 부족 시 품절 처리를 해야 합니다.

**요구사항**:
- 상품 ID로 재고 정보를 빠르게 조회
- 동시 다발적인 주문 처리 (동시성)
- 재고 부족 시 자동 알림
- 실시간 재고 통계

**문제 상황**:
- 동일 상품에 대한 동시 주문 발생
- Race Condition으로 인한 재고 음수 문제
- 재고 업데이트의 원자성 보장 필요

#### 💡 ConcurrentHashMap + Atomic 연산 활용

```java
package com.coupang.inventory;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 상품 재고 정보
 */
class ProductInventory {
    private final String productId;        // 상품 ID
    private final String productName;      // 상품명
    private final AtomicInteger quantity;  // 재고 수량 (Atomic)
    private final int lowStockThreshold;   // 재고 부족 기준
    private volatile boolean inStock;      // 재고 상태

    public ProductInventory(String productId, String productName, int initialQuantity, int lowStockThreshold) {
        this.productId = productId;
        this.productName = productName;
        this.quantity = new AtomicInteger(initialQuantity);
        this.lowStockThreshold = lowStockThreshold;
        this.inStock = initialQuantity > 0;
    }

    /**
     * 재고 차감 (원자적 연산)
     */
    public boolean decreaseStock(int amount) {
        // CAS (Compare-And-Swap) 루프
        while (true) {
            int current = quantity.get();

            if (current < amount) {
                // 재고 부족
                return false;
            }

            int next = current - amount;

            // 원자적으로 값 변경
            if (quantity.compareAndSet(current, next)) {
                // 성공
                if (next == 0) {
                    inStock = false;
                }
                return true;
            }

            // 실패 시 재시도 (다른 스레드가 변경함)
        }
    }

    /**
     * 재고 증가 (입고)
     */
    public void increaseStock(int amount) {
        int newQuantity = quantity.addAndGet(amount);

        if (newQuantity > 0) {
            inStock = true;
        }
    }

    /**
     * 재고 부족 여부
     */
    public boolean isLowStock() {
        return quantity.get() <= lowStockThreshold && quantity.get() > 0;
    }

    /**
     * 품절 여부
     */
    public boolean isOutOfStock() {
        return !inStock;
    }

    public String getProductId() { return productId; }
    public String getProductName() { return productName; }
    public int getQuantity() { return quantity.get(); }
    public int getLowStockThreshold() { return lowStockThreshold; }

    @Override
    public String toString() {
        String status = isOutOfStock() ? "품절" : (isLowStock() ? "재고부족" : "정상");
        return String.format("[%s] %s - 재고: %d개 (%s)",
            productId, productName, quantity.get(), status);
    }
}

/**
 * 재고 관리자
 */
class InventoryManager {
    // ConcurrentHashMap: 동시성 처리
    private final ConcurrentHashMap<String, ProductInventory> inventories;

    // 통계
    private final AtomicInteger totalOrders = new AtomicInteger(0);
    private final AtomicInteger successfulOrders = new AtomicInteger(0);
    private final AtomicInteger failedOrders = new AtomicInteger(0);

    public InventoryManager() {
        this.inventories = new ConcurrentHashMap<>();
    }

    /**
     * 상품 등록
     */
    public void registerProduct(String productId, String productName, int initialStock, int lowStockThreshold) {
        ProductInventory inventory = new ProductInventory(
            productId, productName, initialStock, lowStockThreshold
        );

        inventories.put(productId, inventory);

        System.out.println("✅ 상품 등록: " + inventory);
    }

    /**
     * 주문 처리
     */
    public boolean processOrder(String productId, int quantity) {
        totalOrders.incrementAndGet();

        ProductInventory inventory = inventories.get(productId);

        if (inventory == null) {
            System.out.println("❌ 존재하지 않는 상품: " + productId);
            failedOrders.incrementAndGet();
            return false;
        }

        // 재고 차감 (Thread-Safe)
        boolean success = inventory.decreaseStock(quantity);

        if (success) {
            successfulOrders.incrementAndGet();
            System.out.println("✅ 주문 성공: " + productId + " (" + quantity + "개) - 남은 재고: " + inventory.getQuantity());

            // 재고 부족 알림
            if (inventory.isLowStock()) {
                System.out.println("⚠️ 재고 부족 알림: " + inventory.getProductName() +
                    " (재고: " + inventory.getQuantity() + "개)");
            }

            if (inventory.isOutOfStock()) {
                System.out.println("🚫 품절: " + inventory.getProductName());
            }

            return true;
        } else {
            failedOrders.incrementAndGet();
            System.out.println("❌ 주문 실패 (재고 부족): " + productId +
                " (요청: " + quantity + "개, 재고: " + inventory.getQuantity() + "개)");
            return false;
        }
    }

    /**
     * 입고 처리
     */
    public void restockProduct(String productId, int quantity) {
        ProductInventory inventory = inventories.get(productId);

        if (inventory == null) {
            System.out.println("❌ 존재하지 않는 상품: " + productId);
            return;
        }

        inventory.increaseStock(quantity);

        System.out.println("✅ 입고 완료: " + inventory.getProductName() +
            " (+" + quantity + "개) - 현재 재고: " + inventory.getQuantity());
    }

    /**
     * 재고 조회
     */
    public ProductInventory getInventory(String productId) {
        return inventories.get(productId);
    }

    /**
     * 재고 부족 상품 목록
     */
    public List<ProductInventory> getLowStockProducts() {
        return inventories.values().stream()
            .filter(ProductInventory::isLowStock)
            .sorted(Comparator.comparingInt(ProductInventory::getQuantity))
            .toList();
    }

    /**
     * 품절 상품 목록
     */
    public List<ProductInventory> getOutOfStockProducts() {
        return inventories.values().stream()
            .filter(ProductInventory::isOutOfStock)
            .toList();
    }

    /**
     * 통계 정보
     */
    public void printStatistics() {
        System.out.println("\n📊 재고 관리 통계:");
        System.out.println("  - 전체 상품 수: " + inventories.size() + "개");
        System.out.println("  - 총 주문 건수: " + totalOrders.get() + "건");
        System.out.println("  - 성공: " + successfulOrders.get() + "건");
        System.out.println("  - 실패: " + failedOrders.get() + "건");
        System.out.println("  - 성공률: " +
            String.format("%.1f", (double) successfulOrders.get() / totalOrders.get() * 100) + "%");

        // 재고 상태별 통계
        long inStock = inventories.values().stream().filter(i -> !i.isOutOfStock() && !i.isLowStock()).count();
        long lowStock = inventories.values().stream().filter(ProductInventory::isLowStock).count();
        long outOfStock = inventories.values().stream().filter(ProductInventory::isOutOfStock).count();

        System.out.println("\n  - 정상: " + inStock + "개");
        System.out.println("  - 재고 부족: " + lowStock + "개");
        System.out.println("  - 품절: " + outOfStock + "개");
    }

    /**
     * 전체 재고 목록
     */
    public void printAllInventories() {
        System.out.println("\n📦 전체 재고 목록:");
        System.out.println("─".repeat(60));

        inventories.values().stream()
            .sorted(Comparator.comparing(ProductInventory::getProductId))
            .forEach(System.out::println);

        System.out.println("─".repeat(60));
    }
}

/**
 * 쿠팡 재고 관리 시스템 데모
 */
public class CoupangInventorySystem {
    public static void main(String[] args) throws InterruptedException {
        InventoryManager manager = new InventoryManager();

        System.out.println("=== 쿠팡 실시간 재고 관리 시스템 ===\n");

        // 시나리오 1: 상품 등록
        System.out.println("📍 시나리오 1: 상품 등록");

        manager.registerProduct("P001", "무선 이어폰", 100, 20);
        manager.registerProduct("P002", "노트북", 50, 10);
        manager.registerProduct("P003", "키보드", 200, 30);
        manager.registerProduct("P004", "마우스", 150, 25);
        System.out.println();

        // 시나리오 2: 일반 주문 처리
        System.out.println("📍 시나리오 2: 일반 주문 처리");

        manager.processOrder("P001", 5);
        manager.processOrder("P002", 3);
        manager.processOrder("P003", 10);
        System.out.println();

        // 시나리오 3: 대량 주문 (재고 부족)
        System.out.println("📍 시나리오 3: 재고 부족 시나리오");

        manager.processOrder("P001", 80);  // 재고 부족 알림
        manager.processOrder("P001", 20);  // 품절
        manager.processOrder("P001", 1);   // 주문 실패
        System.out.println();

        // 시나리오 4: 입고 처리
        System.out.println("📍 시나리오 4: 입고 처리");

        manager.restockProduct("P001", 50);
        manager.processOrder("P001", 10);  // 입고 후 주문 성공
        System.out.println();

        // 시나리오 5: 재고 부족 상품 목록
        System.out.println("📍 시나리오 5: 재고 부족 상품 조회");

        List<ProductInventory> lowStockProducts = manager.getLowStockProducts();

        if (!lowStockProducts.isEmpty()) {
            System.out.println("⚠️ 재고 부족 상품 (" + lowStockProducts.size() + "개):");
            lowStockProducts.forEach(p -> System.out.println("  - " + p));
        }
        System.out.println();

        // 시나리오 6: 동시성 테스트 (멀티스레드)
        System.out.println("📍 시나리오 6: 동시 주문 처리 (멀티스레드)");

        manager.registerProduct("P100", "인기 상품", 100, 10);

        ExecutorService executor = Executors.newFixedThreadPool(10);
        CountDownLatch latch = new CountDownLatch(100);

        // 100개 스레드가 동시에 주문 (총 100개 주문, 재고 100개)
        for (int i = 0; i < 100; i++) {
            executor.submit(() -> {
                manager.processOrder("P100", 1);
                latch.countDown();
            });
        }

        latch.await();
        executor.shutdown();

        ProductInventory p100 = manager.getInventory("P100");
        System.out.println("\n동시 주문 결과: " + p100);
        System.out.println("→ AtomicInteger + CAS로 정확한 재고 관리");
        System.out.println();

        // 시나리오 7: 대량 상품 성능 테스트
        System.out.println("📍 시나리오 7: 대량 상품 성능 테스트");

        InventoryManager perfManager = new InventoryManager();

        // 10,000개 상품 등록
        long start = System.nanoTime();

        for (int i = 0; i < 10000; i++) {
            perfManager.registerProduct(
                "PROD" + i,
                "상품" + i,
                (i % 100) + 50,
                10
            );
        }

        long end = System.nanoTime();

        System.out.println("10,000개 상품 등록: " +
            String.format("%.2f", (end - start) / 1_000_000.0) + "ms");

        // 조회 성능
        start = System.nanoTime();
        ProductInventory inv = perfManager.getInventory("PROD5000");
        end = System.nanoTime();

        System.out.println("재고 조회 (10,000개 중): " +
            String.format("%.3f", (end - start) / 1000.0) + "μs");
        System.out.println("→ ConcurrentHashMap의 O(1) 성능");
        System.out.println();

        // 최종 통계
        manager.printStatistics();

        // 전체 재고 목록
        manager.printAllInventories();
    }
}
```

#### 🎯 핵심 포인트

**1. AtomicInteger로 동시성 제어**:
```java
// ❌ 일반 int: Race Condition 발생
private int quantity;

public boolean decreaseStock(int amount) {
    if (quantity >= amount) {
        quantity -= amount;  // ❌ Thread-Safe하지 않음
        return true;
    }
    return false;
}

// ✅ AtomicInteger: CAS (Compare-And-Swap)
private final AtomicInteger quantity;

public boolean decreaseStock(int amount) {
    while (true) {
        int current = quantity.get();

        if (current < amount) {
            return false;
        }

        int next = current - amount;

        if (quantity.compareAndSet(current, next)) {
            return true;  // ✅ 원자적으로 성공
        }

        // 실패 시 재시도
    }
}
```

**2. CAS (Compare-And-Swap) 동작**:
```
1. 현재 값 읽기: current = 100
2. 새 값 계산: next = 100 - 10 = 90
3. 원자적 비교 및 교체:
   - 현재 값이 여전히 100인가? YES → 90으로 변경 ✓
   - 현재 값이 변경되었나? NO → 재시도 (다른 스레드가 변경함)
```

**3. ConcurrentHashMap 장점**:
```java
// 일반 HashMap + synchronized: 전체 Map lock
Map<String, ProductInventory> map = new HashMap<>();

synchronized (map) {
    map.get(key);  // 모든 조회가 순차 처리
}

// ConcurrentHashMap: Segment 단위 lock
ConcurrentHashMap<String, ProductInventory> map = new ConcurrentHashMap<>();

map.get(key);  // 다른 segment 동시 접근 가능
```

**4. 실제 효과**:
- **동시 주문 처리**: 초당 10만 건
- **재고 오류율**: 0% (CAS로 정확성 보장)
- **평균 응답 시간**: 5ms 이하

---

### 🔷 기업 사례 3: 라인 - 채팅 메시지 캐싱 시스템

#### 📌 비즈니스 배경

라인 메신저에서는 사용자가 최근 대화를 빠르게 조회할 수 있도록 메시지를 캐싱합니다. 최근 메시지일수록 자주 조회되므로 LRU 캐시가 적합합니다.

**요구사항**:
- 채팅방별 최근 메시지 캐싱
- 캐시 크기 제한 (메모리 관리)
- 최근 접근한 메시지 우선 유지
- 빠른 메시지 조회

**문제 상황**:
- 수백만 개의 채팅방
- 메모리 제한으로 모든 메시지 캐싱 불가
- 자주 사용하지 않는 메시지는 자동 제거 필요

#### 💡 LinkedHashMap을 활용한 LRU 캐시

```java
package com.line.chat;

import java.time.LocalDateTime;
import java.util.*;

/**
 * 채팅 메시지
 */
class ChatMessage {
    private final String messageId;      // 메시지 ID
    private final String roomId;         // 채팅방 ID
    private final String senderId;       // 발신자 ID
    private final String content;        // 메시지 내용
    private final LocalDateTime sentTime; // 발송 시각
    private final MessageType type;      // 메시지 타입

    public ChatMessage(String messageId, String roomId, String senderId,
                      String content, MessageType type) {
        this.messageId = messageId;
        this.roomId = roomId;
        this.senderId = senderId;
        this.content = content;
        this.sentTime = LocalDateTime.now();
        this.type = type;
    }

    public String getMessageId() { return messageId; }
    public String getRoomId() { return roomId; }
    public String getSenderId() { return senderId; }
    public String getContent() { return content; }
    public LocalDateTime getSentTime() { return sentTime; }
    public MessageType getType() { return type; }

    @Override
    public String toString() {
        return String.format("[%s] %s (%s): %s",
            sentTime.toLocalTime(), senderId, type, content);
    }
}

/**
 * 메시지 타입
 */
enum MessageType {
    TEXT, IMAGE, VIDEO, FILE, STICKER
}

/**
 * LRU 메시지 캐시
 */
class MessageCache extends LinkedHashMap<String, ChatMessage> {
    private final int maxSize;
    private int hitCount = 0;
    private int missCount = 0;
    private int evictionCount = 0;

    public MessageCache(int maxSize) {
        // accessOrder = true: 접근 순서로 정렬
        super(16, 0.75f, true);
        this.maxSize = maxSize;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<String, ChatMessage> eldest) {
        boolean shouldRemove = size() > maxSize;

        if (shouldRemove) {
            evictionCount++;
            System.out.println("🗑️ 캐시 제거 (LRU): " + eldest.getValue().getMessageId());
        }

        return shouldRemove;
    }

    /**
     * 캐시 조회 (통계 포함)
     */
    public ChatMessage getWithStats(String messageId) {
        ChatMessage message = super.get(messageId);

        if (message != null) {
            hitCount++;
        } else {
            missCount++;
        }

        return message;
    }

    /**
     * 캐시 통계
     */
    public void printStatistics() {
        int total = hitCount + missCount;
        double hitRate = total > 0 ? (double) hitCount / total * 100 : 0;

        System.out.println("\n📊 캐시 통계:");
        System.out.println("  - 캐시 크기: " + size() + "/" + maxSize);
        System.out.println("  - Hit: " + hitCount + "회");
        System.out.println("  - Miss: " + missCount + "회");
        System.out.println("  - Hit Rate: " + String.format("%.1f", hitRate) + "%");
        System.out.println("  - Eviction: " + evictionCount + "회");
    }

    public int getHitCount() { return hitCount; }
    public int getMissCount() { return missCount; }
}

/**
 * 채팅 메시지 관리자
 */
class ChatMessageManager {
    // 메시지 캐시 (LRU)
    private final MessageCache messageCache;

    // 채팅방별 메시지 ID 목록
    private final Map<String, LinkedList<String>> roomMessages;

    // 전체 메시지 저장소 (DB 대신)
    private final Map<String, ChatMessage> messageStore;

    public ChatMessageManager(int cacheSize) {
        this.messageCache = new MessageCache(cacheSize);
        this.roomMessages = new HashMap<>();
        this.messageStore = new HashMap<>();
    }

    /**
     * 메시지 전송
     */
    public void sendMessage(String roomId, String senderId, String content, MessageType type) {
        String messageId = generateMessageId();

        ChatMessage message = new ChatMessage(messageId, roomId, senderId, content, type);

        // 1. 저장소에 저장
        messageStore.put(messageId, message);

        // 2. 캐시에 추가 (최신 메시지)
        messageCache.put(messageId, message);

        // 3. 채팅방별 메시지 목록에 추가
        roomMessages.computeIfAbsent(roomId, k -> new LinkedList<>())
                    .addFirst(messageId);  // 최신 메시지가 앞에

        System.out.println("✅ 메시지 전송: " + message);
    }

    /**
     * 메시지 ID 생성
     */
    private String generateMessageId() {
        return "MSG-" + System.currentTimeMillis() + "-" +
            (int)(Math.random() * 1000);
    }

    /**
     * 메시지 조회
     */
    public ChatMessage getMessage(String messageId) {
        // 1. 캐시 확인
        ChatMessage message = messageCache.getWithStats(messageId);

        if (message != null) {
            System.out.println("✅ 캐시 HIT: " + messageId);
            return message;
        }

        // 2. 캐시 MISS → 저장소에서 조회
        message = messageStore.get(messageId);

        if (message != null) {
            System.out.println("📀 캐시 MISS (저장소 조회): " + messageId);

            // 3. 캐시에 추가
            messageCache.put(messageId, message);
        }

        return message;
    }

    /**
     * 채팅방의 최근 메시지 조회
     */
    public List<ChatMessage> getRecentMessages(String roomId, int count) {
        LinkedList<String> messageIds = roomMessages.get(roomId);

        if (messageIds == null) {
            return Collections.emptyList();
        }

        List<ChatMessage> messages = new ArrayList<>();

        int limit = Math.min(count, messageIds.size());
        for (int i = 0; i < limit; i++) {
            String messageId = messageIds.get(i);
            ChatMessage message = getMessage(messageId);

            if (message != null) {
                messages.add(message);
            }
        }

        return messages;
    }

    /**
     * 채팅방 메시지 수
     */
    public int getRoomMessageCount(String roomId) {
        LinkedList<String> messageIds = roomMessages.get(roomId);
        return messageIds != null ? messageIds.size() : 0;
    }

    /**
     * 캐시 통계
     */
    public void printCacheStatistics() {
        messageCache.printStatistics();
    }

    /**
     * 전체 통계
     */
    public void printStatistics() {
        System.out.println("\n📊 전체 통계:");
        System.out.println("  - 총 메시지 수: " + messageStore.size() + "개");
        System.out.println("  - 채팅방 수: " + roomMessages.size() + "개");
        System.out.println("  - 캐시된 메시지: " + messageCache.size() + "개");
    }
}

/**
 * 라인 메시지 캐싱 시스템 데모
 */
public class LineMessageCacheSystem {
    public static void main(String[] args) {
        System.out.println("=== 라인 채팅 메시지 캐싱 시스템 ===\n");

        ChatMessageManager manager = new ChatMessageManager(5);  // 캐시 크기 5

        // 시나리오 1: 메시지 전송
        System.out.println("📍 시나리오 1: 메시지 전송 (캐시 자동 저장)");

        manager.sendMessage("ROOM1", "user001", "안녕하세요!", MessageType.TEXT);
        manager.sendMessage("ROOM1", "user002", "반갑습니다!", MessageType.TEXT);
        manager.sendMessage("ROOM1", "user001", "😊", MessageType.STICKER);
        System.out.println();

        // 시나리오 2: 메시지 조회 (캐시 HIT)
        System.out.println("📍 시나리오 2: 최근 메시지 조회 (캐시 HIT)");

        List<ChatMessage> recentMessages = manager.getRecentMessages("ROOM1", 3);

        System.out.println("\nROOM1 최근 메시지:");
        recentMessages.forEach(m -> System.out.println("  " + m));
        System.out.println();

        // 시나리오 3: 캐시 용량 초과 (LRU 제거)
        System.out.println("📍 시나리오 3: 캐시 용량 초과 (LRU 제거)");

        manager.sendMessage("ROOM2", "user003", "Message 1", MessageType.TEXT);
        manager.sendMessage("ROOM2", "user003", "Message 2", MessageType.TEXT);
        manager.sendMessage("ROOM2", "user003", "Message 3", MessageType.TEXT);
        manager.sendMessage("ROOM2", "user003", "Message 4", MessageType.TEXT);
        System.out.println("\n→ 캐시 크기 5 초과 시 가장 오래된 메시지 제거");
        System.out.println();

        // 시나리오 4: 캐시 MISS (저장소 조회)
        System.out.println("📍 시나리오 4: 캐시에서 제거된 메시지 조회 (MISS)");

        // 첫 번째 메시지는 캐시에서 제거되었음
        List<ChatMessage> room1Messages = manager.getRecentMessages("ROOM1", 3);
        System.out.println();

        // 시나리오 5: 접근 순서 변경
        System.out.println("📍 시나리오 5: 메시지 재접근 (LRU 순서 변경)");

        System.out.println("캐시 상태 확인:");
        manager.printCacheStatistics();
        System.out.println();

        // 시나리오 6: 대량 메시지 성능 테스트
        System.out.println("📍 시나리오 6: 대량 메시지 성능 테스트");

        ChatMessageManager perfManager = new ChatMessageManager(1000);

        // 10,000개 메시지 전송
        long start = System.nanoTime();

        for (int i = 0; i < 10000; i++) {
            String roomId = "ROOM" + (i % 100);
            perfManager.sendMessage(roomId, "user" + (i % 50), "Message " + i, MessageType.TEXT);
        }

        long end = System.nanoTime();

        System.out.println("10,000개 메시지 전송: " +
            String.format("%.2f", (end - start) / 1_000_000.0) + "ms");

        // 캐시 HIT 비율 테스트
        int hitCount = 0;
        int totalQueries = 1000;

        start = System.nanoTime();

        for (int i = 0; i < totalQueries; i++) {
            // 최근 메시지 위주로 조회 (캐시 HIT 가능성 높음)
            perfManager.getRecentMessages("ROOM" + (i % 10), 10);
        }

        end = System.nanoTime();

        System.out.println("\n1,000회 조회: " +
            String.format("%.2f", (end - start) / 1_000_000.0) + "ms");

        perfManager.printCacheStatistics();

        System.out.println("\n→ 최근 메시지 위주 조회 시 높은 캐시 HIT Rate");

        // 최종 통계
        manager.printStatistics();
    }
}
```

#### 🎯 핵심 포인트

**1. LinkedHashMap의 accessOrder**:
```java
// accessOrder = true: 접근 순서로 정렬
public MessageCache(int maxSize) {
    super(16, 0.75f, true);
    this.maxSize = maxSize;
}

// 동작:
// 1. put(A): [A]
// 2. put(B): [A, B]
// 3. get(A): [B, A] ← A가 맨 뒤로 이동 (최근 접근)
// 4. put(C): [B, A, C]
```

**2. removeEldestEntry 자동 호출**:
```java
@Override
protected boolean removeEldestEntry(Map.Entry<String, ChatMessage> eldest) {
    boolean shouldRemove = size() > maxSize;

    if (shouldRemove) {
        // eldest = 가장 오래된 Entry (맨 앞)
        evictionCount++;
    }

    return shouldRemove;  // true 반환 시 자동 제거
}
```

**3. 캐시 레이어 패턴**:
```
조회 요청
    ↓
1. 캐시 확인 (LinkedHashMap) - O(1)
    ├─ HIT → 반환 (빠름)
    └─ MISS → 2단계
              ↓
2. 저장소 조회 (DB/Map) - O(1) or DB 쿼리
    ├─ 찾음 → 캐시에 추가 → 반환
    └─ 없음 → null 반환
```

**4. 실제 효과**:
- **캐시 HIT Rate**: 80% 이상 (최근 메시지 위주 조회)
- **응답 시간**: 캐시 HIT 시 1ms, MISS 시 50ms
- **메모리 절약**: 전체 메시지의 1% 만 캐싱

---

## 🚫 주니어 개발자 실수 시나리오

### ❌ 실수 1: Key로 mutable 객체 사용

#### 문제 상황

```java
package junior.mistake1;

import java.util.*;

/**
 * ❌ 잘못된 코드: mutable 객체를 Key로 사용
 */
class MutableKey {
    private String id;
    private int value;

    public MutableKey(String id, int value) {
        this.id = id;
        this.value = value;
    }

    // Setter 제공 (mutable)
    public void setValue(int value) { this.value = value; }

    public String getId() { return id; }
    public int getValue() { return value; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        MutableKey that = (MutableKey) o;
        return value == that.value && id.equals(that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, value);
    }

    @Override
    public String toString() {
        return String.format("Key[id=%s, value=%d]", id, value);
    }
}

public class WrongMutableKeyUsage {
    public static void main(String[] args) {
        System.out.println("❌ mutable 객체를 Key로 사용 시 문제:\n");

        Map<MutableKey, String> map = new HashMap<>();

        MutableKey key1 = new MutableKey("K001", 100);
        map.put(key1, "Value 1");

        System.out.println("초기 상태:");
        System.out.println("map.get(key1) = " + map.get(key1));
        System.out.println("map.containsKey(key1) = " + map.containsKey(key1));
        System.out.println();

        // ❌ Key 객체의 필드 수정
        System.out.println("Key 객체의 value 변경 (100 → 200):");
        key1.setValue(200);  // hashCode 변경!

        System.out.println();
        System.out.println("문제 발생:");
        System.out.println("map.get(key1) = " + map.get(key1));
        System.out.println("map.containsKey(key1) = " + map.containsKey(key1));
        System.out.println("→ null! Key를 찾을 수 없음 (hashCode 변경됨)");
        System.out.println();

        // ❌ 원래 값으로도 찾을 수 없음
        MutableKey originalKey = new MutableKey("K001", 100);
        System.out.println("원래 값으로 조회:");
        System.out.println("map.get(originalKey) = " + map.get(originalKey));
        System.out.println("→ 여전히 찾을 수 없음 (다른 버킷에 저장됨)");
        System.out.println();

        // ❌ Map 내부 상태 확인
        System.out.println("Map 내부 상태:");
        System.out.println("map.size() = " + map.size());
        System.out.println("map.isEmpty() = " + map.isEmpty());

        System.out.println("\nMap 순회:");
        for (Map.Entry<MutableKey, String> entry : map.entrySet()) {
            System.out.println("  " + entry.getKey() + " → " + entry.getValue());
        }
        System.out.println("→ 데이터는 있지만 접근할 수 없는 '좀비 Entry'");
    }
}
```

**실행 결과**:
```
❌ mutable 객체를 Key로 사용 시 문제:

초기 상태:
map.get(key1) = Value 1
map.containsKey(key1) = true

Key 객체의 value 변경 (100 → 200):

문제 발생:
map.get(key1) = null
map.containsKey(key1) = false
→ null! Key를 찾을 수 없음 (hashCode 변경됨)

원래 값으로 조회:
map.get(originalKey) = null
→ 여전히 찾을 수 없음 (다른 버킷에 저장됨)

Map 내부 상태:
map.size() = 1
map.isEmpty() = false

Map 순회:
  Key[id=K001, value=200] → Value 1
→ 데이터는 있지만 접근할 수 없는 '좀비 Entry'
```

#### ✅ 올바른 해결책

```java
package junior.mistake1;

import java.util.*;

/**
 * ✅ 올바른 코드: immutable 객체를 Key로 사용
 */
class ImmutableKey {
    private final String id;     // final
    private final int value;     // final

    public ImmutableKey(String id, int value) {
        this.id = id;
        this.value = value;
    }

    // ✅ Setter 없음 (immutable)
    public String getId() { return id; }
    public int getValue() { return value; }

    /**
     * 값 변경이 필요하면 새 객체 생성
     */
    public ImmutableKey withValue(int newValue) {
        return new ImmutableKey(this.id, newValue);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ImmutableKey that = (ImmutableKey) o;
        return value == that.value && id.equals(that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, value);
    }

    @Override
    public String toString() {
        return String.format("Key[id=%s, value=%d]", id, value);
    }
}

public class CorrectImmutableKeyUsage {
    public static void main(String[] args) {
        System.out.println("✅ immutable 객체를 Key로 사용:\n");

        Map<ImmutableKey, String> map = new HashMap<>();

        ImmutableKey key1 = new ImmutableKey("K001", 100);
        map.put(key1, "Value 1");

        System.out.println("초기 상태:");
        System.out.println("map.get(key1) = " + map.get(key1));
        System.out.println("map.containsKey(key1) = " + map.containsKey(key1));
        System.out.println();

        // ✅ 값 변경이 필요하면 새 Key 생성
        System.out.println("값 변경 (새 Key 생성):");
        ImmutableKey key2 = key1.withValue(200);

        System.out.println("key1 = " + key1);  // 원본 유지
        System.out.println("key2 = " + key2);  // 새 객체
        System.out.println();

        // ✅ Map 업데이트
        System.out.println("Map 업데이트:");
        map.remove(key1);           // 기존 Key 제거
        map.put(key2, "Value 2");   // 새 Key 추가

        System.out.println("map.get(key1) = " + map.get(key1));  // null
        System.out.println("map.get(key2) = " + map.get(key2));  // Value 2
        System.out.println("→ 안전하게 업데이트 ✓");
        System.out.println();

        // ✅ 항상 올바르게 조회 가능
        ImmutableKey searchKey = new ImmutableKey("K001", 200);
        System.out.println("동일한 값으로 조회:");
        System.out.println("map.get(searchKey) = " + map.get(searchKey));
        System.out.println("→ equals/hashCode가 일관되게 동작 ✓");
    }
}
```

**실행 결과**:
```
✅ immutable 객체를 Key로 사용:

초기 상태:
map.get(key1) = Value 1
map.containsKey(key1) = true

값 변경 (새 Key 생성):
key1 = Key[id=K001, value=100]
key2 = Key[id=K001, value=200]

Map 업데이트:
map.get(key1) = null
map.get(key2) = Value 2
→ 안전하게 업데이트 ✓

동일한 값으로 조회:
map.get(searchKey) = Value 2
→ equals/hashCode가 일관되게 동작 ✓
```

#### 📚 핵심 교훈

**Map Key의 조건**:
```java
// ✅ 좋은 Key 클래스
class GoodKey {
    private final String id;     // 1. final 필드
    private final int value;

    // 2. Setter 없음

    // 3. equals/hashCode는 불변 필드만 사용
    @Override
    public int hashCode() {
        return Objects.hash(id, value);
    }
}

// ❌ 나쁜 Key 클래스
class BadKey {
    private String id;           // ❌ mutable

    public void setId(String id) { // ❌ setter
        this.id = id;
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);  // ❌ 값 변경 시 hashCode 변경
    }
}
```

**Immutable 클래스 설계 패턴**:
```
1. 모든 필드를 final로 선언
2. Setter 제공하지 않음
3. 값 변경이 필요하면 새 객체 생성 (with* 메서드)
4. 생성자에서만 초기화
```

**안전한 Key 타입**:
```java
// ✅ 기본 타입 래퍼 (Immutable)
Map<Integer, String> map = new HashMap<>();
Map<String, String> map = new HashMap<>();

// ✅ Immutable 클래스
Map<LocalDate, String> map = new HashMap<>();
Map<UUID, String> map = new HashMap<>();

// ❌ Mutable 클래스
Map<Date, String> map = new HashMap<>();  // Date는 mutable
Map<StringBuilder, String> map = new HashMap<>();  // mutable
```

---

### ❌ 실수 2: ConcurrentModificationException 발생

#### 문제 상황

```java
package junior.mistake2;

import java.util.*;

/**
 * ❌ 잘못된 코드: 순회 중 Map 수정
 */
public class WrongMapIteration {
    public static void main(String[] args) {
        System.out.println("❌ 순회 중 Map 수정 시 문제:\n");

        Map<String, Integer> scores = new HashMap<>();
        scores.put("김철수", 85);
        scores.put("이영희", 92);
        scores.put("박민수", 78);
        scores.put("정지훈", 88);
        scores.put("최유리", 95);

        System.out.println("초기 데이터:");
        System.out.println(scores);
        System.out.println();

        // ❌ 실수 1: 향상된 for문 중 제거
        System.out.println("실수 1: 향상된 for문 중 제거");
        try {
            for (Map.Entry<String, Integer> entry : scores.entrySet()) {
                if (entry.getValue() < 80) {
                    scores.remove(entry.getKey());  // ConcurrentModificationException!
                }
            }
        } catch (ConcurrentModificationException e) {
            System.out.println("💥 ConcurrentModificationException 발생!");
            System.out.println("→ 순회 중 Map 구조 변경 불가");
        }
        System.out.println();

        // ❌ 실수 2: forEach 람다 중 수정
        System.out.println("실수 2: forEach 중 추가");
        try {
            scores.forEach((name, score) -> {
                if (score >= 90) {
                    scores.put(name + "_VIP", score);  // ConcurrentModificationException!
                }
            });
        } catch (ConcurrentModificationException e) {
            System.out.println("💥 ConcurrentModificationException 발생!");
            System.out.println("→ forEach 중 Map 수정 불가");
        }
        System.out.println();

        // ❌ 실수 3: keySet() 순회 중 제거
        System.out.println("실수 3: keySet() 순회 중 제거");
        try {
            for (String name : scores.keySet()) {
                if (name.startsWith("박")) {
                    scores.remove(name);  // ConcurrentModificationException!
                }
            }
        } catch (ConcurrentModificationException e) {
            System.out.println("💥 ConcurrentModificationException 발생!");
            System.out.println("→ keySet() 순회 중 제거 불가");
        }
    }
}
```

**실행 결과**:
```
❌ 순회 중 Map 수정 시 문제:

초기 데이터:
{김철수=85, 이영희=92, 박민수=78, 정지훈=88, 최유리=95}

실수 1: 향상된 for문 중 제거
💥 ConcurrentModificationException 발생!
→ 순회 중 Map 구조 변경 불가

실수 2: forEach 중 추가
💥 ConcurrentModificationException 발생!
→ forEach 중 Map 수정 불가

실수 3: keySet() 순회 중 제거
💥 ConcurrentModificationException 발생!
→ keySet() 순회 중 제거 불가
```

#### ✅ 올바른 해결책

```java
package junior.mistake2;

import java.util.*;
import java.util.stream.Collectors;

/**
 * ✅ 올바른 코드: 안전한 Map 순회 및 수정
 */
public class CorrectMapIteration {
    public static void main(String[] args) {
        System.out.println("✅ 안전한 Map 순회 및 수정:\n");

        // 방법 1: Iterator 사용
        System.out.println("방법 1: Iterator.remove() 사용");
        Map<String, Integer> scores1 = new HashMap<>();
        scores1.put("김철수", 85);
        scores1.put("이영희", 92);
        scores1.put("박민수", 78);
        scores1.put("정지훈", 88);
        scores1.put("최유리", 95);

        Iterator<Map.Entry<String, Integer>> iterator = scores1.entrySet().iterator();
        while (iterator.hasNext()) {
            Map.Entry<String, Integer> entry = iterator.next();
            if (entry.getValue() < 80) {
                iterator.remove();  // ✅ Iterator로 안전하게 제거
                System.out.println("  제거: " + entry.getKey());
            }
        }

        System.out.println("결과: " + scores1);
        System.out.println("→ Iterator.remove()는 안전 ✓");
        System.out.println();

        // 방법 2: removeIf 사용
        System.out.println("방법 2: removeIf() 사용 (Java 8+)");
        Map<String, Integer> scores2 = new HashMap<>();
        scores2.put("김철수", 85);
        scores2.put("이영희", 92);
        scores2.put("박민수", 78);
        scores2.put("정지훈", 88);
        scores2.put("최유리", 95);

        scores2.entrySet().removeIf(entry -> {
            boolean shouldRemove = entry.getValue() < 80;
            if (shouldRemove) {
                System.out.println("  제거: " + entry.getKey());
            }
            return shouldRemove;
        });

        System.out.println("결과: " + scores2);
        System.out.println("→ removeIf()는 내부적으로 Iterator 사용 ✓");
        System.out.println();

        // 방법 3: 별도 리스트에 저장 후 제거
        System.out.println("방법 3: 제거할 Key를 별도 리스트에 저장");
        Map<String, Integer> scores3 = new HashMap<>();
        scores3.put("김철수", 85);
        scores3.put("이영희", 92);
        scores3.put("박민수", 78);
        scores3.put("정지훈", 88);
        scores3.put("최유리", 95);

        List<String> toRemove = new ArrayList<>();
        for (Map.Entry<String, Integer> entry : scores3.entrySet()) {
            if (entry.getValue() < 80) {
                toRemove.add(entry.getKey());
            }
        }

        toRemove.forEach(scores3::remove);

        System.out.println("제거할 Key: " + toRemove);
        System.out.println("결과: " + scores3);
        System.out.println("→ 순회와 수정을 분리 ✓");
        System.out.println();

        // 방법 4: Stream + filter (새 Map 생성)
        System.out.println("방법 4: Stream + filter (새 Map 생성)");
        Map<String, Integer> scores4 = new HashMap<>();
        scores4.put("김철수", 85);
        scores4.put("이영희", 92);
        scores4.put("박민수", 78);
        scores4.put("정지훈", 88);
        scores4.put("최유리", 95);

        Map<String, Integer> filtered = scores4.entrySet().stream()
            .filter(entry -> entry.getValue() >= 80)
            .collect(Collectors.toMap(
                Map.Entry::getKey,
                Map.Entry::getValue
            ));

        System.out.println("원본: " + scores4);
        System.out.println("필터링: " + filtered);
        System.out.println("→ 원본 유지하고 새 Map 생성 ✓");
        System.out.println();

        // 방법 5: 추가는 미리 수집
        System.out.println("방법 5: 추가할 Entry 미리 수집");
        Map<String, Integer> scores5 = new HashMap<>();
        scores5.put("김철수", 85);
        scores5.put("이영희", 92);
        scores5.put("박민수", 78);
        scores5.put("정지훈", 88);
        scores5.put("최유리", 95);

        Map<String, Integer> toAdd = new HashMap<>();
        for (Map.Entry<String, Integer> entry : scores5.entrySet()) {
            if (entry.getValue() >= 90) {
                toAdd.put(entry.getKey() + "_VIP", entry.getValue());
            }
        }

        scores5.putAll(toAdd);

        System.out.println("추가할 Entry: " + toAdd);
        System.out.println("결과: " + scores5);
        System.out.println("→ 순회 완료 후 일괄 추가 ✓");
    }
}
```

**실행 결과**:
```
✅ 안전한 Map 순회 및 수정:

방법 1: Iterator.remove() 사용
  제거: 박민수
결과: {김철수=85, 이영희=92, 정지훈=88, 최유리=95}
→ Iterator.remove()는 안전 ✓

방법 2: removeIf() 사용 (Java 8+)
  제거: 박민수
결과: {김철수=85, 이영희=92, 정지훈=88, 최유리=95}
→ removeIf()는 내부적으로 Iterator 사용 ✓

방법 3: 제거할 Key를 별도 리스트에 저장
제거할 Key: [박민수]
결과: {김철수=85, 이영희=92, 정지훈=88, 최유리=95}
→ 순회와 수정을 분리 ✓

방법 4: Stream + filter (새 Map 생성)
원본: {김철수=85, 이영희=92, 박민수=78, 정지훈=88, 최유리=95}
필터링: {김철수=85, 이영희=92, 정지훈=88, 최유리=95}
→ 원본 유지하고 새 Map 생성 ✓

방법 5: 추가할 Entry 미리 수집
추가할 Entry: {이영희_VIP=92, 최유리_VIP=95}
결과: {김철수=85, 이영희=92, 박민수=78, 정지훈=88, 최유리=95, 이영희_VIP=92, 최유리_VIP=95}
→ 순회 완료 후 일괄 추가 ✓
```

#### 📚 핵심 교훈

**ConcurrentModificationException 발생 조건**:
```java
// ❌ Fail-Fast Iterator
for (Map.Entry<K, V> entry : map.entrySet()) {
    map.remove(entry.getKey());  // 💥 Exception
    map.put(newKey, newValue);    // 💥 Exception
}

// ✅ Iterator.remove()는 허용
Iterator<Map.Entry<K, V>> it = map.entrySet().iterator();
while (it.hasNext()) {
    it.next();
    it.remove();  // ✓ OK
}
```

**안전한 Map 수정 방법 비교**:
| 방법 | 장점 | 단점 | 추천 |
|------|------|------|------|
| Iterator.remove() | 직접 제어 | 코드가 김 | ⭐⭐⭐ |
| removeIf() | 간결함 | Java 8+ 필요 | ⭐⭐⭐⭐⭐ |
| 별도 리스트 수집 | 이해하기 쉬움 | 메모리 추가 사용 | ⭐⭐⭐⭐ |
| Stream filter | 함수형, 원본 유지 | 새 Map 생성 | ⭐⭐⭐ |

---

### ❌ 실수 3: null Key/Value 처리 미숙

#### 문제 상황

```java
package junior.mistake3;

import java.util.*;

/**
 * ❌ 잘못된 코드: null 처리 미숙
 */
public class WrongNullHandling {
    public static void main(String[] args) {
        System.out.println("❌ null Key/Value 처리 미숙:\n");

        // 실수 1: null Key 구현체별 차이 모름
        System.out.println("실수 1: null Key 구현체별 동작 차이");

        Map<String, Integer> hashMap = new HashMap<>();
        hashMap.put(null, 100);  // ✓ HashMap은 null Key 허용
        System.out.println("HashMap: " + hashMap);

        TreeMap<String, Integer> treeMap = new TreeMap<>();
        try {
            treeMap.put(null, 100);  // 💥 NullPointerException
        } catch (NullPointerException e) {
            System.out.println("TreeMap: NullPointerException!");
            System.out.println("→ TreeMap은 null Key 불가");
        }
        System.out.println();

        // 실수 2: get() 결과로 존재 여부 판단
        System.out.println("실수 2: get() 결과로 존재 여부 판단");

        Map<String, Integer> map = new HashMap<>();
        map.put("A", 100);
        map.put("B", null);  // null Value 저장

        Integer valueA = map.get("A");
        Integer valueB = map.get("B");
        Integer valueC = map.get("C");

        System.out.println("map.get(\"A\") = " + valueA);
        System.out.println("map.get(\"B\") = " + valueB);  // null (Value가 null)
        System.out.println("map.get(\"C\") = " + valueC);  // null (Key 없음)

        System.out.println();
        System.out.println("❌ 잘못된 존재 여부 확인:");
        if (map.get("B") != null) {
            System.out.println("  B 존재");
        } else {
            System.out.println("  B 없음?");  // ❌ 잘못된 판단
        }

        if (map.get("C") != null) {
            System.out.println("  C 존재");
        } else {
            System.out.println("  C 없음");   // ✓ 올바름
        }

        System.out.println();
        System.out.println("✅ 올바른 존재 여부 확인:");
        System.out.println("  containsKey(\"B\"): " + map.containsKey("B"));  // true
        System.out.println("  containsKey(\"C\"): " + map.containsKey("C"));  // false
        System.out.println();

        // 실수 3: null 체크 없이 auto-unboxing
        System.out.println("실수 3: null 체크 없이 auto-unboxing");

        Map<String, Integer> scores = new HashMap<>();
        scores.put("김철수", 85);
        scores.put("이영희", null);  // 결석으로 null 저장

        try {
            int score1 = scores.get("김철수");  // ✓ 85 → int
            System.out.println("김철수: " + score1);

            int score2 = scores.get("이영희");  // 💥 NullPointerException
        } catch (NullPointerException e) {
            System.out.println("💥 NullPointerException!");
            System.out.println("→ null을 primitive int로 auto-unboxing 불가");
        }
        System.out.println();

        // 실수 4: getOrDefault의 오해
        System.out.println("실수 4: getOrDefault의 오해");

        Map<String, String> settings = new HashMap<>();
        settings.put("theme", "dark");
        settings.put("language", null);  // 설정은 있지만 값은 null

        String theme = settings.getOrDefault("theme", "light");
        String language = settings.getOrDefault("language", "en");
        String fontSize = settings.getOrDefault("fontSize", "14px");

        System.out.println("theme: " + theme);        // dark
        System.out.println("language: " + language);  // null (❌ "en"이 아님!)
        System.out.println("fontSize: " + fontSize);  // 14px

        System.out.println();
        System.out.println("→ getOrDefault는 Key가 없을 때만 기본값 반환");
        System.out.println("→ Key가 있고 Value가 null이면 null 반환");
    }
}
```

**실행 결과**:
```
❌ null Key/Value 처리 미숙:

실수 1: null Key 구현체별 동작 차이
HashMap: {null=100}
TreeMap: NullPointerException!
→ TreeMap은 null Key 불가

실수 2: get() 결과로 존재 여부 판단
map.get("A") = 100
map.get("B") = null
map.get("C") = null

❌ 잘못된 존재 여부 확인:
  B 없음?
  C 없음

✅ 올바른 존재 여부 확인:
  containsKey("B"): true
  containsKey("C"): false

실수 3: null 체크 없이 auto-unboxing
김철수: 85
💥 NullPointerException!
→ null을 primitive int로 auto-unboxing 불가

실수 4: getOrDefault의 오해
theme: dark
language: null
fontSize: 14px

→ getOrDefault는 Key가 없을 때만 기본값 반환
→ Key가 있고 Value가 null이면 null 반환
```

#### ✅ 올바른 해결책

```java
package junior.mistake3;

import java.util.*;

/**
 * ✅ 올바른 코드: 안전한 null 처리
 */
public class CorrectNullHandling {
    public static void main(String[] args) {
        System.out.println("✅ 안전한 null 처리:\n");

        // 방법 1: containsKey로 존재 여부 확인
        System.out.println("방법 1: containsKey() 사용");

        Map<String, Integer> map = new HashMap<>();
        map.put("A", 100);
        map.put("B", null);

        if (map.containsKey("B")) {
            Integer value = map.get("B");
            System.out.println("B 존재, 값: " + value);
        }

        if (!map.containsKey("C")) {
            System.out.println("C 없음");
        }
        System.out.println();

        // 방법 2: getOrDefault + null 체크
        System.out.println("방법 2: getOrDefault + null 병합");

        Map<String, String> settings = new HashMap<>();
        settings.put("theme", "dark");
        settings.put("language", null);

        // ✅ null도 기본값으로 치환
        String language = Optional.ofNullable(settings.get("language"))
            .orElse("en");

        System.out.println("language: " + language);  // en
        System.out.println();

        // 방법 3: compute 계열 메서드 활용
        System.out.println("방법 3: computeIfAbsent로 null 방지");

        Map<String, List<String>> groups = new HashMap<>();

        // ❌ null 체크 필요
        // List<String> group1 = groups.get("admin");
        // if (group1 == null) {
        //     group1 = new ArrayList<>();
        //     groups.put("admin", group1);
        // }

        // ✅ computeIfAbsent: null이면 자동 생성
        groups.computeIfAbsent("admin", k -> new ArrayList<>()).add("user1");
        groups.computeIfAbsent("admin", k -> new ArrayList<>()).add("user2");

        System.out.println("groups: " + groups);
        System.out.println("→ computeIfAbsent로 간결하게 처리 ✓");
        System.out.println();

        // 방법 4: primitive 타입은 null 체크
        System.out.println("방법 4: primitive 타입 auto-unboxing 안전 처리");

        Map<String, Integer> scores = new HashMap<>();
        scores.put("김철수", 85);
        scores.put("이영희", null);

        // ✅ Integer로 받아서 null 체크
        Integer score = scores.get("이영희");
        int actualScore = (score != null) ? score : 0;

        System.out.println("이영희 점수: " + actualScore);  // 0

        // ✅ getOrDefault 활용
        int score2 = scores.getOrDefault("이영희", 0);
        System.out.println("이영희 점수 (getOrDefault): " + score2);  // 0 (❌ 실제로는 null 반환)

        // ✅ 가장 안전한 방법
        int score3 = Optional.ofNullable(scores.get("이영희")).orElse(0);
        System.out.println("이영희 점수 (Optional): " + score3);  // 0 ✓
        System.out.println();

        // 방법 5: null 허용 여부 명확히
        System.out.println("방법 5: null 저장 금지 정책");

        Map<String, String> strictMap = new HashMap<>();

        // ✅ null 저장 금지
        String value = "someValue";
        if (value != null) {
            strictMap.put("key", value);
        } else {
            System.out.println("null 저장 불가 - 무시");
        }

        // ✅ 또는 기본값 저장
        strictMap.put("key2", (value != null) ? value : "default");

        System.out.println("strictMap: " + strictMap);
        System.out.println("→ 애초에 null을 저장하지 않는 정책 ✓");
    }
}
```

#### 📚 핵심 교훈

**null Key/Value 구현체별 지원**:
| 구현체 | null Key | null Value |
|--------|----------|------------|
| HashMap | ✅ 1개 | ✅ 다수 |
| LinkedHashMap | ✅ 1개 | ✅ 다수 |
| TreeMap | ❌ 불가 | ✅ 다수 |
| ConcurrentHashMap | ❌ 불가 | ❌ 불가 |

**안전한 null 처리 패턴**:
```java
// ❌ 잘못된 방법
if (map.get(key) != null) {  // Value가 null일 수 있음
    ...
}

// ✅ 올바른 방법
if (map.containsKey(key)) {  // Key 존재 여부 확인
    V value = map.get(key);
    ...
}

// ✅ Optional 활용
Optional.ofNullable(map.get(key))
    .ifPresent(value -> ...);

// ✅ getOrDefault (Key가 없을 때만 기본값)
V value = map.getOrDefault(key, defaultValue);

// ✅ Optional + orElse (null도 기본값으로)
V value = Optional.ofNullable(map.get(key))
    .orElse(defaultValue);
```

---

### ❌ 실수 4: HashMap 동시성 문제 무시

#### 문제 상황

```java
package junior.mistake4;

import java.util.*;
import java.util.concurrent.*;

/**
 * ❌ 잘못된 코드: 멀티스레드에서 HashMap 사용
 */
public class WrongConcurrency {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("❌ HashMap 동시성 문제:\n");

        // 문제 1: 동시 수정으로 인한 데이터 손실
        System.out.println("문제 1: 동시 수정으로 데이터 손실");

        Map<Integer, String> map = new HashMap<>();

        ExecutorService executor = Executors.newFixedThreadPool(10);
        CountDownLatch latch = new CountDownLatch(100);

        // 100개 스레드가 동시에 추가
        for (int i = 0; i < 100; i++) {
            final int num = i;
            executor.submit(() -> {
                map.put(num, "Value" + num);
                latch.countDown();
            });
        }

        latch.await();
        executor.shutdown();

        System.out.println("예상 크기: 100");
        System.out.println("실제 크기: " + map.size());
        System.out.println("→ 데이터 손실 발생 가능 (Race Condition)");
        System.out.println();

        // 문제 2: 무한 루프 (Infinite Loop)
        System.out.println("문제 2: HashMap 내부 구조 손상 가능");
        System.out.println("→ 동시 수정 시 해시 테이블 구조가 손상되어");
        System.out.println("→ get() 호출 시 무한 루프에 빠질 수 있음");
        System.out.println("→ (재현은 어렵지만 실제 프로덕션에서 발생 가능)");
        System.out.println();

        // 문제 3: compute 메서드도 Thread-Safe 아님
        System.out.println("문제 3: compute 메서드도 Thread-Safe 아님");

        Map<String, Integer> counter = new HashMap<>();
        counter.put("count", 0);

        ExecutorService executor2 = Executors.newFixedThreadPool(10);
        CountDownLatch latch2 = new CountDownLatch(1000);

        for (int i = 0; i < 1000; i++) {
            executor2.submit(() -> {
                counter.compute("count", (k, v) -> v + 1);
                latch2.countDown();
            });
        }

        latch2.await();
        executor2.shutdown();

        System.out.println("예상 카운트: 1000");
        System.out.println("실제 카운트: " + counter.get("count"));
        System.out.println("→ compute도 원자적이지 않음");
    }
}
```

**실행 결과** (실행마다 다를 수 있음):
```
❌ HashMap 동시성 문제:

문제 1: 동시 수정으로 데이터 손실
예상 크기: 100
실제 크기: 97
→ 데이터 손실 발생 가능 (Race Condition)

문제 2: HashMap 내부 구조 손상 가능
→ 동시 수정 시 해시 테이블 구조가 손상되어
→ get() 호출 시 무한 루프에 빠질 수 있음
→ (재현은 어렵지만 실제 프로덕션에서 발생 가능)

문제 3: compute 메서드도 Thread-Safe 아님
예상 카운트: 1000
실제 카운트: 987
→ compute도 원자적이지 않음
```

#### ✅ 올바른 해결책

```java
package junior.mistake4;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * ✅ 올바른 코드: Thread-Safe Map 사용
 */
public class CorrectConcurrency {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("✅ Thread-Safe Map 사용:\n");

        // 방법 1: ConcurrentHashMap (권장)
        System.out.println("방법 1: ConcurrentHashMap 사용");

        Map<Integer, String> concurrentMap = new ConcurrentHashMap<>();

        ExecutorService executor1 = Executors.newFixedThreadPool(10);
        CountDownLatch latch1 = new CountDownLatch(100);

        for (int i = 0; i < 100; i++) {
            final int num = i;
            executor1.submit(() -> {
                concurrentMap.put(num, "Value" + num);
                latch1.countDown();
            });
        }

        latch1.await();
        executor1.shutdown();

        System.out.println("예상 크기: 100");
        System.out.println("실제 크기: " + concurrentMap.size());
        System.out.println("→ 정확히 100개 저장 ✓");
        System.out.println();

        // 방법 2: Collections.synchronizedMap
        System.out.println("방법 2: Collections.synchronizedMap");

        Map<Integer, String> syncMap = Collections.synchronizedMap(new HashMap<>());

        ExecutorService executor2 = Executors.newFixedThreadPool(10);
        CountDownLatch latch2 = new CountDownLatch(100);

        for (int i = 0; i < 100; i++) {
            final int num = i;
            executor2.submit(() -> {
                syncMap.put(num, "Value" + num);
                latch2.countDown();
            });
        }

        latch2.await();
        executor2.shutdown();

        System.out.println("크기: " + syncMap.size());
        System.out.println("→ synchronized로 모든 메서드 보호 ✓");
        System.out.println();

        // 방법 3: ConcurrentHashMap의 원자적 연산
        System.out.println("방법 3: ConcurrentHashMap 원자적 연산");

        Map<String, AtomicInteger> atomicCounter = new ConcurrentHashMap<>();
        atomicCounter.put("count", new AtomicInteger(0));

        ExecutorService executor3 = Executors.newFixedThreadPool(10);
        CountDownLatch latch3 = new CountDownLatch(1000);

        for (int i = 0; i < 1000; i++) {
            executor3.submit(() -> {
                atomicCounter.get("count").incrementAndGet();
                latch3.countDown();
            });
        }

        latch3.await();
        executor3.shutdown();

        System.out.println("예상 카운트: 1000");
        System.out.println("실제 카운트: " + atomicCounter.get("count").get());
        System.out.println("→ AtomicInteger로 정확한 카운트 ✓");
        System.out.println();

        // 방법 4: compute 대신 merge 사용
        System.out.println("방법 4: ConcurrentHashMap.merge() 사용");

        Map<String, Integer> mergeCounter = new ConcurrentHashMap<>();

        ExecutorService executor4 = Executors.newFixedThreadPool(10);
        CountDownLatch latch4 = new CountDownLatch(1000);

        for (int i = 0; i < 1000; i++) {
            executor4.submit(() -> {
                mergeCounter.merge("count", 1, Integer::sum);
                latch4.countDown();
            });
        }

        latch4.await();
        executor4.shutdown();

        System.out.println("예상 카운트: 1000");
        System.out.println("실제 카운트: " + mergeCounter.get("count"));
        System.out.println("→ ConcurrentHashMap.merge()는 원자적 ✓");
        System.out.println();

        // 성능 비교
        System.out.println("성능 비교:");
        System.out.println("  - ConcurrentHashMap: 높은 동시성 (segment 단위 lock)");
        System.out.println("  - synchronizedMap: 낮은 동시성 (전체 lock)");
        System.out.println("  → ConcurrentHashMap 권장 ⭐");
    }
}
```

**실행 결과**:
```
✅ Thread-Safe Map 사용:

방법 1: ConcurrentHashMap 사용
예상 크기: 100
실제 크기: 100
→ 정확히 100개 저장 ✓

방법 2: Collections.synchronizedMap
크기: 100
→ synchronized로 모든 메서드 보호 ✓

방법 3: ConcurrentHashMap 원자적 연산
예상 카운트: 1000
실제 카운트: 1000
→ AtomicInteger로 정확한 카운트 ✓

방법 4: ConcurrentHashMap.merge() 사용
예상 카운트: 1000
실제 카운트: 1000
→ ConcurrentHashMap.merge()는 원자적 ✓

성능 비교:
  - ConcurrentHashMap: 높은 동시성 (segment 단위 lock)
  - synchronizedMap: 낮은 동시성 (전체 lock)
  → ConcurrentHashMap 권장 ⭐
```

#### 📚 핵심 교훈

**Thread-Safe Map 비교**:
| | HashMap | synchronizedMap | ConcurrentHashMap |
|---|---------|----------------|-------------------|
| **동시성** | ❌ 없음 | ✅ 있음 | ✅ 있음 (높음) |
| **성능** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Lock 방식** | - | 전체 lock | Segment lock |
| **null** | ✅ 허용 | ✅ 허용 | ❌ 불허 |
| **사용 시기** | 단일 스레드 | 간단한 동기화 | 멀티스레드 권장 |

**ConcurrentHashMap의 원자적 연산**:
```java
// ✅ 원자적 연산
map.putIfAbsent(key, value);     // Key 없으면 추가
map.remove(key, value);          // Key-Value 모두 일치 시 제거
map.replace(key, oldValue, newValue);  // 값 변경
map.compute(key, (k, v) -> newValue);  // 계산 후 업데이트
map.merge(key, value, (old, new) -> old + new);  // 병합

// ❌ 비원자적 (잘못된 패턴)
if (!map.containsKey(key)) {
    map.put(key, value);  // Race Condition 가능
}
```

---

## 🎓 Part 2 종합 정리

### 📊 3개 기업 사례 요약

| 기업 | 시스템 | 사용 기술 | 핵심 포인트 |
|------|--------|-----------|-------------|
| **카카오** | 세션 관리 | ConcurrentHashMap | 이중 매핑, 세션 만료, 동시성 |
| **쿠팡** | 재고 관리 | ConcurrentHashMap + AtomicInteger | CAS 연산, 원자적 재고 차감 |
| **라인** | 메시지 캐싱 | LinkedHashMap (LRU) | removeEldestEntry, 캐시 HIT Rate |

### 🚫 4개 주니어 실수 요약

| 실수 | 문제 | 해결책 | 핵심 |
|------|------|--------|------|
| **1. mutable Key** | hashCode 변경 시 찾을 수 없음 | Immutable 객체 사용 | final 필드, no setter |
| **2. 순회 중 수정** | ConcurrentModificationException | Iterator.remove() / removeIf() | Fail-Fast Iterator |
| **3. null 처리** | get() 결과로 존재 여부 판단 | containsKey() 사용 | getOrDefault 오해 주의 |
| **4. 동시성 무시** | Race Condition, 데이터 손실 | ConcurrentHashMap 사용 | Segment lock, 원자적 연산 |

### 💡 Map 사용 Best Practices

```java
// 1. Immutable Key 사용
class GoodKey {
    private final String id;  // final
    // no setter
}

// 2. 안전한 순회 중 수정
map.entrySet().removeIf(entry -> condition);

// 3. null 안전 처리
if (map.containsKey(key)) {
    V value = map.get(key);
}

// 4. 멀티스레드는 ConcurrentHashMap
Map<K, V> map = new ConcurrentHashMap<>();
map.merge(key, 1, Integer::sum);  // 원자적
```

**다음 Part 3에서는**: 실전 프로젝트 (상품 카탈로그 시스템) + 7 FAQ + 12 면접 질문을 다룹니다.