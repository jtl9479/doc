# 학습 07. Kafka

## Step 목차

| Step | 항목 | 카테고리 |
|------|------|----------|
| Step 1 | 메시지 브로커 개요 — 왜 Kafka인가, Kafka vs RabbitMQ | 기초 |
| Step 2 | Kafka 환경 구축 — 설치, Docker Compose, 첫 메시지 전송 | 기초 |
| Step 3 | 핵심 개념 — Topic, Partition, Offset, Broker, Cluster | 아키텍처 |
| Step 4 | Consumer Group과 파티션 할당 | 아키텍처 |
| Step 5 | 프로듀서 — acks, retries, idempotent, 배치 | 프로듀서 |
| Step 6 | 프로듀서 심화 — 파티셔닝 전략, 직렬화, 인터셉터 | 프로듀서 |
| Step 7 | 컨슈머 — 오프셋 관리, 커밋 전략 (자동/수동) | 컨슈머 |
| Step 8 | 컨슈머 심화 — 리밸런싱, 정적 멤버십, 오류 처리 | 컨슈머 |
| Step 9 | 메시지 보장 수준 — At-Most-Once, At-Least-Once, Exactly-Once | 신뢰성 |
| Step 10 | 토픽 설계 — 파티션 수, 키 설계, 보존 정책 | 설계 |
| Step 11 | Spring Kafka 연동 — KafkaTemplate, @KafkaListener, 설정 | Spring 연동 |
| Step 12 | Spring Kafka 심화 — 에러 핸들링, 재시도, Dead Letter Topic | Spring 연동 |
| Step 13 | Kafka Streams 기초 — 스트림 처리, KTable, 윈도우 | 스트림 |
| Step 14 | 장애 시나리오 — 브로커 다운, 파티션 리밸런싱, 데이터 유실 | 운영 |
| Step 15 | 모니터링 — Consumer Lag, 메트릭, 운영 도구 | 운영 |
| Step 16 | Kafka 실전 패턴 — 이벤트 기반 아키텍처, Outbox 패턴 | 실전 |

---

## 1. 개요

**현재 수준**: Kafka 개념 인지 수준. 직접 구축/운영 경험 없음.
**학습 목표**: 프로듀서/컨슈머를 직접 구축하고, 장애 시나리오에 대응 가능. Consumer Lag을 모니터링하고 원인을 진단 가능. Spring Kafka로 실무 수준 연동 가능.
**분기 배정**: 2분기 (2026.07 ~ 2026.09)

---

## 2. 학습 순서 + 세부 항목

---

### Step 1. 메시지 브로커 개요 — 왜 Kafka인가, Kafka vs RabbitMQ

| 학습 항목 | 학습 목표 |
|----------|----------|
| 메시지 브로커란 | 시스템 간 비동기 통신을 중개하는 미들웨어. 동기 호출(HTTP) 대비 비동기 메시징의 장점(결합도 감소, 버퍼링, 피크 부하 흡수)을 설명 가능. |
| 왜 Kafka인가 | 높은 처리량(초당 수백만 메시지), 내구성(디스크 기반 로그), 수평 확장성(파티션), 이벤트 재생 가능(오프셋 기반)이 Kafka의 핵심 강점임을 설명 가능. |
| Kafka vs RabbitMQ | Kafka: 이벤트 로그(소비 후에도 보존, 재생 가능), 높은 처리량, 순서 보장(파티션 내). RabbitMQ: 전통적 메시지 큐(소비 후 삭제), 유연한 라우팅, 메시지 우선순위. 선택 기준(이벤트 스트리밍 = Kafka, 작업 큐/라우팅 = RabbitMQ)을 설명 가능. |
| 메시지 큐 vs 이벤트 로그 | "소비하면 사라지는 큐" vs "소비해도 남아있는 로그"의 근본적 차이를 설명 가능. Kafka가 로그 기반이라 컨슈머 그룹마다 독립적으로 소비 가능한 이유를 설명 가능. |

