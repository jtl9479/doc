# 학습 08. Redis

## Step 목차

| Step | 항목 | 카테고리 |
|------|------|----------|
| Step 1 | Redis 개요 — 왜 Redis인가, 특징, 활용 사례 | 기초 |
| Step 2 | Redis 환경 구축 — 설치, Docker, redis-cli 기본 | 기초 |
| Step 3 | 자료구조 — String, Hash, List, Set, Sorted Set | 자료구조 |
| Step 4 | 자료구조 심화 — Stream, Bitmap, HyperLogLog, Geospatial | 자료구조 |
| Step 5 | 캐시 전략 — Cache Aside, Read/Write Through, Write Behind | 캐시 |
| Step 6 | 캐시 문제 — 스탬피드, 관통, 눈사태, TTL 설계 | 캐시 |
| Step 7 | 분산 락 — SETNX, Redisson, Redlock 알고리즘 | 분산 락 |
| Step 8 | Pub/Sub + Stream | 메시징 |
| Step 9 | 영속성 — RDB, AOF, 혼합 모드 | 운영 |
| Step 10 | 메모리 관리 — maxmemory-policy, Eviction 전략 | 운영 |
| Step 11 | 고가용성 — Sentinel | 아키텍처 |
| Step 12 | 수평 확장 — Redis Cluster | 아키텍처 |
| Step 13 | Spring Data Redis 연동 — RedisTemplate, @Cacheable | Spring 연동 |
| Step 14 | Spring Data Redis 심화 — 직렬화, 세션 관리, 트랜잭션 | Spring 연동 |
| Step 15 | Redis 성능 — 싱글 스레드 모델, 파이프라이닝, 느린 명령어 | 성능 |
| Step 16 | Redis 트러블슈팅 + 모니터링 | 운영 실전 |

---

## 1. 개요

**현재 수준**: Redis 개념 인지 수준. 직접 구축/운영 경험 없음.
**학습 목표**: 캐시 전략을 설계하고 적절한 Redis 자료구조를 선택 가능. 분산 락을 구현 가능. Redis 장애 시 원인 진단 가능.
**분기 배정**: 2분기 (2026.07 ~ 2026.09)

---

## 2. 학습 순서 + 세부 항목

---

### Step 1. Redis 개요 — 왜 Redis인가, 특징, 활용 사례

| 학습 항목 | 학습 목표 |
|----------|----------|
| Redis란 | Remote Dictionary Server. 인메모리 키-값 저장소. DB/캐시/메시지 브로커로 활용 가능한 다목적 도구임을 설명 가능. |
| 왜 Redis인가 | 인메모리 → 마이크로초 수준 응답 속도. 풍부한 자료구조(단순 키-값이 아닌 Hash/List/Set/Sorted Set 등). 원자적 연산. 복제/클러스터 지원. |
| Memcached vs Redis | Memcached: 단순 키-값만, 멀티스레드, 영속성 없음. Redis: 다양한 자료구조, 싱글 스레드(IO 멀티플렉싱), 영속성 지원. 선택 기준을 설명 가능. |
| 실무 활용 사례 | 캐시(DB 조회 결과), 세션 저장소, 분산 락, 실시간 순위(리더보드), 속도 제한(Rate Limiting), 메시지 큐를 설명 가능. |

---

### Step 2. Redis 환경 구축 — 설치, Docker, redis-cli 기본

| 학습 항목 | 학습 목표 |
|----------|----------|
| Docker로 Redis 실행 | `docker run -p 6379:6379 redis` 또는 Docker Compose로 Redis를 로컬에서 기동 가능. |
| redis-cli 기본 | 접속(`redis-cli`), 기본 명령어(SET, GET, DEL, KEYS, TTL, EXPIRE, TYPE, INFO)를 사용 가능. |
| 데이터 타입 확인 | TYPE 명령으로 키의 자료구조를 확인하는 방법. OBJECT ENCODING으로 내부 인코딩을 확인하는 방법을 알고 있음. |
| Redis 설정 기초 | redis.conf의 핵심 설정(bind, port, requirepass, maxmemory)을 이해. CONFIG GET/SET으로 런타임 설정 변경 가능. |

---

### Step 3. 자료구조 — String, Hash, List, Set, Sorted Set

