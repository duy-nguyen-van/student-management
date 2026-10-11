"""Menu terminal: input, while, for, list, và biến cờ tìm kiếm."""

from student_tracker.manager import StudentManager
from student_tracker.models import Student
from student_tracker.validation import ValidationError


def run_cli(manager: StudentManager) -> None:
    while True:
        _print_menu()
        try:
            choice = input("Chọn chức năng: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if choice == "1":
            add_one(manager)
        elif choice == "2":
            add_many(manager)
        elif choice == "3":
            show_students(manager)
        elif choice == "4":
            search_students(manager)
        elif choice == "5":
            edit_student(manager)
        elif choice == "6":
            delete_student(manager)
        elif choice == "0":
            print("Đã thoát.")
            break
        else:
            print("Lựa chọn không hợp lệ.")


def add_one(manager: StudentManager) -> None:
    _add_until_valid(manager)


def add_many(manager: StudentManager) -> None:
    raw = input("Số lượng học sinh N: ").strip()
    if not raw.isdigit() or int(raw) < 1:
        print("N phải là số nguyên dương.")
        return
    count = int(raw)
    for index in range(1, count + 1):
        print(f"--- Học sinh {index}/{count} ---")
        _add_until_valid(manager)


def show_students(manager: StudentManager) -> None:
    students: list[Student] = manager.list_students()
    if not students:
        print("Chưa có học sinh.")
        return
    for student in students:
        print(format_student(student))


def search_students(manager: StudentManager) -> None:
    query = input("Tên cần tìm: ").strip()
    matches: list[Student] = manager.search(query)
    found = False
    for student in matches:
        found = True
        print(format_student(student))
    if not found:
        print("Không tìm thấy")


def edit_student(manager: StudentManager) -> None:
    student_id = _prompt_id("Mã học sinh cần sửa: ")
    if student_id is None:
        return
    current = manager.get(student_id)
    if current is None:
        print("Không tìm thấy")
        return
    print(f"Hiện tại: {format_student(current)}")
    try:
        updated = manager.update(student_id, *_prompt_fields())
    except ValidationError as exc:
        print(exc)
        return
    print(f"Đã sửa: {format_student(updated)}")


def delete_student(manager: StudentManager) -> None:
    student_id = _prompt_id("Mã học sinh cần xóa: ")
    if student_id is None:
        return
    current = manager.get(student_id)
    if current is None:
        print("Không tìm thấy")
        return
    print(format_student(current))
    confirm = input("Xóa học sinh này? (y/n): ").strip().casefold()
    if confirm != "y":
        print("Đã hủy.")
        return
    try:
        manager.delete(student_id)
    except LookupError as exc:
        print(exc)
        return
    print("Đã xóa.")


def format_student(student: Student) -> str:
    return (
        f"#{student.id} | {student.name} – Tuổi: {student.age} – "
        f"Toán: {student.math:.2f} – Văn: {student.literature:.2f} – "
        f"Anh: {student.english:.2f} – ĐTB: {student.average:.2f} – {student.rank}"
    )


def _print_menu() -> None:
    print()
    print("===== Student Tracker =====")
    print("1. Thêm một học sinh")
    print("2. Nhập nhiều học sinh")
    print("3. Hiển thị danh sách")
    print("4. Tìm theo tên")
    print("5. Sửa thông tin")
    print("6. Xóa học sinh")
    print("0. Thoát")


def _add_until_valid(manager: StudentManager) -> None:
    while True:
        try:
            student = manager.add(*_prompt_fields())
        except ValidationError as exc:
            print(exc)
            continue
        print(f"Đã lưu: {format_student(student)}")
        return


def _prompt_fields() -> tuple[str, str, str, str, str]:
    name = input("Tên: ")
    age = input("Tuổi: ")
    math = input("Điểm Toán: ")
    literature = input("Điểm Văn: ")
    english = input("Điểm Anh: ")
    return name, age, math, literature, english


def _prompt_id(label: str) -> int | None:
    raw = input(label).strip()
    if not raw.isdigit() or int(raw) < 1:
        print("Mã học sinh phải là số nguyên dương.")
        return None
    return int(raw)