---

### Step 2. Kafka 환경 구축 — 설치, Docker Compose, 첫 메시지 전송

| 학습 항목 | 학습 목표 |
|----------|----------|
| Kafka 구성 요소 | Kafka Broker, ZooKeeper(또는 KRaft), Producer, Consumer가 각각 무슨 역할인지, 어떻게 연결되는지 전체 구성도를 그릴 수 있음. |
| Docker Compose로 Kafka 실행 | docker-compose.yml로 ZooKeeper + Kafka Broker를 로컬에서 기동하는 방법. 포트 매핑(9092), 환경 변수(KAFKA_ADVERTISED_LISTENERS 등) 설정을 이해. |
| kafka CLI 도구 기본 | kafka-topics.sh(토픽 생성/조회/삭제), kafka-console-producer.sh(CLI로 메시지 전송), kafka-console-consumer.sh(CLI로 메시지 수신) 사용 가능. |
| 첫 메시지 전송 실습 | 토픽 생성 → CLI Producer로 메시지 전송 → CLI Consumer로 수신까지 전체 흐름을 직접 실행 가능. "메시지가 어디에 저장되고 어떻게 꺼내지는지" 체감. |
| 멀티 브로커 실습 | Docker Compose로 브로커 3대 구성. 파티션과 복제본(replication factor)이 여러 브로커에 분산되는 것을 확인 가능. |

---

### Step 3. 핵심 개념 — Topic, Partition, Offset, Broker, Cluster

| 학습 항목 | 학습 목표 |
|----------|----------|
| Topic | 메시지가 저장되는 논리적 카테고리. 하나의 Topic이 여러 Partition으로 나뉘는 이유(병렬 처리)를 설명 가능. |
| Partition | 순서가 보장되는 불변 로그. 파티션 내에서만 메시지 순서가 보장됨을 설명 가능. 파티션 수 = 최대 컨슈머 병렬 수임을 설명 가능. |
| Offset | 파티션 내 각 메시지의 고유 번호(0부터 시작, 단조 증가). 컨슈머가 "어디까지 읽었는가"를 추적하는 기준임을 설명 가능. |
| Broker | Kafka 서버 1대 = 1 Broker. 여러 Broker가 Cluster를 구성하여 파티션을 분산 저장. |
| Leader / Follower Replica | 각 파티션에 Leader 1개 + Follower N개. 쓰기/읽기는 Leader에서, Follower는 복제만. Leader 장애 시 Follower가 승격. ISR(In-Sync Replica)의 의미를 설명 가능. |
| ZooKeeper / KRaft | ZooKeeper: 기존 클러스터 메타데이터 관리. KRaft(Kafka Raft): ZooKeeper 없이 자체 합의. Kafka 3.x+에서 KRaft로 전환 중인 이유를 알고 있음. |
| Kafka 고성능 비결 — Sequential I/O | Kafka는 메시지를 디스크에 순차적(Sequential)으로 쓰고 읽음. 랜덤 I/O 대비 순차 I/O가 수백 배 빠른 이유(디스크 헤드 이동 없음, OS 프리페치 활용)를 설명 가능. |
| Kafka 고성능 비결 — OS Page Cache | Kafka가 자체 캐시 대신 OS의 Page Cache를 활용하는 이유(JVM 힙 외부 → GC 영향 없음, OS가 최적화)를 설명 가능. 프로듀서가 쓴 데이터가 Page Cache에 있을 때 컨슈머가 디스크 접근 없이 읽는 원리를 설명 가능. |
| Kafka 고성능 비결 — Zero Copy | 일반 전송(디스크 → 커널 버퍼 → 유저 버퍼 → 소켓 버퍼 → NIC, 4번 복사) vs Zero Copy(디스크 → 커널 버퍼 → NIC, sendfile() 시스템 콜로 2번 복사)의 차이를 설명 가능. CPU 개입 없이 데이터를 네트워크로 전송하여 처리량을 극대화하는 원리를 설명 가능. |

