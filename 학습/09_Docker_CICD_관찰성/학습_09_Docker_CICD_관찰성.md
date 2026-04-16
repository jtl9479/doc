# 학습 09. Docker + CI/CD + 관찰성

## Step 목차

| Step | 항목 | 카테고리 |
|------|------|----------|
| Step 1 | 컨테이너 개요 — 왜 Docker인가, VM vs 컨테이너 | Docker 기초 |
| Step 2 | Docker 환경 구축 — 설치, 기본 명령어, 이미지/컨테이너 개념 | Docker 기초 |
| Step 3 | Docker 이미지 — Dockerfile 작성, 빌드, 레이어 구조 | Docker |
| Step 4 | Dockerfile 최적화 — 멀티 스테이지 빌드, 레이어 캐시, 이미지 경량화 | Docker |
| Step 5 | Docker Compose — 멀티 컨테이너 오케스트레이션 | Docker |
| Step 6 | Docker 네트워크 + 볼륨 + 환경 변수 | Docker |
| Step 7 | Docker 실전 — Spring Boot 앱 컨테이너화 | Docker |
| Step 8 | CI/CD 개요 — 왜 CI/CD인가, CI vs CD vs CD | CI/CD 기초 |
| Step 9 | GitHub Actions 기본 — 워크플로, 트리거, 잡, 스텝 | CI/CD |
| Step 10 | GitHub Actions 실전 — 빌드 → 테스트 → 배포 파이프라인 | CI/CD |
| Step 11 | GitHub Actions 심화 — 캐시, 시크릿, 매트릭스, 재사용 워크플로 | CI/CD |
| Step 12 | GitOps / ArgoCD 개념 | CI/CD |
| Step 13 | 관찰성 개요 — 메트릭, 로그, 트레이스 3대 축 | 관찰성 기초 |
| Step 14 | Spring Boot Actuator + Micrometer | 관찰성 |
| Step 15 | Prometheus — 메트릭 수집, PromQL, 알림 | 관찰성 |
| Step 16 | Grafana — 대시보드 구축, 알림 설정 | 관찰성 |
| Step 17 | 로그 수집 — 구조화 로그, Loki 또는 ELK 스택 | 관찰성 |
| Step 18 | 분산 추적 — OpenTelemetry, Zipkin/Jaeger 개념 | 관찰성 |
| Step 19 | 관찰성 실전 — 장애 진단 시나리오 | 관찰성 실전 |

---

## 1. 개요

**현재 수준**: Docker/CI/CD/관찰성 경험 없음. 개념만 인지.
**학습 목표**: Spring Boot 앱을 Docker로 컨테이너화하고, GitHub Actions로 자동 빌드/배포하며, Prometheus+Grafana로 모니터링하는 전체 파이프라인을 자력 구축 가능. 장애 시 로그/메트릭으로 원인 추적 가능.
**분기 배정**: 2분기 (2026.07 ~ 2026.09)

---

## 2. 학습 순서 + 세부 항목

---

### Step 1. 컨테이너 개요 — 왜 Docker인가, VM vs 컨테이너

| 학습 항목 | 학습 목표 |
|----------|----------|
| 컨테이너란 | 애플리케이션과 의존성을 격리된 환경에서 실행하는 기술. "내 PC에서는 되는데 서버에서 안 돼요" 문제를 해결하는 이유를 설명 가능. |
| VM vs 컨테이너 | VM: 하이퍼바이저 위에 게스트 OS 전체 실행 (무거움, 수 GB, 부팅 수 분). 컨테이너: 호스트 OS 커널 공유, 프로세스 격리 (가벼움, 수 MB, 기동 수 초). 차이를 그림으로 설명 가능. |
| Docker의 핵심 가치 | 환경 일관성(개발=테스트=운영), 빠른 기동, 이미지 기반 배포(불변 인프라), 수평 확장 용이를 설명 가능. |
| 컨테이너 격리 원리 | Linux Namespace(PID, Network, Mount 등 격리)와 cgroup(CPU, 메모리 제한)이 컨테이너의 기반 기술임을 개념 수준 설명 가능. |
| OCI (Open Container Initiative) | Docker가 표준이 아니라 OCI가 컨테이너 표준임을 알고 있음. containerd, CRI-O 등 대안 런타임의 존재를 알고 있음. |

