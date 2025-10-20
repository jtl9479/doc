# 섹션 31: Jenkins를 이용한 CI/CD

> **학습 목표**: Jenkins를 Docker 환경에서 설치하고, Jenkinsfile을 작성하여 복잡한 멀티스테이지 CI/CD 파이프라인을 구축하며, 플러그인 생태계를 활용한 엔터프라이즈급 자동화 시스템을 운영할 수 있습니다.

**⏱️ 예상 학습 시간**: 4-5시간
**난이도**: ⭐⭐⭐⭐⭐ (5개/5개)

---

## 🔍 실생활 비유로 이해하기

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

## 💡 왜 Jenkins가 필요한가?

### 실무 배경

**"GitHub Actions로 시작했는데, 프로젝트가 커지면서 한계가 보입니다!"**

#### ❌ GitHub Actions만 사용하면 발생하는 문제

```
문제 1: 빌드 시간 제한으로 비용 증가
- 증상: 빌드 시간 1시간 넘는 프로젝트
- 영향: GitHub Actions 무료 플랜 2000분 금방 소진
- 비용: 월 $40+ 추가 비용 (팀 플랜)

문제 2: 복잡한 파이프라인 관리 어려움
- 증상: 30개 이상의 마이크로서비스 관리
- 영향: YAML 파일 복잡도 증가, 재사용성 낮음
- 비용: 파이프라인 유지보수에 주 10시간 투입

문제 3: 온프레미스 환경 제한
- 증상: 보안상 외부 클라우드 사용 불가
- 영향: Self-hosted runner 관리 부담
- 비용: DevOps 인력 추가 투입

문제 4: 고급 기능 부족
- 증상: 복잡한 승인 프로세스, 다양한 VCS 통합 필요
- 영향: 커스텀 솔루션 개발 필요
- 비용: 개발 및 유지보수 비용
```

#### ✅ Jenkins의 장점

```
장점 1: 무제한 빌드 시간
- Self-hosted로 시간 제한 없음
- 대규모 프로젝트도 비용 걱정 없음

장점 2: 1800+ 플러그인 생태계
- 거의 모든 도구와 통합 가능
- 복잡한 워크플로우 구현 용이

장점 3: 완전한 커스터마이징
- Groovy 스크립트로 모든 것 제어 가능
- 기업 요구사항 완벽 대응

장점 4: 엔터프라이즈 기능
- Role-based access control (RBAC)
- 감사 로그 (Audit Trail)
- 복잡한 승인 프로세스
- 멀티 브랜치 파이프라인
```

### 실제 도입 효과

```
A사 사례 (전자상거래, 마이크로서비스 50개):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Before (GitHub Actions):
- 월 비용: $200
- 파이프라인 관리 시간: 주 15시간
- 빌드 대기 시간: 평균 10분

After (Jenkins):
- 월 비용: $50 (서버 비용만)
- 파이프라인 관리 시간: 주 5시간
- 빌드 대기 시간: 평균 2분
- ROI: 3개월 만에 투자 회수
```

---

## Jenkins vs GitHub Actions 비교

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

## 👨‍💻 주니어 개발자 시나리오

### 시나리오 1: 첫 Jenkinsfile 작성 - "파이프라인을 어떻게 시작하죠?"

**상황:** 신입 개발자로 입사 후, "Jenkinsfile을 작성해서 자동 빌드를 설정해주세요"라는 요청을 받았습니다.

**문제:**
```
"Jenkinsfile이 뭐지?
어디에 만들어야 하지?
Declarative vs Scripted는 뭐가 다르지?"
```

**단계별 해결:**

```bash
# 1단계: 프로젝트 루트에 Jenkinsfile 생성
cd /path/to/project
touch Jenkinsfile
```

**2단계: 첫 번째 Jenkinsfile 작성 (Declarative Pipeline)**

```groovy
// Jenkinsfile
pipeline {
    agent any  // 어느 agent에서든 실행

    stages {
        stage('Checkout') {
            steps {
                echo '코드 체크아웃 중...'
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo '빌드 시작...'
                sh './gradlew clean build'
            }
        }

        stage('Test') {
            steps {
                echo '테스트 실행 중...'
                sh './gradlew test'
            }
        }
    }

    post {
        success {
            echo '✅ 파이프라인 성공!'
        }
        failure {
            echo '❌ 파이프라인 실패!'
        }
    }
}
```

**3단계: Jenkins에서 Job 생성**

```
1. Jenkins 대시보드 접속
2. "New Item" 클릭
3. 이름 입력: "my-first-pipeline"
4. "Pipeline" 선택 후 OK
5. Pipeline 설정:
   - Definition: Pipeline script from SCM
   - SCM: Git
   - Repository URL: https://github.com/your-org/project.git
   - Script Path: Jenkinsfile
6. Save
```

**4단계: 파이프라인 실행**

```
1. "Build Now" 클릭
2. 실행 로그 확인
```

**실행 결과:**
```
Started by user admin
[Pipeline] Start
[Pipeline] node
[Pipeline] {
[Pipeline] stage (Checkout)
[Pipeline] {
코드 체크아웃 중...
Cloning repository...
[Pipeline] }
[Pipeline] stage (Build)
[Pipeline] {
빌드 시작...
BUILD SUCCESSFUL in 30s
[Pipeline] }
[Pipeline] stage (Test)
[Pipeline] {
테스트 실행 중...
45 tests passed
[Pipeline] }
[Pipeline] }
✅ 파이프라인 성공!
[Pipeline] End of Pipeline
Finished: SUCCESS
```

**배운 점:**

1. **Jenkinsfile 위치**: 프로젝트 루트에 `Jenkinsfile` (확장자 없음)
2. **pipeline {}**: Declarative Pipeline의 시작
3. **agent**: 파이프라인을 실행할 위치
4. **stages**: 실행할 단계들
5. **post**: 파이프라인 완료 후 작업

**개선된 버전 (환경 변수 추가):**

```groovy
pipeline {
    agent any

    environment {
        // 환경 변수 정의
        APP_NAME = 'my-app'
        VERSION = '1.0.0'
        GRADLE_OPTS = '-Dorg.gradle.daemon=false'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo "Building ${APP_NAME} v${VERSION}..."
                sh './gradlew clean build'
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                sh './gradlew test'
            }
            post {
                always {
                    // 테스트 결과 항상 저장
                    junit '**/build/test-results/test/*.xml'
                }
            }
        }
    }

    post {
        success {
            echo "✅ ${APP_NAME} v${VERSION} 빌드 성공!"
        }
        failure {
            echo "❌ ${APP_NAME} v${VERSION} 빌드 실패!"
        }
    }
}
```

---

### 시나리오 2: Pipeline 실패 디버깅 - "Jenkins에서 왜 실패하죠?"

**상황:** 로컬에서는 빌드가 성공하는데 Jenkins에서만 실패합니다.

**에러 메시지:**
```
[Pipeline] sh
+ ./gradlew build
FAILURE: Build failed with an exception.

* What went wrong:
A problem occurred evaluating root project 'my-app'.
> Could not find method testImplementation() for arguments [org.junit.jupiter:junit-jupiter:5.9.0]

BUILD FAILED in 5s
```

**문제 분석:**

```groovy
// ❌ 문제가 있는 Jenkinsfile
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh './gradlew build'
                // 문제: Gradle Wrapper가 없거나, Java 버전이 맞지 않음
            }
        }
    }
}
```

**해결 과정:**

**1단계: Java 버전 확인**

```groovy
pipeline {
    agent any

    stages {
        stage('Debug Environment') {
            steps {
                sh 'java -version'
                sh './gradlew --version'
                sh 'env | sort'
            }
        }
    }
}
```

**실행 결과:**
```
openjdk version "11.0.20" 2023-07-18
...
```

**문제 발견:** 프로젝트는 Java 17 필요, Jenkins는 Java 11 사용!

**2단계: 올바른 Java 버전 지정**

```groovy
// ✅ 수정된 Jenkinsfile
pipeline {
    agent any

    tools {
        // Jenkins에 설정된 JDK 사용
        jdk 'JDK17'
        // Jenkins 관리 > Global Tool Configuration에서 JDK17 설정 필요
    }

    environment {
        JAVA_HOME = tool name: 'JDK17'
        PATH = "${JAVA_HOME}/bin:${env.PATH}"
    }

    stages {
        stage('Verify Environment') {
            steps {
                echo 'Verifying environment...'
                sh 'java -version'
                sh './gradlew --version'
            }
        }

        stage('Build') {
            steps {
                echo 'Building application...'
                sh './gradlew clean build'
            }
        }
    }
}
```

**3단계: Jenkins Tool 설정**

```
Jenkins 관리 > Global Tool Configuration

JDK installations:
- Name: JDK17
- JAVA_HOME: /usr/lib/jvm/java-17-openjdk-amd64
  또는
- Install automatically
  - Add Installer: Install from adoptium.net
  - Version: jdk-17+35
```

**실행 결과:**
```
[Pipeline] stage (Verify Environment)
openjdk version "17.0.8" 2023-07-18
OpenJDK Runtime Environment...

[Pipeline] stage (Build)
Building application...
BUILD SUCCESSFUL in 45s

Finished: SUCCESS
```

**추가 디버깅 팁:**

```groovy
pipeline {
    agent any

    stages {
        stage('Debug') {
            steps {
                script {
                    // 환경 정보 출력
                    echo "Workspace: ${env.WORKSPACE}"
                    echo "Build Number: ${env.BUILD_NUMBER}"
                    echo "Job Name: ${env.JOB_NAME}"

                    // 파일 확인
                    sh 'ls -la'
                    sh 'pwd'

                    // Gradle 상태 확인
                    sh './gradlew tasks --all'
                }
            }
        }
    }
}
```

**배운 점:**

1. **tools** 블록으로 JDK 버전 지정
2. Jenkins Global Tool Configuration 설정 중요
3. 디버깅 시 환경 정보 먼저 확인
4. 로컬과 Jenkins 환경 차이 이해
5. `script {}` 블록에서 Groovy 코드 실행 가능

---

### 시나리오 3: Plugin 충돌 해결 - "플러그인이 작동 안 해요!"

**상황:** Slack 알림을 추가했는데 파이프라인이 실패합니다.

**에러 메시지:**
```
[Pipeline] slackSend
java.lang.NoSuchMethodError: No such DSL method 'slackSend' found among steps
```

**문제:**
```
Slack Notification 플러그인이 설치되지 않았거나,
다른 플러그인과 충돌 발생
```

**해결 과정:**

**1단계: 필수 플러그인 확인 및 설치**

```
Jenkins 관리 > Plugins

Available plugins 검색:
□ Slack Notification Plugin
□ Credentials Plugin
□ Pipeline: Stage View Plugin

모두 체크 후 "Install without restart"
```

**2단계: 플러그인 버전 확인**

