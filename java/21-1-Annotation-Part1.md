# 📝 Chapter 21-1: Annotation Part 1

## 🎯 학습 목표
- Annotation의 개념을 실생활 비유를 통해 이해합니다
- 기본 내장 Annotation의 사용법을 익힙니다
- Custom Annotation의 기본 개념을 학습합니다
- Annotation을 활용한 메타데이터 처리 방법을 이해합니다
- 실무에서 자주 사용되는 Annotation 패턴을 학습합니다

---

## 📚 실생활 비유로 이해하는 Annotation

Annotation은 코드에 붙이는 "메타데이터 라벨" 또는 "설명 스티커"입니다.
마치 물건에 붙이는 라벨처럼, 코드에 추가 정보를 제공하여 컴파일러나 프레임워크가 특별한 처리를 할 수 있게 합니다.

---

## 🏷️ 비유 1: @Override - 확인 스탬프/도장

### 실생활 비유
상사가 작성한 보고서 양식을 그대로 따라 작성했다는 **"확인 스탬프"**를 찍는 것과 같습니다.
- ✅ 양식에 맞게 작성했다면: 승인 스탬프 찍힘
- ❌ 양식과 다르게 작성했다면: 오류 발생 (다시 작성 필요)

### 코드로 이해하기

```java
// 📁 OverrideExample.java

class Animal {
    // 부모 클래스의 메서드
    public void makeSound() {
        System.out.println("동물이 소리를 냅니다");
    }

    public void eat() {
        System.out.println("동물이 먹습니다");
    }

    public void sleep() {
        System.out.println("동물이 잡니다");
    }
}

class Dog extends Animal {
    // ✅ 올바른 오버라이드 - @Override가 확인 스탬프 역할
    @Override
    public void makeSound() {
        System.out.println("멍멍!");
    }

    // ✅ 올바른 오버라이드
    @Override
    public void eat() {
        System.out.println("강아지가 사료를 먹습니다");
    }

    // ❌ 컴파일 에러 발생! (메서드 이름 오타)
    // @Override 어노테이션이 오류를 잡아냄
    /*
    @Override
    public void slep() {  // sleep이 아니라 slep - 오타!
        System.out.println("강아지가 잡니다");
    }
    */

    // ✅ 올바른 오버라이드
    @Override
    public void sleep() {
        System.out.println("강아지가 잡니다 💤");
    }
}

public class OverrideExample {
    public static void main(String[] args) {
        System.out.println("=== @Override 확인 스탬프 예제 ===\n");

        Dog dog = new Dog();

        System.out.println("🐕 강아지의 행동:");
        dog.makeSound();
        dog.eat();
        dog.sleep();

        System.out.println("\n💡 @Override의 역할:");
        System.out.println("1. 부모 메서드를 정확히 재정의했는지 확인");
        System.out.println("2. 오타나 실수로 인한 새로운 메서드 생성 방지");
        System.out.println("3. 코드 가독성 향상 - 이 메서드가 오버라이드임을 명시");
    }
}
```

**실행 결과:**
```
=== @Override 확인 스탬프 예제 ===

🐕 강아지의 행동:
멍멍!
강아지가 사료를 먹습니다
강아지가 잡니다 💤

💡 @Override의 역할:
1. 부모 메서드를 정확히 재정의했는지 확인
2. 오타나 실수로 인한 새로운 메서드 생성 방지
3. 코드 가독성 향상 - 이 메서드가 오버라이드임을 명시
```

### 핵심 정리
- `@Override`는 부모 클래스의 메서드를 올바르게 재정의했는지 **컴파일 타임에 검증**
- 메서드 이름 오타, 매개변수 타입 불일치 등을 사전에 방지
- 코드 의도를 명확히 전달 → 유지보수성 향상

---

## ⚠️ 비유 2: @Deprecated - 경고 라벨/스티커

### 실생활 비유
유통기한이 임박한 식품에 붙이는 **"할인" 또는 "곧 판매 중단"** 스티커와 같습니다.
- 📦 "이 제품은 곧 단종됩니다. 새로운 제품을 사용하세요!"
- ⚠️ 아직 사용은 가능하지만, 가능한 한 빨리 대체품으로 변경 권장

### 코드로 이해하기

