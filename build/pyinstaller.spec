# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller配置文件 - KOOK消息转发系统后端
"""

import os
import sys
from pathlib import Path

# 项目根目录
root_dir = Path(SPECPATH).parent
backend_dir = root_dir / "backend"
data_dir = root_dir / "backend" / "data"
redis_dir = root_dir / "redis"

# Playwright浏览器路径
import playwright
playwright_browsers = Path(playwright.__file__).parent / "driver" / "package" / ".local-browsers"

block_cipher = None

# 分析Python依赖
a = Analysis(
    [str(backend_dir / 'app' / 'main.py')],
    pathex=[str(backend_dir)],
    binaries=[],
    datas=[
        # 添加数据文件
        (str(data_dir), 'data'),
        # 添加Chromium浏览器
        (str(playwright_browsers), '.local-browsers'),
        # 添加Redis
        (str(redis_dir), 'redis'),
        # 添加选择器配置
        (str(data_dir / 'selectors.yaml'), 'data'),
    ],
    hiddenimports=[
        'playwright',
        'playwright.sync_api',
        'playwright.async_api',
        'aiohttp',
        'fastapi',
        'uvicorn',
        'pydantic',
        'pydantic_settings',
        'redis',
        'aioredis',
        'PIL',
        'PIL.Image',
        'cryptography',
        'bcrypt',
        'orjson',
        'aiofiles',
        'aiosqlite',
        'python-multipart',
        'discord_webhook',
        'python-telegram-bot',
        'lark_oapi',  # 飞书SDK
        'ddddocr',  # OCR识别
        'apscheduler',
        'apscheduler.schedulers.asyncio',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='kook-forwarder-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口（便于调试）
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(root_dir / 'build' / 'icon.ico') if os.name == 'nt' else None,
)
