# 35장 Reflection - Part 2: 실전 & 주의사항

## 🏢 실전 활용

### 1. 의존성 주입 (DI) 구현
```java
class DIContainer {
    public <T> T createInstance(Class<T> clazz) throws Exception {
        Constructor<T> constructor = clazz.getDeclaredConstructor();
        return constructor.newInstance();
    }
}

// 사용
DIContainer container = new DIContainer();
MyService service = container.createInstance(MyService.class);
```

### 2. DTO 복사 (BeanUtils 패턴)
```java
public void copyProperties(Object source, Object target) throws Exception {
    Class<?> sourceClass = source.getClass();
    Class<?> targetClass = target.getClass();

    for (Field sourceField : sourceClass.getDeclaredFields()) {
        sourceField.setAccessible(true);

        Field targetField = targetClass.getDeclaredField(sourceField.getName());
        targetField.setAccessible(true);

        Object value = sourceField.get(source);
        targetField.set(target, value);
    }
}
```

### 3. 애노테이션 처리
```java
@Retention(RetentionPolicy.RUNTIME)
@interface MyAnnotation {
    String value();
}

class Processor {
    public void process(Object obj) throws Exception {
        Class<?> clazz = obj.getClass();

        for (Method method : clazz.getDeclaredMethods()) {
            if (method.isAnnotationPresent(MyAnnotation.class)) {
                MyAnnotation anno = method.getAnnotation(MyAnnotation.class);
                System.out.println("애노테이션 값: " + anno.value());
                method.invoke(obj);
            }
        }
    }
}
```

---

## 🚨 주의사항

### ⚠️ 1. 성능 저하
```java
// ❌ Reflection은 느림
Method method = clazz.getMethod("toString");
String result = (String) method.invoke(obj);

// ✅ 직접 호출이 빠름
String result = obj.toString();

// 성능 차이: Reflection이 약 10~100배 느림
```

### ⚠️ 2. 타입 안전성 상실
```java
// ❌ 컴파일 타임 체크 불가
Object obj = clazz.newInstance();
Method method = clazz.getMethod("unknownMethod");  // 런타임 에러!

// ✅ 일반 코드는 컴파일 타임 체크
MyClass obj = new MyClass();
obj.knownMethod();  // 컴파일 타임에 오류 발견
```

### ⚠️ 3. 캡슐화 파괴
```java
// ❌ private 필드 강제 접근
Field field = clazz.getDeclaredField("privateField");
field.setAccessible(true);  // 캡슐화 무시!
field.set(obj, value);

// 문제: 클래스 설계 의도 무시
```

### ⚠️ 4. 보안 위험
```java
// SecurityManager가 있으면 Reflection 제한 가능
// setAccessible(true) 실행 시 SecurityException 발생 가능
```

---

## 💡 Best Practices

```java
// ✅ 1. Reflection은 필요할 때만
if (canAvoidReflection()) {
    // 일반 코드 사용
} else {
    // Reflection 사용
}

// ✅ 2. 캐싱으로 성능 개선
private static final Map<String, Method> METHOD_CACHE = new HashMap<>();

Method getMethod(Class<?> clazz, String name) {
    String key = clazz.getName() + "#" + name;
    return METHOD_CACHE.computeIfAbsent(key, k -> {
        try {
            return clazz.getMethod(name);
        } catch (Exception e) {
            return null;
        }
    });
}

// ✅ 3. 예외 처리 철저히
try {
    Method method = clazz.getMethod("methodName");
    method.invoke(obj);
} catch (NoSuchMethodException e) {
    // 메서드 없음
} catch (IllegalAccessException e) {
    // 접근 불가
} catch (InvocationTargetException e) {
    // 메서드 실행 중 예외
}
```

**다음 Part 3**: 면접 질문
