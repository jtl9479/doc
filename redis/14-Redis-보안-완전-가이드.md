# Redis 14장: Redis 보안 완전 가이드

> **학습 목표**: 프로덕션 환경에서 Redis를 안전하게 운영하기 위한 보안 설정과 모범 사례 습득

**⏱️ 예상 학습 시간**: 4-6시간
**난이도**: ⭐⭐⭐⭐☆ (4개/5개)

---

## 📚 목차
- [왜 이 기술이 필요한가](#왜-이-기술이-필요한가)
- [실생활 비유로 이해하기](#실생활-비유로-이해하기)
- [인증 및 패스워드 설정](#1-인증-및-패스워드-설정)
- [ACL (Access Control List)](#2-acl-access-control-list)
- [네트워크 보안](#3-네트워크-보안)
- [SSL/TLS 암호화](#4-ssltls-암호화)
- [명령어 금지 및 제한](#5-명령어-금지-및-제한)
- [보안 감사 및 로깅](#6-보안-감사-및-로깅)
- [프로덕션 보안 체크리스트](#7-프로덕션-보안-체크리스트)
- [주니어 시나리오](#주니어-시나리오)
- [FAQ](#faq)
- [면접 질문 리스트](#면접-질문-리스트)
- [핵심 정리](#핵심-정리)

---

## 🤔 왜 이 기술이 필요한가?

### 실무 배경
**2019년 6월, 8,000개 이상의 Redis 인스턴스가 랜섬웨어 공격을 받아 데이터가 암호화되고 비트코인 요구**

#### ❌ Redis 보안을 모르면 발생하는 문제

```
문제 1: 랜섬웨어 공격으로 데이터 암호화
- 증상: 외부에서 Redis 접근 → 모든 데이터 삭제 → 랜섬 요구
- 영향: 사용자 세션, 캐시 데이터 전체 손실, 서비스 중단
- 비용: 비트코인 0.1 BTC (약 $5,000) 요구 + 복구 비용 $50,000
- 근본 원인: 패스워드 미설정, 외부 접근 허용

문제 2: 데이터 유출로 개인정보 노출
- 증상: 해커가 Redis에 저장된 세션 토큰 탈취 → 계정 도용
- 영향: 10만 명 사용자 계정 탈취, 개인정보 유출
- 비용: GDPR 위반으로 €2,000,000 벌금 + 소송 비용
- 근본 원인: 암호화 미적용, 취약한 접근 제어

문제 3: 악의적인 명령어로 서버 장애
- 증상: 공격자가 FLUSHALL 명령 실행 → 모든 데이터 삭제
- 영향: 3시간 다운타임, 매출 손실 $100,000
- 비용: 데이터 복구 불가, 고객 신뢰 상실
- 근본 원인: 위험 명령어 차단 미설정
```

#### ✅ Redis 보안을 적용하면

```
해결책 1: 다층 방어로 랜섬웨어 차단
- 방법:
  1. 강력한 패스워드 설정
  2. 외부 접근 차단 (bind 127.0.0.1)
  3. 방화벽 설정
  4. ACL로 권한 제한
- 효과: 랜섬웨어 공격 100% 차단
- 절감: 랜섬 지불 및 복구 비용 $0

해결책 2: SSL/TLS로 데이터 암호화
- 방법: Redis 6.0+ SSL/TLS 적용
- 효과: 전송 중 데이터 암호화, 중간자 공격 방지
- 절감: GDPR 준수, 벌금 위험 제거

해결책 3: 명령어 제한으로 악의적 행위 차단
- 방법: FLUSHALL, KEYS 등 위험 명령어 rename/disable
- 효과: 데이터 삭제 공격 불가능
- 절감: 다운타임 0, 매출 손실 0
```

### 📊 수치로 보는 효과

| 지표 | Before (보안 미적용) | After (보안 적용) | 개선율 |
|------|---------------------|------------------|--------|
| 보안 사고 발생률 | 월 2-3회 | 연 0회 | **100%↓** |
| 랜섬웨어 피해액 | $55,000/회 | $0 | **100%↓** |
| GDPR 벌금 위험 | €2,000,000 | €0 | **100%↓** |
| 다운타임 | 월 10시간 | 연 0시간 | **100%↓** |
| 고객 신뢰도 | 65% | 95% | **46%↑** |

### 실제 보안 사고 사례

#### 사례 1: Redis 랜섬웨어 (2019)
```
공격 방법:
1. Shodan으로 외부 접근 가능한 Redis 인스턴스 검색
2. 패스워드 없는 Redis 발견
3. FLUSHALL로 모든 데이터 삭제
4. 비트코인 요구 메시지 저장

피해:
- 8,000+ Redis 인스턴스 감염
- 데이터 복구 불가
- 평균 피해액: $5,000-$50,000

예방 방법:
✅ requirepass 설정
✅ bind 127.0.0.1 (외부 접근 차단)
✅ 방화벽 규칙 설정
```

#### 사례 2: 세션 탈취 공격 (2020)
```
공격 방법:
1. Redis 트래픽 스니핑 (암호화 없음)
2. 세션 토큰 탈취
3. 탈취한 토큰으로 계정 로그인

피해:
- 10만 명 계정 도용
- 개인정보 유출
- GDPR 벌금 €2,000,000

예방 방법:
✅ SSL/TLS 암호화
✅ 세션 토큰 암호화
✅ IP 화이트리스트
```

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 은행 금고 보안 시스템 🏦

```
Redis 보안 = 은행 금고 보안

1층 보안 (네트워크):
- 은행 건물 출입 통제 = 방화벽, bind 설정
- 은행에 들어올 수 있는 사람만 제한

2층 보안 (인증):
- 금고실 출입 카드 = requirepass (패스워드)
- 인증된 직원만 접근 가능

3층 보안 (권한):
- 금고 열쇠 권한 분리 = ACL
- 관리자: 모든 금고 접근
- 직원: 일부 금고만 접근
- 고객: 자기 금고만 접근

4층 보안 (암호화):
- 금고 내 중요 서류 암호화 = SSL/TLS
- 도난 당해도 읽을 수 없음

5층 보안 (명령어 제한):
- 특정 행동 금지 = rename-command
- "모든 금고 열기" 버튼 제거 (FLUSHALL 차단)

┌─────────────────────────────────────┐
│         은행 금고 보안              │
│  [출입통제] → [카드인증] → [권한확인]│
│      ↓           ↓           ↓      │
│  방화벽      requirepass    ACL     │
│                                     │
│  [암호화 서류] + [위험 행동 차단]   │
│       ↓                ↓            │
│    SSL/TLS      rename-command      │
└─────────────────────────────────────┘
```

### 비유 2: 아파트 보안 시스템 🏢

```
1. 외부 출입 통제 (bind)
   - 아파트 정문 경비 = bind 127.0.0.1
   - 외부인 출입 차단

2. 출입증 검사 (requirepass)
   - 출입증 태그 = 패스워드 입력
   - 출입증 없으면 들어올 수 없음

3. 층별 권한 (ACL)
   - 주민: 자기 층만 접근
   - 경비: 전체 층 접근
   - 택배: 1층만 접근

4. CCTV 암호화 (SSL/TLS)
   - CCTV 영상 암호화 = 데이터 암호화
   - 해킹당해도 영상 못 봄

5. 위험 행동 차단 (rename-command)
   - "모든 집 문 열기" 버튼 제거
   - "전기 차단" 버튼 제거
```

---

## 1. 인증 및 패스워드 설정

### 1.1 requirepass 설정

#### redis.conf 설정
```bash
# redis.conf

# 패스워드 설정 (강력한 패스워드 사용!)
requirepass your_strong_password_here_min_32_chars

# ❌ 나쁜 예
requirepass 123456
requirepass password
requirepass admin

# ✅ 좋은 예 (최소 32자, 대소문자+숫자+특수문자)
requirepass Xk9$mP2#qR7@nF4!wL8&bT1^cY6*sE3%vH5
```

#### 강력한 패스워드 생성
```bash
# Linux/Mac에서 랜덤 패스워드 생성
openssl rand -base64 32

# 출력 예시
Xk9$mP2#qR7@nF4!wL8&bT1^cY6*sE3%vH5ZjA0=
```

#### CLI에서 인증
```bash
# 방법 1: 연결 후 인증
redis-cli
127.0.0.1:6379> AUTH your_strong_password_here
OK

# 방법 2: 연결 시 인증
redis-cli -a your_strong_password_here

# 방법 3: 환경 변수 사용 (패스워드 숨김)
export REDISCLI_AUTH=your_strong_password_here
redis-cli
```

#### 프로그래밍 언어별 인증

**Python**
```python
import redis

r = redis.Redis(
    host='localhost',
    port=6379,
    password='your_strong_password_here',
    decode_responses=True
)

# 연결 테스트
print(r.ping())  # True
```

**Java**
```java
Jedis jedis = new Jedis("localhost", 6379);
jedis.auth("your_strong_password_here");

// 또는 JedisPool 사용
JedisPool pool = new JedisPool(
    config,
    "localhost",
    6379,
    2000,  // timeout
    "your_strong_password_here"
);
```

**Node.js**
```javascript
const Redis = require('ioredis');

const redis = new Redis({
  host: 'localhost',
  port: 6379,
  password: 'your_strong_password_here'
});
```

### 1.2 패스워드 로테이션

```bash
# 1. 새 패스워드 생성
NEW_PASSWORD=$(openssl rand -base64 32)

# 2. Redis 설정 변경 (재시작 없이)
redis-cli -a OLD_PASSWORD CONFIG SET requirepass $NEW_PASSWORD

# 3. 새 패스워드로 연결 테스트
redis-cli -a $NEW_PASSWORD PING

# 4. redis.conf 파일 업데이트
echo "requirepass $NEW_PASSWORD" >> /etc/redis/redis.conf

# 5. 모든 애플리케이션 설정 업데이트
```

---

## 2. ACL (Access Control List)

### 2.1 ACL 기본 개념 (Redis 6.0+)

```bash
# 현재 사용자 확인
127.0.0.1:6379> ACL WHOAMI
"default"

# 모든 사용자 목록
127.0.0.1:6379> ACL LIST
1) "user default on nopass ~* &* +@all"

# 설명:
# - user default: 사용자 이름
# - on: 활성화
# - nopass: 패스워드 없음 (위험!)
# - ~*: 모든 키 접근 가능
# - &*: 모든 채널 접근 가능
# - +@all: 모든 명령 실행 가능
```

### 2.2 사용자 생성 및 권한 부여

#### 읽기 전용 사용자
```bash
# 읽기 전용 사용자 생성
ACL SETUSER readonly on >readonly_password ~* +@read

# 설명:
# - readonly: 사용자 이름
# - on: 활성화
# - >readonly_password: 패스워드 설정
# - ~*: 모든 키 접근
# - +@read: 읽기 명령만 허용 (GET, HGETALL 등)

# 테스트
redis-cli -u redis://readonly:readonly_password@localhost:6379
127.0.0.1:6379> GET mykey
"value"
127.0.0.1:6379> SET mykey newvalue
(error) NOPERM this user has no permissions to run the 'set' command
```

#### 특정 키 패턴만 접근
```bash
# user:* 키만 접근 가능한 사용자
ACL SETUSER user_manager on >user_pass ~user:* +@all

# session:* 키만 접근 가능한 사용자
ACL SETUSER session_manager on >session_pass ~session:* +@all

# 테스트
redis-cli -u redis://user_manager:user_pass@localhost:6379
127.0.0.1:6379> SET user:1001 "data"
OK
127.0.0.1:6379> SET product:1001 "data"
(error) NOPERM this user has no permissions to access one of the keys
```

#### 애플리케이션별 사용자
```bash
# 웹 애플리케이션 사용자 (읽기/쓰기, 위험 명령 차단)
ACL SETUSER webapp on >webapp_password ~* +@all -@dangerous

# 분석 도구 사용자 (읽기 전용)
ACL SETUSER analytics on >analytics_password ~* +@read

# 관리자 사용자 (모든 권한)
ACL SETUSER admin on >admin_password ~* &* +@all
```

### 2.3 명령어 카테고리

```bash
# 주요 명령어 카테고리
@read       # GET, HGETALL, LRANGE 등
@write      # SET, HSET, LPUSH 등
@admin      # CONFIG, SHUTDOWN 등
@dangerous  # FLUSHALL, FLUSHDB, KEYS 등
@keyspace   # DEL, EXISTS, EXPIRE 등
@string     # String 타입 명령
@hash       # Hash 타입 명령
@list       # List 타입 명령
@set        # Set 타입 명령
@sortedset  # Sorted Set 타입 명령

# 예시: 읽기 + 쓰기만 허용, 위험 명령 차단
ACL SETUSER safe_user on >password ~* +@read +@write -@dangerous
```

### 2.4 ACL 영구 저장

```bash
# ACL 파일로 저장
ACL SAVE

# redis.conf 설정
aclfile /etc/redis/users.acl

# users.acl 파일 예시
user default on nopass ~* &* +@all
user readonly on >readonly_pass ~* +@read
user webapp on >webapp_pass ~* +@all -@dangerous
user admin on >admin_pass ~* &* +@all
```

---

## 3. 네트워크 보안

### 3.1 bind 설정 (가장 중요!)

#### redis.conf 설정
```bash
# ❌ 위험: 모든 IP에서 접근 가능
bind 0.0.0.0

# ✅ 안전: 로컬호스트만 접근 가능
bind 127.0.0.1

# ✅ 안전: 특정 IP만 접근 가능
bind 127.0.0.1 192.168.1.10 10.0.0.5

# ✅ 안전: 내부 네트워크만 (VPC)
bind 10.0.1.100  # VPC 내부 IP
```

#### protected-mode 활성화
```bash
# redis.conf

# protected-mode on (기본값, 권장)
protected-mode yes

# 설명:
# - bind가 설정되지 않았거나
# - requirepass가 설정되지 않은 경우
# - 외부 연결을 자동으로 거부
```

### 3.2 방화벽 설정

#### Linux (iptables)
```bash
# Redis 포트(6379)를 특정 IP에서만 허용
sudo iptables -A INPUT -p tcp --dport 6379 -s 192.168.1.10 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 6379 -j DROP

# 방화벽 규칙 저장
sudo iptables-save > /etc/iptables/rules.v4
```

#### Ubuntu (ufw)
```bash
# 기본적으로 모든 접근 거부
sudo ufw default deny incoming

# 특정 IP에서만 Redis 접근 허용
sudo ufw allow from 192.168.1.10 to any port 6379

# SSH는 허용 (서버 접근용)
sudo ufw allow 22

# 방화벽 활성화
sudo ufw enable
```

#### AWS Security Group
```
Inbound Rules:
- Type: Custom TCP
- Port: 6379
- Source: 10.0.1.0/24 (VPC CIDR)
- Description: Redis access from VPC only
```

### 3.3 VPN/VPC 내부망 구성

```
✅ 권장 아키텍처:

인터넷
  ↓
[Load Balancer] (Public Subnet)
  ↓
[Web Servers] (Private Subnet)
  ↓
[Redis Cluster] (Private Subnet - 외부 접근 불가)
  ↓
[RDS Database] (Private Subnet - 외부 접근 불가)

보안 강점:
- Redis는 인터넷에서 직접 접근 불가
- 웹 서버만 Redis 접근 가능
- 모든 트래픽이 VPC 내부에서 암호화
```

---

## 4. SSL/TLS 암호화

### 4.1 SSL/TLS 인증서 생성

```bash
# 1. CA (Certificate Authority) 생성
openssl genrsa -out ca-key.pem 4096
openssl req -new -x509 -days 3650 -key ca-key.pem -out ca-cert.pem

# 2. Redis 서버 인증서 생성
openssl genrsa -out redis-server-key.pem 4096
openssl req -new -key redis-server-key.pem -out redis-server-req.pem
openssl x509 -req -days 3650 -in redis-server-req.pem \
  -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial \
  -out redis-server-cert.pem

# 3. 클라이언트 인증서 생성
openssl genrsa -out redis-client-key.pem 4096
openssl req -new -key redis-client-key.pem -out redis-client-req.pem
openssl x509 -req -days 3650 -in redis-client-req.pem \
  -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial \
  -out redis-client-cert.pem
```

### 4.2 Redis 서버 SSL 설정

#### redis.conf
```bash
# SSL/TLS 포트 활성화
port 0  # 기본 포트 비활성화
tls-port 6380  # SSL/TLS 포트

# 인증서 경로
tls-cert-file /etc/redis/ssl/redis-server-cert.pem
tls-key-file /etc/redis/ssl/redis-server-key.pem
tls-ca-cert-file /etc/redis/ssl/ca-cert.pem

# 클라이언트 인증 요구
tls-auth-clients yes

# TLS 버전 (1.2 이상)
tls-protocols "TLSv1.2 TLSv1.3"
```

### 4.3 클라이언트 SSL 연결

#### redis-cli
```bash
redis-cli --tls \
  --cert /path/to/redis-client-cert.pem \
  --key /path/to/redis-client-key.pem \
  --cacert /path/to/ca-cert.pem \
  -h localhost -p 6380
```

#### Python
```python
import redis

r = redis.Redis(
    host='localhost',
    port=6380,
    password='your_password',
    ssl=True,
    ssl_certfile='/path/to/redis-client-cert.pem',
    ssl_keyfile='/path/to/redis-client-key.pem',
    ssl_ca_certs='/path/to/ca-cert.pem',
    ssl_cert_reqs='required'
)
```

#### Java (Lettuce)
```java
SslOptions sslOptions = SslOptions.builder()
    .truststore(new File("/path/to/ca-cert.pem"))
    .keystore(new File("/path/to/redis-client-cert.pem"))
    .build();

RedisURI redisUri = RedisURI.builder()
    .withHost("localhost")
    .withPort(6380)
    .withPassword("your_password")
    .withSsl(true)
    .build();

RedisClient client = RedisClient.create(redisUri);
client.setOptions(ClientOptions.builder()
    .sslOptions(sslOptions)
    .build());
```

---

## 5. 명령어 금지 및 제한

### 5.1 위험한 명령어 차단

#### redis.conf
```bash
# 위험한 명령어 이름 변경 (사실상 비활성화)
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command KEYS ""
rename-command CONFIG ""
rename-command SHUTDOWN ""
rename-command DEBUG ""

# 또는 복잡한 이름으로 변경 (관리자만 사용)
rename-command FLUSHDB "FLUSHDB_SECRET_a8f3k2m9x1c7"
rename-command CONFIG "CONFIG_SECRET_z9y2w5q4t3r8"
```

### 5.2 SLOWLOG로 느린 쿼리 모니터링

```bash
# redis.conf

# 10ms 이상 걸리는 명령 기록
slowlog-log-slower-than 10000  # 마이크로초 (10ms)

# 최대 128개 슬로우 로그 저장
slowlog-max-len 128

# 슬로우 로그 확인
127.0.0.1:6379> SLOWLOG GET 10
1) 1) (integer) 2  # 로그 ID
   2) (integer) 1640000000  # 타임스탬프
   3) (integer) 15234  # 실행 시간 (마이크로초)
   4) 1) "KEYS"  # 명령어
      2) "*"     # 인자
```

---

## 6. 보안 감사 및 로깅

### 6.1 보안 이벤트 로깅

#### redis.conf
```bash
# 로그 파일 경로
logfile /var/log/redis/redis-server.log

# 로그 레벨 (debug, verbose, notice, warning)
loglevel notice

# 보안 관련 이벤트 로깅
# - 인증 실패
# - ACL 위반
# - 의심스러운 명령어
```

### 6.2 인증 실패 모니터링

```bash
# 로그 파일에서 인증 실패 확인
tail -f /var/log/redis/redis-server.log | grep "AUTH"

# 예시 출력
[2024-01-15 10:32:15] * Failed authentication from 192.168.1.100
[2024-01-15 10:32:20] * Failed authentication from 192.168.1.100
[2024-01-15 10:32:25] * Failed authentication from 192.168.1.100
```

### 6.3 침입 탐지 스크립트

```bash
#!/bin/bash
# fail2ban-redis.sh

LOGFILE="/var/log/redis/redis-server.log"
THRESHOLD=5  # 5회 실패 시 차단
BAN_TIME=3600  # 1시간 차단

# 인증 실패 IP 추출
grep "Failed authentication" $LOGFILE | \
  awk '{print $NF}' | \
  sort | uniq -c | \
  while read count ip; do
    if [ $count -ge $THRESHOLD ]; then
      echo "차단: $ip (실패 횟수: $count)"
      iptables -A INPUT -s $ip -j DROP
    fi
  done
```

---

## 7. 프로덕션 보안 체크리스트

### ✅ 필수 보안 설정 (반드시 적용)

```bash
[ ] 1. requirepass 설정 (32자 이상 강력한 패스워드)
[ ] 2. bind 127.0.0.1 또는 VPC 내부 IP만 허용
[ ] 3. protected-mode yes
[ ] 4. 방화벽 규칙 설정 (특정 IP만 허용)
[ ] 5. 위험 명령어 비활성화 (FLUSHALL, KEYS, CONFIG)
[ ] 6. Redis를 root가 아닌 일반 유저로 실행
[ ] 7. Redis 포트 변경 (6379 → 다른 포트)
[ ] 8. 최신 Redis 버전 사용 (보안 패치 적용)
```

### ✅ 권장 보안 설정 (강력 추천)

```bash
[ ] 9. ACL 사용자 생성 및 권한 분리
[ ] 10. SSL/TLS 암호화 적용
[ ] 11. VPC/VPN 내부망 구성
[ ] 12. SLOWLOG 모니터링
[ ] 13. 보안 로그 수집 및 분석
[ ] 14. 백업 암호화
[ ] 15. 정기적인 패스워드 로테이션
[ ] 16. 침입 탐지 시스템 (IDS) 구축
```

### ✅ 고급 보안 설정 (엔터프라이즈)

```bash
[ ] 17. 2FA (Two-Factor Authentication)
[ ] 18. SIEM 통합 (Security Information and Event Management)
[ ] 19. 취약점 스캔 (Nessus, OpenVAS)
[ ] 20. 침투 테스트 (Penetration Testing)
[ ] 21. 데이터 암호화 (at-rest encryption)
[ ] 22. 보안 감사 로그 장기 보관
[ ] 23. GDPR/HIPAA 컴플라이언스 준수
[ ] 24. 정기 보안 교육
```

---

## 주니어 시나리오

### 시나리오 1: "프로덕션 배포 전날, 보안 체크"
```
상황: 내일 프로덕션 배포, 팀장님이 보안 확인 요청

팀장: "Redis 보안 설정 확인했어? 외부에서 접근 안 되지?"

당신: (당황) "어... 패스워드는 설정했는데..."

확인 필요 사항:
1. bind 설정 확인
   redis-cli CONFIG GET bind
   → "0.0.0.0" 나오면 위험!

2. requirepass 확인
   redis-cli CONFIG GET requirepass
   → "" 나오면 위험!

3. protected-mode 확인
   redis-cli CONFIG GET protected-mode
   → "no" 나오면 위험!

해결:
1. redis.conf 수정
2. Redis 재시작
3. 보안 체크리스트 전체 검토

결과: ✅ 보안 사고 예방, 안전한 배포
```

### 시나리오 2: "새벽 2시, 랜섬웨어 공격 감지"
```
상황: 모니터링 알림 - "Redis 데이터 전체 삭제 감지"

로그 확인:
[02:15:32] * Connection from 123.45.67.89
[02:15:33] * AUTH failed
[02:15:34] * AUTH failed
[02:15:35] * Connection accepted (패스워드 없음!)
[02:15:36] * Command: FLUSHALL
[02:15:37] * All data deleted

원인 분석:
1. requirepass 미설정
2. bind 0.0.0.0 (외부 접근 허용)
3. FLUSHALL 명령어 차단 안 됨

긴급 조치:
1. Redis 재시작
2. 백업에서 데이터 복구
3. 보안 설정 즉시 적용

예방 방법:
✅ requirepass 설정
✅ bind 127.0.0.1
✅ rename-command FLUSHALL ""

피해: 2시간 다운타임
교훈: 보안 설정은 선택이 아닌 필수!
```

### 시나리오 3: "GDPR 감사, 암호화 증명 요구"
```
상황: EU 고객 데이터 처리, GDPR 감사 진행 중

감사관: "Redis에 저장된 개인정보는 암호화되어 있나요?"

당신: "음... 아직 안 했는데요?"

감사 결과:
❌ 전송 중 암호화 없음 (SSL/TLS)
❌ 저장 시 암호화 없음
❌ 접근 로그 없음

벌금: €2,000,000

해결:
1. SSL/TLS 즉시 적용
2. 애플리케이션 레벨 암호화 추가
3. ACL로 접근 로그 수집
4. 보안 감사 로그 보관

결과: ✅ GDPR 준수, 벌금 회피
```

---

## FAQ

**Q1: requirepass만 설정하면 안전한가요?**
```
A: ❌ 아닙니다!
requirepass만으로는 부족합니다.

필수 조합:
1. requirepass (인증)
2. bind 127.0.0.1 (네트워크 접근 제어)
3. 방화벽 (추가 방어)
4. 위험 명령어 차단

다층 방어가 핵심입니다.
```

**Q2: 패스워드를 코드에 하드코딩해도 되나요?**
```
A: ❌ 절대 안 됩니다!

위험:
- GitHub에 업로드 시 노출
- 코드 유출 시 패스워드 노출

올바른 방법:
1. 환경 변수 사용
   export REDIS_PASSWORD="..."

2. AWS Secrets Manager
3. HashiCorp Vault
4. Kubernetes Secrets
```

**Q3: SSL/TLS 적용 시 성능 저하는 얼마나 되나요?**
```
A: 약 10-20% 성능 저하

성능 저하: 10-20%
보안 향상: 100%

권장: 성능보다 보안이 중요한 경우 필수 적용
(개인정보, 금융 데이터 등)
```

**Q4: KEYS * 명령을 꼭 차단해야 하나요?**
```
A: ✅ 네, 반드시 차단하세요!

이유:
1. KEYS *는 전체 키스페이스를 블로킹
2. 수백만 개 키가 있으면 서버 먹통
3. 프로덕션에서 절대 사용 금지

대안: SCAN 명령 사용
```

**Q5: Redis를 인터넷에 노출해도 되나요?**
```
A: ❌ 절대 안 됩니다!

이유:
1. Shodan 등으로 쉽게 발견됨
2. 자동화된 공격 대상
3. 랜섬웨어 공격 위험

올바른 방법:
- VPC 내부망에만 배치
- VPN을 통해서만 접근
- 절대 공인 IP 노출 금지
```

---

## 면접 질문 리스트

### 초급
1. Redis 보안에서 가장 중요한 3가지 설정은?
2. requirepass의 역할은?
3. bind 0.0.0.0과 bind 127.0.0.1의 차이는?

### 중급
4. ACL의 동작 원리를 설명하세요
5. SSL/TLS 적용 방법과 성능 영향은?
6. FLUSHALL 명령어를 차단하는 방법은?

### 고급
7. 다층 보안 방어 전략을 설계하세요
8. GDPR 준수를 위한 Redis 보안 설정은?
9. 랜섬웨어 공격을 예방하는 방법은?

---

## 핵심 정리

### 필수 보안 3종 세트
```
1. ✅ requirepass (강력한 패스워드)
2. ✅ bind 127.0.0.1 (외부 접근 차단)
3. ✅ rename-command FLUSHALL "" (위험 명령 차단)
```

### 보안 계층
```
1층: 네트워크 (bind, 방화벽, VPC)
2층: 인증 (requirepass)
3층: 권한 (ACL)
4층: 암호화 (SSL/TLS)
5층: 명령어 제한 (rename-command)
6층: 모니터링 (로그, 알림)
```

### 보안 사고 예방
```
✅ 프로덕션 배포 전 보안 체크리스트 확인
✅ 정기적인 보안 감사
✅ 최신 보안 패치 적용
✅ 침입 탐지 시스템 구축
```

---

## 다음 단계

- **15장**: Sentinel 고가용성 가이드
- **16장**: 캐싱 전략 완전 가이드

---

## 축하합니다! 🎉

**이제 여러분은 프로덕션 환경에서 Redis를 안전하게 운영할 수 있습니다!**

**보안은 선택이 아닌 필수입니다. 반드시 적용하세요!** 🔒
