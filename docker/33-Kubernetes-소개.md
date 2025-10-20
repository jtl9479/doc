# 섹션 33: Kubernetes 소개

> **학습 목표**: Kubernetes의 핵심 개념과 아키텍처를 이해하고, Minikube로 로컬 클러스터를 구성하며, kubectl 명령어로 Pod, Deployment, Service를 생성하고 관리할 수 있습니다.

**⏱️ 예상 학습 시간**: 4-5시간
**난이도**: ⭐⭐⭐⭐⭐ (5개/5개)

---

## 목차
1. [왜 Kubernetes인가?](#왜-kubernetes인가)
2. [Kubernetes 아키텍처](#kubernetes-아키텍처)
3. [핵심 개념](#핵심-개념)
4. [Minikube로 시작하기](#minikube로-시작하기)
5. [kubectl 기본 명령어](#kubectl-기본-명령어)
6. [YAML로 리소스 정의](#yaml로-리소스-정의)
7. [LK-Trade 배포하기](#lk-trade를-kubernetes에-배포하기)

---

## 💡 왜 Kubernetes인가?

### 실무 배경

**"Docker Swarm으로 시작했는데, 규모가 커지니 한계가 보입니다!"**

#### ❌ Docker Swarm의 한계

```
문제 1: 복잡한 네트워킹 어려움
- 증상: 서비스 50개 넘어가니 네트워크 관리 복잡
- 영향: Ingress 설정, 서비스 메시 구현 어려움
- 비용: 네트워킹 문제로 장애 주 1회 발생

문제 2: 고급 스케줄링 제한
- 증상: GPU 필요한 컨테이너, 특정 디스크 타입 등 요구사항
- 영향: 리소스 최적 배치 불가능
- 비용: 서버 리소스 30% 낭비

문제 3: 모니터링/로깅 생태계 부족
- 증상: 커스텀 모니터링 시스템 구축 필요
- 영향: 개발 및 운영 부담 증가
- 비용: 모니터링 시스템 개발에 인력 2명 투입

문제 4: 엔터프라이즈 기능 부족
- 증상: RBAC, Admission Controller, Operators 등 없음
- 영향: 복잡한 워크플로우 구현 어려움
- 비용: 직접 개발 또는 포기
```

#### ✅ Kubernetes를 사용하면

```
해결책 1: 풍부한 네트워킹 기능
- 방법: Ingress, Service Mesh (Istio), Network Policies
- 효과: 복잡한 네트워킹 요구사항 해결
- 절감: 네트워킹 장애 90% 감소

해결책 2: 강력한 스케줄링
- 방법: Node Selector, Affinity, Taints & Tolerations
- 효과: GPU, SSD, 메모리 등 리소스 최적 배치
- 절감: 서버 비용 30% 절감

해결책 3: 풍부한 생태계
- 방법: Prometheus, Grafana, ELK, Helm, Operators
- 효과: 검증된 도구 즉시 사용
- 절감: 개발 인력 2명 → 0명

해결책 4: 엔터프라이즈급 기능
- 방법: RBAC, CRD, Operators, Multi-tenancy
- 효과: 복잡한 시스템 구축 가능
- 절감: 장기적 확장성 확보
```

### 수치로 보는 효과

| 지표 | Docker Swarm | Kubernetes | 개선율 |
|------|-------------|------------|--------|
| 최대 권장 서비스 수 | 50개 | 수천 개 | **99%↑** |
| 네트워킹 기능 | 기본적 | 매우 풍부 | **80%↑** |
| 생태계 크기 | 소규모 | 매우 큼 | **95%↑** |
| 기업 채택률 | 20% | 80% | **300%↑** |
| 채용 시장 | 어려움 | 쉬움 | **90%↑** |

---

## 🔍 실생활 비유로 이해하기

### 비유 1: 대규모 물류 센터의 자동화 시스템

```
Amazon 물류 센터                    Kubernetes
==================                  ===========
📦 수만 개의 택배 상자          →    수천 개의 컨테이너
🤖 자동 분류 로봇               →    Scheduler (자동 배치)
📊 중앙 관제 시스템              →    Control Plane
🚛 수백 대의 배송 트럭          →    Worker Nodes
📱 실시간 추적 시스템            →    kube-apiserver
🔧 자동 수리 로봇               →    Self-healing
⚖️ 부하 분산 컨베이어            →    Service (Load Balancer)
📋 배송 규칙 엔진               →    Controllers

소규모 택배 회사 (Docker Swarm):
- 직원 10명이 수동으로 분류
- 간단한 시스템
- 하루 1,000개 처리 가능

대규모 물류 센터 (Kubernetes):
- 완전 자동화 시스템
- 복잡하지만 효율적
- 하루 100만 개 처리 가능
- 실시간 최적화
- 장애 자동 복구
```

### 비유 2: 스마트 빌딩 관리 시스템

```
스마트 빌딩                      Kubernetes
==========                      ===========
🏢 50층 초고층 빌딩             →    대규모 클러스터
🎛️ 중앙 제어 시스템             →    Control Plane
🌡️ 각 층의 온도 센서            →    kubelet (에이전트)
🚪 자동문, 엘리베이터           →    Pods
📊 에너지 관리 시스템           →    Resource Management
🚨 화재 감지 및 대응            →    Health Checks
🔐 출입 통제 시스템             →    RBAC
📱 스마트폰 앱                  →    kubectl

일반 건물 (Docker Swarm):
- 층마다 개별 관리
- 간단한 시스템
- 10층 건물에 적합

스마트 빌딩 (Kubernetes):
- 중앙 통합 관리
- 복잡한 자동화
- 100층 건물도 관리 가능
- AI 기반 최적화
- 에너지 효율 극대화
```

### 비유 3: 항공 교통 관제 시스템

```
항공 교통 관제                  Kubernetes
==============                  ===========
✈️ 수백 대의 비행기             →    수천 개의 Pods
🗼 관제탑                       →    Control Plane
📡 레이더 시스템                →    Monitoring (Prometheus)
🛬 활주로 배정                  →    Scheduler
🚨 긴급 상황 대응               →    Self-healing
📊 실시간 추적                  →    Dashboard
🗺️ 비행 경로 최적화            →    Resource Optimization
📻 무선 통신                    →    API Server

작은 공항 (Docker Swarm):
- 하루 10편 운항
- 수동 관제
- 간단한 시스템

국제 공항 (Kubernetes):
- 하루 1,000편 운항
- 자동화된 관제
- 복잡하지만 안전하고 효율적
- 실시간 최적화
- 장애 즉시 대응
```

---

## 왜 Kubernetes인가?

### 1. Docker Swarm의 한계

```
프로젝트 성장 시나리오
=====================

Phase 1: 소규모 (서비스 5개, 노드 3개)
→ Docker Swarm 충분 ✅

Phase 2: 중규모 (서비스 20개, 노드 10개)
→ Docker Swarm 가능하지만 기능 부족
   - 복잡한 네트워킹 어려움
   - 고급 스케줄링 제한
   - 모니터링 도구 부족

Phase 3: 대규모 (서비스 100개+, 노드 50개+)
→ Kubernetes 필수 ⭐
   - 풍부한 기능
   - 강력한 생태계
   - 멀티 클라우드 지원
   - 엔터프라이즈급 기능
```

### 2. Kubernetes의 장점

```
┌─────────────────────────────────────────────────┐
│ Kubernetes가 해결하는 문제들                    │
├─────────────────────────────────────────────────┤
│ ✅ 자동 스케일링 (HPA, VPA, Cluster Autoscaler)│
│ ✅ 자가 치유 (Self-healing)                     │
│ ✅ 로드 밸런싱 (Service, Ingress)               │
│ ✅ 스토리지 오케스트레이션 (Persistent Volume) │
│ ✅ 자동 롤아웃 & 롤백                           │
│ ✅ Secret & ConfigMap 관리                      │
│ ✅ 배치 실행 (Jobs, CronJobs)                   │
│ ✅ 리소스 최적화 (Resource Quotas, Limits)     │
│ ✅ 멀티 클라우드 (AWS, GCP, Azure)              │
│ ✅ 풍부한 생태계 (Helm, Operators, etc)        │
└─────────────────────────────────────────────────┘
```

---

## Kubernetes 아키텍처

### 1. 전체 구조

```
Kubernetes 클러스터
===================

┌───────────────────────────────────────────────────────────┐
│                    Control Plane                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │  kube-apiserver                                  │    │
│  │  (모든 요청의 중앙 허브)                        │    │
│  └──────────────────────────────────────────────────┘    │
│         │                │               │                │
│         ↓                ↓               ↓                │
│  ┌──────────┐    ┌─────────────┐   ┌──────────────┐    │
│  │  etcd    │    │  Scheduler  │   │  Controller  │    │
│  │ (상태DB) │    │  (배치결정) │   │   Manager    │    │
│  └──────────┘    └─────────────┘   └──────────────┘    │
└───────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼──────┐   ┌───────▼──────┐   ┌───────▼──────┐
│  Worker 1    │   │  Worker 2    │   │  Worker 3    │
│ ┌──────────┐ │   │ ┌──────────┐ │   │ ┌──────────┐ │
│ │ kubelet  │ │   │ │ kubelet  │ │   │ │ kubelet  │ │
│ │ (에이전트)│   │ │ (에이전트)│   │ │ (에이전트)│
│ └──────────┘ │   │ └──────────┘ │   │ └──────────┘ │
│ ┌──────────┐ │   │ ┌──────────┐ │   │ ┌──────────┐ │
│ │Pod Pod   │ │   │ │Pod Pod   │ │   │ │Pod Pod   │ │
│ │  Pod     │ │   │ │  Pod     │ │   │ │  Pod     │ │
│ └──────────┘ │   │ └──────────┘ │   │ └──────────┘ │
└──────────────┘   └──────────────┘   └──────────────┘
```

### 2. 주요 컴포넌트 설명

```
Control Plane (마스터 노드)
==========================

1. kube-apiserver
   - 모든 요청의 진입점
   - kubectl 명령 처리
   - REST API 제공

2. etcd
   - 클러스터 상태 저장 (키-값 DB)
   - 분산 일관성 보장
   - 백업 필수!

3. kube-scheduler
   - 어느 노드에 Pod 배치할지 결정
   - 리소스, 제약조건 고려

4. kube-controller-manager
   - 여러 컨트롤러 실행
   - ReplicaSet, Deployment 등 관리
   - 원하는 상태 유지


Worker Node (워커 노드)
======================

1. kubelet
   - 각 노드에서 실행되는 에이전트
   - Pod 생성, 관리
   - 컨테이너 헬스 체크

2. kube-proxy
   - 네트워킹 담당
   - Service 로드 밸런싱
   - iptables 규칙 관리

3. Container Runtime
   - Docker, containerd, CRI-O 등
   - 실제 컨테이너 실행
```

---

## 핵심 개념

### 1. Pod (가장 작은 배포 단위)

```
Pod = 하나 이상의 컨테이너 그룹
===================================

단일 컨테이너 Pod (일반적)
┌────────────────────┐
│      Pod           │
│  ┌──────────────┐  │
│  │  Container   │  │
│  │  (app)       │  │
│  └──────────────┘  │
│  192.168.1.10      │
└────────────────────┘


멀티 컨테이너 Pod (특수 케이스)
┌────────────────────────────────┐
│           Pod                  │
│  ┌──────────┐  ┌────────────┐ │
│  │ Main App │  │ Sidecar    │ │
│  │          │  │ (로그 수집)│ │
│  └──────────┘  └────────────┘ │
│  같은 IP, 같은 볼륨 공유       │
└────────────────────────────────┘

Pod 특징:
- 동일한 IP 주소 공유
- 동일한 Volume 공유
- localhost로 서로 통신
- 함께 스케줄링됨
```

### 2. ReplicaSet (복제 관리)

```
ReplicaSet: Pod의 복제본 관리
==============================

원하는 상태: replicas: 3
┌─────┐ ┌─────┐ ┌─────┐
│ Pod │ │ Pod │ │ Pod │
└─────┘ └─────┘ └─────┘

Pod 하나 죽으면?
┌─────┐ ┌─────┐   X
│ Pod │ │ Pod │

ReplicaSet이 자동으로 재생성:
┌─────┐ ┌─────┐ ┌─────┐
│ Pod │ │ Pod │ │ Pod │ (새로 생성)
└─────┘ └─────┘ └─────┘

항상 3개 유지!
```

### 3. Deployment (배포 관리)

```
Deployment: ReplicaSet + 롤링 업데이트
======================================

Deployment (v1.0)
    ↓
ReplicaSet (v1.0)
    ↓
┌─────┐ ┌─────┐ ┌─────┐
│ v1.0│ │ v1.0│ │ v1.0│
└─────┘ └─────┘ └─────┘

업데이트 → v2.0
───────────────

Deployment (v2.0)
    ↓
ReplicaSet (v2.0)
    ↓
┌─────┐ ┌─────┐ ┌─────┐
│ v2.0│ │ v2.0│ │ v1.0│ ← 점진적 교체
└─────┘ └─────┘ └─────┘

완료
┌─────┐ ┌─────┐ ┌─────┐
│ v2.0│ │ v2.0│ │ v2.0│
└─────┘ └─────┘ └─────┘

ReplicaSet (v1.0) 유지 (롤백용)
```

### 4. Service (네트워킹)

```
Service: Pod에 대한 고정 진입점
===============================

문제: Pod IP는 계속 변함
┌─────┐ ┌─────┐ ┌─────┐
│10.1 │ │10.2 │ │10.3 │
└─────┘ └─────┘ └─────┘
   ↓ Pod 재시작
┌─────┐ ┌─────┐ ┌─────┐
│10.5 │ │10.7 │ │10.9 │ ← IP 변경!
└─────┘ └─────┘ └─────┘


해결: Service로 고정 IP 제공
┌──────────────────────┐
│  Service: my-app     │
│  IP: 10.100.200.1    │ ← 고정 IP
└──────────────────────┘
         │
    ┌────┴────┐
    ↓    ↓    ↓
┌─────┐ ┌─────┐ ┌─────┐
│ Pod │ │ Pod │ │ Pod │ ← IP 변경 OK
└─────┘ └─────┘ └─────┘

Service가 자동으로 로드 밸런싱
```

---

## Minikube로 시작하기

### 1. Minikube 설치 (로컬 Kubernetes)

```bash
# Windows (Chocolatey)
choco install minikube

# macOS (Homebrew)
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# kubectl 설치 (Kubernetes CLI)
# Windows
choco install kubernetes-cli

# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# 설치 확인
minikube version
kubectl version --client
```

### 2. Minikube 시작

```bash
# Minikube 클러스터 시작
minikube start --driver=docker --cpus=4 --memory=8192

# 출력:
😄  minikube v1.32.0 on Windows 10
✨  Using the docker driver based on user configuration
👍  Starting control plane node minikube in cluster minikube
🚜  Pulling base image ...
🔥  Creating docker container (CPUs=4, Memory=8192MB) ...
🐳  Preparing Kubernetes v1.28.3 on Docker 24.0.7 ...
🔗  Configuring bridge CNI (Container Networking Interface) ...
🔎  Verifying Kubernetes components...
🌟  Enabled addons: storage-provisioner, default-storageclass
🏄  Done! kubectl is now configured to use "minikube" cluster

# 상태 확인
minikube status

# 출력:
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured

# kubectl 설정 확인
kubectl config current-context
# minikube

# 노드 확인
kubectl get nodes

# 출력:
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   1m    v1.28.3
```

### 3. 대시보드 열기

```bash
# Kubernetes 대시보드 시작
minikube dashboard

# 브라우저가 자동으로 열림
# 모든 리소스를 시각적으로 확인 가능
```

---

## kubectl 기본 명령어

### 1. 리소스 조회

```bash
# 모든 Pod 조회
kubectl get pods

# 모든 네임스페이스의 Pod
kubectl get pods --all-namespaces
kubectl get pods -A

# 상세 정보
kubectl get pods -o wide

# 특정 Pod 상세 정보
kubectl describe pod <pod-name>

# 모든 리소스 조회
kubectl get all

# Service 조회
kubectl get services
kubectl get svc

# Deployment 조회
kubectl get deployments
kubectl get deploy
```

### 2. 리소스 생성

```bash
# Deployment 생성
kubectl create deployment nginx --image=nginx:alpine

# 확인
kubectl get deployments
kubectl get pods

# 출력:
NAME                     READY   STATUS    RESTARTS   AGE
nginx-7c5ddbdf54-x7k2m   1/1     Running   0          10s

# 레플리카 수 조정
kubectl scale deployment nginx --replicas=3

# 확인
kubectl get pods

# 출력:
NAME                     READY   STATUS    RESTARTS   AGE
nginx-7c5ddbdf54-x7k2m   1/1     Running   0          1m
nginx-7c5ddbdf54-abc12   1/1     Running   0          10s
nginx-7c5ddbdf54-def34   1/1     Running   0          10s
```

### 3. Service 생성 (노출)

```bash
# Service 생성 (ClusterIP - 내부 접근만)
kubectl expose deployment nginx --port=80

# Service 생성 (NodePort - 외부 접근 가능)
kubectl expose deployment nginx --type=NodePort --port=80

# Service 생성 (LoadBalancer - 클라우드 환경)
kubectl expose deployment nginx --type=LoadBalancer --port=80

# Service 확인
kubectl get services

# 출력:
NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
nginx        NodePort    10.96.123.45    <none>        80:32000/TCP   10s

# Minikube에서 Service URL 얻기
minikube service nginx --url

# 출력:
http://192.168.49.2:32000

# 브라우저에서 접속
curl http://192.168.49.2:32000
```

### 4. 로그 및 디버깅

```bash
# Pod 로그 확인
kubectl logs <pod-name>

# 실시간 로그
kubectl logs -f <pod-name>

# 특정 컨테이너 로그 (멀티 컨테이너 Pod)
kubectl logs <pod-name> -c <container-name>

# Pod 내부 접속
kubectl exec -it <pod-name> -- /bin/sh

# 명령 실행
kubectl exec <pod-name> -- ls -la /app

# 파일 복사 (Pod → 로컬)
kubectl cp <pod-name>:/path/to/file ./local-file

# 파일 복사 (로컬 → Pod)
kubectl cp ./local-file <pod-name>:/path/to/file
```

### 5. 리소스 삭제

```bash
# Pod 삭제
kubectl delete pod <pod-name>

# Deployment 삭제 (관련 Pod도 삭제)
kubectl delete deployment nginx

# Service 삭제
kubectl delete service nginx

# 모두 삭제
kubectl delete all --all

# 네임스페이스 삭제
kubectl delete namespace <namespace>
```

---

## YAML로 리소스 정의

### 1. Deployment YAML

```yaml
# nginx-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 2. Service YAML

```yaml
# nginx-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  type: NodePort
  ports:
  - protocol: TCP
    port: 80          # Service 포트
    targetPort: 80    # Container 포트
    nodePort: 30080   # 외부 접근 포트 (30000-32767)
```

### 3. 적용 및 관리

```bash
# YAML 파일 적용
kubectl apply -f nginx-deployment.yaml
kubectl apply -f nginx-service.yaml

# 또는 한 번에
kubectl apply -f .

# 확인
kubectl get all

# YAML 파일 수정 후 다시 적용
kubectl apply -f nginx-deployment.yaml

# YAML 출력 (기존 리소스)
kubectl get deployment nginx-deployment -o yaml

# Dry-run (실제 적용 안 함, 검증만)
kubectl apply -f nginx-deployment.yaml --dry-run=client

# 삭제
kubectl delete -f nginx-deployment.yaml
kubectl delete -f nginx-service.yaml
```

---

## LK-Trade를 Kubernetes에 배포하기

### 1. Namespace 생성

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: lk-trade
```

```bash
kubectl apply -f namespace.yaml
kubectl get namespaces
```

### 2. ConfigMap (설정 정보)

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: lk-trade-config
  namespace: lk-trade
data:
  SPRING_PROFILES_ACTIVE: "prod"
  TZ: "Asia/Seoul"
  POSTGRES_HOST: "postgres-service"
  POSTGRES_PORT: "5432"
  POSTGRES_DB: "lk_trade"
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
```

### 3. Secret (비밀 정보)

```bash
# Secret 생성 (명령어)
kubectl create secret generic lk-trade-secrets \
  --from-literal=db-password='super_secure_password' \
  --from-literal=jwt-secret='jwt_secret_key_here' \
  --namespace=lk-trade

# 또는 YAML로
```

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: lk-trade-secrets
  namespace: lk-trade
type: Opaque
data:
  # base64 인코딩 필요
  db-password: c3VwZXJfc2VjdXJlX3Bhc3N3b3Jk
  jwt-secret: and0X3NlY3JldF9rZXlfaGVyZQ==
```

```bash
# base64 인코딩
echo -n 'super_secure_password' | base64
# c3VwZXJfc2VjdXJlX3Bhc3N3b3Jk

# Secret 확인 (값은 숨겨짐)
kubectl get secrets -n lk-trade

# Secret 값 확인 (디코딩)
kubectl get secret lk-trade-secrets -n lk-trade -o jsonpath='{.data.db-password}' | base64 -d
```

### 4. User Service Deployment

```yaml
# user-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  namespace: lk-trade
  labels:
    app: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
        version: v1
    spec:
      containers:
      - name: user-service
        image: lk-trade/user-service:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8080
          name: http
        env:
        - name: SPRING_PROFILES_ACTIVE
          valueFrom:
            configMapKeyRef:
              name: lk-trade-config
              key: SPRING_PROFILES_ACTIVE
        - name: SPRING_DATASOURCE_URL
          value: "jdbc:postgresql://$(POSTGRES_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB)"
        - name: SPRING_DATASOURCE_USERNAME
          value: "lk_admin"
        - name: SPRING_DATASOURCE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: lk-trade-secrets
              key: db-password
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: lk-trade-secrets
              key: jwt-secret
        envFrom:
        - configMapRef:
            name: lk-trade-config
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /actuator/health/liveness
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /actuator/health/readiness
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
```

### 5. User Service Service

```yaml
# user-service-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: user-service
  namespace: lk-trade
  labels:
    app: user-service
spec:
  selector:
    app: user-service
  type: ClusterIP
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 8080
    name: http
```

### 6. PostgreSQL (StatefulSet)

```yaml
# postgres-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: lk-trade
spec:
  serviceName: postgres-service
  replicas: 1
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
        image: postgres:16-alpine
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_DB
          valueFrom:
            configMapKeyRef:
              name: lk-trade-config
              key: POSTGRES_DB
        - name: POSTGRES_USER
          value: "lk_admin"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: lk-trade-secrets
              key: db-password
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: lk-trade
spec:
  selector:
    app: postgres
  type: ClusterIP
  ports:
  - port: 5432
    targetPort: 5432
```

### 7. 배포

```bash
# 모든 리소스 배포
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f postgres-statefulset.yaml
kubectl apply -f user-service-deployment.yaml
kubectl apply -f user-service-service.yaml

# 또는 디렉토리 전체
kubectl apply -f k8s/

# 확인
kubectl get all -n lk-trade

# 출력:
NAME                               READY   STATUS    RESTARTS   AGE
pod/user-service-7d5f6c8d9-abc12   1/1     Running   0          1m
pod/user-service-7d5f6c8d9-def34   1/1     Running   0          1m
pod/user-service-7d5f6c8d9-ghi56   1/1     Running   0          1m
pod/postgres-0                     1/1     Running   0          2m

NAME                       TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
service/user-service       ClusterIP   10.96.10.20     <none>        8080/TCP   1m
service/postgres-service   ClusterIP   10.96.10.30     <none>        5432/TCP   2m

NAME                           READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/user-service   3/3     3            3           1m

# 로그 확인
kubectl logs -f deployment/user-service -n lk-trade

# Service 테스트 (클러스터 내부)
kubectl run -it --rm debug --image=alpine --restart=Never -- sh
# wget -qO- http://user-service.lk-trade:8080/actuator/health
```

---

## 👨‍💻 주니어 개발자 시나리오

### 시나리오 1: 첫 minikube 실행 - "이게 진짜 Kubernetes인가요?"

**상황**:
```
팀장: "로컬에서 Kubernetes 연습해봐요. Minikube 설치하고 시작해보세요."
주니어 A (당황): "Kubernetes는 서버 여러 대 필요한 거 아니에요?"
```

**단계별 해결**:
```bash
# Step 1: Minikube 설치
$ choco install minikube  # Windows
$ brew install minikube   # macOS

# Step 2: kubectl 설치
$ choco install kubernetes-cli  # Windows
$ brew install kubectl          # macOS

# Step 3: Minikube 시작
$ minikube start --driver=docker --cpus=2 --memory=4096

# 출력:
😄  minikube v1.32.0 on Windows 10
✨  Using the docker driver
👍  Starting control plane node minikube in cluster minikube
🚜  Pulling base image ...
🔥  Creating docker container (CPUs=2, Memory=4096MB) ...
🐳  Preparing Kubernetes v1.28.3 on Docker 24.0.7 ...
🔎  Verifying Kubernetes components...
🏄  Done! kubectl is now configured to use "minikube" cluster

# Step 4: 클러스터 확인
$ kubectl get nodes

# 출력:
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   1m    v1.28.3

# Step 5: 첫 Pod 생성
$ kubectl run nginx --image=nginx:alpine

# Step 6: 확인
$ kubectl get pods

# 출력:
NAME    READY   STATUS    RESTARTS   AGE
nginx   1/1     Running   0          10s

✅ Kubernetes 시작 완료!

# Step 7: 대시보드 열어보기
$ minikube dashboard
# 브라우저가 자동으로 열림 - 시각적으로 모든 리소스 확인!
```

**배운 점**:
- Minikube = 로컬 1대에서 Kubernetes 실습 가능
- Docker 컨테이너 안에서 Kubernetes 실행
- kubectl 명령어는 실제 클러스터와 동일
- 학습 및 개발용으로 완벽

---

### 시나리오 2: Docker Compose를 Kubernetes로 변환

**상황**:
```
주니어 B: "기존 docker-compose.yml이 있는데 Kubernetes로 어떻게 옮기죠?"
시니어: "YAML 형식은 비슷하지만 개념이 좀 달라요. 차근차근 변환해봅시다."
```

**단계별 해결**:
```yaml
# 기존 docker-compose.yml
version: '3.8'
services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    replicas: 3  # ← Swarm 문법

# ↓ Kubernetes로 변환

# 1. Deployment (web.yaml)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3  # ← Kubernetes 문법
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80

---
# 2. Service (web-service.yaml)
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web
  type: LoadBalancer  # Minikube에서는 NodePort 권장
  ports:
  - port: 80
    targetPort: 80
```

```bash
# Step 1: 적용
$ kubectl apply -f web.yaml

# Step 2: 확인
$ kubectl get deployments
NAME   READY   UP-TO-DATE   AVAILABLE   AGE
web    3/3     3            3           10s

$ kubectl get pods
NAME                   READY   STATUS    RESTARTS   AGE
web-7c5ddbdf54-abc12   1/1     Running   0          10s
web-7c5ddbdf54-def34   1/1     Running   0          10s
web-7c5ddbdf54-ghi56   1/1     Running   0          10s

# Step 3: Service 생성
$ kubectl apply -f web-service.yaml

# Step 4: 접속 (Minikube)
$ minikube service web --url
http://192.168.49.2:32000

$ curl http://192.168.49.2:32000
# Nginx 응답 확인!

✅ 변환 완료!
```

**주요 차이점**:
```
docker-compose.yml                  Kubernetes YAML
==================                  ===============
services:                        →  Deployment + Service
  web:
    image: nginx                 →  spec.containers[0].image
    ports:                       →  Service.spec.ports
    replicas: 3                  →  Deployment.spec.replicas
    networks:                    →  (자동, Service 이름)
    volumes:                     →  PersistentVolumeClaim
    environment:                 →  ConfigMap + Secret
```

**배운 점**:
- Docker Compose는 단일 파일, Kubernetes는 여러 리소스
- Deployment (실행) + Service (네트워킹) 분리
- labels/selectors로 연결
- YAML 문법은 비슷하지만 개념 다름

---

### 시나리오 3: Pod가 계속 재시작됨 - "CrashLoopBackOff가 뭐죠?"

**상황**:
```
주니어 C: "Pod를 만들었는데 계속 재시작돼요! STATUS가 CrashLoopBackOff라고 나와요."
```

**단계별 해결**:
```bash
# Step 1: 상태 확인
$ kubectl get pods

# 출력:
NAME                        READY   STATUS             RESTARTS   AGE
myapp-7c5ddbdf54-abc12      0/1     CrashLoopBackOff   5          3m

# CrashLoopBackOff = 계속 죽고 재시작 중

# Step 2: 상세 정보 확인
$ kubectl describe pod myapp-7c5ddbdf54-abc12

# 출력 (중요 부분):
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
  Warning  BackOff    30s (x10 over 3m)  kubelet            Back-off restarting failed container
  Warning  Failed     30s (x10 over 3m)  kubelet            Error: couldn't find key DB_HOST in ConfigMap

# 아하! ConfigMap에 DB_HOST 키가 없음

# Step 3: 로그 확인
$ kubectl logs myapp-7c5ddbdf54-abc12

# 출력:
Error: DATABASE_URL is not set
Application failed to start

# Step 4: 문제 해결
# ConfigMap 생성
$ kubectl create configmap myapp-config \
  --from-literal=DB_HOST=postgres \
  --from-literal=DB_PORT=5432

# Step 5: Deployment 수정 (env 추가)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
      - name: myapp
        image: myapp:latest
        env:
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: myapp-config
              key: DB_HOST
        - name: DB_PORT
          valueFrom:
            configMapKeyRef:
              name: myapp-config
              key: DB_PORT

# Step 6: 재적용
$ kubectl apply -f myapp-deployment.yaml

# Step 7: 확인
$ kubectl get pods

# 출력:
NAME                        READY   STATUS    RESTARTS   AGE
myapp-7c5ddbdf54-def34      1/1     Running   0          10s

✅ 해결!
```

**CrashLoopBackOff 디버깅 체크리스트**:
```bash
□ kubectl describe pod <pod-name>
  - Events 섹션 확인
  - 에러 메시지 찾기

□ kubectl logs <pod-name>
  - 애플리케이션 로그 확인
  - 시작 실패 원인 파악

□ 흔한 원인:
  - 환경 변수 누락 (ConfigMap, Secret)
  - 의존성 서비스 미실행 (DB, Redis 등)
  - 이미지 태그 오류
  - 리소스 부족 (메모리, CPU)
  - Liveness Probe 설정 오류
```

**배운 점**:
- `describe pod` 먼저 확인
- `logs`로 애플리케이션 로그 확인
- CrashLoopBackOff = 재시작 간격이 점점 길어짐
- ConfigMap/Secret 누락이 가장 흔한 원인

---

### 시나리오 4: kubectl 기본 명령어 익히기

**상황**:
```
주니어 D: "kubectl 명령어가 너무 많아요. 자주 쓰는 것만 알려주세요!"
```

**필수 명령어 10개**:
```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. 리소스 조회 (가장 많이 씀!)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$ kubectl get pods
$ kubectl get deployments
$ kubectl get services
$ kubectl get all  # 모든 리소스

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. 상세 정보 (문제 생길 때)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$ kubectl describe pod <pod-name>
$ kubectl describe deployment <deployment-name>

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. 로그 확인 (디버깅)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$ kubectl logs <pod-name>
$ kubectl logs -f <pod-name>  # 실시간
$ kubectl logs <pod-name> --tail=100  # 최근 100줄

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. Pod 내부 접속
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$ kubectl exec -it <pod-name> -- sh
$ kubectl exec <pod-name> -- ls -la /app

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. YAML 적용/삭제
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$ kubectl apply -f deployment.yaml
$ kubectl delete -f deployment.yaml

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. 스케일링
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$ kubectl scale deployment nginx --replicas=5

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. 이미지 업데이트 (배포)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$ kubectl set image deployment/nginx nginx=nginx:1.21

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. 롤아웃 관리
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$ kubectl rollout status deployment/nginx
$ kubectl rollout history deployment/nginx
$ kubectl rollout undo deployment/nginx  # 롤백

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 9. 네임스페이스
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$ kubectl get pods -n my-namespace
$ kubectl config set-context --current --namespace=my-namespace

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 10. 클러스터 정보
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$ kubectl cluster-info
$ kubectl get nodes
$ kubectl top nodes  # 리소스 사용량
$ kubectl top pods
```

**단축어 (Alias)**:
```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get services'
alias kgd='kubectl get deployments'
alias kdp='kubectl describe pod'
alias kl='kubectl logs'
alias kex='kubectl exec -it'

# 사용:
$ k get pods  # kubectl get pods
$ kgp         # kubectl get pods
$ kl nginx    # kubectl logs nginx
```

**배운 점**:
- 80% 시간을 `get`, `describe`, `logs`로 보냄
- 단축어 설정하면 생산성 3배 증가
- `-n` 옵션으로 네임스페이스 지정
- `--help`로 언제든지 도움말 확인 가능

---

## ❓ FAQ

<details>
<summary><strong>Q1: Kubernetes vs Docker Swarm, 어떤 걸 선택해야 하나요?</strong></summary>

**A**: **팀 규모, 프로젝트 복잡도, 학습 시간**을 고려하여 선택하세요.

**상세 설명**:

**Docker Swarm을 선택하세요**:
```
✅ 적합한 경우:
- 소~중규모 프로젝트 (서비스 50개 이하)
- 팀원 3-5명, Kubernetes 경험 없음
- 빠른 시작 필요 (1-2일 내 운영)
- Docker Compose에서 마이그레이션
- 복잡성 최소화 원함

실제 사례:
스타트업 A사 (서비스 20개, 노드 10개)
- Swarm 도입 후 3일 만에 운영 시작
- 운영 인력 1명으로 충분
- 문제 발생 시 빠른 디버깅
- 연간 인프라 비용 60% 절감
```

**Kubernetes를 선택하세요**:
```
✅ 적합한 경우:
- 중대규모 프로젝트 (서비스 100개 이상)
- 멀티 클라우드 (AWS, GCP, Azure)
- 복잡한 네트워킹 요구사항
- 풍부한 생태계 필요 (Helm, Istio, etc)
- 장기적 확장성 고려
- DevOps 팀 존재

실제 사례:
엔터프라이즈 B사 (서비스 500개, 노드 200개)
- Kubernetes로 복잡한 워크플로우 구현
- Helm으로 배포 자동화
- Istio로 서비스 메시 구축
- 멀티 클라우드 전략 (AWS + GCP)
```

**비교표**:

| 항목 | Docker Swarm | Kubernetes |
|------|-------------|------------|
| 학습 기간 | 1-3일 | 2-4주 |
| 설정 복잡도 | 낮음 ⭐ | 높음 ⭐⭐⭐⭐⭐ |
| 기능 풍부함 | 기본적 | 매우 풍부 |
| 커뮤니티 | 작음 | 거대함 |
| 채용 | 어려움 | 쉬움 (인기 높음) |
| 최대 권장 규모 | 50 서비스 | 무제한 |
| 클라우드 지원 | 제한적 | 완벽 |

**실용적 조언**:
```
Phase 1: 시작 단계
→ Docker Compose (로컬)
→ 학습 난이도: 쉬움

Phase 2: 소규모 프로덕션
→ Docker Swarm
→ 빠른 시작, 간단한 운영

Phase 3: 중대규모 성장
→ Kubernetes로 전환
→ 복잡하지만 강력

💡 처음부터 Kubernetes?
- 팀에 K8s 경험자 있으면: Yes
- 없으면: Swarm으로 시작 → 필요시 전환
```

</details>

<details>
<summary><strong>Q2: Kubernetes 학습 난이도가 높은 이유는 무엇인가요?</strong></summary>

**A**: **개념이 많고, 추상화 레벨이 높으며, 생태계가 방대**하기 때문입니다.

**상세 설명**:

**왜 어려운가?**

**1. 개념이 많음**:
```
Docker Compose 개념 (5개):
- service
- volume
- network
- environment
- ports

Kubernetes 핵심 개념 (15개 이상):
- Pod
- ReplicaSet
- Deployment
- Service
- Ingress
- ConfigMap
- Secret
- PersistentVolume
- PersistentVolumeClaim
- Namespace
- StatefulSet
- DaemonSet
- Job
- CronJob
- HorizontalPodAutoscaler
... 그리고 더 많음
```

**2. 추상화 레벨이 높음**:
```
Docker Compose (직관적):
services:
  web:
    image: nginx
    ports:
      - "80:80"

Kubernetes (여러 리소스 조합):
# Deployment (Pod 관리)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80

---
# Service (네트워킹)
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 80
```

**3. 용어가 헷갈림**:
```
Docker         Kubernetes
======         ==========
Container   →  Pod (1개 이상의 컨테이너)
service     →  Deployment + Service
stack       →  Namespace + 여러 리소스
replica     →  ReplicaSet
```

**4. 에러 메시지가 복잡함**:
```
Docker Compose 에러 (이해하기 쉬움):
ERROR: cannot start service web:
       port is already allocated

Kubernetes 에러 (해석 필요):
Warning  FailedScheduling  pod/web-7c5ddbdf54-abc12
         0/1 nodes are available:
         1 Insufficient memory.
```

**학습 전략**:

**1단계: 기본 개념 (1주)**
```
- Pod: 가장 작은 배포 단위
- Deployment: Pod 관리
- Service: 네트워킹
- ConfigMap/Secret: 설정 관리
```

**2단계: 실습 (2주)**
```
- Minikube로 로컬 실습
- 간단한 앱 배포
- 스케일링, 업데이트 연습
- kubectl 명령어 익히기
```

**3단계: 심화 (4주)**
```
- StatefulSet, DaemonSet
- Ingress, PersistentVolume
- RBAC, Network Policies
- Helm 차트 작성
```

**학습 자료**:
```
공식 문서:
https://kubernetes.io/docs/tutorials/

실습 환경:
- Play with Kubernetes
- Katacoda
- Killercoda

인증:
- CKA (Certified Kubernetes Administrator)
- CKAD (Certified Kubernetes Application Developer)
```

**실전 팁**:
```
❌ 하지 말 것:
- 모든 개념을 한 번에 배우려고 함
- 실습 없이 이론만 공부
- 에러 무시하고 넘어감

✅ 해야 할 것:
- 매일 조금씩, 실습 위주
- 에러 메시지 읽고 이해하기
- kubectl explain으로 도움말 활용
- 커뮤니티 참여 (Stack Overflow, Slack)
```

</details>

<details>
<summary><strong>Q3: 소규모 프로젝트에도 Kubernetes가 필요한가요?</strong></summary>

**A**: **대부분의 소규모 프로젝트에는 과함**입니다. Docker Compose나 Swarm으로 충분합니다.

**상세 설명**:

**규모별 권장 사항**:

```
초소규모 (개인 프로젝트, MVP)
============================
서비스: 1-3개
트래픽: 일 100명 미만
팀: 1-2명

권장: Docker Compose
이유:
- 설정 간단 (docker-compose.yml 하나)
- 로컬 개발과 동일한 환경
- 학습 시간 1시간
- 비용: 최소 (서버 1대)

예시:
version: '3.8'
services:
  web:
    image: myapp:latest
    ports:
      - "80:80"
  db:
    image: postgres:16
```

```
소규모 (스타트업 초기)
=====================
서비스: 5-20개
트래픽: 일 1,000-10,000명
팀: 3-5명

권장: Docker Swarm
이유:
- 고가용성 확보
- 무중단 배포 가능
- 학습 시간 2-3일
- Compose에서 쉽게 전환
- 비용: 서버 3-5대

예시:
docker swarm init
docker stack deploy -c docker-stack.yml myapp
```

```
중규모 (성장 중인 스타트업)
==========================
서비스: 20-100개
트래픽: 일 10,000-100,000명
팀: 5-20명

권장: Kubernetes (관리형)
이유:
- 복잡한 워크플로우 지원
- 풍부한 모니터링/로깅
- 생태계 활용 (Helm, Istio)
- 학습 시간 2-4주
- 비용: AWS EKS, GKE 등 (월 $100-500)

예시:
# EKS 클러스터 생성
eksctl create cluster --name=mycluster
kubectl apply -f k8s/
```

```
대규모 (엔터프라이즈)
====================
서비스: 100개 이상
트래픽: 일 100,000명 이상
팀: 20명 이상

필수: Kubernetes
이유:
- 대규모 오케스트레이션 필수
- 멀티 클라우드 전략
- 엔터프라이즈 기능 (RBAC, etc)
- DevOps 팀 운영
- 비용: 월 수백만원

예시:
# 멀티 클러스터 관리
kubectx production
kubectl apply -f k8s/prod/
```

**의사 결정 플로우차트**:

```
Q1: 서비스가 5개 미만인가?
    ├─ Yes → Docker Compose 사용
    └─ No → Q2로

Q2: 고가용성이 필수인가?
    ├─ No → Docker Compose 사용
    └─ Yes → Q3로

Q3: 팀에 Kubernetes 경험자가 있는가?
    ├─ No → Docker Swarm 사용
    └─ Yes → Q4로

Q4: 서비스가 50개 이상인가?
    ├─ No → Docker Swarm 사용
    └─ Yes → Kubernetes 사용
```

**실제 사례**:

**사례 1: 과도한 Kubernetes 도입 (실패)**
```
스타트업 C사:
- 서비스: 3개 (웹, API, DB)
- 트래픽: 일 50명
- 팀: 개발자 2명

결정: Kubernetes 도입 (유행이라서)

결과:
- 학습에 2개월 소요
- 제품 출시 2개월 지연
- 복잡도 증가로 버그 증가
- 1년 후 Docker Compose로 회귀

교훈: 오버엔지니어링
```

**사례 2: 적절한 Swarm 사용 (성공)**
```
스타트업 D사:
- 서비스: 15개
- 트래픽: 일 5,000명
- 팀: 개발자 5명

결정: Docker Swarm

결과:
- 3일 만에 운영 시작
- 무중단 배포 구현
- 고가용성 확보
- 필요시 Kubernetes 전환 가능

교훈: 적절한 기술 선택
```

**결론**:
```
소규모 프로젝트에 Kubernetes는:
❌ 과도한 복잡성
❌ 긴 학습 시간
❌ 불필요한 비용

대신:
✅ Docker Compose (초소규모)
✅ Docker Swarm (소중규모)
✅ 성장하면서 Kubernetes로 전환 고려
```

</details>

<details>
<summary><strong>Q4: 관리형 Kubernetes(EKS, GKE)와 자체 구축 중 어떤 게 나을까요?</strong></summary>

**A**: **99% 경우에 관리형 Kubernetes가 낫습니다**. 직접 구축은 특수한 경우에만 고려하세요.

**상세 설명**:

**관리형 Kubernetes (Managed)**:
```
대표 서비스:
- AWS EKS (Elastic Kubernetes Service)
- Google GKE (Google Kubernetes Engine)
- Azure AKS (Azure Kubernetes Service)

장점:
✅ Control Plane 관리 불필요
✅ 자동 업그레이드 및 패치
✅ 고가용성 기본 제공
✅ 통합 모니터링/로깅
✅ 보안 업데이트 자동
✅ 백업/복구 용이
✅ 빠른 시작 (클릭 몇 번)

단점:
❌ 비용 (Control Plane 비용 추가)
❌ 클라우드 종속
❌ 일부 커스터마이징 제한

비용 예시 (AWS EKS):
- Control Plane: $73/월
- Worker Nodes: EC2 비용 (직접 구축과 동일)
- 총: $73 + Worker 비용
```

**자체 구축 (Self-hosted)**:
```
방법:
- kubeadm으로 직접 설치
- Rancher, OpenShift 등 사용

장점:
✅ 완전한 제어권
✅ 클라우드 비종속
✅ Control Plane 비용 절감
✅ 고급 커스터마이징 가능

단점:
❌ Control Plane 관리 필요
❌ 업그레이드 직접 수행
❌ 고가용성 직접 구성
❌ 보안 패치 수동 적용
❌ 전문 인력 필요
❌ 장애 시 자체 해결

운영 비용:
- Control Plane: 서버 3대 (HA)
- DevOps 엔지니어: 최소 1명 (월 급여 500만원+)
- 총: 서버 비용 + 인건비 (월 수백만원)
```

**비교표**:

| 항목 | 관리형 (EKS/GKE) | 자체 구축 |
|------|-----------------|----------|
| 초기 설정 | 10분 | 1-2일 |
| 운영 부담 | 낮음 | 높음 |
| 업그레이드 | 자동/클릭 | 수동 |
| 고가용성 | 기본 제공 | 직접 구성 |
| 모니터링 | 통합됨 | 직접 설치 |
| 비용 (소규모) | $200/월 | $100/월 (서버만) |
| 총 비용 (인건비 포함) | $200/월 | $500만원+/월 |
| 필요 인력 | 0-1명 | 1-2명 (전문가) |

**실제 사례**:

**사례 1: 관리형 성공**
```
스타트업 E사 (팀 10명):
- 처음부터 AWS EKS 사용
- DevOps 1명이 전체 인프라 관리
- 업그레이드, 패치 자동
- 장애 거의 없음
- 비용: 월 $500

장점:
- 빠른 시작 (1주일 내 운영)
- 제품 개발에 집중
- 안정적 운영
```

**사례 2: 자체 구축 실패**
```
중견기업 F사 (팀 50명):
- 비용 절감 목적으로 자체 구축
- kubeadm으로 클러스터 구성
- DevOps 2명 투입

문제:
- 3개월 만에 메이저 장애 2회
- 업그레이드 실패로 롤백
- 보안 패치 누락으로 해킹 시도
- DevOps 팀 스트레스 극심

결과:
- 1년 후 AWS EKS로 전환
- 안정성 대폭 향상
- DevOps 인력 1명으로 감축

교훈: 관리형이 결국 저렴
```

**자체 구축이 합리적인 경우**:

```
✅ 자체 구축 고려 상황:
1. 데이터 주권 (금융, 의료)
   - 클라우드 사용 불가능한 규제
   - 온프레미스 필수

2. 극도의 커스터마이징 필요
   - 특수한 네트워킹 요구사항
   - 커스텀 Control Plane 수정

3. 하이브리드 클라우드
   - 온프레미스 + 클라우드
   - Rancher, OpenShift 등 활용

4. 초대규모 (1000+ 노드)
   - 비용 구조가 역전됨
   - 전문 SRE 팀 존재

5. 이미 DevOps 팀 존재
   - Kubernetes 전문가 3명 이상
   - 24/7 운영 가능
```

**권장 사항**:

```
스타트업, 중소기업:
→ 100% 관리형 (EKS, GKE, AKS)
→ 이유: 빠르고, 안정적이고, 총 비용 저렴

대기업 (특수 요구사항 있음):
→ 하이브리드
→ 관리형 (프로덕션) + 자체 구축 (특수 워크로드)

금융/의료 (규제):
→ 자체 구축 (Rancher, OpenShift)
→ 단, 전문 SRE 팀 필수
```

**시작 가이드 (관리형)**:

```bash
# AWS EKS 클러스터 생성 (10분)
$ eksctl create cluster \
  --name=mycluster \
  --region=ap-northeast-2 \
  --nodegroup-name=standard-workers \
  --node-type=t3.medium \
  --nodes=3

# 배포
$ kubectl apply -f k8s/

# 완료! 운영 시작
```

**결론**:
```
관리형 Kubernetes를 사용하세요!

이유:
- 빠른 시작
- 낮은 운영 부담
- 높은 안정성
- 총 비용 저렴 (인건비 고려 시)

자체 구축은:
- 특수한 경우에만
- 전문 인력 있을 때만
```

</details>

<details>
<summary><strong>Q5: Kubernetes 인증(CKA, CKAD) 취득이 필요한가요?</strong></summary>

**A**: **취업/이직 목적이면 도움되지만, 실무 능력이 더 중요**합니다.

**상세 설명**:

**Kubernetes 인증 종류**:

```
1. CKA (Certified Kubernetes Administrator)
   - 대상: 클러스터 관리자
   - 난이도: ⭐⭐⭐⭐☆
   - 시험 시간: 2시간
   - 형식: 실기 (터미널 조작)
   - 비용: $395
   - 내용:
     - 클러스터 구축
     - 네트워킹 설정
     - 스토리지 관리
     - 트러블슈팅
     - 보안 (RBAC)

2. CKAD (Certified Kubernetes Application Developer)
   - 대상: 애플리케이션 개발자
   - 난이도: ⭐⭐⭐☆☆
   - 시험 시간: 2시간
   - 형식: 실기
   - 비용: $395
   - 내용:
     - Pod, Deployment 생성
     - ConfigMap, Secret
     - Service, Ingress
     - 모니터링, 로깅
     - 디버깅

3. CKS (Certified Kubernetes Security Specialist)
   - 대상: 보안 전문가
   - 난이도: ⭐⭐⭐⭐⭐
   - 전제조건: CKA 필수
   - 비용: $395
```

**필요성 판단**:

```
✅ 인증이 도움되는 경우:

1. 취업/이직
   - DevOps 엔지니어 지원 시
   - 클라우드 엔지니어 직무
   - 이력서에서 눈에 띔
   - 면접 통과율 20-30% 향상

2. 체계적 학습
   - 독학으로 어려움
   - 시험 준비하며 전체 개념 학습
   - 실습 위주 학습

3. 연봉 협상
   - 인증 보유자: 평균 10-15% 높음
   - 특히 외국계 기업

4. 프리랜서/컨설턴트
   - 신뢰도 향상
   - 프로젝트 수주 유리
```

```
❌ 인증이 불필요한 경우:

1. 이미 실무 경험 풍부
   - 3년 이상 Kubernetes 운영
   - 포트폴리오로 증명 가능

2. 개발자 (애플리케이션)
   - Kubernetes 사용자 수준
   - 클러스터 관리 안 함
   - kubectl 사용만 하면 충분

3. 소규모 팀
   - 관리형 Kubernetes 사용 (EKS, GKE)
   - 고급 기능 사용 안 함

4. 시간/비용 부담
   - 준비 시간: 2-3개월
   - 비용: $395 + 교육비
```

**인증 vs 실무 능력**:

```
채용 담당자 관점:

1순위: 실무 경험
- "EKS에서 100개 서비스 운영 경험"
- "Helm 차트 작성 및 배포 자동화"
- "Prometheus + Grafana 모니터링 구축"

2순위: 포트폴리오
- GitHub에 Kubernetes 프로젝트
- 블로그에 트러블슈팅 사례
- 오픈소스 기여

3순위: 인증
- CKA, CKAD 보유
- 기본기 검증됨

인증만 있고 실무 경험 없으면:
→ 면접 통과 어려움
```

**준비 방법**:

```bash
# 1. 공식 문서 학습 (2주)
https://kubernetes.io/docs/

# 2. 실습 환경 (매일 1-2시간)
- Minikube
- Play with Kubernetes
- Killercoda

# 3. 연습 문제 풀이 (4주)
- killer.sh (공식 시뮬레이터)
- CKA/CKAD 연습 문제

# 4. 시험 팁
- kubectl explain 활용
- kubectl 단축어 사용
- 시간 관리 (120분에 15-20문제)
- 구글링 가능 (공식 문서만)
```

**비용 대비 효과**:

```
비용:
- 시험: $395
- 준비 시간: 2-3개월 (시간당 2시간)
- 총 투자: $395 + 150시간

효과 (취업/이직 시):
- 연봉 협상: 평균 200-300만원 ↑
- 면접 통과율: 20-30% ↑
- ROI: 첫 해에 비용 회수

효과 (실무):
- 체계적 지식 습득
- 트러블슈팅 능력 향상
- 자신감 증가
```

**실전 조언**:

```
주니어 개발자:
→ CKAD 준비 (실무 중심)
→ 이직 시 유리

DevOps 엔지니어:
→ CKA 필수
→ CKS는 선택 (보안 특화 시)

백엔드 개발자:
→ 불필요 (kubectl 사용만 배우기)
→ 시간 투자 대비 효과 낮음

프리랜서:
→ CKA + CKAD 모두 유리
→ 프로젝트 수주에 도움
```

**결론**:

```
인증 취득 권장:
✅ DevOps 엔지니어 (필수)
✅ 클라우드 엔지니어 (권장)
✅ 취업/이직 준비 중 (도움됨)

인증 불필요:
❌ 백엔드/프론트 개발자 (선택)
❌ 이미 3년+ 경험자 (과시용)
❌ 소규모 프로젝트만 (과함)

핵심:
실무 능력 > 인증
하지만 인증이 기회의 문을 열어줄 수 있음
```

</details>

---

## 📝 면접 질문

### 주니어 레벨

**Q1: Kubernetes가 무엇이고 Docker Swarm과 어떻게 다른가요?**

**A**: Kubernetes는 **컨테이너 오케스트레이션 플랫폼으로, Docker Swarm보다 훨씬 강력하고 복잡한 기능을 제공**합니다.

**상세 답변**:

```
Kubernetes:
- Google에서 개발, CNCF 기부
- 컨테이너 오케스트레이션의 사실상 표준
- 매우 풍부한 기능과 거대한 생태계

Docker Swarm:
- Docker Inc.에서 개발
- Docker에 내장된 간단한 오케스트레이션
- 소규모 프로젝트에 적합
```

**주요 차이점**:

| 항목 | Docker Swarm | Kubernetes |
|------|-------------|------------|
| 학습 난이도 | 쉬움 (1-3일) | 어려움 (2-4주) |
| 설정 | 간단 | 복잡 |
| 확장성 | ~50 서비스 | 무제한 |
| 네트워킹 | 기본 | 고급 (Ingress, Network Policy) |
| 스토리지 | 제한적 | PersistentVolume, StorageClass |
| 오토스케일링 | 수동 | HPA, VPA, Cluster Autoscaler |
| 생태계 | 작음 | 거대함 (Helm, Operators, Istio) |
| 채용 시장 | 적음 | 많음 |
| 클라우드 지원 | 제한적 | AWS EKS, GKE, AKS |

**실무 예시**:
```bash
# Docker Swarm (간단)
$ docker swarm init
$ docker stack deploy -c docker-stack.yml myapp
# 끝!

# Kubernetes (상세)
$ kubectl apply -f namespace.yaml
$ kubectl apply -f configmap.yaml
$ kubectl apply -f secret.yaml
$ kubectl apply -f deployment.yaml
$ kubectl apply -f service.yaml
$ kubectl apply -f ingress.yaml
# 여러 리소스 관리 필요
```

**언제 무엇을 선택하나?**
```
Docker Swarm:
- 소규모 (서비스 50개 이하)
- 빠른 시작 필요
- 팀에 K8s 경험자 없음

Kubernetes:
- 중대규모 (서비스 100개 이상)
- 복잡한 워크플로우
- 장기적 확장성
- 멀티 클라우드
```

---

**Q2: Pod, ReplicaSet, Deployment의 차이를 설명하세요.**

**A**: **Pod는 컨테이너 실행 단위, ReplicaSet은 Pod 복제 관리, Deployment는 ReplicaSet + 롤링 업데이트**입니다.

**상세 답변**:

**1. Pod (가장 작은 단위)**:
```
Pod = 하나 이상의 컨테이너 그룹

특징:
- 동일한 IP 주소 공유
- 동일한 Volume 공유
- localhost로 통신
- 함께 스케줄링

예시:
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    ports:
    - containerPort: 80

사용 케이스:
- 직접 Pod 생성은 거의 안 함
- Deployment/ReplicaSet이 자동 생성
```

**2. ReplicaSet (복제 관리)**:
```
ReplicaSet = Pod의 복제본 관리

특징:
- 원하는 Pod 개수 유지
- Pod 죽으면 자동 재생성
- 스케일링 가능

예시:
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: nginx-rs
spec:
  replicas: 3  # 항상 3개 유지
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:alpine

동작:
┌─────┐ ┌─────┐ ┌─────┐
│ Pod │ │ Pod │ │ Pod │  ← 3개 유지
└─────┘ └─────┘ └─────┘

Pod 1개 죽음 ↓
┌─────┐ ┌─────┐   X
│ Pod │ │ Pod │

자동 재생성 ↓
┌─────┐ ┌─────┐ ┌─────┐
│ Pod │ │ Pod │ │ Pod │  ← 다시 3개

사용 케이스:
- 직접 ReplicaSet 생성도 거의 안 함
- Deployment가 자동 관리
```

**3. Deployment (배포 관리)**:
```
Deployment = ReplicaSet + 롤링 업데이트 + 롤백

특징:
- ReplicaSet을 자동 관리
- 무중단 롤링 업데이트
- 버전 히스토리 및 롤백
- 가장 많이 사용하는 리소스

예시:
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:alpine

계층 구조:
Deployment
    ↓ 관리
ReplicaSet (v1)
    ↓ 관리
Pod  Pod  Pod

업데이트 시:
Deployment
    ↓ 새로 생성
ReplicaSet (v2)  ← 새 버전
    ↓
Pod  Pod  Pod

    ↓ 유지 (롤백용)
ReplicaSet (v1)  ← 이전 버전 (Pod 0개)
```

**실무에서 사용**:
```bash
# 거의 항상 Deployment 사용
$ kubectl create deployment nginx --image=nginx:alpine --replicas=3

# 스케일링
$ kubectl scale deployment nginx --replicas=5

# 이미지 업데이트 (롤링 업데이트)
$ kubectl set image deployment/nginx nginx=nginx:1.21

# 롤백
$ kubectl rollout undo deployment/nginx

# Pod, ReplicaSet은 Deployment가 자동 관리
$ kubectl get all
NAME                         READY   STATUS    RESTARTS   AGE
pod/nginx-7c5ddbdf54-abc12   1/1     Running   0          1m
pod/nginx-7c5ddbdf54-def34   1/1     Running   0          1m
pod/nginx-7c5ddbdf54-ghi56   1/1     Running   0          1m

NAME                               DESIRED   CURRENT   READY   AGE
replicaset.apps/nginx-7c5ddbdf54   3         3         3       1m

NAME                    READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/nginx   3/3     3            3           1m
```

**비유**:
```
Pod = 계란후라이 (실제 음식)
ReplicaSet = "계란후라이 3개 만들기" 레시피
Deployment = 레시피북 + 버전 관리 + 교체 방법

실제로는:
→ Deployment만 만들면
→ ReplicaSet이 자동 생성되고
→ Pod가 자동 생성됨
```

**핵심 포인트**:
- 실무에서는 거의 항상 Deployment 사용
- Pod, ReplicaSet은 이해만 하면 됨
- Deployment가 모든 걸 자동 관리

---

### 중급 레벨

**Q3: Kubernetes Service의 3가지 타입 (ClusterIP, NodePort, LoadBalancer)의 차이와 사용 시나리오를 설명하세요.**

**A**: **ClusterIP는 내부 통신, NodePort는 노드 포트로 외부 접근, LoadBalancer는 클라우드 로드 밸런서 연동**입니다.

**상세 답변**:

**1. ClusterIP (기본, 내부 전용)**:
```
특징:
- 클러스터 내부에서만 접근 가능
- 고정된 가상 IP 할당
- 기본 타입

사용 시나리오:
- 마이크로서비스 간 통신
- DB, Redis 등 백엔드 서비스
- 외부 노출 불필요한 서비스

예시:
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  type: ClusterIP  # 기본값 (생략 가능)
  selector:
    app: backend
  ports:
  - port: 8080
    targetPort: 8080

동작:
┌─────────────────────────────────┐
│    Kubernetes Cluster           │
│                                 │
│  ┌──────────────────┐           │
│  │ frontend-pod     │           │
│  │                  │           │
│  │ curl backend:8080│           │
│  └──────────┬───────┘           │
│             ↓                   │
│  ┌──────────────────┐           │
│  │ backend-service  │           │
│  │ IP: 10.96.1.100  │ ← ClusterIP
│  │ (내부 고정 IP)   │           │
│  └──────────┬───────┘           │
│             ↓                   │
│    ┌────────┴────────┐          │
│    ↓         ↓       ↓          │
│  ┌────┐  ┌────┐  ┌────┐        │
│  │Pod │  │Pod │  │Pod │        │
│  └────┘  └────┘  └────┘        │
└─────────────────────────────────┘
       ↑
외부에서 접근 불가능
```

**2. NodePort (노드 포트 노출)**:
```
특징:
- 모든 노드의 특정 포트로 접근 가능
- 포트 범위: 30000-32767
- ClusterIP 기능도 포함

사용 시나리오:
- 개발/테스트 환경
- 간단한 외부 노출
- 로드 밸런서 없는 환경

예시:
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: NodePort
  selector:
    app: web
  ports:
  - port: 80          # ClusterIP 포트
    targetPort: 80    # Pod 포트
    nodePort: 30080   # 노드 포트 (생략 시 자동 할당)

동작:
외부
  │
  ↓
http://node1:30080  또는
http://node2:30080  또는
http://node3:30080
  │
  ↓
┌─────────────────────────────────┐
│ Kubernetes Cluster              │
│                                 │
│ ┌─────┐  ┌─────┐  ┌─────┐      │
│ │Node1│  │Node2│  │Node3│      │
│ │:30080  │:30080  │:30080      │
│ └──┬──┘  └──┬──┘  └──┬──┘      │
│    │        │        │          │
│    └────────┼────────┘          │
│             ↓                   │
│    ┌──────────────┐             │
│    │ web-service  │             │
│    │ (ClusterIP)  │             │
│    └──────┬───────┘             │
│           ↓                     │
│   ┌───────┴──────┐              │
│   ↓       ↓      ↓              │
│ ┌───┐  ┌───┐  ┌───┐            │
│ │Pod│  │Pod│  │Pod│            │
│ └───┘  └───┘  └───┘            │
└─────────────────────────────────┘

장점:
- 간단한 외부 접근
- 로드 밸런서 불필요

단점:
- 포트 범위 제한
- 노드 IP 변경 시 문제
- 프로덕션에는 부적합
```

**3. LoadBalancer (클라우드 LB)**:
```
특징:
- 클라우드 로드 밸런서 자동 생성
- 외부 고정 IP 할당
- NodePort + ClusterIP 기능 포함

사용 시나리오:
- 프로덕션 환경
- 클라우드 환경 (AWS, GCP, Azure)
- 공인 IP로 서비스 노출

예시:
apiVersion: v1
kind: Service
metadata:
  name: web-lb
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 80

동작:
외부
  │
  ↓
http://lb-external-ip.com  ← 고정 외부 IP
  │
  ↓
┌─────────────────────────────────┐
│ Cloud Load Balancer (AWS ELB)   │
└─────────────┬───────────────────┘
              ↓
┌─────────────────────────────────┐
│ Kubernetes Cluster              │
│                                 │
│ ┌─────┐  ┌─────┐  ┌─────┐      │
│ │Node1│  │Node2│  │Node3│      │
│ │:32000  │:32000  │:32000      │
│ └──┬──┘  └──┬──┘  └──┬──┘      │
│    │        │        │          │
│    └────────┼────────┘          │
│             ↓                   │
│    ┌──────────────┐             │
│    │  web-lb      │             │
│    │ (ClusterIP)  │             │
│    └──────┬───────┘             │
│           ↓                     │
│   ┌───────┴──────┐              │
│   ↓       ↓      ↓              │
│ ┌───┐  ┌───┐  ┌───┐            │
│ │Pod│  │Pod│  │Pod│            │
│ └───┘  └───┘  └───┘            │
└─────────────────────────────────┘

장점:
- 고정 외부 IP
- 자동 헬스체크
- 고가용성
- SSL 종료 가능

단점:
- 클라우드 환경 필수
- 비용 발생 (LB 비용)
- 로컬(Minikube)에서는 Pending 상태
```

**비교표**:

| 항목 | ClusterIP | NodePort | LoadBalancer |
|------|-----------|----------|--------------|
| 접근 범위 | 내부만 | 노드 IP + 포트 | 외부 IP |
| 외부 노출 | ❌ | ✅ | ✅ |
| 포트 범위 | 임의 | 30000-32767 | 임의 |
| 환경 | 모든 환경 | 모든 환경 | 클라우드만 |
| 비용 | 무료 | 무료 | LB 비용 |
| 프로덕션 | 내부용 | ❌ 부적합 | ✅ 권장 |

**실제 사용**:
```yaml
# 일반적인 구성
apiVersion: v1
kind: Service
metadata:
  name: backend
spec:
  type: ClusterIP  # 내부 서비스
  selector:
    app: backend
  ports:
  - port: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
spec:
  type: LoadBalancer  # 외부 노출
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 3000
```

**Minikube에서 LoadBalancer 사용**:
```bash
# Minikube는 LoadBalancer를 NodePort로 에뮬레이션
$ minikube tunnel  # 터널 열기

# 다른 터미널에서
$ kubectl get svc
NAME       TYPE           CLUSTER-IP      EXTERNAL-IP    PORT(S)
frontend   LoadBalancer   10.96.123.45    127.0.0.1      80:32000/TCP

# 접속
$ curl http://127.0.0.1
```

**핵심 포인트**:
- ClusterIP: 기본, 내부 통신
- NodePort: 간단한 외부 접근 (개발/테스트)
- LoadBalancer: 프로덕션 외부 노출 (클라우드)

---

**Q4: Kubernetes에서 ConfigMap과 Secret의 차이는 무엇이며, 어떻게 사용하나요?**

**A**: **ConfigMap은 일반 설정, Secret은 암호화된 민감 정보**입니다. 둘 다 환경 변수나 파일로 Pod에 주입합니다.

**상세 답변**:

**ConfigMap (일반 설정)**:
```
특징:
- 평문 저장 (암호화 안 됨)
- 설정 파일, 환경 변수 등
- 애플리케이션 설정 분리
- 재시작 없이 업데이트 가능

사용 시나리오:
- 애플리케이션 설정
- 로깅 레벨
- 기능 플래그
- 환경별 설정 (dev, prod)

생성 방법:
# 1. 명령어로
$ kubectl create configmap app-config \
  --from-literal=DB_HOST=postgres \
  --from-literal=DB_PORT=5432 \
  --from-literal=LOG_LEVEL=info

# 2. 파일에서
$ kubectl create configmap nginx-config \
  --from-file=nginx.conf

# 3. YAML로
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DB_HOST: postgres
  DB_PORT: "5432"
  LOG_LEVEL: info
  application.yml: |
    server:
      port: 8080
    logging:
      level: info
```

**Secret (민감 정보)**:
```
특징:
- base64 인코딩 (암호화 아님, 주의!)
- etcd에 암호화 저장 가능 (설정 필요)
- 비밀번호, API 키 등
- 접근 제어 가능 (RBAC)

사용 시나리오:
- 데이터베이스 비밀번호
- API 키
- JWT Secret
- TLS 인증서

생성 방법:
# 1. 명령어로
$ kubectl create secret generic db-secret \
  --from-literal=password='super_secret_password' \
  --from-literal=api-key='1234567890'

# 2. 파일에서
$ kubectl create secret generic tls-secret \
  --from-file=tls.crt \
  --from-file=tls.key

# 3. YAML로 (base64 인코딩 필요)
$ echo -n 'super_secret_password' | base64
c3VwZXJfc2VjcmV0X3Bhc3N3b3Jk

apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  password: c3VwZXJfc2VjcmV0X3Bhc3N3b3Jk  # base64
  api-key: MTIzNDU2Nzg5MA==              # base64
```

**Pod에서 사용**:

```yaml
# 환경 변수로 사용
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
    # ConfigMap에서 개별 값
    - name: DB_HOST
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: DB_HOST

    # Secret에서 개별 값
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password

    # ConfigMap 전체를 환경 변수로
    envFrom:
    - configMapRef:
        name: app-config

    # Secret 전체를 환경 변수로
    - secretRef:
        name: db-secret
```

```yaml
# 파일로 마운트
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  containers:
  - name: app
    image: myapp:latest
    volumeMounts:
    # ConfigMap을 파일로
    - name: config-volume
      mountPath: /etc/config

    # Secret을 파일로
    - name: secret-volume
      mountPath: /etc/secrets
      readOnly: true

  volumes:
  - name: config-volume
    configMap:
      name: app-config

  - name: secret-volume
    secret:
      secretName: db-secret

# 결과:
# /etc/config/DB_HOST → "postgres"
# /etc/config/DB_PORT → "5432"
# /etc/secrets/password → "super_secret_password"
# /etc/secrets/api-key → "1234567890"
```

**비교표**:

| 항목 | ConfigMap | Secret |
|------|-----------|--------|
| 암호화 | ❌ 평문 | ⚠️ base64 (진짜 암호화 아님) |
| 용도 | 일반 설정 | 민감 정보 |
| 크기 제한 | 1MB | 1MB |
| 접근 제어 | RBAC | RBAC (더 엄격) |
| 환경 변수 | ✅ | ✅ |
| 파일 마운트 | ✅ | ✅ (readOnly 권장) |
| 업데이트 | 자동 반영 | 자동 반영 |

**보안 베스트 프랙티스**:

```yaml
# ❌ 나쁜 예: Secret을 환경 변수로 노출
env:
- name: DB_PASSWORD
  value: "mysecret"  # 로그에 노출 위험!

# ✅ 좋은 예: Secret을 파일로 마운트
volumeMounts:
- name: db-secret
  mountPath: /run/secrets
  readOnly: true

volumes:
- name: db-secret
  secret:
    secretName: db-secret

# 애플리케이션 코드:
val password = File("/run/secrets/password").readText()
```

**실무 패턴**:

```yaml
# 환경별 ConfigMap
---
# dev-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: dev
data:
  ENV: "development"
  DB_HOST: "postgres-dev"
  LOG_LEVEL: "debug"
---
# prod-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: prod
data:
  ENV: "production"
  DB_HOST: "postgres-prod.example.com"
  LOG_LEVEL: "warn"
```

**Secret 확인**:
```bash
# Secret 목록
$ kubectl get secrets

# Secret 상세 (값 숨겨짐)
$ kubectl describe secret db-secret

# Secret 값 보기 (디코딩)
$ kubectl get secret db-secret -o jsonpath='{.data.password}' | base64 -d
super_secret_password
```

**업데이트 시 Pod 재시작**:
```bash
# ConfigMap/Secret 업데이트
$ kubectl edit configmap app-config

# Pod 재시작 (변경사항 반영)
$ kubectl rollout restart deployment myapp

# 또는 자동 재시작 설정
# Reloader: https://github.com/stakater/Reloader
```

**핵심 포인트**:
- ConfigMap = 일반 설정 (평문)
- Secret = 민감 정보 (base64, 암호화 가능)
- 환경 변수보다 파일 마운트가 더 안전
- Secret은 RBAC로 접근 제어

---

**Q5: Kubernetes에서 HorizontalPodAutoscaler(HPA)가 무엇이며 어떻게 동작하나요?**

**A**: HPA는 **CPU/메모리 사용률에 따라 Pod 수를 자동으로 조절**하는 기능입니다.

**상세 답변**:

**HPA 개념**:
```
HorizontalPodAutoscaler:
- 워크로드에 따라 Pod 수를 자동 증감
- CPU, 메모리, 커스텀 메트릭 기반
- 트래픽 변동에 자동 대응
- 비용 최적화

동작 원리:
1. Metrics Server가 리소스 사용률 수집
2. HPA가 주기적으로 메트릭 확인 (기본 15초)
3. 목표 사용률과 비교
4. 필요시 Pod 수 조절
```

**HPA 생성**:

```yaml
# deployment.yaml (먼저 Deployment 필요)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 2  # 초기값 (HPA가 조절함)
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m     # HPA 계산에 사용
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
---
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  minReplicas: 2    # 최소 Pod 수
  maxReplicas: 10   # 최대 Pod 수
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50  # 목표 CPU 50%
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 70  # 목표 메모리 70%
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # 5분 안정화
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60  # 1분마다 최대 50%씩 축소
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60  # 1분마다 최대 100%씩 확장
```

**명령어로 생성**:
```bash
# kubectl autoscale 명령어
$ kubectl autoscale deployment web \
  --cpu-percent=50 \
  --min=2 \
  --max=10

# 확인
$ kubectl get hpa

# 출력:
NAME      REFERENCE        TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
web-hpa   Deployment/web   20%/50%   2         10        2          1m
         ↑ 현재/목표
```

**동작 시나리오**:

```
초기 상태 (CPU 20%):
┌─────┐ ┌─────┐
│ Pod │ │ Pod │  ← 2개 (minReplicas)
└─────┘ └─────┘
CPU: 20% (목표: 50%)

트래픽 증가 (CPU 80%):
┌─────┐ ┌─────┐
│ Pod │ │ Pod │
└─────┘ └─────┘
CPU: 80% (목표: 50% 초과!)

HPA 계산:
원하는 Pod 수 = 현재 Pod 수 × (현재 사용률 / 목표 사용률)
             = 2 × (80% / 50%)
             = 3.2 → 4개 (올림)

스케일 아웃:
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│ Pod │ │ Pod │ │ Pod │ │ Pod │  ← 4개로 증가
└─────┘ └─────┘ └─────┘ └─────┘
CPU: 40% (목표: 50% 근접)

트래픽 감소 (CPU 20%):
CPU: 20% (목표: 50% 미달)

HPA 계산:
원하는 Pod 수 = 4 × (20% / 50%)
             = 1.6 → 2개 (minReplicas)

스케일 인:
┌─────┐ ┌─────┐
│ Pod │ │ Pod │  ← 2개로 감소
└─────┘ └─────┘
CPU: 40%
```

**Metrics Server 설치** (필수):
```bash
# Minikube
$ minikube addons enable metrics-server

# 일반 클러스터
$ kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# 확인
$ kubectl top nodes
$ kubectl top pods
```

**HPA 상태 확인**:
```bash
# HPA 상태
$ kubectl get hpa web-hpa

# 출력:
NAME      REFERENCE        TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
web-hpa   Deployment/web   35%/50%, 45%/70%  2       10        3          10m
                          ↑ CPU  ↑ Memory

# 상세 정보
$ kubectl describe hpa web-hpa

# 이벤트 확인
Events:
  Type    Reason             Message
  ----    ------             -------
  Normal  SuccessfulRescale  New size: 4; reason: cpu resource utilization above target
  Normal  SuccessfulRescale  New size: 2; reason: All metrics below target
```

**부하 테스트**:
```bash
# 부하 생성 (무한 요청)
$ kubectl run -it --rm load-generator \
  --image=busybox \
  --restart=Never \
  -- /bin/sh -c "while true; do wget -q -O- http://web; done"

# 다른 터미널에서 HPA 모니터링
$ watch -n 1 kubectl get hpa

# 출력 (시간 경과):
NAME      TARGETS   REPLICAS
web-hpa   20%/50%   2          # 정상
web-hpa   60%/50%   2          # 목표 초과
web-hpa   55%/50%   4          # 스케일 아웃
web-hpa   45%/50%   4          # 안정화
web-hpa   25%/50%   4          # 대기 (안정화 윈도우)
web-hpa   25%/50%   2          # 스케일 인
```

**커스텀 메트릭 (고급)**:
```yaml
# Prometheus 메트릭 기반
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-hpa-custom
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"  # 초당 1000 요청

# Prometheus Adapter 설치 필요
```

**Best Practices**:
```yaml
1. requests 설정 필수:
   resources:
     requests:
       cpu: 100m  # HPA가 이 값 기준으로 계산
       memory: 128Mi

2. 안정화 윈도우 설정:
   behavior:
     scaleDown:
       stabilizationWindowSeconds: 300  # 5분
   # 급격한 스케일 인/아웃 방지

3. 최소/최대값 적절히:
   minReplicas: 2  # 항상 HA
   maxReplicas: 20  # 비용 제한

4. 여러 메트릭 조합:
   metrics:
   - type: Resource
     resource:
       name: cpu
       target:
         averageUtilization: 50
   - type: Resource
     resource:
       name: memory
       target:
         averageUtilization: 70
   # 둘 중 높은 값 기준으로 스케일
```

**핵심 포인트**:
- HPA = 자동 스케일링 (수평 확장)
- CPU/메모리 사용률 기반
- requests 설정 필수
- Metrics Server 필요
- 트래픽 변동 자동 대응

---

## 다음 단계

축하합니다! Kubernetes의 기본을 완벽하게 마스터했습니다.

### 이번 섹션에서 배운 것

✅ Kubernetes의 필요성
✅ Docker Swarm vs Kubernetes 비교
✅ Kubernetes 아키텍처 (Control Plane, Worker Node)
✅ 핵심 개념 (Pod, ReplicaSet, Deployment, Service)
✅ Minikube 설치 및 시작
✅ kubectl 기본 명령어
✅ YAML로 리소스 정의
✅ ConfigMap과 Secret 관리
✅ LK-Trade Kubernetes 배포

### 다음에 배울 것

**섹션 34: 고급 주제와 모범 사례**에서는:
- Ingress (외부 트래픽 라우팅)
- HorizontalPodAutoscaler (자동 스케일링)
- Helm (패키지 관리자)
- 프로덕션 체크리스트
- 성능 최적화

### 추가 학습 자료

**공식 문서:**
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Kubernetes Tutorials](https://kubernetes.io/docs/tutorials/)

**연습 환경:**
- [Play with Kubernetes](https://labs.play-with-k8s.com/)
- [Katacoda](https://www.katacoda.com/courses/kubernetes)

**도구:**
- [k9s](https://k9scli.io/) - Kubernetes CLI UI
- [Lens](https://k8slens.dev/) - Kubernetes IDE

---

**다음 섹션에서 만나요!**
