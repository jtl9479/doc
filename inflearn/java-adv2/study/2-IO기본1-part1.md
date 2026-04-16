# 2. I/O 기본1 - Part 1

**출처**: 인프런 - 김영한의 실전 자바 고급 2편
**작성일**: 2026-01-03

> **문서 구성**
> - Part 1: 스트림 개념, 기본 입출력, InputStream/OutputStream
> - Part 2: 파일 입출력 성능 최적화, 버퍼 활용, 면접 질문

---

## 학습 목표

이 챕터를 학습한 후 다음을 할 수 있습니다:
- [ ] 스트림(Stream)의 개념과 단방향 특성을 설명할 수 있다
- [ ] FileInputStream/FileOutputStream을 사용하여 파일 입출력을 수행할 수 있다
- [ ] InputStream/OutputStream 추상화의 장점을 설명할 수 있다
- [ ] 버퍼를 사용한 성능 최적화 방법을 적용할 수 있다
- [ ] BufferedInputStream/BufferedOutputStream의 동작 원리를 이해할 수 있다

## 연관 개념

- **선행 학습 권장**: 1. 문자 인코딩 (byte, 2진수 개념)
- **후속 학습**: 3. IO 기본2, 4. IO 활용
- **관련 챕터**: 5. File, Files

---

## 목차

