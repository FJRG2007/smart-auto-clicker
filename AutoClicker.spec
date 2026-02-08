# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['init.py'],
    pathex=['.'],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=['src', 'src.main', 'src.memory', 'src.memory.manager', 'src.windows', 'src.windows.main_window', 'src.windows.config_window', 'src.clickers', 'src.clickers.simulating_game', 'src.clickers.antidetection_bypass', 'src.clickers.native_input', 'src.utils', 'src.utils.basics', 'src.lib.globals', 'src.driver', 'src.driver.components', 'src.driver.components.switch', 'src.driver.executions', 'src.driver.executions.startup'],
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
    name='AutoClicker',
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
    icon=['assets\\mouse.ico'],
)
