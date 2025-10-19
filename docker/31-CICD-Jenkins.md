# 섹션 31: Jenkins를 이용한 CI/CD

## 비유로 시작하기

Jenkins는 **공장의 컨베이어 벨트 시스템**과 같습니다.

```
자동차 공장                          Jenkins CI/CD
===========                          =============
🏭 컨베이어 벨트 시작           →    파이프라인 시작
🔧 부품 검사 스테이션           →    테스트 스테이지
🔩 조립 스테이션                →    빌드 스테이지
🎨 도색 스테이션                →    이미지 생성 스테이지
🔍 품질 검사 스테이션           →    보안 스캔 스테이지
✅ 최종 검수                    →    배포 스테이지
📊 대시보드로 전체 현황 모니터링 →    Jenkins UI
```

---

## Jenkins vs GitHub Actions

### 비교표

```
┌─────────────────────┬────────────────────┬──────────────────────┐
│ 특징                │ Jenkins            │ GitHub Actions       │
├─────────────────────┼────────────────────┼──────────────────────┤
│ 호스팅              │ Self-hosted        │ Cloud (또는 self)    │
│ 초기 설정           │ 복잡               │ 간단                 │
│ 설정 파일           │ Jenkinsfile        │ .yml 파일            │
│ 플러그인            │ 매우 많음 (1800+)  │ 많음                 │
│ UI                  │ 풍부한 대시보드    │ GitHub 통합          │
│ 비용                │ 무료 (서버 필요)   │ 무료 (제한 있음)     │
│ 커스터마이징        │ 매우 높음          │ 중간                 │
│ 러닝 커브           │ 높음               │ 낮음                 │
│ 기업 환경 적합성    │ 매우 높음          │ 중간                 │
└─────────────────────┴────────────────────┴──────────────────────┘
```

### 언제 Jenkins를 사용하나?

```
✅ Jenkins를 선택하는 경우:
- 복잡한 파이프라인이 필요한 경우
- 기존 Jenkins 인프라가 있는 경우
- 높은 수준의 커스터마이징이 필요한 경우
- GitHub 외 다른 VCS 사용 (GitLab, Bitbucket)
- 온프레미스 환경 필수
- 빌드 시간이 매우 긴 경우 (비용 절감)

✅ GitHub Actions를 선택하는 경우:
- 빠른 시작이 필요한 경우
- GitHub 중심 워크플로우
- 간단한 파이프라인
- 인프라 관리 부담을 줄이고 싶은 경우
- 소규모 팀
```

---

## Jenkins 설치 (Docker 사용)

### 1. Jenkins Docker Compose

```yaml
# docker-compose.jenkins.yml
version: '3.8'

services:
  jenkins:
    image: jenkins/jenkins:lts-jdk17
    container_name: jenkins
    privileged: true
    user: root
    ports:
      - "8080:8080"      # Jenkins UI
      - "50000:50000"    # Jenkins Agent 통신
    volumes:
      - jenkins-data:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
      - /usr/bin/docker:/usr/bin/docker
    environment:
      - JENKINS_OPTS=--prefix=/jenkins
      - JAVA_OPTS=-Xmx2048m -Xms1024m
    networks:
      - jenkins-network

  jenkins-agent:
    image: jenkins/ssh-agent:latest
    container_name: jenkins-agent
    environment:
      - JENKINS_AGENT_SSH_PUBKEY=<your-public-key>
    networks:
      - jenkins-network

volumes:
  jenkins-data:
    driver: local

networks:
  jenkins-network:
    driver: bridge
```

### 2. Jenkins 시작

```bash
# Jenkins 시작
docker-compose -f docker-compose.jenkins.yml up -d

# 초기 Admin 비밀번호 확인
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# 출력 예시:
# a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

# Jenkins 접속
# http://localhost:8080
```

### 3. 초기 설정

