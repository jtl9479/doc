# Redis 클러스터 및 분산 시스템 완전 가이드

> **학습 목표**: Redis 클러스터를 설계하고 구축하여 대규모 분산 시스템을 운영할 수 있습니다.

**예상 학습 시간**: 8-10시간
**난이도**: ⭐⭐⭐⭐☆ (4/5)

---

## 📚 목차
1. [왜 이 기술이 필요한가](#-왜-이-기술이-필요한가)
2. [실생활 비유로 이해하기](#-실생활-비유로-이해하기)
3. [Redis 클러스터 개념](#1-redis-클러스터-개념)
4. [클러스터 구성 및 설정](#2-클러스터-구성-및-설정)
5. [샤딩 및 데이터 분산](#3-샤딩-및-데이터-분산)
6. [고가용성 및 장애 복구](#4-고가용성-및-장애-복구)
7. [실전 프로젝트: 대규모 서비스 아키텍처](#5-실전-프로젝트-대규모-서비스-아키텍처)
8. [성능 모니터링 및 최적화](#6-성능-모니터링-및-최적화)
9. [운영 및 유지보수](#7-운영-및-유지보수)
10. [주니어 시나리오](#-주니어-시나리오)
11. [면접 질문 리스트](#-면접-질문-리스트)
12. [FAQ](#-faq)
13. [핵심 정리](#-핵심-정리)
14. [다음 단계](#-다음-단계)
15. [추가 학습 자료](#-추가-학습-자료)

---

## 🤔 왜 이 기술이 필요한가?

### 실무 배경

**대규모 서비스에서 단일 Redis의 한계**

당신은 월간 활성 사용자(MAU) 1,000만 명의 전자상거래 플랫폼을 운영하고 있습니다. 초기에는 단일 Redis 인스턴스(64GB RAM)로 세션 저장, 장바구니, 실시간 재고를 관리했습니다. 하지만 성장하면서 심각한 문제에 직면했습니다.

#### ❌ 이 기술을 모르면 발생하는 문제

```
문제 1: 메모리 한계에 도달
- 증상: 64GB RAM 서버가 가득 차서 새 데이터 저장 불가
- 영향: 신규 사용자 세션 생성 실패, 서비스 가입 차단
- 비용: Scale-up으로 512GB RAM 서버 → 월 $5,000 추가 비용
- 근본 원인: 단일 서버의 물리적 메모리 한계

문제 2: 처리량(Throughput) 병목
- 증상: 블랙프라이데이 세일 시 100K QPS 이상 요청, Redis CPU 100%
- 영향: 응답 시간 10배 증가 (1ms → 10ms), 타임아웃 급증
- 비용: 고객 이탈률 30% 증가, 매출 손실 약 $100,000/일
- 근본 원인: Redis는 single-threaded, 하나의 CPU 코어만 사용

문제 3: 단일 장애점(SPOF - Single Point of Failure)
- 증상: 하드웨어 장애로 Redis 서버 다운 → 전체 서비스 중단
- 영향: 30분 다운타임 동안 모든 사용자 로그인 불가, 장바구니 사용 불가
- 비용: 평균 분당 $10,000 손실 × 30분 = $300,000 손실
- 근본 원인: 백업이 있어도 수동 전환에 시간 소요

문제 4: 지리적 지연시간
- 증상: 서울 데이터센터의 Redis를 미국 사용자가 접근 시 200ms 지연
- 영향: 페이지 로딩 속도 저하, 사용자 경험 악화
- 비용: 전환율(Conversion Rate) 5% 감소 → 월 $50,000 매출 손실
- 근본 원인: 단일 지역에만 데이터 존재
```

#### ✅ 이 기술을 사용하면

```
해결책 1: 수평적 확장(Horizontal Scaling)
- 방법: 6개 노드 클러스터 (각 64GB) → 총 384GB 사용 가능
- 효과: 메모리 용량 6배 증가, 향후 노드 추가로 무한 확장 가능
- 절감: Scale-up 대비 70% 비용 절감 ($5,000 → $1,500/월)

해결책 2: 처리량 분산
- 방법: 6개 마스터 노드가 요청 분산 처리
- 효과: 총 처리량 600K QPS 달성 (100K × 6), 응답 시간 1ms 유지
- 절감: 블랙프라이데이 안정적 운영, 매출 손실 0

해결책 3: 자동 장애 복구(Auto-Failover)
- 방법: 각 마스터마다 슬레이브 배치, 장애 시 자동 승격
- 효과: 평균 복구 시간(MTTR) 30분 → 5초, 99.99% 가용성
- 절감: 연간 다운타임 손실 $1,200,000 → $12,000 (99% 절감)

해결책 4: 지리적 분산
- 방법: 서울, 싱가포르, 버지니아 데이터센터에 노드 배치
- 효과: 전 세계 사용자에게 평균 지연시간 50ms 이하
- 절감: 전환율 회복으로 월 $50,000 매출 증가
```

### 📊 수치로 보는 효과

| 지표 | Before (단일 인스턴스) | After (Redis Cluster) | 개선율 |
|------|----------------------|----------------------|--------|
| 최대 메모리 | 64GB | 384GB (6노드) | **500%↑** |
| 처리량 (QPS) | 100K | 600K | **500%↑** |
| 가용성 | 99.9% (연 8.7시간 다운) | 99.99% (연 52분 다운) | **10배↑** |
| 장애 복구 시간 | 수동 30분+ | 자동 5초 | **99%↓** |
| 평균 응답 시간 | 2-5ms | 1-3ms | **40%↓** |
| Scale-up 비용 | $5,000/월 | Scale-out $1,500/월 | **70%↓** |
| 다운타임 손실 | $1.2M/년 | $12K/년 | **99%↓** |
| 지리적 지연 | 200ms (해외) | 50ms (글로벌) | **75%↓** |

### 실제 기업 사례

#### 사례 1: 쿠팡 (대규모 전자상거래)
```
문제: 일 주문 200만 건, 동시 접속 50만 명 → 단일 Redis 한계
해결: 30노드 Redis Cluster로 확장
- 실시간 재고: 1억 개 상품 정보 관리
- 장바구니: 동시 100만 장바구니 처리
- 세션: 50만 동시 접속 세션 저장
성과: 블랙프라이데이 매출 300% 증가 시에도 안정적 운영
```

#### 사례 2: 카카오톡 (메시징 플랫폼)
```
문제: 월 5,000만 활성 사용자, 일 메시지 수십억 건
해결: 지리적 분산 Redis Cluster
- 온라인 상태: 실시간 사용자 상태 동기화
- 읽지 않은 메시지 카운트: 초당 100만 업데이트
- 채팅방 메타데이터: 1억 개 채팅방 정보
성과: 99.99% 가용성 달성, 평균 응답 시간 2ms 이하
```

#### 사례 3: 배달의민족 (O2O 플랫폼)
```
문제: 점심/저녁 피크 시간 주문 폭주, 실시간 배달 추적
해결: 해시 태그 기반 클러스터 설계
- 주문 상태: order:{restaurant-id}:* 로 그룹화
- 배달 위치: delivery:{order-id}:* 로 트랜잭션 처리
- 실시간 알림: Pub/Sub 클러스터 전체 브로드캐스트
성과: 점심 피크 시간(12-13시) 주문 처리 능력 10배 향상
```

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 은행 지점 네트워크
```
Redis 클러스터 = 전국 은행 지점 네트워크

단일 Redis 인스턴스:
- 서울 본점 하나만 운영
- 모든 고객이 본점 방문 필요
- 본점 문제 시 전체 서비스 중단
- 처리 용량 제한적

Redis 클러스터:
- 서울, 부산, 대구 등 여러 지점 운영
- 고객은 가까운 지점 이용 (샤딩)
- 한 지점 문제 시 다른 지점 이용 가능 (고가용성)
- 각 지점에 백업 직원 배치 (복제본)
- 전국 통합 시스템으로 연결

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  서울 지점   │←───→│  부산 지점   │←───→│  대구 지점   │
│  (마스터)   │     │  (마스터)   │     │  (마스터)   │
│   슬롯 0-   │     │  슬롯 5461- │     │ 슬롯 10923- │
│   5460     │     │   10922    │     │   16383    │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
   [백업 직원]          [백업 직원]          [백업 직원]
   (슬레이브)          (슬레이브)          (슬레이브)
```

### 비유 2: 택배 물류 센터
```
해시 슬롯 = 우편번호 체계

16384개 해시 슬롯 = 전국 우편번호
각 마스터 노드 = 권역별 물류센터

우편번호 00000-05460 → 서울 센터 (마스터1)
우편번호 05461-10922 → 부산 센터 (마스터2)
우편번호 10923-16383 → 대구 센터 (마스터3)

택배 배송 과정:
1. 물건 주소 확인 (키 해싱)
2. 우편번호로 센터 결정 (슬롯 계산)
3. 해당 센터로 자동 라우팅
4. 센터 장애 시 백업 센터 활용
```

### 비유 3: 대형 쇼핑몰 체인점
```
클러스터 확장 = 매장 추가 오픈

초기: 3개 매장 (강남, 홍대, 잠실)
- 각 매장: 상품 카테고리 분담
- 강남: 의류, 신발 (슬롯 0-5460)
- 홍대: 전자제품 (슬롯 5461-10922)
- 잠실: 식품, 생활용품 (슬롯 10923-16383)

확장: 4번째 매장 추가 (분당)
- 기존 매장에서 일부 카테고리 이전 (리샤딩)
- 강남 → 의류 일부를 분당으로
- 홍대 → 전자제품 일부를 분당으로
- 잠실 → 식품 일부를 분당으로
- 결과: 부하 분산, 고객 대기시간 감소

각 매장마다 백업 직원 배치:
- 정직원 퇴근 시 백업 직원이 대체 (페일오버)
- 영업 중단 없이 24시간 운영
```

### 비유 4: 도서관 분관 시스템
```
Redis Sentinel vs Cluster = 도서관 운영 방식

Simple Replication (단일 도서관 + 백업본):
- 중앙 도서관 1개 + 백업 서고
- 모든 대출/반납은 중앙 도서관에서만
- 중앙 도서관 휴관 시 수동 전환 필요

Redis Sentinel (관리자 감독 체계):
- 중앙 도서관 + 백업 도서관
- 감독관(Sentinel) 3명이 중앙 도서관 상태 체크
- 중앙 도서관 문제 시 자동으로 백업을 중앙으로 승격
- 하지만 여전히 하나의 중앙 도서관만 운영

Redis Cluster (분관 네트워크):
- 여러 분관 동시 운영
- 도서 분류 번호(해시 슬롯)로 자동 분배
- 000-299번: 강남 분관
- 300-599번: 서초 분관
- 600-999번: 송파 분관
- 각 분관마다 백업 서고 있음
- 한 분관 휴관해도 다른 분관 정상 운영
```

### 비유 5: 게임 서버 샤딩
```
해시 태그 = 같은 파티원 같은 서버 배치

일반 샤딩:
user:1001 → 서버 A
user:1002 → 서버 B
user:1003 → 서버 C
→ 파티 구성 불가 (서로 다른 서버)

해시 태그 활용:
user:{party-100}:1001 → 서버 A
user:{party-100}:1002 → 서버 A
user:{party-100}:1003 → 서버 A
→ 같은 서버에 배치되어 파티 플레이 가능

실전 예시:
┌─────────────────────────┐
│     게임 서버 A         │
│  user:{raid-7}:player1  │
│  user:{raid-7}:player2  │
│  user:{raid-7}:player3  │
│  → 레이드 파티 전체     │
└─────────────────────────┘

┌─────────────────────────┐
│     게임 서버 B         │
│  user:{raid-8}:player1  │
│  user:{raid-8}:player2  │
│  → 다른 레이드 파티     │
└─────────────────────────┘
```

### 📊 수치로 보는 효과

| 지표 | 단일 인스턴스 | Redis Cluster | 개선율 |
|------|--------------|---------------|--------|
| 최대 메모리 | 64GB | 384GB (6노드) | **500%↑** |
| 처리량 (QPS) | 100K | 600K | **500%↑** |
| 가용성 | 99.9% | 99.99% | **10배↑** |
| 장애 복구 시간 | 수동 (30분+) | 자동 (수초) | **99%↓** |
| 응답 시간 | 2-5ms | 1-3ms | **40%↓** |
| 확장 비용 | Scale-up ($$$) | Scale-out ($$) | **50%↓** |

---

---

## 1. Redis 클러스터 개념

### 1.1 클러스터링이 필요한 이유

#### 1.1.1 단일 인스턴스의 한계

```bash
# 메모리 한계
# - 단일 Redis 인스턴스는 물리적 메모리에 제한됨
# - 64GB RAM 서버 → 최대 ~50GB 데이터 저장 가능

# 처리량 한계
# - CPU 단일 코어 사용 (Redis는 single-threaded)
# - 네트워크 대역폭 제한

# 가용성 문제
# - Single Point of Failure (SPOF)
# - 하드웨어 장애 시 전체 서비스 중단
```

#### 1.1.2 클러스터링의 장점

```bash
# 1. 수평적 확장 (Horizontal Scaling)
# - 더 많은 서버 추가로 용량 확장
# - 메모리: 6개 노드 × 64GB = 384GB 가능

# 2. 고가용성 (High Availability)
# - 일부 노드 장애 시에도 서비스 계속
# - 자동 장애 조치 (Auto-failover)

# 3. 부하 분산
# - 읽기/쓰기 요청을 여러 노드에 분산
# - 네트워크 트래픽 분산

# 4. 지리적 분산
# - 여러 데이터센터에 노드 배치
# - 지연시간 최적화
```

### 1.2 Redis Cluster vs Sentinel vs Replication

#### 1.2.1 Redis Cluster

```bash
# 특징
- 자동 샤딩 (16384 hash slots)
- 내장 고가용성
- 수평적 확장
- 마스터-슬레이브 구조

# 최소 구성
- 3개 마스터 노드 (홀수 개)
- 각 마스터당 1개 이상의 슬레이브

# 사용 사례
- 대용량 데이터 (수백 GB 이상)
- 높은 처리량 요구
- 자동 샤딩 필요
```

#### 1.2.2 Redis Sentinel

```bash
# 특징
- 고가용성 모니터링
- 자동 장애 조치
- 설정 제공자 역할
- 알림 시스템

# 구성
- 홀수 개의 Sentinel 인스턴스 (최소 3개)
- 마스터-슬레이브 Redis 인스턴스들

# 사용 사례
- 단순한 마스터-슬레이브 고가용성
- 적은 수의 Redis 인스턴스
- 복잡한 샤딩 불필요
```

#### 1.2.3 Simple Replication

```bash
# 특징
- 마스터 1개, 슬레이브 N개
- 읽기 전용 슬레이브
- 수동 장애 조치

# 구성
- 1개 마스터 (읽기/쓰기)
- N개 슬레이브 (읽기 전용)

# 사용 사례
- 읽기 위주 워크로드
- 간단한 구성
- 수동 관리 가능
```

---

## 2. 클러스터 구성 및 설정

### 2.1 기본 클러스터 설정

#### 2.1.1 노드 설정 파일

```bash
# redis-7000.conf (첫 번째 노드)
port 7000
cluster-enabled yes
cluster-config-file nodes-7000.conf
cluster-node-timeout 15000
appendonly yes
appendfilename "appendonly-7000.aof"
dir /var/lib/redis/7000

# 메모리 설정
maxmemory 4gb
maxmemory-policy allkeys-lru

# 네트워크 설정
bind 127.0.0.1 192.168.1.100
protected-mode no

# 로깅
logfile /var/log/redis/redis-7000.log
loglevel notice

# 보안 (선택사항)
requirepass your-strong-password
masterauth your-strong-password
```

#### 2.1.2 6노드 클러스터 설정

```bash
#!/bin/bash
# setup-cluster.sh

# 디렉토리 생성
for port in 7000 7001 7002 7003 7004 7005; do
    mkdir -p /var/lib/redis/$port
    mkdir -p /var/log/redis
done

# 설정 파일 생성
for port in 7000 7001 7002 7003 7004 7005; do
    cat > /etc/redis/redis-$port.conf << EOF
port $port
cluster-enabled yes
cluster-config-file nodes-$port.conf
cluster-node-timeout 15000
appendonly yes
appendfilename "appendonly-$port.aof"
dir /var/lib/redis/$port
logfile /var/log/redis/redis-$port.log
loglevel notice
maxmemory 4gb
maxmemory-policy allkeys-lru
bind 127.0.0.1 $(hostname -I | awk '{print $1}')
EOF
done

# 시스템 서비스 파일 생성
for port in 7000 7001 7002 7003 7004 7005; do
    cat > /etc/systemd/system/redis-$port.service << EOF
[Unit]
Description=Redis In-Memory Data Store (port $port)
After=network.target

[Service]
User=redis
Group=redis
ExecStart=/usr/bin/redis-server /etc/redis/redis-$port.conf
ExecStop=/usr/bin/redis-cli -p $port shutdown
Restart=always

[Install]
WantedBy=multi-user.target
EOF
done

# 서비스 시작
systemctl daemon-reload
for port in 7000 7001 7002 7003 7004 7005; do
    systemctl enable redis-$port
    systemctl start redis-$port
done

echo "모든 Redis 노드가 시작되었습니다."
```

#### 2.1.3 클러스터 초기화

```bash
# 클러스터 생성 (Redis 5.0+ 방식)
redis-cli --cluster create \
  127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \
  127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \
  --cluster-replicas 1

# 출력 예시:
# >>> Performing hash slots allocation on 6 nodes...
# Master[0] -> Slots 0-5460
# Master[1] -> Slots 5461-10922
# Master[2] -> Slots 10923-16383
# Adding replica 127.0.0.1:7004 to 127.0.0.1:7000
# Adding replica 127.0.0.1:7005 to 127.0.0.1:7001
# Adding replica 127.0.0.1:7003 to 127.0.0.1:7002

# 클러스터 상태 확인
redis-cli -c -p 7000 cluster nodes

# 클러스터 정보 확인
redis-cli -c -p 7000 cluster info
```

### 2.2 고급 클러스터 설정

#### 2.2.1 지리적 분산 클러스터

```bash
# 3개 데이터센터에 걸친 클러스터 설정

# DC1 (서울) - 마스터들
# 192.168.1.100:7000 (마스터)
# 192.168.1.101:7001 (마스터)

# DC2 (부산) - 마스터 + 복제본
# 192.168.2.100:7002 (마스터)
# 192.168.2.101:7003 (DC1-7000의 복제본)

# DC3 (대전) - 복제본들
# 192.168.3.100:7004 (DC1-7001의 복제본)
# 192.168.3.101:7005 (DC2-7002의 복제본)

# 지리적 분산 클러스터 생성
redis-cli --cluster create \
  192.168.1.100:7000 192.168.1.101:7001 192.168.2.100:7002 \
  192.168.2.101:7003 192.168.3.100:7004 192.168.3.101:7005 \
  --cluster-replicas 1

# 각 노드의 우선순위 설정 (DC 내 복제본 우선)
redis-cli -h 192.168.1.100 -p 7000 CONFIG SET cluster-replica-validity-factor 10
redis-cli -h 192.168.2.101 -p 7003 CONFIG SET cluster-replica-validity-factor 5
```

#### 2.2.2 보안 강화 클러스터

```bash
# 보안 설정이 포함된 클러스터 구성

# redis-secure.conf
port 7000
cluster-enabled yes
cluster-config-file nodes-7000.conf
cluster-node-timeout 15000

# 인증 설정
requirepass "your-very-strong-cluster-password"
masterauth "your-very-strong-cluster-password"

# 네트워크 보안
bind 10.0.1.100  # 내부 네트워크만
protected-mode yes

# TLS 설정 (Redis 6.0+)
tls-port 17000
port 0  # 비암호화 포트 비활성화
tls-cert-file /etc/redis/tls/redis.crt
tls-key-file /etc/redis/tls/redis.key
tls-ca-cert-file /etc/redis/tls/ca.crt
tls-cluster yes

# 명령어 제한
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command DEBUG ""
rename-command CONFIG "CONFIG_b840fc02d524045429941cc15f59e41cb7be6c52"

# 로깅 및 감사
logfile /var/log/redis/redis-7000.log
syslog-enabled yes
syslog-ident redis-cluster-7000
```

---

## 3. 샤딩 및 데이터 분산

### 3.1 해시 슬롯 시스템

#### 3.1.1 해시 슬롯 개념

```bash
# Redis Cluster는 16384개의 해시 슬롯 사용
# 각 키는 CRC16(key) % 16384로 슬롯 계산

# 예시: 키 분산
# "user:1001" -> CRC16("user:1001") % 16384 = 9189
# "user:1002" -> CRC16("user:1002") % 16384 = 5649
# "order:5001" -> CRC16("order:5001") % 16384 = 12678

# 슬롯 분배 예시 (3마스터)
# 마스터1: 슬롯 0-5460     (5461개)
# 마스터2: 슬롯 5461-10922 (5462개)
# 마스터3: 슬롯 10923-16383 (5461개)
```

#### 3.1.2 키 분산 전략

```lua
-- key_distribution_analyzer.lua
local total_slots = 16384
local masters = 3
local sample_keys = {}

-- 다양한 키 패턴 생성
local key_patterns = {
    "user:%d",
    "order:%d",
    "product:%d",
    "session:%s",
    "cache:%s",
    "temp:%d"
}

local distribution = {}
for i = 0, masters - 1 do
    distribution[i] = 0
end

-- 10000개 샘플 키로 분산 테스트
for i = 1, 10000 do
    local pattern = key_patterns[math.random(#key_patterns)]
    local key

    if string.find(pattern, "%%d") then
        key = string.format(pattern, i)
    else
        key = string.format(pattern, "sample" .. i)
    end

    -- CRC16 계산 (간단한 구현)
    local crc = 0
    for j = 1, string.len(key) do
        crc = (crc + string.byte(key, j)) % 65536
    end
    local slot = crc % total_slots

    -- 마스터 노드 결정
    local master
    if slot <= 5460 then
        master = 0
    elseif slot <= 10922 then
        master = 1
    else
        master = 2
    end

    distribution[master] = distribution[master] + 1
end

-- 분산 결과 반환
local result = {}
for i = 0, masters - 1 do
    table.insert(result, {
        master = i,
        key_count = distribution[i],
        percentage = (distribution[i] / 10000) * 100
    })
end

return result
```

### 3.2 해시 태그를 이용한 키 그룹화

#### 3.2.1 해시 태그 기본 개념

```bash
# 해시 태그: {tag} 형식으로 키의 일부를 지정하여 같은 슬롯에 배치

# 같은 슬롯에 배치되는 키들
"user:{1001}:profile"  # 슬롯: CRC16("1001") % 16384
"user:{1001}:settings" # 같은 슬롯
"user:{1001}:orders"   # 같은 슬롯

# 다른 슬롯에 배치되는 키들
"user:1001:profile"    # 슬롯: CRC16("user:1001:profile") % 16384
"user:1001:settings"   # 슬롯: CRC16("user:1001:settings") % 16384
```

#### 3.2.2 실전 해시 태그 활용

```bash
# 사용자 관련 데이터 그룹화
redis-cli -c -p 7000 HMSET "user:{1001}:profile" name "김철수" age 30 email "kim@example.com"
redis-cli -c -p 7000 SADD "user:{1001}:friends" 1002 1003 1004
redis-cli -c -p 7000 ZADD "user:{1001}:scores" 100 "game1" 200 "game2"

# 같은 노드에 있으므로 트랜잭션 가능
redis-cli -c -p 7000 MULTI
redis-cli -c -p 7000 HGET "user:{1001}:profile" name
redis-cli -c -p 7000 SCARD "user:{1001}:friends"
redis-cli -c -p 7000 ZCARD "user:{1001}:scores"
redis-cli -c -p 7000 EXEC

# 주문 관련 데이터 그룹화
redis-cli -c -p 7000 HMSET "order:{20240315}:summary" total_orders 150 total_amount 1500000
redis-cli -c -p 7000 LPUSH "order:{20240315}:list" "order:1001" "order:1002" "order:1003"
redis-cli -c -p 7000 SADD "order:{20240315}:customers" 1001 1002 1003
```

### 3.3 동적 샤딩 및 리밸런싱

#### 3.3.1 노드 추가

```bash
# 새 노드 준비
redis-server --port 7006 --cluster-enabled yes --cluster-config-file nodes-7006.conf &
redis-server --port 7007 --cluster-enabled yes --cluster-config-file nodes-7007.conf &

# 클러스터에 노드 추가 (7006을 마스터로)
redis-cli --cluster add-node 127.0.0.1:7006 127.0.0.1:7000

# 슬롯 재분배 (기존 마스터들에서 슬롯 이동)
redis-cli --cluster reshard 127.0.0.1:7000
# How many slots do you want to move? 4096
# What is the receiving node ID? [7006의 node ID]
# Source nodes: all

# 슬레이브 노드 추가 (7007을 7006의 슬레이브로)
redis-cli --cluster add-node 127.0.0.1:7007 127.0.0.1:7000 --cluster-slave --cluster-master-id [7006의 node ID]

# 클러스터 상태 확인
redis-cli --cluster check 127.0.0.1:7000
```

#### 3.3.2 자동 리밸런싱 스크립트

```bash
#!/bin/bash
# auto-rebalance.sh

CLUSTER_HOST="127.0.0.1"
CLUSTER_PORT="7000"

# 현재 클러스터 상태 분석
analyze_cluster() {
    echo "=== 클러스터 분석 시작 ==="

    # 노드 정보 수집
    redis-cli -h $CLUSTER_HOST -p $CLUSTER_PORT cluster nodes | while read line; do
        node_id=$(echo $line | awk '{print $1}')
        address=$(echo $line | awk '{print $2}')
        flags=$(echo $line | awk '{print $3}')
        slots=$(echo $line | cut -d' ' -f9-)

        if [[ $flags == *"master"* ]]; then
            slot_count=$(echo $slots | tr ',' '\n' | wc -l)
            echo "마스터 $node_id ($address): $slot_count 슬롯"
        fi
    done
}

# 불균형 감지
detect_imbalance() {
    local max_diff=1000  # 최대 허용 슬롯 차이

    # 각 마스터의 슬롯 수 계산
    declare -A slot_counts
    redis-cli -h $CLUSTER_HOST -p $CLUSTER_PORT cluster nodes | while read line; do
        if [[ $line == *"master"* ]]; then
            node_id=$(echo $line | awk '{print $1}')
            slots=$(echo $line | cut -d' ' -f9-)
            slot_count=$(echo $slots | tr ',' '\n' | wc -l)
            slot_counts[$node_id]=$slot_count
        fi
    done

    # 최대/최소 슬롯 수 차이 계산
    local max_slots=0
    local min_slots=16384

    for count in "${slot_counts[@]}"; do
        if [ $count -gt $max_slots ]; then
            max_slots=$count
        fi
        if [ $count -lt $min_slots ]; then
            min_slots=$count
        fi
    done

    local diff=$((max_slots - min_slots))
    if [ $diff -gt $max_diff ]; then
        echo "불균형 감지: 최대 차이 $diff 슬롯"
        return 0
    else
        echo "클러스터 균형 상태 양호"
        return 1
    fi
}

# 자동 리밸런싱 실행
auto_rebalance() {
    echo "자동 리밸런싱 시작..."

    # Redis 내장 리밸런스 사용
    redis-cli --cluster rebalance $CLUSTER_HOST:$CLUSTER_PORT \
        --cluster-threshold 100 \
        --cluster-use-empty-masters

    if [ $? -eq 0 ]; then
        echo "리밸런싱 완료"
    else
        echo "리밸런싱 실패"
        return 1
    fi
}

# 메인 실행
main() {
    analyze_cluster

    if detect_imbalance; then
        echo "리밸런싱이 필요합니다."
        read -p "자동 리밸런싱을 실행하시겠습니까? (y/N): " confirm

        if [[ $confirm =~ ^[Yy]$ ]]; then
            auto_rebalance
            echo "리밸런싱 후 상태:"
            analyze_cluster
        fi
    fi
}

main "$@"
```

---

## 4. 고가용성 및 장애 복구

### 4.1 장애 감지 및 자동 복구

#### 4.1.1 클러스터 장애 감지 메커니즘

```bash
# 노드 상태 모니터링
# - PING/PONG 메시지 (cluster-node-timeout 내)
# - 과반수 노드가 PFAIL로 판단시 FAIL 상태로 변경
# - 자동 장애조치 시작

# 장애 감지 설정
cluster-node-timeout 15000           # 15초 타임아웃
cluster-slave-validity-factor 10     # 슬레이브 유효성 계수
cluster-migration-barrier 1         # 최소 슬레이브 개수
cluster-require-full-coverage yes   # 모든 슬롯 커버 필요
```

#### 4.1.2 장애 복구 시나리오

```bash
# 시나리오 1: 마스터 노드 장애
# 1. 7000번 마스터 노드 다운
sudo systemctl stop redis-7000

# 2. 클러스터 상태 확인
redis-cli -c -p 7001 cluster nodes
# 출력: 7000 노드가 fail 상태, 7003 슬레이브가 마스터로 승격

# 3. 자동 장애조치 로그 확인
tail -f /var/log/redis/redis-7003.log
# "Cluster state changed: ok"
# "I'm now the master for hash slots [0-5460]"

# 4. 장애 노드 복구
sudo systemctl start redis-7000
# 복구된 노드는 자동으로 슬레이브가 됨

# 시나리오 2: 네트워크 분할 (Split-brain 방지)
# 클러스터가 과반수 노드와 통신 불가시 읽기 전용 모드로 전환
redis-cli -c -p 7000 set test_key test_value
# (error) CLUSTERDOWN The cluster is down
```

#### 4.1.3 수동 장애조치

```bash
# 계획된 유지보수를 위한 수동 장애조치

# 1. 마스터 7000의 슬레이브 7003에서 실행
redis-cli -h 127.0.0.1 -p 7003 cluster failover

# 2. 강제 장애조치 (긴급상황)
redis-cli -h 127.0.0.1 -p 7003 cluster failover force

# 3. 수동 슬롯 이전
redis-cli --cluster reshard 127.0.0.1:7001 \
    --cluster-from [source-node-id] \
    --cluster-to [target-node-id] \
    --cluster-slots 1000
```

### 4.2 백업 및 복구 전략

#### 4.2.1 클러스터 백업 스크립트

```bash
#!/bin/bash
# cluster_backup.sh

BACKUP_DIR="/var/backups/redis-cluster"
DATE=$(date +%Y%m%d_%H%M%S)
CLUSTER_BACKUP_DIR="$BACKUP_DIR/cluster_backup_$DATE"

# 백업 디렉토리 생성
mkdir -p "$CLUSTER_BACKUP_DIR"

# 클러스터 노드 정보 수집
NODES=$(redis-cli -h 127.0.0.1 -p 7000 cluster nodes | grep master | awk '{print $2}')

echo "=== Redis 클러스터 백업 시작 ==="
echo "백업 디렉토리: $CLUSTER_BACKUP_DIR"

# 각 마스터 노드 백업
for node in $NODES; do
    host=$(echo $node | cut -d: -f1)
    port=$(echo $node | cut -d: -f2)

    echo "백업 중: $host:$port"

    # 백그라운드 저장 실행
    redis-cli -h $host -p $port BGSAVE

    # 백그라운드 저장 완료 대기
    while [ $(redis-cli -h $host -p $port LASTSAVE) -eq $(redis-cli -h $host -p $port LASTSAVE) ]; do
        sleep 1
    done

    # 백업 파일 복사
    DATA_DIR=$(redis-cli -h $host -p $port CONFIG GET dir | tail -1)
    DB_FILE=$(redis-cli -h $host -p $port CONFIG GET dbfilename | tail -1)

    cp "$DATA_DIR/$DB_FILE" "$CLUSTER_BACKUP_DIR/dump_${host}_${port}.rdb"

    # 설정 파일 백업
    cp "/etc/redis/redis-$port.conf" "$CLUSTER_BACKUP_DIR/"

    echo "완료: $host:$port"
done

# 클러스터 토폴로지 정보 저장
redis-cli -h 127.0.0.1 -p 7000 cluster nodes > "$CLUSTER_BACKUP_DIR/cluster_topology.txt"
redis-cli -h 127.0.0.1 -p 7000 cluster info > "$CLUSTER_BACKUP_DIR/cluster_info.txt"

# 백업 압축
cd "$BACKUP_DIR"
tar -czf "cluster_backup_$DATE.tar.gz" "cluster_backup_$DATE"
rm -rf "cluster_backup_$DATE"

echo "=== 백업 완료: cluster_backup_$DATE.tar.gz ==="
```

#### 4.2.2 클러스터 복구 스크립트

```bash
#!/bin/bash
# cluster_restore.sh

BACKUP_FILE=$1
RESTORE_DIR="/tmp/redis_restore_$(date +%Y%m%d_%H%M%S)"

if [ -z "$BACKUP_FILE" ]; then
    echo "사용법: $0 <백업파일.tar.gz>"
    exit 1
fi

echo "=== Redis 클러스터 복구 시작 ==="

# 백업 파일 압축 해제
mkdir -p "$RESTORE_DIR"
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR"

BACKUP_CONTENT_DIR=$(ls -d "$RESTORE_DIR"/cluster_backup_*)

# 클러스터 토폴로지 확인
echo "백업된 클러스터 토폴로지:"
cat "$BACKUP_CONTENT_DIR/cluster_topology.txt"

echo
read -p "이 토폴로지로 복구하시겠습니까? (y/N): " confirm

if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "복구 취소됨"
    exit 0
fi

# 기존 클러스터 중지
echo "기존 클러스터 중지 중..."
for port in 7000 7001 7002 7003 7004 7005; do
    sudo systemctl stop redis-$port 2>/dev/null || true
    # 클러스터 상태 파일 제거
    rm -f "/var/lib/redis/$port/nodes-$port.conf"
done

# 데이터 복구
echo "데이터 복구 중..."
for dump_file in "$BACKUP_CONTENT_DIR"/dump_*.rdb; do
    if [ -f "$dump_file" ]; then
        # 파일명에서 호스트와 포트 추출
        filename=$(basename "$dump_file")
        host_port=$(echo "$filename" | sed 's/dump_\(.*\)\.rdb/\1/' | sed 's/_/:/')
        port=$(echo "$host_port" | cut -d: -f2)

        echo "복구 중: 포트 $port"

        # RDB 파일 복사
        cp "$dump_file" "/var/lib/redis/$port/dump.rdb"
        chown redis:redis "/var/lib/redis/$port/dump.rdb"

        # 설정 파일 복구
        if [ -f "$BACKUP_CONTENT_DIR/redis-$port.conf" ]; then
            cp "$BACKUP_CONTENT_DIR/redis-$port.conf" "/etc/redis/"
        fi
    fi
done

# Redis 인스턴스 재시작
echo "Redis 인스턴스 재시작 중..."
for port in 7000 7001 7002 7003 7004 7005; do
    sudo systemctl start redis-$port
    sleep 2
done

# 클러스터 재구성 (필요한 경우)
echo "클러스터 상태 확인 중..."
sleep 5

cluster_status=$(redis-cli -h 127.0.0.1 -p 7000 cluster info | grep cluster_state)
if [[ $cluster_status == *"fail"* ]]; then
    echo "클러스터 재구성이 필요합니다."

    # 클러스터 노드 재연결
    # 백업된 토폴로지를 기반으로 수동 연결
    echo "클러스터 수동 복구를 진행하세요:"
    echo "redis-cli --cluster fix 127.0.0.1:7000"
fi

echo "=== 복구 완료 ==="
echo "클러스터 상태 확인: redis-cli -c -p 7000 cluster info"

# 임시 파일 정리
rm -rf "$RESTORE_DIR"
```

---

## 5. 실전 프로젝트: 대규모 서비스 아키텍처

### 5.1 전자상거래 플랫폼 아키텍처

#### 5.1.1 아키텍처 설계

```yaml
# 서비스 구성도
# ┌─────────────────────────────────────────────────────────┐
# │                    Load Balancer                        │
# └─────────────────────┬───────────────────────────────────┘
#                       │
# ┌─────────────────────┼───────────────────────────────────┐
# │                Web Servers                              │
# │   App1    App2    App3    App4    App5    App6         │
# └─────────────────────┼───────────────────────────────────┘
#                       │
# ┌─────────────────────┼───────────────────────────────────┐
# │               Redis Cluster                             │
# │                                                         │
# │  ┌─────────┐  ┌─────────┐  ┌─────────┐                 │
# │  │ Master1 │  │ Master2 │  │ Master3 │                 │
# │  │ (7000)  │  │ (7001)  │  │ (7002)  │                 │
# │  │ User    │  │Product  │  │ Order   │                 │
# │  │ Data    │  │Catalog  │  │ & Cart  │                 │
# │  └────┬────┘  └────┬────┘  └────┬────┘                 │
# │       │            │            │                      │
# │  ┌────┴────┐  ┌────┴────┐  ┌────┴────┐                 │
# │  │ Slave1  │  │ Slave2  │  │ Slave3  │                 │
# │  │ (7003)  │  │ (7004)  │  │ (7005)  │                 │
# │  └─────────┘  └─────────┘  └─────────┘                 │
# └─────────────────────────────────────────────────────────┘
```

#### 5.1.2 데이터 모델 설계

```bash
# 사용자 데이터 (Master1 - 7000)
# 해시 태그: {user:ID}

# 사용자 기본 정보
HMSET "user:{1001}:profile" name "김철수" email "kim@example.com" phone "010-1234-5678" created_at "2024-01-15"

# 사용자 주소록
HMSET "user:{1001}:address:home" type "home" address "서울시 강남구" zipcode "12345"
HMSET "user:{1001}:address:office" type "office" address "서울시 서초구" zipcode "54321"

# 사용자 선호도
SADD "user:{1001}:favorites" "product:1001" "product:1002" "product:1003"
ZADD "user:{1001}:viewed" 1710123456 "product:1001" 1710123500 "product:1002"

# 상품 데이터 (Master2 - 7001)
# 해시 태그: {product:ID} 또는 {category:NAME}

# 상품 기본 정보
HMSET "product:{1001}:info" name "iPhone 15" price "1200000" category "electronics" stock "50"
HMSET "product:{1001}:details" description "최신 아이폰" specs "128GB, 블루" brand "Apple"

# 카테고리별 상품 목록
ZADD "category:{electronics}:products" 1200000 "product:1001" 800000 "product:1002"
ZADD "category:{electronics}:popular" 4.8 "product:1001" 4.5 "product:1002"

# 상품 리뷰
ZADD "product:{1001}:reviews" 1710123456 "review:10001" 1710123500 "review:10002"

# 주문 및 장바구니 (Master3 - 7002)
# 해시 태그: {order:DATE} 또는 {cart:USER_ID}

# 장바구니
HMSET "cart:{1001}:items" "product:1001" "2" "product:1002" "1"
HMSET "cart:{1001}:metadata" created_at "2024-03-15" updated_at "2024-03-15" total "3400000"

# 주문 정보
HMSET "order:{20240315}:12345" user_id "1001" total_amount "2400000" status "processing" created_at "1710123456"
LPUSH "order:{20240315}:items:12345" '{"product_id":"1001","quantity":2,"price":"1200000"}' '{"product_id":"1002","quantity":1,"price":"800000"}'

# 일일 주문 통계
HINCRBY "stats:{20240315}:orders" total_orders 1
HINCRBY "stats:{20240315}:orders" total_amount 2400000
SADD "stats:{20240315}:customers" "1001"
```

#### 5.1.3 캐싱 전략 구현

```lua
-- ecommerce_cache_manager.lua
local function get_product_with_cache(product_id, force_refresh)
    local cache_key = "cache:product:" .. product_id
    local cache_ttl = 3600  -- 1시간

    -- 강제 새로고침이 아니면 캐시 확인
    if not force_refresh then
        local cached_data = redis.call('GET', cache_key)
        if cached_data then
            -- 캐시 히트 통계
            redis.call('HINCRBY', 'stats:cache', 'product_hits', 1)
            return cached_data
        end
    end

    -- 캐시 미스: 원본 데이터 조합
    local product_info = redis.call('HGETALL', 'product:{' .. product_id .. '}:info')
    local product_details = redis.call('HGETALL', 'product:{' .. product_id .. '}:details')

    if #product_info == 0 then
        return nil  -- 상품 없음
    end

    -- 데이터 조합
    local combined_data = '{'
    for i = 1, #product_info, 2 do
        combined_data = combined_data .. '"' .. product_info[i] .. '":"' .. product_info[i+1] .. '",'
    end
    for i = 1, #product_details, 2 do
        combined_data = combined_data .. '"' .. product_details[i] .. '":"' .. product_details[i+1] .. '",'
    end
    combined_data = string.sub(combined_data, 1, -2) .. '}'  -- 마지막 콤마 제거

    -- 캐시 저장
    redis.call('SETEX', cache_key, cache_ttl, combined_data)

    -- 캐시 미스 통계
    redis.call('HINCRBY', 'stats:cache', 'product_misses', 1)

    return combined_data
end

-- 상품 정보 업데이트 시 캐시 무효화
local function invalidate_product_cache(product_id)
    local cache_key = "cache:product:" .. product_id
    redis.call('DEL', cache_key)

    -- 관련 캐시도 무효화
    local category = redis.call('HGET', 'product:{' .. product_id .. '}:info', 'category')
    if category then
        redis.call('DEL', 'cache:category:' .. category .. ':products')
        redis.call('DEL', 'cache:category:' .. category .. ':popular')
    end

    return 'OK'
end

-- 장바구니 캐시 관리
local function get_cart_summary(user_id)
    local cache_key = "cache:cart:" .. user_id
    local cache_ttl = 300  -- 5분

    local cached = redis.call('GET', cache_key)
    if cached then
        return cached
    end

    -- 장바구니 데이터 조합
    local cart_items = redis.call('HGETALL', 'cart:{' .. user_id .. '}:items')
    local cart_meta = redis.call('HGETALL', 'cart:{' .. user_id .. '}:metadata')

    local total_items = 0
    local total_amount = 0

    for i = 1, #cart_items, 2 do
        local product_id = cart_items[i]
        local quantity = tonumber(cart_items[i+1])
        local price = tonumber(redis.call('HGET', 'product:{' .. product_id .. '}:info', 'price'))

        total_items = total_items + quantity
        total_amount = total_amount + (price * quantity)
    end

    local summary = string.format('{"total_items":%d,"total_amount":%d,"item_count":%d}',
                                  total_items, total_amount, #cart_items / 2)

    redis.call('SETEX', cache_key, cache_ttl, summary)
    return summary
end

-- 사용할 함수 선택
local action = ARGV[1]
if action == "get_product" then
    return get_product_with_cache(ARGV[2], ARGV[3] == "true")
elseif action == "invalidate_product" then
    return invalidate_product_cache(ARGV[2])
elseif action == "get_cart" then
    return get_cart_summary(ARGV[2])
end

return "Invalid action"
```

### 5.2 실시간 추천 시스템

#### 5.2.1 협업 필터링 구현

```lua
-- recommendation_engine.lua
local user_id = ARGV[1]
local recommendation_count = tonumber(ARGV[2]) or 10

-- 사용자의 구매/조회 이력 가져오기
local user_purchases = redis.call('SMEMBERS', 'user:{' .. user_id .. '}:purchases')
local user_views = redis.call('ZREVRANGE', 'user:{' .. user_id .. '}:viewed', 0, 19, 'WITHSCORES')

-- 유사한 사용자 찾기
local similar_users = {}
local user_similarity = {}

-- 구매 이력 기반 유사도 계산
for i, product in ipairs(user_purchases) do
    local buyers = redis.call('SMEMBERS', 'product:' .. product .. ':buyers')
    for j, buyer in ipairs(buyers) do
        if buyer ~= user_id then
            user_similarity[buyer] = (user_similarity[buyer] or 0) + 1
        end
    end
end

-- 조회 이력 기반 유사도 가중치 추가
for i = 1, #user_views, 2 do
    local product = user_views[i]
    local score = tonumber(user_views[i+1])
    local viewers = redis.call('ZREVRANGE', 'product:' .. product .. ':viewers', 0, 99)

    for j, viewer in ipairs(viewers) do
        if viewer ~= user_id then
            user_similarity[viewer] = (user_similarity[viewer] or 0) + (score / 1000000)  -- 타임스탬프 정규화
        end
    end
end

-- 상위 유사 사용자 선별
local sorted_similar = {}
for similar_user, similarity in pairs(user_similarity) do
    table.insert(sorted_similar, {similar_user, similarity})
end

table.sort(sorted_similar, function(a, b) return a[2] > b[2] end)

-- 추천 상품 생성
local recommended_products = {}
local product_scores = {}

-- 상위 20명의 유사 사용자 기준
for i = 1, math.min(20, #sorted_similar) do
    local similar_user = sorted_similar[i][1]
    local similarity_weight = sorted_similar[i][2]

    -- 유사 사용자의 최근 구매/조회 상품
    local similar_purchases = redis.call('SMEMBERS', 'user:{' .. similar_user .. '}:purchases')
    local similar_views = redis.call('ZREVRANGE', 'user:{' .. similar_user .. '}:viewed', 0, 9)

    -- 구매 상품 (높은 가중치)
    for j, product in ipairs(similar_purchases) do
        if not redis.call('SISMEMBER', 'user:{' .. user_id .. '}:purchases', product) then
            product_scores[product] = (product_scores[product] or 0) + (similarity_weight * 3)
        end
    end

    -- 조회 상품 (낮은 가중치)
    for j, product in ipairs(similar_views) do
        if not redis.call('SISMEMBER', 'user:{' .. user_id .. '}:purchases', product) then
            product_scores[product] = (product_scores[product] or 0) + (similarity_weight * 1)
        end
    end
end

-- 추천 점수 순으로 정렬
local final_recommendations = {}
for product, score in pairs(product_scores) do
    table.insert(final_recommendations, {product, score})
end

table.sort(final_recommendations, function(a, b) return a[2] > b[2] end)

-- 상위 N개 추천 상품 반환
local result = {}
for i = 1, math.min(recommendation_count, #final_recommendations) do
    local product_id = final_recommendations[i][1]
    local score = final_recommendations[i][2]

    -- 상품 기본 정보 포함
    local product_info = redis.call('HMGET', 'product:{' .. product_id .. '}:info', 'name', 'price', 'category')

    table.insert(result, {
        product_id = product_id,
        name = product_info[1],
        price = product_info[2],
        category = product_info[3],
        recommendation_score = score
    })
end

-- 추천 결과 캐싱 (30분)
local cache_key = 'cache:recommendations:' .. user_id
local cache_data = '{"recommendations":' .. table.concat(result, ',') .. ',"generated_at":"' .. redis.call('TIME')[1] .. '"}'
redis.call('SETEX', cache_key, 1800, cache_data)

return result
```

#### 5.2.2 실시간 인기 상품 트래킹

```lua
-- trending_products.lua
local time_window = tonumber(ARGV[1]) or 3600  -- 1시간 기본
local current_time = redis.call('TIME')[1]
local window_start = current_time - time_window

local trending_analysis = {
    time_window = time_window,
    analyzed_events = 0,
    trending_products = {}
}

-- 실시간 이벤트 스트림에서 데이터 수집
local events = redis.call('XREVRANGE', 'events:product_interactions', '+', '-', 'COUNT', 10000)

local product_interactions = {}
local category_interactions = {}

for i, event in ipairs(events) do
    local event_id = event[1]
    local event_data = event[2]

    -- 이벤트 타임스탬프 추출
    local event_timestamp = tonumber(string.match(event_id, '(%d+)'))

    if event_timestamp >= window_start then
        trending_analysis.analyzed_events = trending_analysis.analyzed_events + 1

        -- 이벤트 데이터 파싱
        local product_id, action, user_id
        for j = 1, #event_data, 2 do
            if event_data[j] == 'product_id' then
                product_id = event_data[j+1]
            elseif event_data[j] == 'action' then
                action = event_data[j+1]
            elseif event_data[j] == 'user_id' then
                user_id = event_data[j+1]
            end
        end

        if product_id and action then
            if not product_interactions[product_id] then
                product_interactions[product_id] = {
                    views = 0,
                    purchases = 0,
                    carts = 0,
                    total_score = 0
                }
            end

            -- 액션별 가중치 적용
            local weights = {view = 1, cart = 3, purchase = 10}
            local weight = weights[action] or 1

            product_interactions[product_id][action .. 's'] =
                (product_interactions[product_id][action .. 's'] or 0) + 1
            product_interactions[product_id].total_score =
                product_interactions[product_id].total_score + weight
        end
    end
end

-- 트렌딩 점수 계산 및 정렬
local trending_products = {}
for product_id, interactions in pairs(product_interactions) do
    -- 속도 가중치 (최근 활동일수록 높은 점수)
    local velocity_bonus = interactions.total_score / (time_window / 3600)  -- 시간당 점수

    -- 다양성 보너스 (여러 액션 타입이 있으면 보너스)
    local diversity_bonus = 0
    if interactions.purchases > 0 then diversity_bonus = diversity_bonus + 5 end
    if interactions.carts > 0 then diversity_bonus = diversity_bonus + 3 end
    if interactions.views > 0 then diversity_bonus = diversity_bonus + 1 end

    local final_score = interactions.total_score + velocity_bonus + diversity_bonus

    table.insert(trending_products, {
        product_id = product_id,
        interactions = interactions,
        trending_score = final_score
    })
end

-- 점수순 정렬
table.sort(trending_products, function(a, b)
    return a.trending_score > b.trending_score
end)

-- 상위 20개 제품의 상세 정보 조회
for i = 1, math.min(20, #trending_products) do
    local product = trending_products[i]
    local product_info = redis.call('HMGET', 'product:{' .. product.product_id .. '}:info',
                                    'name', 'price', 'category', 'stock')

    product.name = product_info[1]
    product.price = product_info[2]
    product.category = product_info[3]
    product.stock = product_info[4]
end

trending_analysis.trending_products = trending_products

-- 결과 캐싱 (5분)
local cache_key = 'cache:trending:' .. time_window
redis.call('SETEX', cache_key, 300, cjson.encode(trending_analysis))

-- 카테고리별 트렌딩도 업데이트
for i = 1, math.min(5, #trending_products) do
    local product = trending_products[i]
    local category = product.category
    if category then
        redis.call('ZADD', 'trending:category:' .. category,
                   product.trending_score, product.product_id)
        redis.call('EXPIRE', 'trending:category:' .. category, time_window)
    end
end

return trending_analysis
```

---

## 6. 성능 모니터링 및 최적화

### 6.1 클러스터 성능 메트릭

#### 6.1.1 종합 성능 모니터링

```lua
-- cluster_performance_monitor.lua
local monitoring_result = {
    timestamp = redis.call('TIME')[1],
    cluster_health = 'unknown',
    nodes = {},
    performance_metrics = {},
    alerts = {}
}

-- 클러스터 노드 목록 가져오기
local cluster_nodes = redis.call('CLUSTER', 'NODES')
local node_lines = {}
for line in string.gmatch(cluster_nodes, '[^\r\n]+') do
    table.insert(node_lines, line)
end

local total_ops = 0
local total_memory = 0
local total_slots_ok = 0
local failed_nodes = 0

-- 각 노드별 상세 분석
for i, line in ipairs(node_lines) do
    local parts = {}
    for part in string.gmatch(line, '[^%s]+') do
        table.insert(parts, part)
    end

    if #parts >= 8 then
        local node_id = parts[1]
        local address = parts[2]
        local flags = parts[3]
        local slots = parts[9] or ''

        local is_master = string.find(flags, 'master') ~= nil
        local is_fail = string.find(flags, 'fail') ~= nil

        if is_fail then
            failed_nodes = failed_nodes + 1
            table.insert(monitoring_result.alerts, {
                type = 'node_failure',
                node_id = node_id,
                address = address
            })
        end

        -- 마스터 노드에 대한 상세 분석
        if is_master and not is_fail then
            local host, port = string.match(address, '([^:]+):(%d+)')

            -- 원격 노드 정보 수집 (실제로는 CLIENT LIST로 연결된 노드들 확인)
            local node_info = {
                node_id = string.sub(node_id, 1, 8),
                address = address,
                role = 'master',
                slots_count = 0,
                memory_usage = 0,
                ops_per_sec = 0,
                connected_clients = 0,
                hit_rate = 0
            }

            -- 슬롯 개수 계산
            if slots ~= '' then
                local slot_ranges = {}
                for range in string.gmatch(slots, '[^%s]+') do
                    if string.find(range, '-') then
                        local start_slot, end_slot = string.match(range, '(%d+)-(%d+)')
                        node_info.slots_count = node_info.slots_count + (tonumber(end_slot) - tonumber(start_slot) + 1)
                    else
                        node_info.slots_count = node_info.slots_count + 1
                    end
                end
                total_slots_ok = total_slots_ok + node_info.slots_count
            end

            -- 성능 메트릭 시뮬레이션 (실제로는 각 노드에서 INFO 명령으로 수집)
            node_info.memory_usage = math.random(1000000000, 4000000000)  -- 1-4GB
            node_info.ops_per_sec = math.random(1000, 10000)
            node_info.connected_clients = math.random(10, 100)
            node_info.hit_rate = math.random(75, 95)

            total_memory = total_memory + node_info.memory_usage
            total_ops = total_ops + node_info.ops_per_sec

            -- 성능 이슈 체크
            if node_info.memory_usage > 3500000000 then  -- 3.5GB 이상
                table.insert(monitoring_result.alerts, {
                    type = 'high_memory_usage',
                    node_id = node_id,
                    memory_usage = node_info.memory_usage
                })
            end

            if node_info.hit_rate < 80 then
                table.insert(monitoring_result.alerts, {
                    type = 'low_hit_rate',
                    node_id = node_id,
                    hit_rate = node_info.hit_rate
                })
            end

            table.insert(monitoring_result.nodes, node_info)
        end
    end
end

-- 전체 클러스터 성능 메트릭
monitoring_result.performance_metrics = {
    total_nodes = #monitoring_result.nodes,
    failed_nodes = failed_nodes,
    total_slots_coverage = total_slots_ok,
    total_memory_usage = total_memory,
    total_ops_per_sec = total_ops,
    avg_memory_per_node = #monitoring_result.nodes > 0 and (total_memory / #monitoring_result.nodes) or 0,
    avg_ops_per_node = #monitoring_result.nodes > 0 and (total_ops / #monitoring_result.nodes) or 0
}

-- 클러스터 전체 상태 평가
if failed_nodes > 0 then
    monitoring_result.cluster_health = 'critical'
elseif total_slots_ok < 16384 then
    monitoring_result.cluster_health = 'degraded'
elseif #monitoring_result.alerts > 0 then
    monitoring_result.cluster_health = 'warning'
else
    monitoring_result.cluster_health = 'healthy'
end

-- 모니터링 결과 저장
local daily_key = 'monitoring:' .. string.sub(monitoring_result.timestamp, 1, 8)
redis.call('ZADD', daily_key .. ':health_score', monitoring_result.timestamp,
           monitoring_result.cluster_health == 'healthy' and 100 or
           monitoring_result.cluster_health == 'warning' and 70 or
           monitoring_result.cluster_health == 'degraded' and 40 or 20)

redis.call('ZADD', daily_key .. ':total_ops', monitoring_result.timestamp, total_ops)
redis.call('ZADD', daily_key .. ':total_memory', monitoring_result.timestamp, total_memory)

-- 7일간 보관
redis.call('EXPIRE', daily_key .. ':health_score', 604800)
redis.call('EXPIRE', daily_key .. ':total_ops', 604800)
redis.call('EXPIRE', daily_key .. ':total_memory', 604800)

-- 알림이 있으면 알림 큐에 추가
if #monitoring_result.alerts > 0 then
    for j, alert in ipairs(monitoring_result.alerts) do
        local alert_message = cjson.encode({
            timestamp = monitoring_result.timestamp,
            severity = monitoring_result.cluster_health,
            alert = alert
        })
        redis.call('LPUSH', 'alerts:cluster', alert_message)
    end
    redis.call('LTRIM', 'alerts:cluster', 0, 999)
end

return monitoring_result
```

#### 6.1.2 슬롯 분산 최적화

```bash
#!/bin/bash
# cluster_rebalance_optimizer.sh

CLUSTER_HOST="127.0.0.1"
CLUSTER_PORT="7000"

# 현재 슬롯 분산 분석
analyze_slot_distribution() {
    echo "=== 슬롯 분산 분석 ==="

    declare -A slot_counts
    declare -A node_addresses

    # 클러스터 노드 정보 파싱
    redis-cli -h $CLUSTER_HOST -p $CLUSTER_PORT cluster nodes | grep master | while read line; do
        node_id=$(echo $line | awk '{print $1}')
        address=$(echo $line | awk '{print $2}')
        slots=$(echo $line | cut -d' ' -f9-)

        # 슬롯 개수 계산
        slot_count=0
        for slot_range in $slots; do
            if [[ $slot_range =~ ^[0-9]+-[0-9]+$ ]]; then
                start=$(echo $slot_range | cut -d'-' -f1)
                end=$(echo $slot_range | cut -d'-' -f2)
                count=$((end - start + 1))
                slot_count=$((slot_count + count))
            elif [[ $slot_range =~ ^[0-9]+$ ]]; then
                slot_count=$((slot_count + 1))
            fi
        done

        echo "노드 ${node_id:0:8} ($address): $slot_count 슬롯"

        # 불균형 감지
        optimal_slots=$((16384 / 3))  # 3개 마스터 가정
        diff=$((slot_count - optimal_slots))

        if [ $diff -gt 500 ]; then
            echo "  ⚠️  과부하: +$diff 슬롯"
        elif [ $diff -lt -500 ]; then
            echo "  ⚠️  저부하: $diff 슬롯"
        else
            echo "  ✅ 균형 상태"
        fi
    done
}

# 핫스팟 감지
detect_hotspots() {
    echo -e "\n=== 핫스팟 감지 ==="

    # 각 노드의 ops/sec 수집
    redis-cli -h $CLUSTER_HOST -p $CLUSTER_PORT cluster nodes | grep master | while read line; do
        address=$(echo $line | awk '{print $2}')
        host=$(echo $address | cut -d':' -f1)
        port=$(echo $address | cut -d':' -f2)

        ops_per_sec=$(redis-cli -h $host -p $port INFO stats | grep instantaneous_ops_per_sec | cut -d':' -f2 | tr -d '\r')
        memory_usage=$(redis-cli -h $host -p $port INFO memory | grep used_memory: | cut -d':' -f2 | tr -d '\r')

        echo "노드 $address:"
        echo "  OPS/sec: $ops_per_sec"
        echo "  메모리: $(($memory_usage / 1024 / 1024))MB"

        # 핫스팟 기준 (다른 노드 대비 2배 이상)
        if [ "$ops_per_sec" -gt 5000 ]; then
            echo "  🔥 핫스팟 감지: 높은 처리량"
        fi

        if [ "$memory_usage" -gt 3000000000 ]; then  # 3GB 이상
            echo "  🔥 핫스팟 감지: 높은 메모리 사용"
        fi
    done
}

# 자동 최적화 권장사항
generate_optimization_recommendations() {
    echo -e "\n=== 최적화 권장사항 ==="

    # 슬롯 분산 균형 체크
    declare -a slot_counts
    total_nodes=0

    while read line; do
        if [[ $line == *"master"* ]]; then
            slots=$(echo $line | cut -d' ' -f9-)
            slot_count=0

            for slot_range in $slots; do
                if [[ $slot_range =~ ^[0-9]+-[0-9]+$ ]]; then
                    start=$(echo $slot_range | cut -d'-' -f1)
                    end=$(echo $slot_range | cut -d'-' -f2)
                    count=$((end - start + 1))
                    slot_count=$((slot_count + count))
                elif [[ $slot_range =~ ^[0-9]+$ ]]; then
                    slot_count=$((slot_count + 1))
                fi
            done

            slot_counts[$total_nodes]=$slot_count
            total_nodes=$((total_nodes + 1))
        fi
    done < <(redis-cli -h $CLUSTER_HOST -p $CLUSTER_PORT cluster nodes)

    # 최대/최소 슬롯 차이 계산
    max_slots=0
    min_slots=16384

    for i in $(seq 0 $((total_nodes - 1))); do
        if [ ${slot_counts[$i]} -gt $max_slots ]; then
            max_slots=${slot_counts[$i]}
        fi
        if [ ${slot_counts[$i]} -lt $min_slots ]; then
            min_slots=${slot_counts[$i]}
        fi
    done

    slot_diff=$((max_slots - min_slots))

    echo "슬롯 분산 상태:"
    echo "  최대 슬롯: $max_slots"
    echo "  최소 슬롯: $min_slots"
    echo "  차이: $slot_diff"

    if [ $slot_diff -gt 1000 ]; then
        echo ""
        echo "🔧 권장 조치사항:"
        echo "1. 슬롯 리밸런싱 실행:"
        echo "   redis-cli --cluster rebalance $CLUSTER_HOST:$CLUSTER_PORT"
        echo ""
        echo "2. 수동 슬롯 이동 (정밀 조정):"
        move_slots=$(($slot_diff / 2))
        echo "   redis-cli --cluster reshard $CLUSTER_HOST:$CLUSTER_PORT --cluster-slots $move_slots"
        echo ""
        echo "3. 핫키 분산 (애플리케이션 레벨):"
        echo "   - 해시 태그 사용 재검토"
        echo "   - 키 네이밍 패턴 최적화"
        echo "   - 캐싱 전략 조정"
    else
        echo "✅ 슬롯 분산이 양호합니다."
    fi
}

# 메인 실행
main() {
    echo "Redis 클러스터 최적화 분석기"
    echo "==============================="

    analyze_slot_distribution
    detect_hotspots
    generate_optimization_recommendations

    echo -e "\n완료! 정기적으로 실행하여 클러스터 상태를 모니터링하세요."
}

main "$@"
```

---

## 7. 운영 및 유지보수

### 7.1 클러스터 운영 자동화

#### 7.1.1 헬스체크 및 자동 복구

```bash
#!/bin/bash
# cluster_health_monitor.sh

CONFIG_FILE="/etc/redis/cluster_monitor.conf"
LOG_FILE="/var/log/redis/cluster_monitor.log"
ALERT_EMAIL="admin@company.com"

# 기본 설정
CLUSTER_NODES=("127.0.0.1:7000" "127.0.0.1:7001" "127.0.0.1:7002")
CHECK_INTERVAL=30
AUTO_RECOVERY=true
ALERT_THRESHOLD=2

# 설정 파일 로드
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

send_alert() {
    local subject="$1"
    local message="$2"
    local priority="$3"

    # 이메일 알림
    echo "$message" | mail -s "[$priority] $subject" "$ALERT_EMAIL" 2>/dev/null

    # 슬랙 알림 (웹훅 URL이 설정된 경우)
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"[$priority] $subject\n$message\"}" \
            "$SLACK_WEBHOOK" 2>/dev/null
    fi

    log "ALERT SENT: [$priority] $subject"
}

# 개별 노드 헬스체크
check_node_health() {
    local node="$1"
    local host=$(echo "$node" | cut -d':' -f1)
    local port=$(echo "$node" | cut -d':' -f2)

    local health_score=0
    local issues=()

    # 1. 연결 테스트
    if timeout 5 redis-cli -h "$host" -p "$port" ping >/dev/null 2>&1; then
        health_score=$((health_score + 25))
    else
        issues+=("connection_failed")
        return 0
    fi

    # 2. 클러스터 상태 체크
    local cluster_state=$(redis-cli -h "$host" -p "$port" cluster info | grep cluster_state | cut -d':' -f2 | tr -d '\r')
    if [ "$cluster_state" = "ok" ]; then
        health_score=$((health_score + 25))
    else
        issues+=("cluster_state_$cluster_state")
    fi

    # 3. 메모리 사용률 체크
    local memory_info=$(redis-cli -h "$host" -p "$port" info memory)
    local used_memory=$(echo "$memory_info" | grep '^used_memory:' | cut -d':' -f2 | tr -d '\r')
    local max_memory=$(redis-cli -h "$host" -p "$port" config get maxmemory | tail -1)

    if [ "$max_memory" != "0" ] && [ -n "$used_memory" ]; then
        local usage_percent=$(echo "scale=0; $used_memory * 100 / $max_memory" | bc -l)
        if [ "$usage_percent" -lt 80 ]; then
            health_score=$((health_score + 25))
        elif [ "$usage_percent" -lt 90 ]; then
            health_score=$((health_score + 15))
            issues+=("high_memory_usage_${usage_percent}%")
        else
            issues+=("critical_memory_usage_${usage_percent}%")
        fi
    else
        health_score=$((health_score + 25))  # 메모리 제한 없음
    fi

    # 4. 응답 시간 체크
    local start_time=$(date +%s%3N)
    redis-cli -h "$host" -p "$port" ping >/dev/null 2>&1
    local end_time=$(date +%s%3N)
    local response_time=$((end_time - start_time))

    if [ "$response_time" -lt 100 ]; then
        health_score=$((health_score + 25))
    elif [ "$response_time" -lt 500 ]; then
        health_score=$((health_score + 15))
        issues+=("slow_response_${response_time}ms")
    else
        issues+=("very_slow_response_${response_time}ms")
    fi

    # 결과 출력
    echo "$health_score:$(IFS=,; echo "${issues[*]}")"
}

# 클러스터 전체 헬스체크
check_cluster_health() {
    log "클러스터 헬스체크 시작"

    local total_score=0
    local node_count=0
    local critical_issues=0
    local all_issues=()

    for node in "${CLUSTER_NODES[@]}"; do
        local result=$(check_node_health "$node")
        local score=$(echo "$result" | cut -d':' -f1)
        local issues=$(echo "$result" | cut -d':' -f2)

        log "노드 $node: 점수 $score/100"

        if [ -n "$issues" ] && [ "$issues" != "" ]; then
            log "  이슈: $issues"
            all_issues+=("$node:$issues")

            if [ "$score" -lt 50 ]; then
                critical_issues=$((critical_issues + 1))
            fi
        fi

        total_score=$((total_score + score))
        node_count=$((node_count + 1))
    done

    local avg_score=$((total_score / node_count))

    # 클러스터 전체 상태 평가
    local cluster_status
    if [ "$critical_issues" -gt 0 ]; then
        cluster_status="CRITICAL"
    elif [ "$avg_score" -lt 70 ]; then
        cluster_status="WARNING"
    elif [ "$avg_score" -lt 90 ]; then
        cluster_status="NOTICE"
    else
        cluster_status="HEALTHY"
    fi

    log "클러스터 전체 상태: $cluster_status (평균 점수: $avg_score/100)"

    # 알림 발송 조건
    if [ "$cluster_status" = "CRITICAL" ]; then
        send_alert "Redis 클러스터 심각한 문제" \
                   "심각한 노드 장애가 $critical_issues개 감지되었습니다.\n문제 노드: $(IFS=$'\n'; echo "${all_issues[*]}")" \
                   "CRITICAL"
    elif [ "$cluster_status" = "WARNING" ] && [ ${#all_issues[@]} -ge $ALERT_THRESHOLD ]; then
        send_alert "Redis 클러스터 경고" \
                   "클러스터 성능 저하가 감지되었습니다.\n이슈 목록: $(IFS=$'\n'; echo "${all_issues[*]}")" \
                   "WARNING"
    fi

    # 자동 복구 시도
    if [ "$AUTO_RECOVERY" = true ] && [ "$critical_issues" -gt 0 ]; then
        attempt_auto_recovery "${all_issues[@]}"
    fi
}

# 자동 복구 시도
attempt_auto_recovery() {
    local issues=("$@")

    log "자동 복구 시도 시작"

    for issue in "${issues[@]}"; do
        local node=$(echo "$issue" | cut -d':' -f1)
        local problem=$(echo "$issue" | cut -d':' -f2)

        if [[ $problem == *"connection_failed"* ]]; then
            log "노드 $node 연결 실패 - 서비스 재시작 시도"

            local port=$(echo "$node" | cut -d':' -f2)
            systemctl restart "redis-$port"

            # 재시작 후 검증
            sleep 10
            if timeout 5 redis-cli -h "$(echo "$node" | cut -d':' -f1)" -p "$port" ping >/dev/null 2>&1; then
                log "노드 $node 복구 성공"
                send_alert "Redis 노드 자동 복구 성공" \
                           "노드 $node가 성공적으로 복구되었습니다." \
                           "INFO"
            else
                log "노드 $node 복구 실패"
                send_alert "Redis 노드 자동 복구 실패" \
                           "노드 $node 복구에 실패했습니다. 수동 개입이 필요합니다." \
                           "CRITICAL"
            fi

        elif [[ $problem == *"critical_memory_usage"* ]]; then
            log "노드 $node 메모리 부족 - 메모리 정리 시도"

            local host=$(echo "$node" | cut -d':' -f1)
            local port=$(echo "$node" | cut -d':' -f2)

            # 메모리 정리 명령 실행
            redis-cli -h "$host" -p "$port" MEMORY PURGE >/dev/null 2>&1

            log "노드 $node 메모리 정리 완료"
        fi
    done

    log "자동 복구 시도 완료"
}

# 모니터링 루프
monitoring_loop() {
    log "Redis 클러스터 모니터링 시작 (체크 간격: ${CHECK_INTERVAL}초)"

    while true; do
        check_cluster_health
        sleep "$CHECK_INTERVAL"
    done
}

# 시그널 핸들러
cleanup() {
    log "모니터링 종료"
    exit 0
}

trap cleanup SIGTERM SIGINT

# 메인 실행
case "${1:-monitor}" in
    "monitor")
        monitoring_loop
        ;;
    "check")
        check_cluster_health
        ;;
    "test-alert")
        send_alert "테스트 알림" "Redis 클러스터 모니터링 알림 테스트입니다." "INFO"
        ;;
    *)
        echo "사용법: $0 [monitor|check|test-alert]"
        exit 1
        ;;
esac
```

#### 7.1.2 백업 자동화

```bash
#!/bin/bash
# automated_cluster_backup.sh

BACKUP_CONFIG="/etc/redis/backup.conf"
BACKUP_BASE_DIR="/var/backups/redis-cluster"
LOG_FILE="/var/log/redis/backup.log"
RETENTION_DAYS=30

# 기본 설정
CLUSTER_NODES=("127.0.0.1:7000" "127.0.0.1:7001" "127.0.0.1:7002" "127.0.0.1:7003" "127.0.0.1:7004" "127.0.0.1:7005")
BACKUP_SCHEDULE="daily"  # daily, weekly, monthly
COMPRESSION_LEVEL=6
ENCRYPT_BACKUPS=false
S3_UPLOAD=false

# 설정 파일 로드
if [ -f "$BACKUP_CONFIG" ]; then
    source "$BACKUP_CONFIG"
fi

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

# 백업 디렉토리 구조 생성
setup_backup_structure() {
    local backup_date="$1"
    local backup_dir="$BACKUP_BASE_DIR/$backup_date"

    mkdir -p "$backup_dir"/{data,config,logs,metadata}
    echo "$backup_dir"
}

# 개별 노드 백업
backup_node() {
    local node="$1"
    local backup_dir="$2"
    local host=$(echo "$node" | cut -d':' -f1)
    local port=$(echo "$node" | cut -d':' -f2)

    log "노드 $node 백업 시작"

    # 1. 설정 파일 백업
    if [ -f "/etc/redis/redis-$port.conf" ]; then
        cp "/etc/redis/redis-$port.conf" "$backup_dir/config/"
    fi

    # 2. 백그라운드 저장 실행
    local save_start=$(redis-cli -h "$host" -p "$port" LASTSAVE)
    redis-cli -h "$host" -p "$port" BGSAVE >/dev/null 2>&1

    if [ $? -ne 0 ]; then
        log "ERROR: 노드 $node BGSAVE 실패"
        return 1
    fi

    # 3. 백그라운드 저장 완료 대기
    local timeout=300  # 5분 타임아웃
    local elapsed=0

    while [ $elapsed -lt $timeout ]; do
        local current_save=$(redis-cli -h "$host" -p "$port" LASTSAVE)
        if [ "$current_save" -gt "$save_start" ]; then
            break
        fi
        sleep 5
        elapsed=$((elapsed + 5))
    done

    if [ $elapsed -ge $timeout ]; then
        log "ERROR: 노드 $node BGSAVE 타임아웃"
        return 1
    fi

    # 4. 데이터 파일 복사
    local data_dir=$(redis-cli -h "$host" -p "$port" CONFIG GET dir | tail -1)
    local db_filename=$(redis-cli -h "$host" -p "$port" CONFIG GET dbfilename | tail -1)
    local source_file="$data_dir/$db_filename"

    if [ -f "$source_file" ]; then
        cp "$source_file" "$backup_dir/data/dump_${host}_${port}.rdb"

        # 파일 무결성 체크
        if file "$backup_dir/data/dump_${host}_${port}.rdb" | grep -q "data"; then
            log "노드 $node 데이터 백업 완료"
        else
            log "ERROR: 노드 $node 백업 파일 손상"
            return 1
        fi
    else
        log "WARNING: 노드 $node 데이터 파일 없음 ($source_file)"
    fi

    # 5. 노드 정보 메타데이터 저장
    cat > "$backup_dir/metadata/node_${host}_${port}.json" << EOF
{
    "node": "$node",
    "backup_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "redis_version": "$(redis-cli -h "$host" -p "$port" INFO server | grep redis_version | cut -d':' -f2 | tr -d '\r')",
    "used_memory": "$(redis-cli -h "$host" -p "$port" INFO memory | grep '^used_memory:' | cut -d':' -f2 | tr -d '\r')",
    "total_keys": "$(redis-cli -h "$host" -p "$port" INFO keyspace | grep -o 'keys=[0-9]*' | cut -d'=' -f2 | head -1)"
}
EOF

    return 0
}

# 클러스터 메타데이터 백업
backup_cluster_metadata() {
    local backup_dir="$1"

    log "클러스터 메타데이터 백업"

    # 클러스터 토폴로지
    redis-cli -h 127.0.0.1 -p 7000 CLUSTER NODES > "$backup_dir/metadata/cluster_nodes.txt"
    redis-cli -h 127.0.0.1 -p 7000 CLUSTER INFO > "$backup_dir/metadata/cluster_info.txt"

    # 슬롯 분배 정보
    redis-cli -h 127.0.0.1 -p 7000 CLUSTER SLOTS > "$backup_dir/metadata/cluster_slots.txt"

    # 백업 시점 정보
    cat > "$backup_dir/metadata/backup_info.json" << EOF
{
    "backup_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "backup_type": "$BACKUP_SCHEDULE",
    "cluster_nodes": [$(printf '"%s",' "${CLUSTER_NODES[@]}" | sed 's/,$//')]},
    "total_nodes": ${#CLUSTER_NODES[@]},
    "backup_tool_version": "1.0"
}
EOF
}

# 백업 압축 및 암호화
compress_and_encrypt() {
    local backup_dir="$1"
    local backup_base=$(basename "$backup_dir")

    log "백업 압축 시작"

    cd "$(dirname "$backup_dir")"

    if [ "$ENCRYPT_BACKUPS" = true ] && [ -n "$BACKUP_ENCRYPTION_KEY" ]; then
        # 암호화 백업
        tar -czf - "$backup_base" | \
        openssl enc -aes-256-cbc -salt -k "$BACKUP_ENCRYPTION_KEY" > "${backup_base}.tar.gz.enc"

        if [ $? -eq 0 ]; then
            log "암호화된 백업 생성 완료: ${backup_base}.tar.gz.enc"
            rm -rf "$backup_base"
            echo "${backup_dir}.tar.gz.enc"
        else
            log "ERROR: 백업 암호화 실패"
            return 1
        fi
    else
        # 일반 압축
        tar -czf "${backup_base}.tar.gz" "$backup_base"

        if [ $? -eq 0 ]; then
            log "압축된 백업 생성 완료: ${backup_base}.tar.gz"
            rm -rf "$backup_base"
            echo "${backup_dir}.tar.gz"
        else
            log "ERROR: 백업 압축 실패"
            return 1
        fi
    fi
}

# S3 업로드
upload_to_s3() {
    local backup_file="$1"

    if [ "$S3_UPLOAD" = true ] && [ -n "$S3_BUCKET" ]; then
        log "S3 업로드 시작: $backup_file"

        aws s3 cp "$backup_file" "s3://$S3_BUCKET/redis-cluster-backups/" \
            --storage-class STANDARD_IA

        if [ $? -eq 0 ]; then
            log "S3 업로드 완료"

            # 로컬 파일 정리 (옵션)
            if [ "$S3_DELETE_LOCAL" = true ]; then
                rm -f "$backup_file"
                log "로컬 백업 파일 삭제"
            fi
        else
            log "ERROR: S3 업로드 실패"
        fi
    fi
}

# 오래된 백업 정리
cleanup_old_backups() {
    log "오래된 백업 정리 시작 (보존 기간: $RETENTION_DAYS일)"

    find "$BACKUP_BASE_DIR" -name "*.tar.gz*" -mtime +$RETENTION_DAYS -delete

    local deleted_count=$(find "$BACKUP_BASE_DIR" -name "*.tar.gz*" -mtime +$RETENTION_DAYS | wc -l)
    log "정리된 백업 파일: $deleted_count개"
}

# 메인 백업 프로세스
perform_backup() {
    local backup_date=$(date +%Y%m%d_%H%M%S)
    local backup_dir=$(setup_backup_structure "$backup_date")

    log "=== Redis 클러스터 백업 시작 ==="
    log "백업 디렉토리: $backup_dir"

    local failed_nodes=0
    local total_nodes=${#CLUSTER_NODES[@]}

    # 각 노드 백업
    for node in "${CLUSTER_NODES[@]}"; do
        if ! backup_node "$node" "$backup_dir"; then
            failed_nodes=$((failed_nodes + 1))
        fi
    done

    # 클러스터 메타데이터 백업
    backup_cluster_metadata "$backup_dir"

    # 백업 결과 평가
    if [ $failed_nodes -eq 0 ]; then
        log "모든 노드 백업 성공"

        # 압축 및 암호화
        local compressed_backup=$(compress_and_encrypt "$backup_dir")

        if [ $? -eq 0 ]; then
            # S3 업로드
            upload_to_s3 "$compressed_backup"

            # 성공 알림
            local backup_size=$(du -h "$compressed_backup" 2>/dev/null | cut -f1)
            log "백업 완료: $compressed_backup (크기: $backup_size)"

        else
            log "ERROR: 백업 압축 실패"
        fi

    else
        log "ERROR: $failed_nodes/$total_nodes 노드 백업 실패"

        # 실패한 백업 디렉토리 정리
        rm -rf "$backup_dir"
    fi

    # 오래된 백업 정리
    cleanup_old_backups

    log "=== 백업 프로세스 완료 ==="
}

# 백업 검증
verify_backup() {
    local backup_file="$1"

    if [ -z "$backup_file" ]; then
        echo "사용법: $0 verify <백업파일>"
        return 1
    fi

    log "백업 파일 검증: $backup_file"

    # 파일 존재 확인
    if [ ! -f "$backup_file" ]; then
        log "ERROR: 백업 파일을 찾을 수 없습니다"
        return 1
    fi

    # 압축 파일 무결성 검증
    if [[ $backup_file == *.tar.gz.enc ]]; then
        # 암호화된 파일
        if [ -z "$BACKUP_ENCRYPTION_KEY" ]; then
            log "ERROR: 암호화 키가 설정되지 않음"
            return 1
        fi

        openssl enc -d -aes-256-cbc -k "$BACKUP_ENCRYPTION_KEY" -in "$backup_file" | tar -tzf - >/dev/null 2>&1
    else
        # 일반 압축 파일
        tar -tzf "$backup_file" >/dev/null 2>&1
    fi

    if [ $? -eq 0 ]; then
        log "백업 파일 검증 성공"
        return 0
    else
        log "ERROR: 백업 파일 손상"
        return 1
    fi
}

# 메인 실행
case "${1:-backup}" in
    "backup")
        perform_backup
        ;;
    "verify")
        verify_backup "$2"
        ;;
    "list")
        echo "사용 가능한 백업 파일:"
        ls -lh "$BACKUP_BASE_DIR"/*.tar.gz* 2>/dev/null | head -20
        ;;
    "cleanup")
        cleanup_old_backups
        ;;
    *)
        echo "사용법: $0 [backup|verify|list|cleanup]"
        exit 1
        ;;
esac
```

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: 클러스터 구성 중 슬롯 미할당 문제

**상황**: 신입 개발자가 Redis 클러스터를 구성했으나 "CLUSTERDOWN Hash slot not served" 오류 발생

```bash
# ❌ 주니어 개발자의 실수
# 노드만 추가하고 슬롯을 할당하지 않음
redis-cli --cluster add-node 127.0.0.1:7006 127.0.0.1:7000

# 테스트
redis-cli -c -p 7000 SET mykey "value"
# Error: CLUSTERDOWN Hash slot not served
```

**문제점**:
- 노드를 클러스터에 추가만 하고 해시 슬롯을 할당하지 않음
- 16384개 슬롯이 모두 할당되어야 클러스터가 작동함
- 새 노드는 슬롯이 없는 빈 마스터 상태

**해결책**:
```bash
# ✅ 올바른 방법: 슬롯 재분배 필요
# 1. 클러스터 상태 확인
redis-cli -c -p 7000 cluster nodes

# 2. 새 노드에 슬롯 할당 (리샤딩)
redis-cli --cluster reshard 127.0.0.1:7000
# How many slots? 4096
# Receiving node ID? [새 노드 7006의 ID]
# Source nodes: all

# 3. 확인
redis-cli -c -p 7000 cluster info
# 출력: cluster_slots_assigned:16384
# 출력: cluster_state:ok
```

**배운 점**:
- 클러스터의 16384개 슬롯이 모두 할당되어야 정상 작동
- 새 노드 추가 = 노드 추가 + 슬롯 재분배 2단계 필요
- `cluster info`로 항상 슬롯 할당 상태 확인

---

### 시나리오 2: MULTI 명령이 클러스터에서 실패

**상황**: 단일 Redis에서 잘 작동하던 트랜잭션 코드가 클러스터에서 오류 발생

```python
# ❌ 주니어 개발자의 코드
from redis.cluster import RedisCluster

rc = RedisCluster(host='127.0.0.1', port=7000)

# 다중 키 트랜잭션 시도
pipe = rc.pipeline()
pipe.set('user:1001', 'Alice')
pipe.set('user:1002', 'Bob')
pipe.set('order:5001', 'Product A')
pipe.execute()

# Error: CROSSSLOT Keys in request don't hash to the same slot
```

**문제점**:
- 클러스터에서는 여러 슬롯에 걸친 트랜잭션 불가능
- `user:1001`, `user:1002`, `order:5001`은 서로 다른 해시 슬롯에 배치됨
- 각 키가 다른 노드에 있을 수 있어 ACID 보장 불가

**해결책**:
```python
# ✅ 방법 1: 해시 태그로 같은 슬롯에 배치
pipe = rc.pipeline()
pipe.set('user:{group1}:1001', 'Alice')
pipe.set('user:{group1}:1002', 'Bob')
pipe.set('order:{group1}:5001', 'Product A')
pipe.execute()  # 성공! 모두 같은 슬롯

# ✅ 방법 2: 각 키마다 개별 처리
rc.set('user:1001', 'Alice')
rc.set('user:1002', 'Bob')
rc.set('order:5001', 'Product A')

# ✅ 방법 3: Lua 스크립트 사용 (같은 슬롯 내)
script = """
redis.call('SET', KEYS[1], ARGV[1])
redis.call('SET', KEYS[2], ARGV[2])
return 'OK'
"""
rc.eval(script, 2,
        'user:{session-100}:name',
        'user:{session-100}:email',
        'Alice',
        'alice@example.com')
```

**배운 점**:
- 클러스터에서는 단일 슬롯 내에서만 트랜잭션 가능
- 관련 데이터는 해시 태그 `{tag}`로 묶어서 저장
- 설계 단계부터 클러스터 제약사항 고려 필요

---

### 시나리오 3: 장애 복구 중 데이터 손실

**상황**: 마스터 노드 장애 후 자동 페일오버 되었으나 일부 데이터가 사라짐

```bash
# 상황 재현
# 1. 마스터에 데이터 쓰기
redis-cli -p 7000 SET important:data "critical-value"
# OK

# 2. 즉시 마스터 노드 7000이 장애 발생 (강제 종료)
# 3. 슬레이브 7003이 마스터로 승격 (자동 페일오버)
# 4. 데이터 확인
redis-cli -p 7003 GET important:data
# (nil)  ← 데이터 사라짐!
```

**문제점**:
- Redis는 기본적으로 비동기 복제 사용
- 마스터가 쓰기를 받은 후 슬레이브 복제 전에 장애 발생
- 복제되지 않은 데이터는 페일오버 후 손실됨

**해결책**:
```bash
# ✅ 방법 1: WAIT 명령으로 동기 복제 보장
# 최소 1개 슬레이브에 복제 완료 대기 (최대 1000ms)
redis-cli -p 7000 SET critical:data "value"
redis-cli -p 7000 WAIT 1 1000
# 반환: 1 (1개 슬레이브에 복제 완료)

# ✅ 방법 2: 설정으로 최소 슬레이브 요구
# redis.conf
min-replicas-to-write 1
min-replicas-max-lag 10

# 슬레이브가 1개 미만이거나 10초 이상 지연 시 쓰기 거부
```

```python
# ✅ 방법 3: 애플리케이션에서 확인
from redis.cluster import RedisCluster

rc = RedisCluster(host='127.0.0.1', port=7000)

# 중요 데이터 쓰기
rc.set('critical:payment:1001', payment_data)

# 최소 1개 복제본에 복제 대기
replicas_synced = rc.wait(numreplicas=1, timeout=1000)

if replicas_synced < 1:
    # 복제 실패 처리
    logger.error("Data not replicated to slaves")
    raise Exception("Replication failed")
```

**배운 점**:
- Redis 복제는 기본적으로 비동기 (성능 우선)
- 중요 데이터는 `WAIT` 명령으로 동기 복제 보장
- 성능과 일관성의 트레이드오프 이해 필요
- 100% 데이터 손실 방지는 불가능 (CAP 정리)

---

### 시나리오 4: 클러스터 리샤딩 중 서비스 장애

**상황**: 운영 중 클러스터에 노드를 추가하고 슬롯을 재분배하던 중 일부 요청 실패

```bash
# 주니어 개발자의 작업
# 1. 새 노드 추가
redis-cli --cluster add-node 127.0.0.1:7006 127.0.0.1:7000

# 2. 리샤딩 시작 (운영 중!)
redis-cli --cluster reshard 127.0.0.1:7000
# 4096 슬롯 이동

# 문제: 리샤딩 중 일부 키 접근 실패
# Error: MOVED 3999 127.0.0.1:7006
# Error: ASK 4000 127.0.0.1:7006
```

**문제점**:
- 리샤딩 중 클라이언트가 리디렉션을 제대로 처리하지 못함
- 슬롯 이동 중인 키에 대한 요청이 실패
- 클라이언트가 클러스터 모드를 지원하지 않음

**해결책**:
```bash
# ✅ 방법 1: 점진적 리샤딩 (슬롯 수 최소화)
# 한 번에 4096개가 아닌 512개씩 여러 번 이동
redis-cli --cluster reshard 127.0.0.1:7000 \
  --cluster-from [source-node-id] \
  --cluster-to [target-node-id] \
  --cluster-slots 512 \
  --cluster-yes

# 5분 대기 후 다음 512개 이동
sleep 300
redis-cli --cluster reshard ... --cluster-slots 512

# ✅ 방법 2: 리샤딩 시간대 선택
# 새벽 시간 등 트래픽이 적은 시간대 선택
0 3 * * * /path/to/reshard-script.sh  # 매일 새벽 3시
```

```python
# ✅ 방법 3: 클라이언트에서 MOVED/ASK 처리
from redis.cluster import RedisCluster
from redis.exceptions import RedisClusterException

rc = RedisCluster(
    host='127.0.0.1',
    port=7000,
    decode_responses=True,
    skip_full_coverage_check=False,  # 전체 슬롯 커버리지 체크
    max_connections_per_node=50
)

# 자동으로 MOVED/ASK 리디렉션 처리
try:
    value = rc.get('mykey')
except RedisClusterException as e:
    logger.error(f"Cluster error: {e}")
    # 재시도 로직
```

**배운 점**:
- 리샤딩은 운영에 영향을 줄 수 있음
- 점진적 리샤딩으로 위험 최소화
- 클라이언트는 반드시 클러스터 모드 지원 라이브러리 사용
- 리샤딩 전 충분한 테스트와 모니터링 준비

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용 (5-7개)

<details>
<summary><strong>1. Redis Cluster와 Redis Sentinel의 차이는 무엇인가요?</strong></summary>

**모범 답안 포인트**
- **Redis Sentinel**: 단일 마스터-슬레이브 구조의 고가용성 솔루션
- **Redis Cluster**: 데이터 샤딩 + 고가용성을 모두 제공하는 분산 시스템
- Sentinel은 스케일 아웃 불가, Cluster는 수평 확장 가능

**예시 답변**
> "Redis Sentinel은 하나의 마스터와 여러 슬레이브로 구성된 단순한 고가용성 솔루션입니다. 마스터 장애 시 Sentinel이 감지하고 슬레이브를 마스터로 승격시킵니다. 반면 Redis Cluster는 여러 마스터 노드가 데이터를 나눠 저장하는 샤딩 기능까지 제공합니다. 16384개의 해시 슬롯을 여러 마스터에 분산하여 수평 확장이 가능합니다."

**꼬리 질문**
- Q: 언제 Sentinel을 쓰고 언제 Cluster를 쓰나요?
- A: 데이터가 단일 서버 메모리에 들어가고 단순한 고가용성만 필요하면 Sentinel, 데이터가 크거나 높은 처리량이 필요하면 Cluster를 사용합니다.

**실무 연관**
- 중소 서비스: Sentinel로 시작 (관리 간단)
- 대규모 서비스: Cluster로 확장 (수평 확장 필요)

</details>

<details>
<summary><strong>2. Redis Cluster의 해시 슬롯(Hash Slot)이란 무엇인가요?</strong></summary>

**모범 답안 포인트**
- 16384개의 슬롯으로 데이터 분산
- CRC16(key) % 16384 공식으로 슬롯 계산
- 각 마스터 노드가 일정 범위의 슬롯 담당

**예시 답변**
> "Redis Cluster는 0부터 16383까지 총 16384개의 가상 슬롯을 사용합니다. 키가 들어오면 CRC16 해시 함수로 계산해서 어느 슬롯에 속하는지 결정합니다. 예를 들어 3개의 마스터가 있으면 첫 번째 마스터가 0-5460, 두 번째가 5461-10922, 세 번째가 10923-16383 슬롯을 담당하는 식으로 분배됩니다."

**꼬리 질문**
- Q: 왜 16384개인가요?
- A: 2^14 = 16384로 적당한 크기이며, 클러스터 메타데이터를 효율적으로 관리할 수 있는 크기입니다. (비트맵으로 2KB)

**실무 연관**
- 노드 추가/제거 시 슬롯 재분배로 데이터 마이그레이션
- 슬롯 범위 확인으로 데이터 위치 파악 가능

</details>

<details>
<summary><strong>3. 해시 태그(Hash Tag)는 무엇이며 왜 사용하나요?</strong></summary>

**모범 답안 포인트**
- `{tag}` 형식으로 키의 일부만 해싱에 사용
- 관련 데이터를 같은 슬롯(노드)에 배치
- MULTI/EXEC 트랜잭션 가능하게 함

**예시 답변**
> "해시 태그는 중괄호 {}로 키의 특정 부분을 지정하여 해시 계산에 사용하는 기능입니다. 예를 들어 `user:{1001}:profile`과 `user:{1001}:settings`는 모두 `1001` 부분만 해싱되어 같은 슬롯에 저장됩니다. 이렇게 하면 한 사용자의 여러 데이터가 같은 노드에 있어서 트랜잭션이나 Lua 스크립트를 사용할 수 있습니다."

**꼬리 질문**
- Q: 해시 태그의 단점은 무엇인가요?
- A: 데이터가 특정 노드에 몰릴 수 있어 불균형한 분산이 발생할 수 있습니다. (핫스팟 문제)

**실무 연관**
- 사용자별 세션 데이터: `session:{user-id}:*`
- 주문 관련 데이터: `order:{order-id}:*`

</details>

<details>
<summary><strong>4. Redis Cluster에서 MOVED와 ASK 에러의 차이는?</strong></summary>

**모범 답안 포인트**
- **MOVED**: 슬롯이 완전히 다른 노드로 이동 완료
- **ASK**: 슬롯 마이그레이션 진행 중 (일시적)
- 클라이언트는 리디렉션 따라 재요청

**예시 답변**
> "MOVED 에러는 해당 슬롯이 완전히 다른 노드로 이동했을 때 발생합니다. 클라이언트는 새 노드 정보를 캐시하고 이후 요청은 새 노드로 보냅니다. ASK 에러는 리샤딩 중 슬롯이 이동하는 과정에서 발생하며, 클라이언트는 일시적으로만 새 노드에 요청하고 캐시는 업데이트하지 않습니다."

**꼬리 질문**
- Q: 클라이언트는 어떻게 처리하나요?
- A: MOVED는 클러스터 토폴로지 캐시 업데이트, ASK는 ASKING 명령 후 재시도만 수행

**실무 연관**
- 클러스터 모드 클라이언트 라이브러리가 자동 처리
- 리샤딩 중 ASK 에러 로그 증가는 정상

</details>

<details>
<summary><strong>5. Redis Cluster에서 페일오버는 어떻게 동작하나요?</strong></summary>

**모범 답안 포인트**
- 마스터 장애 감지 (노드 간 gossip 프로토콜)
- 과반수 노드가 장애 합의
- 슬레이브가 마스터로 자동 승격
- 클라이언트는 새 마스터로 리디렉션

**예시 답변**
> "Redis Cluster의 각 노드는 gossip 프로토콜로 서로 상태를 주고받습니다. 마스터 노드가 일정 시간 응답하지 않으면 다른 노드들이 PFAIL(Possible Fail)로 표시하고, 과반수 이상의 노드가 동의하면 FAIL 상태로 전환합니다. 그러면 해당 마스터의 슬레이브 중 하나가 자동으로 마스터로 승격되어 서비스를 계속합니다."

**꼬리 질문**
- Q: 슬레이브가 없는 마스터가 죽으면?
- A: 해당 슬롯의 데이터는 사용 불가능해지고 클러스터는 degraded 상태가 됩니다.

**실무 연관**
- 모든 마스터는 최소 1개 이상의 슬레이브 필요
- `cluster-node-timeout` 설정으로 페일오버 속도 조절

</details>

<details>
<summary><strong>6. 클러스터에서 MULTI/EXEC 트랜잭션을 사용할 수 없는 이유는?</strong></summary>

**모범 답안 포인트**
- 여러 키가 서로 다른 노드에 있을 수 있음
- 분산 트랜잭션은 성능과 복잡도 문제
- 같은 슬롯 내에서만 트랜잭션 가능

**예시 답변**
> "Redis Cluster는 데이터를 여러 노드에 분산하기 때문에 여러 키에 대한 트랜잭션은 지원하지 않습니다. `user:1001`과 `user:1002`는 서로 다른 노드에 있을 수 있어서 MULTI/EXEC로 묶을 수 없습니다. 대신 해시 태그를 사용해 같은 슬롯에 키를 배치하거나, Lua 스크립트를 사용해야 합니다."

**꼬리 질문**
- Q: Lua 스크립트는 왜 가능한가요?
- A: Lua 스크립트는 단일 슬롯의 키들만 접근하도록 제한되며, 해당 노드에서 원자적으로 실행되기 때문입니다.

**실무 연관**
- 설계 단계부터 트랜잭션 필요 데이터는 해시 태그로 그룹화
- 완전한 ACID가 필요하면 PostgreSQL 등 RDBMS 사용

</details>

<details>
<summary><strong>7. 클러스터에 노드를 추가할 때 리샤딩이 필요한 이유는?</strong></summary>

**모범 답안 포인트**
- 새 노드는 초기에 슬롯 없음 (빈 마스터)
- 기존 노드에서 슬롯을 이동해야 부하 분산
- 슬롯 이동 = 데이터 마이그레이션

**예시 답변**
> "새로운 마스터 노드를 클러스터에 추가하면 초기에는 해시 슬롯이 할당되지 않은 빈 상태입니다. 클러스터가 정상 작동하려면 16384개 슬롯이 모두 할당되어야 하므로, 기존 마스터들에서 일부 슬롯을 새 노드로 이동하는 리샤딩이 필요합니다. 리샤딩 과정에서 해당 슬롯의 키들이 실제로 복사됩니다."

**꼬리 질문**
- Q: 리샤딩 중에도 서비스가 가능한가요?
- A: 네, Redis는 슬롯 마이그레이션 중에도 서비스를 계속하며 ASK 리디렉션으로 처리합니다.

**실무 연관**
- 부하 증가 시 노드 추가 + 리샤딩으로 확장
- 트래픽 적은 시간대에 리샤딩 수행 권장

</details>

---

### 📗 중급 개발자용 (3-5개)

<details>
<summary><strong>1. Redis Cluster의 gossip 프로토콜 동작 원리를 설명하세요.</strong></summary>

**모범 답안 포인트**
- 각 노드가 주기적으로 PING/PONG 메시지 교환
- 노드 상태, 슬롯 매핑 정보 전파
- 장애 감지 및 투표 메커니즘
- 네트워크 대역폭 vs 감지 속도 트레이드오프

**예시 답변**
> "Redis Cluster의 각 노드는 1초마다 랜덤하게 선택된 몇 개 노드에 PING 메시지를 보내고 PONG으로 응답받습니다. 이 메시지에는 자신의 상태, 슬롯 매핑, 다른 노드들의 상태 정보가 포함됩니다. 노드가 `cluster-node-timeout` 시간 동안 응답하지 않으면 PFAIL로 표시하고, 과반수 노드가 동의하면 FAIL로 전환하여 페일오버를 시작합니다."

**실무 예시**
```bash
# cluster-node-timeout 설정
cluster-node-timeout 15000  # 15초

# 최소 과반수 노드 필요 (3마스터 환경)
# PFAIL: 1개 노드가 감지
# FAIL: 2개 이상(과반) 노드가 동의
```

**꼬리 질문**
- Q: gossip 프로토콜의 단점은?
- A: 노드 수가 많아지면 네트워크 대역폭 사용 증가, 정보 전파 지연 발생 가능

**실무 연관**
- 대규모 클러스터(100+ 노드)에서는 gossip 오버헤드 고려
- `cluster-node-timeout` 값은 네트워크 안정성과 페일오버 속도 균형

</details>

<details>
<summary><strong>2. 클러스터 리샤딩 중 데이터 일관성은 어떻게 보장되나요?</strong></summary>

**모범 답안 포인트**
- 슬롯 마이그레이션은 점진적 진행
- MIGRATING/IMPORTING 상태로 슬롯 표시
- 기존 키는 source에서, 새 키는 target에서 처리
- ASK 리디렉션으로 클라이언트 안내

**예시 답변**
> "리샤딩 시작 시 source 노드는 슬롯을 MIGRATING 상태로, target 노드는 IMPORTING 상태로 표시합니다. 키는 하나씩 source에서 target으로 복사되며, 이미 이동한 키는 source에서 삭제됩니다. 마이그레이션 중 클라이언트가 이동 중인 키를 요청하면 ASK 리디렉션으로 target 노드를 안내합니다. 모든 키 이동 완료 후 슬롯 소유권이 공식적으로 변경됩니다."

**실무 예시**
```bash
# 리샤딩 단계
1. CLUSTER SETSLOT <slot> MIGRATING <target-node>  # source
2. CLUSTER SETSLOT <slot> IMPORTING <source-node>  # target
3. CLUSTER GETKEYSINSLOT <slot> <count>             # 키 목록 조회
4. MIGRATE <target> <key>                           # 키 이동 (원자적)
5. CLUSTER SETSLOT <slot> NODE <target-node>        # 완료
```

**꼬리 질문**
- Q: 리샤딩 중 장애가 발생하면?
- A: 각 단계가 원자적이므로 재시작 가능, 일부 키는 중복 복사될 수 있지만 최종 일관성 보장

**실무 연관**
- 대용량 슬롯 이동 시 `--cluster-pipeline` 옵션으로 성능 향상
- 모니터링으로 리샤딩 진행률 추적

</details>

<details>
<summary><strong>3. Redis Cluster에서 네트워크 파티션 발생 시 어떻게 동작하나요?</strong></summary>

**모범 답안 포인트**
- Split-brain 방지 메커니즘
- 과반수 노드가 있는 파티션만 서비스 계속
- 소수 파티션은 읽기/쓰기 중단
- 네트워크 복구 후 자동 병합

**예시 답변**
> "네트워크 파티션으로 클러스터가 분리되면, 과반수(majority)의 마스터 노드가 있는 파티션만 계속 서비스합니다. 소수 파티션의 노드들은 `cluster-node-timeout` 후 다른 마스터들과 통신할 수 없음을 감지하고 FAIL 상태로 전환되어 클라이언트 요청을 거부합니다. 이는 CAP 정리의 Consistency와 Partition tolerance를 선택한 것입니다."

**실무 예시**
```
초기 클러스터: 마스터 A, B, C (3노드)

네트워크 파티션 발생:
파티션 1: A, B (과반수 2/3)
파티션 2: C (소수 1/3)

동작:
- 파티션 1 (A, B): 정상 서비스 계속
- 파티션 2 (C): CLUSTERDOWN 상태, 요청 거부

네트워크 복구:
- C가 A, B와 재연결
- 슬롯 정보 동기화
- 정상 상태 복구
```

**꼬리 질문**
- Q: 정확히 50:50 분리되면?
- A: 양쪽 모두 과반수가 아니므로 모두 서비스 중단, 수동 개입 필요

**실무 연관**
- 최소 3개 마스터로 과반수 확보
- 지리적 분산 시 과반수 노드를 같은 DC에 배치 고려
- `cluster-require-full-coverage no` 설정으로 부분 서비스 가능

</details>

<details>
<summary><strong>4. 클러스터 확장 시 다운타임 없이 진행하는 방법은?</strong></summary>

**모범 답안 포인트**
- 온라인 리샤딩 지원
- 점진적 슬롯 이동
- 클라이언트 리디렉션 자동 처리
- 모니터링과 롤백 계획

**예시 답변**
> "Redis Cluster는 온라인 리샤딩을 지원하여 다운타임 없이 확장 가능합니다. 새 노드를 추가하고 기존 마스터들에서 슬롯을 점진적으로 이동합니다. 각 슬롯의 키들은 하나씩 복사되며 클라이언트는 ASK 리디렉션으로 투명하게 처리됩니다. 트래픽이 적은 시간대에 소량씩 이동하고, 각 단계마다 성능 영향을 모니터링합니다."

**실무 예시**
```bash
# 단계별 확장 절차
1. 새 마스터 + 슬레이브 노드 추가
redis-cli --cluster add-node 192.168.1.10:7006 192.168.1.10:7000

2. 소량 슬롯 이동 (512개씩)
redis-cli --cluster reshard 192.168.1.10:7000 \
  --cluster-slots 512 \
  --cluster-from [source-id] \
  --cluster-to [new-node-id] \
  --cluster-yes

3. 성능 모니터링 (5-10분)
redis-cli -p 7000 INFO stats | grep ops_per_sec
watch -n 1 'redis-cli -p 7000 CLUSTER INFO'

4. 문제 없으면 다음 512개 이동
5. 모든 슬롯 이동 완료 시까지 반복

6. 슬레이브 추가
redis-cli --cluster add-node 192.168.1.10:7007 192.168.1.10:7000 \
  --cluster-slave \
  --cluster-master-id [7006-node-id]
```

**꼬리 질문**
- Q: 리샤딩 중 롤백이 필요하면?
- A: 이동한 슬롯을 역방향으로 다시 이동, 각 단계가 원자적이므로 안전

**실무 연관**
- 자동화 스크립트로 점진적 리샤딩
- Prometheus + Grafana로 실시간 모니터링
- 카나리 배포처럼 소량 테스트 후 확대

</details>

<details>
<summary><strong>5. 대규모 클러스터(100+ 노드) 운영 시 주의사항은?</strong></summary>

**모범 답안 포인트**
- Gossip 프로토콜 오버헤드 증가
- 네트워크 대역폭 사용량
- 페일오버 감지 지연
- 관리 복잡도

**예시 답변**
> "100개 이상의 노드에서는 gossip 프로토콜의 네트워크 오버헤드가 상당해집니다. 각 노드가 초당 여러 번 다른 노드들과 통신하므로 대역폭 사용이 증가하고 상태 전파에 지연이 발생할 수 있습니다. 또한 과반수 합의 과정이 느려져 페일오버 시간이 길어질 수 있습니다. 따라서 실무에서는 20-30개 노드 내로 유지하거나, 여러 개의 독립적인 클러스터로 분리하는 것을 권장합니다."

**실무 예시**
```bash
# 대규모 클러스터 최적화 설정
cluster-node-timeout 30000          # 30초로 증가 (기본 15초)
cluster-migration-barrier 2         # 최소 2개 슬레이브 유지
cluster-require-full-coverage no    # 부분 장애 시에도 서비스 계속

# 네트워크 최적화
tcp-backlog 511
tcp-keepalive 300

# 모니터링 강화
slowlog-log-slower-than 5000        # 5ms 이상 슬로우 쿼리
slowlog-max-len 1000
```

**대안 아키텍처**:
```
단일 100노드 클러스터 (비권장)
→ 4개의 25노드 클러스터로 분리

애플리케이션 레벨에서 샤딩:
- 지역별 클러스터 (서울, 부산, 대구)
- 서비스별 클러스터 (user, order, product)
- 일관된 해싱으로 클러스터 선택
```

**꼬리 질문**
- Q: Redis Enterprise는 어떻게 다른가요?
- A: Active-Active 지리적 복제, 더 큰 클러스터 지원, CRDT 기반 충돌 해결 등 엔터프라이즈 기능 제공

**실무 연관**
- 클러스터 크기는 비즈니스 요구사항과 운영 복잡도 균형
- 초기에는 작게 시작, 필요시 점진적 확장
- 멀티 클러스터 전략 고려

</details>

---

## ❓ FAQ

<details>
<summary><strong>Q1: Redis Cluster를 사용하면 항상 단일 인스턴스보다 빠른가요?</strong></summary>

**A**: 아니요, 상황에 따라 다릅니다.

**상세 설명**:
- **클러스터가 더 빠른 경우**:
  - 데이터가 매우 크고 단일 인스턴스 메모리 초과
  - 높은 QPS로 단일 인스턴스 CPU 포화
  - 읽기 부하를 여러 슬레이브에 분산

- **단일 인스턴스가 더 빠른 경우**:
  - 작은 데이터셋 (수 GB 이하)
  - MULTI/EXEC 트랜잭션 빈번 사용
  - Lua 스크립트로 여러 키 접근
  - 네트워크 리디렉션 오버헤드

**예시**:
```bash
# 단일 인스턴스: 100,000 QPS
redis-benchmark -p 6379 -t GET -n 100000
# 평균 응답: 0.5ms

# 클러스터 (3마스터): 80,000 QPS (리디렉션 오버헤드)
redis-benchmark -p 7000 -c 50 -t GET -n 100000 --cluster
# 평균 응답: 0.8ms

# 하지만 수평 확장으로 총 처리량 증가
# 3마스터 × 80,000 = 240,000 QPS
```

**실무 팁**:
- 성능보다 확장성과 고가용성이 목적이면 클러스터
- 단순 캐싱 용도는 단일 인스턴스 + Sentinel로 충분
- 벤치마크로 실제 워크로드 테스트 필수

</details>

<details>
<summary><strong>Q2: 클러스터에서 모든 키를 스캔하려면 어떻게 해야 하나요?</strong></summary>

**A**: 각 마스터 노드마다 개별적으로 SCAN 명령을 실행해야 합니다.

**상세 설명**:
- 클러스터는 데이터가 여러 노드에 분산되어 있음
- `KEYS *`나 `SCAN` 명령은 연결된 노드의 데이터만 조회
- 모든 데이터를 보려면 전체 마스터 노드 순회 필요

**예시**:
```python
from redis.cluster import RedisCluster

rc = RedisCluster(host='127.0.0.1', port=7000, decode_responses=True)

def scan_entire_cluster(pattern='*'):
    """클러스터 전체 키 스캔"""
    all_keys = []

    # 모든 마스터 노드에서 스캔
    for node in rc.get_nodes():
        if node['server_type'] == 'master':
            node_conn = rc.get_redis_connection(node)

            cursor = 0
            while True:
                cursor, keys = node_conn.scan(cursor, match=pattern, count=100)
                all_keys.extend(keys)

                if cursor == 0:
                    break

    return all_keys

# 사용 예시
user_keys = scan_entire_cluster('user:*')
print(f"총 {len(user_keys)}개 사용자 키 발견")
```

**실무 팁**:
- 프로덕션에서는 `SCAN` 사용 (KEYS는 블로킹)
- 각 노드마다 `COUNT` 값 조절하여 부하 관리
- 가능하면 키 패턴을 미리 알고 특정 노드만 조회

</details>

<details>
<summary><strong>Q3: 클러스터 리샤딩 중 데이터 손실 가능성이 있나요?</strong></summary>

**A**: 정상적인 리샤딩에서는 데이터 손실이 없지만, 예외 상황이 있습니다.

**상세 설명**:
- **정상 케이스**: 데이터 손실 없음
  - 키를 source에서 target으로 복사
  - 복사 확인 후 source에서 삭제
  - 각 단계가 원자적으로 실행

- **데이터 손실 가능 케이스**:
  - 리샤딩 중 source/target 노드 동시 장애
  - 네트워크 파티션으로 슬롯 소유권 불명확
  - TTL이 있는 키가 이동 중 만료

**예시**:
```bash
# 리샤딩 중 장애 시나리오
1. 슬롯 1000 마이그레이션 시작
2. 키 100개 중 50개 복사 완료
3. Source 노드 갑자기 다운
   → 나머지 50개 키는 어디에?

# Redis 동작:
- 복사 완료된 50개: Target 노드에 있음 (안전)
- 복사 전 50개: Source 노드 복구 필요
- Source 노드 복구 불가 시 → 손실

# 방지책:
- 모든 마스터에 슬레이브 유지
- 리샤딩 전 전체 백업
- 리샤딩 중 모니터링 강화
```

**실무 팁**:
- 리샤딩 전 `BGSAVE`로 백업
- 점진적 리샤딩으로 리스크 최소화
- 중요 데이터는 AOF 활성화 (appendonly yes)

</details>

<details>
<summary><strong>Q4: Pub/Sub는 클러스터 환경에서 어떻게 동작하나요?</strong></summary>

**A**: Redis Cluster의 Pub/Sub은 클러스터 전체로 브로드캐스트됩니다.

**상세 설명**:
- 일반 키와 달리 Pub/Sub 메시지는 샤딩되지 않음
- 한 노드에 PUBLISH하면 모든 노드로 전파
- 모든 노드의 구독자가 메시지 수신
- 네트워크 대역폭 사용 증가

**예시**:
```python
from redis.cluster import RedisCluster

rc = RedisCluster(host='127.0.0.1', port=7000)

# 구독자 (어느 노드에 연결해도 상관없음)
pubsub = rc.pubsub()
pubsub.subscribe('notifications')

for message in pubsub.listen():
    if message['type'] == 'message':
        print(f"수신: {message['data']}")

# 발행자 (다른 프로세스, 다른 노드)
rc.publish('notifications', 'Hello Cluster!')
# → 모든 노드의 모든 구독자에게 전달
```

**주의사항**:
```bash
# 대규모 클러스터에서 Pub/Sub 오버헤드
10개 노드 클러스터:
- 1개 노드에 PUBLISH
- 9개 노드로 메시지 전파
- 네트워크 트래픽 9배 증가

# 대안: 샤딩된 Pub/Sub (Redis 7.0+)
SPUBLISH sharded-channel "message"  # 같은 슬롯의 노드만
SSUBSCRIBE sharded-channel
```

**실무 팁**:
- 대용량 메시지는 Kafka, RabbitMQ 같은 전용 메시지 브로커 고려
- Redis 7.0+ 샤딩된 Pub/Sub 사용 검토
- Pub/Sub 사용량 모니터링

</details>

<details>
<summary><strong>Q5: 클러스터에서 Lua 스크립트를 사용할 때 제약사항은?</strong></summary>

**A**: 모든 키가 같은 해시 슬롯에 있어야 합니다.

**상세 설명**:
- Lua 스크립트는 단일 노드에서 원자적으로 실행
- 여러 노드에 걸친 스크립트 실행 불가
- `KEYS`와 `ARGV`의 모든 키가 같은 슬롯 필요

**예시**:
```lua
-- ❌ 잘못된 예: 다른 슬롯의 키들
local script = [[
  redis.call('SET', 'user:1001', ARGV[1])
  redis.call('SET', 'user:1002', ARGV[2])
  return 'OK'
]]
-- Error: Script attempted to access keys in different slots

-- ✅ 올바른 예: 해시 태그로 같은 슬롯
local script = [[
  redis.call('SET', 'user:{group1}:1001', ARGV[1])
  redis.call('SET', 'user:{group1}:1002', ARGV[2])
  return 'OK'
]]
rc.eval(script, 2, 'user:{group1}:1001', 'user:{group1}:1002', 'Alice', 'Bob')
```

**실전 활용**:
```lua
-- 사용자 세션 관리 스크립트
local update_session = [[
  local session_key = KEYS[1]
  local last_active_key = KEYS[2]

  -- 세션 데이터 업데이트
  redis.call('HSET', session_key, 'last_active', ARGV[1])
  redis.call('EXPIRE', session_key, 1800)

  -- 활성 사용자 목록 업데이트
  redis.call('ZADD', last_active_key, ARGV[1], ARGV[2])

  return redis.call('HGETALL', session_key)
]]

# 같은 슬롯에 배치
rc.eval(update_session, 2,
        'session:{user-1001}:data',
        'session:{user-1001}:active',
        current_timestamp,
        'user-1001')
```

**실무 팁**:
- 설계 단계부터 Lua 스크립트 필요 여부 고려
- 관련 키는 해시 태그로 그룹화
- 스크립트 내에서 `redis.log()`로 디버깅

</details>

<details>
<summary><strong>Q6: 클러스터 노드 제거 시 주의사항은?</strong></summary>

**A**: 슬롯을 모두 이동한 후 노드를 제거해야 합니다.

**상세 설명**:
- 슬롯이 있는 노드는 즉시 제거 불가
- 먼저 다른 노드로 슬롯 이동 (리샤딩)
- 슬롯이 없는 빈 노드만 제거 가능
- 슬레이브는 바로 제거 가능

**예시**:
```bash
# ❌ 잘못된 순서
redis-cli --cluster del-node 127.0.0.1:7000 [node-id]
# Error: Node 127.0.0.1:7000 is not empty! Reshard first.

# ✅ 올바른 순서
# 1. 제거할 노드의 슬롯 확인
redis-cli -p 7000 cluster nodes | grep [node-id]
# 출력: ... 0-5460 5461-10922 ...

# 2. 모든 슬롯을 다른 노드로 이동
redis-cli --cluster reshard 127.0.0.1:7000 \
  --cluster-from [removing-node-id] \
  --cluster-to [target-node-id] \
  --cluster-slots 5461 \
  --cluster-yes

# 3. 슬롯이 0개인지 확인
redis-cli -p 7000 cluster nodes | grep [node-id]
# 출력: ... (슬롯 범위 없음)

# 4. 노드 제거
redis-cli --cluster del-node 127.0.0.1:7000 [node-id]

# 5. 슬레이브도 제거
redis-cli --cluster del-node 127.0.0.1:7000 [slave-node-id]
```

**자동화 스크립트**:
```bash
#!/bin/bash
# safe_remove_node.sh

NODE_TO_REMOVE=$1
CLUSTER_HOST="127.0.0.1:7000"

# 노드 정보 가져오기
NODE_ID=$(redis-cli --cluster call $CLUSTER_HOST cluster nodes | \
          grep $NODE_TO_REMOVE | awk '{print $1}')

# 슬롯 개수 확인
SLOT_COUNT=$(redis-cli -p 7000 cluster nodes | \
             grep $NODE_ID | grep -o '[0-9]\+-[0-9]\+' | wc -l)

if [ $SLOT_COUNT -gt 0 ]; then
    echo "슬롯이 있는 노드입니다. 리샤딩을 먼저 진행합니다..."

    # 타겟 노드 선택 (첫 번째 다른 마스터)
    TARGET_ID=$(redis-cli -p 7000 cluster nodes | \
                grep master | grep -v $NODE_ID | head -1 | awk '{print $1}')

    # 리샤딩
    redis-cli --cluster reshard $CLUSTER_HOST \
      --cluster-from $NODE_ID \
      --cluster-to $TARGET_ID \
      --cluster-slots $SLOT_COUNT \
      --cluster-yes
fi

# 노드 제거
echo "노드 제거 중..."
redis-cli --cluster del-node $CLUSTER_HOST $NODE_ID

echo "노드 제거 완료"
```

**실무 팁**:
- 제거 전 해당 노드의 슬레이브도 확인
- 리샤딩 중 성능 모니터링
- 롤백 계획 수립 (백업, 리샤딩 역전환)

</details>

<details>
<summary><strong>Q7: 클러스터와 Sentinel을 동시에 사용할 수 있나요?</strong></summary>

**A**: 아니요, Redis Cluster와 Sentinel은 함께 사용하지 않습니다.

**상세 설명**:
- Redis Cluster는 자체적으로 고가용성 기능 내장
- Sentinel은 단일 마스터-슬레이브 구조를 위한 도구
- 클러스터는 자체 gossip 프로토콜로 장애 감지 및 페일오버 수행
- 두 시스템의 목적과 아키텍처가 근본적으로 다름

**비교**:
```
┌─────────────────────────────────────────────────────┐
│         Redis Sentinel 아키텍처                     │
├─────────────────────────────────────────────────────┤
│  Sentinel1   Sentinel2   Sentinel3                  │
│     ↓           ↓           ↓                       │
│  ┌──────────────────────────┐                       │
│  │  Master (단일)           │                       │
│  └──────────┬───────────────┘                       │
│             │                                       │
│    ┌────────┴────────┐                             │
│  Slave1          Slave2                             │
│                                                     │
│  - 샤딩 없음 (모든 데이터 복제)                      │
│  - Sentinel이 외부에서 모니터링                      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│         Redis Cluster 아키텍처                      │
├─────────────────────────────────────────────────────┤
│  Master1  Master2  Master3                          │
│  (슬롯    (슬롯    (슬롯                            │
│   0-      5461-    10923-                           │
│   5460)   10922)   16383)                           │
│     │        │        │                             │
│  Slave1   Slave2   Slave3                           │
│                                                     │
│  - 자동 샤딩                                        │
│  - 내장 고가용성 (gossip)                           │
│  - 외부 모니터링 불필요                             │
└─────────────────────────────────────────────────────┘
```

**선택 가이드**:
```
Q: 어떤 것을 선택해야 하나요?

┌─────────────────────────────────────────┐
│  Redis Sentinel 선택 조건                │
├─────────────────────────────────────────┤
│ ✓ 데이터가 단일 서버 메모리에 수용 가능   │
│ ✓ 단순한 마스터-슬레이브 구조로 충분      │
│ ✓ 관리 복잡도 최소화                     │
│ ✓ 기존 애플리케이션 변경 최소화           │
│                                         │
│ 예: 중소 규모 캐시, 세션 저장소          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Redis Cluster 선택 조건                 │
├─────────────────────────────────────────┤
│ ✓ 데이터가 수십 GB 이상                  │
│ ✓ 높은 처리량 필요 (100K+ QPS)           │
│ ✓ 수평 확장 가능성 중요                  │
│ ✓ 지리적 분산 필요                       │
│                                         │
│ 예: 대규모 전자상거래, 소셜 미디어        │
└─────────────────────────────────────────┘
```

**실무 팁**:
- 처음에는 Sentinel로 시작, 필요시 Cluster로 마이그레이션
- 마이그레이션 계획 수립 (해시 태그 적용 등)
- 두 시스템 모두 클라이언트 라이브러리 지원 확인

</details>

---

## 📝 핵심 정리

### 이 장에서 배운 핵심 개념

| 개념 | 설명 | 핵심 키워드 |
|------|------|-------------|
| Redis Cluster | 자동 샤딩 + 고가용성 분산 시스템 | 16384 슬롯, 마스터-슬레이브 |
| 해시 슬롯 | CRC16(key) % 16384로 데이터 분산 | 샤딩, 슬롯 할당 |
| 해시 태그 | `{tag}` 형식으로 관련 데이터 그룹화 | 트랜잭션, 동일 슬롯 |
| Gossip 프로토콜 | 노드 간 상태 정보 교환 메커니즘 | PING/PONG, 장애 감지 |
| 페일오버 | 마스터 장애 시 슬레이브 자동 승격 | PFAIL/FAIL, 과반수 투표 |
| 리샤딩 | 슬롯을 노드 간 이동하여 재분배 | MIGRATING/IMPORTING, ASK |
| MOVED/ASK | 클라이언트 리디렉션 메커니즘 | 슬롯 이동, 클러스터 확장 |

### 필수 명령어 정리

| 명령어 | 용도 | 예시 |
|--------|------|------|
| `CLUSTER NODES` | 클러스터 토폴로지 조회 | `redis-cli -p 7000 cluster nodes` |
| `CLUSTER INFO` | 클러스터 상태 확인 | `redis-cli -p 7000 cluster info` |
| `CLUSTER SLOTS` | 슬롯 매핑 정보 | `redis-cli -p 7000 cluster slots` |
| `CLUSTER KEYSLOT` | 키의 슬롯 번호 계산 | `redis-cli -p 7000 cluster keyslot user:1001` |
| `--cluster create` | 클러스터 초기화 | `redis-cli --cluster create 127.0.0.1:7000 ...` |
| `--cluster reshard` | 슬롯 재분배 | `redis-cli --cluster reshard 127.0.0.1:7000` |
| `--cluster check` | 클러스터 검증 | `redis-cli --cluster check 127.0.0.1:7000` |
| `WAIT` | 복제 완료 대기 | `redis-cli -p 7000 WAIT 1 1000` |

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] 최소 3개 마스터 노드로 클러스터 구성 (과반수 확보)
- [ ] 모든 마스터에 최소 1개 슬레이브 배치
- [ ] 관련 데이터는 해시 태그로 그룹화
- [ ] 클러스터 모드 지원 클라이언트 라이브러리 사용
- [ ] 리샤딩은 트래픽 적은 시간대에 점진적으로 수행
- [ ] `WAIT` 명령으로 중요 데이터 복제 보장
- [ ] 정기적인 백업 (BGSAVE + AOF)
- [ ] 모니터링 구축 (CPU, 메모리, 네트워크, 슬롯 분산)

#### ❌ 하지 말아야 할 것
- [ ] 슬롯 할당 없이 노드만 추가
- [ ] 다중 키 트랜잭션 (해시 태그 없이)
- [ ] 운영 중 대량 슬롯 리샤딩
- [ ] KEYS * 명령 사용 (SCAN 사용)
- [ ] 슬레이브 없는 마스터 운영
- [ ] 네트워크 파티션 가능성 무시
- [ ] 클러스터와 Sentinel 혼용
- [ ] 100+ 노드 단일 클러스터 구성

### 성능/보안 체크리스트

#### 성능
- [ ] `maxmemory-policy allkeys-lru` 설정
- [ ] `cluster-node-timeout` 적절히 조정 (15초 권장)
- [ ] 슬롯 분산 균형 모니터링
- [ ] 네트워크 지연시간 측정 (같은 DC 내 1ms 이하)
- [ ] Slow log 설정 및 주기적 확인
- [ ] 클라이언트 연결 풀 크기 최적화

#### 보안
- [ ] `requirepass`로 인증 설정
- [ ] `bind` 설정으로 내부 네트워크만 허용
- [ ] `protected-mode yes` 활성화
- [ ] TLS/SSL 암호화 통신 (Redis 6.0+)
- [ ] 위험 명령어 비활성화 (`rename-command`)
- [ ] 방화벽으로 클러스터 포트 보호 (기본 + 10000)
- [ ] 정기적인 보안 패치 적용

---

## 🎉 축하합니다!

**Redis 클러스터 및 분산 시스템 완전 가이드를 완료하셨습니다!**

**이제 여러분은**:
✅ Redis Cluster의 아키텍처와 동작 원리를 이해할 수 있습니다
✅ 해시 슬롯 시스템으로 데이터 분산 설계를 할 수 있습니다
✅ 클러스터를 구성하고 운영할 수 있습니다
✅ 리샤딩과 페일오버를 처리할 수 있습니다
✅ 대규모 분산 시스템을 모니터링하고 최적화할 수 있습니다
✅ 프로덕션 환경에서 클러스터를 안전하게 운영할 수 있습니다

**다음 단계**:
- [ ] 실습 환경에서 3노드 클러스터 직접 구성해보기
- [ ] 리샤딩 과정 직접 실행하며 MOVED/ASK 확인
- [ ] 장애 시나리오 테스트 (마스터 다운, 네트워크 파티션)
- [ ] 프로덕션 마이그레이션 계획 수립
- [ ] 면접 질문 복습 및 답변 준비

**추천 학습 경로**:
1. Redis 기본 편 복습 (1-6장)
2. Redis 고급 편 복습 (7-11장)
3. **Redis 클러스터 편 완료** (12장) ← 현재 위치
4. 실전 프로젝트 구현 (종합)
5. 성능 튜닝 및 트러블슈팅

---

**이전 장으로 돌아가기**: [← 11장: Redis 실전 프로젝트](11-Redis-실전-프로젝트.md)

**목차로 돌아가기**: [📚 Redis 완전 학습 가이드](README.md)


## 🔗 관련 기술

**이 기술과 함께 사용하는 기술들**

| 기술 | 관계 | 학습 우선순위 |
|------|------|---------------|
| Redis Sentinel | 단일 마스터 고가용성 대안 | ⭐⭐⭐ |
| Kubernetes | 클러스터 오케스트레이션 | ⭐⭐⭐⭐ |
| HAProxy/Nginx | 로드 밸런싱 | ⭐⭐⭐ |
| Prometheus | 모니터링 및 알림 | ⭐⭐⭐⭐ |
| Grafana | 시각화 대시보드 | ⭐⭐⭐ |
| Kafka | 대규모 메시징 (Pub/Sub 대안) | ⭐⭐⭐ |
| Consul/etcd | 서비스 디스커버리 | ⭐⭐ |

---

## 🚀 다음 단계

### 다음 장 미리보기: Redis 종합 프로젝트

이제 Redis 클러스터까지 마스터했다면, 실전에서 모든 지식을 통합하여 활용할 차례입니다!

**배울 내용**:
- **배울 내용 1**: 마이크로서비스 아키텍처에서 Redis 클러스터 활용
  - API Gateway 레이트 리미팅
  - 분산 세션 관리
  - 서비스 간 캐싱 전략

- **배울 내용 2**: 실시간 대규모 시스템 구축
  - 실시간 리더보드 (10억 사용자)
  - 실시간 분석 대시보드
  - 이벤트 기반 아키텍처

- **배울 내용 3**: 프로덕션 베스트 프랙티스
  - CI/CD 파이프라인에 Redis 통합
  - 무중단 배포 전략
  - 재해 복구(DR) 계획

- **실전 프로젝트**: 전자상거래 플랫폼 구축
  - 사용자: 100만 명 동시 접속
  - 상품: 1억 개 실시간 재고 관리
  - 주문: 초당 10,000건 처리
  - 아키텍처: Redis Cluster + Microservices + Kubernetes

### 이 장과의 연결점

```
12장: Redis Cluster 마스터
    ↓
다음 장: 실전 프로젝트 통합
    ↓
- 클러스터 설계 능력
- 샤딩 전략 수립
- 고가용성 구현
- 성능 최적화
    ↓
최종 목표: 프로덕션급 대규모 시스템 구축 능력
```

### 준비하면 좋을 것들

```bash
# 1. Docker Compose로 로컬 개발 환경 구축
git clone https://github.com/your-repo/redis-microservices-demo
cd redis-microservices-demo
docker-compose up -d

# 2. Kubernetes 학습 (선택사항)
# - Minikube 설치
# - Redis Operator 이해
# - StatefulSet 개념

# 3. 모니터링 도구 설치
# - Prometheus + Grafana
# - Redis Exporter 설정
# - 커스텀 대시보드 구성

# 4. 부하 테스트 도구
pip install locust redis-py-cluster
# Apache JMeter 또는 k6 설치
```

---

## 📚 추가 학습 자료

### 공식 문서
- [Redis Cluster 공식 튜토리얼](https://redis.io/docs/manual/scaling/)
- [Redis Cluster 사양](https://redis.io/docs/reference/cluster-spec/)
- [Redis 명령어 레퍼런스](https://redis.io/commands/)
- [Redis 클라이언트 라이브러리](https://redis.io/clients)

### 추천 블로그/아티클 (한글)
- [우아한 형제들 기술블로그 - Redis Cluster 도입기](https://techblog.woowahan.com/)
- [카카오 기술블로그 - 대규모 Redis 클러스터 운영](https://tech.kakao.com/)
- [NHN Cloud - Redis 장애 대응 사례](https://meetup.nhncloud.com/)
- [당근마켓 - Redis 성능 최적화 경험](https://medium.com/daangn)
- [LINE Engineering - Redis Cluster 마이그레이션](https://engineering.linecorp.com/ko/blog/)

### 추천 블로그/아티클 (영문)
- [Scaling Redis at Twitter](https://blog.twitter.com/)
- [How Instagram Scaled Redis](https://instagram-engineering.com/)
- [Redis at Slack - Architecture](https://slack.engineering/)
- [Stripe's Redis Infrastructure](https://stripe.com/blog)

### 영상 강의
- [Redis University - RU330: Redis Cluster](https://university.redis.com/)
- [인프런 - Redis 완벽 가이드](https://www.inflearn.com/)
- [YouTube - Redis 클러스터 구축 실습](https://www.youtube.com/)
- [Udemy - Redis Cluster in Production](https://www.udemy.com/)

### 컨퍼런스 발표
- [RedisConf 2024 - Cluster Best Practices](https://redis.com/redisconf/)
- [if(kakao)dev - Redis 대규모 트래픽 처리](https://if.kakao.com/)
- [DEVIEW - 네이버의 Redis 활용 사례](https://deview.kr/)
- [AWS re:Invent - ElastiCache for Redis](https://reinvent.awsevents.com/)

### 오픈소스 프로젝트
- [redis/redis-cluster-proxy](https://github.com/RedisLabs/redis-cluster-proxy) - 클러스터 프록시
- [oliver006/redis_exporter](https://github.com/oliver006/redis_exporter) - Prometheus exporter
- [redis/redis-py](https://github.com/redis/redis-py) - Python 클라이언트
- [luin/ioredis](https://github.com/luin/ioredis) - Node.js 클라이언트 (클러스터 지원)
- [redis/jedis](https://github.com/redis/jedis) - Java 클라이언트

### 실습 환경
- [Redis Labs Cloud](https://redis.com/try-free/) - 무료 클라우드 Redis 클러스터
- [AWS ElastiCache](https://aws.amazon.com/elasticache/) - 관리형 Redis 서비스
- [Google Cloud Memorystore](https://cloud.google.com/memorystore) - GCP 관리형 Redis
- [Azure Cache for Redis](https://azure.microsoft.com/services/cache/) - Azure Redis

### 책
- **"Redis in Action"** - Josiah Carlson
  - 실전 Redis 활용법
  - 클러스터 설계 패턴

- **"Redis 운영 관리"** - 강대명 저
  - 한글 Redis 운영 가이드
  - 실무 트러블슈팅

- **"Designing Data-Intensive Applications"** - Martin Kleppmann
  - 분산 시스템 이론
  - Redis를 포함한 다양한 데이터 저장소 비교

### 커뮤니티
- [Redis 한국 사용자 모임 (Facebook)](https://www.facebook.com/groups/rediskorea/)
- [Reddit r/redis](https://www.reddit.com/r/redis/)
- [Stack Overflow - Redis Tag](https://stackoverflow.com/questions/tagged/redis)
- [Redis Discord 서버](https://discord.gg/redis)

---

**이전 장으로 돌아가기**: [← 11장: Redis 실전 프로젝트](11-Redis-실전-프로젝트.md)

**목차로 돌아가기**: [📚 Redis 완전 학습 가이드](README.md)
