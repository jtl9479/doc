# 섹션 30: CI/CD 파이프라인 (GitHub Actions)

> **학습 목표**: GitHub Actions를 활용하여 Docker 이미지 빌드부터 배포까지 완전 자동화된 CI/CD 파이프라인을 구축하고, 코드 푸시만으로 프로덕션 배포가 가능한 DevOps 워크플로우를 구현할 수 있습니다.

**⏱️ 예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐⭐☆ (4개/5개)

---

## 🔍 실생활 비유로 이해하기

CI/CD는 **자동차 조립 라인**과 같습니다.

```
자동차 공장 조립 라인                CI/CD 파이프라인
====================                ====================
🔧 부품 검사                    →    코드 린트/테스트
🔩 조립                         →    빌드
🎨 도색                         →    Docker 이미지 생성
🔍 품질 검사                    →    보안 스캔
🚗 시험 주행                    →    스테이징 배포
✅ 출고                         →    프로덕션 배포
📊 피드백 수집                  →    모니터링
```

수작업으로 자동차를 만들면 느리고 실수가 많듯이, 수동 배포는 느리고 에러가 발생하기 쉽습니다.

---

## 💡 왜 CI/CD가 필요한가?

### 1. 수동 배포의 문제점

```
❌ 수동 배포 프로세스
===================

개발자: "배포 좀 해주세요"
DevOps: "알겠습니다"

1. 코드 pull
2. 테스트 실행 (5분)
3. 빌드 (10분)
4. Docker 이미지 생성 (5분)
5. 이미지 푸시
6. 서버 접속
7. docker-compose down
8. docker-compose pull
9. docker-compose up -d
10. 헬스 체크
11. 로그 확인

총 소요 시간: 30분
문제점:
- 사람이 실수할 수 있음
- 시간이 오래 걸림
- 밤/주말 배포 불가
- 문서화 누락
- 테스트 건너뛸 수 있음


✅ 자동화된 CI/CD
==================

개발자: git push origin main
    ↓
GitHub Actions 자동 실행:
✓ 테스트 (2분)
✓ 빌드 (3분)
✓ 보안 스캔 (1분)
✓ 이미지 푸시 (2분)
✓ 배포 (2분)
✓ 헬스 체크 (1분)
✓ 슬랙 알림

총 소요 시간: 11분
장점:
- 자동화로 실수 방지
- 빠른 배포
- 24/7 배포 가능
- 모든 단계 기록
- 테스트 필수 실행
```

### 2. CI/CD의 이점

```
┌─────────────────────┬──────────────┬──────────────┐
│ 지표                │ 수동 배포    │ CI/CD        │
├─────────────────────┼──────────────┼──────────────┤
│ 배포 빈도           │ 주 1회       │ 일 10회+     │
│ 배포 시간           │ 30분         │ 10분         │
│ 배포 실패율         │ 20%          │ 2%           │
│ 평균 복구 시간      │ 4시간        │ 15분         │
│ 개발자 대기 시간    │ 1시간        │ 0분          │
└─────────────────────┴──────────────┴──────────────┘

결과:
- 생산성 3배 향상
- 배포 신뢰도 10배 향상
- 빠른 피드백 루프
- 시장 출시 시간 단축
```

---

## GitHub Actions 기초

### 1. GitHub Actions 구조

```
Repository
│
├── .github/
│   └── workflows/
│       ├── ci.yml          ← CI 워크플로우
│       ├── cd.yml          ← CD 워크플로우
│       └── security.yml    ← 보안 스캔
│
└── (프로젝트 파일들)

워크플로우 구조:
===============

Workflow (ci.yml)
    ├── Trigger (on: push, pull_request)
    ├── Job 1: Test
    │   ├── Step 1: Checkout code
    │   ├── Step 2: Setup Java
    │   ├── Step 3: Run tests
    │   └── Step 4: Upload test results
    ├── Job 2: Build
    │   ├── Step 1: Checkout code
    │   ├── Step 2: Build Docker image
    │   └── Step 3: Push to registry
    └── Job 3: Deploy
        ├── Step 1: Deploy to staging
        └── Step 2: Health check
```

### 2. 기본 워크플로우 예시

```yaml
# .github/workflows/hello.yml
name: Hello World

on:
  push:
    branches: [main]

jobs:
  greet:
    runs-on: ubuntu-latest
    steps:
      - name: Say Hello
        run: echo "Hello, World!"

      - name: Show Date
        run: date

      - name: List Files
        run: ls -la
```

---

## LK-Trade CI 파이프라인

### 1. CI 워크플로우 (테스트 & 빌드)

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
    paths:
      - 'modules/**'
      - '.github/workflows/ci.yml'
  pull_request:
    branches: [main, develop]

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: lk-trade

jobs:
  # ========================================
  # Job 1: 코드 품질 검사
  # ========================================
  code-quality:
    name: Code Quality Check
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'gradle'

      - name: Grant execute permission for gradlew
        run: chmod +x gradlew

      - name: Run Ktlint
        run: ./gradlew ktlintCheck

      - name: Run Detekt
        run: ./gradlew detekt

      - name: Upload Detekt Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: detekt-report
          path: build/reports/detekt/

  # ========================================
  # Job 2: 단위 테스트
  # ========================================
  unit-test:
    name: Unit Tests
    runs-on: ubuntu-latest
    strategy:
      matrix:
        module: [user, trade, account, strategy]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'gradle'

      - name: Run Unit Tests - ${{ matrix.module }}
        run: ./gradlew :modules:${{ matrix.module }}:api:test

      - name: Generate Test Report
        if: always()
        run: ./gradlew :modules:${{ matrix.module }}:api:jacocoTestReport

      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.module }}
          path: modules/${{ matrix.module }}/api/build/test-results/

      - name: Upload Coverage Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report-${{ matrix.module }}
          path: modules/${{ matrix.module }}/api/build/reports/jacoco/

      - name: Comment Test Results on PR
        if: github.event_name == 'pull_request'
        uses: EnricoMi/publish-unit-test-result-action@v2
        with:
          files: modules/${{ matrix.module }}/api/build/test-results/**/*.xml

  # ========================================
  # Job 3: 통합 테스트
  # ========================================
  integration-test:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: [unit-test]
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: lk_trade_test
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'gradle'

      - name: Run Integration Tests
        env:
          SPRING_DATASOURCE_URL: jdbc:postgresql://localhost:5432/lk_trade_test
          SPRING_DATASOURCE_USERNAME: test_user
          SPRING_DATASOURCE_PASSWORD: test_password
          SPRING_REDIS_HOST: localhost
          SPRING_REDIS_PORT: 6379
        run: ./gradlew integrationTest

      - name: Upload Integration Test Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: integration-test-results
          path: build/test-results/integrationTest/

  # ========================================
  # Job 4: Docker 이미지 빌드
  # ========================================
  build-images:
    name: Build Docker Images
    runs-on: ubuntu-latest
    needs: [code-quality, unit-test, integration-test]
    if: github.event_name == 'push'
    strategy:
      matrix:
        service: [user-service, trade-service, account-service, strategy-service]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ github.repository_owner }}/${{ env.IMAGE_PREFIX }}/${{ matrix.service }}
          tags: |
            type=ref,event=branch
            type=sha,prefix={{branch}}-
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - name: Determine module path
        id: module
        run: |
          case "${{ matrix.service }}" in
            user-service) echo "path=modules/user/api" >> $GITHUB_OUTPUT ;;
            trade-service) echo "path=modules/trade/api" >> $GITHUB_OUTPUT ;;
            account-service) echo "path=modules/account/api" >> $GITHUB_OUTPUT ;;
            strategy-service) echo "path=modules/strategy/api" >> $GITHUB_OUTPUT ;;
          esac

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: ${{ steps.module.outputs.path }}
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            BUILD_DATE=${{ github.event.head_commit.timestamp }}
            VCS_REF=${{ github.sha }}
            VERSION=${{ steps.meta.outputs.version }}

  # ========================================
  # Job 5: 보안 스캔
  # ========================================
  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: [build-images]
    strategy:
      matrix:
        service: [user-service, trade-service, account-service, strategy-service]
    steps:
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ github.repository_owner }}/${{ env.IMAGE_PREFIX }}/${{ matrix.service }}:${{ github.ref_name }}-${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results-${{ matrix.service }}.sarif'
          severity: 'HIGH,CRITICAL'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: 'trivy-results-${{ matrix.service }}.sarif'

      - name: Fail on high/critical vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ github.repository_owner }}/${{ env.IMAGE_PREFIX }}/${{ matrix.service }}:${{ github.ref_name }}-${{ github.sha }}
          format: 'table'
          exit-code: '1'
          severity: 'HIGH,CRITICAL'

  # ========================================
  # Job 6: 알림
  # ========================================
  notify:
    name: Send Notifications
    runs-on: ubuntu-latest
    needs: [security-scan]
    if: always()
    steps:
      - name: Send Slack notification
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: |
            CI Pipeline ${{ job.status }}
            Branch: ${{ github.ref_name }}
            Commit: ${{ github.sha }}
            Author: ${{ github.actor }}
          webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## CD 파이프라인 (배포)

### 1. Staging 환경 자동 배포

```yaml
# .github/workflows/cd-staging.yml
name: CD - Deploy to Staging

on:
  push:
    branches: [develop]
  workflow_dispatch:  # 수동 실행 가능

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: lk-trade

jobs:
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.lk-trade.com
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.STAGING_SSH_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.STAGING_HOST }} >> ~/.ssh/known_hosts

      - name: Deploy to Staging Server
        env:
          HOST: ${{ secrets.STAGING_HOST }}
          USER: ${{ secrets.STAGING_USER }}
          VERSION: ${{ github.ref_name }}-${{ github.sha }}
        run: |
          ssh $USER@$HOST << 'ENDSSH'
            cd /opt/lk-trade

            # 환경 변수 설정
            export VERSION=${{ env.VERSION }}
            export REGISTRY=${{ env.REGISTRY }}
            export GITHUB_ACTOR=${{ github.actor }}

            # GitHub Container Registry 로그인
            echo "${{ secrets.GITHUB_TOKEN }}" | docker login $REGISTRY -u $GITHUB_ACTOR --password-stdin

            # Docker Compose로 배포
            docker-compose pull
            docker-compose up -d

            # 헬스 체크
            sleep 30
            curl -f http://localhost:8080/actuator/health || exit 1

            echo "Deployment to staging completed successfully!"
          ENDSSH

      - name: Run Smoke Tests
        run: |
          # 기본 API 테스트
          curl -f https://staging.lk-trade.com/health
          curl -f https://staging.lk-trade.com/api/v1/health

      - name: Notify Slack
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: |
            Staging Deployment ${{ job.status }}
            Version: ${{ github.ref_name }}-${{ github.sha }}
            URL: https://staging.lk-trade.com
          webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 2. Production 환경 수동 승인 배포

```yaml
# .github/workflows/cd-production.yml
name: CD - Deploy to Production