```
1. 브라우저에서 http://localhost:8080 접속
2. 초기 Admin 비밀번호 입력
3. "Install suggested plugins" 선택
4. Admin 사용자 생성
   - Username: admin
   - Password: <secure-password>
   - Full name: Admin
   - Email: admin@lk-trade.com
5. Jenkins URL 확인: http://localhost:8080
6. "Start using Jenkins" 클릭
```

### 4. 필수 플러그인 설치

```
Jenkins 관리 > Plugins > Available plugins

필수 플러그인:
□ Docker Pipeline
□ Docker
□ Git
□ Pipeline
□ Blue Ocean (현대적인 UI)
□ Slack Notification
□ Email Extension
□ Credentials Binding
□ Gradle
□ JUnit
□ Jacoco

설치 방법:
1. 플러그인 검색
2. 체크박스 선택
3. "Install without restart" 클릭
```

---

## Jenkinsfile 기본

### 1. Declarative Pipeline 구조

```groovy
// Jenkinsfile
pipeline {
    agent any  // 어느 agent에서든 실행

    environment {
        // 환경 변수 정의
        REGISTRY = 'ghcr.io'
        IMAGE_PREFIX = 'lk-trade'
    }

    stages {
        stage('Checkout') {
            steps {
                // Git 체크아웃
                checkout scm
            }
        }

        stage('Build') {
            steps {
                // 빌드 명령
                sh './gradlew build'
            }
        }

        stage('Test') {
            steps {
                // 테스트 실행
                sh './gradlew test'
            }
        }
    }

    post {
        always {
            // 항상 실행
            echo 'Pipeline finished'
        }
        success {
            // 성공 시 실행
            echo 'Pipeline succeeded!'
        }
        failure {
            // 실패 시 실행
            echo 'Pipeline failed!'
        }
    }
}
```

### 2. Scripted Pipeline (더 유연함)

```groovy
// Jenkinsfile
node {
    try {
        stage('Checkout') {
            checkout scm
        }

        stage('Build') {
            sh './gradlew build'
        }

        stage('Test') {
            sh './gradlew test'
        }

        currentBuild.result = 'SUCCESS'
    } catch (Exception e) {
        currentBuild.result = 'FAILURE'
        throw e
    } finally {
        // 정리 작업
        echo "Pipeline finished with result: ${currentBuild.result}"
    }
}
```

---

## LK-Trade Jenkins 파이프라인

### 1. 완전한 CI/CD Jenkinsfile

