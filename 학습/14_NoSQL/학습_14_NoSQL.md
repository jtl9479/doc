# 학습 14. NoSQL

## Step 목차

| Step | 항목 | 카테고리 |
|------|------|----------|
| Step 1 | NoSQL 개요 — 왜 NoSQL인가, RDBMS의 한계 | 기초 |
| Step 2 | NoSQL 유형 — Document, Key-Value, Column-Family, Graph | 기초 |
| Step 3 | RDBMS vs NoSQL 선택 기준 — 트레이드오프 | 기초 |
| Step 4 | MongoDB 기초 — 개념, 설치, 기본 CRUD | MongoDB |
| Step 5 | MongoDB 데이터 모델링 — 임베딩 vs 레퍼런싱 | MongoDB |
| Step 6 | MongoDB 인덱스와 쿼리 | MongoDB |
| Step 7 | DynamoDB 개념 — AWS 관리형 Key-Value/Document DB | DynamoDB |
| Step 8 | NoSQL 트랜잭션과 정합성 제어 | 심화 |
| Step 9 | NoSQL 실전 — 선택 기준 + 마이그레이션 전략 | 실전 |

---

## 1. 개요

**현재 수준**: RDBMS(Oracle) 실무 경험. NoSQL 경험 없음.
**학습 목표**: "이 데이터에 RDBMS가 맞는가, NoSQL이 맞는가?"를 판단 가능. MongoDB 기본 CRUD 가능. 면접에서 NoSQL 관련 질문에 트레이드오프 기반으로 답변 가능.
**분기 배정**: 3분기 (2026.10 ~ 2026.12)
**선수 조건**: 학습_02 DB/JPA, 학습_03 DDIA(Step 1 데이터 모델) 학습 후 진행 권장

---

## 2. 학습 순서 + 세부 항목

---

### Step 1. NoSQL 개요 — 왜 NoSQL인가, RDBMS의 한계

| 학습 항목 | 학습 목표 |
|----------|----------|
| NoSQL이란 | "Not Only SQL". RDBMS가 아닌 데이터 저장소의 총칭. 하나의 기술이 아니라 다양한 유형(Document, Key-Value, Column-Family, Graph)의 집합임을 설명 가능. |
| RDBMS의 한계 | ① 고정 스키마(스키마 변경 비용), ② 수평 확장 어려움(샤딩 복잡), ③ 비정형 데이터 처리 부적합(JSON, 로그, IoT), ④ 초고속 읽기/쓰기(캐시성 데이터). 각 한계를 설명 가능. |
| NoSQL이 등장한 배경 | 빅데이터(대용량), 웹 서비스(높은 동시성), 다양한 데이터 형태(비정형)에 RDBMS만으로 감당 안 되는 시대적 변화를 설명 가능. |
| NoSQL의 공통 특성 | 유연한 스키마(Schema-on-Read), 수평 확장 용이(분산 설계 기본), 높은 가용성(복제). 단점(트랜잭션 제한, 조인 미지원/제한, 일관성 트레이드오프)도 설명 가능. |
| CAP 정리와 NoSQL | 대부분의 NoSQL이 AP(가용성 + 분단 내성)를 선택하여 최종 일관성(Eventual Consistency)을 허용하는 이유를 설명 가능. (DDIA Step 9와 연계) |

---

### Step 2. NoSQL 유형 — Document, Key-Value, Column-Family, Graph

| 학습 항목 | 학습 목표 |
|----------|----------|
| Document DB | JSON/BSON 문서 단위로 저장. 스키마 유연. 내장 문서(Embedded)로 조인 없이 관련 데이터를 한 번에 조회 가능. **대표: MongoDB, CouchDB**. 적합: 콘텐츠 관리, 사용자 프로필, 상품 카탈로그. |
| Key-Value DB | 키-값 쌍으로 저장. 가장 단순하고 빠름. 복잡한 쿼리 불가(키로만 조회). **대표: Redis, DynamoDB, Memcached**. 적합: 캐시, 세션, 설정. (Redis는 학습_08에서 상세 학습) |
| Column-Family DB | 행(Row)이 아닌 컬럼 패밀리 단위로 저장. 대량 데이터의 특정 컬럼 집합 조회에 최적. **대표: Cassandra, HBase**. 적합: 시계열 데이터, 로그, IoT 센서. |
| Graph DB | 노드(Node)와 관계(Edge)로 저장. 복잡한 관계 탐색에 최적. **대표: Neo4j, Amazon Neptune**. 적합: 소셜 네트워크, 추천, 지식 그래프. |
| 검색 엔진 (Search Engine) | 전문 검색(Full-text Search)에 특화. 역인덱스(Inverted Index: 단어 → 문서 목록 매핑)로 RDBMS의 `LIKE '%검색어%'`(풀 스캔, O(n)) 대비 O(1)에 가까운 검색 성능. **대표: Elasticsearch, OpenSearch**. 적합: 상품 검색, 로그 분석, 자동완성. ERP에서 "수주번호/거래처명/품목명 통합 검색"에 활용 가능. Elasticsearch가 NoSQL로 분류되지만 **"저장소"보다 "검색 엔진"**으로 쓰는 것이 올바른 용도임을 설명 가능. |
| 유형별 선택 기준 | 데이터 구조(문서/키값/컬럼/관계/검색)와 접근 패턴(키 조회/범위 스캔/관계 탐색/전문 검색)에 따라 적합한 NoSQL을 선택하는 판단 기준을 설명 가능. |

