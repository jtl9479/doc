# 26장: 데이터베이스 스키마 관리 (Flyway & Liquibase)

> **"데이터베이스 변경 사항도 Git처럼 버전 관리하세요"**

---

## 📋 학습 목표

이 장을 학습하면 다음을 할 수 있습니다:

- 데이터베이스 마이그레이션의 필요성을 이해합니다
- Flyway를 사용하여 스키마 버전 관리를 할 수 있습니다
- Liquibase의 개념과 활용 방법을 이해합니다
- 마이그레이션 파일을 작성하고 실행할 수 있습니다
- 운영 환경에서 안전하게 스키마를 변경할 수 있습니다
- Rollback과 버전 관리 전략을 수립할 수 있습니다

**예상 학습 시간**: 3-4시간
**난이도**: ⭐⭐⭐ (중급)

---

## 🤔 왜 데이터베이스 마이그레이션 도구가 필요한가?

### 문제 상황: 수동 스키마 관리의 악몽

```sql
-- 개발자 A: 로컬에서 테이블 수정
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- 개발자 B: 같은 테이블을 다르게 수정
ALTER TABLE users ADD COLUMN phone_number VARCHAR(15);

-- 운영 서버: 누가 언제 어떤 변경을 했는지 모름
-- 개발/스테이징/운영 서버의 스키마가 모두 다름!
```

**실제 개발 현장의 문제:**

1. **버전 관리 부재**
   ```
   문제: "이 컬럼은 누가 언제 추가했죠?"
   → SQL 파일은 있지만 실행 여부를 알 수 없음
   ```

2. **환경 간 불일치**
   ```
   로컬: users 테이블에 phone 컬럼 있음
   개발: users 테이블에 phone_number 컬럼 있음
   운영: users 테이블에 두 컬럼 모두 없음
   ```

3. **배포 시 누락**
   ```
   개발자: "코드는 배포했는데 DB 스키마 변경을 깜빡했어요!"
   → 애플리케이션 에러 발생
   ```

4. **롤백 불가**
   ```
   문제 발생 → 코드는 롤백했는데 DB는?
   → 수동으로 ALTER TABLE DROP COLUMN 실행?
   ```

### 마이그레이션 도구의 해결책

```
┌──────────────────────────────────────┐
│ Git (코드 버전 관리)                  │
│ - V1: 초기 코드                       │
│ - V2: 기능 추가                       │
│ - V3: 버그 수정                       │
└──────────────────────────────────────┘
              ↓ 동일한 방식으로
┌──────────────────────────────────────┐
│ Flyway/Liquibase (DB 버전 관리)      │
│ - V1: 초기 스키마                     │
│ - V2: 컬럼 추가                       │
│ - V3: 인덱스 생성                     │
└──────────────────────────────────────┘
```

**마이그레이션 도구의 핵심 가치:**
- 스키마 변경 이력을 코드로 관리
- 모든 환경에서 동일한 스키마 보장
- 자동 실행으로 휴먼 에러 방지
- 변경 이력 추적 및 감사 가능

---

## 🌍 실생활 비유로 이해하는 DB 마이그레이션

### 비유 1: 건물 리모델링 설계도

**수동 관리 (문제):**
```
작업자 A: "2층에 방을 하나 추가했습니다"
작업자 B: "3층 화장실을 옮겼습니다"
건물주: "현재 건물 구조가 정확히 어떻게 되죠?"
→ 설계도 없이 구두로만 전달, 현황 파악 불가
```

**마이그레이션 (해결책):**
```
V1_initial_building.sql        → 초기 설계도
V2_add_room_floor2.sql         → 2층 방 추가
V3_move_bathroom_floor3.sql    → 3층 화장실 이동

→ 모든 변경 이력이 문서화되어 있음
→ 순서대로 실행하면 동일한 건물 완성
```

### 비유 2: 소프트웨어 업데이트

**Windows 업데이트:**
```
Windows 10 → 10.1 → 10.2 → 11.0
각 버전이 이전 버전을 기반으로 순차적 업데이트
중간 버전을 건너뛰면 문제 발생
```

**DB 마이그레이션:**
```
Schema V1 → V2 → V3 → V4
V1__create_users_table.sql
V2__add_email_column.sql
V3__create_orders_table.sql
V4__add_index_on_email.sql

→ 순서대로 실행되며, 중간 버전 건너뛰기 방지
```

### 비유 3: Git 커밋 히스토리

