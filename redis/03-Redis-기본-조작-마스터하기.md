# 🔧 3. Redis 기본 조작 마스터하기

> **학습 목표**: Redis CLI를 능수능란하게 다루고, 기본적인 데이터 조작을 완벽하게 마스터합니다.

**⏱️ 예상 학습 시간**: 2-3시간
**난이도**: ⭐⭐☆☆☆ (2개/5개)

---

## 📚 목차
- [왜 Redis 기본 조작이 중요한가](#왜-redis-기본-조작이-중요한가)
- [실생활 비유로 이해하기](#실생활-비유로-이해하기)
- [핵심 개념](#핵심-개념)
- [학습 목표](#학습-목표)
- [Redis CLI 완전 정복](#1-redis-cli-완전-정복)
- [기본 데이터 저장과 조회](#2-기본-데이터-저장과-조회-set-get)
- [실무 활용 사례](#실무-활용-사례)
- [키 관리 명령어](#3-키-관리-명령어-keys-exists-del)
- [TTL과 만료 시간 설정](#4-ttl과-만료-시간-설정)
- [Redis 데이터베이스 선택](#5-redis-데이터베이스-선택)
- [실전 프로젝트](#실전-프로젝트)
- [실전 연습 및 종합 실습](#6-실전-연습-및-종합-실습)
- [주니어 시나리오](#주니어-시나리오)
- [면접 질문 리스트](#면접-질문-리스트)
- [핵심 내용 정리](#7-핵심-내용-정리)
- [자주 묻는 질문 (FAQ)](#8-자주-묻는-질문-faq)
- [다음 단계 예고](#9-다음-단계-예고)
- [축하합니다](#축하합니다)

---

## 🤔 왜 Redis 기본 조작이 중요한가?

### 실무 배경
**Redis를 단순히 설치만 한다고 활용할 수 있는 것은 아닙니다.**

#### ❌ 기본 조작을 모르면 발생하는 문제
```
문제 1: 데이터 관리 실패
- 증상: 캐시 데이터가 무한정 쌓여 메모리 부족 발생
- 영향: 서비스 장애, 응답 속도 저하
- 비용: 장애 복구에 평균 2-4시간 소요, 매출 손실 $10,000/시간

문제 2: 보안 취약점
- 증상: 중요 데이터에 만료시간 미설정으로 데이터 누출
- 영향: 사용자 세션 영구 저장으로 보안 위험
- 비용: 개인정보 유출 시 법적 책임 및 벌금 최대 수억 원

문제 3: 성능 저하
- 증상: KEYS * 같은 위험한 명령어로 서비스 전체 중단
- 영향: 모든 사용자 요청 블로킹
- 비용: 고객 이탈률 증가, 평판 손실
```

#### ✅ 기본 조작을 마스터하면
```
해결책 1: 효율적 데이터 관리
- 방법: TTL 자동 설정으로 불필요한 데이터 자동 삭제
- 효과: 메모리 사용량 80% 절감
- 절감: 서버 비용 월 $500 → $100

해결책 2: 안전한 운영
- 방법: 적절한 키 명명 규칙과 만료 전략 수립
- 효과: 데이터 누출 위험 제로화
- 절감: 보안 사고 예방으로 연간 수천만 원 절약

해결책 3: 고성능 유지
- 방법: SCAN 같은 안전한 명령어 사용
- 효과: 서비스 안정성 99.9% 이상 유지
- 절감: 장애 대응 시간 90% 감소 (4시간 → 20분)
```

### 📊 수치로 보는 효과

| 지표 | Before | After | 개선율 |
|------|--------|-------|--------|
| 세션 만료 설정 시간 | 수동 관리 (1시간) | TTL 자동 (1초) | **99.97%↓** |
| 캐시 조회 속도 | DB 직접 (100ms) | Redis GET (0.1ms) | **99.9%↓** |
| 메모리 관리 비용 | 수동 삭제 | 자동 만료 | **100%↓** |
| 장애 대응 시간 | 4시간 | 20분 | **92%↓** |

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 편의점 계산대 시스템
```
Redis CLI = 편의점 계산대 직원
Redis 서버 = 창고 시스템
키(Key) = 상품 바코드
값(Value) = 실제 상품
TTL = 유통기한

┌─────────────────────────────────────┐
│     👤 고객 (개발자)                 │
│            ↓                        │
│     💻 계산대 (Redis CLI)            │
│            ↓                        │
│     🏪 창고 (Redis Server)           │
│   ┌──────┬──────┬──────┐            │
│   │콜라  │우유  │빵    │            │
│   │바코드│바코드│바코드│            │
│   │24시간│7일   │3일   │ ← TTL     │
│   └──────┴──────┴──────┘            │
└─────────────────────────────────────┘

작동 방식:
- GET 콜라 = "콜라 주세요" → 직원이 창고에서 가져옴
- SET 빵 "식빵" = "빵을 식빵으로 등록" → 창고에 저장
- DEL 우유 = "우유 버려주세요" → 창고에서 제거
- TTL 콜라 = "콜라 유통기한 얼마나 남았어요?" → 남은 시간 확인
```

### 비유 2: 아파트 관리 시스템
```
Redis 데이터베이스 = 아파트 각 층 (0층~15층)
키-값 쌍 = 각 호수와 가구
KEYS = 층별 입주자 명단 조회
SELECT = 엘리베이터로 층 이동

┌─────────────────────────────────────┐
│  15층 [SELECT 15] - VIP 데이터       │
│  14층 [SELECT 14] - 테스트 데이터    │
│  ...                                │
│   2층 [SELECT 2] - 캐시 데이터       │
│   1층 [SELECT 1] - 세션 데이터       │
│   0층 [SELECT 0] - 기본 데이터       │ ← 기본층
└─────────────────────────────────────┘

특징:
- 각 층은 완전히 독립적 (1층 201호 ≠ 2층 201호)
- 층마다 다른 용도로 사용 가능
- SELECT 명령어로 층 이동
```

### 비유 3: 도서관 대출 시스템
```
SET = 책 대출 (책을 빌려가는 것)
GET = 책 확인 (책이 있는지 보기)
EXPIRE = 반납 기한 (2주 후 자동 반납)
PERSIST = 무기한 대출 (기한 제거)

📚 도서관 시나리오:
┌─────────────────────────────────────┐
│ SET book:1001 "해리포터"              │
│ → 1001번 책을 "해리포터"로 등록       │
│                                     │
│ EXPIRE book:1001 1209600             │
│ → 14일(2주) 후 자동 반납              │
│                                     │
│ TTL book:1001                        │
│ → 반납까지 며칠 남았나요? (10일)      │
│                                     │
│ PERSIST book:1001                    │
│ → 이 책은 무기한 대출로 변경          │
└─────────────────────────────────────┘
```

### 비유 4: 배달앱 주문 관리
```
주문 접수 = SET order:123 "피자 2판"
주문 확인 = GET order:123
주문 취소 = DEL order:123
자동 취소 = EXPIRE order:123 600 (10분 후 미결제 시 자동 취소)

🍕 배달 프로세스:
┌─────────────────────────────────────┐
│ 1. 주문 접수 (SET)                   │
│    SET order:abc123 "피자+콜라"      │
│    EXPIRE order:abc123 600           │
│    → 10분 내 결제 안하면 자동 취소    │
│                                     │
│ 2. 주문 확인 (GET)                   │
│    GET order:abc123                  │
│    → "피자+콜라" 반환                │
│                                     │
│ 3. 남은 시간 확인 (TTL)              │
│    TTL order:abc123                  │
│    → 432초 남음 (약 7분)             │
│                                     │
│ 4. 결제 완료 (PERSIST)               │
│    PERSIST order:abc123              │
│    → 만료 시간 제거, 배달 진행        │
└─────────────────────────────────────┘
```

### 비유 5: 게임 캐릭터 버프 시스템
```
버프 적용 = SETEX buff:player1 30 "공격력+50%"
버프 확인 = GET buff:player1
남은 시간 = TTL buff:player1
버프 해제 = DEL buff:player1

⚔️ 게임 버프 시스템:
┌─────────────────────────────────────┐
│ 플레이어가 아이템 사용                │
│ ↓                                   │
│ SETEX buff:warrior1 60 "방어력+100"  │
│ (60초 동안 방어력 증가)               │
│                                     │
│ 전투 중 버프 확인:                    │
│ GET buff:warrior1 → "방어력+100"     │
│ TTL buff:warrior1 → 42초 남음        │
│                                     │
│ 버프 시간 만료:                       │
│ GET buff:warrior1 → (nil)            │
│ (자동으로 버프 해제됨)                │
└─────────────────────────────────────┘

장점:
- 서버가 자동으로 버프 시간 관리
- 개발자가 타이머 코드 작성 불필요
- 메모리 자동 정리
```

### 🎯 종합 비교표
```
┌──────────┬────────────┬────────────┬────────────┐
│ Redis    │ 편의점     │ 도서관     │ 게임       │
├──────────┼────────────┼────────────┼────────────┤
│ SET      │ 상품 등록  │ 책 대출    │ 버프 적용  │
│ GET      │ 상품 조회  │ 책 확인    │ 버프 확인  │
│ DEL      │ 상품 폐기  │ 책 반납    │ 버프 해제  │
│ EXPIRE   │ 유통기한   │ 반납 기한  │ 버프 시간  │
│ TTL      │ 남은 기한  │ 남은 기한  │ 남은 시간  │
└──────────┴────────────┴────────────┴────────────┘
```

---

## 📖 핵심 개념

### 개념 설명 (3단계 깊이)

#### 1️⃣ 초보자 수준 설명

**Redis는 거대한 메모리 저장소입니다.**

편의점을 생각해보세요. 편의점에는 수많은 상품이 진열대에 있고, 각 상품에는 바코드가 붙어있습니다. 바코드를 스캔하면 상품 정보가 나오죠.

Redis도 마찬가지입니다:
- **키(Key)** = 바코드 (상품을 찾는 번호)
- **값(Value)** = 실제 상품 (저장된 데이터)
- **TTL** = 유통기한 (데이터 만료 시간)

계산대 직원(Redis CLI)에게 "콜라 주세요(GET cola)"라고 하면 창고에서 콜라를 가져다줍니다.

#### 2️⃣ 중급자 수준 설명

**Redis는 In-Memory Key-Value 데이터베이스입니다.**

주요 특징:
- **싱글 스레드**: 한 번에 하나의 명령만 처리 (순차적)
- **원자적 연산**: 명령이 중간에 끊기지 않고 완전히 실행됨
- **논리적 DB 분리**: 0~15번 데이터베이스로 데이터 격리
- **자동 만료**: TTL 설정으로 메모리 자동 관리

동작 원리:
```
클라이언트 → Redis CLI → Redis 서버 → 메모리
                 ↓
          명령어 큐 (FIFO)
                 ↓
       싱글 스레드 처리
```

#### 3️⃣ 고급자 수준 설명

**Redis 내부 메커니즘과 최적화**

**메모리 구조**:
- Hash Table 기반 키-값 저장 (O(1) 조회)
- Dict(Dictionary) 자료구조 사용
- Rehashing: 점진적 해시 테이블 확장

**만료 메커니즘**:
1. **Passive Expiration**: 키 접근 시 만료 확인
2. **Active Expiration**: 초당 10회, 20개 키 랜덤 샘플링

**싱글 스레드의 이점**:
- Lock-free 구조 (경쟁 조건 없음)
- 원자적 연산 보장
- 예측 가능한 성능

**최적화 전략**:
- 파이프라이닝: 여러 명령을 한 번에 전송
- 트랜잭션: MULTI/EXEC로 원자적 실행
- Lua 스크립트: 서버 측 로직 실행

### 주요 용어 정리

| 용어 | 영문 | 설명 | 예시 |
|------|------|------|------|
| 키 | Key | 데이터를 식별하는 고유한 문자열 | `user:1001:name` |
| 값 | Value | 키에 연결된 실제 데이터 | `"김철수"` |
| TTL | Time To Live | 데이터의 생존 시간 (초) | `1800` (30분) |
| 만료 | Expiration | TTL이 지나 데이터가 자동 삭제됨 | 30분 후 자동 삭제 |
| 데이터베이스 | Database | 논리적 데이터 분리 (0~15) | `SELECT 0` |
| CLI | Command Line Interface | 명령줄 인터페이스 | `redis-cli` |
| 원자적 연산 | Atomic Operation | 중단되지 않고 완전히 실행되는 연산 | `SETEX` |
| 싱글 스레드 | Single Thread | 한 번에 하나의 명령만 처리 | 순차적 실행 |

### 기술 아키텍처

```
┌──────────────────────────────────────────────────────┐
│                   클라이언트 계층                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐     │
│  │ redis-cli  │  │ Python     │  │ Node.js    │     │
│  │ (CLI)      │  │ (redis-py) │  │ (ioredis)  │     │
│  └────┬───────┘  └────┬───────┘  └────┬───────┘     │
└───────┼───────────────┼───────────────┼──────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│                  Redis 서버 계층                       │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │          명령어 큐 (Command Queue)              │ │
│  │   GET key1 → SET key2 → DEL key3 → ...        │ │
│  └────────────────┬───────────────────────────────┘ │
│                   ↓                                  │
│  ┌────────────────────────────────────────────────┐ │
│  │       싱글 스레드 이벤트 루프 (Main Thread)     │ │
│  │       명령어를 하나씩 순차적으로 처리            │ │
│  └────────────────┬───────────────────────────────┘ │
│                   ↓                                  │
│  ┌────────────────────────────────────────────────┐ │
│  │              메모리 데이터 구조                  │ │
│  │                                                │ │
│  │  DB 0: ┌──────────────────┐                   │ │
│  │        │ Hash Table       │                   │ │
│  │        │ key1 → value1    │                   │ │
│  │        │ key2 → value2    │                   │ │
│  │        └──────────────────┘                   │ │
│  │                                                │ │
│  │  DB 1: ┌──────────────────┐                   │ │
│  │        │ Hash Table       │                   │ │
│  │        │ key3 → value3    │                   │ │
│  │        └──────────────────┘                   │ │
│  │                                                │ │
│  │  DB 2-15: ...                                  │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │          만료 키 관리 (Expiration)              │ │
│  │  - Passive: 접근 시 확인                        │ │
│  │  - Active: 초당 10회 샘플링                     │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│                   영속성 계층                          │
│  ┌────────────┐              ┌────────────┐         │
│  │    RDB     │              │    AOF     │         │
│  │  (스냅샷)   │              │ (로그파일)  │         │
│  │  dump.rdb  │              │appendonly  │         │
│  └────────────┘              └────────────┘         │
└──────────────────────────────────────────────────────┘

설명:
- 구성 요소 1: 클라이언트 - 다양한 언어의 Redis 클라이언트
- 구성 요소 2: 명령어 큐 - 들어온 명령을 순서대로 대기
- 구성 요소 3: 싱글 스레드 - 명령을 순차적으로 처리
- 구성 요소 4: 메모리 - Hash Table 기반 초고속 저장소
- 구성 요소 5: 만료 관리 - TTL 기반 자동 삭제
- 구성 요소 6: 영속성 - RDB/AOF로 데이터 백업
- 연결 관계: 클라이언트 → 큐 → 처리 → 메모리 → 디스크
```

---

## 📚 학습 목표

이 장을 완료하면 다음과 같은 능력을 갖게 됩니다:

✅ **Redis CLI의 모든 기능을 자유자재로 사용**
✅ **키-값 쌍의 생성, 조회, 수정, 삭제 완벽 이해**
✅ **키 관리 전략과 베스트 프랙티스 습득**
✅ **TTL(만료시간) 개념과 실무 활용법 마스터**
✅ **여러 데이터베이스 간 전환과 관리**
✅ **실무에서 바로 활용 가능한 Redis 조작 능력**

---

## 🎯 실습 환경 준비

시작하기 전에 Redis가 올바르게 설치되고 실행 중인지 확인하세요.

### 📋 사전 체크리스트

```bash
# 1. Redis 서버 실행 확인
redis-server --version
# 예상 출력: Redis server v=7.2.4 sha=00000000:0 malloc=jemalloc-5.3.0 bits=64 build=c6f3693d78dac998

# 2. Redis 서버 시작 (아직 시작하지 않았다면)
redis-server

# 3. 새 터미널에서 Redis CLI 연결
redis-cli
# 프롬프트가 127.0.0.1:6379> 로 변경되면 성공
```

**⚠️ 주의사항**: 실습 중에는 Redis 서버를 종료하지 마세요. 데이터가 손실될 수 있습니다.

---

## 🏗️ 1. Redis CLI 완전 정복

### 1.1 Redis CLI란 무엇인가?

**Redis CLI(Command Line Interface)**는 Redis 서버와 대화하는 도구입니다.

```
🏪 편의점 계산대 비유:
- Redis CLI = 계산대 직원
- Redis 서버 = 창고
- 사용자 = 고객
- 명령어 = 요청

고객이 "콜라 주세요"라고 하면 → 직원이 창고에서 콜라를 가져옴
사용자가 "GET cola"라고 하면 → CLI가 서버에서 cola 값을 가져옴
```

### 1.2 CLI 시작과 종료

#### 기본 연결
```bash
# 기본 연결 (localhost:6379)
redis-cli

# 특정 호스트와 포트로 연결
redis-cli -h 192.168.1.100 -p 6380

# 인증이 필요한 서버에 연결
redis-cli -h redis.example.com -p 6379 -a mypassword

# 종료
127.0.0.1:6379> exit
# 또는 Ctrl+C
```

#### 연결 상태 확인
```bash
127.0.0.1:6379> ping
PONG

# 연결 정보 확인
127.0.0.1:6379> client list
id=3 addr=127.0.0.1:54321 fd=8 name= age=42 idle=0 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=26 qbuf-free=40928 obl=0 oll=0 omem=0 events=r cmd=client
```

### 1.3 CLI 프롬프트 이해하기

```bash
127.0.0.1:6379>
# │       │    │
# │       │    └─ 현재 데이터베이스 번호 (0~15)
# │       └─ Redis 서버 포트
# └─ Redis 서버 IP 주소
```

### 1.4 명령어 자동완성과 도움말

#### 자동완성 사용법
```bash
# Tab 키를 눌러 자동완성
127.0.0.1:6379> S[Tab]
SADD     SCAN     SCRIPT   SET      SETEX    SETNX    ...

# 부분 입력 후 Tab 키
127.0.0.1:6379> SET[Tab]
SET      SETBIT   SETEX    SETNX    SETRANGE
```

#### 도움말 보기
```bash
# 모든 명령어 목록
127.0.0.1:6379> help

# 특정 명령어 도움말
127.0.0.1:6379> help set
SET key value [EX seconds|PX milliseconds|EXAT timestamp|PXAT milliseconds-timestamp|KEEPTTL] [NX|XX] [GET]
summary: Set the string value of a key
since: 1.0.0
group: string

# 명령어 그룹별 도움말
127.0.0.1:6379> help @string
```

### 1.5 CLI 고급 기능

#### 히스토리 기능
```bash
# 위/아래 화살표로 이전 명령어 검색
# Ctrl+R로 명령어 검색

# 히스토리 파일 위치
# Linux/Mac: ~/.rediscli_history
# Windows: %USERPROFILE%\.rediscli_history
```

#### 배치 모드 실행
```bash
# 단일 명령어 실행
redis-cli SET greeting "Hello Redis"

# 여러 명령어 실행
redis-cli --eval script.lua , key1 key2

# 파이프라인으로 여러 명령어
echo -e "SET key1 value1\nSET key2 value2" | redis-cli
```

---

## 🔑 2. 기본 데이터 저장과 조회 (SET, GET)

### 2.1 SET 명령어 완전 분석

**SET은 Redis의 가장 기본적인 명령어입니다.**

#### 기본 문법
```bash
SET key value [옵션들]
```

#### 기본 사용법
```bash
# 가장 기본적인 사용
127.0.0.1:6379> SET name "김철수"
OK

127.0.0.1:6379> SET age 25
OK

127.0.0.1:6379> SET company "테크 주식회사"
OK
```

**💡 실무 팁**:
- 키 이름은 의미 있게 지으세요: `user:1001:name`, `session:abc123`, `cache:product:5678`
- 한글도 사용 가능하지만, 영문을 권장합니다

### 2.2 GET 명령어로 데이터 조회

```bash
# 저장된 값 조회
127.0.0.1:6379> GET name
"김철수"

127.0.0.1:6379> GET age
"25"

127.0.0.1:6379> GET company
"테크 주식회사"

# 존재하지 않는 키 조회
127.0.0.1:6379> GET nonexistent
(nil)
```

### 2.3 SET 명령어 고급 옵션들

#### EX/PX: 만료시간 설정
```bash
# EX: 초 단위 만료시간
127.0.0.1:6379> SET session "user123" EX 3600
OK
# 1시간(3600초) 후 자동 삭제

# PX: 밀리초 단위 만료시간
127.0.0.1:6379> SET temp_data "임시값" PX 5000
OK
# 5초(5000밀리초) 후 자동 삭제
```

#### NX/XX: 조건부 설정
```bash
# NX: 키가 존재하지 않을 때만 설정
127.0.0.1:6379> SET config "production" NX
OK

127.0.0.1:6379> SET config "development" NX
(nil)  # 이미 존재하므로 설정되지 않음

# XX: 키가 이미 존재할 때만 설정
127.0.0.1:6379> SET config "development" XX
OK  # 이미 존재하므로 업데이트됨

127.0.0.1:6379> SET new_key "new_value" XX
(nil)  # 존재하지 않으므로 설정되지 않음
```

#### GET: 설정하면서 이전 값 반환
```bash
127.0.0.1:6379> SET counter 10
OK

127.0.0.1:6379> SET counter 20 GET
"10"  # 이전 값 반환
```

### 2.4 실제 활용 예제

#### 웹 세션 관리
```bash
# 사용자 로그인 시 세션 생성 (30분 만료)
127.0.0.1:6379> SET session:abc123 "user:1001" EX 1800
OK

# 세션 확인
127.0.0.1:6379> GET session:abc123
"user:1001"

# 세션 연장 (활동 시마다)
127.0.0.1:6379> SET session:abc123 "user:1001" EX 1800
OK
```

#### 캐시 시스템
```bash
# 상품 정보 캐시 (1시간 유효)
127.0.0.1:6379> SET cache:product:1001 '{"name":"노트북","price":1200000,"stock":5}' EX 3600
OK

# 캐시 조회
127.0.0.1:6379> GET cache:product:1001
"{\"name\":\"노트북\",\"price\":1200000,\"stock\":5}"
```

#### 설정 값 관리
```bash
# 시스템 설정 (조건부 설정으로 덮어쓰기 방지)
127.0.0.1:6379> SET config:max_connections 1000 NX
OK

# 이미 설정된 값은 변경되지 않음
127.0.0.1:6379> SET config:max_connections 2000 NX
(nil)
```

---

## 🏢 실무 활용 사례

### 실제 기업 활용 사례

#### 사례 1: Twitter (트위터)
```bash
# 사용 목적: 타임라인 캐싱 및 세션 관리
# 규모: 초당 300,000+ GET/SET 연산
# 효과: 응답 시간 98% 단축 (500ms → 10ms)

# 구현 예시
# 사용자 타임라인 캐시 (5분)
SETEX timeline:user:12345 300 '[{"id":1,"text":"Hello"},{"id":2,"text":"World"}]'

# 트윗 조회수 카운터 (다음 장에서 INCR 학습)
SET tweet:99999:views 1500000

# 성과
# - 응답 시간: 500ms → 10ms (98% 개선)
# - DB 부하: 90% 감소
# - 동시 접속자: 5,000 → 50,000 처리 가능
```

#### 사례 2: 카카오톡 (한국)
```bash
# 사용 목적: 사용자 온라인 상태 관리
# 규모: 5천만 사용자, 실시간 상태 추적
# 효과: 실시간 상태 업데이트, DB 쿼리 제거

# 구현 예시
# 사용자 온라인 상태 (5분 TTL, 활동 시 갱신)
SETEX online:user:kim123 300 "active"
SETEX online:user:lee456 300 "active"

# 마지막 접속 시간
SET last_seen:kim123 "2024-01-15 14:30:00"

# 읽지 않은 메시지 수 (다음 장에서 INCR 학습)
SET unread:kim123 5

# 성과
# - 상태 확인 쿼리: 100% 제거
# - 실시간성: 5분 이내 정확한 상태
# - DB 부하: 80% 감소
```

#### 사례 3: Instagram (인스타그램)
```bash
# 사용 목적: 피드 캐싱 및 세션 관리
# 규모: 10억+ 사용자, 수백만 QPS
# 효과: 피드 로딩 속도 95% 향상

# 구현 예시
# 사용자 피드 캐시 (10분)
SETEX feed:user:999 600 '[{"post_id":1,"image":"url1"},{"post_id":2,"image":"url2"}]'

# 사용자 프로필 캐시 (1시간)
SETEX profile:user:999 3600 '{"username":"john","followers":5000,"following":300}'

# 세션 토큰 (2시간)
SETEX session:abc123xyz 7200 '{"user_id":999,"device":"mobile","ip":"192.168.1.1"}'

# 성과
# - 피드 로딩: 2초 → 100ms (95% 개선)
# - 인프라 비용: 연간 $2M 절감
# - DB 쿼리: 70% 감소
```

#### 사례 4: 배달의민족 (한국)
```bash
# 사용 목적: 실시간 주문 상태 관리 및 라이더 위치 추적
# 규모: 일 주문 500만+, 실시간 라이더 10만+
# 효과: 실시간 주문 추적, 고객 만족도 30% 향상

# 구현 예시
# 주문 상태 (10분간 유효, 결제 전까지)
SETEX order:temp:abc123 600 '{"restaurant":"피자집","items":["피자","콜라"],"price":25000}'

# 결제 완료 후 주문 (배달 완료까지 영구)
SET order:confirmed:abc123 '{"status":"배달중","rider":"김라이더","eta":"15분"}'

# 라이더 현재 위치 (30초마다 갱신)
SETEX rider:location:kim123 30 '{"lat":37.5665,"lng":126.9780,"heading":"north"}'

# 실시간 알림 토큰 (1시간)
SETEX push_token:user:lee456 3600 "fcm_token_xyz789"

# 성과
# - 주문 추적 정확도: 실시간 (0초 지연)
# - DB 쿼리: 85% 감소
# - 고객 만족도: 30% 향상
# - 라이더 효율: 20% 개선
```

#### 사례 5: GitHub (깃허브)
```bash
# 사용 목적: API Rate Limiting (속도 제한)
# 규모: 시간당 5,000 요청 제한 (인증된 사용자)
# 효과: API 남용 방지, 서버 안정성 99.9%

# 구현 예시
# API 속도 제한 (1시간 = 3600초)
SETEX rate_limit:api:user:john:2024-01-15-14 3600 1

# 요청할 때마다 증가 (다음 장에서 INCR 학습)
# INCR rate_limit:api:user:john:2024-01-15-14
# 현재 요청 수 확인
GET rate_limit:api:user:john:2024-01-15-14
# "1" (아직 1번만 요청함)

# 1시간 후 자동으로 리셋됨

# 성과
# - API 남용 차단: 100% 자동화
# - 서버 다운타임: 0%
# - DDoS 공격 방어: 자동 차단
```

### 일반적인 활용 패턴

#### 패턴 1: 세션 관리 패턴
**사용 시기**: 사용자 로그인 세션 관리

**구현 방법**:
```bash
# 로그인 시 세션 생성 (30분 TTL)
SETEX session:user:1001 1800 '{"user_id":1001,"username":"kim","role":"admin","login_time":"2024-01-15 14:00"}'

# 사용자 활동 시마다 세션 연장
EXPIRE session:user:1001 1800

# 세션 조회
GET session:user:1001

# 로그아웃 시 즉시 삭제
DEL session:user:1001
```

**실무 주의사항**:
- ⚠️ 주의 1: 민감한 정보(비밀번호)는 세션에 저장하지 말 것
- ⚠️ 주의 2: TTL은 보안 정책에 맞게 설정 (보통 15~60분)
- ⚠️ 주의 3: 여러 디바이스 로그인 시 세션 키 구분 필요

#### 패턴 2: 캐시 Aside 패턴
**사용 시기**: DB 조회 결과 캐싱

**구현 방법**:
```bash
# 1. 캐시 확인
GET cache:product:1001

# 2. 캐시 없으면 (nil)
# → DB에서 조회
# → 캐시에 저장 (5분 TTL)
SETEX cache:product:1001 300 '{"id":1001,"name":"노트북","price":1200000}'

# 3. 다음 요청부터는 캐시에서 바로 반환
GET cache:product:1001

# 4. 데이터 변경 시 캐시 무효화
DEL cache:product:1001
```

**실무 주의사항**:
- ⚠️ 주의 1: 캐시 TTL은 데이터 특성에 맞게 설정
  - 상품 정보: 5~10분
  - API 응답: 1~5분
  - 통계 데이터: 10~30분
- ⚠️ 주의 2: 데이터 변경 시 캐시 무효화 필수
- ⚠️ 주의 3: 캐시 키 명명 규칙 일관성 유지

#### 패턴 3: 임시 데이터 저장 패턴
**사용 시기**: 이메일 인증, 비밀번호 재설정 등

**구현 방법**:
```bash
# 이메일 인증 코드 생성 (10분 유효)
SETEX verify:email:kim@example.com 600 "123456"

# 사용자가 인증 코드 입력
GET verify:email:kim@example.com
# "123456" 반환되면 인증 성공

# 인증 완료 후 즉시 삭제
DEL verify:email:kim@example.com

# 비밀번호 재설정 토큰 (1시간 유효)
SETEX reset_password:token:abc123 3600 "user:1001"
```

**실무 주의사항**:
- ⚠️ 주의 1: 인증 코드는 충분히 랜덤하게 생성 (최소 6자리)
- ⚠️ 주의 2: TTL 만료 후 자동 삭제로 보안 강화
- ⚠️ 주의 3: 토큰은 추측 불가능한 UUID 사용 권장

### 성능 비교

| 방법 | 응답시간 | 처리량 | 메모리 | 비용 | 적용 사례 |
|------|----------|--------|--------|------|----------|
| **직접 DB 쿼리** | 100ms | 100/s | 0MB | $500/월 | 초기 개발 |
| **Redis 캐시** | 1ms | 10,000/s | 100MB | $150/월 | Twitter, Instagram |
| **개선** | **99%↓** | **100배↑** | **+100MB** | **70%↓** | 대부분 서비스 |

**실제 벤치마크 결과**:
```bash
# 테스트 환경: AWS EC2 t3.medium, Redis 7.0
# 데이터: 100만 개 키-값 쌍

# DB 쿼리 (MySQL)
평균 응답 시간: 95ms
처리량: 105 req/s
에러율: 0.2%

# Redis GET
평균 응답 시간: 0.8ms
처리량: 12,500 req/s
에러율: 0%

# 개선율
속도: 118배 향상
처리량: 119배 향상
에러율: 100% 감소
```

---

## 🔍 3. 키 관리 명령어 (KEYS, EXISTS, DEL)

### 3.1 KEYS 명령어 - 키 패턴 검색

**KEYS는 패턴에 맞는 모든 키를 찾는 명령어입니다.**

#### 기본 문법
```bash
KEYS pattern
```

#### 패턴 문법
- `*`: 모든 문자 (0개 이상)
- `?`: 단일 문자
- `[]`: 문자 집합
- `\`: 이스케이프 문자

#### 실습 데이터 준비
```bash
# 다양한 키들을 생성해보겠습니다
127.0.0.1:6379> SET user:1001:name "김철수"
OK
127.0.0.1:6379> SET user:1001:email "kim@example.com"
OK
127.0.0.1:6379> SET user:1002:name "이영희"
OK
127.0.0.1:6379> SET user:1002:email "lee@example.com"
OK
127.0.0.1:6379> SET product:2001:name "노트북"
OK
127.0.0.1:6379> SET product:2001:price "1200000"
OK
127.0.0.1:6379> SET session:abc123 "active"
OK
127.0.0.1:6379> SET session:def456 "active"
OK
127.0.0.1:6379> SET cache:homepage "html_content"
OK
127.0.0.1:6379> SET temp_data_1 "임시1"
OK
127.0.0.1:6379> SET temp_data_2 "임시2"
OK
```

#### KEYS 명령어 활용
```bash
# 모든 키 조회
127.0.0.1:6379> KEYS *
 1) "user:1002:email"
 2) "product:2001:name"
 3) "user:1001:name"
 4) "session:def456"
 5) "temp_data_2"
 6) "cache:homepage"
 7) "user:1002:name"
 8) "session:abc123"
 9) "product:2001:price"
10) "user:1001:email"
11) "temp_data_1"

# 특정 패턴으로 검색
127.0.0.1:6379> KEYS user:*
1) "user:1002:email"
2) "user:1001:name"
3) "user:1002:name"
4) "user:1001:email"

127.0.0.1:6379> KEYS *:name
1) "product:2001:name"
2) "user:1001:name"
3) "user:1002:name"