```groovy
// Jenkinsfile
pipeline {
    agent any

    environment {
        // 환경 변수
        REGISTRY = 'ghcr.io'
        REGISTRY_CREDENTIAL = 'github-registry-credential'
        IMAGE_PREFIX = 'lk-trade'
        SLACK_CHANNEL = '#deployments'
        GRADLE_OPTS = '-Dorg.gradle.daemon=false'
    }

    parameters {
        choice(
            name: 'DEPLOY_ENV',
            choices: ['none', 'staging', 'production'],
            description: 'Deployment environment'
        )
        booleanParam(
            name: 'RUN_SECURITY_SCAN',
            defaultValue: true,
            description: 'Run security vulnerability scan'
        )
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 1, unit: 'HOURS')
        disableConcurrentBuilds()
    }

    stages {
        // ========================================
        // Stage 1: 환경 준비
        // ========================================
        stage('Prepare') {
            steps {
                script {
                    echo "Starting CI/CD Pipeline"
                    echo "Branch: ${env.BRANCH_NAME}"
                    echo "Build Number: ${env.BUILD_NUMBER}"
                    echo "Deploy Environment: ${params.DEPLOY_ENV}"

                    // Git 정보
                    env.GIT_COMMIT_SHORT = sh(
                        script: "git rev-parse --short HEAD",
                        returnStdout: true
                    ).trim()

                    env.GIT_AUTHOR = sh(
                        script: "git log -1 --pretty=format:'%an'",
                        returnStdout: true
                    ).trim()
                }
            }
        }

        // ========================================
        // Stage 2: 코드 품질 검사
        // ========================================
        stage('Code Quality') {
            parallel {
                stage('Ktlint') {
                    steps {
                        echo 'Running Ktlint...'
                        sh './gradlew ktlintCheck'
                    }
                }

                stage('Detekt') {
                    steps {
                        echo 'Running Detekt...'
                        sh './gradlew detekt'
                    }
                }
            }
            post {
                always {
                    // Detekt 리포트 발행
                    publishHTML(target: [
                        reportDir: 'build/reports/detekt',
                        reportFiles: 'detekt.html',
                        reportName: 'Detekt Report'
                    ])
                }
            }
        }

        // ========================================
        // Stage 3: 단위 테스트
        // ========================================
        stage('Unit Tests') {
            steps {
                echo 'Running unit tests...'
                sh './gradlew test'
            }
            post {
                always {
                    // JUnit 테스트 결과 발행
                    junit '**/build/test-results/test/*.xml'

                    // Jacoco 커버리지 리포트
                    jacoco(
                        execPattern: '**/build/jacoco/*.exec',
                        classPattern: '**/build/classes/kotlin/main',
                        sourcePattern: '**/src/main/kotlin'
                    )

                    publishHTML(target: [
                        reportDir: 'build/reports/tests/test',
                        reportFiles: 'index.html',
                        reportName: 'Test Report'
                    ])
                }
            }
        }

        // ========================================
        // Stage 4: 통합 테스트
        // ========================================
        stage('Integration Tests') {
            steps {
                script {
                    echo 'Starting services for integration tests...'

                    // Docker Compose로 테스트 환경 시작
                    sh '''
                        docker-compose -f docker-compose.test.yml up -d postgres redis
                        sleep 10
                    '''

                    try {
                        echo 'Running integration tests...'
                        sh './gradlew integrationTest'
                    } finally {
                        echo 'Stopping test services...'
                        sh 'docker-compose -f docker-compose.test.yml down'
                    }
                }
            }
            post {
                always {
                    junit '**/build/test-results/integrationTest/*.xml'
                }
            }
        }

        // ========================================
        // Stage 5: Docker 이미지 빌드
        // ========================================
        stage('Build Docker Images') {
            steps {
                script {
                    echo 'Building Docker images...'

                    def services = ['user-service', 'trade-service', 'account-service', 'strategy-service']
                    def modulePaths = [
                        'user-service': 'modules/user/api',
                        'trade-service': 'modules/trade/api',
                        'account-service': 'modules/account/api',
                        'strategy-service': 'modules/strategy/api'
                    ]

                    services.each { service ->
                        def modulePath = modulePaths[service]
                        def imageName = "${REGISTRY}/${IMAGE_PREFIX}/${service}"
                        def imageTag = "${env.BRANCH_NAME}-${env.GIT_COMMIT_SHORT}"

                        echo "Building ${service}..."

                        sh """
                            docker build -t ${imageName}:${imageTag} \
                                -t ${imageName}:latest \
                                --build-arg BUILD_DATE=\$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
                                --build-arg VCS_REF=${env.GIT_COMMIT_SHORT} \
                                --build-arg VERSION=${imageTag} \
                                ${modulePath}
                        """

                        // 이미지 정보 저장
                        env."IMAGE_${service.toUpperCase().replace('-', '_')}" = "${imageName}:${imageTag}"
                    }
                }
            }
        }

        // ========================================
        // Stage 6: 보안 스캔
        // ========================================
        stage('Security Scan') {
            when {
                expression { params.RUN_SECURITY_SCAN }
            }
            steps {
                script {
                    echo 'Running security vulnerability scan...'

                    def services = ['user-service', 'trade-service', 'account-service', 'strategy-service']

                    services.each { service ->
                        def imageName = env."IMAGE_${service.toUpperCase().replace('-', '_')}"

                        echo "Scanning ${service}..."

                        // Trivy 스캔
                        sh """
                            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                                aquasec/trivy:latest image \
                                --severity HIGH,CRITICAL \
                                --format table \
                                ${imageName} || true
                        """
                    }
                }
            }
        }

        // ========================================
        // Stage 7: 이미지 푸시
        // ========================================
        stage('Push Images') {
            steps {
                script {
                    echo 'Pushing images to registry...'

                    docker.withRegistry("https://${REGISTRY}", REGISTRY_CREDENTIAL) {
                        def services = ['user-service', 'trade-service', 'account-service', 'strategy-service']

                        services.each { service ->
                            def imageName = env."IMAGE_${service.toUpperCase().replace('-', '_')}"
                            def imageNameLatest = imageName.replaceFirst(/:.*$/, ':latest')

                            sh "docker push ${imageName}"
                            sh "docker push ${imageNameLatest}"

                            echo "Pushed ${imageName}"
                        }
                    }
                }
            }
        }

        // ========================================
        // Stage 8: 배포
        // ========================================
        stage('Deploy') {
            when {
                expression { params.DEPLOY_ENV != 'none' }
            }
            steps {
                script {
                    echo "Deploying to ${params.DEPLOY_ENV}..."

                    if (params.DEPLOY_ENV == 'staging') {
                        deployToStaging()
                    } else if (params.DEPLOY_ENV == 'production') {
                        deployToProduction()
                    }
                }
            }
        }

        // ========================================
        // Stage 9: 헬스 체크
        // ========================================
        stage('Health Check') {
            when {
                expression { params.DEPLOY_ENV != 'none' }
            }
            steps {
                script {
                    def baseUrl = params.DEPLOY_ENV == 'staging'
                        ? 'https://staging.lk-trade.com'
                        : 'https://lk-trade.com'

                    echo 'Waiting for services to be healthy...'
                    sleep(time: 30, unit: 'SECONDS')

                    def services = ['user', 'trade', 'account', 'strategy']

                    services.each { service ->
                        echo "Checking ${service}-service..."
                        sh "curl -f ${baseUrl}/api/${service}/actuator/health || exit 1"
                    }

                    echo 'All services are healthy!'
                }
            }
        }
    }

    post {
        always {
            // 워크스페이스 정리
            cleanWs()
        }

        success {
            script {
                def message = """
                    ✅ *Build Successful!*

                    *Project:* ${env.JOB_NAME}
                    *Build Number:* ${env.BUILD_NUMBER}
                    *Branch:* ${env.BRANCH_NAME}
                    *Commit:* ${env.GIT_COMMIT_SHORT}
                    *Author:* ${env.GIT_AUTHOR}
                    *Deploy:* ${params.DEPLOY_ENV}
                    *Duration:* ${currentBuild.durationString}

                    <${env.BUILD_URL}|View Build>
                """.stripIndent()

                slackSend(
                    channel: SLACK_CHANNEL,
                    color: 'good',
                    message: message
                )
            }
        }

        failure {
            script {
                def message = """
                    ❌ *Build Failed!*

                    *Project:* ${env.JOB_NAME}
                    *Build Number:* ${env.BUILD_NUMBER}
                    *Branch:* ${env.BRANCH_NAME}
                    *Commit:* ${env.GIT_COMMIT_SHORT}
                    *Author:* ${env.GIT_AUTHOR}

                    <${env.BUILD_URL}console|View Console Output>
                """.stripIndent()

                slackSend(
                    channel: SLACK_CHANNEL,
                    color: 'danger',
                    message: message
                )

                // 이메일 알림
                emailext(
                    subject: "Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                    body: message,
                    to: '${DEFAULT_RECIPIENTS}'
                )
            }
        }
    }
}

// ========================================
// 배포 함수
// ========================================
def deployToStaging() {
    echo 'Deploying to Staging...'

    withCredentials([sshUserPrivateKey(
        credentialsId: 'staging-ssh-key',
        keyFileVariable: 'SSH_KEY',
        usernameVariable: 'SSH_USER'
    )]) {
        sh """
            ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no \
                ${SSH_USER}@staging.lk-trade.com \
                'cd /opt/lk-trade && \
                 export VERSION=${env.BRANCH_NAME}-${env.GIT_COMMIT_SHORT} && \
                 docker-compose pull && \
                 docker-compose up -d'
        """
    }
}

def deployToProduction() {
    echo 'Deploying to Production...'

    // 수동 승인 요청
    input(
        message: 'Deploy to Production?',
        ok: 'Deploy',
        submitter: 'admin,devops'
    )

    withCredentials([sshUserPrivateKey(
        credentialsId: 'production-ssh-key',
        keyFileVariable: 'SSH_KEY',
        usernameVariable: 'SSH_USER'
    )]) {
        sh """
            ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no \
                ${SSH_USER}@lk-trade.com \
                'cd /opt/lk-trade && \
                 bash scripts/blue-green-deploy.sh ${env.BRANCH_NAME}-${env.GIT_COMMIT_SHORT}'
        """
    }
}
```

