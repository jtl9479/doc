# 섹션 32: Docker Swarm (오케스트레이션)

## 비유로 시작하기

Docker Swarm은 **오케스트라 지휘자**와 같습니다.

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
```

지휘자 없이 100명이 연주하면 혼란스럽듯이, 오케스트레이션 없이 수백 개의 컨테이너를 관리하면 불가능합니다.

---

## 왜 오케스트레이션이 필요한가?

### 1. docker-compose의 한계

```
docker-compose (단일 호스트)
============================

서버 1대
┌─────────────────────────────────────┐
│  Docker Engine                      │
│  ┌─────┐ ┌─────┐ ┌─────┐          │
│  │ A   │ │ B   │ │ C   │          │
│  └─────┘ └─────┘ └─────┘          │
└─────────────────────────────────────┘

문제점:
❌ 1대 서버 장애 = 전체 서비스 중단
❌ 트래픽 증가 시 스케일 불가
❌ 로드 밸런싱 불가
❌ 자동 복구 없음
❌ 무중단 배포 어려움


Docker Swarm (클러스터)
========================

      Manager Node
     /      |      \
    /       |       \
Worker 1  Worker 2  Worker 3
┌─────┐   ┌─────┐   ┌─────┐
│ A   │   │ A   │   │ B   │
│ B   │   │ C   │   │ C   │
└─────┘   └─────┘   └─────┘

장점:
✅ 고가용성 (HA)
✅ 자동 스케일링
✅ 로드 밸런싱
✅ 자가 치유
✅ 무중단 배포
✅ 보안 (암호화 통신)
```

### 2. Docker Swarm vs Kubernetes

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

## Docker Swarm 기초

### 1. 핵심 개념

```
Swarm 아키텍처
==============

┌─────────────────────────────────────────────────────────┐
│                    Manager Nodes                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Manager 1   │  │  Manager 2   │  │  Manager 3   │  │
│  │   (Leader)   │  │  (Reachable) │  │  (Reachable) │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                  │                  │         │
│         └──────────────────┼──────────────────┘         │
│                            │ (Raft Consensus)           │
└────────────────────────────┼────────────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            │                                 │
┌───────────▼──────────┐          ┌───────────▼──────────┐
│    Worker Node 1     │          │    Worker Node 2     │
│  ┌─────┐   ┌─────┐  │          │  ┌─────┐   ┌─────┐  │
│  │Task1│   │Task2│  │          │  │Task3│   │Task4│  │
│  └─────┘   └─────┘  │          │  └─────┘   └─────┘  │
└──────────────────────┘          └──────────────────────┘

용어:
- Node: Swarm에 참여하는 Docker 엔진 인스턴스
- Manager Node: 클러스터 상태 관리, 스케줄링 결정
- Worker Node: 컨테이너 실행
- Service: 스웜에서 실행되는 애플리케이션 정의
- Task: Service의 개별 컨테이너 인스턴스
- Stack: 여러 Service의 그룹
```

### 2. Service 복제 모드

```
Replicated Mode (복제 모드)
==========================

Service: web
Replicas: 3

Manager가 자동으로 배치:

Node 1      Node 2      Node 3
┌─────┐     ┌─────┐     ┌─────┐
│ web │     │ web │     │ web │
└─────┘     └─────┘     └─────┘

→ 3개의 동일한 레플리카


Global Mode (전역 모드)
======================

Service: monitoring-agent
Mode: global

모든 노드에 1개씩 배치:

Node 1      Node 2      Node 3
┌─────┐     ┌─────┐     ┌─────┐
│agent│     │agent│     │agent│
└─────┘     └─────┘     └─────┘

→ 각 노드마다 1개
→ 로깅, 모니터링에 적합
```

---

## Docker Swarm 시작하기

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

### 4. Service 삭제

```bash
# 서비스 삭제
docker service rm web

