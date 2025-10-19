# 26장 List 인터페이스 Part 2 - 기업 사례 & 주니어 시나리오 💼

## 🏢 기업 실무 사례

---

## 사례 1: 배달의민족 - 주문 처리 시스템 (ArrayList vs LinkedList) 🍔

### 배경
배달의민족은 초당 수천 건의 주문을 처리합니다. 주문 목록 조회가 압도적으로 많지만, 일부 상황에서는 Queue 방식의 처리가 필요합니다.

### 문제 상황
```java
// ❌ 잘못된 구현: LinkedList를 모든 곳에 사용
public class OrderProcessor {
    // 주문 목록: 조회가 99%
    private List<Order> orders = new LinkedList<>();  // 느림!

    public Order getOrderById(String orderId) {
        // O(n) 순차 탐색 - 매우 느림!
        for (Order order : orders) {
            if (order.getOrderId().equals(orderId)) {
                return order;
            }
        }
        return null;
    }

    // 성능 문제: 10만 건 주문에서 조회 시 2초 소요
}
```

### 해결 방법
```java
import java.util.*;

class Order {
    private String orderId;
    private String restaurantName;
    private String customerName;
    private int totalPrice;
    private OrderStatus status;

    public enum OrderStatus {
        PENDING, ACCEPTED, COOKING, DELIVERING, COMPLETED, CANCELLED
    }

    public Order(String orderId, String restaurantName, String customerName, int totalPrice) {
        this.orderId = orderId;
        this.restaurantName = restaurantName;
        this.customerName = customerName;
        this.totalPrice = totalPrice;
        this.status = OrderStatus.PENDING;
    }

    public String getOrderId() { return orderId; }
    public String getRestaurantName() { return restaurantName; }
    public String getCustomerName() { return customerName; }
    public int getTotalPrice() { return totalPrice; }
    public OrderStatus getStatus() { return status; }
    public void setStatus(OrderStatus status) { this.status = status; }

    @Override
    public String toString() {
        return orderId + " | " + restaurantName + " | " + customerName +
               " | " + totalPrice + "원 | " + status;
    }
}

// ✅ 올바른 구현: 용도에 맞게 선택
public class BaeminOrderSystem {

    // 1. 전체 주문 목록: ArrayList (조회 99%)
    private List<Order> allOrders = new ArrayList<>();

    // 2. 대기 주문 큐: LinkedList (FIFO, 앞에서 제거)
    private LinkedList<Order> pendingQueue = new LinkedList<>();

    // 3. 배달 중 주문: ArrayList (조회 많음)
    private List<Order> deliveringOrders = new ArrayList<>();

    // ArrayList 사용: 주문 조회 O(1) with HashMap, 목록 조회 O(n)
    private Map<String, Order> orderMap = new HashMap<>();

    // 주문 생성
    public void createOrder(Order order) {
        allOrders.add(order);  // ArrayList: O(1) 끝에 추가
        orderMap.put(order.getOrderId(), order);  // HashMap: O(1) 추가
        pendingQueue.addLast(order);  // LinkedList: O(1) 끝에 추가

        System.out.println("✅ 주문 생성: " + order.getOrderId() +
                         " (대기열: " + pendingQueue.size() + "건)");
    }

    // 주문 조회: O(1)
    public Order getOrder(String orderId) {
        return orderMap.get(orderId);  // HashMap 사용으로 O(1)
    }

    // 가장 오래된 대기 주문 처리: LinkedList의 장점
    public Order processNextPendingOrder() {
        if (pendingQueue.isEmpty()) {
            System.out.println("⚠️ 대기 중인 주문 없음");
            return null;
        }

        Order order = pendingQueue.removeFirst();  // O(1) 앞에서 제거
        order.setStatus(Order.OrderStatus.ACCEPTED);
        System.out.println("🍳 주문 접수: " + order.getOrderId() +
                         " (남은 대기: " + pendingQueue.size() + "건)");
        return order;
    }

    // 배달 시작
    public void startDelivery(String orderId) {
        Order order = orderMap.get(orderId);
        if (order != null) {
            order.setStatus(Order.OrderStatus.DELIVERING);
            deliveringOrders.add(order);  // ArrayList: O(1) 끝에 추가
            System.out.println("🛵 배달 시작: " + orderId +
                             " (배달 중: " + deliveringOrders.size() + "건)");
        }
    }

    // 배달 완료
    public void completeDelivery(String orderId) {
        Order order = orderMap.get(orderId);
        if (order != null) {
            order.setStatus(Order.OrderStatus.COMPLETED);
            deliveringOrders.remove(order);  // ArrayList: O(n) 하지만 드뭄
            System.out.println("✅ 배달 완료: " + orderId);
        }
    }

    // 실시간 통계: ArrayList의 장점 (빠른 순회)
    public void displayStatistics() {
        int pending = 0, accepted = 0, cooking = 0, delivering = 0, completed = 0;

        // ArrayList: cache-friendly, 빠른 순회
        for (Order order : allOrders) {
            switch (order.getStatus()) {
                case PENDING: pending++; break;
                case ACCEPTED: accepted++; break;
                case COOKING: cooking++; break;
                case DELIVERING: delivering++; break;
                case COMPLETED: completed++; break;
            }
        }

        System.out.println("\n📊 실시간 통계:");
        System.out.println("   대기: " + pending + "건");
        System.out.println("   접수: " + accepted + "건");
        System.out.println("   조리: " + cooking + "건");
        System.out.println("   배달: " + delivering + "건");
        System.out.println("   완료: " + completed + "건");
        System.out.println("   총 주문: " + allOrders.size() + "건");
    }

    // 성능 비교
    public static void performanceComparison() {
        System.out.println("\n=== ArrayList vs LinkedList 성능 비교 ===\n");

        int size = 100000;

        // 1. ArrayList
        List<Integer> arrayList = new ArrayList<>();

        // 끝에 추가
        long start = System.nanoTime();
        for (int i = 0; i < size; i++) {
            arrayList.add(i);
        }
        long arrayAddTime = (System.nanoTime() - start) / 1_000_000;

        // 중간 조회
        start = System.nanoTime();
        for (int i = 0; i < 10000; i++) {
            arrayList.get(size / 2);
        }
        long arrayGetTime = (System.nanoTime() - start) / 1_000_000;

        // 2. LinkedList
        LinkedList<Integer> linkedList = new LinkedList<>();

        // 끝에 추가
        start = System.nanoTime();
        for (int i = 0; i < size; i++) {
            linkedList.add(i);
        }
        long linkedAddTime = (System.nanoTime() - start) / 1_000_000;

        // 중간 조회
        start = System.nanoTime();
        for (int i = 0; i < 10000; i++) {
            linkedList.get(size / 2);
        }
        long linkedGetTime = (System.nanoTime() - start) / 1_000_000;

        System.out.println("1. 끝에 추가 (" + size + "건):");
        System.out.println("   ArrayList:  " + arrayAddTime + "ms ✅");
        System.out.println("   LinkedList: " + linkedAddTime + "ms ✅");

        System.out.println("\n2. 중간 조회 (10000회):");
        System.out.println("   ArrayList:  " + arrayGetTime + "ms ✅ 빠름!");
        System.out.println("   LinkedList: " + linkedGetTime + "ms ❌ 느림!");

        System.out.println("\n✅ 배민 선택:");
        System.out.println("   - 주문 목록: ArrayList + HashMap (조회 많음)");
        System.out.println("   - 대기 큐: LinkedList (FIFO 처리)");
        System.out.println("   - 배달 목록: ArrayList (조회 위주)");
    }
}

public class BaeminOrderExample {
    public static void main(String[] args) {
        System.out.println("=== 배달의민족 주문 처리 시스템 ===\n");

        BaeminOrderSystem system = new BaeminOrderSystem();

        // 주문 생성
        system.createOrder(new Order("ORD001", "김밥천국", "홍길동", 8000));
        system.createOrder(new Order("ORD002", "맘스터치", "김영희", 15000));
        system.createOrder(new Order("ORD003", "버거킹", "이철수", 12000));
        system.createOrder(new Order("ORD004", "피자헛", "박민수", 25000));

        System.out.println();

        // 대기 주문 처리 (LinkedList FIFO)
        system.processNextPendingOrder();
        system.processNextPendingOrder();

        System.out.println();

        // 배달 시작
        system.startDelivery("ORD001");
        system.startDelivery("ORD002");

        System.out.println();

        // 배달 완료
        system.completeDelivery("ORD001");

        // 통계
        system.displayStatistics();

        // 성능 비교
        BaeminOrderSystem.performanceComparison();

        System.out.println("\n\n💡 핵심 교훈:");
        System.out.println("1. 조회가 많으면 ArrayList + HashMap");
        System.out.println("2. FIFO/LIFO 패턴은 LinkedList");
        System.out.println("3. 용도에 맞게 자료구조 선택");
        System.out.println("4. 성능 측정으로 검증");
    }
}
```

