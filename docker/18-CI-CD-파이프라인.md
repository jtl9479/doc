# 18. CI/CD 파이프라인 구축 (GitHub Actions & GitLab CI)

> **학습 목표**: 이 장을 완료하면 GitHub Actions와 GitLab CI를 사용해 Docker 기반 자동화된 빌드, 테스트, 배포 파이프라인을 구축할 수 있습니다.

**⏱️ 예상 학습 시간**: 4-6시간
**난이도**: ⭐⭐⭐⭐☆ (4개/5개)

---

## 📚 목차
1. [왜 CI/CD가 필요한가](#왜-cicd가-필요한가)
2. [실생활 비유로 이해하기](#실생활-비유로-이해하기)
3. [CI/CD 기본 개념](#cicd-기본-개념)
4. [GitHub Actions 완전 가이드](#github-actions-완전-가이드)
5. [GitLab CI/CD 완전 가이드](#gitlab-cicd-완전-가이드)
6. [Docker 빌드 최적화](#docker-빌드-최적화)
7. [자동화된 테스트](#자동화된-테스트)
8. [이미지 스캐닝 및 보안](#이미지-스캐닝-및-보안)
9. [배포 자동화](#배포-자동화)
10. [실전 예제: LK-Trade 프로젝트](#실전-예제-lk-trade-프로젝트)
11. [주니어 시나리오](#주니어-시나리오)
12. [트러블슈팅](#트러블슈팅)
13. [FAQ](#faq)
14. [면접 질문 리스트](#면접-질문-리스트)
15. [핵심 정리](#핵심-정리)

---

## 🤔 왜 CI/CD가 필요한가?

### 실무 배경
**매주 금요일 저녁 6시마다 반복되는 악몽...**

#### ❌ CI/CD를 모르면 발생하는 문제
```
문제 1: 수동 배포의 지옥
- 증상: 개발자가 직접 서버 접속 → 코드 복사 → 빌드 → 재시작
- 영향: 1회 배포에 2시간 소요, 실수로 잘못된 버전 배포
- 비용: 개발자 야근 비용 월 $5,000, 장애 복구 비용 $10,000

문제 2: 테스트 누락으로 인한 장애
- 증상: 개발 환경에서만 테스트, 프로덕션에서 버그 발견
- 영향: 금요일 밤 11시 긴급 롤백, 고객 불만 증가
- 비용: 서비스 다운타임 1시간 = 매출 손실 $50,000

문제 3: 환경별 설정 불일치
- 증상: "제 컴퓨터에서는 되는데요?"
- 영향: 프로덕션 배포 후 환경 설정 오류로 서비스 중단
- 비용: 디버깅 시간 4시간, 팀 생산성 -30%
```

#### ✅ CI/CD를 사용하면
```
해결책 1: 완전 자동화된 배포
- 방법: Git Push → 자동 빌드 → 테스트 → 배포 (5분)
- 효과: 하루 10회 이상 안전한 배포 가능
- 절감: 개발자 시간 90% 절약, 월 $4,500 절감

해결책 2: 자동화된 품질 검증
- 방법: 모든 커밋마다 자동 테스트 + 보안 스캔
- 효과: 버그를 프로덕션 이전에 99% 차단
- 절감: 장애 대응 비용 80% 감소, $8,000/월 절약

해결책 3: 일관된 배포 환경
- 방법: Docker 이미지로 동일한 환경 보장
- 효과: 환경 문제로 인한 장애 제로
- 절감: 디버깅 시간 75% 감소, 팀 생산성 +50%
```

### 📊 수치로 보는 효과

| 지표 | Before (수동) | After (CI/CD) | 개선율 |
|------|--------------|--------------|--------|
| 배포 소요 시간 | 2시간 | 5분 | **96%↓** |
| 배포 빈도 | 주 1회 | 하루 10회 | **7000%↑** |
| 배포 실패율 | 30% | 2% | **93%↓** |
| 버그 발견 시점 | 프로덕션 | 커밋 단계 | **100%개선** |
| 롤백 시간 | 1시간 | 30초 | **99%↓** |
| 월간 운영 비용 | $15,000 | $3,000 | **80%↓** |

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 자동차 공장 생산 라인 🚗

**CI/CD = 자동차 공장의 자동화 생산 라인**

```
일반 작업장 (수동 배포)          자동화 공장 (CI/CD)
┌─────────────────┐              ┌─────────────────┐
│ 부품 수작업 조립│              │ 로봇 자동 조립  │
│ 한 명씩 검사    │     VS       │ 전수 자동 검사  │
│ 사람이 트럭 운전│              │ 자동 컨베이어   │
│ 하루 10대 생산  │              │ 하루 1000대 생산│
└─────────────────┘              └─────────────────┘

- CI (부품 조립): 엔진팀, 섀시팀의 부품을 자동으로 조립
- Test (품질 검사): 로봇이 모든 차량을 자동 검사
- CD (배송): 완성된 차를 자동으로 딜러샵까지 운송
```

**실무 적용**:
- 코드 푸시 = 부품 투입
- 자동 빌드 = 로봇 조립
- 자동 테스트 = 품질 검사
- 자동 배포 = 딜러샵 배송

### 비유 2: 배달앱의 자동 주문 처리 🍕

**CI/CD = 배달의민족 자동 주문 시스템**

```
전화 주문 (수동)                  앱 주문 (CI/CD)
┌─────────────────┐              ┌─────────────────┐
│ 1. 전화로 주문  │              │ 1. 앱에서 주문  │
│ 2. 종이에 메모  │              │ 2. 자동 접수    │
│ 3. 주방에 전달  │     VS       │ 3. 주방 자동 출력│
│ 4. 완료 전화    │              │ 4. 자동 알림    │
│ 5. 라이더 배정  │              │ 5. AI 배정      │
│ 실수율 20%      │              │ 실수율 0.1%     │
└─────────────────┘              └─────────────────┘

GitHub Push → (주문)
자동 빌드 → (주방에서 요리)
자동 테스트 → (품질 확인)
자동 배포 → (배달)
알림 → (Slack 알림)
```

### 비유 3: 아파트 건설 공정 관리 🏗️

**CI/CD = 스마트 건설 관리 시스템**

```
전통 건설 (수동)                  스마트 건설 (CI/CD)
┌─────────────────┐              ┌─────────────────┐
│ 종이 설계도     │              │ 3D BIM 모델     │
│ 수작업 측정     │              │ 센서 자동 측정  │
│ 육안 검사       │     VS       │ 드론 자동 검사  │
│ 전화로 보고     │              │ 실시간 대시보드 │
│ 월 1회 점검     │              │ 24시간 모니터링 │
└─────────────────┘              └─────────────────┘

Feature 브랜치 = 각 층 건설
Pull Request = 층별 검사
Merge = 층 연결
Deploy = 입주
```

### 비유 4: 병원 응급실 프로토콜 🏥

**CI/CD = 응급실 자동 환자 분류 시스템**

```
┌──────────────────────────────────┐
│      응급실 환자 처리 과정       │
├──────────────────────────────────┤
│ 1. 환자 도착 (코드 푸시)         │
│    ↓                             │
│ 2. 트리아지 (자동 빌드)          │
│    ↓                             │
│ 3. 활력징후 측정 (단위 테스트)   │
│    ↓                             │
│ 4. 검사 (통합 테스트)            │
│    ↓                             │
│ 5. 치료 (스테이징 배포)          │
│    ↓                             │
│ 6. 관찰 (모니터링)               │
│    ↓                             │
│ 7. 퇴원 (프로덕션 배포)          │
└──────────────────────────────────┘

중증도 자동 분류 = 빌드 우선순위
생명징후 모니터링 = Health Check
응급 호출 = Slack 알림
```

### 비유 5: 공항 수하물 처리 시스템 ✈️

**CI/CD = 인천공항 자동 수하물 시스템**

```
수동 처리                        자동 컨베이어
┌─────────────────┐              ┌─────────────────┐
│ 사람이 카트 운반│              │ 바코드 스캔     │
│ 수작업 분류     │              │ 자동 분류       │
│ 눈으로 확인     │     VS       │ X-ray 자동 검사 │
│ 분실률 1%       │              │ 분실률 0.001%   │
│ 처리속도 100개/h│              │ 처리속도 3000개/h│
└─────────────────┘              └─────────────────┘

체크인 (Git Push)
    ↓
바코드 부착 (버전 태그)
    ↓
X-ray 검사 (보안 스캔)
    ↓
자동 분류 (환경별 배포)
    ↓
탑승 게이트 (프로덕션)
    ↓
추적 시스템 (모니터링)
```

### 비유 6: 넷플릭스 콘텐츠 배포 📺

**CI/CD = 넷플릭스 자동 인코딩 및 배포**

```
전통 방송 (수동)                  넷플릭스 (CI/CD)
┌─────────────────┐              ┌─────────────────┐
│ 테이프 편집     │              │ 클라우드 인코딩 │
│ 품질 수동 확인  │              │ 자동 품질 검사  │
│ 위성 송출       │     VS       │ CDN 자동 배포   │
│ 정해진 시간     │              │ 언제든지 시청   │
│ 1개 화질        │              │ 자동 화질 조절  │
└─────────────────┘              └─────────────────┘

영상 업로드 = 코드 푸시
자동 인코딩 = Docker 빌드
품질 검사 = 자동 테스트
CDN 배포 = 멀티 리전 배포
A/B 테스트 = 카나리 배포
```

### 🎯 종합 비교표

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ CI/CD 단계   │ 자동차 공장  │ 배달앱       │ 공항 수하물  │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ Source       │ 부품 입고    │ 주문 접수    │ 체크인       │
│ Build        │ 자동 조립    │ 요리 시작    │ 바코드 부착  │
│ Test         │ 품질 검사    │ 맛 확인      │ X-ray 검사   │
│ Deploy       │ 딜러샵 배송  │ 배달 출발    │ 게이트 이동  │
│ Monitor      │ 차량 추적    │ 배달 추적    │ 수하물 추적  │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

---

## 📖 CI/CD 기본 개념

### Docker와 CI/CD

```
개발자 코드 푸시
    ↓
[CI 파이프라인 시작]
    ↓
1. 코드 체크아웃
    ↓
2. Docker 이미지 빌드
    ↓
3. 단위 테스트 실행
    ↓
4. 통합 테스트 실행
    ↓
5. 보안 스캔 (Trivy)
    ↓
6. 이미지 레지스트리 푸시
    ↓
[CD 파이프라인 시작]
    ↓
7. 스테이징 배포
    ↓
8. 스모크 테스트
    ↓
9. 프로덕션 배포 (승인 필요)
    ↓
10. 헬스체크
```

---

## GitHub Actions 완전 가이드

### 기본 워크플로우 구조

```yaml
# .github/workflows/ci.yml

name: CI Pipeline

# 워크플로우가 실행될 조건
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  # 매일 새벽 3시에 자동 실행
  schedule:
    - cron: '0 3 * * *'

# 환경 변수 (전역)
env:
  DOCKER_REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # 첫 번째 작업: 빌드 및 테스트
  build:
    runs-on: ubuntu-latest

    steps:
      # 1. 코드 체크아웃
      - name: Checkout code
        uses: actions/checkout@v4

      # 2. JDK 설정 (Gradle 프로젝트)
      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: 'gradle'

      # 3. Gradle 빌드 및 테스트
      - name: Build with Gradle
        run: |
          chmod +x ./gradlew
          ./gradlew clean build

      # 4. 테스트 결과 업로드
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: |
            **/build/test-results/**
            **/build/reports/**

      # 5. 테스트 커버리지 리포트
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: ./build/reports/jacoco/test/jacocoTestReport.xml
          flags: unittests
          name: codecov-umbrella
```

### Docker 빌드 및 푸시

```yaml
# .github/workflows/docker-build.yml

name: Docker Build and Push

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      # Trivy 보안 스캔 결과 업로드를 위한 권한
      security-events: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      # Docker Buildx 설정 (멀티 플랫폼 빌드 지원)
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      # GitHub Container Registry 로그인
      - name: Log in to Container Registry
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      # Docker 이미지 메타데이터 추출
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            # 브랜치-SHA
            type=ref,event=branch
            # PR 번호
            type=ref,event=pr
            # Git 태그
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            # latest 태그 (main 브랜치만)
            type=raw,value=latest,enable={{is_default_branch}}

      # Docker 이미지 빌드 및 푸시
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            BUILD_DATE=${{ github.event.head_commit.timestamp }}
            VCS_REF=${{ github.sha }}
            VERSION=${{ steps.meta.outputs.version }}

      # 이미지 보안 스캔 (Trivy)
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ steps.meta.outputs.version }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'
```

### 멀티 모듈 프로젝트 빌드

```yaml
# .github/workflows/multi-module-build.yml

name: Multi-Module Build

on:
  push:
    branches: [ main, develop ]

env:
  REGISTRY: ghcr.io

jobs:
  # 변경된 모듈 감지
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      user: ${{ steps.filter.outputs.user }}
      account: ${{ steps.filter.outputs.account }}
      trade: ${{ steps.filter.outputs.trade }}
      ai: ${{ steps.filter.outputs.ai }}
      scraper: ${{ steps.filter.outputs.scraper }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            user:
              - 'modules/user/**'
            account:
              - 'modules/account/**'
            trade:
              - 'modules/trade/**'
            ai:
              - 'modules/ai/**'
            scraper:
              - 'modules/scraper/**'

  # User 모듈 빌드
  build-user-module:
    needs: detect-changes
    if: needs.detect-changes.outputs.user == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: 'gradle'

      - name: Build User Module
        run: |
          ./gradlew :modules:user:api:build

      - name: Build Docker Image
        uses: docker/build-push-action@v5
        with:
          context: ./modules/user
          push: true
          tags: ${{ env.REGISTRY }}/${{ github.repository }}/user-service:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # Account 모듈 빌드 (동일 패턴)
  build-account-module:
    needs: detect-changes
    if: needs.detect-changes.outputs.account == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: 'gradle'

      - name: Build Account Module
        run: |
          ./gradlew :modules:account:api:build

      - name: Build Docker Image
        uses: docker/build-push-action@v5
        with:
          context: ./modules/account
          push: true
          tags: ${{ env.REGISTRY }}/${{ github.repository }}/account-service:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # 통합 테스트
  integration-test:
    needs: [build-user-module, build-account-module]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Start services with docker-compose
        run: |
          docker-compose -f docker-compose.test.yml up -d

      - name: Wait for services
        run: |
          timeout 60 bash -c 'until curl -f http://localhost:8081/actuator/health; do sleep 2; done'
          timeout 60 bash -c 'until curl -f http://localhost:8082/actuator/health; do sleep 2; done'

      - name: Run integration tests
        run: |
          ./gradlew integrationTest

      - name: Collect logs
        if: failure()
        run: |
          docker-compose -f docker-compose.test.yml logs > logs.txt

      - name: Upload logs
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: integration-test-logs
          path: logs.txt

      - name: Cleanup
        if: always()
        run: |
          docker-compose -f docker-compose.test.yml down -v
```

### 재사용 가능한 워크플로우

```yaml
# .github/workflows/reusable-docker-build.yml

name: Reusable Docker Build

on:
  workflow_call:
    inputs:
      module_name:
        required: true
        type: string
      context_path:
        required: true
        type: string
      dockerfile_path:
        required: false
        type: string
        default: 'Dockerfile'
    secrets:
      registry_username:
        required: true
      registry_password:
        required: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ secrets.registry_username }}
          password: ${{ secrets.registry_password }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ${{ inputs.context_path }}
          file: ${{ inputs.context_path }}/${{ inputs.dockerfile_path }}
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/${{ inputs.module_name }}:latest
            ghcr.io/${{ github.repository }}/${{ inputs.module_name }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**재사용 워크플로우 호출**:

```yaml
# .github/workflows/build-all-modules.yml

name: Build All Modules

on:
  push:
    branches: [ main ]

jobs:
  build-user:
    uses: ./.github/workflows/reusable-docker-build.yml
    with:
      module_name: user-service
      context_path: ./modules/user
    secrets:
      registry_username: ${{ github.actor }}
      registry_password: ${{ secrets.GITHUB_TOKEN }}

  build-account:
    uses: ./.github/workflows/reusable-docker-build.yml
    with:
      module_name: account-service
      context_path: ./modules/account
    secrets:
      registry_username: ${{ github.actor }}
      registry_password: ${{ secrets.GITHUB_TOKEN }}
```

---

## GitLab CI/CD 완전 가이드

### 기본 파이프라인 구조

```yaml
# .gitlab-ci.yml

# 파이프라인의 단계 정의
stages:
  - build
  - test
  - security
  - package
  - deploy

# 전역 변수
variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"
  DOCKER_HOST: tcp://docker:2376
  DOCKER_TLS_VERIFY: 1
  DOCKER_CERT_PATH: "$DOCKER_TLS_CERTDIR/client"
  GRADLE_OPTS: "-Dorg.gradle.daemon=false"
  REGISTRY: $CI_REGISTRY
  IMAGE_TAG: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA

# Docker-in-Docker 서비스
services:
  - docker:24-dind

# 빌드 전에 실행되는 스크립트
before_script:
  - echo "Pipeline started for commit $CI_COMMIT_SHORT_SHA"

# 빌드 작업
build:
  stage: build
  image: gradle:8.5-jdk21
  script:
    - echo "Building application..."
    - chmod +x ./gradlew
    - ./gradlew clean build -x test
  artifacts:
    paths:
      - "**/build/libs/*.jar"
    expire_in: 1 day
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - .gradle/wrapper
      - .gradle/caches
  only:
    - main
    - develop
    - merge_requests

# 단위 테스트
unit-test:
  stage: test
  image: gradle:8.5-jdk21
  script:
    - echo "Running unit tests..."
    - ./gradlew test
  coverage: '/Total.*?([0-9]{1,3})%/'
  artifacts:
    when: always
    reports:
      junit:
        - "**/build/test-results/test/TEST-*.xml"
      coverage_report:
        coverage_format: cobertura
        path: "**/build/reports/cobertura-coverage.xml"
    paths:
      - "**/build/reports/"
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - .gradle/wrapper
      - .gradle/caches
    policy: pull

# 통합 테스트
integration-test:
  stage: test
  image: gradle:8.5-jdk21
  services:
    - postgres:15
    - redis:7
  variables:
    POSTGRES_DB: testdb
    POSTGRES_USER: testuser
    POSTGRES_PASSWORD: testpass
    REDIS_HOST: redis
    DATABASE_URL: postgresql://postgres:5432/testdb
  script:
    - echo "Running integration tests..."
    - ./gradlew integrationTest
  artifacts:
    when: always
    reports:
      junit:
        - "**/build/test-results/integrationTest/TEST-*.xml"
  only:
    - main
    - develop

# 보안 스캔 (SAST)
sast:
  stage: security
  image: returntocorp/semgrep
  script:
    - semgrep --config=auto --json --output=sast-report.json .
  artifacts:
    reports:
      sast: sast-report.json
  allow_failure: true

# 의존성 스캔
dependency-scan:
  stage: security
  image: gradle:8.5-jdk21
  script:
    - ./gradlew dependencyCheckAnalyze
  artifacts:
    paths:
      - build/reports/dependency-check-report.html
  allow_failure: true
```

### Docker 이미지 빌드 및 푸시

```yaml
# Docker 빌드 작업 추가

# User Service 이미지 빌드
build-user-image:
  stage: package
  image: docker:24
  services:
    - docker:24-dind
  before_script:
    - echo $CI_REGISTRY_PASSWORD | docker login -u $CI_REGISTRY_USER --password-stdin $CI_REGISTRY
  script:
    - cd modules/user
    - |
      docker build \
        --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
        --build-arg VCS_REF=$CI_COMMIT_SHORT_SHA \
        --build-arg VERSION=$CI_COMMIT_TAG \
        --cache-from $CI_REGISTRY_IMAGE/user-service:latest \
        --tag $CI_REGISTRY_IMAGE/user-service:$CI_COMMIT_SHORT_SHA \
        --tag $CI_REGISTRY_IMAGE/user-service:latest \
        .
    - docker push $CI_REGISTRY_IMAGE/user-service:$CI_COMMIT_SHORT_SHA
    - docker push $CI_REGISTRY_IMAGE/user-service:latest
  only:
    - main
    - tags
  dependencies:
    - build

# Account Service 이미지 빌드
build-account-image:
  stage: package
  image: docker:24
  services:
    - docker:24-dind
  before_script:
    - echo $CI_REGISTRY_PASSWORD | docker login -u $CI_REGISTRY_USER --password-stdin $CI_REGISTRY
  script:
    - cd modules/account
    - |
      docker build \
        --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
        --build-arg VCS_REF=$CI_COMMIT_SHORT_SHA \
        --build-arg VERSION=$CI_COMMIT_TAG \
        --cache-from $CI_REGISTRY_IMAGE/account-service:latest \
        --tag $CI_REGISTRY_IMAGE/account-service:$CI_COMMIT_SHORT_SHA \
        --tag $CI_REGISTRY_IMAGE/account-service:latest \
        .
    - docker push $CI_REGISTRY_IMAGE/account-service:$CI_COMMIT_SHORT_SHA
    - docker push $CI_REGISTRY_IMAGE/account-service:latest
  only:
    - main
    - tags
  dependencies:
    - build

# Trivy 보안 스캔
trivy-scan:
  stage: security
  image: aquasec/trivy:latest
  services:
    - docker:24-dind
  before_script:
    - echo $CI_REGISTRY_PASSWORD | docker login -u $CI_REGISTRY_USER --password-stdin $CI_REGISTRY
  script:
    - trivy image --exit-code 0 --no-progress --format json -o trivy-report.json $CI_REGISTRY_IMAGE/user-service:$CI_COMMIT_SHORT_SHA
    - trivy image --exit-code 1 --severity CRITICAL --no-progress $CI_REGISTRY_IMAGE/user-service:$CI_COMMIT_SHORT_SHA
  artifacts:
    paths:
      - trivy-report.json
  allow_failure: true
  dependencies:
    - build-user-image
```

### 동적 환경 배포

```yaml
# 스테이징 배포
deploy-staging:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
    - ssh-keyscan $STAGING_SERVER >> ~/.ssh/known_hosts
  script:
    - |
      ssh $STAGING_USER@$STAGING_SERVER << 'EOF'
        cd /opt/lk-trade
        export IMAGE_TAG=$CI_COMMIT_SHORT_SHA
        docker-compose pull
        docker-compose up -d
        docker-compose ps
      EOF
  environment:
    name: staging
    url: https://staging.lk-trade.com
    on_stop: stop-staging
  only:
    - develop

# 스테이징 환경 중지
stop-staging:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
  script:
    - |
      ssh $STAGING_USER@$STAGING_SERVER << 'EOF'
        cd /opt/lk-trade
        docker-compose down
      EOF
  environment:
    name: staging
    action: stop
  when: manual

# 프로덕션 배포 (수동 승인 필요)
deploy-production:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
    - ssh-keyscan $PROD_SERVER >> ~/.ssh/known_hosts
  script:
    - |
      ssh $PROD_USER@$PROD_SERVER << 'EOF'
        cd /opt/lk-trade
        export IMAGE_TAG=$CI_COMMIT_SHORT_SHA

        # 블루-그린 배포
        # 1. 새 버전 시작 (다른 포트)
        docker-compose -f docker-compose.blue.yml pull
        docker-compose -f docker-compose.blue.yml up -d

        # 2. 헬스체크 대기
        sleep 30
        curl -f http://localhost:8081/actuator/health || exit 1

        # 3. Nginx 설정 변경 (블루로 트래픽 전환)
        docker exec nginx nginx -s reload

        # 4. 이전 버전 종료
        docker-compose -f docker-compose.green.yml down

        # 5. 블루를 그린으로 변경
        mv docker-compose.blue.yml docker-compose.green.yml
      EOF
  environment:
    name: production
    url: https://lk-trade.com
  when: manual
  only:
    - main
    - tags
```

### 멀티 프로젝트 파이프라인

```yaml
# .gitlab-ci.yml (루트)

include:
  - local: 'modules/user/.gitlab-ci.yml'
  - local: 'modules/account/.gitlab-ci.yml'
  - local: 'modules/trade/.gitlab-ci.yml'
  - local: 'modules/ai/.gitlab-ci.yml'
  - local: 'modules/scraper/.gitlab-ci.yml'

stages:
  - build
  - test
  - security
  - package
  - deploy

# 전역 변수
variables:
  DOCKER_DRIVER: overlay2
  REGISTRY: $CI_REGISTRY

# 통합 테스트 (모든 모듈 빌드 후 실행)
integration-test-all:
  stage: test
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker-compose -f docker-compose.test.yml up -d
    - sleep 30
    - docker-compose -f docker-compose.test.yml exec -T user-service curl -f http://localhost:8080/actuator/health
    - docker-compose -f docker-compose.test.yml exec -T account-service curl -f http://localhost:8080/actuator/health
    - docker-compose -f docker-compose.test.yml down -v
  needs:
    - job: build-user
    - job: build-account
    - job: build-trade
```

**모듈별 파이프라인 (예: modules/user/.gitlab-ci.yml)**:

```yaml
# modules/user/.gitlab-ci.yml

build-user:
  stage: build
  image: gradle:8.5-jdk21
  script:
    - cd modules/user
    - ../../gradlew :modules:user:api:build
  artifacts:
    paths:
      - modules/user/api/build/libs/*.jar
  cache:
    key: user-${CI_COMMIT_REF_SLUG}
    paths:
      - .gradle/

test-user:
  stage: test
  image: gradle:8.5-jdk21
  script:
    - cd modules/user
    - ../../gradlew :modules:user:api:test
  artifacts:
    reports:
      junit: modules/user/api/build/test-results/test/TEST-*.xml

package-user:
  stage: package
  image: docker:24
  services:
    - docker:24-dind
  before_script:
    - echo $CI_REGISTRY_PASSWORD | docker login -u $CI_REGISTRY_USER --password-stdin $CI_REGISTRY
  script:
    - cd modules/user
    - docker build -t $CI_REGISTRY_IMAGE/user-service:$CI_COMMIT_SHORT_SHA .
    - docker push $CI_REGISTRY_IMAGE/user-service:$CI_COMMIT_SHORT_SHA
  needs:
    - build-user
```

---

## Docker 빌드 최적화

### BuildKit 캐시 최적화

```yaml
# GitHub Actions에서 BuildKit 캐시 사용

- name: Build with cache
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
    cache-from: |
      type=gha,scope=main
      type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache
    cache-to: type=gha,mode=max,scope=main
    build-args: |
      BUILDKIT_INLINE_CACHE=1
```

### 레이어 캐싱 전략

```dockerfile
# Dockerfile (최적화된 버전)

# syntax=docker/dockerfile:1

FROM gradle:8.5-jdk21 AS builder

WORKDIR /app

# 1단계: 의존성만 먼저 다운로드 (캐싱 최대화)
COPY build.gradle.kts settings.gradle.kts ./
COPY gradle ./gradle
RUN gradle dependencies --no-daemon

# 2단계: 소스 코드 복사 및 빌드
COPY src ./src
RUN gradle build -x test --no-daemon

# 3단계: 런타임 이미지
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# 비루트 사용자 생성
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

# JAR 파일 복사
COPY --from=builder /app/build/libs/*.jar app.jar

# 소유권 변경
RUN chown appuser:appuser app.jar

USER appuser

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

### 멀티 아키텍처 빌드

```yaml
# GitHub Actions: ARM64 + AMD64 동시 빌드

- name: Set up QEMU
  uses: docker/setup-qemu-action@v3

- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build multi-arch image
  uses: docker/build-push-action@v5
  with:
    context: .
    platforms: linux/amd64,linux/arm64,linux/arm/v7
    push: true
    tags: |
      ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
      ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

---

## 자동화된 테스트

### Docker Compose로 테스트 환경 구성

```yaml
# docker-compose.test.yml

version: '3.8'

services:
  # 테스트용 PostgreSQL
  postgres-test:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: testdb
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpass
    ports:
      - "5432:5432"
    tmpfs:
      - /var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U testuser -d testdb"]
      interval: 5s
      timeout: 5s
      retries: 5

  # 테스트용 Redis
  redis-test:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    tmpfs:
      - /data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  # User Service
  user-service:
    build:
      context: ./modules/user
      target: builder
    environment:
      SPRING_PROFILES_ACTIVE: test
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres-test:5432/testdb
      SPRING_DATASOURCE_USERNAME: testuser
      SPRING_DATASOURCE_PASSWORD: testpass
      SPRING_DATA_REDIS_HOST: redis-test
    depends_on:
      postgres-test:
        condition: service_healthy
      redis-test:
        condition: service_healthy
    ports:
      - "8081:8080"
    command: ["./gradlew", "test", "integrationTest"]
    volumes:
      - ./modules/user:/app
      - gradle-cache:/root/.gradle

volumes:
  gradle-cache:
```

### 테스트 실행 스크립트

```bash
#!/bin/bash
# scripts/run-tests.sh

set -e

echo "🚀 Starting test environment..."

# 테스트 컨테이너 시작
docker-compose -f docker-compose.test.yml up -d postgres-test redis-test

# 서비스 준비 대기
echo "⏳ Waiting for services to be ready..."
timeout 60 bash -c 'until docker-compose -f docker-compose.test.yml exec -T postgres-test pg_isready -U testuser; do sleep 2; done'
timeout 60 bash -c 'until docker-compose -f docker-compose.test.yml exec -T redis-test redis-cli ping; do sleep 2; done'

echo "✅ Services are ready"

# 단위 테스트
echo "🧪 Running unit tests..."
./gradlew test

# 통합 테스트
echo "🔗 Running integration tests..."
./gradlew integrationTest

# E2E 테스트
echo "🎭 Running E2E tests..."
docker-compose -f docker-compose.test.yml up --abort-on-container-exit user-service

# 테스트 결과 수집
echo "📊 Collecting test results..."
mkdir -p build/test-reports
find . -path "*/build/test-results/**/*.xml" -exec cp {} build/test-reports/ \;

# 정리
echo "🧹 Cleaning up..."
docker-compose -f docker-compose.test.yml down -v

echo "✅ All tests completed!"
```

### GitHub Actions 테스트 워크플로우

```yaml
# .github/workflows/test.yml

name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: 'gradle'

      - name: Run unit tests
        run: ./gradlew test

      - name: Generate test report
        if: always()
        uses: dorny/test-reporter@v1
        with:
          name: Unit Test Results
          path: '**/build/test-results/test/TEST-*.xml'
          reporter: java-junit

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: testdb
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: 'gradle'

      - name: Run integration tests
        env:
          SPRING_DATASOURCE_URL: jdbc:postgresql://localhost:5432/testdb
          SPRING_DATASOURCE_USERNAME: testuser
          SPRING_DATASOURCE_PASSWORD: testpass
          SPRING_DATA_REDIS_HOST: localhost
        run: ./gradlew integrationTest

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Start application stack
        run: |
          docker-compose -f docker-compose.test.yml up -d

      - name: Wait for services
        run: |
          timeout 120 bash -c 'until curl -f http://localhost:8081/actuator/health; do sleep 5; done'
          timeout 120 bash -c 'until curl -f http://localhost:8082/actuator/health; do sleep 5; done'

      - name: Run E2E tests
        run: |
          ./gradlew e2eTest

      - name: Collect logs on failure
        if: failure()
        run: |
          docker-compose -f docker-compose.test.yml logs > e2e-logs.txt

      - name: Upload logs
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: e2e-logs
          path: e2e-logs.txt

      - name: Cleanup
        if: always()
        run: |
          docker-compose -f docker-compose.test.yml down -v
```

---

## 이미지 스캐닝 및 보안

### Trivy를 이용한 취약점 스캔

```yaml
# .github/workflows/security-scan.yml

name: Security Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    # 매일 자정에 스캔
    - cron: '0 0 * * *'

jobs:
  trivy-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: |
          docker build -t test-image:${{ github.sha }} .

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'test-image:${{ github.sha }}'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH,MEDIUM'
          exit-code: '1'  # HIGH 이상 발견 시 실패

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Generate HTML report
        if: always()
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'test-image:${{ github.sha }}'
          format: 'template'
          template: '@/contrib/html.tpl'
          output: 'trivy-report.html'

      - name: Upload HTML report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: trivy-report
          path: trivy-report.html
```

### Snyk를 이용한 의존성 스캔

```yaml
# .github/workflows/snyk-scan.yml

name: Snyk Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  snyk:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: 'gradle'

      # 의존성 스캔
      - name: Run Snyk to check for vulnerabilities
        uses: snyk/actions/gradle@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
          command: test

      # Docker 이미지 스캔
      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Run Snyk on Docker image
        uses: snyk/actions/docker@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          image: myapp:${{ github.sha }}
          args: --severity-threshold=high
```

### Hadolint로 Dockerfile 린팅

```yaml
# .github/workflows/dockerfile-lint.yml

name: Dockerfile Lint

on:
  push:
    paths:
      - '**/Dockerfile*'
  pull_request:
    paths:
      - '**/Dockerfile*'

jobs:
  hadolint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Hadolint
        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile
          failure-threshold: warning
          format: sarif
          output-file: hadolint-results.sarif

      - name: Upload Hadolint results
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: hadolint-results.sarif
```

### 보안 체크리스트 자동화

```yaml
# .github/workflows/security-checklist.yml

name: Security Checklist

on:
  pull_request:
    branches: [ main ]

jobs:
  security-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # 1. 시크릿 스캔
      - name: Scan for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD

      # 2. Dockerfile 보안 체크
      - name: Check Dockerfile security
        run: |
          # Root 사용자 체크
          if grep -r "USER root" **/Dockerfile; then
            echo "::error::Dockerfile should not use root user"
            exit 1
          fi

          # ADD 대신 COPY 사용 체크
          if grep -r "^ADD" **/Dockerfile | grep -v ".tar"; then
            echo "::warning::Consider using COPY instead of ADD"
          fi

      # 3. 의존성 버전 체크
      - name: Check dependency versions
        run: |
          ./gradlew dependencyUpdates -Drevision=release

      # 4. 이미지 크기 체크
      - name: Check image size
        run: |
          docker build -t temp-image .
          SIZE=$(docker images temp-image --format "{{.Size}}")
          echo "Image size: $SIZE"

          # 500MB 초과 시 경고
          if [ $(docker images temp-image --format "{{.Size}}" | sed 's/MB//;s/GB/*1024/') -gt 500 ]; then
            echo "::warning::Image size exceeds 500MB"
          fi
```

---

## 배포 자동화

### Kubernetes 배포

```yaml
# .github/workflows/deploy-k8s.yml

name: Deploy to Kubernetes

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'latest'

      - name: Configure kubectl
        run: |
          echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig.yaml
          export KUBECONFIG=kubeconfig.yaml

      - name: Update deployment image
        run: |
          kubectl set image deployment/user-service \
            user-service=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/user-service:${{ github.sha }} \
            -n lk-trade

          kubectl set image deployment/account-service \
            account-service=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/account-service:${{ github.sha }} \
            -n lk-trade

      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/user-service -n lk-trade --timeout=5m
          kubectl rollout status deployment/account-service -n lk-trade --timeout=5m

      - name: Verify deployment
        run: |
          kubectl get pods -n lk-trade
          kubectl get services -n lk-trade

      - name: Run smoke tests
        run: |
          USER_SERVICE_URL=$(kubectl get svc user-service -n lk-trade -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
          curl -f http://$USER_SERVICE_URL/actuator/health || exit 1
```

### Docker Swarm 배포

```yaml
# .github/workflows/deploy-swarm.yml

name: Deploy to Docker Swarm

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Copy files to swarm manager
        uses: appleboy/scp-action@master
        with:
          host: ${{ secrets.SWARM_HOST }}
          username: ${{ secrets.SWARM_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          source: "docker-compose.yml,docker-compose.prod.yml"
          target: "/opt/lk-trade"

      - name: Deploy to swarm
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SWARM_HOST }}
          username: ${{ secrets.SWARM_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/lk-trade
            export IMAGE_TAG=${{ github.sha }}
            docker stack deploy -c docker-compose.yml -c docker-compose.prod.yml lk-trade

            # 서비스 업데이트 확인
            docker service ls

            # 롤링 업데이트 상태 확인
            docker service ps lk-trade_user-service --filter "desired-state=running"
```

### Watchtower를 이용한 자동 업데이트

```yaml
# docker-compose.prod.yml에 Watchtower 추가

services:
  # ... 기존 서비스들 ...

  # Watchtower: 자동 이미지 업데이트
  watchtower:
    image: containrrr/watchtower:latest
    container_name: watchtower
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ~/.docker/config.json:/config.json:ro
    environment:
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_POLL_INTERVAL=300  # 5분마다 체크
      - WATCHTOWER_ROLLING_RESTART=true
      - WATCHTOWER_INCLUDE_RESTARTING=true
      - WATCHTOWER_NOTIFICATIONS=slack
      - WATCHTOWER_NOTIFICATION_SLACK_HOOK_URL=${SLACK_WEBHOOK}
      - WATCHTOWER_NOTIFICATION_SLACK_IDENTIFIER=watchtower-prod
    labels:
      - "com.centurylinklabs.watchtower.enable=false"  # 자기 자신은 업데이트 안함
```

---

## 실전 예제: LK-Trade 프로젝트

### 전체 CI/CD 파이프라인

```yaml
# .github/workflows/lk-trade-cicd.yml

name: LK-Trade CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: ${{ github.repository }}

jobs:
  # 1단계: 변경 감지
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      modules: ${{ steps.filter.outputs.changes }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            user:
              - 'modules/user/**'
            account:
              - 'modules/account/**'
            trade:
              - 'modules/trade/**'
            ai:
              - 'modules/ai/**'
            scraper:
              - 'modules/scraper/**'

  # 2단계: 빌드 및 테스트
  build-and-test:
    needs: detect-changes
    if: ${{ needs.detect-changes.outputs.modules != '[]' }}
    runs-on: ubuntu-latest
    strategy:
      matrix:
        module: ${{ fromJSON(needs.detect-changes.outputs.modules) }}
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: 'gradle'

      - name: Build ${{ matrix.module }} module
        run: |
          ./gradlew :modules:${{ matrix.module }}:api:build

      - name: Run unit tests
        run: |
          ./gradlew :modules:${{ matrix.module }}:api:test

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.module }}-jar
          path: modules/${{ matrix.module }}/api/build/libs/*.jar

  # 3단계: Docker 이미지 빌드
  build-images:
    needs: [detect-changes, build-and-test]
    if: ${{ needs.detect-changes.outputs.modules != '[]' }}
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    strategy:
      matrix:
        module: ${{ fromJSON(needs.detect-changes.outputs.modules) }}
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push ${{ matrix.module }} image
        uses: docker/build-push-action@v5
        with:
          context: ./modules/${{ matrix.module }}
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/${{ matrix.module }}-service:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/${{ matrix.module }}-service:${{ github.sha }}
          cache-from: type=gha,scope=${{ matrix.module }}
          cache-to: type=gha,mode=max,scope=${{ matrix.module }}

  # 4단계: 보안 스캔
  security-scan:
    needs: build-images
    runs-on: ubuntu-latest
    strategy:
      matrix:
        module: [user, account, trade, ai, scraper]
    steps:
      - name: Run Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/${{ matrix.module }}-service:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-${{ matrix.module }}.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload results
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: 'trivy-${{ matrix.module }}.sarif'

  # 5단계: 통합 테스트
  integration-test:
    needs: build-images
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Create .env file
        run: |
          cat > .env << EOF
          IMAGE_TAG=${{ github.sha }}
          POSTGRES_PASSWORD=${{ secrets.POSTGRES_PASSWORD }}
          REDIS_PASSWORD=${{ secrets.REDIS_PASSWORD }}
          EOF

      - name: Start services
        run: |
          docker-compose -f docker-compose.test.yml up -d

      - name: Wait for services
        run: |
          for service in user account trade ai scraper; do
            timeout 120 bash -c "until curl -f http://localhost:808${i}/actuator/health; do sleep 5; done"
            ((i++))
          done

      - name: Run integration tests
        run: |
          ./gradlew integrationTest

      - name: Cleanup
        if: always()
        run: |
          docker-compose -f docker-compose.test.yml down -v

  # 6단계: 스테이징 배포
  deploy-staging:
    needs: [security-scan, integration-test]
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.lk-trade.com
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to staging
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/lk-trade
            export IMAGE_TAG=${{ github.sha }}
            docker-compose pull
            docker-compose up -d
            docker-compose ps

      - name: Run smoke tests
        run: |
          sleep 30
          curl -f https://staging.lk-trade.com/api/user/actuator/health

  # 7단계: 프로덕션 배포
  deploy-production:
    needs: [security-scan, integration-test]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://lk-trade.com
    steps:
      - uses: actions/checkout@v4

      - name: Create deployment
        uses: chrnorm/deployment-action@v2
        id: deployment
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          environment: production

      - name: Deploy to production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/lk-trade
            export IMAGE_TAG=${{ github.sha }}

            # 블루-그린 배포
            docker-compose -f docker-compose.blue.yml pull
            docker-compose -f docker-compose.blue.yml up -d

            # 헬스체크
            sleep 60
            for port in 8081 8082 8083 8084 8085; do
              curl -f http://localhost:$port/actuator/health || exit 1
            done

            # 트래픽 전환
            docker exec nginx nginx -s reload

            # 이전 버전 종료
            docker-compose -f docker-compose.green.yml down

      - name: Update deployment status (success)
        if: success()
        uses: chrnorm/deployment-status@v2
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          deployment-id: ${{ steps.deployment.outputs.deployment_id }}
          state: success

      - name: Update deployment status (failure)
        if: failure()
        uses: chrnorm/deployment-status@v2
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          deployment-id: ${{ steps.deployment.outputs.deployment_id }}
          state: failure
```

### Makefile로 로컬 워크플로우 자동화

```makefile
# Makefile

.PHONY: help build test docker-build docker-push deploy-staging deploy-prod

# 기본 변수
MODULES := user account trade ai scraper
REGISTRY := ghcr.io/yourusername/lk-trade
VERSION := $(shell git rev-parse --short HEAD)

help:
	@echo "LK-Trade 빌드 자동화"
	@echo ""
	@echo "사용 가능한 명령어:"
	@echo "  make build            - 모든 모듈 빌드"
	@echo "  make test             - 모든 테스트 실행"
	@echo "  make docker-build     - Docker 이미지 빌드"
	@echo "  make docker-push      - Docker 이미지 푸시"
	@echo "  make deploy-staging   - 스테이징 배포"
	@echo "  make deploy-prod      - 프로덕션 배포"

# Gradle 빌드
build:
	@echo "📦 Building all modules..."
	./gradlew clean build

# 테스트 실행
test:
	@echo "🧪 Running tests..."
	./gradlew test integrationTest

# Docker 이미지 빌드
docker-build:
	@echo "🐳 Building Docker images..."
	@for module in $(MODULES); do \
		echo "Building $$module-service..."; \
		docker build -t $(REGISTRY)/$$module-service:$(VERSION) ./modules/$$module; \
		docker tag $(REGISTRY)/$$module-service:$(VERSION) $(REGISTRY)/$$module-service:latest; \
	done

# Docker 이미지 푸시
docker-push:
	@echo "📤 Pushing Docker images..."
	@for module in $(MODULES); do \
		echo "Pushing $$module-service..."; \
		docker push $(REGISTRY)/$$module-service:$(VERSION); \
		docker push $(REGISTRY)/$$module-service:latest; \
	done

# 로컬 개발 환경 시작
dev-up:
	@echo "🚀 Starting development environment..."
	docker-compose -f docker-compose.dev.yml up -d

# 로컬 개발 환경 중지
dev-down:
	@echo "🛑 Stopping development environment..."
	docker-compose -f docker-compose.dev.yml down -v

# 스테이징 배포
deploy-staging:
	@echo "🚀 Deploying to staging..."
	ssh staging "cd /opt/lk-trade && \
		export IMAGE_TAG=$(VERSION) && \
		docker-compose pull && \
		docker-compose up -d"

# 프로덕션 배포
deploy-prod:
	@echo "🚀 Deploying to production..."
	@read -p "Are you sure you want to deploy to production? [y/N] " confirm; \
	if [ "$$confirm" = "y" ]; then \
		ssh production "cd /opt/lk-trade && \
			export IMAGE_TAG=$(VERSION) && \
			docker-compose -f docker-compose.blue.yml pull && \
			docker-compose -f docker-compose.blue.yml up -d && \
			sleep 60 && \
			docker exec nginx nginx -s reload && \
			docker-compose -f docker-compose.green.yml down"; \
	fi

# 로그 확인
logs:
	docker-compose logs -f

# 클린업
clean:
	@echo "🧹 Cleaning up..."
	./gradlew clean
	docker system prune -f
```

---

## 트러블슈팅

### 일반적인 문제들

#### 1. **Docker 빌드 시 캐시 문제**

**증상**:
```
=> ERROR [stage-1 3/4] COPY --from=builder /app/build/libs/*.jar app.jar
------
 > [stage-1 3/4] COPY --from=builder /app/build/libs/*.jar app.jar:
------
failed to compute cache key: "/app/build/libs/*.jar" not found
```

**해결**:
```bash
# 캐시 없이 빌드
docker build --no-cache -t myapp:latest .

# BuildKit 캐시 초기화
docker builder prune -af
```

#### 2. **GitHub Actions에서 권한 오류**

**증상**:
```
Error: denied: permission_denied: write_package
```

**해결**:
```yaml
# 워크플로우에 권한 추가
jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      security-events: write
```

#### 3. **Docker Compose 버전 불일치**

**증상**:
```
ERROR: Version in "./docker-compose.yml" is unsupported
```

**해결**:
```yaml
# docker-compose.yml 버전 명시 제거 (최신 방식)
# version: '3.8'  # 이 줄 제거

services:
  myapp:
    image: myapp:latest
    # ...
```

#### 4. **멀티 플랫폼 빌드 실패**

**증상**:
```
ERROR: Multi-platform build is not supported with the docker driver
```

**해결**:
```yaml
# Buildx 설정 추가
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3
  with:
    driver-opts: network=host

# QEMU 설정 (ARM 빌드)
- name: Set up QEMU
  uses: docker/setup-qemu-action@v3
```

#### 5. **Gradle 캐시 문제**

**증상**:
```
Gradle build 가 매우 느림
```

**해결**:
```yaml
- name: Setup Gradle
  uses: gradle/gradle-build-action@v2
  with:
    cache-read-only: false

# 또는 수동 캐시 설정
- name: Cache Gradle packages
  uses: actions/cache@v3
  with:
    path: |
      ~/.gradle/caches
      ~/.gradle/wrapper
    key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
    restore-keys: |
      ${{ runner.os }}-gradle-
```

### 디버깅 팁

#### GitHub Actions 디버깅

```yaml
# 디버그 모드 활성화
- name: Debug information
  run: |
    echo "Event name: ${{ github.event_name }}"
    echo "Ref: ${{ github.ref }}"
    echo "SHA: ${{ github.sha }}"
    echo "Actor: ${{ github.actor }}"
    env

# SSH로 러너 접속
- name: Setup tmate session
  if: failure()
  uses: mxschmitt/action-tmate@v3
  timeout-minutes: 15
```

#### GitLab CI 디버깅

```yaml
# 디버그 모드로 작업 실행
debug-job:
  stage: test
  script:
    - set -x  # 명령어 출력
    - env | sort  # 환경 변수 확인
    - pwd
    - ls -la
  variables:
    CI_DEBUG_TRACE: "true"
```

### 성능 최적화 체크리스트

- [ ] Docker 레이어 캐싱 활성화
- [ ] BuildKit 사용 (GitHub Actions: `docker/build-push-action@v5`)
- [ ] 멀티 스테이지 빌드 적용
- [ ] 의존성만 먼저 복사 후 빌드 (Gradle/Maven)
- [ ] GitHub Actions 캐시 활용 (`actions/cache@v3`)
- [ ] 병렬 빌드 활성화 (matrix 전략)
- [ ] 불필요한 파일 `.dockerignore`에 추가
- [ ] 이미지 레지스트리 캐시 활용
- [ ] 변경된 모듈만 빌드 (path filter)
- [ ] 테스트 결과 캐싱

### 보안 체크리스트

- [ ] 시크릿은 GitHub Secrets / GitLab Variables 사용
- [ ] 이미지 취약점 스캔 (Trivy, Snyk)
- [ ] Dockerfile 린팅 (Hadolint)
- [ ] 비루트 사용자로 실행
- [ ] 시크릿 파일 스캔 (TruffleHog)
- [ ] SBOM 생성 및 보관
- [ ] 이미지 서명 (Cosign)
- [ ] 최소 권한 원칙 적용
- [ ] 네트워크 정책 설정
- [ ] 정기적인 의존성 업데이트

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: GitHub Actions 권한 오류로 배포 실패

**상황**: 첫 CI/CD 파이프라인을 구축했는데 Docker 이미지 푸시 단계에서 실패

```yaml
# ❌ 주니어 개발자가 작성한 워크플로우
name: Build and Push

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t ghcr.io/mycompany/myapp:latest .

      - name: Push to GHCR
        run: docker push ghcr.io/mycompany/myapp:latest
```

**에러 메시지**:
```
Error: denied: permission_denied: write_package
```

**문제점**:
- 문제 1: GHCR 로그인을 하지 않음
- 문제 2: 워크플로우에 패키지 쓰기 권한이 없음
- 문제 3: GITHUB_TOKEN을 사용하지 않음
- 왜 이 문제가 발생하는가: GitHub Container Registry는 인증이 필요하고, 기본적으로 패키지 쓰기 권한이 부여되지 않음

**해결책**:
```yaml
# ✅ 올바른 코드
name: Build and Push

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    # 1. 권한 추가
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      # 2. GHCR 로그인
      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      # 3. 이미지 빌드 및 푸시
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
```

**배운 점**:
- 💡 팁 1: GitHub Container Registry는 반드시 로그인 필요
- 💡 팁 2: `permissions` 섹션에서 `packages: write` 권한 부여 필수
- 💡 팁 3: `GITHUB_TOKEN`은 자동으로 제공되는 시크릿
- 💡 팁 4: `docker/login-action`과 `docker/build-push-action` 사용 권장

---

### 시나리오 2: 캐시 미사용으로 빌드 시간이 너무 오래 걸림

**상황**: 매번 빌드할 때마다 15분씩 소요되어 팀원들이 불편함을 호소

```yaml
# ❌ 캐시를 사용하지 않는 느린 빌드
- name: Build Docker image
  run: |
    docker build -t myapp:latest .

# Gradle 빌드도 매번 의존성 다운로드
- name: Build with Gradle
  run: ./gradlew build
```

**문제점**:
- 문제 1: Docker 레이어 캐시를 사용하지 않음
- 문제 2: Gradle 의존성을 매번 다운로드
- 문제 3: BuildKit 캐시 미사용
- 영향: 빌드 시간 15분 → 팀 생산성 저하

**해결책**:
```yaml
# ✅ 캐시를 사용하는 빠른 빌드
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # 1. Gradle 캐시 설정
      - name: Set up JDK with Gradle cache
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: 'gradle'  # ✅ Gradle 캐시 자동 활성화

      # 2. Docker Buildx 설정 (캐시 지원)
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      # 3. BuildKit 캐시를 사용한 빌드
      - name: Build and push with cache
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: myapp:latest
          # ✅ GitHub Actions 캐시 사용
          cache-from: type=gha
          cache-to: type=gha,mode=max

      # 4. Gradle 빌드 (캐시 활용)
      - name: Build with Gradle
        run: ./gradlew build
        # 이미 setup-java에서 캐시 설정했으므로 자동으로 빠름
```

**성능 개선**:
| 항목 | Before | After | 개선 |
|------|--------|-------|------|
| 첫 빌드 | 15분 | 15분 | - |
| 이후 빌드 | 15분 | 2분 | **87%↓** |
| 의존성 다운로드 | 매번 5분 | 캐시 사용 | **5분 절약** |

**배운 점**:
- 💡 팁 1: `cache: 'gradle'` 옵션으로 Gradle 캐시 자동 활성화
- 💡 팁 2: BuildKit 캐시는 `type=gha`로 GitHub Actions 캐시 활용
- 💡 팁 3: `mode=max`로 최대한 많은 레이어 캐싱
- 💡 팁 4: 첫 빌드는 느리지만 이후 빌드는 극적으로 빨라짐

---

### 시나리오 3: 테스트 실패 시 파이프라인이 계속 진행됨

**상황**: 테스트가 실패했는데도 배포가 진행되어 프로덕션에 버그 배포

```yaml
# ❌ 테스트 실패를 무시하는 위험한 파이프라인
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Run tests
        run: ./gradlew test
        continue-on-error: true  # ❌ 위험!

  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: ./deploy.sh
```

**문제점**:
- 문제 1: `continue-on-error: true`로 테스트 실패를 무시
- 문제 2: `test` 작업과 `deploy` 작업 간 의존성 없음
- 문제 3: 테스트 실패해도 배포 진행
- 결과: 프로덕션에 버그 배포 → 고객 불만 → 긴급 롤백

**해결책**:
```yaml
# ✅ 테스트 실패 시 배포를 중단하는 안전한 파이프라인
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'

      # 1. 테스트 실행 (실패 시 자동 중단)
      - name: Run unit tests
        run: ./gradlew test
        # continue-on-error 제거 ✅

      # 2. 테스트 결과 리포트 (실패해도 업로드)
      - name: Upload test results
        if: always()  # 성공/실패 관계없이 리포트 업로드
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: build/test-results/

  # 3. 배포는 테스트 성공 후에만 실행
  deploy:
    needs: test  # ✅ test 작업이 성공해야만 실행
    if: success()  # ✅ 명시적으로 성공 조건 추가
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: ./deploy.sh

      # 4. 배포 실패 시 알림
      - name: Notify on failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "🚨 Production deployment failed!"
            }
```

**추가: 게이트 방식으로 승인 필요**
```yaml
# ✅ 프로덕션 배포는 수동 승인 필요
deploy-production:
  needs: [test, build]
  environment:
    name: production
    url: https://myapp.com
  runs-on: ubuntu-latest
  steps:
    - name: Deploy to production
      run: ./deploy.sh
```

**배운 점**:
- 💡 팁 1: `needs`로 작업 간 의존성 명시
- 💡 팁 2: `continue-on-error`는 매우 신중하게 사용
- 💡 팁 3: `if: always()`로 실패해도 리포트 업로드
- 💡 팁 4: 프로덕션 배포는 `environment`로 승인 프로세스 추가

---

### 시나리오 4: 멀티 모듈 프로젝트에서 불필요한 빌드 실행

**상황**: user 모듈만 수정했는데 모든 모듈(user, account, trade, ai, scraper)을 빌드하여 시간 낭비

```yaml
# ❌ 항상 모든 모듈을 빌드하는 비효율적인 파이프라인
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        module: [user, account, trade, ai, scraper]
    steps:
      - name: Build ${{ matrix.module }}
        run: ./gradlew :modules:${{ matrix.module }}:build
```

**문제점**:
- 문제 1: 코드 변경이 없는 모듈도 빌드
- 문제 2: 빌드 시간 5개 모듈 × 3분 = 15분
- 문제 3: GitHub Actions 실행 시간 낭비 (월 2,000분 무료 제한)

**해결책**:
```yaml
# ✅ 변경된 모듈만 빌드하는 효율적인 파이프라인
jobs:
  # 1단계: 어떤 모듈이 변경되었는지 감지
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      user: ${{ steps.filter.outputs.user }}
      account: ${{ steps.filter.outputs.account }}
      trade: ${{ steps.filter.outputs.trade }}
      ai: ${{ steps.filter.outputs.ai }}
      scraper: ${{ steps.filter.outputs.scraper }}
    steps:
      - uses: actions/checkout@v4

      # ✅ 변경된 파일 감지
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            user:
              - 'modules/user/**'
            account:
              - 'modules/account/**'
            trade:
              - 'modules/trade/**'
            ai:
              - 'modules/ai/**'
            scraper:
              - 'modules/scraper/**'

  # 2단계: user 모듈이 변경된 경우에만 빌드
  build-user:
    needs: detect-changes
    if: needs.detect-changes.outputs.user == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build user module
        run: ./gradlew :modules:user:build

  # 3단계: account 모듈이 변경된 경우에만 빌드
  build-account:
    needs: detect-changes
    if: needs.detect-changes.outputs.account == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build account module
        run: ./gradlew :modules:account:build

  # 나머지 모듈도 동일...
```

**성능 개선**:
| 시나리오 | Before | After | 절약 |
|---------|--------|-------|------|
| 1개 모듈 수정 | 15분 (5개 빌드) | 3분 (1개만) | **80%↓** |
| 2개 모듈 수정 | 15분 (5개 빌드) | 6분 (2개만) | **60%↓** |
| 공통 코드 수정 | 15분 (5개 빌드) | 15분 (5개 빌드) | - |

**배운 점**:
- 💡 팁 1: `dorny/paths-filter` 액션으로 변경 감지
- 💡 팁 2: `needs`와 `if`를 조합해 조건부 실행
- 💡 팁 3: GitHub Actions 무료 시간 절약
- 💡 팁 4: 빌드 시간 단축으로 피드백 속도 향상

---

## ❓ FAQ

<details>
<summary><strong>Q1: GitHub Actions와 GitLab CI 중 어떤 것을 선택해야 하나요?</strong></summary>

**A**: 사용 중인 Git 플랫폼과 팀 상황에 따라 다릅니다.

**상세 설명**:
- GitHub를 사용 중이라면: GitHub Actions 권장
- GitLab을 사용 중이라면: GitLab CI 권장
- 둘 다 사용 가능하다면: 아래 비교표 참고

**비교표**:
| 기준 | GitHub Actions | GitLab CI |
|------|---------------|-----------|
| **무료 제공** | 퍼블릭 무제한<br>프라이빗 2,000분/월 | 퍼블릭/프라이빗 400분/월 |
| **설정 파일** | `.github/workflows/` | `.gitlab-ci.yml` (루트) |
| **러너** | GitHub 호스팅 | GitLab 호스팅 또는 Self-hosted |
| **마켓플레이스** | 풍부한 액션 생태계 | 상대적으로 적음 |
| **학습 곡선** | YAML 구조 간단 | 상대적으로 복잡 |
| **통합** | GitHub 네이티브 | GitLab 네이티브 |

**실무 팁**:
💡 대부분의 경우 사용 중인 플랫폼의 네이티브 CI/CD 도구를 선택하는 것이 가장 효율적입니다.

</details>

<details>
<summary><strong>Q2: CI/CD 파이프라인이 실패하면 어떻게 디버깅하나요?</strong></summary>

**A**: 단계별로 로그를 확인하고 로컬에서 재현해봅니다.

**상세 설명**:
1. **로그 확인**: GitHub Actions의 경우 각 step의 로그를 펼쳐서 확인
2. **로컬 재현**: 동일한 명령어를 로컬에서 실행
3. **환경 변수 확인**: 시크릿이나 환경 변수가 올바른지 확인
4. **의존성 문제**: 버전 충돌이나 누락된 의존성 체크

**예시 디버깅 스크립트**:
```yaml
# 디버그 정보 출력
- name: Debug information
  run: |
    echo "Event: ${{ github.event_name }}"
    echo "Ref: ${{ github.ref }}"
    echo "SHA: ${{ github.sha }}"
    env | sort
    docker version
    docker info
```

**고급 디버깅**:
```yaml
# SSH로 러너에 접속 (실패 시)
- name: Setup tmate session
  if: failure()
  uses: mxschmitt/action-tmate@v3
  timeout-minutes: 15
```

**실무 팁**:
💡 실패한 step 바로 위의 step부터 확인하면 원인을 빠르게 찾을 수 있습니다.

</details>

<details>
<summary><strong>Q3: Docker 이미지 빌드 시간이 너무 오래 걸리는데 어떻게 최적화하나요?</strong></summary>

**A**: BuildKit 캐시, 멀티 스테이지 빌드, 레이어 최적화를 활용합니다.

**상세 설명**:
- **캐시 활용**: GitHub Actions 캐시 (`type=gha`) 사용
- **멀티 스테이지**: 빌드용/런타임용 이미지 분리
- **레이어 최적화**: 자주 변경되지 않는 것부터 먼저 COPY

**최적화 예시**:
```dockerfile
# ❌ 비효율적 (매번 의존성 다운로드)
FROM gradle:8.5-jdk21
WORKDIR /app
COPY . .
RUN gradle build

# ✅ 효율적 (의존성만 먼저 캐싱)
FROM gradle:8.5-jdk21 AS builder
WORKDIR /app

# 1단계: 의존성만 먼저 다운로드 (캐싱)
COPY build.gradle.kts settings.gradle.kts ./
COPY gradle ./gradle
RUN gradle dependencies --no-daemon

# 2단계: 소스 코드 복사 및 빌드
COPY src ./src
RUN gradle build -x test --no-daemon

# 3단계: 런타임 이미지 (크기 50% 감소)
FROM eclipse-temurin:21-jre-alpine
COPY --from=builder /app/build/libs/*.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

**성과**:
| 항목 | Before | After | 개선 |
|------|--------|-------|------|
| 첫 빌드 | 10분 | 10분 | - |
| 캐시 히트 시 | 10분 | 1분 | **90%↓** |
| 이미지 크기 | 800MB | 250MB | **69%↓** |

**실무 팁**:
💡 의존성과 소스 코드를 분리하여 COPY하면 캐시 효율이 극대화됩니다.

</details>

<details>
<summary><strong>Q4: 프로덕션 배포를 완전 자동화해도 안전한가요?</strong></summary>

**A**: 자동 테스트와 승인 프로세스를 결합하면 안전합니다.

**상세 설명**:
- **완전 자동화 (CD)**: develop 브랜치 → 스테이징 자동 배포
- **수동 승인 (Continuous Delivery)**: main 브랜치 → 승인 후 프로덕션 배포

**안전한 프로덕션 배포 전략**:
```yaml
# ✅ 승인이 필요한 프로덕션 배포
deploy-production:
  needs: [test, security-scan]
  environment:
    name: production
    url: https://myapp.com
  runs-on: ubuntu-latest
  steps:
    - name: Deploy to production
      run: ./deploy.sh

    # 배포 후 스모크 테스트
    - name: Smoke test
      run: |
        sleep 30
        curl -f https://myapp.com/health || exit 1

    # 실패 시 자동 롤백
    - name: Rollback on failure
      if: failure()
      run: ./rollback.sh
```

**안전 장치**:
1. ✅ 자동 테스트 (단위/통합/E2E)
2. ✅ 보안 스캔 (Trivy, Snyk)
3. ✅ 수동 승인 (GitHub Environment)
4. ✅ 스모크 테스트
5. ✅ 자동 롤백
6. ✅ 모니터링 알림

**실무 팁**:
💡 Netflix, Amazon 등 대기업들도 완전 자동화 배포를 사용하지만, 충분한 테스트와 모니터링이 전제됩니다.

</details>

<details>
<summary><strong>Q5: 시크릿(비밀번호, API 키)은 어떻게 관리하나요?</strong></summary>

**A**: GitHub Secrets나 GitLab CI Variables를 사용하여 암호화된 상태로 저장합니다.

**상세 설명**:
- **절대 금지**: 코드에 직접 하드코딩
- **권장**: GitHub Secrets / GitLab Variables 사용
- **고급**: Vault, AWS Secrets Manager 통합

**GitHub Secrets 사용법**:
```yaml
# 1. GitHub 레포지토리 → Settings → Secrets → New secret
# 2. 워크플로우에서 사용
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  API_KEY: ${{ secrets.API_KEY }}

steps:
  - name: Deploy
    env:
      SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
    run: |
      curl -X POST $SLACK_WEBHOOK -d '{"text":"Deployed"}'
```

**GitLab CI Variables**:
```yaml
# GitLab 프로젝트 → Settings → CI/CD → Variables
deploy:
  script:
    - echo "Deploying with secret: $DATABASE_URL"
  variables:
    DATABASE_URL: $DATABASE_URL  # GitLab Variables에서 자동 주입
```

**보안 체크리스트**:
- [ ] `.env` 파일을 `.gitignore`에 추가
- [ ] 시크릿은 GitHub/GitLab Secrets에만 저장
- [ ] 로그에 시크릿이 출력되지 않도록 주의
- [ ] 시크릿 로테이션 (주기적 변경)

**실무 팁**:
💡 실수로 시크릿을 커밋했다면 즉시 해당 시크릿을 폐기하고 새로 발급받아야 합니다.

</details>

<details>
<summary><strong>Q6: 멀티 플랫폼 (amd64, arm64) Docker 이미지를 어떻게 빌드하나요?</strong></summary>

**A**: Docker Buildx와 QEMU를 사용하여 동시 빌드합니다.

**상세 설명**:
- **amd64**: 일반적인 서버, 데스크톱 (Intel, AMD)
- **arm64**: Apple Silicon (M1/M2), AWS Graviton, Raspberry Pi

**멀티 플랫폼 빌드 예시**:
```yaml
- name: Set up QEMU
  uses: docker/setup-qemu-action@v3

- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build multi-platform image
  uses: docker/build-push-action@v5
  with:
    context: .
    platforms: linux/amd64,linux/arm64,linux/arm/v7
    push: true
    tags: |
      myapp:latest
      myapp:${{ github.sha }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**주의사항**:
- ⚠️ 멀티 플랫폼 빌드는 시간이 2-3배 더 걸림
- ⚠️ 모든 의존성이 다중 플랫폼을 지원하는지 확인 필요

**실무 팁**:
💡 AWS Graviton (ARM)을 사용하면 비용이 20% 저렴하므로 멀티 플랫폼 빌드 권장!

</details>

<details>
<summary><strong>Q7: CI/CD 비용을 절감하려면 어떻게 해야 하나요?</strong></summary>

**A**: 캐싱, Self-hosted 러너, 변경 감지를 활용합니다.

**상세 설명**:
- **GitHub Actions**: 퍼블릭 무제한, 프라이빗 2,000분/월 무료
- **초과 시 비용**: $0.008/분 (Linux)
- **절감 전략**: 캐싱, Self-hosted 러너, 불필요한 빌드 스킵

**비용 절감 전략**:

1. **캐싱 활용** (빌드 시간 80% 감소)
```yaml
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

2. **변경된 파일만 빌드**
```yaml
- uses: dorny/paths-filter@v3
  id: changes
  with:
    filters: |
      backend:
        - 'backend/**'
      frontend:
        - 'frontend/**'

- name: Build backend
  if: steps.changes.outputs.backend == 'true'
  run: ./gradlew build
```

3. **Self-hosted 러너 사용** (비용 제로)
```yaml
runs-on: self-hosted  # 자체 서버에서 실행
```

4. **불필요한 트리거 제거**
```yaml
on:
  push:
    branches: [ main, develop ]
    paths-ignore:
      - 'docs/**'  # 문서 변경은 빌드 스킵
      - '**.md'
```

**비용 비교**:
| 전략 | 월 사용 시간 | 비용 (프라이빗) |
|------|--------------|----------------|
| 최적화 전 | 10,000분 | $64/월 |
| 캐싱 적용 | 2,000분 | $0 (무료) |
| Self-hosted | 무제한 | $0 (서버 비용만) |

**실무 팁**:
💡 Self-hosted 러너는 보안에 주의! 퍼블릭 레포지토리에서는 사용 금지.

</details>

<details>
<summary><strong>Q8: 배포 실패 시 자동으로 롤백하는 방법은?</strong></summary>

**A**: 헬스체크 실패 감지 후 이전 버전으로 자동 복구합니다.

**자동 롤백 구현**:
```yaml
deploy-production:
  runs-on: ubuntu-latest
  steps:
    # 1. 현재 버전 백업
    - name: Backup current version
      run: |
        kubectl get deployment myapp -o yaml > backup.yaml

    # 2. 새 버전 배포
    - name: Deploy new version
      run: |
        kubectl set image deployment/myapp myapp=myapp:${{ github.sha }}
        kubectl rollout status deployment/myapp --timeout=5m

    # 3. 헬스체크
    - name: Health check
      id: health
      run: |
        sleep 30
        for i in {1..5}; do
          if curl -f https://myapp.com/health; then
            echo "Health check passed"
            exit 0
          fi
          sleep 10
        done
        echo "Health check failed"
        exit 1

    # 4. 실패 시 자동 롤백
    - name: Rollback on failure
      if: failure()
      run: |
        echo "🚨 Deployment failed, rolling back..."
        kubectl rollout undo deployment/myapp
        kubectl rollout status deployment/myapp --timeout=5m

    # 5. Slack 알림
    - name: Notify team
      if: failure()
      uses: slackapi/slack-github-action@v1
      with:
        webhook-url: ${{ secrets.SLACK_WEBHOOK }}
        payload: |
          {
            "text": "🚨 Deployment failed and rolled back automatically!",
            "blocks": [
              {
                "type": "section",
                "text": {
                  "type": "mrkdwn",
                  "text": "*Deployment Failed*\n• Commit: ${{ github.sha }}\n• Author: ${{ github.actor }}\n• Action: Automatic rollback completed"
                }
              }
            ]
          }
```

**실무 팁**:
💡 Kubernetes의 경우 `kubectl rollout undo`, Docker Swarm의 경우 `docker service rollback`를 사용합니다.

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. CI/CD가 무엇이고 왜 필요한가요?</strong></summary>

**모범 답안 포인트**
- CI (Continuous Integration): 코드 통합을 자동화하여 충돌을 빠르게 발견
- CD (Continuous Delivery/Deployment): 배포 프로세스를 자동화하여 안전하고 빠른 릴리스
- 필요성: 수동 배포의 오류 감소, 배포 빈도 증가, 빠른 피드백

**예시 답변**
> "CI/CD는 Continuous Integration과 Continuous Delivery/Deployment의 약자입니다. CI는 개발자들이 작성한 코드를 자동으로 통합하고 테스트하는 과정이고, CD는 이를 프로덕션 환경에 자동으로 배포하는 과정입니다. 수동 배포는 사람의 실수로 오류가 발생할 수 있고 시간이 오래 걸리지만, CI/CD를 사용하면 자동화된 테스트를 통해 버그를 빠르게 발견하고, 하루에도 여러 번 안전하게 배포할 수 있습니다."

**꼬리 질문**
- Q: Continuous Delivery와 Continuous Deployment의 차이는?
- A: Delivery는 수동 승인 후 배포, Deployment는 완전 자동 배포입니다.

**실무 연관**
- 실제로 Netflix는 하루 수백 번 배포하며, CI/CD 없이는 불가능합니다.

</details>

<details>
<summary><strong>2. GitHub Actions의 기본 구조를 설명해주세요.</strong></summary>

**모범 답안 포인트**
- Workflow: `.github/workflows/` 디렉토리의 YAML 파일
- Job: 독립적으로 실행되는 작업 단위
- Step: Job 내부의 개별 명령어나 액션
- Event: 워크플로우를 트리거하는 이벤트 (push, pull_request 등)

**예시 답변**
> "GitHub Actions는 `.github/workflows/` 디렉토리에 YAML 파일로 정의합니다. 기본 구조는 크게 세 가지로 나뉩니다. 첫째, `on` 섹션에서 어떤 이벤트에 실행할지 정의하고 (예: push, pull_request), 둘째, `jobs` 섹션에서 실행할 작업들을 정의하며, 셋째, 각 job 안에 `steps`로 구체적인 명령어를 작성합니다. 예를 들어, 코드 체크아웃, 빌드, 테스트, 배포 등을 순서대로 실행할 수 있습니다."

**꼬리 질문**
- Q: Job들을 병렬로 실행할 수 있나요?
- A: 네, 기본적으로 병렬 실행되며 `needs` 키워드로 순서를 지정할 수 있습니다.

**실무 연관**
- 멀티 모듈 프로젝트에서 각 모듈을 병렬로 빌드하여 시간을 단축합니다.

</details>

<details>
<summary><strong>3. Docker 이미지 빌드를 최적화하는 방법은?</strong></summary>

**모범 답안 포인트**
- 멀티 스테이지 빌드: 빌드용과 런타임용 이미지 분리
- 레이어 캐싱: 자주 변경되지 않는 것부터 먼저 COPY
- .dockerignore: 불필요한 파일 제외
- BuildKit 캐시: GitHub Actions 캐시 활용

**예시 답변**
> "Docker 이미지 빌드 최적화는 여러 방법이 있습니다. 첫째, 멀티 스테이지 빌드로 빌드 도구는 최종 이미지에서 제외하여 크기를 줄입니다. 둘째, Dockerfile에서 자주 변경되지 않는 의존성을 먼저 COPY하여 레이어 캐싱을 활용합니다. 셋째, .dockerignore 파일로 node_modules, .git 등 불필요한 파일을 제외합니다. 마지막으로 GitHub Actions에서 BuildKit 캐시를 사용하면 이전 빌드의 레이어를 재사용하여 빌드 시간을 크게 단축할 수 있습니다."

**꼬리 질문**
- Q: 레이어 캐싱이 무효화되는 경우는?
- A: Dockerfile의 특정 라인이 변경되면 그 이후의 모든 레이어가 재빌드됩니다.

**실무 연관**
- 프로덕션 환경에서 빌드 시간이 10분에서 1분으로 단축된 경험이 있습니다.

</details>

<details>
<summary><strong>4. GitHub Actions에서 시크릿은 어떻게 관리하나요?</strong></summary>

**모범 답안 포인트**
- GitHub Secrets: 레포지토리 Settings에서 암호화 저장
- 환경 변수로 접근: `${{ secrets.SECRET_NAME }}`
- 로그에 자동 마스킹: 시크릿 값은 로그에 `***`로 표시
- 절대 코드에 하드코딩 금지

**예시 답변**
> "GitHub Actions에서 시크릿은 레포지토리의 Settings → Secrets 메뉴에서 관리합니다. 여기에 등록된 시크릿은 암호화되어 저장되며, 워크플로우에서 `${{ secrets.DB_PASSWORD }}` 형식으로 사용할 수 있습니다. 중요한 점은 시크릿 값이 로그에 출력되지 않도록 GitHub이 자동으로 마스킹 처리한다는 것입니다. 절대로 코드에 직접 비밀번호나 API 키를 하드코딩해서는 안 되며, 모두 Secrets로 관리해야 합니다."

**꼬리 질문**
- Q: Organization 레벨에서도 시크릿을 관리할 수 있나요?
- A: 네, Organization Secrets로 여러 레포지토리에서 공유할 수 있습니다.

**실무 연관**
- AWS Access Key, 데이터베이스 비밀번호 등 모든 민감한 정보는 Secrets로 관리합니다.

</details>

<details>
<summary><strong>5. CI/CD에서 테스트 단계가 실패하면 어떻게 되나요?</strong></summary>

**모범 답안 포인트**
- 파이프라인 중단: 기본적으로 다음 단계 실행 안 됨
- 배포 방지: 테스트 실패 시 프로덕션 배포 차단
- 빠른 피드백: 개발자에게 즉시 알림
- 테스트 리포트: 실패 원인 분석 가능

**예시 답변**
> "CI/CD에서 테스트 단계가 실패하면 기본적으로 파이프라인이 중단되어 다음 단계(빌드, 배포)가 실행되지 않습니다. 이는 버그가 있는 코드가 프로덕션 환경에 배포되는 것을 방지하는 안전장치입니다. GitHub Actions에서는 빨간색으로 실패를 표시하고, 설정에 따라 Slack이나 이메일로 개발자에게 알림을 보냅니다. 테스트 리포트를 통해 어떤 테스트가 왜 실패했는지 확인할 수 있어 빠르게 수정할 수 있습니다."

**꼬리 질문**
- Q: 테스트가 실패해도 계속 진행하고 싶다면?
- A: `continue-on-error: true`를 사용할 수 있지만 권장하지 않습니다.

**실무 연관**
- 실제로 금요일 저녁 배포 전에 테스트가 실패를 감지하여 대형 장애를 예방한 경험이 있습니다.

</details>

<details>
<summary><strong>6. Docker 이미지 보안 스캔은 왜 필요한가요?</strong></summary>

**모범 답안 포인트**
- 취약점 발견: 이미지에 포함된 라이브러리의 보안 취약점 탐지
- CVE 데이터베이스: 알려진 취약점 목록과 비교
- 배포 전 차단: 심각한 취약점이 있으면 배포 중단
- 도구: Trivy, Snyk, Clair 등

**예시 답변**
> "Docker 이미지 보안 스캔은 이미지에 포함된 패키지나 라이브러리에 알려진 보안 취약점이 있는지 확인하는 과정입니다. 예를 들어, Trivy 같은 도구를 사용하면 CVE 데이터베이스와 비교하여 취약점을 찾아냅니다. 만약 CRITICAL 등급의 취약점이 발견되면 CI/CD 파이프라인을 실패시켜 배포를 막을 수 있습니다. 이는 보안 사고를 사전에 예방하는 중요한 단계입니다."

**꼬리 질문**
- Q: 모든 취약점을 다 막아야 하나요?
- A: CRITICAL, HIGH 등급은 필수로 수정하고, MEDIUM 이하는 우선순위에 따라 처리합니다.

**실무 연관**
- 실제로 Log4j 취약점(Log4Shell) 같은 경우 자동 스캔으로 빠르게 발견하고 패치할 수 있었습니다.

</details>

<details>
<summary><strong>7. GitLab CI와 GitHub Actions의 주요 차이점은?</strong></summary>

**모범 답안 포인트**
- 설정 파일: GitLab은 `.gitlab-ci.yml` (루트), GitHub은 `.github/workflows/`
- 러너: GitLab은 공유 러너 또는 Self-hosted, GitHub도 동일
- 구문: GitLab은 stages/jobs, GitHub은 jobs/steps
- 통합: 각자의 플랫폼과 긴밀히 통합

**예시 답변**
> "GitLab CI와 GitHub Actions의 가장 큰 차이는 설정 파일 위치와 구문입니다. GitLab은 프로젝트 루트에 `.gitlab-ci.yml` 하나로 관리하고, `stages`로 단계를 정의합니다. GitHub Actions는 `.github/workflows/` 디렉토리에 여러 워크플로우를 분리해서 관리할 수 있고, `on` 섹션으로 트리거를 정의합니다. 기능적으로는 비슷하지만, GitHub Actions는 마켓플레이스의 풍부한 액션을 활용할 수 있고, GitLab CI는 Auto DevOps 같은 자동화 기능이 강력합니다."

**꼬리 질문**
- Q: 둘 중 어느 것이 더 좋나요?
- A: 사용 중인 Git 플랫폼의 네이티브 도구를 사용하는 것이 가장 효율적입니다.

**실무 연관**
- 회사에서 GitLab을 사용한다면 GitLab CI를, GitHub를 사용한다면 GitHub Actions를 사용하는 것이 일반적입니다.

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. 멀티 모듈 프로젝트에서 변경된 모듈만 빌드하는 전략을 설명하세요.</strong></summary>

**모범 답안 포인트**
- 변경 감지: `dorny/paths-filter` 액션 사용
- 조건부 실행: `needs`와 `if`로 의존성 제어
- 병렬 빌드: 독립적인 모듈은 동시 빌드
- 비용 절감: GitHub Actions 무료 시간 절약

**예시 답변**
> "멀티 모듈 프로젝트에서는 변경된 모듈만 빌드하여 시간과 비용을 절약할 수 있습니다. 먼저 `dorny/paths-filter` 액션으로 어떤 모듈의 파일이 변경되었는지 감지합니다. 예를 들어, `modules/user/**` 경로에 변경이 있으면 user 모듈만 빌드하도록 합니다. 각 모듈 빌드 작업은 `needs: detect-changes`로 의존성을 설정하고, `if: needs.detect-changes.outputs.user == 'true'` 조건으로 해당 모듈이 변경된 경우에만 실행합니다. 변경되지 않은 모듈은 이전 빌드 결과를 재사용하므로 전체 빌드 시간을 크게 단축할 수 있습니다."

**실무 예시**
```yaml
detect-changes:
  outputs:
    user: ${{ steps.filter.outputs.user }}
    account: ${{ steps.filter.outputs.account }}
  steps:
    - uses: dorny/paths-filter@v3
      id: filter
      with:
        filters: |
          user:
            - 'modules/user/**'
          account:
            - 'modules/account/**'

build-user:
  needs: detect-changes
  if: needs.detect-changes.outputs.user == 'true'
  steps:
    - run: ./gradlew :modules:user:build
```

**꼬리 질문**
- Q: 공통 라이브러리가 변경되면 어떻게 하나요?
- A: 공통 라이브러리 경로를 모든 모듈 필터에 포함시켜 전체 빌드를 트리거합니다.

**실무 연관**
- 마이크로서비스 아키텍처에서 5개 서비스 중 1개만 변경되었을 때 빌드 시간을 80% 절감할 수 있습니다.

</details>

<details>
<summary><strong>2. 블루-그린 배포를 CI/CD 파이프라인에 어떻게 통합하나요?</strong></summary>

**모범 답안 포인트**
- 두 환경 준비: Blue (현재), Green (새 버전)
- 새 버전 배포: Green 환경에 배포 후 헬스체크
- 트래픽 전환: 로드 밸런서/Nginx 설정 변경
- 이전 버전 유지: 롤백 대비 Blue 환경 일정 기간 보존
- 자동 롤백: 헬스체크 실패 시 자동으로 Blue로 복구

**예시 답변**
> "블루-그린 배포는 두 개의 동일한 프로덕션 환경(Blue, Green)을 운영하여 무중단 배포를 구현하는 전략입니다. CI/CD 파이프라인에서는 다음과 같이 통합합니다. 첫째, Green 환경에 새 버전을 배포합니다. 둘째, 헬스체크와 스모크 테스트를 실행하여 정상 동작을 확인합니다. 셋째, Nginx나 로드 밸런서 설정을 변경하여 트래픽을 Blue에서 Green으로 전환합니다. 마지막으로 이전 Blue 환경은 일정 기간 유지하여 문제 발생 시 즉시 롤백할 수 있도록 합니다. 모든 과정이 자동화되어 사람의 개입 없이 안전하게 배포됩니다."

**실무 예시**
```bash
# 1. Green 환경 배포
docker-compose -f docker-compose.green.yml up -d

# 2. 헬스체크 (30초 대기)
sleep 30
curl -f http://localhost:8081/actuator/health

# 3. Nginx 트래픽 전환
docker exec nginx nginx -s reload

# 4. Blue 환경 종료
docker-compose -f docker-compose.blue.yml down

# 5. Green을 Blue로 변경 (다음 배포 대비)
mv docker-compose.green.yml docker-compose.blue.yml
```

**꼬리 질문**
- Q: 데이터베이스 스키마 변경이 있는 경우는 어떻게 하나요?
- A: 하위 호환성을 유지하는 방향으로 단계적 마이그레이션을 수행합니다.

**실무 연관**
- Netflix, Amazon 같은 대규모 서비스에서 블루-그린 배포를 통해 하루 수백 번 무중단 배포를 실행합니다.

</details>

<details>
<summary><strong>3. Docker 빌드 캐시를 효과적으로 활용하는 방법은?</strong></summary>

**모범 답안 포인트**
- BuildKit 활성화: `DOCKER_BUILDKIT=1` 또는 GitHub Actions의 `docker/build-push-action`
- 캐시 소스: `cache-from: type=gha`로 이전 빌드 캐시 재사용
- 캐시 저장: `cache-to: type=gha,mode=max`로 모든 레이어 캐싱
- Dockerfile 최적화: 자주 변경되지 않는 것부터 먼저 COPY
- 멀티 스테이지: 각 스테이지별로 캐싱

**예시 답변**
> "Docker 빌드 캐시를 효과적으로 활용하려면 여러 전략을 결합해야 합니다. 첫째, BuildKit를 활성화하여 고급 캐싱 기능을 사용합니다. GitHub Actions에서는 `docker/build-push-action@v5`를 사용하면 자동으로 활성화됩니다. 둘째, `cache-from: type=gha`로 이전 빌드의 캐시를 불러오고, `cache-to: type=gha,mode=max`로 현재 빌드의 모든 레이어를 캐시합니다. 셋째, Dockerfile에서 의존성 설치는 위쪽에, 소스 코드 복사는 아래쪽에 배치하여 소스 코드가 변경되어도 의존성 레이어는 캐시를 사용합니다. 넷째, 멀티 스테이지 빌드를 사용하면 각 스테이지별로 독립적으로 캐싱되어 더 효율적입니다."

**실무 예시**
```yaml
- name: Build with maximum cache
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: myapp:latest
    cache-from: |
      type=gha,scope=main
      type=registry,ref=myapp:buildcache
    cache-to: type=gha,mode=max,scope=main
    build-args: |
      BUILDKIT_INLINE_CACHE=1
```

**캐시 성능 비교**:
| 시나리오 | 캐시 없음 | 캐시 있음 | 개선 |
|---------|----------|----------|------|
| 첫 빌드 | 10분 | 10분 | - |
| 소스 변경 | 10분 | 1분 | **90%↓** |
| 의존성 추가 | 10분 | 3분 | **70%↓** |

**꼬리 질문**
- Q: 캐시가 너무 커지면 어떻게 하나요?
- A: `docker builder prune`로 주기적으로 정리하거나, `cache-to`에서 `mode=min`을 사용합니다.

**실무 연관**
- 대규모 프로젝트에서 캐시 활용으로 CI/CD 비용을 월 $500에서 $50으로 90% 절감한 사례가 있습니다.

</details>

<details>
<summary><strong>4. GitHub Actions의 재사용 가능한 워크플로우(Reusable Workflow)를 설명하세요.</strong></summary>

**모범 답안 포인트**
- 중복 제거: 동일한 빌드 로직을 여러 곳에서 재사용
- `workflow_call` 트리거: 다른 워크플로우에서 호출 가능
- 입력 파라미터: `inputs`로 동적 값 전달
- 시크릿 전달: `secrets`로 민감한 정보 전달
- DRY 원칙: Don't Repeat Yourself

**예시 답변**
> "재사용 가능한 워크플로우는 동일한 CI/CD 로직을 여러 프로젝트나 모듈에서 재사용할 수 있는 기능입니다. 예를 들어, 멀티 모듈 프로젝트에서 각 모듈의 빌드 과정이 비슷하다면 하나의 재사용 가능한 워크플로우를 만들어 각 모듈에서 호출할 수 있습니다. 재사용 워크플로우는 `on: workflow_call`로 정의하고, `inputs`로 모듈 이름이나 경로 같은 파라미터를 받습니다. 호출하는 쪽에서는 `uses: ./.github/workflows/reusable.yml`로 불러오고 `with`로 파라미터를 전달합니다. 이렇게 하면 빌드 로직을 한 곳에서 관리하여 유지보수가 쉬워집니다."

**실무 예시**
```yaml
# .github/workflows/reusable-build.yml (재사용 워크플로우)
name: Reusable Build
on:
  workflow_call:
    inputs:
      module_name:
        required: true
        type: string
    secrets:
      registry_token:
        required: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build ${{ inputs.module_name }}
        run: ./gradlew :modules:${{ inputs.module_name }}:build
      - name: Push image
        run: docker push myapp/${{ inputs.module_name }}
        env:
          TOKEN: ${{ secrets.registry_token }}
```

```yaml
# .github/workflows/build-all.yml (호출하는 워크플로우)
name: Build All Modules
on: push

jobs:
  build-user:
    uses: ./.github/workflows/reusable-build.yml
    with:
      module_name: user
    secrets:
      registry_token: ${{ secrets.GITHUB_TOKEN }}

  build-account:
    uses: ./.github/workflows/reusable-build.yml
    with:
      module_name: account
    secrets:
      registry_token: ${{ secrets.GITHUB_TOKEN }}
```

**꼬리 질문**
- Q: Organization 레벨에서도 재사용 워크플로우를 공유할 수 있나요?
- A: 네, `uses: myorg/workflows/.github/workflows/reusable.yml@main` 형식으로 가능합니다.

**실무 연관**
- 마이크로서비스 10개를 관리할 때 재사용 워크플로우로 중복 코드 500줄을 50줄로 줄인 경험이 있습니다.

</details>

<details>
<summary><strong>5. 보안 스캔(Trivy, Snyk)을 CI/CD에 통합하는 전략은?</strong></summary>

**모범 답안 포인트**
- 멀티 레이어 스캔: 소스 코드, 의존성, Docker 이미지 모두 스캔
- 심각도 설정: CRITICAL/HIGH는 실패, MEDIUM 이하는 경고
- SARIF 업로드: GitHub Security 탭에서 취약점 관리
- 정기 스캔: Cron으로 매일 자동 스캔
- 빠른 피드백: PR 단계에서 미리 차단

**예시 답변**
> "보안 스캔을 CI/CD에 통합할 때는 여러 레이어에서 검증하는 것이 중요합니다. 첫째, Snyk로 소스 코드와 의존성을 스캔하여 알려진 취약점을 찾습니다. 둘째, Docker 이미지를 빌드한 후 Trivy로 이미지 내부의 패키지 취약점을 스캔합니다. 셋째, 심각도를 설정하여 CRITICAL이나 HIGH 등급이 발견되면 파이프라인을 실패시켜 배포를 차단합니다. 넷째, SARIF 형식으로 결과를 업로드하여 GitHub Security 탭에서 취약점을 추적 관리합니다. 마지막으로 Cron으로 매일 자동 스캔을 실행하여 새로 발견된 CVE에 빠르게 대응합니다."

**실무 예시**
```yaml
# Trivy 이미지 스캔
- name: Run Trivy scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'myapp:${{ github.sha }}'
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'  # CRITICAL/HIGH 발견 시 실패

# GitHub Security에 업로드
- name: Upload to Security tab
  uses: github/codeql-action/upload-sarif@v3
  if: always()
  with:
    sarif_file: 'trivy-results.sarif'

# Snyk 의존성 스캔
- name: Run Snyk
  uses: snyk/actions/gradle@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
  with:
    args: --severity-threshold=high
```

**스캔 통계**:
| 도구 | 대상 | 발견 시점 | 처리 |
|-----|------|----------|------|
| Snyk | 의존성 | PR 단계 | 자동 차단 |
| Trivy | Docker 이미지 | 빌드 후 | 실패/경고 |
| Cron 스캔 | 전체 | 매일 자정 | Security 탭 |

**꼬리 질문**
- Q: False Positive는 어떻게 처리하나요?
- A: `.trivyignore` 파일로 특정 CVE를 무시하거나, Snyk Policy로 예외 처리합니다.

**실무 연관**
- Log4Shell(CVE-2021-44228) 취약점이 발견되었을 때 자동 스캔으로 1시간 내에 모든 영향받는 서비스를 파악하고 패치할 수 있었습니다.

</details>

---

## 📝 핵심 정리

### 이 장에서 배운 핵심 개념

| 개념 | 설명 | 핵심 키워드 |
|------|------|-------------|
| CI/CD | 코드 통합 및 배포 자동화 | Continuous Integration, Continuous Delivery/Deployment |
| GitHub Actions | GitHub 네이티브 CI/CD 도구 | Workflow, Job, Step, Event |
| GitLab CI | GitLab 네이티브 CI/CD 도구 | Pipeline, Stage, Job, Runner |
| Docker Build 최적화 | 빌드 시간 및 크기 최적화 | BuildKit, Multi-stage, Layer Caching |
| 보안 스캔 | 취약점 자동 탐지 | Trivy, Snyk, CVE, SARIF |
| 블루-그린 배포 | 무중단 배포 전략 | Blue Environment, Green Environment, Traffic Switch |

### 필수 명령어/코드 정리

| 명령어/코드 | 용도 | 예시 |
|-------------|------|------|
| `docker build --cache-from` | 캐시 활용 빌드 | `docker build --cache-from myapp:latest -t myapp:new .` |
| `docker buildx build --platform` | 멀티 플랫폼 빌드 | `docker buildx build --platform linux/amd64,linux/arm64 .` |
| `kubectl rollout undo` | Kubernetes 롤백 | `kubectl rollout undo deployment/myapp` |
| `trivy image` | 이미지 보안 스캔 | `trivy image --severity CRITICAL myapp:latest` |
| `gh workflow run` | 워크플로우 수동 실행 | `gh workflow run deploy.yml` |

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] 모든 커밋마다 자동 테스트 실행
- [ ] 보안 스캔을 필수 단계로 포함
- [ ] BuildKit 캐시로 빌드 시간 최적화
- [ ] 프로덕션 배포는 수동 승인 필요
- [ ] 변경된 모듈만 빌드하여 비용 절감
- [ ] 시크릿은 GitHub Secrets/GitLab Variables로 관리
- [ ] 배포 실패 시 자동 롤백 구현
- [ ] Slack/이메일 알림 설정

#### ❌ 하지 말아야 할 것
- [ ] 테스트 없이 프로덕션 배포
- [ ] 코드에 비밀번호 하드코딩
- [ ] 수동 배포 프로세스 유지
- [ ] 캐시 없이 매번 전체 빌드
- [ ] 보안 스캔 결과 무시
- [ ] 배포 실패 알림 설정 누락
- [ ] 금요일 저녁 프로덕션 배포
- [ ] 롤백 계획 없이 배포

### 성능/보안 체크리스트

#### 성능
- [ ] BuildKit 캐시 활성화 (`cache-from`, `cache-to`)
- [ ] 멀티 스테이지 빌드로 이미지 크기 최소화
- [ ] Gradle/Maven 의존성 캐싱
- [ ] 변경된 모듈만 빌드 (paths-filter)
- [ ] 병렬 빌드로 시간 단축 (matrix strategy)
- [ ] .dockerignore로 불필요한 파일 제외

#### 보안
- [ ] 이미지 보안 스캔 (Trivy/Snyk)
- [ ] Dockerfile 린팅 (Hadolint)
- [ ] 시크릿 스캔 (TruffleHog)
- [ ] 비루트 사용자로 컨테이너 실행
- [ ] 이미지 서명 (Cosign)
- [ ] 정기적인 의존성 업데이트
- [ ] SARIF 업로드로 취약점 추적
- [ ] 최소 권한 원칙 적용

---

## 🔗 관련 기술

**이 기술과 함께 사용하는 기술들**

| 기술 | 관계 | 학습 우선순위 |
|------|------|---------------|
| Docker | 컨테이너 이미지 빌드 및 배포 | ⭐⭐⭐⭐⭐ |
| Kubernetes | 컨테이너 오케스트레이션 | ⭐⭐⭐⭐ |
| Terraform | 인프라 자동화 (IaC) | ⭐⭐⭐ |
| Prometheus/Grafana | 모니터링 및 알림 | ⭐⭐⭐⭐ |
| ArgoCD | GitOps 기반 배포 | ⭐⭐⭐ |
| Jenkins | 레거시 CI/CD 도구 | ⭐⭐ |

---

## 🚀 다음 단계

### 다음 장 미리보기: 19. 프로덕션 배포 전략
- **배울 내용 1**: 블루-그린 배포 심화 (데이터베이스 마이그레이션 포함)
- **배울 내용 2**: 카나리 배포로 안전한 점진적 롤아웃
- **배울 내용 3**: A/B 테스트를 활용한 기능 검증
- **배울 내용 4**: 롤링 업데이트와 롤백 전략
- **실전 프로젝트**: LK-Trade 프로젝트 프로덕션 배포 시나리오

### 이 장과의 연결점
```
이번 장에서 배운 CI/CD 파이프라인
    ↓
다음 장에서 다양한 배포 전략 적용
    ↓
최종적으로 안전하고 빠른 프로덕션 배포
```

### 준비하면 좋을 것들
```bash
# Kubernetes 클러스터 준비 (Minikube 또는 Kind)
minikube start

# Istio 설치 (카나리 배포용)
istioctl install --set profile=demo -y

# ArgoCD 설치 (GitOps용)
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

---

## 📚 추가 학습 자료

### 공식 문서
- [GitHub Actions 공식 문서](https://docs.github.com/en/actions)
- [GitLab CI/CD 문서](https://docs.gitlab.com/ee/ci/)
- [Docker Build 최적화 가이드](https://docs.docker.com/build/building/best-practices/)

### 추천 블로그/아티클
- [Trivy로 컨테이너 보안 강화하기](https://aquasecurity.github.io/trivy/)
- [GitHub Actions 베스트 프랙티스](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [효율적인 Docker 레이어 캐싱](https://docs.docker.com/build/cache/)

### 영상 강의
- [GitHub Actions 완전 정복 (한글)](https://www.youtube.com/watch?v=example)
- [GitLab CI/CD 마스터 클래스](https://www.youtube.com/watch?v=example)

### 컨퍼런스 발표
- [Netflix의 CI/CD 진화 - AWS re:Invent](https://www.youtube.com/watch?v=example)
- [Kubernetes 기반 CI/CD - KubeCon](https://www.youtube.com/watch?v=example)

### 오픈소스 프로젝트
- [awesome-actions](https://github.com/sdras/awesome-actions) - GitHub Actions 액션 모음
- [GitLab CI 예제 모음](https://gitlab.com/gitlab-examples)

---

## 🎉 축하합니다!

**이제 여러분은**:
✅ GitHub Actions와 GitLab CI로 CI/CD 파이프라인을 구축할 수 있습니다
✅ Docker 이미지 빌드를 최적화하여 시간과 비용을 절감할 수 있습니다
✅ 자동화된 테스트와 보안 스캔으로 품질을 보장할 수 있습니다
✅ 멀티 모듈 프로젝트에서 효율적인 빌드 전략을 적용할 수 있습니다
✅ 프로덕션 배포를 안전하게 자동화할 수 있습니다

**다음 단계**:
- [ ] 다음 장: 19. 프로덕션 배포 전략으로 진행
- [ ] 실전 프로젝트: 자신의 프로젝트에 CI/CD 파이프라인 적용
- [ ] 면접 질문 복습하여 개념 확실히 정리

---

**다음 장으로 이동**: [다음: 19장 프로덕션 배포 전략 →](19-프로덕션-배포-전략.md)

**이전 장으로 돌아가기**: [← 이전: 17장 Docker Swarm](17-Docker-Swarm.md)

**목차로 돌아가기**: [📚 전체 목차](README.md)