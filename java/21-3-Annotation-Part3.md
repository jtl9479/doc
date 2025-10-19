# 📝 Chapter 21-3: Annotation Part 3

## 🎯 학습 목표
- Custom Annotation 기반 Validation Framework를 직접 구축합니다
- 실무에서 사용할 수 있는 수준의 프로젝트를 완성합니다
- Annotation, Reflection, Design Pattern을 종합적으로 활용합니다
- FAQ와 면접 질문을 통해 Annotation 개념을 완전히 마스터합니다

---

## 🚀 실전 프로젝트: Custom Validation Framework

### 프로젝트 개요
**프로젝트명**: SmartValidator - Custom Annotation 기반 검증 프레임워크
**목표**: Spring의 Validation 프레임워크처럼 선언적으로 데이터를 검증하는 시스템 구축
**기술 스택**: Java Annotation, Reflection, Regex, Design Patterns

### 주요 기능
1. ✅ 다양한 Validation Annotation 제공 (@NotNull, @Email, @Range, @Pattern 등)
2. ✅ 커스텀 에러 메시지 지원
3. ✅ Nested Object 검증
4. ✅ 그룹 검증 (Group Validation)
5. ✅ 검증 결과 리포팅

---

## 💻 전체 코드

```java
// 📁 SmartValidatorFramework.java

import java.lang.annotation.*;
import java.lang.reflect.Field;
import java.util.*;
import java.util.regex.Pattern;

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 1️⃣ Validation Annotations 정의
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/**
 * null 값을 허용하지 않음
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface NotNull {
    String message() default "이 필드는 null일 수 없습니다";
    Class<?>[] groups() default {};
}

/**
 * 빈 문자열을 허용하지 않음 (null 또는 공백)
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface NotBlank {
    String message() default "이 필드는 비어있을 수 없습니다";
    Class<?>[] groups() default {};
}

/**
 * 이메일 형식 검증
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Email {
    String message() default "올바른 이메일 형식이 아닙니다";
    Class<?>[] groups() default {};
}

/**
 * 최소 길이 검증
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface MinLength {
    int value();
    String message() default "최소 길이를 만족하지 않습니다";
    Class<?>[] groups() default {};
}

/**
 * 최대 길이 검증
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface MaxLength {
    int value();
    String message() default "최대 길이를 초과했습니다";
    Class<?>[] groups() default {};
}

/**
 * 숫자 범위 검증
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Range {
    int min() default Integer.MIN_VALUE;
    int max() default Integer.MAX_VALUE;
    String message() default "값이 허용 범위를 벗어났습니다";
    Class<?>[] groups() default {};
}

/**
 * 정규식 패턴 검증
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface PatternMatch {
    String regexp();
    String message() default "패턴과 일치하지 않습니다";
    Class<?>[] groups() default {};
}

/**
 * 한국 전화번호 형식 검증
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface PhoneNumber {
    String message() default "올바른 전화번호 형식이 아닙니다 (010-XXXX-XXXX)";
    Class<?>[] groups() default {};
}

/**
 * URL 형식 검증
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface URL {
    String message() default "올바른 URL 형식이 아닙니다";
    Class<?>[] groups() default {};
}

/**
 * Nested Object 검증
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Valid {
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 2️⃣ Validation Groups (그룹 검증)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/**
 * 생성 시 검증 그룹
 */
interface CreateGroup {}

/**
 * 수정 시 검증 그룹
 */
interface UpdateGroup {}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 3️⃣ ValidationError: 개별 검증 오류
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ValidationError {
    private final String fieldName;
    private final Object rejectedValue;
    private final String message;

    public ValidationError(String fieldName, Object rejectedValue, String message) {
        this.fieldName = fieldName;
        this.rejectedValue = rejectedValue;
        this.message = message;
    }

    public String getFieldName() { return fieldName; }
    public Object getRejectedValue() { return rejectedValue; }
    public String getMessage() { return message; }

    @Override
    public String toString() {
        return String.format("[%s] %s (입력값: %s)",
                           fieldName, message, rejectedValue);
    }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 4️⃣ ValidationResult: 전체 검증 결과
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ValidationResult {
    private final List<ValidationError> errors = new ArrayList<>();

    public void addError(ValidationError error) {
        errors.add(error);
    }

    public void addError(String fieldName, Object value, String message) {
        errors.add(new ValidationError(fieldName, value, message));
    }

    public boolean isValid() {
        return errors.isEmpty();
    }

    public List<ValidationError> getErrors() {
        return new ArrayList<>(errors);
    }

    public int getErrorCount() {
        return errors.size();
    }

    public Map<String, List<String>> getErrorsByField() {
        Map<String, List<String>> errorMap = new HashMap<>();
        for (ValidationError error : errors) {
            errorMap.computeIfAbsent(error.getFieldName(), k -> new ArrayList<>())
                   .add(error.getMessage());
        }
        return errorMap;
    }

    public void printErrors() {
        if (isValid()) {
            System.out.println("✅ 모든 검증 통과!");
            return;
        }

        System.out.println("❌ 검증 실패 (" + getErrorCount() + "개 오류):");
        for (ValidationError error : errors) {
            System.out.println("  • " + error);
        }
    }

    public void printSummary() {
        if (isValid()) {
            System.out.println("✅ 검증 성공");
            return;
        }

        System.out.println("❌ 검증 실패:");
        Map<String, List<String>> errorsByField = getErrorsByField();
        errorsByField.forEach((field, messages) -> {
            System.out.println("  📌 " + field + ":");
            messages.forEach(msg -> System.out.println("     - " + msg));
        });
    }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 5️⃣ SmartValidator: 핵심 검증 엔진
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SmartValidator {

    /**
     * 객체 검증 (기본)
     */
    public static ValidationResult validate(Object obj) {
        return validate(obj, (Class<?>) null);
    }

    /**
     * 객체 검증 (그룹 지정)
     */
    public static ValidationResult validate(Object obj, Class<?> group) {
        ValidationResult result = new ValidationResult();
        validateObject(obj, "", result, group);
        return result;
    }

    private static void validateObject(Object obj, String prefix, ValidationResult result, Class<?> group) {
        if (obj == null) {
            return;
        }

        Class<?> clazz = obj.getClass();

        for (Field field : clazz.getDeclaredFields()) {
            field.setAccessible(true);

            try {
                Object value = field.get(obj);
                String fieldName = prefix.isEmpty() ? field.getName() : prefix + "." + field.getName();

                // @NotNull 검증
                if (field.isAnnotationPresent(NotNull.class)) {
                    NotNull annotation = field.getAnnotation(NotNull.class);
                    if (shouldValidate(annotation.groups(), group)) {
                        if (value == null) {
                            result.addError(fieldName, value, annotation.message());
                        }
                    }
                }

                if (value == null) continue;  // 나머지 검증은 null이 아닐 때만

                // @NotBlank 검증
                if (field.isAnnotationPresent(NotBlank.class)) {
                    NotBlank annotation = field.getAnnotation(NotBlank.class);
                    if (shouldValidate(annotation.groups(), group)) {
                        if (value.toString().trim().isEmpty()) {
                            result.addError(fieldName, value, annotation.message());
                        }
                    }
                }

                // @Email 검증
                if (field.isAnnotationPresent(Email.class)) {
                    Email annotation = field.getAnnotation(Email.class);
                    if (shouldValidate(annotation.groups(), group)) {
                        if (!isValidEmail(value.toString())) {
                            result.addError(fieldName, value, annotation.message());
                        }
                    }
                }

                // @MinLength 검증
                if (field.isAnnotationPresent(MinLength.class)) {
                    MinLength annotation = field.getAnnotation(MinLength.class);
                    if (shouldValidate(annotation.groups(), group)) {
                        if (value.toString().length() < annotation.value()) {
                            result.addError(fieldName, value,
                                annotation.message() + " (최소: " + annotation.value() + "자)");
                        }
                    }
                }

                // @MaxLength 검증
                if (field.isAnnotationPresent(MaxLength.class)) {
                    MaxLength annotation = field.getAnnotation(MaxLength.class);
                    if (shouldValidate(annotation.groups(), group)) {
                        if (value.toString().length() > annotation.value()) {
                            result.addError(fieldName, value,
                                annotation.message() + " (최대: " + annotation.value() + "자)");
                        }
                    }
                }

                // @Range 검증
                if (field.isAnnotationPresent(Range.class)) {
                    Range annotation = field.getAnnotation(Range.class);
                    if (shouldValidate(annotation.groups(), group)) {
                        if (value instanceof Number) {
                            int intValue = ((Number) value).intValue();
                            if (intValue < annotation.min() || intValue > annotation.max()) {
                                result.addError(fieldName, value,
                                    annotation.message() + " (" + annotation.min() + "~" + annotation.max() + ")");
                            }
                        }
                    }
                }

                // @PatternMatch 검증
                if (field.isAnnotationPresent(PatternMatch.class)) {
                    PatternMatch annotation = field.getAnnotation(PatternMatch.class);
                    if (shouldValidate(annotation.groups(), group)) {
                        if (!Pattern.matches(annotation.regexp(), value.toString())) {
                            result.addError(fieldName, value, annotation.message());
                        }
                    }
                }

                // @PhoneNumber 검증
                if (field.isAnnotationPresent(PhoneNumber.class)) {
                    PhoneNumber annotation = field.getAnnotation(PhoneNumber.class);
                    if (shouldValidate(annotation.groups(), group)) {
                        if (!isValidPhoneNumber(value.toString())) {
                            result.addError(fieldName, value, annotation.message());
                        }
                    }
                }

                // @URL 검증
                if (field.isAnnotationPresent(URL.class)) {
                    URL annotation = field.getAnnotation(URL.class);
                    if (shouldValidate(annotation.groups(), group)) {
                        if (!isValidURL(value.toString())) {
                            result.addError(fieldName, value, annotation.message());
                        }
                    }
                }

                // @Valid - Nested Object 검증
                if (field.isAnnotationPresent(Valid.class)) {
                    validateObject(value, fieldName, result, group);
                }

            } catch (IllegalAccessException e) {
                result.addError(field.getName(), null, "필드 접근 오류: " + e.getMessage());
            }
        }
    }

    private static boolean shouldValidate(Class<?>[] groups, Class<?> targetGroup) {
        if (targetGroup == null) {
            return groups.length == 0;  // 그룹이 없으면 기본 검증
        }

        if (groups.length == 0) {
            return false;  // 그룹이 지정되지 않은 검증은 스킵
        }

        for (Class<?> group : groups) {
            if (group == targetGroup) {
                return true;
            }
        }
        return false;
    }

    private static boolean isValidEmail(String email) {
        String emailRegex = "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$";
        return Pattern.matches(emailRegex, email);
    }

    private static boolean isValidPhoneNumber(String phone) {
        String phoneRegex = "^010-\\d{4}-\\d{4}$";
        return Pattern.matches(phoneRegex, phone);
    }

    private static boolean isValidURL(String url) {
        String urlRegex = "^https?://[A-Za-z0-9.-]+(:\\d+)?(/.*)?$";
        return Pattern.matches(urlRegex, url);
    }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 6️⃣ 도메인 모델 - 사용자 회원가입
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Address {

    @NotBlank(message = "도시는 필수 입력 항목입니다")
    private String city;

    @NotBlank(message = "상세 주소는 필수 입력 항목입니다")
    @MinLength(value = 5, message = "상세 주소는 최소 5자 이상이어야 합니다")
    private String street;

    @NotNull(message = "우편번호는 필수 입력 항목입니다")
    @PatternMatch(regexp = "^\\d{5}$", message = "우편번호는 5자리 숫자여야 합니다")
    private String zipCode;

    public Address(String city, String street, String zipCode) {
        this.city = city;
        this.street = street;
        this.zipCode = zipCode;
    }

    @Override
    public String toString() {
        return String.format("%s %s (%s)", city, street, zipCode);
    }
}

class UserRegistration {

    @NotNull(message = "사용자 이름은 필수입니다", groups = {CreateGroup.class, UpdateGroup.class})
    @MinLength(value = 2, message = "사용자 이름은 최소 2자 이상", groups = {CreateGroup.class, UpdateGroup.class})
    @MaxLength(value = 20, message = "사용자 이름은 최대 20자 이하", groups = {CreateGroup.class, UpdateGroup.class})
    private String username;

    @NotNull(message = "이메일은 필수입니다", groups = {CreateGroup.class, UpdateGroup.class})
    @Email(message = "올바른 이메일 형식이 아닙니다", groups = {CreateGroup.class, UpdateGroup.class})
    private String email;

    @NotNull(message = "비밀번호는 필수입니다", groups = {CreateGroup.class})
    @MinLength(value = 8, message = "비밀번호는 최소 8자 이상", groups = {CreateGroup.class})
    @PatternMatch(
        regexp = "^(?=.*[A-Za-z])(?=.*\\d)(?=.*[@$!%*#?&])[A-Za-z\\d@$!%*#?&]{8,}$",
        message = "비밀번호는 영문, 숫자, 특수문자를 포함해야 합니다",
        groups = {CreateGroup.class}
    )
    private String password;

    @NotNull(message = "나이는 필수입니다", groups = {CreateGroup.class, UpdateGroup.class})
    @Range(min = 14, max = 120, message = "나이는 14~120세 사이여야 합니다", groups = {CreateGroup.class, UpdateGroup.class})
    private Integer age;

    @NotNull(message = "전화번호는 필수입니다", groups = {CreateGroup.class, UpdateGroup.class})
    @PhoneNumber(groups = {CreateGroup.class, UpdateGroup.class})
    private String phoneNumber;

    @URL(message = "올바른 웹사이트 URL이 아닙니다", groups = {UpdateGroup.class})
    private String website;

    @Valid
    @NotNull(message = "주소는 필수입니다", groups = {CreateGroup.class})
    private Address address;

    public UserRegistration(String username, String email, String password,
                           Integer age, String phoneNumber, String website, Address address) {
        this.username = username;
        this.email = email;
        this.password = password;
        this.age = age;
        this.phoneNumber = phoneNumber;
        this.website = website;
        this.address = address;
    }

    @Override
    public String toString() {
        return String.format("UserRegistration{username='%s', email='%s', age=%d, phone='%s'}",
                           username, email, age, phoneNumber);
    }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 7️⃣ 실행 및 테스트
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

public class SmartValidatorFramework {
    public static void main(String[] args) {
        System.out.println("=== SmartValidator Framework - 실전 프로젝트 ===\n");

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // Test Case 1: 올바른 데이터 (Create)
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        System.out.println("=".repeat(60));
        System.out.println("Test Case 1: 올바른 회원가입 데이터 (Create Group)");
        System.out.println("=".repeat(60) + "\n");

        Address validAddress = new Address("서울", "강남구 테헤란로 123", "06234");
        UserRegistration validUser = new UserRegistration(
            "김철수",
            "chulsoo@example.com",
            "Pass123!@#",
            28,
            "010-1234-5678",
            "https://chulsoo.com",
            validAddress
        );

        System.out.println("사용자 정보: " + validUser);
        ValidationResult result1 = SmartValidator.validate(validUser, CreateGroup.class);
        result1.printSummary();

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // Test Case 2: 이메일 형식 오류
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        System.out.println("\n" + "=".repeat(60));
        System.out.println("Test Case 2: 잘못된 이메일 형식");
        System.out.println("=".repeat(60) + "\n");

        Address address2 = new Address("부산", "해운대구 우동", "48099");
        UserRegistration invalidEmail = new UserRegistration(
            "이영희",
            "invalid-email",  // @ 없음
            "SecurePass1!",
            25,
            "010-9999-8888",
            null,
            address2
        );

        ValidationResult result2 = SmartValidator.validate(invalidEmail, CreateGroup.class);
        result2.printSummary();

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // Test Case 3: 비밀번호 규칙 위반
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        System.out.println("\n" + "=".repeat(60));
        System.out.println("Test Case 3: 약한 비밀번호 (영문+숫자+특수문자 필요)");
        System.out.println("=".repeat(60) + "\n");

        Address address3 = new Address("대전", "유성구 궁동", "34126");
        UserRegistration weakPassword = new UserRegistration(
            "박민수",
            "minsoo@example.com",
            "password",  // 특수문자 없음
            30,
            "010-5555-6666",
            null,
            address3
        );

        ValidationResult result3 = SmartValidator.validate(weakPassword, CreateGroup.class);
        result3.printSummary();

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // Test Case 4: 나이 범위 초과
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        System.out.println("\n" + "=".repeat(60));
        System.out.println("Test Case 4: 나이가 허용 범위를 벗어남");
        System.out.println("=".repeat(60) + "\n");

        Address address4 = new Address("광주", "동구 충장로", "61475");
        UserRegistration invalidAge = new UserRegistration(
            "최지훈",
            "jihoon@example.com",
            "ValidPass1!",
            10,  // 14세 미만
            "010-7777-8888",
            null,
            address4
        );

        ValidationResult result4 = SmartValidator.validate(invalidAge, CreateGroup.class);
        result4.printSummary();

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // Test Case 5: Nested Object 검증 (주소 오류)
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        System.out.println("\n" + "=".repeat(60));
        System.out.println("Test Case 5: Nested Object 검증 - 잘못된 주소");
        System.out.println("=".repeat(60) + "\n");

        Address invalidAddress = new Address("인천", "남", "1234");  // 상세주소 짧음, 우편번호 형식 오류
        UserRegistration nestedError = new UserRegistration(
            "정수진",
            "sujin@example.com",
            "MyPass123!",
            27,
            "010-3333-4444",
            null,
            invalidAddress
        );

        ValidationResult result5 = SmartValidator.validate(nestedError, CreateGroup.class);
        result5.printSummary();

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // Test Case 6: 여러 필드 동시 오류
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        System.out.println("\n" + "=".repeat(60));
        System.out.println("Test Case 6: 여러 필드에 오류가 있는 경우");
        System.out.println("=".repeat(60) + "\n");

        Address address6 = new Address("", "", "ABC");  // 모두 오류
        UserRegistration multipleErrors = new UserRegistration(
            "김",           // 너무 짧음
            "bad@email",   // 도메인 확장자 없음
            "weak",        // 짧고 규칙 위반
            200,           // 범위 초과
            "010-12-34",   // 형식 오류
            "not-a-url",   // URL 형식 오류
            address6
        );

        ValidationResult result6 = SmartValidator.validate(multipleErrors, CreateGroup.class);
        result6.printSummary();

        System.out.println("\n상세 오류 목록:");
        result6.printErrors();

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // Test Case 7: 그룹 검증 - Update Group (비밀번호 제외)
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        System.out.println("\n" + "=".repeat(60));
        System.out.println("Test Case 7: Update Group 검증 (비밀번호 검증 제외)");
        System.out.println("=".repeat(60) + "\n");

        Address address7 = new Address("울산", "남구 삼산로", "44705");
        UserRegistration updateUser = new UserRegistration(
            "강동원",
            "dongwon@example.com",
            null,  // Update 시에는 비밀번호 검증 안 함
            35,
            "010-2222-3333",
            "http://dongwon.dev",
            address7
        );

        System.out.println("📝 Update Group 검증 시작...");
        ValidationResult result7 = SmartValidator.validate(updateUser, UpdateGroup.class);
        result7.printSummary();

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 프로젝트 요약
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        System.out.println("\n" + "=".repeat(60));
        System.out.println("=".repeat(60));
        System.out.println("\n🎯 SmartValidator Framework 핵심 기능:");

        System.out.println("\n1️⃣ 다양한 Validation Annotation");
        System.out.println("   - @NotNull, @NotBlank: null/빈 값 검증");
        System.out.println("   - @Email, @PhoneNumber, @URL: 형식 검증");
        System.out.println("   - @MinLength, @MaxLength: 길이 검증");
        System.out.println("   - @Range: 숫자 범위 검증");
        System.out.println("   - @PatternMatch: 정규식 검증");

        System.out.println("\n2️⃣ Nested Object 검증");
        System.out.println("   - @Valid로 중첩된 객체도 자동 검증");
        System.out.println("   - address.city, address.zipCode 등 경로 표시");

        System.out.println("\n3️⃣ 그룹 검증 (Group Validation)");
        System.out.println("   - CreateGroup: 생성 시에만 검증");
        System.out.println("   - UpdateGroup: 수정 시에만 검증");
        System.out.println("   - 같은 필드도 상황에 따라 다르게 검증");

        System.out.println("\n4️⃣ 상세한 검증 결과");
        System.out.println("   - ValidationError: 각 오류의 상세 정보");
        System.out.println("   - ValidationResult: 전체 검증 결과 집계");
        System.out.println("   - 필드별 오류 그룹화");

        System.out.println("\n5️⃣ 커스텀 에러 메시지");
        System.out.println("   - message 속성으로 사용자 정의 메시지");
        System.out.println("   - 한글 메시지 지원");

        System.out.println("\n" + "=".repeat(60));
        System.out.println("\n🌟 실무 활용 시나리오:");
        System.out.println("  - REST API 입력 검증");
        System.out.println("  - 회원가입/로그인 폼 검증");
        System.out.println("  - 데이터베이스 저장 전 검증");
        System.out.println("  - 설정 파일 검증");

        System.out.println("\n💡 이 프레임워크와 유사한 실제 라이브러리:");
        System.out.println("  - Hibernate Validator (JSR-303/JSR-380)");
        System.out.println("  - Spring Validation (@Valid, @Validated)");
        System.out.println("  - Apache Commons Validator");
    }
}
```

