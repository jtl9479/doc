# 32. Docker Swarm (오케스트레이션)

> **학습 목표**: Docker Swarm을 사용하여 여러 서버에 컨테이너를 자동으로 배포하고 관리하는 오케스트레이션 시스템을 구축하며, 고가용성 클러스터 운영 방법을 익힐 수 있습니다.

**⏱️ 예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐⭐☆ (4개/5개)

---

## 목차
1. [Docker Swarm 기초](#docker-swarm-기초)
2. [Swarm 초기화 및 노드 관리](#swarm-초기화-및-노드-관리)
3. [Service 생성 및 관리](#service-생성-및-관리)
4. [Docker Stack 배포](#docker-stack-배포)
5. [로드 밸런싱과 스케일링](#로드-밸런싱과-스케일링)
6. [무중단 배포](#무중단-배포)
7. [자가 치유](#자가-치유)
8. [고급 기능](#고급-기능)
9. [모니터링](#모니터링)
10. [실전 배포 예제](#실전-배포-예제)

---

## 💡 왜 Docker Swarm이 필요한가?

### 실무 배경

**"단일 서버에서 운영하다가 서버 한 대가 죽어서 서비스 전체가 다운되었습니다!"**

#### ❌ Docker Compose만 사용하면 발생하는 문제

```
문제 1: 단일 서버 장애 = 전체 서비스 중단
- 증상: 서버 1대 다운 → 모든 컨테이너 중단
- 영향: 완전한 서비스 다운타임
- 비용: 1시간 다운타임 = 약 500만원 손실 (쇼핑몰 기준)

문제 2: 트래픽 급증 시 스케일 불가
- 증상: "접속자가 너무 많아 서버가 느려요!"
- 대응: 서버 증설해도 수동으로 재설정 필요
- 영향: 기회 손실 (블랙프라이데이, 이벤트 기간)
- 비용: 매출 기회 손실 시간당 1,000만원

문제 3: 무중단 배포 불가능
- 증상: 배포할 때마다 서비스 중단
- 대응: 새벽 배포 (개발자 야근)
- 영향: 사용자 불만, 개발자 피로도 증가
- 비용: 야간 작업 수당 + 기회 손실
```

#### ✅ Docker Swarm을 사용하면

```
해결책 1: 고가용성 (High Availability)
- 방법: 여러 서버에 컨테이너 분산 배치
- 효과: 서버 1대 다운되어도 서비스 지속
- 절감: 다운타임 99% 감소 (연간 수억원 절감)

해결책 2: 자동 스케일링과 로드 밸런싱
- 방법: 트래픽에 따라 컨테이너 수 자동 조절
- 효과: 피크 타임 대응, 리소스 효율화
- 절감: 서버 비용 30% 절감 + 기회 손실 방지

해결책 3: 무중단 롤링 업데이트
- 방법: 한 대씩 순차적으로 업데이트
- 효과: 배포 중에도 서비스 지속
- 절감: 야간 작업 불필요, 개발자 삶의 질 향상 🎉
```

### 수치로 보는 효과

| 지표 | Before (Compose) | After (Swarm) | 개선율 |
|------|-----------------|---------------|--------|
| 서비스 가용성 | 95% | 99.9% | **5%↑** |
| 다운타임 (연간) | 18일 | 9시간 | **99.5%↓** |
| 배포 시간 | 30분 | 5분 | **83%↓** |
| 트래픽 피크 대응 | 수동 | 자동 | **100%↑** |
| 운영 인력 | 3명 | 1명 | **67%↓** |

---

## 🔍 실생활 비유로 이해하기

### 비유 1: 오케스트라 지휘자

```
오케스트라                           Docker Swarm
=========                           ============
🎼 악보                         →    docker-compose.yml
🎻 바이올린 주자들              →    컨테이너 레플리카
🎺 트럼펫 주자들                →    다른 서비스
👔 지휘자                       →    Swarm Manager
🎭 무대 (여러 개)               →    Worker Nodes
📊 악보 배치                    →    서비스 스케줄링
🔁 연주자 교체                  →    롤링 업데이트
🚨 연주자 부상 시 백업 투입     →    자가 치유

지휘자 없이 100명이 연주하면:
- 타이밍 엇박자
- 일부 악기 너무 크게
- 누가 언제 연주할지 모름

지휘자가 있으면:
- 완벽한 하모니
- 균형 잡힌 볼륨
- 연주자 교체도 자연스럽게
```

### 비유 2: 택배 물류 센터

```
물류 센터 시스템              Docker Swarm
================              =============
📦 택배 상자                  →    컨테이너
🚚 배송 트럭                  →    Worker Node
🎯 관제 센터                  →    Manager Node
📱 실시간 추적 시스템         →    모니터링
🔄 자동 분류기                →    Scheduler
⚖️ 부하 분산                  →    Load Balancer

택배가 몰릴 때:
- 자동으로 분류 라인 추가 (스케일 아웃)
- 고장난 트럭 → 다른 트럭으로 자동 배정
- 실시간 배송 경로 최적화
```

### 비유 3: 레스토랑 체인

```
레스토랑 체인점              Docker Swarm
==============              =============
👨‍🍳 요리사                  →    컨테이너 인스턴스
🏢 지점                     →    Worker Node
📞 본사                     →    Manager Node
📋 표준 레시피              →    Service 정의
🔄 교대 근무                →    롤링 업데이트
🚨 요리사 아플 때 대체      →    자가 치유

단일 레스토랑의 문제:
- 요리사 아프면 → 영업 중단
- 손님 몰리면 → 대기 시간 증가
- 리모델링 → 휴업 필수

체인점의 장점:
- 한 지점 문제 → 다른 지점 이용 가능
- 손님 분산 → 효율적 서빙
- 순차적 리모델링 → 무중단 운영
```

---

## Docker Swarm 기초

### 핵심 개념

```
Swarm 아키텍처
==============

┌───────────────────────────────────────────────────────────┐
│                    Control Plane                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │  kube-apiserver                                  │    │
│  │  (모든 요청의 중앙 허브)                        │    │
│  └──────────────────────────────────────────────────┘    │
│         │                │               │                │
│         ↓                ↓               ↓                │
│  ┌──────────┐    ┌─────────────┐   ┌──────────────┐    │
│  │  etcd    │    │  Scheduler  │   │  Controller  │    │
│  │ (상태DB) │    │  (배치결정) │   │   Manager    │    │
│  └──────────┘    └─────────────┘   └──────────────┘    │
└───────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼──────┐   ┌───────▼──────┐   ┌───────▼──────┐
│  Worker 1    │   │  Worker 2    │   │  Worker 3    │
│ ┌──────────┐ │   │ ┌──────────┐ │   │ ┌──────────┐ │
│ │Task Task │ │   │ │Task Task │ │   │ │Task Task │ │
│ │  Task    │ │   │ │  Task    │ │   │ │  Task    │ │
│ └──────────┘ │   │ └──────────┘ │   │ └──────────┘ │
└──────────────┘   └──────────────┘   └──────────────┘

용어:
- Node: Swarm에 참여하는 Docker 엔진 인스턴스
- Manager Node: 클러스터 상태 관리, 스케줄링 결정
- Worker Node: 컨테이너 실행
- Service: 스웜에서 실행되는 애플리케이션 정의
- Task: Service의 개별 컨테이너 인스턴스
- Stack: 여러 Service의 그룹
```

### Docker Swarm vs Kubernetes

```
┌─────────────────────┬─────────────────┬──────────────────┐
│ 특징                │ Docker Swarm    │ Kubernetes       │
├─────────────────────┼─────────────────┼──────────────────┤
│ 복잡도              │ 낮음 ⭐         │ 높음 ⭐⭐⭐⭐    │
│ 러닝 커브           │ 쉬움            │ 어려움           │
│ 설정                │ 간단            │ 복잡             │
│ 생태계              │ 작음            │ 매우 큼          │
│ 기능                │ 기본적          │ 매우 풍부        │
│ 소규모 프로젝트     │ 적합 ✅         │ 과함             │
│ 대규모 프로젝트     │ 부족            │ 적합 ✅          │
│ Docker 통합         │ 완벽            │ 별도 도구        │
│ 멀티 클라우드       │ 제한적          │ 우수             │
└─────────────────────┴─────────────────┴──────────────────┘

Docker Swarm을 선택하는 경우:
- 소~중규모 프로젝트
- 빠른 시작 필요
- Docker Compose에서 마이그레이션
- 팀의 Kubernetes 경험 부족
- 복잡성 최소화

Kubernetes를 선택하는 경우:
- 대규모 프로젝트
- 복잡한 요구사항
- 멀티 클라우드
- 풍부한 생태계 필요
```

---

## Swarm 초기화 및 노드 관리

### 1. Swarm 초기화

```bash
# Manager 노드에서 Swarm 초기화
docker swarm init --advertise-addr 192.168.1.10

# 출력:
Swarm initialized: current node (abc123xyz) is now a manager.

To add a worker to this swarm, run the following command:

    docker swarm join --token SWMTKN-1-xxx... 192.168.1.10:2377

To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.

# Swarm 상태 확인
docker info | grep Swarm
# Swarm: active

# 노드 목록 확인
docker node ls

# 출력:
ID                            HOSTNAME   STATUS    AVAILABILITY   MANAGER STATUS
abc123xyz *                   manager1   Ready     Active         Leader
```

### 2. Worker 노드 추가

```bash
# Worker 서버에서 실행
docker swarm join --token SWMTKN-1-xxx... 192.168.1.10:2377

# Manager 노드에서 확인
docker node ls

# 출력:
ID                            HOSTNAME   STATUS    AVAILABILITY   MANAGER STATUS
abc123xyz *                   manager1   Ready     Active         Leader
def456abc                     worker1    Ready     Active
ghi789def                     worker2    Ready     Active
```

### 3. 추가 Manager 노드 추가 (HA)

```bash
# Manager 노드에서 토큰 확인
docker swarm join-token manager

# 출력:
To add a manager to this swarm, run the following command:

    docker swarm join --token SWMTKN-1-yyy... 192.168.1.10:2377

# 새 Manager 서버에서 실행
docker swarm join --token SWMTKN-1-yyy... 192.168.1.10:2377

# 확인
docker node ls

# 출력:
ID                            HOSTNAME   STATUS    AVAILABILITY   MANAGER STATUS
abc123xyz *                   manager1   Ready     Active         Leader
def456abc                     worker1    Ready     Active
ghi789def                     worker2    Ready     Active
jkl012ghi                     manager2   Ready     Active         Reachable
```

---

## Service 생성 및 관리

### 1. 간단한 Service 생성

```bash
# Nginx 서비스 생성 (3개 레플리카)
docker service create \
  --name web \
  --replicas 3 \
  --publish 80:80 \
  nginx:alpine

# 서비스 목록 확인
docker service ls

# 출력:
ID             NAME   MODE         REPLICAS   IMAGE          PORTS
abc123xyz      web    replicated   3/3        nginx:alpine   *:80->80/tcp

# 서비스 상세 정보
docker service ps web

# 출력:
ID             NAME      IMAGE          NODE       DESIRED STATE   CURRENT STATE
abc123         web.1     nginx:alpine   manager1   Running         Running 30 seconds ago
def456         web.2     nginx:alpine   worker1    Running         Running 30 seconds ago
ghi789         web.3     nginx:alpine   worker2    Running         Running 30 seconds ago
```

### 2. Service 스케일링

```bash
# 5개로 스케일 업
docker service scale web=5

# 출력:
web scaled to 5
overall progress: 5 out of 5 tasks
1/5: running   [==================================================>]
2/5: running   [==================================================>]
3/5: running   [==================================================>]
4/5: running   [==================================================>]
5/5: running   [==================================================>]
verify: Service converged

# 확인
docker service ls
# REPLICAS: 5/5

# 스케일 다운
docker service scale web=2
```

### 3. Service 업데이트

```bash
# 이미지 업데이트 (롤링 업데이트)
docker service update \
  --image nginx:1.21 \
  --update-parallelism 1 \
  --update-delay 10s \
  web

# 실시간 진행 상황 확인
watch -n 1 'docker service ps web'

# 업데이트 롤백
docker service rollback web
```

---

## Docker Stack 배포

### 1. docker-compose.yml을 Stack으로 배포

```yaml
# docker-stack.yml
version: '3.8'

services:
  # User Service
  user-service:
    image: lk-trade/user-service:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      rollback_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      placement:
        constraints:
          - node.role == worker
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    networks:
      - lk-trade-network
    secrets:
      - db_password
      - jwt_secret
    environment:
      - SPRING_PROFILES_ACTIVE=prod
      - DB_PASSWORD_FILE=/run/secrets/db_password
    healthcheck:
      test: ["CMD", "wget", "--spider", "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 3s
      retries: 3

  # PostgreSQL (단일 인스턴스, Manager에 배치)
  postgres:
    image: postgres:16-alpine
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
      restart_policy:
        condition: on-failure
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - lk-trade-network
    secrets:
      - db_password
    environment:
      - POSTGRES_DB=lk_trade
      - POSTGRES_USER=lk_admin
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password

  # Visualizer (Swarm 시각화 도구)
  visualizer:
    image: dockersamples/visualizer:latest
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
    ports:
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - lk-trade-network

volumes:
  postgres-data:

networks:
  lk-trade-network:
    driver: overlay
    attachable: true

secrets:
  db_password:
    external: true
  jwt_secret:
    external: true
```

### 2. Secret 생성

```bash
# Secret 파일 생성
echo "super_secure_db_password" | docker secret create db_password -
echo "jwt_secret_key_here" | docker secret create jwt_secret -

# Secret 목록 확인
docker secret ls

# 출력:
ID                          NAME           CREATED          UPDATED
abc123xyz                   db_password    10 seconds ago   10 seconds ago
def456abc                   jwt_secret     5 seconds ago    5 seconds ago
```

### 3. Stack 배포

```bash
# Stack 배포
docker stack deploy -c docker-stack.yml lk-trade

# 출력:
Creating network lk-trade_lk-trade-network
Creating service lk-trade_user-service
Creating service lk-trade_postgres
Creating service lk-trade_visualizer

# Stack 목록 확인
docker stack ls

# 출력:
NAME       SERVICES   ORCHESTRATOR
lk-trade   3          Swarm

# Stack의 서비스 확인
docker stack services lk-trade

# Stack 삭제
docker stack rm lk-trade
```

---

## 로드 밸런싱과 스케일링

### Ingress Load Balancing

```
Ingress Load Balancing (기본)
==============================

외부 요청 → 80:80
              ↓
    Swarm Ingress Network
       (자동 로드 밸런싱)
         /    |    \
        /     |     \
    Node1  Node2  Node3
    ┌───┐  ┌───┐  ┌───┐
    │web│  │web│  │web│
    └───┘  └───┘  └───┘

→ 어느 노드로 요청해도 자동으로 분산
→ Round-robin 방식
```

```bash
# 로드 밸런싱 테스트
for i in {1..10}; do
    curl http://localhost/
done

# 각 컨테이너에서 응답 확인
docker service logs lk-trade_user-service
```

---

## 무중단 배포

### 롤링 업데이트 설정

```yaml
services:
  user-service:
    deploy:
      update_config:
        parallelism: 1        # 한 번에 1개씩 업데이트
        delay: 10s            # 각 업데이트 사이 10초 대기
        failure_action: rollback  # 실패 시 롤백
        monitor: 60s          # 60초 동안 모니터링
        max_failure_ratio: 0.3    # 30% 실패 시 중단
        order: stop-first     # 기존 컨테이너 중지 후 새 컨테이너 시작
```

### 롤링 업데이트 실행

```bash
# 이미지 업데이트
docker service update \
  --image lk-trade/user-service:2.0.0 \
  lk-trade_user-service

# 실시간 진행 상황 확인
watch -n 1 'docker service ps lk-trade_user-service'

# 수동 롤백
docker service rollback lk-trade_user-service
```

---

## 자가 치유

### 1. 컨테이너 장애 시 자동 재시작

```bash
# 테스트: 컨테이너 강제 종료
docker ps | grep user-service
# abc123  lk-trade/user-service...

docker kill abc123

# Swarm이 자동으로 새 컨테이너 시작
docker service ps lk-trade_user-service

# 출력:
ID             NAME                       NODE      CURRENT STATE
def456         lk-trade_user-service.1    worker1   Running 5 seconds ago
abc123          \_ lk-trade_user-service.1 worker1   Shutdown 10 seconds ago
```

### 2. 노드 장애 시 자동 재배치

```bash
# 노드 다운 시뮬레이션
# Worker1에서:
sudo systemctl stop docker

# Manager에서 확인
docker node ls

# 출력:
ID             HOSTNAME   STATUS    AVAILABILITY   MANAGER STATUS
abc123         manager1   Ready     Active         Leader
def456         worker1    Down      Active         ← Down!
ghi789         worker2    Ready     Active

# Worker1에 있던 Task들이 자동으로 다른 노드로 이동
docker service ps lk-trade_user-service
```

### 3. 노드 유지보수 모드

```bash
# Worker1을 유지보수 모드로 전환
docker node update --availability drain worker1

# Worker1의 모든 Task가 다른 노드로 이동
docker node ps worker1

# 유지보수 완료 후 다시 활성화
docker node update --availability active worker1
```

---

## 고급 기능

### 배치 제약 조건 (Placement Constraints)

```yaml
services:
  # Manager 노드에만 배치
  postgres:
    deploy:
      placement:
        constraints:
          - node.role == manager

  # Worker 노드에만 배치
  web:
    deploy:
      placement:
        constraints:
          - node.role == worker

  # 특정 레이블을 가진 노드에 배치
  database:
    deploy:
      placement:
        constraints:
          - node.labels.type == database
```

```bash
# 노드에 레이블 추가
docker node update --label-add type=database worker1
docker node update --label-add zone=asia worker2
docker node update --label-add ssd=true worker3
```

---

## 모니터링

### Visualizer로 실시간 시각화

```bash
# Visualizer 접속
http://localhost:8080

# 화면에 표시되는 정보:
- 각 노드의 상태
- 실행 중인 컨테이너
- 컨테이너 배치 상태
- 실시간 업데이트
```

### 명령어로 모니터링

```bash
# 노드 상태 확인
docker node ls

# 서비스 상태 확인
docker service ls

# 특정 서비스의 Task 확인
docker service ps lk-trade_user-service

# 서비스 로그 확인
docker service logs -f lk-trade_user-service

# 서비스 상세 정보
docker service inspect lk-trade_user-service --pretty
```

---

## 👨‍💻 주니어 개발자 시나리오

### 시나리오 1: 첫 Swarm 클러스터 구축 - "어떻게 시작하죠?"

**상황**:
```
팀장: "우리 서비스 Docker Swarm으로 전환해봐요. 서버 3대 있어요."
주니어 A (당황): "Docker는 알겠는데 Swarm은 뭐죠?"
```

**단계별 해결**:
```bash
# Step 1: 첫 번째 서버를 Manager로 초기화
$ ssh manager1
$ docker swarm init --advertise-addr 192.168.1.10

# 토큰이 나옴 (복사해두기!)
To add a worker to this swarm, run:
    docker swarm join --token SWMTKN-1-xxx... 192.168.1.10:2377

# Step 2: 두 번째 서버를 Worker로 추가
$ ssh worker1
$ docker swarm join --token SWMTKN-1-xxx... 192.168.1.10:2377
This node joined a swarm as a worker.

# Step 3: 세 번째 서버도 Worker로 추가
$ ssh worker2
$ docker swarm join --token SWMTKN-1-xxx... 192.168.1.10:2377

# Step 4: Manager에서 확인
$ ssh manager1
$ docker node ls

# 출력:
ID                            HOSTNAME   STATUS    AVAILABILITY   MANAGER STATUS
abc123xyz *                   manager1   Ready     Active         Leader
def456abc                     worker1    Ready     Active
ghi789def                     worker2    Ready     Active

✅ 클러스터 구축 완료!

# Step 5: 첫 서비스 배포
$ docker service create --name web --replicas 3 -p 80:80 nginx:alpine

# Step 6: 어느 서버에서든 접속
$ curl http://192.168.1.10
$ curl http://192.168.1.11  # Worker1
$ curl http://192.168.1.12  # Worker2
# 모두 동일하게 응답! (Ingress 네트워킹)
```

**배운 점**:
- Swarm 초기화는 `docker swarm init` 한 줄
- Worker 추가는 토큰으로 간단히 join
- 어느 노드로 요청해도 자동 로드 밸런싱
- `docker-compose`랑 비슷하지만 여러 서버에 분산

---

### 시나리오 2: 서버 한 대 죽었는데 서비스는 살아있음

**상황**:
```
주니어 B: "Worker1 서버가 꺼졌는데 서비스가 멀쩡해요! 신기해요!"
시니어: "그게 바로 자가 치유(Self-healing)죠."
```

**단계별 확인**:
```bash
# Step 1: 현재 상태 확인
$ docker service ps user-service

# 출력:
ID             NAME               NODE      CURRENT STATE
abc123         user-service.1     manager1  Running
def456         user-service.2     worker1   Running
ghi789         user-service.3     worker2   Running

# Step 2: Worker1 서버 장애 시뮬레이션
$ ssh worker1
$ sudo systemctl stop docker

# Step 3: Manager에서 확인
$ docker node ls

# 출력:
ID             HOSTNAME   STATUS    AVAILABILITY   MANAGER STATUS
abc123xyz      manager1   Ready     Active         Leader
def456abc      worker1    Down      Active         ← Down!
ghi789def      worker2    Ready     Active

# Step 4: 서비스 상태 확인
$ docker service ps user-service

# 출력:
ID             NAME                 NODE      CURRENT STATE
abc123         user-service.1       manager1  Running
ghi789         user-service.3       worker2   Running
jkl012         user-service.2       manager1  Running 30 seconds ago
def456          \_ user-service.2    worker1   Shutdown 35 seconds ago

# Worker1에 있던 Task가 자동으로 Manager로 이동!

# Step 5: 서비스 테스트
$ curl http://localhost/api/users
# 정상 응답! 서비스 중단 없음

✅ 자가 치유 확인 완료!

# Step 6: Worker1 복구
$ ssh worker1
$ sudo systemctl start docker

# 자동으로 Swarm에 재가입
$ docker node ls
# worker1이 다시 Ready 상태
```

**배운 점**:
- 노드가 죽어도 다른 노드로 자동 재배치
- 서비스 중단 없음 (고가용성)
- 복구되면 자동으로 다시 참여
- 이게 바로 Swarm의 핵심 가치!

---

### 시나리오 3: 무중단 배포 - "배포했는데 서비스가 안 멈췄어요!"

**상황**:
```
주니어 C: "새 버전 배포했는데 사용자들이 그대로 사용 중이에요. 마법인가요?"
시니어: "롤링 업데이트죠. Swarm의 킬러 기능입니다."
```

**단계별 해결**:
```bash
# Step 1: 현재 버전 확인
$ docker service ps user-service

# 출력:
ID             NAME               IMAGE                         NODE
abc123         user-service.1     lk-trade/user-service:1.0.0   manager1
def456         user-service.2     lk-trade/user-service:1.0.0   worker1
ghi789         user-service.3     lk-trade/user-service:1.0.0   worker2

# Step 2: 새 버전으로 업데이트 (v2.0.0)
$ docker service update \
    --image lk-trade/user-service:2.0.0 \
    --update-parallelism 1 \
    --update-delay 10s \
    user-service

# Step 3: 실시간 진행 상황 확인
$ watch -n 1 'docker service ps user-service'

# 시간 경과에 따른 변화:
# 10초: user-service.1 업데이트 중
ID             NAME                 IMAGE       NODE      CURRENT STATE
jkl012         user-service.1       v2.0.0      manager1  Running
abc123          \_ user-service.1    v1.0.0      manager1  Shutdown
def456         user-service.2       v1.0.0      worker1   Running
ghi789         user-service.3       v1.0.0      worker2   Running

# 20초: user-service.2 업데이트 중
ID             NAME                 IMAGE       NODE      CURRENT STATE
jkl012         user-service.1       v2.0.0      manager1  Running
mno345         user-service.2       v2.0.0      worker1   Running
def456          \_ user-service.2    v1.0.0      worker1   Shutdown
ghi789         user-service.3       v1.0.0      worker2   Running

# 30초: 모두 완료
ID             NAME                 IMAGE       NODE      CURRENT STATE
jkl012         user-service.1       v2.0.0      manager1  Running
mno345         user-service.2       v2.0.0      worker1   Running
pqr678         user-service.3       v2.0.0      worker2   Running

✅ 무중단 업데이트 완료!

# Step 4: 문제 발생 시 롤백
$ docker service update \
    --rollback \
    user-service

# 자동으로 이전 버전(v1.0.0)으로 복구
```

**배운 점**:
- 한 번에 1개씩 순차적으로 업데이트
- 업데이트 중에도 서비스 지속 (2/3 또는 3/3 항상 실행 중)
- 문제 생기면 `--rollback`으로 즉시 복구
- 새벽 배포 필요 없음! 언제든지 배포 가능

---

### 시나리오 4: Compose에서 Swarm으로 마이그레이션

**상황**:
```
주니어 D: "기존 docker-compose.yml이 있는데 Swarm에서도 쓸 수 있나요?"
시니어: "거의 그대로 사용 가능합니다. 몇 가지만 추가하면 돼요."
```

**단계별 해결**:
```yaml
# 기존 docker-compose.yml
version: '3.8'

services:
  user-service:
    image: lk-trade/user-service:latest
    ports:
      - "8080:8080"
    environment:
      - DB_HOST=postgres

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_PASSWORD=mysecret

# ↓ Swarm용으로 변환 (docker-stack.yml)

version: '3.8'

services:
  user-service:
    image: lk-trade/user-service:latest
    deploy:              # 추가: deploy 섹션
      replicas: 3        # 추가: 레플리카 수
      update_config:     # 추가: 업데이트 설정
        parallelism: 1
        delay: 10s
      restart_policy:    # 추가: 재시작 정책
        condition: on-failure
    ports:
      - "8080:8080"
    environment:
      - DB_HOST=postgres

  postgres:
    image: postgres:16-alpine
    deploy:
      replicas: 1
      placement:          # 추가: Manager에만 배치
        constraints:
          - node.role == manager
    volumes:
      - postgres-data:/var/lib/postgresql/data
    secrets:              # 변경: 환경 변수 → Secret
      - db_password
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password

volumes:
  postgres-data:

secrets:
  db_password:
    external: true
```

```bash
# Step 1: Secret 생성
$ echo "mysecret" | docker secret create db_password -

# Step 2: Stack 배포
$ docker stack deploy -c docker-stack.yml myapp

# Step 3: 확인
$ docker stack services myapp

# 출력:
ID             NAME               MODE         REPLICAS   IMAGE
abc123         myapp_user-service replicated   3/3        lk-trade/user-service:latest
def456         myapp_postgres     replicated   1/1        postgres:16-alpine

✅ 마이그레이션 완료!
```

**배운 점**:
- `docker-compose.yml` 대부분 재사용 가능
- `deploy` 섹션만 추가하면 됨
- `build`는 사용 불가 (미리 빌드된 이미지 사용)
- Secret으로 보안 강화

---

## ❓ FAQ

<details>
<summary><strong>Q1: Docker Swarm과 Kubernetes 중 어떤 걸 선택해야 하나요?</strong></summary>

**A**: 프로젝트 규모와 팀 상황에 따라 다릅니다.

**Docker Swarm을 선택하세요**:
```
✅ 적합한 경우:
- 소~중규모 프로젝트 (서비스 50개 이하)
- Docker Compose에서 마이그레이션
- 빠른 시작이 필요 (1일 내 구축 가능)
- 팀에 Kubernetes 경험자 없음
- 복잡성 최소화 원함

실제 사례:
스타트업 A사 (서비스 20개, 노드 10개)
- Swarm 도입 후 3일 만에 운영 시작
- 운영 인력 1명으로 충분
- 문제 발생 시 빠른 디버깅
```

**Kubernetes를 선택하세요**:
```
✅ 적합한 경우:
- 대규모 프로젝트 (서비스 100개 이상)
- 멀티 클라우드 (AWS, GCP, Azure)
- 복잡한 네트워킹 요구사항
- 풍부한 생태계 필요 (Helm, Operators, etc)
- 장기적 확장성 고려

실제 사례:
엔터프라이즈 B사 (서비스 200개, 노드 100개)
- Kubernetes로 복잡한 워크플로우 구현
- Helm으로 배포 자동화
- Istio로 서비스 메시 구축
```

**비교표**:

| 항목 | Docker Swarm | Kubernetes |
|------|-------------|------------|
| 학습 기간 | 1-3일 | 1-3개월 |
| 설정 복잡도 | 낮음 | 높음 |
| 기능 풍부함 | 기본적 | 매우 풍부 |
| 커뮤니티 | 작음 | 매우 큼 |
| 채용 | 어려움 | 쉬움 (인기 높음) |

**실용적 조언**:
- 처음 시작: Swarm으로 시작 → 필요하면 K8s 전환
- 이미 K8s 경험: 바로 K8s 사용
- 두 가지 모두 학습: Swarm 먼저 (K8s 개념 이해에 도움)

</details>

<details>
<summary><strong>Q2: Swarm Mode에서 데이터베이스는 어떻게 관리하나요?</strong></summary>

**A**: **StatefulSet 대신 단일 레플리카 + 볼륨 사용**을 권장합니다.

**상세 설명**:

**문제점**:
```
Docker Swarm은 Kubernetes의 StatefulSet 같은
Stateful 애플리케이션 전용 리소스가 없음
→ 데이터베이스 클러스터링 어려움
```

**권장 방법 1: 단일 레플리카 + Named Volume**
```yaml
services:
  postgres:
    image: postgres:16-alpine
    deploy:
      replicas: 1  # 단일 인스턴스
      placement:
        constraints:
          - node.role == manager  # Manager 노드 고정
    volumes:
      - postgres-data:/var/lib/postgresql/data
    secrets:
      - db_password
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password

volumes:
  postgres-data:  # Named volume (노드에 고정됨)
```

**장점**:
- 간단한 설정
- 데이터 유실 걱정 없음
- 소~중규모에 충분

**단점**:
- 해당 노드 다운 시 DB 중단 (복구 필요)

**권장 방법 2: 외부 데이터베이스 사용 (프로덕션)**
```yaml
services:
  user-service:
    environment:
      - DB_HOST=rds.amazonaws.com  # 외부 DB
      - DB_PORT=5432

# PostgreSQL은 Swarm 외부에서 관리
# - AWS RDS
# - Google Cloud SQL
# - Azure Database for PostgreSQL
# - 또는 전용 DB 서버
```

**장점**:
- 고가용성 (클라우드 제공)
- 자동 백업
- 관리 부담 감소
- Swarm과 독립적

**권장 방법 3: 데이터베이스 클러스터링 (고급)**
```yaml
# Patroni + etcd로 PostgreSQL HA 구성
services:
  postgres-master:
    image: patroni:latest
    # ... 복잡한 설정

  postgres-replica:
    image: patroni:latest
    # ... 복잡한 설정

# 주의: 복잡도 매우 높음
# Kubernetes + Operators 사용이 더 나을 수 있음
```

**실전 가이드**:
```bash
# 개발/스테이징: 단일 레플리카 OK
deploy:
  replicas: 1

# 프로덕션: 외부 DB 사용 권장
- AWS RDS (관리형)
- 또는 전용 DB 클러스터 구축
```

**백업 전략**:
```bash
# 정기 백업 스크립트 (cron)
#!/bin/bash
# backup-db.sh

docker exec postgres-container pg_dump -U postgres lk_trade > backup-$(date +%Y%m%d).sql

# S3로 업로드
aws s3 cp backup-$(date +%Y%m%d).sql s3://my-backups/
```

</details>

<details>
<summary><strong>Q3: Swarm에서 Secret과 Config의 차이는 무엇인가요?</strong></summary>

**A**: **Secret은 암호화되고, Config는 암호화 안 됨**입니다.

**상세 설명**:

**Secret (비밀 정보)**:
```bash
# 특징:
- 암호화되어 저장 (TLS)
- Manager 노드에만 저장
- 필요한 컨테이너에만 전달
- 파일로 마운트 (/run/secrets/<name>)

# 사용 예:
echo "super_secure_password" | docker secret create db_password -

# YAML:
services:
  app:
    secrets:
      - db_password
    environment:
      - DB_PASSWORD_FILE=/run/secrets/db_password

secrets:
  db_password:
    external: true

# 읽는 방법 (컨테이너 내부):
cat /run/secrets/db_password
# super_secure_password
```

**Config (설정 파일)**:
```bash
# 특징:
- 암호화 안 됨 (평문)
- 모든 노드에 복제
- 파일로 마운트
- 버전 관리 가능

# 사용 예:
docker config create nginx_config nginx.conf

# YAML:
services:
  nginx:
    configs:
      - source: nginx_config
        target: /etc/nginx/nginx.conf

configs:
  nginx_config:
    external: true

# 읽는 방법 (컨테이너 내부):
cat /etc/nginx/nginx.conf
```

**비교표**:

| 항목 | Secret | Config |
|------|--------|--------|
| 암호화 | ✅ Yes | ❌ No |
| 용도 | 비밀번호, 키 | 설정 파일 |
| 저장 위치 | Manager만 | 모든 노드 |
| 마운트 경로 | /run/secrets/ | 임의 |
| 환경 변수 | 간접 사용 | 직접 사용 |

**사용 가이드**:

**Secret 사용 (민감 정보)**:
```
✅ 데이터베이스 비밀번호
✅ API 키
✅ JWT Secret
✅ TLS 인증서/키
✅ SSH 키
```

**Config 사용 (일반 설정)**:
```
✅ Nginx 설정 파일
✅ 애플리케이션 설정
✅ 로깅 설정
✅ 환경별 설정 (dev/prod)
```

**실전 예제**:
```yaml
version: '3.8'

services:
  app:
    image: myapp:latest
    # Secret 사용
    secrets:
      - db_password
      - jwt_secret
    environment:
      - DB_PASSWORD_FILE=/run/secrets/db_password
      - JWT_SECRET_FILE=/run/secrets/jwt_secret

    # Config 사용
    configs:
      - source: app_config
        target: /app/config.yml
      - source: logging_config
        target: /app/logging.yml

secrets:
  db_password:
    external: true
  jwt_secret:
    external: true

configs:
  app_config:
    file: ./config/application.yml
  logging_config:
    file: ./config/logging.yml
```

**보안 베스트 프랙티스**:
```bash
# ❌ 나쁜 예: 환경 변수에 직접
environment:
  - DB_PASSWORD=mysecret  # 로그에 노출 위험!

# ✅ 좋은 예: Secret 파일 사용
secrets:
  - db_password
environment:
  - DB_PASSWORD_FILE=/run/secrets/db_password

# 애플리케이션 코드:
val password = File("/run/secrets/db_password").readText()
```

</details>

<details>
<summary><strong>Q4: Swarm 노드가 다운되면 어떻게 되나요?</strong></summary>

**A**: **Manager냐 Worker냐에 따라 다르게 동작**합니다.

**상세 설명**:

**Worker 노드 다운**:
```
시나리오:
3개 노드 (Manager 1, Worker 2)
User-Service 레플리카 3개 (각 노드에 1개씩)

Worker1 다운 ↓

1. Swarm Manager가 감지 (수초 이내)
2. Worker1의 Task를 다른 노드로 재배치
3. 서비스 중단 없음 (2/3 → 3/3으로 복구)

┌──────────┐   ┌──────────┐   ┌──────────┐
│ Manager  │   │ Worker1  │   │ Worker2  │
│ Task 1   │   │ Task 2   │   │ Task 3   │
└──────────┘   └──────────┘   └──────────┘
                     ↓ DOWN
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Manager  │   │ Worker1  │   │ Worker2  │
│ Task 1   │   │    X     │   │ Task 3   │
│ Task 2   │   │          │   │          │
└──────────┘   └──────────┘   └──────────┘
   ↑ 새로 생성
```

**Manager 노드 다운 (단일 Manager)**:
```
위험! 클러스터 관리 불가

Manager 1대 (Leader) 다운 ↓

1. 기존 컨테이너는 계속 실행
2. 하지만 새로운 작업 불가:
   - Service 생성 불가
   - 스케일링 불가
   - 업데이트 불가
   - 장애 복구 불가

→ 빠른 복구 필수!
```

**Manager 노드 다운 (다중 Manager - HA)**:
```
안전! 자동 Failover

Manager 3대 (1 Leader, 2 Reachable) 중 Leader 다운 ↓

1. Raft 알고리즘이 새 Leader 선출 (수초)
2. 새 Leader가 클러스터 관리
3. 서비스 중단 없음

┌──────────┐   ┌──────────┐   ┌──────────┐
│ Manager1 │   │ Manager2 │   │ Manager3 │
│ (Leader) │   │(Reachable)│   │(Reachable)│
└──────────┘   └──────────┘   └──────────┘
       ↓ DOWN
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Manager1 │   │ Manager2 │   │ Manager3 │
│    X     │   │ (Leader) │   │(Reachable)│
└──────────┘   └──────────┘   └──────────┘
                     ↑ 새 Leader 선출
```

**권장 Manager 노드 수**:
```
1개: 테스트/개발 환경만
3개: 프로덕션 최소 (1개 장애 허용)
5개: 대규모 프로덕션 (2개 장애 허용)

홀수 권장 이유:
- Raft 알고리즘 특성
- 짝수는 split-brain 위험
```

**실전 시나리오**:

**시나리오 1: Worker 복구**
```bash
# Worker1 다운
$ docker node ls
ID             HOSTNAME   STATUS
abc123         manager1   Ready
def456         worker1    Down    ← Down!
ghi789         worker2    Ready

# Task 자동 재배치 확인
$ docker service ps user-service
ID             NAME                 NODE      CURRENT STATE
jkl012         user-service.1       manager1  Running
mno345         user-service.2       manager1  Running 30s  ← 재배치
def456          \_ user-service.2    worker1   Shutdown
pqr678         user-service.3       worker2   Running

# Worker1 복구
$ ssh worker1
$ sudo systemctl start docker

# 자동으로 Swarm 재가입
$ docker node ls
ID             HOSTNAME   STATUS
abc123         manager1   Ready
def456         worker1    Ready   ← 복구!
ghi789         worker2    Ready
```

**시나리오 2: Manager Failover (HA)**
```bash
# Manager1 (Leader) 다운 시뮬레이션
$ ssh manager1
$ sudo systemctl stop docker

# Manager2에서 확인
$ ssh manager2
$ docker node ls
ID             HOSTNAME   STATUS    MANAGER STATUS
abc123         manager1   Down      Unreachable
def456         manager2   Ready     Leader      ← 새 Leader!
ghi789         manager3   Ready     Reachable

# 서비스 정상 작동 확인
$ docker service ls
# 모든 서비스 정상

# Manager1 복구
$ ssh manager1
$ sudo systemctl start docker
$ docker node ls
ID             HOSTNAME   STATUS    MANAGER STATUS
abc123         manager1   Ready     Reachable   ← 재가입
def456         manager2   Ready     Leader
ghi789         manager3   Ready     Reachable
```

**자동 복구 설정**:
```yaml
# Stack 파일에 restart_policy 설정
services:
  user-service:
    deploy:
      restart_policy:
        condition: on-failure  # 실패 시 재시작
        delay: 5s              # 5초 대기 후
        max_attempts: 3        # 최대 3회 시도
        window: 120s           # 2분 내 실패 횟수 카운트
```

</details>

<details>
<summary><strong>Q5: Swarm에서 로그를 어떻게 관리하나요?</strong></summary>

**A**: **로깅 드라이버 + 중앙 집중식 로깅 시스템**을 권장합니다.

**상세 설명**:

**문제점**:
```
Swarm 환경에서 로그 확인의 어려움:
- 여러 노드에 컨테이너 분산
- 컨테이너 재시작 시 로그 유실
- 각 노드마다 로그인해서 확인 불가능
```

**방법 1: docker service logs (기본)**
```bash
# 서비스의 모든 Task 로그 확인
$ docker service logs user-service

# 실시간 로그
$ docker service logs -f user-service

# 최근 100줄
$ docker service logs --tail 100 user-service

# 타임스탬프 포함
$ docker service logs -t user-service

# 특정 Task만
$ docker service logs user-service.1

# 장점:
# - 간단, 별도 설정 불필요
# - 여러 노드의 로그를 한 번에 확인

# 단점:
# - 로그 검색 어려움
# - 장기 보관 불가
# - 분석 기능 없음
```

**방법 2: 중앙 집중식 로깅 (프로덕션 권장)**

**ELK Stack (Elasticsearch + Logstash + Kibana)**:
```yaml
# docker-stack-logging.yml
version: '3.8'

services:
  # Elasticsearch (로그 저장)
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    networks:
      - logging

  # Kibana (로그 시각화)
  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    networks:
      - logging

  # Logstash (로그 수집)
  logstash:
    image: logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    networks:
      - logging

  # 애플리케이션 (로그 전송)
  user-service:
    image: lk-trade/user-service:latest
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service"
        env: "ENV"
    deploy:
      replicas: 3
    networks:
      - logging

volumes:
  elasticsearch-data:

networks:
  logging:
    driver: overlay
```

**Loki + Grafana (경량 대안)**:
```yaml
version: '3.8'

services:
  # Loki (로그 저장)
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - loki-data:/loki
    networks:
      - logging

  # Grafana (시각화)
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - logging

  # Promtail (로그 수집)
  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log
      - ./promtail-config.yml:/etc/promtail/config.yml
    deploy:
      mode: global  # 모든 노드에 배치
    networks:
      - logging

  # 애플리케이션
  user-service:
    image: lk-trade/user-service:latest
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      replicas: 3
    networks:
      - logging

volumes:
  loki-data:
  grafana-data:

networks:
  logging:
    driver: overlay
```

**방법 3: 로깅 드라이버 (syslog, fluentd)**:
```yaml
services:
  user-service:
    logging:
      driver: syslog
      options:
        syslog-address: "tcp://log-server:514"
        tag: "user-service/{{.ID}}"

  # 또는 fluentd
  trade-service:
    logging:
      driver: fluentd
      options:
        fluentd-address: "log-server:24224"
        tag: "trade-service"
```

**구조화된 로깅 (애플리케이션)**:
```kotlin
// Logback 설정 (JSON 출력)
// logback-spring.xml
<configuration>
    <appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
            <customFields>{"service":"user-service"}</customFields>
        </encoder>
    </appender>

    <root level="INFO">
        <appender-ref ref="JSON"/>
    </root>
</configuration>

// 애플리케이션 코드
logger.info(
    "User login",
    kv("userId", user.id),
    kv("email", user.email),
    kv("ip", request.remoteAddr)
)

// JSON 출력:
{
  "timestamp": "2025-01-15T10:30:00.123Z",
  "level": "INFO",
  "service": "user-service",
  "message": "User login",
  "userId": 123,
  "email": "test@example.com",
  "ip": "203.0.113.1"
}
```

**실전 로깅 전략**:

```
개발 환경:
- docker service logs로 충분

스테이징:
- Loki + Grafana (경량)
- 또는 클라우드 로깅 (CloudWatch, Stackdriver)

프로덕션:
- ELK Stack (대규모)
- 또는 Loki + Grafana (중소규모)
- 로그 보관 기간 설정 (30일, 90일)
- 알림 설정 (ERROR 발생 시)
```

</details>

---

## 📝 면접 질문

### 주니어 레벨

**Q1: Docker Swarm이 무엇이고 왜 필요한가요?**

**A**: Docker Swarm은 **여러 Docker 호스트를 하나의 가상 클러스터로 관리하는 오케스트레이션 도구**입니다.

**상세 답변**:

```
필요한 이유:

1. 고가용성 (High Availability)
   docker-compose: 서버 1대 다운 = 서비스 중단
   docker swarm: 서버 다운되어도 다른 노드로 자동 재배치

2. 스케일링
   docker-compose: 수동으로 컨테이너 추가
   docker swarm: 명령어 하나로 자동 스케일링

   $ docker service scale web=10

3. 무중단 배포
   docker-compose: 배포 시 서비스 중단
   docker swarm: 롤링 업데이트로 무중단 배포

4. 로드 밸런싱
   docker-compose: 별도 로드 밸런서 필요
   docker swarm: 자동 로드 밸런싱 (Ingress Network)
```

**실제 예시**:
```bash
# Swarm 초기화
$ docker swarm init

# 서비스 배포 (3개 레플리카, 자동 분산)
$ docker service create --name web --replicas 3 -p 80:80 nginx

# 어느 노드로 요청해도 자동 로드 밸런싱
$ curl http://node1  # OK
$ curl http://node2  # OK
$ curl http://node3  # OK
```

**핵심 포인트**:
- 단일 서버 → 여러 서버 클러스터
- 수동 관리 → 자동 관리
- 서비스 중단 → 무중단 운영

---

**Q2: Docker Swarm에서 Service와 Task의 차이는 무엇인가요?**

**A**: **Service는 원하는 상태 정의, Task는 실제 실행되는 컨테이너 인스턴스**입니다.

**상세 답변**:

```
Service (추상적 정의):
- "Nginx를 3개 실행하고 싶다"
- 원하는 상태(Desired State)
- 이미지, 레플리카 수, 포트 등 정의

Task (실제 실행):
- 각 노드에서 실행되는 컨테이너
- Service 정의에 따라 자동 생성
- 현재 상태(Current State)
```

**시각화**:
```
Service: web
├─ 원하는 상태: replicas=3, image=nginx
│
├─ Task 1 (worker1) ← 실제 컨테이너
├─ Task 2 (worker2) ← 실제 컨테이너
└─ Task 3 (manager1) ← 실제 컨테이너

만약 Task 2가 죽으면:
→ Swarm이 자동으로 새 Task 2 생성
→ Service의 원하는 상태(3개) 유지
```

**명령어 예시**:
```bash
# Service 생성
$ docker service create --name web --replicas 3 nginx

# Service 확인 (추상적 상태)
$ docker service ls
ID             NAME   REPLICAS
abc123         web    3/3

# Task 확인 (실제 실행 상태)
$ docker service ps web
ID             NAME      NODE      CURRENT STATE
task1          web.1     worker1   Running
task2          web.2     worker2   Running
task3          web.3     manager1  Running

# Task 하나 강제 종료
$ docker kill task2

# 자동으로 새 Task 생성 (Service 상태 유지)
$ docker service ps web
ID             NAME          NODE      CURRENT STATE
task1          web.1         worker1   Running
task4          web.2         worker2   Running 10s ago
task2           \_ web.2      worker2   Shutdown
task3          web.3         manager1  Running
```

**비유**:
```
Service = 레시피 (계란후라이 3개 만들기)
Task = 실제 계란후라이 (각각의 계란후라이)

하나가 타버리면 (Task 실패):
→ 레시피에 따라 새로 만듦 (새 Task 생성)
```

---

### 중급 레벨

**Q3: Docker Swarm의 Raft Consensus 알고리즘에 대해 설명하고, Manager 노드 개수를 홀수로 권장하는 이유는?**

**A**: Raft는 **분산 합의 알고리즘**으로, Manager 노드들이 클러스터 상태를 일관되게 유지하기 위해 사용하며, **과반수 투표**를 통해 Leader를 선출하기 때문에 홀수 개가 효율적입니다.

**상세 답변**:

**Raft 알고리즘 동작 원리**:
```
1. Leader 선출
   - 모든 Manager 중 1명이 Leader
   - Leader가 모든 쓰기 작업 처리
   - Leader 장애 시 자동 재선출

2. 로그 복제
   - Leader가 상태 변경사항을 로그에 기록
   - 다른 Manager들에게 복제
   - 과반수가 확인하면 커밋

3. 일관성 보장
   - 모든 Manager가 동일한 상태 유지
   - Split-brain 방지
```

**Manager 노드 수와 장애 허용**:
```
┌─────────┬─────────┬──────────────┐
│ Manager │ 과반수  │ 장애 허용    │
├─────────┼─────────┼──────────────┤
│ 1개     │ 1       │ 0개 (위험!)  │
│ 2개     │ 2       │ 0개 (의미X)  │
│ 3개     │ 2       │ 1개 ✅       │
│ 4개     │ 3       │ 1개 (비효율) │
│ 5개     │ 3       │ 2개 ✅       │
│ 6개     │ 4       │ 2개 (비효율) │
│ 7개     │ 4       │ 3개 ✅       │
└─────────┴─────────┴──────────────┘

홀수 권장 이유:
- 3개와 4개 모두 1개 장애 허용
- 하지만 4개는 리소스 낭비
- 5개와 6개 모두 2개 장애 허용
- 하지만 6개는 리소스 낭비
```

**시나리오: 3개 Manager (홀수)**
```
정상 상태:
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Manager1 │   │ Manager2 │   │ Manager3 │
│ (Leader) │   │(Follower)│   │(Follower)│
└──────────┘   └──────────┘   └──────────┘

Manager1 다운:
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Manager1 │   │ Manager2 │   │ Manager3 │
│    X     │   │(Candidate)│   │(Candidate)│
└──────────┘   └──────────┘   └──────────┘

과반수 투표 (2/3):
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Manager1 │   │ Manager2 │   │ Manager3 │
│    X     │   │ (Leader) │   │(Follower)│
└──────────┘   └──────────┘   └──────────┘
                     ↑ 새 Leader 선출 성공!
```

**시나리오: 2개 Manager (짝수) - 문제!**
```
정상 상태:
┌──────────┐   ┌──────────┐
│ Manager1 │   │ Manager2 │
│ (Leader) │   │(Follower)│
└──────────┘   └──────────┘

Manager1 다운:
┌──────────┐   ┌──────────┐
│ Manager1 │   │ Manager2 │
│    X     │   │(Candidate)│
└──────────┘   └──────────┘

과반수 투표 실패 (1/2 ≠ 과반수):
┌──────────┐   ┌──────────┐
│ Manager1 │   │ Manager2 │
│    X     │   │ 투표 불가│
└──────────┘   └──────────┘
                     ↑ Leader 선출 실패!
                     ↑ 클러스터 마비!

Split-Brain 위험:
네트워크 분리 시 각각 Leader 주장
→ 데이터 불일치
```

**실전 가이드**:
```bash
# 소규모 (테스트/개발)
1개 Manager: 빠르지만 HA 없음

# 프로덕션 (최소)
3개 Manager: 1개 장애 허용, 권장
$ docker swarm init  # Manager1
$ docker swarm join-token manager  # Manager2, 3 추가

# 대규모 프로덕션
5개 Manager: 2개 장애 허용
7개 Manager: 3개 장애 허용 (매우 큰 규모)
```

**Leader 선출 확인**:
```bash
$ docker node ls

# 출력:
ID                            HOSTNAME   MANAGER STATUS
abc123 *                      manager1   Leader      ← Leader
def456                        manager2   Reachable   ← Follower
ghi789                        manager3   Reachable   ← Follower

# Leader 강제 다운 후:
$ docker node ls

# 출력:
ID                            HOSTNAME   MANAGER STATUS
abc123                        manager1   Unreachable
def456 *                      manager2   Leader      ← 새 Leader!
ghi789                        manager3   Reachable
```

**핵심 포인트**:
- Raft = 분산 합의 알고리즘
- 과반수 투표 → 홀수가 효율적
- 3개: 소규모, 5개: 중대규모, 7개: 대규모

---

**Q4: Docker Swarm에서 롤링 업데이트 중 실패하면 어떻게 되나요? 자동 롤백 메커니즘을 설명하세요.**

**A**: **update_config의 failure_action 설정에 따라 자동 롤백 또는 일시 중지**되며, 헬스체크와 연계하여 문제를 조기 감지합니다.

**상세 답변**:

**롤링 업데이트 설정**:
```yaml
services:
  user-service:
    image: lk-trade/user-service:2.0.0
    deploy:
      replicas: 5
      update_config:
        parallelism: 1           # 한 번에 1개씩
        delay: 10s               # 10초 대기
        failure_action: rollback # 실패 시 롤백
        monitor: 60s             # 60초 동안 모니터링
        max_failure_ratio: 0.3   # 30% 실패 시 중단
        order: stop-first        # 중지 → 시작 순서

      rollback_config:
        parallelism: 1           # 롤백도 1개씩
        delay: 10s
        failure_action: pause    # 롤백 실패 시 일시 중지
        monitor: 60s

      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

**업데이트 프로세스**:
```
초기 상태 (v1.0.0):
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│v1.0 │ │v1.0 │ │v1.0 │ │v1.0 │ │v1.0 │
└─────┘ └─────┘ └─────┘ └─────┘ └─────┘

업데이트 시작 (v2.0.0):

Step 1 (0초):
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│v2.0 │ │v1.0 │ │v1.0 │ │v1.0 │ │v1.0 │
└─────┘ └─────┘ └─────┘ └─────┘ └─────┘
   ↑ 업데이트

# monitor 60s: 60초 동안 헬스체크 감시
# 문제 없으면 다음 진행

Step 2 (70초):
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│v2.0 │ │v2.0 │ │v1.0 │ │v1.0 │ │v1.0 │
└─────┘ └─────┘ └─────┘ └─────┘ └─────┘
         ↑ 업데이트

... (계속)

완료 (350초):
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│v2.0 │ │v2.0 │ │v2.0 │ │v2.0 │ │v2.0 │
└─────┘ └─────┘ └─────┘ └─────┘ └─────┘
```

**실패 시나리오 1: 헬스체크 실패**
```
Step 2에서 v2.0 컨테이너가 헬스체크 실패:

┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│v2.0 │ │v2.0 │ │v1.0 │ │v1.0 │ │v1.0 │
│ OK  │ │ X   │ │     │ │     │ │     │
└─────┘ └─────┘ └─────┘ └─────┘ └─────┘
         ↑ 헬스체크 실패 감지

failure_action: rollback 실행:

┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│v1.0 │ │v1.0 │ │v1.0 │ │v1.0 │ │v1.0 │
└─────┘ └─────┘ └─────┘ └─────┘ └─────┘
   ↑      ↑ 모두 v1.0으로 롤백
```

**실패 시나리오 2: max_failure_ratio 초과**
```
max_failure_ratio: 0.3 (30%)
replicas: 5
→ 허용 실패 수: 5 * 0.3 = 1.5 → 1개

Step 3에서 2번째 실패 발생:
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│v2.0 │ │v2.0 │ │v2.0 │ │v1.0 │ │v1.0 │
│ OK  │ │ X   │ │ X   │ │     │ │     │
└─────┘ └─────┘ └─────┘ └─────┘ └─────┘
         ↑      ↑ 2개 실패 = 40% > 30%

자동 롤백:
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│v1.0 │ │v1.0 │ │v1.0 │ │v1.0 │ │v1.0 │
└─────┘ └─────┘ └─────┘ └─────┘ └─────┘
```

**failure_action 옵션**:
```yaml
failure_action: rollback  # 자동 롤백 (권장)
failure_action: pause     # 일시 중지 (수동 개입)
failure_action: continue  # 계속 진행 (위험!)
```

**실제 명령어**:
```bash
# 업데이트 시작
$ docker service update \
    --image lk-trade/user-service:2.0.0 \
    lk-trade_user-service

# 실시간 진행 상황 확인
$ watch -n 1 'docker service ps lk-trade_user-service'

# 실패 시 로그 확인
$ docker service logs lk-trade_user-service

# 수동 롤백
$ docker service rollback lk-trade_user-service

# 또는 이전 버전으로 업데이트
$ docker service update \
    --image lk-trade/user-service:1.0.0 \
    lk-trade_user-service
```

**헬스체크 연계**:
```yaml
services:
  user-service:
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8080/health"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 40s
    deploy:
      update_config:
        monitor: 60s  # 헬스체크 결과 60초 동안 모니터링
        # Unhealthy 상태 → 실패로 간주
```

**Best Practice**:
```yaml
# 안전한 롤링 업데이트 설정
services:
  user-service:
    deploy:
      replicas: 5
      update_config:
        parallelism: 1        # 천천히 (1개씩)
        delay: 30s            # 충분한 대기 시간
        failure_action: rollback
        monitor: 60s          # 충분한 모니터링 시간
        max_failure_ratio: 0.2  # 낮은 허용치 (20%)
        order: start-first    # 새 컨테이너 먼저 시작 (다운타임 최소화)

      rollback_config:
        parallelism: 2        # 롤백은 빠르게 (2개씩)
        delay: 10s
```

**핵심 포인트**:
- `failure_action: rollback` 필수
- 헬스체크로 조기 감지
- `max_failure_ratio`로 허용 범위 설정
- `monitor` 시간 충분히 설정
- 롤백도 점진적으로

---

**Q5: Docker Swarm의 Overlay 네트워크는 어떻게 동작하며, 다른 노드에 있는 컨테이너 간 통신이 가능한 이유는?**

**A**: Overlay 네트워크는 **VXLAN 기술을 사용하여 여러 호스트 간 가상 네트워크를 구성**하며, 각 노드의 Docker 데몬이 **VXLAN 터널을 생성하여 컨테이너 간 직접 통신**을 가능하게 합니다.

**상세 답변**:

**Overlay 네트워크 구조**:
```
물리적 네트워크 (Underlay):
┌────────────┐      ┌────────────┐      ┌────────────┐
│  Node 1    │      │  Node 2    │      │  Node 3    │
│192.168.1.10│──────│192.168.1.11│──────│192.168.1.12│
└────────────┘      └────────────┘      └────────────┘
      ↑                   ↑                   ↑
      │                   │                   │
    VXLAN               VXLAN               VXLAN
    Tunnel              Tunnel              Tunnel
      │                   │                   │
      ↓                   ↓                   ↓
가상 네트워크 (Overlay):
┌────────────┐      ┌────────────┐      ┌────────────┐
│Container A │      │Container B │      │Container C │
│ 10.0.1.10  │──────│ 10.0.1.11  │──────│ 10.0.1.12  │
└────────────┘      └────────────┘      └────────────┘

컨테이너는 같은 네트워크에 있다고 인식
→ 실제로는 다른 호스트에 있음
```

**VXLAN (Virtual Extensible LAN) 동작 원리**:
```
Container A (Node1) → Container B (Node2) 통신:

1. Container A가 패킷 전송
   Source: 10.0.1.10 (Container A)
   Dest: 10.0.1.11 (Container B)

2. Node1의 Docker 데몬이 패킷 캡슐화
   ┌───────────────────────────────────┐
   │ Outer Header (Physical)           │
   │ Source: 192.168.1.10 (Node1)      │
   │ Dest: 192.168.1.11 (Node2)        │
   ├───────────────────────────────────┤
   │ VXLAN Header (VNI)                │
   ├───────────────────────────────────┤
   │ Inner Header (Virtual)            │
   │ Source: 10.0.1.10 (Container A)   │
   │ Dest: 10.0.1.11 (Container B)     │
   ├───────────────────────────────────┤
   │ Payload                           │
   └───────────────────────────────────┘

3. 물리 네트워크로 전송

4. Node2의 Docker 데몬이 패킷 디캡슐화
   - Outer Header 제거
   - Inner Header 추출
   - Container B에게 전달

5. Container B가 패킷 수신
   Source: 10.0.1.10 (Container A로 인식)
```

**Swarm Overlay 네트워크 생성**:
```bash
# Overlay 네트워크 생성 (Manager 노드에서)
$ docker network create \
    --driver overlay \
    --attachable \
    my-overlay-network

# 네트워크 확인
$ docker network ls

# 출력:
NETWORK ID     NAME                 DRIVER    SCOPE
abc123def456   my-overlay-network   overlay   swarm

# 서비스를 Overlay 네트워크에 연결
$ docker service create \
    --name web \
    --network my-overlay-network \
    --replicas 3 \
    nginx
```

**네트워크 구성 요소**:
```
Swarm Overlay 네트워크의 구성:

1. Ingress Network (기본)
   - 외부 트래픽 → 서비스 라우팅
   - 자동 생성
   - 모든 노드에 존재

2. User-defined Overlay Network
   - 서비스 간 통신
   - 격리된 네트워크
   - 필요 시 생성

3. Docker_gwbridge (브리지)
   - 컨테이너 ↔ 물리 네트워크 연결
   - 각 노드에 자동 생성
```

**서비스 디스커버리 (DNS)**:
```
같은 Overlay 네트워크의 서비스는 이름으로 통신 가능:

서비스 구성:
- user-service (3 replicas)
- account-service (2 replicas)

user-service에서 account-service 호출:
$ curl http://account-service/api/accounts

DNS 해석:
1. account-service → 10.0.1.100 (Virtual IP)
2. 10.0.1.100 → 2개 Task로 로드 밸런싱
   - 10.0.1.21 (Task 1)
   - 10.0.1.22 (Task 2)

VIP (Virtual IP) 모드:
┌──────────────────┐
│ account-service  │
│  10.0.1.100 (VIP)│
└──────────────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌────────┐ ┌────────┐
│Task 1  │ │Task 2  │
│10.0.1.21│ │10.0.1.22│
└────────┘ └────────┘
```

**실전 예제**:
```yaml
# docker-stack.yml
version: '3.8'

services:
  frontend:
    image: frontend:latest
    deploy:
      replicas: 2
    networks:
      - frontend-net
      - backend-net

  api:
    image: api:latest
    deploy:
      replicas: 3
    networks:
      - backend-net
      - db-net

  database:
    image: postgres:16
    deploy:
      replicas: 1
    networks:
      - db-net

networks:
  frontend-net:
    driver: overlay
  backend-net:
    driver: overlay
  db-net:
    driver: overlay

# 네트워크 격리:
# frontend → api (OK)
# frontend → database (불가능, 다른 네트워크)
# api → database (OK)
```

**Overlay 네트워크 검증**:
```bash
# 네트워크 상세 정보
$ docker network inspect my-overlay-network

# 출력 (일부):
[
    {
        "Name": "my-overlay-network",
        "Driver": "overlay",
        "Scope": "swarm",
        "IPAM": {
            "Config": [
                {
                    "Subnet": "10.0.1.0/24",
                    "Gateway": "10.0.1.1"
                }
            ]
        },
        "Containers": {
            "abc123": {
                "Name": "web.1",
                "IPv4Address": "10.0.1.10/24"
            },
            "def456": {
                "Name": "web.2",
                "IPv4Address": "10.0.1.11/24"
            }
        }
    }
]

# 컨테이너 간 통신 테스트
$ docker exec web.1 ping web.2
PING web.2 (10.0.1.11): 56 data bytes
64 bytes from 10.0.1.11: seq=0 ttl=64 time=0.123 ms
```

**Ingress Load Balancing (외부 접근)**:
```
외부 요청 → 80:80 (모든 노드)

Ingress Network가 자동 라우팅:

    외부 → Node1:80
              ↓
        Ingress Network
         /    |    \
        /     |     \
    Task1  Task2  Task3
   (Node1)(Node2)(Node3)

→ 어느 노드로 요청해도 자동 분산
→ 해당 노드에 Task가 없어도 OK
```

**보안 (암호화)**:
```bash
# 암호화된 Overlay 네트워크 생성
$ docker network create \
    --driver overlay \
    --opt encrypted \
    secure-network

# 모든 트래픽 자동 암호화 (IPsec)
```

**핵심 포인트**:
- Overlay = VXLAN 터널
- 다른 호스트 컨테이너도 같은 네트워크처럼
- 서비스 이름으로 자동 DNS
- VIP로 자동 로드 밸런싱
- Ingress로 외부 접근 자동 분산

---

## 다음 단계

### 33. Kubernetes 소개
- Kubernetes의 필요성
- Docker Swarm vs Kubernetes 비교
- Kubernetes 아키텍처
- kubectl 기본 명령어

### 학습 자료

**공식 문서**:
- [Docker Swarm Documentation](https://docs.docker.com/engine/swarm/)
- [Docker Stack Deploy](https://docs.docker.com/engine/reference/commandline/stack_deploy/)

**유용한 도구**:
- [Portainer](https://www.portainer.io/) - Swarm 웹 UI
- [Swarmpit](https://swarmpit.io/) - Swarm 관리 도구

---

**축하합니다! 🎉** Docker Swarm 오케스트레이션 마스터!
