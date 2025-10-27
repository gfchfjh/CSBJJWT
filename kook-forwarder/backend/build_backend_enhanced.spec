# -*- mode: python ; coding: utf-8 -*-
"""
增强版PyInstaller配置
完整打包Python后端 + Redis + 所有依赖
版本: v6.0.0
作者: KOOK Forwarder Team
日期: 2025-10-25

使用方法:
    pyinstaller --clean backend/build_backend_enhanced.spec
    
环境变量:
    PACK_PLAYWRIGHT=true  # 是否打包Playwright浏览器（默认false，首次启动下载）
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
from pathlib import Path

# 配置
block_cipher = None
project_root = os.path.abspath(os.path.join(SPECPATH, '..'))

# 是否打包Playwright浏览器（300MB+）
PACK_PLAYWRIGHT = os.environ.get('PACK_PLAYWRIGHT', 'false').lower() == 'true'

# ================== 数据文件收集 ==================
print("=" * 60)
print("开始收集数据文件...")
print("=" * 60)

datas = []

# 1. 打包Redis可执行文件（跨平台）
print("\n[1/5] 收集Redis可执行文件...")
redis_dir = os.path.join(project_root, 'redis')
if os.path.exists(redis_dir):
    if sys.platform == 'win32':
        redis_files = [
            ('redis-server.exe', 'redis'),
            ('redis.conf', 'redis')
        ]
    elif sys.platform == 'darwin':  # macOS
        redis_files = [
            ('redis-server-mac', 'redis'),
            ('redis.conf', 'redis')
        ]
    else:  # Linux
        redis_files = [
            ('redis-server-linux', 'redis'),
            ('redis.conf', 'redis')
        ]
    
    for src_file, dest_dir in redis_files:
        src_path = os.path.join(redis_dir, src_file)
        if os.path.exists(src_path):
            datas.append((src_path, dest_dir))
            print(f"  ✅ 已添加: {src_file}")
        else:
            print(f"  ⚠️  未找到: {src_file}")
else:
    print("  ⚠️  Redis目录不存在，跳过")

# 2. 打包配置文件
print("\n[2/5] 收集配置文件...")
config_files = [
    ('backend/data/selectors.yaml', 'data'),
    ('backend/pytest.ini', '.'),
]

for src, dest in config_files:
    src_path = os.path.join(project_root, src)
    if os.path.exists(src_path):
        datas.append((src_path, dest))
        print(f"  ✅ 已添加: {src}")

# 3. 打包文档
print("\n[3/5] 收集文档文件...")
docs_dir = os.path.join(project_root, 'docs')
if os.path.exists(docs_dir):
    datas.append((docs_dir, 'docs'))
    print(f"  ✅ 已添加: docs目录")

# 4. 打包Playwright浏览器（可选）
print("\n[4/5] 处理Playwright浏览器...")
if PACK_PLAYWRIGHT:
    print("  ⚠️  正在打包Playwright浏览器（约300MB），这将需要较长时间...")
    
    # 查找Playwright缓存目录
    playwright_cache_paths = [
        os.path.join(os.path.expanduser('~'), '.cache', 'ms-playwright'),
        os.path.join(os.path.expanduser('~'), 'Library', 'Caches', 'ms-playwright'),  # macOS
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'ms-playwright'),  # Windows
    ]
    
    playwright_dir = None
    for path in playwright_cache_paths:
        if os.path.exists(path):
            playwright_dir = path
            break
    
    if playwright_dir:
        datas.append((playwright_dir, 'playwright_cache'))
        size_mb = sum(f.stat().st_size for f in Path(playwright_dir).rglob('*') if f.is_file()) / (1024*1024)
        print(f"  ✅ 已添加Playwright浏览器（约{size_mb:.0f}MB）")
    else:
        print("  ❌ 警告：Playwright浏览器未找到！")
        print("     将在首次启动时自动下载（约300MB，需要网络连接）")
else:
    print("  ℹ️  Playwright浏览器将在首次启动时自动下载")
    print("     如需打包浏览器，请设置环境变量: PACK_PLAYWRIGHT=true")

# 5. 打包Python依赖的数据文件
print("\n[5/5] 收集Python包数据文件...")
try:
    # Pillow字体文件
    datas += collect_data_files('PIL')
    print("  ✅ 已添加: PIL数据文件")
except:
    pass

try:
    # Playwright数据文件
    datas += collect_data_files('playwright')
    print("  ✅ 已添加: playwright数据文件")
except:
    pass

print(f"\n数据文件收集完成，共{len(datas)}项")

# ================== 隐藏导入 ==================
print("\n" + "=" * 60)
print("配置隐藏导入...")
print("=" * 60)

hiddenimports = [
    # ===== 核心框架 =====
    'playwright',
    'playwright.async_api',
    'playwright.sync_api',
    '_playwright',
    
    'fastapi',
    'fastapi.responses',
    'fastapi.staticfiles',
    'fastapi.middleware',
    'fastapi.middleware.cors',
    
    'uvicorn',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.websockets.websockets_impl',
    'uvicorn.protocols.websockets.wsproto_impl',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.logging',
    
    # ===== 数据库 =====
    'sqlite3',
    'aiosqlite',
    
    # ===== Redis =====
    'redis',
    'redis.asyncio',
    'redis.asyncio.client',
    'redis.asyncio.connection',
    'redis.commands',
    
    # ===== 图片处理 =====
    'PIL',
    'PIL.Image',
    'PIL.ImageFilter',
    'PIL.ImageEnhance',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    
    # ===== HTTP客户端 =====
    'aiohttp',
    'aiohttp.client',
    'aiohttp.connector',
    'aiohttp.helpers',
    'aiofiles',
    
    # ===== 加密 =====
    'cryptography',
    'cryptography.fernet',
    'cryptography.hazmat',
    'cryptography.hazmat.primitives',
    'cryptography.hazmat.primitives.ciphers',
    'bcrypt',
    
    # ===== 数据验证 =====
    'pydantic',
    'pydantic.fields',
    'pydantic.main',
    'pydantic.types',
    'pydantic_settings',
    
    # ===== 配置文件 =====
    'yaml',
    'toml',
    'dotenv',
    
    # ===== JSON处理 =====
    'orjson',
    'json',
    
    # ===== 转发SDK =====
    'discord_webhook',
    'telegram',
    'telegram.ext',
    'telegram.error',
    'lark_oapi',
    
    # ===== 邮件 =====
    'aiosmtplib',
    'email',
    'email.message',
    'email.mime',
    'email.mime.text',
    'email.mime.multipart',
    'email_validator',
    
    # ===== OCR（可选） =====
    'ddddocr',
    
    # ===== 其他工具 =====
    'bs4',
    'lxml',
    'asyncio',
    'multiprocessing',
    'concurrent.futures',
]

# 自动收集子模块
print("\n自动收集子模块...")
auto_collect = ['fastapi', 'uvicorn', 'pydantic', 'aiohttp']
for module_name in auto_collect:
    try:
        submodules = collect_submodules(module_name)
        hiddenimports.extend(submodules)
        print(f"  ✅ 已收集 {module_name} 的 {len(submodules)} 个子模块")
    except Exception as e:
        print(f"  ⚠️  收集 {module_name} 失败: {str(e)}")

print(f"\n隐藏导入配置完成，共{len(hiddenimports)}项")

# ================== 排除不需要的模块 ==================
excludes = [
    # 大型科学计算库（不需要）
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'sklearn',
    
    # GUI库（不需要）
    'tkinter',
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',
    'wx',
    
    # 开发工具（不需要）
    'IPython',
    'jupyter',
    'notebook',
    'pytest',
    'unittest',
    
    # 其他（不需要）
    'setuptools',
    'pip',
    'wheel',
]

# ================== 分析 ==================
print("\n" + "=" * 60)
print("开始分析依赖...")
print("=" * 60)

a = Analysis(
    [os.path.join(SPECPATH, 'app', 'main.py')],
    pathex=[SPECPATH],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ================== 打包 ==================
print("\n" + "=" * 60)
print("开始打包...")
print("=" * 60)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 配置图标
icon_path = None
if sys.platform == 'win32':
    icon_candidate = os.path.join(project_root, 'build', 'icon.ico')
    if os.path.exists(icon_candidate):
        icon_path = icon_candidate
elif sys.platform == 'darwin':
    icon_candidate = os.path.join(project_root, 'build', 'icon.icns')
    if os.path.exists(icon_candidate):
        icon_path = icon_candidate
else:
    icon_candidate = os.path.join(project_root, 'build', 'icon.png')
    if os.path.exists(icon_candidate):
        icon_path = icon_candidate

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
    upx=True,  # 启用UPX压缩
    upx_exclude=[
        # 排除大文件不压缩（UPX可能导致问题）
        'libcrypto*',
        'libssl*',
        'Qt*',
        '*.dll' if sys.platform == 'win32' else '*.so*',
    ],
    runtime_tmpdir=None,
    console=False,  # 生产环境：不显示控制台
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
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
        upx_exclude=[
            'libcrypto*',
            'libssl*',
        ],
        name='KookForwarder-Backend',
    )

print("\n" + "=" * 60)
print("✅ PyInstaller配置完成！")
print("=" * 60)
print("\n输出文件:")
if sys.platform == 'win32':
    print(f"  - dist/KookForwarder-Backend.exe")
else:
    print(f"  - dist/KookForwarder-Backend")
print("\n下一步:")
print("  1. 测试可执行文件")
print("  2. 配置electron-builder")
print("  3. 打包完整安装包")
print("=" * 60)
