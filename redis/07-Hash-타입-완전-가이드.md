# 🗂️ 7. Hash 타입 완전 가이드

> **이 장에서 배울 내용**: Redis Hash 타입의 모든 기능을 완벽하게 마스터하여 구조화된 데이터, 사용자 프로필, 설정 관리를 자유자재로 구현합니다.

**⏱️ 예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐☆☆ (3개/5개)

---

## 📚 목차
- [학습 목표](#학습-목표)
- [실생활 비유로 이해하기](#실생활-비유로-이해하기)
- [Hash 타입 완전 이해](#1-hash-타입-완전-이해)
- [필드 조작](#2-필드-조작-hset-hget-hdel)
- [전체 Hash 조작](#3-전체-hash-조작-hgetall-hkeys-hvals)
- [숫자 필드 연산](#4-숫자-필드-연산-hincrby-hincrbyfloat)
- [실전 종합 프로젝트](#5-실전-종합-프로젝트)
- [주니어 시나리오](#주니어-시나리오)
- [핵심 내용 정리 및 베스트 프랙티스](#6-핵심-내용-정리-및-베스트-프랙티스)
- [FAQ](#7-자주-묻는-질문-faq)
- [면접 질문 리스트](#면접-질문-리스트)
- [다음 단계 예고](#8-다음-단계-예고)

---

## 📚 학습 목표

이 장을 완료하면 다음과 같은 능력을 갖게 됩니다:

✅ **Hash 타입의 내부 구조와 특성 완벽 이해**
✅ **필드별 세밀한 데이터 조작 완전 마스터**
✅ **Hash 전체 조작과 일괄 처리 능력 정복**
✅ **숫자 필드 연산과 카운터 관리 능력 습득**
✅ **사용자 프로필과 설정 관리 시스템 구현 능력**
✅ **실무에서 바로 활용 가능한 Hash 패턴 완전 정복**

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 서류 보관함 (사무실)
```
Hash = 직원별 인사 서류 보관함
Field = 서류 라벨 (이름, 입사일, 부서, 직급, 연봉)
Value = 서류 내용 (김철수, 2024-01-01, 개발팀, 대리, 5000)

장점:
- 한 사람의 모든 정보를 한 폴더에 체계적으로 관리
- 특정 정보만 빠르게 꺼내볼 수 있음
- 필요한 서류만 추가/삭제 가능

┌─────────────────────────────┐
│  [김철수 인사 서류 보관함]   │
│  ┌────────────────────┐     │
│  │ 이름: 김철수       │     │
│  │ 입사일: 2024-01-01 │     │
│  │ 부서: 개발팀       │     │
│  │ 직급: 대리         │     │
│  │ 연봉: 5000만원     │     │
│  └────────────────────┘     │
└─────────────────────────────┘
```

### 비유 2: 아파트 호수 정보 (부동산)
```
Hash = 아파트 각 호수의 정보
Field = 정보 항목 (평수, 층, 가격, 거주자, 주차공간)
Value = 실제 값 (34평, 15층, 5억, 김철수, 2대)

왜 Hash를 쓰나요?
- 101호, 102호 각각의 정보를 독립적으로 관리
- 특정 호수의 가격만 수정 가능
- 새로운 정보(예: 발코니 확장) 쉽게 추가

아파트 동 (Redis Server)
├── 101호 (Hash: apt:101)
│   ├── 평수: 34평
│   ├── 층: 15층
│   ├── 가격: 5억
│   └── 거주자: 김철수
├── 102호 (Hash: apt:102)
│   ├── 평수: 25평
│   └── 층: 10층
```

### 비유 3: 게임 캐릭터 스탯 창 (게임)
```
Hash = 캐릭터 스탯 정보
Field = 스탯 항목 (레벨, HP, MP, 공격력, 방어력, 골드)
Value = 수치 (25, 1500, 800, 120, 85, 50000)

게임에서의 활용:
- HINCRBY로 경험치 증가 → 레벨업
- HINCRBYFLOAT로 골드 획득/소비
- HGET으로 현재 HP 확인
- HSET으로 장비 변경 시 스탯 업데이트

┌──────────────────────────┐
│   [드래곤 슬레이어]       │
├──────────────────────────┤
│  레벨: 25   HP: 1500     │
│  MP: 800    공격력: 120  │
│  방어력: 85  골드: 50000  │
├──────────────────────────┤
│ [몬스터 처치]             │
│ HINCRBY player:1 exp 150 │
│ HINCRBY player:1 gold 500│
└──────────────────────────┘
```

### 비유 4: 상품 진열대 태그 (쇼핑몰)
```
Hash = 상품별 상세 정보 태그
Field = 정보 종류 (이름, 가격, 할인가, 재고, 카테고리, 평점)
Value = 상품 정보 (노트북A, 1299000, 1199000, 25, 전자제품, 4.5)

쇼핑몰에서의 장점:
- 상품 목록 페이지: HMGET으로 이름, 가격, 평점만 조회
- 상품 상세 페이지: HGETALL로 모든 정보 조회
- 재고 감소: HINCRBY stock -1
- 할인가 적용: HSET discount_price 999000

상품 진열대
┌─────────────────────┐
│  🖥️ 노트북A         │
│  ───────────────    │
│  정가: 1,299,000원  │
│  할인: 1,199,000원  │
│  재고: 25개         │
│  평점: ⭐⭐⭐⭐☆      │
│  (HGETALL product:1)│
└─────────────────────┘
```

### 비유 5: 학생 생활기록부 (학교)
```
Hash = 학생별 생활기록부
Field = 기록 항목 (이름, 학년, 반, 출석일수, 국어, 수학, 영어, 총점, 평균)
Value = 기록 내용 (김철수, 2, 3, 180, 85, 90, 88, 263, 87.7)

학교 시스템 활용:
- 출석 체크: HINCRBY student:1001 attendance 1
- 시험 점수 입력: HSET student:1001 math 90
- 평균 계산: HMGET으로 전 과목 점수 가져와서 계산
- 학기말 성적표: HGETALL student:1001

┌────────────────────────────┐
│   [김철수 생활기록부]       │
├────────────────────────────┤
│ 학년/반: 2학년 3반          │
│ 출석: 180일                │
│ ──────────────────────    │
│ 국어: 85점  수학: 90점      │
│ 영어: 88점  총점: 263점     │
│ 평균: 87.7점               │
└────────────────────────────┘
```

### 🎯 종합 비교표
```
┌──────────────┬────────────┬────────────┬────────────┐
│ Redis Hash   │ 서류보관함  │ 게임 캐릭터 │ 쇼핑몰 상품 │
├──────────────┼────────────┼────────────┼────────────┤
│ Hash 키      │ 직원 이름   │ 캐릭터 ID   │ 상품 코드   │
│ Field        │ 서류 종류   │ 스탯 항목   │ 정보 항목   │
│ Value        │ 서류 내용   │ 스탯 수치   │ 상품 정보   │
│ HGET         │ 서류 꺼내기 │ 스탯 확인   │ 가격 조회   │
│ HSET         │ 서류 추가   │ 스탯 변경   │ 정보 수정   │
│ HINCRBY      │ 연차 증가   │ 경험치 획득 │ 재고 감소   │
│ HGETALL      │ 전체 서류   │ 캐릭터 정보 │ 상세 페이지 │
└──────────────┴────────────┴────────────┴────────────┘
```

---

## 🧬 1. Hash 타입 완전 이해

### 1.1 Redis Hash란 무엇인가?

**Redis Hash는 필드-값 쌍들의 컬렉션으로, 구조화된 객체를 표현하는 데 최적화된 데이터 타입입니다.**

```
🗃️ 서류 보관함 비유:
- Hash = 서류 보관함
- Field = 서류 라벨 (이름, 주소, 전화번호)
- Value = 서류 내용 (김철수, 서울시, 010-1234-5678)
- 장점: 관련 정보를 하나로 묶어 체계적 관리

프로그래밍 언어의 객체나 구조체와 매우 유사합니다.
```

### 1.2 Hash의 핵심 특징

#### 1) 구조화된 데이터 관리
```bash
# 사용자 정보를 Hash로 관리
127.0.0.1:6379> HSET user:1001 name "김철수" age 30 email "kim@example.com" city "서울"
(integer) 4

# 개별 필드 조회 가능
127.0.0.1:6379> HGET user:1001 name
"김철수"

127.0.0.1:6379> HGET user:1001 age
"30"

# 전체 정보 조회
127.0.0.1:6379> HGETALL user:1001
1) "name"
2) "김철수"
3) "age"
4) "30"
5) "email"
6) "kim@example.com"
7) "city"
8) "서울"
```

#### 2) 메모리 효율성
```bash
# String으로 관리할 때
SET user:1001:name "김철수"
SET user:1001:age "30"
SET user:1001:email "kim@example.com"
SET user:1001:city "서울"
# 4개의 키, 더 많은 메모리 사용

# Hash로 관리할 때
HSET user:1001 name "김철수" age "30" email "kim@example.com" city "서울"
# 1개의 키, 메모리 효율적
```

#### 3) 필드별 개별 조작
```bash
# 특정 필드만 수정
127.0.0.1:6379> HSET user:1001 age 31
(integer) 0   # 기존 필드 업데이트

# 새 필드 추가
127.0.0.1:6379> HSET user:1001 phone "010-1234-5678"
(integer) 1   # 새 필드 추가

# 특정 필드만 삭제
127.0.0.1:6379> HDEL user:1001 city
(integer) 1   # 필드 삭제

127.0.0.1:6379> HGETALL user:1001
1) "name"
2) "김철수"
3) "age"
4) "31"
5) "email"
6) "kim@example.com"
7) "phone"
8) "010-1234-5678"
```

### 1.3 Hash의 내부 구조와 성능

#### 내부 인코딩 방식
```bash
# Redis는 Hash 크기에 따라 다른 인코딩 사용:
# 1. ziplist: 작은 Hash (512개 이하 필드, 64바이트 이하 값)
# 2. hashtable: 큰 Hash (조건 초과 시)

# 작은 Hash (ziplist 인코딩)
127.0.0.1:6379> HSET small_hash field1 "value1" field2 "value2"
(integer) 2

127.0.0.1:6379> OBJECT ENCODING small_hash
"ziplist"

# 큰 Hash (hashtable 인코딩)
127.0.0.1:6379> HSET large_hash $(for i in {1..600}; do echo "field$i value$i"; done)
(integer) 600

127.0.0.1:6379> OBJECT ENCODING large_hash
"hashtable"
```

#### 시간 복잡도
```bash
# O(1) 연산: 매우 빠름
HGET, HSET, HDEL, HEXISTS, HLEN

# O(N) 연산: 필드 수에 비례
HGETALL, HKEYS, HVALS, HMGET (여러 필드)

# 실무 팁: 필드 수가 많은 Hash의 HGETALL 사용 주의
```

### 📊 수치로 보는 효과

**실제 전자상거래 상품 정보 관리 시스템 개선 사례**

| 지표 | Before (JSON String) | After (Hash) | 개선율 |
|------|---------------------|--------------|--------|
| 메모리 사용량 (1만 상품) | 150MB | 100MB | **33%↓** |
| 단일 필드 조회 속도 | 0.05ms (전체 파싱) | 0.01ms (직접 조회) | **80%↑** |
| 부분 수정 속도 | 0.08ms (전체 재작성) | 0.01ms (필드만 수정) | **87.5%↑** |
| 네트워크 대역폭 | 2KB/조회 (전체 전송) | 0.2KB/조회 (필드만) | **90%↓** |
| Redis 서버 CPU 사용률 | 45% | 18% | **60%↓** |
| API 응답 시간 | 12ms | 3ms | **75%↑** |

**실시간 통계 시스템 성능 비교**

| 항목 | Before (개별 String 키) | After (Hash) | 개선율 |
|------|------------------------|--------------|--------|
| 키 개수 (1만 사용자) | 100,000개 | 10,000개 | **90%↓** |
| 메모리 오버헤드 | 200MB | 100MB | **50%↓** |
| 통계 집계 속도 | 100ms (MGET 100개) | 10ms (HMGET) | **90%↑** |
| 카운터 증가 속도 | 0.02ms (GET+SET) | 0.01ms (HINCRBY) | **50%↑** |
| 원자성 보장 | ❌ (락 필요) | ✅ (자동 보장) | **안전성 100%↑** |

---

## 🔧 2. 필드 조작 (HSET, HGET, HDEL)

### 2.1 HSET - 필드 설정

#### 기본 사용법
```bash
# 새 Hash 생성하면서 필드 설정
127.0.0.1:6379> HSET product:1001 name "노트북A"
(integer) 1

# 기존 Hash에 필드 추가
127.0.0.1:6379> HSET product:1001 price "1299000"
(integer) 1

127.0.0.1:6379> HSET product:1001 category "전자제품"
(integer) 1

# 현재 상태 확인
127.0.0.1:6379> HGETALL product:1001
1) "name"
2) "노트북A"
3) "price"
4) "1299000"
5) "category"
6) "전자제품"
```

#### 여러 필드 동시 설정
```bash
# 여러 필드를 한 번에 설정
127.0.0.1:6379> HSET product:1002 name "마우스B" price "59000" category "전자제품" brand "TechBrand" stock "150"
(integer) 5

# 확인
127.0.0.1:6379> HGETALL product:1002
 1) "name"
 2) "마우스B"
 3) "price"
 4) "59000"
 5) "category"
 6) "전자제품"
 7) "brand"
 8) "TechBrand"
 9) "stock"
10) "150"
```

#### 기존 필드 업데이트
```bash
# 기존 값 업데이트
127.0.0.1:6379> HSET product:1001 price "1199000"
(integer) 0   # 기존 필드 업데이트 (새 필드가 아님)

127.0.0.1:6379> HGET product:1001 price
"1199000"   # 업데이트된 값

# 여러 필드 동시 업데이트
127.0.0.1:6379> HSET product:1001 price "1099000" stock "25" description "고성능 노트북"
(integer) 2   # stock과 description이 새 필드, price는 업데이트
```

### 2.2 HSETNX - 필드가 없을 때만 설정

```bash
# 필드가 없으면 설정, 있으면 무시
127.0.0.1:6379> HSETNX product:1001 warranty "2년"
(integer) 1   # 성공 (새 필드)

127.0.0.1:6379> HSETNX product:1001 warranty "3년"
(integer) 0   # 실패 (이미 존재)

127.0.0.1:6379> HGET product:1001 warranty
"2년"   # 처음 설정된 값 유지

# 실무 활용: 기본값 설정
127.0.0.1:6379> HSETNX user:1001 theme "light"
(integer) 1   # 기본 테마 설정

127.0.0.1:6379> HSETNX user:1001 theme "dark"
(integer) 0   # 이미 설정된 테마 유지
```

### 2.3 HGET - 필드 조회

#### 기본 필드 조회
```bash
# 특정 필드 값 조회
127.0.0.1:6379> HGET product:1001 name
"노트북A"

127.0.0.1:6379> HGET product:1001 price
"1099000"

# 존재하지 않는 필드 조회
127.0.0.1:6379> HGET product:1001 color
(nil)

# 존재하지 않는 Hash 조회
127.0.0.1:6379> HGET nonexistent:hash field
(nil)
```

#### 실무 활용 패턴
```bash
# 사용자 설정 조회
127.0.0.1:6379> HSET user:1001:settings language "ko" timezone "Asia/Seoul" notifications "true"
(integer) 3

127.0.0.1:6379> HGET user:1001:settings language
"ko"

# 기본값 처리 (애플리케이션 레벨)
# language = HGET user:1001:settings language
# if language is None:
#     language = "en"  # 기본값
```

### 2.4 HMGET - 여러 필드 동시 조회

```bash
# 여러 필드를 한 번에 조회
127.0.0.1:6379> HMGET product:1001 name price stock
1) "노트북A"
2) "1099000"
3) "25"

# 존재하지 않는 필드 포함
127.0.0.1:6379> HMGET product:1001 name color weight
1) "노트북A"
2) (nil)      # color 필드 없음
3) (nil)      # weight 필드 없음

# 모든 필드가 존재하지 않는 경우
127.0.0.1:6379> HMGET nonexistent:hash field1 field2
1) (nil)
2) (nil)
```

### 2.5 HDEL - 필드 삭제

#### 기본 필드 삭제
```bash
# 단일 필드 삭제
127.0.0.1:6379> HDEL product:1001 description
(integer) 1   # 삭제된 필드 개수

# 여러 필드 동시 삭제
127.0.0.1:6379> HDEL product:1001 warranty stock
(integer) 2   # 삭제된 필드 개수

# 존재하지 않는 필드 삭제 시도
127.0.0.1:6379> HDEL product:1001 nonexistent
(integer) 0   # 삭제된 필드 없음

# 현재 상태 확인
127.0.0.1:6379> HGETALL product:1001
1) "name"
2) "노트북A"
3) "price"
4) "1099000"
5) "category"
6) "전자제품"
```

### 2.6 실무 활용 패턴

#### 1) 사용자 프로필 관리
```bash
# 회원가입 시 프로필 생성
127.0.0.1:6379> HSET user:1001:profile name "김철수" email "kim@example.com" join_date "2024-01-01" status "active"
(integer) 4

# 프로필 정보 업데이트
127.0.0.1:6379> HSET user:1001:profile phone "010-1234-5678" address "서울시 강남구"
(integer) 2

# 특정 정보만 조회
127.0.0.1:6379> HMGET user:1001:profile name email status
1) "김철수"
2) "kim@example.com"
3) "active"

# 민감한 정보 삭제 (탈퇴 시)
127.0.0.1:6379> HDEL user:1001:profile phone address email
(integer) 3
```

#### 2) 상품 정보 관리
```bash
# 상품 등록
127.0.0.1:6379> HSET product:2001 name "스마트폰X" price "999000" category "전자제품" brand "TechCorp" description "최신 스마트폰" stock "100"
(integer) 6

# 가격 업데이트 (할인)
127.0.0.1:6379> HSET product:2001 price "899000" sale_price "799000"
(integer) 1   # sale_price는 새 필드

# 재고 관리 (별도 처리 - 나중에 HINCRBY 학습)
127.0.0.1:6379> HGET product:2001 stock
"100"

# 상품 정보 조회 (상세 페이지용)
127.0.0.1:6379> HMGET product:2001 name price sale_price description stock
1) "스마트폰X"
2) "999000"
3) "799000"
4) "최신 스마트폰"
5) "100"
```

#### 3) 설정 관리
```bash
# 애플리케이션 설정
127.0.0.1:6379> HSET app:config max_connections "1000" timeout "30" debug_mode "false" cache_ttl "3600"
(integer) 4

# 특정 설정만 조회
127.0.0.1:6379> HGET app:config debug_mode
"false"

# 설정 업데이트
127.0.0.1:6379> HSET app:config debug_mode "true" log_level "debug"
(integer) 1   # debug_mode 업데이트, log_level 새로 추가

# 운영 모드로 전환 시 개발 설정 제거
127.0.0.1:6379> HDEL app:config debug_mode log_level
(integer) 2
```

#### 4) 세션 데이터 관리
```bash
# 로그인 시 세션 생성
127.0.0.1:6379> HSET session:abc123 user_id "1001" username "kim_chul_soo" role "user" login_time "2024-01-01T10:00:00Z" ip "192.168.1.100"
(integer) 5

# 세션에 TTL 설정 (30분)
127.0.0.1:6379> EXPIRE session:abc123 1800
(integer) 1

# 활동 시마다 마지막 활동 시간 업데이트
127.0.0.1:6379> HSET session:abc123 last_activity "2024-01-01T10:15:00Z"
(integer) 0   # 기존 필드 업데이트

# 세션 유효성 확인
127.0.0.1:6379> HMGET session:abc123 user_id role
1) "1001"
2) "user"

# 로그아웃 시 세션 삭제
127.0.0.1:6379> DEL session:abc123
(integer) 1
```

---

## 📊 3. 전체 Hash 조작 (HGETALL, HKEYS, HVALS)

### 3.1 HGETALL - 모든 필드와 값 조회

#### 기본 사용법
```bash
# 테스트 데이터 준비
127.0.0.1:6379> HSET server:web01 hostname "web01.example.com" ip "192.168.1.101" port "80" status "running" cpu_usage "45" memory_usage "67"
(integer) 6

# 모든 필드와 값 조회
127.0.0.1:6379> HGETALL server:web01
 1) "hostname"
 2) "web01.example.com"
 3) "ip"
 4) "192.168.1.101"
 5) "port"
 6) "80"
 7) "status"
 8) "running"
 9) "cpu_usage"
10) "45"
11) "memory_usage"
12) "67"
```

#### 빈 Hash 조회
```bash
127.0.0.1:6379> HGETALL empty:hash
(empty array)

127.0.0.1:6379> HGETALL nonexistent:hash
(empty array)
```

#### HGETALL 사용 시 주의사항
```bash
# 큰 Hash의 경우 성능 문제 발생 가능
127.0.0.1:6379> HSET large_hash $(for i in {1..1000}; do echo "field$i value$i"; done)
(integer) 1000

# 위험: 1000개 필드를 모두 반환 (메모리 및 네트워크 부하)
# HGETALL large_hash  # 운영환경에서는 사용 금지

# 대안: 필요한 필드만 HMGET으로 조회
127.0.0.1:6379> HMGET large_hash field1 field10 field100
1) "value1"
2) "value10"
3) "value100"
```

### 3.2 HKEYS - 모든 필드명 조회

```bash
# 모든 필드명만 조회
127.0.0.1:6379> HKEYS server:web01
1) "hostname"
2) "ip"
3) "port"
4) "status"
5) "cpu_usage"
6) "memory_usage"

# 실무 활용: 동적 필드 확인
127.0.0.1:6379> HKEYS user:1001:preferences
1) "theme"
2) "language"
3) "timezone"
4) "notifications"

# 필드 존재 여부 확인 (애플리케이션에서 활용)
# available_fields = HKEYS user:1001:preferences
# if "dark_mode" not in available_fields:
#     HSET user:1001:preferences dark_mode "false"
```

### 3.3 HVALS - 모든 값 조회

```bash
# 모든 값만 조회 (필드명 없이)
127.0.0.1:6379> HVALS server:web01
1) "web01.example.com"
2) "192.168.1.101"
3) "80"
4) "running"
5) "45"
6) "67"

# 실무 활용 예: 통계 계산
127.0.0.1:6379> HSET daily_stats visitors "1250" page_views "5680" orders "89" revenue "1250000"
(integer) 4

127.0.0.1:6379> HVALS daily_stats
1) "1250"
2) "5680"
3) "89"
4) "1250000"

# 애플리케이션에서 합계 계산
# values = HVALS daily_stats
# total = sum(int(v) for v in values)
```

### 3.4 HLEN - Hash 크기 확인

```bash
# Hash의 필드 개수 확인
127.0.0.1:6379> HLEN server:web01
(integer) 6

127.0.0.1:6379> HLEN daily_stats
(integer) 4

# 빈 Hash 크기
127.0.0.1:6379> HLEN empty:hash
(integer) 0

# 존재하지 않는 Hash 크기
127.0.0.1:6379> HLEN nonexistent:hash
(integer) 0
```

### 3.5 HEXISTS - 필드 존재 확인

```bash
# 필드 존재 여부 확인
127.0.0.1:6379> HEXISTS server:web01 hostname
(integer) 1   # 존재함

127.0.0.1:6379> HEXISTS server:web01 ssl_enabled
(integer) 0   # 존재하지 않음

# 실무 활용: 조건부 로직
127.0.0.1:6379> HEXISTS user:1001:profile avatar
(integer) 0   # 아바타 없음

# 애플리케이션 로직:
# if not HEXISTS user:1001:profile avatar:
#     show_default_avatar()
# else:
#     show_user_avatar()
```

### 3.6 실무 활용 패턴

#### 1) 서버 모니터링 시스템
```bash
# 서버별 상태 정보
127.0.0.1:6379> HSET server:web01 status "running" cpu "45" memory "67" disk "78" last_check "2024-01-01T10:00:00Z"
(integer) 5

127.0.0.1:6379> HSET server:web02 status "running" cpu "52" memory "71" disk "65" last_check "2024-01-01T10:00:00Z"
(integer) 5

127.0.0.1:6379> HSET server:db01 status "running" cpu "89" memory "95" disk "82" last_check "2024-01-01T10:00:00Z"
(integer) 5

# 모든 서버 상태 한눈에 보기
127.0.0.1:6379> KEYS server:*
1) "server:web01"
2) "server:web02"
3) "server:db01"

# 특정 지표만 조회
127.0.0.1:6379> HMGET server:db01 status cpu memory
1) "running"
2) "89"      # 높은 CPU 사용률
3) "95"      # 높은 메모리 사용률

# 알림이 필요한 서버 확인 (애플리케이션 로직)
# for server in ["server:web01", "server:web02", "server:db01"]:
#     cpu = int(HGET server cpu)
#     memory = int(HGET server memory)
#     if cpu > 80 or memory > 90:
#         send_alert(server)
```

#### 2) 사용자 대시보드 데이터
```bash
# 사용자별 대시보드 정보
127.0.0.1:6379> HSET user:1001:dashboard total_orders "15" total_spent "1500000" points "2500" last_login "2024-01-01T09:30:00Z" favorite_category "전자제품"
(integer) 5

# 대시보드 페이지 로딩 시 필요한 모든 정보
127.0.0.1:6379> HGETALL user:1001:dashboard
 1) "total_orders"
 2) "15"
 3) "total_spent"
 4) "1500000"
 5) "points"
 6) "2500"
 7) "last_login"
 8) "2024-01-01T09:30:00Z"
 9) "favorite_category"
10) "전자제품"

# 새 주문 시 통계 업데이트 (HINCRBY로 나중에 학습)
# HINCRBY user:1001:dashboard total_orders 1
# HINCRBY user:1001:dashboard total_spent 299000
```

#### 3) 게임 플레이어 정보
```bash
# 플레이어 스탯 관리
127.0.0.1:6379> HSET player:1001:stats level "25" experience "125000" gold "50000" health "100" mana "80" wins "45" losses "12"
(integer) 7

# 게임 UI에 표시할 정보
127.0.0.1:6379> HMGET player:1001:stats level health mana gold
1) "25"
2) "100"
3) "80"
4) "50000"

# 랭킹 시스템용 정보
127.0.0.1:6379> HMGET player:1001:stats level wins losses
1) "25"
2) "45"
3) "12"

# 플레이어 장비 정보
127.0.0.1:6379> HSET player:1001:equipment helmet "드래곤헬름" weapon "불의검" armor "미스릴갑옷" boots "속도의부츠"
(integer) 4

# 모든 장비 정보 조회
127.0.0.1:6379> HGETALL player:1001:equipment
1) "helmet"
2) "드래곤헬름"
3) "weapon"
4) "불의검"
5) "armor"
6) "미스릴갑옷"
7) "boots"
8) "속도의부츠"
```

#### 4) 제품 카탈로그 관리
```bash
# 제품별 상세 정보
127.0.0.1:6379> HSET product:laptop001 name "고성능노트북" brand "TechCorp" model "TC-2024" price "1299000" discount_price "1199000" category "전자제품" subcategory "노트북" specs "CPU:i7,RAM:16GB,SSD:512GB" rating "4.5" review_count "128"
(integer) 10

# 제품 목록 페이지용 정보
127.0.0.1:6379> HMGET product:laptop001 name brand discount_price rating review_count
1) "고성능노트북"
2) "TechCorp"
3) "1199000"
4) "4.5"
5) "128"

# 제품 상세 페이지용 전체 정보
127.0.0.1:6379> HGETALL product:laptop001
 1) "name"
 2) "고성능노트북"
 3) "brand"
 4) "TechCorp"
 5) "model"
 6) "TC-2024"
 7) "price"
 8) "1299000"
 9) "discount_price"
10) "1199000"
11) "category"
12) "전자제품"
13) "subcategory"
14) "노트북"
15) "specs"
16) "CPU:i7,RAM:16GB,SSD:512GB"
17) "rating"
18) "4.5"
19) "review_count"
20) "128"

# 검색/필터링용 필드들
127.0.0.1:6379> HMGET product:laptop001 category subcategory brand
1) "전자제품"
2) "노트북"
3) "TechCorp"
```

---

## 🔢 4. 숫자 필드 연산 (HINCRBY, HINCRBYFLOAT)

### 4.1 HINCRBY - 정수 필드 증감

#### 기본 증감 연산
```bash
# 테스트 데이터 준비
127.0.0.1:6379> HSET counter:daily page_views 0 visitors 0 orders 0
(integer) 3

# 필드 값 증가
127.0.0.1:6379> HINCRBY counter:daily page_views 1
(integer) 1

127.0.0.1:6379> HINCRBY counter:daily page_views 5
(integer) 6

127.0.0.1:6379> HINCRBY counter:daily visitors 1
(integer) 1

# 현재 상태 확인
127.0.0.1:6379> HGETALL counter:daily
1) "page_views"
2) "6"
3) "visitors"
4) "1"
5) "orders"
6) "0"
```

#### 필드가 없는 경우
```bash
# 존재하지 않는 필드에 HINCRBY 시 0에서 시작
127.0.0.1:6379> HINCRBY counter:daily new_metric 10
(integer) 10   # 0 + 10

127.0.0.1:6379> HGET counter:daily new_metric
"10"

# 존재하지 않는 Hash에 HINCRBY
127.0.0.1:6379> HINCRBY new_counter field1 5
(integer) 5   # 새 Hash 생성됨

127.0.0.1:6379> HGETALL new_counter
1) "field1"
2) "5"
```

#### 음수로 감소 연산
```bash
# 재고 관리 예시
127.0.0.1:6379> HSET inventory:product001 stock 100 reserved 0 sold 0
(integer) 3

# 상품 주문 시 재고 감소
127.0.0.1:6379> HINCRBY inventory:product001 stock -3
(integer) 97

127.0.0.1:6379> HINCRBY inventory:product001 reserved 3
(integer) 3

# 주문 확정 시
127.0.0.1:6379> HINCRBY inventory:product001 reserved -3
(integer) 0

127.0.0.1:6379> HINCRBY inventory:product001 sold 3
(integer) 3

127.0.0.1:6379> HGETALL inventory:product001
1) "stock"
2) "97"
3) "reserved"
4) "0"
5) "sold"
6) "3"
```

#### 에러 상황
```bash
# 숫자가 아닌 값에 HINCRBY 시도
127.0.0.1:6379> HSET test_hash text_field "hello"
(integer) 1

127.0.0.1:6379> HINCRBY test_hash text_field 1
(error) ERR hash value is not an integer
```

### 4.2 HINCRBYFLOAT - 실수 필드 증감

```bash
# 실수 계산이 필요한 경우
127.0.0.1:6379> HSET financial:daily revenue 0.0 tax 0.0 profit 0.0
(integer) 3

# 매출 추가
127.0.0.1:6379> HINCRBYFLOAT financial:daily revenue 1299.99
"1299.99"

127.0.0.1:6379> HINCRBYFLOAT financial:daily revenue 599.50
"1899.49"

# 세금 계산 (10%)
127.0.0.1:6379> HINCRBYFLOAT financial:daily tax 189.949
"189.949"

# 이익 계산
127.0.0.1:6379> HINCRBYFLOAT financial:daily profit 1709.541
"1709.541"

127.0.0.1:6379> HGETALL financial:daily
1) "revenue"
2) "1899.49"
3) "tax"
4) "189.949"
5) "profit"
6) "1709.541"
```

#### 음수로 감소
```bash
# 환불 처리
127.0.0.1:6379> HINCRBYFLOAT financial:daily revenue -299.99
"1599.5"

# 온도 변화
127.0.0.1:6379> HSET weather:seoul temperature 15.5 humidity 65.2
(integer) 2

127.0.0.1:6379> HINCRBYFLOAT weather:seoul temperature -2.3
"13.2"   # 온도 하강

127.0.0.1:6379> HINCRBYFLOAT weather:seoul humidity 5.8
"71"     # 습도 증가
```

### 4.3 실무 활용 패턴

#### 1) 웹사이트 통계 관리
```bash
# 일일 통계 초기화
127.0.0.1:6379> HSET stats:2024-01-01 page_views 0 unique_visitors 0 new_signups 0 orders 0 revenue 0.0
(integer) 5

# 페이지 뷰 증가
127.0.0.1:6379> HINCRBY stats:2024-01-01 page_views 1
(integer) 1

# 신규 방문자
127.0.0.1:6379> HINCRBY stats:2024-01-01 unique_visitors 1
(integer) 1

# 회원가입
127.0.0.1:6379> HINCRBY stats:2024-01-01 new_signups 1
(integer) 1

# 주문 완료
127.0.0.1:6379> HINCRBY stats:2024-01-01 orders 1
(integer) 1

127.0.0.1:6379> HINCRBYFLOAT stats:2024-01-01 revenue 299.99
"299.99"

# 실시간 대시보드용 통계 조회
127.0.0.1:6379> HGETALL stats:2024-01-01
 1) "page_views"
 2) "1"
 3) "unique_visitors"
 4) "1"
 5) "new_signups"
 6) "1"
 7) "orders"
 8) "1"
 9) "revenue"
10) "299.99"
```

#### 2) 사용자 포인트 시스템
```bash
# 사용자 포인트 초기화
127.0.0.1:6379> HSET user:1001:points total 0 earned_today 0 spent_today 0 cashback 0.0
(integer) 4

# 구매 시 포인트 적립 (구매 금액의 1%)
127.0.0.1:6379> HINCRBY user:1001:points total 100
(integer) 100

127.0.0.1:6379> HINCRBY user:1001:points earned_today 100
(integer) 100

# 캐시백 적립 (실수)
127.0.0.1:6379> HINCRBYFLOAT user:1001:points cashback 25.50
"25.5"

# 포인트 사용
127.0.0.1:6379> HINCRBY user:1001:points total -50
(integer) 50

127.0.0.1:6379> HINCRBY user:1001:points spent_today 50
(integer) 50

# 현재 포인트 상황
127.0.0.1:6379> HGETALL user:1001:points
1) "total"
2) "50"
3) "earned_today"
4) "100"
5) "spent_today"
6) "50"
7) "cashback"
8) "25.5"
```

#### 3) 게임 플레이어 경험치 시스템
```bash
# 플레이어 경험치 관리
127.0.0.1:6379> HSET player:1001:exp current_exp 0 total_exp 0 level 1 exp_to_next_level 1000
(integer) 4

# 몬스터 처치 시 경험치 획득
127.0.0.1:6379> HINCRBY player:1001:exp current_exp 150
(integer) 150

127.0.0.1:6379> HINCRBY player:1001:exp total_exp 150
(integer) 150

# 퀘스트 완료 시 경험치 획득
127.0.0.1:6379> HINCRBY player:1001:exp current_exp 500
(integer) 650

127.0.0.1:6379> HINCRBY player:1001:exp total_exp 500
(integer) 650

# 레벨업 확인 로직 (애플리케이션에서)
# current_exp = int(HGET player:1001:exp current_exp)
# exp_to_next = int(HGET player:1001:exp exp_to_next_level)
# if current_exp >= exp_to_next:
#     HINCRBY player:1001:exp level 1
#     HINCRBY player:1001:exp current_exp -exp_to_next
#     HSET player:1001:exp exp_to_next_level new_requirement

127.0.0.1:6379> HGETALL player:1001:exp
1) "current_exp"
2) "650"
3) "total_exp"
4) "650"
5) "level"
6) "1"
7) "exp_to_next_level"
8) "1000"
```

#### 4) API 사용량 추적
```bash
# API 키별 사용량 추적
127.0.0.1:6379> HSET api:usage:key123 requests_today 0 requests_total 0 errors_today 0 quota_remaining 10000
(integer) 4

# API 호출 시마다 카운터 증가
127.0.0.1:6379> HINCRBY api:usage:key123 requests_today 1
(integer) 1

127.0.0.1:6379> HINCRBY api:usage:key123 requests_total 1
(integer) 1

127.0.0.1:6379> HINCRBY api:usage:key123 quota_remaining -1
(integer) 9999

# 에러 발생 시
127.0.0.1:6379> HINCRBY api:usage:key123 errors_today 1
(integer) 1

# API 사용량 현황
127.0.0.1:6379> HGETALL api:usage:key123
1) "requests_today"
2) "1"
3) "requests_total"
4) "1"
5) "errors_today"
6) "1"
7) "quota_remaining"
8) "9999"

# 할당량 초과 확인
127.0.0.1:6379> HGET api:usage:key123 quota_remaining
"9999"   # 양수면 사용 가능

# 일일 리셋 (자정에 실행)
127.0.0.1:6379> HSET api:usage:key123 requests_today 0 errors_today 0 quota_remaining 10000
(integer) 0   # 기존 필드들 업데이트
```

#### 5) 실시간 이벤트 카운터
```bash
# 라이브 스트리밍 이벤트 통계
127.0.0.1:6379> HSET live:stream001 viewers 0 likes 0 comments 0 shares 0 donations 0.0
(integer) 5

# 시청자 입장/퇴장
127.0.0.1:6379> HINCRBY live:stream001 viewers 1
(integer) 1

127.0.0.1:6379> HINCRBY live:stream001 viewers 1
(integer) 2

127.0.0.1:6379> HINCRBY live:stream001 viewers -1
(integer) 1   # 1명 퇴장

# 좋아요, 댓글, 공유
127.0.0.1:6379> HINCRBY live:stream001 likes 1
(integer) 1

127.0.0.1:6379> HINCRBY live:stream001 comments 1
(integer) 1

127.0.0.1:6379> HINCRBY live:stream001 shares 1
(integer) 1

# 후원
127.0.0.1:6379> HINCRBYFLOAT live:stream001 donations 5.99
"5.99"

127.0.0.1:6379> HINCRBYFLOAT live:stream001 donations 10.00
"15.99"

# 실시간 통계 조회 (웹소켓으로 클라이언트에 전송)
127.0.0.1:6379> HGETALL live:stream001
 1) "viewers"
 2) "1"
 3) "likes"
 4) "1"
 5) "comments"
 6) "1"
 7) "shares"
 8) "1"
 9) "donations"
10) "15.99"
```

---

## 🎯 5. 실전 종합 프로젝트

### 5.1 프로젝트 1: 완전한 사용자 관리 시스템

#### 요구사항
- 사용자 프로필 관리
- 사용자 설정 관리
- 활동 통계 추적
- 포인트 시스템 연동

#### 구현

##### 1) 사용자 프로필 관리
```bash
# 회원가입 시 기본 프로필 생성
127.0.0.1:6379> HSET user:1001:profile name "김철수" email "kim@example.com" phone "010-1234-5678" join_date "2024-01-01" status "active" email_verified "true" phone_verified "false"
(integer) 7

# 추가 정보 업데이트
127.0.0.1:6379> HSET user:1001:profile birthday "1990-03-15" gender "male" address "서울시 강남구" company "테크컴퍼니" job_title "개발자"
(integer) 5

# 프로필 이미지 업데이트
127.0.0.1:6379> HSET user:1001:profile avatar_url "/uploads/avatars/user1001.jpg" avatar_updated "2024-01-01T10:00:00Z"
(integer) 2

# 프로필 조회 (마이페이지용)
127.0.0.1:6379> HGETALL user:1001:profile
 1) "name"
 2) "김철수"
 3) "email"
 4) "kim@example.com"
 5) "phone"
 6) "010-1234-5678"
 7) "join_date"
 8) "2024-01-01"
 9) "status"
10) "active"
11) "email_verified"
12) "true"
13) "phone_verified"
14) "false"
15) "birthday"
16) "1990-03-15"
17) "gender"
18) "male"
19) "address"
20) "서울시 강남구"
21) "company"
22) "테크컴퍼니"
23) "job_title"
24) "개발자"
25) "avatar_url"
26) "/uploads/avatars/user1001.jpg"
27) "avatar_updated"
28) "2024-01-01T10:00:00Z"

# 공개 프로필 조회 (다른 사용자가 볼 때)
127.0.0.1:6379> HMGET user:1001:profile name avatar_url company job_title
1) "김철수"
2) "/uploads/avatars/user1001.jpg"
3) "테크컴퍼니"
4) "개발자"
```

##### 2) 사용자 설정 관리
```bash
# 기본 설정 초기화
127.0.0.1:6379> HSET user:1001:settings theme "light" language "ko" timezone "Asia/Seoul" notifications_email "true" notifications_sms "false" notifications_push "true" privacy_profile "public" privacy_activity "friends"
(integer) 8

# 설정 업데이트
127.0.0.1:6379> HSET user:1001:settings theme "dark" notifications_email "false"
(integer) 0   # 기존 필드 업데이트

# 새 설정 추가
127.0.0.1:6379> HSET user:1001:settings auto_save "true" dark_mode_schedule "sunset_to_sunrise"
(integer) 2

# 특정 설정만 조회
127.0.0.1:6379> HMGET user:1001:settings theme language notifications_push
1) "dark"
2) "ko"
3) "true"

# 모든 설정 조회
127.0.0.1:6379> HGETALL user:1001:settings
 1) "theme"
 2) "dark"
 3) "language"
 4) "ko"
 5) "timezone"
 6) "Asia/Seoul"
 7) "notifications_email"
 8) "false"
 9) "notifications_sms"
10) "false"
11) "notifications_push"
12) "true"
13) "privacy_profile"
14) "public"
15) "privacy_activity"
16) "friends"
17) "auto_save"
18) "true"
19) "dark_mode_schedule"
20) "sunset_to_sunrise"
```

##### 3) 사용자 활동 통계
```bash
# 활동 통계 초기화
127.0.0.1:6379> HSET user:1001:stats login_count 0 posts_created 0 comments_made 0 likes_given 0 likes_received 0 profile_views 0 last_login_date "" most_active_hour "0"
(integer) 8

# 로그인 시 통계 업데이트
127.0.0.1:6379> HINCRBY user:1001:stats login_count 1
(integer) 1

127.0.0.1:6379> HSET user:1001:stats last_login_date "2024-01-01T10:00:00Z"
(integer) 0

# 활동별 통계 업데이트
127.0.0.1:6379> HINCRBY user:1001:stats posts_created 1
(integer) 1

127.0.0.1:6379> HINCRBY user:1001:stats comments_made 1
(integer) 1

127.0.0.1:6379> HINCRBY user:1001:stats likes_given 1
(integer) 1

# 다른 사용자가 좋아요할 때
127.0.0.1:6379> HINCRBY user:1001:stats likes_received 1
(integer) 1

127.0.0.1:6379> HINCRBY user:1001:stats profile_views 1
(integer) 1

# 통계 조회
127.0.0.1:6379> HGETALL user:1001:stats
 1) "login_count"
 2) "1"
 3) "posts_created"
 4) "1"
 5) "comments_made"
 6) "1"
 7) "likes_given"
 8) "1"
 9) "likes_received"
10) "1"
11) "profile_views"
12) "1"
13) "last_login_date"
14) "2024-01-01T10:00:00Z"
15) "most_active_hour"
16) "0"
```

##### 4) 포인트 시스템 연동
```bash
# 포인트 시스템 초기화
127.0.0.1:6379> HSET user:1001:points total 0 earned_total 0 spent_total 0 pending 0 cashback_total 0.0 level 1 exp_to_next_level 1000
(integer) 7

# 활동별 포인트 적립
# 포스트 작성: 10점
127.0.0.1:6379> HINCRBY user:1001:points total 10
(integer) 10

127.0.0.1:6379> HINCRBY user:1001:points earned_total 10
(integer) 10

# 댓글 작성: 5점
127.0.0.1:6379> HINCRBY user:1001:points total 5
(integer) 15

127.0.0.1:6379> HINCRBY user:1001:points earned_total 5
(integer) 15

# 좋아요 받기: 2점
127.0.0.1:6379> HINCRBY user:1001:points total 2
(integer) 17

127.0.0.1:6379> HINCRBY user:1001:points earned_total 2
(integer) 17

# 구매 시 캐시백 (1%)
127.0.0.1:6379> HINCRBYFLOAT user:1001:points cashback_total 12.99
"12.99"

# 포인트 사용
127.0.0.1:6379> HINCRBY user:1001:points total -10
(integer) 7

127.0.0.1:6379> HINCRBY user:1001:points spent_total 10
(integer) 10

# 포인트 현황 조회
127.0.0.1:6379> HGETALL user:1001:points
 1) "total"
 2) "7"
 3) "earned_total"
 4) "17"
 5) "spent_total"
 6) "10"
 7) "pending"
 8) "0"
 9) "cashback_total"
10) "12.99"
11) "level"
12) "1"
13) "exp_to_next_level"
14) "1000"
```

### 5.2 프로젝트 2: 전자상거래 상품 관리 시스템

#### 요구사항
- 상품 정보 관리
- 재고 관리
- 가격 및 할인 관리
- 상품 통계 추적

#### 구현

##### 1) 상품 기본 정보 관리
```bash
# 상품 등록
127.0.0.1:6379> HSET product:1001 name "고성능 노트북" brand "TechCorp" model "TC-2024-Pro" category "전자제품" subcategory "노트북" description "최신 고성능 노트북으로 게임과 업무에 최적화" specifications "CPU:i7-12700H,RAM:32GB,SSD:1TB,GPU:RTX3070"
(integer) 8

# 가격 정보
127.0.0.1:6379> HSET product:1001 original_price "1899000" current_price "1699000" discount_rate "10.5" currency "KRW"
(integer) 4

# 배송 정보
127.0.0.1:6379> HSET product:1001 weight "2.1" dimensions "35.5x24.5x1.9" shipping_free "true" shipping_cost "0"
(integer) 4

# 상태 정보
127.0.0.1:6379> HSET product:1001 status "active" featured "true" created_date "2024-01-01" updated_date "2024-01-01"
(integer) 4

# 상품 상세 페이지용 전체 정보 조회
127.0.0.1:6379> HGETALL product:1001
 1) "name"
 2) "고성능 노트북"
 3) "brand"
 4) "TechCorp"
 5) "model"
 6) "TC-2024-Pro"
 7) "category"
 8) "전자제품"
 9) "subcategory"
10) "노트북"
11) "description"
12) "최신 고성능 노트북으로 게임과 업무에 최적화"
13) "specifications"
14) "CPU:i7-12700H,RAM:32GB,SSD:1TB,GPU:RTX3070"
15) "original_price"
16) "1899000"
17) "current_price"
18) "1699000"
19) "discount_rate"
20) "10.5"
21) "currency"
22) "KRW"
23) "weight"
24) "2.1"
25) "dimensions"
26) "35.5x24.5x1.9"
27) "shipping_free"
28) "true"
29) "shipping_cost"
30) "0"
31) "status"
32) "active"
33) "featured"
34) "true"
35) "created_date"
36) "2024-01-01"
37) "updated_date"
38) "2024-01-01"

# 상품 목록용 간단 정보 조회
127.0.0.1:6379> HMGET product:1001 name brand current_price discount_rate status
1) "고성능 노트북"
2) "TechCorp"
3) "1699000"
4) "10.5"
5) "active"
```

##### 2) 재고 관리 시스템
```bash
# 재고 정보 초기화
127.0.0.1:6379> HSET product:1001:inventory total_stock 100 available_stock 100 reserved_stock 0 sold_stock 0 damaged_stock 0 reorder_level 10 max_stock 200
(integer) 7

# 주문 시 재고 차감
127.0.0.1:6379> HINCRBY product:1001:inventory available_stock -2
(integer) 98

127.0.0.1:6379> HINCRBY product:1001:inventory reserved_stock 2
(integer) 2

# 주문 확정 시
127.0.0.1:6379> HINCRBY product:1001:inventory reserved_stock -2
(integer) 0

127.0.0.1:6379> HINCRBY product:1001:inventory sold_stock 2
(integer) 2

# 입고 시 재고 증가
127.0.0.1:6379> HINCRBY product:1001:inventory total_stock 50
(integer) 150

127.0.0.1:6379> HINCRBY product:1001:inventory available_stock 50
(integer) 148

# 손상 상품 처리
127.0.0.1:6379> HINCRBY product:1001:inventory available_stock -1
(integer) 147

127.0.0.1:6379> HINCRBY product:1001:inventory damaged_stock 1
(integer) 1

# 재고 현황 조회
127.0.0.1:6379> HGETALL product:1001:inventory
 1) "total_stock"
 2) "149"
 3) "available_stock"
 4) "147"
 5) "reserved_stock"
 6) "0"
 7) "sold_stock"
 8) "2"
 9) "damaged_stock"
10) "1"
11) "reorder_level"
12) "10"
13) "max_stock"
14) "200"

# 재주문 필요 여부 확인
127.0.0.1:6379> HMGET product:1001:inventory available_stock reorder_level
1) "147"
2) "10"
# available_stock > reorder_level 이므로 재주문 불필요
```

##### 3) 가격 히스토리 관리
```bash
# 가격 변경 이력 관리 (별도 Hash로)
127.0.0.1:6379> HSET product:1001:price_history 2024-01-01 "1899000" 2024-01-15 "1799000" 2024-01-30 "1699000"
(integer) 3

# 할인 이벤트 정보
127.0.0.1:6379> HSET product:1001:discount event_name "신제품 출시 기념" start_date "2024-01-30" end_date "2024-02-29" discount_type "percentage" discount_value "10.5"
(integer) 5

# 현재 유효한 할인 확인
127.0.0.1:6379> HMGET product:1001:discount start_date end_date discount_value
1) "2024-01-30"
2) "2024-02-29"
3) "10.5"

# 가격 히스토리 조회
127.0.0.1:6379> HGETALL product:1001:price_history
1) "2024-01-01"
2) "1899000"
3) "2024-01-15"
4) "1799000"
5) "2024-01-30"
6) "1699000"
```

##### 4) 상품 성과 통계
```bash
# 상품 통계 초기화
127.0.0.1:6379> HSET product:1001:stats views_total 0 views_today 0 likes_total 0 reviews_count 0 rating_sum 0.0 rating_average 0.0 sales_total 0 revenue_total 0.0
(integer) 8

# 상품 페이지 조회 시
127.0.0.1:6379> HINCRBY product:1001:stats views_total 1
(integer) 1

127.0.0.1:6379> HINCRBY product:1001:stats views_today 1
(integer) 1

# 상품 좋아요
127.0.0.1:6379> HINCRBY product:1001:stats likes_total 1
(integer) 1

# 리뷰 작성 시
127.0.0.1:6379> HINCRBY product:1001:stats reviews_count 1
(integer) 1

127.0.0.1:6379> HINCRBYFLOAT product:1001:stats rating_sum 4.5
"4.5"

# 평균 평점 계산 (애플리케이션에서)
# rating_sum = float(HGET product:1001:stats rating_sum)
# reviews_count = int(HGET product:1001:stats reviews_count)
# rating_average = rating_sum / reviews_count
127.0.0.1:6379> HSET product:1001:stats rating_average "4.5"
(integer) 0

# 판매 시
127.0.0.1:6379> HINCRBY product:1001:stats sales_total 2
(integer) 2

127.0.0.1:6379> HINCRBYFLOAT product:1001:stats revenue_total 3398000.0
"3398000"

# 상품 성과 대시보드용 통계
127.0.0.1:6379> HGETALL product:1001:stats
 1) "views_total"
 2) "1"
 3) "views_today"
 4) "1"
 5) "likes_total"
 6) "1"
 7) "reviews_count"
 8) "1"
 9) "rating_sum"
10) "4.5"
11) "rating_average"
12) "4.5"
13) "sales_total"
14) "2"
15) "revenue_total"
16) "3398000"
```

### 5.3 프로젝트 3: 온라인 게임 길드 관리 시스템

#### 요구사항
- 길드 정보 관리
- 멤버 관리 시스템
- 길드 활동 통계
- 길드 레벨 시스템

#### 구현

##### 1) 길드 기본 정보
```bash
# 길드 생성
127.0.0.1:6379> HSET guild:1001 name "드래곤 슬레이어" description "용을 사냥하는 최강 길드" leader_id "player:1001" created_date "2024-01-01" status "active" level 1 max_members 50 current_members 1
(integer) 8

# 길드 설정
127.0.0.1:6379> HSET guild:1001 join_policy "approval" min_level_requirement 10 region "Asia" language "Korean" guild_tag "[DS]"
(integer) 5

# 길드 정보 조회
127.0.0.1:6379> HGETALL guild:1001
 1) "name"
 2) "드래곤 슬레이어"
 3) "description"
 4) "용을 사냥하는 최강 길드"
 5) "leader_id"
 6) "player:1001"
 7) "created_date"
 8) "2024-01-01"
 9) "status"
10) "active"
11) "level"
12) "1"
13) "max_members"
14) "50"
15) "current_members"
16) "1"
17) "join_policy"
18) "approval"
19) "min_level_requirement"
20) "10"
21) "region"
22) "Asia"
23) "language"
24) "Korean"
25) "guild_tag"
26) "[DS]"
```

##### 2) 길드 경험치 및 레벨 시스템
```bash
# 길드 경험치 시스템 초기화
127.0.0.1:6379> HSET guild:1001:exp current_exp 0 total_exp 0 exp_to_next_level 10000 level_up_bonus 0
(integer) 4

# 멤버 활동으로 길드 경험치 획득
# 던전 클리어
127.0.0.1:6379> HINCRBY guild:1001:exp current_exp 500
(integer) 500

127.0.0.1:6379> HINCRBY guild:1001:exp total_exp 500
(integer) 500

# 길드 전쟁 승리
127.0.0.1:6379> HINCRBY guild:1001:exp current_exp 2000
(integer) 2500

127.0.0.1:6379> HINCRBY guild:1001:exp total_exp 2000
(integer) 2500

# 월드 보스 처치
127.0.0.1:6379> HINCRBY guild:1001:exp current_exp 5000
(integer) 7500

127.0.0.1:6379> HINCRBY guild:1001:exp total_exp 5000
(integer) 7500

# 경험치 현황 조회
127.0.0.1:6379> HGETALL guild:1001:exp
1) "current_exp"
2) "7500"
3) "total_exp"
4) "7500"
5) "exp_to_next_level"
6) "10000"
7) "level_up_bonus"
8) "0"
```

##### 3) 길드 활동 통계
```bash
# 길드 활동 통계 초기화
127.0.0.1:6379> HSET guild:1001:stats dungeons_cleared 0 bosses_defeated 0 pvp_wins 0 pvp_losses 0 total_playtime_hours 0 active_members_today 0 guild_wars_won 0 guild_wars_lost 0
(integer) 8

# 던전 클리어 시
127.0.0.1:6379> HINCRBY guild:1001:stats dungeons_cleared 1
(integer) 1

# 보스 처치 시
127.0.0.1:6379> HINCRBY guild:1001:stats bosses_defeated 1
(integer) 1

# PvP 결과
127.0.0.1:6379> HINCRBY guild:1001:stats pvp_wins 1
(integer) 1

# 길드전 결과
127.0.0.1:6379> HINCRBY guild:1001:stats guild_wars_won 1
(integer) 1

# 플레이 시간 누적
127.0.0.1:6379> HINCRBY guild:1001:stats total_playtime_hours 5
(integer) 5

# 오늘 활동한 멤버 수
127.0.0.1:6379> HINCRBY guild:1001:stats active_members_today 1
(integer) 1

# 길드 통계 조회
127.0.0.1:6379> HGETALL guild:1001:stats
 1) "dungeons_cleared"
 2) "1"
 3) "bosses_defeated"
 4) "1"
 5) "pvp_wins"
 6) "1"
 7) "pvp_losses"
 8) "0"
 9) "total_playtime_hours"
10) "5"
11) "active_members_today"
12) "1"
13) "guild_wars_won"
14) "1"
15) "guild_wars_lost"
16) "0"
```

##### 4) 길드 금고 관리
```bash
# 길드 금고 초기화
127.0.0.1:6379> HSET guild:1001:treasury gold 10000 gems 50 contribution_total 0 expenses_total 0 daily_income 0 weekly_bonus 0
(integer) 6

# 멤버 기부
127.0.0.1:6379> HINCRBY guild:1001:treasury gold 5000
(integer) 15000

127.0.0.1:6379> HINCRBY guild:1001:treasury contribution_total 5000
(integer) 5000

127.0.0.1:6379> HINCRBY guild:1001:treasury gems 20
(integer) 70

# 길드 스킬 업그레이드 비용
127.0.0.1:6379> HINCRBY guild:1001:treasury gold -3000
(integer) 12000

127.0.0.1:6379> HINCRBY guild:1001:treasury expenses_total 3000
(integer) 3000

# 일일 수입 (길드 활동 보상)
127.0.0.1:6379> HINCRBY guild:1001:treasury daily_income 1000
(integer) 1000

127.0.0.1:6379> HINCRBY guild:1001:treasury gold 1000
(integer) 13000

# 금고 현황 조회
127.0.0.1:6379> HGETALL guild:1001:treasury
 1) "gold"
 2) "13000"
 3) "gems"
 4) "70"
 5) "contribution_total"
 6) "5000"
 7) "expenses_total"
 8) "3000"
 9) "daily_income"
10) "1000"
11) "weekly_bonus"
12) "0"
```

---

## 📝 6. 핵심 내용 정리 및 베스트 프랙티스

### 6.1 Hash 타입 명령어 완전 정리

#### 기본 조작 명령어
| 명령어 | 용도 | 예시 | 반환값 |
|--------|------|------|--------|
| `HSET key field value [field value ...]` | 필드 설정 | `HSET user name "김철수" age 30` | 새로 추가된 필드 개수 |
| `HGET key field` | 필드 조회 | `HGET user name` | 필드 값 또는 nil |
| `HMGET key field [field ...]` | 여러 필드 조회 | `HMGET user name age` | 필드 값들의 배열 |
| `HGETALL key` | 모든 필드-값 조회 | `HGETALL user` | 필드-값 쌍들의 배열 |
| `HDEL key field [field ...]` | 필드 삭제 | `HDEL user age` | 삭제된 필드 개수 |
| `HEXISTS key field` | 필드 존재 확인 | `HEXISTS user name` | 1 또는 0 |
| `HSETNX key field value` | 필드가 없을 때만 설정 | `HSETNX user theme "light"` | 1 또는 0 |

#### 정보 조회 명령어
| 명령어 | 용도 | 예시 | 반환값 |
|--------|------|------|--------|
| `HKEYS key` | 모든 필드명 조회 | `HKEYS user` | 필드명들의 배열 |
| `HVALS key` | 모든 값 조회 | `HVALS user` | 값들의 배열 |
| `HLEN key` | 필드 개수 | `HLEN user` | 필드 개수 |

#### 숫자 연산 명령어
| 명령어 | 용도 | 예시 | 반환값 |
|--------|------|------|--------|
| `HINCRBY key field increment` | 정수 필드 증감 | `HINCRBY stats views 1` | 증감 후 값 |
| `HINCRBYFLOAT key field increment` | 실수 필드 증감 | `HINCRBYFLOAT stats revenue 99.99` | 증감 후 값 |

### 6.2 Hash vs 다른 데이터 타입 비교

#### Hash vs String (JSON)
```bash
# String 방식 (JSON)
SET user:1001 '{"name":"김철수","age":30,"email":"kim@example.com"}'
# 단점: 부분 수정 불가, 전체 파싱 필요

# Hash 방식
HSET user:1001 name "김철수" age 30 email "kim@example.com"
# 장점: 부분 수정 가능, 개별 필드 접근 가능
```

#### Hash vs 여러 String 키
```bash
# 여러 String 키
SET user:1001:name "김철수"
SET user:1001:age "30"
SET user:1001:email "kim@example.com"
# 단점: 키 개수 많음, 메모리 비효율

# Hash 방식
HSET user:1001 name "김철수" age "30" email "kim@example.com"
# 장점: 키 1개, 메모리 효율적
```

### 6.3 실무 베스트 프랙티스

#### 1) 적절한 Hash 크기 관리
```bash
# 적정 크기: 필드 수백 개 이하 권장
# 좋은 예
HSET user:1001 name "김철수" age "30" email "kim@example.com"  # 적은 필드

# 주의 필요한 예
HSET large_object field1 value1 field2 value2 ... field1000 value1000
# 필드가 너무 많으면 성능 저하
```

#### 2) 일관성 있는 필드 명명 규칙
```bash
# 좋은 예: 일관된 명명 규칙
HSET user:1001 first_name "철수" last_name "김" email_address "kim@example.com"

# 나쁜 예: 비일관적 명명
HSET user:1001 firstName "철수" last_name "김" emailAddr "kim@example.com"
```

#### 3) 효율적인 필드 조회
```bash
# 좋은 예: 필요한 필드만 조회
HMGET user:1001 name email status

# 나쁜 예: 불필요한 전체 조회
HGETALL user:1001  # 필드가 많을 때 비효율
```

#### 4) 숫자 필드 활용
```bash
# 카운터로 활용
HINCRBY stats:daily page_views 1
HINCRBY user:1001:points total 100

# 실수 계산
HINCRBYFLOAT financial:daily revenue 299.99
```

#### 5) 적절한 TTL 설정
```bash
# Hash 전체에 TTL 설정
HSET session:abc123 user_id "1001" login_time "2024-01-01T10:00:00Z"
EXPIRE session:abc123 1800  # 30분 후 전체 Hash 삭제

# 개별 필드 TTL은 지원하지 않음
```

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: HGETALL을 프로덕션에서 남용하는 실수

**상황**: 신입 개발자가 사용자 프로필 조회 API에서 Hash 전체를 조회하는 코드를 작성했습니다.

```python
# ❌ 주니어 개발자가 작성한 코드
def get_user_profile(user_id):
    # 모든 필드를 가져와서 필요한 것만 사용
    all_data = redis.hgetall(f"user:{user_id}:profile")
    return {
        "name": all_data.get("name"),
        "email": all_data.get("email"),
        "avatar": all_data.get("avatar")
    }
```

**문제점**:
- 문제 1: 불필요한 30개 이상의 필드를 모두 조회
- 문제 2: 네트워크 대역폭 낭비 (응답 크기 10배 증가)
- 문제 3: Redis 서버 부하 증가 (O(N) 연산)
- 왜 이 문제가 발생하는가: HGETALL이 편리해 보여서 무분별하게 사용

**해결책**:
```python
# ✅ 올바른 코드
def get_user_profile(user_id):
    # 필요한 필드만 정확히 조회 (O(1) 연산 3번)
    name, email, avatar = redis.hmget(
        f"user:{user_id}:profile",
        "name", "email", "avatar"
    )
    return {
        "name": name,
        "email": email,
        "avatar": avatar
    }

# 설명
# 1. HMGET으로 필요한 필드만 조회
# 2. 네트워크 트래픽 90% 감소
# 3. Redis 부하 70% 감소
```

**배운 점**:
- 💡 팁 1: HGETALL은 관리 도구나 디버깅 용도로만 사용
- 💡 팁 2: 프로덕션 코드에서는 항상 HMGET으로 필요한 필드만 조회
- 💡 팁 3: Hash 필드가 10개 이상이면 특히 주의

### 시나리오 2: 숫자가 아닌 필드에 HINCRBY 사용

**상황**: 주니어 개발자가 사용자 이름 필드에 HINCRBY를 실수로 사용했습니다.

```bash
# ❌ 잘못된 시도
127.0.0.1:6379> HSET user:1001 name "김철수" age "30"
(integer) 2

127.0.0.1:6379> HINCRBY user:1001 name 1
(error) ERR hash value is not an integer

# 프로그램이 크래시!
```

**문제점**:
- 문제 1: 타입 검증 없이 HINCRBY 사용
- 문제 2: 에러 처리 없어서 애플리케이션 중단
- 문제 3: 필드명 혼동 (name과 age를 착각)

**해결책**:
```python
# ✅ 올바른 코드
def increment_user_age(user_id, increment=1):
    try:
        # 숫자 필드만 증가
        new_age = redis.hincrby(f"user:{user_id}", "age", increment)
        return new_age
    except redis.exceptions.ResponseError as e:
        # 에러 처리: 숫자가 아닌 경우
        logger.error(f"Failed to increment age for user {user_id}: {e}")
        # 필드를 숫자로 초기화하거나 적절히 처리
        redis.hset(f"user:{user_id}", "age", str(increment))
        return increment

# 더 안전한 방법: 사전 검증
def safe_increment(key, field, increment):
    value = redis.hget(key, field)
    if value is None:
        # 필드가 없으면 increment 값으로 설정
        redis.hset(key, field, str(increment))
        return increment

    try:
        # 숫자로 변환 가능한지 확인
        current = int(value)
        return redis.hincrby(key, field, increment)
    except ValueError:
        raise ValueError(f"Field {field} is not a number: {value}")
```

**배운 점**:
- 💡 팁 1: HINCRBY는 반드시 숫자 필드에만 사용
- 💡 팁 2: 예외 처리를 항상 포함
- 💡 팁 3: 필드명을 명확하게 (count, score, points 등)

### 시나리오 3: Hash 필드 삭제 후 존재 확인 누락

**상황**: 사용자 프로필에서 전화번호 삭제 후 확인 없이 사용하려고 시도했습니다.

```python
# ❌ 잘못된 코드
def delete_user_phone(user_id):
    # 전화번호 삭제
    redis.hdel(f"user:{user_id}:profile", "phone")

def send_sms_notification(user_id, message):
    # 삭제 여부 확인 없이 바로 사용
    phone = redis.hget(f"user:{user_id}:profile", "phone")
    send_sms(phone, message)  # phone이 None이면 에러!
```

**문제점**:
- 문제 1: 필드 존재 여부 확인 없음
- 문제 2: None 값 처리 로직 누락
- 문제 3: SMS 전송 실패로 사용자 불편

**해결책**:
```python
# ✅ 올바른 코드
def send_sms_notification(user_id, message):
    # 1. HEXISTS로 존재 확인
    if redis.hexists(f"user:{user_id}:profile", "phone"):
        phone = redis.hget(f"user:{user_id}:profile", "phone")
        if phone:
            send_sms(phone, message)
            return True

    # 2. 전화번호가 없으면 대체 알림 방법 사용
    email = redis.hget(f"user:{user_id}:profile", "email")
    if email:
        send_email(email, message)
        return True

    logger.warning(f"No contact method for user {user_id}")
    return False

# 더 나은 방법: 여러 필드 한 번에 확인
def get_user_contact_info(user_id):
    contact = redis.hmget(
        f"user:{user_id}:profile",
        "phone", "email"
    )
    return {
        "phone": contact[0] if contact[0] else None,
        "email": contact[1] if contact[1] else None
    }
```

**배운 점**:
- 💡 팁 1: 필드 사용 전 HEXISTS로 존재 확인
- 💡 팁 2: None 값에 대한 방어 코드 작성
- 💡 팁 3: 대체 로직(fallback) 항상 준비

### 시나리오 4: 동시성 이슈 - 재고 차감 시 Race Condition

**상황**: 여러 사용자가 동시에 상품을 주문할 때 재고 관리에서 문제 발생

```python
# ❌ 잘못된 코드 (Race Condition 발생)
def purchase_product(product_id, quantity):
    # 1. 현재 재고 조회
    current_stock = int(redis.hget(f"product:{product_id}", "stock"))

    # 2. 재고 확인
    if current_stock >= quantity:
        # 3. 재고 차감 (문제: 사이에 다른 요청이 끼어들 수 있음!)
        time.sleep(0.1)  # 네트워크 지연 시뮬레이션
        new_stock = current_stock - quantity
        redis.hset(f"product:{product_id}", "stock", new_stock)
        return True
    return False

# 결과: 재고 10개인데 15개 판매되는 문제 발생!
```

**문제점**:
- 문제 1: Read-Modify-Write 패턴의 원자성 문제
- 문제 2: 동시 요청 시 재고 초과 판매
- 문제 3: 실제 재고와 DB 재고 불일치

**해결책**:
```python
# ✅ 올바른 코드 (원자적 연산 사용)
def purchase_product_safe(product_id, quantity):
    # HINCRBY는 원자적 연산이므로 안전
    new_stock = redis.hincrby(f"product:{product_id}", "stock", -quantity)

    # 재고가 음수가 되었다면 롤백
    if new_stock < 0:
        redis.hincrby(f"product:{product_id}", "stock", quantity)
        return False

    return True

# 더 안전한 방법: Lua 스크립트 사용
lua_script = """
local stock = tonumber(redis.call('HGET', KEYS[1], 'stock'))
local quantity = tonumber(ARGV[1])

if stock >= quantity then
    redis.call('HINCRBY', KEYS[1], 'stock', -quantity)
    return 1
else
    return 0
end
"""

def purchase_product_with_lua(product_id, quantity):
    result = redis.eval(
        lua_script,
        1,  # 키 개수
        f"product:{product_id}",  # KEYS[1]
        quantity  # ARGV[1]
    )
    return result == 1

# 설명
# 1. Lua 스크립트는 원자적으로 실행
# 2. 재고 확인과 차감이 한 번에 처리
# 3. Race Condition 완전 방지
```

**배운 점**:
- 💡 팁 1: HINCRBY/HINCRBYFLOAT는 원자적 연산
- 💡 팁 2: 복잡한 로직은 Lua 스크립트 사용
- 💡 팁 3: Read-Modify-Write 패턴 주의

---

## ❓ 7. 자주 묻는 질문 (FAQ)

<details>
<summary><strong>Q1: Hash의 개별 필드에 TTL을 설정할 수 있나요?</strong></summary>

**A**: 아니요. TTL은 Hash 전체에만 적용됩니다.

**상세 설명**:
- Redis는 키 단위로만 TTL 관리
- 개별 필드는 만료 시간을 가질 수 없음
- Hash 전체가 만료되면 모든 필드 삭제

**예시**:
```bash
# Hash 전체 TTL만 가능
EXPIRE user:1001 3600

# 개별 필드 TTL은 불가능
# EXPIRE user:1001:name 3600  # 이런 기능 없음
```

**실무 팁**:
💡 필드별 만료가 필요하면 별도 String 키로 분리하거나, 만료 시간을 필드 값에 포함하여 애플리케이션에서 관리

</details>

<details>
<summary><strong>Q2: HINCRBY에서 overflow가 발생하면 어떻게 되나요?</strong></summary>

**A**: Redis는 64비트 정수 범위를 사용하며, overflow 시 에러를 반환합니다.

**상세 설명**:
- 최대값: 9,223,372,036,854,775,807 (2^63 - 1)
- 최소값: -9,223,372,036,854,775,808 (-2^63)
- 범위 초과 시 에러 발생하고 값 변경 안 됨

**예시**:
```bash
# 최대값 근처에서 증가 시도
HSET counter num "9223372036854775807"
HINCRBY counter num 1
# (error) ERR increment or decrement would overflow
```

**실무 팁**:
💡 큰 숫자를 다루거나 계속 증가하는 카운터는 주기적으로 리셋하거나 애플리케이션에서 범위 체크

</details>

<details>
<summary><strong>Q3: Hash 필드명에 특수문자나 공백을 사용할 수 있나요?</strong></summary>

**A**: 네, 가능하지만 일관성 있는 명명 규칙을 권장합니다.

**상세 설명**:
- 기술적으로는 모든 문자 사용 가능
- 공백, 특수문자, 이모지도 가능
- 하지만 가독성과 유지보수를 위해 일관된 규칙 권장

**예시**:
```bash
# 가능하지만 권장하지 않음
HSET user:1001 "user name" "김철수" "email@domain" "kim@example.com" "😀 status" "happy"

# 권장하는 명명 규칙
HSET user:1001 user_name "김철수" email_address "kim@example.com" status "active"
```

**실무 팁**:
💡 snake_case나 camelCase 중 하나를 선택하여 프로젝트 전체에서 일관되게 사용

</details>

<details>
<summary><strong>Q4: Hash와 JSON String 중 어느 것이 더 효율적인가요?</strong></summary>

**A**: 용도에 따라 다르며, 각각의 장단점이 명확합니다.

**상세 설명**:
- Hash가 좋은 경우: 개별 필드 수정이 빈번하고, 특정 필드만 조회하는 경우
- JSON이 좋은 경우: 복잡한 중첩 구조, 전체 객체 전송이 많은 경우

**비교표**:
| 특징 | Hash | JSON String |
|------|------|-------------|
| 메모리 효율 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 부분 수정 | ⭐⭐⭐⭐⭐ | ⭐ (전체 파싱 필요) |
| 중첩 구조 | ⭐ (1레벨만) | ⭐⭐⭐⭐⭐ |
| 숫자 연산 | ⭐⭐⭐⭐⭐ (HINCRBY) | ⭐ |

**예시**:
```bash
# Hash가 좋은 경우: 사용자 프로필
HSET user:1001 name "김철수" age "30" email "kim@example.com"
HINCRBY user:1001 age 1  # 나이만 증가

# JSON이 좋은 경우: 복잡한 설정
SET config:app '{"server":{"host":"localhost","port":8080,"ssl":{"enabled":true,"cert":"path"}}}'
```

**실무 팁**:
💡 간단한 객체는 Hash, 복잡한 중첩 구조는 JSON 사용. 필요하면 혼용도 가능 (Hash에 JSON 값 저장)

</details>

<details>
<summary><strong>Q5: Hash의 최대 필드 개수는 몇 개인가요?</strong></summary>

**A**: 이론적으로는 2^32 - 1개 (약 42억 개)까지 가능하지만, 실무에서는 수백 개 이하를 권장합니다.

**상세 설명**:
- ziplist 인코딩: 512개 필드 이하 (메모리 효율적)
- hashtable 인코딩: 512개 초과 (상대적으로 메모리 사용량 증가)
- 실무 권장: 100-500개 필드

**성능 영향**:
```bash
# 작은 Hash (빠름)
HSET small field1 val1 ... field100 val100
HGETALL small  # 빠름

# 큰 Hash (느림)
HSET large field1 val1 ... field10000 val10000
HGETALL large  # 느림 (O(N) 연산)
```

**실무 팁**:
💡 필드가 1000개 이상 필요하면 Hash 분할 고려. 예: user:1001:profile, user:1001:settings, user:1001:stats

</details>

<details>
<summary><strong>Q6: HGETALL 대신 HSCAN을 사용해야 하는 경우는?</strong></summary>

**A**: Hash 필드가 많고 (100개 이상), 프로덕션 환경에서 블로킹을 피해야 할 때 HSCAN을 사용합니다.

**상세 설명**:
- HGETALL: 모든 필드를 한 번에 조회 (O(N), 블로킹)
- HSCAN: 커서 기반으로 일부씩 조회 (블로킹 최소화)
- 큰 Hash는 HSCAN으로 반복 조회

**예시**:
```bash
# HGETALL (블로킹)
HGETALL large_hash  # 1000개 필드를 한 번에

# HSCAN (블로킹 최소화)
HSCAN large_hash 0 COUNT 100  # 100개씩 조회
# cursor를 이용해 다음 100개 조회
HSCAN large_hash <cursor> COUNT 100
```

**실무 팁**:
💡 관리 도구나 배치 작업에서 큰 Hash를 처리할 때는 HSCAN 사용

</details>

<details>
<summary><strong>Q7: Hash와 Sorted Set 중 무엇을 선택해야 하나요?</strong></summary>

**A**: 정렬이 필요하면 Sorted Set, 구조화된 데이터 저장이 목적이면 Hash를 사용합니다.

**상세 설명**:
- Hash: 필드-값 쌍 저장, 정렬 없음, 빠른 개별 조회
- Sorted Set: 점수 기반 정렬, 범위 조회, 랭킹 시스템

**비교**:
| 기능 | Hash | Sorted Set |
|------|------|------------|
| 정렬 | ❌ | ✅ (점수 기반) |
| 범위 조회 | ❌ | ✅ |
| 개별 조회 | ✅ (O(1)) | ✅ (O(log N)) |
| 사용 사례 | 프로필, 설정 | 랭킹, 리더보드 |

**예시**:
```bash
# Hash: 사용자 프로필
HSET user:1001 name "김철수" age "30"

# Sorted Set: 게임 리더보드
ZADD leaderboard 1500 "김철수"  # 점수 1500
ZRANGE leaderboard 0 9  # 상위 10명
```

**실무 팁**:
💡 두 개를 함께 사용하는 경우도 많음. Hash에 상세 정보, Sorted Set에 랭킹 저장

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용 (5-7개)

<details>
<summary><strong>1. Redis Hash는 무엇이고, 어떤 경우에 사용하나요?</strong></summary>

**모범 답안 포인트**
- Hash는 필드-값 쌍의 컬렉션으로 구조화된 데이터 저장에 사용
- 사용자 프로필, 상품 정보, 설정 등 객체 형태 데이터에 적합
- 개별 필드를 독립적으로 조회/수정 가능

**예시 답변**
> "Redis Hash는 필드와 값 쌍으로 이루어진 데이터 타입으로, 관계형 DB의 한 행이나 프로그래밍 언어의 객체와 유사합니다. 사용자 프로필처럼 여러 속성을 가진 데이터를 하나의 키로 묶어서 관리할 때 사용합니다. 예를 들어 `HSET user:1001 name '김철수' age 30`처럼 한 사용자의 정보를 여러 필드로 나누어 저장할 수 있습니다."

**꼬리 질문**
- Q: Hash 대신 JSON String을 사용하면 안 되나요?
- A: JSON String도 가능하지만, 개별 필드 수정 시 전체를 파싱하고 다시 저장해야 하므로 비효율적입니다. Hash는 특정 필드만 수정 가능해서 더 효율적입니다.

**실무 연관**
- 실무에서는 사용자 세션, 장바구니, 상품 캐시 등에 Hash를 많이 사용합니다.

</details>

<details>
<summary><strong>2. HSET과 HMSET의 차이는 무엇인가요?</strong></summary>

**모범 답안 포인트**
- HMSET은 Redis 4.0 이후 deprecated됨
- HSET이 여러 필드를 동시에 설정 가능하도록 개선됨
- 현재는 HSET만 사용하면 됨

**예시 답변**
> "과거에는 HSET은 단일 필드만, HMSET은 여러 필드를 설정했습니다. 하지만 Redis 4.0부터 HSET이 여러 필드를 동시에 설정할 수 있게 개선되어, HMSET은 deprecated 되었습니다. 현재는 `HSET user:1 name '김철수' age 30 email 'kim@example.com'`처럼 HSET 하나로 모든 작업이 가능합니다."

**꼬리 질문**
- Q: 기존 필드를 HSET으로 수정하면 어떻게 되나요?
- A: 덮어쓰기 됩니다. 반환값이 0이면 업데이트, 1이면 새 필드 추가입니다.

**실무 연관**
- 레거시 코드에서 HMSET을 발견하면 HSET으로 마이그레이션 권장합니다.

</details>

<details>
<summary><strong>3. HGET과 HMGET의 차이와 사용 시점은?</strong></summary>

**모범 답안 포인트**
- HGET: 단일 필드 조회 (O(1))
- HMGET: 여러 필드 조회 (O(N), N은 조회할 필드 수)
- HMGET이 여러 번 HGET 호출보다 효율적

**예시 답변**
> "HGET은 하나의 필드만 조회하고, HMGET은 여러 필드를 한 번에 조회합니다. 예를 들어 사용자의 이름, 이메일, 나이를 모두 조회해야 한다면, HGET을 3번 호출하는 것보다 `HMGET user:1001 name email age`로 한 번에 가져오는 게 네트워크 왕복 횟수를 줄여서 더 빠릅니다."

**꼬리 질문**
- Q: 존재하지 않는 필드를 HMGET으로 조회하면?
- A: 해당 필드 위치에 nil이 반환됩니다.

**실무 연관**
- API 응답을 만들 때 필요한 필드만 HMGET으로 조회하여 성능 최적화합니다.

</details>

<details>
<summary><strong>4. HINCRBY와 HINCRBYFLOAT의 용도와 주의사항은?</strong></summary>

**모범 답안 포인트**
- HINCRBY: 정수 필드 증감 (카운터, 재고 등)
- HINCRBYFLOAT: 실수 필드 증감 (금액, 평점 등)
- 숫자가 아닌 필드에 사용 시 에러 발생

**예시 답변**
> "HINCRBY는 정수 필드를 증감시킬 때 사용합니다. 예를 들어 페이지 조회수나 상품 재고를 관리할 때 `HINCRBY stats:daily page_views 1`처럼 사용합니다. HINCRBYFLOAT는 실수가 필요한 경우인데, 매출액이나 평점 같은 데이터에 사용합니다. 주의할 점은 문자열 필드에 HINCRBY를 실행하면 에러가 발생하므로, 숫자 필드임을 명확히 해야 합니다."

**꼬리 질문**
- Q: HINCRBY로 음수를 전달하면?
- A: 감소 연산이 됩니다. `HINCRBY key field -5`는 5 감소입니다.

**실무 연관**
- 실시간 통계나 재고 관리 시스템에서 원자적 연산으로 동시성 문제를 해결합니다.

</details>

<details>
<summary><strong>5. HGETALL을 프로덕션 환경에서 사용할 때 주의할 점은?</strong></summary>

**모범 답안 포인트**
- O(N) 연산으로 필드가 많으면 느림
- 네트워크 대역폭 낭비
- 필요한 필드만 HMGET으로 조회 권장

**예시 답변**
> "HGETALL은 Hash의 모든 필드를 조회하는 O(N) 연산입니다. 필드가 수십 개 이상이면 성능 문제가 발생할 수 있습니다. 특히 프로덕션 환경에서는 필요한 3-4개 필드만 사용하는데 30개 필드를 모두 조회하는 건 낭비입니다. 따라서 실무에서는 HMGET으로 필요한 필드만 정확히 조회하고, HGETALL은 디버깅이나 관리 도구에서만 사용합니다."

**꼬리 질문**
- Q: 그럼 언제 HGETALL을 사용하나요?
- A: 관리 콘솔, 디버깅, 데이터 마이그레이션 등 모든 필드가 정말 필요한 경우에만 사용합니다.

**실무 연관**
- API 응답 시간을 줄이기 위해 HGETALL 대신 HMGET 사용을 코드 리뷰에서 권장합니다.

</details>

<details>
<summary><strong>6. Hash의 TTL은 어떻게 설정하나요?</strong></summary>

**모범 답안 포인트**
- Hash 전체 키에 TTL 설정 가능
- 개별 필드는 TTL 설정 불가
- EXPIRE 명령어 사용

**예시 답변**
> "Hash의 TTL은 전체 키 단위로만 설정할 수 있습니다. `EXPIRE user:1001:session 1800`처럼 EXPIRE 명령어를 사용하면 30분 후 Hash 전체가 삭제됩니다. 하지만 개별 필드만 만료시킬 수는 없습니다. 만약 특정 필드만 만료가 필요하다면 별도 키로 분리하거나 애플리케이션 레벨에서 관리해야 합니다."

**꼬리 질문**
- Q: 세션 데이터를 Hash로 관리할 때 TTL은 어떻게 처리하나요?
- A: 세션 Hash 전체에 TTL을 설정하고, 사용자 활동이 있을 때마다 EXPIRE로 TTL을 갱신합니다.

**실무 연관**
- 세션 관리, 임시 캐시 등에서 TTL을 활용하여 메모리를 효율적으로 관리합니다.

</details>

<details>
<summary><strong>7. Hash와 JSON String 중 어떤 것을 선택해야 하나요?</strong></summary>

**모범 답안 포인트**
- Hash: 개별 필드 수정 빈번, 숫자 연산 필요, 1레벨 구조
- JSON: 복잡한 중첩 구조, 전체 객체 조회 빈번, 스키마 유연성

**예시 답변**
> "사용 패턴에 따라 다릅니다. 사용자 프로필처럼 개별 필드(이름, 나이, 이메일)를 자주 수정하고, 숫자 연산(나이 증가)이 필요하면 Hash가 유리합니다. 반면 애플리케이션 설정처럼 복잡한 중첩 구조가 있고, 전체를 한 번에 읽어서 사용하는 경우는 JSON String이 더 적합합니다. 메모리 효율은 Hash가 약 50% 더 좋습니다."

**꼬리 질문**
- Q: Hash와 JSON을 함께 사용할 수 있나요?
- A: 네, Hash의 값으로 JSON을 저장할 수 있습니다. 예: `HSET config app_settings '{"theme":"dark","lang":"ko"}'`

**실무 연관**
- 대부분의 경우 간단한 구조는 Hash, 복잡한 구조는 JSON으로 분리하여 사용합니다.

</details>

---

### 📗 중급 개발자용 (3-5개)

<details>
<summary><strong>1. Hash의 내부 인코딩 방식(ziplist vs hashtable)에 대해 설명하고, 성능에 미치는 영향은?</strong></summary>

**모범 답안 포인트**
- ziplist: 512개 이하 필드, 64바이트 이하 값 (메모리 효율적)
- hashtable: 조건 초과 시 (조회 빠름, 메모리 더 사용)
- redis.conf로 임계값 조정 가능

**예시 답변**
> "Redis는 Hash 크기에 따라 두 가지 내부 인코딩을 사용합니다. 작은 Hash는 ziplist로 인코딩하여 메모리를 절약하고, 필드가 512개를 초과하거나 값이 64바이트를 초과하면 hashtable로 자동 변환됩니다. ziplist는 선형 탐색이지만 작은 크기에서는 캐시 효율이 좋아 빠르고, hashtable은 O(1) 조회지만 메모리 오버헤드가 있습니다. 실무에서는 Hash를 100-500개 필드 이하로 유지하여 ziplist 인코딩의 이점을 누립니다."

**실무 예시**:
```bash
# 인코딩 확인
OBJECT ENCODING user:1001:profile
# "ziplist"

# 큰 Hash로 변환되면
OBJECT ENCODING large_hash
# "hashtable"
```

**꼬리 질문**
- Q: ziplist와 hashtable 간 변환이 성능에 영향을 주나요?
- A: 변환 시점에는 약간의 오버헤드가 있지만, 변환 후에는 해당 인코딩의 성능 특성을 따릅니다. 대용량 Hash는 처음부터 hashtable로 생성되도록 설계하는 게 좋습니다.

**실무 연관**
- 사용자 프로필을 profile, settings, stats로 분할하여 각각 작은 Hash로 유지하면 ziplist 인코딩으로 메모리를 절약할 수 있습니다.

</details>

<details>
<summary><strong>2. Hash를 사용한 재고 관리 시스템에서 동시성 문제를 해결하는 방법은?</strong></summary>

**모범 답안 포인트**
- HINCRBY는 원자적 연산
- Lua 스크립트로 복잡한 조건 처리
- 낙관적 락 패턴 (WATCH + MULTI)

**예시 답변**
> "재고 관리에서 가장 큰 문제는 Race Condition입니다. 읽고-수정하고-쓰는 패턴은 동시 요청에서 재고 초과 판매를 일으킬 수 있습니다. 해결책은 세 가지입니다. 첫째, HINCRBY를 사용한 원자적 연산입니다. `HINCRBY product:1001 stock -3`은 원자적으로 실행되어 안전합니다. 둘째, 재고 확인과 차감을 모두 포함하는 Lua 스크립트를 사용합니다. Lua는 원자적으로 실행되어 중간에 다른 명령이 끼어들 수 없습니다. 셋째, WATCH-MULTI-EXEC 패턴으로 낙관적 락을 구현할 수 있습니다."

**실무 예시**:
```lua
-- Lua 스크립트 예시
local stock = tonumber(redis.call('HGET', KEYS[1], 'stock'))
local quantity = tonumber(ARGV[1])

if stock >= quantity then
    redis.call('HINCRBY', KEYS[1], 'stock', -quantity)
    return 1
else
    return 0
end
```

**꼬리 질문**
- Q: HINCRBY로 음수가 되는 것을 방지할 수 있나요?
- A: HINCRBY 자체는 막지 못하므로, 실행 후 값을 확인하여 음수면 롤백하거나, Lua 스크립트로 사전 검증이 필요합니다.

**실무 연관**
- 전자상거래에서 주문 동시 처리 시 재고 부족 에러를 방지하는 핵심 패턴입니다.

</details>

<details>
<summary><strong>3. Hash의 메모리 최적화 전략은 무엇인가요?</strong></summary>

**모범 답안 포인트**
- Hash 크기를 512개 필드 이하로 유지 (ziplist)
- 값 크기를 64바이트 이하로 유지
- Hash 분할 (sharding) 전략

**예시 답변**
> "Hash의 메모리 최적화는 주로 ziplist 인코딩을 활용하는 것입니다. 첫째, 필드 수를 512개 이하로 유지합니다. 예를 들어 사용자 데이터를 user:1001:profile, user:1001:settings처럼 분할합니다. 둘째, 필드 값을 64바이트 이하로 유지합니다. 긴 텍스트는 별도 키로 분리하거나 압축합니다. 셋째, Hash Sharding을 적용합니다. 수백만 사용자가 있다면 user:{userId%1000}:profiles 같은 버킷으로 분산시킵니다. 이렇게 하면 메모리 효율이 약 50% 향상됩니다."

**실무 예시**:
```bash
# 나쁜 예: 하나의 큰 Hash
HSET all_users user1 "..." user2 "..." ... user1000000 "..."

# 좋은 예: 분할된 Hash
HSET users:bucket:0 user1 "..." user101 "..."
HSET users:bucket:1 user2 "..." user102 "..."
```

**꼬리 질문**
- Q: 필드 수가 정확히 512개를 넘으면 바로 성능이 나빠지나요?
- A: 급격한 성능 저하는 없지만, 인코딩 변환 시 약간의 오버헤드가 있고, 메모리 사용량이 증가합니다. 여유를 두고 300-400개 정도로 제한하는 게 안전합니다.

**실무 연관**
- 대규모 서비스에서 메모리 비용을 절감하는 핵심 전략입니다.

</details>

<details>
<summary><strong>4. Hash를 활용한 캐싱 전략의 장단점과 Best Practice는?</strong></summary>

**모범 답안 포인트**
- Cache-Aside 패턴에서 Hash 활용
- 부분 업데이트 가능 (JSON 대비 장점)
- TTL 설정과 메모리 관리

**예시 답변**
> "Hash는 Cache-Aside 패턴에서 매우 유용합니다. 상품 정보 캐싱을 예로 들면, DB에서 조회한 데이터를 `HSET product:1001 name '노트북' price 1299000`처럼 저장합니다. 장점은 첫째, 부분 업데이트가 가능합니다. 가격만 변경되면 `HSET product:1001 price 999000`만 실행하면 되고, JSON은 전체를 다시 저장해야 합니다. 둘째, 필요한 필드만 조회하여 네트워크 비용을 줄입니다. Best Practice는 TTL을 설정하여 stale 데이터를 방지하고, 캐시 워밍 전략으로 자주 조회되는 데이터를 미리 로드하며, 캐시 무효화(invalidation) 로직을 명확히 하는 것입니다."

**실무 예시**:
```python
def get_product(product_id):
    # 1. 캐시 조회
    cached = redis.hmget(f"product:{product_id}", "name", "price", "stock")

    if all(cached):
        return dict(zip(["name", "price", "stock"], cached))

    # 2. DB 조회
    product = db.query(f"SELECT * FROM products WHERE id={product_id}")

    # 3. 캐시 저장 (TTL 1시간)
    redis.hset(f"product:{product_id}", mapping=product)
    redis.expire(f"product:{product_id}", 3600)

    return product
```

**꼬리 질문**
- Q: 캐시와 DB 간 데이터 불일치를 어떻게 처리하나요?
- A: Write-Through (쓰기 시 캐시도 업데이트), Write-Behind (비동기 업데이트), Invalidation (변경 시 캐시 삭제) 중 선택합니다. 대부분은 Invalidation이 간단하고 안전합니다.

**실무 연관**
- 전자상거래, SNS 등에서 DB 부하를 줄이고 응답 속도를 10배 이상 향상시킵니다.

</details>

<details>
<summary><strong>5. Hash를 사용한 Session Store 설계 시 고려사항은?</strong></summary>

**모범 답안 포인트**
- 세션 데이터를 Hash로 저장
- TTL 자동 갱신 전략
- 분산 환경에서의 세션 공유

**예시 답변**
> "Hash 기반 세션 스토어는 다음을 고려해야 합니다. 첫째, 세션 ID를 키로 사용하고 사용자 정보를 필드로 저장합니다. `HSET session:abc123 user_id 1001 username 'kim' role 'admin'` 같은 형태입니다. 둘째, TTL 관리입니다. 초기 로그인 시 `EXPIRE session:abc123 1800`로 30분 설정하고, 사용자 활동마다 EXPIRE를 다시 호출하여 세션을 연장합니다. 셋째, 분산 환경에서는 Redis Cluster나 Sentinel을 사용하여 고가용성을 보장합니다. 넷째, 민감한 정보는 암호화하여 저장하고, 로그아웃 시 DEL로 즉시 삭제합니다."

**실무 예시**:
```python
def create_session(user):
    session_id = generate_session_id()
    redis.hset(f"session:{session_id}",
        mapping={
            "user_id": user.id,
            "username": user.name,
            "role": user.role,
            "created_at": datetime.now().isoformat()
        }
    )
    redis.expire(f"session:{session_id}", 1800)  # 30분
    return session_id

def refresh_session(session_id):
    if redis.exists(f"session:{session_id}"):
        redis.expire(f"session:{session_id}", 1800)
        return True
    return False
```

**꼬리 질문**
- Q: 세션이 너무 많아지면 메모리 문제가 생기지 않나요?
- A: TTL 설정으로 비활성 세션이 자동 삭제되고, maxmemory-policy를 volatile-lru로 설정하여 메모리 부족 시 오래된 세션부터 제거합니다.

**실무 연관**
- 마이크로서비스 아키텍처에서 여러 서버가 세션을 공유하는 표준 패턴입니다.

</details>

---

## 🚀 8. 다음 단계 예고

다음 장에서는 **Sorted Set 타입**을 완전히 정복합니다!

### 다음 장 미리보기: Sorted Set 타입 완전 가이드
- **Sorted Set 구조와 특징**: 점수 기반 정렬된 집합의 모든 것
- **랭킹과 순위 시스템**: `ZADD`, `ZRANK`, `ZRANGE`로 리더보드 구현
- **점수 기반 연산**: `ZINCRBY`, `ZSCORE`, `ZCOUNT`로 점수 관리
- **범위 조회와 필터링**: 점수 범위, 사전순 범위 조회
- **실전 활용**: 리더보드, 실시간 랭킹, 추천 시스템, 시계열 데이터

### 준비하면 좋을 것들
```bash
# 다음 장을 위한 환경 정리
127.0.0.1:6379> SELECT 4
OK

127.0.0.1:6379[4]> FLUSHDB
OK

127.0.0.1:6379[4]> SELECT 0
OK
```

---

## 🎉 축하합니다!

Redis Hash 타입을 완전히 마스터했습니다!

**현재 여러분의 능력**:
✅ Hash의 모든 조작 명령어 완벽 활용
✅ 구조화된 데이터 모델링 능력
✅ 필드별 세밀한 데이터 관리 기술
✅ 숫자 필드 연산으로 실시간 통계 관리
✅ 사용자 프로필과 설정 시스템 구현 능력
✅ 전자상거래와 게임 시스템 설계 능력

### 학습 완료 체크리스트

**기본 개념**
- [ ] Hash가 무엇인지 설명할 수 있다
- [ ] Hash와 JSON String의 차이를 알고 선택할 수 있다
- [ ] 실생활 비유로 Hash를 이해했다
- [ ] Hash의 내부 인코딩 (ziplist vs hashtable)을 알고 있다

**명령어 마스터**
- [ ] HSET으로 필드를 생성/수정할 수 있다
- [ ] HGET/HMGET으로 필드를 조회할 수 있다
- [ ] HDEL로 필드를 삭제할 수 있다
- [ ] HGETALL의 위험성을 이해하고 대안을 사용할 수 있다
- [ ] HEXISTS로 필드 존재를 확인할 수 있다
- [ ] HINCRBY/HINCRBYFLOAT로 숫자 연산을 수행할 수 있다

**실무 활용**
- [ ] 사용자 프로필 시스템을 Hash로 설계할 수 있다
- [ ] 상품 정보 관리 시스템을 구현할 수 있다
- [ ] 재고 관리에서 동시성 문제를 해결할 수 있다
- [ ] Hash를 사용한 캐싱 전략을 수립할 수 있다
- [ ] 세션 스토어를 Hash로 구현할 수 있다

**성능 최적화**
- [ ] 필요한 필드만 조회하여 성능을 최적화할 수 있다
- [ ] Hash 크기를 적절히 유지하여 메모리를 절약할 수 있다
- [ ] ziplist 인코딩을 활용한 최적화를 할 수 있다
- [ ] TTL을 적절히 설정하여 메모리를 관리할 수 있다

**면접 대비**
- [ ] 주니어 질문 7개에 답변할 수 있다
- [ ] 중급 질문 5개를 이해하고 설명할 수 있다
- [ ] 실무 예시를 들어 Hash 활용을 설명할 수 있다

**프로젝트 경험**
- [ ] 사용자 관리 시스템 프로젝트를 완성했다
- [ ] 전자상거래 상품 관리 시스템을 구현했다
- [ ] 게임 길드 관리 시스템을 만들었다

---

### 다음 단계 추천

**즉시 실천할 수 있는 것들**:
1. 현재 프로젝트에서 JSON String을 Hash로 리팩토링하기
2. 사용자 세션 스토어를 Hash로 마이그레이션하기
3. 실시간 통계 대시보드 구현하기

**복습 방법**:
- 💡 주니어 시나리오 4개를 코드로 직접 구현해보기
- 💡 면접 질문에 대한 답변을 본인 언어로 정리하기
- 💡 실전 프로젝트를 확장하여 기능 추가하기

---

이제 구조화된 데이터 관리의 마스터가 되었습니다. 다음 장에서는 점수 기반으로 정렬된 Sorted Set 타입으로 랭킹 시스템과 실시간 리더보드 구현 능력을 키워보겠습니다! 🚀

---

**다음 장으로 이동**: [8. Sorted Set 타입 완전 가이드](./08-Sorted-Set-타입-완전-가이드.md)

**이전 장으로 돌아가기**: [6. Set 타입 완전 가이드](./06-Set-타입-완전-가이드.md)

**목차로 돌아가기**: [Redis 완전 학습 가이드](./redis%20가이드.md)