**Git:**
```
commit 1: Initial commit
commit 2: Add user feature
commit 3: Fix bug

→ 모든 변경 이력이 남아있고, 특정 시점으로 되돌리기 가능
```

**Flyway/Liquibase:**
```
V1__initial_schema.sql
V2__add_user_table.sql
V3__fix_column_type.sql

→ 모든 스키마 변경이 파일로 저장
→ 실행 이력이 DB에 기록됨
→ 특정 버전으로 롤백 가능
```

---

## 💡 Flyway 핵심 개념

### 1️⃣ 초급: Flyway란?

**Flyway = 데이터베이스의 Git**

```
┌─────────────────────────────────────┐
│ Application Code                    │
│ ├─ src/main/java                    │
│ └─ src/main/resources/db/migration  │ ← SQL 파일 위치
│    ├─ V1__create_users_table.sql    │
│    ├─ V2__add_email_column.sql      │
│    └─ V3__create_orders_table.sql   │
└─────────────────────────────────────┘
              ↓ 애플리케이션 시작 시
┌─────────────────────────────────────┐
│ Database                            │
│ ├─ users (V1, V2에서 생성/수정)     │
│ ├─ orders (V3에서 생성)             │
│ └─ flyway_schema_history            │ ← 실행 이력 저장
└─────────────────────────────────────┘
```

#### 마이그레이션 파일 명명 규칙

```
V{버전}__{설명}.sql

예시:
V1__create_users_table.sql
V2__add_email_to_users.sql
V2.1__add_phone_to_users.sql
V3__create_orders_table.sql

규칙:
- V: Version (필수)
- 버전 번호: 숫자, 점(.), 언더스코어(_) 사용 가능
- __: 구분자 (언더스코어 2개, 필수)
- 설명: snake_case 권장
```

#### Flyway 동작 원리

```
1. 애플리케이션 시작
   ↓
2. db/migration 폴더의 SQL 파일 스캔
   ↓
3. flyway_schema_history 테이블 확인
   - 어떤 마이그레이션이 실행되었는지 기록
   ↓
4. 미실행된 마이그레이션만 순차 실행
   ↓
5. 실행 결과를 flyway_schema_history에 기록
```

**flyway_schema_history 테이블:**

| installed_rank | version | description | type | script | checksum | installed_on | execution_time | success |
|----------------|---------|-------------|------|--------|----------|--------------|----------------|---------|
| 1 | 1 | create users table | SQL | V1__create_users_table.sql | 123456 | 2025-01-15 10:00:00 | 50 | true |
| 2 | 2 | add email column | SQL | V2__add_email_column.sql | 789012 | 2025-01-15 10:00:01 | 20 | true |

### 2️⃣ 중급: Flyway 실전 활용

#### 마이그레이션 파일 종류

**1. Versioned Migration (V)**
```sql
-- V1__create_users_table.sql
-- 한 번만 실행, 순서 보장
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**2. Repeatable Migration (R)**
```sql
-- R__create_user_view.sql
-- 체크섬이 변경될 때마다 재실행 (View, Procedure, Function)
CREATE OR REPLACE VIEW active_users AS
SELECT * FROM users WHERE status = 'ACTIVE';
```

**3. Undo Migration (U) - Pro 버전**
```sql
-- U1__create_users_table.sql
-- V1의 롤백 스크립트
DROP TABLE users;
```

#### 실전 마이그레이션 예시

```sql
-- V1__initial_schema.sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- V2__add_email_to_users.sql
ALTER TABLE users
ADD COLUMN email VARCHAR(255);

ALTER TABLE users
ADD CONSTRAINT uk_email UNIQUE (email);

-- V3__add_status_to_users.sql
ALTER TABLE users
ADD COLUMN status VARCHAR(20) DEFAULT 'ACTIVE';

CREATE INDEX idx_users_status ON users(status);

-- V4__add_view_count_to_posts.sql
ALTER TABLE posts
ADD COLUMN view_count INT DEFAULT 0;

-- V5__create_comments_table.sql
CREATE TABLE comments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
```

### 3️⃣ 고급: Flyway 명령어와 전략

#### Flyway CLI 명령어

```bash
# 1. migrate - 마이그레이션 실행
flyway migrate

# 2. info - 현재 상태 확인
flyway info
# 출력 예시:
# +-----------+---------+---------------------+--------+
# | Version   | State   | Description         | Type   |
# +-----------+---------+---------------------+--------+
# | 1         | Success | create users table  | SQL    |
# | 2         | Pending | add email column    | SQL    |
# +-----------+---------+---------------------+--------+

