# 29장: Spring Boot 소개 - 설정 지옥에서 탈출하기

> **"복잡한 설정은 이제 그만, 코드 작성에 집중하세요"**

---

## 📋 학습 목표

이 장을 학습하면 다음을 할 수 있습니다:

- Spring Boot의 등장 배경과 핵심 가치를 이해합니다
- Spring과 Spring Boot의 차이를 명확히 설명할 수 있습니다
- Spring Boot의 핵심 기능(자동 설정, 스타터)을 활용합니다
- 첫 Spring Boot 애플리케이션을 5분 만에 생성하고 실행합니다
- 내장 서버의 장점과 운영 전략을 이해합니다

**예상 학습 시간**: 2-3시간
**난이도**: ⭐⭐ (초중급)

---

## 🤔 왜 Spring Boot가 필요한가?

### 문제 상황: 전통적인 Spring의 복잡함

#### 문제 1: 설정 지옥 (Configuration Hell)

**전통 Spring - 200줄 이상의 XML 설정:**

```xml
<!-- web.xml - 서블릿 설정 -->
<web-app>
    <servlet>
        <servlet-name>dispatcher</servlet-name>
        <servlet-class>org.springframework.web.servlet.DispatcherServlet</servlet-class>
        <init-param>
            <param-name>contextConfigLocation</param-name>
            <param-value>/WEB-INF/spring/appServlet/servlet-context.xml</param-value>
        </init-param>
        <load-on-startup>1</load-on-startup>
    </servlet>
    <!-- 50줄 더... -->
</web-app>

<!-- applicationContext.xml - Bean 설정 -->
<beans xmlns="http://www.springframework.org/schema/beans"...>
    <context:component-scan base-package="com.example"/>
    <mvc:annotation-driven/>

    <!-- DataSource 설정 -->
    <bean id="dataSource" class="org.apache.commons.dbcp2.BasicDataSource">
        <property name="driverClassName" value="com.mysql.cj.jdbc.Driver"/>
        <property name="url" value="jdbc:mysql://localhost:3306/mydb"/>
        <property name="username" value="root"/>
        <property name="password" value="password"/>
    </bean>

    <!-- EntityManagerFactory 설정 -->
    <bean id="entityManagerFactory"
          class="org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean">
        <property name="dataSource" ref="dataSource"/>
        <property name="packagesToScan" value="com.example.entity"/>
        <!-- 30줄 더... -->
    </bean>

    <!-- 100줄 더... -->
</beans>
```

**개발자의 고통:**
- "첫 프로젝트 설정에 3일 걸렸어요"
- "라이브러리 버전 충돌로 하루 날렸어요"
- "XML 오타로 찾는데 2시간..."

#### 문제 2: 의존성 관리의 악몽

```xml
<!-- pom.xml - 각 라이브러리 버전 일일이 관리 -->
<dependencies>
    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-webmvc</artifactId>
        <version>5.3.20</version>
    </dependency>
    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-jdbc</artifactId>
        <version>5.3.20</version>  <!-- 버전 불일치 위험 -->
    </dependency>
    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-orm</artifactId>
        <version>5.3.15</version>  <!-- 다른 버전! 충돌 발생 -->
    </dependency>
    <!-- 50개 이상의 의존성... -->
</dependencies>
```

#### 문제 3: 서버 설정 및 배포

```
1. Tomcat 다운로드
2. 설치 및 환경 변수 설정
3. WAR 파일 빌드
4. Tomcat에 수동 배포
5. 서버 시작 및 로그 확인
→ 로컬 개발 환경과 운영 환경 차이로 문제 발생
```

### Spring Boot의 해결책

```java
// Spring Boot - 단 하나의 클래스
@SpringBootApplication
public class MyApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}

// application.yml - 간단한 설정
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb
    username: root
    password: password
  jpa:
    hibernate:
      ddl-auto: update

// 실행: java -jar myapp.jar
// 끝!
```

