# 10장: Redis Pub/Sub 및 메시징 시스템 완전 가이드

> **학습 목표**: 이 장을 완료하면 Redis Pub/Sub와 Streams를 활용한 실시간 메시징 시스템을 설계하고 구현할 수 있습니다

**⏱️ 예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐⭐☆ (4개/5개)

---

## 📚 목차
- [왜 이 기술이 필요한가](#왜-이-기술이-필요한가)
- [실생활 비유로 이해하기](#실생활-비유로-이해하기)
- [Redis Pub/Sub 기본 개념](#1-redis-pubsub-기본-개념)
- [채널 기반 메시징](#2-채널-기반-메시징)
- [패턴 구독 및 고급 기능](#3-패턴-구독-및-고급-기능)
- [실전 프로젝트 1: 실시간 채팅 시스템](#4-실전-프로젝트-1-실시간-채팅-시스템)
- [실전 프로젝트 2: 실시간 알림 시스템](#5-실전-프로젝트-2-실시간-알림-시스템)
- [스트림 기반 메시징](#6-스트림-기반-메시징)
- [성능 최적화](#7-성능-최적화)
- [주니어 시나리오](#주니어-시나리오)
- [FAQ](#faq)
- [면접 질문 리스트](#면접-질문-리스트)
- [핵심 정리](#핵심-정리)
- [관련 기술](#관련-기술)
- [다음 단계](#다음-단계)
- [축하합니다](#축하합니다)

---

## 🤔 왜 이 기술이 필요한가?

### 실무 배경
**실시간 통신이 필수가 된 현대 웹 서비스에서 발생하는 문제들**

#### ❌ Redis Pub/Sub을 모르면 발생하는 문제
```
문제 1: 폴링 방식의 비효율성
- 증상: 클라이언트가 1초마다 서버에 "새 메시지 있나요?" 요청
- 영향: 초당 1000명 × 1요청 = 1000 TPS 낭비, 서버 CPU 80% 사용
- 비용: AWS EC2 t3.large → c5.2xlarge 업그레이드 필요 (월 $150 추가)

문제 2: 마이크로서비스 간 결합도 증가
- 증상: 주문 서비스가 알림 서비스 API를 직접 호출
- 영향: 알림 서비스 장애 시 주문 처리도 지연, 타임아웃 증가
- 비용: 평균 응답시간 200ms → 3000ms, 사용자 이탈률 35% 증가
```

#### ✅ Redis Pub/Sub을 사용하면
```
해결책 1: 실시간 푸시 방식
- 방법: WebSocket + Redis Pub/Sub으로 이벤트 발생 시 즉시 전송
- 효과: 서버 요청 99% 감소, CPU 사용률 10%로 하락
- 절감: t3.medium으로 다운그레이드 가능 (월 $100 절감)

해결책 2: 이벤트 기반 아키텍처
- 방법: 서비스 간 메시지 큐로 느슨한 결합
- 효과: 평균 응답시간 50ms, 장애 격리로 가용성 99.9% 달성
- 절감: 고객 만족도 40% 상승, 이탈률 5%로 감소
```

### 📊 수치로 보는 효과

| 지표 | 폴링 방식 | Redis Pub/Sub | 개선율 |
|------|-----------|---------------|--------|
| 평균 지연시간 | 500ms | 5ms | **99%↓** |
| 서버 CPU 사용률 | 80% | 10% | **87.5%↓** |
| 월 인프라 비용 | $500 | $120 | **76%↓** |
| 동시 접속 처리 | 1,000명 | 50,000명 | **4900%↑** |
| 메시지 전송 실패율 | 5% | 0.01% | **99.8%↓** |

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 유튜브 구독과 알림 🔔

```
Redis Pub/Sub = 유튜브 구독 시스템

Publisher (채널 주인):
- 유튜버가 새 영상을 업로드하면
- 구독자 모두에게 자동으로 알림 전송

Subscriber (구독자):
- 좋아하는 채널을 구독하면
- 새 영상이 올라올 때마다 알림 받음

Channel (채널):
- "게임 채널", "요리 채널", "기술 채널"처럼
- 주제별로 분리된 메시지 통로

┌─────────────────────────────────────┐
│     [유튜버] 새 영상 업로드!         │
│            ↓                        │
│    [유튜브 알림 시스템]              │
│      ↓      ↓      ↓                │
│  [구독자A] [구독자B] [구독자C]       │
│   "딩동!"  "딩동!"  "딩동!"         │
└─────────────────────────────────────┘

특징:
- 실시간: 영상 업로드 즉시 알림 (Pub/Sub도 즉시 전달)
- 다대다: 한 유튜버 → 여러 구독자 (1:N 관계)
- 선택적: 원하는 채널만 구독 (패턴 구독)
```

### 비유 2: 아파트 방송 시스템 📢

```
Redis Channels = 아파트 각 동별 스피커

전체 방송 (전체 채널):
- "전 주민 여러분, 내일 수도 공사가 있습니다"
- 모든 동에 동시에 방송

동별 방송 (특정 채널):
- "101동 주민분들만, 엘리베이터 점검합니다"
- 해당 동 주민만 듣게 됨

패턴 구독 (와일드카드):
- "1XX동 주민" → 101동, 102동, 103동... 모두 수신
- chat:room:* → 모든 채팅방 메시지 구독

┌──────────────────────────────────────┐
│  [관리사무소] 방송 송출               │
│       ↓         ↓         ↓          │
│   [101동]   [102동]   [103동]        │
│    ↓ ↓ ↓    ↓ ↓ ↓    ↓ ↓ ↓          │
│   세대들    세대들    세대들          │
└──────────────────────────────────────┘
```

### 비유 3: 카카오톡 단체 채팅방 💬

```
Redis Pub/Sub = 카카오톡 오픈 채팅

메시지 발행 (PUBLISH):
- 누군가 채팅방에 메시지 전송
- "오늘 저녁 뭐 먹을까요?"

메시지 구독 (SUBSCRIBE):
- 채팅방에 입장한 사람들만
- 실시간으로 메시지 수신

채팅방 나가기 (UNSUBSCRIBE):
- 퇴장하면 더 이상 메시지 안 받음
- 새 메시지 알림 없음

비영속성 특징:
- 채팅방에 없을 때 온 메시지는 못 봄
  (Redis Pub/Sub도 구독 중일 때만 수신)
- 나중에 들어와도 이전 메시지 안 보임
  (→ Streams를 쓰면 히스토리 저장 가능!)

┌─────────────────────────────────────┐
│  철수: "배고파"                      │
│     → [오픈채팅방]                   │
│         ↓  ↓  ↓                     │
│      영희 민수 지수 (모두 수신)      │
│                                     │
│  지수가 퇴장함                       │
│                                     │
│  영희: "치킨 먹을래?"                │
│     → [오픈채팅방]                   │
│         ↓  ↓                        │
│      철수 민수 (지수는 못 받음)      │
└─────────────────────────────────────┘
```

### 비유 4: 라디오 방송국 📻

```
Redis Pub/Sub = FM 라디오 방송

주파수 = 채널:
- FM 89.1 (뉴스 채널)
- FM 95.9 (음악 채널)
- FM 103.7 (스포츠 채널)

방송국 = Publisher:
- 라디오 주파수로 신호 송출
- 듣는 사람이 있든 없든 계속 방송

라디오 = Subscriber:
- 원하는 주파수에 맞춤
- 실시간으로 방송 수신

패턴 매칭 = 프리셋:
- "FM 90대 모두" → 90.1, 95.9, 99.9 등
- news:* → news:korea, news:world 등

┌─────────────────────────────────────┐
│  [방송국] 전파 송출                  │
│     ~~~~ 전파 ~~~~                  │
│    ↓     ↓     ↓                    │
│  [차량]  [집]  [사무실]             │
│  라디오  라디오 라디오              │
└─────────────────────────────────────┘

Fire-and-Forget:
- 방송은 계속되지만 듣는 사람 없으면 사라짐
- Redis도 구독자 없으면 메시지 버려짐
```

### 비유 5: 배달 앱 실시간 추적 🛵

```
Redis Streams = 배달 기사 이동 경로 기록

실시간 위치 업데이트:
- Pub/Sub: "지금 배달 기사가 여기 있어요!" (실시간만)
- Streams: "출발 → 음식점 도착 → 픽업 → 배달 중 → 완료" (히스토리 저장)

Consumer Group:
- 여러 알림 서버가 역할 분담
- A서버: 주문자에게 알림
- B서버: 통계 수집
- C서버: 관리자 대시보드 업데이트

┌─────────────────────────────────────┐
│ [배달 기사 앱]                       │
│   위치 업데이트 계속 전송             │
│         ↓                           │
│   [Redis Streams]                   │
│   출발(14:00) → 픽업(14:15) →       │
│   배달중(14:20) → 완료(14:35)       │
│         ↓                           │
│  [Consumer Group]                   │
│   ┌────┬────┬────┐                 │
│   │앱  │통계│대시│                 │
│   │알림│수집│보드│                 │
│   └────┴────┴────┘                 │
└─────────────────────────────────────┘

Pub/Sub vs Streams:
- Pub/Sub: 실시간만 필요할 때 (가볍고 빠름)
- Streams: 히스토리 필요할 때 (영속성, 재처리)
```

### 🎯 종합 비교표

```
┌──────────────┬────────────┬────────────┬────────────┐
│ Redis 개념   │ 유튜브     │ 아파트     │ 배달앱     │
├──────────────┼────────────┼────────────┼────────────┤
│ Publisher    │ 유튜버     │ 관리사무소 │ 배달기사   │
│ Subscriber   │ 구독자     │ 주민       │ 주문자     │
│ Channel      │ 채널       │ 각 동      │ 주문번호   │
│ Pattern      │ 카테고리   │ XX동 전체  │ 지역별     │
│ Message      │ 새 영상    │ 안내방송   │ 위치정보   │
│ Fire-Forget  │ 실시간알림 │ 실시간방송 │ 푸시알림   │
│ Streams      │ 업로드목록 │ 방송기록   │ 배달내역   │
└──────────────┴────────────┴────────────┴────────────┘
```

---

## 1. Redis Pub/Sub 기본 개념

### 1.1 Pub/Sub 아키텍처

Redis Pub/Sub는 **발행자(Publisher)**가 메시지를 전송하고 **구독자(Subscriber)**가 메시지를 수신하는 메시징 패턴입니다.

```bash
# 기본 구조
Publisher -> Channel -> Subscriber(s)

# 특징
# 1. 비동기 통신
# 2. 다대다 관계 (N:M)
# 3. 메시지 영속성 없음 (fire-and-forget)
# 4. 실시간 통신
```

### 1.2 기본 명령어

#### 1.2.1 SUBSCRIBE - 채널 구독

```bash
# 단일 채널 구독
127.0.0.1:6379> SUBSCRIBE news
Reading messages... (press Ctrl-C to quit)
1) "subscribe"
2) "news"
3) (integer) 1

# 여러 채널 동시 구독
127.0.0.1:6379> SUBSCRIBE news sports weather
Reading messages... (press Ctrl-C to quit)
1) "subscribe"
2) "news"
3) (integer) 1
1) "subscribe"
2) "sports"
3) (integer) 2
1) "subscribe"
2) "weather"
3) (integer) 3
```

#### 1.2.2 PUBLISH - 메시지 발행

```bash
# 새 터미널에서 메시지 발행
127.0.0.1:6379> PUBLISH news "Breaking: 새로운 기술 발표"
(integer) 1

127.0.0.1:6379> PUBLISH sports "축구: 월드컵 결과"
(integer) 1

# 구독자 터미널에서 메시지 수신 확인
1) "message"
2) "news"
3) "Breaking: 새로운 기술 발표"
1) "message"
2) "sports"
3) "축구: 월드컵 결과"
```

#### 1.2.3 UNSUBSCRIBE - 구독 해제

```bash
# 특정 채널 구독 해제
127.0.0.1:6379> UNSUBSCRIBE news
1) "unsubscribe"
2) "news"
3) (integer) 2

# 모든 채널 구독 해제
127.0.0.1:6379> UNSUBSCRIBE
1) "unsubscribe"
2) "sports"
3) (integer) 1
1) "unsubscribe"
2) "weather"
3) (integer) 0
```

### 1.3 Pub/Sub 정보 확인

#### 1.3.1 PUBSUB 명령어

```bash
# 활성 채널 목록
127.0.0.1:6379> PUBSUB CHANNELS
1) "news"
2) "sports"
3) "chat:room:1001"

# 패턴으로 채널 필터링
127.0.0.1:6379> PUBSUB CHANNELS chat:*
1) "chat:room:1001"
2) "chat:room:1002"

# 채널별 구독자 수 확인
127.0.0.1:6379> PUBSUB NUMSUB news sports
1) "news"
2) (integer) 3
3) "sports"
4) (integer) 1

# 패턴 구독자 수 확인
127.0.0.1:6379> PUBSUB NUMPAT
(integer) 2
```

---

## 2. 채널 기반 메시징

### 2.1 채널 네이밍 전략

#### 2.1.1 계층적 채널 구조

```bash
# 사용자별 알림 채널
user:1001:notifications
user:1001:messages
user:1001:updates

# 채팅방별 채널
chat:room:general
chat:room:tech
chat:room:private:1001:1002

# 시스템 이벤트 채널
system:alerts:critical
system:alerts:warning
system:alerts:info

# 게임 이벤트 채널
game:lobby:events
game:match:1001:events
game:leaderboard:updates
```

#### 2.1.2 환경별 채널 분리

```bash
# 개발 환경
dev:user:1001:notifications
dev:chat:room:general

# 스테이징 환경
staging:user:1001:notifications
staging:chat:room:general

# 프로덕션 환경
prod:user:1001:notifications
prod:chat:room:general
```

### 2.2 메시지 형식 표준화

#### 2.2.1 JSON 메시지 형식

```bash
# 기본 메시지 구조
{
  "type": "notification",
  "timestamp": "2024-03-15T14:30:22Z",
  "sender": "system",
  "data": {
    "title": "새 메시지",
    "content": "안녕하세요!",
    "priority": "normal"
  }
}

# 채팅 메시지
{
  "type": "chat_message",
  "timestamp": "2024-03-15T14:30:22Z",
  "sender": "user:1001",
  "room_id": "general",
  "data": {
    "message": "안녕하세요 여러분!",
    "message_id": "msg_123456"
  }
}

# 시스템 알림
{
  "type": "system_alert",
  "timestamp": "2024-03-15T14:30:22Z",
  "sender": "monitoring",
  "severity": "warning",
  "data": {
    "service": "database",
    "message": "연결 지연 감지",
    "metrics": {
      "latency": 1500,
      "threshold": 1000
    }
  }
}
```

### 2.3 실시간 애플리케이션 패턴

#### 2.3.1 사용자 상태 브로드캐스팅

```lua
-- user_status_broadcast.lua
local user_id = ARGV[1]
local status = ARGV[2]  -- "online", "offline", "away", "busy"
local timestamp = ARGV[3]

-- 사용자 상태 업데이트
redis.call('HSET', 'user:' .. user_id .. ':info', 'status', status, 'last_seen', timestamp)

-- 친구 목록 가져오기
local friends = redis.call('SMEMBERS', 'user:' .. user_id .. ':friends')

-- 각 친구에게 상태 변경 알림
for i, friend_id in ipairs(friends) do
    local channel = 'user:' .. friend_id .. ':friend_updates'
    local message = string.format('{"type":"friend_status","user_id":"%s","status":"%s","timestamp":"%s"}',
                                  user_id, status, timestamp)
    redis.call('PUBLISH', channel, message)
end

-- 전체 사용자 상태 채널에도 발행
local global_channel = 'users:status_updates'
local global_message = string.format('{"type":"user_status","user_id":"%s","status":"%s","timestamp":"%s"}',
                                    user_id, status, timestamp)
redis.call('PUBLISH', global_channel, global_message)

return #friends
```

```bash
# 사용자 상태 변경 알림
127.0.0.1:6379> EVAL "$(cat user_status_broadcast.lua)" 0 1001 online $(date +%s)
(integer) 25
```

#### 2.3.2 실시간 데이터 동기화

```lua
-- data_sync_broadcast.lua
local entity_type = ARGV[1]  -- "product", "user", "order"
local entity_id = ARGV[2]
local action = ARGV[3]       -- "create", "update", "delete"
local data = ARGV[4]         -- JSON 데이터
local user_id = ARGV[5]      -- 변경한 사용자

local timestamp = redis.call('TIME')[1]

-- 변경 이력 저장
local history_key = 'changes:' .. entity_type .. ':' .. entity_id
local change_record = string.format('{"action":"%s","user":"%s","timestamp":"%s","data":%s}',
                                   action, user_id, timestamp, data)
redis.call('LPUSH', history_key, change_record)
redis.call('LTRIM', history_key, 0, 99)  -- 최근 100개만 보관

-- 관련 채널들에 브로드캐스트
local channels = {
    entity_type .. ':' .. entity_id .. ':changes',           -- 특정 엔티티 채널
    entity_type .. ':changes',                               -- 엔티티 타입별 채널
    'admin:changes',                                         -- 관리자 채널
    'user:' .. user_id .. ':my_changes'                     -- 변경한 사용자 채널
}

local broadcast_message = string.format('{"type":"%s_%s","entity_id":"%s","action":"%s","user":"%s","timestamp":"%s","data":%s}',
                                       entity_type, action, entity_id, action, user_id, timestamp, data)

local published_count = 0
for i, channel in ipairs(channels) do
    local subscribers = redis.call('PUBLISH', channel, broadcast_message)
    published_count = published_count + subscribers
end

return {published_count, #channels}
```

---

## 3. 패턴 구독 및 고급 기능

### 3.1 PSUBSCRIBE - 패턴 구독

#### 3.1.1 와일드카드 패턴

```bash
# 모든 사용자 알림 구독
127.0.0.1:6379> PSUBSCRIBE user:*:notifications
Reading messages... (press Ctrl-C to quit)
1) "psubscribe"
2) "user:*:notifications"
3) (integer) 1

# 특정 채팅방들 구독
127.0.0.1:6379> PSUBSCRIBE chat:room:tech:* chat:room:general:*
Reading messages... (press Ctrl-C to quit)
1) "psubscribe"
2) "chat:room:tech:*"
3) (integer) 1
1) "psubscribe"
2) "chat:room:general:*"
3) (integer) 2

# 시스템 알림 구독 (모든 레벨)
127.0.0.1:6379> PSUBSCRIBE system:alerts:*
```

#### 3.1.2 복잡한 패턴 매칭

```bash
# 게임 관련 모든 이벤트
127.0.0.1:6379> PSUBSCRIBE game:*

# 특정 사용자의 모든 활동
127.0.0.1:6379> PSUBSCRIBE user:1001:*

# 여러 환경의 에러 로그
127.0.0.1:6379> PSUBSCRIBE *:errors:* *:logs:error
```

### 3.2 메시지 라우팅 시스템

#### 3.2.1 지능형 메시지 라우터

```lua
-- message_router.lua
local message_type = ARGV[1]
local priority = ARGV[2]     -- "low", "normal", "high", "critical"
local target_users = ARGV[3] -- JSON 배열 문자열
local content = ARGV[4]      -- 메시지 내용
local sender = ARGV[5]

local timestamp = redis.call('TIME')[1]

-- 우선순위별 채널 접두사
local priority_prefixes = {
    low = "low:",
    normal = "",
    high = "priority:",
    critical = "urgent:"
}

local prefix = priority_prefixes[priority] or ""

-- 사용자 목록 파싱 (간단한 구현)
local users = {}
for user_id in string.gmatch(target_users, '"([^"]+)"') do
    table.insert(users, user_id)
end

local delivered_count = 0

-- 각 대상 사용자에게 메시지 전송
for i, user_id in ipairs(users) do
    -- 사용자 상태 확인
    local user_status = redis.call('HGET', 'user:' .. user_id .. ':info', 'status')

    if user_status and user_status ~= 'offline' then
        -- 온라인 사용자: 즉시 전송
        local channel = prefix .. 'user:' .. user_id .. ':' .. message_type
        local message = string.format('{"type":"%s","priority":"%s","sender":"%s","timestamp":"%s","content":%s}',
                                     message_type, priority, sender, timestamp, content)

        local subscribers = redis.call('PUBLISH', channel, message)
        if subscribers > 0 then
            delivered_count = delivered_count + 1
        end
    else
        -- 오프라인 사용자: 큐에 저장
        local queue_key = 'user:' .. user_id .. ':message_queue'
        local queued_message = string.format('{"type":"%s","priority":"%s","sender":"%s","timestamp":"%s","content":%s,"queued":true}',
                                            message_type, priority, sender, timestamp, content)

        if priority == "critical" then
            redis.call('LPUSH', queue_key, queued_message)  -- 높은 우선순위는 앞쪽에
        else
            redis.call('RPUSH', queue_key, queued_message)  -- 일반 우선순위는 뒤쪽에
        end

        redis.call('EXPIRE', queue_key, 86400 * 7)  -- 7일 후 만료
    end
end

-- 브로드캐스트 채널에도 발행 (모니터링용)
if priority == "critical" then
    redis.call('PUBLISH', 'admin:critical_messages',
               string.format('{"delivered":%d,"total":%d,"type":"%s","timestamp":"%s"}',
                           delivered_count, #users, message_type, timestamp))
end

return {delivered_count, #users - delivered_count}  -- [전송됨, 큐에저장됨]
```

#### 3.2.2 조건부 메시지 필터링

```lua
-- conditional_publisher.lua
local base_channel = ARGV[1]
local message = ARGV[2]
local conditions = ARGV[3]  -- JSON 조건

-- 조건 파싱 (예: {"min_level":5,"tags":["vip","premium"]})
local min_level = string.match(conditions, '"min_level":(%d+)') or 0
local required_tags = {}
for tag in string.gmatch(conditions, '"([^"]+)"') do
    if tag ~= "min_level" and tag ~= "tags" then
        table.insert(required_tags, tag)
    end
end

-- 현재 온라인 사용자들 중 조건에 맞는 사용자 찾기
local online_users = redis.call('SMEMBERS', 'users:online')
local qualified_users = {}

for i, user_id in ipairs(online_users) do
    local user_level = tonumber(redis.call('HGET', 'user:' .. user_id .. ':info', 'level') or 0)
    local user_tags = redis.call('SMEMBERS', 'user:' .. user_id .. ':tags')

    -- 레벨 조건 확인
    if user_level >= tonumber(min_level) then
        -- 태그 조건 확인
        local has_all_tags = true
        for j, required_tag in ipairs(required_tags) do
            local has_tag = false
            for k, user_tag in ipairs(user_tags) do
                if user_tag == required_tag then
                    has_tag = true
                    break
                end
            end
            if not has_tag then
                has_all_tags = false
                break
            end
        end

        if has_all_tags then
            table.insert(qualified_users, user_id)
        end
    end
end

-- 조건에 맞는 사용자들에게 개별 전송
local total_sent = 0
for i, user_id in ipairs(qualified_users) do
    local user_channel = base_channel .. ':' .. user_id
    local sent = redis.call('PUBLISH', user_channel, message)
    total_sent = total_sent + sent
end

-- 통계 저장
local stats_key = 'message_stats:' .. string.sub(base_channel, 1, 20)
redis.call('HINCRBY', stats_key, 'total_sent', total_sent)
redis.call('HINCRBY', stats_key, 'qualified_users', #qualified_users)
redis.call('HINCRBY', stats_key, 'total_online', #online_users)

return {total_sent, #qualified_users, #online_users}
```

---

## 4. 실전 프로젝트 1: 실시간 채팅 시스템

### 4.1 시스템 아키텍처

```bash
# 채널 구조
chat:room:{room_id}:messages     # 채팅 메시지
chat:room:{room_id}:typing       # 타이핑 상태
chat:room:{room_id}:presence     # 사용자 접속 상태
chat:user:{user_id}:notifications # 개인 알림

# 데이터 구조
HSET chat:room:1001 name "일반채팅" created_by 1001 created_at 1647834022
SADD chat:room:1001:members 1001 1002 1003
SET chat:room:1001:member_count 3
LIST chat:room:1001:message_history  # 최근 메시지 히스토리
```

### 4.2 핵심 기능 구현

#### 4.2.1 채팅방 입장/퇴장 시스템

```lua
-- chat_room_join.lua
local room_id = ARGV[1]
local user_id = ARGV[2]
local user_name = ARGV[3]
local timestamp = ARGV[4]

local room_key = 'chat:room:' .. room_id
local members_key = room_key .. ':members'
local presence_channel = room_key .. ':presence'
local messages_channel = room_key .. ':messages'
local online_key = room_key .. ':online'

-- 멤버십 확인
local is_member = redis.call('SISMEMBER', members_key, user_id)
if is_member == 0 then
    return {0, 'NOT_A_MEMBER'}
end

-- 온라인 사용자에 추가
redis.call('SADD', online_key, user_id)
redis.call('EXPIRE', online_key, 3600)  -- 1시간 후 자동 만료

-- 사용자 정보 업데이트
redis.call('HSET', 'user:' .. user_id .. ':session', 'current_room', room_id, 'joined_at', timestamp)

-- 접속 알림 메시지 생성
local join_message = string.format('{"type":"user_joined","user_id":"%s","user_name":"%s","timestamp":"%s"}',
                                  user_id, user_name, timestamp)

-- 접속 상태 채널에 발행
redis.call('PUBLISH', presence_channel, join_message)

-- 시스템 메시지로 채팅방에 발행
local system_message = string.format('{"type":"system","content":"%s님이 입장했습니다.","timestamp":"%s"}',
                                    user_name, timestamp)
redis.call('PUBLISH', messages_channel, system_message)

-- 현재 온라인 사용자 수 반환
local online_count = redis.call('SCARD', online_key)

-- 최근 메시지 히스토리 가져오기 (최근 50개)
local recent_messages = redis.call('LRANGE', room_key .. ':history', 0, 49)

return {1, online_count, recent_messages}
```

#### 4.2.2 메시지 전송 및 저장

```lua
-- send_chat_message.lua
local room_id = ARGV[1]
local user_id = ARGV[2]
local message_content = ARGV[3]
local message_type = ARGV[4]  -- "text", "image", "file", "emoji"
local timestamp = ARGV[5]

local room_key = 'chat:room:' .. room_id
local members_key = room_key .. ':members'
local messages_channel = room_key .. ':messages'
local history_key = room_key .. ':history'
local online_key = room_key .. ':online'

-- 멤버십 및 온라인 상태 확인
local is_member = redis.call('SISMEMBER', members_key, user_id)
local is_online = redis.call('SISMEMBER', online_key, user_id)

if is_member == 0 then
    return {0, 'NOT_A_MEMBER'}
end

if is_online == 0 then
    return {0, 'NOT_ONLINE'}
end

-- 메시지 ID 생성
local message_id = room_id .. '_' .. timestamp .. '_' .. user_id

-- 사용자 정보 가져오기
local user_info = redis.call('HMGET', 'user:' .. user_id .. ':info', 'name', 'avatar')
local user_name = user_info[1] or 'Unknown'
local user_avatar = user_info[2] or ''

-- 메시지 객체 생성
local message = string.format('{"id":"%s","type":"%s","user_id":"%s","user_name":"%s","user_avatar":"%s","content":%s,"timestamp":"%s","room_id":"%s"}',
                             message_id, message_type, user_id, user_name, user_avatar,
                             message_content, timestamp, room_id)

-- 실시간 채널에 발행
local subscribers = redis.call('PUBLISH', messages_channel, message)

-- 메시지 히스토리에 저장
redis.call('LPUSH', history_key, message)
redis.call('LTRIM', history_key, 0, 999)  -- 최근 1000개만 보관

-- 채팅방 통계 업데이트
redis.call('HINCRBY', room_key .. ':stats', 'total_messages', 1)
redis.call('HSET', room_key .. ':stats', 'last_message_at', timestamp, 'last_message_by', user_id)

-- 오프라인 멤버들에게 알림 큐잉
local all_members = redis.call('SMEMBERS', members_key)
local online_members = redis.call('SMEMBERS', online_key)

-- 오프라인 멤버 찾기
local offline_notifications = 0
for i, member_id in ipairs(all_members) do
    if member_id ~= user_id then  -- 자신 제외
        local is_member_online = false
        for j, online_member in ipairs(online_members) do
            if member_id == online_member then
                is_member_online = true
                break
            end
        end

        if not is_member_online then
            -- 오프라인 멤버에게 알림 큐잉
            local notification = string.format('{"type":"missed_message","room_id":"%s","room_name":"%s","sender":"%s","preview":"%.50s","timestamp":"%s"}',
                                              room_id, redis.call('HGET', room_key, 'name') or 'Chat Room',
                                              user_name, message_content, timestamp)

            redis.call('LPUSH', 'user:' .. member_id .. ':notifications', notification)
            redis.call('LTRIM', 'user:' .. member_id .. ':notifications', 0, 99)
            offline_notifications = offline_notifications + 1
        end
    end
end

return {1, subscribers, message_id, offline_notifications}
```

#### 4.2.3 타이핑 상태 관리

```lua
-- typing_status.lua
local room_id = ARGV[1]
local user_id = ARGV[2]
local is_typing = ARGV[3]  -- "true" or "false"
local timestamp = ARGV[4]

local typing_channel = 'chat:room:' .. room_id .. ':typing'
local typing_key = 'chat:room:' .. room_id .. ':typing_users'

local user_name = redis.call('HGET', 'user:' .. user_id .. ':info', 'name') or 'Unknown'

if is_typing == "true" then
    -- 타이핑 시작
    redis.call('SADD', typing_key, user_id)
    redis.call('EXPIRE', typing_key, 10)  -- 10초 후 자동 제거

    local typing_message = string.format('{"type":"typing_start","user_id":"%s","user_name":"%s","timestamp":"%s"}',
                                        user_id, user_name, timestamp)
    redis.call('PUBLISH', typing_channel, typing_message)
else
    -- 타이핑 중지
    redis.call('SREM', typing_key, user_id)

    local stop_message = string.format('{"type":"typing_stop","user_id":"%s","user_name":"%s","timestamp":"%s"}',
                                      user_id, user_name, timestamp)
    redis.call('PUBLISH', typing_channel, stop_message)
end

-- 현재 타이핑 중인 사용자 목록
local typing_users = redis.call('SMEMBERS', typing_key)

return {#typing_users, typing_users}
```

### 4.3 채팅방 관리 기능

#### 4.3.1 채팅방 생성 및 설정

```lua
-- create_chat_room.lua
local room_name = ARGV[1]
local creator_id = ARGV[2]
local room_type = ARGV[3]    -- "public", "private", "group"
local max_members = tonumber(ARGV[4]) or 100
local timestamp = ARGV[5]

-- 고유 룸 ID 생성
local room_counter = redis.call('INCR', 'chat:room_counter')
local room_id = 'room_' .. room_counter

local room_key = 'chat:room:' .. room_id

-- 채팅방 기본 정보 설정
redis.call('HMSET', room_key,
    'name', room_name,
    'type', room_type,
    'creator', creator_id,
    'created_at', timestamp,
    'max_members', max_members,
    'status', 'active'
)

-- 생성자를 첫 번째 멤버로 추가
redis.call('SADD', room_key .. ':members', creator_id)
redis.call('SADD', room_key .. ':admins', creator_id)

-- 통계 초기화
redis.call('HMSET', room_key .. ':stats',
    'total_messages', 0,
    'member_count', 1,
    'created_at', timestamp
)

-- 전역 채팅방 목록에 추가
if room_type == "public" then
    redis.call('ZADD', 'chat:public_rooms', timestamp, room_id)
end

-- 생성자의 채팅방 목록에 추가
redis.call('SADD', 'user:' .. creator_id .. ':chat_rooms', room_id)

-- 채팅방 생성 알림
local creation_message = string.format('{"type":"room_created","room_id":"%s","room_name":"%s","creator":"%s","timestamp":"%s"}',
                                      room_id, room_name, creator_id, timestamp)
redis.call('PUBLISH', 'chat:system:room_events', creation_message)

return {1, room_id, room_name}
```

---

## 5. 실전 프로젝트 2: 실시간 알림 시스템

### 5.1 알림 타입 및 우선순위

```bash
# 알림 타입
# 1. 시스템 알림 (system)
# 2. 사용자 활동 알림 (user_activity)
# 3. 트랜잭션 알림 (transaction)
# 4. 보안 알림 (security)
# 5. 마케팅 알림 (marketing)

# 우선순위 레벨
# 1. critical - 즉시 처리 필요
# 2. high     - 중요
# 3. normal   - 일반
# 4. low      - 낮음
```

### 5.2 지능형 알림 배송 시스템

#### 5.2.1 사용자 선호도 기반 알림

```lua
-- smart_notification_delivery.lua
local notification_type = ARGV[1]
local priority = ARGV[2]
local target_users = ARGV[3]  -- JSON 배열
local title = ARGV[4]
local content = ARGV[5]
local action_url = ARGV[6]
local sender_id = ARGV[7]

local timestamp = redis.call('TIME')[1]
local notification_id = 'notif_' .. timestamp .. '_' .. (sender_id or 'system')

-- 사용자별 알림 처리
local users = {}
for user_id in string.gmatch(target_users, '"([^"]+)"') do
    table.insert(users, user_id)
end

local delivery_stats = {
    delivered = 0,
    queued = 0,
    filtered = 0,
    failed = 0
}

for i, user_id in ipairs(users) do
    -- 사용자 알림 설정 확인
    local user_settings = redis.call('HMGET', 'user:' .. user_id .. ':notification_settings',
                                    notification_type, 'do_not_disturb', 'quiet_hours_start', 'quiet_hours_end')

    local type_enabled = user_settings[1] ~= "false"
    local dnd_mode = user_settings[2] == "true"
    local quiet_start = tonumber(user_settings[3]) or 22  -- 22시
    local quiet_end = tonumber(user_settings[4]) or 8     -- 8시

    -- 현재 시간 확인 (조용한 시간대 체크)
    local current_hour = tonumber(os.date("%H"))
    local is_quiet_time = false

    if quiet_start > quiet_end then  -- 22시 ~ 8시 같은 경우
        is_quiet_time = current_hour >= quiet_start or current_hour < quiet_end
    else  -- 8시 ~ 22시 같은 경우
        is_quiet_time = current_hour >= quiet_start and current_hour < quiet_end
    end

    -- 알림 필터링 로직
    if not type_enabled then
        delivery_stats.filtered = delivery_stats.filtered + 1
    elseif dnd_mode and priority ~= "critical" then
        delivery_stats.filtered = delivery_stats.filtered + 1
    elseif is_quiet_time and priority == "low" then
        delivery_stats.queued = delivery_stats.queued + 1
        -- 조용한 시간대에는 낮은 우선순위 알림을 큐에 저장
        local queue_key = 'user:' .. user_id .. ':notification_queue'
        local queued_notification = string.format('{"id":"%s","type":"%s","priority":"%s","title":%s,"content":%s,"action_url":"%s","timestamp":"%s","queued_reason":"quiet_hours"}',
                                                 notification_id, notification_type, priority, title, content, action_url, timestamp)
        redis.call('RPUSH', queue_key, queued_notification)
        redis.call('EXPIRE', queue_key, 86400 * 3)  -- 3일 후 만료
    else
        -- 즉시 전송
        local user_status = redis.call('HGET', 'user:' .. user_id .. ':info', 'status')

        if user_status == "online" then
            -- 실시간 알림 채널에 전송
            local channel = 'user:' .. user_id .. ':notifications:' .. priority
            local notification = string.format('{"id":"%s","type":"%s","priority":"%s","title":%s,"content":%s,"action_url":"%s","timestamp":"%s","real_time":true}',
                                              notification_id, notification_type, priority, title, content, action_url, timestamp)

            local subscribers = redis.call('PUBLISH', channel, notification)
            if subscribers > 0 then
                delivery_stats.delivered = delivery_stats.delivered + 1

                -- 읽지 않은 알림 카운터 증가
                redis.call('HINCRBY', 'user:' .. user_id .. ':notification_stats', 'unread_count', 1)
                redis.call('HINCRBY', 'user:' .. user_id .. ':notification_stats', 'unread_' .. priority, 1)
            else
                delivery_stats.failed = delivery_stats.failed + 1
            end
        else
            -- 오프라인 사용자: 알림 저장소에 저장
            local storage_key = 'user:' .. user_id .. ':notifications:stored'
            local stored_notification = string.format('{"id":"%s","type":"%s","priority":"%s","title":%s,"content":%s,"action_url":"%s","timestamp":"%s","stored":true}',
                                                     notification_id, notification_type, priority, title, content, action_url, timestamp)

            if priority == "critical" then
                redis.call('LPUSH', storage_key, stored_notification)  -- 높은 우선순위는 앞쪽에
            else
                redis.call('RPUSH', storage_key, stored_notification)  -- 일반 우선순위는 뒤쪽에
            end

            redis.call('LTRIM', storage_key, 0, 999)  -- 최대 1000개 저장
            redis.call('EXPIRE', storage_key, 86400 * 30)  -- 30일 후 만료

            delivery_stats.queued = delivery_stats.queued + 1

            -- 읽지 않은 알림 카운터 증가
            redis.call('HINCRBY', 'user:' .. user_id .. ':notification_stats', 'unread_count', 1)
            redis.call('HINCRBY', 'user:' .. user_id .. ':notification_stats', 'unread_' .. priority, 1)
        end
    end
end

-- 전체 알림 통계 업데이트
redis.call('HINCRBY', 'notification_stats:global', 'total_sent', delivery_stats.delivered + delivery_stats.queued)
redis.call('HINCRBY', 'notification_stats:global', 'delivered', delivery_stats.delivered)
redis.call('HINCRBY', 'notification_stats:global', 'queued', delivery_stats.queued)
redis.call('HINCRBY', 'notification_stats:global', 'filtered', delivery_stats.filtered)

-- 알림 타입별 통계
redis.call('HINCRBY', 'notification_stats:' .. notification_type, 'total', #users)
redis.call('HINCRBY', 'notification_stats:' .. notification_type, 'delivered', delivery_stats.delivered)

return {notification_id, delivery_stats}
```

#### 5.2.2 알림 집계 및 다이제스트

```lua
-- notification_digest.lua
local user_id = ARGV[1]
local digest_type = ARGV[2]  -- "hourly", "daily", "weekly"
local timestamp = ARGV[3]

local digest_key = 'user:' .. user_id .. ':digest:' .. digest_type
local notifications_key = 'user:' .. user_id .. ':notifications:stored'

-- 시간 범위 계산
local time_ranges = {
    hourly = 3600,      -- 1시간
    daily = 86400,      -- 1일
    weekly = 604800     -- 1주일
}

local time_range = time_ranges[digest_type] or 86400
local start_time = tonumber(timestamp) - time_range

-- 해당 기간의 알림들 수집
local all_notifications = redis.call('LRANGE', notifications_key, 0, -1)
local period_notifications = {}
local notifications_by_type = {}

for i, notification_json in ipairs(all_notifications) do
    local notif_timestamp = string.match(notification_json, '"timestamp":"(%d+)"')
    if notif_timestamp and tonumber(notif_timestamp) >= start_time then
        table.insert(period_notifications, notification_json)

        -- 타입별 그룹화
        local notif_type = string.match(notification_json, '"type":"([^"]+)"')
        if notif_type then
            if not notifications_by_type[notif_type] then
                notifications_by_type[notif_type] = {}
            end
            table.insert(notifications_by_type[notif_type], notification_json)
        end
    end
end

-- 다이제스트 생성
local digest_summary = {
    total_count = #period_notifications,
    by_type = {},
    top_notifications = {},
    period = digest_type,
    start_time = start_time,
    end_time = timestamp
}

-- 타입별 요약
for notif_type, notifications in pairs(notifications_by_type) do
    digest_summary.by_type[notif_type] = {
        count = #notifications,
        latest = notifications[#notifications]  -- 가장 최근 알림
    }
end

-- 중요한 알림들 선별 (critical, high 우선순위)
for i, notification_json in ipairs(period_notifications) do
    local priority = string.match(notification_json, '"priority":"([^"]+)"')
    if priority == "critical" or priority == "high" then
        table.insert(digest_summary.top_notifications, notification_json)
    end
end

-- 다이제스트가 의미 있는 경우에만 전송
if digest_summary.total_count > 0 then
    local digest_message = string.format('{"type":"notification_digest","period":"%s","summary":%s,"user_id":"%s","timestamp":"%s"}',
                                        digest_type,
                                        string.format('{"total":%d,"types":%d,"important":%d}',
                                                    digest_summary.total_count,
                                                    table_count(digest_summary.by_type),
                                                    #digest_summary.top_notifications),
                                        user_id, timestamp)

    -- 다이제스트 채널에 발행
    redis.call('PUBLISH', 'user:' .. user_id .. ':notifications:digest', digest_message)

    -- 다이제스트 히스토리에 저장
    redis.call('SETEX', digest_key .. ':' .. timestamp, 86400 * 7, digest_message)

    return {1, digest_summary.total_count, table_count(digest_summary.by_type)}
else
    return {0, 0, 0}
end

-- 테이블 크기 계산 함수
function table_count(t)
    local count = 0
    for _ in pairs(t) do count = count + 1 end
    return count
end
```

---

## 6. 스트림 기반 메시징

### 6.1 Redis Streams 기본 개념

Redis 5.0부터 도입된 Streams는 **영속적인 메시지 큐**와 **이벤트 소싱** 패턴을 지원합니다.

#### 6.1.1 기본 스트림 명령어

```bash
# 스트림에 메시지 추가
127.0.0.1:6379> XADD events:user_actions * user_id 1001 action login timestamp 1647834022
"1647834022000-0"

127.0.0.1:6379> XADD events:user_actions * user_id 1002 action logout timestamp 1647834123
"1647834123000-0"

# 스트림 메시지 읽기
127.0.0.1:6379> XREAD STREAMS events:user_actions 0
1) 1) "events:user_actions"
   2) 1) 1) "1647834022000-0"
         2) 1) "user_id"
            2) "1001"
            3) "action"
            4) "login"
            5) "timestamp"
            6) "1647834022"

# 스트림 길이 확인
127.0.0.1:6379> XLEN events:user_actions
(integer) 2

# 스트림 정보 확인
127.0.0.1:6379> XINFO STREAM events:user_actions
```

#### 6.1.2 컨슈머 그룹 생성

```bash
# 컨슈머 그룹 생성
127.0.0.1:6379> XGROUP CREATE events:user_actions analytics_team $ MKSTREAM
OK

127.0.0.1:6379> XGROUP CREATE events:user_actions notification_service $ MKSTREAM
OK

# 그룹별로 메시지 읽기
127.0.0.1:6379> XREADGROUP GROUP analytics_team worker1 COUNT 1 STREAMS events:user_actions >
1) 1) "events:user_actions"
   2) 1) 1) "1647834022000-0"
         2) 1) "user_id"
            2) "1001"
            3) "action"
            4) "login"

# 메시지 처리 완료 확인
127.0.0.1:6379> XACK events:user_actions analytics_team 1647834022000-0
(integer) 1
```

### 6.2 이벤트 소싱 패턴 구현

#### 6.2.1 사용자 활동 이벤트 스트림

```lua
-- user_event_stream.lua
local user_id = ARGV[1]
local event_type = ARGV[2]
local event_data = ARGV[3]  -- JSON 형태
local timestamp = ARGV[4]
local session_id = ARGV[5]

-- 이벤트 스트림에 추가
local stream_key = 'events:user:' .. user_id
local event_id = redis.call('XADD', stream_key, '*',
    'user_id', user_id,
    'event_type', event_type,
    'event_data', event_data,
    'timestamp', timestamp,
    'session_id', session_id
)

-- 전역 이벤트 스트림에도 추가
local global_stream = 'events:all_users'
redis.call('XADD', global_stream, '*',
    'user_id', user_id,
    'event_type', event_type,
    'event_data', event_data,
    'timestamp', timestamp,
    'session_id', session_id
)

-- 이벤트 타입별 스트림에도 추가
local type_stream = 'events:type:' .. event_type
redis.call('XADD', type_stream, '*',
    'user_id', user_id,
    'event_data', event_data,
    'timestamp', timestamp,
    'session_id', session_id
)

-- 스트림 크기 제한 (최대 10,000개 유지)
redis.call('XTRIM', stream_key, 'MAXLEN', '~', 10000)
redis.call('XTRIM', type_stream, 'MAXLEN', '~', 50000)

-- 실시간 알림을 위한 Pub/Sub도 함께 사용
local notification_channel = 'user:' .. user_id .. ':events'
local real_time_message = string.format('{"event_id":"%s","type":"%s","data":%s,"timestamp":"%s"}',
                                       event_id, event_type, event_data, timestamp)
redis.call('PUBLISH', notification_channel, real_time_message)

-- 사용자 활동 통계 업데이트
redis.call('HINCRBY', 'user:' .. user_id .. ':activity_stats', event_type, 1)
redis.call('HINCRBY', 'user:' .. user_id .. ':activity_stats', 'total_events', 1)
redis.call('HSET', 'user:' .. user_id .. ':activity_stats', 'last_event_at', timestamp)

return {event_id, stream_key, type_stream}
```

#### 6.2.2 주문 처리 이벤트 스트림

```lua
-- order_event_stream.lua
local order_id = ARGV[1]
local event_type = ARGV[2]  -- "created", "paid", "shipped", "delivered", "cancelled"
local event_data = ARGV[3]
local user_id = ARGV[4]
local timestamp = ARGV[5]

local order_stream = 'events:order:' .. order_id
local user_orders_stream = 'events:user:' .. user_id .. ':orders'
local global_orders_stream = 'events:orders:all'

-- 주문별 이벤트 스트림
local event_id = redis.call('XADD', order_stream, '*',
    'order_id', order_id,
    'event_type', event_type,
    'event_data', event_data,
    'user_id', user_id,
    'timestamp', timestamp
)

-- 사용자별 주문 이벤트 스트림
redis.call('XADD', user_orders_stream, '*',
    'order_id', order_id,
    'event_type', event_type,
    'event_data', event_data,
    'timestamp', timestamp
)

-- 전역 주문 이벤트 스트림
redis.call('XADD', global_orders_stream, '*',
    'order_id', order_id,
    'event_type', event_type,
    'event_data', event_data,
    'user_id', user_id,
    'timestamp', timestamp
)

-- 주문 상태 업데이트
if event_type == "created" then
    redis.call('HSET', 'order:' .. order_id, 'status', 'pending', 'created_at', timestamp)
elseif event_type == "paid" then
    redis.call('HSET', 'order:' .. order_id, 'status', 'paid', 'paid_at', timestamp)
elseif event_type == "shipped" then
    redis.call('HSET', 'order:' .. order_id, 'status', 'shipped', 'shipped_at', timestamp)
elseif event_type == "delivered" then
    redis.call('HSET', 'order:' .. order_id, 'status', 'delivered', 'delivered_at', timestamp)
elseif event_type == "cancelled" then
    redis.call('HSET', 'order:' .. order_id, 'status', 'cancelled', 'cancelled_at', timestamp)
end

-- 상태 변경 알림
local status_channel = 'order:' .. order_id .. ':status_updates'
local status_message = string.format('{"order_id":"%s","status":"%s","timestamp":"%s","user_id":"%s"}',
                                    order_id, event_type, timestamp, user_id)
redis.call('PUBLISH', status_channel, status_message)

-- 사용자 알림
local user_notification_channel = 'user:' .. user_id .. ':order_updates'
redis.call('PUBLISH', user_notification_channel, status_message)

return {event_id, event_type, order_stream}
```

---

## 7. 성능 최적화

### 7.1 채널 및 패턴 최적화

#### 7.1.1 채널 네이밍 최적화

```bash
# 비효율적인 패턴 (피해야 할 것들)
user:1001:notifications:email:marketing:campaign:2024:march
app:prod:service:auth:logs:error:database:connection:timeout

# 효율적인 패턴 (권장)
user:1001:notif:email
app:auth:error
system:alert:db

# 인덱싱 고려사항
# 1. 자주 사용되는 부분을 앞쪽에 배치
# 2. 와일드카드 패턴을 고려한 구조
# 3. 계층 구조를 일관성 있게 유지
```

#### 7.1.2 구독자 관리 최적화

```lua
-- subscription_manager.lua
local action = ARGV[1]  -- "subscribe", "unsubscribe", "list"
local user_id = ARGV[2]
local channels = ARGV[3]  -- JSON 배열

local user_subs_key = 'user:' .. user_id .. ':subscriptions'

if action == "subscribe" then
    local channel_list = {}
    for channel in string.gmatch(channels, '"([^"]+)"') do
        table.insert(channel_list, channel)
        redis.call('SADD', user_subs_key, channel)
    end

    -- 구독 수 제한 (최대 100개)
    local total_subs = redis.call('SCARD', user_subs_key)
    if total_subs > 100 then
        return {0, 'TOO_MANY_SUBSCRIPTIONS', total_subs}
    end

    -- 구독 히스토리 저장
    local timestamp = redis.call('TIME')[1]
    for i, channel in ipairs(channel_list) do
        redis.call('ZADD', 'user:' .. user_id .. ':subscription_history', timestamp, 'sub:' .. channel)
    end

    return {1, 'SUBSCRIBED', #channel_list, total_subs}

elseif action == "unsubscribe" then
    local channel_list = {}
    for channel in string.gmatch(channels, '"([^"]+)"') do
        table.insert(channel_list, channel)
        redis.call('SREM', user_subs_key, channel)
    end

    -- 구독 해제 히스토리
    local timestamp = redis.call('TIME')[1]
    for i, channel in ipairs(channel_list) do
        redis.call('ZADD', 'user:' .. user_id .. ':subscription_history', timestamp, 'unsub:' .. channel)
    end

    local remaining_subs = redis.call('SCARD', user_subs_key)
    return {1, 'UNSUBSCRIBED', #channel_list, remaining_subs}

elseif action == "list" then
    local user_channels = redis.call('SMEMBERS', user_subs_key)
    return {1, 'LISTED', user_channels}
end

return {0, 'INVALID_ACTION'}
```

### 7.2 메시지 크기 최적화

#### 7.2.1 메시지 압축 및 최적화

```lua
-- message_optimizer.lua
local message_type = ARGV[1]
local raw_message = ARGV[2]
local compression_level = tonumber(ARGV[3]) or 1  -- 1: 기본, 2: 중간, 3: 최대

-- 메시지 크기 확인
local message_size = string.len(raw_message)

-- 크기에 따른 처리 전략
if message_size < 1000 then
    -- 작은 메시지: 그대로 전송
    return {1, raw_message, message_size, 'no_compression'}

elseif message_size < 10000 then
    -- 중간 크기: JSON 압축 최적화
    local optimized = raw_message

    -- 불필요한 공백 제거
    optimized = string.gsub(optimized, '%s+', ' ')
    optimized = string.gsub(optimized, ': ', ':')
    optimized = string.gsub(optimized, ', ', ',')

    local new_size = string.len(optimized)
    local compression_ratio = new_size / message_size

    return {1, optimized, new_size, string.format('json_optimized_%.2f', compression_ratio)}

else
    -- 큰 메시지: 참조 방식 사용
    local message_id = 'msg_' .. redis.call('TIME')[1] .. '_' .. redis.call('TIME')[2]
    local storage_key = 'message_storage:' .. message_id

    -- 메시지를 별도 저장소에 저장
    redis.call('SETEX', storage_key, 3600, raw_message)  -- 1시간 TTL

    -- 참조 메시지 생성
    local reference_message = string.format('{"type":"message_reference","id":"%s","size":%d,"expires":3600}',
                                           message_id, message_size)

    return {1, reference_message, string.len(reference_message), 'reference_storage'}
end
```

### 7.3 배치 처리 최적화

#### 7.3.1 메시지 배치 발행

```lua
-- batch_publish.lua
local batch_messages = ARGV[1]  -- JSON 배열 형태의 메시지들
local max_batch_size = tonumber(ARGV[2]) or 100

-- JSON 파싱 (간단한 구현)
local messages = {}
for message in string.gmatch(batch_messages, '{[^}]+}') do
    table.insert(messages, message)
end

-- 배치 크기 제한
if #messages > max_batch_size then
    return {0, 'BATCH_TOO_LARGE', #messages, max_batch_size}
end

local results = {}
local total_subscribers = 0

-- 각 메시지 처리
for i, message_json in ipairs(messages) do
    local channel = string.match(message_json, '"channel":"([^"]+)"')
    local content = string.match(message_json, '"content":"([^"]+)"')

    if channel and content then
        local subscribers = redis.call('PUBLISH', channel, content)
        total_subscribers = total_subscribers + subscribers

        table.insert(results, {
            channel = channel,
            subscribers = subscribers,
            status = 'published'
        })
    else
        table.insert(results, {
            message = message_json,
            status = 'invalid_format'
        })
    end
end

-- 배치 통계 저장
local timestamp = redis.call('TIME')[1]
redis.call('HINCRBY', 'batch_stats:' .. string.sub(timestamp, 1, 8), 'total_batches', 1)
redis.call('HINCRBY', 'batch_stats:' .. string.sub(timestamp, 1, 8), 'total_messages', #messages)
redis.call('HINCRBY', 'batch_stats:' .. string.sub(timestamp, 1, 8), 'total_subscribers', total_subscribers)

return {1, #messages, total_subscribers, results}
```

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: 구독자 없는 채널에 메시지 발행하는 실수

**상황**: 신입 개발자가 실시간 알림 기능을 구현했는데, 사용자가 알림을 받지 못한다고 불만 제기

```python
# ❌ 주니어 개발자가 작성한 코드
import redis

r = redis.Redis()

# 주문 완료 시 알림 발송
def notify_order_complete(user_id, order_id):
    channel = f"user:{user_id}:notifications"
    message = f"주문 #{order_id}가 완료되었습니다"

    # 메시지 발행
    subscribers = r.publish(channel, message)
    print(f"알림 전송 완료: {subscribers}명에게 전달됨")

    # 문제: subscribers가 0이면 메시지가 사라짐!
    # 사용자가 구독 중이 아니면 알림을 못 받음
```

**문제점**:
- 문제 1: Pub/Sub은 fire-and-forget 방식이라 구독자가 없으면 메시지 손실
- 문제 2: 사용자가 오프라인이거나 앱을 켜지 않으면 알림 못 받음
- 왜 이 문제가 발생하는가: Pub/Sub의 특성을 이해하지 못하고 메시지 큐처럼 사용함

**해결책**:
```python
# ✅ 올바른 코드 - 하이브리드 방식
import redis
import json
from datetime import datetime

r = redis.Redis()

def notify_order_complete(user_id, order_id):
    channel = f"user:{user_id}:notifications"
    message_data = {
        "type": "order_complete",
        "order_id": order_id,
        "message": f"주문 #{order_id}가 완료되었습니다",
        "timestamp": datetime.now().isoformat()
    }
    message = json.dumps(message_data)

    # 1. 실시간 발송 시도 (온라인 사용자용)
    subscribers = r.publish(channel, message)

    # 2. 구독자가 없으면 저장소에 보관 (오프라인 사용자용)
    if subscribers == 0:
        # List에 저장 (사용자가 다음 로그인 시 확인)
        queue_key = f"user:{user_id}:notification_queue"
        r.lpush(queue_key, message)
        r.ltrim(queue_key, 0, 99)  # 최근 100개만 보관
        r.expire(queue_key, 86400 * 7)  # 7일 후 자동 삭제
        print(f"오프라인 사용자: 알림 큐에 저장됨")
    else:
        print(f"온라인 사용자: {subscribers}명에게 즉시 전달됨")

    # 3. 통계 기록
    r.hincrby("notification_stats", "total_sent", 1)
    r.hincrby("notification_stats", "realtime_delivered" if subscribers > 0 else "queued", 1)

# 사용자 로그인 시 큐에 저장된 알림 확인
def get_pending_notifications(user_id):
    queue_key = f"user:{user_id}:notification_queue"
    notifications = r.lrange(queue_key, 0, -1)
    r.delete(queue_key)  # 확인 후 삭제
    return [json.loads(n) for n in notifications]
```

**배운 점**:
- 💡 팁 1: Pub/Sub은 실시간 통신용, 메시지 보장이 필요하면 List/Stream과 함께 사용
- 💡 팁 2: PUBLISH 반환값(구독자 수)을 항상 확인하여 전송 여부 검증
- 💡 팁 3: 중요한 알림은 Streams나 영속적 저장소에 백업 필수

---

### 시나리오 2: 패턴 구독 시 성능 저하

**상황**: 관리자 대시보드에서 모든 사용자 활동을 모니터링하려고 패턴 구독을 사용했는데 시스템이 느려짐

```python
# ❌ 주니어 개발자가 작성한 코드
import redis

r = redis.Redis()
pubsub = r.pubsub()

# 모든 사용자 채널을 구독하려고 시도
pubsub.psubscribe('user:*')  # 10만 개 채널 매칭!

# 메시지 처리
for message in pubsub.listen():
    if message['type'] == 'pmessage':
        # 문제: 초당 10만 개 메시지 발생 시 처리 불가
        process_message(message['data'])
        save_to_database(message)  # DB에 모두 저장하려니 느림!
```

**문제점**:
- 문제 1: user:*는 모든 사용자 채널과 매칭되어 메시지 폭주
- 문제 2: 메시지 처리 중 DB 저장으로 병목 발생, 메시지 유실
- 문제 3: CPU 사용률 100%, Redis 응답 시간 증가
- 왜 이 문제가 발생하는가: 패턴 구독의 범위를 제한하지 않고 무분별하게 사용

**해결책**:
```python
# ✅ 올바른 코드 - 선택적 구독 + 비동기 처리
import redis
import json
from queue import Queue
from threading import Thread

r = redis.Redis()

# 1. 구독 범위를 제한
def subscribe_critical_events_only():
    pubsub = r.pubsub()

    # 중요한 이벤트만 선별적으로 구독
    patterns = [
        'user:*:critical',      # 중요 알림만
        'system:*:error',       # 시스템 에러만
        'transaction:*:failed'  # 실패한 거래만
    ]

    pubsub.psubscribe(*patterns)
    return pubsub

# 2. 비동기 처리 큐 사용
message_queue = Queue(maxsize=10000)

def message_listener():
    pubsub = subscribe_critical_events_only()

    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            # 빠르게 큐에 넣고 다음 메시지 처리
            try:
                message_queue.put_nowait({
                    'channel': message['channel'],
                    'data': message['data']
                })
            except:
                print("큐가 가득 참: 메시지 드롭")

# 3. 별도 스레드에서 DB 저장 (느린 작업 분리)
def message_processor():
    while True:
        msg = message_queue.get()
        try:
            # 배치로 모아서 한번에 저장 (성능 향상)
            batch = [msg]
            while not message_queue.empty() and len(batch) < 100:
                batch.append(message_queue.get_nowait())

            # DB에 배치 저장
            save_batch_to_database(batch)
        except Exception as e:
            print(f"처리 에러: {e}")

# 스레드 시작
Thread(target=message_listener, daemon=True).start()
Thread(target=message_processor, daemon=True).start()

# 4. 대시보드는 Redis에서 요약 통계만 조회
def get_dashboard_stats():
    return {
        "total_users_online": r.scard("users:online"),
        "critical_alerts": r.get("stats:critical_alerts") or 0,
        "error_count": r.get("stats:errors:count") or 0
    }
```

**배운 점**:
- 💡 팁 1: 패턴 구독은 필요한 최소한만 사용, 와일드카드 범위 제한
- 💡 팁 2: 메시지 처리는 비동기로, 느린 작업(DB 저장)은 별도 스레드에서
- 💡 팁 3: 실시간 대시보드는 집계된 통계만 보여주고, 상세 로그는 별도 저장

---

### 시나리오 3: Pub/Sub과 Streams 선택 실수

**상황**: 주문 처리 시스템을 구축하는데 Pub/Sub을 사용했더니 일부 주문이 누락됨

```python
# ❌ 주니어 개발자가 작성한 코드
import redis

r = redis.Redis()

# 주문 생성
def create_order(order_data):
    order_id = generate_order_id()

    # 주문 정보 저장
    r.hset(f"order:{order_id}", mapping=order_data)

    # 주문 처리 이벤트 발행
    r.publish("orders:new", json.dumps({
        "order_id": order_id,
        "customer_id": order_data['customer_id']
    }))

    # 문제: 주문 처리 서비스가 재시작 중이면 메시지 손실!

# 주문 처리 서비스
def order_processor():
    pubsub = r.pubsub()
    pubsub.subscribe("orders:new")

    for message in pubsub.listen():
        if message['type'] == 'message':
            process_order(message['data'])
            # 문제: 처리 중 에러 발생 시 재시도 불가
```

**문제점**:
- 문제 1: 구독자가 없거나 재시작 중이면 주문 메시지 손실
- 문제 2: 처리 실패 시 재시도 메커니즘 없음
- 문제 3: 여러 워커로 분산 처리 불가능 (모든 워커가 동일 메시지 수신)
- 왜 이 문제가 발생하는가: 메시지 보장이 필요한 상황에서 Pub/Sub 선택

**해결책**:
```python
# ✅ 올바른 코드 - Streams + Consumer Group 사용
import redis
import json
from datetime import datetime

r = redis.Redis()

# 주문 생성
def create_order(order_data):
    order_id = generate_order_id()

    # 1. 주문 정보 저장
    r.hset(f"order:{order_id}", mapping=order_data)

    # 2. Streams에 이벤트 추가 (영속성 보장)
    stream_id = r.xadd(
        "orders:stream",
        {
            "order_id": order_id,
            "customer_id": order_data['customer_id'],
            "amount": order_data['amount'],
            "timestamp": datetime.now().isoformat()
        }
    )

    print(f"주문 이벤트 저장됨: {stream_id}")
    return order_id

# Consumer Group 생성 (최초 1회)
try:
    r.xgroup_create("orders:stream", "order_processors", id='0', mkstream=True)
except redis.ResponseError as e:
    if "BUSYGROUP" not in str(e):
        raise

# 주문 처리 워커 (여러 인스턴스 실행 가능)
def order_processor_worker(worker_name):
    while True:
        try:
            # 1. Consumer Group으로 메시지 읽기 (자동 분산)
            messages = r.xreadgroup(
                groupname="order_processors",
                consumername=worker_name,
                streams={"orders:stream": '>'},
                count=10,
                block=5000  # 5초 대기
            )

            for stream, message_list in messages:
                for message_id, data in message_list:
                    try:
                        # 2. 주문 처리
                        order_id = data[b'order_id'].decode()
                        process_order(order_id)

                        # 3. 처리 완료 확인 (ACK)
                        r.xack("orders:stream", "order_processors", message_id)
                        print(f"{worker_name}: 주문 {order_id} 처리 완료")

                    except Exception as e:
                        # 처리 실패 시 ACK 안 함 -> 재시도 가능
                        print(f"처리 에러: {e}, 메시지 {message_id} 재시도 대기")

        except Exception as e:
            print(f"워커 에러: {e}")
            time.sleep(1)

# 3. 미처리 메시지 재시도 (장애 복구)
def retry_pending_messages():
    # 10분 이상 처리 안 된 메시지 재할당
    pending = r.xpending_range(
        "orders:stream",
        "order_processors",
        min='-',
        max='+',
        count=100
    )

    for msg in pending:
        if msg['time_since_delivered'] > 600000:  # 10분
            # 다른 워커에게 재할당
            r.xclaim(
                "orders:stream",
                "order_processors",
                "recovery_worker",
                min_idle_time=600000,
                message_ids=[msg['message_id']]
            )

# 여러 워커 실행
import threading
threading.Thread(target=order_processor_worker, args=("worker1",), daemon=True).start()
threading.Thread(target=order_processor_worker, args=("worker2",), daemon=True).start()
```

**배운 점**:
- 💡 팁 1: 메시지 손실 불가한 경우 → Streams 사용 (주문, 결제, 중요 이벤트)
- 💡 팁 2: 실시간만 필요한 경우 → Pub/Sub 사용 (채팅, 알림, 모니터링)
- 💡 팁 3: Consumer Group으로 여러 워커 분산 처리 + 자동 재시도

---

### 시나리오 4: 채널 네이밍 일관성 부족으로 인한 혼란

**상황**: 여러 개발자가 협업하는 프로젝트에서 채널명이 제각각이라 메시지가 엉뚱한 곳으로 가거나 못 받음

```python
# ❌ 주니어 개발자들이 작성한 일관성 없는 코드

# 개발자 A
r.publish("UserNotification:1001", "메시지")

# 개발자 B
r.publish("user_notifications_1001", "메시지")

# 개발자 C
r.publish("notifications:user:1001", "메시지")

# 개발자 D
r.publish("1001:user:notify", "메시지")

# 문제: 구독자는 어떤 채널명을 구독해야 할지 모름!
```

**문제점**:
- 문제 1: 네이밍 컨벤션이 없어 채널명이 중구난방
- 문제 2: 패턴 구독 시 일부 채널만 매칭되어 메시지 누락
- 문제 3: 디버깅 시 어떤 채널을 확인해야 할지 혼란
- 왜 이 문제가 발생하는가: 팀 차원의 네이밍 규칙 부재

**해결책**:
```python
# ✅ 올바른 코드 - 채널 네이밍 규칙 + 헬퍼 클래스

# 1. 채널 네이밍 규칙 문서화
"""
채널 네이밍 컨벤션:
- 형식: <도메인>:<리소스>:<ID>:<이벤트타입>
- 소문자 + 콜론(:) 구분자
- 계층 구조: 왼쪽이 상위, 오른쪽이 하위
- 예시:
  - user:1001:notifications
  - chat:room:general:messages
  - order:12345:status_updates
  - system:alerts:critical
"""

# 2. 채널 빌더 클래스 (일관성 보장)
class RedisChannelBuilder:
    """Redis 채널명을 일관되게 생성하는 헬퍼 클래스"""

    @staticmethod
    def user_notifications(user_id):
        return f"user:{user_id}:notifications"

    @staticmethod
    def user_messages(user_id):
        return f"user:{user_id}:messages"

    @staticmethod
    def chat_room(room_id):
        return f"chat:room:{room_id}:messages"

    @staticmethod
    def chat_room_typing(room_id):
        return f"chat:room:{room_id}:typing"

    @staticmethod
    def order_status(order_id):
        return f"order:{order_id}:status"

    @staticmethod
    def system_alerts(level):
        """level: critical, warning, info"""
        return f"system:alerts:{level}"

    # 패턴 생성
    @staticmethod
    def all_user_notifications():
        return "user:*:notifications"

    @staticmethod
    def all_chat_rooms():
        return "chat:room:*:messages"

# 3. 사용 예시
channels = RedisChannelBuilder()

# 메시지 발행
r.publish(channels.user_notifications(1001), "새 알림이 있습니다")
r.publish(channels.chat_room("general"), "안녕하세요!")
r.publish(channels.system_alerts("critical"), "디스크 용량 부족")

# 구독
pubsub = r.pubsub()
pubsub.subscribe(channels.user_notifications(1001))
pubsub.psubscribe(channels.all_chat_rooms())

# 4. 채널 검증 (배포 전 체크)
def validate_channel_name(channel):
    """채널명이 규칙을 따르는지 검증"""
    parts = channel.split(':')

    if len(parts) < 2:
        raise ValueError(f"잘못된 채널명: {channel}. 최소 2개 계층 필요")

    if not channel.islower():
        raise ValueError(f"잘못된 채널명: {channel}. 소문자만 허용")

    if channel != channel.replace('_', ':'):
        raise ValueError(f"잘못된 채널명: {channel}. 언더스코어(_) 대신 콜론(:) 사용")

    return True

# 테스트
try:
    validate_channel_name("UserNotification:1001")  # 에러: 대문자
except ValueError as e:
    print(e)

validate_channel_name(channels.user_notifications(1001))  # OK

# 5. 팀 공유용 채널 문서 자동 생성
def generate_channel_docs():
    """사용 가능한 모든 채널 목록 생성"""
    docs = []
    for attr in dir(RedisChannelBuilder):
        if not attr.startswith('_'):
            method = getattr(RedisChannelBuilder, attr)
            if callable(method):
                docs.append(f"- {attr}: {method.__doc__ or '설명 없음'}")

    return "\n".join(docs)

print(generate_channel_docs())
```

**배운 점**:
- 💡 팁 1: 프로젝트 시작 시 채널 네이밍 규칙을 팀과 합의하고 문서화
- 💡 팁 2: 헬퍼 클래스로 채널명 생성 로직을 중앙화하여 일관성 유지
- 💡 팁 3: CI/CD에 채널명 검증 단계 추가하여 규칙 위반 방지

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용 (5-7개)

<details>
<summary><strong>1. Redis Pub/Sub이 무엇이고, 어떤 상황에서 사용하나요?</strong></summary>

**모범 답안 포인트**
- 포인트 1: Publisher와 Subscriber 간 메시징 패턴으로, 발행자가 메시지를 보내면 구독자가 실시간으로 수신
- 포인트 2: 채널 기반 통신으로 특정 주제에 관심 있는 구독자만 메시지를 받음
- 포인트 3: 실시간 알림, 채팅, 이벤트 브로드캐스팅 등에 사용

**예시 답변**
> "Redis Pub/Sub은 발행-구독 패턴을 구현한 메시징 시스템입니다. 유튜브 구독과 비슷하게, Publisher가 특정 채널에 메시지를 발행하면 해당 채널을 구독한 Subscriber들이 실시간으로 메시지를 받습니다. 실시간 채팅, 알림 시스템, 마이크로서비스 간 이벤트 통신 등에 주로 사용됩니다."

**꼬리 질문**
- Q: Pub/Sub과 메시지 큐의 차이는 무엇인가요?
- A: Pub/Sub은 1:N 브로드캐스트 방식이고, 메시지 큐는 1:1 방식입니다. 또한 Pub/Sub은 메시지를 저장하지 않지만(fire-and-forget), 메시지 큐는 영속성을 보장합니다.

**실무 연관**
- 이 개념이 실무에서 어떻게 활용되는지: 쿠팡의 주문 상태 변경 알림, 카카오톡의 실시간 메시지 전송 등에 활용됩니다.

</details>

<details>
<summary><strong>2. SUBSCRIBE, PUBLISH, PSUBSCRIBE 명령어의 차이를 설명하세요.</strong></summary>

**모범 답안 포인트**
- 포인트 1: SUBSCRIBE는 정확한 채널명으로 구독
- 포인트 2: PUBLISH는 특정 채널에 메시지 발행
- 포인트 3: PSUBSCRIBE는 와일드카드 패턴으로 여러 채널 구독

**예시 답변**
> "SUBSCRIBE는 'user:1001:notifications'처럼 정확한 채널명으로 구독하고, PUBLISH는 해당 채널에 메시지를 발행합니다. PSUBSCRIBE는 'user:*:notifications'처럼 패턴을 사용해 여러 채널을 한번에 구독할 수 있습니다. 패턴 구독은 편리하지만 성능 오버헤드가 있어 신중하게 사용해야 합니다."

**꼬리 질문**
- Q: 패턴 구독의 성능 문제를 어떻게 해결하나요?
- A: 패턴 범위를 최소화하고, 필요한 경우에만 사용합니다. 또한 메시지 처리를 비동기로 하여 병목을 방지합니다.

**실무 연관**
- 실무에서는 관리자 대시보드에서 모든 에러 로그를 모니터링할 때 'system:*:error' 같은 패턴 구독을 사용합니다.

</details>

<details>
<summary><strong>3. Redis Pub/Sub의 메시지가 영속적으로 저장되지 않는 이유와 해결 방법은?</strong></summary>

**모범 답안 포인트**
- 포인트 1: Pub/Sub은 fire-and-forget 방식으로 설계되어 실시간성을 우선시
- 포인트 2: 구독자가 없으면 메시지가 즉시 사라짐
- 포인트 3: 메시지 보장이 필요하면 Streams나 List를 함께 사용

**예시 답변**
> "Redis Pub/Sub은 실시간 전송에 최적화되어 있어 메시지를 저장하지 않습니다. 구독자가 없거나 오프라인이면 메시지가 손실됩니다. 중요한 메시지는 PUBLISH 후 구독자 수를 확인하고, 0이면 List나 Streams에 백업하는 하이브리드 방식을 사용합니다."

**꼬리 질문**
- Q: 그렇다면 주문 시스템에는 Pub/Sub을 사용하면 안 되나요?
- A: 주문처럼 메시지 손실이 허용되지 않는 경우 Streams를 사용해야 합니다. Pub/Sub은 실시간 알림같이 일부 손실이 허용되는 경우에 적합합니다.

**실무 연관**
- 배달의민족 같은 서비스에서는 실시간 알림은 Pub/Sub으로, 주문 처리는 Streams로 분리하여 사용합니다.

</details>

<details>
<summary><strong>4. PUBLISH 명령어의 반환값은 무엇이고 왜 중요한가요?</strong></summary>

**모범 답안 포인트**
- 포인트 1: PUBLISH는 메시지를 받은 구독자 수를 반환
- 포인트 2: 0이면 구독자가 없어 메시지가 사라진 것
- 포인트 3: 반환값을 확인하여 메시지 전송 여부 검증 필요

**예시 답변**
> "PUBLISH 명령어는 메시지를 수신한 구독자 수를 integer로 반환합니다. 만약 0을 반환하면 구독자가 없어 메시지가 전달되지 않은 것입니다. 실무에서는 이 값을 확인하여 중요한 메시지는 별도 저장소에 백업합니다."

**꼬리 질문**
- Q: 구독자가 3명인데 1명이 네트워크 오류로 못 받으면 반환값은?
- A: 여전히 3을 반환합니다. PUBLISH는 메시지를 전송 시도한 구독자 수를 반환하며, 실제 수신 여부는 보장하지 않습니다.

**실무 연관**
- 알림 시스템에서 PUBLISH 반환값을 로그로 남겨 전송 통계를 수집하고, 0일 때는 재시도 로직을 실행합니다.

</details>

<details>
<summary><strong>5. Pub/Sub을 사용할 때 발생할 수 있는 메시지 손실 상황 3가지를 말씀해주세요.</strong></summary>

**모범 답안 포인트**
- 포인트 1: 구독자가 없을 때 메시지 발행
- 포인트 2: 구독자의 네트워크 연결이 끊어졌을 때
- 포인트 3: 구독자의 메시지 처리 속도가 느려 버퍼 오버플로

**예시 답변**
> "첫째, 구독자가 없는 채널에 메시지를 발행하면 즉시 사라집니다. 둘째, 구독자가 네트워크 장애로 연결이 끊어지면 해당 시간의 메시지를 못 받습니다. 셋째, 구독자의 처리 속도가 발행 속도를 따라가지 못하면 클라이언트 버퍼가 가득 차서 메시지가 드롭됩니다."

**꼬리 질문**
- Q: 메시지 손실을 방지하려면 어떻게 해야 하나요?
- A: 중요한 메시지는 Streams를 사용하고, Pub/Sub은 보조적으로 사용합니다. 또한 구독자의 재연결 로직과 백프레셔 처리를 구현해야 합니다.

**실무 연관**
- 금융 시스템에서는 거래 알림에 Pub/Sub과 Streams를 병행하여, 실시간성과 안정성을 동시에 확보합니다.

</details>

<details>
<summary><strong>6. Redis Pub/Sub과 Kafka의 차이점은 무엇인가요?</strong></summary>

**모범 답안 포인트**
- 포인트 1: Redis Pub/Sub은 메모리 기반 실시간 메시징, Kafka는 디스크 기반 영속적 메시징
- 포인트 2: Redis는 가볍고 빠르지만 메시지 손실 가능, Kafka는 느리지만 안정적
- 포인트 3: Redis는 간단한 알림용, Kafka는 대규모 이벤트 스트리밍용

**예시 답변**
> "Redis Pub/Sub은 메모리 기반으로 매우 빠르지만 메시지를 저장하지 않아 손실 가능성이 있습니다. 반면 Kafka는 디스크에 영속적으로 저장하여 안정적이지만 상대적으로 복잡합니다. Redis는 실시간 채팅이나 알림처럼 가볍고 빠른 통신에 적합하고, Kafka는 주문 처리나 로그 수집처럼 대규모 이벤트 스트리밍에 적합합니다."

**꼬리 질문**
- Q: 그렇다면 어떤 기준으로 선택해야 하나요?
- A: 초당 수만 건 미만의 메시지에 실시간성이 중요하면 Redis, 수십만 건 이상이거나 메시지 손실이 허용 안 되면 Kafka를 선택합니다.

**실무 연관**
- 많은 기업이 실시간 알림은 Redis, 주문/결제는 Kafka로 분리하여 사용합니다.

</details>

<details>
<summary><strong>7. 채널 네이밍 컨벤션이 왜 중요하고, 어떻게 설계해야 하나요?</strong></summary>

**모범 답안 포인트**
- 포인트 1: 일관된 네이밍으로 패턴 구독과 디버깅이 쉬워짐
- 포인트 2: 계층 구조로 설계하여 확장성 확보
- 포인트 3: 팀 전체가 공유하는 규칙 필요

**예시 답변**
> "채널명을 일관되게 짓지 않으면 패턴 구독 시 일부 채널이 누락되거나, 디버깅이 어려워집니다. 'domain:resource:id:event' 형식처럼 계층 구조로 설계하고, 소문자와 콜론(:)을 구분자로 사용하는 것이 일반적입니다. 예를 들어 'user:1001:notifications', 'chat:room:general:messages' 같은 형식입니다."

**꼬리 질문**
- Q: 채널명에 콜론(:) 대신 언더스코어(_)를 쓰면 안 되나요?
- A: 기술적으로는 가능하지만, 콜론이 계층 구조를 더 명확하게 표현하고, Redis 커뮤니티의 관습입니다.

**실무 연관**
- 대규모 프로젝트에서는 채널 빌더 클래스를 만들어 네이밍 일관성을 강제합니다.

</details>

---

### 📗 중급 개발자용 (3-5개)

<details>
<summary><strong>1. Redis Pub/Sub의 내부 동작 원리와 성능 특성을 설명하세요.</strong></summary>

**모범 답안 포인트**
- 심화 포인트 1: 채널명을 키로 하는 딕셔너리 구조로 구독자 리스트 관리
- 심화 포인트 2: PUBLISH 시 O(N+M) 복잡도 (N=구독자 수, M=패턴 구독 수)
- 내부 동작 원리: 메시지를 각 구독자의 출력 버퍼에 복사하여 전송

**예시 답변**
> "Redis는 내부적으로 채널명을 키로 하는 딕셔너리와 구독자 리스트를 유지합니다. PUBLISH 명령어는 해당 채널의 모든 구독자와 매칭되는 패턴 구독자를 찾아 메시지를 복사합니다. 시간 복잡도는 O(N+M)으로, 구독자와 패턴이 많아질수록 느려집니다. 메시지는 각 클라이언트의 출력 버퍼에 복사되므로, 1MB 메시지를 1000명에게 보내면 1GB 메모리가 순간적으로 필요합니다."

**실무 예시**
```python
# 성능 측정 코드
import redis
import time

r = redis.Redis()

# 구독자 수에 따른 PUBLISH 성능 테스트
def benchmark_publish(num_subscribers):
    channel = "test_channel"

    # 구독자 생성
    pubsubs = [r.pubsub() for _ in range(num_subscribers)]
    for ps in pubsubs:
        ps.subscribe(channel)

    # 발행 시간 측정
    start = time.time()
    for i in range(1000):
        r.publish(channel, f"message {i}")
    elapsed = time.time() - start

    print(f"{num_subscribers}명 구독자: {elapsed:.3f}초, {1000/elapsed:.0f} msg/s")

# 결과: 10명 → 50000 msg/s, 1000명 → 5000 msg/s
```

**꼬리 질문**
- Q: 대규모 시스템에서 Pub/Sub 성능을 높이려면?
- A: 1) 샤딩: 채널을 여러 Redis 인스턴스에 분산, 2) 패턴 구독 최소화, 3) 메시지 크기 압축

**실무 연관**
- 실제 프로젝트에서의 적용 사례: 네이버 라인은 채팅 서버를 지역별로 샤딩하여 Pub/Sub 성능 확보
- 성능 측정 결과: 단일 Redis에서 초당 10만 메시지 처리 가능

</details>

<details>
<summary><strong>2. Redis Streams와 Pub/Sub을 함께 사용하는 하이브리드 아키텍처를 설계하세요.</strong></summary>

**모범 답안 포인트**
- 심화 포인트 1: Pub/Sub은 실시간 전송, Streams는 백업 및 재처리용
- 심화 포인트 2: 이벤트를 Streams에 먼저 저장 후 Pub/Sub으로 알림
- 내부 동작 원리: At-least-once 보장을 위해 양쪽 모두 사용

**예시 답변**
> "중요한 이벤트는 먼저 Streams에 저장하여 영속성을 보장하고, 동시에 Pub/Sub으로 실시간 알림을 보냅니다. 구독자가 오프라인이면 Streams에서 나중에 읽을 수 있고, 온라인이면 Pub/Sub으로 즉시 받습니다. Consumer Group을 사용하면 여러 워커가 분산 처리하며, Pub/Sub은 대시보드 같은 실시간 모니터링용으로 사용합니다."

**실무 예시**
```python
# 하이브리드 메시징 시스템
class HybridMessaging:
    def __init__(self, redis_client):
        self.r = redis_client

    def send_message(self, channel, message_data):
        """메시지를 Streams와 Pub/Sub 모두에 전송"""
        import json
        from datetime import datetime

        # 1. Streams에 영구 저장 (재처리 가능)
        stream_key = f"stream:{channel}"
        stream_id = self.r.xadd(stream_key, {
            "data": json.dumps(message_data),
            "timestamp": datetime.now().isoformat()
        })

        # 2. Pub/Sub으로 실시간 알림
        pubsub_channel = f"realtime:{channel}"
        subscribers = self.r.publish(pubsub_channel, json.dumps({
            "stream_id": stream_id,
            "data": message_data
        }))

        return {
            "stream_id": stream_id,
            "realtime_subscribers": subscribers,
            "persisted": True
        }

    def subscribe_realtime(self, channel, callback):
        """실시간 구독 (빠름, 일부 손실 가능)"""
        pubsub = self.r.pubsub()
        pubsub.subscribe(f"realtime:{channel}")

        for message in pubsub.listen():
            if message['type'] == 'message':
                callback(json.loads(message['data']))

    def process_stream(self, channel, consumer_group, consumer_name):
        """Streams에서 읽기 (느림, 손실 없음, 재처리 가능)"""
        stream_key = f"stream:{channel}"

        # Consumer Group 생성
        try:
            self.r.xgroup_create(stream_key, consumer_group, id='0', mkstream=True)
        except redis.ResponseError:
            pass

        while True:
            messages = self.r.xreadgroup(
                consumer_group, consumer_name,
                {stream_key: '>'},
                count=10, block=5000
            )

            for stream, msg_list in messages:
                for msg_id, data in msg_list:
                    try:
                        # 메시지 처리
                        process(json.loads(data[b'data']))
                        # ACK
                        self.r.xack(stream_key, consumer_group, msg_id)
                    except Exception as e:
                        # 처리 실패 시 ACK 안 함 -> 재시도
                        print(f"처리 에러: {e}")

# 사용 예시
msg_system = HybridMessaging(redis.Redis())

# 주문 생성 시
msg_system.send_message("orders", {
    "order_id": "12345",
    "user_id": "1001",
    "amount": 50000
})

# 실시간 대시보드는 Pub/Sub 구독
msg_system.subscribe_realtime("orders", lambda data: update_dashboard(data))

# 주문 처리 워커는 Streams 사용
msg_system.process_stream("orders", "order_processors", "worker1")
```

**꼬리 질문**
- Q: 두 방식을 모두 사용하면 비용이 2배 아닌가요?
- A: Pub/Sub은 메모리 오버헤드가 거의 없고, Streams는 TTL로 오래된 메시지 삭제하므로 실제 비용은 1.2배 정도입니다.

**실무 연관**
- 쿠팡은 주문 시스템에서 이 패턴을 사용: Streams로 주문 보장, Pub/Sub으로 실시간 알림

</details>

<details>
<summary><strong>3. 대규모 트래픽 환경에서 Pub/Sub 성능 최적화 전략을 제시하세요.</strong></summary>

**모범 답안 포인트**
- 심화 포인트 1: 샤딩으로 부하 분산
- 심화 포인트 2: 메시지 배치 처리
- 심화 포인트 3: 클라이언트 사이드 필터링

**예시 답변**
> "첫째, 채널을 해시 기반으로 여러 Redis 인스턴스에 샤딩하여 부하를 분산합니다. 둘째, 메시지를 배치로 모아 한 번에 발행하여 네트워크 오버헤드를 줄입니다. 셋째, 모든 메시지를 구독하는 대신 클라이언트가 필요한 메시지만 필터링합니다. 넷째, 패턴 구독 대신 정확한 채널 구독을 우선 사용합니다."

**실무 예시**
```python
# 샤딩 기반 Pub/Sub
class ShardedPubSub:
    def __init__(self, redis_nodes):
        self.nodes = redis_nodes  # [Redis(host1), Redis(host2), ...]

    def get_shard(self, channel):
        """채널명 해시로 샤드 결정"""
        import hashlib
        hash_value = int(hashlib.md5(channel.encode()).hexdigest(), 16)
        shard_index = hash_value % len(self.nodes)
        return self.nodes[shard_index]

    def publish(self, channel, message):
        """적절한 샤드에 발행"""
        shard = self.get_shard(channel)
        return shard.publish(channel, message)

    def subscribe(self, channel):
        """적절한 샤드에서 구독"""
        shard = self.get_shard(channel)
        pubsub = shard.pubsub()
        pubsub.subscribe(channel)
        return pubsub

# 배치 발행
class BatchPublisher:
    def __init__(self, redis_client, batch_size=100, flush_interval=1):
        self.r = redis_client
        self.batch_size = batch_size
        self.batch = []
        self.lock = threading.Lock()

        # 자동 플러시 스레드
        threading.Thread(target=self._auto_flush, daemon=True).start()

    def publish(self, channel, message):
        with self.lock:
            self.batch.append((channel, message))
            if len(self.batch) >= self.batch_size:
                self._flush()

    def _flush(self):
        if not self.batch:
            return

        pipeline = self.r.pipeline()
        for channel, message in self.batch:
            pipeline.publish(channel, message)

        pipeline.execute()
        self.batch = []

    def _auto_flush(self):
        while True:
            time.sleep(1)
            with self.lock:
                self._flush()

# 사용
sharded_pubsub = ShardedPubSub([
    redis.Redis(host='redis1'),
    redis.Redis(host='redis2'),
    redis.Redis(host='redis3')
])

batch_publisher = BatchPublisher(redis.Redis())

# 초당 10만 건도 처리 가능
for i in range(100000):
    batch_publisher.publish(f"events:type_{i % 100}", f"message {i}")
```

**꼬리 질문**
- Q: 샤딩 시 클라이언트가 모든 샤드를 구독해야 하나요?
- A: 일관된 해싱을 사용하면 클라이언트도 어느 샤드를 구독할지 알 수 있어, 필요한 샤드만 구독합니다.

**실무 연관**
- 트위터는 수백 대의 Redis 인스턴스로 타임라인 업데이트를 샤딩하여 초당 수십만 건 처리

</details>

<details>
<summary><strong>4. Pub/Sub에서 메시지 순서 보장 문제와 해결 방법은?</strong></summary>

**모범 답안 포인트**
- 심화 포인트 1: 기본적으로 단일 채널 내에서는 FIFO 보장
- 심화 포인트 2: 여러 채널에서는 순서 보장 안 됨
- 심화 포인트 3: Streams를 사용하거나 시퀀스 번호 추가

**예시 답변**
> "Redis Pub/Sub은 동일 채널 내에서는 발행 순서대로 전달되지만, 다른 채널 간에는 순서가 보장되지 않습니다. 또한 네트워크 지연이나 구독자의 처리 속도 차이로 순서가 뒤바뀔 수 있습니다. 순서가 중요한 경우 메시지에 시퀀스 번호를 추가하거나, Streams를 사용하여 메시지 ID로 순서를 보장해야 합니다."

**실무 예시**
```python
# 순서 보장 메시징
class OrderedMessaging:
    def __init__(self, redis_client):
        self.r = redis_client
        self.sequence_counters = {}

    def publish_ordered(self, channel, message):
        """순서 번호를 추가하여 발행"""
        # 채널별 시퀀스 번호 증가
        seq = self.r.incr(f"seq:{channel}")

        ordered_message = {
            "seq": seq,
            "data": message,
            "timestamp": time.time()
        }

        self.r.publish(channel, json.dumps(ordered_message))
        return seq

    def subscribe_ordered(self, channel, callback):
        """순서대로 메시지 처리"""
        pubsub = self.r.pubsub()
        pubsub.subscribe(channel)

        expected_seq = 1
        buffer = {}  # 순서 안 맞는 메시지 버퍼

        for message in pubsub.listen():
            if message['type'] == 'message':
                msg = json.loads(message['data'])
                seq = msg['seq']

                if seq == expected_seq:
                    # 순서 맞음: 즉시 처리
                    callback(msg['data'])
                    expected_seq += 1

                    # 버퍼에 있는 다음 메시지들 처리
                    while expected_seq in buffer:
                        callback(buffer[expected_seq]['data'])
                        del buffer[expected_seq]
                        expected_seq += 1

                elif seq > expected_seq:
                    # 순서 안 맞음: 버퍼에 저장
                    buffer[seq] = msg
                else:
                    # 중복 메시지: 무시
                    pass

# Streams 사용 (더 간단함)
def ordered_with_streams(redis_client, stream_key):
    """Streams는 자동으로 순서 보장"""
    r = redis_client

    # 발행
    r.xadd(stream_key, {"message": "첫 번째"})
    r.xadd(stream_key, {"message": "두 번째"})
    r.xadd(stream_key, {"message": "세 번째"})

    # 구독 (항상 순서대로)
    messages = r.xread({stream_key: '0'})
    for stream, msg_list in messages:
        for msg_id, data in msg_list:
            print(f"{msg_id}: {data[b'message'].decode()}")
            # 결과: 항상 순서대로 출력
```

**꼬리 질문**
- Q: 버퍼에 메시지가 계속 쌓이면 메모리 문제가 발생하지 않나요?
- A: 타임아웃을 설정하여 일정 시간 후에는 버퍼를 비우거나, Streams로 전환하는 것이 안전합니다.

**실무 연관**
- 금융 거래 시스템에서는 Streams를 사용하여 거래 순서를 보장합니다.

</details>

<details>
<summary><strong>5. 클라이언트 출력 버퍼 문제와 해결 방법을 설명하세요.</strong></summary>

**모범 답안 포인트**
- 심화 포인트 1: 구독자가 느리면 출력 버퍼가 가득 차서 연결 끊김
- 심화 포인트 2: client-output-buffer-limit 설정으로 제어
- 심화 포인트 3: 백프레셔 처리 또는 메시지 샘플링 필요

**예시 답변**
> "Pub/Sub에서 구독자가 메시지를 빠르게 소비하지 못하면 Redis의 출력 버퍼가 가득 차서 자동으로 연결을 끊습니다. redis.conf의 'client-output-buffer-limit pubsub'로 제한을 설정할 수 있습니다. 기본값은 32MB 하드 리밋, 8MB 소프트 리밋(60초)입니다. 구독자는 비동기 처리, 메시지 샘플링, 또는 백프레셔 로직으로 대응해야 합니다."

**실무 예시**
```python
# 백프레셔 처리
class BackpressureSubscriber:
    def __init__(self, redis_client, max_queue_size=1000):
        self.r = redis_client
        self.queue = queue.Queue(maxsize=max_queue_size)
        self.dropped_count = 0

    def subscribe(self, channel):
        pubsub = self.r.pubsub()
        pubsub.subscribe(channel)

        # 리스너 스레드
        def listener():
            for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        # 큐가 가득 차면 즉시 반환 (블로킹 안 함)
                        self.queue.put_nowait(message['data'])
                    except queue.Full:
                        # 메시지 드롭 + 카운트
                        self.dropped_count += 1
                        if self.dropped_count % 100 == 0:
                            print(f"경고: {self.dropped_count}개 메시지 드롭됨")

        threading.Thread(target=listener, daemon=True).start()

    def process(self):
        """별도 스레드에서 처리"""
        while True:
            msg = self.queue.get()
            try:
                # 실제 처리 (느릴 수 있음)
                process_message(msg)
            except Exception as e:
                print(f"처리 에러: {e}")

# 메시지 샘플링 (모든 메시지를 처리할 필요 없는 경우)
class SamplingSubscriber:
    def __init__(self, redis_client, sample_rate=0.1):
        self.r = redis_client
        self.sample_rate = sample_rate  # 10%만 처리

    def subscribe(self, channel):
        pubsub = self.r.pubsub()
        pubsub.subscribe(channel)

        for message in pubsub.listen():
            if message['type'] == 'message':
                # 확률적으로 샘플링
                if random.random() < self.sample_rate:
                    process_message(message['data'])
                # 나머지 90%는 무시 (모니터링/통계용으로 적합)

# Redis 설정 확인
def check_buffer_config(redis_client):
    config = redis_client.config_get('client-output-buffer-limit')
    print(f"Pub/Sub 버퍼 제한: {config}")

    # 권장 설정 (redis.conf):
    # client-output-buffer-limit pubsub 64mb 16mb 60
    # (하드 리밋 64MB, 소프트 리밋 16MB 60초)
```

**꼬리 질문**
- Q: 출력 버퍼 크기를 무한대로 설정하면 안 되나요?
- A: 절대 안 됩니다. 느린 클라이언트 하나가 Redis 메모리를 모두 소진하여 전체 서비스 장애를 유발할 수 있습니다.

**실무 연관**
- 대규모 로그 수집 시스템에서는 샘플링으로 메시지 양을 줄여 버퍼 문제를 방지합니다.

</details>

---

## ❓ FAQ

<details>
<summary><strong>Q1: 구독자가 없는 채널에 메시지를 발행하면 어떻게 되나요?</strong></summary>

**A:** 메시지는 즉시 손실됩니다. Redis Pub/Sub는 fire-and-forget 방식입니다.

```bash
# 구독자 없는 채널에 발행
127.0.0.1:6379> PUBLISH empty_channel "test message"
(integer) 0  # 구독자 수 0 반환

# 해결 방법: 메시지 영속성이 필요한 경우 Streams 사용
127.0.0.1:6379> XADD persistent_messages * content "test message" timestamp $(date +%s)
"1647834022000-0"
```

**실무 팁**:
💡 중요한 메시지는 PUBLISH 반환값을 확인하고, 0이면 List나 Streams에 백업하는 하이브리드 방식을 사용하세요.

</details>

<details>
<summary><strong>Q2: 구독 중인 클라이언트가 연결이 끊어지면 어떻게 되나요?</strong></summary>

**A:** 자동으로 구독이 해제되며, 해당 클라이언트로 전송될 메시지는 손실됩니다.

```python
# Python 클라이언트 재연결 로직
import redis
import time
import logging

class ResilientSubscriber:
    def __init__(self, host='localhost', port=6379):
        self.host = host
        self.port = port
        self.channels = []
        self.patterns = []

    def subscribe(self, channels=None, patterns=None):
        self.channels = channels or []
        self.patterns = patterns or []

        while True:
            try:
                r = redis.Redis(host=self.host, port=self.port, socket_keepalive=True)
                pubsub = r.pubsub()

                if self.channels:
                    pubsub.subscribe(*self.channels)
                if self.patterns:
                    pubsub.psubscribe(*self.patterns)

                logging.info(f"구독 시작: {self.channels + self.patterns}")

                for message in pubsub.listen():
                    if message['type'] in ['message', 'pmessage']:
                        self.handle_message(message)

            except (redis.ConnectionError, redis.TimeoutError) as e:
                logging.error(f"연결 오류: {e}, 5초 후 재시도")
                time.sleep(5)
            except KeyboardInterrupt:
                logging.info("구독 종료")
                break

    def handle_message(self, message):
        print(f"메시지 수신: {message}")
```

**실무 팁**:
💡 WebSocket 연결처럼 재연결 로직을 반드시 구현하고, 지수 백오프(exponential backoff)로 재시도 간격을 조절하세요.

</details>

<details>
<summary><strong>Q3: 한 클라이언트가 너무 많은 채널을 구독하면 성능에 영향이 있나요?</strong></summary>

**A:** 네, 있습니다. 채널 수가 증가하면 메모리 사용량과 메시지 매칭 시간이 증가합니다.

```bash
# 구독 수 모니터링
cat > subscription_monitor.sh << 'EOF'
#!/bin/bash

echo "=== Redis Pub/Sub 모니터링 ==="
echo "활성 채널 수: $(redis-cli PUBSUB CHANNELS | wc -l)"
echo "패턴 구독자 수: $(redis-cli PUBSUB NUMPAT)"

echo -e "\n채널별 구독자 수:"
redis-cli PUBSUB CHANNELS | head -10 | while read channel; do
    subscribers=$(redis-cli PUBSUB NUMSUB "$channel" | tail -1)
    echo "  $channel: $subscribers"
done

echo -e "\n메모리 사용량:"
redis-cli INFO memory | grep used_memory_human
EOF

chmod +x subscription_monitor.sh
./subscription_monitor.sh
```

**실무 팁**:
💡 클라이언트당 구독 채널은 100개 이하로 제한하고, 패턴 구독은 꼭 필요한 경우만 사용하세요.

</details>

<details>
<summary><strong>Q4: 메시지 발행 성능을 높이는 방법은?</strong></summary>

**A:** 여러 최적화 기법을 사용할 수 있습니다.

```bash
# 1. 파이프라인 사용
cat > high_performance_publisher.py << 'EOF'
import redis
import time

def benchmark_publishing():
    r = redis.Redis()

    # 일반적인 방법
    start = time.time()
    for i in range(1000):
        r.publish('test_channel', f'message_{i}')
    normal_time = time.time() - start

    # 파이프라인 방법
    start = time.time()
    pipe = r.pipeline()
    for i in range(1000):
        pipe.publish('test_channel', f'message_{i}')
    pipe.execute()
    pipeline_time = time.time() - start

    print(f"일반 방법: {normal_time:.3f}초")
    print(f"파이프라인: {pipeline_time:.3f}초")
    print(f"성능 향상: {normal_time/pipeline_time:.1f}배")

benchmark_publishing()
EOF

python3 high_performance_publisher.py
```

**실무 팁**:
💡 Pipeline을 사용하면 네트워크 왕복 시간을 줄여 성능을 5-10배 향상시킬 수 있습니다. 배치 크기는 100-1000개가 적당합니다.

</details>

<details>
<summary><strong>Q5: 메시지 크기가 성능에 미치는 영향은?</strong></summary>

**A:** 메시지 크기가 클수록 네트워크 대역폭과 메모리 사용량이 증가합니다.

```bash
# 메시지 크기별 성능 테스트
cat > message_size_benchmark.lua << 'EOF'
local message_sizes = {100, 1000, 10000, 100000}
local test_channel = 'size_test'
local results = {}

for i, size in ipairs(message_sizes) do
    local message = string.rep('x', size)

    local start_time = redis.call('TIME')
    local start_micro = tonumber(start_time[2])

    -- 100번 발행 테스트
    for j = 1, 100 do
        redis.call('PUBLISH', test_channel, message)
    end

    local end_time = redis.call('TIME')
    local end_micro = tonumber(end_time[2])

    local duration = end_micro - start_micro
    table.insert(results, {size, duration})
end

return results
EOF

redis-cli --eval message_size_benchmark.lua
```

**실무 팁**:
💡 메시지는 1KB 이하로 유지하고, 큰 데이터는 별도 저장소에 저장 후 참조 ID만 전송하세요. JSON 대신 MessagePack 같은 바이너리 포맷도 고려하세요.

</details>

<details>
<summary><strong>Q6: Pub/Sub과 Streams 중 어떤 것을 선택해야 하나요?</strong></summary>

**A**: 사용 목적에 따라 선택하세요.

**상세 설명**:
- **Pub/Sub 선택**: 실시간성이 중요하고 일부 메시지 손실이 허용되는 경우
  - 실시간 채팅, 알림, 모니터링 대시보드
  - 가볍고 빠름 (레이턴시 < 1ms)
  - 메모리 오버헤드 최소

- **Streams 선택**: 메시지 손실이 허용되지 않는 경우
  - 주문 처리, 결제, 감사 로그
  - 메시지 히스토리 필요
  - 여러 Consumer가 작업 분산 처리

**비교표**:
```
┌──────────────┬────────────┬────────────┐
│ 특징         │ Pub/Sub    │ Streams    │
├──────────────┼────────────┼────────────┤
│ 영속성       │ ✗          │ ✓          │
│ 재처리       │ ✗          │ ✓          │
│ 속도         │ 매우 빠름  │ 빠름       │
│ 메모리       │ 낮음       │ 중간       │
│ Consumer 분산│ ✗          │ ✓          │
│ 메시지 순서  │ 기본       │ 보장       │
└──────────────┴────────────┴────────────┘
```

**실무 팁**:
💡 하이브리드 방식: Streams에 저장 + Pub/Sub으로 실시간 알림을 병행하면 안정성과 속도를 모두 확보할 수 있습니다.

</details>

<details>
<summary><strong>Q7: 대규모 시스템에서 Pub/Sub 샤딩은 어떻게 하나요?</strong></summary>

**A**: 채널명을 해시하여 여러 Redis 인스턴스에 분산합니다.

**상세 설명**:
샤딩 전략은 다음과 같습니다:
1. **일관된 해싱**: 채널명을 MD5/SHA256로 해시
2. **샤드 결정**: 해시값 % 샤드 수로 인스턴스 선택
3. **클라이언트 라우팅**: 발행/구독 시 동일한 로직으로 샤드 찾기

**예시**:
```python
import hashlib
import redis

class ShardedPubSub:
    def __init__(self, redis_nodes):
        # redis_nodes = ['redis1:6379', 'redis2:6379', 'redis3:6379']
        self.shards = [redis.Redis.from_url(f'redis://{node}') for node in redis_nodes]

    def get_shard(self, channel):
        hash_val = int(hashlib.md5(channel.encode()).hexdigest(), 16)
        return self.shards[hash_val % len(self.shards)]

    def publish(self, channel, message):
        shard = self.get_shard(channel)
        return shard.publish(channel, message)

    def subscribe(self, channel):
        shard = self.get_shard(channel)
        return shard.pubsub()

# 사용
pubsub_cluster = ShardedPubSub(['localhost:6379', 'localhost:6380', 'localhost:6381'])
pubsub_cluster.publish('user:1001:notifications', 'Hello')
```

**실무 팁**:
💡 샤딩 시 각 샤드의 부하를 모니터링하고, 핫스팟(특정 샤드에 트래픽 집중)이 발생하면 채널 분산을 재조정하세요.

</details>

---

## 📝 핵심 정리

### 이 장에서 배운 핵심 개념

| 개념 | 설명 | 핵심 키워드 |
|------|------|-------------|
| Pub/Sub 패턴 | 발행자와 구독자 간 메시징 시스템 | Fire-and-forget, 실시간, 1:N |
| Channel | 메시지를 전달하는 통로 | 토픽 기반, 계층 구조 |
| Pattern 구독 | 와일드카드로 여러 채널 구독 | PSUBSCRIBE, 성능 고려 |
| Redis Streams | 영속적 메시지 큐 | 재처리, Consumer Group, ACK |
| 하이브리드 방식 | Pub/Sub + Streams 병행 | 실시간 + 안정성 |

### 필수 명령어/코드 정리

| 명령어/코드 | 용도 | 예시 |
|-------------|------|------|
| PUBLISH | 메시지 발행 | `PUBLISH channel "message"` |
| SUBSCRIBE | 채널 구독 | `SUBSCRIBE news sports` |
| PSUBSCRIBE | 패턴 구독 | `PSUBSCRIBE user:*:notifications` |
| UNSUBSCRIBE | 구독 해제 | `UNSUBSCRIBE channel` |
| PUBSUB CHANNELS | 활성 채널 조회 | `PUBSUB CHANNELS pattern` |
| PUBSUB NUMSUB | 구독자 수 조회 | `PUBSUB NUMSUB channel` |
| XADD | Streams에 추가 | `XADD stream * field value` |
| XREAD | Streams 읽기 | `XREAD STREAMS stream 0` |
| XGROUP CREATE | Consumer Group 생성 | `XGROUP CREATE stream group 0` |
| XREADGROUP | 그룹으로 읽기 | `XREADGROUP GROUP group consumer` |

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- PUBLISH 반환값(구독자 수)을 항상 확인하여 전송 여부 검증
- 중요한 메시지는 Streams에 백업하는 하이브리드 방식 사용
- 채널 네이밍 컨벤션을 팀과 합의하고 일관성 유지
- 메시지에 timestamp와 ID를 포함하여 추적 가능하게 설계
- 구독자의 재연결 로직 구현 (네트워크 장애 대응)
- 패턴 구독은 범위를 최소화하여 성능 영향 감소
- 비동기 처리로 느린 작업(DB 저장)을 분리

#### ❌ 하지 말아야 할 것
- 주문/결제처럼 손실 불가한 데이터에 Pub/Sub만 사용
- 패턴 구독을 무분별하게 사용 (user:* 같은 너무 넓은 범위)
- 메시지 처리 로직에서 동기 블로킹 작업 수행
- 출력 버퍼 제한을 무한대로 설정
- 채널명에 일관성 없는 네이밍 (대소문자 혼용, 구분자 변경)
- 구독 중인 클라이언트에서 다른 Redis 명령어 실행
- 메시지 크기를 무제한으로 증가 (1MB 이상 주의)

### 성능/보안 체크리스트

#### 성능
- 메시지 크기 최적화 (JSON 압축, 불필요한 데이터 제거)
- 구독자 수 모니터링 (채널별 구독자 수 추적)
- 패턴 구독 최소화 (정확한 채널 구독 우선)
- 메시지 배치 발행 (Pipeline 사용)
- 샤딩으로 부하 분산 (대규모 시스템)
- 클라이언트 버퍼 설정 적절히 조정
- 메시지 샘플링 또는 필터링 (불필요한 처리 방지)

#### 보안
- 민감한 데이터 암호화 후 전송
- 채널명에 인증 토큰 포함하여 접근 제어
- ACL로 채널별 권한 관리 (Redis 6.0+)
- TLS/SSL로 네트워크 통신 암호화
- 메시지 크기 제한으로 DoS 공격 방지
- 로그에 민감 정보 기록 금지
- 프로덕션 환경에서 DEBUG 모드 비활성화

---

## 📚 추가 학습 자료

### 공식 문서
- [Redis Pub/Sub 공식 문서](https://redis.io/docs/manual/pubsub/)
- [Redis Streams 공식 가이드](https://redis.io/docs/data-types/streams/)
- [Redis 클라이언트 출력 버퍼 설정](https://redis.io/docs/reference/clients/)

### 추천 블로그/아티클
- [Redis Pub/Sub 실전 가이드 - 우아한형제들 기술 블로그](https://techblog.woowahan.com/)
- [대규모 실시간 알림 시스템 구축기 - 카카오 기술 블로그](https://tech.kakao.com/)
- [Redis Pub/Sub vs Kafka - AWS 아키텍처 블로그](https://aws.amazon.com/ko/blogs/)

### 영상 강의
- [Redis University - RU202: Redis Streams](https://university.redis.com/)
- [인프런 - Redis 완벽 가이드](https://www.inflearn.com/)

### 컨퍼런스 발표
- [Redis Day 2023 - Pub/Sub at Scale](https://redis.com/redisconf/)
- [AWS re:Invent - Building Real-time Applications with Redis](https://reinvent.awsevents.com/)

### 오픈소스 프로젝트
- [Socket.io with Redis adapter](https://github.com/socketio/socket.io-redis-adapter)
- [Bull Queue - Redis 기반 작업 큐](https://github.com/OptimalBits/bull)
- [Node-Redis Pub/Sub 예제](https://github.com/redis/node-redis)

---

## 🔗 관련 기술

**이 기술과 함께 사용하는 기술들**

| 기술 | 관계 | 학습 우선순위 |
|------|------|---------------|
| WebSocket | Pub/Sub으로 브라우저에 실시간 푸시 | ⭐⭐⭐ |
| Redis Streams | 영속적 메시징으로 Pub/Sub 보완 | ⭐⭐⭐ |
| Kafka | 대규모 이벤트 스트리밍 (Pub/Sub 대안) | ⭐⭐ |
| RabbitMQ | 메시지 큐 (더 복잡한 라우팅) | ⭐⭐ |
| Socket.io | Node.js 실시간 통신 라이브러리 | ⭐⭐⭐ |
| gRPC | 마이크로서비스 간 통신 | ⭐⭐ |
| GraphQL Subscriptions | 실시간 GraphQL 쿼리 | ⭐⭐ |

---

## 🚀 다음 단계

### 다음 장 미리보기: 11장 - Redis 트랜잭션과 Lua 스크립팅
- **배울 내용 1**: MULTI/EXEC로 원자적 작업 수행
- **배울 내용 2**: Lua 스크립트로 복잡한 로직을 서버에서 실행
- **배울 내용 3**: 낙관적 락(WATCH)과 비관적 락 비교
- **실전 프로젝트**: 재고 관리 시스템 (동시성 제어)

### 이 장과의 연결점
```
10장: Pub/Sub으로 실시간 메시징 학습
    ↓
11장: 트랜잭션으로 데이터 일관성 보장
    ↓
Lua 스크립트로 Pub/Sub + 트랜잭션 결합
    ↓
최종적으로 안정적인 실시간 시스템 구축
```

### 준비하면 좋을 것들
```bash
# Lua 기본 문법 미리 학습 (선택)
# https://www.lua.org/pil/1.html

# Redis 트랜잭션 개념 미리 보기
redis-cli
> MULTI
> SET key1 "value1"
> SET key2 "value2"
> EXEC
```

---

## 🎉 축하합니다!

**10장 학습 완료! Redis Pub/Sub 마스터가 되셨습니다!**

**이제 여러분은**:
✅ Redis Pub/Sub의 동작 원리와 내부 구조를 이해하고 실시간 메시징 시스템을 설계할 수 있습니다
✅ 실시간 채팅, 알림 시스템을 직접 구현하고 프로덕션 환경에 배포할 수 있습니다
✅ Pub/Sub과 Streams의 차이를 명확히 알고 상황에 맞게 선택할 수 있습니다
✅ 패턴 구독의 활용법과 성능 이슈를 파악하고 최적화할 수 있습니다
✅ 하이브리드 메시징 아키텍처를 설계하여 안정성과 속도를 동시에 확보할 수 있습니다
✅ 대규모 트래픽 환경에서 샤딩과 배치 처리로 성능을 최적화할 수 있습니다
✅ 메시지 손실을 방지하는 안전한 시스템을 구축하고 장애를 대응할 수 있습니다

**학습 체크리스트**:
- [ ] 기본 명령어 (PUBLISH, SUBSCRIBE, PSUBSCRIBE) 실습 완료
- [ ] 실시간 채팅 시스템 프로젝트 구현 완료
- [ ] 실시간 알림 시스템 프로젝트 구현 완료
- [ ] Streams 기반 메시징 실습 완료
- [ ] 주니어 시나리오 4가지 코드 작성 및 이해 완료
- [ ] 면접 질문 12개 (주니어 7개 + 중급 5개) 답변 준비 완료
- [ ] FAQ 7개 모두 숙지 완료
- [ ] 채널 네이밍 컨벤션 적용 연습 완료
- [ ] 성능 최적화 기법 (Pipeline, 샤딩) 실습 완료
- [ ] 하이브리드 메시징 아키텍처 구현 완료

**다음 단계**:
- [ ] 다음 장 (11장: 트랜잭션과 Lua 스크립팅)으로 진행
- [ ] 실전 프로젝트를 확장하여 포트폴리오에 추가
- [ ] 면접 질문을 복습하고 모의 면접 연습
- [ ] 실무 프로젝트에 Pub/Sub 적용 계획 수립
- [ ] 오픈소스 프로젝트 분석 (Socket.io, Bull Queue)
- [ ] Redis Conference 영상 시청

**🌟 실무 프로젝트 아이디어**:
1. **실시간 주식 시세 알림** - Pub/Sub으로 가격 변동 즉시 전달
2. **협업 도구 실시간 동기화** - 구글 독스처럼 여러 사용자 동시 편집
3. **IoT 센서 데이터 수집** - Streams로 센서 데이터 저장 및 분석
4. **게임 리더보드 실시간 업데이트** - 순위 변동 즉시 반영
5. **실시간 로그 모니터링 대시보드** - 패턴 구독으로 에러 추적

**계속해서 성장하세요!** 🚀

Redis는 단순한 캐시가 아니라 강력한 실시간 메시징 플랫폼입니다.
이제 여러분은 세계적인 서비스에서 사용하는 기술을 마스터했습니다!

---

**다음 장으로 이동**: [다음: 11장 - Redis 트랜잭션과 Lua 스크립팅 →](11-트랜잭션-Lua-스크립팅.md)

**이전 장으로 돌아가기**: [← 이전: 09장](09장-링크.md)

**목차로 돌아가기**: [📚 전체 목차](../README.md)