on:
  push:
    branches: [main]
    tags:
      - 'v*.*.*'
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to deploy'
        required: true
        type: string

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: lk-trade

jobs:
  # ========================================
  # Job 1: 프로덕션 배포 준비
  # ========================================
  prepare-deployment:
    name: Prepare Production Deployment
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Determine version
        id: version
        run: |
          if [ "${{ github.event_name }}" == "workflow_dispatch" ]; then
            echo "version=${{ inputs.version }}" >> $GITHUB_OUTPUT
          elif [ "${{ github.ref_type }}" == "tag" ]; then
            echo "version=${{ github.ref_name }}" >> $GITHUB_OUTPUT
          else
            echo "version=${{ github.ref_name }}-${{ github.sha }}" >> $GITHUB_OUTPUT
          fi

      - name: Create deployment summary
        run: |
          echo "# Production Deployment Summary" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "- **Version**: ${{ steps.version.outputs.version }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Branch**: ${{ github.ref_name }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Commit**: ${{ github.sha }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Author**: ${{ github.actor }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Timestamp**: $(date -u)" >> $GITHUB_STEP_SUMMARY

  # ========================================
  # Job 2: 프로덕션 배포 (수동 승인 필요)
  # ========================================
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [prepare-deployment]
    environment:
      name: production
      url: https://lk-trade.com
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Create backup
        env:
          HOST: ${{ secrets.PROD_HOST }}
          USER: ${{ secrets.PROD_USER }}
        run: |
          ssh $USER@$HOST << 'ENDSSH'
            cd /opt/lk-trade
            bash scripts/backup-all.sh
          ENDSSH

      - name: Blue-Green Deployment
        env:
          HOST: ${{ secrets.PROD_HOST }}
          USER: ${{ secrets.PROD_USER }}
          VERSION: ${{ needs.prepare-deployment.outputs.version }}
        run: |
          ssh $USER@$HOST << 'ENDSSH'
            cd /opt/lk-trade

            # 환경 변수 설정
            export VERSION=${{ env.VERSION }}
            export REGISTRY=${{ env.REGISTRY }}

            # GitHub Container Registry 로그인
            echo "${{ secrets.GITHUB_TOKEN }}" | docker login $REGISTRY -u ${{ github.actor }} --password-stdin

            # Blue-Green 배포 실행
            bash scripts/blue-green-deploy.sh

            echo "Production deployment completed!"
          ENDSSH

      - name: Health Check
        run: |
          echo "Waiting for services to be healthy..."
          sleep 60

          # 모든 서비스 헬스 체크
          services=(user trade account strategy)
          for service in "${services[@]}"; do
            echo "Checking $service-service..."
            curl -f https://lk-trade.com/api/$service/actuator/health || exit 1
          done

          echo "All services are healthy!"

      - name: Run Production Smoke Tests
        run: |
          # 중요 API 테스트
          curl -f https://lk-trade.com/api/v1/health
          curl -f https://lk-trade.com/api/user/actuator/health
          curl -f https://lk-trade.com/api/trade/actuator/health

      - name: Update deployment record
        run: |
          # 배포 기록 저장
          echo "Deployment completed at $(date -u)" >> deployment-log.txt
          echo "Version: ${{ needs.prepare-deployment.outputs.version }}" >> deployment-log.txt

      - name: Notify Slack - Success
        if: success()
        uses: 8398a7/action-slack@v3
        with:
          status: custom
          custom_payload: |
            {
              "text": "🚀 Production Deployment Successful!",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Production Deployment Successful!* ✅"
                  }
                },
                {
                  "type": "section",
                  "fields": [
                    {"type": "mrkdwn", "text": "*Version:*\n${{ needs.prepare-deployment.outputs.version }}"},
                    {"type": "mrkdwn", "text": "*Deployed by:*\n${{ github.actor }}"},
                    {"type": "mrkdwn", "text": "*Branch:*\n${{ github.ref_name }}"},
                    {"type": "mrkdwn", "text": "*URL:*\n<https://lk-trade.com|lk-trade.com>"}
                  ]
                }
              ]
            }
          webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}

      - name: Notify Slack - Failure
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: custom
          custom_payload: |
            {
              "text": "🚨 Production Deployment Failed!",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Production Deployment Failed!* ❌"
                  }
                },
                {
                  "type": "section",
                  "fields": [
                    {"type": "mrkdwn", "text": "*Version:*\n${{ needs.prepare-deployment.outputs.version }}"},
                    {"type": "mrkdwn", "text": "*Attempted by:*\n${{ github.actor }}"},
                    {"type": "mrkdwn", "text": "*Action:*\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Logs>"}
                  ]
                }
              ]
            }
          webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}

  # ========================================
  # Job 3: 롤백 (배포 실패 시)
  # ========================================
  rollback:
    name: Rollback on Failure
    runs-on: ubuntu-latest
    needs: [deploy-production]
    if: failure()
    steps:
      - name: Rollback deployment
        env:
          HOST: ${{ secrets.PROD_HOST }}
          USER: ${{ secrets.PROD_USER }}
        run: |
          ssh $USER@$HOST << 'ENDSSH'
            cd /opt/lk-trade
            bash scripts/blue-green-rollback.sh
          ENDSSH

      - name: Notify rollback
        uses: 8398a7/action-slack@v3
        with:
          status: custom
          custom_payload: |
            {
              "text": "⏪ Production Rollback Completed",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Rollback completed due to deployment failure*"
                  }
                }
              ]
            }
          webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## GitHub Secrets 설정

```bash
# GitHub Repository Settings > Secrets and variables > Actions

# SSH 접속 정보
STAGING_HOST=staging.lk-trade.com
STAGING_USER=deploy
STAGING_SSH_KEY=<private-key-content>

PROD_HOST=lk-trade.com
PROD_USER=deploy
PROD_SSH_KEY=<private-key-content>

# 알림
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX

# 데이터베이스 (테스트용)
DB_PASSWORD=test_password

# 기타
GITHUB_TOKEN=<automatically-provided>
```

### Secrets 설정 방법

```bash
# 1. SSH 키 생성
ssh-keygen -t ed25519 -C "github-actions@lk-trade.com" -f ~/.ssh/github-actions

# 2. 공개 키를 서버에 추가
ssh-copy-id -i ~/.ssh/github-actions.pub deploy@lk-trade.com

# 3. 개인 키를 GitHub Secrets에 추가
cat ~/.ssh/github-actions
# 내용 복사 후 GitHub Secrets에 PROD_SSH_KEY로 등록
```

---

## 고급 기능

### 1. Matrix 전략 (병렬 실행)

```yaml
# 여러 버전/환경에서 동시 테스트
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        java: ['11', '17', '21']
        exclude:
          - os: macos-latest
            java: '11'
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: ${{ matrix.java }}
      - run: ./gradlew test
```

### 2. Reusable Workflows (재사용 가능한 워크플로우)

```yaml
# .github/workflows/reusable-build.yml
name: Reusable Build Workflow

on:
  workflow_call:
    inputs:
      service-name:
        required: true
        type: string
      module-path:
        required: true
        type: string
    outputs:
      image-tag:
        description: "Built image tag"
        value: ${{ jobs.build.outputs.tag }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        # ... 빌드 로직
```

```yaml
# .github/workflows/build-all-services.yml
name: Build All Services

on: [push]

jobs:
  build-user-service:
    uses: ./.github/workflows/reusable-build.yml
    with:
      service-name: user-service
      module-path: modules/user/api

  build-trade-service:
    uses: ./.github/workflows/reusable-build.yml
    with:
      service-name: trade-service
      module-path: modules/trade/api
```

### 3. Composite Actions (커스텀 액션)

```yaml
# .github/actions/setup-kotlin-env/action.yml
name: 'Setup Kotlin Environment'
description: 'Setup Java, Kotlin, and Gradle with caching'

inputs:
  java-version:
    description: 'Java version to use'
    required: false
    default: '17'

runs:
  using: 'composite'
  steps:
    - name: Setup Java
      uses: actions/setup-java@v4
      with:
        java-version: ${{ inputs.java-version }}
        distribution: 'temurin'
        cache: 'gradle'

    - name: Grant execute permission for gradlew
      shell: bash
      run: chmod +x gradlew

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

사용:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-kotlin-env
        with:
          java-version: '17'
      - run: ./gradlew test
```

---

## 모니터링 및 디버깅

### 1. 워크플로우 실행 모니터링

```yaml
# .github/workflows/monitor.yml
name: Monitor Workflow Performance

on:
  workflow_run:
    workflows: ["CI Pipeline"]
    types: [completed]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - name: Analyze workflow run
        uses: actions/github-script@v7
        with:
          script: |
            const run = context.payload.workflow_run;

            console.log(`Workflow: ${run.name}`);
            console.log(`Status: ${run.conclusion}`);
            console.log(`Duration: ${(new Date(run.updated_at) - new Date(run.created_at)) / 1000}s`);

            // Slack으로 알림
            if (run.conclusion === 'failure') {
              // 실패 알림 로직
            }
```

### 2. 디버깅 팁

```yaml
# 디버그 모드 활성화
jobs:
  debug:
    runs-on: ubuntu-latest
    steps:
      - name: Enable debug logging
        run: echo "ACTIONS_STEP_DEBUG=true" >> $GITHUB_ENV

      - name: Print environment
        run: |
          echo "GitHub Context:"
          echo "${{ toJSON(github) }}"

          echo "Environment Variables:"
          env | sort

      - name: SSH debug session (필요 시)
        uses: mxschmitt/action-tmate@v3
        if: failure()
```

---

## 비용 최적화

### 1. Self-hosted Runners

```yaml
# 자체 호스팅 러너 사용 (무료)
jobs:
  build:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t myapp .
```

러너 설정:

```bash
# 서버에 러너 설치
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# 러너 등록
./config.sh --url https://github.com/your-org/lk-trade --token YOUR_TOKEN

# 러너 시작
./run.sh

# 또는 서비스로 등록
sudo ./svc.sh install
sudo ./svc.sh start
```

### 2. 캐싱 최적화

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Gradle 캐싱
      - uses: actions/cache@v3
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*') }}
          restore-keys: |
            ${{ runner.os }}-gradle-

      # Docker 레이어 캐싱
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build with cache
        uses: docker/build-push-action@v5
        with:
          context: .
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

## 다음 단계

축하합니다! 🎉 GitHub Actions로 완전한 CI/CD 파이프라인을 구축했습니다.

### 이번 섹션에서 배운 것

