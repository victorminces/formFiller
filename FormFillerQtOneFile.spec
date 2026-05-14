# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui_qt.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('field_maps', 'field_maps'),
        ('templates', 'templates'),
        ('assets', 'assets'),
        ('patient_input.example.json', '.'),
    ],
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
    name='FormFillerQt',
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