```java
// 📁 DeprecatedExample.java

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Date;

class UserService {

    // ❌ 구버전 메서드 - Deprecated
    /**
     * @deprecated 이 메서드는 곧 제거될 예정입니다.
     *             대신 {@link #registerUserV2(String, String, int)}를 사용하세요.
     *             제거 예정 버전: v3.0
     */
    @Deprecated
    public void registerUser(String name, String email) {
        System.out.println("⚠️ [구버전] 사용자 등록: " + name);
        System.out.println("   이메일: " + email);
        // 간단한 로직만 처리
    }

    // ✅ 신버전 메서드 - 개선된 기능
    public void registerUserV2(String name, String email, int age) {
        System.out.println("✅ [신버전] 사용자 등록: " + name);
        System.out.println("   이메일: " + email);
        System.out.println("   나이: " + age);
        System.out.println("   등록 시각: " + LocalDateTime.now().format(
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        // 향상된 유효성 검증, 로깅, 보안 처리 등
    }

    // ❌ Java 구버전 Date 클래스 사용 - Deprecated
    @Deprecated
    public String getOldDateFormat() {
        Date now = new Date();
        return now.toString();
    }

    // ✅ Java 8+ LocalDateTime 사용 권장
    public String getNewDateFormat() {
        LocalDateTime now = LocalDateTime.now();
        return now.format(DateTimeFormatter.ofPattern("yyyy년 MM월 dd일 HH시 mm분 ss초"));
    }
}

class PaymentService {

    // ❌ Deprecated - 보안 취약점 존재
    /**
     * @deprecated 이 메서드는 보안 취약점이 있습니다.
     *             대신 processSecurePayment()를 사용하세요.
     */
    @Deprecated(since = "2.0", forRemoval = true)
    public boolean processPayment(String cardNumber) {
        System.out.println("⚠️ [경고] 안전하지 않은 결제 처리 중...");
        System.out.println("   카드번호: " + cardNumber);  // 평문 노출!
        return true;
    }

    // ✅ 신규 보안 강화 메서드
    public boolean processSecurePayment(String encryptedCardNumber) {
        System.out.println("✅ [안전] 암호화된 결제 처리 중...");
        System.out.println("   카드번호: " + maskCardNumber(encryptedCardNumber));
        return true;
    }

    private String maskCardNumber(String cardNumber) {
        if (cardNumber.length() < 4) return "****";
        return "****-****-****-" + cardNumber.substring(cardNumber.length() - 4);
    }
}

public class DeprecatedExample {
    public static void main(String[] args) {
        System.out.println("=== @Deprecated 경고 라벨 예제 ===\n");

        UserService userService = new UserService();
        PaymentService paymentService = new PaymentService();

        System.out.println("📋 Case 1: 구버전 vs 신버전 메서드\n");

        // ⚠️ Deprecated 메서드 사용 - IDE에서 취소선 표시됨
        userService.registerUser("홍길동", "hong@example.com");

        System.out.println("\n" + "─".repeat(50) + "\n");

        // ✅ 권장 메서드 사용
        userService.registerUserV2("김철수", "kim@example.com", 28);

        System.out.println("\n" + "=".repeat(50));
        System.out.println("📅 Case 2: 날짜 처리 - Old vs New\n");

        System.out.println("⚠️ 구버전 Date: " + userService.getOldDateFormat());
        System.out.println("✅ 신버전 LocalDateTime: " + userService.getNewDateFormat());

        System.out.println("\n" + "=".repeat(50));
        System.out.println("💳 Case 3: 결제 처리 - 보안 취약점 개선\n");

        // ⚠️ Deprecated - 보안 취약
        paymentService.processPayment("1234-5678-9012-3456");

        System.out.println("\n" + "─".repeat(50) + "\n");

        // ✅ 보안 강화 버전
        paymentService.processSecurePayment("1234-5678-9012-3456");

        System.out.println("\n" + "=".repeat(50));
        System.out.println("\n💡 @Deprecated 사용 이유:");
        System.out.println("1. 하위 호환성 유지 - 기존 코드가 즉시 깨지지 않음");
        System.out.println("2. 점진적 마이그레이션 - 개발자에게 변경 시간 제공");
        System.out.println("3. 명확한 의도 전달 - '이 코드는 곧 사라집니다'");
        System.out.println("4. IDE 지원 - 취소선, 경고 메시지로 시각적 표시");
    }
}
```

**실행 결과:**
```
=== @Deprecated 경고 라벨 예제 ===

📋 Case 1: 구버전 vs 신버전 메서드

⚠️ [구버전] 사용자 등록: 홍길동
   이메일: hong@example.com

──────────────────────────────────────────────────

✅ [신버전] 사용자 등록: 김철수
   이메일: kim@example.com
   나이: 28
   등록 시각: 2025-10-10 14:30:45

==================================================
📅 Case 2: 날짜 처리 - Old vs New

⚠️ 구버전 Date: Fri Oct 10 14:30:45 KST 2025
✅ 신버전 LocalDateTime: 2025년 10월 10일 14시 30분 45초

==================================================
💳 Case 3: 결제 처리 - 보안 취약점 개선

⚠️ [경고] 안전하지 않은 결제 처리 중...
   카드번호: 1234-5678-9012-3456

──────────────────────────────────────────────────

✅ [안전] 암호화된 결제 처리 중...
   카드번호: ****-****-****-3456

==================================================

💡 @Deprecated 사용 이유:
1. 하위 호환성 유지 - 기존 코드가 즉시 깨지지 않음
2. 점진적 마이그레이션 - 개발자에게 변경 시간 제공
3. 명확한 의도 전달 - '이 코드는 곧 사라집니다'
4. IDE 지원 - 취소선, 경고 메시지로 시각적 표시
```

### 핵심 정리
- `@Deprecated`는 "이 코드는 곧 제거되니 대안을 사용하세요"라는 경고
- `since` 속성: 언제부터 deprecated인지 명시
- `forRemoval = true`: 실제로 제거될 예정임을 강조
- JavaDoc에 대체 방법을 명확히 기술하는 것이 좋은 관례

---

## 🔕 비유 3: @SuppressWarnings - 알람 끄기/방해금지 모드

### 실생활 비유
스마트폰의 **"방해금지 모드"** 또는 **"알람 끄기"**와 같습니다.
- 📱 "이 시간 동안은 알림을 받지 않겠습니다"
- 🔕 필요한 경우에만 사용하고, 남용하면 중요한 알림을 놓칠 수 있음

### 코드로 이해하기

