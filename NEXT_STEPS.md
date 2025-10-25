# 📋 下一步行动计划

## 🎯 立即执行（本周）

### 1. 完成 P0 级剩余优化（预计 2 天）

#### P0-8~11: 账号登录优化

**文件创建清单**：
```bash
# 1. 选择器配置文件
touch backend/data/selectors.yaml

# 2. 选择器管理器（已存在，需增强）
# 修改：backend/app/utils/selector_manager.py

# 3. 登录诊断模块
touch backend/app/utils/login_diagnostics.py

# 4. 前端登录诊断组件
touch frontend/src/components/LoginDiagnostics.vue
```

**实施步骤**：

**Step 1**: 创建选择器配置文件（30 分钟）
```yaml
# backend/data/selectors.yaml
login:
  email_input:
    - 'input[type="email"]'
    - 'input[name="email"]'
    - '#email'
  
  password_input:
    - 'input[type="password"]'
    - 'input[name="password"]'
    - '#password'
  
  submit_button:
    - 'button[type="submit"]'
    - 'button.login-btn'
    - '.login-button'
  
  captcha_input:
    - 'input[name="captcha"]'
    - 'input[placeholder*="验证码"]'
  
  captcha_image:
    - 'img.captcha-image'
    - 'img[alt*="验证码"]'
  
  sms_code_input:
    - 'input[name="sms_code"]'
    - 'input[placeholder*="短信验证码"]'
```

**Step 2**: 修改 scraper.py 使用选择器（1 小时）
```python
# backend/app/kook/scraper.py
async def _login_with_password(self, email: str, password: str):
    # 使用配置化选择器
    email_selectors = selector_manager.get_selectors('login.email_input')
    
    for selector in email_selectors:
        try:
            await self.page.fill(selector, email)
            break
        except:
            continue
```

**Step 3**: 添加自动保存 Cookie（30 分钟）
```python
# 登录成功后
if await self._check_login_status():
    # 获取 Cookie
    cookies = await self.context.cookies()
    cookie_json = json.dumps(cookies)
    
    # 保存到数据库
    db.update_account_cookie(self.account_id, cookie_json)
    logger.info("✅ Cookie 已自动保存")
```

**Step 4**: 实现登录诊断（2 小时）
```python
# backend/app/utils/login_diagnostics.py
class LoginDiagnostics:
    async def diagnose(self, page, error_message):
        results = {
            'network': await self._check_network(),
            'credentials': await self._check_credentials(),
            'captcha': await self._check_captcha(),
            'sms': await self._check_sms(),
        }
        
        # 生成诊断报告
        return self._generate_report(results)
```

---

### 2. 集成新功能到主应用（1 天）

#### 更新 main.py 注册新路由
```python
# backend/app/main.py
from .api import environment_enhanced

app.include_router(environment_enhanced.router)
```

#### 更新前端路由
```javascript
// frontend/src/router/index.js
{
  path: '/help',
  name: 'Help',
  component: () => import('@/views/HelpCenter.vue')
}
```

#### 更新向导流程
```vue
<!-- frontend/src/views/Wizard.vue -->
<!-- 添加环境检查步骤 -->
<WizardStepEnvironment
  v-if="currentStep === 0"
  @next="nextStep"
/>

<!-- 添加测试步骤 -->
<WizardStepTest
  v-if="currentStep === 3"
  @next="handleComplete"
/>
```

---

### 3. 测试与验证（1 天）

#### 测试清单
```bash
# 1. 打包脚本测试
python build/prepare_chromium_enhanced.py
python build/prepare_redis_complete.py
python build/build_all_final.py

# 2. 环境检查测试
# 访问 http://localhost:9527/api/environment/check

# 3. 向导流程测试
# 首次启动应用，完整走一遍向导

# 4. Cookie 导入测试
# 测试三种导入方式

# 5. 帮助系统测试
# 访问所有帮助页面
```

---

## 🚀 下周计划（P1 级优化）

### Week 2: 核心功能增强

#### Day 1-2: 频道映射拖拽界面

**安装依赖**：
```bash
cd frontend
npm install vuedraggable@next
```

**创建组件**：
```vue
<!-- frontend/src/components/DraggableMappingList.vue -->
<template>
  <draggable
    v-model="mappings"
    item-key="id"
    @end="handleDragEnd"
  >
    <template #item="{element}">
      <div class="mapping-item">
        {{ element.kook_channel_name }}
        →
        {{ element.target_channel_id }}
      </div>
    </template>
  </draggable>
</template>
```

---

#### Day 3-4: 智能匹配算法优化

**安装依赖**：
```bash
pip install fuzzywuzzy python-Levenshtein
```

**创建同义词词典**：
```python
# backend/app/utils/synonyms.py
SYNONYMS = {
    "公告": ["announcement", "news", "notice", "通知", "announcements"],
    "活动": ["event", "activity", "events"],
    "更新": ["update", "changelog", "updates", "release"],
    "讨论": ["discussion", "chat", "talk", "general"],
    "帮助": ["help", "support", "question", "ask"],
    "技术": ["tech", "technical", "developer", "dev"],
    "闲聊": ["off-topic", "random", "chat"],
}
```

