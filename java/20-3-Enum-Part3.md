# 20-3. Enum (열거형) Part 3: 실전 프로젝트, FAQ, 면접 질문

## 🚀 실전 프로젝트: 주문 관리 시스템

이번 프로젝트에서는 Enum을 활용하여 **이커머스 주문 관리 시스템**을 구축하겠습니다. 주문 상태, 결제 방법, 배송 타입 등 다양한 Enum을 조합하여 실무에서 자주 사용되는 패턴을 구현합니다.

### 📋 프로젝트 요구사항

1. **주문 상태 관리**
   - 상태 전이 검증
   - 각 상태별 허용 동작

2. **결제 방법 다양화**
   - 카드, 현금, 페이, 포인트 등
   - 결제 수단별 수수료 계산

3. **배송 타입**
   - 일반 배송, 빠른 배송, 새벽 배송
   - 타입별 배송비 및 예상 시간

4. **할인 타입**
   - 정률, 정액, 쿠폰 등
   - 할인 조합 규칙

5. **통계 및 리포트**
   - 상태별, 결제별 통계
   - 매출 분석

### 💻 프로젝트 구현

```java
import java.time.*;
import java.util.*;
import java.util.stream.Collectors;

/**
 * ============================================
 * 1단계: 핵심 Enum 정의
 * ============================================
 */

/**
 * 주문 상태 Enum
 */
enum OrderStatus {
    PENDING("주문 접수", "주문이 접수되었습니다.") {
        @Override
        public Set<OrderStatus> getAllowedTransitions() {
            return EnumSet.of(CONFIRMED, CANCELLED);
        }

        @Override
        public boolean canCancel() {
            return true;
        }
    },

    CONFIRMED("주문 확인", "주문이 확인되었습니다.") {
        @Override
        public Set<OrderStatus> getAllowedTransitions() {
            return EnumSet.of(PROCESSING, CANCELLED);
        }

        @Override
        public boolean canCancel() {
            return true;
        }
    },

    PROCESSING("처리 중", "주문을 처리하고 있습니다.") {
        @Override
        public Set<OrderStatus> getAllowedTransitions() {
            return EnumSet.of(SHIPPED, CANCELLED);
        }

        @Override
        public boolean canCancel() {
            return true;
        }
    },

    SHIPPED("배송 중", "상품이 배송 중입니다.") {
        @Override
        public Set<OrderStatus> getAllowedTransitions() {
            return EnumSet.of(DELIVERED);
        }

        @Override
        public boolean canCancel() {
            return false;
        }
    },

    DELIVERED("배송 완료", "배송이 완료되었습니다.") {
        @Override
        public Set<OrderStatus> getAllowedTransitions() {
            return EnumSet.of(RETURNED);
        }

        @Override
        public boolean canReturn() {
            return true;
        }
    },

    CANCELLED("취소", "주문이 취소되었습니다.") {
        @Override
        public Set<OrderStatus> getAllowedTransitions() {
            return EnumSet.noneOf(OrderStatus.class);
        }

        @Override
        public boolean isFinalState() {
            return true;
        }
    },

    RETURNED("반품", "주문이 반품되었습니다.") {
        @Override
        public Set<OrderStatus> getAllowedTransitions() {
            return EnumSet.noneOf(OrderStatus.class);
        }

        @Override
        public boolean isFinalState() {
            return true;
        }
    };

    private final String displayName;
    private final String message;

    OrderStatus(String displayName, String message) {
        this.displayName = displayName;
        this.message = message;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getMessage() {
        return message;
    }

    public abstract Set<OrderStatus> getAllowedTransitions();

    public boolean canTransitionTo(OrderStatus newStatus) {
        return getAllowedTransitions().contains(newStatus);
    }

    public boolean canCancel() {
        return false;
    }

    public boolean canReturn() {
        return false;
    }

    public boolean isFinalState() {
        return false;
    }
}

/**
 * 결제 방법 Enum
 */
enum PaymentMethod {
    CREDIT_CARD("신용카드", 0.0, true, 1000000),
    DEBIT_CARD("체크카드", 0.0, true, 500000),
    BANK_TRANSFER("계좌이체", 0.0, false, Integer.MAX_VALUE),
    KAKAO_PAY("카카오페이", 0.015, true, 2000000),
    NAVER_PAY("네이버페이", 0.018, true, 2000000),
    TOSS_PAY("토스페이", 0.012, true, 1500000),
    CASH("현금", 0.0, false, 1000000),
    POINT("포인트", 0.0, true, 100000);

    private final String displayName;
    private final double feeRate;          // 수수료율
    private final boolean supportsInstallment; // 할부 지원
    private final int maxAmount;           // 최대 결제 금액

    PaymentMethod(String displayName, double feeRate, boolean supportsInstallment, int maxAmount) {
        this.displayName = displayName;
        this.feeRate = feeRate;
        this.supportsInstallment = supportsInstallment;
        this.maxAmount = maxAmount;
    }

    public String getDisplayName() {
        return displayName;
    }

    public double getFeeRate() {
        return feeRate;
    }

    public boolean supportsInstallment() {
        return supportsInstallment;
    }

    public int getMaxAmount() {
        return maxAmount;
    }

    public int calculateFee(int amount) {
        return (int) (amount * feeRate);
    }

    public boolean canPay(int amount) {
        return amount <= maxAmount;
    }
}

/**
 * 배송 타입 Enum
 */
enum DeliveryType {
    STANDARD("일반 배송", 3000, 3, "3일 이내 배송"),
    FAST("빠른 배송", 5000, 1, "익일 배송"),
    DAWN("새벽 배송", 7000, 0, "당일 새벽 배송"),
    PICKUP("매장 픽업", 0, 0, "매장에서 직접 수령");

    private final String displayName;
    private final int fee;                 // 배송비
    private final int estimatedDays;       // 예상 소요일
    private final String description;

    DeliveryType(String displayName, int fee, int estimatedDays, String description) {
        this.displayName = displayName;
        this.fee = fee;
        this.estimatedDays = estimatedDays;
        this.description = description;
    }

    public String getDisplayName() {
        return displayName;
    }

    public int getFee() {
        return fee;
    }

    public int getEstimatedDays() {
        return estimatedDays;
    }

    public String getDescription() {
        return description;
    }

    public LocalDateTime getEstimatedDeliveryDate() {
        return LocalDateTime.now().plusDays(estimatedDays);
    }

    public boolean isFreeDelivery() {
        return fee == 0;
    }
}

/**
 * 할인 타입 Enum
 */
enum DiscountType {
    PERCENTAGE("정률 할인") {
        @Override
        public int calculate(int amount, int value) {
            return amount * value / 100;
        }
    },
    FIXED("정액 할인") {
        @Override
        public int calculate(int amount, int value) {
            return Math.min(value, amount);
        }
    },
    COUPON("쿠폰 할인") {
        @Override
        public int calculate(int amount, int value) {
            return Math.min(value, amount);
        }
    };

    private final String displayName;

    DiscountType(String displayName) {
        this.displayName = displayName;
    }

    public String getDisplayName() {
        return displayName;
    }

    public abstract int calculate(int amount, int value);
}

/**
 * ============================================
 * 2단계: 도메인 모델
 * ============================================
 */

/**
 * 주문 항목
 */
class OrderItem {
    private String productName;
    private int quantity;
    private int unitPrice;

    public OrderItem(String productName, int quantity, int unitPrice) {
        this.productName = productName;
        this.quantity = quantity;
        this.unitPrice = unitPrice;
    }

    public int getTotalPrice() {
        return quantity * unitPrice;
    }

    public String getProductName() {
        return productName;
    }

    public int getQuantity() {
        return quantity;
    }

    public int getUnitPrice() {
        return unitPrice;
    }
}

/**
 * 할인 정보
 */
class Discount {
    private DiscountType type;
    private int value;
    private String description;

    public Discount(DiscountType type, int value, String description) {
        this.type = type;
        this.value = value;
        this.description = description;
    }

    public int apply(int amount) {
        return type.calculate(amount, value);
    }

    public DiscountType getType() {
        return type;
    }

    public String getDescription() {
        return description;
    }
}

/**
 * 주문
 */
class Order {
    private String orderId;
    private String customerId;
    private List<OrderItem> items;
    private OrderStatus status;
    private PaymentMethod paymentMethod;
    private DeliveryType deliveryType;
    private List<Discount> discounts;
    private LocalDateTime createdAt;
    private List<StatusHistory> statusHistory;

    public Order(String orderId, String customerId) {
        this.orderId = orderId;
        this.customerId = customerId;
        this.items = new ArrayList<>();
        this.status = OrderStatus.PENDING;
        this.discounts = new ArrayList<>();
        this.createdAt = LocalDateTime.now();
        this.statusHistory = new ArrayList<>();
        addStatusHistory(null, OrderStatus.PENDING, "주문 생성");
    }

    public void addItem(OrderItem item) {
        items.add(item);
    }

    public void setPaymentMethod(PaymentMethod method) {
        this.paymentMethod = method;
    }

    public void setDeliveryType(DeliveryType type) {
        this.deliveryType = type;
    }

    public void addDiscount(Discount discount) {
        discounts.add(discount);
    }

    public boolean transitionTo(OrderStatus newStatus, String reason) {
        if (!status.canTransitionTo(newStatus)) {
            System.out.println("❌ 상태 전이 불가: " + status.getDisplayName() +
                             " → " + newStatus.getDisplayName());
            return false;
        }

        OrderStatus oldStatus = status;
        status = newStatus;
        addStatusHistory(oldStatus, newStatus, reason);

        System.out.println("✅ 상태 변경: " + oldStatus.getDisplayName() +
                         " → " + newStatus.getDisplayName());
        return true;
    }

    private void addStatusHistory(OrderStatus from, OrderStatus to, String reason) {
        statusHistory.add(new StatusHistory(from, to, reason, LocalDateTime.now()));
    }

    public boolean cancel(String reason) {
        if (!status.canCancel()) {
            System.out.println("❌ 현재 상태에서는 취소할 수 없습니다: " + status.getDisplayName());
            return false;
        }
        return transitionTo(OrderStatus.CANCELLED, reason);
    }

    public int getItemsTotal() {
        return items.stream()
            .mapToInt(OrderItem::getTotalPrice)
            .sum();
    }

    public int getDiscountAmount() {
        int itemsTotal = getItemsTotal();
        return discounts.stream()
            .mapToInt(d -> d.apply(itemsTotal))
            .sum();
    }

    public int getDeliveryFee() {
        return deliveryType != null ? deliveryType.getFee() : 0;
    }

    public int getPaymentFee() {
        if (paymentMethod == null) return 0;
        int amount = getItemsTotal() - getDiscountAmount() + getDeliveryFee();
        return paymentMethod.calculateFee(amount);
    }

    public int getFinalAmount() {
        return getItemsTotal() - getDiscountAmount() + getDeliveryFee() + getPaymentFee();
    }

    public void printOrderSummary() {
        System.out.println("\n" + "=".repeat(60));
        System.out.println("주문 요약 - " + orderId);
        System.out.println("=".repeat(60));

        System.out.println("고객 ID: " + customerId);
        System.out.println("주문 시간: " + createdAt);
        System.out.println("현재 상태: " + status.getDisplayName());

        System.out.println("\n[주문 항목]");
        for (OrderItem item : items) {
            System.out.println(String.format("  %s x %d = %,d원",
                item.getProductName(), item.getQuantity(), item.getTotalPrice()));
        }

        System.out.println("\n[금액 계산]");
        System.out.println("  상품 금액: " + String.format("%,d원", getItemsTotal()));

        if (!discounts.isEmpty()) {
            System.out.println("  할인:");
            for (Discount discount : discounts) {
                int discountAmount = discount.apply(getItemsTotal());
                System.out.println(String.format("    - %s: -%,d원",
                    discount.getDescription(), discountAmount));
            }
        }

        if (deliveryType != null) {
            System.out.println("  배송비 (" + deliveryType.getDisplayName() + "): " +
                             String.format("%,d원", getDeliveryFee()));
        }

        if (paymentMethod != null && getPaymentFee() > 0) {
            System.out.println("  결제 수수료 (" + paymentMethod.getDisplayName() + "): " +
                             String.format("%,d원", getPaymentFee()));
        }

        System.out.println("\n  최종 결제 금액: " + String.format("%,d원", getFinalAmount()));

        if (paymentMethod != null) {
            System.out.println("\n[결제 정보]");
            System.out.println("  결제 수단: " + paymentMethod.getDisplayName());
            System.out.println("  할부 지원: " + (paymentMethod.supportsInstallment() ? "가능" : "불가능"));
        }

        if (deliveryType != null) {
            System.out.println("\n[배송 정보]");
            System.out.println("  배송 타입: " + deliveryType.getDisplayName());
            System.out.println("  배송 설명: " + deliveryType.getDescription());
            System.out.println("  예상 배송일: " + deliveryType.getEstimatedDeliveryDate());
        }
    }

    public void printStatusHistory() {
        System.out.println("\n[상태 변경 이력]");
        for (int i = 0; i < statusHistory.size(); i++) {
            StatusHistory history = statusHistory.get(i);
            System.out.println((i + 1) + ". " + history);
        }
    }

    // Getters
    public String getOrderId() { return orderId; }
    public OrderStatus getStatus() { return status; }
    public PaymentMethod getPaymentMethod() { return paymentMethod; }
    public DeliveryType getDeliveryType() { return deliveryType; }
}

/**
 * 상태 변경 이력
 */
class StatusHistory {
    private OrderStatus from;
    private OrderStatus to;
    private String reason;
    private LocalDateTime timestamp;

    public StatusHistory(OrderStatus from, OrderStatus to, String reason, LocalDateTime timestamp) {
        this.from = from;
        this.to = to;
        this.reason = reason;
        this.timestamp = timestamp;
    }

    @Override
    public String toString() {
        String fromStr = from == null ? "없음" : from.getDisplayName();
        return String.format("%s - %s → %s (%s)",
            timestamp.toLocalTime(), fromStr, to.getDisplayName(), reason);
    }
}

/**
 * ============================================
 * 3단계: 주문 관리 서비스
 * ============================================
 */

class OrderService {
    private Map<String, Order> orders = new HashMap<>();
    private int orderCounter = 1;

    public Order createOrder(String customerId) {
        String orderId = String.format("ORD-%05d", orderCounter++);
        Order order = new Order(orderId, customerId);
        orders.put(orderId, order);

        System.out.println("✅ 주문 생성: " + orderId);
        return order;
    }

    public Order getOrder(String orderId) {
        return orders.get(orderId);
    }

    public List<Order> getOrdersByStatus(OrderStatus status) {
        return orders.values().stream()
            .filter(o -> o.getStatus() == status)
            .collect(Collectors.toList());
    }

    public Map<OrderStatus, Long> getOrderCountByStatus() {
        return orders.values().stream()
            .collect(Collectors.groupingBy(Order::getStatus, Collectors.counting()));
    }

    public Map<PaymentMethod, Long> getOrderCountByPaymentMethod() {
        return orders.values().stream()
            .filter(o -> o.getPaymentMethod() != null)
            .collect(Collectors.groupingBy(Order::getPaymentMethod, Collectors.counting()));
    }

    public int getTotalRevenue() {
        return orders.values().stream()
            .filter(o -> o.getStatus() == OrderStatus.DELIVERED)
            .mapToInt(Order::getFinalAmount)
            .sum();
    }

    public void printStatistics() {
        System.out.println("\n" + "=".repeat(60));
        System.out.println("주문 통계");
        System.out.println("=".repeat(60));

        System.out.println("\n[상태별 주문 수]");
        Map<OrderStatus, Long> statusCount = getOrderCountByStatus();
        for (OrderStatus status : OrderStatus.values()) {
            long count = statusCount.getOrDefault(status, 0L);
            if (count > 0) {
                System.out.println("  " + status.getDisplayName() + ": " + count + "건");
            }
        }

        System.out.println("\n[결제 수단별 주문 수]");
        Map<PaymentMethod, Long> paymentCount = getOrderCountByPaymentMethod();
        paymentCount.forEach((method, count) ->
            System.out.println("  " + method.getDisplayName() + ": " + count + "건")
        );

        System.out.println("\n[매출 정보]");
        System.out.println("  총 주문 수: " + orders.size() + "건");
        System.out.println("  완료된 주문: " + getOrdersByStatus(OrderStatus.DELIVERED).size() + "건");
        System.out.println("  총 매출: " + String.format("%,d원", getTotalRevenue()));
    }
}

/**
 * ============================================
 * 4단계: 테스트 및 실행
 * ============================================
 */

public class OrderManagementSystemTest {

    public static void main(String[] args) {

        System.out.println("╔════════════════════════════════════════════════════════╗");
        System.out.println("║         주문 관리 시스템 - 실전 프로젝트              ║");
        System.out.println("╚════════════════════════════════════════════════════════╝");

        OrderService service = new OrderService();

        // 테스트 시나리오
        test1_NormalOrder(service);
        test2_CancelledOrder(service);
        test3_VariousPaymentMethods(service);
        test4_DeliveryTypes(service);
        test5_Discounts(service);

        // 통계 출력
        service.printStatistics();
    }

    static void test1_NormalOrder(OrderService service) {
        System.out.println("\n\n### 테스트 1: 정상 주문 ###");

        Order order = service.createOrder("CUST-001");
        order.addItem(new OrderItem("노트북", 1, 1500000));
        order.addItem(new OrderItem("마우스", 2, 30000));
        order.setPaymentMethod(PaymentMethod.CREDIT_CARD);
        order.setDeliveryType(DeliveryType.STANDARD);

        order.printOrderSummary();

        // 주문 진행
        order.transitionTo(OrderStatus.CONFIRMED, "결제 완료");
        order.transitionTo(OrderStatus.PROCESSING, "상품 준비");
        order.transitionTo(OrderStatus.SHIPPED, "배송 시작");
        order.transitionTo(OrderStatus.DELIVERED, "배송 완료");

        order.printStatusHistory();
    }

    static void test2_CancelledOrder(OrderService service) {
        System.out.println("\n\n### 테스트 2: 주문 취소 ###");

        Order order = service.createOrder("CUST-002");
        order.addItem(new OrderItem("키보드", 1, 80000));
        order.setPaymentMethod(PaymentMethod.KAKAO_PAY);
        order.setDeliveryType(DeliveryType.FAST);

        order.transitionTo(OrderStatus.CONFIRMED, "결제 완료");
        order.cancel("고객 요청");

        order.printOrderSummary();
        order.printStatusHistory();
    }

    static void test3_VariousPaymentMethods(OrderService service) {
        System.out.println("\n\n### 테스트 3: 다양한 결제 수단 ###");

        PaymentMethod[] methods = {
            PaymentMethod.NAVER_PAY,
            PaymentMethod.TOSS_PAY,
            PaymentMethod.BANK_TRANSFER
        };

        for (PaymentMethod method : methods) {
            Order order = service.createOrder("CUST-003");
            order.addItem(new OrderItem("모니터", 1, 300000));
            order.setPaymentMethod(method);
            order.setDeliveryType(DeliveryType.STANDARD);
            order.transitionTo(OrderStatus.CONFIRMED, "결제 완료");
            order.transitionTo(OrderStatus.PROCESSING, "처리 중");
            order.transitionTo(OrderStatus.SHIPPED, "배송 중");
            order.transitionTo(OrderStatus.DELIVERED, "배송 완료");

            System.out.println("\n" + method.getDisplayName() + " 주문:");
            System.out.println("  결제 금액: " + String.format("%,d원", order.getFinalAmount()));
            System.out.println("  결제 수수료: " + String.format("%,d원", order.getPaymentFee()));
        }
    }

    static void test4_DeliveryTypes(OrderService service) {
        System.out.println("\n\n### 테스트 4: 배송 타입 ###");

        for (DeliveryType type : DeliveryType.values()) {
            Order order = service.createOrder("CUST-004");
            order.addItem(new OrderItem("책", 3, 15000));
            order.setPaymentMethod(PaymentMethod.CREDIT_CARD);
            order.setDeliveryType(type);

            System.out.println("\n" + type.getDisplayName() + ":");
            System.out.println("  배송비: " + String.format("%,d원", type.getFee()));
            System.out.println("  예상 소요일: " + type.getEstimatedDays() + "일");
            System.out.println("  예상 도착: " + type.getEstimatedDeliveryDate());
        }
    }

    static void test5_Discounts(OrderService service) {
        System.out.println("\n\n### 테스트 5: 할인 적용 ###");

        Order order = service.createOrder("CUST-005");
        order.addItem(new OrderItem("스마트폰", 1, 1000000));
        order.setPaymentMethod(PaymentMethod.CREDIT_CARD);
        order.setDeliveryType(DeliveryType.STANDARD);

        // 다양한 할인 적용
        order.addDiscount(new Discount(DiscountType.PERCENTAGE, 10, "10% 할인"));
        order.addDiscount(new Discount(DiscountType.FIXED, 50000, "추가 5만원 할인"));
        order.addDiscount(new Discount(DiscountType.COUPON, 20000, "쿠폰 할인"));

        order.printOrderSummary();
    }
}
```