```java
// 📁 SuppressWarningsExample.java

import java.util.*;

class WarningDemo {

    // ⚠️ 경고 1: Unchecked cast (타입 안전성 경고)
    @SuppressWarnings("unchecked")
    public List<String> getLegacyList() {
        // 레거시 코드와의 호환성을 위해 Raw Type 사용
        List rawList = new ArrayList();  // 경고 발생하지만 @SuppressWarnings로 억제
        rawList.add("Item 1");
        rawList.add("Item 2");

        // 개발자가 타입 안전성을 직접 보장함
        return (List<String>) rawList;  // 경고 억제됨
    }

    // ⚠️ 경고 2: Unused variable (사용하지 않는 변수)
    @SuppressWarnings("unused")
    public void demonstrateUnusedWarning() {
        String unusedVariable = "이 변수는 사용되지 않지만 의도적입니다";
        int temporaryDebugCounter = 0;  // 디버깅용 - 나중에 사용 예정

        System.out.println("메서드 실행 완료");
    }

    // ⚠️ 경고 3: Deprecated (더 이상 사용하지 않는 메서드 호출)
    @SuppressWarnings("deprecation")
    public void callDeprecatedMethod() {
        Date date = new Date(2025, 10, 10);  // Date(int, int, int) is deprecated
        System.out.println("날짜: " + date);
    }

    // ⚠️ 여러 경고를 동시에 억제
    @SuppressWarnings({"unchecked", "rawtypes", "unused"})
    public Map getRawMap() {
        Map rawMap = new HashMap();  // Raw type 사용
        rawMap.put("key1", "value1");
        rawMap.put("key2", "value2");

        String unusedDebugInfo = "디버그 정보";

        return rawMap;
    }
}

class ResourceManager {

    // ✅ 올바른 사용: 레거시 라이브러리와의 통합
    @SuppressWarnings("unchecked")
    public <T> List<T> convertLegacyData(Object legacyData) {
        System.out.println("🔄 레거시 데이터 변환 중...");

        // 외부 레거시 시스템에서 받은 데이터
        // 타입 안전성은 우리가 직접 검증함
        if (legacyData instanceof List) {
            return (List<T>) legacyData;
        }

        return new ArrayList<>();
    }

    // ❌ 잘못된 사용: 모든 경고를 무분별하게 억제
    // @SuppressWarnings("all")  // 이렇게 하지 마세요!
    public void badPractice() {
        // 모든 경고를 억제하면 실제 문제를 놓칠 수 있습니다
    }

    // ✅ 올바른 사용: 특정 경고만 선택적으로 억제
    @SuppressWarnings("unchecked")
    public void goodPractice() {
        // unchecked 경고만 억제
        // 다른 경고는 여전히 표시됨
    }
}

public class SuppressWarningsExample {
    public static void main(String[] args) {
        System.out.println("=== @SuppressWarnings 방해금지 모드 예제 ===\n");

        WarningDemo demo = new WarningDemo();
        ResourceManager manager = new ResourceManager();

        System.out.println("📋 Case 1: Unchecked Cast 경고 억제");
        List<String> list = demo.getLegacyList();
        System.out.println("가져온 리스트: " + list);

        System.out.println("\n" + "─".repeat(50));
        System.out.println("📋 Case 2: Unused Variable 경고 억제\n");
        demo.demonstrateUnusedWarning();

        System.out.println("\n" + "─".repeat(50));
        System.out.println("📋 Case 3: Deprecation 경고 억제\n");
        demo.callDeprecatedMethod();

        System.out.println("\n" + "─".repeat(50));
        System.out.println("📋 Case 4: 여러 경고 동시 억제\n");
        Map rawMap = demo.getRawMap();
        System.out.println("가져온 맵: " + rawMap);

        System.out.println("\n" + "─".repeat(50));
        System.out.println("📋 Case 5: 레거시 데이터 변환\n");

        List<Object> legacyList = Arrays.asList("Data1", "Data2", "Data3");
        List<String> converted = manager.convertLegacyData(legacyList);
        System.out.println("변환된 데이터: " + converted);

        System.out.println("\n" + "=".repeat(50));
        System.out.println("\n💡 @SuppressWarnings 사용 가이드:");
        System.out.println("✅ 좋은 사용:");
        System.out.println("   - 레거시 코드와의 호환성을 위해");
        System.out.println("   - 개발자가 안전성을 직접 보장할 수 있을 때");
        System.out.println("   - 특정 경고만 선택적으로 억제");

        System.out.println("\n❌ 나쁜 사용:");
        System.out.println("   - @SuppressWarnings(\"all\") - 모든 경고 억제");
        System.out.println("   - 실제 문제를 감추기 위해 사용");
        System.out.println("   - 클래스 전체에 광범위하게 적용");

        System.out.println("\n🎯 주요 경고 타입:");
        System.out.println("   - unchecked: 타입 안전성 검증 안 됨");
        System.out.println("   - deprecation: deprecated API 사용");
        System.out.println("   - unused: 사용되지 않는 코드");
        System.out.println("   - rawtypes: Raw Type 사용");
        System.out.println("   - serial: Serializable 클래스에 serialVersionUID 없음");
    }
}
```

**실행 결과:**
```
=== @SuppressWarnings 방해금지 모드 예제 ===

📋 Case 1: Unchecked Cast 경고 억제
가져온 리스트: [Item 1, Item 2]

──────────────────────────────────────────────────
📋 Case 2: Unused Variable 경고 억제

메서드 실행 완료

──────────────────────────────────────────────────
📋 Case 3: Deprecation 경고 억제

날짜: Sat Nov 10 00:00:00 KST 3925

──────────────────────────────────────────────────
📋 Case 4: 여러 경고 동시 억제

가져온 맵: {key1=value1, key2=value2}

──────────────────────────────────────────────────
📋 Case 5: 레거시 데이터 변환

🔄 레거시 데이터 변환 중...
변환된 데이터: [Data1, Data2, Data3]

==================================================

💡 @SuppressWarnings 사용 가이드:
✅ 좋은 사용:
   - 레거시 코드와의 호환성을 위해
   - 개발자가 안전성을 직접 보장할 수 있을 때
   - 특정 경고만 선택적으로 억제

❌ 나쁜 사용:
   - @SuppressWarnings("all") - 모든 경고 억제
   - 실제 문제를 감추기 위해 사용
   - 클래스 전체에 광범위하게 적용

🎯 주요 경고 타입:
   - unchecked: 타입 안전성 검증 안 됨
   - deprecation: deprecated API 사용
   - unused: 사용되지 않는 코드
   - rawtypes: Raw Type 사용
   - serial: Serializable 클래스에 serialVersionUID 없음
```

