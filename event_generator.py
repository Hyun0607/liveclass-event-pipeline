import uuid
import json
import random
from datetime import datetime, timedelta

# ── 도메인 데이터 ──────────────────────────────────────────────
COURSES = [
    {"course_id": "C001", "title": "파이썬으로 시작하는 데이터 분석", "instructor_id": "I001", "price": 89000, "category": "개발"},
    {"course_id": "C002", "title": "직장인을 위한 엑셀 마스터",       "instructor_id": "I002", "price": 49000, "category": "업무스킬"},
    {"course_id": "C003", "title": "SNS 마케팅 완전정복",             "instructor_id": "I003", "price": 79000, "category": "마케팅"},
    {"course_id": "C004", "title": "포토샵 & 일러스트 기초",          "instructor_id": "I004", "price": 69000, "category": "디자인"},
    {"course_id": "C005", "title": "재테크 입문: 주식과 ETF",         "instructor_id": "I005", "price": 99000, "category": "재테크"},
    {"course_id": "C006", "title": "유튜브 채널 운영 노하우",          "instructor_id": "I001", "price": 59000, "category": "크리에이터"},
    {"course_id": "C007", "title": "글쓰기로 돈 버는 법",             "instructor_id": "I006", "price": 45000, "category": "글쓰기"},
    {"course_id": "C008", "title": "온라인 강의 기획 & 제작",         "instructor_id": "I002", "price": 119000, "category": "크리에이터"},
]

LECTURES = {
    "C001": [f"L{i:03d}" for i in range(1, 16)],
    "C002": [f"L{i:03d}" for i in range(1, 11)],
    "C003": [f"L{i:03d}" for i in range(1, 13)],
    "C004": [f"L{i:03d}" for i in range(1, 20)],
    "C005": [f"L{i:03d}" for i in range(1, 12)],
    "C006": [f"L{i:03d}" for i in range(1, 8)],
    "C007": [f"L{i:03d}" for i in range(1, 10)],
    "C008": [f"L{i:03d}" for i in range(1, 18)],
}

DEVICES = ["desktop", "mobile", "tablet"]
PAYMENT_METHODS = ["card", "kakao_pay", "naver_pay", "toss"]
ERROR_CODES = [
    {"code": "VIDEO_LOAD_FAIL",   "message": "영상을 불러오는 데 실패했습니다."},
    {"code": "PAYMENT_TIMEOUT",   "message": "결제 요청이 시간 초과되었습니다."},
    {"code": "AUTH_EXPIRED",      "message": "로그인 세션이 만료되었습니다."},
    {"code": "CONTENT_NOT_FOUND", "message": "요청한 강의를 찾을 수 없습니다."},
]
REVIEWS_BY_RATING = {
    1: [
        "기대했던 것과 너무 달랐어요. 내용이 너무 부실합니다.",
        "설명이 너무 불친절하고 내용도 얕아서 실망했습니다.",
        "돈이 아깝네요. 무료 유튜브보다 못한 것 같아요.",
        "강의 구성이 엉망이고 음질도 너무 나빠요.",
    ],
    2: [
        "내용은 있는데 설명이 너무 빠르고 불친절해요.",
        "초보자한테는 너무 어렵게 설명하는 것 같아요.",
        "기대에 못 미쳤어요. 좀 더 보완이 필요할 것 같습니다.",
        "강의 자료도 부실하고 예제도 너무 적어요.",
    ],
    3: [
        "무난한 강의입니다. 딱히 나쁘지도 좋지도 않아요.",
        "기본적인 내용은 잘 다루는데 심화 내용이 아쉬워요.",
        "보통 수준의 강의입니다. 가격 대비 평범해요.",
        "나쁘지 않은데 특별히 추천하기도 애매하네요.",
    ],
    4: [
        "설명이 친절하고 이해하기 쉬웠어요. 추천합니다!",
        "실무에 바로 적용할 수 있는 내용이 많아서 좋았어요.",
        "강의 구성이 체계적이고 예제도 풍부해서 만족합니다.",
        "전반적으로 만족스러운 강의였어요. 다음 강의도 기대됩니다.",
    ],
    5: [
        "정말 최고의 강의입니다! 완강하고 나서 실력이 확실히 늘었어요.",
        "이 가격에 이런 퀄리티라니 놀랍습니다. 강력 추천!",
        "강사님 설명이 너무 명확하고 이해가 쏙쏙 됩니다. 감사해요!",
        "완강했는데 아깝지 않은 강의였어요. 주변에도 추천하고 싶어요.",
        "실습 예제가 실무와 딱 맞아서 바로 써먹을 수 있었어요!",
    ],
}

