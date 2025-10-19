# 섹션 11: Docker 볼륨 완전 가이드

> **학습 목표**: 이 장을 완료하면 Docker 볼륨을 사용하여 컨테이너 데이터를 안전하게 영속화하고, 백업/복원/마이그레이션을 자유롭게 수행할 수 있습니다.

**⏱️ 예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐☆☆ (3개/5개)

---

## 📚 목차
- [데이터 영속성 필요성](#111-데이터-영속성-필요성)
- [실생활 비유로 이해하기](#🌟-실생활-비유로-이해하기)
- [볼륨 vs 바인드 마운트 vs tmpfs](#112-볼륨-vs-바인드-마운트-vs-tmpfs)
- [볼륨 생성 및 관리](#113-볼륨-생성-및-관리)
- [볼륨 드라이버](#114-볼륨-드라이버)
- [볼륨 백업 및 복원](#115-볼륨-백업-및-복원)
- [데이터 마이그레이션](#116-데이터-마이그레이션)
- [컨테이너 간 볼륨 공유](#117-컨테이너-간-볼륨-공유)
- [실습 예제](#118-실습-예제)
- [문제 해결](#119-문제-해결)
- [베스트 프랙티스](#1110-베스트-프랙티스)
- [주니어 시나리오](#👨‍💻-주니어-시나리오)
- [FAQ](#❓-faq)
- [면접 질문 리스트](#💼-면접-질문-리스트)
- [핵심 정리](#📝-핵심-정리)

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 호텔과 개인 창고

```
[컨테이너 = 호텔 방]
체크아웃하면 → 짐 모두 사라짐 ❌
새 손님(컨테이너) → 깨끗한 방(초기 상태)

[볼륨 = 개인 창고]
호텔을 옮겨도 → 창고의 짐은 그대로 ✅
언제든지 → 창고에서 꺼내 사용 가능

┌────────────────────────────────────┐
│  [호텔 A]   [호텔 B]   [호텔 C]    │
│     ↓          ↓          ↓        │
│  [개인 창고] ← 항상 접근 가능       │
└────────────────────────────────────┘
```

### 비유 2: USB 메모리와 클라우드 저장소

```
[바인드 마운트 = USB 메모리]
- 특정 위치에 꽂아야 함 (호스트 경로 의존)
- 컴퓨터마다 드라이브 문자 다름 (크로스 플랫폼 이슈)
- 직접 파일 확인/수정 가능 ✅

[Docker 볼륨 = 클라우드 저장소]
- 어디서나 접근 (Docker가 관리)
- 자동 동기화 (자동 권한 관리)
- 클라우드만 알면 됨 (경로 몰라도 OK)

[tmpfs = 휘발성 메모리]
- 전원 꺼지면 사라짐 (재부팅 시 삭제)
- 매우 빠름 ✅
- 중요 데이터는 저장 금지 ⚠️
```

### 비유 3: 아파트 거주와 창고 이용

```
[시나리오]
아파트 이사 = 컨테이너 재생성
개인 창고 = Docker 볼륨

[이사 전]
101호 거주 (컨테이너 A)
    ↓
창고에 짐 보관 (볼륨에 데이터 저장)

[이사 후]
201호로 이사 (컨테이너 B)
    ↓
같은 창고 계속 사용 (같은 볼륨 마운트)
    ↓
짐은 그대로 ✅ (데이터 유지)
```

### 비유 4: 배달앱 주문 데이터

```
[배달의민족/쿠팡이츠 시나리오]

앱 업데이트 (컨테이너 재생성)
    ↓
[잘못된 경우]
주문 내역 사라짐 ❌
찜한 식당 초기화 ❌
포인트 소멸 ❌

    ↓
[올바른 경우 - 볼륨 사용]
주문 내역 유지 ✅
찜한 식당 그대로 ✅
포인트 보존 ✅

데이터베이스 = Docker 볼륨
앱(컨테이너) 업데이트 ≠ 데이터 손실
```

### 비유 5: 게임 캐릭터와 세이브 파일

```
[게임 = 컨테이너]
게임 삭제/재설치 → 기본 상태로 초기화

[세이브 파일 = 볼륨]
게임 재설치해도 → 세이브 파일 유지
다른 컴퓨터에서도 → 세이브 파일 로드 가능

┌─────────────────────────────────┐
│  컴퓨터 A        컴퓨터 B        │
│    ↓               ↓            │
│ 게임 실행       게임 실행        │
│    ↓               ↓            │
│ [세이브 파일 - 클라우드 저장]    │
│    ↓               ↓            │
│ 레벨 100       레벨 100 (동일)  │
└─────────────────────────────────┘
```

### 비유 6: 은행 계좌 시스템

```
[은행 앱 = 컨테이너]
앱 삭제 → 앱만 삭제됨
앱 재설치 → 깨끗한 앱

[계좌 잔액 = 볼륨]
앱과 무관 → 은행 서버에 저장
앱 재설치해도 → 잔액 그대로 ✅

실제 구조:
├─ 카카오뱅크 앱 (컨테이너)
├─ 토스 앱 (컨테이너)
└─ 계좌 데이터베이스 (볼륨) ← 영구 보존
```

### 🎯 종합 비교표

| 개념 | 비유 1 (호텔) | 비유 2 (저장소) | 비유 3 (아파트) | 비유 4 (배달앱) | 비유 5 (게임) |
|------|--------------|----------------|----------------|----------------|--------------|
| **컨테이너** | 호텔 방 | 앱 | 아파트 호실 | 배달앱 | 게임 |
| **볼륨** | 개인 창고 | 클라우드 | 창고 | 주문 DB | 세이브 파일 |
| **재생성** | 다른 방으로 이동 | 앱 재설치 | 이사 | 앱 업데이트 | 게임 재설치 |
| **데이터 유지** | 창고는 그대로 | 클라우드 유지 | 창고는 계속 사용 | 주문내역 유지 | 세이브 유지 |

---

## 📊 수치로 보는 효과

| 지표 | 볼륨 없이 | 볼륨 사용 | 개선율 |
|------|-----------|-----------|--------|
| **데이터 손실 위험** | 컨테이너 재생성 시 100% 손실 | 0% 손실 | **100%↓** |
| **백업 시간** | 컨테이너 전체 (5GB, 10분) | 볼륨만 (500MB, 1분) | **90%↓** |
| **마이그레이션 시간** | 30분 (수동 작업) | 5분 (볼륨 연결) | **83%↓** |
| **스토리지 효율** | 컨테이너마다 복제 (10GB×3) | 공유 볼륨 (10GB×1) | **67%↓** |
| **개발 환경 구성** | 매번 초기화 (30분) | 볼륨으로 즉시 (1분) | **97%↓** |

---

## 11.1 데이터 영속성 필요성

### 11.1.1 컨테이너의 문제점

**실생활 비유: 임시 숙소 vs 창고**

```
[컨테이너 = 호텔 방]
체크아웃하면 → 짐 모두 사라짐 ❌
새 손님(컨테이너) → 깨끗한 방(초기 상태)

[볼륨 = 개인 창고]
호텔을 옮겨도 → 창고의 짐은 그대로 ✅
언제든지 → 창고에서 꺼내 사용 가능
```

#### 컨테이너 없이 데이터 저장 시

```bash
# PostgreSQL 컨테이너 실행
docker run -d --name postgres postgres:15-alpine

# 데이터베이스 생성 및 데이터 추가
docker exec -it postgres psql -U postgres
# CREATE TABLE users (id SERIAL, name TEXT);
# INSERT INTO users (name) VALUES ('Alice'), ('Bob');
# \q

# 컨테이너 삭제
docker rm -f postgres

# 새 컨테이너 실행
docker run -d --name postgres postgres:15-alpine

# 데이터 확인
docker exec -it postgres psql -U postgres -c "SELECT * FROM users;"
# ERROR: relation "users" does not exist
# 😱 모든 데이터가 사라짐!
```

**문제 발생 상황:**

```
1. 컨테이너 재시작
   docker restart postgres  # ✅ 데이터 유지 (컨테이너만 재시작)

2. 컨테이너 재생성
   docker rm -f postgres && docker run ...  # ❌ 데이터 손실!

3. 이미지 업데이트
   docker pull postgres:16 && docker run ...  # ❌ 데이터 손실!

4. 장애 복구
   컨테이너 크래시 후 재생성  # ❌ 데이터 손실!
```

---

### 11.1.2 볼륨의 해결책

```bash
# 볼륨 생성
docker volume create pgdata

# 볼륨을 사용하는 컨테이너 실행
docker run -d \
  --name postgres \
  -v pgdata:/var/lib/postgresql/data \
  postgres:15-alpine

# 데이터 추가
docker exec -it postgres psql -U postgres \
  -c "CREATE TABLE users (id SERIAL, name TEXT);" \
  -c "INSERT INTO users (name) VALUES ('Alice'), ('Bob');"

# 컨테이너 삭제
docker rm -f postgres

# 새 컨테이너 실행 (같은 볼륨 사용)
docker run -d \
  --name postgres \
  -v pgdata:/var/lib/postgresql/data \
  postgres:15-alpine

# 데이터 확인
docker exec -it postgres psql -U postgres -c "SELECT * FROM users;"
#  id | name
# ----+-------
#   1 | Alice
#   2 | Bob
# ✅ 데이터가 그대로 유지됨!
```

**볼륨의 생명주기:**

```
[컨테이너 생명주기]
create → start → stop → rm
         ↑________________↑
         데이터는 컨테이너와 함께 삭제 ❌

[볼륨 생명주기]
create → 사용 → 사용 → 사용 → ...
  ↓       ↓       ↓       ↓
 컨테이너1  컨테이너2  컨테이너3  컨테이너4

명시적으로 삭제하기 전까지 영구 보존 ✅
```

---

## 11.2 볼륨 vs 바인드 마운트 vs tmpfs

### 11.2.1 세 가지 방식 비교

```
[호스트 파일 시스템]
├─ /var/lib/docker/volumes/
│   └─ myvolume/_data/          ← Docker 볼륨 (Docker 관리)
│       └─ database files
│
├─ /home/user/project/
│   └─ config.json              ← 바인드 마운트 (사용자 관리)
│
└─ [메모리]
    └─ tmpfs 마운트             ← 임시 저장 (메모리, 빠름)
```

**비교표:**

| 특징 | Docker 볼륨 | 바인드 마운트 | tmpfs |
|------|-------------|---------------|-------|
| **저장 위치** | Docker 관리 디렉토리 | 호스트 임의 경로 | 메모리 |
| **관리 주체** | Docker | 사용자 | Docker |
| **명령어로 관리** | ✅ docker volume | ❌ | ❌ |
| **성능** | 빠름 | 보통 | 매우 빠름 |
| **크로스 플랫폼** | ✅ | ⚠️ (경로 차이) | ✅ |
| **백업** | 쉬움 | 쉬움 | ❌ (휘발성) |
| **권한 관리** | Docker 자동 | 수동 설정 필요 | Docker 자동 |
| **사용 사례** | DB, 파일 저장소 | 설정 파일, 소스 코드 | 비밀번호, 캐시 |

---

### 11.2.2 Docker 볼륨 (Volume)

#### 특징

```
✅ Docker가 완전히 관리
✅ 호스트 경로를 몰라도 됨
✅ 다양한 드라이버 지원 (NFS, AWS EBS 등)
✅ 컨테이너 간 공유 용이
✅ 볼륨 드라이버로 원격 저장소 사용 가능
```

#### 사용법

```bash
# 1. 볼륨 생성
docker volume create mydata

# 2. 컨테이너에서 사용
docker run -d \
  --name app \
  -v mydata:/app/data \
  myapp:latest

# 또는 --mount 문법 (명확함, 권장)
docker run -d \
  --name app \
  --mount source=mydata,target=/app/data \
  myapp:latest
```

#### 볼륨 위치 확인

```bash
# 볼륨 상세 정보
docker volume inspect mydata

# 출력:
# [
#     {
#         "CreatedAt": "2024-01-15T10:30:00Z",
#         "Driver": "local",
#         "Mountpoint": "/var/lib/docker/volumes/mydata/_data",
#         "Name": "mydata",
#         "Scope": "local"
#     }
# ]

# 실제 파일 확인 (Linux)
sudo ls -la /var/lib/docker/volumes/mydata/_data

# macOS/Windows (Docker Desktop)
# Docker VM 내부에 저장되어 직접 접근 어려움
```

---

### 11.2.3 바인드 마운트 (Bind Mount)

#### 특징

```
✅ 호스트의 정확한 경로 지정
✅ 개발 중 실시간 코드 반영 (핫 리로드)
✅ 호스트 파일 직접 수정 가능
⚠️  호스트 경로가 존재해야 함
⚠️  권한 문제 발생 가능
❌ 크로스 플랫폼 경로 차이
```

#### 사용법

```bash
# 호스트 디렉토리를 컨테이너에 마운트
docker run -d \
  --name webapp \
  -v /home/user/project:/app \
  node:18-alpine

# --mount 문법 (권장)
docker run -d \
  --name webapp \
  --mount type=bind,source=/home/user/project,target=/app \
  node:18-alpine

# Windows 경로
docker run -d \
  --name webapp \
  -v C:\Users\user\project:/app \
  node:18-alpine
```

#### 개발 환경에서 활용

```bash
# Node.js 앱 개발
docker run -it --rm \
  --name dev \
  -v $(pwd):/app \
  -w /app \
  -p 3000:3000 \
  node:18-alpine \
  sh -c "npm install && npm run dev"

# 소스 코드 수정 시 자동 반영 (핫 리로드)
```

#### 읽기 전용 마운트

```bash
# 컨테이너에서 수정 불가
docker run -d \
  --name app \
  -v /host/config:/app/config:ro \
  myapp:latest

# 쓰기 시도 시 에러
docker exec app sh -c "echo 'test' > /app/config/test.txt"
# sh: can't create /app/config/test.txt: Read-only file system
```

---

### 11.2.4 tmpfs 마운트

#### 특징

```
✅ 메모리에 저장 (매우 빠름)
✅ 컨테이너 종료 시 자동 삭제 (보안)
✅ 민감한 데이터 임시 저장
❌ 영속성 없음
❌ 컨테이너 간 공유 불가
❌ Linux만 지원
```

#### 사용법

```bash
# tmpfs 마운트
docker run -d \
  --name app \
  --mount type=tmpfs,target=/app/cache,tmpfs-size=100m,tmpfs-mode=1777 \
  myapp:latest

# 또는 --tmpfs
docker run -d \
  --name app \
  --tmpfs /app/cache:rw,size=100m,mode=1777 \
  myapp:latest
```

#### 사용 사례

```bash
# 1. 세션 데이터
docker run -d \
  --name webapp \
  --tmpfs /tmp/sessions:size=50m \
  webapp:latest

# 2. 임시 파일 처리
docker run -d \
  --name worker \
  --tmpfs /tmp/processing:size=500m \
  worker:latest

# 3. 비밀번호 임시 저장
docker run -d \
  --name secure-app \
  --tmpfs /run/secrets:size=10m,mode=0700 \
  secure-app:latest
```

---

### 11.2.5 선택 가이드

```
📊 데이터베이스 (PostgreSQL, MySQL, MongoDB)
   → Docker 볼륨 ✅
   이유: 영속성, 성능, 백업 용이

🔧 개발 중 소스 코드
   → 바인드 마운트 ✅
   이유: 실시간 반영, 직접 편집 가능

📝 설정 파일 (nginx.conf, app.config)
   → 바인드 마운트 (읽기 전용) ✅
   이유: 버전 관리, 쉬운 수정

🔐 비밀번호, API 키, 세션
   → tmpfs ✅
   이유: 보안 (메모리만, 디스크 기록 없음)

📦 프로덕션 애플리케이션 데이터
   → Docker 볼륨 ✅
   이유: 안정성, 백업, 마이그레이션

🚀 고성능 캐시 (Redis, Memcached)
   → tmpfs (선택사항) ✅
   이유: 초고속, 데이터 휘발성 OK
```

---

## 11.3 볼륨 생성 및 관리

### 11.3.1 볼륨 생성

```bash
# 기본 생성
docker volume create mydata

# 드라이버 지정 생성
docker volume create \
  --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.100,rw \
  --opt device=:/path/to/share \
  nfs-volume

# 레이블 지정
docker volume create \
  --label project=myapp \
  --label environment=production \
  --label backup=daily \
  prod-data
```

---

### 11.3.2 볼륨 조회

```bash
# 모든 볼륨 목록
docker volume ls

# 출력:
# DRIVER    VOLUME NAME
# local     mydata
# local     prod-data
# local     abc123def456  (익명 볼륨)

# 필터링
docker volume ls --filter name=prod
docker volume ls --filter label=project=myapp
docker volume ls --filter dangling=true  # 사용하지 않는 볼륨

# 상세 정보
docker volume inspect mydata

# JSON 출력:
# [
#     {
#         "CreatedAt": "2024-01-15T10:30:00Z",
#         "Driver": "local",
#         "Labels": {
#             "project": "myapp",
#             "environment": "production"
#         },
#         "Mountpoint": "/var/lib/docker/volumes/mydata/_data",
#         "Name": "mydata",
#         "Options": {},
#         "Scope": "local"
#     }
# ]

# 특정 필드만 추출
docker volume inspect mydata --format '{{ .Mountpoint }}'
# /var/lib/docker/volumes/mydata/_data
```

---

### 11.3.3 볼륨 삭제

```bash
# 특정 볼륨 삭제
docker volume rm mydata

# 사용 중인 볼륨 삭제 시도
docker volume rm prod-data
# Error: volume is in use - [abc123]

# 강제 삭제 (컨테이너 먼저 중지 필요)
docker stop mycontainer
docker rm mycontainer
docker volume rm prod-data

# 사용하지 않는 모든 볼륨 삭제
docker volume prune

# 출력:
# WARNING! This will remove all local volumes not used by at least one container.
# Are you sure you want to continue? [y/N] y
# Deleted Volumes:
# old-volume-1
# old-volume-2
# Total reclaimed space: 2.5GB

# 강제 삭제 (확인 없이)
docker volume prune -f

# 필터와 함께 사용
docker volume prune --filter "label=temporary=true"
```

---

### 11.3.4 익명 볼륨 vs 명명된 볼륨

#### 익명 볼륨

```bash
# Dockerfile에서 VOLUME 선언
FROM postgres:15-alpine
VOLUME /var/lib/postgresql/data

# 컨테이너 실행 시 자동 생성
docker run -d --name postgres postgres:15-alpine

# 자동 생성된 익명 볼륨 확인
docker volume ls
# DRIVER    VOLUME NAME
# local     abc123def456789...  (랜덤 이름)

# 문제점: 관리 어려움
docker rm -f postgres
docker volume ls
# 여전히 존재 (고아 볼륨)
```

#### 명명된 볼륨 (권장)

```bash
# 명시적으로 볼륨 생성
docker volume create pgdata

# 컨테이너 실행 시 지정
docker run -d \
  --name postgres \
  -v pgdata:/var/lib/postgresql/data \
  postgres:15-alpine

# 관리 용이
docker volume ls
# DRIVER    VOLUME NAME
# local     pgdata  (의미 있는 이름)
```

---

## 11.4 볼륨 드라이버

### 11.4.1 기본 드라이버 (local)

```bash
# 기본 local 드라이버
docker volume create mydata
# = docker volume create --driver local mydata
```

**local 드라이버 옵션:**

```bash
# 1. 특정 파일 시스템 타입
docker volume create \
  --driver local \
  --opt type=tmpfs \
  --opt device=tmpfs \
  --opt o=size=100m,uid=1000 \
  tmpfs-volume

# 2. 바인드 마운트로 생성
docker volume create \
  --driver local \
  --opt type=none \
  --opt device=/path/on/host \
  --opt o=bind \
  bind-volume

# 3. NFS 마운트
docker volume create \
  --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.100,rw,nfsvers=4 \
  --opt device=:/path/to/share \
  nfs-volume
```

---

### 11.4.2 NFS 볼륨 (네트워크 파일 시스템)

#### 시나리오: 여러 호스트에서 같은 볼륨 공유

```
[NFS 서버: 192.168.1.100]
└─ /mnt/shared-data/
    └─ uploads/

[Docker 호스트 A: 192.168.1.101]
└─ [Container 1] → NFS 볼륨

[Docker 호스트 B: 192.168.1.102]
└─ [Container 2] → NFS 볼륨

두 컨테이너가 같은 데이터 공유 ✅
```

#### NFS 서버 설정 (Ubuntu)

```bash
# NFS 서버 설치
sudo apt-get update
sudo apt-get install -y nfs-kernel-server

# 공유 디렉토리 생성
sudo mkdir -p /mnt/shared-data
sudo chown nobody:nogroup /mnt/shared-data
sudo chmod 777 /mnt/shared-data

# /etc/exports 편집
sudo nano /etc/exports
# 추가:
# /mnt/shared-data 192.168.1.0/24(rw,sync,no_subtree_check,no_root_squash)

# NFS 서버 재시작
sudo exportfs -a
sudo systemctl restart nfs-kernel-server
```

#### Docker에서 NFS 볼륨 사용

```bash
# NFS 볼륨 생성
docker volume create \
  --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.100,rw,nfsvers=4 \
  --opt device=:/mnt/shared-data \
  shared-volume

# 컨테이너에서 사용
docker run -d \
  --name app1 \
  -v shared-volume:/app/data \
  myapp:latest

# 다른 호스트에서도 같은 방법으로 사용
# (같은 NFS 서버 가리킴)
```

---

### 11.4.3 클라우드 스토리지 볼륨 드라이버

#### AWS EBS (Elastic Block Store)

```bash
# REX-Ray 플러그인 설치
docker plugin install rexray/ebs \
  EBS_REGION=us-east-1 \
  EBS_ACCESSKEY=AKIA... \
  EBS_SECRETKEY=...

# EBS 볼륨 생성
docker volume create \
  --driver rexray/ebs \
  --opt size=10 \
  ebs-volume

# 컨테이너에서 사용
docker run -d \
  --name app \
  -v ebs-volume:/app/data \
  myapp:latest
```

#### Azure File Storage

```bash
# Azure File 드라이버 설치
docker plugin install --alias azure \
  --grant-all-permissions \
  docker4x/cloudstor:azure

# Azure 볼륨 생성
docker volume create \
  --driver azure \
  --opt share=myshare \
  azure-volume
```

---

### 11.4.4 커스텀 볼륨 드라이버

**사용 가능한 드라이버:**

| 드라이버 | 용도 | 특징 |
|---------|------|------|
| **local** | 로컬 스토리지 | 기본, 빠름 |
| **nfs** | 네트워크 공유 | 여러 호스트 공유 |
| **rexray/ebs** | AWS EBS | 클라우드, 스냅샷 |
| **rexray/s3fs** | AWS S3 | 객체 스토리지 |
| **convoy** | 백업/복원 | 스냅샷, 백업 |
| **flocker** | 컨테이너 마이그레이션 | 볼륨과 컨테이너 함께 이동 |

---

## 11.5 볼륨 백업 및 복원

### 11.5.1 방법 1: tar 아카이브

#### 백업

```bash
# 1. 백업할 볼륨이 연결된 컨테이너 실행
docker run --rm \
  -v mydata:/data \
  -v $(pwd):/backup \
  alpine \
  tar czf /backup/mydata-backup-$(date +%Y%m%d-%H%M%S).tar.gz -C /data .

# 설명:
# --rm: 작업 후 컨테이너 자동 삭제
# -v mydata:/data: 백업할 볼륨
# -v $(pwd):/backup: 백업 파일 저장 위치
# tar czf: 압축 아카이브 생성
```

**실행 결과:**

```bash
ls -lh mydata-backup-*.tar.gz
# -rw-r--r-- 1 user user 125M Jan 15 10:30 mydata-backup-20240115-103045.tar.gz
```

#### 복원

```bash
# 1. 새 볼륨 생성
docker volume create mydata-restored

# 2. 백업 파일에서 복원
docker run --rm \
  -v mydata-restored:/data \
  -v $(pwd):/backup \
  alpine \
  tar xzf /backup/mydata-backup-20240115-103045.tar.gz -C /data

# 3. 검증
docker run --rm \
  -v mydata-restored:/data \
  alpine \
  ls -la /data
```

---

### 11.5.2 방법 2: 컨테이너 중지 없이 백업

```bash
# PostgreSQL 예시 (컨테이너 실행 중)
docker exec postgres \
  pg_dump -U postgres mydb > backup.sql

# 복원
docker exec -i postgres \
  psql -U postgres mydb < backup.sql
```

---

### 11.5.3 방법 3: 스크립트 자동화

**backup-volume.sh:**

```bash
#!/bin/bash

# 사용법: ./backup-volume.sh <볼륨이름> [백업디렉토리]

VOLUME_NAME=$1
BACKUP_DIR=${2:-./backups}
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${VOLUME_NAME}-${TIMESTAMP}.tar.gz"

# 백업 디렉토리 생성
mkdir -p "$BACKUP_DIR"

echo "Backing up volume: $VOLUME_NAME"
echo "Backup file: $BACKUP_FILE"

# 백업 실행
docker run --rm \
  -v "$VOLUME_NAME":/data \
  -v "$BACKUP_DIR":/backup \
  alpine \
  sh -c "cd /data && tar czf /backup/$(basename $BACKUP_FILE) ."

# 백업 파일 크기 확인
if [ -f "$BACKUP_FILE" ]; then
  SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
  echo "Backup completed successfully: $SIZE"
else
  echo "Backup failed!"
  exit 1
fi

# 7일 이전 백업 파일 삭제
find "$BACKUP_DIR" -name "${VOLUME_NAME}-*.tar.gz" -mtime +7 -delete
echo "Old backups cleaned up (>7 days)"
```

**사용:**

```bash
chmod +x backup-volume.sh

# 백업 실행
./backup-volume.sh pgdata
# Backing up volume: pgdata
# Backup file: ./backups/pgdata-20240115-103045.tar.gz
# Backup completed successfully: 125M
# Old backups cleaned up (>7 days)

# cron으로 자동화 (매일 새벽 2시)
crontab -e
# 0 2 * * * /path/to/backup-volume.sh pgdata /mnt/backups
```

---

### 11.5.4 방법 4: Docker CLI 플러그인 사용

```bash
# 볼륨 백업 플러グ인 설치
docker plugin install vieux/sshfs

# 원격 백업
docker volume create \
  --driver vieux/sshfs \
  -o sshcmd=user@backup-server:/backups \
  -o password=secret \
  remote-backup

# 백업 실행
docker run --rm \
  -v mydata:/source:ro \
  -v remote-backup:/backup \
  alpine \
  cp -a /source/. /backup/
```

---

## 11.6 데이터 마이그레이션

### 11.6.1 같은 호스트 내 마이그레이션

```bash
# 시나리오: 볼륨 이름 변경

# 1. 새 볼륨 생성
docker volume create new-volume

# 2. 데이터 복사
docker run --rm \
  -v old-volume:/source:ro \
  -v new-volume:/target \
  alpine \
  sh -c "cp -av /source/. /target/"

# 3. 컨테이너를 새 볼륨으로 재시작
docker stop mycontainer
docker rm mycontainer
docker run -d \
  --name mycontainer \
  -v new-volume:/app/data \
  myapp:latest

# 4. 검증 후 이전 볼륨 삭제
docker volume rm old-volume
```

---

### 11.6.2 다른 호스트로 마이그레이션

#### 방법 1: SSH를 통한 직접 전송

```bash
# 호스트 A에서 실행
docker run --rm \
  -v mydata:/data \
  alpine \
  tar czf - -C /data . \
  | ssh user@hostB "docker run --rm -i -v mydata:/data alpine tar xzf - -C /data"

# 설명:
# 1. 호스트 A: 볼륨 → tar 압축 → stdout
# 2. SSH로 전송
# 3. 호스트 B: stdin → tar 압축 해제 → 볼륨
```

#### 방법 2: 중간 파일 사용

```bash
# 호스트 A: 백업
docker run --rm \
  -v mydata:/data \
  -v $(pwd):/backup \
  alpine \
  tar czf /backup/data.tar.gz -C /data .

# 파일 전송
scp data.tar.gz user@hostB:/tmp/

# 호스트 B: 복원
docker volume create mydata
docker run --rm \
  -v mydata:/data \
  -v /tmp:/backup \
  alpine \
  tar xzf /backup/data.tar.gz -C /data
```

---

### 11.6.3 클라우드로 마이그레이션

#### AWS S3 사용

```bash
# 1. 볼륨 백업
docker run --rm \
  -v mydata:/data \
  -v $(pwd):/backup \
  alpine \
  tar czf /backup/data.tar.gz -C /data .

# 2. S3에 업로드
aws s3 cp data.tar.gz s3://my-bucket/backups/

# 3. 다른 EC2 인스턴스에서 다운로드
aws s3 cp s3://my-bucket/backups/data.tar.gz /tmp/

# 4. 복원
docker volume create mydata
docker run --rm \
  -v mydata:/data \
  -v /tmp:/backup \
  alpine \
  tar xzf /backup/data.tar.gz -C /data
```

---

## 11.7 컨테이너 간 볼륨 공유

### 11.7.1 같은 호스트 내 공유

#### 시나리오: Nginx + PHP-FPM

```bash
# 볼륨 생성
docker volume create webroot

# PHP-FPM (파일 생성)
docker run -d \
  --name php-fpm \
  -v webroot:/var/www/html \
  php:8.2-fpm

# Nginx (파일 서빙)
docker run -d \
  --name nginx \
  -v webroot:/var/www/html:ro \
  -p 80:80 \
  nginx:alpine

# 파일 추가
docker exec php-fpm sh -c "echo '<?php phpinfo(); ?>' > /var/www/html/info.php"

# 브라우저에서 확인
curl http://localhost/info.php
```

**구조:**

```
[webroot 볼륨]
    ↓          ↓
[php-fpm]   [nginx]
  (RW)        (RO)
   ↓
파일 생성      파일 서빙
```

---

### 11.7.2 volumes-from (레거시 방식)

```bash
# 데이터 컨테이너 (더 이상 권장하지 않음)
docker create -v /data --name datastore alpine

# 다른 컨테이너에서 볼륨 공유
docker run -d --volumes-from datastore --name app1 myapp
docker run -d --volumes-from datastore --name app2 myapp

# 현대적 방식: 명명된 볼륨 사용 (권장)
docker volume create shared-data
docker run -d -v shared-data:/data --name app1 myapp
docker run -d -v shared-data:/data --name app2 myapp
```

---

### 11.7.3 읽기 전용 공유

```bash
# 볼륨 생성 및 데이터 추가
docker volume create config-data
docker run --rm \
  -v config-data:/data \
  alpine \
  sh -c "echo 'production config' > /data/config.txt"

# 읽기 전용으로 공유
docker run -d \
  --name app1 \
  -v config-data:/app/config:ro \
  myapp:latest

docker run -d \
  --name app2 \
  -v config-data:/app/config:ro \
  myapp:latest

# 쓰기 시도 시 실패
docker exec app1 sh -c "echo 'test' > /app/config/test.txt"
# sh: can't create /app/config/test.txt: Read-only file system
```

---

### 11.7.4 Docker Compose로 볼륨 공유

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  # PHP 애플리케이션
  php:
    image: php:8.2-fpm
    volumes:
      - webroot:/var/www/html
      - app-logs:/var/log/php
    networks:
      - backend

  # Nginx 웹 서버
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - webroot:/var/www/html:ro  # 읽기 전용
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - nginx-logs:/var/log/nginx
    depends_on:
      - php
    networks:
      - backend

  # 로그 수집기
  logstash:
    image: logstash:8.11.0
    volumes:
      - app-logs:/logs/app:ro
      - nginx-logs:/logs/nginx:ro
    networks:
      - backend

volumes:
  webroot:
    driver: local
  app-logs:
    driver: local
  nginx-logs:
    driver: local

networks:
  backend:
```

**볼륨 공유 구조:**

```
[webroot]
  ├─ php (RW)     → 파일 생성/수정
  └─ nginx (RO)   → 파일 읽기만

[app-logs]
  ├─ php (RW)        → 로그 작성
  └─ logstash (RO)   → 로그 수집

[nginx-logs]
  ├─ nginx (RW)      → 로그 작성
  └─ logstash (RO)   → 로그 수집
```

---

## 11.8 실습 예제

### 11.8.1 실습 1: WordPress + MySQL

#### 목표
- 데이터베이스와 WordPress 파일을 볼륨에 저장
- 컨테이너 재생성 후에도 데이터 유지

```bash
# 1. 네트워크 생성
docker network create wordpress-net

# 2. 볼륨 생성
docker volume create mysql-data
docker volume create wordpress-data

# 3. MySQL 실행
docker run -d \
  --name mysql \
  --network wordpress-net \
  -v mysql-data:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=wordpress \
  -e MYSQL_USER=wpuser \
  -e MYSQL_PASSWORD=wppassword \
  mysql:8.0

# 4. WordPress 실행
docker run -d \
  --name wordpress \
  --network wordpress-net \
  -v wordpress-data:/var/www/html \
  -p 8080:80 \
  -e WORDPRESS_DB_HOST=mysql \
  -e WORDPRESS_DB_USER=wpuser \
  -e WORDPRESS_DB_PASSWORD=wppassword \
  -e WORDPRESS_DB_NAME=wordpress \
  wordpress:latest

# 5. 브라우저에서 설정
# http://localhost:8080

# 6. 데이터 영속성 테스트
docker stop wordpress mysql
docker rm wordpress mysql

# 7. 재생성 (같은 볼륨 사용)
docker run -d \
  --name mysql \
  --network wordpress-net \
  -v mysql-data:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  mysql:8.0

docker run -d \
  --name wordpress \
  --network wordpress-net \
  -v wordpress-data:/var/www/html \
  -p 8080:80 \
  -e WORDPRESS_DB_HOST=mysql \
  -e WORDPRESS_DB_USER=wpuser \
  -e WORDPRESS_DB_PASSWORD=wppassword \
  -e WORDPRESS_DB_NAME=wordpress \
  wordpress:latest

# 8. 확인
# http://localhost:8080
# ✅ 이전 데이터가 그대로 유지됨!
```

---

### 11.8.2 실습 2: 개발 환경 (바인드 마운트 + 볼륨)

#### 목표
- 소스 코드는 호스트에서 편집 (바인드 마운트)
- node_modules는 컨테이너 볼륨에 저장

**프로젝트 구조:**

```
myapp/
├── src/
│   ├── index.js
│   └── routes/
├── package.json
├── package-lock.json
└── Dockerfile
```

**Dockerfile:**

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    volumes:
      # 소스 코드 (바인드 마운트, 핫 리로드)
      - ./src:/app/src

      # node_modules (명명된 볼륨, 속도 향상)
      - node_modules:/app/node_modules
    environment:
      - NODE_ENV=development
    command: npm run dev

volumes:
  node_modules:
```

**실행:**

```bash
# 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 소스 코드 편집
# src/index.js 파일 수정 → 자동으로 재시작 (nodemon)

# 의존성 추가 시
docker-compose exec app npm install express
# node_modules 볼륨에 저장됨
```

**장점:**

```
✅ 소스 코드 실시간 반영 (바인드 마운트)
✅ node_modules는 컨테이너 내부 (속도 빠름)
✅ 크로스 플랫폼 호환 (Windows, macOS, Linux)
```

---

### 11.8.3 실습 3: 다중 환경 백업 시스템

#### 목표
- 여러 볼륨 자동 백업
- 백업 스케줄링
- 오래된 백업 자동 삭제

**backup-service/Dockerfile:**

```dockerfile
FROM alpine:3.18

RUN apk add --no-cache dcron aws-cli

COPY backup.sh /usr/local/bin/
COPY crontab /etc/crontabs/root

RUN chmod +x /usr/local/bin/backup.sh

CMD ["crond", "-f", "-l", "2"]
```

**backup-service/backup.sh:**

```bash
#!/bin/sh
set -e

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="/backups"
S3_BUCKET="${S3_BUCKET:-my-docker-backups}"

# 백업할 볼륨 목록
VOLUMES="mysql-data wordpress-data redis-data"

for VOLUME in $VOLUMES; do
  echo "Backing up $VOLUME..."

  BACKUP_FILE="$BACKUP_DIR/${VOLUME}-${TIMESTAMP}.tar.gz"

  # 볼륨 백업
  docker run --rm \
    -v "$VOLUME":/data:ro \
    -v "$BACKUP_DIR":/backup \
    alpine \
    tar czf "/backup/$(basename $BACKUP_FILE)" -C /data .

  # S3에 업로드 (선택사항)
  if [ -n "$AWS_ACCESS_KEY_ID" ]; then
    aws s3 cp "$BACKUP_FILE" "s3://$S3_BUCKET/"
    echo "Uploaded to S3: $BACKUP_FILE"
  fi

  echo "Backup completed: $BACKUP_FILE"
done

# 7일 이상 된 백업 삭제
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete
echo "Old backups cleaned up"
```

**backup-service/crontab:**

```
# 매일 새벽 2시에 백업
0 2 * * * /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  # 백업 서비스
  backup:
    build: ./backup-service
    volumes:
      # 백업할 볼륨들 (읽기 전용)
      - mysql-data:/volumes/mysql-data:ro
      - wordpress-data:/volumes/wordpress-data:ro
      - redis-data:/volumes/redis-data:ro

      # 백업 저장소
      - ./backups:/backups

      # Docker 소켓 (볼륨 관리용)
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - S3_BUCKET=my-docker-backups
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=us-east-1

  # 애플리케이션들
  mysql:
    image: mysql:8.0
    volumes:
      - mysql-data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: secret

  wordpress:
    image: wordpress:latest
    volumes:
      - wordpress-data:/var/www/html
    depends_on:
      - mysql

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data

volumes:
  mysql-data:
  wordpress-data:
  redis-data:
```

**실행:**

```bash
# 서비스 시작
docker-compose up -d

# 백업 즉시 실행
docker-compose exec backup /usr/local/bin/backup.sh

# 백업 로그 확인
docker-compose exec backup cat /var/log/backup.log

# 백업 파일 확인
ls -lh backups/
# -rw-r--r-- 1 user user 125M Jan 15 02:00 mysql-data-20240115-020000.tar.gz
# -rw-r--r-- 1 user user  50M Jan 15 02:01 wordpress-data-20240115-020100.tar.gz
# -rw-r--r-- 1 user user  10M Jan 15 02:02 redis-data-20240115-020200.tar.gz
```

---

### 11.8.4 실습 4: NFS를 통한 다중 호스트 공유

#### 시나리오
- 호스트 A: 웹 서버 (파일 업로드)
- 호스트 B: 이미지 처리 서버
- 호스트 C: 백업 서버
- 모두 NFS를 통해 같은 스토리지 공유

**NFS 서버 (별도 서버 또는 호스트 A):**

```bash
# NFS 서버 설치
sudo apt-get update
sudo apt-get install -y nfs-kernel-server

# 공유 디렉토리 생성
sudo mkdir -p /mnt/docker-shared
sudo chown nobody:nogroup /mnt/docker-shared
sudo chmod 777 /mnt/docker-shared

# /etc/exports 설정
echo "/mnt/docker-shared 192.168.1.0/24(rw,sync,no_subtree_check,no_root_squash)" | sudo tee -a /etc/exports

# NFS 재시작
sudo exportfs -a
sudo systemctl restart nfs-kernel-server
```

**호스트 A (웹 서버):**

```bash
# NFS 볼륨 생성
docker volume create \
  --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.100,rw,nfsvers=4 \
  --opt device=:/mnt/docker-shared \
  shared-storage

# 웹 서버 실행
docker run -d \
  --name webapp \
  -p 80:80 \
  -v shared-storage:/app/uploads \
  mywebapp:latest
```

**호스트 B (이미지 처리):**

```bash
# 같은 NFS 볼륨 생성
docker volume create \
  --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.100,rw,nfsvers=4 \
  --opt device=:/mnt/docker-shared \
  shared-storage

# 이미지 처리 서버 실행
docker run -d \
  --name processor \
  -v shared-storage:/data \
  image-processor:latest
```

**호스트 C (백업):**

```bash
# 같은 NFS 볼륨 (읽기 전용)
docker volume create \
  --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.100,ro,nfsvers=4 \
  --opt device=:/mnt/docker-shared \
  shared-storage

# 백업 서비스 실행
docker run -d \
  --name backup \
  -v shared-storage:/source:ro \
  -v /backup:/destination \
  backup-service:latest
```

**테스트:**

```bash
# 호스트 A: 파일 업로드
curl -F "file=@image.jpg" http://host-a/upload

# 호스트 B: 자동으로 처리됨
docker logs processor
# Processing image.jpg...
# Thumbnail created: image_thumb.jpg

# 호스트 C: 백업 확인
ls -la /backup/mnt/docker-shared/
# -rw-r--r-- 1 nobody nogroup 1.2M Jan 15 10:30 image.jpg
# -rw-r--r-- 1 nobody nogroup  50K Jan 15 10:31 image_thumb.jpg
```

---

## 11.9 문제 해결

### 11.9.1 권한 문제

**증상:**

```bash
docker run --rm -v mydata:/data alpine touch /data/test.txt
# touch: /data/test.txt: Permission denied
```

**해결:**

```bash
# 방법 1: 컨테이너 내부에서 소유권 변경
docker run --rm -v mydata:/data alpine chown -R 1000:1000 /data

# 방법 2: 특정 사용자로 실행
docker run --rm --user 1000:1000 -v mydata:/data alpine touch /data/test.txt

# 방법 3: 호스트에서 직접 변경 (local 드라이버)
sudo chown -R 1000:1000 /var/lib/docker/volumes/mydata/_data
```

---

### 11.9.2 볼륨이 비어있음

**증상:**

```bash
docker volume create mydata
docker run -d --name app -v mydata:/app/data myapp
docker exec app ls /app/data
# (아무것도 없음)
```

**원인:**
- Dockerfile에 `/app/data`에 파일이 있었지만 볼륨 마운트로 덮어씌워짐

**해결:**

```bash
# 방법 1: 초기 데이터가 있는 볼륨 생성
docker run --rm -v mydata:/data myapp sh -c "cp -r /app/data/. /data/"

# 방법 2: 엔트리포인트에서 초기화
# Dockerfile
COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]

# docker-entrypoint.sh
#!/bin/sh
if [ -z "$(ls -A /app/data)" ]; then
  echo "Initializing data directory..."
  cp -r /default-data/. /app/data/
fi
exec "$@"
```

---

### 11.9.3 디스크 공간 부족

**증상:**

```bash
docker run -d myapp
# Error: no space left on device
```

**진단:**

```bash
# Docker 디스크 사용량 확인
docker system df

# 출력:
# TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
# Images          15        5         10.5GB    5.2GB (49%)
# Containers      20        3         500MB     450MB (90%)
# Local Volumes   50        10        25GB      15GB (60%)
# Build Cache     100       0         5GB       5GB (100%)

# 볼륨 상세
docker system df -v
```

**해결:**

```bash
# 사용하지 않는 볼륨 삭제
docker volume prune -f

# 특정 볼륨만 삭제
docker volume rm old-volume-1 old-volume-2

# 전체 정리 (주의!)
docker system prune -a --volumes
```

---

### 11.9.4 NFS 마운트 실패

**증상:**

```bash
docker run -v nfs-volume:/data alpine ls /data
# ls: /data: Input/output error
```

**진단:**

```bash
# NFS 서버 연결 테스트
ping 192.168.1.100

# NFS 마운트 테스트 (호스트에서)
sudo mount -t nfs 192.168.1.100:/mnt/shared /tmp/test
ls /tmp/test
sudo umount /tmp/test

# Docker 로그 확인
docker volume inspect nfs-volume
journalctl -u docker
```

**해결:**

```bash
# 1. 방화벽 확인
sudo ufw allow from 192.168.1.0/24 to any port nfs

# 2. NFS 서버 설정 확인
showmount -e 192.168.1.100

# 3. 볼륨 재생성
docker volume rm nfs-volume
docker volume create \
  --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.100,rw,nfsvers=4,soft,timeo=30 \
  --opt device=:/mnt/shared \
  nfs-volume
```

---

## 11.10 베스트 프랙티스

### ✅ 체크리스트

- [ ] **명명된 볼륨 사용**: 익명 볼륨 대신 의미 있는 이름
- [ ] **볼륨 백업**: 정기적인 자동 백업 설정
- [ ] **레이블 지정**: 프로젝트, 환경, 용도 등으로 분류
- [ ] **읽기 전용 마운트**: 변경 불필요한 데이터는 `:ro`
- [ ] **볼륨 정리**: `docker volume prune` 정기 실행
- [ ] **개발/프로덕션 분리**: 바인드 마운트(개발), 볼륨(프로덕션)
- [ ] **권한 관리**: 컨테이너 사용자와 볼륨 권한 일치
- [ ] **모니터링**: 볼륨 크기 및 사용량 추적
- [ ] **문서화**: 볼륨 용도 및 백업 절차 기록

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: "데이터가 왜 자꾸 사라지나요?"

**상황**: 신입 개발자가 PostgreSQL 컨테이너로 개발 중 매일 데이터를 다시 입력하고 있음

```bash
# ❌ 주니어 개발자가 작성한 명령어
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=mysecret \
  postgres:15-alpine

# 다음날 컨테이너 재시작 후
docker exec postgres psql -U postgres -c "SELECT * FROM users;"
# ERROR: relation "users" does not exist
# 😱 어제 만든 테이블이 사라졌어요!
```

**문제점**:
- 볼륨을 마운트하지 않아 데이터가 컨테이너 내부에만 저장됨
- `docker rm` 또는 컨테이너 재생성 시 모든 데이터 손실
- 매일 더미 데이터를 다시 입력하는 시간 낭비

**해결책**:
```bash
# ✅ 올바른 코드
# 1. 볼륨 생성
docker volume create postgres-data

# 2. 볼륨을 마운트하여 컨테이너 실행
docker run -d --name postgres \
  -v postgres-data:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=mysecret \
  postgres:15-alpine

# 3. 데이터 추가
docker exec postgres psql -U postgres \
  -c "CREATE TABLE users (id SERIAL, name TEXT);" \
  -c "INSERT INTO users (name) VALUES ('Alice'), ('Bob');"

# 4. 컨테이너 재생성해도 데이터 유지됨!
docker rm -f postgres
docker run -d --name postgres \
  -v postgres-data:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=mysecret \
  postgres:15-alpine

# 5. 데이터 확인
docker exec postgres psql -U postgres -c "SELECT * FROM users;"
#  id | name
# ----+-------
#   1 | Alice
#   2 | Bob
# ✅ 데이터가 그대로 유지됨!
```

**배운 점**:
- 💡 데이터베이스는 반드시 볼륨을 사용해야 함
- 💡 명명된 볼륨 사용으로 관리 용이
- 💡 컨테이너 삭제 ≠ 볼륨 삭제 (별도 관리)

---

### 시나리오 2: "node_modules가 너무 느려요!"

**상황**: Windows에서 바인드 마운트로 개발 중 `npm install`이 10분 이상 걸림

```bash
# ❌ 주니어 개발자의 docker-compose.yml
version: '3.8'
services:
  app:
    image: node:18-alpine
    volumes:
      - .:/app  # 전체 프로젝트를 바인드 마운트
    working_dir: /app
    command: sh -c "npm install && npm run dev"
    ports:
      - "3000:3000"

# 실행 결과
# npm install... (10분 대기) ⏰
# 매번 의존성 설치가 너무 느림!
```

**문제점**:
- Windows/macOS에서 바인드 마운트는 성능이 느림 (파일 시스템 변환 오버헤드)
- `node_modules`도 바인드 마운트되어 호스트 파일 시스템 사용
- 수천 개의 작은 파일로 인한 I/O 병목

**해결책**:
```yaml
# ✅ 올바른 코드
version: '3.8'
services:
  app:
    image: node:18-alpine
    volumes:
      # 소스 코드만 바인드 마운트 (개발 중 실시간 반영)
      - ./src:/app/src
      - ./package.json:/app/package.json
      - ./package-lock.json:/app/package-lock.json

      # node_modules는 볼륨 사용 (빠른 I/O)
      - node_modules:/app/node_modules
    working_dir: /app
    command: sh -c "npm install && npm run dev"
    ports:
      - "3000:3000"

volumes:
  node_modules:  # 명명된 볼륨
```

**성능 비교**:
```bash
# Before (전체 바인드 마운트)
npm install: 10분 30초 ❌
npm run build: 3분 20초 ❌

# After (node_modules 볼륨 분리)
npm install: 1분 20초 ✅ (87% 개선)
npm run build: 45초 ✅ (77% 개선)
```

**배운 점**:
- 💡 바인드 마운트는 소스 코드에만 사용
- 💡 의존성 디렉토리는 볼륨으로 분리
- 💡 볼륨 성능 >> 바인드 마운트 성능 (Windows/macOS)

---

### 시나리오 3: "볼륨을 삭제했는데도 용량이 안 줄어요!"

**상황**: 디스크 공간 확보를 위해 볼륨을 삭제했지만 여전히 용량 부족

```bash
# ❌ 주니어 개발자의 시도
# 1. 컨테이너 삭제
docker rm -f $(docker ps -aq)

# 2. 이미지 삭제
docker rmi $(docker images -q)

# 3. 디스크 확인
docker system df
# TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
# Images          0         0         0B        0B
# Containers      0         0         0B        0B
# Local Volumes   50        0         25GB      25GB (100%)  ← 여전히 25GB!
# Build Cache     0         0         0B        0B

# 볼륨을 삭제하려고 시도
docker volume rm mydata
# Error: volume is in use - [abc123]
# 😱 컨테이너를 다 지웠는데도 삭제가 안 돼요!
```

**문제점**:
- 중지된 컨테이너가 여전히 볼륨을 참조하고 있음
- `docker ps`는 실행 중인 컨테이너만 표시 (`-a` 옵션 필요)
- 익명 볼륨들이 계속 쌓이고 있음

**해결책**:
```bash
# ✅ 올바른 정리 방법

# 1. 모든 컨테이너 확인 (중지된 것 포함)
docker ps -a
# CONTAINER ID   IMAGE     STATUS                      PORTS
# abc123def456   postgres  Exited (0) 2 hours ago
# def456ghi789   mysql     Exited (137) 1 day ago

# 2. 모든 컨테이너 삭제
docker rm -f $(docker ps -aq)

# 3. 사용하지 않는 볼륨만 삭제
docker volume prune -f
# Deleted Volumes:
# abc123def456789...
# def456ghi789abc...
# Total reclaimed space: 20GB  ✅

# 또는 특정 볼륨 삭제
docker volume rm mydata old-volume test-data

# 4. 전체 시스템 정리 (주의!)
docker system prune -a --volumes -f
# WARNING! This will remove:
#   - all stopped containers
#   - all networks not used by at least one container
#   - all images without at least one container associated to them
#   - all volumes not used by at least one container
# Total reclaimed space: 25GB  ✅
```

**정리 스크립트 자동화**:
```bash
#!/bin/bash
# cleanup-docker.sh

echo "🧹 Docker 정리 시작..."

# 중지된 컨테이너 삭제
echo "1. 중지된 컨테이너 삭제 중..."
docker container prune -f

# 사용하지 않는 이미지 삭제
echo "2. 미사용 이미지 삭제 중..."
docker image prune -a -f

# 사용하지 않는 볼륨 삭제
echo "3. 미사용 볼륨 삭제 중..."
docker volume prune -f

# 사용하지 않는 네트워크 삭제
echo "4. 미사용 네트워크 삭제 중..."
docker network prune -f

# 빌드 캐시 삭제
echo "5. 빌드 캐시 삭제 중..."
docker builder prune -a -f

# 결과 확인
echo "✅ 정리 완료!"
docker system df
```

**배운 점**:
- 💡 `docker ps -a`로 중지된 컨테이너도 확인
- 💡 정기적인 `docker volume prune` 실행
- 💡 정리 스크립트 작성으로 자동화

---

### 시나리오 4: "프로덕션 서버 마이그레이션 중 데이터 손실!"

**상황**: 기존 서버에서 새 서버로 이전 중 데이터베이스 데이터 손실

```bash
# ❌ 주니어 개발자의 마이그레이션 시도
# [기존 서버 A]
docker ps
# CONTAINER ID   IMAGE      PORTS
# abc123         postgres   5432->5432

# [신규 서버 B에서]
docker pull postgres:15-alpine
docker run -d --name postgres -p 5432:5432 postgres:15-alpine
# 😱 깨끗한 데이터베이스가 실행됨! (기존 데이터 없음)

# 뒤늦게 백업 시도
# [서버 A에서]
docker exec postgres pg_dump -U postgres mydb > backup.sql
# 하지만 이미 서버 A는 종료됨... ❌
```

**문제점**:
- 마이그레이션 전 백업을 하지 않음
- 볼륨 데이터를 새 서버로 전송하지 않음
- 롤백 계획 없음

**해결책**:
```bash
# ✅ 올바른 마이그레이션 절차

# ========== [서버 A에서] ==========
# 1단계: 볼륨 백업
docker run --rm \
  -v postgres-data:/data:ro \
  -v $(pwd):/backup \
  alpine \
  tar czf /backup/postgres-backup-$(date +%Y%m%d).tar.gz -C /data .

# 백업 파일 확인
ls -lh postgres-backup-*.tar.gz
# -rw-r--r-- 1 user user 250M Jan 15 10:30 postgres-backup-20240115.tar.gz

# 2단계: 백업 파일을 서버 B로 전송
scp postgres-backup-20240115.tar.gz user@server-b:/tmp/

# ========== [서버 B에서] ==========
# 3단계: 새 볼륨 생성
docker volume create postgres-data

# 4단계: 백업 복원
docker run --rm \
  -v postgres-data:/data \
  -v /tmp:/backup \
  alpine \
  tar xzf /backup/postgres-backup-20240115.tar.gz -C /data

# 5단계: 컨테이너 실행 (복원된 볼륨 사용)
docker run -d \
  --name postgres \
  -v postgres-data:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=mysecret \
  -p 5432:5432 \
  postgres:15-alpine

# 6단계: 데이터 검증
docker exec postgres psql -U postgres -c "\dt"
# List of relations
#  Schema |   Name   | Type  |  Owner
# --------+----------+-------+----------
#  public | users    | table | postgres
#  public | orders   | table | postgres
# ✅ 모든 테이블이 정상적으로 복원됨!

# 7단계: 애플리케이션 연결 테스트
curl http://server-b:8080/api/health
# {"status":"ok","database":"connected"}
# ✅ 성공!
```

**무중단 마이그레이션 (고급)**:
```bash
# 1. 서버 B에서 복제본 실행 (읽기 전용)
# 2. 데이터 실시간 동기화 (pg_logical 등)
# 3. DNS 전환으로 트래픽 이동
# 4. 서버 A 모니터링 후 종료
```

**배운 점**:
- 💡 마이그레이션 전 반드시 백업
- 💡 백업 파일 검증 (복원 테스트)
- 💡 롤백 계획 수립 (문제 발생 시 복구)
- 💡 프로덕션은 무중단 마이그레이션 고려

---

## ❓ FAQ

<details>
<summary><strong>Q1: Docker 볼륨과 바인드 마운트 중 어떤 것을 사용해야 하나요?</strong></summary>

**A**: 용도에 따라 다릅니다.

**상세 설명**:
- **Docker 볼륨 사용 시기**:
  - 프로덕션 환경의 데이터베이스
  - 백업/복원이 필요한 데이터
  - 컨테이너 간 데이터 공유
  - 크로스 플랫폼 호환성 필요

- **바인드 마운트 사용 시기**:
  - 개발 환경의 소스 코드 (핫 리로드)
  - 설정 파일 (nginx.conf 등)
  - 로그 파일 (호스트에서 직접 확인)
  - 호스트 도구로 직접 수정 필요

**예시**:
```yaml
# docker-compose.yml
services:
  app:
    image: myapp
    volumes:
      # 개발: 바인드 마운트
      - ./src:/app/src
      - ./config:/app/config:ro

      # 프로덕션: 볼륨
      - app-data:/app/data
      - logs:/var/log

volumes:
  app-data:
  logs:
```

**실무 팁**:
💡 개발은 바인드 마운트, 프로덕션은 볼륨 사용!

</details>

<details>
<summary><strong>Q2: 볼륨을 삭제하면 데이터도 완전히 삭제되나요?</strong></summary>

**A**: 네, 볼륨 삭제 시 데이터는 영구적으로 삭제됩니다.

**상세 설명**:
- `docker volume rm` 실행 시 볼륨의 모든 데이터 삭제
- 복구 불가능 (휴지통 개념 없음)
- 사용 중인 볼륨은 삭제되지 않음 (안전장치)

**안전한 삭제 절차**:
```bash
# 1. 백업 먼저
docker run --rm \
  -v mydata:/data:ro \
  -v $(pwd):/backup \
  alpine \
  tar czf /backup/mydata-final.tar.gz -C /data .

# 2. 백업 검증
tar tzf mydata-final.tar.gz | head

# 3. 볼륨 삭제
docker volume rm mydata

# 4. 필요 시 복원
docker volume create mydata-restored
docker run --rm \
  -v mydata-restored:/data \
  -v $(pwd):/backup \
  alpine \
  tar xzf /backup/mydata-final.tar.gz -C /data
```

**실무 팁**:
💡 중요 볼륨은 삭제 전 반드시 백업! 자동 백업 스크립트 사용 권장.

</details>

<details>
<summary><strong>Q3: Windows에서 볼륨 파일을 직접 확인할 수 있나요?</strong></summary>

**A**: Docker Desktop 사용 시 직접 접근이 어렵지만, 컨테이너를 통해 확인 가능합니다.

**상세 설명**:
- **Linux**: `/var/lib/docker/volumes/` 직접 접근 가능
- **macOS/Windows**: Docker VM 내부에 저장되어 직접 접근 어려움
- 해결책: 임시 컨테이너로 볼륨 마운트하여 확인

**Windows/macOS에서 볼륨 확인 방법**:
```bash
# 방법 1: 임시 컨테이너로 파일 확인
docker run --rm -it \
  -v mydata:/data \
  alpine \
  sh

# 컨테이너 내부에서
ls -la /data
cat /data/config.json

# 방법 2: 파일 복사
docker run --rm \
  -v mydata:/data \
  -v $(pwd):/host \
  alpine \
  cp -r /data/. /host/volume-backup/

# 호스트에서 확인
ls -la volume-backup/

# 방법 3: Docker Desktop GUI 사용
# Docker Desktop > Volumes > [볼륨 선택] > Data 탭
```

**실무 팁**:
💡 개발 중 디버깅은 바인드 마운트가 더 편리함.

</details>

<details>
<summary><strong>Q4: 볼륨이 너무 많이 쌓여서 정리하고 싶어요. 안전한 방법은?</strong></summary>

**A**: `docker volume prune`으로 미사용 볼륨만 안전하게 삭제 가능합니다.

**상세 설명**:
- `docker volume prune`: 컨테이너에 연결되지 않은 볼륨만 삭제
- 실행 중이거나 중지된 컨테이너가 사용하는 볼륨은 보호됨
- 확인 메시지 제공 (`-f`로 건너뛰기 가능)

**단계별 정리 방법**:
```bash
# 1. 현재 볼륨 사용량 확인
docker system df -v
# Volumes space usage:
# VOLUME NAME               SIZE
# postgres-data             250MB
# redis-data                10MB
# abc123def456 (anonymous)  5GB     ← 미사용 익명 볼륨
# old-project-data          2GB     ← 미사용 볼륨

# 2. 미사용 볼륨 확인
docker volume ls --filter dangling=true
# DRIVER    VOLUME NAME
# local     abc123def456
# local     old-project-data

# 3. 안전하게 삭제 (확인 후)
docker volume prune
# WARNING! This will remove all local volumes not used by at least one container.
# Are you sure you want to continue? [y/N] y
# Deleted Volumes:
# abc123def456
# old-project-data
# Total reclaimed space: 7GB

# 4. 특정 볼륨만 삭제
docker volume rm old-project-data test-volume
```

**자동 정리 스크립트**:
```bash
# 매주 일요일 새벽 3시에 실행
# crontab -e
0 3 * * 0 docker volume prune -f >> /var/log/docker-cleanup.log
```

**실무 팁**:
💡 프로덕션 환경에서는 수동 확인 후 삭제 권장 (`-f` 사용 금지).

</details>

<details>
<summary><strong>Q5: 여러 컨테이너가 같은 볼륨을 동시에 쓸 때 문제가 없나요?</strong></summary>

**A**: 파일 시스템 수준에서는 가능하지만, 애플리케이션 레벨에서 동기화 문제가 발생할 수 있습니다.

**상세 설명**:
- **파일 시스템**: 여러 컨테이너가 동시 접근 가능
- **데이터베이스**: 동시 쓰기 시 데이터 손상 위험 ⚠️
- **로그 파일**: 일반적으로 안전 (append-only)
- **정적 파일**: 읽기 전용이면 안전 ✅

**안전한 사용 예시**:
```yaml
# ✅ 안전: 읽기 전용 공유
services:
  nginx:
    image: nginx
    volumes:
      - static-files:/usr/share/nginx/html:ro  # 읽기 전용

  app:
    image: myapp
    volumes:
      - static-files:/app/static  # 쓰기 가능 (빌드 시)

volumes:
  static-files:
```

**위험한 사용 예시**:
```yaml
# ❌ 위험: 여러 DB가 같은 볼륨 쓰기
services:
  mysql1:
    image: mysql
    volumes:
      - db-data:/var/lib/mysql  # 동시 쓰기 위험!

  mysql2:
    image: mysql
    volumes:
      - db-data:/var/lib/mysql  # 데이터 손상 가능!
```

**올바른 패턴**:
```yaml
# ✅ 올바름: 각각 별도 볼륨
services:
  mysql-master:
    image: mysql
    volumes:
      - mysql-master-data:/var/lib/mysql

  mysql-replica:
    image: mysql
    volumes:
      - mysql-replica-data:/var/lib/mysql

volumes:
  mysql-master-data:
  mysql-replica-data:
```

**실무 팁**:
💡 데이터베이스는 절대 볼륨 공유 금지! 로그/정적 파일만 공유.

</details>

<details>
<summary><strong>Q6: 볼륨 백업을 자동화할 수 있나요?</strong></summary>

**A**: 네, cron과 스크립트를 사용하여 자동 백업 가능합니다.

**상세 설명**:
- cron으로 정기 실행
- 백업 파일을 S3/NFS 등으로 전송
- 오래된 백업 자동 삭제
- 백업 성공/실패 알림

**자동 백업 스크립트**:
```bash
#!/bin/bash
# /usr/local/bin/backup-docker-volumes.sh

set -e

BACKUP_DIR="/mnt/backups/docker-volumes"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
RETENTION_DAYS=7

# 백업할 볼륨 목록
VOLUMES="postgres-data redis-data app-data"

mkdir -p "$BACKUP_DIR"

for VOLUME in $VOLUMES; do
  echo "Backing up $VOLUME..."

  BACKUP_FILE="$BACKUP_DIR/${VOLUME}-${TIMESTAMP}.tar.gz"

  docker run --rm \
    -v "$VOLUME":/data:ro \
    -v "$BACKUP_DIR":/backup \
    alpine \
    tar czf "/backup/$(basename $BACKUP_FILE)" -C /data .

  # S3 업로드 (선택사항)
  if [ -n "$AWS_S3_BUCKET" ]; then
    aws s3 cp "$BACKUP_FILE" "s3://$AWS_S3_BUCKET/docker-volumes/"
    echo "Uploaded to S3: $BACKUP_FILE"
  fi

  echo "✅ Backup completed: $BACKUP_FILE"
done

# 오래된 백업 삭제
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
echo "🧹 Old backups cleaned (>$RETENTION_DAYS days)"

# Slack 알림 (선택사항)
if [ -n "$SLACK_WEBHOOK" ]; then
  curl -X POST "$SLACK_WEBHOOK" \
    -H 'Content-Type: application/json' \
    -d "{\"text\":\"✅ Docker 볼륨 백업 완료: $TIMESTAMP\"}"
fi
```

**cron 설정**:
```bash
# 매일 새벽 2시 백업
sudo crontab -e
0 2 * * * /usr/local/bin/backup-docker-volumes.sh >> /var/log/docker-backup.log 2>&1
```

**Docker Compose로 백업 서비스 구성**:
```yaml
version: '3.8'
services:
  backup:
    image: alpine:3.18
    volumes:
      - postgres-data:/volumes/postgres:ro
      - redis-data:/volumes/redis:ro
      - /mnt/backups:/backups
      - ./backup.sh:/backup.sh:ro
    environment:
      - AWS_S3_BUCKET=my-backups
      - SLACK_WEBHOOK=${SLACK_WEBHOOK}
    command: crond -f -l 2
    restart: unless-stopped

volumes:
  postgres-data:
  redis-data:
```

**실무 팁**:
💡 백업 파일도 정기적으로 복원 테스트 필수!

</details>

<details>
<summary><strong>Q7: tmpfs 마운트는 언제 사용하나요?</strong></summary>

**A**: 민감한 데이터나 임시 캐시 등 영속성이 필요 없는 데이터에 사용합니다.

**상세 설명**:
- **장점**:
  - 메모리에 저장되어 매우 빠름
  - 컨테이너 종료 시 자동 삭제 (보안)
  - 디스크 I/O 없음

- **단점**:
  - 영속성 없음 (재시작 시 삭제)
  - 메모리 사용량 증가
  - Linux만 지원 (Windows/macOS 불가)

**사용 사례**:
```bash
# 1. 비밀번호/토큰 임시 저장
docker run -d \
  --name secure-app \
  --tmpfs /run/secrets:rw,size=10m,mode=0700 \
  myapp

# 2. 세션 데이터
docker run -d \
  --name webapp \
  --tmpfs /tmp/sessions:rw,size=100m \
  webapp

# 3. 임시 파일 처리
docker run -d \
  --name worker \
  --tmpfs /tmp/processing:rw,size=500m \
  worker

# 4. 캐시 (Redis 등)
docker run -d \
  --name redis \
  --tmpfs /data:rw,size=1g \
  redis
```

**Docker Compose 예시**:
```yaml
services:
  app:
    image: myapp
    tmpfs:
      - /tmp:size=100m,mode=1777
      - /run/secrets:size=10m,mode=0700
```

**성능 비교**:
```bash
# 벤치마크: 10000번 쓰기
# 볼륨 (디스크):    5.2초
# tmpfs (메모리):   0.3초  ← 17배 빠름!
```

**실무 팁**:
💡 보안이 중요한 임시 데이터는 tmpfs 사용! (API 키, 임시 비밀번호 등)

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. Docker 볼륨이 무엇이고 왜 필요한가요?</strong></summary>

**모범 답안 포인트**
- Docker 볼륨은 컨테이너의 데이터를 영속적으로 저장하는 메커니즘
- 컨테이너는 삭제되면 내부 데이터도 함께 사라지는 문제 해결
- Docker가 관리하는 스토리지로 데이터 백업/공유 용이

**예시 답변**
> "Docker 볼륨은 컨테이너의 데이터를 영속적으로 저장하기 위한 기능입니다. 컨테이너는 기본적으로 삭제되면 내부 데이터도 함께 사라지는데, 볼륨을 사용하면 컨테이너와 독립적으로 데이터를 유지할 수 있습니다. 예를 들어, 데이터베이스 컨테이너를 업데이트할 때 볼륨을 사용하지 않으면 모든 데이터가 손실되지만, 볼륨을 사용하면 데이터를 안전하게 보존할 수 있습니다."

**꼬리 질문**
- Q: 볼륨 없이 컨테이너를 재시작하면 데이터가 유지되나요?
- A: 재시작(`docker restart`)은 데이터가 유지되지만, 재생성(`docker rm` 후 `docker run`)은 데이터가 손실됩니다.

**실무 연관**
- 모든 프로덕션 데이터베이스는 반드시 볼륨 사용
- 개발 환경에서도 매일 데이터 재입력 방지 위해 볼륨 필수

</details>

<details>
<summary><strong>2. Docker 볼륨과 바인드 마운트의 차이점은 무엇인가요?</strong></summary>

**모범 답안 포인트**
- 볼륨: Docker가 관리하는 스토리지 (`/var/lib/docker/volumes/`)
- 바인드 마운트: 호스트의 특정 경로를 직접 마운트
- 볼륨은 프로덕션, 바인드 마운트는 개발 환경에 적합

**예시 답변**
> "Docker 볼륨은 Docker가 관리하는 저장소로, 호스트의 정확한 경로를 몰라도 사용할 수 있고 크로스 플랫폼 호환성이 좋습니다. 반면 바인드 마운트는 호스트의 특정 디렉토리를 컨테이너에 직접 연결하는 방식으로, 개발 중 소스 코드를 실시간으로 반영할 때 유용합니다. 프로덕션 환경에서는 데이터 백업과 마이그레이션이 쉬운 볼륨을 주로 사용하고, 개발 환경에서는 코드 편집을 위해 바인드 마운트를 사용합니다."

**꼬리 질문**
- Q: 바인드 마운트의 단점은 무엇인가요?
- A: Windows/macOS에서 성능이 느리고, 호스트 경로에 의존적이며, 권한 문제가 발생할 수 있습니다.

**실무 연관**
- 개발: `./src:/app/src` (바인드 마운트)
- 프로덕션: `app-data:/app/data` (볼륨)

</details>

<details>
<summary><strong>3. 볼륨을 백업하는 방법을 설명해주세요.</strong></summary>

**모범 답안 포인트**
- 임시 컨테이너로 볼륨을 마운트하여 tar 아카이브 생성
- 백업 파일을 호스트 또는 S3 등에 저장
- 복원 시 새 볼륨 생성 후 아카이브 압축 해제

**예시 답변**
> "Docker 볼륨 백업은 임시 컨테이너를 사용합니다. 먼저 백업할 볼륨을 읽기 전용으로 마운트하고, 호스트 디렉토리도 함께 마운트한 후, tar 명령어로 압축 파일을 생성합니다. 예를 들어 `docker run --rm -v mydata:/data:ro -v $(pwd):/backup alpine tar czf /backup/mydata.tar.gz -C /data .` 같은 명령어를 사용합니다. 복원할 때는 새 볼륨을 생성하고 같은 방법으로 압축을 해제합니다."

**꼬리 질문**
- Q: 운영 중인 데이터베이스 볼륨을 백업할 때 주의사항은?
- A: 데이터 일관성을 위해 데이터베이스를 먼저 중지하거나, `pg_dump` 같은 DB 전용 백업 도구를 사용해야 합니다.

**실무 연관**
- cron으로 매일 자동 백업 설정
- S3 같은 원격 저장소에 백업 파일 보관

</details>

<details>
<summary><strong>4. 익명 볼륨과 명명된 볼륨의 차이는 무엇인가요?</strong></summary>

**모범 답안 포인트**
- 익명 볼륨: Dockerfile `VOLUME` 명령이나 `-v /path`로 자동 생성, 랜덤 이름
- 명명된 볼륨: `-v name:/path`로 생성, 의미 있는 이름
- 명명된 볼륨이 관리하기 쉬워 권장됨

**예시 답변**
> "익명 볼륨은 `docker run -v /app/data myapp` 처럼 이름 없이 생성되는 볼륨으로, Docker가 `abc123def456` 같은 랜덤 이름을 부여합니다. 명명된 볼륨은 `docker run -v mydata:/app/data myapp` 처럼 명시적으로 이름을 지정하는 볼륨입니다. 익명 볼륨은 컨테이너 삭제 후 어떤 볼륨이 어떤 용도였는지 알기 어려워 고아 볼륨이 쌓이는 문제가 있습니다. 따라서 실무에서는 항상 명명된 볼륨을 사용하는 것이 권장됩니다."

**꼬리 질문**
- Q: 익명 볼륨은 어떻게 정리하나요?
- A: `docker volume prune` 명령어로 미사용 볼륨을 일괄 삭제할 수 있습니다.

**실무 연관**
- Dockerfile에 `VOLUME` 사용 시 익명 볼륨 생성 주의
- docker-compose.yml에서 명명된 볼륨 선언 권장

</details>

<details>
<summary><strong>5. 여러 컨테이너가 같은 볼륨을 공유할 수 있나요? 주의사항은?</strong></summary>

**모범 답안 포인트**
- 파일 시스템 수준에서는 여러 컨테이너 공유 가능
- 데이터베이스 같은 경우 동시 쓰기 시 데이터 손상 위험
- 읽기 전용(`:ro`) 마운트로 안전하게 공유 가능

**예시 답변**
> "네, 여러 컨테이너가 같은 볼륨을 공유할 수 있습니다. 예를 들어 Nginx와 PHP-FPM이 같은 웹 루트 디렉토리를 공유하는 경우가 일반적입니다. 하지만 데이터베이스처럼 파일 잠금이 필요한 애플리케이션은 동시에 여러 컨테이너가 쓰기 작업을 하면 데이터가 손상될 수 있습니다. 안전하게 공유하려면 한 컨테이너는 쓰기 권한을, 나머지는 읽기 전용(`:ro`)으로 마운트하는 것이 좋습니다."

**꼬리 질문**
- Q: Docker Compose에서 볼륨을 공유하려면 어떻게 하나요?
- A: `volumes:` 섹션에 볼륨을 선언하고, 각 서비스에서 같은 볼륨 이름을 사용하면 됩니다.

**실무 연관**
- Nginx(읽기) + PHP-FPM(쓰기) 구조
- 로그 수집 컨테이너(읽기 전용)

</details>

<details>
<summary><strong>6. tmpfs 마운트는 언제 사용하나요?</strong></summary>

**모범 답안 포인트**
- tmpfs는 메모리에 저장되는 임시 파일 시스템
- 컨테이너 재시작 시 데이터 자동 삭제
- 비밀번호, 세션, 캐시 등 민감하거나 임시 데이터에 사용

**예시 답변**
> "tmpfs 마운트는 메모리에 데이터를 저장하는 방식으로, 디스크 I/O가 없어 매우 빠르지만 컨테이너 종료 시 데이터가 사라집니다. 주로 API 키나 임시 비밀번호 같은 민감한 데이터를 저장할 때 사용하는데, 디스크에 기록되지 않아 보안이 강화됩니다. 또한 Redis 캐시처럼 영속성이 필요 없고 속도가 중요한 경우에도 활용됩니다. 단, Linux 환경에서만 지원되고 메모리를 사용하므로 크기 제한에 주의해야 합니다."

**꼬리 질문**
- Q: tmpfs와 볼륨의 성능 차이는 얼마나 되나요?
- A: tmpfs는 메모리 속도이므로 볼륨(디스크)보다 10배 이상 빠를 수 있습니다.

**실무 연관**
- 세션 저장소 (`/tmp/sessions`)
- 빌드 중간 파일 (`/tmp/build`)

</details>

<details>
<summary><strong>7. 볼륨 드라이버는 무엇이고 언제 사용하나요?</strong></summary>

**모범 답안 포인트**
- 볼륨 드라이버는 볼륨을 저장하는 백엔드 방식
- 기본은 local 드라이버 (호스트 디스크)
- NFS, AWS EBS 등 원격 스토리지 연결 가능

**예시 답변**
> "볼륨 드라이버는 볼륨 데이터를 어디에, 어떻게 저장할지 결정하는 플러그인입니다. 기본 드라이버인 'local'은 호스트의 로컬 디스크를 사용하지만, NFS 드라이버를 사용하면 네트워크 저장소에 데이터를 저장할 수 있습니다. 이렇게 하면 여러 Docker 호스트가 같은 볼륨을 공유할 수 있어 클러스터 환경에서 유용합니다. AWS 같은 클라우드 환경에서는 EBS 드라이버를 사용하여 영속적인 블록 스토리지를 볼륨으로 사용할 수도 있습니다."

**꼬리 질문**
- Q: NFS 볼륨의 단점은 무엇인가요?
- A: 네트워크 지연으로 인한 성능 저하와 네트워크 장애 시 데이터 접근 불가 문제가 있습니다.

**실무 연관**
- 단일 서버: local 드라이버
- 다중 서버: NFS 또는 클라우드 스토리지 드라이버

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. 프로덕션 환경에서 무중단으로 볼륨을 마이그레이션하는 방법은?</strong></summary>

**모범 답안 포인트**
- 데이터베이스 복제(replication) 설정
- 실시간 동기화 후 트래픽 전환
- 롤백 계획 수립 및 모니터링

**예시 답변**
> "프로덕션 환경에서 무중단 볼륨 마이그레이션은 데이터베이스 복제 기능을 활용합니다. 먼저 기존 서버(A)에서 새 서버(B)로 초기 데이터를 복사한 후, PostgreSQL의 경우 pg_logical이나 streaming replication으로 실시간 동기화를 설정합니다. 동기화가 완료되면 애플리케이션을 읽기 전용 모드로 전환하고, 최종 동기화 후 DNS나 로드 밸런서 설정을 변경하여 트래픽을 새 서버로 이동합니다. 이후 기존 서버를 모니터링하다가 문제가 없으면 종료하고, 문제 발생 시 즉시 롤백할 수 있도록 준비해야 합니다."

**실무 예시**:
```bash
# 1. 기존 서버 A: Master로 운영
# 2. 새 서버 B: Replica로 실시간 동기화
docker run -d --name postgres-replica \
  -v postgres-new:/var/lib/postgresql/data \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  postgres:15-alpine

# 3. 동기화 확인 후 B를 Master로 승격
# 4. DNS/로드밸런서를 B로 전환
# 5. A 모니터링 후 종료
```

**꼬리 질문**
- Q: 동기화 지연(lag)이 발생하면 어떻게 처리하나요?
- A: 읽기 전용 모드로 전환하여 쓰기를 중단하고 완전 동기화를 기다린 후 전환합니다.

**실무 연관**
- AWS RDS의 Read Replica 승격 방식과 유사
- Blue-Green 배포 패턴 적용

</details>

<details>
<summary><strong>2. 볼륨 성능 최적화 방법과 모니터링 전략은?</strong></summary>

**모범 답안 포인트**
- 볼륨 드라이버 선택 (local vs NFS vs cloud)
- I/O 성능 모니터링 (iostat, docker stats)
- SSD 사용, 파일 시스템 튜닝

**예시 답변**
> "볼륨 성능 최적화는 먼저 적절한 드라이버 선택부터 시작합니다. 로컬 환경에서는 local 드라이버가 가장 빠르고, 네트워크 스토리지가 필요한 경우 NFS보다 AWS EBS 같은 블록 스토리지가 일반적으로 성능이 좋습니다. 스토리지는 반드시 SSD를 사용하고, 데이터베이스 볼륨의 경우 `noatime` 마운트 옵션으로 불필요한 메타데이터 업데이트를 줄일 수 있습니다. 모니터링은 `docker stats`로 I/O 사용량을 확인하고, `iostat`로 디스크 병목을 파악하며, 프로메테우스와 그라파나로 장기 추세를 분석합니다."

**실무 예시**:
```bash
# 1. I/O 모니터링
docker stats --format "table {{.Container}}\t{{.BlockIO}}"

# 2. 볼륨 드라이버 최적화
docker volume create \
  --driver local \
  --opt type=tmpfs \  # 고성능이 필요한 경우
  --opt device=tmpfs \
  --opt o=size=1g,uid=1000 \
  fast-cache

# 3. 프로메테우스 메트릭 수집
node_filesystem_io_time_seconds_total
container_fs_reads_bytes_total
container_fs_writes_bytes_total
```

**꼬리 질문**
- Q: 볼륨 I/O가 병목인 것을 어떻게 확인하나요?
- A: `docker stats`에서 BlockIO가 높거나, `iostat`에서 util%가 지속적으로 100%에 가까우면 I/O 병목입니다.

**실무 연관**
- 데이터베이스 성능 튜닝
- 로그 파일 I/O 최적화

</details>

<details>
<summary><strong>3. Docker 볼륨의 백업 전략과 재해 복구 계획은 어떻게 수립하나요?</strong></summary>

**모범 답안 포인트**
- 3-2-1 백업 규칙: 3개 복사본, 2개 매체, 1개 오프사이트
- 정기 백업 자동화 (cron, CI/CD)
- 복원 테스트 및 RPO/RTO 정의

**예시 답변**
> "Docker 볼륨 백업 전략은 3-2-1 규칙을 따릅니다. 데이터를 최소 3개 복사본으로 유지하되, 2개는 서로 다른 매체(로컬 디스크, NAS)에, 1개는 오프사이트(S3, Azure Blob)에 저장합니다. 매일 자동 백업을 cron으로 실행하되, 증분 백업과 전체 백업을 조합하여 스토리지 비용을 최적화합니다. 중요한 것은 RPO(목표 복구 시점)와 RTO(목표 복구 시간)를 정의하는 것입니다. 예를 들어 RPO 1시간, RTO 30분이면, 1시간마다 백업하고 30분 내 복원 가능해야 합니다. 또한 최소 분기별로 백업 복원 테스트를 실시하여 실제 재해 상황에서 복구 가능함을 검증해야 합니다."

**실무 예시**:
```bash
# 백업 스크립트 (매일 실행)
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d-%H%M)
VOLUME="postgres-data"

# 1. 로컬 백업
docker run --rm \
  -v $VOLUME:/data:ro \
  -v /backup/local:/backup \
  alpine tar czf /backup/${VOLUME}-${TIMESTAMP}.tar.gz -C /data .

# 2. S3 업로드 (오프사이트)
aws s3 cp /backup/local/${VOLUME}-${TIMESTAMP}.tar.gz \
  s3://backups/docker-volumes/

# 3. 7일 이상 된 로컬 백업 삭제
find /backup/local -mtime +7 -delete

# 4. 복원 테스트 (주 1회)
if [ $(date +%u) -eq 7 ]; then
  docker volume create ${VOLUME}-test
  docker run --rm \
    -v ${VOLUME}-test:/data \
    -v /backup/local:/backup \
    alpine tar xzf /backup/${VOLUME}-${TIMESTAMP}.tar.gz -C /data
  # 검증 로직...
  docker volume rm ${VOLUME}-test
fi
```

**꼬리 질문**
- Q: 증분 백업과 전체 백업의 장단점은?
- A: 전체 백업은 복원이 빠르지만 스토리지 비용이 높고, 증분 백업은 비용이 적지만 복원이 복잡합니다.

**실무 연관**
- 금융권: RPO/RTO 엄격 (분 단위)
- 일반 서비스: RPO 1시간, RTO 4시간

</details>

<details>
<summary><strong>4. 대용량 볼륨 데이터를 효율적으로 전송하는 방법은?</strong></summary>

**모범 답안 포인트**
- 압축 + 스트리밍 조합
- rsync를 통한 증분 전송
- 네트워크 대역폭 최적화

**예시 답변**
> "대용량 볼륨 데이터는 압축과 스트리밍을 조합하여 전송합니다. 예를 들어 100GB 데이터베이스 볼륨을 전송할 때, tar로 압축하면서 동시에 SSH 파이프로 전송하면 중간 파일 없이 빠르게 처리할 수 있습니다. 초기 전송 후에는 rsync를 사용하여 변경된 부분만 증분 전송하면 시간을 크게 단축할 수 있습니다. 네트워크 대역폭이 충분하다면 병렬 전송 도구(parallel, pigz)를 사용하거나, AWS Snowball 같은 물리적 데이터 전송 서비스를 고려할 수도 있습니다."

**실무 예시**:
```bash
# 방법 1: 압축 + SSH 스트리밍
docker run --rm \
  -v mydata:/data \
  alpine tar czf - -C /data . \
  | ssh user@target-server \
  "docker run --rm -i -v mydata:/data alpine tar xzf - -C /data"

# 방법 2: rsync 증분 전송
# 초기 전송
docker run --rm \
  -v mydata:/data \
  -v /tmp:/tmp \
  alpine sh -c "cp -a /data/. /tmp/mydata/"
rsync -avz --progress /tmp/mydata/ user@target:/tmp/mydata/

# 증분 전송 (변경분만)
rsync -avz --progress --delete /tmp/mydata/ user@target:/tmp/mydata/

# 방법 3: 병렬 압축 (pigz)
docker run --rm \
  -v mydata:/data \
  alpine tar -I pigz -cf - -C /data . \
  | ssh user@target \
  "docker run --rm -i -v mydata:/data alpine tar -I pigz -xf - -C /data"
```

**성능 비교**:
```
100GB 볼륨 전송 시간:
- 일반 tar+gzip: 45분
- tar+pigz (병렬): 12분 (3.7배 빠름)
- rsync (초기): 40분
- rsync (증분, 10% 변경): 5분 (8배 빠름)
```

**꼬리 질문**
- Q: 네트워크 대역폭이 제한적일 때는 어떻게 하나요?
- A: 압축률을 높이거나(-9 옵션), 네트워크 사용이 적은 시간대에 전송하거나, 물리적 전송을 고려합니다.

**실무 연관**
- 클라우드 마이그레이션
- 재해 복구 사이트 동기화

</details>

<details>
<summary><strong>5. 컨테이너 오케스트레이션 환경에서 볼륨 관리 전략은?</strong></summary>

**모범 답안 포인트**
- Kubernetes PersistentVolume/PersistentVolumeClaim 사용
- 동적 프로비저닝 vs 정적 프로비저닝
- StatefulSet을 통한 볼륨 자동 관리

**예시 답변**
> "Kubernetes 같은 오케스트레이션 환경에서는 PersistentVolume(PV)과 PersistentVolumeClaim(PVC)으로 볼륨을 추상화하여 관리합니다. 동적 프로비저닝을 사용하면 PVC 생성 시 StorageClass에 따라 자동으로 볼륨이 생성되어 관리가 편리합니다. 데이터베이스 같은 stateful 애플리케이션은 StatefulSet을 사용하여 각 Pod마다 고유한 볼륨을 자동 할당받고, Pod 재시작 시에도 같은 볼륨을 재연결합니다. 백업 전략은 Velero 같은 도구로 자동화하고, 클러스터 간 마이그레이션은 Rook이나 클라우드 네이티브 스토리지를 활용합니다."

**실무 예시**:
```yaml
# StatefulSet with PVC
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 100Gi
```

**꼬리 질문**
- Q: StatefulSet과 Deployment의 볼륨 처리 차이는?
- A: StatefulSet은 각 Pod에 고유한 PVC를 할당하고 Pod 이름과 연결되지만, Deployment는 모든 Pod가 같은 PVC를 공유합니다.

**실무 연관**
- Kubernetes에서 데이터베이스 운영
- 클라우드 네이티브 스토리지 (AWS EBS, GCP PD)

</details>

---

## 📝 핵심 정리

### 이 장에서 배운 핵심 개념

| 개념 | 설명 | 핵심 키워드 |
|------|------|-------------|
| **Docker 볼륨** | 컨테이너 데이터를 영속적으로 저장하는 메커니즘 | 영속성, Docker 관리, 독립성 |
| **바인드 마운트** | 호스트의 특정 디렉토리를 컨테이너에 마운트 | 개발 환경, 실시간 반영, 경로 의존 |
| **tmpfs** | 메모리에 저장되는 임시 파일 시스템 | 보안, 고속, 휘발성 |
| **명명된 볼륨** | 사용자가 지정한 이름을 가진 볼륨 | 관리 용이, 권장 방식 |
| **볼륨 드라이버** | 볼륨 저장 방식을 결정하는 플러그인 | local, NFS, cloud |

### 필수 명령어 정리

| 명령어/코드 | 용도 | 예시 |
|-------------|------|------|
| `docker volume create` | 볼륨 생성 | `docker volume create mydata` |
| `docker volume ls` | 볼륨 목록 조회 | `docker volume ls --filter dangling=true` |
| `docker volume inspect` | 볼륨 상세 정보 | `docker volume inspect mydata` |
| `docker volume rm` | 볼륨 삭제 | `docker volume rm mydata` |
| `docker volume prune` | 미사용 볼륨 삭제 | `docker volume prune -f` |
| `-v name:/path` | 명명된 볼륨 마운트 | `docker run -v mydata:/app/data myapp` |
| `-v /host:/container` | 바인드 마운트 | `docker run -v $(pwd):/app myapp` |
| `--mount` | 명확한 마운트 문법 | `--mount source=mydata,target=/data` |
| `--tmpfs` | tmpfs 마운트 | `--tmpfs /tmp:size=100m` |

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] 데이터베이스는 반드시 명명된 볼륨 사용
- [ ] 프로덕션 환경에서 정기 백업 자동화
- [ ] 볼륨에 의미 있는 이름과 레이블 지정
- [ ] 변경 불필요한 데이터는 읽기 전용(`:ro`) 마운트
- [ ] 정기적으로 `docker volume prune` 실행
- [ ] 백업 파일의 복원 테스트 실시
- [ ] 개발 환경에서는 바인드 마운트 활용

#### ❌ 하지 말아야 할 것
- [ ] 익명 볼륨 사용 (관리 어려움)
- [ ] 여러 데이터베이스가 같은 볼륨 쓰기
- [ ] 백업 없이 볼륨 삭제
- [ ] Windows/macOS에서 전체 프로젝트 바인드 마운트
- [ ] 중요 데이터를 tmpfs에 저장
- [ ] 볼륨 백업 없이 프로덕션 배포
- [ ] 호스트 경로를 하드코딩 (이식성 저하)

### 성능 체크리스트

#### 성능
- [ ] SSD 스토리지 사용
- [ ] node_modules는 볼륨으로 분리
- [ ] I/O 집약적 작업은 tmpfs 고려
- [ ] 볼륨 드라이버 선택 최적화 (local > NFS)
- [ ] 불필요한 로그 파일 정리 자동화

#### 보안
- [ ] 민감한 데이터는 tmpfs 사용
- [ ] 볼륨 백업 파일 암호화
- [ ] 읽기 전용 마운트 적극 활용
- [ ] 볼륨 접근 권한 최소화
- [ ] 정기적인 보안 감사

---

## 🔗 관련 기술

| 기술 | 관계 | 학습 우선순위 |
|------|------|---------------|
| **Docker Compose** | 멀티 컨테이너 볼륨 관리 | ⭐⭐⭐ |
| **Kubernetes PV/PVC** | 오케스트레이션 환경 볼륨 | ⭐⭐⭐ |
| **NFS** | 네트워크 볼륨 공유 | ⭐⭐ |
| **AWS EBS** | 클라우드 블록 스토리지 | ⭐⭐ |
| **Rook** | 클라우드 네이티브 스토리지 | ⭐⭐ |
| **Velero** | Kubernetes 백업 도구 | ⭐⭐ |

---

## 🚀 다음 단계

### 다음 장 미리보기: 섹션 12: Docker Compose 기초
- **배울 내용 1**: docker-compose.yml 파일 구조 이해
- **배울 내용 2**: 멀티 컨테이너 애플리케이션 관리
- **배울 내용 3**: 환경 변수와 설정 파일 관리
- **실전 프로젝트**: WordPress + MySQL + Redis 스택 구축

### 이 장과의 연결점
```
이번 장에서 배운 [Docker 볼륨]
    ↓
다음 장에서 [Docker Compose로 볼륨 선언 및 관리]
    ↓
최종적으로 [프로덕션 멀티 컨테이너 앱 배포]
```

### 준비하면 좋을 것들
```bash
# Docker Compose 설치 확인
docker-compose --version

# 샘플 프로젝트 클론
git clone https://github.com/docker/awesome-compose
cd awesome-compose
```

---

## 🎉 축하합니다!

**이제 여러분은**:
✅ Docker 볼륨으로 컨테이너 데이터를 안전하게 영속화할 수 있습니다
✅ 볼륨, 바인드 마운트, tmpfs를 상황에 맞게 선택할 수 있습니다
✅ 볼륨 백업/복원/마이그레이션을 자유롭게 수행할 수 있습니다
✅ 프로덕션 환경에서 안정적인 데이터 관리 전략을 수립할 수 있습니다
✅ 주니어 개발자가 겪는 흔한 실수를 피할 수 있습니다

**다음 단계**:
- [ ] 다음 장(Docker Compose)으로 진행
- [ ] 실전 프로젝트로 볼륨 활용 연습
- [ ] 면접 질문 답변 연습
- [ ] 기존 프로젝트에 볼륨 적용해보기

---

**다음 장으로 이동**: [다음: 12장 Docker Compose 기초 →](12-Docker-Compose-기초.md)

**이전 장으로 돌아가기**: [← 이전: 10장 Docker 네트워크](10-Docker-네트워크.md)

**목차로 돌아가기**: [📚 전체 목차](README.md)