---

### Step 4. Consumer Group과 파티션 할당

| 학습 항목 | 학습 목표 |
|----------|----------|
| Consumer Group | 같은 Consumer Group의 컨슈머들이 파티션을 나눠서 소비하는 구조를 설명 가능. 1개 파티션은 그룹 내 1개 컨슈머에만 할당됨을 설명 가능. |
| 병렬 처리 | 파티션 수 ≥ 컨슈머 수일 때 최대 병렬 처리. 컨슈머가 파티션보다 많으면 놀게 되는 이유를 설명 가능. |
| 다중 Consumer Group | 같은 Topic을 여러 Consumer Group이 독립적으로 소비 가능(각 그룹이 자기 오프셋 관리). "주문 이벤트를 결제 서비스와 알림 서비스가 각각 소비"하는 패턴을 설명 가능. |
| Partition Assignment Strategy | Range, RoundRobin, Sticky, CooperativeSticky 전략의 차이를 개념 수준 설명 가능. |

---

### Step 5. 프로듀서 — acks, retries, idempotent, 배치

| 학습 항목 | 학습 목표 |
|----------|----------|
| acks 설정 | acks=0(전송 후 확인 안 함, 최고 속도, 유실 가능), acks=1(Leader 기록 확인), acks=all/-1(모든 ISR 기록 확인, 가장 안전). 각각의 트레이드오프(속도 vs 내구성)를 설명 가능. |
| retries + retry.backoff.ms | 전송 실패 시 재시도 횟수와 간격. 재시도로 인한 메시지 순서 역전 문제와 max.in.flight.requests.per.connection=1 또는 enable.idempotence=true로 방지하는 방법을 설명 가능. |
| Idempotent Producer | enable.idempotence=true로 프로듀서 중복 전송 방지. PID(Producer ID) + Sequence Number로 브로커가 중복 감지하는 원리를 설명 가능. |
| 배치 (Batching) | linger.ms(배치 대기 시간)와 batch.size(배치 크기)의 관계. 배치가 처리량을 높이는 이유(네트워크 왕복 감소)와 지연시간 트레이드오프를 설명 가능. |
| buffer.memory + max.block.ms | 프로듀서 내부 버퍼가 가득 차면 블로킹되는 동작을 설명 가능. |

---

### Step 6. 프로듀서 심화 — 파티셔닝 전략, 직렬화, 인터셉터

| 학습 항목 | 학습 목표 |
|----------|----------|
| 파티셔닝 전략 | 키가 있으면 키의 해시값으로 파티션 결정(같은 키 = 같은 파티션 = 순서 보장), 키가 없으면 라운드로빈 또는 Sticky Partitioner. 키 설계가 순서 보장과 부하 분산에 미치는 영향을 설명 가능. |
| 직렬화 (Serializer) | StringSerializer, JsonSerializer, Avro/Protobuf Serializer의 차이. 스키마 레지스트리(Confluent Schema Registry)의 역할을 개념 수준 설명 가능. |
| ProducerInterceptor | 메시지 전송 전/후에 가로채는 메커니즘. 로깅, 메트릭 수집에 활용 가능. |
| 커스텀 파티셔너 | 기본 해시 파티셔닝 외 비즈니스 요구에 맞는 커스텀 파티셔너(예: 지역별, 우선순위별)를 구현하는 시나리오를 설명 가능. |

---

### Step 7. 컨슈머 — 오프셋 관리, 커밋 전략 (자동/수동)

