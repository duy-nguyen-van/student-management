"""SQLite repository cho danh sách học sinh."""

import sqlite3
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from student_tracker.models import Student, fold_name

_CENT = Decimal("0.01")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    name_key TEXT NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 1 AND age <= 120),
    math REAL NOT NULL CHECK (math >= 0 AND math <= 10),
    literature REAL NOT NULL CHECK (literature >= 0 AND literature <= 10),
    english REAL NOT NULL CHECK (english >= 0 AND english <= 10),
    external_id TEXT UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_students_name_key ON students(name_key);
"""

_INSERT = """
INSERT INTO students (name, name_key, age, math, literature, english, external_id)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""

_UPSERT = """
INSERT INTO students (name, name_key, age, math, literature, english, external_id)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(external_id) DO UPDATE SET
    name = excluded.name,
    name_key = excluded.name_key,
    age = excluded.age,
    math = excluded.math,
    literature = excluded.literature,
    english = excluded.english
"""


def score_to_real(score: Decimal) -> float:
    return float(Decimal(score).quantize(_CENT, rounding=ROUND_HALF_UP))


def score_from_real(value: float) -> Decimal:
    return Decimal(str(value)).quantize(_CENT, rounding=ROUND_HALF_UP)


class SqliteRepository:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        self._configure()
        self._conn.executescript(_SCHEMA)

    def _configure(self) -> None:
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.execute("PRAGMA cache_size=-8000")

    def close(self) -> None:
        self._conn.close()

    def add(self, student: Student) -> Student:
        with self._conn:
            cursor = self._conn.execute(_INSERT, _values(student))
        return Student(
            id=int(cursor.lastrowid),
            name=student.name,
            age=student.age,
            math=student.math,
            literature=student.literature,
            english=student.english,
            external_id=student.external_id,
        )

    def update(self, student: Student) -> bool:
        if student.id is None:
            raise ValueError("Thiếu mã học sinh.")
        with self._conn:
            cursor = self._conn.execute(
                """
                UPDATE students
                SET name = ?, name_key = ?, age = ?, math = ?, literature = ?, english = ?
                WHERE id = ?
                """,
                (
                    student.name,
                    fold_name(student.name),
                    student.age,
                    score_to_real(student.math),
                    score_to_real(student.literature),
                    score_to_real(student.english),
                    student.id,
                ),
            )
        return cursor.rowcount > 0

    def delete(self, student_id: int) -> bool:
        with self._conn:
            cursor = self._conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        return cursor.rowcount > 0

    def get(self, student_id: int) -> Student | None:
        row = self._conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        if row is None:
            return None
        return _from_row(row)

    def list_all(self) -> list[Student]:
        rows = self._conn.execute("SELECT * FROM students ORDER BY name_key, id").fetchall()
        return [_from_row(row) for row in rows]

    def search(self, query: str) -> list[Student]:
        key = fold_name(query)
        if not key:
            return []
        pattern = f"%{_escape_like(key)}%"
        rows = self._conn.execute(
            """
            SELECT * FROM students
            WHERE name_key LIKE ? ESCAPE '\\'
            ORDER BY name_key, id
            """,
            (pattern,),
        ).fetchall()
        return [_from_row(row) for row in rows]

    def import_external(self, students: list[Student]) -> int:
        if not students:
            return 0
        rows: list[tuple[object, ...]] = []
        for student in students:
            if not student.external_id:
                raise ValueError("Học sinh nhập từ API phải có external_id.")
            rows.append(_values(student))
        with self._conn:
            self._conn.executemany(_UPSERT, rows)
        return len(rows)


def _values(student: Student) -> tuple[object, ...]:
    return (
        student.name,
        fold_name(student.name),
        student.age,
        score_to_real(student.math),
        score_to_real(student.literature),
        score_to_real(student.english),
        student.external_id,
    )


def _from_row(row: sqlite3.Row) -> Student:
    return Student(
        id=int(row["id"]),
        name=str(row["name"]),
        age=int(row["age"]),
        math=score_from_real(row["math"]),
        literature=score_from_real(row["literature"]),
        english=score_from_real(row["english"]),
        external_id=row["external_id"],
    )


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