**실행 결과:**
```
=== SmartValidator Framework - 실전 프로젝트 ===

============================================================
Test Case 1: 올바른 회원가입 데이터 (Create Group)
============================================================

사용자 정보: UserRegistration{username='김철수', email='chulsoo@example.com', age=28, phone='010-1234-5678'}
✅ 검증 성공

============================================================
Test Case 2: 잘못된 이메일 형식
============================================================

❌ 검증 실패:
  📌 email:
     - 올바른 이메일 형식이 아닙니다

============================================================
Test Case 3: 약한 비밀번호 (영문+숫자+특수문자 필요)
============================================================

❌ 검증 실패:
  📌 password:
     - 비밀번호는 영문, 숫자, 특수문자를 포함해야 합니다

============================================================
Test Case 4: 나이가 허용 범위를 벗어남
============================================================

❌ 검증 실패:
  📌 age:
     - 나이는 14~120세 사이여야 합니다 (14~120)

============================================================
Test Case 5: Nested Object 검증 - 잘못된 주소
============================================================

❌ 검증 실패:
  📌 address.street:
     - 상세 주소는 최소 5자 이상이어야 합니다 (최소: 5자)
  📌 address.zipCode:
     - 우편번호는 5자리 숫자여야 합니다

============================================================
Test Case 6: 여러 필드에 오류가 있는 경우
============================================================

❌ 검증 실패:
  📌 password:
     - 비밀번호는 최소 8자 이상 (최소: 8자)
     - 비밀번호는 영문, 숫자, 특수문자를 포함해야 합니다
  📌 address.zipCode:
     - 우편번호는 5자리 숫자여야 합니다
  📌 phoneNumber:
     - 올바른 전화번호 형식이 아닙니다 (010-XXXX-XXXX)
  📌 username:
     - 사용자 이름은 최소 2자 이상 (최소: 2자)
  📌 address.city:
     - 도시는 필수 입력 항목입니다
  📌 email:
     - 올바른 이메일 형식이 아닙니다
  📌 age:
     - 나이는 14~120세 사이여야 합니다 (14~120)
  📌 address.street:
     - 상세 주소는 필수 입력 항목입니다

상세 오류 목록:
❌ 검증 실패 (10개 오류):
  • [username] 사용자 이름은 최소 2자 이상 (최소: 2자) (입력값: 김)
  • [email] 올바른 이메일 형식이 아닙니다 (입력값: bad@email)
  • [password] 비밀번호는 최소 8자 이상 (최소: 8자) (입력값: weak)
  • [password] 비밀번호는 영문, 숫자, 특수문자를 포함해야 합니다 (입력값: weak)
  • [age] 나이는 14~120세 사이여야 합니다 (14~120) (입력값: 200)
  • [phoneNumber] 올바른 전화번호 형식이 아닙니다 (010-XXXX-XXXX) (입력값: 010-12-34)
  • [address.city] 도시는 필수 입력 항목입니다 (입력값: )
  • [address.street] 상세 주소는 필수 입력 항목입니다 (입력값: )
  • [address.zipCode] 우편번호는 5자리 숫자여야 합니다 (입력값: ABC)

============================================================
Test Case 7: Update Group 검증 (비밀번호 검증 제외)
============================================================

📝 Update Group 검증 시작...
✅ 검증 성공

============================================================
============================================================

🎯 SmartValidator Framework 핵심 기능:

1️⃣ 다양한 Validation Annotation
   - @NotNull, @NotBlank: null/빈 값 검증
   - @Email, @PhoneNumber, @URL: 형식 검증
   - @MinLength, @MaxLength: 길이 검증
   - @Range: 숫자 범위 검증
   - @PatternMatch: 정규식 검증

2️⃣ Nested Object 검증
   - @Valid로 중첩된 객체도 자동 검증
   - address.city, address.zipCode 등 경로 표시

3️⃣ 그룹 검증 (Group Validation)
   - CreateGroup: 생성 시에만 검증
   - UpdateGroup: 수정 시에만 검증
   - 같은 필드도 상황에 따라 다르게 검증

4️⃣ 상세한 검증 결과
   - ValidationError: 각 오류의 상세 정보
   - ValidationResult: 전체 검증 결과 집계
   - 필드별 오류 그룹화

5️⃣ 커스텀 에러 메시지
   - message 속성으로 사용자 정의 메시지
   - 한글 메시지 지원

============================================================

🌟 실무 활용 시나리오:
  - REST API 입력 검증
  - 회원가입/로그인 폼 검증
  - 데이터베이스 저장 전 검증
  - 설정 파일 검증

💡 이 프레임워크와 유사한 실제 라이브러리:
  - Hibernate Validator (JSR-303/JSR-380)
  - Spring Validation (@Valid, @Validated)
  - Apache Commons Validator
```