**Spring Boot의 혁명:**
- 설정 200줄 → 10줄
- 프로젝트 시작 3일 → 5분
- WAR 배포 → JAR 실행
- XML 지옥 → Java/YAML 간결함

---

## 🌍 실생활 비유로 이해하는 Spring Boot

### 비유 1: 조립식 가구 vs 완제품 가구

**전통 Spring (조립식 가구):**
```
1. IKEA 가구 구매
2. 설명서 100페이지 읽기
3. 나사 찾기, 공구 준비
4. 3시간 조립
5. 나사 하나 남음 (뭔가 잘못됨)
→ 가구는 만들어지지만 시간 낭비
```

**Spring Boot (완제품 가구):**
```
1. 완성된 가구 배송
2. 포장 뜯기
3. 원하는 위치에 배치
4. 바로 사용
→ 5분 안에 사용 가능
```

**코드로 표현:**
```java
// Spring - 100줄 설정
public class SpringConfig {
    @Bean public DataSource dataSource() { /* 20줄 */ }
    @Bean public EntityManagerFactory emf() { /* 30줄 */ }
    @Bean public TransactionManager tm() { /* 15줄 */ }
    // 10개 이상의 Bean 설정...
}

// Spring Boot - 자동 설정
// 의존성만 추가하면 끝!
// implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
```

### 비유 2: 수동 vs 자동 세팅 (스마트폰)

**전통 Spring (수동 세팅):**
```
새 폰 구매 → 일일이 설정
- Wi-Fi 연결
- 앱 하나씩 다운로드
- 알림 설정
- 화면 밝기 조절
- 백업 설정
→ 2시간 소요
```

**Spring Boot (자동 세팅):**
```
새 폰 구매 → "이전 폰에서 복원"
- 모든 설정 자동 적용
- 앱 자동 설치
- 환경 그대로 재현
→ 5분 완료
```

### 비유 3: 요리 재료 vs 밀키트

**전통 Spring (재료 직접 구매):**
```
김치찌개 만들기
1. 마트에서 재료 구매
   - 김치, 돼지고기, 두부, 파, 마늘...
2. 각 재료 손질
3. 양념 비율 맞추기
4. 조리 시작
→ 준비만 1시간
```

**Spring Boot (밀키트):**
```
김치찌개 밀키트
1. 박스 오픈
2. 손질된 재료 확인
3. 레시피대로 조리
→ 준비 5분, 조리만 집중
```

**코드 비교:**
```java
// Spring - 재료 하나씩 설정
@Bean
public DataSource dataSource() {
    BasicDataSource ds = new BasicDataSource();
    ds.setDriverClassName("com.mysql.cj.jdbc.Driver");
    ds.setUrl("jdbc:mysql://localhost:3306/mydb");
    ds.setUsername("root");
    ds.setPassword("password");
    ds.setInitialSize(5);
    ds.setMaxTotal(20);
    // 10개 이상의 설정...
    return ds;
}

// Spring Boot - 밀키트 (자동 설정)
spring.datasource.url=jdbc:mysql://localhost:3306/mydb
spring.datasource.username=root
spring.datasource.password=password
// 끝! 나머지는 자동
```

---

## 💡 Spring Boot 핵심 개념

### 1️⃣ 초급: Spring Boot의 4대 핵심 기능

#### 1. Auto Configuration (자동 설정)

**동작 원리:**
```
1. 클래스패스에 있는 라이브러리 감지
2. 적절한 기본 설정 자동 적용
3. 필요 시 커스터마이징 가능
```

**예시:**
```java
// 1. JPA 의존성 추가
implementation 'org.springframework.boot:spring-boot-starter-data-jpa'

// 2. Spring Boot가 자동으로 설정하는 것들:
// - DataSource
// - EntityManagerFactory
// - TransactionManager
// - JpaRepositories

// 3. 개발자는 Entity만 작성
@Entity
public class User {
    @Id @GeneratedValue
    private Long id;
    private String name;
}

// 4. Repository 인터페이스만 정의
public interface UserRepository extends JpaRepository<User, Long> {
}

// 끝! 모든 설정 완료
```

