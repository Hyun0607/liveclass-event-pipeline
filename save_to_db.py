import os
import time
import mysql.connector
from mysql.connector import Error
from event_generator import generate_events

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 3306)),
    "database": os.getenv("DB_NAME", "liveclas_events"),
    "user":     os.getenv("DB_USER", "pipeline"),
    "password": os.getenv("DB_PASSWORD", "pipeline123"),
}

# 이벤트 타입별 detail 테이블 INSERT SQL
DETAIL_SQL = {
    "page_view": (
        "INSERT INTO event_page_view (event_id, page_name, course_id, referrer) "
        "VALUES (%(event_id)s, %(page_name)s, %(course_id)s, %(referrer)s)"
    ),
    "course_purchase": (
        "INSERT INTO event_course_purchase "
        "(event_id, course_id, course_title, instructor_id, price, payment_method, category) "
        "VALUES (%(event_id)s, %(course_id)s, %(course_title)s, %(instructor_id)s, "
        "%(price)s, %(payment_method)s, %(category)s)"
    ),
    "lecture_play": (
        "INSERT INTO event_lecture_play "
        "(event_id, course_id, lecture_id, playback_quality, progress_seconds) "
        "VALUES (%(event_id)s, %(course_id)s, %(lecture_id)s, %(playback_quality)s, %(progress_seconds)s)"
    ),
    "lecture_complete": (
        "INSERT INTO event_lecture_complete "
        "(event_id, course_id, lecture_id, total_duration_seconds, watch_duration_seconds) "
        "VALUES (%(event_id)s, %(course_id)s, %(lecture_id)s, %(total_duration_seconds)s, %(watch_duration_seconds)s)"
    ),
    "review_submit": (
        "INSERT INTO event_review_submit "
        "(event_id, course_id, course_title, rating, review_text) "
        "VALUES (%(event_id)s, %(course_id)s, %(course_title)s, %(rating)s, %(review_text)s)"
    ),
    "search": (
        "INSERT INTO event_search (event_id, query, result_count) "
        "VALUES (%(event_id)s, %(query)s, %(result_count)s)"
    ),
    "error": (
        "INSERT INTO event_error (event_id, error_code, error_message, page_url) "
        "VALUES (%(event_id)s, %(error_code)s, %(error_message)s, %(page_url)s)"
    ),
}

BASE_SQL = (
    "INSERT INTO events (event_id, event_type, user_id, session_id, timestamp, device_type) "
    "VALUES (%(event_id)s, %(event_type)s, %(user_id)s, %(session_id)s, %(timestamp)s, %(device_type)s)"
)


def wait_for_db(retries: int = 15, delay: int = 5) -> mysql.connector.MySQLConnection:
    for attempt in range(1, retries + 1):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            print(f"DB 연결 성공 (시도 {attempt}회)")
            return conn
        except Error as e:
            print(f"DB 연결 대기 중... ({attempt}/{retries}): {e}")
            time.sleep(delay)
    raise RuntimeError("MySQL 연결 실패")


def insert_events(conn: mysql.connector.MySQLConnection, events: list[dict]) -> None:
    cursor = conn.cursor()
    for event in events:
        cursor.execute(BASE_SQL, event)
        detail_sql = DETAIL_SQL.get(event["event_type"])
        if detail_sql:
            cursor.execute(detail_sql, event)
    conn.commit()
    cursor.close()


def main() -> None:
    print("이벤트 1,000건 생성 중...")
    events = generate_events(1000)

    conn = wait_for_db()
    try:
        insert_events(conn, events)
        print(f"총 {len(events)}건 MySQL 저장 완료")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