---

## Jenkins Job 생성

### 1. Multibranch Pipeline 생성

```
1. Jenkins 대시보드 > New Item
2. 이름 입력: lk-trade-pipeline
3. "Multibranch Pipeline" 선택
4. OK 클릭

5. Branch Sources 설정:
   - Add source > Git
   - Project Repository: https://github.com/your-org/lk-trade.git
   - Credentials: GitHub Personal Access Token

6. Build Configuration:
   - Mode: by Jenkinsfile
   - Script Path: Jenkinsfile

7. Scan Multibranch Pipeline Triggers:
   - ☑ Periodically if not otherwise run
   - Interval: 1 minute

8. Save
```

### 2. Credentials 설정

```
Jenkins 관리 > Credentials > System > Global credentials

추가할 Credentials:

1. GitHub Token (ID: github-token)
   - Kind: Secret text
   - Secret: <GitHub Personal Access Token>
   - ID: github-token

2. GitHub Registry (ID: github-registry-credential)
   - Kind: Username with password
   - Username: <GitHub Username>
   - Password: <GitHub Personal Access Token>
   - ID: github-registry-credential

3. Staging SSH Key (ID: staging-ssh-key)
   - Kind: SSH Username with private key
   - Username: deploy
   - Private Key: Enter directly
   - Key: <SSH Private Key>
   - ID: staging-ssh-key

4. Production SSH Key (ID: production-ssh-key)
   - Kind: SSH Username with private key
   - Username: deploy
   - Private Key: Enter directly
   - Key: <SSH Private Key>
   - ID: production-ssh-key

5. Slack Token (ID: slack-token)
   - Kind: Secret text
   - Secret: <Slack Webhook URL>
   - ID: slack-token
```

