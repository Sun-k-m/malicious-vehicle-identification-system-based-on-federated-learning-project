# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[('C:\\\\Users\\\\19528\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python311\\\\python311.dll', '.')],
    datas=[('images', 'images'), ('saved_models', 'saved_models'), ('sounds', 'sounds')],
    hiddenimports=['sklearn.ensemble', 'sklearn.tree', 'sklearn.neighbors', 'sklearn.svm', 'sklearn.neural_network', 'sklearn.preprocessing', 'sklearn.impute', 'sklearn.compose', 'sklearn.pipeline', 'pandas', 'ttkbootstrap', 'PIL', 'pygame'],
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
    name='基于联邦学习的恶意车辆识别系统',
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
