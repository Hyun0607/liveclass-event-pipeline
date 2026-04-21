# 라이브클래스 이벤트 로그 파이프라인

라이브클래스(온라인 강의 판매 플랫폼)의 수강생 행동 이벤트를 생성하고, MySQL에 저장하고, 집계 분석 및 시각화하는 데이터 파이프라인입니다.

## 파이프라인 구조

```
이벤트 생성 (event_generator.py)
        ↓
MySQL 저장 (save_to_db.py)
        ↓
집계 분석 & 시각화 (analyze.py / Metabase)
```

---

## 실행 방법

### 필요 도구
- Docker Desktop
- Python 3.11 이상 (로컬 분석 실행 시)

### 1. 이벤트 생성 & DB 저장 (자동)

```bash
docker compose up --build
```

실행하면 아래 순서로 자동 동작합니다:
1. MySQL 컨테이너 기동 및 스키마 자동 생성
2. Python 앱이 이벤트 1,000건 생성 후 MySQL에 저장

### 2. Metabase 대시보드

`docker compose up` 실행 후 브라우저에서 `http://localhost:3000` 접속

DB 연결 설정:
| 항목 | 값 |
|---|---|
| Type | MySQL |
| Host | `mysql` |
| Port | `3306` |
| Database | `liveclas_events` |
| Username | `pipeline` |
| Password | `pipeline123` |

DBeaver 로컬 접속 시 Port는 `3307` 사용

---

## 스키마 설명

이벤트 종류마다 필요한 필드가 다르기 때문에, **공통 필드는 `events` 테이블 하나에 모으고 이벤트 타입별 고유 필드는 별도 상세 테이블로 분리**하는 구조를 선택했습니다. 하나의 테이블에 모든 필드를 넣으면 대부분의 컬럼이 NULL로 낭비되기 때문입니다. `event_id`(UUID)를 PK이자 FK로 사용해 두 테이블을 연결하며, 자주 쓰는 `event_type`, `user_id`, `timestamp` 컬럼에 인덱스를 걸어 집계 쿼리 성능을 높였습니다.

### 테이블 구성

| 테이블 | 역할 |
|---|---|
| `events` | 모든 이벤트의 공통 필드 (event_id, event_type, user_id, session_id, timestamp, device_type) |
| `event_course_purchase` | 강의 구매 — course_id, course_title, price, payment_method, category |
| `event_lecture_play` | 강의 재생 — course_id, lecture_id, playback_quality, progress_seconds |
| `event_lecture_complete` | 강의 완강 — course_id, lecture_id, total_duration_seconds, watch_duration_seconds |
| `event_review_submit` | 리뷰 작성 — course_id, rating, review_text |
| `event_error` | 에러 발생 — error_code, error_message, page_url |

> 실무에서는 강의 메타정보(course_title 등)를 별도 `courses` 마스터 테이블로 관리하는 것이 적합하나, 이 과제에서는 이벤트 로그 파이프라인 구현에 집중하기 위해 생략했습니다.

---

## 집계 분석 쿼리

### 분석 1. 강의별 매출 & 구매 횟수

```sql
SELECT
    course_id,
    course_title,
    category,
    COUNT(*)   AS purchase_count,
    SUM(price) AS total_revenue
FROM event_course_purchase
GROUP BY course_id, course_title, category
ORDER BY total_revenue DESC
```

### 분석 2. 시간대별 이벤트 추이

```sql
SELECT
    HOUR(timestamp) AS hour,
    COUNT(*)        AS event_count
FROM events
GROUP BY HOUR(timestamp)
ORDER BY hour
```

### 분석 3. 강의별 완강률

```sql
SELECT
    p.course_id,
    cp.course_title,
    p.play_count,
    COALESCE(c.complete_count, 0) AS complete_count,
    ROUND(COALESCE(c.complete_count, 0) / p.play_count * 100, 1) AS completion_rate_pct
FROM (
    SELECT course_id, COUNT(*) AS play_count
    FROM event_lecture_play
    GROUP BY course_id
) p
LEFT JOIN (
    SELECT course_id, COUNT(*) AS complete_count
    FROM event_lecture_complete
    GROUP BY course_id
) c ON p.course_id = c.course_id
LEFT JOIN (
    SELECT DISTINCT course_id, course_title
    FROM event_course_purchase
) cp ON p.course_id = cp.course_id
ORDER BY completion_rate_pct DESC
```

---

## 구현하면서 고민한 점

### Step 1. 이벤트 설계

다양한 웹사이트 도메인이 존재하지만, 라이브클래스와 유사한 교육 도메인에서 이벤트를 설계하는 것이 더 의미 있는 분석 결과로 이어질 수 있다고 판단했습니다. 향후 실제 업무와의 연관성까지 고려했을 때, 이질적인 도메인보다 인강·교육 데이터를 기반으로 접근하는 것이 적절하다고 보아 해당 데이터로 프로젝트를 시작했습니다.

이벤트 타입을 정의하기 위해 교육 플랫폼에서 핵심적으로 봐야 할 지표를 고민했습니다. 그 결과 단순 매출보다 **완강률**이 더 중요한 지표라고 판단했습니다. 강의 구매는 일회성 성과에 그칠 수 있지만, 완강은 사용자가 실제로 가치를 소비했음을 의미하며 플랫폼의 지속적인 성장과 직결된다고 보았기 때문입니다.

이에 따라 학습 행동 추적을 위한 `lecture_play`, `lecture_complete` 이벤트와 매출 분석을 위한 `course_purchase` 이벤트를 정의했습니다. 또한 사용자 만족도 지표로 `review_submit`을, 서비스 안정성 모니터링을 위해 `error` 이벤트를 포함했습니다.

### Step 2. 저장소 선택

DB 저장소는 MySQL을 DBeaver로 연결해 사용했습니다. RDB로서 운영하기 편하고 오픈소스이기에 다루기 쉬웠으며, 추후 BigQuery 혹은 CDC 연결 등의 확장성을 고려했을 때도 MySQL이라면 어렵지 않게 쓸 수 있다고 판단했습니다. 또한 빠른 데이터 분석과 시각화, Docker와의 호환성을 고려했을 때 가장 알맞는다고 생각했습니다.

### Step 3. 집계 분석

완강률 쿼리에서 `event_lecture_play`와 `event_lecture_complete`는 서로 직접 연결된 키가 없어, 각각 `course_id` 기준으로 집계한 뒤 JOIN하는 방식으로 처리했습니다. 또한 course_title이 `event_course_purchase` 테이블에만 존재하는 구조적 한계를 인지했으며, 실무에서는 별도 마스터 테이블 관리가 필요하다는 점을 확인했습니다.

### Step 4. Docker 구성

`docker compose up` 한 번으로 MySQL 기동 → 스키마 생성 → 이벤트 저장까지 자동화했습니다. MySQL 8.0의 기본 인증 방식(`caching_sha2_password`)이 Metabase JDBC 드라이버와 호환되지 않아 `--default-authentication-plugin=mysql_native_password` 옵션을 추가하는 과정에서 클라이언트에 따라 DB 인증 방식 호환성이 달라질 수 있다는 점을 배웠습니다.

### Step 5. 시각화

집계 분석과 시각화를 모두 Metabase에서 진행했습니다. Metabase는 MySQL과 직접 연결되어 SQL 쿼리 결과를 바로 Bar chart, Line chart 등으로 시각화할 수 있어 별도 코드 없이 대시보드를 구성할 수 있었습니다. docker-compose에 서비스로 추가해 `docker compose up` 한 번으로 Metabase까지 함께 실행되도록 구성했습니다.
