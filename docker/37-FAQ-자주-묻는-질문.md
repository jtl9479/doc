# 섹션 37: FAQ - 자주 묻는 질문

## 기본 개념

### Q1: Docker와 가상 머신(VM)의 차이는 무엇인가요?

**A:**

```
가상 머신 (VM)                    Docker 컨테이너
==============                    ===============
호스트 OS                         호스트 OS
   ↓                                 ↓
하이퍼바이저                      Docker Engine
   ↓                                 ↓
┌─────────┬─────────┐            ┌────┬────┬────┐
│ Guest OS│ Guest OS│            │App1│App2│App3│
│   App   │   App   │            └────┴────┴────┘
└─────────┴─────────┘

- 크기: GB 단위              - 크기: MB 단위
- 시작: 분 단위              - 시작: 초 단위
- 격리: 완전 격리            - 격리: 프로세스 레벨
- 오버헤드: 높음             - 오버헤드: 낮음
```

### Q2: Docker 이미지와 컨테이너의 차이는?

**A:**
- **이미지**: 읽기 전용 템플릿 (클래스)
- **컨테이너**: 실행 중인 인스턴스 (객체)

```bash
# 이미지 = 설계도
docker images

# 컨테이너 = 설계도로 만든 집
docker run nginx  # 이미지로 컨테이너 생성
docker ps         # 실행 중인 컨테이너
```

### Q3: Docker Hub vs Docker Registry?

**A:**
- **Docker Hub**: Docker 공식 공개 레지스트리
- **Docker Registry**: 프라이빗 이미지 저장소

```bash
# Docker Hub (공개)
docker pull nginx

# 프라이빗 Registry
docker pull myregistry.com/myapp:latest
```

---

## 설치 및 설정

### Q4: Windows에서 Docker 설치 시 WSL2가 필요한가요?

**A:** 네, Docker Desktop for Windows는 WSL2 백엔드를 권장합니다.

```bash
# WSL2 설치
wsl --install

# Ubuntu 설치
wsl --install -d Ubuntu

# Docker Desktop 설치 후 설정 확인
Settings > General > Use the WSL2 based engine
```

### Q5: Docker가 제대로 설치되었는지 확인하는 방법?

**A:**
```bash
# 버전 확인
docker --version

# Hello World 실행
docker run hello-world

# Docker 정보
docker info
```

---

## 이미지 관리

### Q6: 이미지 크기를 줄이려면?

**A:**
1. **Alpine 베이스 이미지 사용**
```dockerfile
# 800MB
FROM ubuntu:22.04

# 5MB
FROM alpine:3.18
```

2. **멀티 스테이지 빌드**
```dockerfile
FROM gradle:8.5 AS builder
WORKDIR /app
COPY . .
RUN gradle build

FROM openjdk:17-jre-alpine
COPY --from=builder /app/build/libs/*.jar app.jar
CMD ["java", "-jar", "app.jar"]
```

3. **불필요한 파일 제외** (.dockerignore)

### Q7: 이미지 레이어는 무엇인가요?

**A:** Dockerfile의 각 명령어가 레이어를 생성합니다.

```dockerfile
FROM ubuntu:22.04        # Layer 1
RUN apt-get update       # Layer 2
RUN apt-get install -y curl  # Layer 3
COPY app.jar /app/       # Layer 4

# 레이어는 캐시됨
# COPY만 변경하면 Layer 1-3은 캐시 사용
```

### Q8: latest 태그 사용이 왜 나쁜가요?

**A:** `latest`는 재현성을 해칩니다.

```bash
# ❌ 나쁜 예
FROM node:latest
# 내일 다시 빌드하면 다른 버전일 수 있음

# ✅ 좋은 예
FROM node:18.17.0
# 항상 동일한 버전
```

---

## 컨테이너 실행

### Q9: `-d`와 `-it` 플래그 차이는?

**A:**
```bash
# -d: 백그라운드 실행
docker run -d nginx
# 컨테이너 ID 반환 후 터미널 복귀

# -it: 대화형 모드
docker run -it ubuntu /bin/bash
# 컨테이너 내부 쉘 실행

# 둘 다 사용 불가 (모순)
```

### Q10: 컨테이너가 바로 종료되는 이유는?

