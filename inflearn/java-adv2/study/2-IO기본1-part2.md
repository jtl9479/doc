# 2. I/O 기본1 - Part 2

**출처**: 인프런 - 김영한의 실전 자바 고급 2편
**작성일**: 2026-01-03

> **문서 구성**
> - Part 1: 스트림 개념, 기본 입출력, InputStream/OutputStream
> - Part 2: 파일 입출력 성능 최적화, 버퍼 활용, 면접 질문

---

## 목차

1. [파일 입출력과 성능 최적화1 - 하나씩 쓰기](#1-파일-입출력과-성능-최적화1---하나씩-쓰기)
2. [파일 입출력과 성능 최적화2 - 버퍼 활용](#2-파일-입출력과-성능-최적화2---버퍼-활용)
3. [파일 입출력과 성능 최적화3 - BufferedOutputStream](#3-파일-입출력과-성능-최적화3---bufferedoutputstream)
4. [파일 입출력과 성능 최적화4 - BufferedInputStream](#4-파일-입출력과-성능-최적화4---bufferedinputstream)
5. [파일 입출력과 성능 최적화5 - 한 번에 쓰기](#5-파일-입출력과-성능-최적화5---한-번에-쓰기)
6. [면접 질문](#면접-질문)

---

## 1. 파일 입출력과 성능 최적화1 - 하나씩 쓰기

> **TL;DR**
> - 1byte씩 디스크에 쓰면 **매우 느림** (10MB: 약 14초)
> - 매번 OS 시스템 콜 호출 → 디스크 접근 오버헤드 발생
> - 실무에서 절대 사용하면 안 되는 방식

### 핵심 개념

파일에 1byte씩 쓰면 어떤 성능 문제가 발생하는지 알아봅니다.

### 테스트 설정

```java
package io.buffered;

public class BufferedConst {
    public static final String FILE_NAME = "temp/buffered.dat";
    public static final int FILE_SIZE = 10 * 1024 * 1024;  // 10MB
    public static final int BUFFER_SIZE = 8192;            // 8KB
}
```

### 예제 코드 - V1 (하나씩 쓰기)

```java
package io.buffered;

import java.io.FileOutputStream;
import java.io.IOException;
import static io.buffered.BufferedConst.*;

public class CreateFileV1 {

    public static void main(String[] args) throws IOException {
        FileOutputStream fos = new FileOutputStream(FILE_NAME);
        long startTime = System.currentTimeMillis();

        for (int i = 0; i < FILE_SIZE; i++) {
            fos.write(1);  // 1byte씩 쓰기 (1000만 번!)
        }
        fos.close();

        long endTime = System.currentTimeMillis();
        System.out.println("File created: " + FILE_NAME);
        System.out.println("File size: " + FILE_SIZE / 1024 / 1024 + "MB");
        System.out.println("Time taken: " + (endTime - startTime) + "ms");
    }
}
```

### 실행 결과

```
File created: temp/buffered.dat
File size: 10MB
Time taken: 14197ms  (약 14초!)
```

### 왜 느릴까?

```
┌─────────────────────────────────────────────────────────────────┐
│                       1byte 쓰기 과정                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  자바 프로세스                         OS                        │
│  ┌─────────────┐                    ┌─────────────┐              │
│  │ write(1)    │ ───시스템 콜───→  │ 커널 버퍼   │──→ 디스크    │
│  │ write(1)    │ ───시스템 콜───→  │ 커널 버퍼   │──→ 디스크    │
│  │ write(1)    │ ───시스템 콜───→  │ 커널 버퍼   │──→ 디스크    │
│  │    ...      │       ...         │    ...      │    ...       │
│  │ (1000만번!) │                    │             │              │
│  └─────────────┘                    └─────────────┘              │
│                                                                  │
│  ⚠️ 문제점: 1byte마다 OS 시스템 콜 호출!                         │
│     → 컨텍스트 스위칭 오버헤드                                    │
│     → 디스크 접근 오버헤드                                       │
└─────────────────────────────────────────────────────────────────┘
```

### 주요 포인트

1. **시스템 콜 오버헤드**: 매번 사용자 모드 → 커널 모드 전환
2. **디스크 접근 오버헤드**: 디스크는 RAM보다 수천~수만 배 느림
3. **비효율적인 자원 사용**: CPU, 메모리, 디스크 모두 비효율적 사용

> **참고**
> 실제로 OS나 하드웨어 레벨에서도 어느 정도의 최적화가 이루어지기 때문에 1byte씩 쓴다고 해서 진짜 디스크에 1byte씩 쓰이는 것은 아닙니다. 하지만 **시스템 콜 호출 자체의 오버헤드**가 크기 때문에 성능이 매우 느려집니다.

### 읽기도 마찬가지

```java
// ReadFileV1 - 1byte씩 읽기
FileInputStream fis = new FileInputStream(FILE_NAME);
int data;
while ((data = fis.read()) != -1) {
    fileSize++;
}
// 결과: 약 14초
```

---

## 2. 파일 입출력과 성능 최적화2 - 버퍼 활용

> **TL;DR**
> - **버퍼(buffer)**: 데이터를 모아두는 임시 저장 공간
> - byte[] 배열을 버퍼로 사용하여 **한 번에 여러 byte 전송**
> - 성능 **1000배 향상** (14초 → 14ms)

### 핵심 개념

**버퍼(buffer)**는 데이터를 일시적으로 모아두었다가 한 번에 전송하는 기법입니다.

```
┌─────────────────────────────────────────────────────────────────┐
│                       버퍼 활용 방식                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  자바 프로세스                         OS                        │
│  ┌─────────────┐                    ┌─────────────┐              │
│  │ [버퍼 8KB]  │ ───시스템 콜───→  │ 커널 버퍼   │──→ 디스크    │
│  │  모아서     │     (1번만!)       │             │              │
│  │  한 번에!   │                    │             │              │
│  └─────────────┘                    └─────────────┘              │
│                                                                  │
│  ✅ 개선점: 8KB마다 OS 시스템 콜 1번!                            │
│     → 시스템 콜 횟수 8000배 감소                                 │
│     → 디스크 접근 효율 극대화                                    │
└─────────────────────────────────────────────────────────────────┘
```

### 예제 코드 - V2 (버퍼 활용)

```java
package io.buffered;

import java.io.FileOutputStream;
import java.io.IOException;
import static io.buffered.BufferedConst.*;

public class CreateFileV2 {

    public static void main(String[] args) throws IOException {
        FileOutputStream fos = new FileOutputStream(FILE_NAME);
        long startTime = System.currentTimeMillis();

        byte[] buffer = new byte[BUFFER_SIZE];  // 8KB 버퍼
        int bufferIndex = 0;

        for (int i = 0; i < FILE_SIZE; i++) {
            buffer[bufferIndex++] = 1;

            // 버퍼가 가득 차면 쓰고, 버퍼를 비운다.
            if (bufferIndex == BUFFER_SIZE) {
                fos.write(buffer);
                bufferIndex = 0;
            }
        }

        // 끝 부분에 남아있는 데이터 쓰기
        if (bufferIndex > 0) {
            fos.write(buffer, 0, bufferIndex);
        }

        fos.close();

        long endTime = System.currentTimeMillis();
        System.out.println("File created: " + FILE_NAME);
        System.out.println("File size: " + FILE_SIZE / 1024 / 1024 + "MB");
        System.out.println("Time taken: " + (endTime - startTime) + "ms");
    }
}
```

### 실행 결과

```
File created: temp/buffered.dat
File size: 10MB
Time taken: 14ms  (1000배 빨라짐!)
```

### 버퍼 읽기

```java
// ReadFileV2 - 버퍼로 읽기
FileInputStream fis = new FileInputStream(FILE_NAME);
byte[] buffer = new byte[BUFFER_SIZE];
int size;
while ((size = fis.read(buffer)) != -1) {
    fileSize += size;
}
// 결과: 약 10ms
```

### 시스템 콜 횟수 비교

| 방식 | 시스템 콜 횟수 (10MB) | 소요 시간 |
|------|---------------------|----------|
| V1 (1byte씩) | 10,485,760번 | 14,197ms |
| V2 (8KB 버퍼) | 1,280번 | 14ms |

### 버퍼 크기 권장

| 버퍼 크기 | 특징 |
|----------|------|
| 512byte ~ 2KB | 너무 작음, 효과 미미 |
| **4KB ~ 8KB** | **권장 크기** (OS 블록 크기와 유사) |
| 16KB ~ 64KB | 효과 있지만 메모리 사용 증가 |
| 1MB 이상 | 메모리 낭비, 효과 미미 |

### 주요 포인트

1. **버퍼 크기는 4KB~8KB가 적정** (OS 디스크 블록 크기)
2. **나머지 데이터 처리 필수**: 파일 끝에 버퍼가 가득 차지 않을 수 있음
3. **메모리와 성능의 트레이드오프**: 너무 큰 버퍼는 메모리 낭비

---

## 3. 파일 입출력과 성능 최적화3 - BufferedOutputStream

> **TL;DR**
> - Java가 제공하는 **버퍼 기능 내장 스트림**
> - write(1byte)를 호출해도 내부 버퍼에 모았다가 한 번에 전송
> - 단, **synchronized 오버헤드**로 직접 버퍼보다 약간 느림

### 핵심 개념

`BufferedOutputStream`은 스트림을 감싸서(Decorator 패턴) 버퍼 기능을 추가합니다.

```
┌─────────────────────────────────────────────────────────────────┐
│                    BufferedOutputStream 구조                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────┐                  │
│  │           BufferedOutputStream             │                  │
│  │  ┌─────────────────────────────────────┐  │                  │
│  │  │         내부 버퍼 (8KB)              │  │                  │
│  │  │  [1][1][1][1][1][1][1][1]...        │  │                  │
│  │  └─────────────────────────────────────┘  │                  │
│  │              │                             │                  │
│  │              │ (버퍼가 가득 차면)          │                  │
│  │              ▼                             │                  │
│  │  ┌─────────────────────────────────────┐  │                  │
│  │  │       FileOutputStream              │  │                  │
│  │  │       (실제 파일 쓰기)               │  │                  │
│  │  └─────────────────────────────────────┘  │                  │
│  └───────────────────────────────────────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 예제 코드 - V3 (BufferedOutputStream)

```java
package io.buffered;

import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import static io.buffered.BufferedConst.*;

public class CreateFileV3 {

    public static void main(String[] args) throws IOException {
        FileOutputStream fos = new FileOutputStream(FILE_NAME);
        BufferedOutputStream bos = new BufferedOutputStream(fos, BUFFER_SIZE);
        long startTime = System.currentTimeMillis();

        for (int i = 0; i < FILE_SIZE; i++) {
            bos.write(1);  // 1byte씩 호출해도 내부 버퍼에 모음
        }
        bos.close();  // close()시 flush() 자동 호출

        long endTime = System.currentTimeMillis();
        System.out.println("File created: " + FILE_NAME);
        System.out.println("File size: " + FILE_SIZE / 1024 / 1024 + "MB");
        System.out.println("Time taken: " + (endTime - startTime) + "ms");
    }
}
```

### 실행 결과

```
File created: temp/buffered.dat
File size: 10MB
Time taken: 102ms
```

### 성능 비교

| 버전 | 방식 | 소요 시간 |
|------|------|----------|
| V1 | 1byte씩 직접 | 14,197ms |
| V2 | byte[] 버퍼 직접 관리 | 14ms |
| **V3** | **BufferedOutputStream** | **102ms** |

### 왜 V2보다 느릴까?

```java
// BufferedOutputStream.write() 내부 코드
public synchronized void write(int b) throws IOException {
    if (count >= buf.length) {
        flushBuffer();
    }
    buf[count++] = (byte)b;
}
```

**synchronized 키워드!**
- 멀티스레드 환경에서의 안전성을 위해 동기화
- 매번 락 획득/해제 오버헤드 발생
- 단일 스레드에서는 불필요한 오버헤드

### flush()와 close()

| 메서드 | 설명 |
|--------|------|
| `flush()` | 버퍼에 남은 데이터를 즉시 출력 |
| `close()` | flush() 호출 후 스트림 닫기 |

```java
bos.write(1);   // 버퍼에만 저장
bos.flush();    // 버퍼 → 파일로 강제 출력
bos.close();    // flush() + 자원 해제
```

### 주요 포인트

1. **코드가 간결해짐**: 버퍼 관리를 BufferedOutputStream이 담당
2. **close()는 flush() 포함**: 자원 해제 전 버퍼 비우기 보장
3. **synchronized 오버헤드**: 단일 스레드라면 직접 버퍼가 더 빠름

---

## 4. 파일 입출력과 성능 최적화4 - BufferedInputStream

> **TL;DR**
> - 읽기 버전의 버퍼 스트림
> - 내부적으로 데이터를 미리 읽어서 버퍼에 보관
> - read()마다 시스템 콜 대신 버퍼에서 데이터 반환

### 핵심 개념

`BufferedInputStream`은 **미리 읽기(prefetch)** 방식으로 동작합니다.

```
┌─────────────────────────────────────────────────────────────────┐
│                   BufferedInputStream 동작                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. 버퍼가 비어있으면 → 파일에서 8KB 읽어서 버퍼에 채움          │
│                                                                  │
│  2. read() 호출 시 → 버퍼에서 1byte 반환 (시스템 콜 없음!)       │
│                                                                  │
│  ┌───────────────────────────────────────────┐                  │
│  │           BufferedInputStream              │                  │
│  │  ┌─────────────────────────────────────┐  │                  │
│  │  │         내부 버퍼 (8KB)              │  │                  │
│  │  │  [1][2][3][4][5][6][7][8]...        │  │                  │
│  │  │   ↑                                  │  │                  │
│  │  │   현재 위치                          │  │                  │
│  │  └─────────────────────────────────────┘  │                  │
│  │              ↑                             │                  │
│  │              │ (버퍼가 비면 다시 채움)     │                  │
│  │  ┌─────────────────────────────────────┐  │                  │
│  │  │       FileInputStream               │  │                  │
│  │  └─────────────────────────────────────┘  │                  │
│  └───────────────────────────────────────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 예제 코드 - ReadFileV3 (BufferedInputStream)

```java
package io.buffered;

import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.io.IOException;
import static io.buffered.BufferedConst.*;

public class ReadFileV3 {

    public static void main(String[] args) throws IOException {
        FileInputStream fis = new FileInputStream(FILE_NAME);
        BufferedInputStream bis = new BufferedInputStream(fis, BUFFER_SIZE);
        long startTime = System.currentTimeMillis();

        int fileSize = 0;
        int data;
        while ((data = bis.read()) != -1) {  // 1byte씩 읽어도 빠름!
            fileSize++;
        }
        bis.close();

        long endTime = System.currentTimeMillis();
        System.out.println("File name: " + FILE_NAME);
        System.out.println("File size: " + fileSize / 1024 / 1024 + "MB");
        System.out.println("Time taken: " + (endTime - startTime) + "ms");
    }
}
```

### 실행 결과

```
File name: temp/buffered.dat
File size: 10MB
Time taken: 110ms
```

### 읽기 성능 비교

| 버전 | 방식 | 소요 시간 |
|------|------|----------|
| V1 | 1byte씩 직접 | ~14,000ms |
| V2 | byte[] 버퍼 직접 관리 | ~10ms |
| **V3** | **BufferedInputStream** | **~110ms** |

### 기존 코드와의 호환성

```java
// V1 코드 (느림)
FileInputStream fis = new FileInputStream(FILE_NAME);
while ((data = fis.read()) != -1) { ... }

// V3 코드 (빠름) - BufferedInputStream만 추가!
FileInputStream fis = new FileInputStream(FILE_NAME);
BufferedInputStream bis = new BufferedInputStream(fis);  // 한 줄 추가
while ((data = bis.read()) != -1) { ... }  // 나머지 코드 동일
```

---

## 5. 파일 입출력과 성능 최적화5 - 한 번에 쓰기

> **TL;DR**
> - 파일 전체를 **한 번에** 메모리에 올려서 처리
> - 가장 빠름 (10ms 미만)
> - 단, **메모리 사용량 주의** 필요

### 예제 코드 - V4 (한 번에 쓰기)

```java
package io.buffered;

import java.io.FileOutputStream;
import java.io.IOException;
import static io.buffered.BufferedConst.*;

public class CreateFileV4 {

    public static void main(String[] args) throws IOException {
        FileOutputStream fos = new FileOutputStream(FILE_NAME);
        long startTime = System.currentTimeMillis();

        byte[] buffer = new byte[FILE_SIZE];  // 10MB 배열!
        for (int i = 0; i < FILE_SIZE; i++) {
            buffer[i] = 1;
        }
        fos.write(buffer);  // 한 번에 쓰기
        fos.close();

        long endTime = System.currentTimeMillis();
        System.out.println("File created: " + FILE_NAME);
        System.out.println("File size: " + FILE_SIZE / 1024 / 1024 + "MB");
        System.out.println("Time taken: " + (endTime - startTime) + "ms");
    }
}
```

### 한 번에 읽기 - readAllBytes()

```java
package io.buffered;

import java.io.FileInputStream;
import java.io.IOException;
import static io.buffered.BufferedConst.*;

public class ReadFileV4 {

    public static void main(String[] args) throws IOException {
        FileInputStream fis = new FileInputStream(FILE_NAME);
        long startTime = System.currentTimeMillis();

        byte[] bytes = fis.readAllBytes();  // 파일 전체 읽기
        fis.close();

        long endTime = System.currentTimeMillis();
        System.out.println("File name: " + FILE_NAME);
        System.out.println("File size: " + bytes.length / 1024 / 1024 + "MB");
        System.out.println("Time taken: " + (endTime - startTime) + "ms");
    }
}
```

### 전체 성능 비교 표

| 버전 | 쓰기 방식 | 쓰기 시간 | 읽기 시간 |
|------|----------|----------|----------|
| V1 | 1byte씩 | 14,197ms | 14,000ms |
| V2 | byte[] 버퍼 (8KB) | 14ms | 10ms |
| V3 | BufferedXxx | 102ms | 110ms |
| **V4** | **한 번에** | **10ms** | **8ms** |

### 각 방식의 사용 케이스

| 방식 | 사용 케이스 | 장점 | 단점 |
|------|-----------|------|------|
| V1 | (사용 금지) | - | 너무 느림 |
| V2 | 대용량 파일 처리 | 빠름, 메모리 효율 | 코드 복잡 |
| V3 | 일반적인 파일 처리 | 코드 간결 | synchronized 오버헤드 |
| V4 | 작은 파일 | 가장 빠름, 간단 | 메모리 사용량 큼 |

### 주의사항

```
⚠️ V4 사용 시 주의!

1GB 파일을 readAllBytes()로 읽으면?
→ 1GB 메모리 필요
→ OutOfMemoryError 위험

권장:
- 작은 파일 (수 MB 이하): V4 (한 번에)
- 중간 파일 (수십 MB): V3 (BufferedXxx)
- 대용량 파일 (수백 MB 이상): V2 (직접 버퍼 관리)
```

---

## 정리

### 성능 최적화 핵심 원리

```
┌─────────────────────────────────────────────────────────────────┐
│                     성능 최적화 핵심                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ❌ 느림: 1byte마다 시스템 콜                                   │
│     → 시스템 콜은 비용이 비쌈!                                  │
│                                                                  │
│  ✅ 빠름: 여러 byte를 모아서 한 번에 시스템 콜                   │
│     → 시스템 콜 횟수 최소화!                                    │
│                                                                  │
│  핵심: 버퍼를 사용하여 I/O 호출 횟수를 줄이자!                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 버퍼 사용 방법 비교

| 방법 | 장점 | 단점 |
|------|------|------|
| 직접 byte[] 관리 | 가장 빠름 | 코드 복잡, 실수 가능 |
| BufferedXxx 사용 | 코드 간결 | synchronized 오버헤드 |
| readAllBytes() | 가장 간단 | 메모리 사용량 큼 |

### 실무 권장 사항

1. **대부분의 경우**: `BufferedInputStream/BufferedOutputStream` 사용
2. **극한의 성능 필요 시**: 직접 byte[] 버퍼 관리
3. **작은 파일**: `readAllBytes()`, `write(byte[])` 사용
4. **버퍼 크기**: 4KB ~ 8KB 권장

---

## 면접 질문

### 초급 개발자 (Junior)

**Q1. 파일 I/O에서 버퍼를 사용하면 왜 빨라지나요?**
<details>
<summary>답안 보기</summary>

버퍼를 사용하면 시스템 콜 호출 횟수가 줄어들기 때문입니다.

- 1byte씩 쓰면 10MB 파일에 1000만 번 시스템 콜 필요
- 8KB 버퍼 사용 시 약 1,280번 시스템 콜로 감소
- 시스템 콜은 사용자 모드 → 커널 모드 전환 비용이 발생하므로, 호출 횟수를 줄이면 성능이 향상됨

</details>

**Q2. BufferedOutputStream과 FileOutputStream의 차이점은?**
<details>
<summary>답안 보기</summary>

- **FileOutputStream**: 직접 파일에 쓰는 스트림. write() 호출마다 시스템 콜 발생
- **BufferedOutputStream**: FileOutputStream을 감싸서 버퍼 기능 추가. write() 호출 시 내부 버퍼에 저장하고, 버퍼가 가득 차면 한 번에 파일에 씀

BufferedOutputStream은 Decorator 패턴을 사용하여 기존 스트림에 버퍼 기능을 추가합니다.

</details>

**Q3. flush()와 close()의 차이점은?**
<details>
<summary>답안 보기</summary>

- **flush()**: 버퍼에 남아있는 데이터를 강제로 출력. 스트림은 열린 상태 유지
- **close()**: flush()를 호출한 후 스트림을 닫고 시스템 자원 해제

close()를 호출하면 자동으로 flush()가 먼저 실행되므로, 정상 종료 시에는 close()만 호출하면 됩니다.

</details>

### 중급 개발자 (Mid-Level)

**Q4. BufferedOutputStream이 직접 byte[] 버퍼를 사용하는 것보다 느린 이유는?**
<details>
<summary>답안 보기</summary>

BufferedOutputStream의 write() 메서드는 **synchronized** 키워드로 동기화되어 있습니다.

```java
public synchronized void write(int b) throws IOException {
    if (count >= buf.length) {
        flushBuffer();
    }
    buf[count++] = (byte)b;
}
```

멀티스레드 환경에서의 안전성을 위해 모든 write 호출마다 락을 획득/해제하므로, 단일 스레드 환경에서는 불필요한 오버헤드가 발생합니다.

직접 byte[] 버퍼를 사용하면 이러한 동기화 오버헤드가 없어 더 빠릅니다.

</details>

**Q5. 파일 크기에 따른 최적의 I/O 전략은?**
<details>
<summary>답안 보기</summary>

| 파일 크기 | 권장 전략 | 이유 |
|----------|----------|------|
| 작은 파일 (수 MB 이하) | readAllBytes() / write(byte[]) | 코드 간결, 충분히 빠름 |
| 중간 파일 (수십 MB) | BufferedXxx 스트림 | 코드 간결 + 적절한 성능 |
| 대용량 파일 (수백 MB~) | 직접 byte[] 버퍼 관리 | 메모리 효율 + 최고 성능 |

대용량 파일에서 readAllBytes()를 사용하면 OutOfMemoryError 위험이 있습니다.

</details>

### 고급 개발자 (Senior)

**Q6. 운영체제의 I/O 버퍼링과 Java BufferedXxx의 관계를 설명해주세요.**
<details>
<summary>답안 보기</summary>

I/O 버퍼링은 두 레벨에서 발생합니다:

1. **Java 레벨 (BufferedXxx)**
   - JVM 힙 메모리에 버퍼 유지
   - 시스템 콜 호출 횟수 감소 목적

2. **OS 레벨 (페이지 캐시)**
   - 커널이 관리하는 파일 시스템 캐시
   - 실제 디스크 I/O 횟수 감소 목적

Java의 BufferedOutputStream이 버퍼를 비우면:
1. 시스템 콜로 커널에 데이터 전달
2. 커널은 페이지 캐시에 데이터 저장
3. 커널이 적절한 시점에 디스크에 쓰기 (지연 쓰기)

따라서 Java 버퍼와 OS 버퍼 두 단계의 버퍼링이 협력하여 성능을 최적화합니다.

</details>

---

## 학습 체크리스트

- [ ] 1byte씩 I/O하면 왜 느린지 설명할 수 있다
- [ ] 버퍼의 개념과 최적 크기를 설명할 수 있다
- [ ] BufferedXxx 스트림의 동작 원리를 이해했다
- [ ] flush()와 close()의 차이를 알고 있다
- [ ] 파일 크기에 따른 최적 I/O 전략을 선택할 수 있다
- [ ] 예제 코드를 직접 실행하고 성능을 측정해보았다

---

## 네비게이션

- [이전: Part 1 - 스트림 기본 개념](./2-IO기본1-part1.md)
- [다음: 3. IO 기본2](./3-IO기본2-part1.md)