127.0.0.1:6379> KEYS session:*
1) "session:def456"
2) "session:abc123"

# 단일 문자 패턴
127.0.0.1:6379> KEYS temp_data_?
1) "temp_data_2"
2) "temp_data_1"

# 문자 집합 패턴
127.0.0.1:6379> KEYS user:100[12]:*
1) "user:1002:email"
2) "user:1001:name"
3) "user:1002:name"
4) "user:1001:email"
```

**⚠️ 성능 주의사항**:
- `KEYS *`는 모든 키를 스캔하므로 운영환경에서는 사용 금지
- 대신 `SCAN` 명령어 사용 권장 (나중에 학습)

### 3.2 EXISTS 명령어 - 키 존재 여부 확인

```bash
# 단일 키 존재 확인
127.0.0.1:6379> EXISTS user:1001:name
(integer) 1  # 존재함

127.0.0.1:6379> EXISTS user:9999:name
(integer) 0  # 존재하지 않음

# 여러 키 동시 확인
127.0.0.1:6379> EXISTS user:1001:name user:1002:name nonexistent
(integer) 2  # 3개 중 2개 존재

# 실무 활용: 조건부 로직
127.0.0.1:6379> EXISTS cache:product:1001
(integer) 0
# 캐시가 없으면 데이터베이스에서 조회 후 캐시 생성
```

### 3.3 DEL 명령어 - 키 삭제

```bash
# 단일 키 삭제
127.0.0.1:6379> DEL temp_data_1
(integer) 1  # 삭제된 키 개수