# 확인
docker service ls
# (빈 목록)
```

---

## Docker Stack (복잡한 애플리케이션)

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

  # Trade Service
  trade-service:
    image: lk-trade/trade-service:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
      placement:
        constraints:
          - node.role == worker
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
    networks:
      - lk-trade-network
    secrets:
      - db_password

  # Account Service
  account-service:
    image: lk-trade/account-service:latest
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
      placement:
        constraints:
          - node.role == worker
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    networks:
      - lk-trade-network

  # Strategy Service
  strategy-service:
    image: lk-trade/strategy-service:latest
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
      placement:
        constraints:
          - node.role == worker
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    networks:
      - lk-trade-network

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

  # Redis
  redis:
    image: redis:7-alpine
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
      restart_policy:
        condition: on-failure
    volumes:
      - redis-data:/data
    networks:
      - lk-trade-network

  # Nginx (Reverse Proxy & Load Balancer)
  nginx:
    image: nginx:alpine
    deploy:
      replicas: 2
      placement:
        constraints:
          - node.role == worker
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    networks:
      - lk-trade-network

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
  redis-data:

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

# 또는 파일에서 생성
docker secret create db_password ./secrets/db_password.txt

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
Creating service lk-trade_trade-service
Creating service lk-trade_account-service
Creating service lk-trade_strategy-service
Creating service lk-trade_postgres
Creating service lk-trade_redis
Creating service lk-trade_nginx
Creating service lk-trade_visualizer

# Stack 목록 확인
docker stack ls

# 출력:
NAME       SERVICES   ORCHESTRATOR
lk-trade   8          Swarm

# Stack의 서비스 확인
docker stack services lk-trade

# 출력:
ID             NAME                        MODE         REPLICAS   IMAGE
abc123         lk-trade_user-service       replicated   3/3        lk-trade/user-service:latest
def456         lk-trade_trade-service      replicated   3/3        lk-trade/trade-service:latest
ghi789         lk-trade_account-service    replicated   2/2        lk-trade/account-service:latest
jkl012         lk-trade_strategy-service   replicated   2/2        lk-trade/strategy-service:latest
mno345         lk-trade_postgres           replicated   1/1        postgres:16-alpine
pqr678         lk-trade_redis              replicated   1/1        redis:7-alpine
stu901         lk-trade_nginx              replicated   2/2        nginx:alpine
vwx234         lk-trade_visualizer         replicated   1/1        dockersamples/visualizer:latest

# Stack의 Task 확인 (어느 노드에서 실행 중인지)
docker stack ps lk-trade

# Stack 삭제
docker stack rm lk-trade
```

---

## 고급 기능

### 1. 로드 밸런싱

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

### 2. 배치 제약 조건 (Placement Constraints)

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

  # 여러 조건
  app:
    deploy:
      placement:
        constraints:
          - node.role == worker
          - node.labels.zone == asia
          - node.labels.ssd == true
```

노드에 레이블 추가:

```bash
# 노드에 레이블 추가
docker node update --label-add type=database worker1
docker node update --label-add zone=asia worker2
docker node update --label-add ssd=true worker3

# 노드 정보 확인
docker node inspect worker1 --pretty
```

### 3. 배치 선호도 (Placement Preferences)

```yaml
services:
  web:
    deploy:
      replicas: 6
      placement:
        # 가능한 여러 zone에 분산
        preferences:
          - spread: node.labels.zone
```

### 4. 헬스 체크

```yaml
services:
  user-service:
    healthcheck:
      test: ["CMD", "wget", "--spider", "http://localhost:8080/actuator/health"]
      interval: 30s      # 30초마다 체크
      timeout: 3s        # 3초 내에 응답 없으면 실패
      retries: 3         # 3회 연속 실패 시 unhealthy
      start_period: 40s  # 시작 후 40초는 실패 무시
