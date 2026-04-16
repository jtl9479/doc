# 학습 12. AWS

## Step 목차

| Step | 항목 | 카테고리 |
|------|------|----------|
| Step 1 | 클라우드 개요 — 왜 AWS인가, 온프레미스 vs 클라우드 | 기초 |
| Step 2 | AWS 기본 — 계정, 리전/AZ, 콘솔, CLI, 프리 티어 | 기초 |
| Step 3 | IAM — 사용자, 그룹, 역할, 정책, 최소 권한 원칙 | 보안/권한 |
| Step 4 | VPC — 네트워크 기초, 서브넷, 보안 그룹, 인터넷 게이트웨이 | 네트워크 |
| Step 5 | EC2 — 인스턴스 생성, SSH 접속, AMI, 인스턴스 유형 | 컴퓨팅 |
| Step 6 | EC2 심화 — ELB, Auto Scaling Group, 배치 그룹 | 컴퓨팅 |
| Step 7 | S3 — 버킷, 객체, 스토리지 클래스, 정적 호스팅 | 스토리지 |
| Step 8 | RDS — 관계형 DB 서비스, Multi-AZ, Read Replica | DB |
| Step 9 | ECS — 컨테이너 서비스, Fargate vs EC2 모드 | 컨테이너 |
| Step 10 | EKS — Kubernetes on AWS | 컨테이너 |
| Step 11 | Lambda — 서버리스 컴퓨팅 | 서버리스 |
| Step 12 | 기타 핵심 서비스 — SQS, SNS, CloudWatch, Route 53 | 부가 서비스 |
| Step 13 | 비용 관리 — 과금 구조, 비용 최적화, 프리 티어 한도 | 운영 |
| Step 14 | AWS 아키텍처 패턴 — 3-Tier, 서버리스, 컨테이너 기반 | 설계 |

---

## 1. 개요

**현재 수준**: AWS 경험 없음. 온프레미스(사내 서버) 환경에서 ERP 개발 중.
**학습 목표**: AWS 핵심 서비스를 이해하고, 콘솔+CLI로 인프라를 구성 가능. EKS에 Spring Boot 앱을 배포 가능. AWS 아키텍처 면접 질문에 답변 가능.
**분기 배정**: 3분기 (2026.10 ~ 2026.12)
**선수 조건**: 학습_09 Docker, 학습_11 K8s 기초 학습 후 진행 권장

---

## 2. 학습 순서 + 세부 항목

---

### Step 1. 클라우드 개요 — 왜 AWS인가, 온프레미스 vs 클라우드

| 학습 항목 | 학습 목표 |
|----------|----------|
| 클라우드란 | 물리 서버를 직접 소유/관리하지 않고, 인터넷을 통해 컴퓨팅 자원(서버, DB, 스토리지 등)을 빌려 쓰는 모델. "필요할 때 필요한 만큼 쓰고 쓴 만큼 비용 지불"을 설명 가능. |
| 온프레미스 vs 클라우드 | 온프레미스: 초기 투자(서버 구매), 유지보수 직접, 확장 느림. 클라우드: 초기 투자 없음(종량제), 유지보수 위임, 수 분 내 확장. 각각의 장단점을 설명 가능. |
| IaaS / PaaS / SaaS | IaaS(EC2: VM 제공), PaaS(Elastic Beanstalk: 런타임+배포 제공), SaaS(Gmail: 소프트웨어 제공). 추상화 수준에 따른 차이를 설명 가능. |
| 왜 AWS인가 | 시장 점유율 1위, 서비스 종류 최다, 글로벌 인프라(리전/AZ), 생태계(자격증, 커뮤니티). AWS vs Azure vs GCP 포지셔닝을 개념 수준 설명 가능. |
| Well-Architected Framework | AWS가 제시하는 5가지 기둥(운영 우수성, 보안, 안정성, 성능 효율성, 비용 최적화)을 개념 수준 알고 있음. |

---

### Step 2. AWS 기본 — 계정, 리전/AZ, 콘솔, CLI, 프리 티어