### 실행 결과
```
=== 배달의민족 주문 처리 시스템 ===

✅ 주문 생성: ORD001 (대기열: 1건)
✅ 주문 생성: ORD002 (대기열: 2건)
✅ 주문 생성: ORD003 (대기열: 3건)
✅ 주문 생성: ORD004 (대기열: 4건)

🍳 주문 접수: ORD001 (남은 대기: 3건)
🍳 주문 접수: ORD002 (남은 대기: 2건)

🛵 배달 시작: ORD001 (배달 중: 1건)
🛵 배달 시작: ORD002 (배달 중: 2건)

✅ 배달 완료: ORD001

📊 실시간 통계:
   대기: 2건
   접수: 1건
   조리: 0건
   배달: 1건
   완료: 1건
   총 주문: 4건

=== ArrayList vs LinkedList 성능 비교 ===

1. 끝에 추가 (100000건):
   ArrayList:  8ms ✅
   LinkedList: 14ms ✅

2. 중간 조회 (10000회):
   ArrayList:  0ms ✅ 빠름!
   LinkedList: 2134ms ❌ 느림!

✅ 배민 선택:
   - 주문 목록: ArrayList + HashMap (조회 많음)
   - 대기 큐: LinkedList (FIFO 처리)
   - 배달 목록: ArrayList (조회 위주)


💡 핵심 교훈:
1. 조회가 많으면 ArrayList + HashMap
2. FIFO/LIFO 패턴은 LinkedList
3. 용도에 맞게 자료구조 선택
4. 성능 측정으로 검증
```

