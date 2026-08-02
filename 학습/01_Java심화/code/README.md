# Java 심화 학습 코드

Effective Java 예제·실습 코드를 Step별로 실행·검증하는 Gradle 프로젝트.

## 디렉터리 구조

```
code/
├── build.gradle.kts
├── settings.gradle.kts
└── src/
    ├── main/java/
    │   └── stepNN/itemNN/ClassName.java
    └── test/java/
        └── stepNN/itemNN/ClassNameTest.java
```

## 실행 방법

### 1) Gradle Wrapper 생성 (최초 1회)

```bash
# Gradle이 전역 설치되어 있다면
gradle wrapper --gradle-version 8.10

# 또는 IntelliJ IDEA에서 이 폴더를 "Open"으로 열면 자동 생성
```

### 2) 단일 파일 즉시 실행 (JDK 11+)

```bash
java src/main/java/step01/item01/StaticFactoryExample.java
```

### 3) Gradle로 실행

```bash
./gradlew run -PmainClass=step01.item01.StaticFactoryExample
./gradlew test
```

## 네이밍 규칙

- 패키지: `stepNN.itemNN` (예: `step01.item01`)
- 클래스: Item 주제를 드러내는 이름 (예: `StaticFactoryExample`, `BuilderPattern`)
- 테스트: `ClassNameTest` (JUnit 5)