127.0.0.1:6379> DEL temp_data_1
(integer) 0  # 이미 없으므로 0 반환

# 여러 키 동시 삭제
127.0.0.1:6379> DEL temp_data_2 session:abc123 session:def456
(integer) 3  # 3개 키 삭제됨

# 패턴으로 삭제 (조심스럽게!)
# 먼저 확인
127.0.0.1:6379> KEYS user:1002:*
1) "user:1002:email"
2) "user:1002:name"

# 삭제 실행
127.0.0.1:6379> DEL user:1002:email user:1002:name
(integer) 2
```

### 3.4 키 관리 베스트 프랙티스

#### 명명 규칙
```bash
# 좋은 예: 계층적 구조
user:1001:profile
user:1001:settings:theme
product:electronics:laptop:1001
cache:api:user_list:page_1

# 나쁜 예: 일관성 없는 구조
user1001profile
UserProfile1001
user_profile_1001_data
```

#### 키 삭제 시 주의사항
```bash
# 삭제 전 반드시 확인
127.0.0.1:6379> KEYS session:*
127.0.0.1:6379> # 결과 확인 후 삭제

# 운영환경에서는 백업 후 삭제
127.0.0.1:6379> GET important_data
"중요한 데이터"
127.0.0.1:6379> DEL important_data
(integer) 1
```

---

## ⏰ 4. TTL과 만료 시간 설정

### 4.1 TTL(Time To Live) 개념 이해

**TTL은 데이터의 생존 시간입니다.**

```
🥛 우유 유통기한 비유:
- 우유 = Redis 데이터
- 유통기한 = TTL
- 유통기한 지나면 자동 폐기 = TTL 만료 시 자동 삭제

Redis에서는 설정한 시간이 지나면 데이터가 자동으로 삭제됩니다.
```

### 4.2 만료시간 설정 명령어들

#### EXPIRE: 초 단위 만료시간 설정
```bash
# 기존 키에 만료시간 설정
127.0.0.1:6379> SET message "안녕하세요"
OK

127.0.0.1:6379> EXPIRE message 10
(integer) 1  # 10초 후 삭제

# 10초 후...
127.0.0.1:6379> GET message
(nil)  # 삭제됨
```

#### EXPIREAT: 특정 시점에 만료
```bash
# Unix 타임스탬프로 만료시간 설정
127.0.0.1:6379> SET event "새해 이벤트"
OK

# 2024년 1월 1일 00:00:00에 만료 (예시 타임스탬프)
127.0.0.1:6379> EXPIREAT event 1704067200
(integer) 1
```

#### PEXPIRE: 밀리초 단위 만료시간
```bash
127.0.0.1:6379> SET quick_data "빠른 데이터"
OK

127.0.0.1:6379> PEXPIRE quick_data 5000
(integer) 1  # 5초(5000밀리초) 후 삭제
```

#### SETEX: 설정과 동시에 만료시간 지정
```bash
# SET + EXPIRE를 한 번에
127.0.0.1:6379> SETEX temp_token "abc123" 300
OK  # 5분(300초) 후 삭제

# 위 명령어는 아래와 동일
# SET temp_token "abc123"
# EXPIRE temp_token 300
```

### 4.3 TTL 조회 명령어들

#### TTL: 남은 시간 조회 (초)
```bash
127.0.0.1:6379> SETEX countdown "시작!" 60
OK

127.0.0.1:6379> TTL countdown
(integer) 58  # 58초 남음

127.0.0.1:6379> TTL countdown
(integer) 45  # 45초 남음

# 만료된 후
127.0.0.1:6379> TTL countdown
(integer) -2  # 키가 존재하지 않음

# 만료시간이 없는 키
127.0.0.1:6379> SET permanent "영구 데이터"
OK
127.0.0.1:6379> TTL permanent
(integer) -1  # 만료시간 없음
```

#### PTTL: 남은 시간 조회 (밀리초)
```bash
127.0.0.1:6379> SETEX precise_timer "정밀 타이머" 10
OK

127.0.0.1:6379> PTTL precise_timer
(integer) 8234  # 8234밀리초 남음
```

### 4.4 만료시간 제거와 수정

#### PERSIST: 만료시간 제거
```bash
127.0.0.1:6379> SETEX temp_data "임시 데이터" 60
OK

127.0.0.1:6379> TTL temp_data
(integer) 57

127.0.0.1:6379> PERSIST temp_data
(integer) 1  # 성공

127.0.0.1:6379> TTL temp_data
(integer) -1  # 만료시간 없음 (영구 보존)
```

#### 만료시간 수정
```bash
# 기존 만료시간 덮어쓰기
127.0.0.1:6379> SETEX data "테스트" 60
OK

127.0.0.1:6379> TTL data
(integer) 58

127.0.0.1:6379> EXPIRE data 120
(integer) 1  # 2분으로 연장

127.0.0.1:6379> TTL data
(integer) 119
```

### 4.5 실무 활용 패턴

#### 세션 관리
```bash
# 로그인 시 세션 생성 (30분)
127.0.0.1:6379> SETEX session:user123 1800 '{"user_id":123,"role":"user"}'
OK

# 활동 시마다 세션 연장
127.0.0.1:6379> EXPIRE session:user123 1800
(integer) 1

# 로그아웃 시 즉시 삭제
127.0.0.1:6379> DEL session:user123
(integer) 1
```

#### 캐시 관리
```bash
# API 응답 캐시 (5분)
127.0.0.1:6379> SETEX cache:api:users 300 '[{"id":1,"name":"김철수"},{"id":2,"name":"이영희"}]'
OK

# 데이터 변경 시 캐시 무효화
127.0.0.1:6379> DEL cache:api:users
(integer) 1
```

#### 임시 토큰 관리
```bash
# 이메일 인증 토큰 (10분)
127.0.0.1:6379> SETEX verify:email:kim@example.com 600 "abc123def456"
OK

# 비밀번호 재설정 토큰 (1시간)
127.0.0.1:6379> SETEX reset:password:789 3600 "xyz789abc123"
OK
```

#### Rate Limiting (속도 제한)
```bash
# IP별 API 호출 제한 (1분간 100회)
127.0.0.1:6379> SETEX rate_limit:192.168.1.100 60 1
OK

# 호출할 때마다 카운터 증가 (후에 INCR 명령어로 학습)
```

---

## 🗂️ 5. Redis 데이터베이스 선택

### 5.1 Redis 데이터베이스 개념

**Redis는 기본적으로 16개의 논리적 데이터베이스를 제공합니다.**

```
🏢 아파트 비유:
- Redis 서버 = 아파트 건물
- 데이터베이스 = 각 층 (0층~15층)
- 키-값 쌍 = 각 층의 가구들

각 층은 독립적이며, 0층의 '냉장고'와 1층의 '냉장고'는 완전히 다른 물건입니다.
```

### 5.2 데이터베이스 번호 체계

```bash
데이터베이스 번호: 0 ~ 15 (총 16개)
기본 데이터베이스: 0번
```

#### 현재 데이터베이스 확인
```bash
# CLI 프롬프트에서 확인
127.0.0.1:6379>
#           └─ 현재 0번 데이터베이스

# 명령어로 확인
127.0.0.1:6379> CLIENT LIST
id=3 addr=127.0.0.1:54321 ... db=0 ...
#                              └─ 현재 데이터베이스 번호
```

### 5.3 SELECT 명령어 - 데이터베이스 전환

```bash
# 1번 데이터베이스로 전환
127.0.0.1:6379> SELECT 1
OK
127.0.0.1:6379[1]>
#              └─ 1번 데이터베이스임을 표시

# 5번 데이터베이스로 전환
127.0.0.1:6379[1]> SELECT 5
OK
127.0.0.1:6379[5]>

# 0번 데이터베이스로 돌아가기
127.0.0.1:6379[5]> SELECT 0
OK
127.0.0.1:6379>
```

### 5.4 데이터베이스별 데이터 격리 확인

```bash
# 0번 데이터베이스에 데이터 저장
127.0.0.1:6379> SET greeting "안녕하세요"
OK

127.0.0.1:6379> SET counter 100
OK

# 1번 데이터베이스로 전환
127.0.0.1:6379> SELECT 1
OK

# 1번 데이터베이스에서는 0번의 데이터를 볼 수 없음
127.0.0.1:6379[1]> GET greeting
(nil)

127.0.0.1:6379[1]> GET counter
(nil)

# 1번 데이터베이스에 다른 데이터 저장
127.0.0.1:6379[1]> SET greeting "Hello"
OK

127.0.0.1:6379[1]> SET counter 200
OK

# 0번 데이터베이스로 돌아가서 확인
127.0.0.1:6379[1]> SELECT 0
OK

127.0.0.1:6379> GET greeting
"안녕하세요"  # 0번 데이터베이스의 값

127.0.0.1:6379> GET counter
"100"  # 0번 데이터베이스의 값
```

### 5.5 각 데이터베이스 정보 확인

#### DBSIZE: 현재 데이터베이스 키 개수
```bash
127.0.0.1:6379> DBSIZE
(integer) 2  # 0번 데이터베이스에 2개 키

127.0.0.1:6379> SELECT 1
OK

127.0.0.1:6379[1]> DBSIZE
(integer) 2  # 1번 데이터베이스에 2개 키
```

#### INFO keyspace: 모든 데이터베이스 정보
```bash
127.0.0.1:6379> INFO keyspace
# Keyspace
db0:keys=2,expires=0,avg_ttl=0
db1:keys=2,expires=0,avg_ttl=0
# │   │       │         └─ 평균 TTL
# │   │       └─ 만료시간이 설정된 키 개수
# │   └─ 총 키 개수
# └─ 데이터베이스 번호
```

### 5.6 데이터베이스 관리 명령어

#### FLUSHDB: 현재 데이터베이스 모든 데이터 삭제
```bash
127.0.0.1:6379[1]> KEYS *
1) "greeting"
2) "counter"

127.0.0.1:6379[1]> FLUSHDB
OK

127.0.0.1:6379[1]> KEYS *
(empty array)

# 다른 데이터베이스는 영향 없음
127.0.0.1:6379[1]> SELECT 0
OK