**A:** 컨테이너는 메인 프로세스가 종료되면 같이 종료됩니다.

```bash
# ❌ 바로 종료
docker run ubuntu
# /bin/bash가 실행되고 즉시 종료

# ✅ 계속 실행
docker run -d nginx
# nginx 프로세스가 계속 실행됨

# ✅ 대화형으로 유지
docker run -it ubuntu /bin/bash
```

### Q11: 실행 중인 컨테이너에 어떻게 접속하나요?

**A:**
```bash
# 방법 1: exec 사용 (권장)
docker exec -it <container> /bin/bash

# 방법 2: attach (주의: Ctrl+C 하면 컨테이너 종료)
docker attach <container>

# 방법 3: logs로 확인만
docker logs -f <container>
```

---

## 네트워킹

### Q12: 컨테이너 간 통신은 어떻게 하나요?

**A:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx
    networks:
      - mynetwork

  db:
    image: postgres
    networks:
      - mynetwork

networks:
  mynetwork:
    driver: bridge

# web 컨테이너에서 db 접속
# http://db:5432 (서비스 이름으로 접근)
```

### Q13: localhost로 접근이 안 됩니다

**A:** 포트 매핑을 확인하세요.

```bash
# ❌ 포트 매핑 없음
docker run nginx
# 호스트에서 접근 불가

# ✅ 포트 매핑
docker run -p 8080:80 nginx
# http://localhost:8080 접근 가능
```

### Q14: 컨테이너가 외부 네트워크에 접근할 수 없습니다

**A:**
```bash
# DNS 문제 확인
docker run --rm busybox nslookup google.com

# Docker 네트워크 재시작
sudo systemctl restart docker

# DNS 서버 설정
# /etc/docker/daemon.json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

---

## 볼륨 및 스토리지

### Q15: 볼륨과 바인드 마운트의 차이는?

**A:**
```bash
# 볼륨 (Docker 관리)
docker run -v myvolume:/data nginx
# Docker가 관리하는 위치에 저장

# 바인드 마운트 (호스트 경로)
docker run -v $(pwd)/data:/data nginx
# 호스트의 특정 경로와 연결
```

### Q16: 컨테이너 삭제 시 데이터가 사라집니다

**A:** 볼륨을 사용하세요.

```yaml
version: '3.8'

services:
  db:
    image: postgres
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
    # 컨테이너 삭제해도 데이터 유지
```

### Q17: 볼륨 권한 문제 (Permission denied)

**A:**
```dockerfile
# Dockerfile에서 권한 설정
FROM nginx:alpine

# 디렉토리 생성 및 권한 설정
RUN mkdir -p /data && chown -R nginx:nginx /data

USER nginx
```

---

## Docker Compose

### Q18: docker-compose up vs docker-compose start 차이는?

**A:**
```bash
# up: 컨테이너 생성 + 시작
docker-compose up

# start: 이미 존재하는 컨테이너만 시작
docker-compose start

# 일반적인 워크플로우
docker-compose up -d      # 처음 시작
docker-compose stop       # 중지
docker-compose start      # 다시 시작
docker-compose down       # 완전히 삭제
```

### Q19: 특정 서비스만 재시작하려면?

**A:**
```bash
# 특정 서비스만
docker-compose restart web

# 여러 서비스
docker-compose restart web db

# 재빌드 후 재시작
docker-compose up -d --build web
```

### Q20: 환경 변수를 어떻게 전달하나요?

**A:**
```yaml
# docker-compose.yml
services:
  web:
    # 방법 1: 직접 설정
    environment:
      - NODE_ENV=production

    # 방법 2: .env 파일 사용
    env_file:
      - .env

    # 방법 3: 호스트 환경 변수
    environment:
      - API_KEY=${API_KEY}
```

---

## 성능 및 리소스

### Q21: Docker가 느립니다 (특히 Windows/Mac)

**A:**
```bash
# Windows: WSL2 사용 확인
Settings > General > Use WSL2

# Mac: 메모리 증가
Settings > Resources > Memory: 4GB → 8GB

# 볼륨 대신 named volume 사용
# ❌ 느림
volumes:
  - ./code:/app

# ✅ 빠름
volumes:
  - code:/app
```

