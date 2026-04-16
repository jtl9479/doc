# 학습 02. DB(Oracle)/JPA 심화 + 튜닝

## Step 목차

| Step | 항목 | 카테고리 |
|------|------|----------|
| Step 1 | 인덱스 원리 — B-Tree, IOT, Bitmap, 커버링 인덱스 | Oracle 튜닝 |
| Step 2 | 실행계획 분석 — EXPLAIN PLAN, DBMS_XPLAN, CBO | Oracle 튜닝 |
| Step 3 | Oracle 힌트 — LEADING, USE_NL, USE_HASH, INDEX 등 | Oracle 튜닝 |
| Step 4 | 조인 방식 — Nested Loop, Hash Join, Sort Merge Join | Oracle 튜닝 |
| Step 5 | 트랜잭션 격리 수준 — READ COMMITTED ~ SERIALIZABLE | 트랜잭션 |
| Step 6 | Oracle MVCC — Undo Segment, SCN, CR Copy | 트랜잭션 |
| Step 7 | 락 — Row Lock, Table Lock, 데드락, Enqueue | 트랜잭션 |
| Step 8 | AWR / ASH / Statspack — 성능 분석 보고서 | 성능 분석 |
| Step 9 | SQL 튜닝 실전 — 바인드 변수, 부분 범위 처리, 소트 튜닝 | 튜닝 실전 |
| Step 10 | 파티셔닝 — RANGE/LIST/HASH/Composite | 아키텍처 |
| Step 11 | 레플리카 — Data Guard, RAC 개념 | 아키텍처 |
| Step 12 | 커넥션 풀 — HikariCP 튜닝 | 인프라 |
| Step 13 | JPA 개요 — ORM 개념, JPA vs MyBatis vs JDBC | JPA 기초 |
| Step 14 | 엔티티 매핑 — @Entity, @Id, @Column, @GeneratedValue | JPA 기초 |
| Step 15 | 연관관계 매핑 — @ManyToOne, @OneToMany, 양방향 | JPA 기초 |
| Step 16 | 상속 매핑 — @Inheritance, @MappedSuperclass | JPA 기초 |
| Step 17 | JPQL 기본 — SELECT, JOIN, 페이징, 집합 함수 | JPA 기초 |
| Step 18 | JPA 영속성 컨텍스트 내부 동작 | JPA 심화 |
| Step 19 | JPA N+1 문제 + 해결 | JPA 심화 |
| Step 20 | JPA 변경 감지, 지연 로딩, 프록시 | JPA 심화 |
| Step 21 | QueryDSL / Native Query 최적화 | JPA 심화 |
| Step 22 | MySQL/PostgreSQL 차이 정리 (면접 대비) | 면접 대비 |

---

## 1. 개요

**현재 수준**: Oracle + MyBatis/JPA로 ERP 시스템 개발 중. SQL 작성 가능하나 실행계획 분석·튜닝·트랜잭션 설계는 깊이 부족.
**학습 목표**: 실행계획을 보고 "왜 느린지, 어떻게 고칠지" 즉시 판단 가능. 트랜잭션 격리 수준을 설계 가능. JPA의 내부 동작을 이해하고 성능 문제를 사전에 식별 가능.
**분기 배정**: 1분기 (2026.04 ~ 2026.06)

---

## 2. 학습 순서 + 세부 항목

---

### Step 1. 인덱스 원리 — B-Tree, IOT, Bitmap, 커버링 인덱스

| 학습 항목 | 학습 목표 |
|----------|----------|
| B-Tree 인덱스 구조 | Root → Branch → Leaf 3단 구조를 그림으로 그릴 수 있음. Leaf 노드가 정렬된 연결 리스트(Double Linked List)인 이유(Range Scan)를 설명 가능. |
| 인덱스 스캔 종류 | Index Range Scan, Index Full Scan, Index Unique Scan, Index Skip Scan, Index Fast Full Scan 각각의 동작 조건과 차이를 설명 가능. |
| 인덱스 선두 컬럼의 중요성 | 복합 인덱스에서 선두 컬럼이 WHERE 조건에 없으면 Range Scan이 안 되는 이유(정렬 순서)를 설명 가능. "인덱스를 만들었는데 왜 안 타나요?"에 답변 가능. |
| 인덱스 컬럼 순서 설계 | 복합 인덱스의 컬럼 순서를 결정하는 기준(동치 조건 선행, 범위 조건 후행, 소트 연산 대체)을 설명 + 적용 가능. |
| IOT (Index-Organized Table) | 일반 테이블과의 차이(데이터가 인덱스 리프에 저장), 언제 쓰는지(PK 기반 조회가 대부분인 경우), InnoDB 클러스터드 인덱스와의 유사성을 설명 가능. |
| Bitmap Index | 동작 원리(비트 벡터 AND/OR 연산), 카디널리티가 낮은 컬럼에 적합한 이유, DML이 많은 테이블에 부적합한 이유(비트맵 전체 잠금)를 설명 가능. |
| 커버링 인덱스 (Covered Index) | 테이블 액세스 없이 인덱스만으로 쿼리를 처리하는 원리를 설명 가능. 실행계획에서 "TABLE ACCESS BY INDEX ROWID" 유무로 판단 가능. |
| 인덱스 설계 시 고려사항 | 인덱스 생성 비용(DML 성능 저하, 저장 공간), 과도한 인덱스의 부작용, 불필요한 인덱스 식별 방법을 설명 가능. |

---

### Step 2. 실행계획 분석 — EXPLAIN PLAN, DBMS_XPLAN, CBO