---

## ❓ FAQ - 자주 묻는 질문

### Q1. Annotation과 인터페이스의 차이점은 무엇인가요?

**A:** Annotation은 `@interface` 키워드로 정의하는 특수한 형태의 인터페이스입니다.

| 구분 | 일반 인터페이스 | Annotation |
|-----|--------------|-----------|
| 정의 | `interface MyInterface {}` | `@interface MyAnnotation {}` |
| 용도 | 메서드 시그니처 정의, 다형성 | 메타데이터 제공 |
| 구현 | 클래스가 implements | 코드에 @로 붙임 |
| 메서드 | 추상 메서드, default 메서드 | 속성 정의 (메서드처럼 보임) |
| 값 반환 | 없음 | 기본값 지정 가능 |

**예시:**
```java
// 일반 인터페이스
interface Flyable {
    void fly();
}

// Annotation
@interface Author {
    String name();
    String date() default "N/A";
}

// 사용
@Author(name = "김철수", date = "2025-10-10")
class Book {}
```

---

### Q2. Annotation이 성능에 미치는 영향은 어떤가요?

**A:** Annotation 자체는 성능 오버헤드가 거의 없지만, **리플렉션으로 처리할 때** 성능 저하가 발생할 수 있습니다.

**성능 비교:**
1. **컴파일 타임 Annotation** (@Override, @SuppressWarnings)
   - 성능 영향 없음 (컴파일 후 사라짐)

