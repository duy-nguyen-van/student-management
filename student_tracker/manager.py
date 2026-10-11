"""Luồng nghiệp vụ: kiểm tra dữ liệu rồi gọi repository."""

from student_tracker.models import Student
from student_tracker.repository import SqliteRepository
from student_tracker.validation import validate_student_fields, ValidationError


class StudentManager:
    def __init__(self, repository: SqliteRepository) -> None:
        self._repository = repository

    def add(
        self,
        name: object,
        age: object,
        math: object,
        literature: object,
        english: object,
    ) -> Student:
        return self._repository.add(self._build(name, age, math, literature, english))

    def update(
        self,
        student_id: int,
        name: object,
        age: object,
        math: object,
        literature: object,
        english: object,
    ) -> Student:
        if self._repository.get(student_id) is None:
            raise LookupError("Không tìm thấy học sinh.")
        student = self._build(name, age, math, literature, english, student_id=student_id)
        self._repository.update(student)
        return student

    def delete(self, student_id: int) -> None:
        if not self._repository.delete(student_id):
            raise LookupError("Không tìm thấy học sinh.")

    def get(self, student_id: int) -> Student | None:
        return self._repository.get(student_id)

    def list_students(self) -> list[Student]:
        return self._repository.list_all()

    def search(self, query: str) -> list[Student]:
        return self._repository.search(query)

    def import_samples(self, students: list[Student]) -> int:
        cleaned: list[Student] = []
        for student in students:
            if not student.external_id:
                raise ValidationError("Học sinh mẫu phải có mã nguồn.")
            built = self._build(
                student.name,
                student.age,
                student.math,
                student.literature,
                student.english,
                external_id=student.external_id,
            )
            cleaned.append(built)
        return self._repository.import_external(cleaned)

    def _build(
        self,
        name: object,
        age: object,
        math: object,
        literature: object,
        english: object,
        student_id: int | None = None,
        external_id: str | None = None,
    ) -> Student:
        cleaned_name, cleaned_age, math_score, literature_score, english_score = (
            validate_student_fields(name, age, math, literature, english)
        )
        return Student(
            id=student_id,
            name=cleaned_name,
            age=cleaned_age,
            math=math_score,
            literature=literature_score,
            english=english_score,
            external_id=external_id,
        )
