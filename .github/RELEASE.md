# 发布新版本指南

## 自动发布流程

本项目使用GitHub Actions自动构建和发布。

### 发布步骤

1. **更新版本号和变更日志**
   ```bash
   # 更新 docs/CHANGELOG.md
   # 添加新版本的更新内容
   
   # 更新 frontend/package.json 中的 version
   # 更新 backend/app/config.py 中的 app_version
   ```

2. **提交更改**
   ```bash
   git add .
   git commit -m "chore: 准备发布 v1.2.0"
   git push origin main
   ```

3. **创建Git标签并推送**
   ```bash
   # 创建标签（必须以v开头）
   git tag -a v1.2.0 -m "Release v1.2.0"
   
   # 推送标签到GitHub（这会触发构建）
   git push origin v1.2.0
   ```

4. **等待构建完成**
   - GitHub Actions会自动：
     - ✅ 运行测试
     - ✅ 构建Windows、macOS、Linux三个平台的安装包
     - ✅ 创建GitHub Release
     - ✅ 上传安装包到Release
     - ✅ （可选）构建并推送Docker镜像

5. **检查Release**
   - 访问 `https://github.com/你的用户名/CSBJJWT/releases`
   - 确认新版本已发布
   - 下载并测试安装包

## 手动触发构建

如果需要手动触发构建（不创建Release）：

1. 访问 GitHub Actions 页面
2. 选择 "Build and Release" workflow
3. 点击 "Run workflow"
4. 选择分支并运行

## 版本号规范

使用语义化版本号：`v主版本.次版本.修订版本`

- **主版本号**：重大变更，可能不兼容
- **次版本号**：新功能，向后兼容
- **修订版本**：Bug修复，向后兼容

示例：
- `v1.0.0` - 首个稳定版本
- `v1.1.0` - 添加新功能
- `v1.1.1` - 修复Bug
- `v2.0.0` - 重大更新

## 注意事项

1. **标签格式**：必须以`v`开头，如`v1.0.0`
2. **推送标签**：必须推送标签到GitHub才会触发构建
3. **构建时间**：完整构建约需20-30分钟
4. **失败处理**：如果构建失败，查看Actions日志排查问题

## Docker镜像发布（可选）

如果需要发布Docker镜像，需要先配置：

1. 在Docker Hub创建仓库
2. 在GitHub仓库设置Secrets：
   - `DOCKERHUB_USERNAME`: Docker Hub用户名
   - `DOCKERHUB_TOKEN`: Docker Hub访问令牌

配置完成后，每次发布版本时会自动构建并推送Docker镜像。

## 常见问题

### Q: 构建失败怎么办？
A: 
1. 查看GitHub Actions日志
2. 确认代码能通过测试：`cd backend && pytest`
3. 确认依赖正确：检查requirements.txt和package.json
4. 本地测试构建：`cd build && python build_all_complete.py`

### Q: 如何删除错误的Release？
A:
1. 在GitHub Releases页面删除Release
2. 删除对应的Git标签：
   ```bash
   git tag -d v1.0.0
   git push origin :refs/tags/v1.0.0
   ```

### Q: 如何创建预发布版本？
A:
1. 使用带后缀的标签：`v1.0.0-beta.1`
2. 在Release中勾选"This is a pre-release"

## 构建产物

成功构建后会生成：

- `KookForwarder-{version}-Setup.exe` - Windows安装包（NSIS）
- `KookForwarder-{version}.dmg` - macOS磁盘镜像
- `KookForwarder-{version}.AppImage` - Linux应用镜像
- （可选）Docker镜像：`username/kook-forwarder:latest`

## 发布检查清单

发布前确认：

- [ ] 所有测试通过
- [ ] 更新日志已更新
- [ ] 版本号已更新（package.json, config.py）
- [ ] 文档已更新
- [ ] 本地测试通过
- [ ] 创建并推送标签
- [ ] 等待构建完成
- [ ] 下载并测试安装包
- [ ] 更新README.md中的下载链接

---

**提示**：首次发布时，建议先使用测试标签（如`v0.1.0-test`）验证构建流程。