2. **런타임 Annotation + 리플렉션** (@Entity, @Autowired)
   - 리플렉션 호출 시 일반 메서드 대비 수십 배 느림
   - 해결책: **캐싱**, 애플리케이션 시작 시 초기화

**최적화 예시:**
```java
// ❌ 느린 방식
for (int i = 0; i < 100000; i++) {
    Field[] fields = clazz.getDeclaredFields();  // 매번 리플렉션
}

// ✅ 빠른 방식
Field[] fields = clazz.getDeclaredFields();  // 한 번만
for (int i = 0; i < 100000; i++) {
    // fields 재사용
}
```

---

### Q3. 언제 Custom Annotation을 만들어야 하나요?

**A:** 다음 경우에 Custom Annotation을 고려하세요.

✅ **만들어야 할 때:**
1. **반복적인 boilerplate 코드 제거**
   - 같은 검증 로직을 여러 곳에서 반복
   - 예: @NotNull, @Email, @Transactional

2. **선언적 프로그래밍**
   - "어떻게"보다 "무엇을"에 집중
   - 예: @Cacheable, @Async, @Scheduled

3. **프레임워크/라이브러리 설정**
   - 코드 생성, AOP, DI 등
   - 예: @Entity, @Component, @Test

4. **메타데이터 표현**
   - 코드에 추가 정보 부여
   - 예: @Author, @Version, @Deprecated