| 학습 항목 | 학습 목표 |
|----------|----------|
| EXPLAIN PLAN / DBMS_XPLAN 사용법 | `EXPLAIN PLAN FOR ...` + `SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY)`, `DBMS_XPLAN.DISPLAY_CURSOR` 사용 가능. |
| 실행계획 읽는 법 | 들여쓰기 기반 트리 구조를 위에서 아래로, 같은 레벨이면 위의 것이 먼저 실행됨을 이해. Id, Operation, Name, Rows, Bytes, Cost 각 컬럼의 의미를 설명 가능. |
| CBO (Cost-Based Optimizer) | 옵티마이저가 통계 정보(테이블 행 수, 컬럼 분포도, 인덱스 클러스터링 팩터)를 기반으로 비용을 산출하는 원리를 개념 수준으로 설명 가능. |
| 통계 정보의 중요성 | 통계가 오래되면 실행계획이 잘못 수립되는 이유를 설명 가능. `DBMS_STATS.GATHER_TABLE_STATS` 사용 시점과 방법을 알고 있음. |
| Predicate Information | Access Predicate(인덱스 접근 조건)와 Filter Predicate(필터링 조건)의 차이를 설명 가능. Filter가 많으면 비효율인 이유를 설명 가능. |
| 실행계획에서 비효율 식별 | TABLE ACCESS FULL(대량 데이터에서), TABLE ACCESS BY INDEX ROWID + 과도한 블록 I/O, SORT ORDER BY(인덱스로 대체 가능한 경우), HASH JOIN(작은 테이블인데 NESTED LOOP가 나은 경우) 등 비효율 패턴을 식별 가능. |

---

### Step 3. Oracle 힌트 — LEADING, USE_NL, USE_HASH, INDEX 등

| 학습 항목 | 학습 목표 |
|----------|----------|
| 힌트의 역할과 사용 원칙 | 옵티마이저가 최적의 실행계획을 못 찾을 때 개발자가 강제하는 수단. 남용하면 안 되는 이유(통계 변경 시 비효율 고정)를 설명 가능. |
| LEADING 힌트 | 조인 순서를 강제. `/*+ LEADING(a b c) */` — 어떤 테이블부터 조인할지 지정. 드라이빙 테이블 선택이 성능에 미치는 영향을 설명 가능. |
| USE_NL / USE_HASH / USE_MERGE | Nested Loop Join, Hash Join, Sort Merge Join을 각각 강제. 언제 어떤 조인을 선택하는지 판단 기준(Step 4에서 상세)과 연계하여 힌트 적용 가능. |
| INDEX / INDEX_RS / NO_INDEX | 특정 인덱스 사용 강제/금지. 옵티마이저가 잘못된 인덱스를 선택할 때 교정 가능. |
| FULL | 테이블 풀 스캔 강제. 대량 데이터 배치에서 인덱스보다 풀 스캔이 효율적인 경우 판단 가능. |
| ORDERED | FROM 절에 기술된 순서대로 조인 강제. LEADING과의 차이를 설명 가능. |
| PARALLEL | 병렬 처리 강제. 언제 쓰면 좋고(대량 배치), 언제 쓰면 안 되는지(OLTP) 설명 가능. |
| 힌트 적용 전후 비교 | 같은 쿼리에 힌트 있을 때/없을 때 실행계획 + 수행 시간을 비교하여 효과를 판단 가능. |

---

### Step 4. 조인 방식 — Nested Loop, Hash Join, Sort Merge Join

| 학습 항목 | 학습 목표 |
|----------|----------|
| Nested Loop Join (NL Join) | 동작 원리(드라이빙 테이블의 각 행마다 내부 테이블 반복 탐색)를 설명 가능. 소량 데이터 + 인덱스 존재 시 최적인 이유를 설명 가능. 랜덤 I/O가 발생하는 이유를 설명 가능. |
| Hash Join | 동작 원리(빌드 단계: 작은 테이블을 해시 테이블로 / 프로브 단계: 큰 테이블에서 해시 매칭)를 설명 가능. 대량 데이터 + 동치 조인(=)에서 최적인 이유를 설명 가능. PGA 메모리 사용과 Temp 영역 스필의 관계를 설명 가능. |
| Sort Merge Join | 동작 원리(양쪽 정렬 후 병합)를 설명 가능. 비동치 조인(>, <, BETWEEN)에서 Hash Join을 쓸 수 없을 때 사용됨을 설명 가능. |
| 조인 방식 선택 기준 | 데이터 크기, 인덱스 유무, 조인 조건 유형(동치/범위), 응답 시간 vs 처리량에 따라 NL/Hash/Sort Merge를 판단하는 기준을 설명 가능. |
| 드라이빙 테이블 선택 | NL Join에서 드라이빙 테이블이 작아야 하는 이유(반복 횟수 최소화), 잘못 선택하면 성능이 급락하는 사례를 설명 가능. |

---

### Step 5. 트랜잭션 격리 수준 — READ COMMITTED ~ SERIALIZABLE