```
Jenkins 관리 > Plugins > Installed plugins

Slack Notification Plugin: v2.49
Credentials Plugin: v2.6.1
```

**3단계: Jenkinsfile 수정**

```groovy
// ❌ 잘못된 사용
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh './gradlew build'
            }
        }
    }

    post {
        always {
            slackSend channel: '#deployments', message: 'Build completed'
            // 에러: Slack credential 설정 안 됨
        }
    }
}

// ✅ 올바른 사용
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh './gradlew build'
            }
        }
    }

    post {
        success {
            slackSend(
                channel: '#deployments',
                color: 'good',
                message: """
                    ✅ Build Successful!
                    Job: ${env.JOB_NAME}
                    Build: ${env.BUILD_NUMBER}
                    URL: ${env.BUILD_URL}
                """.stripIndent(),
                teamDomain: 'your-team',
                tokenCredentialId: 'slack-token'
            )
        }

        failure {
            slackSend(
                channel: '#deployments',
                color: 'danger',
                message: """
                    ❌ Build Failed!
                    Job: ${env.JOB_NAME}
                    Build: ${env.BUILD_NUMBER}
                    URL: ${env.BUILD_URL}console
                """.stripIndent(),
                teamDomain: 'your-team',
                tokenCredentialId: 'slack-token'
            )
        }
    }
}
```

**4단계: Slack Credential 설정**

```
1. Slack App 생성:
   https://api.slack.com/apps
   - Create New App
   - From scratch
   - App Name: Jenkins Bot
   - Workspace: your-workspace

2. OAuth & Permissions:
   - Bot Token Scopes 추가:
     - chat:write
     - chat:write.public
   - Install to Workspace
   - OAuth Token 복사 (xoxb-...)

3. Jenkins Credential 추가:
   Jenkins > Credentials > System > Global credentials
   - Kind: Secret text
   - Secret: xoxb-your-token
   - ID: slack-token
   - Description: Slack Bot Token
```

**실행 결과:**
```
[Pipeline] slackSend
Slack Send Pipeline step configured values from global config - baseUrl: https://slack.com/api/, teamDomain: your-team, tokenCredentialId: slack-token
Slack Send Pipeline step running, values are - channel: #deployments, color: good, message: ...
[Pipeline] End of Pipeline
Finished: SUCCESS

Slack에 메시지 전송됨:
┌─────────────────────────────────┐
│ Jenkins Bot                      │
├─────────────────────────────────┤
│ ✅ Build Successful!            │
│ Job: my-app-pipeline             │
│ Build: #42                       │
│ URL: http://jenkins/job/my-app/ │
└─────────────────────────────────┘
```

**플러그인 충돌 해결:**

```groovy
// 여러 플러그인 사용 시
@Library('shared-library') _

pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                script {
                    // Docker Pipeline Plugin
                    docker.image('gradle:7-jdk17').inside {
                        sh 'gradle build'
                    }
                }
            }
        }
    }

    post {
        always {
            // JUnit Plugin
            junit '**/build/test-results/**/*.xml'

            // HTML Publisher Plugin
            publishHTML(target: [
                reportDir: 'build/reports/tests/test',
                reportFiles: 'index.html',
                reportName: 'Test Report'
            ])

            // Slack Notification Plugin
            slackSend(
                channel: '#builds',
                message: "Build ${currentBuild.result}",
                tokenCredentialId: 'slack-token'
            )
        }
    }
}
```

**배운 점:**

1. 플러그인 설치 후 Jenkins 재시작 필요할 수 있음
2. Credential ID는 정확히 일치해야 함
3. 플러그인 문서 확인 중요
4. `script {}` 블록 안에서만 작동하는 플러그인 있음
5. 플러그인 버전 호환성 확인

---

### 시나리오 4: Blue Ocean으로 시각화 - "파이프라인을 예쁘게 보고 싶어요!"

**상황:** 기본 Jenkins UI가 복잡해서 파이프라인 상태를 한눈에 보기 어렵습니다.

**해결: Blue Ocean 설치**

**1단계: Blue Ocean 플러그인 설치**

```
Jenkins 관리 > Plugins > Available plugins

검색: Blue Ocean
□ Blue Ocean
□ Blue Ocean Pipeline Editor

"Install without restart"
```

**2단계: Blue Ocean 접속**

```
Jenkins 메인 화면에서
"Open Blue Ocean" 클릭

또는

URL: http://localhost:8080/blue
```

**3단계: 복잡한 파이프라인 작성**

```groovy
// Jenkinsfile
pipeline {
    agent any

    environment {
        REGISTRY = 'ghcr.io'
        IMAGE_NAME = 'my-app'
    }

    stages {
        stage('Prepare') {
            steps {
                echo 'Preparing build environment...'
                sh 'java -version'
            }
        }

        stage('Build & Test') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        echo 'Running unit tests...'
                        sh './gradlew test'
                    }
                }

                stage('Integration Tests') {
                    steps {
                        echo 'Running integration tests...'
                        sh './gradlew integrationTest'
                    }
                }

                stage('Code Quality') {
                    steps {
                        echo 'Running code quality checks...'
                        sh './gradlew ktlintCheck detekt'
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building Docker image...'
                    docker.build("${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER}")
                }
            }
        }

        stage('Security Scan') {
            steps {
                echo 'Scanning for vulnerabilities...'
                sh "docker run --rm aquasec/trivy:latest image ${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER}"
            }
        }

        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                echo 'Deploying to staging...'
                sh './deploy-staging.sh'
            }
        }

        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'
                echo 'Deploying to production...'
                sh './deploy-production.sh'
            }
        }
    }

    post {
        always {
            junit '**/build/test-results/**/*.xml'
            publishHTML(target: [
                reportDir: 'build/reports/tests/test',
                reportFiles: 'index.html',
                reportName: 'Test Report'
            ])
        }

        success {
            slackSend(
                channel: '#deployments',
                color: 'good',
                message: "✅ Pipeline Success: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                tokenCredentialId: 'slack-token'
            )
        }

        failure {
            slackSend(
                channel: '#deployments',
                color: 'danger',
                message: "❌ Pipeline Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                tokenCredentialId: 'slack-token'
            )
        }
    }
}
```

**Blue Ocean에서 보이는 것:**

```
┌─────────────────────────────────────────────────────┐
│ my-app-pipeline                            #42  ✅  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Prepare ──> Build & Test ──> Build Docker ──>     │
│              ├─ Unit Tests                          │
│              ├─ Integration Tests                   │
│              └─ Code Quality                        │
│                                                      │
│  Security Scan ──> Deploy to Staging                │
│                                                      │
│  Duration: 8m 30s                                   │
│  Branch: develop                                    │
│  Commit: a1b2c3d                                    │
│  Author: John Doe                                   │
└─────────────────────────────────────────────────────┘

각 스테이지를 클릭하면 상세 로그 확인 가능
병렬 실행 스테이지는 나란히 표시됨
실패한 스테이지는 빨간색으로 강조
```

**Blue Ocean의 장점:**

1. **시각적 파이프라인 뷰**: 단계별 진행 상황 한눈에 확인
2. **병렬 실행 표시**: 동시 실행되는 작업 명확히 구분
3. **실시간 로그**: 각 스테이지 로그 실시간 확인
4. **브랜치별 뷰**: Git 브랜치별 파이프라인 상태
5. **직관적인 UI**: 초보자도 쉽게 이해

**Visual Pipeline Editor 사용:**

```
Blue Ocean > New Pipeline 클릭
또는
기존 파이프라인 > Edit Pipeline

GUI로 파이프라인 작성:
1. Stage 추가 버튼 클릭
2. Stage 이름 입력
3. Step 추가 (Shell Script, Git, etc.)
4. Parallel stages 추가 가능
5. 완료 후 "Save" → Jenkinsfile 자동 생성
```

**배운 점:**

1. Blue Ocean은 시각화에 특화
2. Pipeline Editor로 GUI에서 파이프라인 작성 가능
3. 기존 Jenkinsfile과 호환됨
4. 병렬 실행과 복잡한 파이프라인에 유용
5. Git 브랜치 전략과 잘 맞음

---

## ❓ FAQ

<details>
<summary><strong>Q1: Jenkins vs GitHub Actions, 어떤 것을 선택해야 하나요?</strong></summary>

### 상세 답변

**Jenkins를 선택하는 경우:**

```
✅ 적합한 상황:
- 복잡한 파이프라인 필요 (10+ 단계, 복잡한 로직)
- 기존 Jenkins 인프라가 있는 경우
- 매우 높은 수준의 커스터마이징 필요
- 온프레미스 환경 필수 (보안, 규정 준수)
- 빌드가 매우 빈번한 경우 (하루 100회+)
- 대규모 팀 (20명 이상)
- 다양한 VCS 사용 (GitLab, Bitbucket, SVN)
- 빌드 시간이 매우 긴 경우 (1시간+)

장점:
- 무제한 빌드 (서버 비용만 지불)
- 1800+ 플러그인으로 거의 모든 것 통합 가능
- 매우 높은 커스터마이징 (Groovy 스크립트)
- 풍부한 UI와 대시보드 (Blue Ocean)
- 강력한 분산 빌드 (Agent 활용)
- 오랜 역사와 커뮤니티

단점:
- 초기 설정 복잡 (설치, 플러그인, 권한 등)
- 서버 관리 필요 (업데이트, 백업, 모니터링)
- 러닝 커브 높음 (Groovy, Pipeline DSL)
- 플러그인 충돌 가능성
- 보안 설정 복잡
```

**GitHub Actions를 선택하는 경우:**

```
✅ 적합한 상황:
- GitHub 중심 개발 워크플로우
- 빠른 시작과 설정이 필요한 경우
- 소규모~중규모 팀 (5~15명)
- 간단~중간 수준의 파이프라인
- 인프라 관리 부담을 줄이고 싶은 경우
- 오픈소스 프로젝트 (무료)
- 빌드 빈도가 적당한 경우 (하루 20회 이하)

장점:
- 설정이 매우 간단 (.yml 파일만 추가)
- GitHub와 완벽한 통합 (PR, Issues, etc.)
- 무료 tier 제공 (월 2000분)
- 서버 관리 불필요
- Marketplace의 다양한 액션
- 빠른 학습 곡선 (YAML)

단점:
- 복잡한 커스터마이징 제한적
- 빌드 시간이 길면 비용 증가
- Self-hosted runner 설정이 Jenkins보다 복잡
- GitHub 외 VCS 지원 제한적
```

**비용 비교 (실제 시나리오):**

