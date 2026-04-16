# 1. 문자 인코딩 - Part 2

**출처**: 인프런 - 김영한의 실전 자바 고급 2편
**작성일**: 2026-01-03

> **문서 구성**
> - Part 1: 컴퓨터와 데이터, 문자 인코딩 기초 (ASCII, ISO-8859-1, EUC-KR, MS949)
> - Part 2: 유니코드 (UTF-8, UTF-16), Java 문자 인코딩 실습, 면접 질문

---

## 목차

1. [유니코드의 등장](#1-유니코드의-등장)
2. [UTF-16](#2-utf-16)
3. [UTF-8](#3-utf-8)
4. [Java 문자 집합 조회](#4-java-문자-집합-조회)
5. [Java 문자 인코딩 실습](#5-java-문자-인코딩-실습)
6. [한글 깨짐 문제 정리](#6-한글-깨짐-문제-정리)
7. [면접 질문](#7-면접-질문)

---

## 1. 유니코드의 등장

> **TL;DR**
> - 각 나라별 문자 집합의 호환성 문제 해결을 위해 등장
> - 전 세계 모든 문자를 하나의 표준으로 통합
> - UTF-16, UTF-8 두 가지 인코딩 방식 존재

### 핵심 개념

**문제점**
- EUC-KR, MS949 등 각 나라별 문자표가 다름
- 한글 문서를 보려면 한글 문자표가 필요
- 한 문서에 여러 언어를 함께 저장하기 어려움

**해결책: 유니코드(Unicode)**
- 1990년대 도입
- 전 세계 모든 문자와 기호를 **하나의 표준**으로 통합
- Uni(Universal) + code = 전 세계적인 코드!

### 상세 설명

```
┌─────────────────────────────────────────────────┐
│                  기존 방식                       │
│                                                 │
│   한국 ──── EUC-KR ────┐                        │
│   일본 ──── Shift-JIS ─┼─── 호환 불가 ❌        │
│   중국 ──── GB2312 ────┘                        │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│                 유니코드 방식                    │
│                                                 │
│   한국 ──┐                                      │
│   일본 ──┼─── Unicode ─── 모두 호환 ✅          │
│   중국 ──┘                                      │
└─────────────────────────────────────────────────┘
```

---

## 2. UTF-16

> **TL;DR**
> - 16bit(2byte) 기반 인코딩
> - 대부분의 문자 2byte, 일부 4byte
> - ASCII와 **호환되지 않음** (영문도 2byte)
> - Java 내부에서 문자 표현에 사용 (char = 2byte)

### 핵심 개념

| 항목 | 내용 |
|------|------|
| 개발 시기 | 1990년대 |
| 기본 단위 | 16bit (2byte) |
| 영문 | **2byte** |
| 한글/중국어/일본어 | 2byte |
| 이모지/고대문자 | 4byte |
| ASCII 호환 | **X** |

### 상세 설명

#### 장점
- 대부분의 문자를 2byte로 처리 → **계산이 편리함**
- 문자열 길이 계산, 특정 문자 접근이 상대적으로 단순

#### 단점
```
ASCII 'A' 저장 시:
- ASCII/UTF-8: [65]        → 1byte
- UTF-16:      [0, 65]     → 2byte  (2배!)

웹 문서의 80% 이상이 영문 → 메모리/네트워크 낭비
```

### Java와 UTF-16

```java
// Java의 char 타입은 2byte (UTF-16 기반)
char c = 'A';  // 내부적으로 2byte 사용
char k = '가'; // 내부적으로 2byte 사용
```

초반에 UTF-16이 인기 → Java 설계 시 채택 → `char`가 2byte인 이유

---

## 3. UTF-8

> **TL;DR**
> - 8bit(1byte) 기반 **가변 길이** 인코딩
> - ASCII 문자 1byte, 한글 3byte
> - ASCII와 **완벽 호환**
> - **현대의 사실상 표준 인코딩**

### 핵심 개념

| 항목 | 내용 |
|------|------|
| 개발 시기 | 1990년대 |
| 기본 단위 | 8bit (1byte) |
| 영문/ASCII | **1byte** |
| 그리스어/히브리어 | 2byte |
| **한글/한자/일본어** | **3byte** |
| 이모지/고대문자 | 4byte |
| ASCII 호환 | **O** |

### 상세 설명

#### 인코딩 비교
```
문자 'A' (영문):
┌──────────────┬─────────────┬───────────┐
│   인코딩     │    결과     │   크기    │
├──────────────┼─────────────┼───────────┤
│   ASCII      │    [65]     │   1byte   │
│   UTF-8      │    [65]     │   1byte   │ ← 동일!
│   UTF-16     │   [0, 65]   │   2byte   │
└──────────────┴─────────────┴───────────┘

문자 '가' (한글):
┌──────────────┬─────────────────────┬───────────┐
│   인코딩     │        결과         │   크기    │
├──────────────┼─────────────────────┼───────────┤
│   EUC-KR     │    [-80, -95]       │   2byte   │
│   MS949      │    [-80, -95]       │   2byte   │
│   UTF-8      │ [-22, -80, -128]    │   3byte   │
│   UTF-16     │    [-84, 0]         │   2byte   │
└──────────────┴─────────────────────┴───────────┘
```

### UTF-8이 표준이 된 이유

1. **저장 공간 절약 & 네트워크 효율성**
   - 웹 문서의 80% 이상이 영문
   - 영문 1byte로 처리 → UTF-16 대비 2배 효율적

2. **ASCII 호환성**
   - 기존 ASCII 기반 레거시 시스템과 호환
   - 문자 'A'는 ASCII, UTF-8 모두 65로 인코딩

3. **표준화**
   - 2008년 W3C 웹 표준에 UTF-8 채택
   - 현재 대부분의 웹사이트/애플리케이션 기본 인코딩

### 주요 포인트

```
결론: UTF-8을 사용하자!
```

### 주의사항

한글 윈도우의 경우 호환성 때문에 기본 인코딩이 **MS949**로 유지됨
(UTF-8로 변경 중)

---

## 4. Java 문자 집합 조회

> **TL;DR**
> - `Charset` 클래스로 문자 집합 다루기
> - `StandardCharsets`에 자주 사용하는 문자 집합 상수 정의
> - `Charset.defaultCharset()`으로 시스템 기본 문자 집합 확인

### 예제 코드

```java
package charset;

import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.util.Set;
import java.util.SortedMap;

public class AvailableCharsetsMain {

    public static void main(String[] args) {
        // 1. 이용 가능한 모든 Charset 조회 (자바 + OS)
        SortedMap<String, Charset> charsets = Charset.availableCharsets();
        for (String charsetName : charsets.keySet()) {
            System.out.println("charsetName = " + charsetName);
        }

        // 2. 문자로 조회 (대소문자 구분 X)
        Charset charset1 = Charset.forName("MS949");
        System.out.println("charset1 = " + charset1);

        // 3. 별칭 조회
        Set<String> aliases = charset1.aliases();
        for (String alias : aliases) {
            System.out.println("alias = " + alias);
        }

        // 4. UTF-8 상수로 조회 (권장)
        Charset charset2 = StandardCharsets.UTF_8;
        System.out.println("charset2 = " + charset2);

        // 5. 시스템 기본 Charset 조회
        Charset defaultCharset = Charset.defaultCharset();
        System.out.println("defaultCharset = " + defaultCharset);
    }
}
```

### 실행 결과

```
charsetName = EUC-KR
charsetName = ISO-8859-1
charsetName = US-ASCII
charsetName = UTF-16
charsetName = UTF-8
charsetName = x-windows-949
...
charset1 = x-windows-949
alias = ms949
alias = ms_949
alias = windows-949
charset2 = UTF-8
defaultCharset = UTF-8
```

### StandardCharsets 상수

```java
public final class StandardCharsets {
    public static final Charset US_ASCII;
    public static final Charset ISO_8859_1;
    public static final Charset UTF_8;      // 가장 많이 사용
    public static final Charset UTF_16BE;
    public static final Charset UTF_16LE;
    public static final Charset UTF_16;
}
```

### 주요 메서드 정리

| 메서드 | 설명 |
|--------|------|
| `Charset.availableCharsets()` | 사용 가능한 모든 문자 집합 |
| `Charset.forName("UTF-8")` | 이름으로 문자 집합 조회 |
| `charset.aliases()` | 별칭 목록 조회 |
| `Charset.defaultCharset()` | 시스템 기본 문자 집합 |
| `StandardCharsets.UTF_8` | UTF-8 상수 (권장) |

---

## 5. Java 문자 인코딩 실습

> **TL;DR**
> - `String.getBytes(Charset)`: 문자 → byte[] (인코딩)
> - `new String(byte[], Charset)`: byte[] → 문자 (디코딩)
> - 인코딩/디코딩에 같은 문자 집합 사용 필수

### 인코딩 예제

```java
package charset;

import java.nio.charset.Charset;
import java.util.Arrays;
import static java.nio.charset.StandardCharsets.*;

public class EncodingMain1 {

    private static final Charset EUC_KR = Charset.forName("EUC-KR");
    private static final Charset MS_949 = Charset.forName("MS949");

    public static void main(String[] args) {
        System.out.println("== ASCII 영문 처리 ==");
        encoding("A", US_ASCII);
        encoding("A", ISO_8859_1);
        encoding("A", EUC_KR);
        encoding("A", UTF_8);
        encoding("A", UTF_16BE);

        System.out.println("== 한글 지원 ==");
        encoding("가", EUC_KR);
        encoding("가", MS_949);
        encoding("가", UTF_8);
        encoding("가", UTF_16BE);
    }

    private static void encoding(String text, Charset charset) {
        byte[] bytes = text.getBytes(charset);  // 인코딩
        System.out.printf("%s -> [%s] 인코딩 -> %s %sbyte\n",
            text, charset, Arrays.toString(bytes), bytes.length);
    }
}
```

### 실행 결과

```
== ASCII 영문 처리 ==
A -> [US-ASCII] 인코딩 -> [65] 1byte
A -> [ISO-8859-1] 인코딩 -> [65] 1byte
A -> [EUC-KR] 인코딩 -> [65] 1byte
A -> [UTF-8] 인코딩 -> [65] 1byte
A -> [UTF-16BE] 인코딩 -> [0, 65] 2byte

== 한글 지원 ==
가 -> [EUC-KR] 인코딩 -> [-80, -95] 2byte
가 -> [x-windows-949] 인코딩 -> [-80, -95] 2byte
가 -> [UTF-8] 인코딩 -> [-22, -80, -128] 3byte
가 -> [UTF-16BE] 인코딩 -> [-84, 0] 2byte
```

### 인코딩 + 디코딩 예제

```java
package charset;

import java.nio.charset.Charset;
import java.util.Arrays;
import static java.nio.charset.StandardCharsets.*;

public class EncodingMain2 {

    private static final Charset EUC_KR = Charset.forName("EUC-KR");
    private static final Charset MS_949 = Charset.forName("MS949");

    public static void main(String[] args) {
        // 같은 문자 집합으로 인코딩/디코딩 - 성공
        test("가", EUC_KR, EUC_KR);
        test("가", UTF_8, UTF_8);

        // 다른 문자 집합으로 디코딩 - 실패
        test("가", EUC_KR, UTF_8);
        test("가", UTF_8, MS_949);

        // EUC-KR에 없는 문자 - 실패
        test("뷁", EUC_KR, EUC_KR);
        test("뷁", MS_949, MS_949);  // MS949는 성공
    }

    private static void test(String text, Charset encodingCharset,
                             Charset decodingCharset) {
        byte[] encoded = text.getBytes(encodingCharset);  // 인코딩
        String decoded = new String(encoded, decodingCharset);  // 디코딩
        System.out.printf("%s -> [%s] 인코딩 -> %s -> [%s] 디코딩 -> %s\n",
            text, encodingCharset, Arrays.toString(encoded),
            decodingCharset, decoded);
    }
}
```

### 실행 결과

```
가 -> [EUC-KR] 인코딩 -> [-80, -95] -> [EUC-KR] 디코딩 -> 가
가 -> [UTF-8] 인코딩 -> [-22, -80, -128] -> [UTF-8] 디코딩 -> 가
가 -> [EUC-KR] 인코딩 -> [-80, -95] -> [UTF-8] 디코딩 -> ��
가 -> [UTF-8] 인코딩 -> [-22, -80, -128] -> [x-windows-949] 디코딩 -> 媛�
뷁 -> [EUC-KR] 인코딩 -> [63] -> [EUC-KR] 디코딩 -> ?
뷁 -> [x-windows-949] 인코딩 -> [-108, -18] -> [x-windows-949] 디코딩 -> 뷁
```

### 핵심 API

| 메서드 | 설명 |
|--------|------|
| `String.getBytes()` | 기본 문자 집합으로 인코딩 |
| `String.getBytes(Charset)` | 지정 문자 집합으로 인코딩 |
| `new String(byte[])` | 기본 문자 집합으로 디코딩 |
| `new String(byte[], Charset)` | 지정 문자 집합으로 디코딩 |

---

## 6. 한글 깨짐 문제 정리

> **TL;DR**
> - 인코딩과 디코딩에 **다른 문자 집합**을 사용하면 깨짐
> - UTF-8 ↔ EUC-KR/MS949 호환 안됨
> - 해결책: **UTF-8로 통일**

### 한글 깨지는 2가지 주요 원인

#### 원인 1: UTF-8 ↔ EUC-KR(MS949) 불일치

```
UTF-8로 인코딩 → EUC-KR로 디코딩 = 깨짐!
EUC-KR로 인코딩 → UTF-8로 디코딩 = 깨짐!
```

```java
// 실패 케이스
test("가", UTF_8, EUC_KR);   // 媛�
test("가", EUC_KR, UTF_8);   // ��
```

#### 원인 2: ISO-8859-1로 디코딩

```
한글 인코딩 → ISO-8859-1로 디코딩 = 깨짐!
(ISO-8859-1은 한글을 지원하지 않음)
```

### 문자 집합 호환성 정리

```
┌─────────────────────────────────────────────────────┐
│                    호환성 관계                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│   ASCII ──────┬───── ISO-8859-1                    │
│               │                                     │
│               ├───── EUC-KR ─── MS949              │
│               │       (포함)    (확장)              │
│               │                                     │
│               └───── UTF-8                         │
│                                                     │
│   * UTF-16은 ASCII와 호환 안됨                      │
│   * UTF-8 ↔ EUC-KR/MS949 호환 안됨                 │
└─────────────────────────────────────────────────────┘
```

### 호환성 표

| 인코딩 | 디코딩 | 영문 | 한글 |
|--------|--------|------|------|
| EUC-KR | EUC-KR | O | O (2,350자) |
| EUC-KR | MS949 | O | O |
| MS949 | EUC-KR | O | △ (일부만) |
| UTF-8 | UTF-8 | O | O |
| EUC-KR | UTF-8 | O | **X** |
| UTF-8 | EUC-KR | O | **X** |

### 해결책

```
┌─────────────────────────────────────────┐
│                                         │
│    모든 곳에서 UTF-8 사용하기!          │
│                                         │
│    - 소스 코드 파일                     │
│    - 데이터베이스                       │
│    - HTTP 통신                          │
│    - 파일 저장                          │
│                                         │
└─────────────────────────────────────────┘
```

---

## 7. 면접 질문

### 초급 개발자 (Junior)

**Q1. 문자 인코딩과 디코딩의 차이점은 무엇인가요?**
<details>
<summary>답안 보기</summary>

- **인코딩(Encoding)**: 문자를 컴퓨터가 이해할 수 있는 숫자(byte)로 변환하는 것
  - 예: 'A' → 65
- **디코딩(Decoding)**: 숫자(byte)를 사람이 읽을 수 있는 문자로 변환하는 것
  - 예: 65 → 'A'
- 핵심: 인코딩과 디코딩에 **같은 문자 집합**을 사용해야 함

</details>

**Q2. UTF-8과 ASCII의 관계는 무엇인가요?**
<details>
<summary>답안 보기</summary>

- UTF-8은 ASCII와 **완벽하게 호환**됩니다
- ASCII 문자(0-127)는 UTF-8에서도 동일한 1byte로 표현
- 예: 문자 'A'는 ASCII, UTF-8 모두 65로 인코딩
- 따라서 ASCII로 작성된 문서는 UTF-8로 읽어도 정상 동작

</details>

**Q3. Java에서 char 타입이 2byte인 이유는 무엇인가요?**
<details>
<summary>답안 보기</summary>

- Java가 설계될 당시(1990년대 초) UTF-16이 인기였음
- UTF-16은 대부분의 문자를 2byte로 표현
- Java는 내부적으로 문자를 UTF-16으로 표현하도록 설계
- 따라서 `char` 타입이 2byte(16bit)로 정의됨

</details>

### 중급 개발자 (Mid-Level)

**Q4. UTF-8과 UTF-16의 차이점과 UTF-8이 표준이 된 이유는?**
<details>
<summary>답안 보기</summary>

**차이점:**
| 항목 | UTF-8 | UTF-16 |
|------|-------|--------|
| 기본 단위 | 1byte | 2byte |
| 영문 | 1byte | 2byte |
| 한글 | 3byte | 2byte |
| ASCII 호환 | O | X |

**UTF-8이 표준이 된 이유:**
1. **저장 공간 절약**: 웹 문서의 80%가 영문 → 1byte로 처리하여 효율적
2. **ASCII 호환성**: 레거시 시스템과 호환 가능
3. **네트워크 효율성**: 데이터 전송 시 트래픽 절약

</details>

**Q5. 한글이 깨지는 원인과 해결 방법은?**
<details>
<summary>답안 보기</summary>

**원인:**
1. 인코딩과 디코딩에 서로 다른 문자 집합 사용
   - UTF-8로 인코딩 → EUC-KR로 디코딩 (또는 그 반대)
2. 한글을 지원하지 않는 문자 집합으로 디코딩
   - 예: ISO-8859-1로 한글 디코딩

**해결 방법:**
- 모든 시스템에서 **UTF-8로 통일**
- 소스 파일, DB, HTTP 통신, 파일 저장 모두 UTF-8 사용
- Java에서는 `StandardCharsets.UTF_8` 명시적 지정

</details>

### 고급 개발자 (Senior)

**Q6. EUC-KR, MS949, UTF-8 중 어떤 것을 선택해야 하나요?**
<details>
<summary>답안 보기</summary>

**권장: UTF-8**

**이유:**
1. **국제 표준**: W3C 웹 표준, 대부분의 시스템 기본값
2. **모든 언어 지원**: 한글뿐 아니라 전 세계 모든 문자 표현 가능
3. **ASCII 호환**: 레거시 시스템과 호환
4. **네트워크 효율**: 영문 위주 데이터에서 효율적

**EUC-KR/MS949를 사용해야 하는 경우:**
- 레거시 시스템과의 호환성이 필수인 경우
- 한글 윈도우 시스템과 직접 연동하는 경우
- 기존 EUC-KR 데이터베이스 마이그레이션이 어려운 경우

**트레이드오프:**
- UTF-8은 한글 3byte → EUC-KR(2byte) 대비 용량 증가
- 하지만 현대 시스템에서는 이 차이가 거의 무의미함

</details>

---

## 전체 요약

1. **컴퓨터는 0과 1만 이해** → 문자를 숫자로 매핑하는 문자 집합 필요
2. **ASCII**: 7bit, 128자, 영문/숫자/특수문자
3. **EUC-KR/MS949**: 한글 지원, ASCII 호환, 한글 2byte
4. **UTF-8**: 현대 표준, ASCII 호환, 가변 길이(영문 1byte, 한글 3byte)
5. **UTF-16**: Java 내부 사용, ASCII 비호환, 대부분 2byte

## 학습 체크리스트

- [ ] 문자 인코딩/디코딩 개념 이해
- [ ] ASCII, UTF-8, UTF-16 차이점 암기
- [ ] Java Charset API 사용법 숙지
- [ ] 한글 깨짐 문제 원인과 해결법 이해
- [ ] 면접 질문 연습

## 다음 학습

- [2. IO 기본1](./2-IO기본1.md) - 스트림 기반 입출력

---

## 네비게이션

- [이전: Part 1 - 컴퓨터와 문자 인코딩 기초](./1-문자인코딩-part1.md)