```

### 5. 리소스 제한

```yaml
services:
  user-service:
    deploy:
      resources:
        # 하드 리미트 (초과 불가)
        limits:
          cpus: '1.0'
          memory: 1G
        # 예약 (보장)
        reservations:
          cpus: '0.5'
          memory: 512M
```

---

## Swarm 모니터링

### 1. Visualizer (실시간 시각화)

```bash
# Visualizer 접속
http://localhost:8080

# 화면에 표시되는 정보:
- 각 노드의 상태
- 실행 중인 컨테이너
- 컨테이너 배치 상태
- 실시간 업데이트
```

### 2. 명령어로 모니터링

```bash
# 노드 상태 확인
docker node ls

# 서비스 상태 확인
docker service ls

# 특정 서비스의 Task 확인
docker service ps lk-trade_user-service

# 서비스 로그 확인
docker service logs -f lk-trade_user-service

# 특정 Task의 로그
docker service logs lk-trade_user-service.1

# 서비스 상세 정보
docker service inspect lk-trade_user-service --pretty

# 노드 상세 정보
docker node inspect manager1 --pretty
```

### 3. Prometheus + Grafana 통합

```yaml
# docker-stack-monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - monitoring

  # Docker 메트릭 수집
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    deploy:
      mode: global  # 모든 노드에 배치
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    networks:
      - monitoring

  # Node 메트릭 수집
  node-exporter:
    image: prom/node-exporter:latest
    deploy:
      mode: global
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - monitoring

volumes:
  prometheus-data:
  grafana-data:

networks:
  monitoring:
    driver: overlay
```

---

## 자가 치유 (Self-Healing)

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

# Worker1 복구
# Worker1에서:
sudo systemctl start docker

# Swarm에 자동 재가입
docker node ls
# worker1이 다시 Ready 상태
```

### 3. 노드 유지보수 모드

```bash
# Worker1을 유지보수 모드로 전환 (새 Task 배치 안 됨)
docker node update --availability drain worker1

# 확인
docker node ls

# 출력:
ID             HOSTNAME   STATUS    AVAILABILITY   MANAGER STATUS
abc123         manager1   Ready     Active         Leader
def456         worker1    Ready     Drain          ← Drain!
ghi789         worker2    Ready     Active

# Worker1의 모든 Task가 다른 노드로 이동
docker node ps worker1

# 유지보수 완료 후 다시 활성화
docker node update --availability active worker1
```

---

## 무중단 배포 (Rolling Update)

### 1. 업데이트 설정

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

### 2. 롤링 업데이트 실행

```bash
# 이미지 업데이트
docker service update \
  --image lk-trade/user-service:2.0.0 \
  lk-trade_user-service

# 실시간 진행 상황 확인
watch -n 1 'docker service ps lk-trade_user-service'

# 출력 (시간 경과):
# 10:00 - user-service.1 업데이트 중
# 10:10 - user-service.1 완료, user-service.2 업데이트 중
# 10:20 - user-service.2 완료, user-service.3 업데이트 중
# 10:30 - 모두 완료!
```

### 3. 롤백

```bash
# 수동 롤백
docker service rollback lk-trade_user-service

# 또는 이전 버전으로 업데이트
docker service update \
  --image lk-trade/user-service:1.0.0 \
  lk-trade_user-service
```

---

## 자동화 스크립트

### 1. Swarm 초기화 스크립트

```bash
#!/bin/bash
# scripts/swarm-init.sh

set -e

echo "🐝 Initializing Docker Swarm..."

# 현재 서버 IP 감지
IP=$(hostname -I | awk '{print $1}')

# Swarm 초기화
docker swarm init --advertise-addr $IP

echo "✅ Swarm initialized successfully!"
echo ""
echo "Manager node is ready at: $IP"
echo ""
echo "To add worker nodes, run this on worker servers:"
docker swarm join-token worker
echo ""
echo "To add manager nodes, run this on manager servers:"
docker swarm join-token manager
```