#### 2. Starter Dependencies (스타터 의존성)

**개념:**
```
관련 라이브러리를 묶어서 제공
→ 하나만 추가하면 필요한 모든 것이 포함
```

**주요 스타터:**

| 스타터 | 포함 내용 | 용도 |
|-------|---------|------|
| `spring-boot-starter-web` | Spring MVC, Tomcat, Jackson | REST API 개발 |
| `spring-boot-starter-data-jpa` | Hibernate, JPA, JDBC | 데이터베이스 연동 |
| `spring-boot-starter-security` | Spring Security | 보안 |
| `spring-boot-starter-test` | JUnit, Mockito, AssertJ | 테스트 |
| `spring-boot-starter-validation` | Hibernate Validator | 검증 |

**전통 방식 vs Spring Boot:**

```gradle
// ❌ 전통 방식 - 20개 이상 직접 관리
dependencies {
    implementation 'org.springframework:spring-webmvc:5.3.20'
    implementation 'org.springframework:spring-web:5.3.20'
    implementation 'com.fasterxml.jackson.core:jackson-databind:2.13.3'
    implementation 'org.apache.tomcat.embed:tomcat-embed-core:9.0.65'
    implementation 'org.apache.tomcat.embed:tomcat-embed-websocket:9.0.65'
    // 15개 더...
}

// ✅ Spring Boot - 단 하나로 해결
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
}
```

#### 3. Embedded Server (내장 서버)

**개념:**
```
애플리케이션 내부에 서버 포함
→ 별도 Tomcat 설치 불필요
```

**장점:**

```
1. 간편한 실행
   java -jar myapp.jar

2. 환경 일관성
   개발 = 스테이징 = 운영

3. 클라우드 친화적
   Docker 컨테이너화 쉬움

4. 버전 관리
   Tomcat 버전도 의존성으로 관리
```

**실행 비교:**

```bash
# ❌ 전통 방식
1. Tomcat 다운로드
2. 압축 해제: /opt/tomcat
3. 환경 변수 설정: CATALINA_HOME
4. WAR 빌드: mvn package
5. 배포: cp target/app.war /opt/tomcat/webapps/
6. 실행: /opt/tomcat/bin/startup.sh

# ✅ Spring Boot
java -jar app.jar
```

#### 4. Production-Ready Features (운영 기능)

**Actuator로 제공:**
- 헬스 체크: `/actuator/health`
- 메트릭: `/actuator/metrics`
- 환경 정보: `/actuator/env`
- 로그 레벨 변경: `/actuator/loggers`

```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      show-details: always
```

```bash
# 애플리케이션 상태 확인
curl http://localhost:8080/actuator/health

# 결과
{
  "status": "UP",
  "components": {
    "db": { "status": "UP" },
    "diskSpace": { "status": "UP" }
  }
}
```

### 2️⃣ 중급: Spring vs Spring Boot 상세 비교

#### 설정 복잡도 비교

**Web MVC 설정 예시:**

```java
// ❌ Spring - 50줄 이상
@Configuration
@EnableWebMvc
@ComponentScan(basePackages = "com.example")
public class WebConfig implements WebMvcConfigurer {

    @Bean
    public ViewResolver viewResolver() {
        InternalResourceViewResolver resolver = new InternalResourceViewResolver();
        resolver.setPrefix("/WEB-INF/views/");
        resolver.setSuffix(".jsp");
        return resolver;
    }

    @Bean
    public MultipartResolver multipartResolver() {
        CommonsMultipartResolver resolver = new CommonsMultipartResolver();
        resolver.setMaxUploadSize(5242880);
        return resolver;
    }

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/resources/**")
                .addResourceLocations("/resources/");
    }

    @Override
    public void configureDefaultServletHandling(DefaultServletHandlerConfigurer configurer) {
        configurer.enable();
    }

    // 20줄 더...
}

// ✅ Spring Boot - 자동 설정
@SpringBootApplication
public class MyApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}
```

