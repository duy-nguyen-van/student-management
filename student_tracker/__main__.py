"""Điểm vào: giao diện mặc định, hoặc menu terminal với --cli."""

import argparse

from student_tracker.manager import StudentManager
from student_tracker.paths import database_path
from student_tracker.repository import SqliteRepository


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Student Tracker – Quản lý học sinh")
    parser.add_argument("--cli", action="store_true", help="Chạy menu trên terminal")
    args = parser.parse_args(argv)
    repository = SqliteRepository(database_path())
    manager = StudentManager(repository)
    try:
        if args.cli:
            from student_tracker.cli import run_cli

            run_cli(manager)
        else:
            try:
                from student_tracker.gui import run_gui
            except ModuleNotFoundError as exc:
                if exc.name == "_tkinter":
                    print("Tkinter chưa có trong Python này. Xem README mục Tcl/Tk, hoặc chạy --cli.")
                    raise SystemExit(1) from exc
                raise
            run_gui(manager)
    finally:
        repository.close()


if __name__ == "__main__":
    main()
