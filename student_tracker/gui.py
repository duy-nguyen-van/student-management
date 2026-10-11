"""Giao diện Tkinter. Tải API chạy trên luồng nền, ghi DB trên luồng giao diện."""

import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from student_tracker.importer import SampleFetchError, fetch_sample_students
from student_tracker.manager import StudentManager
from student_tracker.models import Student
from student_tracker.validation import ValidationError

_SAMPLE_NOTE = (
    "Điểm là điểm minh họa tạo từ mã người dùng, vì API không có điểm."
)


class StudentApp(tk.Tk):
    """Cửa sổ quản lý học sinh: nhập, sửa, xóa, tìm và tải dữ liệu mẫu."""

    def __init__(self, manager: StudentManager) -> None:
        super().__init__()
        self.manager = manager
        self.title("Student Tracker – Quản lý học sinh")
        self.geometry("980x640")
        self.minsize(860, 560)
        self._queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self._importing = False
        self._selected_id: int | None = None
        self._build()
        self.refresh()

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        padding = {"padx": 12, "pady": 6}

        form = ttk.LabelFrame(self, text="Thông tin học sinh", padding=12)
        form.grid(row=0, column=0, sticky="ew", **padding)
        for column in range(6):
            form.columnconfigure(column, weight=1)

        self.name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.math_var = tk.StringVar()
        self.literature_var = tk.StringVar()
        self.english_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Sẵn sàng.")

        fields = (
            ("Tên", self.name_var),
            ("Tuổi", self.age_var),
            ("Toán", self.math_var),
            ("Văn", self.literature_var),
            ("Anh", self.english_var),
        )
        for index, (label, variable) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=0, column=index, sticky="w")
            ttk.Entry(form, textvariable=variable).grid(row=1, column=index, sticky="ew", padx=(0, 8))

        actions = ttk.Frame(self, padding=(12, 0))
        actions.grid(row=1, column=0, sticky="ew")
        ttk.Button(actions, text="Thêm", command=self._add).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Sửa", command=self._update).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Xóa", command=self._delete).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Làm mới", command=self._reset).pack(side="left", padx=(0, 12))
        ttk.Label(actions, text="Tìm theo tên").pack(side="left")
        ttk.Entry(actions, textvariable=self.search_var, width=24).pack(side="left", padx=6)
        ttk.Button(actions, text="Tìm", command=self._search).pack(side="left", padx=(0, 6))
        self.import_button = ttk.Button(actions, text="Tải dữ liệu mẫu", command=self._start_import)
        self.import_button.pack(side="left")

        table_frame = ttk.Frame(self, padding=(12, 0))
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        columns = ("name", "age", "math", "literature", "english", "average", "rank")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        headings = {
            "name": "Tên",
            "age": "Tuổi",
            "math": "Toán",
            "literature": "Văn",
            "english": "Anh",
            "average": "ĐTB",
            "rank": "Xếp loại",
        }
        widths = {
            "name": 220,
            "age": 70,
            "math": 80,
            "literature": 80,
            "english": 80,
            "average": 80,
            "rank": 120,
        }
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="center" if column != "name" else "w")
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        status = ttk.Label(self, textvariable=self.status_var, anchor="w", padding=(12, 8))
        status.grid(row=3, column=0, sticky="ew")

    def refresh(self, students: list[Student] | None = None) -> None:
        """Nạp lại bảng. Không truyền danh sách thì lấy toàn bộ học sinh từ manager."""
        if students is None:
            students = self.manager.list_students()
        children = self.tree.get_children()
        if children:
            self.tree.delete(*children)
        for student in students:
            self.tree.insert("", "end", iid=str(student.id), values=_row_values(student))
        self._selected_id = None

    def _add(self) -> None:
        try:
            student = self.manager.add(*self._form_values())
        except ValidationError as exc:
            self.status_var.set(str(exc))
            return
        self._clear_form()
        self.search_var.set("")
        self.refresh()
        self.status_var.set(f"Đã thêm {student.name}. ĐTB {student.average:.2f} – {student.rank}.")

    def _update(self) -> None:
        if self._selected_id is None:
            self.status_var.set("Chọn một học sinh trong danh sách để sửa.")
            return
        try:
            student = self.manager.update(self._selected_id, *self._form_values())
        except ValidationError as exc:
            self.status_var.set(str(exc))
            return
        except LookupError as exc:
            self.status_var.set(str(exc))
            return
        self.refresh()
        self.status_var.set(f"Đã sửa {student.name}. ĐTB {student.average:.2f} – {student.rank}.")
        if self.tree.exists(str(student.id)):
            self.tree.selection_set(str(student.id))
            self._selected_id = student.id

    def _delete(self) -> None:
        if self._selected_id is None:
            self.status_var.set("Chọn một học sinh trong danh sách để xóa.")
            return
        current = self.manager.get(self._selected_id)
        if current is None:
            self.status_var.set("Không tìm thấy")
            self.refresh()
            return
        confirmed = messagebox.askyesno("Xóa học sinh", f"Xóa {current.name}?", parent=self)
        if not confirmed:
            return
        try:
            self.manager.delete(self._selected_id)
        except LookupError as exc:
            self.status_var.set(str(exc))
            return
        self._clear_form()
        self.refresh()
        self.status_var.set(f"Đã xóa {current.name}.")

    def _search(self) -> None:
        query = self.search_var.get().strip()
        if not query:
            self.status_var.set("Nhập tên cần tìm.")
            return
        matches = self.manager.search(query)
        self.refresh(matches)
        if not matches:
            self.status_var.set("Không tìm thấy")
            return
        self.status_var.set(f"Tìm thấy {len(matches)} học sinh.")

    def _reset(self) -> None:
        self.search_var.set("")
        self._clear_form()
        self.refresh()
        self.status_var.set("Sẵn sàng.")

    def _start_import(self) -> None:
        if self._importing:
            return
        self._importing = True
        self.import_button.configure(state="disabled")
        self.status_var.set("Đang tải dữ liệu mẫu...")
        threading.Thread(target=self._fetch_worker, daemon=True).start()
        self.after(100, self._poll_import)

    def _fetch_worker(self) -> None:
        try:
            students = fetch_sample_students()
        except SampleFetchError as exc:
            self._queue.put(("error", str(exc)))
            return
        self._queue.put(("ok", students))

    def _poll_import(self) -> None:
        try:
            kind, payload = self._queue.get_nowait()
        except queue.Empty:
            self.after(100, self._poll_import)
            return
        self._importing = False
        self.import_button.configure(state="normal")
        if kind == "error":
            self.status_var.set(f"Không tải được dữ liệu mẫu: {payload}")
            return
        students = payload
        if not isinstance(students, list):
            self.status_var.set("Dữ liệu mẫu không hợp lệ.")
            return
        try:
            count = self.manager.import_samples(students)
        except ValueError as exc:
            self.status_var.set(str(exc))
            return
        self.refresh()
        self.status_var.set(f"Đã nhập {count} học sinh mẫu. {_SAMPLE_NOTE}")

    def _on_select(self, _event: tk.Event) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        student_id = int(selected[0])
        student = self.manager.get(student_id)
        if student is None:
            return
        self._selected_id = student.id
        self.name_var.set(student.name)
        self.age_var.set(str(student.age))
        self.math_var.set(f"{student.math:.2f}")
        self.literature_var.set(f"{student.literature:.2f}")
        self.english_var.set(f"{student.english:.2f}")

    def _form_values(self) -> tuple[str, str, str, str, str]:
        return (
            self.name_var.get(),
            self.age_var.get(),
            self.math_var.get(),
            self.literature_var.get(),
            self.english_var.get(),
        )

    def _clear_form(self) -> None:
        self._selected_id = None
        self.name_var.set("")
        self.age_var.set("")
        self.math_var.set("")
        self.literature_var.set("")
        self.english_var.set("")
        selection = self.tree.selection()
        if selection:
            self.tree.selection_remove(selection)


def run_gui(manager: StudentManager) -> None:
    """Mở cửa sổ Tkinter và chạy vòng lặp sự kiện."""
    app = StudentApp(manager)
    app.mainloop()


def _row_values(student: Student) -> tuple[str, int, str, str, str, str, str]:
    return (
        student.name,
        student.age,
        f"{student.math:.2f}",
        f"{student.literature:.2f}",
        f"{student.english:.2f}",
        f"{student.average:.2f}",
        student.rank,
    )