### 🎯 프로젝트 학습 포인트

1. **Enum 상태 머신**
   - `getAllowedTransitions()`로 명확한 전이 규칙
   - 잘못된 상태 전이 방지

2. **Enum 비즈니스 로직**
   - `calculateFee()`: 수수료 계산
   - `getEstimatedDeliveryDate()`: 배송일 계산
   - 각 Enum이 자신의 로직을 캡슐화

3. **추상 메서드 활용**
   - `DiscountType.calculate()`: 할인 타입별 다른 계산
   - 다형성을 통한 유연한 설계

4. **EnumSet 활용**
   - 허용된 상태 전이를 효율적으로 관리
   - 비트 연산으로 빠른 성능

5. **실무 패턴**
   - 상태 이력 추적
   - 통계 및 리포트
   - 검증 로직

---

## ❓ FAQ (자주 묻는 질문)

### Q1. Enum에 생성자를 왜 만들 수 없나요? (private만 가능)

**A:** Enum은 **컴파일 타임에 모든 인스턴스가 생성**되므로, 런타임에 새로운 인스턴스를 만들 수 없습니다.

```java
enum Day {
    MONDAY, TUESDAY, WEDNESDAY;

    // ✅ private 생성자 (기본)
    private Day() {
        System.out.println("Creating: " + this.name());
    }

    // ❌ public 생성자는 컴파일 에러!
    // public Day() { }
}

// Enum 상수들은 클래스 로딩 시 자동으로 생성됨
// new Day()와 같은 코드는 불가능
```