| 학습 항목 | 학습 목표 |
|----------|----------|
| 트랜잭션 ACID | Atomicity, Consistency, Isolation, Durability 각각을 설명 가능. |
| 이상 현상 3가지 | Dirty Read, Non-Repeatable Read, Phantom Read 각각의 발생 시나리오를 구체적 예시로 설명 가능. |
| READ COMMITTED | Oracle 기본 격리 수준. 커밋된 데이터만 읽음. Non-Repeatable Read가 발생할 수 있는 시나리오를 설명 가능. 대부분의 OLTP에 적합한 이유를 설명 가능. |
| REPEATABLE READ | 같은 트랜잭션 내에서 같은 데이터를 읽으면 항상 같은 결과. Oracle에서는 직접 지원하지 않고 SELECT FOR UPDATE 또는 SERIALIZABLE로 대체하는 이유를 설명 가능. |
| SERIALIZABLE | 가장 강한 격리. Phantom Read까지 방지. 동시성이 크게 떨어지는 이유를 설명 가능. 언제 써야 하는지(금융 결산, 재고 차감 등 정합성 필수) 판단 가능. |
| 격리 수준 선택 기준 | 정합성 vs 동시성 트레이드오프를 이해하고, 업무 요구사항에 맞는 격리 수준을 설계 가능. |
| Lost Update (갱신 분실) | 두 트랜잭션이 동시에 같은 데이터를 수정할 때 한쪽 변경이 사라지는 문제를 시나리오로 설명 가능. 격리 수준만으로는 해결되지 않는 이유(READ COMMITTED에서도 발생)를 설명 가능. |
| Pessimistic Lock (비관적 락) | SELECT FOR UPDATE로 행을 먼저 잠그는 방식. 충돌이 빈번한 경우 적합. 동시성 저하 + 데드락 위험이 있는 트레이드오프를 설명 가능. JPA에서 `LockModeType.PESSIMISTIC_WRITE` 사용법을 알고 있음. |
| Optimistic Lock (낙관적 락) | 충돌이 드문 경우 적합. 변경 시점에 버전을 비교하여 충돌을 감지하는 방식. JPA `@Version` 어노테이션의 동작 원리(UPDATE ... WHERE id = ? AND version = ?)를 설명 가능. `OptimisticLockException` 발생 시 대응(재시도, 사용자 알림)을 설명 가능. |
| Optimistic vs Pessimistic 선택 기준 | 충돌 빈도가 낮으면 Optimistic(성능 우수), 높으면 Pessimistic(정합성 확실). ERP에서의 실무 판단 기준(예: 재고 차감은 Pessimistic, 게시글 수정은 Optimistic)을 설명 가능. |

---

### Step 6. Oracle MVCC — Undo Segment, SCN, CR Copy

| 학습 항목 | 학습 목표 |
|----------|----------|
| MVCC 개념 | 읽기와 쓰기가 서로를 블로킹하지 않는 원리를 설명 가능. "Oracle에서 SELECT는 락을 잡지 않는다"의 이유를 설명 가능. |
| SCN (System Change Number) | 모든 변경에 부여되는 논리적 타임스탬프. 트랜잭션 시작 시점의 SCN을 기준으로 읽기 일관성을 보장하는 메커니즘을 설명 가능. |
| Undo Segment | 변경 전 데이터를 Undo에 저장하는 이유(읽기 일관성 + 롤백)를 설명 가능. |
| CR Copy (Consistent Read Copy) | 다른 트랜잭션이 변경 중인 블록을 읽을 때 Undo를 이용해 변경 전 상태의 CR Copy를 생성하는 과정을 설명 가능. |
| ORA-01555 (Snapshot Too Old) | Undo가 덮어씌워져 CR Copy를 못 만들 때 발생. 원인(장시간 쿼리 + 짧은 Undo Retention)과 대응(Undo Retention 확대, 쿼리 최적화)을 설명 가능. |
| MySQL InnoDB MVCC와의 차이 | MySQL도 Undo Log 기반 MVCC. 차이점(Oracle은 Undo Tablespace, MySQL은 Undo Log in System Tablespace)을 개념 수준 설명 가능. |

---

### Step 7. 락 — Row Lock, Table Lock, 데드락, Enqueue

| 학습 항목 | 학습 목표 |
|----------|----------|
| Oracle 락의 종류 | Row Lock(TX Lock), Table Lock(TM Lock)의 차이를 설명 가능. Oracle은 행 수준 락이 기본이고 에스컬레이션이 없는 이유를 설명 가능. |
| SELECT FOR UPDATE | 행 수준 배타적 락 획득. NOWAIT, WAIT N, SKIP LOCKED 옵션의 차이와 용도를 설명 가능. |
| DML과 락 | INSERT, UPDATE, DELETE 시 자동으로 잡히는 락의 범위를 설명 가능. UPDATE 시 WHERE 조건에 해당하는 행만 락이 잡히는 이유를 설명 가능. |
| 데드락 (Deadlock) | 발생 메커니즘(트랜잭션 A가 행1 잠금 + 행2 대기, 트랜잭션 B가 행2 잠금 + 행1 대기)을 설명 가능. Oracle이 데드락을 자동 감지하고 한쪽을 롤백하는 동작을 설명 가능. ORA-00060 에러 해석 가능. |
| 데드락 방지 전략 | 락 획득 순서 일관성, 트랜잭션 짧게 유지, SELECT FOR UPDATE NOWAIT 활용 등을 설명 + 적용 가능. |
| Enqueue 대기 | V$LOCK, V$SESSION에서 락 대기 현황 조회 방법. 어떤 세션이 누구를 블로킹하는지 식별 가능. |
| 락 관련 트러블슈팅 | "특정 화면이 갑자기 멈춤" → 락 대기 의심 → V$LOCK/V$SESSION 조회 → 블로커 식별 → 원인 분석 순서를 설명 가능. |

---

### Step 8. AWR / ASH / Statspack — 성능 분석 보고서

| 학습 항목 | 학습 목표 |
|----------|----------|
| AWR (Automatic Workload Repository) | AWR이 무엇인지(주기적 성능 스냅샷 수집), 스냅샷 생성/조회 방법을 알고 있음. |
| AWR 리포트 핵심 섹션 | Load Profile(초당 트랜잭션, 물리 읽기), Top 5 Timed Events(가장 오래 걸린 대기 이벤트), SQL ordered by Elapsed Time(느린 SQL Top 10), Instance Efficiency Percentages(Buffer Cache Hit Ratio 등)를 읽고 해석 가능. |
| Top SQL 식별 | AWR에서 Elapsed Time, CPU Time, Buffer Gets 기준 상위 SQL을 식별하고 튜닝 대상을 선정 가능. |
| ASH (Active Session History) | 실시간 세션 활동 기록. "지금 이 순간 무엇이 느린가?"를 진단할 때 사용. V$ACTIVE_SESSION_HISTORY 조회 가능. |
| Statspack | AWR의 무료 대안. 소규모 환경에서의 활용 방법을 알고 있음. |
| Wait Event 분석 | db file sequential read(인덱스 I/O), db file scattered read(풀 스캔 I/O), log file sync(커밋 대기), enq: TX - row lock contention(락 경합) 등 주요 대기 이벤트의 의미와 대응을 설명 가능. |