127.0.0.1:6379> KEYS *
1) "greeting"
2) "counter"
```

#### FLUSHALL: 모든 데이터베이스 데이터 삭제
```bash
⚠️ 위험: 이 명령어는 모든 데이터베이스의 모든 데이터를 삭제합니다!

127.0.0.1:6379> FLUSHALL
OK

127.0.0.1:6379> KEYS *
(empty array)

127.0.0.1:6379> SELECT 1
OK

127.0.0.1:6379[1]> KEYS *
(empty array)
```

### 5.7 실무에서의 데이터베이스 활용 패턴

#### 환경별 분리
```bash
# 0번: 개발환경 데이터
SELECT 0
SET config:environment "development"
SET debug:enabled "true"

# 1번: 테스트환경 데이터
SELECT 1
SET config:environment "test"
SET debug:enabled "false"

# 2번: 캐시 데이터
SELECT 2
SET cache:user:1001 "user_data"
SET cache:product:2001 "product_data"
```

#### 기능별 분리
```bash
# 0번: 세션 데이터
SELECT 0
SET session:abc123 "user_session_data"

# 1번: 큐 데이터
SELECT 1
LPUSH job:queue "email_task"

# 2번: 통계 데이터
SELECT 2
SET stats:daily:2024-01-01 "statistics_data"
```

#### 권한별 분리
```bash
# 0번: 일반 사용자 데이터
SELECT 0
SET user:normal:1001 "user_data"

# 1번: 관리자 데이터
SELECT 1
SET admin:config "admin_settings"
```

---

## 🛠️ 실전 프로젝트

### 프로젝트: Redis 기반 세션 관리 시스템

**난이도**: ⭐⭐☆☆☆
**예상 소요 시간**: 1-2시간
**학습 목표**: 실무에서 가장 많이 사용하는 세션 관리 시스템을 Redis로 완벽하게 구현

### 요구사항 분석

#### 기능 요구사항
- [ ] 기능 1: 사용자 로그인 시 세션 생성
- [ ] 기능 2: 세션 유효성 검증
- [ ] 기능 3: 사용자 활동 시 세션 자동 연장
- [ ] 기능 4: 로그아웃 시 세션 삭제
- [ ] 기능 5: 만료된 세션 자동 정리

#### 기술 요구사항
- [ ] 기술 1: Redis SET/GET 명령어 활용
- [ ] 기술 2: TTL 기반 자동 만료 구현
- [ ] 기술 3: 세션 키 명명 규칙 준수
- [ ] 기술 4: 다중 디바이스 로그인 지원

#### 비기능 요구사항
- [ ] 성능: 세션 조회 1ms 이내
- [ ] 보안: 30분 무활동 시 자동 로그아웃
- [ ] 확장성: 수백만 동시 세션 지원 가능

### 프로젝트 구조

```
session-management/
├── 1_login.redis          # 로그인 및 세션 생성
├── 2_validate.redis       # 세션 검증
├── 3_extend.redis         # 세션 연장
├── 4_logout.redis         # 로그아웃
├── 5_cleanup.redis        # 정리 및 모니터링
└── README.md              # 프로젝트 설명
```

### 설계 의사결정

#### 왜 이렇게 설계했는가?

1. **결정 1: TTL 30분 설정**
   - 이유: 보안(무활동 시 자동 로그아웃)과 UX(적당한 세션 시간) 균형
   - 대안: 15분(너무 짧음), 60분(보안 위험), 무제한(매우 위험)
   - 선택 근거: 업계 표준이 30분, 대부분의 서비스가 채택

2. **결정 2: SETEX 사용 (SET + EXPIRE 대신)**
   - 이유: 원자적 연산으로 안전성 보장
   - 대안: SET 후 EXPIRE (두 명령 사이 장애 위험)
   - 선택 근거: 네트워크/서버 장애 시에도 TTL 보장

3. **결정 3: session:user:{user_id} 키 구조**
   - 이유: 사용자별로 세션 식별 및 관리 용이
   - 대안: session:{random_token} (사용자 찾기 어려움)
   - 선택 근거: 관리자가 특정 사용자 세션 쉽게 조회 가능

### 단계별 구현 가이드

#### 1단계: 로그인 및 세션 생성

**시나리오**: 사용자가 로그인하면 세션을 생성하고 30분 TTL 설정

```bash
# 파일: 1_login.redis

# 사용자 로그인 (user_id: 1001, username: kim)
# 세션 데이터를 JSON 형태로 저장 (30분 TTL)
SETEX session:user:1001 1800 '{"user_id":1001,"username":"kim","role":"user","login_time":"2024-01-15 14:00:00","device":"desktop","ip":"192.168.1.100"}'
# 예상 출력: OK

# 세션 생성 확인
GET session:user:1001
# 예상 출력: {"user_id":1001,"username":"kim","role":"user","login_time":"2024-01-15 14:00:00","device":"desktop","ip":"192.168.1.100"}

# 남은 세션 시간 확인
TTL session:user:1001
# 예상 출력: (integer) 1798  (약 30분)

# 다른 사용자 로그인 (user_id: 1002)
SETEX session:user:1002 1800 '{"user_id":1002,"username":"lee","role":"admin","login_time":"2024-01-15 14:05:00","device":"mobile","ip":"192.168.1.101"}'
# 예상 출력: OK
```

**체크포인트**:
- [ ] 세션이 정상적으로 생성됨
- [ ] TTL이 1800초(30분)로 설정됨
- [ ] 세션 데이터를 조회할 수 있음

#### 2단계: 세션 유효성 검증

**시나리오**: API 요청 시마다 세션이 유효한지 확인

```bash
# 파일: 2_validate.redis

# 세션 존재 여부 확인
EXISTS session:user:1001
# 예상 출력: (integer) 1  (존재함)

EXISTS session:user:9999
# 예상 출력: (integer) 0  (존재하지 않음 = 로그인 안함)

# 세션 데이터 조회 및 검증
GET session:user:1001
# 예상 출력: {"user_id":1001,...}
# 반환되면 → 로그인 상태
# (nil) 반환되면 → 비로그인 상태 또는 세션 만료

# 여러 세션 한 번에 확인
EXISTS session:user:1001 session:user:1002 session:user:1003
# 예상 출력: (integer) 2  (1001, 1002만 존재)

# 세션 남은 시간 확인
TTL session:user:1001
# 예상 출력: (integer) 1650  (약 27.5분 남음)

# 만료된 세션 확인
TTL session:user:expired
# 예상 출력: (integer) -2  (키가 존재하지 않음)
```

**코드 설명**:
- **EXISTS**: 세션 존재 여부만 빠르게 확인 (O(1))
- **GET**: 세션 데이터 전체를 가져와서 상세 검증 (권한 등)
- **TTL**: 세션 만료까지 남은 시간 확인
- **-2**: 키 없음 (세션 만료 또는 미로그인)
- **-1**: 영구 키 (세션에서는 발생하면 안됨!)

#### 3단계: 사용자 활동 시 세션 자동 연장

**시나리오**: 사용자가 페이지를 클릭할 때마다 세션 시간 30분으로 재설정

```bash
# 파일: 3_extend.redis

# 방법 1: EXPIRE로 TTL 갱신 (추천)
# 사용자가 활동(클릭, API 호출 등)을 하면
EXPIRE session:user:1001 1800
# 예상 출력: (integer) 1  (TTL 갱신 성공)

# 갱신 확인
TTL session:user:1001
# 예상 출력: (integer) 1798  (다시 30분)

# 방법 2: SETEX로 덮어쓰기 (비추천)
# 세션 데이터를 다시 가져와서 저장해야 함
GET session:user:1001
# → 반환된 데이터를 그대로 다시 저장
SETEX session:user:1001 1800 '{"user_id":1001,"username":"kim",...}'
# 예상 출력: OK
# 문제점: GET + SETEX 두 번의 명령, 네트워크 왕복 증가

# 활동 로그 기록 (선택 사항)
SET last_activity:user:1001 "2024-01-15 14:30:00"
# 예상 출력: OK
```

**코드 설명**:
- **방법 1 (EXPIRE)**: 기존 세션 데이터 유지하고 TTL만 갱신 (효율적)
- **방법 2 (SETEX)**: 세션 데이터 전체를 다시 저장 (비효율적)
- **best practice**: EXPIRE 사용 권장

#### 4단계: 로그아웃 및 세션 삭제

**시나리오**: 사용자가 로그아웃 버튼을 누르면 즉시 세션 삭제

```bash
# 파일: 4_logout.redis

# 로그아웃 전 세션 확인
GET session:user:1001
# 예상 출력: {"user_id":1001,...}

# 로그아웃 - 세션 즉시 삭제
DEL session:user:1001
# 예상 출력: (integer) 1  (삭제됨)

# 로그아웃 확인
GET session:user:1001
# 예상 출력: (nil)  (세션 없음)

EXISTS session:user:1001
# 예상 출력: (integer) 0  (존재하지 않음)

# 여러 디바이스에서 로그인한 경우 모두 로그아웃
# (키 구조: session:user:{user_id}:{device})
DEL session:user:1002:desktop session:user:1002:mobile session:user:1002:tablet
# 예상 출력: (integer) 3  (3개 세션 모두 삭제)

# 관리자가 특정 사용자 강제 로그아웃
DEL session:user:1003
# 예상 출력: (integer) 1
```

#### 5단계: 모니터링 및 정리

**시나리오**: 현재 활성 세션 수 확인 및 모니터링

```bash
# 파일: 5_cleanup.redis

# 모든 활성 세션 확인 (개발 환경에서만!)
KEYS session:user:*
# 예상 출력:
# 1) "session:user:1002"
# ⚠️ 운영 환경에서는 SCAN 사용!

# 활성 세션 개수 확인 (총 키 개수)
DBSIZE
# 예상 출력: (integer) 5  (세션 외 다른 키 포함)

# 특정 사용자 세션만 검색
SCAN 0 MATCH session:user:* COUNT 100
# 예상 출력:
# 1) "0"  (커서, 0이면 검색 완료)
# 2) 1) "session:user:1002"

# 세션 정보 상세 조회
# 사용자 1002의 세션 상세 정보
GET session:user:1002
TTL session:user:1002
# 예상 출력:
# {"user_id":1002,"username":"lee",...}
# (integer) 1200  (20분 남음)

# 전체 세션 통계 (스크립트로 구현 필요)
# 활성 세션 수: SCAN으로 session:user:* 패턴 카운트
# 평균 TTL: 모든 세션 TTL의 평균값
```

### 전체 시나리오 실행 예시

```bash
# === 시나리오: 사용자 로그인부터 로그아웃까지 ===

# 1. 사용자 kim이 로그인 (14:00)
SETEX session:user:1001 1800 '{"user_id":1001,"username":"kim","login_time":"2024-01-15 14:00"}'
# OK

# 2. 2분 후 (14:02) - 세션 확인
GET session:user:1001
# 반환: {...}
TTL session:user:1001
# (integer) 1680  (28분 남음)

# 3. 10분 후 (14:10) - 사용자가 페이지 클릭 (세션 연장)
EXPIRE session:user:1001 1800
# (integer) 1

# 4. 연장 확인
TTL session:user:1001
# (integer) 1798  (다시 30분)

# 5. 15분 후 (14:25) - 사용자가 로그아웃
DEL session:user:1001
# (integer) 1

# 6. 로그아웃 확인
GET session:user:1001
# (nil)  → 세션 없음, 로그인 필요
```

### 실행 결과 화면

```
127.0.0.1:6379> SETEX session:user:1001 1800 '{"user_id":1001,"username":"kim"}'
OK

127.0.0.1:6379> GET session:user:1001
"{\"user_id\":1001,\"username\":\"kim\"}"

127.0.0.1:6379> TTL session:user:1001
(integer) 1795

127.0.0.1:6379> EXPIRE session:user:1001 1800
(integer) 1

127.0.0.1:6379> DEL session:user:1001
(integer) 1

127.0.0.1:6379> GET session:user:1001
(nil)
```

### 트러블슈팅

#### 문제 1: 세션이 저장되지 않음

**증상**:
```
127.0.0.1:6379> SETEX session:user:1001 1800 "data"
(error) OOM command not allowed when used memory > 'maxmemory'
```

**원인**: Redis 메모리 부족

**해결 방법**:
```bash
# 1. 메모리 사용량 확인
INFO memory

# 2. 불필요한 키 삭제
DEL old:data:*

# 3. maxmemory 설정 확인 및 조정
# redis.conf에서 maxmemory 증가
```

#### 문제 2: TTL이 자동으로 리셋되지 않음

**증상**:
```bash
SET session:user:1001 "data"
EXPIRE session:user:1001 1800
# 나중에 SET으로 덮어쓰면
SET session:user:1001 "new_data"
TTL session:user:1001
# (integer) -1  ← TTL 사라짐!
```

**원인**: SET 명령은 기존 TTL을 제거함

**해결 방법**:
```bash
# ✅ 해결책 1: SETEX 사용
SETEX session:user:1001 1800 "new_data"

# ✅ 해결책 2: SET + KEEPTTL 옵션 (Redis 6.0+)
SET session:user:1001 "new_data" KEEPTTL

# ✅ 해결책 3: SET 후 EXPIRE
SET session:user:1001 "new_data"
EXPIRE session:user:1001 1800
```

### 확장 아이디어

#### 추가 기능 1: 다중 디바이스 로그인 지원
**난이도**: ⭐⭐⭐☆☆
**구현 힌트**:
```bash
# 키 구조 변경: session:user:{user_id}:{device_id}
SETEX session:user:1001:desktop 1800 "session_data"
SETEX session:user:1001:mobile 1800 "session_data"

# 한 사용자의 모든 디바이스 세션 조회
SCAN 0 MATCH session:user:1001:* COUNT 10

# 특정 디바이스만 로그아웃
DEL session:user:1001:desktop
```

#### 추가 기능 2: 세션 활동 로그
**난이도**: ⭐⭐⭐⭐☆
**구현 힌트**:
```bash
# 마지막 활동 시간 기록
SET last_activity:user:1001 "2024-01-15 14:30:00"

# 로그인 횟수 카운터 (다음 장에서 INCR 학습)
SET login_count:user:1001 5
```

#### 추가 기능 3: 세션 도용 방지
**난이도**: ⭐⭐⭐⭐⭐
**구현 힌트**:
```bash
# IP 주소와 User-Agent 검증
SETEX session:user:1001 1800 '{"user_id":1001,"ip":"192.168.1.100","user_agent":"Mozilla/5.0..."}'