| 학습 항목 | 학습 목표 |
|----------|----------|
| String | 가장 기본. SET/GET/INCR/DECR/MSET/MGET. 카운터(조회수, 좋아요), 캐시 값 저장, 분산 락(SETNX)에 활용. 최대 512MB. |
| Hash | 필드-값 쌍의 집합. HSET/HGET/HMSET/HGETALL. 객체를 저장할 때 String(JSON 직렬화) 대비 장점(부분 조회/수정 가능, 메모리 효율)을 설명 가능. 사용자 프로필, 세션 데이터 저장에 적합. |
| List | 순서가 있는 문자열 리스트. LPUSH/RPUSH/LPOP/RPOP/LRANGE. 큐(FIFO: LPUSH+RPOP), 스택(LIFO: LPUSH+LPOP), 최근 N건 목록에 활용. BLPOP/BRPOP(블로킹 팝)으로 메시지 큐 구현 가능. |
| Set | 중복 없는 문자열 집합. SADD/SMEMBERS/SISMEMBER/SUNION/SINTER/SDIFF. 태그, 좋아요 사용자 목록, 집합 연산(교집합: 공통 친구)에 활용. |
| Sorted Set (ZSet) | 점수(score)가 있는 정렬된 집합. ZADD/ZRANGE/ZREVRANGE/ZRANK/ZSCORE. 리더보드(실시간 순위), 시간 기반 정렬(타임스탬프를 score로), 우선순위 큐에 활용. |
| 자료구조 선택 기준 | "이 데이터를 Redis에 저장할 때 어떤 자료구조를 쓸 것인가?"를 요구사항(조회 패턴, 업데이트 패턴, 메모리 효율)에 따라 판단 가능. |

---

### Step 4. 자료구조 심화 — Stream, Bitmap, HyperLogLog, Geospatial

| 학습 항목 | 학습 목표 |
|----------|----------|
| Stream | Kafka 스타일의 이벤트 로그. XADD/XREAD/XRANGE. Consumer Group 지원. Kafka와의 차이(Redis Stream은 경량, 소규모에 적합)를 설명 가능. |
| Bitmap | 비트 단위 연산. SETBIT/GETBIT/BITCOUNT. 일별 활성 사용자(DAU) 추적에 활용. 1억 사용자도 12.5MB로 추적 가능한 이유를 설명 가능. |
| HyperLogLog | 확률적 자료구조로 고유 원소 수(카디널리티) 근사 추정. PFADD/PFCOUNT. 오차 0.81%. 정확한 COUNT DISTINCT 대비 극소 메모리(12KB)로 추정 가능한 이유를 설명 가능. UV(Unique Visitor) 집계에 활용. |
| Geospatial | 위도/경도 기반 위치 데이터. GEOADD/GEODIST/GEORADIUS. "주변 N km 이내 매장 검색"에 활용. 내부적으로 Sorted Set 사용. |

---

### Step 5. 캐시 전략 — Cache Aside, Read/Write Through, Write Behind

| 학습 항목 | 학습 목표 |
|----------|----------|
| Cache Aside (Lazy Loading) | 읽기: 캐시 확인 → 없으면(Cache Miss) DB 조회 → 캐시에 저장 → 반환. 쓰기: DB에 쓰고 캐시 무효화(삭제). 가장 일반적인 패턴. 장점(필요한 데이터만 캐시)과 단점(첫 요청 항상 Cache Miss)을 설명 가능. |
| Read Through | Cache Aside와 유사하지만 캐시 라이브러리가 DB 조회를 자동 수행. 애플리케이션 코드가 단순해지는 장점. |
| Write Through | 쓰기: 캐시에 먼저 쓰고 → 캐시가 DB에도 동기적으로 쓰기. 캐시와 DB가 항상 일치. 단점(모든 쓰기에 지연 추가, 사용 안 하는 데이터도 캐시에 저장)을 설명 가능. |
| Write Behind (Write Back) | 쓰기: 캐시에만 쓰고 → 나중에 비동기로 DB에 반영. 쓰기 성능 극대화. 단점(캐시 장애 시 데이터 유실 위험)을 설명 가능. |
| 캐시 전략 선택 기준 | 읽기 Heavy → Cache Aside, 읽기/쓰기 일관성 필수 → Write Through, 쓰기 Heavy + 유실 감수 → Write Behind. 비즈니스 요구에 맞게 판단 가능. |

---

### Step 6. 캐시 문제 — 스탬피드, 관통, 눈사태, TTL 설계