---

## Jenkins 고급 기능

### 1. Shared Library (공통 코드 재사용)

```groovy
// vars/buildDockerImage.groovy
def call(String serviceName, String modulePath) {
    def imageName = "${env.REGISTRY}/${env.IMAGE_PREFIX}/${serviceName}"
    def imageTag = "${env.BRANCH_NAME}-${env.GIT_COMMIT_SHORT}"

    echo "Building ${serviceName}..."

    sh """
        docker build -t ${imageName}:${imageTag} \
            -t ${imageName}:latest \
            ${modulePath}
    """

    return "${imageName}:${imageTag}"
}
```

```groovy
// vars/deployService.groovy
def call(String environment, String version) {
    def host = environment == 'staging'
        ? 'staging.lk-trade.com'
        : 'lk-trade.com'

    withCredentials([sshUserPrivateKey(
        credentialsId: "${environment}-ssh-key",
        keyFileVariable: 'SSH_KEY',
        usernameVariable: 'SSH_USER'
    )]) {
        sh """
            ssh -i ${SSH_KEY} ${SSH_USER}@${host} \
                'cd /opt/lk-trade && \
                 export VERSION=${version} && \
                 docker-compose up -d'
        """
    }
}
```

사용:

```groovy
// Jenkinsfile
@Library('lk-trade-shared-library') _

pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                script {
                    buildDockerImage('user-service', 'modules/user/api')
                    buildDockerImage('trade-service', 'modules/trade/api')
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    deployService('staging', "${env.BRANCH_NAME}-${env.GIT_COMMIT_SHORT}")
                }
            }
        }
    }
}
```