| 학습 항목 | 학습 목표 |
|----------|----------|
| 오프셋 관리 | 컨슈머가 소비한 위치(오프셋)를 __consumer_offsets 토픽에 저장하는 구조를 설명 가능. |
| 자동 커밋 (enable.auto.commit=true) | 주기적(auto.commit.interval.ms)으로 오프셋 자동 커밋. 처리 완료 전에 커밋되면 데이터 유실, 커밋 후 처리 실패하면 중복 처리 가능성을 설명 가능. |
| 수동 커밋 | commitSync()(블로킹, 확실), commitAsync()(논블로킹, 실패 가능)의 차이. 처리 완료 후 커밋하는 패턴(At-Least-Once)을 적용 가능. |
| poll() 루프 | 컨슈머의 기본 동작이 poll() 반복임을 이해. max.poll.records, max.poll.interval.ms 설정의 의미와 튜닝 기준을 설명 가능. |
| auto.offset.reset | earliest(처음부터), latest(최신부터), none(오프셋 없으면 에러). 컨슈머 그룹이 처음 접속하거나 오프셋이 만료됐을 때의 동작을 설명 가능. |

---

### Step 8. 컨슈머 심화 — 리밸런싱, 정적 멤버십, 오류 처리

| 학습 항목 | 학습 목표 |
|----------|----------|
| 리밸런싱 (Rebalancing) | 컨슈머 추가/제거/장애 시 파티션 재할당이 발생하는 과정을 설명 가능. 리밸런싱 중 전체 컨슈머가 일시 정지되는 문제(Stop-the-World)를 설명 가능. |
| Cooperative Rebalancing | Eager(전체 파티션 해제 후 재할당) vs Cooperative(변경된 파티션만 재할당, 나머지는 계속 소비)의 차이를 설명 가능. |
| 정적 멤버십 (Static Membership) | group.instance.id 설정으로 리밸런싱 빈도를 줄이는 방법. 컨슈머 재시작 시 같은 파티션을 다시 받는 이유를 설명 가능. |
| 컨슈머 지연 감지 | max.poll.interval.ms 초과 시 컨슈머가 죽은 것으로 판단 → 리밸런싱 발생. 처리가 오래 걸리는 메시지로 인한 의도치 않은 리밸런싱 대응을 설명 가능. |
| Rebalance Storm (심화) | 특정 컨슈머가 느려짐 → max.poll.interval.ms 초과 → 리밸런싱 발생 → 리밸런싱 중 다른 컨슈머도 처리 중단 → Lag 폭증 → 리밸런싱 완료 후 밀린 메시지 처리에 또 시간 초과 → 또 리밸런싱 → **폭포수 장애(Rebalance Storm)** 시나리오를 설명 가능. 대응: ① Cooperative Rebalancing 적용(변경 파티션만 재할당), ② 정적 멤버십(리밸런싱 빈도 감소), ③ max.poll.interval.ms/max.poll.records 적절 튜닝, ④ 처리 시간이 긴 메시지는 별도 스레드로 분리. |
| 오류 처리 전략 | 처리 실패 시 재시도 → 재시도 실패 시 Dead Letter Topic 전송 → 나중에 수동 처리하는 패턴을 설명 가능. |

---

### Step 9. 메시지 보장 수준 — At-Most-Once, At-Least-Once, Exactly-Once

| 학습 항목 | 학습 목표 |
|----------|----------|
| At-Most-Once | 메시지 유실 가능, 중복 없음. 오프셋 먼저 커밋 → 처리 실패해도 재처리 안 함. 로그/메트릭처럼 유실 허용 가능한 경우에 사용. |
| At-Least-Once | 메시지 유실 없음, 중복 가능. 처리 완료 후 커밋. 컨슈머 장애 시 마지막 커밋 이후 메시지 재처리. 대부분의 실무에서 기본 선택인 이유를 설명 가능. |
| Exactly-Once (EOS) | 유실도 중복도 없음. Kafka Transaction(Transactional Producer + read_committed Consumer)으로 달성하는 원리를 설명 가능. 성능 오버헤드가 있는 이유를 설명 가능. |
| 멱등성(Idempotency)으로 보완 | At-Least-Once + 컨슈머 측 멱등성(같은 메시지 2번 처리해도 결과 동일)으로 실질적 Exactly-Once 효과를 달성하는 실무 패턴을 설명 가능. |
| 보장 수준 선택 기준 | "이 비즈니스에서 유실과 중복 중 어떤 게 더 위험한가?"로 판단. 결제 = EOS 또는 At-Least-Once + 멱등성, 로그 = At-Most-Once 가능. |