✅ CI/CD의 중요성 및 이점
✅ GitHub Actions 기본 구조
✅ 코드 품질 검사 및 테스트 자동화
✅ Docker 이미지 자동 빌드 및 푸시
✅ 보안 스캔 통합
✅ Staging/Production 자동 배포
✅ Blue-Green 배포 자동화
✅ Slack 알림 통합
✅ 고급 기능 (Matrix, Reusable Workflows)
✅ 비용 최적화

### 다음에 배울 것

**섹션 31: Jenkins를 이용한 CI/CD**에서는:
- Jenkins 설치 및 설정
- Jenkinsfile (Pipeline as Code)
- Jenkins + Docker 통합
- Jenkins vs GitHub Actions 비교

### 추가 학습 자료

**공식 문서:**
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

**유용한 액션:**
- [Awesome Actions](https://github.com/sdras/awesome-actions)
- [GitHub Marketplace](https://github.com/marketplace?type=actions)

---

## 👨‍💻 주니어 개발자 시나리오

### 시나리오 1: 첫 GitHub Actions 워크플로우 작성

**상황:** 신입 개발자로 입사한 첫날, 팀장님이 "간단한 CI 워크플로우를 추가해주세요"라고 요청했습니다.

**문제:**
```
"어디서부터 시작해야 하지?
.github/workflows 디렉토리를 어떻게 만들지?
워크플로우 파일은 어떻게 작성하지?"
```

**단계별 해결:**

```bash
# 1단계: 디렉토리 구조 생성
mkdir -p .github/workflows

# 2단계: 첫 번째 워크플로우 파일 작성
cat > .github/workflows/hello.yml << 'EOF'
name: My First Workflow

on:
  push:
    branches: [main]

jobs:
  greet:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Say Hello
        run: echo "Hello, GitHub Actions!"

      - name: Show Date
        run: date
EOF

# 3단계: Git에 추가 및 푸시
git add .github/workflows/hello.yml
git commit -m "Add first GitHub Actions workflow"
git push origin main

# 4단계: GitHub에서 확인
# Repository > Actions 탭 확인
```

**실제 화면에서 보이는 것:**
```
✅ Workflow 실행 성공!

Greet
├── Checkout code (5s)
├── Say Hello (1s)
│   Hello, GitHub Actions!
└── Show Date (1s)
    Mon Oct 20 10:30:45 UTC 2025
```

**배운 점:**
1. `.github/workflows` 디렉토리가 필수
2. YAML 파일로 워크플로우 정의
3. `on:` 트리거 설정이 중요
4. `uses:`는 기존 액션 사용, `run:`은 명령 실행
5. GitHub UI에서 실시간 로그 확인 가능

**팀장님의 피드백:**
```
"잘했어요! 이제 실제 테스트를 추가해볼까요?"
```

---

### 시나리오 2: CI 실패 디버깅 - "테스트가 로컬에서는 되는데 CI에서 실패해요!"

**상황:** 로컬에서는 모든 테스트가 통과하는데 GitHub Actions에서만 실패합니다.

**에러 메시지:**
```
Error: Database connection failed
  at UserServiceTest.kt:45

Expected: Connection successful
Actual: Connection timeout

❌ Tests failed: 3 tests, 1 passed, 2 failed
```

**단계별 해결:**

```yaml
# ❌ 원래 워크플로우 (문제 있음)
name: CI

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Run tests
        run: ./gradlew test
      # 문제: 데이터베이스가 없음!
```

**수정된 워크플로우:**

```yaml
# ✅ 수정된 워크플로우 (서비스 추가)
name: CI with Database

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest

    # 핵심: 테스트에 필요한 서비스 추가!
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'gradle'

      - name: Wait for PostgreSQL
        run: |
          for i in {1..30}; do
            pg_isready -h localhost -p 5432 && break
            echo "Waiting for PostgreSQL..."
            sleep 1
          done

      - name: Run tests
        env:
          SPRING_DATASOURCE_URL: jdbc:postgresql://localhost:5432/test_db
          SPRING_DATASOURCE_USERNAME: test_user
          SPRING_DATASOURCE_PASSWORD: test_password
          SPRING_REDIS_HOST: localhost
          SPRING_REDIS_PORT: 6379
        run: ./gradlew test

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: build/test-results/
```

**결과:**
```
✅ All tests passed!

Test Results:
- Total: 45 tests
- Passed: 45 ✅
- Failed: 0
- Duration: 2m 30s
```

**배운 점:**
1. **Services** 블록으로 DB, Redis 등 추가 가능
2. **Health check**로 서비스 준비 확인
3. **Environment variables**로 연결 정보 전달
4. `if: always()`로 실패해도 결과 업로드
5. `pg_isready` 같은 도구로 서비스 대기

**디버깅 팁:**
```yaml
# 디버그 로그 활성화
- name: Enable Debug
  run: echo "ACTIONS_STEP_DEBUG=true" >> $GITHUB_ENV

# 환경 변수 출력
- name: Print Environment
  run: env | sort
```

---

### 시나리오 3: GitHub Secrets 설정 - "민감한 정보를 어떻게 관리하죠?"

**상황:** 배포를 위해 SSH 키와 API 토큰이 필요한데, 코드에 직접 넣을 수 없습니다.

**잘못된 방법 (절대 하지 말 것!):**
```yaml
# ❌ 위험! 민감 정보 노출!
- name: Deploy
  run: |
    ssh -i /tmp/private-key deploy@server.com
    export API_KEY="sk-1234567890abcdef"  # 절대 하면 안 됨!
```

**올바른 방법:**

**1단계: GitHub Secrets 추가**
```
GitHub Repository 설정:
1. Settings > Secrets and variables > Actions
2. "New repository secret" 클릭
3. 다음 시크릿 추가:

Name: PROD_SSH_KEY
Secret: -----BEGIN OPENSSH PRIVATE KEY-----
        b3BlbnNzaC1rZXktdjEAAA...
        -----END OPENSSH PRIVATE KEY-----

Name: PROD_HOST
Secret: production.lk-trade.com

Name: PROD_USER
Secret: deploy

Name: API_KEY
Secret: sk-1234567890abcdef

Name: SLACK_WEBHOOK_URL
Secret: https://hooks.slack.com/services/T00/B00/XXX
```

**2단계: 워크플로우에서 사용**
```yaml
name: Deploy to Production

on:
  workflow_dispatch:  # 수동 실행

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production  # 환경 보호 기능

    steps:
      - uses: actions/checkout@v4

      # SSH 키 설정
      - name: Configure SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.PROD_SSH_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.PROD_HOST }} >> ~/.ssh/known_hosts

      # 배포 스크립트 실행
      - name: Deploy
        env:
          API_KEY: ${{ secrets.API_KEY }}
        run: |
          ssh ${{ secrets.PROD_USER }}@${{ secrets.PROD_HOST }} << 'ENDSSH'
            cd /opt/lk-trade
            export API_KEY=${{ secrets.API_KEY }}
            docker-compose pull
            docker-compose up -d
          ENDSSH

      # Slack 알림
      - name: Notify Slack
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

**로그에서 보이는 것:**
```
Configure SSH
***  # Secret은 자동으로 마스킹됨!

Deploy
Connecting to ***@***...  # 호스트와 사용자도 마스킹
Deployment successful!

Notify Slack
Slack notification sent to #deployments
```

**배운 점:**
1. **절대 민감 정보를 코드에 넣지 말 것**
2. GitHub Secrets로 안전하게 관리
3. `${{ secrets.NAME }}` 문법으로 사용
4. 로그에 자동으로 마스킹됨 (***)
5. `environment:`로 추가 보호 (승인 필요)

**보안 체크리스트:**
```
✅ SSH 키는 Secrets에 저장
✅ API 키는 Secrets에 저장
✅ 비밀번호는 Secrets에 저장
✅ Secrets는 최소 권한 원칙
✅ 정기적으로 Secrets 교체
❌ .env 파일 커밋 금지
❌ 하드코딩 금지
❌ 로그에 민감 정보 출력 금지
```

---

### 시나리오 4: 자동 배포 파이프라인 구축

**상황:** develop 브랜치에 푸시하면 자동으로 Staging에 배포되도록 해야 합니다.

**요구사항:**
```
1. develop 브랜치 푸시 시 자동 배포
2. 테스트 실패 시 배포 중단
3. 배포 성공/실패 시 Slack 알림
4. 롤백 가능하도록 이전 버전 유지
```

**완전한 CD 워크플로우:**

```yaml
name: CD - Auto Deploy to Staging

on:
  push:
    branches: [develop]
    paths-ignore:
      - '**.md'
      - 'docs/**'

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: lk-trade

jobs:
  # Job 1: 테스트
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'gradle'

      - name: Run all tests
        run: ./gradlew test integrationTest

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: build/test-results/

  # Job 2: 빌드 및 푸시
  build:
    name: Build & Push Images
    runs-on: ubuntu-latest
    needs: [test]  # 테스트 성공 후에만 실행
    outputs:
      version: ${{ steps.version.outputs.version }}
    steps:
      - uses: actions/checkout@v4

      - name: Generate version
        id: version
        run: |
          VERSION="develop-$(date +%Y%m%d-%H%M%S)-${GITHUB_SHA::7}"
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "Generated version: $VERSION"

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push all services
        run: |
          services=(user-service trade-service account-service strategy-service)
          for service in "${services[@]}"; do
            echo "Building $service..."
            docker build \
              -t ${{ env.REGISTRY }}/${{ github.repository_owner }}/${{ env.IMAGE_PREFIX }}/$service:${{ steps.version.outputs.version }} \
              -t ${{ env.REGISTRY }}/${{ github.repository_owner }}/${{ env.IMAGE_PREFIX }}/$service:staging-latest \
              modules/${service%-service}/api

            docker push ${{ env.REGISTRY }}/${{ github.repository_owner }}/${{ env.IMAGE_PREFIX }}/$service:${{ steps.version.outputs.version }}
            docker push ${{ env.REGISTRY }}/${{ github.repository_owner }}/${{ env.IMAGE_PREFIX }}/$service:staging-latest
          done

  # Job 3: Staging 배포
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [build]
    environment:
      name: staging
      url: https://staging.lk-trade.com
    steps:
      - uses: actions/checkout@v4

      - name: Create backup point
        run: |
          echo "BACKUP_VERSION=${{ needs.build.outputs.version }}" >> $GITHUB_ENV
          echo "Backup point: ${{ needs.build.outputs.version }}"

      - name: Configure SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.STAGING_SSH_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.STAGING_HOST }} >> ~/.ssh/known_hosts

      - name: Deploy to Staging
        run: |
          ssh ${{ secrets.STAGING_USER }}@${{ secrets.STAGING_HOST }} << 'ENDSSH'
            cd /opt/lk-trade

            # 현재 실행 중인 버전 백업
            docker-compose ps --format json > backup/running-version.json

            # 환경 변수 설정
            export VERSION=${{ needs.build.outputs.version }}
            export REGISTRY=${{ env.REGISTRY }}

            # GitHub Registry 로그인
            echo "${{ secrets.GITHUB_TOKEN }}" | docker login $REGISTRY -u ${{ github.actor }} --password-stdin

            # 새 버전 배포
            docker-compose pull
            docker-compose up -d

            echo "Deployment completed!"
          ENDSSH

      - name: Wait for services
        run: sleep 30

      - name: Health Check
        id: health
        run: |
          services=(user trade account strategy)
          for service in "${services[@]}"; do
            echo "Checking $service-service..."
            if ! curl -f https://staging.lk-trade.com/api/$service/actuator/health; then
              echo "health_status=failed" >> $GITHUB_OUTPUT
              exit 1
            fi
          done
          echo "health_status=success" >> $GITHUB_OUTPUT

      - name: Smoke Tests
        if: steps.health.outputs.health_status == 'success'
        run: |
          # 기본 API 테스트
          curl -f https://staging.lk-trade.com/api/v1/health
          curl -f https://staging.lk-trade.com/api/user/actuator/health

          echo "All smoke tests passed!"

      - name: Rollback on failure
        if: failure()
        run: |
          echo "Deployment failed, rolling back..."
          ssh ${{ secrets.STAGING_USER }}@${{ secrets.STAGING_HOST }} << 'ENDSSH'
            cd /opt/lk-trade
            docker-compose down
            # 이전 버전으로 복구 로직
            docker-compose up -d
          ENDSSH

      - name: Notify Slack - Success
        if: success()
        uses: 8398a7/action-slack@v3
        with:
          status: custom
          custom_payload: |
            {
              "text": "✅ Staging Deployment Successful!",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Staging Deployment Successful!* ✅"
                  }
                },
                {
                  "type": "section",
                  "fields": [
                    {"type": "mrkdwn", "text": "*Version:*\n${{ needs.build.outputs.version }}"},
                    {"type": "mrkdwn", "text": "*Branch:*\ndevelop"},
                    {"type": "mrkdwn", "text": "*Deployed by:*\n${{ github.actor }}"},
                    {"type": "mrkdwn", "text": "*URL:*\n<https://staging.lk-trade.com|staging.lk-trade.com>"}
                  ]
                }
              ]
            }
          webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}

      - name: Notify Slack - Failure
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: custom
          custom_payload: |
            {
              "text": "❌ Staging Deployment Failed!",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Staging Deployment Failed!* ❌\n\nRollback initiated."
                  }
                },
                {
                  "type": "section",
                  "fields": [
                    {"type": "mrkdwn", "text": "*Version:*\n${{ needs.build.outputs.version }}"},
                    {"type": "mrkdwn", "text": "*Failed at:*\n${{ job.status }}"},
                    {"type": "mrkdwn", "text": "*Logs:*\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Logs>"}
                  ]
                }
              ]
            }
          webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

