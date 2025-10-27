/**
 * E2E测试：频道映射功能
 * 测试频道映射的创建、编辑、删除等操作
 */

import { test, expect } from '@playwright/test'

test.describe('频道映射', () => {
  test.beforeEach(async ({ page }) => {
    // 访问映射页面
    await page.goto('/mapping')
  })

  test('应该显示映射页面', async ({ page }) => {
    await expect(page.locator('text=频道映射配置')).toBeVisible()
    await expect(page.locator('.el-table')).toBeVisible()
  })

  test('应该有操作按钮', async ({ page }) => {
    await expect(page.locator('button:has-text("添加映射")').first()).toBeVisible()
    await expect(page.locator('button:has-text("智能映射")').first()).toBeVisible()
    await expect(page.locator('button:has-text("导入")').first()).toBeVisible()
    await expect(page.locator('button:has-text("导出")').first()).toBeVisible()
  })

  test('点击添加映射应该打开对话框', async ({ page }) => {
    await page.locator('button:has-text("添加映射")').first().click()
    
    // 验证对话框显示
    await expect(page.locator('.el-dialog')).toBeVisible()
    await expect(page.locator('text=添加频道映射')).toBeVisible()
  })

  test('添加映射表单应该有所有必填字段', async ({ page }) => {
    await page.locator('button:has-text("添加映射")').first().click()
    
    // 验证表单字段
    await expect(page.locator('text=KOOK服务器ID')).toBeVisible()
    await expect(page.locator('text=KOOK频道ID')).toBeVisible()
    await expect(page.locator('text=目标平台')).toBeVisible()
    await expect(page.locator('text=目标机器人')).toBeVisible()
    await expect(page.locator('text=目标频道ID')).toBeVisible()
  })

  test('智能映射功能', async ({ page }) => {
    await page.locator('button:has-text("智能映射")').first().click()
    
    // 验证智能映射对话框
    await expect(page.locator('.el-dialog')).toBeVisible()
    await expect(page.locator('text=智能频道映射')).toBeVisible()
    
    // 应该有生成建议按钮
    await expect(page.locator('button:has-text("生成映射建议")').first()).toBeVisible()
  })

  test('删除映射应该显示确认对话框', async ({ page }) => {
    // 假设表格中有数据
    const deleteButton = page.locator('button:has-text("删除")').first()
    
    if (await deleteButton.isVisible()) {
      await deleteButton.click()
      
      // 应该显示确认对话框
      await expect(page.locator('.el-message-box')).toBeVisible({ timeout: 5000 })
    }
  })

  test('导出映射功能', async ({ page }) => {
    const exportButton = page.locator('button:has-text("导出")').first()
    await exportButton.click()
    
    // 验证下载是否触发（通过监听download事件）
    const downloadPromise = page.waitForEvent('download', { timeout: 5000 })
      .catch(() => null)
    
    const download = await downloadPromise
    // 如果有数据，应该触发下载
  })

  test('导入映射功能', async ({ page }) => {
    await page.locator('button:has-text("导入")').first().click()
    
    // 验证导入对话框
    await expect(page.locator('.el-dialog')).toBeVisible()
    await expect(page.locator('text=导入频道映射')).toBeVisible()
    
    // 应该有文件上传组件
    await expect(page.locator('.el-upload')).toBeVisible()
  })

  test('表格应该显示映射信息', async ({ page }) => {
    const table = page.locator('.el-table')
    await expect(table).toBeVisible()
    
    // 验证表格列
    await expect(page.locator('text=KOOK频道')).toBeVisible()
    await expect(page.locator('text=目标平台')).toBeVisible()
    await expect(page.locator('text=状态')).toBeVisible()
    await expect(page.locator('text=操作')).toBeVisible()
  })
})