❌ **만들지 말아야 할 때:**
1. 한두 곳에서만 사용
2. 단순한 if-else로 해결 가능
3. 리플렉션 없이 처리 불가능한 경우 (성능 중요 시)

---

### Q4. Annotation Processor와 Reflection의 차이점은?

**A:**

| 구분 | Annotation Processor | Reflection |
|-----|---------------------|-----------|
| 실행 시점 | 컴파일 타임 | 런타임 |
| 성능 | 빠름 (런타임 오버헤드 없음) | 느림 (리플렉션 호출 비용) |
| 코드 생성 | 가능 (소스 파일 생성) | 불가능 (읽기만 가능) |
| 활용 | Lombok, Dagger, AutoValue | Spring, Hibernate, JUnit |
| @Retention | SOURCE 또는 CLASS | RUNTIME 필수 |

**Annotation Processor 예시 (Lombok):**
```java
// 작성 코드
@Getter
@Setter
public class User {
    private String name;
}

// 컴파일 시 자동 생성
public class User {
    private String name;

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
}
```

**Reflection 예시 (Spring):**
```java
@Component
public class UserService {
    @Autowired
    private UserRepository repository;
}

// Spring이 런타임에 리플렉션으로 처리
```

---

### Q5. Meta-Annotation이란 무엇인가요?

