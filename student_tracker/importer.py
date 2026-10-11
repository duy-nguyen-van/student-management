"""Tải học sinh mẫu từ DummyJSON. Điểm được suy ra ổn định từ mã người dùng."""

import json
import urllib.request
from decimal import Decimal

from student_tracker.models import Student

API_URL = "https://dummyjson.com/users?limit=30"
_CENT = Decimal("0.01")
_FETCH_ERRORS = (OSError, ValueError, KeyError, TypeError, UnicodeError, AttributeError)


class SampleFetchError(Exception):
    """Không tải hoặc không đọc được dữ liệu mẫu."""


def fetch_sample_students(url: str = API_URL, timeout: float = 10) -> list[Student]:
    try:
        return _download_sample_students(url, timeout)
    except _FETCH_ERRORS as exc:
        raise SampleFetchError(str(exc)) from exc


def _download_sample_students(url: str, timeout: float) -> list[Student]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "StudentTracker/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.load(response)
    students: list[Student] = []
    for user in payload.get("users", []):
        students.append(student_from_user(user))
    return students


def student_from_user(user: dict) -> Student:
    first = str(user.get("firstName", "")).strip()
    last = str(user.get("lastName", "")).strip()
    name = " ".join(part for part in (first, last) if part)
    user_id = int(user["id"])
    math, literature, english = sample_scores(user_id)
    return Student(
        name=name,
        age=int(user["age"]),
        math=math,
        literature=literature,
        english=english,
        external_id=f"dummyjson:{user_id}",
    )


def sample_scores(user_id: int) -> tuple[Decimal, Decimal, Decimal]:
    math = _sample_mark(user_id, 37)
    literature = _sample_mark(user_id, 53)
    english = _sample_mark(user_id, 71)
    return math, literature, english


def _sample_mark(user_id: int, factor: int) -> Decimal:
    cents = (user_id * factor) % 1001
    return (Decimal(cents) / Decimal(100)).quantize(_CENT)