# 3. validate - 변경 감지
flyway validate

# 4. clean - 모든 객체 삭제 (개발용만!)
flyway clean

# 5. baseline - 기존 DB에 Flyway 도입
flyway baseline -baselineVersion=1

# 6. repair - 실패한 마이그레이션 수정
flyway repair
```

---

## 🛠️ 기본 실습 1: Flyway 설정

### Step 1: 의존성 추가

```gradle
// build.gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.flywaydb:flyway-core'
    implementation 'org.flywaydb:flyway-mysql'  // MySQL 사용 시
    runtimeOnly 'com.mysql.cj:mysql-connector-j'
}
```

### Step 2: application.yml 설정

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?serverTimezone=Asia/Seoul
    username: root
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver

  jpa:
    hibernate:
      ddl-auto: validate  # Flyway 사용 시 필수! (validate 또는 none)
    properties:
      hibernate:
        format_sql: true
        show_sql: false

  flyway:
    enabled: true
    baseline-on-migrate: true  # 기존 DB에 Flyway 도입 시
    locations: classpath:db/migration  # 기본값
    sql-migration-suffixes: .sql
    encoding: UTF-8
    validate-on-migrate: true  # 마이그레이션 전 검증
    out-of-order: false  # 순서 엄격하게 유지
    # baseline-version: 1  # 기존 DB의 시작 버전

logging:
  level:
    org.flywaydb: DEBUG
```

### Step 3: 마이그레이션 파일 작성

**디렉토리 구조:**
```
src/main/resources/
└── db/
    └── migration/
        ├── V1__create_users_table.sql
        ├── V2__create_posts_table.sql
        ├── V3__add_email_to_users.sql
        └── R__create_views.sql
```

**V1__create_users_table.sql:**
```sql
-- 사용자 테이블 생성
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 인덱스 생성
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);
```

**V2__create_posts_table.sql:**
```sql
-- 게시글 테이블 생성
CREATE TABLE posts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    view_count INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'PUBLISHED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_posts_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 인덱스
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_posts_created_at ON posts(created_at);
```

**V3__add_phone_to_users.sql:**
```sql
-- 사용자 테이블에 전화번호 컬럼 추가
ALTER TABLE users
ADD COLUMN phone VARCHAR(20) AFTER email;

-- 전화번호 인덱스
CREATE INDEX idx_users_phone ON users(phone);
```

**R__create_views.sql (반복 실행):**
```sql
-- 활성 사용자 뷰
CREATE OR REPLACE VIEW active_users AS
SELECT id, username, email, phone, created_at
FROM users
WHERE status = 'ACTIVE';

-- 인기 게시글 뷰
CREATE OR REPLACE VIEW popular_posts AS
SELECT p.id, p.title, p.view_count, u.username, p.created_at
FROM posts p
JOIN users u ON p.user_id = u.id
WHERE p.status = 'PUBLISHED'
ORDER BY p.view_count DESC
LIMIT 10;
```

### Step 4: 애플리케이션 실행