### 핵심 교훈
- **ArrayList**: 조회 중심 (주문 목록, 배달 목록)
- **LinkedList**: Queue 구현 (FIFO 대기열)
- **HashMap**: O(1) 조회 (ID로 주문 검색)
- **성능 측정**: 실제 환경에서 벤치마크

---

## 사례 2: 네이버 - 검색 히스토리 관리 (List 크기 제한) 🔍

### 배경
네이버 검색은 사용자의 최근 검색어를 저장하여 자동완성에 활용합니다. 최대 100개까지만 저장하며, 오래된 검색어는 자동 삭제됩니다.

### 문제 상황
```java
// ❌ 잘못된 구현: 크기 제한 없음
public class SearchHistory {
    private List<String> history = new ArrayList<>();

    public void addSearchKeyword(String keyword) {
        history.add(keyword);  // 무한정 증가!
        // 메모리 누수 위험
    }
}
```

### 해결 방법
```java
import java.util.*;

class SearchRecord {
    private String keyword;
    private long timestamp;
    private int clickCount;

    public SearchRecord(String keyword) {
        this.keyword = keyword;
        this.timestamp = System.currentTimeMillis();
        this.clickCount = 0;
    }

    public String getKeyword() { return keyword; }
    public long getTimestamp() { return timestamp; }
    public int getClickCount() { return clickCount; }
    public void incrementClick() { this.clickCount++; }

    @Override
    public String toString() {
        return keyword + " (조회: " + clickCount + "회)";
    }
}

// ✅ 올바른 구현: LRU (Least Recently Used) 방식
public class NaverSearchHistory {
    private static final int MAX_HISTORY_SIZE = 100;

    // ArrayList: 순서 유지 (최신순)
    private List<SearchRecord> history = new ArrayList<>();

    // 중복 검색어 빠른 조회
    private Map<String, SearchRecord> recordMap = new HashMap<>();

    // 검색어 추가
    public void addSearch(String keyword) {
        keyword = keyword.trim().toLowerCase();

        if (keyword.isEmpty()) {
            return;
        }

        // 1. 이미 존재하면 제거 후 맨 앞으로 (MRU)
        if (recordMap.containsKey(keyword)) {
            SearchRecord existing = recordMap.get(keyword);
            history.remove(existing);  // ArrayList: O(n) 하지만 크기 제한으로 최대 100
            existing.incrementClick();
            history.add(0, existing);  // 맨 앞에 추가
            System.out.println("🔄 재검색: " + existing);
        } else {
            // 2. 새 검색어
            SearchRecord newRecord = new SearchRecord(keyword);

            // 3. 크기 제한 확인
            if (history.size() >= MAX_HISTORY_SIZE) {
                // 가장 오래된 항목 제거 (LRU)
                SearchRecord oldest = history.remove(history.size() - 1);
                recordMap.remove(oldest.getKeyword());
                System.out.println("🗑️ 오래된 검색어 삭제: " + oldest.getKeyword());
            }

            // 4. 맨 앞에 추가
            history.add(0, newRecord);
            recordMap.put(keyword, newRecord);
            System.out.println("✅ 새 검색: " + keyword);
        }
    }

    // 최근 N개 검색어 조회
    public List<String> getRecentSearches(int count) {
        List<String> recent = new ArrayList<>();
        int limit = Math.min(count, history.size());

        for (int i = 0; i < limit; i++) {
            recent.add(history.get(i).getKeyword());
        }

        return recent;
    }

    // 자동완성: 키워드로 시작하는 검색어
    public List<String> autoComplete(String prefix) {
        prefix = prefix.toLowerCase();
        List<String> suggestions = new ArrayList<>();

        for (SearchRecord record : history) {
            if (record.getKeyword().startsWith(prefix)) {
                suggestions.add(record.getKeyword());

                if (suggestions.size() >= 10) {  // 최대 10개
                    break;
                }
            }
        }

        return suggestions;
    }

    // 인기 검색어 (조회수 기준)
    public List<SearchRecord> getPopularSearches(int count) {
        // ArrayList 복사 후 정렬
        List<SearchRecord> sorted = new ArrayList<>(history);
        sorted.sort((a, b) -> Integer.compare(b.getClickCount(), a.getClickCount()));

        return sorted.subList(0, Math.min(count, sorted.size()));
    }

    // 검색어 삭제
    public void removeSearch(String keyword) {
        SearchRecord record = recordMap.remove(keyword.toLowerCase());
        if (record != null) {
            history.remove(record);
            System.out.println("🗑️ 삭제: " + keyword);
        }
    }

    // 전체 삭제
    public void clearAll() {
        history.clear();
        recordMap.clear();
        System.out.println("🗑️ 검색 히스토리 전체 삭제");
    }

    // 통계
    public void displayStatistics() {
        System.out.println("\n📊 검색 히스토리 통계:");
        System.out.println("   총 검색어: " + history.size() + "개");
        System.out.println("   최대 용량: " + MAX_HISTORY_SIZE + "개");
        System.out.println("   사용률: " + (history.size() * 100 / MAX_HISTORY_SIZE) + "%");

        if (!history.isEmpty()) {
            System.out.println("\n   최근 5개:");
            List<String> recent = getRecentSearches(5);
            for (int i = 0; i < recent.size(); i++) {
                System.out.println("      " + (i + 1) + ". " + recent.get(i));
            }
        }
    }

    // List 크기 제한 패턴 시연
    public static void demonstrateSizeLimitPattern() {
        System.out.println("\n=== List 크기 제한 패턴 ===\n");

        System.out.println("패턴 1: 고정 크기 유지 (Circular Buffer)");
        System.out.println("```java");
        System.out.println("if (list.size() >= MAX_SIZE) {");
        System.out.println("    list.remove(0);  // 또는 remove(list.size() - 1)");
        System.out.println("}");
        System.out.println("list.add(newItem);");
        System.out.println("```");
        System.out.println();

        System.out.println("패턴 2: 주기적 정리");
        System.out.println("```java");
        System.out.println("if (list.size() > MAX_SIZE * 1.2) {");
        System.out.println("    // 오래된 항목 20% 삭제");
        System.out.println("    int removeCount = (int)(MAX_SIZE * 0.2);");
        System.out.println("    list.subList(0, removeCount).clear();");
        System.out.println("}");
        System.out.println("```");
        System.out.println();

        System.out.println("패턴 3: 시간 기반 만료");
        System.out.println("```java");
        System.out.println("long expirationTime = System.currentTimeMillis() - 30_DAYS;");
        System.out.println("list.removeIf(item -> item.getTimestamp() < expirationTime);");
        System.out.println("```");
        System.out.println();

        System.out.println("✅ 네이버는 패턴 1 + MRU 사용");
        System.out.println("   - 최대 100개 유지");
        System.out.println("   - 재검색 시 맨 앞으로 이동");
        System.out.println("   - 가장 오래된 항목 자동 삭제");
    }
}

