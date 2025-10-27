/**
 * Vitest测试环境设置
 */
import { vi } from 'vitest'

// Mock Element Plus 自动导入
global.ElMessage = {
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn(),
  info: vi.fn()
}

global.ElMessageBox = {
  confirm: vi.fn(() => Promise.resolve()),
  alert: vi.fn(() => Promise.resolve()),
  prompt: vi.fn(() => Promise.resolve({ value: '' }))
}

global.ElNotification = {
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn(),
  info: vi.fn()
}

// Mock window.electron
global.window.electron = {
  ipcRenderer: {
    send: vi.fn(),
    on: vi.fn(),
    once: vi.fn(),
    removeListener: vi.fn()
  },
  closeWindow: vi.fn(),
  minimizeWindow: vi.fn()
}

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
global.localStorage = localStorageMock
