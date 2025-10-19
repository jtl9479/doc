# 섹션 33: Kubernetes 소개

## 비유로 시작하기

Kubernetes는 **대형 항구의 컨테이너 관리 시스템**과 같습니다.

```
항구 컨테이너 터미널                 Kubernetes
===================                 ===========
🚢 화물선                       →    Node (서버)
📦 컨테이너                     →    Pod (컨테이너 그룹)
🏗️ 크레인                      →    Scheduler (배치)
🎯 컨테이너 배치 계획           →    Deployment
👔 항만 관리자                  →    Control Plane
📊 실시간 모니터링 시스템       →    kube-apiserver
🔧 자동 수리 시스템             →    Self-healing
⚖️ 부하 분산 시스템            →    Service (Load Balancer)
```

항구 없이 수천 개의 컨테이너를 관리할 수 없듯이, Kubernetes 없이 수천 개의 Docker 컨테이너를 관리하기 어렵습니다.

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

## 다음 단계

축하합니다! 🎉 Kubernetes의 기본을 완벽하게 마스터했습니다.

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

**다음 섹션에서 만나요!** 🚀