### 핵심 정리
- `@SuppressWarnings`는 컴파일러 경고를 억제하는 어노테이션
- **최소한의 범위**에만 적용 (메서드 > 클래스, 특정 경고만)
- 경고를 억제하는 **이유를 주석으로 설명**하는 것이 좋은 관례
- `"all"`은 가능한 한 사용하지 말 것

---

## ✅ 비유 4: Custom Validation Annotation - 품질 검사 라벨

### 실생활 비유
공장에서 제품에 붙이는 **"품질 검사 완료" 스티커**와 같습니다.
- 📦 "이 제품은 다음 기준을 통과했습니다: 무게, 크기, 색상"
- ✅ 각 검사 항목마다 다른 라벨 (무게 검사, 크기 검사, 색상 검사)

### 코드로 이해하기

```java
// 📁 CustomValidationExample.java

import java.lang.annotation.*;
import java.lang.reflect.Field;
import java.util.regex.Pattern;

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 1️⃣ Custom Annotation 정의
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// ✅ NotNull: null이 아님을 검증
@Retention(RetentionPolicy.RUNTIME)  // 실행 시점에도 유지
@Target(ElementType.FIELD)           // 필드에만 적용 가능
@interface NotNull {
    String message() default "이 필드는 null일 수 없습니다";
}

// ✅ Email: 이메일 형식 검증
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Email {
    String message() default "올바른 이메일 형식이 아닙니다";
}

// ✅ MinLength: 최소 길이 검증
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface MinLength {
    int value();  // 최소 길이
    String message() default "최소 길이를 만족하지 않습니다";
}

// ✅ Range: 숫자 범위 검증
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Range {
    int min();
    int max();
    String message() default "값이 허용 범위를 벗어났습니다";
}

// ✅ PhoneNumber: 전화번호 형식 검증
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface PhoneNumber {
    String message() default "올바른 전화번호 형식이 아닙니다 (010-XXXX-XXXX)";
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 2️⃣ Validator: Annotation을 실제로 검증하는 클래스
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Validator {

    public static ValidationResult validate(Object obj) {
        ValidationResult result = new ValidationResult();
        Class<?> clazz = obj.getClass();

        // 모든 필드를 검사
        for (Field field : clazz.getDeclaredFields()) {
            field.setAccessible(true);  // private 필드 접근 가능하게

            try {
                Object value = field.get(obj);

                // @NotNull 검증
                if (field.isAnnotationPresent(NotNull.class)) {
                    if (value == null) {
                        NotNull annotation = field.getAnnotation(NotNull.class);
                        result.addError(field.getName(), annotation.message());
                    }
                }

                // @Email 검증
                if (field.isAnnotationPresent(Email.class)) {
                    if (value != null && !isValidEmail(value.toString())) {
                        Email annotation = field.getAnnotation(Email.class);
                        result.addError(field.getName(), annotation.message());
                    }
                }

                // @MinLength 검증
                if (field.isAnnotationPresent(MinLength.class)) {
                    MinLength annotation = field.getAnnotation(MinLength.class);
                    if (value != null && value.toString().length() < annotation.value()) {
                        result.addError(field.getName(),
                            annotation.message() + " (최소: " + annotation.value() + "자)");
                    }
                }

                // @Range 검증
                if (field.isAnnotationPresent(Range.class)) {
                    Range annotation = field.getAnnotation(Range.class);
                    if (value != null) {
                        int intValue = (Integer) value;
                        if (intValue < annotation.min() || intValue > annotation.max()) {
                            result.addError(field.getName(),
                                annotation.message() + " (" + annotation.min() + "~" + annotation.max() + ")");
                        }
                    }
                }

                // @PhoneNumber 검증
                if (field.isAnnotationPresent(PhoneNumber.class)) {
                    if (value != null && !isValidPhoneNumber(value.toString())) {
                        PhoneNumber annotation = field.getAnnotation(PhoneNumber.class);
                        result.addError(field.getName(), annotation.message());
                    }
                }

            } catch (IllegalAccessException e) {
                result.addError(field.getName(), "필드 접근 오류: " + e.getMessage());
            }
        }

        return result;
    }

    private static boolean isValidEmail(String email) {
        String emailRegex = "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$";
        return Pattern.matches(emailRegex, email);
    }

    private static boolean isValidPhoneNumber(String phone) {
        String phoneRegex = "^010-\\d{4}-\\d{4}$";
        return Pattern.matches(phoneRegex, phone);
    }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 3️⃣ ValidationResult: 검증 결과를 담는 클래스
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ValidationResult {
    private final java.util.Map<String, java.util.List<String>> errors = new java.util.HashMap<>();

    public void addError(String fieldName, String message) {
        errors.computeIfAbsent(fieldName, k -> new java.util.ArrayList<>()).add(message);
    }

    public boolean isValid() {
        return errors.isEmpty();
    }

    public void printErrors() {
        if (isValid()) {
            System.out.println("✅ 모든 검증 통과!");
            return;
        }

        System.out.println("❌ 검증 실패:");
        errors.forEach((field, messages) -> {
            System.out.println("  📌 " + field + ":");
            messages.forEach(msg -> System.out.println("     - " + msg));
        });
    }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 4️⃣ 실제 사용 예제: User 클래스에 Validation Annotation 적용
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class User {

    @NotNull
    @MinLength(2)
    private String name;

    @NotNull
    @Email
    private String email;

    @NotNull
    @Range(min = 0, max = 150)
    private Integer age;

    @NotNull
    @PhoneNumber
    private String phone;

    @MinLength(8)
    private String password;

    public User(String name, String email, Integer age, String phone, String password) {
        this.name = name;
        this.email = email;
        this.age = age;
        this.phone = phone;
        this.password = password;
    }

    @Override
    public String toString() {
        return String.format("User{name='%s', email='%s', age=%d, phone='%s'}",
                           name, email, age, phone);
    }
}

public class CustomValidationExample {
    public static void main(String[] args) {
        System.out.println("=== Custom Validation Annotation 품질 검사 예제 ===\n");

        // ✅ Case 1: 올바른 데이터
        System.out.println("📋 Case 1: 올바른 사용자 데이터");
        System.out.println("─".repeat(50));
        User validUser = new User(
            "김철수",
            "kim@example.com",
            28,
            "010-1234-5678",
            "password123"
        );
        System.out.println("사용자 정보: " + validUser);
        ValidationResult result1 = Validator.validate(validUser);
        result1.printErrors();

        // ❌ Case 2: 이름이 너무 짧음
        System.out.println("\n" + "=".repeat(50));
        System.out.println("📋 Case 2: 이름이 너무 짧은 경우\n");
        User invalidUser1 = new User(
            "김",  // 1글자 - MinLength(2) 위반
            "test@example.com",
            25,
            "010-9999-8888",
            "pass1234"
        );
        ValidationResult result2 = Validator.validate(invalidUser1);
        result2.printErrors();

        // ❌ Case 3: 이메일 형식 오류
        System.out.println("\n" + "=".repeat(50));
        System.out.println("📋 Case 3: 잘못된 이메일 형식\n");
        User invalidUser2 = new User(
            "이영희",
            "invalid-email",  // @ 없음 - Email 형식 위반
            30,
            "010-5555-6666",
            "password"
        );
        ValidationResult result3 = Validator.validate(invalidUser2);
        result3.printErrors();

        // ❌ Case 4: 나이 범위 초과
        System.out.println("\n" + "=".repeat(50));
        System.out.println("📋 Case 4: 나이가 허용 범위를 벗어난 경우\n");
        User invalidUser3 = new User(
            "박민수",
            "park@example.com",
            200,  // 0~150 범위 초과
            "010-7777-8888",
            "secure123"
        );
        ValidationResult result4 = Validator.validate(invalidUser3);
        result4.printErrors();

        // ❌ Case 5: 전화번호 형식 오류
        System.out.println("\n" + "=".repeat(50));
        System.out.println("📋 Case 5: 잘못된 전화번호 형식\n");
        User invalidUser4 = new User(
            "최지훈",
            "choi@example.com",
            35,
            "01012345678",  // - 없음 - PhoneNumber 형식 위반
            "mypassword"
        );
        ValidationResult result5 = Validator.validate(invalidUser4);
        result5.printErrors();

        // ❌ Case 6: 여러 필드 동시 오류
        System.out.println("\n" + "=".repeat(50));
        System.out.println("📋 Case 6: 여러 필드에 오류가 있는 경우\n");
        User invalidUser5 = new User(
            "강",           // 이름 짧음
            "bad-email",   // 이메일 형식 오류
            -5,            // 나이 범위 오류
            "123-456",     // 전화번호 형식 오류
            "short"        // 비밀번호 짧음
        );
        ValidationResult result6 = Validator.validate(invalidUser5);
        result6.printErrors();

        // ❌ Case 7: null 값
        System.out.println("\n" + "=".repeat(50));
        System.out.println("📋 Case 7: null 값이 있는 경우\n");
        User invalidUser6 = new User(
            null,   // @NotNull 위반
            null,   // @NotNull 위반
            null,   // @NotNull 위반
            null,   // @NotNull 위반
            "password"
        );
        ValidationResult result7 = Validator.validate(invalidUser6);
        result7.printErrors();

        System.out.println("\n" + "=".repeat(50));
        System.out.println("\n💡 Custom Annotation의 장점:");
        System.out.println("✅ 코드 재사용성 - 검증 로직을 한 곳에 정의");
        System.out.println("✅ 가독성 향상 - 필드 선언부에서 제약사항 명확히 표시");
        System.out.println("✅ 유지보수 용이 - 검증 규칙 변경 시 Annotation만 수정");
        System.out.println("✅ 선언적 프로그래밍 - '어떻게'보다 '무엇을' 강조");

        System.out.println("\n🎯 실무 활용:");
        System.out.println("- Spring Framework: @Valid, @Validated");
        System.out.println("- Hibernate Validator: @NotBlank, @Size, @Pattern");
        System.out.println("- JPA: @Entity, @Column, @Id");
        System.out.println("- JSON 처리: @JsonProperty, @JsonIgnore");
    }
}
```