---

### Step 10. 토픽 설계 — 파티션 수, 키 설계, 보존 정책

| 학습 항목 | 학습 목표 |
|----------|----------|
| 파티션 수 결정 | 파티션 수 = 최대 컨슈머 병렬 수. 너무 적으면 처리량 한계, 너무 많으면 브로커 부하(파일 핸들, 리밸런싱 비용) 증가. 초기 설계 기준(목표 처리량 / 파티션당 처리량)을 설명 가능. 파티션 수는 늘릴 수 있지만 줄일 수 없는 제약을 설명 가능. |
| 키 설계 | 같은 키 = 같은 파티션 = 순서 보장. 주문ID를 키로 쓰면 같은 주문의 이벤트가 순서대로 처리되는 이유를 설명 가능. 핫키(특정 키에 트래픽 집중) 문제와 대응을 설명 가능. |
| 보존 정책 (Retention) | retention.ms(시간 기반, 기본 7일), retention.bytes(용량 기반)의 역할. 비즈니스 요구에 따른 보존 기간 설정 판단 가능. |
| Compacted Topic | 키별 최신 값만 유지하는 보존 방식. 설정(cleanup.policy=compact)과 활용(상태 저장, 설정 전파)을 설명 가능. |
| 토픽 네이밍 컨벤션 | domain.event-type(예: order.created, payment.completed) 같은 네이밍 규칙의 중요성을 설명 가능. |
| 이벤트 스키마 진화 (심화) | 운영 중 메시지 포맷이 변경될 때 구버전/신버전 컨슈머가 동시에 동작해야 하는 문제를 설명 가능. **전방 호환성**(Forward Compatibility: 새 스키마로 쓴 데이터를 구 컨슈머가 읽음 — 새 필드 무시), **후방 호환성**(Backward Compatibility: 구 스키마로 쓴 데이터를 새 컨슈머가 읽음 — 새 필드에 기본값)의 차이를 설명 가능. 호환성을 보장하는 실전 규칙(필드 추가는 Optional + 기본값, 필드 삭제 금지 또는 단계적 폐기, 필드 타입 변경 금지)을 설명 가능. Avro + Schema Registry를 사용하면 스키마 호환성을 자동 검증하는 이유를 개념 수준 설명 가능. |

---

### Step 11. Spring Kafka 연동 — KafkaTemplate, @KafkaListener, 설정

| 학습 항목 | 학습 목표 |
|----------|----------|
| spring-kafka 의존성 | Spring Boot에서 spring-kafka 스타터 추가 시 자동 설정되는 항목을 알고 있음. |
| KafkaTemplate | 메시지 전송 API. send(topic, key, value) 사용 가능. 비동기 전송 + ListenableFuture/CompletableFuture 콜백 처리 가능. |
| @KafkaListener | 어노테이션 기반 컨슈머. topics, groupId, containerFactory 설정. 메서드 파라미터로 메시지 값, ConsumerRecord, Acknowledgment 받는 방법을 적용 가능. |
| application.yml 설정 | spring.kafka.bootstrap-servers, producer/consumer 직렬화, acks, auto-offset-reset 등 핵심 설정을 작성 가능. |
| ConsumerFactory / ProducerFactory | 커스텀 설정이 필요할 때 Factory 빈을 직접 정의하는 방법을 알고 있음. |

---