**实现智能匹配**：
```python
from fuzzywuzzy import fuzz
from .synonyms import SYNONYMS

def smart_match(kook_name: str, target_channels: List) -> List:
    results = []
    
    # 1. 精确匹配
    for target in target_channels:
        if kook_name.lower() == target.name.lower():
            results.append({'channel': target, 'score': 100})
    
    # 2. 同义词匹配
    for cn, en_list in SYNONYMS.items():
        if cn in kook_name:
            for target in target_channels:
                if any(en in target.name.lower() for en in en_list):
                    results.append({'channel': target, 'score': 90})
    
    # 3. 模糊匹配
    for target in target_channels:
        score = fuzz.ratio(kook_name, target.name)
        if score >= 60:
            results.append({'channel': target, 'score': score})
    
    return sorted(results, key=lambda x: x['score'], reverse=True)
```

---

#### Day 5: 过滤规则完善

**数据库迁移**：
```sql
-- backend/app/migrations/add_filter_enhancements.sql
ALTER TABLE filter_rules ADD COLUMN list_type TEXT DEFAULT 'blacklist';
ALTER TABLE filter_rules ADD COLUMN priority INTEGER DEFAULT 0;
ALTER TABLE filter_rules ADD COLUMN regex_enabled INTEGER DEFAULT 0;

-- 白名单类型：whitelist
-- 黑名单类型：blacklist
```

**更新过滤器**：
```python
# backend/app/processors/filter.py
class MessageFilter:
    def apply_filters(self, message):
        # 1. 应用白名单（优先级最高）
        if self.has_whitelist():
            if not self.match_whitelist(message):
                return False
        
        # 2. 应用黑名单
        if self.match_blacklist(message):
            return False
        
        # 3. 应用正则表达式规则
        if self.has_regex_rules():
            if not self.match_regex(message):
                return False
        
        return True
```

---

## 📅 后续周计划概览

### Week 3: 稳定性优化
- Redis 跨平台修复
- 异常恢复机制
- 失败消息备份
- 自动重启功能

### Week 4: 性能与安全
- WebSocket 实时通信
- 批量处理优化
- API Token 强制启用
- 审计日志完善

### Week 5-6: 体验优化与测试
- 国际化翻译
- 深色主题完善
- E2E 测试
- 性能测试
- 文档完善

---

## 🛠️ 开发环境准备

### 1. 安装开发工具

```bash
# Python 开发
pip install -r backend/requirements-dev.txt
pip install pytest pytest-cov black flake8

# 前端开发
cd frontend
npm install
npm install -D vitest @vue/test-utils playwright

# 打包工具
pip install pyinstaller
npm install -g electron-builder

# 额外工具
pip install fuzzywuzzy python-Levenshtein  # 智能匹配
pip install watchdog  # 文件监控
```

---

### 2. 配置开发环境

```bash
# 设置环境变量
export DEBUG=True
export API_PORT=9527
export REDIS_PORT=6379

# 创建测试配置
cp backend/.env.example backend/.env

# 启动开发服务器
cd backend
python -m app.main

# 另一个终端启动前端
cd frontend
npm run dev
```

---

### 3. Git 工作流

```bash
# 创建功能分支
git checkout -b feature/p0-login-optimization

# 开发完成后
git add .
git commit -m "feat(P0): 优化账号登录功能

- 添加选择器配置化
- 实现自动保存 Cookie
- 添加登录诊断功能
- 支持手机验证码

Closes #P0-8, #P0-9, #P0-10, #P0-11"

# 推送到远程
git push origin feature/p0-login-optimization
```

---

## 📊 进度追踪

### 使用 Todo 更新进度

```bash
# 完成一项优化后
echo "✅ P0-8: 选择器配置化 - 已完成" >> OPTIMIZATION_PROGRESS.md

# 提交进度更新
git add OPTIMIZATION_PROGRESS.md
git commit -m "docs: 更新优化进度"
```

---

## 🎯 验收标准

### P0 级验收清单
- [ ] 所有环境检查通过率 > 95%
- [ ] 一键安装成功率 > 90%
- [ ] 配置向导完成率 > 80%
- [ ] 帮助文档访问量 > 50/天
- [ ] Cookie 导入成功率 > 85%
- [ ] 账号登录成功率 > 90%

### P1 级验收清单
- [ ] 频道映射准确率 > 70%
- [ ] 拖拽操作流畅（无卡顿）
- [ ] 过滤规则有效率 > 95%
- [ ] 图片转发成功率 > 90%

### P2 级验收清单
- [ ] 页面加载时间 < 2s
- [ ] 消息转发延迟 < 1s
- [ ] 内存占用 < 300MB
- [ ] CPU 占用（空闲）< 2%

---

## 💡 提示

1. **优先级**：始终先完成高优先级（P0）项目
2. **测试驱动**：每完成一项，立即测试验证
3. **文档同步**：代码变更时同步更新文档
4. **代码质量**：使用 black 格式化，flake8 检查
5. **Git 提交**：小步快跑，频繁提交

---

**准备好了吗？让我们开始吧！** 🚀

*下一步：执行 `python build/prepare_chromium_enhanced.py` 测试打包脚本*
