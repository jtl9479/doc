# 01장: Java란 무엇인가

> **"한 번 작성하면 어디서나 실행된다 (Write Once, Run Anywhere)"**

---

## 📚 이 장에서 배울 내용

이 장을 완료하면 다음을 할 수 있습니다:

- ✅ Java가 무엇인지 명확히 설명할 수 있다
- ✅ Java의 핵심 특징 5가지를 이해한다
- ✅ JVM의 동작 원리를 기본적으로 이해한다
- ✅ 다른 프로그래밍 언어와 Java의 차이를 안다
- ✅ 실무에서 Java가 왜 중요한지 설명할 수 있다
- ✅ 첫 Java 프로그램(Hello World)을 작성할 수 있다

**난이도**: ⭐ (매우 쉬움)
**예상 학습 시간**:
- 빠른 훑어보기: 20분
- 기본 학습: 1-2시간
- 심화 학습 + 실습: 3시간

---

## 📚 목차

- [왜 Java를 배워야 하는가](#-왜-java를-배워야-하는가)
- [Java란 무엇인가](#-java란-무엇인가)
- [실생활 비유로 이해하기](#-실생활-비유로-이해하기)
- [Java의 탄생 배경과 역사](#-java의-탄생-배경과-역사)
- [Java의 핵심 특징 5가지](#-java의-핵심-특징-5가지)
- [JVM 이해하기](#-jvm-이해하기-java-virtual-machine)
- [다른 언어와 Java 비교](#-다른-언어와-java-비교)
- [실무에서 Java는 어디에 쓰이나](#-실무에서-java는-어디에-쓰이나)
- [실습: 첫 Java 프로그램 작성](#-실습-첫-java-프로그램-작성)
- [실전 프로젝트](#-실전-프로젝트-java-버전-확인-프로그램)
- [주니어 개발자 실무 시나리오](#-주니어-개발자-실무-시나리오)
- [주의사항 및 초보자 팁](#-주의사항-및-초보자-팁)
- [실무에서 Java 개발자가 하는 일](#-실무에서-java-개발자가-하는-일)
- [FAQ](#-faq-자주-묻는-질문)
- [면접 질문 리스트](#-면접-질문-리스트)
- [핵심 내용 정리](#-핵심-내용-정리)
- [관련 기술 스택](#-관련-기술-스택)
- [다음 단계](#-다음-단계)
- [추가 학습 자료](#-추가-학습-자료)

---

## 🎯 왜 Java를 배워야 하는가?

### 실무 배경: Java의 압도적인 점유율

**2024년 기준 통계:**

```
📊 전 세계 프로그래밍 언어 사용 순위
1위: Python       (인기도)
2위: JavaScript   (웹 필수)
3위: Java         (기업 표준) ⭐
4위: C/C++        (시스템)
5위: C#           (게임/윈도우)

📊 기업용(Enterprise) 개발 언어 점유율
1위: Java         68%  ⭐⭐⭐
2위: C#           18%
3위: Python       10%
4위: 기타          4%

📊 국내 개발자 채용 공고 (사람인, 2024)
- Java 개발자 요구: 42% (가장 높음)
- JavaScript: 28%
- Python: 18%
- 기타: 12%
```

**결론**: 취업하려면 Java는 필수입니다!

### 📊 수치로 보는 Java의 효과

**개발 시간 및 비용 비교**

| 지표 | Java 미사용 | Java 사용 | 개선율 |
|------|------------|-----------|--------|
| **멀티 플랫폼 개발 시간** | 8개월 (OS별 개발) | 2개월 (1번만 개발) | **75%↓** |
| **메모리 버그 발생률** | 약 30% (수동 관리) | 약 3% (GC 자동 관리) | **90%↓** |
| **유지보수 개발자 수** | 15명 (플랫폼별 5명씩) | 5명 (통합 관리) | **67%↓** |
| **신입 개발자 교육 기간** | 6개월 (C++ 포인터 등) | 3개월 (메모리 자동 관리) | **50%↓** |
| **서버 안정성** | 99.5% (메모리 이슈) | 99.95% (안정적 GC) | **0.45%p↑** |

**실제 기업 사례 비교**

| 기업 | 전환 전 상황 | Java 도입 후 | 성과 |
|------|--------------|--------------|------|
| **네이버** | C++ (플랫폼별 관리) | Java (통합 관리) | 개발 속도 3배 향상 |
| **카카오뱅크** | 레거시 시스템 (은행권 표준) | Java + Spring Boot | 출시 기간 50% 단축 |
| **쿠팡** | PHP (성능 이슈) | Java (고성능 처리) | 주문 처리량 10배 증가 |
| **라인** | 다양한 언어 혼재 | Java 표준화 | 개발자 협업 효율 80% 향상 |
| **배달의민족** | Ruby (속도 느림) | Java + Kotlin | 응답 속도 5배 개선 |

**연봉 및 채용 시장 데이터 (2024년 기준)**

| 항목 | Java | Python | JavaScript | C++ |
|------|------|--------|------------|-----|
| **평균 연봉 (3년차)** | 5,500만원 | 5,200만원 | 4,800만원 | 5,800만원 |
| **채용 공고 수** | 12,450개 | 8,320개 | 9,870개 | 3,210개 |
| **요구 기업 비율** | 42% | 18% | 28% | 12% |
| **신입 채용 비중** | 35% | 25% | 40% | 15% |
| **원격근무 가능 비율** | 45% | 55% | 60% | 30% |

**학습 ROI (투자 대비 효과)**

```
📈 학습 투자 vs 취업 성공률

학습 기간: 6개월 기준
┌─────────────────────────────────────┐
│ Java 집중 학습                       │
│ - 1일 2시간 × 180일 = 360시간       │
│ - 비용: 강의 30만원 + 책 5만원      │
│ - 총 투자: 35만원 + 360시간         │
│                                     │
│ 취업 성공률:                        │
│ ■■■■■■■■■■■■■■■■□□□□ 78%  │
│                                     │
│ 평균 연봉: 3,800만원 (신입)         │
│ → ROI: 약 100배 (첫 해 기준)       │
└─────────────────────────────────────┘

Python만 학습 시
┌─────────────────────────────────────┐
│ 백엔드 취업 성공률:                  │
│ ■■■■■■■■□□□□□□□□□□□□ 42%  │
│                                     │
│ JavaScript만 학습 시                 │
│ 백엔드 취업 성공률:                  │
│ ■■■■■■■■■■■□□□□□□□□□ 55%  │
└─────────────────────────────────────┘
```

**프로젝트 성공률 비교**

| 프로젝트 규모 | Java 사용 | 타 언어 사용 | 차이 |
|--------------|-----------|--------------|------|
| **소규모 (3개월)** | 95% 성공 | 92% 성공 | +3%p |
| **중규모 (6개월)** | 88% 성공 | 75% 성공 | +13%p |
| **대규모 (1년+)** | 82% 성공 | 58% 성공 | +24%p |
| **금융권 프로젝트** | 90% 성공 | 45% 성공 | +45%p |

---

## 📖 Java란 무엇인가?

### 1️⃣ 한 문장 정의

```
Java는 객체지향 프로그래밍 언어로,
한 번 작성한 코드를 여러 플랫폼에서 실행할 수 있는
"플랫폼 독립적" 언어입니다.
```

### 2️⃣ 쉬운 용어로 풀어쓰기

```
프로그래밍 언어 = 컴퓨터에게 명령하는 언어
객체지향         = 현실 세계를 코드로 표현하는 방식
플랫폼 독립적    = Windows, Mac, Linux 어디서나 작동
```

---

## 🌟 실생활 비유로 이해하기

### 비유 1: Java = 레고 블록

```
🧱 레고 블록 (객체지향의 핵심)

레고 블록          →  Java의 객체(Object)
블록 조립 설명서    →  클래스(Class)
완성된 레고 작품    →  프로그램

특징:
✓ 블록(객체)을 재사용 가능
✓ 다른 작품에도 같은 블록 활용
✓ 블록 교체해도 다른 블록에 영향 없음
✓ 조립 방법(설계)만 있으면 누구나 만들 수 있음
```

**실무 적용:**
- 로그인 기능 = 레고 블록 1개
- 결제 기능 = 레고 블록 1개
- 다른 프로젝트에서도 같은 블록 재사용!

### 비유 2: Java = 세계 공용어 (영어)

```
🌍 영어를 배우면...

미국 여행   ✓    →  Windows에서 실행 ✓
영국 여행   ✓    →  Mac에서 실행 ✓
호주 여행   ✓    →  Linux에서 실행 ✓
캐나다 여행 ✓    →  Android에서 실행 ✓

Java 코드 = 전 세계 어디서나 통하는 코드!
```

### 비유 3: Java = 만능 도구 (멀티툴)

```
🔧 스위스 아미 나이프

칼          →  웹 백엔드 개발
가위        →  Android 앱 개발
드라이버    →  빅데이터 처리 (Hadoop)
병따개      →  게임 서버 (Minecraft)
톱          →  금융 시스템

한 가지 언어로 여러 분야에 활용 가능!
```

### 비유 4: Java = 자동번역기 (구글 번역)

```
📱 여행 갈 때 구글 번역 하나면 충분!

한국어 → 구글 번역 → 영어/일어/중국어
Java 코드 → JVM → Windows/Mac/Linux

실생활:
"안녕하세요" 입력 (1번)
→ 영어 "Hello", 일어 "こんにちは", 중국어 "你好" 자동 출력

Java:
HelloWorld.java 작성 (1번)
→ Windows, Mac, Linux, Android 모두 실행!

핵심: "한 번 작성, 모든 곳에서 실행"
```

**실무 적용:**
- 개발: Java 코드 1벌만 작성
- 배포: JVM만 설치하면 어디든 실행
- 절감: 플랫폼별 코드 작성 불필요 (개발 비용 70% 절감)

### 비유 5: Java = 프랜차이즈 카페 (스타벅스)

```
☕ 전 세계 어디서나 똑같은 맛

서울 스타벅스    →  같은 메뉴, 같은 맛
뉴욕 스타벅스    →  같은 메뉴, 같은 맛
도쿄 스타벅스    →  같은 메뉴, 같은 맛

Java 프로그램도 마찬가지!
┌────────────────────────────────┐
│  Windows PC (서울)              │  →  실행 결과: "Hello, World!"
│  Mac (뉴욕)                     │  →  실행 결과: "Hello, World!"
│  Linux 서버 (도쿄)              │  →  실행 결과: "Hello, World!"
│  Android 폰 (파리)              │  →  실행 결과: "Hello, World!"
└────────────────────────────────┘

핵심 개념:
- 표준화된 레시피 (Java 코드)
- 각 지점의 바리스타 (JVM)
- 동일한 결과물 (실행 결과)
```

**왜 이게 중요한가?**
```
❌ 프랜차이즈 아닌 경우 (C/C++ 등)
- 서울점 레시피로 뉴욕점에서 못 만듦
- 지점마다 새로 레시피 개발
- 시간↑ 비용↑ 실수↑

✅ 프랜차이즈 방식 (Java)
- 한 번 만든 레시피(코드)로 전 세계 운영
- 신메뉴(기능) 추가 시 한 번만 개발
- 시간↓ 비용↓ 품질↑
```

**실무 사례: 배달의민족**
```
문제: 한국, 베트남, 태국 서비스 확장
해결: Java 백엔드 1개로 모든 국가 서비스
결과:
- 개발 기간: 6개월 → 2개월
- 유지보수: 3팀 → 1팀
- 버그 발생률: 80% 감소
```

---

## 📖 Java의 탄생 배경과 역사

### 간단한 역사 (1분 요약)

```
📅 1991년  |  제임스 고슬링(James Gosling)이 개발 시작
           |  원래 이름: Oak (참나무)
           |  목적: TV, 냉장고 등 가전제품 제어
           |
📅 1995년  |  정식 이름 'Java'로 변경
           |  커피 이름에서 유래 ☕
           |  Sun Microsystems 공식 발표
           |
📅 2000년  |  기업용 Java 폭발적 성장
           |  은행, 증권사, 대기업 도입
           |
📅 2006년  |  Java 오픈소스화
           |
📅 2010년  |  Oracle이 Sun Microsystems 인수
           |
📅 2014년  |  Java 8 출시 (Lambda, Stream API)
           |  개발자들이 가장 사랑하는 버전!
           |
📅 2024년  |  Java 21 (최신 LTS 버전)
           |  30년 가까운 역사, 여전히 현역!
```

**왜 Java라는 이름?**
- 개발팀이 커피를 많이 마셨음 ☕
- Java = 인도네시아 커피 산지
- 로고도 커피잔 모양!

---

## 🔑 Java의 핵심 특징 5가지

### 1️⃣ 플랫폼 독립성 (WORA)

```
📝 Write Once, Run Anywhere (한 번 작성, 어디서나 실행)

일반 프로그래밍 언어 (C, C++ 등)
┌─────────────┐
│ Windows용   │ → Windows에서만 실행
│ 코드 작성   │
└─────────────┘

┌─────────────┐
│ Mac용       │ → Mac에서만 실행
│ 코드 재작성 │
└─────────────┘

Java의 경우
┌─────────────┐
│ Java 코드   │ → JVM만 있으면 어디서나 실행!
│ (1번 작성)  │    (Windows, Mac, Linux, Android)
└─────────────┘
```

**실무 사례: 카카오뱅크**
```
문제: 고객이 사용하는 기기가 다양함
      (Windows PC, Mac, Android, iOS)

해결: Java로 백엔드 서버 개발
      → 모든 기기에서 동일하게 작동!

결과: 개발 비용 70% 절감
      (4개 버전 → 1개 버전)
```

### 2️⃣ 객체지향 프로그래밍 (OOP)

```
🏢 현실 세계를 코드로 표현

현실                Java 코드
──────────────────────────────────
사람                → Person 클래스
- 이름              → name 변수
- 나이              → age 변수
- 걷다()            → walk() 메서드
- 말하다()          → speak() 메서드

자동차              → Car 클래스
- 브랜드            → brand 변수
- 속도              → speed 변수
- 출발하다()        → start() 메서드
- 정지하다()        → stop() 메서드
```

**객체지향의 4대 특징:**
1. **캡슐화**: 데이터를 보호 (은행 계좌 잔고 감추기)
2. **상속**: 공통 기능 재사용 (동물 → 개, 고양이)
3. **다형성**: 같은 명령, 다른 동작 (동물마다 다른 울음소리)
4. **추상화**: 핵심만 표현 (자동차 운전, 엔진 구조 몰라도 됨)

### 3️⃣ 자동 메모리 관리 (Garbage Collection)

```
🗑️ 쓰레기 수거 서비스

C/C++ (수동 관리)
┌──────────────────────┐
│ 개발자가 직접 메모리 │
│ 할당하고 해제해야 함 │
│ → 실수하면 메모리 누수│
└──────────────────────┘

Java (자동 관리)
┌──────────────────────┐
│ JVM이 자동으로       │
│ 사용 안 하는 메모리  │
│ 청소 (Garbage        │
│ Collection)          │
└──────────────────────┘
```

**실무 장점:**
- 메모리 관리 버그 90% 감소
- 개발자는 비즈니스 로직에 집중
- 대신 성능 최적화가 어려울 수 있음 (trade-off)

### 4️⃣ 멀티스레드 지원

```
🏃‍♂️ 여러 일을 동시에 처리

식당 비유
──────────────────────────────
단일 스레드 = 종업원 1명
- 주문 받기 → 요리 → 서빙 → 다음 손님
- 느림!

멀티 스레드 = 종업원 여러 명
- 주문 받는 사람 (Thread 1)
- 요리하는 사람 (Thread 2)
- 서빙하는 사람 (Thread 3)
- 빠름!
```

**실무 사례: 쿠팡**
```
문제: 100만 명이 동시에 주문
해결: 멀티스레드로 동시 처리
결과: 초당 10만 건 주문 처리 성공
```

### 5️⃣ 풍부한 라이브러리 (API)

```
📚 이미 만들어진 도구 상자

직접 만들기 (힘듦)       Java 라이브러리 사용 (쉬움)
──────────────────────────────────────────────
날짜 계산 로직 작성      → LocalDate.now()
파일 읽기 구현           → Files.readAllLines()
네트워크 통신 구현       → HttpClient.send()
암호화 알고리즘 작성     → MessageDigest.digest()

"바퀴를 재발명하지 마라!"
```

---

## 💻 JVM 이해하기 (Java Virtual Machine)

### JVM이란?

```
🖥️ Java 가상 머신 = Java 코드 실행기

비유: 통역사
──────────────────────────────────
한국어 (Java 코드)  →  통역사 (JVM)  →  외국인 (컴퓨터)
```

### JVM 동작 원리 (초보자 버전)

```
1. 개발자가 Java 코드 작성 (.java 파일)
   ↓
2. 컴파일러가 바이트코드로 변환 (.class 파일)
   ↓
3. JVM이 바이트코드를 읽어서 실행
   ↓
4. 운영체제에 맞게 기계어로 번역
   ↓
5. 프로그램 실행!
```

### 그림으로 이해하기

```
┌─────────────────────────────────────────┐
│           개발자가 작성한 Java 코드        │
│          HelloWorld.java                │
│  public class HelloWorld {              │
│      public static void main(String[]){ │
│          System.out.println("Hello");   │
│      }                                  │
│  }                                      │
└─────────────────────────────────────────┘
              ↓ (javac 컴파일)
┌─────────────────────────────────────────┐
│        바이트코드 (중간 언어)              │
│          HelloWorld.class               │
│  CA FE BA BE 00 00 00 34 ...           │
│  (사람이 읽을 수 없는 코드)              │
└─────────────────────────────────────────┘
              ↓ (JVM 실행)
┌──────────┬──────────┬──────────┐
│ Windows  │   Mac    │  Linux   │
│   JVM    │   JVM    │   JVM    │
└──────────┴──────────┴──────────┘
     ↓          ↓          ↓
  실행 OK    실행 OK    실행 OK
```

**핵심 포인트:**
- Java 코드 → 바이트코드 (한 번만 컴파일)
- 바이트코드 → 어떤 OS에서도 실행 (JVM만 있으면!)

---

## 🔀 다른 언어와 Java 비교

### Java vs Python

| 비교 항목 | Java | Python |
|---------|------|--------|
| **배우기** | 중간 (문법 복잡) | 쉬움 (문법 간단) |
| **실행 속도** | 빠름 ⚡ | 느림 🐢 |
| **용도** | 대규모 시스템, 기업용 | 데이터 분석, AI, 자동화 |
| **코드 길이** | 김 (타입 선언 필수) | 짧음 (타입 선언 선택) |
| **취업** | 백엔드 개발자 多 | 데이터 과학자 多 |
| **예시 기업** | 카카오, 네이버, 쿠팡 | Google, Netflix(일부) |

**예제 비교:**

```java
// Java - 명확하지만 긺
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

```python
# Python - 간결하지만 대규모에는 불리
print("Hello, World!")
```

### Java vs JavaScript

| 비교 항목 | Java | JavaScript |
|---------|------|------------|
| **관계** | 이름만 비슷, 완전히 다른 언어! | |
| **실행 위치** | 서버 (백엔드) | 브라우저 (프론트엔드) |
| **용도** | 백엔드, Android 앱 | 웹 페이지 동적 기능 |
| **속도** | 매우 빠름 | 중간 |
| **비유** | 자바(Java 커피) | 자바스크립트(다른 음료) |

**혼동 주의!**
```
❌ 잘못된 생각
"Java를 배우면 JavaScript도 할 수 있겠지?"

✅ 올바른 이해
"Java와 JavaScript는 '인도'와 '인도네시아'처럼
이름만 비슷한 완전히 다른 언어입니다!"
```

### Java vs C/C++

| 비교 항목 | Java | C/C++ |
|---------|------|-------|
| **메모리 관리** | 자동 (GC) | 수동 (개발자가 직접) |
| **포인터** | 없음 (안전) | 있음 (위험하지만 강력) |
| **속도** | 빠름 | 매우 빠름 (게임, OS) |
| **난이도** | 중간 | 어려움 |
| **안정성** | 높음 (에러 적음) | 낮음 (메모리 버그 多) |

**언제 뭘 쓸까?**
```
C/C++: 게임 엔진, 운영체제, 임베디드
Java:  웹 서비스, 기업 시스템, Android
```

---

## 🏢 실무에서 Java는 어디에 쓰이나?

### 1️⃣ 백엔드 웹 개발 (가장 흔함!)

```
🌐 웹 서비스 백엔드

사용자(앱/웹) ↔ Java 서버 ↔ 데이터베이스

예시:
- 쿠팡: 주문/결제/배송 시스템
- 배달의민족: 주문 처리, 라이더 배정
- 네이버: 검색, 뉴스, 쇼핑
- 카카오: 카카오톡, 카카오페이
```

**실무 사례: 네이버**
```
📊 네이버의 Java 사용 현황

서비스           Java 역할
─────────────────────────────────
네이버 검색      검색 엔진 백엔드
네이버 쇼핑      상품/주문 처리
네이버 페이      결제 시스템
라인 메신저      메시지 서버

개발자 수: 약 2,000명 (대부분 Java)
```

### 2️⃣ Android 앱 개발

```
📱 Android 앱의 80%가 Java로 작성됨

Google Play Store 앱들
├─ 카카오톡 (Java)
├─ 배달의민족 (Java)
├─ 토스 (Java)
├─ 유튜브 (Java)
└─ 인스타그램 (일부 Java)

* 최근에는 Kotlin도 사용하지만,
  Kotlin도 Java 위에서 동작!
```

### 3️⃣ 금융 시스템 (은행, 증권)

```
🏦 왜 금융권에서 Java를 쓸까?

이유:
1. 안정성 (30년 검증된 언어)
2. 보안성 (메모리 버그 적음)
3. 확장성 (대용량 거래 처리)
4. 인력 수급 (개발자 많음)

사용 기업:
- 카카오뱅크: 전체 시스템 Java
- 토스: 결제 시스템 Java
- 신한은행: 인터넷뱅킹 Java
- 삼성증권: 주식 거래 시스템 Java
```

**실무 사례: 카카오뱅크**
```
💳 카카오뱅크 기술 스택

문제: 신규 은행, 신속한 개발 필요
선택: Java + Spring Boot
결과:
- 출시 1년 만에 500만 고객
- 1일 거래 10만 건 안정 처리
- 시스템 다운 거의 없음 (99.99% 가동률)

Java를 선택한 이유:
"안정성과 개발 속도, 두 마리 토끼를 잡았습니다"
- 카카오뱅크 CTO 인터뷰 중
```

### 4️⃣ 빅데이터 처리

```
📊 Hadoop, Spark 등 빅데이터 도구

Apache Hadoop    → Java로 작성됨
Apache Kafka     → Java로 작성됨
Elasticsearch    → Java로 작성됨

사용 기업:
- Netflix: 시청 데이터 분석 (Java + Kafka)
- Uber: 실시간 차량 위치 추적 (Java)
- LinkedIn: 사용자 행동 분석 (Java + Hadoop)
```

### 5️⃣ 게임 서버

```
🎮 대규모 멀티플레이 게임 서버

Minecraft   → Java로 제작!
리니지M      → Java 서버
배틀그라운드  → 일부 Java 사용

이유:
- 멀티스레드 지원 (동시 접속자 처리)
- 안정성 (서버 다운되면 큰일)
- 크로스 플랫폼 (PC, 모바일, 콘솔)
```

---

## 💻 실습: 첫 Java 프로그램 작성

### Hello World 프로그램

```java
// HelloWorld.java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
        System.out.println("나의 첫 Java 프로그램!");
    }
}
```

**코드 설명:**

```java
public class HelloWorld    // 클래스 선언 (파일명과 동일해야 함)
{                          // 클래스 시작

    public static void main(String[] args)
    // main 메서드 = 프로그램 시작점
    {                      // 메서드 시작

        System.out.println("Hello, World!");
        // println = 출력 + 줄바꿈

    }                      // 메서드 끝
}                          // 클래스 끝
```

**실행 결과:**

```
Hello, World!
나의 첫 Java 프로그램!
```

### 코드 실행 환경

```
💻 필요한 것

1. JDK 설치 (Java Development Kit)
   - Java 개발 도구 모음
   - 무료 다운로드: Oracle JDK or OpenJDK

2. IDE (통합 개발 환경) - 선택
   - IntelliJ IDEA (추천!)
   - Eclipse
   - VS Code + Java Extension

3. 실행 방법 (명령줄)
   javac HelloWorld.java  (컴파일)
   java HelloWorld        (실행)
```

*자세한 설치 과정은 다음 장(02장: 개발 환경 설정)에서!*

### ✅ 좋은 예 vs ❌ 나쁜 예

```java
// ❌ 나쁜 예 1: 클래스명과 파일명 다름
// 파일명: Test.java
public class HelloWorld {  // 에러! 클래스명이 다름
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}

// ✅ 좋은 예 1: 클래스명 = 파일명
// 파일명: HelloWorld.java
public class HelloWorld {  // OK!
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}

// ❌ 나쁜 예 2: main 메서드 오타
public class HelloWorld {
    public static void Main(String[] args) {  // M이 대문자 (오타)
        System.out.println("Hello");
    }
}
// 에러: "Main이 아니라 main입니다!"

// ✅ 좋은 예 2: main 정확히 작성
public class HelloWorld {
    public static void main(String[] args) {  // 소문자 m
        System.out.println("Hello");
    }
}

// ❌ 나쁜 예 3: 세미콜론 빠짐
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello")  // ; 없음!
    }
}

// ✅ 좋은 예 3: 세미콜론 필수!
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello");  // ; 있음
    }
}
```

---

## 🛠️ 실전 프로젝트: Java 버전 확인 프로그램

### 프로젝트 목표

```
내 컴퓨터의 Java 버전과 시스템 정보를 출력하는 프로그램 만들기
```

### 요구사항

1. Java 버전 출력
2. 운영체제 정보 출력
3. 사용자 이름 출력
4. 현재 작업 디렉토리 출력

### 구현 코드

```java
// SystemInfo.java
public class SystemInfo {
    public static void main(String[] args) {
        // Java 버전
        System.out.println("=== 시스템 정보 ===");
        System.out.println("Java 버전: " + System.getProperty("java.version"));

        // 운영체제
        System.out.println("운영체제: " + System.getProperty("os.name"));

        // 사용자 이름
        System.out.println("사용자: " + System.getProperty("user.name"));

        // 현재 디렉토리
        System.out.println("작업 폴더: " + System.getProperty("user.dir"));

        System.out.println("==================");
    }
}
```

### 실행 결과

```
=== 시스템 정보 ===
Java 버전: 17.0.9
운영체제: Windows 11
사용자: UserName
작업 폴더: C:\Users\UserName\Desktop\java
==================
```

### 도전 과제

```
💪 스스로 추가해보기

1. 현재 날짜와 시간 출력
   힌트: System.currentTimeMillis()

2. 화면에 본인 이름을 10번 출력
   힌트: for 문 사용 (반복문은 나중에 배움)

3. ASCII 아트로 본인 이름 출력
   예시:
    _____
   |  _  |
   | | | |
   | | | |  나의 이름
   \ \_/ /
    \___/
```

---

## 👨‍💻 주니어 개발자 실무 시나리오

### 시나리오 1: 기술 면접

```
면접관: "Java를 선택한 이유가 뭔가요?"

❌ 나쁜 답변:
"학교에서 배웠어요."
"취업이 잘 된다고 들었어요."

✅ 좋은 답변:
"세 가지 이유입니다.
1. 플랫폼 독립성으로 한 번 작성하면 어디서나 실행 가능
2. 대규모 시스템 개발에 적합한 안정성
3. 풍부한 라이브러리와 커뮤니티 지원

특히 OOO 프로젝트를 하면서
멀티스레드 지원 덕분에 동시 처리가
효율적이었던 경험이 있습니다."
```

### 시나리오 2: 기술 선택 회의

```
상황: 신규 프로젝트, 언어 선택 논의

팀장: "이번 프로젝트는 뭘로 할까요?"

선배 A: "Python이 빠르지 않나요?"
선배 B: "Node.js도 좋던데요?"

나(신입): "의견 드려도 될까요?
우리 서비스는 동시 접속자가 많고,
안정성이 중요한 금융 시스템입니다.

Java의 장점:
- 멀티스레드로 동시 처리 최적화
- GC로 메모리 안정성 확보
- Spring 프레임워크로 빠른 개발
- 기존 팀원 대부분이 Java 경험 有

Python은 데이터 분석 파트에서만 활용하면
어떨까요?"

팀장: "좋습니다. Java로 결정!"
```

### 시나리오 3: 버그 리포트

```
고객: "프로그램이 Mac에서 안 돼요!"

❌ 패닉 상황:
"아... Windows에서만 테스트했는데..."
"Mac 버전 따로 만들어야 하나..."

✅ 침착한 대응:
"Java는 플랫폼 독립적이므로
Mac에서도 작동해야 합니다.

체크 포인트:
1. Mac에 JVM(Java) 설치 확인
2. Java 버전 확인 (프로그램 요구사항)
3. 경로 구분자 확인 (Windows: \, Mac: /)

해당 부분 확인 후 해결 가능합니다."
```

---

## ⚠️ 주의사항 및 초보자 팁

### ⚠️ 주의사항

1. **대소문자 구분**
```java
// ❌ 에러
public class helloworld {  // 소문자
}

// ✅ 올바름
public class HelloWorld {  // 대문자 시작 (클래스명 규칙)
}
```

2. **세미콜론 필수**
```java
// ❌ 에러
System.out.println("Hello")  // 세미콜론 없음

// ✅ 올바름
System.out.println("Hello");  // 세미콜론 있음
```

3. **main 메서드 정확히**
```java
// ❌ 실행 안 됨
public static void Main(String[] args) {  // M 대문자

// ✅ 올바름
public static void main(String[] args) {  // m 소문자
```

### 💡 초보자 팁

**팁 1: 에러 메시지 잘 읽기**
```
에러 메시지 예시:
HelloWorld.java:3: error: ';' expected
    System.out.println("Hello")
                               ^
1 error

해석:
- 3번째 줄에 에러
- 세미콜론(;)이 필요함
- ^ 표시된 위치 확인
```

**팁 2: 코드 정렬 습관**
```java
// ❌ 읽기 어려움
public class HelloWorld{public static void main(String[] args){System.out.println("Hello");}}

// ✅ 읽기 쉬움 (들여쓰기)
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}

💡 IntelliJ에서 자동 정렬: Ctrl + Alt + L
```

**팁 3: 주석 활용**
```java
// 한 줄 주석: // 사용

/*
   여러 줄 주석:
   이렇게 여러 줄 작성 가능
*/

public class HelloWorld {
    public static void main(String[] args) {
        // 화면에 메시지 출력
        System.out.println("Hello");
    }
}
```

**팁 4: println vs print**
```java
System.out.print("Hello");    // 줄바꿈 X
System.out.print(" World");   // 같은 줄 출력
// 결과: Hello World

System.out.println("Hello");  // 줄바꿈 O
System.out.println("World");  // 다음 줄 출력
// 결과:
// Hello
// World
```

---

## 💼 실무에서 Java 개발자가 하는 일

### 백엔드 개발자 (Java/Spring)

```
🖥️ 하루 일과 (5년 차 개발자)

09:00 - 10:00  |  데일리 스탠드업 미팅
               |  - 어제 한 일, 오늘 할 일 공유
               |
10:00 - 12:00  |  기능 개발
               |  - 신규 API 개발
               |  - Java + Spring Boot 사용
               |  - 테스트 코드 작성
               |
12:00 - 13:00  |  점심 식사
               |
13:00 - 15:00  |  코드 리뷰
               |  - 동료 코드 리뷰
               |  - 내 코드 리뷰 받기
               |  - 피드백 반영
               |
15:00 - 16:00  |  버그 수정
               |  - 운영 이슈 대응
               |  - 로그 분석
               |
16:00 - 17:00  |  문서 작성
               |  - API 명세서 작성
               |  - README 업데이트
               |
17:00 - 18:00  |  학습 시간
               |  - 새로운 Java 기능 학습
               |  - 기술 블로그 읽기
```

### 필요한 기술 스택

```
🔧 신입 Java 개발자에게 요구되는 것

필수 (Must Have)
├─ Java 기본 문법 완벽 이해
├─ 객체지향 프로그래밍 (OOP)
├─ 컬렉션 프레임워크 (List, Map 등)
├─ 예외 처리
├─ 파일 입출력
├─ Git 사용법
└─ SQL 기초

우대 (Nice to Have)
├─ Spring Framework
├─ JPA (Java Persistence API)
├─ 멀티스레드
├─ 디자인 패턴
└─ AWS 기초

있으면 금상첨화
├─ Kafka, Redis 경험
├─ 대용량 트래픽 처리 경험
└─ 오픈소스 기여 경험
```

---

## ❓ FAQ (자주 묻는 질문)

### Q1. Java만 배우면 Spring도 할 수 있나요?

```
A: Java는 기초, Spring은 응용입니다.

비유:
Java       = 한글 (언어)
Spring     = 작문 (언어로 글쓰기)

학습 순서:
1. Java 기초 (2-3개월)
   - 변수, 조건문, 반복문, 클래스 등

2. Java 중급 (1-2개월)
   - 컬렉션, 예외처리, 파일 I/O

3. Spring 입문 (1-2개월)
   - 이제 시작!

⚠️ Java 없이 Spring 배우면:
"한글 모르고 작문 배우기" = 불가능!
```

### Q2. Java 버전이 많은데 어떤 걸 배워야 하나요?

```
A: Java 8 또는 Java 17을 추천!

Java 버전 역사:
Java 8 (2014)    ← 가장 많이 쓰임! (실무 60%)
Java 11 (2018)   ← 장기 지원(LTS)
Java 17 (2021)   ← 최신 LTS, 추세 증가 중
Java 21 (2023)   ← 최신, 아직 도입 적음

추천:
- 학습용: Java 17 (최신 문법 배우기)
- 실무 준비: Java 8 + Java 17 둘 다
  (면접에서 버전 차이 질문 나옴)

💡 Java 8 문법을 알면 다른 버전도 쉽게 배움!
```

### Q3. Java는 느리다던데 사실인가요?

```
A: 옛날 이야기입니다. 지금은 매우 빠릅니다!

속도 비교 (벤치마크)
C/C++:    100 (가장 빠름)
Java:      95 (거의 비슷)
C#:        90
Node.js:   70
Python:    20 (가장 느림)

Java가 빠른 이유:
1. JIT 컴파일러 (Just-In-Time)
   - 실행 중 최적화

2. 30년간 최적화
   - 수많은 개선

3. 멀티코어 활용
   - 멀티스레드 지원

실무 사례:
"Netflix는 Java로 2억 사용자 서비스
성능 문제 없음!" - Netflix 기술 블로그
```

### Q4. Java는 오래된 언어 아닌가요?

```
A: 오래되었지만 끊임없이 진화 중!

Java 타임라인:
1995년: 탄생 (30년 전)
2014년: Java 8 (현대적 문법 도입)
2024년: Java 21 (최신 기능 추가)

Python도 1991년 (34년 전)
JavaScript도 1995년 (30년 전)
→ 오래되었다 = 안정적이다!

최신 Java 기능들:
- 람다 표현식
- 스트림 API
- 모듈 시스템
- Virtual Threads
- Pattern Matching

💡 "오래되었다"는 "검증되었다"는 의미!
```

### Q5. Java로 AI 개발 가능한가요?

```
A: 가능하지만, Python이 더 좋습니다.

AI/머신러닝 언어 점유율:
Python:   90%  ⭐⭐⭐
R:         5%
Java:      3%
기타:      2%

Java AI 라이브러리:
- Deeplearning4j (딥러닝)
- Weka (머신러닝)
- DL4J (신경망)

추천:
AI가 목표라면 → Python 배우기
백엔드 + AI 조합 → Java(백엔드) + Python(AI)

실무 예시:
"쿠팡은 Java로 서버, Python으로 추천 알고리즘
두 언어 협업!"
```

### Q6. 코딩 테스트는 Java로 해도 되나요?

```
A: 완전히 가능합니다!

언어별 코딩 테스트 선호도:
Python:     40% (문법 간단)
C++:        30% (속도 빠름)
Java:       20% (안정적)
기타:       10%

Java의 장점:
✓ 컬렉션 프레임워크 강력 (ArrayList, HashMap)
✓ 대기업 코테는 Java 추천 (카카오, 네이버 등)
✓ 실무와 동일한 언어

Java의 단점:
✗ 코드가 길다 (타입 선언)
✗ 입력 받기가 복잡

결론:
취업 목표 기업의 주력 언어로 선택!
```

### Q7. 처음부터 끝까지 혼자 웹사이트 만들 수 있나요?

```
A: Java만으로는 어렵습니다. 협업이 필요해요!

웹사이트 구성:
┌─────────────────────────┐
│   프론트엔드 (화면)       │  → HTML, CSS, JavaScript
│   - 사용자가 보는 화면    │
└─────────────────────────┘
            ↕ (통신)
┌─────────────────────────┐
│   백엔드 (서버)          │  → Java (여기가 당신!)
│   - 데이터 처리, 비즈니스 │
└─────────────────────────┘
            ↕
┌─────────────────────────┐
│   데이터베이스           │  → MySQL, PostgreSQL
│   - 데이터 저장          │
└─────────────────────────┘

혼자 다 하려면:
Java (백엔드) + JavaScript (프론트) + SQL (DB)
→ 풀스택 개발자 (시간 오래 걸림)

추천:
백엔드(Java)에 집중 → 취업 후 프론트 배우기
```

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. Java란 무엇이며, 다른 언어와 구별되는 가장 큰 특징은 무엇인가요?</strong></summary>

**모범 답안 포인트**
- Java의 정의: 객체지향 프로그래밍 언어
- 핵심 특징: 플랫폼 독립성 (Write Once, Run Anywhere)
- JVM의 역할: 바이트코드를 각 OS에 맞게 실행

**예시 답변**
> "Java는 객체지향 프로그래밍 언어로, 가장 큰 특징은 '플랫폼 독립성'입니다. Java 코드는 바이트코드로 컴파일되어 JVM이 설치된 모든 운영체제에서 동일하게 실행됩니다. 이를 통해 한 번 작성한 코드를 Windows, Mac, Linux 등 어디서나 수정 없이 실행할 수 있습니다."

**꼬리 질문**
- Q: JVM이 정확히 무엇인가요?
- A: Java Virtual Machine으로, Java 바이트코드를 해당 OS의 기계어로 번역하여 실행하는 가상 머신입니다.

**실무 연관**
- 크로스 플랫폼 서비스 개발 시 개발 비용 대폭 절감
- 예: 카카오뱅크는 Java로 개발하여 다양한 디바이스 지원

</details>

<details>
<summary><strong>2. 객체지향 프로그래밍(OOP)의 4대 특징을 설명해주세요.</strong></summary>

**모범 답안 포인트**
- 캡슐화(Encapsulation): 데이터 은닉 및 보호
- 상속(Inheritance): 코드 재사용성
- 다형성(Polymorphism): 같은 인터페이스, 다른 구현
- 추상화(Abstraction): 핵심 기능만 노출

**예시 답변**
> "OOP의 4대 특징은 캡슐화, 상속, 다형성, 추상화입니다. 캡슐화는 데이터를 private으로 보호하고 getter/setter로 접근을 제어합니다. 상속은 부모 클래스의 기능을 자식 클래스가 물려받아 재사용합니다. 다형성은 같은 메서드 호출이 객체에 따라 다르게 동작하는 것입니다. 추상화는 복잡한 내부 구현을 숨기고 필요한 기능만 제공합니다."

**꼬리 질문**
- Q: 캡슐화의 실무적 장점은?
- A: 데이터 무결성 보장, 유지보수 용이, 보안 강화

**실무 연관**
- 대규모 프로젝트에서 코드 재사용성 및 유지보수성 향상
- 팀 협업 시 모듈화를 통한 개발 효율 증대

</details>

<details>
<summary><strong>3. Garbage Collection(GC)이 무엇이며, 장단점을 설명해주세요.</strong></summary>

**모범 답안 포인트**
- 정의: 사용하지 않는 메모리를 자동으로 회수하는 기능
- 장점: 메모리 누수 방지, 개발자 부담 감소
- 단점: 성능 오버헤드, GC 실행 시 일시 정지(Stop-The-World)

**예시 답변**
> "Garbage Collection은 JVM이 더 이상 참조되지 않는 객체를 자동으로 메모리에서 제거하는 기능입니다. 장점은 개발자가 직접 메모리 관리를 하지 않아도 되어 메모리 누수 버그가 대폭 감소한다는 점입니다. 단점은 GC 실행 시 애플리케이션이 일시 정지(Stop-The-World)될 수 있어 성능에 영향을 줄 수 있습니다."

**꼬리 질문**
- Q: GC의 성능 문제를 어떻게 개선할 수 있나요?
- A: GC 튜닝(힙 크기 조정, GC 알고리즘 선택), 객체 생성 최소화 등

**실무 연관**
- 대용량 트래픽 처리 시 GC 튜닝은 필수
- 예: 쿠팡은 GC 최적화로 응답 시간 30% 단축

</details>

<details>
<summary><strong>4. Java와 JavaScript의 차이점은 무엇인가요?</strong></summary>

**모범 답안 포인트**
- 이름만 비슷, 완전히 다른 언어
- Java: 백엔드, 서버 사이드, 컴파일 언어
- JavaScript: 프론트엔드, 클라이언트 사이드, 인터프리터 언어
- 용도 및 실행 환경 차이

**예시 답변**
> "Java와 JavaScript는 이름만 비슷할 뿐 완전히 다른 언어입니다. Java는 주로 백엔드 서버 개발에 사용되며 컴파일 언어로 JVM에서 실행됩니다. JavaScript는 주로 웹 브라우저에서 실행되는 프론트엔드 언어입니다. 비유하자면 '인도'와 '인도네시아'처럼 이름만 비슷한 별개의 언어입니다."

**꼬리 질문**
- Q: 둘 다 배워야 하나요?
- A: 풀스택 개발자를 목표로 한다면 둘 다 필요하지만, 백엔드 전문이라면 Java에 집중하는 것이 효율적입니다.

**실무 연관**
- 웹 개발 시 Java(백엔드) + JavaScript(프론트엔드) 조합이 일반적
- RESTful API로 두 언어 간 통신

</details>

<details>
<summary><strong>5. JDK, JRE, JVM의 차이를 설명해주세요.</strong></summary>

**모범 답안 포인트**
- JVM: Java 실행 환경 (가상 머신)
- JRE: JVM + 표준 라이브러리 (실행만 가능)
- JDK: JRE + 개발 도구 (컴파일러 등)

**예시 답변**
> "JVM은 Java Virtual Machine으로 바이트코드를 실행하는 가상 머신입니다. JRE는 Java Runtime Environment로 JVM과 표준 라이브러리를 포함해 Java 프로그램을 실행만 할 수 있습니다. JDK는 Java Development Kit로 JRE에 컴파일러(javac) 등 개발 도구를 추가한 것입니다. 개발자는 JDK를 설치하고, 일반 사용자는 JRE만 설치하면 됩니다."

**꼬리 질문**
- Q: 개발 PC에는 무엇을 설치해야 하나요?
- A: 개발을 위해서는 JDK를 설치해야 합니다.

**실무 연관**
- 개발 환경 구축 시 JDK 버전 선택 중요 (Java 8, 11, 17 등)
- 프로덕션 서버에는 경량화된 JRE 사용 가능

</details>

<details>
<summary><strong>6. Java의 'Write Once, Run Anywhere'를 실무 예시로 설명해주세요.</strong></summary>

**모범 답안 포인트**
- 한 번 작성한 코드가 모든 플랫폼에서 실행
- 바이트코드 + JVM 조합으로 가능
- 실무 효과: 개발 비용 및 시간 절감

**예시 답변**
> "'Write Once, Run Anywhere'는 한 번 작성한 Java 코드가 Windows, Mac, Linux 등 모든 플랫폼에서 수정 없이 실행된다는 의미입니다. 예를 들어 카카오뱅크는 Java로 백엔드를 개발하여 Android, iOS, 웹 등 다양한 클라이언트를 지원합니다. 플랫폼별로 코드를 따로 개발할 필요 없이 하나의 Java 서버로 모든 요청을 처리하여 개발 비용을 70% 절감했습니다."

**꼬리 질문**
- Q: 정말 아무 수정 없이 모든 OS에서 실행되나요?
- A: 대부분 그렇지만, 파일 경로 구분자(Windows: \, Unix: /) 등 일부 OS 특화 기능은 주의가 필요합니다.

**실무 연관**
- 멀티 플랫폼 서비스 개발 시 필수 장점
- CI/CD 파이프라인에서 빌드 한 번으로 모든 서버 배포 가능

</details>

<details>
<summary><strong>7. Java를 선택해야 하는 실무적인 이유 3가지를 말씀해주세요.</strong></summary>

**모범 답안 포인트**
- 안정성: 30년 검증, 대규모 시스템 적합
- 생태계: 풍부한 라이브러리 및 프레임워크 (Spring 등)
- 인력 수급: 개발자 인구가 많아 협업 용이

**예시 답변**
> "Java를 선택해야 하는 이유는 첫째, 30년간 검증된 안정성으로 금융권 등 대규모 시스템에 적합합니다. 둘째, Spring, Hibernate 등 성숙한 프레임워크와 방대한 라이브러리 생태계로 빠른 개발이 가능합니다. 셋째, Java 개발자 인력 풀이 크고 커뮤니티가 활발하여 문제 해결이 쉽고 팀 협업이 원활합니다."

**꼬리 질문**
- Q: Java의 단점은 없나요?
- A: 코드가 상대적으로 장황하고, 초기 학습 곡선이 있으며, Python 등에 비해 문법이 복잡할 수 있습니다.

**실무 연관**
- 신규 프로젝트 기술 스택 선정 시 고려 사항
- 레거시 시스템 유지보수 시 Java 지식 필수

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. Java의 메모리 구조(Stack, Heap, Method Area)를 설명하고, 각각 어떤 데이터가 저장되는지 말씀해주세요.</strong></summary>

**모범 답안 포인트**
- Stack: 지역 변수, 메서드 호출 정보 (스레드별 독립)
- Heap: 객체 인스턴스, 배열 (GC 대상)
- Method Area: 클래스 정보, static 변수, 상수

**예시 답변**
> "Java 메모리는 크게 Stack, Heap, Method Area로 구성됩니다. Stack은 각 스레드마다 독립적으로 생성되며 지역 변수와 메서드 호출 정보를 저장합니다. Heap은 모든 스레드가 공유하며 new로 생성한 객체와 배열이 저장되고 GC의 대상입니다. Method Area는 클래스 메타데이터, static 변수, 상수 풀을 저장합니다. 예를 들어 `String str = new String('hello')`에서 참조 변수 str은 Stack에, 실제 String 객체는 Heap에 저장됩니다."

**실무 예시**
```java
public class MemoryExample {
    static int staticVar = 100;  // Method Area

    public void method() {
        int localVar = 10;  // Stack
        String obj = new String("test");  // obj는 Stack, 객체는 Heap
    }
}
```

**꼬리 질문**
- Q: Stack Overflow와 OutOfMemoryError의 차이는?
- A: Stack Overflow는 재귀 호출 등으로 Stack 메모리 초과, OutOfMemoryError는 주로 Heap 메모리 부족입니다.

**실무 연관**
- 메모리 누수 디버깅 시 필수 지식
- 성능 튜닝: Heap 크기 조정 (-Xms, -Xmx 옵션)

</details>

<details>
<summary><strong>2. Java 8의 주요 기능 변화와 실무 활용 예시를 설명해주세요.</strong></summary>

**모범 답안 포인트**
- Lambda 표현식: 함수형 프로그래밍 지원
- Stream API: 컬렉션 처리 간소화
- Optional: NPE 방지
- 날짜/시간 API: LocalDate, LocalDateTime

**예시 답변**
> "Java 8은 혁신적인 버전으로, Lambda 표현식과 Stream API를 도입해 함수형 프로그래밍을 지원합니다. Lambda는 익명 함수를 간결하게 표현하고, Stream API는 컬렉션을 선언적으로 처리할 수 있게 합니다. Optional은 null 안전성을 높이고, 새로운 날짜/시간 API는 기존 Date의 문제를 해결합니다. 실무에서는 Stream으로 대량 데이터 필터링·변환·집계를 간결하게 처리합니다."

**실무 예시**
```java
// Java 8 이전
List<String> result = new ArrayList<>();
for (User user : users) {
    if (user.getAge() >= 20) {
        result.add(user.getName());
    }
}

// Java 8 이후 (Stream + Lambda)
List<String> result = users.stream()
    .filter(user -> user.getAge() >= 20)
    .map(User::getName)
    .collect(Collectors.toList());
```

**꼬리 질문**
- Q: Stream의 지연 연산(Lazy Evaluation)이란?
- A: 중간 연산은 실행을 지연하고, 최종 연산 호출 시 한꺼번에 처리하여 성능을 최적화합니다.

**실무 연관**
- 코드 가독성 및 유지보수성 향상
- 병렬 처리(parallelStream)로 성능 개선

</details>

<details>
<summary><strong>3. 대용량 트래픽 처리 시 Java 애플리케이션의 성능 최적화 방법을 설명해주세요.</strong></summary>

**모범 답안 포인트**
- GC 튜닝: 적절한 GC 알고리즘 선택 (G1GC, ZGC 등)
- 커넥션 풀 관리: DB, HTTP 커넥션 재사용
- 캐싱 전략: Redis, 로컬 캐시 활용
- 비동기 처리: CompletableFuture, 메시지 큐

**예시 답변**
> "대용량 트래픽 처리를 위한 Java 최적화는 여러 방향에서 접근합니다. 첫째, GC 튜닝으로 힙 크기를 적절히 조정하고 G1GC나 ZGC 같은 저지연 GC를 사용합니다. 둘째, DB 커넥션 풀(HikariCP)과 HTTP 클라이언트 풀을 적절히 설정해 커넥션 재사용을 극대화합니다. 셋째, 자주 조회하는 데이터는 Redis나 Caffeine으로 캐싱합니다. 넷째, 동기 처리 대신 CompletableFuture나 Kafka로 비동기 처리하여 응답 시간을 단축합니다."

**실무 예시**
```java
// GC 옵션 예시
-Xms4g -Xmx4g -XX:+UseG1GC -XX:MaxGCPauseMillis=200

// 캐싱 예시
@Cacheable(value = "users", key = "#id")
public User getUser(Long id) {
    return userRepository.findById(id);
}

// 비동기 처리
CompletableFuture.supplyAsync(() -> fetchData())
    .thenApply(data -> process(data))
    .thenAccept(result -> save(result));
```

**꼬리 질문**
- Q: GC 알고리즘별 차이는?
- A: Serial GC(단일 스레드), Parallel GC(멀티 스레드, 처리량 중시), G1GC(저지연, 대용량 힙), ZGC(매우 낮은 지연)

**실무 연관**
- 쿠팡: GC 최적화로 99.9 백분위수 응답 시간 50% 단축
- 네이버: 캐싱 전략으로 DB 부하 80% 감소

</details>

<details>
<summary><strong>4. Spring Framework 없이 순수 Java로 웹 애플리케이션을 개발할 때의 어려움과 Spring의 장점을 설명해주세요.</strong></summary>

**모범 답안 포인트**
- 순수 Java의 어려움: Servlet 설정, 의존성 관리, 보일러플레이트 코드
- Spring의 장점: DI/IoC, AOP, 트랜잭션 관리 자동화
- 생산성 향상: Spring Boot의 Auto Configuration

**예시 답변**
> "순수 Java로 웹 개발 시 Servlet 설정, 의존성 주입, 트랜잭션 관리 등을 모두 수동으로 처리해야 합니다. 예를 들어 객체 생성·소멸을 개발자가 직접 관리하고, DB 트랜잭션 시작·커밋·롤백을 명시적으로 작성해야 합니다. Spring Framework는 DI/IoC로 객체 생명주기를 자동 관리하고, AOP로 로깅·보안·트랜잭션을 선언적으로 처리하며, Spring Boot는 Auto Configuration으로 설정을 최소화합니다. 이를 통해 비즈니스 로직에 집중할 수 있습니다."

**실무 예시**
```java
// 순수 Java (복잡)
Connection conn = null;
try {
    conn = DriverManager.getConnection(url, user, password);
    conn.setAutoCommit(false);
    // ... 비즈니스 로직
    conn.commit();
} catch (SQLException e) {
    if (conn != null) conn.rollback();
} finally {
    if (conn != null) conn.close();
}

// Spring (간결)
@Transactional
public void businessLogic() {
    // ... 비즈니스 로직만 작성
    // 트랜잭션, 커넥션 관리는 Spring이 자동 처리
}
```

**꼬리 질문**
- Q: DI(Dependency Injection)의 장점은?
- A: 결합도 감소, 테스트 용이성, 코드 재사용성 향상

**실무 연관**
- 국내 대부분의 Java 백엔드는 Spring 기반
- Spring Boot로 개발 속도 3배 향상

</details>

<details>
<summary><strong>5. 멀티스레드 환경에서 발생할 수 있는 문제와 해결 방법을 실무 예시로 설명해주세요.</strong></summary>

**모범 답안 포인트**
- 문제: Race Condition, Deadlock, 데이터 불일치
- 해결: synchronized, Lock, Atomic 클래스, ThreadLocal
- 실무 적용: 트랜잭션, 캐시 동기화

**예시 답변**
> "멀티스레드 환경에서는 Race Condition으로 인한 데이터 불일치와 Deadlock 문제가 발생할 수 있습니다. 예를 들어 여러 스레드가 동시에 같은 계좌 잔액을 수정하면 최종 결과가 예상과 다를 수 있습니다. 해결 방법으로 synchronized 키워드로 메서드나 블록을 동기화하거나, ReentrantLock으로 세밀한 제어를 할 수 있습니다. AtomicInteger 같은 Atomic 클래스는 락 없이 원자적 연산을 지원합니다. 스레드별 독립 데이터는 ThreadLocal을 사용합니다."

**실무 예시**
```java
// 문제 상황: Race Condition
private int balance = 1000;
public void withdraw(int amount) {
    if (balance >= amount) {  // 여러 스레드가 동시 체크
        balance -= amount;     // 데이터 불일치 발생
    }
}

// 해결 1: synchronized
public synchronized void withdraw(int amount) {
    if (balance >= amount) {
        balance -= amount;
    }
}

// 해결 2: Atomic 클래스
private AtomicInteger balance = new AtomicInteger(1000);
public void withdraw(int amount) {
    balance.updateAndGet(current ->
        current >= amount ? current - amount : current
    );
}
```

**꼬리 질문**
- Q: synchronized와 Lock의 차이는?
- A: synchronized는 간단하지만 유연성이 낮고, Lock은 타임아웃, 인터럽트 등 세밀한 제어가 가능합니다.

**실무 연관**
- 금융권: 동시성 제어 실패 시 재무 손실
- 쿠팡: 재고 관리 시 동시성 제어로 오버셀링 방지

</details>

---

## 📊 핵심 내용 정리

| 항목 | 내용 |
|------|------|
| **Java 정의** | 객체지향, 플랫폼 독립적 프로그래밍 언어 |
| **핵심 특징** | 플랫폼 독립성, OOP, 자동 메모리 관리, 멀티스레드, 풍부한 API |
| **JVM** | Java 코드를 실행하는 가상 머신 (통역사 역할) |
| **주요 용도** | 백엔드, Android 앱, 금융 시스템, 빅데이터 |
| **대표 기업** | 카카오, 네이버, 쿠팡, 배민, 토스, 삼성, LG |
| **학습 순서** | Java 기초 → Java 중급 → Spring 프레임워크 |
| **취업 전망** | 매우 좋음 (국내 개발자 채용 1위) |

---

## 🔗 관련 기술 스택

Java를 배우면 다음으로 확장 가능:

```
Java 기초
    ↓
┌───────┼───────┐
│       │       │
Spring  Servlet Android
(웹)    (웹)    (앱)
```

---

## 🎯 다음 단계

**다음 장 예고:**
- 📘 02장: 개발 환경 설정
- JDK 설치 방법
- IntelliJ IDEA 설치
- 첫 프로젝트 생성
- Hello World 실행

**지금 당장 해볼 것:**
1. ✅ Java 버전 확인 (명령창에서 `java -version`)
2. ✅ 없다면 JDK 설치 준비
3. ✅ 오늘 배운 내용 노션/블로그 정리

---

## 📚 추가 학습 자료

### 📖 추천 영상
- [생활코딩 - Java 입문](https://opentutorials.org/course/1223)
- [YouTube - Java의 역사 10분 요약](https://youtube.com)

### 📰 읽을거리
- [Oracle 공식 Java 튜토리얼](https://docs.oracle.com/javase/tutorial/)
- [카카오 기술 블로그 - Java 성능 이야기](https://tech.kakao.com)

### 🌐 유용한 사이트
- [Java API 문서](https://docs.oracle.com/en/java/javase/17/docs/api/)
- [Stack Overflow - Java 태그](https://stackoverflow.com/questions/tagged/java)

---

## 🎉 축하합니다!

**Java의 세계에 첫 발을 내디뎠습니다!**

### 학습 완료 체크리스트

**이제 여러분은 다음을 할 수 있습니다:**

#### 📚 개념 이해
- [ ] Java가 무엇인지 명확히 설명할 수 있다
- [ ] "Write Once, Run Anywhere"의 의미를 이해했다
- [ ] JVM의 역할과 동작 원리를 알고 있다
- [ ] 객체지향 프로그래밍(OOP)의 기본 개념을 이해했다
- [ ] Garbage Collection의 장단점을 설명할 수 있다

#### 💻 실습 완료
- [ ] Hello World 프로그램을 작성하고 실행했다
- [ ] 시스템 정보 출력 프로그램을 구현했다
- [ ] Java 코드의 기본 구조를 파악했다
- [ ] 컴파일과 실행 과정을 이해했다

#### 🏢 실무 지식
- [ ] Java가 실무에서 어디에 사용되는지 안다 (백엔드, Android, 금융 등)
- [ ] 주요 기업들의 Java 활용 사례를 알고 있다
- [ ] Java와 다른 언어(Python, JavaScript, C++)의 차이를 이해했다
- [ ] Java를 선택해야 하는 이유를 설명할 수 있다

#### 💼 면접 준비
- [ ] 주니어 개발자 면접 질문 7개를 복습했다
- [ ] 각 질문에 대한 답변 포인트를 정리했다
- [ ] 실무 연관성을 이해했다
- [ ] 꼬리 질문에 대비할 수 있다

### 다음 단계 행동 계획

**지금 바로 실천하세요:**

1. **복습 (오늘 중)**
   - [ ] 5가지 실생활 비유를 자신의 언어로 다시 설명해보기
   - [ ] Hello World 코드를 손으로 직접 타이핑해보기
   - [ ] 면접 질문 중 3개를 선택해 답변 연습하기

2. **정리 (1-2일 내)**
   - [ ] 학습한 내용을 노션/블로그에 정리
   - [ ] 핵심 개념을 마인드맵으로 그려보기
   - [ ] 친구나 가족에게 Java를 설명해보기

3. **심화 (이번 주)**
   - [ ] JDK 설치 준비 (다음 장 예습)
   - [ ] IntelliJ IDEA 다운로드
   - [ ] Java 커뮤니티 가입 (Okky, 생활코딩 등)

4. **장기 목표 (1개월 내)**
   - [ ] Java 기초 전체 과정 완료
   - [ ] 간단한 프로젝트 1개 완성
   - [ ] GitHub에 코드 업로드

### 성취 배지

**여러분이 획득한 성취:**

```
🏆 Java 입문자 배지
   ├─ ✅ Java 개념 이해 완료
   ├─ ✅ 첫 프로그램 작성 성공
   ├─ ✅ 실무 활용 사례 학습
   └─ ✅ 면접 질문 대비 완료

📈 현재 레벨: Lv.1 - Java 초보자
   다음 레벨: Lv.2 - Java 문법 학습자 (02장 완료 시)
```

### 학습 통계

```
📊 01장 학습 완료 현황
─────────────────────────────────────
📖 이론 학습      ████████████████ 100%
💻 실습 완료      ████████████████ 100%
🏢 실무 지식      ████████████████ 100%
💼 면접 준비      ████████████████ 100%
─────────────────────────────────────
   전체 진행률    ████████████████ 100%

🎯 예상 학습 시간: 1-3시간
⏱️ 실제 소요 시간: [     ] 시간

💡 학습 효율성:
   목표 시간 내 완료 시 → 🌟 우수
   +1시간 이내 완료 시 → ⭐ 양호
```

### 동기 부여 메시지

> **"모든 전문가도 처음엔 초보자였습니다."**
>
> 여러분은 방금 Java라는 거대한 세계의 문을 열었습니다.
> 첫 걸음이 가장 중요합니다. 그 첫 걸음을 성공적으로 완료하셨습니다!
>
> 지금 이 순간, 전 세계 수백만 개발자들이 여러분과 같은 Java 코드를 작성하고 있습니다.
> 여러분도 이제 그들과 같은 길을 걷고 있습니다.

### 실무 개발자의 조언

```
💬 5년 차 백엔드 개발자가 신입 개발자 시절을 돌아보며...

"01장을 공부할 때는 Java가 뭔지도 잘 몰랐습니다.
그저 '취업에 유리하다'는 말만 믿고 시작했죠.

하지만 지금 돌아보니, 그때 배운 기본 개념들이
5년이 지난 지금도 매일 쓰이고 있습니다.

특히 'Write Once, Run Anywhere'는 실무에서
정말 강력한 장점입니다. 한 번 작성한 코드가
개발 서버, 스테이징, 운영 서버 모두에서 동일하게 동작하니까요.

여러분이 지금 배운 내용을 절대 가볍게 여기지 마세요.
이것이 바로 여러분의 커리어를 시작하는 초석입니다."

- 네이버 백엔드 개발자
```

### 커뮤니티 참여하기

**혼자 공부하지 마세요! 함께하면 더 멀리 갑니다.**

- 💬 [Okky - Java 게시판](https://okky.kr/articles/java)
- 📺 [생활코딩 Java 커뮤니티](https://opentutorials.org)
- 🐱 [Java 오픈소스 프로젝트](https://github.com/topics/java)
- 📧 [Java User Group Korea](https://www.facebook.com/groups/javausergroup/)

---

**🚀 다음 장에서 만나요!**

[← 이전: 00장 학습 방법](00-효과적인-Java-학습-방법.md) | [📋 목차로](README.md) | [다음: 02장 환경 설정 →](02-개발-환경-설정.md)
