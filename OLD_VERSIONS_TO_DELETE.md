# 需要删除的旧版本安装包清单

## 📋 问题识别

检查发现以下Release和安装包有问题，需要删除：

---

## 🗑️ 需要删除的Release

### 1. v18.0.0-win (Latest)
**创建时间**: 2025-10-31T13:33:01Z  
**状态**: Published  
**问题**: 
- 文件名格式错误（KOOK.而不是KOOK-Forwarder）
- 与主Release v18.0.0重复
- 版本号显示错误（18.0.0而不是v18.0.0）

**包含的资产**:
- `checksums.txt`
- `KOOK.-18.0.0-arm64.dmg`
- `KOOK.-18.0.0.AppImage`
- `KOOK.Setup.18.0.0.exe`

**删除原因**: 
- 文件名格式不规范
- 应该使用统一的命名规范（KOOK-Forwarder-v18.0.0-*）
- 与主Release v18.0.0冲突

---

### 2. v18.0.0-win (Draft)
**创建时间**: 2025-10-31T13:29:38Z  
**状态**: Draft (草稿)  
**问题**: 
- 草稿状态，未正式发布
- 与已发布的v18.0.0-win重复

**删除原因**: 
- 草稿Release应该被清理
- 避免混淆

---

### 3. v18.0.0-update
**创建时间**: 2025-10-31T15:36:54Z  
**状态**: Latest  
**问题**: 
- 这是一个临时的更新标签
- 不应该作为独立Release存在
- 所有内容应该合并到主Release v18.0.0

**删除原因**: 
- 仅用于触发CI/CD
- 不是正式发布版本
- 避免版本混淆

---

## ✅ 需要保留的Release

### v18.0.0 (主Release)
**标题**: KOOK消息转发系统 v18.0.0 - 重大更新  
**创建时间**: 2025-10-31T12:20:35Z  
**状态**: Published  

**包含的资产** (全部保留):
- ✅ `KOOK-Forwarder-v18.0.0-Linux.tar.gz` (274MB) - 最新Linux包
- ✅ `KOOK-Forwarder-v18.0.0-Linux.tar.gz.md5`
- ✅ `KOOK-Forwarder-v18.0.0-Linux.tar.gz.sha256`
- ✅ `KOOK-Forwarder-v18.0.0-Windows.zip` (111MB) - Windows包
- ✅ `KOOK-Forwarder-v18.0.0-Windows.zip.md5`
- ✅ `KOOK-Forwarder-v18.0.0-Windows.zip.sha256`

**保留原因**:
- 正式发布的主版本
- 文件命名规范统一
- 包含完整的校验和
- 包含最新的代码修复

---

## 📊 删除统计

| Release | 状态 | 资产数量 | 操作 |
|---------|------|----------|------|
| v18.0.0-win (Latest) | Published | 4个文件 | 🗑️ 删除整个Release |
| v18.0.0-win (Draft) | Draft | 未知 | 🗑️ 删除整个Release |
| v18.0.0-update | Latest | 0个文件 | 🗑️ 删除整个Release |
| **v18.0.0** | **Published** | **6个文件** | **✅ 保留** |

---

## 🎯 删除策略

### 方式1: 删除整个Release (推荐)
```bash
gh release delete v18.0.0-win --yes
gh release delete v18.0.0-update --yes

# 删除对应的Git标签
git push --delete origin v18.0.0-win
git push --delete origin v18.0.0-update
```

### 方式2: 仅删除资产（保留Release）
```bash
# 如果只想删除v18.0.0-win的资产但保留Release
gh release delete-asset v18.0.0-win checksums.txt --yes
gh release delete-asset v18.0.0-win KOOK.-18.0.0-arm64.dmg --yes
gh release delete-asset v18.0.0-win KOOK.-18.0.0.AppImage --yes
gh release delete-asset v18.0.0-win KOOK.Setup.18.0.0.exe --yes
```

---

## ⚠️ 注意事项

1. **删除前备份**: 虽然这些是有问题的版本，但建议先确认没有用户依赖
2. **Git标签**: 删除Release后，对应的Git标签也应该删除
3. **v18.0.0保护**: 确保不影响主Release v18.0.0
4. **通知用户**: 如果有用户已下载旧版本，建议发布公告

---

## 📝 删除理由总结

### 为什么删除这些Release？

1. **文件命名不规范**
   - `KOOK.` vs `KOOK-Forwarder-v18.0.0-`
   - 缺少版本号前缀`v`

2. **版本混淆**
   - 3个不同的v18.0.0系列Release
   - 用户难以识别正确版本

3. **草稿状态**
   - Draft Release不应该长期保留

4. **临时标签**
   - v18.0.0-update是CI/CD触发标签
   - 不是用户面向的Release

5. **代码质量**
   - 旧版本包含已修复的语法错误
   - 最新版本已经修复所有问题

---

## ✅ 删除后的效果

删除后，用户在Release页面将只看到：
- **v18.0.0** - 唯一的、正确的v18.0.0版本
- 清晰的下载链接
- 统一的文件命名
- 完整的校验和

---

*分析时间: 2025-10-31*