---

### Step 2. Docker 환경 구축 — 설치, 기본 명령어, 이미지/컨테이너 개념

| 학습 항목 | 학습 목표 |
|----------|----------|
| Docker Desktop 설치 | Windows/Mac에서 Docker Desktop 설치 + 동작 확인. docker version, docker info 실행 가능. |
| 이미지 vs 컨테이너 | 이미지: 읽기 전용 템플릿(클래스). 컨테이너: 이미지의 실행 인스턴스(객체). Java 클래스/인스턴스 비유로 설명 가능. |
| 기본 명령어 | docker pull, docker run, docker ps, docker stop, docker rm, docker images, docker rmi 사용 가능. |
| docker run 옵션 | -d(백그라운드), -p(포트 매핑), -v(볼륨 마운트), -e(환경 변수), --name(컨테이너 이름), --rm(종료 시 자동 삭제) 각 옵션을 설명 + 사용 가능. |
| Docker Hub | 공개 이미지 레지스트리. nginx, redis, postgres 등 공식 이미지를 pull하여 실행하는 실습. |
| docker exec / logs | 실행 중인 컨테이너에 접속(exec -it bash)하고 로그를 확인(logs -f)하는 방법. |

---

### Step 3. Docker 이미지 — Dockerfile 작성, 빌드, 레이어 구조

| 학습 항목 | 학습 목표 |
|----------|----------|
| Dockerfile이란 | 이미지를 만드는 스크립트. FROM → COPY → RUN → EXPOSE → CMD/ENTRYPOINT 기본 구조를 작성 가능. |
| 핵심 명령어 | FROM(베이스 이미지), RUN(빌드 시 명령 실행), COPY/ADD(파일 복사), WORKDIR(작업 디렉토리), EXPOSE(포트 문서화), ENV(환경 변수), CMD vs ENTRYPOINT(실행 명령)의 차이를 설명 가능. |
| CMD vs ENTRYPOINT | CMD: 기본 실행 명령(docker run 시 덮어쓰기 가능). ENTRYPOINT: 고정 실행 명령(인자만 추가). 조합(ENTRYPOINT + CMD)을 설명 가능. |
| 레이어 구조 | 각 Dockerfile 명령어가 하나의 읽기 전용 레이어를 생성. 레이어가 캐시되어 변경 없는 레이어는 재빌드하지 않는 원리를 설명 가능. |
| docker build | docker build -t name:tag . 명령으로 이미지 빌드. 빌드 컨텍스트와 .dockerignore의 역할을 설명 가능. |
| 이미지 태깅/푸시 | docker tag, docker push로 레지스트리에 이미지를 업로드하는 방법을 알고 있음. |

---

### Step 4. Dockerfile 최적화 — 멀티 스테이지 빌드, 레이어 캐시, 이미지 경량화

| 학습 항목 | 학습 목표 |
|----------|----------|
| 멀티 스테이지 빌드 | 빌드 스테이지(JDK + Gradle/Maven) → 실행 스테이지(JRE만) 분리. 빌드 도구가 최종 이미지에 포함되지 않아 이미지 크기를 줄이는 원리를 설명 가능. |
| 레이어 캐시 최적화 | 변경 빈도가 낮은 것(의존성 설치)을 위에, 높은 것(소스 코드 복사)을 아래에 배치하여 캐시 히트율을 높이는 전략. COPY build.gradle → RUN gradle dependencies → COPY src 순서의 이유를 설명 가능. |
| 베이스 이미지 선택 | eclipse-temurin(JDK), amazoncorretto, alpine 기반 이미지의 차이. alpine이 작지만 glibc 호환성 문제가 있는 이유를 설명 가능. |
| .dockerignore | 빌드 컨텍스트에서 불필요한 파일(node_modules, .git, build/)을 제외하여 빌드 속도를 높이는 방법. |
| 이미지 크기 분석 | docker images로 크기 확인. docker history로 레이어별 크기 분석. dive 도구의 존재를 알고 있음. |
| 보안 | root 사용자로 실행하면 안 되는 이유. USER 명령으로 비루트 사용자 설정. 불필요한 패키지 최소화 원칙. |