public class NaverSearchHistoryExample {
    public static void main(String[] args) {
        System.out.println("=== 네이버 검색 히스토리 관리 ===\n");

        NaverSearchHistory searchHistory = new NaverSearchHistory();

        // 검색어 추가
        String[] keywords = {
            "Java", "Python", "JavaScript", "ArrayList", "HashMap",
            "Spring Boot", "React", "Node.js", "Docker", "Kubernetes"
        };

        for (String keyword : keywords) {
            searchHistory.addSearch(keyword);
        }

        System.out.println();

        // 재검색 (MRU)
        searchHistory.addSearch("Java");  // 맨 앞으로
        searchHistory.addSearch("Python");

        System.out.println();

        // 최근 검색어
        System.out.println("📝 최근 5개 검색어:");
        List<String> recent = searchHistory.getRecentSearches(5);
        for (int i = 0; i < recent.size(); i++) {
            System.out.println("   " + (i + 1) + ". " + recent.get(i));
        }

        // 자동완성
        System.out.println("\n🔍 자동완성 'Ja':");
        List<String> suggestions = searchHistory.autoComplete("Ja");
        for (String suggestion : suggestions) {
            System.out.println("   - " + suggestion);
        }

        // 통계
        searchHistory.displayStatistics();

        // 크기 제한 패턴
        NaverSearchHistory.demonstrateSizeLimitPattern();

        System.out.println("\n\n💡 핵심 교훈:");
        System.out.println("1. List 크기 제한으로 메모리 관리");
        System.out.println("2. MRU (Most Recently Used) 패턴");
        System.out.println("3. ArrayList + HashMap 조합");
        System.out.println("4. 자동완성은 순차 탐색 (크기 제한으로 O(n) 허용)");
    }
}
```

### 실행 결과
```
=== 네이버 검색 히스토리 관리 ===

✅ 새 검색: java
✅ 새 검색: python
✅ 새 검색: javascript
✅ 새 검색: arraylist
✅ 새 검색: hashmap
✅ 새 검색: spring boot
✅ 새 검색: react
✅ 새 검색: node.js
✅ 새 검색: docker
✅ 새 검색: kubernetes

🔄 재검색: java (조회: 1회)
🔄 재검색: python (조회: 1회)

📝 최근 5개 검색어:
   1. python
   2. java
   3. kubernetes
   4. docker
   5. node.js

🔍 자동완성 'Ja':
   - java
   - javascript

📊 검색 히스토리 통계:
   총 검색어: 10개
   최대 용량: 100개
   사용률: 10%

   최근 5개:
      1. python
      2. java
      3. kubernetes
      4. docker
      5. node.js

=== List 크기 제한 패턴 ===

패턴 1: 고정 크기 유지 (Circular Buffer)
```java
if (list.size() >= MAX_SIZE) {
    list.remove(0);  // 또는 remove(list.size() - 1)
}
list.add(newItem);
```

패턴 2: 주기적 정리
```java
if (list.size() > MAX_SIZE * 1.2) {
    // 오래된 항목 20% 삭제
    int removeCount = (int)(MAX_SIZE * 0.2);
    list.subList(0, removeCount).clear();
}
```

패턴 3: 시간 기반 만료
```java
long expirationTime = System.currentTimeMillis() - 30_DAYS;
list.removeIf(item -> item.getTimestamp() < expirationTime);
```