| 학습 항목 | 학습 목표 |
|----------|----------|
| AWS 계정 생성 | 프리 티어 계정 생성 가능. 루트 계정과 IAM 사용자의 차이(루트는 최소 사용)를 설명 가능. |
| 리전 (Region) | 전 세계에 분산된 데이터센터 그룹. 서울 리전(ap-northeast-2). 리전 선택 기준(지연시간, 법적 요구사항, 서비스 가용성, 비용)을 설명 가능. |
| 가용 영역 (AZ) | 리전 내 물리적으로 분리된 데이터센터. 하나의 리전에 보통 3개 AZ. Multi-AZ 배포로 고가용성을 확보하는 이유를 설명 가능. |
| AWS 콘솔 | 웹 기반 관리 인터페이스. 서비스 검색, 리전 선택, 리소스 관리를 콘솔에서 수행 가능. |
| AWS CLI | 명령줄 도구. aws configure(자격 증명 설정), aws s3 ls, aws ec2 describe-instances 등 기본 명령어를 사용 가능. |
| 프리 티어 | 12개월 무료(EC2 t2.micro 750시간/월, S3 5GB, RDS 750시간/월 등). 한도 초과 시 과금 발생. 비용 알림(Billing Alert) 설정 필수. |

---

### Step 3. IAM — 사용자, 그룹, 역할, 정책, 최소 권한 원칙