**왜 private만 가능한가?**
- Enum은 고정된 상수 집합
- 런타임에 새 인스턴스 생성을 막아야 함
- 싱글톤 패턴 보장

---

### Q2. Enum은 상속이 가능한가요?

**A:** **불가능**합니다. 모든 Enum은 자동으로 `java.lang.Enum`을 상속하며, Java는 다중 상속을 지원하지 않습니다.

```java
// ❌ 컴파일 에러! Enum은 다른 클래스를 상속할 수 없음
// enum MyEnum extends SomeClass {
// }

// ❌ 컴파일 에러! Enum을 상속할 수 없음
// class MyClass extends MyEnum {
// }

// ✅ 인터페이스는 구현 가능
interface Describable {
    String getDescription();
}

enum Status implements Describable {
    ACTIVE("활성"),
    INACTIVE("비활성");

    private String description;

    Status(String description) {
        this.description = description;
    }

    @Override
    public String getDescription() {
        return description;
    }
}
```

**대신 할 수 있는 것:**
- ✅ 인터페이스 구현
- ✅ 추상 메서드로 각 상수가 다르게 구현

---

### Q3. Enum에 메서드를 추가하는 것이 좋은 설계인가요?

**A:** **상황에 따라 다릅니다.** 비즈니스 로직이 Enum과 밀접하게 관련되어 있다면 좋은 설계입니다.

