# KOOK消息转发系统 - CMD完整操作指南

**生成时间**: 2025-11-10  
**适用系统**: Windows 10/11  
**项目路径**: C:\Users\tanzu\Desktop\CSBJJWT  
**当前版本**: v18.0.4+  

---

## 📋 目录

1. [第一阶段：环境检查](#第一阶段环境检查)
2. [第二阶段：代码同步](#第二阶段代码同步)
3. [第三阶段：启动服务](#第三阶段启动服务)
4. [第四阶段：功能测试](#第四阶段功能测试)
5. [第五阶段：Cookie管理](#第五阶段cookie管理)
6. [第六阶段：数据库检查](#第六阶段数据库检查)
7. [第七阶段：完整测试](#第七阶段完整测试)
8. [常见问题处理](#常见问题处理)

---

## 第一阶段：环境检查

### 步骤1.1: 打开CMD（以管理员身份）

```cmd
Win + X → 选择"Windows Terminal（管理员）"
或
Win + R → 输入 cmd → Ctrl+Shift+Enter
```

### 步骤1.2: 进入项目目录

```cmd
cd C:\Users\tanzu\Desktop\CSBJJWT
```

### 步骤1.3: 检查环境版本

```cmd
REM 检查Python版本（应该是3.12+）
python --version

REM 检查Node版本（应该是18+）
node --version

REM 检查Git版本
git --version

REM 检查虚拟环境是否存在
dir venv
```

**预期输出**:
```
Python 3.12.x
v18.x.x 或更高
git version 2.x.x
venv 目录存在
```

### 步骤1.4: 检查Git状态

```cmd
REM 查看当前分支
git branch

REM 查看工作区状态
git status

REM 查看最近提交
git log --oneline -5
```

---

## 第二阶段：代码同步

### 步骤2.1: 切换到main分支

```cmd
REM 如果当前不在main分支，切换到main
git checkout main
```

### 步骤2.2: 拉取最新代码

```cmd
REM 从远程拉取最新代码
git pull origin main
```

### 步骤2.3: 检查是否有Cookie功能（可选验证）

```cmd
REM 查找Cookie更新API
findstr /s /i "update_cookie" backend\app\api\accounts.py
```

**预期输出**: 应该看到 `async def update_cookie`

---

## 第三阶段：启动服务

### 步骤3.1: 打开第一个CMD窗口（后端）

```cmd
REM 进入项目目录
cd C:\Users\tanzu\Desktop\CSBJJWT

REM 进入backend目录
cd backend

REM 激活虚拟环境
..\venv\Scripts\activate

REM 启动后端服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 9527 --reload
```

**预期输出**:
```
INFO:     日志系统已初始化
INFO:     智能默认配置系统已初始化
INFO:     账号限制器初始化完成
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:9527 (Press CTRL+C to quit)
```

**保持这个窗口运行，不要关闭！**

### 步骤3.2: 打开第二个CMD窗口（前端）

```cmd
REM 打开新的CMD窗口
Win + R → cmd → Enter

REM 进入项目目录
cd C:\Users\tanzu\Desktop\CSBJJWT\frontend

REM 启动前端服务
npm run dev
```

**预期输出**:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: http://192.168.x.x:5173/
➜  press h + enter to show help
```

**保持这个窗口运行，不要关闭！**

### 步骤3.3: 验证服务启动

打开浏览器，访问以下地址：

```
前端界面: http://localhost:5173
后端API: http://localhost:9527
健康检查: http://localhost:9527/health
API文档: http://localhost:9527/docs
```

**预期结果**:
- ✅ 前端显示登录或主界面
- ✅ 后端返回 `{"status": "healthy"}`
- ✅ API文档显示Swagger界面

---

## 第四阶段：功能测试

### 步骤4.1: 测试后端健康检查（第三个CMD窗口）

```cmd
REM 打开第三个CMD窗口用于测试
Win + R → cmd → Enter

REM 测试健康检查API
curl http://localhost:9527/health

REM 测试系统状态API
curl http://localhost:9527/api/system/status

REM 测试账号列表API
curl http://localhost:9527/api/accounts/
```

**预期输出**:
```json
{"status":"healthy"}
{"service_running":false,"redis_connected":true,...}
{"accounts":[]}
```

### 步骤4.2: 在浏览器中测试前端

1. 打开浏览器访问: http://localhost:5173
2. 应该看到系统主界面
3. 点击左侧菜单，测试各个页面是否正常

---

## 第五阶段：Cookie管理

### 步骤5.1: 获取KOOK Cookie

**方法1: 浏览器手动获取**

1. 打开新的浏览器标签
2. 访问: https://www.kookapp.cn
3. 登录您的KOOK账号
4. 按 F12 打开开发者工具
5. 切换到 Console 标签
6. 复制粘贴以下代码并回车:

```javascript
copy(JSON.stringify(document.cookie.split("; ").map(c => {
  let [name, ...v] = c.split("=");
  return {
    name, 
    value: v.join("="), 
    domain: ".kookapp.cn", 
    path: "/", 
    secure: true, 
    sameSite: "None"
  };
})))
```

7. Cookie已自动复制到剪贴板

### 步骤5.2: 添加KOOK账号

在系统前端界面:

1. 点击左侧菜单 "账号管理"
2. 点击 "添加账号" 按钮
3. 填写邮箱地址
4. 粘贴Cookie（Ctrl+V）
5. 点击 "保存"

### 步骤5.3: 使用Cookie更新功能（新功能！）

**功能说明**: 现在系统已经支持Cookie一键更新功能！

在账号管理页面:

1. 找到需要更新Cookie的账号
2. 点击账号右侧的 "更新Cookie" 按钮（黄色）
3. 在弹出的对话框中粘贴新的Cookie
4. 点击 "更新"
5. 看到 "Cookie更新成功" 提示
6. 页面自动刷新

**优势**:
- ✅ 无需删除账号重新添加
- ✅ 保留所有配置和映射
- ✅ 一键更新，方便快捷

### 步骤5.4: 启动账号监听

1. 在账号管理页面
2. 点击账号右侧的 "启动" 按钮（绿色）
3. 等待几秒钟
4. Chrome浏览器会自动打开
5. 账号状态变为 "🟢 在线"

**预期结果**:
- ✅ Chrome窗口打开（无界面模式）
- ✅ 看到 "账号已启动" 提示
- ✅ 账号状态显示在线

---

## 第六阶段：数据库检查

### 步骤6.1: 查找数据库文件

```cmd
REM 打开CMD窗口（可以是测试窗口）

REM 查找数据库文件
dir /s /b C:\Users\tanzu\Documents\KookForwarder\data\*.db

REM 如果上面找不到，尝试搜索整个Documents目录
dir /s /b C:\Users\tanzu\Documents\*.db | findstr /i "kook config"
```

**预期输出**: 应该找到类似 `C:\Users\tanzu\Documents\KookForwarder\data\config.db` 的路径

### 步骤6.2: 检查数据库大小

```cmd
REM 查看数据库文件详细信息
dir C:\Users\tanzu\Documents\KookForwarder\data\config.db
```

**预期输出**: 应该看到文件大小（不为0）

### 步骤6.3: 备份数据库（可选）

```cmd
REM 创建备份目录
mkdir C:\Users\tanzu\Documents\KookForwarder\data\backups

REM 复制数据库文件
copy C:\Users\tanzu\Documents\KookForwarder\data\config.db C:\Users\tanzu\Documents\KookForwarder\data\backups\config_backup_%date:~0,4%%date:~5,2%%date:~8,2%.db

REM 查看备份
dir C:\Users\tanzu\Documents\KookForwarder\data\backups
```

### 步骤6.4: 检查数据库表结构（高级）

如果需要验证数据库表，可以使用Python:

```cmd
REM 激活虚拟环境
cd C:\Users\tanzu\Desktop\CSBJJWT
venv\Scripts\activate

REM 运行Python检查脚本
python -c "import sqlite3; conn = sqlite3.connect(r'C:\Users\tanzu\Documents\KookForwarder\data\config.db'); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"'); tables = cursor.fetchall(); print('数据库中的表:'); [print(f'  - {t[0]}') for t in tables]; conn.close()"
```

**预期输出**:
```
数据库中的表:
  - accounts
  - audit_logs
  - bot_configs
  - channel_mappings
  - failed_messages
  - filter_rules
  - mapping_learning_feedback
  - message_logs
  - plugins
  - sqlite_sequence
  - system_config
```

---

## 第七阶段：完整测试

### 步骤7.1: 配置Bot（以Discord为例）

在系统前端界面:

1. 点击左侧菜单 "Bot配置"
2. 选择 "Discord" 标签
3. 填写以下信息:
   - Bot名称: 我的Discord Bot
   - Webhook URL: https://discord.com/api/webhooks/...
4. 点击 "测试连接" 按钮
5. 看到 "测试成功" 提示
6. 点击 "保存"

### 步骤7.2: 配置频道映射

在系统前端界面:

1. 点击左侧菜单 "频道映射"
2. 点击 "添加映射" 按钮
3. 选择:
   - KOOK服务器
   - KOOK频道
   - 目标平台: Discord
   - 目标Bot
   - 目标频道ID
4. 点击 "保存"

### 步骤7.3: 发送测试消息

1. 在KOOK客户端或网页中，进入配置的频道
2. 发送一条测试消息: "测试消息转发"
3. 等待3-5秒
4. 检查Discord频道是否收到消息

**预期结果**:
- ✅ Discord频道收到消息
- ✅ 系统日志页面显示转发记录
- ✅ 统计数据增加

### 步骤7.4: 查看实时日志

在系统前端界面:

1. 点击左侧菜单 "实时日志"
2. 应该看到消息处理日志
3. 可以使用过滤器筛选日志

### 步骤7.5: 查看统计数据

在系统前端界面:

1. 点击左侧菜单 "首页"
2. 查看统计卡片:
   - 今日转发数
   - 成功率
   - 平均延迟
   - 队列长度
3. 查看实时图表

---

## 常见问题处理

### 问题1: 端口被占用

**现象**:
```
ERROR: [Errno 10048] Address already in use
```

**解决方案**:

```cmd
REM 查找占用端口的进程（9527为例）
netstat -ano | findstr :9527

REM 记下最后一列的PID号，然后结束进程
taskkill /F /PID <PID号>

REM 重新启动服务
```

### 问题2: Chrome浏览器无法启动

**现象**: 点击"启动"按钮后无反应

**解决方案**:

```cmd
REM 强制关闭所有Chrome进程
taskkill /F /IM chrome.exe /T

REM 等待5秒
timeout /t 5

REM 重新点击"启动"按钮
```

### 问题3: 虚拟环境激活失败

**现象**:
```
'venv' 不是内部或外部命令
```

**解决方案**:

```cmd
REM 确保在项目根目录
cd C:\Users\tanzu\Desktop\CSBJJWT

REM 如果虚拟环境不存在，重新创建
python -m venv venv

REM 激活虚拟环境（使用完整路径）
venv\Scripts\activate

REM 重新安装依赖
pip install -r backend\requirements.txt
```

### 问题4: npm install失败

**现象**:
```
npm ERR! ERESOLVE could not resolve
```

**解决方案**:

```cmd
REM 使用legacy-peer-deps参数
cd C:\Users\tanzu\Desktop\CSBJJWT\frontend
npm install --legacy-peer-deps
```

### 问题5: Redis连接失败

**现象**: 后端日志显示Redis连接失败

**解决方案**:

```cmd
REM Redis连接失败不影响核心功能，系统会自动使用内存模式
REM 如果需要手动启动Redis:

cd C:\Users\tanzu\Desktop\CSBJJWT\redis
start redis-server.exe redis.conf
```

### 问题6: 数据库文件找不到

**解决方案**:

```cmd
REM 创建数据目录
mkdir C:\Users\tanzu\Documents\KookForwarder\data

REM 重启后端服务，会自动创建数据库
REM 在后端CMD窗口按 Ctrl+C 停止
REM 然后重新运行:
python -m uvicorn app.main:app --host 0.0.0.0 --port 9527 --reload
```

### 问题7: Cookie过期

**现象**: 账号状态变为离线，浏览器显示登录页

**解决方案**:

```cmd
REM 1. 在KOOK网页重新登录
REM 2. 使用浏览器Console获取新Cookie
REM 3. 在系统中点击"更新Cookie"按钮
REM 4. 粘贴新Cookie
REM 5. 重新启动账号
```

---

## 完整测试清单

使用以下清单确保所有功能正常：

### 后端功能测试

- [ ] 后端服务正常启动
- [ ] 健康检查API响应正常
- [ ] Redis连接正常（或内存模式）
- [ ] 数据库初始化成功
- [ ] 所有API端点响应正常

### 前端功能测试

- [ ] 前端页面正常加载
- [ ] 主题切换功能正常
- [ ] 所有菜单页面可访问
- [ ] 表单提交功能正常

### 账号管理测试

- [ ] 可以添加KOOK账号
- [ ] 可以更新Cookie（新功能）
- [ ] 可以启动账号监听
- [ ] 可以停止账号监听
- [ ] 可以删除账号
- [ ] Chrome浏览器正常启动

### Bot配置测试

- [ ] 可以添加Discord Bot
- [ ] 可以添加Telegram Bot
- [ ] 可以添加飞书Bot
- [ ] 可以测试连接
- [ ] 可以删除Bot

### 映射功能测试

- [ ] 可以添加频道映射
- [ ] 可以查看映射列表
- [ ] 可以编辑映射
- [ ] 可以删除映射
- [ ] 智能映射推荐正常

### 消息转发测试

- [ ] KOOK消息能被监听到
- [ ] 消息能成功转发到目标平台
- [ ] 图片能正常转发
- [ ] 文字格式正确
- [ ] 转发延迟可接受（<2秒）

### 日志和统计测试

- [ ] 实时日志页面显示正常
- [ ] 日志可以过滤
- [ ] 统计数据显示正常
- [ ] 图表显示正常
- [ ] 数据实时更新

---

## 停止服务

### 步骤1: 停止账号监听

在系统前端界面:
1. 进入"账号管理"页面
2. 点击每个在线账号的"停止"按钮
3. 等待账号变为离线状态

### 步骤2: 停止前端服务

在前端CMD窗口:
```cmd
REM 按 Ctrl+C 停止
Ctrl + C

REM 确认停止
Y
```

### 步骤3: 停止后端服务

在后端CMD窗口:
```cmd
REM 按 Ctrl+C 停止
Ctrl + C

REM 等待服务完全停止
```

### 步骤4: 停止Redis（如果手动启动了）

```cmd
REM 查找Redis进程
tasklist | findstr redis

REM 结束Redis进程
taskkill /F /IM redis-server.exe
```

---

## 日常使用流程

### 每天启动

```cmd
REM 窗口1: 启动后端
cd C:\Users\tanzu\Desktop\CSBJJWT\backend
..\venv\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 9527 --reload

REM 窗口2: 启动前端
cd C:\Users\tanzu\Desktop\CSBJJWT\frontend
npm run dev

REM 浏览器: 访问 http://localhost:5173
REM 系统界面: 启动需要的账号
```

### 每天停止

```cmd
REM 1. 前端界面停止所有账号
REM 2. 前端窗口 Ctrl+C
REM 3. 后端窗口 Ctrl+C
```

---

## 维护命令

### 清理日志文件

```cmd
REM 删除旧日志（保留最近7天）
forfiles /p "C:\Users\tanzu\Documents\KookForwarder\data\logs" /s /m *.log /d -7 /c "cmd /c del @path"
```

### 备份配置

```cmd
REM 备份整个data目录
xcopy /E /I /Y C:\Users\tanzu\Documents\KookForwarder\data C:\Users\tanzu\Documents\KookForwarder\backup_%date:~0,4%%date:~5,2%%date:~8,2%
```

### 更新代码

```cmd
cd C:\Users\tanzu\Desktop\CSBJJWT
git pull origin main

REM 更新Python依赖
cd backend
..\venv\Scripts\activate
pip install -r requirements.txt --upgrade

REM 更新Node依赖
cd ..\frontend
npm install --legacy-peer-deps
```

---

## 📞 获取帮助

如果遇到问题:

1. **查看日志**:
   - 后端: CMD窗口中的输出
   - 前端: 浏览器Console (F12)
   - 文件日志: `C:\Users\tanzu\Documents\KookForwarder\data\logs\`

2. **参考文档**:
   - TROUBLESHOOTING_WINDOWS.md - 故障排查
   - README.md - 项目说明
   - docs/tutorials/ - 教程文档

3. **提交Issue**:
   - GitHub: https://github.com/gfchfjh/CSBJJWT/issues

---

## 🎉 完成！

恭喜！您已经完成了KOOK消息转发系统的完整设置和测试。

**系统当前状态**: ✅ 生产就绪，可正常使用

**关键功能**:
- ✅ 账号管理（含Cookie更新）
- ✅ 多平台Bot配置
- ✅ 频道映射管理
- ✅ 实时消息转发
- ✅ 日志和统计

**下一步**:
- 配置更多KOOK账号
- 添加更多转发平台
- 设置过滤规则
- 优化映射配置

---

**文档版本**: 1.0  
**生成时间**: 2025-11-10  
**适用版本**: v18.0.4+
