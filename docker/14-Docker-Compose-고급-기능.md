# 섹션 14: Docker Compose 고급 기능

> **학습 목표**: 프로파일, 확장/오버라이드, 스케일링, 고급 빌드 설정, 시크릿 관리 등 Docker Compose의 고급 기능을 마스터하여 실무에서 효율적인 개발 환경을 구축할 수 있습니다.

**⏱️ 예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐⭐☆ (4개/5개)

---

## 📚 목차
- [왜 Docker Compose 고급 기능이 필요한가](#왜-docker-compose-고급-기능이-필요한가)
- [실생활 비유로 이해하기](#실생활-비유로-이해하기)
- [프로파일 (profiles)](#141-프로파일-profiles)
- [확장 및 오버라이드](#142-확장-및-오버라이드)
- [스케일링 (scale)](#143-스케일링-scale)
- [빌드 설정 (build)](#144-빌드-설정-build)
- [시크릿 관리](#145-시크릿-관리)
- [실전 예제](#146-실전-예제)
- [주니어 시나리오](#주니어-시나리오)
- [FAQ](#faq)
- [면접 질문 리스트](#면접-질문-리스트)
- [핵심 정리](#핵심-정리)
- [다음 단계](#다음-단계)

---

## 🤔 왜 Docker Compose 고급 기능이 필요한가?

### 실무 배경
**실무에서는 개발, 테스트, 스테이징, 프로덕션 등 다양한 환경에서 동일한 애플리케이션을 실행해야 합니다. 각 환경마다 설정이 달라지고, 필요한 서비스도 다릅니다. 이런 복잡성을 관리하지 못하면 환경별로 별도의 설정 파일을 관리해야 하며, 배포 실수와 유지보수 비용이 증가합니다.**

#### ❌ 고급 기능을 모르면 발생하는 문제
```
문제 1: 환경별 설정 파일 관리의 복잡성
- 증상: docker-compose-dev.yml, docker-compose-test.yml, docker-compose-prod.yml 등 파일이 난립
- 영향: 변경사항이 생기면 모든 파일을 일일이 수정해야 함
- 비용: 한 번의 배포에 30분 이상 소요, 설정 오류로 인한 장애 발생

문제 2: 불필요한 서비스 항상 실행
- 증상: 디버깅 도구, 모니터링 도구 등이 개발 환경에서도 항상 실행됨
- 영향: 시스템 리소스 낭비, 컨테이너 시작 시간 증가
- 비용: 개발자 PC 메모리 부족, 도커 시작 시간 2-3분 소요

문제 3: 스케일링 불가능
- 증상: 트래픽 증가 시 수동으로 컨테이너를 추가해야 함
- 영향: 빠른 대응 불가, 운영 부담 증가
- 비용: 서비스 다운타임 발생, 수동 작업 시간 낭비

문제 4: 비밀 정보 노출 위험
- 증상: .env 파일이나 docker-compose.yml에 비밀번호 하드코딩
- 영향: Git에 실수로 커밋, 보안 취약점 발생
- 비용: 데이터 유출 사고, 컴플라이언스 위반
```

#### ✅ 고급 기능을 사용하면
```
해결책 1: 프로파일로 선택적 서비스 실행
- 방법: 개발 도구는 --profile dev로만 실행
- 효과: 기본 환경은 빠르게 시작, 필요할 때만 도구 추가
- 절감: 도커 시작 시간 2분 → 10초

해결책 2: 오버라이드로 환경별 설정 관리
- 방법: 기본 docker-compose.yml + 환경별 override 파일
- 효과: 공통 설정은 한 곳에서 관리, 차이점만 오버라이드
- 절감: 배포 준비 시간 30분 → 5분

해결책 3: 스케일 명령으로 즉시 확장
- 방법: docker compose up --scale api=5
- 효과: 단일 명령으로 트래픽에 따라 즉시 스케일링
- 절감: 수동 작업 10분 → 명령 1줄 (5초)

해결책 4: 시크릿으로 안전한 비밀 관리
- 방법: Docker secrets로 런타임에만 주입
- 효과: Git에 비밀 정보 노출 없음, 보안 강화
- 절감: 보안 감사 통과, 컴플라이언스 준수
```

### 📊 수치로 보는 효과

| 지표 | Before | After | 개선율 |
|------|--------|-------|--------|
| 도커 시작 시간 | 2분 | 10초 | **92%↓** |
| 배포 준비 시간 | 30분 | 5분 | **83%↓** |
| 설정 파일 수 | 10개 | 3개 | **70%↓** |
| 스케일링 시간 | 10분 (수동) | 5초 (자동) | **99%↓** |
| 보안 위험 | 높음 | 낮음 | **위험 제거** |
| 리소스 사용량 | 8GB | 2GB | **75%↓** |

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 레스토랑 메뉴판 (프로파일)
```
[일반 메뉴판]
├─ 기본 메뉴 (항상 제공) - 밥, 국, 반찬
├─ 아침 메뉴 (profile: breakfast) - 토스트, 커피
├─ 점심 메뉴 (profile: lunch) - 정식, 덮밥
└─ 디저트 메뉴 (profile: dessert) - 케이크, 아이스크림

손님이 오면:
- 기본: 밥, 국, 반찬만 제공
- 아침 손님: 기본 + 토스트, 커피
- 점심 손님: 기본 + 정식, 덮밥
- 디저트 원하는 손님: 기본 + 케이크

Docker Compose:
- 기본: database, api만 실행
- --profile dev: 기본 + mailcatcher, debugger
- --profile test: 기본 + test-runner
- --profile monitoring: 기본 + prometheus, grafana

┌──────────────────────────────────┐
│    [레스토랑 메뉴]                │
│                                  │
│  기본 메뉴 (항상)                 │
│  ├─ 밥                           │
│  ├─ 국                           │
│  └─ 반찬                         │
│                                  │
│  아침 메뉴 (선택)                 │
│  ├─ 토스트                        │
│  └─ 커피                         │
│                                  │
│  점심 메뉴 (선택)                 │
│  └─ 정식                         │
└──────────────────────────────────┘

= Docker Compose 프로파일
```

### 비유 2: 아파트 설계도 (오버라이드)
```
[기본 설계도]
- 거실, 침실, 주방, 화장실 (모든 아파트 공통)

[30평형 오버라이드]
- 기본 설계도 + 침실 1개 추가

[50평형 오버라이드]
- 기본 설계도 + 침실 2개 추가 + 드레스룸

Docker Compose:
[docker-compose.yml] - 기본 설정
- database, api (모든 환경 공통)

[docker-compose.override.yml] - 로컬 개발 추가
- 기본 + 소스코드 볼륨, 디버거 포트

[docker-compose.prod.yml] - 프로덕션 추가
- 기본 + 리소스 제한, 복제본 3개

┌─────────────────────────────────┐
│   [설계도 상속]                  │
│                                 │
│   기본 설계도                    │
│   ├─ 거실                       │
│   ├─ 침실                       │
│   └─ 주방                       │
│        ↓                        │
│   30평형 (기본 + 추가)           │
│   └─ 침실 +1                    │
│        ↓                        │
│   50평형 (30평 + 추가)           │
│   └─ 침실 +1, 드레스룸          │
└─────────────────────────────────┘
```

### 비유 3: 택시 호출 시스템 (스케일링)
```
[평상시]
택시 3대만 운영
- 손님이 적어서 충분

[퇴근 시간]
택시 10대로 증가
- 손님이 많아서 확장

[새벽 시간]
택시 1대로 축소
- 손님이 거의 없어서 축소

Docker Compose 스케일링:
# 평상시
docker compose up --scale api=3

# 트래픽 증가 (Black Friday)
docker compose up --scale api=10

# 새벽 시간
docker compose up --scale api=1

┌─────────────────────────────────┐
│   시간대별 택시 운영             │
│                                 │
│   평상시 (09:00-17:00)          │
│   🚕 🚕 🚕                      │
│                                 │
│   퇴근 시간 (18:00-20:00)       │
│   🚕 🚕 🚕 🚕 🚕               │
│   🚕 🚕 🚕 🚕 🚕               │
│                                 │
│   새벽 (02:00-05:00)            │
│   🚕                            │
└─────────────────────────────────┘
```

### 비유 4: 은행 금고 (시크릿 관리)
```
[나쁜 방법 - 메모지에 비밀번호 적어두기]
- 누구나 볼 수 있음
- Git에 실수로 올라감
- 해킹 위험

[좋은 방법 - 금고에 보관]
- 필요할 때만 꺼내서 사용
- 사용 후 다시 금고에 보관
- 권한 있는 사람만 접근

Docker Secrets:
[나쁜 예]
environment:
  DB_PASSWORD=supersecret123  # Git에 노출!

[좋은 예]
secrets:
  - db_password
# 런타임에 /run/secrets/db_password로 주입
# Git에는 절대 들어가지 않음

┌─────────────────────────────────┐
│   [비밀 관리 비교]               │
│                                 │
│   ❌ 메모지에 적기               │
│   "비밀번호: 1234"               │
│   → 누구나 볼 수 있음            │
│                                 │
│   ✅ 금고에 보관                 │
│   🔐 [금고]                     │
│   → 필요할 때만 꺼내서 사용       │
│   → 사용 후 다시 보관            │
└─────────────────────────────────┘
```

### 비유 5: 공장 생산 라인 (멀티스테이지 빌드)
```
[자동차 공장]
1단계: 프레임 제작 (개발 단계)
2단계: 엔진 조립 (빌드 단계)
3단계: 도색 및 마무리 (프로덕션 단계)

완성차에는:
- 프레임 제작 도구 ❌ (필요 없음)
- 엔진 조립 도구 ❌ (필요 없음)
- 완성된 자동차만 출고 ✅

Docker 멀티스테이지 빌드:
FROM node:18 AS builder  # 빌드 도구
RUN npm install
RUN npm run build

FROM node:18-alpine AS production  # 최종 이미지
COPY --from=builder /app/dist /app
# 빌드 도구는 포함 안 됨 (이미지 크기 감소)

┌─────────────────────────────────┐
│   [공장 생산 라인]               │
│                                 │
│   1단계: 프레임 제작             │
│   🔧 도구: 용접기, 절단기        │
│   ↓                             │
│   2단계: 엔진 조립               │
│   🔧 도구: 렌치, 드라이버        │
│   ↓                             │
│   3단계: 도색 및 마무리           │
│   🔧 도구: 스프레이건            │
│   ↓                             │
│   출고: 🚗 (도구는 제외)         │
└─────────────────────────────────┘
```

### 🎯 종합 비교표

| Docker Compose 기능 | 실생활 비유 | 핵심 개념 | 사용 시기 |
|---------------------|------------|----------|----------|
| **프로파일** | 레스토랑 메뉴판 | 선택적 서비스 실행 | 개발/테스트 도구 분리 |
| **오버라이드** | 아파트 설계도 | 기본 + 추가 설정 | 환경별 설정 관리 |
| **스케일링** | 택시 호출 | 인스턴스 증감 | 트래픽 대응 |
| **시크릿** | 은행 금고 | 안전한 비밀 관리 | 비밀번호, API 키 |
| **멀티스테이지 빌드** | 공장 생산 라인 | 단계별 빌드 | 이미지 크기 최적화 |

---

## 14.1 프로파일 (profiles)

### 14.1.1 프로파일이란?

**프로파일**은 특정 서비스를 선택적으로 실행할 수 있게 해주는 기능입니다.
개발, 테스트, 디버깅 도구 등을 필요할 때만 시작할 수 있습니다.

**실생활 비유: 식당 메뉴판**

```
[전체 메뉴판]
├─ 기본 메뉴 (항상 제공)
│   ├─ 밥
│   ├─ 국
│   └─ 반찬
├─ 아침 메뉴 (profile: breakfast)
│   ├─ 토스트
│   └─ 커피
├─ 점심 메뉴 (profile: lunch)
│   ├─ 정식
│   └─ 덮밥
└─ 디버그 메뉴 (profile: debug)
    └─ 주방 CCTV 모니터

기본 실행: 밥, 국, 반찬만
--profile breakfast: 기본 + 토스트, 커피
--profile lunch: 기본 + 정식, 덮밥
--profile debug: 기본 + 주방 모니터
```

---

### 14.1.2 기본 사용법

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  # 프로파일 없음 = 항상 실행
  database:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret

  api:
    image: myapi
    depends_on:
      - database

  # 개발 도구 (프로파일: dev)
  mailcatcher:
    image: schickling/mailcatcher
    profiles: ["dev"]
    ports:
      - "1080:1080"

  # 디버그 도구 (프로파일: debug)
  debugger:
    image: node:18
    profiles: ["debug"]
    command: node --inspect=0.0.0.0:9229
    ports:
      - "9229:9229"

  # 테스트 도구 (프로파일: test)
  test-runner:
    image: myapp-test
    profiles: ["test"]
    command: npm test
```

**실행:**

```bash
# 기본 실행 (database, api만)
docker compose up

# 개발 환경
docker compose --profile dev up
# database, api, mailcatcher 실행

# 디버그 모드
docker compose --profile debug up
# database, api, debugger 실행

# 여러 프로파일
docker compose --profile dev --profile debug up
# database, api, mailcatcher, debugger 실행

# 모든 서비스 (프로파일 무시)
docker compose --profile "*" up
```

---

### 14.1.3 실전 예시: 개발 환경 구성

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  # ==================== 기본 서비스 (항상 실행) ====================
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data

  api:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://postgres:secret@postgres:5432/myapp
      REDIS_URL: redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy

  frontend:
    build: ./frontend
    ports:
      - "8080:8080"
    depends_on:
      - api

  # ==================== 개발 도구 (--profile dev) ====================
  # 이메일 테스트
  mailcatcher:
    image: schickling/mailcatcher
    profiles: ["dev"]
    ports:
      - "1080:1080"  # Web UI
      - "1025:1025"  # SMTP

  # 핫 리로드 개발 서버
  dev-server:
    build:
      context: ./backend
      target: development
    profiles: ["dev"]
    volumes:
      - ./backend/src:/app/src
      - backend-modules:/app/node_modules
    command: npm run dev
    ports:
      - "3001:3000"
      - "9229:9229"  # 디버거

  # ==================== 데이터베이스 UI (--profile db-ui) ====================
  pgadmin:
    image: dpage/pgadmin4:latest
    profiles: ["db-ui"]
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    depends_on:
      - postgres

  redis-commander:
    image: rediscommander/redis-commander:latest
    profiles: ["db-ui"]
    environment:
      REDIS_HOSTS: local:redis:6379
    ports:
      - "8081:8081"
    depends_on:
      - redis

  # ==================== 모니터링 (--profile monitoring) ====================
  prometheus:
    image: prom/prometheus:latest
    profiles: ["monitoring"]
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    profiles: ["monitoring"]
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana-data:/var/lib/grafana
    ports:
      - "3001:3000"
    depends_on:
      - prometheus

  # ==================== 테스트 (--profile test) ====================
  test-unit:
    build:
      context: ./backend
      target: test
    profiles: ["test"]
    command: npm run test:unit
    environment:
      NODE_ENV: test

  test-e2e:
    build:
      context: ./backend
      target: test
    profiles: ["test"]
    command: npm run test:e2e
    environment:
      NODE_ENV: test
      DATABASE_URL: postgresql://postgres:secret@postgres:5432/myapp_test
    depends_on:
      postgres:
        condition: service_healthy

  # ==================== 디버깅 (--profile debug) ====================
  debugger:
    image: node:18-alpine
    profiles: ["debug"]
    volumes:
      - ./backend:/app
    working_dir: /app
    command: node --inspect=0.0.0.0:9229 src/index.js
    ports:
      - "9229:9229"

volumes:
  postgres-data:
  redis-data:
  backend-modules:
  prometheus-data:
  grafana-data:
```

**사용 시나리오:**

```bash
# 1. 기본 개발
docker compose up
# postgres, redis, api, frontend

# 2. 풀 개발 환경 (이메일 테스트 포함)
docker compose --profile dev up
# 기본 + mailcatcher, dev-server

# 3. DB 관리 필요 시
docker compose --profile db-ui up
# 기본 + pgadmin, redis-commander

# 4. 성능 모니터링
docker compose --profile monitoring up
# 기본 + prometheus, grafana

# 5. 테스트 실행
docker compose --profile test run test-unit
docker compose --profile test run test-e2e

# 6. 디버깅
docker compose --profile debug up
# 기본 + debugger (포트 9229)

# 7. 조합 사용
docker compose --profile dev --profile db-ui --profile monitoring up
# 개발 + DB UI + 모니터링 모두 실행
```

---

### 14.1.4 프로파일 베스트 프랙티스

```yaml
services:
  # ✅ 좋은 예: 목적별 프로파일
  service1:
    profiles: ["dev"]           # 개발 전용
  service2:
    profiles: ["test"]          # 테스트 전용
  service3:
    profiles: ["monitoring"]    # 모니터링
  service4:
    profiles: ["debug"]         # 디버깅

  # ✅ 좋은 예: 여러 프로파일 지정
  service5:
    profiles: ["dev", "test"]   # 개발 및 테스트에서 사용

  # ❌ 나쁜 예: 핵심 서비스에 프로파일
  database:
    profiles: ["all"]           # 핵심 서비스는 프로파일 없이!
```

---

## 14.2 확장 및 오버라이드

### 14.2.1 docker-compose.override.yml

**자동 병합 메커니즘:**

```
프로젝트 디렉토리:
├── docker-compose.yml          (기본 설정)
└── docker-compose.override.yml (오버라이드, 자동 적용)

실행:
docker compose up
→ 자동으로 두 파일 병합!
```

**docker-compose.yml (기본):**

```yaml
version: '3.8'

services:
  api:
    image: myapi:latest
    environment:
      NODE_ENV: production
    restart: always

  database:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
```

**docker-compose.override.yml (로컬 개발용):**

```yaml
version: '3.8'

services:
  # api 서비스 오버라이드
  api:
    build: .                    # 이미지 대신 빌드
    volumes:
      - ./src:/app/src          # 소스 코드 마운트
    environment:
      NODE_ENV: development     # 환경 변경
    ports:
      - "3000:3000"             # 포트 추가
      - "9229:9229"             # 디버거
    command: npm run dev        # 명령어 변경

  # database 서비스에 추가
  database:
    ports:
      - "5432:5432"             # 로컬 접근 가능
    volumes:
      - ./data:/var/lib/postgresql/data  # 로컬 데이터

  # 새 서비스 추가
  mailcatcher:
    image: schickling/mailcatcher
    ports:
      - "1080:1080"
```

**병합 결과:**

```yaml
# 실제 실행되는 설정 (docker compose config로 확인)
services:
  api:
    build: .                              # override
    image: myapi:latest
    volumes:
      - ./src:/app/src                    # override 추가
    environment:
      NODE_ENV: development               # override로 변경
    ports:
      - "3000:3000"                       # override 추가
      - "9229:9229"
    command: npm run dev                  # override로 변경
    restart: always

  database:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
    ports:
      - "5432:5432"                       # override 추가
    volumes:
      - ./data:/var/lib/postgresql/data   # override 추가

  mailcatcher:                            # override에서 새로 추가
    image: schickling/mailcatcher
    ports:
      - "1080:1080"
```

---

### 14.2.2 환경별 설정 파일

**파일 구조:**

```
project/
├── docker-compose.yml                 # 기본 설정
├── docker-compose.override.yml        # 로컬 개발 (자동)
├── docker-compose.dev.yml             # 개발 서버
├── docker-compose.staging.yml         # 스테이징
├── docker-compose.prod.yml            # 프로덕션
└── docker-compose.test.yml            # 테스트
```

#### 기본 설정 (docker-compose.yml)

```yaml
version: '3.8'

# 모든 환경 공통 설정
services:
  api:
    image: myapi:${VERSION:-latest}
    environment:
      NODE_ENV: ${NODE_ENV:-production}
    restart: unless-stopped

  database:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

#### 로컬 개발 (docker-compose.override.yml)

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      target: development
    volumes:
      - ./src:/app/src
      - node-modules:/app/node_modules
    environment:
      NODE_ENV: development
      DEBUG: "app:*"
    ports:
      - "3000:3000"
      - "9229:9229"
    command: npm run dev

  database:
    ports:
      - "5432:5432"
    environment:
      POSTGRES_PASSWORD: devpassword

  # 개발 도구
  mailcatcher:
    image: schickling/mailcatcher
    ports:
      - "1080:1080"
      - "1025:1025"

volumes:
  node-modules:
```

#### 개발 서버 (docker-compose.dev.yml)

```yaml
version: '3.8'

services:
  api:
    image: myregistry.com/myapi:dev
    environment:
      NODE_ENV: development
      LOG_LEVEL: debug
    ports:
      - "3000:3000"

  database:
    environment:
      POSTGRES_PASSWORD: devserver_password

  # Nginx 리버스 프록시
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/dev.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api
```

#### 스테이징 (docker-compose.staging.yml)

```yaml
version: '3.8'

services:
  api:
    image: myregistry.com/myapi:staging
    environment:
      NODE_ENV: staging
      LOG_LEVEL: info
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M

  database:
    environment:
      POSTGRES_PASSWORD: ${STAGING_DB_PASSWORD}
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/staging.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
```

#### 프로덕션 (docker-compose.prod.yml)

```yaml
version: '3.8'

services:
  api:
    image: myregistry.com/myapi:${VERSION}
    environment:
      NODE_ENV: production
      LOG_LEVEL: warn
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '1'
          memory: 512M
      replicas: 3
    restart: always

  database:
    environment:
      POSTGRES_PASSWORD: ${PROD_DB_PASSWORD}
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
        reservations:
          cpus: '2'
          memory: 2G
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/prod.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 256M
    restart: always
    depends_on:
      - api
```

#### 테스트 (docker-compose.test.yml)

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      target: test
    environment:
      NODE_ENV: test
      DATABASE_URL: postgresql://postgres:testpass@database:5432/test
    command: npm test
    depends_on:
      database:
        condition: service_healthy

  database:
    environment:
      POSTGRES_PASSWORD: testpass
      POSTGRES_DB: test
    tmpfs:
      - /var/lib/postgresql/data  # 메모리에 저장 (빠름)

  # 테스트 리포터
  test-reporter:
    image: myapi:test
    command: npm run test:report
    volumes:
      - ./test-results:/app/test-results
    depends_on:
      - api
```

---

### 14.2.3 환경별 실행

```bash
# 로컬 개발 (자동으로 override.yml 병합)
docker compose up

# 개발 서버
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 스테이징
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# 프로덕션
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 테스트
docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm api

# 설정 확인 (병합 결과)
docker compose -f docker-compose.yml -f docker-compose.prod.yml config

# 환경 변수와 함께
VERSION=1.2.0 docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

### 14.2.4 Makefile로 간편화

**Makefile:**

```makefile
.PHONY: dev staging prod test clean

# 로컬 개발
dev:
	docker compose up

# 개발 서버 배포
dev-server:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 스테이징 배포
staging:
	docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# 프로덕션 배포
prod:
	@read -p "Enter version: " VERSION; \
	VERSION=$$VERSION docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 테스트 실행
test:
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm api

# 정리
clean:
	docker compose down -v

# 로그 확인
logs:
	docker compose logs -f

# 설정 확인
config-dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml config

config-prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml config
```

**사용:**

```bash
make dev          # 로컬 개발 시작
make dev-server   # 개발 서버 배포
make staging      # 스테이징 배포
make prod         # 프로덕션 배포 (버전 입력)
make test         # 테스트 실행
make clean        # 정리
make logs         # 로그 확인
```

---

## 14.3 스케일링 (scale)

### 14.3.1 기본 스케일링

```yaml
version: '3.8'

services:
  # 로드 밸런서
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api

  # API 서버 (스케일 가능)
  api:
    build: ./backend
    expose:
      - "3000"
    environment:
      DATABASE_URL: postgresql://postgres:secret@database:5432/myapp

  # 데이터베이스 (스케일 불가)
  database:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
```

**스케일링 실행:**

```bash
# API 서버 3개로 스케일
docker compose up -d --scale api=3

# 확인
docker compose ps
# NAME           STATE    PORTS
# nginx-1        Up       0.0.0.0:80->80/tcp
# api-1          Up       3000/tcp
# api-2          Up       3000/tcp
# api-3          Up       3000/tcp
# database-1     Up       5432/tcp

# 스케일 축소
docker compose up -d --scale api=1

# 동적 스케일 조정
docker compose up -d --scale api=5
docker compose up -d --scale api=2
```

---

### 14.3.2 Nginx 로드 밸런싱 설정

**nginx.conf:**

```nginx
events {
    worker_connections 1024;
}

http {
    # 업스트림 정의 (Docker DNS 사용)
    upstream api_backend {
        # Docker Compose가 자동으로 DNS 해석
        server api:3000;
        # 스케일된 모든 인스턴스로 자동 분산
    }

    server {
        listen 80;

        location / {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

**테스트:**

```bash
# 스케일 업
docker compose up -d --scale api=3

# 로드 밸런싱 확인
for i in {1..10}; do
  curl http://localhost/
  echo ""
done

# API 서버가 번갈아가며 응답
# Response from api-1
# Response from api-2
# Response from api-3
# Response from api-1
# ...
```

---

### 14.3.3 Compose V3 deploy 사용 (Swarm)

```yaml
version: '3.8'

services:
  api:
    image: myapi
    deploy:
      replicas: 3           # 기본 3개 인스턴스
      update_config:
        parallelism: 1      # 한 번에 1개씩 업데이트
        delay: 10s          # 업데이트 간 10초 대기
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

**Swarm 모드에서 실행:**

```bash
# Swarm 초기화
docker swarm init

# 스택 배포
docker stack deploy -c docker-compose.yml myapp

# 스케일 조정
docker service scale myapp_api=5

# 상태 확인
docker service ls
docker service ps myapp_api
```

---

### 14.3.4 스케일링 제약사항

```yaml
services:
  # ❌ 포트 매핑 시 스케일 불가
  web1:
    image: nginx
    ports:
      - "80:80"
  # docker compose up --scale web1=2
  # 에러: 포트 80 충돌!

  # ✅ expose 사용 (스케일 가능)
  web2:
    image: nginx
    expose:
      - "80"

  # ❌ container_name 지정 시 스케일 불가
  web3:
    image: nginx
    container_name: my-nginx
  # 에러: 컨테이너 이름 중복!

  # ✅ container_name 없이 (스케일 가능)
  web4:
    image: nginx
    # 자동 이름: project-web4-1, project-web4-2, ...
```

---

## 14.4 빌드 설정 (build)

### 14.4.1 고급 빌드 옵션

```yaml
services:
  app:
    build:
      # 빌드 컨텍스트
      context: ./backend
      dockerfile: Dockerfile.prod

      # 빌드 인자
      args:
        NODE_VERSION: "18"
        BUILD_DATE: "2024-01-15"
        GIT_COMMIT: "${GIT_COMMIT}"

      # 멀티스테이지 타겟
      target: production

      # 캐시 소스
      cache_from:
        - myapp:cache
        - myapp:latest

      # 추가 컨텍스트
      additional_contexts:
        shared: ../shared

      # 레이블
      labels:
        - "com.example.version=1.0"
        - "com.example.build-date=${BUILD_DATE}"

      # 네트워크 모드
      network: host

      # 공유 메모리 크기
      shm_size: '2gb'

      # 플랫폼 지정
      platforms:
        - linux/amd64
        - linux/arm64

    # 빌드된 이미지 태그
    image: myregistry.com/myapp:${VERSION:-latest}
```

---

### 14.4.2 BuildKit 활용

**.env:**

```env
COMPOSE_DOCKER_CLI_BUILD=1
DOCKER_BUILDKIT=1
```

**docker-compose.yml:**

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      cache_from:
        - type=registry,ref=myapp:buildcache
      cache_to:
        - type=inline

      # BuildKit 시크릿 마운트
      secrets:
        - npmrc

      # SSH 에이전트 포워딩
      ssh:
        - default

secrets:
  npmrc:
    file: ./.npmrc
```

**Dockerfile with BuildKit:**

```dockerfile
# syntax=docker/dockerfile:1.4

FROM node:18-alpine

WORKDIR /app

# 시크릿 마운트 (이미지에 포함 안 됨)
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci --only=production

# SSH 마운트 (Private repo 클론)
RUN --mount=type=ssh \
    git clone git@github.com:user/private-repo.git

COPY . .

CMD ["node", "server.js"]
```

---

### 14.4.3 멀티 플랫폼 빌드

```yaml
services:
  app:
    build:
      context: .
      platforms:
        - linux/amd64    # Intel/AMD 64비트
        - linux/arm64    # ARM 64비트 (Apple Silicon)
        - linux/arm/v7   # ARM 32비트
    image: myregistry.com/myapp:multiarch
```

**빌드:**

```bash
# Buildx 빌더 생성
docker buildx create --name multiarch --use

# 멀티 플랫폼 빌드
docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest .

# Compose로 빌드
docker compose build

# 특정 플랫폼으로 빌드
docker compose build --platform linux/amd64
```

---

## 14.5 시크릿 관리

### 14.5.1 Docker Swarm 시크릿

```yaml
version: '3.8'

services:
  api:
    image: myapi
    secrets:
      - db_password
      - api_key
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password
      API_KEY_FILE: /run/secrets/api_key

secrets:
  db_password:
    external: true  # 외부에서 생성된 시크릿

  api_key:
    file: ./secrets/api_key.txt  # 파일에서 로드
```

**Swarm에서 시크릿 생성:**

```bash
# 시크릿 생성
echo "supersecretpassword" | docker secret create db_password -

# 파일에서 시크릿 생성
docker secret create api_key ./secrets/api_key.txt

# 시크릿 목록
docker secret ls

# 스택 배포
docker stack deploy -c docker-compose.yml myapp
```

**애플리케이션에서 사용:**

```javascript
// Node.js 예시
const fs = require('fs');

// 시크릿 읽기
const dbPassword = fs.readFileSync('/run/secrets/db_password', 'utf8').trim();
const apiKey = fs.readFileSync('/run/secrets/api_key', 'utf8').trim();

// 데이터베이스 연결
const db = connectDB({
  password: dbPassword
});

// API 클라이언트
const apiClient = createClient({
  apiKey: apiKey
});
```

---

### 14.5.2 로컬 개발용 시크릿 (파일)

```yaml
version: '3.8'

services:
  api:
    image: myapi
    secrets:
      - db_password
      - api_key
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password
      API_KEY_FILE: /run/secrets/api_key

secrets:
  db_password:
    file: ./secrets/db_password.txt

  api_key:
    file: ./secrets/api_key.txt
```

**secrets/ 디렉토리:**

```
secrets/
├── db_password.txt
├── api_key.txt
└── .gitignore
```

**secrets/.gitignore:**

```
# 모든 시크릿 파일 Git 제외
*
!.gitignore
```

---

### 14.5.3 환경 변수 + 시크릿 하이브리드

```yaml
services:
  api:
    image: myapi
    environment:
      # 민감하지 않은 정보
      NODE_ENV: production
      PORT: 3000
      LOG_LEVEL: info

      # 시크릿 파일 경로
      DB_PASSWORD_FILE: /run/secrets/db_password
      JWT_SECRET_FILE: /run/secrets/jwt_secret

    secrets:
      - db_password
      - jwt_secret

secrets:
  db_password:
    file: ./secrets/db_password.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt
```

**헬퍼 함수 (애플리케이션):**

```javascript
// config.js
const fs = require('fs');

function getSecret(envVar, defaultValue = '') {
  const secretFile = process.env[`${envVar}_FILE`];

  if (secretFile && fs.existsSync(secretFile)) {
    return fs.readFileSync(secretFile, 'utf8').trim();
  }

  return process.env[envVar] || defaultValue;
}

module.exports = {
  nodeEnv: process.env.NODE_ENV,
  port: process.env.PORT,

  // 시크릿 (파일 우선, 환경 변수 fallback)
  dbPassword: getSecret('DB_PASSWORD'),
  jwtSecret: getSecret('JWT_SECRET'),
  apiKey: getSecret('API_KEY')
};
```

---

## 14.6 실전 예제

### 14.6.1 완전한 마이크로서비스 개발 환경

**프로젝트 구조:**

```
microservices/
├── docker-compose.yml
├── docker-compose.override.yml
├── docker-compose.prod.yml
├── services/
│   ├── gateway/
│   ├── user-service/
│   ├── product-service/
│   └── order-service/
├── nginx/
│   ├── dev.conf
│   └── prod.conf
└── secrets/
    ├── .gitignore
    └── (시크릿 파일들)
```

**docker-compose.yml (기본):**

```yaml
version: '3.8'

# 재사용 가능한 템플릿
x-service-defaults: &service-defaults
  restart: unless-stopped
  networks:
    - backend
  logging:
    driver: json-file
    options:
      max-size: "10m"
      max-file: "3"

x-healthcheck: &healthcheck
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s

services:
  # ==================== API Gateway ====================
  gateway:
    <<: *service-defaults
    build:
      context: ./services/gateway
    image: myapp-gateway:${VERSION:-latest}
    ports:
      - "${GATEWAY_PORT:-3000}:3000"
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
    healthcheck:
      <<: *healthcheck
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]

  # ==================== User Service ====================
  user-service:
    <<: *service-defaults
    build:
      context: ./services/user-service
    image: myapp-user-service:${VERSION:-latest}
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@postgres:5432/users
      REDIS_URL: redis://cache:6379
    depends_on:
      postgres:
        condition: service_healthy
      cache:
        condition: service_healthy
    healthcheck:
      <<: *healthcheck
      test: ["CMD", "curl", "-f", "http://localhost:4001/health"]

  # ==================== Product Service ====================
  product-service:
    <<: *service-defaults
    build:
      context: ./services/product-service
    image: myapp-product-service:${VERSION:-latest}
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@postgres:5432/products
      REDIS_URL: redis://cache:6379
    depends_on:
      postgres:
        condition: service_healthy
      cache:
        condition: service_healthy
    healthcheck:
      <<: *healthcheck
      test: ["CMD", "curl", "-f", "http://localhost:4002/health"]

  # ==================== Order Service ====================
  order-service:
    <<: *service-defaults
    build:
      context: ./services/order-service
    image: myapp-order-service:${VERSION:-latest}
    environment:
      MONGODB_URI: mongodb://mongo:27017/orders
      KAFKA_BROKERS: kafka:9092
    depends_on:
      mongo:
        condition: service_healthy
    healthcheck:
      <<: *healthcheck
      test: ["CMD", "curl", "-f", "http://localhost:4003/health"]

  # ==================== Databases ====================
  postgres:
    <<: *service-defaults
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  mongo:
    <<: *service-defaults
    image: mongo:7
    volumes:
      - mongo-data:/data/db
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 3

  cache:
    <<: *service-defaults
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 3

networks:
  frontend:
  backend:
    internal: true

volumes:
  postgres-data:
  mongo-data:
  redis-data:
```

**docker-compose.override.yml (로컬 개발):**

```yaml
version: '3.8'

services:
  # 모든 서비스에 개발 설정 추가
  gateway:
    build:
      target: development
    volumes:
      - ./services/gateway/src:/app/src
      - gateway-modules:/app/node_modules
    environment:
      NODE_ENV: development
      DEBUG: "app:*"
    ports:
      - "9229:9229"
    command: npm run dev

  user-service:
    build:
      target: development
    volumes:
      - ./services/user-service/src:/app/src
      - user-modules:/app/node_modules
    environment:
      NODE_ENV: development
    ports:
      - "4001:4001"
      - "9230:9229"
    command: npm run dev

  product-service:
    build:
      target: development
    volumes:
      - ./services/product-service/src:/app/src
      - product-modules:/app/node_modules
    environment:
      NODE_ENV: development
    ports:
      - "4002:4002"
      - "9231:9229"
    command: npm run dev

  order-service:
    build:
      target: development
    volumes:
      - ./services/order-service/src:/app/src
      - order-modules:/app/node_modules
    environment:
      NODE_ENV: development
    ports:
      - "4003:4003"
      - "9232:9229"
    command: npm run dev

  # 데이터베이스 포트 노출
  postgres:
    ports:
      - "5432:5432"

  mongo:
    ports:
      - "27017:27017"

  cache:
    ports:
      - "6379:6379"

  # 개발 도구
  mailcatcher:
    image: schickling/mailcatcher
    profiles: ["tools"]
    ports:
      - "1080:1080"
      - "1025:1025"
    networks:
      - backend

  pgadmin:
    image: dpage/pgadmin4
    profiles: ["tools"]
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    networks:
      - backend

volumes:
  gateway-modules:
  user-modules:
  product-modules:
  order-modules:
```

**docker-compose.prod.yml (프로덕션):**

```yaml
version: '3.8'

services:
  # Nginx 리버스 프록시
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/prod.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - nginx-logs:/var/log/nginx
    networks:
      - frontend
    depends_on:
      - gateway
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 256M

  gateway:
    build:
      target: production
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 512M
    environment:
      NODE_ENV: production
      LOG_LEVEL: warn

  user-service:
    build:
      target: production
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 512M

  product-service:
    build:
      target: production
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 512M

  order-service:
    build:
      target: production
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 512M

  postgres:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G

  mongo:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

  cache:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M

volumes:
  nginx-logs:
```

**Makefile:**

```makefile
.PHONY: dev prod test clean logs

# 로컬 개발
dev:
	docker compose up

# 개발 + 도구
dev-tools:
	docker compose --profile tools up

# 프로덕션
prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 특정 서비스만 빌드
build-%:
	docker compose build $*

# 테스트
test:
	docker compose run --rm user-service npm test
	docker compose run --rm product-service npm test
	docker compose run --rm order-service npm test

# 로그
logs:
	docker compose logs -f

logs-%:
	docker compose logs -f $*

# 정리
clean:
	docker compose down -v

# 상태 확인
ps:
	docker compose ps
```

**사용:**

```bash
# 개발 시작
make dev

# 개발 + 도구 (pgAdmin, mailcatcher)
make dev-tools

# 특정 서비스 빌드
make build-gateway
make build-user-service

# 테스트
make test

# 로그
make logs
make logs-gateway
make logs-user-service

# 프로덕션 배포
make prod

# 정리
make clean
```

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: 모든 서비스를 항상 실행해서 PC가 느려요

**상황**: 주니어 개발자 김개발님은 docker compose up을 실행하면 개발에 필요한 서비스뿐만 아니라 pgAdmin, 모니터링 도구, 테스트 컨테이너까지 모두 실행됩니다. PC 메모리가 부족해서 VSCode도 느려지고 있습니다.

```yaml
# ❌ 주니어 개발자가 작성한 docker-compose.yml
version: '3.8'
services:
  database:
    image: postgres:15
  api:
    build: .
  pgadmin:  # 항상 실행 (불필요)
    image: dpage/pgadmin4
  prometheus:  # 항상 실행 (불필요)
    image: prom/prometheus
  grafana:  # 항상 실행 (불필요)
    image: grafana/grafana
  test-runner:  # 항상 실행 (불필요)
    image: myapp-test
```

**문제점**:
- 문제 1: 모든 서비스가 프로파일 없이 항상 실행됨
- 문제 2: 메모리 8GB 중 6GB를 Docker가 사용
- 문제 3: 도커 시작 시간이 2-3분 소요
- 왜 이 문제가 발생하는가: 프로파일을 사용하지 않아 선택적 실행이 불가능

**해결책**:
```yaml
# ✅ 프로파일을 사용한 올바른 코드
version: '3.8'

services:
  # 기본 서비스 (항상 실행)
  database:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret

  api:
    build: .
    depends_on:
      - database

  # 개발 도구 (필요할 때만)
  pgadmin:
    image: dpage/pgadmin4
    profiles: ["tools"]  # --profile tools로만 실행
    ports:
      - "5050:80"

  # 모니터링 (필요할 때만)
  prometheus:
    image: prom/prometheus
    profiles: ["monitoring"]  # --profile monitoring으로만 실행

  grafana:
    image: grafana/grafana
    profiles: ["monitoring"]

  # 테스트 (필요할 때만)
  test-runner:
    image: myapp-test
    profiles: ["test"]  # --profile test로만 실행
```

**사용 방법**:
```bash
# 기본 개발 (database, api만)
docker compose up
# 메모리 사용: 2GB, 시작 시간: 10초

# DB 관리 필요 시
docker compose --profile tools up
# database, api, pgadmin

# 모니터링 필요 시
docker compose --profile monitoring up
# database, api, prometheus, grafana

# 테스트 실행 시
docker compose --profile test run test-runner
```

**배운 점**:
- 💡 팁 1: 핵심 서비스는 프로파일 없이, 부가 도구는 프로파일로 분리
- 💡 팁 2: profiles: ["dev", "test"] 처럼 여러 프로파일 지정 가능
- 💡 팁 3: 개발 환경은 빠르게 시작하는 것이 중요 (10초 이내)

---

### 시나리오 2: 환경별 설정을 여러 파일로 관리하다가 헷갈려요

**상황**: 주니어 개발자 박신입님은 개발/스테이징/프로덕션 환경마다 별도의 docker-compose 파일을 만들었습니다. 그런데 database 설정을 변경하려니 3개 파일을 모두 수정해야 하고, 실수로 프로덕션 파일에 개발용 설정을 넣어버렸습니다.

```bash
# ❌ 주니어 개발자의 파일 구조
docker-compose-dev.yml      # 500줄
docker-compose-staging.yml  # 500줄 (dev와 95% 동일)
docker-compose-prod.yml     # 500줄 (dev와 95% 동일)

# 문제: database 포트를 5433으로 변경하려면?
# → 3개 파일 모두 수정해야 함
# → 한 파일 빼먹으면 버그 발생
```

**문제점**:
- 문제 1: 중복 코드가 너무 많음 (95% 동일)
- 문제 2: 변경사항 발생 시 모든 파일 수정 필요
- 문제 3: 실수로 프로덕션에 개발 설정 적용
- 왜 이 문제가 발생하는가: 오버라이드 개념을 모르고 복사-붙여넣기로 관리

**해결책**:
```yaml
# ✅ docker-compose.yml (기본 설정 - 100줄)
version: '3.8'

services:
  database:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db-data:/var/lib/postgresql/data

  api:
    image: myapp:${VERSION:-latest}
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@database:5432/myapp
    depends_on:
      - database

volumes:
  db-data:
```

```yaml
# ✅ docker-compose.override.yml (로컬 개발용 - 30줄)
version: '3.8'

services:
  api:
    build: .  # 로컬에서는 빌드
    volumes:
      - ./src:/app/src  # 소스 코드 마운트
    environment:
      NODE_ENV: development
    ports:
      - "3000:3000"
      - "9229:9229"  # 디버거

  database:
    ports:
      - "5432:5432"  # 로컬 접근 가능
```

```yaml
# ✅ docker-compose.prod.yml (프로덕션용 - 40줄)
version: '3.8'

services:
  api:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 512M
    environment:
      NODE_ENV: production
      LOG_LEVEL: warn

  database:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
```

**사용 방법**:
```bash
# 로컬 개발 (자동으로 override.yml 병합)
docker compose up
# → docker-compose.yml + docker-compose.override.yml

# 프로덕션
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
# → docker-compose.yml + docker-compose.prod.yml

# database 포트 변경 시?
# → docker-compose.yml 한 곳만 수정하면 끝!
```

**배운 점**:
- 💡 팁 1: 공통 설정은 docker-compose.yml에, 차이점만 오버라이드
- 💡 팁 2: docker-compose.override.yml은 자동으로 병합됨
- 💡 팁 3: -f 옵션으로 여러 파일 병합 가능 (순서 중요!)
- 💡 팁 4: 중복 코드 500줄 → 170줄 (66% 감소)

---

### 시나리오 3: 트래픽이 증가해서 API 서버를 늘리고 싶은데 어떻게 하나요?

**상황**: 주니어 개발자 이초보님은 블랙 프라이데이에 트래픽이 10배 증가했습니다. API 서버를 늘려야 하는데, 지금은 docker-compose.yml에 api 서비스가 1개만 정의되어 있습니다. 어떻게 해야 할까요?

```yaml
# ❌ 주니어 개발자의 시도 1: 서비스를 복사?
services:
  api-1:
    image: myapi
    ports:
      - "3000:3000"

  api-2:
    image: myapi
    ports:
      - "3001:3000"  # 포트를 다르게?

  api-3:
    image: myapi
    ports:
      - "3002:3000"

  # 문제: 포트를 일일이 관리해야 함
  # 문제: nginx 설정도 수정해야 함
  # 문제: 너무 번거로움!
```

**문제점**:
- 문제 1: 서비스를 복사하면 설정 관리가 복잡
- 문제 2: 포트를 수동으로 관리해야 함
- 문제 3: 스케일 변경 시마다 docker-compose.yml 수정
- 왜 이 문제가 발생하는가: --scale 옵션을 몰라서 수동으로 복사

**해결책**:
```yaml
# ✅ 스케일 가능한 올바른 설정
version: '3.8'

services:
  # Nginx 로드 밸런서
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api

  # API 서버 (스케일 가능)
  api:
    image: myapi
    expose:  # ports 대신 expose 사용!
      - "3000"
    environment:
      DATABASE_URL: postgresql://postgres:secret@database:5432/myapp
    depends_on:
      - database

  database:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
```

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        # Docker DNS가 자동으로 모든 api 인스턴스로 분산
        server api:3000;
    }

    server {
        listen 80;
        location / {
            proxy_pass http://api_backend;
        }
    }
}
```

**사용 방법**:
```bash
# 평상시: API 서버 3개
docker compose up -d --scale api=3

# 블랙 프라이데이: API 서버 10개로 확장
docker compose up -d --scale api=10
# 5초 만에 완료!

# 새벽 시간: API 서버 1개로 축소
docker compose up -d --scale api=1

# 확인
docker compose ps
# NAME           STATE    PORTS
# nginx-1        Up       0.0.0.0:80->80/tcp
# api-1          Up       3000/tcp
# api-2          Up       3000/tcp
# api-3          Up       3000/tcp
# ...
# api-10         Up       3000/tcp
```

**배운 점**:
- 💡 팁 1: 포트 매핑(ports) 대신 expose 사용해야 스케일 가능
- 💡 팁 2: container_name 지정하면 스케일 불가
- 💡 팁 3: Nginx가 Docker DNS로 자동 로드밸런싱
- 💡 팁 4: 수동 작업 10분 → 명령 1줄 (5초)

---

### 시나리오 4: .env 파일을 Git에 커밋했다가 비밀번호가 노출됐어요

**상황**: 주니어 개발자 최실수님은 데이터베이스 비밀번호를 .env 파일에 저장하고, 실수로 Git에 커밋했습니다. GitHub에 public 레포지토리로 올라가서 누구나 볼 수 있게 되었습니다. 회사에서 큰 문제가 되었습니다.

```bash
# ❌ 주니어 개발자의 실수
# .env
DB_PASSWORD=supersecret123
API_KEY=sk-1234567890abcdef
JWT_SECRET=my-very-secret-key

# docker-compose.yml
environment:
  DB_PASSWORD: ${DB_PASSWORD}  # .env에서 로드
  API_KEY: ${API_KEY}
  JWT_SECRET: ${JWT_SECRET}

# Git에 커밋
git add .
git commit -m "fix: update config"
git push
# → .env 파일이 GitHub에 올라감!
# → 비밀번호 노출!
```

**문제점**:
- 문제 1: .env 파일이 Git에 커밋됨
- 문제 2: 누구나 비밀번호를 볼 수 있음
- 문제 3: 보안 감사 실패, 컴플라이언스 위반
- 왜 이 문제가 발생하는가: Docker Secrets를 몰라서 .env 파일로 관리

**해결책**:
```yaml
# ✅ Docker Secrets로 안전하게 관리
version: '3.8'

services:
  api:
    image: myapi
    secrets:
      - db_password
      - api_key
      - jwt_secret
    environment:
      # 파일 경로만 전달
      DB_PASSWORD_FILE: /run/secrets/db_password
      API_KEY_FILE: /run/secrets/api_key
      JWT_SECRET_FILE: /run/secrets/jwt_secret

  database:
    image: postgres:15
    secrets:
      - db_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    file: ./secrets/api_key.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt
```

```bash
# secrets/ 디렉토리 구조
secrets/
├── db_password.txt     # "supersecret123"
├── api_key.txt         # "sk-1234567890abcdef"
├── jwt_secret.txt      # "my-very-secret-key"
└── .gitignore          # "*" (모든 파일 제외)

# .gitignore
secrets/*
!secrets/.gitignore
```

```javascript
// 애플리케이션에서 시크릿 읽기
const fs = require('fs');

function getSecret(name) {
  const secretFile = process.env[`${name}_FILE`];
  if (secretFile && fs.existsSync(secretFile)) {
    return fs.readFileSync(secretFile, 'utf8').trim();
  }
  throw new Error(`Secret ${name} not found`);
}

const dbPassword = getSecret('DB_PASSWORD');
const apiKey = getSecret('API_KEY');
const jwtSecret = getSecret('JWT_SECRET');

// 이제 안전하게 사용
const db = connectDB({ password: dbPassword });
```

**사용 방법**:
```bash
# 1. secrets 디렉토리 생성
mkdir secrets
echo "supersecret123" > secrets/db_password.txt
echo "sk-1234567890abcdef" > secrets/api_key.txt
echo "my-very-secret-key" > secrets/jwt_secret.txt

# 2. .gitignore 설정
echo "secrets/*" >> secrets/.gitignore
echo "!secrets/.gitignore" >> secrets/.gitignore

# 3. 실행
docker compose up

# 4. 확인
docker compose exec api sh
cat /run/secrets/db_password
# supersecret123 (파일로만 접근 가능, 환경 변수 아님)

# Git에는 secrets/.gitignore만 커밋됨
# 실제 비밀 파일은 절대 커밋 안 됨!
```

**배운 점**:
- 💡 팁 1: 비밀 정보는 절대 .env 파일에 저장하지 말 것
- 💡 팁 2: Docker Secrets는 /run/secrets/ 디렉토리로 마운트
- 💡 팁 3: secrets/ 디렉토리는 .gitignore로 완전히 차단
- 💡 팁 4: 프로덕션에서는 Docker Swarm secrets 또는 AWS Secrets Manager 사용

---

## ❓ FAQ

<details>
<summary><strong>Q1: 프로파일을 여러 개 동시에 사용할 수 있나요?</strong></summary>

**A**: 네, --profile 옵션을 여러 번 사용하면 여러 프로파일을 동시에 활성화할 수 있습니다.

**상세 설명**:
- 포인트 1: --profile 옵션은 여러 번 반복 가능
- 포인트 2: 프로파일이 없는 서비스는 항상 실행
- 포인트 3: 하나의 서비스에 여러 프로파일 지정 가능

**예시**:
```bash
# 개발 + 모니터링 동시 실행
docker compose --profile dev --profile monitoring up

# 서비스가 여러 프로파일에 속할 수 있음
services:
  test-db:
    profiles: ["dev", "test"]  # dev 또는 test 프로파일에서 실행
```

**실무 팁**:
💡 자주 사용하는 프로파일 조합은 Makefile이나 스크립트로 만들어두면 편리합니다.

```makefile
# Makefile
dev-full:
	docker compose --profile dev --profile tools --profile monitoring up
```

</details>

<details>
<summary><strong>Q2: docker-compose.override.yml은 언제 자동으로 적용되나요?</strong></summary>

**A**: docker compose 명령 실행 시 현재 디렉토리에 docker-compose.override.yml이 있으면 자동으로 병합됩니다.

**상세 설명**:
- 포인트 1: -f 옵션 없이 실행하면 자동 적용
- 포인트 2: docker-compose.yml → docker-compose.override.yml 순서로 병합
- 포인트 3: 프로덕션 배포 시 override.yml이 적용되지 않도록 주의

**예시**:
```bash
# 자동 병합 (override.yml 적용됨)
docker compose up

# override.yml 무시
docker compose -f docker-compose.yml up

# 프로덕션 (override.yml 대신 prod.yml 사용)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```

**실무 팁**:
💡 CI/CD 파이프라인에서는 항상 -f 옵션으로 명시적으로 파일 지정하는 것이 안전합니다.

</details>

<details>
<summary><strong>Q3: 스케일링할 때 포트 충돌이 발생하는데 어떻게 해결하나요?</strong></summary>

**A**: ports 대신 expose를 사용하고, 로드 밸런서(Nginx, HAProxy 등)를 앞에 두면 됩니다.

**상세 설명**:
- 포인트 1: ports는 호스트 포트를 바인딩하므로 스케일 불가
- 포인트 2: expose는 컨테이너 간 통신만 허용 (호스트 바인딩 안 함)
- 포인트 3: 외부 접근은 로드 밸런서를 통해서만

**예시**:
```yaml
# ❌ 스케일 불가 (포트 충돌)
services:
  api:
    ports:
      - "3000:3000"  # 두 번째 인스턴스부터 충돌!

# ✅ 스케일 가능
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"  # 외부 접근은 여기로만

  api:
    image: myapi
    expose:
      - "3000"  # 컨테이너 간 통신만
```

**실무 팁**:
💡 개발 환경에서 특정 서비스에 직접 접근하고 싶다면, 해당 서비스에만 ports를 사용하고 스케일링 대상 서비스는 expose 사용

</details>

<details>
<summary><strong>Q4: Docker Secrets는 로컬 개발 환경에서도 사용할 수 있나요?</strong></summary>

**A**: 네, Docker Compose는 로컬 파일 기반 Secrets를 지원합니다. Swarm 없이도 사용 가능합니다.

**상세 설명**:
- 포인트 1: Swarm 모드: 외부 시크릿 사용 (docker secret create)
- 포인트 2: Compose 모드: 로컬 파일 사용 (file: ./secrets/xxx.txt)
- 포인트 3: 둘 다 /run/secrets/ 경로로 마운트됨

**예시**:
```yaml
# 로컬 개발용 (Swarm 불필요)
secrets:
  db_password:
    file: ./secrets/db_password.txt

# 프로덕션용 (Swarm 필요)
secrets:
  db_password:
    external: true  # docker secret create로 생성
```

**실무 팁**:
💡 로컬은 파일 기반, 프로덕션은 외부 시크릿 관리 시스템(AWS Secrets Manager, HashiCorp Vault) 사용

</details>

<details>
<summary><strong>Q5: 여러 docker-compose 파일을 병합할 때 순서가 중요한가요?</strong></summary>

**A**: 네, 매우 중요합니다! 나중에 지정한 파일이 이전 파일의 설정을 오버라이드합니다.

**상세 설명**:
- 포인트 1: -f 옵션 순서대로 병합됨
- 포인트 2: 나중 파일이 이전 파일 덮어씀
- 포인트 3: 배열(ports, volumes)은 병합, 단일 값(image, command)은 교체

**예시**:
```bash
# 순서 1: base → prod
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
# prod의 설정이 base를 오버라이드

# 순서 2: prod → base (잘못된 예시)
docker compose -f docker-compose.prod.yml -f docker-compose.yml up
# base의 설정이 prod를 오버라이드 (의도와 반대!)
```

**병합 규칙**:
```yaml
# base.yml
services:
  api:
    image: myapi:v1
    ports:
      - "3000:3000"

# prod.yml
services:
  api:
    image: myapi:v2  # 교체됨
    ports:
      - "80:3000"    # 병합됨 (두 포트 모두 바인딩)
```

**실무 팁**:
💡 docker compose config 명령으로 병합 결과 미리 확인하세요.

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml config
```

</details>

<details>
<summary><strong>Q6: 스케일링과 Swarm의 deploy.replicas는 뭐가 다른가요?</strong></summary>

**A**: --scale은 단일 호스트에서 즉시 사용 가능하고, deploy.replicas는 Swarm 클러스터에서만 동작합니다.

**상세 설명**:
- 포인트 1: --scale: Docker Compose 명령어, 단일 서버
- 포인트 2: deploy.replicas: Docker Swarm 설정, 여러 서버 분산
- 포인트 3: Swarm은 자동 재시작, 로드밸런싱, 롤링 업데이트 제공

**예시**:
```yaml
# --scale 방식 (단일 호스트)
services:
  api:
    image: myapi
# docker compose up --scale api=3

# Swarm 방식 (클러스터)
services:
  api:
    image: myapi
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
      restart_policy:
        condition: on-failure
# docker stack deploy -c docker-compose.yml myapp
```

**비교표**:

| 항목 | --scale | deploy.replicas |
|------|---------|-----------------|
| 실행 환경 | 단일 호스트 | Swarm 클러스터 |
| 명령어 | docker compose | docker stack |
| 자동 재시작 | ❌ | ✅ |
| 여러 서버 분산 | ❌ | ✅ |
| 헬스체크 기반 재배포 | ❌ | ✅ |
| 학습 곡선 | 쉬움 | 어려움 |

**실무 팁**:
💡 소규모 프로젝트: --scale 충분
💡 대규모 서비스: Kubernetes 고려 (Swarm보다 생태계 풍부)

</details>

<details>
<summary><strong>Q7: BuildKit의 시크릿 마운트는 일반 Secrets와 뭐가 다른가요?</strong></summary>

**A**: BuildKit 시크릿은 빌드 타임에만 사용되고 이미지에 포함되지 않습니다. Docker Secrets는 런타임에 컨테이너에 주입됩니다.

**상세 설명**:
- 포인트 1: BuildKit 시크릿: 이미지 빌드 중에만 사용 (npm 인증 등)
- 포인트 2: Docker Secrets: 컨테이너 실행 중에만 사용 (DB 비밀번호 등)
- 포인트 3: BuildKit 시크릿은 이미지 레이어에 남지 않음 (보안 강화)

**예시**:
```dockerfile
# BuildKit 시크릿 (빌드 타임)
# syntax=docker/dockerfile:1.4
FROM node:18

# .npmrc 파일이 필요하지만 이미지에는 포함하고 싶지 않음
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci
# 빌드 후 .npmrc는 이미지에 없음!
```

```yaml
# Docker Secrets (런타임)
services:
  api:
    build:
      context: .
      secrets:
        - npmrc  # 빌드 타임 시크릿
    secrets:
      - db_password  # 런타임 시크릿
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password

secrets:
  npmrc:
    file: ./.npmrc
  db_password:
    file: ./secrets/db_password.txt
```

**비교표**:

| 항목 | BuildKit Secrets | Docker Secrets |
|------|------------------|----------------|
| 사용 시점 | 이미지 빌드 중 | 컨테이너 실행 중 |
| 이미지 포함 여부 | ❌ (레이어에 없음) | ❌ (런타임만) |
| 용도 | npm 인증, git 인증 | DB 비밀번호, API 키 |
| 경로 | Dockerfile에서 지정 | /run/secrets/ |

**실무 팁**:
💡 Private npm 패키지 설치 시 BuildKit 시크릿 필수!
💡 .npmrc를 COPY하면 이미지에 남아서 보안 취약점 발생

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. Docker Compose의 프로파일(profiles)은 무엇이고 왜 사용하나요?</strong></summary>

**모범 답안 포인트**
- 포인트 1: 특정 서비스를 선택적으로 실행하는 기능
- 포인트 2: 개발 도구, 테스트 도구 등을 필요할 때만 실행
- 포인트 3: 리소스 절약, 빠른 시작 시간

**예시 답변**
> "프로파일은 Docker Compose에서 특정 서비스를 선택적으로 실행할 수 있게 해주는 기능입니다. 예를 들어, database와 api는 항상 실행하지만, pgAdmin이나 모니터링 도구는 필요할 때만 --profile tools 옵션으로 실행할 수 있습니다. 이를 통해 개발 환경의 리소스 사용량을 줄이고 시작 시간을 단축할 수 있습니다."

**꼬리 질문**
- Q: 프로파일 없이 서비스를 실행하면 어떻게 되나요?
- A: 프로파일이 지정되지 않은 서비스만 실행됩니다. 프로파일이 있는 서비스는 무시됩니다.

**실무 연관**
- 실무에서는 개발/테스트/모니터링 도구를 프로파일로 분리하여 평소에는 빠르게 시작하고, 필요할 때만 추가 도구를 실행합니다.

</details>

<details>
<summary><strong>2. docker-compose.override.yml 파일의 역할은 무엇인가요?</strong></summary>

**모범 답안 포인트**
- 포인트 1: docker-compose.yml의 설정을 오버라이드하는 파일
- 포인트 2: -f 옵션 없이 실행하면 자동으로 병합됨
- 포인트 3: 로컬 개발 환경 설정에 주로 사용

**예시 답변**
> "docker-compose.override.yml은 기본 docker-compose.yml의 설정을 덮어쓰거나 추가하는 파일입니다. docker compose up을 실행하면 자동으로 병합되어 적용됩니다. 주로 로컬 개발 환경에서 소스 코드 볼륨 마운트, 디버거 포트 추가 등 개발자마다 다른 설정을 관리할 때 사용합니다."

**꼬리 질문**
- Q: 프로덕션 배포 시 override.yml이 적용되지 않게 하려면?
- A: -f 옵션으로 명시적으로 파일을 지정하면 됩니다. 예: docker compose -f docker-compose.yml -f docker-compose.prod.yml up

**실무 연관**
- 팀원마다 다른 로컬 설정(포트, 볼륨 경로 등)을 override.yml로 관리하면 충돌 없이 협업 가능합니다.

</details>

<details>
<summary><strong>3. Docker Compose에서 스케일링할 때 주의해야 할 점은 무엇인가요?</strong></summary>

**모범 답안 포인트**
- 포인트 1: ports 대신 expose 사용
- 포인트 2: container_name 지정하면 스케일 불가
- 포인트 3: 로드 밸런서 필요

**예시 답변**
> "스케일링할 서비스는 호스트 포트를 바인딩하는 ports 대신 expose를 사용해야 합니다. ports를 사용하면 두 번째 인스턴스부터 포트 충돌이 발생합니다. 또한 container_name을 지정하면 컨테이너 이름이 고정되어 스케일링이 불가능합니다. 스케일링한 서비스 앞에는 Nginx 같은 로드 밸런서를 두어 트래픽을 분산해야 합니다."

**꼬리 질문**
- Q: 스케일링된 컨테이너는 어떻게 이름이 지정되나요?
- A: project-service-1, project-service-2 형식으로 자동 부여됩니다.

**실무 연관**
- 트래픽이 증가하는 이벤트(블랙 프라이데이 등) 전에 --scale 옵션으로 미리 서버를 늘려둡니다.

</details>

<details>
<summary><strong>4. Docker Secrets와 환경 변수의 차이점은 무엇인가요?</strong></summary>

**모범 답안 포인트**
- 포인트 1: Secrets는 파일로 마운트, 환경 변수는 메모리에 저장
- 포인트 2: Secrets는 docker inspect로 안 보임
- 포인트 3: Secrets는 Git에 커밋되지 않음

**예시 답변**
> "Docker Secrets는 /run/secrets/ 경로에 파일로 마운트되어 컨테이너 내부에서만 접근 가능합니다. 반면 환경 변수는 docker inspect나 docker-compose.yml에서 볼 수 있어 보안에 취약합니다. Secrets는 로컬 파일로 관리하므로 .gitignore로 차단하면 Git에 절대 커밋되지 않습니다. 데이터베이스 비밀번호, API 키 등 민감한 정보는 반드시 Secrets로 관리해야 합니다."

**꼬리 질문**
- Q: Secrets는 어떻게 읽나요?
- A: fs.readFileSync('/run/secrets/db_password', 'utf8') 같은 방식으로 파일을 읽습니다.

**실무 연관**
- 보안 감사 시 환경 변수에 비밀번호가 있으면 탈락합니다. Secrets 사용이 필수입니다.

</details>

<details>
<summary><strong>5. 여러 개의 docker-compose 파일을 병합하는 순서가 왜 중요한가요?</strong></summary>

**모범 답안 포인트**
- 포인트 1: 나중에 지정한 파일이 이전 파일을 오버라이드
- 포인트 2: 배열은 병합, 단일 값은 교체
- 포인트 3: 순서를 바꾸면 의도와 다른 결과 발생

**예시 답변**
> "-f 옵션으로 지정한 파일은 순서대로 병합되며, 나중 파일이 이전 파일의 설정을 덮어씁니다. 예를 들어, docker compose -f docker-compose.yml -f docker-compose.prod.yml up 명령은 base 설정에 prod 설정을 덮어쓰지만, 순서를 바꾸면 prod 설정이 base로 다시 덮어써집니다. image 같은 단일 값은 교체되고, ports 같은 배열은 병합됩니다."

**꼬리 질문**
- Q: 병합 결과를 미리 확인하려면?
- A: docker compose config 명령으로 최종 병합 결과를 볼 수 있습니다.

**실무 연관**
- CI/CD 파이프라인에서 파일 순서를 잘못 지정하면 프로덕션에 개발 설정이 적용되는 심각한 사고가 발생할 수 있습니다.

</details>

<details>
<summary><strong>6. 프로파일이 있는 서비스와 없는 서비스를 함께 실행하면 어떻게 되나요?</strong></summary>

**모범 답안 포인트**
- 포인트 1: 프로파일 없는 서비스는 항상 실행
- 포인트 2: 프로파일 있는 서비스는 --profile 옵션 필요
- 포인트 3: 여러 프로파일 동시 지정 가능

**예시 답변**
> "프로파일이 없는 서비스는 기본 서비스로, docker compose up만 실행해도 항상 시작됩니다. 프로파일이 지정된 서비스는 --profile 옵션을 사용해야만 실행됩니다. 예를 들어, database와 api는 항상 실행하고, mailcatcher는 --profile dev를 줬을 때만 실행되도록 설계할 수 있습니다. --profile dev --profile monitoring처럼 여러 프로파일을 동시에 활성화할 수도 있습니다."

**꼬리 질문**
- Q: 모든 서비스를 강제로 실행하려면?
- A: --profile "*" 옵션을 사용하면 모든 프로파일의 서비스가 실행됩니다.

**실무 연관**
- 핵심 서비스는 프로파일 없이, 개발 도구/모니터링 도구는 프로파일로 분리하면 개발 환경이 훨씬 가벼워집니다.

</details>

<details>
<summary><strong>7. 스케일링 시 Nginx가 어떻게 여러 컨테이너로 트래픽을 분산하나요?</strong></summary>

**모범 답안 포인트**
- 포인트 1: Docker DNS가 서비스 이름을 모든 IP로 해석
- 포인트 2: Nginx upstream이 자동으로 로드밸런싱
- 포인트 3: 라운드 로빈 방식이 기본

**예시 답변**
> "Docker Compose는 내부 DNS를 제공하여 서비스 이름(예: api)을 해당 서비스의 모든 컨테이너 IP로 해석합니다. Nginx의 upstream 블록에서 server api:3000으로 지정하면, Docker DNS가 api-1, api-2, api-3의 IP를 모두 반환하고 Nginx는 이를 자동으로 로드밸런싱합니다. 기본적으로 라운드 로빈 방식으로 순차적으로 요청을 분배합니다."

**꼬리 질문**
- Q: 특정 컨테이너가 죽으면 어떻게 되나요?
- A: Nginx가 자동으로 해당 컨테이너로의 요청을 중단하고, 남은 컨테이너로만 트래픽을 보냅니다.

**실무 연관**
- 무중단 배포 시 일부 컨테이너를 업데이트하는 동안 나머지 컨테이너가 트래픽을 처리합니다.

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. BuildKit의 시크릿 마운트와 일반 Secrets의 차이점과 사용 사례를 설명하세요.</strong></summary>

**모범 답안 포인트**
- 포인트 1: BuildKit 시크릿은 빌드 타임, Docker Secrets는 런타임
- 포인트 2: BuildKit 시크릿은 이미지 레이어에 남지 않음
- 포인트 3: npm 인증, git 인증은 BuildKit, DB 비밀번호는 Docker Secrets

**예시 답변**
> "BuildKit 시크릿은 이미지 빌드 중에만 사용되고 최종 이미지에는 포함되지 않습니다. 반면 Docker Secrets는 컨테이너 실행 시 /run/secrets/로 마운트됩니다. Private npm 패키지를 설치할 때 .npmrc 파일이 필요하지만 이미지에 포함되면 안 되므로 BuildKit 시크릿을 사용합니다. 반면 데이터베이스 비밀번호는 런타임에 필요하므로 Docker Secrets를 사용합니다."

**실무 예시**:
```dockerfile
# BuildKit 시크릿 (빌드 타임)
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci
```

```yaml
# Docker Secrets (런타임)
services:
  api:
    secrets:
      - db_password
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password
```

**꼬리 질문**
- Q: BuildKit 시크릿 없이 .npmrc를 COPY하면 어떤 문제가 있나요?
- A: .npmrc가 이미지 레이어에 남아서 docker history로 볼 수 있고, 레지스트리에 푸시하면 누구나 인증 정보를 탈취할 수 있습니다.

**실무 연관**
- 보안 감사 시 이미지 레이어에 인증 정보가 남아있으면 심각한 취약점으로 분류됩니다. BuildKit 시크릿은 필수입니다.

</details>

<details>
<summary><strong>2. Docker Compose의 extends와 오버라이드 파일의 차이점과 각각의 장단점을 설명하세요.</strong></summary>

**모범 답안 포인트**
- 포인트 1: extends는 Compose v2.1에서 deprecated, 오버라이드가 권장
- 포인트 2: extends는 서비스 단위 상속, 오버라이드는 파일 단위 병합
- 포인트 3: 오버라이드가 더 직관적이고 유지보수 쉬움

**예시 답변**
> "extends는 특정 서비스의 설정을 다른 서비스에서 상속받는 기능이었지만, Compose v2.1부터 deprecated되었습니다. 현재는 오버라이드 파일 방식이 권장됩니다. extends는 서비스 단위로 상속받아 설정이 복잡해지고, 오버라이드는 파일 단위로 병합되어 더 직관적입니다. 오버라이드 방식은 환경별 파일 분리가 명확하고, -f 옵션으로 병합 순서를 제어할 수 있어 실무에서 더 많이 사용됩니다."

**실무 예시**:
```yaml
# ❌ extends (deprecated)
services:
  web:
    extends:
      file: common.yml
      service: base-service

# ✅ 오버라이드 (권장)
# docker-compose.yml (기본)
# docker-compose.prod.yml (프로덕션 추가)
# docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```

**꼬리 질문**
- Q: 오버라이드 방식의 단점은 없나요?
- A: 병합 순서를 명시적으로 관리해야 하고, 파일이 여러 개로 나뉘어 처음에는 복잡해 보일 수 있습니다.

**실무 연관**
- 대부분의 최신 프로젝트는 오버라이드 방식을 사용하며, extends를 사용하는 레거시 프로젝트는 마이그레이션을 권장합니다.

</details>

<details>
<summary><strong>3. 멀티스테이지 빌드에서 각 스테이지의 target을 Compose에서 어떻게 활용하나요?</strong></summary>

**모범 답안 포인트**
- 포인트 1: Dockerfile에 여러 스테이지 정의, Compose에서 target 선택
- 포인트 2: 개발/테스트/프로덕션별로 다른 스테이지 사용
- 포인트 3: 이미지 크기 최적화 및 빌드 시간 단축

**예시 답변**
> "멀티스테이지 빌드에서 Dockerfile에 development, test, production 스테이지를 정의하고, Compose의 build.target으로 환경별로 다른 스테이지를 선택할 수 있습니다. 개발 환경에서는 development 스테이지로 핫 리로드 도구와 디버거를 포함하고, 프로덕션에서는 production 스테이지로 최소한의 파일만 포함하여 이미지 크기를 줄입니다. 이를 통해 하나의 Dockerfile로 모든 환경을 관리할 수 있습니다."

**실무 예시**:
```dockerfile
# Dockerfile
FROM node:18 AS base
WORKDIR /app
COPY package*.json ./

FROM base AS development
RUN npm install
COPY . .
CMD ["npm", "run", "dev"]

FROM base AS production
RUN npm ci --only=production
COPY . .
CMD ["node", "server.js"]
```

```yaml
# docker-compose.yml
services:
  api:
    build:
      context: .
      target: development  # 개발 스테이지

# docker-compose.prod.yml
services:
  api:
    build:
      context: .
      target: production  # 프로덕션 스테이지
```

**꼬리 질문**
- Q: 멀티스테이지 빌드의 캐싱 전략은?
- A: 변경 빈도가 낮은 레이어(의존성 설치)를 앞에 두고, 자주 변경되는 레이어(소스 코드 복사)를 뒤에 두면 캐시 효율이 높아집니다.

**실무 연관**
- 프로덕션 이미지는 개발 이미지의 1/5 크기로 줄일 수 있어 배포 시간과 저장 비용이 크게 절감됩니다.

</details>

<details>
<summary><strong>4. Docker Compose에서 depends_on의 condition과 헬스체크를 활용한 의존성 관리 전략을 설명하세요.</strong></summary>

**모범 답안 포인트**
- 포인트 1: depends_on만으로는 실제 준비 여부 확인 불가
- 포인트 2: healthcheck로 서비스 준비 상태 감지
- 포인트 3: condition: service_healthy로 순서 보장

**예시 답변**
> "depends_on은 컨테이너 시작 순서만 제어할 뿐, 서비스가 실제로 준비됐는지는 확인하지 않습니다. 예를 들어 데이터베이스 컨테이너는 시작됐지만 PostgreSQL이 아직 준비되지 않아 API 서버가 연결 실패할 수 있습니다. healthcheck를 정의하고 depends_on에서 condition: service_healthy를 사용하면 데이터베이스가 완전히 준비된 후에야 API 서버가 시작됩니다."

**실무 예시**:
```yaml
services:
  database:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

  api:
    image: myapi
    depends_on:
      database:
        condition: service_healthy  # database가 healthy일 때까지 대기
```

**꼬리 질문**
- Q: healthcheck가 없으면 어떻게 해결하나요?
- A: wait-for-it.sh 같은 스크립트를 entrypoint에서 실행하거나, 애플리케이션에서 재시도 로직을 구현합니다.

**실무 연관**
- 마이크로서비스 아키텍처에서 서비스 간 의존성이 복잡할 때 healthcheck 기반 의존성 관리가 필수입니다.

</details>

<details>
<summary><strong>5. 프로덕션 환경에서 Docker Compose 대신 Kubernetes를 사용하는 이유와, Compose를 사용해도 되는 경우는 언제인가요?</strong></summary>

**모범 답안 포인트**
- 포인트 1: Kubernetes는 여러 서버 클러스터, 자동 스케일링, 롤링 업데이트 지원
- 포인트 2: Compose는 단일 서버, 수동 스케일링, 간단한 설정
- 포인트 3: 소규모 프로젝트나 팀 내부 도구는 Compose로 충분

**예시 답변**
> "Kubernetes는 여러 서버에 걸친 클러스터 관리, 자동 스케일링, 롤링 업데이트, 자가 치유 등 프로덕션급 기능을 제공합니다. 반면 Docker Compose는 단일 서버에서만 동작하고 수동 관리가 필요합니다. 하지만 소규모 프로젝트(일 방문자 1만 명 이하), 사내 도구, 스타트업 초기 단계에서는 Compose로도 충분합니다. Kubernetes는 학습 곡선이 가파르고 운영 비용이 높아서, 규모가 작을 때는 오히려 Compose가 더 효율적입니다."

**비교표**:

| 항목 | Docker Compose | Kubernetes |
|------|----------------|------------|
| 학습 난이도 | 쉬움 | 어려움 |
| 서버 수 | 단일 | 다중 (클러스터) |
| 자동 스케일링 | ❌ | ✅ (HPA) |
| 롤링 업데이트 | 수동 | ✅ (자동) |
| 자가 치유 | 제한적 | ✅ (자동) |
| 서비스 메시 | ❌ | ✅ (Istio 등) |
| 적합한 규모 | 소규모 | 대규모 |

**꼬리 질문**
- Q: Compose에서 Kubernetes로 마이그레이션하는 방법은?
- A: Kompose 도구를 사용하면 docker-compose.yml을 Kubernetes YAML로 변환할 수 있습니다.

**실무 연관**
- 많은 스타트업이 Compose로 시작해서 트래픽이 증가하면 Kubernetes로 전환합니다. 처음부터 Kubernetes를 도입하면 오버 엔지니어링이 될 수 있습니다.

</details>

---

## 📝 핵심 정리

### 이 장에서 배운 핵심 개념

| 개념 | 설명 | 핵심 키워드 |
|------|------|-------------|
| **프로파일** | 특정 서비스를 선택적으로 실행 | profiles, --profile, 개발 도구 분리 |
| **오버라이드** | 환경별 설정을 기본 설정에 추가/덮어쓰기 | docker-compose.override.yml, -f 옵션, 병합 |
| **스케일링** | 서비스 인스턴스를 동적으로 증감 | --scale, expose, 로드밸런싱 |
| **시크릿 관리** | 민감한 정보를 안전하게 관리 | secrets, /run/secrets/, 보안 |
| **멀티스테이지 빌드** | 단계별 빌드로 이미지 크기 최적화 | target, AS, 캐시 |

### 필수 명령어/코드 정리

| 명령어/코드 | 용도 | 예시 |
|-------------|------|------|
| `--profile <name>` | 특정 프로파일 실행 | `docker compose --profile dev up` |
| `-f <file>` | 여러 파일 병합 | `docker compose -f base.yml -f prod.yml up` |
| `--scale <service>=<num>` | 서비스 스케일링 | `docker compose up --scale api=5` |
| `config` | 병합 결과 확인 | `docker compose config` |
| `secrets:` | 시크릿 정의 | `secrets: - db_password` |
| `healthcheck:` | 서비스 준비 상태 감지 | `test: ["CMD", "pg_isready"]` |
| `depends_on: condition:` | 의존성 순서 보장 | `condition: service_healthy` |

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] 핵심 서비스는 프로파일 없이, 부가 도구는 프로파일로 분리
- [ ] 공통 설정은 docker-compose.yml에, 환경별 차이는 오버라이드 파일로
- [ ] 스케일링 대상 서비스는 expose 사용, container_name 제거
- [ ] 비밀 정보는 절대 환경 변수 사용 금지, Docker Secrets 사용
- [ ] healthcheck로 서비스 준비 상태 확인 후 의존 서비스 시작
- [ ] 멀티스테이지 빌드로 프로덕션 이미지 크기 최소화
- [ ] docker compose config로 병합 결과 항상 확인

#### ❌ 하지 말아야 할 것
- [ ] 모든 서비스를 항상 실행 (리소스 낭비)
- [ ] 환경별로 docker-compose 파일 전체 복사 (중복 코드)
- [ ] 스케일링 서비스에 ports 사용 (포트 충돌)
- [ ] .env 파일에 비밀번호 저장 후 Git 커밋 (보안 위험)
- [ ] depends_on만 사용 (실제 준비 여부 확인 안 됨)
- [ ] 프로덕션에서 docker-compose.override.yml 자동 적용

### 성능/보안 체크리스트

#### 성능
- [ ] 개발 환경 시작 시간 10초 이내 (프로파일로 최소화)
- [ ] 프로덕션 이미지 크기 100MB 이하 (멀티스테이지 빌드)
- [ ] 캐시 최적화 (변경 빈도 낮은 레이어 앞에 배치)
- [ ] 스케일링으로 트래픽 대응 (Nginx 로드밸런싱)

#### 보안
- [ ] 비밀번호는 Docker Secrets로만 관리
- [ ] secrets/ 디렉토리는 .gitignore로 차단
- [ ] docker inspect로 비밀 정보 노출 여부 확인
- [ ] BuildKit 시크릿으로 빌드 타임 인증 정보 보호
- [ ] 프로덕션 이미지에 개발 도구 포함 안 됨

---

## 🔗 관련 기술

**이 기술과 함께 사용하는 기술들**

| 기술 | 관계 | 학습 우선순위 |
|------|------|---------------|
| **Nginx** | 로드 밸런서, 리버스 프록시 | ⭐⭐⭐ (스케일링 필수) |
| **Docker Swarm** | 멀티 호스트 오케스트레이션 | ⭐⭐ (Compose 다음 단계) |
| **Kubernetes** | 프로덕션급 오케스트레이션 | ⭐⭐⭐ (대규모 서비스) |
| **Traefik** | 자동 서비스 디스커버리 | ⭐⭐ (동적 라우팅) |
| **Prometheus** | 모니터링 및 알림 | ⭐⭐⭐ (운영 필수) |
| **Vault** | 시크릿 관리 | ⭐⭐ (엔터프라이즈) |

---

## 🚀 다음 단계

### 다음 장 미리보기: 섹션 15: LK-Trade 프로젝트에 Docker 적용
- **배울 내용 1**: 실제 프로젝트를 Docker 컨테이너로 변환
- **배울 내용 2**: 개발/프로덕션 환경 분리 전략
- **배울 내용 3**: CI/CD 파이프라인 구축
- **실전 프로젝트**: LK-Trade 프로젝트 완전 Docker화

### 이 장과의 연결점
```
이번 장에서 배운 [프로파일, 오버라이드, 스케일링]
    ↓
다음 장에서 [실제 프로젝트에 적용]
    ↓
최종적으로 [프로덕션 배포 가능한 환경 구축]
```

### 준비하면 좋을 것들
```bash
# 다음 장 실습을 위한 준비
# 1. LK-Trade 프로젝트 클론
git clone https://github.com/your-repo/lk-trade.git

# 2. 프로젝트 구조 파악
tree -L 2 lk-trade/

# 3. 기존 설정 파일 확인
cat lk-trade/package.json
cat lk-trade/.env.example
```

---

## 🎉 축하합니다!

**이제 여러분은**:
✅ Docker Compose의 프로파일로 개발 환경을 효율적으로 관리할 수 있습니다
✅ 오버라이드 파일로 환경별 설정을 체계적으로 분리할 수 있습니다
✅ 스케일링으로 트래픽 변화에 즉시 대응할 수 있습니다
✅ Docker Secrets로 비밀 정보를 안전하게 관리할 수 있습니다
✅ 멀티스테이지 빌드로 프로덕션 이미지를 최적화할 수 있습니다
✅ 실무에서 Docker Compose를 프로덕션급으로 활용할 수 있습니다

**다음 단계**:
- [ ] 다음 장으로 진행 (LK-Trade 프로젝트 Docker 적용)
- [ ] 현재 진행 중인 프로젝트에 프로파일 적용해보기
- [ ] 면접 질문 복습 및 모범 답변 연습
- [ ] 주니어 시나리오를 실제로 재현해보며 학습

---

**다음 장으로 이동**: [다음: 15장 LK-Trade 프로젝트에 Docker 적용 →](15-LK-Trade-프로젝트-Docker-적용.md)

**이전 장으로 돌아가기**: [← 이전: 13장 Docker Compose 네트워크와 볼륨](13-Docker-Compose-네트워크와-볼륨.md)

**목차로 돌아가기**: [📚 전체 목차](README.md)