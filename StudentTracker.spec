# -*- mode: python ; coding: utf-8 -*-
"""Gói cửa sổ onedir. Trên macOS, BUNDLE tạo StudentTracker.app."""

import sys

a = Analysis(
    ["student_tracker/__main__.py"],
    pathex=["."],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name="StudentTracker",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="StudentTracker",
)
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="StudentTracker.app",
        icon=None,
        bundle_identifier="com.teky.studenttracker",
    )