| 학습 항목 | 학습 목표 |
|----------|----------|
| 캐시 스탬피드 (Cache Stampede / Thundering Herd) | 인기 키의 TTL 만료 시 동시에 수백 요청이 DB로 몰리는 현상. 대응: ① 뮤텍스(분산 락으로 1개 요청만 DB 조회), ② TTL에 랜덤 오프셋 추가(Jitter), ③ 논리적 만료(TTL 전에 백그라운드 갱신). |
| 캐시 관통 (Cache Penetration) | 존재하지 않는 키를 반복 조회 → 항상 Cache Miss → DB 부하. 대응: ① null 값도 캐시(짧은 TTL), ② Bloom Filter로 존재 여부 사전 필터링. |
| 캐시 눈사태 (Cache Avalanche) | 대량의 키가 동시에 만료 → 동시 DB 부하 폭증. 대응: ① TTL에 랜덤 값 분산, ② 캐시 워밍(미리 적재), ③ 다단계 캐시(L1 로컬 + L2 Redis). |
| 캐시 불일치 (Cache Inconsistency) | DB는 변경됐는데 캐시는 옛날 값을 가지고 있는 문제. Cache Aside에서 "DB 쓰기 → 캐시 삭제" 순서의 중요성(반대로 하면 Race Condition)을 설명 가능. 이벤트 기반 캐시 무효화(CDC, 메시지 큐)를 설명 가능. |
| TTL 설계 | 너무 짧으면 Cache Miss 증가, 너무 길면 stale 데이터 위험. 데이터 변경 빈도와 일관성 요구 수준에 따라 TTL을 설계하는 판단 기준을 설명 가능. |

---

### Step 7. 분산 락 — SETNX, Redisson, Redlock 알고리즘

| 학습 항목 | 학습 목표 |
|----------|----------|
| 왜 분산 락이 필요한가 | 여러 서버에서 동시에 같은 자원(재고, 포인트 등)을 수정할 때 Race Condition을 방지하는 이유를 설명 가능. DB Lock과의 차이(Redis Lock은 DB 부하 없이 빠른 락 획득/해제)를 설명 가능. |
| SETNX 기반 락 | `SET key value NX EX 30`(키가 없을 때만 설정 + 만료 30초). 락 획득 → 작업 → DEL(락 해제) 기본 패턴. DEL 전에 프로세스 죽으면 EX로 자동 해제되는 이유를 설명 가능. |
| SETNX의 문제점 | ① 락 소유자가 아닌 다른 프로세스가 DEL 가능(소유권 검증 없음) → value에 UUID 저장 + Lua 스크립트로 원자적 검증 후 삭제 필요. ② TTL 내 작업 미완료 시 다른 프로세스가 락 획득(Fencing 문제). |
| Redisson | Java 기반 Redis 클라이언트. RLock 인터페이스로 분산 락을 간편하게 사용. Watchdog이 자동으로 락 TTL을 연장하여 작업 완료 전 만료 방지. tryLock(waitTime, leaseTime, unit) 사용법을 적용 가능. |
| Redlock 알고리즘 | 단일 Redis 장애 시에도 락을 보장하기 위해 N대(보통 5대) 중 과반수(N/2+1)에서 락을 획득하는 알고리즘. Martin Kleppmann의 Redlock 비판(시계 의존성)을 개념 수준 설명 가능. 실무에서 단일 Redis + Redisson이 더 일반적인 이유를 설명 가능. |
| Fencing Token (심화) | Watchdog이 연장해도 GC Pause/네트워크 지연으로 락이 만료된 후 프로세스가 작업을 계속하는 시나리오를 설명 가능. Fencing Token(단조 증가 ID)을 발급하여 DB/스토리지에 쓸 때 "이 토큰이 현재 유효한지"를 검증하는 패턴을 설명 가능. "분산 락을 썼다"가 아니라 "락이 만료되는 예외 상황에서도 정합성을 보장한다"는 설계 철학을 설명 가능. (DDIA Step 7 분산 시스템의 어려움과 연계) |
| 분산 락 vs DB 비관적 락 | Redis 분산 락: DB 부하 없음, 빠름, TTL 자동 해제. DB 비관적 락(SELECT FOR UPDATE): DB 트랜잭션과 통합, 데이터 정합성 확실. 선택 기준(성능 vs 정합성)을 설명 가능. |