| 학습 항목 | 학습 목표 |
|----------|----------|
| IAM이란 | Identity and Access Management. "누가(Identity) 무엇을(Resource) 어떻게(Action) 할 수 있는가"를 관리하는 서비스. |
| 사용자 (User) | 개별 사람 또는 애플리케이션에 부여하는 영구 자격 증명. Access Key/Secret Key를 설명 가능. |
| 그룹 (Group) | 사용자를 묶어서 동일 정책을 일괄 부여. "developers" 그룹에 S3 읽기 권한 부여 같은 패턴. |
| 역할 (Role) | 임시 자격 증명. EC2 인스턴스나 Lambda 함수에 역할을 부여하여 AWS 서비스 접근 허용. 사용자가 아닌 **서비스에 권한을 부여**하는 방법을 설명 가능. |
| 정책 (Policy) | JSON 형식의 권한 정의. Effect(Allow/Deny), Action(s3:GetObject), Resource(arn:aws:s3:::my-bucket/*) 구조를 읽을 수 있음. |
| 최소 권한 원칙 | "필요한 최소한의 권한만 부여". 루트 계정 사용 금지, 와일드카드(*) 남용 금지의 이유를 설명 가능. |
| MFA (Multi-Factor Authentication) | 루트 계정과 관리자 계정에 MFA를 설정해야 하는 이유를 설명 가능. |

---

### Step 4. VPC — 네트워크 기초, 서브넷, 보안 그룹, 인터넷 게이트웨이

| 학습 항목 | 학습 목표 |
|----------|----------|
| VPC (Virtual Private Cloud) | AWS 내 격리된 가상 네트워크. CIDR 블록(예: 10.0.0.0/16)으로 IP 대역을 정의하는 개념을 설명 가능. |
| 서브넷 | VPC 내 IP 범위 분할. 퍼블릭 서브넷(인터넷 접근 가능) vs 프라이빗 서브넷(인터넷 접근 불가, 내부만). AZ별로 서브넷을 배치하는 이유(고가용성)를 설명 가능. |
| 인터넷 게이트웨이 (IGW) | VPC → 인터넷 연결 관문. 퍼블릭 서브넷에 IGW를 연결하는 방법을 설명 가능. |
| NAT 게이트웨이 | 프라이빗 서브넷의 리소스가 인터넷에 접근(아웃바운드만)할 수 있게 하는 서비스. 인바운드는 차단. |
| 보안 그룹 (Security Group) | 인스턴스 수준 방화벽. 인바운드/아웃바운드 규칙. 상태 저장형(Stateful: 나간 응답은 자동 허용). |
| NACL (Network ACL) | 서브넷 수준 방화벽. 무상태(Stateless). 보안 그룹과의 차이를 설명 가능. |
| 3-Tier VPC 구조 | 퍼블릭 서브넷(ALB) → 프라이빗 서브넷(App 서버) → 프라이빗 서브넷(DB). 전형적인 VPC 설계를 그림으로 그릴 수 있음. |

---

### Step 5. EC2 — 인스턴스 생성, SSH 접속, AMI, 인스턴스 유형

| 학습 항목 | 학습 목표 |
|----------|----------|
| EC2란 | Elastic Compute Cloud. 가상 서버(VM)를 수 분 내에 생성/삭제. "필요할 때 서버를 빌린다"의 핵심 서비스. |
| 인스턴스 생성 | 콘솔에서 AMI 선택 → 인스턴스 유형 선택 → 키 페어 생성 → 보안 그룹 설정 → 시작(Launch)하는 과정을 수행 가능. |
| SSH 접속 | 키 페어(.pem)로 EC2 인스턴스에 SSH 접속하는 방법. chmod 400 key.pem + ssh -i key.pem ec2-user@IP를 실행 가능. |
| AMI (Amazon Machine Image) | 인스턴스의 템플릿. OS + 소프트웨어가 포함된 이미지. 커스텀 AMI를 만들어 동일 환경을 복제하는 용도를 설명 가능. |
| 인스턴스 유형 | t(범용, 버스트), m(범용), c(컴퓨팅), r(메모리), g/p(GPU) 패밀리 분류와 선택 기준(CPU/메모리/네트워크 요구사항)을 설명 가능. |
| 키 페어 | 퍼블릭 키(AWS에 저장) + 프라이빗 키(로컬 보관)로 SSH 인증. 프라이빗 키 분실 시 접속 불가함을 알고 있음. |
| 과금 모델 | On-Demand(시간당), Reserved(예약, 할인), Spot(경매, 최대 90% 할인, 중단 가능)의 차이와 선택 기준을 설명 가능. |

---

### Step 6. EC2 심화 — ELB, Auto Scaling Group, 배치 그룹

| 학습 항목 | 학습 목표 |
|----------|----------|
| ELB (Elastic Load Balancer) | 트래픽을 여러 EC2 인스턴스에 분산. ALB(L7, HTTP/HTTPS, 경로 기반 라우팅), NLB(L4, TCP/UDP, 초고성능), CLB(레거시)의 차이를 설명 가능. |
| 헬스 체크 | ELB가 인스턴스 상태를 주기적 확인. Unhealthy 인스턴스에 트래픽 차단. Spring Boot Actuator /actuator/health와 연동하는 패턴을 설명 가능. |
| Auto Scaling Group (ASG) | CPU 사용률 등 메트릭에 따라 EC2 인스턴스 수를 자동 증가/감소. 최소/최대/원하는 수(min/max/desired)의 의미를 설명 가능. |
| ELB + ASG 조합 | ALB가 트래픽 분산 + ASG가 인스턴스 수 조절 → 수요에 따른 자동 확장 아키텍처를 설명 가능. |
| 시작 템플릿 (Launch Template) | ASG가 새 인스턴스를 생성할 때 사용하는 설정(AMI, 인스턴스 유형, 보안 그룹, 사용자 데이터). |

---

### Step 7. S3 — 버킷, 객체, 스토리지 클래스, 정적 호스팅

| 학습 항목 | 학습 목표 |
|----------|----------|
| S3란 | Simple Storage Service. 무제한 객체 스토리지. 파일(객체)을 버킷에 저장. 내구성 99.999999999%(11 9's). |
| 버킷과 객체 | 버킷: 최상위 컨테이너(글로벌 고유 이름). 객체: 파일 + 메타데이터. 키(경로)로 식별. |
| 스토리지 클래스 | Standard(자주 접근), Standard-IA(비자주), Glacier(아카이브, 복원 시 수 분~시간), Glacier Deep Archive(최저 비용). 접근 빈도에 따른 선택 기준을 설명 가능. |
| 버전 관리 | Versioning으로 객체의 모든 버전을 보존. 실수로 삭제해도 복구 가능. |
| 접근 제어 | 버킷 정책(JSON), ACL, IAM 정책으로 접근 제어. 퍼블릭 접근 차단 설정의 중요성을 설명 가능. |
| 정적 웹 호스팅 | S3 버킷으로 정적 웹사이트(HTML/CSS/JS) 호스팅. CloudFront(CDN)와 조합하는 패턴을 설명 가능. |
| 실무 활용 | 파일 업로드(이미지, 문서), 백업, 로그 저장, 데이터 레이크 등 활용 사례를 설명 가능. |

---

### Step 8. RDS — 관계형 DB 서비스, Multi-AZ, Read Replica

| 학습 항목 | 학습 목표 |
|----------|----------|
| RDS란 | Relational Database Service. 관리형 DB(Oracle, MySQL, PostgreSQL, MariaDB, SQL Server, Aurora). 패치, 백업, 복제를 AWS가 관리. |
| RDS vs 직접 EC2에 DB 설치 | RDS: 자동 백업/패치/모니터링, Multi-AZ 원클릭. EC2: 전부 수동. RDS를 선택하는 이유를 설명 가능. |
| Multi-AZ | 주 DB와 대기 DB(Standby)를 다른 AZ에 동기 복제. 주 DB 장애 시 자동 페일오버. 고가용성(HA)의 핵심을 설명 가능. |
| Read Replica | 읽기 전용 복제본. 읽기 부하를 분산. 비동기 복제이므로 약간의 지연(Lag) 발생 가능. Multi-AZ와의 차이(Multi-AZ는 HA, Read Replica는 읽기 성능)를 설명 가능. |
| 백업 | 자동 백업(일일 스냅샷 + 트랜잭션 로그, 최대 35일 보존), 수동 스냅샷(사용자가 직접)의 차이를 설명 가능. |
| 파라미터 그룹 | DB 설정(max_connections, character_set 등)을 그룹으로 관리. 직접 DB에 접속하지 않고 AWS에서 설정하는 방법을 알고 있음. |
| Spring Boot 연동 | application.yml에서 spring.datasource.url에 RDS 엔드포인트를 설정하는 방법. |

---

### Step 9. ECS — 컨테이너 서비스, Fargate vs EC2 모드

| 학습 항목 | 학습 목표 |
|----------|----------|
| ECS란 | Elastic Container Service. AWS 자체 컨테이너 오케스트레이션. Docker 컨테이너를 클러스터에서 실행/관리. |
| ECS 핵심 개념 | Task Definition(컨테이너 정의: 이미지, CPU/메모리, 포트), Service(Task를 원하는 수만큼 유지), Cluster(인프라 그룹)의 관계를 설명 가능. |
| Fargate vs EC2 모드 | Fargate: 서버리스(인스턴스 관리 불필요, Task 단위 과금). EC2 모드: EC2 인스턴스 위에서 실행(인스턴스 관리 필요, 비용 제어 유리). 선택 기준을 설명 가능. |
| ECS vs EKS | ECS: AWS 전용, 단순, AWS 서비스와 긴밀 통합. EKS: K8s 표준, 이식성, 복잡. "K8s 경험이 있거나 멀티 클라우드 필요 → EKS, AWS에 올인 + 단순함 → ECS"를 설명 가능. |
| ECR (Elastic Container Registry) | Docker 이미지를 저장하는 AWS 프라이빗 레지스트리. Docker Hub 대안으로 사용하는 이유(보안, 속도, IAM 통합)를 설명 가능. |

---

### Step 10. EKS — Kubernetes on AWS

| 학습 항목 | 학습 목표 |
|----------|----------|
| EKS란 | Elastic Kubernetes Service. AWS 관리형 K8s. Control Plane을 AWS가 관리(etcd, API server 등). Worker Node만 사용자가 관리. |
| EKS 아키텍처 | AWS가 관리하는 Control Plane + 사용자의 Worker Node(EC2 또는 Fargate)의 구조를 설명 가능. |
| 노드 그룹 | Managed Node Group(AWS가 EC2 인스턴스 관리), Self-managed(직접 관리), Fargate(서버리스)의 차이와 선택 기준을 설명 가능. |
| EKS + ALB Ingress Controller | AWS ALB를 K8s Ingress로 사용하는 방법. AWS Load Balancer Controller의 역할을 설명 가능. |
| EKS 배포 실습 | eksctl로 클러스터 생성 → kubectl로 앱 배포 → Service/Ingress로 외부 노출하는 전체 흐름을 설명 가능. |
| K8s 학습과의 연계 | 학습_11에서 배운 K8s 리소스(Deployment, Service, Ingress, Helm 등)를 EKS에 그대로 적용 가능함을 이해. |

---

### Step 11. Lambda — 서버리스 컴퓨팅

| 학습 항목 | 학습 목표 |
|----------|----------|
| Lambda란 | 서버 관리 없이 코드를 실행하는 서버리스 컴퓨팅. 이벤트 트리거(API Gateway 요청, S3 업로드, SQS 메시지 등)로 실행. 실행 시간만 과금. |
| Lambda 특징 | 최대 실행 시간 15분, 메모리 128MB~10GB, 콜드 스타트(첫 실행 지연), 무상태(Stateless). 각 특징의 영향을 설명 가능. |
| Lambda 활용 사례 | API 백엔드(API Gateway + Lambda), 파일 처리(S3 업로드 → Lambda 실행), 스케줄링(EventBridge → Lambda), 데이터 변환. |
| 콜드 스타트 문제 | 함수가 일정 시간 미호출 시 컨테이너가 폐기 → 다음 호출 시 새 컨테이너 생성으로 지연 발생. Java는 콜드 스타트가 특히 긴 이유(JVM 기동)와 대응(Provisioned Concurrency, GraalVM Native Image)을 설명 가능. |
| Lambda vs EC2/ECS 선택 | 짧은 실행, 이벤트 기반, 간헐적 트래픽 → Lambda. 장시간 실행, 지속적 트래픽, 상태 유지 → EC2/ECS. |

---

### Step 12. 기타 핵심 서비스 — SQS, SNS, CloudWatch, Route 53

| 학습 항목 | 학습 목표 |
|----------|----------|
| SQS (Simple Queue Service) | 관리형 메시지 큐. Standard(순서 보장 X, 최소 1회 전달) vs FIFO(순서 보장, 정확히 1회 전달)의 차이를 설명 가능. Kafka와의 차이(SQS: 단순 큐/서비스 분리, Kafka: 이벤트 스트리밍/재생)를 설명 가능. |
| SNS (Simple Notification Service) | Pub/Sub 메시지 서비스. 토픽에 발행 → 여러 구독자(SQS, Lambda, 이메일, HTTP)에 전달. SNS + SQS 팬아웃(Fan-out) 패턴을 설명 가능. |
| CloudWatch | 모니터링 + 로그 + 알림. 메트릭(CPU, 네트워크), 로그(Log Groups), 알람(임계값 초과 시 알림/ASG 트리거)의 역할을 설명 가능. |
| Route 53 | 관리형 DNS 서비스. 도메인 등록 + DNS 라우팅(단순, 가중치, 지연 시간, 장애 조치). 헬스 체크 기반 페일오버를 설명 가능. |
| CloudFront | CDN 서비스. S3/EC2 앞에 배치하여 전 세계 엣지 서버에서 콘텐츠 캐싱. 지연시간 감소 + DDoS 방어 효과를 설명 가능. |

---

### Step 13. 비용 관리 — 과금 구조, 비용 최적화, 프리 티어 한도

| 학습 항목 | 학습 목표 |
|----------|----------|
| AWS 과금 원칙 | 사용한 만큼 지불(Pay-as-you-go). 데이터 전송 아웃바운드만 과금(인바운드 무료). |
| 주요 비용 항목 | EC2(인스턴스 시간), RDS(인스턴스 시간 + 스토리지), S3(저장 용량 + 요청 수), 데이터 전송(리전 간/인터넷 아웃바운드)을 설명 가능. |
| 비용 최적화 전략 | Reserved Instance(1~3년 예약 할인), Spot Instance(경매 할인), 사용 안 하는 리소스 삭제, 적절한 인스턴스 사이징, S3 스토리지 클래스 최적화를 설명 가능. |
| AWS Cost Explorer | 비용을 서비스별/태그별로 분석하는 도구의 존재를 알고 있음. |
| Billing Alert | 예상 비용이 임계값 초과 시 알림 설정. 프리 티어 학습 중 과금 방지에 필수. |
| 프리 티어 함정 | EBS 볼륨, Elastic IP(미사용 시 과금), NAT 게이트웨이(시간당 과금) 등 프리 티어에 포함되지 않는 서비스를 알고 있음. |

---

### Step 14. AWS 아키텍처 패턴 — 3-Tier, 서버리스, 컨테이너 기반

| 학습 항목 | 학습 목표 |
|----------|----------|
| 3-Tier 아키텍처 | ALB(웹) → EC2/ECS(앱) → RDS(DB). 퍼블릭/프라이빗 서브넷 분리. 가장 전통적인 AWS 아키텍처를 그림으로 그릴 수 있음. |
| 컨테이너 기반 아키텍처 | ECR(이미지 저장) → ECS Fargate 또는 EKS(실행) → ALB(라우팅) → RDS/ElastiCache(데이터). |
| 서버리스 아키텍처 | API Gateway → Lambda → DynamoDB/S3. 서버 관리 없음, 자동 확장, 이벤트 기반. 적합한 경우(API, 배치, 이벤트 처리)를 설명 가능. |
| 이벤트 기반 아키텍처 | SNS/SQS/EventBridge로 서비스 간 비동기 통신. 결합도 감소. Lambda + SQS 조합 패턴을 설명 가능. |
| "이 아키텍처를 AWS에서 구성하면?" | 시스템 디자인 면접에서 "이 시스템을 AWS로 구성하라"에 적절한 서비스를 선택하여 아키텍처를 그릴 수 있음. |

---

## 3. 자가 검증

### 기초
- [ ] "온프레미스 vs 클라우드 차이" 설명 가능
- [ ] "리전과 AZ의 차이" + Multi-AZ의 목적 설명 가능
- [ ] AWS CLI로 기본 명령어(s3 ls, ec2 describe-instances) 실행 가능

### 보안/네트워크
- [ ] "IAM 사용자 vs 역할(Role) 차이" + 최소 권한 원칙 설명 가능
- [ ] "VPC 3-Tier 구조(퍼블릭/프라이빗 서브넷)" 그림으로 그릴 수 있음
- [ ] "보안 그룹 vs NACL 차이" 설명 가능

### 컴퓨팅/스토리지
- [ ] EC2 인스턴스를 생성하고 SSH 접속 가능
- [ ] "On-Demand vs Reserved vs Spot 차이" 설명 가능
- [ ] "S3 스토리지 클래스 선택 기준" 설명 가능
- [ ] "RDS Multi-AZ vs Read Replica 차이" 설명 가능

### 컨테이너
- [ ] "ECS vs EKS 선택 기준" 설명 가능
- [ ] "Fargate vs EC2 모드 차이" 설명 가능
- [ ] EKS에 Spring Boot 앱 배포 가능

### 서버리스/기타
- [ ] "Lambda 콜드 스타트란? Java에서 왜 심한가?" 설명 가능
- [ ] "SQS vs Kafka 차이" 설명 가능
- [ ] "SNS + SQS 팬아웃 패턴" 설명 가능

### 설계/비용
- [ ] AWS 콘솔 + CLI로 인프라(VPC+EC2+RDS+S3) 구성 가능
- [ ] "이 시스템을 AWS로 구성하라" → 적절한 서비스 선택 + 아키텍처 그림 가능
- [ ] "프리 티어 함정" 3가지 이상 설명 가능

---

## 4. 진행 상태

| Step | 항목 | 상태 |
|------|------|------|
| Step 1 | 클라우드 개요 | 미시작 |
| Step 2 | AWS 기본 | 미시작 |
| Step 3 | IAM | 미시작 |
| Step 4 | VPC | 미시작 |
| Step 5 | EC2 기본 | 미시작 |
| Step 6 | EC2 심화 (ELB, ASG) | 미시작 |
| Step 7 | S3 | 미시작 |
| Step 8 | RDS | 미시작 |
| Step 9 | ECS | 미시작 |
| Step 10 | EKS | 미시작 |
| Step 11 | Lambda | 미시작 |
| Step 12 | 기타 (SQS, SNS, CloudWatch, Route 53) | 미시작 |
| Step 13 | 비용 관리 | 미시작 |
| Step 14 | AWS 아키텍처 패턴 | 미시작 |

---

## 5. 참고 자료 (보조용)

| 자료 | 용도 |
|------|------|
| AWS 공식 문서 (docs.aws.amazon.com) | 전 Step 레퍼런스 |
| AWS Well-Architected Framework | Step 14 보조. 아키텍처 설계 원칙 |
| AWS 프리 티어 안내 (aws.amazon.com/free) | Step 2, 13 보조. 과금 방지 |

---

> 이 문서는 Claude가 미래 세션에서 읽고 학습을 안내하기 위한 가이드입니다.
> 사용자가 "AWS 공부하자" 또는 "Step N 하자"라고 하면, 진행 상태를 확인하고 다음 미시작 Step부터 학습_템플릿.md 형식으로 진행합니다.
> 선수 조건: Docker(학습_09), K8s(학습_11) 학습 후 진행 권장 (ECS/EKS 이해를 위해).