**좋은 예: Enum에 메서드 추가**
```java
enum Season {
    SPRING(15.0),
    SUMMER(28.0),
    AUTUMN(18.0),
    WINTER(0.0);

    private double avgTemperature;

    Season(double avgTemperature) {
        this.avgTemperature = avgTemperature;
    }

    // ✅ 좋음: Season과 밀접한 로직
    public String getClothingAdvice() {
        if (avgTemperature < 10) return "두꺼운 외투";
        if (avgTemperature < 20) return "가벼운 자켓";
        return "반팔";
    }

    public boolean isHot() {
        return avgTemperature > 25;
    }
}
```

**나쁜 예: 관련 없는 로직**
```java
enum Status {
    ACTIVE, INACTIVE;

    // ❌ 나쁨: Status와 무관한 로직
    public void sendEmail(String to, String message) {
        // 이메일 전송은 Status의 책임이 아님
    }

    public void saveToDatabase() {
        // DB 저장도 Status의 책임이 아님
    }
}
```

**가이드라인:**
- ✅ Enum 상수와 직접 관련된 속성/동작
- ✅ 각 상수별로 다른 동작이 필요한 경우
- ❌ Enum과 무관한 비즈니스 로직
- ❌ 외부 의존성이 필요한 복잡한 로직

---

### Q4. EnumSet과 EnumMap은 언제 사용하나요?

**A:** Enum을 집합이나 맵의 키로 사용할 때 **성능 최적화**를 위해 사용합니다.

**EnumSet 예제:**
```java
enum Permission {
    READ, WRITE, DELETE, ADMIN
}

class User {
    private EnumSet<Permission> permissions;

    public User() {
        // ✅ EnumSet: 내부적으로 비트 벡터 사용 (빠름)
        permissions = EnumSet.noneOf(Permission.class);
    }

    public void grantPermission(Permission permission) {
        permissions.add(permission);
    }

    public boolean hasPermission(Permission permission) {
        return permissions.contains(permission);  // O(1) 시간
    }

    public void grantAllPermissions() {
        permissions = EnumSet.allOf(Permission.class);
    }

    public void grantReadWrite() {
        permissions = EnumSet.of(Permission.READ, Permission.WRITE);
    }
}

// 비교
Set<Permission> normalSet = new HashSet<>();  // ⚠️  느림
EnumSet<Permission> enumSet = EnumSet.noneOf(Permission.class);  // ✅ 빠름
```

**EnumMap 예제:**
```java
enum Day {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
}

class Schedule {
    // ✅ EnumMap: 배열 기반으로 빠름
    private EnumMap<Day, String> schedule;

    public Schedule() {
        schedule = new EnumMap<>(Day.class);
    }

    public void addTask(Day day, String task) {
        schedule.put(day, task);
    }

    public String getTask(Day day) {
        return schedule.get(day);
    }
}

// 비교
Map<Day, String> normalMap = new HashMap<>();  // ⚠️  느림
EnumMap<Day, String> enumMap = new EnumMap<>(Day.class);  // ✅ 빠름
```

**장점:**
- ⚡ **성능**: 일반 Set/Map보다 훨씬 빠름
- 💾 **메모리**: 더 적은 메모리 사용
- 🔒 **타입 안정성**: Enum만 사용 가능

---

### Q5. Enum으로 싱글톤 패턴을 구현하는 것이 최선인가요?

**A:** **예, Enum 싱글톤은 가장 안전하고 간단한 방법**입니다.

**전통적인 싱글톤 (문제 많음):**
```java
class Singleton {
    private static Singleton instance;

    private Singleton() { }

    public static Singleton getInstance() {
        if (instance == null) {
            instance = new Singleton();  // ⚠️  멀티스레드 문제
        }
        return instance;
    }
}
```

**Enum 싱글톤 (완벽함):**
```java
enum Singleton {
    INSTANCE;

    private int value;

    public void setValue(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }

    public void doSomething() {
        System.out.println("Doing something: " + value);
    }
}

// 사용
Singleton.INSTANCE.setValue(42);
Singleton.INSTANCE.doSomething();
```

**Enum 싱글톤의 장점:**

1. **스레드 안전**: JVM이 보장
2. **직렬화 안전**: 자동으로 처리
3. **리플렉션 공격 방지**: Enum은 리플렉션으로 생성 불가
4. **간결함**: 코드가 매우 짧음

**실무 예제:**
```java
enum DatabaseConnection {
    INSTANCE;

    private Connection connection;

    DatabaseConnection() {
        // 연결 초기화 (한 번만 실행됨)
        System.out.println("DB 연결 초기화");
        // connection = DriverManager.getConnection(...);
    }

    public void executeQuery(String sql) {
        System.out.println("쿼리 실행: " + sql);
    }
}

// 어디서든 동일한 인스턴스
DatabaseConnection.INSTANCE.executeQuery("SELECT * FROM users");
```

**언제 사용하지 말아야 하나?**
- 싱글톤이 인터페이스를 구현해야 하는 경우
- 싱글톤을 lazy 초기화해야 하는 경우
- 싱글톤에 생성자 파라미터가 필요한 경우

---

### Q6. switch 문에서 Enum을 사용할 때 default가 필요한가요?

**A:** **가능하면 default를 피하세요.** 모든 Enum 케이스를 명시적으로 처리하는 것이 좋습니다.

**나쁜 예 (default 사용):**
```java
enum Status {
    ACTIVE, INACTIVE, PENDING
}

void handleStatus(Status status) {
    switch (status) {
        case ACTIVE:
            System.out.println("활성");
            break;
        case INACTIVE:
            System.out.println("비활성");
            break;
        default:  // ❌ 나쁨: 새 상수 추가 시 놓칠 수 있음
            System.out.println("기타");
            break;
    }
}

// 나중에 Status에 SUSPENDED 추가
// → default로 처리되어 버그 발견 어려움
```

**좋은 예 (모든 케이스 명시):**
```java
void handleStatus(Status status) {
    switch (status) {
        case ACTIVE:
            System.out.println("활성");
            break;
        case INACTIVE:
            System.out.println("비활성");
            break;
        case PENDING:
            System.out.println("대기");
            break;
        // default 없음
        // → 새 상수 추가 시 컴파일 경고
    }
}

// Status에 SUSPENDED 추가
// → 컴파일러가 경고: "switch 문이 모든 케이스를 처리하지 않음"
```