---

### Step 8. Pub/Sub + Stream

| 학습 항목 | 학습 목표 |
|----------|----------|
| Pub/Sub 개념 | PUBLISH/SUBSCRIBE로 실시간 메시지 전달. 메시지가 저장되지 않음(수신자가 없으면 유실). 실시간 알림, 채팅, 이벤트 브로드캐스트에 활용. |
| Pub/Sub의 한계 | 메시지 영속성 없음, 재생 불가, Consumer Group 없음. Kafka와의 차이(Kafka는 영속적, 재생 가능, Consumer Group 지원)를 설명 가능. |
| Redis Stream | Kafka 스타일의 이벤트 로그. 영속적이고 Consumer Group 지원. Pub/Sub의 한계를 보완. 소규모 이벤트 스트리밍에 적합한 이유를 설명 가능. |
| Pub/Sub vs Stream vs Kafka 선택 기준 | 실시간 브로드캐스트(유실 허용) → Pub/Sub, 소규모 이벤트 스트리밍(영속 필요) → Stream, 대규모 이벤트 스트리밍 → Kafka. |

---

### Step 9. 영속성 — RDB, AOF, 혼합 모드

| 학습 항목 | 학습 목표 |
|----------|----------|
| 인메모리의 위험 | Redis 재시작 시 모든 데이터 유실. 영속성 옵션이 필요한 이유를 설명 가능. |
| RDB (Redis Database) | 특정 시점 스냅샷을 디스크에 저장. SAVE/BGSAVE. 장점(복구 빠름, 파일 크기 작음)과 단점(마지막 스냅샷 이후 데이터 유실 가능)을 설명 가능. |
| AOF (Append Only File) | 모든 쓰기 명령을 로그로 기록. appendfsync(always/everysec/no)의 트레이드오프(내구성 vs 성능)를 설명 가능. 장점(데이터 유실 최소화)과 단점(파일 크기 큼, 복구 느림)을 설명 가능. |
| 혼합 모드 (RDB + AOF) | Redis 4.0+에서 RDB 스냅샷 + 이후 변경분을 AOF로 기록하는 혼합 방식. 복구 속도와 내구성 모두 확보. 실무에서 권장되는 이유를 설명 가능. |
| 영속성 설정 판단 | 캐시 전용(영속성 불필요) vs 데이터 저장소(영속성 필수)에 따른 설정 판단 가능. |

---

### Step 10. 메모리 관리 — maxmemory-policy, Eviction 전략

| 학습 항목 | 학습 목표 |
|----------|----------|
| maxmemory 설정 | Redis가 사용할 최대 메모리 설정. 설정하지 않으면 시스템 메모리를 모두 사용하여 OOM 위험을 설명 가능. |
| Eviction 정책 | noeviction(메모리 초과 시 에러), allkeys-lru(가장 오래 안 쓴 키 제거), volatile-lru(TTL 있는 키 중 LRU 제거), allkeys-lfu(가장 적게 쓴 키 제거), volatile-ttl(TTL 짧은 키 우선 제거). 각 정책의 차이와 선택 기준을 설명 가능. |
| LRU vs LFU | LRU(Least Recently Used): 최근 사용 시간 기준. LFU(Least Frequently Used): 사용 빈도 기준. 인기 있는 키가 잠시 안 쓰였을 때 제거되는 LRU의 문제를 LFU가 해결하는 이유를 설명 가능. |
| 메모리 최적화 | 작은 데이터에 ziplist/listpack 인코딩이 적용되는 이유(메모리 절약)를 설명 가능. OBJECT ENCODING으로 확인하는 방법을 알고 있음. |
| 메모리 사용량 모니터링 | INFO memory 명령으로 used_memory, maxmemory, fragmentation_ratio를 확인하고 해석 가능. |
| RSS vs Used Memory (심화) | used_memory(Redis가 실제 사용하는 메모리)와 used_memory_rss(OS가 할당한 물리 메모리)의 차이를 설명 가능. RSS > Used Memory이면 단편화 발생(fragmentation_ratio > 1). 장기 운영 시 잦은 할당/해제로 단편화가 누적되어 실제 사용량 대비 메모리를 과다 점유하는 문제를 설명 가능. |
| Active Defrag (심화) | Redis 4.0+의 activedefrag yes 설정으로 런타임에 메모리 단편화를 자동 해소하는 기능. active-defrag-threshold-lower/upper, active-defrag-cycle-min/max 설정의 의미를 설명 가능. 재시작 없이 단편화를 줄이는 운영 기법으로 활용 가능. |

