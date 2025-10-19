# 32장 날짜와 시간 API - Part 1: 기초

## 🔍 Java 8 날짜/시간 API

**기존 Date/Calendar의 문제점을 해결한 새로운 API (java.time)**

```java
// ❌ 구식 (Date, Calendar)
Date date = new Date();
Calendar cal = Calendar.getInstance();

// ✅ 신식 (LocalDate, LocalDateTime)
LocalDate today = LocalDate.now();
LocalDateTime now = LocalDateTime.now();
```

---

## 📖 주요 클래스

### 1. LocalDate (날짜만)
```java
LocalDate today = LocalDate.now();
LocalDate birthday = LocalDate.of(2000, 1, 1);

System.out.println("오늘: " + today);  // 2024-01-15
System.out.println("생일: " + birthday);  // 2000-01-01
```

### 2. LocalTime (시간만)
```java
LocalTime now = LocalTime.now();
LocalTime lunch = LocalTime.of(12, 30);

System.out.println("현재 시각: " + now);  // 14:30:45
System.out.println("점심 시간: " + lunch);  // 12:30
```

### 3. LocalDateTime (날짜 + 시간)
```java
LocalDateTime now = LocalDateTime.now();
LocalDateTime meeting = LocalDateTime.of(2024, 1, 15, 14, 30);

System.out.println("지금: " + now);
```

### 4. ZonedDateTime (타임존 포함)
```java
ZonedDateTime seoulTime = ZonedDateTime.now(ZoneId.of("Asia/Seoul"));
ZonedDateTime nyTime = ZonedDateTime.now(ZoneId.of("America/New_York"));

System.out.println("서울: " + seoulTime);
System.out.println("뉴욕: " + nyTime);
```

### 5. Period (날짜 간격)
```java
LocalDate start = LocalDate.of(2024, 1, 1);
LocalDate end = LocalDate.of(2024, 12, 31);

Period period = Period.between(start, end);
System.out.println("기간: " + period.getMonths() + "개월 " + period.getDays() + "일");
```

### 6. Duration (시간 간격)
```java
LocalTime start = LocalTime.of(9, 0);
LocalTime end = LocalTime.of(18, 0);

Duration duration = Duration.between(start, end);
System.out.println("근무 시간: " + duration.toHours() + "시간");
```

---

## 🎯 핵심 연산

```java
LocalDate today = LocalDate.now();

// 더하기
LocalDate tomorrow = today.plusDays(1);
LocalDate nextMonth = today.plusMonths(1);

// 빼기
LocalDate yesterday = today.minusDays(1);

// 비교
boolean isBefore = today.isBefore(tomorrow);
boolean isAfter = today.isAfter(yesterday);

// 포맷팅
String formatted = today.format(DateTimeFormatter.ofPattern("yyyy년 MM월 dd일"));
```

**다음 Part 2**: 실전 활용