---

### Step 3. RDBMS vs NoSQL 선택 기준 — 트레이드오프

| 학습 항목 | 학습 목표 |
|----------|----------|
| RDBMS가 적합한 경우 | 데이터 간 관계가 복잡(조인 빈번), 트랜잭션 필수(ACID), 데이터 정합성 최우선(금융, ERP), 스키마가 안정적. |
| NoSQL이 적합한 경우 | 스키마가 자주 변경, 대용량 + 수평 확장 필요, 읽기/쓰기 성능 최우선, 비정형 데이터, 조인이 필요 없는 독립 문서. |
| "둘 다 쓰는" 패턴 (Polyglot Persistence) | RDBMS(핵심 트랜잭션 데이터) + MongoDB(비정형 로그/콘텐츠) + Redis(캐시) + Elasticsearch(검색)를 함께 쓰는 실무 패턴을 설명 가능. |
| ERP에서 NoSQL이 적합한 부분 | ERP 핵심(수주/재고/회계)은 RDBMS 필수. 하지만 파일 메타데이터, 알림 이력, 로그 데이터, 대시보드 집계는 NoSQL이 적합할 수 있음을 설명 가능. |
| 면접 답변 프레임워크 | "이 데이터에 어떤 DB를 쓸 것인가?"에 대해 ① 데이터 구조(정형/비정형) ② 접근 패턴(조인/키 조회) ③ 일관성 요구(ACID/Eventual) ④ 확장성 요구(수직/수평) 4가지 기준으로 판단하는 프레임워크를 설명 가능. |

---

### Step 4. MongoDB 기초 — 개념, 설치, 기본 CRUD

| 학습 항목 | 학습 목표 |
|----------|----------|
| MongoDB란 | 가장 인기 있는 Document DB. JSON 형태(BSON)로 데이터 저장. 스키마 없음(같은 컬렉션에 다른 구조의 문서 가능). |
| 핵심 용어 매핑 | RDBMS → MongoDB: Database → Database, Table → Collection, Row → Document, Column → Field, JOIN → Embedding/Lookup. 매핑을 설명 가능. |
| 환경 구축 | Docker로 MongoDB 실행(`docker run -p 27017:27017 mongo`). mongosh(MongoDB Shell)로 접속 가능. |
| CRUD 기본 | 아래 기본 문법을 실행 가능. |
| 쿼리 연산자 | 아래 연산자를 조합하여 조건부 조회 가능. |
| Aggregation 기초 | 아래 파이프라인 문법으로 집계 쿼리 작성 가능. SQL과 대응시켜 설명 가능. |

**MongoDB 기본 문법 레퍼런스:**