**Java 14+ Enhanced Switch (더 좋음):**
```java
String message = switch (status) {
    case ACTIVE -> "활성";
    case INACTIVE -> "비활성";
    case PENDING -> "대기";
    // 모든 케이스를 처리하지 않으면 컴파일 에러!
};
```

**default가 필요한 경우:**
- 일부 케이스만 특별 처리하고 나머지는 동일한 경우
- 예상치 못한 값 처리 (외부 입력 등)

---

### Q7. Enum의 values()와 valueOf()의 성능은 어떤가요?

**A:**

**values():**
- 호출할 때마다 **새 배열을 생성**하여 반환
- ⚠️  반복 호출 시 성능 저하

```java
// ❌ 나쁨: 매번 새 배열 생성
for (int i = 0; i < 1000; i++) {
    for (Status status : Status.values()) {  // 1000번 배열 생성!
        process(status);
    }
}

// ✅ 좋음: 한 번만 생성
Status[] statuses = Status.values();
for (int i = 0; i < 1000; i++) {
    for (Status status : statuses) {  // 배열 재사용
        process(status);
    }
}
```

**valueOf():**
- 내부적으로 HashMap 사용
- O(1) 시간 복잡도
- ✅ 성능 걱정 없음

```java
// ✅ 빠름
Status status = Status.valueOf("ACTIVE");
```

**실무 팁:**
```java
enum Status {
    ACTIVE, INACTIVE;

    // ✅ 정적 캐싱으로 values() 최적화
    private static final Status[] VALUES = values();

    public static Status[] cachedValues() {
        return VALUES.clone();  // 복사본 반환 (안전)
    }
}

// 사용
for (Status status : Status.cachedValues()) {
    // 성능 최적화됨
}
```

---

## 🎤 면접 질문

### 주니어 개발자 면접 질문 (7문제)

#### Q1. Enum이 무엇이고, 언제 사용하나요?

**모범 답변:**

Enum(열거형)은 **서로 관련된 상수들의 집합을 타입으로 정의**하는 특별한 클래스입니다.

**정의:**
```java
enum Day {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
}
```

**언제 사용하나:**

1. **고정된 상수 집합**
   - 요일, 계절, 월 등
   - 컴파일 타임에 모든 값을 알 수 있는 경우

2. **상태 또는 타입**
   - 주문 상태: PENDING, CONFIRMED, SHIPPED
   - 사용자 역할: ADMIN, USER, GUEST

3. **설정 옵션**
   - 로그 레벨: DEBUG, INFO, WARN, ERROR
   - 우선순위: LOW, MEDIUM, HIGH

**장점:**
- ✅ 타입 안정성: 정해진 값만 사용 가능
- ✅ 가독성: 의미 있는 이름
- ✅ 유지보수: 한 곳에서 관리
- ✅ 추가 기능: 메서드와 필드 추가 가능

**예제:**
```java
enum OrderStatus {
    PENDING("대기 중"),
    SHIPPED("배송 중"),
    DELIVERED("배송 완료");

    private String description;

    OrderStatus(String description) {
        this.description = description;
    }

    public String getDescription() {
        return description;
    }
}

// 사용
OrderStatus status = OrderStatus.PENDING;
System.out.println(status.getDescription());  // "대기 중"
```

---

#### Q2. Enum과 상수 클래스(static final)의 차이점은 무엇인가요?

**모범 답변:**

| 구분 | 상수 클래스 | Enum |
|------|-------------|------|
| **타입 안정성** | ❌ 없음 | ✅ 있음 |
| **값 제한** | ❌ 모든 값 가능 | ✅ 정해진 값만 |
| **메서드 추가** | ❌ 불가능 | ✅ 가능 |
| **switch 지원** | ⚠️  가능하지만 위험 | ✅ 완벽 지원 |
| **순회** | ❌ 불가능 | ✅ values() |

**상수 클래스 (구식):**
```java
class Status {
    public static final int ACTIVE = 0;
    public static final int INACTIVE = 1;
}

// ❌ 문제점
int status = 999;  // 잘못된 값 허용
int status = Status.ACTIVE;  // 의미 불명확
```

**Enum (현대적):**
```java
enum Status {
    ACTIVE, INACTIVE
}

// ✅ 장점
Status status = Status.ACTIVE;  // 의미 명확
// Status status = 999;  // 컴파일 에러!

// 모든 값 순회 가능
for (Status s : Status.values()) {
    System.out.println(s);
}
```

---

#### Q3. Enum의 ordinal() 메서드는 무엇이며, 주의할 점은?

**모범 답변:**

`ordinal()`은 Enum 상수의 **선언 순서**(0부터 시작)를 반환합니다.

```java
enum Priority {
    LOW, MEDIUM, HIGH, URGENT
}

Priority.LOW.ordinal();     // 0
Priority.MEDIUM.ordinal();  // 1
Priority.HIGH.ordinal();    // 2
Priority.URGENT.ordinal();  // 3
```

**⚠️  주의사항: ordinal()을 저장하지 마세요!**

**나쁜 예:**
```java
// ❌ ordinal()을 DB에 저장
int code = priority.ordinal();  // 2
saveToDatabase(code);

// 나중에 Enum 순서 변경
// enum Priority {
//     URGENT, HIGH, MEDIUM, LOW  // 순서 바뀜!
// }

// 기존 DB의 2는 HIGH였는데, 이제는 MEDIUM!
```

**좋은 예:**
```java
enum Priority {
    LOW(1), MEDIUM(2), HIGH(3), URGENT(4);

    private final int code;  // ✅ 명시적 코드

    Priority(int code) {
        this.code = code;
    }

    public int getCode() {
        return code;
    }
}

// ✅ 명시적 코드 사용
int code = priority.getCode();  // 순서 변경에 영향 없음
```

**ordinal()의 유일한 용도:**
- EnumSet, EnumMap 내부 구현
- 일반 개발자는 거의 사용하지 않음

---

#### Q4. Enum에 메서드를 추가할 수 있나요? 예제를 보여주세요.

**모범 답변:**

**예, 가능합니다.** Enum은 클래스이므로 필드, 생성자, 메서드를 모두 가질 수 있습니다.

**기본 예제:**
```java
enum Season {
    SPRING("봄", 15.0),
    SUMMER("여름", 28.0),
    AUTUMN("가을", 18.0),
    WINTER("겨울", 0.0);

    private final String koreanName;
    private final double avgTemp;

    // 생성자
    Season(String koreanName, double avgTemp) {
        this.koreanName = koreanName;
        this.avgTemp = avgTemp;
    }

    // 일반 메서드
    public String getKoreanName() {
        return koreanName;
    }

    public boolean isHot() {
        return avgTemp > 25;
    }

    public String getClothingAdvice() {
        if (avgTemp < 10) return "두꺼운 코트";
        if (avgTemp < 20) return "가벼운 자켓";
        return "반팔";
    }
}

// 사용
Season season = Season.SUMMER;
System.out.println(season.getKoreanName());      // "여름"
System.out.println(season.isHot());              // true
System.out.println(season.getClothingAdvice()); // "반팔"
```