```java
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

**실행 로그:**
```
INFO  o.f.c.i.d.DatabaseFactory - Database: jdbc:mysql://localhost:3306/mydb
INFO  o.f.c.i.s.JdbcTableSchemaHistory - Creating Schema History table: `mydb`.`flyway_schema_history`
INFO  o.f.c.i.c.DbMigrate - Current version of schema `mydb`: << Empty Schema >>
INFO  o.f.c.i.c.DbMigrate - Migrating schema `mydb` to version "1 - create users table"
INFO  o.f.c.i.c.DbMigrate - Migrating schema `mydb` to version "2 - create posts table"
INFO  o.f.c.i.c.DbMigrate - Migrating schema `mydb` to version "3 - add phone to users"
INFO  o.f.c.i.c.DbMigrate - Successfully applied 3 migrations to schema `mydb`
```

### Step 5: 상태 확인

```sql
-- flyway_schema_history 테이블 확인
SELECT * FROM flyway_schema_history ORDER BY installed_rank;
```

**결과:**
| installed_rank | version | description | type | script | checksum | execution_time | success |
|----------------|---------|-------------|------|--------|----------|----------------|---------|
| 1 | 1 | create users table | SQL | V1__create_users_table.sql | -123456789 | 45 | 1 |
| 2 | 2 | create posts table | SQL | V2__create_posts_table.sql | 987654321 | 32 | 1 |
| 3 | 3 | add phone to users | SQL | V3__add_phone_to_users.sql | 456789123 | 18 | 1 |

---

## 💡 Liquibase 핵심 개념

### 1️⃣ 초급: Liquibase란?

**Liquibase = 더 강력하고 유연한 마이그레이션 도구**

```
Flyway: SQL 파일 중심, 간단명료
Liquibase: XML/YAML/JSON 지원, 다양한 기능
```

#### 주요 특징

1. **다양한 형식 지원**
   - XML, YAML, JSON, SQL
   - 데이터베이스 독립적 표현 가능

2. **강력한 Rollback**
   - 자동 Rollback 생성
   - 특정 버전으로 되돌리기

3. **Context & Label**
   - 환경별 실행 제어 (dev, staging, prod)
   - 특정 변경만 선택 실행

4. **Preconditions**
   - 실행 전 조건 검사
   - 안전성 향상

### 2️⃣ 중급: Liquibase 파일 형식

#### XML 형식

```xml
<!-- db/changelog/db.changelog-master.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <changeSet id="1" author="john">
        <createTable tableName="users">
            <column name="id" type="BIGINT" autoIncrement="true">
                <constraints primaryKey="true" nullable="false"/>
            </column>
            <column name="username" type="VARCHAR(50)">
                <constraints nullable="false" unique="true"/>
            </column>
            <column name="email" type="VARCHAR(255)"/>
            <column name="created_at" type="TIMESTAMP" defaultValueComputed="CURRENT_TIMESTAMP"/>
        </createTable>
    </changeSet>

    <changeSet id="2" author="jane">
        <addColumn tableName="users">
            <column name="phone" type="VARCHAR(20)"/>
        </addColumn>
    </changeSet>

</databaseChangeLog>
```

#### YAML 형식 (더 간결)

```yaml
# db/changelog/db.changelog-master.yaml
databaseChangeLog:
  - changeSet:
      id: 1
      author: john
      changes:
        - createTable:
            tableName: users
            columns:
              - column:
                  name: id
                  type: BIGINT
                  autoIncrement: true
                  constraints:
                    primaryKey: true
                    nullable: false
              - column:
                  name: username
                  type: VARCHAR(50)
                  constraints:
                    nullable: false
                    unique: true
              - column:
                  name: email
                  type: VARCHAR(255)
              - column:
                  name: created_at
                  type: TIMESTAMP
                  defaultValueComputed: CURRENT_TIMESTAMP

  - changeSet:
      id: 2
      author: jane
      changes:
        - addColumn:
            tableName: users
            columns:
              - column:
                  name: phone
                  type: VARCHAR(20)
```

#### SQL 형식

```sql
-- db/changelog/changes/v0001_create_users_table.sql
--liquibase formatted sql

--changeset john:1
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
--rollback DROP TABLE users;

--changeset jane:2
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
--rollback ALTER TABLE users DROP COLUMN phone;
```

### 3️⃣ 고급: Liquibase 고급 기능

#### 1. Context (환경별 실행)

```yaml
databaseChangeLog:
  - changeSet:
      id: 1
      author: john
      context: dev  # 개발 환경에서만 실행
      changes:
        - insert:
            tableName: users
            columns:
              - column:
                  name: username
                  value: test_user
              - column:
                  name: email
                  value: test@example.com

  - changeSet:
      id: 2
      author: jane
      context: prod  # 운영 환경에서만 실행
      changes:
        - createIndex:
            indexName: idx_users_email
            tableName: users
            columns:
              - column:
                  name: email
```

#### 2. Preconditions (실행 전 조건)

```yaml
databaseChangeLog:
  - changeSet:
      id: 3
      author: john
      preConditions:
        - onFail: MARK_RAN  # 실패 시 실행한 것으로 표시
        - not:
            - columnExists:
                tableName: users
                columnName: phone
      changes:
        - addColumn:
            tableName: users
            columns:
              - column:
                  name: phone
                  type: VARCHAR(20)
```

#### 3. Rollback

```yaml
databaseChangeLog:
  - changeSet:
      id: 4
      author: jane
      changes:
        - addColumn:
            tableName: users
            columns:
              - column:
                  name: age
                  type: INT
      rollback:
        - dropColumn:
            tableName: users
            columnName: age
```

---

## 🛠️ 기본 실습 2: Liquibase 설정

### Step 1: 의존성 추가

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.liquibase:liquibase-core'
    runtimeOnly 'com.mysql.cj:mysql-connector-j'
}
```

