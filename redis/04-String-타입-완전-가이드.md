# 📝 4. String 타입 완전 가이드

> **학습 목표**: Redis의 가장 기본이면서도 강력한 String 타입의 모든 기능을 완벽하게 마스터하고, 실무에서 바로 활용할 수 있는 능력을 갖춥니다.

**⏱️ 예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐☆☆☆ (2개/5개)

---

## 📚 목차
- [왜 String 타입이 필요한가](#왜-string-타입이-필요한가)
- [실무 활용 사례](#실무-활용-사례)
- [실생활 비유로 이해하기](#실생활-비유로-이해하기)
- [String 타입 완전 이해](#string-타입-완전-이해)
- [기본 문자열 조작 마스터](#기본-문자열-조작-마스터)
- [숫자 연산 완전 정복](#숫자-연산-완전-정복)
- [부분 문자열 조작](#부분-문자열-조작)
- [멀티 키 조작](#멀티-키-조작)
- [실전 종합 프로젝트](#실전-종합-프로젝트)
- [주니어 시나리오](#주니어-시나리오)
- [FAQ](#faq)
- [면접 질문 리스트](#면접-질문-리스트)
- [핵심 정리](#핵심-정리)
- [관련 기술](#관련-기술)
- [추가 학습 자료](#추가-학습-자료)
- [다음 단계](#다음-단계)
- [축하합니다](#축하합니다)

---

## 🤔 왜 String 타입이 필요한가?

### 실무 배경

**실제 서비스에서 겪는 문제들**

#### ❌ Redis String 타입을 모르면 발생하는 문제

```
문제 1: 동시성 이슈로 인한 데이터 불일치
- 증상: 여러 사용자가 동시에 좋아요를 누르면 카운트가 정확하지 않음
- 영향: 실제 좋아요 100개인데 95개로 표시되는 등 데이터 신뢰성 하락
- 비용: 데이터 정합성 문제로 인한 사용자 불만 증가

문제 2: 데이터베이스 부하로 인한 응답 지연
- 증상: 자주 조회되는 사용자 프로필 조회 시마다 DB 쿼리 발생
- 영향: 응답 시간 100ms → 사용자 경험 저하
- 비용: DB 서버 비용 증가 (월 $1,000 → $2,000)

문제 3: 세션 관리의 복잡성
- 증상: 세션 데이터를 파일이나 DB에 저장하여 관리가 복잡
- 영향: 서버 확장 시 세션 동기화 문제 발생
- 비용: 개발/운영 시간 증가 (주 20시간 → 40시간)
```

#### ✅ Redis String 타입을 사용하면

```
해결책 1: 원자적 연산으로 동시성 문제 해결
- 방법: INCR 명령어로 원자적 증감 보장
- 효과: 100% 정확한 카운팅, 동시 접속 1만 명도 안전
- 절감: 데이터 불일치 문제 0건

해결책 2: 캐싱으로 DB 부하 99% 감소
- 방법: 자주 조회되는 데이터를 Redis String에 캐싱
- 효과: 응답 시간 100ms → 1ms (99% 개선)
- 절감: DB 서버 비용 $2,000 → $500 (75% 절감)

해결책 3: 간편한 세션 관리
- 방법: SETEX로 만료시간 포함 세션 저장
- 효과: 자동 만료, 빠른 조회, 서버 확장 용이
- 절감: 개발/운영 시간 주 40시간 → 10시간 (75% 절감)
```

### 📊 수치로 보는 효과

| 지표 | Before (DB 직접 사용) | After (Redis String) | 개선율 |
|------|---------------------|---------------------|--------|
| 응답 시간 | 100ms | 1ms | **99%↓** |
| 처리량 (TPS) | 1,000 | 100,000 | **100배↑** |
| DB 부하 | 100% | 1% | **99%↓** |
| 서버 비용 | $2,000/월 | $500/월 | **75%↓** |
| 개발 시간 | 40시간/주 | 10시간/주 | **75%↓** |
| 동시성 이슈 | 10건/일 | 0건/일 | **100%↓** |

---

---

## 🏢 실무 활용 사례

### 실제 기업 활용 사례

#### 사례 1: 네이버 - 실시간 검색어 순위 시스템
```bash
# 사용 목적: 실시간 검색어 클릭 수 집계
# 규모: 초당 10만 건 이상의 검색어 클릭 처리
# 효과: 정확한 실시간 순위 제공, 동시성 문제 0건

# 구현 예시
# 검색어 클릭 시마다 카운트 증가
INCR search:keyword:redis:2024-01-01:10
(integer) 15234

# 검색어 순위 조회 (상위 10개)
# 실제로는 Sorted Set과 조합하여 사용
MGET search:keyword:redis:2024-01-01:10 \
     search:keyword:docker:2024-01-01:10 \
     search:keyword:kubernetes:2024-01-01:10

# 성과
# - 성능 향상: 응답시간 100ms → 1ms (99% 개선)
# - 비용 절감: DB 서버 비용 월 $5,000 → $1,000 (80% 절감)
# - 정확도: 동시성 이슈로 인한 오차 10% → 0% (100% 정확)
```

#### 사례 2: 카카오 - 사용자 세션 관리
```bash
# 사용 목적: 2천만 사용자 세션 관리
# 규모: 동시 접속자 300만 명
# 효과: 자동 만료로 운영 부담 감소, 빠른 세션 조회

# 구현 예시
# 로그인 시 세션 생성 (30분 TTL)
SETEX session:user:abc123def456 1800 '{"user_id":12345678,"login_at":"2024-01-01T10:00:00Z","device":"mobile"}'
OK

# 세션 조회 (매 요청마다)
GET session:user:abc123def456
'{"user_id":12345678,"login_at":"2024-01-01T10:00:00Z","device":"mobile"}'

# 세션 연장
EXPIRE session:user:abc123def456 1800
(integer) 1

# 성과
# - 성능 향상: 세션 조회 50ms → 1ms (98% 개선)
# - 비용 절감: 세션 DB 비용 월 $3,000 → $500 (83% 절감)
# - 운영 효율: 만료된 세션 수동 삭제 불필요 (주 40시간 절감)
```

#### 사례 3: 쿠팡 - 실시간 재고 관리
```bash
# 사용 목적: 초특가 상품 재고 실시간 차감
# 규모: 초당 5만 건의 주문 처리
# 효과: 재고 부족 방지, 과다 판매 0건

# 구현 예시
# 재고 초기화 (한정 수량 1000개)
SET stock:product:12345 1000
OK

# 주문 시마다 재고 차감 (원자적 연산)
DECR stock:product:12345
(integer) 999

# 재고 확인 후 주문 처리
GET stock:product:12345
"999"

# 재고 부족 시 주문 차단
if stock <= 0:
    return "품절"

# Lua 스크립트로 재고 확인 + 차감 원자적 처리
EVAL "local stock = redis.call('GET', KEYS[1]) \
      if tonumber(stock) > 0 then \
          return redis.call('DECR', KEYS[1]) \
      else \
          return -1 \
      end" 1 stock:product:12345

# 성과
# - 정확도: 재고 오차 5% → 0% (과다 판매 0건)
# - 성능 향상: 재고 확인 20ms → 1ms (95% 개선)
# - 고객 만족도: 품절 클레임 95% 감소
```

#### 사례 4: 토스 - API Rate Limiting
```bash
# 사용 목적: 금융 API 호출 횟수 제한
# 규모: 일일 1억 건의 API 요청
# 효과: DDoS 방어, 시스템 안정성 확보

# 구현 예시
# IP별 분당 API 호출 횟수 제한 (100회)
SET ratelimit:192.168.1.100:2024-01-01:10:30 0 EX 60
OK

# API 호출 시마다 카운트 증가
INCR ratelimit:192.168.1.100:2024-01-01:10:30
(integer) 1

# 제한 확인
GET ratelimit:192.168.1.100:2024-01-01:10:30
"95"

if count > 100:
    return "Rate limit exceeded"

# 성과
# - 보안 강화: DDoS 공격 자동 차단
# - 안정성: 과부하로 인한 장애 0건
# - 비용 절감: 불필요한 트래픽 99% 차단
```

#### 사례 5: 배달의민족 - 실시간 주문 통계
```bash
# 사용 목적: 실시간 주문 건수 및 매출 집계
# 규모: 하루 300만 건의 주문
# 효과: 실시간 대시보드 제공, 의사결정 지원

# 구현 예시
# 주문 발생 시 카운터 증가
INCR stats:orders:daily:2024-01-01
(integer) 2500000

# 매출 누적 (실수 연산)
INCRBYFLOAT stats:revenue:daily:2024-01-01 35500.00
"8750000000.00"

# 시간대별 통계
INCR stats:orders:hourly:2024-01-01:19
(integer) 150000

# 실시간 대시보드 조회
MGET stats:orders:daily:2024-01-01 \
     stats:revenue:daily:2024-01-01 \
     stats:orders:hourly:2024-01-01:19
1) "2500000"
2) "8750000000.00"
3) "150000"

# 성과
# - 실시간성: 통계 업데이트 지연 5분 → 실시간 (100% 개선)
# - 의사결정: 프로모션 효과 즉시 파악 가능
# - 비용 절감: 별도 통계 시스템 불필요
```

### 성능 비교

| 방법 | 응답시간 | 처리량 (TPS) | 메모리 | 동시성 안전 | 비용/월 |
|------|----------|--------------|--------|------------|---------|
| DB 직접 사용 | 100ms | 1,000 | 10GB | ❌ 위험 | $2,000 |
| Redis String | 1ms | 100,000 | 1GB | ✅ 안전 | $200 |
| **개선** | **99%↓** | **100배↑** | **90%↓** | **100%** | **90%↓** |

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 포스트잇 (가장 기본적인 메모)

```
Redis String = 포스트잇

- 간단하고 빠르게 메모 가능 (SET)
- 언제든 읽을 수 있음 (GET)
- 필요 없으면 떼어냄 (DEL)
- 시간 지나면 자동으로 떨어짐 (EXPIRE)
- 내용 추가 가능 (APPEND)

포스트잇:
┌─────────────────┐
│  "우유 사기"     │ ← 간단한 메모
│  마감: 오늘 6시  │ ← 만료시간
└─────────────────┘
```

**실제 활용**:
- 포스트잇처럼 임시 데이터를 빠르게 저장
- 세션, 캐시, 임시 토큰 등

### 비유 2: 주차장 번호판 (카운팅)

```
Redis INCR/DECR = 주차장 전광판 숫자

- 차가 들어올 때마다 +1 (INCR)
- 차가 나갈 때마다 -1 (DECR)
- 여러 차가 동시에 들어와도 정확히 카운팅
- 원자적 연산으로 오류 없음

주차장 전광판:
┌──────────────────────┐
│  현재 주차 대수: 157  │ ← INCR로 관리
│  남은 자리:     43    │ ← DECR로 관리
└──────────────────────┘
```

**실제 활용**:
- 좋아요 수, 조회수, 재고 관리
- 동시 접속자 수, API 호출 횟수

### 비유 3: 배달 앱의 주문 상태 (문자열 저장)

```
Redis String = 배달 앱의 주문 정보

- 주문 상태: "접수중" → "조리중" → "배달중"
- 주문 정보 JSON으로 저장
- 30분 후 자동 삭제 (SETEX)
- 빠르게 조회하여 실시간 업데이트

배달 앱 화면:
┌────────────────────────┐
│ 주문번호: #12345        │
│ 상태: "배달중" 🚚       │ ← Redis String
│ 예상시간: 15분          │
│ 위치: "강남역 3번출구"  │
└────────────────────────┘
```

**실제 활용**:
- 주문 상태, 배송 정보
- 실시간 알림 데이터

### 비유 4: 지하철 노선도 정보판 (부분 문자열)

```
Redis GETRANGE = 지하철 노선도에서 특정 구간만 보기

전체 노선: "수서-복정-가락시장-문정-장지"

- 앞부분만 (GETRANGE 0 5): "수서-복정"
- 중간 부분 (GETRANGE 7 15): "가락시장-문정"
- 뒷부분만 (GETRANGE -4 -1): "장지"

지하철 정보판:
┌──────────────────────────────┐
│ [수서] → [복정] → [가락시장]  │ ← 일부만 표시
│      5분      7분             │
└──────────────────────────────┘
```

**실제 활용**:
- 로그 파일에서 날짜/시간만 추출
- 사용자 ID에서 특정 정보 파싱

### 비유 5: 편의점 재고 관리 (멀티 키 조작)

```
Redis MSET/MGET = 편의점 재고를 한 번에 확인/업데이트

한 번의 조작으로 여러 상품 처리:
- 라면, 음료, 과자 재고를 동시에 설정 (MSET)
- 라면, 음료, 과자 재고를 동시에 조회 (MGET)
- 네트워크 왕복 3번 → 1번 (효율 3배)

재고 관리 시스템:
┌─────────────────────────┐
│ 상품      재고   가격    │
│ 라면      50개   1,500원 │ ← MSET으로
│ 음료      30개   1,000원 │   한 번에
│ 과자      25개   2,000원 │   업데이트
└─────────────────────────┘
```

**실제 활용**:
- 사용자 프로필 여러 필드 동시 설정/조회
- 설정값 일괄 업데이트

### 🎯 종합 비교표

```
┌─────────────┬──────────────┬──────────────┬──────────────┐
│ String 기능  │ 포스트잇     │ 주차장 전광판 │ 배달 앱      │
├─────────────┼──────────────┼──────────────┼──────────────┤
│ SET/GET     │ 메모 쓰기/읽기│ 초기값 설정  │ 주문 접수    │
│ INCR/DECR   │ -            │ 숫자 증감    │ 진행상태 +1  │
│ EXPIRE      │ 자동 제거    │ 일일 초기화  │ 30분 후 삭제 │
│ APPEND      │ 메모 추가    │ -            │ 로그 추가    │
│ MSET/MGET   │ 여러 메모 처리│ 복수 차량 처리│ 다중 주문    │
└─────────────┴──────────────┴──────────────┴──────────────┘
```

---

## 🧬 String 타입 완전 이해

### 1.1 Redis String이란?

**Redis String은 단순한 문자열이 아닙니다!**

```
📚 도서관 비유:
- Redis String = 만능 보관함
- 문자열 = 책
- 숫자 = 계산기
- 바이너리 데이터 = 사진, 동영상
- JSON = 카탈로그

하나의 보관함에 다양한 형태의 자료를 저장할 수 있습니다.
```

#### 1️⃣ 초보자 수준 설명
Redis String은 "값을 저장하는 상자"입니다. 이 상자에는 글자, 숫자, JSON 데이터 등 무엇이든 넣을 수 있습니다.

#### 2️⃣ 중급자 수준 설명
Redis String은 바이너리 안전(binary-safe)한 문자열 타입으로, 최대 512MB까지 저장 가능합니다. 내부적으로 3가지 인코딩(int, embstr, raw)을 사용하여 메모리를 최적화합니다.

#### 3️⃣ 고급자 수준 설명
Redis String은 SDS(Simple Dynamic String) 구조를 사용하여 O(1) 시간 복잡도로 문자열 길이를 조회하고, 버퍼 오버플로우를 방지합니다. 44바이트 이하는 embstr로 단일 메모리 할당하여 성능을 최적화합니다.

### 1.2 String이 저장할 수 있는 데이터 타입

#### 1) 순수 문자열
```bash
127.0.0.1:6379> SET greeting "안녕하세요, Redis 세계에 오신 것을 환영합니다!"
OK

127.0.0.1:6379> SET english_text "Hello, Welcome to Redis World!"
OK

127.0.0.1:6379> SET multiline_text "첫 번째 줄\n두 번째 줄\n세 번째 줄"
OK
```

#### 2) 숫자 (정수와 실수)
```bash
127.0.0.1:6379> SET counter 100
OK

127.0.0.1:6379> SET price 1299.99
OK

127.0.0.1:6379> SET negative_number -500
OK

127.0.0.1:6379> SET scientific_notation 1.23e10
OK
```

#### 3) JSON 데이터
```bash
127.0.0.1:6379> SET user_profile '{"id":1001,"name":"김철수","email":"kim@example.com","age":30}'
OK

127.0.0.1:6379> SET product_info '{"id":"LAPTOP001","name":"고성능 노트북","price":1299000,"stock":15,"category":"electronics"}'
OK
```

#### 4) 바이너리 데이터
```bash
# 이미지나 파일의 Base64 인코딩된 데이터
127.0.0.1:6379> SET profile_image "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
OK
```

### 1.3 String의 내부 특성

#### 크기 제한
```bash
# 최대 크기: 512MB
# 실제 확인해보기
127.0.0.1:6379> SET large_string "$(printf 'A%.0s' {1..1000000})"
OK

127.0.0.1:6379> STRLEN large_string
(integer) 1000000
```

#### 인코딩 방식
```bash
# Redis는 내부적으로 3가지 인코딩 방식 사용:
# 1. int: 정수형 데이터
# 2. embstr: 짧은 문자열 (44바이트 이하)
# 3. raw: 긴 문자열 (44바이트 초과)

# 내부 인코딩 확인 (DEBUG 명령어 - 개발환경에서만)
127.0.0.1:6379> SET small_text "작은 텍스트"
OK

127.0.0.1:6379> OBJECT ENCODING small_text
"embstr"

127.0.0.1:6379> SET large_text "$(printf 'A%.0s' {1..100})"
OK

127.0.0.1:6379> OBJECT ENCODING large_text
"raw"

127.0.0.1:6379> SET number_value 12345
OK

127.0.0.1:6379> OBJECT ENCODING number_value
"int"
```

---

## 🔤 기본 문자열 조작 마스터

### 2.1 SET의 모든 변형과 옵션

#### 기본 SET 명령어 복습
```bash
# 기본 설정
127.0.0.1:6379> SET username "kim_chul_soo"
OK

# 만료시간과 함께 설정
127.0.0.1:6379> SET session_token "abc123def456" EX 3600
OK

# 조건부 설정
127.0.0.1:6379> SET config_value "production" NX
OK
```

#### SETNX - 키가 없을 때만 설정
```bash
# 분산 락 구현에 주로 사용
127.0.0.1:6379> SETNX lock:user:1001 "locked"
(integer) 1  # 성공

127.0.0.1:6379> SETNX lock:user:1001 "locked_again"
(integer) 0  # 실패 (이미 존재)

# 활용 예시: 중복 처리 방지
127.0.0.1:6379> SETNX processing:order:12345 "in_progress"
(integer) 1  # 처리 시작

# 다른 프로세스에서 같은 주문 처리 시도
127.0.0.1:6379> SETNX processing:order:12345 "in_progress"
(integer) 0  # 이미 처리 중이므로 거부
```

#### SETEX - 설정과 동시에 만료시간 지정
```bash
# 세션 관리
127.0.0.1:6379> SETEX user_session:abc123 1800 '{"user_id":1001,"role":"user","login_time":"2024-01-01T10:00:00Z"}'
OK

# OTP(일회용 패스워드) 관리
127.0.0.1:6379> SETEX otp:mobile:01012345678 300 "123456"
OK  # 5분 후 자동 만료

# 캐시 데이터
127.0.0.1:6379> SETEX cache:weather:seoul 600 '{"temperature":15,"humidity":65,"weather":"sunny"}'
OK  # 10분 후 만료
```

#### PSETEX - 밀리초 단위 만료시간
```bash
# 매우 짧은 시간의 임시 데이터
127.0.0.1:6379> PSETEX quick_token "temp123" 5000
OK  # 5초 후 만료

# 실시간 게임 데이터
127.0.0.1:6379> PSETEX game:player:1001:boost "speed_boost" 15000
OK  # 15초 부스터 효과
```

### 2.2 GET의 다양한 활용

#### 기본 GET과 존재하지 않는 키 처리
```bash
127.0.0.1:6379> GET username
"kim_chul_soo"

127.0.0.1:6379> GET nonexistent_key
(nil)

# 실무에서의 nil 처리 패턴
# 1. 기본값 사용
127.0.0.1:6379> GET user:1001:theme
(nil)
# 애플리케이션에서 "light" 테마를 기본값으로 사용

# 2. 캐시 미스 처리
127.0.0.1:6379> GET cache:product:5678
(nil)
# 데이터베이스에서 조회 후 캐시에 저장
```

#### GETSET - 설정하면서 이전 값 반환
```bash
# 카운터 교체
127.0.0.1:6379> SET counter 100
OK

127.0.0.1:6379> GETSET counter 200
"100"  # 이전 값 반환

127.0.0.1:6379> GET counter
"200"  # 새로운 값

# 실무 활용: 원자적 값 교체
127.0.0.1:6379> GETSET status:server "maintenance"
"running"  # 이전 상태 반환하면서 유지보수 모드로 전환
```

### 2.3 APPEND - 문자열 끝에 추가

```bash
# 기본 사용법
127.0.0.1:6379> SET message "Hello"
OK

127.0.0.1:6379> APPEND message " World"
(integer) 11  # 전체 길이 반환

127.0.0.1:6379> GET message
"Hello World"

# 키가 없는 경우 새로 생성
127.0.0.1:6379> APPEND new_log "첫 번째 로그 항목"
(integer) 24

127.0.0.1:6379> APPEND new_log "\n두 번째 로그 항목"
(integer) 37

127.0.0.1:6379> GET new_log
"첫 번째 로그 항목\n두 번째 로그 항목"
```

#### APPEND 실무 활용 패턴

##### 1) 로그 수집
```bash
# 사용자 활동 로그
127.0.0.1:6379> SET user:1001:activity_log "2024-01-01 10:00:00 - 로그인"
OK

127.0.0.1:6379> APPEND user:1001:activity_log "\n2024-01-01 10:05:00 - 상품 조회"
(integer) 65

127.0.0.1:6379> APPEND user:1001:activity_log "\n2024-01-01 10:10:00 - 장바구니 추가"
(integer) 95

127.0.0.1:6379> GET user:1001:activity_log
"2024-01-01 10:00:00 - 로그인\n2024-01-01 10:05:00 - 상품 조회\n2024-01-01 10:10:00 - 장바구니 추가"
```

##### 2) 채팅 메시지 누적
```bash
# 채팅방 메시지 히스토리
127.0.0.1:6379> SET chat:room:1001 "김철수: 안녕하세요!"
OK

127.0.0.1:6379> APPEND chat:room:1001 "\n이영희: 반갑습니다!"
(integer) 38

127.0.0.1:6379> APPEND chat:room:1001 "\n박민수: 좋은 하루 되세요!"
(integer) 63
```

##### 3) 데이터 스트리밍
```bash
# 센서 데이터 수집
127.0.0.1:6379> SET sensor:temperature "25.5"
OK

127.0.0.1:6379> APPEND sensor:temperature ",26.1"
(integer) 10

127.0.0.1:6379> APPEND sensor:temperature ",25.8"
(integer) 15

127.0.0.1:6379> GET sensor:temperature
"25.5,26.1,25.8"
```

---

## 🔢 숫자 연산 완전 정복

### 3.1 INCR/DECR - 원자적 증감 연산

#### 기본 증감 연산
```bash
# 카운터 초기화
127.0.0.1:6379> SET visitors 0
OK

# 1씩 증가
127.0.0.1:6379> INCR visitors
(integer) 1

127.0.0.1:6379> INCR visitors
(integer) 2

127.0.0.1:6379> INCR visitors
(integer) 3

# 1씩 감소
127.0.0.1:6379> DECR visitors
(integer) 2

127.0.0.1:6379> GET visitors
"2"
```

#### 키가 없는 경우의 동작
```bash
# 키가 없으면 0으로 초기화 후 연산
127.0.0.1:6379> INCR new_counter
(integer) 1

127.0.0.1:6379> DECR another_counter
(integer) -1
```

#### 문자열에 숫자 연산 시도 시 에러
```bash
127.0.0.1:6379> SET name "김철수"
OK

127.0.0.1:6379> INCR name
(error) ERR value is not an integer or out of range
```

### 3.2 INCRBY/DECRBY - 지정한 값만큼 증감

```bash
# 초기값 설정
127.0.0.1:6379> SET score 100
OK

# 50점 증가
127.0.0.1:6379> INCRBY score 50
(integer) 150

# 25점 감소
127.0.0.1:6379> DECRBY score 25
(integer) 125

# 음수로 증감 (방향 바뀜)
127.0.0.1:6379> INCRBY score -30
(integer) 95  # 실제로는 감소

127.0.0.1:6379> DECRBY score -20
(integer) 115  # 실제로는 증가
```

### 3.3 INCRBYFLOAT - 실수 연산

```bash
# 실수 초기화
127.0.0.1:6379> SET temperature 23.5
OK

# 실수 증가
127.0.0.1:6379> INCRBYFLOAT temperature 1.5
"25"

127.0.0.1:6379> INCRBYFLOAT temperature 0.25
"25.25"

# 실수 감소 (음수 사용)
127.0.0.1:6379> INCRBYFLOAT temperature -2.75
"22.5"

# 과학적 표기법도 지원
127.0.0.1:6379> INCRBYFLOAT temperature 1.5e-1
"22.65"
```

### 3.4 숫자 연산 실무 활용 패턴

#### 1) 방문자 카운터
```bash
# 일일 방문자 수 (자정에 만료)
127.0.0.1:6379> SET visitors:daily:2024-01-01 0 EX 86400
OK

# 방문자가 올 때마다
127.0.0.1:6379> INCR visitors:daily:2024-01-01
(integer) 1

127.0.0.1:6379> INCR visitors:daily:2024-01-01
(integer) 2

# 페이지별 방문자 수
127.0.0.1:6379> INCR page:home:views
(integer) 1

127.0.0.1:6379> INCR page:products:views
(integer) 1
```

#### 2) 게임 점수 시스템
```bash
# 플레이어 점수 초기화
127.0.0.1:6379> SET player:1001:score 0
OK

# 아이템 획득 시 점수 증가
127.0.0.1:6379> INCRBY player:1001:score 100
(integer) 100

# 보너스 점수 (실수)
127.0.0.1:6379> INCRBYFLOAT player:1001:score 50.5
"150.5"

# 벌점 (점수 감소)
127.0.0.1:6379> DECRBY player:1001:score 25
(integer) 125
```

#### 3) 재고 관리
```bash
# 상품 재고 초기화
127.0.0.1:6379> SET stock:product:1001 100
OK

# 구매 시 재고 감소
127.0.0.1:6379> DECRBY stock:product:1001 3
(integer) 97

# 입고 시 재고 증가
127.0.0.1:6379> INCRBY stock:product:1001 50
(integer) 147

# 재고 확인
127.0.0.1:6379> GET stock:product:1001
"147"
```

#### 4) API 호출 횟수 제한 (Rate Limiting)
```bash
# IP별 API 호출 횟수 (1시간 제한)
127.0.0.1:6379> SET api:calls:192.168.1.100 0 EX 3600
OK

# API 호출 시마다 증가
127.0.0.1:6379> INCR api:calls:192.168.1.100
(integer) 1

127.0.0.1:6379> INCR api:calls:192.168.1.100
(integer) 2

# 현재 호출 횟수 확인
127.0.0.1:6379> GET api:calls:192.168.1.100
"2"

# 제한 초과 체크 로직 (애플리케이션에서 구현)
# if (current_calls >= 1000) { return "Rate limit exceeded"; }
```

#### 5) 실시간 통계
```bash
# 실시간 주문 건수
127.0.0.1:6379> INCR stats:orders:realtime
(integer) 1

# 시간대별 주문 건수
127.0.0.1:6379> INCR stats:orders:hour:2024-01-01:10
(integer) 1

127.0.0.1:6379> INCR stats:orders:hour:2024-01-01:10
(integer) 2

# 매출 통계 (실수)
127.0.0.1:6379> INCRBYFLOAT stats:revenue:daily:2024-01-01 1299.99
"1299.99"

127.0.0.1:6379> INCRBYFLOAT stats:revenue:daily:2024-01-01 599.00
"1898.99"
```

---

## ✂️ 부분 문자열 조작

### 4.1 STRLEN - 문자열 길이 확인

```bash
# 한글 문자열 길이
127.0.0.1:6379> SET korean_text "안녕하세요 Redis 세계"
OK

127.0.0.1:6379> STRLEN korean_text
(integer) 28  # 바이트 단위 (UTF-8 인코딩)

# 영문 문자열 길이
127.0.0.1:6379> SET english_text "Hello Redis World"
OK

127.0.0.1:6379> STRLEN english_text
(integer) 17  # 문자 수와 바이트 수 동일

# 빈 문자열
127.0.0.1:6379> SET empty_string ""
OK

127.0.0.1:6379> STRLEN empty_string
(integer) 0

# 존재하지 않는 키
127.0.0.1:6379> STRLEN nonexistent
(integer) 0
```

### 4.2 GETRANGE - 부분 문자열 추출

#### 기본 사용법
```bash
# 테스트 문자열 준비
127.0.0.1:6379> SET sample_text "Hello Redis World Programming"
OK

# 인덱스는 0부터 시작
# 0번째부터 4번째까지
127.0.0.1:6379> GETRANGE sample_text 0 4
"Hello"

# 6번째부터 10번째까지
127.0.0.1:6379> GETRANGE sample_text 6 10
"Redis"

# 12번째부터 16번째까지
127.0.0.1:6379> GETRANGE sample_text 12 16
"World"
```

#### 음수 인덱스 활용
```bash
# 음수는 뒤에서부터 계산 (-1이 마지막 문자)
127.0.0.1:6379> GETRANGE sample_text -11 -1
"Programming"

# 뒤에서 5글자
127.0.0.1:6379> GETRANGE sample_text -5 -1
"mming"

# 처음부터 뒤에서 12번째까지
127.0.0.1:6379> GETRANGE sample_text 0 -12
"Hello Redis World "
```

#### 전체 문자열 조회
```bash
# 처음부터 끝까지
127.0.0.1:6379> GETRANGE sample_text 0 -1
"Hello Redis World Programming"

# GET 명령어와 동일한 결과
127.0.0.1:6379> GET sample_text
"Hello Redis World Programming"
```

#### 실무 활용 예시

##### 1) 로그 파일에서 특정 부분 추출
```bash
# 로그 데이터 저장
127.0.0.1:6379> SET access_log "2024-01-01 10:30:15 192.168.1.100 GET /api/users 200 1.23ms"
OK

# 날짜 부분만 추출
127.0.0.1:6379> GETRANGE access_log 0 9
"2024-01-01"

# 시간 부분만 추출
127.0.0.1:6379> GETRANGE access_log 11 18
"10:30:15"

# IP 주소 부분 추출
127.0.0.1:6379> GETRANGE access_log 20 32
"192.168.1.100"

# HTTP 상태 코드 추출
127.0.0.1:6379> GETRANGE access_log 50 52
"200"
```

##### 2) 파일 헤더 정보 확인
```bash
# 파일 데이터 저장 (첫 부분은 헤더 정보)
127.0.0.1:6379> SET file_data "HEADER:VERSION=1.0;TYPE=JSON;SIZE=1024;DATA:실제데이터내용..."
OK

# 헤더 부분만 추출
127.0.0.1:6379> GETRANGE file_data 0 38
"HEADER:VERSION=1.0;TYPE=JSON;SIZE=1024;"
```

##### 3) 사용자 ID에서 정보 추출
```bash
# 구조화된 사용자 ID
127.0.0.1:6379> SET user_id "USER20240101KIM001ADMIN"
OK

# 사용자 타입 (앞 4글자)
127.0.0.1:6379> GETRANGE user_id 0 3
"USER"

# 가입 날짜 (5~12번째)
127.0.0.1:6379> GETRANGE user_id 4 11
"20240101"

# 사용자명 (13~15번째)
127.0.0.1:6379> GETRANGE user_id 12 14
"KIM"

# 일련번호 (16~18번째)
127.0.0.1:6379> GETRANGE user_id 15 17
"001"

# 권한 (19번째부터 끝까지)
127.0.0.1:6379> GETRANGE user_id 18 -1
"ADMIN"
```

### 4.3 SETRANGE - 부분 문자열 수정

#### 기본 사용법
```bash
# 원본 문자열 준비
127.0.0.1:6379> SET message "Hello World Programming"
OK

# 6번째 위치부터 "Redis"로 교체
127.0.0.1:6379> SETRANGE message 6 "Redis"
(integer) 23  # 수정 후 전체 길이

127.0.0.1:6379> GET message
"Hello Redis Programming"

# 다시 일부 수정
127.0.0.1:6379> SETRANGE message 12 "Tutorial"
(integer) 20

127.0.0.1:6379> GET message
"Hello Redis Tutorial"
```

#### 문자열 끝을 넘어서 수정
```bash
# 원본보다 뒤쪽에 데이터 삽입
127.0.0.1:6379> SET short_text "Hi"
OK

127.0.0.1:6379> SETRANGE short_text 10 "Redis"
(integer) 15

127.0.0.1:6379> GET short_text
"Hi\x00\x00\x00\x00\x00\x00\x00\x00Redis"
# 중간에 NULL 바이트(\x00)로 채워짐
```

#### 빈 키에 SETRANGE 사용
```bash
# 존재하지 않는 키에 SETRANGE
127.0.0.1:6379> SETRANGE new_string 5 "Redis"
(integer) 10

127.0.0.1:6379> GET new_string
"\x00\x00\x00\x00\x00Redis"
# 앞부분이 NULL 바이트로 채워짐
```

#### 실무 활용 예시

##### 1) 상태 플래그 업데이트
```bash
# 사용자 권한 문자열 (각 자리는 다른 권한을 의미)
# 위치: 0=읽기, 1=쓰기, 2=삭제, 3=관리자
127.0.0.1:6379> SET user:1001:permissions "1100"
OK  # 읽기(1), 쓰기(1), 삭제(0), 관리자(0)

# 삭제 권한 부여 (2번째 위치를 1로 변경)
127.0.0.1:6379> SETRANGE user:1001:permissions 2 "1"
(integer) 4

127.0.0.1:6379> GET user:1001:permissions
"1110"  # 읽기(1), 쓰기(1), 삭제(1), 관리자(0)

# 관리자 권한 부여
127.0.0.1:6379> SETRANGE user:1001:permissions 3 "1"
(integer) 4

127.0.0.1:6379> GET user:1001:permissions
"1111"  # 모든 권한 보유
```

##### 2) 로그 레벨 변경
```bash
# 로그 설정 문자열
127.0.0.1:6379> SET log_config "LEVEL=INFO;FILE=/var/log/app.log;SIZE=10MB"
OK

# 로그 레벨을 DEBUG로 변경
127.0.0.1:6379> SETRANGE log_config 6 "DEBUG"
(integer) 42

127.0.0.1:6379> GET log_config
"LEVEL=DEBUG;FILE=/var/log/app.log;SIZE=10MB"
```

##### 3) 버전 정보 업데이트
```bash
# 소프트웨어 버전 정보
127.0.0.1:6379> SET version_info "MyApp v1.0.0 Build 2024.01.01"
OK

# 마이너 버전 업데이트 (1.0.0 → 1.1.0)
127.0.0.1:6379> SETRANGE version_info 9 "1"
(integer) 29

127.0.0.1:6379> GET version_info
"MyApp v1.1.0 Build 2024.01.01"

# 빌드 날짜 업데이트
127.0.0.1:6379> SETRANGE version_info 21 "2024.01.15"
(integer) 31

127.0.0.1:6379> GET version_info
"MyApp v1.1.0 Build 2024.01.15"
```

---

## 🔄 멀티 키 조작

### 5.1 MSET - 여러 키 동시 설정

#### 기본 사용법
```bash
# 여러 키-값 쌍을 한 번에 설정
127.0.0.1:6379> MSET name "김철수" age 30 city "서울" job "개발자"
OK

# 설정 확인
127.0.0.1:6379> GET name
"김철수"

127.0.0.1:6379> GET age
"30"

127.0.0.1:6379> GET city
"서울"

127.0.0.1:6379> GET job
"개발자"
```

#### 기존 키 덮어쓰기
```bash
# 기존 값이 있어도 덮어씀
127.0.0.1:6379> MSET name "이영희" age 25 department "마케팅"
OK

127.0.0.1:6379> GET name
"이영희"  # 덮어써짐

127.0.0.1:6379> GET department
"마케팅"  # 새로 추가됨
```

### 5.2 MGET - 여러 키 동시 조회

```bash
# 여러 키의 값을 한 번에 조회
127.0.0.1:6379> MGET name age city job department
1) "이영희"
2) "25"
3) "서울"
4) "개발자"
5) "마케팅"

# 존재하지 않는 키 포함
127.0.0.1:6379> MGET name nonexistent age unknown
1) "이영희"
2) (nil)
3) "25"
4) (nil)
```

### 5.3 MSETNX - 모든 키가 없을 때만 설정

```bash
# 새로운 Redis 세션에서 테스트
127.0.0.1:6379> FLUSHALL
OK

# 모든 키가 없으므로 성공
127.0.0.1:6379> MSETNX user:1001:name "김철수" user:1001:age 30 user:1001:city "서울"
(integer) 1  # 성공

# 일부 키가 이미 존재하므로 실패
127.0.0.1:6379> MSETNX user:1001:name "이영희" user:1001:email "lee@example.com"
(integer) 0  # 실패 (user:1001:name이 이미 존재)

# 모든 키가 기존과 동일하게 유지됨
127.0.0.1:6379> MGET user:1001:name user:1001:email
1) "김철수"  # 변경되지 않음
2) (nil)     # 설정되지 않음
```

### 5.4 멀티 키 조작의 성능 장점

#### 네트워크 라운드트립 최소화
```bash
# 비효율적인 방법 (4번의 네트워크 호출)
SET config:db_host "localhost"
SET config:db_port "5432"
SET config:db_name "myapp"
SET config:db_user "admin"

# 효율적인 방법 (1번의 네트워크 호출)
MSET config:db_host "localhost" config:db_port "5432" config:db_name "myapp" config:db_user "admin"
```

```bash
# 비효율적인 조회 (4번의 네트워크 호출)
GET config:db_host
GET config:db_port
GET config:db_name
GET config:db_user

# 효율적인 조회 (1번의 네트워크 호출)
MGET config:db_host config:db_port config:db_name config:db_user
```

### 5.5 멀티 키 조작 실무 활용 패턴

#### 1) 사용자 프로필 일괄 설정
```bash
# 회원가입 시 사용자 정보 일괄 저장
127.0.0.1:6379> MSET \
  user:1001:name "김철수" \
  user:1001:email "kim@example.com" \
  user:1001:phone "010-1234-5678" \
  user:1001:address "서울시 강남구" \
  user:1001:join_date "2024-01-01" \
  user:1001:status "active"
OK

# 사용자 정보 일괄 조회
127.0.0.1:6379> MGET \
  user:1001:name \
  user:1001:email \
  user:1001:phone \
  user:1001:address \
  user:1001:status
1) "김철수"
2) "kim@example.com"
3) "010-1234-5678"
4) "서울시 강남구"
5) "active"
```

#### 2) 설정값 일괄 관리
```bash
# 애플리케이션 설정 일괄 저장
127.0.0.1:6379> MSET \
  config:max_connections 1000 \
  config:timeout 30 \
  config:retry_count 3 \
  config:cache_ttl 3600 \
  config:debug_mode "false" \
  config:environment "production"
OK

# 설정 확인
127.0.0.1:6379> MGET \
  config:max_connections \
  config:timeout \
  config:retry_count \
  config:cache_ttl \
  config:debug_mode \
  config:environment
1) "1000"
2) "30"
3) "3"
4) "3600"
5) "false"
6) "production"
```

---

## 🎯 실전 종합 프로젝트

### 프로젝트 1: 완전한 사용자 관리 시스템

**난이도**: ⭐⭐⭐☆☆
**예상 소요 시간**: 2-3시간
**학습 목표**: String 타입을 활용한 실무 수준의 사용자 관리 시스템 구축

#### 요구사항
- 사용자 프로필 관리
- 로그인 세션 관리
- 사용자 활동 로그
- 계정 상태 관리

#### 구현

##### 1) 사용자 등록
```bash
# 사용자 기본 정보 등록
127.0.0.1:6379> MSET \
  user:1001:profile:name "김철수" \
  user:1001:profile:email "kim@example.com" \
  user:1001:profile:phone "010-1234-5678" \
  user:1001:profile:join_date "2024-01-01" \
  user:1001:profile:status "active" \
  user:1001:profile:login_count 0
OK

# 사용자 설정
127.0.0.1:6379> MSET \
  user:1001:settings:theme "light" \
  user:1001:settings:language "ko" \
  user:1001:settings:notifications "true" \
  user:1001:settings:privacy "public"
OK
```

##### 2) 로그인 처리
```bash
# 로그인 카운트 증가
127.0.0.1:6379> INCR user:1001:profile:login_count
(integer) 1

# 세션 생성 (30분 만료)
127.0.0.1:6379> MSET \
  session:sess_abc123:user_id "1001" \
  session:sess_abc123:login_time "2024-01-01T10:00:00Z" \
  session:sess_abc123:ip "192.168.1.100" \
  session:sess_abc123:user_agent "Mozilla/5.0..."
OK

# 세션 만료시간 설정
127.0.0.1:6379> EXPIRE session:sess_abc123:user_id 1800
(integer) 1
127.0.0.1:6379> EXPIRE session:sess_abc123:login_time 1800
(integer) 1
127.0.0.1:6379> EXPIRE session:sess_abc123:ip 1800
(integer) 1
127.0.0.1:6379> EXPIRE session:sess_abc123:user_agent 1800
(integer) 1

# 마지막 로그인 시간 업데이트
127.0.0.1:6379> SET user:1001:profile:last_login "2024-01-01T10:00:00Z"
OK
```

##### 3) 사용자 활동 로깅
```bash
# 활동 로그 시작
127.0.0.1:6379> SET user:1001:activity:2024-01-01 "10:00:00 - 로그인"
OK

# 활동 추가
127.0.0.1:6379> APPEND user:1001:activity:2024-01-01 "\n10:05:00 - 프로필 조회"
(integer) 42

127.0.0.1:6379> APPEND user:1001:activity:2024-01-01 "\n10:10:00 - 설정 변경"
(integer) 65

# 일일 활동 로그에 만료시간 설정 (30일)
127.0.0.1:6379> EXPIRE user:1001:activity:2024-01-01 2592000
(integer) 1
```

### 프로젝트 2: 실시간 통계 대시보드

**난이도**: ⭐⭐⭐⭐☆
**예상 소요 시간**: 3-4시간
**학습 목표**: 원자적 연산을 활용한 실시간 통계 시스템 구축

#### 요구사항
- 실시간 방문자 수
- 페이지별 조회수
- 시간대별 통계
- 일일/월별 누적 통계

#### 구현

##### 1) 실시간 카운터 초기화
```bash
# 현재 온라인 사용자 수
127.0.0.1:6379> SET stats:realtime:online_users 0
OK

# 실시간 페이지 뷰
127.0.0.1:6379> SET stats:realtime:page_views 0
OK

# 실시간 주문 수
127.0.0.1:6379> SET stats:realtime:orders 0
OK
```

##### 2) 페이지별 통계 관리
```bash
# 페이지별 조회수 초기화
127.0.0.1:6379> MSET \
  stats:pages:home 0 \
  stats:pages:products 0 \
  stats:pages:cart 0 \
  stats:pages:checkout 0 \
  stats:pages:profile 0
OK

# 방문 시마다 증가
127.0.0.1:6379> INCR stats:pages:home
(integer) 1

127.0.0.1:6379> INCR stats:pages:products
(integer) 1

127.0.0.1:6379> INCR stats:pages:home
(integer) 2
```

##### 3) 시간대별 통계
```bash
# 시간별 방문자 수 (현재 시간: 10시)
127.0.0.1:6379> INCR stats:hourly:2024-01-01:10:visitors
(integer) 1

127.0.0.1:6379> INCR stats:hourly:2024-01-01:10:visitors
(integer) 2

# 시간별 주문 수
127.0.0.1:6379> INCR stats:hourly:2024-01-01:10:orders
(integer) 1

# 시간별 매출 (실수)
127.0.0.1:6379> INCRBYFLOAT stats:hourly:2024-01-01:10:revenue 1299.99
"1299.99"

127.0.0.1:6379> INCRBYFLOAT stats:hourly:2024-01-01:10:revenue 599.00
"1898.99"
```

### 프로젝트 3: 간단한 캐시 시스템

**난이도**: ⭐⭐⭐☆☆
**예상 소요 시간**: 2시간
**학습 목표**: SETEX를 활용한 캐싱 시스템 구축

#### 구현

##### 1) API 응답 캐싱
```bash
# API 응답 캐시 (5분 만료)
127.0.0.1:6379> SETEX cache:api:users:list 300 '[{"id":1,"name":"김철수"},{"id":2,"name":"이영희"}]'
OK

127.0.0.1:6379> SETEX cache:api:products:electronics 300 '[{"id":1001,"name":"노트북","price":1299000}]'
OK

# 캐시 조회
127.0.0.1:6379> GET cache:api:users:list
"[{\"id\":1,\"name\":\"김철수\"},{\"id\":2,\"name\":\"이영희\"}]"

# 캐시 히트 통계 증가
127.0.0.1:6379> INCR cache:stats:hits
(integer) 1
```

##### 2) 캐시 통계 관리
```bash
# 캐시 통계 초기화
127.0.0.1:6379> MSET \
  cache:stats:hits 0 \
  cache:stats:misses 0 \
  cache:stats:sets 0 \
  cache:stats:deletes 0
OK

# 캐시 히트 시
127.0.0.1:6379> INCR cache:stats:hits
(integer) 1

# 캐시 미스 시
127.0.0.1:6379> INCR cache:stats:misses
(integer) 1
```

### 트러블슈팅

#### 문제 1: Redis 메모리 부족 에러
**증상**:
```
(error) OOM command not allowed when used memory > 'maxmemory'
```

**원인**: Redis 최대 메모리 설정을 초과하여 새로운 데이터 저장 불가

**해결 방법**:
```bash
# 1. 현재 메모리 사용량 확인
127.0.0.1:6379> INFO memory
used_memory_human:950.00M
maxmemory:1.00G

# 2. maxmemory 증가 (임시)
127.0.0.1:6379> CONFIG SET maxmemory 2gb
OK

# 3. 또는 eviction policy 설정
127.0.0.1:6379> CONFIG SET maxmemory-policy allkeys-lru
OK

# 4. 불필요한 키 삭제
127.0.0.1:6379> DEL cache:old:key1 cache:old:key2
(integer) 2

# 5. 모든 캐시 데이터에 TTL 설정 확인
127.0.0.1:6379> TTL cache:api:users:list
(integer) 245  # TTL이 설정되어 있음
```

#### 문제 2: INCR 명령어가 에러 발생
**증상**:
```
(error) ERR value is not an integer or out of range
```

**원인**: 문자열 타입의 키에 INCR 시도

**해결 방법**:
```bash
# 문제 원인 확인
127.0.0.1:6379> GET counter
"hello"  # 숫자가 아님!

# 해결: 키 삭제 후 재설정
127.0.0.1:6379> DEL counter
(integer) 1

127.0.0.1:6379> SET counter 0
OK

127.0.0.1:6379> INCR counter
(integer) 1
```

#### 문제 3: 한글 데이터 GETRANGE 시 깨짐
**증상**: 한글 문자열 일부 추출 시 깨진 문자 출력

**원인**: GETRANGE는 바이트 단위로 동작, 한글은 UTF-8에서 3바이트

**해결 방법**:
```bash
# 문제 상황
127.0.0.1:6379> SET message "안녕하세요"
OK

127.0.0.1:6379> GETRANGE message 0 2
"안"  # 1글자만 출력 (3바이트)

# 해결: 바이트 계산 정확히
127.0.0.1:6379> GETRANGE message 0 8
"안녕하"  # 3글자 (9바이트 = 0~8)

# 또는 전체 GET 후 애플리케이션에서 슬라이싱
```

### 확장 아이디어

#### 추가 기능 1: 캐시 히트율 자동 모니터링
**난이도**: ⭐⭐⭐⭐☆
**구현 힌트**:
- Lua 스크립트로 히트/미스 자동 집계
- 히트율이 70% 이하면 알림 발송
- 시간대별 히트율 통계 수집

```bash
# Lua 스크립트 예시
EVAL "
local hits = redis.call('GET', 'cache:stats:hits') or 0
local misses = redis.call('GET', 'cache:stats:misses') or 0
local total = tonumber(hits) + tonumber(misses)
if total > 0 then
    local hit_rate = (tonumber(hits) / total) * 100
    redis.call('SET', 'cache:stats:hit_rate', hit_rate)
    return hit_rate
end
return 0
" 0
```

#### 추가 기능 2: 분산 락 구현
**난이도**: ⭐⭐⭐⭐⭐
**구현 힌트**:
- SETNX + EXPIRE로 락 획득
- Lua 스크립트로 원자성 보장
- 타임아웃 처리

```bash
# 분산 락 획득
SET lock:resource:12345 "unique_token" NX EX 10

# 락 해제 (자신의 락인지 확인 후)
EVAL "
if redis.call('GET', KEYS[1]) == ARGV[1] then
    return redis.call('DEL', KEYS[1])
else
    return 0
end
" 1 lock:resource:12345 "unique_token"
```

### 코드 리뷰 포인트

#### 체크리스트
- [ ] 모든 캐시 키에 TTL이 설정되어 있는가?
- [ ] 카운터는 INCR/DECR을 사용하는가? (GET+SET 금지)
- [ ] 만료시간 설정은 SETEX를 사용하는가? (SET+EXPIRE 분리 금지)
- [ ] 여러 키 조회 시 MGET을 사용하는가?
- [ ] 키 명명 규칙이 일관적인가? (예: cache:api:users:list)
- [ ] 한글 문자열 GETRANGE 사용 시 바이트 단위 고려했는가?
- [ ] 대용량 데이터(1MB 이상)를 String에 저장하지 않았는가?
- [ ] 에러 처리가 적절한가? (nil 체크, 타입 체크)
- [ ] 메모리 정책(maxmemory-policy)이 설정되어 있는가?
- [ ] 성능 테스트를 수행했는가?

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: 동시성 문제로 인한 카운터 오류

**상황**: 신입 개발자 김주니어는 좋아요 기능을 구현하면서 GET → +1 → SET 패턴을 사용했습니다.

```python
# ❌ 주니어 개발자가 작성한 코드
def increment_likes(post_id):
    # 현재 좋아요 수 조회
    current_likes = redis.get(f"post:{post_id}:likes")
    if current_likes is None:
        current_likes = 0
    else:
        current_likes = int(current_likes)

    # 1 증가
    new_likes = current_likes + 1

    # 저장
    redis.set(f"post:{post_id}:likes", new_likes)
    return new_likes
```

**문제점**:
- 문제 1: 동시에 100명이 좋아요를 누르면 100이 아닌 1~100 사이의 임의 값이 됨
- 문제 2: GET과 SET 사이에 다른 요청이 끼어들 수 있음 (Race Condition)
- 왜 이 문제가 발생하는가: 읽기-수정-쓰기가 원자적이지 않음

**해결책**:
```python
# ✅ 올바른 코드
def increment_likes(post_id):
    # INCR은 원자적 연산으로 동시성 문제 없음
    new_likes = redis.incr(f"post:{post_id}:likes")
    return new_likes

# 설명
# 1. INCR 명령어는 내부적으로 원자적으로 실행됨
# 2. 100명이 동시에 실행해도 정확히 100이 됨
# 3. 성능도 더 빠름 (네트워크 왕복 3번 → 1번)
```

**배운 점**:
- 💡 팁 1: 카운터는 항상 INCR/DECR 사용
- 💡 팁 2: GET + 계산 + SET은 원자성이 보장되지 않음
- 💡 팁 3: Redis의 원자적 연산을 최대한 활용하자

### 시나리오 2: 캐시 만료시간을 설정하지 않아 메모리 부족

**상황**: 신입 개발자가 캐시 데이터에 만료시간을 설정하지 않아 메모리가 계속 증가했습니다.

```python
# ❌ 주니어 개발자가 작성한 코드
def cache_user_profile(user_id, profile_data):
    # JSON으로 변환하여 저장
    redis.set(f"cache:user:{user_id}", json.dumps(profile_data))
    # 만료시간 설정 없음!
```

**문제점**:
- 문제 1: 캐시 데이터가 영구적으로 저장되어 메모리 낭비
- 문제 2: 사용자가 프로필을 수정해도 오래된 캐시 데이터 반환
- 문제 3: Redis 메모리 부족으로 서비스 중단 위험

**해결책**:
```python
# ✅ 올바른 코드
def cache_user_profile(user_id, profile_data):
    # JSON으로 변환하여 저장 (5분 TTL)
    redis.setex(
        f"cache:user:{user_id}",
        300,  # 5분 (300초)
        json.dumps(profile_data)
    )

# 또는 SET 명령어의 EX 옵션 사용
def cache_user_profile_v2(user_id, profile_data):
    redis.set(
        f"cache:user:{user_id}",
        json.dumps(profile_data),
        ex=300  # 5분
    )

# 설명
# 1. SETEX 또는 SET with EX 옵션 사용
# 2. 적절한 TTL 설정으로 메모리 관리
# 3. 데이터 신선도 유지 (5분마다 갱신)
```

**배운 점**:
- 💡 팁 1: 캐시 데이터는 항상 TTL 설정
- 💡 팁 2: TTL은 데이터 특성에 맞게 설정 (세션 30분, 캐시 5분, OTP 3분 등)
- 💡 팁 3: 메모리 모니터링 필수

### 시나리오 3: MGET/MSET을 몰라서 네트워크 낭비

**상황**: 여러 개의 설정값을 조회할 때 반복문으로 GET을 호출했습니다.

```python
# ❌ 주니어 개발자가 작성한 코드
def get_all_configs():
    config_keys = [
        "config:db_host",
        "config:db_port",
        "config:db_name",
        "config:cache_ttl",
        "config:max_connections"
    ]

    configs = {}
    for key in config_keys:
        # 네트워크 왕복 5번!
        configs[key] = redis.get(key)

    return configs
```

**문제점**:
- 문제 1: 네트워크 왕복 5번 발생 (응답 시간 50ms × 5 = 250ms)
- 문제 2: Redis 서버에 부하 증가
- 문제 3: 설정이 많아질수록 성능 저하

**해결책**:
```python
# ✅ 올바른 코드
def get_all_configs():
    config_keys = [
        "config:db_host",
        "config:db_port",
        "config:db_name",
        "config:cache_ttl",
        "config:max_connections"
    ]

    # MGET으로 한 번에 조회 (네트워크 왕복 1번!)
    values = redis.mget(config_keys)

    # 딕셔너리로 변환
    configs = dict(zip(config_keys, values))
    return configs

# 설정도 마찬가지
def set_all_configs(configs):
    # MSET으로 한 번에 설정
    redis.mset(configs)

# 설명
# 1. MGET/MSET으로 여러 키를 한 번에 처리
# 2. 네트워크 왕복 5번 → 1번 (5배 성능 향상)
# 3. 응답 시간 250ms → 50ms
```

**배운 점**:
- 💡 팁 1: 여러 키 처리는 MGET/MSET 사용
- 💡 팁 2: 네트워크 왕복을 최소화하는 것이 성능의 핵심
- 💡 팁 3: 단, 너무 많은 키(1000개 이상)는 분할 처리

### 시나리오 4: 한글 문자열의 GETRANGE 사용 시 깨짐

**상황**: 한글 문자열에서 일부를 추출하려다 글자가 깨졌습니다.

```python
# ❌ 주니어 개발자가 작성한 코드
redis.set("message", "안녕하세요 Redis")

# 앞 3글자만 가져오려고 시도
result = redis.getrange("message", 0, 2)
print(result)  # "안" (깨진 글자!)
```

**문제점**:
- 문제 1: GETRANGE는 바이트 단위로 동작
- 문제 2: 한글은 UTF-8에서 한 글자당 3바이트
- 문제 3: 0~2 바이트는 "안" 1글자만 (3바이트)

**해결책**:
```python
# ✅ 올바른 코드
redis.set("message", "안녕하세요 Redis")

# 방법 1: 전체를 가져와서 애플리케이션에서 슬라이싱
message = redis.get("message").decode('utf-8')
result = message[:3]  # "안녕하"
print(result)

# 방법 2: 바이트 단위로 정확히 계산
# 한글 1글자 = 3바이트
# "안녕하" = 9바이트 (0~8)
result = redis.getrange("message", 0, 8)
print(result.decode('utf-8'))  # "안녕하"

# 설명
# 1. Redis는 바이트 단위로 동작
# 2. 한글은 문자 단위 처리를 애플리케이션에서 수행
# 3. 또는 바이트 계산을 정확히 수행
```

**배운 점**:
- 💡 팁 1: GETRANGE는 바이트 단위임을 명심
- 💡 팁 2: 한글/이모지 등 멀티바이트 문자는 애플리케이션에서 처리
- 💡 팁 3: 영문/숫자만 사용하는 경우에는 GETRANGE가 유용

---

## ❓ FAQ

<details>
<summary><strong>Q1: String 타입에 JSON을 저장할 때 주의사항은?</strong></summary>

**A**: JSON 저장 시 고려사항이 있습니다.

**상세 설명**:
- 포인트 1: 큰따옴표 이스케이프 처리 필요
- 포인트 2: 부분 수정이 어려움 (전체 교체만 가능)
- 포인트 3: JSON 내부 검색 불가능

**예시**:
```bash
# 올바른 JSON 저장
SET user_data '{"name":"김철수","age":30}'  # 작은따옴표 사용 권장

# 문제점: 나이만 수정하려면?
GET user_data  # 전체 조회
# 애플리케이션에서 파싱
# age 값 수정
SET user_data '{"name":"김철수","age":31}'  # 전체 재저장

# 대안: Hash 타입 사용
HSET user:1001 name "김철수" age 30
HINCRBY user:1001 age 1  # age만 증가
```

**실무 팁**:
💡 자주 변경되는 필드가 있다면 Hash 타입 고려, 읽기만 하는 데이터는 String+JSON이 적합

</details>

<details>
<summary><strong>Q2: INCR과 GET+SET의 성능 차이는?</strong></summary>

**A**: INCR이 훨씬 빠르고 안전합니다.

**상세 설명**:
- 포인트 1: INCR은 원자적 연산으로 동시성 문제 없음
- 포인트 2: 네트워크 왕복 1번 vs 3번
- 포인트 3: Race Condition 방지

**예시**:
```bash
# INCR: 원자적, 빠름, 안전
INCR counter  # 1번의 명령어

# GET + 계산 + SET: 비원자적, 느림, 동시성 문제
GET counter   # 1번째 명령어
# 애플리케이션에서 +1 계산
SET counter newvalue  # 2번째 명령어
# → 총 2번의 네트워크 왕복, 동시 요청 시 데이터 손실
```

**성능 비교**:
| 방식 | 네트워크 왕복 | 동시성 안전 | 응답시간 |
|------|--------------|------------|---------|
| INCR | 1번 | ✅ 안전 | 1ms |
| GET+SET | 2번 | ❌ 위험 | 2-3ms |

**실무 팁**:
💡 카운터는 무조건 INCR/DECR 사용, GET+SET은 절대 사용 금지

</details>

<details>
<summary><strong>Q3: APPEND vs SETRANGE 언제 사용하나요?</strong></summary>

**A**: 용도가 다릅니다.

**상세 설명**:
- APPEND: 끝에 추가할 때 (로그, 메시지 누적)
- SETRANGE: 특정 위치 수정할 때 (플래그, 상태 변경)

**예시**:
```bash
# APPEND: 끝에 추가
SET log "첫 줄"
APPEND log "\n둘째 줄"
APPEND log "\n셋째 줄"
# → "첫 줄\n둘째 줄\n셋째 줄"

# SETRANGE: 중간 수정
SET status "inactive"
SETRANGE status 0 "active  "
# → "active  "
```

**성능**: APPEND가 일반적으로 더 빠름

**실무 팁**:
💡 로그나 히스토리는 APPEND, 상태나 플래그는 SETRANGE

</details>

<details>
<summary><strong>Q4: 한글 문자열의 GETRANGE 주의사항은?</strong></summary>

**A**: 바이트 단위로 동작하므로 주의 필요합니다.

**상세 설명**:
- 포인트 1: GETRANGE는 바이트 단위
- 포인트 2: 한글은 UTF-8에서 3바이트
- 포인트 3: 잘못 사용하면 글자 깨짐

**예시**:
```bash
SET korean "안녕하세요"
STRLEN korean
# (integer) 15  # UTF-8 바이트 수

GETRANGE korean 0 2
# "안"  # 한글 1글자 = 3바이트

# 올바른 사용
GETRANGE korean 0 8
# "안녕하"  # 3글자 = 9바이트 (0~8)
```

**해결책**: 애플리케이션에서 문자 단위 처리

**실무 팁**:
💡 한글/이모지는 전체 GET 후 애플리케이션에서 슬라이싱

</details>

<details>
<summary><strong>Q5: 대용량 문자열 처리 시 주의사항은?</strong></summary>

**A**: Redis String 최대 크기는 512MB이지만 실무에서는 1MB 이하 권장합니다.

**상세 설명**:
- 포인트 1: 큰 데이터는 메모리 낭비
- 포인트 2: 네트워크 전송 시간 증가
- 포인트 3: Redis 블로킹 발생 가능

**큰 데이터 처리 방법**:
1. **압축 후 저장**
```python
import gzip
import json

data = {"large": "data" * 1000}
compressed = gzip.compress(json.dumps(data).encode())
redis.set("large_data", compressed)

# 조회 시 압축 해제
compressed = redis.get("large_data")
data = json.loads(gzip.decompress(compressed))
```

2. **청크 단위로 분할 저장**
```python
# 큰 파일을 1MB 단위로 분할
chunk_size = 1024 * 1024  # 1MB
for i, chunk in enumerate(chunks):
    redis.set(f"file:12345:chunk:{i}", chunk)
```

3. **별도 스토리지 사용**
```python
# S3나 파일시스템에 저장하고 URL만 Redis에
s3_url = upload_to_s3(large_file)
redis.set("file:12345:url", s3_url)
```

**실무 팁**:
💡 1MB 이상 데이터는 Redis 외부에 저장하고 참조만 Redis에

</details>

<details>
<summary><strong>Q6: SETEX vs SET + EXPIRE의 차이는?</strong></summary>

**A**: SETEX가 원자적이고 권장됩니다.

**상세 설명**:
- 포인트 1: SETEX는 하나의 명령어 (원자적)
- 포인트 2: SET + EXPIRE는 두 개의 명령어 (비원자적)
- 포인트 3: SET 후 EXPIRE 전 서버 장애 시 만료시간 미설정

**예시**:
```bash
# ❌ 비권장: SET + EXPIRE
SET session:abc123 "data"
# 여기서 서버 장애 발생 시 만료시간 미설정!
EXPIRE session:abc123 1800

# ✅ 권장: SETEX (원자적)
SETEX session:abc123 1800 "data"

# 또는 SET with EX option
SET session:abc123 "data" EX 1800
```

**실무 팁**:
💡 만료시간이 필요한 경우 항상 SETEX 또는 SET with EX 사용

</details>

<details>
<summary><strong>Q7: 여러 키를 조회할 때 MGET vs Pipeline의 차이는?</strong></summary>

**A**: 용도가 다릅니다.

**상세 설명**:
- MGET: 같은 명령어(GET)를 여러 키에 실행
- Pipeline: 다른 명령어들을 일괄 실행

**예시**:
```python
# MGET: GET 명령어만
values = redis.mget(["key1", "key2", "key3"])

# Pipeline: 다양한 명령어 조합
pipe = redis.pipeline()
pipe.get("key1")
pipe.incr("counter")
pipe.hget("hash", "field")
results = pipe.execute()
```

**성능**:
| 방식 | 네트워크 왕복 | 용도 |
|------|--------------|------|
| 개별 명령어 | N번 | 일반 |
| MGET | 1번 | 같은 명령어 |
| Pipeline | 1번 | 다른 명령어 조합 |

**실무 팁**:
💡 GET만 여러 개면 MGET, 다양한 명령어면 Pipeline

</details>

<details>
<summary><strong>Q8: String 타입의 메모리 효율은?</strong></summary>

**A**: 인코딩 방식에 따라 메모리 사용량이 달라집니다.

**상세 설명**:
- int: 8바이트 (정수)
- embstr: 문자열 + 오버헤드 (44바이트 이하)
- raw: 문자열 + 포인터 + 오버헤드 (44바이트 초과)

**예시**:
```bash
# int 인코딩 (가장 효율적)
SET counter 12345
OBJECT ENCODING counter
# "int"

# embstr 인코딩 (효율적)
SET short "작은 문자열"
OBJECT ENCODING short
# "embstr"

# raw 인코딩 (일반)
SET long "매우 긴 문자열입니다..." (45바이트 이상)
OBJECT ENCODING long
# "raw"
```

**최적화 팁**:
- 숫자는 정수로 저장 (문자열 "123" 보다 숫자 123이 효율적)
- 짧은 문자열은 자동으로 embstr로 최적화
- 긴 문자열은 압축 고려

**실무 팁**:
💡 가능하면 정수로 저장, 긴 문자열은 압축 또는 분할

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. Redis String 타입이란 무엇이고, 어떤 데이터를 저장할 수 있나요?</strong></summary>

**모범 답안 포인트**
- 포인트 1: Redis의 가장 기본적인 데이터 타입
- 포인트 2: 바이너리 안전(binary-safe)하여 문자열, 숫자, JSON, 바이너리 모두 저장 가능
- 포인트 3: 최대 512MB까지 저장 가능

**예시 답변**
> "Redis String은 가장 기본적인 key-value 타입으로, 단순한 문자열뿐만 아니라 숫자, JSON, 이미지 등 바이너리 데이터도 저장할 수 있습니다. 최대 512MB까지 저장 가능하며, 실무에서는 세션 데이터, 캐시, 카운터 등 다양하게 활용됩니다."

**꼬리 질문**
- Q: String 타입의 내부 인코딩 방식은?
- A: int(정수), embstr(44바이트 이하), raw(44바이트 초과) 3가지입니다.

**실무 연관**
- 세션 관리: 사용자 로그인 정보 저장
- 캐시: API 응답 결과 저장
- 카운터: 좋아요 수, 조회수 관리

</details>

<details>
<summary><strong>2. INCR 명령어를 사용하는 이유와 GET+SET 대비 장점은?</strong></summary>

**모범 답안 포인트**
- 포인트 1: 원자적(atomic) 연산으로 동시성 문제 해결
- 포인트 2: 네트워크 왕복 1번 vs 2-3번으로 성능 향상
- 포인트 3: Race Condition 방지

**예시 답변**
> "INCR은 원자적 연산으로 동시에 여러 요청이 와도 정확한 카운팅이 보장됩니다. GET으로 값을 읽고 +1 계산 후 SET으로 저장하는 방식은 읽기와 쓰기 사이에 다른 요청이 끼어들 수 있어 데이터 불일치가 발생합니다. 또한 INCR은 네트워크 왕복이 1번이라 성능도 3배 정도 빠릅니다."

**꼬리 질문**
- Q: 실수 증감은 어떻게 하나요?
- A: INCRBYFLOAT 명령어를 사용합니다.

**실무 연관**
- 좋아요 수 증가
- 조회수 카운팅
- 재고 관리

</details>

<details>
<summary><strong>3. SETEX와 SET + EXPIRE의 차이점과 어떤 것을 사용해야 하나요?</strong></summary>

**모범 답안 포인트**
- 포인트 1: SETEX는 원자적, SET + EXPIRE는 비원자적
- 포인트 2: SET 후 EXPIRE 전 장애 발생 시 만료시간 미설정 위험
- 포인트 3: SETEX 또는 SET with EX option 권장

**예시 답변**
> "SETEX는 값 설정과 만료시간 설정을 하나의 명령어로 원자적으로 수행합니다. 반면 SET 후 EXPIRE를 따로 실행하면 두 개의 명령어 사이에 서버 장애가 발생할 경우 만료시간이 설정되지 않아 메모리 누수가 발생할 수 있습니다. 따라서 SETEX 또는 SET with EX option을 사용하는 것이 안전합니다."

**꼬리 질문**
- Q: 밀리초 단위 만료시간은?
- A: PSETEX 또는 SET with PX option을 사용합니다.

**실무 연관**
- 세션 관리 (30분 TTL)
- OTP 관리 (3분 TTL)
- 캐시 데이터 (5-10분 TTL)

</details>

<details>
<summary><strong>4. MGET/MSET을 사용하는 이유와 성능상 이점은?</strong></summary>

**모범 답안 포인트**
- 포인트 1: 여러 키를 한 번에 처리하여 네트워크 왕복 최소화
- 포인트 2: N개 키 처리 시 네트워크 왕복 N번 → 1번
- 포인트 3: 응답 시간 및 처리량 대폭 향상

**예시 답변**
> "MGET/MSET은 여러 개의 키를 한 번의 명령어로 처리하여 네트워크 왕복 횟수를 획기적으로 줄입니다. 예를 들어 10개의 키를 조회할 때 개별 GET을 10번 호출하면 네트워크 왕복 10번이 필요하지만, MGET을 사용하면 1번만 필요합니다. 네트워크 지연이 10ms라면 100ms → 10ms로 10배 성능 향상이 가능합니다."

**꼬리 질문**
- Q: MGET으로 수천 개의 키를 조회해도 되나요?
- A: 너무 많은 키(1000개 이상)는 분할 처리하는 것이 좋습니다.

**실무 연관**
- 사용자 프로필 여러 필드 조회
- 설정값 일괄 업데이트
- 대시보드 데이터 조회

</details>

<details>
<summary><strong>5. String 타입에 JSON을 저장할 때 장단점은?</strong></summary>

**모범 답안 포인트**
- 포인트 1: 장점 - 간단하고 빠르게 저장/조회 가능
- 포인트 2: 단점 - 부분 수정 불가능 (전체 교체만 가능)
- 포인트 3: 단점 - JSON 내부 필드 검색 불가능

**예시 답변**
> "String 타입에 JSON을 저장하면 간단하게 복잡한 데이터를 저장할 수 있고, 전체 조회가 빠릅니다. 하지만 JSON 내부의 특정 필드만 수정하려면 전체를 읽어서 파싱하고 수정 후 다시 저장해야 하는 단점이 있습니다. 또한 JSON 내부 필드로 검색이 불가능합니다. 자주 변경되는 필드가 있다면 Hash 타입을 고려하는 것이 좋습니다."

**꼬리 질문**
- Q: JSON 내부 필드를 효율적으로 다루려면?
- A: Hash 타입을 사용하거나 RedisJSON 모듈을 고려합니다.

**실무 연관**
- 사용자 프로필 캐싱
- API 응답 캐싱
- 설정 데이터 저장

</details>

<details>
<summary><strong>6. APPEND 명령어의 실무 활용 사례는?</strong></summary>

**모범 답안 포인트**
- 포인트 1: 문자열 끝에 데이터 추가
- 포인트 2: 로그 수집, 메시지 히스토리에 유용
- 포인트 3: 키가 없으면 새로 생성

**예시 답변**
> "APPEND는 기존 문자열의 끝에 새로운 데이터를 추가하는 명령어로, 사용자 활동 로그나 채팅 메시지 히스토리를 누적할 때 유용합니다. 예를 들어 사용자의 오늘 활동을 'user:1001:activity:2024-01-01' 키에 시간순으로 APPEND하여 기록할 수 있습니다. 키가 없으면 자동으로 생성되어 첫 데이터로 저장됩니다."

**꼬리 질문**
- Q: APPEND와 SETRANGE의 차이는?
- A: APPEND는 끝에 추가, SETRANGE는 특정 위치 수정입니다.

**실무 연관**
- 사용자 활동 로그
- 채팅 메시지 누적
- 센서 데이터 수집

</details>

<details>
<summary><strong>7. Redis String 타입의 메모리 최적화 방법은?</strong></summary>

**모범 답안 포인트**
- 포인트 1: 숫자는 정수로 저장 (int 인코딩)
- 포인트 2: 큰 데이터는 압축 또는 분할
- 포인트 3: 적절한 TTL 설정으로 메모리 관리

**예시 답변**
> "Redis String의 메모리를 최적화하려면 첫째, 가능하면 숫자를 정수로 저장하여 int 인코딩을 활용합니다. 둘째, 1MB 이상의 큰 데이터는 gzip 압축하거나 청크 단위로 분할 저장합니다. 셋째, 모든 캐시 데이터에 적절한 TTL을 설정하여 불필요한 데이터가 메모리를 차지하지 않도록 합니다."

**꼬리 질문**
- Q: embstr과 raw 인코딩의 차이는?
- A: 44바이트 이하는 embstr(단일 메모리 할당), 초과는 raw(별도 메모리 할당)입니다.

**실무 연관**
- 메모리 비용 절감
- 성능 최적화
- 대용량 서비스 운영

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. Redis String의 내부 구조(SDS)와 C 문자열 대비 장점은?</strong></summary>

**모범 답안 포인트**
- 포인트 1: SDS(Simple Dynamic String) 구조 사용
- 포인트 2: O(1) 시간 복잡도로 문자열 길이 조회
- 포인트 3: 버퍼 오버플로우 방지, 바이너리 안전

**예시 답변**
> "Redis는 C 문자열 대신 SDS(Simple Dynamic String)를 사용합니다. SDS는 길이 정보를 헤더에 저장하여 STRLEN을 O(1)로 수행하고, 할당된 버퍼 크기를 관리하여 버퍼 오버플로우를 방지합니다. 또한 NULL 바이트를 포함할 수 있어 바이너리 안전하며, 공간 사전 할당(space preallocation) 전략으로 재할당 빈도를 줄여 성능을 최적화합니다."

**실무 예시**:
```c
// SDS 구조 (간략화)
struct sdshdr {
    int len;        // 현재 길이 (O(1) 조회)
    int free;       // 사용 가능한 공간
    char buf[];     // 실제 문자열
};
```

**꼬리 질문**
- Q: SDS의 공간 사전 할당 전략은?
- A: 1MB 미만은 2배 할당, 1MB 이상은 1MB씩 추가 할당하여 재할당 빈도를 줄입니다.

**실무 연관**
- 대용량 데이터 처리 시 성능 예측
- 메모리 사용량 최적화
- 바이너리 데이터 안전한 저장

</details>

<details>
<summary><strong>2. String 타입의 3가지 인코딩(int, embstr, raw)과 변환 조건은?</strong></summary>

**모범 답안 포인트**
- 포인트 1: int - 정수형 데이터 (8바이트)
- 포인트 2: embstr - 44바이트 이하 문자열 (단일 메모리 할당)
- 포인트 3: raw - 44바이트 초과 문자열 (별도 메모리 할당)

**예시 답변**
> "Redis String은 메모리 효율을 위해 3가지 인코딩을 사용합니다. 정수는 int로 저장하여 8바이트만 사용하고, 44바이트 이하 문자열은 embstr로 redisObject와 SDS를 한 번에 할당하여 메모리 단편화를 줄입니다. 44바이트를 초과하면 raw로 전환되어 redisObject와 SDS가 별도로 할당됩니다. embstr은 읽기 전용이므로 수정 시 raw로 변환됩니다."

**실무 예시**:
```bash
# int 인코딩
SET counter 12345
OBJECT ENCODING counter  # "int"
MEMORY USAGE counter     # 8바이트 + 오버헤드

# embstr 인코딩 (44바이트 이하)
SET short "Hello Redis"
OBJECT ENCODING short    # "embstr"

# raw 인코딩 (44바이트 초과)
SET long "Very long string..." (45바이트 이상)
OBJECT ENCODING long     # "raw"

# embstr → raw 변환
APPEND short " World"
OBJECT ENCODING short    # "raw" (수정되어 변환)
```

**꼬리 질문**
- Q: 44바이트 기준의 의미는?
- A: redisObject(16바이트) + SDS 헤더(9바이트) + 문자열(44바이트) + NULL(1바이트) = 70바이트가 jemalloc의 64바이트 클래스에 맞는 최적값입니다.

**실무 연관**
- 메모리 사용량 예측 및 최적화
- 대량 데이터 저장 시 인코딩 선택
- 성능 튜닝

</details>

<details>
<summary><strong>3. 대규모 트래픽 환경에서 INCR을 활용한 Rate Limiting 구현 방법은?</strong></summary>

**모범 답안 포인트**
- 포인트 1: INCR + EXPIRE로 시간 윈도우 기반 제한
- 포인트 2: 슬라이딩 윈도우는 Sorted Set 활용
- 포인트 3: 분산 환경에서 원자성 보장

**예시 답변**
> "Rate Limiting은 INCR의 원자성을 활용하여 구현합니다. 고정 윈도우 방식은 IP별로 'rate:limit:{IP}:{timestamp}' 키를 만들어 INCR로 카운팅하고 첫 요청 시 EXPIRE로 윈도우 시간을 설정합니다. 더 정교한 슬라이딩 윈도우는 Sorted Set에 타임스탬프를 저장하여 구현합니다. Lua 스크립트로 INCR과 비교를 원자적으로 수행하면 분산 환경에서도 정확한 제한이 가능합니다."

**실무 예시**:
```python
# 고정 윈도우 방식
def rate_limit_fixed_window(ip, limit=100, window=3600):
    key = f"rate:limit:{ip}:{int(time.time() // window)}"
    count = redis.incr(key)

    if count == 1:
        redis.expire(key, window)

    return count <= limit

# Lua 스크립트로 원자성 보장
lua_script = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])

local current = redis.call('INCR', key)
if current == 1 then
    redis.call('EXPIRE', key, window)
end

if current > limit then
    return 0
else
    return 1
end
"""

allowed = redis.eval(lua_script, 1, f"rate:limit:{ip}", 100, 3600)
```

**성능 측정 결과**:
- 처리량: 10만 TPS
- 응답 시간: 1ms 이하
- 정확도: 100%

**꼬리 질문**
- Q: 분산 환경에서 여러 Redis 인스턴스를 사용하면?
- A: Redis Cluster나 Sentinel을 사용하거나, 일관된 해싱으로 IP별로 같은 노드에 라우팅합니다.

**실무 연관**
- API Rate Limiting
- DDoS 방어
- 리소스 사용량 제어

</details>

<details>
<summary><strong>4. 대용량 캐시 시스템에서 String 타입의 메모리 관리 전략은?</strong></summary>

**모범 답안 포인트**
- 포인트 1: 적절한 TTL 설정 및 LRU/LFU 정책
- 포인트 2: 압축 및 직렬화 최적화
- 포인트 3: 메모리 모니터링 및 경고 시스템

**예시 답변**
> "대용량 캐시에서는 첫째, 데이터 특성에 맞는 TTL을 설정합니다(세션 30분, API 캐시 5분, 정적 데이터 1시간). 둘째, maxmemory-policy를 allkeys-lru나 volatile-lru로 설정하여 메모리 부족 시 자동 삭제합니다. 셋째, 큰 데이터는 gzip 압축하거나 MessagePack 같은 효율적인 직렬화를 사용합니다. 넷째, INFO memory로 모니터링하고 used_memory_rss가 maxmemory의 80% 넘으면 경고를 발생시킵니다."

**실무 예시**:
```python
# 1. 압축 전략
import gzip
import json

def cache_with_compression(key, data, ttl=300):
    # 1KB 이상만 압축
    json_data = json.dumps(data)
    if len(json_data) > 1024:
        compressed = gzip.compress(json_data.encode())
        redis.setex(f"cache:compressed:{key}", ttl, compressed)
    else:
        redis.setex(f"cache:{key}", ttl, json_data)

# 2. 메모리 모니터링
def check_memory_usage():
    info = redis.info('memory')
    used_memory_rss = info['used_memory_rss']
    maxmemory = info['maxmemory']

    usage_percent = (used_memory_rss / maxmemory) * 100

    if usage_percent > 80:
        alert("Redis memory usage high", usage_percent)

    return usage_percent

# 3. TTL 전략
TTL_CONFIG = {
    'session': 1800,        # 30분
    'api_cache': 300,       # 5분
    'user_profile': 600,    # 10분
    'static_data': 3600,    # 1시간
}
```

**최적화 결과**:
| 항목 | Before | After | 개선 |
|------|--------|-------|------|
| 메모리 사용량 | 10GB | 3GB | 70%↓ |
| 캐시 히트율 | 60% | 95% | 58%↑ |
| 비용 | $500/월 | $150/월 | 70%↓ |

**꼬리 질문**
- Q: maxmemory-policy의 종류와 선택 기준은?
- A: noeviction(쓰기 거부), allkeys-lru(모든 키 LRU), volatile-lru(TTL 있는 키만 LRU) 등이 있으며, 캐시 용도는 allkeys-lru, 세션 용도는 volatile-lru를 권장합니다.

**실무 연관**
- 대규모 캐시 시스템 운영
- 비용 최적화
- 성능 튜닝

</details>

<details>
<summary><strong>5. String 타입의 멀티 키 조작(MGET/MSET)의 내부 동작과 성능 특성은?</strong></summary>

**모범 답안 포인트**
- 포인트 1: 단일 명령어로 여러 키 처리하여 네트워크 왕복 최소화
- 포인트 2: Redis 단일 스레드에서 원자적으로 실행
- 포인트 3: 너무 많은 키는 블로킹 발생 가능

**예시 답변**
> "MGET/MSET은 Redis의 단일 스레드 모델에서 원자적으로 실행되어 여러 키를 한 번에 처리합니다. 네트워크 왕복이 N번에서 1번으로 줄어 레이턴시가 대폭 감소하며, 처리량은 N배 향상됩니다. 단, Redis는 단일 스레드이므로 수천 개의 키를 한 번에 처리하면 다른 명령어가 블로킹될 수 있습니다. 따라서 실무에서는 키를 100~1000개 단위로 나누어 처리하는 것이 권장됩니다."

**실무 예시**:
```python
# 성능 비교
import time

keys = [f"key:{i}" for i in range(1000)]

# 개별 GET (느림)
start = time.time()
for key in keys:
    redis.get(key)
elapsed_individual = time.time() - start
# 약 1초 (네트워크 지연 1ms × 1000)

# MGET (빠름)
start = time.time()
redis.mget(keys)
elapsed_mget = time.time() - start
# 약 10ms (네트워크 지연 1ms × 1 + Redis 처리 9ms)

print(f"개선율: {elapsed_individual / elapsed_mget}배")
# 약 100배 빠름

# 대량 키 처리 (청크 단위)
def mget_chunked(keys, chunk_size=1000):
    results = []
    for i in range(0, len(keys), chunk_size):
        chunk = keys[i:i+chunk_size]
        results.extend(redis.mget(chunk))
    return results

# 1만 개 키 처리
large_keys = [f"key:{i}" for i in range(10000)]
values = mget_chunked(large_keys, chunk_size=1000)
# 네트워크 왕복 10번, 총 약 100ms
```

**성능 측정**:
| 방식 | 1000개 키 | 10000개 키 | 네트워크 왕복 |
|------|----------|-----------|--------------|
| 개별 GET | 1000ms | 10000ms | N번 |
| MGET (단일) | 10ms | 100ms | 1번 |
| MGET (청크) | 10ms | 100ms | N/1000번 |

**꼬리 질문**
- Q: Pipeline과 MGET의 차이는?
- A: MGET은 GET 명령어만 일괄 실행, Pipeline은 다양한 명령어를 일괄 전송할 수 있습니다.

**실무 연관**
- 대시보드 데이터 조회 최적화
- 대량 설정값 업데이트
- 캐시 워밍(Cache Warming)

</details>

---

## 📝 핵심 정리

### 학습 목표 달성도 체크

**이 장을 완료하면 다음과 같은 능력을 갖게 됩니다:**

✅ **String 타입의 내부 구조와 특징 완벽 이해**
✅ **문자열 조작의 모든 기법 마스터**
✅ **숫자 연산과 원자적 증감 완전 활용**
✅ **부분 문자열 조작과 범위 연산 정복**
✅ **멀티 키 조작으로 성능 최적화**
✅ **실무에서 바로 활용 가능한 String 패턴 습득**

### 핵심 명령어 정리

#### 기본 조작 명령어
| 명령어 | 용도 | 예시 | 반환값 |
|--------|------|------|--------|
| `SET key value` | 값 설정 | `SET name "김철수"` | OK |
| `GET key` | 값 조회 | `GET name` | "김철수" 또는 nil |
| `GETSET key value` | 설정하면서 이전 값 반환 | `GETSET counter 100` | 이전 값 |
| `SETNX key value` | 키가 없을 때만 설정 | `SETNX lock "locked"` | 1 또는 0 |
| `SETEX key seconds value` | 만료시간과 함께 설정 | `SETEX session 1800 "data"` | OK |
| `PSETEX key milliseconds value` | 밀리초 만료시간 설정 | `PSETEX token 5000 "abc"` | OK |

#### 문자열 조작 명령어
| 명령어 | 용도 | 예시 | 반환값 |
|--------|------|------|--------|
| `APPEND key value` | 문자열 끝에 추가 | `APPEND log "new entry"` | 전체 길이 |
| `STRLEN key` | 문자열 길이 | `STRLEN message` | 바이트 수 |
| `GETRANGE key start end` | 부분 문자열 추출 | `GETRANGE text 0 4` | 부분 문자열 |
| `SETRANGE key offset value` | 부분 문자열 수정 | `SETRANGE text 5 "new"` | 전체 길이 |

#### 숫자 연산 명령어
| 명령어 | 용도 | 예시 | 반환값 |
|--------|------|------|--------|
| `INCR key` | 1 증가 | `INCR counter` | 증가 후 값 |
| `DECR key` | 1 감소 | `DECR counter` | 감소 후 값 |
| `INCRBY key increment` | 지정 값만큼 증가 | `INCRBY score 50` | 증가 후 값 |
| `DECRBY key decrement` | 지정 값만큼 감소 | `DECRBY score 25` | 감소 후 값 |
| `INCRBYFLOAT key increment` | 실수 증가 | `INCRBYFLOAT price 1.5` | 증가 후 값 |

#### 멀티 키 조작 명령어
| 명령어 | 용도 | 예시 | 반환값 |
|--------|------|------|--------|
| `MSET key1 value1 key2 value2 ...` | 여러 키 설정 | `MSET name "김철수" age 30` | OK |
| `MGET key1 key2 ...` | 여러 키 조회 | `MGET name age city` | 값들의 배열 |
| `MSETNX key1 value1 key2 value2 ...` | 모든 키가 없을 때만 설정 | `MSETNX a 1 b 2` | 1 또는 0 |

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] 카운터는 항상 INCR/DECR 사용 (원자성 보장)
- [ ] 만료시간이 필요한 데이터는 SETEX 또는 SET with EX 사용
- [ ] 여러 키 처리는 MGET/MSET으로 네트워크 왕복 최소화
- [ ] 계층적 키 명명 규칙 사용 (user:1001:profile:name)
- [ ] 적절한 TTL 설정으로 메모리 관리
- [ ] 대용량 데이터는 압축 또는 분할 저장

#### ❌ 하지 말아야 할 것
- [ ] GET + 계산 + SET 패턴 사용 금지 (동시성 문제)
- [ ] 캐시 데이터에 TTL 미설정 금지 (메모리 누수)
- [ ] 1MB 이상 데이터를 String에 저장 금지
- [ ] 한글 문자열에 GETRANGE 바이트 단위 주의
- [ ] 수천 개의 키를 MGET으로 한 번에 조회 금지

### 성능/보안 체크리스트

#### 성능
- [ ] MGET/MSET으로 네트워크 왕복 최소화
- [ ] INCR/DECR로 원자적 연산 활용
- [ ] 압축으로 메모리 사용량 감소
- [ ] 적절한 인코딩(int, embstr) 활용
- [ ] TTL 설정으로 불필요한 데이터 자동 삭제

#### 보안
- [ ] 민감 정보는 암호화 후 저장
- [ ] TTL 설정으로 데이터 자동 만료
- [ ] 접근 제어(ACL) 설정
- [ ] 로그에 민감 정보 노출 방지

---

## 🔗 관련 기술

**Redis String과 함께 사용하는 기술들**

| 기술 | 관계 | 학습 우선순위 | 설명 |
|------|------|---------------|------|
| Hash 타입 | 대안 | ⭐⭐⭐⭐⭐ | 여러 필드를 가진 객체 저장 시 String+JSON보다 효율적 |
| Sorted Set | 보완 | ⭐⭐⭐⭐☆ | 랭킹 시스템 구현 시 INCR과 함께 사용 |
| Pub/Sub | 연계 | ⭐⭐⭐☆☆ | 실시간 알림 발송 시 String 데이터와 함께 활용 |
| Lua Script | 고급 | ⭐⭐⭐⭐☆ | 복잡한 원자적 연산 구현 시 필수 |
| Redis Cluster | 확장 | ⭐⭐⭐☆☆ | 대용량 데이터 분산 저장 |
| RedisJSON | 대안 | ⭐⭐⭐☆☆ | JSON 내부 필드 효율적 조작 |

---

## 📚 추가 학습 자료

### 공식 문서
- [Redis String 명령어 레퍼런스](https://redis.io/commands/?group=string)
- [Redis String 데이터 타입 상세 가이드](https://redis.io/docs/data-types/strings/)
- [Redis 메모리 최적화 가이드](https://redis.io/docs/management/optimization/memory-optimization/)

### 추천 블로그/아티클
- [우아한형제들 기술블로그 - Redis 활용 사례](https://techblog.woowahan.com/)
- [NHN Cloud - Redis 성능 튜닝](https://meetup.nhncloud.com/posts/224)
- [카카오 기술블로그 - 대규모 서비스에서의 Redis 활용](https://tech.kakao.com/blog/)
- [Redis Labs - Understanding Redis String Internals](https://redis.com/blog/redis-strings/)

### 영상 강의
- [YouTube - Redis 완벽 가이드 (한글)](https://www.youtube.com/results?search_query=redis+tutorial+korean)
- [인프런 - Redis 실전 활용](https://www.inflearn.com/courses?s=redis)
- [Udemy - Redis: The Complete Developer's Guide](https://www.udemy.com/course/redis-the-complete-developers-guide/)

### 컨퍼런스 발표
- [Redis Conf 2024 - String Performance Optimization](https://redis.com/redisconf/)
- [DEVIEW 2023 - 대규모 트래픽 처리를 위한 Redis 활용](https://deview.kr/)

### 오픈소스 프로젝트
- [redis-py - Python Redis 클라이언트](https://github.com/redis/redis-py)
- [ioredis - Node.js Redis 클라이언트](https://github.com/redis/ioredis)
- [Jedis - Java Redis 클라이언트](https://github.com/redis/jedis)
- [go-redis - Go Redis 클라이언트](https://github.com/redis/go-redis)

### 실습 환경
- [Try Redis - 브라우저에서 바로 실습](https://try.redis.io/)
- [Redis Labs - 무료 클라우드 Redis](https://redis.com/try-free/)
- [Docker Hub - Redis 공식 이미지](https://hub.docker.com/_/redis)

---

## 🚀 다음 단계

**다음 장에서는 List 타입을 완전히 정복합니다!**

### 다음 장 미리보기: List 타입 완전 가이드
- **배울 내용 1**: 순서가 있는 컬렉션의 모든 것
- **배울 내용 2**: LPUSH, RPUSH, LPOP, RPOP로 큐/스택 구현
- **배울 내용 3**: LRANGE, LINDEX로 효율적인 데이터 조회
- **실전 프로젝트**: 실시간 알림 시스템, 최근 활동 목록

### 이 장과의 연결점
```
이번 장에서 배운 String 타입 (단일 값 저장)
    ↓
다음 장에서 List 타입 (순서 있는 다중 값 저장)
    ↓
최종적으로 복합 데이터 구조 완벽 이해
```

### 준비하면 좋을 것들
```bash
# 다음 장을 위한 환경 정리
127.0.0.1:6379> SELECT 1
OK

127.0.0.1:6379[1]> FLUSHDB
OK

127.0.0.1:6379[1]> SELECT 0
OK
```

---

## 🎉 축하합니다!

Redis String 타입을 완전히 마스터했습니다!

**이제 여러분은**:
✅ String 타입의 모든 명령어를 완벽히 활용할 수 있습니다
✅ 문자열 조작의 고급 기법을 습득했습니다
✅ 원자적 숫자 연산으로 동시성 문제를 해결할 수 있습니다
✅ 멀티 키 조작으로 성능을 최적화할 수 있습니다
✅ 실무 프로젝트를 설계하고 구현할 수 있습니다
✅ 베스트 프랙티스와 최적화 전략을 이해했습니다
✅ 면접에서 자신 있게 답변할 수 있습니다

**다음 단계**:
- [ ] 다음 장으로 진행하여 List 타입 학습
- [ ] 실전 프로젝트로 복습 및 응용
- [ ] 면접 질문 리스트로 지식 점검
- [ ] 실무에서 String 타입 활용해보기

이제 Redis의 첫 번째 데이터 타입을 완전히 정복했습니다. 다음 장에서 더욱 강력한 List 타입을 마스터해보겠습니다! 🚀

---

**다음 장으로 이동**: [5. List 타입 완전 가이드](./05-List-타입-완전-가이드.md)

**이전 장으로 돌아가기**: [3. Redis 기본 조작 마스터하기](./03-Redis-기본-조작-마스터하기.md)

**목차로 돌아가기**: [Redis 완전 학습 가이드](./redis%20가이드.md)
