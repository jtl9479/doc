# 20-1. Enum (열거형) Part 1: 실생활 비유

## 🎯 Enum이란?

Enum(열거형)은 **서로 관련된 상수들의 집합을 정의하는 특별한 클래스**입니다. 정해진 값들만 가질 수 있는 타입을 만들 때 사용하며, 타입 안정성을 제공합니다.

### 왜 Enum을 사용할까?

**Before (상수 사용):**
```java
// ❌ 문제점이 많은 방식
class DayConstants {
    public static final int MONDAY = 0;
    public static final int TUESDAY = 1;
    public static final int WEDNESDAY = 2;
    // ...
}

// 타입 안정성 없음
int day = 999;  // 잘못된 값도 허용됨
if (day == DayConstants.MONDAY) { /* ... */ }
```

**After (Enum 사용):**
```java
// ✅ 타입 안정성 제공
enum Day {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
}

// 정해진 값만 허용
Day day = Day.MONDAY;  // ✅
// Day day = 999;  // ❌ 컴파일 에러!
```

---

## 🌍 실생활 비유 1: 요일 (DayOfWeek)

### 📖 비유 설명

요일은 항상 7개로 고정되어 있습니다. 월, 화, 수, 목, 금, 토, 일 - 이 외의 요일은 존재하지 않습니다. 이런 **고정된 값들의 집합**을 표현하는 데 Enum이 완벽합니다.

### 💻 코드 구현

```java
/**
 * 요일 열거형
 */
enum DayOfWeek {
    MONDAY("월요일", true),
    TUESDAY("화요일", true),
    WEDNESDAY("수요일", true),
    THURSDAY("목요일", true),
    FRIDAY("금요일", true),
    SATURDAY("토요일", false),
    SUNDAY("일요일", false);

    private final String koreanName;
    private final boolean isWeekday;

    // Enum 생성자 (항상 private)
    DayOfWeek(String koreanName, boolean isWeekday) {
        this.koreanName = koreanName;
        this.isWeekday = isWeekday;
    }

    // Getter 메서드
    public String getKoreanName() {
        return koreanName;
    }

    public boolean isWeekday() {
        return isWeekday;
    }

    public boolean isWeekend() {
        return !isWeekday;
    }

    // 다음 날 구하기
    public DayOfWeek next() {
        int nextOrdinal = (this.ordinal() + 1) % 7;
        return DayOfWeek.values()[nextOrdinal];
    }

    // 이전 날 구하기
    public DayOfWeek previous() {
        int prevOrdinal = (this.ordinal() + 6) % 7;
        return DayOfWeek.values()[prevOrdinal];
    }

    // 며칠 후 구하기
    public DayOfWeek plus(int days) {
        int newOrdinal = (this.ordinal() + days) % 7;
        if (newOrdinal < 0) {
            newOrdinal += 7;
        }
        return DayOfWeek.values()[newOrdinal];
    }
}

/**
 * 근무 스케줄 클래스
 */
class WorkSchedule {
    private DayOfWeek workDay;
    private String task;

    public WorkSchedule(DayOfWeek workDay, String task) {
        this.workDay = workDay;
        this.task = task;
    }

    public void printSchedule() {
        String dayType = workDay.isWeekday() ? "평일" : "주말";
        System.out.println(workDay.getKoreanName() + " (" + dayType + "): " + task);
    }

    public DayOfWeek getWorkDay() {
        return workDay;
    }

    public String getTask() {
        return task;
    }
}
```

### 🧪 테스트 코드