**실행 결과:**
```
=== Custom Validation Annotation 품질 검사 예제 ===

📋 Case 1: 올바른 사용자 데이터
──────────────────────────────────────────────────
사용자 정보: User{name='김철수', email='kim@example.com', age=28, phone='010-1234-5678'}
✅ 모든 검증 통과!

==================================================
📋 Case 2: 이름이 너무 짧은 경우

❌ 검증 실패:
  📌 name:
     - 최소 길이를 만족하지 않습니다 (최소: 2자)

==================================================
📋 Case 3: 잘못된 이메일 형식

❌ 검증 실패:
  📌 email:
     - 올바른 이메일 형식이 아닙니다

==================================================
📋 Case 4: 나이가 허용 범위를 벗어난 경우

❌ 검증 실패:
  📌 age:
     - 값이 허용 범위를 벗어났습니다 (0~150)

==================================================
📋 Case 5: 잘못된 전화번호 형식

❌ 검증 실패:
  📌 phone:
     - 올바른 전화번호 형식이 아닙니다 (010-XXXX-XXXX)

==================================================
📋 Case 6: 여러 필드에 오류가 있는 경우

❌ 검증 실패:
  📌 password:
     - 최소 길이를 만족하지 않습니다 (최소: 8자)
  📌 phone:
     - 올바른 전화번호 형식이 아닙니다 (010-XXXX-XXXX)
  📌 name:
     - 최소 길이를 만족하지 않습니다 (최소: 2자)
  📌 email:
     - 올바른 이메일 형식이 아닙니다
  📌 age:
     - 값이 허용 범위를 벗어났습니다 (0~150)

==================================================
📋 Case 7: null 값이 있는 경우

❌ 검증 실패:
  📌 phone:
     - 이 필드는 null일 수 없습니다
  📌 name:
     - 이 필드는 null일 수 없습니다
  📌 email:
     - 이 필드는 null일 수 없습니다
  📌 age:
     - 이 필드는 null일 수 없습니다

==================================================

💡 Custom Annotation의 장점:
✅ 코드 재사용성 - 검증 로직을 한 곳에 정의
✅ 가독성 향상 - 필드 선언부에서 제약사항 명확히 표시
✅ 유지보수 용이 - 검증 규칙 변경 시 Annotation만 수정
✅ 선언적 프로그래밍 - '어떻게'보다 '무엇을' 강조

🎯 실무 활용:
- Spring Framework: @Valid, @Validated
- Hibernate Validator: @NotBlank, @Size, @Pattern
- JPA: @Entity, @Column, @Id
- JSON 처리: @JsonProperty, @JsonIgnore
```