---

### Step 9. SQL 튜닝 실전 — 바인드 변수, 부분 범위 처리, 소트 튜닝

| 학습 항목 | 학습 목표 |
|----------|----------|
| 바인드 변수 | 리터럴 SQL vs 바인드 변수의 차이를 설명 가능. 하드 파싱(Hard Parse)과 소프트 파싱(Soft Parse)의 차이를 설명 가능. 바인드 변수가 라이브러리 캐시 효율을 높이는 이유를 설명 가능. 바인드 변수 페킹(Bind Peeking)의 부작용을 설명 가능. |
| 부분 범위 처리 | 전체 결과를 다 구한 후 정렬하는 것(전체 범위 처리) vs 인덱스 순서로 읽으며 필요한 만큼만 반환하는 것(부분 범위 처리)의 차이를 설명 가능. 페이징 쿼리에서 부분 범위 처리가 중요한 이유를 설명 가능. |
| 소트 튜닝 | ORDER BY, GROUP BY에서 불필요한 소트를 인덱스로 대체하는 방법을 설명 가능. 소트가 PGA에서 처리되지 못하고 Temp 영역으로 스필되는 현상과 대응을 설명 가능. |
| 서브쿼리 최적화 | 상관 서브쿼리(Correlated Subquery)의 성능 문제를 설명 가능. EXISTS vs IN vs JOIN 변환의 판단 기준을 설명 가능. |
| 대량 DML 튜닝 | 대량 INSERT/UPDATE/DELETE 시 성능 향상 기법(INSERT /*+ APPEND */, NOLOGGING, 배치 커밋 주기)을 설명 가능. |

---

### Step 10. 파티셔닝 — RANGE/LIST/HASH/Composite

| 학습 항목 | 학습 목표 |
|----------|----------|
| 파티셔닝 개념 | 하나의 큰 테이블을 물리적으로 분할하여 관리하는 이유(쿼리 성능, 관리 편의, 가용성)를 설명 가능. |
| RANGE 파티셔닝 | 날짜/숫자 범위 기준 분할. 이력 데이터(주문 이력, 로그)에 적합한 이유 설명 가능. Partition Pruning(옵티마이저가 불필요한 파티션 스캔 제외)을 설명 가능. |
| LIST 파티셔닝 | 특정 값 목록 기준 분할 (지역, 유형 등). 적합한 사례 설명 가능. |
| HASH 파티셔닝 | 해시 함수 기반 균등 분할. 핫스팟 분산에 적합한 이유 설명 가능. |
| Composite 파티셔닝 | RANGE + HASH, RANGE + LIST 등 2단계 분할. 대용량 이력 테이블에서의 활용 설명 가능. |
| 파티션 인덱스 | Local Index vs Global Index의 차이와 선택 기준을 설명 가능. |

---

### Step 11. 레플리카 — Data Guard, RAC 개념

| 학습 항목 | 학습 목표 |
|----------|----------|
| Oracle Data Guard | 물리적 Standby / 논리적 Standby의 차이를 설명 가능. Redo Log 전송 방식(동기/비동기)에 따른 데이터 손실 가능성을 설명 가능. 읽기 전용 Standby(Active Data Guard)의 활용(리포트 쿼리 분산)을 설명 가능. |
| Oracle RAC (Real Application Clusters) | 여러 인스턴스가 하나의 DB를 공유하는 구조. Cache Fusion(인스턴스 간 블록 전송)의 개념을 설명 가능. 고가용성(HA) + 부하 분산 목적임을 설명 가능. |
| HA 구성 목적 | 단일 장애점(SPOF) 제거, RTO/RPO 개념을 설명 가능. |

---

### Step 12. 커넥션 풀 — HikariCP 튜닝

| 학습 항목 | 학습 목표 |
|----------|----------|
| 커넥션 풀의 필요성 | DB 커넥션 생성 비용(TCP 핸드셰이크 + 인증)이 비싼 이유를 설명 가능. 풀을 사용해 미리 생성해두고 재사용하는 원리를 설명 가능. |
| HikariCP 핵심 설정 | `maximumPoolSize` (최대 커넥션 수), `minimumIdle` (최소 유휴 커넥션), `connectionTimeout` (커넥션 대기 시간), `maxLifetime` (커넥션 최대 수명), `idleTimeout` (유휴 커넥션 제거 시간) 각 설정의 의미와 튜닝 기준을 설명 가능. |
| 적정 풀 크기 산정 | `Pool Size = CPU 코어 수 * 2 + 유효 디스크 수` 공식의 배경(I/O 대기 시간 고려)을 설명 가능. 너무 크면(컨텍스트 스위칭, DB 부하) / 너무 작으면(커넥션 대기) 문제를 설명 가능. |
| 커넥션 누수 진단 | `leakDetectionThreshold` 설정으로 커넥션 반환 안 되는 코드 식별 가능. 커넥션 누수 원인(try-with-resources 미사용, 예외 시 close 누락)을 설명 가능. |
| Spring Boot와의 연동 | `application.yml`에서 HikariCP 설정 방법. 모니터링(Actuator + Micrometer로 풀 사용률 확인) 방법을 알고 있음. |
| Oracle PROCESSES/SESSIONS와의 관계 | Oracle의 `PROCESSES`(OS 프로세스 수 상한)와 `SESSIONS`(접속 세션 수 상한, 통상 PROCESSES * 1.5 + 22) 파라미터를 설명 가능. WAS가 여러 대일 때 `WAS 수 × maximumPoolSize ≤ Oracle SESSIONS` 를 확인해야 하는 이유를 설명 가능. "WAS 설정은 완벽한데 DB 접속이 안 된다" → Oracle PROCESSES/SESSIONS 한도 초과 의심 → `V$RESOURCE_LIMIT` 조회로 진단하는 순서를 설명 가능. |