### Step 12. Spring Kafka 심화 — 에러 핸들링, 재시도, Dead Letter Topic

| 학습 항목 | 학습 목표 |
|----------|----------|
| ErrorHandler | DefaultErrorHandler(Spring Kafka 2.8+)의 역할. 예외 발생 시 재시도 + 최종 실패 시 Dead Letter Topic 전송 설정을 적용 가능. |
| 재시도 설정 | FixedBackOff, ExponentialBackOff로 재시도 간격 설정 가능. RetryableTopic 어노테이션 기반 재시도 토픽 체인(retry-1, retry-2, dlt) 구성을 알고 있음. |
| Dead Letter Topic (DLT) | 처리 불가능한 메시지를 별도 토픽에 보관하여 나중에 수동/자동 재처리하는 패턴을 적용 가능. |
| 수동 Acknowledgment | AckMode.MANUAL_IMMEDIATE로 직접 ack/nack 제어. 처리 성공 시에만 커밋하는 패턴을 적용 가능. |
| Poison Pill 처리 | 역직렬화 자체가 실패하는 메시지(형식 오류 등) 대응. ErrorHandlingDeserializer 설정을 알고 있음. |

---

### Step 13. Kafka Streams 기초 — 스트림 처리, KTable, 윈도우

| 학습 항목 | 학습 목표 |
|----------|----------|
| Kafka Streams란 | Kafka 위에서 동작하는 스트림 처리 라이브러리. 별도 클러스터(Spark, Flink) 없이 애플리케이션 내에서 실행 가능한 장점을 설명 가능. |
| KStream vs KTable | KStream: 이벤트 스트림(모든 레코드가 독립적). KTable: 변경 로그(키별 최신 값 유지). 차이를 설명 가능. |
| 기본 연산 | filter, map, flatMap, groupByKey, count, reduce 등 스트림 변환 연산을 개념 수준 설명 가능. |
| 윈도우 (Windowing) | Tumbling Window(겹치지 않는 고정 크기), Hopping Window(겹치는 고정 크기), Session Window(활동 기반)의 차이를 설명 가능. |
| 상태 저장소 (State Store) | RocksDB 기반 로컬 상태 저장소의 역할. Changelog Topic으로 상태를 복구하는 메커니즘을 개념 수준 설명 가능. |

---

### Step 14. 장애 시나리오 — 브로커 다운, 파티션 리밸런싱, 데이터 유실

| 학습 항목 | 학습 목표 |
|----------|----------|
| 브로커 장애 | Leader 브로커 다운 시 ISR의 Follower가 Leader로 승격되는 과정을 설명 가능. min.insync.replicas와 acks=all 조합이 데이터 유실을 방지하는 원리를 설명 가능. |
| Unclean Leader Election | ISR에 없는 Follower가 Leader로 승격(데이터 유실 가능)하는 상황. unclean.leader.election.enable=false(기본)로 방지하는 이유를 설명 가능. |
| 컨슈머 장애와 리밸런싱 | 컨슈머 1대 죽으면 나머지 컨슈머가 파티션을 재할당받는 과정. 리밸런싱 중 처리 지연 발생을 설명 가능. |
| 데이터 유실 시나리오 | acks=1 + Leader 장애(Follower에 복제 안 된 메시지 유실), 자동 커밋 + 처리 전 장애(오프셋은 커밋됐지만 처리 안 됨) 등 구체적 유실 시나리오를 설명 가능. |
| 프로듀서 장애 | 프로듀서 장애 시 buffer.memory의 미전송 메시지 유실. 콜백/Future로 전송 실패를 감지하고 재시도하는 패턴을 설명 가능. |

---

### Step 15. 모니터링 — Consumer Lag, 메트릭, 운영 도구