**추상 메서드 예제 (각 상수별로 다르게 구현):**
```java
enum Operation {
    PLUS("+") {
        @Override
        public int apply(int a, int b) {
            return a + b;
        }
    },
    MINUS("-") {
        @Override
        public int apply(int a, int b) {
            return a - b;
        }
    },
    MULTIPLY("*") {
        @Override
        public int apply(int a, int b) {
            return a * b;
        }
    };

    private final String symbol;

    Operation(String symbol) {
        this.symbol = symbol;
    }

    public abstract int apply(int a, int b);

    public String getSymbol() {
        return symbol;
    }
}

// 사용
int result = Operation.PLUS.apply(5, 3);  // 8
System.out.println(Operation.MULTIPLY.getSymbol());  // "*"
```

---

#### Q5. Enum을 switch 문에서 어떻게 사용하나요?

**모범 답변:**

Enum은 switch 문과 **완벽하게 호환**됩니다.

**기본 사용법:**
```java
enum Day {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
}

void printDayType(Day day) {
    switch (day) {
        case MONDAY:
        case TUESDAY:
        case WEDNESDAY:
        case THURSDAY:
        case FRIDAY:
            System.out.println("평일");
            break;
        case SATURDAY:
        case SUNDAY:
            System.out.println("주말");
            break;
    }
}
```

**Java 14+ Enhanced Switch (권장):**
```java
String dayType = switch (day) {
    case MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY -> "평일";
    case SATURDAY, SUNDAY -> "주말";
};

// 값 반환도 가능
int workHours = switch (day) {
    case MONDAY, TUESDAY, WEDNESDAY, THURSDAY -> 8;
    case FRIDAY -> 6;
    case SATURDAY, SUNDAY -> 0;
};
```

**실무 예제:**
```java
enum OrderStatus {
    PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
}

String getMessage(OrderStatus status) {
    return switch (status) {
        case PENDING -> "주문 접수 완료";
        case CONFIRMED -> "결제 확인됨";
        case SHIPPED -> "배송 시작";
        case DELIVERED -> "배송 완료";
        case CANCELLED -> "주문 취소됨";
    };
}
```

**주의사항:**
- ✅ 모든 케이스를 처리하는 것이 좋음 (컴파일러 경고 활용)
- ⚠️  default는 가능하면 피하기 (새 상수 추가 시 놓칠 수 있음)

---

#### Q6. Enum의 values()와 valueOf() 메서드는 무엇인가요?

**모범 답변:**

**values()**: 모든 Enum 상수를 배열로 반환
```java
enum Status {
    ACTIVE, INACTIVE, PENDING
}

// 모든 상수 가져오기
Status[] allStatuses = Status.values();

for (Status status : allStatuses) {
    System.out.println(status);
}
// 출력:
// ACTIVE
// INACTIVE
// PENDING
```

**valueOf(String)**: 문자열을 Enum 상수로 변환
```java
// 문자열 → Enum
Status status = Status.valueOf("ACTIVE");
System.out.println(status);  // ACTIVE

// ⚠️  주의: 잘못된 문자열은 예외 발생
try {
    Status invalid = Status.valueOf("INVALID");
} catch (IllegalArgumentException e) {
    System.out.println("존재하지 않는 상수");
}
```

**실무에서 안전하게 사용:**
```java
enum Status {
    ACTIVE, INACTIVE;

    // ✅ 안전한 valueOf
    public static Status fromString(String name) {
        try {
            return valueOf(name.toUpperCase());
        } catch (IllegalArgumentException e) {
            return null;  // 또는 기본값
        }
    }

    // ✅ Optional 반환
    public static Optional<Status> fromStringSafe(String name) {
        try {
            return Optional.of(valueOf(name.toUpperCase()));
        } catch (IllegalArgumentException e) {
            return Optional.empty();
        }
    }
}

// 사용
Status status = Status.fromString("active");  // null 안전
Optional<Status> optStatus = Status.fromStringSafe("active");
```

**성능 고려:**
- `values()`는 호출 시마다 새 배열 생성 → 반복 사용 시 캐싱 권장
- `valueOf()`는 HashMap 기반 → 성능 좋음

---

#### Q7. Enum을 JSON으로 직렬화/역직렬화할 때 주의사항은?

**모범 답변:**

Enum은 기본적으로 **name()**으로 직렬화되지만, 커스터마이징이 가능합니다.

**기본 동작 (Jackson):**
```java
enum Status {
    ACTIVE, INACTIVE, PENDING
}

// 직렬화
Status status = Status.ACTIVE;
// JSON: "ACTIVE"

// 역직렬화
// "ACTIVE" → Status.ACTIVE
```

**문제: 한글 이름 출력하고 싶을 때**
```java
enum Status {
    ACTIVE("활성"),
    INACTIVE("비활성"),
    PENDING("대기");

    private String displayName;

    Status(String displayName) {
        this.displayName = displayName;
    }

    // ✅ @JsonValue: 직렬화 시 이 값 사용
    @JsonValue
    public String getDisplayName() {
        return displayName;
    }

    // ✅ @JsonCreator: 역직렬화 시 사용
    @JsonCreator
    public static Status fromDisplayName(String displayName) {
        for (Status status : values()) {
            if (status.displayName.equals(displayName)) {
                return status;
            }
        }
        throw new IllegalArgumentException("Unknown: " + displayName);
    }
}

// 직렬화: Status.ACTIVE → "활성"
// 역직렬화: "활성" → Status.ACTIVE
```

**ordinal 직렬화 (비추천):**
```java
enum Status {
    ACTIVE, INACTIVE;
}

// ❌ 나쁨: ordinal로 직렬화
// @JsonFormat(shape = JsonFormat.Shape.NUMBER)
// → Status.ACTIVE는 0으로 저장
// → Enum 순서 변경 시 문제!
```

**Best Practice:**
```java
enum Status {
    ACTIVE("ACT", "활성"),
    INACTIVE("INA", "비활성");

    private final String code;  // API/DB용
    private final String displayName;  // 화면용

    Status(String code, String displayName) {
        this.code = code;
        this.displayName = displayName;
    }

    @JsonValue
    public String getCode() {
        return code;  // "ACT", "INA"
    }

    @JsonCreator
    public static Status fromCode(String code) {
        for (Status status : values()) {
            if (status.code.equals(code)) {
                return status;
            }
        }
        throw new IllegalArgumentException("Unknown code: " + code);
    }
}
```

---

### 중급 개발자 면접 질문 (5문제)

#### Q8. Enum은 어떻게 싱글톤을 보장하나요? 내부 구현을 설명하세요.

**모범 답변:**

Enum은 **JVM 레벨에서 싱글톤을 보장**하며, 가장 안전한 싱글톤 구현 방법입니다.

**내부 동작 원리:**

1. **컴파일 시 변환:**
```java
// 개발자가 작성한 코드
enum Singleton {
    INSTANCE;

    public void doSomething() {
        System.out.println("Hello");
    }
}

// 컴파일러가 생성한 코드 (의사 코드)
public final class Singleton extends Enum<Singleton> {
    public static final Singleton INSTANCE = new Singleton();

    private static final Singleton[] VALUES = { INSTANCE };

    private Singleton() {
        super("INSTANCE", 0);
    }

    public static Singleton[] values() {
        return VALUES.clone();
    }

    public static Singleton valueOf(String name) {
        // HashMap 기반 조회
    }

    public void doSomething() {
        System.out.println("Hello");
    }
}
```

2. **클래스 로딩 시 초기화:**
   - JVM이 Singleton 클래스를 처음 로드할 때
   - `static final INSTANCE` 필드 초기화
   - 단 한 번만 실행됨 (JVM 보장)

3. **스레드 안전성:**
   - 클래스 로딩은 JVM의 ClassLoader가 동기화 처리
   - 멀티스레드 환경에서도 안전

**전통적 싱글톤과 비교:**

