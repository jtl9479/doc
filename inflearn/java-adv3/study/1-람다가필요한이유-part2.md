# 1. 람다가 필요한 이유 - Part 2

**출처**: 인프런 - 김영한의 실전 자바 고급 3편
**작성일**: 2026-01-03

> **문서 구성**
> - Part 1: 프로젝트 환경 구성, 값 매개변수화, 동작 매개변수화
> - Part 2: 익명 클래스와 람다, 함수 vs 메서드, 람다 시작

---

## 목차

4. [람다가 필요한 이유3 - 익명 클래스와 람다](#4-람다가-필요한-이유3---익명-클래스와-람다)
5. [함수 vs 메서드](#5-함수-vs-메서드)
6. [람다 시작](#6-람다-시작)

---

## 4. 람다가 필요한 이유3 - 익명 클래스와 람다

> **TL;DR**
> - 정적 중첩 클래스 → 익명 클래스 → 람다로 점점 간결해짐
> - 람다는 `() -> {}` 형태로 코드 블럭을 직접 전달
> - 클래스나 인스턴스 정의 없이 간편하게 코드 조각 전달 가능

### 익명 클래스 사용 1 - 기본

정적 중첩 클래스 대신 익명 클래스를 사용하면 코드가 더 간결해집니다.

```java
package lambda.start;

import lambda.Procedure;
import java.util.Random;

// 익명 클래스 사용
public class Ex1RefMainV2 {

    public static void hello(Procedure procedure) {
        long startNs = System.nanoTime();
        procedure.run();
        long endNs = System.nanoTime();
        System.out.println("실행 시간: " + (endNs - startNs) + "ns");
    }

    public static void main(String[] args) {
        Procedure dice = new Procedure() {
            @Override
            public void run() {
                int randomValue = new Random().nextInt(6) + 1;
                System.out.println("주사위 = " + randomValue);
            }
        };

        Procedure sum = new Procedure() {
            @Override
            public void run() {
                for (int i = 1; i <= 3; i++) {
                    System.out.println("i = " + i);
                }
            }
        };

        hello(dice);
        hello(sum);
    }
}
```

### 익명 클래스 사용 2 - 참조값 직접 전달

익명 클래스의 참조값을 지역 변수에 담지 않고 **매개변수에 직접 전달**할 수 있습니다.

```java
package lambda.start;

import lambda.Procedure;
import java.util.Random;

// 익명 클래스의 참조값을 매개변수에 직접 전달
public class Ex1RefMainV3 {

    public static void hello(Procedure procedure) {
        long startNs = System.nanoTime();
        procedure.run();
        long endNs = System.nanoTime();
        System.out.println("실행 시간: " + (endNs - startNs) + "ns");
    }

    public static void main(String[] args) {
        hello(new Procedure() {
            @Override
            public void run() {
                int randomValue = new Random().nextInt(6) + 1;
                System.out.println("주사위 = " + randomValue);
            }
        });

        hello(new Procedure() {
            @Override
            public void run() {
                for (int i = 1; i <= 3; i++) {
                    System.out.println("i = " + i);
                }
            }
        });
    }
}
```

### 람다(Lambda) 등장

자바에서 메서드의 매개변수에 인수로 전달할 수 있는 것:
- `int`, `double` 같은 **기본형 타입**
- `Procedure`, `Member` 같은 **참조형 타입(인스턴스)**

**문제점**: 코드 조각을 전달하기 위해 클래스 정의 → 메서드 정의 → 인스턴스 생성의 복잡한 과정 필요

**해결책**: 자바 8부터 **람다**를 통해 코드 블럭을 직접 전달 가능!

### 리팩토링 - 람다 사용

```java
package lambda.start;

import lambda.Procedure;
import java.util.Random;

// 람다 사용
public class Ex1RefMainV4 {

    public static void hello(Procedure procedure) {
        long startNs = System.nanoTime();
        procedure.run();
        long endNs = System.nanoTime();
        System.out.println("실행 시간: " + (endNs - startNs) + "ns");
    }

    public static void main(String[] args) {
        hello(() -> {
            int randomValue = new Random().nextInt(6) + 1;
            System.out.println("주사위 = " + randomValue);
        });

        hello(() -> {
            for (int i = 1; i <= 3; i++) {
                System.out.println("i = " + i);
            }
        });
    }
}
```

### 코드 변화 비교

```
┌───────────────────────────────────────────────────────────────────┐
│                        코드 진화 과정                              │
├───────────────────────────────────────────────────────────────────┤
│                                                                    │
│  1. 정적 중첩 클래스                                               │
│     ┌─────────────────────────────────────────────────────────┐   │
│     │ static class Dice implements Procedure {                │   │
│     │     @Override                                           │   │
│     │     public void run() {                                 │   │
│     │         // 코드 조각                                     │   │
│     │     }                                                   │   │
│     │ }                                                       │   │
│     │ hello(new Dice());                                      │   │
│     └─────────────────────────────────────────────────────────┘   │
│                              ↓                                     │
│  2. 익명 클래스                                                    │
│     ┌─────────────────────────────────────────────────────────┐   │
│     │ hello(new Procedure() {                                 │   │
│     │     @Override                                           │   │
│     │     public void run() {                                 │   │
│     │         // 코드 조각                                     │   │
│     │     }                                                   │   │
│     │ });                                                     │   │
│     └─────────────────────────────────────────────────────────┘   │
│                              ↓                                     │
│  3. 람다                                                           │
│     ┌─────────────────────────────────────────────────────────┐   │
│     │ hello(() -> {                                           │   │
│     │     // 코드 조각                                         │   │
│     │ });                                                     │   │
│     └─────────────────────────────────────────────────────────┘   │
│                                                                    │
└───────────────────────────────────────────────────────────────────┘
```

### 주요 포인트

- `() -> {...}` 형태가 **람다 표현식**
- 클래스나 인스턴스 정의 없이 **코드 블럭을 직접 전달**
- 익명 클래스보다 훨씬 **간결한 코드**

---

## 5. 함수 vs 메서드

> **TL;DR**
> - **함수(Function)**: 독립적으로 존재, 클래스와 무관
> - **메서드(Method)**: 클래스(객체)에 속한 함수
> - 람다는 **함수**이다. 따라서 함수에 대한 이해가 필요

### 핵심 개념

| 구분 | 함수 (Function) | 메서드 (Method) |
|------|----------------|-----------------|
| 소속 | 독립적 (클래스와 무관) | 클래스(객체)에 속함 |
| 호출 방식 | `이름(매개변수)` | `객체.메서드이름(매개변수)` |
| 접근 가능 범위 | 지역/전역 변수 | 객체의 필드, 다른 메서드 |

### 상세 설명

#### C 언어 - 함수

```c
// C에서는 클래스나 객체가 없으므로, 모든 것이 함수
int add(int x, int y) {
    return x + y;
}
```

#### Java - 메서드

```java
// 자바에서는 클래스 내부에 함수를 정의 -> 메서드
public class Calculator {
    // 인스턴스 메서드
    public int add(int x, int y) {
        return x + y;
    }
}

// 사용 예
Calculator cal = new Calculator();
int result = cal.add(2, 3);  // 'add'는 메서드
```

#### Python - 함수와 메서드 모두 지원

```python
# 함수: 클래스 밖에서 독립적으로 정의
def add(x, y):
    return x + y

# 메서드: 클래스(객체) 내부에 정의
class Calculator:
    def add(self, x, y):
        return x + y

# 사용 예
print(add(2, 3))         # 함수 호출
cal = Calculator()
print(cal.add(2, 3))     # 메서드 호출
```

### 함수와 메서드의 차이

```
┌─────────────────────────────────────────────────────────────────┐
│                    함수 (Function)                               │
├─────────────────────────────────────────────────────────────────┤
│  • 독립적으로 존재하며, 클래스(객체)와 직접적인 연관이 없음      │
│  • 객체지향이 아닌 절차적 언어(C 등)에서는 모든 로직이 함수 단위 │
│  • 호출 시 객체 인스턴스 불필요                                  │
│  • 보통 이름(매개변수) 형태로 호출                               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    메서드 (Method)                               │
├─────────────────────────────────────────────────────────────────┤
│  • 클래스(또는 객체)에 속해 있는 "함수"                          │
│  • 객체의 상태(필드)에 직접 접근 가능                            │
│  • 보통 객체(인스턴스).메서드이름(매개변수) 형태로 호출          │
│  • 인스턴스 메서드, 클래스(정적) 메서드, 추상 메서드 등          │
└─────────────────────────────────────────────────────────────────┘
```

### 정리

- **메서드**는 클래스(객체) 내부의 함수, 객체의 상태와 밀접한 관련
- **함수**는 클래스(객체)와 상관없이 독립적으로 호출 가능한 로직의 단위
- 메서드는 객체지향에서 **클래스 안에 정의하는 특별한 함수**

> **람다는 함수이다!** 따라서 람다를 제대로 이해하기 위해서는 함수에 대해 알아야 한다.

---

## 6. 람다 시작

> **TL;DR**
> - 람다는 `(매개변수) -> { 본문 }` 형태로 표현
> - 이름, 반환 타입은 생략하고 매개변수와 본문만 작성
> - 익명 클래스보다 훨씬 간결한 코드

### 핵심 개념

람다 표현식 기본 형태:
```
(매개변수) -> { 본문 }
```

- `()`: 매개변수
- `->`: 람다 연산자 (화살표)
- `{}`: 코드 본문

### 익명 클래스를 람다로 1 - 매개변수 없는 경우

#### Procedure 인터페이스

```java
package lambda;

public interface Procedure {
    void run();  // 매개변수 없음, 반환값 없음
}
```

#### 익명 클래스 버전

```java
package lambda.lambda1;

import lambda.Procedure;

public class ProcedureMain1 {

    public static void main(String[] args) {
        Procedure procedure = new Procedure() {
            @Override
            public void run() {
                System.out.println("hello! lambda");
            }
        };

        procedure.run();
    }
}
```

#### 람다 버전

```java
package lambda.lambda1;

import lambda.Procedure;

public class ProcedureMain2 {

    public static void main(String[] args) {
        Procedure procedure = () -> {
            System.out.println("hello! lambda");
        };

        procedure.run();
    }
}
```

**실행 결과**
```
hello! lambda
```

### 익명 클래스를 람다로 2 - 매개변수 있는 경우

#### MyFunction 인터페이스

```java
package lambda;

public interface MyFunction {
    int apply(int a, int b);  // 매개변수 2개, int 반환
}
```

- **패키지 위치 주의**: `lambda` 패키지에 위치 (여러 곳에서 사용 예정)

#### 익명 클래스 버전

```java
package lambda.lambda1;

import lambda.MyFunction;

public class MyFunctionMain1 {

    public static void main(String[] args) {
        MyFunction myFunction = new MyFunction() {
            @Override
            public int apply(int a, int b) {
                return a + b;
            }
        };

        int result = myFunction.apply(1, 2);
        System.out.println("result = " + result);
    }
}
```

#### 람다 버전

```java
package lambda.lambda1;

import lambda.MyFunction;

public class MyFunctionMain2 {

    public static void main(String[] args) {
        MyFunction myFunction = (int a, int b) -> {
            return a + b;
        };

        int result = myFunction.apply(1, 2);
        System.out.println("result = " + result);
    }
}
```

**실행 결과**
```
result = 3
```

### 람다 표현식 비교

```
┌─────────────────────────────────────────────────────────────────┐
│                     익명 클래스 vs 람다                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  매개변수 없는 경우 (Procedure)                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 익명 클래스:                                            │    │
│  │ new Procedure() {                                       │    │
│  │     @Override                                           │    │
│  │     public void run() {                                 │    │
│  │         System.out.println("hello");                    │    │
│  │     }                                                   │    │
│  │ }                                                       │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 람다:                                                   │    │
│  │ () -> { System.out.println("hello"); }                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  매개변수 있는 경우 (MyFunction)                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 익명 클래스:                                            │    │
│  │ new MyFunction() {                                      │    │
│  │     @Override                                           │    │
│  │     public int apply(int a, int b) {                    │    │
│  │         return a + b;                                   │    │
│  │     }                                                   │    │
│  │ }                                                       │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 람다:                                                   │    │
│  │ (int a, int b) -> { return a + b; }                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 람다 표현식 정리

| 인터페이스 메서드 | 람다 표현식 |
|-----------------|-----------|
| `void run()` | `() -> { ... }` |
| `int apply(int a, int b)` | `(int a, int b) -> { return ...; }` |

### 주요 포인트

- 람다 사용 시 **이름, 반환 타입 생략**
- **매개변수와 본문만** 간단하게 작성
- 익명 클래스의 모든 부분을 생략하고 **꼭 필요한 것만** 작성

---

## 전체 요약

| 개념 | 설명 |
|------|------|
| 값 매개변수화 | 값(숫자, 문자열)을 매개변수로 전달하여 메서드 동작을 달리함 |
| 동작 매개변수화 | 코드 조각(로직)을 매개변수로 전달하여 메서드 동작을 달리함 |
| 함수 vs 메서드 | 함수는 독립적, 메서드는 클래스에 종속 |
| 람다 | `(매개변수) -> { 본문 }` 형태로 코드 블럭을 간결하게 전달 |

## 학습 체크리스트

- [ ] 값 매개변수화 개념 이해
- [ ] 동작 매개변수화 개념 이해
- [ ] Procedure, MyFunction 인터페이스 작성
- [ ] 익명 클래스를 람다로 변환 실습
- [ ] 함수와 메서드의 차이 이해

---

## 면접 질문

### 초급 개발자 (Junior)

**Q1. 람다(Lambda)란 무엇인가요?**
<details>
<summary>답안 보기</summary>

람다는 익명 함수(Anonymous Function)를 간결하게 표현하는 방법입니다.
- `(매개변수) -> { 본문 }` 형태로 표현
- 클래스나 인스턴스 정의 없이 코드 블럭을 직접 전달 가능
- 자바 8부터 도입됨

</details>

**Q2. 값 매개변수화와 동작 매개변수화의 차이는 무엇인가요?**
<details>
<summary>답안 보기</summary>

- **값 매개변수화**: 숫자, 문자열 같은 값을 매개변수로 전달
- **동작 매개변수화**: 코드 조각(로직, 동작)을 매개변수로 전달
- 둘 다 메서드의 재사용성을 높이기 위한 방법

</details>

### 중급 개발자 (Mid-Level)

**Q3. 익명 클래스 대신 람다를 사용하면 어떤 이점이 있나요?**
<details>
<summary>답안 보기</summary>

- **코드 간결성**: 익명 클래스의 보일러플레이트 코드 제거
- **가독성 향상**: 핵심 로직에만 집중 가능
- **함수형 프로그래밍 지원**: 함수를 일급 객체처럼 다룰 수 있음

```java
// 익명 클래스 (장황함)
new Procedure() {
    @Override
    public void run() {
        System.out.println("hello");
    }
}

// 람다 (간결함)
() -> System.out.println("hello")
```

</details>

**Q4. 함수와 메서드의 차이점을 설명해주세요.**
<details>
<summary>답안 보기</summary>

- **함수(Function)**: 독립적으로 존재, 클래스에 속하지 않음
- **메서드(Method)**: 클래스(객체)에 속한 함수, 객체의 상태에 접근 가능
- 자바에서는 모든 것이 클래스에 속하므로 기본적으로 메서드만 존재
- 람다는 함수의 개념을 자바에 도입한 것

</details>

### 고급 개발자 (Senior)

**Q5. 동작 매개변수화가 필요한 실무 상황의 예를 들어주세요.**
<details>
<summary>답안 보기</summary>

- **정렬 기준**: `Comparator`를 전달하여 다양한 정렬 기준 적용
- **필터링**: `Predicate`를 전달하여 조건에 맞는 데이터 필터링
- **비동기 콜백**: 작업 완료 후 실행할 로직 전달
- **템플릿 메서드 패턴**: 알고리즘의 골격은 유지하고 특정 단계만 변경
- **전략 패턴**: 런타임에 알고리즘을 교체

```java
// 예: 정렬 기준 전달
list.sort((a, b) -> a.getName().compareTo(b.getName()));

// 예: 필터링 조건 전달
list.stream().filter(user -> user.getAge() > 20).collect(toList());
```

</details>

---

## 네비게이션

- [이전: Part 1 - 값 매개변수화, 동작 매개변수화](./1-람다가필요한이유-part1.md)
- [다음: 2. 람다](./2-람다.md)
