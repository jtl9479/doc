# 1. 람다가 필요한 이유 - Part 1

**출처**: 인프런 - 김영한의 실전 자바 고급 3편
**작성일**: 2026-01-03

> **문서 구성**
> - Part 1: 프로젝트 환경 구성, 값 매개변수화, 동작 매개변수화
> - Part 2: 익명 클래스와 람다, 함수 vs 메서드, 람다 시작

---

## 학습 목표

이 챕터를 학습한 후 다음을 할 수 있습니다:
- [ ] 값 매개변수화(Value Parameterization)의 개념을 설명할 수 있다
- [ ] 동작 매개변수화(Behavior Parameterization)의 개념을 설명할 수 있다
- [ ] 코드 조각을 메서드에 전달하는 방법을 이해할 수 있다
- [ ] 익명 클래스를 람다로 변환할 수 있다
- [ ] 함수와 메서드의 차이를 설명할 수 있다

## 연관 개념

- **선행 학습 권장**: 중급 1편 - 중첩 클래스, 내부 클래스, 익명 클래스
- **후속 학습**: 2. 람다, 3. 함수형 인터페이스
- **관련 챕터**: 자바 중급 1편 - 익명 클래스 활용

---

## 목차

1. [프로젝트 환경 구성](#1-프로젝트-환경-구성)
2. [람다가 필요한 이유1 - 값 매개변수화](#2-람다가-필요한-이유1---값-매개변수화)
3. [람다가 필요한 이유2 - 동작 매개변수화](#3-람다가-필요한-이유2---동작-매개변수화)

---

## 1. 프로젝트 환경 구성

> **TL;DR**
> - 프로젝트 이름: java-adv3
> - JDK 버전: 21 이상 필수
> - Build system: IntelliJ

### 핵심 개념

| 항목 | 설정값 |
|------|--------|
| Name | java-adv3 |
| Language | Java |
| Build system | IntelliJ |
| JDK | 21 이상 (Oracle OpenJDK 또는 Eclipse Temurin) |

### 주요 포인트

- IntelliJ는 영문 버전 사용 권장 (검색 자료가 영문으로 더 많음)
- 한글 언어팩 설치되어 있다면: `Settings > Plugins > Installed > Korean Language Pack 체크 해제`

---

## 2. 람다가 필요한 이유1 - 값 매개변수화

> **TL;DR**
> - 변하는 부분과 변하지 않는 부분을 분리하는 것이 핵심
> - 문자열, 숫자 같은 값(Value)을 매개변수로 받아 메서드 재사용성을 높임
> - 이를 **값 매개변수화(Value Parameterization)**라 함

### 학습 전 체크 사항

```
자바 람다에 대해 제대로 이해하려면 먼저 내부 클래스에 대해 확실한 이해가 필요하다.
내부 클래스에 대한 개념이 약하다면 중급 1편 - 중첩 클래스, 내부 클래스를 먼저 복습하자.
```

### 핵심 개념

프로그래밍에서 중복을 제거하고 좋은 코드를 유지하는 핵심:
- **변하는 부분**과 **변하지 않는 부분**을 분리
- 변하지 않는 부분은 그대로 유지
- 변하는 부분은 **외부에서 전달** 받아서 처리

### 상세 설명

#### 리팩토링 전 - 중복 코드

```java
package lambda.start;

public class Ex0Main {

    public static void helloJava() {
        System.out.println("프로그램 시작");   // 변하지 않는 부분
        System.out.println("Hello Java");      // 변하는 부분
        System.out.println("프로그램 종료");   // 변하지 않는 부분
    }

    public static void helloSpring() {
        System.out.println("프로그램 시작");   // 변하지 않는 부분
        System.out.println("Hello Spring");    // 변하는 부분
        System.out.println("프로그램 종료");   // 변하지 않는 부분
    }

    public static void main(String[] args) {
        helloJava();
        helloSpring();
    }
}
```

#### 리팩토링 후 - 값 매개변수화 적용

```java
package lambda.start;

public class Ex0RefMain {

    public static void hello(String str) {
        System.out.println("프로그램 시작");  // 변하지 않는 부분
        System.out.println(str);              // str: 변하는 부분
        System.out.println("프로그램 종료");  // 변하지 않는 부분
    }

    public static void main(String[] args) {
        hello("hello Java");
        hello("hello Spring");
    }
}
```

**실행 결과**
```
프로그램 시작
hello Java
프로그램 종료
프로그램 시작
hello Spring
프로그램 종료
```

### 값 매개변수화(Value Parameterization) 정의

```
┌─────────────────────────────────────────────────────────────┐
│              값 매개변수화 (Value Parameterization)          │
├─────────────────────────────────────────────────────────────┤
│  문자값(Value), 숫자값(Value)처럼 구체적인 값을              │
│  메서드(함수) 안에 두는 것이 아니라,                         │
│  매개변수(파라미터)를 통해 외부에서 전달 받도록 해서,        │
│  메서드의 동작을 달리하고, 재사용성을 높이는 방법           │
└─────────────────────────────────────────────────────────────┘
```

### 주요 포인트

- 변하는 값을 메서드 내부에 두지 않고 **외부에서 전달**
- 메서드(함수)의 **재사용성**이 높아짐
- `String`, `int` 등의 데이터 타입을 매개변수로 전달

---

## 3. 람다가 필요한 이유2 - 동작 매개변수화

> **TL;DR**
> - 단순한 값이 아닌 **코드 조각(동작)을 전달**해야 하는 경우가 있음
> - 자바에서는 인터페이스를 정의하고 구현 클래스의 인스턴스를 전달
> - 이를 **동작 매개변수화(Behavior Parameterization)**라 함

### 핵심 개념

값 매개변수화로는 해결할 수 없는 경우:
- 전달해야 하는 것이 단순한 문자열/숫자가 아닌 **코드 조각**일 때
- 코드 조각은 보통 **메서드(함수)에 정의**됨
- 자바에서는 메서드만 전달할 수 없으므로 **인스턴스를 전달**하고 해당 인스턴스의 메서드를 호출

### 상세 설명

#### 문제 상황 - 리팩토링 전

```java
package lambda.start;

import java.util.Random;

public class Ex1Main {

    public static void helloDice() {
        long startNs = System.nanoTime();       // 변하지 않는 부분

        //코드 조각 시작 (변하는 부분)
        int randomValue = new Random().nextInt(6) + 1;
        System.out.println("주사위 = " + randomValue);
        //코드 조각 종료

        long endNs = System.nanoTime();         // 변하지 않는 부분
        System.out.println("실행 시간: " + (endNs - startNs) + "ns");
    }

    public static void helloSum() {
        long startNs = System.nanoTime();       // 변하지 않는 부분

        //코드 조각 시작 (변하는 부분)
        for (int i = 1; i <= 3; i++) {
            System.out.println("i = " + i);
        }
        //코드 조각 종료

        long endNs = System.nanoTime();         // 변하지 않는 부분
        System.out.println("실행 시간: " + (endNs - startNs) + "ns");
    }

    public static void main(String[] args) {
        helloDice();
        helloSum();
    }
}
```

**실행 결과**
```
주사위 = 2
실행 시간: 2882959ns
i = 1
i = 2
i = 3
실행 시간: 191083ns
```

#### 해결 방법 - 인터페이스 정의

```java
package lambda;

public interface Procedure {
    void run();
}
```

- **패키지 위치 주의**: `lambda` 패키지에 위치 (다른 곳에서도 사용 예정)
- `run()` 메서드: 매개변수 없음, 반환값 없음

#### 리팩토링 후 - 정적 중첩 클래스 사용

```java
package lambda.start;

import lambda.Procedure;
import java.util.Random;

public class Ex1RefMainV1 {

    public static void hello(Procedure procedure) {
        long startNs = System.nanoTime();
        //코드 조각 시작
        procedure.run();
        //코드 조각 종료
        long endNs = System.nanoTime();
        System.out.println("실행 시간: " + (endNs - startNs) + "ns");
    }

    static class Dice implements Procedure {
        @Override
        public void run() {
            int randomValue = new Random().nextInt(6) + 1;
            System.out.println("주사위 = " + randomValue);
        }
    }

    static class Sum implements Procedure {
        @Override
        public void run() {
            for (int i = 1; i <= 3; i++) {
                System.out.println("i = " + i);
            }
        }
    }

    public static void main(String[] args) {
        Procedure dice = new Dice();
        Procedure sum = new Sum();

        hello(dice);
        hello(sum);
    }
}
```

**실행 결과**
```
주사위 = 6
실행 시간: 3245875ns
i = 1
i = 2
i = 3
실행 시간: 259125ns
```

### 동작 매개변수화 흐름도

```
┌─────────────────────────────────────────────────────────────────┐
│                     동작 매개변수화 흐름                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. 인터페이스 정의                                             │
│      ┌──────────────────────┐                                   │
│      │ interface Procedure  │                                   │
│      │   void run();        │                                   │
│      └──────────────────────┘                                   │
│                 ↓                                                │
│   2. 구현 클래스 생성 (코드 조각 정의)                           │
│      ┌──────────────────────┐  ┌──────────────────────┐        │
│      │ class Dice           │  │ class Sum            │        │
│      │   implements         │  │   implements         │        │
│      │   Procedure          │  │   Procedure          │        │
│      │   run() {...}        │  │   run() {...}        │        │
│      └──────────────────────┘  └──────────────────────┘        │
│                 ↓                                                │
│   3. 인스턴스 생성 및 전달                                       │
│      hello(new Dice());  // 주사위 로직 실행                    │
│      hello(new Sum());   // 계산 로직 실행                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 동작 매개변수화(Behavior Parameterization) 정의

```
┌─────────────────────────────────────────────────────────────┐
│           동작 매개변수화 (Behavior Parameterization)        │
├─────────────────────────────────────────────────────────────┤
│  코드 조각(코드의 동작 방법, 로직, Behavior)을               │
│  메서드(함수) 안에 두는 것이 아니라,                         │
│  매개변수(파라미터)를 통해 외부에서 전달 받도록 해서,        │
│  메서드의 동작을 달리하고, 재사용성을 높이는 방법           │
└─────────────────────────────────────────────────────────────┘
```

### 값 매개변수화 vs 동작 매개변수화

| 구분 | 값 매개변수화 | 동작 매개변수화 |
|------|-------------|---------------|
| 전달하는 것 | 값 (숫자, 문자열 등) | 동작 (코드 조각, 로직) |
| 방법 | String, int 등 기본/참조 타입 전달 | 인터페이스 구현 인스턴스 전달 |
| 목적 | 메서드의 동작을 달리함 | 메서드의 동작을 달리함 |
| 예시 | `hello("Java")` | `hello(new Dice())` |

### 주요 포인트

- 자바에서 메서드만 독립적으로 전달하는 것은 불가능
- **인스턴스를 전달**하고 해당 인스턴스의 **메서드를 호출**하는 방식으로 해결
- **다형성**을 활용하여 외부에서 전달되는 인스턴스에 따라 다른 코드 조각 실행

### 정리

| 전달하려는 것 | 방법 |
|-------------|------|
| 문자열, 숫자 같은 **값** | `String`, `int` 타입으로 직접 전달 |
| **코드 조각** | 인터페이스 구현 인스턴스 전달 후 메서드 호출 |

---

## 정리

| 개념 | 설명 |
|------|------|
| 값 매개변수화 | 값(숫자, 문자열)을 외부에서 전달받아 메서드 동작을 달리함 |
| 동작 매개변수화 | 코드 조각(로직)을 외부에서 전달받아 메서드 동작을 달리함 |
| 핵심 원칙 | 변하는 부분과 변하지 않는 부분을 분리 |

---

## 네비게이션

- [다음: Part 2 - 익명 클래스와 람다, 함수 vs 메서드, 람다 시작](./1-람다가필요한이유-part2.md)