```javascript
// ===== 데이터베이스 / 컬렉션 =====
use mydb                          // DB 선택 (없으면 자동 생성)
show dbs                          // DB 목록
show collections                  // 컬렉션 목록
db.createCollection("orders")     // 컬렉션 생성

// ===== CREATE (삽입) =====
// SQL: INSERT INTO orders (orderId, customer, amount) VALUES (1, '홍길동', 10000)
db.orders.insertOne({
  orderId: 1,
  customer: "홍길동",
  amount: 10000,
  items: [
    { itemName: "상품A", qty: 2, price: 3000 },
    { itemName: "상품B", qty: 1, price: 4000 }
  ],
  createdAt: new Date()
})

db.orders.insertMany([
  { orderId: 2, customer: "김영희", amount: 5000 },
  { orderId: 3, customer: "박철수", amount: 20000 }
])

// ===== READ (조회) =====
// SQL: SELECT * FROM orders
db.orders.find()

// SQL: SELECT * FROM orders WHERE customer = '홍길동'
db.orders.find({ customer: "홍길동" })

// SQL: SELECT * FROM orders WHERE orderId = 1
db.orders.findOne({ orderId: 1 })

// SQL: SELECT customer, amount FROM orders WHERE amount > 5000
db.orders.find(
  { amount: { $gt: 5000 } },          // 조건 (WHERE)
  { customer: 1, amount: 1, _id: 0 }  // 프로젝션 (SELECT 컬럼)
)

// 쿼리 연산자
db.orders.find({ amount: { $gte: 5000 } })              // >= 5000
db.orders.find({ amount: { $lt: 10000 } })               // < 10000
db.orders.find({ customer: { $in: ["홍길동", "김영희"] } }) // IN
db.orders.find({ $and: [{ amount: { $gt: 5000 } }, { customer: "홍길동" }] }) // AND
db.orders.find({ $or: [{ amount: { $gt: 15000 } }, { customer: "김영희" }] }) // OR
db.orders.find({ items: { $exists: true } })              // 필드 존재 여부
db.orders.find({ customer: { $regex: /홍/ } })            // 정규식

// 정렬, 페이징
// SQL: SELECT * FROM orders ORDER BY amount DESC LIMIT 10 OFFSET 5
db.orders.find().sort({ amount: -1 }).skip(5).limit(10)

// 카운트
db.orders.countDocuments({ amount: { $gt: 5000 } })

// ===== UPDATE (수정) =====
// SQL: UPDATE orders SET amount = 15000 WHERE orderId = 1
db.orders.updateOne(
  { orderId: 1 },              // 조건 (WHERE)
  { $set: { amount: 15000 } }  // 변경 ($set: 특정 필드만)
)

// 여러 문서 수정
db.orders.updateMany(
  { amount: { $lt: 10000 } },
  { $set: { status: "소액주문" } }
)

// 숫자 증가
// SQL: UPDATE orders SET amount = amount + 1000 WHERE orderId = 1
db.orders.updateOne(
  { orderId: 1 },
  { $inc: { amount: 1000 } }
)

// 배열에 추가
db.orders.updateOne(
  { orderId: 1 },
  { $push: { items: { itemName: "상품C", qty: 3, price: 2000 } } }
)

// ===== DELETE (삭제) =====
// SQL: DELETE FROM orders WHERE orderId = 3
db.orders.deleteOne({ orderId: 3 })

// SQL: DELETE FROM orders WHERE amount < 5000
db.orders.deleteMany({ amount: { $lt: 5000 } })

// 전체 삭제 (주의!)
db.orders.deleteMany({})

// ===== AGGREGATION (집계) =====
// SQL: SELECT customer, SUM(amount) as total
//      FROM orders
//      WHERE amount > 5000
//      GROUP BY customer
//      HAVING total > 10000
//      ORDER BY total DESC
db.orders.aggregate([
  { $match: { amount: { $gt: 5000 } } },          // WHERE
  { $group: {
      _id: "$customer",                             // GROUP BY
      total: { $sum: "$amount" },                   // SUM
      count: { $sum: 1 }                            // COUNT
  }},
  { $match: { total: { $gt: 10000 } } },           // HAVING
  { $sort: { total: -1 } },                         // ORDER BY
  { $project: {                                      // SELECT 컬럼
      customer: "$_id",
      total: 1,
      count: 1,
      _id: 0
  }}
])

// $lookup (JOIN 유사)
// SQL: SELECT * FROM orders o JOIN customers c ON o.customerId = c._id
db.orders.aggregate([
  { $lookup: {
      from: "customers",          // 조인 대상 컬렉션
      localField: "customerId",   // orders의 필드
      foreignField: "_id",        // customers의 필드
      as: "customerInfo"          // 결과 필드명
  }}
])

// ===== INDEX (인덱스) =====
db.orders.createIndex({ customer: 1 })                // 단일 인덱스 (오름차순)
db.orders.createIndex({ customer: 1, amount: -1 })    // 복합 인덱스
db.orders.createIndex({ orderId: 1 }, { unique: true }) // 유니크 인덱스
db.orders.createIndex({ createdAt: 1 }, { expireAfterSeconds: 86400 }) // TTL (24시간 후 자동 삭제)

db.orders.getIndexes()        // 인덱스 목록
db.orders.dropIndex("인덱스명") // 인덱스 삭제

// 실행계획 확인 (RDBMS의 EXPLAIN과 동일 역할)
db.orders.find({ customer: "홍길동" }).explain("executionStats")
// COLLSCAN = 풀스캔 (인덱스 없음), IXSCAN = 인덱스 스캔
```

