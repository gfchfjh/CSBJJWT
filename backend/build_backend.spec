# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller打包配置文件
用于将Python后端打包成单个可执行文件

使用方法：
    pyinstaller backend/build_backend.spec

生成文件：
    dist/KookForwarder（Linux/macOS）
    dist/KookForwarder.exe（Windows）
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 项目根目录
block_cipher = None
project_root = os.path.abspath(os.path.join(SPECPATH, '..'))

# 收集所有需要的数据文件
datas = []

# 1. 添加Redis可执行文件
redis_dir = os.path.join(project_root, 'redis')
if sys.platform == 'win32':
    datas.append((os.path.join(redis_dir, 'redis-server.exe'), 'redis'))
    datas.append((os.path.join(redis_dir, 'redis.conf'), 'redis'))
else:
    datas.append((os.path.join(redis_dir, 'redis-server'), 'redis'))
    datas.append((os.path.join(redis_dir, 'redis.conf'), 'redis'))

# 2. 添加选择器配置文件
selectors_file = os.path.join(project_root, 'backend', 'data', 'selectors.yaml')
if os.path.exists(selectors_file):
    datas.append((selectors_file, 'data'))

# 3. 添加文档文件
docs_dir = os.path.join(project_root, 'docs')
if os.path.exists(docs_dir):
    datas.append((docs_dir, 'docs'))

# 4. 添加Playwright浏览器（可选，如果需要打包浏览器）
# 注意：Playwright浏览器非常大（~300MB），建议运行时下载
# datas += collect_data_files('playwright')

# 收集所有隐藏导入
hiddenimports = [
    # Playwright相关
    'playwright',
    'playwright.async_api',
    'playwright.sync_api',
    
    # FastAPI相关
    'fastapi',
    'uvicorn',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    
    # Redis相关
    'redis',
    'redis.asyncio',
    
    # SQLite相关
    'sqlite3',
    
    # 图片处理相关
    'PIL',
    'PIL.Image',
    'PIL.ImageFilter',
    
    # 其他依赖
    'aiohttp',
    'asyncio',
    'bs4',
    'lxml',
    'cryptography',
    'pydantic',
    'pydantic_settings',
    'yaml',
    'ddddocr',
    'discord_webhook',
    'telegram',
    'lark_oapi',
]

# 分析入口文件
a = Analysis(
    ['backend/app/main.py'],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
        'PyQt5',
        'PySide2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 打包可执行文件
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KookForwarder-Backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 使用UPX压缩（可选）
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口（可改为False隐藏）
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 暂时不使用图标
)

# Linux/macOS: 创建COLLECT（包含所有依赖）
if sys.platform != 'win32':
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='KookForwarder-Backend',
    )