**실행 결과:**
```
✅ CD - Auto Deploy to Staging

Run Tests (2m 15s)
  ✓ Unit tests passed
  ✓ Integration tests passed

Build & Push Images (5m 30s)
  ✓ Generated version: develop-20251020-143022-a1b2c3d
  ✓ Built user-service
  ✓ Built trade-service
  ✓ Built account-service
  ✓ Built strategy-service

Deploy to Staging (1m 45s)
  ✓ Backup created
  ✓ Deployed successfully
  ✓ Health checks passed
  ✓ Smoke tests passed
  ✓ Slack notification sent

Total time: 9m 30s
```

**배운 점:**
1. **needs**로 Job 순서 제어 (테스트 → 빌드 → 배포)
2. **outputs**로 Job 간 데이터 전달
3. **environment**로 배포 환경 보호
4. **if: failure()**로 자동 롤백
5. **Health check**로 배포 검증
6. **Slack 알림**으로 팀 협업

**자동화된 워크플로우:**
```
Developer Push
      ↓
   Run Tests ────→ Failed? → Stop, notify
      ↓
   Build Images
      ↓
   Deploy to Staging
      ↓
   Health Check ──→ Failed? → Rollback, notify
      ↓
   Notify Success
```

---

## ❓ FAQ

<details>
<summary><strong>Q1: GitHub Actions vs Jenkins, 어떤 것을 선택해야 하나요?</strong></summary>

### 상세 답변

**GitHub Actions를 선택하는 경우:**
```
✅ 적합한 상황:
- GitHub 중심 개발 워크플로우
- 빠른 시작과 설정이 필요한 경우
- 소규모 팀 (5명 이하)
- 간단~중간 수준의 파이프라인
- 인프라 관리 부담을 줄이고 싶은 경우
- 오픈소스 프로젝트 (무료)

장점:
- 설정이 매우 간단 (.yml 파일만 추가)
- GitHub와 완벽한 통합
- 무료 tier 제공 (월 2000분)
- 서버 관리 불필요
- Marketplace의 다양한 액션

단점:
- 복잡한 커스터마이징 제한적
- 빌드 시간이 길면 비용 증가
- Self-hosted runner 설정이 Jenkins보다 복잡
```

**Jenkins를 선택하는 경우:**
```
✅ 적합한 상황:
- 복잡한 파이프라인 필요
- 기존 Jenkins 인프라가 있는 경우
- 높은 수준의 커스터마이징 필요
- 온프레미스 환경 필수
- 빌드가 매우 빈번한 경우 (비용 절감)
- 대규모 팀 (10명 이상)

장점:
- 무제한 빌드 (서버만 있으면 됨)
- 매우 높은 커스터마이징 가능
- 1800+ 플러그인
- 풍부한 UI와 대시보드
- 다양한 VCS 지원

단점:
- 초기 설정 복잡
- 서버 관리 필요
- 러닝 커브 높음
- 플러그인 충돌 가능성
```

**실제 비용 비교:**
```
시나리오: 하루 20회 빌드, 빌드당 10분

GitHub Actions:
- 월 빌드 시간: 20 × 10분 × 30일 = 6,000분
- 무료 tier: 2,000분
- 초과 시간: 4,000분
- 비용: 4,000분 × $0.008 = $32/월

Jenkins (Self-hosted):
- 서버 비용: $50/월 (고정)
- 빌드 횟수: 무제한
- 총 비용: $50/월

결론:
- 월 6,250분 이하: GitHub Actions 권장
- 월 6,250분 이상: Jenkins 권장
```

**Best Practice: 하이브리드 접근**
```yaml
# GitHub Actions로 간단한 검증
# .github/workflows/quick-check.yml
name: Quick Check
on: [pull_request]
jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./gradlew ktlintCheck test

# Jenkins로 복잡한 배포
# Jenkinsfile
pipeline {
    stages {
        stage('Full Build') { ... }
        stage('Security Scan') { ... }
        stage('Deploy') { ... }
    }
}
```

</details>

<details>
<summary><strong>Q2: Self-hosted Runner는 언제 사용하나요? 어떻게 설정하나요?</strong></summary>

### 상세 답변

**Self-hosted Runner가 필요한 경우:**
```
✅ 사용해야 하는 상황:
1. 빌드 시간이 매우 긴 경우 (30분+)
   → GitHub-hosted는 시간당 비용 발생

2. 특수 하드웨어 필요
   → GPU, 특정 CPU 아키텍처 (ARM 등)

3. 온프레미스 리소스 접근 필요
   → 내부 데이터베이스, 네트워크 제한

4. 높은 빌드 빈도
   → 하루 50회+ 빌드

5. 보안/규정 준수 요구사항
   → 데이터가 자체 인프라에만 있어야 함
```

**설정 방법:**

```bash
# 1. Ubuntu 서버 준비
ssh admin@build-server.company.com

# 2. 필수 패키지 설치
sudo apt-get update
sudo apt-get install -y curl git

# 3. Runner 다운로드
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# 4. Runner 등록
# GitHub: Repository > Settings > Actions > Runners > New self-hosted runner
# 표시된 토큰을 사용
./config.sh \
  --url https://github.com/your-org/lk-trade \
  --token YOUR_REGISTRATION_TOKEN \
  --name build-server-1 \
  --labels ubuntu-20.04,x64,gpu \
  --work _work

# 5. 서비스로 설치 (재부팅 시 자동 시작)
sudo ./svc.sh install
sudo ./svc.sh start

# 6. 상태 확인
sudo ./svc.sh status
```

**Docker로 Self-hosted Runner 실행:**

```yaml
# docker-compose.runner.yml
version: '3.8'

services:
  github-runner:
    image: myoung34/github-runner:latest
    container_name: github-runner
    environment:
      - REPO_URL=https://github.com/your-org/lk-trade
      - RUNNER_NAME=docker-runner
      - RUNNER_TOKEN=${RUNNER_TOKEN}
      - RUNNER_WORKDIR=/tmp/runner
      - LABELS=ubuntu-latest,docker
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - runner-data:/tmp/runner
    restart: unless-stopped

volumes:
  runner-data:
```

```bash
# 실행
export RUNNER_TOKEN=YOUR_TOKEN
docker-compose -f docker-compose.runner.yml up -d
```

**워크플로우에서 사용:**

```yaml
name: Build on Self-hosted Runner

on: [push]

jobs:
  build:
    runs-on: self-hosted  # Self-hosted runner 사용
    # 또는 특정 레이블 지정
    # runs-on: [self-hosted, ubuntu-20.04, gpu]

    steps:
      - uses: actions/checkout@v4

      - name: Build with GPU
        run: |
          nvidia-smi  # GPU 정보 확인
          ./gradlew build -Pgpu=true

      - name: Access internal database
        run: |
          # 내부 네트워크 접근 가능
          mysql -h internal-db.company.local -u user -p${{ secrets.DB_PASSWORD }}
```

**보안 Best Practices:**

```yaml
# 1. 공개 저장소에는 Self-hosted runner 사용 금지!
# GitHub-hosted runner만 사용

# 2. Private 저장소에서만 사용
# .github/workflows/secure-build.yml
name: Secure Build

on:
  push:
    branches: [main]

jobs:
  build:
    # 공개 저장소라면 이 Job은 실행 안 됨
    if: github.repository == 'your-org/lk-trade' && github.event.repository.private == true
    runs-on: self-hosted

    steps:
      - uses: actions/checkout@v4
      # ...

# 3. Runner 격리
# 각 조직/팀별로 별도의 runner 사용

# 4. 정기적인 보안 업데이트
# Cron job으로 자동 업데이트
```

**비용 비교:**

```
GitHub-hosted Runner:
- 무료 tier: 2,000분/월
- 초과 시: $0.008/분 (Linux)
- 예: 10,000분/월 = $64/월

Self-hosted Runner:
- 서버 비용: $50~200/월
- 빌드 시간: 무제한
- 전력, 관리 비용 추가

Break-even point: 월 8,000분
```

