# 🧹 临时文件清理说明

**目的**: 清理构建过程中产生的临时文件  
**状态**: 可选执行

---

## 📦 可以清理的临时文件

### 1. 构建产物 (本地)

这些文件已上传到GitHub Release，本地可以删除：

```bash
# Windows构建下载目录
rm -rf windows-build/

# Linux构建产物（已上传）
rm -rf frontend/dist-electron/

# 前端构建产物
rm -rf frontend/dist/

# Node.js依赖（约500MB）
rm -rf frontend/node_modules/
rm -f frontend/package-lock.json
```

**节省空间**: 约700-800 MB

### 2. Python缓存文件

```bash
# __pycache__ 目录
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# .pyc 文件
find . -type f -name "*.pyc" -delete
```

**节省空间**: 约5-10 MB

---

## ✅ 保留的重要文件

### 不要删除

- ✅ 所有 `.md` 文档
- ✅ 所有 `.sh` 脚本
- ✅ 源代码文件
- ✅ 配置文件
- ✅ workflow文件

---

## 🔧 清理脚本

### 方式1: 手动选择清理

```bash
# 查看各目录大小
du -sh frontend/node_modules/ 2>/dev/null
du -sh frontend/dist/ 2>/dev/null
du -sh frontend/dist-electron/ 2>/dev/null
du -sh windows-build/ 2>/dev/null

# 根据需要删除
rm -rf frontend/node_modules/  # 如果不需要前端开发
rm -rf frontend/dist/          # 前端构建产物
rm -rf windows-build/          # Windows构建下载
```

### 方式2: 一键清理所有临时文件

```bash
#!/bin/bash
# cleanup_all.sh

echo "清理临时文件..."

# 构建产物
rm -rf windows-build/
rm -rf frontend/dist-electron/
rm -rf frontend/dist/
rm -rf frontend/node_modules/
rm -f frontend/package-lock.json

# Python缓存
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

echo "✅ 清理完成！"
du -sh . | awk '{print "当前项目大小:", $1}'
```

### 方式3: Git清理

```bash
# 使用git clean清理未跟踪的文件（谨慎使用）
git clean -xdf frontend/dist/
git clean -xdf frontend/dist-electron/
git clean -xdf windows-build/
```

---

## ⚠️ 注意事项

### 1. node_modules

- 如果需要前端开发，保留 `frontend/node_modules/`
- 如果只是使用，可以删除（节省500MB+）
- 下次需要时运行 `npm install` 即可恢复

### 2. dist目录

- `frontend/dist/` - 前端构建产物，可删除
- `frontend/dist-electron/` - Electron构建产物，可删除
- 需要时重新运行构建即可

### 3. windows-build

- 从GitHub Actions下载的artifact
- 已上传到Release，本地可删除

---

## 📊 空间统计

### 当前项目大小

```bash
du -sh /workspace
# 约 1.5-2 GB（包含所有临时文件）
```

### 清理后

```bash
# 删除所有临时文件后
约 50-100 MB（仅源代码和文档）
```

---

## ✅ 推荐操作

### 保持清洁的项目目录

**推荐清理**:
```bash
# 只清理构建产物，保留依赖
rm -rf windows-build/
rm -rf frontend/dist-electron/
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
```

**完全清理**（如果不需要本地开发）:
```bash
# 清理所有临时文件
rm -rf windows-build/
rm -rf frontend/dist-electron/
rm -rf frontend/dist/
rm -rf frontend/node_modules/
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
```

---

## 🎯 总结

### 可删除的文件类型

- ✅ 构建产物 (dist/, dist-electron/)
- ✅ Node.js依赖 (node_modules/)
- ✅ Python缓存 (__pycache__/, *.pyc)
- ✅ 下载的artifacts (windows-build/)

### 必须保留的文件

- ✅ 源代码 (*.py, *.vue, *.js)
- ✅ 配置文件 (*.json, *.yml, *.yaml)
- ✅ 文档文件 (*.md)
- ✅ 脚本文件 (*.sh, *.bat)

---

**💡 建议**: 如果不需要本地开发，可以删除所有临时文件节省空间。所有重要文件都已提交到GitHub。