```
시나리오: 중규모 프로젝트 (5개 마이크로서비스)

GitHub Actions:
- 하루 30회 빌드
- 빌드당 평균 15분
- 월 빌드 시간: 30 × 15분 × 30일 = 13,500분
- 무료 tier: 2,000분
- 초과 시간: 11,500분
- 비용: 11,500 × $0.008 = $92/월

Jenkins (Self-hosted):
- AWS EC2 t3.large 인스턴스
- CPU: 2 vCPU, RAM: 8GB
- 월 서버 비용: $60~80
- 빌드 횟수: 무제한
- 총 비용: $70/월 (고정)

결론:
- 월 8,000분 이하: GitHub Actions 권장
- 월 8,000분 이상: Jenkins 권장
- 복잡한 파이프라인: Jenkins 권장
```

**실전 예시:**

```groovy
// Jenkins: 복잡한 배포 로직
pipeline {
    agent any

    stages {
        stage('Deploy') {
            steps {
                script {
                    // Groovy 로직으로 복잡한 분기 처리
                    def deployEnv = env.BRANCH_NAME == 'main' ? 'production' : 'staging'
                    def approvers = deployEnv == 'production' ? ['admin', 'devops'] : ['developers']

                    if (deployEnv == 'production') {
                        // Production은 승인 필요
                        timeout(time: 1, unit: 'HOURS') {
                            input message: 'Deploy to production?',
                                  submitter: approvers.join(',')
                        }
                    }

                    // Blue-Green 배포
                    def currentColor = sh(
                        script: "ssh deploy@${deployEnv}.com 'cat /opt/app/current-color'",
                        returnStdout: true
                    ).trim()

                    def newColor = currentColor == 'blue' ? 'green' : 'blue'

                    // 새 컬러 환경에 배포
                    sh "ssh deploy@${deployEnv}.com 'bash /opt/app/deploy-${newColor}.sh'"

                    // 헬스 체크
                    def healthy = sh(
                        script: "curl -f http://${deployEnv}.com:${newColor == 'blue' ? '8080' : '8081'}/health",
                        returnStatus: true
                    ) == 0

                    if (healthy) {
                        // 트래픽 전환
                        sh "ssh deploy@${deployEnv}.com 'bash /opt/app/switch-to-${newColor}.sh'"
                        echo "Switched to ${newColor}"
                    } else {
                        error "Health check failed for ${newColor}"
                    }
                }
            }
        }
    }
}
```

```yaml
# GitHub Actions: 비슷한 로직이지만 제한적
name: Deploy

on:
  push:
    branches: [main, develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.ref == 'refs/heads/main' && 'production' || 'staging' }}
    steps:
      - uses: actions/checkout@v4

      - name: Deploy
        run: |
          # 복잡한 로직은 외부 스크립트로 분리해야 함
          ./scripts/blue-green-deploy.sh
        env:
          DEPLOY_ENV: ${{ github.ref == 'refs/heads/main' && 'production' || 'staging' }}
```

**Best Practice: 하이브리드 접근**

```
많은 조직이 두 가지를 함께 사용:

GitHub Actions:
- PR 검증 (lint, unit tests)
- 간단한 빌드
- 오픈소스 프로젝트

Jenkins:
- Production 배포
- 복잡한 통합 테스트
- 레거시 시스템 통합
- 대규모 빌드
```

</details>

<details>
<summary><strong>Q2: Jenkins Pipeline의 Declarative vs Scripted, 어떤 것을 사용해야 하나요?</strong></summary>

### 상세 답변

**Declarative Pipeline (권장):**

```groovy
// Declarative: 구조화되고 읽기 쉬움
pipeline {
    agent any

    environment {
        VERSION = '1.0.0'
    }

    stages {
        stage('Build') {
            steps {
                sh './gradlew build'
            }
        }

        stage('Test') {
            steps {
                sh './gradlew test'
            }
        }
    }

    post {
        always {
            junit '**/test-results/**/*.xml'
        }
    }
}

✅ 장점:
- 읽기 쉽고 이해하기 쉬움
- 구조가 명확 (pipeline, agent, stages, steps, post)
- Blue Ocean과 완벽 호환
- Syntax 검증 기능
- 초보자 친화적
- 대부분의 use case 커버

❌ 단점:
- 복잡한 로직 구현 제한적
- script {} 블록 필요한 경우 있음
```

**Scripted Pipeline (유연함):**

```groovy
// Scripted: Groovy 코드로 자유로운 구현
node {
    def version = '1.0.0'

    try {
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
        junit '**/test-results/**/*.xml'
    }
}

✅ 장점:
- 매우 높은 유연성
- 복잡한 로직 구현 가능
- Groovy의 모든 기능 사용
- 조건문, 반복문 자유롭게 사용

❌ 단점:
- 코드가 복잡해질 수 있음
- Groovy 지식 필요
- Blue Ocean 지원 제한적
- 디버깅 어려움
```

**언제 어떤 것을 사용하나요?**

```
Declarative 사용 (대부분의 경우):
✅ 일반적인 CI/CD 파이프라인
✅ 표준화된 프로세스
✅ 팀 협업 (읽기 쉬움)
✅ Blue Ocean 사용
✅ 초보자

Scripted 사용 (특수한 경우):
✅ 매우 복잡한 로직 필요
✅ 동적 파이프라인 생성
✅ 고급 Groovy 기능 필요
✅ 레거시 파이프라인 (이미 Scripted로 작성됨)
```

**Declarative에서 복잡한 로직 구현:**

```groovy
// Declarative + script 블록 조합 (Best Practice)
pipeline {
    agent any

    stages {
        stage('Complex Logic') {
            steps {
                script {
                    // Groovy 코드 자유롭게 사용
                    def services = ['user', 'trade', 'account', 'strategy']

                    for (service in services) {
                        echo "Building ${service}-service..."
                        sh "./gradlew :${service}:build"

                        // 조건문
                        if (env.BRANCH_NAME == 'main') {
                            echo "Deploying ${service} to production..."
                            sh "./deploy-${service}.sh production"
                        } else {
                            echo "Deploying ${service} to staging..."
                            sh "./deploy-${service}.sh staging"
                        }
                    }

                    // 함수 호출
                    def version = calculateVersion()
                    currentBuild.description = "Version: ${version}"
                }
            }
        }
    }
}

def calculateVersion() {
    def gitCommit = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
    def timestamp = new Date().format('yyyyMMdd-HHmmss')
    return "${timestamp}-${gitCommit}"
}
```

**실전 비교:**

```groovy
// ====================================
// Declarative: 간단한 파이프라인
// ====================================
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh './gradlew build'
            }
        }
    }

    post {
        success {
            echo 'Build succeeded!'
        }
    }
}

// ====================================
// Scripted: 동일한 로직
// ====================================
node {
    try {
        stage('Build') {
            sh './gradlew build'
        }
        echo 'Build succeeded!'
    } catch (Exception e) {
        echo 'Build failed!'
        throw e
    }
}
```

**복잡한 시나리오:**

```groovy
// Declarative로 복잡한 Blue-Green 배포
pipeline {
    agent any

    environment {
        DEPLOY_HOST = credentials('deploy-host')
    }

    stages {
        stage('Determine Current Color') {
            steps {
                script {
                    env.CURRENT_COLOR = sh(
                        script: "ssh ${DEPLOY_HOST} 'cat /opt/app/current-color'",
                        returnStdout: true
                    ).trim()

                    env.NEW_COLOR = env.CURRENT_COLOR == 'blue' ? 'green' : 'blue'
                    echo "Current: ${env.CURRENT_COLOR}, New: ${env.NEW_COLOR}"
                }
            }
        }

        stage('Deploy to New Color') {
            steps {
                script {
                    sh "ssh ${DEPLOY_HOST} 'bash /opt/app/deploy-${env.NEW_COLOR}.sh'"
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    def port = env.NEW_COLOR == 'blue' ? '8080' : '8081'
                    def maxRetries = 10

                    for (int i = 0; i < maxRetries; i++) {
                        def status = sh(
                            script: "curl -f http://${DEPLOY_HOST}:${port}/health",
                            returnStatus: true
                        )

                        if (status == 0) {
                            echo "Health check passed!"
                            return
                        }

                        echo "Attempt ${i + 1}/${maxRetries} failed, retrying..."
                        sleep(time: 10, unit: 'SECONDS')
                    }

                    error "Health check failed after ${maxRetries} attempts"
                }
            }
        }

        stage('Switch Traffic') {
            steps {
                input message: "Switch traffic to ${env.NEW_COLOR}?", ok: 'Switch'

                script {
                    sh "ssh ${DEPLOY_HOST} 'bash /opt/app/switch-to-${env.NEW_COLOR}.sh'"
                    sh "ssh ${DEPLOY_HOST} 'echo ${env.NEW_COLOR} > /opt/app/current-color'"
                }
            }
        }
    }

    post {
        failure {
            script {
                // 실패 시 롤백
                sh "ssh ${DEPLOY_HOST} 'bash /opt/app/rollback.sh'"
            }
        }
    }
}
```

**권장 사항:**

```
1. 기본은 Declarative 사용
2. 복잡한 로직은 script {} 블록 활용
3. 매우 복잡하면 Groovy 함수로 분리
4. Shared Library로 재사용 가능한 코드 관리
5. 가독성 최우선
```

</details>

<details>
<summary><strong>Q3: Jenkins Shared Library는 무엇이고 어떻게 사용하나요?</strong></summary>

### 상세 답변

**Shared Library란?**

여러 파이프라인에서 공통으로 사용하는 Groovy 코드를 라이브러리로 만들어 재사용하는 기능입니다.

**구조:**

```
shared-library/
├── vars/
│   ├── buildDockerImage.groovy    # Global 변수/함수
│   ├── deployToK8s.groovy
│   └── sendSlackNotification.groovy
├── src/
│   └── com/
│       └── company/
│           └── jenkins/
│               ├── Docker.groovy   # 클래스
│               └── Deploy.groovy
└── resources/
    ├── templates/
    │   └── deployment.yaml
    └── scripts/
        └── health-check.sh
```

**1. Shared Library 생성:**

```groovy
// vars/buildDockerImage.groovy
def call(String serviceName, String registry = 'ghcr.io') {
    def imageName = "${registry}/lk-trade/${serviceName}"
    def imageTag = "${env.BRANCH_NAME}-${env.GIT_COMMIT_SHORT}"

    echo "Building Docker image: ${imageName}:${imageTag}"

    sh """
        docker build -t ${imageName}:${imageTag} \
            -t ${imageName}:latest \
            --build-arg BUILD_DATE=\$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
            --build-arg VCS_REF=${env.GIT_COMMIT} \
            modules/${serviceName}/api
    """

    return "${imageName}:${imageTag}"
}
```

