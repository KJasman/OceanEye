# -*- mode: python ; coding: utf-8 -*-

# this file was generated with (no need to rerun):
# pyi-makespec --onedir --additional-hooks-dir=./hooks run.py

# build the executable with:
# python -m PyInstaller run.spec --clean --noconfirm

from distutils.sysconfig import get_python_lib

site_packages = get_python_lib()

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        (
            f"{site_packages}/altair/vegalite/v5/schema/vega-lite-schema.json",
            "./altair/vegalite/v5/schema/"
        ),
        (
            f"{site_packages}/streamlit",
            "./streamlit"
        ),
        (
            f"{site_packages}/",
            "."
        ),
        (
            "./src",
            "./src"
        )
    ],
    hiddenimports=[
        "streamlit",
        "logging.config",
        "ultralytics",
        "torch"
    ],
    hookspath=['./hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OceanEye',
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
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OceanEye',
)