---

### Step 13. JPA 개요 — ORM 개념, JPA vs MyBatis vs JDBC

| 학습 항목 | 학습 목표 |
|----------|----------|
| ORM이란 | 객체-관계 매핑(Object-Relational Mapping)의 개념을 설명 가능. 객체 모델과 관계형 DB 모델 사이의 패러다임 불일치(상속, 연관관계, 데이터 타입, 동일성)를 설명 가능. |
| JPA란 | Java Persistence API가 인터페이스(표준 명세)이고, Hibernate가 구현체임을 설명 가능. JPA를 쓰는 이유(생산성, DB 독립성, 패러다임 불일치 해결)를 설명 가능. |
| JPA vs MyBatis | JPA는 객체 중심(엔티티 매핑, 자동 SQL), MyBatis는 SQL 중심(직접 SQL 작성). 각각의 장단점과 선택 기준을 설명 가능. 둘을 함께 쓰는 경우(복잡한 통계 쿼리는 MyBatis, 도메인 CRUD는 JPA)를 설명 가능. |
| JPA vs JDBC | JDBC는 커넥션 획득 → SQL 작성 → ResultSet 매핑을 수동으로 하는 반면, JPA는 이를 자동화. 반복 코드 제거 + 유지보수성 향상 이유를 설명 가능. |
| Spring Data JPA | JPA를 한 번 더 추상화한 것. Repository 인터페이스만 정의하면 구현체가 자동 생성되는 원리를 설명 가능. JPA vs Spring Data JPA의 관계를 설명 가능. |

---

### Step 14. 엔티티 매핑 — @Entity, @Id, @Column, @GeneratedValue

| 학습 항목 | 학습 목표 |
|----------|----------|
| @Entity, @Table | 클래스를 엔티티로 등록하는 방법. @Table(name = "...")으로 테이블명 매핑. 기본 생성자(protected/public)가 필수인 이유를 설명 가능. |
| @Id, @GeneratedValue | PK 매핑 방법. GenerationType.IDENTITY(MySQL AUTO_INCREMENT), SEQUENCE(Oracle), TABLE, AUTO 각각의 차이와 DB별 선택 기준을 설명 가능. |
| @Column | 컬럼 매핑 속성(name, nullable, unique, length, columnDefinition). nullable = false와 DDL 자동 생성의 관계를 설명 가능. |
| @Enumerated | EnumType.STRING vs EnumType.ORDINAL의 차이. ORDINAL을 쓰면 안 되는 이유(Enum 순서 변경 시 데이터 불일치)를 설명 가능. |
| @Temporal, @Lob, @Transient | 날짜 타입 매핑(Java 8 이후 LocalDate/LocalDateTime은 @Temporal 불필요), 대용량 데이터 매핑, 매핑 제외 필드를 설명 가능. |
| DDL 자동 생성 (hibernate.ddl-auto) | create, create-drop, update, validate, none 각 옵션의 동작을 설명 가능. 운영 환경에서 validate 또는 none만 써야 하는 이유를 설명 가능. |

---

### Step 15. 연관관계 매핑 — @ManyToOne, @OneToMany, 양방향

| 학습 항목 | 학습 목표 |
|----------|----------|
| 단방향 @ManyToOne | 가장 기본적인 연관관계. FK가 있는 쪽에 @ManyToOne을 붙이는 이유(DB FK 위치와 일치)를 설명 가능. @JoinColumn으로 FK 컬럼 지정 가능. |
| 단방향 @OneToMany | @OneToMany만 있는 단방향의 문제점(중간 테이블 생성 또는 UPDATE SQL 추가 발생)을 설명 가능. 실무에서 잘 쓰지 않는 이유를 설명 가능. |
| 양방향 연관관계 | @ManyToOne + @OneToMany(mappedBy = "...")로 양방향 설정. 연관관계의 주인(FK가 있는 쪽) 개념을 설명 가능. mappedBy의 의미(읽기 전용, 주인이 아닌 쪽)를 설명 가능. |
| 연관관계 편의 메서드 | 양방향에서 양쪽 모두 세팅해야 하는 이유를 설명 가능. 편의 메서드를 한쪽에 작성하는 패턴을 적용 가능. |
| @OneToOne | 일대일 매핑. FK를 어느 테이블에 두는지에 따른 장단점(주 테이블 FK vs 대상 테이블 FK)을 설명 가능. |
| @ManyToMany | 다대다 매핑의 한계(중간 테이블에 추가 컬럼 불가)를 설명 가능. 실무에서 중간 엔티티를 만들어 @OneToMany + @ManyToOne으로 풀어쓰는 이유를 설명 가능. |
| 연관관계 설계 원칙 | 실무에서 "가급적 단방향, 필요할 때만 양방향" 원칙의 이유를 설명 가능. |

---

### Step 16. 상속 매핑 — @Inheritance, @MappedSuperclass