```groovy
// vars/deployToEnvironment.groovy
def call(String environment, String service, String version) {
    def host = environment == 'production' ? 'prod.lk-trade.com' : 'staging.lk-trade.com'

    withCredentials([sshUserPrivateKey(
        credentialsId: "${environment}-ssh-key",
        keyFileVariable: 'SSH_KEY',
        usernameVariable: 'SSH_USER'
    )]) {
        sh """
            ssh -i ${SSH_KEY} ${SSH_USER}@${host} \
                'cd /opt/lk-trade && \
                 export SERVICE=${service} && \
                 export VERSION=${version} && \
                 docker-compose pull \$SERVICE && \
                 docker-compose up -d \$SERVICE'
        """
    }

    // Health check
    sleep(time: 30, unit: 'SECONDS')

    def healthUrl = "https://${host}/api/${service}/actuator/health"
    def status = sh(
        script: "curl -f ${healthUrl}",
        returnStatus: true
    )

    if (status != 0) {
        error "Health check failed for ${service} on ${environment}"
    }

    echo "✅ ${service} deployed successfully to ${environment}"
}
```

```groovy
// vars/sendSlackNotification.groovy
def call(String status, Map params = [:]) {
    def defaultParams = [
        channel: '#deployments',
        teamDomain: 'your-team',
        tokenCredentialId: 'slack-token'
    ]

    def mergedParams = defaultParams + params

    def color = status == 'SUCCESS' ? 'good' : 'danger'
    def emoji = status == 'SUCCESS' ? '✅' : '❌'

    slackSend(
        channel: mergedParams.channel,
        color: color,
        message: """
            ${emoji} *${status}*
            Job: ${env.JOB_NAME}
            Build: #${env.BUILD_NUMBER}
            Branch: ${env.BRANCH_NAME}
            Author: ${env.GIT_AUTHOR}
            URL: ${env.BUILD_URL}
        """.stripIndent(),
        teamDomain: mergedParams.teamDomain,
        tokenCredentialId: mergedParams.tokenCredentialId
    )
}
```

**2. Jenkins 설정:**

```
Jenkins 관리 > System

Global Pipeline Libraries:
- Name: lk-trade-library
- Default version: main
- Retrieval method: Modern SCM
  - Source Code Management: Git
    - Project Repository: https://github.com/your-org/jenkins-shared-library.git
    - Credentials: github-token
```

**3. Jenkinsfile에서 사용:**

```groovy
// Jenkinsfile
@Library('lk-trade-library') _

pipeline {
    agent any

    environment {
        GIT_COMMIT_SHORT = sh(
            script: 'git rev-parse --short HEAD',
            returnStdout: true
        ).trim()
    }

    stages {
        stage('Build Images') {
            steps {
                script {
                    def services = ['user-service', 'trade-service', 'account-service']

                    services.each { service ->
                        // Shared Library 함수 호출
                        def imageTag = buildDockerImage(service)
                        echo "Built: ${imageTag}"
                    }
                }
            }
        }

        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                script {
                    deployToEnvironment('staging', 'user-service', env.GIT_COMMIT_SHORT)
                    deployToEnvironment('staging', 'trade-service', env.GIT_COMMIT_SHORT)
                }
            }
        }

        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'

                script {
                    deployToEnvironment('production', 'user-service', env.GIT_COMMIT_SHORT)
                    deployToEnvironment('production', 'trade-service', env.GIT_COMMIT_SHORT)
                }
            }
        }
    }

    post {
        success {
            sendSlackNotification('SUCCESS')
        }

        failure {
            sendSlackNotification('FAILURE', [channel: '#alerts'])
        }
    }
}
```

**고급 기능 - 클래스 사용:**

```groovy
// src/com/company/jenkins/Docker.groovy
package com.company.jenkins

class Docker implements Serializable {
    def script

    Docker(script) {
        this.script = script
    }

    def buildAndPush(String serviceName, String registry, String tag) {
        def imageName = "${registry}/lk-trade/${serviceName}"

        script.echo "Building ${serviceName}..."

        script.sh """
            docker build -t ${imageName}:${tag} modules/${serviceName}/api
            docker push ${imageName}:${tag}
        """

        return "${imageName}:${tag}"
    }

    def scan(String imageName) {
        script.echo "Scanning ${imageName}..."

        script.sh """
            docker run --rm \
                aquasec/trivy:latest image \
                --severity HIGH,CRITICAL \
                --exit-code 1 \
                ${imageName}
        """
    }
}
```

```groovy
// Jenkinsfile에서 클래스 사용
@Library('lk-trade-library') _

import com.company.jenkins.Docker

pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                script {
                    def docker = new Docker(this)

                    def image = docker.buildAndPush(
                        'user-service',
                        'ghcr.io',
                        "${env.BRANCH_NAME}-${env.GIT_COMMIT_SHORT}"
                    )

                    docker.scan(image)
                }
            }
        }
    }
}
```

**Resources 사용:**

```groovy
// vars/deployToK8s.groovy
def call(String service, String namespace) {
    // resources/templates/deployment.yaml 로드
    def deploymentTemplate = libraryResource 'templates/deployment.yaml'

    // 템플릿 치환
    def deployment = deploymentTemplate
        .replace('{{SERVICE}}', service)
        .replace('{{NAMESPACE}}', namespace)
        .replace('{{IMAGE}}', env.IMAGE_TAG)

    // 파일로 저장
    writeFile file: 'deployment.yaml', text: deployment

    // Kubernetes 배포
    sh 'kubectl apply -f deployment.yaml'

    // Health check 스크립트 실행
    def healthCheckScript = libraryResource 'scripts/health-check.sh'
    writeFile file: 'health-check.sh', text: healthCheckScript
    sh 'chmod +x health-check.sh && ./health-check.sh'
}
```

**장점:**

1. **코드 재사용**: DRY 원칙 적용
2. **중앙 관리**: 공통 로직을 한 곳에서 관리
3. **일관성**: 모든 파이프라인이 동일한 방식으로 작동
4. **유지보수성**: 수정 사항을 한 번에 모든 파이프라인에 반영
5. **테스트 용이성**: 라이브러리를 독립적으로 테스트 가능

**Best Practices:**

```
1. 함수는 단일 책임 원칙 적용
2. 파라미터는 명확하게 문서화
3. 에러 처리 철저히
4. 버전 관리 (Git tags)
5. 단위 테스트 작성
```

</details>

<details>
<summary><strong>Q4: Jenkins 성능 최적화 방법은?</strong></summary>

### 상세 답변

**성능 문제 증상:**

```
❌ 빌드가 너무 느림 (30분+)
❌ Jenkins UI가 느림
❌ 빌드 대기 시간이 김
❌ Agent가 자주 오프라인됨
❌ 디스크 공간 부족
```

**1. 빌드 시간 최적화:**

```groovy
// ❌ 느린 파이프라인
pipeline {
    agent any

    stages {
        stage('Test User') {
            steps {
                sh './gradlew :user:test'
            }
        }
        stage('Test Trade') {
            steps {
                sh './gradlew :trade:test'
            }
        }
        stage('Test Account') {
            steps {
                sh './gradlew :account:test'
            }
        }
    }
}
// 총 시간: 15분 (5분 × 3)

// ✅ 병렬 실행으로 최적화
pipeline {
    agent any

    stages {
        stage('Tests') {
            parallel {
                stage('Test User') {
                    steps {
                        sh './gradlew :user:test'
                    }
                }
                stage('Test Trade') {
                    steps {
                        sh './gradlew :trade:test'
                    }
                }
                stage('Test Account') {
                    steps {
                        sh './gradlew :account:test'
                    }
                }
            }
        }
    }
}
// 총 시간: 5분 (병렬 실행)
```

**2. Gradle 캐싱:**

```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                // Gradle 캐싱 활성화
                sh '''
                    ./gradlew build \
                        --build-cache \
                        --configuration-cache \
                        --parallel \
                        --max-workers=4
                '''
            }
        }
    }
}

// gradle.properties 설정
org.gradle.caching=true
org.gradle.parallel=true
org.gradle.daemon=false  # CI에서는 daemon 비활성화
```

**3. Docker 레이어 캐싱:**

```groovy
pipeline {
    agent any

    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    // BuildKit 활성화
                    sh '''
                        DOCKER_BUILDKIT=1 docker build \
                            --cache-from ghcr.io/lk-trade/user-service:latest \
                            --build-arg BUILDKIT_INLINE_CACHE=1 \
                            -t ghcr.io/lk-trade/user-service:${BUILD_NUMBER} \
                            .
                    '''
                }
            }
        }
    }
}
```

**4. Agent 분산 빌드:**

```groovy
// 특정 라벨의 Agent에서 실행
pipeline {
    agent none  // 기본 agent 없음

    stages {
        stage('Build') {
            agent {
                label 'linux && gradle'  # linux 이고 gradle이 설치된 agent
            }
            steps {
                sh './gradlew build'
            }
        }

        stage('Deploy') {
            agent {
                label 'deploy-server'  # 배포 전용 agent
            }
            steps {
                sh './deploy.sh'
            }
        }
    }
}
```

**5. 워크스페이스 정리:**

```groovy
pipeline {
    agent any

    options {
        // 빌드 히스토리 제한
        buildDiscarder(logRotator(
            numToKeepStr: '10',           # 최근 10개 빌드만 유지
            artifactNumToKeepStr: '5'     # Artifact는 5개만
        ))

        // 동시 빌드 방지
        disableConcurrentBuilds()

        // 타임아웃 설정
        timeout(time: 1, unit: 'HOURS')
    }

    stages {
        stage('Build') {
            steps {
                sh './gradlew build'
            }
        }
    }

    post {
        always {
            // 워크스페이스 정리
            cleanWs()
        }
    }
}
```

**6. Jenkins 시스템 설정:**

```
Jenkins 관리 > System

# 1. Executor 수 증가
Number of executors: 4
(CPU 코어 수에 맞게 설정)

# 2. 빌드 히스토리 제한
Default Days to Keep Builds: 30
Default Max # of Builds to Keep: 100

# 3. Quiet period
Quiet period: 5
(연속된 커밋을 하나로 묶어 빌드)
```

**7. 플러그인 최적화:**

```
Jenkins 관리 > Plugins

# 불필요한 플러그인 제거
# 자주 사용하는 플러그인만 유지

# 권장 플러그인:
✅ Pipeline
✅ Git
✅ Docker Pipeline
✅ Credentials Binding
✅ Blue Ocean

❌ 오래되고 사용 안 하는 플러그인 제거
```

**8. 디스크 공간 관리:**

```bash
# Jenkins 홈 디렉토리 정리 스크립트
#!/bin/bash
# cleanup-jenkins.sh

JENKINS_HOME=/var/jenkins_home

# 오래된 빌드 삭제 (30일 이상)
find $JENKINS_HOME/jobs/*/builds/*/log \
    -mtime +30 -type f -delete

# 오래된 워크스페이스 정리
find $JENKINS_HOME/workspace/* \
    -mtime +7 -type d -exec rm -rf {} +

# Docker 이미지 정리
docker system prune -af --volumes

# 디스크 사용량 확인
df -h $JENKINS_HOME
```

