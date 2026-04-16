# K8s 학습 템플릿

> 유형: **개념 + YAML/kubectl 실습**
> 적용: 학습_11_K8s.md의 Step 1~16

## 공통 원칙

| 원칙 | 설명 |
|------|------|
| **왜 먼저** | "Docker Compose만으로 운영하면 이런 한계. K8s가 이렇게 해결" |
| **비유 먼저** | K8s 리소스/개념을 일상 비유로 직관 잡기 |
| **트레이드오프** | 모든 설정/전략에 트레이드오프 명시 |
| **버전 차이** | K8s API 버전 변경, deprecated API 언급 |

### 비유 예시
```
K8s = "호텔 매니저. 방(Pod)을 배정하고, 손님(요청)을 안내하고, 문제 있는 방은 교체"
Pod = "호텔 방. 침대(컨테이너) 1~2개. 방이 고장 나면 새 방으로 안내(재생성)"
Deployment = "예약 시스템. '항상 방 3개를 유지'를 보장. 1개 고장나면 자동으로 새 방 준비"
Service = "호텔 프론트 데스크. 방 번호(Pod IP)가 바뀌어도 프론트(Service IP)는 동일"
Ingress = "호텔 입구 간판. 'A동(api.example.com)은 왼쪽, B동(web.example.com)은 오른쪽'"
ConfigMap = "호텔 비품 목록(수건 수, 어메니티 종류). 방마다 다르게 설정 가능"
Secret = "금고. 비밀번호/카드키를 안전하게 보관"
HPA = "성수기 대응. 손님이 많아지면 방을 자동 추가, 줄어들면 축소"
Helm = "인테리어 패키지. '비즈니스 룸 세트'를 주문하면 가구/조명/비품이 한 번에"
```

### 트레이드오프 예시
```
K8s 도입: 자동화/확장↑ ↔ 학습 곡선↑ 인프라 복잡↑ 운영 비용↑
Readiness Probe 민감: 불안정 Pod 차단↑ ↔ 정상 Pod도 잠시 제외 가능
HPA: 자동 확장 ↔ 비용 변동, 스케일 인/아웃 지연
Helm: 원클릭 배포 ↔ 템플릿 복잡도↑ (단순하면 Kustomize가 나을 수도)
NodePort: 외부 접근 간편 ↔ 포트 제한(30000~32767), 보안 약함
LoadBalancer: 편리 ↔ 서비스마다 LB 1개 → 비용↑
```

## 설명 흐름
1. **왜 써야 하는가**: "Docker Compose로는 이 문제를 못 풂"
2. **비유로 직관 잡기**
3. **핵심 개념 + 아키텍처 다이어그램** (텍스트)
4. **YAML 전체 예시** + kubectl 명령어
5. **"이러면 어떻게 되는가" 시나리오** + 트레이드오프
6. **오해하기 쉬운 부분 + 버전 차이**:
```
"K8s = Docker" → K8s는 오케스트레이션. Docker는 컨테이너 런타임. K8s는 containerd/CRI-O도 사용
"Pod를 직접 만들면 된다" → Pod는 일회성. Deployment로 관리해야 자가 치유(Self-healing)
"Readiness Probe 없어도 된다" → 없으면 기동 중인 Pod에 트래픽 → 에러 폭발
"Secret은 안전하다" → Base64 인코딩이지 암호화 아님. etcd 암호화 또는 외부 시크릿 도구 필요
"HPA만 설정하면 무한 확장" → Node 리소스 한계. Cluster Autoscaler도 필요할 수 있음
K8s 버전 주의: apps/v1beta → apps/v1 변경, PodSecurityPolicy → Pod Security Admission
```
7. **확인 질문**: 사용자 답변 → 피드백
```
Step 2: "Control Plane의 핵심 컴포넌트 4개와 역할은?"
Step 5: "Deployment가 ReplicaSet을 통해 Pod를 관리하는 이유는?"
Step 6: "ClusterIP vs NodePort vs LoadBalancer 차이는?"
Step 8: "ConfigMap 변경 시 Pod에 자동 반영되는가?"
Step 12: "Liveness vs Readiness Probe를 잘못 설정하면 어떤 문제?"
Step 16: "Pod가 CrashLoopBackOff면 어떤 순서로 진단하는가?"
```
8. **정리 + 다음 안내**

## Step별 특이사항
- 기초 Step(1~3): 아키텍처 그림 + 환경 구축 + Skaffold/Telepresence
- 리소스 Step(4~9): YAML 전체 예시 + kubectl. Graceful Shutdown(Step 5)
- Probe Step(12): 잘못된 설정의 위험 시나리오
- Helm Step(14): Helm vs Kustomize 트레이드오프
- 배포 Step(15): Rolling/Blue-Green/Canary 비교 + 트레이드오프
- 트러블슈팅 Step(16): "Pod가 안 뜬다" 진단 순서