| 학습 항목 | 학습 목표 |
|----------|----------|
| Consumer Lag | Lag = 파티션의 최신 오프셋 - 컨슈머가 커밋한 오프셋. Lag이 증가하면 "소비 속도 < 생산 속도"임을 설명 가능. Lag이 계속 증가하는 원인(컨슈머 처리 느림, 컨슈머 다운, 파티션 수 부족)을 진단 가능. |
| 핵심 메트릭 | 프로듀서: record-send-rate, request-latency. 컨슈머: records-lag, records-consumed-rate, commit-rate. 브로커: UnderReplicatedPartitions, ActiveControllerCount를 알고 있음. |
| kafka-consumer-groups.sh | --describe로 그룹별 Lag 조회하는 방법. --reset-offsets로 오프셋 재설정하는 방법(주의사항 포함)을 알고 있음. |
| 모니터링 도구 | Kafka Manager(CMAK), Burrow(Lag 모니터링), Prometheus + Grafana(JMX Exporter 연동)로 대시보드를 구성하는 구조를 알고 있음. |
| 알림 설정 | "Consumer Lag > 임계값" 알림을 설정하여 장애를 조기 감지하는 운영 패턴을 설명 가능. |

---

### Step 16. Kafka 실전 패턴 — 이벤트 기반 아키텍처, Outbox 패턴

| 학습 항목 | 학습 목표 |
|----------|----------|
| 이벤트 기반 아키텍처 | 서비스 간 동기 호출(HTTP) 대신 이벤트(Kafka) 기반 비동기 통신으로 결합도를 낮추는 패턴을 설명 가능. 장점(결합도 감소, 확장성)과 단점(디버깅 어려움, 순서 보장 복잡성)을 설명 가능. |
| Outbox 패턴 | DB 트랜잭션 + Kafka 전송의 원자성 문제(DB는 커밋됐는데 Kafka 전송 실패)를 설명 가능. Outbox 테이블에 이벤트를 DB 트랜잭션으로 저장 → 별도 프로세스(CDC 또는 폴링)가 Kafka로 전송하는 패턴을 설명 가능. |
| CDC (Change Data Capture) | Debezium 등을 통해 DB 변경 사항을 자동으로 Kafka로 전파하는 방식. Outbox 패턴의 CDC 방식 구현을 개념 수준 설명 가능. |
| 이벤트 설계 원칙 | 이벤트에 필요한 정보를 충분히 담기(Fat Event) vs 최소 정보만 담기(Thin Event + 조회)의 트레이드오프를 설명 가능. 이벤트 버전 관리(스키마 진화)의 중요성을 설명 가능. |
| ERP 도메인 연결 | "수주 확정 → 재고 차감 → 출고 지시 → 매출 반영"의 흐름을 Kafka 이벤트로 연결하는 설계를 설명 가능. |

---

## 3. 자가 검증

### 기초 / 환경
- [ ] Docker Compose로 Kafka 클러스터(브로커 3대)를 기동 가능
- [ ] CLI로 토픽 생성 → 메시지 전송 → 메시지 수신 직접 실행 가능
- [ ] Kafka 전체 구성도(Broker, ZooKeeper/KRaft, Producer, Consumer) 그림 가능

### 핵심 개념
- [ ] "Kafka의 파티션은 왜 필요한가?" → 병렬 처리 + 순서 보장(파티션 내) 설명 가능
- [ ] "Consumer Group이란?" → 파티션 분배 + 다중 그룹 독립 소비 설명 가능
- [ ] "Kafka가 RabbitMQ와 근본적으로 다른 점" → 이벤트 로그 vs 메시지 큐 설명 가능
- [ ] "Kafka가 디스크 기반인데 왜 빠른가?" → Sequential I/O + OS Page Cache + Zero Copy 설명 가능

### 프로듀서
- [ ] "acks=0 vs 1 vs all 차이" → 속도 vs 내구성 트레이드오프 설명 가능
- [ ] "Idempotent Producer란?" → PID + Sequence Number 중복 방지 설명 가능
- [ ] "배치 설정(linger.ms, batch.size)의 트레이드오프" 설명 가능