# 요청마다 IP 확인
# GET session:user:1001 → IP 비교 → 다르면 강제 로그아웃
```

### 코드 리뷰 포인트

#### 체크리스트
- [ ] TTL이 모든 세션에 설정되었는가?
- [ ] SETEX를 사용하여 원자적으로 저장하는가?
- [ ] 키 명명 규칙이 일관성 있는가? (session:user:{id})
- [ ] 로그아웃 시 세션이 확실히 삭제되는가?
- [ ] 민감한 정보(비밀번호)가 세션에 없는가?
- [ ] 운영 환경에서 KEYS 대신 SCAN을 사용하는가?
- [ ] 세션 데이터가 JSON 형태로 구조화되었는가?

---

## 🔄 6. 실전 연습 및 종합 실습

### 6.1 시나리오 1: 간단한 방문자 카운터

```bash
# 웹사이트 방문자 수 관리
127.0.0.1:6379> SET visitors:today 0
OK

# 방문자가 올 때마다 (INCR은 다음 장에서 자세히)
127.0.0.1:6379> SET visitors:today 1
OK

# 다시 방문자 증가
127.0.0.1:6379> GET visitors:today
"1"

# 새로운 값으로 업데이트
127.0.0.1:6379> SET visitors:today 2
OK

# 자정에 초기화하기 위해 만료시간 설정
127.0.0.1:6379> EXPIRE visitors:today 86400
(integer) 1  # 24시간(86400초) 후 삭제
```

### 6.2 시나리오 2: 사용자 상태 관리

```bash
# 사용자 온라인 상태 관리 (5분간 활동 없으면 오프라인)
127.0.0.1:6379> SETEX user:1001:online "true" 300
OK

# 사용자 활동 시마다 상태 갱신
127.0.0.1:6379> SETEX user:1001:online "true" 300
OK

# 온라인 상태 확인
127.0.0.1:6379> GET user:1001:online
"true"

# 5분 후 자동으로 오프라인 상태가 됨 (키가 삭제됨)
127.0.0.1:6379> GET user:1001:online
(nil)  # 오프라인
```

### 6.3 시나리오 3: 게임 점수 시스템

```bash
# 게임 점수 저장
127.0.0.1:6379> SET game:player:1001:score 1500
OK

127.0.0.1:6379> SET game:player:1002:score 2300
OK

127.0.0.1:6379> SET game:player:1003:score 1800
OK

# 특정 플레이어 점수 조회
127.0.0.1:6379> GET game:player:1002:score
"2300"

# 모든 점수 키 찾기
127.0.0.1:6379> KEYS game:player:*:score
1) "game:player:1001:score"
2) "game:player:1002:score"
3) "game:player:1003:score"

# 일일 점수는 24시간 후 초기화
127.0.0.1:6379> SET game:daily:player:1001 500 EX 86400
OK
```

### 6.4 시나리오 4: 설정값 관리 시스템

```bash
# 시스템 설정값들 저장
127.0.0.1:6379> SELECT 2
OK

127.0.0.1:6379[2]> SET config:max_users 1000
OK

127.0.0.1:6379[2]> SET config:maintenance_mode "false"
OK

127.0.0.1:6379[2]> SET config:debug_level "INFO"
OK

# 모든 설정 조회
127.0.0.1:6379[2]> KEYS config:*
1) "config:max_users"
2) "config:maintenance_mode"
3) "config:debug_level"

# 특정 설정 확인
127.0.0.1:6379[2]> GET config:maintenance_mode
"false"

# 긴급 설정 변경 (1시간 후 자동 복구)
127.0.0.1:6379[2]> SETEX config:emergency_mode "true" 3600
OK
```

### 6.5 종합 실습 과제

#### 과제 1: 쇼핑몰 장바구니 시스템
```bash
# 요구사항:
# 1. 사용자별 장바구니 데이터 저장
# 2. 24시간 후 자동 만료
# 3. 상품 추가/제거 기능 (현재는 덮어쓰기로)

# 해결책:
127.0.0.1:6379> SETEX cart:user:1001 86400 '{"items":[{"id":1,"name":"노트북","qty":1}]}'
OK

127.0.0.1:6379> GET cart:user:1001
"{\"items\":[{\"id\":1,\"name\":\"\ub178\ud2b8\ubd81\",\"qty\":1}]}"

127.0.0.1:6379> TTL cart:user:1001
(integer) 86397
```

#### 과제 2: API 속도 제한 시스템
```bash
# 요구사항:
# 1. IP별로 1분간 최대 60회 요청
# 2. 초과 시 차단
# 3. 1분 후 자동 리셋

# 기본 구조 (다음 장에서 INCR로 개선):
127.0.0.1:6379> SETEX rate_limit:192.168.1.100 60 1
OK

127.0.0.1:6379> GET rate_limit:192.168.1.100
"1"

127.0.0.1:6379> TTL rate_limit:192.168.1.100
(integer) 58
```

---

## 👨‍💻 주니어 시나리오

**실무에서 자주 겪는 상황과 해결 방법**

### 시나리오 1: TTL 설정을 깜빡한 세션 데이터

**상황**: 주니어 개발자가 사용자 세션을 Redis에 저장했지만 만료시간 설정을 깜빡했습니다.

```bash
# ❌ 주니어 개발자가 작성한 코드
127.0.0.1:6379> SET session:user:1001 "user_session_data"
OK

127.0.0.1:6379> SET session:user:1002 "user_session_data"
OK

# 일주일 후...
127.0.0.1:6379> DBSIZE
(integer) 150000  # 세션이 무한정 쌓임!

127.0.0.1:6379> INFO memory
used_memory_human:2.50G  # 메모리 부족!
```

**문제점**:
- 문제 1: 로그아웃하지 않은 세션이 영구 저장되어 메모리 낭비
- 문제 2: 메모리 부족으로 새로운 데이터 저장 불가
- 문제 3: 보안 위험 - 오래된 세션으로 접근 가능
- 왜 이 문제가 발생하는가: SET 명령어는 기본적으로 영구 저장이며, TTL 설정이 필수

**해결책**:
```bash
# ✅ 올바른 코드
# 방법 1: SETEX 사용 (권장)
127.0.0.1:6379> SETEX session:user:1001 1800 "user_session_data"
OK
# 30분(1800초) 후 자동 삭제

# 방법 2: SET + EXPIRE
127.0.0.1:6379> SET session:user:1002 "user_session_data"
OK
127.0.0.1:6379> EXPIRE session:user:1002 1800
(integer) 1

# 기존 데이터에 TTL 추가
127.0.0.1:6379> EXPIRE session:user:old 1800
(integer) 1

# TTL 확인
127.0.0.1:6379> TTL session:user:1001
(integer) 1795  # 정상적으로 설정됨

# 설명
# 1. SETEX는 원자적(atomic) 동작으로 더 안전
# 2. SET + EXPIRE는 두 명령어 사이에 오류 발생 가능성 있음
# 3. 세션은 30분, 캐시는 5분 등 용도에 따라 TTL 조정
```

**배운 점**:
- 💡 팁 1: 임시 데이터는 반드시 TTL 설정 (세션, 캐시, 토큰 등)
- 💡 팁 2: SETEX를 사용하면 SET + EXPIRE보다 안전
- 💡 팁 3: 운영 전 TTL 설정 여부를 체크리스트에 포함
- 💡 팁 4: 주기적으로 `TTL -1` 패턴으로 만료시간 없는 키 찾기

---

### 시나리오 2: KEYS * 명령어로 운영 서버 장애 발생

**상황**: 운영 서버에서 특정 패턴의 키를 찾기 위해 KEYS * 명령어를 사용했더니 서비스 전체가 먹통이 되었습니다.

```bash
# ❌ 주니어 개발자가 운영 서버에서 실행
127.0.0.1:6379> KEYS *
# ... 30초 동안 응답 없음 ...
# 이 시간 동안 모든 사용자 요청 블로킹!

# 고객 문의 폭주
"앱이 안 열려요!"
"결제가 안 돼요!"
"로그인이 안 돼요!"
```

**문제점**:
- 문제 1: KEYS는 O(N) 시간복잡도로 모든 키를 순차 스캔
- 문제 2: Redis는 싱글 스레드라 KEYS 실행 중 다른 명령 처리 불가
- 문제 3: 키가 100만 개면 수십 초 소요
- 왜 이 문제가 발생하는가: Redis는 싱글 스레드 구조로 하나의 명령이 끝나야 다음 명령 처리 가능

**해결책**:
```bash
# ✅ 올바른 방법 1: SCAN 사용 (운영 환경 권장)
127.0.0.1:6379> SCAN 0 MATCH user:* COUNT 100
1) "17"  # 다음 커서
2) 1) "user:1001:name"
   2) "user:1002:name"
   3) "user:1003:name"
   # ... 최대 100개

127.0.0.1:6379> SCAN 17 MATCH user:* COUNT 100
1) "35"
2) 1) "user:1004:name"
   2) "user:1005:name"
   # ... 계속

# ✅ 올바른 방법 2: 개발 환경에서만 KEYS 사용
# 로컬 개발 서버에서
127.0.0.1:6379> KEYS user:*
1) "user:1001:name"
2) "user:1002:name"

# ✅ 올바른 방법 3: EXISTS로 특정 키만 확인
127.0.0.1:6379> EXISTS user:1001:session
(integer) 1  # 존재

# 설명
# 1. SCAN은 커서 기반으로 조금씩 검색
# 2. 다른 명령어 처리를 블로킹하지 않음
# 3. COUNT로 한 번에 가져올 개수 조절 가능
```

**배운 점**:
- 💡 팁 1: 운영 환경에서는 KEYS * 절대 금지
- 💡 팁 2: SCAN 명령어 사용법 숙지 필수
- 💡 팁 3: Redis 모니터링으로 느린 명령어 감지
- 💡 팁 4: 코드 리뷰에서 KEYS 사용 여부 체크

---

### 시나리오 3: 잘못된 키 삭제로 중요 데이터 손실

**상황**: 테스트 데이터를 삭제하려다가 실수로 운영 데이터까지 삭제했습니다.

```bash
# ❌ 주니어 개발자의 실수
127.0.0.1:6379> KEYS user:test:*
1) "user:test:1001"
2) "user:test:1002"

# 복사-붙여넣기 하다가 실수로 다른 패턴 실행
127.0.0.1:6379> KEYS user:*
1) "user:test:1001"
2) "user:test:1002"
3) "user:1001:profile"  # 운영 데이터!
4) "user:1002:profile"  # 운영 데이터!
5) "user:1003:session"  # 운영 데이터!

# 전부 삭제 명령 실행
127.0.0.1:6379> DEL user:1001:profile user:1002:profile user:1003:session
(integer) 3

# 헉! 운영 데이터 삭제됨!
# 고객: "제 프로필이 사라졌어요!"
```

**문제점**:
- 문제 1: 패턴 확인 없이 바로 삭제 실행
- 문제 2: 테스트와 운영 데이터가 같은 데이터베이스에 혼재
- 문제 3: 백업이나 되돌리기 메커니즘 부재
- 왜 이 문제가 발생하는가: Redis는 트랜잭션이 제한적이고 DELETE는 즉시 실행됨

**해결책**:
```bash
# ✅ 올바른 방법 1: 데이터베이스 분리
# 테스트 데이터는 다른 DB 사용
127.0.0.1:6379> SELECT 1
OK
127.0.0.1:6379[1]> SET user:test:1001 "test_data"
OK

# 운영 데이터는 DB 0
127.0.0.1:6379[1]> SELECT 0
OK
127.0.0.1:6379> SET user:1001:profile "real_data"
OK

# ✅ 올바른 방법 2: 삭제 전 반드시 확인
# 1단계: 패턴 확인
127.0.0.1:6379[1]> KEYS user:test:*
1) "user:test:1001"
2) "user:test:1002"

# 2단계: 개수 확인
127.0.0.1:6379[1]> KEYS user:test:* | wc -l
2

# 3단계: 하나씩 확인하며 삭제
127.0.0.1:6379[1]> GET user:test:1001
"test_data"  # 확인 후 삭제

127.0.0.1:6379[1]> DEL user:test:1001
(integer) 1

# ✅ 올바른 방법 3: 중요 데이터는 백업 후 삭제
127.0.0.1:6379> GET important:data
"critical_value"

# 백업 (다른 키로 복사)
127.0.0.1:6379> SET important:data:backup "critical_value"
OK

# 안전하게 삭제
127.0.0.1:6379> DEL important:data
(integer) 1

# ✅ 올바른 방법 4: RENAME 사용
127.0.0.1:6379> RENAME important:data important:data:deleted
OK
# 잠시 후 문제없으면 삭제

# 설명
# 1. 환경별 데이터베이스 분리 (0: 운영, 1: 테스트)
# 2. 삭제는 신중하게, 반드시 확인 절차 거치기
# 3. 중요 데이터는 RENAME으로 먼저 숨기기
```

**배운 점**:
- 💡 팁 1: 테스트/운영 데이터를 다른 DB에 분리
- 💡 팁 2: 삭제 전 반드시 KEYS로 확인
- 💡 팁 3: 중요 데이터는 RENAME 후 관찰하다가 삭제
- 💡 팁 4: Redis 백업 정책 수립 (RDB, AOF)

---

### 시나리오 4: 키 명명 규칙 없이 개발하다가 충돌 발생

**상황**: 각자 마음대로 키 이름을 지었더니 나중에 충돌하고 관리가 불가능해졌습니다.

```bash
# ❌ 팀원들이 각자 다른 스타일로 키 생성
# 개발자 A
127.0.0.1:6379> SET user1001 "김철수"
OK

# 개발자 B
127.0.0.1:6379> SET user_1001_profile "김철수 프로필"
OK

# 개발자 C
127.0.0.1:6379> SET User:1001:Profile "김철수 프로필"
OK

# 개발자 D
127.0.0.1:6379> SET 1001 "김철수"  # 키가 너무 짧음!
OK

# 결과: 혼란스러운 키 구조
127.0.0.1:6379> KEYS *
1) "user1001"
2) "user_1001_profile"
3) "User:1001:Profile"
4) "1001"
5) "session_abc"
6) "SessionDEF"
7) "product-2001"
# ... 완전 무법천지

# 문제 발생
127.0.0.1:6379> GET user:1001:name
(nil)  # 어? 왜 없지?

127.0.0.1:6379> GET user1001
"김철수"  # 아, 여기 있었구나...
```

**문제점**:
- 문제 1: 일관성 없는 키 명명으로 검색 불가
- 문제 2: 대소문자, 구분자 혼용으로 버그 발생
- 문제 3: 키가 무엇을 의미하는지 알 수 없음
- 문제 4: 팀 협업 시 커뮤니케이션 비용 증가
- 왜 이 문제가 발생하는가: Redis는 키 명명 규칙을 강제하지 않아 개발자 재량에 달림

**해결책**:
```bash
# ✅ 팀 전체가 따르는 명명 규칙 수립

# 규칙 1: 콜론(:)으로 계층 구조 표현
# [도메인]:[엔티티]:[ID]:[속성]
user:1001:profile
user:1001:session
product:2001:name
product:2001:price
order:3001:status

# 규칙 2: 소문자 + 언더스코어 사용
cache:user_list:page_1
rate_limit:api:192.168.1.100
temp:upload_file:abc123

