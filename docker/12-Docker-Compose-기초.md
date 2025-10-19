# 섹션 12: Docker Compose 기초

> **학습 목표**: Docker Compose를 사용하여 여러 컨테이너를 YAML 파일 하나로 정의하고 관리할 수 있습니다.

**⏱️ 예상 학습 시간**: 2-3시간
**난이도**: ⭐⭐☆☆☆ (2개/5개)

---

## 📚 목차
- [Docker Compose란?](#121-docker-compose란)
- [왜 Docker Compose를 사용하나?](#122-왜-docker-compose를-사용하나)
- [docker-compose.yml 구조](#123-docker-composeyml-구조)
- [기본 명령어](#124-기본-명령어)
- [실전 예제](#125-실전-예제)
- [환경 변수 및 .env 파일](#126-환경-변수-및-env-파일)
- [실생활 비유로 이해하기](#-실생활-비유로-이해하기)
- [수치로 보는 효과](#-수치로-보는-효과)
- [주니어 시나리오](#-주니어-시나리오)
- [FAQ](#-faq)
- [면접 질문 리스트](#-면접-질문-리스트)
- [핵심 정리](#-핵심-정리)
- [다음 단계](#127-다음-단계)

---

## 12.1 Docker Compose란?

### 12.1.1 개념 이해

**Docker Compose**는 여러 개의 Docker 컨테이너를 정의하고 실행하기 위한 도구입니다.
YAML 파일 하나로 애플리케이션의 모든 서비스를 설정하고, 단일 명령어로 전체 스택을 실행할 수 있습니다.

**실생활 비유: 요리 레시피 vs 단일 식재료**

```
[Docker CLI만 사용 = 식재료 하나씩 요리]
1. 당근 씻기: docker run carrot
2. 양파 썰기: docker run onion
3. 고기 굽기: docker run meat
4. 국물 끓이기: docker run broth
5. 모두 섞기: docker network connect ...

→ 번거롭고 실수하기 쉬움 ❌

[Docker Compose = 완성된 레시피]
카레 레시피 (docker-compose.yml):
- 재료 목록
- 조리 순서
- 양념 비율
- 완성 시간

실행: docker-compose up
→ 한 번에 완성! ✅
```

---

### 12.1.2 Docker CLI vs Docker Compose

#### Docker CLI로 WordPress 실행

```bash
# 1. 네트워크 생성
docker network create wordpress-net

# 2. 볼륨 생성
docker volume create mysql-data
docker volume create wordpress-data

# 3. MySQL 컨테이너 실행
docker run -d \
  --name mysql \
  --network wordpress-net \
  -v mysql-data:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=wordpress \
  -e MYSQL_USER=wpuser \
  -e MYSQL_PASSWORD=wppassword \
  mysql:8.0

# 4. WordPress 컨테이너 실행
docker run -d \
  --name wordpress \
  --network wordpress-net \
  -v wordpress-data:/var/www/html \
  -p 8080:80 \
  -e WORDPRESS_DB_HOST=mysql \
  -e WORDPRESS_DB_USER=wpuser \
  -e WORDPRESS_DB_PASSWORD=wppassword \
  -e WORDPRESS_DB_NAME=wordpress \
  --depends-on mysql \
  wordpress:latest

# 문제점:
# ❌ 명령어가 길고 복잡함
# ❌ 재실행 시 모든 명령어 다시 입력
# ❌ 팀원과 공유하기 어려움
# ❌ 실수하기 쉬움
```

#### Docker Compose로 WordPress 실행

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    networks:
      - wordpress-net
    volumes:
      - mysql-data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wpuser
      MYSQL_PASSWORD: wppassword

  wordpress:
    image: wordpress:latest
    networks:
      - wordpress-net
    volumes:
      - wordpress-data:/var/www/html
    ports:
      - "8080:80"
    environment:
      WORDPRESS_DB_HOST: mysql
      WORDPRESS_DB_USER: wpuser
      WORDPRESS_DB_PASSWORD: wppassword
      WORDPRESS_DB_NAME: wordpress
    depends_on:
      - mysql

networks:
  wordpress-net:

volumes:
  mysql-data:
  wordpress-data:
```

**실행:**

```bash
# 한 줄로 전체 스택 실행!
docker-compose up -d

# 장점:
# ✅ 간결하고 명확함
# ✅ Git으로 버전 관리 가능
# ✅ 팀원과 쉽게 공유
# ✅ 재사용 가능
# ✅ 실수 방지
```

---

### 12.1.3 Docker Compose 버전

```
Docker Compose V1 (레거시)
├─ 명령어: docker-compose (하이픈)
├─ Python으로 작성
├─ 별도 설치 필요
└─ 더 이상 권장하지 않음 ⚠️

Docker Compose V2 (현재)
├─ 명령어: docker compose (공백)
├─ Go로 작성
├─ Docker CLI 플러그인
├─ Docker Desktop에 포함
└─ 권장 버전 ✅
```

**버전 확인:**

```bash
# V2 (권장)
docker compose version
# Docker Compose version v2.23.0

# V1 (레거시)
docker-compose version
# docker-compose version 1.29.2
```

**이 가이드에서는 V2 문법을 사용합니다.**

---

## 12.2 왜 Docker Compose를 사용하나?

### 12.2.1 장점

```
1. 선언적 설정 (Declarative Configuration)
   "무엇을 원하는지" 정의 → Docker가 알아서 실행

   docker-compose.yml에 원하는 최종 상태 기술
   → docker compose up 실행
   → 자동으로 네트워크, 볼륨, 컨테이너 생성

2. 재현 가능한 환경 (Reproducible Environment)
   팀원 A의 환경 = 팀원 B의 환경 = 프로덕션 환경

   "내 컴퓨터에서는 되는데요?" 문제 해결 ✅

3. 버전 관리 (Version Control)
   Git에 docker-compose.yml 커밋
   → 인프라 변경 이력 추적
   → 롤백 가능

4. 환경 분리 (Environment Isolation)
   프로젝트마다 독립된 환경

   프로젝트A: MySQL 5.7, Redis 6
   프로젝트B: MySQL 8.0, Redis 7
   → 충돌 없이 동시 실행

5. 간단한 명령어
   docker compose up     # 시작
   docker compose down   # 정리
   docker compose logs   # 로그 확인
```

---

### 12.2.2 사용 사례

```
✅ 로컬 개발 환경
   - 개발자 컴퓨터에서 전체 스택 실행
   - DB, 캐시, 메시지 큐 등 한 번에 시작

✅ 자동화 테스트
   - CI/CD에서 테스트 환경 자동 구성
   - 테스트 완료 후 자동 정리

✅ 단일 호스트 배포
   - 소규모 프로덕션 환경
   - 스테이징 서버

✅ 프로토타이핑
   - 빠른 POC (Proof of Concept)
   - 데모 환경 구축

❌ 대규모 클러스터 (권장하지 않음)
   → Kubernetes, Docker Swarm 사용
```

---

## 12.3 docker-compose.yml 구조

### 12.3.1 기본 구조

```yaml
version: '3.8'  # Compose 파일 버전

services:       # 컨테이너 정의
  service1:
    # 서비스 설정
  service2:
    # 서비스 설정

networks:       # 네트워크 정의 (선택)
  network1:

volumes:        # 볼륨 정의 (선택)
  volume1:

configs:        # 설정 파일 (선택, Swarm)
  config1:

secrets:        # 비밀 정보 (선택, Swarm)
  secret1:
```

---

### 12.3.2 최소 예제

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
```

**실행:**

```bash
docker compose up -d
# [+] Running 2/2
#  ✔ Network myproject_default  Created
#  ✔ Container myproject-web-1   Started

curl http://localhost:8080
# Welcome to nginx!

docker compose down
# [+] Running 2/2
#  ✔ Container myproject-web-1   Removed
#  ✔ Network myproject_default   Removed
```

---

### 12.3.3 서비스 설정 옵션

#### 이미지 관련

```yaml
services:
  # 방법 1: 기존 이미지 사용
  app1:
    image: nginx:alpine

  # 방법 2: Dockerfile로 빌드
  app2:
    build: .

  # 방법 3: 빌드 컨텍스트 지정
  app3:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
      args:
        NODE_VERSION: 18
```

#### 네트워크 및 포트

```yaml
services:
  web:
    image: nginx:alpine
    ports:
      # 호스트:컨테이너
      - "8080:80"
      - "8443:443"
      # 특정 인터페이스
      - "127.0.0.1:3000:3000"
      # 랜덤 호스트 포트
      - "80"
    networks:
      - frontend
      - backend
```

#### 볼륨 및 바인드 마운트

```yaml
services:
  app:
    image: myapp
    volumes:
      # 명명된 볼륨
      - data:/app/data

      # 바인드 마운트
      - ./src:/app/src

      # 읽기 전용
      - ./config:/app/config:ro

      # 긴 문법 (명확함, 권장)
      - type: volume
        source: data
        target: /app/data

      - type: bind
        source: ./src
        target: /app/src
```

#### 환경 변수

```yaml
services:
  app:
    image: myapp
    environment:
      # 방법 1: 키-값 쌍
      NODE_ENV: production
      PORT: 3000

      # 방법 2: 호스트 환경 변수 전달
      DB_PASSWORD: ${DB_PASSWORD}

    # 방법 3: .env 파일 사용
    env_file:
      - .env
      - .env.production
```

#### 의존성 및 시작 순서

```yaml
services:
  web:
    image: nginx
    depends_on:
      - api
      - cache

  api:
    image: myapi
    depends_on:
      database:
        condition: service_healthy

  database:
    image: postgres:15
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
```

#### 재시작 정책

```yaml
services:
  app:
    image: myapp
    restart: always  # 항상 재시작
    # restart: unless-stopped  # 수동 중지 전까지
    # restart: on-failure  # 오류 시만
    # restart: no  # 재시작 안 함 (기본)
```

#### 리소스 제한

```yaml
services:
  app:
    image: myapp
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '1'
          memory: 512M
```

---

### 12.3.4 완전한 예제

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  # ==================== 프론트엔드 ====================
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        NODE_VERSION: 18
    ports:
      - "3000:3000"
    volumes:
      - ./frontend/src:/app/src
      - frontend-modules:/app/node_modules
    environment:
      - NODE_ENV=development
      - API_URL=http://api:4000
    networks:
      - frontend-net
    depends_on:
      - api
    restart: unless-stopped

  # ==================== 백엔드 API ====================
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "4000:4000"
    volumes:
      - ./backend/src:/app/src
      - backend-modules:/app/node_modules
    environment:
      NODE_ENV: development
      PORT: 4000
      DATABASE_URL: postgresql://postgres:secret@database:5432/myapp
      REDIS_URL: redis://cache:6379
    env_file:
      - .env
    networks:
      - frontend-net
      - backend-net
    depends_on:
      database:
        condition: service_healthy
      cache:
        condition: service_started
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M

  # ==================== 데이터베이스 ====================
  database:
    image: postgres:15-alpine
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp
    networks:
      - backend-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    restart: always

  # ==================== 캐시 ====================
  cache:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis-data:/data
    networks:
      - backend-net
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    restart: always

  # ==================== 리버스 프록시 ====================
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - nginx-logs:/var/log/nginx
    networks:
      - frontend-net
    depends_on:
      - frontend
      - api
    restart: always

# ==================== 네트워크 ====================
networks:
  frontend-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

  backend-net:
    driver: bridge
    internal: true  # 외부 접근 차단
    ipam:
      config:
        - subnet: 172.21.0.0/16

# ==================== 볼륨 ====================
volumes:
  postgres-data:
    driver: local
    labels:
      project: myapp
      backup: daily

  redis-data:
    driver: local

  frontend-modules:
    driver: local

  backend-modules:
    driver: local

  nginx-logs:
    driver: local
```

---

## 12.4 기본 명령어

### 12.4.1 up - 서비스 시작

```bash
# 기본 실행 (포그라운드)
docker compose up

# 백그라운드 실행 (데몬)
docker compose up -d

# 특정 서비스만 시작
docker compose up -d database cache

# 이미지 강제 재빌드
docker compose up -d --build

# 컨테이너 재생성 (설정 변경 시)
docker compose up -d --force-recreate

# 고아 컨테이너 제거
docker compose up -d --remove-orphans

# 스케일 조정
docker compose up -d --scale api=3
```

**출력 예시:**

```bash
docker compose up -d

# [+] Running 8/8
#  ✔ Network myapp_frontend-net     Created    0.1s
#  ✔ Network myapp_backend-net      Created    0.1s
#  ✔ Volume "myapp_postgres-data"   Created    0.0s
#  ✔ Volume "myapp_redis-data"      Created    0.0s
#  ✔ Container myapp-database-1     Started    1.2s
#  ✔ Container myapp-cache-1        Started    1.0s
#  ✔ Container myapp-api-1          Started    2.3s
#  ✔ Container myapp-frontend-1     Started    2.5s
```

---

### 12.4.2 down - 서비스 중지 및 제거

```bash
# 기본 중지 (컨테이너, 네트워크 제거)
docker compose down

# 볼륨도 함께 제거
docker compose down -v

# 이미지도 함께 제거
docker compose down --rmi all
# --rmi local: 빌드된 이미지만 제거
# --rmi all: 모든 이미지 제거

# 타임아웃 지정
docker compose down -t 30  # 30초 대기 후 강제 종료
```

**출력 예시:**

```bash
docker compose down

# [+] Running 8/8
#  ✔ Container myapp-frontend-1    Removed    1.2s
#  ✔ Container myapp-api-1         Removed    1.5s
#  ✔ Container myapp-cache-1       Removed    0.3s
#  ✔ Container myapp-database-1    Removed    0.5s
#  ✔ Network myapp_frontend-net    Removed    0.1s
#  ✔ Network myapp_backend-net     Removed    0.1s
#  ✔ Volume myapp_redis-data       Removed    0.0s
#  ✔ Volume myapp_postgres-data    Removed    0.0s
```

---

### 12.4.3 start / stop / restart

```bash
# 기존 컨테이너 시작 (새로 생성 안 함)
docker compose start
docker compose start api database

# 컨테이너 중지 (제거 안 함)
docker compose stop
docker compose stop api database

# 재시작
docker compose restart
docker compose restart api
```

**차이점:**

```
up vs start:
┌────────────────────────────────────────────────┐
│ docker compose up                               │
├────────────────────────────────────────────────┤
│ 1. 이미지 빌드 (필요 시)                        │
│ 2. 네트워크 생성                                │
│ 3. 볼륨 생성                                    │
│ 4. 컨테이너 생성                                │
│ 5. 컨테이너 시작                                │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ docker compose start                            │
├────────────────────────────────────────────────┤
│ 1. 기존 컨테이너 시작 (이미 생성된 것만)        │
└────────────────────────────────────────────────┘

down vs stop:
┌────────────────────────────────────────────────┐
│ docker compose down                             │
├────────────────────────────────────────────────┤
│ 1. 컨테이너 중지                                │
│ 2. 컨테이너 제거                                │
│ 3. 네트워크 제거                                │
│ 4. (선택) 볼륨 제거                             │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ docker compose stop                             │
├────────────────────────────────────────────────┤
│ 1. 컨테이너 중지 (제거 안 함)                   │
└────────────────────────────────────────────────┘
```

---

### 12.4.4 ps - 컨테이너 목록

```bash
# 모든 컨테이너 상태 확인
docker compose ps

# 출력:
# NAME                IMAGE              STATUS         PORTS
# myapp-api-1         myapp-api:latest   Up 2 minutes   0.0.0.0:4000->4000/tcp
# myapp-database-1    postgres:15        Up 2 minutes   5432/tcp
# myapp-cache-1       redis:7-alpine     Up 2 minutes   6379/tcp

# 모든 컨테이너 (중지된 것 포함)
docker compose ps -a

# 특정 서비스만
docker compose ps api

# 간단한 출력 (이름만)
docker compose ps -q
# myapp-api-1
# myapp-database-1
# myapp-cache-1

# JSON 형식
docker compose ps --format json
```

---

### 12.4.5 logs - 로그 확인

```bash
# 모든 서비스 로그
docker compose logs

# 특정 서비스 로그
docker compose logs api

# 여러 서비스 로그
docker compose logs api database

# 실시간 로그 (follow)
docker compose logs -f

# 최근 N줄만
docker compose logs --tail 100

# 타임스탬프 포함
docker compose logs -t

# 조합 사용
docker compose logs -f --tail 50 api
```

**출력 예시:**

```bash
docker compose logs -f --tail 20 api

# api-1  | [2024-01-15 10:30:45] Server starting...
# api-1  | [2024-01-15 10:30:46] Connected to database
# api-1  | [2024-01-15 10:30:46] Server listening on port 4000
# api-1  | [2024-01-15 10:31:10] GET /api/users 200 25ms
# api-1  | [2024-01-15 10:31:15] POST /api/users 201 150ms
```

---

### 12.4.6 exec - 컨테이너 내부 명령 실행

```bash
# 기본 사용
docker compose exec <service> <command>

# 예시: 데이터베이스 접속
docker compose exec database psql -U postgres

# 셸 실행
docker compose exec api sh
docker compose exec api bash

# 환경 변수 전달
docker compose exec -e DEBUG=true api node debug.js

# 작업 디렉토리 지정
docker compose exec -w /app/src api npm test

# 루트 사용자로 실행
docker compose exec -u root api apk add curl

# 인덱스 지정 (스케일된 서비스)
docker compose exec --index 2 api sh
```

---

### 12.4.7 build - 이미지 빌드

```bash
# 모든 서비스 빌드
docker compose build

# 특정 서비스만 빌드
docker compose build api

# 캐시 없이 빌드
docker compose build --no-cache

# 병렬 빌드
docker compose build --parallel

# 빌드 인자 전달
docker compose build --build-arg NODE_VERSION=20
```

---

### 12.4.8 pull - 이미지 다운로드

```bash
# 모든 서비스 이미지 다운로드
docker compose pull

# 특정 서비스만
docker compose pull database cache

# 다운로드 실패 시 무시
docker compose pull --ignore-pull-failures

# 조용한 모드
docker compose pull -q
```

---

### 12.4.9 config - 설정 검증 및 확인

```bash
# 설정 파일 검증
docker compose config

# 환경 변수 치환 후 출력
docker compose config

# 서비스 이름만 출력
docker compose config --services
# api
# database
# cache

# 볼륨 이름만 출력
docker compose config --volumes
# postgres-data
# redis-data

# 해시 값 출력 (변경 감지)
docker compose config --hash="*"
```

---

### 12.4.10 기타 유용한 명령어

#### top - 프로세스 확인

```bash
# 모든 컨테이너의 프로세스
docker compose top

# 출력:
# myapp-api-1
# UID    PID     PPID    CMD
# node   12345   12330   node server.js

# myapp-database-1
# UID      PID     PPID    CMD
# postgres 12400   12380   postgres
```

#### pause / unpause - 일시 중지

```bash
# 컨테이너 일시 중지
docker compose pause

# 재개
docker compose unpause

# 특정 서비스만
docker compose pause api
docker compose unpause api
```

#### rm - 중지된 컨테이너 제거

```bash
# 중지된 컨테이너 제거
docker compose rm

# 확인 없이 제거
docker compose rm -f

# 중지 및 제거
docker compose rm -sf

# 익명 볼륨도 제거
docker compose rm -v
```

#### images - 이미지 목록

```bash
# 사용 중인 이미지 확인
docker compose images

# 출력:
# CONTAINER        REPOSITORY       TAG       SIZE
# myapp-api-1      myapp-api        latest    350MB
# myapp-database-1 postgres         15        230MB
# myapp-cache-1    redis            7-alpine  30MB
```

---

## 12.5 실전 예제

### 12.5.1 예제 1: LAMP 스택 (Linux, Apache, MySQL, PHP)

**프로젝트 구조:**

```
lamp-project/
├── docker-compose.yml
├── www/
│   └── index.php
├── mysql/
│   └── init.sql
└── apache/
    └── Dockerfile
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  # Apache + PHP
  web:
    build:
      context: ./apache
    ports:
      - "8080:80"
    volumes:
      - ./www:/var/www/html
    networks:
      - lamp-net
    depends_on:
      - database
    restart: unless-stopped

  # MySQL
  database:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: lampdb
      MYSQL_USER: lampuser
      MYSQL_PASSWORD: lamppassword
    volumes:
      - mysql-data:/var/lib/mysql
      - ./mysql/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - lamp-net
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-prootpassword"]
      interval: 10s
      timeout: 5s
      retries: 3
    restart: always

  # phpMyAdmin
  phpmyadmin:
    image: phpmyadmin:latest
    ports:
      - "8081:80"
    environment:
      PMA_HOST: database
      PMA_USER: root
      PMA_PASSWORD: rootpassword
    networks:
      - lamp-net
    depends_on:
      - database

networks:
  lamp-net:
    driver: bridge

volumes:
  mysql-data:
```

**apache/Dockerfile:**

```dockerfile
FROM php:8.2-apache

# PHP 확장 설치
RUN docker-php-ext-install mysqli pdo pdo_mysql

# Apache 모듈 활성화
RUN a2enmod rewrite

# 작업 디렉토리
WORKDIR /var/www/html
```

**www/index.php:**

```php
<?php
$host = 'database';
$db = 'lampdb';
$user = 'lampuser';
$pass = 'lamppassword';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$db", $user, $pass);
    echo "<h1>Connection Successful!</h1>";
    echo "<p>Connected to database: $db</p>";

    // 테이블 조회
    $stmt = $pdo->query("SELECT * FROM users");
    echo "<h2>Users:</h2><ul>";
    while ($row = $stmt->fetch()) {
        echo "<li>{$row['name']} ({$row['email']})</li>";
    }
    echo "</ul>";
} catch (PDOException $e) {
    echo "Connection failed: " . $e->getMessage();
}
?>
```

**mysql/init.sql:**

```sql
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (name, email) VALUES
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com'),
    ('Charlie', 'charlie@example.com');
```

**사용법:**

```bash
# 시작
docker compose up -d

# 로그 확인
docker compose logs -f web

# 브라우저 접속
# http://localhost:8080 - 웹 애플리케이션
# http://localhost:8081 - phpMyAdmin

# MySQL 직접 접속
docker compose exec database mysql -u lampuser -plamppassword lampdb

# 정리
docker compose down -v
```

---

### 12.5.2 예제 2: MEAN 스택 (MongoDB, Express, Angular, Node.js)

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  # MongoDB
  mongodb:
    image: mongo:7
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: adminpassword
      MONGO_INITDB_DATABASE: meanapp
    volumes:
      - mongo-data:/data/db
      - ./mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro
    networks:
      - mean-net
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 3
    restart: always

  # Express API
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: development
      PORT: 3000
      MONGODB_URI: mongodb://admin:adminpassword@mongodb:27017/meanapp?authSource=admin
    volumes:
      - ./backend/src:/app/src
      - backend-modules:/app/node_modules
    networks:
      - mean-net
    depends_on:
      mongodb:
        condition: service_healthy
    restart: unless-stopped
    command: npm run dev

  # Angular Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "4200:4200"
    environment:
      API_URL: http://localhost:3000
    volumes:
      - ./frontend/src:/app/src
      - frontend-modules:/app/node_modules
    networks:
      - mean-net
    depends_on:
      - api
    restart: unless-stopped
    command: npm start

  # Mongo Express (DB 관리 도구)
  mongo-express:
    image: mongo-express:latest
    ports:
      - "8081:8081"
    environment:
      ME_CONFIG_MONGODB_ADMINUSERNAME: admin
      ME_CONFIG_MONGODB_ADMINPASSWORD: adminpassword
      ME_CONFIG_MONGODB_URL: mongodb://admin:adminpassword@mongodb:27017/
      ME_CONFIG_BASICAUTH_USERNAME: admin
      ME_CONFIG_BASICAUTH_PASSWORD: admin
    networks:
      - mean-net
    depends_on:
      - mongodb
    restart: unless-stopped

networks:
  mean-net:
    driver: bridge

volumes:
  mongo-data:
  backend-modules:
  frontend-modules:
```

**mongo-init.js:**

```javascript
// 애플리케이션 사용자 생성
db = db.getSiblingDB('meanapp');

db.createUser({
    user: 'appuser',
    pwd: 'apppassword',
    roles: [
        { role: 'readWrite', db: 'meanapp' }
    ]
});

// 초기 데이터
db.users.insertMany([
    { name: 'Alice', email: 'alice@example.com', role: 'admin' },
    { name: 'Bob', email: 'bob@example.com', role: 'user' }
]);

print('Database initialized successfully');
```

**사용법:**

```bash
# 시작
docker compose up -d

# 빌드부터 시작
docker compose up -d --build

# 로그 확인 (모든 서비스)
docker compose logs -f

# 특정 서비스만
docker compose logs -f api

# API 테스트
curl http://localhost:3000/api/users

# MongoDB 직접 접속
docker compose exec mongodb mongosh -u admin -p adminpassword meanapp

# 정리
docker compose down -v
```

---

### 12.5.3 예제 3: 마이크로서비스 개발 환경

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  # API Gateway
  gateway:
    build: ./gateway
    ports:
      - "80:3000"
    environment:
      USER_SERVICE_URL: http://user-service:4001
      PRODUCT_SERVICE_URL: http://product-service:4002
      ORDER_SERVICE_URL: http://order-service:4003
    networks:
      - frontend
      - backend
    depends_on:
      - user-service
      - product-service
      - order-service
    restart: unless-stopped

  # User Service
  user-service:
    build: ./services/user
    ports:
      - "4001:4001"
    environment:
      DATABASE_URL: postgresql://postgres:secret@postgres:5432/users
      REDIS_URL: redis://cache:6379
    volumes:
      - ./services/user/src:/app/src
    networks:
      - backend
    depends_on:
      - postgres
      - cache
    restart: unless-stopped

  # Product Service
  product-service:
    build: ./services/product
    ports:
      - "4002:4002"
    environment:
      DATABASE_URL: postgresql://postgres:secret@postgres:5432/products
      REDIS_URL: redis://cache:6379
    volumes:
      - ./services/product/src:/app/src
    networks:
      - backend
    depends_on:
      - postgres
      - cache
    restart: unless-stopped

  # Order Service
  order-service:
    build: ./services/order
    ports:
      - "4003:4003"
    environment:
      MONGODB_URI: mongodb://mongo:27017/orders
      KAFKA_BROKERS: kafka:9092
    volumes:
      - ./services/order/src:/app/src
    networks:
      - backend
    depends_on:
      - mongo
      - kafka
    restart: unless-stopped

  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: always

  # MongoDB
  mongo:
    image: mongo:7
    volumes:
      - mongo-data:/data/db
    networks:
      - backend
    restart: always

  # Redis
  cache:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis-data:/data
    networks:
      - backend
    restart: always

  # Kafka
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    networks:
      - backend
    restart: always

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    networks:
      - backend
    restart: always

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true

volumes:
  postgres-data:
  mongo-data:
  redis-data:
```

**명령어 예시:**

```bash
# 전체 스택 시작
docker compose up -d

# 서비스별로 로그 확인
docker compose logs -f gateway
docker compose logs -f user-service
docker compose logs -f product-service
docker compose logs -f order-service

# 특정 서비스만 재시작
docker compose restart user-service

# 서비스 스케일 조정
docker compose up -d --scale user-service=3

# 상태 확인
docker compose ps

# 리소스 사용량
docker compose top

# 정리
docker compose down
```

---

## 12.6 환경 변수 및 .env 파일

### 12.6.1 .env 파일 사용

**.env:**

```env
# 데이터베이스 설정
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secretpassword
POSTGRES_DB=myapp

# Redis 설정
REDIS_PASSWORD=redispassword

# 애플리케이션 설정
NODE_ENV=development
API_PORT=3000
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  api:
    image: myapi
    ports:
      - "${API_PORT}:3000"
    environment:
      NODE_ENV: ${NODE_ENV}
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@database:5432/${POSTGRES_DB}

  database:
    image: postgres:15
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
```

---

### 12.6.2 여러 환경 파일

```bash
# 개발 환경
docker compose --env-file .env.development up -d

# 프로덕션 환경
docker compose --env-file .env.production up -d

# 테스트 환경
docker compose --env-file .env.test up -d
```

**.env.development:**

```env
NODE_ENV=development
API_PORT=3000
DEBUG=true
```

**.env.production:**

```env
NODE_ENV=production
API_PORT=80
DEBUG=false
```

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 오케스트라 지휘자
```
[Docker CLI] = 악기 연주자들 개별 지시
지휘자가 각 연주자에게 일일이 신호를 보냄:
"바이올린 시작!" "첼로 중지!" "피아노 다시!"
→ 지휘자가 엄청나게 바쁨 ❌

[Docker Compose] = 악보(악보에 모든 것 기록)
┌────────────────────────────────┐
│ 교향곡 악보 (docker-compose.yml) │
├────────────────────────────────┤
│ 바이올린: 1분에 시작, 피아니시모  │
│ 첼로: 2분에 시작, 포르테          │
│ 피아노: 바이올린 후 시작          │
│ 타이밍: 모두 자동 조율           │
└────────────────────────────────┘

지휘: docker compose up
→ 모든 연주자가 악보대로 연주 ✅
```

### 비유 2: 아파트 건설 프로세스
```
[개별 docker run 명령어] = 건설 인부 직접 관리
"1층 콘크리트 부어!" → 대기 → "2층 철근 세워!"
→ 반복 → "배관 설치!" → "전기 공사!"
→ 매번 지시, 순서 기억 필요, 실수 多 ❌

[Docker Compose] = 건축 설계도
┌──────────────────────────────┐
│ 아파트 설계도면               │
├──────────────────────────────┤
│ 기초: 콘크리트 (db 컨테이너)  │
│ 골조: 철근 (api 컨테이너)     │
│ 배관: depends_on db          │
│ 전기: networks 연결          │
│ 마감: volumes 데이터 저장     │
└──────────────────────────────┘

실행: docker compose up
→ 설계도대로 자동 시공 ✅
```

### 비유 3: 한식당 주방 조리
```
[Docker CLI] = 요리사가 모든 것 수동 관리
1. 쌀 씻기: docker run rice-washer
2. 밥 짓기: docker run rice-cooker
3. 국 끓이기: docker run soup-pot
4. 반찬 만들기: docker run side-dish
5. 배치: docker network connect...
→ 주문마다 처음부터 반복 ❌

[Docker Compose] = 정식 정찬 레시피
┌─────────────────────────────┐
│ 한정식 코스 (compose.yml)    │
├─────────────────────────────┤
│ 밥: 쌀 3컵, 물 4컵           │
│ 국: 된장 2스푼, 두부 1모      │
│ 주菜: 불고기 300g            │
│ 부菜: 시금치나물, 콩나물     │
│ 타이밍: 국→밥→반찬 순서     │
└─────────────────────────────┘

실행: docker compose up
→ 한정식 전체 자동 조리 ✅
```

### 비유 4: 영화 촬영 준비
```
[Docker CLI] = 스태프 개별 연락
감독이 일일이 전화:
"조명팀 9시!" "음향팀 9:30!" "배우 10시!"
→ 전화 수십 통, 누락 위험 ❌

[Docker Compose] = 촬영 콘티
┌──────────────────────────────┐
│ 촬영 스케줄표                 │
├──────────────────────────────┤
│ Scene 1:                     │
│  - 조명: 자연광 모드          │
│  - 카메라: A, B 앵글         │
│  - 배우: 홍길동, 김철수       │
│  - 의존성: 조명→카메라→배우  │
│ 준비시간: 각 부서별 자동 대기 │
└──────────────────────────────┘

실행: docker compose up
→ 모든 스태프 자동 소집 ✅
```

### 비유 5: 게임 파티 구성
```
[Docker CLI] = 파티원 수동 초대
1. 전사 찾기: docker run warrior
2. 마법사 찾기: docker run mage
3. 힐러 찾기: docker run healer
4. 파티 묶기: docker network...
→ 매번 반복, 누가 누군지 헷갈림 ❌

[Docker Compose] = 파티 프리셋
┌───────────────────────────────┐
│ 레이드 파티 구성표             │
├───────────────────────────────┤
│ 탱커(database):               │
│  - HP: 10000 (메모리 1GB)     │
│  - 방어력: 높음 (재시작 정책)  │
│                               │
│ 딜러(api):                    │
│  - 공격력: 중간 (CPU 2코어)    │
│  - 의존: 탱커 필수             │
│                               │
│ 힐러(cache):                  │
│  - 치유: 빠름 (Redis 인메모리) │
│                               │
│ 파티 버프: 네트워크 연결      │
└───────────────────────────────┘

실행: docker compose up
→ 파티 자동 구성, 즉시 레이드 시작 ✅
```

### 🎯 종합 비교표
```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Docker       │ 오케스트라   │ 아파트 건설   │ 한식당 주방   │
│ Compose      │ 지휘         │ 설계         │ 조리         │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ services     │ 악기 파트    │ 건물 층      │ 요리 종류    │
│ depends_on   │ 연주 순서    │ 시공 순서    │ 조리 순서    │
│ networks     │ 하모니       │ 연결통로     │ 동선         │
│ volumes      │ 악보 보관    │ 자재 보관    │ 재료 보관    │
│ compose up   │ 지휘 시작    │ 착공         │ 조리 시작    │
│ compose down │ 연주 종료    │ 철거         │ 정리         │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

---

## 📊 수치로 보는 효과

### 개발 생산성 비교

| 지표 | Docker CLI | Docker Compose | 개선율 |
|------|------------|----------------|--------|
| 환경 구축 시간 | 30분 (명령어 15개) | 1분 (명령어 1개) | **96%↓** |
| 재시작 시간 | 5분 (수동 순서) | 10초 (자동 순서) | **96%↓** |
| 명령어 암기 | 20개 이상 | 5개 핵심만 | **75%↓** |
| 실수 발생률 | 30% (순서 오류) | 1% (YAML 오타) | **96%↓** |
| 팀원 온보딩 | 2시간 (설명 필요) | 5분 (파일 공유) | **95%↓** |

### 실제 프로젝트 적용 사례

#### 사례 1: 토스 - 마이크로서비스 개발환경
```yaml
# 사용 목적: 200개 마이크로서비스 로컬 개발
# 규모: 개발자 500명

# Before (Docker CLI)
- 환경 구축: 개발자당 4시간
- 문서: 50페이지 위키
- 문제: "내 컴퓨터에서는 안돼요" 빈발

# After (Docker Compose)
- 환경 구축: 5분 (docker compose up)
- 문서: docker-compose.yml 1개
- 문제: 거의 없음 (동일 환경)

# 성과
- 온보딩 시간: 4시간 → 5분 (98%↓)
- 개발자 생산성: 30%↑
- 인프라 비용: 연간 $100,000 절감
```

#### 사례 2: 우아한형제들(배달의민족) - 테스트 자동화
```yaml
# 사용 목적: CI/CD 파이프라인 테스트 환경
# 규모: 일일 빌드 300회

# Before
- 테스트 환경 준비: 빌드당 10분
- 정리: 수동, 5분
- 총 시간: 15분 × 300회 = 75시간/일

# After
- 준비+정리: docker compose up -d && test && compose down
- 총 시간: 2분 × 300회 = 10시간/일

# 성과
- 시간 절감: 65시간/일 (86%↓)
- 리소스 효율: 메모리 사용량 40%↓
- 테스트 안정성: 실패율 15% → 2% (86%↓)
```

#### 사례 3: 당근마켓 - 스테이징 환경
```yaml
# 사용 목적: 프로덕션 유사 환경 구축
# 규모: 15개 서비스 스택

# Before
- 수동 배포 스크립트: 200줄
- 환경별 설정: 파일 20개
- 배포 시간: 30분
- 롤백: 거의 불가능

# After
- docker-compose.yml: 1개 파일
- 환경별 오버라이드: .env 파일
- 배포 시간: 3분
- 롤백: docker compose down && git checkout && compose up

# 성과
- 배포 속도: 30분 → 3분 (90%↓)
- 설정 오류: 월 10건 → 0건
- 개발자 만족도: 95%↑
```

### 비용 절감 효과

| 항목 | Before (CLI) | After (Compose) | 절감액 |
|------|--------------|-----------------|--------|
| 개발자 시간 (시급 $50) | $200/주 | $20/주 | **$180/주** |
| 서버 리소스 낭비 | $300/월 | $100/월 | **$200/월** |
| 장애 대응 시간 | $1,000/월 | $200/월 | **$800/월** |
| 교육 비용 | $500/신입 | $50/신입 | **$450/신입** |
| **연간 총 절감 (10명 팀)** | - | - | **약 $15,000** |

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: 컨테이너 시작 순서 실수

**상황**: API 서버가 데이터베이스보다 먼저 시작되어 계속 실패하는 상황

```bash
# ❌ 주니어 개발자의 접근
# 1. DB 먼저 시작
docker run -d --name db postgres

# 2. API 시작 (너무 빨리 실행)
docker run -d --name api my-api
# Error: could not connect to database

# 3. 당황해서 API 재시작
docker restart api
# 또 실패...

# 4. 매번 수동으로 대기 시간 조절
docker run -d --name db postgres
sleep 30  # 얼마나 기다려야 할까?
docker run -d --name api my-api
```

**문제점**:
- 문제 1: 데이터베이스 준비 시간을 알 수 없음
- 문제 2: 매번 수동으로 순서 관리 필요
- 문제 3: 팀원마다 다른 대기 시간 사용
- 왜 이 문제가 발생하는가: 컨테이너 간 의존성을 명시하지 않음

**해결책**:
```yaml
# ✅ Docker Compose로 해결
version: '3.8'

services:
  database:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5
    environment:
      POSTGRES_PASSWORD: secret

  api:
    image: my-api
    depends_on:
      database:
        condition: service_healthy  # DB가 healthy 상태일 때만 시작
    environment:
      DATABASE_URL: postgresql://postgres:secret@database:5432/mydb
```

**실행**:
```bash
docker compose up -d
# [+] Running 2/2
#  ✔ Container project-database-1  Healthy    5.2s
#  ✔ Container project-api-1       Started    5.5s
```

**배운 점**:
- 💡 팁 1: `depends_on`으로 시작 순서 보장
- 💡 팁 2: `healthcheck`로 실제 준비 상태 확인
- 💡 팁 3: `service_healthy` 조건으로 확실한 동기화
- 💡 팁 4: 서비스 이름이 자동으로 DNS 이름이 됨 (database → hostname)

---

### 시나리오 2: 환경 변수 관리 혼란

**상황**: 개발/스테이징/프로덕션 환경마다 다른 설정 관리

```bash
# ❌ 주니어 개발자의 코드
# 개발 환경
docker run -d \
  -e NODE_ENV=development \
  -e DB_HOST=localhost \
  -e DB_PORT=5432 \
  -e DB_USER=dev \
  -e DB_PASSWORD=devpass \
  -e REDIS_HOST=localhost \
  -e REDIS_PORT=6379 \
  -e API_KEY=dev-key-123 \
  -e SECRET=dev-secret \
  my-app

# 스테이징 환경 (어떤 값을 바꿔야 하지??)
docker run -d \
  -e NODE_ENV=staging \
  -e DB_HOST=staging-db \
  -e DB_PORT=5432 \
  -e DB_USER=staging \
  -e DB_PASSWORD=???  # 어디에 적어뒀지?
  -e REDIS_HOST=??? \
  # ... 계속 헷갈림
  my-app
```

**문제점**:
- 문제 1: 환경마다 명령어 다시 작성
- 문제 2: 비밀번호 평문 노출 위험
- 문제 3: 어떤 환경 변수를 설정했는지 추적 어려움
- 문제 4: 팀원과 공유 불가능

**해결책**:
```yaml
# ✅ docker-compose.yml
version: '3.8'

services:
  app:
    image: my-app
    env_file:
      - .env  # 공통 설정
      - .env.${ENVIRONMENT}  # 환경별 설정
    environment:
      NODE_ENV: ${ENVIRONMENT}
```

**.env (공통 설정)**:
```env
# 모든 환경에서 동일
APP_NAME=MyApp
LOG_LEVEL=info
```

**.env.development**:
```env
ENVIRONMENT=development
DB_HOST=localhost
DB_USER=dev
DB_PASSWORD=devpass
API_KEY=dev-key-123
DEBUG=true
```

**.env.staging**:
```env
ENVIRONMENT=staging
DB_HOST=staging-db.example.com
DB_USER=staging
DB_PASSWORD=staging-pass-456
API_KEY=staging-key-456
DEBUG=false
```

**.env.production**:
```env
ENVIRONMENT=production
DB_HOST=prod-db.example.com
DB_USER=prod
DB_PASSWORD=${PROD_DB_PASSWORD}  # 외부 환경 변수에서 주입
API_KEY=${PROD_API_KEY}
DEBUG=false
```

**실행**:
```bash
# 개발 환경
ENVIRONMENT=development docker compose up -d

# 스테이징 환경
ENVIRONMENT=staging docker compose up -d

# 프로덕션 환경 (민감 정보는 외부 주입)
export PROD_DB_PASSWORD="super-secret"
export PROD_API_KEY="prod-key-789"
ENVIRONMENT=production docker compose up -d
```

**배운 점**:
- 💡 팁 1: `.env` 파일로 환경 변수 관리 (Git에는 `.env.example`만 커밋)
- 💡 팁 2: 환경별 파일 분리로 명확한 구분
- 💡 팁 3: 민감 정보는 환경 변수로 외부 주입
- 💡 팁 4: `.env`를 `.gitignore`에 추가 필수!

---

### 시나리오 3: 볼륨 데이터 날아감

**상황**: 컨테이너 재시작 후 데이터베이스 데이터가 모두 사라짐

```bash
# ❌ 주니어 개발자의 실수
# 볼륨 없이 실행
docker run -d --name db postgres

# 데이터 입력
docker exec db psql -U postgres -c "CREATE TABLE users ..."
docker exec db psql -U postgres -c "INSERT INTO users ..."

# 컨테이너 재시작
docker stop db
docker rm db
docker run -d --name db postgres

# 데이터 확인
docker exec db psql -U postgres -c "SELECT * FROM users;"
# ERROR: relation "users" does not exist
# 😱 모든 데이터가 사라짐!
```

**문제점**:
- 문제 1: 볼륨 마운트를 깜빡함
- 문제 2: 컨테이너 삭제 시 데이터도 함께 삭제됨
- 문제 3: 백업 없이 개발 진행
- 왜 이 문제가 발생하는가: 컨테이너는 기본적으로 임시(ephemeral) 저장소 사용

**해결책**:
```yaml
# ✅ Docker Compose로 영구 저장
version: '3.8'

services:
  database:
    image: postgres:15
    volumes:
      # 명명된 볼륨 (Docker가 관리)
      - postgres-data:/var/lib/postgresql/data

      # 초기화 스크립트 (읽기 전용)
      - ./init-db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    environment:
      POSTGRES_PASSWORD: secret
    restart: unless-stopped  # 자동 재시작

volumes:
  postgres-data:  # 영구 볼륨 정의
    driver: local
    labels:
      backup: daily  # 백업 표시
```

**init-db.sql**:
```sql
-- 초기 데이터베이스 스키마
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 초기 데이터
INSERT INTO users (name, email) VALUES
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com')
ON CONFLICT DO NOTHING;
```

**실행 및 확인**:
```bash
# 시작
docker compose up -d

# 데이터 확인
docker compose exec database psql -U postgres -c "SELECT * FROM users;"
#  id | name  |       email
# ----+-------+-------------------
#   1 | Alice | alice@example.com
#   2 | Bob   | bob@example.com

# 컨테이너 완전 제거 (볼륨 유지)
docker compose down

# 다시 시작
docker compose up -d

# 데이터 여전히 존재!
docker compose exec database psql -U postgres -c "SELECT * FROM users;"
#  id | name  |       email
# ----+-------+-------------------
#   1 | Alice | alice@example.com
#   2 | Bob   | bob@example.com
# ✅ 데이터 보존됨!

# 볼륨까지 제거하려면 (주의!)
docker compose down -v  # -v 플래그로 볼륨도 삭제
```

**배운 점**:
- 💡 팁 1: 영구 저장이 필요한 데이터는 반드시 볼륨 사용
- 💡 팁 2: `docker compose down`은 볼륨을 삭제하지 않음 (안전)
- 💡 팁 3: `docker compose down -v`는 볼륨까지 삭제 (주의!)
- 💡 팁 4: 초기화 스크립트로 개발 데이터 자동 세팅

---

### 시나리오 4: 포트 충돌 지옥

**상황**: 여러 프로젝트를 동시에 실행하려니 포트가 겹침

```bash
# ❌ 주니어 개발자의 문제

# 프로젝트 A (쇼핑몰)
docker run -d -p 3000:3000 --name shop-api shop-api
docker run -d -p 5432:5432 --name shop-db postgres
docker run -d -p 6379:6379 --name shop-redis redis

# 프로젝트 B (블로그) 실행 시도
docker run -d -p 3000:3000 --name blog-api blog-api
# Error: port is already allocated
# 😱 포트 3000이 이미 사용 중!

docker run -d -p 5432:5432 --name blog-db postgres
# Error: port is already allocated
# 😱 PostgreSQL 포트도 겹침!

# 매번 포트 번호 외워서 변경해야 함
docker run -d -p 3001:3000 --name blog-api blog-api
docker run -d -p 5433:5432 --name blog-db postgres
# 어느 프로젝트가 어느 포트인지 헷갈림...
```

**문제점**:
- 문제 1: 프로젝트마다 포트 번호 충돌
- 문제 2: 어떤 포트를 어떤 프로젝트가 쓰는지 추적 어려움
- 문제 3: 팀원마다 다른 포트 사용으로 설정 불일치
- 문제 4: 컨테이너 이름 충돌도 발생

**해결책**:
```yaml
# ✅ 프로젝트별 docker-compose.yml로 격리

# 프로젝트 A: shop/docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "3000:3000"  # 외부 3000
    networks:
      - shop-network

  database:
    image: postgres:15
    ports:
      - "5432:5432"  # 외부 5432
    networks:
      - shop-network

networks:
  shop-network:
    name: shop-network  # 명시적 이름

# 프로젝트 B: blog/docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "3001:3000"  # 외부 3001 (내부는 여전히 3000)
    networks:
      - blog-network

  database:
    image: postgres:15
    ports:
      - "5433:5432"  # 외부 5433 (내부는 여전히 5432)
    networks:
      - blog-network

networks:
  blog-network:
    name: blog-network  # 다른 네트워크
```

**실행**:
```bash
# 프로젝트 A 실행
cd shop
docker compose up -d
# ✔ shop-api-1     Started (포트 3000)
# ✔ shop-database-1 Started (포트 5432)

# 프로젝트 B 실행 (동시에!)
cd ../blog
docker compose up -d
# ✔ blog-api-1     Started (포트 3001)
# ✔ blog-database-1 Started (포트 5433)

# 두 프로젝트 모두 정상 실행!
curl http://localhost:3000  # Shop API
curl http://localhost:3001  # Blog API

# 프로젝트별 관리
cd shop && docker compose logs -f api
cd blog && docker compose logs -f api

# 프로젝트별 정리
cd shop && docker compose down
cd blog && docker compose down
```

**더 나은 방법: 프로젝트 이름 활용**:
```bash
# 프로젝트 이름으로 자동 격리
cd shop
docker compose -p shop up -d

cd ../blog
docker compose -p blog up -d

# 컨테이너 이름 자동 구분
# shop-api-1, shop-database-1
# blog-api-1, blog-database-1

# 네트워크도 자동 구분
# shop_default
# blog_default
```

**배운 점**:
- 💡 팁 1: 프로젝트마다 docker-compose.yml 별도 관리
- 💡 팁 2: 프로젝트 이름(-p)으로 리소스 자동 격리
- 💡 팁 3: 외부 포트만 다르게, 내부 포트는 동일하게 유지
- 💡 팁 4: 네트워크 이름을 명시하면 더 명확한 관리 가능

---

## ❓ FAQ

<details>
<summary><strong>Q1: docker-compose와 docker compose의 차이는?</strong></summary>

**A**: 하이픈 유무는 버전 차이입니다.

**상세 설명**:
- `docker-compose` (V1): Python으로 작성된 독립 실행 파일 (레거시)
- `docker compose` (V2): Go로 작성된 Docker CLI 플러그인 (최신)

**기능 차이**:
```bash
# V1 (구버전)
docker-compose up
- 별도 설치 필요
- 느린 속도
- 일부 최신 기능 미지원

# V2 (신버전)
docker compose up
- Docker Desktop에 포함
- 2-3배 빠른 성능
- 새로운 Compose 명세 지원
- BuildKit 통합
```

**확인 방법**:
```bash
# V1 확인
docker-compose --version
# docker-compose version 1.29.2

# V2 확인
docker compose version
# Docker Compose version v2.23.0
```

**실무 팁**:
💡 2023년부터는 V2 사용을 강력 권장합니다. V1은 2023년 7월부터 업데이트 중단되었습니다.

</details>

<details>
<summary><strong>Q2: docker-compose.yml 파일 위치는 어디가 좋나요?</strong></summary>

**A**: 프로젝트 루트 디렉토리가 표준입니다.

**상세 설명**:
```
권장 구조:
my-project/
├── docker-compose.yml          # 메인 개발 환경
├── docker-compose.prod.yml     # 프로덕션 오버라이드
├── docker-compose.test.yml     # 테스트 환경
├── .env                        # 환경 변수 (Git 제외)
├── .env.example                # 환경 변수 템플릿 (Git 포함)
├── src/                        # 소스 코드
├── Dockerfile                  # 애플리케이션 이미지
└── README.md
```

**사용 예시**:
```bash
# 기본 실행 (docker-compose.yml 자동 인식)
docker compose up

# 특정 파일 지정
docker compose -f docker-compose.prod.yml up

# 여러 파일 조합 (나중 파일이 오버라이드)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```

**실무 팁**:
💡 `.env` 파일은 반드시 `.gitignore`에 추가하고, `.env.example`을 Git에 커밋하세요.

</details>

<details>
<summary><strong>Q3: 컨테이너가 시작 순서를 무시하는 이유는?</strong></summary>

**A**: `depends_on`은 시작 순서만 보장하고, 준비 완료는 보장하지 않습니다.

**문제 상황**:
```yaml
services:
  api:
    image: my-api
    depends_on:
      - database  # DB가 "시작"되면 API 시작

  database:
    image: postgres
    # 시작 != 준비 완료
```

```bash
# 실행
docker compose up
# database 컨테이너 시작 (1초)
# api 컨테이너 시작 (2초)
# api 에러: could not connect to database
# (PostgreSQL은 시작 후 5초 더 초기화 필요)
```

**해결책 1: healthcheck 사용 (권장)**:
```yaml
services:
  database:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 10s

  api:
    image: my-api
    depends_on:
      database:
        condition: service_healthy  # healthy 상태 대기
```

**해결책 2: 재시도 로직 구현**:
```javascript
// Node.js 예시
async function connectWithRetry(maxRetries = 10, delay = 2000) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      await db.connect();
      console.log('Database connected!');
      return;
    } catch (err) {
      console.log(`Retry ${i+1}/${maxRetries} in ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  throw new Error('Failed to connect to database');
}
```

**실무 팁**:
💡 프로덕션 환경에서는 애플리케이션에 재시도 로직을 구현하는 것이 더 안정적입니다.

</details>

<details>
<summary><strong>Q4: 볼륨을 삭제하지 않고 컨테이너만 삭제하려면?</strong></summary>

**A**: `docker compose down` (기본)은 볼륨을 유지하고, `-v` 옵션을 추가해야 볼륨이 삭제됩니다.

**명령어 비교**:
```bash
# 1. 컨테이너와 네트워크만 삭제 (볼륨 유지)
docker compose down
# ✔ Container removed
# ✔ Network removed
# ✔ Volume preserved (안전!)

# 2. 볼륨까지 모두 삭제 (주의!)
docker compose down -v
# ✔ Container removed
# ✔ Network removed
# ✔ Volume removed (데이터 삭제!)

# 3. 이미지까지 삭제
docker compose down --rmi all
# ✔ Container removed
# ✔ Network removed
# ✔ Images removed

# 4. 모든 것 삭제 (완전 초기화)
docker compose down -v --rmi all --remove-orphans
```

**볼륨 확인**:
```bash
# 볼륨 목록
docker volume ls
# DRIVER    VOLUME NAME
# local     myapp_postgres-data
# local     myapp_redis-data

# 특정 볼륨 상세 정보
docker volume inspect myapp_postgres-data

# 사용하지 않는 볼륨만 정리
docker volume prune
```

**실무 팁**:
💡 개발 중에는 `down`만 사용하고, 완전 초기화가 필요할 때만 `down -v`를 사용하세요.

</details>

<details>
<summary><strong>Q5: 특정 서비스만 재시작하려면?</strong></summary>

**A**: 서비스 이름을 지정하면 됩니다.

**명령어 예시**:
```bash
# 1. 특정 서비스만 재시작
docker compose restart api
# [+] Restarting 1/1
#  ✔ Container myapp-api-1  Restarted

# 2. 여러 서비스 동시 재시작
docker compose restart api cache
# [+] Restarting 2/2
#  ✔ Container myapp-api-1    Restarted
#  ✔ Container myapp-cache-1  Restarted

# 3. 설정 변경 후 재생성 (rebuild)
docker compose up -d --build api
# 이미지 다시 빌드 → 컨테이너 재생성

# 4. 강제 재생성 (이미지는 동일)
docker compose up -d --force-recreate api

# 5. 서비스 중지 → 시작 (재시작 아님)
docker compose stop api
docker compose start api
```

**차이점**:
```
restart:
- 컨테이너 중지 → 시작
- 설정 변경 반영 안 됨
- 빠름 (1-2초)

up -d --force-recreate:
- 컨테이너 삭제 → 재생성
- 설정 변경 반영됨
- 느림 (5-10초)

up -d --build:
- 이미지 다시 빌드 → 컨테이너 재생성
- 코드 변경 반영됨
- 매우 느림 (1-5분)
```

**실무 팁**:
💡 코드 변경: `up -d --build api`, 설정 변경: `up -d --force-recreate api`, 단순 재시작: `restart api`

</details>

<details>
<summary><strong>Q6: 프로덕션에서 Docker Compose를 사용해도 되나요?</strong></summary>

**A**: 단일 서버 환경에서는 가능하지만, 다중 서버 환경에서는 권장하지 않습니다.

**사용 가능한 경우**:
```
✅ 소규모 프로덕션 (단일 서버)
- 스타트업 MVP
- 내부 도구
- 스테이징 환경
- 트래픽 < 10,000 req/day

예시:
docker compose -f docker-compose.prod.yml up -d
```

**권장하지 않는 경우**:
```
❌ 대규모 프로덕션 (다중 서버)
- 고가용성 필요
- 자동 스케일링
- 로드 밸런싱
- 트래픽 > 100,000 req/day

대안:
- Kubernetes
- Docker Swarm
- AWS ECS
- Google Cloud Run
```

**프로덕션 사용 시 주의사항**:
```yaml
version: '3.8'

services:
  app:
    image: my-app:1.2.3  # ❌ latest 금지, ✅ 명시적 버전
    restart: always      # ✅ 자동 재시작
    deploy:
      resources:
        limits:
          cpus: '2'      # ✅ 리소스 제한
          memory: 1G
    logging:             # ✅ 로그 관리
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    healthcheck:         # ✅ 헬스체크
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**실무 팁**:
💡 스타트업 초기에는 Compose로 시작하고, 트래픽 증가 시 Kubernetes로 마이그레이션하는 것이 일반적입니다.

</details>

<details>
<summary><strong>Q7: docker-compose.yml 버전 번호는 무엇인가요?</strong></summary>

**A**: Compose 파일 형식의 버전이며, 현재는 3.8 또는 생략을 권장합니다.

**버전 역사**:
```yaml
# Version 1 (구버전, 사용 금지)
web:
  build: .
  ports:
    - "5000:5000"

# Version 2 (2016년)
version: '2'
services:
  web:
    build: .

# Version 3 (2017년, Docker Swarm 지원)
version: '3'
services:
  web:
    build: .
    deploy:  # Swarm 전용 기능
      replicas: 3

# Version 3.8 (2019년, 최신)
version: '3.8'
services:
  web:
    build: .
```

**최신 권장사항 (2024년)**:
```yaml
# 방법 1: 버전 생략 (Compose V2)
services:
  web:
    build: .

# 방법 2: 3.8 명시
version: '3.8'
services:
  web:
    build: .
```

**버전별 주요 기능**:

| 버전 | 주요 기능 | 권장 여부 |
|------|-----------|-----------|
| 1 | 기본 기능만 | ❌ 사용 금지 |
| 2.x | depends_on, healthcheck | ⚠️ 레거시 |
| 3.0-3.7 | Swarm 지원 | ⚠️ 레거시 |
| 3.8 | 모든 기능 | ✅ 권장 |
| 생략 | 최신 명세 자동 적용 | ✅ 권장 (V2) |

**실무 팁**:
💡 Docker Compose V2를 사용한다면 버전 번호를 생략해도 됩니다. 명시하려면 `3.8`을 사용하세요.

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. Docker Compose가 무엇이고, Docker CLI와 어떻게 다른가요?</strong></summary>

**모범 답안 포인트**
- Docker Compose는 여러 컨테이너를 YAML 파일로 정의하고 관리하는 도구
- Docker CLI는 개별 컨테이너를 명령어로 관리
- Compose는 선언적 방식, CLI는 명령형 방식
- 팀 협업과 재현 가능한 환경 구축에 유리

**예시 답변**
> "Docker Compose는 여러 개의 Docker 컨테이너를 하나의 YAML 파일로 정의하고 관리하는 도구입니다. 예를 들어, 웹 애플리케이션에 API 서버, 데이터베이스, 캐시가 필요할 때, Docker CLI로는 각각 `docker run` 명령어를 3번 실행해야 하지만, Compose는 `docker-compose.yml` 파일 하나에 모든 설정을 작성하고 `docker compose up` 한 번으로 전체를 실행할 수 있습니다. 이는 팀원 간 동일한 환경을 쉽게 공유할 수 있고, Git으로 인프라 설정을 버전 관리할 수 있다는 장점이 있습니다."

**꼬리 질문**
- Q: Compose 파일을 Git에 커밋해도 되나요?
- A: 네, `docker-compose.yml`은 커밋하되, 민감 정보가 담긴 `.env` 파일은 `.gitignore`에 추가하고 `.env.example`만 커밋합니다.

**실무 연관**
- 신입 개발자 온보딩 시 `docker compose up` 한 번으로 개발 환경 즉시 구축
- "내 컴퓨터에서는 되는데요" 문제 해결

</details>

<details>
<summary><strong>2. docker-compose.yml 파일의 기본 구조를 설명해주세요.</strong></summary>

**모범 답안 포인트**
- version: Compose 파일 버전 (3.8 권장 또는 생략)
- services: 실행할 컨테이너들 정의
- networks: 네트워크 설정 (선택)
- volumes: 볼륨 정의 (선택)

**예시 답변**
> "docker-compose.yml의 기본 구조는 크게 4부분으로 나뉩니다. 첫째, `version`은 Compose 파일 형식의 버전을 지정하며 보통 '3.8'을 사용합니다. 둘째, `services`는 가장 중요한 부분으로 실행할 컨테이너들을 정의합니다. 예를 들어 'web', 'database' 같은 서비스 이름 아래에 이미지, 포트, 환경변수 등을 설정합니다. 셋째, `networks`는 서비스 간 통신을 위한 네트워크를 정의하고, 넷째, `volumes`는 데이터를 영구 저장하기 위한 볼륨을 정의합니다. networks와 volumes는 필요할 때만 선택적으로 사용합니다."

**꼬리 질문**
- Q: services에는 어떤 설정을 주로 작성하나요?
- A: image(이미지 이름), ports(포트 매핑), environment(환경 변수), volumes(볼륨 마운트), depends_on(의존성) 등을 주로 작성합니다.

**실무 연관**
- 신규 프로젝트 시작 시 기본 템플릿으로 활용
- 프로젝트 구조 파악을 위한 첫 번째 참고 문서

</details>

<details>
<summary><strong>3. depends_on의 역할과 한계점은 무엇인가요?</strong></summary>

**모범 답안 포인트**
- 역할: 컨테이너 시작 순서 제어
- 한계: 시작만 보장, 준비 완료는 보장 안 함
- 해결책: healthcheck 조합 사용

**예시 답변**
> "`depends_on`은 컨테이너의 시작 순서를 제어하는 옵션입니다. 예를 들어 API 서버가 데이터베이스에 의존한다면, `depends_on: [database]`로 지정하면 데이터베이스 컨테이너가 먼저 시작됩니다. 하지만 중요한 한계가 있습니다. 데이터베이스 컨테이너가 '시작'은 했지만 실제 연결을 받을 '준비'가 안 된 상태일 수 있습니다. PostgreSQL은 시작 후 초기화에 5-10초가 더 필요한데, 이 시간 동안 API가 연결을 시도하면 실패합니다. 이를 해결하려면 `healthcheck`를 정의하고 `condition: service_healthy`를 사용해야 합니다."

**꼬리 질문**
- Q: healthcheck 없이 해결할 수 있나요?
- A: 애플리케이션 코드에 재시도 로직을 구현하는 방법도 있습니다. 실무에서는 두 방법을 모두 사용하는 것이 안전합니다.

**실무 연관**
- 마이크로서비스 아키텍처에서 서비스 간 의존성 관리
- 초기 개발자가 자주 겪는 "API가 DB 연결 실패" 문제 해결

</details>

<details>
<summary><strong>4. volumes와 bind mount의 차이는?</strong></summary>

**모범 답안 포인트**
- Named volume: Docker가 관리, 위치 자동, 프로덕션 권장
- Bind mount: 호스트 경로 직접 지정, 개발 환경 편리
- 사용 사례 구분

**예시 답변**
> "volumes는 두 가지 방식이 있습니다. 첫째, named volume(명명된 볼륨)은 `volumes` 섹션에 정의하고 Docker가 저장 위치를 자동으로 관리합니다. 예를 들어 `postgres-data:/var/lib/postgresql/data`처럼 사용하며, 실제 데이터는 Docker가 관리하는 디렉토리에 저장됩니다. 프로덕션 환경에서 권장됩니다. 둘째, bind mount는 `./src:/app/src`처럼 호스트의 특정 경로를 직접 지정합니다. 개발 환경에서 코드를 수정하면 즉시 컨테이너에 반영되어 편리합니다. 정리하면, 데이터베이스 데이터처럼 영구 보존이 필요하면 named volume, 소스 코드처럼 실시간 동기화가 필요하면 bind mount를 사용합니다."

**꼬리 질문**
- Q: 볼륨 데이터를 백업하려면?
- A: `docker run --rm -v myvolume:/data -v $(pwd):/backup ubuntu tar czf /backup/backup.tar.gz /data` 같은 명령어로 백업 가능합니다.

**실무 연관**
- 개발 환경: 코드 수정 시 자동 반영 (bind mount)
- 프로덕션: 데이터베이스 데이터 안전하게 보존 (named volume)

</details>

<details>
<summary><strong>5. docker compose up -d와 docker compose start의 차이는?</strong></summary>

**모범 답안 포인트**
- up: 전체 생애주기 (생성 + 시작)
- start: 기존 컨테이너만 시작
- 사용 시나리오 구분

**예시 답변**
> "`docker compose up`은 전체 생애주기를 관리합니다. 네트워크와 볼륨을 생성하고, 이미지가 없으면 빌드하고, 컨테이너를 새로 생성한 뒤 시작합니다. 반면 `docker compose start`는 이미 생성된 컨테이너를 단순히 시작만 합니다. 비유하자면, `up`은 아파트를 새로 짓고 입주하는 것이고, `start`는 이미 있는 아파트에 불을 켜는 것입니다. 일반적인 시나리오는 이렇습니다: 처음 실행할 때나 설정 변경 시에는 `docker compose up -d`, 단순히 중지된 컨테이너를 다시 시작할 때는 `docker compose start`를 사용합니다."

**꼬리 질문**
- Q: down과 stop의 차이는?
- A: `stop`은 컨테이너만 중지하고, `down`은 컨테이너를 삭제하고 네트워크도 제거합니다. 볼륨은 `-v` 옵션을 추가해야 삭제됩니다.

**실무 연관**
- 아침 출근: `docker compose start` (빠른 재시작)
- 설정 변경 후: `docker compose up -d --force-recreate` (재생성)

</details>

<details>
<summary><strong>6. 환경 변수를 관리하는 방법은?</strong></summary>

**모범 답안 포인트**
- .env 파일 사용
- environment 키워드
- 민감 정보 처리 방법

**예시 답변**
> "Docker Compose에서 환경 변수는 세 가지 방법으로 관리합니다. 첫째, `.env` 파일에 `DB_PASSWORD=secret` 형태로 작성하고 `env_file: [.env]`로 로드합니다. 둘째, `environment` 키워드로 직접 지정합니다. 셋째, 호스트 환경 변수를 `${VARIABLE}` 형식으로 참조합니다. 실무에서는 개발/스테이징/프로덕션 환경별로 `.env.development`, `.env.production` 파일을 분리하고, 민감한 정보(비밀번호, API 키)는 `.env` 파일에 작성한 뒤 `.gitignore`에 추가합니다. Git에는 `.env.example` 파일만 커밋하여 필요한 변수 목록을 공유합니다."

**꼬리 질문**
- Q: 프로덕션에서 비밀번호를 어떻게 관리하나요?
- A: Docker Secrets, AWS Secrets Manager, Vault 등 전용 비밀 관리 도구를 사용하거나, CI/CD 환경 변수로 주입합니다.

**실무 연관**
- 로컬 개발: `.env.development` 사용
- 배포: CI/CD 파이프라인에서 환경 변수 주입

</details>

<details>
<summary><strong>7. 여러 프로젝트를 동시에 실행할 때 포트 충돌을 어떻게 해결하나요?</strong></summary>

**모범 답안 포인트**
- 프로젝트별 포트 번호 다르게 설정
- 프로젝트 이름(-p) 활용
- 네트워크 격리

**예시 답변**
> "여러 프로젝트를 동시에 실행할 때는 세 가지 방법으로 포트 충돌을 방지합니다. 첫째, 각 프로젝트의 docker-compose.yml에서 외부 포트를 다르게 설정합니다. 예를 들어 프로젝트 A는 `3000:3000`, 프로젝트 B는 `3001:3000`으로 설정합니다. 내부 포트(컨테이너 내부)는 동일하게 유지하고, 외부 포트(호스트)만 다르게 하는 것입니다. 둘째, `docker compose -p projectA up`처럼 프로젝트 이름을 명시하면 컨테이너 이름과 네트워크가 자동으로 격리됩니다. 셋째, 각 프로젝트마다 별도 네트워크를 사용하여 완전히 독립된 환경을 만듭니다. 실무에서는 이 방법들을 조합하여 수십 개의 프로젝트를 동시에 실행합니다."

**꼬리 질문**
- Q: 포트 번호를 외우기 어려운데요?
- A: README.md에 "이 프로젝트는 3000번 포트 사용"이라고 명시하거나, `docker compose ps`로 확인합니다.

**실무 연관**
- 마이크로서비스 개발 시 10개 이상 서비스 동시 실행
- 여러 클라이언트 프로젝트 동시 작업

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. Docker Compose의 네트워크 격리 방식과 서비스 디스커버리를 설명해주세요.</strong></summary>

**모범 답안 포인트**
- 기본 네트워크 자동 생성 (bridge 드라이버)
- 서비스 이름이 DNS 이름으로 자동 등록
- 네트워크 드라이버 종류 (bridge, host, overlay)
- 다중 네트워크 활용 (프론트엔드/백엔드 분리)

**예시 답변**
> "Docker Compose는 프로젝트마다 자동으로 격리된 bridge 네트워크를 생성합니다. 예를 들어 'myapp' 프로젝트는 'myapp_default' 네트워크가 생성되며, 같은 네트워크 내의 서비스들은 서비스 이름으로 서로를 찾을 수 있습니다. 이를 서비스 디스커버리라고 하는데, 내부 DNS를 사용하여 'api' 서비스에서 'database'로 연결할 때 `postgresql://database:5432` 형태로 접근합니다. 실무에서는 보안을 위해 다중 네트워크를 활용하는데, 예를 들어 'frontend' 네트워크는 외부 접근 가능, 'backend' 네트워크는 internal 옵션으로 외부 차단하여 데이터베이스를 보호합니다. 또한 overlay 네트워크를 사용하면 Docker Swarm에서 여러 호스트 간 통신도 가능합니다."

**실무 예시**:
```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # 외부 접근 차단

services:
  nginx:
    networks:
      - frontend
  api:
    networks:
      - frontend
      - backend
  database:
    networks:
      - backend  # 외부에서 접근 불가
```

**꼬리 질문**
- Q: external 네트워크는 언제 사용하나요?
- A: 여러 Compose 프로젝트가 하나의 네트워크를 공유해야 할 때 사용합니다. 예를 들어 공통 프록시 네트워크를 만들고 여러 애플리케이션이 연결하는 경우입니다.

**실무 연관**
- 마이크로서비스 간 통신 설계
- 데이터베이스 보안 강화 (내부 네트워크 격리)
- 멀티 프로젝트 환경에서 네트워크 공유

</details>

<details>
<summary><strong>2. Compose 파일의 오버라이드 메커니즘을 설명하고 활용 사례를 제시해주세요.</strong></summary>

**모범 답안 포인트**
- docker-compose.override.yml 자동 병합
- -f 옵션으로 여러 파일 조합
- 환경별 설정 분리 패턴
- 우선순위 규칙

**예시 답변**
> "Compose는 파일 오버라이드 메커니즘을 통해 환경별 설정을 효율적으로 관리합니다. 기본적으로 `docker-compose.yml`과 `docker-compose.override.yml`을 자동으로 병합하며, 후자가 전자를 덮어씁니다. 실무에서는 베이스 설정을 `docker-compose.yml`에 작성하고, 개발 환경 설정은 `docker-compose.dev.yml`, 프로덕션 설정은 `docker-compose.prod.yml`로 분리합니다. 예를 들어 베이스에는 공통 이미지와 볼륨을, 개발용에는 핫 리로드와 디버그 포트를, 프로덕션용에는 리소스 제한과 헬스체크를 추가합니다. 실행 시 `docker compose -f docker-compose.yml -f docker-compose.prod.yml up`처럼 명시적으로 지정하거나, CI/CD에서 환경 변수로 제어합니다."

**실무 예시**:
```yaml
# docker-compose.yml (베이스)
services:
  api:
    image: myapi:latest

# docker-compose.dev.yml (개발)
services:
  api:
    build: .  # 로컬 빌드
    volumes:
      - ./src:/app/src  # 핫 리로드
    environment:
      DEBUG: "true"

# docker-compose.prod.yml (프로덕션)
services:
  api:
    image: myapi:1.2.3  # 명시적 버전
    deploy:
      resources:
        limits:
          memory: 512M
    restart: always
```

**꼬리 질문**
- Q: 오버라이드 순서는 어떻게 되나요?
- A: 나중에 지정한 파일이 우선순위가 높습니다. `-f a.yml -f b.yml`이면 b.yml이 a.yml을 덮어씁니다.

**실무 연관**
- DRY 원칙 (Don't Repeat Yourself) 준수
- 환경별 설정 관리 (dev/staging/prod)
- CI/CD 파이프라인 통합

</details>

<details>
<summary><strong>3. 대규모 마이크로서비스 환경에서 Compose의 한계와 대안을 논의해주세요.</strong></summary>

**모범 답안 포인트**
- 단일 호스트 제약
- 자동 스케일링 부재
- 로드 밸런싱 제한
- Kubernetes/Swarm으로의 마이그레이션 경로

**예시 답변**
> "Docker Compose는 단일 호스트 환경에 최적화되어 있어 대규모 환경에서는 한계가 있습니다. 첫째, 여러 서버에 분산 배포가 불가능합니다. 둘째, 트래픽에 따른 자동 스케일링이 없습니다. `--scale api=3`으로 수동 스케일은 가능하지만 자동 조정은 안 됩니다. 셋째, 로드 밸런싱이 제한적입니다. 여러 인스턴스를 띄워도 라운드 로빈 방식만 지원하며 헬스 기반 라우팅은 불가능합니다. 넷째, 서비스 메시, 시크릿 관리, 롤링 업데이트 같은 고급 기능이 부족합니다. 실무에서는 트래픽이 일정 수준(보통 10,000 req/day)을 넘으면 Kubernetes로 마이그레이션하는데, Compose 파일은 kompose 도구로 Kubernetes 매니페스트로 변환 가능합니다. 중간 단계로 Docker Swarm을 사용하기도 하지만, 최근에는 Kubernetes가 표준입니다."

**마이그레이션 경로**:
```bash
# Compose → Kubernetes 변환
kompose convert -f docker-compose.yml
# → deployment.yaml, service.yaml 생성

# 또는 Helm 차트로
kompose convert -c -f docker-compose.yml
```

**한계 비교**:

| 기능 | Compose | Kubernetes |
|------|---------|------------|
| 다중 호스트 | ❌ | ✅ |
| 자동 스케일링 | ❌ | ✅ (HPA) |
| 로드 밸런싱 | 제한적 | ✅ (Ingress) |
| 롤링 업데이트 | ❌ | ✅ |
| 시크릿 관리 | 제한적 | ✅ |
| 헬스 모니터링 | 기본 | ✅ (Liveness/Readiness) |

**실무 연관**
- 스타트업 초기: Compose (빠른 개발)
- 성장기: Swarm (중간 단계)
- 대규모: Kubernetes (엔터프라이즈)

</details>

<details>
<summary><strong>4. 프로덕션 환경에서 Compose를 안전하게 사용하는 방법은?</strong></summary>

**모범 답안 포인트**
- 명시적 이미지 태그 (latest 금지)
- 리소스 제한 설정
- 로깅 관리
- 헬스체크 및 재시작 정책
- 비밀 정보 보안

**예시 답변**
> "프로덕션 환경에서 Compose를 사용할 때는 몇 가지 필수 설정이 있습니다. 첫째, 이미지 태그를 명시적으로 지정합니다. `image: myapp:latest` 대신 `image: myapp:1.2.3`처럼 버전을 고정하여 예상치 못한 업데이트를 방지합니다. 둘째, deploy.resources로 CPU와 메모리 제한을 설정하여 하나의 컨테이너가 전체 시스템 리소스를 고갈시키지 않도록 합니다. 셋째, logging 드라이버를 설정하여 로그가 무한정 쌓이지 않도록 로테이션합니다. 넷째, healthcheck로 서비스 상태를 모니터링하고 restart: always로 장애 시 자동 복구합니다. 다섯째, 비밀번호나 API 키는 환경 변수로 외부에서 주입하며, Docker Secrets를 사용하면 더욱 안전합니다. 마지막으로 읽기 전용 파일시스템(read_only: true)과 최소 권한 원칙을 적용합니다."

**프로덕션 체크리스트**:
```yaml
version: '3.8'

services:
  api:
    image: myapi:1.2.3  # ✅ 명시적 버전
    restart: always     # ✅ 자동 재시작

    deploy:
      resources:
        limits:
          cpus: '2'     # ✅ CPU 제한
          memory: 1G    # ✅ 메모리 제한
        reservations:
          cpus: '1'
          memory: 512M

    logging:            # ✅ 로그 로테이션
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

    healthcheck:        # ✅ 헬스체크
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

    environment:
      API_KEY: ${API_KEY}  # ✅ 환경 변수 주입

    read_only: true     # ✅ 읽기 전용 FS
    tmpfs:
      - /tmp

    security_opt:       # ✅ 보안 옵션
      - no-new-privileges:true
```

**실무 연관**
- 중소규모 프로덕션 서비스 (단일 서버)
- 스테이징 환경 안정화
- 내부 도구 배포

</details>

<details>
<summary><strong>5. Compose 파일에서 빌드 성능을 최적화하는 방법은?</strong></summary>

**모범 답안 포인트**
- 멀티 스테이지 빌드
- 빌드 캐시 활용
- BuildKit 사용
- .dockerignore 최적화

**예시 답변**
> "Compose에서 빌드 성능을 최적화하는 핵심은 빌드 캐시를 효율적으로 활용하는 것입니다. 첫째, Dockerfile에서 멀티 스테이지 빌드를 사용하여 의존성 설치와 애플리케이션 빌드를 분리합니다. package.json만 먼저 COPY하여 의존성을 설치하면, 코드 변경 시에도 의존성 레이어는 캐시됩니다. 둘째, BuildKit을 활성화하여 병렬 빌드와 고급 캐싱을 사용합니다. `DOCKER_BUILDKIT=1 docker compose build`로 실행하면 빌드 속도가 2-3배 향상됩니다. 셋째, `.dockerignore`에 `node_modules`, `.git`, `*.log` 등을 추가하여 불필요한 파일이 빌드 컨텍스트에 포함되지 않도록 합니다. 넷째, 외부 캐시를 사용하여 CI/CD에서도 캐시를 재사용합니다. 실무에서 이 방법들을 적용하면 10분 걸리던 빌드가 1-2분으로 단축됩니다."

**최적화 예시**:
```dockerfile
# Dockerfile (최적화)
FROM node:18 AS builder

WORKDIR /app

# 1단계: 의존성만 먼저 설치 (캐시 활용)
COPY package*.json ./
RUN npm ci --only=production

# 2단계: 소스 코드 복사 (캐시 무효화 최소화)
COPY . .
RUN npm run build

# 3단계: 프로덕션 이미지
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/server.js"]
```

```yaml
# docker-compose.yml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
      cache_from:
        - myapi:latest
      args:
        BUILDKIT_INLINE_CACHE: 1
```

**.dockerignore**:
```
node_modules
.git
.env
*.log
.DS_Store
coverage
dist
```

**실무 연관**
- CI/CD 파이프라인 빌드 시간 단축
- 로컬 개발 환경 재빌드 시간 최소화
- 대규모 모노레포 환경 최적화

</details>

---

## 📝 핵심 정리

### 이 장에서 배운 핵심 개념

| 개념 | 설명 | 핵심 키워드 |
|------|------|-------------|
| Docker Compose | 여러 컨테이너를 YAML로 정의/관리 | 선언적, 재현 가능, 팀 협업 |
| docker-compose.yml | 서비스, 네트워크, 볼륨 정의 | services, networks, volumes |
| depends_on | 컨테이너 시작 순서 제어 | 의존성, healthcheck 조합 |
| 환경 변수 | .env 파일로 설정 관리 | env_file, environment, ${VAR} |
| 볼륨 | 데이터 영구 저장 | named volume, bind mount |
| 네트워크 | 서비스 간 통신 및 격리 | 서비스 디스커버리, DNS |

### 필수 명령어 정리

| 명령어 | 용도 | 예시 |
|--------|------|------|
| `docker compose up -d` | 서비스 시작 (백그라운드) | `docker compose up -d` |
| `docker compose down` | 서비스 중지 및 제거 | `docker compose down` |
| `docker compose down -v` | 볼륨까지 제거 | `docker compose down -v` |
| `docker compose logs -f` | 실시간 로그 확인 | `docker compose logs -f api` |
| `docker compose ps` | 실행 중인 컨테이너 확인 | `docker compose ps` |
| `docker compose exec` | 컨테이너 내부 명령 실행 | `docker compose exec db psql` |
| `docker compose restart` | 서비스 재시작 | `docker compose restart api` |
| `docker compose build` | 이미지 빌드 | `docker compose build --no-cache` |

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] 프로젝트마다 docker-compose.yml 작성하여 환경 표준화
- [ ] .env 파일 사용하여 환경별 설정 분리
- [ ] depends_on + healthcheck로 시작 순서 보장
- [ ] 명명된 볼륨으로 중요 데이터 영구 저장
- [ ] Git에 docker-compose.yml 커밋 (.env는 제외)
- [ ] 프로덕션에서는 명시적 이미지 버전 사용 (latest 금지)
- [ ] 리소스 제한 설정으로 안정성 확보

#### ❌ 하지 말아야 할 것
- [ ] 민감 정보를 docker-compose.yml에 평문 작성
- [ ] 볼륨 없이 데이터베이스 실행 (데이터 손실 위험)
- [ ] latest 태그를 프로덕션에서 사용
- [ ] 모든 서비스를 하나의 compose 파일에 몰아넣기 (관심사 분리)
- [ ] depends_on만으로 의존성 관리 (healthcheck 병행 필요)
- [ ] docker compose down -v를 습관적으로 사용 (데이터 손실)

### 성능/보안 체크리스트

#### 성능
- [ ] 멀티 스테이지 빌드로 이미지 크기 최소화
- [ ] BuildKit 활성화로 빌드 속도 향상
- [ ] .dockerignore로 불필요한 파일 제외
- [ ] 의존성 레이어 캐싱 최적화

#### 보안
- [ ] 비밀 정보는 환경 변수 또는 Docker Secrets 사용
- [ ] read_only: true로 파일시스템 보호
- [ ] 최소 권한 원칙 (non-root 사용자)
- [ ] 내부 네트워크 격리 (internal: true)
- [ ] 명시적 이미지 버전으로 공급망 공격 방지

---

## 12.7 다음 단계

### 다음 장 미리보기: Docker Compose 심화

Docker Compose 기초를 마스터했습니다! 다음 섹션에서는:

- **배울 내용 1**: 오버라이드 파일로 환경별 설정 관리
- **배울 내용 2**: 프로파일로 선택적 서비스 실행
- **배울 내용 3**: 헬스체크와 의존성 고급 패턴
- **배울 내용 4**: 확장 필드로 설정 재사용
- **실전 프로젝트**: 멀티 환경 마이크로서비스 구축

### 이 장과의 연결점
```
이번 장에서 배운 [기본 docker-compose.yml 작성]
    ↓
다음 장에서 [고급 패턴과 프로덕션 최적화]
    ↓
최종적으로 [실무 수준의 컨테이너 오케스트레이션]
```

### 준비하면 좋을 것들
```bash
# 다음 장 실습을 위한 준비
# 1. 여러 환경 파일 생성
touch docker-compose.yml docker-compose.prod.yml docker-compose.dev.yml

# 2. 프로파일 실습용 프로젝트 클론
git clone https://github.com/example/compose-advanced-demo

# 3. BuildKit 확인
docker buildx version
```

---

## 🎉 축하합니다!

**이제 여러분은**:
✅ Docker Compose로 여러 컨테이너를 한 번에 관리할 수 있습니다
✅ YAML 파일로 재현 가능한 개발 환경을 구축할 수 있습니다
✅ 환경 변수와 볼륨으로 안전하게 데이터를 관리할 수 있습니다
✅ 실무에서 팀원과 협업 가능한 인프라 코드를 작성할 수 있습니다
✅ 기본적인 마이크로서비스 아키텍처를 로컬에서 실행할 수 있습니다

**다음 단계**:
- [ ] 섹션 13: Docker Compose 심화로 진행
- [ ] 실전 프로젝트: 자신의 프로젝트를 Compose로 변환해보기
- [ ] 면접 질문 복습하여 개념 확실히 다지기

---

**다음 장으로 이동**: [다음: 섹션 13 - Docker Compose 심화 →](13-Docker-Compose-심화.md)

**이전 장으로 돌아가기**: [← 이전: 섹션 11](11-이전-섹션.md)

**목차로 돌아가기**: [📚 전체 목차](../README.md)

계속 학습하세요! 🚀