### Step 2: application.yml 설정

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb
    username: root
    password: password

  jpa:
    hibernate:
      ddl-auto: validate

  liquibase:
    enabled: true
    change-log: classpath:db/changelog/db.changelog-master.yaml
    contexts: dev  # 환경: dev, staging, prod
    drop-first: false  # 주의! true 시 모든 객체 삭제
    default-schema: mydb
```

### Step 3: Master Changelog 작성

**db/changelog/db.changelog-master.yaml:**
```yaml
databaseChangeLog:
  - include:
      file: db/changelog/changes/v0001-create-users-table.yaml
  - include:
      file: db/changelog/changes/v0002-create-posts-table.yaml
  - include:
      file: db/changelog/changes/v0003-add-indexes.yaml
```

### Step 4: 개별 Changelog 작성

**db/changelog/changes/v0001-create-users-table.yaml:**
```yaml
databaseChangeLog:
  - changeSet:
      id: v0001-1
      author: john
      changes:
        - createTable:
            tableName: users
            columns:
              - column:
                  name: id
                  type: BIGINT
                  autoIncrement: true
                  constraints:
                    primaryKey: true
              - column:
                  name: username
                  type: VARCHAR(50)
                  constraints:
                    nullable: false
                    unique: true
              - column:
                  name: email
                  type: VARCHAR(255)
              - column:
                  name: status
                  type: VARCHAR(20)
                  defaultValue: ACTIVE
              - column:
                  name: created_at
                  type: TIMESTAMP
                  defaultValueComputed: CURRENT_TIMESTAMP
      rollback:
        - dropTable:
            tableName: users
```

**db/changelog/changes/v0002-create-posts-table.yaml:**
```yaml
databaseChangeLog:
  - changeSet:
      id: v0002-1
      author: jane
      changes:
        - createTable:
            tableName: posts
            columns:
              - column:
                  name: id
                  type: BIGINT
                  autoIncrement: true
                  constraints:
                    primaryKey: true
              - column:
                  name: user_id
                  type: BIGINT
                  constraints:
                    nullable: false
              - column:
                  name: title
                  type: VARCHAR(200)
                  constraints:
                    nullable: false
              - column:
                  name: content
                  type: TEXT
              - column:
                  name: view_count
                  type: INT
                  defaultValue: 0
              - column:
                  name: created_at
                  type: TIMESTAMP
                  defaultValueComputed: CURRENT_TIMESTAMP

        - addForeignKeyConstraint:
            baseTableName: posts
            baseColumnNames: user_id
            referencedTableName: users
            referencedColumnNames: id
            constraintName: fk_posts_user
            onDelete: CASCADE
```

**db/changelog/changes/v0003-add-indexes.yaml:**
```yaml
databaseChangeLog:
  - changeSet:
      id: v0003-1
      author: john
      changes:
        - createIndex:
            indexName: idx_users_email
            tableName: users
            columns:
              - column:
                  name: email

        - createIndex:
            indexName: idx_users_status
            tableName: users
            columns:
              - column:
                  name: status

        - createIndex:
            indexName: idx_posts_user_id
            tableName: posts
            columns:
              - column:
                  name: user_id

        - createIndex:
            indexName: idx_posts_created_at
            tableName: posts
            columns:
              - column:
                  name: created_at
```

### Step 5: 테스트 데이터 (개발 환경만)

**db/changelog/changes/v0004-test-data.yaml:**
```yaml
databaseChangeLog:
  - changeSet:
      id: v0004-1
      author: john
      context: dev  # 개발 환경에서만 실행
      changes:
        - insert:
            tableName: users
            columns:
              - column:
                  name: username
                  value: testuser1
              - column:
                  name: email
                  value: test1@example.com
              - column:
                  name: status
                  value: ACTIVE

        - insert:
            tableName: users
            columns:
              - column:
                  name: username
                  value: testuser2
              - column:
                  name: email
                  value: test2@example.com
              - column:
                  name: status
                  value: ACTIVE

        - insert:
            tableName: posts
            columns:
              - column:
                  name: user_id
                  valueNumeric: 1
              - column:
                  name: title
                  value: First Post
              - column:
                  name: content
                  value: This is test content