# 규칙 3: 명확한 접두사 사용
session:abc123       # 세션 데이터
cache:api:users      # 캐시 데이터
config:max_users     # 설정 값
temp:job:xyz         # 임시 데이터
queue:email          # 큐 데이터

# 규칙 4: 만료 시간 포함 여부 명시 (선택)
session:30m:user123  # 30분 만료
cache:5m:product     # 5분 만료

# 좋은 예시 모음
user:1001:profile          # ✅ 명확하고 계층적
session:abc123             # ✅ 용도가 분명
cache:product:2001:detail  # ✅ 구조화됨
rate_limit:ip:192.168.1.1  # ✅ 이해하기 쉬움

# 나쁜 예시 모음
usr1001                    # ❌ 약어 사용
user_profile_1001_data     # ❌ 너무 김
UserProfile               # ❌ 카멜케이스
u:1                       # ❌ 너무 짧음
user-1001                 # ❌ 하이픈 사용 (콜론 권장)

# 설명
# 1. 팀 위키에 명명 규칙 문서화
# 2. 코드 리뷰에서 규칙 준수 확인
# 3. 새 프로젝트 시작 시 반드시 규칙 정의
```

**배운 점**:
- 💡 팁 1: 프로젝트 시작 전 키 명명 규칙 문서화
- 💡 팁 2: 콜론(:)으로 계층 구조 표현이 업계 표준
- 💡 팁 3: 명명 규칙을 README에 명시
- 💡 팁 4: 자동화 도구로 규칙 위반 검사

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용 (7개)

<details>
<summary><strong>1. Redis의 SET과 GET 명령어는 무엇이며, 어떻게 사용하나요?</strong></summary>

**모범 답안 포인트**
- SET은 키-값 쌍을 저장하는 명령어
- GET은 키로 값을 조회하는 명령어
- 기본 문법과 옵션 설명
- 실무 활용 사례 제시

**예시 답변**
> "SET은 Redis에서 데이터를 저장하는 가장 기본적인 명령어입니다. `SET key value` 형태로 사용하며,
> 세션 관리나 캐싱에 주로 활용합니다. GET은 저장된 값을 조회하는 명령어로 `GET key`로 사용합니다.
> 실무에서는 SET 명령어에 EX 옵션을 추가해서 `SET session:user123 'data' EX 1800`처럼
> 만료시간을 함께 설정하는 경우가 많습니다."

**꼬리 질문**
- Q: SET할 때 이미 존재하는 키면 어떻게 되나요?
- A: 기존 값을 덮어씁니다. NX 옵션을 사용하면 키가 없을 때만 저장할 수 있습니다.

**실무 연관**
- 웹 세션 저장: `SET session:abc123 "user_data" EX 1800`
- API 응답 캐싱: `SET cache:api:users "json_data" EX 300`

</details>

<details>
<summary><strong>2. TTL(Time To Live)이 무엇이고 왜 중요한가요?</strong></summary>

**모범 답안 포인트**
- TTL은 데이터의 생존 시간
- 메모리 관리와 보안을 위해 필수
- EXPIRE, SETEX 명령어 사용법
- 실무에서 TTL 미설정 시 문제점

**예시 답변**
> "TTL은 Time To Live의 약자로 Redis 데이터의 생존 시간을 의미합니다.
> 설정한 시간이 지나면 데이터가 자동으로 삭제되어 메모리를 효율적으로 관리할 수 있습니다.
> 세션 데이터나 임시 캐시 등에 반드시 TTL을 설정해야 하며, 미설정 시 메모리 부족이나 보안 문제가 발생할 수 있습니다.
> `SETEX key 3600 value`로 1시간 만료를 설정하거나, `EXPIRE key 3600`으로 기존 키에 추가할 수 있습니다."

**꼬리 질문**
- Q: TTL 명령어의 반환값이 -1과 -2일 때 각각 무엇을 의미하나요?
- A: -1은 만료시간이 없는 영구 데이터, -2는 키가 존재하지 않음을 의미합니다.

**실무 연관**
- 세션: 30분 (1800초)
- 캐시: 5분 (300초)
- 인증 토큰: 10분 (600초)
- 임시 파일: 24시간 (86400초)

</details>

<details>
<summary><strong>3. KEYS * 명령어가 운영 환경에서 위험한 이유는 무엇인가요?</strong></summary>

**모범 답안 포인트**
- O(N) 시간 복잡도로 모든 키를 스캔
- 싱글 스레드 구조로 다른 명령 블로킹
- 대안으로 SCAN 명령어 사용
- 실제 장애 사례

**예시 답변**
> "KEYS * 명령어는 Redis의 모든 키를 순차적으로 스캔하기 때문에 O(N) 시간 복잡도를 가집니다.
> Redis는 싱글 스레드로 동작하므로 KEYS 명령이 실행되는 동안 다른 모든 요청이 블로킹되어
> 서비스 전체가 멈출 수 있습니다. 운영 환경에서는 SCAN 명령어를 사용해야 하며,
> 이는 커서 기반으로 조금씩 검색해서 다른 명령어의 실행을 방해하지 않습니다."

**꼬리 질문**
- Q: 그렇다면 개발 환경에서는 KEYS를 사용해도 되나요?
- A: 네, 로컬 개발 환경이나 데이터가 적은 테스트 환경에서는 사용 가능합니다.

**실무 연관**
- 실제로 KEYS * 사용으로 인한 서비스 장애 사례 다수
- 모니터링 도구에서 느린 명령어로 감지됨
- 코드 리뷰에서 KEYS 사용 여부 체크 필수

</details>

<details>
<summary><strong>4. Redis의 데이터베이스 번호(0~15)는 무엇이며 어떻게 활용하나요?</strong></summary>

**모범 답안 포인트**
- Redis는 기본 16개의 논리적 DB 제공
- SELECT 명령어로 전환
- 환경별, 용도별 데이터 분리에 활용
- 각 DB는 완전히 독립적

**예시 답변**
> "Redis는 기본적으로 0번부터 15번까지 16개의 논리적 데이터베이스를 제공합니다.
> 각 데이터베이스는 완전히 독립적이어서 같은 키 이름을 사용해도 충돌하지 않습니다.
> SELECT 명령어로 전환할 수 있으며, 실무에서는 0번은 운영 데이터, 1번은 테스트 데이터,
> 2번은 캐시 데이터 이렇게 용도별로 분리해서 사용합니다."

**꼬리 질문**
- Q: 16개보다 더 많은 데이터베이스를 사용할 수 있나요?
- A: redis.conf 파일에서 databases 설정을 변경하면 가능하지만, 일반적으로 16개면 충분합니다.

**실무 연관**
- 0번: 프로덕션 데이터
- 1번: 개발/테스트 데이터
- 2번: 캐시 전용
- 3번: 큐 데이터

</details>

<details>
<summary><strong>5. SET 명령어의 NX와 XX 옵션의 차이는 무엇인가요?</strong></summary>

**모범 답안 포인트**
- NX: 키가 없을 때만 설정 (Not eXists)
- XX: 키가 있을 때만 설정 (eXists)
- 실무 활용 사례
- 원자적 연산의 중요성

**예시 답변**
> "NX 옵션은 'Not eXists'의 약자로 키가 존재하지 않을 때만 값을 설정합니다.
> 반대로 XX 옵션은 키가 이미 존재할 때만 값을 업데이트합니다.
> 실무에서 NX는 중복 방지가 필요한 경우(예: 분산 락), XX는 기존 값만 업데이트하고 싶을 때 사용합니다.
> 예를 들어 `SET lock:resource 1 NX EX 10`으로 분산 락을 구현할 수 있습니다."

**꼬리 질문**
- Q: 두 옵션을 동시에 사용할 수 있나요?
- A: 아니요, NX와 XX는 상호 배타적이므로 동시 사용 불가능합니다.

**실무 연관**
- NX: 분산 락, 중복 방지, 초기값 설정
- XX: 기존 데이터 업데이트만 허용

</details>

<details>
<summary><strong>6. Redis 키 명명 규칙(Naming Convention)은 왜 중요하며 어떻게 정하나요?</strong></summary>

**모범 답안 포인트**
- 일관성 있는 구조로 관리 용이
- 콜론(:)으로 계층 구조 표현이 표준
- 팀 협업에 필수
- 실제 예시 제시

**예시 답변**
> "Redis 키 명명 규칙은 데이터를 체계적으로 관리하고 팀 협업을 위해 매우 중요합니다.
> 업계 표준은 콜론(:)을 사용한 계층 구조로, `user:1001:profile`, `cache:product:2001` 같은 형태입니다.
> 명확한 접두사를 사용해서 용도를 구분하고(session:, cache:, config: 등),
> 소문자와 언더스코어를 일관되게 사용하는 것이 좋습니다.
> 프로젝트 시작 시 팀 전체가 합의한 규칙을 문서화해야 합니다."

**꼬리 질문**
- Q: 하이픈(-)과 콜론(:) 중 어느 것을 사용하는 게 좋나요?
- A: 콜론(:)이 업계 표준입니다. Redis 도구들도 콜론 기준으로 계층을 인식합니다.

**실무 연관**
- 좋은 예: `user:1001:session`, `cache:api:users:page:1`
- 나쁜 예: `usr1001`, `UserSession`, `u:1`

</details>

<details>
<summary><strong>7. DEL 명령어로 데이터를 삭제할 때 주의할 점은 무엇인가요?</strong></summary>

**모범 답안 포인트**
- 삭제는 즉시 실행되고 되돌릴 수 없음
- 삭제 전 반드시 확인
- 중요 데이터는 백업 또는 RENAME
- 운영/테스트 데이터 분리

**예시 답변**
> "DEL 명령어는 즉시 실행되며 되돌릴 수 없기 때문에 매우 신중해야 합니다.
> 삭제 전에 반드시 KEYS나 GET으로 확인하고, 중요한 데이터는 다른 키로 백업하거나
> RENAME으로 먼저 이름을 변경한 후 관찰하다가 삭제하는 것이 안전합니다.
> 또한 테스트 데이터와 운영 데이터를 다른 데이터베이스에 분리해서
> 실수로 운영 데이터를 삭제하는 것을 방지해야 합니다."

**꼬리 질문**
- Q: 여러 키를 한 번에 삭제할 수 있나요?
- A: 네, `DEL key1 key2 key3` 형태로 여러 키를 동시 삭제 가능하며, 삭제된 키 개수를 반환합니다.

**실무 연관**
- 삭제 전 체크리스트: 1) 패턴 확인 2) 개수 확인 3) 샘플 조회 4) 삭제 실행
- Redis 백업 정책 수립 (RDB, AOF)

</details>

---

### 📗 중급 개발자용 (5개)

<details>
<summary><strong>1. Redis의 싱글 스레드 구조가 성능에 미치는 영향과 대응 방법은?</strong></summary>

**모범 답안 포인트**
- 싱글 스레드의 장단점
- O(N) 명령어의 위험성
- 파이프라이닝과 배치 처리
- 클러스터링으로 스케일 아웃

**예시 답변**
> "Redis는 싱글 스레드로 동작하여 명령어를 순차적으로 처리합니다.
> 이는 락(lock) 없이 원자적 연산이 가능하다는 장점이 있지만,
> O(N) 시간 복잡도를 가진 명령어(KEYS, FLUSHALL 등)가 실행되면
> 모든 요청이 블로킹된다는 단점이 있습니다.
> 대응 방법으로는 1) SCAN 같은 커서 기반 명령 사용,
> 2) 파이프라이닝으로 네트워크 왕복 최소화,
> 3) 클러스터링으로 데이터 분산이 있습니다."

**실무 예시**
```bash
# ❌ 나쁜 예: 순차 실행
for i in 1..1000:
    GET key_{i}  # 1000번 왕복

# ✅ 좋은 예: 파이프라이닝
MGET key_1 key_2 ... key_1000  # 1번 왕복
```

**꼬리 질문**
- Q: Redis 6.0부터 멀티 스레드를 지원한다고 들었는데 어떤 부분인가요?
- A: I/O 스레드만 멀티 스레드이고, 핵심 데이터 처리는 여전히 싱글 스레드입니다.

**실무 연관**
- 느린 명령어 모니터링으로 병목 지점 파악
- SLOWLOG로 10ms 이상 걸린 명령 추적
- 프로덕션에서 O(N) 명령 금지 정책

</details>

<details>
<summary><strong>2. SETEX와 SET + EXPIRE의 차이점과 원자성(Atomicity) 문제는?</strong></summary>

**모범 답안 포인트**
- SETEX는 원자적(atomic) 연산
- SET + EXPIRE는 두 개의 독립적 명령
- 네트워크 장애나 서버 크래시 시나리오
- 실무에서 SETEX 선호 이유

**예시 답변**
> "SETEX는 SET과 EXPIRE를 하나의 원자적 연산으로 수행하지만,
> SET + EXPIRE는 두 개의 독립적인 명령어입니다.
> SET 실행 후 EXPIRE 전에 네트워크 장애나 서버 크래시가 발생하면
> TTL이 설정되지 않아 데이터가 영구 저장되는 문제가 발생합니다.
> 따라서 실무에서는 SETEX를 사용하는 것이 안전하며,
> 특히 세션이나 캐시처럼 반드시 만료되어야 하는 데이터에 필수적입니다."

**실무 예시**
```bash
# ❌ 위험: SET 후 서버 크래시
SET session:user123 "data"
# 여기서 서버 크래시! EXPIRE 실행 안됨
EXPIRE session:user123 1800

# ✅ 안전: 원자적 실행
SETEX session:user123 1800 "data"
```

**꼬리 질문**
- Q: 이미 존재하는 키에 TTL만 추가하려면 어떻게 하나요?
- A: EXPIRE 명령어를 사용하면 됩니다. 기존 값은 유지하고 TTL만 설정/변경합니다.

**실무 연관**
- 세션 관리에서 SETEX 필수 사용
- 트랜잭션 처리 시 원자성 보장
- 장애 복구 시나리오 대비

</details>

<details>
<summary><strong>3. Redis 데이터베이스 16개 분리 전략과 한계점은?</strong></summary>

**모범 답안 포인트**
- 논리적 분리일 뿐 물리적 격리 아님
- 메모리는 공유, CPU도 공유
- 클러스터 모드에서는 DB 0만 사용
- 실무 분리 전략

**예시 답변**
> "Redis의 16개 데이터베이스는 논리적 분리일 뿐 물리적으로 격리되지 않습니다.
> 모든 DB가 동일한 메모리와 CPU를 공유하므로 한 DB의 부하가 전체에 영향을 줍니다.
> 또한 Redis 클러스터 모드에서는 DB 0만 사용 가능하다는 한계가 있습니다.
> 실무에서는 환경별 분리(0:운영, 1:테스트)나 용도별 분리(2:캐시, 3:큐)로 활용하되,
> 완전한 격리가 필요하면 별도 Redis 인스턴스를 사용해야 합니다."

**실무 예시**
```bash
# 환경별 분리
DB 0: 프로덕션 데이터
DB 1: 스테이징 데이터
DB 2: 개발 데이터