```java
/**
 * 요일 Enum 테스트
 */
public class DayOfWeekTest {

    public static void main(String[] args) {

        System.out.println("=================================================");
        System.out.println("요일 (DayOfWeek) Enum 테스트");
        System.out.println("=================================================\n");

        // 테스트 1: 기본 사용
        test1_BasicUsage();

        // 테스트 2: 요일 순환
        test2_DayRotation();

        // 테스트 3: 평일/주말 구분
        test3_WeekdayWeekend();

        // 테스트 4: 근무 스케줄
        test4_WorkSchedule();

        // 테스트 5: Enum 메서드들
        test5_EnumMethods();
    }

    static void test1_BasicUsage() {
        System.out.println("### 테스트 1: 기본 사용 ###\n");

        DayOfWeek today = DayOfWeek.MONDAY;
        System.out.println("오늘: " + today);
        System.out.println("한글 이름: " + today.getKoreanName());
        System.out.println("평일 여부: " + today.isWeekday());
        System.out.println("주말 여부: " + today.isWeekend());

        System.out.println();
    }

    static void test2_DayRotation() {
        System.out.println("### 테스트 2: 요일 순환 ###\n");

        DayOfWeek today = DayOfWeek.FRIDAY;
        System.out.println("오늘: " + today.getKoreanName());
        System.out.println("다음 날: " + today.next().getKoreanName());
        System.out.println("이전 날: " + today.previous().getKoreanName());
        System.out.println("3일 후: " + today.plus(3).getKoreanName());
        System.out.println("10일 후: " + today.plus(10).getKoreanName());

        System.out.println();
    }

    static void test3_WeekdayWeekend() {
        System.out.println("### 테스트 3: 평일/주말 구분 ###\n");

        System.out.println("평일:");
        for (DayOfWeek day : DayOfWeek.values()) {
            if (day.isWeekday()) {
                System.out.println("  " + day.getKoreanName());
            }
        }

        System.out.println("\n주말:");
        for (DayOfWeek day : DayOfWeek.values()) {
            if (day.isWeekend()) {
                System.out.println("  " + day.getKoreanName());
            }
        }

        System.out.println();
    }

    static void test4_WorkSchedule() {
        System.out.println("### 테스트 4: 근무 스케줄 ###\n");

        WorkSchedule[] schedules = {
            new WorkSchedule(DayOfWeek.MONDAY, "프로젝트 회의"),
            new WorkSchedule(DayOfWeek.WEDNESDAY, "코드 리뷰"),
            new WorkSchedule(DayOfWeek.FRIDAY, "스프린트 회고"),
            new WorkSchedule(DayOfWeek.SATURDAY, "휴식"),
            new WorkSchedule(DayOfWeek.SUNDAY, "자기계발")
        };

        for (WorkSchedule schedule : schedules) {
            schedule.printSchedule();
        }

        System.out.println();
    }

    static void test5_EnumMethods() {
        System.out.println("### 테스트 5: Enum 메서드들 ###\n");

        DayOfWeek day = DayOfWeek.WEDNESDAY;

        // name() - Enum 상수의 이름
        System.out.println("name(): " + day.name());

        // ordinal() - Enum 상수의 순서 (0부터 시작)
        System.out.println("ordinal(): " + day.ordinal());

        // values() - 모든 Enum 상수 배열
        System.out.println("\nvalues():");
        for (DayOfWeek d : DayOfWeek.values()) {
            System.out.println("  " + d.name() + " (순서: " + d.ordinal() + ")");
        }

        // valueOf() - 문자열을 Enum 상수로 변환
        System.out.println("\nvalueOf(\"FRIDAY\"): " + DayOfWeek.valueOf("FRIDAY").getKoreanName());

        // compareTo() - Enum 상수 비교
        System.out.println("\nMONDAY.compareTo(FRIDAY): " + DayOfWeek.MONDAY.compareTo(DayOfWeek.FRIDAY));

        System.out.println();
    }
}
```

### 🎯 핵심 포인트

1. **타입 안정성**: 정해진 요일만 사용 가능
2. **필드와 메서드**: Enum에 데이터와 동작 추가 가능
3. **순환 로직**: ordinal()과 values()로 다음/이전 요일 계산
4. **가독성**: MONDAY보다 DayOfWeek.MONDAY가 의미 명확

---

## 🌸 실생활 비유 2: 계절 (Season)

### 📖 비유 설명

1년은 항상 봄, 여름, 가을, 겨울 4계절로 구성됩니다. 각 계절은 고유한 특성(평균 기온, 대표 월 등)을 가지며, 순환합니다.

### 💻 코드 구현