---

### Step 11. 고가용성 — Sentinel

| 학습 항목 | 학습 목표 |
|----------|----------|
| Sentinel 개요 | Redis 마스터/슬레이브 구성에서 마스터 장애 시 자동 페일오버를 수행하는 모니터링 시스템. |
| 마스터-슬레이브 복제 | 마스터(읽기/쓰기) + 슬레이브(읽기 전용, 데이터 복제)의 구조. 비동기 복제이므로 마스터 장애 시 일부 데이터 유실 가능성을 설명 가능. |
| Sentinel의 역할 | 모니터링(마스터 상태 감시), 알림(장애 통보), 자동 페일오버(슬레이브를 마스터로 승격), 설정 제공(클라이언트에 현재 마스터 주소 제공)을 설명 가능. |
| Sentinel 최소 구성 | Sentinel 3대(과반수 합의 필요)로 Split Brain을 방지하는 이유를 설명 가능. |

---

### Step 12. 수평 확장 — Redis Cluster

| 학습 항목 | 학습 목표 |
|----------|----------|
| Redis Cluster 개요 | 데이터를 여러 노드에 분산 저장(샤딩). 16384개 해시 슬롯을 노드에 배분하는 구조를 설명 가능. |
| 해시 슬롯 | CRC16(key) % 16384로 슬롯 결정. 특정 키가 어느 노드에 저장되는지 알 수 있음. 해시 태그({tag})로 관련 키를 같은 슬롯에 강제 배치하는 방법을 설명 가능. |
| 클러스터 제약사항 | 다중 키 명령(MGET, MSET)은 같은 슬롯의 키만 가능. 트랜잭션(MULTI/EXEC)도 같은 슬롯 제약. 이 제약이 설계에 미치는 영향을 설명 가능. |
| 노드 추가/제거 | 슬롯 재배치(Resharding)으로 데이터 이동. 운영 중 무중단 확장 가능. |
| Sentinel vs Cluster | Sentinel: 고가용성(HA)만, 단일 마스터. Cluster: HA + 수평 확장(다중 마스터). 데이터 크기/트래픽에 따른 선택 기준을 설명 가능. |

---

### Step 13. Spring Data Redis 연동 — RedisTemplate, @Cacheable

| 학습 항목 | 학습 목표 |
|----------|----------|
| spring-boot-starter-data-redis | 의존성 추가 시 자동 설정되는 항목. Lettuce(기본)와 Jedis 클라이언트의 차이(Lettuce: 비동기, Netty 기반, 커넥션 공유)를 설명 가능. |
| RedisTemplate | opsForValue/opsForHash/opsForList/opsForSet/opsForZSet으로 자료구조별 연산 수행 가능. |
| @Cacheable / @CacheEvict / @CachePut | Spring Cache Abstraction으로 메서드 결과를 Redis에 자동 캐시하는 방법. key, condition, unless 속성을 설정 가능. |
| application.yml 설정 | spring.data.redis.host, port, password, timeout 설정 작성 가능. |
| CacheManager 설정 | RedisCacheManager로 기본 TTL, 캐시별 TTL을 다르게 설정하는 방법을 적용 가능. |

---

### Step 14. Spring Data Redis 심화 — 직렬화, 세션 관리, 트랜잭션

| 학습 항목 | 학습 목표 |
|----------|----------|
| 직렬화 (Serializer) | JdkSerializationRedisSerializer(기본, 가독성 나쁨, 호환성 위험) vs StringRedisSerializer vs Jackson2JsonRedisSerializer vs GenericJackson2JsonRedisSerializer의 차이와 선택 기준을 설명 가능. 실무에서 JSON Serializer를 권장하는 이유(가독성, 언어 독립성)를 설명 가능. |
| Spring Session + Redis | 세션을 Redis에 저장하여 다중 서버 환경에서 세션 공유하는 패턴. spring-session-data-redis 설정 방법을 알고 있음. |
| Redis 트랜잭션 | MULTI/EXEC로 여러 명령을 원자적 실행. 단, 롤백이 안 되는 제약(실패한 명령만 무시, 나머지는 실행)을 설명 가능. Lua 스크립트로 진정한 원자적 연산을 구현하는 방법을 알고 있음. |
| Redis 파이프라이닝 | 여러 명령을 한 번에 보내고 응답을 모아 받는 기법. 네트워크 왕복 횟수를 줄여 성능 향상하는 원리를 설명 가능. RedisTemplate에서 executePipelined 사용법을 알고 있음. |