# 용도별 분리
DB 0: 세션
DB 1: 캐시
DB 2: 큐
DB 3: 통계

# ⚠️ 한계
- DB 1이 과부하면 DB 0도 느려짐
- 메모리 사용량 전체 공유
```

**꼬리 질문**
- Q: 그렇다면 언제 별도 Redis 인스턴스를 사용해야 하나요?
- A: 완전한 격리가 필요하거나, 각각 다른 설정이 필요하거나, 장애 격리가 중요한 경우입니다.

**실무 연관**
- 멀티 테넌시 구조에서 주의
- 클러스터 전환 시 DB 통합 필요
- 모니터링은 인스턴스 단위로

</details>

<details>
<summary><strong>4. 대용량 키 삭제 시 성능 이슈와 해결 방법은?</strong></summary>

**모범 답안 포인트**
- 큰 컬렉션 삭제 시 블로킹 발생
- UNLINK 명령어 사용 (비동기 삭제)
- 점진적 삭제 전략
- lazy-free 설정

**예시 답변**
> "대용량 키(예: 수백만 개 요소를 가진 List나 Set)를 DEL로 삭제하면
> 싱글 스레드 특성상 삭제가 완료될 때까지 모든 요청이 블로킹됩니다.
> 해결 방법으로는 1) UNLINK 명령어로 비동기 삭제,
> 2) SCAN + DEL로 점진적 삭제,
> 3) redis.conf의 lazyfree-lazy-user-del 설정 활성화가 있습니다.
> Redis 4.0 이상에서는 UNLINK 사용을 권장합니다."

**실무 예시**
```bash
# ❌ 블로킹 발생 (100만 개 요소)
DEL large_list  # 수백 ms 블로킹

# ✅ 비동기 삭제 (즉시 반환)
UNLINK large_list  # 백그라운드 삭제

# ✅ 점진적 삭제
SCAN 0 MATCH temp:* COUNT 1000
# 1000개씩 나눠서 DEL

# redis.conf 설정
lazyfree-lazy-user-del yes
```

**꼬리 질문**
- Q: UNLINK와 DEL의 성능 차이는 얼마나 되나요?
- A: 대용량 키의 경우 UNLINK는 O(1), DEL은 O(N)으로 수백 배 차이 날 수 있습니다.

**실무 연관**
- 캐시 전체 삭제 시 주의
- 배치 작업에서 대용량 삭제
- 모니터링으로 느린 DEL 감지

</details>

<details>
<summary><strong>5. Redis 키 만료(Expiration) 메커니즘의 내부 동작 원리는?</strong></summary>

**모범 답안 포인트**
- Passive 방식: 접근 시 확인
- Active 방식: 주기적 스캔
- 메모리 부족 시 eviction policy
- maxmemory-policy 설정

**예시 답변**
> "Redis의 키 만료는 두 가지 방식으로 동작합니다.
> 1) Passive 방식: 키에 접근할 때 만료 여부를 확인하여 만료되었으면 삭제합니다.
> 2) Active 방식: 초당 10회 랜덤하게 20개 키를 샘플링하여 만료된 키를 삭제합니다.
> 만료된 키가 25% 이상이면 반복합니다.
> 메모리가 부족하면 maxmemory-policy 설정에 따라 키를 제거하며,
> 기본값은 noeviction(에러 반환)입니다.
> 실무에서는 volatile-lru(TTL 있는 키 중 LRU)나 allkeys-lru를 많이 사용합니다."

**실무 예시**
```bash
# redis.conf 설정
maxmemory 2gb
maxmemory-policy allkeys-lru

# 정책 종류
noeviction        # 기본값, 에러 반환
volatile-lru      # TTL 있는 키만 LRU 삭제
allkeys-lru       # 모든 키 LRU 삭제
volatile-ttl      # TTL 짧은 키부터 삭제
volatile-random   # TTL 있는 키 랜덤 삭제
allkeys-random    # 모든 키 랜덤 삭제
```

**꼬리 질문**
- Q: Active 방식으로 100% 만료된 키가 즉시 삭제되지 않을 수도 있나요?
- A: 네, 랜덤 샘플링이라 일부 만료 키가 남을 수 있지만, Passive 방식으로 접근 시 삭제됩니다.

**실무 연관**
- 메모리 모니터링으로 만료 효율 확인
- eviction 정책은 서비스 특성에 맞게 선택
- INFO stats로 evicted_keys 추적

</details>

---

## 📝 7. 핵심 내용 정리

### 7.1 이 장에서 배운 핵심 명령어

| 명령어 | 용도 | 예시 |
|--------|------|------|
| `SET key value` | 값 저장 | `SET name "김철수"` |
| `GET key` | 값 조회 | `GET name` |
| `KEYS pattern` | 키 패턴 검색 | `KEYS user:*` |
| `EXISTS key` | 키 존재 확인 | `EXISTS session:123` |
| `DEL key` | 키 삭제 | `DEL temp_data` |
| `EXPIRE key seconds` | 만료시간 설정 | `EXPIRE session 1800` |
| `TTL key` | 남은 시간 조회 | `TTL session` |
| `SELECT db` | 데이터베이스 전환 | `SELECT 1` |

### 7.2 SET 명령어 옵션 정리

| 옵션 | 의미 | 예시 |
|------|------|------|
| `EX seconds` | 초 단위 만료시간 | `SET key value EX 60` |
| `PX milliseconds` | 밀리초 단위 만료시간 | `SET key value PX 5000` |
| `NX` | 키가 없을 때만 설정 | `SET key value NX` |
| `XX` | 키가 있을 때만 설정 | `SET key value XX` |
| `GET` | 이전 값 반환 | `SET key newvalue GET` |

### 7.3 TTL 값의 의미

| TTL 반환값 | 의미 |
|------------|------|
| `양수` | 남은 초 수 |
| `-1` | 만료시간 없음 (영구) |
| `-2` | 키가 존재하지 않음 |

### 7.4 실무 베스트 프랙티스

#### 키 명명 규칙
```bash
# 좋은 예
user:1001:profile
session:abc123
cache:api:users:page:1
rate_limit:192.168.1.100

# 나쁜 예
user1001profile
sessionabc123
apiuserspage1cache
```

#### 만료시간 활용
```bash
# 세션: 30분
SETEX session:user123 1800 "session_data"

# 캐시: 5분
SETEX cache:api_response 300 "cached_data"

# 인증토큰: 10분
SETEX verify:email:token 600 "verification_code"

# 임시 데이터: 24시간
SETEX temp:upload:file123 86400 "temp_file_path"
```

#### 데이터베이스 분리 전략
```bash
# 0번: 세션 및 사용자 데이터
# 1번: 캐시 데이터
# 2번: 큐 및 작업 데이터
# 3번: 통계 및 분석 데이터
# 4번: 설정 및 메타데이터
```

---

## ❓ 8. 자주 묻는 질문 (FAQ)

<details>
<summary><strong>Q1: KEYS * 명령어가 위험한 이유는 무엇인가요?</strong></summary>

**A**: `KEYS *`는 모든 키를 순차적으로 스캔하므로 운영 환경에서 매우 위험합니다.

**상세 설명**:
- 포인트 1: O(N) 시간 복잡도로 키가 많을수록 실행 시간이 기하급수적으로 증가
- 포인트 2: Redis는 싱글 스레드라 KEYS 실행 중 모든 다른 명령어가 블로킹됨
- 포인트 3: 100만 개 키가 있으면 수십 초 소요 가능
- 포인트 4: 그 시간 동안 모든 사용자 요청이 멈춤 (서비스 장애)

**대안**:
```bash
# ❌ 위험: 운영 환경
KEYS *  # 절대 금지!

# ✅ 안전: SCAN 사용
SCAN 0 MATCH pattern:* COUNT 100
# 커서 기반으로 조금씩 검색, 다른 명령 블로킹 안함

# ✅ 개발 환경에서만
KEYS *  # 로컬/테스트 환경에서만 사용
```

**실무 팁**:
- 💡 redis.conf에서 KEYS 명령 금지 가능: `rename-command KEYS ""`
- 💡 모니터링 도구로 느린 명령어 감지
- 💡 코드 리뷰에서 KEYS 사용 여부 필수 체크

</details>

<details>
<summary><strong>Q2: SET과 SETEX 중 어느 것을 사용해야 하나요?</strong></summary>

**A**: 용도에 따라 선택하되, TTL이 필요하면 무조건 SETEX를 사용하세요.

**상세 설명**:
- SETEX는 원자적(atomic) 연산으로 안전
- SET + EXPIRE는 두 명령 사이에 장애 발생 가능성 있음
- SETEX는 SET과 EXPIRE를 동시에 실행하는 최적화된 명령

**예시**:
```bash
# ✅ 영구 저장 (설정값 등)
SET config:max_users 1000
SET system:version "2.0.1"

# ✅ 임시 데이터 (TTL 필수)
SETEX session:user123 1800 "session_data"  # 권장
SETEX cache:product:1001 300 "cached_data"

# ❌ 위험한 방법
SET session:user123 "session_data"
EXPIRE session:user123 1800
# SET과 EXPIRE 사이에 서버 장애 시 TTL 설정 안됨!

# ✅ 밀리초 단위 TTL
SET key value PX 5000  # 5초 = 5000ms
```

**실무 팁**:
- 💡 세션, 캐시, 토큰은 100% SETEX 사용
- 💡 SETEX는 성능도 더 좋음 (명령어 1번)
- 💡 Redis 클라이언트 라이브러리도 SETEX 권장

</details>

<details>
<summary><strong>Q3: 데이터베이스를 16개보다 더 많이 사용할 수 있나요?</strong></summary>

**A**: 설정 파일에서 변경 가능하지만, 일반적으로 16개면 충분합니다.

**상세 설명**:
```bash
# redis.conf 파일에서 설정 변경
databases 32  # 32개로 증가 가능
databases 64  # 64개도 가능

# 재시작 필요
sudo systemctl restart redis
```

**주의사항**:
- ⚠️ 주의 1: 너무 많은 DB는 관리 복잡도 증가
- ⚠️ 주의 2: Redis 클러스터 모드에서는 DB 0만 사용 가능
- ⚠️ 주의 3: 모든 DB가 메모리와 CPU 공유 (물리적 격리 아님)
- ⚠️ 주의 4: 완전한 격리가 필요하면 별도 Redis 인스턴스 사용

**권장 사항**:
```bash
# 실무 활용 예시 (16개로 충분)
DB 0: 프로덕션 데이터
DB 1: 스테이징 데이터
DB 2: 개발 데이터
DB 3: 캐시 전용
DB 4: 세션 전용
DB 5: 큐 데이터
DB 6-15: 예약/미사용
```

**실무 팁**:
- 💡 16개로 부족하면 설계 재검토
- 💡 완전 격리는 별도 Redis 인스턴스가 정답
- 💡 용도별로 명확히 구분해서 사용

</details>

<details>
<summary><strong>Q4: 한글 키와 값을 사용해도 되나요?</strong></summary>

**A**: 기술적으로 가능하지만 권장하지 않습니다. 값은 괜찮지만 키는 영문 사용을 강력히 권장합니다.

**상세 설명**:
```bash
# 기술적으로 가능
SET 사용자:1001:이름 "김철수"  # 작동은 함
GET 사용자:1001:이름
"김철수"

# ✅ 권장 방식
SET user:1001:name "김철수"  # 키는 영문, 값은 한글 OK
GET user:1001:name
"김철수"
```

**키에 한글 사용을 권장하지 않는 이유**:
1. **국제화 고려**: 다양한 언어 환경에서 문제 발생 가능
2. **키보드 입력 불편**: CLI에서 한글 입력이 번거로움
3. **호환성 문제**: 일부 클라이언트 라이브러리에서 이슈 발생 가능
4. **URL 인코딩**: API에서 사용 시 인코딩 필요
5. **디버깅 어려움**: 로그나 모니터링 도구에서 가독성 저하

**값은 한글 사용 OK**:
```bash
# 값은 한글 사용해도 전혀 문제없음
SET user:1001:name "김철수"
SET product:2001:desc "최고급 노트북"
SET notice:today "오늘은 점검일입니다"
```

**실무 팁**:
- 💡 키: 영문 소문자 + 콜론 + 언더스코어
- 💡 값: 한글 포함 모든 문자 가능
- 💡 JSON 값 저장 시 UTF-8 인코딩 확인

</details>

<details>
<summary><strong>Q5: 실수로 중요한 데이터를 삭제했을 때 복구 방법은?</strong></summary>

**A**: Redis는 기본적으로 되돌릴 수 없으므로 **예방이 최선**입니다.

**예방 방법**:
```bash
# 1. 삭제 전 반드시 확인
KEYS user:test:*  # 먼저 확인
# 1) "user:test:1001"
# 2) "user:test:1002"

GET user:test:1001  # 내용 확인
"test_data"

DEL user:test:1001  # 확인 후 삭제

# 2. 중요 데이터는 백업 후 삭제
GET important:data
"critical_value"

SET important:data:backup "critical_value"  # 백업
DEL important:data  # 삭제

# 3. RENAME으로 먼저 숨기기
RENAME important:data important:data:deleted_20240101
# 일정 기간 관찰 후 문제없으면 삭제
DEL important:data:deleted_20240101

# 4. 운영/테스트 DB 분리
SELECT 0  # 운영
SELECT 1  # 테스트 (여기서만 삭제)
```

**복구 방법 (사전 설정 필요)**:
```bash
# Redis 백업 설정 (redis.conf)
# 1. RDB (스냅샷)
save 900 1      # 15분마다 1개 이상 변경 시
save 300 10     # 5분마다 10개 이상 변경 시
save 60 10000   # 1분마다 10000개 이상 변경 시

# 2. AOF (Append Only File)
appendonly yes
appendfsync everysec  # 매초 동기화

# 복구
redis-server --appendonly yes --dir /backup/path
```

**운영 환경 보호**:
- ⚠️ DEL, FLUSHDB, FLUSHALL 명령 권한 제한
- ⚠️ 운영 서버 직접 접속 최소화
- ⚠️ 백업 자동화 및 주기적 검증
- ⚠️ 삭제 작업 승인 프로세스 수립

**실무 팁**:
- 💡 삭제 전 3단계 확인: 1)패턴 2)개수 3)샘플조회
- 💡 중요 작업은 점검 시간에만
- 💡 RDB + AOF 둘 다 활성화 권장

</details>

<details>
<summary><strong>Q6: TTL을 설정했는데 데이터가 즉시 삭제되지 않는 이유는?</strong></summary>

**A**: Redis의 키 만료는 Passive + Active 두 가지 방식으로 동작하며, 100% 즉시 삭제를 보장하지 않습니다.

**상세 설명**:

**1. Passive Expiration (수동적 만료)**:
```bash
SETEX temp:data 10 "value"  # 10초 후 만료

