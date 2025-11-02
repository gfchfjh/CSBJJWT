# -*- mode: python ; c['../backend/app/main.py'],oding: utf-8 -*-
"""
PyInstaller打包配置
✅ P2-2: Python后端打包为可执行文件
"""

block_cipher = None

# 后端主文件
backend_main = Analysis(
    ['../backend/run.py'],
    pathex=['../backend'],
    binaries=[],
    datas=[
        # 包含数据文件
        ('../backend/data', 'data'),
        ('../backend/app/api', 'app/api'),
        ('../backend/app/processors', 'app/processors'),
        ('../backend/app/forwarders', 'app/forwarders'),
        ('../backend/app/utils', 'app/utils'),
        ('../backend/app/kook', 'app/kook'),
        ('../backend/app/queue', 'app/queue'),
        ('../backend/app/plugins', 'app/plugins'),
        ('../backend/app/webhooks', 'app/webhooks'),
        ('../backend/app/scheduler', 'app/scheduler'),
        ('../backend/app/search', 'app/search'),
        ('../backend/app/analytics', 'app/analytics'),
        ('../backend/app/middleware', 'app/middleware'),
        ('../backend/app/core', 'app/core'),
        # Redis可执行文件
        ('../redis', 'redis'),
    ],
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.websockets',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'playwright',
        'playwright._impl',
        'playwright.sync_api',
        'aiohttp',
        'redis',
        'redis.asyncio',
        'pydantic',
        'pydantic_settings',
        'sqlalchemy',
        'apscheduler',
        'yaml',
        'PIL',
        'cryptography',
        'aiosmtplib',
        'psutil',
        'loguru',
        'aiosqlite',
        'httpx',
        'starlette',
        'pydantic_core',
        'email_validator',
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

pyz = PYZ(backend_main.pure, backend_main.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    backend_main.scripts,
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
    icon='../build/icon.ico',
)

coll = COLLECT(
    exe,
    backend_main.binaries,
    backend_main.zipfiles,
    backend_main.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='KOOKForwarder',
)