```java
/**
 * 계절 열거형
 */
enum Season {
    SPRING("봄", "🌸", new int[]{3, 4, 5}, 15.0),
    SUMMER("여름", "☀️", new int[]{6, 7, 8}, 28.0),
    AUTUMN("가을", "🍂", new int[]{9, 10, 11}, 18.0),
    WINTER("겨울", "⛄", new int[]{12, 1, 2}, 0.0);

    private final String koreanName;
    private final String emoji;
    private final int[] months;
    private final double averageTemperature;

    Season(String koreanName, String emoji, int[] months, double averageTemperature) {
        this.koreanName = koreanName;
        this.emoji = emoji;
        this.months = months;
        this.averageTemperature = averageTemperature;
    }

    public String getKoreanName() {
        return koreanName;
    }

    public String getEmoji() {
        return emoji;
    }

    public int[] getMonths() {
        return months;
    }

    public double getAverageTemperature() {
        return averageTemperature;
    }

    // 다음 계절
    public Season next() {
        int nextOrdinal = (this.ordinal() + 1) % 4;
        return Season.values()[nextOrdinal];
    }

    // 특정 월의 계절 찾기
    public static Season fromMonth(int month) {
        for (Season season : Season.values()) {
            for (int m : season.months) {
                if (m == month) {
                    return season;
                }
            }
        }
        throw new IllegalArgumentException("Invalid month: " + month);
    }

    // 추천 활동
    public String getRecommendedActivity() {
        switch (this) {
            case SPRING:
                return "벚꽃 구경, 소풍";
            case SUMMER:
                return "해수욕, 캠핑";
            case AUTUMN:
                return "단풍 구경, 등산";
            case WINTER:
                return "스키, 온천";
            default:
                return "휴식";
        }
    }

    // 옷차림 추천
    public String getClothingRecommendation() {
        if (averageTemperature < 5) {
            return "두꺼운 외투, 목도리";
        } else if (averageTemperature < 12) {
            return "가디건, 얇은 자켓";
        } else if (averageTemperature < 20) {
            return "긴팔 티셔츠, 가벼운 외투";
        } else {
            return "반팔, 반바지";
        }
    }
}

/**
 * 계절 정보 출력 클래스
 */
class SeasonInfo {

    public static void printSeasonDetails(Season season) {
        System.out.println("\n" + "=".repeat(50));
        System.out.println(season.getEmoji() + " " + season.getKoreanName() + " " + season.getEmoji());
        System.out.println("=".repeat(50));

        System.out.print("해당 월: ");
        for (int month : season.getMonths()) {
            System.out.print(month + "월 ");
        }
        System.out.println();

        System.out.println("평균 기온: " + season.getAverageTemperature() + "°C");
        System.out.println("추천 활동: " + season.getRecommendedActivity());
        System.out.println("옷차림: " + season.getClothingRecommendation());
    }

    public static void printSeasonCycle() {
        System.out.println("\n계절 순환:");
        Season current = Season.SPRING;
        for (int i = 0; i < 8; i++) {
            System.out.print(current.getKoreanName());
            if (i < 7) {
                System.out.print(" → ");
            }
            current = current.next();
        }
        System.out.println();
    }
}
```

### 🧪 테스트 코드

```java
/**
 * 계절 Enum 테스트
 */
public class SeasonTest {

    public static void main(String[] args) {

        System.out.println("=================================================");
        System.out.println("계절 (Season) Enum 테스트");
        System.out.println("=================================================");

        // 테스트 1: 모든 계절 정보
        test1_AllSeasons();

        // 테스트 2: 계절 순환
        test2_SeasonCycle();

        // 테스트 3: 월로 계절 찾기
        test3_FindSeasonByMonth();

        // 테스트 4: 기온에 따른 추천
        test4_TemperatureBasedRecommendation();
    }

    static void test1_AllSeasons() {
        System.out.println("\n### 테스트 1: 모든 계절 정보 ###");

        for (Season season : Season.values()) {
            SeasonInfo.printSeasonDetails(season);
        }
    }

    static void test2_SeasonCycle() {
        System.out.println("\n### 테스트 2: 계절 순환 ###");

        SeasonInfo.printSeasonCycle();
    }

    static void test3_FindSeasonByMonth() {
        System.out.println("\n### 테스트 3: 월로 계절 찾기 ###\n");

        int[] testMonths = {1, 3, 7, 10, 12};

        for (int month : testMonths) {
            Season season = Season.fromMonth(month);
            System.out.println(month + "월 → " + season.getKoreanName() + " " + season.getEmoji());
        }
    }

    static void test4_TemperatureBasedRecommendation() {
        System.out.println("\n### 테스트 4: 기온에 따른 추천 ###\n");

        for (Season season : Season.values()) {
            System.out.println(season.getKoreanName() +
                " (평균 " + season.getAverageTemperature() + "°C):");
            System.out.println("  옷차림: " + season.getClothingRecommendation());
            System.out.println("  추천 활동: " + season.getRecommendedActivity());
            System.out.println();
        }
    }
}
```

### 🎯 핵심 포인트

1. **복잡한 데이터**: 배열, 실수 등 다양한 타입 저장 가능
2. **static 메서드**: fromMonth()처럼 유틸리티 메서드 추가
3. **switch 문**: Enum은 switch 문과 완벽하게 호환
4. **비즈니스 로직**: getRecommendedActivity()처럼 도메인 로직 포함

---

## 🚦 실생활 비유 3: 신호등 (TrafficLight)

### 📖 비유 설명

신호등은 빨강, 노랑, 초록 3가지 상태만 가지며, 순환하며 변합니다. 각 신호는 특정 행동(정지, 주의, 진행)을 나타냅니다.

### 💻 코드 구현

