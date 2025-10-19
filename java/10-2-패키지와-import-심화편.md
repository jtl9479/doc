# 10-2장: 패키지와 import (심화편)

> **이전 내용 요약**: 10-1장에서는 패키지의 개념, 선언 방법, import 사용법, 실전 프로젝트를 다뤘습니다.

> **이번 장의 목표**: 접근 제어자, JAR 파일, 패키지 설계 패턴을 학습하고, FAQ와 면접 질문으로 완벽하게 마스터합니다.

**⏱️ 예상 학습 시간**: 2-3시간
**난이도**: ⭐⭐⭐☆☆ (3/5)

---

## 📚 목차
- [접근 제어자 완벽 가이드](#-접근-제어자-완벽-가이드)
- [JAR 파일과 클래스 경로](#-jar-파일과-클래스-경로)
- [패키지 설계 패턴](#-패키지-설계-패턴)
- [FAQ (자주 묻는 질문)](#-faq)
- [면접 질문 리스트](#-면접-질문-리스트)
- [핵심 정리](#-핵심-정리)
- [다음 단계](#-다음-단계)
- [추가 학습 자료](#-추가-학습-자료)

---

## 🔐 접근 제어자 완벽 가이드

### 4가지 접근 제어자

| 접근 제어자 | 같은 클래스 | 같은 패키지 | 자식 클래스 | 다른 패키지 |
|------------|------------|------------|-----------|-----------|
| **public** | ✅ | ✅ | ✅ | ✅ |
| **protected** | ✅ | ✅ | ✅ | ❌ |
| **default** | ✅ | ✅ | ❌ | ❌ |
| **private** | ✅ | ❌ | ❌ | ❌ |

### 상세 설명과 예제

```java
// com/example/demo/AccessDemo.java
package com.example.demo;

public class AccessDemo {
    public int publicField = 1;        // 어디서나 접근 가능
    protected int protectedField = 2;  // 같은 패키지 + 자식 클래스
    int defaultField = 3;              // 같은 패키지만 (package-private)
    private int privateField = 4;      // 같은 클래스만

    public void publicMethod() {
        System.out.println("public 메서드");
    }

    protected void protectedMethod() {
        System.out.println("protected 메서드");
    }

    void defaultMethod() {  // 접근 제어자 생략 = default
        System.out.println("default 메서드");
    }

    private void privateMethod() {
        System.out.println("private 메서드");
    }

    // 같은 클래스 내에서는 모든 멤버 접근 가능
    public void testAccess() {
        System.out.println(publicField);     // ✅
        System.out.println(protectedField);  // ✅
        System.out.println(defaultField);    // ✅
        System.out.println(privateField);    // ✅

        publicMethod();     // ✅
        protectedMethod();  // ✅
        defaultMethod();    // ✅
        privateMethod();    // ✅
    }
}
```

```java
// com/example/demo/SamePackageTest.java (같은 패키지)
package com.example.demo;

public class SamePackageTest {
    public void test() {
        AccessDemo demo = new AccessDemo();

        System.out.println(demo.publicField);      // ✅ public
        System.out.println(demo.protectedField);   // ✅ protected
        System.out.println(demo.defaultField);     // ✅ default
        // System.out.println(demo.privateField);  // ❌ private (컴파일 에러)

        demo.publicMethod();      // ✅
        demo.protectedMethod();   // ✅
        demo.defaultMethod();     // ✅
        // demo.privateMethod();  // ❌ (컴파일 에러)
    }
}
```

```java
// com/example/other/DifferentPackageTest.java (다른 패키지)
package com.example.other;

import com.example.demo.AccessDemo;

public class DifferentPackageTest {
    public void test() {
        AccessDemo demo = new AccessDemo();

        System.out.println(demo.publicField);      // ✅ public만 가능
        // System.out.println(demo.protectedField);  // ❌
        // System.out.println(demo.defaultField);    // ❌
        // System.out.println(demo.privateField);    // ❌

        demo.publicMethod();      // ✅ public만 가능
        // demo.protectedMethod();  // ❌
        // demo.defaultMethod();    // ❌
        // demo.privateMethod();    // ❌
    }
}
```

```java
// com/example/other/SubClassTest.java (다른 패키지의 자식 클래스)
package com.example.other;

import com.example.demo.AccessDemo;

public class SubClassTest extends AccessDemo {
    public void test() {
        // 상속받은 멤버 접근
        System.out.println(publicField);      // ✅ public
        System.out.println(protectedField);   // ✅ protected (자식이므로)
        // System.out.println(defaultField);  // ❌ default
        // System.out.println(privateField);  // ❌ private

        publicMethod();      // ✅
        protectedMethod();   // ✅ protected (자식이므로)
        // defaultMethod();  // ❌
        // privateMethod();  // ❌

        // 단, 다른 객체의 protected 멤버는 접근 불가
        AccessDemo demo = new AccessDemo();
        // System.out.println(demo.protectedField);  // ❌ (자신의 상속받은 것만 가능)
    }
}
```

### 실무 사용 가이드

```java
// ✅ 실무 권장 사용법
public class User {
    // 1. 필드는 private (캡슐화)
    private String name;
    private int age;

    // 2. 생성자는 public (객체 생성 허용)
    public User(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // 3. Getter/Setter는 public (외부 접근 허용)
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    // 4. 내부 헬퍼 메서드는 private
    private boolean validateAge(int age) {
        return age >= 0 && age <= 150;
    }

    // 5. 상속용 메서드는 protected
    protected void internalLogic() {
        System.out.println("자식 클래스에서 사용 가능");
    }

    // 6. 같은 패키지 내 협력 메서드는 default
    void packageInternalMethod() {
        System.out.println("같은 패키지에서만 사용");
    }
}
```

---

## 📦 JAR 파일과 클래스 경로

### JAR 파일이란?

**JAR (Java Archive)**: 여러 클래스 파일과 리소스를 하나로 압축한 파일

```
ZIP 형식의 압축 파일
├── com/
│   └── library/
│        ├── model/
│        │   ├── Book.class
│        │   └── Member.class
│        ├── service/
│        │   └── BookService.class
│        └── Main.class
├── META-INF/
│   └── MANIFEST.MF  (메타 정보)
└── resources/
    └── config.properties
```

### JAR 파일 생성 (명령줄)

```bash
# 1. 클래스 파일 컴파일
javac -d bin src/com/library/**/*.java

# 2. JAR 파일 생성
cd bin
jar -cvf library.jar com/

# 옵션 설명:
# c: create (생성)
# v: verbose (상세 출력)
# f: file (파일명 지정)

# 3. JAR 파일 내용 확인
jar -tf library.jar

# 4. 실행 가능한 JAR 생성 (Main 클래스 지정)
jar -cvfe library.jar com.library.Main com/

# e: entry point (main 클래스 지정)
```

### JAR 파일 사용

```bash
# 1. JAR 파일 실행
java -jar library.jar

# 2. JAR 파일을 클래스 경로에 추가하여 실행
java -cp library.jar com.library.Main

# 3. 여러 JAR 파일 사용 (Windows)
java -cp "lib1.jar;lib2.jar;lib3.jar" com.Main

# 3-2. 여러 JAR 파일 사용 (Linux/Mac)
java -cp "lib1.jar:lib2.jar:lib3.jar" com.Main
```

### CLASSPATH 환경 변수

```bash
# Windows
set CLASSPATH=C:\lib\library.jar;C:\classes

# Linux/Mac
export CLASSPATH=/lib/library.jar:/classes

# Java 실행 시 자동으로 이 경로에서 클래스 검색
java com.library.Main
```

### Maven/Gradle로 JAR 관리

**Maven (pom.xml)**:
```xml
<dependencies>
    <dependency>
        <groupId>com.google.gson</groupId>
        <artifactId>gson</artifactId>
        <version>2.10</version>
    </dependency>
</dependencies>
```

**Gradle (build.gradle)**:
```groovy
dependencies {
    implementation 'com.google.gson:gson:2.10'
}
```

---

## 🏗️ 패키지 설계 패턴

### 패턴 1: 계층형 구조 (Layered Architecture)

```java
com.company.project/
  ├── controller/      // 프레젠테이션 계층
  │   ├── UserController.java
  │   └── ProductController.java
  ├── service/         // 비즈니스 로직 계층
  │   ├── UserService.java
  │   └── ProductService.java
  ├── repository/      // 데이터 접근 계층
  │   ├── UserRepository.java
  │   └── ProductRepository.java
  ├── model/           // 도메인 모델
  │   ├── User.java
  │   └── Product.java
  └── util/            // 유틸리티
      └── DateUtil.java

// 장점: 계층별 역할 명확, 이해하기 쉬움
// 단점: 도메인이 여러 패키지에 분산
// 적합: 소규모~중규모 프로젝트
```

### 패턴 2: 도메인 중심 구조 (Domain-Driven Design)

```java
com.company.ecommerce/
  ├── user/
  │   ├── domain/
  │   │   └── User.java
  │   ├── service/
  │   │   └── UserService.java
  │   ├── repository/
  │   │   └── UserRepository.java
  │   └── controller/
  │       └── UserController.java
  ├── order/
  │   ├── domain/
  │   │   └── Order.java
  │   ├── service/
  │   │   └── OrderService.java
  │   └── repository/
  │       └── OrderRepository.java
  └── product/
      ├── domain/
      ├── service/
      └── repository/

// 장점: 도메인별 독립성, 대규모 팀 협업 용이
// 단점: 구조 복잡, 초기 설정 비용
// 적합: 대규모 프로젝트, 마이크로서비스
```

### 패턴 3: 기능 중심 구조 (Feature-Based)

```java
com.company.app/
  ├── authentication/
  │   ├── LoginController.java
  │   ├── AuthService.java
  │   └── User.java
  ├── payment/
  │   ├── PaymentController.java
  │   ├── PaymentService.java
  │   └── Payment.java
  └── notification/
      ├── NotificationService.java
      └── Notification.java

// 장점: 기능별 응집도 높음, 기능 추가/제거 용이
// 단점: 공통 모델 관리 어려움
// 적합: 빠르게 변화하는 프로젝트
```

### 실무 패키지 설계 예시

```java
// Spring Boot 프로젝트 표준 구조
com.company.projectname/
  ├── config/              // 설정
  │   ├── SecurityConfig.java
  │   └── DatabaseConfig.java
  ├── domain/              // 도메인 모델
  │   ├── user/
  │   │   ├── User.java
  │   │   ├── UserRepository.java
  │   │   └── UserService.java
  │   └── order/
  │       ├── Order.java
  │       ├── OrderRepository.java
  │       └── OrderService.java
  ├── web/                 // 웹 계층
  │   ├── controller/
  │   │   ├── UserController.java
  │   │   └── OrderController.java
  │   └── dto/
  │       ├── UserDto.java
  │       └── OrderDto.java
  ├── infrastructure/      // 인프라
  │   ├── cache/
  │   └── storage/
  ├── common/              // 공통
  │   ├── exception/
  │   │   └── CustomException.java
  │   └── util/
  │       └── DateUtils.java
  └── ProjectNameApplication.java  // Main 클래스
```

---

## ❓ FAQ

<details>
<summary><strong>Q1: default 패키지는 왜 사용하면 안 되나요?</strong></summary>

**A**: **다른 패키지에서 import할 수 없고, 이름 충돌 위험이 크기 때문입니다.**

**상세 설명**:

**1. Import 불가**
```java
// MyClass.java (default 패키지, package 선언 없음)
public class MyClass {
    public void hello() {
        System.out.println("Hello");
    }
}

// com/example/Main.java
package com.example;

// import MyClass;  // ❌ 불가능! default 패키지는 import 안 됨
// 따라서 MyClass를 사용할 수 없음!

public class Main {
    public static void main(String[] args) {
        // MyClass obj = new MyClass();  // 컴파일 에러!
    }
}
```

**2. 이름 충돌**
```java
// default 패키지에 User.java
public class User { }

// 다른 라이브러리도 User.java를 default 패키지에 둔다면?
// → 이름 충돌! 같은 이름 클래스 사용 불가
```

**3. 모듈 시스템 미지원**
```java
// Java 9+ 모듈 시스템에서 default 패키지는 사용 불가
```

**실무 팁**:
💡 **모든 클래스는 반드시 패키지에 포함**시키세요. 간단한 테스트 코드라도 `test` 패키지에 넣는 것을 권장합니다.

```java
// ✅ 간단한 테스트도 패키지 선언
package test;

public class QuickTest {
    public static void main(String[] args) {
        System.out.println("Test");
    }
}
```

</details>

<details>
<summary><strong>Q2: import java.util.*; 와 개별 import의 차이는 무엇인가요?</strong></summary>

**A**: **성능은 동일하지만, 가독성과 유지보수 측면에서 개별 import가 우수합니다.**

**성능 비교**:
```java
// 1. 와일드카드 import
import java.util.*;

// 2. 개별 import
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

// 컴파일 시간: 거의 동일 (밀리초 단위 차이)
// 런타임 성능: 완전히 동일 (import는 컴파일 타임에만 사용)
// 클래스 파일 크기: 동일
```

**가독성 비교**:
```java
// ❌ 와일드카드: 어떤 클래스를 사용하는지 불명확
import java.util.*;
import java.io.*;
import java.net.*;

public class Demo {
    // List, File, URL 중 어느 패키지의 것인지?
    // 코드를 봐야만 알 수 있음
}

// ✅ 개별 import: 명확
import java.util.List;
import java.util.ArrayList;
import java.io.File;

public class Demo {
    // 사용 클래스가 명확히 보임
}
```

**이름 충돌**:
```java
// ❌ 와일드카드로 충돌 발생
import java.util.*;   // java.util.Date
import java.sql.*;    // java.sql.Date

public class Demo {
    public static void main(String[] args) {
        Date date = new Date();  // 어느 Date? 모호함!
    }
}

// ✅ 개별 import로 명확하게
import java.util.Date;  // 이것만 사용

public class Demo {
    public static void main(String[] args) {
        Date date = new Date();  // java.util.Date 명확
    }
}
```

**IDE 지원**:
```java
// 와일드카드는 IDE의 자동 import 방해
// 개별 import는 IDE가 미사용 import 탐지 가능

// IntelliJ: Ctrl+Alt+O (import 최적화)
// Eclipse: Ctrl+Shift+O (import 정리)
```

**실무 팁**:
💡 **개별 import를 사용**하세요. IDE가 자동으로 관리해주므로 불편함이 없습니다.

</details>

<details>
<summary><strong>Q3: 한 파일에 여러 public 클래스를 둘 수 없나요?</strong></summary>

**A**: **불가능합니다. 한 파일에는 하나의 public 클래스만 가능하며, 파일명과 동일해야 합니다.**

**규칙**:
```java
// ❌ MyClass.java에 여러 public 클래스 (컴파일 에러!)
package com.example;

public class MyClass {  // OK: 파일명과 동일
}

public class AnotherClass {  // ❌ 에러! 두 번째 public 클래스
}

// error: class AnotherClass is public, should be declared in a file named AnotherClass.java
```

**해결 방법 1: 파일 분리**
```java
// MyClass.java
package com.example;

public class MyClass {
}

// AnotherClass.java (별도 파일)
package com.example;

public class AnotherClass {
}
```

**해결 방법 2: default 접근자 사용**
```java
// MyClass.java
package com.example;

public class MyClass {  // public (파일명과 동일)
}

class HelperClass {  // default (public 아님) - OK!
    // 같은 패키지 내에서만 사용하는 헬퍼 클래스
}

class UtilClass {  // default - OK!
}
```

**왜 이런 규칙이 있나?**
```
1. 파일 검색 용이성
   - MyClass를 찾으려면? → MyClass.java 파일 열면 됨
   - 파일명 = 클래스명 규칙으로 빠른 탐색

2. 컴파일러 최적화
   - 컴파일러가 파일명으로 public 클래스 빠르게 찾음

3. 가독성
   - 한 파일에 하나의 주요 클래스로 명확성 확보
```

**실무 팁**:
💡 **public 클래스 하나 + 내부 헬퍼 클래스(default)** 패턴이 일반적입니다.

</details>

<details>
<summary><strong>Q4: 패키지 구조를 바꾸면 어떻게 되나요?</strong></summary>

**A**: **패키지명이 변경되면 모든 import 문과 FQCN을 수정해야 합니다.**

**변경 전**:
```java
// com/example/old/User.java
package com.example.old;

public class User {
    private String name;
    // ...
}

// com/example/Main.java
package com.example;

import com.example.old.User;  // 기존 패키지

public class Main {
    public static void main(String[] args) {
        User user = new User();
    }
}
```

**변경 후**:
```java
// com/example/new_location/User.java (패키지 변경)
package com.example.new_location;  // 패키지명 변경!

public class User {
    private String name;
    // ...
}

// com/example/Main.java
package com.example;

// import com.example.old.User;  // ❌ 더 이상 찾을 수 없음!
import com.example.new_location.User;  // ✅ 수정 필요

public class Main {
    public static void main(String[] args) {
        User user = new User();  // 이제 새 패키지의 User
    }
}
```

**IDE 리팩토링 기능 사용**:
```
IntelliJ IDEA:
1. 패키지 선택 → Refactor → Move (F6)
2. 새 패키지 위치 지정
3. IDE가 모든 import 자동 수정!

Eclipse:
1. 패키지 우클릭 → Refactor → Move
2. IDE가 모든 참조 자동 업데이트
```

**주의사항**:
```java
// ⚠️ 주의 1: 외부 프로젝트가 참조 중이라면?
// 다른 프로젝트의 import도 수정 필요 → API 버전 관리 필요

// ⚠️ 주의 2: 리플렉션 사용 시
Class<?> clazz = Class.forName("com.example.old.User");  // 문자열로 참조
// → 리플렉션 코드도 수정 필요

// ⚠️ 주의 3: 설정 파일
// XML, properties 파일에 패키지명이 문자열로 있다면 수정 필요
```

**실무 팁**:
💡 **패키지 구조는 초기 설계 시 신중히 결정**하세요. 나중에 변경하면 영향 범위가 큽니다.

</details>

<details>
<summary><strong>Q5: static import는 언제 사용하나요?</strong></summary>

**A**: **자주 사용하는 정적 멤버(상수, 메서드)를 클래스명 없이 사용할 때 편리합니다.**

**일반 import vs static import**:
```java
// 1. 일반 import
import java.lang.Math;

public class Demo {
    public static void main(String[] args) {
        double result = Math.sqrt(16);  // 클래스명.메서드명
        double pi = Math.PI;            // 클래스명.상수
        System.out.println(result);
    }
}

// 2. static import
import static java.lang.Math.sqrt;
import static java.lang.Math.PI;

public class Demo {
    public static void main(String[] args) {
        double result = sqrt(16);  // 클래스명 생략!
        double pi = PI;            // 클래스명 생략!
        System.out.println(result);
    }
}

// 3. static 와일드카드 import
import static java.lang.Math.*;

public class Demo {
    public static void main(String[] args) {
        double result = sqrt(16);
        double pi = PI;
        double max = max(10, 20);
        System.out.println(result);
    }
}
```

**좋은 사용 예**:
```java
// ✅ 1. 상수 사용
import static java.time.temporal.ChronoUnit.DAYS;
import static java.time.temporal.ChronoUnit.HOURS;

long daysBetween = DAYS.between(start, end);
long hoursBetween = HOURS.between(start, end);

// ✅ 2. 유틸리티 메서드
import static com.company.util.StringUtils.isEmpty;
import static com.company.util.StringUtils.isNotEmpty;

if (isEmpty(name)) {
    // ...
}

// ✅ 3. 테스트 코드 (매우 흔한 사용)
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.assertFalse;

@Test
public void testSomething() {
    assertEquals(3, 1 + 2);
    assertTrue(list.isEmpty());
}
```

**나쁜 사용 예**:
```java
// ❌ 너무 많은 static import (가독성 저하)
import static java.lang.Math.*;
import static java.util.Collections.*;
import static com.company.Constants.*;

// 어디서 온 메서드인지 불명확
sort(list);  // Collections.sort인가? 다른 것인가?
```

**실무 가이드라인**:
```java
// ✅ static import 사용 OK
// 1. 테스트 코드 (JUnit, Mockito)
// 2. 자주 사용하는 상수 (ChronoUnit, TimeUnit 등)
// 3. 프로젝트 내 공통 유틸리티 메서드

// ❌ static import 지양
// 1. 일반 비즈니스 로직
// 2. 여러 클래스에서 같은 이름의 static 메서드 있을 때
// 3. 코드 리뷰어가 출처를 찾기 어려운 경우
```

**실무 팁**:
💡 **테스트 코드에서는 적극 활용, 프로덕션 코드에서는 신중히 사용**하세요.

</details>

<details>
<summary><strong>Q6: 패키지명에 숫자를 사용할 수 있나요?</strong></summary>

**A**: **가능하지만, 예약어와 충돌하거나 숫자로 시작하면 안 됩니다.**

**가능한 패키지명**:
```java
// ✅ 숫자 포함 (중간이나 끝)
package com.company.project2;
package com.company.api.v1;
package com.company.product3d;

public class Demo {
    // OK
}
```

**불가능한 패키지명**:
```java
// ❌ 숫자로 시작
package com.company.2024project;  // 컴파일 에러!

// ❌ 예약어 사용
package com.company.class;  // class는 예약어!
package com.company.int;    // int는 예약어!

// ❌ 특수 문자
package com.company.my-project;  // - 사용 불가
package com.company.my_project;  // _ 사용 가능하지만 비권장
```

**패키지 명명 규칙**:
```java
// ✅ 좋은 패키지명
com.kakao.talk           // 소문자
com.naver.blog.api.v2    // 버전은 v2, v3 형식
com.company.util         // 간결하고 명확

// ❌ 나쁜 패키지명
com.COMPANY.Project      // 대문자 (관례 위반)
com.company.my_project   // _ 사용 (Java 관례 아님)
com.company.2d_graphics  // 숫자로 시작 (불가능)
```

**버전 관리**:
```java
// 실무에서 버전별 패키지 분리
com.company.api.v1/
  └── UserController.java

com.company.api.v2/
  └── UserController.java  // v2에서 개선된 버전

// REST API 버전 관리
// /api/v1/users
// /api/v2/users
```

**실무 팁**:
💡 **영문 소문자 + 점(.)만 사용**하세요. 숫자는 버전 표시 용도로만 제한적으로 사용하는 것이 좋습니다.

</details>

<details>
<summary><strong>Q7: 순환 참조(Circular Dependency)를 어떻게 해결하나요?</strong></summary>

**A**: **인터페이스 도입, 패키지 재구성, 또는 Dependency Injection을 사용하여 해결합니다.**

**순환 참조 문제**:
```java
// ❌ com/example/service/UserService.java
package com.example.service;

import com.example.service.OrderService;  // OrderService 참조

public class UserService {
    private OrderService orderService;

    public void registerUser(User user) {
        // ...
        orderService.createWelcomeOrder(user);
    }
}

// ❌ com/example/service/OrderService.java
package com.example.service;

import com.example.service.UserService;  // UserService 참조 (순환!)

public class OrderService {
    private UserService userService;

    public void processOrder(Order order) {
        // ...
        userService.notifyUser(order);
    }
}

// 문제: A → B, B → A 순환 참조
// 컴파일은 되지만, 유지보수와 테스트가 어려움
```

**해결 방법 1: 인터페이스 도입**
```java
// ✅ com/example/service/UserNotifier.java (인터페이스)
package com.example.service;

public interface UserNotifier {
    void notifyUser(Order order);
}

// ✅ com/example/service/UserService.java
package com.example.service;

import com.example.service.OrderService;

public class UserService implements UserNotifier {
    private OrderService orderService;

    @Override
    public void notifyUser(Order order) {
        // 알림 로직
    }
}

// ✅ com/example/service/OrderService.java
package com.example.service;

public class OrderService {
    private UserNotifier userNotifier;  // 인터페이스에 의존

    public void processOrder(Order order) {
        userNotifier.notifyUser(order);  // OK
    }
}

// UserService → OrderService
// OrderService → UserNotifier (인터페이스)
// 순환 참조 해결!
```

**해결 방법 2: 패키지 재구성**
```java
// 공통 기능을 별도 패키지로 분리
com.example/
  ├── user/
  │   └── UserService.java
  ├── order/
  │   └── OrderService.java
  └── notification/  // 공통 기능 분리
      └── NotificationService.java

// UserService와 OrderService 모두 NotificationService 의존
// user → notification
// order → notification
// 순환 없음!
```

**해결 방법 3: 이벤트 기반 (느슨한 결합)**
```java
// ✅ 이벤트 발행/구독 패턴
public class OrderService {
    private EventPublisher eventPublisher;

    public void processOrder(Order order) {
        // 주문 처리
        eventPublisher.publish(new OrderCreatedEvent(order));
        // UserService를 직접 호출하지 않음
    }
}

public class UserService {
    @EventListener
    public void onOrderCreated(OrderCreatedEvent event) {
        // 이벤트 수신하여 처리
        notifyUser(event.getOrder());
    }
}

// OrderService는 UserService를 모름
// 이벤트를 통한 간접 통신
```

**실무 팁**:
💡 **순환 참조는 설계 문제의 신호**입니다. 인터페이스 분리 원칙(ISP)과 의존성 역전 원칙(DIP)을 적용하세요.

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. 패키지의 역할과 사용 이유를 설명해주세요</strong></summary>

**모범 답안 포인트**
- 네임스페이스 제공 (이름 충돌 방지)
- 접근 제어 (default 접근자)
- 코드 구조화 (유지보수성 향상)

**예시 답변**
> "패키지는 관련된 클래스들을 그룹화하는 메커니즘입니다.
>
> 첫째, 네임스페이스를 제공하여 같은 이름의 클래스가 다른 패키지에 존재할 수 있게 합니다. 예를 들어 `java.util.Date`와 `java.sql.Date`는 같은 이름이지만 패키지가 다릅니다.
>
> 둘째, 접근 제어를 통해 같은 패키지 내부에서만 사용하는 클래스는 public을 붙이지 않아 캡슐화할 수 있습니다.
>
> 셋째, 코드를 기능별, 계층별로 체계적으로 구조화하여 유지보수성을 높입니다."

**꼬리 질문**
- Q: default 패키지는 무엇인가요?
- A: "package 선언 없이 만든 클래스가 속하는 무명 패키지입니다. 다른 패키지에서 import할 수 없어 실무에서는 사용하지 않습니다."

**실무 연관**
- Spring Boot 프로젝트의 패키지 구조 (controller, service, repository)
- 대규모 프로젝트에서 도메인별 패키지 분리
- 라이브러리 개발 시 public API와 내부 구현 분리

</details>

<details>
<summary><strong>2. import 문의 역할과 사용 방법을 설명해주세요</strong></summary>

**모범 답안 포인트**
- 다른 패키지의 클래스 사용
- FQCN을 짧게 쓰기 위함
- java.lang 패키지는 자동 import

**예시 답변**
> "import 문은 다른 패키지의 클래스를 사용할 때 전체 경로(FQCN)를 매번 쓰지 않고 간결하게 사용하기 위한 것입니다.
>
> 예를 들어 `import java.util.ArrayList;`를 선언하면 `java.util.ArrayList` 대신 `ArrayList`만 써도 됩니다.
>
> java.lang 패키지(String, System 등)는 자동으로 import되어 선언 없이 사용 가능합니다.
>
> import는 컴파일 시점에만 사용되며, 런타임 성능에는 영향을 주지 않습니다."

**꼬리 질문**
- Q: import java.util.*;과 개별 import의 차이는?
- A: "성능은 동일하지만, 개별 import가 어떤 클래스를 사용하는지 명확하여 가독성이 좋고 IDE의 미사용 import 탐지가 가능합니다."

**실무 연관**
- IDE의 자동 import 기능 (Alt+Enter, Ctrl+Shift+O)
- 코드 리뷰 시 불필요한 import 제거
- import 순서 정렬 (java, javax, org, com 순)

</details>

<details>
<summary><strong>3. 4가지 접근 제어자의 차이를 설명해주세요</strong></summary>

**모범 답안 포인트**
- public, protected, default, private
- 접근 범위: 같은 클래스, 같은 패키지, 자식 클래스, 다른 패키지
- 표로 정리

**예시 답변**
> "Java에는 4가지 접근 제어자가 있습니다.
>
> **public**: 어디서나 접근 가능합니다.
> **protected**: 같은 패키지 또는 자식 클래스에서 접근 가능합니다.
> **default (package-private)**: 같은 패키지 내에서만 접근 가능합니다. 접근 제어자를 생략하면 default입니다.
> **private**: 같은 클래스 내에서만 접근 가능합니다.
>
> 실무에서는 필드는 private으로 선언하고, 필요한 경우 public getter/setter를 제공하는 것이 일반적입니다."

**표로 정리**:
| 제어자 | 같은 클래스 | 같은 패키지 | 자식 클래스 | 다른 패키지 |
|--------|------------|------------|-----------|-----------|
| public | ✅ | ✅ | ✅ | ✅ |
| protected | ✅ | ✅ | ✅ | ❌ |
| default | ✅ | ✅ | ❌ | ❌ |
| private | ✅ | ❌ | ❌ | ❌ |

**꼬리 질문**
- Q: 캡슐화와 접근 제어자의 관계는?
- A: "캡슐화는 내부 구현을 숨기는 것인데, private 필드와 public 메서드로 이를 구현합니다. 외부에서 직접 필드에 접근하지 못하게 하여 데이터 무결성을 보장합니다."

**실무 연관**
- DTO 클래스: private 필드 + public getter/setter
- 내부 헬퍼 메서드: private
- 상속용 메서드: protected

</details>

<details>
<summary><strong>4. 같은 패키지와 다른 패키지의 클래스 사용 차이는?</strong></summary>

**모범 답안 포인트**
- 같은 패키지: import 불필요, default 접근자 접근 가능
- 다른 패키지: import 필요, public만 접근 가능

**예시 답변**
> "같은 패키지의 클래스는 import 없이 바로 사용할 수 있으며, default 접근 제어자도 접근 가능합니다.
>
> 다른 패키지의 클래스는 반드시 import해야 하고, public으로 선언된 클래스만 사용할 수 있습니다.
>
> 예를 들어, com.example.model 패키지의 User 클래스를 com.example.service 패키지에서 사용하려면 `import com.example.model.User;`를 선언해야 합니다."

**코드 예시**:
```java
// com/example/model/User.java
package com.example.model;

public class User { }        // public: 다른 패키지 접근 OK
class Helper { }             // default: 같은 패키지만 접근

// com/example/model/Product.java (같은 패키지)
package com.example.model;

public class Product {
    public void test() {
        User user = new User();     // import 불필요
        Helper helper = new Helper(); // default 접근 OK
    }
}

// com/example/service/UserService.java (다른 패키지)
package com.example.service;

import com.example.model.User;  // import 필요

public class UserService {
    public void test() {
        User user = new User();     // OK
        // Helper helper = new Helper();  // ❌ default 접근 불가
    }
}
```

**실무 연관**
- 패키지 내부용 유틸리티 클래스는 public 없이 선언
- 같은 도메인 패키지 내 클래스들은 import 없이 협력

</details>

<details>
<summary><strong>5. 패키지 선언 시 주의사항은 무엇인가요?</strong></summary>

**모범 답안 포인트**
- 파일 맨 위에 위치 (주석 제외)
- 한 파일에 하나만 가능
- 디렉토리 구조와 일치

**예시 답변**
> "패키지 선언 시 주의사항은 세 가지입니다.
>
> 첫째, package 문은 주석을 제외하고 파일의 맨 처음에 와야 합니다. import보다 앞에 있어야 합니다.
>
> 둘째, 한 파일에는 하나의 package 선언만 가능합니다.
>
> 셋째, 패키지명과 디렉토리 구조가 일치해야 합니다. 예를 들어 `package com.example.model;`이면 파일은 `com/example/model/` 디렉토리에 있어야 합니다."

**올바른 순서**:
```java
// 1. 주석 (선택)
/*
 * 클래스 설명
 */

// 2. package 선언 (필수)
package com.example;

// 3. import 문 (선택)
import java.util.List;

// 4. 클래스 선언
public class MyClass {
}
```

**꼬리 질문**
- Q: 패키지 선언을 생략하면?
- A: "default 패키지에 속하게 됩니다. 다른 패키지에서 import할 수 없고 모듈 시스템과 호환되지 않아 실무에서는 절대 사용하지 않습니다."

**실무 연관**
- 코드 리뷰 시 패키지 선언 확인
- IDE가 자동으로 package 선언 추가
- 파일 이동 시 패키지 선언 자동 업데이트

</details>

<details>
<summary><strong>6. FQCN (Fully Qualified Class Name)이란 무엇인가요?</strong></summary>

**모범 답안 포인트**
- 패키지명을 포함한 전체 클래스 이름
- import 없이 사용 가능
- 이름 충돌 해결

**예시 답변**
> "FQCN은 Fully Qualified Class Name의 약자로, 패키지명을 포함한 클래스의 전체 이름입니다.
>
> 예를 들어, ArrayList의 FQCN은 `java.util.ArrayList`입니다.
>
> import 없이도 FQCN을 사용하면 클래스를 사용할 수 있습니다. 특히 같은 이름의 클래스를 여러 개 사용할 때 유용합니다.
>
> 예를 들어, `java.util.Date`와 `java.sql.Date`를 동시에 사용할 때 하나는 import하고 다른 하나는 FQCN으로 쓸 수 있습니다."

**코드 예시**:
```java
package com.example;

// import 없이 FQCN 사용
public class Demo {
    public static void main(String[] args) {
        // FQCN 사용
        java.util.ArrayList<String> list = new java.util.ArrayList<>();
        list.add("Hello");

        // 이름 충돌 해결
        java.util.Date utilDate = new java.util.Date();
        java.sql.Date sqlDate = java.sql.Date.valueOf("2024-01-15");
    }
}
```

**실무 연관**
- 코드에서는 import 사용이 일반적
- 이름 충돌 시에만 FQCN 사용
- 리플렉션에서 Class.forName("java.util.ArrayList") 같이 문자열로 FQCN 사용

</details>

<details>
<summary><strong>7. 한 파일에 public 클래스가 여러 개 있으면 어떻게 되나요?</strong></summary>

**모범 답안 포인트**
- 불가능 (컴파일 에러)
- 한 파일에 하나의 public 클래스만 가능
- public 클래스명 = 파일명

**예시 답변**
> "한 파일에는 하나의 public 클래스만 존재할 수 있으며, 그 클래스명이 파일명과 동일해야 합니다.
>
> 예를 들어, MyClass.java 파일에는 `public class MyClass`만 가능합니다. 다른 public 클래스를 추가하면 컴파일 에러가 발생합니다.
>
> 단, public이 아닌 default 접근자 클래스는 같은 파일에 여러 개 선언할 수 있습니다. 이런 클래스는 같은 패키지 내에서만 사용하는 헬퍼 클래스로 활용됩니다."

**코드 예시**:
```java
// MyClass.java
package com.example;

public class MyClass {  // OK: 파일명과 동일
}

// public class AnotherClass { }  // ❌ 에러!

class HelperClass {  // ✅ OK: default 접근자
    // 같은 패키지 내부용
}

class UtilClass {  // ✅ OK: default
}
```

**꼬리 질문**
- Q: 왜 이런 규칙이 있나요?
- A: "컴파일러가 public 클래스를 파일명으로 빠르게 찾을 수 있게 하기 위함입니다. 또한 한 파일에 하나의 주요 클래스만 두어 가독성을 높입니다."

**실무 연관**
- 내부 헬퍼 클래스는 default로 같은 파일에 선언 가능
- 일반적으로 클래스마다 별도 파일로 분리하는 것이 관례

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. 패키지 설계 패턴(계층형 vs 도메인 중심)의 차이와 선택 기준을 설명해주세요</strong></summary>

**모범 답안 포인트**
- 계층형: controller, service, repository 분리
- 도메인 중심: user, order, product별 분리
- 프로젝트 규모와 팀 구조에 따라 선택

**예시 답변**
> "계층형 구조는 기술적 관심사로 패키지를 나누는 방식으로, controller, service, repository 등으로 분리합니다. 코드를 이해하기 쉽고 소규모 프로젝트에 적합합니다.
>
> 도메인 중심 구조는 비즈니스 도메인별로 패키지를 나누어, user, order, product 같이 구성합니다. 각 도메인이 독립적이어서 대규모 팀에서 병렬 개발이 용이하고 마이크로서비스로 전환하기 쉽습니다.
>
> 선택 기준은 프로젝트 규모입니다. 소규모(~10만 줄)는 계층형, 대규모나 마이크로서비스는 도메인 중심을 권장합니다."

**코드 비교**:
```java
// 계층형 (Layered)
com.company.project/
  ├── controller/
  │   ├── UserController.java
  │   └── OrderController.java
  ├── service/
  │   ├── UserService.java
  │   └── OrderService.java
  └── repository/
      ├── UserRepository.java
      └── OrderRepository.java

// 도메인 중심 (DDD)
com.company.ecommerce/
  ├── user/
  │   ├── domain/User.java
  │   ├── service/UserService.java
  │   └── repository/UserRepository.java
  └── order/
      ├── domain/Order.java
      ├── service/OrderService.java
      └── repository/OrderRepository.java
```

**실무 예시**
- Netflix: 마이크로서비스 구조로 도메인 중심
- 스타트업 MVP: 계층형으로 빠른 개발
- 대기업 레거시: 점진적 도메인 중심 전환

</details>

<details>
<summary><strong>2. JAR 파일의 내부 구조와 실행 메커니즘을 설명해주세요</strong></summary>

**모범 답안 포인트**
- ZIP 형식의 압축 파일
- META-INF/MANIFEST.MF에 메타 정보
- 클래스 로더가 JAR에서 클래스 로드

**예시 답변**
> "JAR 파일은 ZIP 형식의 압축 파일로, 여러 .class 파일과 리소스를 하나로 묶은 것입니다.
>
> 내부 구조는 컴파일된 클래스 파일들이 패키지 구조대로 저장되고, META-INF/MANIFEST.MF 파일에 JAR의 메타 정보가 들어있습니다. MANIFEST.MF에 Main-Class를 지정하면 실행 가능한 JAR이 됩니다.
>
> 실행 시 JVM의 클래스 로더가 JAR 파일을 클래스 경로에 추가하고, 필요한 클래스를 압축 해제 없이 직접 읽어 메모리에 로드합니다. 이 방식으로 배포와 실행이 간편해집니다."

**JAR 구조**:
```
myapp.jar
├── com/
│   └── example/
│        ├── Main.class
│        └── util/
│             └── Helper.class
├── META-INF/
│   └── MANIFEST.MF
└── resources/
    └── config.properties

// MANIFEST.MF 예시
Manifest-Version: 1.0
Main-Class: com.example.Main
Class-Path: lib/dependency1.jar lib/dependency2.jar
```

**실행 과정**:
```bash
java -jar myapp.jar

# 1. JVM 시작
# 2. MANIFEST.MF 읽기
# 3. Main-Class 찾기 (com.example.Main)
# 4. 클래스 로더가 JAR에서 Main.class 로드
# 5. main() 메서드 실행
```

**실무 연관**
- Spring Boot의 Uber JAR (모든 의존성 포함)
- Maven/Gradle이 자동으로 JAR 생성
- Docker 이미지에 JAR 포함하여 배포

</details>

<details>
<summary><strong>3. 클래스 경로(CLASSPATH)의 동작 원리를 설명해주세요</strong></summary>

**모범 답안 포인트**
- 클래스 파일 검색 경로
- 환경 변수 또는 -cp 옵션
- 클래스 로더의 위임 모델

**예시 답변**
> "CLASSPATH는 JVM이 클래스 파일을 찾기 위한 검색 경로입니다.
>
> 설정 방법은 두 가지입니다. 환경 변수 CLASSPATH를 설정하거나, `java -cp` 옵션으로 지정합니다. 경로에는 디렉토리나 JAR 파일을 포함할 수 있습니다.
>
> JVM은 클래스를 로드할 때 CLASSPATH에 지정된 순서대로 검색합니다. 클래스 로더는 부트스트랩 → 확장 → 애플리케이션 클래스 로더 순으로 위임하며, 각 로더가 CLASSPATH 내에서 클래스를 찾습니다.
>
> 실무에서는 Maven/Gradle이 자동으로 CLASSPATH를 관리하므로 직접 설정할 일은 드뭅니다."

**설정 예시**:
```bash
# Windows
set CLASSPATH=C:\lib\app.jar;C:\classes

# Linux/Mac
export CLASSPATH=/lib/app.jar:/classes

# -cp 옵션 사용 (권장)
java -cp "lib/*:classes" com.example.Main

# Maven 프로젝트 실행
mvn exec:java -Dexec.mainClass="com.example.Main"
# Maven이 의존성을 자동으로 CLASSPATH에 추가
```

**클래스 로딩 순서**:
```
1. com.example.MyClass 로드 요청
2. 애플리케이션 클래스 로더가 부모(확장 로더)에 위임
3. 확장 로더가 부모(부트스트랩 로더)에 위임
4. 부트스트랩 로더가 java.* 패키지 검색 → 없음
5. 확장 로더가 javax.* 등 검색 → 없음
6. 애플리케이션 로더가 CLASSPATH 검색 → 발견!
7. MyClass 로드
```

**실무 연관**
- IDE가 프로젝트 빌드 경로를 자동 설정
- Spring Boot의 fat JAR는 내부 클래스 로더 사용
- 클래스 로딩 이슈 디버깅 시 CLASSPATH 확인 필요

</details>

<details>
<summary><strong>4. 순환 의존성(Circular Dependency)의 문제점과 해결 방법을 설명해주세요</strong></summary>

**모범 답안 포인트**
- A → B, B → A 순환 참조
- 테스트 어려움, 컴파일 순서 문제
- 인터페이스 도입, DI, 이벤트 기반으로 해결

**예시 답변**
> "순환 의존성은 패키지 A가 B를 참조하고, B가 다시 A를 참조하는 상황입니다.
>
> 문제점은 첫째, 단위 테스트가 어려워집니다. A를 테스트하려면 B가 필요하고, B를 테스트하려면 A가 필요한 상황이 됩니다. 둘째, 재컴파일 시 전체를 다시 빌드해야 하여 빌드 시간이 길어집니다.
>
> 해결 방법은 인터페이스를 도입하여 의존성을 역전시키거나, Spring의 Dependency Injection을 활용합니다. 또는 이벤트 기반 아키텍처로 직접 참조를 끊을 수 있습니다."

**문제 상황**:
```java
// ❌ 순환 의존성
// com.example.service.UserService
package com.example.service;
import com.example.service.OrderService;

public class UserService {
    private OrderService orderService;  // OrderService 참조
}

// com.example.service.OrderService
package com.example.service;
import com.example.service.UserService;

public class OrderService {
    private UserService userService;  // UserService 참조 (순환!)
}
```

**해결 방법**:
```java
// ✅ 해결 1: 인터페이스 도입
public interface UserNotifier {
    void notify(String message);
}

public class UserService implements UserNotifier {
    private OrderService orderService;

    @Override
    public void notify(String message) { }
}

public class OrderService {
    private UserNotifier notifier;  // 인터페이스에 의존 (역전!)
}

// ✅ 해결 2: 이벤트 기반
public class OrderService {
    private EventPublisher publisher;

    public void createOrder() {
        publisher.publish(new OrderCreatedEvent());
        // UserService를 직접 호출하지 않음
    }
}

@EventListener
public class UserService {
    public void onOrderCreated(OrderCreatedEvent event) {
        // 이벤트 수신
    }
}
```

**실무 연관**
- Spring의 @Autowired로 순환 참조 시 경고
- 마이크로서비스에서 이벤트 기반 통신
- 모듈 간 의존성 분석 도구 (JDepend, Structure101)

</details>

<details>
<summary><strong>5. Java 9+ 모듈 시스템과 패키지의 관계를 설명해주세요</strong></summary>

**모범 답안 포인트**
- 모듈은 패키지의 상위 개념
- module-info.java로 모듈 정의
- exports, requires로 접근 제어

**예시 답변**
> "Java 9부터 도입된 모듈 시스템(JPMS)은 패키지를 더 큰 단위로 그룹화하는 메커니즘입니다.
>
> 모듈은 module-info.java 파일로 정의하며, exports 키워드로 외부에 공개할 패키지를 선언하고, requires로 의존 모듈을 명시합니다.
>
> 이를 통해 JDK 자체도 모듈화되어 java.base, java.sql 등으로 분리되었고, 애플리케이션은 필요한 모듈만 포함하여 런타임 크기를 줄일 수 있습니다.
>
> 실무에서는 레거시 프로젝트는 아직 클래스 경로 방식을 사용하지만, 신규 프로젝트는 점차 모듈 시스템을 도입하고 있습니다."

**모듈 정의 예시**:
```java
// module-info.java
module com.example.myapp {
    // 의존 모듈
    requires java.sql;
    requires java.logging;

    // 외부에 공개할 패키지
    exports com.example.api;
    exports com.example.model;

    // 공개하지 않는 패키지 (내부 구현)
    // com.example.internal (exports 안 함)
}
```

**구조**:
```
myapp/
├── module-info.java
└── com/
    └── example/
        ├── api/          (exports: 외부 공개)
        ├── model/        (exports: 외부 공개)
        └── internal/     (미공개: 내부 전용)
```

**장점**:
```java
// 1. 강력한 캡슐화
// public 클래스도 exports하지 않으면 모듈 외부에서 접근 불가

// 2. 명확한 의존성
// requires로 모듈 간 의존성 명시 → 순환 참조 방지

// 3. JDK 모듈화
// 필요한 모듈만 포함 → Docker 이미지 크기 감소
```

**실무 연관**
- Spring Boot 2.x+에서 모듈 시스템 지원
- jlink로 커스텀 JRE 생성 (모듈 기반)
- 레거시 JAR은 자동 모듈(automatic module)로 동작

</details>

---

## 📝 핵심 정리

### 이 장에서 배운 핵심 개념

| 개념 | 설명 | 핵심 키워드 |
|------|------|-------------|
| 접근 제어자 | public, protected, default, private | 캡슐화, 가시성 |
| JAR 파일 | 클래스를 압축한 배포 단위 | 압축, 배포, META-INF |
| CLASSPATH | 클래스 검색 경로 | 환경 변수, -cp |
| 패키지 설계 | 계층형 vs 도메인 중심 | Layered, DDD |
| 순환 참조 | A → B, B → A 의존성 | 인터페이스, DI, 이벤트 |

### 접근 제어자 완벽 정리

| 접근 제어자 | 같은 클래스 | 같은 패키지 | 자식 클래스 (다른 패키지) | 다른 패키지 |
|------------|------------|------------|----------------------|-----------|
| **public** | ✅ | ✅ | ✅ | ✅ |
| **protected** | ✅ | ✅ | ✅ | ❌ |
| **default** | ✅ | ✅ | ❌ | ❌ |
| **private** | ✅ | ❌ | ❌ | ❌ |

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] **필드는 private**: 캡슐화 원칙
- [ ] **public 클래스는 파일명과 동일**: 컨벤션 준수
- [ ] **개별 import 사용**: 가독성과 명확성
- [ ] **패키지는 소문자**: com.company.project
- [ ] **접근 범위는 최소화**: 필요한 만큼만 public

#### ❌ 하지 말아야 할 것
- [ ] **default 패키지 사용**: 실무 금지
- [ ] **와일드카드 import 남발**: import java.util.*;
- [ ] **순환 참조**: 패키지 간 상호 의존
- [ ] **너무 깊은 패키지 계층**: 3-4단계 권장
- [ ] **한 파일에 여러 public 클래스**: 컴파일 에러

### JAR 파일 명령어

```bash
# JAR 생성
jar -cvf myapp.jar com/

# JAR 내용 확인
jar -tf myapp.jar

# 실행 가능한 JAR 생성
jar -cvfe myapp.jar com.example.Main com/

# JAR 실행
java -jar myapp.jar

# 클래스 경로 지정
java -cp "lib1.jar;lib2.jar" com.Main
```

### 패키지 설계 선택 가이드

```
프로젝트 규모 < 10만 줄
    → 계층형 (controller, service, repository)

프로젝트 규모 > 10만 줄 또는 대규모 팀
    → 도메인 중심 (user, order, product)

마이크로서비스
    → 도메인 중심 + 각 서비스별 분리
```

---

## 🔗 관련 기술

**패키지와 함께 사용하는 기술들**

| 기술 | 관계 | 학습 우선순위 |
|------|------|---------------|
| Maven/Gradle | 의존성 및 패키지 관리 | ⭐⭐⭐⭐⭐ (필수) |
| Java Module System | 패키지 그룹화 | ⭐⭐⭐ |
| Spring Framework | DI, 패키지 스캔 | ⭐⭐⭐⭐⭐ |
| JUnit | 테스트 패키지 구조 | ⭐⭐⭐⭐ |
| Docker | JAR 배포 | ⭐⭐⭐⭐ |

**학습 순서 추천**:
```
패키지와 import (현재) ✅
    ↓
Maven/Gradle 빌드 도구
    ↓
Spring Framework (DI, 컴포넌트 스캔)
    ↓
테스트 패키지 구조
    ↓
모듈 시스템 (선택)
```

---

## 🚀 다음 단계

### 다음 장 미리보기: 11장 JVM 메모리 구조

**배울 내용**:
- **Stack 영역**: 메서드 호출과 지역 변수 저장
- **Heap 영역**: 객체와 배열 저장
- **Method Area**: 클래스 메타데이터
- **가비지 컬렉션**: 메모리 자동 관리
- **메모리 누수 방지**: 실무 주의사항

**실전 프로젝트**:
- 🧠 메모리 분석 프로그램
- 📊 메모리 사용량 모니터링

### 이 장과의 연결점

```
10장: 패키지와 import
    ↓
클래스 구조화와 배포 방법 습득
    ↓
11장: JVM 메모리 구조
    ↓
클래스가 메모리에 어떻게 로드되는지 이해
    ↓
최종적으로
    ↓
성능 최적화와 메모리 관리 능력
```

### 준비하면 좋을 것들

```bash
# 10장 복습
# 다음 패키지 구조로 프로젝트 만들어보기

com.myproject/
  ├── model/
  ├── service/
  ├── util/
  └── Main.java

# JAR 파일 만들어보기
# 실행 가능한 JAR로 배포해보기
```

---

## 📚 추가 학습 자료

### 공식 문서
- [Oracle Java Package Tutorial](https://docs.oracle.com/javase/tutorial/java/package/index.html)
- [Java Module System (JPMS)](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/module-summary.html)
- [JAR File Specification](https://docs.oracle.com/en/java/javase/17/docs/specs/jar/jar.html)

### 추천 블로그/아티클
- [Baeldung - Java Packages](https://www.baeldung.com/java-packages)
- [Package Naming Conventions](https://www.baeldung.com/java-package-naming-conventions)
- [Java 9 Module System](https://www.baeldung.com/java-9-modularity)

### 영상 강의
- [인프런 - 김영한의 자바 입문](https://www.inflearn.com/course/%EA%B9%80%EC%98%81%ED%95%9C%EC%9D%98-%EC%9E%90%EB%B0%94-%EC%9E%85%EB%AC%B8)
- [YouTube - 코딩애플 Java 패키지](https://www.youtube.com/@codingapple)

### 도서
- **"Effective Java" (조슈아 블로크)** ⭐⭐⭐⭐⭐
  - Item 15: 클래스와 멤버의 접근 권한을 최소화하라
  - Item 16: public 클래스에서는 public 필드가 아닌 접근자 메서드를 사용하라

- **"Clean Architecture" (로버트 C. 마틴)** ⭐⭐⭐⭐⭐
  - 패키지 원칙 (Package Principles)
  - 컴포넌트 응집도와 결합도

---

## 🎉 축하합니다!

**10장 패키지와 import 완전 마스터!**

**이제 여러분은**:
✅ 패키지의 개념과 사용법을 완벽히 이해했습니다
✅ import 문을 효과적으로 사용할 수 있습니다
✅ 4가지 접근 제어자의 차이를 명확히 알았습니다
✅ JAR 파일을 생성하고 실행할 수 있습니다
✅ 실무 수준의 패키지 구조를 설계할 수 있습니다
✅ 계층형과 도메인 중심 구조의 차이를 이해했습니다
✅ 순환 의존성을 해결하는 방법을 배웠습니다
✅ FAQ 7개 질문에 답할 수 있습니다
✅ 면접 질문 12개를 준비했습니다
✅ 도서관 관리 시스템을 구현했습니다

**다음 단계**:
- [ ] 10장 실전 프로젝트 복습하기
- [ ] 자신만의 패키지 구조로 미니 프로젝트 만들기
- [ ] 면접 질문 답변 연습하기
- [ ] 11장 "JVM 메모리 구조"로 진행하기

---

## 💬 학습 후 체크리스트

### 기초 개념 (10-1장)
- [ ] 패키지의 역할을 설명할 수 있다
- [ ] import 문을 올바르게 사용할 수 있다
- [ ] FQCN을 이해한다
- [ ] 패키지 구조를 설계할 수 있다
- [ ] 도서관 관리 시스템을 구현했다

### 심화 개념 (10-2장)
- [ ] 4가지 접근 제어자의 차이를 안다
- [ ] JAR 파일을 생성하고 실행할 수 있다
- [ ] CLASSPATH 개념을 이해한다
- [ ] 패키지 설계 패턴을 선택할 수 있다
- [ ] 순환 의존성을 해결하는 방법을 안다
- [ ] FAQ 7개 질문에 답할 수 있다
- [ ] 주니어 면접 질문 7개를 준비했다
- [ ] 중급 면접 질문 5개를 이해했다

### 실무 역량
- [ ] 실무 수준의 패키지 구조를 설계한다
- [ ] 접근 제어자를 적절히 활용한다
- [ ] Maven/Gradle 프로젝트를 이해한다
- [ ] 순환 참조를 방지한다
- [ ] 코드 리뷰 시 패키지 구조를 검토한다

---

**💪 "패키지로 대규모 프로젝트를 체계적으로 관리할 수 있습니다!"**

**📖 다음 장에서 만나요!**

[← 이전: 10-1장 패키지와 import 기초편](10-1-패키지와-import-기초편.md) | [다음: 11장 JVM 메모리 구조 →](11-1-JVM-메모리-구조-기초편.md)

[📚 전체 목차로 돌아가기](README.md)

---

**🌟 Java 마스터의 길, 계속 전진하세요! 🚀**

*"Good code is its own best documentation." - Steve McConnell*
