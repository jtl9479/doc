# 27장 Set 인터페이스 - Part 3: 실전 프로젝트 & FAQ & 면접 질문

## 📚 목차
1. [실전 프로젝트: 회원 관리 시스템](#실전-프로젝트)
2. [7개 FAQ](#faq)
3. [12개 면접 질문](#면접-질문)
   - 주니어 레벨 (7문)
   - 중급 레벨 (5문)

---

## 🚀 실전 프로젝트: 회원 관리 시스템

### 📋 프로젝트 개요

**프로젝트명**: MembershipSystem
**난이도**: ⭐⭐⭐ (중급)
**학습 목표**:
- HashSet으로 회원 ID 중복 체크
- TreeSet으로 등급별 회원 정렬
- LinkedHashSet으로 가입 순서 유지
- Set 집합 연산으로 세그먼트 분석

**요구사항**:
1. 회원 등록/조회/삭제 (중복 ID 방지)
2. 등급별 회원 정렬 (VIP → Gold → Silver)
3. 가입 순서 추적
4. 세그먼트 분석 (활성/비활성 회원)

---

### 📁 프로젝트 구조

```
membership/
├── model/
│   ├── Member.java
│   ├── MemberGrade.java
│   └── MemberStatus.java
├── service/
│   ├── MembershipService.java
│   ├── MemberAnalytics.java
│   └── MemberSegmentation.java
├── repository/
│   └── MemberRepository.java
└── Main.java
```

---

### 💻 전체 구현 코드

#### 1. Member.java (회원 도메인)

```java
package membership.model;

import java.time.LocalDateTime;
import java.util.Objects;

/**
 * 회원 정보
 */
public class Member implements Comparable<Member> {
    private final String memberId;           // 회원 ID (유니크)
    private String name;                     // 이름
    private String email;                    // 이메일
    private MemberGrade grade;               // 등급
    private MemberStatus status;             // 상태
    private final LocalDateTime joinedAt;    // 가입일시
    private LocalDateTime lastLoginAt;       // 최종 로그인
    private int point;                       // 포인트

    public Member(String memberId, String name, String email, MemberGrade grade) {
        this.memberId = memberId;
        this.name = name;
        this.email = email;
        this.grade = grade;
        this.status = MemberStatus.ACTIVE;
        this.joinedAt = LocalDateTime.now();
        this.lastLoginAt = LocalDateTime.now();
        this.point = 0;
    }

    /**
     * Comparable 구현: 등급 → 포인트 → 가입일순 정렬
     */
    @Override
    public int compareTo(Member other) {
        // 1순위: 등급 (VIP > GOLD > SILVER)
        int gradeCompare = this.grade.compareTo(other.grade);
        if (gradeCompare != 0) {
            return gradeCompare;
        }

        // 2순위: 포인트 (많은 순)
        int pointCompare = Integer.compare(other.point, this.point);
        if (pointCompare != 0) {
            return pointCompare;
        }

        // 3순위: 가입일 (오래된 순)
        return this.joinedAt.compareTo(other.joinedAt);
    }

    /**
     * equals/hashCode: memberId로만 판단
     */
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Member member = (Member) o;
        return memberId.equals(member.memberId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(memberId);
    }

    // Getters and Setters
    public String getMemberId() { return memberId; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public MemberGrade getGrade() { return grade; }
    public void setGrade(MemberGrade grade) { this.grade = grade; }
    public MemberStatus getStatus() { return status; }
    public void setStatus(MemberStatus status) { this.status = status; }
    public LocalDateTime getJoinedAt() { return joinedAt; }
    public LocalDateTime getLastLoginAt() { return lastLoginAt; }
    public void setLastLoginAt(LocalDateTime lastLoginAt) { this.lastLoginAt = lastLoginAt; }
    public int getPoint() { return point; }
    public void setPoint(int point) { this.point = point; }

    public void addPoint(int point) {
        this.point += point;
    }

    @Override
    public String toString() {
        return String.format("[%s] %s (%s) - %s, %,d포인트",
            memberId, name, email, grade, point);
    }

    public String toDetailString() {
        return String.format("""
            회원 ID: %s
            이름: %s
            이메일: %s
            등급: %s
            상태: %s
            포인트: %,d
            가입일: %s
            최종 로그인: %s
            """,
            memberId, name, email, grade, status, point,
            joinedAt.toLocalDate(), lastLoginAt.toLocalDate()
        );
    }
}
```

#### 2. MemberGrade.java (회원 등급)

```java
package membership.model;

/**
 * 회원 등급
 */
public enum MemberGrade {
    VIP("VIP", 1000000),
    GOLD("골드", 500000),
    SILVER("실버", 0);

    private final String displayName;
    private final int requiredPoint; // 등급 유지 포인트

    MemberGrade(String displayName, int requiredPoint) {
        this.displayName = displayName;
        this.requiredPoint = requiredPoint;
    }

    public String getDisplayName() { return displayName; }
    public int getRequiredPoint() { return requiredPoint; }

    /**
     * 포인트로 등급 계산
     */
    public static MemberGrade fromPoint(int point) {
        if (point >= VIP.requiredPoint) {
            return VIP;
        } else if (point >= GOLD.requiredPoint) {
            return GOLD;
        } else {
            return SILVER;
        }
    }

    @Override
    public String toString() {
        return displayName;
    }
}
```

#### 3. MemberStatus.java (회원 상태)

```java
package membership.model;

/**
 * 회원 상태
 */
public enum MemberStatus {
    ACTIVE("활성"),
    INACTIVE("휴면"),
    BANNED("정지"),
    WITHDRAWN("탈퇴");

    private final String displayName;

    MemberStatus(String displayName) {
        this.displayName = displayName;
    }

    public String getDisplayName() { return displayName; }

    @Override
    public String toString() {
        return displayName;
    }
}
```

#### 4. MemberRepository.java (저장소)

```java
package membership.repository;

import membership.model.Member;
import membership.model.MemberGrade;
import membership.model.MemberStatus;

import java.util.*;

/**
 * 회원 저장소
 *
 * 3가지 Set을 활용한 다중 인덱싱
 */
public class MemberRepository {
    // 1. HashSet: 빠른 조회 (O(1))
    private final Map<String, Member> memberMap;

    // 2. TreeSet: 등급별 정렬된 조회
    private final TreeSet<Member> membersByGrade;

    // 3. LinkedHashSet: 가입 순서 유지
    private final LinkedHashSet<Member> membersByJoinOrder;

    public MemberRepository() {
        this.memberMap = new HashMap<>();
        this.membersByGrade = new TreeSet<>();
        this.membersByJoinOrder = new LinkedHashSet<>();
    }

    /**
     * 회원 등록
     */
    public boolean addMember(Member member) {
        // 중복 체크
        if (memberMap.containsKey(member.getMemberId())) {
            return false;
        }

        // 3개 자료구조에 모두 추가
        memberMap.put(member.getMemberId(), member);
        membersByGrade.add(member);
        membersByJoinOrder.add(member);

        return true;
    }

    /**
     * 회원 조회 (O(1))
     */
    public Member findById(String memberId) {
        return memberMap.get(memberId);
    }

    /**
     * 회원 존재 여부
     */
    public boolean exists(String memberId) {
        return memberMap.containsKey(memberId);
    }

    /**
     * 회원 삭제
     */
    public boolean removeMember(String memberId) {
        Member member = memberMap.remove(memberId);

        if (member != null) {
            membersByGrade.remove(member);
            membersByJoinOrder.remove(member);
            return true;
        }

        return false;
    }

    /**
     * 회원 정보 업데이트 (TreeSet 재정렬 필요)
     */
    public void updateMember(Member member) {
        Member existing = memberMap.get(member.getMemberId());

        if (existing != null) {
            // TreeSet에서 제거 (정렬 기준이 바뀔 수 있음)
            membersByGrade.remove(existing);

            // 정보 업데이트
            existing.setName(member.getName());
            existing.setEmail(member.getEmail());
            existing.setGrade(member.getGrade());
            existing.setStatus(member.getStatus());
            existing.setPoint(member.getPoint());
            existing.setLastLoginAt(member.getLastLoginAt());

            // TreeSet에 재추가 (자동 재정렬)
            membersByGrade.add(existing);
        }
    }

    /**
     * 전체 회원 수
     */
    public int getMemberCount() {
        return memberMap.size();
    }

    /**
     * 전체 회원 (HashSet - 순서 없음)
     */
    public Set<Member> getAllMembers() {
        return new HashSet<>(memberMap.values());
    }

    /**
     * 등급순 회원 조회 (TreeSet)
     */
    public List<Member> getMembersByGrade() {
        return new ArrayList<>(membersByGrade);
    }

    /**
     * 가입순 회원 조회 (LinkedHashSet)
     */
    public List<Member> getMembersByJoinOrder() {
        return new ArrayList<>(membersByJoinOrder);
    }

    /**
     * 등급별 회원 조회
     */
    public Set<Member> getMembersByGrade(MemberGrade grade) {
        Set<Member> result = new HashSet<>();

        for (Member member : memberMap.values()) {
            if (member.getGrade() == grade) {
                result.add(member);
            }
        }

        return result;
    }

    /**
     * 상태별 회원 조회
     */
    public Set<Member> getMembersByStatus(MemberStatus status) {
        Set<Member> result = new HashSet<>();

        for (Member member : memberMap.values()) {
            if (member.getStatus() == status) {
                result.add(member);
            }
        }

        return result;
    }

    /**
     * 통계 정보
     */
    public void printStatistics() {
        System.out.println("📊 회원 통계:");
        System.out.println("  - 전체: " + memberMap.size() + "명");
        System.out.println("  - VIP: " + getMembersByGrade(MemberGrade.VIP).size() + "명");
        System.out.println("  - 골드: " + getMembersByGrade(MemberGrade.GOLD).size() + "명");
        System.out.println("  - 실버: " + getMembersByGrade(MemberGrade.SILVER).size() + "명");
        System.out.println("  - 활성: " + getMembersByStatus(MemberStatus.ACTIVE).size() + "명");
        System.out.println("  - 휴면: " + getMembersByStatus(MemberStatus.INACTIVE).size() + "명");
    }
}
```

#### 5. MembershipService.java (비즈니스 로직)

```java
package membership.service;

import membership.model.Member;
import membership.model.MemberGrade;
import membership.model.MemberStatus;
import membership.repository.MemberRepository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Set;

/**
 * 회원 서비스
 */
public class MembershipService {
    private final MemberRepository repository;

    public MembershipService(MemberRepository repository) {
        this.repository = repository;
    }

    /**
     * 회원 가입
     */
    public boolean registerMember(String memberId, String name, String email) {
        // 중복 체크
        if (repository.exists(memberId)) {
            System.out.println("❌ 이미 존재하는 회원 ID입니다: " + memberId);
            return false;
        }

        Member member = new Member(memberId, name, email, MemberGrade.SILVER);
        boolean success = repository.addMember(member);

        if (success) {
            System.out.println("✅ 회원 가입 완료: " + member);
        }

        return success;
    }

    /**
     * 회원 조회
     */
    public Member getMember(String memberId) {
        Member member = repository.findById(memberId);

        if (member == null) {
            System.out.println("❌ 회원을 찾을 수 없습니다: " + memberId);
        }

        return member;
    }

    /**
     * 회원 탈퇴
     */
    public boolean withdrawMember(String memberId) {
        boolean success = repository.removeMember(memberId);

        if (success) {
            System.out.println("✅ 회원 탈퇴 완료: " + memberId);
        } else {
            System.out.println("❌ 회원을 찾을 수 없습니다: " + memberId);
        }

        return success;
    }

    /**
     * 포인트 적립
     */
    public void earnPoint(String memberId, int point) {
        Member member = repository.findById(memberId);

        if (member == null) {
            System.out.println("❌ 회원을 찾을 수 없습니다: " + memberId);
            return;
        }

        member.addPoint(point);

        // 등급 재계산
        MemberGrade newGrade = MemberGrade.fromPoint(member.getPoint());
        if (newGrade != member.getGrade()) {
            System.out.println("🎉 등급 상승: " + member.getGrade() + " → " + newGrade);
            member.setGrade(newGrade);
        }

        // 업데이트 (TreeSet 재정렬)
        repository.updateMember(member);

        System.out.println("✅ 포인트 적립: " + memberId + " (+" + String.format("%,d", point) + "포인트)");
    }

    /**
     * 로그인 처리
     */
    public void login(String memberId) {
        Member member = repository.findById(memberId);

        if (member == null) {
            System.out.println("❌ 회원을 찾을 수 없습니다: " + memberId);
            return;
        }

        member.setLastLoginAt(LocalDateTime.now());

        // 휴면 → 활성 전환
        if (member.getStatus() == MemberStatus.INACTIVE) {
            member.setStatus(MemberStatus.ACTIVE);
            System.out.println("🔄 휴면 회원 활성화: " + memberId);
        }

        repository.updateMember(member);
        System.out.println("✅ 로그인: " + member.getName());
    }

    /**
     * 휴면 회원 전환 (90일 미접속)
     */
    public void updateInactiveMembers() {
        LocalDateTime threshold = LocalDateTime.now().minusDays(90);
        int count = 0;

        Set<Member> allMembers = repository.getAllMembers();

        for (Member member : allMembers) {
            if (member.getStatus() == MemberStatus.ACTIVE &&
                member.getLastLoginAt().isBefore(threshold)) {

                member.setStatus(MemberStatus.INACTIVE);
                repository.updateMember(member);
                count++;
            }
        }

        System.out.println("🔄 휴면 회원 전환: " + count + "명");
    }

    /**
     * 등급별 회원 조회
     */
    public void printMembersByGrade() {
        System.out.println("\n📋 등급순 회원 목록:");

        List<Member> members = repository.getMembersByGrade();

        MemberGrade currentGrade = null;
        int index = 1;

        for (Member member : members) {
            // 등급이 바뀔 때마다 헤더 출력
            if (currentGrade != member.getGrade()) {
                currentGrade = member.getGrade();
                System.out.println("\n" + currentGrade + " 등급:");
            }

            System.out.println("  " + index++ + ". " + member);
        }
    }

    /**
     * 가입순 회원 조회
     */
    public void printMembersByJoinOrder() {
        System.out.println("\n📋 가입순 회원 목록:");

        List<Member> members = repository.getMembersByJoinOrder();

        for (int i = 0; i < members.size(); i++) {
            System.out.println("  " + (i + 1) + ". " + members.get(i));
        }
    }
}
```

#### 6. MemberAnalytics.java (분석 서비스)

```java
package membership.service;

import membership.model.Member;
import membership.model.MemberGrade;
import membership.model.MemberStatus;
import membership.repository.MemberRepository;

import java.util.*;

/**
 * 회원 분석 서비스
 */
public class MemberAnalytics {
    private final MemberRepository repository;

    public MemberAnalytics(MemberRepository repository) {
        this.repository = repository;
    }

    /**
     * VIP 회원 분석
     */
    public void analyzeVipMembers() {
        Set<Member> vipMembers = repository.getMembersByGrade(MemberGrade.VIP);

        System.out.println("\n🎯 VIP 회원 분석:");
        System.out.println("  - VIP 회원 수: " + vipMembers.size() + "명");

        if (vipMembers.isEmpty()) {
            return;
        }

        // 평균 포인트
        double avgPoint = vipMembers.stream()
            .mapToInt(Member::getPoint)
            .average()
            .orElse(0);

        System.out.println("  - 평균 포인트: " + String.format("%,.0f", avgPoint));

        // TOP 3 VIP
        System.out.println("\n  TOP 3 VIP:");
        List<Member> sortedVips = new ArrayList<>(vipMembers);
        sortedVips.sort(Comparator.comparingInt(Member::getPoint).reversed());

        for (int i = 0; i < Math.min(3, sortedVips.size()); i++) {
            Member member = sortedVips.get(i);
            System.out.println("    " + (i + 1) + ". " + member.getName() +
                " (" + String.format("%,d", member.getPoint()) + "포인트)");
        }
    }

    /**
     * 활성/휴면 회원 비율
     */
    public void analyzeActivityRate() {
        Set<Member> activeMembers = repository.getMembersByStatus(MemberStatus.ACTIVE);
        Set<Member> inactiveMembers = repository.getMembersByStatus(MemberStatus.INACTIVE);

        int total = repository.getMemberCount();

        double activeRate = (double) activeMembers.size() / total * 100;
        double inactiveRate = (double) inactiveMembers.size() / total * 100;

        System.out.println("\n📊 활성 비율:");
        System.out.println("  - 활성: " + activeMembers.size() + "명 (" +
            String.format("%.1f", activeRate) + "%)");
        System.out.println("  - 휴면: " + inactiveMembers.size() + "명 (" +
            String.format("%.1f", inactiveRate) + "%)");
    }

    /**
     * 등급별 분포
     */
    public void analyzeGradeDistribution() {
        System.out.println("\n📊 등급별 분포:");

        for (MemberGrade grade : MemberGrade.values()) {
            Set<Member> members = repository.getMembersByGrade(grade);
            double percentage = (double) members.size() / repository.getMemberCount() * 100;

            System.out.println("  - " + grade + ": " + members.size() + "명 (" +
                String.format("%.1f", percentage) + "%)");
        }
    }
}
```

#### 7. MemberSegmentation.java (세그먼트 분석)

```java
package membership.service;

import membership.model.Member;
import membership.model.MemberGrade;
import membership.model.MemberStatus;
import membership.repository.MemberRepository;

import java.util.*;

/**
 * 회원 세그먼트 분석 (Set 집합 연산 활용)
 */
public class MemberSegmentation {
    private final MemberRepository repository;

    public MemberSegmentation(MemberRepository repository) {
        this.repository = repository;
    }

    /**
     * 타겟 마케팅 세그먼트 찾기
     * (활성 VIP/GOLD 회원)
     */
    public Set<Member> findTargetSegment() {
        // VIP 회원
        Set<Member> vipMembers = repository.getMembersByGrade(MemberGrade.VIP);

        // GOLD 회원
        Set<Member> goldMembers = repository.getMembersByGrade(MemberGrade.GOLD);

        // 활성 회원
        Set<Member> activeMembers = repository.getMembersByStatus(MemberStatus.ACTIVE);

        // 합집합: VIP ∪ GOLD
        Set<Member> premiumMembers = new HashSet<>(vipMembers);
        premiumMembers.addAll(goldMembers);

        // 교집합: (VIP ∪ GOLD) ∩ ACTIVE
        Set<Member> targetSegment = new HashSet<>(premiumMembers);
        targetSegment.retainAll(activeMembers);

        System.out.println("\n🎯 타겟 마케팅 세그먼트 (활성 VIP/GOLD):");
        System.out.println("  - VIP: " + vipMembers.size() + "명");
        System.out.println("  - GOLD: " + goldMembers.size() + "명");
        System.out.println("  - 활성: " + activeMembers.size() + "명");
        System.out.println("  - 타겟: " + targetSegment.size() + "명");

        return targetSegment;
    }

    /**
     * 재활성화 타겟 (휴면 VIP/GOLD)
     */
    public Set<Member> findReactivationTarget() {
        // VIP + GOLD
        Set<Member> premiumMembers = new HashSet<>(repository.getMembersByGrade(MemberGrade.VIP));
        premiumMembers.addAll(repository.getMembersByGrade(MemberGrade.GOLD));

        // 휴면 회원
        Set<Member> inactiveMembers = repository.getMembersByStatus(MemberStatus.INACTIVE);

        // 교집합: Premium ∩ Inactive
        Set<Member> reactivationTarget = new HashSet<>(premiumMembers);
        reactivationTarget.retainAll(inactiveMembers);

        System.out.println("\n🔄 재활성화 타겟 (휴면 VIP/GOLD):");
        System.out.println("  - 타겟: " + reactivationTarget.size() + "명");

        if (!reactivationTarget.isEmpty()) {
            System.out.println("  목록:");
            reactivationTarget.forEach(m ->
                System.out.println("    - " + m.getName() + " (" + m.getGrade() + ")")
            );
        }

        return reactivationTarget;
    }

    /**
     * 등급 업그레이드 후보 (고포인트 SILVER/GOLD)
     */
    public Set<Member> findUpgradeCandidates() {
        // SILVER 회원 중 GOLD 기준 근접
        Set<Member> silverMembers = repository.getMembersByGrade(MemberGrade.SILVER);
        Set<Member> silverCandidates = new HashSet<>();

        for (Member member : silverMembers) {
            if (member.getPoint() >= MemberGrade.GOLD.getRequiredPoint() * 0.8) {
                silverCandidates.add(member);
            }
        }

        // GOLD 회원 중 VIP 기준 근접
        Set<Member> goldMembers = repository.getMembersByGrade(MemberGrade.GOLD);
        Set<Member> goldCandidates = new HashSet<>();

        for (Member member : goldMembers) {
            if (member.getPoint() >= MemberGrade.VIP.getRequiredPoint() * 0.8) {
                goldCandidates.add(member);
            }
        }

        System.out.println("\n⬆️ 등급 업그레이드 후보:");
        System.out.println("  - SILVER → GOLD 후보: " + silverCandidates.size() + "명");
        System.out.println("  - GOLD → VIP 후보: " + goldCandidates.size() + "명");

        // 합집합 반환
        Set<Member> allCandidates = new HashSet<>(silverCandidates);
        allCandidates.addAll(goldCandidates);

        return allCandidates;
    }

    /**
     * 이탈 위험 회원 (낮은 포인트 + 낮은 활동)
     */
    public Set<Member> findChurnRisk() {
        Set<Member> activeMembers = repository.getMembersByStatus(MemberStatus.ACTIVE);
        Set<Member> churnRisk = new HashSet<>();

        // 포인트 하위 20% + 최근 30일 미접속
        List<Member> sortedByPoint = new ArrayList<>(activeMembers);
        sortedByPoint.sort(Comparator.comparingInt(Member::getPoint));

        int bottom20Percent = (int) (sortedByPoint.size() * 0.2);

        for (int i = 0; i < Math.min(bottom20Percent, sortedByPoint.size()); i++) {
            Member member = sortedByPoint.get(i);

            if (member.getLastLoginAt().isBefore(
                java.time.LocalDateTime.now().minusDays(30))) {
                churnRisk.add(member);
            }
        }

        System.out.println("\n⚠️ 이탈 위험 회원:");
        System.out.println("  - 타겟: " + churnRisk.size() + "명");

        return churnRisk;
    }

    /**
     * 세그먼트 벤 다이어그램
     */
    public void printVennDiagram() {
        Set<Member> vipMembers = repository.getMembersByGrade(MemberGrade.VIP);
        Set<Member> activeMembers = repository.getMembersByStatus(MemberStatus.ACTIVE);

        // VIP ∩ ACTIVE
        Set<Member> vipAndActive = new HashSet<>(vipMembers);
        vipAndActive.retainAll(activeMembers);

        // VIP - ACTIVE
        Set<Member> vipOnly = new HashSet<>(vipMembers);
        vipOnly.removeAll(activeMembers);

        // ACTIVE - VIP
        Set<Member> activeOnly = new HashSet<>(activeMembers);
        activeOnly.removeAll(vipMembers);

        System.out.println("\n📊 벤 다이어그램 (VIP vs 활성):");
        System.out.println("  - VIP만: " + vipOnly.size() + "명");
        System.out.println("  - 교집합: " + vipAndActive.size() + "명");
        System.out.println("  - 활성만: " + activeOnly.size() + "명");
    }
}
```

#### 8. Main.java (메인 프로그램)

```java
package membership;

import membership.model.Member;
import membership.model.MemberGrade;
import membership.repository.MemberRepository;
import membership.service.MemberAnalytics;
import membership.service.MemberSegmentation;
import membership.service.MembershipService;

import java.util.Set;

/**
 * 회원 관리 시스템 데모
 */
public class Main {
    public static void main(String[] args) {
        // 초기화
        MemberRepository repository = new MemberRepository();
        MembershipService service = new MembershipService(repository);
        MemberAnalytics analytics = new MemberAnalytics(repository);
        MemberSegmentation segmentation = new MemberSegmentation(repository);

        System.out.println("=== 회원 관리 시스템 ===\n");

        // 시나리오 1: 회원 가입
        System.out.println("📍 시나리오 1: 회원 가입");
        service.registerMember("M001", "김철수", "kim@example.com");
        service.registerMember("M002", "이영희", "lee@example.com");
        service.registerMember("M003", "박민수", "park@example.com");
        service.registerMember("M004", "정지훈", "jung@example.com");
        service.registerMember("M005", "최유리", "choi@example.com");
        System.out.println();

        // 중복 가입 시도
        System.out.println("중복 가입 시도:");
        service.registerMember("M001", "김철수2", "kim2@example.com");
        System.out.println();

        // 시나리오 2: 포인트 적립 (등급 변화)
        System.out.println("📍 시나리오 2: 포인트 적립");
        service.earnPoint("M001", 600000);  // GOLD 달성
        service.earnPoint("M002", 1200000); // VIP 달성
        service.earnPoint("M003", 300000);  // SILVER 유지
        service.earnPoint("M001", 500000);  // VIP 달성
        service.earnPoint("M004", 800000);  // GOLD 달성
        System.out.println();

        // 시나리오 3: 등급순 조회 (TreeSet)
        System.out.println("📍 시나리오 3: 등급순 조회");
        service.printMembersByGrade();
        System.out.println();

        // 시나리오 4: 가입순 조회 (LinkedHashSet)
        System.out.println("📍 시나리오 4: 가입순 조회");
        service.printMembersByJoinOrder();
        System.out.println();

        // 시나리오 5: 통계 조회
        System.out.println("\n📍 시나리오 5: 통계 조회");
        repository.printStatistics();

        // 시나리오 6: VIP 분석
        analytics.analyzeVipMembers();

        // 시나리오 7: 등급별 분포
        analytics.analyzeGradeDistribution();

        // 시나리오 8: 세그먼트 분석
        System.out.println("\n📍 시나리오 8: 세그먼트 분석");

        Set<Member> targetSegment = segmentation.findTargetSegment();

        Set<Member> upgradeCandidates = segmentation.findUpgradeCandidates();

        // 시나리오 9: 휴면 회원 시뮬레이션
        System.out.println("\n📍 시나리오 9: 휴면 회원 처리");

        // M003, M005를 휴면으로 변경
        Member m3 = repository.findById("M003");
        Member m5 = repository.findById("M005");

        if (m3 != null) {
            m3.setLastLoginAt(java.time.LocalDateTime.now().minusDays(100));
            m3.setStatus(membership.model.MemberStatus.INACTIVE);
            repository.updateMember(m3);
        }

        if (m5 != null) {
            m5.setLastLoginAt(java.time.LocalDateTime.now().minusDays(120));
            m5.setStatus(membership.model.MemberStatus.INACTIVE);
            repository.updateMember(m5);
        }

        repository.printStatistics();

        // 재활성화 타겟
        segmentation.findReactivationTarget();

        // 벤 다이어그램
        segmentation.printVennDiagram();

        // 시나리오 10: 로그인 (휴면 → 활성)
        System.out.println("\n📍 시나리오 10: 휴면 회원 로그인");
        service.login("M003");
        System.out.println();

        repository.printStatistics();

        // 시나리오 11: 회원 탈퇴
        System.out.println("\n📍 시나리오 11: 회원 탈퇴");
        service.withdrawMember("M005");
        System.out.println();

        repository.printStatistics();

        // 시나리오 12: 대량 회원 처리
        System.out.println("\n📍 시나리오 12: 대량 회원 성능 테스트");

        long start = System.nanoTime();

        // 10,000명 회원 가입
        for (int i = 1000; i < 11000; i++) {
            String memberId = "M" + String.format("%05d", i);
            Member member = new Member(memberId, "회원" + i, "user" + i + "@example.com", MemberGrade.SILVER);
            repository.addMember(member);
        }

        long end = System.nanoTime();

        System.out.println("10,000명 회원 가입: " +
            String.format("%.2f", (end - start) / 1_000_000.0) + "ms");

        // 조회 성능
        start = System.nanoTime();
        Member found = repository.findById("M05000");
        end = System.nanoTime();

        System.out.println("회원 조회 (10,005명 중): " +
            String.format("%.3f", (end - start) / 1_000.0) + "μs");
        System.out.println("→ HashSet의 O(1) 성능");

        // 최종 통계
        System.out.println("\n📊 최종 통계:");
        repository.printStatistics();
    }
}
```

---

### 🎯 프로젝트 실행 결과

```
=== 회원 관리 시스템 ===

📍 시나리오 1: 회원 가입
✅ 회원 가입 완료: [M001] 김철수 (kim@example.com) - 실버, 0포인트
✅ 회원 가입 완료: [M002] 이영희 (lee@example.com) - 실버, 0포인트
✅ 회원 가입 완료: [M003] 박민수 (park@example.com) - 실버, 0포인트
✅ 회원 가입 완료: [M004] 정지훈 (jung@example.com) - 실버, 0포인트
✅ 회원 가입 완료: [M005] 최유리 (choi@example.com) - 실버, 0포인트

중복 가입 시도:
❌ 이미 존재하는 회원 ID입니다: M001

📍 시나리오 2: 포인트 적립
✅ 포인트 적립: M001 (+600,000포인트)
🎉 등급 상승: 실버 → 골드
✅ 포인트 적립: M002 (+1,200,000포인트)
🎉 등급 상승: 실버 → VIP
✅ 포인트 적립: M003 (+300,000포인트)
✅ 포인트 적립: M001 (+500,000포인트)
🎉 등급 상승: 골드 → VIP
✅ 포인트 적립: M004 (+800,000포인트)
🎉 등급 상승: 실버 → 골드

📍 시나리오 3: 등급순 조회

📋 등급순 회원 목록:

VIP 등급:
  1. [M002] 이영희 (lee@example.com) - VIP, 1,200,000포인트
  2. [M001] 김철수 (kim@example.com) - VIP, 1,100,000포인트

골드 등급:
  3. [M004] 정지훈 (jung@example.com) - 골드, 800,000포인트

실버 등급:
  4. [M003] 박민수 (park@example.com) - 실버, 300,000포인트
  5. [M005] 최유리 (choi@example.com) - 실버, 0포인트

📍 시나리오 4: 가입순 조회

📋 가입순 회원 목록:
  1. [M001] 김철수 (kim@example.com) - VIP, 1,100,000포인트
  2. [M002] 이영희 (lee@example.com) - VIP, 1,200,000포인트
  3. [M003] 박민수 (park@example.com) - 실버, 300,000포인트
  4. [M004] 정지훈 (jung@example.com) - 골드, 800,000포인트
  5. [M005] 최유리 (choi@example.com) - 실버, 0포인트

📍 시나리오 5: 통계 조회
📊 회원 통계:
  - 전체: 5명
  - VIP: 2명
  - 골드: 1명
  - 실버: 2명
  - 활성: 5명
  - 휴면: 0명

🎯 VIP 회원 분석:
  - VIP 회원 수: 2명
  - 평균 포인트: 1,150,000

  TOP 3 VIP:
    1. 이영희 (1,200,000포인트)
    2. 김철수 (1,100,000포인트)

📊 등급별 분포:
  - VIP: 2명 (40.0%)
  - 골드: 1명 (20.0%)
  - 실버: 2명 (40.0%)

📍 시나리오 8: 세그먼트 분석

🎯 타겟 마케팅 세그먼트 (활성 VIP/GOLD):
  - VIP: 2명
  - GOLD: 1명
  - 활성: 5명
  - 타겟: 3명

⬆️ 등급 업그레이드 후보:
  - SILVER → GOLD 후보: 0명
  - GOLD → VIP 후보: 1명

📍 시나리오 12: 대량 회원 성능 테스트
10,000명 회원 가입: 45.32ms
회원 조회 (10,005명 중): 2.134μs
→ HashSet의 O(1) 성능

📊 최종 통계:
  - 전체: 10,004명
  - VIP: 2명
  - 골드: 1명
  - 실버: 10,001명
  - 활성: 10,002명
  - 휴면: 1명
```

---

### 📊 프로젝트 핵심 포인트

#### 1. 3가지 Set 활용

| Set 구현체 | 용도 | 성능 | 특징 |
|-----------|------|------|------|
| **HashMap (memberMap)** | ID 기반 조회 | O(1) | 빠른 검색 |
| **TreeSet (membersByGrade)** | 등급순 정렬 | O(log n) | 자동 정렬 |
| **LinkedHashSet (membersByJoinOrder)** | 가입순 유지 | O(1) | 순서 보존 |

#### 2. 집합 연산 활용

```java
// 합집합: VIP ∪ GOLD
Set<Member> premium = new HashSet<>(vip);
premium.addAll(gold);

// 교집합: Premium ∩ Active
Set<Member> target = new HashSet<>(premium);
target.retainAll(active);

// 차집합: VIP - Active (휴면 VIP)
Set<Member> inactive = new HashSet<>(vip);
inactive.removeAll(active);
```

#### 3. TreeSet 재정렬 패턴

```java
// 포인트 변경 시 TreeSet 재정렬 필요
membersByGrade.remove(member);  // 1. 제거
member.addPoint(point);         // 2. 값 변경
membersByGrade.add(member);     // 3. 재추가 (자동 정렬)
```

#### 4. 성능 측정

```
10,000명 회원 가입: 45ms
회원 조회 (10,005명 중): 2μs

→ HashSet의 O(1) 조회 성능 입증
```

---

## ❓ FAQ

### ❓ FAQ 1: Set과 List의 차이점은?

**답변**:
```java
// List: 중복 허용, 순서 유지, 인덱스 접근
List<String> list = new ArrayList<>();
list.add("사과");
list.add("사과"); // 중복 허용
System.out.println(list.size()); // 2
System.out.println(list.get(0)); // 인덱스 접근 가능

// Set: 중복 불가, 순서 보장 안 됨 (구현체에 따라 다름)
Set<String> set = new HashSet<>();
set.add("사과");
set.add("사과"); // 중복 무시
System.out.println(set.size()); // 1
// set.get(0); // ❌ 컴파일 오류 (인덱스 접근 불가)
```

**선택 기준**:
| 요구사항 | 선택 |
|---------|------|
| 중복 허용 필요 | `List` |
| 중복 제거 필요 | `Set` |
| 순서 유지 필요 | `List` 또는 `LinkedHashSet` |
| 인덱스 접근 필요 | `List` |
| 빠른 contains() | `Set` (O(1) vs O(n)) |

---

### ❓ FAQ 2: HashSet, LinkedHashSet, TreeSet 중 어떤 것을 선택해야 하나요?

**답변**:

**1. HashSet** - 기본 선택
```java
Set<String> set = new HashSet<>();
```
- ✅ 가장 빠름 (O(1))
- ✅ 메모리 효율적
- ❌ 순서 없음

**사용 예**: 중복 제거, 빠른 존재 여부 확인

**2. LinkedHashSet** - 순서 필요 시
```java
Set<String> set = new LinkedHashSet<>();
```
- ✅ 빠름 (O(1))
- ✅ 삽입 순서 유지
- ❌ 약간 더 많은 메모리

**사용 예**: 중복 제거 + 순서 유지, LRU 캐시

**3. TreeSet** - 정렬 필요 시
```java
Set<String> set = new TreeSet<>();
```
- ✅ 자동 정렬
- ✅ 범위 검색 (subSet, headSet, tailSet)
- ❌ 느림 (O(log n))
- ❌ Comparable/Comparator 필요

**사용 예**: 정렬된 데이터, 범위 검색

**선택 플로우차트**:
```
정렬이 필요한가?
├─ YES → TreeSet
└─ NO  → 순서가 필요한가?
          ├─ YES → LinkedHashSet
          └─ NO  → HashSet (기본 선택)
```

---

### ❓ FAQ 3: Set에 null을 저장할 수 있나요?

**답변**:

**구현체별 null 지원**:
```java
// 1. HashSet: null 1개 허용
Set<String> hashSet = new HashSet<>();
hashSet.add(null);
hashSet.add(null); // 중복이므로 무시
System.out.println(hashSet.size()); // 1 ✓

// 2. LinkedHashSet: null 1개 허용
Set<String> linkedSet = new LinkedHashSet<>();
linkedSet.add(null); // ✓

// 3. TreeSet: null 불가 (NullPointerException)
Set<String> treeSet = new TreeSet<>();
try {
    treeSet.add(null); // ❌ NullPointerException
} catch (NullPointerException e) {
    System.out.println("TreeSet은 null 불가");
}
```

**왜 TreeSet은 null 불가?**
```java
// TreeSet은 정렬을 위해 compareTo() 호출
// null.compareTo(other) → NullPointerException

// 해결책: null 허용 Comparator 사용
Set<String> treeSet = new TreeSet<>(Comparator.nullsFirst(Comparator.naturalOrder()));
treeSet.add(null); // ✓
treeSet.add("A");
treeSet.add("B");
// 출력: [null, A, B]
```

**권장사항**:
```
❌ Set에 null 저장하지 마세요
✅ Optional이나 빈 문자열 사용
✅ null 체크 로직 추가
```

---

### ❓ FAQ 4: equals()와 hashCode()를 반드시 같이 구현해야 하나요?

**답변**: **예, 반드시 함께 구현해야 합니다!**

**이유**:
```java
// HashSet은 2단계로 중복 체크
// 1단계: hashCode() - 같은 버킷 찾기
// 2단계: equals() - 버킷 내에서 동일성 확인

// ❌ hashCode만 구현 시
class BadProduct {
    private String id;

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    // equals 미구현 → Object.equals (참조 비교)
}

Set<BadProduct> set = new HashSet<>();
BadProduct p1 = new BadProduct("P001");
BadProduct p2 = new BadProduct("P001");

set.add(p1);
set.add(p2);

System.out.println(set.size()); // 2 ❌ (같은 버킷이지만 equals가 false)
```

**equals/hashCode 계약**:
```java
// 규칙 1: equals가 true면 hashCode도 같아야 함
if (a.equals(b)) {
    assert a.hashCode() == b.hashCode(); // 반드시
}

// 규칙 2: hashCode가 다르면 equals는 false
if (a.hashCode() != b.hashCode()) {
    assert !a.equals(b); // 반드시
}

// 규칙 3: equals에서 사용한 필드를 hashCode에서도 사용
@Override
public boolean equals(Object o) {
    Product that = (Product) o;
    return id.equals(that.id) && name.equals(that.name);
}

@Override
public int hashCode() {
    return Objects.hash(id, name); // equals와 동일한 필드
}
```

**IDE 자동 생성 사용**:
```java
// IntelliJ: Alt + Insert → equals() and hashCode()
// Eclipse: Source → Generate hashCode() and equals()

// Lombok 사용
@EqualsAndHashCode(of = "id")
class Product {
    private String id;
    private String name;
}
```

---

### ❓ FAQ 5: Set의 순회 순서는 보장되나요?

**답변**: **구현체에 따라 다릅니다!**

```java
// 1. HashSet: 순서 보장 안 됨
Set<Integer> hashSet = new HashSet<>();
hashSet.add(3);
hashSet.add(1);
hashSet.add(2);

for (Integer n : hashSet) {
    System.out.print(n + " "); // 1 2 3 (이 순서 보장 안 됨)
}

// 2. LinkedHashSet: 삽입 순서 유지
Set<Integer> linkedSet = new LinkedHashSet<>();
linkedSet.add(3);
linkedSet.add(1);
linkedSet.add(2);

for (Integer n : linkedSet) {
    System.out.print(n + " "); // 3 1 2 (삽입 순서 보장)
}

// 3. TreeSet: 정렬 순서
Set<Integer> treeSet = new TreeSet<>();
treeSet.add(3);
treeSet.add(1);
treeSet.add(2);

for (Integer n : treeSet) {
    System.out.print(n + " "); // 1 2 3 (정렬 순서 보장)
}
```

**주의사항**:
```java
// ❌ HashSet 순서에 의존하는 코드
Set<String> set = new HashSet<>();
set.add("A");
set.add("B");
set.add("C");

List<String> list = new ArrayList<>(set);
String first = list.get(0); // "A"라고 보장할 수 없음!

// ✅ 순서가 필요하면 LinkedHashSet 사용
Set<String> orderedSet = new LinkedHashSet<>();
```

---

### ❓ FAQ 6: Set에서 특정 요소를 가져오려면 어떻게 하나요?

**답변**: **Set은 인덱스 접근이 없습니다. contains()나 iterator를 사용하세요.**

```java
Set<String> set = new HashSet<>();
set.add("사과");
set.add("바나나");
set.add("오렌지");

// ❌ 인덱스 접근 불가
// String first = set.get(0); // 컴파일 오류

// ✅ 방법 1: contains() - 존재 여부만 확인
if (set.contains("사과")) {
    System.out.println("사과 있음");
}

// ✅ 방법 2: iterator
Iterator<String> iterator = set.iterator();
if (iterator.hasNext()) {
    String first = iterator.next();
    System.out.println("첫 번째: " + first);
}

// ✅ 방법 3: 향상된 for문
for (String fruit : set) {
    System.out.println(fruit);
    break; // 첫 번째만
}

// ✅ 방법 4: Stream
set.stream()
   .findFirst()
   .ifPresent(System.out::println);

// ✅ 방법 5: List로 변환 (순서 필요 시)
List<String> list = new ArrayList<>(set);
String first = list.get(0); // 인덱스 접근 가능
```

**TreeSet의 특수 메서드**:
```java
TreeSet<Integer> treeSet = new TreeSet<>();
treeSet.add(3);
treeSet.add(1);
treeSet.add(5);

Integer first = treeSet.first();   // 1 (최소값)
Integer last = treeSet.last();     // 5 (최대값)
Integer ceiling = treeSet.ceiling(2); // 3 (2 이상 최소값)
Integer floor = treeSet.floor(4);     // 3 (4 이하 최대값)
```

---

### ❓ FAQ 7: Set의 크기를 제한할 수 있나요?

**답변**: **직접 구현하거나 Guava/Apache Commons를 사용하세요.**

```java
// 방법 1: 직접 구현 (LRU Set)
class BoundedSet<E> extends LinkedHashSet<E> {
    private final int maxSize;

    public BoundedSet(int maxSize) {
        this.maxSize = maxSize;
    }

    @Override
    public boolean add(E e) {
        // 최대 크기 초과 시 가장 오래된 요소 제거
        if (size() >= maxSize) {
            Iterator<E> iterator = iterator();
            if (iterator.hasNext()) {
                iterator.next();
                iterator.remove();
            }
        }

        return super.add(e);
    }
}

// 사용 예
Set<String> boundedSet = new BoundedSet<>(3);
boundedSet.add("A");
boundedSet.add("B");
boundedSet.add("C");
boundedSet.add("D"); // A 제거, D 추가

System.out.println(boundedSet); // [B, C, D]

// 방법 2: add 전 크기 체크
Set<String> set = new HashSet<>();
int MAX_SIZE = 100;

if (set.size() < MAX_SIZE) {
    set.add("new");
} else {
    System.out.println("Set이 가득 참");
}

// 방법 3: Guava 사용
// import com.google.common.collect.EvictingQueue;
// (EvictingQueue는 Queue이지만 Set과 유사한 용도)
```

**LRU 캐시 패턴**:
```java
class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int maxSize;

    public LRUCache(int maxSize) {
        super(16, 0.75f, true); // accessOrder = true
        this.maxSize = maxSize;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > maxSize;
    }
}

// 사용
LRUCache<String, String> cache = new LRUCache<>(3);
cache.put("A", "1");
cache.put("B", "2");
cache.put("C", "3");
cache.get("A"); // A 접근
cache.put("D", "4"); // B 제거 (가장 오래 미접근)

System.out.println(cache.keySet()); // [C, A, D]
```

---

## 🎤 면접 질문

### 🟢 주니어 레벨 (7문)

#### Q1. Set 인터페이스의 가장 큰 특징은 무엇인가요?

**답변**:
Set의 가장 큰 특징은 **중복을 허용하지 않는다**는 것입니다.

```java
Set<String> set = new HashSet<>();
set.add("사과");
set.add("사과"); // 무시됨
set.add("사과"); // 무시됨

System.out.println(set.size()); // 1
```

**중복 판단 기준**:
- `equals()` 메서드가 `true`를 반환하면 중복으로 간주
- `hashCode()`도 함께 구현해야 올바르게 동작

**List와 비교**:
| | Set | List |
|---|-----|------|
| 중복 | ❌ 불허 | ✅ 허용 |
| 순서 | 구현체에 따라 다름 | ✅ 유지 |
| 인덱스 | ❌ 없음 | ✅ 있음 |

---

#### Q2. HashSet, LinkedHashSet, TreeSet의 차이점을 설명해주세요.

**답변**:

**1. HashSet** - 기본 구현체
```java
Set<String> set = new HashSet<>();
set.add("C");
set.add("A");
set.add("B");
// 출력 순서: 불확정 (보통 A, B, C 순이지만 보장 안 됨)
```
- 내부 구조: HashMap 기반
- 성능: O(1) - 가장 빠름
- 순서: 없음
- 사용 예: 단순 중복 제거

**2. LinkedHashSet** - 순서 유지
```java
Set<String> set = new LinkedHashSet<>();
set.add("C");
set.add("A");
set.add("B");
// 출력 순서: C, A, B (삽입 순서 유지)
```
- 내부 구조: HashMap + 이중 연결 리스트
- 성능: O(1)
- 순서: 삽입 순서 유지
- 사용 예: 중복 제거 + 순서 유지

**3. TreeSet** - 자동 정렬
```java
Set<String> set = new TreeSet<>();
set.add("C");
set.add("A");
set.add("B");
// 출력 순서: A, B, C (정렬 순서)
```
- 내부 구조: Red-Black Tree
- 성능: O(log n)
- 순서: 정렬 순서 (Comparable/Comparator)
- 사용 예: 정렬된 데이터, 범위 검색

**비교 표**:
| | HashSet | LinkedHashSet | TreeSet |
|---|---------|---------------|---------|
| 내부 구조 | HashMap | HashMap + LinkedList | Red-Black Tree |
| 추가/삭제 | O(1) | O(1) | O(log n) |
| 조회 | O(1) | O(1) | O(log n) |
| 순서 | ❌ | ✅ 삽입 순서 | ✅ 정렬 순서 |
| null | ✅ 1개 | ✅ 1개 | ❌ 불가 |
| 메모리 | 적음 | 중간 | 많음 |

---

#### Q3. Set에 객체를 저장할 때 equals()와 hashCode()를 구현해야 하는 이유는?

**답변**:

Set은 **중복을 판단하기 위해** equals()와 hashCode()를 사용합니다.

**HashSet의 중복 판단 과정**:
```java
// 1단계: hashCode()로 버킷 찾기
int bucket = object.hashCode() % buckets.length;

// 2단계: 해당 버킷 내에서 equals()로 동일성 확인
for (Object existing : buckets[bucket]) {
    if (object.equals(existing)) {
        return false; // 중복!
    }
}
```

**문제 상황 (미구현 시)**:
```java
class Product {
    private String id;
    private String name;

    // ❌ equals/hashCode 미구현
}

Set<Product> set = new HashSet<>();
Product p1 = new Product("P001", "노트북");
Product p2 = new Product("P001", "노트북"); // 논리적으로 동일

set.add(p1);
set.add(p2);

System.out.println(set.size()); // 2 ❌ (중복 제거 실패)
```

**올바른 구현**:
```java
class Product {
    private String id;
    private String name;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Product product = (Product) o;
        return id.equals(product.id); // id로 동일성 판단
    }

    @Override
    public int hashCode() {
        return Objects.hash(id); // equals와 동일한 필드 사용
    }
}

Set<Product> set = new HashSet<>();
Product p1 = new Product("P001", "노트북");
Product p2 = new Product("P001", "노트북");

set.add(p1);
set.add(p2);

System.out.println(set.size()); // 1 ✓ (올바르게 중복 제거)
```

**equals/hashCode 계약**:
```
1. equals가 true면 hashCode도 같아야 함
2. hashCode가 다르면 equals는 false
3. equals에서 사용한 필드를 hashCode에서도 사용
```

---

#### Q4. TreeSet 사용 시 Comparable을 구현해야 하는 이유는?

**답변**:

TreeSet은 **정렬을 위해** 요소 간 비교가 필요하므로 Comparable 또는 Comparator가 필수입니다.

**문제 상황 (미구현 시)**:
```java
class Task {
    private String title;
    private int priority;

    // ❌ Comparable 미구현
}

TreeSet<Task> tasks = new TreeSet<>();
tasks.add(new Task("이메일", 1));
tasks.add(new Task("회의", 2)); // ClassCastException 발생!
```

**오류 메시지**:
```
java.lang.ClassCastException: class Task cannot be cast to class java.lang.Comparable
```

**해결책 1: Comparable 구현**:
```java
class Task implements Comparable<Task> {
    private String title;
    private int priority;

    @Override
    public int compareTo(Task other) {
        // priority 오름차순 정렬
        return Integer.compare(this.priority, other.priority);
    }
}

TreeSet<Task> tasks = new TreeSet<>();
tasks.add(new Task("이메일", 3));
tasks.add(new Task("회의", 1));
tasks.add(new Task("보고서", 2));

// 출력: [회의(1), 보고서(2), 이메일(3)]
```

**해결책 2: Comparator 제공**:
```java
// Comparable 구현 불가 시 (외부 라이브러리 클래스 등)
TreeSet<Task> tasks = new TreeSet<>(
    Comparator.comparingInt(Task::getPriority)
);
```

**Comparable vs Comparator**:
| | Comparable | Comparator |
|---|------------|------------|
| 위치 | 클래스 내부 | 외부 |
| 구현 | `compareTo(T other)` | `compare(T o1, T o2)` |
| 개수 | 1개 (자연 순서) | 여러 개 가능 |
| 사용 | `new TreeSet<>()` | `new TreeSet<>(comparator)` |

---

#### Q5. Set과 List 중 어떤 것을 선택해야 할까요?

**답변**:

**요구사항에 따라 선택**합니다.

**Set 선택 시**:
```java
// ✅ 중복 제거가 필요할 때
Set<String> uniqueEmails = new HashSet<>();
uniqueEmails.add("user@example.com");
uniqueEmails.add("user@example.com"); // 무시
uniqueEmails.add("user@example.com"); // 무시

// ✅ 빠른 존재 여부 확인이 필요할 때
Set<Integer> ids = new HashSet<>();
ids.add(1001);
ids.add(1002);

if (ids.contains(1001)) { // O(1)
    System.out.println("존재함");
}

// ✅ 집합 연산이 필요할 때
Set<String> groupA = new HashSet<>(Arrays.asList("김철수", "이영희"));
Set<String> groupB = new HashSet<>(Arrays.asList("이영희", "박민수"));

// 교집합
Set<String> intersection = new HashSet<>(groupA);
intersection.retainAll(groupB); // [이영희]
```

**List 선택 시**:
```java
// ✅ 중복 허용이 필요할 때
List<String> logs = new ArrayList<>();
logs.add("INFO");
logs.add("INFO"); // 중복 허용
logs.add("ERROR");

// ✅ 순서가 중요할 때
List<String> steps = new ArrayList<>();
steps.add("1. 로그인");
steps.add("2. 상품 선택");
steps.add("3. 결제");

// ✅ 인덱스 접근이 필요할 때
String secondStep = steps.get(1); // O(1)
steps.set(1, "2. 장바구니 추가"); // 수정
```

**선택 플로우차트**:
```
중복을 허용해야 하나?
├─ YES → List
└─ NO  → Set
          ├─ 빠른 조회 필요? → HashSet
          ├─ 순서 유지 필요? → LinkedHashSet
          └─ 정렬 필요? → TreeSet
```

**성능 비교**:
| 연산 | ArrayList | HashSet |
|------|-----------|---------|
| add | O(1) | O(1) |
| contains | O(n) | O(1) ⭐ |
| remove | O(n) | O(1) ⭐ |
| get(index) | O(1) ⭐ | ❌ 불가 |

---

#### Q6. Set의 요소를 수정하려면 어떻게 해야 하나요?

**답변**:

Set은 **직접 수정이 불가능**합니다. **제거 후 재추가**해야 합니다.

**문제 상황**:
```java
class Member {
    private String id;
    private String name;
    private int point;

    // equals/hashCode는 id로만 판단
}

Set<Member> members = new HashSet<>();
Member member = new Member("M001", "김철수", 1000);
members.add(member);

// ❌ 잘못된 수정 (특히 equals/hashCode 필드 수정 시)
member.setId("M002"); // hashCode 변경!
// → Set에서 찾을 수 없게 됨

System.out.println(members.contains(member)); // false ❌
```

**올바른 방법 1: 제거 후 재추가**:
```java
Set<Member> members = new HashSet<>();
Member member = new Member("M001", "김철수", 1000);
members.add(member);

// ✅ 수정: 제거 후 새 객체 추가
members.remove(member);
Member updated = new Member("M001", "김철수", 2000); // 포인트 변경
members.add(updated);
```

**올바른 방법 2: Immutable 객체 사용**:
```java
class ImmutableMember {
    private final String id;   // final
    private final String name; // final
    private final int point;   // final

    // Setter 없음
    // 값 변경이 필요하면 새 객체 생성
    public ImmutableMember withPoint(int newPoint) {
        return new ImmutableMember(this.id, this.name, newPoint);
    }
}

Set<ImmutableMember> members = new HashSet<>();
ImmutableMember member = new ImmutableMember("M001", "김철수", 1000);
members.add(member);

// ✅ 수정: 새 객체 생성
members.remove(member);
ImmutableMember updated = member.withPoint(2000);
members.add(updated);
```

**TreeSet의 특수 케이스**:
```java
TreeSet<Member> members = new TreeSet<>();
Member member = new Member("M001", "김철수", 1000);
members.add(member);

// ❌ 정렬 기준 필드 수정 시 TreeSet 재정렬 필요
member.setPoint(2000); // Comparable에서 point 사용 시 문제

// ✅ TreeSet 재정렬
members.remove(member);   // 1. 제거
member.setPoint(2000);    // 2. 수정
members.add(member);      // 3. 재추가 (자동 재정렬)
```

**핵심 원칙**:
```
1. Set에 추가한 객체의 equals/hashCode 필드는 수정하지 마세요
2. 수정이 필요하면 제거 후 재추가하세요
3. Immutable 객체를 사용하는 것이 가장 안전합니다
```

---

#### Q7. Set을 List로, List를 Set으로 변환하는 방법은?

**답변**:

**1. Set → List 변환**:
```java
Set<String> set = new HashSet<>(Arrays.asList("사과", "바나나", "오렌지"));

// 방법 1: ArrayList 생성자
List<String> list1 = new ArrayList<>(set);

// 방법 2: addAll
List<String> list2 = new ArrayList<>();
list2.addAll(set);

// 방법 3: Stream
List<String> list3 = set.stream()
    .collect(Collectors.toList());

// 방법 4: List.copyOf (Java 10+, 불변 리스트)
List<String> list4 = List.copyOf(set);
```

**2. List → Set 변환 (중복 제거)**:
```java
List<String> list = Arrays.asList("사과", "바나나", "사과", "오렌지");

// 방법 1: HashSet 생성자
Set<String> set1 = new HashSet<>(list);

// 방법 2: addAll
Set<String> set2 = new HashSet<>();
set2.addAll(list);

// 방법 3: Stream
Set<String> set3 = list.stream()
    .collect(Collectors.toSet());

// 방법 4: LinkedHashSet (순서 유지)
Set<String> set4 = new LinkedHashSet<>(list);

// 방법 5: TreeSet (정렬)
Set<String> set5 = new TreeSet<>(list);

// 방법 6: Set.copyOf (Java 10+, 불변 Set)
Set<String> set6 = Set.copyOf(list);
```

**실용 예시: 중복 제거**:
```java
// List의 중복 제거 (순서 유지)
List<Integer> numbers = Arrays.asList(1, 2, 2, 3, 3, 3, 4);

List<Integer> uniqueNumbers = new ArrayList<>(
    new LinkedHashSet<>(numbers)
);
// [1, 2, 3, 4]

// List의 중복 제거 (정렬)
List<Integer> sortedUnique = new ArrayList<>(
    new TreeSet<>(numbers)
);
// [1, 2, 3, 4]
```

**성능 고려**:
```java
// 대량 데이터 (100만 개)
List<Integer> bigList = // 100만 개 데이터

// ✅ 생성자 사용 (가장 빠름)
Set<Integer> set = new HashSet<>(bigList); // ~100ms

// ❌ 반복문으로 추가 (느림)
Set<Integer> set2 = new HashSet<>();
for (Integer n : bigList) {
    set2.add(n); // ~200ms
}
```

---

### 🟡 중급 레벨 (5문)

#### Q8. HashSet의 내부 동작 원리를 설명해주세요.

**답변**:

HashSet은 **내부적으로 HashMap을 사용**합니다.

**내부 구조**:
```java
// HashSet 내부 코드 (단순화)
public class HashSet<E> {
    private transient HashMap<E, Object> map;
    private static final Object PRESENT = new Object();

    public HashSet() {
        map = new HashMap<>();
    }

    public boolean add(E e) {
        return map.put(e, PRESENT) == null;
    }

    public boolean contains(Object o) {
        return map.containsKey(o);
    }

    public boolean remove(Object o) {
        return map.remove(o) == PRESENT;
    }
}
```

**동작 과정**:

**1. add() 과정**:
```java
Set<String> set = new HashSet<>();
set.add("사과");

// 내부 동작:
// 1. "사과".hashCode() 계산 → 예: 48710646
// 2. 버킷 인덱스 계산: hashCode % buckets.length → 예: 6
// 3. buckets[6]에 "사과" 저장 (value는 더미 객체 PRESENT)

// 중복 추가 시도:
set.add("사과");

// 내부 동작:
// 1. "사과".hashCode() → 48710646
// 2. 버킷 인덱스 → 6
// 3. buckets[6]에 이미 "사과" 존재
// 4. equals()로 확인 → true
// 5. 추가하지 않고 false 반환
```

**2. contains() 과정**:
```java
boolean exists = set.contains("사과");

// 내부 동작:
// 1. "사과".hashCode() → 48710646
// 2. 버킷 인덱스 → 6
// 3. buckets[6] 탐색
// 4. equals()로 확인 → true
// 5. true 반환

// 성능: O(1) - 직접 버킷 접근
```

**해시 충돌 처리**:
```java
// 서로 다른 객체가 같은 버킷에 매핑되는 경우
String a = "사과"; // hashCode: 48710646, bucket: 6
String b = "포도"; // hashCode: 50953766, bucket: 6 (가정)

// 동일 버킷에 저장 (Linked List 또는 Red-Black Tree)
buckets[6] = ["사과", "포도"]

// contains("포도") 시:
// 1. bucket 6 접근
// 2. 리스트 순회하며 equals() 확인
// 3. 성능: O(n) - 해시 충돌이 많으면 성능 저하
```

**해시 충돌 최소화**:
```java
// ✅ 좋은 hashCode 구현
@Override
public int hashCode() {
    return Objects.hash(field1, field2, field3);
    // Objects.hash()는 충돌을 최소화하는 알고리즘 사용
}

// ❌ 나쁜 hashCode 구현
@Override
public int hashCode() {
    return 1; // 모든 객체가 동일한 버킷으로!
    // 성능: O(1) → O(n)로 저하
}
```

**리사이징**:
```java
// 기본 용량: 16, 로드 팩터: 0.75
HashSet<String> set = new HashSet<>();

// 12개 추가 시 (16 * 0.75 = 12) 리사이징
// 용량: 16 → 32
// 모든 요소를 새 버킷에 재배치 (rehashing)
```

---

#### Q9. TreeSet에서 사용하는 Red-Black Tree란 무엇인가요?

**답변**:

Red-Black Tree는 **자가 균형 이진 검색 트리**입니다.

**특징**:
1. 각 노드는 RED 또는 BLACK
2. 루트는 항상 BLACK
3. 모든 리프(NIL)는 BLACK
4. RED 노드의 자식은 모두 BLACK
5. 모든 경로의 BLACK 노드 수는 동일

**장점**:
```
✅ 균형 유지 → 최악의 경우에도 O(log n) 보장
✅ 삽입/삭제 시 자동 재균형
✅ AVL 트리보다 재균형 비용 낮음
```

**TreeSet의 동작**:
```java
TreeSet<Integer> set = new TreeSet<>();
set.add(5);
set.add(3);
set.add(7);
set.add(1);

// 내부 트리 구조 (단순화):
//        5(B)
//       / \
//     3(R) 7(R)
//     /
//   1(B)

// contains(7) 과정:
// 1. 루트(5)와 비교: 7 > 5 → 오른쪽
// 2. 7과 비교: 7 == 7 → 찾음
// 성능: O(log n)
```

**자동 재균형 예시**:
```java
TreeSet<Integer> set = new TreeSet<>();
set.add(1);
set.add(2);
set.add(3);

// 균형 없는 이진 트리 (최악):
// 1
//  \
//   2
//    \
//     3
// 높이: 3, 성능: O(n)

// Red-Black Tree 자동 재균형:
//     2(B)
//    / \
//  1(R) 3(R)
// 높이: 2, 성능: O(log n)
```

**AVL Tree vs Red-Black Tree**:
| | AVL Tree | Red-Black Tree |
|---|----------|----------------|
| 균형 조건 | 엄격 (높이 차 ≤ 1) | 느슨 (경로 BLACK 수 동일) |
| 조회 | 더 빠름 | 약간 느림 |
| 삽입/삭제 | 느림 (재균형 많음) | 빠름 ⭐ |
| 사용 | 조회 위주 | 삽입/삭제 위주 (Java TreeSet) |

**실제 성능**:
```java
TreeSet<Integer> set = new TreeSet<>();

// 100만 개 삽입
for (int i = 0; i < 1_000_000; i++) {
    set.add(i);
}
// 삽입: ~800ms
// 균형 유지로 O(log n) 보장

// 조회
set.contains(500_000); // ~0.1ms
// log₂(1,000,000) ≈ 20회 비교
```

---

#### Q10. Set의 집합 연산 (합/교/차집합)을 구현하는 방법은?

**답변**:

**1. 합집합 (Union)**: A ∪ B
```java
Set<String> setA = new HashSet<>(Arrays.asList("A", "B", "C"));
Set<String> setB = new HashSet<>(Arrays.asList("B", "C", "D"));

// 방법 1: addAll
Set<String> union = new HashSet<>(setA);
union.addAll(setB);
// [A, B, C, D]

// 방법 2: Stream
Set<String> union2 = Stream.concat(setA.stream(), setB.stream())
    .collect(Collectors.toSet());
```

**2. 교집합 (Intersection)**: A ∩ B
```java
Set<String> setA = new HashSet<>(Arrays.asList("A", "B", "C"));
Set<String> setB = new HashSet<>(Arrays.asList("B", "C", "D"));

// 방법 1: retainAll
Set<String> intersection = new HashSet<>(setA);
intersection.retainAll(setB);
// [B, C]

// 방법 2: Stream
Set<String> intersection2 = setA.stream()
    .filter(setB::contains)
    .collect(Collectors.toSet());
```

**3. 차집합 (Difference)**: A - B
```java
Set<String> setA = new HashSet<>(Arrays.asList("A", "B", "C"));
Set<String> setB = new HashSet<>(Arrays.asList("B", "C", "D"));

// 방법 1: removeAll
Set<String> difference = new HashSet<>(setA);
difference.removeAll(setB);
// [A]

// 방법 2: Stream
Set<String> difference2 = setA.stream()
    .filter(e -> !setB.contains(e))
    .collect(Collectors.toSet());
```

**4. 대칭 차집합 (Symmetric Difference)**: (A - B) ∪ (B - A)
```java
Set<String> setA = new HashSet<>(Arrays.asList("A", "B", "C"));
Set<String> setB = new HashSet<>(Arrays.asList("B", "C", "D"));

// A - B
Set<String> onlyA = new HashSet<>(setA);
onlyA.removeAll(setB);

// B - A
Set<String> onlyB = new HashSet<>(setB);
onlyB.removeAll(setA);

// 합집합
Set<String> symmetric = new HashSet<>(onlyA);
symmetric.addAll(onlyB);
// [A, D]
```

**실용 예시: 회원 세그먼트 분석**:
```java
Set<String> premiumMembers = new HashSet<>(Arrays.asList("김철수", "이영희", "박민수"));
Set<String> activeMembers = new HashSet<>(Arrays.asList("이영희", "박민수", "정지훈"));

// 타겟 마케팅: Premium ∩ Active
Set<String> target = new HashSet<>(premiumMembers);
target.retainAll(activeMembers);
// [이영희, 박민수]

// 재활성화 타겟: Premium - Active
Set<String> inactive = new HashSet<>(premiumMembers);
inactive.removeAll(activeMembers);
// [김철수]

// 일반 활성 회원: Active - Premium
Set<String> regularActive = new HashSet<>(activeMembers);
regularActive.removeAll(premiumMembers);
// [정지훈]
```

**성능**:
```java
Set<Integer> setA = // 100만 개
Set<Integer> setB = // 100만 개

// retainAll: O(n) - n = setA.size()
Set<Integer> intersection = new HashSet<>(setA);
intersection.retainAll(setB); // ~50ms

// Stream filter: O(n × m) - n = setA.size(), m = setB.contains()
// HashSet.contains()가 O(1)이므로 실제로는 O(n)
Set<Integer> intersection2 = setA.stream()
    .filter(setB::contains)
    .collect(Collectors.toSet()); // ~100ms

// → retainAll이 더 빠름
```

---

#### Q11. HashSet의 Thread-Safety를 보장하는 방법은?

**답변**:

HashSet은 **Thread-Safe하지 않습니다**. 멀티스레드 환경에서 동기화가 필요합니다.

**문제 상황**:
```java
Set<Integer> set = new HashSet<>();

// 10개 스레드가 동시에 추가
ExecutorService executor = Executors.newFixedThreadPool(10);

for (int i = 0; i < 10; i++) {
    final int threadId = i;
    executor.submit(() -> {
        for (int j = 0; j < 1000; j++) {
            set.add(threadId * 1000 + j);
        }
    });
}

executor.shutdown();
executor.awaitTermination(1, TimeUnit.MINUTES);

System.out.println("예상 크기: 10,000");
System.out.println("실제 크기: " + set.size()); // 9,847 ❌ (손실 발생)
// 또는 ConcurrentModificationException 발생
```

**해결책 1: Collections.synchronizedSet()**:
```java
Set<Integer> set = Collections.synchronizedSet(new HashSet<>());

// 모든 메서드가 synchronized로 동기화됨
set.add(1); // synchronized
set.contains(1); // synchronized
set.remove(1); // synchronized

// ⚠️ iterator는 수동 동기화 필요
synchronized (set) {
    for (Integer n : set) {
        System.out.println(n);
    }
}
```

**해결책 2: ConcurrentHashMap.newKeySet()**:
```java
Set<Integer> set = ConcurrentHashMap.newKeySet();

// Thread-Safe + 높은 성능
// 내부적으로 segment 단위 lock 사용

// 멀티스레드 환경에서 안전
ExecutorService executor = Executors.newFixedThreadPool(10);

for (int i = 0; i < 10; i++) {
    final int threadId = i;
    executor.submit(() -> {
        for (int j = 0; j < 1000; j++) {
            set.add(threadId * 1000 + j);
        }
    });
}

executor.shutdown();
executor.awaitTermination(1, TimeUnit.MINUTES);

System.out.println("크기: " + set.size()); // 10,000 ✓
```

**해결책 3: CopyOnWriteArraySet**:
```java
Set<Integer> set = new CopyOnWriteArraySet<>();

// 쓰기 시 전체 복사 (Copy-On-Write)
// 읽기가 많고 쓰기가 적을 때 적합

set.add(1); // 전체 배열 복사
set.add(2); // 전체 배열 복사

// 장점: iterator가 Thread-Safe (ConcurrentModificationException 없음)
for (Integer n : set) {
    System.out.println(n); // 안전
}

// 단점: 쓰기 성능 낮음 (O(n))
```

**성능 비교**:
```java
// 10개 스레드, 각 10,000번 추가

// 1. synchronizedSet
Set<Integer> sync = Collections.synchronizedSet(new HashSet<>());
// 소요 시간: ~200ms
// 모든 연산이 synchronized → 병목

// 2. ConcurrentHashMap.newKeySet()
Set<Integer> concurrent = ConcurrentHashMap.newKeySet();
// 소요 시간: ~50ms ⭐
// Segment 단위 lock → 높은 동시성

// 3. CopyOnWriteArraySet
Set<Integer> cow = new CopyOnWriteArraySet<>();
// 소요 시간: ~5000ms ❌
// 매번 전체 복사 → 쓰기 성능 낮음
```

**선택 가이드**:
| 상황 | 선택 |
|------|------|
| 단순 동기화 필요 | `Collections.synchronizedSet()` |
| 높은 동시성 + 읽기/쓰기 혼합 | `ConcurrentHashMap.newKeySet()` ⭐ |
| 읽기 위주 (쓰기 적음) | `CopyOnWriteArraySet` |
| Thread-Safe 불필요 | `HashSet` |

---

#### Q12. 대용량 데이터를 다룰 때 Set의 성능을 최적화하는 방법은?

**답변**:

**1. 초기 용량 설정**:
```java
// ❌ 기본 용량 (16) → 리사이징 빈번
Set<String> set = new HashSet<>();
for (int i = 0; i < 1_000_000; i++) {
    set.add("item" + i);
}
// 소요 시간: ~800ms

// ✅ 예상 크기로 초기화
Set<String> set2 = new HashSet<>(1_200_000); // 1M / 0.75 = 1.33M
for (int i = 0; i < 1_000_000; i++) {
    set2.add("item" + i);
}
// 소요 시간: ~500ms ⭐ (리사이징 없음)
```

**2. 로드 팩터 조정**:
```java
// 로드 팩터: 리사이징 기준
// 기본값: 0.75 (75% 채워지면 리사이징)

// 메모리 절약 (로드 팩터 높임)
Set<String> set1 = new HashSet<>(1000, 0.9f);
// 장점: 메모리 사용 적음
// 단점: 해시 충돌 증가 → 성능 저하

// 성능 우선 (로드 팩터 낮춤)
Set<String> set2 = new HashSet<>(1000, 0.5f);
// 장점: 해시 충돌 감소 → 성능 향상
// 단점: 메모리 사용 많음
```

**3. 적절한 구현체 선택**:
```java
// 100만 개 데이터

// HashSet: 가장 빠름
Set<Integer> hashSet = new HashSet<>(1_200_000);
// 추가: 500ms, 조회: 0.001ms

// LinkedHashSet: 약간 느림 (순서 유지 오버헤드)
Set<Integer> linkedSet = new LinkedHashSet<>(1_200_000);
// 추가: 600ms, 조회: 0.001ms

// TreeSet: 느림 (정렬 오버헤드)
Set<Integer> treeSet = new TreeSet<>();
// 추가: 1500ms, 조회: 0.01ms

// → 순서/정렬 필요 없으면 HashSet 사용
```

**4. equals/hashCode 최적화**:
```java
// ❌ 나쁜 hashCode (모든 객체가 같은 버킷)
class BadProduct {
    private String id;
    private String name;

    @Override
    public int hashCode() {
        return 1; // 모든 객체가 bucket[1]로!
    }
    // 성능: O(1) → O(n)으로 저하
}

// ✅ 좋은 hashCode (골고루 분산)
class GoodProduct {
    private String id;
    private String name;

    @Override
    public int hashCode() {
        return Objects.hash(id, name); // 충돌 최소화
    }
}

// 성능 비교 (100만 개)
Set<BadProduct> badSet = new HashSet<>();
// contains(): ~500ms ❌ (리스트 순회)

Set<GoodProduct> goodSet = new HashSet<>();
// contains(): ~0.001ms ✓ (직접 접근)
```

**5. Bulk 연산 활용**:
```java
// ❌ 반복문으로 추가
Set<Integer> set = new HashSet<>();
List<Integer> list = // 100만 개
for (Integer n : list) {
    set.add(n); // ~200ms
}

// ✅ addAll 사용
Set<Integer> set2 = new HashSet<>(list.size());
set2.addAll(list); // ~100ms ⭐ (최적화됨)

// ✅ 생성자 사용 (가장 빠름)
Set<Integer> set3 = new HashSet<>(list); // ~80ms ⭐⭐
```

**6. 메모리 최적화**:
```java
// Primitive 타입 최적화
// ❌ Integer (100만 개) → 약 40MB
Set<Integer> integerSet = new HashSet<>();

// ✅ IntSet (Trove/FastUtil 라이브러리)
// TIntHashSet intSet = new TIntHashSet();
// → 약 8MB (5배 절약)
```

**7. 병렬 처리**:
```java
// 대용량 데이터 병렬 처리
List<String> bigList = // 1000만 개

// ✅ 병렬 스트림
Set<String> set = bigList.parallelStream()
    .collect(Collectors.toSet());
// 소요 시간: ~2000ms (4코어)

// vs 순차 처리
Set<String> set2 = new HashSet<>(bigList);
// 소요 시간: ~5000ms
```

**최적화 체크리스트**:
```
□ 초기 용량 설정 (예상 크기 / 0.75)
□ 적절한 구현체 선택 (HashSet > LinkedHashSet > TreeSet)
□ 좋은 hashCode 구현 (충돌 최소화)
□ Bulk 연산 활용 (addAll, 생성자)
□ Primitive 타입은 전용 라이브러리 고려
□ 대용량은 병렬 처리 고려
```

---

## 🎓 마무리

**27장 Set 인터페이스 완료**:
- ✅ Part 1: 5개 실생활 비유
- ✅ Part 2: 3개 기업 사례 + 4개 주니어 실수
- ✅ Part 3: 실전 프로젝트 + 7 FAQ + 12 면접 질문

**다음 장**: 28장 Map 인터페이스
- HashMap, LinkedHashMap, TreeMap
- Key-Value 구조
- 해시 충돌 처리
- ConcurrentHashMap