```java
/**
 * 신호등 열거형
 */
enum TrafficLight {
    RED("빨강", "🔴", "정지", 0) {
        @Override
        public TrafficLight next() {
            return GREEN;  // 빨강 다음은 초록
        }
    },
    YELLOW("노랑", "🟡", "주의", 3) {
        @Override
        public TrafficLight next() {
            return RED;  // 노랑 다음은 빨강
        }
    },
    GREEN("초록", "🟢", "진행", 30) {
        @Override
        public TrafficLight next() {
            return YELLOW;  // 초록 다음은 노랑
        }
    };

    private final String koreanName;
    private final String emoji;
    private final String action;
    private final int durationSeconds;

    TrafficLight(String koreanName, String emoji, String action, int durationSeconds) {
        this.koreanName = koreanName;
        this.emoji = emoji;
        this.action = action;
        this.durationSeconds = durationSeconds;
    }

    public String getKoreanName() {
        return koreanName;
    }

    public String getEmoji() {
        return emoji;
    }

    public String getAction() {
        return action;
    }

    public int getDurationSeconds() {
        return durationSeconds;
    }

    // 추상 메서드 - 각 신호등이 다르게 구현
    public abstract TrafficLight next();

    // 진행 가능 여부
    public boolean canGo() {
        return this == GREEN;
    }

    // 정지 필요 여부
    public boolean mustStop() {
        return this == RED || this == YELLOW;
    }
}

/**
 * 교차로 시뮬레이터
 */
class Intersection {
    private TrafficLight currentLight;
    private String name;

    public Intersection(String name) {
        this.name = name;
        this.currentLight = TrafficLight.RED;
    }

    public void changeLight() {
        TrafficLight oldLight = currentLight;
        currentLight = currentLight.next();

        System.out.println("\n[" + name + " 교차로]");
        System.out.println(oldLight.getEmoji() + " " + oldLight.getKoreanName() +
                         " → " + currentLight.getEmoji() + " " + currentLight.getKoreanName());
        System.out.println("행동: " + currentLight.getAction());
        System.out.println("신호 유지 시간: " + currentLight.getDurationSeconds() + "초");
    }

    public void checkCanCross() {
        System.out.println("\n현재 신호: " + currentLight.getEmoji() + " " + currentLight.getKoreanName());

        if (currentLight.canGo()) {
            System.out.println("✅ 안전하게 건널 수 있습니다.");
        } else if (currentLight.mustStop()) {
            System.out.println("⛔ 정지하세요!");
        }
    }

    public TrafficLight getCurrentLight() {
        return currentLight;
    }
}

/**
 * 차량 클래스
 */
class Vehicle {
    private String name;

    public Vehicle(String name) {
        this.name = name;
    }

    public void reactToLight(TrafficLight light) {
        System.out.print("\n[" + name + "] ");
        System.out.print(light.getEmoji() + " " + light.getKoreanName() + " 신호 → ");

        switch (light) {
            case RED:
                System.out.println("정지선에서 멈춥니다.");
                break;
            case YELLOW:
                System.out.println("속도를 줄이고 정지 준비합니다.");
                break;
            case GREEN:
                System.out.println("안전하게 출발합니다.");
                break;
        }
    }
}
```

### 🧪 테스트 코드

```java
/**
 * 신호등 Enum 테스트
 */
public class TrafficLightTest {

    public static void main(String[] args) {

        System.out.println("=================================================");
        System.out.println("신호등 (TrafficLight) Enum 테스트");
        System.out.println("=================================================");

        // 테스트 1: 신호등 순환
        test1_LightCycle();

        // 테스트 2: 교차로 시뮬레이션
        test2_IntersectionSimulation();

        // 테스트 3: 차량 반응
        test3_VehicleReaction();

        // 테스트 4: 안전 체크
        test4_SafetyCheck();
    }

    static void test1_LightCycle() {
        System.out.println("\n### 테스트 1: 신호등 순환 ###\n");

        TrafficLight light = TrafficLight.RED;

        for (int i = 0; i < 6; i++) {
            System.out.println((i + 1) + ". " + light.getEmoji() + " " +
                             light.getKoreanName() + " (" +
                             light.getDurationSeconds() + "초)");
            light = light.next();
        }
    }

    static void test2_IntersectionSimulation() {
        System.out.println("\n### 테스트 2: 교차로 시뮬레이션 ###");

        Intersection intersection = new Intersection("서울역");

        for (int i = 0; i < 4; i++) {
            intersection.changeLight();
            try {
                Thread.sleep(1000);  // 1초 대기 (시뮬레이션)
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    static void test3_VehicleReaction() {
        System.out.println("\n### 테스트 3: 차량 반응 ###");

        Vehicle car = new Vehicle("현대 소나타");

        for (TrafficLight light : TrafficLight.values()) {
            car.reactToLight(light);
        }
    }

    static void test4_SafetyCheck() {
        System.out.println("\n### 테스트 4: 안전 체크 ###");

        Intersection intersection = new Intersection("강남역");

        for (int i = 0; i < 3; i++) {
            intersection.checkCanCross();
            intersection.changeLight();
        }
    }
}
```

### 🎯 핵심 포인트

