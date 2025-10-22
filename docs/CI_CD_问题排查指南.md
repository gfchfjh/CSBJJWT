# CI/CD 问题排查指南

本文档记录了项目在 CI/CD 过程中遇到的所有问题和解决方案，供开发者参考。

---

## 📋 目录

- [构建历史总结](#构建历史总结)
- [问题1: GitHub Release 不存在](#问题1-github-release-不存在)
- [问题2: GitHub Actions Artifact Actions 弃用](#问题2-github-actions-artifact-actions-弃用)
- [问题3: Python httpx 依赖冲突](#问题3-python-httpx-依赖冲突)
- [问题4: 前端 mappings.js 文件缺失](#问题4-前端-mappingsjs-文件缺失)
- [问题5: package.json 缺少 repository 字段](#问题5-packagejson-缺少-repository-字段)
- [问题6: Playwright libasound2 系统依赖问题](#问题6-playwright-libasound2-系统依赖问题)
- [问题7: Electron Builder 自动发布 403 错误](#问题7-electron-builder-自动发布-403-错误)
- [问题8: Release Job 权限不足](#问题8-release-job-权限不足)
- [问题9: 测试文件导入路径错误](#问题9-测试文件导入路径错误)
- [问题10: encrypt_password 函数缺失](#问题10-encrypt_password-函数缺失)
- [最佳实践](#最佳实践)
- [常用调试命令](#常用调试命令)

---

## 构建历史总结

| 构建次数 | 状态 | 主要问题 | 修复时间 |
|---------|------|---------|---------|
| 第1次 | ❌ 失败 | Tag 不存在，workflow 未触发 | 即时 |
| 第2次 | ❌ 失败 | GitHub Actions artifact actions 弃用 | 5分钟 |
| 第3次 | ❌ 失败 | Python httpx 依赖冲突 | 10分钟 |
| 第4次 | ❌ 失败 | 前端文件缺失、配置不完整 | 20分钟 |
| 第5次 | ⚠️ 部分成功 | Build 成功，Release 失败（Electron 403） | 30分钟 |
| 第6次 | ✅ 成功 | 所有平台构建成功，Release 创建成功 | 15分钟 |

**总计**: 6次构建，5次失败，1次成功，总耗时约2小时。

---

## 问题1: GitHub Release 不存在

### 症状

用户无法从 GitHub 下载安装包，访问 Releases 页面显示为空。

### 原因

- Git tag `v1.13.0` 未创建或未推送
- GitHub Actions workflow 配置为 `on.push.tags: 'v*'`，没有 tag 就不会触发

### 解决方案

```bash
# 创建 annotated tag
git tag -a v1.13.0 -m "Release v1.13.0"

# 推送到远程仓库
git push origin v1.13.0
```

### 预防措施

- 发布新版本时，确保创建并推送 tag
- 可以设置 Git hooks 提醒未推送的 tags
- 在 README 中明确说明发布流程

---

## 问题2: GitHub Actions Artifact Actions 弃用

### 症状

构建失败，错误日志：
```
The `set-output` command is deprecated and will be disabled soon.
Node.js 12 actions are deprecated. Please update actions to use Node.js 16.
```

### 原因

- `actions/upload-artifact@v3` 和 `actions/download-artifact@v3` 已弃用
- GitHub 强制要求使用 v4 版本

### 解决方案

**修改文件**: `.github/workflows/build-and-release.yml`

```yaml
# 修改前
- uses: actions/upload-artifact@v3
- uses: actions/download-artifact@v3

# 修改后
- uses: actions/upload-artifact@v4
- uses: actions/download-artifact@v4
```

### 影响的位置

- `build-windows` job: upload-artifact
- `build-macos` job: upload-artifact
- `build-linux` job: upload-artifact
- `release` job: download-artifact (3处)

### 预防措施

- 定期检查 GitHub Actions 的 deprecation 通知
- 在 workflow 中添加注释标注使用的 action 版本
- 订阅 GitHub Changelog

---

## 问题3: Python httpx 依赖冲突

### 症状

Python 依赖安装失败：
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.
httpx 0.26.0 is incompatible with python-telegram-bot 20.7 which requires httpx~=0.25.2
```

### 原因

- `backend/requirements.txt` 指定 `httpx==0.26.0`
- `python-telegram-bot==20.7` 要求 `httpx~=0.25.2`
- `backend/requirements-dev.txt` 也显式声明了 `httpx==0.26.0`，覆盖了 requirements.txt

### 解决方案

**修改文件 1**: `backend/requirements.txt`
```python
# 修改前
httpx==0.26.0

# 修改后
httpx==0.25.2  # 兼容 python-telegram-bot 20.7
```

**修改文件 2**: `backend/requirements-dev.txt`
```python
# 修改前
httpx==0.26.0
respx==0.20.2

# 修改后
# httpx已在requirements.txt中定义（0.25.2，兼容python-telegram-bot）
respx==0.20.2
```

### 预防措施

- 使用 `pip-compile` 或 `poetry` 管理依赖
- 添加 CI 步骤验证依赖兼容性
- 在 requirements-dev.txt 中使用 `-r requirements.txt` 而不是重复声明

---

## 问题4: 前端 mappings.js 文件缺失

### 症状

前端构建失败：
```
Could not resolve "../store/mappings" from "src/views/Logs.vue"
```

### 原因

- `frontend/src/views/Logs.vue` 导入了 `useMappingsStore`
- 但 `frontend/src/store/mappings.js` 文件不存在
- 可能是开发过程中遗漏提交

### 解决方案

**创建文件**: `frontend/src/store/mappings.js`

```javascript
import { defineStore } from 'pinia'
import api from '../api'

export const useMappingsStore = defineStore('mappings', {
  state: () => ({
    mappings: [],
    loading: false,
    error: null
  }),

  getters: {
    getChannelNameById: (state) => (channelId) => {
      const mapping = state.mappings.find(m => m.kook_channel_id === channelId)
      return mapping ? mapping.kook_channel_name : channelId
    },
    allMappings: (state) => state.mappings,
    hasMappings: (state) => state.mappings.length > 0
  },

  actions: {
    async fetchMappings() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/api/mappings')
        this.mappings = response.data || []
      } catch (error) {
        console.error('获取频道映射失败:', error)
        this.error = error.message
        this.mappings = []
      } finally {
        this.loading = false
      }
    },

    async addMapping(mappingData) {
      try {
        const response = await api.post('/api/mappings', mappingData)
        this.mappings.push(response.data)
        return response.data
      } catch (error) {
        console.error('添加映射失败:', error)
        throw error
      }
    },

    async deleteMapping(mappingId) {
      try {
        await api.delete(`/api/mappings/${mappingId}`)
        this.mappings = this.mappings.filter(m => m.id !== mappingId)
      } catch (error) {
        console.error('删除映射失败:', error)
        throw error
      }
    },

    async updateMapping(mappingId, mappingData) {
      try {
        const response = await api.put(`/api/mappings/${mappingId}`, mappingData)
        const index = this.mappings.findIndex(m => m.id === mappingId)
        if (index !== -1) {
          this.mappings[index] = response.data
        }
        return response.data
      } catch (error) {
        console.error('更新映射失败:', error)
        throw error
      }
    },

    clearMappings() {
      this.mappings = []
      this.error = null
    }
  }
})
```

### 预防措施

- 使用 `.gitignore` 检查，避免遗漏关键文件
- 本地构建验证后再推送
- 添加 pre-commit hook 检查文件完整性

---

## 问题5: package.json 缺少 repository 字段

### 症状

Electron Builder 报错：
```
Cannot detect repository by .git/config. Please specify "repository" in the package.json
```

### 原因

Electron Builder 需要 `repository` 字段来生成安装包的元数据和更新检查。

### 解决方案

**修改文件**: `frontend/package.json`

```json
{
  "name": "kook-forwarder-frontend",
  "version": "1.13.0",
  "author": "KOOK Forwarder Team",
  "license": "MIT",
  
  // 添加 repository 字段
  "repository": {
    "type": "git",
    "url": "https://github.com/gfchfjh/CSBJJWT.git"
  },
  
  "dependencies": {
    // ...
  }
}
```

### 预防措施

- 使用 `npm init` 时完整填写信息
- 参考 Electron Builder 官方文档的最小配置要求
- 添加 lint 规则检查必需字段

---

## 问题6: Playwright libasound2 系统依赖问题

### 症状

Ubuntu 24.04 上 Playwright 安装失败：
```
The following packages have unmet dependencies:
 libasound2:amd64 : Depends: libasound2-data (>= 1.2.11)
E: Unable to correct problems, you have held broken packages.
```

### 原因

- `playwright install chromium --with-deps` 尝试安装 `libasound2`
- Ubuntu 24.04 将 `libasound2` 重命名为 `libasound2t64`
- 包管理器无法找到 `libasound2`

### 解决方案

**修改文件**: `.github/workflows/build-and-release.yml`

```yaml
# 修改前（test 和 build-linux jobs）
- name: Install Python dependencies
  run: |
    cd backend
    pip install -r requirements.txt
    playwright install chromium --with-deps  # ❌ 会尝试安装系统依赖

# 修改后
- name: Install Python dependencies
  run: |
    cd backend
    pip install -r requirements.txt
    playwright install chromium  # ✅ 只安装浏览器，不安装系统依赖
```

**原因**: GitHub Actions runners 已预装所有必需的系统依赖，无需使用 `--with-deps`。

### 预防措施

- 在 CI/CD 环境中避免使用 `--with-deps`
- 本地开发使用 `--with-deps`，CI 使用 `playwright install`
- 使用 Docker 容器统一环境

---

## 问题7: Electron Builder 自动发布 403 错误

### 症状

Windows 和 macOS 构建失败，日志显示：
```
⚠️ GitHub release failed with status: 403
Unable to publish artifacts
```

### 原因

- Electron Builder 默认会尝试发布到 GitHub Releases
- 检测到环境变量 `GH_TOKEN`，自动触发发布
- 但此时 Release 还未创建（由后续的 `release` job 创建）
- 导致权限冲突

### 解决方案

**修改文件**: `frontend/package.json`

```json
{
  "build": {
    "appId": "com.kookforwarder.app",
    "productName": "KOOK消息转发系统",
    
    // 添加这一行，明确禁用自动发布
    "publish": null,
    
    "directories": {
      "output": "dist-electron"
    },
    // ...
  }
}
```

### 架构说明

项目采用**两阶段发布架构**：

```
阶段1: Build Jobs (并行)
  ├─ build-windows → 生成 .exe → 上传到 Artifacts
  ├─ build-macos   → 生成 .dmg → 上传到 Artifacts
  └─ build-linux   → 生成 .AppImage → 上传到 Artifacts

阶段2: Release Job (统一发布)
  └─ release → 下载所有 Artifacts → 创建 GitHub Release → 上传安装包
```

**为什么需要禁用 Electron 自动发布**:
- Build jobs 只负责构建，不应该发布
- Release job 负责统一发布，避免重复和冲突
- 符合关注点分离原则

### 替代方案

如果需要 Electron Builder 直接发布，需要：
1. 移除 `release` job
2. 给每个 build job 添加 `permissions: contents: write`
3. 配置 `"publish": { "provider": "github" }`

但**不推荐**，因为：
- 3个 jobs 会尝试创建3个 Release（冲突）
- 无法生成统一的 Release Notes
- 违反最小权限原则

### 预防措施

- 在 CI/CD 环境中明确设置 `publish: null`
- 本地构建使用 `electron-builder --publish never`
- 参考 Electron Builder 官方文档的 CI/CD 最佳实践

---

## 问题8: Release Job 权限不足

### 症状

Release job 创建 Release 失败：
```
⚠️ GitHub release failed with status: 403
Too many retries. Aborting...
```

### 原因

- `softprops/action-gh-release@v1` 需要 `contents: write` 权限
- workflow 中没有为 `release` job 设置权限
- `GITHUB_TOKEN` 默认只有读权限

### 解决方案

**修改文件**: `.github/workflows/build-and-release.yml`

```yaml
release:
  needs: [build-windows, build-macos, build-linux]
  runs-on: ubuntu-latest
  if: startsWith(github.ref, 'refs/tags/')
  
  # 添加权限配置
  permissions:
    contents: write
  
  steps:
    - name: Create Release
      uses: softprops/action-gh-release@v1
      # ...
```

### GitHub Actions 权限模型

| 权限级别 | 说明 | 允许的操作 |
|---------|------|-----------|
| `read` | 只读（默认） | 读取代码、下载 artifacts |
| `write` | 读写 | 创建 Release、推送代码、创建 tag |
| `admin` | 管理员 | 修改仓库设置 |

### 最小权限原则

```yaml
# ✅ 好的实践：只给需要的权限
build-windows:
  # 不需要权限，使用默认的 read

release:
  permissions:
    contents: write  # 只给 release job 写权限

# ❌ 坏的实践：给所有 jobs 写权限
permissions:
  contents: write  # 全局权限，过度授权
```

### 预防措施

- 遵循最小权限原则，只给必需的 jobs 写权限
- 在 workflow 顶部注释说明权限需求
- 定期 review 权限配置

---

## 问题9: 测试文件导入路径错误

### 症状

测试失败：
```
ModuleNotFoundError: No module named 'backend'
ImportError: cannot import name 'encrypt_password' from 'app.utils.crypto'
```

### 原因

测试文件使用了错误的导入路径：
```python
# ❌ 错误
from backend.app.database import Database
from backend.app.processors.image import ImageProcessor
from backend.app.utils.scheduler import TaskScheduler
```

正确的导入路径应该是：
```python
# ✅ 正确
from app.database import Database
from app.processors.image import ImageProcessor
from app.utils.scheduler import TaskScheduler
```

### 解决方案

**修改文件**: 
- `backend/tests/test_database.py`
- `backend/tests/test_image_processor.py`
- `backend/tests/test_scheduler.py`

```python
# 修改前
from backend.app.database import Database

# 修改后
from app.database import Database
```

### Python 导入路径说明

项目结构：
```
backend/
  ├── app/
  │   ├── __init__.py
  │   ├── database.py
  │   └── utils/
  │       └── crypto.py
  └── tests/
      └── test_database.py
```

pytest 运行时：
- 工作目录: `backend/`
- Python 路径包含: `backend/`
- 所以应该使用: `from app.database import Database`
- 而不是: `from backend.app.database import Database`

### 预防措施

- 使用相对导入或从项目根目录导入
- 配置 `pytest.ini` 明确 Python 路径
- 添加 import linter 检查

---

## 问题10: encrypt_password 函数缺失

### 症状

导入失败：
```python
from app.utils.crypto import encrypt_password
ImportError: cannot import name 'encrypt_password' from 'app.utils.crypto'
```

### 原因

- `app/api/password_reset.py` 尝试导入 `encrypt_password`
- 但 `app/utils/crypto.py` 中只有 `hash_password`，没有 `encrypt_password`
- 缺少密码加密（encryption）和解密（decryption）函数

**注意**: `hash_password` 和 `encrypt_password` 的区别
- `hash_password`: 单向哈希，不可逆，用于验证密码
- `encrypt_password`: 双向加密，可解密，用于安全存储可恢复的密码

### 解决方案

**修改文件**: `backend/app/utils/crypto.py`

```python
# 在文件末尾添加

def encrypt_password(password: str) -> str:
    """
    加密密码（快捷函数）
    用于安全存储密码
    
    Args:
        password: 原始密码
        
    Returns:
        加密后的密码
    """
    return crypto_manager.encrypt(password)


def decrypt_password(encrypted_password: str) -> str:
    """
    解密密码（快捷函数）
    
    Args:
        encrypted_password: 加密后的密码
        
    Returns:
        原始密码
    """
    return crypto_manager.decrypt(encrypted_password)
```

### 函数用途说明

| 函数 | 用途 | 可逆性 | 使用场景 |
|------|-----|--------|---------|
| `hash_password` | 密码哈希 | 不可逆 | 用户登录验证 |
| `verify_password` | 验证哈希 | - | 验证用户密码 |
| `encrypt_password` | 密码加密 | 可逆 | 存储 KOOK/Discord 密码 |
| `decrypt_password` | 密码解密 | - | 恢复 KOOK/Discord 密码 |

### 预防措施

- 导出的函数应该在文件顶部或末尾明确列出
- 使用 `__all__` 明确导出列表
- 添加单元测试覆盖所有导出函数

---

## 最佳实践

### 1. 依赖管理

```python
# requirements.txt - 只列出直接依赖
fastapi==0.104.1
python-telegram-bot==20.7
httpx==0.25.2  # 明确版本，避免冲突

# requirements-dev.txt - 使用 -r 继承
-r requirements.txt
pytest==7.4.3
pytest-cov==4.1.0
# 不重复声明已在 requirements.txt 中的包
```

### 2. GitHub Actions Workflow

```yaml
name: Build and Release

on:
  push:
    tags: ['v*']
  workflow_dispatch:  # 允许手动触发

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      # 使用缓存加速构建
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: 'frontend/package-lock.json'
      
      # 使用最新版本的 actions
      - uses: actions/upload-artifact@v4
      
      # ...

  release:
    needs: [build-windows, build-macos, build-linux]
    runs-on: ubuntu-latest
    
    # 只给需要的 job 写权限
    permissions:
      contents: write
    
    steps:
      - uses: softprops/action-gh-release@v1
        # ...
```

### 3. Electron Builder 配置

```json
{
  "build": {
    "appId": "com.example.app",
    "productName": "My App",
    
    // 在 CI/CD 中禁用自动发布
    "publish": null,
    
    // 必需的元数据
    "repository": {
      "type": "git",
      "url": "https://github.com/user/repo.git"
    },
    
    // 平台配置
    "win": { "target": "nsis" },
    "mac": { "target": "dmg" },
    "linux": { "target": "AppImage" }
  }
}
```

### 4. Python 导入规范

```python
# ✅ 推荐：从项目根导入
from app.database import Database
from app.utils.crypto import encrypt_password

# ❌ 避免：使用包名导入
from backend.app.database import Database

# ✅ 推荐：相对导入（同一包内）
from .database import Database
from ..utils.crypto import encrypt_password
```

### 5. 发布流程

```bash
# 1. 更新版本号
# - frontend/package.json
# - README.md

# 2. 提交更改
git add .
git commit -m "chore: bump version to v1.14.0"
git push origin main

# 3. 创建并推送 tag（触发 CI/CD）
git tag -a v1.14.0 -m "Release v1.14.0

Features:
- 新功能1
- 新功能2

Bug Fixes:
- 修复问题1
"
git push origin v1.14.0

# 4. 监控构建状态
# https://github.com/user/repo/actions

# 5. 验证 Release
# https://github.com/user/repo/releases/tag/v1.14.0
```

---

## 常用调试命令

### 本地测试构建

```bash
# 测试前端构建
cd frontend
npm install
npm run build
npm run electron:build:win  # Windows
npm run electron:build:mac  # macOS
npm run electron:build:linux  # Linux

# 测试后端构建
cd backend
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --onefile --name kook-forwarder-backend app/main.py

# 运行测试
cd backend
pytest tests/ -v
```

### GitHub CLI 调试

```bash
# 查看最近的 workflow 运行
gh run list --limit 5

# 查看特定运行的详细信息
gh run view <run-id>

# 查看失败的日志
gh run view <run-id> --log-failed

# 重新运行失败的 jobs
gh run rerun <run-id> --failed

# 查看 Release
gh release list
gh release view v1.13.0
```

### 依赖检查

```bash
# 检查依赖冲突
pip install pip-tools
pip-compile --resolver=backtracking requirements.txt

# 检查 npm 依赖
cd frontend
npm audit
npm outdated

# 检查 Python 导入
cd backend
python -c "from app.utils.crypto import encrypt_password; print('OK')"
```

### Playwright 调试

```bash
# 安装 Playwright
pip install playwright

# 安装浏览器（本地开发）
playwright install chromium --with-deps

# 安装浏览器（CI 环境）
playwright install chromium

# 验证安装
playwright --version
python -c "from playwright.sync_api import sync_playwright; print('OK')"
```

---

## 总结

### 核心教训

1. **完整的 CI/CD 测试**: 项目第一次完整的 CI/CD 发布，暴露了大量隐藏问题
2. **依赖管理的重要性**: Python 和 npm 依赖冲突可能导致难以调试的错误
3. **权限最小化原则**: GitHub Actions 权限应该遵循最小权限原则
4. **两阶段发布架构**: 构建和发布分离，避免权限和逻辑冲突
5. **环境差异**: Ubuntu 24.04 系统依赖变化需要及时适配

### 改进建议

- ✅ 添加依赖缓存，加快构建速度（已完成）
- ✅ 修复测试导入路径（已完成）
- ✅ 完善 README 发布流程说明（已完成）
- ✅ 创建问题排查文档（本文档）
- 🔄 考虑使用 Docker 统一构建环境
- 🔄 添加 pre-commit hooks 防止常见错误
- 🔄 建立自动化的依赖更新检查

---

## 参考资料

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Electron Builder 文档](https://www.electron.build/)
- [Playwright 文档](https://playwright.dev/)
- [Python packaging 最佳实践](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)

---

**文档版本**: v1.0  
**最后更新**: 2025-10-22  
**维护者**: KOOK Forwarder Team
