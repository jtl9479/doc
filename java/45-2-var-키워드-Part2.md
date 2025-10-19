# 45장 var 키워드 - Part 2: 기업 사례 & 주니어 개발자 시나리오

## 📚 목차
1. [3개 기업 실전 사례](#기업-사례)
   - 카카오: 대용량 데이터 처리
   - 배민: 주문 시스템
   - 당근마켓: 검색 필터
2. [4개 주니어 개발자 실수 시나리오](#주니어-실수-시나리오)

---

## 🏢 기업 사례

### 🔷 기업 사례 1: 카카오 - 대용량 데이터 처리 파이프라인

#### 📌 비즈니스 배경

카카오톡 메시지 분석 시스템에서 수백만 개의 메시지 데이터를 처리해야 합니다.

**요구사항**:
- 복잡한 제네릭 타입 (Map, List 중첩)
- Stream API 대량 사용
- 코드 가독성 유지
- 타입 안전성 보장

**문제 상황 (Before)**:
```java
// 타입 선언이 너무 길고 반복적
Map<String, Map<String, List<MessageData>>> categoryData =
    new HashMap<String, Map<String, List<MessageData>>>();

Map<String, List<Map<String, Object>>> aggregatedData =
    new HashMap<String, List<Map<String, Object>>>();
```

#### 💡 var를 활용한 해결책

```java
package com.kakao.messaging;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 메시지 데이터
 */
class MessageData {
    private String userId;
    private String content;
    private String category;
    private LocalDateTime timestamp;
    private int length;

    public MessageData(String userId, String content, String category,
                       LocalDateTime timestamp) {
        this.userId = userId;
        this.content = content;
        this.category = category;
        this.timestamp = timestamp;
        this.length = content.length();
    }

    public String getUserId() { return userId; }
    public String getContent() { return content; }
    public String getCategory() { return category; }
    public LocalDateTime getTimestamp() { return timestamp; }
    public int getLength() { return length; }

    @Override
    public String toString() {
        return String.format("[%s] %s: %s", category, userId,
            content.substring(0, Math.min(20, content.length())));
    }
}

/**
 * 메시지 분석 파이프라인
 */
class MessageAnalyzer {

    /**
     * ✅ var를 사용한 복잡한 데이터 구조 처리
     */
    public Map<String, Map<String, List<MessageData>>> analyzeMessages(
        List<MessageData> messages) {

        System.out.println("=== 메시지 분석 시작 ===\n");

        // ✅ 복잡한 중첩 Map을 var로 간소화
        var categoryData = new HashMap<String, Map<String, List<MessageData>>>();

        for (var message : messages) {
            var category = message.getCategory();
            var userId = message.getUserId();

            // 카테고리별 Map 생성
            categoryData.putIfAbsent(category, new HashMap<>());
            var userMap = categoryData.get(category);

            // 사용자별 List 생성
            userMap.putIfAbsent(userId, new ArrayList<>());
            var messageList = userMap.get(userId);

            messageList.add(message);
        }

        return categoryData;
    }

    /**
     * ✅ Stream API와 var 조합
     */
    public Map<String, Long> getMessageCountByCategory(List<MessageData> messages) {
        // Before: 타입이 너무 김
        // Map<String, Long> result = messages.stream()...

        // After: var로 간소화
        var result = messages.stream()
            .collect(Collectors.groupingBy(
                MessageData::getCategory,
                Collectors.counting()
            ));

        return result;
    }

    /**
     * ✅ 복잡한 통계 데이터 생성
     */
    public Map<String, Map<String, Object>> generateStatistics(
        List<MessageData> messages) {

        var statistics = new HashMap<String, Map<String, Object>>();

        // 카테고리별 통계
        var categoryCounts = messages.stream()
            .collect(Collectors.groupingBy(
                MessageData::getCategory,
                Collectors.counting()
            ));

        // 카테고리별 평균 길이
        var categoryAvgLength = messages.stream()
            .collect(Collectors.groupingBy(
                MessageData::getCategory,
                Collectors.averagingInt(MessageData::getLength)
            ));

        for (var category : categoryCounts.keySet()) {
            var stats = new HashMap<String, Object>();
            stats.put("count", categoryCounts.get(category));
            stats.put("avgLength", categoryAvgLength.get(category));
            statistics.put(category, stats);
        }

        return statistics;
    }
}

/**
 * 카카오 메시지 분석 데모
 */
public class KakaoMessageAnalysisDemo {
    public static void main(String[] args) {
        System.out.println("=== 카카오 메시지 분석 시스템 ===\n");

        // 샘플 데이터 생성
        var messages = generateSampleMessages();
        var analyzer = new MessageAnalyzer();

        // 시나리오 1: 복잡한 중첩 데이터 구조
        System.out.println("📍 시나리오 1: 카테고리별 사용자별 메시지 분석");

        var categoryData = analyzer.analyzeMessages(messages);

        System.out.println("카테고리 수: " + categoryData.size());
        categoryData.forEach((category, userMap) -> {
            System.out.println("\n[" + category + "] 카테고리:");
            userMap.forEach((userId, messageList) -> {
                System.out.println("  " + userId + ": " + messageList.size() + "개 메시지");
            });
        });
        System.out.println();

        // 시나리오 2: Stream API 활용
        System.out.println("📍 시나리오 2: 카테고리별 메시지 수");

        var categoryCounts = analyzer.getMessageCountByCategory(messages);
        categoryCounts.forEach((category, count) -> {
            System.out.println("  " + category + ": " + count + "개");
        });
        System.out.println();

        // 시나리오 3: 통계 데이터 생성
        System.out.println("📍 시나리오 3: 카테고리별 상세 통계");

        var statistics = analyzer.generateStatistics(messages);
        statistics.forEach((category, stats) -> {
            System.out.println("[" + category + "]");
            System.out.println("  메시지 수: " + stats.get("count"));
            System.out.println("  평균 길이: " + String.format("%.1f", stats.get("avgLength")));
        });
        System.out.println();

        // 성과 측정
        System.out.println("📊 var 도입 효과:");
        System.out.println("✅ 코드 라인 수 30% 감소");
        System.out.println("✅ 타입 오류 발생률 감소");
        System.out.println("✅ 개발자 생산성 향상");
        System.out.println("✅ 코드 리뷰 시간 단축");
    }

    static List<MessageData> generateSampleMessages() {
        var now = LocalDateTime.now();

        return Arrays.asList(
            new MessageData("user1", "안녕하세요 카카오톡입니다", "일반", now),
            new MessageData("user2", "오픈채팅 참여했습니다", "오픈채팅", now),
            new MessageData("user1", "쇼핑 링크 공유", "쇼핑", now),
            new MessageData("user3", "단체채팅방 생성", "일반", now),
            new MessageData("user2", "이모티콘 선물", "선물", now),
            new MessageData("user3", "오픈채팅 대화중", "오픈채팅", now),
            new MessageData("user1", "상품 구매 완료", "쇼핑", now),
            new MessageData("user4", "선물하기 이용", "선물", now)
        );
    }
}
```

#### 🎯 핵심 포인트

**1. 복잡한 제네릭 타입 간소화**:
```java
// Before
Map<String, Map<String, List<MessageData>>> data =
    new HashMap<String, Map<String, List<MessageData>>>();

// After
var data = new HashMap<String, Map<String, List<MessageData>>>();
```

**2. Stream API 결과 타입**:
```java
// var로 복잡한 Collector 결과 타입 간소화
var result = messages.stream()
    .collect(Collectors.groupingBy(...));
```

**3. 코드 가독성 향상**:
```
- 타입 선언 중복 제거
- 핵심 로직에 집중
- 유지보수 용이
```

---

### 🔷 기업 사례 2: 배민 - 주문 처리 시스템

#### 📌 비즈니스 배경

배달의민족 주문 시스템에서 실시간 주문 데이터를 처리합니다.

**요구사항**:
- 주문 데이터 필터링
- 통계 데이터 생성
- 실시간 집계
- 가독성 있는 코드

**문제 상황**:
```java
// 타입 선언이 길고 반복적
Map<String, List<Order>> restaurantOrders = new HashMap<>();
Map<OrderStatus, Long> statusCounts = new HashMap<>();
```

#### 💡 var를 활용한 해결책

```java
package com.baemin.order;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 주문 상태
 */
enum OrderStatus {
    PENDING,    // 대기
    ACCEPTED,   // 접수
    COOKING,    // 조리중
    DELIVERING, // 배달중
    COMPLETED,  // 완료
    CANCELLED   // 취소
}

/**
 * 주문 정보
 */
class Order {
    private String orderId;
    private String restaurantId;
    private String customerId;
    private int totalAmount;
    private OrderStatus status;
    private LocalDateTime orderTime;

    public Order(String orderId, String restaurantId, String customerId,
                 int totalAmount, OrderStatus status, LocalDateTime orderTime) {
        this.orderId = orderId;
        this.restaurantId = restaurantId;
        this.customerId = customerId;
        this.totalAmount = totalAmount;
        this.status = status;
        this.orderTime = orderTime;
    }

    public String getOrderId() { return orderId; }
    public String getRestaurantId() { return restaurantId; }
    public String getCustomerId() { return customerId; }
    public int getTotalAmount() { return totalAmount; }
    public OrderStatus getStatus() { return status; }
    public LocalDateTime getOrderTime() { return orderTime; }

    @Override
    public String toString() {
        return String.format("[%s] %s: %,d원 (%s)",
            orderId, restaurantId, totalAmount, status);
    }
}

/**
 * 주문 처리 시스템
 */
class OrderProcessor {

    /**
     * ✅ var를 사용한 주문 그룹핑
     */
    public Map<String, List<Order>> groupByRestaurant(List<Order> orders) {
        // Before: Map<String, List<Order>> result = ...

        // After: var로 간소화
        var result = orders.stream()
            .collect(Collectors.groupingBy(Order::getRestaurantId));

        return result;
    }

    /**
     * ✅ 상태별 주문 통계
     */
    public Map<OrderStatus, Long> getStatusStatistics(List<Order> orders) {
        var statistics = orders.stream()
            .collect(Collectors.groupingBy(
                Order::getStatus,
                Collectors.counting()
            ));

        return statistics;
    }

    /**
     * ✅ 음식점별 매출 통계
     */
    public Map<String, Integer> getRevenueByRestaurant(List<Order> orders) {
        var revenue = orders.stream()
            .filter(order -> order.getStatus() == OrderStatus.COMPLETED)
            .collect(Collectors.groupingBy(
                Order::getRestaurantId,
                Collectors.summingInt(Order::getTotalAmount)
            ));

        return revenue;
    }

    /**
     * ✅ 복잡한 분석 데이터 생성
     */
    public Map<String, Map<String, Object>> generateAnalytics(List<Order> orders) {
        var analytics = new HashMap<String, Map<String, Object>>();

        // 음식점별 그룹핑
        var restaurantOrders = groupByRestaurant(orders);

        for (var entry : restaurantOrders.entrySet()) {
            var restaurantId = entry.getKey();
            var orderList = entry.getValue();

            var stats = new HashMap<String, Object>();
            stats.put("totalOrders", orderList.size());
            stats.put("totalRevenue", orderList.stream()
                .filter(o -> o.getStatus() == OrderStatus.COMPLETED)
                .mapToInt(Order::getTotalAmount)
                .sum());
            stats.put("avgOrderAmount", orderList.stream()
                .mapToInt(Order::getTotalAmount)
                .average()
                .orElse(0.0));

            analytics.put(restaurantId, stats);
        }

        return analytics;
    }
}

/**
 * 배민 주문 시스템 데모
 */
public class BaeminOrderDemo {
    public static void main(String[] args) {
        System.out.println("=== 배민 주문 처리 시스템 ===\n");

        var orders = generateSampleOrders();
        var processor = new OrderProcessor();

        // 시나리오 1: 음식점별 주문 그룹핑
        System.out.println("📍 시나리오 1: 음식점별 주문 현황");

        var restaurantOrders = processor.groupByRestaurant(orders);
        restaurantOrders.forEach((restaurantId, orderList) -> {
            System.out.println(restaurantId + ": " + orderList.size() + "건");
        });
        System.out.println();

        // 시나리오 2: 상태별 통계
        System.out.println("📍 시나리오 2: 주문 상태별 통계");

        var statusStats = processor.getStatusStatistics(orders);
        statusStats.forEach((status, count) -> {
            System.out.println("  " + status + ": " + count + "건");
        });
        System.out.println();

        // 시나리오 3: 음식점별 매출
        System.out.println("📍 시나리오 3: 음식점별 매출 (완료 주문만)");

        var revenue = processor.getRevenueByRestaurant(orders);
        revenue.forEach((restaurantId, amount) -> {
            System.out.println("  " + restaurantId + ": " +
                String.format("%,d", amount) + "원");
        });
        System.out.println();

        // 시나리오 4: 종합 분석
        System.out.println("📍 시나리오 4: 음식점별 종합 분석");

        var analytics = processor.generateAnalytics(orders);
        analytics.forEach((restaurantId, stats) -> {
            System.out.println("[" + restaurantId + "]");
            System.out.println("  주문 수: " + stats.get("totalOrders"));
            System.out.println("  총 매출: " +
                String.format("%,d", stats.get("totalRevenue")) + "원");
            System.out.println("  평균 주문액: " +
                String.format("%.0f", stats.get("avgOrderAmount")) + "원");
        });
        System.out.println();

        System.out.println("📊 var 도입 효과:");
        System.out.println("✅ 타입 선언 간소화");
        System.out.println("✅ Stream API 사용 편의성 증가");
        System.out.println("✅ 코드 유지보수성 향상");
    }

    static List<Order> generateSampleOrders() {
        var now = LocalDateTime.now();

        return Arrays.asList(
            new Order("O001", "R001", "C001", 25000, OrderStatus.COMPLETED, now),
            new Order("O002", "R001", "C002", 32000, OrderStatus.DELIVERING, now),
            new Order("O003", "R002", "C003", 18000, OrderStatus.COMPLETED, now),
            new Order("O004", "R001", "C004", 45000, OrderStatus.COOKING, now),
            new Order("O005", "R003", "C005", 22000, OrderStatus.ACCEPTED, now),
            new Order("O006", "R002", "C006", 28000, OrderStatus.COMPLETED, now),
            new Order("O007", "R003", "C007", 35000, OrderStatus.CANCELLED, now),
            new Order("O008", "R001", "C008", 40000, OrderStatus.PENDING, now)
        );
    }
}
```

#### 🎯 핵심 포인트

**1. Stream Collectors와 var**:
```java
// 복잡한 groupingBy 결과를 var로 간소화
var grouped = orders.stream()
    .collect(Collectors.groupingBy(Order::getRestaurantId));
```

**2. 반복문에서 var 활용**:
```java
for (var entry : map.entrySet()) {
    var key = entry.getKey();
    var value = entry.getValue();
}
```

---

### 🔷 기업 사례 3: 당근마켓 - 검색 필터 시스템

#### 📌 비즈니스 배경

당근마켓에서 중고물품 검색 필터링 기능을 구현합니다.

**요구사항**:
- 다양한 필터 조건 (가격, 카테고리, 지역)
- 동적 필터 조합
- 검색 결과 정렬
- 코드 간결성

#### 💡 var를 활용한 해결책

```java
package com.daangn.search;

import java.util.*;
import java.util.function.Predicate;
import java.util.stream.Collectors;

/**
 * 상품 정보
 */
class Product {
    private String id;
    private String title;
    private int price;
    private String category;
    private String location;
    private int viewCount;

    public Product(String id, String title, int price, String category,
                   String location, int viewCount) {
        this.id = id;
        this.title = title;
        this.price = price;
        this.category = category;
        this.location = location;
        this.viewCount = viewCount;
    }

    public String getId() { return id; }
    public String getTitle() { return title; }
    public int getPrice() { return price; }
    public String getCategory() { return category; }
    public String getLocation() { return location; }
    public int getViewCount() { return viewCount; }

    @Override
    public String toString() {
        return String.format("[%s] %s - %,d원 (%s, 조회 %d)",
            category, title, price, location, viewCount);
    }
}

/**
 * 검색 필터 시스템
 */
class SearchFilter {

    /**
     * ✅ var를 사용한 동적 필터 생성
     */
    public List<Product> search(List<Product> products, Map<String, Object> filters) {
        // 동적으로 필터 조건 생성
        var predicate = buildPredicate(filters);

        // 필터 적용
        var filtered = products.stream()
            .filter(predicate)
            .collect(Collectors.toList());

        return filtered;
    }

    /**
     * ✅ 필터 조건 빌더
     */
    private Predicate<Product> buildPredicate(Map<String, Object> filters) {
        var predicate = (Predicate<Product>) (p -> true);  // 초기 조건

        // 가격 범위 필터
        if (filters.containsKey("minPrice")) {
            var minPrice = (int) filters.get("minPrice");
            predicate = predicate.and(p -> p.getPrice() >= minPrice);
        }

        if (filters.containsKey("maxPrice")) {
            var maxPrice = (int) filters.get("maxPrice");
            predicate = predicate.and(p -> p.getPrice() <= maxPrice);
        }

        // 카테고리 필터
        if (filters.containsKey("category")) {
            var category = (String) filters.get("category");
            predicate = predicate.and(p -> p.getCategory().equals(category));
        }

        // 지역 필터
        if (filters.containsKey("location")) {
            var location = (String) filters.get("location");
            predicate = predicate.and(p -> p.getLocation().equals(location));
        }

        return predicate;
    }

    /**
     * ✅ 검색 결과 정렬
     */
    public List<Product> searchAndSort(List<Product> products,
                                       Map<String, Object> filters,
                                       String sortBy) {
        var filtered = search(products, filters);

        // 정렬 기준 선택
        var comparator = switch (sortBy) {
            case "price_asc" -> Comparator.comparing(Product::getPrice);
            case "price_desc" -> Comparator.comparing(Product::getPrice).reversed();
            case "views" -> Comparator.comparing(Product::getViewCount).reversed();
            default -> Comparator.comparing(Product::getTitle);
        };

        // 정렬 적용
        var sorted = filtered.stream()
            .sorted(comparator)
            .collect(Collectors.toList());

        return sorted;
    }

    /**
     * ✅ 카테고리별 통계
     */
    public Map<String, Long> getCategoryStatistics(List<Product> products) {
        var stats = products.stream()
            .collect(Collectors.groupingBy(
                Product::getCategory,
                Collectors.counting()
            ));

        return stats;
    }
}

/**
 * 당근마켓 검색 데모
 */
public class DaangnSearchDemo {
    public static void main(String[] args) {
        System.out.println("=== 당근마켓 검색 필터 시스템 ===\n");

        var products = generateSampleProducts();
        var filter = new SearchFilter();

        // 시나리오 1: 가격 범위 필터
        System.out.println("📍 시나리오 1: 가격 범위 검색 (10만원 ~ 50만원)");

        var filters1 = new HashMap<String, Object>();
        filters1.put("minPrice", 100000);
        filters1.put("maxPrice", 500000);

        var result1 = filter.search(products, filters1);
        result1.forEach(p -> System.out.println("  " + p));
        System.out.println();

        // 시나리오 2: 카테고리 + 지역 필터
        System.out.println("📍 시나리오 2: 전자기기 + 서울 지역");

        var filters2 = new HashMap<String, Object>();
        filters2.put("category", "전자기기");
        filters2.put("location", "서울");

        var result2 = filter.search(products, filters2);
        result2.forEach(p -> System.out.println("  " + p));
        System.out.println();

        // 시나리오 3: 필터 + 정렬
        System.out.println("📍 시나리오 3: 가격 낮은 순 정렬");

        var filters3 = new HashMap<String, Object>();
        filters3.put("category", "전자기기");

        var result3 = filter.searchAndSort(products, filters3, "price_asc");
        result3.forEach(p -> System.out.println("  " + p));
        System.out.println();

        // 시나리오 4: 카테고리별 통계
        System.out.println("📍 시나리오 4: 카테고리별 상품 수");

        var stats = filter.getCategoryStatistics(products);
        stats.forEach((category, count) -> {
            System.out.println("  " + category + ": " + count + "개");
        });
        System.out.println();

        System.out.println("📊 var 도입 효과:");
        System.out.println("✅ 필터 로직 간결화");
        System.out.println("✅ 동적 필터 구성 용이");
        System.out.println("✅ 코드 가독성 향상");
    }

    static List<Product> generateSampleProducts() {
        return Arrays.asList(
            new Product("P001", "아이폰 13", 700000, "전자기기", "서울", 150),
            new Product("P002", "에어팟 프로", 250000, "전자기기", "서울", 80),
            new Product("P003", "나이키 운동화", 80000, "패션", "부산", 45),
            new Product("P004", "책상", 150000, "가구", "서울", 30),
            new Product("P005", "노트북", 1200000, "전자기기", "인천", 200),
            new Product("P006", "의자", 120000, "가구", "서울", 25),
            new Product("P007", "자전거", 300000, "스포츠", "부산", 60),
            new Product("P008", "갤럭시 버즈", 180000, "전자기기", "서울", 90)
        );
    }
}
```

#### 🎯 핵심 포인트

**1. 동적 필터 생성**:
```java
// var로 Predicate 조합을 간결하게
var predicate = (Predicate<Product>) (p -> true);
predicate = predicate.and(p -> p.getPrice() > 100000);
```

**2. Switch 표현식과 var**:
```java
var comparator = switch (sortBy) {
    case "price" -> Comparator.comparing(Product::getPrice);
    case "views" -> Comparator.comparing(Product::getViewCount);
    default -> Comparator.comparing(Product::getTitle);
};
```

---

## 🚨 주니어 실수 시나리오

### ❌ 실수 1: var를 모든 곳에 무분별하게 사용

#### 문제 코드

```java
package var.mistakes;

import java.util.*;

public class Mistake1_OverusingVar {
    public static void main(String[] args) {
        // ❌ 타입이 불명확한 경우
        var data = getData();  // 뭐가 반환되는지?
        var result = process();  // 타입을 알 수 없음
        var value = calculate();  // int? long? double?

        // ❌ 짧은 타입도 var 사용
        var x = 10;  // int를 쓰는 게 더 명확
        var y = 20;
        var sum = x + y;
    }

    static Object getData() {
        return new HashMap<String, String>();
    }

    static Object process() {
        return Arrays.asList(1, 2, 3);
    }

    static Object calculate() {
        return 42;
    }
}
```

#### 왜 문제인가?

```
1. 타입이 불명확하면 코드 이해 어려움
2. IDE 없이는 타입을 알 수 없음
3. 코드 리뷰가 어려워짐
4. 유지보수성 저하
```

#### ✅ 올바른 해결책

```java
package var.mistakes;

import java.util.*;

public class Mistake1_Solution {
    public static void main(String[] args) {
        System.out.println("=== var 적절한 사용 ===\n");

        // ✅ 타입이 명확한 경우만 var 사용
        var customerList = new ArrayList<Customer>();  // 명확
        var orderMap = new HashMap<String, Order>();  // 명확

        // ✅ 타입이 불명확하면 명시적 선언
        Map<String, String> data = getData();  // 명시적
        List<Integer> result = process();  // 명시적
        int value = calculate();  // 명시적

        // ✅ 변수명으로 타입 유추 가능하게
        var totalPrice = 10000;  // 가격임을 알 수 있음
        var itemCount = 5;  // 개수임을 알 수 있음
        var isActive = true;  // boolean임을 알 수 있음

        System.out.println("💡 가이드라인:");
        System.out.println("1. 타입이 명확한 경우만 var 사용");
        System.out.println("2. 변수명으로 의미를 명확히");
        System.out.println("3. 우변이 불명확하면 명시적 타입");
    }

    static Map<String, String> getData() {
        return new HashMap<>();
    }

    static List<Integer> process() {
        return Arrays.asList(1, 2, 3);
    }

    static int calculate() {
        return 42;
    }

    static class Customer { }
    static class Order { }
}
```

---

### ❌ 실수 2: 다이아몬드 연산자만 사용

#### 문제 코드

```java
package var.mistakes;

import java.util.*;

public class Mistake2_DiamondOperator {
    public static void main(String[] args) {
        // ❌ 컴파일 에러: 타입을 추론할 수 없음
        // var list = new ArrayList<>();

        // ❌ Object로 추론됨
        // var map = new HashMap<>();
    }
}
```

#### 왜 문제인가?

```
var는 우변의 타입을 추론함
다이아몬드만 사용하면 제네릭 타입을 알 수 없음
→ 컴파일 에러 또는 Object로 추론
```

#### ✅ 올바른 해결책

```java
package var.mistakes;

import java.util.*;

public class Mistake2_Solution {
    public static void main(String[] args) {
        System.out.println("=== 다이아몬드 연산자 올바른 사용 ===\n");

        // ❌ 잘못된 사용
        // var list1 = new ArrayList<>();  // 컴파일 에러

        // ✅ 올바른 사용 1: 제네릭 타입 명시
        var list2 = new ArrayList<String>();
        list2.add("Hello");

        // ✅ 올바른 사용 2: 명시적 타입 선언
        List<String> list3 = new ArrayList<>();

        // ✅ 올바른 사용 3: 타입이 명확한 경우
        var list4 = List.of("A", "B", "C");  // List<String>으로 추론

        System.out.println("list2: " + list2);
        System.out.println("list3: " + list3);
        System.out.println("list4: " + list4);
        System.out.println();

        System.out.println("💡 핵심:");
        System.out.println("var + 다이아몬드는 제네릭 타입 명시 필요");
    }
}
```

---

### ❌ 실수 3: 인터페이스 타입 대신 구현 클래스 노출

#### 문제 코드

```java
package var.mistakes;

import java.util.*;

public class Mistake3_ConcreteType {
    public static void main(String[] args) {
        // ❌ ArrayList로 추론됨 (구현체 노출)
        var list = new ArrayList<String>();

        // ArrayList 특화 메서드 사용 가능
        list.ensureCapacity(100);

        // 나중에 LinkedList로 변경하면?
        // var list = new LinkedList<String>();
        // list.ensureCapacity(100);  // 컴파일 에러!
    }
}
```

#### 왜 문제인가?

```
1. var는 구현 클래스 타입으로 추론
2. 구현체에 의존하는 코드 작성 가능
3. 나중에 구현체 변경 시 문제 발생
4. 인터페이스 프로그래밍 원칙 위배
```

#### ✅ 올바른 해결책

```java
package var.mistakes;

import java.util.*;

public class Mistake3_Solution {
    public static void main(String[] args) {
        System.out.println("=== 인터페이스 타입 사용 ===\n");

        // ✅ 방법 1: 인터페이스 타입이 필요하면 명시적 선언
        List<String> list1 = new ArrayList<>();

        // 구현체를 쉽게 변경 가능
        // List<String> list1 = new LinkedList<>();

        // ✅ 방법 2: 구현체가 명확하고 변경 없을 경우 var 사용
        var arrayList = new ArrayList<String>();  // ArrayList 사용이 확실

        // ✅ 방법 3: 팩토리 메서드 사용
        var list2 = List.of("A", "B", "C");  // 불변 List 반환

        System.out.println("list1: " + list1.getClass().getSimpleName());
        System.out.println("arrayList: " + arrayList.getClass().getSimpleName());
        System.out.println("list2: " + list2.getClass().getSimpleName());
        System.out.println();

        System.out.println("💡 가이드라인:");
        System.out.println("1. 인터페이스 타입 필요: 명시적 선언");
        System.out.println("2. 구현체 명확: var 사용 가능");
        System.out.println("3. 팩토리 메서드: var 사용 적합");
    }
}
```

---

### ❌ 실수 4: null 초기화 시도

#### 문제 코드

```java
package var.mistakes;

public class Mistake4_NullInitialization {
    public static void main(String[] args) {
        // ❌ 컴파일 에러: 타입을 추론할 수 없음
        // var name = null;

        // ❌ null을 반환하는 메서드도 문제
        // var result = getNullValue();
    }

    static String getNullValue() {
        return null;
    }
}
```

#### 왜 문제인가?

```
var는 우변의 타입을 추론함
null은 타입 정보가 없음
→ 컴파일 에러
```

#### ✅ 올바른 해결책

```java
package var.mistakes;

import java.util.Optional;

public class Mistake4_Solution {
    public static void main(String[] args) {
        System.out.println("=== null 처리 올바른 방법 ===\n");

        // ✅ 방법 1: 명시적 타입 선언
        String name1 = null;

        // ✅ 방법 2: Optional 사용 (권장)
        var optionalName = Optional.ofNullable(getName());
        optionalName.ifPresent(name -> System.out.println("Name: " + name));

        // ✅ 방법 3: 기본값 제공
        var name2 = getName() != null ? getName() : "Unknown";

        // ✅ 방법 4: 메서드 반환 타입이 명확하면 var 사용
        var result = getResult();  // String 타입으로 추론 (null일 수 있음)

        System.out.println("name2: " + name2);
        System.out.println("result: " + result);
        System.out.println();

        System.out.println("💡 핵심:");
        System.out.println("1. null 직접 대입 불가");
        System.out.println("2. Optional 사용 권장");
        System.out.println("3. 기본값 제공 고려");
    }

    static String getName() {
        return Math.random() > 0.5 ? "김철수" : null;
    }

    static String getResult() {
        return "result";
    }
}
```

---

## 🎓 Part 2 종합 정리

### 📊 var 사용 가이드라인

| 상황 | var 사용 | 명시적 타입 |
|------|---------|-----------|
| 복잡한 제네릭 타입 | ✅ 권장 | 가능 |
| Stream 결과 | ✅ 권장 | 가능 |
| 인터페이스 타입 필요 | ❌ 비권장 | ✅ 권장 |
| 타입이 불명확 | ❌ 비권장 | ✅ 권장 |
| 짧은 타입 (int, String) | 선택 | 선택 |

---

### 🚨 주니어 개발자 실수 요약

```
1. ❌ var 무분별 사용
   ✅ 타입이 명확한 경우만

2. ❌ 다이아몬드만 사용
   ✅ 제네릭 타입 명시 필요

3. ❌ 구현 클래스 노출
   ✅ 인터페이스 타입 필요 시 명시적 선언

4. ❌ null 초기화
   ✅ 명시적 타입 또는 Optional
```

**다음 Part 3에서는**: 성능 분석, 바이트코드 비교, 고급 활용 기법, 면접 질문을 다룹니다.
