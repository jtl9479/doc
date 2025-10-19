# 35장 Reflection - Part 3: 면접 질문

## 🎤 면접 질문 TOP 3

### Q1. Reflection이란 무엇이고, 언제 사용하나요?

**답변**:
```
Reflection:
- 런타임에 클래스 정보를 조회하고 조작하는 기능
- Class 객체를 통해 필드, 메서드, 생성자 접근

사용 시기:
1. 프레임워크 개발
   - Spring의 @Autowired (의존성 주입)
   - Hibernate의 엔티티 매핑

2. 라이브러리 개발
   - Jackson, Gson (JSON 직렬화)
   - JUnit (테스트 프레임워크)

3. 동적 클래스 로딩
   - 플러그인 시스템
   - 설정 기반 객체 생성

예시:
Class<?> clazz = Class.forName("com.example.MyClass");
Object instance = clazz.getDeclaredConstructor().newInstance();
```

### Q2. Reflection의 단점은?

**답변**:
```
1. 성능 저하
   - 일반 호출보다 10~100배 느림
   - 메서드 조회, 타입 체크 등 오버헤드

2. 타입 안전성 상실
   - 컴파일 타임 체크 불가
   - 런타임 에러 발생 가능

3. 캡슐화 파괴
   - private 접근 제어 무시
   - 클래스 설계 의도 무시

4. 보안 문제
   - setAccessible(true) 사용 시 위험
   - SecurityManager로 제한 필요

해결책:
- 필요할 때만 사용
- 캐싱으로 성능 개선
- 철저한 예외 처리
```

### Q3. getDeclaredMethod와 getMethod의 차이는?

**답변**:
```
getMethod():
- public 메서드만 조회
- 상속된 메서드 포함
- 접근 가능한 메서드만

getDeclaredMethod():
- 모든 접근 제어자 메서드 조회
- 해당 클래스에 선언된 메서드만
- private도 조회 가능 (setAccessible 필요)

예시:
class Parent {
    public void publicMethod() {}
    private void privateMethod() {}
}

class Child extends Parent {
    private void childMethod() {}
}

Child child = new Child();
Class<?> clazz = child.getClass();

// getMethod - public + 상속
Method m1 = clazz.getMethod("publicMethod");  // ✅ 가능

// getDeclaredMethod - 선언된 메서드만
Method m2 = clazz.getDeclaredMethod("childMethod");  // ✅ 가능
Method m3 = clazz.getDeclaredMethod("publicMethod");  // ❌ 에러!
```

---

## 🎓 Reflection Best Practices

```java
// ✅ 1. 캐싱으로 성능 개선
private static final Map<String, Method> METHOD_CACHE = new ConcurrentHashMap<>();

Method getMethodCached(Class<?> clazz, String name) {
    String key = clazz.getName() + "#" + name;
    return METHOD_CACHE.computeIfAbsent(key, k -> {
        try {
            return clazz.getMethod(name);
        } catch (NoSuchMethodException e) {
            return null;
        }
    });
}

// ✅ 2. 예외 처리 세분화
try {
    Method method = clazz.getDeclaredMethod("methodName");
    method.setAccessible(true);
    method.invoke(obj);
} catch (NoSuchMethodException e) {
    // 메서드 없음
} catch (IllegalAccessException e) {
    // 접근 권한 없음
} catch (InvocationTargetException e) {
    // 메서드 실행 중 예외
    Throwable cause = e.getCause();  // 실제 예외
}

// ✅ 3. setAccessible 최소화
if (method.isAccessible()) {
    method.invoke(obj);
} else {
    method.setAccessible(true);
    try {
        method.invoke(obj);
    } finally {
        method.setAccessible(false);  // 복원
    }
}

// ✅ 4. MethodHandle 사용 (Java 7+)
MethodHandles.Lookup lookup = MethodHandles.lookup();
MethodHandle mh = lookup.findVirtual(MyClass.class, "method",
    MethodType.methodType(void.class));
mh.invoke(obj);  // Reflection보다 빠름
```

---

## 💡 언제 Reflection 대신 다른 방법?

```java
// ❌ Reflection 불필요
if (className.equals("TypeA")) {
    new TypeA().process();
} else if (className.equals("TypeB")) {
    new TypeB().process();
}

// ✅ 인터페이스 + 팩토리 패턴
interface Processor {
    void process();
}

Map<String, Processor> processors = Map.of(
    "TypeA", new TypeA(),
    "TypeB", new TypeB()
);

processors.get(className).process();
```

**시리즈 완료**: 35장 Reflection 마스터! 🎊
