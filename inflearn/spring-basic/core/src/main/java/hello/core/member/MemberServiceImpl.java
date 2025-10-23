package hello.core.member;

public class MemberServiceImpl implements MemberService {

    //dip, ocp 위반
    private final MemberRepository memberRepository = new MemoryMemberRepository();

    //회원가입
    public void join(Member member) {
        memberRepository.save(member);
    }

    //멤버 찾기
    public Member findMember(Long memberId) {
        return memberRepository.findById(memberId);
    }
}