1. **추상 메서드**: 각 Enum 상수가 다르게 구현 가능
2. **상태 전이**: next() 메서드로 상태 변화 표현
3. **조건 메서드**: canGo(), mustStop()으로 비즈니스 로직
4. **익명 클래스**: 각 Enum 상수에서 메서드 오버라이드

---

## 💳 실생활 비유 4: 카드 등급 (CardTier)

### 📖 비유 설명

신용카드는 등급(일반, 실버, 골드, 플래티넘)에 따라 혜택이 다릅니다. 등급이 높을수록 할인율, 포인트 적립률이 높아집니다.

### 💻 코드 구현

```java
/**
 * 카드 등급 열거형
 */
enum CardTier {
    BASIC("일반", 0.5, 1.0, 0, 0xC0C0C0),
    SILVER("실버", 1.0, 1.5, 100000, 0xC0C0C0),
    GOLD("골드", 2.0, 2.5, 500000, 0xFFD700),
    PLATINUM("플래티넘", 3.0, 5.0, 2000000, 0xE5E4E2);

    private final String koreanName;
    private final double discountRate;      // 할인율 (%)
    private final double pointRate;         // 포인트 적립률 (%)
    private final int annualFee;            // 연회비 (원)
    private final int colorCode;            // 카드 색상 코드

    CardTier(String koreanName, double discountRate, double pointRate,
             int annualFee, int colorCode) {
        this.koreanName = koreanName;
        this.discountRate = discountRate;
        this.pointRate = pointRate;
        this.annualFee = annualFee;
        this.colorCode = colorCode;
    }

    public String getKoreanName() {
        return koreanName;
    }

    public double getDiscountRate() {
        return discountRate;
    }

    public double getPointRate() {
        return pointRate;
    }

    public int getAnnualFee() {
        return annualFee;
    }

    public String getColorCode() {
        return String.format("#%06X", colorCode);
    }

    // 할인 금액 계산
    public int calculateDiscount(int amount) {
        return (int) (amount * discountRate / 100);
    }

    // 적립 포인트 계산
    public int calculatePoints(int amount) {
        return (int) (amount * pointRate / 100);
    }

    // 등급 업그레이드 가능 여부
    public boolean canUpgrade() {
        return this.ordinal() < CardTier.values().length - 1;
    }

    // 다음 등급
    public CardTier nextTier() {
        if (!canUpgrade()) {
            throw new IllegalStateException("이미 최고 등급입니다.");
        }
        return CardTier.values()[this.ordinal() + 1];
    }

    // 등급에 따른 혜택 설명
    public String getBenefits() {
        switch (this) {
            case BASIC:
                return "기본 혜택";
            case SILVER:
                return "공항 라운지 이용권 연 2회";
            case GOLD:
                return "공항 라운지 무제한 + 호텔 할인 10%";
            case PLATINUM:
                return "공항 라운지 무제한 + 호텔 할인 20% + 전용 컨시어지";
            default:
                return "혜택 없음";
        }
    }

    // 소비 금액 기준 추천 등급
    public static CardTier recommendTier(int monthlySpending) {
        if (monthlySpending < 500000) {
            return BASIC;
        } else if (monthlySpending < 2000000) {
            return SILVER;
        } else if (monthlySpending < 5000000) {
            return GOLD;
        } else {
            return PLATINUM;
        }
    }
}

/**
 * 신용카드 클래스
 */
class CreditCard {
    private String cardNumber;
    private String ownerName;
    private CardTier tier;
    private int accumulatedPoints;

    public CreditCard(String cardNumber, String ownerName, CardTier tier) {
        this.cardNumber = cardNumber;
        this.ownerName = ownerName;
        this.tier = tier;
        this.accumulatedPoints = 0;
    }

    public void purchase(int amount) {
        int discount = tier.calculateDiscount(amount);
        int finalAmount = amount - discount;
        int earnedPoints = tier.calculatePoints(amount);

        accumulatedPoints += earnedPoints;

        System.out.println("\n💳 카드 결제");
        System.out.println("카드 등급: " + tier.getKoreanName());
        System.out.println("원래 금액: " + String.format("%,d원", amount));
        System.out.println("할인 금액: " + String.format("%,d원", discount) +
                         " (" + tier.getDiscountRate() + "%)");
        System.out.println("최종 금액: " + String.format("%,d원", finalAmount));
        System.out.println("적립 포인트: " + String.format("%,d P", earnedPoints) +
                         " (" + tier.getPointRate() + "%)");
        System.out.println("누적 포인트: " + String.format("%,d P", accumulatedPoints));
    }

    public void printCardInfo() {
        System.out.println("\n" + "=".repeat(50));
        System.out.println("카드 정보");
        System.out.println("=".repeat(50));
        System.out.println("카드 번호: " + cardNumber);
        System.out.println("소유자: " + ownerName);
        System.out.println("등급: " + tier.getKoreanName());
        System.out.println("카드 색상: " + tier.getColorCode());
        System.out.println("연회비: " + String.format("%,d원", tier.getAnnualFee()));
        System.out.println("할인율: " + tier.getDiscountRate() + "%");
        System.out.println("포인트 적립률: " + tier.getPointRate() + "%");
        System.out.println("특별 혜택: " + tier.getBenefits());
        System.out.println("누적 포인트: " + String.format("%,d P", accumulatedPoints));
    }

    public void upgrade() {
        if (tier.canUpgrade()) {
            CardTier oldTier = tier;
            tier = tier.nextTier();
            System.out.println("\n🎉 카드 등급 업그레이드!");
            System.out.println(oldTier.getKoreanName() + " → " + tier.getKoreanName());
        } else {
            System.out.println("\n이미 최고 등급입니다.");
        }
    }

    public CardTier getTier() {
        return tier;
    }
}
```