```java
// ❌ 전통적 싱글톤 (문제 많음)
class TraditionalSingleton {
    private static TraditionalSingleton instance;

    private TraditionalSingleton() { }

    public static TraditionalSingleton getInstance() {
        if (instance == null) {  // ⚠️  스레드 안전하지 않음
            instance = new TraditionalSingleton();
        }
        return instance;
    }
}

// ✅ Enum 싱글톤 (완벽)
enum EnumSingleton {
    INSTANCE;

    // 추가 필드와 메서드
    private int value;

    public void setValue(int value) {
        this.value = value;
    }
}
```

**Enum 싱글톤의 추가 이점:**

1. **직렬화 안전:**
   ```java
   // 일반 클래스는 readResolve() 필요
   class NormalSingleton implements Serializable {
       private static final NormalSingleton INSTANCE = new NormalSingleton();

       private NormalSingleton() { }

       // ⚠️  이것이 없으면 역직렬화 시 새 인스턴스 생성
       private Object readResolve() {
           return INSTANCE;
       }
   }

   // Enum은 자동으로 처리됨
   enum EnumSingleton {
       INSTANCE;
       // readResolve() 불필요!
   }
   ```

2. **리플렉션 공격 방지:**
   ```java
   // 일반 클래스는 리플렉션으로 private 생성자 호출 가능
   Constructor<NormalSingleton> constructor =
       NormalSingleton.class.getDeclaredConstructor();
   constructor.setAccessible(true);
   NormalSingleton hacked = constructor.newInstance();  // 새 인스턴스!

   // Enum은 리플렉션으로 생성 불가능
   // Constructor.newInstance()가 Enum 체크하고 예외 발생
   ```

**실무 활용:**
```java
enum DatabaseConnection {
    INSTANCE;

    private Connection connection;

    DatabaseConnection() {
        // 초기화 (클래스 로딩 시 한 번만)
        try {
            connection = DriverManager.getConnection(
                "jdbc:mysql://localhost/db", "user", "password"
            );
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    public ResultSet executeQuery(String sql) throws SQLException {
        return connection.createStatement().executeQuery(sql);
    }
}

// 사용
DatabaseConnection.INSTANCE.executeQuery("SELECT * FROM users");
```

---

#### Q9. EnumSet과 EnumMap의 내부 구현과 성능 특성을 설명하세요.

**모범 답변:**

**EnumSet 내부 구현:**

```java
// EnumSet은 abstract 클래스
// 실제로는 RegularEnumSet 또는 JumboEnumSet 사용

// Enum이 64개 이하: RegularEnumSet (long 비트 벡터)
// Enum이 65개 이상: JumboEnumSet (long[] 배열)

enum SmallEnum {  // 3개
    A, B, C
}

EnumSet<SmallEnum> set = EnumSet.noneOf(SmallEnum.class);
// 내부적으로 long elements = 0L;

set.add(SmallEnum.A);  // elements |= (1L << 0);  → 001
set.add(SmallEnum.C);  // elements |= (1L << 2);  → 101

set.contains(SmallEnum.B);  // (elements & (1L << 1)) != 0  → false
set.contains(SmallEnum.A);  // (elements & (1L << 0)) != 0  → true
```

**성능 비교:**
```java
// HashSet vs EnumSet 벤치마크
enum Letter { A, B, C, D, E, F, G, H }

// HashSet<Letter>
// - contains(): O(1) 하지만 해시 계산 필요
// - add/remove: O(1) 하지만 해시 재조정 가능
// - 메모리: Node 객체들 + 배열

// EnumSet<Letter>
// - contains(): O(1) 단순 비트 연산
// - add/remove: O(1) 단순 비트 연산
// - 메모리: 단일 long (8바이트)

// 성능 차이
Set<Letter> hashSet = new HashSet<>();
EnumSet<Letter> enumSet = EnumSet.noneOf(Letter.class);

// HashSet.contains(): ~20ns (해시 계산)
// EnumSet.contains(): ~5ns (비트 AND)
// → EnumSet이 약 4배 빠름!
```

**EnumMap 내부 구현:**

```java
public class EnumMap<K extends Enum<K>, V> {
    private final Class<K> keyType;
    private transient K[] keyUniverse;  // Enum.values()
    private transient Object[] vals;    // 값 배열

    public V get(Object key) {
        // HashMap: 해시 계산 + 충돌 처리
        // EnumMap: 배열 인덱스 직접 접근
        return (V) vals[((Enum<?>)key).ordinal()];
    }

    public V put(K key, V value) {
        int index = key.ordinal();
        vals[index] = value;
        return oldValue;
    }
}

// 예제
enum Day { MON, TUE, WED }

EnumMap<Day, String> map = new EnumMap<>(Day.class);
// 내부: Object[] vals = new Object[3];

map.put(Day.MON, "월요일");
// vals[0] = "월요일"

map.get(Day.MON);
// return vals[0];  // O(1) 배열 접근
```

**실무 활용:**
```java
// 권한 관리
enum Permission {
    READ, WRITE, DELETE, ADMIN
}

class User {
    private EnumSet<Permission> permissions;

    public User() {
        permissions = EnumSet.noneOf(Permission.class);
    }

    public void grantAdmin() {
        permissions = EnumSet.allOf(Permission.class);
    }

    public void grantReadWrite() {
        permissions = EnumSet.of(Permission.READ, Permission.WRITE);
    }

    public boolean hasPermission(Permission p) {
        return permissions.contains(p);  // 비트 연산으로 초고속
    }
}

// 스케줄 관리
enum Day {
    MON, TUE, WED, THU, FRI, SAT, SUN
}

EnumMap<Day, List<Task>> schedule = new EnumMap<>(Day.class);
schedule.put(Day.MON, Arrays.asList(task1, task2));
```

**성능 요약:**

| 연산 | HashSet/HashMap | EnumSet/EnumMap |
|------|-----------------|-----------------|
| 메모리 | 큼 (Node 객체) | 작음 (배열/비트) |
| contains/get | O(1) 해시 계산 | O(1) 비트/인덱스 |
| add/put | O(1) + 재조정 | O(1) 단순 대입 |
| 순회 | 순서 불확실 | Enum 순서 보장 |
| 속도 | 보통 | 매우 빠름 (2~4배) |

---

#### Q10. Enum을 사용한 상태 머신(State Machine) 패턴을 설계하고 구현하세요.

**모범 답변:**

상태 머신은 **정해진 상태들 사이의 전이 규칙**을 관리하는 패턴으로, Enum이 이상적입니다.

**설계 원칙:**
1. 각 상태가 허용하는 다음 상태 정의
2. 상태별 행동 정의
3. 잘못된 전이 방지

**구현:**