# 10초 후...
GET temp:data  # 이때 만료 확인 → 삭제 → (nil) 반환
```
- 키에 접근할 때 만료 여부 확인
- 만료되었으면 그때 삭제
- 접근하지 않으면 메모리에 남아있을 수 있음

**2. Active Expiration (능동적 만료)**:
```bash
# Redis가 자동으로 수행
- 초당 10회 실행
- 매번 랜덤하게 20개 키 샘플링
- 만료된 키 발견 시 삭제
- 만료된 키가 25% 이상이면 반복
```

**왜 즉시 삭제되지 않나요?**:
- Redis는 성능을 위해 완벽한 즉시 삭제를 하지 않음
- 랜덤 샘플링이라 일부 만료 키가 잠시 남을 수 있음
- 하지만 접근 시(Passive)에는 100% 삭제됨
- 메모리 부족 시 eviction policy로 강제 삭제

**실무 영향**:
```bash
# 걱정하지 않아도 되는 이유
1. 만료된 키는 접근 불가 (GET 시 nil)
2. 메모리 부족 시 자동 정리
3. Active 방식으로 점진적 정리
4. 실무에서 큰 문제 없음

# 즉시 삭제가 필요하면
DEL key  # 수동으로 즉시 삭제
```

**실무 팁**:
- 💡 만료 시간은 여유있게 설정
- 💡 메모리 모니터링 중요
- 💡 maxmemory-policy 적절히 설정

</details>

<details>
<summary><strong>Q7: Redis CLI에서 대량의 데이터를 한 번에 입력하는 방법은?</strong></summary>

**A**: 파이프라인, Mass Insertion, Lua 스크립트 등 여러 방법이 있습니다.

**방법 1: 파이프라인 (간단한 경우)**:
```bash
# 방법 1-1: echo + pipe
echo -e "SET key1 value1\nSET key2 value2\nSET key3 value3" | redis-cli

# 방법 1-2: 파일 사용
cat data.txt | redis-cli
# data.txt 내용:
# SET key1 value1
# SET key2 value2
# SET key3 value3
```

**방법 2: Mass Insertion (대용량)**:
```bash
# 1. Redis 프로토콜 형식 파일 생성 (mass_insert.txt)
*3\r\n$3\r\nSET\r\n$4\r\nkey1\r\n$6\r\nvalue1\r\n
*3\r\n$3\r\nSET\r\n$4\r\nkey2\r\n$6\r\nvalue2\r\n

# 2. 대량 입력
cat mass_insert.txt | redis-cli --pipe

# 결과
All data transferred. Waiting for the last reply...
Last reply received from server.
errors: 0, replies: 1000000
```

**방법 3: 프로그래밍 언어 사용 (권장)**:
```python
# Python 예시
import redis

r = redis.Redis(host='localhost', port=6379)

# 파이프라인 사용 (빠름)
pipe = r.pipeline()
for i in range(10000):
    pipe.set(f'user:{i}:name', f'user{i}')
pipe.execute()

# 또는 Mass insertion
data = {}
for i in range(10000):
    data[f'user:{i}:name'] = f'user{i}'
r.mset(data)
```

**방법 4: redis-cli --csv 모드**:
```bash
# CSV 파일에서 읽기
cat users.csv | redis-cli --pipe
```

**성능 비교**:
```bash
# 단일 명령: 1000개 = 10초
for i in 1..1000; do redis-cli SET key_$i value_$i; done

# 파이프라인: 1000개 = 0.1초
echo "..." | redis-cli --pipe

# Mass Insertion: 100만개 = 2초
cat huge_file.txt | redis-cli --pipe
```

**실무 팁**:
- 💡 1000개 미만: echo + pipe
- 💡 1000~10000개: 프로그래밍 언어 파이프라인
- 💡 10000개 이상: Mass Insertion
- 💡 데이터 마이그레이션: DUMP + RESTORE

</details>

<details>
<summary><strong>Q8: Redis 메모리가 부족할 때 어떻게 되나요?</strong></summary>

**A**: maxmemory-policy 설정에 따라 다르게 동작합니다.

**기본 동작 (noeviction)**:
```bash
# maxmemory 설정
maxmemory 2gb

# 메모리 가득 차면
SET new:key "value"
(error) OOM command not allowed when used memory > 'maxmemory'
```

**eviction 정책 종류**:
```bash
# redis.conf 설정
maxmemory 2gb
maxmemory-policy [정책]

# 1. noeviction (기본값)
- 메모리 가득 차면 쓰기 명령 거부
- 읽기는 계속 가능
- 에러: OOM command not allowed

# 2. allkeys-lru (권장 - 범용)
- 모든 키 중 LRU(Least Recently Used) 알고리즘으로 삭제
- 가장 오래 사용안한 키부터 제거

# 3. volatile-lru (권장 - 캐시)
- TTL 설정된 키만 LRU로 삭제
- TTL 없는 키는 보존

# 4. allkeys-random
- 모든 키 중 랜덤 삭제

# 5. volatile-random
- TTL 있는 키 중 랜덤 삭제

# 6. volatile-ttl
- TTL 짧은 키부터 삭제

# 7. allkeys-lfu (Redis 4.0+)
- LFU(Least Frequently Used) 알고리즘
- 사용 빈도 낮은 키 삭제

# 8. volatile-lfu
- TTL 있고 사용 빈도 낮은 키 삭제
```

**실무 권장 설정**:
```bash
# 캐시 서버
maxmemory 4gb
maxmemory-policy allkeys-lru

# 세션 + 캐시 혼용
maxmemory 4gb
maxmemory-policy volatile-lru

# 중요 데이터
maxmemory 4gb
maxmemory-policy noeviction  # 에러내고 확인
```

**모니터링**:
```bash
# 메모리 사용량 확인
INFO memory
used_memory_human:1.50G
maxmemory_human:2.00G

# eviction 통계
INFO stats
evicted_keys:1234  # 제거된 키 수
```

**실무 팁**:
- 💡 메모리는 여유있게 설정 (80% 수준)
- 💡 캐시는 allkeys-lru 권장
- 💡 evicted_keys 모니터링 필수
- 💡 메모리 부족 알람 설정

</details>

---

## 🚀 9. 다음 단계 예고

다음 장에서는 **String 타입의 고급 기능**을 학습합니다:

### 다음 장 미리보기: String 타입 완전 가이드
- **숫자 연산**: `INCR`, `DECR`, `INCRBY`, `DECRBY`
- **문자열 조작**: `APPEND`, `STRLEN`, `GETRANGE`, `SETRANGE`
- **멀티 키 조작**: `MSET`, `MGET`, `MSETNX`
- **비트 연산**: `SETBIT`, `GETBIT`, `BITCOUNT`
- **실전 활용**: 카운터, 통계, 세션 관리 고급 패턴

### 준비하면 좋을 것들
```bash
# 다음 장 실습을 위한 준비
127.0.0.1:6379> FLUSHALL  # 깨끗한 환경에서 시작
OK

127.0.0.1:6379> SELECT 0  # 0번 데이터베이스 사용
OK
```

---

## 🎉 축하합니다!

**이제 Redis의 기본 조작을 완전히 마스터했습니다!**

당신은 이제 Redis 초보자가 아닙니다. 실무에서 바로 사용 가능한 Redis 개발자입니다!

---

### 🏆 현재 여러분의 능력

**✅ 기술적 능력**:
- Redis CLI를 능숙하게 다루며 모든 기본 명령어를 숙지
- SET, GET, DEL 등 핵심 명령어를 완벽히 이해하고 활용
- TTL을 활용한 자동 메모리 관리 구현 가능
- 16개 데이터베이스를 용도에 맞게 분리하여 사용
- KEYS의 위험성을 인지하고 SCAN으로 안전하게 대체
- 키 명명 규칙을 수립하여 체계적인 데이터 관리 가능

**✅ 실무 역량**:
- 세션 관리 시스템 구현 가능
- 캐시 시스템 설계 및 구축 가능
- TTL 기반 자동 데이터 정리 구현
- 운영 환경 장애 상황 예방 및 대응
- 주니어 개발자가 흔히 하는 실수 방지

**✅ 문제 해결 능력**:
- Redis 관련 면접 질문에 자신있게 답변 가능
- 실무 장애 상황 시나리오 대응 경험 보유
- FAQ 8개 항목을 숙지하여 문제 해결 가능

---

### 📊 학습 완료 체크리스트

#### 필수 명령어 마스터
- [ ] SET, GET 명령어를 다양한 옵션과 함께 사용
- [ ] SETEX로 TTL 설정된 데이터 저장
- [ ] KEYS, SCAN의 차이점 이해 및 적절히 사용
- [ ] EXISTS로 키 존재 여부 확인
- [ ] DEL로 안전하게 데이터 삭제
- [ ] EXPIRE, TTL로 만료시간 관리
- [ ] SELECT로 데이터베이스 전환
- [ ] FLUSHDB, FLUSHALL의 위험성 이해

#### 실무 패턴 습득
- [ ] 세션 관리 (30분 TTL)
- [ ] 캐시 시스템 (5분 TTL)
- [ ] 임시 토큰 (10분 TTL)
- [ ] Rate Limiting 구현
- [ ] 온라인 상태 관리

#### 안전 수칙 숙지
- [ ] 운영 환경에서 KEYS * 금지
- [ ] TTL 설정 필수 항목 체크
- [ ] 삭제 전 3단계 확인 (패턴→개수→샘플)
- [ ] 테스트/운영 데이터베이스 분리
- [ ] 키 명명 규칙 준수

#### 주니어 시나리오 학습
- [ ] TTL 미설정으로 인한 메모리 부족 해결
- [ ] KEYS * 사용으로 인한 서비스 장애 예방
- [ ] 실수로 운영 데이터 삭제 방지
- [ ] 키 명명 규칙 수립 및 적용

#### 면접 준비 완료
- [ ] 주니어 질문 7개 답변 가능
- [ ] 중급 질문 5개 답변 가능
- [ ] 각 질문의 꼬리 질문까지 대응 준비
- [ ] 실무 경험 예시 준비

#### FAQ 숙지
- [ ] Q1: KEYS * 위험성
- [ ] Q2: SET vs SETEX
- [ ] Q3: 데이터베이스 개수 확장
- [ ] Q4: 한글 키/값 사용
- [ ] Q5: 데이터 삭제 복구
- [ ] Q6: TTL 즉시 삭제 메커니즘
- [ ] Q7: 대량 데이터 입력
- [ ] Q8: 메모리 부족 대응

---

### 🎯 다음 단계 추천

**레벨 1 (현재)**: Redis 기본 조작 마스터 ✅ **완료!**

**레벨 2 (다음 장)**: String 타입 완전 가이드
- INCR, DECR로 카운터 구현
- APPEND, GETRANGE로 문자열 조작
- MGET, MSET으로 대량 처리
- 비트 연산으로 고급 기능 구현

**레벨 3 (향후)**: 다양한 자료구조
- List로 큐/스택 구현
- Set으로 집합 연산
- Hash로 객체 저장
- Sorted Set으로 랭킹 시스템

**레벨 4 (최종)**: 실전 프로젝트
- 실시간 채팅 시스템
- 좋아요/조회수 카운터
- 실시간 랭킹 시스템
- 분산 락 구현

---

### 💪 당신이 할 수 있는 것들

이제 다음과 같은 시스템을 **직접 구현**할 수 있습니다:

**1. 사용자 세션 관리 시스템**
```bash
# 로그인 시
SETEX session:abc123 1800 '{"user_id":1001,"role":"admin"}'

# 활동 시 연장
EXPIRE session:abc123 1800

# 로그아웃 시
DEL session:abc123
```

**2. API 캐시 시스템**
```bash
# 캐시 저장
SETEX cache:api:users 300 '[{"id":1,"name":"김철수"}...]'

# 캐시 조회
GET cache:api:users

# 데이터 변경 시 캐시 무효화
DEL cache:api:users
```

**3. 임시 인증 코드 시스템**
```bash
# 이메일 인증 코드 (10분)
SETEX verify:email:kim@example.com 600 "123456"

# 인증 확인
GET verify:email:kim@example.com

# 인증 완료 시 삭제
DEL verify:email:kim@example.com
```

**4. 온라인 사용자 추적**
```bash
# 사용자 활동 시
SETEX online:user:1001 300 "active"

# 5분간 활동 없으면 자동 오프라인 처리
```

---

### 🌟 성장 지표

**이 장을 시작하기 전**:
- Redis가 뭔지만 알았던 단계
- 명령어를 외우지 못한 상태
- 실무 적용 방법을 몰랐던 시기

**이 장을 완료한 후**:
- ✨ 20개 이상의 핵심 명령어 습득
- ✨ 4가지 실무 시나리오 구현 가능
- ✨ 면접 질문 12개에 답변 가능
- ✨ 주니어 개발자 흔한 실수 4가지 예방
- ✨ FAQ 8개 완벽 숙지

**성장률**: 📈 **400% 향상!**

---

### 🎓 인증서 (스스로에게)

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│             🏆 Redis 기본 조작 마스터 인증 🏆          │
│                                                     │
│   이 인증서는 아래의 개발자가 Redis의 기본 조작을      │
│   완벽하게 마스터했음을 스스로 인정합니다.            │
│                                                     │
│   - SET, GET, DEL 등 핵심 명령어 완전 숙지          │
│   - TTL 기반 자동 메모리 관리 구현 능력              │
│   - 실무 4가지 시나리오 해결 경험                    │
│   - 면접 질문 12개 답변 준비 완료                    │
│   - FAQ 8개 항목 완벽 이해                          │
│                                                     │
│   인증 날짜: ___________________                     │
│                                                     │
│   개발자 서명: ___________________                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

### 🚀 지금 바로 해보세요!

**실습 챌린지 (5분)**:
```bash
# 1. 세션 생성 (30분 만료)
SETEX session:my-test 1800 "test-session"

# 2. 세션 확인
GET session:my-test

# 3. 남은 시간 확인
TTL session:my-test

# 4. 세션 연장
EXPIRE session:my-test 1800

# 5. 세션 삭제
DEL session:my-test

# 성공했다면 축하합니다! 🎉
```

---

### 💌 마지막 한마디

Redis 기본 조작은 모든 Redis 활용의 **기초**입니다.

이 기초가 탄탄해야 다음 단계로 나아갈 수 있습니다.

**당신은 이미 충분히 훌륭합니다.**

지금까지 배운 내용만으로도 실무에서 사용하는 Redis 작업의 **70%**를 커버할 수 있습니다.

**자신감을 가지세요!**

다음 장에서는 String 타입의 고급 기능을 배우며 더욱 강력한 Redis 개발자가 됩니다.

**당신의 Redis 여정을 응원합니다!** 🚀

---

**다음 장에서 만나요!** 👋

---

**다음 장으로 이동**: [4. String 타입 완전 가이드](./04-String-타입-완전-가이드.md)

**이전 장으로 돌아가기**: [2. Redis 설치 및 환경 설정](./02-Redis-설치-및-환경-설정.md)

**목차로 돌아가기**: [Redis 완전 학습 가이드](./redis%20가이드.md)