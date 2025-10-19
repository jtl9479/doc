# 11장-1: Spring MVC 개요 - 기본 개념

> **학습 목표**: Spring MVC의 구조와 동작 원리를 이해하고, DispatcherServlet의 요청 처리 흐름을 설명할 수 있습니다.

**⏱️ 예상 학습 시간**: 2-3시간
**난이도**: ⭐⭐⭐☆☆ (3개/5개)

---

## 📚 목차
- [왜 이 기술이 필요한가](#왜-이-기술이-필요한가)
- [실생활 비유로 이해하기](#실생활-비유로-이해하기)
- [핵심 개념](#핵심-개념)
- [기본 실습](#기본-실습)
- [핵심 정리](#핵심-정리)
- [다음 단계](#다음-단계)

---

## 🤔 왜 이 기술이 필요한가?

### 실무 배경
**웹 애플리케이션 개발 시 발생하는 반복적인 작업들**

매번 웹 요청을 처리할 때마다:
- HTTP 요청 파싱
- URL에 따른 적절한 로직 호출
- 비즈니스 로직 실행
- 결과를 HTML로 변환
- HTTP 응답 생성

이러한 작업을 매번 직접 작성하면 생산성이 크게 떨어집니다.

#### ❌ Spring MVC를 모르면 발생하는 문제

```
문제 1: 반복 코드 과다
- 증상: Servlet마다 요청 파싱, 응답 생성 코드 반복
- 영향: 개발 시간 증가, 유지보수 어려움
- 비용: 1개 기능 개발에 4시간 소요

문제 2: 일관성 없는 구조
- 증상: 개발자마다 다른 방식으로 구현
- 영향: 코드 리뷰 어려움, 인수인계 복잡
- 비용: 신입 온보딩 2주 이상 소요

문제 3: 비즈니스 로직과 웹 로직 혼재
- 증상: Controller에 DB 접근, 계산 로직 혼재
- 영향: 테스트 어려움, 재사용 불가
- 비용: 버그 수정 시간 3배 증가
```

#### ✅ Spring MVC를 사용하면

```
해결책 1: 프레임워크가 반복 작업 처리
- 방법: 어노테이션 기반 자동 매핑
- 효과: 핵심 로직에만 집중
- 절감: 개발 시간 75% 단축

해결책 2: 표준화된 구조
- 방법: MVC 패턴 강제
- 효과: 일관된 코드 구조
- 절감: 온보딩 시간 85% 단축

해결책 3: 명확한 레이어 분리
- 방법: Controller-Service-Repository 패턴
- 효과: 테스트 용이, 재사용 가능
- 절감: 유지보수 비용 60% 절감
```

### 📊 수치로 보는 효과

| 지표 | Servlet 직접 사용 | Spring MVC | 개선율 |
|------|------------------|------------|--------|
| 개발 시간 | 4시간/기능 | 1시간/기능 | **75%↓** |
| 코드 라인 수 | 200줄 | 50줄 | **75%↓** |
| 버그 발생률 | 15% | 3% | **80%↓** |
| 신규 기능 추가 | 8시간 | 2시간 | **75%↓** |

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 레스토랑 운영 시스템

```
Spring MVC = 레스토랑 운영 시스템

손님 (사용자)
    ↓
입구 직원 (DispatcherServlet)
    ↓
매니저 (HandlerMapping)
    ↓
담당 웨이터 (Controller)
    ↓
주방장 (Service)
    ↓
창고 관리자 (Repository)

┌─────────────────────────────────────┐
│         레스토랑 (Web Application)    │
│                                       │
│  입구 ← 손님 주문                      │
│   ↓                                   │
│  매니저: "이 손님은 3번 테이블"         │
│   ↓                                   │
│  웨이터: 주문 받고 주방에 전달          │
│   ↓                                   │
│  주방장: 요리 제작                     │
│   ↓                                   │
│  웨이터: 음식 서빙                     │
└─────────────────────────────────────┘

특징:
- 입구 직원(DispatcherServlet)이 모든 손님을 맞이
- 매니저가 적절한 웨이터에게 배정
- 웨이터는 주문만 받고 요리는 주방장이 담당
- 명확한 역할 분담으로 효율적 운영
```

### 비유 2: 택배 배송 시스템

**Spring MVC = 택배 물류 센터**

```
고객 주문 (HTTP Request)
    ↓
물류 센터 (DispatcherServlet) - 모든 택배 집중
    ↓
분류 시스템 (HandlerMapping) - 지역별 분류
    ↓
배송 기사 (Controller) - 해당 지역 담당
    ↓
배송 (View) - 고객에게 전달

장점:
- 하나의 센터에서 모든 택배 관리
- 자동 분류로 빠른 처리
- 담당 기사가 책임지고 배송
- 추적 가능 (로깅)
```

### 비유 3: 119 긴급 출동 시스템

```
Spring MVC = 119 종합 상황실

긴급 신고 전화 (HTTP Request)
    ↓
119 상황실 (DispatcherServlet)
    ↓
상황 판단 (HandlerMapping)
    ↓
소방차/구급차 출동 (Controller)
    ↓
현장 처리 (Service)
    ↓
결과 보고 (View)

┌─────────────────────────────────┐
│     119 상황실                    │
│                                   │
│  "불이야!" → 소방차 출동           │
│  "다쳤어요!" → 구급차 출동         │
│  "갇혔어요!" → 구조대 출동         │
│                                   │
│  상황실이 자동으로 판단하고 배정   │
└─────────────────────────────────┘
```

### 비유 4: 병원 접수 시스템

**예약 없이 병원 방문 시**

```
환자 (사용자)
    ↓
병원 접수 창구 (DispatcherServlet) - 단일 진입점
    ↓
접수 직원 (HandlerMapping) - "어디가 아프세요?"
    ↓
해당 과 진료실 (Controller)
    ↓
의사 진료 (Service)
    ↓
처방전 발급 (View)

효율성:
- 환자는 접수만 하면 됨
- 증상에 따라 자동 배정
- 의사는 진료에만 집중
- 진료 기록 자동 관리
```

### 비유 5: 공항 수하물 처리

```
Spring MVC = 공항 수하물 처리 시스템

체크인 (사용자 요청)
    ↓
수하물 태그 부착 (DispatcherServlet)
    ↓
자동 분류 컨베이어 (HandlerMapping)
    ↓
해당 항공편 담당 (Controller)
    ↓
비행기 적재 (Service)
    ↓
목적지 도착 (View)

┌─────────────────────────────────┐
│    자동 수하물 분류 시스템        │
│                                   │
│  인천→뉴욕    →  AA123편          │
│  인천→도쿄    →  KE456편          │
│  인천→파리    →  AF789편          │
│                                   │
│  바코드 스캔으로 자동 분류         │
└─────────────────────────────────┘
```

### 🎯 종합 비교표

```
┌──────────────┬───────────┬───────────┬───────────┐
│ MVC 구성요소  │ 레스토랑   │ 택배      │ 119       │
├──────────────┼───────────┼───────────┼───────────┤
│ DispatcherServlet│ 입구 직원 │ 물류센터  │ 상황실    │
│ HandlerMapping│ 매니저    │ 분류시스템 │ 상황판단  │
│ Controller   │ 웨이터    │ 배송기사  │ 출동팀    │
│ Service      │ 주방장    │ 배송처리  │ 현장처리  │
│ View         │ 서빙      │ 고객전달  │ 결과보고  │
└──────────────┴───────────┴───────────┴───────────┘
```

---

## 📖 핵심 개념

### 개념 설명 (3단계 깊이)

#### 1️⃣ 초보자 수준 설명

**Spring MVC는 웹 애플리케이션을 만드는 도구입니다.**

마치 레고 블록처럼, 각 부품(Controller, Service, View)을 조립해서 웹사이트를 만듭니다.

- **Controller**: 사용자 요청을 받는 곳
- **Service**: 실제 일을 하는 곳
- **View**: 결과를 보여주는 곳

```
사용자 → Controller → Service → View → 사용자
       (요청받기)   (처리하기)  (보여주기)
```

#### 2️⃣ 중급자 수준 설명

**Spring MVC는 Model-View-Controller 패턴을 구현한 웹 프레임워크입니다.**

**핵심 구성 요소:**

1. **DispatcherServlet**: 모든 요청의 진입점 (Front Controller 패턴)
2. **HandlerMapping**: URL을 Controller 메서드에 매핑
3. **Controller**: 요청 처리 로직
4. **ViewResolver**: 논리적 뷰 이름을 실제 뷰로 변환
5. **Model**: 데이터 전달 객체

**요청 처리 흐름:**
```
1. HTTP Request → DispatcherServlet
2. HandlerMapping이 적절한 Controller 찾기
3. Controller가 비즈니스 로직 실행
4. Model에 데이터 저장
5. ViewResolver가 View 결정
6. View가 렌더링
7. HTTP Response 반환
```

#### 3️⃣ 고급자 수준 설명

**Spring MVC는 Servlet API 위에 구축된 요청 기반 웹 프레임워크입니다.**

**내부 동작 원리:**

1. **DispatcherServlet 초기화**
   - WebApplicationContext 생성
   - HandlerMapping, HandlerAdapter, ViewResolver 등 전략 객체 초기화

2. **요청 처리 프로세스**
   - `doDispatch()` 메서드가 핵심
   - HandlerExecutionChain 구성 (Interceptor 포함)
   - HandlerAdapter를 통한 실제 핸들러 실행
   - ModelAndView 객체 반환

3. **View 렌더링**
   - ViewResolver 체인을 통한 View 해석
   - View 인터페이스의 render() 메서드 호출
   - Model 데이터를 HttpServletRequest attribute로 전달

**최적화 포인트:**
- HandlerMapping 캐싱
- ViewResolver 캐싱
- Interceptor 체인 최적화
- 비동기 요청 처리 (DeferredResult, Callable)

### 주요 용어 정리

| 용어 | 영문 | 설명 | 예시 |
|------|------|------|------|
| 디스패처 서블릿 | DispatcherServlet | 모든 요청을 받는 프론트 컨트롤러 | 단일 진입점 |
| 핸들러 매핑 | HandlerMapping | URL과 컨트롤러를 연결 | `/user` → UserController |
| 컨트롤러 | Controller | 요청을 처리하는 클래스 | `@Controller` |
| 모델 | Model | 데이터를 담는 객체 | `model.addAttribute()` |
| 뷰 | View | 결과를 렌더링하는 템플릿 | JSP, Thymeleaf |
| 뷰 리졸버 | ViewResolver | 논리적 뷰 이름을 실제 뷰로 변환 | "home" → "/WEB-INF/views/home.jsp" |
| 핸들러 어댑터 | HandlerAdapter | 다양한 형태의 핸들러를 실행 | @RequestMapping 처리 |
| 인터셉터 | Interceptor | 요청 전/후 처리 | 로깅, 인증 |
| 모델앤뷰 | ModelAndView | Model과 View를 함께 담는 객체 | 컨트롤러 반환 타입 |

### MVC 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Spring MVC Architecture                    │
└─────────────────────────────────────────────────────────────┘

                        [Browser]
                            │
                            ↓
              ┌─────────────────────────┐
              │   ① HTTP Request        │
              └─────────────────────────┘
                            │
                            ↓
         ╔══════════════════════════════════════╗
         ║      DispatcherServlet              ║
         ║    (Front Controller)                ║
         ╚══════════════════════════════════════╝
                   │              ↑
        ② 핸들러 찾기│              │⑦ ModelAndView
                   ↓              │
         ┌────────────────────────┴──────┐
         │    HandlerMapping             │
         │  - RequestMappingHandlerMapping│
         └───────────────────────────────┘
                   │
        ③ 핸들러 실행 요청
                   ↓
         ┌───────────────────────────────┐
         │    HandlerAdapter             │
         │  - RequestMappingHandlerAdapter│
         └───────────────────────────────┘
                   │
        ④ 메서드 실행
                   ↓
         ╔═══════════════════════════════╗
         ║      Controller               ║
         ║    (@Controller)              ║
         ╚═══════════════════════════════╝
                   │
        ⑤ 비즈니스 로직
                   ↓
         ┌───────────────────────────────┐
         │       Service                 │
         │     (@Service)                │
         └───────────────────────────────┘
                   │
                   ↓
         ┌───────────────────────────────┐
         │     Repository                │
         │   (@Repository)               │
         └───────────────────────────────┘
                   │
        ⑥ Model + ViewName 반환
                   ↓
         ╔═══════════════════════════════╗
         ║   ViewResolver                ║
         ║  - InternalResourceViewResolver║
         ╚═══════════════════════════════╝
                   │
        ⑧ View 객체 반환
                   ↓
         ┌───────────────────────────────┐
         │         View                  │
         │      (JSP/Thymeleaf)          │
         └───────────────────────────────┘
                   │
        ⑨ 렌더링
                   ↓
         ┌───────────────────────────────┐
         │    ⑩ HTTP Response            │
         └───────────────────────────────┘
                   │
                   ↓
                [Browser]

설명:
1. 사용자가 URL 요청
2. DispatcherServlet이 HandlerMapping에게 처리 가능한 Controller 찾기 요청
3. HandlerMapping이 URL에 매핑된 Controller 반환
4. DispatcherServlet이 HandlerAdapter를 통해 Controller 메서드 실행
5. Controller가 Service 호출하여 비즈니스 로직 실행
6. Controller가 Model(데이터)과 View(화면) 이름 반환
7. DispatcherServlet이 ViewResolver에게 View 찾기 요청
8. ViewResolver가 실제 View 객체 반환
9. View가 Model 데이터로 렌더링
10. 최종 HTML을 사용자에게 응답
```

### DispatcherServlet 상세 동작

```
┌─────────────────────────────────────────────────────────┐
│           DispatcherServlet 내부 동작                    │
└─────────────────────────────────────────────────────────┘

doDispatch(request, response) {

    ① HandlerExecutionChain 획득
    ┌─────────────────────────────────┐
    │ HandlerExecutionChain            │
    │  - Handler (Controller 메서드)   │
    │  - Interceptor 목록              │
    └─────────────────────────────────┘

    ② preHandle 실행 (Interceptor)
    ┌─────────────────────────────────┐
    │ for (Interceptor : interceptors) │
    │   if (!interceptor.preHandle())  │
    │     return;                      │
    └─────────────────────────────────┘

    ③ Handler 실행
    ┌─────────────────────────────────┐
    │ HandlerAdapter.handle()          │
    │  - 파라미터 바인딩               │
    │  - Validator 실행                │
    │  - 컨트롤러 메서드 호출          │
    │  - 반환값 처리                   │
    └─────────────────────────────────┘

    ④ postHandle 실행 (Interceptor)
    ┌─────────────────────────────────┐
    │ for (Interceptor : interceptors) │
    │   interceptor.postHandle()       │
    └─────────────────────────────────┘

    ⑤ View 렌더링
    ┌─────────────────────────────────┐
    │ ViewResolver.resolveViewName()   │
    │ View.render(model, request)      │
    └─────────────────────────────────┘

    ⑥ afterCompletion 실행 (Interceptor)
    ┌─────────────────────────────────┐
    │ for (Interceptor : interceptors) │
    │   interceptor.afterCompletion()  │
    └─────────────────────────────────┘
}
```

---

## 💻 기본 실습

### 📋 사전 체크리스트

```bash
# 1. Java 버전 확인
java -version
# 필요: Java 11 이상

# 2. Maven/Gradle 확인
mvn -version
# 또는
gradle -version

# 3. IDE 준비
# IntelliJ IDEA, Eclipse, VS Code + Spring Extension
```

### 실습 1: Spring MVC 프로젝트 생성

**난이도**: ⭐☆☆☆☆

#### 프로젝트 구조

```
spring-mvc-demo/
├── src/
│   └── main/
│       ├── java/
│       │   └── com/
│       │       └── example/
│       │           ├── config/
│       │           │   └── WebConfig.java
│       │           └── controller/
│       │               └── HomeController.java
│       ├── resources/
│       └── webapp/
│           └── WEB-INF/
│               └── views/
│                   └── home.jsp
└── pom.xml
```

#### pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>spring-mvc-demo</artifactId>
    <version>1.0-SNAPSHOT</version>
    <packaging>war</packaging>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <spring.version>5.3.23</spring.version>
    </properties>

    <dependencies>
        <!-- Spring MVC -->
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-webmvc</artifactId>
            <version>${spring.version}</version>
        </dependency>

        <!-- Servlet API -->
        <dependency>
            <groupId>javax.servlet</groupId>
            <artifactId>javax.servlet-api</artifactId>
            <version>4.0.1</version>
            <scope>provided</scope>
        </dependency>

        <!-- JSP API -->
        <dependency>
            <groupId>javax.servlet.jsp</groupId>
            <artifactId>javax.servlet.jsp-api</artifactId>
            <version>2.3.3</version>
            <scope>provided</scope>
        </dependency>

        <!-- JSTL -->
        <dependency>
            <groupId>javax.servlet</groupId>
            <artifactId>jstl</artifactId>
            <version>1.2</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-war-plugin</artifactId>
                <version>3.3.2</version>
            </plugin>
        </plugins>
    </build>
</project>
```

#### WebConfig.java

```java
package com.example.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import org.springframework.web.servlet.view.InternalResourceViewResolver;
import org.springframework.web.servlet.view.JstlView;

// Spring MVC 설정 클래스
@Configuration
@EnableWebMvc  // Spring MVC 기능 활성화
@ComponentScan(basePackages = "com.example.controller")  // Controller 스캔
public class WebConfig implements WebMvcConfigurer {

    // ViewResolver 설정: 논리적 뷰 이름을 실제 JSP 파일로 변환
    @Bean
    public InternalResourceViewResolver viewResolver() {
        InternalResourceViewResolver resolver = new InternalResourceViewResolver();
        resolver.setViewClass(JstlView.class);
        resolver.setPrefix("/WEB-INF/views/");  // JSP 파일 경로 접두사
        resolver.setSuffix(".jsp");              // JSP 파일 확장자
        return resolver;
    }
}

/*
동작 설명:
- @EnableWebMvc: Spring MVC의 기본 설정 자동 적용
- @ComponentScan: Controller 클래스 자동 스캔
- viewResolver: "home" → "/WEB-INF/views/home.jsp" 변환
*/
```

#### HomeController.java

```java
package com.example.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

// Controller 선언: 이 클래스가 웹 요청을 처리함을 표시
@Controller
public class HomeController {

    // GET 요청 처리: http://localhost:8080/home
    @GetMapping("/home")
    public String home(Model model) {
        // Model에 데이터 추가: View에서 사용 가능
        model.addAttribute("message", "Welcome to Spring MVC!");
        model.addAttribute("timestamp", System.currentTimeMillis());

        // View 이름 반환: "home" → ViewResolver가 "/WEB-INF/views/home.jsp"로 변환
        return "home";
    }
}

/*
요청 처리 흐름:
1. 사용자가 /home 접속
2. DispatcherServlet이 이 메서드 호출
3. Model에 데이터 저장
4. "home" 반환
5. ViewResolver가 home.jsp 찾음
6. JSP가 렌더링되어 사용자에게 전달
*/
```

#### home.jsp

```jsp
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <title>Spring MVC Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f0f0f0;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #6db33f;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌱 Spring MVC</h1>

        <!-- Controller에서 전달한 데이터 출력 -->
        <p><strong>메시지:</strong> ${message}</p>
        <p><strong>타임스탬프:</strong> ${timestamp}</p>

        <hr>

        <h2>동작 원리</h2>
        <ol>
            <li>사용자가 /home 요청</li>
            <li>DispatcherServlet이 요청 수신</li>
            <li>HandlerMapping이 HomeController 찾기</li>
            <li>Controller가 Model에 데이터 저장</li>
            <li>ViewResolver가 home.jsp 찾기</li>
            <li>JSP가 렌더링</li>
            <li>최종 HTML 응답</li>
        </ol>
    </div>
</body>
</html>
```

#### WebApplicationInitializer (web.xml 대체)

```java
package com.example.config;

import org.springframework.web.servlet.support.AbstractAnnotationConfigDispatcherServletInitializer;

// Java Config로 DispatcherServlet 설정 (web.xml 없이)
public class WebAppInitializer extends AbstractAnnotationConfigDispatcherServletInitializer {

    // Root WebApplicationContext 설정
    @Override
    protected Class<?>[] getRootConfigClasses() {
        return null;  // Root config가 필요하면 여기에 추가
    }

    // Servlet WebApplicationContext 설정
    @Override
    protected Class<?>[] getServletConfigClasses() {
        return new Class[] { WebConfig.class };
    }

    // DispatcherServlet 매핑 URL
    @Override
    protected String[] getServletMappings() {
        return new String[] { "/" };  // 모든 요청을 DispatcherServlet이 처리
    }
}

/*
이 클래스는 다음과 같은 web.xml을 대체합니다:

<web-app>
    <servlet>
        <servlet-name>dispatcher</servlet-name>
        <servlet-class>org.springframework.web.servlet.DispatcherServlet</servlet-class>
        <init-param>
            <param-name>contextConfigLocation</param-name>
            <param-value>com.example.config.WebConfig</param-value>
        </init-param>
    </servlet>
    <servlet-mapping>
        <servlet-name>dispatcher</servlet-name>
        <url-pattern>/</url-pattern>
    </servlet-mapping>
</web-app>
*/
```

#### 실행

```bash
# Maven으로 빌드
mvn clean package

# Tomcat에 배포
# - target/spring-mvc-demo.war 파일을 Tomcat의 webapps 폴더에 복사
# - Tomcat 시작

# 또는 Maven Tomcat 플러그인 사용
mvn tomcat7:run
```

#### 예상 출력

브라우저에서 `http://localhost:8080/home` 접속 시:

```
🌱 Spring MVC

메시지: Welcome to Spring MVC!
타임스탬프: 1698765432100

동작 원리
1. 사용자가 /home 요청
2. DispatcherServlet이 요청 수신
3. HandlerMapping이 HomeController 찾기
4. Controller가 Model에 데이터 저장
5. ViewResolver가 home.jsp 찾기
6. JSP가 렌더링
7. 최종 HTML 응답
```

#### 코드 설명

**핵심 구성 요소:**

1. **WebConfig.java**
   - `@EnableWebMvc`: Spring MVC 기능 활성화
   - `@ComponentScan`: Controller 자동 스캔
   - `viewResolver()`: View 이름 → JSP 파일 매핑

2. **HomeController.java**
   - `@Controller`: 웹 요청 처리 클래스
   - `@GetMapping`: HTTP GET 요청 매핑
   - `Model`: View로 데이터 전달

3. **WebAppInitializer.java**
   - `DispatcherServlet` 자동 등록
   - URL 패턴 매핑
   - WebConfig 연결

**데이터 흐름:**
```
Request → DispatcherServlet → HandlerMapping
→ Controller → Model → ViewResolver → View → Response
```

### 실습 2: 다양한 URL 매핑

**난이도**: ⭐⭐☆☆☆

#### ProductController.java

```java
package com.example.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping("/products")  // 클래스 레벨 매핑: 모든 메서드의 기본 경로
public class ProductController {

    // GET /products - 상품 목록
    @GetMapping
    public String list(Model model) {
        model.addAttribute("title", "상품 목록");
        return "products/list";
    }

    // GET /products/123 - 특정 상품 조회 (경로 변수 사용)
    @GetMapping("/{id}")
    public String detail(@PathVariable("id") Long id, Model model) {
        model.addAttribute("productId", id);
        model.addAttribute("productName", "Sample Product " + id);
        model.addAttribute("price", 10000);
        return "products/detail";
    }

    // GET /products/search?keyword=laptop - 검색 (쿼리 파라미터 사용)
    @GetMapping("/search")
    public String search(
        @RequestParam(value = "keyword", required = false, defaultValue = "") String keyword,
        @RequestParam(value = "minPrice", required = false, defaultValue = "0") int minPrice,
        Model model
    ) {
        model.addAttribute("keyword", keyword);
        model.addAttribute("minPrice", minPrice);
        model.addAttribute("message", "검색어: " + keyword + ", 최소가격: " + minPrice);
        return "products/search";
    }

    // GET /products/category/electronics - 카테고리별 조회
    @GetMapping("/category/{categoryName}")
    public String category(
        @PathVariable String categoryName,
        @RequestParam(defaultValue = "1") int page,
        Model model
    ) {
        model.addAttribute("category", categoryName);
        model.addAttribute("page", page);
        return "products/category";
    }

    // GET /products/new - 상품 등록 폼
    @GetMapping("/new")
    public String newProductForm(Model model) {
        model.addAttribute("title", "새 상품 등록");
        return "products/form";
    }

    // POST /products - 상품 등록 처리
    @PostMapping
    public String create(
        @RequestParam String name,
        @RequestParam int price,
        Model model
    ) {
        // 실제로는 Service를 호출하여 DB 저장
        model.addAttribute("message", "상품 등록 완료: " + name + " (가격: " + price + "원)");
        return "products/result";
    }
}

/*
URL 매핑 패턴:
- @RequestMapping("/products"): 기본 경로 설정
- @GetMapping: GET 요청 매핑
- @PostMapping: POST 요청 매핑
- @PathVariable: URL 경로의 변수 추출
- @RequestParam: 쿼리 파라미터 추출

예시 URL:
- /products → list()
- /products/123 → detail(123)
- /products/search?keyword=laptop → search("laptop", 0)
- /products/category/electronics?page=2 → category("electronics", 2)
- /products/new → newProductForm()
*/
```

#### 실행 예시

```bash
# 1. 상품 목록
GET http://localhost:8080/products
→ list() 메서드 실행

# 2. 상품 상세 (ID=5)
GET http://localhost:8080/products/5
→ detail(5) 메서드 실행

# 3. 상품 검색
GET http://localhost:8080/products/search?keyword=laptop&minPrice=500000
→ search("laptop", 500000) 메서드 실행

# 4. 카테고리별 조회 (2페이지)
GET http://localhost:8080/products/category/electronics?page=2
→ category("electronics", 2) 메서드 실행

# 5. 상품 등록 폼
GET http://localhost:8080/products/new
→ newProductForm() 메서드 실행

# 6. 상품 등록 처리
POST http://localhost:8080/products
Content-Type: application/x-www-form-urlencoded
name=Laptop&price=1000000
→ create("Laptop", 1000000) 메서드 실행
```

---

## 📝 핵심 정리

### 이 장에서 배운 핵심 개념

| 개념 | 설명 | 핵심 키워드 |
|------|------|-------------|
| Spring MVC | Model-View-Controller 패턴 웹 프레임워크 | DispatcherServlet, MVC |
| DispatcherServlet | 모든 요청의 진입점 (Front Controller) | 단일 진입점, 요청 분배 |
| HandlerMapping | URL과 Controller 메서드 매핑 | @RequestMapping, URL 매핑 |
| Controller | 요청 처리 및 응답 반환 | @Controller, @GetMapping |
| Model | View로 데이터 전달하는 객체 | model.addAttribute() |
| ViewResolver | 논리적 뷰 이름을 실제 View로 변환 | prefix, suffix |
| View | 최종 결과를 렌더링 | JSP, Thymeleaf |

### 필수 어노테이션 정리

| 어노테이션 | 용도 | 예시 |
|-----------|------|------|
| `@Controller` | Controller 클래스 선언 | `@Controller public class HomeController` |
| `@RequestMapping` | URL 매핑 (클래스/메서드) | `@RequestMapping("/home")` |
| `@GetMapping` | HTTP GET 요청 매핑 | `@GetMapping("/list")` |
| `@PostMapping` | HTTP POST 요청 매핑 | `@PostMapping("/create")` |
| `@PathVariable` | URL 경로 변수 추출 | `@PathVariable("id") Long id` |
| `@RequestParam` | 쿼리 파라미터 추출 | `@RequestParam String name` |

### 요청 처리 흐름 정리

```
1. 사용자 요청 (HTTP Request)
   ↓
2. DispatcherServlet이 요청 수신
   ↓
3. HandlerMapping이 적절한 Controller 찾기
   ↓
4. HandlerAdapter가 Controller 메서드 실행
   ↓
5. Controller가 비즈니스 로직 처리 (Service 호출)
   ↓
6. Controller가 Model에 데이터 저장 & ViewName 반환
   ↓
7. ViewResolver가 ViewName → 실제 View 변환
   ↓
8. View가 Model 데이터로 렌더링
   ↓
9. DispatcherServlet이 응답 전송 (HTTP Response)
   ↓
10. 사용자가 결과 확인
```

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] Controller는 요청 처리만, 비즈니스 로직은 Service로 분리
- [ ] RESTful URL 설계 (`/products/123`, `/users/new`)
- [ ] 명확한 HTTP 메서드 사용 (GET, POST, PUT, DELETE)
- [ ] @RequestParam에 기본값 설정 (`defaultValue`)
- [ ] 에러 처리용 @ExceptionHandler 구현

#### ❌ 하지 말아야 할 것
- [ ] Controller에 DB 접근 로직 작성하지 않기
- [ ] 모든 요청을 GET으로 처리하지 않기
- [ ] Model에 불필요한 데이터 담지 않기
- [ ] ViewName에 확장자 포함하지 않기 ("home.jsp" → "home")
- [ ] 한 메서드에 여러 책임 부여하지 않기

---

## 🚀 다음 단계

### 다음 장 미리보기: 11장-2: Spring MVC 개요 - 설정과 실습

**배울 내용:**
- **실무 활용 사례**: 네이버, 카카오, 배달의민족의 Spring MVC 활용
- **주니어 시나리오**: 자주 하는 실수와 해결 방법
- **실전 프로젝트**: 게시판 CRUD 구현
- **면접 질문**: 주니어/중급 면접 대비 질문과 답변
- **FAQ**: 실무에서 자주 묻는 질문들

### 이 장과의 연결점

```
11장-1: 기본 개념 이해
    ↓
11장-2: 실무 활용과 심화
    ↓
12장: 컨트롤러와 요청 매핑 상세
    ↓
최종 목표: Spring MVC 완벽 마스터
```

---

**다음 장으로 이동**: [다음: 11장-2: 설정과 실습 →](SpringMVC-Part2-11-2-Overview-Practice.md)

**목차로 돌아가기**: [📚 전체 목차](README.md)
