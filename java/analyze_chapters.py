import os
import re

files = sorted([f for f in os.listdir('.') if f.endswith('.md')])

result = {}
for file in files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract chapter number
            match = re.match(r'(\d+)', file)
            if match:
                chapter_num = int(match.group(1))
            else:
                chapter_num = 0

            # Check for Part pattern
            is_part = bool(re.search(r'Part[123]', file))

            # Check for key sections
            has_learning_goals = '학습 목표' in content or '## 학습 목표' in content
            has_why_needed = '왜 필요한가' in content
            has_analogy = '비유로 이해하기' in content or '실생활 비유' in content
            has_core_concept = '핵심 개념' in content
            has_practice = '기본 실습' in content
            has_real_case = '실무 활용' in content or '기업 사례' in content
            has_junior_scenario = '주니어' in content
            has_project = '실전 프로젝트' in content
            has_faq = 'FAQ' in content or '자주 묻는 질문' in content
            has_interview = '면접 질문' in content
            has_summary = '핵심 정리' in content or '핵심 내용 정리' in content
            has_next_step = '다음 단계' in content

            result[file] = {
                'chapter': chapter_num,
                'is_part': is_part,
                'sections': {
                    '학습목표': has_learning_goals,
                    '왜필요한가': has_why_needed,
                    '비유': has_analogy,
                    '핵심개념': has_core_concept,
                    '기본실습': has_practice,
                    '실무활용': has_real_case,
                    '주니어시나리오': has_junior_scenario,
                    '실전프로젝트': has_project,
                    'FAQ': has_faq,
                    '면접질문': has_interview,
                    '핵심정리': has_summary,
                    '다음단계': has_next_step
                }
            }
    except:
        pass

# Group by chapter
chapters = {}
for file, data in result.items():
    ch = data['chapter']
    if ch not in chapters:
        chapters[ch] = []
    chapters[ch].append((file, data))

# Print results
print("=" * 80)
print("Java 챕터 분석 결과")
print("=" * 80)

ultimate_count = 0
part_count = 0
other_count = 0

for ch in sorted(chapters.keys()):
    files_in_chapter = chapters[ch]

    # Determine chapter type
    has_parts = any(data['is_part'] for _, data in files_in_chapter)

    if has_parts:
        # Part 형식
        part_count += 1
        print(f'\n챕터 {ch:02d}: ⚠️ Part 형식')
        for file, data in files_in_chapter:
            sections = data['sections']
            count = sum(1 for v in sections.values() if v)
            missing = [k for k, v in sections.items() if not v]
            print(f'  - {file}: {count}/12 섹션')
            if missing:
                print(f'    누락: {", ".join(missing[:5])}')
    else:
        # SINGLE 파일 - ULTIMATE 형식 확인
        if len(files_in_chapter) == 1:
            file, data = files_in_chapter[0]
            sections = data['sections']
            count = sum(1 for v in sections.values() if v)

            if count >= 10:
                ultimate_count += 1
                print(f'\n챕터 {ch:02d}: ✅ ULTIMATE 형식 ({count}/12)')
                print(f'  - {file}')
            else:
                other_count += 1
                print(f'\n챕터 {ch:02d}: ❌ 불명확 ({count}/12)')
                print(f'  - {file}')
                missing = [k for k, v in sections.items() if not v]
                if missing:
                    print(f'    누락: {", ".join(missing)}')
        else:
            other_count += 1
            print(f'\n챕터 {ch:02d}: ❌ 복수 파일')
            for file, data in files_in_chapter:
                print(f'  - {file}')

print("\n" + "=" * 80)
print("최종 요약")
print("=" * 80)
print(f"전체 챕터 수: {len(chapters)}")
print(f"✅ ULTIMATE 형식: {ultimate_count}개")
print(f"⚠️ Part 형식: {part_count}개")
print(f"❌ 기타/불명확: {other_count}개")
print("=" * 80)
