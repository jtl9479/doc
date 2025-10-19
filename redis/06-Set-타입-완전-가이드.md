# 🎯 6. Set 타입 완전 가이드

> **이 장에서 배울 내용**: Redis Set 타입의 모든 기능을 완벽하게 마스터하여 집합 연산, 태그 시스템, 추천 알고리즘을 자유자재로 구현합니다.

**⏱️ 예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐☆☆ (3/5)

---

## 📚 목차
- [학습 목표](#학습-목표)
- [왜 Set 타입이 필요한가](#왜-set-타입이-필요한가)
- [실생활 비유로 이해하기](#실생활-비유로-이해하기)
- [Set 타입 완전 이해](#set-타입-완전-이해)
- [Set 조작 기본 명령어](#set-조작-기본-명령어)
- [집합 연산](#집합-연산)
- [Set 크기와 멤버십 테스트](#set-크기와-멤버십-테스트)
- [실전 종합 프로젝트](#실전-종합-프로젝트)
- [주니어 시나리오](#주니어-시나리오)
- [핵심 내용 정리 및 베스트 프랙티스](#핵심-내용-정리-및-베스트-프랙티스)
- [면접 질문 리스트](#면접-질문-리스트)
- [FAQ](#faq)
- [다음 단계](#다음-단계)

---

## 📚 학습 목표

이 장을 완료하면 다음과 같은 능력을 갖게 됩니다:

✅ **Set 타입의 내부 구조와 특성 완벽 이해**
✅ **집합 연산(교집합, 합집합, 차집합) 완전 마스터**
✅ **멤버십 테스트와 빠른 검색 능력 정복**
✅ **Set 조작의 모든 방법과 최적화 기법 습득**
✅ **태그 시스템과 추천 알고리즘 구현 능력**
✅ **실무에서 바로 활용 가능한 Set 패턴 완전 정복**

---

## 🤔 왜 Set 타입이 필요한가?

### 실무 배경

현대 웹 애플리케이션에서는 "중복 없는 데이터"와 "집합 연산"이 필수입니다. 사용자 태그, 권한 관리, 추천 시스템 등에서 Set은 핵심 역할을 합니다.

#### ❌ Set을 모르면 발생하는 문제

**문제 1: 중복 데이터 처리의 비효율**
- 증상: 리스트에 중복 데이터가 계속 쌓임
- 영향: 메모리 낭비, 검색 속도 저하 (O(N) 시간복잡도)
- 비용: 100만 개 데이터에서 검색 시 평균 500ms → 사용자 이탈률 증가

**문제 2: 복잡한 집합 연산의 어려움**
- 증상: 애플리케이션 레벨에서 교집합/합집합 구현
- 영향: 코드 복잡도 증가, 버그 발생 가능성
- 비용: 개발 시간 2-3배 증가, 유지보수 어려움

**문제 3: 실시간 추천 시스템 구현 불가**
- 증상: 데이터베이스 조인 쿼리로 인한 성능 저하
- 영향: 추천 응답 시간 5초 이상 → 사용자 경험 악화
- 비용: 서버 비용 3배 증가

#### ✅ Set을 사용하면

**해결책 1: O(1) 시간복잡도로 즉시 검색**
- 방법: SISMEMBER로 멤버십 테스트
- 효과: 100만 개 데이터에서도 1ms 이내 검색
- 절감: 응답 시간 **99.8% 감소**

**해결책 2: 내장 집합 연산으로 간단한 구현**
- 방법: SINTER, SUNION, SDIFF 명령어 활용
- 효과: 복잡한 비즈니스 로직을 한 줄로 구현
- 절감: 개발 시간 **70% 단축**

**해결책 3: 실시간 추천 시스템 구현**
- 방법: Set 연산으로 공통 관심사 즉시 계산
- 효과: 추천 응답 시간 5초 → 50ms
- 절감: 서버 비용 **60% 절감**, 사용자 만족도 **40% 향상**

### 📊 수치로 보는 효과

| 지표 | Before (List/DB) | After (Set) | 개선율 |
|------|------------------|-------------|--------|
| 중복 체크 시간 | 500ms (O(N)) | 1ms (O(1)) | **99.8%↓** |
| 메모리 사용량 | 100MB (중복 포함) | 60MB (중복 제거) | **40%↓** |
| 추천 응답 시간 | 5,000ms | 50ms | **99%↓** |
| 코드 복잡도 | 200줄 | 10줄 | **95%↓** |
| 개발 시간 | 3일 | 1일 | **67%↓** |
| 서버 비용 | $1,000/월 | $400/월 | **60%↓** |

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 학교 동아리 명단 📋

```
Redis Set = 동아리 회원 명단

특징:
- 같은 학생이 두 번 등록될 수 없음 (중복 불허)
- 회원 순서는 중요하지 않음 (순서 없음)
- "김철수가 회원인가?" 즉시 확인 가능 (빠른 검색)

집합 연산:
- 교집합(SINTER) = 축구부와 농구부 모두 속한 학생
- 합집합(SUNION) = 축구부 또는 농구부 회원 전체
- 차집합(SDIFF) = 축구부엔 있지만 농구부엔 없는 학생

┌────────────────────────────────────┐
│   축구부    │    농구부            │
│  김철수     │   김철수 (교집합!)   │
│  이영희     │   박민수            │
│  정수진     │   최지훈            │
└────────────────────────────────────┘

SADD soccer:club "김철수" "이영희" "정수진"
SADD basketball:club "김철수" "박민수" "최지훈"
SINTER soccer:club basketball:club  # ["김철수"]
```

### 비유 2: 영화 스트리밍 서비스 태그 🎬

```
Redis Set = Netflix의 영화 태그 시스템

각 영화의 장르, 배우, 분위기를 Set으로 관리:

영화 "기생충":
- 장르: {스릴러, 드라마, 코미디}
- 주연: {송강호, 이선균, 조여정}
- 분위기: {긴장감, 반전, 사회비판}

사용자 취향 분석:
- 사용자가 좋아한 영화들의 태그 합집합
- 비슷한 태그를 가진 영화 추천 (교집합)
- 이미 본 영화 제외 (차집합)

실제 구현:
SADD movie:parasite:genres "thriller" "drama" "comedy"
SADD user:1001:favorite_genres "thriller" "action" "sci-fi"
SINTER movie:parasite:genres user:1001:favorite_genres
# ["thriller"] → 추천 가능!
```

### 비유 3: 배달 앱의 가게 필터링 🍔

```
Redis Set = 배달의민족 가게 필터 시스템

필터 옵션:
- 배달 가능한 가게: {가게A, 가게B, 가게C, 가게D}
- 한식 카테고리: {가게B, 가게C, 가게E}
- 할인 중인 가게: {가게A, 가게C, 가게F}
- 리뷰 4.5점 이상: {가게B, 가게C, 가게D}

사용자가 "배달 가능 + 한식 + 할인"을 선택하면:
교집합 = {가게C}  # 모든 조건 만족!

┌─────────────────────────────────────────┐
│  배달가능 ∩ 한식 ∩ 할인 = {가게C}        │
│                                          │
│  조건을 완화하려면:                      │
│  배달가능 ∩ (한식 ∪ 할인) = 더 많은 결과 │
└─────────────────────────────────────────┘

실제 Redis 명령어:
SINTER deliverable korean_food on_sale
```

### 비유 4: 카카오톡 그룹채팅 공통 친구 찾기 💬

```
Redis Set = 카카오톡 친구 목록

철수의 친구: {영희, 민수, 지훈, 수진, 하나}
영희의 친구: {철수, 민수, 수진, 정우, 미영}

공통 친구 찾기 (교집합):
SINTER user:chulsu:friends user:younghee:friends
→ {민수, 수진}

친구 추천 로직:
1. 영희의 친구들 (SMEMBERS user:younghee:friends)
2. 철수가 아직 친구 아닌 사람 (SDIFF)
→ {정우, 미영}을 철수에게 추천

단체방 만들 때 (합집합):
SUNION user:chulsu:friends user:younghee:friends
→ 전체 7명
```

### 비유 5: 대학교 수강신청 시스템 📚

```
Redis Set = 수강신청 과목 및 학생 관리

컴퓨터공학과 필수과목: {자료구조, 알고리즘, 운영체제, 데이터베이스}
전기공학과 필수과목: {회로이론, 신호처리, 전자기학, 제어공학}

복수전공생이 들어야 할 과목:
SUNION cs:required ee:required  # 합집합 (모두 들어야 함)

이미 수강한 과목:
학생A 수강완료: {자료구조, 알고리즘, 회로이론}

남은 과목 계산:
SDIFF cs:required student:A:completed
→ {운영체제, 데이터베이스}  # 아직 들어야 할 과목

┌──────────────────────────────────────┐
│  과목 관리                            │
│  - 전체 과목 목록 (SUNION)           │
│  - 수강 가능 과목 (SDIFF)            │
│  - 동시 수강 가능 (교집합 없음 체크) │
└──────────────────────────────────────┘
```

### 🎯 종합 비교표

| 기술 개념 | 동아리 명단 | Netflix 태그 | 배달앱 필터 | 카톡 친구 | 수강신청 |
|-----------|-------------|--------------|-------------|-----------|----------|
| **SADD** | 회원 등록 | 태그 추가 | 가게 분류 | 친구 추가 | 과목 등록 |
| **SREM** | 회원 탈퇴 | 태그 제거 | 가게 제외 | 친구 삭제 | 수강 취소 |
| **SISMEMBER** | 회원 확인 | 태그 검색 | 필터 확인 | 친구 여부 | 수강 여부 |
| **SINTER** | 겹치는 회원 | 공통 태그 | 모든 조건 | 공통 친구 | 공통 과목 |
| **SUNION** | 전체 회원 | 모든 태그 | 조건 완화 | 친구 통합 | 전체 과목 |
| **SDIFF** | 한쪽만 회원 | 차별 태그 | 제외 조건 | 친구 추천 | 남은 과목 |

---

## 🧬 1. Set 타입 완전 이해

### 1.1 Redis Set이란 무엇인가?

**Redis Set은 중복되지 않는 문자열들의 순서 없는 컬렉션입니다.**

```
🎲 주사위 게임 비유:
- Set = 주사위 눈의 집합 {1, 2, 3, 4, 5, 6}
- Element = 각 숫자
- 특징: 중복 없음, 순서 없음, 빠른 검색

카드 게임의 덱처럼 같은 카드가 두 번 나올 수 없습니다.
```

### 1.2 Set의 핵심 특징

#### 1) 중복 불허 (No Duplicates)
```bash
# 같은 값을 여러 번 추가해도 하나만 저장됨
127.0.0.1:6379> SADD colors "빨강"
(integer) 1

127.0.0.1:6379> SADD colors "파랑"
(integer) 1

127.0.0.1:6379> SADD colors "빨강"
(integer) 0   # 이미 존재하므로 추가되지 않음

127.0.0.1:6379> SMEMBERS colors
1) "빨강"   # 하나만 존재
2) "파랑"
```

#### 2) 순서 없음 (Unordered)
```bash
# 삽입 순서와 조회 순서가 다를 수 있음
127.0.0.1:6379> SADD fruits "사과" "바나나" "오렌지"
(integer) 3

127.0.0.1:6379> SMEMBERS fruits
1) "오렌지"   # 삽입 순서와 다름
2) "바나나"
3) "사과"

# 순서에 의존하지 말고 존재 여부만 확인
127.0.0.1:6379> SISMEMBER fruits "사과"
(integer) 1   # 존재함
```

#### 3) 빠른 멤버십 테스트 (Fast Membership Test)
```bash
# O(1) 시간복잡도로 매우 빠른 검색
127.0.0.1:6379> SADD large_set $(printf 'item%d ' {1..100000})
(integer) 100000

127.0.0.1:6379> SISMEMBER large_set "item50000"
(integer) 1   # 10만 개 중에서도 즉시 찾음

127.0.0.1:6379> SISMEMBER large_set "nonexistent"
(integer) 0   # 즉시 없음을 확인
```

### 1.3 Set의 내부 구조와 성능

#### 내부 인코딩 방식
```bash
# Redis는 Set 크기와 데이터에 따라 다른 인코딩 사용:
# 1. intset: 정수만 포함하고 512개 이하인 경우
# 2. hashtable: 일반적인 경우

# 정수 Set (intset 인코딩)
127.0.0.1:6379> SADD numbers 1 2 3 4 5
(integer) 5

127.0.0.1:6379> OBJECT ENCODING numbers
"intset"

# 문자열 Set (hashtable 인코딩)
127.0.0.1:6379> SADD strings "a" "b" "c"
(integer) 3

127.0.0.1:6379> OBJECT ENCODING strings
"hashtable"

# 혼합 Set (hashtable 인코딩)
127.0.0.1:6379> SADD mixed 1 "a" 2 "b"
(integer) 4

127.0.0.1:6379> OBJECT ENCODING mixed
"hashtable"
```

#### 시간 복잡도
```bash
# O(1) 연산: 매우 빠름
SADD, SREM, SISMEMBER, SCARD

# O(N) 연산: Set 크기에 비례
SMEMBERS, SINTER, SUNION, SDIFF

# 실무 팁: 큰 Set의 경우 SMEMBERS 대신 SSCAN 사용 권장
```

---

## ➕ 2. Set 조작 기본 명령어 (SADD, SREM, SMEMBERS)

### 2.1 SADD - Set에 원소 추가

#### 기본 사용법
```bash
# 새 Set 생성하면서 원소 추가
127.0.0.1:6379> SADD programming_languages "Python"
(integer) 1

# 기존 Set에 원소 추가
127.0.0.1:6379> SADD programming_languages "JavaScript"
(integer) 1

127.0.0.1:6379> SADD programming_languages "Java"
(integer) 1

# 현재 Set 확인
127.0.0.1:6379> SMEMBERS programming_languages
1) "Python"
2) "JavaScript"
3) "Java"
```

#### 여러 원소 동시 추가
```bash
# 한 번에 여러 원소 추가
127.0.0.1:6379> SADD web_technologies "HTML" "CSS" "JavaScript" "React" "Vue" "Angular"
(integer) 6

127.0.0.1:6379> SMEMBERS web_technologies
1) "HTML"
2) "CSS"
3) "JavaScript"
4) "React"
5) "Vue"
6) "Angular"
```

#### 중복 추가 시 동작
```bash
# 이미 존재하는 원소 추가 시도
127.0.0.1:6379> SADD programming_languages "Python" "Go" "Rust"
(integer) 2   # Python은 이미 존재, Go와 Rust만 추가됨

127.0.0.1:6379> SMEMBERS programming_languages
1) "Python"   # 중복되지 않음
2) "JavaScript"
3) "Java"
4) "Go"       # 새로 추가됨
5) "Rust"     # 새로 추가됨
```

### 2.2 SREM - Set에서 원소 제거

#### 기본 제거
```bash
# 단일 원소 제거
127.0.0.1:6379> SREM programming_languages "Java"
(integer) 1   # 제거된 원소 개수

127.0.0.1:6379> SMEMBERS programming_languages
1) "Python"
2) "JavaScript"
3) "Go"
4) "Rust"
```

#### 여러 원소 동시 제거
```bash
# 여러 원소 한 번에 제거
127.0.0.1:6379> SREM programming_languages "Go" "Rust" "Nonexistent"
(integer) 2   # Go와 Rust만 제거됨 (Nonexistent는 없으므로 0)

127.0.0.1:6379> SMEMBERS programming_languages
1) "Python"
2) "JavaScript"
```

#### 존재하지 않는 원소 제거 시도
```bash
127.0.0.1:6379> SREM programming_languages "C++"
(integer) 0   # 존재하지 않으므로 제거되지 않음

127.0.0.1:6379> SREM nonexistent_set "anything"
(integer) 0   # Set 자체가 존재하지 않아도 에러 없이 0 반환
```

### 2.3 SMEMBERS - Set의 모든 원소 조회

```bash
# 전체 원소 조회
127.0.0.1:6379> SMEMBERS programming_languages
1) "Python"
2) "JavaScript"

# 빈 Set 조회
127.0.0.1:6379> SMEMBERS empty_set
(empty array)

# 존재하지 않는 Set 조회
127.0.0.1:6379> SMEMBERS nonexistent_set
(empty array)
```

#### SMEMBERS 사용 시 주의사항
```bash
# 큰 Set의 경우 성능 문제 발생 가능
127.0.0.1:6379> SADD big_set $(printf 'user%d ' {1..100000})
(integer) 100000

# 위험: 10만 개 원소를 모두 반환 (메모리 및 네트워크 부하)
# SMEMBERS big_set  # 운영환경에서는 사용 금지

# 대안: SSCAN 사용 (나중에 학습)
127.0.0.1:6379> SSCAN big_set 0 COUNT 10
1) "98304"   # 다음 커서
2)  1) "user12345"
    2) "user67890"
    3) "user54321"
    ... (10개 원소)
```

### 2.4 SCARD - Set 크기 확인

```bash
# Set의 원소 개수 확인
127.0.0.1:6379> SCARD programming_languages
(integer) 2

127.0.0.1:6379> SCARD web_technologies
(integer) 6

# 빈 Set 또는 존재하지 않는 Set
127.0.0.1:6379> SCARD empty_set
(integer) 0

127.0.0.1:6379> SCARD nonexistent_set
(integer) 0
```

### 2.5 실무 활용 패턴

#### 1) 사용자 권한 관리
```bash
# 사용자별 권한 Set
127.0.0.1:6379> SADD user:1001:permissions "read" "write" "delete"
(integer) 3

127.0.0.1:6379> SADD user:1002:permissions "read" "write"
(integer) 2

# 권한 확인
127.0.0.1:6379> SISMEMBER user:1001:permissions "delete"
(integer) 1   # 삭제 권한 있음

127.0.0.1:6379> SISMEMBER user:1002:permissions "delete"
(integer) 0   # 삭제 권한 없음

# 권한 추가
127.0.0.1:6379> SADD user:1002:permissions "admin"
(integer) 1

# 권한 제거
127.0.0.1:6379> SREM user:1001:permissions "delete"
(integer) 1
```

#### 2) 태그 시스템
```bash
# 게시글별 태그
127.0.0.1:6379> SADD post:1001:tags "기술" "프로그래밍" "Redis" "데이터베이스"
(integer) 4

127.0.0.1:6379> SADD post:1002:tags "여행" "일본" "도쿄" "맛집"
(integer) 4

127.0.0.1:6379> SADD post:1003:tags "기술" "AI" "머신러닝" "Python"
(integer) 4

# 특정 태그를 가진 게시글인지 확인
127.0.0.1:6379> SISMEMBER post:1001:tags "Redis"
(integer) 1   # Redis 태그 있음

# 게시글의 모든 태그 조회
127.0.0.1:6379> SMEMBERS post:1001:tags
1) "기술"
2) "프로그래밍"
3) "Redis"
4) "데이터베이스"
```

#### 3) 온라인 사용자 추적
```bash
# 현재 온라인 사용자 Set
127.0.0.1:6379> SADD online_users "user1001" "user1002" "user1003"
(integer) 3

# 사용자 로그인 시 추가
127.0.0.1:6379> SADD online_users "user1004"
(integer) 1

# 사용자 로그아웃 시 제거
127.0.0.1:6379> SREM online_users "user1002"
(integer) 1

# 현재 온라인 사용자 수
127.0.0.1:6379> SCARD online_users
(integer) 3

# 특정 사용자가 온라인인지 확인
127.0.0.1:6379> SISMEMBER online_users "user1001"
(integer) 1   # 온라인
```

#### 4) 좋아요/관심 목록
```bash
# 사용자가 좋아요한 게시글
127.0.0.1:6379> SADD user:1001:liked_posts "post123" "post456" "post789"
(integer) 3

# 게시글을 좋아요한 사용자들
127.0.0.1:6379> SADD post:123:likers "user1001" "user1002" "user1003"
(integer) 3

# 좋아요 추가
127.0.0.1:6379> SADD user:1001:liked_posts "post999"
(integer) 1

127.0.0.1:6379> SADD post:999:likers "user1001"
(integer) 1

# 좋아요 취소
127.0.0.1:6379> SREM user:1001:liked_posts "post456"
(integer) 1

127.0.0.1:6379> SREM post:456:likers "user1001"
(integer) 1

# 특정 게시글을 좋아요했는지 확인
127.0.0.1:6379> SISMEMBER user:1001:liked_posts "post123"
(integer) 1   # 좋아요함

# 게시글의 좋아요 수
127.0.0.1:6379> SCARD post:123:likers
(integer) 3
```

---

## 🔍 3. 집합 연산 (SINTER, SUNION, SDIFF)

### 3.1 SINTER - 교집합 (Intersection)

#### 기본 교집합 연산
```bash
# 테스트 데이터 준비
127.0.0.1:6379> SADD frontend_skills "HTML" "CSS" "JavaScript" "React" "Vue"
(integer) 5

127.0.0.1:6379> SADD backend_skills "JavaScript" "Python" "Java" "Node.js" "Django"
(integer) 5

127.0.0.1:6379> SADD fullstack_skills "HTML" "CSS" "JavaScript" "Python" "React" "Node.js"
(integer) 6

# 두 Set의 교집합
127.0.0.1:6379> SINTER frontend_skills backend_skills
1) "JavaScript"   # 공통 스킬

# 세 Set의 교집합
127.0.0.1:6379> SINTER frontend_skills backend_skills fullstack_skills
1) "JavaScript"   # 모든 Set에 공통인 스킬
```

#### 여러 Set 교집합
```bash
# 더 많은 Set으로 테스트
127.0.0.1:6379> SADD mobile_skills "JavaScript" "React" "Swift" "Kotlin"
(integer) 4

127.0.0.1:6379> SADD cloud_skills "JavaScript" "Python" "Docker" "AWS"
(integer) 4

# 5개 Set의 교집합
127.0.0.1:6379> SINTER frontend_skills backend_skills fullstack_skills mobile_skills cloud_skills
1) "JavaScript"   # 모든 분야에 공통인 스킬
```

#### 교집합이 없는 경우
```bash
127.0.0.1:6379> SADD design_skills "Photoshop" "Illustrator" "Figma"
(integer) 3

127.0.0.1:6379> SINTER frontend_skills design_skills
(empty array)   # 공통 원소 없음
```

### 3.2 SINTERSTORE - 교집합 결과 저장

```bash
# 교집합 결과를 새로운 Set에 저장
127.0.0.1:6379> SINTERSTORE common_skills frontend_skills backend_skills
(integer) 1   # 저장된 원소 개수

127.0.0.1:6379> SMEMBERS common_skills
1) "JavaScript"

# 기존 Set이 있으면 덮어씀
127.0.0.1:6379> SADD temp_set "old_data"
(integer) 1

127.0.0.1:6379> SINTERSTORE temp_set frontend_skills fullstack_skills
(integer) 4   # HTML, CSS, JavaScript, React

127.0.0.1:6379> SMEMBERS temp_set
1) "HTML"
2) "CSS"
3) "JavaScript"
4) "React"
```

### 3.3 SUNION - 합집합 (Union)

#### 기본 합집합 연산
```bash
# 두 Set의 합집합
127.0.0.1:6379> SUNION frontend_skills backend_skills
1) "HTML"
2) "CSS"
3) "JavaScript"   # 중복 제거됨
4) "React"
5) "Vue"
6) "Python"
7) "Java"
8) "Node.js"
9) "Django"

# 세 Set의 합집합
127.0.0.1:6379> SUNION frontend_skills backend_skills design_skills
 1) "HTML"
 2) "CSS"
 3) "JavaScript"
 4) "React"
 5) "Vue"
 6) "Python"
 7) "Java"
 8) "Node.js"
 9) "Django"
10) "Photoshop"
11) "Illustrator"
12) "Figma"
```

### 3.4 SUNIONSTORE - 합집합 결과 저장

```bash
# 합집합 결과를 새로운 Set에 저장
127.0.0.1:6379> SUNIONSTORE all_skills frontend_skills backend_skills design_skills
(integer) 12   # 저장된 원소 개수

127.0.0.1:6379> SCARD all_skills
(integer) 12

# 저장된 결과 확인
127.0.0.1:6379> SISMEMBER all_skills "Photoshop"
(integer) 1   # 포함됨

127.0.0.1:6379> SISMEMBER all_skills "JavaScript"
(integer) 1   # 포함됨
```

### 3.5 SDIFF - 차집합 (Difference)

#### 기본 차집합 연산
```bash
# A - B: A에는 있지만 B에는 없는 원소들
127.0.0.1:6379> SDIFF frontend_skills backend_skills
1) "HTML"     # frontend_skills에만 있음
2) "CSS"      # frontend_skills에만 있음
3) "React"    # frontend_skills에만 있음
4) "Vue"      # frontend_skills에만 있음

# B - A: B에는 있지만 A에는 없는 원소들
127.0.0.1:6379> SDIFF backend_skills frontend_skills
1) "Python"   # backend_skills에만 있음
2) "Java"     # backend_skills에만 있음
3) "Node.js"  # backend_skills에만 있음
4) "Django"   # backend_skills에만 있음
```

#### 여러 Set 차집합
```bash
# A - B - C: A에는 있지만 B와 C에는 없는 원소들
127.0.0.1:6379> SDIFF fullstack_skills frontend_skills backend_skills
1) "Python"   # fullstack_skills에만 있고 나머지에는 없음

# 순서가 중요함: 첫 번째 Set에서 나머지 모든 Set을 빼기
127.0.0.1:6379> SDIFF fullstack_skills backend_skills frontend_skills
1) "HTML"     # 결과가 다름
2) "CSS"
```

### 3.6 SDIFFSTORE - 차집합 결과 저장

```bash
# 차집합 결과를 새로운 Set에 저장
127.0.0.1:6379> SDIFFSTORE frontend_only frontend_skills backend_skills
(integer) 4   # HTML, CSS, React, Vue

127.0.0.1:6379> SMEMBERS frontend_only
1) "HTML"
2) "CSS"
3) "React"
4) "Vue"

127.0.0.1:6379> SDIFFSTORE backend_only backend_skills frontend_skills
(integer) 4   # Python, Java, Node.js, Django

127.0.0.1:6379> SMEMBERS backend_only
1) "Python"
2) "Java"
3) "Node.js"
4) "Django"
```

### 3.7 집합 연산 실무 활용 패턴

#### 1) 사용자 추천 시스템
```bash
# 사용자별 관심 분야
127.0.0.1:6379> SADD user:1001:interests "기술" "프로그래밍" "AI" "게임"
(integer) 4

127.0.0.1:6379> SADD user:1002:interests "기술" "프로그래밍" "여행" "요리"
(integer) 4

127.0.0.1:6379> SADD user:1003:interests "AI" "게임" "영화" "음악"
(integer) 4

# 공통 관심사 찾기 (친구 추천용)
127.0.0.1:6379> SINTER user:1001:interests user:1002:interests
1) "기술"
2) "프로그래밍"   # 공통 관심사

127.0.0.1:6379> SINTER user:1001:interests user:1003:interests
1) "AI"
2) "게임"        # 공통 관심사

# 사용자가 관심 없어하는 분야 찾기 (새로운 추천용)
127.0.0.1:6379> SADD all_categories "기술" "프로그래밍" "AI" "게임" "여행" "요리" "영화" "음악" "스포츠" "독서"
(integer) 10

127.0.0.1:6379> SDIFF all_categories user:1001:interests
1) "여행"
2) "요리"
3) "영화"
4) "음악"
5) "스포츠"
6) "독서"        # user:1001이 아직 관심 없는 분야들
```

#### 2) 권한 관리 시스템
```bash
# 역할별 권한 정의
127.0.0.1:6379> SADD role:admin "user_read" "user_write" "user_delete" "system_config" "backup"
(integer) 5

127.0.0.1:6379> SADD role:manager "user_read" "user_write" "report_read" "report_write"
(integer) 4

127.0.0.1:6379> SADD role:user "user_read" "profile_write"
(integer) 2

# 사용자에게 여러 역할 부여
127.0.0.1:6379> SADD user:1001:roles "admin" "manager"
(integer) 2

# 사용자의 실제 권한 계산 (모든 역할의 합집합)
127.0.0.1:6379> SUNIONSTORE user:1001:permissions role:admin role:manager
(integer) 6

127.0.0.1:6379> SMEMBERS user:1001:permissions
1) "user_read"
2) "user_write"
3) "user_delete"
4) "system_config"
5) "backup"
6) "report_read"
7) "report_write"

# 특정 권한 확인
127.0.0.1:6379> SISMEMBER user:1001:permissions "system_config"
(integer) 1   # 권한 있음
```

#### 3) 상품 필터링 시스템
```bash
# 상품별 속성
127.0.0.1:6379> SADD product:1001:attributes "전자제품" "노트북" "게이밍" "고성능" "15인치"
(integer) 5

127.0.0.1:6379> SADD product:1002:attributes "전자제품" "노트북" "사무용" "경량" "13인치"
(integer) 5

127.0.0.1:6379> SADD product:1003:attributes "전자제품" "데스크탑" "게이밍" "고성능" "RGB"
(integer) 5

# 사용자 검색 조건
127.0.0.1:6379> SADD search_filter "전자제품" "노트북" "게이밍"
(integer) 3

# 조건에 맞는 상품 찾기 (교집합 활용)
127.0.0.1:6379> SINTER product:1001:attributes search_filter
1) "전자제품"
2) "노트북"
3) "게이밍"      # 모든 조건 만족

127.0.0.1:6379> SINTER product:1002:attributes search_filter
1) "전자제품"
2) "노트북"      # 부분 만족 (게이밍 조건 불만족)

127.0.0.1:6379> SINTER product:1003:attributes search_filter
1) "전자제품"
2) "게이밍"      # 부분 만족 (노트북 조건 불만족)

# 정확히 일치하는 상품만 찾기
# SCARD(교집합) == SCARD(검색조건) 인 상품 필터링
```

#### 4) 소셜 네트워크 분석
```bash
# 사용자별 팔로워
127.0.0.1:6379> SADD user:alice:followers "bob" "charlie" "david" "eve"
(integer) 4

127.0.0.1:6379> SADD user:bob:followers "alice" "charlie" "frank" "grace"
(integer) 4

127.0.0.1:6379> SADD user:charlie:followers "alice" "bob" "david" "frank"
(integer) 4

# 공통 팔로워 찾기 (상호 친구)
127.0.0.1:6379> SINTER user:alice:followers user:bob:followers
1) "charlie"     # alice와 bob의 공통 팔로워

# 추천 친구 찾기 (alice의 친구들의 친구 중 alice가 팔로우하지 않는 사람)
127.0.0.1:6379> SUNIONSTORE alice_friends_friends user:bob:followers user:charlie:followers user:david:followers
(integer) 6

127.0.0.1:6379> SDIFFSTORE potential_friends alice_friends_friends user:alice:followers
(integer) 3

127.0.0.1:6379> SREM potential_friends "alice"  # 자기 자신 제거
(integer) 1

127.0.0.1:6379> SMEMBERS potential_friends
1) "frank"
2) "grace"       # alice에게 추천할 친구들
```

---

## 🔄 4. Set 크기와 멤버십 테스트

### 4.1 SISMEMBER - 원소 존재 확인

#### 기본 멤버십 테스트
```bash
# 테스트 데이터 준비
127.0.0.1:6379> SADD supported_languages "ko" "en" "ja" "zh" "es" "fr" "de"
(integer) 7

# 지원 언어 확인
127.0.0.1:6379> SISMEMBER supported_languages "ko"
(integer) 1   # 한국어 지원

127.0.0.1:6379> SISMEMBER supported_languages "ru"
(integer) 0   # 러시아어 미지원

127.0.0.1:6379> SISMEMBER supported_languages "en"
(integer) 1   # 영어 지원
```

#### 대소문자 구분
```bash
127.0.0.1:6379> SADD case_sensitive "Apple" "apple" "APPLE"
(integer) 3

127.0.0.1:6379> SISMEMBER case_sensitive "Apple"
(integer) 1   # 정확히 일치

127.0.0.1:6379> SISMEMBER case_sensitive "apple"
(integer) 1   # 정확히 일치

127.0.0.1:6379> SISMEMBER case_sensitive "APPLE"
(integer) 1   # 정확히 일치

127.0.0.1:6379> SISMEMBER case_sensitive "aPpLe"
(integer) 0   # 일치하지 않음
```

### 4.2 SMISMEMBER - 여러 원소 존재 확인 (Redis 6.2+)

```bash
# 여러 원소를 한 번에 확인
127.0.0.1:6379> SMISMEMBER supported_languages "ko" "en" "ru" "ja" "ar"
1) (integer) 1   # ko: 존재
2) (integer) 1   # en: 존재
3) (integer) 0   # ru: 없음
4) (integer) 1   # ja: 존재
5) (integer) 0   # ar: 없음

# 결과는 요청한 순서대로 반환됨
```

### 4.3 SCARD - Set 크기 확인

```bash
# Set 크기 확인
127.0.0.1:6379> SCARD supported_languages
(integer) 7

# 빈 Set 크기
127.0.0.1:6379> SCARD empty_set
(integer) 0

# 존재하지 않는 Set 크기
127.0.0.1:6379> SCARD nonexistent_set
(integer) 0
```

### 4.4 SPOP - 임의 원소 제거

#### 기본 사용법
```bash
# 테스트 데이터 준비
127.0.0.1:6379> SADD lottery_numbers "1" "7" "13" "21" "35" "42"
(integer) 6

# 임의의 원소 하나 제거하며 반환
127.0.0.1:6379> SPOP lottery_numbers
"21"   # 임의의 숫자 (매번 다를 수 있음)

127.0.0.1:6379> SPOP lottery_numbers
"7"    # 또 다른 임의의 숫자

127.0.0.1:6379> SMEMBERS lottery_numbers
1) "1"
2) "13"
3) "35"
4) "42"   # 21과 7이 제거됨
```

#### 여러 원소 동시 제거 (Redis 3.2+)
```bash
# 여러 개 임의 원소 제거
127.0.0.1:6379> SPOP lottery_numbers 2
1) "35"
2) "1"    # 임의의 2개 원소 제거

127.0.0.1:6379> SMEMBERS lottery_numbers
1) "13"
2) "42"   # 남은 원소들
```

#### 빈 Set에서 SPOP
```bash
127.0.0.1:6379> SPOP empty_set
(nil)

127.0.0.1:6379> SPOP empty_set 5
(empty array)
```

### 4.5 SRANDMEMBER - 임의 원소 조회 (제거하지 않음)

#### 기본 사용법
```bash
# 테스트 데이터 준비
127.0.0.1:6379> SADD colors "빨강" "주황" "노랑" "초록" "파랑" "남색" "보라"
(integer) 7

# 임의의 원소 하나 조회 (제거하지 않음)
127.0.0.1:6379> SRANDMEMBER colors
"초록"   # 임의의 색상

127.0.0.1:6379> SRANDMEMBER colors
"파랑"   # 또 다른 임의의 색상

127.0.0.1:6379> SCARD colors
(integer) 7   # 크기는 변하지 않음
```

#### 여러 원소 조회
```bash
# 중복 없이 여러 원소 조회
127.0.0.1:6379> SRANDMEMBER colors 3
1) "보라"
2) "빨강"
3) "노랑"   # 중복 없는 3개

# 중복 허용하며 여러 원소 조회 (음수 사용)
127.0.0.1:6379> SRANDMEMBER colors -5
1) "파랑"
2) "초록"
3) "초록"   # 중복 가능
4) "빨강"
5) "보라"
```

### 4.6 실무 활용 패턴

#### 1) 추첨 시스템
```bash
# 참가자 등록
127.0.0.1:6379> SADD event_participants "user1001" "user1002" "user1003" "user1004" "user1005"
(integer) 5

# 1등 당첨자 뽑기 (제거)
127.0.0.1:6379> SPOP event_participants
"user1003"   # 1등 당첨자

# 2등, 3등 당첨자 뽑기
127.0.0.1:6379> SPOP event_participants 2
1) "user1001"  # 2등
2) "user1005"  # 3등

# 남은 참가자 확인
127.0.0.1:6379> SMEMBERS event_participants
1) "user1002"
2) "user1004"  # 미당첨자들
```

#### 2) 랜덤 콘텐츠 추천
```bash
# 추천 가능한 콘텐츠
127.0.0.1:6379> SADD recommended_movies "어벤져스" "타이타닉" "인셉션" "인터스텔라" "기생충"
(integer) 5

# 사용자가 이미 본 영화
127.0.0.1:6379> SADD user:1001:watched_movies "타이타닉" "기생충"
(integer) 2

# 아직 보지 않은 영화 중에서 추천
127.0.0.1:6379> SDIFFSTORE user:1001:unwatched recommended_movies user:1001:watched_movies
(integer) 3

127.0.0.1:6379> SRANDMEMBER user:1001:unwatched 2
1) "인셉션"
2) "어벤져스"   # 랜덤 추천 영화 2개
```

#### 3) A/B 테스트 그룹 분배
```bash
# 전체 사용자
127.0.0.1:6379> SADD all_users $(printf 'user%d ' {1001..1100})
(integer) 100

# A 그룹에 50% 할당
127.0.0.1:6379> SPOP all_users 50 | head -50 | xargs -I {} redis-cli SADD group_a {}

# B 그룹에 나머지 할당
127.0.0.1:6379> SUNIONSTORE group_b all_users
(integer) 50

# 그룹 크기 확인
127.0.0.1:6379> SCARD group_a
(integer) 50

127.0.0.1:6379> SCARD group_b
(integer) 50

# 사용자가 어느 그룹인지 확인
127.0.0.1:6379> SISMEMBER group_a "user1050"
(integer) 1   # A 그룹

127.0.0.1:6379> SISMEMBER group_b "user1050"
(integer) 0   # B 그룹 아님
```

#### 4) 캐시 무효화 태그
```bash
# 캐시 항목별 태그
127.0.0.1:6379> SADD cache:user:1001:tags "user_data" "profile" "settings"
(integer) 3

127.0.0.1:6379> SADD cache:user:1002:tags "user_data" "profile"
(integer) 2

127.0.0.1:6379> SADD cache:posts:recent:tags "posts" "homepage"
(integer) 2

# 특정 태그로 캐시 무효화 대상 찾기
127.0.0.1:6379> KEYS cache:*
1) "cache:user:1001:tags"
2) "cache:user:1002:tags"
3) "cache:posts:recent:tags"

# "user_data" 태그를 가진 캐시들 찾기 (애플리케이션 로직)
# for cache_key in cache:*:tags:
#     if SISMEMBER cache_key "user_data":
#         invalidate_cache(cache_key)

127.0.0.1:6379> SISMEMBER cache:user:1001:tags "user_data"
(integer) 1   # 무효화 대상

127.0.0.1:6379> SISMEMBER cache:posts:recent:tags "user_data"
(integer) 0   # 무효화 대상 아님
```

---

## 🔍 5. 실전 종합 프로젝트

### 5.1 프로젝트 1: 소셜 미디어 태그 시스템

#### 요구사항
- 게시글별 태그 관리
- 태그별 게시글 검색
- 인기 태그 순위
- 사용자별 관심 태그

#### 구현

##### 1) 게시글 태그 관리
```bash
# 게시글별 태그 추가
127.0.0.1:6379> SADD post:1001:tags "여행" "일본" "도쿄" "맛집" "카페"
(integer) 5

127.0.0.1:6379> SADD post:1002:tags "기술" "프로그래밍" "Python" "AI" "머신러닝"
(integer) 5

127.0.0.1:6379> SADD post:1003:tags "여행" "유럽" "프랑스" "파리" "맛집"
(integer) 5

127.0.0.1:6379> SADD post:1004:tags "기술" "웹개발" "JavaScript" "React" "프론트엔드"
(integer) 5

# 태그별 게시글 인덱스 생성
127.0.0.1:6379> SADD tag:여행:posts "post:1001" "post:1003"
(integer) 2

127.0.0.1:6379> SADD tag:기술:posts "post:1002" "post:1004"
(integer) 2

127.0.0.1:6379> SADD tag:맛집:posts "post:1001" "post:1003"
(integer) 2

127.0.0.1:6379> SADD tag:프로그래밍:posts "post:1002"
(integer) 1

127.0.0.1:6379> SADD tag:JavaScript:posts "post:1004"
(integer) 1
```

##### 2) 태그 검색 기능
```bash
# 특정 태그를 가진 게시글 찾기
127.0.0.1:6379> SMEMBERS tag:여행:posts
1) "post:1001"
2) "post:1003"

# 여러 태그의 교집합 (AND 검색)
127.0.0.1:6379> SINTER tag:여행:posts tag:맛집:posts
1) "post:1001"
2) "post:1003"   # 여행 AND 맛집

# 여러 태그의 합집합 (OR 검색)
127.0.0.1:6379> SUNION tag:기술:posts tag:여행:posts
1) "post:1001"
2) "post:1002"
3) "post:1003"
4) "post:1004"   # 기술 OR 여행

# 복잡한 검색: (기술 OR 프로그래밍) AND NOT 웹개발
127.0.0.1:6379> SUNIONSTORE temp:tech_programming tag:기술:posts tag:프로그래밍:posts
(integer) 2

127.0.0.1:6379> SDIFF temp:tech_programming tag:웹개발:posts
1) "post:1002"   # 기술/프로그래밍이지만 웹개발이 아닌 게시글
```

##### 3) 인기 태그 시스템
```bash
# 태그 사용 횟수 추적 (String 타입 활용)
127.0.0.1:6379> INCR tag:여행:count
(integer) 1

127.0.0.1:6379> INCR tag:여행:count
(integer) 2   # post:1001, post:1003에서 사용

127.0.0.1:6379> INCR tag:기술:count
(integer) 1

127.0.0.1:6379> INCR tag:기술:count
(integer) 2   # post:1002, post:1004에서 사용

127.0.0.1:6379> INCR tag:맛집:count
(integer) 1

127.0.0.1:6379> INCR tag:맛집:count
(integer) 2   # post:1001, post:1003에서 사용

# 모든 태그 목록 관리
127.0.0.1:6379> SADD all_tags "여행" "일본" "도쿄" "맛집" "카페" "기술" "프로그래밍" "Python" "AI" "머신러닝" "유럽" "프랑스" "파리" "웹개발" "JavaScript" "React" "프론트엔드"
(integer) 17

# 인기 태그 상위 5개 찾기 (애플리케이션에서 구현)
# for tag in all_tags:
#     count = GET tag:{tag}:count
#     top_tags.append((tag, count))
# sort and return top 5
```

##### 4) 사용자 관심 태그 추천
```bash
# 사용자가 좋아요한 게시글들의 태그 분석
127.0.0.1:6379> SADD user:1001:liked_posts "post:1001" "post:1003"
(integer) 2

# 좋아요한 게시글들의 태그 합집합
127.0.0.1:6379> SUNIONSTORE user:1001:interest_tags post:1001:tags post:1003:tags
(integer) 8

127.0.0.1:6379> SMEMBERS user:1001:interest_tags
1) "여행"
2) "일본"
3) "도쿄"
4) "맛집"
5) "카페"
6) "유럽"
7) "프랑스"
8) "파리"

# 사용자의 관심 태그 기반 게시글 추천
127.0.0.1:6379> SINTER user:1001:interest_tags post:1002:tags
(empty array)   # 공통 태그 없음

127.0.0.1:6379> SINTER user:1001:interest_tags post:1004:tags
(empty array)   # 공통 태그 없음

# 새로운 게시글 추가
127.0.0.1:6379> SADD post:1005:tags "여행" "이탈리아" "로마" "맛집" "와인"
(integer) 5

127.0.0.1:6379> SINTER user:1001:interest_tags post:1005:tags
1) "여행"
2) "맛집"        # 관심 태그와 일치하는 새 게시글
```

### 5.2 프로젝트 2: 온라인 쇼핑몰 추천 시스템

#### 요구사항
- 사용자별 구매 이력 관리
- 상품별 구매자 추적
- 협업 필터링 추천
- 카테고리별 인기 상품

#### 구현

##### 1) 구매 이력 관리
```bash
# 사용자별 구매한 상품
127.0.0.1:6379> SADD user:1001:purchased "상품A" "상품B" "상품C" "상품D"
(integer) 4

127.0.0.1:6379> SADD user:1002:purchased "상품B" "상품C" "상품E" "상품F"
(integer) 4

127.0.0.1:6379> SADD user:1003:purchased "상품A" "상품C" "상품G" "상품H"
(integer) 4

127.0.0.1:6379> SADD user:1004:purchased "상품B" "상품D" "상품F" "상품I"
(integer) 4

# 상품별 구매자
127.0.0.1:6379> SADD product:상품A:buyers "user:1001" "user:1003"
(integer) 2

127.0.0.1:6379> SADD product:상품B:buyers "user:1001" "user:1002" "user:1004"
(integer) 3

127.0.0.1:6379> SADD product:상품C:buyers "user:1001" "user:1002" "user:1003"
(integer) 3
```

##### 2) 유사한 취향의 사용자 찾기
```bash
# user:1001과 비슷한 취향의 사용자 찾기
127.0.0.1:6379> SINTER user:1001:purchased user:1002:purchased
1) "상품B"
2) "상품C"        # 공통 구매 상품 2개

127.0.0.1:6379> SINTER user:1001:purchased user:1003:purchased
1) "상품A"
2) "상품C"        # 공통 구매 상품 2개

127.0.0.1:6379> SINTER user:1001:purchased user:1004:purchased
1) "상품B"
2) "상품D"        # 공통 구매 상품 2개

# 가장 유사한 사용자의 추천 상품 (user:1002가 샀지만 user:1001이 안 산 것)
127.0.0.1:6379> SDIFF user:1002:purchased user:1001:purchased
1) "상품E"
2) "상품F"        # user:1001에게 추천할 상품들
```

##### 3) 상품 기반 추천 (함께 구매된 상품)
```bash
# user:1001이 구매한 상품을 산 다른 사용자들 찾기
127.0.0.1:6379> SUNIONSTORE users_with_similar_products product:상품A:buyers product:상품B:buyers product:상품C:buyers product:상품D:buyers
(integer) 4

127.0.0.1:6379> SREM users_with_similar_products "user:1001"  # 자기 자신 제거
(integer) 1

127.0.0.1:6379> SMEMBERS users_with_similar_products
1) "user:1002"
2) "user:1003"
3) "user:1004"

# 이 사용자들이 구매한 모든 상품
127.0.0.1:6379> SUNIONSTORE potential_recommendations user:1002:purchased user:1003:purchased user:1004:purchased
(integer) 8

# user:1001이 아직 구매하지 않은 상품만 추천
127.0.0.1:6379> SDIFF potential_recommendations user:1001:purchased
1) "상품E"
2) "상품F"
3) "상품G"
4) "상품H"
5) "상품I"        # 추천 상품 목록
```

##### 4) 카테고리별 인기 상품
```bash
# 카테고리별 상품 분류
127.0.0.1:6379> SADD category:전자제품 "상품A" "상품B" "상품C"
(integer) 3

127.0.0.1:6379> SADD category:의류 "상품D" "상품E" "상품F"
(integer) 3

127.0.0.1:6379> SADD category:도서 "상품G" "상품H" "상품I"
(integer) 3

# 전자제품 카테고리에서 인기 상품 (구매자 수 기준)
127.0.0.1:6379> SCARD product:상품A:buyers
(integer) 2

127.0.0.1:6379> SCARD product:상품B:buyers
(integer) 3

127.0.0.1:6379> SCARD product:상품C:buyers
(integer) 3

# 상품B와 상품C가 가장 인기 (구매자 3명)
```

### 5.3 프로젝트 3: 멀티플레이어 게임 매칭 시스템

#### 요구사항
- 플레이어 스킬 레벨별 그룹화
- 온라인 플레이어 관리
- 게임 방 참가자 관리
- 매칭 대기열 시스템

#### 구현

##### 1) 스킬 레벨별 플레이어 분류
```bash
# 스킬 레벨별 플레이어 그룹
127.0.0.1:6379> SADD skill:bronze "player1001" "player1002" "player1003"
(integer) 3

127.0.0.1:6379> SADD skill:silver "player1004" "player1005" "player1006" "player1007"
(integer) 4

127.0.0.1:6379> SADD skill:gold "player1008" "player1009" "player1010"
(integer) 3

127.0.0.1:6379> SADD skill:platinum "player1011" "player1012"
(integer) 2

# 현재 온라인 플레이어
127.0.0.1:6379> SADD online_players "player1001" "player1004" "player1005" "player1008" "player1009" "player1011"
(integer) 6
```

##### 2) 매칭 가능한 플레이어 찾기
```bash
# 실버 레벨 온라인 플레이어
127.0.0.1:6379> SINTER skill:silver online_players
1) "player1004"
2) "player1005"

# 골드 레벨 온라인 플레이어
127.0.0.1:6379> SINTER skill:gold online_players
1) "player1008"
2) "player1009"

# 플래티넘 레벨 온라인 플레이어
127.0.0.1:6379> SINTER skill:platinum online_players
1) "player1011"   # 혼자뿐이므로 매칭 어려움

# 인접 스킬 레벨 플레이어와 매칭 (플래티넘 + 골드)
127.0.0.1:6379> SUNIONSTORE expanded_match skill:platinum skill:gold
(integer) 5

127.0.0.1:6379> SINTER expanded_match online_players
1) "player1008"
2) "player1009"
3) "player1011"   # 3명으로 매칭 가능
```

##### 3) 게임 방 관리
```bash
# 게임 방 생성 및 참가자 관리
127.0.0.1:6379> SADD room:1001:players "player1004" "player1005"
(integer) 2

127.0.0.1:6379> SADD room:1002:players "player1008" "player1009" "player1011"
(integer) 3

# 방 정원 확인
127.0.0.1:6379> SCARD room:1001:players
(integer) 2   # 2/4명 (예: 4인 게임)

127.0.0.1:6379> SCARD room:1002:players
(integer) 3   # 3/4명

# 플레이어가 방에 참가
127.0.0.1:6379> SADD room:1001:players "player1006"
(integer) 1

127.0.0.1:6379> SCARD room:1001:players
(integer) 3   # 3/4명

# 플레이어가 방에서 나감
127.0.0.1:6379> SREM room:1002:players "player1011"
(integer) 1

127.0.0.1:6379> SCARD room:1002:players
(integer) 2   # 2/4명
```

##### 4) 매칭 대기열 시스템
```bash
# 매칭 대기 중인 플레이어들
127.0.0.1:6379> SADD queue:bronze "player1002" "player1003"
(integer) 2

127.0.0.1:6379> SADD queue:silver "player1007"
(integer) 1

127.0.0.1:6379> SADD queue:gold "player1010"
(integer) 1

# 매칭 시스템: 같은 레벨에서 4명 모이면 게임 시작
127.0.0.1:6379> SCARD queue:bronze
(integer) 2   # 부족 (2/4명)

127.0.0.1:6379> SCARD queue:silver
(integer) 1   # 부족 (1/4명)

# 새 플레이어가 대기열에 참가
127.0.0.1:6379> SADD queue:bronze "player1013" "player1014"
(integer) 2

127.0.0.1:6379> SCARD queue:bronze
(integer) 4   # 충분! (4/4명)

# 매칭 완료 - 게임 방 생성
127.0.0.1:6379> SUNIONSTORE room:1003:players queue:bronze
(integer) 4

127.0.0.1:6379> DEL queue:bronze
(integer) 1   # 대기열 비우기

# 플레이어가 현재 어떤 상태인지 확인
127.0.0.1:6379> SISMEMBER online_players "player1002"
(integer) 1   # 온라인

127.0.0.1:6379> SISMEMBER room:1003:players "player1002"
(integer) 1   # 게임 중

127.0.0.1:6379> SISMEMBER queue:bronze "player1002"
(integer) 0   # 대기열에 없음
```

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: SMEMBERS로 대용량 Set 조회하다 서버 다운 😱

**상황**: 신입 개발자가 온라인 사용자 목록을 조회하려고 SMEMBERS를 사용했는데, 피크 시간대에 서버가 느려지기 시작했습니다.

```bash
# ❌ 주니어 개발자가 작성한 코드
# 10만 명의 온라인 사용자 조회
127.0.0.1:6379> SADD online_users $(printf 'user%d ' {1..100000})
(integer) 100000

# 위험: 모든 사용자를 한 번에 조회!
127.0.0.1:6379> SMEMBERS online_users
# 100,000개 원소를 모두 반환 → 메모리 폭발, 네트워크 과부하
# 서버 응답 시간: 5초 이상
# 다른 요청들 블로킹됨
```

**문제점**:
- 문제 1: SMEMBERS는 O(N) 시간복잡도로 모든 원소를 반환
- 문제 2: 10만 개 데이터를 한 번에 전송하여 네트워크 대역폭 소진
- 문제 3: Redis는 싱글 스레드라서 다른 요청 처리 불가
- 왜 이 문제가 발생하는가: SMEMBERS는 작은 Set(< 1,000개)용 명령어

**해결책**:
```bash
# ✅ 올바른 코드 - SSCAN 사용
127.0.0.1:6379> SSCAN online_users 0 COUNT 100
1) "98304"   # 다음 커서
2)  1) "user1234"
    2) "user5678"
    ... (100개만 반환)

# 애플리케이션에서 반복 호출
cursor = 0
while True:
    cursor, users = redis.sscan('online_users', cursor, count=100)
    process_users(users)  # 100명씩 처리
    if cursor == 0:
        break

# 또는 크기만 확인하려면
127.0.0.1:6379> SCARD online_users
(integer) 100000  # O(1) 시간복잡도, 즉시 반환
```

**배운 점**:
- 💡 팁 1: Set 크기가 1,000개 이상이면 SSCAN 사용
- 💡 팁 2: 전체 조회가 필요 없다면 SCARD로 크기만 확인
- 💡 팁 3: 프로덕션 환경에서는 KEYS, SMEMBERS 같은 O(N) 명령어 금지
- 💡 팁 4: Redis 모니터링으로 느린 명령어 감지 (`CONFIG SET slowlog-log-slower-than 10000`)

### 시나리오 2: 집합 연산 순서를 잘못 이해해서 버그 발생 🐛

**상황**: 주니어 개발자가 "구매하지 않은 상품 찾기" 기능을 구현하다가 예상과 다른 결과가 나왔습니다.

```bash
# ❌ 주니어 개발자가 작성한 코드
127.0.0.1:6379> SADD all_products "상품A" "상품B" "상품C" "상품D" "상품E"
(integer) 5

127.0.0.1:6379> SADD user:1001:purchased "상품A" "상품C"
(integer) 2

# 잘못된 순서: 구매한 것에서 전체 상품을 빼기?!
127.0.0.1:6379> SDIFF user:1001:purchased all_products
(empty array)  # 예상: ["상품B", "상품D", "상품E"], 실제: []

# 왜? 차집합은 "첫 번째 Set - 두 번째 Set"
# user:1001:purchased - all_products = {}
# {상품A, 상품C} - {상품A, 상품B, 상품C, 상품D, 상품E} = {}
```

**문제점**:
- 문제 1: SDIFF의 순서 의미를 잘못 이해
- 문제 2: 교집합/합집합은 순서 무관이지만, 차집합은 순서가 중요
- 문제 3: 테스트 데이터로 검증하지 않음
- 왜 이 문제가 발생하는가: 수학의 차집합 개념을 Redis 명령어에 제대로 적용하지 못함

**해결책**:
```bash
# ✅ 올바른 코드 - 순서 수정
127.0.0.1:6379> SDIFF all_products user:1001:purchased
1) "상품B"
2) "상품D"
3) "상품E"   # 정확한 결과!

# 명확한 이해를 위한 주석
# SDIFF A B = A에는 있지만 B에는 없는 원소
# SDIFF all_products purchased = 전체 상품 중 구매하지 않은 것

# 여러 Set 차집합도 순서 중요
127.0.0.1:6379> SADD user:1001:cart "상품B"
(integer) 1

# 구매도 안 했고 장바구니에도 없는 상품
127.0.0.1:6379> SDIFF all_products user:1001:purchased user:1001:cart
1) "상품D"
2) "상품E"   # 전체 - 구매 - 장바구니
```

**배운 점**:
- 💡 팁 1: SDIFF는 "첫 번째 - 나머지 모두" 순서로 동작
- 💡 팁 2: SINTER, SUNION은 순서 무관 (교환법칙 성립)
- 💡 팁 3: 항상 작은 테스트 데이터로 먼저 검증
- 💡 팁 4: 복잡한 연산은 중간 결과를 STORE로 저장해서 디버깅

### 시나리오 3: 양방향 관계를 한쪽만 업데이트해서 데이터 불일치 💔

**상황**: 좋아요 기능을 구현하는데, 사용자의 좋아요 목록만 업데이트하고 게시글의 좋아요 사용자 목록은 업데이트하지 않았습니다.

```bash
# ❌ 주니어 개발자가 작성한 코드
# 사용자가 게시글에 좋아요 클릭
127.0.0.1:6379> SADD user:1001:liked_posts "post:123"
(integer) 1

# 문제: post:123:likers에는 user:1001이 추가되지 않음!
127.0.0.1:6379> SMEMBERS post:123:likers
(empty array)  # 불일치 발생!

# 이후 "이 게시글의 좋아요 수"를 조회하면
127.0.0.1:6379> SCARD post:123:likers
(integer) 0  # 실제로는 user:1001이 좋아요 했는데 0으로 나옴

# 다른 개발자가 같은 게시글에 좋아요
127.0.0.1:6379> SADD user:1002:liked_posts "post:123"
(integer) 1
127.0.0.1:6379> SADD post:123:likers "user:1002"
(integer) 1

# 결과: user:1001의 좋아요는 누락, user:1002만 기록됨
127.0.0.1:6379> SCARD post:123:likers
(integer) 1  # 실제로는 2명인데 1명만 카운트
```

**문제점**:
- 문제 1: 양방향 관계를 한쪽만 업데이트 → 데이터 불일치
- 문제 2: 좋아요 수가 실제보다 적게 표시됨
- 문제 3: 트랜잭션 미사용으로 일관성 깨짐
- 왜 이 문제가 발생하는가: 관계형 DB처럼 자동으로 양방향 업데이트되지 않음

**해결책**:
```bash
# ✅ 올바른 코드 - 트랜잭션으로 양방향 업데이트
127.0.0.1:6379> MULTI
OK

127.0.0.1:6379> SADD user:1001:liked_posts "post:123"
QUEUED

127.0.0.1:6379> SADD post:123:likers "user:1001"
QUEUED

127.0.0.1:6379> EXEC
1) (integer) 1
2) (integer) 1

# 검증: 양쪽 모두 업데이트 확인
127.0.0.1:6379> SISMEMBER user:1001:liked_posts "post:123"
(integer) 1  # ✅

127.0.0.1:6379> SISMEMBER post:123:likers "user:1001"
(integer) 1  # ✅

# 좋아요 취소도 양방향
127.0.0.1:6379> MULTI
OK
127.0.0.1:6379> SREM user:1001:liked_posts "post:123"
QUEUED
127.0.0.1:6379> SREM post:123:likers "user:1001"
QUEUED
127.0.0.1:6379> EXEC
1) (integer) 1
2) (integer) 1

# Lua 스크립트로 더 안전하게 (선택사항)
# EVAL "redis.call('SADD', KEYS[1], ARGV[1]); redis.call('SADD', KEYS[2], ARGV[2])" 2 user:1001:liked_posts post:123:likers post:123 user:1001
```

**배운 점**:
- 💡 팁 1: 양방향 관계는 항상 MULTI/EXEC 트랜잭션으로 묶기
- 💡 팁 2: 중요한 로직은 Lua 스크립트로 원자성 보장
- 💡 팁 3: 코드 리뷰 시 양방향 업데이트 확인 체크리스트 추가
- 💡 팁 4: 정기적으로 데이터 정합성 검증 스크립트 실행

### 시나리오 4: 임시 Set을 정리하지 않아 메모리 누수 발생 💧

**상황**: 복잡한 집합 연산 결과를 임시 Set에 저장했는데, 정리하지 않아서 메모리가 계속 증가했습니다.

```bash
# ❌ 주니어 개발자가 작성한 코드
# 사용자 추천을 위한 복잡한 연산
127.0.0.1:6379> SINTERSTORE temp:recommendation user:1001:interests user:1002:interests
(integer) 5

127.0.0.1:6379> SUNIONSTORE temp:all_interests user:1001:interests user:1002:interests user:1003:interests
(integer) 15

127.0.0.1:6379> SDIFFSTORE temp:new_recommendations temp:all_interests user:1001:viewed
(integer) 8

# 결과만 사용하고 temp: 키들을 삭제하지 않음!
# 매 요청마다 새로운 temp: 키가 생성됨
# temp:recommendation:user1001:20241008:143522
# temp:recommendation:user1001:20241008:143523
# temp:recommendation:user1001:20241008:143524
# ... 계속 쌓임

# 1주일 후
127.0.0.1:6379> KEYS temp:*
1) "temp:recommendation"
2) "temp:all_interests"
3) "temp:new_recommendations"
... (수천 개)

# 메모리 사용량 폭증
127.0.0.1:6379> INFO memory
used_memory_human:5.23G  # 원래는 1GB였는데...
```

**문제점**:
- 문제 1: 임시 데이터를 정리하지 않아 메모리 누수
- 문제 2: TTL을 설정하지 않아 영구 저장됨
- 문제 3: 고유한 키 이름을 사용하지 않아 덮어쓰기도 안 됨
- 왜 이 문제가 발생하는가: Redis는 자동으로 메모리 정리를 하지 않음

**해결책**:
```bash
# ✅ 올바른 코드 - TTL 설정 또는 즉시 삭제

# 방법 1: TTL 설정 (권장)
127.0.0.1:6379> SINTERSTORE temp:recommendation user:1001:interests user:1002:interests
(integer) 5

127.0.0.1:6379> EXPIRE temp:recommendation 300
(integer) 1  # 5분 후 자동 삭제

# 방법 2: 사용 후 즉시 삭제
127.0.0.1:6379> SUNIONSTORE temp:all_interests user:1001:interests user:1002:interests
(integer) 10

# 결과 사용
127.0.0.1:6379> SMEMBERS temp:all_interests
... (결과 처리)

# 즉시 삭제
127.0.0.1:6379> DEL temp:all_interests
(integer) 1

# 방법 3: 트랜잭션으로 묶기
127.0.0.1:6379> MULTI
OK
127.0.0.1:6379> SDIFFSTORE temp:new_recs temp:all user:1001:viewed
QUEUED
127.0.0.1:6379> EXPIRE temp:new_recs 60
QUEUED
127.0.0.1:6379> EXEC
1) (integer) 8
2) (integer) 1

# 방법 4: 고유한 키 이름 + TTL
import time
import uuid

temp_key = f"temp:recs:{uuid.uuid4()}:{int(time.time())}"
redis.sinterstore(temp_key, "set1", "set2")
redis.expire(temp_key, 300)
result = redis.smembers(temp_key)
redis.delete(temp_key)  # 명시적 삭제
```

**배운 점**:
- 💡 팁 1: 모든 임시 키는 반드시 TTL 설정 (5분~1시간 권장)
- 💡 팁 2: temp: 접두사 사용으로 임시 데이터 명확히 표시
- 💡 팁 3: 크론 작업으로 오래된 temp: 키 정리
- 💡 팁 4: Redis 메모리 모니터링 알람 설정 (80% 이상 시 경고)
- 💡 팁 5: try-finally 블록으로 에러 발생 시에도 정리 보장

```python
# Python 예시
temp_key = None
try:
    temp_key = f"temp:recs:{uuid.uuid4()}"
    redis.sinterstore(temp_key, "set1", "set2")
    result = redis.smembers(temp_key)
    # 결과 처리
finally:
    if temp_key:
        redis.delete(temp_key)  # 에러 발생해도 정리
```

---

## 📝 핵심 정리

### 이 장에서 배운 핵심 개념

| 개념 | 설명 | 핵심 키워드 |
|------|------|-------------|
| Redis Set | 중복되지 않는 문자열들의 순서 없는 컬렉션 | 중복 불허, 순서 없음, O(1) 검색 |
| 멤버십 테스트 | SISMEMBER로 원소 존재 여부 즉시 확인 | O(1) 시간복잡도 |
| 교집합 | SINTER로 모든 Set에 공통인 원소 찾기 | AND 연산, 공통점 |
| 합집합 | SUNION으로 여러 Set의 모든 원소 합치기 | OR 연산, 전체 모으기 |
| 차집합 | SDIFF로 첫 Set에만 있는 원소 찾기 | 차이점, 추천 시스템 |

### 필수 명령어/코드 정리

| 명령어/코드 | 용도 | 예시 |
|-------------|------|------|
| `SADD key member ...` | 원소 추가 | `SADD tags "redis" "db"` |
| `SREM key member ...` | 원소 제거 | `SREM tags "old"` |
| `SISMEMBER key member` | 원소 존재 확인 | `SISMEMBER tags "redis"` |
| `SINTER key1 key2 ...` | 교집합 | `SINTER set1 set2` |
| `SUNION key1 key2 ...` | 합집합 | `SUNION set1 set2` |
| `SDIFF key1 key2 ...` | 차집합 | `SDIFF all purchased` |
| `SCARD key` | Set 크기 | `SCARD online_users` |
| `SPOP key [count]` | 임의 원소 제거 | `SPOP lottery 1` |
| `SRANDMEMBER key [count]` | 임의 원소 조회 | `SRANDMEMBER items 5` |

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [x] 1,000개 이상 Set은 SSCAN으로 순회
- [x] 양방향 관계는 MULTI/EXEC로 원자적 업데이트
- [x] 임시 Set은 반드시 TTL 설정 (5분~1시간)
- [x] temp: 접두사로 임시 키 명시
- [x] 집합 연산 전 Set 크기 확인
- [x] 자주 사용하는 연산 결과는 SINTERSTORE로 캐싱

#### ❌ 하지 말아야 할 것
- [x] 대용량 Set에서 SMEMBERS 사용 금지
- [x] 단방향만 업데이트하여 데이터 불일치 발생
- [x] 임시 Set을 정리하지 않아 메모리 누수
- [x] 순서가 필요한 데이터를 Set에 저장
- [x] 차집합(SDIFF) 순서 무시
- [x] 트랜잭션 없이 복잡한 연산 수행

### 성능/보안 체크리스트

#### 성능
- [x] Set 크기가 10만 개 이상이면 샤딩 고려
- [x] SLOWLOG로 느린 집합 연산 모니터링
- [x] 작은 Set을 집합 연산 첫 번째 인자로 배치
- [x] 결과 캐싱으로 중복 연산 방지
- [x] intset 인코딩 활용 (정수만 사용 시)

#### 보안
- [x] 사용자 입력 검증 후 Set에 추가
- [x] Set 크기 제한으로 DoS 공격 방지
- [x] 민감한 데이터는 암호화하여 저장
- [x] 권한 Set 접근 제어 강화
- [x] 임시 Set의 TTL 설정으로 정보 유출 방지

---

## 📝 6. 핵심 내용 정리 및 베스트 프랙티스

### 6.1 Set 타입 명령어 완전 정리

#### 기본 조작 명령어
| 명령어 | 용도 | 예시 | 반환값 |
|--------|------|------|--------|
| `SADD key member [member ...]` | 원소 추가 | `SADD myset "a" "b"` | 추가된 원소 개수 |
| `SREM key member [member ...]` | 원소 제거 | `SREM myset "a"` | 제거된 원소 개수 |
| `SISMEMBER key member` | 원소 존재 확인 | `SISMEMBER myset "a"` | 1 또는 0 |
| `SMISMEMBER key member [member ...]` | 여러 원소 존재 확인 | `SMISMEMBER myset "a" "b"` | [1, 0] 형태 |
| `SMEMBERS key` | 모든 원소 조회 | `SMEMBERS myset` | 원소 배열 |
| `SCARD key` | Set 크기 | `SCARD myset` | 원소 개수 |

#### 집합 연산 명령어
| 명령어 | 용도 | 예시 | 반환값 |
|--------|------|------|--------|
| `SINTER key [key ...]` | 교집합 | `SINTER set1 set2` | 교집합 원소들 |
| `SUNION key [key ...]` | 합집합 | `SUNION set1 set2` | 합집합 원소들 |
| `SDIFF key [key ...]` | 차집합 | `SDIFF set1 set2` | 차집합 원소들 |
| `SINTERSTORE dest key [key ...]` | 교집합 저장 | `SINTERSTORE result set1 set2` | 저장된 원소 개수 |
| `SUNIONSTORE dest key [key ...]` | 합집합 저장 | `SUNIONSTORE result set1 set2` | 저장된 원소 개수 |
| `SDIFFSTORE dest key [key ...]` | 차집합 저장 | `SDIFFSTORE result set1 set2` | 저장된 원소 개수 |

#### 랜덤 조작 명령어
| 명령어 | 용도 | 예시 | 반환값 |
|--------|------|------|--------|
| `SPOP key [count]` | 임의 원소 제거 | `SPOP myset 2` | 제거된 원소들 |
| `SRANDMEMBER key [count]` | 임의 원소 조회 | `SRANDMEMBER myset 3` | 임의 원소들 |

### 6.2 집합 연산 활용 패턴

#### 교집합 (SINTER) - "공통점 찾기"
```bash
# 공통 관심사, 공통 권한, 공통 태그
SINTER user:A:interests user:B:interests    # 공통 관심사
SINTER role:admin role:manager              # 공통 권한
SINTER post:A:tags post:B:tags              # 공통 태그
```

#### 합집합 (SUNION) - "전체 모으기"
```bash
# 전체 권한, 전체 태그, 전체 사용자
SUNION role:admin role:manager role:user    # 모든 권한
SUNION tag:tech tag:travel tag:food         # 모든 태그
SUNION group:A group:B group:C              # 모든 그룹 사용자
```

#### 차집합 (SDIFF) - "차이점 찾기"
```bash
# 추천 대상, 미완료 항목, 신규 콘텐츠
SDIFF all_products user:purchased           # 아직 안 산 상품
SDIFF all_tasks user:completed              # 미완료 작업
SDIFF new_content user:viewed               # 안 본 콘텐츠
```

### 6.3 실무 베스트 프랙티스

#### 1) 적절한 Set 크기 관리
```bash
# 큰 Set의 SMEMBERS 사용 주의
# 좋은 예: 크기 확인 후 조회
SCARD large_set
# if size > 1000: use SSCAN instead of SMEMBERS

# 나쁜 예: 무조건 전체 조회
SMEMBERS very_large_set  # 위험!
```

#### 2) 메모리 효율적인 Set 설계
```bash
# 정수만 포함하는 Set은 intset 인코딩 활용
SADD numbers 1 2 3 4 5     # intset 인코딩 (메모리 효율적)
SADD mixed 1 "a" 2 "b"     # hashtable 인코딩 (메모리 많이 사용)

# 불필요한 Set은 주기적으로 정리
# TTL 설정 또는 애플리케이션에서 정리
```

#### 3) 일관성 있는 키 명명 규칙
```bash
# 좋은 예
user:1001:permissions
post:123:tags
category:electronics:products
room:1001:players

# 나쁜 예
user1001permissions
post123tags
electronicsproducts
room1001players
```

#### 4) 원자적 연산 활용
```bash
# 여러 Set 동시 업데이트 시 트랜잭션 고려
MULTI
SADD user:1001:liked_posts "post123"
SADD post:123:likers "user1001"
EXEC

# 또는 Lua 스크립트 활용 고려
```

#### 5) 성능 최적화 팁
```bash
# 빈번한 집합 연산은 결과 캐싱
SINTERSTORE cache:common_interests user:A:interests user:B:interests
EXPIRE cache:common_interests 3600

# 대용량 Set 순회는 SSCAN 사용
SSCAN large_set 0 COUNT 100

# 불필요한 중간 결과 즉시 정리
SDIFFSTORE temp:result set1 set2
# 사용 후
DEL temp:result
```

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용 (7개)

<details>
<summary><strong>1. Redis Set이란 무엇이며, List와 어떻게 다른가요?</strong></summary>

**모범 답안 포인트**
- Redis Set은 중복되지 않는 문자열들의 순서 없는 컬렉션입니다
- List는 중복 허용, 순서 있음 / Set은 중복 불허, 순서 없음
- Set은 O(1) 멤버십 테스트, List는 O(N)
- Set은 집합 연산(교집합, 합집합, 차집합) 지원

**예시 답변**
> "Redis Set은 중복되지 않는 문자열들의 집합입니다. List와의 가장 큰 차이는 중복 불허와 순서가 없다는 점입니다. 예를 들어, 온라인 사용자 목록이나 태그 시스템처럼 중복이 없어야 하고 순서가 중요하지 않은 데이터에 적합합니다. 또한 SISMEMBER로 특정 원소의 존재 여부를 O(1) 시간복잡도로 즉시 확인할 수 있어, List의 O(N)보다 훨씬 빠릅니다."

**꼬리 질문**
- Q: 그럼 언제 Set을 사용하고 언제 List를 사용하나요?
- A: 순서가 중요하고 중복을 허용해야 하면 List(예: 최근 검색 기록, 메시지 큐), 중복이 없어야 하고 빠른 검색이 필요하면 Set(예: 좋아요 목록, 태그 시스템, 권한 관리)를 사용합니다.

**실무 연관**
- 실무에서 Set은 소셜 기능(좋아요, 팔로우), 권한 관리, 태그 시스템, 추천 엔진에 많이 사용됩니다.

</details>

<details>
<summary><strong>2. Set의 교집합(SINTER), 합집합(SUNION), 차집합(SDIFF)을 설명하고 각각의 사용 사례를 제시하세요.</strong></summary>

**모범 답안 포인트**
- SINTER: 모든 Set에 공통으로 있는 원소 (AND 연산)
- SUNION: 여러 Set의 모든 원소를 합침 (OR 연산)
- SDIFF: 첫 번째 Set에서 나머지 Set의 원소를 뺌 (차집합)
- 각 연산의 실무 활용 사례

**예시 답변**
> "SINTER는 여러 Set의 교집합으로, 모든 조건을 만족하는 데이터를 찾을 때 사용합니다. 예를 들어 '서울에 배달 가능하면서 한식이고 할인 중인 가게'를 찾을 때 세 Set의 교집합을 구합니다. SUNION은 합집합으로, 여러 역할의 권한을 모두 합칠 때 사용합니다. SDIFF는 차집합으로, 전체 상품 중 사용자가 구매하지 않은 상품을 찾을 때 사용합니다."

**실무 예시**
```bash
# 친구 추천: A의 친구들의 친구 중 A가 아직 친구가 아닌 사람
SUNIONSTORE temp:friends_of_friends user:A:friend1:friends user:A:friend2:friends
SDIFF temp:friends_of_friends user:A:friends  # 추천 대상
```

**꼬리 질문**
- Q: SDIFF에서 인자 순서가 중요한가요?
- A: 네, 매우 중요합니다. SDIFF는 "첫 번째 Set - 나머지 모든 Set"을 계산하므로, SDIFF A B와 SDIFF B A는 완전히 다른 결과를 반환합니다.

**실무 연관**
- 추천 시스템, 검색 필터링, 권한 관리 등에서 집합 연산은 핵심 기능입니다.

</details>

<details>
<summary><strong>3. SMEMBERS 명령어가 위험한 이유와 대안을 설명하세요.</strong></summary>

**모범 답안 포인트**
- SMEMBERS는 O(N) 시간복잡도로 모든 원소를 반환
- 대용량 Set에서 사용 시 서버 블로킹 및 메모리/네트워크 과부하
- 대안: SSCAN (커서 기반 순회), SCARD (크기만 확인)
- 프로덕션 환경에서는 SMEMBERS 사용 금지 권장

**예시 답변**
> "SMEMBERS는 Set의 모든 원소를 한 번에 반환하는 명령어입니다. 문제는 10만 개 이상의 대용량 Set에서 사용하면 모든 데이터를 메모리에 로드하고 네트워크로 전송하느라 서버가 블로킹된다는 점입니다. Redis는 싱글 스레드라서 이 동안 다른 요청을 처리할 수 없습니다. 대신 SSCAN을 사용해 100~1,000개씩 나눠서 조회하거나, 전체 개수만 필요하다면 SCARD를 사용하는 것이 안전합니다."

**실무 예시**
```bash
# ❌ 위험: 10만 개 모두 조회
SMEMBERS large_set  # 서버 다운 가능성

# ✅ 안전: 100개씩 순회
SSCAN large_set 0 COUNT 100

# ✅ 또는 개수만 확인
SCARD large_set  # O(1), 즉시 반환
```

**꼬리 질문**
- Q: SSCAN의 COUNT 파라미터는 정확히 그 개수만큼 반환하나요?
- A: 아니오, COUNT는 힌트일 뿐이며 실제로는 그보다 많거나 적게 반환될 수 있습니다. 하지만 대략 그 정도 개수를 목표로 합니다.

**실무 연관**
- 프로덕션 환경에서 SMEMBERS 사용으로 인한 장애 사례가 많아, 대부분의 회사에서 금지 명령어로 지정합니다.

</details>

<details>
<summary><strong>4. Set에서 중복된 값을 추가하면 어떻게 되나요? 반환값은 무엇인가요?</strong></summary>

**모범 답안 포인트**
- Set은 중복을 허용하지 않으므로 이미 존재하는 값은 추가되지 않음
- SADD는 실제로 추가된 원소의 개수를 반환
- 중복 값은 0을 반환하여 이미 존재함을 알림
- 멱등성(idempotency) 보장

**예시 답변**
> "Set은 중복을 허용하지 않으므로, 이미 존재하는 값을 SADD로 추가하려고 하면 무시됩니다. 반환값은 실제로 추가된 원소의 개수이므로, 이미 존재하는 값만 추가하려고 하면 0이 반환됩니다. 예를 들어 SADD myset 'apple'을 두 번 실행하면, 첫 번째는 1을 반환하지만 두 번째는 0을 반환합니다. 이러한 특성 덕분에 중복 체크 로직 없이 안전하게 사용할 수 있습니다."

**실무 예시**
```bash
127.0.0.1:6379> SADD tags "redis"
(integer) 1  # 추가됨

127.0.0.1:6379> SADD tags "redis"
(integer) 0  # 이미 존재, 추가 안 됨

127.0.0.1:6379> SADD tags "redis" "python" "java"
(integer) 2  # redis는 0, python과 java만 추가되어 2 반환
```

**꼬리 질문**
- Q: 이런 특성이 실무에서 어떻게 유용한가요?
- A: 태그 시스템이나 좋아요 기능에서 중복 체크 로직 없이 SADD만 호출하면 되므로 코드가 단순해지고 버그 가능성이 줄어듭니다. 또한 SADD의 반환값으로 실제로 추가되었는지 확인할 수 있습니다.

**실무 연관**
- 좋아요, 팔로우, 태그 추가 등의 기능에서 중복 방지를 위해 Set의 이 특성을 활용합니다.

</details>

<details>
<summary><strong>5. Set의 내부 인코딩 방식(intset, hashtable)에 대해 설명하세요.</strong></summary>

**모범 답안 포인트**
- intset: 정수만 포함하고 512개 이하일 때 사용 (메모리 효율적)
- hashtable: 일반적인 경우 또는 문자열 포함 시 사용
- Redis가 자동으로 최적 인코딩 선택
- OBJECT ENCODING 명령어로 확인 가능

**예시 답변**
> "Redis는 Set의 크기와 데이터 타입에 따라 내부적으로 다른 인코딩을 사용합니다. intset은 모든 원소가 정수이고 512개 이하일 때 사용되며, 메모리를 매우 효율적으로 사용합니다. hashtable은 문자열이 포함되거나 512개를 초과할 때 사용되며, O(1) 검색 성능을 보장합니다. Redis가 자동으로 최적의 인코딩을 선택하므로, 개발자는 특별히 신경 쓸 필요 없이 항상 좋은 성능을 얻을 수 있습니다."

**실무 예시**
```bash
# intset 인코딩 (메모리 효율적)
127.0.0.1:6379> SADD numbers 1 2 3 4 5
127.0.0.1:6379> OBJECT ENCODING numbers
"intset"

# hashtable 인코딩 (문자열 포함)
127.0.0.1:6379> SADD mixed 1 "a" 2 "b"
127.0.0.1:6379> OBJECT ENCODING mixed
"hashtable"
```

**꼬리 질문**
- Q: 인코딩을 개발자가 직접 선택할 수 있나요?
- A: 아니오, Redis가 자동으로 선택합니다. 하지만 set-max-intset-entries 설정으로 intset의 최대 크기를 조정할 수 있습니다 (기본값 512).

**실무 연관**
- 정수 ID를 다루는 경우 intset 인코딩으로 메모리를 크게 절약할 수 있습니다. 예를 들어 사용자 ID 목록은 intset으로 관리됩니다.

</details>

<details>
<summary><strong>6. 좋아요 기능을 구현할 때 왜 양방향 관계를 모두 업데이트해야 하나요?</strong></summary>

**모범 답안 포인트**
- user:X:liked_posts와 post:Y:likers 두 Set을 모두 관리
- 한쪽만 업데이트하면 데이터 불일치 발생
- MULTI/EXEC 트랜잭션으로 원자적 업데이트
- 양방향 조회 성능을 위한 역정규화(denormalization)

**예시 답변**
> "좋아요 기능은 '사용자가 어떤 게시글을 좋아했는가'와 '게시글을 누가 좋아했는가' 두 관점이 모두 필요합니다. 만약 user:1001:liked_posts에만 추가하고 post:123:likers는 업데이트하지 않으면, 해당 게시글의 좋아요 수를 조회할 때 잘못된 결과가 나옵니다. 따라서 MULTI/EXEC 트랜잭션으로 두 Set을 동시에 업데이트하여 데이터 일관성을 보장해야 합니다."

**실무 예시**
```bash
# 좋아요 추가 (양방향 업데이트)
MULTI
SADD user:1001:liked_posts "post:123"
SADD post:123:likers "user:1001"
EXEC

# 좋아요 취소 (양방향 삭제)
MULTI
SREM user:1001:liked_posts "post:123"
SREM post:123:likers "user:1001"
EXEC
```

**꼬리 질문**
- Q: Lua 스크립트를 사용하는 것이 MULTI/EXEC보다 나은가요?
- A: Lua 스크립트는 더 복잡한 로직이 필요할 때 유용합니다. 단순한 양방향 업데이트는 MULTI/EXEC으로 충분하지만, 조건부 로직이 필요하면 Lua 스크립트를 고려할 수 있습니다.

**실무 연관**
- 소셜 기능(좋아요, 팔로우), 태그 시스템 등 양방향 관계가 있는 모든 기능에 적용됩니다.

</details>

<details>
<summary><strong>7. Set을 사용한 추천 시스템의 기본 원리를 설명하세요.</strong></summary>

**모범 답안 포인트**
- 공통 관심사 찾기: SINTER로 교집합 계산
- 유사 사용자 찾기: 공통 아이템이 많은 사용자
- 추천 아이템: 유사 사용자가 좋아한 것 중 본인이 안 본 것 (SDIFF)
- 협업 필터링(Collaborative Filtering)의 기본 개념

**예시 답변**
> "Set 기반 추천 시스템은 협업 필터링의 간단한 형태입니다. 먼저 SINTER로 두 사용자의 공통 관심사를 찾아 유사도를 측정합니다. 공통 관심사가 많은 사용자를 '유사한 사용자'로 판단하고, 그 사용자가 좋아한 아이템 중 본인이 아직 접하지 않은 것을 SDIFF로 찾아 추천합니다. 예를 들어 A와 B가 10개 영화 중 8개를 공통으로 좋아했다면, B가 좋아한 나머지 2개를 A에게 추천하는 방식입니다."

**실무 예시**
```bash
# 사용자 A, B의 공통 관심사
SINTER user:A:interests user:B:interests
# → {여행, 음식, 영화}

# B가 관심 있지만 A는 아닌 것
SDIFF user:B:interests user:A:interests
# → {독서, 운동} → A에게 추천

# 여러 유사 사용자의 관심사 합집합
SUNION user:B:interests user:C:interests user:D:interests
SDIFF temp:all user:A:interests  # A에게 추천할 새 관심사
```

**꼬리 질문**
- Q: 이 방식의 한계는 무엇인가요?
- A: 단순 교집합만으로는 선호도 강도를 반영할 수 없고, 인기 아이템에 편향될 수 있습니다. 실무에서는 Sorted Set으로 점수를 함께 관리하거나, 머신러닝 모델과 결합하여 사용합니다.

**실무 연관**
- Netflix, YouTube, Amazon 등 모든 추천 시스템의 기초가 되는 개념이며, Set 연산은 초기 필터링 단계에서 활용됩니다.

</details>

---

### 📗 중급 개발자용 (5개)

<details>
<summary><strong>1. Set 연산의 시간 복잡도와 대용량 데이터 처리 시 고려사항을 설명하세요.</strong></summary>

**모범 답안 포인트**
- O(1) 연산: SADD, SREM, SISMEMBER, SCARD
- O(N) 연산: SMEMBERS, SINTER, SUNION, SDIFF
- 대용량 Set 연산 시 블로킹 이슈
- 성능 최적화 전략: 작은 Set 먼저, 결과 캐싱, 비동기 처리

**예시 답변**
> "Set의 기본 조작(SADD, SISMEMBER 등)은 O(1)으로 매우 빠르지만, 집합 연산(SINTER, SUNION 등)은 O(N)입니다. 10만 개 Set 3개의 교집합을 구하면 최악의 경우 30만 번 연산이 필요하므로, Redis가 수 밀리초 동안 블로킹될 수 있습니다. 최적화 전략으로는 1) 가장 작은 Set을 먼저 처리, 2) 자주 사용하는 결과는 SINTERSTORE로 캐싱, 3) 매우 큰 Set은 애플리케이션 레벨에서 나눠서 처리하는 방법이 있습니다."

**실무 예시**
```bash
# 최적화 전략 1: 작은 Set 먼저
# SINTER는 첫 번째 Set을 기준으로 나머지를 체크하므로
# 가장 작은 Set을 첫 번째 인자로 전달
SINTER small_set(100) large_set(100000)  # 빠름
# vs
SINTER large_set(100000) small_set(100)  # 느림

# 최적화 전략 2: 결과 캐싱
SINTERSTORE cache:common_tags tag:A tag:B tag:C
EXPIRE cache:common_tags 3600  # 1시간 캐싱
# 이후 재사용: SMEMBERS cache:common_tags
```

**꼬리 질문**
- Q: 집합 연산이 너무 느리면 어떻게 감지하고 대응하나요?
- A: Redis의 slowlog를 모니터링하여 느린 명령어를 감지하고, 필요시 Read Replica로 부하를 분산하거나, 연산을 비동기 작업으로 옮기거나, 결과를 미리 계산해두는 사전 집계(pre-aggregation) 방식을 사용합니다.

**실무 연관**
- 대규모 서비스에서는 집합 연산의 성능 이슈가 자주 발생하므로, 모니터링과 최적화가 필수입니다.

</details>

<details>
<summary><strong>2. 임시 Set 관리 전략과 메모리 누수 방지 방법을 설명하세요.</strong></summary>

**모범 답안 포인트**
- 임시 Set의 TTL 설정 필수 (5분~1시간)
- temp: 네임스페이스 사용으로 명확한 구분
- try-finally 패턴으로 에러 시에도 정리 보장
- 정기적인 메모리 모니터링 및 알람

**예시 답변**
> "복잡한 집합 연산의 중간 결과를 임시 Set에 저장할 때, 반드시 TTL을 설정해야 합니다. 설정하지 않으면 영구 저장되어 메모리 누수가 발생합니다. 모범 사례는 1) temp: 접두사로 임시 키 명시, 2) SINTERSTORE 직후 EXPIRE 호출, 3) 고유한 키 이름(UUID, 타임스탬프) 사용, 4) 프로그래밍 언어의 try-finally 블록으로 에러 발생 시에도 정리 보장입니다. 또한 크론 작업으로 오래된 temp: 키를 주기적으로 정리하는 것도 좋습니다."

**실무 예시**
```python
import uuid
import redis

def safe_set_operation():
    temp_key = f"temp:intersect:{uuid.uuid4()}"
    try:
        # 집합 연산
        redis_client.sinterstore(temp_key, "set1", "set2", "set3")
        redis_client.expire(temp_key, 300)  # 5분 TTL

        # 결과 사용
        result = redis_client.smembers(temp_key)
        return result
    finally:
        # 에러 발생 시에도 정리
        redis_client.delete(temp_key)

# 크론 작업 (매 시간 실행)
# SCAN으로 temp:* 패턴 찾아서 1시간 이상 오래된 키 삭제
```

**꼬리 질문**
- Q: Lua 스크립트로 더 안전하게 처리할 수 있나요?
- A: 네, Lua 스크립트는 원자적으로 실행되므로 중간에 에러가 발생해도 일관성을 보장합니다. 하지만 간단한 경우는 TTL + try-finally로 충분합니다.

**실무 연관**
- 메모리 누수는 실무에서 가장 흔한 Redis 장애 원인 중 하나이므로, 철저한 관리가 필요합니다.

</details>

<details>
<summary><strong>3. Set을 활용한 권한 관리 시스템 설계 방법을 설명하세요.</strong></summary>

**모범 답안 포인트**
- 역할별 권한 Set 정의 (role:admin, role:user 등)
- 사용자별 역할 Set (user:X:roles)
- SUNION으로 모든 역할의 권한 합치기
- 권한 확인: SISMEMBER로 O(1) 체크

**예시 답변**
> "Set 기반 권한 관리는 RBAC(Role-Based Access Control)를 구현하는 효율적인 방법입니다. 먼저 role:admin, role:manager 등 역할별 권한 Set을 정의합니다. 사용자는 여러 역할을 가질 수 있으므로 user:1001:roles에 역할 목록을 저장합니다. 실제 권한 확인 시, SUNION으로 사용자의 모든 역할 권한을 합친 후, SISMEMBER로 특정 권한 여부를 O(1)에 확인합니다. 캐싱을 위해 SUNIONSTORE로 사용자별 전체 권한을 미리 계산해둘 수도 있습니다."

**실무 예시**
```bash
# 역할별 권한 정의
SADD role:admin user_read user_write user_delete system_config
SADD role:manager user_read user_write report_read
SADD role:user profile_read profile_write

# 사용자에게 역할 부여
SADD user:1001:roles admin manager

# 사용자의 전체 권한 계산 (캐싱)
SUNIONSTORE user:1001:permissions role:admin role:manager
EXPIRE user:1001:permissions 3600  # 1시간 캐싱

# 권한 확인
SISMEMBER user:1001:permissions system_config
# → 1 (권한 있음)
```

**꼬리 질문**
- Q: 역할이 변경되면 어떻게 캐시를 갱신하나요?
- A: 역할 변경 시 해당 역할을 가진 모든 사용자의 user:X:permissions 키를 삭제하거나, Pub/Sub으로 캐시 무효화 이벤트를 발행합니다.

**실무 연관**
- 마이크로서비스에서 권한 관리 서비스를 별도로 구성할 때 Redis Set이 자주 사용됩니다.

</details>

<details>
<summary><strong>4. Set과 Sorted Set의 차이점과 각각의 적합한 사용 사례를 설명하세요.</strong></summary>

**모범 답안 포인트**
- Set: 순서 없음, 점수 없음, 단순 집합 연산
- Sorted Set: 점수 기반 정렬, 범위 조회 가능, 순위 시스템
- Set은 멤버십 테스트와 집합 연산에 최적화
- Sorted Set은 랭킹, 우선순위 큐, 시간 범위 조회에 최적화

**예시 답변**
> "Set은 순서와 점수가 없는 단순 집합으로, 중복 체크와 집합 연산(교집합, 합집합)에 최적화되어 있습니다. 반면 Sorted Set은 각 원소에 점수(score)를 부여하여 자동 정렬되며, 범위 조회와 순위 계산이 가능합니다. 따라서 '사용자가 좋아요한 게시글 목록'은 순서가 필요 없으므로 Set을 사용하고, '게임 리더보드'는 점수순 정렬이 필요하므로 Sorted Set을 사용합니다. Set의 집합 연산은 Sorted Set에서도 가능하지만, 성능이 Set보다 느릴 수 있습니다."

**실무 예시**
```bash
# Set 사용 사례: 태그, 권한, 좋아요
SADD post:123:tags "redis" "database" "nosql"
SISMEMBER post:123:tags "redis"  # O(1) 확인

# Sorted Set 사용 사례: 랭킹, 최신 게시글
ZADD leaderboard 9500 "player1" 8700 "player2"
ZREVRANGE leaderboard 0 9  # 상위 10명

# Sorted Set으로 시간 범위 조회
ZADD recent:posts 1696723200 "post:1" 1696809600 "post:2"
ZRANGEBYSCORE recent:posts 1696723200 1696809600  # 특정 시간대
```

**꼬리 질문**
- Q: 그럼 항상 Sorted Set을 사용하는 게 좋지 않나요?
- A: 아니오, Sorted Set은 메모리를 더 많이 사용하고 집합 연산이 느립니다. 점수와 정렬이 필요 없다면 Set이 더 효율적입니다.

**실무 연관**
- 실무에서는 두 타입을 함께 사용하는 경우가 많습니다. 예: 좋아요 여부는 Set으로, 인기 순위는 Sorted Set으로 관리.

</details>

<details>
<summary><strong>5. Redis Set을 사용한 실시간 추천 시스템의 성능 최적화 전략을 제시하세요.</strong></summary>

**모범 답안 포인트**
- 사전 계산(Pre-computation): 유사도 미리 계산
- 캐싱: SINTERSTORE로 중간 결과 저장
- 샘플링: 전체가 아닌 일부만 비교
- 하이브리드 접근: Set + Sorted Set + 머신러닝

**예시 답변**
> "대규모 추천 시스템에서는 실시간 집합 연산이 병목이 될 수 있습니다. 최적화 전략으로 1) 사용자 간 유사도를 미리 계산하여 Sorted Set에 저장 (매 시간 배치 작업), 2) 자주 요청되는 추천 결과를 SINTERSTORE로 캐싱 (TTL 1시간), 3) 모든 사용자가 아닌 상위 100명 유사 사용자만 샘플링하여 비교, 4) Set 연산으로 후보를 좁히고 Sorted Set으로 정밀 랭킹을 계산하는 하이브리드 방식을 사용합니다. 또한 Read Replica를 활용해 추천 조회 부하를 분산합니다."

**실무 예시**
```bash
# 전략 1: 유사 사용자 사전 계산 (배치 작업)
# 매 시간 모든 사용자 간 공통 관심사 개수 계산
SINTER user:A:interests user:B:interests | SCARD
# → Sorted Set에 저장
ZADD user:A:similar_users 8 "user:B" 6 "user:C"

# 전략 2: 추천 결과 캐싱
SUNIONSTORE cache:recs:user:A similar_user_1:likes similar_user_2:likes
SDIFFSTORE cache:new_recs:user:A cache:recs:user:A user:A:likes
EXPIRE cache:new_recs:user:A 3600

# 전략 3: 상위 N명만 사용
ZREVRANGE user:A:similar_users 0 99  # 유사도 상위 100명
# 이들의 관심사만 합침
```

**꼬리 질문**
- Q: 사전 계산의 비용이 너무 크면 어떻게 하나요?
- A: 증분 업데이트(incremental update) 방식으로 변경된 부분만 재계산하거나, 중요도가 높은 사용자(활성 사용자)만 우선 계산합니다. 또한 Apache Spark 같은 분산 처리 시스템으로 오프라인 배치를 수행할 수 있습니다.

**실무 연관**
- Netflix, Amazon, YouTube 등은 모두 사전 계산 + 실시간 보정 하이브리드 방식을 사용합니다.

</details>

---

---

## 🔗 관련 기술

**Set과 함께 사용하는 Redis 타입들**

| 기술 | 관계 | 학습 우선순위 |
|------|------|---------------|
| Hash | 사용자 프로필 + 권한 Set 조합 | ⭐⭐⭐ |
| Sorted Set | Set 필터링 + Sorted Set 랭킹 | ⭐⭐⭐ |
| List | Set 멤버십 + List 순서 보장 | ⭐⭐ |
| String | Set 크기 카운터 (태그 인기도) | ⭐⭐ |
| Pub/Sub | Set 변경 시 이벤트 발행 | ⭐ |

---

## ❓ FAQ

<details>
<summary><strong>Q1: Set에서 원소의 순서가 보장되지 않는 이유는 무엇인가요?</strong></summary>

**A**: Set은 내부적으로 해시 테이블을 사용하므로 순서가 없습니다.

**상세 설명**:
- Set은 빠른 O(1) 검색을 위해 해시 테이블 구조 사용
- 해시 함수의 특성상 삽입 순서와 저장 순서가 다름
- 순서가 필요하면 다른 타입 사용 권장

**예시**:
```bash
# 순서가 필요하면 다른 데이터 타입 사용
# List: 순서 있음, 중복 허용
# Sorted Set: 순서 있음, 중복 없음, 점수 기반 정렬
```

**실무 팁**:
순서가 필요한 경우 Set + Sorted Set을 함께 사용하여 멤버십 테스트(Set)와 순서(Sorted Set)를 동시에 활용할 수 있습니다.

</details>

<details>
<summary><strong>Q2: SMEMBERS가 위험한 이유는 무엇인가요?</strong></summary>

**A**: 큰 Set의 모든 원소를 한 번에 반환하여 메모리와 네트워크 부하를 일으킵니다.

**상세 설명**:
- O(N) 시간복잡도로 모든 원소 조회
- 10만 개 이상 Set에서 사용 시 서버 블로킹
- 메모리 폭발 및 네트워크 대역폭 소진

**예시**:
```bash
# 위험한 상황
SADD huge_set $(seq 1 1000000)  # 100만 개 원소
SMEMBERS huge_set               # 100만 개 원소 모두 반환!

# 안전한 대안
SSCAN huge_set 0 COUNT 100      # 100개씩 순회
```

**실무 팁**:
프로덕션 환경에서는 SMEMBERS를 금지 명령어로 지정하고, SSCAN 사용을 권장합니다.

</details>

<details>
<summary><strong>Q3: Set 연산의 성능은 어떻게 되나요?</strong></summary>

**A**: Set 크기에 따라 다릅니다.

**상세 설명**:
- O(1) 연산: SADD, SREM, SISMEMBER, SCARD (즉시 실행)
- O(N) 연산: SMEMBERS, SINTER, SUNION, SDIFF (크기에 비례)
- 큰 Set 연산 시 블로킹 가능

**예시**:
```bash
# O(1): 매우 빠름
SADD, SREM, SISMEMBER, SCARD

# O(N): Set 크기에 비례 (주의 필요)
SMEMBERS, SINTER, SUNION, SDIFF

# 큰 Set 연산 시 성능 고려 필요
```

**실무 팁**:
대용량 Set 연산은 Read Replica로 부하 분산하거나, 결과를 미리 계산하여 캐싱합니다.

</details>

<details>
<summary><strong>Q4: 집합 연산에서 순서가 중요한가요?</strong></summary>

**A**: SDIFF에서는 순서가 중요합니다.

**상세 설명**:
- SINTER, SUNION: 순서 무관 (교환법칙 성립)
- SDIFF: "첫 번째 Set - 나머지 Set" 순서로 동작
- 차집합은 순서에 따라 완전히 다른 결과

**예시**:
```bash
SADD setA "a" "b" "c"
SADD setB "b" "c" "d"

SDIFF setA setB   # ["a"] - setA에만 있는 것
SDIFF setB setA   # ["d"] - setB에만 있는 것

# SINTER, SUNION은 순서 무관
SINTER setA setB  # SINTER setB setA와 동일
```

**실무 팁**:
차집합 사용 시 "전체 - 부분" 순서로 인자를 배치하면 혼란을 줄일 수 있습니다.

</details>

<details>
<summary><strong>Q5: Set의 최대 크기 제한이 있나요?</strong></summary>

**A**: 이론적으로는 2^32 - 1개 원소까지 가능하지만, 실무에서는 메모리 제한을 고려해야 합니다.

**상세 설명**:
- 이론적 최대: 약 42억 개 원소
- 실무적 권장: 수천~수만 개
- 메모리가 충분하면 더 큰 Set도 가능

**예시**:
```bash
# 실무 권장사항:
# - 일반적인 Set: 수천~수만 개
# - 자주 조회하는 Set: 수백~수천 개
# - 큰 Set: SSCAN으로 순회, 정기적 정리
```

**실무 팁**:
10만 개 이상의 Set은 샤딩을 고려하거나, 주기적으로 정리하는 전략이 필요합니다.

</details>

<details>
<summary><strong>Q6: SPOP과 SRANDMEMBER의 차이점은 무엇인가요?</strong></summary>

**A**: SPOP은 원소를 제거하면서 반환하고, SRANDMEMBER는 제거하지 않고 조회만 합니다.

**상세 설명**:
- SPOP: 원소를 Set에서 **영구 제거**하며 반환 (추첨, 샘플링에 사용)
- SRANDMEMBER: 원소를 그대로 두고 **조회만** (미리보기, 랜덤 추천에 사용)
- SPOP은 빈 Set에서 nil 반환, SRANDMEMBER도 동일

**예시**:
```bash
127.0.0.1:6379> SADD prize_pool "상품A" "상품B" "상품C" "상품D" "상품E"
(integer) 5

# SPOP: 1등 당첨 (제거됨)
127.0.0.1:6379> SPOP prize_pool
"상품C"   # 상품C가 영구 제거됨

127.0.0.1:6379> SCARD prize_pool
(integer) 4   # 4개 남음

# SRANDMEMBER: 미리보기 (제거 안 됨)
127.0.0.1:6379> SRANDMEMBER prize_pool
"상품A"   # 조회만, 여전히 존재

127.0.0.1:6379> SCARD prize_pool
(integer) 4   # 여전히 4개

# 여러 개 조회/제거
127.0.0.1:6379> SRANDMEMBER prize_pool 2   # 2개 조회 (제거 안 됨)
1) "상품B"
2) "상품D"

127.0.0.1:6379> SPOP prize_pool 2   # 2등, 3등 당첨 (제거됨)
1) "상품A"
2) "상품E"

127.0.0.1:6379> SMEMBERS prize_pool
1) "상품B"
2) "상품D"   # 2개만 남음
```

**실무 팁**:
- 추첨 시스템: SPOP (한 번 뽑힌 사람은 제외)
- 랜덤 콘텐츠 추천: SRANDMEMBER (같은 콘텐츠 반복 추천 가능)
- A/B 테스트 그룹 분배: SPOP (각 사용자는 한 그룹에만 속함)

</details>

<details>
<summary><strong>Q7: Set 연산 결과를 저장하는 STORE 명령어는 언제 사용하나요?</strong></summary>

**A**: 집합 연산 결과를 재사용하거나, 중간 결과를 캐싱할 때 SINTERSTORE, SUNIONSTORE, SDIFFSTORE를 사용합니다.

**상세 설명**:
- 일반 명령어(SINTER, SUNION, SDIFF): 결과를 클라이언트에 반환만
- STORE 명령어: 결과를 새로운 Set에 저장 (재사용 가능)
- 네트워크 대역폭 절약 (큰 결과를 매번 전송하지 않음)
- 복잡한 다단계 연산에서 중간 결과 저장

**예시**:
```bash
# 사용자의 모든 역할 권한 합치기
127.0.0.1:6379> SADD role:admin "user_read" "user_write" "system_config"
(integer) 3

127.0.0.1:6379> SADD role:manager "user_read" "report_read"
(integer) 2

# 일반 SUNION: 클라이언트에 결과 반환만
127.0.0.1:6379> SUNION role:admin role:manager
1) "user_read"
2) "user_write"
3) "system_config"
4) "report_read"

# SUNIONSTORE: 결과를 user:1001:permissions에 저장
127.0.0.1:6379> SUNIONSTORE user:1001:permissions role:admin role:manager
(integer) 4   # 저장된 원소 개수

# 이후 빠르게 재사용
127.0.0.1:6379> SISMEMBER user:1001:permissions "system_config"
(integer) 1   # 즉시 확인 (재계산 불필요)

# TTL 설정으로 자동 정리
127.0.0.1:6379> EXPIRE user:1001:permissions 3600
(integer) 1   # 1시간 후 자동 삭제
```

**실무 활용**:
```bash
# 복잡한 검색 필터링
# 1단계: 배달 가능한 가게
SINTERSTORE temp:step1 deliverable:stores korean:stores
# → 배달 가능한 한식 가게

# 2단계: 할인 중인 가게만
SINTERSTORE temp:step2 temp:step1 on_sale:stores
# → 배달 가능한 한식 할인 가게

# 3단계: 이미 주문한 가게 제외
SDIFFSTORE final_results temp:step2 user:1001:ordered_stores
# → 최종 추천 가게

# 결과 확인
SMEMBERS final_results

# 정리
DEL temp:step1 temp:step2 final_results
```

**실무 팁**:
- 자주 사용하는 연산은 STORE로 캐싱 (응답 시간 단축)
- 임시 Set은 반드시 TTL 설정 또는 명시적 삭제
- 복잡한 다단계 연산에서 디버깅 용이

</details>

<details>
<summary><strong>Q8: Set을 사용한 태그 시스템에서 "OR" 검색과 "AND" 검색을 어떻게 구현하나요?</strong></summary>
**A**: SUNION으로 OR 검색, SINTER로 AND 검색을 구현합니다.

**상세 설명**:
- OR 검색: 태그 중 하나라도 만족 (SUNION)
- AND 검색: 모든 태그를 만족 (SINTER)
- 복합 조건: SUNION과 SINTER 조합

**예시**:
```bash
# 태그별 게시글 인덱스
127.0.0.1:6379> SADD tag:python:posts "post:1" "post:2" "post:3"
(integer) 3

127.0.0.1:6379> SADD tag:redis:posts "post:2" "post:4" "post:5"
(integer) 3

127.0.0.1:6379> SADD tag:docker:posts "post:3" "post:4" "post:6"
(integer) 3

# OR 검색: "python" OR "redis" (둘 중 하나라도 있으면)
127.0.0.1:6379> SUNION tag:python:posts tag:redis:posts
1) "post:1"
2) "post:2"
3) "post:3"
4) "post:4"
5) "post:5"   # python 또는 redis 태그가 있는 모든 게시글

# AND 검색: "python" AND "redis" (둘 다 있어야 함)
127.0.0.1:6379> SINTER tag:python:posts tag:redis:posts
1) "post:2"   # python과 redis 둘 다 있는 게시글만

# 복합 조건: ("python" OR "redis") AND "docker"
# 1단계: python OR redis
127.0.0.1:6379> SUNIONSTORE temp:python_or_redis tag:python:posts tag:redis:posts
(integer) 5

# 2단계: (python OR redis) AND docker
127.0.0.1:6379> SINTER temp:python_or_redis tag:docker:posts
1) "post:3"
2) "post:4"   # (python 또는 redis) 그리고 docker가 모두 있는 게시글

# 정리
127.0.0.1:6379> DEL temp:python_or_redis
(integer) 1
```

**실무 구현 예시** (Python):
```python
def search_posts(or_tags=None, and_tags=None):
    """
    or_tags: OR 조건 태그 리스트
    and_tags: AND 조건 태그 리스트
    """
    if or_tags and len(or_tags) > 1:
        # OR 검색
        keys = [f"tag:{tag}:posts" for tag in or_tags]
        return redis_client.sunion(*keys)
    elif and_tags and len(and_tags) > 1:
        # AND 검색
        keys = [f"tag:{tag}:posts" for tag in and_tags]
        return redis_client.sinter(*keys)
    elif or_tags or and_tags:
        # 단일 태그
        tag = (or_tags or and_tags)[0]
        return redis_client.smembers(f"tag:{tag}:posts")
    return set()

# 사용 예시
search_posts(or_tags=["python", "redis"])  # OR 검색
search_posts(and_tags=["python", "redis"])  # AND 검색
```

**실무 팁**:
- 대부분의 검색 엔진은 OR가 기본, AND는 고급 필터
- 성능: AND 검색이 OR 검색보다 빠름 (결과가 적음)
- 복잡한 쿼리: 중간 결과를 temp: Set에 저장하여 단계적 처리

</details>

<details>
<summary><strong>Q9: Set 데이터를 백업하고 복원하는 방법은?</strong></summary>
**A**: RDB 또는 AOF를 사용하거나, 애플리케이션 레벨에서 SMEMBERS로 내보내고 SADD로 복원합니다.

**상세 설명**:
- Redis 내장 방법: RDB 스냅샷, AOF 로그
- 애플리케이션 레벨: SMEMBERS로 읽어서 파일 저장, 복원 시 SADD
- 대용량 Set: SSCAN으로 나눠서 백업

**방법 1: Redis RDB 스냅샷** (권장)
```bash
# 즉시 스냅샷 생성
127.0.0.1:6379> SAVE   # 블로킹 (운영 환경 사용 금지)
# 또는
127.0.0.1:6379> BGSAVE   # 백그라운드 (권장)

# 스냅샷 파일 확인
127.0.0.1:6379> CONFIG GET dir
1) "dir"
2) "/var/lib/redis"

# dump.rdb 파일이 생성됨
# 복원: Redis 재시작 시 자동으로 dump.rdb 로드
```

**방법 2: 애플리케이션 레벨 백업** (Python)
```python
import redis
import json

# 백업
def backup_sets(set_keys, filename):
    r = redis.Redis()
    backup_data = {}

    for key in set_keys:
        # 작은 Set: SMEMBERS
        if r.scard(key) < 10000:
            backup_data[key] = list(r.smembers(key))
        else:
            # 큰 Set: SSCAN
            members = []
            cursor = 0
            while True:
                cursor, data = r.sscan(key, cursor, count=1000)
                members.extend(data)
                if cursor == 0:
                    break
            backup_data[key] = members

    with open(filename, 'w') as f:
        json.dump(backup_data, f)

    print(f"Backed up {len(set_keys)} sets to {filename}")

# 복원
def restore_sets(filename):
    r = redis.Redis()

    with open(filename, 'r') as f:
        backup_data = json.load(f)

    for key, members in backup_data.items():
        # 기존 데이터 삭제 (선택사항)
        r.delete(key)

        # 복원 (큰 Set은 나눠서)
        chunk_size = 1000
        for i in range(0, len(members), chunk_size):
            chunk = members[i:i+chunk_size]
            r.sadd(key, *chunk)

    print(f"Restored {len(backup_data)} sets from {filename}")

# 사용 예시
set_keys = ["online_users", "post:123:tags", "user:1001:permissions"]
backup_sets(set_keys, "redis_sets_backup.json")
restore_sets("redis_sets_backup.json")
```

**방법 3: Redis DUMP/RESTORE 명령어**
```bash
# 단일 키 백업
127.0.0.1:6379> DUMP myset
"\x0f\x01\x00\x00\x00\x03\x00\x00\x00\x01\x00a\xff..."

# 다른 Redis 인스턴스에 복원
127.0.0.1:6380> RESTORE myset 0 "\x0f\x01\x00\x00\x00\x03..."
OK

# TTL 포함 복원
127.0.0.1:6380> RESTORE myset 3600 "\x0f\x01..." # 1시간 TTL
OK
```

**실무 팁**:
- 정기적인 RDB 스냅샷 스케줄링 (cron 작업)
- 중요한 Set은 AOF(Append Only File)로 실시간 백업
- 재해 복구(DR) 계획에 백업 절차 포함
- 대용량 Set 백업 시 SSCAN으로 나눠서 처리

</details>

<details>
<summary><strong>Q10: 실무에서 Set 성능 모니터링은 어떻게 하나요?</strong></summary>
**A**: Redis INFO, SLOWLOG, 메모리 분석 도구를 활용하여 Set 성능을 모니터링합니다.

**주요 모니터링 지표**:

**1. Set 크기 모니터링**
```bash
# 특정 Set 크기 확인
127.0.0.1:6379> SCARD online_users
(integer) 45328

# 메모리 사용량 확인
127.0.0.1:6379> MEMORY USAGE online_users
(integer) 1048576   # 바이트 단위

# 전체 메모리 통계
127.0.0.1:6379> INFO memory
used_memory_human:2.50G
used_memory_peak_human:3.20G
```

**2. 느린 명령어 감지 (SLOWLOG)**
```bash
# slowlog 설정 (10ms 이상 명령어 기록)
127.0.0.1:6379> CONFIG SET slowlog-log-slower-than 10000
OK

# slowlog 조회
127.0.0.1:6379> SLOWLOG GET 10
1) 1) (integer) 15   # 로그 ID
   2) (integer) 1696723456   # 타임스탬프
   3) (integer) 25000   # 실행 시간 (마이크로초)
   4) 1) "SINTER"
      2) "large_set1"
      3) "large_set2"
      4) "large_set3"
   5) "127.0.0.1:52341"
   6) ""

# SINTER가 25ms 걸림 → 최적화 필요
```

**3. 주요 명령어 통계**
```bash
127.0.0.1:6379> INFO commandstats
# Commandstats
cmdstat_sadd:calls=125000,usec=450000,usec_per_call=3.60
cmdstat_sismember:calls=350000,usec=280000,usec_per_call=0.80
cmdstat_sinter:calls=1500,usec=125000,usec_per_call=83.33

# SINTER의 평균 실행 시간이 83.33μs → 주의 필요
```

**4. Set별 메모리 분석** (redis-cli --bigkeys)
```bash
$ redis-cli --bigkeys

# Scanning the entire keyspace to find biggest keys
# Biggest set found 'online_users' has 45328 members
# Biggest set found 'post:123:tags' has 156 members

# Summary
-------- summary -------
Sampled 10000 keys in the keyspace!
Total key length in bytes is 180000 (avg len 18.00)

Biggest   set found 'online_users' has 45328 members
```

**5. 실시간 모니터링** (Python)
```python
import redis
import time

r = redis.Redis()

def monitor_sets(set_keys):
    while True:
        print("=" * 50)
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        for key in set_keys:
            size = r.scard(key)
            memory = r.memory_usage(key) if r.exists(key) else 0

            print(f"{key}:")
            print(f"  Size: {size:,} members")
            print(f"  Memory: {memory:,} bytes ({memory/1024/1024:.2f} MB)")

        # 슬로우 로그 확인
        slow_logs = r.slowlog_get(5)
        if slow_logs:
            print("\nSlow commands (top 5):")
            for log in slow_logs:
                duration_ms = log['duration'] / 1000
                print(f"  {log['command']}: {duration_ms:.2f}ms")

        time.sleep(60)  # 1분마다 체크

# 사용 예시
monitor_sets(["online_users", "post:123:likers", "user:1001:permissions"])
```

**실무 알람 설정 예시**:
```python
def check_set_health(key, max_size=100000, max_memory_mb=100):
    """Set 건강 체크 및 알람"""
    size = r.scard(key)
    memory_mb = r.memory_usage(key) / 1024 / 1024

    alerts = []

    if size > max_size:
        alerts.append(f"⚠️  {key} 크기 초과: {size:,} > {max_size:,}")

    if memory_mb > max_memory_mb:
        alerts.append(f"⚠️  {key} 메모리 초과: {memory_mb:.2f}MB > {max_memory_mb}MB")

    # 슬로우 로그에서 해당 키 관련 명령어 체크
    slow_logs = r.slowlog_get(100)
    for log in slow_logs:
        if key.encode() in log['command']:
            duration_ms = log['duration'] / 1000
            if duration_ms > 100:  # 100ms 이상
                alerts.append(f"⚠️  {key} 느린 연산: {log['command']}, {duration_ms:.2f}ms")

    return alerts

# 정기 체크 (크론 작업)
alerts = check_set_health("online_users", max_size=50000, max_memory_mb=50)
if alerts:
    send_slack_alert("\n".join(alerts))  # Slack 알람
```

**실무 팁**:
- SLOWLOG 임계값: 10-50ms 권장 (운영 환경)
- 메모리 알람: 전체 메모리의 80% 도달 시 경고
- 대용량 Set (10만 개 이상): 주기적으로 SSCAN으로 정리
- Grafana + Prometheus로 시각화 대시보드 구성

</details>

---

## 🚀 8. 다음 단계 예고

다음 장에서는 **Hash 타입**을 완전히 정복합니다!

### 다음 장 미리보기: Hash 타입 완전 가이드
- **Hash 구조와 특징**: 필드-값 쌍의 효율적 관리
- **필드 조작**: `HSET`, `HGET`, `HDEL`로 세밀한 데이터 관리
- **Hash 전체 조작**: `HGETALL`, `HKEYS`, `HVALS`로 일괄 처리
- **숫자 필드 연산**: `HINCRBY`, `HINCRBYFLOAT`로 카운터 관리
- **실전 활용**: 사용자 프로필, 설정 관리, 세션 데이터, 캐시 시스템

### 준비하면 좋을 것들
```bash
# 다음 장을 위한 환경 정리
127.0.0.1:6379> SELECT 3
OK

127.0.0.1:6379[3]> FLUSHDB
OK

127.0.0.1:6379[3]> SELECT 0
OK
```

---

## 🎉 축하합니다!

**Redis Set 타입을 완전히 마스터했습니다!**

이 장을 완료한 여러분은 이제 Redis Set의 모든 기능을 실무에서 자유자재로 활용할 수 있는 능력을 갖추었습니다.

### 🏆 학습 완료 체크리스트

**이제 여러분은 다음을 할 수 있습니다**:

#### 핵심 능력
- ✅ **Set 기본 조작 완벽 마스터**: SADD, SREM, SMEMBERS, SISMEMBER, SCARD 완전 활용
- ✅ **집합 연산 전문가**: SINTER, SUNION, SDIFF로 복잡한 비즈니스 로직을 한 줄로 구현
- ✅ **O(1) 멤버십 테스트**: 100만 개 데이터에서도 1ms 내 검색 가능
- ✅ **성능 최적화**: SSCAN으로 대용량 Set 안전하게 순회
- ✅ **메모리 효율 관리**: intset과 hashtable 인코딩 이해 및 최적화

#### 실무 적용 능력
- ✅ **태그 시스템 구현**: OR/AND 검색, 다중 태그 필터링
- ✅ **추천 알고리즘 설계**: 공통 관심사 기반 협업 필터링
- ✅ **소셜 기능 구축**: 친구 추천, 공통 친구 찾기, 팔로우 시스템
- ✅ **권한 관리 시스템**: RBAC 구현, 역할별 권한 집합 연산
- ✅ **게임 매칭 시스템**: 티어별 대기열, 실시간 플레이어 관리
- ✅ **중복 제거 시스템**: 유니크 방문자, 중복 이벤트 처리

#### 고급 기술
- ✅ **임시 Set 안전 관리**: TTL 설정, try-finally 패턴, 메모리 누수 방지
- ✅ **트랜잭션 활용**: MULTI/EXEC로 양방향 관계 일관성 유지
- ✅ **성능 모니터링**: SLOWLOG, INFO commandstats, 메모리 분석
- ✅ **백업/복원 전략**: RDB, AOF, 애플리케이션 레벨 백업
- ✅ **프로덕션 최적화**: 작은 Set 우선, 결과 캐싱, Read Replica 활용

### 📊 학습 성과 요약

| 항목 | 학습 전 | 학습 후 | 개선 |
|------|---------|---------|------|
| Set 명령어 이해도 | 20% | 100% | **5배 향상** |
| 집합 연산 활용 능력 | 0% | 100% | **완전 습득** |
| 실무 문제 해결 속도 | 느림 | 즉시 | **10배 빠름** |
| 코드 품질 | 비효율 | 최적화 | **프로덕션급** |
| 면접 대응 능력 | 불안 | 자신감 | **완벽 준비** |

### 🎯 다음 단계 로드맵

**즉시 실행 가능한 액션 아이템**:
- [ ] **오늘**: 주니어 시나리오 3가지 다시 읽고 실습
- [ ] **이번 주**: 실전 프로젝트(소셜 네트워크 추천 시스템) 완성
- [ ] **다음 주**: 면접 질문 주니어 7개 + 중급 5개 모두 답변 연습
- [ ] **2주 내**: 본인 프로젝트에 Set 적용 (태그 또는 권한 시스템)

**지속적 성장 계획**:
- [ ] Hash 타입으로 필드-값 쌍 데이터 마스터 (다음 장)
- [ ] Sorted Set으로 랭킹 시스템 구현 (8장)
- [ ] Set + Hash + Sorted Set 조합 패턴 익히기
- [ ] 실제 서비스에 Redis Set 도입하여 성능 측정

### 💼 실무 준비도 체크

**면접 준비**:
- ✅ Set의 시간복잡도 설명 가능
- ✅ 집합 연산 실무 활용 사례 3개 이상 제시 가능
- ✅ SMEMBERS의 위험성과 대안 설명 가능
- ✅ 대용량 데이터 처리 최적화 전략 보유

**프로젝트 적용**:
- ✅ 태그 시스템 설계 및 구현 가능
- ✅ 추천 알고리즘 기초 구현 가능
- ✅ 권한 관리 시스템 설계 가능
- ✅ 성능 이슈 발생 시 즉시 대응 가능

### 🌟 당신은 이제...

**Set 타입의 마스터입니다!** 🎓

- 중복 없는 데이터 처리의 달인
- 집합 연산으로 복잡한 로직을 간단히 해결하는 개발자
- O(1) 검색으로 빠른 시스템을 만드는 엔지니어
- 메모리 효율과 성능 최적화를 모두 고려하는 전문가

이제 다음 장에서는 **Hash 타입**으로 필드-값 쌍 데이터를 다루며, 더욱 정교한 데이터 모델링 능력을 키워보겠습니다!

**계속해서 멋진 학습을 이어가세요!** 🚀

---

**다음 장으로 이동**: [7. Hash 타입 완전 가이드](./07-Hash-타입-완전-가이드.md)

**이전 장으로 돌아가기**: [5. List 타입 완전 가이드](./05-List-타입-완전-가이드.md)

**목차로 돌아가기**: [Redis 완전 학습 가이드](./redis%20가이드.md)