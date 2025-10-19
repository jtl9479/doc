# 섹션 30: CI/CD 파이프라인 (GitHub Actions)

## 비유로 시작하기

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

## 왜 CI/CD가 필요한가?

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

**다음 섹션에서 만나요!** 🚀