**SQL ↔ MongoDB 매핑 요약:**

| SQL | MongoDB |
|-----|---------|
| `SELECT * FROM t WHERE a = 1` | `db.t.find({ a: 1 })` |
| `SELECT a, b FROM t` | `db.t.find({}, { a: 1, b: 1 })` |
| `WHERE a > 5 AND b = 'x'` | `{ a: { $gt: 5 }, b: 'x' }` |
| `WHERE a IN (1, 2, 3)` | `{ a: { $in: [1, 2, 3] } }` |
| `ORDER BY a DESC LIMIT 10` | `.sort({ a: -1 }).limit(10)` |
| `UPDATE t SET a = 1 WHERE b = 2` | `db.t.updateOne({ b: 2 }, { $set: { a: 1 } })` |
| `DELETE FROM t WHERE a = 1` | `db.t.deleteOne({ a: 1 })` |
| `COUNT(*) WHERE a > 5` | `db.t.countDocuments({ a: { $gt: 5 } })` |
| `GROUP BY a, SUM(b)` | `aggregate: $group: { _id: "$a", total: { $sum: "$b" } }` |
| `JOIN` | `aggregate: $lookup` |
| `CREATE INDEX` | `db.t.createIndex({ a: 1 })` |
| `EXPLAIN` | `db.t.find(...).explain()` |

---

### Step 5. MongoDB 데이터 모델링 — 임베딩 vs 레퍼런싱

| 학습 항목 | 학습 목표 |
|----------|----------|
| 임베딩 (Embedding) | 관련 데이터를 하나의 문서 안에 중첩. 예: 주문 문서 안에 주문 항목 배열 포함. 장점(한 번 읽기로 전체 조회, 원자적 업데이트)을 설명 가능. |
| 레퍼런싱 (Referencing) | 다른 컬렉션의 _id를 참조. RDBMS의 FK와 유사. 장점(데이터 중복 없음, 독립적 업데이트)을 설명 가능. |
| 임베딩 vs 레퍼런싱 선택 기준 | 함께 조회되는 빈도 높음 + 데이터 크기 작음 + 1:N(소수) → 임베딩. 독립적 조회 + 데이터 크기 큼 + N:M → 레퍼런싱. 판단 기준을 설명 가능. |
| 문서 크기 제한 | MongoDB 문서 최대 16MB. 무한히 임베딩하면 안 되는 이유. 배열이 무한정 커지는 패턴(Unbounded Array)의 위험을 설명 가능. |
| RDBMS 정규화 vs MongoDB 비정규화 | RDBMS: 정규화(중복 제거) 우선 → 조인으로 조합. MongoDB: 비정규화(읽기 최적화) 우선 → 조인 최소화. 패러다임 차이를 설명 가능. |

---

### Step 6. MongoDB 인덱스와 쿼리

| 학습 항목 | 학습 목표 |
|----------|----------|
| 인덱스 | B-Tree 기반(RDBMS와 동일 원리). 인덱스 없으면 컬렉션 풀 스캔. createIndex()로 생성 가능. |
| 복합 인덱스 | 여러 필드를 포함하는 인덱스. 필드 순서가 중요한 이유(RDBMS 복합 인덱스와 동일 원리)를 설명 가능. |
| explain() | 쿼리 실행계획 확인. COLLSCAN(풀 스캔) vs IXSCAN(인덱스 스캔)을 식별 가능. RDBMS의 EXPLAIN과 같은 역할임을 설명 가능. |
| 유니크 인덱스 | `unique: true`로 중복 방지. _id 필드는 자동 유니크 인덱스. |
| TTL 인덱스 | 특정 시간 경과 후 문서 자동 삭제. 로그/세션 데이터 관리에 활용. |

---

### Step 7. DynamoDB 개념 — AWS 관리형 Key-Value/Document DB

