#!/bin/bash
# CLUDE-ULTIMATE 템플릿 체크리스트 분석 스크립트

cd "/c/Users/user/Desktop/doc/doc/docker"

files=(
    "00-효과적인-학습-방법.md"
    "01-Docker란-무엇인가.md"
    "02-아키텍처와-내부-동작-원리.md"
    "03-이미지-레이어와-파일시스템.md"
    "04-격리-기술과-생명주기.md"
    "05-설치-및-환경-설정.md"
    "06-기본-명령어.md"
    "07-Dockerfile-작성-가이드.md"
    "08-멀티스테이지-빌드.md"
    "09-이미지-최적화.md"
    "10-Docker-네트워크.md"
    "11-Docker-볼륨.md"
    "12-Docker-Compose-기초.md"
    "13-docker-compose-yml-완전-가이드.md"
    "14-Docker-Compose-고급-기능.md"
    "15-LK-Trade-Docker-구성.md"
    "16-API-Gateway와-Nginx.md"
    "17-모니터링과-로깅.md"
    "18-CI-CD-파이프라인.md"
    "19-개발-환경-구성.md"
    "20-실전-워크플로우.md"
)

echo "| 문서명 | 학습목표 | 예상시간 | 난이도 | 목차 | 왜필요 | 비유개수 | 시나리오 | FAQ | 면접질문 |"
echo "|--------|----------|----------|--------|------|--------|----------|----------|-----|----------|"

for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "| $file | ⚠️ 파일 없음 | | | | | | | | |"
        continue
    fi

    # 1. 학습 목표
    학습목표=$(grep -c "^> \*\*학습 목표\*\*:" "$file" 2>/dev/null || echo "0")
    학습목표_mark=$([[ $학습목표 -gt 0 ]] && echo "✅" || echo "❌")

    # 2. 예상 학습 시간
    예상시간=$(grep -c "^\*\*⏱️ 예상 학습 시간\*\*:" "$file" 2>/dev/null || echo "0")
    예상시간_mark=$([[ $예상시간 -gt 0 ]] && echo "✅" || echo "❌")

    # 3. 난이도
    난이도=$(grep -c "^\*\*난이도\*\*:" "$file" 2>/dev/null || echo "0")
    난이도_mark=$([[ $난이도 -gt 0 ]] && echo "✅" || echo "❌")

    # 4. 목차
    목차=$(grep -c "^## .*목차" "$file" 2>/dev/null || echo "0")
    목차_mark=$([[ $목차 -gt 0 ]] && echo "✅" || echo "❌")

    # 5. 왜 필요한가
    왜필요=$(grep -c "^## 왜" "$file" 2>/dev/null || echo "0")
    왜필요_mark=$([[ $왜필요 -gt 0 ]] && echo "✅" || echo "❌")

    # 6. 비유 개수 (### 비유 1, ### 비유 2 패턴)
    비유개수=$(grep -c "^### 비유 [0-9]" "$file" 2>/dev/null || echo "0")

    # 7. 주니어 시나리오 개수
    시나리오=$(grep -c "^### 시나리오 [0-9]" "$file" 2>/dev/null || echo "0")

    # 8. FAQ 개수 (tail로 끝부분만 읽어서 성능 향상)
    faq개수=$(tail -800 "$file" 2>/dev/null | grep -c "^<summary><strong>[Q❓]" || echo "0")

    # 9. 면접 질문 개수
    면접개수=$(tail -1500 "$file" 2>/dev/null | grep -c "^<summary><strong>[0-9]" || echo "0")

    # 파일명을 짧게 표시
    short_name=$(echo "$file" | cut -c1-25)

    echo "| $short_name | $학습목표_mark | $예상시간_mark | $난이도_mark | $목차_mark | $왜필요_mark | $비유개수 | $시나리오 | $faq개수 | $면접개수 |"
done

echo ""
echo "=== 상세 분석 시작 ==="
echo ""

# 100% 완벽한 문서 찾기
for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        continue
    fi

    학습목표=$(grep -c "^> \*\*학습 목표\*\*:" "$file" 2>/dev/null || echo "0")
    예상시간=$(grep -c "^\*\*⏱️ 예상 학습 시간\*\*:" "$file" 2>/dev/null || echo "0")
    난이도=$(grep -c "^\*\*난이도\*\*:" "$file" 2>/dev/null || echo "0")
    목차=$(grep -c "^## .*목차" "$file" 2>/dev/null || echo "0")
    왜필요=$(grep -c "^## 왜" "$file" 2>/dev/null || echo "0")
    비유개수=$(grep -c "^### 비유 [0-9]" "$file" 2>/dev/null || echo "0")
    시나리오=$(grep -c "^### 시나리오 [0-9]" "$file" 2>/dev/null || echo "0")
    faq개수=$(tail -800 "$file" 2>/dev/null | grep -c "^<summary><strong>[Q❓]" || echo "0")
    면접개수=$(tail -1500 "$file" 2>/dev/null | grep -c "^<summary><strong>[0-9]" || echo "0")

    # 완벽한지 체크
    perfect=true
    missing=()

    [[ $학습목표 -eq 0 ]] && perfect=false && missing+=("학습목표")
    [[ $예상시간 -eq 0 ]] && perfect=false && missing+=("예상시간")
    [[ $난이도 -eq 0 ]] && perfect=false && missing+=("난이도")
    [[ $목차 -eq 0 ]] && perfect=false && missing+=("목차")
    [[ $왜필요 -eq 0 ]] && perfect=false && missing+=("왜필요")
    [[ $비유개수 -lt 2 ]] && perfect=false && missing+=("비유부족($비유개수/2+)")
    [[ $시나리오 -lt 3 ]] && perfect=false && missing+=("시나리오부족($시나리오/3-4)")
    [[ $faq개수 -lt 3 ]] && perfect=false && missing+=("FAQ부족($faq개수/3-5)")
    [[ $면접개수 -lt 5 ]] && perfect=false && missing+=("면접부족($면접개수/5)")

    if [ "$perfect" = false ]; then
        echo "❌ $file"
        echo "   누락 항목:"
        for item in "${missing[@]}"; do
            echo "      - $item"
        done
        echo ""
    fi
done
