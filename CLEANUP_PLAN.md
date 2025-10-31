# 代码清理与完善计划

## 审计结果：代码冗余严重

### 重复模块清单（需要合并/删除）

#### 1. smart_mapping系列 (7个文件 → 保留1个)
- ❌ `smart_mapping.py` - 基础版
- ❌ `smart_mapping_v2.py` - V2版本
- ❌ `smart_mapping_api.py` - API版本
- ❌ `smart_mapping_enhanced.py` - 增强版
- ❌ `smart_mapping_advanced.py` - 高级版
- ❌ `smart_mapping_ultimate.py` - 终极版
- ✅ **保留** `smart_mapping_unified.py` - 统一版（最完整）

#### 2. environment系列 (6个文件 → 保留1个)
- ❌ `environment.py` - 基础版
- ❌ `environment_enhanced.py` - 增强版
- ❌ `environment_ultimate.py` - 终极版
- ❌ `environment_autofix.py` - 自动修复基础版
- ❌ `environment_autofix_enhanced.py` - 自动修复增强版
- ✅ **保留** `environment_ultimate_api.py` - 终极API版（功能最全）

#### 3. password_reset系列 (3个文件 → 保留1个)
- ❌ `password_reset.py` - 基础版
- ❌ `password_reset_ultimate.py` - 终极版
- ✅ **保留** `password_reset_enhanced.py` - 增强版（带邮箱验证）

#### 4. server_discovery系列 (3个文件 → 保留1个)
- ❌ `server_discovery.py` - 基础版
- ❌ `server_discovery_enhanced.py` - 增强版
- ✅ **保留** `servers_discovery_ultimate.py` - 终极版（使用真实KOOK API）

#### 5. cookie_import系列 (3个文件 → 保留2个)
- ❌ `cookie_import.py` - 基础版
- ❌ `cookie_import_enhanced.py` - 增强版
- ✅ **保留** `cookie_import_ultimate.py` - 终极版（支持Chrome扩展）
- ✅ **保留** `cookie_websocket.py` - WebSocket实时导入（独立功能）

#### 6. wizard系列 (5个文件 → 保留2个)
- ❌ `wizard_testing.py` - 测试版
- ❌ `wizard_testing_enhanced.py` - 测试增强版
- ❌ `wizard_smart_setup.py` - 智能设置版
- ✅ **保留** `wizard_unified.py` - 统一向导（主向导）
- ✅ **保留** `wizard_first_run.py` - 首次运行检测（独立功能）

#### 7. mapping_learning系列 (4个文件 → 保留2个)
- ❌ `mapping_learning_api.py` - 基础API
- ❌ `mapping_learning_ultimate.py` - 终极版
- ✅ **保留** `mapping_learning_ultimate_api.py` - 终极API版（最完整）
- ✅ **保留** `mapping_learning_feedback.py` - 反馈系统（独立功能）

#### 8. database_optimizer系列 (2个文件 → 保留1个)
- ❌ `database_optimizer_api.py` - 基础版
- ✅ **保留** `database_optimizer_ultimate_api.py` - 终极版

#### 9. websocket系列 (4个文件 → 保留2个)
- ❌ `websocket.py` - 基础版
- ✅ **保留** `websocket_enhanced.py` - 增强版（功能最全）
- ✅ **保留** `websocket_status.py` - 状态推送（独立功能）
- ❌ `system_status_ws.py` - 系统状态（功能重复）

#### 10. captcha系列 (3个文件 → 保留2个)
- ✅ **保留** `captcha_api.py` - 验证码API（基础功能）
- ❌ `captcha_websocket.py` - WebSocket基础版
- ✅ **保留** `captcha_websocket_enhanced.py` - WebSocket增强版

#### 11. 其他重复
- ❌ `update_checker_enhanced.py` - 增强版更新检查（updates.py已足够）
- ❌ `tray_stats_enhanced.py` - 托盘统计增强（system_stats_api.py已有）
- ❌ `health_check.py` - 健康检查（health.py已有）
- ❌ `audit.py` - 审计（audit_logs.py已有）
- ❌ `video_api.py` - 视频API基础版（video_tutorials.py更完整）

---

## 清理策略

### 阶段1：代码合并（保留最优版本）
**删除文件数**: 27个  
**保留文件数**: 53个（原80个）

### 阶段2：修复所有TODO
1. 实现所有mock数据的真实版本
2. 完成所有标记为TODO的功能
3. 移除所有不必要的debug代码

### 阶段3：统一前端调用
1. 所有前端组件使用统一的`api/index.js`
2. 移除直接的axios调用
3. 修复路由中的缺失组件引用

### 阶段4：功能完善
1. 实现企业微信转发模块
2. 实现钉钉转发模块
3. 完善插件系统（翻译、关键词回复）
4. 修复VueFlow流程图视图

---

## 执行顺序

1. ✅ **立即执行**: 删除冗余文件
2. ✅ **立即执行**: 更新main.py的import语句
3. ✅ **立即执行**: 更新前端API调用
4. → **后续执行**: 功能完善与测试

---

## 风险评估

**风险**: 低  
**原因**: 保留的都是最完整版本，删除的是过时版本  
**建议**: 先备份，再执行删除