**9. 모니터링:**

```groovy
// 빌드 시간 측정
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                script {
                    def startTime = System.currentTimeMillis()

                    sh './gradlew build'

                    def endTime = System.currentTimeMillis()
                    def duration = (endTime - startTime) / 1000

                    echo "Build took ${duration} seconds"

                    // Grafana/Prometheus로 메트릭 전송
                    sh """
                        curl -X POST http://prometheus-pushgateway:9091/metrics/job/jenkins \
                            --data-binary @- << EOF
                        jenkins_build_duration_seconds{job="${env.JOB_NAME}"} ${duration}
                        EOF
                    """
                }
            }
        }
    }
}
```

**10. 성능 체크리스트:**

```
✅ 병렬 실행 사용
✅ Gradle/Maven 캐싱
✅ Docker 빌드 캐싱
✅ Agent 라벨링 및 분산
✅ 워크스페이스 정리
✅ 빌드 히스토리 제한
✅ 불필요한 플러그인 제거
✅ Executor 수 최적화
✅ 디스크 공간 모니터링
✅ 빌드 타임아웃 설정

❌ 순차 실행
❌ 캐싱 없음
❌ 무제한 빌드 히스토리
❌ 워크스페이스 누적
❌ 너무 많은 플러그인
```

**실제 최적화 예시:**

```
최적화 전:
- 총 빌드 시간: 45분
- 테스트: 20분 (순차)
- Docker 빌드: 15분 (캐싱 없음)
- 배포: 10분

최적화 후:
- 총 빌드 시간: 12분
- 테스트: 5분 (병렬)
- Docker 빌드: 3분 (캐싱)
- 배포: 4분

시간 절감: 73%
```

</details>

<details>
<summary><strong>Q5: Jenkins 백업 및 복구 전략은?</strong></summary>

### 상세 답변

**백업이 필요한 데이터:**

```
JENKINS_HOME/
├── config.xml                  # Jenkins 시스템 설정
├── credentials.xml             # Credential 정보
├── jobs/                       # Job 설정
│   ├── my-pipeline/
│   │   └── config.xml
│   └── ...
├── plugins/                    # 설치된 플러그인
├── users/                      # 사용자 정보
├── secrets/                    # Secret 키
└── fingerprints/               # Build fingerprints

⚠️  백업 불필요:
- workspace/                    # 워크스페이스 (재생성 가능)
- builds/*/log                  # 빌드 로그 (용량 큼)
- caches/                       # 캐시 (재생성 가능)
```

**1. 전체 백업 스크립트:**

```bash
#!/bin/bash
# scripts/backup-jenkins.sh

JENKINS_HOME=/var/jenkins_home
BACKUP_DIR=/backups/jenkins
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="jenkins-backup-$DATE.tar.gz"

echo "🔄 Starting Jenkins backup..."

# Jenkins 백업 (제외 항목 포함)
docker exec jenkins tar czf - \
    --exclude='workspace/*' \
    --exclude='*/builds/*/log' \
    --exclude='caches/*' \
    --exclude='logs/*' \
    --exclude='*.log' \
    /var/jenkins_home \
    > "$BACKUP_DIR/$BACKUP_FILE"

# 백업 파일 압축 확인
if [ $? -eq 0 ]; then
    echo "✅ Backup completed: $BACKUP_FILE"

    # 파일 크기 확인
    du -h "$BACKUP_DIR/$BACKUP_FILE"

    # 오래된 백업 삭제 (30일 이상)
    find $BACKUP_DIR -name "jenkins-backup-*.tar.gz" -mtime +30 -delete
    echo "Cleaned up old backups"
else
    echo "❌ Backup failed!"
    exit 1
fi

# S3에 업로드 (선택사항)
aws s3 cp "$BACKUP_DIR/$BACKUP_FILE" s3://my-backups/jenkins/

echo "✅ Backup uploaded to S3"
```

**2. 증분 백업 (Job 설정만):**

```bash
#!/bin/bash
# scripts/backup-jobs.sh

JENKINS_HOME=/var/jenkins_home
BACKUP_DIR=/backups/jenkins/jobs
DATE=$(date +%Y%m%d-%H%M%S)

echo "🔄 Backing up Jenkins jobs..."

# Job 설정만 백업
docker exec jenkins tar czf - \
    /var/jenkins_home/jobs \
    > "$BACKUP_DIR/jobs-$DATE.tar.gz"

# Git으로 버전 관리
cd $BACKUP_DIR
tar xzf "jobs-$DATE.tar.gz"
git add .
git commit -m "Backup jobs - $DATE"
git push origin main

echo "✅ Jobs backed up and pushed to Git"
```

**3. 자동 백업 (Cron):**

```bash
# /etc/cron.d/jenkins-backup

# 매일 새벽 2시 전체 백업
0 2 * * * root /opt/jenkins/scripts/backup-jenkins.sh >> /var/log/jenkins-backup.log 2>&1

# 매 시간 Job 설정 백업
0 * * * * root /opt/jenkins/scripts/backup-jobs.sh >> /var/log/jenkins-jobs-backup.log 2>&1
```

**4. Jenkins Plugin 백업:**

```bash
#!/bin/bash
# scripts/backup-plugins.sh

JENKINS_HOME=/var/jenkins_home
BACKUP_DIR=/backups/jenkins/plugins

# 설치된 플러그인 목록 저장
docker exec jenkins java -jar /usr/share/jenkins/jenkins-cli.jar \
    -s http://localhost:8080/ \
    -auth admin:$(cat /var/jenkins_home/secrets/initialAdminPassword) \
    list-plugins \
    > "$BACKUP_DIR/plugins-$(date +%Y%m%d).txt"

echo "✅ Plugin list saved"
```

**5. 복구 스크립트:**

```bash
#!/bin/bash
# scripts/restore-jenkins.sh

if [ -z "$1" ]; then
    echo "Usage: $0 <backup-file>"
    echo "Available backups:"
    ls -lh /backups/jenkins/jenkins-backup-*.tar.gz
    exit 1
fi

BACKUP_FILE=$1

echo "🔄 Restoring Jenkins from $BACKUP_FILE..."

# Jenkins 중지
docker-compose -f docker-compose.jenkins.yml stop jenkins

# 기존 데이터 백업 (안전을 위해)
docker run --rm \
    -v jenkins-data:/var/jenkins_home \
    -v $(pwd):/backup \
    alpine \
    tar czf /backup/jenkins-pre-restore-$(date +%Y%m%d-%H%M%S).tar.gz /var/jenkins_home

# 데이터 복구
docker run --rm \
    -v jenkins-data:/var/jenkins_home \
    -v $(pwd):/backup \
    alpine \
    sh -c "cd /var/jenkins_home && tar xzf /backup/$BACKUP_FILE --strip-components=2"

# Jenkins 시작
docker-compose -f docker-compose.jenkins.yml start jenkins

echo "⏳ Waiting for Jenkins to start..."
sleep 30

# 헬스 체크
curl -f http://localhost:8080/login || {
    echo "❌ Jenkins failed to start!"
    exit 1
}

echo "✅ Jenkins restored successfully!"
```

**6. Disaster Recovery Plan:**

```bash
#!/bin/bash
# scripts/disaster-recovery.sh

echo "🚨 Initiating Disaster Recovery..."

# 1. 최신 백업 다운로드
aws s3 cp s3://my-backups/jenkins/latest/ . --recursive

# 2. Jenkins 재설치
docker-compose -f docker-compose.jenkins.yml down -v
docker-compose -f docker-compose.jenkins.yml up -d

# 3. 백업 복구
LATEST_BACKUP=$(ls -t jenkins-backup-*.tar.gz | head -1)
./scripts/restore-jenkins.sh $LATEST_BACKUP

# 4. 플러그인 재설치
PLUGIN_LIST=$(ls -t plugins-*.txt | head -1)
while read plugin; do
    echo "Installing $plugin..."
    docker exec jenkins java -jar /usr/share/jenkins/jenkins-cli.jar \
        -s http://localhost:8080/ \
        install-plugin $plugin
done < $PLUGIN_LIST

# 5. Jenkins 재시작
docker-compose -f docker-compose.jenkins.yml restart jenkins

echo "✅ Disaster recovery completed!"
```

**7. Configuration as Code (JCasC):**

```yaml
# jenkins.yaml
jenkins:
  systemMessage: "LK-Trade Jenkins Server"
  numExecutors: 4
  mode: NORMAL

  securityRealm:
    local:
      allowsSignup: false
      users:
        - id: "admin"
          password: "${JENKINS_ADMIN_PASSWORD}"

  authorizationStrategy:
    globalMatrix:
      permissions:
        - "Overall/Administer:admin"
        - "Overall/Read:authenticated"

credentials:
  system:
    domainCredentials:
      - credentials:
          - usernamePassword:
              scope: GLOBAL
              id: "github-token"
              username: "${GITHUB_USERNAME}"
              password: "${GITHUB_TOKEN}"
          - string:
              scope: GLOBAL
              id: "slack-token"
              secret: "${SLACK_TOKEN}"

unclassified:
  location:
    url: "https://jenkins.lk-trade.com"

  slackNotifier:
    teamDomain: "your-team"
    tokenCredentialId: "slack-token"
```

**8. 백업 검증:**

```bash
#!/bin/bash
# scripts/verify-backup.sh

BACKUP_FILE=$1

echo "🔍 Verifying backup: $BACKUP_FILE"

# 압축 파일 무결성 확인
tar tzf $BACKUP_FILE > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Archive is valid"
else
    echo "❌ Archive is corrupted!"
    exit 1
fi

# 필수 파일 확인
REQUIRED_FILES=(
    "var/jenkins_home/config.xml"
    "var/jenkins_home/jobs"
    "var/jenkins_home/credentials.xml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if tar tzf $BACKUP_FILE | grep -q "$file"; then
        echo "✅ $file found"
    else
        echo "❌ $file missing!"
        exit 1
    fi
done

echo "✅ Backup verification passed!"
```

**9. Best Practices:**

```
✅ 매일 자동 백업
✅ 오프사이트 저장 (S3, Azure Blob)
✅ 백업 암호화
✅ 정기적인 복구 테스트 (월 1회)
✅ 백업 모니터링
✅ 다중 백업 (로컬 + 클라우드)
✅ Configuration as Code 사용
✅ Job 설정 Git 관리

❌ 워크스페이스 백업 (불필요)
❌ 빌드 로그 백업 (용량 큼)
❌ 백업 검증 안 함
❌ 단일 백업 위치
```

**10. 복구 테스트 계획:**