#### 데이터베이스 설정 비교

```java
// ❌ Spring - 80줄
@Configuration
@EnableTransactionManagement
@EnableJpaRepositories(basePackages = "com.example.repository")
public class JpaConfig {

    @Bean
    public DataSource dataSource() {
        BasicDataSource dataSource = new BasicDataSource();
        dataSource.setDriverClassName("com.mysql.cj.jdbc.Driver");
        dataSource.setUrl("jdbc:mysql://localhost:3306/mydb");
        dataSource.setUsername("root");
        dataSource.setPassword("password");
        dataSource.setInitialSize(5);
        dataSource.setMaxTotal(20);
        dataSource.setMaxIdle(10);
        dataSource.setMinIdle(5);
        return dataSource;
    }

    @Bean
    public LocalContainerEntityManagerFactoryBean entityManagerFactory() {
        LocalContainerEntityManagerFactoryBean em = new LocalContainerEntityManagerFactoryBean();
        em.setDataSource(dataSource());
        em.setPackagesToScan("com.example.entity");

        JpaVendorAdapter vendorAdapter = new HibernateJpaVendorAdapter();
        em.setJpaVendorAdapter(vendorAdapter);
        em.setJpaProperties(additionalProperties());

        return em;
    }

    private Properties additionalProperties() {
        Properties properties = new Properties();
        properties.setProperty("hibernate.hbm2ddl.auto", "update");
        properties.setProperty("hibernate.dialect", "org.hibernate.dialect.MySQL8Dialect");
        properties.setProperty("hibernate.show_sql", "true");
        properties.setProperty("hibernate.format_sql", "true");
        return properties;
    }

    @Bean
    public PlatformTransactionManager transactionManager() {
        JpaTransactionManager transactionManager = new JpaTransactionManager();
        transactionManager.setEntityManagerFactory(entityManagerFactory().getObject());
        return transactionManager;
    }
}

// ✅ Spring Boot - 5줄
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb
    username: root
    password: password
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
```

### 3️⃣ 고급: Spring Boot 내부 동작 원리

#### @SpringBootApplication 분석

```java
@SpringBootApplication
// ↓ 실제로는 3개 애노테이션의 조합
@SpringBootConfiguration  // = @Configuration
@EnableAutoConfiguration  // 자동 설정 활성화
@ComponentScan            // 컴포넌트 스캔
public class MyApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}
```

#### 자동 설정 동작 원리

```
1. @EnableAutoConfiguration 처리
   ↓
2. spring.factories 파일 읽기
   (spring-boot-autoconfigure.jar 내부)
   ↓
3. 조건부 설정 클래스 로드
   @ConditionalOnClass(DataSource.class)
   @ConditionalOnMissingBean(DataSource.class)
   ↓
4. 조건 만족 시 Bean 자동 생성
```

**예시: DataSource 자동 설정**

```java
// Spring Boot 내부 코드 (단순화)
@Configuration
@ConditionalOnClass({ DataSource.class, EmbeddedDatabaseType.class })
@ConditionalOnMissingBean(DataSource.class)
@EnableConfigurationProperties(DataSourceProperties.class)
public class DataSourceAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public DataSource dataSource(DataSourceProperties properties) {
        return properties.initializeDataSourceBuilder().build();
    }
}
```

**조건부 애노테이션:**

| 애노테이션 | 설명 |
|----------|------|
| `@ConditionalOnClass` | 클래스패스에 해당 클래스가 있을 때 |
| `@ConditionalOnMissingBean` | 해당 타입의 Bean이 없을 때 |
| `@ConditionalOnProperty` | 프로퍼티가 특정 값일 때 |
| `@ConditionalOnWebApplication` | 웹 애플리케이션일 때 |

---

## 🛠️ 기본 실습