</details>

<details>
<summary><strong>Q3: GitHub Actions 비용을 최적화하려면 어떻게 해야 하나요?</strong></summary>

### 상세 답변

**비용 최적화 전략:**

**1. 캐싱 적극 활용**

```yaml
# ❌ 캐싱 없음 (느리고 비용 증가)
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - run: ./gradlew build  # 매번 의존성 다운로드!

# ✅ 캐싱 있음 (빠르고 비용 절감)
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'gradle'  # Gradle 캐시 활성화

      # 추가 캐싱
      - uses: actions/cache@v3
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
          restore-keys: |
            ${{ runner.os }}-gradle-

      - run: ./gradlew build

# 결과:
# - 의존성 다운로드: 5분 → 10초
# - 총 빌드 시간: 10분 → 3분
# - 비용 절감: 70%
```

**2. 불필요한 워크플로우 실행 방지**

```yaml
# ❌ 모든 파일 변경 시 실행
on: [push]

# ✅ 필요한 경우에만 실행
on:
  push:
    branches: [main, develop]
    paths:
      - 'src/**'
      - 'build.gradle.kts'
      - '.github/workflows/**'
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - '.gitignore'

# 예: README.md 수정 시 빌드 안 함 → 비용 절감
```

**3. Job 병렬화로 시간 단축**

```yaml
# ❌ 순차 실행 (느림)
jobs:
  test-user:
    runs-on: ubuntu-latest
    steps:
      - run: ./gradlew :user:test

  test-trade:
    needs: [test-user]  # 대기 시간 낭비!
    runs-on: ubuntu-latest
    steps:
      - run: ./gradlew :trade:test

# ✅ 병렬 실행 (빠름)
jobs:
  test:
    strategy:
      matrix:
        module: [user, trade, account, strategy]
    runs-on: ubuntu-latest
    steps:
      - run: ./gradlew :${{ matrix.module }}:test

# 결과:
# - 순차: 20분 (5분 × 4)
# - 병렬: 5분
# - 시간 절감: 75%
```

**4. Docker 레이어 캐싱**

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build with cache
        uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          cache-from: type=gha  # GitHub Actions 캐시 사용
          cache-to: type=gha,mode=max
          tags: myapp:latest

# 결과:
# - 첫 빌드: 10분
# - 이후 빌드: 2분 (캐시 히트)
# - 비용 절감: 80%
```

**5. 조건부 Job 실행**

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./gradlew test

  # 배포는 main 브랜치에만
  deploy:
    needs: [test]
    if: github.ref == 'refs/heads/main'  # main 브랜치에만 실행
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh

# PR에서는 deploy Job 건너뜀 → 비용 절감
```

**6. Self-hosted Runner로 전환 (대규모 프로젝트)**

```yaml
jobs:
  # 빠른 검증은 GitHub-hosted
  quick-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./gradlew ktlintCheck

  # 긴 빌드는 Self-hosted
  full-build:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - run: ./gradlew build integrationTest

# 비용:
# - quick-check: 1분 × $0.008 = $0.008
# - full-build: 30분 × $0 (self-hosted) = $0
```

**7. 스케줄된 워크플로우 최적화**

```yaml
# ❌ 비용 낭비
on:
  schedule:
    - cron: '*/5 * * * *'  # 5분마다 실행 (너무 빈번!)

# ✅ 적절한 빈도
on:
  schedule:
    - cron: '0 2 * * *'  # 하루 1번, 새벽 2시
  workflow_dispatch:  # 필요 시 수동 실행
```

**비용 최적화 요약:**

```
최적화 전:
- 하루 20회 빌드
- 빌드당 15분
- 월 총 시간: 20 × 15 × 30 = 9,000분
- 무료 tier: 2,000분
- 초과 시간: 7,000분
- 비용: 7,000 × $0.008 = $56/월

최적화 후:
- 하루 15회 빌드 (불필요한 실행 제거)
- 빌드당 5분 (캐싱, 병렬화)
- 월 총 시간: 15 × 5 × 30 = 2,250분
- 무료 tier: 2,000분
- 초과 시간: 250분
- 비용: 250 × $0.008 = $2/월

절감액: $54/월 (96% 절감!)
```

**Best Practices 체크리스트:**

```
✅ Gradle/Maven 캐시 활성화
✅ Docker 빌드 캐시 사용
✅ paths-ignore로 불필요한 실행 방지
✅ Matrix strategy로 병렬 실행
✅ 조건부 Job 실행 (if:)
✅ Self-hosted runner 고려 (빌드 빈번한 경우)
✅ 스케줄 워크플로우 최적화
✅ Artifacts 정리 (오래된 것 삭제)
❌ 모든 push/PR에 긴 워크플로우 실행
❌ 캐싱 없이 의존성 매번 다운로드
❌ 불필요한 스텝 실행
```

</details>

<details>
<summary><strong>Q4: GitHub Actions에서 캐싱을 효과적으로 사용하는 방법은?</strong></summary>

### 상세 답변

**캐싱 전략:**

**1. Gradle 캐싱 (자동)**

```yaml
# 방법 1: setup-java 내장 캐싱 (가장 간단!)
- uses: actions/setup-java@v4
  with:
    java-version: '17'
    distribution: 'temurin'
    cache: 'gradle'  # 자동으로 ~/.gradle 캐싱

# 결과:
# - 첫 실행: 의존성 다운로드 5분
# - 이후 실행: 캐시 복원 10초
```

**2. Gradle 캐싱 (수동, 더 세밀한 제어)**

```yaml
- uses: actions/cache@v3
  with:
    path: |
      ~/.gradle/caches
      ~/.gradle/wrapper
      .gradle/
    key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
    restore-keys: |
      ${{ runner.os }}-gradle-

# key 설명:
# - runner.os: 운영체제별로 캐시 분리
# - hashFiles(): 파일 내용 기반 키 생성
#   → build.gradle.kts 변경 시 새 캐시 생성
# - restore-keys: 완전 일치 없을 때 fallback
```

**3. Docker 레이어 캐싱**

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: myapp:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max

# mode=max: 모든 레이어 캐싱 (권장)
# mode=min: 최종 이미지만 캐싱

# 결과:
# - 첫 빌드: 10분
# - 이후 빌드 (변경 없음): 30초
# - 이후 빌드 (소스만 변경): 2분
```

**4. npm/yarn 캐싱**

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'  # 또는 'yarn', 'pnpm'

# 수동:
- uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

**5. 커스텀 캐싱 (빌드 산출물)**

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # 빌드 산출물 캐싱
      - uses: actions/cache@v3
        id: build-cache
        with:
          path: build/libs
          key: build-${{ github.sha }}  # 커밋별로 캐시

      - name: Build
        if: steps.build-cache.outputs.cache-hit != 'true'
        run: ./gradlew build

      - name: Use cached build
        if: steps.build-cache.outputs.cache-hit == 'true'
        run: echo "Using cached build!"

  test:
    needs: [build]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # 같은 빌드 산출물 재사용
      - uses: actions/cache@v3
        with:
          path: build/libs
          key: build-${{ github.sha }}

      - run: ./test.sh build/libs/app.jar
```

**6. 다중 캐시 사용**

```yaml
- name: Cache multiple paths
  uses: actions/cache@v3
  with:
    path: |
      ~/.gradle/caches
      ~/.gradle/wrapper
      ~/.m2/repository
      node_modules
      .next/cache
    key: ${{ runner.os }}-multi-${{ hashFiles('**/*.gradle*', '**/pom.xml', '**/package-lock.json') }}
```

**7. 캐시 무효화 전략**

```yaml
# 캐시 키에 버전 추가
- uses: actions/cache@v3
  with:
    path: ~/.gradle
    key: v2-${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*') }}
    #    ^^^ 버전 변경 시 새 캐시

# 매일 새로운 캐시 생성
- uses: actions/cache@v3
  with:
    path: ~/.gradle
    key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*') }}-${{ github.run_number }}
    restore-keys: |
      ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*') }}-
      ${{ runner.os }}-gradle-
```

**캐싱 Best Practices:**

```yaml
name: Optimized Build with Caching

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # 1. Java/Gradle 캐싱 (자동)
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'gradle'

      # 2. Docker Buildx 설정
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      # 3. Gradle 빌드 (캐시 활용)
      - name: Build with Gradle
        run: |
          ./gradlew build \
            --build-cache \
            --configuration-cache

      # 4. Docker 빌드 (레이어 캐싱)
      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          cache-from: type=gha
          cache-to: type=gha,mode=max
          tags: myapp:latest

      # 5. 테스트 결과 캐싱 (선택적)
      - uses: actions/cache@v3
        with:
          path: build/test-results
          key: test-results-${{ github.sha }}

# 결과:
# - 첫 실행: 15분
# - 이후 실행 (캐시 히트): 3분
# - 시간 절감: 80%
```

**캐시 크기 제한:**

```
GitHub Actions 캐시 제한:
- 리포지토리당: 10GB
- 캐시 보관: 7일 (사용되지 않으면 삭제)
- 개별 캐시: 10GB

주의:
- 너무 큰 캐시는 복원 시간 증가
- 불필요한 파일은 제외
```

**캐싱 디버깅:**

```yaml
- name: Debug cache
  run: |
    echo "Cache key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*') }}"
    du -sh ~/.gradle
    ls -la ~/.gradle/caches

- uses: actions/cache@v3
  with:
    path: ~/.gradle
    key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*') }}
    restore-keys: |
      ${{ runner.os }}-gradle-

- name: Check cache hit
  run: |
    if [ "${{ steps.cache.outputs.cache-hit }}" == "true" ]; then
      echo "✅ Cache hit!"
    else
      echo "❌ Cache miss"
    fi
```

</details>

<details>
<summary><strong>Q5: GitHub Actions 보안 Best Practices는 무엇인가요?</strong></summary>

### 상세 답변

**보안 Best Practices:**

**1. Secrets 관리**

```yaml
# ❌ 절대 하지 말 것!
- name: Deploy
  run: |
    export API_KEY="sk-1234567890"  # 하드코딩 금지!
    export PASSWORD="admin123"       # 로그에 노출됨!

# ✅ 올바른 방법
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
    PASSWORD: ${{ secrets.DB_PASSWORD }}
  run: |
    ./deploy.sh

# Secrets는 자동으로 마스킹됨:
# 로그: "Using API key: ***"
```

**2. 최소 권한 원칙**

```yaml
# GitHub Token 권한 제한
permissions:
  contents: read        # 코드 읽기만
  pull-requests: write  # PR 코멘트
  packages: write       # Docker 이미지 푸시
  # issues: write       # 불필요하면 제외

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: ./gradlew build
```

**3. 공개 저장소에서 Self-hosted Runner 사용 금지**