```
분기별 복구 테스트:

1. 테스트 환경 준비
   - 새로운 서버 또는 Docker 컨테이너

2. 최신 백업으로 복구 수행

3. 검증:
   ✅ Jenkins 접속 가능
   ✅ 모든 Job 존재
   ✅ Credential 복구 확인
   ✅ 플러그인 정상 작동
   ✅ Pipeline 실행 테스트

4. 복구 시간 측정 (RTO)
   - 목표: 1시간 이내

5. 데이터 손실 확인 (RPO)
   - 목표: 1시간 이내 데이터

6. 문제점 문서화 및 개선
```

</details>

---

## 📝 면접 질문

### 주니어 레벨

<details>
<summary><strong>Q1: Jenkins Pipeline의 기본 구조를 설명하고, 간단한 CI 파이프라인을 작성해보세요.</strong></summary>

### 답변

**Jenkins Pipeline 기본 구조:**

Jenkins Pipeline은 크게 **Declarative**와 **Scripted** 두 가지 문법이 있습니다. 초보자에게는 Declarative를 권장합니다.

**Declarative Pipeline 구조:**

```groovy
pipeline {
    agent         // 어디서 실행할지
    environment   // 환경 변수
    tools         // 도구 (JDK, Maven 등)
    options       // 파이프라인 옵션
    stages {      // 실행 단계들
        stage     // 개별 단계
    }
    post {        // 파이프라인 완료 후 작업
        always
        success
        failure
    }
}
```

**간단한 CI 파이프라인 예시:**

```groovy
// Jenkinsfile
pipeline {
    // 1. Agent: 어느 Jenkins agent에서 실행할지
    agent any

    // 2. Tools: JDK 버전 지정
    tools {
        jdk 'JDK17'
    }

    // 3. Environment: 환경 변수
    environment {
        APP_NAME = 'my-app'
        VERSION = '1.0.0'
    }

    // 4. Stages: 실행할 단계들
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo "Building ${APP_NAME} v${VERSION}..."
                sh './gradlew clean build'
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                sh './gradlew test'
            }
        }

        stage('Package') {
            steps {
                echo 'Packaging application...'
                sh './gradlew bootJar'
            }
        }
    }

    // 5. Post: 파이프라인 완료 후 작업
    post {
        always {
            echo 'Cleaning up...'
            cleanWs()
        }

        success {
            echo "✅ ${APP_NAME} v${VERSION} build succeeded!"
            // JUnit 테스트 결과 발행
            junit '**/build/test-results/test/*.xml'
        }

        failure {
            echo "❌ ${APP_NAME} v${VERSION} build failed!"
        }
    }
}
```

**실행 흐름:**

```
Push to Git
    ↓
Jenkins Webhook 트리거
    ↓
┌─────────────────────┐
│ Checkout            │  코드 체크아웃
└─────────────────────┘
    ↓
┌─────────────────────┐
│ Build               │  Gradle 빌드
└─────────────────────┘
    ↓
┌─────────────────────┐
│ Test                │  단위 테스트 실행
└─────────────────────┘
    ↓
┌─────────────────────┐
│ Package             │  JAR 파일 생성
└─────────────────────┘
    ↓
Post Actions (항상 실행)
```

**핵심 개념:**

1. **agent**: 파이프라인을 실행할 위치
   - `agent any`: 사용 가능한 아무 agent
   - `agent { label 'linux' }`: 특정 라벨의 agent

2. **stages**: 논리적 단계 묶음

3. **steps**: 실제 실행할 명령들

4. **post**: 파이프라인 완료 후 실행
   - `always`: 항상 실행
   - `success`: 성공 시만
   - `failure`: 실패 시만

**실행 결과:**

```
[Pipeline] Start of Pipeline
[Pipeline] node
[Pipeline] {
[Pipeline] stage (Checkout)
Checking out code...
Cloning repository...
[Pipeline] }

[Pipeline] stage (Build)
Building my-app v1.0.0...
BUILD SUCCESSFUL in 30s
[Pipeline] }

[Pipeline] stage (Test)
Running tests...
45 tests passed
[Pipeline] }

[Pipeline] stage (Package)
Packaging application...
Created my-app-1.0.0.jar
[Pipeline] }

[Pipeline] post
✅ my-app v1.0.0 build succeeded!
[Pipeline] End of Pipeline
Finished: SUCCESS
```

</details>

<details>
<summary><strong>Q2: Jenkins에서 Credential을 안전하게 관리하고 사용하는 방법을 설명하세요.</strong></summary>

### 답변

**Jenkins Credential 개념:**

Jenkins Credential은 비밀번호, API 키, SSH 키 등 민감한 정보를 안전하게 저장하고 파이프라인에서 사용할 수 있게 해주는 기능입니다.

**Credential 종류:**

```
1. Username with password     - 사용자명/비밀번호
2. SSH Username with private key - SSH 키
3. Secret text                - API 키, 토큰 등
4. Secret file                - 인증서 파일 등
5. Certificate                - TLS/SSL 인증서
```

**Credential 추가 방법:**

```
1. Jenkins > Credentials > System > Global credentials
2. "Add Credentials" 클릭
3. Kind 선택 (예: Username with password)
4. 정보 입력:
   - Username: admin
   - Password: mypassword
   - ID: github-credentials
   - Description: GitHub Personal Access Token
5. "OK" 클릭
```

**파이프라인에서 사용:**

**1. Username with password:**

```groovy
pipeline {
    agent any

    stages {
        stage('Deploy') {
            steps {
                // withCredentials로 사용
                withCredentials([
                    usernamePassword(
                        credentialsId: 'github-credentials',
                        usernameVariable: 'USERNAME',
                        passwordVariable: 'PASSWORD'
                    )
                ]) {
                    sh """
                        echo "Deploying as $USERNAME"
                        # PASSWORD는 로그에서 마스킹됨: ***
                        curl -u $USERNAME:$PASSWORD https://api.github.com
                    """
                }
            }
        }
    }
}
```

**2. SSH Username with private key:**

```groovy
pipeline {
    agent any

    stages {
        stage('Deploy') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'deploy-ssh-key',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {
                    sh """
                        ssh -i $SSH_KEY $SSH_USER@production-server.com \
                            'cd /opt/app && ./deploy.sh'
                    """
                }
            }
        }
    }
}
```

**3. Secret text:**

```groovy
pipeline {
    agent any

    stages {
        stage('Notify') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'slack-token',
                        variable: 'SLACK_TOKEN'
                    )
                ]) {
                    sh """
                        curl -X POST https://slack.com/api/chat.postMessage \
                            -H "Authorization: Bearer $SLACK_TOKEN" \
                            -d '{"channel":"#deployments","text":"Deployed!"}'
                    """
                }
            }
        }
    }
}
```

**4. 여러 Credential 동시 사용:**

```groovy
pipeline {
    agent any

    stages {
        stage('Deploy') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'db-credentials',
                        usernameVariable: 'DB_USER',
                        passwordVariable: 'DB_PASSWORD'
                    ),
                    string(
                        credentialsId: 'api-key',
                        variable: 'API_KEY'
                    ),
                    sshUserPrivateKey(
                        credentialsId: 'deploy-key',
                        keyFileVariable: 'SSH_KEY'
                    )
                ]) {
                    sh """
                        echo "Deploying with DB: $DB_USER"
                        echo "API Key: $API_KEY"
                        ssh -i $SSH_KEY deploy@server.com './deploy.sh'
                    """
                }
            }
        }
    }
}
```

**로그에서의 보안:**

```
[Pipeline] withCredentials
Masking supported pattern matches of $PASSWORD
[Pipeline] {
[Pipeline] sh
+ echo 'Deploying as admin'
Deploying as admin
+ curl -u admin:*** https://api.github.com
# 비밀번호는 자동으로 *** 로 마스킹됨!
```

**Environment Credential Binding:**

```groovy
pipeline {
    agent any

    environment {
        // Credential을 환경 변수로 바인딩
        DOCKER_CREDENTIALS = credentials('docker-hub-credentials')
        // 자동으로 _USR과 _PSW 변수 생성
    }

    stages {
        stage('Docker Login') {
            steps {
                sh """
                    echo $DOCKER_CREDENTIALS_PSW | \
                        docker login -u $DOCKER_CREDENTIALS_USR --password-stdin
                """
            }
        }
    }
}
```

**보안 Best Practices:**

```groovy
pipeline {
    agent any

    stages {
        stage('Secure Deploy') {
            steps {
                script {
                    // ❌ 잘못된 방법: Credential을 직접 출력
                    // withCredentials([string(credentialsId: 'api-key', variable: 'KEY')]) {
                    //     sh "echo $KEY"  # 절대 하면 안 됨!
                    // }

                    // ✅ 올바른 방법: Credential을 직접 출력하지 않음
                    withCredentials([string(credentialsId: 'api-key', variable: 'API_KEY')]) {
                        sh """
                            # API_KEY를 사용하되 출력하지 않음
                            curl -H "Authorization: Bearer $API_KEY" \
                                https://api.example.com/deploy
                        """
                    }
                }
            }
        }
    }
}
```

**보안 체크리스트:**

```
✅ Credential ID는 명확하게 명명
✅ Description 작성으로 용도 명시
✅ 최소 권한 원칙 적용
✅ 정기적인 Credential 교체 (90일)
✅ withCredentials 블록 최소화
✅ Credential을 로그에 출력 금지
✅ Environment별 Credential 분리

❌ Jenkinsfile에 하드코딩 금지
❌ Credential을 Git에 커밋 금지
❌ 불필요하게 넓은 scope
❌ 만료된 Credential 방치
```

**Credential Scope:**

```
Global: 모든 Job에서 사용 가능
System: Jenkins 자체 및 Agent 노드만 사용
Folder: 특정 폴더 내 Job만 사용

권장: 최소 권한 원칙에 따라 Folder scope 사용
```

</details>

---

### 중급 레벨

<details>
<summary><strong>Q3: Jenkins에서 병렬 실행을 구현하여 빌드 시간을 최적화하는 방법을 설명하고 구현하세요.</strong></summary>

### 답변

**병렬 실행이 필요한 이유:**

```
순차 실행:
Test User (5분) → Test Trade (5분) → Test Account (5분) → Test Strategy (5분)
= 총 20분

병렬 실행:
Test User (5분)
Test Trade (5분)       } 동시 실행
Test Account (5분)
Test Strategy (5분)
= 총 5분

시간 절감: 75%
```

**기본 병렬 실행:**

```groovy
pipeline {
    agent any

    stages {
        stage('Tests') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        echo 'Running unit tests...'
                        sh './gradlew test'
                    }
                }

                stage('Integration Tests') {
                    steps {
                        echo 'Running integration tests...'
                        sh './gradlew integrationTest'
                    }
                }

                stage('Code Quality') {
                    steps {
                        echo 'Running code quality checks...'
                        sh './gradlew ktlintCheck detekt'
                    }
                }
            }
        }
    }
}
```

**실행 결과 (Blue Ocean):**