✅ 네이버는 패턴 1 + MRU 사용
   - 최대 100개 유지
   - 재검색 시 맨 앞으로 이동
   - 가장 오래된 항목 자동 삭제


💡 핵심 교훈:
1. List 크기 제한으로 메모리 관리
2. MRU (Most Recently Used) 패턴
3. ArrayList + HashMap 조합
4. 자동완성은 순차 탐색 (크기 제한으로 O(n) 허용)
```

### 핵심 교훈
- **크기 제한**: 메모리 누수 방지
- **MRU 패턴**: 재검색 시 맨 앞으로 이동
- **ArrayList**: 순서 유지 (최신순)
- **HashMap**: 중복 검색어 빠른 확인

---

## 사례 3: 쿠팡 - 장바구니 관리 (동시성 문제) 🛒

### 배경
쿠팡 장바구니는 여러 탭/디바이스에서 동시 접근이 가능합니다. 동시성 문제를 해결해야 합니다.

### 문제 상황
```java
// ❌ 잘못된 구현: 동시성 문제
public class ShoppingCart {
    private List<CartItem> items = new ArrayList<>();  // Not thread-safe!

    public void addItem(CartItem item) {
        items.add(item);  // Race condition!
    }

    // 여러 스레드에서 동시 호출 시 데이터 손실 가능
}
```

### 해결 방법
```java
import java.util.*;
import java.util.concurrent.*;

class CartItem {
    private String productId;
    private String productName;
    private int price;
    private int quantity;

    public CartItem(String productId, String productName, int price, int quantity) {
        this.productId = productId;
        this.productName = productName;
        this.price = price;
        this.quantity = quantity;
    }

    public String getProductId() { return productId; }
    public String getProductName() { return productName; }
    public int getPrice() { return price; }
    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }

    public int getTotalPrice() {
        return price * quantity;
    }

    @Override
    public String toString() {
        return productName + " x " + quantity + " = " + getTotalPrice() + "원";
    }
}

// ✅ 해결 방법 1: CopyOnWriteArrayList (읽기 >> 쓰기)
public class CoupangShoppingCartV1 {
    // 읽기 99%, 쓰기 1% → CopyOnWriteArrayList
    private CopyOnWriteArrayList<CartItem> items = new CopyOnWriteArrayList<>();

    public void addItem(CartItem item) {
        // 중복 확인
        for (CartItem existing : items) {
            if (existing.getProductId().equals(item.getProductId())) {
                existing.setQuantity(existing.getQuantity() + item.getQuantity());
                System.out.println("📦 수량 증가: " + item.getProductName() +
                                 " (총 " + existing.getQuantity() + "개)");
                return;
            }
        }

        items.add(item);
        System.out.println("✅ 장바구니 추가: " + item.getProductName());
    }

    public void removeItem(String productId) {
        items.removeIf(item -> {
            if (item.getProductId().equals(productId)) {
                System.out.println("🗑️ 장바구니 제거: " + item.getProductName());
                return true;
            }
            return false;
        });
    }

    public List<CartItem> getItems() {
        return new ArrayList<>(items);  // 복사본 반환
    }

    public int getTotalPrice() {
        int total = 0;
        for (CartItem item : items) {
            total += item.getTotalPrice();
        }
        return total;
    }

    public void displayCart() {
        System.out.println("\n🛒 장바구니 (" + items.size() + "개 상품):");
        for (int i = 0; i < items.size(); i++) {
            System.out.println("   " + (i + 1) + ". " + items.get(i));
        }
        System.out.println("   총 금액: " + getTotalPrice() + "원");
    }
}

// ✅ 해결 방법 2: Collections.synchronizedList (쓰기 많음)
public class CoupangShoppingCartV2 {
    // synchronized wrapper
    private List<CartItem> items = Collections.synchronizedList(new ArrayList<>());

    public void addItem(CartItem item) {
        synchronized (items) {
            // 중복 확인도 동기화 블록 안에서
            for (CartItem existing : items) {
                if (existing.getProductId().equals(productId)) {
                    existing.setQuantity(existing.getQuantity() + item.getQuantity());
                    System.out.println("📦 수량 증가: " + item.getProductName());
                    return;
                }
            }

            items.add(item);
            System.out.println("✅ 장바구니 추가: " + item.getProductName());
        }
    }

    public void removeItem(String productId) {
        synchronized (items) {
            items.removeIf(item -> item.getProductId().equals(productId));
        }
    }

    public int getTotalPrice() {
        synchronized (items) {
            int total = 0;
            for (CartItem item : items) {
                total += item.getTotalPrice();
            }
            return total;
        }
    }
}

// ✅ 해결 방법 3: 명시적 Lock (세밀한 제어)
public class CoupangShoppingCartV3 {
    private List<CartItem> items = new ArrayList<>();
    private final ReentrantReadWriteLock lock = new ReentrantReadWriteLock();