```yaml
# ❌ 위험! 공개 저장소에서 Self-hosted runner
jobs:
  build:
    runs-on: self-hosted  # 누구나 악의적 PR로 코드 실행 가능!

# ✅ 안전: 공개 저장소는 GitHub-hosted만
jobs:
  build:
    runs-on: ubuntu-latest

# ✅ Private 저장소에서만 Self-hosted
jobs:
  build:
    if: github.event.repository.private == true
    runs-on: self-hosted
```

**4. Pull Request 보호**

```yaml
# ❌ 위험: Fork에서 온 PR에 Secrets 노출
on: [pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo ${{ secrets.API_KEY }}  # Fork PR에서 접근 가능!

# ✅ 안전: pull_request_target + 승인 필요
on:
  pull_request_target:  # Fork PR은 기본적으로 Secrets 접근 불가

jobs:
  test:
    runs-on: ubuntu-latest
    environment: production  # 수동 승인 필요
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}  # PR 브랜치 체크아웃
      - run: ./test.sh
```

**5. 써드파티 액션 검증**

```yaml
# ❌ 위험: 최신 버전 자동 사용
- uses: some-org/some-action@main  # main 브랜치가 변경될 수 있음!

# ✅ 안전: 특정 버전 고정
- uses: actions/checkout@v4  # 메이저 버전 고정
- uses: actions/setup-java@8df82afff59ac2b6
  # 또는 커밋 SHA로 고정 (가장 안전)

# ✅ 신뢰할 수 있는 액션만 사용
# - GitHub 공식: actions/*
# - 검증된 조직: docker/*, aws-actions/*
```

**6. 코드 인젝션 방지**

```yaml
# ❌ 위험: 사용자 입력을 직접 사용
on:
  pull_request:
    types: [opened]

jobs:
  comment:
    runs-on: ubuntu-latest
    steps:
      - name: Comment
        run: |
          echo "PR Title: ${{ github.event.pull_request.title }}"
          # 악의적 PR 제목: "; rm -rf / #"
          # 실행됨: echo "PR Title: "; rm -rf / #"

# ✅ 안전: 환경 변수 사용
jobs:
  comment:
    runs-on: ubuntu-latest
    steps:
      - name: Comment
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: |
          echo "PR Title: $PR_TITLE"
          # 환경 변수는 안전하게 이스케이프됨
```

**7. 보안 스캔 통합**

```yaml
jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # 1. 의존성 취약점 스캔
      - name: Dependency Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: 'LK-Trade'
          path: '.'
          format: 'HTML'

      # 2. 코드 보안 스캔
      - name: Run CodeQL
        uses: github/codeql-action/analyze@v2

      # 3. Docker 이미지 스캔
      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:latest'
          severity: 'HIGH,CRITICAL'
          exit-code: '1'  # 취약점 발견 시 실패

      # 4. Secrets 노출 검사
      - name: Gitleaks
        uses: gitleaks/gitleaks-action@v2
```

**8. Environment 보호 규칙**

```yaml
# Production 환경 보호
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: production
      # GitHub Settings에서 설정:
      # - Required reviewers: admin, devops팀
      # - Wait timer: 5분 (실수 방지)
      # - Deployment branches: main만
    steps:
      - name: Deploy to production
        run: ./deploy.sh
```

**Settings > Environments > production 설정:**
```
✅ Required reviewers
   - admin
   - devops-team

✅ Wait timer: 5 minutes

✅ Deployment branches
   - main
   - release/*

✅ Environment secrets
   - PROD_API_KEY
   - PROD_DB_PASSWORD
```

**9. Secrets 교체 전략**

```bash
# 정기적인 Secrets 교체 (90일마다)

# 1. 새 키 생성
ssh-keygen -t ed25519 -f ~/.ssh/new-deploy-key

# 2. 서버에 새 키 추가
ssh-copy-id -i ~/.ssh/new-deploy-key.pub deploy@server.com

# 3. GitHub Secrets 업데이트
# Settings > Secrets > DEPLOY_SSH_KEY 수정

# 4. 워크플로우 테스트

# 5. 이전 키 제거 (1주일 후)
ssh deploy@server.com
nano ~/.ssh/authorized_keys
# 이전 키 삭제
```

**10. 감사 로그 활성화**

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Log deployment
        run: |
          echo "Deployment started by ${{ github.actor }}"
          echo "Commit: ${{ github.sha }}"
          echo "Timestamp: $(date -u)"
          echo "Branch: ${{ github.ref_name }}"

      - name: Deploy
        run: ./deploy.sh

      - name: Notify audit log
        if: always()
        run: |
          curl -X POST ${{ secrets.AUDIT_WEBHOOK }} \
            -H "Content-Type: application/json" \
            -d '{
              "actor": "${{ github.actor }}",
              "action": "deploy",
              "status": "${{ job.status }}",
              "timestamp": "'$(date -u)'"
            }'
```

**보안 체크리스트:**

```
✅ Secrets는 GitHub Secrets에 저장
✅ 최소 권한 원칙 (permissions:)
✅ 공개 저장소에 Self-hosted runner 사용 안 함
✅ pull_request_target 주의
✅ 써드파티 액션 버전 고정
✅ 코드 인젝션 방지 (환경 변수 사용)
✅ 보안 스캔 통합 (Trivy, CodeQL)
✅ Production 환경 보호 규칙
✅ Secrets 정기 교체 (90일)
✅ 감사 로그 기록
❌ 하드코딩된 Secrets
❌ 검증되지 않은 액션 사용
❌ Secrets를 로그에 출력
❌ Fork PR에 Secrets 노출
```

</details>

---

## 📝 면접 질문

### 주니어 레벨

<details>
<summary><strong>Q1: GitHub Actions 워크플로우의 기본 구조를 설명하고, 간단한 CI 파이프라인을 작성해보세요.</strong></summary>

### 답변

**기본 구조 설명:**

GitHub Actions 워크플로우는 **name, on, jobs** 세 가지 핵심 요소로 구성됩니다.

```yaml
name: 워크플로우 이름

on: 트리거 (언제 실행할지)

jobs:
  job-name:
    runs-on: 실행 환경
    steps:
      - 실행할 작업들
```

**구체적인 예시:**

```yaml
name: CI Pipeline

# 1. Trigger: 언제 실행할지
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

