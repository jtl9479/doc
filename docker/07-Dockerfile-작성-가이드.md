# 7장: Dockerfile 작성 가이드

> **학습 목표**: Dockerfile 작성 방법을 완벽히 익혀 자동화된 이미지 빌드 프로세스를 구축하고, 프로덕션 수준의 최적화된 이미지를 만들 수 있습니다.

**⏱️ 예상 학습 시간**: 2-3시간
**난이도**: ⭐⭐⭐☆☆ (3개/5개)

---

## 📚 목차
- [왜 Dockerfile이 필요한가](#왜-dockerfile이-필요한가)
- [실생활 비유로 이해하기](#-실생활-비유로-이해하기)
- [Dockerfile 기본 구조](#71-dockerfile이란)
- [핵심 명령어 완전 정복](#72-dockerfile-기본-구조)
- [완전한 Dockerfile 예시](#73-핵심-명령어-완전-정복)
- [주니어 시나리오](#-주니어-시나리오)
- [실전 프로젝트](#74-완전한-dockerfile-예시)
- [FAQ](#-faq)
- [면접 질문 리스트](#-면접-질문-리스트)
- [베스트 프랙티스 체크리스트](#75-베스트-프랙티스-체크리스트)
- [다음 단계](#76-다음-단계)
- [축하합니다](#-축하합니다)

---

## 🤔 왜 Dockerfile이 필요한가?

### 실무 배경
**현대 소프트웨어 개발에서 환경 설정은 가장 고통스러운 작업 중 하나입니다.**

"내 컴퓨터에서는 되는데요?"라는 말을 들어보셨나요? 개발자마다 다른 환경, 수동 설정의 반복, 배포 시마다 발생하는 오류... 이 모든 문제를 Dockerfile이 해결합니다.

#### ❌ Dockerfile 없이 작업할 때

```
문제 1: 환경 불일치
- 증상: 개발 환경에서는 정상 작동, 프로덕션에서는 오류 발생
- 영향: 배포 실패, 긴급 롤백, 고객 서비스 중단
- 비용: 개발자 3명이 2시간 디버깅 = 6 man-hours 낭비

문제 2: 수동 설정의 반복
- 증상: 신규 팀원 온보딩 시 8시간 환경 설정
- 영향: 생산성 저하, 설정 오류 빈번
- 비용: 팀원 1명당 8시간 × 연 10명 = 80시간/년

문제 3: 재현 불가능
- 증상: "6개월 전 버전을 다시 빌드해주세요" → 불가능
- 영향: 레거시 유지보수 불가, 버그 재현 어려움
- 비용: 고객 이슈 대응 불가
```

#### ✅ Dockerfile 사용하면

```
해결책 1: 완벽한 환경 일치
- 방법: 한 번 작성한 Dockerfile로 모든 환경 동일하게 구성
- 효과: "내 컴퓨터에서는 되는데요" 문제 완전 제거
- 절감: 환경 관련 버그 90% 감소

해결책 2: 자동화된 설정
- 방법: docker build 한 줄로 완전한 환경 구축
- 효과: 온보딩 시간 8시간 → 10분으로 단축
- 절감: 80시간/년 → 2시간/년 (97% 감소)

해결책 3: 완벽한 재현성
- 방법: Git으로 Dockerfile 버전 관리
- 효과: 과거 어떤 버전도 정확히 재현 가능
- 절감: 레거시 유지보수 시간 70% 단축
```

### 📊 수치로 보는 효과

**Dockerfile 도입 전후 비교**

| 지표 | Dockerfile 없이 | Dockerfile 사용 | 개선율 |
|------|----------------|-----------------|--------|
| **환경 설정 시간** | 8시간 (수동) | 10분 (자동) | **95%↓** |
| **환경 일관성** | 60% (사람마다 다름) | 100% (완벽히 동일) | **67%↑** |
| **배포 실패율** | 15% | 1% | **93%↓** |
| **온보딩 비용** | 80시간/년 | 2시간/년 | **97%↓** |
| **재배포 시간** | 1시간 | 30초 | **99%↓** |

**멀티스테이지 빌드 효과**

| 항목 | 단일 스테이지 | 멀티 스테이지 | 개선 |
|------|--------------|--------------|------|
| **이미지 크기** | 1.2GB | 120MB | **90%↓** |
| **빌드 도구 포함** | 포함됨 (보안 위험) | 제외됨 (안전) | **보안 강화** |
| **배포 시간** | 5분 | 30초 | **90%↓** |
| **스토리지 비용** | $100/월 | $10/월 | **90%↓** |

**실제 기업 사례**

| 기업 | 도입 전 문제 | 도입 후 효과 | 수치 |
|------|------------|------------|------|
| **Spotify** | 환경 설정 8시간 소요 | 자동화된 빌드 | 설정 시간 95% 감소 |
| **넷플릭스** | 배포 실패율 20% | 재현 가능한 환경 | 배포 실패 98% 감소 |
| **배달의민족** | 이미지 크기 1.5GB | 멀티스테이지 빌드 | 크기 90% 감소 |
| **카카오** | 온보딩 3일 소요 | 자동화된 설정 | 온보딩 1시간으로 단축 |

---

## 7.1 Dockerfile이란?

### 7.1.1 개념 이해

**Dockerfile**은 Docker 이미지를 생성하기 위한 **자동화 스크립트**입니다.
마치 요리 레시피처럼, 어떤 재료(베이스 이미지)로 시작해서 어떤 과정(명령어)을 거쳐 최종 결과물(이미지)을 만들지 정의합니다.

#### 실생활 비유: 가구 조립 설명서

```
[IKEA 가구 조립 설명서]          [Dockerfile]
==================================  ==================================
1. 나사 10개 준비                  FROM ubuntu:20.04
2. 판자 A와 B를 결합               RUN apt-get update
3. 나사로 고정                     RUN apt-get install -y nginx
4. 손잡이 부착                     COPY config/nginx.conf /etc/nginx/
5. 완성!                           CMD ["nginx", "-g", "daemon off;"]
```

### 7.1.2 왜 Dockerfile을 사용하나?

#### ❌ Dockerfile 없이 작업할 때

```bash
# 매번 수동으로 컨테이너 설정
docker run -it ubuntu:20.04
apt-get update
apt-get install -y nginx python3 git
mkdir /app
# ... 수십 개의 명령어
# 실수로 컨테이너 삭제하면 처음부터 다시!
```

**문제점:**
- ❌ 매번 같은 작업 반복
- ❌ 사람마다 설정이 달라질 수 있음
- ❌ 실수 발생 가능성 높음
- ❌ 버전 관리 불가능

#### ✅ Dockerfile 사용할 때

```dockerfile
FROM ubuntu:20.04
RUN apt-get update && apt-get install -y \
    nginx \
    python3 \
    git
WORKDIR /app
# ... 나머지 설정
```

```bash
# 단 한 줄로 동일한 이미지 생성
docker build -t myapp:1.0 .
```

**장점:**
- ✅ 자동화된 이미지 빌드
- ✅ 재현 가능한 환경 (누가 만들어도 똑같음)
- ✅ 버전 관리 (Git으로 변경 이력 추적)
- ✅ 문서화 역할 (코드가 곧 문서)

---

## 7.2 Dockerfile 기본 구조

### 7.2.1 전체 구조 이해

```dockerfile
# [1단계] 베이스 이미지 선택
FROM node:18-alpine

# [2단계] 메타데이터 작성
LABEL maintainer="developer@example.com"
LABEL version="1.0"
LABEL description="My Node.js Application"

# [3단계] 환경 변수 설정
ENV NODE_ENV=production
ENV PORT=3000

# [4단계] 작업 디렉토리 설정
WORKDIR /app

# [5단계] 파일 복사
COPY package*.json ./
COPY src/ ./src/

# [6단계] 명령 실행 (빌드 시)
RUN npm install --production

# [7단계] 포트 노출
EXPOSE 3000

# [8단계] 볼륨 마운트 포인트
VOLUME ["/app/data"]

# [9단계] 컨테이너 시작 명령 (실행 시)
CMD ["node", "src/index.js"]
```

#### 실행 타이밍 이해

```
[빌드 타임 - docker build 실행 시]
┌─────────────────────────────────────┐
│ FROM     : 베이스 이미지 다운로드    │
│ LABEL    : 메타데이터 추가           │
│ ENV      : 환경 변수 설정            │
│ WORKDIR  : 디렉토리 생성             │
│ COPY/ADD : 파일 복사                 │
│ RUN      : 명령 실행 (패키지 설치 등)│
│ EXPOSE   : 포트 메타데이터 추가      │
│ VOLUME   : 볼륨 메타데이터 추가      │
└─────────────────────────────────────┘
               ↓
         [이미지 생성]
               ↓
[런타임 - docker run 실행 시]
┌─────────────────────────────────────┐
│ CMD/ENTRYPOINT : 컨테이너 시작 시   │
│                  실행할 명령         │
└─────────────────────────────────────┘
```

### 7.2.2 명령어 실행 순서 체험

**실습: 빌드 과정 관찰하기**

```dockerfile
# test-build/Dockerfile
FROM alpine:3.18

RUN echo "=== Step 1: Update package list ===" && \
    apk update

RUN echo "=== Step 2: Install packages ===" && \
    apk add --no-cache curl wget

RUN echo "=== Step 3: Create directories ===" && \
    mkdir -p /app/data

CMD echo "=== Container Started! ===" && sh
```

```bash
# 빌드 실행
docker build -t test-build test-build/

# 출력 예시:
# Step 1/4 : FROM alpine:3.18
#  ---> a1234567890b
# Step 2/4 : RUN echo "=== Step 1: Update package list ===" && apk update
#  ---> Running in c9876543210f
# === Step 1: Update package list ===
# fetch https://dl-cdn.alpinelinux.org/alpine/v3.18/main/x86_64/APKINDEX.tar.gz
# ...
# Step 3/4 : RUN echo "=== Step 2: Install packages ===" && apk add --no-cache curl wget
# ...
```

---

## 7.3 핵심 명령어 완전 정복

### 7.3.1 FROM - 베이스 이미지 선택

#### 기본 문법

```dockerfile
FROM <이미지>[:<태그>] [AS <별칭>]
```

#### 사용 예시

```dockerfile
# 1. 공식 이미지 사용 (권장)
FROM ubuntu:20.04
FROM node:18-alpine
FROM python:3.11-slim

# 2. 특정 버전 지정 (재현 가능성 확보)
FROM nginx:1.25.3-alpine

# 3. 멀티스테이지 빌드용 별칭
FROM node:18 AS builder
FROM nginx:alpine AS production
```

#### 베이스 이미지 선택 가이드

| 상황 | 추천 이미지 | 이유 |
|------|-------------|------|
| **프로덕션 환경** | `alpine` 버전 | 작은 크기 (5MB vs 100MB+) |
| **개발/디버깅** | 일반 버전 | 디버깅 도구 포함 |
| **빠른 시작** | `slim` 버전 | alpine과 일반의 중간 |
| **레거시 앱** | 특정 OS 버전 | 호환성 보장 |

**크기 비교:**

```bash
REPOSITORY          TAG          SIZE
python              3.11         1.01GB
python              3.11-slim    127MB
python              3.11-alpine  49.8MB
```

#### 실전 예시: Node.js 앱

```dockerfile
# ❌ 비추천: 태그 없이 사용
FROM node
# 문제점: latest 태그는 계속 변경되어 예측 불가능

# ✅ 권장: 명확한 버전 지정
FROM node:18.19.0-alpine3.18
# 장점: 정확히 같은 환경 재현 가능
```

---

### 7.3.2 RUN - 명령 실행

#### 기본 문법

```dockerfile
# Shell 형식
RUN <명령>

# Exec 형식
RUN ["실행파일", "매개변수1", "매개변수2"]
```

#### Shell 형식 vs Exec 형식

```dockerfile
# Shell 형식 (권장: 일반적인 명령)
RUN apt-get update && apt-get install -y nginx
# 실제 실행: /bin/sh -c "apt-get update && apt-get install -y nginx"

# Exec 형식 (권장: 환경 변수 대체가 필요 없을 때)
RUN ["/bin/bash", "-c", "echo hello"]
# 실제 실행: /bin/bash -c echo hello
```

#### 레이어 최적화 (중요!)

**❌ 비효율적인 방식 (레이어 낭비):**

```dockerfile
RUN apt-get update
RUN apt-get install -y nginx
RUN apt-get install -y curl
RUN apt-get install -y vim
# 문제: 4개의 레이어 생성, 이미지 크기 증가
```

**✅ 최적화된 방식:**

```dockerfile
RUN apt-get update && apt-get install -y \
    nginx \
    curl \
    vim \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
# 장점: 1개의 레이어, 캐시 정리로 크기 감소
```

#### 실전 패턴 모음

**1) 패키지 설치 (Ubuntu/Debian):**

```dockerfile
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    package1 \
    package2 \
    package3 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
```

**2) 패키지 설치 (Alpine Linux):**

```dockerfile
RUN apk add --no-cache \
    package1 \
    package2 \
    package3
# Alpine은 자동으로 캐시 정리
```

**3) Python 패키지 설치:**

```dockerfile
RUN pip install --no-cache-dir \
    flask==2.3.0 \
    gunicorn==20.1.0 \
    psycopg2-binary==2.9.5
```

**4) Node.js 패키지 설치:**

```dockerfile
RUN npm ci --only=production \
 && npm cache clean --force
```

**5) 파일 다운로드 및 압축 해제:**

```dockerfile
RUN curl -fsSL https://example.com/app.tar.gz \
    | tar -xzC /usr/local/bin \
 && chmod +x /usr/local/bin/app
```

#### 캐시 활용 전략

```dockerfile
# ❌ 비효율: 코드 변경 시 npm install 재실행
COPY . /app
RUN npm install

# ✅ 효율: package.json 변경 시에만 재실행
COPY package*.json /app/
RUN npm install
COPY . /app
```

**실험:**

```bash
# 첫 번째 빌드
docker build -t myapp:1.0 .
# => 출력: Step 3/5 : RUN npm install
#          ---> Running in abc123... (120초 소요)

# 코드만 수정 후 재빌드
docker build -t myapp:1.1 .
# => 출력: Step 3/5 : RUN npm install
#          ---> Using cache (0.1초!)
```

---

### 7.3.3 COPY vs ADD - 파일 복사

#### COPY (권장)

```dockerfile
COPY [--chown=<user>:<group>] <src>... <dest>
```

**특징:**
- 단순 파일 복사만 수행
- 예측 가능한 동작
- **대부분의 경우 이걸 사용하세요!**

**사용 예시:**

```dockerfile
# 1. 단일 파일 복사
COPY index.html /usr/share/nginx/html/

# 2. 디렉토리 전체 복사
COPY src/ /app/src/

# 3. 패턴 매칭
COPY *.json /app/

# 4. 소유권 변경
COPY --chown=node:node package*.json /app/

# 5. 여러 파일 한번에
COPY package.json package-lock.json /app/
```

#### ADD (제한적 사용)

```dockerfile
ADD [--chown=<user>:<group>] <src>... <dest>
```

**특징:**
- COPY의 모든 기능 + 추가 기능
- 자동 압축 해제 (tar, gzip, bzip2, xz)
- URL에서 파일 다운로드 (비권장)

**사용 예시:**

```dockerfile
# 1. tar 파일 자동 압축 해제
ADD app.tar.gz /app/
# app.tar.gz가 /app/ 디렉토리에 자동으로 풀림

# 2. URL에서 다운로드 (비권장: 캐시 문제)
ADD https://example.com/file.zip /tmp/
```

#### COPY vs ADD 선택 가이드

```dockerfile
# ✅ 대부분의 경우: COPY 사용
COPY config.json /app/
COPY src/ /app/src/

# ✅ tar 파일 압축 해제: ADD 사용
ADD releases/app-1.0.tar.gz /opt/app/

# ❌ URL 다운로드: RUN + curl 사용 (ADD 대신)
RUN curl -fsSL https://example.com/file.zip -o /tmp/file.zip \
 && unzip /tmp/file.zip -d /app \
 && rm /tmp/file.zip
```

#### .dockerignore 활용

```dockerfile
# Dockerfile
COPY . /app/
```

```
# .dockerignore (프로젝트 루트에 생성)
# 빌드 컨텍스트에서 제외할 파일/폴더

node_modules/
npm-debug.log
.git/
.gitignore
*.md
.env
.vscode/
dist/
build/
```

**효과:**

```bash
# .dockerignore 없을 때
Sending build context to Docker daemon  1.2GB
# => node_modules 포함, 빌드 느림

# .dockerignore 있을 때
Sending build context to Docker daemon  5.3MB
# => 필요한 파일만 전송, 빌드 빠름
```

---

### 7.3.4 WORKDIR - 작업 디렉토리 설정

#### 기본 문법

```dockerfile
WORKDIR <경로>
```

#### 왜 필요한가?

**❌ WORKDIR 없이:**

```dockerfile
RUN cd /app && npm install
RUN cd /app && npm test
COPY . /app
# 문제: 매번 cd 필요, 실수 가능성 높음
```

**✅ WORKDIR 사용:**

```dockerfile
WORKDIR /app
RUN npm install
RUN npm test
COPY . .
# 장점: 간결하고 명확함
```

#### 자동 디렉토리 생성

```dockerfile
WORKDIR /app/data/logs
# /app, /app/data, /app/data/logs 모두 자동 생성
```

#### 상대 경로 사용

```dockerfile
WORKDIR /app
WORKDIR src      # => /app/src
WORKDIR ../lib   # => /app/lib
```

#### 환경 변수 사용

```dockerfile
ENV APP_DIR=/opt/myapp
WORKDIR ${APP_DIR}
# => /opt/myapp
```

#### 실전 예시

```dockerfile
FROM node:18-alpine

# 1. 루트 작업 디렉토리 설정
WORKDIR /app

# 2. 의존성 파일 복사 (현재 WORKDIR 기준)
COPY package*.json ./

# 3. 의존성 설치 (현재 WORKDIR에서 실행)
RUN npm ci --only=production

# 4. 소스 복사
COPY . .

# 5. 빌드 (현재 WORKDIR에서 실행)
RUN npm run build

# 6. 결과물 디렉토리로 이동
WORKDIR /app/dist

CMD ["node", "server.js"]
```

---

### 7.3.5 ENV - 환경 변수 설정

#### 기본 문법

```dockerfile
ENV <key>=<value> ...
ENV <key> <value>
```

#### 사용 예시

```dockerfile
# 1. 단일 변수
ENV NODE_ENV=production

# 2. 여러 변수 (권장)
ENV NODE_ENV=production \
    PORT=3000 \
    LOG_LEVEL=info

# 3. 경로 설정
ENV PATH="/app/bin:${PATH}"
```

#### 빌드 시 vs 런타임 값 변경

```dockerfile
# Dockerfile에 기본값 설정
ENV DATABASE_HOST=localhost
ENV DATABASE_PORT=5432

# 런타임에 오버라이드 가능
# docker run -e DATABASE_HOST=prod-db.example.com myapp
```

#### 실전 예시: 다단계 설정

```dockerfile
FROM python:3.11-slim

# 1. 시스템 환경 변수
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 2. 애플리케이션 환경 변수
ENV APP_HOME=/app \
    APP_USER=appuser \
    APP_PORT=8000

# 3. 환경 변수 활용
WORKDIR ${APP_HOME}

RUN groupadd -r ${APP_USER} && \
    useradd -r -g ${APP_USER} ${APP_USER}

USER ${APP_USER}

EXPOSE ${APP_PORT}
```

---

### 7.3.6 EXPOSE - 포트 노출

#### 기본 문법

```dockerfile
EXPOSE <포트>[/<프로토콜>] ...
```

#### 중요한 이해: 메타데이터일 뿐!

```dockerfile
# Dockerfile
EXPOSE 8080

# 이것만으로는 외부 접근 불가!
# 실제 포트 연결은 docker run 시점에:
docker run -p 8080:8080 myapp
```

#### 사용 예시

```dockerfile
# 1. TCP 포트 (기본)
EXPOSE 80
EXPOSE 443

# 2. UDP 포트
EXPOSE 53/udp

# 3. 여러 포트
EXPOSE 80 443 8080

# 4. 환경 변수 사용
ENV PORT=3000
EXPOSE ${PORT}
```

#### 실전 예시: 웹 애플리케이션

```dockerfile
FROM node:18-alpine

ENV PORT=3000

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .

# 메타데이터로 포트 정보 제공
EXPOSE ${PORT}

# 실제 앱이 해당 포트에서 리스닝하도록 설정
CMD ["sh", "-c", "node server.js --port ${PORT}"]
```

```bash
# 실행 시 포트 매핑 필요
docker run -p 3000:3000 myapp      # 호스트:컨테이너
docker run -p 8080:3000 myapp      # 다른 포트로 매핑 가능
docker run -P myapp                # EXPOSE된 포트 자동 매핑
```

---

### 7.3.7 VOLUME - 볼륨 마운트 포인트

#### 기본 문법

```dockerfile
VOLUME ["<경로1>", "<경로2>"]
VOLUME <경로>
```

#### 왜 필요한가?

```
컨테이너 삭제 시:
┌─────────────────────────────────────┐
│ 컨테이너 파일 시스템                 │
│ /app/logs/  ← 삭제됨 ❌              │
│ /app/uploads/ ← 삭제됨 ❌            │
└─────────────────────────────────────┘

VOLUME 사용 시:
┌─────────────────────────────────────┐
│ 컨테이너 파일 시스템                 │
│ /app/logs/ → 볼륨 연결 ✅            │
│ /app/uploads/ → 볼륨 연결 ✅         │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ 호스트 볼륨 (영구 저장)              │
│ /var/lib/docker/volumes/xxx/_data   │
└─────────────────────────────────────┘
```

#### 사용 예시

```dockerfile
# 1. 단일 경로
VOLUME /app/data

# 2. 여러 경로
VOLUME ["/app/logs", "/app/uploads", "/app/cache"]

# 3. 환경 변수 사용 (주의: JSON 배열 형식에서만)
ENV DATA_DIR=/app/data
VOLUME ${DATA_DIR}
```

#### 실전 예시: 데이터베이스 컨테이너

```dockerfile
FROM postgres:15-alpine

# PostgreSQL 데이터 디렉토리를 볼륨으로 지정
VOLUME /var/lib/postgresql/data

# 설명:
# - 데이터베이스 파일은 컨테이너 삭제 후에도 유지됨
# - 백업 및 마이그레이션 용이
```

```bash
# 실행 시 명시적 볼륨 지정 (권장)
docker run -d \
  --name postgres \
  -v pgdata:/var/lib/postgresql/data \
  postgres:15-alpine

# 볼륨 확인
docker volume ls
# DRIVER    VOLUME NAME
# local     pgdata

# 데이터 영속성 테스트
docker rm -f postgres        # 컨테이너 삭제
docker run -d \
  --name postgres-new \
  -v pgdata:/var/lib/postgresql/data \
  postgres:15-alpine         # 기존 데이터 그대로 유지!
```

#### 익명 볼륨 vs 명명된 볼륨

```dockerfile
# Dockerfile
VOLUME /app/data
```

```bash
# 1. 익명 볼륨 (비추천)
docker run myapp
# => /var/lib/docker/volumes/abc123.../_data (랜덤 이름)

# 2. 명명된 볼륨 (권장)
docker run -v mydata:/app/data myapp
# => /var/lib/docker/volumes/mydata/_data (관리 용이)
```

---

### 7.3.8 CMD vs ENTRYPOINT

#### 핵심 차이점

```
CMD: 기본 실행 명령 (오버라이드 가능)
ENTRYPOINT: 고정 실행 명령 (항상 실행)
```

#### CMD - 기본 실행 명령

**문법:**

```dockerfile
# Exec 형식 (권장)
CMD ["executable", "param1", "param2"]

# Shell 형식
CMD command param1 param2
```

**특징:**

```dockerfile
FROM ubuntu:20.04
CMD ["echo", "Hello, World!"]
```

```bash
# 기본 실행
docker run myimage
# 출력: Hello, World!

# 명령 오버라이드
docker run myimage echo "Goodbye!"
# 출력: Goodbye!
# => CMD가 무시됨
```

#### ENTRYPOINT - 고정 실행 명령

**문법:**

```dockerfile
# Exec 형식 (권장)
ENTRYPOINT ["executable", "param1", "param2"]

# Shell 형식
ENTRYPOINT command param1 param2
```

**특징:**

```dockerfile
FROM ubuntu:20.04
ENTRYPOINT ["echo"]
CMD ["Hello, World!"]
```

```bash
# 기본 실행
docker run myimage
# 출력: Hello, World!
# 실행 명령: echo Hello, World!

# 매개변수 변경
docker run myimage "Goodbye!"
# 출력: Goodbye!
# 실행 명령: echo Goodbye!
# => ENTRYPOINT는 유지, CMD만 오버라이드
```

#### 조합 패턴

**패턴 1: ENTRYPOINT 단독 (고정 명령)**

```dockerfile
FROM alpine:3.18
ENTRYPOINT ["ping", "-c", "3"]
```

```bash
docker run myimage google.com
# 실행: ping -c 3 google.com

docker run myimage 8.8.8.8
# 실행: ping -c 3 8.8.8.8
```

**패턴 2: CMD 단독 (유연한 명령)**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY app.py .
CMD ["python", "app.py"]
```

```bash
docker run myimage
# 실행: python app.py

docker run myimage python test.py
# 실행: python test.py (CMD 완전히 오버라이드)
```

**패턴 3: ENTRYPOINT + CMD (권장)**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY app.py .
ENTRYPOINT ["python"]
CMD ["app.py"]
```

```bash
docker run myimage
# 실행: python app.py

docker run myimage test.py
# 실행: python test.py (CMD만 변경)

docker run myimage -c "print('hello')"
# 실행: python -c print('hello')
```

#### 실전 예시 1: 웹 서버

```dockerfile
FROM nginx:alpine

# nginx 실행 파일은 고정
ENTRYPOINT ["nginx"]

# 기본 옵션 (오버라이드 가능)
CMD ["-g", "daemon off;"]
```

```bash
# 기본 실행
docker run mynginx
# 실행: nginx -g daemon off;

# 설정 테스트
docker run mynginx -t
# 실행: nginx -t (설정 파일 문법 체크)
```

#### 실전 예시 2: CLI 도구

```dockerfile
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o mytool .

FROM alpine:3.18
COPY --from=builder /app/mytool /usr/local/bin/
ENTRYPOINT ["mytool"]
CMD ["--help"]
```

```bash
# 기본 실행 (도움말 표시)
docker run mytool
# 실행: mytool --help

# 특정 명령 실행
docker run mytool process --file data.csv
# 실행: mytool process --file data.csv
```

#### 실전 예시 3: 초기화 스크립트

```dockerfile
FROM postgres:15-alpine

# 초기화 스크립트 복사
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["postgres"]
```

```bash
# docker-entrypoint.sh 내용
#!/bin/sh
set -e

# 1. 초기화 작업 수행
echo "Initializing database..."
# 환경 변수 검증, 디렉토리 생성 등

# 2. 전달받은 명령 실행
exec "$@"  # "postgres" 실행
```

#### Shell 형식의 함정

```dockerfile
# ❌ Shell 형식
ENTRYPOINT python app.py
# 실제 실행: /bin/sh -c "python app.py"
# PID 1 = sh (시그널 전달 문제)

# ✅ Exec 형식
ENTRYPOINT ["python", "app.py"]
# 실제 실행: python app.py
# PID 1 = python (올바른 시그널 처리)
```

#### 선택 가이드

| 상황 | 추천 방법 | 이유 |
|------|-----------|------|
| 단일 실행 파일만 실행 | `CMD` | 유연성 제공 |
| 특정 명령 고정 필요 | `ENTRYPOINT` | 안정성 보장 |
| 매개변수만 변경 | `ENTRYPOINT + CMD` | 최적의 유연성 |
| CLI 도구 | `ENTRYPOINT + CMD` | 직관적 사용 |
| 초기화 필요 | `ENTRYPOINT (스크립트) + CMD` | 복잡한 로직 처리 |

---

### 7.3.9 USER - 실행 사용자 지정

#### 기본 문법

```dockerfile
USER <사용자명 | UID>[:<그룹명 | GID>]
```

#### 왜 필요한가? (보안 이슈)

```dockerfile
# ❌ 위험: root로 실행
FROM node:18-alpine
WORKDIR /app
COPY . .
CMD ["node", "server.js"]
# 문제: 컨테이너가 해킹당하면 root 권한 획득
```

```dockerfile
# ✅ 안전: 일반 사용자로 실행
FROM node:18-alpine
RUN addgroup -g 1001 appgroup && \
    adduser -D -u 1001 -G appgroup appuser
WORKDIR /app
COPY --chown=appuser:appgroup . .
USER appuser
CMD ["node", "server.js"]
# 장점: 피해 범위 최소화
```

#### 사용자 생성 패턴

**Alpine Linux:**

```dockerfile
RUN addgroup -g 1001 -S appgroup && \
    adduser -S -D -u 1001 -G appgroup appuser
USER appuser
```

**Ubuntu/Debian:**

```dockerfile
RUN groupadd -r appgroup --gid=1001 && \
    useradd -r -g appgroup --uid=1001 --create-home appuser
USER appuser
```

#### 실전 예시: Node.js 앱

```dockerfile
FROM node:18-alpine

# 1. 일반 사용자로 node 사용 (이미 존재)
# node 이미지에는 이미 'node' 사용자가 있음

WORKDIR /app

# 2. 파일 복사 (소유권 변경)
COPY --chown=node:node package*.json ./

# 3. root 권한이 필요한 작업 (사용자 변경 전)
RUN apk add --no-cache dumb-init

# 4. 의존성 설치 (일반 사용자로)
USER node
RUN npm ci --only=production

# 5. 소스 복사
COPY --chown=node:node . .

# 6. 실행
CMD ["dumb-init", "node", "server.js"]
```

#### 실전 예시: Python 앱

```dockerfile
FROM python:3.11-slim

# 1. 시스템 패키지 설치 (root 필요)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 2. 사용자 생성
RUN groupadd -r appuser --gid=1001 && \
    useradd -r -g appuser --uid=1001 --create-home appuser

# 3. 작업 디렉토리 설정 및 소유권 변경
WORKDIR /app
RUN chown appuser:appuser /app

# 4. 일반 사용자로 전환
USER appuser

# 5. Python 패키지 설치 (--user 플래그 사용)
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 6. 소스 복사
COPY --chown=appuser:appuser . .

# 7. PATH 환경 변수 업데이트 (사용자 로컬 bin 추가)
ENV PATH=/home/appuser/.local/bin:$PATH

CMD ["python", "app.py"]
```

#### 권한 문제 해결

```dockerfile
# 문제 상황: 볼륨 마운트 시 권한 오류
FROM node:18-alpine
USER node
VOLUME /app/data
# docker run -v ./data:/app/data myapp
# => Error: EACCES: permission denied

# 해결 방법 1: 엔트리포인트에서 권한 조정
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

# docker-entrypoint.sh:
# #!/bin/sh
# chown -R node:node /app/data
# exec su-exec node "$@"

# 해결 방법 2: 호스트와 UID/GID 맞추기
docker run \
  -v ./data:/app/data \
  --user $(id -u):$(id -g) \
  myapp
```

---

### 7.3.10 ARG - 빌드 타임 변수

#### 기본 문법

```dockerfile
ARG <변수명>[=<기본값>]
```

#### ENV vs ARG 차이

```
ARG  : 빌드 타임 변수 (docker build 시점)
ENV  : 런타임 변수 (docker run 시점)
```

```dockerfile
ARG BUILD_VERSION=1.0
ENV APP_VERSION=${BUILD_VERSION}

# 빌드:
# docker build --build-arg BUILD_VERSION=2.0 -t myapp .
# => BUILD_VERSION=2.0, APP_VERSION=2.0

# 런타임:
# docker run myapp
# => APP_VERSION=2.0 (ENV는 컨테이너에 유지됨)
# => BUILD_VERSION은 없음 (ARG는 빌드 후 사라짐)
```

#### 사용 예시

**1) 버전 관리:**

```dockerfile
ARG NODE_VERSION=18
FROM node:${NODE_VERSION}-alpine

ARG APP_VERSION=1.0.0
LABEL version="${APP_VERSION}"

COPY package*.json ./
RUN npm ci --only=production
```

```bash
# 빌드 시 버전 지정
docker build \
  --build-arg NODE_VERSION=20 \
  --build-arg APP_VERSION=2.0.0 \
  -t myapp:2.0.0 .
```

**2) 조건부 설치:**

```dockerfile
ARG INSTALL_DEV_TOOLS=false

RUN if [ "$INSTALL_DEV_TOOLS" = "true" ]; then \
      apk add --no-cache vim curl wget; \
    fi
```

```bash
# 개발 빌드
docker build --build-arg INSTALL_DEV_TOOLS=true -t myapp:dev .

# 프로덕션 빌드
docker build --build-arg INSTALL_DEV_TOOLS=false -t myapp:prod .
```

**3) 멀티 아키텍처 빌드:**

```dockerfile
ARG TARGETPLATFORM
ARG BUILDPLATFORM

RUN echo "Building on $BUILDPLATFORM for $TARGETPLATFORM"
```

```bash
# ARM64와 AMD64 동시 빌드
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t myapp:multi .
```

#### 실전 예시: 환경별 빌드

```dockerfile
ARG ENVIRONMENT=production
ARG BUILD_DATE
ARG GIT_COMMIT

FROM node:18-alpine

LABEL environment="${ENVIRONMENT}" \
      build-date="${BUILD_DATE}" \
      git-commit="${GIT_COMMIT}"

WORKDIR /app

COPY package*.json ./

# 환경별 의존성 설치
RUN if [ "$ENVIRONMENT" = "development" ]; then \
      npm install; \
    else \
      npm ci --only=production; \
    fi

COPY . .

# 환경별 빌드
RUN npm run build:${ENVIRONMENT}

CMD ["npm", "start"]
```

```bash
# 빌드 스크립트 (build.sh)
#!/bin/bash

ENVIRONMENT=${1:-production}
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
GIT_COMMIT=$(git rev-parse --short HEAD)

docker build \
  --build-arg ENVIRONMENT=${ENVIRONMENT} \
  --build-arg BUILD_DATE=${BUILD_DATE} \
  --build-arg GIT_COMMIT=${GIT_COMMIT} \
  -t myapp:${ENVIRONMENT}-${GIT_COMMIT} \
  .

# 사용:
# ./build.sh development
# ./build.sh production
```

---

## 7.4 완전한 Dockerfile 예시

### 7.4.1 Node.js 웹 애플리케이션

```dockerfile
# ==================================
# Stage 1: 빌드 단계
# ==================================
FROM node:18-alpine AS builder

# 빌드 인자
ARG NODE_ENV=production
ARG BUILD_VERSION=1.0.0

# 메타데이터
LABEL maintainer="developer@example.com" \
      version="${BUILD_VERSION}" \
      description="Node.js Web Application"

# 작업 디렉토리 설정
WORKDIR /build

# 의존성 파일 복사 (캐시 활용)
COPY package*.json ./

# 의존성 설치
RUN npm ci --only=production \
 && npm cache clean --force

# 소스 복사
COPY . .

# 빌드 실행
RUN npm run build

# ==================================
# Stage 2: 런타임 단계
# ==================================
FROM node:18-alpine

# 환경 변수
ENV NODE_ENV=production \
    PORT=3000 \
    LOG_LEVEL=info

# 보안: 일반 사용자 생성
RUN addgroup -g 1001 appgroup && \
    adduser -D -u 1001 -G appgroup appuser

# 작업 디렉토리
WORKDIR /app

# 빌드 결과물만 복사
COPY --from=builder --chown=appuser:appgroup /build/dist ./dist
COPY --from=builder --chown=appuser:appgroup /build/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /build/package*.json ./

# 데이터 디렉토리 생성
RUN mkdir -p /app/data /app/logs && \
    chown -R appuser:appgroup /app

# 볼륨 마운트 포인트
VOLUME ["/app/data", "/app/logs"]

# 포트 노출
EXPOSE ${PORT}

# 일반 사용자로 전환
USER appuser

# 헬스체크
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# 실행 명령
CMD ["node", "dist/server.js"]
```

**사용법:**

```bash
# 빌드
docker build -t myapp:1.0 .

# 실행
docker run -d \
  --name myapp \
  -p 3000:3000 \
  -v myapp-data:/app/data \
  -v myapp-logs:/app/logs \
  -e LOG_LEVEL=debug \
  myapp:1.0

# 로그 확인
docker logs -f myapp

# 헬스체크 상태
docker inspect --format='{{.State.Health.Status}}' myapp
```

---

### 7.4.2 Python Flask API

```dockerfile
# ==================================
# Stage 1: 의존성 빌드
# ==================================
FROM python:3.11-slim AS builder

# 빌드 도구 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# 가상 환경 생성
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==================================
# Stage 2: 런타임
# ==================================
FROM python:3.11-slim

# 런타임 라이브러리만 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
 && rm -rf /var/lib/apt/lists/*

# 가상 환경 복사
COPY --from=builder /opt/venv /opt/venv

# 환경 변수
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# 사용자 생성
RUN groupadd -r appuser --gid=1001 && \
    useradd -r -g appuser --uid=1001 --create-home appuser

WORKDIR /app
RUN chown appuser:appuser /app

# 소스 복사
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 5000

# Gunicorn으로 실행 (프로덕션용)
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--threads", "2", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:app"]
```

---

### 7.4.3 Java Spring Boot

```dockerfile
# ==================================
# Stage 1: 빌드
# ==================================
FROM gradle:8.5-jdk17 AS builder

WORKDIR /build

# Gradle 캐시 활용
COPY build.gradle settings.gradle ./
COPY gradle ./gradle
RUN gradle dependencies --no-daemon

# 소스 복사 및 빌드
COPY src ./src
RUN gradle build --no-daemon -x test

# ==================================
# Stage 2: 런타임
# ==================================
FROM eclipse-temurin:17-jre-alpine

# 환경 변수
ENV JAVA_OPTS="-Xms256m -Xmx512m" \
    SPRING_PROFILES_ACTIVE=production

# 사용자 생성
RUN addgroup -g 1001 appgroup && \
    adduser -D -u 1001 -G appgroup appuser

WORKDIR /app

# JAR 파일 복사
COPY --from=builder /build/build/libs/*.jar app.jar

RUN chown appuser:appgroup app.jar

USER appuser

EXPOSE 8080

ENTRYPOINT ["sh", "-c", "java ${JAVA_OPTS} -jar app.jar"]
```

---

## 🌟 실생활 비유로 이해하기

### 비유 1: IKEA 가구 조립 설명서

```
[IKEA 조립 설명서]              [Dockerfile]
========================        ========================
1. 부품 목록 확인               FROM ubuntu:20.04
2. 나사 10개 준비               RUN apt-get update
3. 판자 A와 B 결합              RUN apt-get install -y nginx
4. 나사로 고정                  COPY config.json /etc/
5. 손잡이 부착                  CMD ["nginx"]
6. 완성!                        (이미지 생성 완료)

공통점:
- 순서대로 따라하면 누구나 같은 결과
- 단계를 건너뛰면 실패
- 한번 작성하면 반복 사용 가능
```

### 비유 2: 요리 레시피

```
[떡볶이 레시피]                 [Dockerfile]
========================        ========================
재료: 떡, 고추장, 어묵          FROM node:18-alpine (베이스 재료)

1. 물 끓이기                    RUN apt-get update
2. 고추장 넣기                  RUN apt-get install dependencies
3. 떡 넣기                      COPY app.js /app/
4. 10분 끓이기                  RUN npm install
5. 완성                         CMD ["node", "app.js"]

왜 레시피가 필요한가?
- 매번 같은 맛 보장
- 다른 사람도 똑같이 만들 수 있음
- 실수 방지
```

### 비유 3: 건축 설계도

```
[아파트 설계도]                 [Dockerfile]
========================        ========================
기초 공사 (철근 배치)           FROM ubuntu:20.04
벽 세우기                       RUN apt-get install packages
전기 배선                       COPY source code
수도 배관                       ENV NODE_ENV=production
내부 인테리어                   WORKDIR /app
입주 가능                       CMD ["start-app"]

공통점:
- 설계도 없이는 건축 불가능
- 모든 작업이 순서대로 진행
- 검증된 설계로 안정성 보장
```

### 비유 4: 게임 캐릭터 생성

```
[게임 캐릭터 커스터마이징]      [Dockerfile]
========================        ========================
1. 기본 종족 선택               FROM python:3.11
   (인간/엘프/드워프)
2. 스탯 분배                    ENV MEMORY=512MB
   (힘/민첩/지능)
3. 스킬 배우기                  RUN pip install packages
   (검술/마법/암살)
4. 장비 착용                    COPY gear.txt /inventory/
   (갑옷/무기/방패)
5. 게임 시작                    CMD ["start-game"]

공통점:
- 템플릿 기반 커스터마이징
- 설정 저장 후 재사용 가능
- 같은 설정으로 무한 복제
```

### 비유 5: 프랜차이즈 매뉴얼

```
[스타벅스 매장 개점 매뉴얼]     [Dockerfile]
========================        ========================
1. 표준 인테리어 설치           FROM baseimage
2. 커피 머신 배치               RUN install-machines
3. 재료 준비                    COPY ingredients/
4. 직원 교육                    RUN train-staff
5. 영업 시작                    CMD ["open-store"]

왜 프랜차이즈 매뉴얼인가?
- 전세계 어디서나 같은 품질
- 신입도 매뉴얼만 보면 OK
- 성공 패턴 공유
```

### 비유 6: 음반 제작 마스터링

```
[음반 마스터 제작]              [Dockerfile]
========================        ========================
1. 원본 녹음본 준비             FROM audio-base
2. 노이즈 제거                  RUN remove-noise
3. 음량 균형 조정               RUN normalize-volume
4. 이퀄라이저 적용              ENV EQ=pop-preset
5. 최종 마스터 생성             CMD ["export-master"]
6. 대량 복제                    docker build (여러 장 제작)

공통점:
- 마스터 1개 → 무한 복제
- 품질 일정
- 수정은 마스터만 변경
```

### 🎯 종합 비교표

| 개념 | IKEA 설명서 | 요리 레시피 | 프랜차이즈 매뉴얼 | Dockerfile |
|------|-------------|------------|------------------|------------|
| **준비물** | 부품 목록 | 재료 | 장비 리스트 | FROM (베이스 이미지) |
| **작업 과정** | 조립 단계 | 조리 순서 | 개점 절차 | RUN/COPY 명령어 |
| **최종 결과** | 완성된 가구 | 완성된 요리 | 오픈한 매장 | Docker 이미지 |
| **재사용성** | 여러 번 조립 | 여러 번 조리 | 여러 지점 오픈 | 여러 컨테이너 생성 |
| **일관성** | 항상 같은 모양 | 항상 같은 맛 | 항상 같은 품질 | 항상 같은 환경 |

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: 캐시가 안 먹혀요!

**상황**: 코드만 살짝 수정했는데 npm install이 매번 실행되어 빌드가 너무 느립니다.

```dockerfile
# ❌ 주니어 개발자가 작성한 코드
FROM node:18-alpine
WORKDIR /app

# 모든 파일을 먼저 복사
COPY . .

# npm install 실행
RUN npm install

CMD ["npm", "start"]
```

**문제점**:
- 소스 코드가 변경될 때마다 `COPY . .`가 변경됨
- Docker는 이 레이어 이후의 모든 캐시를 무효화
- `npm install`이 매번 재실행 (2-5분 소요)
- 개발 속도 심각하게 저하

**해결책**:
```dockerfile
# ✅ 올바른 코드
FROM node:18-alpine
WORKDIR /app

# 1단계: 의존성 파일만 먼저 복사
COPY package.json package-lock.json ./

# 2단계: 의존성 설치 (package.json 변경 시에만 재실행)
RUN npm ci --only=production

# 3단계: 소스 코드 복사 (자주 변경됨)
COPY . .

CMD ["npm", "start"]
```

**효과**:
```bash
# 첫 번째 빌드
docker build -t myapp:1.0 .
# => npm ci: 120초 소요

# 소스 코드만 수정 후 재빌드
docker build -t myapp:1.1 .
# => npm ci: 0.1초 (캐시 사용!)
# => 전체 빌드: 5초 완료

# 시간 절약: 115초 (96%↓)
```

**배운 점**:
- 💡 **레이어 순서가 중요**: 자주 변경되는 파일은 Dockerfile 하단에 배치
- 💡 **의존성과 소스 코드 분리**: 의존성은 거의 변경되지 않으므로 먼저 설치
- 💡 **캐시 활용이 성능의 핵심**: 빌드 시간 90% 이상 단축 가능

---

### 시나리오 2: 이미지가 너무 커요!

**상황**: Node.js 앱을 Docker 이미지로 만들었는데 1.5GB나 됩니다. 배포가 너무 느립니다.

```dockerfile
# ❌ 주니어 개발자가 작성한 코드
FROM node:18
WORKDIR /app
COPY . .
RUN npm install
CMD ["npm", "start"]
```

**결과**:
```bash
REPOSITORY    TAG       SIZE
myapp         latest    1.52GB  # 😱 너무 큼!
```

**문제점**:
- `node:18` 이미지는 모든 빌드 도구 포함 (gcc, python 등)
- `npm install`은 개발 의존성도 설치 (devDependencies)
- npm 캐시가 이미지에 포함됨
- 불필요한 파일들 (node_modules, .git 등) 모두 포함

**해결책 1단계: alpine 사용 + 프로덕션 의존성만**
```dockerfile
# ✅ 개선 버전 1
FROM node:18-alpine  # alpine: 작은 베이스 이미지
WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production \  # 프로덕션 의존성만
 && npm cache clean --force      # 캐시 정리

COPY . .
CMD ["node", "server.js"]
```

**결과**:
```bash
REPOSITORY    TAG       SIZE
myapp         v1        580MB   # 62% 감소!
```

**해결책 2단계: 멀티스테이지 빌드**
```dockerfile
# ✅ 최종 버전 (멀티스테이지)
# Stage 1: 빌드 단계
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Stage 2: 실행 단계 (빌드 결과물만 복사)
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package.json .

CMD ["node", "dist/server.js"]
```

**최종 결과**:
```bash
REPOSITORY    TAG       SIZE
myapp         v1        580MB   (alpine만 사용)
myapp         v2        142MB   (멀티스테이지) # 91% 감소! 🎉
```

**배운 점**:
- 💡 **alpine 이미지 사용**: 베이스 이미지 크기 80% 감소
- 💡 **멀티스테이지 빌드**: 빌드 도구 제외, 실행 파일만 포함
- 💡 **캐시 정리**: `npm cache clean`, `apt-get clean` 필수
- 💡 **.dockerignore 활용**: 불필요한 파일 제외

---

### 시나리오 3: root 권한으로 실행하면 안 된다고요?

**상황**: 보안 감사에서 컨테이너가 root로 실행된다고 지적받았습니다.

```dockerfile
# ❌ 주니어 개발자가 작성한 코드
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install
EXPOSE 3000
CMD ["npm", "start"]
```

**문제 확인**:
```bash
docker run -d --name myapp myapp:latest

# 컨테이너 내부 사용자 확인
docker exec myapp whoami
# 출력: root  😱 보안 위험!

# 프로세스 확인
docker exec myapp ps aux
# USER   PID  COMMAND
# root   1    node server.js  # root로 실행 중!
```

**위험성**:
- 컨테이너가 해킹당하면 root 권한 획득
- 호스트 시스템 침입 가능성
- 규정 위반 (보안 정책)

**해결책**:
```dockerfile
# ✅ 올바른 코드
FROM node:18-alpine

# 일반 사용자 생성 (Alpine Linux 방식)
RUN addgroup -g 1001 appgroup && \
    adduser -D -u 1001 -G appgroup appuser

WORKDIR /app

# 파일 복사 (소유권 변경)
COPY --chown=appuser:appgroup package*.json ./

# root 권한이 필요한 작업 (사용자 전환 전)
RUN npm ci --only=production

# 소스 복사
COPY --chown=appuser:appgroup . .

# 일반 사용자로 전환 (이 이후 모든 명령은 appuser로 실행)
USER appuser

EXPOSE 3000
CMD ["node", "server.js"]
```

**검증**:
```bash
docker build -t myapp:secure .
docker run -d --name myapp-secure myapp:secure

# 사용자 확인
docker exec myapp-secure whoami
# 출력: appuser  ✅ 안전!

# 프로세스 확인
docker exec myapp-secure ps aux
# USER      PID  COMMAND
# appuser   1    node server.js  ✅ 일반 사용자로 실행!
```

**추가 팁: 파일 권한 문제 해결**
```dockerfile
# 문제: 로그 파일 쓰기 권한 없음
FROM node:18-alpine
RUN addgroup -g 1001 appgroup && \
    adduser -D -u 1001 -G appgroup appuser

WORKDIR /app
COPY --chown=appuser:appgroup . .

# 로그 디렉토리 생성 및 권한 설정
RUN mkdir -p /app/logs && \
    chown -R appuser:appgroup /app/logs

USER appuser

CMD ["node", "server.js"]
```

**배운 점**:
- 💡 **항상 일반 사용자로 실행**: 보안 기본 원칙
- 💡 **root 작업은 USER 전에 완료**: 패키지 설치 등
- 💡 **파일 소유권 주의**: `--chown` 플래그 사용
- 💡 **디렉토리 권한 사전 설정**: 쓰기 권한 필요한 곳은 미리 생성

---

### 시나리오 4: 환경변수를 Dockerfile에 하드코딩했어요

**상황**: 개발/스테이징/프로덕션 환경별로 Dockerfile을 3개 만들어야 할까요?

```dockerfile
# ❌ 주니어 개발자가 작성한 코드 (하드코딩)
FROM node:18-alpine
WORKDIR /app

# 환경 변수 하드코딩 😱
ENV DATABASE_HOST=prod-db.example.com
ENV DATABASE_PORT=5432
ENV DATABASE_NAME=production_db
ENV API_KEY=sk_live_abc123xyz  # 보안 위험!

COPY . .
RUN npm ci
CMD ["npm", "start"]
```

**문제점**:
- 환경별로 다른 Dockerfile 필요 (유지보수 지옥)
- API 키가 이미지에 노출 (보안 위험)
- Git에 민감 정보 커밋 (규정 위반)
- 환경 변경 시 이미지 재빌드 필요

**해결책 1: 런타임 환경변수 사용**
```dockerfile
# ✅ 올바른 코드 (기본값만 제공)
FROM node:18-alpine
WORKDIR /app

# 기본값 설정 (런타임에 오버라이드 가능)
ENV NODE_ENV=production
ENV PORT=3000
# 민감한 정보는 기본값 제공 안 함!

COPY package*.json ./
RUN npm ci --only=production
COPY . .

EXPOSE ${PORT}
CMD ["node", "server.js"]
```

**사용법**:
```bash
# 개발 환경
docker run -d \
  -e NODE_ENV=development \
  -e DATABASE_HOST=dev-db.local \
  -e DATABASE_PORT=5432 \
  -e API_KEY=sk_test_dev123 \
  myapp:latest

# 프로덕션 환경
docker run -d \
  -e NODE_ENV=production \
  -e DATABASE_HOST=prod-db.example.com \
  -e DATABASE_PORT=5432 \
  -e API_KEY=sk_live_prod456 \
  myapp:latest

# 같은 이미지로 모든 환경 대응! 🎉
```

**해결책 2: .env 파일 사용**
```bash
# dev.env
NODE_ENV=development
DATABASE_HOST=dev-db.local
API_KEY=sk_test_dev123

# prod.env
NODE_ENV=production
DATABASE_HOST=prod-db.example.com
API_KEY=sk_live_prod456
```

```bash
# 개발 환경 실행
docker run -d --env-file dev.env myapp:latest

# 프로덕션 환경 실행
docker run -d --env-file prod.env myapp:latest
```

**해결책 3: Docker Compose 활용**
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    image: myapp:latest
    environment:
      - NODE_ENV=${ENVIRONMENT:-production}
      - DATABASE_HOST=${DB_HOST}
      - API_KEY=${API_KEY}
    env_file:
      - .env
```

**해결책 4: 시크릿 관리 (프로덕션)**
```bash
# Docker Swarm secrets
echo "sk_live_prod456" | docker secret create api_key -

# 컨테이너에서 사용
docker service create \
  --name myapp \
  --secret api_key \
  myapp:latest

# 컨테이너 내부에서 /run/secrets/api_key로 접근
```

**배운 점**:
- 💡 **Dockerfile에 민감 정보 금지**: 기본값만 제공
- 💡 **런타임 환경변수 활용**: `-e` 플래그 또는 `--env-file`
- 💡 **환경별 이미지 분리 불필요**: 하나의 이미지로 모든 환경 대응
- 💡 **시크릿 관리 도구 사용**: 프로덕션에서는 Docker Secrets, Kubernetes Secrets 등

---

## ❓ FAQ

<details>
<summary><strong>Q1: FROM에서 latest 태그를 사용하면 안 되나요?</strong></summary>

**A**: 프로덕션에서는 절대 사용하지 마세요!

**상세 설명**:
- **문제점 1**: `latest`는 고정된 버전이 아님
  - 오늘 빌드: `node:latest` → v18.0.0
  - 1주 후 빌드: `node:latest` → v19.0.0 (자동 업데이트)
  - 결과: 갑자기 앱이 안 돌아감

- **문제점 2**: 재현 불가능
  - 팀원 A의 환경: `node:latest` = v18
  - 팀원 B의 환경: `node:latest` = v19
  - "내 컴퓨터에서는 되는데요?" 상황 발생

- **문제점 3**: 롤백 불가능
  - 어떤 버전으로 빌드했는지 알 수 없음
  - 문제 발생 시 원인 파악 어려움

**올바른 방법**:
```dockerfile
# ❌ 나쁜 예
FROM node:latest

# ✅ 좋은 예 (정확한 버전 명시)
FROM node:18.19.0-alpine3.18

# ✅ 허용 가능 (메이저 버전만 고정)
FROM node:18-alpine  # 18.x 최신 버전
```

**실무 팁**:
💡 개발 환경에서는 `18-alpine` 정도로 사용해도 OK
💡 프로덕션에서는 반드시 전체 버전 명시 (18.19.0-alpine3.18)

</details>

<details>
<summary><strong>Q2: RUN 명령어를 여러 번 쓰는 것과 한 번에 쓰는 것 중 어느 게 좋나요?</strong></summary>

**A**: 한 번에 체이닝하는 것이 90% 상황에서 더 좋습니다!

**상세 설명**:

**이유 1: 레이어 수 감소**
```dockerfile
# ❌ 나쁜 예 (4개 레이어)
RUN apt-get update
RUN apt-get install -y nginx
RUN apt-get install -y curl
RUN apt-get clean

# 이미지 크기: 각 레이어마다 메타데이터 추가
# 레이어 4개 = 메타데이터 4배
```

```dockerfile
# ✅ 좋은 예 (1개 레이어)
RUN apt-get update \
 && apt-get install -y nginx curl \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# 이미지 크기: 최적화됨
# 레이어 1개 = 메타데이터 최소화
```

**이유 2: 캐시 문제 방지**
```dockerfile
# ❌ 위험한 패턴
RUN apt-get update
RUN apt-get install -y nginx  # 캐시 사용

# 문제: 나중에 nginx를 curl로 변경하면?
RUN apt-get update  # 캐시 사용 (오래된 패키지 목록)
RUN apt-get install -y curl  # curl이 안 깔릴 수 있음!
```

```dockerfile
# ✅ 안전한 패턴
RUN apt-get update && apt-get install -y curl
# update와 install이 항상 함께 실행됨
```

**이유 3: 중간 파일 정리**
```dockerfile
# ❌ 비효율적
RUN curl -O https://example.com/big-file.tar.gz
RUN tar -xzf big-file.tar.gz
RUN rm big-file.tar.gz  # 삭제해도 이미지 크기 안 줄어듬!
# 이유: 각 RUN은 별도 레이어, 이전 레이어는 변경 불가

# ✅ 효율적
RUN curl -O https://example.com/big-file.tar.gz \
 && tar -xzf big-file.tar.gz \
 && rm big-file.tar.gz
# 같은 레이어에서 삭제하면 실제로 이미지 크기 감소!
```

**예외: 언제 분리하나?**
```dockerfile
# ✅ 의존성과 소스를 분리 (캐시 효율)
COPY package.json .
RUN npm install  # 레이어 1: 자주 변경 안 됨

COPY . .
RUN npm run build  # 레이어 2: 자주 변경됨
```

**실무 팁**:
💡 패키지 설치는 항상 체이닝
💡 의존성 설치와 소스 빌드는 분리
💡 한 줄이 너무 길면 `\`로 여러 줄 작성

</details>

<details>
<summary><strong>Q3: COPY와 ADD의 차이가 뭔가요? 언제 ADD를 써야 하나요?</strong></summary>

**A**: 99%는 COPY를 쓰세요! ADD는 특수한 경우만 사용합니다.

**차이점**:

| 기능 | COPY | ADD |
|------|------|-----|
| 파일 복사 | ✅ | ✅ |
| 디렉토리 복사 | ✅ | ✅ |
| tar 자동 압축 해제 | ❌ | ✅ |
| URL 다운로드 | ❌ | ✅ (비권장) |
| 예측 가능성 | 높음 | 낮음 |

**COPY 사용 (권장)**:
```dockerfile
# ✅ 명확하고 예측 가능
COPY package.json .
COPY src/ ./src/
COPY config/ ./config/
```

**ADD 사용 (특수 케이스)**:
```dockerfile
# ✅ tar 파일 자동 압축 해제
ADD app-release.tar.gz /opt/app/
# app-release.tar.gz가 /opt/app/에 자동으로 풀림
```

**ADD 피해야 하는 경우**:
```dockerfile
# ❌ URL 다운로드 (비권장)
ADD https://example.com/file.zip /tmp/
# 문제점:
# - 캐시가 제대로 안 됨
# - 파일 크기를 빌드 전에 알 수 없음
# - 네트워크 오류 처리 어려움

# ✅ 대신 RUN + curl 사용
RUN curl -fsSL https://example.com/file.zip -o /tmp/file.zip \
 && unzip /tmp/file.zip -d /app \
 && rm /tmp/file.zip
```

**혼란스러운 케이스**:
```dockerfile
# 로컬에 app.tar.gz 파일이 있을 때

# ADD 사용 시
ADD app.tar.gz /app/
# 결과: /app/에 압축 해제됨

# COPY 사용 시
COPY app.tar.gz /app/
# 결과: /app/app.tar.gz 파일로 복사됨 (압축 해제 안 됨)
```

**실무 팁**:
💡 기본은 COPY 사용
💡 tar 파일 자동 압축 해제만 ADD 사용
💡 URL 다운로드는 RUN + curl 사용

</details>

<details>
<summary><strong>Q4: CMD와 ENTRYPOINT 차이를 쉽게 설명해주세요!</strong></summary>

**A**: CMD는 "기본 명령", ENTRYPOINT는 "고정 명령"입니다!

**쉬운 비유**:
```
CMD: 기본 목적지가 설정된 택시
     → 다른 곳으로 가고 싶으면 목적지 변경 가능

ENTRYPOINT: 정해진 노선만 다니는 버스
     → 노선은 고정, 정류장만 선택 가능
```

**실전 예시**:

**패턴 1: CMD만 사용**
```dockerfile
FROM ubuntu:20.04
CMD ["echo", "Hello"]
```

```bash
docker run myimage
# 출력: Hello

docker run myimage echo "Goodbye"
# 출력: Goodbye
# CMD가 완전히 무시됨
```

**패턴 2: ENTRYPOINT만 사용**
```dockerfile
FROM ubuntu:20.04
ENTRYPOINT ["echo"]
```

```bash
docker run myimage "Hello"
# 출력: Hello

docker run myimage "Goodbye"
# 출력: Goodbye
# ENTRYPOINT는 유지, 매개변수만 변경됨
```

**패턴 3: ENTRYPOINT + CMD (최고의 조합!)**
```dockerfile
FROM alpine:3.18
ENTRYPOINT ["ping", "-c", "3"]
CMD ["google.com"]
```

```bash
# 기본 실행 (CMD 사용)
docker run myimage
# 실행: ping -c 3 google.com

# 다른 호스트 (CMD 오버라이드)
docker run myimage naver.com
# 실행: ping -c 3 naver.com

# ENTRYPOINT는 항상 유지!
```

**실무 예시: CLI 도구**
```dockerfile
FROM python:3.11-slim
COPY mytool.py /usr/local/bin/mytool
ENTRYPOINT ["python", "/usr/local/bin/mytool"]
CMD ["--help"]
```

```bash
# 도움말 (기본)
docker run mytool
# 실행: python mytool --help

# 특정 명령
docker run mytool process --file data.csv
# 실행: python mytool process --file data.csv

# 버전 확인
docker run mytool --version
# 실행: python mytool --version
```

**선택 가이드**:

| 상황 | 추천 | 이유 |
|------|------|------|
| 단일 앱 실행 | CMD | 유연성 제공 |
| CLI 도구 | ENTRYPOINT + CMD | 직관적 사용 |
| 초기화 스크립트 필요 | ENTRYPOINT (스크립트) + CMD | 복잡한 로직 처리 |

**실무 팁**:
💡 일반적인 웹 앱: CMD 사용
💡 CLI 도구: ENTRYPOINT + CMD 조합
💡 Exec 형식 사용 (시그널 처리 때문)

</details>

<details>
<summary><strong>Q5: 멀티스테이지 빌드가 뭐고 왜 써야 하나요?</strong></summary>

**A**: 빌드 도구는 빼고 실행 파일만 담아서 이미지 크기를 90% 줄이는 기법입니다!

**문제 상황**:
```dockerfile
# ❌ 단일 스테이지 (모든 것 포함)
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install  # node_modules: 200MB
COPY . .
RUN npm run build  # build 도구: 150MB
CMD ["node", "dist/server.js"]

# 최종 이미지:
# - Node.js: 900MB
# - node_modules (전체): 200MB
# - build 도구: 150MB
# - 소스 코드: 50MB
# 총: 1.3GB 😱
```

**해결: 멀티스테이지**
```dockerfile
# ✅ 멀티스테이지 (필요한 것만)
# Stage 1: 빌드 (임시)
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
# 이 단계는 최종 이미지에 포함 안 됨!

# Stage 2: 실행 (최종 이미지)
FROM node:18-alpine
WORKDIR /app
# builder 단계에서 필요한 것만 복사
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package.json .
CMD ["node", "dist/server.js"]

# 최종 이미지:
# - Node.js (alpine): 150MB
# - node_modules (프로덕션만): 50MB
# - 빌드 결과물: 10MB
# 총: 210MB ✅ (84% 감소!)
```

**동작 원리**:
```
[Stage 1: builder]
├─ node:18 (900MB)
├─ node_modules (200MB)
├─ build tools (150MB)
├─ src/ (50MB)
└─ dist/ (10MB) ← 이것만 복사

         ↓

[Stage 2: 최종 이미지]
├─ node:18-alpine (150MB)
├─ node_modules/production (50MB)
└─ dist/ (10MB) ← builder에서 복사
총: 210MB

[Stage 1은 버려짐!]
```

**실전 예시: Go 앱 (극적인 효과)**
```dockerfile
# Stage 1: 빌드
FROM golang:1.21 AS builder
WORKDIR /app
COPY . .
RUN go build -o myapp

# Stage 2: 실행 (scratch = 완전히 빈 이미지!)
FROM scratch
COPY --from=builder /app/myapp /myapp
ENTRYPOINT ["/myapp"]

# 최종 이미지: 5MB! (단일 스테이지: 800MB)
```

**언제 사용하나?**

| 상황 | 단일 스테이지 | 멀티 스테이지 |
|------|--------------|--------------|
| 빌드 도구 필요 (npm, maven, go) | ❌ 1GB+ | ✅ 100MB |
| 개발 의존성 많음 | ❌ 포함됨 | ✅ 제외됨 |
| 이미지 크기 중요 | ❌ | ✅ |
| 빌드 시간 중요 | ✅ (약간 빠름) | ⚠️ (약간 느림) |

**실무 팁**:
💡 프로덕션 이미지는 무조건 멀티스테이지
💡 빌드 스테이지에는 일반 이미지, 실행 스테이지에는 alpine
💡 보안도 좋아짐 (빌드 도구 없어서 공격 표면 감소)

</details>

<details>
<summary><strong>Q6: .dockerignore는 꼭 필요한가요?</strong></summary>

**A**: 필수입니다! 빌드 시간과 이미지 크기를 극적으로 줄여줍니다.

**문제 상황**:
```bash
# .dockerignore 없이 빌드
docker build -t myapp .
# Sending build context to Docker daemon  1.2GB
# Step 1/5 : FROM node:18-alpine
# ... (3분 소요)

# 왜 1.2GB?
# - node_modules: 800MB
# - .git: 200MB
# - dist/: 150MB
# - logs/: 50MB
```

**.dockerignore 생성**:
```
# .dockerignore (프로젝트 루트에 생성)

# 의존성 (Dockerfile에서 설치)
node_modules/
npm-debug.log
yarn-error.log

# Git
.git/
.gitignore

# 빌드 결과물
dist/
build/
target/

# 로그
*.log
logs/

# 테스트
coverage/
.nyc_output/

# IDE
.vscode/
.idea/
*.swp
*.swo

# 환경 설정
.env
.env.local
.env.*.local

# OS
.DS_Store
Thumbs.db

# 문서
README.md
CHANGELOG.md
docs/
```

**효과**:
```bash
# .dockerignore 적용 후 빌드
docker build -t myapp .
# Sending build context to Docker daemon  5.3MB  ✅ (99.5% 감소!)
# Step 1/5 : FROM node:18-alpine
# ... (15초 소요)  ✅ (92% 단축!)
```

**작동 원리**:
```
[빌드 컨텍스트 생성]
project/
├─ node_modules/     ← .dockerignore: 제외
├─ .git/             ← .dockerignore: 제외
├─ src/              ← 포함됨
├─ package.json      ← 포함됨
└─ Dockerfile        ← 포함됨

         ↓
[Docker 데몬으로 전송]
5.3MB만 전송! (1.2GB 대신)
```

**Git과의 차이**:
```
.gitignore          .dockerignore
──────────          ─────────────
Git 추적 제외       Docker 빌드 제외
node_modules        node_modules
dist/               dist/
.env                .env
                    Dockerfile (포함)
                    .dockerignore (포함)
```

**실무 패턴**:
```
# .dockerignore 템플릿 (Node.js)
node_modules/
npm-debug.log*
.npm
.git/
.env*
dist/
build/
coverage/
*.md
.vscode/
.idea/

# .dockerignore 템플릿 (Python)
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.venv/
venv/
.git/
.env
*.md
.vscode/

# .dockerignore 템플릿 (Java)
target/
.gradle/
build/
.git/
.env
*.md
.idea/
.vscode/
```

**실무 팁**:
💡 프로젝트 시작 시 바로 생성
💡 .gitignore와 유사하게 작성
💡 빌드 시간 90% 이상 단축 가능

</details>

<details>
<summary><strong>Q7: ENV와 ARG의 차이는 뭔가요?</strong></summary>

**A**: ARG는 빌드 타임, ENV는 런타임입니다!

**핵심 차이**:

| 특성 | ARG | ENV |
|------|-----|-----|
| **사용 시점** | docker build | docker run |
| **컨테이너에 남는가** | ❌ (빌드 후 사라짐) | ✅ (컨테이너 실행 중 유지) |
| **오버라이드** | --build-arg | -e, --env |
| **용도** | 빌드 설정 | 앱 설정 |

**실전 예시**:

**ARG 사용 (빌드 타임)**:
```dockerfile
# Dockerfile
ARG NODE_VERSION=18
FROM node:${NODE_VERSION}-alpine

ARG BUILD_ENV=production
RUN if [ "$BUILD_ENV" = "development" ]; then \
      apk add --no-cache vim curl; \
    fi

# ARG는 여기서 끝 (컨테이너에 남지 않음)
```

```bash
# 빌드 시 변경
docker build --build-arg NODE_VERSION=20 --build-arg BUILD_ENV=development -t myapp:dev .
docker build --build-arg NODE_VERSION=18 --build-arg BUILD_ENV=production -t myapp:prod .

# 컨테이너에서 확인
docker run myapp:dev printenv BUILD_ENV
# 출력: (없음) ← ARG는 빌드 후 사라짐!
```

**ENV 사용 (런타임)**:
```dockerfile
# Dockerfile
FROM node:18-alpine

ENV NODE_ENV=production
ENV PORT=3000
ENV LOG_LEVEL=info

CMD ["node", "server.js"]
```

```bash
# 런타임에 변경
docker run -e NODE_ENV=development -e PORT=8080 myapp

# 컨테이너에서 확인
docker run myapp printenv NODE_ENV
# 출력: production (ENV 값 유지됨)

# 오버라이드
docker run -e NODE_ENV=development myapp printenv NODE_ENV
# 출력: development
```

**조합 사용 (권장 패턴)**:
```dockerfile
# Dockerfile
# ARG로 빌드 설정
ARG BUILD_VERSION=1.0.0
ARG NODE_VERSION=18

# ENV로 런타임 설정
FROM node:${NODE_VERSION}-alpine

ENV APP_VERSION=${BUILD_VERSION}
ENV NODE_ENV=production
ENV PORT=3000

LABEL version="${APP_VERSION}"

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE ${PORT}
CMD ["node", "server.js"]
```

```bash
# 빌드 (ARG 사용)
docker build \
  --build-arg BUILD_VERSION=2.0.0 \
  --build-arg NODE_VERSION=20 \
  -t myapp:2.0.0 .

# 실행 (ENV 오버라이드)
docker run \
  -e NODE_ENV=development \
  -e PORT=8080 \
  myapp:2.0.0

# 컨테이너 내부에서
printenv APP_VERSION  # 2.0.0 (빌드 시 ARG → ENV 변환)
printenv NODE_ENV     # development (런타임 오버라이드)
```

**보안 주의사항**:
```dockerfile
# ❌ 위험: ARG에 비밀 정보
ARG DATABASE_PASSWORD=secret123
RUN echo "DB_PASS=${DATABASE_PASSWORD}" > /app/config

# 문제: docker history로 비밀번호 노출됨!
# docker history myapp
# ... ARG DATABASE_PASSWORD=secret123

# ✅ 안전: 런타임에만 주입
# Dockerfile에는 넣지 않음
```

```bash
# 런타임에 시크릿 주입
docker run -e DATABASE_PASSWORD=secret123 myapp
# 또는
docker run --env-file secrets.env myapp
```

**실무 팁**:
💡 빌드 옵션 → ARG (이미지 버전, 빌드 플래그)
💡 앱 설정 → ENV (포트, 로그 레벨, 환경)
💡 비밀번호/API 키 → 런타임에 주입 (Dockerfile에 넣지 않기!)

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. Dockerfile이 무엇이고 왜 사용하나요?</strong></summary>

**모범 답안 포인트**
- Docker 이미지를 생성하기 위한 자동화 스크립트
- 인프라를 코드로 관리 (Infrastructure as Code)
- 재현 가능한 환경 보장
- 버전 관리 가능

**예시 답변**
> "Dockerfile은 Docker 이미지를 자동으로 생성하기 위한 텍스트 파일입니다. 마치 요리 레시피처럼 베이스 이미지 선택부터 패키지 설치, 파일 복사, 실행 명령까지 모든 과정을 순서대로 정의합니다. Dockerfile을 사용하면 누가 만들어도 동일한 환경이 만들어지고, Git으로 버전 관리도 가능하며, 수동 작업에 비해 실수를 줄일 수 있습니다."

**꼬리 질문**
- Q: Dockerfile 없이 docker commit으로 이미지를 만들 수도 있는데 왜 Dockerfile을 써야 하나요?
- A: docker commit은 수동 작업의 결과물이라 재현이 어렵고, 어떤 과정을 거쳤는지 알 수 없으며, 버전 관리가 불가능합니다. Dockerfile은 모든 과정이 코드로 문서화되어 있어 투명하고 재현 가능합니다.

**실무 연관**
- 실무에서는 Dockerfile을 Git 저장소에 함께 관리하여 코드와 인프라를 동시에 버전 관리합니다.
- CI/CD 파이프라인에서 Dockerfile을 자동으로 빌드하여 배포합니다.

</details>

<details>
<summary><strong>2. FROM 명령어에서 alpine 이미지를 주로 사용하는 이유는?</strong></summary>

**모범 답안 포인트**
- 매우 작은 크기 (5MB 수준)
- 보안 취약점 최소화
- 빠른 다운로드 및 배포
- 프로덕션 환경에 최적

**예시 답변**
> "alpine 이미지는 Alpine Linux 기반의 초경량 Docker 이미지입니다. 일반 ubuntu 이미지가 100MB 이상인 데 비해 alpine은 5MB 정도로 매우 작습니다. 크기가 작아서 다운로드와 배포가 빠르고, 포함된 패키지가 적어 보안 취약점도 줄어듭니다. 프로덕션 환경에서는 node:18-alpine, python:3.11-alpine처럼 alpine 버전을 주로 사용합니다."

**꼬리 질문**
- Q: alpine의 단점은 없나요?
- A: musl libc를 사용해서 일부 바이너리와 호환성 문제가 있을 수 있고, 디버깅 도구가 기본으로 포함되지 않아 문제 해결이 어려울 수 있습니다. 개발 환경에서는 일반 이미지를 쓰고 프로덕션에서만 alpine을 사용하는 것도 방법입니다.

**실무 연관**
- 이미지 크기 차이가 배포 시간에 직접적 영향: 1GB 이미지 vs 100MB 이미지는 10배 차이
- 보안 스캔 시 alpine 이미지가 취약점 수가 현저히 적음

</details>

<details>
<summary><strong>3. RUN, CMD, ENTRYPOINT의 차이를 설명해주세요.</strong></summary>

**모범 답안 포인트**
- RUN: 빌드 타임에 실행 (이미지 레이어 생성)
- CMD: 컨테이너 시작 시 실행 (오버라이드 가능)
- ENTRYPOINT: 컨테이너 시작 시 실행 (고정 명령)

**예시 답변**
> "RUN은 docker build 시점에 명령을 실행하고 그 결과를 이미지 레이어에 저장합니다. 주로 패키지 설치에 사용됩니다. CMD는 docker run 시점에 실행할 기본 명령을 지정하며, 사용자가 docker run 명령에서 다른 명령을 주면 오버라이드됩니다. ENTRYPOINT는 CMD와 비슷하지만 항상 실행되는 고정 명령입니다. 실무에서는 ENTRYPOINT에 실행 파일을 지정하고 CMD에 기본 인자를 지정하는 조합을 많이 씁니다."

**꼬리 질문**
- Q: CMD와 ENTRYPOINT를 함께 사용하면 어떻게 되나요?
- A: ENTRYPOINT가 실행 파일이 되고 CMD가 인자가 됩니다. 예를 들어 `ENTRYPOINT ["ping"]`과 `CMD ["google.com"]`이면 `ping google.com`이 실행되고, docker run 시 `naver.com`을 주면 `ping naver.com`이 실행됩니다.

**실무 연관**
- CLI 도구 이미지: ENTRYPOINT + CMD 조합으로 사용자 친화적 인터페이스 제공
- 웹 앱: CMD만 사용하여 유연성 확보

</details>

<details>
<summary><strong>4. COPY와 ADD의 차이는 무엇이며 언제 각각 사용하나요?</strong></summary>

**모범 답안 포인트**
- COPY: 단순 파일 복사만
- ADD: 복사 + tar 자동 압축 해제 + URL 다운로드
- 일반적으로 COPY 권장
- tar 압축 해제만 ADD 사용

**예시 답변**
> "COPY는 로컬 파일을 이미지로 복사하는 단순한 명령입니다. ADD는 COPY의 기능에 더해 tar 파일을 자동으로 압축 해제하고 URL에서 파일을 다운로드하는 기능이 있습니다. 하지만 ADD의 추가 기능은 예측하기 어렵고 의도치 않은 동작을 할 수 있어서, 일반적으로는 COPY를 사용하고 tar 파일 압축 해제가 필요한 경우만 ADD를 사용합니다. URL 다운로드는 RUN curl을 사용하는 것이 더 명확합니다."

**꼬리 질문**
- Q: 왜 ADD의 URL 다운로드 기능은 비권장인가요?
- A: 빌드 캐시가 제대로 작동하지 않고, 다운로드 실패 시 에러 처리가 어려우며, 파일 크기를 미리 알 수 없어 예측이 어렵습니다. RUN + curl을 사용하면 에러 처리와 다운로드 후 정리 작업을 명확하게 할 수 있습니다.

**실무 연관**
- 소스 코드 복사: 항상 COPY 사용
- 릴리스 tar.gz 배포: ADD로 자동 압축 해제

</details>

<details>
<summary><strong>5. Dockerfile에서 레이어 캐싱이 어떻게 작동하나요?</strong></summary>

**모범 답안 포인트**
- 각 명령어가 레이어 생성
- 변경된 레이어부터 재빌드
- 변경되지 않은 레이어는 캐시 사용
- 레이어 순서가 중요

**예시 답변**
> "Docker는 Dockerfile의 각 명령어를 실행할 때마다 레이어를 생성하고 캐시합니다. 재빌드 시 이전과 동일한 명령이면 캐시를 재사용하고, 변경된 명령을 만나면 그 시점부터 모든 레이어를 다시 빌드합니다. 예를 들어 소스 코드를 먼저 복사하고 npm install을 하면 코드 변경 시마다 npm install이 재실행되지만, package.json만 먼저 복사해서 npm install하고 나중에 소스를 복사하면 의존성이 변경되지 않는 한 npm install은 캐시를 사용합니다."

**꼬리 질문**
- Q: 캐시를 무효화하고 싶을 때는 어떻게 하나요?
- A: `docker build --no-cache` 옵션을 사용하거나, 특정 시점부터 캐시를 무효화하려면 ARG 값을 변경하는 등의 방법을 사용합니다.

**실무 연관**
- 의존성 파일 먼저 복사 → 설치 → 소스 복사 순서로 빌드 시간 90% 단축 가능

</details>

<details>
<summary><strong>6. .dockerignore 파일은 무엇이며 왜 필요한가요?</strong></summary>

**모범 답안 포인트**
- 빌드 컨텍스트에서 제외할 파일 지정
- .gitignore와 유사한 문법
- 빌드 시간 단축
- 이미지 크기 감소

**예시 답변**
> ".dockerignore는 Docker 빌드 컨텍스트에서 제외할 파일과 디렉토리를 지정하는 파일입니다. .gitignore와 비슷한 문법을 사용하며, node_modules, .git, 로그 파일, 테스트 커버리지 등 불필요한 파일을 빌드에서 제외합니다. 이를 통해 Docker 데몬으로 전송하는 데이터 양이 줄어들어 빌드 시간이 크게 단축되고, 불필요한 파일이 이미지에 포함되지 않아 이미지 크기도 줄어듭니다."

**꼬리 질문**
- Q: .dockerignore에 Dockerfile을 추가하면 어떻게 되나요?
- A: Dockerfile 자체는 자동으로 처리되므로 .dockerignore에 명시적으로 추가해도 빌드에는 영향이 없습니다. 다만 일반적으로 Dockerfile은 제외하지 않습니다.

**실무 연관**
- 대규모 프로젝트에서 .dockerignore 없이 빌드하면 1GB+ 전송, 있으면 10MB 이하로 99% 감소
- node_modules, .git, dist/ 등은 필수 제외 대상

</details>

<details>
<summary><strong>7. USER 명령어로 non-root 사용자를 설정하는 이유는?</strong></summary>

**모범 답안 포인트**
- 보안 강화 (최소 권한 원칙)
- root 권한 획득 방지
- 컨테이너 탈출 시 피해 최소화
- 보안 정책 준수

**예시 답변**
> "컨테이너를 root로 실행하면 컨테이너가 해킹당했을 때 root 권한을 획득할 수 있어 보안 위험이 큽니다. USER 명령어로 일반 사용자를 생성하고 전환하면 최소 권한 원칙에 따라 애플리케이션이 필요한 최소한의 권한만 가지게 됩니다. 이렇게 하면 공격자가 컨테이너를 장악해도 피해 범위가 제한됩니다. 대부분의 보안 정책과 규정에서도 non-root 실행을 요구합니다."

**꼬리 질문**
- Q: 파일 권한 문제가 발생하면 어떻게 해결하나요?
- A: `COPY --chown` 플래그로 복사 시 소유권을 지정하거나, RUN 명령으로 `chown`, `chmod`를 실행해서 권한을 조정합니다. 볼륨 마운트 시에는 호스트의 UID/GID와 맞춰야 할 수도 있습니다.

**실무 연관**
- Kubernetes security context에서도 non-root 실행 강제 가능
- 보안 스캔 도구들이 root 실행을 경고

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. 멀티스테이지 빌드의 동작 원리와 장점을 설명하고, 실제 프로젝트에서 어떻게 활용했나요?</strong></summary>

**모범 답안 포인트**
- 여러 FROM 명령으로 단계 분리
- 빌드 스테이지와 실행 스테이지 분리
- 빌드 도구와 의존성 제외
- 이미지 크기 90% 이상 감소 가능
- 보안 강화 (공격 표면 축소)

**예시 답변**
> "멀티스테이지 빌드는 Dockerfile에 여러 개의 FROM 명령을 사용해서 빌드 과정을 단계별로 나누는 기법입니다. 첫 번째 스테이지에서는 빌드 도구와 개발 의존성을 포함한 큰 이미지로 애플리케이션을 빌드하고, 두 번째 스테이지에서는 작은 베이스 이미지에 빌드 결과물만 복사해서 최종 이미지를 만듭니다. 이전 프로젝트에서 Node.js 앱을 빌드할 때 단일 스테이지는 1.2GB였지만 멀티스테이지로 변경해서 150MB로 줄였고, 빌드 도구가 없어져서 보안 취약점도 40% 감소했습니다."

**실무 예시**
```dockerfile
# Stage 1: 빌드 (큰 이미지 OK)
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install  # devDependencies 포함
COPY . .
RUN npm run build

# Stage 2: 실행 (최소화)
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/server.js"]
```

**꼬리 질문**
- Q: 멀티스테이지 빌드에서 중간 스테이지의 이미지는 어떻게 되나요?
- A: 중간 스테이지는 빌드 캐시에 남지만 최종 이미지에는 포함되지 않습니다. `--target` 옵션으로 특정 스테이지만 빌드할 수도 있어 개발 환경과 프로덕션 환경을 하나의 Dockerfile로 관리할 수 있습니다.

**실무 연관**
- Go 앱: scratch 베이스로 5MB 이하 이미지 가능
- Java 앱: JDK 빌드 → JRE 실행으로 크기 70% 감소
- 빌드 시간은 약간 늘지만 배포 시간은 크게 단축

</details>

<details>
<summary><strong>2. Docker 빌드 캐시를 최대한 활용하기 위한 Dockerfile 작성 전략은?</strong></summary>

**모범 답안 포인트**
- 변경 빈도 낮은 레이어를 상단에 배치
- 의존성 파일과 소스 코드 분리
- RUN 명령 체이닝으로 레이어 최소화
- BuildKit 캐시 마운트 활용

**예시 답변**
> "캐시 효율을 높이려면 변경 빈도가 낮은 명령을 위쪽에 배치해야 합니다. 예를 들어 베이스 이미지 선택, 시스템 패키지 설치, 의존성 파일 복사와 설치를 먼저 하고, 자주 변경되는 소스 코드는 마지막에 복사합니다. 또한 RUN 명령을 체이닝해서 불필요한 레이어 생성을 줄이고, BuildKit을 활성화하면 캐시 마운트 기능으로 npm이나 pip 캐시를 레이어 간에 공유할 수 있습니다. 실제로 이 전략을 적용해서 빌드 시간을 120초에서 8초로 단축했습니다."

**실무 예시**
```dockerfile
# ✅ 캐시 최적화된 구조
FROM node:18-alpine

# 1단계: 시스템 패키지 (거의 변경 안 됨)
RUN apk add --no-cache dumb-init

# 2단계: 의존성 파일만 복사
COPY package.json package-lock.json ./

# 3단계: 의존성 설치 (package.json 변경 시에만 재실행)
RUN npm ci --only=production

# 4단계: 소스 복사 (자주 변경됨)
COPY . .

# BuildKit 캐시 마운트 (추가 최적화)
# RUN --mount=type=cache,target=/root/.npm npm ci
```

**꼬리 질문**
- Q: BuildKit이 무엇이고 어떻게 활성화하나요?
- A: BuildKit은 Docker의 차세대 빌드 엔진으로 병렬 빌드, 캐시 마운트, 시크릿 마운트 등의 기능을 제공합니다. `DOCKER_BUILDKIT=1 docker build` 또는 Docker 데몬 설정에서 활성화할 수 있습니다.

**실무 연관**
- CI/CD에서 캐시 전략이 파이프라인 속도에 직접적 영향
- 레이어 순서 최적화만으로 빌드 시간 90% 단축 가능

</details>

<details>
<summary><strong>3. Dockerfile ARG와 ENV의 차이점과 보안 상 주의사항은?</strong></summary>

**모범 답안 포인트**
- ARG: 빌드 타임, 이미지에 남지 않음
- ENV: 런타임, 컨테이너에 유지됨
- ARG는 docker history에 노출
- 민감 정보는 런타임에 주입

**예시 답변**
> "ARG는 빌드 타임에만 사용되는 변수로 이미지에는 저장되지 않지만 docker history로 볼 수 있어 보안 위험이 있습니다. ENV는 런타임 환경 변수로 컨테이너 실행 중에 유지되며 docker run의 -e 옵션으로 오버라이드할 수 있습니다. 민감 정보는 ARG나 ENV 모두 사용하지 않고, docker run 시 환경변수나 Docker Secrets, Kubernetes Secrets로 주입해야 합니다. 실무에서는 ARG로 빌드 옵션을 설정하고, ENV로 기본값만 제공하며, 실제 값은 배포 시에 주입하는 방식을 사용합니다."

**실무 예시**
```dockerfile
# ARG: 빌드 옵션
ARG NODE_VERSION=18
ARG BUILD_ENV=production

FROM node:${NODE_VERSION}-alpine

# ENV: 런타임 설정 (기본값만)
ENV NODE_ENV=production
ENV PORT=3000
# ❌ ENV DATABASE_PASSWORD=secret  <- 절대 금지!

# ARG를 ENV로 변환 (필요 시)
ARG BUILD_VERSION
ENV APP_VERSION=${BUILD_VERSION}
```

```bash
# 빌드
docker build --build-arg BUILD_VERSION=1.0.0 -t myapp .

# 실행 (민감 정보 주입)
docker run -e DATABASE_PASSWORD=actual_secret myapp
# 또는 시크릿 사용
echo "actual_secret" | docker secret create db_pass -
```

**꼬리 질문**
- Q: docker history로 ARG 값이 노출되는 것을 막을 방법은 없나요?
- A: ARG를 RUN에서 사용하면 history에 남습니다. BuildKit의 `--secret` 옵션을 사용하면 이력에 남지 않고 빌드 시 시크릿을 주입할 수 있습니다.

**실무 연관**
- 보안 감사에서 Dockerfile에 하드코딩된 비밀번호가 가장 흔한 취약점
- 환경별 설정은 Kubernetes ConfigMap/Secret, AWS SSM, HashiCorp Vault 등 활용

</details>

<details>
<summary><strong>4. ENTRYPOINT와 CMD의 Exec 형식과 Shell 형식의 차이와 실무적 의미는?</strong></summary>

**모범 답안 포인트**
- Exec 형식: ["cmd", "arg"]
- Shell 형식: cmd arg
- PID 1 프로세스 차이
- 시그널 처리 차이
- 프로덕션에서는 Exec 형식 권장

**예시 답변**
> "Exec 형식은 JSON 배열로 작성하며 프로세스가 PID 1로 직접 실행됩니다. Shell 형식은 /bin/sh -c로 감싸져서 실행되어 쉘이 PID 1이 됩니다. 이 차이는 시그널 처리에 영향을 줍니다. Exec 형식은 docker stop 시 SIGTERM이 프로세스에 직접 전달되어 graceful shutdown이 가능하지만, Shell 형식은 쉘이 시그널을 받아서 프로세스에 제대로 전달하지 못할 수 있습니다. 실무에서는 항상 Exec 형식을 사용해서 컨테이너가 올바르게 종료되도록 합니다."

**실무 예시**
```dockerfile
# ❌ Shell 형식 (비권장)
CMD node server.js
# 실행: /bin/sh -c "node server.js"
# PID 1 = /bin/sh (시그널 전달 문제)

# ✅ Exec 형식 (권장)
CMD ["node", "server.js"]
# 실행: node server.js
# PID 1 = node (올바른 시그널 처리)

# 환경 변수 필요 시
CMD ["sh", "-c", "node server.js --port ${PORT}"]
```

**검증**:
```bash
docker run -d --name test1 myapp-shell
docker exec test1 ps aux
# PID   COMMAND
# 1     /bin/sh -c node server.js
# 7     node server.js  ← 실제 프로세스

docker run -d --name test2 myapp-exec
docker exec test2 ps aux
# PID   COMMAND
# 1     node server.js  ← PID 1로 직접 실행
```

**꼬리 질문**
- Q: 환경 변수 치환이 필요한데 Exec 형식은 쉘이 없어서 안 되지 않나요?
- A: Exec 형식에서 환경 변수를 사용하려면 `["sh", "-c", "command $VAR"]` 형태로 명시적으로 쉘을 호출하거나, 애플리케이션 코드에서 환경 변수를 읽도록 구현합니다.

**실무 연관**
- Kubernetes에서 graceful shutdown을 위해 Exec 형식 필수
- Health check, readiness probe가 제대로 동작하려면 PID 1 관리 중요

</details>

<details>
<summary><strong>5. Dockerfile 최적화를 위한 고급 기법들을 설명해주세요.</strong></summary>

**모범 답안 포인트**
- 멀티스테이지 빌드
- 레이어 캐싱 전략
- .dockerignore 최적화
- BuildKit 기능 활용
- 불필요한 파일 제거

**예시 답변**
> "Dockerfile 최적화는 이미지 크기 감소, 빌드 시간 단축, 보안 강화를 목표로 합니다. 멀티스테이지 빌드로 빌드 도구를 제외하고, 레이어 순서를 최적화해서 캐시 히트율을 높이며, alpine 베이스 이미지로 크기를 줄입니다. RUN 명령에서 패키지 설치 후 캐시를 정리하고, .dockerignore로 불필요한 파일을 제외합니다. BuildKit의 캐시 마운트로 패키지 관리자 캐시를 공유하고, 시크릿 마운트로 빌드 시 민감 정보를 안전하게 주입합니다. 실제 프로젝트에서 이런 기법들을 적용해서 이미지 크기를 1.2GB에서 120MB로, 빌드 시간을 5분에서 30초로 줄인 경험이 있습니다."

**실무 예시**
```dockerfile
# syntax=docker/dockerfile:1.4  # BuildKit 기능 활성화

# 멀티스테이지: 빌드 단계
FROM node:18 AS builder
WORKDIR /app

# 캐시 최적화: 의존성 먼저
COPY package*.json ./

# BuildKit 캐시 마운트
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production

COPY . .
RUN npm run build

# 멀티스테이지: 실행 단계
FROM node:18-alpine
WORKDIR /app

# 보안: non-root 사용자
RUN addgroup -g 1001 appgroup && \
    adduser -D -u 1001 -G appgroup appuser

# 최소한의 파일만 복사
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --chown=appuser:appgroup package.json ./

USER appuser

# Exec 형식으로 시그널 처리
CMD ["node", "dist/server.js"]
```

**.dockerignore 최적화**:
```
node_modules
.git
.env*
*.md
coverage
.vscode
dist
build
logs
*.log
```

**BuildKit 고급 기능**:
```dockerfile
# 시크릿 마운트 (빌드 시에만 사용, 이미지에 안 남음)
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm install private-package

# 빌드
docker build --secret id=npmrc,src=$HOME/.npmrc -t myapp .
```

**꼬리 질문**
- Q: 이미지 크기를 더 줄이려면 어떤 방법이 있나요?
- A: distroless 이미지나 scratch를 베이스로 사용하면 더 줄일 수 있습니다. Go 같은 정적 바이너리는 scratch로 5MB 이하까지 가능합니다. 또는 UPX로 바이너리를 압축하는 방법도 있습니다.

**실무 연관**
- 이미지 크기가 배포 시간과 스토리지 비용에 직접 영향
- 최적화된 Dockerfile이 CI/CD 파이프라인 속도의 핵심

</details>

---

## 7.5 베스트 프랙티스 체크리스트

### ✅ 보안

- [ ] `USER` 명령어로 root가 아닌 사용자로 실행
- [ ] 불필요한 패키지 설치하지 않기
- [ ] 민감한 정보 (비밀번호, API 키) Dockerfile에 포함하지 않기
- [ ] `.dockerignore` 파일로 불필요한 파일 제외

### ✅ 성능

- [ ] 멀티스테이지 빌드로 이미지 크기 최소화
- [ ] `RUN` 명령어 체이닝으로 레이어 수 줄이기
- [ ] 자주 변경되는 파일은 Dockerfile 하단에 배치
- [ ] 패키지 관리자 캐시 정리 (`apt-get clean`, `npm cache clean`)

### ✅ 유지보수성

- [ ] 명확한 베이스 이미지 태그 사용 (`:latest` 금지)
- [ ] `LABEL`로 메타데이터 추가
- [ ] 주석으로 복잡한 명령어 설명
- [ ] `ARG`로 빌드 시 커스터마이징 가능하게

### ✅ 신뢰성

- [ ] `HEALTHCHECK`로 컨테이너 상태 모니터링
- [ ] `VOLUME`으로 데이터 영속성 보장
- [ ] 환경 변수로 설정 외부화
- [ ] Exec 형식 명령어 사용 (시그널 처리)

---

## 7.6 다음 단계

이제 Dockerfile 작성 기본을 마스터했습니다! 다음 섹션에서는:

- **섹션 8: 멀티스테이지 빌드** - 이미지 크기 90% 줄이기
- **섹션 9: 이미지 최적화 기법** - 프로덕션 최적화 전략

계속 학습하세요!

---

## 🎉 축하합니다!

**7장: Dockerfile 작성 가이드를 완료하셨습니다!**

이제 여러분은 Dockerfile 마스터입니다! 🎊

### 이제 여러분은

**기본 역량**:
- ✅ Dockerfile의 모든 핵심 명령어(FROM, RUN, COPY, CMD, ENTRYPOINT 등)를 완벽히 이해하고 사용할 수 있습니다
- ✅ 레이어 캐싱 메커니즘을 이해하고 활용해서 빌드 시간을 90% 단축할 수 있습니다
- ✅ 멀티스테이지 빌드 패턴으로 이미지 크기를 90% 줄일 수 있습니다
- ✅ .dockerignore를 활용해서 빌드 컨텍스트를 99% 최적화할 수 있습니다

**보안 및 최적화**:
- ✅ 보안을 고려한 Dockerfile을 작성할 수 있습니다 (non-root, 최소 권한)
- ✅ 프로덕션 수준의 최적화된 이미지를 빌드할 수 있습니다
- ✅ 환경별 설정을 ARG/ENV로 안전하게 관리할 수 있습니다
- ✅ Exec 형식과 Shell 형식의 차이를 이해하고 올바르게 사용할 수 있습니다

**실무 적용**:
- ✅ 실제 프로젝트에 Dockerfile을 작성하고 최적화할 수 있습니다
- ✅ 6가지 실생활 비유로 동료에게 Dockerfile을 쉽게 설명할 수 있습니다
- ✅ 주니어 개발자가 흔히 하는 실수를 피하고 올바른 방법을 안내할 수 있습니다
- ✅ 면접에서 Dockerfile 관련 질문(주니어 7개 + 중급 5개)에 자신 있게 답변할 수 있습니다

### 실무 성과 지표

**여러분이 작성한 Dockerfile로 달성할 수 있는 것**:

| 지표 | Before | After | 개선율 |
|------|--------|-------|--------|
| 이미지 크기 | 1.5GB | 150MB | **90%↓** |
| 빌드 시간 | 5분 | 30초 | **90%↓** |
| 환경 설정 시간 | 8시간 | 10분 | **95%↓** |
| 배포 시간 | 5분 | 30초 | **90%↓** |
| 배포 실패율 | 15% | 1% | **93%↓** |
| 스토리지 비용 | $100/월 | $10/월 | **90%↓** |

**보안 강화**:
- ✅ root 실행 → non-root 실행
- ✅ 빌드 도구 포함 → 런타임만 포함
- ✅ 하드코딩된 비밀번호 → 런타임 주입
- ✅ 공격 표면 90% 감소

### 다음 단계

**즉시 실습하기**:
- [ ] 현재 진행 중인 프로젝트에 Dockerfile 작성
- [ ] 멀티스테이지 빌드로 이미지 크기 90% 줄이기 도전
- [ ] .dockerignore 작성으로 빌드 시간 90% 단축하기

**심화 학습**:
- [ ] 섹션 8: Docker Compose 마스터하기
- [ ] 섹션 9: 이미지 최적화 및 보안 강화
- [ ] 섹션 10: 프로덕션 환경 배포 전략

**면접 준비**:
- [ ] 주니어 질문 7개 모두 답변 연습
- [ ] 중급 질문 5개 답변 준비
- [ ] FAQ 7개 숙지하여 실무 문제 해결 능력 향상

**실전 프로젝트**:
- [ ] Node.js 앱 Dockerfile 작성 및 최적화
- [ ] Python 앱 멀티스테이지 빌드 적용
- [ ] Java 앱 JDK→JRE 전환으로 크기 70% 감소

---

### 마지막 조언

> "완벽한 Dockerfile은 한 번에 만들어지지 않습니다. 작게 시작해서 점진적으로 최적화하세요!"

**시작 단계**:
1. 일단 동작하는 Dockerfile 작성 (FROM + COPY + CMD)
2. 레이어 캐싱 최적화 (의존성 먼저, 소스는 나중에)
3. 멀티스테이지 빌드 적용 (크기 90% 감소)
4. 보안 강화 (non-root, .dockerignore)
5. BuildKit 고급 기능 활용 (캐시 마운트, 시크릿)

**실무 팁**:
- 첫 Dockerfile 작성 시간: 30분
- 최적화 추가 시간: 1시간
- 얻게 되는 시간 절감: 평생!

---

**다음 장으로 이동**: [다음: 8장 Docker Compose 완전 정복 →](08-Docker-Compose-완전-정복.md)

**이전 장으로 돌아가기**: [← 이전: 6장 컨테이너 관리](06-컨테이너-관리.md)

**목차로 돌아가기**: [📚 Docker 학습 전체 목차](README.md)