```
┌─────────────────────────────────────────┐
│ Tests                                   │
├─────────────────────────────────────────┤
│ ┌─────────────────┐                    │
│ │ Unit Tests      │  5분               │
│ ├─────────────────┤                    │
│ │ Integration     │  5분  } 병렬 실행  │
│ │ Tests           │                     │
│ ├─────────────────┤                    │
│ │ Code Quality    │  5분               │
│ └─────────────────┘                    │
│                                         │
│ 총 실행 시간: 5분 (가장 긴 작업 기준) │
└─────────────────────────────────────────┘
```

**마이크로서비스 병렬 빌드:**

```groovy
pipeline {
    agent any

    stages {
        stage('Build All Services') {
            parallel {
                stage('Build User Service') {
                    steps {
                        script {
                            buildService('user-service', 'modules/user/api')
                        }
                    }
                }

                stage('Build Trade Service') {
                    steps {
                        script {
                            buildService('trade-service', 'modules/trade/api')
                        }
                    }
                }

                stage('Build Account Service') {
                    steps {
                        script {
                            buildService('account-service', 'modules/account/api')
                        }
                    }
                }

                stage('Build Strategy Service') {
                    steps {
                        script {
                            buildService('strategy-service', 'modules/strategy/api')
                        }
                    }
                }
            }
        }
    }
}

def buildService(String serviceName, String path) {
    echo "Building ${serviceName}..."

    sh """
        cd ${path}
        ./gradlew build
        docker build -t ghcr.io/lk-trade/${serviceName}:${BUILD_NUMBER} .
        docker push ghcr.io/lk-trade/${serviceName}:${BUILD_NUMBER}
    """

    echo "${serviceName} built successfully!"
}
```

**동적 병렬 실행:**

```groovy
pipeline {
    agent any

    stages {
        stage('Dynamic Parallel Build') {
            steps {
                script {
                    def services = ['user', 'trade', 'account', 'strategy']
                    def parallelStages = [:]

                    services.each { service ->
                        parallelStages["Build ${service}"] = {
                            stage("Build ${service}") {
                                echo "Building ${service}-service..."
                                sh "./gradlew :${service}:build"

                                echo "Testing ${service}-service..."
                                sh "./gradlew :${service}:test"

                                echo "Building Docker image..."
                                sh "docker build -t ghcr.io/lk-trade/${service}-service:${BUILD_NUMBER} modules/${service}/api"
                            }
                        }
                    }

                    // 병렬 실행
                    parallel parallelStages
                }
            }
        }
    }
}
```

**failFast 옵션:**

```groovy
pipeline {
    agent any

    stages {
        stage('Tests') {
            failFast true  // 하나라도 실패하면 나머지 중단

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
    }
}
```

**Agent별 병렬 실행:**

```groovy
pipeline {
    agent none  // 기본 agent 없음

    stages {
        stage('Parallel Builds') {
            parallel {
                stage('Build on Linux') {
                    agent { label 'linux' }
                    steps {
                        sh './gradlew build'
                    }
                }

                stage('Build on Windows') {
                    agent { label 'windows' }
                    steps {
                        bat 'gradlew.bat build'
                    }
                }

                stage('Build on Mac') {
                    agent { label 'macos' }
                    steps {
                        sh './gradlew build'
                    }
                }
            }
        }
    }
}
```

**복잡한 병렬 워크플로우:**

```groovy
pipeline {
    agent any

    stages {
        // 1단계: 순차 실행
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // 2단계: 병렬 빌드
        stage('Build') {
            parallel {
                stage('Build Services') {
                    stages {
                        stage('Compile') {
                            steps {
                                sh './gradlew compileJava'
                            }
                        }
                        stage('Package') {
                            steps {
                                sh './gradlew bootJar'
                            }
                        }
                    }
                }

                stage('Build Docker Images') {
                    steps {
                        script {
                            def services = ['user', 'trade', 'account']
                            services.each { service ->
                                sh "docker build -t ${service}:${BUILD_NUMBER} modules/${service}/api"
                            }
                        }
                    }
                }
            }
        }

        // 3단계: 병렬 테스트
        stage('Test') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh './gradlew test'
                    }
                    post {
                        always {
                            junit '**/build/test-results/test/*.xml'
                        }
                    }
                }

                stage('Security Scan') {
                    steps {
                        sh 'docker run --rm aquasec/trivy:latest image user:${BUILD_NUMBER}'
                    }
                }
            }
        }

        // 4단계: 순차 배포
        stage('Deploy') {
            steps {
                echo 'Deploying to staging...'
                sh './deploy-staging.sh'
            }
        }
    }
}
```

**실전 최적화 예시:**

```groovy
// 최적화 전: 45분
pipeline {
    agent any
    stages {
        stage('Test User') { steps { sh './gradlew :user:test' } }        // 5분
        stage('Test Trade') { steps { sh './gradlew :trade:test' } }      // 5분
        stage('Test Account') { steps { sh './gradlew :account:test' } }  // 5분
        stage('Test Strategy') { steps { sh './gradlew :strategy:test' } }// 5분
        stage('Build User') { steps { sh 'docker build user' } }           // 5분
        stage('Build Trade') { steps { sh 'docker build trade' } }         // 5분
        stage('Build Account') { steps { sh 'docker build account' } }     // 5분
        stage('Build Strategy') { steps { sh 'docker build strategy' } }   // 5분
        stage('Deploy') { steps { sh './deploy.sh' } }                     // 5분
    }
}

// 최적화 후: 15분
pipeline {
    agent any
    stages {
        stage('Test & Build') {
            parallel {
                stage('User') {
                    stages {
                        stage('Test') { steps { sh './gradlew :user:test' } }
                        stage('Build') { steps { sh 'docker build user' } }
                    }
                }
                stage('Trade') {
                    stages {
                        stage('Test') { steps { sh './gradlew :trade:test' } }
                        stage('Build') { steps { sh 'docker build trade' } }
                    }
                }
                stage('Account') {
                    stages {
                        stage('Test') { steps { sh './gradlew :account:test' } }
                        stage('Build') { steps { sh 'docker build account' } }
                    }
                }
                stage('Strategy') {
                    stages {
                        stage('Test') { steps { sh './gradlew :strategy:test' } }
                        stage('Build') { steps { sh 'docker build strategy' } }
                    }
                }
            }
        }
        stage('Deploy') { steps { sh './deploy.sh' } }
    }
}

시간 절감: 66% (45분 → 15분)
```

**핵심 포인트:**

1. **parallel {}**: 병렬 실행 블록
2. **failFast**: 실패 시 즉시 중단
3. **agent**: 각 병렬 스테이지마다 다른 agent 사용 가능
4. **동적 생성**: 반복문으로 병렬 스테이지 생성
5. **nested stages**: 병렬 안에 순차 스테이지 가능

</details>

<details>
<summary><strong>Q4: Jenkins에서 Docker를 활용한 CI/CD 파이프라인을 구현하세요.</strong></summary>

### 답변

**Jenkins + Docker 통합의 이점:**

```
✅ 격리된 빌드 환경
✅ 재현 가능한 빌드
✅ 빠른 환경 구성
✅ 버전별 도구 사용 가능
✅ 클린업 자동화
```

**1. Docker Agent 사용:**

```groovy
pipeline {
    agent {
        docker {
            image 'gradle:7-jdk17'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    stages {
        stage('Build') {
            steps {
                sh 'gradle --version'
                sh 'gradle build'
            }
        }
    }
}
```

**2. 스테이지별 다른 Docker 이미지:**

```groovy
pipeline {
    agent none

    stages {
        stage('Build') {
            agent {
                docker {
                    image 'gradle:7-jdk17'
                }
            }
            steps {
                sh 'gradle build'
            }
        }

        stage('Test') {
            agent {
                docker {
                    image 'gradle:7-jdk17'
                    args '-v $HOME/.gradle:/root/.gradle'  # 캐싱
                }
            }
            steps {
                sh 'gradle test'
            }
        }

        stage('Security Scan') {
            agent {
                docker {
                    image 'aquasec/trivy:latest'
                }
            }
            steps {
                sh 'trivy filesystem .'
            }
        }
    }
}
```

**3. Docker 이미지 빌드 및 푸시:**

```groovy
pipeline {
    agent any

    environment {
        REGISTRY = 'ghcr.io'
        IMAGE_NAME = 'lk-trade/user-service'
        REGISTRY_CREDENTIAL = 'github-registry-credential'
    }

    stages {
        stage('Build Application') {
            steps {
                sh './gradlew bootJar'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Docker 이미지 빌드
                    def app = docker.build(
                        "${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER}",
                        "--build-arg BUILD_DATE=\$(date -u +'%Y-%m-%dT%H:%M:%SZ') " +
                        "--build-arg VCS_REF=${GIT_COMMIT} " +
                        "."
                    )

                    // 이미지 태깅
                    app.tag('latest')
                    app.tag("${BRANCH_NAME}-${GIT_COMMIT[0..7]}")
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry("https://${REGISTRY}", REGISTRY_CREDENTIAL) {
                        def app = docker.image("${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER}")
                        app.push()
                        app.push('latest')
                        app.push("${BRANCH_NAME}-${GIT_COMMIT[0..7]}")
                    }
                }
            }
        }
    }
}
```

**4. Docker Compose로 통합 테스트:**

```groovy
pipeline {
    agent any

    stages {
        stage('Integration Tests') {
            steps {
                script {
                    try {
                        // Docker Compose로 서비스 시작
                        sh '''
                            docker-compose -f docker-compose.test.yml up -d postgres redis
                            sleep 10
                        '''

                        // 헬스 체크
                        sh '''
                            docker-compose -f docker-compose.test.yml ps
                            docker-compose -f docker-compose.test.yml logs
                        '''

                        // 통합 테스트 실행
                        docker.image('gradle:7-jdk17').inside('--network test-network') {
                            sh './gradlew integrationTest'
                        }
                    } finally {
                        // 정리
                        sh 'docker-compose -f docker-compose.test.yml down -v'
                    }
                }
            }
        }
    }
}
```

**5. Multi-stage Docker 빌드:**

```groovy
// Dockerfile
FROM gradle:7-jdk17 AS builder
WORKDIR /app
COPY . .
RUN gradle bootJar

FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=builder /app/build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]

// Jenkinsfile
pipeline {
    agent any

    stages {
        stage('Build Multi-stage Image') {
            steps {
                script {
                    def buildArgs = [
                        "--build-arg BUILD_DATE=\$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
                        "--build-arg VCS_REF=${GIT_COMMIT}",
                        "--build-arg VERSION=${BUILD_NUMBER}"
                    ].join(' ')

                    sh """
                        DOCKER_BUILDKIT=1 docker build ${buildArgs} \
                            -t ${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER} \
                            .
                    """
                }
            }
        }
    }
}
```

**6. Docker 캐싱 활용:**

