# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Transcriber.
Includes the launcher `transcriber_gui.py` and the `locales/` folder as data.

Usage (on Windows):
  pyinstaller --clean --noconfirm transcriber.spec

This spec collects all files from the `locales/` folder and bundles them into the
final application. It is tuned for a one-file build (PyInstaller `--onefile` can
also be used from the command line). Adjust `icon` or other options as needed.
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None
project_root = Path(__file__).parent

# Collect locale files (flat list of tuples (source, destdir))
datas = []
for p in project_root.joinpath('locales').rglob('*'):
    if p.is_file():
        # destination directory inside the bundle: 'locales'
        datas.append((str(p), 'locales'))

# Analysis
a = Analysis([
    'transcriber_gui.py'
],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    name='Transcriber',
    debug=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='Transcriber'
)