### 🧪 테스트 코드

```java
/**
 * 카드 등급 Enum 테스트
 */
public class CardTierTest {

    public static void main(String[] args) {

        System.out.println("=================================================");
        System.out.println("카드 등급 (CardTier) Enum 테스트");
        System.out.println("=================================================");

        // 테스트 1: 모든 등급 정보
        test1_AllTiers();

        // 테스트 2: 카드 사용 시뮬레이션
        test2_CardUsage();

        // 테스트 3: 등급 업그레이드
        test3_TierUpgrade();

        // 테스트 4: 등급 추천
        test4_TierRecommendation();
    }

    static void test1_AllTiers() {
        System.out.println("\n### 테스트 1: 모든 등급 정보 ###\n");

        for (CardTier tier : CardTier.values()) {
            System.out.println(tier.getKoreanName() + " 카드:");
            System.out.println("  연회비: " + String.format("%,d원", tier.getAnnualFee()));
            System.out.println("  할인율: " + tier.getDiscountRate() + "%");
            System.out.println("  포인트: " + tier.getPointRate() + "%");
            System.out.println("  색상: " + tier.getColorCode());
            System.out.println("  혜택: " + tier.getBenefits());
            System.out.println();
        }
    }

    static void test2_CardUsage() {
        System.out.println("\n### 테스트 2: 카드 사용 시뮬레이션 ###");

        CreditCard card = new CreditCard("1234-5678-9012-3456", "홍길동", CardTier.GOLD);
        card.printCardInfo();

        // 여러 번 결제
        card.purchase(100000);
        card.purchase(50000);
        card.purchase(200000);

        card.printCardInfo();
    }

    static void test3_TierUpgrade() {
        System.out.println("\n### 테스트 3: 등급 업그레이드 ###");

        CreditCard card = new CreditCard("9876-5432-1098-7654", "김철수", CardTier.BASIC);

        System.out.println("\n초기 상태:");
        card.printCardInfo();

        // 등급 업그레이드
        card.upgrade();  // BASIC → SILVER
        card.upgrade();  // SILVER → GOLD
        card.upgrade();  // GOLD → PLATINUM
        card.upgrade();  // 이미 최고 등급

        System.out.println("\n최종 상태:");
        card.printCardInfo();
    }

    static void test4_TierRecommendation() {
        System.out.println("\n### 테스트 4: 등급 추천 ###\n");

        int[] monthlySpending = {300000, 1000000, 3000000, 7000000};

        for (int spending : monthlySpending) {
            CardTier recommended = CardTier.recommendTier(spending);
            System.out.println("월 소비: " + String.format("%,d원", spending) +
                             " → 추천 등급: " + recommended.getKoreanName());
        }
    }
}
```

### 🎯 핵심 포인트

1. **계산 로직**: Enum에 비즈니스 로직(할인, 포인트 계산) 포함
2. **static 메서드**: recommendTier()로 등급 추천 로직
3. **상태 확인**: canUpgrade()로 업그레이드 가능 여부 확인
4. **풍부한 데이터**: 여러 타입의 필드로 복잡한 정보 표현

---

## 📦 실생활 비유 5: 주문 상태 (OrderStatus)

### 📖 비유 설명

온라인 쇼핑에서 주문은 여러 상태를 거칩니다: 주문 접수 → 결제 완료 → 배송 준비 → 배송 중 → 배송 완료. 각 상태는 특정 행동만 허용합니다.

### 💻 코드 구현