---

### Step 5. Docker Compose — 멀티 컨테이너 오케스트레이션

| 학습 항목 | 학습 목표 |
|----------|----------|
| Docker Compose란 | 여러 컨테이너를 YAML 파일 하나로 정의하고 한 번에 기동/중지하는 도구. "App + DB + Redis + Kafka를 한 줄로 기동"하는 편의성을 설명 가능. |
| docker-compose.yml 구조 | services, networks, volumes 최상위 키의 역할. 각 서비스에 image/build, ports, environment, volumes, depends_on을 설정하는 방법을 작성 가능. |
| depends_on과 헬스 체크 | depends_on은 기동 순서만 보장하고 준비 완료를 보장하지 않음. healthcheck + condition: service_healthy로 진정한 의존 관계를 설정하는 방법을 설명 가능. |
| docker compose 명령어 | up -d, down, logs -f, ps, exec, restart 사용 가능. |
| 전체 스택 구성 실습 | App(Spring Boot) + DB(PostgreSQL/Oracle) + Redis + Kafka + Prometheus + Grafana를 docker-compose.yml로 정의하고 기동 가능. |

---

### Step 6. Docker 네트워크 + 볼륨 + 환경 변수

| 학습 항목 | 학습 목표 |
|----------|----------|
| Docker 네트워크 | bridge(기본, 같은 호스트 컨테이너 간 통신), host(호스트 네트워크 직접 사용), none(네트워크 없음)의 차이를 설명 가능. Compose에서 같은 네트워크의 컨테이너끼리 서비스명으로 통신(app → redis:6379)하는 원리를 설명 가능. |
| Docker 볼륨 | Named Volume(docker volume create), Bind Mount(호스트 경로 직접 마운트)의 차이. DB 데이터 영속성을 위해 볼륨이 필수인 이유(컨테이너 삭제 시 데이터 보존)를 설명 가능. |
| 환경 변수 | Dockerfile ENV, docker run -e, docker-compose environment, .env 파일의 우선순위와 사용 방법. 시크릿(비밀번호 등)을 이미지에 하드코딩하면 안 되는 이유를 설명 가능. |

---

### Step 7. Docker 실전 — Spring Boot 앱 컨테이너화

| 학습 항목 | 학습 목표 |
|----------|----------|
| Spring Boot Dockerfile | 멀티 스테이지로 Gradle/Maven 빌드 → JRE 기반 실행 이미지 생성하는 Dockerfile을 작성 가능. |
| Spring Boot Layered Jar | Spring Boot 2.3+의 레이어드 Jar 기능으로 의존성/어플리케이션 레이어를 분리하여 Docker 레이어 캐시 효율을 높이는 방법을 설명 가능. |
| Jib (Google) | Dockerfile 없이 Maven/Gradle 플러그인으로 이미지를 빌드하는 대안. Docker 데몬 없이도 이미지 생성 가능한 장점을 알고 있음. |
| 컨테이너 환경에서의 JVM 설정 | 컨테이너 메모리 제한과 JVM 힙의 관계. -XX:MaxRAMPercentage로 컨테이너 메모리에 비례한 힙 설정하는 방법을 설명 가능. Java 10+ 이전에 컨테이너 메모리를 인식하지 못하던 문제를 알고 있음. |
| PID 1 문제와 Graceful Shutdown (심화) | 컨테이너에서 Java 앱이 PID 1로 실행되면 SIGTERM 시그널을 제대로 받지 못하는 이유(PID 1은 Linux에서 특수 취급, 기본 시그널 핸들러 없음)를 설명 가능. 자식 프로세스가 종료되어도 PID 1이 좀비 프로세스를 거두지(reap) 않는 문제를 설명 가능. 해결: ① ENTRYPOINT ["java", ...] 대신 tini(경량 init 프로세스)를 PID 1으로 실행하여 시그널 전달 + 좀비 정리, ② docker run --init 옵션, ③ Spring Boot의 server.shutdown=graceful 설정으로 처리 중인 요청 완료 후 종료하는 패턴을 설명 가능. |