### 핵심 정리
- Custom Annotation은 메타데이터를 정의하고 런타임에 리플렉션으로 처리
- `@Retention`: 어노테이션 정보를 언제까지 유지할지 (SOURCE/CLASS/RUNTIME)
- `@Target`: 어노테이션을 어디에 적용할 수 있는지 (FIELD/METHOD/TYPE 등)
- 실무에서는 Spring, Hibernate 등 프레임워크의 Annotation을 많이 활용

---

## 🏷️ 비유 5: @JsonProperty / @Column - 이름표/명찰

### 실생활 비유
국제 회의에서 참가자가 다는 **"이름표/명찰"**과 같습니다.
- 🏷️ 실제 이름: "김철수" → 명찰: "Chulsoo Kim (KOR)"
- 🌍 같은 사람이지만 상황에 따라 다른 이름으로 표시
- 📝 내부 이름과 외부에 보여지는 이름을 다르게 설정

### 코드로 이해하기

```java
// 📁 MappingAnnotationExample.java

import java.lang.annotation.*;
import java.lang.reflect.Field;
import java.util.*;

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 1️⃣ Custom Mapping Annotation 정의
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// JSON 직렬화 시 필드 이름을 다르게 매핑
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface JsonProperty {
    String value();  // JSON에서 사용할 키 이름
}

// 데이터베이스 컬럼 매핑
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Column {
    String name();        // DB 컬럼 이름
    int length() default 255;
    boolean nullable() default true;
}

// JSON 직렬화에서 제외
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface JsonIgnore {
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 2️⃣ Simple JSON Serializer (Annotation 기반)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SimpleJsonSerializer {

    public static String toJson(Object obj) {
        StringBuilder json = new StringBuilder("{");
        Class<?> clazz = obj.getClass();
        Field[] fields = clazz.getDeclaredFields();

        List<String> jsonFields = new ArrayList<>();

        for (Field field : fields) {
            field.setAccessible(true);

            // @JsonIgnore가 있으면 제외
            if (field.isAnnotationPresent(JsonIgnore.class)) {
                continue;
            }

            try {
                Object value = field.get(obj);

                // JSON 키 이름 결정
                String jsonKey;
                if (field.isAnnotationPresent(JsonProperty.class)) {
                    // @JsonProperty 있으면 그 값 사용
                    jsonKey = field.getAnnotation(JsonProperty.class).value();
                } else {
                    // 없으면 필드 이름 그대로 사용
                    jsonKey = field.getName();
                }

                // JSON 값 처리
                String jsonValue;
                if (value == null) {
                    jsonValue = "null";
                } else if (value instanceof String) {
                    jsonValue = "\"" + value + "\"";
                } else if (value instanceof Number || value instanceof Boolean) {
                    jsonValue = value.toString();
                } else {
                    jsonValue = "\"" + value.toString() + "\"";
                }

                jsonFields.add("\"" + jsonKey + "\": " + jsonValue);

            } catch (IllegalAccessException e) {
                e.printStackTrace();
            }
        }

        json.append(String.join(", ", jsonFields));
        json.append("}");

        return json.toString();
    }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 3️⃣ Simple SQL Generator (Annotation 기반)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SimpleSqlGenerator {

    public static String generateCreateTable(Class<?> clazz) {
        StringBuilder sql = new StringBuilder();
        sql.append("CREATE TABLE ").append(toSnakeCase(clazz.getSimpleName())).append(" (\n");

        List<String> columns = new ArrayList<>();

        for (Field field : clazz.getDeclaredFields()) {
            if (field.isAnnotationPresent(Column.class)) {
                Column column = field.getAnnotation(Column.class);

                StringBuilder columnDef = new StringBuilder();
                columnDef.append("  ").append(column.name());

                // 타입 추론
                if (field.getType() == String.class) {
                    columnDef.append(" VARCHAR(").append(column.length()).append(")");
                } else if (field.getType() == Integer.class || field.getType() == int.class) {
                    columnDef.append(" INT");
                } else if (field.getType() == Boolean.class || field.getType() == boolean.class) {
                    columnDef.append(" BOOLEAN");
                }

                // NULL 가능 여부
                if (!column.nullable()) {
                    columnDef.append(" NOT NULL");
                }

                columns.add(columnDef.toString());
            }
        }

        sql.append(String.join(",\n", columns));
        sql.append("\n);");

        return sql.toString();
    }

    private static String toSnakeCase(String camelCase) {
        return camelCase.replaceAll("([a-z])([A-Z])", "$1_$2").toLowerCase();
    }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 4️⃣ 예제: Product 클래스 (여러 Annotation 조합)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Product {

    // Java 필드명: productId
    // JSON: "id"
    // DB: "product_id"
    @JsonProperty("id")
    @Column(name = "product_id", nullable = false)
    private Integer productId;

    // Java 필드명: productName
    // JSON: "name"
    // DB: "product_name"
    @JsonProperty("name")
    @Column(name = "product_name", length = 100, nullable = false)
    private String productName;

    // Java 필드명: price
    // JSON: "price"
    // DB: "price"
    @JsonProperty("price")
    @Column(name = "price", nullable = false)
    private Integer price;

    // Java 필드명: stockQuantity
    // JSON: "stock"
    // DB: "stock_qty"
    @JsonProperty("stock")
    @Column(name = "stock_qty", nullable = false)
    private Integer stockQuantity;

    // Java 필드명: internalCode
    // JSON: 제외 (@JsonIgnore)
    // DB: "internal_code"
    @JsonIgnore
    @Column(name = "internal_code", length = 50)
    private String internalCode;

    // Java 필드명: isAvailable
    // JSON: "available"
    // DB: "is_available"
    @JsonProperty("available")
    @Column(name = "is_available", nullable = false)
    private Boolean isAvailable;

    public Product(Integer productId, String productName, Integer price,
                   Integer stockQuantity, String internalCode, Boolean isAvailable) {
        this.productId = productId;
        this.productName = productName;
        this.price = price;
        this.stockQuantity = stockQuantity;
        this.internalCode = internalCode;
        this.isAvailable = isAvailable;
    }
}

class UserAccount {

    @JsonProperty("user_id")
    @Column(name = "user_id", nullable = false)
    private Integer userId;

    @JsonProperty("username")
    @Column(name = "username", length = 50, nullable = false)
    private String username;

    @JsonProperty("email")
    @Column(name = "email", length = 100, nullable = false)
    private String email;

    // 비밀번호는 JSON으로 내보내지 않음
    @JsonIgnore
    @Column(name = "password_hash", length = 255, nullable = false)
    private String passwordHash;

    @JsonProperty("is_active")
    @Column(name = "is_active", nullable = false)
    private Boolean isActive;

    public UserAccount(Integer userId, String username, String email,
                      String passwordHash, Boolean isActive) {
        this.userId = userId;
        this.username = username;
        this.email = email;
        this.passwordHash = passwordHash;
        this.isActive = isActive;
    }
}

public class MappingAnnotationExample {
    public static void main(String[] args) {
        System.out.println("=== Mapping Annotation 이름표/명찰 예제 ===\n");

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // Product 예제
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        Product product = new Product(
            1001,
            "무선 이어폰",
            89000,
            150,
            "INTERNAL-WE-001",
            true
        );

        System.out.println("📦 Product 객체");
        System.out.println("=".repeat(50));

        // JSON 직렬화
        System.out.println("\n🔹 JSON 형식 (API 응답):");
        System.out.println("─".repeat(50));
        String productJson = SimpleJsonSerializer.toJson(product);
        System.out.println(productJson);

        System.out.println("\n💡 주목할 점:");
        System.out.println("  - productId → \"id\"");
        System.out.println("  - productName → \"name\"");
        System.out.println("  - stockQuantity → \"stock\"");
        System.out.println("  - internalCode → JSON에서 제외됨 (@JsonIgnore)");

        // SQL 생성
        System.out.println("\n" + "=".repeat(50));
        System.out.println("🔹 SQL CREATE TABLE 문:");
        System.out.println("─".repeat(50));
        String createTableSql = SimpleSqlGenerator.generateCreateTable(Product.class);
        System.out.println(createTableSql);

        System.out.println("\n💡 주목할 점:");
        System.out.println("  - Java 필드명: productId → DB 컬럼명: product_id");
        System.out.println("  - Java 필드명: stockQuantity → DB 컬럼명: stock_qty");
        System.out.println("  - @Column의 length, nullable 속성 반영");

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // UserAccount 예제
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        System.out.println("\n" + "=".repeat(50));
        System.out.println("=".repeat(50));

        UserAccount user = new UserAccount(
            2001,
            "chulsoo_kim",
            "chulsoo@example.com",
            "$2a$10$HASH_VALUE_HERE",  // 해시된 비밀번호
            true
        );

        System.out.println("\n👤 UserAccount 객체");
        System.out.println("=".repeat(50));

        // JSON 직렬화
        System.out.println("\n🔹 JSON 형식 (API 응답):");
        System.out.println("─".repeat(50));
        String userJson = SimpleJsonSerializer.toJson(user);
        System.out.println(userJson);

        System.out.println("\n💡 주목할 점:");
        System.out.println("  - userId → \"user_id\"");
        System.out.println("  - isActive → \"is_active\"");
        System.out.println("  - passwordHash → JSON에서 완전히 제외됨 (보안!)");

        // SQL 생성
        System.out.println("\n" + "=".repeat(50));
        System.out.println("🔹 SQL CREATE TABLE 문:");
        System.out.println("─".repeat(50));
        String createUserTableSql = SimpleSqlGenerator.generateCreateTable(UserAccount.class);
        System.out.println(createUserTableSql);

        System.out.println("\n" + "=".repeat(50));
        System.out.println("=".repeat(50));

        System.out.println("\n🎯 Mapping Annotation의 핵심 가치:");
        System.out.println("\n1️⃣ 관심사 분리 (Separation of Concerns)");
        System.out.println("   - Java 코드: camelCase (productName)");
        System.out.println("   - JSON: snake_case 또는 약어 (product_name, name)");
        System.out.println("   - DB: snake_case (product_name)");
        System.out.println("   → 각 레이어의 명명 규칙을 독립적으로 유지!");

        System.out.println("\n2️⃣ 보안 강화");
        System.out.println("   - @JsonIgnore로 민감 정보 제외");
        System.out.println("   - API 응답에서 비밀번호, 내부 코드 등 숨김");

        System.out.println("\n3️⃣ 유연한 API 설계");
        System.out.println("   - 클라이언트에게 짧고 명확한 키 제공");
        System.out.println("   - 버전별로 다른 필드명 제공 가능");

        System.out.println("\n4️⃣ 데이터베이스 독립성");
        System.out.println("   - Java 코드 변경 없이 DB 스키마 수정 가능");
        System.out.println("   - 레거시 DB와의 통합 용이");

        System.out.println("\n" + "=".repeat(50));
        System.out.println("\n🌟 실무에서의 활용:");
        System.out.println("  - Jackson: @JsonProperty, @JsonIgnore, @JsonFormat");
        System.out.println("  - Gson: @SerializedName, @Expose");
        System.out.println("  - JPA/Hibernate: @Column, @Table, @Id, @GeneratedValue");
        System.out.println("  - MyBatis: @Select, @Insert, @Update, @Delete");
    }
}
```