```

---

## 👨‍💻 주니어 개발자 실전 시나리오

### 시나리오: "운영 중인 서비스에 새 기능 추가"

**상황:**
- 운영 중인 블로그 서비스에 "댓글 기능" 추가
- 기존 사용자 데이터 유지 필수
- 다운타임 최소화

#### Step 1: 새 마이그레이션 작성

**V4__create_comments_table.sql (Flyway):**
```sql
-- 댓글 테이블 생성
CREATE TABLE comments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'PUBLISHED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_comments_post FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    CONSTRAINT fk_comments_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 인덱스
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_comments_status ON comments(status);
CREATE INDEX idx_comments_created_at ON comments(created_at);
```

**V5__add_comment_count_to_posts.sql:**
```sql
-- 게시글에 댓글 수 컬럼 추가
ALTER TABLE posts
ADD COLUMN comment_count INT DEFAULT 0 AFTER view_count;

-- 기존 데이터의 댓글 수 계산 (초기값 설정)
UPDATE posts p
SET comment_count = (
    SELECT COUNT(*)
    FROM comments c
    WHERE c.post_id = p.id AND c.status = 'PUBLISHED'
);

-- 인덱스
CREATE INDEX idx_posts_comment_count ON posts(comment_count);
```

#### Step 2: 배포 전 검증

**로컬 환경에서 테스트:**
```bash
# 1. 로컬 DB에 적용
./gradlew bootRun

# 2. 마이그레이션 확인
mysql> SELECT * FROM flyway_schema_history ORDER BY installed_rank;

# 3. 테이블 생성 확인
mysql> SHOW TABLES;
mysql> DESC comments;
```

#### Step 3: 스테이징 환경 배포

**application-staging.yml:**
```yaml
spring:
  datasource:
    url: jdbc:mysql://staging-db:3306/mydb
  flyway:
    enabled: true
    validate-on-migrate: true
    baseline-on-migrate: false  # 스테이징은 이미 Flyway 사용 중
```

```bash
# 스테이징 배포
./gradlew bootJar
java -jar build/libs/app.jar --spring.profiles.active=staging

# 로그 확인
INFO  o.f.c.i.c.DbMigrate - Migrating schema to version "4 - create comments table"
INFO  o.f.c.i.c.DbMigrate - Migrating schema to version "5 - add comment count to posts"
INFO  o.f.c.i.c.DbMigrate - Successfully applied 2 migrations
```

#### Step 4: 운영 환경 배포

**주의사항 체크리스트:**
- [ ] 백업 완료 확인
- [ ] 마이그레이션 실행 시간 예측 (대용량 테이블 ALTER 주의)
- [ ] Rollback 계획 수립
- [ ] 모니터링 준비

**application-prod.yml:**
```yaml
spring:
  flyway:
    enabled: true
    validate-on-migrate: true
    out-of-order: false
    # baseline-on-migrate: false  # 운영은 엄격하게
```

**배포 순서:**
```bash
# 1. 데이터베이스 백업
mysqldump -u root -p mydb > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. 애플리케이션 배포
./deploy-prod.sh

# 3. 마이그레이션 확인
mysql> SELECT * FROM flyway_schema_history WHERE success = 0;  # 실패한 것 확인
mysql> SELECT COUNT(*) FROM comments;  # 테이블 생성 확인

# 4. 애플리케이션 동작 확인
curl http://prod-server/api/health