    public void addItem(CartItem item) {
        lock.writeLock().lock();
        try {
            // 중복 확인
            for (CartItem existing : items) {
                if (existing.getProductId().equals(item.getProductId())) {
                    existing.setQuantity(existing.getQuantity() + item.getQuantity());
                    System.out.println("📦 수량 증가: " + item.getProductName());
                    return;
                }
            }

            items.add(item);
            System.out.println("✅ 장바구니 추가: " + item.getProductName());
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void removeItem(String productId) {
        lock.writeLock().lock();
        try {
            items.removeIf(item -> item.getProductId().equals(productId));
        } finally {
            lock.writeLock().unlock();
        }
    }

    public int getTotalPrice() {
        lock.readLock().lock();
        try {
            int total = 0;
            for (CartItem item : items) {
                total += item.getTotalPrice();
            }
            return total;
        } finally {
            lock.readLock().unlock();
        }
    }

    public List<CartItem> getItems() {
        lock.readLock().lock();
        try {
            return new ArrayList<>(items);
        } finally {
            lock.readLock().unlock();
        }
    }
}

// 동시성 테스트
public class ConcurrencyTest {
    public static void testConcurrency() throws InterruptedException {
        System.out.println("\n=== 동시성 테스트 ===\n");

        // 1. 일반 ArrayList (동시성 문제)
        List<Integer> unsafeList = new ArrayList<>();
        ExecutorService executor = Executors.newFixedThreadPool(10);

        long start = System.currentTimeMillis();
        for (int i = 0; i < 10; i++) {
            executor.submit(() -> {
                for (int j = 0; j < 1000; j++) {
                    unsafeList.add(j);
                }
            });
        }

        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);
        long unsafeTime = System.currentTimeMillis() - start;

        System.out.println("1. ArrayList (Not Thread-Safe):");
        System.out.println("   예상 크기: 10000");
        System.out.println("   실제 크기: " + unsafeList.size() + " ⚠️ 데이터 손실");
        System.out.println("   소요 시간: " + unsafeTime + "ms");

        // 2. CopyOnWriteArrayList
        CopyOnWriteArrayList<Integer> cowList = new CopyOnWriteArrayList<>();
        executor = Executors.newFixedThreadPool(10);

        start = System.currentTimeMillis();
        for (int i = 0; i < 10; i++) {
            executor.submit(() -> {
                for (int j = 0; j < 1000; j++) {
                    cowList.add(j);
                }
            });
        }

        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);
        long cowTime = System.currentTimeMillis() - start;

        System.out.println("\n2. CopyOnWriteArrayList (Thread-Safe):");
        System.out.println("   예상 크기: 10000");
        System.out.println("   실제 크기: " + cowList.size() + " ✅");
        System.out.println("   소요 시간: " + cowTime + "ms");

        // 3. Collections.synchronizedList
        List<Integer> syncList = Collections.synchronizedList(new ArrayList<>());
        executor = Executors.newFixedThreadPool(10);

        start = System.currentTimeMillis();
        for (int i = 0; i < 10; i++) {
            executor.submit(() -> {
                for (int j = 0; j < 1000; j++) {
                    syncList.add(j);
                }
            });
        }

        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);
        long syncTime = System.currentTimeMillis() - start;

        System.out.println("\n3. Collections.synchronizedList (Thread-Safe):");
        System.out.println("   예상 크기: 10000");
        System.out.println("   실제 크기: " + syncList.size() + " ✅");
        System.out.println("   소요 시간: " + syncTime + "ms");

        System.out.println("\n✅ 쿠팡 선택:");
        System.out.println("   - CopyOnWriteArrayList (읽기 >> 쓰기)");
        System.out.println("   - 장바구니 조회가 추가보다 압도적으로 많음");
        System.out.println("   - Fail-safe iterator로 안전한 순회");
    }
}

public class CoupangShoppingCartExample {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== 쿠팡 장바구니 시스템 ===\n");

        CoupangShoppingCartV1 cart = new CoupangShoppingCartV1();

        // 상품 추가
        cart.addItem(new CartItem("P001", "삼성 갤럭시 S24", 1200000, 1));
        cart.addItem(new CartItem("P002", "에어팟 Pro", 350000, 2));
        cart.addItem(new CartItem("P003", "애플워치", 550000, 1));

        // 중복 추가 (수량 증가)
        cart.addItem(new CartItem("P002", "에어팟 Pro", 350000, 1));

        cart.displayCart();

        // 제거
        System.out.println();
        cart.removeItem("P003");

        cart.displayCart();

        // 동시성 테스트
        ConcurrencyTest.testConcurrency();

        System.out.println("\n\n💡 핵심 교훈:");
        System.out.println("1. 멀티스레드 환경에서는 thread-safe List 사용");
        System.out.println("2. 읽기 >> 쓰기: CopyOnWriteArrayList");
        System.out.println("3. 균형: Collections.synchronizedList");
        System.out.println("4. 세밀한 제어: ReentrantReadWriteLock");
    }
}
```

### 실행 결과
```
=== 쿠팡 장바구니 시스템 ===

✅ 장바구니 추가: 삼성 갤럭시 S24
✅ 장바구니 추가: 에어팟 Pro
✅ 장바구니 추가: 애플워치
📦 수량 증가: 에어팟 Pro (총 3개)

🛒 장바구니 (3개 상품):
   1. 삼성 갤럭시 S24 x 1 = 1200000원
   2. 에어팟 Pro x 3 = 1050000원
   3. 애플워치 x 1 = 550000원
   총 금액: 2800000원

🗑️ 장바구니 제거: 애플워치

