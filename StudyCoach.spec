# -*- mode: python ; coding: utf-8 -*-
import os

# Include assets if present; build succeeds even if missing
_datas = []
for _f in ('certiv-icon.png', 'certiv-icon.ico'):
    _p = os.path.join('assets', _f)
    if os.path.isfile(_p):
        _datas.append((_p, 'assets'))

a = Analysis(
    ['StudyCoach.py'],
    pathex=[],
    binaries=[],
    datas=_datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='studycoachapp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
