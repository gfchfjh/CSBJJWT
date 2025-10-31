# 版本号修复说明

## 问题
之前构建的 Windows 安装包版本号显示为 v16.0.0，而非 v18.0.0。

## 原因
- `frontend/package.json` 中的 version 字段仍为 "16.0.0"
- electron-builder 使用 package.json 中的 version 生成安装包文件名
- 导致生成的文件名为 `KOOK.Setup.16.0.0.exe`

## 修复措施
1. ✅ 更新 `frontend/package.json` version 为 "18.0.0"
2. ✅ 更新 `/workspace/VERSION` 为 "v18.0.0"
3. ✅ 提交更改 (commit 5d0f2d7)
4. ✅ 重新创建标签 v18.0.0-win
5. ⏳ 触发新的 GitHub Actions 构建

## 预期结果
新构建将生成正确的文件名：
- `KOOK消息转发系统 Setup 18.0.0.exe`
- `KOOK-Forwarder-v18.0.0-Windows.zip`

## 构建监控
查看最新构建: https://github.com/gfchfjh/CSBJJWT/actions/workflows/build-windows.yml

预计时间: 3-4分钟
