# 32장 날짜와 시간 API - Part 3: 면접 질문

## 🎤 면접 질문 TOP 3

### Q1. Date/Calendar vs LocalDate/LocalDateTime 차이는?

**답변**:
```
Date/Calendar (구식):
- 가변 객체 (Mutable)
- 월이 0부터 시작 (헷갈림)
- 타임존 처리 복잡
- 스레드 안전하지 않음

LocalDate/LocalDateTime (신식):
- 불변 객체 (Immutable)
- 월이 1부터 시작 (직관적)
- 타임존 명확히 분리
- 스레드 안전함
- 메서드 체이닝 가능

권장: LocalDate/LocalDateTime 사용
```

### Q2. LocalDate, LocalTime, LocalDateTime 차이는?

**답변**:
```
LocalDate:
- 날짜만 (년월일)
- 예: 2024-01-15

LocalTime:
- 시간만 (시분초)
- 예: 14:30:45

LocalDateTime:
- 날짜 + 시간
- 예: 2024-01-15T14:30:45

ZonedDateTime:
- 날짜 + 시간 + 타임존
- 예: 2024-01-15T14:30:45+09:00[Asia/Seoul]

선택 기준:
- 생일, 기념일 → LocalDate
- 알람 시간 → LocalTime
- 회의 일정 → LocalDateTime
- 글로벌 서비스 → ZonedDateTime
```

### Q3. Period vs Duration 차이는?

**답변**:
```
Period:
- 날짜 기반 간격
- 년, 월, 일 단위
- LocalDate 간 차이

Duration:
- 시간 기반 간격
- 시, 분, 초 단위
- LocalTime/LocalDateTime 간 차이

예시:
// Period
LocalDate start = LocalDate.of(2024, 1, 1);
LocalDate end = LocalDate.of(2024, 12, 31);
Period period = Period.between(start, end);
// → 11개월 30일

// Duration
LocalTime start = LocalTime.of(9, 0);
LocalTime end = LocalTime.of(18, 0);
Duration duration = Duration.between(start, end);
// → 9시간
```

---

## 🎓 Best Practices

```java
// ✅ 좋은 사용
LocalDate date = LocalDate.now();
LocalDate tomorrow = date.plusDays(1);

ZonedDateTime meeting = ZonedDateTime.of(
    LocalDateTime.of(2024, 1, 15, 14, 0),
    ZoneId.of("Asia/Seoul")
);

// ❌ 나쁜 사용
Date date = new Date();  // 구식 API
Calendar cal = Calendar.getInstance();  // 구식 API
```

**시리즈 완료**: 32장 날짜와 시간 API 마스터! 🎊