### 실습 1: 첫 Spring Boot 애플리케이션 (5분 완성)

#### Step 1: 프로젝트 생성

**방법 1: Spring Initializr (https://start.spring.io)**
```
Project: Gradle
Language: Java
Spring Boot: 3.2.0
Group: com.example
Artifact: demo
Dependencies: Spring Web
```

**방법 2: IntelliJ IDEA**
```
New Project → Spring Initializr → 설정 입력
```

#### Step 2: 생성된 구조 확인

```
demo/
├── src/
│   ├── main/
│   │   ├── java/com/example/demo/
│   │   │   └── DemoApplication.java
│   │   └── resources/
│   │       └── application.properties
│   └── test/
├── build.gradle
└── gradlew
```

#### Step 3: Controller 작성

```java
package com.example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/")
    public String hello() {
        return "Hello, Spring Boot!";
    }

    @GetMapping("/api/users")
    public User getUser() {
        return new User(1L, "홍길동", "hong@example.com");
    }
}

record User(Long id, String name, String email) {}
```

#### Step 4: 실행

```bash
# Gradle
./gradlew bootRun

# 또는 직접 실행
./gradlew build
java -jar build/libs/demo-0.0.1-SNAPSHOT.jar
```

**결과:**
```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v3.2.0)

... Tomcat started on port(s): 8080 ...
```

#### Step 5: 테스트

```bash
# 브라우저 또는 curl
curl http://localhost:8080/
# 결과: Hello, Spring Boot!

curl http://localhost:8080/api/users
# 결과: {"id":1,"name":"홍길동","email":"hong@example.com"}
```

---

### 실습 2: 데이터베이스 연동 (10분 완성)

#### Step 1: 의존성 추가

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    runtimeOnly 'com.h2database:h2'  // 메모리 DB
}
```

#### Step 2: Entity 작성

```java
package com.example.demo.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "users")
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private String email;
}
```

#### Step 3: Repository 작성

```java
package com.example.demo.repository;

import com.example.demo.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<User, Long> {
    User findByEmail(String email);
}
```

#### Step 4: Service 작성

```java
package com.example.demo.service;

import com.example.demo.entity.User;
import com.example.demo.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class UserService {

    private final UserRepository userRepository;

    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    public User getUser(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("User not found"));
    }

    @Transactional
    public User createUser(String name, String email) {
        User user = User.builder()
                .name(name)
                .email(email)
                .build();
        return userRepository.save(user);
    }
}
```

#### Step 5: Controller 작성

```java
package com.example.demo.controller;

import com.example.demo.entity.User;
import com.example.demo.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping
    public List<User> getAllUsers() {
        return userService.getAllUsers();
    }

    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        return ResponseEntity.ok(userService.getUser(id));
    }

    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody UserRequest request) {
        User user = userService.createUser(request.name(), request.email());
        return ResponseEntity.ok(user);
    }
}

record UserRequest(String name, String email) {}
```

#### Step 6: 설정 파일

```yaml
# application.yml
spring:
  datasource:
    url: jdbc:h2:mem:testdb
    driver-class-name: org.h2.Driver
  h2:
    console:
      enabled: true
  jpa:
    hibernate:
      ddl-auto: create
    show-sql: true
```

#### Step 7: 실행 및 테스트

```bash
# 실행
./gradlew bootRun

# H2 콘솔 접속
http://localhost:8080/h2-console

# API 테스트
# 사용자 생성
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"홍길동","email":"hong@example.com"}'

# 전체 조회
curl http://localhost:8080/api/users
```

---

### 실습 3: 애플리케이션 설정 커스터마이징

#### Step 1: 포트 변경

```yaml
# application.yml
server:
  port: 9090
```

#### Step 2: 로깅 설정

```yaml
logging:
  level:
    root: INFO
    com.example.demo: DEBUG
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} - %msg%n"
```

#### Step 3: 프로파일별 설정

```yaml
# application-dev.yml (개발)
spring:
  datasource:
    url: jdbc:h2:mem:devdb
  jpa:
    show-sql: true