```java
/**
 * 신호등 상태 머신
 */
enum TrafficLightState {
    RED(30) {
        @Override
        public TrafficLightState next() {
            return GREEN;
        }

        @Override
        public String getAction() {
            return "정지";
        }

        @Override
        public boolean canCross() {
            return false;
        }
    },

    YELLOW(3) {
        @Override
        public TrafficLightState next() {
            return RED;
        }

        @Override
        public String getAction() {
            return "주의";
        }

        @Override
        public boolean canCross() {
            return false;
        }
    },

    GREEN(25) {
        @Override
        public TrafficLightState next() {
            return YELLOW;
        }

        @Override
        public String getAction() {
            return "진행";
        }

        @Override
        public boolean canCross() {
            return true;
        }
    };

    private final int duration;  // 지속 시간 (초)

    TrafficLightState(int duration) {
        this.duration = duration;
    }

    public int getDuration() {
        return duration;
    }

    // 각 상태가 구현해야 하는 메서드
    public abstract TrafficLightState next();
    public abstract String getAction();
    public abstract boolean canCross();
}

/**
 * 신호등 컨트롤러
 */
class TrafficLight {
    private TrafficLightState currentState;
    private int remainingTime;

    public TrafficLight() {
        this.currentState = TrafficLightState.RED;
        this.remainingTime = currentState.getDuration();
    }

    public void tick() {  // 1초 경과
        remainingTime--;

        if (remainingTime <= 0) {
            changeState();
        }
    }

    private void changeState() {
        TrafficLightState oldState = currentState;
        currentState = currentState.next();
        remainingTime = currentState.getDuration();

        System.out.println(oldState + " → " + currentState +
                         " (" + currentState.getAction() + ")");
    }

    public void printStatus() {
        System.out.println("현재: " + currentState +
                         " | 남은 시간: " + remainingTime + "초 | " +
                         "횡단: " + (currentState.canCross() ? "가능" : "불가"));
    }
}

/**
 * 더 복잡한 예: 주문 상태 머신
 */
enum OrderState {
    PENDING("주문 접수") {
        @Override
        public Set<OrderState> getAllowedTransitions() {
            return EnumSet.of(CONFIRMED, CANCELLED);
        }

        @Override
        public void onEnter(Order order) {
            order.sendEmail("주문이 접수되었습니다.");
        }
    },

    CONFIRMED("주문 확인") {
        @Override
        public Set<OrderState> getAllowedTransitions() {
            return EnumSet.of(PROCESSING, CANCELLED);
        }

        @Override
        public void onEnter(Order order) {
            order.processPayment();
            order.sendEmail("결제가 완료되었습니다.");
        }
    },

    PROCESSING("처리 중") {
        @Override
        public Set<OrderState> getAllowedTransitions() {
            return EnumSet.of(SHIPPED, CANCELLED);
        }

        @Override
        public void onEnter(Order order) {
            order.prepareItems();
        }
    },

    SHIPPED("배송 중") {
        @Override
        public Set<OrderState> getAllowedTransitions() {
            return EnumSet.of(DELIVERED);
        }

        @Override
        public void onEnter(Order order) {
            order.assignDelivery();
            order.sendSMS("상품이 배송 시작되었습니다.");
        }

        @Override
        public void onExit(Order order) {
            order.updateDeliveryTracking();
        }
    },

    DELIVERED("배송 완료") {
        @Override
        public Set<OrderState> getAllowedTransitions() {
            return EnumSet.of(RETURNED);
        }

        @Override
        public void onEnter(Order order) {
            order.sendEmail("배송이 완료되었습니다.");
            order.requestReview();
        }
    },

    CANCELLED("취소") {
        @Override
        public Set<OrderState> getAllowedTransitions() {
            return EnumSet.noneOf(OrderState.class);
        }

        @Override
        public void onEnter(Order order) {
            order.refundPayment();
            order.sendEmail("주문이 취소되었습니다.");
        }

        @Override
        public boolean isFinalState() {
            return true;
        }
    },

    RETURNED("반품") {
        @Override
        public Set<OrderState> getAllowedTransitions() {
            return EnumSet.noneOf(OrderState.class);
        }

        @Override
        public void onEnter(Order order) {
            order.processReturn();
            order.refundPayment();
        }

        @Override
        public boolean isFinalState() {
            return true;
        }
    };

    private final String displayName;

    OrderState(String displayName) {
        this.displayName = displayName;
    }

    public String getDisplayName() {
        return displayName;
    }

    // 각 상태가 정의하는 전이 규칙
    public abstract Set<OrderState> getAllowedTransitions();

    // 상태 진입 시 동작
    public void onEnter(Order order) {
        // 기본 구현 없음
    }

    // 상태 이탈 시 동작
    public void onExit(Order order) {
        // 기본 구현 없음
    }

    // 최종 상태 여부
    public boolean isFinalState() {
        return false;
    }

    // 전이 가능 여부 확인
    public boolean canTransitionTo(OrderState newState) {
        return getAllowedTransitions().contains(newState);
    }
}

/**
 * 주문 클래스
 */
class Order {
    private String orderId;
    private OrderState state;

    public Order(String orderId) {
        this.orderId = orderId;
        this.state = OrderState.PENDING;
        state.onEnter(this);
    }

    public boolean transitionTo(OrderState newState) {
        if (!state.canTransitionTo(newState)) {
            System.out.println("❌ 전이 불가: " + state + " → " + newState);
            return false;
        }

        OrderState oldState = state;

        // 1. 현재 상태 종료
        oldState.onExit(this);

        // 2. 상태 변경
        state = newState;

        // 3. 새 상태 진입
        newState.onEnter(this);

        System.out.println("✅ 전이 성공: " + oldState + " → " + newState);
        return true;
    }

    // 주문 관련 동작들
    public void sendEmail(String message) {
        System.out.println("  📧 Email: " + message);
    }

    public void sendSMS(String message) {
        System.out.println("  📱 SMS: " + message);
    }

    public void processPayment() {
        System.out.println("  💳 결제 처리");
    }

    public void refundPayment() {
        System.out.println("  💰 환불 처리");
    }

    public void prepareItems() {
        System.out.println("  📦 상품 준비");
    }

    public void assignDelivery() {
        System.out.println("  🚚 배송 할당");
    }

    public void updateDeliveryTracking() {
        System.out.println("  🔍 배송 추적 업데이트");
    }

    public void requestReview() {
        System.out.println("  ⭐ 리뷰 요청");
    }

    public void processReturn() {
        System.out.println("  ↩️  반품 처리");
    }
}
```

**테스트:**
```java
public class StateMachineTest {
    public static void main(String[] args) {
        // 신호등 테스트
        System.out.println("=== 신호등 상태 머신 ===\n");
        TrafficLight light = new TrafficLight();
        for (int i = 0; i < 60; i++) {
            light.tick();
            if (i % 10 == 0) {
                light.printStatus();
            }
        }

        // 주문 테스트
        System.out.println("\n=== 주문 상태 머신 ===\n");
        Order order = new Order("ORD-001");
        order.transitionTo(OrderState.CONFIRMED);
        order.transitionTo(OrderState.PROCESSING);
        order.transitionTo(OrderState.SHIPPED);
        order.transitionTo(OrderState.DELIVERED);

        // 잘못된 전이 시도
        order.transitionTo(OrderState.PROCESSING);  // 실패
    }
}
```

**장점:**
- ✅ 명확한 상태 전이 규칙
- ✅ 잘못된 전이 컴파일 타임에 방지
- ✅ 각 상태의 행동 캡슐화
- ✅ 테스트 용이

---

## 🎯 최종 정리

### Enum 핵심 개념

1. **타입 안정성**
   - 정해진 값만 사용 가능
   - 컴파일 타임에 오류 발견

2. **풍부한 기능**
   - 필드와 메서드 추가
   - 추상 메서드로 각 상수별 구현

3. **성능**
   - `==` 비교로 빠름
   - EnumSet/EnumMap으로 최적화

4. **안전성**
   - 싱글톤 보장
   - 직렬화 안전
   - 리플렉션 방어

### 실무 가이드

1. **== 사용**
   - Enum 비교는 항상 `==`
   - null-safe하고 빠름

2. **ordinal() 금지**
   - DB, 파일, API에 저장 금지
   - 명시적 코드 필드 사용

3. **valueOf() 예외 처리**
   - 사용자 입력은 검증 필수
   - Optional 또는 기본값 제공

4. **상수 클래스 대체**
   - 항상 Enum 사용
   - 타입 안정성과 기능 확보

다음 Chapter 21에서는 **Annotation (어노테이션)**을 다루겠습니다! 🚀