**A:** **Annotation을 정의할 때 사용하는 Annotation**입니다.

**주요 Meta-Annotation:**

1. **@Retention** - 언제까지 유지?
   ```java
   @Retention(RetentionPolicy.RUNTIME)  // 런타임까지 유지
   ```

2. **@Target** - 어디에 적용?
   ```java
   @Target(ElementType.METHOD)  // 메서드에만 적용
   ```

3. **@Inherited** - 상속 가능?
   ```java
   @Inherited  // 자식 클래스에 자동 상속
   ```

4. **@Documented** - JavaDoc에 포함?
   ```java
   @Documented  // JavaDoc에 표시
   ```

5. **@Repeatable** - 반복 가능?
   ```java
   @Repeatable(Authors.class)  // 같은 Annotation 여러 번 적용 가능
   ```

**예시:**
```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@Documented
@interface MyAnnotation {
}
```

---

### Q6. Annotation은 상속이 가능한가요?

**A:** **클래스 레벨**에서는 `@Inherited`를 사용하면 가능하지만, **메서드/필드**는 상속되지 않습니다.

**예시:**
```java
@Inherited
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@interface MyAnnotation {
}

@MyAnnotation
class Parent {
}

class Child extends Parent {  // @MyAnnotation이 자동으로 상속됨
}
```

**주의:** `@Inherited`가 없으면 상속되지 않습니다.

---

### Q7. Annotation의 기본값은 어떻게 설정하나요?

**A:** `default` 키워드를 사용합니다.

```java
@interface MyAnnotation {
    String value() default "기본값";
    int count() default 1;
    String[] tags() default {};
}

// 사용
@MyAnnotation  // 모든 속성이 기본값 사용
class Example1 {}

@MyAnnotation(value = "커스텀", count = 5)
class Example2 {}

@MyAnnotation("축약형")  // value는 속성명 생략 가능
class Example3 {}
```

**규칙:**
- 기본값이 없는 속성은 **필수**
- 속성이 하나뿐이고 이름이 `value`면 **이름 생략 가능**
- 배열 기본값은 `{}` 또는 `{"item1", "item2"}`

---

## 🎤 면접 질문

### 주니어 레벨 (Junior Level)

#### Q1. Annotation이란 무엇이며, 왜 사용하나요?

**A:** Annotation은 Java 소스 코드에 메타데이터를 추가하는 방법입니다.

**주요 용도:**
1. **컴파일러에게 정보 제공** - @Override, @Deprecated
2. **컴파일 시 코드 생성** - Lombok (@Getter, @Setter)
3. **런타임 처리** - Spring (@Autowired), JPA (@Entity)

**예시:**
```java
@Override
public String toString() {
    return "Example";
}
```

**장점:**
- 코드 가독성 향상
- Boilerplate 코드 감소
- 선언적 프로그래밍

---

#### Q2. @Override Annotation의 역할은 무엇인가요?