```groovy
pipeline {
    agent any

    stages {
        stage('Build with Cache') {
            steps {
                script {
                    sh """
                        # BuildKit 활성화
                        export DOCKER_BUILDKIT=1

                        # 이전 이미지를 캐시로 사용
                        docker build \
                            --cache-from ${REGISTRY}/${IMAGE_NAME}:latest \
                            --build-arg BUILDKIT_INLINE_CACHE=1 \
                            -t ${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER} \
                            .
                    """
                }
            }
        }
    }
}
```

**7. 완전한 Docker CI/CD 파이프라인:**

```groovy
pipeline {
    agent any

    environment {
        REGISTRY = 'ghcr.io'
        IMAGE_NAME = 'lk-trade/user-service'
        DOCKER_BUILDKIT = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Test in Docker') {
            agent {
                docker {
                    image 'gradle:7-jdk17'
                    args '-v $HOME/.gradle:/root/.gradle'
                }
            }
            steps {
                sh 'gradle clean build test'
            }
            post {
                always {
                    junit '**/build/test-results/test/*.xml'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh """
                        docker build \
                            --cache-from ${REGISTRY}/${IMAGE_NAME}:latest \
                            --build-arg BUILDKIT_INLINE_CACHE=1 \
                            --build-arg BUILD_DATE=\$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
                            --build-arg VCS_REF=${GIT_COMMIT} \
                            -t ${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER} \
                            -t ${REGISTRY}/${IMAGE_NAME}:latest \
                            .
                    """
                }
            }
        }

        stage('Security Scan') {
            steps {
                sh """
                    docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        aquasec/trivy:latest image \
                        --severity HIGH,CRITICAL \
                        --exit-code 1 \
                        ${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER}
                """
            }
        }

        stage('Push Image') {
            steps {
                script {
                    docker.withRegistry("https://${REGISTRY}", 'github-registry-credential') {
                        sh """
                            docker push ${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER}
                            docker push ${REGISTRY}/${IMAGE_NAME}:latest
                        """
                    }
                }
            }
        }

        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                sh """
                    ssh deploy@staging.lk-trade.com \
                        'docker pull ${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER} && \
                         docker-compose up -d user-service'
                """
            }
        }
    }

    post {
        always {
            sh 'docker system prune -f'  // 사용하지 않는 이미지 정리
        }
    }
}
```

**Best Practices:**

```
✅ DOCKER_BUILDKIT=1 사용 (빠른 빌드)
✅ Multi-stage 빌드로 이미지 크기 최소화
✅ 캐싱 활용 (--cache-from)
✅ 보안 스캔 (Trivy)
✅ 태그 전략 (latest, version, commit)
✅ 정리 작업 (docker system prune)
✅ .dockerignore 사용

❌ root 사용자로 실행
❌ 너무 큰 이미지
❌ 캐싱 없이 매번 전체 빌드
❌ 취약점 스캔 생략
```

</details>

<details>
<summary><strong>Q5: Jenkins 파이프라인의 모범 사례와 안티패턴을 설명하세요.</strong></summary>

### 답변

**모범 사례 (Best Practices):**

**1. Declarative Pipeline 사용:**

```groovy
// ✅ Good: Declarative (읽기 쉽고 유지보수 용이)
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh './gradlew build'
            }
        }
    }
}

// ❌ Bad: Scripted (복잡하고 이해하기 어려움)
node {
    try {
        stage('Build') {
            sh './gradlew build'
        }
    } catch (Exception e) {
        throw e
    }
}
```

**2. Shared Library 활용:**

```groovy
// ✅ Good: 재사용 가능한 로직
@Library('lk-trade-library') _

pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                buildDockerImage('user-service')  // Shared Library 함수
            }
        }
    }
}

// ❌ Bad: 모든 파이프라인에 중복 코드
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                script {
                    // 매번 반복되는 긴 코드...
                    sh 'docker build -t ...'
                    sh 'docker push ...'
                    // ...
                }
            }
        }
    }
}
```

**3. 환경 변수 명확히:**

```groovy
// ✅ Good: 환경 변수로 설정
pipeline {
    agent any

    environment {
        REGISTRY = 'ghcr.io'
        IMAGE_NAME = 'lk-trade/user-service'
        VERSION = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Build') {
            steps {
                sh """
                    docker build -t ${REGISTRY}/${IMAGE_NAME}:${VERSION} .
                """
            }
        }
    }
}

// ❌ Bad: 하드코딩
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh """
                    docker build -t ghcr.io/lk-trade/user-service:1.0.0 .
                """
            }
        }
    }
}
```

**4. Credential 안전하게 사용:**

```groovy
// ✅ Good: withCredentials 사용
pipeline {
    agent any

    stages {
        stage('Deploy') {
            steps {
                withCredentials([
                    string(credentialsId: 'api-key', variable: 'API_KEY')
                ]) {
                    sh 'curl -H "Authorization: Bearer $API_KEY" ...'
                }
            }
        }
    }
}

// ❌ Bad: 하드코딩
pipeline {
    agent any

    stages {
        stage('Deploy') {
            steps {
                sh 'curl -H "Authorization: Bearer sk-1234567890" ...'
            }
        }
    }
}
```

**5. 병렬 실행 활용:**

```groovy
// ✅ Good: 병렬 실행으로 시간 단축
pipeline {
    agent any

    stages {
        stage('Tests') {
            parallel {
                stage('Unit') { steps { sh './gradlew test' } }
                stage('Integration') { steps { sh './gradlew integrationTest' } }
                stage('E2E') { steps { sh './gradlew e2eTest' } }
            }
        }
    }
}

// ❌ Bad: 순차 실행 (느림)
pipeline {
    agent any

    stages {
        stage('Unit Tests') { steps { sh './gradlew test' } }
        stage('Integration Tests') { steps { sh './gradlew integrationTest' } }
        stage('E2E Tests') { steps { sh './gradlew e2eTest' } }
    }
}
```

**6. 정리 작업 (Cleanup):**

```groovy
// ✅ Good: 항상 정리
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh './gradlew build'
            }
        }
    }

    post {
        always {
            cleanWs()  // 워크스페이스 정리
            sh 'docker system prune -f'  // Docker 정리
        }
    }
}

// ❌ Bad: 정리 안 함 (디스크 공간 부족)
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh './gradlew build'
            }
        }
    }
}
```

**7. 에러 처리:**

```groovy
// ✅ Good: 명확한 에러 처리
pipeline {
    agent any

    stages {
        stage('Deploy') {
            steps {
                script {
                    try {
                        sh './deploy.sh'
                    } catch (Exception e) {
                        echo "Deployment failed: ${e.message}"
                        // 롤백
                        sh './rollback.sh'
                        throw e
                    }
                }
            }
        }
    }

    post {
        failure {
            slackSend(
                channel: '#alerts',
                color: 'danger',
                message: "Pipeline failed: ${env.BUILD_URL}"
            )
        }
    }
}

// ❌ Bad: 에러 처리 없음
pipeline {
    agent any

    stages {
        stage('Deploy') {
            steps {
                sh './deploy.sh'  // 실패해도 그냥 멈춤
            }
        }
    }
}
```

**8. 타임아웃 설정:**

```groovy
// ✅ Good: 타임아웃 설정
pipeline {
    agent any

    options {
        timeout(time: 1, unit: 'HOURS')
    }

    stages {
        stage('Build') {
            options {
                timeout(time: 30, unit: 'MINUTES')
            }
            steps {
                sh './gradlew build'
            }
        }
    }
}

// ❌ Bad: 타임아웃 없음 (무한 대기 가능)
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh './gradlew build'
            }
        }
    }
}
```

**9. 빌드 히스토리 관리:**

```groovy
// ✅ Good: 빌드 히스토리 제한
pipeline {
    agent any

    options {
        buildDiscarder(logRotator(
            numToKeepStr: '10',
            artifactNumToKeepStr: '5'
        ))
    }

    stages {
        stage('Build') {
            steps {
                sh './gradlew build'
            }
        }
    }
}

// ❌ Bad: 무제한 히스토리 (디스크 공간 부족)
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh './gradlew build'
            }
        }
    }
}
```

**10. 명확한 스테이지 이름:**

```groovy
// ✅ Good: 명확한 이름
pipeline {
    agent any

    stages {
        stage('Checkout Source Code') { ... }
        stage('Compile Application') { ... }
        stage('Run Unit Tests') { ... }
        stage('Build Docker Image') { ... }
        stage('Deploy to Staging') { ... }
    }
}

// ❌ Bad: 모호한 이름
pipeline {
    agent any

    stages {
        stage('Step 1') { ... }
        stage('Step 2') { ... }
        stage('Step 3') { ... }
    }
}
```

**안티패턴 (Anti-Patterns):**

```groovy
// ❌ 1. 너무 긴 파이프라인 (가독성 저하)
// 해결: Shared Library로 분리

// ❌ 2. 순차 실행만 사용 (느림)
// 해결: parallel {} 사용

// ❌ 3. 하드코딩된 값
// 해결: 환경 변수, 파라미터 사용

// ❌ 4. Credential 노출
// 해결: withCredentials 사용

// ❌ 5. 에러 처리 없음
// 해결: try-catch, post 블록

// ❌ 6. 정리 작업 없음
// 해결: post { always { cleanWs() } }

// ❌ 7. 타임아웃 없음
// 해결: options { timeout() }

// ❌ 8. 모든 코드를 script {} 안에
// 해결: Declarative 문법 최대 활용

// ❌ 9. 너무 많은 플러그인 의존
// 해결: 필수 플러그인만 사용

// ❌ 10. 테스트 없이 배포
// 해결: 테스트 스테이지 필수화
```

**종합 예시 (Best Practices 적용):**

```groovy
@Library('lk-trade-library') _

pipeline {
    agent any

    environment {
        REGISTRY = 'ghcr.io'
        IMAGE_NAME = 'lk-trade/user-service'
        VERSION = "${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 1, unit: 'HOURS')
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Parallel Build & Test') {
            parallel {
                stage('Build') {
                    steps {
                        sh './gradlew build'
                    }
                }

                stage('Unit Tests') {
                    steps {
                        sh './gradlew test'
                    }
                    post {
                        always {
                            junit '**/build/test-results/test/*.xml'
                        }
                    }
                }

                stage('Security Scan') {
                    steps {
                        sh 'trivy filesystem .'
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    buildDockerImage(env.IMAGE_NAME, env.VERSION)
                }
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                script {
                    deployToEnvironment('staging', env.IMAGE_NAME, env.VERSION)
                }
            }
        }
    }

    post {
        always {
            cleanWs()
            sh 'docker system prune -f'
        }

        success {
            sendSlackNotification('SUCCESS')
        }

        failure {
            sendSlackNotification('FAILURE')
        }
    }
}
```

</details>

---

**다음 섹션에서 만나요!** 🚀