# 5. 모니터링 대시보드 확인
```

---

## 🏢 기업 사례: Netflix

### 배경

Netflix는 수천 개의 마이크로서비스와 수백 개의 데이터베이스를 운영합니다.

**도전 과제:**
- 다양한 팀이 독립적으로 스키마 변경
- 무중단 배포 필수
- 롤백 가능해야 함

### Flyway 도입 전략

1. **Blue-Green Deployment와 결합**
   ```
   Blue (현재 운영) - Schema V10
   Green (새 버전) - Schema V11 적용

   → 트래픽을 Green으로 전환
   → 문제 발생 시 Blue로 즉시 복귀
   ```

2. **Backward Compatible 마이그레이션**
   ```sql
   -- ❌ Bad - 기존 앱이 동작 안 함
   ALTER TABLE users DROP COLUMN old_email;

   -- ✅ Good - 3단계 전략
   -- Step 1: 새 컬럼 추가 (앱은 두 컬럼 모두 쓰기)
   ALTER TABLE users ADD COLUMN email VARCHAR(255);

   -- Step 2: 데이터 마이그레이션 (배치 작업)
   UPDATE users SET email = old_email WHERE email IS NULL;

   -- Step 3: 구 컬럼 삭제 (다음 버전에서)
   ALTER TABLE users DROP COLUMN old_email;
   ```

3. **자동화된 검증**
   ```java
   @SpringBootTest
   class FlywayIntegrationTest {
       @Autowired
       private Flyway flyway;

       @Test
       void 마이그레이션_검증() {
           // 현재 버전 확인
           assertThat(flyway.info().current().getVersion()).isNotNull();

           // 미적용 마이그레이션 없음
           assertThat(flyway.info().pending()).isEmpty();
       }
   }
   ```

**결과:**
- 하루 수천 건의 배포 가능
- 데이터베이스 관련 장애 90% 감소
- 롤백 시간 10분 → 30초로 단축

---

## ❓ FAQ

### Q1. Flyway와 Liquibase 중 어떤 것을 선택해야 하나요?

**A:** 프로젝트 특성에 따라 선택

| 상황 | 추천 | 이유 |
|-----|------|------|
| 간단한 프로젝트, SQL 선호 | Flyway | 학습 곡선 낮음, 설정 간단 |
| 복잡한 프로젝트, 멀티 DB | Liquibase | DB 독립적, 강력한 기능 |
| 팀이 SQL에 익숙함 | Flyway | SQL 파일로 직관적 |
| 자동 Rollback 필요 | Liquibase | Rollback 자동 생성 |
| 환경별 다른 스크립트 | Liquibase | Context 기능 |

**Netflix, Airbnb**: Flyway
**LinkedIn, Uber**: Liquibase

### Q2. 운영 DB에 Flyway를 처음 도입하려면?

**A:** Baseline 전략 사용

```yaml
# application.yml
spring:
  flyway:
    enabled: true
    baseline-on-migrate: true  # 기존 DB 인식
    baseline-version: 0        # 현재 버전을 0으로 설정
```

```sql
-- V1__baseline.sql 은 만들지 않음
-- V2__add_new_feature.sql 부터 시작
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
```

**단계:**
1. 현재 스키마 export
2. `baseline-on-migrate: true` 설정
3. 애플리케이션 시작 → flyway_schema_history 생성
4. 이후 변경부터 V1, V2, ... 로 관리

### Q3. 마이그레이션이 실패하면 어떻게 하나요?

**A:** 상황별 대응

**1. 개발 환경:**
```bash
# Clean & Migrate (데이터 삭제 주의!)
flyway clean
flyway migrate
```

**2. 운영 환경:**
```bash
# 1. 실패 원인 확인
SELECT * FROM flyway_schema_history WHERE success = 0;

# 2. 수동으로 문제 해결 후 repair
flyway repair  # 실패 기록 제거

# 3. 다시 실행
flyway migrate
```

**3. 복구 불가능한 경우:**
```bash
# 백업에서 복원
mysql -u root -p mydb < backup_20250115.sql

# 애플리케이션 이전 버전으로 롤백
```

### Q4. 대용량 테이블의 ALTER는 어떻게 처리하나요?

**A:** Online DDL 또는 점진적 마이그레이션

**방법 1: MySQL 5.6+ Online DDL**
```sql
-- V10__add_index_online.sql
ALTER TABLE users ADD INDEX idx_email (email), ALGORITHM=INPLACE, LOCK=NONE;
-- 읽기/쓰기 계속 가능, 백그라운드에서 인덱스 생성
```

**방법 2: pt-online-schema-change (Percona Toolkit)**
```bash
# Flyway 마이그레이션에서 실행
pt-online-schema-change \
  --alter "ADD COLUMN phone VARCHAR(20)" \
  D=mydb,t=users \
  --execute
```

**방법 3: 점진적 마이그레이션 (3단계)**
```sql
-- V10__add_phone_column.sql
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- V11__migrate_phone_data.sql (배치 작업)
-- 애플리케이션 코드로 천천히 마이그레이션

-- V12__add_phone_constraint.sql
ALTER TABLE users MODIFY phone VARCHAR(20) NOT NULL;
```

### Q5. Git 브랜치별로 마이그레이션이 충돌하면?

**A:** 버전 번호 전략

**문제 상황:**
```
feature-A: V10__add_phone.sql
feature-B: V10__add_address.sql  ← 충돌!
```

**해결책 1: Timestamp 사용**
```
V20250115_1430__add_phone.sql
V20250115_1445__add_address.sql
```

**해결책 2: 브랜치별 범위 할당**
```
main: V1~V999
feature-A: V1000~V1099
feature-B: V1100~V1199
```

**Flyway 설정:**
```yaml
spring:
  flyway:
    out-of-order: true  # 순서 상관없이 실행
