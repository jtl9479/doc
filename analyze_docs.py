#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLUDE-ULTIMATE 템플릿 체크리스트 분석 도구
"""

import os
import re
from pathlib import Path

def count_items(content, pattern):
    """패턴을 기반으로 항목 개수를 세는 함수"""
    matches = re.findall(pattern, content, re.MULTILINE)
    return len(matches)

def analyze_document(filepath):
    """각 문서를 분석하여 체크리스트 항목을 확인"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    result = {
        'filename': os.path.basename(filepath),
        'has_learning_goal': bool(re.search(r'^> \*\*학습 목표\*\*:', content, re.MULTILINE)),
        'has_time': bool(re.search(r'^\*\*⏱️ 예상 학습 시간\*\*:', content, re.MULTILINE)),
        'has_difficulty': bool(re.search(r'^\*\*난이도\*\*:', content, re.MULTILINE)),
        'has_toc': bool(re.search(r'^## (📚 )?목차', content, re.MULTILINE)),
        'has_why': bool(re.search(r'^## 왜', content, re.MULTILINE)),
        'has_analogy_section': bool(re.search(r'^## (🔍 |🌟 )?실생활 비유', content, re.MULTILINE)),
        'has_scenario': bool(re.search(r'^## (👨‍💻 )?주니어 시나리오', content, re.MULTILINE)),
        'has_faq': bool(re.search(r'^## (❓ )?FAQ', content, re.MULTILINE)),
        'has_interview': bool(re.search(r'^## (📝 )?면접 질문', content, re.MULTILINE)),
    }

    # 비유 개수 세기 (### 비유 1, ### 비유 2, 등)
    analogy_count = count_items(content, r'^### 비유 \d+')
    result['analogy_count'] = analogy_count

    # 주니어 시나리오 개수 세기
    scenario_section = re.search(r'^## (👨‍💻 )?주니어 시나리오.*?(?=^## |\Z)', content, re.MULTILINE | re.DOTALL)
    if scenario_section:
        scenario_text = scenario_section.group(0)
        # 시나리오 1, 시나리오 2 등 패턴
        scenario_count = count_items(scenario_text, r'^### 시나리오 \d+')
        result['scenario_count'] = scenario_count
    else:
        result['scenario_count'] = 0

    # FAQ 개수 세기
    faq_section = re.search(r'^## (❓ )?FAQ.*?(?=^## |\Z)', content, re.MULTILINE | re.DOTALL)
    if faq_section:
        faq_text = faq_section.group(0)
        # Q: 또는 ### Q 패턴
        faq_count = count_items(faq_text, r'^### [Q❓]')
        result['faq_count'] = faq_count
    else:
        result['faq_count'] = 0

    # 면접 질문 개수 세기
    interview_section = re.search(r'^## (📝 )?면접 질문.*?(?=^## |\Z)', content, re.MULTILINE | re.DOTALL)
    if interview_section:
        interview_text = interview_section.group(0)
        # 주니어 질문 개수
        junior_count = count_items(interview_text, r'^\*\*Q\d+\*\*:|^#### [Q❓]\d+')
        # 중급 질문 개수도 세기
        mid_count = count_items(interview_text, r'^#### 중급')
        result['interview_count'] = junior_count
        result['interview_junior'] = count_items(interview_text, r'^#### 주니어')
        result['interview_mid'] = count_items(interview_text, r'^#### 중급')
    else:
        result['interview_count'] = 0
        result['interview_junior'] = 0
        result['interview_mid'] = 0

    return result