USER_IDS  = [f"U{i:04d}" for i in range(1, 201)]   # 수강생 200명
SESSION_POOL = [str(uuid.uuid4()) for _ in range(500)]


# ── 공통 필드 ──────────────────────────────────────────────────
def _base(event_type: str, ts: datetime) -> dict:
    return {
        "event_id":   str(uuid.uuid4()),
        "event_type": event_type,
        "user_id":    random.choice(USER_IDS),
        "session_id": random.choice(SESSION_POOL),
        "timestamp":  ts.isoformat(),
        "device_type": random.choice(DEVICES),
    }


# ── 이벤트 생성 함수 ───────────────────────────────────────────
def make_course_purchase(ts: datetime) -> dict:
    course = random.choice(COURSES)
    return {
        **_base("course_purchase", ts),
        "course_id":      course["course_id"],
        "course_title":   course["title"],
        "instructor_id":  course["instructor_id"],
        "price":          course["price"],
        "payment_method": random.choice(PAYMENT_METHODS),
        "category":       course["category"],
    }


def make_lecture_play(ts: datetime) -> dict:
    course = random.choice(COURSES)
    lecture_id = random.choice(LECTURES[course["course_id"]])
    return {
        **_base("lecture_play", ts),
        "course_id":        course["course_id"],
        "lecture_id":       lecture_id,
        "playback_quality": random.choice(["1080p", "720p", "480p"]),
        "progress_seconds": random.randint(0, 300),
    }


def make_lecture_complete(ts: datetime) -> dict:
    course = random.choice(COURSES)
    lecture_id = random.choice(LECTURES[course["course_id"]])
    duration = random.randint(600, 3600)
    return {
        **_base("lecture_complete", ts),
        "course_id":              course["course_id"],
        "lecture_id":             lecture_id,
        "total_duration_seconds": duration,
        "watch_duration_seconds": random.randint(int(duration * 0.8), duration),
    }


def make_review_submit(ts: datetime) -> dict:
    course = random.choice(COURSES)
    rating = random.choices([1, 2, 3, 4, 5], weights=[2, 3, 10, 30, 55])[0]
    return {
        **_base("review_submit", ts),
        "course_id":   course["course_id"],
        "course_title": course["title"],
        "rating":      rating,
        "review_text": random.choice(REVIEWS_BY_RATING[rating]),
    }


def make_error(ts: datetime) -> dict:
    err = random.choice(ERROR_CODES)
    return {
        **_base("error", ts),
        "error_code":    err["code"],
        "error_message": err["message"],
        "page_url":      f"/courses/{random.choice(COURSES)['course_id']}",
    }


# ── 이벤트 믹스 (현실적인 비율) ──────────────────────────────
EVENT_FACTORIES = [
    (make_lecture_play,     40),
    (make_lecture_complete, 25),
    (make_course_purchase,  20),
    (make_review_submit,    10),
    (make_error,             5),
]

_factories, _weights = zip(*EVENT_FACTORIES)


def generate_events(n: int = 1000, days: int = 30) -> list[dict]:
    now = datetime.now()
    start = now - timedelta(days=days)

    events = []
    for _ in range(n):
        ts = start + timedelta(seconds=random.randint(0, days * 86400))
        factory = random.choices(_factories, weights=_weights, k=1)[0]
        events.append(factory(ts))

    events.sort(key=lambda e: e["timestamp"])
    return events


if __name__ == "__main__":
    
    # 1000개의 이벤트를 생성해서 파일로 저장
    events = generate_events(1000)
    
    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    
    print(f"총 {len(events)}개의 데이터를 events.json 파일로 저장했습니다.")