| 학습 항목 | 학습 목표 |
|----------|----------|
| DynamoDB란 | AWS 완전 관리형 NoSQL. Key-Value + Document 모델. 서버리스(프로비저닝 불필요), 자동 확장, 밀리초 응답. |
| Partition Key + Sort Key | Partition Key(해시 키): 데이터 분산 기준. Sort Key(범위 키): 같은 파티션 내 정렬. 두 키의 조합이 PK. RDBMS의 복합 PK와 비교하여 설명 가능. |
| 용량 모드 | On-Demand(요청량에 따라 자동, 비용 높음) vs Provisioned(RCU/WCU 미리 설정, 비용 낮음, 초과 시 쓰로틀링). 선택 기준을 설명 가능. |
| GSI (Global Secondary Index) | 기본 키 외 다른 속성으로 조회하기 위한 인덱스. RDBMS의 세컨더리 인덱스와 유사하지만 별도 테이블처럼 데이터를 복사하는 구조임을 설명 가능. |
| DynamoDB의 한계 | 복잡한 쿼리/조인 불가, 트랜잭션 제한(25개 아이템), 유연하지 않은 쿼리(설계 시 접근 패턴을 미리 결정해야 함). |
| MongoDB vs DynamoDB | MongoDB: 자체 호스팅 가능, 유연한 쿼리, 조인($lookup) 가능. DynamoDB: AWS 관리형, 서버리스, 자동 확장, 하지만 쿼리 제한. 선택 기준을 설명 가능. |

---

### Step 8. NoSQL 트랜잭션과 정합성 제어

| 학습 항목 | 학습 목표 |
|----------|----------|
| "NoSQL은 트랜잭션이 안 된다"는 오해 | 과거에는 맞았지만 현재 MongoDB 4.0+, DynamoDB 모두 트랜잭션을 지원. 다만 RDBMS 수준의 유연함은 아니며 제약이 있음을 설명 가능. |
| MongoDB Multi-document Transaction | MongoDB 4.0+에서 여러 문서/컬렉션에 걸친 ACID 트랜잭션 지원. `session.startTransaction()` → 작업 → `session.commitTransaction()` / `session.abortTransaction()` 패턴을 설명 가능. |
| MongoDB 트랜잭션 제약 | 성능 오버헤드(락 경합 증가), 단일 문서 작업은 트랜잭션 없이도 원자적(MongoDB의 강점), 트랜잭션을 남용하면 MongoDB의 장점을 상쇄. "트랜잭션이 필요한 설계 자체가 MongoDB에 부적합할 수 있다"는 판단을 설명 가능. |
| DynamoDB Conditional Writes | `ConditionExpression`으로 "version = :expected_version일 때만 업데이트"하는 낙관적 락 패턴. RDBMS의 `WHERE version = ?`와 유사. 동시 쓰기 충돌을 방지하는 원리를 설명 가능. |
| DynamoDB TransactWriteItems | 최대 25개 아이템에 대한 ACID 트랜잭션. "주문 생성 + 재고 차감"을 원자적으로 처리하는 패턴을 설명 가능. 제약(25개, 동일 아이템 중복 불가, 4MB 제한)을 설명 가능. |
| NoSQL 정합성 전략 정리 | 단일 문서 원자성(MongoDB의 기본 강점) → Multi-document Transaction(필요 시) → Conditional Writes(낙관적 락) → 이벤트 기반 최종 일관성(서비스 간). 상황에 맞는 전략 선택을 설명 가능. |

---

### Step 9. NoSQL 실전 — 선택 기준 + 마이그레이션 전략

| 학습 항목 | 학습 목표 |
|----------|----------|
| 시나리오별 선택 | **사용자 프로필 저장** → MongoDB(유연한 스키마, 문서 단위 조회). **세션/캐시** → Redis(초고속, TTL). **채팅 메시지** → Cassandra(시계열, 대량 쓰기) 또는 MongoDB. **소셜 관계 탐색** → Neo4j(그래프 순회). **실시간 분석/검색** → Elasticsearch. 시나리오별 판단 근거를 설명 가능. |
| "왜 이 DB를 선택했는가?" 답변 | 데이터 구조 + 접근 패턴 + 일관성 요구 + 확장성 요구 4가지 기준으로 선택 근거를 논리적으로 설명하는 프레임워크를 적용 가능. |
| 잘못된 NoSQL 선택 사례 | "RDBMS 조인이 필요한 데이터를 MongoDB에 넣고 $lookup 남발", "강한 일관성이 필요한 금융 데이터를 Eventual Consistency DB에 저장" 같은 안티패턴을 식별 가능. |
| Polyglot Persistence 실전 | "RDBMS(핵심) + MongoDB(비정형) + Redis(캐시) + Elasticsearch(검색)"을 하나의 시스템에서 함께 쓰는 아키텍처를 설명 가능. 각 DB의 역할 분담을 설명 가능. |
| RDBMS → NoSQL 마이그레이션 전략 (심화) | 정규화된 RDBMS 데이터를 비정규화된 NoSQL 구조로 변환하는 ETL(Extract → Transform → Load) 프로세스를 설명 가능. **Zero-downtime 마이그레이션**: ① 신규 쓰기를 양쪽(RDBMS + NoSQL)에 이중 쓰기 → ② 기존 데이터를 배치로 NoSQL에 이관 → ③ 읽기를 NoSQL로 전환 → ④ 이중 쓰기 해제, RDBMS 읽기 종료. 각 단계의 위험(데이터 불일치, 이중 쓰기 실패)과 대응을 설명 가능. CDC(Change Data Capture)로 실시간 동기화하는 대안 접근을 설명 가능. |

