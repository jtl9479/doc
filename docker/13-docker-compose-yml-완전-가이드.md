# 13장: docker-compose.yml 완전 가이드

> **학습 목표**: docker-compose.yml 파일의 모든 설정을 이해하고, 프로덕션 수준의 멀티 컨테이너 환경을 구성할 수 있습니다

**⏱️ 예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐⭐☆ (4개/5개)

---

## 📚 목차
- [왜 docker-compose.yml이 필요한가](#왜-docker-composeyml이-필요한가)
- [실생활 비유로 이해하기](#실생활-비유로-이해하기)
- [버전별 차이점](#131-버전별-차이점)
- [서비스 정의](#132-서비스-정의-services)
- [네트워크 정의](#133-네트워크-정의-networks)
- [볼륨 정의](#134-볼륨-정의-volumes)
- [환경 변수 관리](#135-환경-변수-관리)
- [의존성 관리](#136-depends_on과-의존성-관리)
- [헬스체크 설정](#137-healthcheck-설정)
- [재시작 정책](#138-restart-정책)
- [리소스 제한](#139-리소스-제한-cpu-메모리)
- [포트 및 네트워크](#1310-포트-및-네트워크-설정)
- [완전한 프로덕션 예제](#1311-완전한-프로덕션-예제)
- [주니어 시나리오](#주니어-시나리오)
- [FAQ](#faq)
- [면접 질문 리스트](#면접-질문-리스트)
- [핵심 정리](#핵심-정리)
- [다음 단계](#다음-단계)

---

## 🤔 왜 docker-compose.yml이 필요한가?

### 실무 배경

**상황**: 웹 애플리케이션(프론트엔드 + 백엔드 + 데이터베이스 + 캐시 + 리버스 프록시)을 배포하려고 합니다.

#### ❌ docker-compose.yml을 모르면 발생하는 문제

```
문제 1: 매번 긴 명령어 실행
- 증상: 5개 컨테이너마다 docker run 명령어 수동 입력
- 영향: 배포 1번에 30분 소요, 오타 발생률 80%
- 비용: 개발자 시간 낭비, 배포 실패로 서비스 중단

문제 2: 컨테이너 간 설정 불일치
- 증상: 네트워크, 볼륨, 환경 변수가 제각각
- 영향: 컨테이너 간 통신 실패, 데이터 유실
- 비용: 장애 대응에 4시간 소요

문제 3: 팀원마다 다른 환경
- 증상: "제 컴퓨터에서는 되는데요?" 증후군
- 영향: 환경 차이로 버그 재현 불가
- 비용: 디버깅에 하루 소모
```

#### ✅ docker-compose.yml을 사용하면

```
해결책 1: 단일 명령어로 전체 환경 실행
- 방법: docker compose up 한 줄
- 효과: 배포 시간 30분 → 30초
- 절감: 개발자 시간 95% 단축

해결책 2: 설정 파일로 일관성 보장
- 방법: YAML 파일에 모든 설정 명시
- 효과: 설정 오류 80% → 0%
- 절감: 장애 대응 시간 4시간 → 0시간

해결책 3: 팀 전체가 동일 환경
- 방법: git으로 docker-compose.yml 공유
- 효과: "내 컴퓨터에서는 되는데" 문제 완전 해결
- 절감: 환경 차이 디버깅 시간 100% 절감
```

### 📊 수치로 보는 효과

| 지표 | docker run 수동 | docker-compose.yml | 개선율 |
|------|----------------|-------------------|--------|
| 배포 시간 | 30분 | 30초 | **99%↓** |
| 설정 오류율 | 80% | 5% | **94%↓** |
| 환경 구성 시간 | 4시간 | 5분 | **98%↓** |
| 팀원 온보딩 | 2일 | 30분 | **94%↓** |
| 문서화 시간 | 8시간 | 0시간 | **100%↓** |

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 레고 조립 설명서

```
docker-compose.yml = 레고 조립 설명서

개별 docker run = 레고 블록 하나씩 어디에 놓을지 말로 설명
  "빨간 블록을 왼쪽에, 파란 블록을 위에..."
  → 시간 오래 걸림, 실수 많음, 재현 어려움

docker-compose.yml = 그림이 있는 조립 설명서
  1단계: 바닥판 준비
  2단계: 벽 세우기
  3단계: 지붕 올리기
  → 빠르고, 정확하고, 누구나 동일하게 조립

┌────────────────────────────────┐
│  [레고 조립 설명서]             │
│  ┌──┐  ┌──┐  ┌──┐             │
│  │1 │→ │2 │→ │3 │             │
│  └──┘  └──┘  └──┘             │
│  바닥   벽    지붕              │
└────────────────────────────────┘
```

### 비유 2: 아파트 건축 설계도

```
docker-compose.yml = 아파트 건축 설계도

각 컨테이너 = 아파트 각 세대
네트워크 = 층마다 복도 (세대 간 이동 경로)
볼륨 = 공용 창고 (데이터 저장)
의존성 = 건축 순서 (기초 → 기둥 → 벽 → 지붕)

설계도 없이 짓기:
  "여기 벽 하나, 저기 문 하나..."
  → 무너지거나 이상하게 지어짐

설계도로 짓기:
  도면대로 정확히 건축
  → 안전하고 예측 가능
```

### 비유 3: 오케스트라 악보

```
docker-compose.yml = 오케스트라 총악보

각 서비스 = 각 악기 파트
depends_on = 연주 순서 (전주 → 주선율 → 화음)
healthcheck = 악기 조율 확인
restart = 실수 시 재연주

악보 없이:
  지휘자가 일일이 "바이올린 시작! 첼로 대기!"
  → 혼란스럽고 불협화음

악보 있으면:
  모두가 악보 보고 정확히 연주
  → 완벽한 하모니
```

### 비유 4: 요리 레시피

```
docker-compose.yml = 요리 레시피 카드

서비스 = 요리 재료
볼륨 = 조리 도구
네트워크 = 조리 순서
환경 변수 = 양념 비율

레시피 없이:
  "소금 적당히, 설탕 대충..."
  → 매번 다른 맛

레시피 있으면:
  "소금 5g, 설탕 10g, 180도 20분"
  → 항상 동일한 맛
```

### 비유 5: 회사 조직도

```
docker-compose.yml = 회사 조직도

서비스 = 각 부서 (개발팀, 디자인팀, 마케팅팀)
네트워크 = 부서 간 협업 채널
depends_on = 업무 순서 (기획 → 개발 → 테스트)
리소스 제한 = 부서별 예산 배정

조직도 없이:
  누가 뭘 하는지 모름
  → 업무 중복, 책임 회피

조직도 있으면:
  역할과 책임이 명확
  → 효율적 협업
```

### 🎯 종합 비교표

```
┌──────────────┬──────────┬──────────┬──────────┬──────────┐
│ Compose 요소 │ 레고     │ 아파트   │ 오케스트라│ 요리     │
├──────────────┼──────────┼──────────┼──────────┼──────────┤
│ services     │ 블록     │ 세대     │ 악기     │ 재료     │
│ networks     │ 연결부   │ 복도     │ 박자     │ 순서     │
│ volumes      │ 받침판   │ 창고     │ 악보대   │ 도구     │
│ depends_on   │ 조립순서 │ 건축순서 │ 연주순서 │ 조리순서 │
│ healthcheck  │ 강도확인 │ 안전검사 │ 조율     │ 간맛보기 │
└──────────────┴──────────┴──────────┴──────────┴──────────┘
```

---

## 13.1 버전별 차이점

### 13.1.1 Compose 파일 버전 역사

```yaml
# Version 1 (레거시, 사용 중단)
web:
  image: nginx
  ports:
    - "80:80"

# Version 2.x
version: '2.4'
services:
  web:
    image: nginx
    ports:
      - "80:80"

# Version 3.x (현재 권장)
version: '3.8'
services:
  web:
    image: nginx
    ports:
      - "80:80"
```

### 13.1.2 버전별 주요 기능

| 기능 | V2 | V3.0-3.3 | V3.4+ |
|------|----|---------|----|
| **depends_on 조건** | ✅ | ❌ | ✅ |
| **extends** | ✅ | ❌ | ❌ |
| **deploy (Swarm)** | ❌ | ✅ | ✅ |
| **init 옵션** | ❌ | ❌ | ✅ |
| **volume 읽기전용** | ✅ | ✅ | ✅ |
| **네트워크 우선순위** | ❌ | ✅ | ✅ |

### 13.1.3 권장 버전

```yaml
# 로컬 개발 및 단일 호스트 배포
version: '3.8'  # ✅ 권장

# Docker Swarm 클러스터
version: '3.8'  # ✅ 최신 기능 사용

# 레거시 시스템 (Docker 19.03 이하)
version: '3.3'  # ⚠️  필요 시만
```

**버전 확인:**

```bash
# Docker Compose 버전
docker compose version

# 지원하는 Compose 파일 버전 확인
docker compose config --version
```

---

## 13.2 서비스 정의 (services)

### 13.2.1 이미지 및 빌드

#### 기존 이미지 사용

```yaml
services:
  web:
    # 공식 이미지
    image: nginx:alpine

  database:
    # Docker Hub 이미지
    image: postgres:15-alpine

  custom:
    # 프라이빗 레지스트리
    image: registry.example.com/myapp:1.0.0

  pinned:
    # SHA256 다이제스트로 고정 (불변성 보장)
    image: nginx@sha256:abc123def456...
```

#### Dockerfile로 빌드

```yaml
services:
  # 기본 빌드
  app1:
    build: .

  # 빌드 컨텍스트 지정
  app2:
    build: ./backend

  # 상세 빌드 옵션
  app3:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
      args:
        NODE_VERSION: 18
        BUILD_DATE: 2024-01-15
      target: production
      cache_from:
        - myapp:cache
      labels:
        - "com.example.version=1.0"
      network: host
      shm_size: '2gb'

  # 이미지 태그 지정
  app4:
    build:
      context: .
    image: myapp:latest
```

**빌드 인자 (ARG) 전달:**

```yaml
# docker-compose.yml
services:
  app:
    build:
      context: .
      args:
        - NODE_VERSION=18
        - BUILD_ENV=production

# Dockerfile
ARG NODE_VERSION=16
FROM node:${NODE_VERSION}-alpine

ARG BUILD_ENV
ENV NODE_ENV=${BUILD_ENV}
```

---

### 13.2.2 컨테이너 이름 및 호스트명

```yaml
services:
  # 커스텀 컨테이너 이름
  web:
    container_name: my-nginx-server
    image: nginx

  # 호스트명 설정
  api:
    hostname: api-server
    image: myapi

  # 도메인 설정
  database:
    hostname: db
    domainname: example.com
    # FQDN: db.example.com
    image: postgres
```

**주의사항:**

```yaml
# ❌ 비권장: container_name 사용 시 스케일 불가
services:
  web:
    container_name: web-server
    # docker compose up --scale web=3  # 에러 발생!

# ✅ 권장: container_name 없이 자동 이름 생성
services:
  web:
    image: nginx
    # 자동 이름: projectname-web-1, projectname-web-2, ...
```

---

### 13.2.3 명령어 및 엔트리포인트

```yaml
services:
  # 기본 명령어 오버라이드
  app1:
    image: node:18-alpine
    command: npm start

  # 배열 형식 (권장)
  app2:
    image: node:18-alpine
    command: ["npm", "run", "dev"]

  # 셸 명령어
  app3:
    image: alpine
    command: sh -c "echo 'Starting...' && sleep 3600"

  # 엔트리포인트 오버라이드
  app4:
    image: myapp
    entrypoint: /custom-entrypoint.sh

  # 배열 형식 엔트리포인트
  app5:
    image: myapp
    entrypoint: ["python", "-m", "flask"]
    command: ["run", "--host=0.0.0.0"]
    # 실제 실행: python -m flask run --host=0.0.0.0
```

---

### 13.2.4 작업 디렉토리 및 사용자

```yaml
services:
  # 작업 디렉토리
  app1:
    image: node:18-alpine
    working_dir: /app/src
    command: npm test

  # 실행 사용자
  app2:
    image: myapp
    user: "1000:1000"

  # 사용자 이름으로 지정
  app3:
    image: nginx
    user: nginx

  # 루트 권한 필요 시 (비권장)
  app4:
    image: myapp
    user: root
    # 보안 주의!
```

---

### 13.2.5 레이블 및 메타데이터

```yaml
services:
  web:
    image: nginx
    labels:
      # 프로젝트 정보
      com.example.project: "MyApp"
      com.example.version: "1.0.0"
      com.example.environment: "production"

      # Traefik 라우팅 (리버스 프록시)
      traefik.enable: "true"
      traefik.http.routers.web.rule: "Host(`example.com`)"
      traefik.http.services.web.loadbalancer.server.port: "80"

      # 모니터링 레이블
      prometheus.scrape: "true"
      prometheus.port: "9090"
```

---

## 13.3 네트워크 정의 (networks)

### 13.3.1 기본 네트워크

```yaml
# 서비스만 정의 시 기본 네트워크 자동 생성
version: '3.8'

services:
  web:
    image: nginx
  api:
    image: myapi

# 자동 생성:
# - 네트워크 이름: <프로젝트명>_default
# - 드라이버: bridge
# - 모든 서비스가 연결됨
```

### 13.3.2 커스텀 네트워크

```yaml
version: '3.8'

services:
  web:
    image: nginx
    networks:
      - frontend

  api:
    image: myapi
    networks:
      - frontend
      - backend

  database:
    image: postgres
    networks:
      - backend

networks:
  # 기본 브리지 네트워크
  frontend:
    driver: bridge

  # 외부 접근 차단 (내부만)
  backend:
    driver: bridge
    internal: true
```

### 13.3.3 상세 네트워크 설정

```yaml
networks:
  # 서브넷 및 게이트웨이 지정
  custom-net:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
          gateway: 172.28.0.1
          ip_range: 172.28.5.0/24

  # 드라이버 옵션
  advanced-net:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: br-myapp
      com.docker.network.bridge.enable_ip_masquerade: "true"
      com.docker.network.bridge.enable_icc: "true"
      com.docker.network.driver.mtu: "1500"

  # 외부 네트워크 사용
  existing-net:
    external: true
    name: my-existing-network
```

### 13.3.4 서비스별 네트워크 설정

```yaml
services:
  web:
    image: nginx
    networks:
      frontend:
        # 고정 IP 할당
        ipv4_address: 172.28.5.10
        # 네트워크 별칭
        aliases:
          - webserver
          - nginx-server

      backend:
        ipv4_address: 172.29.5.10

networks:
  frontend:
    ipam:
      config:
        - subnet: 172.28.0.0/16
  backend:
    ipam:
      config:
        - subnet: 172.29.0.0/16
```

### 13.3.5 네트워크 우선순위

```yaml
services:
  api:
    image: myapi
    networks:
      - frontend
      - backend
      - monitoring

    # 네트워크 우선순위 지정 (낮을수록 우선)
    network_mode: service:web  # web 서비스와 네트워크 공유

# 또는
services:
  api:
    image: myapi
    network_mode: "host"        # 호스트 네트워크 사용
    # network_mode: "none"      # 네트워크 없음
    # network_mode: "container:web"  # 다른 컨테이너 네트워크 공유
```

---

## 13.4 볼륨 정의 (volumes)

### 13.4.1 기본 볼륨

```yaml
version: '3.8'

services:
  database:
    image: postgres:15
    volumes:
      # 명명된 볼륨
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
    driver: local
```

### 13.4.2 상세 볼륨 설정

```yaml
volumes:
  # 기본 로컬 볼륨
  simple-volume:

  # 드라이버 지정
  custom-volume:
    driver: local
    driver_opts:
      type: none
      device: /path/on/host
      o: bind

  # NFS 볼륨
  nfs-volume:
    driver: local
    driver_opts:
      type: nfs
      o: addr=192.168.1.100,rw,nfsvers=4
      device: ":/mnt/shared"

  # 레이블 지정
  labeled-volume:
    driver: local
    labels:
      project: myapp
      backup: daily
      environment: production

  # 외부 볼륨 사용
  external-volume:
    external: true
    name: my-existing-volume
```

### 13.4.3 서비스별 볼륨 마운트

```yaml
services:
  app:
    image: myapp
    volumes:
      # 짧은 문법
      - db-data:/app/data
      - ./src:/app/src
      - ./config:/app/config:ro

      # 긴 문법 (권장, 명확함)
      - type: volume
        source: db-data
        target: /app/data
        volume:
          nocopy: true  # 초기 복사 안 함

      - type: bind
        source: ./src
        target: /app/src
        read_only: false

      - type: bind
        source: ./config
        target: /app/config
        read_only: true

      # tmpfs (메모리)
      - type: tmpfs
        target: /app/cache
        tmpfs:
          size: 100000000  # 100MB
          mode: 1777

volumes:
  db-data:
```

### 13.4.4 볼륨 옵션

```yaml
services:
  database:
    image: postgres:15
    volumes:
      - type: volume
        source: pgdata
        target: /var/lib/postgresql/data
        volume:
          # 볼륨 드라이버 옵션
          nocopy: false  # 컨테이너 내용을 볼륨으로 복사
          subpath: postgres  # 볼륨 내 하위 경로

      - type: bind
        source: ./backup
        target: /backup
        bind:
          propagation: rprivate  # 마운트 전파 방식
          # rslave, rshared, rprivate

volumes:
  pgdata:
```

---

## 13.5 환경 변수 관리

### 13.5.1 environment (인라인 환경 변수)

```yaml
services:
  app:
    image: myapp
    environment:
      # 키-값 형식
      NODE_ENV: production
      PORT: 3000
      DEBUG: "false"

      # 배열 형식
      - NODE_ENV=production
      - PORT=3000
      - DEBUG=false

      # 호스트 환경 변수 전달
      DB_PASSWORD: ${DB_PASSWORD}
      API_KEY: ${API_KEY:-default_key}  # 기본값 지정
```

### 13.5.2 env_file (파일에서 로드)

```yaml
services:
  app:
    image: myapp
    env_file:
      # 단일 파일
      - .env

      # 여러 파일 (나중 파일이 우선)
      - .env.common
      - .env.production

      # 상대 경로
      - ./config/.env
```

**.env 파일 형식:**

```env
# 데이터베이스 설정
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_USER=postgres
DB_PASSWORD=secret

# 애플리케이션 설정
NODE_ENV=production
PORT=3000
LOG_LEVEL=info

# 외부 API
API_KEY=abc123def456
API_ENDPOINT=https://api.example.com

# 주석 가능
# 빈 줄 무시

# 따옴표는 선택사항
QUOTED="value with spaces"
UNQUOTED=simple_value
```

### 13.5.3 우선순위

```
환경 변수 우선순위 (높음 → 낮음):
1. Compose CLI에서 전달 (-e 플래그)
2. 셸 환경 변수
3. docker-compose.yml의 environment
4. env_file
5. Dockerfile의 ENV
```

**예시:**

```yaml
# docker-compose.yml
services:
  app:
    image: myapp
    environment:
      NODE_ENV: production    # 우선순위 3
      PORT: ${PORT:-3000}     # 우선순위 2 (셸 환경 변수)
    env_file:
      - .env                  # 우선순위 4
```

```bash
# 실행 시 오버라이드
PORT=4000 docker compose up  # PORT=4000 사용 (우선순위 2)

# 또는
docker compose run -e PORT=5000 app  # PORT=5000 사용 (우선순위 1)
```

### 13.5.4 .env 파일 (Compose 전용)

**프로젝트 루트의 .env:**

```env
# Compose 변수 치환용
COMPOSE_PROJECT_NAME=myapp
POSTGRES_VERSION=15
NODE_VERSION=18
APP_PORT=3000
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  database:
    image: postgres:${POSTGRES_VERSION:-14}
    # ${변수:-기본값} 형식

  app:
    build:
      context: .
      args:
        NODE_VERSION: ${NODE_VERSION}
    ports:
      - "${APP_PORT}:3000"
```

**실행:**

```bash
# 자동으로 .env 파일 로드
docker compose up

# 다른 환경 파일 사용
docker compose --env-file .env.production up

# 변수 확인
docker compose config
```

---

## 13.6 depends_on과 의존성 관리

### 13.6.1 기본 의존성

```yaml
services:
  web:
    image: nginx
    depends_on:
      - api

  api:
    image: myapi
    depends_on:
      - database
      - cache

  database:
    image: postgres

  cache:
    image: redis
```

**시작 순서:**

```
1. database, cache (동시 시작)
2. api (database, cache 시작 후)
3. web (api 시작 후)
```

**⚠️ 주의사항:**

```
depends_on은 "시작 순서"만 보장!
"준비 완료"는 보장하지 않음!

예시:
- database 컨테이너는 시작되었지만
- PostgreSQL이 아직 준비 안 됨
- api가 연결 시도 → 실패!
```

---

### 13.6.2 조건부 의존성 (v3.4+)

```yaml
services:
  web:
    image: nginx
    depends_on:
      api:
        condition: service_started

  api:
    image: myapi
    depends_on:
      database:
        condition: service_healthy
      cache:
        condition: service_started

  database:
    image: postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  cache:
    image: redis
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 3
```

**조건 종류:**

```yaml
depends_on:
  service_name:
    condition: service_started     # 시작됨 (기본)
    condition: service_healthy     # 헬스체크 통과
    condition: service_completed_successfully  # 성공적으로 종료 (배치 작업)
```

---

### 13.6.3 초기화 컨테이너 패턴

```yaml
services:
  # 데이터베이스 초기화 (한 번만 실행)
  db-init:
    image: myapp-db-init
    depends_on:
      database:
        condition: service_healthy
    command: python init_db.py
    restart: "no"  # 한 번만 실행

  # 마이그레이션 (한 번만 실행)
  db-migrate:
    image: myapp
    depends_on:
      db-init:
        condition: service_completed_successfully
    command: python manage.py migrate
    restart: "no"

  # 애플리케이션 (계속 실행)
  app:
    image: myapp
    depends_on:
      db-migrate:
        condition: service_completed_successfully
    restart: always

  database:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 10s
```

**실행 순서:**

```
1. database 시작 → 헬스체크 대기
2. db-init 실행 → 완료 후 종료
3. db-migrate 실행 → 완료 후 종료
4. app 시작 → 계속 실행
```

---

### 13.6.4 wait-for 스크립트 패턴

**wait-for-it.sh를 사용한 안전한 시작:**

```yaml
services:
  api:
    image: myapi
    depends_on:
      - database
    entrypoint: ["./wait-for-it.sh", "database:5432", "--timeout=60", "--"]
    command: ["npm", "start"]

  database:
    image: postgres:15
```

**wait-for-it.sh (컨테이너에 포함):**

```bash
#!/bin/bash
# 특정 호스트:포트가 준비될 때까지 대기

HOST=$1
shift
TIMEOUT=15

until nc -z -v -w30 $HOST 2>/dev/null; do
  echo "Waiting for $HOST..."
  sleep 1
  TIMEOUT=$((TIMEOUT - 1))
  if [ $TIMEOUT -le 0 ]; then
    echo "Timeout waiting for $HOST"
    exit 1
  fi
done

echo "$HOST is ready"
exec "$@"
```

---

## 13.7 healthcheck 설정

### 13.7.1 기본 헬스체크

```yaml
services:
  # 웹 서버
  web:
    image: nginx
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s      # 체크 간격
      timeout: 10s       # 타임아웃
      retries: 3         # 재시도 횟수
      start_period: 40s  # 시작 유예 시간

  # 셸 명령어 형식
  api:
    image: myapi
    healthcheck:
      test: curl -f http://localhost:3000/health || exit 1
      interval: 30s
      timeout: 10s
      retries: 3
```

### 13.7.2 데이터베이스별 헬스체크

```yaml
services:
  # PostgreSQL
  postgres:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  # MySQL
  mysql:
    image: mysql:8.0
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p$$MYSQL_ROOT_PASSWORD"]
      interval: 10s
      timeout: 5s
      retries: 3

  # MongoDB
  mongodb:
    image: mongo:7
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Redis
  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 3

  # Elasticsearch
  elasticsearch:
    image: elasticsearch:8.11.0
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
```

### 13.7.3 커스텀 헬스체크 엔드포인트

**애플리케이션 코드 (Node.js 예시):**

```javascript
// health.js
app.get('/health', async (req, res) => {
  try {
    // 데이터베이스 연결 확인
    await db.query('SELECT 1');

    // Redis 연결 확인
    await redis.ping();

    res.status(200).json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      checks: {
        database: 'ok',
        cache: 'ok'
      }
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      error: error.message
    });
  }
});
```

**docker-compose.yml:**

```yaml
services:
  api:
    build: .
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 13.7.4 헬스체크 비활성화

```yaml
services:
  # 헬스체크 없음 (기본)
  app1:
    image: myapp

  # 명시적 비활성화
  app2:
    image: myapp
    healthcheck:
      disable: true

  # Dockerfile의 헬스체크 상속
  app3:
    image: myapp-with-healthcheck
    # Dockerfile에 HEALTHCHECK 정의됨
```

---

## 13.8 restart 정책

### 13.8.1 재시작 정책 종류

```yaml
services:
  # 재시작 안 함 (기본)
  app1:
    image: myapp
    restart: "no"

  # 항상 재시작 (프로덕션 권장)
  app2:
    image: myapp
    restart: always

  # 수동 중지 전까지 재시작
  app3:
    image: myapp
    restart: unless-stopped

  # 실패 시에만 재시작
  app4:
    image: myapp
    restart: on-failure

  # 실패 시 재시도 횟수 제한
  app5:
    image: myapp
    restart: on-failure:5  # 최대 5번 재시도
```

### 13.8.2 정책별 동작

```
restart: "no"
├─ 컨테이너 종료 → 재시작 안 함
└─ 사용 사례: 일회성 배치 작업

restart: always
├─ 컨테이너 종료 → 항상 재시작
├─ Docker 데몬 재시작 → 자동 재시작
└─ 사용 사례: 웹 서버, API, 데이터베이스

restart: unless-stopped
├─ 컨테이너 종료 → 재시작
├─ 수동 중지 (docker stop) → 재시작 안 함
├─ Docker 데몬 재시작 → 수동 중지된 것만 제외하고 재시작
└─ 사용 사례: 대부분의 프로덕션 서비스

restart: on-failure
├─ 성공 종료 (exit 0) → 재시작 안 함
├─ 실패 종료 (exit 1-255) → 재시작
└─ 사용 사례: 불안정한 애플리케이션, 재시도 가능한 작업
```

### 13.8.3 실전 예시

```yaml
services:
  # 프로덕션 웹 서버
  web:
    image: nginx
    restart: unless-stopped
    # 수동 유지보수 시 중지 가능

  # 데이터베이스
  database:
    image: postgres:15
    restart: always
    # 항상 실행 유지

  # API 서버
  api:
    image: myapi
    restart: on-failure:3
    # 3번 실패 후 중지 (무한 재시작 방지)

  # 초기화 작업
  db-init:
    image: db-init
    restart: "no"
    # 한 번만 실행

  # 배치 작업
  cron-job:
    image: cron-job
    restart: unless-stopped
    # 스케줄러는 계속 실행
```

---

## 13.9 리소스 제한 (CPU, 메모리)

### 13.9.1 메모리 제한

```yaml
services:
  # 메모리 제한
  app1:
    image: myapp
    mem_limit: 512m        # 최대 512MB
    mem_reservation: 256m  # 최소 예약 256MB

  # 상세 설정
  app2:
    image: myapp
    deploy:
      resources:
        limits:
          memory: 1G       # 최대 1GB
        reservations:
          memory: 512M     # 최소 512MB

  # 스왑 제한
  app3:
    image: myapp
    mem_limit: 512m
    memswap_limit: 1g     # 메모리 + 스왑 = 1GB (스왑 512MB)
```

**메모리 초과 시:**

```
OOM (Out Of Memory) Killer 동작:
1. 메모리 사용량이 제한 초과
2. 컨테이너 강제 종료
3. restart 정책에 따라 재시작
```

---

### 13.9.2 CPU 제한

```yaml
services:
  # CPU 코어 수 제한
  app1:
    image: myapp
    cpus: '1.5'  # 1.5 코어

  # CPU 점유율 제한
  app2:
    image: myapp
    cpu_percent: 50  # 50% 제한

  # CPU 공유 비율 (상대적)
  app3:
    image: myapp
    cpu_shares: 512  # 기본 1024

  # 상세 설정
  app4:
    image: myapp
    deploy:
      resources:
        limits:
          cpus: '2'       # 최대 2 코어
        reservations:
          cpus: '1'       # 최소 1 코어

  # 특정 CPU 코어 할당
  app5:
    image: myapp
    cpuset: '0,1'  # CPU 코어 0, 1만 사용
```

---

### 13.9.3 실전 리소스 할당 예시

```yaml
version: '3.8'

services:
  # 프론트엔드 (가벼움)
  frontend:
    image: myfrontend
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M
    restart: unless-stopped

  # API 서버 (중간)
  api:
    image: myapi
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '1'
          memory: 512M
    restart: unless-stopped

  # 데이터베이스 (무거움)
  database:
    image: postgres:15
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
        reservations:
          cpus: '2'
          memory: 2G
    restart: always

  # 캐시 (가벼움)
  cache:
    image: redis:7-alpine
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
    restart: always

  # 백그라운드 워커 (중간)
  worker:
    image: myworker
    deploy:
      resources:
        limits:
          cpus: '1.5'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      replicas: 3  # 3개 인스턴스
    restart: unless-stopped
```

---

### 13.9.4 리소스 모니터링

```bash
# 컨테이너 리소스 사용량 확인
docker compose top

# 실시간 통계
docker stats

# 출력:
# CONTAINER        CPU %    MEM USAGE / LIMIT     MEM %    NET I/O          BLOCK I/O
# myapp-api-1      15.2%    450MiB / 1GiB         43.95%   1.2MB / 800KB    5MB / 2MB
# myapp-db-1       5.8%     1.2GiB / 4GiB         30.00%   500KB / 1.5MB    100MB / 50MB
```

---

## 13.10 포트 및 네트워크 설정

### 13.10.1 포트 매핑

```yaml
services:
  # 기본 포트 매핑
  web1:
    image: nginx
    ports:
      - "8080:80"        # 호스트:컨테이너

  # 여러 포트
  web2:
    image: myapp
    ports:
      - "3000:3000"      # HTTP
      - "3001:3001"      # WebSocket
      - "9229:9229"      # 디버거

  # 특정 인터페이스
  web3:
    image: myapp
    ports:
      - "127.0.0.1:3000:3000"  # localhost만

  # 랜덤 호스트 포트
  web4:
    image: myapp
    ports:
      - "3000"           # 호스트는 랜덤 할당

  # UDP 포트
  dns:
    image: dns-server
    ports:
      - "53:53/udp"

  # TCP + UDP
  vpn:
    image: openvpn
    ports:
      - "1194:1194/tcp"
      - "1194:1194/udp"

  # 포트 범위
  media:
    image: media-server
    ports:
      - "8000-8010:8000-8010"
```

### 13.10.2 긴 문법 (권장)

```yaml
services:
  web:
    image: nginx
    ports:
      - target: 80         # 컨테이너 포트
        published: 8080    # 호스트 포트
        protocol: tcp      # tcp | udp
        mode: host         # host | ingress (Swarm)

      - target: 443
        published: 8443
        protocol: tcp
        mode: host
```

### 13.10.3 expose (내부만 공개)

```yaml
services:
  # 외부 접근 (포트 매핑)
  web:
    image: nginx
    ports:
      - "80:80"

  # 내부 접근만 (같은 네트워크)
  api:
    image: myapi
    expose:
      - "3000"      # 포트 메타데이터 (실제 매핑 없음)
    networks:
      - backend

  database:
    image: postgres
    expose:
      - "5432"
    networks:
      - backend

networks:
  backend:
```

**차이점:**

```
ports:
- 호스트 포트와 매핑
- 외부에서 접근 가능
- 포트 충돌 가능

expose:
- 메타데이터만 (실제 매핑 없음)
- 같은 네트워크 내부만 접근
- 포트 충돌 없음
```

---

### 13.10.4 네트워크 별칭

```yaml
services:
  api:
    image: myapi
    networks:
      backend:
        aliases:
          - api-service
          - backend-api
          - api.internal

  # 다른 서비스에서 접근 가능:
  # - http://api:3000 (서비스 이름)
  # - http://api-service:3000 (별칭1)
  # - http://backend-api:3000 (별칭2)
  # - http://api.internal:3000 (별칭3)

networks:
  backend:
```

---

### 13.10.5 링크 (레거시, 비권장)

```yaml
# ❌ 옛날 방식 (사용하지 마세요)
services:
  web:
    image: nginx
    links:
      - database
      - cache:redis

  database:
    image: postgres

  cache:
    image: redis

# ✅ 현대적 방식 (권장)
services:
  web:
    image: nginx
    networks:
      - mynetwork
    depends_on:
      - database
      - cache

  database:
    image: postgres
    networks:
      - mynetwork

  cache:
    image: redis
    networks:
      - mynetwork

networks:
  mynetwork:
```

---

## 13.11 완전한 프로덕션 예제

```yaml
version: '3.8'

# ==================== X-템플릿 (재사용 가능한 설정) ====================
x-common-healthcheck: &common-healthcheck
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s

x-common-resources: &common-resources
  limits:
    cpus: '1'
    memory: 512M
  reservations:
    cpus: '0.5'
    memory: 256M

x-common-logging: &common-logging
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"

# ==================== 서비스 ====================
services:
  # Nginx 리버스 프록시
  nginx:
    image: nginx:alpine
    ports:
      - target: 80
        published: 80
        mode: host
      - target: 443
        published: 443
        mode: host
    volumes:
      - type: bind
        source: ./nginx/nginx.conf
        target: /etc/nginx/nginx.conf
        read_only: true
      - type: bind
        source: ./nginx/ssl
        target: /etc/nginx/ssl
        read_only: true
      - nginx-logs:/var/log/nginx
    networks:
      - frontend
    depends_on:
      frontend:
        condition: service_started
      api:
        condition: service_healthy
    healthcheck:
      <<: *common-healthcheck
      test: ["CMD", "wget", "-q", "--spider", "http://localhost/health"]
    deploy:
      resources:
        <<: *common-resources
    logging:
      <<: *common-logging
    restart: unless-stopped
    labels:
      com.example.service: "nginx"
      com.example.tier: "proxy"

  # 프론트엔드
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
      args:
        NODE_VERSION: "18"
        BUILD_ENV: production
    image: myapp-frontend:${VERSION:-latest}
    environment:
      API_URL: http://api:4000
    networks:
      - frontend
    depends_on:
      - api
    healthcheck:
      <<: *common-healthcheck
      test: ["CMD", "curl", "-f", "http://localhost:3000/"]
    deploy:
      resources:
        <<: *common-resources
    logging:
      <<: *common-logging
    restart: unless-stopped
    labels:
      com.example.service: "frontend"
      com.example.tier: "presentation"

  # API 서버
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    image: myapp-api:${VERSION:-latest}
    environment:
      NODE_ENV: production
      PORT: 4000
      DATABASE_URL: postgresql://${DB_USER:-postgres}:${DB_PASSWORD}@database:5432/${DB_NAME:-myapp}
      REDIS_URL: redis://cache:6379
      JWT_SECRET: ${JWT_SECRET}
      LOG_LEVEL: ${LOG_LEVEL:-info}
    env_file:
      - .env.production
    networks:
      - frontend
      - backend
    depends_on:
      database:
        condition: service_healthy
      cache:
        condition: service_healthy
    healthcheck:
      <<: *common-healthcheck
      test: ["CMD", "curl", "-f", "http://localhost:4000/health"]
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '1'
          memory: 512M
    logging:
      <<: *common-logging
    restart: unless-stopped
    labels:
      com.example.service: "api"
      com.example.tier: "application"

  # PostgreSQL 데이터베이스
  database:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME:-myapp}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - type: volume
        source: postgres-data
        target: /var/lib/postgresql/data
      - type: bind
        source: ./postgres/init.sql
        target: /docker-entrypoint-initdb.d/init.sql
        read_only: true
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
        reservations:
          cpus: '2'
          memory: 2G
    logging:
      <<: *common-logging
    restart: always
    labels:
      com.example.service: "database"
      com.example.tier: "data"

  # Redis 캐시
  cache:
    image: redis:7-alpine
    command: >
      redis-server
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
      --appendonly yes
      --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    networks:
      - backend
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 5s
      timeout: 3s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
    logging:
      <<: *common-logging
    restart: always
    labels:
      com.example.service: "cache"
      com.example.tier: "data"

  # 백그라운드 워커
  worker:
    build:
      context: ./worker
      dockerfile: Dockerfile.prod
    image: myapp-worker:${VERSION:-latest}
    environment:
      NODE_ENV: production
      DATABASE_URL: postgresql://${DB_USER:-postgres}:${DB_PASSWORD}@database:5432/${DB_NAME:-myapp}
      REDIS_URL: redis://cache:6379
    env_file:
      - .env.production
    networks:
      - backend
    depends_on:
      database:
        condition: service_healthy
      cache:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: '1.5'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      replicas: 2
    logging:
      <<: *common-logging
    restart: unless-stopped
    labels:
      com.example.service: "worker"
      com.example.tier: "background"

# ==================== 네트워크 ====================
networks:
  frontend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
    labels:
      com.example.network: "frontend"

  backend:
    driver: bridge
    internal: true
    ipam:
      config:
        - subnet: 172.21.0.0/16
    labels:
      com.example.network: "backend"

# ==================== 볼륨 ====================
volumes:
  postgres-data:
    driver: local
    labels:
      com.example.volume: "postgres-data"
      com.example.backup: "daily"

  redis-data:
    driver: local
    labels:
      com.example.volume: "redis-data"
      com.example.backup: "daily"

  nginx-logs:
    driver: local
    labels:
      com.example.volume: "nginx-logs"
```

**.env.production:**

```env
# 버전
VERSION=1.0.0

# 데이터베이스
DB_USER=postgres
DB_PASSWORD=strongpassword123
DB_NAME=myapp_production

# Redis
REDIS_PASSWORD=redispassword456

# JWT
JWT_SECRET=supersecretjwtkey789

# 로깅
LOG_LEVEL=warn
```

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: 환경 변수 실수로 평문 패스워드 커밋

**상황**: 신입 개발자가 docker-compose.yml에 데이터베이스 비밀번호를 하드코딩하여 Git에 커밋했습니다.

```yaml
# ❌ 주니어 개발자가 작성한 코드
version: '3.8'

services:
  database:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: mySecretPassword123  # 하드코딩!
      POSTGRES_USER: admin
```

**문제점**:
- 문제 1: 비밀번호가 Git 히스토리에 영구 기록됨
- 문제 2: 팀 전체가 접근 가능한 저장소에 노출
- 문제 3: 프로덕션과 개발 환경의 비밀번호 분리 불가
- 왜 이 문제가 발생하는가: 환경 변수와 설정 파일의 차이를 이해하지 못함

**해결책**:
```yaml
# ✅ 올바른 코드
version: '3.8'

services:
  database:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}  # 환경 변수 사용
      POSTGRES_USER: ${DB_USER:-postgres}  # 기본값 설정
    env_file:
      - .env  # .env 파일에서 로드
```

**.env 파일 (Git에서 제외):**
```env
DB_PASSWORD=mySecretPassword123
DB_USER=admin
```

**.gitignore:**
```
.env
.env.production
.env.local
```

**배운 점**:
- 💡 팁 1: 모든 민감 정보는 .env 파일로 분리
- 💡 팁 2: .env 파일은 반드시 .gitignore에 추가
- 💡 팁 3: .env.example 파일로 필요한 변수 목록 공유
- 💡 팁 4: ${변수:-기본값} 문법으로 안전한 기본값 제공

---

### 시나리오 2: depends_on만 믿고 DB 연결 실패

**상황**: API 서버가 데이터베이스보다 먼저 시작되어 연결 실패 에러가 발생합니다.

```yaml
# ❌ 문제가 있는 코드
version: '3.8'

services:
  api:
    image: myapi
    depends_on:
      - database
    environment:
      DB_HOST: database

  database:
    image: postgres:15
```

**에러 메시지**:
```
Error: connect ECONNREFUSED database:5432
API server crashed: Database connection failed
```

**문제점**:
- 문제 1: depends_on은 시작 순서만 보장, 준비 상태는 보장 안 함
- 문제 2: PostgreSQL이 준비되려면 10-30초 소요
- 문제 3: API가 즉시 연결 시도하다 실패
- 왜 이 문제가 발생하는가: depends_on의 동작 방식을 오해

**해결책 1: healthcheck + condition 사용**
```yaml
# ✅ 올바른 코드 - healthcheck 사용
version: '3.8'

services:
  api:
    image: myapi
    depends_on:
      database:
        condition: service_healthy  # 헬스체크 통과까지 대기
    environment:
      DB_HOST: database

  database:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 10
      start_period: 30s  # 최대 30초 대기
```

**해결책 2: 애플리케이션 레벨 재시도**
```javascript
// Node.js 예시 - API 서버 코드
const connectWithRetry = async () => {
  const maxRetries = 10;
  const retryDelay = 3000;

  for (let i = 0; i < maxRetries; i++) {
    try {
      await db.connect();
      console.log('Database connected successfully');
      return;
    } catch (error) {
      console.log(`DB connection failed (${i + 1}/${maxRetries}). Retrying in ${retryDelay}ms...`);
      await new Promise(resolve => setTimeout(resolve, retryDelay));
    }
  }

  throw new Error('Failed to connect to database after multiple retries');
};

connectWithRetry();
```

**배운 점**:
- 💡 팁 1: depends_on은 시작 순서만 보장 (준비 상태 X)
- 💡 팁 2: 중요한 서비스는 반드시 healthcheck 설정
- 💡 팁 3: 애플리케이션 코드에도 재시도 로직 구현
- 💡 팁 4: start_period로 초기 대기 시간 충분히 제공

---

### 시나리오 3: 포트 충돌로 컨테이너 시작 실패

**상황**: 로컬에서 이미 포트 3000을 사용 중인데, docker-compose로 같은 포트를 사용하려 해서 에러 발생.

```yaml
# ❌ 문제가 있는 코드
version: '3.8'

services:
  app:
    image: myapp
    ports:
      - "3000:3000"  # 로컬에서 이미 3000 포트 사용 중!
```

**에러 메시지**:
```
Error: Bind for 0.0.0.0:3000 failed: port is already allocated
```

**해결책 1: 다른 호스트 포트 사용**
```yaml
# ✅ 해결 방법 1 - 다른 포트 매핑
version: '3.8'

services:
  app:
    image: myapp
    ports:
      - "3001:3000"  # 호스트 3001 → 컨테이너 3000
```

**해결책 2: 환경 변수로 포트 설정**
```yaml
# ✅ 해결 방법 2 - 유연한 포트 설정
version: '3.8'

services:
  app:
    image: myapp
    ports:
      - "${APP_PORT:-3000}:3000"  # .env에서 설정 가능
```

**.env:**
```env
APP_PORT=3001
```

**해결책 3: 포트 사용 확인 후 정리**
```bash
# 포트 사용 중인 프로세스 확인 (Linux/Mac)
lsof -i :3000

# 포트 사용 중인 프로세스 확인 (Windows)
netstat -ano | findstr :3000

# 프로세스 종료 (Linux/Mac)
kill -9 <PID>

# 프로세스 종료 (Windows)
taskkill /PID <PID> /F
```

**배운 점**:
- 💡 팁 1: 포트 충돌 에러는 먼저 사용 중인 프로세스 확인
- 💡 팁 2: 호스트 포트는 유연하게 변경 가능 (3001:3000)
- 💡 팁 3: 환경 변수로 포트 관리하면 팀원마다 다른 포트 사용 가능
- 💡 팁 4: expose로 내부 포트만 공개하면 충돌 없음

---

### 시나리오 4: 볼륨 마운트 경로 실수로 데이터 유실

**상황**: Windows 경로를 잘못 입력하여 볼륨 마운트가 실패하고 데이터가 사라졌습니다.

```yaml
# ❌ 문제가 있는 코드 (Windows)
version: '3.8'

services:
  database:
    image: postgres:15
    volumes:
      - C:\Users\myuser\data:/var/lib/postgresql/data  # 잘못된 경로!
```

**에러 또는 문제**:
- 볼륨이 마운트되지 않음
- 컨테이너 재시작 시 데이터 사라짐
- 경로 파싱 에러 발생

**해결책**:
```yaml
# ✅ 올바른 코드
version: '3.8'

services:
  database:
    image: postgres:15
    volumes:
      # 방법 1: 명명된 볼륨 사용 (권장)
      - postgres-data:/var/lib/postgresql/data

      # 방법 2: 상대 경로 사용
      - ./data:/var/lib/postgresql/data

      # 방법 3: Windows 절대 경로 (슬래시로 변환)
      - /c/Users/myuser/data:/var/lib/postgresql/data

volumes:
  postgres-data:
    driver: local
```

**플랫폼별 경로 작성법**:
```yaml
# Linux/Mac
volumes:
  - /home/user/data:/app/data
  - ./data:/app/data  # 상대 경로

# Windows (Git Bash, WSL)
volumes:
  - /c/Users/user/data:/app/data  # C:\를 /c/로 변환
  - ./data:/app/data  # 상대 경로

# Windows (명명된 볼륨 권장)
volumes:
  - mydata:/app/data

volumes:
  mydata:
```

**배운 점**:
- 💡 팁 1: Windows에서는 명명된 볼륨 사용이 가장 안전
- 💡 팁 2: 절대 경로보다 상대 경로가 이식성 좋음
- 💡 팁 3: Windows 경로는 슬래시(/)로 변환 필요
- 💡 팁 4: 중요 데이터는 반드시 볼륨 백업 설정

---

## ❓ FAQ

<details>
<summary><strong>Q1: docker-compose.yml과 docker-compose.yaml 중 어느 확장자를 써야 하나요?</strong></summary>

**A**: 둘 다 사용 가능하지만, **docker-compose.yml이 관례**입니다.

**상세 설명**:
- Docker Compose는 .yml과 .yaml 모두 인식
- 하지만 공식 문서와 대부분의 프로젝트는 .yml 사용
- GitHub, GitLab 등도 .yml을 기본으로 표시

**예시**:
```bash
# 둘 다 작동
docker compose -f docker-compose.yml up
docker compose -f docker-compose.yaml up

# 파일명이 docker-compose.yml이면 -f 플래그 생략 가능
docker compose up
```

**실무 팁**:
💡 일관성을 위해 프로젝트 전체에서 하나의 확장자로 통일하세요.

</details>

<details>
<summary><strong>Q2: version 필드를 생략해도 되나요?</strong></summary>

**A**: Docker Compose v2부터는 version 필드가 **선택사항**입니다.

**상세 설명**:
- Docker Compose v1: version 필드 필수
- Docker Compose v2 (2020년 이후): version 필드 무시됨
- 하위 호환성을 위해 version: '3.8' 유지 권장

**예시**:
```yaml
# 최신 방식 (version 생략)
services:
  web:
    image: nginx

# 기존 방식 (하위 호환)
version: '3.8'
services:
  web:
    image: nginx
```

**실무 팁**:
💡 레거시 시스템 지원이 필요하면 version: '3.8' 유지, 아니면 생략 가능.

</details>

<details>
<summary><strong>Q3: 같은 이미지로 여러 서비스를 실행하려면 어떻게 하나요?</strong></summary>

**A**: 서비스명을 다르게 정의하거나, **deploy.replicas** 또는 **docker compose up --scale**을 사용합니다.

**예시 1: 서비스 중복 정의**
```yaml
services:
  worker1:
    image: myworker
    environment:
      WORKER_ID: 1

  worker2:
    image: myworker
    environment:
      WORKER_ID: 2

  worker3:
    image: myworker
    environment:
      WORKER_ID: 3
```

**예시 2: scale 명령어**
```yaml
services:
  worker:
    image: myworker

# 실행
# docker compose up --scale worker=3
```

**예시 3: deploy.replicas (Swarm)**
```yaml
services:
  worker:
    image: myworker
    deploy:
      replicas: 3
```

**실무 팁**:
💡 로컬 개발: 서비스 중복 정의
💡 프로덕션: scale 또는 Kubernetes로 관리

</details>

<details>
<summary><strong>Q4: 컨테이너 간 통신은 어떻게 하나요?</strong></summary>

**A**: 같은 네트워크에 있는 서비스는 **서비스 이름으로 접근** 가능합니다.

**상세 설명**:
- Docker Compose는 자동으로 네트워크 생성
- 각 서비스는 서비스명이 DNS 이름이 됨
- 포트는 컨테이너 내부 포트 사용

**예시**:
```yaml
services:
  api:
    image: myapi
    environment:
      # database:5432로 접근 (호스트 포트 아님!)
      DB_HOST: database
      DB_PORT: 5432
      CACHE_HOST: redis
      CACHE_PORT: 6379

  database:
    image: postgres:15
    # 외부 노출 안 해도 내부 통신 가능

  redis:
    image: redis:7
```

**API 서버 코드 예시**:
```javascript
// database:5432로 연결 (서비스명 사용)
const db = new Pool({
  host: 'database',  // 서비스명
  port: 5432,        // 컨테이너 포트
  user: 'postgres',
  password: process.env.DB_PASSWORD
});

// redis:6379로 연결
const redis = new Redis({
  host: 'redis',     // 서비스명
  port: 6379
});
```

**실무 팁**:
💡 서비스명은 DNS처럼 작동 (IP 불필요)
💡 포트는 컨테이너 내부 포트 사용 (호스트 포트 X)

</details>

<details>
<summary><strong>Q5: .env 파일의 변수가 적용 안 되는데 왜 그런가요?</strong></summary>

**A**: .env 파일은 **docker-compose.yml 변수 치환용**이고, **컨테이너 환경 변수**는 env_file로 전달해야 합니다.

**상세 설명**:
- .env 파일: docker-compose.yml의 ${변수} 치환
- env_file: 컨테이너 내부 환경 변수 전달
- 둘의 용도가 다름!

**예시**:
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    image: node:${NODE_VERSION}  # .env에서 치환
    environment:
      API_KEY: ${API_KEY}  # .env에서 치환
    env_file:
      - .env.app  # 컨테이너로 전달
```

**.env (Compose 변수 치환용):**
```env
NODE_VERSION=18
API_KEY=abc123
DB_PASSWORD=secret
```

**.env.app (컨테이너 환경 변수):**
```env
NODE_ENV=production
PORT=3000
LOG_LEVEL=info
```

**동작 방식**:
```
1. Docker Compose가 .env 읽음
2. ${NODE_VERSION} → 18로 치환
3. image: node:18로 변환
4. .env.app을 컨테이너에 전달
5. 컨테이너 내부에서 NODE_ENV 등 사용 가능
```

**실무 팁**:
💡 .env: Compose 설정 관리 (이미지 태그, 포트 등)
💡 env_file: 애플리케이션 설정 (API 키, 데이터베이스 등)

</details>

<details>
<summary><strong>Q6: 프로덕션에서 docker-compose를 써도 되나요?</strong></summary>

**A**: **단일 호스트 배포**에는 괜찮지만, **대규모/고가용성**은 Kubernetes 권장합니다.

**상세 설명**:
- Docker Compose: 단일 서버, 소규모 프로젝트
- Kubernetes: 멀티 서버, 대규모, 오토스케일링, 장애 복구

**Docker Compose 프로덕션 적합 사례**:
- 소규모 웹 애플리케이션 (월 방문자 < 10만)
- 내부 도구 (관리자 페이지, 모니터링 대시보드)
- 개발/스테이징 환경
- 단일 서버 배포

**Kubernetes 필요 사례**:
- 대규모 트래픽 (월 방문자 > 100만)
- 멀티 리전 배포
- 자동 스케일링 필요
- 무중단 배포, 장애 복구 자동화

**절충안: Docker Swarm**
```yaml
version: '3.8'

services:
  web:
    image: myapp
    deploy:
      replicas: 3  # 3개 인스턴스
      update_config:
        parallelism: 1  # 롤링 업데이트
      restart_policy:
        condition: on-failure
```

**실무 팁**:
💡 소규모: Docker Compose로 충분
💡 중규모: Docker Swarm 고려
💡 대규모: Kubernetes 필수

</details>

<details>
<summary><strong>Q7: docker-compose up과 docker-compose up -d의 차이는?</strong></summary>

**A**: **-d 플래그**는 백그라운드(detached) 모드로 실행합니다.

**비교**:
```bash
# 포어그라운드 (기본)
docker compose up
→ 터미널에 로그 출력
→ Ctrl+C로 종료 시 컨테이너도 중지
→ 개발 중 디버깅에 유용

# 백그라운드 (-d)
docker compose up -d
→ 백그라운드 실행
→ 터미널 바로 반환
→ 컨테이너는 계속 실행
→ 프로덕션, 장기 실행 서비스에 적합
```

**로그 확인**:
```bash
# 백그라운드 실행 후 로그 보기
docker compose up -d
docker compose logs -f  # 실시간 로그
docker compose logs -f api  # 특정 서비스만
```

**중지 방법**:
```bash
# 포어그라운드: Ctrl+C
# 백그라운드: 명령어로 중지
docker compose down
```

**실무 팁**:
💡 개발: docker compose up (로그 즉시 확인)
💡 프로덕션: docker compose up -d (백그라운드)
💡 디버깅: docker compose logs -f --tail=100

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. docker-compose.yml 파일의 역할과 장점은 무엇인가요?</strong></summary>

**모범 답안 포인트**
- 포인트 1: 멀티 컨테이너 환경을 YAML 파일로 정의
- 포인트 2: 단일 명령어(docker compose up)로 전체 환경 실행
- 포인트 3: 팀 전체가 동일한 환경 공유 가능
- 포인트 4: 버전 관리 가능 (Git으로 관리)

**예시 답변**
> "docker-compose.yml은 여러 컨테이너로 구성된 애플리케이션을 정의하는 설정 파일입니다.
> 예를 들어 웹 서버, API, 데이터베이스, 캐시를 개별적으로 docker run으로 실행하는 대신,
> docker-compose.yml 하나로 모든 서비스를 정의하고 docker compose up 한 줄로 실행할 수 있습니다.
> 이를 통해 팀원들이 동일한 개발 환경을 쉽게 구축할 수 있고, Git으로 버전 관리도 가능해집니다."

**꼬리 질문**
- Q: docker run과 비교했을 때 어떤 점이 더 나은가요?
- A: docker run은 컨테이너 하나씩 수동 실행, docker compose는 여러 컨테이너를 한 번에 관리하고 네트워크/볼륨 자동 설정

**실무 연관**
- 프로젝트에서 프론트엔드, 백엔드, DB를 docker-compose로 한 번에 실행
- 신규 팀원 온보딩 시 docker compose up 한 줄로 환경 구축

</details>

<details>
<summary><strong>2. depends_on의 동작 방식과 한계는 무엇인가요?</strong></summary>

**모범 답안 포인트**
- 포인트 1: 컨테이너 시작 순서를 제어
- 포인트 2: 시작 순서만 보장, 준비 상태는 보장 안 함
- 포인트 3: healthcheck와 함께 사용 권장
- 포인트 4: condition으로 대기 조건 설정 가능

**예시 답변**
> "depends_on은 컨테이너 시작 순서를 지정하는 옵션입니다.
> 예를 들어 API가 데이터베이스에 의존한다면 depends_on: database를 설정하여 DB가 먼저 시작되도록 합니다.
> 하지만 중요한 점은 depends_on이 '시작 순서'만 보장하지, 'DB가 준비 완료'되었는지는 보장하지 않는다는 것입니다.
> 실무에서는 healthcheck를 함께 설정하거나 애플리케이션 코드에 재시도 로직을 추가합니다."

**꼬리 질문**
- Q: healthcheck 없이 depends_on만 사용하면 어떤 문제가 생기나요?
- A: DB 컨테이너는 시작되었지만 PostgreSQL이 준비 안 된 상태에서 API가 연결 시도해 실패

**실무 연관**
- API 서버가 DB 연결 실패로 크래시하는 문제
- depends_on + healthcheck + 재시도 로직 3중 방어

</details>

<details>
<summary><strong>3. 환경 변수 관리 방법 (.env vs env_file vs environment)을 설명하세요.</strong></summary>

**모범 답안 포인트**
- 포인트 1: .env는 docker-compose.yml 변수 치환용
- 포인트 2: env_file은 컨테이너 환경 변수 전달용
- 포인트 3: environment는 인라인으로 직접 지정
- 포인트 4: 민감 정보는 .env 파일로 분리하고 .gitignore 추가

**예시 답변**
> ".env 파일은 docker-compose.yml에서 ${변수} 형태로 사용되는 값을 치환하는 용도입니다.
> 예를 들어 이미지 태그나 포트 번호를 .env에 정의합니다.
> env_file은 컨테이너 내부의 환경 변수로 전달되어 애플리케이션 코드에서 process.env로 접근합니다.
> environment는 YAML에서 직접 환경 변수를 지정하는 방식이고요.
> 실무에서는 DB 비밀번호 같은 민감 정보는 .env 파일에 넣고 Git에서 제외합니다."

**꼬리 질문**
- Q: 우선순위는 어떻게 되나요?
- A: CLI 플래그 > 셸 환경 변수 > environment > env_file > Dockerfile ENV

**실무 연관**
- .env.example로 필요한 변수 목록 공유
- 프로덕션/개발 환경별 .env 파일 분리

</details>

<details>
<summary><strong>4. 볼륨(volume)과 바인드 마운트(bind mount)의 차이는?</strong></summary>

**모범 답안 포인트**
- 포인트 1: 볼륨은 Docker가 관리하는 저장소
- 포인트 2: 바인드 마운트는 호스트 디렉토리 직접 마운트
- 포인트 3: 볼륨이 이식성 좋고 안전함
- 포인트 4: 바인드 마운트는 개발 시 코드 수정 즉시 반영에 유용

**예시 답변**
> "볼륨은 Docker가 관리하는 독립적인 저장소로, /var/lib/docker/volumes에 저장됩니다.
> 플랫폼 독립적이고 백업/복원이 쉬워서 프로덕션에 적합합니다.
> 바인드 마운트는 호스트의 특정 경로를 컨테이너에 직접 연결하는 방식으로,
> 개발 중 ./src를 마운트하면 코드 수정이 즉시 반영되어 편리합니다.
> 하지만 호스트 경로에 의존하므로 이식성이 떨어집니다."

**예시 코드**
```yaml
services:
  app:
    image: myapp
    volumes:
      # 볼륨 (프로덕션)
      - app-data:/app/data

      # 바인드 마운트 (개발)
      - ./src:/app/src

volumes:
  app-data:
```

**실무 연관**
- 프로덕션: 볼륨으로 데이터베이스 저장
- 개발: 바인드 마운트로 핫 리로딩

</details>

<details>
<summary><strong>5. 네트워크 설정이 없는데도 컨테이너 간 통신이 되는 이유는?</strong></summary>

**모범 답안 포인트**
- 포인트 1: Docker Compose가 자동으로 기본 네트워크 생성
- 포인트 2: 모든 서비스가 같은 네트워크에 연결됨
- 포인트 3: 서비스명이 DNS 이름으로 작동
- 포인트 4: 컨테이너 내부 포트로 통신

**예시 답변**
> "Docker Compose는 프로젝트당 기본 브리지 네트워크를 자동으로 생성합니다.
> 네트워크 이름은 보통 '<프로젝트명>_default'이고, 모든 서비스가 이 네트워크에 연결됩니다.
> Docker의 내부 DNS가 서비스명을 IP로 해석해주기 때문에,
> API 서비스에서 'database:5432'로 접근하면 자동으로 database 컨테이너의 IP를 찾아 연결합니다.
> 따라서 별도 설정 없이도 서비스명만으로 통신이 가능합니다."

**꼬리 질문**
- Q: 외부에서 접근하려면 어떻게 하나요?
- A: ports로 호스트 포트 매핑 (예: "80:80")

**실무 연관**
- 마이크로서비스 간 통신을 서비스명으로 간단히 구현
- 외부 노출이 필요 없는 DB는 ports 설정 생략

</details>

<details>
<summary><strong>6. restart 정책의 종류와 각각의 용도는?</strong></summary>

**모범 답안 포인트**
- 포인트 1: "no" - 재시작 안 함 (기본값)
- 포인트 2: always - 항상 재시작
- 포인트 3: unless-stopped - 수동 중지 전까지 재시작
- 포인트 4: on-failure - 실패 시만 재시작

**예시 답변**
> "restart 정책은 4가지가 있습니다.
> 'no'는 컨테이너가 종료되어도 재시작하지 않으며, 일회성 배치 작업에 적합합니다.
> 'always'는 종료 시 항상 재시작하므로 프로덕션 서비스에 사용됩니다.
> 'unless-stopped'는 always와 비슷하지만 수동으로 중지한 경우는 재시작하지 않아 유지보수 시 편리합니다.
> 'on-failure'는 exit code가 0이 아닐 때만 재시작하여 불안정한 서비스에 적합합니다."

**예시 코드**
```yaml
services:
  web:
    restart: unless-stopped  # 프로덕션 웹 서버

  database:
    restart: always  # 데이터베이스

  migration:
    restart: "no"  # 마이그레이션 (한 번만)
```

**실무 연관**
- 웹 서버는 unless-stopped로 유지보수 시 수동 제어
- DB는 always로 절대 중단 방지

</details>

<details>
<summary><strong>7. healthcheck의 목적과 설정 방법은?</strong></summary>

**모범 답안 포인트**
- 포인트 1: 컨테이너가 실제로 정상 작동하는지 확인
- 포인트 2: 시작됨 ≠ 준비 완료 상태
- 포인트 3: interval, timeout, retries 설정
- 포인트 4: depends_on과 함께 사용하여 의존성 보장

**예시 답변**
> "healthcheck는 컨테이너가 단순히 실행 중인 것을 넘어 실제로 요청을 처리할 수 있는 상태인지 확인합니다.
> 예를 들어 PostgreSQL 컨테이너가 시작되어도 DB 초기화에 10초가 걸리는데,
> healthcheck 없이는 API가 즉시 연결 시도하다 실패합니다.
> pg_isready 명령어로 DB 준비 상태를 확인하고, interval로 체크 주기, retries로 재시도 횟수를 설정합니다.
> depends_on의 condition: service_healthy와 함께 사용하면 준비 완료까지 대기할 수 있습니다."

**예시 코드**
```yaml
services:
  database:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s  # 10초마다 체크
      timeout: 5s    # 5초 안에 응답
      retries: 5     # 5번 실패 시 unhealthy
```

**실무 연관**
- API 서버의 /health 엔드포인트로 healthcheck
- 모니터링 도구(Prometheus)가 healthcheck 상태 수집

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. x-templates (YAML 앵커)를 활용한 설정 재사용 방법을 설명하세요.</strong></summary>

**모범 답안 포인트**
- 포인트 1: YAML 앵커(&)와 병합(<<)으로 중복 제거
- 포인트 2: x-로 시작하는 최상위 키는 Docker가 무시
- 포인트 3: 공통 설정을 템플릿화하여 재사용
- 포인트 4: 유지보수성과 가독성 향상

**예시 답변**
> "대규모 프로젝트에서는 healthcheck, 리소스 제한, 로깅 설정이 여러 서비스에 반복됩니다.
> x-로 시작하는 확장 필드에 공통 설정을 앵커(&)로 정의하고,
> 각 서비스에서 <<: *앵커명으로 병합하여 재사용합니다.
> 예를 들어 x-common-healthcheck에 interval, timeout을 정의하면,
> 모든 서비스에서 <<: *common-healthcheck 한 줄로 동일한 healthcheck를 적용할 수 있습니다.
> 설정 변경 시 한 곳만 수정하면 되어 유지보수가 쉽습니다."

**예시 코드**
```yaml
x-common-healthcheck: &common-healthcheck
  interval: 30s
  timeout: 10s
  retries: 3

x-common-resources: &common-resources
  limits:
    cpus: '1'
    memory: 512M

services:
  api:
    image: myapi
    healthcheck:
      <<: *common-healthcheck
      test: ["CMD", "curl", "-f", "http://localhost/health"]
    deploy:
      resources:
        <<: *common-resources

  worker:
    image: myworker
    healthcheck:
      <<: *common-healthcheck
      test: ["CMD", "curl", "-f", "http://localhost/status"]
    deploy:
      resources:
        <<: *common-resources
```

**실무 연관**
- 마이크로서비스 10개 이상 시 설정 중복 제거
- 프로덕션 표준 설정을 템플릿으로 관리

</details>

<details>
<summary><strong>2. 프로덕션 환경에서 리소스 제한을 설정하는 이유와 방법은?</strong></summary>

**모범 답안 포인트**
- 포인트 1: 한 컨테이너의 폭주가 전체 시스템 영향 방지
- 포인트 2: CPU, 메모리 limits와 reservations 구분
- 포인트 3: OOM Killer 동작 방지
- 포인트 4: 비용 예측 가능성 향상

**예시 답변**
> "프로덕션에서 리소스 제한을 설정하지 않으면,
> 특정 컨테이너가 메모리 누수로 전체 호스트 메모리를 소진하거나 CPU를 독점하여 다른 서비스에 영향을 줍니다.
> deploy.resources에서 limits는 최대 사용량, reservations는 보장된 최소 자원을 의미합니다.
> 예를 들어 API 서버에 memory: 1G 제한을 두면, 1GB 초과 시 OOM Killer가 컨테이너를 종료하고 재시작합니다.
> CPU는 cpus: '2'로 최대 2코어까지 사용하도록 제한합니다.
> 이를 통해 리소스 사용을 예측 가능하게 하고 비용을 관리할 수 있습니다."

**예시 코드**
```yaml
services:
  api:
    image: myapi
    deploy:
      resources:
        limits:
          cpus: '2'      # 최대 2코어
          memory: 1G     # 최대 1GB
        reservations:
          cpus: '1'      # 최소 1코어 보장
          memory: 512M   # 최소 512MB 보장
```

**성능 측정**
```bash
# 리소스 사용량 모니터링
docker stats

# 출력 예시:
# CONTAINER  CPU %   MEM USAGE / LIMIT   MEM %
# api        45.2%   750MiB / 1GiB       73.24%
```

**실무 연관**
- 트래픽 급증 시에도 다른 서비스는 정상 작동
- AWS/GCP에서 인스턴스 크기 최적화

</details>

<details>
<summary><strong>3. 멀티 스테이지 빌드와 docker-compose를 연계하는 방법은?</strong></summary>

**모범 답안 포인트**
- 포인트 1: Dockerfile의 target 단계를 docker-compose에서 선택
- 포인트 2: 개발/프로덕션 환경별로 다른 단계 사용
- 포인트 3: 빌드 인자(args)로 환경 변수 전달
- 포인트 4: 이미지 크기와 보안 향상

**예시 답변**
> "멀티 스테이지 빌드는 Dockerfile에서 여러 FROM을 사용하여 단계별로 빌드하는 방법입니다.
> docker-compose.yml에서 build.target으로 특정 단계를 선택할 수 있습니다.
> 예를 들어 개발 환경에서는 target: development로 개발 도구가 포함된 단계를,
> 프로덕션에서는 target: production으로 최적화된 최종 단계만 사용합니다.
> args로 NODE_ENV 같은 변수를 전달하여 빌드 시점에 환경을 설정합니다.
> 이를 통해 개발과 프로덕션 이미지를 하나의 Dockerfile로 관리하면서도 크기와 보안을 최적화할 수 있습니다."

**Dockerfile 예시**
```dockerfile
# 개발 단계
FROM node:18 AS development
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]

# 프로덕션 단계
FROM node:18-alpine AS production
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

**docker-compose.yml 예시**
```yaml
services:
  # 개발 환경
  app-dev:
    build:
      context: .
      target: development
      args:
        NODE_ENV: development
    volumes:
      - ./src:/app/src  # 핫 리로딩

  # 프로덕션 환경
  app-prod:
    build:
      context: .
      target: production
      args:
        NODE_ENV: production
```

**실무 연관**
- 개발: 전체 도구 포함 (1GB)
- 프로덕션: 최소 의존성만 (100MB)

</details>

<details>
<summary><strong>4. 네트워크 분리를 통한 보안 강화 전략을 설명하세요.</strong></summary>

**모범 답안 포인트**
- 포인트 1: 프론트엔드/백엔드 네트워크 분리
- 포인트 2: 데이터베이스는 내부 네트워크만
- 포인트 3: internal: true로 외부 접근 차단
- 포인트 4: 최소 권한 원칙 적용

**예시 답변**
> "프로덕션 환경에서는 네트워크를 계층별로 분리하여 공격 표면을 최소화합니다.
> frontend 네트워크는 nginx와 웹 서비스만 연결하고,
> backend 네트워크는 API, 데이터베이스, 캐시만 연결합니다.
> 데이터베이스는 backend 네트워크만 속하므로 프론트엔드에서 직접 접근할 수 없습니다.
> 또한 internal: true 옵션으로 backend 네트워크를 외부 인터넷과 격리하여,
> 설령 API 서버가 침해되어도 외부로 데이터를 전송할 수 없게 합니다."

**예시 코드**
```yaml
services:
  nginx:
    image: nginx
    networks:
      - frontend
    ports:
      - "80:80"

  api:
    image: myapi
    networks:
      - frontend  # nginx와 통신
      - backend   # DB와 통신

  database:
    image: postgres:15
    networks:
      - backend  # API만 접근 가능
    # 외부 포트 노출 안 함!

networks:
  frontend:
    driver: bridge

  backend:
    driver: bridge
    internal: true  # 외부 인터넷 차단
```

**보안 효과**
```
공격자가 nginx 침해 시:
  → frontend 네트워크만 접근
  → database는 backend 네트워크라 접근 불가

공격자가 API 침해 시:
  → backend는 internal: true
  → 외부로 데이터 유출 불가
```

**실무 연관**
- 금융권/의료 시스템의 필수 보안 요구사항
- PCI-DSS, HIPAA 컴플라이언스 충족

</details>

<details>
<summary><strong>5. docker-compose 오버라이드(override) 파일의 활용 방법은?</strong></summary>

**모범 답안 포인트**
- 포인트 1: docker-compose.override.yml 자동 병합
- 포인트 2: 환경별 설정 분리 (개발/프로덕션)
- 포인트 3: -f 플래그로 여러 파일 조합
- 포인트 4: 팀원별 로컬 설정 분리

**예시 답변**
> "docker-compose.override.yml은 기본 docker-compose.yml에 자동으로 병합되는 설정 파일입니다.
> 공통 설정은 docker-compose.yml에, 환경별 차이는 오버라이드 파일에 작성합니다.
> 예를 들어 개발 환경에서는 볼륨 마운트와 디버그 포트를 추가하고,
> 프로덕션에서는 리소스 제한과 헬스체크를 강화합니다.
> -f 플래그로 여러 파일을 조합할 수 있어,
> docker compose -f docker-compose.yml -f docker-compose.prod.yml up 처럼 실행합니다.
> 이를 통해 환경별 설정을 깔끔하게 분리할 수 있습니다."

**파일 구조**
```
project/
├── docker-compose.yml          # 공통 설정
├── docker-compose.override.yml # 개발 환경 (자동 병합)
├── docker-compose.prod.yml     # 프로덕션 환경
└── docker-compose.local.yml    # 개인별 설정 (.gitignore)
```

**docker-compose.yml (공통)**
```yaml
services:
  api:
    image: myapi
    environment:
      NODE_ENV: production
```

**docker-compose.override.yml (개발)**
```yaml
services:
  api:
    volumes:
      - ./src:/app/src  # 핫 리로딩
    ports:
      - "9229:9229"  # 디버거
    environment:
      NODE_ENV: development  # 오버라이드
```

**docker-compose.prod.yml (프로덕션)**
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
    restart: unless-stopped
```

**실행 방법**
```bash
# 개발 (자동으로 override 병합)
docker compose up

# 프로덕션
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**실무 연관**
- 팀원마다 다른 포트 사용 (docker-compose.local.yml)
- CI/CD에서 환경별 배포 스크립트

</details>

---

## 📝 핵심 정리

### 이 장에서 배운 핵심 개념

| 개념 | 설명 | 핵심 키워드 |
|------|------|-------------|
| **services** | 컨테이너 정의 | image, build, ports, environment |
| **networks** | 컨테이너 간 통신 | frontend, backend, internal |
| **volumes** | 데이터 영속화 | 명명된 볼륨, 바인드 마운트 |
| **depends_on** | 시작 순서 제어 | condition, service_healthy |
| **healthcheck** | 준비 상태 확인 | interval, timeout, retries |
| **restart** | 재시작 정책 | always, unless-stopped, on-failure |
| **deploy.resources** | 리소스 제한 | cpus, memory, limits, reservations |

### 필수 명령어 정리

| 명령어 | 용도 | 예시 |
|--------|------|------|
| `docker compose up` | 모든 서비스 시작 | `docker compose up -d` |
| `docker compose down` | 모든 서비스 중지 및 삭제 | `docker compose down -v` |
| `docker compose ps` | 실행 중인 컨테이너 확인 | `docker compose ps` |
| `docker compose logs` | 로그 확인 | `docker compose logs -f api` |
| `docker compose exec` | 컨테이너 명령 실행 | `docker compose exec api sh` |
| `docker compose build` | 이미지 빌드 | `docker compose build --no-cache` |
| `docker compose config` | 설정 검증 및 출력 | `docker compose config` |
| `docker compose restart` | 서비스 재시작 | `docker compose restart api` |

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] 모든 민감 정보는 .env 파일로 분리하고 .gitignore에 추가
- [ ] 중요한 서비스에는 healthcheck 설정
- [ ] 프로덕션에서는 리소스 제한(CPU, 메모리) 설정
- [ ] 네트워크를 프론트엔드/백엔드로 분리
- [ ] 데이터베이스 볼륨은 명명된 볼륨 사용
- [ ] depends_on과 healthcheck를 함께 사용
- [ ] 버전 관리를 위해 Git 사용
- [ ] .env.example로 필요한 변수 목록 공유

#### ❌ 하지 말아야 할 것
- [ ] 비밀번호를 docker-compose.yml에 하드코딩
- [ ] depends_on만 믿고 재시도 로직 생략
- [ ] 프로덕션에서 바인드 마운트로 중요 데이터 저장
- [ ] 모든 서비스를 하나의 네트워크에 연결
- [ ] 리소스 제한 없이 프로덕션 배포
- [ ] container_name으로 스케일링 불가능하게 만들기
- [ ] 로그 로테이션 없이 무한 로그 축적

### 성능/보안 체크리스트

#### 성능
- [ ] 리소스 제한으로 공정한 자원 분배
- [ ] healthcheck 간격을 적절히 설정 (너무 짧으면 부하)
- [ ] 로그 드라이버 설정으로 디스크 절약
- [ ] 불필요한 서비스는 profiles로 선택적 실행
- [ ] 캐시 레이어 최적화 (build.cache_from)

#### 보안
- [ ] 민감 정보는 .env 파일로 분리
- [ ] 데이터베이스는 외부 포트 노출 금지
- [ ] backend 네트워크에 internal: true 설정
- [ ] 최소 권한 원칙 (user 설정)
- [ ] 읽기 전용 볼륨 사용 (read_only: true)
- [ ] 신뢰할 수 있는 이미지만 사용 (공식 이미지)
- [ ] 이미지 태그는 latest 대신 구체적 버전 명시

---

## 🔗 관련 기술

**docker-compose와 함께 사용하는 기술들**

| 기술 | 관계 | 학습 우선순위 |
|------|------|---------------|
| **Docker** | Compose의 기반 기술 | ⭐⭐⭐⭐⭐ |
| **Nginx** | 리버스 프록시, 로드 밸런서 | ⭐⭐⭐⭐ |
| **PostgreSQL** | 데이터베이스 컨테이너화 | ⭐⭐⭐⭐ |
| **Redis** | 캐시/세션 저장소 | ⭐⭐⭐⭐ |
| **Traefik** | 자동 리버스 프록시 | ⭐⭐⭐ |
| **Docker Swarm** | 멀티 호스트 오케스트레이션 | ⭐⭐⭐ |
| **Kubernetes** | 대규모 컨테이너 관리 | ⭐⭐⭐ |
| **GitHub Actions** | CI/CD 자동화 | ⭐⭐⭐⭐ |

---

## 🚀 다음 단계

### 다음 장 미리보기: 14장 - Docker Compose 심화

- **배울 내용 1**: 오버라이드 파일로 환경별 설정 분리
- **배울 내용 2**: profiles로 선택적 서비스 실행
- **배울 내용 3**: extends로 설정 상속 및 재사용
- **배울 내용 4**: 실제 프로젝트에 Docker Compose 적용

### 이 장과의 연결점

```
13장에서 배운 docker-compose.yml 기본 문법
    ↓
14장에서 고급 기능과 패턴 학습
    ↓
최종적으로 프로덕션 수준의 멀티 컨테이너 환경 구축
```

### 준비하면 좋을 것들

```bash
# 다음 장 실습을 위한 준비
# 1. 실제 프로젝트 준비
git clone https://github.com/yourusername/your-project.git

# 2. 멀티 환경 설정 파일 생성
touch docker-compose.override.yml
touch docker-compose.prod.yml

# 3. 환경 변수 파일 준비
cp .env.example .env
```

---

## 🎉 축하합니다!

**학습 완료 후 메시지**

**이제 여러분은**:
✅ docker-compose.yml의 모든 설정 항목을 이해하고 사용할 수 있습니다
✅ 멀티 컨테이너 환경을 단일 파일로 정의하고 관리할 수 있습니다
✅ 프로덕션 수준의 네트워크, 볼륨, 리소스 설정을 할 수 있습니다
✅ 환경 변수와 의존성을 안전하게 관리할 수 있습니다
✅ healthcheck와 restart 정책으로 안정적인 서비스를 구성할 수 있습니다

**다음 단계**:
- [ ] 14장: Docker Compose 심화 학습
- [ ] 실전 프로젝트에 docker-compose 적용
- [ ] 면접 질문 복습 및 답변 연습

**실무 적용 팁**:
- 💼 회사 프로젝트에 docker-compose 도입 제안
- 💼 팀원들에게 docker compose up 한 줄로 환경 구축 공유
- 💼 프로덕션 배포 자동화 (CI/CD 연계)

---

**다음 장으로 이동**: [다음: 14장 Docker Compose 심화 →](14-docker-compose-심화.md)

**이전 장으로 돌아가기**: [← 이전: 12장 Docker Compose 기초](12-docker-compose-기초.md)

**목차로 돌아가기**: [📚 전체 목차](README.md)