**A:** 부모 클래스의 메서드를 **올바르게 재정의했는지 컴파일러가 검증**합니다.

**없으면?**
- 메서드 이름 오타 시 새로운 메서드로 추가됨
- 런타임에서야 문제 발견

**있으면?**
- 컴파일 타임에 오류 발견
- "부모에 해당 메서드가 없습니다" 오류 표시

```java
class Animal {
    public void makeSound() {}
}

class Dog extends Animal {
    @Override
    public void makeSoung() {}  // 컴파일 에러! (오타: makeSound → makeSoung)
}
```

---

#### Q3. @Retention의 세 가지 정책을 설명하세요.

**A:**

1. **SOURCE**
   - 소스 코드에만 유지, 컴파일 후 사라짐
   - 예: @Override, @SuppressWarnings

2. **CLASS** (기본값)
   - .class 파일까지 유지, 런타임에는 없음
   - Annotation Processor에서 사용

3. **RUNTIME**
   - 런타임까지 유지, 리플렉션으로 읽기 가능
   - 예: @Entity, @Autowired, Custom Validation

```java
@Retention(RetentionPolicy.RUNTIME)
@interface MyAnnotation {}
```

---

#### Q4. @Target Annotation은 무엇이며, 주요 옵션은?

**A:** Annotation을 **어디에 적용할 수 있는지** 제한합니다.

**주요 ElementType:**
- `TYPE`: 클래스, 인터페이스, enum
- `FIELD`: 필드 (멤버 변수)
- `METHOD`: 메서드
- `PARAMETER`: 메서드 파라미터
- `CONSTRUCTOR`: 생성자
- `LOCAL_VARIABLE`: 지역 변수
- `ANNOTATION_TYPE`: Annotation

```java
@Target(ElementType.METHOD)
@interface Transactional {}

@Transactional  // 컴파일 에러!
class MyClass {}

class MyClass {
    @Transactional  // OK
    public void save() {}
}
```

---

#### Q5. Custom Annotation은 어떻게 만드나요?

**A:**

```java
// 1. @interface로 정의
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface NotNull {
    String message() default "null일 수 없습니다";
}

// 2. 사용
class User {
    @NotNull(message = "이름은 필수입니다")
    private String name;
}

// 3. 처리 (리플렉션)
for (Field field : User.class.getDeclaredFields()) {
    if (field.isAnnotationPresent(NotNull.class)) {
        NotNull annotation = field.getAnnotation(NotNull.class);
        System.out.println(annotation.message());
    }
}
```

---

#### Q6. Reflection으로 Annotation을 어떻게 읽나요?

**A:**

```java
Class<?> clazz = MyClass.class;

// 클래스 레벨 Annotation
if (clazz.isAnnotationPresent(Entity.class)) {
    Entity entity = clazz.getAnnotation(Entity.class);
}

// 필드 레벨 Annotation
for (Field field : clazz.getDeclaredFields()) {
    if (field.isAnnotationPresent(NotNull.class)) {
        NotNull annotation = field.getAnnotation(NotNull.class);
    }
}

// 메서드 레벨 Annotation
for (Method method : clazz.getDeclaredMethods()) {
    if (method.isAnnotationPresent(Transactional.class)) {
        // ...
    }
}
```

---

#### Q7. Spring에서 자주 사용하는 Annotation은?

**A:**

**DI 관련:**
- `@Component`: 일반 컴포넌트
- `@Service`: 비즈니스 로직
- `@Repository`: 데이터 접근
- `@Controller`, `@RestController`: 웹 계층
- `@Autowired`: 의존성 주입

**Web MVC:**
- `@GetMapping`, `@PostMapping`: HTTP 메서드 매핑
- `@PathVariable`: URL 경로 변수
- `@RequestParam`: 쿼리 파라미터
- `@RequestBody`: HTTP 요청 본문

**JPA:**
- `@Entity`: 엔티티 클래스
- `@Table`: 테이블 매핑
- `@Id`: 기본 키
- `@Column`: 컬럼 매핑

---

### 중급 레벨 (Intermediate Level)

#### Q8. Annotation Processor의 동작 원리를 설명하세요.

**A:** Annotation Processor는 **컴파일 타임에 Annotation을 읽고 새로운 소스 파일을 생성**하는 도구입니다.

**동작 과정:**
1. `javac` 컴파일러가 소스 코드를 파싱
2. Annotation Processor가 특정 Annotation을 찾음
3. Processor가 새로운 `.java` 파일 생성
4. 생성된 파일도 컴파일되어 `.class`로 변환

**예시 - Lombok:**
```java
// 작성 코드
@Getter
@Setter
@ToString
public class User {
    private String name;
    private int age;
}

// Annotation Processor가 생성하는 코드
public class User {
    private String name;
    private int age;

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getAge() { return age; }
    public void setAge(int age) { this.age = age; }

    @Override
    public String toString() {
        return "User(name=" + name + ", age=" + age + ")";
    }
}
```

**장점:**
- 런타임 오버헤드 없음
- 타입 안전성 유지
- IDE 지원 (자동 완성)

**구현:**
```java
@SupportedAnnotationTypes("com.example.MyAnnotation")
@SupportedSourceVersion(SourceVersion.RELEASE_17)
public class MyProcessor extends AbstractProcessor {
    @Override
    public boolean process(Set<? extends TypeElement> annotations,
                          RoundEnvironment roundEnv) {
        // Annotation 처리 및 코드 생성
        return true;
    }
}
```

---

#### Q9. Meta-Annotation의 종류와 각각의 역할을 설명하세요.

**A:**

