# 32장 날짜와 시간 API - Part 2: 실전 활용

## 🏢 실전 예시

### 1. 나이 계산
```java
LocalDate birthday = LocalDate.of(2000, 3, 15);
LocalDate today = LocalDate.now();

Period age = Period.between(birthday, today);
System.out.println("나이: " + age.getYears() + "세");
```

### 2. D-Day 계산
```java
LocalDate exam = LocalDate.of(2024, 6, 15);
LocalDate today = LocalDate.now();

long dDay = ChronoUnit.DAYS.between(today, exam);
System.out.println("D-" + dDay);
```

### 3. 근무 시간 계산
```java
LocalTime start = LocalTime.of(9, 0);
LocalTime end = LocalTime.of(18, 30);

Duration workTime = Duration.between(start, end);
System.out.println("근무: " + workTime.toHours() + "시간 " +
    (workTime.toMinutes() % 60) + "분");
```

### 4. 타임존 변환
```java
ZonedDateTime seoulTime = ZonedDateTime.now(ZoneId.of("Asia/Seoul"));
ZonedDateTime nyTime = seoulTime.withZoneSameInstant(ZoneId.of("America/New_York"));

System.out.println("서울: " + seoulTime);
System.out.println("뉴욕: " + nyTime);
```

---

## 🚨 주니어 실수

### ❌ 실수 1: 구식 API 사용
```java
// ❌ Date/Calendar (구식)
Date date = new Date();
Calendar cal = Calendar.getInstance();

// ✅ LocalDate/LocalDateTime (신식)
LocalDate date = LocalDate.now();
LocalDateTime dateTime = LocalDateTime.now();
```

### ❌ 실수 2: 불변성 무시
```java
// ❌ 원본이 변경된다고 착각
LocalDate date = LocalDate.now();
date.plusDays(1);  // 원본 안 변함!

// ✅ 반환값 사용
LocalDate tomorrow = date.plusDays(1);  // 새 객체 반환
```

### ❌ 실수 3: 타임존 미고려
```java
// ❌ 타임존 없이 저장
LocalDateTime time = LocalDateTime.now();  // 타임존 정보 없음

// ✅ 타임존 포함
ZonedDateTime time = ZonedDateTime.now();  // 타임존 포함
```

**다음 Part 3**: 면접 질문