| 학습 항목 | 학습 목표 |
|----------|----------|
| JOINED 전략 | 부모/자식 테이블 각각 생성 + JOIN으로 조회. 정규화된 구조의 장점(데이터 중복 없음)과 단점(JOIN 성능)을 설명 가능. |
| SINGLE_TABLE 전략 | 한 테이블에 모든 컬럼을 넣고 DTYPE으로 구분. 장점(조회 성능, JOIN 없음)과 단점(null 컬럼 많음, 테이블 비대화)을 설명 가능. |
| TABLE_PER_CLASS 전략 | 각 클래스마다 독립 테이블. 쓰지 않는 것이 권장되는 이유(UNION ALL 필요, 비효율)를 설명 가능. |
| @DiscriminatorColumn, @DiscriminatorValue | 구분 컬럼(DTYPE)의 역할과 설정 방법을 알고 있음. |
| @MappedSuperclass | 상속 매핑이 아닌 공통 매핑 정보(createdDate, modifiedDate 등)를 부모 클래스에서 제공하는 용도임을 설명 가능. 엔티티가 아니므로 테이블과 매핑되지 않음을 설명 가능. |
| 실무 선택 기준 | 기본은 SINGLE_TABLE(단순), 비즈니스적으로 중요하면 JOINED, TABLE_PER_CLASS는 쓰지 않는다는 실무 가이드를 설명 가능. |

---

### Step 17. JPQL 기본 — SELECT, JOIN, 페이징, 집합 함수

| 학습 항목 | 학습 목표 |
|----------|----------|
| JPQL이란 | SQL은 테이블 대상, JPQL은 엔티티 대상 쿼리임을 설명 가능. JPQL이 결국 SQL로 변환되는 과정을 설명 가능. |
| 기본 SELECT | `SELECT m FROM Member m WHERE m.name = :name` 형태의 JPQL 작성 가능. 파라미터 바인딩(:name, ?1) 사용 가능. |
| JOIN (내부 조인, 외부 조인, 세타 조인) | `JOIN m.team t` (내부 조인), `LEFT JOIN` (외부 조인)을 JPQL로 작성 가능. ON 절 활용 가능. |
| 페이징 | `setFirstResult()`, `setMaxResults()`로 페이징 처리. DB 방언에 따라 SQL이 다르게 생성됨(Oracle ROWNUM, MySQL LIMIT)을 설명 가능. |
| 집합 함수 | COUNT, SUM, AVG, MAX, MIN + GROUP BY, HAVING을 JPQL로 작성 가능. |
| 서브쿼리 | WHERE/HAVING 절 서브쿼리 작성 가능. EXISTS, IN, ALL, ANY 사용 가능. FROM 절 서브쿼리(인라인 뷰)는 JPQL에서 지원 안 되므로 Native Query 필요함을 알고 있음. |
| 벌크 연산 | `executeUpdate()`로 한 번에 여러 행 UPDATE/DELETE. 영속성 컨텍스트와 DB 불일치 문제 + em.clear() 필요성을 설명 가능. (Step 20에서 심화) |

---

### Step 18. JPA 영속성 컨텍스트 내부 동작

| 학습 항목 | 학습 목표 |
|----------|----------|
| 영속성 컨텍스트란 | EntityManager가 관리하는 엔티티 저장소. "1차 캐시"의 역할을 설명 가능. |
| 엔티티 생명주기 | 비영속(new) → 영속(persist) → 준영속(detach) → 삭제(remove) 각 상태의 의미와 전이 조건을 설명 가능. |
| 1차 캐시 | 같은 트랜잭션 내에서 같은 엔티티를 반복 조회해도 DB 쿼리가 1번만 발생하는 이유를 설명 가능. |
| 동일성 보장 | 같은 영속성 컨텍스트에서 같은 PK 엔티티는 `==` 비교가 true인 이유를 설명 가능. |
| 쓰기 지연 (Transactional Write-behind) | persist() 호출 시 즉시 INSERT가 안 나가고 커밋 시점에 모아서 처리하는 이유(배치 최적화)를 설명 가능. |
| 변경 감지 (Dirty Checking) | flush 시점에 1차 캐시의 스냅샷과 현재 엔티티를 비교하여 변경된 필드만 UPDATE하는 메커니즘을 설명 가능. |
| flush vs commit | flush(SQL 전송)와 commit(트랜잭션 확정)의 차이를 설명 가능. flush 타이밍(자동: JPQL 실행 전, 트랜잭션 커밋 전 / 수동: em.flush())을 설명 가능. |
| OSIV (Open Session In View) | OSIV 켜짐/꺼짐의 차이, 켜져 있을 때 장점(뷰에서 지연 로딩 가능)과 단점(DB 커넥션 오래 점유)을 설명 가능. 실무에서 끄는 것을 권장하는 이유를 설명 가능. |

---

### Step 19. JPA N+1 문제 + 해결

| 학습 항목 | 학습 목표 |
|----------|----------|
| N+1 문제란 | 1개 쿼리로 N개 엔티티 조회 후, 각 엔티티의 연관 엔티티를 조회하기 위해 N개 추가 쿼리가 발생하는 현상을 구체적 코드/쿼리로 설명 가능. |
| 발생 조건 | LAZY 로딩 + 컬렉션/연관 엔티티 접근 시, EAGER 로딩 + JPQL 사용 시 모두 발생할 수 있음을 설명 가능. |
| Fetch Join | `JOIN FETCH`로 연관 엔티티를 한 번에 조회하는 방법. |
| 컬렉션 Fetch Join의 데이터 뻥튀기 | 1:N 컬렉션을 Fetch Join하면 Cartesian Product가 발생하여 부모 엔티티가 N개로 중복되는 문제를 설명 가능. JPQL `DISTINCT`로 애플리케이션 레벨에서 중복 제거하는 방법을 설명 가능. Hibernate 6+에서 DISTINCT 자동 적용 변경 사항을 알고 있음. |
| 컬렉션 Fetch Join + 페이징 위험 | 컬렉션 Fetch Join 시 DB 레벨 페이징이 불가능한 이유(뻥튀기된 결과에서 페이징하면 데이터 잘림)를 설명 가능. Hibernate가 메모리에서 페이징하며 `WARN: firstResult/maxResults specified with collection fetch; applying in memory!` 경고가 나오는 이유를 설명 가능. 대량 데이터에서 메모리 OOM 위험을 설명 가능. |
| @EntityGraph | 어노테이션 기반으로 Fetch Join을 적용하는 방법. attributePaths 사용법을 알고 있음. |
| @BatchSize | `IN` 절로 묶어서 조회하는 방법. N+1 → 1+ceil(N/BatchSize) 쿼리로 감소. 글로벌 설정(`default_batch_fetch_size`)과 개별 설정의 차이를 설명 가능. 컬렉션 페이징이 필요한 경우 Fetch Join 대신 BatchSize가 안전한 이유를 설명 가능. |
| 해결 전략 선택 기준 | **"무조건 Fetch Join"은 주니어 답변.** 1:1/N:1은 Fetch Join, 1:N 컬렉션 + 페이징 필요 시 BatchSize가 실무에서 안전한 이유를 트레이드오프와 함께 설명 가능. |
| 코드 리뷰에서 N+1 식별 | 엔티티 연관관계 + 반복문/스트림에서 getter 호출 패턴을 보고 N+1 위험을 사전 식별 가능. |