### 2. Blue Ocean (현대적인 UI)

```bash
# Blue Ocean 플러그인 설치 후
# http://localhost:8080/blue 접속

특징:
- 시각적 파이프라인 에디터
- 깔끔한 UI
- 실시간 로그
- 브랜치별 뷰
```

### 3. Jenkins Job DSL (Infrastructure as Code)

```groovy
// jobs/lk-trade-jobs.groovy
pipelineJob('lk-trade-ci-cd') {
    description('LK-Trade CI/CD Pipeline')

    parameters {
        choiceParam('DEPLOY_ENV', ['none', 'staging', 'production'], 'Deployment environment')
        booleanParam('RUN_SECURITY_SCAN', true, 'Run security scan')
    }

    definition {
        cpsScm {
            scm {
                git {
                    remote {
                        url('https://github.com/your-org/lk-trade.git')
                        credentials('github-token')
                    }
                    branches('*/main', '*/develop')
                }
            }
            scriptPath('Jenkinsfile')
        }
    }

    triggers {
        githubPush()
        pollSCM('H/5 * * * *')
    }
}

// 여러 Job 생성
['user', 'trade', 'account', 'strategy'].each { module ->
    pipelineJob("lk-trade-${module}-service") {
        description("Build and deploy ${module}-service")

        definition {
            cpsScm {
                scm {
                    git {
                        remote {
                            url('https://github.com/your-org/lk-trade.git')
                        }
                        branches('*/main')
                    }
                }
                scriptPath("modules/${module}/Jenkinsfile")
            }
        }
    }
}
```

---

## 모니터링 및 최적화

### 1. 빌드 시간 최적화

```groovy
pipeline {
    agent any

    options {
        // 빌드 히스토리 제한
        buildDiscarder(logRotator(
            numToKeepStr: '10',
            artifactNumToKeepStr: '5'
        ))

        // 동시 빌드 방지
        disableConcurrentBuilds()

        // 타임아웃 설정
        timeout(time: 1, unit: 'HOURS')
    }

    stages {
        stage('Build') {
            steps {
                // Gradle 캐싱 활용
                sh '''
                    ./gradlew build \
                        --build-cache \
                        --parallel \
                        --max-workers=4
                '''
            }
        }
    }
}
```

### 2. Docker 레이어 캐싱

```groovy
stage('Build Docker Image') {
    steps {
        script {
            // BuildKit 활성화
            sh """
                DOCKER_BUILDKIT=1 docker build \
                    --cache-from ${imageName}:latest \
                    --build-arg BUILDKIT_INLINE_CACHE=1 \
                    -t ${imageName}:${imageTag} \
                    .
            """
        }
    }
}
```

### 3. 병렬 실행

```groovy
stage('Tests') {
    parallel {
        stage('Unit Tests') {
            steps {
                sh './gradlew test'
            }
        }
        stage('Integration Tests') {
            steps {
                sh './gradlew integrationTest'
            }
        }
        stage('E2E Tests') {
            steps {
                sh './gradlew e2eTest'
            }
        }
    }
}
```

---

## Jenkins 백업 및 복구

### 1. Jenkins 데이터 백업

```bash
#!/bin/bash
# scripts/backup-jenkins.sh

JENKINS_HOME=/var/jenkins_home
BACKUP_DIR=./backups/jenkins
DATE=$(date +%Y%m%d-%H%M%S)

echo "🔄 Backing up Jenkins..."

# Jenkins 홈 디렉토리 백업
docker exec jenkins tar czf - \
    --exclude='workspace/*' \
    --exclude='caches/*' \
    --exclude='logs/*' \
    /var/jenkins_home \
    > "$BACKUP_DIR/jenkins-home-$DATE.tar.gz"

echo "✅ Jenkins backup completed: jenkins-home-$DATE.tar.gz"
```

