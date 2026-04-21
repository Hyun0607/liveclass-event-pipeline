CREATE TABLE IF NOT EXISTS events (
    event_id    CHAR(36)    NOT NULL,
    event_type  VARCHAR(30) NOT NULL,
    user_id     VARCHAR(10) NOT NULL,
    session_id  CHAR(36)    NOT NULL,
    timestamp   DATETIME    NOT NULL,
    device_type VARCHAR(10) NOT NULL,
    PRIMARY KEY (event_id),
    INDEX idx_event_type (event_type),
    INDEX idx_user_id    (user_id),
    INDEX idx_timestamp  (timestamp)
);

CREATE TABLE IF NOT EXISTS event_course_purchase (
    event_id       CHAR(36)     NOT NULL,
    course_id      VARCHAR(10)  NOT NULL,
    course_title   VARCHAR(100) NOT NULL,
    instructor_id  VARCHAR(10)  NOT NULL,
    price          INT          NOT NULL,
    payment_method VARCHAR(20)  NOT NULL,
    category       VARCHAR(20)  NOT NULL,
    PRIMARY KEY (event_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

CREATE TABLE IF NOT EXISTS event_lecture_play (
    event_id         CHAR(36)    NOT NULL,
    course_id        VARCHAR(10) NOT NULL,
    lecture_id       VARCHAR(10) NOT NULL,
    playback_quality VARCHAR(10) NOT NULL,
    progress_seconds INT         NOT NULL,
    PRIMARY KEY (event_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

CREATE TABLE IF NOT EXISTS event_lecture_complete (
    event_id               CHAR(36)    NOT NULL,
    course_id              VARCHAR(10) NOT NULL,
    lecture_id             VARCHAR(10) NOT NULL,
    total_duration_seconds INT         NOT NULL,
    watch_duration_seconds INT         NOT NULL,
    PRIMARY KEY (event_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

CREATE TABLE IF NOT EXISTS event_review_submit (
    event_id      CHAR(36)     NOT NULL,
    course_id     VARCHAR(10)  NOT NULL,
    course_title  VARCHAR(100) NOT NULL,
    rating        TINYINT      NOT NULL,
    review_text   TEXT         NOT NULL,
    PRIMARY KEY (event_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

CREATE TABLE IF NOT EXISTS event_error (
    event_id      CHAR(36)     NOT NULL,
    error_code    VARCHAR(30)  NOT NULL,
    error_message VARCHAR(100) NOT NULL,
    page_url      VARCHAR(100) NOT NULL,
    PRIMARY KEY (event_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);