### 컨슈머
- [ ] "자동 커밋 vs 수동 커밋 차이와 위험" 설명 가능
- [ ] "리밸런싱이란? 왜 문제가 되는가?" → Stop-the-World + Cooperative 대안 설명 가능
- [ ] "Rebalance Storm이란?" → 느린 컨슈머 → 리밸런싱 연쇄 → 폭포수 장애 시나리오 + 대응 전략 설명 가능
- [ ] "auto.offset.reset 옵션 3가지" 설명 가능

### 신뢰성
- [ ] "Kafka에서 Exactly-Once Semantics를 어떻게 달성하는가?" → Transactional Producer + read_committed + 컨슈머 멱등성 설명 가능
- [ ] "At-Least-Once + 멱등성으로 실질적 EOS를 달성하는 패턴" 설명 가능
- [ ] "acks=1에서 Leader 장애 시 데이터 유실 시나리오" 설명 가능

### Spring 연동
- [ ] KafkaTemplate + @KafkaListener로 메시지 송수신 구현 가능
- [ ] Dead Letter Topic 설정 + 재시도 전략 구현 가능
- [ ] Poison Pill 메시지 대응 설명 가능

### 운영
- [ ] Consumer Lag의 의미와 원인 진단 가능
- [ ] "Lag이 계속 증가하면 어떻게 대응하는가?" → 컨슈머 확장, 파티션 추가, 처리 최적화 설명 가능
- [ ] kafka-consumer-groups.sh로 Lag 조회 + 오프셋 재설정 가능

### 실전 패턴
- [ ] "Outbox 패턴이란?" → DB 트랜잭션 + Kafka 원자성 문제 해결 설명 가능
- [ ] "이벤트 기반 아키텍처의 장단점" 설명 가능
- [ ] "운영 중 메시지 포맷을 바꿔야 할 때 어떻게 하는가?" → Forward/Backward Compatibility + 실전 규칙 설명 가능

---

## 4. 진행 상태

| Step | 항목 | 상태 |
|------|------|------|
| Step 1 | 메시지 브로커 개요 | 미시작 |
| Step 2 | Kafka 환경 구축 | 미시작 |
| Step 3 | 핵심 개념 | 미시작 |
| Step 4 | Consumer Group | 미시작 |
| Step 5 | 프로듀서 기본 | 미시작 |
| Step 6 | 프로듀서 심화 | 미시작 |
| Step 7 | 컨슈머 기본 | 미시작 |
| Step 8 | 컨슈머 심화 | 미시작 |
| Step 9 | 메시지 보장 수준 | 미시작 |
| Step 10 | 토픽 설계 | 미시작 |
| Step 11 | Spring Kafka 기본 | 미시작 |
| Step 12 | Spring Kafka 심화 | 미시작 |
| Step 13 | Kafka Streams 기초 | 미시작 |
| Step 14 | 장애 시나리오 | 미시작 |
| Step 15 | 모니터링 | 미시작 |
| Step 16 | 실전 패턴 | 미시작 |

---

## 5. 참고 자료 (보조용)

| 자료 | 용도 |
|------|------|
| Kafka: The Definitive Guide (O'Reilly) | Step 1~9 보조. 핵심 개념/아키텍처 |
| Apache Kafka 공식 문서 | 전 Step 설정/API 레퍼런스 |
| Spring Kafka 공식 문서 | Step 10~11 보조 |
| Confluent 블로그/문서 | Kafka Streams, Schema Registry 참고 |

---

> 이 문서는 Claude가 미래 세션에서 읽고 학습을 안내하기 위한 가이드입니다.
> 사용자가 "Kafka 공부하자" 또는 "Step N 하자"라고 하면, 진행 상태를 확인하고 다음 미시작 Step부터 학습_템플릿.md 형식으로 진행합니다.