# 2. Jobs: 실행할 작업들
jobs:
  # Job 1: 코드 품질 검사
  lint:
    name: Code Quality
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Run Ktlint
        run: ./gradlew ktlintCheck

  # Job 2: 테스트
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    needs: [lint]  # lint Job이 성공한 후 실행
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'gradle'

      - name: Run unit tests
        run: ./gradlew test

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: build/test-results/

  # Job 3: 빌드
  build:
    name: Build Application
    runs-on: ubuntu-latest
    needs: [test]
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'gradle'

      - name: Build JAR
        run: ./gradlew build

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: application-jar
          path: build/libs/*.jar
```

**실행 흐름:**
```
Push/PR 발생
    ↓
lint Job 실행 (코드 품질 검사)
    ↓ (성공 시)
test Job 실행 (테스트)
    ↓ (성공 시)
build Job 실행 (빌드)
    ↓
완료
```

**핵심 개념:**

1. **uses vs run**
   - `uses`: 기존에 만들어진 액션 사용
   - `run`: 셸 명령 직접 실행

2. **needs**
   - Job 간 의존성 정의
   - 순차 실행 보장

3. **if**
   - 조건부 실행
   - `always()`, `success()`, `failure()` 등

4. **artifacts**
   - Job 간 파일 공유
   - 빌드 산출물 저장

</details>

<details>
<summary><strong>Q2: GitHub Actions Secrets를 사용하여 민감한 정보를 안전하게 관리하는 방법을 설명하세요.</strong></summary>

### 답변

**Secrets 개념:**

GitHub Secrets는 API 키, 비밀번호, SSH 키 등 민감한 정보를 안전하게 저장하고 워크플로우에서 사용할 수 있게 해주는 기능입니다.

**설정 방법:**

```
1. GitHub Repository 페이지
2. Settings > Secrets and variables > Actions
3. "New repository secret" 클릭
4. Name과 Secret 입력
5. "Add secret" 클릭
```

**사용 예시:**

```yaml
name: Deploy Application

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # 1. 환경 변수로 사용
      - name: Deploy with API key
        env:
          API_KEY: ${{ secrets.API_KEY }}
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
        run: |
          echo "Deploying with API key..."
          ./deploy.sh

      # 2. SSH 키 사용
      - name: Configure SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.HOST }} >> ~/.ssh/known_hosts

      - name: Deploy via SSH
        run: |
          ssh ${{ secrets.USER }}@${{ secrets.HOST }} "cd /app && ./deploy.sh"

      # 3. Docker Registry 로그인
      - name: Log in to Docker Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}  # 자동 제공됨
```

**로그에서의 보안:**

```yaml
- name: Test secret masking
  env:
    MY_SECRET: ${{ secrets.API_KEY }}
  run: |
    echo "Secret value: $MY_SECRET"
    # 로그 출력: "Secret value: ***"
    # 자동으로 마스킹됨!
```

**실제 로그:**
```
Run echo "Secret value: $MY_SECRET"
Secret value: ***
```

**보안 Best Practices:**

```yaml
# 1. Environment별 Secrets 분리
jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging  # staging 환경의 Secrets 사용
    steps:
      - run: ./deploy.sh
        env:
          API_KEY: ${{ secrets.API_KEY }}  # staging API_KEY

  deploy-production:
    runs-on: ubuntu-latest
    environment: production  # production 환경의 Secrets
    steps:
      - run: ./deploy.sh
        env:
          API_KEY: ${{ secrets.API_KEY }}  # production API_KEY
```

```yaml
# 2. Secrets 절대 출력하지 않기
- name: Wrong - exposes secret
  run: echo "My secret is ${{ secrets.API_KEY }}"  # ❌ 위험!

- name: Correct - use without printing
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: ./script.sh  # ✅ 안전
```

```yaml
# 3. 최소 권한 원칙
permissions:
  contents: read
  packages: write
# 필요한 권한만 부여
```

**Secret 종류:**

1. **Repository secrets**: 해당 저장소에서만 사용
2. **Organization secrets**: 조직 전체 저장소에서 사용
3. **Environment secrets**: 특정 환경(staging, production)에서만 사용

**자동 제공되는 Secrets:**

```yaml
- name: Use GitHub Token
  run: |
    # GITHUB_TOKEN은 자동으로 제공됨
    echo "Token: ${{ secrets.GITHUB_TOKEN }}"
    # 용도: Git 작업, Packages 푸시, API 호출 등
```

**정리:**
```
✅ Secrets로 민감 정보 관리
✅ 로그에 자동 마스킹 (***)
✅ Environment별로 분리
✅ 최소 권한 원칙
❌ 절대 하드코딩 금지
❌ Secrets를 로그에 출력 금지
```

</details>

---

### 중급 레벨

<details>
<summary><strong>Q3: Matrix Strategy를 사용하여 여러 환경에서 동시에 테스트하는 방법을 설명하고 구현하세요.</strong></summary>

### 답변

**Matrix Strategy란?**

하나의 Job을 여러 다른 설정(OS, 버전, 환경 등)으로 동시에 실행하는 기능입니다. 병렬 실행으로 시간을 크게 단축할 수 있습니다.

**기본 예시:**

```yaml
name: Multi-Environment Tests

on: [push, pull_request]

jobs:
  test:
    name: Test on ${{ matrix.os }} with Java ${{ matrix.java }}
    runs-on: ${{ matrix.os }}

    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        java: ['11', '17', '21']
        # 총 9개 Job 생성: 3 OS × 3 Java 버전

    steps:
      - uses: actions/checkout@v4

      - name: Setup Java ${{ matrix.java }}
        uses: actions/setup-java@v4
        with:
          java-version: ${{ matrix.java }}
          distribution: 'temurin'

      - name: Run tests
        run: ./gradlew test

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.os }}-${{ matrix.java }}
          path: build/test-results/
```

**실행 결과:**
```
9개 Job 병렬 실행:
├── ubuntu-latest + Java 11
├── ubuntu-latest + Java 17
├── ubuntu-latest + Java 21
├── windows-latest + Java 11
├── windows-latest + Java 17
├── windows-latest + Java 21
├── macos-latest + Java 11
├── macos-latest + Java 17
└── macos-latest + Java 21

순차 실행 시간: 9 × 5분 = 45분
병렬 실행 시간: 5분 (모두 동시 실행)
```

**고급 사용 - exclude와 include:**

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        java: ['11', '17', '21']

        # 특정 조합 제외
        exclude:
          - os: macos-latest
            java: '11'  # macOS + Java 11 조합 제외
          - os: windows-latest
            java: '21'  # Windows + Java 21 조합 제외

        # 추가 조합
        include:
          - os: ubuntu-latest
            java: '17'
            experimental: true  # 추가 변수
          - os: ubuntu-20.04  # 특정 버전 추가
            java: '11'

    runs-on: ${{ matrix.os }}
    continue-on-error: ${{ matrix.experimental == true }}

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: ${{ matrix.java }}
          distribution: 'temurin'
      - run: ./gradlew test
```

**실전 예시 - 마이크로서비스 테스트:**

```yaml
name: Test All Services

on: [push]

jobs:
  test-services:
    name: Test ${{ matrix.service }}
    runs-on: ubuntu-latest

    strategy:
      # fail-fast: false면 하나 실패해도 나머지 계속 실행
      fail-fast: false
      matrix:
        service:
          - user-service
          - trade-service
          - account-service
          - strategy-service
        node-version: ['18', '20']

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}

      - name: Test ${{ matrix.service }}
        run: |
          cd services/${{ matrix.service }}
          npm install
          npm test

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.service }}-node${{ matrix.node-version }}
          path: services/${{ matrix.service }}/coverage/
```

**복잡한 Matrix - 데이터베이스 조합:**

```yaml
jobs:
  integration-test:
    strategy:
      matrix:
        include:
          - db: postgres
            db_version: '14'
            db_image: postgres:14-alpine
          - db: postgres
            db_version: '15'
            db_image: postgres:15-alpine
          - db: postgres
            db_version: '16'
            db_image: postgres:16-alpine
          - db: mysql
            db_version: '8.0'
            db_image: mysql:8.0
          - db: mysql
            db_version: '8.2'
            db_image: mysql:8.2

    runs-on: ubuntu-latest

    services:
      database:
        image: ${{ matrix.db_image }}
        env:
          POSTGRES_PASSWORD: test
          MYSQL_ROOT_PASSWORD: test
        options: >-
          --health-cmd="${{ matrix.db == 'postgres' && 'pg_isready' || 'mysqladmin ping' }}"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5

    steps:
      - uses: actions/checkout@v4

      - name: Run integration tests with ${{ matrix.db }} ${{ matrix.db_version }}
        env:
          DB_TYPE: ${{ matrix.db }}
          DB_VERSION: ${{ matrix.db_version }}
        run: ./gradlew integrationTest
```

**Matrix 최적화:**

```yaml
jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        arch: [x64, arm64]

      # 최대 동시 실행 수 제한 (리소스 절약)
      max-parallel: 4

    runs-on: ${{ matrix.os }}

    steps:
      - name: Build for ${{ matrix.os }}-${{ matrix.arch }}
        run: ./build.sh --arch ${{ matrix.arch }}
```

**동적 Matrix (고급):**

```yaml
jobs:
  # 1단계: Matrix 값 생성
  generate-matrix:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4

      - name: Generate matrix
        id: set-matrix
        run: |
          # services 디렉토리에서 서비스 목록 자동 생성
          SERVICES=$(ls -d services/*/ | xargs -n 1 basename | jq -R -s -c 'split("\n")[:-1]')
          echo "matrix={\"service\":$SERVICES}" >> $GITHUB_OUTPUT

  # 2단계: 생성된 Matrix로 테스트
  test:
    needs: [generate-matrix]
    strategy:
      matrix: ${{ fromJson(needs.generate-matrix.outputs.matrix) }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Test ${{ matrix.service }}
        run: cd services/${{ matrix.service }} && npm test
```

**핵심 포인트:**

1. **병렬 실행**: 시간 단축 (45분 → 5분)
2. **fail-fast**: 하나 실패 시 나머지 중단 여부
3. **exclude/include**: 조합 제어
4. **continue-on-error**: 실험적 빌드 허용
5. **max-parallel**: 리소스 관리

</details>

<details>
<summary><strong>Q4: Reusable Workflow를 만들어 코드 중복을 줄이는 방법을 설명하고 구현하세요.</strong></summary>

### 답변

**Reusable Workflow란?**

여러 워크플로우에서 공통으로 사용되는 로직을 하나의 워크플로우로 만들어 재사용하는 기능입니다. DRY(Don't Repeat Yourself) 원칙을 적용한 것입니다.

**기본 구조:**

**1. Reusable Workflow 정의 (.github/workflows/reusable-build.yml):**

```yaml
name: Reusable Build Workflow

on:
  workflow_call:  # 다른 워크플로우에서 호출 가능
    inputs:
      service-name:
        description: 'Name of the service to build'
        required: true
        type: string
      java-version:
        description: 'Java version to use'
        required: false
        type: string
        default: '17'
      run-tests:
        description: 'Whether to run tests'
        required: false
        type: boolean
        default: true

    secrets:
      registry-username:
        description: 'Docker registry username'
        required: true
      registry-password:
        description: 'Docker registry password'
        required: true

    outputs:
      image-tag:
        description: 'Built Docker image tag'
        value: ${{ jobs.build.outputs.tag }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.meta.outputs.tags }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          java-version: ${{ inputs.java-version }}
          distribution: 'temurin'
          cache: 'gradle'

      - name: Run tests
        if: ${{ inputs.run-tests }}
        run: ./gradlew :${{ inputs.service-name }}:test

      - name: Build
        run: ./gradlew :${{ inputs.service-name }}:build

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Docker Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ secrets.registry-username }}
          password: ${{ secrets.registry-password }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository_owner }}/${{ inputs.service-name }}
          tags: |
            type=ref,event=branch
            type=sha

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: ./modules/${{ inputs.service-name }}
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**2. Reusable Workflow 호출 (.github/workflows/build-all-services.yml):**

```yaml
name: Build All Services

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # 서비스별로 Reusable Workflow 호출
  build-user-service:
    uses: ./.github/workflows/reusable-build.yml
    with:
      service-name: user-service
      java-version: '17'
      run-tests: true
    secrets:
      registry-username: ${{ github.actor }}
      registry-password: ${{ secrets.GITHUB_TOKEN }}

  build-trade-service:
    uses: ./.github/workflows/reusable-build.yml
    with:
      service-name: trade-service
      java-version: '17'
      run-tests: true
    secrets:
      registry-username: ${{ github.actor }}
      registry-password: ${{ secrets.GITHUB_TOKEN }}

  build-account-service:
    uses: ./.github/workflows/reusable-build.yml
    with:
      service-name: account-service
      java-version: '17'
      run-tests: true
    secrets:
      registry-username: ${{ github.actor }}
      registry-password: ${{ secrets.GITHUB_TOKEN }}

  build-strategy-service:
    uses: ./.github/workflows/reusable-build.yml
    with:
      service-name: strategy-service
      java-version: '17'
      run-tests: true
    secrets:
      registry-username: ${{ github.actor }}
      registry-password: ${{ secrets.GITHUB_TOKEN }}

  # Output 사용
  deploy:
    needs: [build-user-service, build-trade-service]
    runs-on: ubuntu-latest
    steps:
      - name: Deploy services
        run: |
          echo "Deploying user-service: ${{ needs.build-user-service.outputs.image-tag }}"
          echo "Deploying trade-service: ${{ needs.build-trade-service.outputs.image-tag }}"
```

**고급 예시 - 배포 Reusable Workflow:**

**1. Reusable Deploy Workflow (.github/workflows/reusable-deploy.yml):**

```yaml
name: Reusable Deploy Workflow

on:
  workflow_call:
    inputs:
      environment:
        description: 'Deployment environment (staging/production)'
        required: true
        type: string
      version:
        description: 'Version to deploy'
        required: true
        type: string
      service:
        description: 'Service name'
        required: true
        type: string

    secrets:
      ssh-key:
        required: true
      host:
        required: true
      user:
        required: true
      slack-webhook:
        required: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: ${{ inputs.environment }}
      url: https://${{ inputs.environment == 'production' && '' || 'staging.' }}lk-trade.com

    steps:
      - uses: actions/checkout@v4

      - name: Configure SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.ssh-key }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.host }} >> ~/.ssh/known_hosts

      - name: Deploy ${{ inputs.service }}
        run: |
          ssh ${{ secrets.user }}@${{ secrets.host }} << ENDSSH
            cd /opt/lk-trade
            export SERVICE=${{ inputs.service }}
            export VERSION=${{ inputs.version }}
            docker-compose pull \$SERVICE
            docker-compose up -d \$SERVICE
          ENDSSH

      - name: Health check
        run: |
          sleep 30
          curl -f https://${{ inputs.environment == 'production' && '' || 'staging.' }}lk-trade.com/api/${{ inputs.service }}/health

      - name: Notify Slack
        if: always() && secrets.slack-webhook != ''
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: |
            Deployment ${{ job.status }}
            Service: ${{ inputs.service }}
            Environment: ${{ inputs.environment }}
            Version: ${{ inputs.version }}
          webhook_url: ${{ secrets.slack-webhook }}
```

**2. 호출 (.github/workflows/deploy-production.yml):**