def main():
    docker_dir = Path(r'C:\Users\user\Desktop\doc\doc\docker')

    files_to_analyze = [
        '00-효과적인-학습-방법.md',
        '01-Docker란-무엇인가.md',
        '02-아키텍처와-내부-동작-원리.md',
        '03-이미지-레이어와-파일시스템.md',
        '04-격리-기술과-생명주기.md',
        '05-설치-및-환경-설정.md',
        '06-기본-명령어.md',
        '07-Dockerfile-작성-가이드.md',
        '08-멀티스테이지-빌드.md',
        '09-이미지-최적화.md',
        '10-Docker-네트워크.md',
        '11-Docker-볼륨.md',
        '12-Docker-Compose-기초.md',
        '13-docker-compose-yml-완전-가이드.md',
        '14-Docker-Compose-고급-기능.md',
        '15-LK-Trade-Docker-구성.md',
        '16-API-Gateway와-Nginx.md',
        '17-모니터링과-로깅.md',
        '18-CI-CD-파이프라인.md',
        '19-개발-환경-구성.md',
        '20-실전-워크플로우.md',
    ]

    print("| 문서명 | 학습목표 | 예상시간 | 난이도 | 목차 | 왜필요 | 비유개수 | 주니어시나리오 | FAQ | 면접질문 | 누락항목 |")
    print("|--------|----------|----------|--------|------|--------|----------|----------------|-----|----------|----------|")

    results = []
    for filename in files_to_analyze:
        filepath = docker_dir / filename
        if filepath.exists():
            result = analyze_document(filepath)
            results.append(result)

            # 누락 항목 파악
            missing = []
            if not result['has_learning_goal']:
                missing.append('학습목표')
            if not result['has_time']:
                missing.append('예상시간')
            if not result['has_difficulty']:
                missing.append('난이도')
            if not result['has_toc']:
                missing.append('목차')
            if not result['has_why']:
                missing.append('왜필요')
            if not result['has_analogy_section']:
                missing.append('비유섹션')
            if result['analogy_count'] < 2:
                missing.append(f'비유부족({result["analogy_count"]}/2+)')
            if not result['has_scenario']:
                missing.append('시나리오섹션')
            if result['scenario_count'] < 3:
                missing.append(f'시나리오부족({result["scenario_count"]}/3-4)')
            if not result['has_faq']:
                missing.append('FAQ섹션')
            if result['faq_count'] < 3:
                missing.append(f'FAQ부족({result["faq_count"]}/3-5)')
            if not result['has_interview']:
                missing.append('면접섹션')
            if result['interview_count'] < 5:
                missing.append(f'면접질문부족({result["interview_count"]}/5)')

            # 체크 마크 또는 X
            def check(val):
                return '✅' if val else '❌'

            missing_str = ', '.join(missing) if missing else '없음'

            print(f"| {filename[:20]}... | {check(result['has_learning_goal'])} | {check(result['has_time'])} | {check(result['has_difficulty'])} | {check(result['has_toc'])} | {check(result['has_why'])} | {result['analogy_count']} | {result['scenario_count']} | {result['faq_count']} | {result['interview_count']} | {missing_str} |")
        else:
            print(f"| {filename} | ⚠️ 파일 없음 |")

    print("\n\n=== 상세 분석 ===\n")

    # 100% 완벽한 문서
    perfect = [r for r in results if not any([
        not r['has_learning_goal'],
        not r['has_time'],
        not r['has_difficulty'],
        not r['has_toc'],
        not r['has_why'],
        not r['has_analogy_section'],
        r['analogy_count'] < 2,
        not r['has_scenario'],
        r['scenario_count'] < 3,
        not r['has_faq'],
        r['faq_count'] < 3,
        not r['has_interview'],
        r['interview_count'] < 5
    ])]

    print(f"✅ 100% 완벽한 문서 ({len(perfect)}개):")
    for r in perfect:
        print(f"   - {r['filename']}")

    print(f"\n⚠️ 개선 필요 문서 ({len(results) - len(perfect)}개):")
    for r in results:
        if r not in perfect:
            print(f"\n   {r['filename']}:")
            if not r['has_learning_goal']:
                print(f"      - [ ] 학습 목표 추가")
            if not r['has_time']:
                print(f"      - [ ] 예상 학습 시간 추가")
            if not r['has_difficulty']:
                print(f"      - [ ] 난이도 추가")
            if not r['has_toc']:
                print(f"      - [ ] 목차 추가")
            if not r['has_why']:
                print(f"      - [ ] '왜 필요한가' 섹션 추가")
            if not r['has_analogy_section']:
                print(f"      - [ ] 실생활 비유 섹션 추가")
            if r['analogy_count'] < 2:
                print(f"      - [ ] 비유 추가 (현재 {r['analogy_count']}개 → 최소 2-3개 필요)")
            if not r['has_scenario']:
                print(f"      - [ ] 주니어 시나리오 섹션 추가")
            if r['scenario_count'] < 3:
                print(f"      - [ ] 시나리오 추가 (현재 {r['scenario_count']}개 → 3-4개 필요)")
            if not r['has_faq']:
                print(f"      - [ ] FAQ 섹션 추가")
            if r['faq_count'] < 3:
                print(f"      - [ ] FAQ 추가 (현재 {r['faq_count']}개 → 3-5개 필요)")
            if not r['has_interview']:
                print(f"      - [ ] 면접 질문 섹션 추가")
            if r['interview_count'] < 5:
                print(f"      - [ ] 면접 질문 추가 (현재 {r['interview_count']}개 → 주니어 2개 + 중급 3개 = 5개 필요)")

if __name__ == '__main__':
    main()