```

---

## 💼 면접 질문 TOP 5

### ⭐ 초급 1: 데이터베이스 마이그레이션이란?

**답변:**
데이터베이스 스키마 변경을 버전 관리하는 것입니다. Git으로 코드를 관리하듯, Flyway/Liquibase로 DB 스키마를 관리합니다.

**장점:**
- 모든 환경에서 동일한 스키마 보장
- 변경 이력 추적 가능
- 자동화로 휴먼 에러 방지

### ⭐ 초급 2: Flyway 마이그레이션 파일 명명 규칙은?

**답변:**
```
V{버전}__{설명}.sql

예시:
V1__create_users_table.sql
V2__add_email_column.sql
V2.1__add_phone_column.sql
```

**규칙:**
- `V`: Version (필수)
- 숫자 버전 (점, 언더스코어 가능)
- `__`: 구분자 (언더스코어 2개)
- 설명 (snake_case 권장)

### ⭐⭐ 중급 1: Flyway와 Liquibase의 차이는?

**답변:**

| 구분 | Flyway | Liquibase |
|-----|--------|-----------|
| 형식 | SQL 중심 | XML/YAML/JSON/SQL |
| 간단함 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 기능 | 기본 기능 | 고급 기능 다수 |
| Rollback | Pro 버전만 | 무료 |
| DB 독립성 | SQL은 DB 의존적 | XML은 DB 독립적 |
| 사용 사례 | 간단한 프로젝트 | 복잡한 엔터프라이즈 |

### ⭐⭐ 중급 2: 운영 환경에서 마이그레이션 실패 시 대응은?

**답변:**

**1. 즉시 대응:**
```bash
# 실패 원인 확인
SELECT * FROM flyway_schema_history WHERE success = 0;

# 문제 수정 후 repair
flyway repair
flyway migrate
```

**2. 롤백 필요 시:**
```bash
# 백업 복원
mysql -u root -p mydb < backup.sql

# 애플리케이션 이전 버전 배포
```

**3. 예방 전략:**
- 백업 필수
- 스테이징 환경에서 충분한 테스트
- Backward Compatible 마이그레이션
- 모니터링 및 알림 설정

### ⭐⭐ 중급 3: JPA ddl-auto와 Flyway를 같이 쓸 때 설정은?

**답변:**

```yaml
spring:
  jpa:
    hibernate:
      ddl-auto: validate  # 또는 none (필수!)
      # create, update는 절대 금지

  flyway:
    enabled: true
```

**이유:**
- `ddl-auto: create/update`는 스키마를 자동 변경
- Flyway와 충돌하여 예측 불가능한 결과 발생
- **운영 환경**: `validate` 또는 `none` 필수
- **개발 환경**: 초기에만 `create`, 이후 `validate`

**검증 동작:**
```
애플리케이션 시작 시:
1. Flyway가 마이그레이션 실행
2. Hibernate가 Entity와 스키마 비교 (validate)
3. 불일치 발견 시 애플리케이션 시작 실패
```

---

## 🎯 다음 단계

DB 스키마 관리를 마쳤다면:

1. **27장: QueryDSL** - 타입 안전한 동적 쿼리
2. **28장: MyBatis 연동** - 복잡한 SQL 처리
3. **CI/CD 파이프라인 통합** - 자동화된 마이그레이션
4. **Blue-Green Deployment** - 무중단 배포 전략
5. **Database Versioning 전략** - 팀 협업 규칙 수립

---

## 📚 참고 자료

- **Flyway 문서**: https://flywaydb.org/documentation/
- **Liquibase 문서**: https://docs.liquibase.com/
- **Spring Boot + Flyway**: https://docs.spring.io/spring-boot/docs/current/reference/html/howto.html#howto.data-initialization.migration-tool.flyway

---

**🎓 학습 완료 체크리스트:**

- [ ] Flyway 개념과 동작 원리 이해
- [ ] 마이그레이션 파일 작성 및 명명 규칙
- [ ] Liquibase 다양한 형식 활용
- [ ] 운영 환경 안전 배포 전략
- [ ] Rollback 및 복구 절차 이해
- [ ] JPA ddl-auto와 마이그레이션 도구 병용 설정

**다음 장에서는 QueryDSL로 타입 안전한 동적 쿼리를 작성하는 방법을 배웁니다!** 🚀