```yaml
name: Deploy to Production

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to deploy'
        required: true

jobs:
  deploy-all-services:
    strategy:
      matrix:
        service: [user-service, trade-service, account-service, strategy-service]
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: production
      version: ${{ inputs.version }}
      service: ${{ matrix.service }}
    secrets:
      ssh-key: ${{ secrets.PROD_SSH_KEY }}
      host: ${{ secrets.PROD_HOST }}
      user: ${{ secrets.PROD_USER }}
      slack-webhook: ${{ secrets.SLACK_WEBHOOK_URL }}
```

**실전 활용 - 테스트 Reusable Workflow:**

```yaml
# .github/workflows/reusable-test.yml
name: Reusable Test Workflow

on:
  workflow_call:
    inputs:
      module:
        required: true
        type: string
      coverage-threshold:
        required: false
        type: number
        default: 80

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'gradle'

      - name: Run tests
        run: ./gradlew :modules:${{ inputs.module }}:test

      - name: Generate coverage report
        run: ./gradlew :modules:${{ inputs.module }}:jacocoTestReport

      - name: Check coverage threshold
        run: |
          COVERAGE=$(grep -oP 'Total.*?(\d+)%' build/reports/jacoco/test/html/index.html | grep -oP '\d+')
          if [ $COVERAGE -lt ${{ inputs.coverage-threshold }} ]; then
            echo "Coverage $COVERAGE% is below threshold ${{ inputs.coverage-threshold }}%"
            exit 1
          fi
          echo "Coverage: $COVERAGE%"

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ inputs.module }}
          path: modules/${{ inputs.module }}/build/test-results/
```

**호출:**

```yaml
# .github/workflows/test-all.yml
name: Test All Modules

on: [push, pull_request]

jobs:
  test-user:
    uses: ./.github/workflows/reusable-test.yml
    with:
      module: user
      coverage-threshold: 85

  test-trade:
    uses: ./.github/workflows/reusable-test.yml
    with:
      module: trade
      coverage-threshold: 80
```

**장점:**

1. **코드 중복 제거**: 공통 로직을 한 곳에서 관리
2. **일관성**: 모든 서비스가 동일한 방식으로 빌드/배포
3. **유지보수성**: 수정 사항을 한 곳에서만 변경
4. **테스트 용이성**: Reusable workflow를 독립적으로 테스트 가능

**주의사항:**

```yaml
# ❌ 같은 저장소 내 Reusable workflow는 상대 경로 사용
uses: ./.github/workflows/reusable-build.yml

# ✅ 다른 저장소의 Reusable workflow는 전체 경로 사용
uses: your-org/shared-workflows/.github/workflows/build.yml@main
```

</details>

<details>
<summary><strong>Q5: GitHub Actions에서 보안을 강화하는 방법과 Best Practices를 설명하세요.</strong></summary>

### 답변

**GitHub Actions 보안 강화 전략:**

**1. Secrets 관리**

```yaml
# ❌ 잘못된 방법
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: |
          export API_KEY="sk-1234567890"  # 하드코딩 금지!
          curl -H "Authorization: Bearer sk-1234567890" api.example.com

# ✅ 올바른 방법
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        env:
          API_KEY: ${{ secrets.API_KEY }}
        run: |
          curl -H "Authorization: Bearer $API_KEY" api.example.com
          # 로그: Authorization: Bearer ***
```

**2. 최소 권한 원칙 (GITHUB_TOKEN)**

```yaml
# ✅ 기본 권한 제한
permissions:
  contents: read        # 코드 읽기만
  pull-requests: write  # PR 코멘트 작성
  packages: write       # Docker 이미지 푸시

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build and push
        run: |
          docker build -t myapp .
          docker push ghcr.io/myapp

# Job별 권한 세분화
jobs:
  test:
    permissions:
      contents: read  # 테스트는 읽기만
    steps:
      - run: ./gradlew test

  deploy:
    permissions:
      contents: read
      packages: write  # 배포는 패키지 쓰기 필요
    steps:
      - run: docker push ghcr.io/myapp
```

**3. 공개 저장소에서 Self-hosted Runner 사용 금지**

```yaml
# ❌ 위험: 공개 저장소 + Self-hosted runner
# 누구나 악의적 PR로 runner에서 코드 실행 가능!
jobs:
  build:
    runs-on: self-hosted

# ✅ 안전: Private 저장소에서만 Self-hosted runner
jobs:
  build:
    if: github.event.repository.private == true
    runs-on: self-hosted

  build-public:
    if: github.event.repository.private != true
    runs-on: ubuntu-latest
```

**4. Pull Request 보호**

```yaml
# ❌ 위험: Fork PR에 Secrets 노출
on: pull_request

jobs:
  test:
    steps:
      - uses: actions/checkout@v4
      - run: echo ${{ secrets.API_KEY }}  # Fork PR에서 접근 가능!

# ✅ 안전: pull_request_target + Environment 보호
on:
  pull_request_target:  # Fork PR은 기본적으로 Secrets 접근 불가

jobs:
  test-trusted:
    # 신뢰할 수 있는 PR만 (maintainer, 조직 멤버)
    if: |
      github.event.pull_request.head.repo.full_name == github.repository ||
      contains(fromJson('["MEMBER", "OWNER"]'), github.event.pull_request.author_association)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - run: ./test.sh

  test-untrusted:
    # 외부 기여자는 Secrets 없이 테스트
    if: |
      github.event.pull_request.head.repo.full_name != github.repository &&
      !contains(fromJson('["MEMBER", "OWNER"]'), github.event.pull_request.author_association)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - run: ./test.sh  # Secrets 없이 실행
```

**5. 써드파티 액션 보안**

```yaml
# ❌ 위험: 최신 버전 자동 사용
- uses: some-org/some-action@main  # main 브랜치가 악의적으로 변경될 수 있음

# ✅ 안전: 특정 버전 고정
- uses: actions/checkout@v4  # 메이저 버전 고정

# ✅ 가장 안전: 커밋 SHA로 고정
- uses: actions/checkout@8df82afff59ac2b6d4b45922f47b7e9f2c4f5e1a
  # SHA는 변경 불가능하므로 가장 안전

# ✅ 신뢰할 수 있는 액션만 사용
# - GitHub 공식: actions/*
# - 검증된 파트너: docker/*, aws-actions/*
```

**6. 코드 인젝션 방지**

```yaml
# ❌ 위험: 사용자 입력을 직접 사용
on:
  issues:
    types: [opened]

jobs:
  comment:
    steps:
      - name: Comment on issue
        run: |
          echo "Issue title: ${{ github.event.issue.title }}"
          # 악의적 제목: "; rm -rf / #"
          # 실행: echo "Issue title: "; rm -rf / #"

# ✅ 안전: 환경 변수 사용
jobs:
  comment:
    steps:
      - name: Comment on issue
        env:
          ISSUE_TITLE: ${{ github.event.issue.title }}
        run: |
          echo "Issue title: $ISSUE_TITLE"
          # 환경 변수는 안전하게 이스케이프됨
```

**7. 보안 스캔 통합**

```yaml
name: Security Scans

on: [push, pull_request]

jobs:
  # 1. 코드 보안 스캔
  codeql:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v2
        with:
          languages: kotlin, java

      - name: Autobuild
        uses: github/codeql-action/autobuild@v2

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2

  # 2. 의존성 취약점 스캔
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Dependency Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: 'LK-Trade'
          path: '.'
          format: 'HTML'
          args: >
            --failOnCVSS 7
            --enableRetired

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: dependency-check-report
          path: reports/

  # 3. Docker 이미지 스캔
  container-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Run Trivy scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:${{ github.sha }}'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'HIGH,CRITICAL'
          exit-code: '1'  # 취약점 발견 시 실패

      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'

  # 4. Secrets 노출 검사
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # 전체 히스토리 검사

      - name: Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**8. Environment 보호 규칙**

```yaml
# Production 배포 보호
jobs:
  deploy-production:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://lk-trade.com
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        run: ./deploy.sh
```

**GitHub Settings > Environments > production:**
```
✅ Required reviewers
   - admin@company.com
   - devops-team

✅ Wait timer: 5 minutes

✅ Deployment branches
   - main
   - release/*

✅ Environment secrets
   - PROD_API_KEY
   - PROD_DB_PASSWORD
```

**9. 감사 로그 및 모니터링**

```yaml
jobs:
  deploy:
    steps:
      - name: Log deployment attempt
        run: |
          cat << EOF >> deployment-audit.log
          Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
          Actor: ${{ github.actor }}
          Action: deploy
          Environment: production
          Commit: ${{ github.sha }}
          Workflow: ${{ github.workflow }}
          EOF

      - name: Deploy
        run: ./deploy.sh

      - name: Record deployment result
        if: always()
        run: |
          echo "Status: ${{ job.status }}" >> deployment-audit.log

          # 외부 감사 시스템에 전송
          curl -X POST ${{ secrets.AUDIT_WEBHOOK }} \
            -H "Content-Type: application/json" \
            -d '{
              "actor": "${{ github.actor }}",
              "action": "deploy",
              "status": "${{ job.status }}",
              "timestamp": "'$(date -u)'",
              "commit": "${{ github.sha }}"
            }'
```

**10. 보안 체크리스트**

```yaml
# .github/workflows/security-checklist.yml
name: Security Checklist

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  security-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check for hardcoded secrets
        run: |
          echo "Checking for hardcoded secrets..."
          ! grep -r -E "(password|api_key|secret).*=.*['\"][^'\"]{8,}" . --exclude-dir={.git,node_modules}

      - name: Check .env files not committed
        run: |
          if git ls-files | grep -E '\.env$'; then
            echo "ERROR: .env file committed!"
            exit 1
          fi

      - name: Check dependencies
        run: |
          ./gradlew dependencyCheckAnalyze

      - name: Verify HTTPS only
        run: |
          ! grep -r "http://" . --include="*.yml" --include="*.yaml" | grep -v "localhost"
```

**보안 요약:**

```
✅ Secrets는 GitHub Secrets에 저장
✅ 최소 권한 원칙 적용
✅ 공개 저장소에 Self-hosted runner 사용 금지
✅ pull_request_target 신중 사용
✅ 써드파티 액션 버전 고정 (SHA 권장)
✅ 코드 인젝션 방지 (환경 변수 사용)
✅ 보안 스캔 통합 (CodeQL, Trivy, Gitleaks)
✅ Environment 보호 규칙 설정
✅ 감사 로그 기록
✅ 정기적인 Secrets 교체 (90일)

❌ 하드코딩된 Secrets
❌ 과도한 권한 부여
❌ 검증되지 않은 액션 사용
❌ Fork PR에 Secrets 노출
❌ 보안 스캔 생략
```

</details>

---

**다음 섹션에서 만나요!** 🚀