---

### Step 20. JPA 변경 감지, 지연 로딩, 프록시

| 학습 항목 | 학습 목표 |
|----------|----------|
| 지연 로딩 (LAZY) vs 즉시 로딩 (EAGER) | LAZY가 기본이어야 하는 이유(불필요한 쿼리 방지)를 설명 가능. EAGER의 문제점(사용하지 않는 연관 엔티티도 항상 조회)을 설명 가능. |
| 프록시 객체 | LAZY 로딩 시 JPA가 프록시 객체(가짜 객체)를 넣어두고, 실제 접근 시 DB 쿼리를 발생시키는 메커니즘을 설명 가능. |
| LazyInitializationException | 영속성 컨텍스트가 닫힌 후(트랜잭션 종료 후) 프록시에 접근하면 발생하는 이유를 설명 가능. 해결 방법(Fetch Join, OSIV, DTO 변환)을 설명 가능. |
| 변경 감지 심화 | @DynamicUpdate(변경된 컬럼만 UPDATE)의 사용 시점과 트레이드오프를 설명 가능. |
| 벌크 연산 | `@Modifying` + JPQL UPDATE/DELETE가 영속성 컨텍스트를 거치지 않는 이유를 설명 가능. 벌크 연산 후 `em.clear()` 해야 하는 이유를 설명 가능. |

---

### Step 21. QueryDSL / Native Query 최적화

| 학습 항목 | 학습 목표 |
|----------|----------|
| QueryDSL 장점 | 타입 안전(컴파일 시점 오류 감지), 동적 쿼리 작성 용이성, JPQL 문자열 오류 방지를 설명 가능. |
| BooleanExpression 조합 | 동적 WHERE 조건을 메서드로 분리 + null이면 조건 제외하는 패턴을 작성 가능. |
| Projection (DTO 직접 조회) | `Projections.constructor()`, `@QueryProjection`으로 엔티티가 아닌 DTO를 직접 조회하는 방법과 장점(불필요한 컬럼 제외, 영속성 컨텍스트 비사용)을 설명 가능. |
| Native Query 사용 판단 | JPQL/QueryDSL로 표현 불가능한 경우(윈도우 함수, DB 고유 함수, 복잡한 통계 쿼리)에만 Native Query를 쓰는 판단 기준을 설명 가능. |
| 성능 비교 | 같은 로직을 JPQL, QueryDSL, Native Query로 각각 작성했을 때 성능 차이가 거의 없는 이유(결국 SQL로 변환)를 설명 가능. 진짜 성능 차이는 "어떤 SQL이 생성되느냐"에 달려 있음을 이해. |

---

### Step 22. MySQL/PostgreSQL 차이 정리 (면접 대비)

| 학습 항목 | 학습 목표 |
|----------|----------|
| InnoDB 클러스터드 인덱스 vs Oracle IOT | MySQL InnoDB는 PK가 곧 클러스터드 인덱스(데이터 정렬 저장)인 반면, Oracle은 일반 테이블(힙 구조)이 기본이고 IOT는 명시적 선택임을 설명 가능. 세컨더리 인덱스 동작 차이(MySQL: PK 값 저장 → PK 인덱스 재탐색 / Oracle: ROWID 직접 접근)를 설명 가능. |
| MySQL Gap Lock / Next-Key Lock vs Oracle Row Lock | MySQL REPEATABLE READ에서 팬텀 읽기 방지를 위해 Gap Lock이 존재. Oracle은 Row Lock만 사용하고 MVCC로 팬텀 읽기를 처리하는 차이를 설명 가능. |
| 실행계획 도구 차이 | MySQL `EXPLAIN ANALYZE` vs Oracle `DBMS_XPLAN` 사용법과 출력 형식 차이를 설명 가능. |
| 힌트 사용 문화 | Oracle은 힌트를 적극 사용하는 반면, MySQL은 옵티마이저에 위임하는 경향. MySQL 힌트(`FORCE INDEX`, `STRAIGHT_JOIN`)는 사용 빈도 낮음을 설명 가능. |
| PostgreSQL 특징 | MVCC 구현 차이(PostgreSQL은 튜플 버전 관리, Vacuum 필요), JSON 지원(JSONB), 확장성(Extension)을 개념 수준 설명 가능. |

---

## 3. 자가 검증

### Oracle 튜닝
- [ ] "B-Tree 인덱스 구조를 그려보세요" → Root-Branch-Leaf + Leaf 간 연결 리스트 즉시 그림 가능
- [ ] "인덱스를 만들었는데 안 타는 이유 3가지" 즉시 답변 가능
- [ ] DBMS_XPLAN 결과 보고 "왜 느린지, 어떻게 고칠지" 즉시 답변 가능
- [ ] "NL Join vs Hash Join 선택 기준" 설명 가능
- [ ] "바인드 변수를 써야 하는 이유" → 하드 파싱 vs 소프트 파싱으로 설명 가능
- [ ] AWR 리포트에서 Top SQL 식별 + 튜닝 포인트 도출 가능
- [ ] "db file sequential read 대기 이벤트의 의미는?" 즉시 답변 가능