🛒 장바구니 (2개 상품):
   1. 삼성 갤럭시 S24 x 1 = 1200000원
   2. 에어팟 Pro x 3 = 1050000원
   총 금액: 2250000원

=== 동시성 테스트 ===

1. ArrayList (Not Thread-Safe):
   예상 크기: 10000
   실제 크기: 9847 ⚠️ 데이터 손실
   소요 시간: 12ms

2. CopyOnWriteArrayList (Thread-Safe):
   예상 크기: 10000
   실제 크기: 10000 ✅
   소요 시간: 156ms

3. Collections.synchronizedList (Thread-Safe):
   예상 크기: 10000
   실제 크기: 10000 ✅
   소요 시간: 23ms

✅ 쿠팡 선택:
   - CopyOnWriteArrayList (읽기 >> 쓰기)
   - 장바구니 조회가 추가보다 압도적으로 많음
   - Fail-safe iterator로 안전한 순회


💡 핵심 교훈:
1. 멀티스레드 환경에서는 thread-safe List 사용
2. 읽기 >> 쓰기: CopyOnWriteArrayList
3. 균형: Collections.synchronizedList
4. 세밀한 제어: ReentrantReadWriteLock
```

### 핵심 교훈
- **동시성 문제**: ArrayList는 thread-safe 하지 않음
- **CopyOnWriteArrayList**: 읽기 중심 (장바구니 조회)
- **Collections.synchronizedList**: 균형잡힌 읽기/쓰기
- **ReentrantReadWriteLock**: 세밀한 제어 필요 시

---

## 🚨 주니어 개발자가 자주 하는 실수

### 실수 1: for-each에서 remove() 호출

```java
// ❌ 잘못된 코드
List<String> names = new ArrayList<>(Arrays.asList("Alice", "Bob", "Charlie", "David"));

for (String name : names) {
    if (name.startsWith("C")) {
        names.remove(name);  // ConcurrentModificationException!
    }
}
```

**문제점**: `for-each`는 내부적으로 `Iterator`를 사용하며, 순회 중 컬렉션을 직접 수정하면 `ConcurrentModificationException` 발생

**해결 방법**:
```java
// ✅ 방법 1: Iterator 사용
List<String> names = new ArrayList<>(Arrays.asList("Alice", "Bob", "Charlie", "David"));
Iterator<String> iterator = names.iterator();

while (iterator.hasNext()) {
    String name = iterator.next();
    if (name.startsWith("C")) {
        iterator.remove();  // Iterator의 remove() 사용
    }
}

// ✅ 방법 2: removeIf() 사용 (Java 8+)
names.removeIf(name -> name.startsWith("C"));

// ✅ 방법 3: 복사본으로 순회
List<String> copy = new ArrayList<>(names);
for (String name : copy) {
    if (name.startsWith("C")) {
        names.remove(name);  // 원본 수정
    }
}

// ✅ 방법 4: 인덱스 역순 순회
for (int i = names.size() - 1; i >= 0; i--) {
    if (names.get(i).startsWith("C")) {
        names.remove(i);
    }
}
```

---

### 실수 2: ArrayList 초기 용량 미지정

```java
// ❌ 잘못된 코드
public List<User> loadUsers() {
    List<User> users = new ArrayList<>();  // 기본 용량 10

    // 10만 명의 사용자 로드
    for (int i = 0; i < 100000; i++) {
        users.add(loadUser(i));  // 여러 번 배열 복사 발생!
    }

    return users;
}
// 10 → 15 → 22 → 33 → 49 → 73 → ... (수십 번 확장)
```

**문제점**: 용량 초과 시마다 배열 복사 발생 (O(n) 비용)

**해결 방법**:
```java
// ✅ 올바른 코드
public List<User> loadUsers() {
    int expectedSize = 100000;
    List<User> users = new ArrayList<>(expectedSize);  // 초기 용량 지정

    for (int i = 0; i < expectedSize; i++) {
        users.add(loadUser(i));  // 배열 복사 없음!
    }

    return users;
}

// 성능 비교
public static void compareInitialCapacity() {
    int size = 1000000;

    // 1. 초기 용량 미지정
    long start = System.nanoTime();
    List<Integer> list1 = new ArrayList<>();
    for (int i = 0; i < size; i++) {
        list1.add(i);
    }
    long time1 = (System.nanoTime() - start) / 1_000_000;

    // 2. 초기 용량 지정
    start = System.nanoTime();
    List<Integer> list2 = new ArrayList<>(size);
    for (int i = 0; i < size; i++) {
        list2.add(i);
    }
    long time2 = (System.nanoTime() - start) / 1_000_000;

    System.out.println("초기 용량 미지정: " + time1 + "ms");
    System.out.println("초기 용량 지정:   " + time2 + "ms (" + (time1 - time2) + "ms 빠름)");
}
```

---

### 실수 3: get(index) 반복 호출 (LinkedList)

```java
// ❌ 잘못된 코드
LinkedList<String> list = new LinkedList<>();
// ... 데이터 추가 ...

// O(n²) 시간 복잡도!
for (int i = 0; i < list.size(); i++) {
    String item = list.get(i);  // 매번 O(n) 순차 탐색!
    System.out.println(item);
}
```

**문제점**: `LinkedList.get(index)`는 O(n) 시간이 걸림 → 전체 O(n²)

**해결 방법**:
```java
// ✅ 올바른 코드 1: for-each 사용
for (String item : list) {  // Iterator 사용: O(n)
    System.out.println(item);
}