# application-prod.yml (운영)
spring:
  datasource:
    url: jdbc:mysql://prod-db:3306/mydb
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
  jpa:
    show-sql: false
```

```bash
# 프로파일 지정 실행
java -jar app.jar --spring.profiles.active=prod
```

---

## 👨‍💻 주니어 개발자 실전 시나리오

### 시나리오: "레거시 Spring을 Spring Boot로 마이그레이션"

**상황:**
- 5년된 Spring 프로젝트
- XML 설정 500줄 이상
- Tomcat 수동 배포
- 신규 팀원 온보딩에 1주일 소요

#### Step 1: 현황 분석

```
기존 프로젝트 구조:
webapp/
├── WEB-INF/
│   ├── web.xml (100줄)
│   ├── spring/
│   │   ├── root-context.xml (200줄)
│   │   ├── servlet-context.xml (150줄)
│   │   └── database-context.xml (100줄)
│   └── lib/ (50개 JAR 파일)
```

#### Step 2: 마이그레이션 계획

```
1단계: Spring Boot 프로젝트 생성
2단계: 기존 Java 코드 이동
3단계: XML 설정 → Java/YAML 변환
4단계: 의존성 정리
5단계: 테스트 및 검증
```

#### Step 3: 실행

**1단계: 새 프로젝트 생성**
```bash
# Spring Initializr에서 생성
- Spring Web
- Spring Data JPA
- MySQL Driver
```

**2단계: 코드 이동**
```bash
# 기존 소스 복사
cp -r old-project/src/main/java/com/example/* new-project/src/main/java/com/example/
```

**3단계: 설정 변환**

```xml
<!-- 기존 XML -->
<bean id="dataSource" class="org.apache.commons.dbcp2.BasicDataSource">
    <property name="driverClassName" value="com.mysql.cj.jdbc.Driver"/>
    <property name="url" value="jdbc:mysql://localhost:3306/mydb"/>
    <property name="username" value="root"/>
    <property name="password" value="password"/>
</bean>
```

```yaml
# Spring Boot YAML
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb
    username: root
    password: password
```

**4단계: 의존성 정리**

```gradle
// Before: 50개 개별 의존성
dependencies {
    implementation 'org.springframework:spring-webmvc:5.3.20'
    implementation 'org.springframework:spring-jdbc:5.3.20'
    // 48개 더...
}

// After: 3개 스타터
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    runtimeOnly 'com.mysql.cj:mysql-connector-j'
}
```

#### Step 4: 결과

**마이그레이션 효과:**
- 설정 파일: 550줄 → 30줄 (95% 감소)
- 빌드 시간: 5분 → 30초 (90% 단축)
- 배포 시간: 10분 → 1분 (90% 단축)
- 온보딩 시간: 1주일 → 1일 (85% 단축)

---

## 🏢 기업 사례: Netflix

### 배경

Netflix는 2013년 Spring에서 Spring Boot로 전환을 시작했습니다.

**당시 문제:**
- 마이크로서비스 수백 개 운영
- 각 서비스마다 설정 파일 수백 줄
- 새 서비스 생성에 3일 소요
- 배포 복잡도 증가

### Spring Boot 도입

```java
// Netflix의 표준 Spring Boot 템플릿
@SpringBootApplication
@EnableEurekaClient  // 서비스 디스커버리
@EnableCircuitBreaker  // Hystrix
public class MyMicroservice {
    public static void main(String[] args) {
        SpringApplication.run(MyMicroservice.class, args);
    }
}
```

**효과:**
- 새 서비스 생성: 3일 → 2시간
- 설정 표준화로 유지보수성 향상
- 개발자 생산성 300% 증가
- 클라우드 배포 자동화

---

## ❓ FAQ

### Q1. Spring Boot를 사용하면 Spring을 몰라도 되나요?

**A:** 아니요, Spring의 기본 원리는 반드시 알아야 합니다.

```
Spring Boot = Spring + 편의 기능

알아야 할 것:
- DI/IoC 개념
- Bean 생명주기
- AOP 원리
- 트랜잭션 관리

Spring Boot가 해주는 것:
- 설정 자동화
- 의존성 관리
- 내장 서버 제공
```

**학습 순서:**
1. Spring 핵심 개념 이해 (1-2주)
2. Spring Boot로 실전 개발 (계속)
3. 필요시 내부 원리 학습

### Q2. 자동 설정을 커스터마이징할 수 있나요?

**A:** 네, 여러 방법으로 가능합니다.

```yaml
# 1. application.yml 오버라이드
spring:
  datasource:
    hikari:
      maximum-pool-size: 20  # 기본값 10 변경
```

```java
// 2. @Bean으로 직접 등록 (자동 설정 대체)
@Configuration
public class CustomDataSourceConfig {

    @Bean
    public DataSource dataSource() {
        // 커스텀 DataSource
        return new MyCustomDataSource();
    }
}
```

```yaml
# 3. 특정 자동 설정 비활성화
spring:
  autoconfigure:
    exclude:
      - org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
```

### Q3. WAR vs JAR 배포, 어떤 것을 선택해야 하나요?

**A:** 대부분의 경우 JAR 배포를 권장합니다.

| 상황 | 권장 방식 | 이유 |
|-----|----------|------|
| 신규 프로젝트 | JAR | 간편함, 클라우드 친화적 |
| 레거시 통합 | WAR | 기존 Tomcat 활용 |
| 컨테이너 환경 (Docker) | JAR | 가벼움, 독립 실행 |
| 전통적인 WAS 환경 | WAR | 규정 준수 |

```gradle
// JAR 빌드 (기본)
plugins {
    id 'org.springframework.boot' version '3.2.0'
}

// WAR 빌드
plugins {
    id 'org.springframework.boot' version '3.2.0'
    id 'war'
}

// Main 클래스 수정 필요
@SpringBootApplication
public class MyApplication extends SpringBootServletInitializer {

    @Override
    protected SpringApplicationBuilder configure(SpringApplicationBuilder application) {
        return application.sources(MyApplication.class);
    }

    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}
```

### Q4. 내장 서버를 변경할 수 있나요?

**A:** 네, Tomcat/Jetty/Undertow 선택 가능합니다.

```gradle
// Tomcat → Jetty 변경
dependencies {
    implementation('org.springframework.boot:spring-boot-starter-web') {
        exclude group: 'org.springframework.boot', module: 'spring-boot-starter-tomcat'
    }
    implementation 'org.springframework.boot:spring-boot-starter-jetty'
}
```

**성능 비교:**

| 서버 | 메모리 사용량 | 처리량 | 특징 |
|-----|-------------|-------|------|
| Tomcat | 중간 | 중간 | 범용적, 검증됨 |
| Jetty | 낮음 | 높음 | 비동기 처리 우수 |
| Undertow | 매우 낮음 | 매우 높음 | 성능 최고 |

### Q5. Spring Boot의 단점은 없나요?

**A:** 몇 가지 고려사항이 있습니다.

**단점:**
1. **무거운 초기 로딩**: 자동 설정 스캔으로 시작 시간 증가
2. **블랙박스**: 내부 동작을 모르면 문제 해결 어려움
3. **불필요한 의존성**: 사용하지 않는 라이브러리도 포함될 수 있음

**해결책:**
```java
// 1. 로딩 시간 개선
@SpringBootApplication(exclude = {
    DataSourceAutoConfiguration.class,  // 불필요한 설정 제외
    SecurityAutoConfiguration.class
})

// 2. Lazy Initialization
spring.main.lazy-initialization=true

// 3. 의존성 최적화
dependencies {
    implementation('org.springframework.boot:spring-boot-starter-web') {
        exclude group: 'org.springframework.boot', module: 'spring-boot-starter-tomcat'
    }
}
```

---

## 💼 면접 질문 TOP 5

### ⭐ 초급 1: Spring과 Spring Boot의 차이는?

**답변:**

| 구분 | Spring | Spring Boot |
|-----|--------|-------------|
| 설정 | XML/Java 수동 설정 | 자동 설정 |
| 의존성 | 개별 관리 | 스타터로 일괄 관리 |
| 서버 | 외부 WAS 필요 | 내장 서버 |
| 실행 | WAR 배포 | JAR 실행 |
| 개발 속도 | 느림 | 빠름 |

### ⭐ 초급 2: @SpringBootApplication의 역할은?

**답변:**
3개 애노테이션의 조합입니다.

```java
@SpringBootApplication
= @SpringBootConfiguration  // @Configuration과 동일
+ @EnableAutoConfiguration  // 자동 설정 활성화
+ @ComponentScan            // 컴포넌트 스캔

// 실제 동작
1. 현재 패키지부터 컴포넌트 스캔
2. 클래스패스의 라이브러리 감지
3. 조건에 맞는 Bean 자동 생성
```

### ⭐⭐ 중급 1: 자동 설정이 동작하는 원리는?

**답변:**

```
1. @EnableAutoConfiguration 처리
   ↓
2. spring.factories 파일 로딩
   (META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports)
   ↓
3. 조건부 설정 클래스 평가
   @ConditionalOnClass
   @ConditionalOnMissingBean
   ↓
4. 조건 만족 시 Bean 생성
```

**예시:**
```java
@Configuration
@ConditionalOnClass(DataSource.class)  // DataSource 클래스 있으면
@ConditionalOnMissingBean(DataSource.class)  // DataSource Bean 없으면
public class DataSourceAutoConfiguration {
    @Bean
    public DataSource dataSource() {
        // DataSource 자동 생성
    }
}
```

### ⭐⭐ 중급 2: Starter의 장점은?

**답변:**

```gradle
// Without Starter: 20+ dependencies
dependencies {
    implementation 'org.springframework:spring-webmvc:5.3.20'
    implementation 'org.springframework:spring-web:5.3.20'
    implementation 'com.fasterxml.jackson.core:jackson-databind:2.13.3'
    // 17 more...
}

// With Starter: 1 dependency
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
}
```

**장점:**
1. **의존성 간소화**: 하나로 여러 라이브러리 포함
2. **버전 관리 자동**: 호환되는 버전 자동 선택
3. **충돌 방지**: 검증된 조합 제공

### ⭐⭐ 중급 3: 내장 서버의 장점은?

**답변:**

**장점:**
1. **환경 일관성**: 개발 = 운영
2. **배포 간소화**: `java -jar app.jar`
3. **버전 관리**: Tomcat도 의존성으로 관리
4. **클라우드 친화적**: Docker 컨테이너화 쉬움

**비교:**
```bash
# 전통 방식
1. Tomcat 설치
2. 환경 변수 설정
3. WAR 빌드
4. Tomcat에 배포
5. 서버 재시작

# Spring Boot
java -jar app.jar
```

---

## 🎯 다음 단계

Spring Boot 소개를 마쳤다면:

1. **30장: 자동 설정 원리** - 내부 동작 깊이 이해
2. **31장: 프로퍼티 관리** - 설정 외부화
3. **32장: Actuator** - 운영 모니터링
4. **실전 프로젝트** - REST API 서버 구축

---

**🎓 학습 완료 체크리스트:**

- [ ] Spring과 Spring Boot의 차이 이해
- [ ] 첫 Spring Boot 애플리케이션 생성 및 실행
- [ ] 자동 설정의 개념 이해
- [ ] Starter 의존성 활용
- [ ] 내장 서버로 애플리케이션 실행
- [ ] application.yml로 기본 설정

**다음 장에서는 Spring Boot의 마법, 자동 설정 원리를 깊이 파헤칩니다!** 🚀