```java
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * 주문 상태 열거형
 */
enum OrderStatus {
    PENDING("주문 접수", "주문이 접수되었습니다.") {
        @Override
        public boolean canCancel() {
            return true;
        }

        @Override
        public OrderStatus next() {
            return CONFIRMED;
        }
    },
    CONFIRMED("결제 완료", "결제가 완료되었습니다.") {
        @Override
        public boolean canCancel() {
            return true;
        }

        @Override
        public OrderStatus next() {
            return PREPARING;
        }
    },
    PREPARING("배송 준비", "상품을 준비 중입니다.") {
        @Override
        public boolean canCancel() {
            return true;  // 배송 전까지는 취소 가능
        }

        @Override
        public OrderStatus next() {
            return SHIPPED;
        }
    },
    SHIPPED("배송 중", "상품이 배송 중입니다.") {
        @Override
        public boolean canCancel() {
            return false;  // 배송 시작 후에는 취소 불가
        }

        @Override
        public OrderStatus next() {
            return DELIVERED;
        }
    },
    DELIVERED("배송 완료", "배송이 완료되었습니다.") {
        @Override
        public boolean canCancel() {
            return false;
        }

        @Override
        public OrderStatus next() {
            throw new IllegalStateException("배송 완료는 최종 상태입니다.");
        }

        @Override
        public boolean canReturn() {
            return true;  // 배송 완료 후 반품 가능
        }
    },
    CANCELLED("주문 취소", "주문이 취소되었습니다.") {
        @Override
        public boolean canCancel() {
            return false;
        }

        @Override
        public OrderStatus next() {
            throw new IllegalStateException("취소된 주문은 진행할 수 없습니다.");
        }
    },
    RETURNED("반품 완료", "반품이 완료되었습니다.") {
        @Override
        public boolean canCancel() {
            return false;
        }

        @Override
        public OrderStatus next() {
            throw new IllegalStateException("반품 완료는 최종 상태입니다.");
        }
    };

    private final String koreanName;
    private final String message;

    OrderStatus(String koreanName, String message) {
        this.koreanName = koreanName;
        this.message = message;
    }

    public String getKoreanName() {
        return koreanName;
    }

    public String getMessage() {
        return message;
    }

    // 추상 메서드 - 각 상태별로 다르게 구현
    public abstract boolean canCancel();
    public abstract OrderStatus next();

    // 기본값 제공 (일부 상태만 오버라이드)
    public boolean canReturn() {
        return false;
    }

    // 진행 가능 여부
    public boolean canProgress() {
        return this != DELIVERED && this != CANCELLED && this != RETURNED;
    }

    // 상태 아이콘
    public String getIcon() {
        switch (this) {
            case PENDING: return "📝";
            case CONFIRMED: return "💳";
            case PREPARING: return "📦";
            case SHIPPED: return "🚚";
            case DELIVERED: return "✅";
            case CANCELLED: return "❌";
            case RETURNED: return "↩️";
            default: return "❓";
        }
    }
}

/**
 * 주문 클래스
 */
class Order {
    private String orderId;
    private String productName;
    private int price;
    private OrderStatus status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public Order(String orderId, String productName, int price) {
        this.orderId = orderId;
        this.productName = productName;
        this.price = price;
        this.status = OrderStatus.PENDING;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    // 주문 진행
    public void proceed() {
        if (!status.canProgress()) {
            System.out.println("⚠️  더 이상 진행할 수 없습니다. 현재 상태: " + status.getKoreanName());
            return;
        }

        OrderStatus oldStatus = status;
        try {
            status = status.next();
            updatedAt = LocalDateTime.now();

            System.out.println("\n" + status.getIcon() + " 주문 상태 변경");
            System.out.println(oldStatus.getKoreanName() + " → " + status.getKoreanName());
            System.out.println(status.getMessage());
        } catch (IllegalStateException e) {
            System.out.println("⚠️  " + e.getMessage());
        }
    }

    // 주문 취소
    public void cancel() {
        if (!status.canCancel()) {
            System.out.println("⚠️  이 상태에서는 취소할 수 없습니다. 현재 상태: " + status.getKoreanName());
            return;
        }

        OrderStatus oldStatus = status;
        status = OrderStatus.CANCELLED;
        updatedAt = LocalDateTime.now();

        System.out.println("\n❌ 주문 취소");
        System.out.println(oldStatus.getKoreanName() + " → " + status.getKoreanName());
        System.out.println(status.getMessage());
    }

    // 반품
    public void returnOrder() {
        if (!status.canReturn()) {
            System.out.println("⚠️  이 상태에서는 반품할 수 없습니다. 현재 상태: " + status.getKoreanName());
            return;
        }

        OrderStatus oldStatus = status;
        status = OrderStatus.RETURNED;
        updatedAt = LocalDateTime.now();

        System.out.println("\n↩️  주문 반품");
        System.out.println(oldStatus.getKoreanName() + " → " + status.getKoreanName());
        System.out.println(status.getMessage());
    }

    // 주문 정보 출력
    public void printOrderInfo() {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

        System.out.println("\n" + "=".repeat(60));
        System.out.println("주문 정보");
        System.out.println("=".repeat(60));
        System.out.println("주문 번호: " + orderId);
        System.out.println("상품명: " + productName);
        System.out.println("가격: " + String.format("%,d원", price));
        System.out.println("현재 상태: " + status.getIcon() + " " + status.getKoreanName());
        System.out.println("주문 시간: " + createdAt.format(formatter));
        System.out.println("최종 수정: " + updatedAt.format(formatter));
        System.out.println("취소 가능: " + (status.canCancel() ? "가능" : "불가능"));
        System.out.println("반품 가능: " + (status.canReturn() ? "가능" : "불가능"));
    }

    public OrderStatus getStatus() {
        return status;
    }
}
```

