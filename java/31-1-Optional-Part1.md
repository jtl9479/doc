# 31장 Optional - Part 1: 실생활 비유로 이해하기

## 📚 목차
1. [Optional이란?](#optional이란)
2. [비유로 이해하기](#비유로-이해하기)

---

## 🔍 Optional이란?

**Optional**은 값이 있을 수도, 없을 수도 있는 컨테이너입니다.

```java
// 전통적인 방식
String name = getName();
if (name != null) {
    System.out.println(name.toUpperCase());
}

// Optional 방식
Optional<String> name = getNameOptional();
name.ifPresent(n -> System.out.println(n.toUpperCase()));
```

---

## 📖 비유 1: 선물 상자

**상자 안에 선물이 있을 수도, 없을 수도 있습니다.**

```java
// 빈 상자
Optional<String> empty = Optional.empty();

// 선물이 든 상자
Optional<String> present = Optional.of("Gift");

// 선물이 있으면 열기
present.ifPresent(gift -> System.out.println("받은 선물: " + gift));
```

---

## 📖 비유 2: 검색 결과

**검색 결과가 있을 수도, 없을 수도 있습니다.**

```java
Optional<User> findUser(String id) {
    User user = database.findById(id);
    return Optional.ofNullable(user);  // null일 수 있음
}

// 사용
Optional<User> user = findUser("USER001");
user.ifPresent(u -> System.out.println("찾음: " + u.getName()));
```

---

## 🎯 Optional 주요 메서드

```java
// 1. 생성
Optional.of(value)           // null이면 NPE
Optional.ofNullable(value)   // null 허용
Optional.empty()             // 빈 Optional

// 2. 값 확인
isPresent()   // 값 있으면 true
isEmpty()     // 값 없으면 true (Java 11+)

// 3. 값 꺼내기
get()         // 값 반환 (없으면 예외)
orElse(T)     // 값 or 기본값
orElseGet(Supplier)  // 값 or 함수 실행
orElseThrow()  // 값 or 예외

// 4. 함수형
map(Function)           // 변환
flatMap(Function)       // Optional 반환하는 변환
filter(Predicate)       // 조건 필터
ifPresent(Consumer)     // 값 있으면 실행
```

---

## 💡 핵심 패턴

```java
// ❌ 나쁜 예 (Optional의 의미 없음)
Optional<String> name = getName();
if (name.isPresent()) {
    System.out.println(name.get());
}

// ✅ 좋은 예
getName().ifPresent(System.out::println);

// ✅ 기본값 제공
String result = getName().orElse("Unknown");

// ✅ 변환
String upper = getName()
    .map(String::toUpperCase)
    .orElse("NO NAME");
```

**다음 Part 2**: 실전 활용 + 주니어 실수