---

## 3. 자가 검증

### 기초
- [ ] "NoSQL이란?" → 유형 4가지(Document, Key-Value, Column-Family, Graph) + 각각의 대표 DB 설명 가능
- [ ] "RDBMS vs NoSQL 선택 기준" → 4가지 판단 기준(데이터 구조, 접근 패턴, 일관성, 확장성) 설명 가능
- [ ] "Polyglot Persistence란?" → RDBMS + NoSQL 혼합 사용 패턴 설명 가능
- [ ] "ERP에서 NoSQL이 적합한 부분" → 핵심은 RDBMS, 로그/알림/대시보드는 NoSQL 가능 설명 가능

### MongoDB
- [ ] Docker로 MongoDB 기동 + mongosh로 기본 CRUD 가능
- [ ] "임베딩 vs 레퍼런싱 선택 기준" 설명 가능
- [ ] "MongoDB 문서 16MB 제한" + Unbounded Array 위험 설명 가능
- [ ] explain()으로 COLLSCAN vs IXSCAN 식별 가능

### DynamoDB
- [ ] "Partition Key + Sort Key 역할" 설명 가능
- [ ] "On-Demand vs Provisioned 모드 차이" 설명 가능
- [ ] "MongoDB vs DynamoDB 선택 기준" 설명 가능

### 트랜잭션/정합성
- [ ] "MongoDB Multi-document Transaction이란?" → 사용법 + 제약 + "남용하면 안 되는 이유" 설명 가능
- [ ] "DynamoDB Conditional Writes란?" → 낙관적 락 패턴 설명 가능
- [ ] "NoSQL에서 정합성을 보장하는 전략" → 단일 문서 원자성 → Transaction → Conditional Writes → 이벤트 기반 설명 가능

### Elasticsearch
- [ ] "Elasticsearch의 역인덱스란?" → RDBMS LIKE 대비 장점 설명 가능

### 실전
- [ ] "채팅 메시지 저장에 어떤 DB?" → 근거와 함께 답변 가능
- [ ] "잘못된 NoSQL 선택 사례" 2가지 이상 설명 가능
- [ ] "RDBMS → NoSQL 마이그레이션 시 Zero-downtime 전략" 설명 가능

---

## 4. 진행 상태

| Step | 항목 | 상태 |
|------|------|------|
| Step 1 | NoSQL 개요 | 미시작 |
| Step 2 | NoSQL 유형 | 미시작 |
| Step 3 | RDBMS vs NoSQL 선택 기준 | 미시작 |
| Step 4 | MongoDB 기초 | 미시작 |
| Step 5 | MongoDB 데이터 모델링 | 미시작 |
| Step 6 | MongoDB 인덱스와 쿼리 | 미시작 |
| Step 7 | DynamoDB 개념 | 미시작 |
| Step 8 | NoSQL 트랜잭션/정합성 | 미시작 |
| Step 9 | NoSQL 실전 + 마이그레이션 | 미시작 |

---

## 5. 참고 자료 (보조용)

| 자료 | 용도 |
|------|------|
| MongoDB 공식 문서 (docs.mongodb.com) | Step 4~6 레퍼런스 |
| AWS DynamoDB 공식 문서 | Step 7 레퍼런스 |
| DDIA Chapter 2 (Data Models) | Step 1~3 보조. 데이터 모델 이론 |

---

> 이 문서는 Claude가 미래 세션에서 읽고 학습을 안내하기 위한 가이드입니다.
> 사용자가 "NoSQL 공부하자" 또는 "Step N 하자"라고 하면, 진행 상태를 확인하고 다음 미시작 Step부터 학습_템플릿.md 형식으로 진행합니다.
> 핵심 관점: "RDBMS가 기본, NoSQL은 RDBMS로 안 되는 경우에 선택"하는 판단 능력 중심.