### 2. Stack 배포 스크립트

```bash
#!/bin/bash
# scripts/deploy-stack.sh

set -e

STACK_NAME=${1:-lk-trade}
VERSION=${2:-latest}

echo "🚀 Deploying stack: $STACK_NAME (version: $VERSION)"

# Secret 생성 (없으면)
if ! docker secret ls | grep -q db_password; then
    echo "Creating db_password secret..."
    cat ./secrets/db_password.txt | docker secret create db_password -
fi

if ! docker secret ls | grep -q jwt_secret; then
    echo "Creating jwt_secret secret..."
    cat ./secrets/jwt_secret.txt | docker secret create jwt_secret -
fi

# 환경 변수 설정
export VERSION=$VERSION

# Stack 배포
docker stack deploy -c docker-stack.yml $STACK_NAME

echo ""
echo "⏳ Waiting for services to start..."
sleep 30

# 서비스 상태 확인
docker stack services $STACK_NAME

echo ""
echo "✅ Stack deployed successfully!"
echo ""
echo "Visualizer: http://localhost:8080"
```

### 3. Makefile 통합

```makefile
# Makefile
.PHONY: swarm-init swarm-join deploy-stack update-stack remove-stack swarm-status

# Swarm 초기화
swarm-init:
	bash scripts/swarm-init.sh

# Swarm 상태 확인
swarm-status:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "Nodes:"
	@docker node ls
	@echo ""
	@echo "Stacks:"
	@docker stack ls
	@echo ""
	@echo "Services:"
	@docker service ls

# Stack 배포
deploy-stack:
	@read -p "Enter stack name (default: lk-trade): " name; \
	name=$${name:-lk-trade}; \
	read -p "Enter version (default: latest): " version; \
	version=$${version:-latest}; \
	bash scripts/deploy-stack.sh $$name $$version

# Stack 업데이트
update-stack:
	@read -p "Enter stack name: " name; \
	read -p "Enter service to update: " service; \
	read -p "Enter new version: " version; \
	docker service update --image lk-trade/$$service:$$version $${name}_$$service

# Stack 삭제
remove-stack:
	@read -p "Enter stack name: " name; \
	docker stack rm $$name

# Swarm 떠나기
swarm-leave:
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker swarm leave --force; \
	fi

# 모니터링
swarm-monitor:
	watch -n 2 'docker node ls; echo ""; docker service ls'
```

---

## 다음 단계

축하합니다! 🎉 Docker Swarm 오케스트레이션을 완벽하게 마스터했습니다.

### 이번 섹션에서 배운 것

✅ Docker Swarm의 필요성 및 Kubernetes 비교
✅ Swarm 아키텍처 (Manager, Worker, Service, Task)
✅ Swarm 초기화 및 노드 추가
✅ Service 생성, 스케일링, 업데이트
✅ Docker Stack으로 복잡한 애플리케이션 배포
✅ Secret 관리
✅ 로드 밸런싱 및 배치 제약조건
✅ 자가 치유 및 무중단 배포
✅ Swarm 모니터링 (Visualizer, Prometheus)
✅ 자동화 스크립트

### 다음에 배울 것

**섹션 33: Kubernetes 소개**에서는:
- Kubernetes 기본 개념
- Docker Swarm vs Kubernetes 실전 비교
- Kubernetes 아키텍처
- kubectl 기본 명령어
- 간단한 애플리케이션 배포

### 추가 학습 자료

**공식 문서:**
- [Docker Swarm Documentation](https://docs.docker.com/engine/swarm/)
- [Docker Stack Deploy](https://docs.docker.com/engine/reference/commandline/stack_deploy/)

**유용한 도구:**
- [Portainer](https://www.portainer.io/) - Swarm 웹 UI
- [Swarmpit](https://swarmpit.io/) - Swarm 관리 도구

---

**다음 섹션에서 만나요!** 🚀