### Q22: 컨테이너가 호스트 리소스를 모두 사용합니다

**A:**
```yaml
# 리소스 제한 설정
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Q23: 디스크 공간이 부족합니다

**A:**
```bash
# 디스크 사용량 확인
docker system df

# 정리
docker system prune -a --volumes

# 주의: 모든 데이터 삭제됨
# 백업 후 실행!
```

---

## 보안

### Q24: Docker는 안전한가요?

**A:** 올바르게 사용하면 안전합니다.

```yaml
# 보안 체크리스트
services:
  app:
    # ✅ non-root 사용자
    user: "1000:1000"

    # ✅ 읽기 전용 파일 시스템
    read_only: true

    # ✅ 권한 제한
    cap_drop:
      - ALL

    # ✅ Secret 사용
    secrets:
      - db_password
```

### Q25: 이미지에 취약점이 있는지 확인하려면?

**A:**
```bash
# Trivy 사용
trivy image nginx:latest

# Docker Scout 사용
docker scout cves nginx:latest

# 결과 확인 및 업데이트
docker pull nginx:alpine  # 더 작고 안전한 버전
```

---

## 트러블슈팅

### Q26: "Cannot connect to the Docker daemon" 에러

**A:**
```bash
# Docker 서비스 시작
sudo systemctl start docker

# Docker 데몬 상태 확인
sudo systemctl status docker

# 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER
# 로그아웃 후 재로그인 필요
```

### Q27: "port is already allocated" 에러

**A:**
```bash
# 포트 사용 중인 프로세스 확인
sudo lsof -i :8080
sudo netstat -tulpn | grep 8080

# 프로세스 종료
sudo kill <PID>

# 또는 다른 포트 사용
docker run -p 8081:80 nginx
```

### Q28: 컨테이너 로그가 너무 큽니다

**A:**
```yaml
# docker-compose.yml
services:
  web:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 프로덕션

### Q29: 프로덕션에서 Docker Compose를 사용해도 되나요?

**A:** 소규모는 가능하지만, 중대규모는 오케스트레이터를 권장합니다.

```
소규모 (1-5 서버)
→ Docker Compose ✅

중규모 (5-20 서버)
→ Docker Swarm ✅

대규모 (20+ 서버)
→ Kubernetes ✅
```

### Q30: 무중단 배포는 어떻게 하나요?

**A:**
```yaml
# Docker Swarm
services:
  web:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback

# Kubernetes
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
```

---

## 개발 워크플로우

### Q31: 코드 변경 시마다 이미지를 다시 빌드해야 하나요?

**A:** 개발 환경에서는 볼륨 마운트를 사용하세요.

```yaml
# docker-compose.dev.yml
services:
  app:
    build: .
    volumes:
      - ./src:/app/src  # 소스 코드 마운트
    command: npm run dev  # Hot reload
```

### Q32: 프론트엔드 개발에 Docker를 사용해야 하나요?

**A:** 팀 환경에서는 권장합니다.

```dockerfile
# Dockerfile.dev
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
```

---

## 마이그레이션

### Q33: 기존 VM 애플리케이션을 Docker로 마이그레이션하려면?

**A:** 단계적으로 진행하세요.

```
1단계: 분석
- 의존성 파악
- 상태 저장 확인

2단계: Dockerfile 작성
- 베이스 이미지 선택
- 의존성 설치
- 애플리케이션 복사

3단계: 테스트
- 로컬에서 테스트
- 통합 테스트

4단계: 배포
- 스테이징 환경
- 프로덕션 환경
```

### Q34: 데이터베이스도 컨테이너로 실행해야 하나요?

**A:** 환경에 따라 다릅니다.

```
개발 환경: ✅ 컨테이너 사용
- 빠른 설정
- 일관된 환경

프로덕션: ⚠️ 신중히 고려
- 장점: 일관성, 이동성
- 단점: 복잡성, 성능

권장: Managed 서비스 (RDS, Cloud SQL) 또는
      전용 DB 서버 사용
```

---

## 추가 질문이 있으신가요?

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Community Forums](https://forums.docker.com/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/docker)
- [Docker Discord](https://discord.gg/docker)

**질문을 주저하지 마세요!** 🙋‍♂️