# 31장 Optional - Part 2: 실전 활용 & 주니어 실수

## 🏢 실전 활용

### 1. Repository 패턴
```java
public interface UserRepository {
    Optional<User> findById(String id);
    Optional<User> findByEmail(String email);
}

// 사용
Optional<User> user = userRepository.findById("USER001");
user.ifPresentOrElse(
    u -> System.out.println("찾음: " + u),
    () -> System.out.println("없음")
);
```

### 2. 설정 값 처리
```java
Optional<String> config = getConfig("db.url");
String url = config.orElse("jdbc:mysql://localhost");
```

### 3. 체이닝
```java
String street = user
    .flatMap(User::getAddress)
    .map(Address::getStreet)
    .orElse("주소 없음");
```

---

## 🚨 주니어 실수

### ❌ 실수 1: get() 남용
```java
// ❌ NPE 위험
Optional<String> name = getName();
String result = name.get();  // 값 없으면 예외!

// ✅ orElse 사용
String result = getName().orElse("Unknown");
```

### ❌ 실수 2: Optional을 필드로 사용
```java
// ❌ 잘못됨
class User {
    private Optional<String> email;  // X
}

// ✅ 올바름
class User {
    private String email;  // null 허용

    public Optional<String> getEmail() {
        return Optional.ofNullable(email);
    }
}
```

### ❌ 실수 3: isPresent() + get() 패턴
```java
// ❌ Optional 의미 없음
if (opt.isPresent()) {
    doSomething(opt.get());
}

// ✅ ifPresent 사용
opt.ifPresent(value -> doSomething(value));
```

### ❌ 실수 4: Optional.of(null)
```java
// ❌ NPE 발생!
Optional<String> opt = Optional.of(null);

// ✅ ofNullable 사용
Optional<String> opt = Optional.ofNullable(nullableValue);
```

**다음 Part 3**: 면접 질문
