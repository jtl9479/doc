# 31장 Optional - Part 3: 면접 질문

## 🎤 면접 질문 TOP 3

### Q1. Optional을 사용하는 이유는?

**답변**:
```
1. NullPointerException 방지
2. null 체크 코드 감소
3. API의 의도를 명확히 표현
   - Optional<User>: 값이 없을 수 있음을 명시
   - User: 항상 값이 있어야 함

예시:
// Before
public User findUser(String id) {
    return ...; // null일 수도?
}

// After
public Optional<User> findUser(String id) {
    return ...; // 명확히 Optional
}
```

### Q2. Optional.of vs Optional.ofNullable 차이는?

**답변**:
```
Optional.of(value):
- value가 null이면 즉시 NPE
- null이 절대 아닐 때 사용

Optional.ofNullable(value):
- value가 null이면 Optional.empty() 반환
- null 가능성이 있을 때 사용

// 예시
Optional.of("Hello")        // OK
Optional.of(null)           // NPE!

Optional.ofNullable("Hello") // OK
Optional.ofNullable(null)    // Optional.empty()
```

### Q3. orElse vs orElseGet 차이는?

**답변**:
```
orElse(T value):
- 항상 value 평가 (값이 있어도!)
- 단순 값일 때 사용

orElseGet(Supplier<T>):
- 값이 없을 때만 Supplier 실행
- 비용이 큰 연산일 때 사용

// 예시
String name1 = opt.orElse(createDefault());
// → 값이 있어도 createDefault() 실행됨!

String name2 = opt.orElseGet(() -> createDefault());
// → 값이 없을 때만 createDefault() 실행

성능:
- orElseGet이 더 효율적 (Lazy)
- 단순 값은 orElse 사용 가능
```

---

## 🎓 Best Practices

```java
// ✅ 좋은 사용
return Optional.ofNullable(findUser(id));

userOpt.map(User::getName)
    .filter(name -> name.length() > 3)
    .orElse("Anonymous");

// ❌ 나쁜 사용
Optional<User> user = ...; // 필드에 사용 X
user.get();  // get() 남용 X
if (user.isPresent()) { ... }  // isPresent() + get() X
```

**시리즈 완료**: 31장 Optional 마스터! 🎊