---

### Step 8. CI/CD 개요 — 왜 CI/CD인가, CI vs CD vs CD

| 학습 항목 | 학습 목표 |
|----------|----------|
| CI (Continuous Integration) | 코드 변경 시 자동으로 빌드 + 테스트 실행. "통합 지옥" 방지. 작은 변경을 자주 머지하는 문화를 설명 가능. |
| CD (Continuous Delivery) | CI + 스테이징 환경까지 자동 배포. 프로덕션 배포는 수동 승인. "언제든 배포 가능한 상태"를 유지하는 목적을 설명 가능. |
| CD (Continuous Deployment) | CI + 프로덕션까지 자동 배포. 수동 승인 없음. Delivery와의 차이(마지막 단계 자동화 여부)를 설명 가능. |
| CI/CD의 가치 | 빠른 피드백(빌드/테스트 실패 즉시 감지), 배포 빈도 향상, 수동 실수 감소, 팀 생산성 향상을 설명 가능. |
| CI/CD 도구 | GitHub Actions, Jenkins, GitLab CI, CircleCI 등 주요 도구의 존재를 알고 있음. |

---

### Step 9. GitHub Actions 기본 — 워크플로, 트리거, 잡, 스텝

| 학습 항목 | 학습 목표 |
|----------|----------|
| 워크플로 (Workflow) | .github/workflows/ 디렉토리에 YAML 파일로 정의. 하나의 자동화 프로세스 단위. |
| 트리거 (on) | push, pull_request, schedule(cron), workflow_dispatch(수동 실행) 등 이벤트 트리거를 설정 가능. 브랜치/경로 필터(on.push.branches, paths)를 적용 가능. |
| 잡 (Jobs) | 독립적으로 실행되는 작업 단위. runs-on(실행 환경: ubuntu-latest 등)을 설정 가능. 잡 간 의존성(needs)을 설정 가능. |
| 스텝 (Steps) | 잡 내에서 순서대로 실행되는 명령. uses(액션 사용) vs run(쉘 명령)의 차이. actions/checkout, actions/setup-java 등 공식 액션을 사용 가능. |
| 환경 변수 / 시크릿 | env로 환경 변수, ${{ secrets.XXX }}로 시크릿을 참조하는 방법. Settings > Secrets에 비밀번호/토큰을 저장하는 방법. |

---

### Step 10. GitHub Actions 실전 — 빌드 → 테스트 → 배포 파이프라인

| 학습 항목 | 학습 목표 |
|----------|----------|
| Java 빌드 파이프라인 | actions/setup-java + Gradle/Maven 빌드 + 테스트 실행 워크플로를 작성 가능. |
| Docker 이미지 빌드 + 푸시 | docker/build-push-action으로 이미지 빌드 → Docker Hub 또는 GitHub Container Registry(ghcr.io)에 푸시하는 워크플로를 작성 가능. |
| 배포 연동 | SSH로 서버 접속 → docker pull → docker compose up 또는 K8s kubectl apply로 배포하는 단계를 설정 가능. |
| PR 자동 체크 | Pull Request 시 자동으로 빌드 + 테스트 실행하여 코드 품질을 게이트키핑하는 워크플로를 설정 가능. |
| 빌드 상태 배지 | README에 빌드 상태 배지를 추가하는 방법을 알고 있음. |
| 배포 전략 (심화) | **Rolling Update**(순차 교체, 기본), **Blue-Green**(구버전/신버전 동시 운영 후 트래픽 전환, 즉시 롤백 가능), **Canary**(소수 사용자에게 먼저 배포 후 점진 확대)의 차이와 각각의 트레이드오프(비용, 롤백 속도, 복잡도)를 설명 가능. 각 전략에서 헬스 체크가 필수인 이유를 설명 가능. |
| 이미지 보안 스캔 (DevSecOps) | CI 파이프라인에서 Trivy 같은 도구로 컨테이너 이미지의 취약점(CVE)을 자동 스캔하는 단계를 추가하는 방법을 설명 가능. 취약점 발견 시 빌드를 실패시키는 게이트키핑 패턴을 설명 가능. |
| 시크릿 마스킹 | 시크릿(비밀번호, 토큰)이 CI 로그에 절대 노출되지 않도록 마스킹하는 원칙. GitHub Actions가 secrets를 자동 마스킹하는 동작을 이해. 환경 변수로 노출된 시크릿이 echo로 찍히지 않도록 주의하는 방법을 설명 가능. |

