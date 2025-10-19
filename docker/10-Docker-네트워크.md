# 섹션 10: Docker 네트워크 완전 가이드

> **학습 목표**: Docker 네트워크의 동작 원리를 이해하고, 컨테이너 간 안전한 통신 환경을 설계하고 구축할 수 있습니다.

**⏱️ 예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐☆☆ (3개/5개)

---

## 📚 목차
- [왜 Docker 네트워크가 필요한가](#-왜-docker-네트워크가-필요한가)
- [실생활 비유로 이해하기](#-실생활-비유로-이해하기)
- [Docker 네트워크 기초](#101-docker-네트워크-기초)
- [네트워크 드라이버 종류](#102-네트워크-드라이버-종류)
- [네트워크 생성 및 관리](#103-네트워크-생성-및-관리)
- [컨테이너 간 통신](#104-컨테이너-간-통신)
- [외부 네트워크 연결](#105-외부-네트워크-연결)
- [포트 매핑 심화](#106-포트-매핑-심화)
- [DNS 및 서비스 디스커버리](#107-dns-및-서비스-디스커버리)
- [실습 예제](#108-실습-예제)
- [문제 해결](#109-문제-해결)
- [보안 모범 사례](#1010-보안-모범-사례)
- [주니어 시나리오](#-주니어-시나리오)
- [FAQ](#-faq)
- [면접 질문 리스트](#-면접-질문-리스트)
- [핵심 정리](#-핵심-정리)
- [다음 단계](#-다음-단계)

---

## 🤔 왜 Docker 네트워크가 필요한가?

### 실무 배경

**마이크로서비스 아키텍처에서 컨테이너 간 안전하고 효율적인 통신이 필수입니다.**

#### ❌ Docker 네트워크를 모르면 발생하는 문제

```
문제 1: 보안 취약점
- 증상: 데이터베이스 컨테이너가 외부에 직접 노출됨
- 영향: 해킹 위험, 데이터 유출 가능성
- 비용: 보안 사고 시 평균 $424만 손실 (IBM 2023)

문제 2: 통신 장애
- 증상: 컨테이너 IP가 재시작할 때마다 변경됨
- 영향: 애플리케이션 연결 실패, 서비스 다운타임
- 비용: 장애 복구 시간 평균 4시간, 시간당 $30만 손실

문제 3: 관리 복잡도
- 증상: 수십 개의 컨테이너 포트를 수동으로 관리
- 영향: 설정 오류, 포트 충돌 빈번
- 비용: 개발자 시간 낭비 (주당 8시간)
```

#### ✅ Docker 네트워크를 사용하면

```
해결책 1: 네트워크 격리
- 방법: 사용자 정의 브리지 네트워크로 컨테이너 그룹화
- 효과: 데이터베이스는 내부 네트워크에만, 웹은 외부 접근 가능
- 절감: 보안 사고 위험 95% 감소

해결책 2: DNS 기반 자동 서비스 디스커버리
- 방법: 컨테이너 이름으로 통신 (IP 불필요)
- 효과: 컨테이너 재시작해도 자동 연결
- 절감: 장애 시간 4시간 → 0초

해결책 3: 자동 네트워크 관리
- 방법: Docker Compose로 네트워크 자동 생성/연결
- 효과: 포트 충돌 없음, 설정 간소화
- 절감: 관리 시간 80% 감소 (주당 8시간 → 1.6시간)
```

### 📊 수치로 보는 효과

| 지표 | Before | After | 개선율 |
|------|--------|-------|--------|
| 설정 시간 | 4시간 (수동 포트 관리) | 10분 (자동 네트워크) | **96%↓** |
| 보안 사고 위험 | 높음 (외부 노출) | 낮음 (격리) | **95%↓** |
| 장애 복구 시간 | 4시간 | 즉시 (자동 재연결) | **100%↓** |
| 통신 지연 시간 | 0.5ms (NAT) | 0.1ms (직접 통신) | **80%↓** |
| 관리 인력 비용 | $1,000/월 | $200/월 | **80%↓** |

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 아파트 단지 네트워크

**실생활 비유: 아파트 내부 네트워크**

```
[일반 아파트 (네트워크 있음)]
101호 (웹서버) ←→ 내부 복도 ←→ 102호 (DB)
  ↑                                    ↑
  │                                    │
외부 출입구 (80번 포트)          직접 접근 불가 (보안)

[격리된 주택 (네트워크 없음)]
웹서버 집 🏠                    DB 집 🏠
  │                              │
  └──── 공공 도로 통해서만 통신 ────┘
       (느리고 불안전)
```

**핵심**: Docker 네트워크는 아파트 내부 복도처럼 컨테이너들을 안전하게 연결합니다.

### 비유 2: 회사 조직도와 부서 네트워크

```
[회사 조직 구조]
┌─────────────────────────────────┐
│       경영진 (외부 접근 포트)      │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│    영업팀 네트워크 (Frontend)     │
│    - 고객 대응 서비스             │
│    - 외부 노출 가능               │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│   개발팀 네트워크 (Backend)       │
│    - API 서버                    │
│    - 내부 통신만                 │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│    재무팀 네트워크 (Database)     │
│    - 민감한 데이터               │
│    - 완전 격리                   │
└─────────────────────────────────┘
```

**핵심**: 부서별로 네트워크를 나누면 보안과 관리가 쉬워집니다.

### 비유 3: 카카오톡 그룹 채팅방

```
[오픈 채팅방 - 기본 브리지 네트워크]
- 누구나 들어올 수 있음
- 사람들의 닉네임만 보임
- ID(IP)로 직접 검색 불가

[친구 그룹방 - 사용자 정의 네트워크]
- 초대받은 친구만 입장
- 이름으로 바로 멘션 가능 (@김철수)
- 자동으로 메시지 전달
```

**핵심**: 사용자 정의 네트워크는 친구 그룹방처럼 이름으로 소통 가능합니다.

### 비유 4: 배달의민족 주문 시스템

```
[배달 프로세스 - 마이크로서비스 네트워크]

고객 앱 (Frontend)
    ↓ [주문 요청]
주문 서비스 (Order Service)
    ↓ [결제 요청]
결제 서비스 (Payment Service)
    ↓ [가게 알림]
가게 서비스 (Restaurant Service)
    ↓ [배달 요청]
라이더 서비스 (Rider Service)

각 서비스는 독립된 컨테이너
네트워크로 안전하게 연결
하나가 다운되어도 다른 서비스는 정상 작동
```

**핵심**: 각 서비스(컨테이너)가 독립적이지만 네트워크로 협력합니다.

### 비유 5: 은행 금고실 보안 시스템

```
[3단계 보안 네트워크]

1층: 공개 로비 (Host Network)
- 외부인 출입 가능
- 포트 80, 443 개방
- 웹 페이지만 제공

2층: 직원 전용 (Backend Network)
- 직원 카드로만 입장
- API 서버, 업무 시스템
- 내부 통신만 허용

지하 금고실 (Internal Database Network)
- 최고 보안 등급
- 외부 인터넷 차단
- 데이터베이스만 존재
```

**핵심**: 중요도에 따라 네트워크를 계층화하면 보안이 강화됩니다.

### 🎯 종합 비교표

```
┌───────────────┬────────────┬────────────┬────────────┬────────────┐
│ Docker 네트워크 │ 아파트 복도 │ 회사 부서   │ 카톡 그룹방 │ 은행 금고   │
├───────────────┼────────────┼────────────┼────────────┼────────────┤
│ 격리         │ 동별 분리   │ 부서별 분리 │ 방 초대제   │ 층별 분리   │
│ 통신         │ 내부 복도   │ 내선 전화   │ 멘션 기능   │ 보안 통로   │
│ 외부 접근     │ 정문만      │ 리셉션만    │ 공개 링크   │ 1층 로비만  │
│ DNS          │ 호수 번호   │ 직급/이름   │ 닉네임      │ 직원 이름   │
└───────────────┴────────────┴────────────┴────────────┴────────────┘
```

---

## 10.1 Docker 네트워크 기초

### 10.1.1 네트워크가 왜 필요한가?

#### Docker 네트워크의 역할

```
1. 컨테이너 간 통신
   ┌──────────────┐      ┌──────────────┐
   │   Web App    │ ←──→ │   Database   │
   │ (container1) │      │ (container2) │
   └──────────────┘      └──────────────┘
        같은 네트워크에서 안전하게 통신

2. 외부 접근 제어
   인터넷 → Port 80 → Web App (공개)
   인터넷 ✗ → Database (비공개, 내부만)

3. 격리 (Isolation)
   [프로덕션 네트워크]      [개발 네트워크]
   - Web App               - Test Web
   - DB                    - Test DB
   서로 통신 불가 (보안)
```

---

### 10.1.2 Docker 네트워크 아키텍처

```
[호스트 머신]
├─ eth0 (물리 네트워크 카드): 192.168.1.100
│
├─ docker0 (기본 브리지): 172.17.0.1
│   ├─ veth12345 ←→ [Container 1] eth0: 172.17.0.2
│   └─ veth67890 ←→ [Container 2] eth0: 172.17.0.3
│
├─ br-abc123 (커스텀 브리지): 172.20.0.1
│   ├─ vethdef456 ←→ [Container 3] eth0: 172.20.0.2
│   └─ vethhij789 ←→ [Container 4] eth0: 172.20.0.3
│
└─ iptables (방화벽 규칙)
    - 포트 포워딩: 80 → 172.17.0.2:80
    - NAT: 컨테이너 → 외부 인터넷
```

**핵심 구성 요소:**

| 구성 요소 | 역할 | 예시 |
|----------|------|------|
| **docker0** | 기본 브리지 네트워크 | 172.17.0.0/16 |
| **veth pair** | 가상 이더넷 케이블 | veth12345 ↔ eth0 |
| **iptables** | 방화벽 및 NAT | 포트 포워딩, 패킷 필터링 |
| **Network Namespace** | 격리된 네트워크 스택 | 각 컨테이너마다 독립적 |

---

### 10.1.3 기본 네트워크 확인

```bash
# 모든 네트워크 목록
docker network ls

# 출력:
# NETWORK ID     NAME      DRIVER    SCOPE
# abc123def456   bridge    bridge    local
# def456ghi789   host      host      local
# ghi789jkl012   none      null      local
```

**기본 네트워크 3종:**

```
1. bridge (기본)
   - 새 컨테이너의 기본 네트워크
   - 격리된 네트워크 (172.17.0.0/16)
   - 컨테이너 이름으로 통신 불가 (IP만)

2. host
   - 호스트의 네트워크를 직접 사용
   - 네트워크 격리 없음
   - 최고 성능 (네트워크 오버헤드 0)

3. none
   - 네트워크 없음
   - 완전 격리 (외부 통신 불가)
   - 보안이 최우선인 경우
```

---

## 10.2 네트워크 드라이버 종류

### 10.2.1 Bridge 네트워크 (기본)

**특징:**
- 가장 많이 사용되는 네트워크
- 동일 호스트 내 컨테이너 간 통신
- 외부 접근은 포트 매핑 필요

#### 기본 브리지 vs 사용자 정의 브리지

```bash
# 1. 기본 브리지 (docker0)
docker run -d --name web1 nginx
docker inspect web1 | grep IPAddress
# "IPAddress": "172.17.0.2"

docker run -d --name web2 nginx
docker inspect web2 | grep IPAddress
# "IPAddress": "172.17.0.3"

# 통신 테스트 (IP로만 가능)
docker exec web1 ping 172.17.0.3  # ✅ 성공
docker exec web1 ping web2         # ❌ 실패 (이름 해석 불가)
```

```bash
# 2. 사용자 정의 브리지
docker network create mynetwork

docker run -d --name web1 --network mynetwork nginx
docker run -d --name web2 --network mynetwork nginx

# 통신 테스트 (이름으로 가능!)
docker exec web1 ping web2         # ✅ 성공 (내장 DNS)
docker exec web1 curl http://web2  # ✅ 성공
```

**사용자 정의 브리지의 장점:**

| 기능 | 기본 브리지 | 사용자 정의 브리지 |
|------|-------------|-------------------|
| DNS 이름 해석 | ❌ | ✅ |
| 네트워크 격리 | 부분 | ✅ 완전 |
| 동적 연결/해제 | ❌ | ✅ |
| 서브넷 커스터마이징 | ❌ | ✅ |

#### 실습: Bridge 네트워크 생성

```bash
# 커스텀 브리지 네트워크 생성
docker network create \
  --driver bridge \
  --subnet 172.25.0.0/16 \
  --gateway 172.25.0.1 \
  --ip-range 172.25.5.0/24 \
  myapp-network

# 상세 정보 확인
docker network inspect myapp-network

# 출력:
# [
#     {
#         "Name": "myapp-network",
#         "Driver": "bridge",
#         "IPAM": {
#             "Config": [
#                 {
#                     "Subnet": "172.25.0.0/16",
#                     "Gateway": "172.25.0.1",
#                     "IPRange": "172.25.5.0/24"
#                 }
#             ]
#         }
#     }
# ]
```

**네트워크 구조:**

```
[호스트: 192.168.1.100]
│
├─ br-abc123 (myapp-network): 172.25.0.1
│   │
│   ├─ veth1 ←→ [web-app] eth0: 172.25.5.2
│   │           └─ nginx:80
│   │
│   └─ veth2 ←→ [api-server] eth0: 172.25.5.3
│               └─ node:3000
│
└─ iptables 규칙
    - 172.25.5.2:80 → 외부:8080 (포트 포워딩)
```

---

### 10.2.2 Host 네트워크

**특징:**
- 컨테이너가 호스트의 네트워크 스택을 직접 사용
- 포트 매핑 불필요
- 최고 성능 (네트워크 오버헤드 없음)
- 네트워크 격리 없음 (보안 주의)

```bash
# Host 네트워크로 컨테이너 실행
docker run -d --name web --network host nginx

# 호스트의 80번 포트에서 직접 리스닝
curl http://localhost:80  # ✅ 바로 접근 가능

# 확인
docker exec web ip addr show
# 출력: 호스트와 동일한 네트워크 인터페이스
```

**비교:**

```
[Bridge 모드]
외부 요청 → 호스트:8080 → iptables NAT → 컨테이너:80
          (변환 오버헤드 있음)

[Host 모드]
외부 요청 → 호스트:80 (= 컨테이너:80)
          (변환 없음, 직접 접근)
```

**사용 사례:**

```
✅ 사용하면 좋은 경우:
- 초고성능이 필요한 네트워크 애플리케이션
- 모니터링 도구 (Prometheus, Grafana)
- 네트워크 디버깅 도구

❌ 사용하면 안 되는 경우:
- 여러 컨테이너가 같은 포트 사용
- 보안이 중요한 프로덕션 환경
- 격리가 필요한 멀티테넌트 환경
```

---

### 10.2.3 Overlay 네트워크 (Swarm/Kubernetes)

**특징:**
- 여러 Docker 호스트 간 통신
- Docker Swarm 또는 Kubernetes 환경에서 사용
- VXLAN 기술 활용

```
[호스트 A: 192.168.1.100]          [호스트 B: 192.168.1.101]
├─ overlay-net                      ├─ overlay-net
│   └─ [web] 10.0.0.2               │   └─ [api] 10.0.0.3
│                                   │
└─────── 물리 네트워크 (192.168.1.0/24) ─────┘
              │
         [VXLAN 터널]
     (논리적으로 같은 네트워크)
```

```bash
# Swarm 초기화
docker swarm init

# Overlay 네트워크 생성
docker network create \
  --driver overlay \
  --attachable \
  myoverlay

# 서비스 생성
docker service create \
  --name web \
  --network myoverlay \
  --replicas 3 \
  nginx

# 다른 호스트의 컨테이너도 같은 네트워크에서 통신 가능
```

**Overlay vs Bridge:**

| 특징 | Bridge | Overlay |
|------|--------|---------|
| 범위 | 단일 호스트 | 다중 호스트 |
| 기술 | Linux Bridge | VXLAN |
| 사용 환경 | 로컬 개발 | 클러스터 (Swarm, K8s) |
| 성능 | 빠름 | 약간 느림 (캡슐화) |

---

### 10.2.4 Macvlan 네트워크

**특징:**
- 컨테이너에 물리 네트워크의 MAC 주소 할당
- 컨테이너가 물리 네트워크의 "진짜" 장치처럼 보임
- 레거시 애플리케이션에 유용

```
[물리 네트워크: 192.168.1.0/24]
├─ 라우터: 192.168.1.1
├─ 호스트: 192.168.1.100
├─ [컨테이너1]: 192.168.1.150 (MAC: 02:42:c0:a8:01:96)
└─ [컨테이너2]: 192.168.1.151 (MAC: 02:42:c0:a8:01:97)

외부에서 컨테이너를 일반 서버처럼 접근 가능
```

```bash
# Macvlan 네트워크 생성
docker network create -d macvlan \
  --subnet=192.168.1.0/24 \
  --gateway=192.168.1.1 \
  -o parent=eth0 \
  macvlan-net

# 컨테이너 실행
docker run -d \
  --name web \
  --network macvlan-net \
  --ip 192.168.1.150 \
  nginx

# 외부에서 직접 접근
curl http://192.168.1.150
```

**주의사항:**

```
⚠️  호스트에서 컨테이너 접근 불가
    (물리 네트워크 인터페이스 제약)

⚠️  네트워크 스위치가 프로미스큐어스 모드 지원 필요

✅  사용 사례:
    - DHCP 서버 컨테이너
    - 네트워크 모니터링 도구
    - 레거시 애플리케이션 (특정 MAC 주소 필요)
```

---

### 10.2.5 None 네트워크

**특징:**
- 네트워크 인터페이스 없음
- 완전 격리 (loopback만 존재)
- 최고 수준 보안

```bash
# None 네트워크로 실행
docker run -d --name isolated --network none alpine sleep 3600

# 네트워크 확인
docker exec isolated ip addr show

# 출력:
# 1: lo: <LOOPBACK,UP,LOWER_UP>
#     inet 127.0.0.1/8 scope host lo
# (다른 인터페이스 없음)

# 외부 통신 불가
docker exec isolated ping 8.8.8.8
# ping: bad address '8.8.8.8'
```

**사용 사례:**

```
✅ 네트워크가 불필요한 배치 작업
   - 데이터 변환 프로세스
   - 파일 처리 작업

✅ 보안이 극도로 중요한 경우
   - 암호화 키 생성
   - 민감한 데이터 처리
```

---

## 10.3 네트워크 생성 및 관리

### 10.3.1 네트워크 생성

```bash
# 기본 생성
docker network create mynetwork

# 상세 옵션 지정
docker network create \
  --driver bridge \
  --subnet 172.28.0.0/16 \
  --gateway 172.28.0.1 \
  --ip-range 172.28.5.0/24 \
  --opt "com.docker.network.bridge.name"="br-myapp" \
  --opt "com.docker.network.bridge.enable_ip_masquerade"="true" \
  --opt "com.docker.network.bridge.enable_icc"="true" \
  --opt "com.docker.network.driver.mtu"="1500" \
  --label project=myapp \
  --label environment=production \
  myapp-network
```

**옵션 설명:**

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--driver` | 네트워크 드라이버 | bridge, overlay, macvlan |
| `--subnet` | 서브넷 CIDR | 172.28.0.0/16 |
| `--gateway` | 게이트웨이 IP | 172.28.0.1 |
| `--ip-range` | IP 할당 범위 | 172.28.5.0/24 |
| `--opt` | 드라이버 옵션 | MTU, ICC 등 |
| `--label` | 메타데이터 | project, env 등 |

---

### 10.3.2 네트워크 조회 및 검사

```bash
# 모든 네트워크 목록
docker network ls

# 필터링
docker network ls --filter driver=bridge
docker network ls --filter label=project=myapp

# 상세 정보
docker network inspect myapp-network

# 특정 필드만 추출 (jq 사용)
docker network inspect myapp-network | jq '.[0].IPAM.Config'

# 출력:
# [
#   {
#     "Subnet": "172.28.0.0/16",
#     "Gateway": "172.28.0.1",
#     "IPRange": "172.28.5.0/24"
#   }
# ]
```

---

### 10.3.3 컨테이너 네트워크 연결/해제

```bash
# 컨테이너 실행 (기본 네트워크)
docker run -d --name web nginx

# 새 네트워크에 연결 (다중 네트워크)
docker network connect myapp-network web

# 확인
docker inspect web | jq '.[0].NetworkSettings.Networks'

# 출력:
# {
#   "bridge": {
#     "IPAddress": "172.17.0.2",
#     ...
#   },
#   "myapp-network": {
#     "IPAddress": "172.28.5.2",
#     ...
#   }
# }

# 네트워크 해제
docker network disconnect bridge web

# 이제 myapp-network만 사용
```

---

### 10.3.4 네트워크 정리

```bash
# 특정 네트워크 삭제
docker network rm myapp-network

# 사용하지 않는 모든 네트워크 삭제
docker network prune

# 출력:
# WARNING! This will remove all custom networks not used by at least one container.
# Are you sure you want to continue? [y/N] y
# Deleted Networks:
# myapp-network
# test-network

# 강제 삭제 (확인 없이)
docker network prune -f
```

---

## 10.4 컨테이너 간 통신

### 10.4.1 같은 네트워크 내 통신

#### 시나리오: 웹 앱 + 데이터베이스

```bash
# 네트워크 생성
docker network create app-network

# PostgreSQL 컨테이너 실행
docker run -d \
  --name postgres \
  --network app-network \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=myapp \
  postgres:15-alpine

# 웹 애플리케이션 실행
docker run -d \
  --name webapp \
  --network app-network \
  -e DATABASE_URL=postgresql://postgres:secret@postgres:5432/myapp \
  mywebapp:latest

# webapp에서 postgres로 연결 (DNS 이름 사용)
docker exec webapp psql postgresql://postgres:secret@postgres:5432/myapp -c "SELECT version();"
# ✅ 성공!
```

**네트워크 구조:**

```
[app-network: 172.18.0.0/16]
├─ postgres: 172.18.0.2
│   └─ Port 5432 (내부만 접근 가능)
│
└─ webapp: 172.18.0.3
    └─ Port 3000
    └─ 환경변수: DATABASE_URL=postgresql://postgres:secret@postgres:5432/myapp
                                                            ↑
                                             내장 DNS가 172.18.0.2로 해석
```

---

### 10.4.2 여러 네트워크에 연결

#### 시나리오: API 게이트웨이

```bash
# 프론트엔드 네트워크
docker network create frontend

# 백엔드 네트워크
docker network create backend

# 데이터베이스 (backend만)
docker run -d \
  --name database \
  --network backend \
  postgres:15-alpine

# API 서버 (backend만)
docker run -d \
  --name api \
  --network backend \
  myapi:latest

# API 게이트웨이 (frontend + backend 모두)
docker run -d \
  --name gateway \
  --network frontend \
  nginx:alpine

docker network connect backend gateway

# 프론트엔드 앱 (frontend만)
docker run -d \
  --name webapp \
  --network frontend \
  myfrontend:latest
```

**네트워크 구조:**

```
[frontend: 172.20.0.0/16]
├─ gateway: 172.20.0.2 (양쪽 연결!)
└─ webapp: 172.20.0.3

[backend: 172.21.0.0/16]
├─ gateway: 172.21.0.2 (양쪽 연결!)
├─ api: 172.21.0.3
└─ database: 172.21.0.4

통신 흐름:
webapp → gateway (172.20.0.2) → api (172.21.0.3) → database (172.21.0.4)
                   ↑
              두 네트워크를 연결하는 다리
```

**보안 이점:**

```
✅ webapp은 database에 직접 접근 불가 (격리됨)
✅ gateway가 트래픽 제어 (프록시 역할)
✅ 최소 권한 원칙 (Principle of Least Privilege)
```

---

### 10.4.3 Docker Compose로 네트워크 관리

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  # 프론트엔드
  webapp:
    image: myfrontend:latest
    networks:
      - frontend
    depends_on:
      - gateway

  # API 게이트웨이
  gateway:
    image: nginx:alpine
    networks:
      - frontend
      - backend
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"

  # API 서버
  api:
    image: myapi:latest
    networks:
      - backend
    environment:
      DATABASE_URL: postgresql://postgres:secret@database:5432/myapp
    depends_on:
      - database

  # 데이터베이스
  database:
    image: postgres:15-alpine
    networks:
      - backend
    environment:
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp
    volumes:
      - pgdata:/var/lib/postgresql/data

networks:
  frontend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

  backend:
    driver: bridge
    internal: true  # 외부 접근 차단
    ipam:
      config:
        - subnet: 172.21.0.0/16

volumes:
  pgdata:
```

```bash
# 실행
docker-compose up -d

# 네트워크 확인
docker network ls | grep myproject
# myproject_frontend
# myproject_backend

# 통신 테스트
docker-compose exec webapp curl http://gateway/api/health
# ✅ 성공

docker-compose exec webapp curl http://database:5432
# ❌ 실패 (다른 네트워크, 접근 불가)
```

---

## 10.5 외부 네트워크 연결

### 10.5.1 인터넷 접근 (NAT)

```bash
# 기본적으로 컨테이너는 인터넷 접근 가능
docker run -it alpine sh

# 컨테이너 내부에서
ping 8.8.8.8       # ✅ 성공
wget google.com    # ✅ 성공
```

**작동 원리 (NAT - Network Address Translation):**

```
[컨테이너: 172.17.0.2]
    ↓ 요청: 8.8.8.8 (Google DNS)
[docker0: 172.17.0.1]
    ↓ iptables NAT 규칙
[호스트 eth0: 192.168.1.100]
    ↓ 소스 IP 변환: 172.17.0.2 → 192.168.1.100
[인터넷]
    ↓ 응답: 192.168.1.100
[호스트]
    ↓ 목적지 IP 변환: 192.168.1.100 → 172.17.0.2
[컨테이너] ✅ 응답 수신
```

**iptables 규칙 확인:**

```bash
sudo iptables -t nat -L -n -v | grep docker

# 출력 예시:
# Chain POSTROUTING
# MASQUERADE  all  --  172.17.0.0/16  0.0.0.0/0
#             ↑                        ↑
#        컨테이너 네트워크          모든 목적지
```

---

### 10.5.2 인터넷 접근 차단

```bash
# 격리된 네트워크 생성 (인터넷 차단)
docker network create \
  --internal \
  isolated-network

# 컨테이너 실행
docker run -it --network isolated-network alpine sh

# 외부 접근 불가
ping 8.8.8.8  # ❌ 실패
wget google.com  # ❌ 실패

# 같은 네트워크 내부 통신은 가능
```

**사용 사례:**

```
✅ 민감한 데이터 처리
✅ 데이터베이스 (외부 접근 불필요)
✅ 캐시 서버 (Redis, Memcached)
✅ 내부 마이크로서비스
```

---

## 10.6 포트 매핑 심화

### 10.6.1 포트 매핑 기본

```bash
# 기본 형식: -p [호스트포트]:[컨테이너포트]

# 1. 단일 포트
docker run -d -p 8080:80 nginx
# 호스트:8080 → 컨테이너:80

# 2. 여러 포트
docker run -d \
  -p 8080:80 \
  -p 8443:443 \
  nginx

# 3. 특정 인터페이스 바인딩
docker run -d -p 127.0.0.1:8080:80 nginx
# localhost에서만 접근 가능

# 4. 랜덤 호스트 포트
docker run -d -p 80 nginx
# 호스트의 임의 포트 → 컨테이너:80

# 할당된 포트 확인
docker port <container>
```

---

### 10.6.2 포트 매핑 고급

#### UDP 포트

```bash
# UDP 포트 매핑
docker run -d -p 53:53/udp dns-server

# TCP + UDP 동시
docker run -d \
  -p 53:53/tcp \
  -p 53:53/udp \
  dns-server
```

#### 포트 범위

```bash
# 연속된 포트 범위
docker run -d -p 8000-8010:8000-8010 myapp

# 호스트:8000 → 컨테이너:8000
# 호스트:8001 → 컨테이너:8001
# ...
# 호스트:8010 → 컨테이너:8010
```

---

### 10.6.3 포트 매핑 없이 외부 접근

#### nginx 리버스 프록시 사용

```bash
# 네트워크 생성
docker network create webapps

# 웹 앱 (포트 매핑 없음)
docker run -d \
  --name app1 \
  --network webapps \
  myapp:latest

# nginx 프록시 (80번만 공개)
docker run -d \
  --name proxy \
  --network webapps \
  -p 80:80 \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf \
  nginx:alpine
```

**nginx.conf:**

```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app1:3000;
    }

    server {
        listen 80;
        server_name example.com;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

**장점:**

```
✅ 하나의 호스트 포트(80)로 여러 앱 서비스
✅ SSL/TLS 종료를 프록시에서 처리
✅ 로드 밸런싱 가능
✅ 보안 (앱 컨테이너는 직접 노출 안됨)
```

---

## 10.7 DNS 및 서비스 디스커버리

### 10.7.1 내장 DNS 서버

**Docker의 내장 DNS (127.0.0.11):**

```bash
# 네트워크 생성
docker network create mynet

# 컨테이너 실행
docker run -d --name web --network mynet nginx
docker run -d --name api --network mynet alpine sleep 3600

# DNS 확인
docker exec api cat /etc/resolv.conf

# 출력:
# nameserver 127.0.0.11
# options ndots:0

# DNS 조회
docker exec api nslookup web

# 출력:
# Server:    127.0.0.11
# Address 1: 127.0.0.11
#
# Name:      web
# Address 1: 172.18.0.2 web.mynet
```

**작동 원리:**

```
[api 컨테이너]
    ↓ DNS 쿼리: "web이 뭐야?"
[127.0.0.11 - Docker DNS]
    ↓ 네트워크 정보 조회
[Docker Engine - 네트워크 데이터베이스]
    ↓ "web = 172.18.0.2"
[127.0.0.11]
    ↓ 응답: 172.18.0.2
[api 컨테이너] ✅ 172.18.0.2로 연결
```

---

### 10.7.2 컨테이너 별칭 (Alias)

```bash
# 네트워크 생성
docker network create mynet

# 별칭으로 컨테이너 실행
docker run -d \
  --name postgres-primary \
  --network mynet \
  --network-alias database \
  --network-alias db \
  postgres:15-alpine

docker run -d \
  --name postgres-replica \
  --network mynet \
  --network-alias database \
  postgres:15-alpine

# DNS 조회
docker run --rm --network mynet alpine nslookup database

# 출력:
# Name:      database
# Address 1: 172.18.0.2 postgres-primary.mynet
# Address 2: 172.18.0.3 postgres-replica.mynet
```

**사용 사례: 로드 밸런싱**

```bash
# 애플리케이션에서 "database"로 연결
# Docker DNS가 자동으로 라운드 로빈
DATABASE_URL=postgresql://user:pass@database:5432/mydb

# 요청 1 → 172.18.0.2 (postgres-primary)
# 요청 2 → 172.18.0.3 (postgres-replica)
# 요청 3 → 172.18.0.2 (다시 첫 번째)
```

---

### 10.7.3 Docker Compose 서비스 디스커버리

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    networks:
      - frontend
      - backend

  api:
    image: myapi:latest
    networks:
      backend:
        aliases:
          - api-service
          - backend-api
    environment:
      # 서비스 이름으로 접근 가능
      DATABASE_URL: postgresql://postgres:secret@database:5432/myapp
      REDIS_URL: redis://cache:6379

  database:
    image: postgres:15-alpine
    networks:
      - backend

  cache:
    image: redis:7-alpine
    networks:
      - backend

networks:
  frontend:
  backend:
```

**자동 DNS 해석:**

```bash
# api 컨테이너 내부에서
curl http://web              # ✅ nginx 접근
curl http://database:5432    # ✅ PostgreSQL 접근
curl http://cache:6379       # ✅ Redis 접근

# 별칭으로도 접근 가능
curl http://api-service      # ✅ api 컨테이너
curl http://backend-api      # ✅ api 컨테이너
```

---

## 10.8 실습 예제

### 10.8.1 마이크로서비스 네트워크 구축

#### 시나리오: 전자상거래 시스템

```
[인터넷]
    ↓
[Nginx Proxy: 80, 443]
    ↓
[Frontend Network]
    ├─ Web UI (React)
    └─ API Gateway
         ↓
[Backend Network]
    ├─ User Service
    ├─ Product Service
    ├─ Order Service
    └─ Payment Service
         ↓
[Data Network]
    ├─ PostgreSQL (Users, Products)
    ├─ MongoDB (Orders)
    └─ Redis (Cache)
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  # ==================== 프록시 레이어 ====================
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    networks:
      - frontend
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api-gateway

  # ==================== 프론트엔드 레이어 ====================
  webapp:
    image: ecommerce-webapp:latest
    networks:
      - frontend
    environment:
      API_URL: http://api-gateway:3000

  api-gateway:
    image: ecommerce-gateway:latest
    networks:
      - frontend
      - backend
    environment:
      USER_SERVICE: http://user-service:4001
      PRODUCT_SERVICE: http://product-service:4002
      ORDER_SERVICE: http://order-service:4003
      PAYMENT_SERVICE: http://payment-service:4004
    depends_on:
      - user-service
      - product-service
      - order-service
      - payment-service

  # ==================== 백엔드 레이어 ====================
  user-service:
    image: user-service:latest
    networks:
      - backend
      - data
    environment:
      DATABASE_URL: postgresql://postgres:secret@postgres:5432/users
      REDIS_URL: redis://cache:6379
    depends_on:
      - postgres
      - cache

  product-service:
    image: product-service:latest
    networks:
      - backend
      - data
    environment:
      DATABASE_URL: postgresql://postgres:secret@postgres:5432/products
      REDIS_URL: redis://cache:6379
    depends_on:
      - postgres
      - cache

  order-service:
    image: order-service:latest
    networks:
      - backend
      - data
    environment:
      MONGODB_URL: mongodb://mongo:27017/orders
      REDIS_URL: redis://cache:6379
    depends_on:
      - mongo
      - cache

  payment-service:
    image: payment-service:latest
    networks:
      - backend
    environment:
      STRIPE_API_KEY: ${STRIPE_API_KEY}
      REDIS_URL: redis://cache:6379
    depends_on:
      - cache

  # ==================== 데이터 레이어 ====================
  postgres:
    image: postgres:15-alpine
    networks:
      - data
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init.sql

  mongo:
    image: mongo:7
    networks:
      - data
    volumes:
      - mongodata:/data/db

  cache:
    image: redis:7-alpine
    networks:
      - backend
      - data
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru

networks:
  frontend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

  backend:
    driver: bridge
    internal: true  # 외부 접근 차단
    ipam:
      config:
        - subnet: 172.21.0.0/16

  data:
    driver: bridge
    internal: true  # 외부 접근 차단
    ipam:
      config:
        - subnet: 172.22.0.0/16

volumes:
  pgdata:
  mongodata:
```

---

### 10.8.2 실습: 3-Tier 웹 애플리케이션

#### 단계 1: 네트워크 생성

```bash
# 프론트엔드 네트워크 (외부 접근 가능)
docker network create \
  --driver bridge \
  --subnet 172.20.0.0/16 \
  frontend

# 백엔드 네트워크 (내부만)
docker network create \
  --driver bridge \
  --internal \
  --subnet 172.21.0.0/16 \
  backend
```

---

#### 단계 2: 데이터베이스 실행

```bash
docker run -d \
  --name database \
  --network backend \
  -e POSTGRES_PASSWORD=secretpassword \
  -e POSTGRES_DB=webapp \
  -v pgdata:/var/lib/postgresql/data \
  postgres:15-alpine
```

---

#### 단계 3: API 서버 실행

**app.js (Node.js API):**

```javascript
const express = require('express');
const { Pool } = require('pg');

const app = express();
const port = 3000;

// PostgreSQL 연결
const pool = new Pool({
  host: 'database',  // DNS 이름!
  port: 5432,
  database: 'webapp',
  user: 'postgres',
  password: 'secretpassword'
});

app.get('/api/health', async (req, res) => {
  try {
    const result = await pool.query('SELECT NOW()');
    res.json({ status: 'ok', database: result.rows[0].now });
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

app.get('/api/users', async (req, res) => {
  const result = await pool.query('SELECT * FROM users');
  res.json(result.rows);
});

app.listen(port, '0.0.0.0', () => {
  console.log(`API server listening on port ${port}`);
});
```

**Dockerfile:**

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["node", "app.js"]
```

**실행:**

```bash
# 이미지 빌드
docker build -t myapi:latest .

# 컨테이너 실행 (양쪽 네트워크에 연결)
docker run -d \
  --name api \
  --network backend \
  myapi:latest

docker network connect frontend api
```

---

#### 단계 4: 웹 서버 (Nginx) 실행

**nginx.conf:**

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        server api:3000;
    }

    server {
        listen 80;
        server_name localhost;

        # 정적 파일
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
        }

        # API 프록시
        location /api/ {
            proxy_pass http://api_backend/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

**실행:**

```bash
docker run -d \
  --name webserver \
  --network frontend \
  -p 80:80 \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf \
  -v $(pwd)/html:/usr/share/nginx/html \
  nginx:alpine
```

---

#### 단계 5: 테스트

```bash
# 헬스체크
curl http://localhost/api/health

# 출력:
# {"status":"ok","database":"2024-01-15T10:30:00.000Z"}

# 네트워크 확인
docker network inspect frontend
docker network inspect backend

# 통신 테스트
docker exec api ping database  # ✅ 성공 (같은 backend 네트워크)
docker exec webserver ping api  # ✅ 성공 (같은 frontend 네트워크)
docker exec webserver ping database  # ❌ 실패 (다른 네트워크)
```

---

### 10.8.3 실습: 로드 밸런싱

#### 시나리오: Nginx로 3개 API 서버 로드 밸런싱

```bash
# 네트워크 생성
docker network create loadbalancer-net

# API 서버 3개 실행
for i in {1..3}; do
  docker run -d \
    --name api-${i} \
    --network loadbalancer-net \
    -e PORT=3000 \
    -e INSTANCE_ID=api-${i} \
    myapi:latest
done

# Nginx 로드 밸런서 실행
docker run -d \
  --name loadbalancer \
  --network loadbalancer-net \
  -p 80:80 \
  -v $(pwd)/nginx-lb.conf:/etc/nginx/nginx.conf \
  nginx:alpine
```

**nginx-lb.conf:**

```nginx
events {
    worker_connections 1024;
}

http {
    # 업스트림 정의 (로드 밸런싱 풀)
    upstream api_pool {
        # 라운드 로빈 (기본)
        server api-1:3000;
        server api-2:3000;
        server api-3:3000;

        # 선택사항: 로드 밸런싱 방식
        # least_conn;  # 연결 수 기준
        # ip_hash;     # 클라이언트 IP 기준 (세션 유지)

        # 가중치 설정
        # server api-1:3000 weight=3;
        # server api-2:3000 weight=2;
        # server api-3:3000 weight=1;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://api_pool;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

            # 헬스체크 (Nginx Plus 기능, 오픈소스는 별도 모듈 필요)
            # health_check interval=5s fails=3 passes=2;
        }
    }
}
```

**테스트:**

```bash
# 여러 번 요청 (라운드 로빈 확인)
for i in {1..6}; do
  curl http://localhost/
  echo ""
done

# 출력:
# {"instance":"api-1","response":"Hello"}
# {"instance":"api-2","response":"Hello"}
# {"instance":"api-3","response":"Hello"}
# {"instance":"api-1","response":"Hello"}
# {"instance":"api-2","response":"Hello"}
# {"instance":"api-3","response":"Hello"}
```

---

## 10.9 문제 해결

### 10.9.1 컨테이너 간 통신 실패

**증상:**

```bash
docker exec webapp curl http://database:5432
# curl: (6) Could not resolve host: database
```

**원인 및 해결:**

```bash
# 1. 같은 네트워크에 있는지 확인
docker inspect webapp | jq '.[0].NetworkSettings.Networks'
docker inspect database | jq '.[0].NetworkSettings.Networks'

# 다른 네트워크에 있으면:
docker network connect mynetwork webapp

# 2. 기본 브리지 네트워크 사용 중인지 확인
# (기본 브리지는 DNS 없음)
docker network create mynetwork
docker network connect mynetwork webapp
docker network connect mynetwork database
docker network disconnect bridge webapp
docker network disconnect bridge database
```

---

### 10.9.2 포트 충돌

**증상:**

```bash
docker run -d -p 80:80 nginx
# Error: Bind for 0.0.0.0:80 failed: port is already allocated
```

**해결:**

```bash
# 1. 다른 포트 사용
docker run -d -p 8080:80 nginx

# 2. 기존 프로세스 종료
sudo lsof -i :80
sudo kill <PID>

# 3. 특정 인터페이스에만 바인딩
docker run -d -p 127.0.0.1:80:80 nginx
```

---

### 10.9.3 외부 인터넷 접근 안 됨

**증상:**

```bash
docker exec mycontainer ping 8.8.8.8
# ping: sendto: Network is unreachable
```

**원인 및 해결:**

```bash
# 1. IP 포워딩 활성화 확인
cat /proc/sys/net/ipv4/ip_forward
# 0이면 비활성화, 1이면 활성화

# 활성화:
sudo sysctl -w net.ipv4.ip_forward=1
sudo systemctl restart docker

# 2. iptables NAT 규칙 확인
sudo iptables -t nat -L -n -v | grep MASQUERADE

# 규칙 없으면 Docker 재시작:
sudo systemctl restart docker

# 3. 방화벽 확인 (firewalld, ufw)
sudo firewall-cmd --zone=public --add-masquerade --permanent
sudo firewall-cmd --reload
```

---

### 10.9.4 느린 DNS 해석

**증상:**

```bash
docker exec mycontainer time nslookup google.com
# real    0m10.234s  (너무 느림!)
```

**해결:**

```bash
# Docker DNS 서버 변경
# /etc/docker/daemon.json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}

sudo systemctl restart docker
```

---

## 10.10 보안 모범 사례

### ✅ 체크리스트

- [ ] **최소 권한 원칙**: 필요한 네트워크만 연결
- [ ] **내부 네트워크 사용**: 데이터베이스 등은 `--internal`
- [ ] **포트 최소화**: 필요한 포트만 공개
- [ ] **특정 인터페이스 바인딩**: `-p 127.0.0.1:8080:80`
- [ ] **방화벽 규칙**: iptables로 추가 제어
- [ ] **TLS/SSL 사용**: 민감한 통신은 암호화
- [ ] **네트워크 정책**: Overlay 네트워크에서 정책 적용
- [ ] **모니터링**: 네트워크 트래픽 로깅

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: 기본 브리지만 사용하다 DNS 문제 발생

**상황**: 주니어 개발자가 웹 앱과 데이터베이스를 기본 설정으로 실행했는데, 컨테이너 이름으로 연결이 안 됩니다.

```bash
# ❌ 주니어 개발자가 작성한 명령어
docker run -d --name postgres postgres:15-alpine
docker run -d --name webapp \
  -e DATABASE_URL=postgresql://postgres@postgres:5432/mydb \
  mywebapp:latest

# 앱 로그 확인
docker logs webapp
# Error: getaddrinfo ENOTFOUND postgres
```

**문제점**:
- 기본 브리지 네트워크는 DNS 이름 해석을 지원하지 않음
- 컨테이너 이름으로 통신 불가, IP 주소만 가능
- 재시작 시 IP가 변경되어 연결이 끊어짐

**해결책**:
```bash
# ✅ 올바른 코드
# 1. 사용자 정의 네트워크 생성
docker network create myapp-network

# 2. 기존 컨테이너 삭제
docker rm -f postgres webapp

# 3. 네트워크 지정하여 재실행
docker run -d --name postgres \
  --network myapp-network \
  postgres:15-alpine

docker run -d --name webapp \
  --network myapp-network \
  -e DATABASE_URL=postgresql://postgres@postgres:5432/mydb \
  mywebapp:latest

# 4. 테스트
docker exec webapp ping postgres  # ✅ 성공!
```

**배운 점**:
- 사용자 정의 네트워크는 자동 DNS 제공
- 프로덕션에서는 절대 기본 브리지 사용 금지
- Docker Compose는 자동으로 사용자 정의 네트워크 생성

---

### 시나리오 2: 데이터베이스를 외부에 노출시킨 보안 사고

**상황**: 포트 매핑을 잘못 설정해서 데이터베이스가 인터넷에 노출되었습니다.

```bash
# ❌ 위험한 설정
docker run -d --name postgres \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=weak123 \
  postgres:15-alpine

# 이제 누구나 접근 가능!
# psql -h <서버IP> -U postgres
```

**문제점**:
- 데이터베이스가 인터넷에 직접 노출됨
- 약한 비밀번호로 해킹 위험
- 비용: 데이터 유출 시 평균 $424만 손실

**해결책**:
```bash
# ✅ 올바른 보안 설정
# 1. 내부 네트워크 생성
docker network create --internal backend-network

# 2. 데이터베이스는 포트 매핑 없이
docker run -d --name postgres \
  --network backend-network \
  -e POSTGRES_PASSWORD=<강력한비밀번호> \
  postgres:15-alpine

# 3. API 서버만 양쪽 네트워크에 연결
docker network create frontend-network

docker run -d --name api \
  --network backend-network \
  -p 3000:3000 \
  myapi:latest

docker network connect frontend-network api

# 설명:
# - postgres는 backend-network에만 → 외부 접근 불가
# - api는 양쪽 네트워크에 → 브리지 역할
# - frontend-network는 외부 접근 가능
```

**배운 점**:
- 데이터베이스는 절대 포트 매핑 금지
- `--internal` 플래그로 인터넷 차단
- 계층화된 네트워크 아키텍처 필수

---

### 시나리오 3: 여러 프로젝트의 네트워크가 충돌

**상황**: 동시에 여러 프로젝트를 실행하니 포트가 충돌합니다.

```bash
# ❌ 프로젝트 A
docker run -d --name projectA-web -p 80:80 nginx

# ❌ 프로젝트 B
docker run -d --name projectB-web -p 80:80 nginx
# Error: port is already allocated
```

**문제점**:
- 호스트의 80번 포트를 중복 사용
- 프로젝트마다 다른 포트 사용은 관리 복잡

**해결책**:
```bash
# ✅ 리버스 프록시 패턴 사용
# 1. 각 프로젝트 네트워크 생성
docker network create projectA-network
docker network create projectB-network

# 2. 웹 서버는 포트 매핑 없이
docker run -d --name projectA-web \
  --network projectA-network \
  nginx

docker run -d --name projectB-web \
  --network projectB-network \
  nginx

# 3. 하나의 nginx 프록시로 통합
cat > proxy.conf <<EOF
http {
    upstream projectA {
        server projectA-web:80;
    }
    upstream projectB {
        server projectB-web:80;
    }
    server {
        listen 80;
        server_name projecta.local;
        location / { proxy_pass http://projectA; }
    }
    server {
        listen 80;
        server_name projectb.local;
        location / { proxy_pass http://projectB; }
    }
}
EOF

docker run -d --name proxy \
  --network projectA-network \
  -p 80:80 \
  -v $(pwd)/proxy.conf:/etc/nginx/nginx.conf \
  nginx

docker network connect projectB-network proxy

# /etc/hosts에 추가
# 127.0.0.1 projecta.local projectb.local
```

**배운 점**:
- 리버스 프록시로 여러 서비스 통합
- 도메인 이름으로 라우팅
- 프로덕션 환경의 표준 패턴

---

### 시나리오 4: Docker Compose 없이 수동으로 관리하다 실수 연발

**상황**: 10개의 컨테이너를 수동으로 실행하다가 네트워크 연결을 잊어먹었습니다.

```bash
# ❌ 수동 관리의 지옥
docker network create app-net
docker run -d --name db --network app-net postgres
docker run -d --name redis --network app-net redis
docker run -d --name api1 --network app-net myapi
docker run -d --name api2 myapi  # 앗, --network 빠트림!
docker run -d --name frontend --network app-net myfrontend
# ... 5개 더
# api2가 db에 연결 안 됨!
```

**해결책**:
```yaml
# ✅ docker-compose.yml로 자동화
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    networks:
      - backend
    environment:
      POSTGRES_PASSWORD: secret

  redis:
    image: redis:7-alpine
    networks:
      - backend

  api:
    image: myapi:latest
    deploy:
      replicas: 3  # api1, api2, api3 자동 생성
    networks:
      - backend
      - frontend
    depends_on:
      - db
      - redis

  frontend:
    image: myfrontend:latest
    networks:
      - frontend
    ports:
      - "80:80"
    depends_on:
      - api

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # 외부 인터넷 차단
```

```bash
# 한 줄로 전체 실행
docker-compose up -d

# 확인
docker-compose ps
# 모든 네트워크 자동 연결 완료!
```

**배운 점**:
- 수동 관리는 에러 가능성 높음
- Docker Compose로 자동화 필수
- depends_on으로 시작 순서 제어
- 코드로 관리 (Infrastructure as Code)

---

## ❓ FAQ

<details>
<summary><strong>Q1: 기본 브리지 네트워크와 사용자 정의 네트워크의 차이는?</strong></summary>

**A**: 가장 큰 차이는 **DNS 이름 해석 지원 여부**입니다.

**상세 설명**:
- **기본 브리지 (docker0)**: IP 주소로만 통신 가능, 컨테이너 이름 사용 불가
- **사용자 정의 네트워크**: 컨테이너 이름으로 자동 DNS 해석

**예시**:
```bash
# 기본 브리지
docker run -d --name web1 nginx  # 기본 네트워크
docker run -d --name web2 nginx
docker exec web1 ping web2  # ❌ 실패

# 사용자 정의
docker network create mynet
docker run -d --name web3 --network mynet nginx
docker run -d --name web4 --network mynet nginx
docker exec web3 ping web4  # ✅ 성공!
```

**실무 팁**:
프로덕션 환경에서는 무조건 사용자 정의 네트워크를 사용하세요. 기본 브리지는 로컬 테스트용입니다.

</details>

<details>
<summary><strong>Q2: Host 네트워크는 언제 사용하나요?</strong></summary>

**A**: **초고성능이 필요하거나 네트워크 격리가 필요 없는 경우**에만 사용합니다.

**상세 설명**:
- 장점: 네트워크 오버헤드 제로 (NAT 없음), 최고 성능
- 단점: 포트 충돌 가능, 보안 격리 없음, 컨테이너 이식성 떨어짐

**예시**:
```bash
# Host 네트워크 사용
docker run -d --network host nginx
# 컨테이너가 호스트의 80번 포트를 직접 사용
curl http://localhost:80  # 바로 접근

# 성능 비교
# Bridge: 요청 → 호스트 → NAT → 컨테이너 (지연 0.5ms)
# Host: 요청 → 컨테이너 (지연 0.1ms)
```

**실무 팁**:
Prometheus, Grafana 같은 모니터링 도구에 적합합니다. 일반 웹앱에는 권장하지 않습니다.

</details>

<details>
<summary><strong>Q3: 컨테이너가 인터넷 접근을 못 하는 이유는?</strong></summary>

**A**: **IP 포워딩이 비활성화**되었거나 **--internal 네트워크**를 사용 중입니다.

**원인 및 해결**:
```bash
# 원인 1: IP 포워딩 비활성화
cat /proc/sys/net/ipv4/ip_forward  # 0이면 비활성화
sudo sysctl -w net.ipv4.ip_forward=1
sudo systemctl restart docker

# 원인 2: Internal 네트워크 사용
docker network inspect mynetwork | grep Internal
# "Internal": true → 인터넷 차단됨

# 해결: 일반 네트워크로 변경
docker network create public-network  # internal 플래그 없음
docker network connect public-network mycontainer

# 원인 3: 방화벽 규칙 문제
sudo iptables -t nat -L -n | grep MASQUERADE
# 규칙 없으면 Docker 재시작
```

**실무 팁**:
데이터베이스 컨테이너는 의도적으로 --internal 네트워크에 두어 인터넷을 차단합니다.

</details>

<details>
<summary><strong>Q4: 포트 매핑 없이도 외부에서 접근 가능한가요?</strong></summary>

**A**: 가능합니다. **리버스 프록시 패턴**을 사용하면 됩니다.

**방법**:
```bash
# 1. 앱 컨테이너는 포트 매핑 없음
docker network create appnet
docker run -d --name app1 --network appnet myapp:latest
docker run -d --name app2 --network appnet myapp:latest

# 2. Nginx만 포트 80 공개
docker run -d --name proxy \
  --network appnet \
  -p 80:80 \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf \
  nginx

# nginx.conf
# upstream backend {
#     server app1:3000;
#     server app2:3000;
# }
# server {
#     listen 80;
#     location / { proxy_pass http://backend; }
# }
```

**장점**:
- 하나의 포트(80)로 여러 앱 서비스
- SSL/TLS 종료를 프록시에서 처리
- 로드 밸런싱 자동

**실무 팁**:
쿠버네티스의 Ingress Controller도 같은 원리입니다.

</details>

<details>
<summary><strong>Q5: 네트워크 성능을 측정하려면?</strong></summary>

**A**: **iperf3**를 사용하면 네트워크 처리량과 지연 시간을 정확히 측정할 수 있습니다.

**측정 방법**:
```bash
# 네트워크 생성
docker network create perftest

# 서버 컨테이너
docker run -d --name server \
  --network perftest \
  networkstatic/iperf3 -s

# 클라이언트 컨테이너에서 테스트
docker run --rm --network perftest \
  networkstatic/iperf3 -c server

# 출력 예시:
# [ ID] Interval           Transfer     Bitrate
# [  5]   0.00-10.00  sec  11.2 GBytes  9.62 Gbits/sec

# 지연 시간 측정
docker run --rm --network perftest \
  alpine ping -c 10 server
# rtt min/avg/max = 0.1/0.15/0.2 ms
```

**실무 팁**:
- Bridge 네트워크: 약 10 Gbps
- Host 네트워크: 물리 네트워크 속도와 동일
- Overlay 네트워크: 약 5-8 Gbps (VXLAN 오버헤드)

</details>

<details>
<summary><strong>Q6: Overlay 네트워크는 언제 사용하나요?</strong></summary>

**A**: **여러 Docker 호스트**에 걸쳐 컨테이너를 실행할 때 사용합니다.

**사용 시나리오**:
- Docker Swarm 클러스터
- 멀티 호스트 마이크로서비스
- 지역 분산 서비스

**예시**:
```bash
# 호스트 A에서 Swarm 초기화
docker swarm init

# Overlay 네트워크 생성
docker network create --driver overlay --attachable myoverlay

# 서비스 배포 (여러 호스트에 분산)
docker service create \
  --name web \
  --network myoverlay \
  --replicas 10 \
  nginx

# 호스트 A의 컨테이너가 호스트 B의 컨테이너와 통신
# 마치 같은 네트워크에 있는 것처럼!
```

**실무 팁**:
개인 프로젝트나 소규모 팀은 단일 호스트로 충분합니다. Overlay는 대규모 클러스터용입니다.

</details>

<details>
<summary><strong>Q7: 네트워크를 삭제할 수 없는 이유는?</strong></summary>

**A**: **해당 네트워크를 사용 중인 컨테이너**가 있기 때문입니다.

**해결 방법**:
```bash
# 에러 발생
docker network rm mynetwork
# Error: network mynetwork has active endpoints

# 1. 어떤 컨테이너가 사용 중인지 확인
docker network inspect mynetwork | grep Name

# 2. 컨테이너를 다른 네트워크로 이동
docker network disconnect mynetwork container1
docker network disconnect mynetwork container2

# 3. 이제 삭제 가능
docker network rm mynetwork

# 또는 강제 삭제 (컨테이너 중지)
docker rm -f $(docker ps -aq --filter network=mynetwork)
docker network rm mynetwork
```

**실무 팁**:
`docker network prune`으로 사용하지 않는 네트워크를 일괄 삭제할 수 있습니다.

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. Docker 네트워크의 기본 드라이버 종류를 설명해주세요.</strong></summary>

**모범 답안 포인트**
- Bridge: 기본 네트워크, 단일 호스트
- Host: 호스트 네트워크 직접 사용
- None: 네트워크 없음, 완전 격리
- Overlay: 다중 호스트 (Swarm/K8s)
- Macvlan: 컨테이너에 MAC 주소 할당

**예시 답변**
> "Docker 네트워크의 기본 드라이버는 Bridge입니다. Bridge는 단일 호스트에서 컨테이너 간 통신을 제공하며, 사용자 정의 브리지 네트워크는 자동 DNS를 지원합니다. Host 네트워크는 호스트의 네트워크 스택을 직접 사용하여 최고 성능을 제공하지만 격리가 없습니다. Overlay는 Docker Swarm이나 Kubernetes 같은 클러스터 환경에서 여러 호스트 간 통신에 사용됩니다."

**꼬리 질문**
- Q: Bridge와 Host 네트워크의 성능 차이는?
- A: Bridge는 NAT 변환으로 약 0.3-0.5ms 지연, Host는 거의 0ms입니다.

**실무 연관**
로컬 개발은 Bridge, 모니터링 도구는 Host, 프로덕션 클러스터는 Overlay를 사용합니다.

</details>

<details>
<summary><strong>2. 기본 브리지 네트워크와 사용자 정의 브리지 네트워크의 차이는?</strong></summary>

**모범 답안 포인트**
- DNS 자동 해석 지원 여부가 핵심 차이
- 기본 브리지: IP로만 통신, 컨테이너 이름 불가
- 사용자 정의: 컨테이너 이름으로 DNS 자동 해석
- 프로덕션에서는 사용자 정의만 사용

**예시 답변**
> "가장 큰 차이는 DNS 이름 해석입니다. 기본 브리지(docker0)는 IP 주소로만 통신 가능하지만, 사용자 정의 브리지는 컨테이너 이름을 자동으로 DNS 해석합니다. 예를 들어 'ping database'처럼 이름만으로 통신할 수 있습니다. 또한 사용자 정의 네트워크는 동적 연결/해제가 가능하고, 서브넷을 커스터마이징할 수 있습니다."

**꼬리 질문**
- Q: Docker Compose는 어떤 네트워크를 사용하나요?
- A: 자동으로 사용자 정의 브리지 네트워크를 생성합니다.

**실무 연관**
기본 브리지는 레거시 호환성 목적이며, 실무에서는 사용자 정의 네트워크만 사용합니다.

</details>

<details>
<summary><strong>3. 컨테이너 간 통신이 안 될 때 확인할 사항은?</strong></summary>

**모범 답안 포인트**
- 같은 네트워크에 있는지 확인 (docker network inspect)
- 기본 브리지 사용 중이면 DNS 불가
- 방화벽/보안 그룹 설정
- 컨테이너가 실행 중인지 확인

**예시 답변**
> "먼저 두 컨테이너가 같은 네트워크에 있는지 확인합니다. `docker network inspect` 명령으로 확인할 수 있습니다. 기본 브리지 네트워크를 사용 중이면 컨테이너 이름으로 통신할 수 없으므로, 사용자 정의 네트워크를 생성하고 컨테이너를 연결해야 합니다. 또한 `docker exec` 명령으로 컨테이너 내부에서 ping이나 curl로 직접 테스트해볼 수 있습니다."

**꼬리 질문**
- Q: DNS 문제인지 네트워크 문제인지 어떻게 구분하나요?
- A: `ping <IP>` 성공 + `ping <이름>` 실패 = DNS 문제입니다.

**실무 연관**
실무에서 가장 자주 발생하는 문제로, 네트워크 연결 확인이 트러블슈팅의 첫 단계입니다.

</details>

<details>
<summary><strong>4. 포트 매핑(-p)과 포트 노출(EXPOSE)의 차이는?</strong></summary>

**모범 답안 포인트**
- EXPOSE: 문서화 목적, 실제 포트 열지 않음
- -p: 호스트 포트와 컨테이너 포트 매핑
- EXPOSE는 선택사항, -p가 실제 동작

**예시 답변**
> "EXPOSE는 Dockerfile에서 컨테이너가 어떤 포트를 사용하는지 문서화하는 명령어로, 실제로 포트를 열지는 않습니다. 반면 `-p` 플래그는 `docker run` 시 호스트 포트와 컨테이너 포트를 실제로 매핑하여 외부 접근을 가능하게 합니다. 예를 들어 `-p 8080:80`은 호스트의 8080번 포트를 컨테이너의 80번 포트에 연결합니다."

**꼬리 질문**
- Q: -P (대문자) 플래그는 무엇인가요?
- A: EXPOSE된 모든 포트를 호스트의 임의 포트에 자동 매핑합니다.

**실무 연관**
Dockerfile에 EXPOSE를 명시하면 다른 개발자가 어떤 포트를 사용하는지 쉽게 알 수 있습니다.

</details>

<details>
<summary><strong>5. 데이터베이스 컨테이너를 외부에 노출하지 않으려면?</strong></summary>

**모범 답안 포인트**
- 포트 매핑(-p) 사용하지 않음
- --internal 플래그로 인터넷 차단
- 별도의 백엔드 네트워크에 격리

**예시 답변**
> "데이터베이스 컨테이너는 포트 매핑 없이 실행하고, `--internal` 플래그를 사용한 네트워크에 연결합니다. 예를 들어 `docker network create --internal backend`로 네트워크를 만들고, 데이터베이스는 이 네트워크에만 연결합니다. API 서버는 backend 네트워크와 외부 네트워크 양쪽에 연결하여 브리지 역할을 합니다."

**꼬리 질문**
- Q: --internal 네트워크는 어떻게 인터넷을 차단하나요?
- A: iptables NAT 규칙을 생성하지 않아 외부 라우팅이 불가능합니다.

**실무 연관**
실제 보안 사고의 많은 부분이 데이터베이스 노출로 발생하므로, 네트워크 격리는 필수입니다.

</details>

<details>
<summary><strong>6. Docker Compose에서 네트워크는 어떻게 관리되나요?</strong></summary>

**모범 답안 포인트**
- 자동으로 프로젝트명_default 네트워크 생성
- services는 모두 이 네트워크에 자동 연결
- 여러 네트워크를 정의하여 격리 가능

**예시 답변**
> "Docker Compose는 자동으로 `프로젝트명_default` 네트워크를 생성하고, 모든 서비스를 이 네트워크에 연결합니다. 서비스 이름이 DNS로 자동 등록되어 `http://api:3000`처럼 이름만으로 통신할 수 있습니다. networks 섹션에서 여러 네트워크를 정의하면 서비스별로 다른 네트워크에 배치하여 격리할 수 있습니다."

**꼬리 질문**
- Q: 외부 네트워크를 사용하려면?
- A: `external: true` 옵션을 사용하면 됩니다.

**실무 연관**
마이크로서비스 아키텍처에서 Docker Compose의 네트워크 관리는 개발 환경의 핵심입니다.

</details>

<details>
<summary><strong>7. 네트워크 드라이버를 선택하는 기준은?</strong></summary>

**모범 답안 포인트**
- 로컬 개발: Bridge (기본값)
- 성능 중요: Host
- 클러스터: Overlay
- 레거시 시스템: Macvlan

**예시 답변**
> "대부분의 경우 Bridge 네트워크가 적합합니다. 단일 호스트에서 컨테이너 간 통신과 외부 접근을 모두 지원하기 때문입니다. 네트워크 성능이 극도로 중요한 경우(예: 모니터링 도구)는 Host 네트워크를 사용합니다. Docker Swarm이나 Kubernetes 클러스터 환경에서는 Overlay 네트워크를 사용하여 여러 호스트에 걸쳐 통신합니다. Macvlan은 레거시 애플리케이션이 특정 MAC 주소를 요구할 때 사용합니다."

**꼬리 질문**
- Q: None 네트워크는 언제 사용하나요?
- A: 배치 작업이나 보안이 극도로 중요한 데이터 처리 시 사용합니다.

**실무 연관**
프로젝트 요구사항에 따라 적절한 네트워크 드라이버를 선택하는 능력이 중요합니다.

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. Docker 네트워크의 내부 동작 원리를 설명해주세요. (veth, bridge, iptables)</strong></summary>

**모범 답안 포인트**
- veth pair: 가상 이더넷 케이블로 컨테이너와 브리지 연결
- Linux Bridge: 가상 스위치 역할
- iptables: NAT, 포트 포워딩, 방화벽 규칙
- Network Namespace: 격리된 네트워크 스택

**예시 답변**
> "Docker 네트워크는 Linux 커널의 Network Namespace로 각 컨테이너를 격리합니다. 컨테이너마다 veth pair가 생성되어 한쪽 끝은 컨테이너의 eth0에, 다른 한쪽은 호스트의 docker0 브리지에 연결됩니다. docker0는 가상 스위치로 동작하며, iptables 규칙으로 NAT와 포트 포워딩을 구현합니다. 예를 들어 `-p 8080:80`은 iptables DNAT 규칙으로 변환됩니다."

**실무 예시**
```bash
# veth 확인
ip link show | grep veth

# iptables 규칙 확인
sudo iptables -t nat -L -n | grep docker

# 네임스페이스 확인
sudo ip netns list
```

**꼬리 질문**
- Q: veth pair의 성능 오버헤드는?
- A: 약 5-10% 성능 저하가 있지만, 격리의 이점이 더 큽니다.

**실무 연관**
네트워크 장애 시 iptables 규칙을 이해하면 빠른 트러블슈팅이 가능합니다.

</details>

<details>
<summary><strong>2. 마이크로서비스 아키텍처에서 네트워크 보안을 어떻게 설계하시겠습니까?</strong></summary>

**모범 답안 포인트**
- 3-tier 네트워크: frontend, backend, data
- 최소 권한 원칙 적용
- --internal로 인터넷 차단
- TLS/SSL 통신 암호화

**예시 답변**
> "3계층 네트워크 아키텍처를 사용합니다. Frontend 네트워크는 외부 접근이 가능하고 웹/API 게이트웨이만 배치합니다. Backend 네트워크는 내부 통신만 허용하며 마이크로서비스들이 위치합니다. Data 네트워크는 `--internal` 플래그로 완전 격리하여 데이터베이스, 캐시만 배치합니다. API 게이트웨이만 여러 네트워크에 연결하여 브리지 역할을 하며, 서비스 간 통신은 mTLS로 암호화합니다."

**실무 예시**
```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: false
  data:
    driver: bridge
    internal: true  # 인터넷 차단
```

**꼬리 질문**
- Q: Service Mesh(Istio, Linkerd)와의 차이는?
- A: Service Mesh는 네트워크 정책, 트래픽 관리, 관찰성을 추가로 제공합니다.

**실무 연관**
쿠버네티스의 Network Policy도 유사한 개념으로, Docker 네트워크 이해가 기초가 됩니다.

</details>

<details>
<summary><strong>3. 대규모 트래픽 환경에서 네트워크 성능 최적화 방법은?</strong></summary>

**모범 답안 포인트**
- Host 네트워크로 NAT 오버헤드 제거
- MTU 튜닝
- TCP/UDP 파라미터 조정
- 로드 밸런싱 전략

**예시 답변**
> "성능 최적화는 여러 단계로 진행합니다. 첫째, 성능이 극도로 중요한 서비스는 Host 네트워크를 사용하여 NAT 오버헤드를 제거합니다. 둘째, MTU 값을 9000(Jumbo Frame)으로 증가시켜 패킷 오버헤드를 줄입니다. 셋째, `/etc/docker/daemon.json`에서 DNS 서버를 최적화하고, 넷째, Nginx나 HAProxy로 로드 밸런싱하여 부하를 분산합니다. 마지막으로 컨테이너에 CPU/메모리 리소스를 적절히 할당합니다."

**실무 예시**
```json
// /etc/docker/daemon.json
{
  "mtu": 1500,
  "dns": ["8.8.8.8", "1.1.1.1"],
  "default-address-pools": [
    {"base": "172.80.0.0/16", "size": 24}
  ]
}
```

**꼬리 질문**
- Q: MTU를 9000으로 설정할 때 주의사항은?
- A: 전체 네트워크 경로가 Jumbo Frame을 지원해야 하며, 지원하지 않으면 패킷이 드롭됩니다.

**실무 연관**
Netflix는 Host 네트워크와 커스텀 TCP 튜닝으로 초당 수백만 요청을 처리합니다.

</details>

<details>
<summary><strong>4. Overlay 네트워크에서 VXLAN은 어떻게 동작하나요?</strong></summary>

**모범 답안 포인트**
- VXLAN: Virtual Extensible LAN
- UDP 캡슐화로 L2 over L3 구현
- VNI (VXLAN Network Identifier)로 네트워크 구분
- VTEP (VXLAN Tunnel Endpoint)

**예시 답변**
> "VXLAN은 L2 이더넷 프레임을 UDP 패킷으로 캡슐화하여 L3 네트워크 위에서 L2 네트워크를 구현합니다. 각 Docker 호스트는 VTEP 역할을 하며, VNI로 여러 Overlay 네트워크를 구분합니다. 예를 들어 호스트 A의 컨테이너가 호스트 B의 컨테이너로 패킷을 보내면, 호스트 A의 VTEP가 패킷을 UDP로 캡슐화하여 호스트 B로 전송하고, 호스트 B의 VTEP가 디캡슐화하여 컨테이너에 전달합니다."

**실무 예시**
```bash
# VXLAN 인터페이스 확인
ip -d link show | grep vxlan

# VNI 확인
docker network inspect myoverlay | grep VNI
```

**꼬리 질문**
- Q: VXLAN의 성능 오버헤드는?
- A: 캡슐화로 약 10-20% 처리량 감소, 지연 시간 0.5ms 증가합니다.

**실무 연관**
Kubernetes CNI 플러그인(Flannel, Calico)도 VXLAN이나 유사한 기술을 사용합니다.

</details>

<details>
<summary><strong>5. 컨테이너 네트워크 트래픽을 모니터링하고 디버깅하는 방법은?</strong></summary>

**모범 답안 포인트**
- tcpdump로 패킷 캡처
- docker stats로 네트워크 I/O 확인
- Prometheus + cAdvisor로 메트릭 수집
- Wireshark로 패킷 분석

**예시 답변**
> "네트워크 모니터링은 여러 도구를 조합합니다. 실시간 확인은 `docker stats`로 네트워크 I/O를 모니터링합니다. 상세 분석은 `tcpdump`로 컨테이너의 veth 인터페이스에서 패킷을 캡처하고, Wireshark로 분석합니다. 장기 모니터링은 Prometheus와 cAdvisor를 사용하여 네트워크 메트릭을 수집하고, Grafana로 시각화합니다. 문제 발생 시 `docker network inspect`로 네트워크 구성을 확인하고, `docker exec <container> netstat -tunlp`로 포트 리스닝 상태를 체크합니다."

**실무 예시**
```bash
# veth 인터페이스 찾기
CONTAINER_PID=$(docker inspect -f '{{.State.Pid}}' mycontainer)
sudo nsenter -t $CONTAINER_PID -n ip link

# 패킷 캡처
sudo tcpdump -i veth12345 -w capture.pcap

# 네트워크 통계
docker stats --no-stream --format "table {{.Name}}\t{{.NetIO}}"
```

**꼬리 질문**
- Q: 프로덕션 환경에서 tcpdump 사용 시 주의사항은?
- A: CPU 부하가 높으므로 필터를 사용하여 특정 트래픽만 캡처해야 합니다.

**실무 연관**
Datadog, New Relic 같은 APM 도구도 유사한 방식으로 네트워크 메트릭을 수집합니다.

</details>

---

## 📝 핵심 정리

### 이 장에서 배운 핵심 개념

| 개념 | 설명 | 핵심 키워드 |
|------|------|-------------|
| **Bridge 네트워크** | 단일 호스트에서 컨테이너 간 통신 | DNS, 격리, 사용자 정의 |
| **Host 네트워크** | 호스트 네트워크 직접 사용 | 고성능, 격리 없음 |
| **Overlay 네트워크** | 다중 호스트 통신 | VXLAN, Swarm, 클러스터 |
| **DNS 서비스 디스커버리** | 컨테이너 이름으로 자동 연결 | 127.0.0.11, 이름 해석 |
| **포트 매핑** | 호스트 포트를 컨테이너에 연결 | -p, NAT, iptables |
| **네트워크 격리** | 보안을 위한 네트워크 분리 | --internal, 3-tier |
| **리버스 프록시** | 하나의 포트로 여러 서비스 제공 | Nginx, 로드 밸런싱 |

### 필수 명령어 정리

| 명령어 | 용도 | 예시 |
|--------|------|------|
| `docker network create` | 네트워크 생성 | `docker network create mynet` |
| `docker network ls` | 네트워크 목록 | `docker network ls` |
| `docker network inspect` | 네트워크 상세 정보 | `docker network inspect mynet` |
| `docker network connect` | 컨테이너를 네트워크에 연결 | `docker network connect mynet web` |
| `docker network disconnect` | 네트워크 연결 해제 | `docker network disconnect mynet web` |
| `docker network rm` | 네트워크 삭제 | `docker network rm mynet` |
| `docker network prune` | 미사용 네트워크 삭제 | `docker network prune -f` |

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] 사용자 정의 네트워크만 사용 (기본 브리지 금지)
- [ ] 데이터베이스는 --internal 네트워크에 격리
- [ ] 포트는 필요한 것만 최소한으로 공개
- [ ] Docker Compose로 네트워크 자동화
- [ ] 서비스 이름으로 통신 (IP 하드코딩 금지)
- [ ] 3-tier 네트워크 아키텍처 적용
- [ ] TLS/SSL로 통신 암호화

#### ❌ 하지 말아야 할 것
- [ ] 기본 브리지 네트워크에서 프로덕션 실행
- [ ] 데이터베이스 포트를 외부에 노출
- [ ] IP 주소 하드코딩
- [ ] 모든 컨테이너를 하나의 네트워크에 배치
- [ ] 네트워크 없이(--network none) 서비스 실행
- [ ] Host 네트워크를 일반 웹앱에 사용

### 성능/보안 체크리스트

#### 성능
- [ ] Host 네트워크 고려 (모니터링 도구용)
- [ ] MTU 값 최적화
- [ ] DNS 서버 설정 최적화
- [ ] 로드 밸런싱 구현
- [ ] 네트워크 I/O 모니터링

#### 보안
- [ ] 데이터베이스는 --internal 네트워크
- [ ] 최소 권한 원칙 적용
- [ ] 불필요한 포트 닫기
- [ ] TLS/SSL 인증서 적용
- [ ] 방화벽 규칙 설정
- [ ] 네트워크 트래픽 로깅

---

## 🔗 관련 기술

**Docker 네트워크와 함께 사용하는 기술들**

| 기술 | 관계 | 학습 우선순위 |
|------|------|---------------|
| **Docker Compose** | 네트워크 자동 생성/관리 | ⭐⭐⭐ (필수) |
| **Nginx/HAProxy** | 리버스 프록시, 로드 밸런서 | ⭐⭐⭐ (필수) |
| **Kubernetes** | 고급 네트워킹 (CNI) | ⭐⭐ (중급) |
| **Consul/Etcd** | 서비스 디스커버리 | ⭐⭐ (선택) |
| **Prometheus** | 네트워크 모니터링 | ⭐⭐⭐ (권장) |
| **Istio/Linkerd** | Service Mesh | ⭐ (고급) |
| **WireGuard/VPN** | 보안 터널 | ⭐ (선택) |

---

## 🚀 다음 단계

### 다음 장 미리보기: Docker 볼륨 (Section 11)
- **배울 내용 1**: 데이터 영속성과 볼륨 관리
- **배울 내용 2**: Bind Mount vs Named Volume 비교
- **배울 내용 3**: 여러 컨테이너 간 데이터 공유
- **실전 프로젝트**: PostgreSQL 데이터 백업 시스템 구축

### 이 장과의 연결점
```
이번 장: 컨테이너 간 통신 (네트워크)
    ↓
다음 장: 컨테이너 간 데이터 공유 (볼륨)
    ↓
최종 목표: 완전한 마이크로서비스 시스템 구축
```

### 준비하면 좋을 것들
```bash
# 다음 장 실습을 위한 준비
# 1. PostgreSQL 이미지 다운로드
docker pull postgres:15-alpine

# 2. 볼륨 테스트용 디렉터리 생성
mkdir -p ~/docker-volumes-test

# 3. 현재 볼륨 목록 확인
docker volume ls
```

---

## 🎉 축하합니다!

**Docker 네트워크 완전 정복을 완료하셨습니다!**

**이제 여러분은**:
✅ Docker 네트워크의 5가지 드라이버를 이해하고 선택할 수 있습니다
✅ 사용자 정의 네트워크로 안전한 통신 환경을 구축할 수 있습니다
✅ DNS 서비스 디스커버리로 컨테이너 이름만으로 통신할 수 있습니다
✅ 3-tier 네트워크 아키텍처로 보안을 강화할 수 있습니다
✅ 리버스 프록시 패턴으로 여러 서비스를 통합할 수 있습니다
✅ 네트워크 문제를 빠르게 진단하고 해결할 수 있습니다
✅ 프로덕션 수준의 마이크로서비스 네트워크를 설계할 수 있습니다

**다음 단계**:
- [ ] 섹션 11: Docker 볼륨으로 진행
- [ ] 실전 프로젝트: 3-tier 웹 애플리케이션 완성하기
- [ ] 면접 질문 복습 및 답변 연습

**실무 적용 과제**:
1. 현재 프로젝트의 네트워크 구조 점검
2. 기본 브리지 사용 중이면 사용자 정의로 전환
3. 데이터베이스 포트 노출 여부 확인 및 격리
4. Docker Compose로 네트워크 자동화

---

**다음 장으로 이동**: [다음: 11장 Docker 볼륨 →](11-Docker-볼륨.md)

**이전 장으로 돌아가기**: [← 이전: 09장 Docker 컨테이너 관리](09-Docker-컨테이너-관리.md)

**목차로 돌아가기**: [📚 전체 목차](README.md)