import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from student_tracker.models import Student
from student_tracker.repository import SqliteRepository


class RepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.repo = SqliteRepository(Path(self._temp.name) / "students.db")

    def tearDown(self) -> None:
        self.repo.close()
        self._temp.cleanup()

    def test_wal_mode(self) -> None:
        mode = self.repo._conn.execute("PRAGMA journal_mode").fetchone()[0]
        self.assertEqual(str(mode).lower(), "wal")

    def test_score_roundtrip_and_rank(self) -> None:
        saved = self.repo.add(
            Student(
                name="Lê Lan",
                age=16,
                math=Decimal("8.10"),
                literature=Decimal("6.50"),
                english=Decimal("5.00"),
            )
        )
        loaded = self.repo.get(saved.id or 0)
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded.math, Decimal("8.10"))
        self.assertEqual(loaded.literature, Decimal("6.50"))
        self.assertEqual(loaded.english, Decimal("5.00"))
        self.assertEqual(loaded.average, Decimal("6.53"))
        self.assertEqual(loaded.rank, "Khá")

    def test_search_folds_case_and_escapes_wildcards(self) -> None:
        self.repo.add(_student("Nguyễn An"))
        self.repo.add(_student("Trần Bình"))
        self.repo.add(_student("100%"))
        self.repo.add(_student("A_B"))

        self.assertEqual([item.name for item in self.repo.search("NGUYỄN")], ["Nguyễn An"])
        self.assertEqual([item.name for item in self.repo.search("an")], ["Nguyễn An"])
        self.assertEqual(self.repo.search("zzz"), [])
        self.assertEqual([item.name for item in self.repo.search("%")], ["100%"])
        self.assertEqual([item.name for item in self.repo.search("_")], ["A_B"])

    def test_import_upsert_keeps_one_row(self) -> None:
        self.repo.import_external([_student("An", external_id="dummyjson:1", math=Decimal("1"))])
        self.repo.import_external(
            [_student("Bình", external_id="dummyjson:1", math=Decimal("9"), literature=Decimal("9"), english=Decimal("9"))]
        )
        rows = self.repo.list_all()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].name, "Bình")
        self.assertEqual(rows[0].math, Decimal("9.00"))
        self.assertEqual(rows[0].external_id, "dummyjson:1")

    def test_manual_rows_allow_empty_external_id(self) -> None:
        self.repo.add(_student("An"))
        self.repo.add(_student("An"))
        self.assertEqual(len(self.repo.list_all()), 2)


def _student(
    name: str,
    external_id: str | None = None,
    math: Decimal = Decimal("8"),
    literature: Decimal = Decimal("8"),
    english: Decimal = Decimal("8"),
) -> Student:
    return Student(
        name=name,
        age=15,
        math=math,
        literature=literature,
        english=english,
        external_id=external_id,
    )


if __name__ == "__main__":
    unittest.main()