---

### Step 11. GitHub Actions 심화 — 캐시, 시크릿, 매트릭스, 재사용 워크플로

| 학습 항목 | 학습 목표 |
|----------|----------|
| 의존성 캐시 | actions/cache로 Gradle/Maven 의존성을 캐시하여 빌드 시간을 단축하는 방법. 캐시 키 설계(hashFiles('**/build.gradle'))를 설명 가능. |
| 매트릭스 (Matrix Strategy) | 여러 Java 버전(17, 21), OS(ubuntu, windows)에서 동시 테스트하는 설정을 작성 가능. |
| 재사용 워크플로 (Reusable Workflow) | workflow_call로 공통 워크플로를 정의하고 여러 저장소에서 재사용하는 패턴. |
| 환경 (Environments) | production, staging 환경별로 시크릿과 승인 규칙을 분리하는 방법을 알고 있음. |
| 비용/성능 관리 | 불필요한 워크플로 실행 방지(paths-ignore, concurrency로 중복 실행 취소), 셀프 호스티드 러너 개념을 알고 있음. |

---

### Step 12. GitOps / ArgoCD 개념

| 학습 항목 | 학습 목표 |
|----------|----------|
| GitOps란 | Git 저장소를 "원하는 상태(Desired State)"의 단일 진실 소스(Single Source of Truth)로 사용하는 운영 방법론. Git에 커밋하면 자동으로 인프라/배포가 반영되는 원리를 설명 가능. |
| Push vs Pull 기반 배포 | Push(CI에서 kubectl apply): 외부에서 클러스터에 접근 필요. Pull(ArgoCD가 Git을 감시 → 변경 감지 → 자동 동기화): 클러스터 내부에서 동작, 보안 우수. 차이를 설명 가능. |
| ArgoCD 개요 | K8s 전용 GitOps 도구. Git 저장소의 매니페스트와 클러스터 상태를 지속 비교 → 차이 발생 시 자동 동기화. 대시보드 UI 제공. 개념 수준 설명 가능. (K8s 학습과 연계) |

---

### Step 13. 관찰성 개요 — 메트릭, 로그, 트레이스 3대 축

| 학습 항목 | 학습 목표 |
|----------|----------|
| 관찰성(Observability)이란 | 시스템의 외부 출력(메트릭, 로그, 트레이스)을 보고 내부 상태를 추론하는 능력. 모니터링(알려진 문제 감지) vs 관찰성(미지의 문제 탐색)의 차이를 설명 가능. |
| 메트릭 (Metrics) | 숫자형 시계열 데이터(CPU 사용률, 응답 시간, 에러율 등). "무엇이 일어나고 있는가"를 수치로 파악. Prometheus가 대표 도구. |
| 로그 (Logs) | 이벤트 기반 텍스트/JSON 기록. "왜 그런 일이 일어났는가"를 상세히 파악. ELK/Loki가 대표 도구. |
| 트레이스 (Traces) | 분산 시스템에서 하나의 요청이 여러 서비스를 거치는 경로 추적. "어디서 느려졌는가"를 파악. Zipkin/Jaeger/OpenTelemetry가 대표 도구. |
| 3대 축의 관계 | 메트릭(이상 감지) → 로그(원인 분석) → 트레이스(병목 위치 추적) 순서로 장애를 진단하는 흐름을 설명 가능. |

---

### Step 14. Spring Boot Actuator + Micrometer

