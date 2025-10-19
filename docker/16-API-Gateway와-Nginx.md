# 섹션 16: API Gateway 및 Nginx 설정

> **학습 목표**: API Gateway의 필요성을 이해하고, Nginx를 활용한 리버스 프록시, 로드 밸런싱, SSL/TLS 설정, Rate Limiting을 마스터합니다.

**⏱️ 예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐⭐☆ (4개/5개)

---

## 📚 목차
- [API Gateway 필요성](#161-api-gateway-필요성)
- [실생활 비유로 이해하기](#실생활-비유로-이해하기)
- [Nginx 리버스 프록시 설정](#162-nginx-리버스-프록시-설정)
- [로드 밸런싱](#163-로드-밸런싱)
- [SSL/TLS 설정](#164-ssltls-설정)
- [속도 제한 (Rate Limiting)](#165-속도-제한-rate-limiting)
- [캐싱](#166-캐싱)
- [모니터링 및 로깅](#167-모니터링-및-로깅)
- [완전한 설정 예제](#168-완전한-설정-예제)
- [테스트 및 검증](#169-테스트-및-검증)
- [수치로 보는 효과](#📊-수치로-보는-효과)
- [주니어 시나리오](#👨‍💻-주니어-시나리오)
- [FAQ](#❓-faq)
- [면접 질문 리스트](#💼-면접-질문-리스트)
- [핵심 정리](#📝-핵심-정리)
- [다음 단계](#1611-다음-단계)

---

## 🌟 실생활 비유로 이해하기

### 비유 1: 대형 쇼핑몰의 중앙 접수처

```
API Gateway = 쇼핑몰 중앙 안내 데스크

[고객] → [중앙 안내 데스크] → [각 매장]
         (API Gateway)      (마이크로서비스)

┌──────────────────────────────────────┐
│        고객 (클라이언트)              │
└───────────┬──────────────────────────┘
            ↓
┌───────────────────────────────────────┐
│   중앙 안내 데스크 (API Gateway)       │
│   - 방문자 확인 (인증)                │
│   - 안내 (라우팅)                     │
│   - 혼잡도 관리 (Rate Limiting)       │
└───┬───┬───┬───┬──────────────────────┘
    ↓   ↓   ↓   ↓
   의류 식품 전자 서점 (각 마이크로서비스)
```

**비유 설명**:
- 고객이 쇼핑몰에 가면 중앙 안내 데스크에서 원하는 매장을 안내받음
- 중앙 데스크는 회원 확인, 포인트 적립, 안내 서비스 제공
- 각 매장(서비스)은 고객이 직접 찾아갈 필요 없음

### 비유 2: 아파트 경비실

```
API Gateway = 아파트 경비실

[방문객] → [경비실] → [각 동/호수]
         (Gateway)   (서비스)

경비실의 역할:
✅ 신분 확인 (인증/인가)
✅ 방문 기록 (로깅)
✅ 차량 통제 (Rate Limiting)
✅ 안내 서비스 (라우팅)
✅ 보안 (SSL/TLS)
```

### 비유 3: 공항 체크인 카운터

```
[승객] → [체크인 카운터] → [각 게이트]
       (API Gateway)      (서비스)

체크인 카운터의 역할:
- 신분 확인 (인증)
- 탑승권 발급 (토큰)
- 짐 무게 제한 (Request Size Limit)
- 게이트 안내 (라우팅)
- 승객 분산 (로드 밸런싱)
```

### 비유 4: 배달앱의 중앙 서버

```
[고객 앱] → [배달앱 서버] → [식당/라이더/결제]
          (API Gateway)     (마이크로서비스)

배달앱 서버의 역할:
- 로그인 확인 (인증)
- 주문 라우팅 (식당 → 라이더 → 결제)
- 부하 분산 (여러 서버)
- 보안 통신 (HTTPS)
- 요청 제한 (스팸 방지)
```

### 비유 5: 콜센터 ARS 시스템

```
[고객 전화] → [ARS 시스템] → [각 담당 부서]
            (API Gateway)   (서비스)

ARS의 역할:
1번: 고객 확인 (인증)
2번: 상담원 연결 (라우팅)
3번: 대기열 관리 (Rate Limiting)
4번: 통화 녹음 (로깅)
```

### 🎯 종합 비교표

```
┌──────────────┬─────────────┬──────────────┬─────────────┐
│ 기술         │ 실생활 비유  │ 핵심 기능     │ 효과        │
├──────────────┼─────────────┼──────────────┼─────────────┤
│ API Gateway  │ 경비실      │ 신분 확인     │ 보안 강화    │
│ 로드 밸런싱  │ 체크인 분산  │ 부하 분산     │ 성능 향상    │
│ Rate Limit   │ 차량 통제   │ 요청 제한     │ 안정성 확보  │
│ SSL/TLS      │ 보안 통신   │ 암호화        │ 데이터 보호  │
│ 캐싱         │ 안내 책자   │ 빠른 응답     │ 속도 개선    │
└──────────────┴─────────────┴──────────────┴─────────────┘
```

---

## 📊 수치로 보는 효과

**API Gateway와 Nginx 도입 전후 비교**

| 지표 | Before (Gateway 없음) | After (Nginx Gateway) | 개선율 |
|------|----------------------|----------------------|--------|
| 평균 응답 시간 | 250ms | 80ms | **68%↓** |
| SSL 처리 시간 | 각 서비스 50ms | Gateway 15ms | **70%↓** |
| 인증 처리 중복 | 5개 서비스 각각 | 1회만 처리 | **80%↓** |
| CORS 설정 관리 | 5개 파일 | 1개 파일 | **80%↓** |
| 로드 밸런싱 | 불가능 | 자동 분산 | **100%↑** |
| Rate Limiting | 불가능 | 초당 10,000 요청 | **100%↑** |
| 월 인프라 비용 | $500 | $150 | **70%↓** |
| SSL 인증서 관리 | 5개 | 1개 | **80%↓** |

**실제 기업 사례**:
- **Netflix**: Zuul Gateway로 초당 200만 요청 처리, 99.99% 가용성 달성
- **쿠팡**: Nginx로 Black Friday 트래픽 500% 급증 대응
- **카카오**: API Gateway로 300개 이상 마이크로서비스 통합 관리

---

## 16.1 API Gateway 필요성

### 16.1.1 마이크로서비스 통신 문제

**Gateway 없는 구조:**

```
[클라이언트]
    ↓
    ├─→ User Service (8081)
    ├─→ Account Service (8082)
    ├─→ Trade Service (8083)
    ├─→ AI Service (8084)
    └─→ Scraper Service (8085)

문제점:
❌ 클라이언트가 모든 서비스 주소 알아야 함
❌ CORS 설정이 모든 서비스에 중복
❌ 인증/인가를 각 서비스에서 처리
❌ 로드 밸런싱 불가
❌ SSL/TLS 인증서 관리 복잡
```

**Gateway 있는 구조:**

```
[클라이언트]
    ↓
[API Gateway: 80/443]
    ├─→ User Service (내부망)
    ├─→ Account Service (내부망)
    ├─→ Trade Service (내부망)
    ├─→ AI Service (내부망)
    └─→ Scraper Service (내부망)

장점:
✅ 단일 진입점 (Single Entry Point)
✅ 통합 인증/인가
✅ 로드 밸런싱
✅ SSL/TLS 종료 (Termination)
✅ 요청 라우팅 및 변환
✅ 속도 제한 (Rate Limiting)
```

---

## 16.2 Nginx 리버스 프록시 설정

### 16.2.1 기본 Nginx 설정

**docker/nginx/nginx.conf:**

```nginx
# 워커 프로세스 설정
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

# 이벤트 블록
events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

# HTTP 블록
http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 로그 형식
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;

    # 성능 최적화
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip 압축
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss
               application/rss+xml font/truetype font/opentype
               application/vnd.ms-fontobject image/svg+xml;

    # 업스트림 정의
    upstream user_backend {
        least_conn;  # 최소 연결 수 기반 로드 밸런싱
        server user-service:8081 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    upstream account_backend {
        least_conn;
        server account-service:8082 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    upstream trade_backend {
        least_conn;
        server trade-service:8083 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    upstream ai_backend {
        least_conn;
        server ai-service:8084 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    upstream scraper_backend {
        least_conn;
        server scraper-service:8085 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    # 메인 서버 블록
    server {
        listen 80;
        server_name lktrade.local;

        # 클라이언트 요청 크기 제한
        client_max_body_size 10M;

        # 보안 헤더
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # 헬스체크 엔드포인트
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # API 라우팅
        location /api/users {
            proxy_pass http://user_backend;
            include /etc/nginx/proxy_params;
        }

        location /api/accounts {
            proxy_pass http://account_backend;
            include /etc/nginx/proxy_params;
        }

        location /api/trades {
            proxy_pass http://trade_backend;
            include /etc/nginx/proxy_params;
        }

        location /api/ai {
            proxy_pass http://ai_backend;
            include /etc/nginx/proxy_params;
        }

        location /api/scraper {
            proxy_pass http://scraper_backend;
            include /etc/nginx/proxy_params;
        }

        # WebSocket 지원 (실시간 데이터)
        location /ws/ {
            proxy_pass http://trade_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # 정적 파일 (Swagger UI 등)
        location /swagger-ui/ {
            proxy_pass http://user_backend/swagger-ui/;
            include /etc/nginx/proxy_params;
        }

        location /api-docs/ {
            proxy_pass http://user_backend/api-docs/;
            include /etc/nginx/proxy_params;
        }
    }
}
```

---

### 16.2.2 프록시 파라미터

**docker/nginx/proxy_params:**

```nginx
# 프록시 헤더 설정
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Port $server_port;

# 타임아웃 설정
proxy_connect_timeout 60s;
proxy_send_timeout 60s;
proxy_read_timeout 60s;

# 버퍼 설정
proxy_buffering on;
proxy_buffer_size 4k;
proxy_buffers 8 4k;
proxy_busy_buffers_size 8k;

# HTTP 버전
proxy_http_version 1.1;
proxy_set_header Connection "";

# 리다이렉트 처리
proxy_redirect off;
```

---

### 16.2.3 docker-compose.yml에 Nginx 추가

```yaml
services:
  # ... (기존 서비스들)

  # Nginx API Gateway
  nginx:
    image: nginx:alpine
    container_name: lktrade-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/nginx/proxy_params:/etc/nginx/proxy_params:ro
      - ./docker/nginx/ssl:/etc/nginx/ssl:ro
      - nginx-logs:/var/log/nginx
    networks:
      - lktrade-network
    depends_on:
      - user-service
      - account-service
      - trade-service
      - ai-service
      - scraper-service
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

volumes:
  # ... (기존 볼륨들)
  nginx-logs:
    name: lktrade-nginx-logs
```

---

## 16.3 로드 밸런싱

### 16.3.1 스케일링 + 로드 밸런싱

**docker-compose.yml 수정:**

```yaml
services:
  # Trade 서비스 (스케일 가능하도록 포트 제거)
  trade-service:
    build:
      context: .
      dockerfile: modules/trade/api/Dockerfile
    # ports 제거 (내부에서만 접근)
    expose:
      - "8083"
    environment:
      <<: *common-env
      SERVER_PORT: 8083
    networks:
      - lktrade-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      <<: *healthcheck-defaults
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8083/actuator/health"]
    restart: unless-stopped
```

**Nginx 설정 (자동 로드 밸런싱):**

```nginx
upstream trade_backend {
    least_conn;  # 연결 수 기반

    # Docker Compose가 자동으로 DNS 라운드 로빈
    server trade-service:8083 max_fails=3 fail_timeout=30s;

    keepalive 32;
}

server {
    location /api/trades {
        proxy_pass http://trade_backend;
        include /etc/nginx/proxy_params;
    }
}
```

**스케일 실행:**

```bash
# Trade 서비스 3개로 스케일
docker compose up -d --scale trade-service=3

# Nginx가 자동으로 3개 인스턴스에 분산
# trade-service-1, trade-service-2, trade-service-3
```

---

### 16.3.2 로드 밸런싱 알고리즘

**nginx.conf 업스트림 설정:**

```nginx
# 1. 라운드 로빈 (기본)
upstream backend1 {
    server service1:8080;
    server service2:8080;
    server service3:8080;
    # 요청을 순차적으로 분산: 1 → 2 → 3 → 1 → 2 → 3 ...
}

# 2. 최소 연결 (least_conn)
upstream backend2 {
    least_conn;
    server service1:8080;
    server service2:8080;
    server service3:8080;
    # 현재 연결이 가장 적은 서버로 전달
}

# 3. IP 해시 (ip_hash)
upstream backend3 {
    ip_hash;
    server service1:8080;
    server service2:8080;
    server service3:8080;
    # 같은 클라이언트 IP는 항상 같은 서버로
    # 세션 고정 (Sticky Session) 필요 시 사용
}

# 4. 가중치 기반 (weighted)
upstream backend4 {
    server service1:8080 weight=3;  # 60%
    server service2:8080 weight=2;  # 40%
    # 성능이 좋은 서버에 더 많은 요청
}

# 5. 조합
upstream backend5 {
    least_conn;
    server service1:8080 weight=3 max_fails=3 fail_timeout=30s;
    server service2:8080 weight=2 max_fails=3 fail_timeout=30s;
    server service3:8080 weight=1 max_fails=3 fail_timeout=30s backup;
    # service3는 백업 (다른 서버 장애 시만 사용)
}
```

---

## 16.4 SSL/TLS 설정

### 16.4.1 자체 서명 인증서 생성 (개발용)

**docker/nginx/ssl/generate-cert.sh:**

```bash
#!/bin/bash

# 개발용 자체 서명 인증서 생성

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/lktrade.key \
  -out /etc/nginx/ssl/lktrade.crt \
  -subj "/C=KR/ST=Seoul/L=Seoul/O=LK-Trade/CN=lktrade.local"

echo "자체 서명 인증서 생성 완료"
echo "Key: /etc/nginx/ssl/lktrade.key"
echo "Cert: /etc/nginx/ssl/lktrade.crt"
```

**실행:**

```bash
# 인증서 생성
chmod +x docker/nginx/ssl/generate-cert.sh
docker run --rm -v $(pwd)/docker/nginx/ssl:/etc/nginx/ssl alpine sh -c \
  "apk add openssl && sh /etc/nginx/ssl/generate-cert.sh"
```

---

### 16.4.2 HTTPS Nginx 설정

**docker/nginx/nginx.conf (HTTPS 추가):**

```nginx
http {
    # ... (기존 설정)

    # HTTP → HTTPS 리다이렉트
    server {
        listen 80;
        server_name lktrade.local;

        # Let's Encrypt ACME 챌린지 (프로덕션)
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        # 나머지는 HTTPS로 리다이렉트
        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    # HTTPS 서버
    server {
        listen 443 ssl http2;
        server_name lktrade.local;

        # SSL 인증서
        ssl_certificate /etc/nginx/ssl/lktrade.crt;
        ssl_certificate_key /etc/nginx/ssl/lktrade.key;

        # SSL 설정
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # HSTS (HTTP Strict Transport Security)
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # 보안 헤더
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;

        # 클라이언트 요청 크기 제한
        client_max_body_size 10M;

        # API 라우팅 (기존과 동일)
        location /api/users {
            proxy_pass http://user_backend;
            include /etc/nginx/proxy_params;
        }

        location /api/accounts {
            proxy_pass http://account_backend;
            include /etc/nginx/proxy_params;
        }

        location /api/trades {
            proxy_pass http://trade_backend;
            include /etc/nginx/proxy_params;
        }

        location /api/ai {
            proxy_pass http://ai_backend;
            include /etc/nginx/proxy_params;
        }

        location /api/scraper {
            proxy_pass http://scraper_backend;
            include /etc/nginx/proxy_params;
        }

        # WebSocket (WSS)
        location /ws/ {
            proxy_pass http://trade_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            include /etc/nginx/proxy_params;
        }
    }
}
```

---

### 16.4.3 Let's Encrypt (프로덕션)

**docker-compose.prod.yml:**

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/nginx/proxy_params:/etc/nginx/proxy_params:ro
      - certbot-etc:/etc/letsencrypt
      - certbot-var:/var/lib/letsencrypt
      - certbot-www:/var/www/certbot
      - nginx-logs:/var/log/nginx
    depends_on:
      - certbot

  # Certbot (Let's Encrypt)
  certbot:
    image: certbot/certbot:latest
    volumes:
      - certbot-etc:/etc/letsencrypt
      - certbot-var:/var/lib/letsencrypt
      - certbot-www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

volumes:
  certbot-etc:
  certbot-var:
  certbot-www:
```

**인증서 발급:**

```bash
# 초기 인증서 발급
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email admin@lktrade.com \
  --agree-tos \
  --no-eff-email \
  -d lktrade.com \
  -d www.lktrade.com

# Nginx 재시작
docker compose -f docker-compose.prod.yml restart nginx
```

---

## 16.5 속도 제한 (Rate Limiting)

### 16.5.1 기본 Rate Limiting

**nginx.conf:**

```nginx
http {
    # ... (기존 설정)

    # Rate Limit Zone 정의
    # 클라이언트 IP 기반, 10MB 메모리, 초당 10개 요청
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    # 인증 API는 더 엄격하게
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;

    # 거래 API는 버스트 허용
    limit_req_zone $binary_remote_addr zone=trade_limit:10m rate=20r/s;

    server {
        listen 80;

        # 일반 API (초당 10개, 버스트 20개)
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://backend;
        }

        # 로그인/회원가입 (분당 5개)
        location /api/users/login {
            limit_req zone=auth_limit burst=2 nodelay;
            proxy_pass http://user_backend;
        }

        location /api/users/register {
            limit_req zone=auth_limit burst=2 nodelay;
            proxy_pass http://user_backend;
        }

        # 거래 실행 (초당 20개, 버스트 50개)
        location /api/trades/execute {
            limit_req zone=trade_limit burst=50 nodelay;
            proxy_pass http://trade_backend;
        }

        # Rate Limit 초과 시 커스텀 에러
        error_page 429 /429.json;
        location = /429.json {
            internal;
            default_type application/json;
            return 429 '{"error":"Too Many Requests","message":"Please slow down"}';
        }
    }
}
```

---

### 16.5.2 사용자별 Rate Limiting

**nginx.conf:**

```nginx
http {
    # JWT 토큰에서 사용자 ID 추출 (Lua 필요)
    # 또는 X-User-ID 헤더 사용

    # 사용자별 Rate Limit
    map $http_x_user_id $limit_key {
        default $http_x_user_id;
        "" $binary_remote_addr;  # 인증 안 된 사용자는 IP 기반
    }

    limit_req_zone $limit_key zone=per_user:10m rate=100r/s;

    server {
        location /api/ {
            limit_req zone=per_user burst=200 nodelay;
            proxy_pass http://backend;
        }
    }
}
```

---

## 16.6 캐싱

### 16.6.1 정적 컨텐츠 캐싱

**nginx.conf:**

```nginx
http {
    # 캐시 경로 설정
    proxy_cache_path /var/cache/nginx
                     levels=1:2
                     keys_zone=api_cache:10m
                     max_size=1g
                     inactive=60m
                     use_temp_path=off;

    server {
        # 시장 데이터 (1분 캐싱)
        location /api/market-price/current {
            proxy_cache api_cache;
            proxy_cache_valid 200 1m;
            proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
            proxy_cache_background_update on;
            proxy_cache_lock on;

            add_header X-Cache-Status $upstream_cache_status;

            proxy_pass http://scraper_backend;
            include /etc/nginx/proxy_params;
        }

        # AI 전략 분석 (10분 캐싱)
        location /api/ai/strategy/analyze {
            proxy_cache api_cache;
            proxy_cache_valid 200 10m;
            proxy_cache_key "$request_uri|$request_body";
            proxy_cache_methods GET POST;

            add_header X-Cache-Status $upstream_cache_status;

            proxy_pass http://ai_backend;
            include /etc/nginx/proxy_params;
        }

        # 캐시 무효화 (관리자만)
        location /api/cache/purge {
            allow 10.0.0.0/8;  # 내부 네트워크만
            deny all;

            proxy_cache_purge api_cache "$request_uri";
        }
    }
}
```

**docker-compose.yml 볼륨 추가:**

```yaml
services:
  nginx:
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/nginx/proxy_params:/etc/nginx/proxy_params:ro
      - nginx-cache:/var/cache/nginx  # 캐시 볼륨
      - nginx-logs:/var/log/nginx

volumes:
  nginx-cache:
    name: lktrade-nginx-cache
```

---

## 16.7 모니터링 및 로깅

### 16.7.1 상세 로깅

**nginx.conf:**

```nginx
http {
    # 상세 로그 형식
    log_format detailed '$remote_addr - $remote_user [$time_local] '
                        '"$request" $status $body_bytes_sent '
                        '"$http_referer" "$http_user_agent" '
                        'rt=$request_time '
                        'uct="$upstream_connect_time" '
                        'uht="$upstream_header_time" '
                        'urt="$upstream_response_time" '
                        'upstream="$upstream_addr" '
                        'cache="$upstream_cache_status"';

    access_log /var/log/nginx/access.log detailed;
    error_log /var/log/nginx/error.log warn;

    server {
        # API별 로그 파일 분리
        location /api/users {
            access_log /var/log/nginx/user-service.log detailed;
            proxy_pass http://user_backend;
        }

        location /api/trades {
            access_log /var/log/nginx/trade-service.log detailed;
            proxy_pass http://trade_backend;
        }
    }
}
```

---

### 16.7.2 Prometheus Exporter

**docker-compose.yml:**

```yaml
services:
  # Nginx Prometheus Exporter
  nginx-exporter:
    image: nginx/nginx-prometheus-exporter:latest
    container_name: lktrade-nginx-exporter
    profiles: ["monitoring"]
    command:
      - -nginx.scrape-uri=http://nginx:80/nginx_status
    ports:
      - "9113:9113"
    networks:
      - lktrade-network
    depends_on:
      - nginx
```

**nginx.conf에 status 엔드포인트 추가:**

```nginx
server {
    # 모니터링 전용 (내부만 접근)
    location /nginx_status {
        stub_status on;
        access_log off;
        allow 172.0.0.0/8;  # Docker 네트워크
        deny all;
    }
}
```

---

## 16.8 완전한 설정 예제

**docker-compose.yml (Nginx 포함):**

```yaml
version: '3.8'

x-healthcheck-defaults: &healthcheck-defaults
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s

services:
  # ==================== Nginx Gateway ====================
  nginx:
    image: nginx:alpine
    container_name: lktrade-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/nginx/proxy_params:/etc/nginx/proxy_params:ro
      - ./docker/nginx/ssl:/etc/nginx/ssl:ro
      - nginx-cache:/var/cache/nginx
      - nginx-logs:/var/log/nginx
    networks:
      - lktrade-network
    depends_on:
      - user-service
      - account-service
      - trade-service
      - ai-service
      - scraper-service
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost/health"]
      interval: 10s
      timeout: 5s
      retries: 3
    restart: unless-stopped
    labels:
      - "com.lktrade.service=gateway"
      - "com.lktrade.tier=proxy"

  # ... (기존 서비스들: postgres, redis, user-service 등)

volumes:
  nginx-cache:
    name: lktrade-nginx-cache
  nginx-logs:
    name: lktrade-nginx-logs
  # ... (기존 볼륨들)
```

---

## 16.9 테스트 및 검증

### 16.9.1 Nginx 설정 검증

```bash
# 설정 파일 문법 체크
docker compose exec nginx nginx -t

# 출력:
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful

# 설정 리로드 (다운타임 없이)
docker compose exec nginx nginx -s reload
```

---

### 16.9.2 API 라우팅 테스트

```bash
# 1. User API
curl http://localhost/api/users/health
# → user-service:8081로 라우팅

# 2. Account API
curl http://localhost/api/accounts/health
# → account-service:8082로 라우팅

# 3. Trade API
curl http://localhost/api/trades/health
# → trade-service:8083로 라우팅

# 4. 헤더 확인
curl -I http://localhost/api/users/health
# X-Frame-Options: SAMEORIGIN
# X-Content-Type-Options: nosniff
# X-XSS-Protection: 1; mode=block

# 5. Rate Limit 테스트
for i in {1..100}; do
  curl http://localhost/api/users/test
done
# 11번째 요청부터 429 Too Many Requests
```

---

### 16.9.3 로드 밸런싱 테스트

```bash
# Trade 서비스 스케일
docker compose up -d --scale trade-service=3

# 여러 요청 전송
for i in {1..10}; do
  curl http://localhost/api/trades/health
done

# Nginx 로그 확인
docker compose logs nginx | grep trade
# trade-service-1 응답
# trade-service-2 응답
# trade-service-3 응답
# ... 순환
```

---

## 16.10 Makefile 업데이트

**Makefile:**

```makefile
# ... (기존 명령어)

# Nginx 관련
nginx-reload:
	docker compose exec nginx nginx -s reload

nginx-test:
	docker compose exec nginx nginx -t

nginx-logs:
	docker compose logs -f nginx

nginx-access-log:
	docker compose exec nginx tail -f /var/log/nginx/access.log

nginx-error-log:
	docker compose exec nginx tail -f /var/log/nginx/error.log

# 스케일링
scale-trade:
	docker compose up -d --scale trade-service=3

scale-down:
	docker compose up -d --scale trade-service=1
```

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: "왜 모든 서비스가 403 Forbidden 에러가 나요?"

**상황**: 주니어 개발자가 Nginx 설정 후 모든 API가 403 에러 반환

```nginx
# ❌ 주니어 개발자가 작성한 nginx.conf
server {
    listen 80;

    location /api/users {
        proxy_pass http://user-service:8081;
    }
}
```

**문제점**:
- proxy_pass 뒤에 슬래시(/) 누락
- 프록시 헤더 설정 없음
- 백엔드 서비스가 요청 출처를 모름

**해결책**:
```nginx
# ✅ 올바른 설정
http {
    upstream user_backend {
        server user-service:8081;
    }

    server {
        listen 80;

        location /api/users {
            proxy_pass http://user_backend;

            # 프록시 헤더 설정 필수
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

**배운 점**:
- 💡 프록시 헤더는 백엔드가 원본 요청 정보를 알기 위해 필수
- 💡 proxy_params 파일로 공통 설정 분리 추천
- 💡 nginx -t로 설정 검증 후 재시작

---

### 시나리오 2: "Rate Limiting 설정했는데 정상 사용자도 차단돼요!"

**상황**: Rate Limiting을 너무 엄격하게 설정하여 정상 사용자 차단

```nginx
# ❌ 너무 엄격한 설정
http {
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=1r/s;

    server {
        location /api/ {
            limit_req zone=api_limit;  # burst 없음
            proxy_pass http://backend;
        }
    }
}
```

**문제점**:
- 초당 1개 요청만 허용 (너무 제한적)
- burst 설정 없어 순간 트래픽 처리 불가
- 모든 API에 동일한 제한 적용

**해결책**:
```nginx
# ✅ 합리적인 설정
http {
    # 일반 API: 초당 10개, 버스트 20개
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    # 인증 API: 분당 5개, 버스트 2개 (보안 중요)
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;

    server {
        # 일반 API
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://backend;
        }

        # 로그인 API (더 엄격)
        location /api/auth/login {
            limit_req zone=auth_limit burst=2 nodelay;
            proxy_pass http://backend;
        }
    }
}
```

**배운 점**:
- 💡 burst로 순간 트래픽 허용
- 💡 API별 다른 제한 설정
- 💡 nodelay로 대기 없이 즉시 처리
- 💡 모니터링하며 점진적으로 조정

---

### 시나리오 3: "HTTPS 설정했는데 무한 리다이렉트 발생!"

**상황**: HTTP를 HTTPS로 리다이렉트 설정 후 무한 루프

```nginx
# ❌ 잘못된 리다이렉트 설정
server {
    listen 80;
    listen 443 ssl;

    # 모든 요청을 HTTPS로 리다이렉트
    return 301 https://$server_name$request_uri;

    ssl_certificate /etc/nginx/ssl/cert.crt;
    ssl_certificate_key /etc/nginx/ssl/cert.key;
}
```

**문제점**:
- 80번과 443번 포트를 같은 서버 블록에서 처리
- HTTPS 요청도 다시 HTTPS로 리다이렉트됨

**해결책**:
```nginx
# ✅ 올바른 설정
# HTTP 서버 (80번 포트)
server {
    listen 80;
    server_name lktrade.local;

    # HTTP만 HTTPS로 리다이렉트
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS 서버 (443번 포트)
server {
    listen 443 ssl http2;
    server_name lktrade.local;

    ssl_certificate /etc/nginx/ssl/cert.crt;
    ssl_certificate_key /etc/nginx/ssl/cert.key;

    # 실제 프록시 설정
    location /api/ {
        proxy_pass http://backend;
        include proxy_params;
    }
}
```

**배운 점**:
- 💡 HTTP(80)와 HTTPS(443)는 별도 서버 블록으로 분리
- 💡 리다이렉트는 HTTP 블록에만 설정
- 💡 curl -I로 리다이렉트 체인 확인

---

### 시나리오 4: "로드 밸런싱이 안 돼요. 한 서버로만 요청이 가요!"

**상황**: 스케일 아웃했는데 트래픽이 한 서버로만 몰림

```bash
# 3개로 스케일
docker compose up -d --scale trade-service=3

# 확인
docker ps | grep trade-service
# trade-service-1, trade-service-2, trade-service-3 실행 중
```

```nginx
# ❌ 문제의 nginx 설정
upstream trade_backend {
    server trade-service-1:8083;  # 고정된 이름
}
```

**문제점**:
- Docker Compose가 생성한 서비스명 (trade-service-1, -2, -3)을 직접 지정
- DNS 라운드 로빈 미활용
- 수동으로 모든 인스턴스 추가 필요

**해결책**:
```nginx
# ✅ Docker Compose DNS 활용
upstream trade_backend {
    least_conn;

    # Docker Compose가 자동으로 DNS 라운드 로빈 제공
    server trade-service:8083;

    keepalive 32;
}

server {
    location /api/trades {
        proxy_pass http://trade_backend;
        include proxy_params;
    }
}
```

**추가 확인**:
```bash
# Nginx 컨테이너에서 DNS 확인
docker compose exec nginx nslookup trade-service

# 출력: trade-service의 여러 IP 주소
# Docker가 자동으로 3개 인스턴스 IP 반환
```

**배운 점**:
- 💡 Docker Compose 서비스명 사용 (인스턴스 번호 없이)
- 💡 Docker DNS가 자동으로 로드 밸런싱 지원
- 💡 스케일 변경 시 Nginx 설정 수정 불필요
- 💡 least_conn 알고리즘으로 효율적 분산

---

## ❓ FAQ

<details>
<summary><strong>Q1: API Gateway와 Reverse Proxy의 차이점은 무엇인가요?</strong></summary>

**A**: Reverse Proxy는 API Gateway의 하위 개념입니다.

**상세 설명**:
- **Reverse Proxy**: 클라이언트 요청을 백엔드 서버로 전달하는 기본 기능
- **API Gateway**: Reverse Proxy + 인증/인가 + Rate Limiting + 캐싱 + 로깅 등

**비교표**:
| 기능 | Reverse Proxy | API Gateway |
|------|---------------|-------------|
| 요청 전달 | ✅ | ✅ |
| 로드 밸런싱 | ✅ | ✅ |
| SSL 종료 | ✅ | ✅ |
| 인증/인가 | ❌ | ✅ |
| Rate Limiting | 부분 지원 | ✅ |
| API 버전 관리 | ❌ | ✅ |
| 요청/응답 변환 | ❌ | ✅ |

**실무 팁**:
💡 Nginx는 Reverse Proxy지만, 설정으로 API Gateway처럼 사용 가능합니다.

</details>

<details>
<summary><strong>Q2: Nginx vs HAProxy vs Traefik, 어떤 걸 선택해야 하나요?</strong></summary>

**A**: 프로젝트 요구사항과 팀 역량에 따라 선택합니다.

**비교**:

| 특성 | Nginx | HAProxy | Traefik |
|------|-------|---------|---------|
| 학습 곡선 | 중간 | 낮음 | 낮음 |
| 성능 | 높음 | 매우 높음 | 중간 |
| 설정 방식 | 파일 기반 | 파일 기반 | 동적 (자동 발견) |
| HTTP/2 | ✅ | ✅ | ✅ |
| gRPC | ✅ | ✅ | ✅ |
| 웹 서버 기능 | ✅ | ❌ | ❌ |
| Docker 통합 | 수동 | 수동 | 자동 |
| Let's Encrypt | 수동 | 수동 | 자동 |

**추천**:
- **Nginx**: 범용적, 웹 서버 + 프록시 필요 시
- **HAProxy**: 최고 성능, L7 로드 밸런싱 중심
- **Traefik**: Docker/Kubernetes 환경, 자동화 선호

**실무 팁**:
💡 대부분의 경우 Nginx로 충분합니다. 특별한 이유 없으면 Nginx 추천.

</details>

<details>
<summary><strong>Q3: keepalive 설정은 왜 필요한가요?</strong></summary>

**A**: HTTP 연결을 재사용하여 성능을 크게 향상시킵니다.

**keepalive 없을 때**:
```
요청 1: 연결 → 요청 → 응답 → 연결 종료
요청 2: 연결 → 요청 → 응답 → 연결 종료  (매번 새 연결)
요청 3: 연결 → 요청 → 응답 → 연결 종료
```

**keepalive 있을 때**:
```
연결 → 요청1 → 응답1 → 요청2 → 응답2 → 요청3 → 응답3 → (연결 유지)
```

**성능 비교**:
| 지표 | keepalive 없음 | keepalive 32 | 개선 |
|------|---------------|--------------|------|
| 요청 처리 시간 | 50ms | 10ms | **80%↓** |
| CPU 사용률 | 높음 | 낮음 | **60%↓** |
| 동시 연결 수 | 1000 | 5000 | **400%↑** |

**설정 예시**:
```nginx
upstream backend {
    server app:8080;
    keepalive 32;  # 32개 연결 풀
}

server {
    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";  # keepalive 활성화
    }
}
```

**실무 팁**:
💡 keepalive 값은 (worker_connections / 백엔드 서버 수) 의 10-20% 정도로 설정

</details>

<details>
<summary><strong>Q4: Rate Limiting의 burst와 nodelay는 언제 사용하나요?</strong></summary>

**A**: burst는 순간 트래픽 허용, nodelay는 즉시 처리입니다.

**burst 없을 때** (rate=10r/s):
```
시간: 0.0s  0.1s  0.2s  0.3s
요청: ✅    ✅    ✅    ✅   (1개씩만 처리)
      ❌❌❌ ❌❌❌ ❌❌❌      (나머지 거부)
```

**burst=20 있을 때**:
```
시간: 0.0s
요청: ✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅  (20개까지 허용)
      ❌❌❌                          (21개부터 거부)
```

**nodelay 추가**:
```
burst=20              → 20개 요청을 대기열에 넣고 천천히 처리
burst=20 nodelay      → 20개 요청을 즉시 처리 (대기 없음)
```

**사용 시나리오**:
```nginx
# 1. 일반 API - burst + nodelay
location /api/products {
    limit_req zone=api_limit burst=20 nodelay;  # 순간 트래픽 OK
}

# 2. 로그인 API - burst만 (DDoS 방지)
location /api/login {
    limit_req zone=auth_limit burst=5;  # 대기 강제 (공격 지연)
}

# 3. 결제 API - burst 없음
location /api/payment {
    limit_req zone=payment_limit;  # 정확히 제한
}
```

**실무 팁**:
💡 정상 사용자 보호: burst 높게, nodelay 사용
💡 보안 중요 API: burst 낮게, nodelay 제거

</details>

<details>
<summary><strong>Q5: SSL/TLS 인증서는 어떻게 관리해야 하나요?</strong></summary>

**A**: 개발은 자체 서명, 프로덕션은 Let's Encrypt 사용

**환경별 전략**:

**개발/테스트**:
```bash
# 자체 서명 인증서 생성 (5분)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx.key -out nginx.crt \
  -subj "/CN=localhost"
```

**스테이징**:
```bash
# Let's Encrypt 스테이징 (무료, 테스트용)
certbot certonly --staging \
  --webroot -w /var/www/certbot \
  -d staging.lktrade.com
```

**프로덕션**:
```bash
# Let's Encrypt 프로덕션 (무료, 자동 갱신)
certbot certonly \
  --webroot -w /var/www/certbot \
  -d lktrade.com -d www.lktrade.com

# 자동 갱신 (90일 유효 → 60일마다 자동 갱신)
certbot renew --dry-run
```

**docker-compose.yml**:
```yaml
services:
  certbot:
    image: certbot/certbot
    volumes:
      - certbot-etc:/etc/letsencrypt
      - certbot-www:/var/www/certbot
    # 매일 자동 갱신 확인
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
```

**실무 팁**:
💡 인증서 만료 30일 전 알림 설정
💡 Certbot은 60일 이상 남았으면 갱신 안 함
💡 와일드카드 인증서는 DNS 인증 필요

</details>

<details>
<summary><strong>Q6: Nginx 캐싱과 Redis 캐싱의 차이는 무엇인가요?</strong></summary>

**A**: Nginx는 HTTP 응답 캐싱, Redis는 애플리케이션 데이터 캐싱입니다.

**비교**:

| 특성 | Nginx 캐싱 | Redis 캐싱 |
|------|-----------|-----------|
| 위치 | 프록시 레벨 | 애플리케이션 레벨 |
| 캐시 키 | URL | 커스텀 키 |
| 캐시 대상 | HTTP 응답 전체 | 데이터 일부 |
| 유효성 검증 | HTTP 헤더 기반 | 애플리케이션 제어 |
| 공유 범위 | 모든 클라이언트 | 애플리케이션 선택 |
| 성능 | 매우 빠름 | 빠름 |

**사용 시나리오**:

```nginx
# Nginx 캐싱 - 정적 API 응답
location /api/market/current-price {
    proxy_cache api_cache;
    proxy_cache_valid 200 1m;  # 1분 캐싱
    proxy_pass http://backend;
}
```

```java
// Redis 캐싱- 동적 계산 결과
@Cacheable(value = "user", key = "#userId")
public User getUserById(Long userId) {
    return userRepository.findById(userId);
}
```

**조합 사용**:
```
[클라이언트]
    ↓
[Nginx 캐시] ← 첫 방어선 (HTTP 응답 캐싱)
    ↓
[애플리케이션]
    ↓
[Redis 캐시] ← 두 번째 방어선 (데이터 캐싱)
    ↓
[데이터베이스]
```

**실무 팁**:
💡 Nginx 캐싱: 동일 URL 요청이 많을 때
💡 Redis 캐싱: 복잡한 계산/조회가 많을 때
💡 둘 다 사용하면 최대 성능

</details>

<details>
<summary><strong>Q7: 로드 밸런싱 알고리즘은 어떤 것을 선택해야 하나요?</strong></summary>

**A**: 서비스 특성에 따라 선택합니다.

**알고리즘별 특성**:

**1. Round Robin (기본)**:
```nginx
upstream backend {
    server server1:8080;
    server server2:8080;
    server server3:8080;
}
```
- **사용 시기**: 모든 서버 성능이 동일할 때
- **장점**: 단순, 공평한 분산
- **단점**: 서버 상태 고려 안 함

**2. Least Connections**:
```nginx
upstream backend {
    least_conn;
    server server1:8080;
    server server2:8080;
}
```
- **사용 시기**: 요청 처리 시간이 다를 때 (롱 폴링, 스트리밍)
- **장점**: 부하가 적은 서버로 분산
- **단점**: 약간의 오버헤드

**3. IP Hash**:
```nginx
upstream backend {
    ip_hash;
    server server1:8080;
    server server2:8080;
}
```
- **사용 시기**: 세션 고정 필요 시 (Sticky Session)
- **장점**: 같은 클라이언트 = 같은 서버
- **단점**: 불균등 분산 가능

**4. Weighted (가중치)**:
```nginx
upstream backend {
    server server1:8080 weight=3;  # 60%
    server server2:8080 weight=2;  # 40%
}
```
- **사용 시기**: 서버 성능이 다를 때
- **장점**: 성능에 따른 분산
- **단점**: 수동 조정 필요

**실무 추천**:
```nginx
# REST API (무상태)
upstream api_backend {
    least_conn;  # 추천
    server api1:8080;
    server api2:8080;
}

# WebSocket (상태 유지)
upstream ws_backend {
    ip_hash;  # 추천
    server ws1:8080;
    server ws2:8080;
}

# 정적 파일
upstream static_backend {
    # Round Robin (기본값) - 추천
    server cdn1:8080;
    server cdn2:8080;
}
```

**실무 팁**:
💡 대부분의 경우 least_conn이 최선
💡 세션 필요 시 Redis 세션 공유 > ip_hash
💡 모니터링하며 조정

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. API Gateway가 무엇이고, 왜 필요한가요?</strong></summary>

**모범 답안 포인트**
- API Gateway는 클라이언트와 마이크로서비스 사이의 단일 진입점
- 라우팅, 인증, Rate Limiting, 로드 밸런싱 등을 중앙에서 처리
- 클라이언트가 여러 서비스 주소를 알 필요 없음
- 보안, 모니터링, 로깅을 한곳에서 관리

**예시 답변**
> "API Gateway는 쇼핑몰의 중앙 안내 데스크와 같습니다. 클라이언트가 여러 마이크로서비스에 직접 접근하는 대신, API Gateway를 통해 단일 진입점으로 접근합니다. 이를 통해 인증/인가, 라우팅, Rate Limiting 등을 중앙에서 처리할 수 있어 각 서비스의 부담을 줄이고 보안을 강화할 수 있습니다."

**꼬리 질문**
- Q: API Gateway 없이도 개발할 수 있지 않나요?
- A: 가능하지만, CORS 설정, 인증 로직, SSL 인증서 등을 모든 서비스에 중복 구현해야 하고, 클라이언트가 여러 엔드포인트를 관리해야 해서 복잡도가 크게 증가합니다.

**실무 연관**
- 마이크로서비스 아키텍처에서 필수 컴포넌트
- Netflix Zuul, Spring Cloud Gateway, Kong 등이 대표적인 API Gateway 솔루션

</details>

<details>
<summary><strong>2. Nginx의 Reverse Proxy와 Forward Proxy의 차이는?</strong></summary>

**모범 답안 포인트**
- **Forward Proxy**: 클라이언트 앞에 위치, 클라이언트를 대신해 요청
- **Reverse Proxy**: 서버 앞에 위치, 서버를 대신해 응답
- Nginx는 주로 Reverse Proxy로 사용
- Forward Proxy는 클라이언트 익명화, Reverse Proxy는 서버 보호

**예시 답변**
> "Forward Proxy는 클라이언트 측에서 작동하여 클라이언트를 대신해 외부 서버에 요청합니다. VPN이나 회사 방화벽이 대표적입니다. 반면 Reverse Proxy는 서버 측에서 작동하여 클라이언트 요청을 받아 백엔드 서버로 전달합니다. Nginx를 Reverse Proxy로 사용하면 클라이언트는 실제 백엔드 서버를 알 필요 없고, 로드 밸런싱, SSL 종료 등을 처리할 수 있습니다."

**꼬리 질문**
- Q: Reverse Proxy의 장점은?
- A: 보안 강화 (백엔드 서버 숨김), 로드 밸런싱, SSL/TLS 종료, 캐싱, 압축 등 다양한 기능 제공

**실무 연관**
- 거의 모든 프로덕션 환경에서 Reverse Proxy 사용
- CDN도 Reverse Proxy의 일종

</details>

<details>
<summary><strong>3. Nginx의 upstream과 proxy_pass의 역할은?</strong></summary>

**모범 답안 포인트**
- **upstream**: 백엔드 서버 그룹을 정의하는 블록
- **proxy_pass**: 실제 요청을 upstream으로 전달하는 지시어
- upstream에서 로드 밸런싱 알고리즘 설정
- proxy_pass에서 라우팅 규칙 설정

**예시 답변**
> "upstream은 백엔드 서버들을 그룹으로 정의하는 블록으로, 로드 밸런싱 방식과 서버 목록을 설정합니다. proxy_pass는 클라이언트 요청을 어느 upstream으로 전달할지 결정하는 지시어입니다. 예를 들어, upstream에서 user-service 그룹을 정의하고, location 블록에서 /api/users 경로를 user-service upstream으로 proxy_pass하는 방식으로 사용합니다."

**코드 예시**:
```nginx
upstream user_backend {
    least_conn;
    server user1:8081;
    server user2:8081;
}

server {
    location /api/users {
        proxy_pass http://user_backend;
    }
}
```

**실무 연관**
- 마이크로서비스별로 upstream 정의
- 경로 기반 라우팅 구현

</details>

<details>
<summary><strong>4. Rate Limiting은 왜 필요하고 어떻게 구현하나요?</strong></summary>

**모범 답안 포인트**
- DDoS 공격 방어
- 서버 과부하 방지
- 공정한 리소스 사용
- Nginx의 limit_req_zone과 limit_req 사용

**예시 답변**
> "Rate Limiting은 특정 시간 동안 허용되는 요청 수를 제한하여 서버를 보호합니다. DDoS 공격, 크롤러, 실수로 인한 무한 루프 등으로부터 서버를 보호하고, 모든 사용자가 공정하게 서비스를 이용할 수 있게 합니다. Nginx에서는 limit_req_zone으로 제한 영역을 정의하고, limit_req로 적용합니다."

**코드 예시**:
```nginx
http {
    # IP당 초당 10개 요청
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    server {
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://backend;
        }
    }
}
```

**꼬리 질문**
- Q: burst와 nodelay는 무슨 의미인가요?
- A: burst는 순간 트래픽을 허용하는 버퍼, nodelay는 대기 없이 즉시 처리하는 옵션입니다.

**실무 연관**
- API별 다른 제한 설정 (로그인 API는 더 엄격)
- 모니터링하며 점진적으로 조정

</details>

<details>
<summary><strong>5. Nginx에서 SSL/TLS를 어떻게 설정하나요?</strong></summary>

**모범 답안 포인트**
- 인증서와 개인키 필요
- listen 443 ssl로 HTTPS 포트 오픈
- ssl_certificate와 ssl_certificate_key 지시어 사용
- HTTP를 HTTPS로 리다이렉트 권장

**예시 답변**
> "Nginx에서 SSL/TLS를 설정하려면 먼저 인증서를 준비해야 합니다. 개발 환경은 자체 서명 인증서, 프로덕션은 Let's Encrypt를 사용합니다. 443번 포트로 listen하고 ssl_certificate와 ssl_certificate_key로 인증서 경로를 지정합니다. HTTP(80번 포트)는 HTTPS로 리다이렉트하여 모든 통신을 암호화합니다."

**코드 예시**:
```nginx
# HTTP → HTTPS 리다이렉트
server {
    listen 80;
    return 301 https://$server_name$request_uri;
}

# HTTPS 서버
server {
    listen 443 ssl http2;

    ssl_certificate /etc/nginx/ssl/cert.crt;
    ssl_certificate_key /etc/nginx/ssl/key.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://backend;
    }
}
```

**실무 연관**
- Let's Encrypt로 무료 SSL 인증서 발급
- Certbot으로 자동 갱신 설정

</details>

<details>
<summary><strong>6. Nginx 설정 변경 후 무중단 재시작하는 방법은?</strong></summary>

**모범 답안 포인트**
- nginx -t로 설정 파일 검증
- nginx -s reload로 무중단 재시작
- 기존 연결 유지하며 새 설정 적용
- 설정 오류 시 기존 설정 유지

**예시 답변**
> "Nginx 설정을 변경한 후에는 먼저 nginx -t 명령어로 문법 오류를 확인합니다. 오류가 없으면 nginx -s reload로 무중단 재시작합니다. reload는 기존 워커 프로세스는 유지하며 새로운 워커 프로세스를 생성하고, 기존 연결이 모두 종료되면 이전 워커를 종료합니다. 따라서 서비스 중단 없이 설정을 반영할 수 있습니다."

**명령어**:
```bash
# 1. 설정 검증
docker compose exec nginx nginx -t

# 2. 무중단 재시작
docker compose exec nginx nginx -s reload

# 3. (또는) 컨테이너 재시작
docker compose restart nginx
```

**꼬리 질문**
- Q: reload와 restart의 차이는?
- A: reload는 무중단(기존 연결 유지), restart는 서비스 중단 발생

**실무 연관**
- CI/CD 파이프라인에서 자동화
- 설정 변경 전 백업 권장

</details>

<details>
<summary><strong>7. Nginx 로그를 어떻게 확인하고 분석하나요?</strong></summary>

**모범 답안 포인트**
- access.log: 모든 요청 기록
- error.log: 오류 및 경고
- 로그 형식 커스터마이징 가능
- 응답 시간, 캐시 상태 등 추가 정보 기록

**예시 답변**
> "Nginx는 access.log에 모든 요청을, error.log에 오류를 기록합니다. log_format 지시어로 로그 형식을 커스터마이징하여 요청 시간, 업스트림 응답 시간, 캐시 상태 등을 추가로 기록할 수 있습니다. Docker 환경에서는 docker compose logs 명령어로 확인하거나, 볼륨 마운트로 호스트에서 직접 확인합니다."

**명령어**:
```bash
# 실시간 로그 확인
docker compose logs -f nginx

# access.log 확인
docker compose exec nginx tail -f /var/log/nginx/access.log

# error.log 확인
docker compose exec nginx tail -f /var/log/nginx/error.log

# 특정 패턴 검색
docker compose exec nginx grep "500" /var/log/nginx/access.log
```

**커스텀 로그 형식**:
```nginx
log_format detailed '$remote_addr - [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    'rt=$request_time urt="$upstream_response_time"';

access_log /var/log/nginx/access.log detailed;
```

**실무 연관**
- ELK 스택으로 중앙 로그 수집
- Prometheus Exporter로 메트릭 수집

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. Nginx의 이벤트 기반 아키텍처와 성능 최적화 전략을 설명하세요.</strong></summary>

**모범 답안 포인트**
- 비동기 이벤트 기반 (epoll, kqueue)
- 단일 워커 프로세스가 수천 개 연결 처리
- worker_processes와 worker_connections 최적화
- sendfile, tcp_nopush, tcp_nodelay 활용

**예시 답변**
> "Nginx는 이벤트 기반 비동기 아키텍처로 설계되어, Apache처럼 연결당 프로세스/스레드를 생성하지 않고 소수의 워커 프로세스로 수만 개의 동시 연결을 처리합니다. Linux에서는 epoll, BSD에서는 kqueue를 사용하여 효율적으로 I/O 이벤트를 관리합니다. worker_processes는 CPU 코어 수만큼, worker_connections는 시스템 리소스에 따라 설정하며, sendfile로 커널 레벨 파일 전송을 활용하여 성능을 극대화합니다."

**최적화 설정**:
```nginx
# 워커 프로세스 최적화
worker_processes auto;  # CPU 코어 수만큼 자동 설정

events {
    worker_connections 4096;  # 워커당 최대 연결 수
    use epoll;  # Linux 최적화
    multi_accept on;  # 여러 연결 동시 수락
}

http {
    # 파일 전송 최적화
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;

    # 타임아웃 최적화
    keepalive_timeout 65;
    keepalive_requests 100;

    # 버퍼 최적화
    client_body_buffer_size 128k;
    client_max_body_size 10m;
}
```

**성능 비교**:
| 지표 | Apache (mpm_prefork) | Nginx |
|------|---------------------|-------|
| 메모리 (1만 연결) | ~1GB | ~100MB |
| C10K 문제 | 어려움 | 해결 |
| 동시 연결 수 | 수백 | 수만 |

**실무 예시**:
- Netflix: Nginx로 초당 200만 요청 처리
- Cloudflare: Nginx 기반으로 전 세계 트래픽 프록시

**실무 연관**
- 대규모 트래픽 서비스에서 Nginx 선호
- 정적 파일 서빙, 리버스 프록시 모두 우수

</details>

<details>
<summary><strong>2. Blue-Green 배포 시 Nginx를 어떻게 활용하나요?</strong></summary>

**모범 답안 포인트**
- upstream에서 Blue/Green 서버 그룹 정의
- 설정 변경으로 트래픽 전환
- 무중단 배포 가능
- 롤백 시 설정 되돌리기만 하면 됨

**예시 답변**
> "Blue-Green 배포에서 Nginx는 트래픽 스위치 역할을 합니다. Blue(현재 버전)와 Green(신규 버전)을 별도 upstream으로 정의하고, proxy_pass를 Blue에서 Green으로 변경하여 트래픽을 전환합니다. Nginx reload는 무중단이므로 서비스 중단 없이 배포할 수 있고, 문제 발생 시 설정을 Blue로 되돌려 즉시 롤백할 수 있습니다."

**구현 예시**:
```nginx
# Blue (현재 운영 중)
upstream app_blue {
    server app-blue-1:8080;
    server app-blue-2:8080;
}

# Green (신규 배포)
upstream app_green {
    server app-green-1:8080;
    server app-green-2:8080;
}

server {
    listen 80;

    location / {
        # 배포 시: app_blue → app_green으로 변경
        proxy_pass http://app_blue;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**배포 프로세스**:
```bash
# 1. Green 환경 배포
docker compose up -d app-green-1 app-green-2

# 2. Green 환경 헬스체크
curl http://app-green-1:8080/health

# 3. Nginx 설정 변경 (app_blue → app_green)
# 4. 설정 검증
docker compose exec nginx nginx -t

# 5. 무중단 재시작
docker compose exec nginx nginx -s reload

# 6. Blue 환경 제거 (또는 대기)
docker compose stop app-blue-1 app-blue-2
```

**고급 기법 - Canary 배포**:
```nginx
upstream app {
    server app-blue:8080 weight=9;   # 90% 트래픽
    server app-green:8080 weight=1;  # 10% 트래픽
}

# 점진적으로 Green 비중 증가: 1 → 3 → 5 → 10
```

**실무 연관**
- Kubernetes에서도 Nginx Ingress로 동일 패턴 사용
- 대규모 서비스에서 필수 배포 전략

</details>

<details>
<summary><strong>3. Nginx 캐싱 전략과 캐시 무효화 방법을 설명하세요.</strong></summary>

**모범 답안 포인트**
- proxy_cache로 HTTP 응답 캐싱
- proxy_cache_key로 캐시 키 정의
- proxy_cache_valid로 유효 시간 설정
- proxy_cache_purge로 캐시 무효화
- stale 응답으로 장애 대응

**예시 답변**
> "Nginx 캐싱은 proxy_cache_path로 캐시 저장소를 정의하고, proxy_cache 지시어로 활성화합니다. 캐시 키는 기본적으로 URL이지만 proxy_cache_key로 커스터마이징 가능하며, POST 요청도 캐싱할 수 있습니다. proxy_cache_purge로 특정 캐시를 삭제하거나, proxy_cache_bypass로 캐시를 건너뛸 수 있습니다. 백엔드 장애 시 proxy_cache_use_stale로 오래된 캐시를 반환하여 가용성을 높입니다."

**캐싱 설정**:
```nginx
http {
    # 캐시 경로 정의
    proxy_cache_path /var/cache/nginx
        levels=1:2
        keys_zone=api_cache:10m
        max_size=1g
        inactive=60m
        use_temp_path=off;

    server {
        # 시장 가격 API (1분 캐싱)
        location /api/market/price {
            proxy_cache api_cache;
            proxy_cache_key "$request_uri";
            proxy_cache_valid 200 1m;
            proxy_cache_valid 404 10s;

            # 캐시 상태 헤더 추가
            add_header X-Cache-Status $upstream_cache_status;

            # 백엔드 장애 시 오래된 캐시 사용
            proxy_cache_use_stale error timeout updating
                                  http_500 http_502 http_503 http_504;

            # 캐시 업데이트 중에도 응답
            proxy_cache_background_update on;

            # 동시 요청 시 하나만 백엔드로
            proxy_cache_lock on;

            proxy_pass http://backend;
        }

        # POST 요청도 캐싱 (AI 분석 등)
        location /api/ai/analyze {
            proxy_cache api_cache;
            proxy_cache_key "$request_uri|$request_body";
            proxy_cache_methods GET POST;
            proxy_cache_valid 200 10m;

            proxy_pass http://ai_backend;
        }

        # 캐시 무효화 엔드포인트 (관리자만)
        location ~ /api/cache/purge(/.*) {
            allow 10.0.0.0/8;  # 내부 IP만
            deny all;

            proxy_cache_purge api_cache "$1$is_args$args";
        }
    }
}
```

**캐시 상태 값**:
- **HIT**: 캐시에서 응답
- **MISS**: 캐시 없음, 백엔드 요청
- **EXPIRED**: 캐시 만료, 갱신 필요
- **STALE**: 백엔드 장애 시 오래된 캐시 사용
- **UPDATING**: 캐시 업데이트 중
- **REVALIDATED**: 백엔드 확인 후 캐시 유효

**캐시 무효화 방법**:
```bash
# 1. 특정 URL 캐시 삭제
curl -X PURGE http://localhost/api/cache/purge/api/market/price

# 2. 전체 캐시 삭제
docker compose exec nginx sh -c "rm -rf /var/cache/nginx/*"
docker compose exec nginx nginx -s reload

# 3. 애플리케이션에서 헤더로 제어
# Cache-Control: no-cache, no-store, must-revalidate
```

**성능 비교**:
| 시나리오 | 캐싱 없음 | 캐싱 있음 |
|---------|----------|----------|
| 응답 시간 | 100ms | 1ms |
| 백엔드 부하 | 100% | 5% |
| 처리량 | 1,000 req/s | 100,000 req/s |

**실무 연관**
- CDN도 동일한 원리로 작동
- Redis와 조합하여 2단계 캐싱 전략

</details>

<details>
<summary><strong>4. Nginx의 보안 설정과 DDoS 방어 전략은?</strong></summary>

**모범 답안 포인트**
- Rate Limiting으로 요청 제한
- 보안 헤더 설정 (HSTS, CSP 등)
- IP 화이트리스트/블랙리스트
- 요청 크기 제한
- 느린 공격 (Slowloris) 방어

**예시 답변**
> "Nginx의 보안은 다층 방어 전략이 필요합니다. Rate Limiting으로 IP당 요청 수를 제한하고, 보안 헤더로 XSS, Clickjacking 등을 방어합니다. client_max_body_size로 대용량 요청을 차단하고, limit_conn으로 동시 연결 수를 제한합니다. Slowloris 같은 느린 공격은 client_body_timeout과 send_timeout으로 방어합니다. GeoIP 모듈로 국가별 차단, fail2ban으로 반복 공격 IP를 자동 차단할 수 있습니다."

**보안 설정**:
```nginx
http {
    # Rate Limiting (DDoS 방어)
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

    # 요청 크기 제한
    client_max_body_size 10M;
    client_body_buffer_size 128k;

    # 타임아웃 (Slowloris 방어)
    client_body_timeout 10s;
    client_header_timeout 10s;
    send_timeout 10s;
    keepalive_timeout 30s;

    # 숨기기
    server_tokens off;  # Nginx 버전 숨김

    server {
        listen 443 ssl http2;

        # 보안 헤더
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Content-Security-Policy "default-src 'self'" always;

        # SSL 설정
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        ssl_stapling on;
        ssl_stapling_verify on;

        # Rate Limiting 적용
        location /api/ {
            limit_req zone=general burst=20 nodelay;
            limit_conn conn_limit 10;  # IP당 10개 연결
            proxy_pass http://backend;
        }

        # 로그인 API (더 엄격)
        location /api/auth/login {
            limit_req zone=login burst=2 nodelay;
            limit_conn conn_limit 3;
            proxy_pass http://backend;
        }

        # IP 화이트리스트 (관리자 API)
        location /api/admin/ {
            allow 10.0.0.0/8;     # 내부 네트워크
            allow 192.168.1.100;  # 관리자 IP
            deny all;

            proxy_pass http://backend;
        }

        # 특정 User-Agent 차단
        if ($http_user_agent ~* (bot|crawler|spider|scraper)) {
            return 403;
        }

        # 특정 국가 차단 (GeoIP2 모듈 필요)
        # if ($geoip2_country_code ~ (CN|RU)) {
        #     return 403;
        # }
    }
}
```

**fail2ban 연동** (호스트 레벨):
```bash
# /etc/fail2ban/filter.d/nginx-limit-req.conf
[Definition]
failregex = limiting requests, excess:.* by zone.*client: <HOST>

# /etc/fail2ban/jail.local
[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 5
findtime = 60
bantime = 3600
```

**모니터링 지표**:
```nginx
# Prometheus Exporter 활용
location /nginx_status {
    stub_status on;
    access_log off;
    allow 172.0.0.0/8;
    deny all;
}
```

**실무 연관**
- CloudFlare, AWS WAF와 조합하여 다층 방어
- 로그 분석으로 공격 패턴 파악

</details>

<details>
<summary><strong>5. Nginx와 Kubernetes Ingress의 관계와 차이점은?</strong></summary>

**모범 답안 포인트**
- Kubernetes Ingress는 API 명세, 실제 구현은 다양 (Nginx, Traefik, HAProxy 등)
- Nginx Ingress Controller가 가장 널리 사용됨
- Kubernetes의 Service와 통합
- 동적 설정 업데이트 (ConfigMap, Ingress 리소스)

**예시 답변**
> "Kubernetes Ingress는 클러스터 외부에서 내부 서비스로의 HTTP/HTTPS 라우팅을 정의하는 API 리소스이고, Ingress Controller가 실제 구현체입니다. Nginx Ingress Controller는 Nginx를 기반으로 Ingress 리소스를 읽어 동적으로 Nginx 설정을 생성합니다. Docker Compose의 Nginx는 수동 설정이지만, Kubernetes는 Ingress 리소스 생성만으로 자동 설정되며, Pod 변경 시 자동으로 업데이트됩니다."

**비교**:

| 특성 | Docker Compose + Nginx | Kubernetes + Nginx Ingress |
|------|----------------------|---------------------------|
| 설정 방식 | nginx.conf 수동 작성 | Ingress YAML 작성 |
| 서비스 발견 | Docker DNS | Kubernetes Service |
| 설정 업데이트 | 수동 reload | 자동 업데이트 |
| 로드 밸런싱 | upstream 수동 정의 | Pod 자동 발견 |
| SSL 인증서 | 수동 관리 | cert-manager 자동 발급 |
| 확장성 | 수동 스케일 | HPA 자동 스케일 |

**Docker Compose Nginx**:
```nginx
upstream user_backend {
    server user-service:8081;  # 수동 정의
}

server {
    location /api/users {
        proxy_pass http://user_backend;
    }
}
```

**Kubernetes Ingress**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: lktrade-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - lktrade.com
    secretName: lktrade-tls
  rules:
  - host: lktrade.com
    http:
      paths:
      - path: /api/users
        pathType: Prefix
        backend:
          service:
            name: user-service  # Service 자동 발견
            port:
              number: 8081
```

**Nginx Ingress Controller 동작**:
```
[Ingress 리소스 생성]
       ↓
[Nginx Ingress Controller 감지]
       ↓
[Nginx 설정 자동 생성]
       ↓
[Nginx Reload]
       ↓
[트래픽 라우팅]
```

**주요 차이점**:
1. **동적 vs 정적**:
   - Docker Compose: 설정 변경 시 수동 수정 필요
   - Kubernetes: Ingress/Service 변경 시 자동 반영

2. **서비스 발견**:
   - Docker Compose: DNS 기반, 서비스명 직접 지정
   - Kubernetes: Service 리소스 통합, Pod IP 자동 추적

3. **SSL 관리**:
   - Docker Compose: 인증서 수동 발급/갱신
   - Kubernetes: cert-manager로 자동화

4. **확장성**:
   - Docker Compose: 수동 스케일, upstream 수정 필요
   - Kubernetes: HPA로 자동 스케일, Ingress는 자동 업데이트

**실무 선택 기준**:
- **Docker Compose + Nginx**: 소규모, 개발/테스트 환경, 간단한 프로덕션
- **Kubernetes + Nginx Ingress**: 대규모, 자동화, 고가용성 필요

**실무 연관**
- 대부분의 Kubernetes 클러스터에서 Nginx Ingress Controller 사용
- Helm 차트로 쉽게 설치 가능

</details>

---

## 📝 핵심 정리

### 이 장에서 배운 핵심 개념

| 개념 | 설명 | 핵심 키워드 |
|------|------|-------------|
| API Gateway | 마이크로서비스 단일 진입점 | 라우팅, 인증, Rate Limiting |
| Reverse Proxy | 클라이언트-서버 중간 프록시 | 보안, 로드 밸런싱, SSL 종료 |
| Upstream | 백엔드 서버 그룹 정의 | least_conn, keepalive, max_fails |
| Rate Limiting | 요청 수 제한 | limit_req_zone, burst, nodelay |
| SSL/TLS | 보안 통신 암호화 | 인증서, HTTPS, Let's Encrypt |
| 캐싱 | HTTP 응답 저장 | proxy_cache, 성능 향상 |
| 로드 밸런싱 | 트래픽 분산 | Round Robin, Least Conn, IP Hash |

### 필수 명령어/설정 정리

| 명령어/설정 | 용도 | 예시 |
|-------------|------|------|
| `nginx -t` | 설정 파일 검증 | `docker compose exec nginx nginx -t` |
| `nginx -s reload` | 무중단 재시작 | `docker compose exec nginx nginx -s reload` |
| `proxy_pass` | 요청 전달 | `proxy_pass http://backend;` |
| `limit_req` | Rate Limiting | `limit_req zone=api_limit burst=20 nodelay;` |
| `ssl_certificate` | SSL 인증서 | `ssl_certificate /etc/nginx/ssl/cert.crt;` |
| `proxy_cache` | 캐싱 활성화 | `proxy_cache api_cache;` |
| `upstream` | 백엔드 그룹 | `upstream backend { server app:8080; }` |

### 실무 베스트 프랙티스

#### ✅ 해야 할 것
- [ ] 프록시 헤더 설정 (X-Real-IP, X-Forwarded-For)
- [ ] Rate Limiting 적용 (DDoS 방어)
- [ ] HTTPS 사용 (HTTP는 리다이렉트)
- [ ] 로그 형식 커스터마이징 (응답 시간 포함)
- [ ] keepalive 설정 (연결 재사용)
- [ ] 설정 변경 전 nginx -t 검증
- [ ] 보안 헤더 추가 (HSTS, CSP 등)
- [ ] 캐싱 활용 (정적 응답)

#### ❌ 하지 말아야 할 것
- [ ] 프록시 헤더 없이 proxy_pass 사용
- [ ] Rate Limiting 없이 공개 API 노출
- [ ] HTTP로 민감 정보 전송
- [ ] 너무 엄격한 Rate Limiting (정상 사용자 차단)
- [ ] 설정 검증 없이 reload
- [ ] server_tokens on (버전 노출)
- [ ] 기본 타임아웃 사용 (Slowloris 취약)
- [ ] 모든 API에 동일한 설정 적용

### 성능/보안 체크리스트

#### 성능
- [ ] worker_processes auto 설정
- [ ] worker_connections 4096 이상
- [ ] keepalive 활성화 (upstream, server)
- [ ] sendfile, tcp_nopush, tcp_nodelay on
- [ ] gzip 압축 활성화
- [ ] proxy_cache 활용
- [ ] 로그 레벨 조정 (error, warn만)

#### 보안
- [ ] HTTPS 적용 (Let's Encrypt)
- [ ] Rate Limiting 설정
- [ ] 보안 헤더 추가 (7가지)
- [ ] server_tokens off (버전 숨김)
- [ ] client_max_body_size 제한
- [ ] 타임아웃 설정 (Slowloris 방어)
- [ ] 관리자 API IP 제한
- [ ] SSL 프로토콜 TLS 1.2 이상

---

## 🎉 축하합니다!

**이제 여러분은**:
✅ API Gateway의 필요성과 역할을 이해했습니다
✅ Nginx로 리버스 프록시를 구성할 수 있습니다
✅ 로드 밸런싱으로 트래픽을 분산할 수 있습니다
✅ SSL/TLS로 보안 통신을 구현할 수 있습니다
✅ Rate Limiting으로 서버를 보호할 수 있습니다
✅ 캐싱으로 성능을 극대화할 수 있습니다
✅ 실전 프로덕션 환경 설정을 마스터했습니다

**다음 단계**:
- [ ] 다음 장으로 진행 (모니터링 및 로깅)
- [ ] Nginx 설정 최적화 실습
- [ ] 면접 질문 복습

---

## 16.11 다음 단계

### 다음 장 미리보기: 섹션 17 - 모니터링 및 로깅

**배울 내용**:
- **Prometheus + Grafana**: 메트릭 수집 및 시각화
- **ELK Stack**: 중앙 로그 수집 및 분석
- **분산 추적**: Jaeger로 요청 추적
- **알림 설정**: Alertmanager로 장애 알림

### 이 장과의 연결점
```
섹션 16: Nginx 설정
    ↓
섹션 17: 모니터링/로깅 (Nginx 로그 수집, 메트릭 시각화)
    ↓
섹션 18: 프로덕션 최적화
```

### 준비하면 좋을 것들
```bash
# Prometheus와 Grafana 이미지 미리 다운로드
docker pull prom/prometheus:latest
docker pull grafana/grafana:latest
docker pull prom/node-exporter:latest
docker pull nginx/nginx-prometheus-exporter:latest
```

---

**다음 장으로 이동**: [다음: 섹션 17 - 모니터링 및 로깅 →](17-모니터링-로깅.md)

**이전 장으로 돌아가기**: [← 이전: 섹션 15](15-이전-섹션.md)

**목차로 돌아가기**: [📚 전체 목차](../README.md)