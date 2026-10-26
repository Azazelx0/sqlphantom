# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for SQLPhantom.
Packages SQLPhantom desktop GUI and terminal TUI into a standalone binary.
"""

import sys
from pathlib import Path

block_cipher = None

root_dir = Path.cwd()
src_dir = root_dir / "src"
sqlmap_dir = root_dir / "sqlmap"

datas = [
    (str(sqlmap_dir), "sqlmap"),
    (str(root_dir / "assets"), "assets"),
    (str(src_dir / "sqlphantom" / "assets"), "sqlphantom/assets"),
]

hiddenimports = [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "textual",
    "rich",
    "httpx",
    "pydantic",
    "sqlphantom.domain",
    "sqlphantom.application",
    "sqlphantom.engine",
    "sqlphantom.storage",
    "sqlphantom.reporting",
    "sqlphantom.plugins",
    "sqlphantom.gui",
    "sqlphantom.tui",
]

a = Analysis(
    [str(src_dir / "sqlphantom" / "cli.py")],
    pathex=[str(src_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "unittest"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="sqlphantom",
    icon=str(root_dir / "assets" / "logo.ico"),
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="sqlphantom",
)
