# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pet.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/pet', 'assets/pet')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'PySide6.Qt3DCore', 'PySide6.QtMultimedia', 'PySide6.QtCharts', 'PySide6.QtDataVisualization', 'PySide6.QtPdf', 'PySide6.QtSql', 'PySide6.QtTest', 'PySide6.QtOpenGL', 'PySide6.QtOpenGLWidgets', 'scipy', 'numpy', 'PIL'],
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
    name='大肥鱼',
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
    icon=['assets/icon.ico'],
)
