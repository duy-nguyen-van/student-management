"""Mô hình học sinh."""

import unicodedata
from dataclasses import dataclass
from decimal import Decimal

from student_tracker.grading import average, classify


def fold_name(name: str) -> str:
    return unicodedata.normalize("NFC", name).casefold().strip()


@dataclass
class Student:
    name: str
    age: int
    math: Decimal
    literature: Decimal
    english: Decimal
    id: int | None = None
    external_id: str | None = None

    @property
    def average(self) -> Decimal:
        return average(self.math, self.literature, self.english)

    @property
    def rank(self) -> str:
        return classify(self.average)