1. [스트림 시작1 - 기본 개념](#1-스트림-시작1---기본-개념)
2. [스트림 시작2 - byte 배열 활용](#2-스트림-시작2---byte-배열-활용)
3. [InputStream, OutputStream](#3-inputstream-outputstream)
4. [메모리 스트림과 콘솔 스트림](#4-메모리-스트림과-콘솔-스트림)

---

## 1. 스트림 시작1 - 기본 개념

> **TL;DR**
> - 스트림(Stream)은 데이터를 주고받는 단방향 통로
> - 출력 스트림: 자바 → 외부 (파일, 네트워크)
> - 입력 스트림: 외부 → 자바
> - 외부 자원 사용 후 반드시 `close()` 호출 필요

### 핵심 개념

자바 프로세스가 가지고 있는 데이터를 파일에 저장하려면 **스트림(Stream)**을 사용합니다.

```
┌─────────────────┐                        ┌─────────────┐
│                 │     출력 스트림 →      │             │
│  자바 프로세스   │    10010110010010      │  hello.dat  │
│   (A, B, C)     │                        │   (파일)    │
│                 │    10010110010010      │             │
│                 │     ← 입력 스트림      │             │
└─────────────────┘                        └─────────────┘
```

**스트림의 특성:**
- **단방향**: 각 스트림은 한 방향으로만 흐른다
- 출력 스트림: 자바 → 외부 저장소
- 입력 스트림: 외부 저장소 → 자바

### 예제 코드

```java
package io.start;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;

public class StreamStartMain1 {

    public static void main(String[] args) throws IOException {
        // 출력 스트림 - 파일에 데이터 쓰기
        FileOutputStream fos = new FileOutputStream("temp/hello.dat");
        fos.write(65);  // 'A'
        fos.write(66);  // 'B'
        fos.write(67);  // 'C'
        fos.close();

        // 입력 스트림 - 파일에서 데이터 읽기
        FileInputStream fis = new FileInputStream("temp/hello.dat");
        System.out.println(fis.read());  // 65
        System.out.println(fis.read());  // 66
        System.out.println(fis.read());  // 67
        System.out.println(fis.read());  // -1 (EOF)
        fis.close();
    }
}
```

### 실행 결과

```
65
66
67
-1
```

### 주요 메서드 설명

| 메서드 | 설명 |
|--------|------|
| `new FileOutputStream(path)` | 파일 출력 스트림 생성 (파일 없으면 자동 생성) |
| `write(int)` | byte 단위로 데이터 출력 |
| `new FileInputStream(path)` | 파일 입력 스트림 생성 |
| `read()` | byte 단위로 데이터 읽기, EOF시 -1 반환 |
| `close()` | 스트림 자원 해제 (필수!) |

### 주의사항

```
⚠️ 폴더 미리 생성 필요
- FileOutputStream은 파일은 자동 생성하지만 폴더는 만들지 않음
- temp 폴더가 없으면 FileNotFoundException 발생
```

### 파일 append 옵션

```java
// true: 기존 파일 끝에 이어서 쓰기
// false: 기존 파일 덮어쓰기 (기본값)
new FileOutputStream("temp/hello.dat", true);
```

---

## 2. 스트림 시작2 - byte 배열 활용

> **TL;DR**
> - `write(byte[])`: 여러 byte를 한 번에 출력
> - `read(byte[])`: 여러 byte를 한 번에 읽기
> - `readAllBytes()`: 파일 전체를 한 번에 읽기

### byte 배열로 데이터 쓰기/읽기

```java
package io.start;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Arrays;

public class StreamStartMain3 {

    public static void main(String[] args) throws IOException {
        // byte[] 로 한 번에 쓰기
        FileOutputStream fos = new FileOutputStream("temp/hello.dat");
        byte[] input = {65, 66, 67};
        fos.write(input);
        fos.close();

        // byte[] 로 한 번에 읽기
        FileInputStream fis = new FileInputStream("temp/hello.dat");
        byte[] buffer = new byte[10];
        int readCount = fis.read(buffer, 0, 10);
        System.out.println("readCount = " + readCount);  // 3
        System.out.println(Arrays.toString(buffer));     // [65, 66, 67, 0, 0, 0, 0, 0, 0, 0]
        fis.close();
    }
}
```

### read() 메서드 변형

| 메서드 | 설명 |
|--------|------|
| `read()` | 1byte 읽기, EOF시 -1 반환 |
| `read(byte[])` | 배열 크기만큼 읽기 |
| `read(byte[], offset, length)` | offset부터 length만큼 읽기 |
| `readAllBytes()` | 파일 전체 읽기 (Java 9+) |

### 반복문으로 파일 전체 읽기

```java
FileInputStream fis = new FileInputStream("temp/hello.dat");
int data;
while ((data = fis.read()) != -1) {
    System.out.println(data);
}
fis.close();
```

### 모든 데이터 한 번에 읽기

```java
FileInputStream fis = new FileInputStream("temp/hello.dat");
byte[] readBytes = fis.readAllBytes();  // 파일 전체 읽기
System.out.println(Arrays.toString(readBytes));  // [65, 66, 67]
fis.close();
```

### 부분 읽기 vs 전체 읽기

| 방식 | 장점 | 단점 | 사용 케이스 |
|------|------|------|------------|
| `read(byte[], offset, length)` | 메모리 사용량 제어 가능 | 코드 복잡 | 대용량 파일 |
| `readAllBytes()` | 간단한 코드 | 메모리 많이 사용 | 작은 파일 |

```
예시: 100MB 파일 처리
- readAllBytes(): 100MB 메모리 한 번에 사용 → OutOfMemoryError 위험
- read(byte[], 0, 1MB): 1MB씩 처리 → 안전한 메모리 사용
```

### read()가 int를 반환하는 이유

```
Q: byte를 읽는데 왜 int로 반환할까?

A: EOF 표현을 위해!
- byte: -128 ~ 127 (256가지) → 모든 값이 유효한 데이터
- int로 반환하면 0~255 + EOF(-1) 표현 가능
```

---

## 3. InputStream, OutputStream

> **TL;DR**
> - 모든 byte 스트림의 **추상 부모 클래스**
> - 파일, 네트워크, 메모리 등 다양한 대상에 **일관된 방식**으로 입출력
> - 다형성을 활용한 유연한 코드 작성 가능

### 핵심 개념

현대 컴퓨터는 **byte 단위**로 데이터를 주고받습니다. 자바는 다양한 대상(파일, 네트워크, 콘솔)에 일관된 방식으로 데이터를 주고받기 위해 `InputStream`, `OutputStream` 추상 클래스를 제공합니다.

```
┌─────────────────┐
│                 │  byte 출력  ┌──────────────┐
│                 │ ──────────→ │  파일 저장소  │
│                 │  byte 입력  │              │
│                 │ ←────────── └──────────────┘
│                 │
│   자바 프로세스  │  byte 출력  ┌──────────────┐
│                 │ ──────────→ │   네트워크   │
│                 │  byte 입력  │              │
│                 │ ←────────── └──────────────┘
│                 │
│                 │  byte 출력  ┌──────────────┐
│                 │ ──────────→ │    콘솔     │
│                 │  byte 입력  │              │
│                 │ ←────────── └──────────────┘
└─────────────────┘
```

### 클래스 계층 구조

```
         ┌─────────────────┐              ┌─────────────────┐
         │   InputStream   │              │  OutputStream   │
         │    read()       │              │   write(int)    │
         │    read(byte[]) │              │   write(byte[]) │
         │  readAllBytes() │              └────────┬────────┘
         └────────┬────────┘                       │
                  │                                │
    ┌─────────────┼─────────────┐    ┌─────────────┼─────────────┐
    │             │             │    │             │             │
┌───┴───┐   ┌─────┴─────┐   ┌───┴───┐┌───┴───┐   ┌─────┴─────┐   ┌───┴───┐
│ File  │   │ ByteArray │   │Socket ││ File  │   │ ByteArray │   │Socket │
│Input  │   │ Input     │   │Input  ││Output │   │ Output    │   │Output │
│Stream │   │ Stream    │   │Stream ││Stream │   │ Stream    │   │Stream │
└───────┘   └───────────┘   └───────┘└───────┘   └───────────┘   └───────┘
```

### InputStream 주요 메서드

| 메서드 | 설명 |
|--------|------|
| `read()` | 1byte 읽기 |
| `read(byte[])` | byte 배열로 읽기 |
| `readAllBytes()` | 전체 읽기 |
| `close()` | 스트림 닫기 |

### OutputStream 주요 메서드

| 메서드 | 설명 |
|--------|------|
| `write(int)` | 1byte 쓰기 |
| `write(byte[])` | byte 배열 쓰기 |
| `flush()` | 버퍼 강제 출력 |
| `close()` | 스트림 닫기 |

### 왜 인터페이스가 아니라 추상 클래스인가?

> **참고**
> `InputStream`, `OutputStream`은 **추상 클래스**입니다.
> 자바 1.0부터 제공되었으며, 일부 작동하는 코드도 들어있기 때문에 인터페이스가 아니라 추상 클래스로 제공됩니다.

### 추상화의 장점

1. **일관성**: 모든 입출력에 동일한 인터페이스 사용
2. **유연성**: 대상이 바뀌어도 코드 변경 최소화
3. **확장성**: 새로운 스트림 쉽게 추가 가능
4. **재사용성**: 다양한 스트림 조합 가능

```java
// 예: 출력 대상만 바꿔서 사용
void writeData(OutputStream os, byte[] data) throws IOException {
    os.write(data);
}

// 파일에 쓰기
writeData(new FileOutputStream("file.dat"), data);

// 네트워크로 전송
writeData(socket.getOutputStream(), data);
```

---

## 4. 메모리 스트림과 콘솔 스트림

> **TL;DR**
> - `ByteArrayOutputStream/InputStream`: 메모리에 데이터 쓰기/읽기
> - `System.out`: PrintStream (OutputStream 상속)
> - 모두 동일한 OutputStream/InputStream 인터페이스 사용

### 메모리 스트림

```java
package io.start;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.Arrays;

public class ByteArrayStreamMain {

    public static void main(String[] args) throws IOException {
        byte[] input = {1, 2, 3};

        // 메모리에 쓰기
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        baos.write(input);

        // 메모리에서 읽기
        ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
        byte[] bytes = bais.readAllBytes();
        System.out.println(Arrays.toString(bytes));  // [1, 2, 3]
    }
}
```

**용도:**
- 스트림 테스트
- 스트림 데이터 확인
- 실제로는 컬렉션/배열 사용이 더 일반적

### 콘솔 스트림

```java
package io.start;

import java.io.IOException;
import java.io.PrintStream;
import static java.nio.charset.StandardCharsets.UTF_8;

public class PrintStreamMain {

    public static void main(String[] args) throws IOException {
        PrintStream printStream = System.out;  // System.out은 PrintStream

        // OutputStream 부모의 기능
        byte[] bytes = "Hello!\n".getBytes(UTF_8);
        printStream.write(bytes);

        // PrintStream 자체 기능
        printStream.println("Print!");
    }
}
```

**실행 결과:**
```
Hello!
Print!
```

### System.out의 정체

```java
public final class System {
    public static final PrintStream out;  // PrintStream은 OutputStream 상속
    ...
}
```

- `System.out`은 **PrintStream** 타입
- PrintStream은 **OutputStream**을 상속
- 따라서 `write(byte[])`, `println()` 모두 사용 가능

---

## 정리

### 스트림 기본 개념

| 개념 | 설명 |
|------|------|
| 스트림 | 데이터를 주고받는 단방향 통로 |
| 출력 스트림 | 자바 → 외부 |
| 입력 스트림 | 외부 → 자바 |
| EOF | End of File, read()가 -1 반환 |

### 주요 클래스

| 클래스 | 용도 |
|--------|------|
| FileInputStream | 파일에서 읽기 |
| FileOutputStream | 파일에 쓰기 |
| ByteArrayInputStream | 메모리에서 읽기 |
| ByteArrayOutputStream | 메모리에 쓰기 |
| PrintStream | 콘솔 출력 (System.out) |

### 핵심 포인트

1. **외부 자원은 반드시 close()** - GC가 처리하지 않음
2. **read()는 EOF시 -1 반환** - 반복문 종료 조건으로 활용
3. **InputStream/OutputStream 추상화** - 다형성으로 유연한 코드 작성
4. **byte 단위 처리** - 모든 데이터는 byte로 주고받음

---

## 네비게이션

- [이전: 1. 문자 인코딩](./1-문자인코딩-part2.md)
- [다음: Part 2 - 파일 입출력 성능 최적화](./2-IO기본1-part2.md)
