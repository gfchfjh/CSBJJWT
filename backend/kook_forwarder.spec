# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app/api', 'app/api'),
        ('app/core', 'app/core'),
        ('app/processors', 'app/processors'),
        ('app/forwarders', 'app/forwarders'),
        ('app/plugins', 'app/plugins'),
        ('app/queue', 'app/queue'),
        ('app/utils', 'app/utils'),
        ('app/middleware', 'app/middleware'),
        ('app/kook', 'app/kook'),
        ('app/webhooks', 'app/webhooks'),
        ('app/scheduler', 'app/scheduler'),
        ('app/search', 'app/search'),
        ('app/analytics', 'app/analytics'),
    ],
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'pydantic',
        'sqlalchemy',
        'redis',
        'playwright',
        'cryptography',
        'aiohttp',
        'websockets',
        'apscheduler',
        'babel.numbers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='KOOKForwarder',
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
    name='KOOKForwarder',
)