| 학습 항목 | 학습 목표 |
|----------|----------|
| Actuator 개요 | /actuator/health, /actuator/metrics, /actuator/info 등 운영 엔드포인트의 역할. 의존성 추가만으로 활성화됨을 설명 가능. |
| 헬스 체크 | /actuator/health로 DB, Redis, Kafka 등 의존 서비스의 상태를 확인. 커스텀 HealthIndicator를 구현하는 방법을 알고 있음. |
| Micrometer | 메트릭 수집 추상화 라이브러리. Prometheus, Datadog, CloudWatch 등 다양한 백엔드를 지원하는 "메트릭의 SLF4J"임을 설명 가능. |
| 핵심 메트릭 | JVM 메트릭(heap, GC, thread), HTTP 메트릭(요청 수, 응답 시간, 에러율), DB 커넥션 풀 메트릭(HikariCP)을 설명 가능. |
| 커스텀 메트릭 | Counter, Gauge, Timer, DistributionSummary로 비즈니스 메트릭을 직접 정의하는 방법을 적용 가능. |
| 비즈니스 메트릭 관점 (심화) | 시스템 메트릭(CPU, 메모리)만으로는 "서비스가 정상인가?"에 답 못 함을 설명 가능. **비즈니스 메트릭** 예시: 주문 성공률(Counter: 주문 성공/실패), 결제 처리 시간(Timer), 재고 부족 발생 횟수(Counter), 동시 접속 사용자 수(Gauge). "서버가 살아있다"가 아닌 "서비스가 비즈니스 가치를 정상 생산하고 있다"를 메트릭으로 증명하는 관점. ERP 도메인(수주 처리율, 출고 지연율 등)에 연결하여 비즈니스 메트릭을 설계 가능. |
| Prometheus 포맷 노출 | micrometer-registry-prometheus 의존성으로 /actuator/prometheus 엔드포인트를 노출하는 설정을 적용 가능. |

---

### Step 15. Prometheus — 메트릭 수집, PromQL, 알림

| 학습 항목 | 학습 목표 |
|----------|----------|
| Prometheus 아키텍처 | Pull 기반 수집(타겟의 /metrics 엔드포인트를 주기적으로 스크래핑). Push 기반(Pushgateway)과의 차이를 설명 가능. |
| prometheus.yml 설정 | scrape_configs에 타겟(Spring Boot 앱, Redis Exporter, Kafka Exporter 등)을 등록하는 방법을 작성 가능. |
| PromQL 기본 | rate()(초당 변화율), sum()(합계), avg()(평균), histogram_quantile()(퍼센타일)을 사용하여 메트릭을 쿼리 가능. |
| PromQL 실전 | "최근 5분간 HTTP 500 에러 비율", "P99 응답 시간", "JVM 힙 사용률 추이"를 PromQL로 작성 가능. |
| Alertmanager | 알림 규칙(예: 에러율 > 5% 지속 5분)을 정의하고, Slack/이메일로 알림을 보내는 구조를 설명 가능. |

---

### Step 16. Grafana — 대시보드 구축, 알림 설정

| 학습 항목 | 학습 목표 |
|----------|----------|
| Grafana 개요 | Prometheus/Loki 등 데이터 소스를 시각화하는 대시보드 도구. |
| 데이터 소스 연결 | Prometheus를 데이터 소스로 등록하는 방법. Loki(로그), Tempo(트레이스) 등 추가 소스도 연결 가능. |
| 대시보드 구축 | 패널(Panel) 추가, PromQL 쿼리 작성, 시각화 유형(그래프, 게이지, 테이블, 히트맵) 선택, 변수(Variable)로 동적 필터링하는 방법을 적용 가능. |
| 기본 대시보드 | JVM 메트릭(힙, GC, 스레드), HTTP 메트릭(요청 수, 응답 시간, 에러율), 인프라 메트릭(CPU, 메모리, 디스크)을 포함하는 대시보드를 구축 가능. |
| 공개 대시보드 활용 | Grafana Labs 대시보드 마켓에서 Spring Boot, Redis, Kafka 등 공개 대시보드를 가져와 활용하는 방법을 알고 있음. |
| Grafana 알림 | 대시보드 패널에 알림 조건을 설정하고, Slack/이메일로 알림을 보내는 방법을 적용 가능. |

---

### Step 17. 로그 수집 — 구조화 로그, Loki 또는 ELK 스택

