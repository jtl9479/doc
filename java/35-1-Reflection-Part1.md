# 35장 Reflection - Part 1: 기본 개념

## 🔍 Reflection이란?

**런타임에 클래스 정보를 조회하고 조작하는 기능**

```java
// 컴파일 타임에 알 수 없는 클래스 사용
Class<?> clazz = Class.forName("com.example.MyClass");
Object instance = clazz.getDeclaredConstructor().newInstance();
```

---

## 📖 Class 객체 얻기

```java
// 방법 1: .class 리터럴
Class<String> clazz1 = String.class;

// 방법 2: .getClass()
String str = "Hello";
Class<?> clazz2 = str.getClass();

// 방법 3: Class.forName()
Class<?> clazz3 = Class.forName("java.lang.String");
```

---

## 📖 클래스 정보 조회

```java
Class<?> clazz = MyClass.class;

// 클래스 이름
String name = clazz.getName();
String simpleName = clazz.getSimpleName();

// 필드 조회
Field[] fields = clazz.getDeclaredFields();
for (Field field : fields) {
    System.out.println(field.getName());
}

// 메서드 조회
Method[] methods = clazz.getDeclaredMethods();
for (Method method : methods) {
    System.out.println(method.getName());
}

// 생성자 조회
Constructor<?>[] constructors = clazz.getDeclaredConstructors();
```

---

## 📖 동적 객체 생성

```java
// 기본 생성자
Class<?> clazz = MyClass.class;
Object instance = clazz.getDeclaredConstructor().newInstance();

// 매개변수 있는 생성자
Constructor<?> constructor = clazz.getConstructor(String.class, int.class);
Object instance = constructor.newInstance("value", 123);
```

---

## 📖 필드 접근

```java
class Person {
    private String name = "John";
}

Person person = new Person();
Class<?> clazz = person.getClass();

// private 필드 접근
Field field = clazz.getDeclaredField("name");
field.setAccessible(true);  // private 무시

// 값 읽기
String name = (String) field.get(person);

// 값 쓰기
field.set(person, "Jane");
```

---

## 📖 메서드 호출

```java
class Calculator {
    private int add(int a, int b) {
        return a + b;
    }
}

Calculator calc = new Calculator();
Class<?> clazz = calc.getClass();

// private 메서드 호출
Method method = clazz.getDeclaredMethod("add", int.class, int.class);
method.setAccessible(true);

int result = (int) method.invoke(calc, 10, 20);
System.out.println("결과: " + result);  // 30
```

---

## 💡 활용 사례

```
1. 프레임워크 (Spring, Hibernate)
   - 의존성 주입 (@Autowired)
   - ORM 매핑

2. 테스트 (JUnit, Mockito)
   - private 메서드 테스트
   - Mock 객체 생성

3. 직렬화/역직렬화 (JSON)
   - Jackson, Gson

4. 플러그인 시스템
   - 동적 클래스 로딩
```

**다음 Part 2**: 실전 활용 + 주의사항