**실행 결과:**
```
=== Mapping Annotation 이름표/명찰 예제 ===

📦 Product 객체
==================================================

🔹 JSON 형식 (API 응답):
──────────────────────────────────────────────────
{"id": 1001, "name": "무선 이어폰", "price": 89000, "stock": 150, "available": true}

💡 주목할 점:
  - productId → "id"
  - productName → "name"
  - stockQuantity → "stock"
  - internalCode → JSON에서 제외됨 (@JsonIgnore)

==================================================
🔹 SQL CREATE TABLE 문:
──────────────────────────────────────────────────
CREATE TABLE product (
  product_id INT NOT NULL,
  product_name VARCHAR(100) NOT NULL,
  price INT NOT NULL,
  stock_qty INT NOT NULL,
  internal_code VARCHAR(50),
  is_available BOOLEAN NOT NULL
);

💡 주목할 점:
  - Java 필드명: productId → DB 컬럼명: product_id
  - Java 필드명: stockQuantity → DB 컬럼명: stock_qty
  - @Column의 length, nullable 속성 반영

==================================================
==================================================

👤 UserAccount 객체
==================================================

🔹 JSON 형식 (API 응답):
──────────────────────────────────────────────────
{"user_id": 2001, "username": "chulsoo_kim", "email": "chulsoo@example.com", "is_active": true}

💡 주목할 점:
  - userId → "user_id"
  - isActive → "is_active"
  - passwordHash → JSON에서 완전히 제외됨 (보안!)

==================================================
🔹 SQL CREATE TABLE 문:
──────────────────────────────────────────────────
CREATE TABLE user_account (
  user_id INT NOT NULL,
  username VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  is_active BOOLEAN NOT NULL
);

==================================================
==================================================

🎯 Mapping Annotation의 핵심 가치:

1️⃣ 관심사 분리 (Separation of Concerns)
   - Java 코드: camelCase (productName)
   - JSON: snake_case 또는 약어 (product_name, name)
   - DB: snake_case (product_name)
   → 각 레이어의 명명 규칙을 독립적으로 유지!

2️⃣ 보안 강화
   - @JsonIgnore로 민감 정보 제외
   - API 응답에서 비밀번호, 내부 코드 등 숨김

3️⃣ 유연한 API 설계
   - 클라이언트에게 짧고 명확한 키 제공
   - 버전별로 다른 필드명 제공 가능

4️⃣ 데이터베이스 독립성
   - Java 코드 변경 없이 DB 스키마 수정 가능
   - 레거시 DB와의 통합 용이

==================================================

🌟 실무에서의 활용:
  - Jackson: @JsonProperty, @JsonIgnore, @JsonFormat
  - Gson: @SerializedName, @Expose
  - JPA/Hibernate: @Column, @Table, @Id, @GeneratedValue
  - MyBatis: @Select, @Insert, @Update, @Delete
```