### 2. Jenkins 복구

```bash
#!/bin/bash
# scripts/restore-jenkins.sh

if [ -z "$1" ]; then
    echo "Usage: $0 <backup-file>"
    exit 1
fi

BACKUP_FILE=$1

echo "🔄 Restoring Jenkins..."

# Jenkins 중지
docker-compose -f docker-compose.jenkins.yml stop jenkins

# 데이터 복구
docker run --rm \
    -v jenkins-data:/var/jenkins_home \
    -v $(pwd):/backup \
    alpine \
    sh -c "cd /var/jenkins_home && tar xzf /backup/$BACKUP_FILE --strip-components=2"

# Jenkins 시작
docker-compose -f docker-compose.jenkins.yml start jenkins

echo "✅ Jenkins restored successfully"
```

---

## Jenkins vs GitHub Actions: 실전 비교

### LK-Trade 프로젝트 시나리오

```
시나리오: 4개 마이크로서비스 빌드 및 배포

GitHub Actions:
- 실행 시간: 12분
- 비용: $0.008/분 × 12분 = $0.096/빌드
- 월 100회 빌드: $9.6
- 장점: 설정 간단, GitHub 통합
- 단점: 복잡한 커스터마이징 제한

Jenkins (Self-hosted):
- 실행 시간: 8분 (캐싱 최적화)
- 비용: 서버 비용 $50/월 (고정)
- 월 100회 빌드: $50 (빌드 횟수 무관)
- 장점: 무제한 빌드, 높은 커스터마이징
- 단점: 서버 관리 필요

결론:
- 월 500회 이하: GitHub Actions 권장
- 월 500회 이상: Jenkins 권장
- 복잡한 파이프라인: Jenkins 권장
```

---

## Makefile 통합

```makefile
# Makefile
.PHONY: jenkins-start jenkins-stop jenkins-backup jenkins-restore

# Jenkins 시작
jenkins-start:
	docker-compose -f docker-compose.jenkins.yml up -d
	@echo "Jenkins is starting..."
	@echo "Waiting for Jenkins to be ready..."
	@sleep 30
	@docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword || echo "Jenkins already configured"
	@echo "Jenkins URL: http://localhost:8080"

# Jenkins 중지
jenkins-stop:
	docker-compose -f docker-compose.jenkins.yml stop

# Jenkins 백업
jenkins-backup:
	bash scripts/backup-jenkins.sh

# Jenkins 복구
jenkins-restore:
	@read -p "Enter backup file: " file; \
	bash scripts/restore-jenkins.sh $$file

# Jenkins 로그 확인
jenkins-logs:
	docker-compose -f docker-compose.jenkins.yml logs -f jenkins
```

---

## 다음 단계

축하합니다! 🎉 Jenkins를 이용한 CI/CD 파이프라인을 완벽하게 마스터했습니다.

### 이번 섹션에서 배운 것

✅ Jenkins 설치 및 초기 설정
✅ Jenkinsfile (Declarative & Scripted)
✅ LK-Trade 완전한 CI/CD 파이프라인
✅ Multibranch Pipeline 설정
✅ Credentials 관리
✅ Shared Library (코드 재사용)
✅ Blue Ocean (현대적인 UI)
✅ 빌드 최적화 및 병렬 실행
✅ Jenkins 백업 및 복구
✅ Jenkins vs GitHub Actions 비교

### 다음에 배울 것

**섹션 32: Docker Swarm (오케스트레이션)**에서는:
- Docker Swarm 클러스터 구성
- 서비스 배포 및 스케일링
- 로드 밸런싱
- 롤링 업데이트
- Secret 관리

### 추가 학습 자료

**공식 문서:**
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Blue Ocean](https://www.jenkins.io/doc/book/blueocean/)

**플러그인:**
- [Jenkins Plugins Index](https://plugins.jenkins.io/)

---

**다음 섹션에서 만나요!** 🚀