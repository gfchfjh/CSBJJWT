import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright E2E测试配置
 * 用于测试完整的用户流程和界面交互
 */
export default defineConfig({
  // 测试目录
  testDir: './e2e',
  
  // 完全并行运行测试
  fullyParallel: true,
  
  // 在CI上失败时重试
  retries: process.env.CI ? 2 : 0,
  
  // 并发worker数量
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter配置
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'playwright-report/results.json' }],
    ['list']
  ],
  
  // 共享设置
  use: {
    // Base URL
    baseURL: 'http://localhost:5173',
    
    // 收集失败测试的trace
    trace: 'on-first-retry',
    
    // 截图设置
    screenshot: 'only-on-failure',
    
    // 视频设置
    video: 'retain-on-failure',
    
    // 浏览器上下文选项
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,
    
    // 等待超时
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  // 测试项目配置
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    // 移动端测试
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // 开发服务器配置
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
})