| 학습 항목 | 학습 목표 |
|----------|----------|
| 구조화 로그 | 텍스트 로그 vs JSON 구조화 로그의 차이. JSON 로그가 검색/분석에 유리한 이유를 설명 가능. Logback에서 JSON 포맷(logstash-logback-encoder)을 설정하는 방법을 알고 있음. |
| 로그 레벨 전략 | TRACE/DEBUG/INFO/WARN/ERROR 각 레벨의 용도와, 프로덕션에서 INFO 이상만 남기는 이유를 설명 가능. |
| 추적 ID (Correlation ID) | 하나의 요청에 고유 ID를 부여하여 여러 서비스의 로그를 연결하는 패턴. MDC(Mapped Diagnostic Context)에 traceId를 넣는 방법을 설명 가능. |
| Loki | Grafana Labs의 경량 로그 수집 도구. "로그의 Prometheus". 인덱스가 아닌 레이블 기반 검색. Promtail(로그 수집기) → Loki(저장) → Grafana(시각화) 구조를 설명 가능. |
| ELK 스택 (개념) | Elasticsearch(저장/검색) + Logstash(수집/변환) + Kibana(시각화). Loki 대비 강력하지만 무겁고 운영 비용 높음. 선택 기준(소규모 → Loki, 대규모/복잡 검색 → ELK)을 설명 가능. |

---

### Step 18. 분산 추적 — OpenTelemetry, Zipkin/Jaeger 개념

| 학습 항목 | 학습 목표 |
|----------|----------|
| 분산 추적이란 | 하나의 HTTP 요청이 API Gateway → Service A → Service B → DB를 거치는 전체 경로를 추적하는 기술. "어디서 느려졌는가"를 파악하는 목적을 설명 가능. |
| Trace / Span | Trace: 하나의 요청 전체 경로. Span: Trace 내 개별 작업 단위(예: DB 쿼리 1건). 부모-자식 관계(Span Tree)를 설명 가능. |
| OpenTelemetry | 메트릭, 로그, 트레이스를 통합하는 오픈 표준/SDK. 벤더 중립적(Zipkin, Jaeger, Datadog 등으로 전송 가능)인 이유를 설명 가능. |
| Zipkin / Jaeger | 대표적 분산 추적 시각화 도구. Trace를 타임라인으로 보여주어 병목 구간을 식별하는 UI를 개념 수준 설명 가능. |
| Spring Boot 연동 | Micrometer Tracing(구 Spring Cloud Sleuth)으로 자동 Trace/Span 생성 + OpenTelemetry 또는 Zipkin으로 전송하는 구조를 개념 수준 설명 가능. |

---

### Step 19. 관찰성 실전 — 장애 진단 시나리오

| 학습 항목 | 학습 목표 |
|----------|----------|
| "응답이 느려졌다" | Grafana에서 HTTP 응답 시간 그래프 확인 → 특정 시점부터 P99 급증 → 해당 시점 로그 확인 → DB 슬로 쿼리 또는 외부 API 지연 발견 순서를 설명 가능. |
| "에러율이 급증했다" | Grafana에서 HTTP 5xx 비율 알림 → 해당 시점 로그에서 에러 메시지 확인 → 원인(OOM, DB 커넥션 고갈, 외부 서비스 장애 등) 식별 순서를 설명 가능. |
| "특정 요청만 느리다" | 분산 추적(Trace)에서 해당 요청의 Span Tree 확인 → 어느 서비스/DB 호출에서 지연 발생하는지 식별 가능. |
| "메모리 사용량이 계속 증가한다" | JVM 힙 메트릭에서 GC 후에도 메모리가 줄지 않는 패턴 확인 → 메모리 누수 의심 → Heap Dump 분석(트러블슈팅 학습과 연계) 순서를 설명 가능. |
| 장애 대응 → 알림 → 진단 → 해결 → 회고 | 관찰성 도구를 활용한 체계적 장애 대응 프로세스를 설명 가능. |

---

## 3. 자가 검증