**1. @Retention** - 언제까지 유지?
```java
@Retention(RetentionPolicy.SOURCE)   // 소스코드만
@Retention(RetentionPolicy.CLASS)    // .class 파일까지
@Retention(RetentionPolicy.RUNTIME)  // 런타임까지
```

**2. @Target** - 어디에 적용?
```java
@Target(ElementType.TYPE)         // 클래스, 인터페이스
@Target(ElementType.FIELD)        // 필드
@Target(ElementType.METHOD)       // 메서드
@Target({TYPE, METHOD})           // 여러 곳
```

**3. @Inherited** - 상속 가능?
```java
@Inherited  // 자식 클래스가 자동으로 상속받음 (클래스 레벨만)
```

**4. @Documented** - JavaDoc에 포함?
```java
@Documented  // API 문서에 Annotation 정보 표시
```

**5. @Repeatable** - 반복 가능?
```java
@Repeatable(Authors.class)
@interface Author {
    String name();
}

// 사용
@Author(name = "김철수")
@Author(name = "이영희")
class Book {}
```

---

#### Q10. Annotation과 AOP의 관계를 설명하세요.

**A:** Annotation은 AOP의 **Pointcut 지정에 자주 사용**됩니다.

**AOP (Aspect-Oriented Programming):**
- 공통 관심사를 분리하는 프로그래밍 패러다임
- 예: 로깅, 트랜잭션, 보안, 성능 측정

**Annotation 기반 AOP:**
```java
// 1. Custom Annotation 정의
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface Loggable {
}

// 2. 비즈니스 메서드에 적용
class UserService {
    @Loggable
    public void createUser(String name) {
        // 사용자 생성 로직
    }
}

// 3. AOP Aspect 정의
@Aspect
class LoggingAspect {
    @Around("@annotation(Loggable)")
    public Object logExecutionTime(ProceedingJoinPoint joinPoint) throws Throwable {
        long start = System.currentTimeMillis();

        Object result = joinPoint.proceed();  // 실제 메서드 실행

        long end = System.currentTimeMillis();
        System.out.println("실행 시간: " + (end - start) + "ms");

        return result;
    }
}
```

**Spring의 Annotation 기반 AOP:**
- `@Transactional`: 트랜잭션 관리
- `@Cacheable`: 캐싱
- `@Async`: 비동기 실행
- `@Secured`: 보안

**장점:**
- 선언적 프로그래밍
- 비즈니스 로직과 공통 관심사 분리
- 코드 중복 제거

---

#### Q11. @Inherited의 역할과 한계를 설명하세요.

**A:** `@Inherited`는 **클래스 레벨 Annotation을 자식 클래스가 자동으로 상속**받게 합니다.

**동작:**
```java
@Inherited
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@interface MyAnnotation {
}

@MyAnnotation
class Parent {
}

class Child extends Parent {
    // @MyAnnotation이 자동으로 상속됨
}

// 확인
Child.class.isAnnotationPresent(MyAnnotation.class)  // true
```

**한계:**

1. **클래스 레벨만 가능**
   ```java
   @MyAnnotation
   public void parentMethod() {}  // 메서드는 상속 안 됨
   ```

2. **인터페이스는 적용 안 됨**
   ```java
   @MyAnnotation
   interface MyInterface {}

   class Impl implements MyInterface {}  // 상속 안 됨
   ```

3. **직접 상속만 가능**
   ```java
   @MyAnnotation
   class A {}

   class B extends A {}  // OK
   class C extends B {}  // C에는 없음 (A → B만 상속)
   ```

---

#### Q12. Type Annotation (Java 8+)이란 무엇인가요?

**A:** Java 8부터 **타입이 사용되는 모든 위치**에 Annotation을 붙일 수 있습니다.

**기존 (Java 7 이하):**
```java
@NotNull
String name;  // 필드 선언에만 적용
```

**Type Annotation (Java 8+):**
```java
// 1. 제네릭 타입 파라미터
List<@NotNull String> names;

// 2. 배열 요소
String @NotNull [] array;

// 3. 타입 캐스팅
String s = (@NotNull String) obj;

// 4. instanceof
if (obj instanceof @NonNull String) {}

// 5. throws 절
void method() throws @Critical IOException {}

// 6. 메서드 리턴 타입
@NotNull String getName() {}
```

**@Target 설정:**
```java
@Target(ElementType.TYPE_USE)  // 모든 타입 사용 위치
@interface NotNull {}

@Target(ElementType.TYPE_PARAMETER)  // 제네릭 타입 파라미터만
@interface NonEmpty {}
```

**활용:**
- Null 안전성 검사 (Checker Framework)
- 타입 안전성 강화
- 정적 분석 도구

---

## 🎓 전체 요약

### Annotation의 핵심
1. **메타데이터 제공** - 코드에 추가 정보 부여
2. **선언적 프로그래밍** - "무엇을" 명시, "어떻게"는 프레임워크가 처리
3. **Boilerplate 코드 감소** - @Getter, @Setter, @Override 등

### 주요 사용처
- **Spring**: DI, AOP, Web MVC
- **JPA/Hibernate**: ORM 매핑
- **Validation**: 데이터 검증
- **Testing**: JUnit, Mockito
- **Lombok**: 코드 생성

### 성능 고려사항
- Annotation 자체는 성능 영향 없음
- **Reflection은 느림** → 캐싱 필수
- **Annotation Processor** 사용 시 런타임 오버헤드 없음

---

**🎉 축하합니다! Annotation 마스터를 완료했습니다!**

**다음 학습 주제:**
- Chapter 22: 내부 클래스 (Inner Classes)
- Chapter 23: 예외 처리 (Exception Handling)