### 트랜잭션
- [ ] 트랜잭션 격리 수준별 동작 차이를 실제 시나리오로 설명 가능
- [ ] "Oracle에서 SELECT는 왜 락을 잡지 않는가?" → MVCC/CR Copy로 설명 가능
- [ ] "ORA-01555는 왜 발생하는가?" → Undo 덮어쓰기 + 장시간 쿼리 설명 가능
- [ ] 데드락 발생 시 V$LOCK 조회 → 블로커 식별 → 원인 분석 순서 설명 가능
- [ ] "Lost Update를 어떻게 해결하는가?" → Optimistic Lock(@Version) vs Pessimistic Lock(SELECT FOR UPDATE) 비교 + 선택 기준 설명 가능
- [ ] "재고 차감에는 어떤 락 전략을 쓰는가?" → 근거와 함께 답변 가능

### 인프라
- [ ] "WAS 커넥션 풀 설정은 완벽한데 DB 접속이 안 된다" → Oracle PROCESSES/SESSIONS 한도 초과 진단 가능

### JPA 기초
- [ ] "JPA vs MyBatis 차이와 선택 기준" 설명 가능
- [ ] "연관관계의 주인이란?" → FK가 있는 쪽, mappedBy의 의미 설명 가능
- [ ] "@ManyToMany를 실무에서 쓰지 않는 이유" 설명 가능
- [ ] "상속 매핑 전략 3가지와 실무 선택 기준" 설명 가능
- [ ] "JPQL과 SQL의 차이" 설명 가능

### JPA 심화
- [ ] "영속성 컨텍스트의 역할 4가지" 즉시 답변 가능 (1차 캐시, 동일성 보장, 쓰기 지연, 변경 감지)
- [ ] "N+1 문제가 무엇이고 어떻게 해결하는가?" 3가지 방법(Fetch Join, BatchSize, EntityGraph) 설명 가능
- [ ] "컬렉션 Fetch Join 시 데이터 뻥튀기란?" → Cartesian Product + DISTINCT 해결 설명 가능
- [ ] "컬렉션 Fetch Join + 페이징이 위험한 이유" → 메모리 내 페이징 + OOM 위험 설명 가능
- [ ] "페이징이 필요한 1:N 조회에서 N+1을 해결하려면?" → BatchSize 사용 + 이유 설명 가능
- [ ] N+1 문제를 코드 리뷰에서 사전에 식별 가능
- [ ] "OSIV를 끄면 어떤 문제가 생기고 어떻게 대응하나?" 설명 가능
- [ ] "벌크 연산 후 em.clear()를 해야 하는 이유" 설명 가능

### 면접 대비
- [ ] Oracle과 MySQL의 핵심 차이 3가지 이상 설명 가능
- [ ] "InnoDB 클러스터드 인덱스란?" 설명 가능
- [ ] "MySQL Gap Lock이란?" 설명 가능

---

## 4. 진행 상태

| Step | 항목 | 상태 |
|------|------|------|
| Step 1 | 인덱스 원리 | 미시작 |
| Step 2 | 실행계획 분석 | 미시작 |
| Step 3 | Oracle 힌트 | 미시작 |
| Step 4 | 조인 방식 | 미시작 |
| Step 5 | 트랜잭션 격리 수준 | 미시작 |
| Step 6 | Oracle MVCC | 미시작 |
| Step 7 | 락 | 미시작 |
| Step 8 | AWR / ASH / Statspack | 미시작 |
| Step 9 | SQL 튜닝 실전 | 미시작 |
| Step 10 | 파티셔닝 | 미시작 |
| Step 11 | 레플리카 | 미시작 |
| Step 12 | 커넥션 풀 (HikariCP) | 미시작 |
| Step 13 | JPA 개요 — ORM, JPA vs MyBatis | 미시작 |
| Step 14 | 엔티티 매핑 | 미시작 |
| Step 15 | 연관관계 매핑 | 미시작 |
| Step 16 | 상속 매핑 | 미시작 |
| Step 17 | JPQL 기본 | 미시작 |
| Step 18 | JPA 영속성 컨텍스트 | 미시작 |
| Step 19 | JPA N+1 문제 | 미시작 |
| Step 20 | JPA 변경 감지/지연 로딩/프록시 | 미시작 |
| Step 21 | QueryDSL / Native Query | 미시작 |
| Step 22 | MySQL/PostgreSQL 차이 | 미시작 |

---

## 5. 참고 자료 (보조용)

| 자료 | 용도 |
|------|------|
| 친절한 SQL 튜닝 (조시형) | Step 1~4, 9 보조. Oracle 실전 튜닝 원문 참조 시 |
| Oracle 성능 고도화 원리와 해법 1, 2 (조시형) | Step 5~8 보조. 트랜잭션/락/AWR 심화 |
| Database Internals (Alex Petrov) | DB 엔진 내부 구조 심화 참고 |
| 김영한 인프런 JPA 기본편 + 활용편 | Step 13~16 보조. JPA 강의 참고 시 |
| Oracle 공식 문서 (docs.oracle.com) | AWR, 힌트, 파티셔닝 등 공식 레퍼런스 |

---

> 이 문서는 Claude가 미래 세션에서 읽고 학습을 안내하기 위한 가이드입니다.
> 사용자가 "DB 공부하자" 또는 "Step N 하자"라고 하면, 진행 상태를 확인하고 다음 미시작 Step부터 학습_템플릿.md 형식으로 진행합니다.