### Docker
- [ ] "VM과 컨테이너의 차이" 그림으로 설명 가능
- [ ] Dockerfile을 작성하고 멀티 스테이지 빌드로 이미지 경량화 가능
- [ ] "레이어 캐시를 최적화하는 방법" 설명 가능
- [ ] Docker Compose로 전체 스택(DB+Redis+Kafka+App+Prometheus+Grafana) 기동 가능
- [ ] "컨테이너 환경에서 JVM 힙 설정" → MaxRAMPercentage 설명 가능
- [ ] "컨테이너가 Graceful Shutdown되지 않을 때 의심할 점" → PID 1 문제 + tini 설명 가능

### CI/CD
- [ ] "CI vs CD(Delivery) vs CD(Deployment) 차이" 설명 가능
- [ ] GitHub Actions 워크플로(빌드 → 테스트 → Docker 빌드 → 배포)를 작성 가능
- [ ] "의존성 캐시로 빌드 시간을 단축하는 방법" 설명 가능
- [ ] "GitOps란?" → Git = 단일 진실 소스, Push vs Pull 배포 차이 설명 가능
- [ ] "Blue-Green vs Canary vs Rolling Update 차이" 설명 가능
- [ ] "CI 파이프라인에서 이미지 보안 스캔을 하는 이유" → DevSecOps 설명 가능

### 관찰성
- [ ] "관찰성의 3대 축(메트릭, 로그, 트레이스)" 각각의 역할 설명 가능
- [ ] Spring Boot Actuator + Micrometer로 Prometheus 메트릭 노출 가능
- [ ] PromQL로 "HTTP 500 에러 비율", "P99 응답 시간" 쿼리 작성 가능
- [ ] Grafana 대시보드(JVM, HTTP, 인프라)를 구축 가능
- [ ] "구조화 로그란?" → JSON 로그 + 추적 ID(MDC) 설명 가능
- [ ] "분산 추적이란?" → Trace/Span 개념 + OpenTelemetry 역할 설명 가능
- [ ] "비즈니스 메트릭 vs 시스템 메트릭 차이" → 주문 성공률, 처리 시간 등 비즈니스 지표 설계 가능
- [ ] "응답이 느려졌다" → 메트릭 → 로그 → 트레이스 순서로 진단 가능

---

## 4. 진행 상태

| Step | 항목 | 상태 |
|------|------|------|
| Step 1 | 컨테이너 개요 | 미시작 |
| Step 2 | Docker 환경 구축 | 미시작 |
| Step 3 | Docker 이미지 / Dockerfile | 미시작 |
| Step 4 | Dockerfile 최적화 | 미시작 |
| Step 5 | Docker Compose | 미시작 |
| Step 6 | 네트워크 + 볼륨 + 환경 변수 | 미시작 |
| Step 7 | Docker 실전 (Spring Boot) | 미시작 |
| Step 8 | CI/CD 개요 | 미시작 |
| Step 9 | GitHub Actions 기본 | 미시작 |
| Step 10 | GitHub Actions 실전 | 미시작 |
| Step 11 | GitHub Actions 심화 | 미시작 |
| Step 12 | GitOps / ArgoCD | 미시작 |
| Step 13 | 관찰성 개요 | 미시작 |
| Step 14 | Actuator + Micrometer | 미시작 |
| Step 15 | Prometheus | 미시작 |
| Step 16 | Grafana | 미시작 |
| Step 17 | 로그 수집 | 미시작 |
| Step 18 | 분산 추적 | 미시작 |
| Step 19 | 관찰성 실전 | 미시작 |

---

## 5. 참고 자료 (보조용)

| 자료 | 용도 |
|------|------|
| Docker 공식 문서 (docs.docker.com) | Step 1~7 레퍼런스 |
| GitHub Actions 공식 문서 | Step 8~11 레퍼런스 |
| Prometheus 공식 문서 | Step 15 PromQL/설정 참고 |
| Grafana 공식 문서 | Step 16 대시보드 구축 참고 |
| Spring Boot Actuator 공식 문서 | Step 14 설정 참고 |

---

> 이 문서는 Claude가 미래 세션에서 읽고 학습을 안내하기 위한 가이드입니다.
> 사용자가 "Docker 공부하자", "CI/CD 공부하자", "관찰성 공부하자" 또는 "Step N 하자"라고 하면, 진행 상태를 확인하고 다음 미시작 Step부터 학습_템플릿.md 형식으로 진행합니다.