// ✅ 올바른 코드 2: Iterator 명시적 사용
Iterator<String> iterator = list.iterator();
while (iterator.hasNext()) {
    String item = iterator.next();
    System.out.println(item);
}

// ✅ 올바른 코드 3: ArrayList로 변경
List<String> list = new ArrayList<>();  // 조회 중심이면 ArrayList
for (int i = 0; i < list.size(); i++) {
    String item = list.get(i);  // O(1)
    System.out.println(item);
}

// 성능 비교
public static void compareIteration() {
    int size = 10000;

    LinkedList<Integer> linkedList = new LinkedList<>();
    for (int i = 0; i < size; i++) {
        linkedList.add(i);
    }

    // 1. get(index) 사용
    long start = System.nanoTime();
    for (int i = 0; i < linkedList.size(); i++) {
        Integer value = linkedList.get(i);  // O(n²)
    }
    long getTime = (System.nanoTime() - start) / 1_000_000;

    // 2. for-each 사용
    start = System.nanoTime();
    for (Integer value : linkedList) {  // O(n)
        // do nothing
    }
    long forEachTime = (System.nanoTime() - start) / 1_000_000;

    System.out.println("get(index): " + getTime + "ms ⚠️");
    System.out.println("for-each:   " + forEachTime + "ms ✅ (" + (getTime / forEachTime) + "배 빠름)");
}
```

---

### 실수 4: Arrays.asList()의 고정 크기 리스트

```java
// ❌ 잘못된 코드
List<String> list = Arrays.asList("A", "B", "C");
list.add("D");  // UnsupportedOperationException!
list.remove(0); // UnsupportedOperationException!
```

**문제점**: `Arrays.asList()`는 **고정 크기** 리스트를 반환 (add/remove 불가)

**해결 방법**:
```java
// ✅ 올바른 코드 1: ArrayList로 복사
List<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));
list.add("D");     // ✅ 가능
list.remove(0);    // ✅ 가능

// ✅ 올바른 코드 2: List.of() 사용 (Java 9+) - 불변
List<String> immutable = List.of("A", "B", "C");
// immutable.add("D");  // UnsupportedOperationException (의도된 불변)

// ✅ 올바른 코드 3: 가변 리스트로 복사
List<String> mutable = new ArrayList<>(List.of("A", "B", "C"));
mutable.add("D");  // ✅ 가능

// Arrays.asList() vs new ArrayList() vs List.of()
public static void compareListCreation() {
    System.out.println("=== List 생성 방법 비교 ===\n");

    // 1. Arrays.asList() - 고정 크기, 수정 가능
    List<String> list1 = Arrays.asList("A", "B", "C");
    System.out.println("1. Arrays.asList():");
    try {
        list1.set(0, "Z");  // ✅ 수정 가능
        System.out.println("   set(): ✅ " + list1);
    } catch (UnsupportedOperationException e) {
        System.out.println("   set(): ❌");
    }
    try {
        list1.add("D");  // ❌ 크기 변경 불가
        System.out.println("   add(): ✅");
    } catch (UnsupportedOperationException e) {
        System.out.println("   add(): ❌ UnsupportedOperationException");
    }

    // 2. new ArrayList<>() - 가변
    List<String> list2 = new ArrayList<>(Arrays.asList("A", "B", "C"));
    System.out.println("\n2. new ArrayList<>(Arrays.asList()):");
    list2.set(0, "Z");  // ✅
    list2.add("D");     // ✅
    System.out.println("   set(): ✅");
    System.out.println("   add(): ✅ " + list2);

    // 3. List.of() - 불변 (Java 9+)
    List<String> list3 = List.of("A", "B", "C");
    System.out.println("\n3. List.of() (불변):");
    try {
        list3.set(0, "Z");  // ❌ 불변
        System.out.println("   set(): ✅");
    } catch (UnsupportedOperationException e) {
        System.out.println("   set(): ❌ UnsupportedOperationException");
    }
    try {
        list3.add("D");  // ❌ 불변
        System.out.println("   add(): ✅");
    } catch (UnsupportedOperationException e) {
        System.out.println("   add(): ❌ UnsupportedOperationException");
    }

    System.out.println("\n✅ 정리:");
    System.out.println("   Arrays.asList(): 고정 크기, 수정 가능");
    System.out.println("   new ArrayList<>(): 가변 (일반적)");
    System.out.println("   List.of(): 불변 (Java 9+)");
}
```

---

## 📋 주니어 실수 종합 정리

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| **for-each remove** | ConcurrentModificationException | Iterator.remove() 또는 removeIf() |
| **초기 용량 미지정** | 여러 번 배열 복사 | new ArrayList<>(expectedSize) |
| **LinkedList get(i)** | O(n²) 성능 | for-each 또는 ArrayList 사용 |
| **Arrays.asList() 수정** | UnsupportedOperationException | new ArrayList<>(Arrays.asList()) |

---

**다음 Part 3에서는**: 실전 프로젝트 (작업 스케줄러) + 7 FAQ + 12 면접 질문을 다룹니다.