### 🧪 테스트 코드

```java
/**
 * 주문 상태 Enum 테스트
 */
public class OrderStatusTest {

    public static void main(String[] args) {

        System.out.println("=================================================");
        System.out.println("주문 상태 (OrderStatus) Enum 테스트");
        System.out.println("=================================================");

        // 테스트 1: 정상적인 주문 흐름
        test1_NormalOrderFlow();

        // 테스트 2: 주문 취소
        test2_OrderCancellation();

        // 테스트 3: 반품
        test3_OrderReturn();

        // 테스트 4: 잘못된 상태 전이
        test4_InvalidTransitions();
    }

    static void test1_NormalOrderFlow() {
        System.out.println("\n### 테스트 1: 정상적인 주문 흐름 ###");

        Order order = new Order("ORD-001", "노트북", 1500000);
        order.printOrderInfo();

        // 주문 진행: PENDING → CONFIRMED → PREPARING → SHIPPED → DELIVERED
        for (int i = 0; i < 4; i++) {
            sleep(500);
            order.proceed();
        }

        order.printOrderInfo();
    }

    static void test2_OrderCancellation() {
        System.out.println("\n\n### 테스트 2: 주문 취소 ###");

        // 시나리오 1: 배송 준비 중 취소 (가능)
        System.out.println("\n[시나리오 1] 배송 준비 중 취소");
        Order order1 = new Order("ORD-002", "마우스", 30000);
        order1.proceed();  // CONFIRMED
        order1.proceed();  // PREPARING
        order1.cancel();   // 취소 성공
        order1.printOrderInfo();

        // 시나리오 2: 배송 중 취소 시도 (불가능)
        System.out.println("\n[시나리오 2] 배송 중 취소 시도");
        Order order2 = new Order("ORD-003", "키보드", 80000);
        order2.proceed();  // CONFIRMED
        order2.proceed();  // PREPARING
        order2.proceed();  // SHIPPED
        order2.cancel();   // 취소 실패
    }

    static void test3_OrderReturn() {
        System.out.println("\n\n### 테스트 3: 반품 ###");

        Order order = new Order("ORD-004", "모니터", 300000);

        // 배송 완료까지 진행
        for (int i = 0; i < 4; i++) {
            order.proceed();
        }

        // 반품 시도
        order.returnOrder();
        order.printOrderInfo();
    }

    static void test4_InvalidTransitions() {
        System.out.println("\n\n### 테스트 4: 잘못된 상태 전이 ###");

        Order order = new Order("ORD-005", "헤드셋", 150000);

        // 배송 완료까지 진행
        for (int i = 0; i < 4; i++) {
            order.proceed();
        }

        // 배송 완료 후 더 진행 시도
        System.out.println("\n[시도 1] 배송 완료 후 더 진행");
        order.proceed();

        // 배송 완료 상태에서 취소 시도
        System.out.println("\n[시도 2] 배송 완료 상태에서 취소");
        order.cancel();
    }

    static void sleep(int millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
```

### 🎯 핵심 포인트

1. **상태 머신**: Enum으로 상태 전이 로직 구현
2. **검증 로직**: canCancel(), canReturn()으로 허용 여부 확인
3. **예외 처리**: 잘못된 상태 전이 시 명확한 에러 메시지
4. **실전 활용**: 주문, 결제, 배송 등 실무에서 자주 사용

---

## 🎯 Part 1 핵심 정리

### Enum의 장점

1. **타입 안정성**
   - 정해진 값만 사용 가능
   - 컴파일 타임에 오류 발견

2. **가독성**
   - 의미 있는 이름 사용
   - 코드의 의도가 명확

3. **유지보수성**
   - 한 곳에서 관리
   - 값 추가/변경이 쉬움

4. **기능 확장**
   - 필드와 메서드 추가 가능
   - 비즈니스 로직 포함 가능

### Enum 사용 시기

- 고정된 값들의 집합이 있을 때
- 상태, 타입, 카테고리를 표현할 때
- switch 문에서 사용할 때
- 싱글톤 패턴을 구현할 때

다음 Part 2에서는 **기업 사례**와 **주니어 개발자 시나리오**를 다루겠습니다! 🚀