---

### Step 15. Redis 성능 — 싱글 스레드 모델, 파이프라이닝, 느린 명령어

| 학습 항목 | 학습 목표 |
|----------|----------|
| 싱글 스레드 모델 | Redis가 싱글 스레드임에도 초당 10만+ 요청을 처리하는 이유(IO 멀티플렉싱, 인메모리 연산, 커널 레벨 최적화)를 설명 가능. 싱글 스레드이므로 긴 명령어 1개가 전체를 블로킹하는 위험을 설명 가능. |
| IO 멀티플렉싱 (epoll) | 하나의 스레드가 여러 클라이언트의 소켓을 동시 감시하여 준비된 요청만 처리하는 원리를 개념 수준 설명 가능. |
| Redis 6.0+ IO 스레드 | 네트워크 I/O 처리만 멀티스레드로 분리하되, 명령 실행은 여전히 싱글 스레드인 구조를 설명 가능. |
| 느린 명령어 주의 | KEYS *(전체 키 스캔, O(n)), SMEMBERS(대량 Set), SORT(정렬) 등이 프로덕션에서 위험한 이유. SCAN으로 대체하는 이유를 설명 가능. |
| SLOWLOG | SLOWLOG GET으로 느린 명령어를 조회하고 원인을 분석하는 방법을 알고 있음. |
| Client-side Caching (Redis 6+, 심화) | 클라이언트가 자주 읽는 키를 로컬 메모리에 캐시하고, Redis 서버가 해당 키가 변경되면 Invalidation 메시지를 보내 로컬 캐시를 무효화하는 원리를 설명 가능. "캐시의 캐시"로 네트워크 왕복(RTT)을 극단적으로 줄이는 효과를 설명 가능. Tracking 모드(기본: 서버가 키별 클라이언트 추적, Broadcasting: 프리픽스 기반 브로드캐스트)의 차이를 개념 수준 설명 가능. |

---

### Step 16. Redis 트러블슈팅 + 모니터링

| 학습 항목 | 학습 목표 |
|----------|----------|
| INFO 명령 | INFO server/clients/memory/stats/replication/keyspace 각 섹션의 핵심 지표를 읽고 해석 가능. |
| 핵심 모니터링 지표 | used_memory(메모리 사용량), connected_clients(접속 클라이언트 수), instantaneous_ops_per_sec(초당 명령 수), keyspace_hits/misses(캐시 히트율), evicted_keys(제거된 키 수)를 모니터링 가능. |
| 메모리 단편화 | mem_fragmentation_ratio가 1보다 크게 높으면 단편화 발생. 원인(잦은 할당/해제)과 대응(MEMORY PURGE, 재시작)을 설명 가능. |
| 연결 고갈 | maxclients 초과 시 새 연결 거부. 커넥션 풀 크기와 연결 수의 관계. 커넥션 누수 진단(CLIENT LIST)을 설명 가능. |
| Prometheus + Grafana 연동 | Redis Exporter로 메트릭을 Prometheus에 노출하고 Grafana 대시보드로 시각화하는 구조를 알고 있음. |
| 장애 대응 순서 | "Redis가 느려졌다" → SLOWLOG 확인 → INFO memory(메모리 부족?) → INFO clients(연결 폭주?) → KEYS 등 O(n) 명령 확인 → 네트워크 문제 확인 순서를 설명 가능. |
| ACL (Redis 6+, 심화) | 기존 requirepass(단일 비밀번호, 모든 권한) 방식의 한계를 설명 가능. ACL로 사용자별 허용 명령어/키 패턴을 세분화(예: 읽기 전용 사용자, 특정 프리픽스 키만 접근 가능)하는 방법을 설명 가능. ACL SETUSER, ACL LIST, ACL LOG 사용법을 알고 있음. 금융/엔터프라이즈 환경에서 보안 계정 분리가 필요한 이유를 설명 가능. |

---

## 3. 자가 검증

