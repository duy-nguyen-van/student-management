"""Đường dẫn file SQLite khi chạy nguồn và khi đóng gói."""

import sys
from pathlib import Path


def data_dir() -> Path:
    if getattr(sys, "frozen", False):
        executable = Path(sys.executable).resolve()
        macos_dir = executable.parent
        if macos_dir.name == "MacOS" and macos_dir.parent.name == "Contents":
            directory = Path.home() / "Library" / "Application Support" / "StudentTracker"
            directory.mkdir(parents=True, exist_ok=True)
            return directory
        return macos_dir
    return Path.cwd()


def database_path() -> Path:
    return data_dir() / "students.db"
