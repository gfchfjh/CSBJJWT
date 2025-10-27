# E2E测试文档

## 概述

本项目使用Playwright进行端到端（E2E）测试，测试完整的用户交互流程。

## 安装

```bash
# 安装Playwright
npm install -D @playwright/test

# 安装浏览器
npx playwright install
```

## 运行测试

```bash
# 运行所有E2E测试
npm run test:e2e

# UI模式运行（推荐）
npm run test:e2e:ui

# 调试模式
npm run test:e2e:debug

# 查看测试报告
npm run test:e2e:report

# 运行特定测试文件
npx playwright test wizard.spec.js

# 运行特定浏览器
npx playwright test --project=chromium
```

## 测试文件结构

```
e2e/
├── wizard.spec.js      # 配置向导测试
├── mapping.spec.js     # 频道映射测试
├── accounts.spec.js    # 账号管理测试（待添加）
├── bots.spec.js        # 机器人配置测试（待添加）
└── logs.spec.js        # 日志监控测试（待添加）
```

## 编写测试

### 基本结构

```javascript
import { test, expect } from '@playwright/test'

test.describe('功能模块', () => {
  test.beforeEach(async ({ page }) => {
    // 每个测试前的准备工作
    await page.goto('/path')
  })

  test('测试用例描述', async ({ page }) => {
    // 测试步骤
    await page.locator('button').click()
    
    // 断言
    await expect(page.locator('text=成功')).toBeVisible()
  })
})
```

### 最佳实践

1. **使用有意义的测试描述**
   ```javascript
   test('用户应该能够添加新的频道映射', async ({ page }) => {
     // ...
   })
   ```

2. **使用Page Object模式**
   ```javascript
   class WizardPage {
     constructor(page) {
       this.page = page
       this.agreeCheckbox = page.locator('text=我已阅读')
       this.nextButton = page.locator('button:has-text("继续")')
     }

     async agreeAndContinue() {
       await this.agreeCheckbox.click()
       await this.nextButton.click()
     }
   }
   ```

3. **避免硬编码等待时间**
   ```javascript
   // ❌ 不好
   await page.waitForTimeout(5000)
   
   // ✅ 好
   await page.waitForSelector('text=加载完成')
   ```

4. **使用测试数据工厂**
   ```javascript
   function createTestMapping() {
     return {
       kook_server_id: 'test_server',
       kook_channel_id: 'test_channel',
       target_platform: 'discord'
     }
   }
   ```

## Mock API响应

对于E2E测试，建议使用真实的后端API。但在某些情况下，可以mock API响应：

```javascript
test('测试Mock数据', async ({ page }) => {
  await page.route('/api/accounts', route => {
    route.fulfill({
      status: 200,
      body: JSON.stringify([{ id: 1, name: '测试账号' }])
    })
  })
  
  await page.goto('/accounts')
  await expect(page.locator('text=测试账号')).toBeVisible()
})
```

## 截图和视频

Playwright自动为失败的测试生成截图和视频：

- 截图位置：`test-results/*/test-failed-1.png`
- 视频位置：`test-results/*/video.webm`
- HTML报告：`playwright-report/index.html`

## CI/CD集成

在GitHub Actions中运行E2E测试：

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright
        run: npx playwright install --with-deps
      - name: Run E2E tests
        run: npm run test:e2e
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

## 调试技巧

1. **使用Playwright Inspector**
   ```bash
   npx playwright test --debug
   ```

2. **查看测试追踪**
   ```bash
   npx playwright show-trace test-results/traces/trace.zip
   ```

3. **Headed模式运行**
   ```bash
   npx playwright test --headed
   ```

4. **慢速模式**
   ```bash
   npx playwright test --slow-mo=1000
   ```

## 测试覆盖的功能

### ✅ 已完成
- [x] 配置向导基本流程
- [x] 频道映射操作

### 🔄 进行中
- [ ] 账号管理完整流程
- [ ] 机器人配置和测试
- [ ] 日志查询和筛选

### 📋 待添加
- [ ] 过滤规则配置
- [ ] 系统设置修改
- [ ] 导入导出功能
- [ ] WebSocket实时更新

## 参考资源

- [Playwright官方文档](https://playwright.dev/)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Testing Library](https://testing-library.com/)