### 기초 / 자료구조
- [ ] "Redis의 자료구조 5가지와 각각의 활용 사례" 즉시 답변 가능
- [ ] "Hash vs String(JSON)으로 객체를 저장할 때의 차이" 설명 가능
- [ ] "Sorted Set으로 리더보드를 구현하는 방법" 설명 가능
- [ ] redis-cli로 기본 CRUD + TTL 설정 가능

### 캐시
- [ ] "Cache Aside 패턴의 동작과 장단점" 설명 가능
- [ ] "캐시 스탬피드란? 어떻게 방지하는가?" → 뮤텍스, Jitter, 백그라운드 갱신 설명 가능
- [ ] "캐시 관통이란? 어떻게 방지하는가?" → null 캐시, Bloom Filter 설명 가능
- [ ] "DB는 변경됐는데 캐시가 옛날 값이면?" → 캐시 무효화 전략 설명 가능

### 분산 락
- [ ] "SETNX 기반 분산 락의 문제점" → 소유권 검증, Fencing 설명 가능
- [ ] "Redisson의 Watchdog이란?" → 락 TTL 자동 연장 설명 가능
- [ ] "Redlock 알고리즘과 그 비판" 개념 수준 설명 가능
- [ ] "락이 만료된 후에도 프로세스가 작업을 계속하면?" → Fencing Token으로 정합성 보장 설명 가능

### 아키텍처
- [ ] "Sentinel vs Cluster 선택 기준" 설명 가능
- [ ] "Redis Cluster의 해시 슬롯이란?" 설명 가능
- [ ] "RDB vs AOF 차이와 혼합 모드" 설명 가능

### 성능 / 운영
- [ ] "RSS vs Used Memory 차이와 메모리 단편화 진단" → fragmentation_ratio + Active Defrag 설명 가능
- [ ] "Redis가 싱글 스레드인데 왜 빠른가?" → IO 멀티플렉싱 + 인메모리 설명 가능
- [ ] "Client-side Caching이란?" → 로컬 캐시 + Invalidation 메커니즘 설명 가능
- [ ] "KEYS * 명령이 프로덕션에서 위험한 이유" → O(n) 블로킹 + SCAN 대안 설명 가능
- [ ] "Redis 메모리 사용량 모니터링 + Eviction 정책 설정" 가능
- [ ] "Redis가 느려졌을 때 진단 순서" 설명 가능

### Spring 연동
- [ ] RedisTemplate + @Cacheable로 캐시 구현 가능
- [ ] "JDK Serializer를 쓰면 안 되는 이유" → JSON Serializer 권장 설명 가능
- [ ] "Redis ACL이란? 왜 필요한가?" → 사용자별 명령어/키 권한 분리 설명 가능

---

## 4. 진행 상태

| Step | 항목 | 상태 |
|------|------|------|
| Step 1 | Redis 개요 | 미시작 |
| Step 2 | 환경 구축 | 미시작 |
| Step 3 | 자료구조 기본 | 미시작 |
| Step 4 | 자료구조 심화 | 미시작 |
| Step 5 | 캐시 전략 | 미시작 |
| Step 6 | 캐시 문제 | 미시작 |
| Step 7 | 분산 락 | 미시작 |
| Step 8 | Pub/Sub + Stream | 미시작 |
| Step 9 | 영속성 | 미시작 |
| Step 10 | 메모리 관리 | 미시작 |
| Step 11 | Sentinel | 미시작 |
| Step 12 | Redis Cluster | 미시작 |
| Step 13 | Spring Data Redis 기본 | 미시작 |
| Step 14 | Spring Data Redis 심화 | 미시작 |
| Step 15 | Redis 성능 | 미시작 |
| Step 16 | 트러블슈팅 + 모니터링 | 미시작 |

---

## 5. 참고 자료 (보조용)

| 자료 | 용도 |
|------|------|
| Redis in Action (Josiah Carlson) | Step 1~8 보조. 자료구조/캐시/분산 락 |
| Redis 공식 문서 (redis.io) | 전 Step 명령어/설정 레퍼런스 |
| Spring Data Redis 공식 문서 | Step 13~14 보조 |

---

> 이 문서는 Claude가 미래 세션에서 읽고 학습을 안내하기 위한 가이드입니다.
> 사용자가 "Redis 공부하자" 또는 "Step N 하자"라고 하면, 진행 상태를 확인하고 다음 미시작 Step부터 학습_템플릿.md 형식으로 진행합니다.