### 핵심 정리
- Mapping Annotation은 **하나의 필드를 여러 이름으로 표현**
- `@JsonProperty`: JSON 직렬화 시 필드 이름 변경
- `@Column`: 데이터베이스 컬럼 매핑
- `@JsonIgnore`: 민감 정보를 외부에 노출하지 않음
- 실무에서는 Jackson, JPA 등의 라이브러리가 이런 Annotation을 제공

---

## 🎓 전체 요약

### Annotation이란?
- 코드에 붙이는 **메타데이터 라벨/스티커**
- 컴파일러, 프레임워크, 개발 도구가 특별한 처리를 하도록 지시
- `@` 기호로 시작

### 주요 내장 Annotation
1. **@Override**: 부모 메서드를 올바르게 재정의했는지 확인
2. **@Deprecated**: 더 이상 사용하지 않을 코드에 경고 표시
3. **@SuppressWarnings**: 컴파일러 경고를 억제

### Custom Annotation
4. **Validation Annotation** (@NotNull, @Email 등): 데이터 검증
5. **Mapping Annotation** (@JsonProperty, @Column 등): 필드 이름 매핑

### Annotation의 핵심 요소
- **@Retention**: SOURCE (소스코드만) / CLASS (컴파일까지) / RUNTIME (실행 시점까지)
- **@Target**: TYPE (클래스) / FIELD (필드) / METHOD (메서드) / PARAMETER (파라미터) 등

### 실무 활용
- **Spring**: @Component, @Service, @Repository, @Controller, @Autowired
- **JPA**: @Entity, @Table, @Id, @Column, @OneToMany
- **Jackson**: @JsonProperty, @JsonIgnore, @JsonFormat
- **Validation**: @NotNull, @Size, @Email, @Pattern

---

## 💡 다음 단계
- **Part 2**: 기업 사례 연구 + 주니어 개발자 시나리오
- **Part 3**: 실전 프로젝트 - Custom Annotation 기반 Validation Framework 구축

---

**📌 핵심 기억 포인트**
1. Annotation은 코드의 "메타데이터"
2. @Override로 오버라이드 실수 방지
3. @Deprecated로 점진적 마이그레이션 지원
4. @SuppressWarnings는 신중하게 사용
5. Custom Annotation으로 선언적 프로그래밍 구현
