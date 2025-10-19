# 2. Redis 설치 및 환경 설정 💻

> **Redis를 처음 설치하는 분을 위한 완전 단계별 가이드**
>
> **목표:** 어떤 운영체제에서든 Redis를 성공적으로 설치하고 첫 명령어까지 실행하기

---

## 목차
- [2.1 설치 전 준비사항](#21-설치-전-준비사항)
- [2.2 Windows 설치 가이드](#22-windows-설치-가이드)
- [2.3 macOS 설치 가이드](#23-macos-설치-가이드)
- [2.4 Linux 설치 가이드](#24-linux-설치-가이드)
- [2.5 Docker로 Redis 실행하기](#25-docker로-redis-실행하기)
- [2.6 Redis 설정 파일 완전 분석](#26-redis-설정-파일-완전-분석)
- [2.7 Redis CLI 사용법 마스터](#27-redis-cli-사용법-마스터)
- [2.8 설치 확인 및 첫 번째 명령어](#28-설치-확인-및-첫-번째-명령어)
- [2.9 개발 환경별 최적화 설정](#29-개발-환경별-최적화-설정)
- [2.10 트러블슈팅 완전 가이드](#210-트러블슈팅-완전-가이드)

---

## 2.1 설치 전 준비사항

### 🎯 시스템 요구사항 완전 분석

#### 최소 시스템 요구사항
```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│   구분          │   최소 요구사항 │   권장 사항     │   고성능 환경   │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ CPU             │ 1 코어          │ 2 코어 이상     │ 4 코어 이상     │
│ 메모리 (RAM)    │ 512MB           │ 2GB 이상        │ 8GB 이상        │
│ 디스크 공간     │ 100MB           │ 1GB 이상        │ 10GB 이상       │
│ 네트워크        │ 로컬호스트      │ LAN 환경        │ 고속 네트워크   │
│ 운영체제        │ 64-bit 권장     │ 최신 안정 버전  │ 서버용 OS       │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

#### 운영체제별 지원 상황

**Windows:**
```
✅ 지원 버전:
- Windows 10 (64-bit) - 권장
- Windows 11 (64-bit) - 최신
- Windows Server 2016+ - 서버용

⚠️ 제한사항:
- Windows 7/8: 공식 지원 종료
- 32-bit 시스템: 성능 제한
- WSL 권장: 더 나은 성능과 호환성

💡 실무 팁:
- 개발용: WSL2 + Redis
- 운영용: Linux 서버 권장
- 테스트용: Docker Desktop
```

**macOS:**
```
✅ 지원 버전:
- macOS 10.14 (Mojave) 이상
- macOS 11+ (Big Sur) - 권장
- Apple Silicon (M1/M2/M3) - 완전 지원

🏆 최적 환경:
- Apple Silicon + macOS 12+
- Homebrew를 통한 설치 권장
- Docker Desktop 대안 가능

💡 개발자 팁:
- Xcode Command Line Tools 필수
- Homebrew 패키지 매니저 활용
- 포트 충돌 주의 (MySQL, PostgreSQL)
```

**Linux:**
```
✅ 완전 지원 배포판:
- Ubuntu 18.04+ (LTS 권장)
- CentOS 7+ / RHEL 7+
- Debian 9+ (Stretch)
- Fedora 최신 버전
- Amazon Linux 2
- Alpine Linux (경량)

🏆 최적 배포판:
- Ubuntu 22.04 LTS (가장 안정적)
- CentOS 8 Stream (기업용)
- Alpine (컨테이너용)

💡 운영 팁:
- 커널 3.2 이상 필수
- systemd 지원 권장
- 방화벽 설정 확인 필요
```

### 📋 설치 전 체크리스트

#### 1️⃣ **시스템 정보 확인**

**Windows에서:**
```powershell
# PowerShell에서 실행
# 시스템 정보 확인
systeminfo | findstr /C:"OS Name" /C:"OS Version" /C:"Total Physical Memory"

# 출력 예시:
OS Name:                   Microsoft Windows 11 Pro
OS Version:                10.0.22000 N/A Build 22000
Total Physical Memory:     16,384 MB

# CPU 정보 확인
wmic cpu get name

# 출력 예시:
Name
Intel(R) Core(TM) i7-10700K CPU @ 3.80GHz

# 디스크 공간 확인
dir C:\ | findstr "bytes free"
```

**macOS에서:**
```bash
# 터미널에서 실행
# 시스템 정보 확인
system_profiler SPSoftwareDataType SPHardwareDataType

# 간단한 정보
sw_vers
uname -m  # 아키텍처 확인 (arm64 = Apple Silicon)

# 메모리 정보
sysctl hw.memsize

# 디스크 공간 확인
df -h /
```

**Linux에서:**
```bash
# 배포판 확인
cat /etc/os-release
lsb_release -a  # Ubuntu/Debian

# 하드웨어 정보
lscpu              # CPU 정보
free -h            # 메모리 정보
df -h              # 디스크 정보
uname -a           # 커널 정보

# 상세 정보 (설치되어 있다면)
neofetch
htop
```

#### 2️⃣ **네트워크 환경 확인**

```bash
# 포트 사용 확인 (Redis 기본 포트 6379)
# Windows
netstat -an | findstr :6379

# macOS/Linux
netstat -an | grep :6379
lsof -i :6379  # macOS/Linux (lsof 설치된 경우)

# 방화벽 상태 확인
# Windows
netsh advfirewall show allprofiles

# macOS
sudo pfctl -s rules

# Linux (Ubuntu)
sudo ufw status
sudo iptables -L
```

#### 3️⃣ **개발 도구 확인**

**필수 도구:**
```bash
# 컴파일러 확인 (소스 컴파일 시 필요)
gcc --version
clang --version  # macOS

# 패키지 매니저 확인
# Windows
choco --version      # Chocolatey
winget --version     # Windows Package Manager

# macOS
brew --version       # Homebrew

# Linux
apt --version        # Ubuntu/Debian
yum --version        # CentOS/RHEL
dnf --version        # Fedora
```

**선택 도구:**
```bash
# Git (소스 빌드 시)
git --version

# wget/curl (다운로드용)
wget --version
curl --version

# Docker (컨테이너 사용 시)
docker --version
docker-compose --version
```

### 🎯 설치 방법 선택 가이드

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│   설치 방법     │   난이도        │   권장 대상     │   장점/단점     │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ 패키지 매니저   │ 쉬움 ⭐⭐⭐     │ 일반 사용자     │ ✅간편 ❌버전제한│
│ 소스 컴파일     │ 어려움 ⭐       │ 고급 사용자     │ ✅최신 ❌복잡함 │
│ 바이너리 다운   │ 중간 ⭐⭐       │ 개발자         │ ✅빠름 ❌수동관리│
│ Docker          │ 중간 ⭐⭐       │ 개발자/운영자   │ ✅격리 ❌오버헤드│
│ 클라우드 서비스 │ 매우쉬움 ⭐⭐⭐⭐│ 운영 환경       │ ✅관리형 ❌비용 │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

**상황별 권장 방법:**
```
🏠 개인 학습용:
1순위: Docker (격리되고 깔끔)
2순위: 패키지 매니저 (간편)

🏢 개발 환경:
1순위: Docker Compose (팀 협업)
2순위: 로컬 설치 + 설정파일 공유

🏭 운영 환경:
1순위: 클라우드 관리형 서비스
2순위: 소스 컴파일 (성능 최적화)
```

---

## 2.2 Windows 설치 가이드

### 🪟 방법 1: WSL2 + Ubuntu (권장)

#### Step 1: WSL2 설치 및 설정

**WSL2 설치:**
```powershell
# PowerShell을 관리자 권한으로 실행
# Windows 키 + X → Windows PowerShell (관리자)

# WSL 기능 활성화
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 가상머신 플랫폼 활성화
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 재부팅 후 WSL2를 기본 버전으로 설정
wsl --set-default-version 2

# Ubuntu 설치
wsl --install -d Ubuntu-22.04

# 설치 확인
wsl --list --verbose
```

**출력 예시:**
```
  NAME            STATE           VERSION
* Ubuntu-22.04    Running         2
  docker-desktop  Stopped         2
```

#### Step 2: Ubuntu에서 Redis 설치

**Ubuntu 업데이트:**
```bash
# WSL Ubuntu 터미널에서 실행
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y curl wget gpg lsb-release software-properties-common
```

**Redis 공식 저장소 추가:**
```bash
# Redis GPG 키 추가
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg

# Redis 저장소 추가
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

# 패키지 목록 업데이트
sudo apt update

# Redis 설치
sudo apt install -y redis

# 설치 확인
redis-server --version
```

**출력 예시:**
```bash
Redis server v=7.2.3 sha=00000000:0 malloc=jemalloc-5.3.0 bits=64 build=c6e4d3e0ccd5
```

#### Step 3: Redis 서비스 설정

**서비스 시작:**
```bash
# Redis 서비스 시작
sudo systemctl start redis-server

# 부팅 시 자동 시작 설정
sudo systemctl enable redis-server

# 서비스 상태 확인
sudo systemctl status redis-server
```

**출력 예시:**
```bash
● redis-server.service - Advanced key-value store
     Loaded: loaded (/lib/systemd/system/redis-server.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2024-01-15 10:00:00 KST; 2min 3s ago
       Docs: http://redis.io/documentation,
             man:redis-server(1)
   Main PID: 1234 (redis-server)
     Status: "Ready to accept connections"
      Tasks: 5 (limit: 9485)
     Memory: 7.3M
        CPU: 123ms
     CGroup: /system.slice/redis-server.service
             └─1234 /usr/bin/redis-server 127.0.0.1:6379
```

### 🪟 방법 2: Native Windows (Redis for Windows)

#### Step 1: Redis for Windows 다운로드

**⚠️ 주의사항:**
```
Redis for Windows는 Microsoft에서 유지보수하는 포트 버전입니다.
- 최신 Redis 기능이 지연될 수 있음
- 성능이 Linux 버전보다 낮을 수 있음
- 학습용으로는 충분, 운영용으로는 권장하지 않음
```

**다운로드 및 설치:**
```powershell
# GitHub 릴리스 페이지에서 다운로드
# https://github.com/microsoftarchive/redis/releases

# PowerShell에서 직접 다운로드 (예시)
$url = "https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip"
$output = "$env:USERPROFILE\Downloads\Redis-x64-3.0.504.zip"
Invoke-WebRequest -Uri $url -OutFile $output

# 압축 해제
Expand-Archive -Path $output -DestinationPath "$env:USERPROFILE\Redis"

# 디렉토리 이동
cd "$env:USERPROFILE\Redis"
```

#### Step 2: Windows 서비스로 등록

**서비스 설치:**
```powershell
# Redis 디렉토리에서 실행
# 관리자 권한 PowerShell 필요

# 서비스 설치
.\redis-server.exe --service-install redis.windows.conf --service-name Redis

# 서비스 시작
.\redis-server.exe --service-start

# 서비스 상태 확인
Get-Service -Name Redis
```

**출력 예시:**
```powershell
Status   Name               DisplayName
------   ----               -----------
Running  Redis              Redis
```

### 🪟 방법 3: Chocolatey 패키지 매니저

#### Step 1: Chocolatey 설치

```powershell
# PowerShell 관리자 권한으로 실행
Set-ExecutionPolicy Bypass -Scope Process -Force

# Chocolatey 설치
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 설치 확인
choco --version
```

#### Step 2: Redis 설치

```powershell
# Redis 설치
choco install redis-64 -y

# 설치 확인
redis-server --version

# 서비스 시작
net start redis
```

### 🪟 Windows 환경 최적화 설정

#### 메모리 설정

**Windows 메모리 관리 최적화:**
```powershell
# 가상 메모리 설정 확인
Get-WmiObject -Class Win32_PageFileUsage

# Redis 전용 메모리 설정 (redis.conf 수정)
# maxmemory 2gb
# maxmemory-policy allkeys-lru
```

#### 네트워크 설정

**방화벽 규칙 추가:**
```powershell
# Windows Defender 방화벽에 Redis 포트 허용
netsh advfirewall firewall add rule name="Redis Server" dir=in action=allow protocol=TCP localport=6379

# 규칙 확인
netsh advfirewall firewall show rule name="Redis Server"
```

**포트 사용 확인:**
```powershell
# 6379 포트 사용 상황 확인
netstat -an | findstr :6379

# 출력 예시:
TCP    127.0.0.1:6379         0.0.0.0:0              LISTENING
```

---

## 2.3 macOS 설치 가이드

### 🍎 방법 1: Homebrew (권장)

#### Step 1: Homebrew 설치

**Homebrew가 없는 경우:**
```bash
# Xcode Command Line Tools 설치
xcode-select --install

# Homebrew 설치
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# PATH 추가 (Apple Silicon Mac)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# PATH 추가 (Intel Mac)
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"

# 설치 확인
brew --version
```

#### Step 2: Redis 설치

**기본 설치:**
```bash
# Redis 설치
brew install redis

# 설치 확인
redis-server --version

# 출력 예시:
Redis server v=7.2.3 sha=00000000:0 malloc=libc bits=64 build=1234567890
```

**자세한 설치 정보:**
```bash
# 설치된 패키지 정보 확인
brew info redis

# 출력 예시:
==> redis: stable 7.2.3 (bottled), HEAD
Persistent key-value database, with built-in net interface
https://redis.io/
/opt/homebrew/Cellar/redis/7.2.3 (14 files, 2.9MB) *
  Poured from bottle using the formulae.brew.sh API on 2024-01-15 at 10:00:00
From: https://github.com/Homebrew/homebrew-core/blob/HEAD/Formula/r/redis.rb
License: BSD-3-Clause
==> Dependencies
Build: pkg-config ✓
==> Options
--HEAD
	Install HEAD version
==> Caveats
To start redis now and restart at login:
  brew services start redis
Or, if you don't want/need a background service you can just run:
  redis-server /opt/homebrew/etc/redis.conf
```

#### Step 3: Redis 서비스 관리

**서비스로 시작 (권장):**
```bash
# 서비스 시작 (백그라운드 실행)
brew services start redis

# 서비스 상태 확인
brew services list | grep redis

# 출력 예시:
redis            started          user     ~/Library/LaunchAgents/homebrew.mxcl.redis.plist

# 서비스 중지
brew services stop redis

# 서비스 재시작
brew services restart redis
```

**수동으로 시작:**
```bash
# 포그라운드에서 실행 (디버깅용)
redis-server /opt/homebrew/etc/redis.conf

# 설정 파일 없이 기본값으로 실행
redis-server

# 특정 포트로 실행
redis-server --port 6380
```

### 🍎 방법 2: 소스 컴파일

#### Step 1: 빌드 도구 설치

```bash
# Xcode Command Line Tools (이미 설치되어 있다면 건너뛰기)
xcode-select --install

# 필요한 도구들
brew install wget make gcc
```

#### Step 2: Redis 소스 다운로드 및 컴파일

```bash
# 작업 디렉토리 생성
mkdir -p ~/redis-build && cd ~/redis-build

# 최신 안정 버전 다운로드 (7.2.3 예시)
wget https://download.redis.io/releases/redis-7.2.3.tar.gz

# 압축 해제
tar xzf redis-7.2.3.tar.gz
cd redis-7.2.3

# 컴파일 (Apple Silicon에 최적화)
make BUILD_TLS=yes

# 설치 (선택사항)
sudo make install

# 컴파일 확인
./src/redis-server --version
```

**Apple Silicon 최적화 빌드:**
```bash
# M1/M2/M3 Mac 전용 최적화
export CFLAGS="-arch arm64 -O3"
export CXXFLAGS="-arch arm64 -O3"
make BUILD_TLS=yes
```

### 🍎 macOS 환경 최적화

#### 시스템 설정 최적화

**파일 디스크립터 제한 증가:**
```bash
# 현재 제한 확인
ulimit -n

# 세션별 제한 증가
ulimit -n 65536

# 영구 설정 (~/.zshrc 또는 ~/.bash_profile에 추가)
echo 'ulimit -n 65536' >> ~/.zshrc

# 시스템 전체 제한 확인
sudo launchctl limit maxfiles
```

**메모리 설정:**
```bash
# 시스템 메모리 정보
sysctl hw.memsize
vm_stat

# Redis 설정 파일 수정
sudo nano /opt/homebrew/etc/redis.conf

# 추가할 설정:
# maxmemory 2gb
# maxmemory-policy allkeys-lru
```

#### 네트워크 설정

**방화벽 설정:**
```bash
# 방화벽 상태 확인
sudo pfctl -s rules

# 개발용 설정 (주의: 보안 위험)
# 시스템 환경설정 → 보안 및 개인 정보 보호 → 방화벽 → 방화벽 옵션
# Redis 앱에 대한 연결 허용
```

**포트 확인:**
```bash
# Redis 포트 사용 확인
lsof -i :6379

# 출력 예시:
COMMAND    PID USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
redis-ser 1234 user   6u  IPv4 0x1234567890      0t0  TCP localhost:6379 (LISTEN)
```

---

## 2.4 Linux 설치 가이드

### 🐧 Ubuntu/Debian 설치

#### 방법 1: APT 패키지 매니저 (권장)

**Step 1: 시스템 업데이트**
```bash
# 패키지 목록 업데이트
sudo apt update

# 시스템 업그레이드 (선택사항)
sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y curl wget gpg lsb-release software-properties-common
```

**Step 2: Redis 공식 저장소 추가**
```bash
# Redis 공식 GPG 키 다운로드 및 추가
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg

# 저장소 추가
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

# 패키지 목록 업데이트
sudo apt update

# 사용 가능한 Redis 버전 확인
apt-cache policy redis

# 출력 예시:
redis:
  Installed: (none)
  Candidate: 6:7.2.3-1rl1~jammy1
  Version table:
     6:7.2.3-1rl1~jammy1 500
        500 https://packages.redis.io/deb jammy/main amd64 Packages
```

**Step 3: Redis 설치**
```bash
# Redis 서버와 CLI 설치
sudo apt install -y redis

# 설치 확인
redis-server --version
redis-cli --version

# 출력 예시:
Redis server v=7.2.3 sha=00000000:0 malloc=jemalloc-5.3.0 bits=64 build=c6e4d3e0
redis-cli 7.2.3
```

#### 방법 2: 소스 컴파일 (성능 최적화)

**Step 1: 빌드 환경 준비**
```bash
# 빌드 도구 설치
sudo apt update
sudo apt install -y build-essential tcl wget

# GCC 버전 확인 (9.0 이상 권장)
gcc --version

# 메모리 할당자 라이브러리 설치 (선택사항, 성능 향상)
sudo apt install -y libjemalloc-dev

# SSL/TLS 지원을 위한 라이브러리 (선택사항)
sudo apt install -y libssl-dev
```

**Step 2: Redis 소스 다운로드**
```bash
# 작업 디렉토리 생성
mkdir -p ~/redis-src && cd ~/redis-src

# 최신 안정 버전 다운로드
REDIS_VERSION="7.2.3"
wget https://download.redis.io/releases/redis-${REDIS_VERSION}.tar.gz

# 체크섬 확인 (보안)
wget https://download.redis.io/releases/redis-${REDIS_VERSION}.tar.gz.SHA256SUM
sha256sum -c redis-${REDIS_VERSION}.tar.gz.SHA256SUM

# 압축 해제
tar xzf redis-${REDIS_VERSION}.tar.gz
cd redis-${REDIS_VERSION}
```

**Step 3: 컴파일 및 설치**
```bash
# 기본 컴파일
make

# TLS 지원 포함 컴파일 (권장)
make BUILD_TLS=yes

# 테스트 실행 (선택사항, 시간 소요)
make test

# 설치
sudo make install

# 설치 확인
which redis-server
redis-server --version
```

**컴파일 최적화 옵션:**
```bash
# 성능 최적화 컴파일
make MALLOC=jemalloc BUILD_TLS=yes CFLAGS="-O3 -march=native"

# 디버그 정보 포함 (개발용)
make DEBUG=1

# 정적 링크 (독립 실행 파일)
make MALLOC=libc
```

#### 방법 3: Snap 패키지

**Snap을 통한 설치:**
```bash
# Snap 설치 (Ubuntu 16.04+에는 기본 설치됨)
sudo apt install snapd

# Redis 설치
sudo snap install redis

# 설치 확인
redis.server --version
redis.cli --version

# Snap 서비스 관리
sudo snap start redis
sudo snap stop redis
sudo snap restart redis
```

### 🐧 CentOS/RHEL/Fedora 설치

#### RHEL 계열 시스템

**CentOS 8 / RHEL 8:**
```bash
# EPEL 저장소 활성화
sudo dnf install -y epel-release

# Redis 설치
sudo dnf install -y redis

# 설치 확인
redis-server --version
```

**CentOS 7 / RHEL 7:**
```bash
# EPEL 저장소 활성화
sudo yum install -y epel-release

# Redis 설치
sudo yum install -y redis

# 설치 확인
redis-server --version
```

**Fedora:**
```bash
# Redis 설치 (최신 버전)
sudo dnf install -y redis

# 설치 확인
redis-server --version
```

### 🐧 Linux 서비스 설정

#### systemd 서비스 관리

**서비스 시작:**
```bash
# Redis 서비스 시작
sudo systemctl start redis

# 부팅 시 자동 시작 설정
sudo systemctl enable redis

# 서비스 상태 확인
sudo systemctl status redis

# 상세 로그 확인
sudo journalctl -u redis -f
```

**서비스 설정 파일 확인:**
```bash
# systemd 서비스 파일 위치
cat /etc/systemd/system/redis.service
# 또는
cat /lib/systemd/system/redis-server.service

# 예시 내용:
[Unit]
Description=Advanced key-value store
After=network.target
Documentation=http://redis.io/documentation, man:redis-server(1)

[Service]
Type=notify
ExecStart=/usr/bin/redis-server /etc/redis/redis.conf
ExecStop=/bin/kill -s QUIT $MAINPID
TimeoutStopSec=0
Restart=always
User=redis
Group=redis
RuntimeDirectory=redis
RuntimeDirectoryMode=0755

[Install]
WantedBy=multi-user.target
```

#### 사용자 및 권한 설정

**Redis 전용 사용자:**
```bash
# Redis 사용자 확인
id redis

# 사용자가 없는 경우 생성
sudo useradd -r -s /bin/false redis

# Redis 디렉토리 권한 설정
sudo mkdir -p /var/lib/redis /var/log/redis
sudo chown redis:redis /var/lib/redis /var/log/redis
sudo chmod 755 /var/lib/redis /var/log/redis
```

### 🐧 Linux 보안 설정

#### 방화벽 설정

**UFW (Ubuntu):**
```bash
# UFW 상태 확인
sudo ufw status

# Redis 포트 허용 (로컬만)
sudo ufw allow from 127.0.0.1 to any port 6379

# 특정 네트워크에서만 허용
sudo ufw allow from 192.168.1.0/24 to any port 6379

# 설정 확인
sudo ufw status numbered
```

**firewalld (CentOS/RHEL):**
```bash
# firewalld 상태 확인
sudo firewall-cmd --state

# Redis 포트 허용 (영구)
sudo firewall-cmd --permanent --add-port=6379/tcp

# 특정 소스에서만 허용
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" port protocol="tcp" port="6379" accept'

# 설정 적용
sudo firewall-cmd --reload

# 설정 확인
sudo firewall-cmd --list-all
```

#### SELinux 설정 (CentOS/RHEL)

```bash
# SELinux 상태 확인
sestatus

# Redis SELinux 정책 설치
sudo yum install -y policycoreutils-python-utils

# Redis 포트 허용
sudo semanage port -a -t redis_port_t -p tcp 6379

# 설정 확인
sudo semanage port -l | grep redis
```

---

## 2.5 Docker로 Redis 실행하기

### 🐳 방법 1: 단일 컨테이너 실행

#### 기본 실행

**가장 간단한 방법:**
```bash
# Docker가 설치되어 있는지 확인
docker --version

# Redis 컨테이너 실행
docker run --name my-redis -d -p 6379:6379 redis:7.2.3

# 실행 확인
docker ps

# 출력 예시:
CONTAINER ID   IMAGE         COMMAND                  CREATED         STATUS         PORTS                    NAMES
abc123def456   redis:7.2.3   "docker-entrypoint.s…"   10 seconds ago   Up 9 seconds   0.0.0.0:6379->6379/tcp   my-redis
```

**명령어 분석:**
```bash
docker run \
  --name my-redis \      # 컨테이너 이름 지정
  -d \                   # 백그라운드 실행 (detached)
  -p 6379:6379 \        # 포트 매핑 (호스트:컨테이너)
  redis:7.2.3           # 사용할 이미지와 태그
```

#### 고급 실행 옵션

**메모리 제한과 재시작 정책:**
```bash
docker run \
  --name redis-prod \
  -d \
  -p 6379:6379 \
  --restart unless-stopped \    # 재시작 정책
  --memory="2g" \               # 메모리 제한
  --memory-swap="4g" \          # 스왑 제한
  -v redis-data:/data \         # 데이터 볼륨
  redis:7.2.3 \
  redis-server --appendonly yes # AOF 영속성 활성화
```

**환경 변수와 설정:**
```bash
docker run \
  --name redis-configured \
  -d \
  -p 6379:6379 \
  -e REDIS_PASSWORD=mypassword \     # 패스워드 설정
  -v ./redis.conf:/usr/local/etc/redis/redis.conf \  # 설정 파일 마운트
  redis:7.2.3 \
  redis-server /usr/local/etc/redis/redis.conf
```

#### Redis CLI 접속

**Docker 컨테이너 내부 CLI:**
```bash
# 컨테이너 내부 접속
docker exec -it my-redis redis-cli

# 직접 명령어 실행
docker exec my-redis redis-cli ping

# 출력: PONG

# 호스트에서 연결 (redis-cli가 설치된 경우)
redis-cli -h localhost -p 6379
```

### 🐳 방법 2: Docker Compose (권장)

#### Docker Compose 파일 작성

**기본 docker-compose.yml:**
```yaml
version: '3.8'

services:
  redis:
    image: redis:7.2.3-alpine  # Alpine 버전 (경량)
    container_name: redis-server
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
      - ./redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    environment:
      - REDIS_REPLICATION_MODE=master
    networks:
      - redis-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

volumes:
  redis-data:
    driver: local

networks:
  redis-network:
    driver: bridge
```

**실행 및 관리:**
```bash
# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f redis

# 서비스 상태 확인
docker-compose ps

# 서비스 중지
docker-compose down

# 볼륨까지 삭제
docker-compose down -v
```

#### 개발용 완전한 설정

**docker-compose.dev.yml:**
```yaml
version: '3.8'

services:
  redis:
    image: redis:7.2.3-alpine
    container_name: redis-dev
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
      - ./config/redis.conf:/usr/local/etc/redis/redis.conf
      - ./logs:/var/log/redis
    command: redis-server /usr/local/etc/redis/redis.conf
    environment:
      - REDIS_PASSWORD=${REDIS_PASSWORD:-devpassword}
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  redis-commander:  # Redis 웹 UI
    image: rediscommander/redis-commander:latest
    container_name: redis-ui
    restart: unless-stopped
    ports:
      - "8081:8081"
    environment:
      - REDIS_HOSTS=local:redis:6379
      - REDIS_PASSWORD=${REDIS_PASSWORD:-devpassword}
    depends_on:
      - redis
    networks:
      - app-network

  redis-insight:    # RedisLabs 공식 GUI
    image: redislabs/redisinsight:latest
    container_name: redis-insight
    restart: unless-stopped
    ports:
      - "8001:8001"
    volumes:
      - redis-insight-data:/db
    depends_on:
      - redis
    networks:
      - app-network

volumes:
  redis-data:
  redis-insight-data:

networks:
  app-network:
    driver: bridge
```

**.env 파일:**
```env
# Redis 설정
REDIS_PASSWORD=your-secure-password
REDIS_PORT=6379

# UI 설정
REDIS_COMMANDER_PORT=8081
REDIS_INSIGHT_PORT=8001
```

### 🐳 클러스터 구성 (고급)

#### Redis 클러스터 Docker Compose

**docker-compose.cluster.yml:**
```yaml
version: '3.8'

services:
  redis-node1:
    image: redis:7.2.3-alpine
    container_name: redis-node1
    ports:
      - "7001:7001"
      - "17001:17001"
    volumes:
      - ./cluster-config/node1.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    networks:
      redis-cluster:
        ipv4_address: 172.20.0.11

  redis-node2:
    image: redis:7.2.3-alpine
    container_name: redis-node2
    ports:
      - "7002:7002"
      - "17002:17002"
    volumes:
      - ./cluster-config/node2.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    networks:
      redis-cluster:
        ipv4_address: 172.20.0.12

  redis-node3:
    image: redis:7.2.3-alpine
    container_name: redis-node3
    ports:
      - "7003:7003"
      - "17003:17003"
    volumes:
      - ./cluster-config/node3.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    networks:
      redis-cluster:
        ipv4_address: 172.20.0.13

networks:
  redis-cluster:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

**클러스터 노드 설정 파일 (node1.conf 예시):**
```conf
port 7001
cluster-enabled yes
cluster-config-file nodes-7001.conf
cluster-node-timeout 15000
appendonly yes
bind 0.0.0.0
protected-mode no
```

---

## 2.6 Redis 설정 파일 완전 분석

### 📁 설정 파일 위치

**운영체제별 기본 위치:**
```
Windows (Native):
C:\Program Files\Redis\redis.windows.conf

Windows (WSL2):
/etc/redis/redis.conf

macOS (Homebrew):
/opt/homebrew/etc/redis.conf
/usr/local/etc/redis.conf (Intel Mac)

Linux (Package):
/etc/redis/redis.conf
/etc/redis/6379.conf

소스 컴파일:
./redis.conf (소스 디렉토리)
/usr/local/etc/redis.conf (설치 후)

Docker:
/usr/local/etc/redis/redis.conf (컨테이너 내부)
```

### 📝 기본 설정 파일 생성

**기본 설정 파일 복사:**
```bash
# Linux/macOS
sudo cp /etc/redis/redis.conf /etc/redis/redis.conf.backup
sudo nano /etc/redis/redis.conf

# Docker에서 설정 파일 추출
docker run --rm redis:7.2.3 cat /usr/local/etc/redis/redis.conf > ./redis.conf
```

### ⚙️ 핵심 설정 항목 완전 분석

#### 1️⃣ **네트워크 설정**

**bind 설정 (보안 중요):**
```conf
# 기본값 (로컬호스트만 접근 허용)
bind 127.0.0.1

# 모든 인터페이스에서 접근 허용 (위험!)
bind 0.0.0.0

# 특정 IP에서만 접근 허용
bind 127.0.0.1 192.168.1.100

# IPv6 포함
bind 127.0.0.1 ::1

# 실무 권장 설정 (개발용)
bind 127.0.0.1 192.168.1.0/24

# 실무 권장 설정 (운영용)
bind 127.0.0.1  # 또는 내부 네트워크 IP만
```

**포트 설정:**
```conf
# 기본 포트
port 6379

# 커스텀 포트 (보안상 권장)
port 16379

# 포트 비활성화 (Unix 소켓만 사용)
port 0
unixsocket /var/run/redis/redis.sock
unixsocketperm 700
```

**보호 모드:**
```conf
# 보호 모드 (기본값: yes)
protected-mode yes

# 보호 모드 해제 (개발용만)
protected-mode no
```

#### 2️⃣ **메모리 관리 설정**

**최대 메모리 설정:**
```conf
# 메모리 제한 없음 (기본값)
# maxmemory <bytes>

# 실무 예시 (시스템 메모리의 75%)
maxmemory 6gb
maxmemory 1073741824  # 1GB in bytes

# 메모리 부족 시 정책
maxmemory-policy allkeys-lru

# 사용 가능한 정책들:
# noeviction: 메모리 부족 시 오류 반환
# allkeys-lru: 모든 키 중 LRU 알고리즘으로 제거
# volatile-lru: TTL 설정된 키 중 LRU로 제거
# allkeys-random: 모든 키 중 랜덤 제거
# volatile-random: TTL 설정된 키 중 랜덤 제거
# volatile-ttl: TTL이 짧은 키부터 제거
# allkeys-lfu: 모든 키 중 LFU 알고리즘으로 제거
# volatile-lfu: TTL 설정된 키 중 LFU로 제거
```

**메모리 최적화:**
```conf
# 해시 테이블 최적화
hash-max-ziplist-entries 512
hash-max-ziplist-value 64

# 리스트 최적화
list-max-ziplist-size -2
list-compress-depth 0

# 집합 최적화
set-max-intset-entries 512

# 정렬된 집합 최적화
zset-max-ziplist-entries 128
zset-max-ziplist-value 64

# HyperLogLog 최적화
hll-sparse-max-bytes 3000
```

#### 3️⃣ **영속성 설정**

**RDB 스냅샷:**
```conf
# 자동 스냅샷 조건 (기본값)
save 900 1      # 900초 동안 1개 이상 변경 시
save 300 10     # 300초 동안 10개 이상 변경 시
save 60 10000   # 60초 동안 10000개 이상 변경 시

# 스냅샷 비활성화
save ""

# 수동 스냅샷만 사용
save 3600 1     # 1시간마다 한 번

# 스냅샷 파일 이름
dbfilename dump.rdb

# 스냅샷 저장 경로
dir /var/lib/redis

# 압축 사용 (CPU vs 디스크 공간)
rdbcompression yes

# 체크섬 사용 (무결성 vs 성능)
rdbchecksum yes
```

**AOF (Append Only File):**
```conf
# AOF 활성화
appendonly yes

# AOF 파일 이름
appendfilename "appendonly.aof"

# 동기화 정책
appendfsync everysec  # 권장값

# 사용 가능한 옵션:
# always: 모든 쓰기마다 동기화 (가장 안전, 가장 느림)
# everysec: 1초마다 동기화 (균형)
# no: OS에 맡김 (가장 빠름, 위험)

# AOF 재작성 최적화
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# AOF 로딩 시 에러 처리
aof-load-truncated yes
```

#### 4️⃣ **보안 설정**

**인증:**
```conf
# 패스워드 설정
requirepass your-secure-password-here

# 사용자별 권한 (Redis 6.0+)
user default on >your-secure-password ~* &* -@dangerous
user readonly on >readonly-password ~* &* +@read -@write -@dangerous
user admin on >admin-password ~* &* +@all
```

**위험한 명령어 비활성화:**
```conf
# 명령어 이름 변경
rename-command FLUSHDB "DELETE_ALL_KEYS_ABC123"
rename-command FLUSHALL "DELETE_EVERYTHING_XYZ789"
rename-command CONFIG ""  # 완전 비활성화
rename-command DEBUG ""
rename-command SHUTDOWN SHUTDOWN_ABC123
```

#### 5️⃣ **로깅 설정**

**로그 레벨과 파일:**
```conf
# 로그 레벨
loglevel notice

# 사용 가능한 레벨:
# debug: 매우 상세한 정보
# verbose: 많은 정보
# notice: 중요한 정보 (기본값)
# warning: 경고만

# 로그 파일 경로
logfile /var/log/redis/redis-server.log

# 표준 출력으로 로그 (로그 파일과 동시 사용 가능)
# logfile ""

# Syslog 사용
syslog-enabled yes
syslog-ident redis
syslog-facility local0
```

#### 6️⃣ **클라이언트 연결 설정**

**연결 제한:**
```conf
# 최대 클라이언트 연결 수
maxclients 10000

# 클라이언트 타임아웃 (초, 0 = 무제한)
timeout 300

# TCP keepalive
tcp-keepalive 300

# TCP backlog
tcp-backlog 511
```

**네트워크 최적화:**
```conf
# Nagle 알고리즘 비활성화
tcp-nodelay yes

# SO_REUSEPORT 사용 (Linux 3.9+)
tcp-reuseport yes
```

### 📋 환경별 권장 설정

#### 개발 환경 설정

**development.conf:**
```conf
# 개발용 Redis 설정
port 6379
bind 127.0.0.1

# 보안 (개발용)
protected-mode yes
requirepass devpassword

# 메모리 (개발 머신)
maxmemory 1gb
maxmemory-policy allkeys-lru

# 영속성 (빠른 재시작)
save 900 1
appendonly no

# 로깅 (디버깅용)
loglevel verbose
logfile /var/log/redis/redis-dev.log

# 클라이언트
maxclients 100
timeout 0
```

#### 테스트 환경 설정

**testing.conf:**
```conf
# 테스트용 Redis 설정
port 6379
bind 127.0.0.1

# 보안
protected-mode yes
requirepass testpassword

# 메모리 (테스트 서버)
maxmemory 2gb
maxmemory-policy allkeys-lru

# 영속성 (데이터 유실 방지)
save 300 10
save 60 10000
appendonly yes
appendfsync everysec

# 로깅
loglevel notice
logfile /var/log/redis/redis-test.log

# 성능
tcp-keepalive 60
maxclients 1000
```

#### 운영 환경 설정

**production.conf:**
```conf
# 운영용 Redis 설정
port 16379  # 보안을 위한 비표준 포트
bind 10.0.1.100  # 내부 IP만

# 보안 강화
protected-mode yes
requirepass very-secure-production-password

# 위험 명령어 비활성화
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command CONFIG "CONFIG_b840fc02d524045429941cc15f59e41cb7be6c52"
rename-command DEBUG ""

# 메모리 (운영 서버)
maxmemory 8gb
maxmemory-policy allkeys-lru

# 영속성 (데이터 안전성 최우선)
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# 로깅
loglevel notice
logfile /var/log/redis/redis-prod.log
syslog-enabled yes

# 성능 최적화
tcp-keepalive 300
maxclients 10000
tcp-backlog 511
tcp-nodelay yes

# 슬로우 로그
slowlog-log-slower-than 10000  # 10ms 이상
slowlog-max-len 128
```

---

## 2.7 Redis CLI 사용법 마스터

### 🖥️ Redis CLI 기본 사용법

#### 연결 방법

**로컬 연결:**
```bash
# 기본 연결 (localhost:6379)
redis-cli

# 특정 호스트와 포트
redis-cli -h localhost -p 6379

# 패스워드 인증
redis-cli -a yourpassword

# 데이터베이스 번호 지정
redis-cli -n 1

# 모든 옵션 조합
redis-cli -h redis.example.com -p 6380 -a password -n 2
```

**원격 연결:**
```bash
# 원격 서버 연결
redis-cli -h 192.168.1.100 -p 6379 -a password

# URI 방식 연결
redis-cli --uri redis://username:password@hostname:port/database

# TLS 연결 (Redis 6.0+)
redis-cli --tls --cert client.crt --key client.key --cacert ca.crt
```

#### 대화형 모드

**기본 사용:**
```bash
# Redis CLI 시작
$ redis-cli
127.0.0.1:6379>

# 인증 (연결 후)
127.0.0.1:6379> AUTH yourpassword
OK

# 데이터베이스 선택
127.0.0.1:6379> SELECT 1
OK
127.0.0.1:6379[1]>

# 연결 테스트
127.0.0.1:6379> PING
PONG

# 종료
127.0.0.1:6379> EXIT
```

**도움말:**
```bash
# 명령어 도움말
127.0.0.1:6379> HELP SET
SET key value [expiration EX seconds|PX milliseconds] [NX|XX]

# 전체 명령어 목록
127.0.0.1:6379> HELP @string
127.0.0.1:6379> HELP @list
127.0.0.1:6379> HELP @set
```

#### 명령행 모드

**단일 명령 실행:**
```bash
# 하나의 명령만 실행
redis-cli SET mykey "Hello World"

# 여러 명령을 파이프로 연결
echo "SET key1 value1" | redis-cli
echo -e "SET key1 value1\nGET key1" | redis-cli

# 파일에서 명령 실행
redis-cli < commands.txt
```

### 🔧 CLI 고급 기능

#### 자동 완성과 히스토리

**자동 완성:**
```bash
# Tab 키로 명령어 자동 완성
127.0.0.1:6379> S[TAB]
SADD     SCARD    SDIFF    SINTER   ...

# 키 이름 자동 완성
127.0.0.1:6379> GET my[TAB]
mykey1   mykey2   mykey3
```

**명령 히스토리:**
```bash
# 히스토리 파일 위치: ~/.rediscli_history

# 이전 명령 탐색: ↑ ↓ 화살표 키
# 히스토리 검색: Ctrl+R

# 히스토리 지우기
127.0.0.1:6379> FLUSHALL
```

#### 출력 형식 제어

**원시 출력 모드:**
```bash
# 원시 출력 (프로그래밍용)
redis-cli --raw GET mykey

# CSV 출력
redis-cli --csv LRANGE mylist 0 -1

# JSON 출력 (키-값 쌍)
redis-cli --json GET mykey
```

**출력 구분자 설정:**
```bash
# 커스텀 구분자
redis-cli -d '\n' MGET key1 key2 key3
```

#### 반복 실행

**명령 반복:**
```bash
# 5번 반복
redis-cli -r 5 PING

# 무한 반복 (Ctrl+C로 중단)
redis-cli -r -1 PING

# 간격 설정 (1초마다)
redis-cli -r -1 -i 1 INFO memory
```

**실시간 모니터링:**
```bash
# 실시간 명령 모니터링
redis-cli MONITOR

# 실시간 로그 (Redis 6.0+)
redis-cli CLIENT TRACKING on

# 특정 키 모니터링
redis-cli --scan --pattern user:*
```

### 📊 모니터링과 디버깅

#### 성능 모니터링

**연결 대기시간 측정:**
```bash
# 100번 ping으로 평균 지연 시간 측정
redis-cli --latency -i 1

# 지연 시간 히스토리
redis-cli --latency-history -i 1

# 지연 시간 분포
redis-cli --latency-dist -i 1
```

**메모리 사용량 분석:**
```bash
# 메모리 사용량 요약
redis-cli INFO memory

# 키별 메모리 사용량 (Redis 4.0+)
redis-cli --memkeys

# 메모리 사용량 상위 키들
redis-cli --memkeys-samples 1000
```

**실시간 통계:**
```bash
# 실시간 통계 표시
redis-cli --stat

# 출력 예시:
------- data ------ --------------------- load -------------------- - child -
keys       mem      clients blocked requests            connections
502        1.41M    1       0       24 (+0)             9
502        1.41M    1       0       25 (+1)             9
```

#### 데이터 탐색

**키 스캔:**
```bash
# 모든 키 스캔 (위험: 대용량 DB)
redis-cli --scan

# 패턴으로 필터링
redis-cli --scan --pattern user:*
redis-cli --scan --pattern session:*:data

# 타입별 필터링
redis-cli --scan --pattern "*" | xargs -I {} redis-cli TYPE {}
```

**빅키 찾기:**
```bash
# 메모리를 많이 사용하는 키 찾기
redis-cli --bigkeys

# 출력 예시:
[00.00%] Biggest string found so far 'user:12345' with 1024 bytes
[00.00%] Biggest list   found so far 'logs:2024' with 50000 items
[00.00%] Biggest set    found so far 'tags:popular' with 200 members
[00.00%] Biggest hash   found so far 'profile:user123' with 100 fields
[00.00%] Biggest zset   found so far 'leaderboard' with 1000 members
```

**핫키 찾기:**
```bash
# 자주 접근하는 키 찾기 (Redis 4.0+)
redis-cli --hotkeys

# 실시간 핫키 모니터링
redis-cli MONITOR | grep -E "(GET|SET|INCR|DECR)"
```

### 🛠️ 유지보수 명령어

#### 설정 관리

**설정 조회:**
```bash
# 모든 설정 조회
redis-cli CONFIG GET "*"

# 특정 설정 조회
redis-cli CONFIG GET "max*"
redis-cli CONFIG GET "save"

# 설정 변경 (일시적)
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET save "900 1 300 10"

# 설정을 파일에 저장
redis-cli CONFIG REWRITE
```

#### 백업과 복원

**데이터 백업:**
```bash
# RDB 스냅샷 생성
redis-cli BGSAVE

# 스냅샷 상태 확인
redis-cli LASTSAVE

# AOF 재작성
redis-cli BGREWRITEAOF

# 즉시 동기화 저장 (주의: 블로킹)
redis-cli SAVE
```

**데이터 내보내기:**
```bash
# 모든 데이터를 텍스트로 내보내기
redis-cli --rdb dump.rdb

# 특정 패턴의 키만 내보내기
redis-cli --scan --pattern "user:*" | xargs redis-cli MGET > users.txt

# JSON 형태로 내보내기
redis-cli --json --scan | while read key; do
  echo "$key: $(redis-cli --json GET "$key")"
done > export.json
```

#### 클라이언트 관리

**연결된 클라이언트 확인:**
```bash
# 클라이언트 목록
redis-cli CLIENT LIST

# 특정 클라이언트 종료
redis-cli CLIENT KILL 127.0.0.1:12345

# 모든 클라이언트 종료 (현재 제외)
redis-cli CLIENT KILL TYPE normal SKIPME yes
```

### 🎨 CLI 사용자 정의

#### 설정 파일

**~/.redisclirc 파일:**
```ini
# Redis CLI 설정 파일
127.0.0.1:6379>
prompt "%h:%p%d> "    # 호스트:포트데이터베이스> 형식
timeout 30            # 연결 타임아웃 (초)
output csv           # 기본 출력 형식
```

#### 별칭과 스크립트

**유용한 별칭들:**
```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
alias redisc='redis-cli'
alias redism='redis-cli MONITOR'
alias rediss='redis-cli --stat'
alias redisb='redis-cli --bigkeys'
alias redish='redis-cli --hotkeys'

# 자주 사용하는 명령 조합
alias redis-mem='redis-cli INFO memory | grep used_memory_human'
alias redis-keys='redis-cli INFO keyspace'
alias redis-clients='redis-cli CLIENT LIST | wc -l'
```

**스크립트 예시:**
```bash
#!/bin/bash
# redis-monitor.sh - Redis 모니터링 스크립트

echo "=== Redis Status ==="
redis-cli INFO server | grep redis_version
redis-cli INFO memory | grep used_memory_human
redis-cli INFO stats | grep total_commands_processed
redis-cli INFO clients | grep connected_clients

echo -e "\n=== Top 5 Biggest Keys ==="
redis-cli --bigkeys 2>/dev/null | tail -10

echo -e "\n=== Recent Commands ==="
redis-cli MONITOR &
MONITOR_PID=$!
sleep 5
kill $MONITOR_PID
```

---

## 2.8 설치 확인 및 첫 번째 명령어

### ✅ 설치 검증 체크리스트

#### 1단계: 서비스 상태 확인

**Linux/macOS:**
```bash
# Redis 프로세스 확인
ps aux | grep redis

# 출력 예시:
redis     1234  0.1  0.1  65536  12345 ?        Sl   10:00   0:00 redis-server 127.0.0.1:6379
user      5678  0.0  0.0  12345   6789 pts/0    S+   10:01   0:00 grep redis

# 포트 사용 확인
netstat -tlnp | grep :6379
# 또는
ss -tlnp | grep :6379

# 출력 예시:
tcp 0 0 127.0.0.1:6379 0.0.0.0:* LISTEN 1234/redis-server

# systemd 서비스 상태 (Linux)
systemctl status redis
# 또는
systemctl status redis-server

# Homebrew 서비스 상태 (macOS)
brew services list | grep redis
```

**Windows:**
```powershell
# Redis 프로세스 확인
Get-Process redis-server

# 포트 사용 확인
netstat -an | findstr :6379

# 서비스 상태 확인
Get-Service -Name Redis
```

**Docker:**
```bash
# 컨테이너 상태 확인
docker ps | grep redis

# 컨테이너 로그 확인
docker logs my-redis

# 헬스체크 상태 확인
docker inspect my-redis | grep Health -A 10
```

#### 2단계: 연결 테스트

**기본 연결 테스트:**
```bash
# Redis CLI로 연결
redis-cli ping

# 출력: PONG

# 연결 정보 확인
redis-cli INFO server

# 출력 예시:
# Server
redis_version:7.2.3
redis_git_sha1:00000000
redis_git_dirty:0
redis_build_id:c6e4d3e0ccd5e8a3
redis_mode:standalone
os:Linux 5.15.0-53-generic x86_64
arch_bits:64
multiplexing_api:epoll
gcc_version:9.4.0
process_id:1234
tcp_port:6379
uptime_in_seconds:300
uptime_in_days:0
```

**상세 연결 정보:**
```bash
# 클라이언트 정보
redis-cli CLIENT INFO

# 출력 예시:
id=3 addr=127.0.0.1:54321 fd=8 name= age=0 idle=0 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=26 qbuf-free=32742 argv-mem=10 obl=0 oll=0 omem=0 tot-mem=61466 events=r cmd=client user=default

# 메모리 정보
redis-cli INFO memory

# 키 공간 정보
redis-cli INFO keyspace
```

### 🚀 첫 번째 명령어 실습

#### 기본 데이터 조작

**1. 문자열 저장과 조회:**
```bash
# Redis CLI 시작
redis-cli

# 문자열 저장
127.0.0.1:6379> SET name "Redis Tutorial"
OK

# 문자열 조회
127.0.0.1:6379> GET name
"Redis Tutorial"

# 여러 값 동시 저장
127.0.0.1:6379> MSET user:1 "Alice" user:2 "Bob" user:3 "Charlie"
OK

# 여러 값 동시 조회
127.0.0.1:6379> MGET user:1 user:2 user:3
1) "Alice"
2) "Bob"
3) "Charlie"
```

**2. 숫자 연산:**
```bash
# 카운터 설정
127.0.0.1:6379> SET counter 0
OK

# 증가
127.0.0.1:6379> INCR counter
(integer) 1

# 5만큼 증가
127.0.0.1:6379> INCRBY counter 5
(integer) 6

# 감소
127.0.0.1:6379> DECR counter
(integer) 5

# 현재 값 확인
127.0.0.1:6379> GET counter
"5"
```

**3. TTL (Time To Live) 설정:**
```bash
# 10초 후 만료되는 키 설정
127.0.0.1:6379> SETEX temp_key 10 "This will expire"
OK

# TTL 확인
127.0.0.1:6379> TTL temp_key
(integer) 8

# 5초 후 다시 확인
127.0.0.1:6379> TTL temp_key
(integer) 3

# 만료 후 확인
127.0.0.1:6379> GET temp_key
(nil)
```

#### 리스트 조작

**4. 리스트 사용하기:**
```bash
# 리스트에 항목 추가 (왼쪽에)
127.0.0.1:6379> LPUSH shopping_list "Milk"
(integer) 1

127.0.0.1:6379> LPUSH shopping_list "Bread"
(integer) 2

127.0.0.1:6379> LPUSH shopping_list "Eggs"
(integer) 3

# 리스트 전체 보기
127.0.0.1:6379> LRANGE shopping_list 0 -1
1) "Eggs"
2) "Bread"
3) "Milk"

# 리스트에서 항목 제거 (오른쪽에서)
127.0.0.1:6379> RPOP shopping_list
"Milk"

# 리스트 길이 확인
127.0.0.1:6379> LLEN shopping_list
(integer) 2
```

#### 해시 조작

**5. 해시 사용하기:**
```bash
# 사용자 프로필 저장
127.0.0.1:6379> HSET profile:user1 name "Alice"
(integer) 1

127.0.0.1:6379> HSET profile:user1 age "25"
(integer) 1

127.0.0.1:6379> HSET profile:user1 city "Seoul"
(integer) 1

# 특정 필드 조회
127.0.0.1:6379> HGET profile:user1 name
"Alice"

# 전체 해시 조회
127.0.0.1:6379> HGETALL profile:user1
1) "name"
2) "Alice"
3) "age"
4) "25"
5) "city"
6) "Seoul"

# 여러 필드 동시 설정
127.0.0.1:6379> HMSET profile:user2 name "Bob" age "30" city "Busan"
OK
```

#### 집합 조작

**6. 집합 사용하기:**
```bash
# 태그 집합 생성
127.0.0.1:6379> SADD tags:post1 "redis" "database" "nosql"
(integer) 3

127.0.0.1:6379> SADD tags:post2 "redis" "tutorial" "programming"
(integer) 3

# 집합 멤버 확인
127.0.0.1:6379> SMEMBERS tags:post1
1) "nosql"
2) "database"
3) "redis"

# 교집합 구하기
127.0.0.1:6379> SINTER tags:post1 tags:post2
1) "redis"

# 합집합 구하기
127.0.0.1:6379> SUNION tags:post1 tags:post2
1) "nosql"
2) "database"
3) "redis"
4) "tutorial"
5) "programming"
```

### 🎯 실전 예제: 간단한 방문자 카운터

**7. 웹사이트 방문자 카운터 만들기:**
```bash
# 오늘 날짜로 카운터 초기화
127.0.0.1:6379> SET visitors:2024-01-15 0
OK

# 방문자 1명 추가
127.0.0.1:6379> INCR visitors:2024-01-15
(integer) 1

# 방문자 여러 명 추가
127.0.0.1:6379> INCRBY visitors:2024-01-15 5
(integer) 6

# 현재 방문자 수 확인
127.0.0.1:6379> GET visitors:2024-01-15
"6"

# 페이지별 방문자 수
127.0.0.1:6379> HINCRBY page_views "/home" visits 1
(integer) 1

127.0.0.1:6379> HINCRBY page_views "/about" visits 3
(integer) 3

127.0.0.1:6379> HINCRBY page_views "/contact" visits 2
(integer) 2

# 페이지별 통계 확인
127.0.0.1:6379> HGETALL page_views
1) "/home"
2) "1"
3) "/about"
4) "3"
5) "/contact"
6) "2"
```

### 🔍 기본 관리 명령어

**8. 키 관리:**
```bash
# 모든 키 보기 (주의: 대용량 DB에서는 위험)
127.0.0.1:6379> KEYS *
1) "name"
2) "counter"
3) "shopping_list"
4) "profile:user1"
5) "profile:user2"
6) "tags:post1"
7) "tags:post2"
8) "visitors:2024-01-15"
9) "page_views"

# 패턴으로 키 찾기
127.0.0.1:6379> KEYS profile:*
1) "profile:user1"
2) "profile:user2"

# 키 존재 여부 확인
127.0.0.1:6379> EXISTS name
(integer) 1

127.0.0.1:6379> EXISTS nonexistent
(integer) 0

# 키 타입 확인
127.0.0.1:6379> TYPE shopping_list
list

127.0.0.1:6379> TYPE profile:user1
hash

# 키 삭제
127.0.0.1:6379> DEL temp_key
(integer) 0

# 여러 키 삭제
127.0.0.1:6379> DEL key1 key2 key3
(integer) 2
```

**9. 데이터베이스 관리:**
```bash
# 현재 데이터베이스 정보
127.0.0.1:6379> INFO keyspace
# Keyspace
db0:keys=9,expires=0,avg_ttl=0

# 다른 데이터베이스로 전환
127.0.0.1:6379> SELECT 1
OK
127.0.0.1:6379[1]>

# 키를 다른 데이터베이스로 이동
127.0.0.1:6379> SELECT 0
OK
127.0.0.1:6379> MOVE name 1
(integer) 1

# 데이터베이스 크기 확인
127.0.0.1:6379> DBSIZE
(integer) 8

# 현재 데이터베이스 비우기 (주의!)
127.0.0.1:6379> FLUSHDB
OK
```

### 🏆 성공 확인

**모든 것이 정상 작동한다면 다음과 같은 출력을 볼 수 있습니다:**

```bash
# 최종 확인 테스트
127.0.0.1:6379> SET test "Redis is working!"
OK

127.0.0.1:6379> GET test
"Redis is working!"

127.0.0.1:6379> INCR test_counter
(integer) 1

127.0.0.1:6379> LPUSH test_list "item1" "item2"
(integer) 2

127.0.0.1:6379> HSET test_hash field1 "value1"
(integer) 1

127.0.0.1:6379> SADD test_set "member1" "member2"
(integer) 2

127.0.0.1:6379> INFO server | grep redis_version
redis_version:7.2.3

127.0.0.1:6379> PING
PONG
```

**축하합니다! 🎉 Redis가 성공적으로 설치되고 작동하고 있습니다!**

---

## 2.9 개발 환경별 최적화 설정

### 💻 로컬 개발 환경

#### 개발자 워크스테이션 설정

**개발용 redis.conf 최적화:**
```conf
# 개발 환경 최적화 설정
# /etc/redis/redis-dev.conf

################################## NETWORK #####################################
bind 127.0.0.1
port 6379
protected-mode yes
tcp-backlog 128

################################# GENERAL #####################################
daemonize yes
pidfile /var/run/redis/redis-dev.pid
loglevel notice
logfile /var/log/redis/redis-dev.log
databases 16

################################ SNAPSHOTTING  ################################
# 개발 중에는 빠른 재시작을 위해 스냅샷 비활성화
save ""

################################# REPLICATION #################################
# 개발용이므로 복제 없음

################################## SECURITY ###################################
requirepass devpassword123

################################### CLIENTS ####################################
maxclients 100

############################# MEMORY MANAGEMENT ##############################
maxmemory 1gb
maxmemory-policy allkeys-lru

############################# LAZY FREEING ####################################
lazyfree-lazy-eviction yes
lazyfree-lazy-expire yes
lazyfree-lazy-server-del yes
replica-lazy-flush yes

############################ KERNEL OOM CONTROL ##############################
oom-score-adj no

#################### KERNEL TRANSPARENT HUGEPAGE CONTROL ######################
disable-thp yes

############################## APPEND ONLY MODE ###############################
# 개발 중에는 성능을 위해 AOF 비활성화 (선택사항)
appendonly no

################################ LUA SCRIPTING  ###############################
lua-time-limit 5000

################################## SLOW LOG ###################################
slowlog-log-slower-than 10000
slowlog-max-len 128

################################ LATENCY MONITOR ##############################
latency-monitor-threshold 100
```

**개발용 시작 스크립트:**
```bash
#!/bin/bash
# redis-dev-start.sh

echo "Starting Redis Development Server..."

# 개발용 설정으로 Redis 시작
redis-server /etc/redis/redis-dev.conf

# 상태 확인
sleep 2
redis-cli -a devpassword123 ping

if [ $? -eq 0 ]; then
    echo "✅ Redis Development Server is running!"
    echo "📝 Connection: redis-cli -a devpassword123"
    echo "🔧 Config: /etc/redis/redis-dev.conf"
    echo "📊 Logs: /var/log/redis/redis-dev.log"
else
    echo "❌ Failed to start Redis Development Server"
    exit 1
fi
```

#### IDE 통합 설정

**VS Code 확장 프로그램:**
```json
// .vscode/extensions.json
{
  "recommendations": [
    "cweijan.vscode-redis-client",
    "humao.rest-client",
    "ms-vscode.vscode-json"
  ]
}
```

**VS Code Redis 설정:**
```json
// .vscode/settings.json
{
  "redis-client.defaultConnection": {
    "host": "127.0.0.1",
    "port": 6379,
    "auth": "devpassword123",
    "name": "Local Development"
  }
}
```

### 🧪 테스트 환경

#### 자동화된 테스트용 설정

**테스트용 Docker Compose:**
```yaml
# docker-compose.test.yml
version: '3.8'

services:
  redis-test:
    image: redis:7.2.3-alpine
    container_name: redis-test
    ports:
      - "6380:6379"  # 다른 포트 사용
    command: >
      redis-server
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
      --save ""
      --appendonly no
      --requirepass testpass123
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "testpass123", "ping"]
      interval: 5s
      timeout: 3s
      retries: 3
    tmpfs:
      - /data  # 메모리 파일시스템 사용 (빠른 테스트)

  redis-cluster-test:
    image: redis:7.2.3-alpine
    container_name: redis-cluster-test
    ports:
      - "7000-7005:7000-7005"
    command: redis-cli --cluster create 127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 --cluster-replicas 1 --cluster-yes
    depends_on:
      - redis-node1
      - redis-node2
      - redis-node3

  redis-node1:
    image: redis:7.2.3-alpine
    ports:
      - "7000:7000"
    volumes:
      - ./test-cluster/node1.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf

  redis-node2:
    image: redis:7.2.3-alpine
    ports:
      - "7001:7001"
    volumes:
      - ./test-cluster/node2.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf

  redis-node3:
    image: redis:7.2.3-alpine
    ports:
      - "7002:7002"
    volumes:
      - ./test-cluster/node3.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
```

**테스트 자동화 스크립트:**
```bash
#!/bin/bash
# test-redis-setup.sh

set -e

echo "🧪 Setting up Redis test environment..."

# 테스트 환경 시작
docker-compose -f docker-compose.test.yml up -d redis-test

# Redis가 준비될 때까지 대기
echo "⏳ Waiting for Redis to be ready..."
timeout 30 sh -c 'until docker exec redis-test redis-cli -a testpass123 ping; do sleep 1; done'

# 테스트 데이터 설정
echo "📊 Setting up test data..."
docker exec redis-test redis-cli -a testpass123 << EOF
FLUSHALL
SET test:config "test_environment"
HSET test:user:1 name "Test User" email "test@example.com"
LPUSH test:queue "job1" "job2" "job3"
SADD test:tags "redis" "test" "automation"
ZADD test:scores 100 "player1" 95 "player2" 87 "player3"
EOF

echo "✅ Redis test environment is ready!"
echo "🔗 Connection: redis-cli -h localhost -p 6380 -a testpass123"

# 연결 테스트
if docker exec redis-test redis-cli -a testpass123 ping > /dev/null; then
    echo "🎯 Connection test passed!"
else
    echo "❌ Connection test failed!"
    exit 1
fi
```

### 🏗️ CI/CD 파이프라인 통합

#### GitHub Actions 예시

**.github/workflows/redis-tests.yml:**
```yaml
name: Redis Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      redis:
        image: redis:7.2.3
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
          --entrypoint redis-server
          --
          --requirepass testpassword
          --maxmemory 256mb
          --maxmemory-policy allkeys-lru

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm install

    - name: Wait for Redis
      run: |
        until redis-cli -a testpassword ping; do
          echo "Waiting for Redis..."
          sleep 1
        done

    - name: Run Redis connection test
      run: |
        redis-cli -a testpassword set test "GitHub Actions"
        redis-cli -a testpassword get test

    - name: Run application tests
      env:
        REDIS_URL: redis://:testpassword@localhost:6379
      run: npm test

    - name: Run integration tests
      env:
        REDIS_HOST: localhost
        REDIS_PORT: 6379
        REDIS_PASSWORD: testpassword
      run: npm run test:integration
```

#### Jenkins 파이프라인

**Jenkinsfile:**
```groovy
pipeline {
    agent any

    environment {
        REDIS_PASSWORD = credentials('redis-test-password')
    }

    stages {
        stage('Setup Redis') {
            steps {
                script {
                    // Redis 테스트 컨테이너 시작
                    sh '''
                        docker run -d --name redis-test \
                          -p 6379:6379 \
                          --health-cmd="redis-cli -a $REDIS_PASSWORD ping" \
                          --health-interval=10s \
                          --health-timeout=5s \
                          --health-retries=3 \
                          redis:7.2.3 \
                          redis-server --requirepass $REDIS_PASSWORD
                    '''

                    // 헬스체크 대기
                    timeout(time: 2, unit: 'MINUTES') {
                        sh '''
                            until docker exec redis-test redis-cli -a $REDIS_PASSWORD ping; do
                                echo "Waiting for Redis..."
                                sleep 5
                            done
                        '''
                    }
                }
            }
        }

        stage('Test') {
            steps {
                sh '''
                    # 연결 테스트
                    docker exec redis-test redis-cli -a $REDIS_PASSWORD set test "Jenkins Pipeline"

                    # 애플리케이션 테스트 실행
                    export REDIS_URL="redis://:$REDIS_PASSWORD@localhost:6379"
                    npm test
                '''
            }
        }

        stage('Cleanup') {
            always {
                sh 'docker rm -f redis-test || true'
            }
        }
    }
}
```

### ⚡ 성능 테스트 환경

#### 벤치마크 설정

**성능 테스트 스크립트:**
```bash
#!/bin/bash
# redis-benchmark.sh

echo "🚀 Redis Performance Testing"

# 기본 성능 테스트
echo "📊 Basic Performance Test..."
redis-benchmark -h localhost -p 6379 -a yourpassword -q

# 특정 명령어 성능 테스트
echo "📈 SET Command Performance..."
redis-benchmark -h localhost -p 6379 -a yourpassword -t set -n 100000 -d 1000

echo "📈 GET Command Performance..."
redis-benchmark -h localhost -p 6379 -a yourpassword -t get -n 100000

# 파이프라인 성능 테스트
echo "🔄 Pipeline Performance..."
redis-benchmark -h localhost -p 6379 -a yourpassword -t set,get -n 100000 -P 16

# 메모리 사용량 테스트
echo "💾 Memory Usage Test..."
redis-cli -a yourpassword INFO memory | grep used_memory_human

# 동시 연결 테스트
echo "🔗 Concurrent Connections Test..."
redis-benchmark -h localhost -p 6379 -a yourpassword -c 50 -n 10000

echo "✅ Performance testing completed!"
```

**부하 테스트 Docker Compose:**
```yaml
# docker-compose.loadtest.yml
version: '3.8'

services:
  redis-target:
    image: redis:7.2.3
    container_name: redis-loadtest-target
    command: >
      redis-server
      --maxmemory 2gb
      --maxmemory-policy allkeys-lru
      --save ""
      --appendonly yes
      --appendfsync everysec
    ports:
      - "6379:6379"
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'

  redis-benchmark:
    image: redis:7.2.3
    container_name: redis-benchmark
    depends_on:
      - redis-target
    command: >
      sh -c "
        sleep 10 &&
        redis-benchmark -h redis-target -p 6379 -t set,get,incr,lpush,rpush,lpop,rpop,sadd,hset,spop,lrange,mset -n 1000000 -c 50 -d 1000 --csv
      "
    volumes:
      - ./benchmark-results:/results

  redis-monitor:
    image: redis:7.2.3
    container_name: redis-monitor
    depends_on:
      - redis-target
    command: >
      sh -c "
        sleep 5 &&
        while true; do
          echo '=== Redis Info ===' &&
          redis-cli -h redis-target INFO stats | grep instantaneous &&
          redis-cli -h redis-target INFO memory | grep used_memory_human &&
          redis-cli -h redis-target INFO clients | grep connected &&
          sleep 10
        done
      "
```

---

## 2.10 트러블슈팅 완전 가이드

### 🚨 일반적인 설치 문제

#### 문제 1: Redis 서버가 시작되지 않음

**증상:**
```bash
$ redis-server
Could not create server TCP listening socket 127.0.0.1:6379: bind: Address already in use
```

**원인 분석 및 해결:**
```bash
# 1. 포트 사용 중인 프로세스 확인
sudo lsof -i :6379
# 또는
sudo netstat -tlnp | grep :6379

# 출력 예시:
COMMAND    PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
redis-ser 1234 redis   6u  IPv4  12345      0t0  TCP 127.0.0.1:6379 (LISTEN)

# 2. 기존 Redis 프로세스 종료
sudo kill -TERM 1234
# 또는 강제 종료
sudo kill -9 1234

# 3. systemd 서비스 확인 및 중지
sudo systemctl stop redis
sudo systemctl status redis

# 4. 설정 파일 검증
redis-server --test-config /etc/redis/redis.conf

# 5. 다른 포트로 시작 (임시 해결)
redis-server --port 6380
```

#### 문제 2: 권한 문제

**증상:**
```bash
$ redis-server
Fatal error, can't open config file '/etc/redis/redis.conf': Permission denied
```

**해결책:**
```bash
# 1. 파일 권한 확인
ls -la /etc/redis/redis.conf

# 2. 소유권 수정
sudo chown redis:redis /etc/redis/redis.conf
sudo chmod 640 /etc/redis/redis.conf

# 3. Redis 사용자로 실행
sudo -u redis redis-server /etc/redis/redis.conf

# 4. 디렉토리 권한 확인
sudo chown -R redis:redis /var/lib/redis
sudo chown -R redis:redis /var/log/redis
sudo chmod 755 /var/lib/redis
sudo chmod 755 /var/log/redis
```

#### 문제 3: 메모리 부족

**증상:**
```bash
# Redis 로그에서
[1234] 15 Jan 10:00:00.000 # Warning: no config file specified, using the default config.
[1234] 15 Jan 10:00:01.000 # Out of memory: cannot allocate memory
```

**해결책:**
```bash
# 1. 시스템 메모리 확인
free -h
cat /proc/meminfo | grep MemAvailable

# 2. Redis 메모리 사용량 확인
redis-cli INFO memory

# 3. maxmemory 설정 추가
echo "maxmemory 1gb" >> /etc/redis/redis.conf
echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf

# 4. 스왑 설정 확인
sudo swapon --show
sudo fallocate -l 2G /swapfile  # 스왑 파일 생성 (필요시)

# 5. 오버커밋 설정 (Linux)
echo 'vm.overcommit_memory = 1' | sudo tee -a /etc/sysctl.conf
sudo sysctl vm.overcommit_memory=1
```

### 🔌 연결 문제

#### 문제 4: 클라이언트 연결 실패

**증상:**
```bash
$ redis-cli
Could not connect to Redis at 127.0.0.1:6379: Connection refused
```

**진단 및 해결:**
```bash
# 1. Redis 프로세스 확인
ps aux | grep redis-server

# 2. 서비스 상태 확인
sudo systemctl status redis

# 3. 서비스 시작
sudo systemctl start redis

# 4. 로그 확인
sudo journalctl -u redis -f
# 또는
tail -f /var/log/redis/redis-server.log

# 5. 설정 파일 bind 주소 확인
grep "^bind" /etc/redis/redis.conf

# 6. 방화벽 확인
sudo ufw status
sudo iptables -L

# 7. 테스트용 연결
telnet 127.0.0.1 6379
```

#### 문제 5: 인증 오류

**증상:**
```bash
$ redis-cli
127.0.0.1:6379> GET test
(error) NOAUTH Authentication required.
```

**해결책:**
```bash
# 1. 패스워드로 인증
redis-cli -a yourpassword

# 2. 연결 후 인증
redis-cli
127.0.0.1:6379> AUTH yourpassword
OK

# 3. 설정 파일에서 패스워드 확인
grep "^requirepass" /etc/redis/redis.conf

# 4. 패스워드 변경
redis-cli
127.0.0.1:6379> CONFIG SET requirepass newpassword
OK

# 5. 패스워드 제거 (개발용)
redis-cli -a currentpassword
127.0.0.1:6379> CONFIG SET requirepass ""
OK
```

### 🐳 Docker 관련 문제

#### 문제 6: Docker 컨테이너 시작 실패

**증상:**
```bash
$ docker run redis
docker: Error response from daemon: Conflict. The container name "/redis" is already in use
```

**해결책:**
```bash
# 1. 기존 컨테이너 확인
docker ps -a | grep redis

# 2. 기존 컨테이너 제거
docker rm -f redis

# 3. 이미지 문제 확인
docker images | grep redis

# 4. 이미지 재다운로드
docker pull redis:7.2.3

# 5. 로그 확인
docker logs redis-container-name

# 6. 컨테이너 내부 접속하여 디버깅
docker exec -it redis-container-name /bin/sh
```

#### 문제 7: Docker 볼륨 문제

**증상:**
```bash
# 컨테이너 재시작 후 데이터 손실
```

**해결책:**
```bash
# 1. 볼륨 확인
docker volume ls

# 2. 볼륨 상세 정보
docker volume inspect redis-data

# 3. 올바른 볼륨 마운트
docker run -d --name redis -v redis-data:/data redis:7.2.3

# 4. 바인드 마운트 사용
docker run -d --name redis -v /host/path:/data redis:7.2.3

# 5. 권한 문제 해결
sudo chown -R 999:999 /host/path  # Redis UID/GID
```

### 🔧 성능 문제

#### 문제 8: 느린 응답 시간

**진단:**
```bash
# 1. 응답 시간 측정
redis-cli --latency -i 1

# 2. 슬로우 로그 확인
redis-cli SLOWLOG GET 10

# 3. 메모리 사용량 확인
redis-cli INFO memory

# 4. 클라이언트 연결 확인
redis-cli INFO clients

# 5. 키 분포 확인
redis-cli --bigkeys
```

**해결책:**
```bash
# 1. 메모리 최적화
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# 2. 파이프라이닝 사용
redis-cli --pipe < commands.txt

# 3. 연결 풀링 설정 (애플리케이션에서)

# 4. 인덱스 최적화 (키 네이밍 개선)

# 5. 하드웨어 업그레이드 고려
```

#### 문제 9: 메모리 사용량 급증

**진단:**
```bash
# 1. 메모리 사용량 모니터링
redis-cli INFO memory | grep used_memory

# 2. 큰 키 찾기
redis-cli --bigkeys

# 3. 키 만료 설정 확인
redis-cli TTL suspicious-key

# 4. 메모리 누수 확인
redis-cli DEBUG OBJECT suspicious-key
```

**해결책:**
```bash
# 1. TTL 설정
redis-cli EXPIRE large-key 3600

# 2. 메모리 정책 변경
redis-cli CONFIG SET maxmemory-policy volatile-lru

# 3. 대용량 키 분할
# 예: 큰 해시를 여러 개의 작은 해시로 분할

# 4. 압축 알고리즘 활용
redis-cli CONFIG SET hash-max-ziplist-entries 512
```

### 📱 플랫폼별 특수 문제

#### Windows 관련 문제

**문제: WSL2에서 Redis 접근 불가**
```powershell
# Windows에서 WSL2 Redis 접근
# 1. WSL2 IP 확인
wsl hostname -I

# 2. Windows에서 접근
redis-cli -h 172.x.x.x -p 6379

# 3. 포트 포워딩 설정
netsh interface portproxy add v4tov4 listenport=6379 listenaddress=0.0.0.0 connectport=6379 connectaddress=172.x.x.x
```

#### macOS 관련 문제

**문제: M1/M2 Mac에서 성능 이슈**
```bash
# 1. Rosetta 2 확인
arch -arm64 redis-server --version

# 2. 네이티브 바이너리 설치
brew install redis

# 3. Docker 대신 네이티브 설치 권장
```

### 🔍 고급 디버깅

#### 상세 로그 분석

**로그 레벨 증가:**
```bash
# 임시로 디버그 로그 활성화
redis-cli CONFIG SET loglevel debug

# 로그 실시간 모니터링
tail -f /var/log/redis/redis-server.log

# 특정 패턴 검색
grep "ERROR\|WARNING" /var/log/redis/redis-server.log
```

#### 네트워크 디버깅

**연결 추적:**
```bash
# 1. 네트워크 연결 모니터링
sudo ss -tulpn | grep :6379

# 2. 패킷 캡처
sudo tcpdump -i any port 6379

# 3. Redis 프로토콜 분석
redis-cli MONITOR

# 4. 클라이언트 정보 확인
redis-cli CLIENT LIST
```

### 📞 도움 요청하기

#### 버그 리포트 준비

**필요한 정보 수집:**
```bash
#!/bin/bash
# redis-debug-info.sh

echo "=== Redis Debug Information ==="
echo "Date: $(date)"
echo ""

echo "=== System Information ==="
uname -a
cat /etc/os-release
echo ""

echo "=== Redis Version ==="
redis-server --version
echo ""

echo "=== Redis Configuration ==="
redis-cli CONFIG GET "*" 2>/dev/null || echo "Cannot connect to Redis"
echo ""

echo "=== Redis Info ==="
redis-cli INFO 2>/dev/null || echo "Cannot connect to Redis"
echo ""

echo "=== System Resources ==="
free -h
df -h
echo ""

echo "=== Process Information ==="
ps aux | grep redis
echo ""

echo "=== Network ==="
ss -tulpn | grep :6379
echo ""

echo "=== Recent Logs ==="
tail -50 /var/log/redis/redis-server.log 2>/dev/null || echo "No log file found"
```

**커뮤니티 도움:**
- Redis GitHub Issues: https://github.com/redis/redis/issues
- Redis Google Group: https://groups.google.com/g/redis-db
- Stack Overflow: 태그 `redis`
- Reddit: r/redis

---

## ✅ 섹션 2 요약

### 🎯 설치 완료 체크리스트

```
✅ 운영체제별 설치 완료:
- [ ] Windows (WSL2/Native/Docker)
- [ ] macOS (Homebrew/소스컴파일)
- [ ] Linux (APT/YUM/소스컴파일)
- [ ] Docker (단일/Compose/클러스터)

✅ 기본 설정 완료:
- [ ] 네트워크 설정 (bind, port)
- [ ] 보안 설정 (requirepass)
- [ ] 메모리 설정 (maxmemory)
- [ ] 영속성 설정 (RDB/AOF)

✅ 도구 사용법 습득:
- [ ] Redis CLI 기본 사용법
- [ ] 모니터링 명령어
- [ ] 디버깅 도구 활용

✅ 환경별 최적화:
- [ ] 개발 환경 설정
- [ ] 테스트 환경 구성
- [ ] CI/CD 통합

✅ 트러블슈팅 대비:
- [ ] 일반적인 문제 해결법 숙지
- [ ] 로그 분석 방법 이해
- [ ] 성능 최적화 방법 학습
```

### 🚀 다음 단계

이제 Redis가 완벽하게 설치되고 설정되었습니다! 다음 장에서는:

```
섹션 3: Redis 기본 조작 마스터하기
- Redis CLI 고급 사용법
- 데이터 저장과 조회의 모든 것
- 키 관리 전략
- TTL과 만료 시간 활용법
- 데이터베이스 선택과 관리
```

### 💡 핵심 포인트

```
🔧 설치는 환경에 맞게:
- 개발: Docker 또는 로컬 설치
- 테스트: Docker Compose
- 운영: 클라우드 관리형 서비스 권장

⚙️ 설정은 용도에 맞게:
- 개발: 편의성 중심
- 테스트: 안정성 중심
- 운영: 보안과 성능 중심

🚨 문제 발생 시:
- 로그를 먼저 확인
- 네트워크와 권한 점검
- 커뮤니티 도움 요청
```

---

**축하합니다! 🎉** Redis 설치와 환경 설정을 완벽하게 마스터했습니다!

**다음 장으로 이동:** 👉 [3. Redis 기본 조작 마스터하기](./03-Redis-기본-조작-마스터하기.md)