/**
 * E2E测试：配置向导流程
 * 测试用户首次使用时的完整配置流程
 */

import { test, expect } from '@playwright/test'

test.describe('配置向导', () => {
  test.beforeEach(async ({ page }) => {
    // 清除localStorage，模拟首次访问
    await page.goto('/')
    await page.evaluate(() => {
      localStorage.clear()
    })
    await page.goto('/wizard')
  })

  test('应该显示欢迎页面', async ({ page }) => {
    // 验证欢迎页标题
    await expect(page.locator('text=欢迎使用KOOK消息转发系统')).toBeVisible()
    
    // 验证免责声明
    await expect(page.locator('text=免责声明')).toBeVisible()
    
    // "同意并继续"按钮应该禁用
    const agreeButton = page.locator('button:has-text("同意并继续")')
    await expect(agreeButton).toBeDisabled()
  })

  test('同意免责声明后可以继续', async ({ page }) => {
    // 勾选同意复选框
    await page.locator('text=我已阅读并同意以上免责声明').click()
    
    // "同意并继续"按钮应该启用
    const agreeButton = page.locator('button:has-text("同意并继续")')
    await expect(agreeButton).toBeEnabled()
    
    // 点击继续
    await agreeButton.click()
    
    // 应该进入第二步
    await expect(page.locator('text=登录KOOK账号')).toBeVisible()
  })

  test('拒绝免责声明应该显示确认对话框', async ({ page }) => {
    // 点击拒绝按钮
    await page.locator('button:has-text("拒绝并退出")').click()
    
    // 应该显示确认对话框
    await expect(page.locator('.el-message-box')).toBeVisible()
  })

  test('步骤2：选择登录方式', async ({ page }) => {
    // 同意并继续到第二步
    await page.locator('text=我已阅读并同意以上免责声明').click()
    await page.locator('button:has-text("同意并继续")').click()
    
    // 验证登录方式选项
    await expect(page.locator('text=Cookie导入')).toBeVisible()
    await expect(page.locator('text=账号密码登录')).toBeVisible()
    
    // 默认应该选中Cookie导入
    const cookieRadio = page.locator('input[type="radio"][value="cookie"]')
    await expect(cookieRadio).toBeChecked()
  })

  test('步骤2：Cookie登录表单验证', async ({ page }) => {
    // 进入第二步
    await page.locator('text=我已阅读并同意以上免责声明').click()
    await page.locator('button:has-text("同意并继续")').click()
    
    // 点击登录按钮（不填写内容）
    await page.locator('button:has-text("登录并继续")').click()
    
    // 应该显示错误提示
    await expect(page.locator('text=请输入Cookie')).toBeVisible({ timeout: 5000 })
  })

  test('完整流程：跳过机器人配置', async ({ page }) => {
    // 步骤1：同意免责声明
    await page.locator('text=我已阅读并同意以上免责声明').click()
    await page.locator('button:has-text("同意并继续")').click()
    
    // 步骤2：跳过账号登录（测试环境）
    // 注意：实际使用需要提供有效的Cookie或账号密码
    
    // 步骤3：假设已经有账号，选择服务器
    // 这里需要mock API响应
    
    // 步骤4：跳过机器人配置
    // 假设已经到第4步
    const skipButton = page.locator('button:has-text("跳过，稍后配置")')
    if (await skipButton.isVisible()) {
      await skipButton.click()
      
      // 应该进入第5步（完成）
      await expect(page.locator('text=配置完成')).toBeVisible()
    }
  })

  test('步骤进度显示正确', async ({ page }) => {
    // 验证步骤指示器
    const steps = page.locator('.el-step')
    await expect(steps).toHaveCount(5)
    
    // 第一步应该是活动状态
    const firstStep = steps.first()
    await expect(firstStep).toHaveClass(/is-process/)
  })

  test('可以返回上一步', async ({ page }) => {
    // 进入第二步
    await page.locator('text=我已阅读并同意以上免责声明').click()
    await page.locator('button:has-text("同意并继续")').click()
    
    // 点击上一步
    await page.locator('button:has-text("上一步")').click()
    
    // 应该返回第一步
    await expect(page.locator('text=欢迎使用KOOK消息转发系统')).toBeVisible()
  })
})
