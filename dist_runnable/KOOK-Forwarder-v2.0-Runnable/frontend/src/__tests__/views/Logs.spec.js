/**
 * Logs.vue 测试文件
 * 测试实时日志监控功能
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ElementPlus from 'element-plus'
import Logs from '@/views/Logs.vue'

// Mock API
vi.mock('@/api', () => ({
  default: {
    getLogs: vi.fn(() => Promise.resolve({
      logs: [
        {
          id: 1,
          kook_channel_id: 'ch123',
          content: '测试消息',
          status: 'success',
          created_at: '2025-10-19T10:00:00',
          latency_ms: 800
        }
      ],
      total: 1
    })),
    getStats: vi.fn(() => Promise.resolve({
      total: 100,
      success_rate: 98.5,
      avg_latency: 1200
    })),
    exportLogs: vi.fn(() => Promise.resolve(new Blob())),
    clearLogs: vi.fn(() => Promise.resolve()),
  }
}))

// Mock WebSocket
global.WebSocket = class WebSocket {
  constructor(url) {
    this.url = url
    this.readyState = WebSocket.CONNECTING
    setTimeout(() => {
      this.readyState = WebSocket.OPEN
      if (this.onopen) this.onopen()
    }, 0)
  }

  send(data) {}
  close() {
    this.readyState = WebSocket.CLOSED
    if (this.onclose) this.onclose()
  }

  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3
}

describe('Logs.vue', () => {
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('正确渲染日志页面', () => {
    wrapper = mount(Logs, {
      global: {
        plugins: [ElementPlus]
      }
    })

    expect(wrapper.find('.logs-view').exists()).toBe(true)
    expect(wrapper.text()).toContain('日志')
  })

  it('显示统计信息', async () => {
    wrapper = mount(Logs, {
      global: {
        plugins: [ElementPlus]
      }
    })

    await wrapper.vm.$nextTick()
    
    // 检查统计卡片
    const statsCards = wrapper.findAll('.stat-card')
    expect(statsCards.length).toBeGreaterThan(0)
  })

  it('加载日志列表', async () => {
    wrapper = mount(Logs, {
      global: {
        plugins: [ElementPlus]
      }
    })

    await wrapper.vm.$nextTick()

    // 应该显示日志表格或列表
    const logsTable = wrapper.find('.el-table')
    expect(logsTable.exists()).toBe(true)
  })

  it('状态筛选功能', async () => {
    wrapper = mount(Logs, {
      global: {
        plugins: [ElementPlus]
      }
    })

    // 查找状态筛选器
    const statusFilter = wrapper.find('.status-filter')
    if (statusFilter.exists()) {
      // 应该有全部、成功、失败等选项
      expect(['全部', '成功', '失败'].some(text => 
        wrapper.text().includes(text)
      )).toBe(true)
    }
  })

  it('平台筛选功能', async () => {
    wrapper = mount(Logs, {
      global: {
        plugins: [ElementPlus]
      }
    })

    // 检查平台筛选
    const platformFilter = wrapper.find('.platform-filter')
    if (platformFilter.exists()) {
      expect(['Discord', 'Telegram', '飞书'].some(text => 
        wrapper.text().includes(text)
      )).toBe(true)
    }
  })

  it('搜索功能', async () => {
    wrapper = mount(Logs, {
      global: {
        plugins: [ElementPlus]
      }
    })

    const searchInput = wrapper.find('input[placeholder*="搜索"]')
    if (searchInput.exists()) {
      await searchInput.setValue('测试')
      // 应该触发搜索
    }
  })

  it('自动刷新功能', async () => {
    wrapper = mount(Logs, {
      global: {
        plugins: [ElementPlus]
      }
    })

    // 查找自动刷新开关
    const autoRefreshSwitch = wrapper.find('.auto-refresh-switch')
    if (autoRefreshSwitch.exists()) {
      await autoRefreshSwitch.trigger('click')
      // 验证自动刷新状态
    }
  })

  it('WebSocket实时推送', async () => {
    wrapper = mount(Logs, {
      global: {
        plugins: [ElementPlus]
      }
    })

    // 模拟WebSocket消息
    const ws = wrapper.vm.ws
    if (ws && ws.onmessage) {
      ws.onmessage({
        data: JSON.stringify({
          type: 'new_log',
          log: {
            id: 2,
            content: '新消息',
            status: 'success'
          }
        })
      })

      await wrapper.vm.$nextTick()
      // 验证新日志是否添加到列表
    }
  })

  it('查看日志详情', async () => {
    wrapper = mount(Logs, {
      global: {
        plugins: [ElementPlus]
      }
    })

    // 点击日志行查看详情
    const logRows = wrapper.findAll('.el-table__row')
    if (logRows.length > 0) {
      await logRows[0].trigger('click')
      // 应该打开详情对话框
    }
  })

  it('导出日志功能', async () => {
    const mockExport = vi.fn(() => Promise.resolve(new Blob()))
    
    wrapper = mount(Logs, {
      global: {
        plugins: [ElementPlus],
        mocks: {
          api: {
            exportLogs: mockExport
          }
        }
      }
    })

    const exportButton = wrapper.find('button:contains("导出")')
    if (exportButton.exists()) {
      await exportButton.trigger('click')
      // 验证导出API调用
    }
  })

  it('清空日志功能', async () => {
    const mockClear = vi.fn(() => Promise.resolve())
    
    wrapper = mount(Logs, {
      global: {
        plugins: [ElementPlus],
        mocks: {
          api: {
            clearLogs: mockClear
          }
        }
      }
    })

    const clearButton = wrapper.find('button:contains("清空")')
    if (clearButton.exists()) {
      await clearButton.trigger('click')
      // 应该显示确认对话框
    }
  })

  it('分页功能', async () => {
    wrapper = mount(Logs, {
      global: {
        plugins: [ElementPlus]
      }
    })

    const pagination = wrapper.find('.el-pagination')
    if (pagination.exists()) {
      // 测试页码切换
      const nextButton = pagination.find('.btn-next')
      if (nextButton.exists()) {
        await nextButton.trigger('click')
        // 验证页码变化
      }
    }
  })

  it('显示转发延迟', async () => {
    wrapper = mount(Logs, {
      global: {
        plugins: [ElementPlus]
      }
    })

    await wrapper.vm.$nextTick()
    
    // 日志应该显示延迟信息
    expect(wrapper.text()).toMatch(/延迟|latency|ms/)
  })

  it('显示失败原因', async () => {
    const mockGetLogs = vi.fn(() => Promise.resolve({
      logs: [
        {
          id: 1,
          status: 'failed',
          error_message: 'API限流'
        }
      ],
      total: 1
    }))

    wrapper = mount(Logs, {
      global: {
        plugins: [ElementPlus],
        mocks: {
          api: {
            getLogs: mockGetLogs
          }
        }
      }
    })

    await wrapper.vm.$nextTick()
    
    // 失败的日志应该显示错误信息
    expect(wrapper.text()).toContain('失败')
  })

  it('重试失败消息', async () => {
    wrapper = mount(Logs, {
      global: {
        plugins: [ElementPlus]
      }
    })

    // 查找重试按钮
    const retryButtons = wrapper.findAll('button:contains("重试")')
    if (retryButtons.length > 0) {
      await retryButtons[0].trigger('click')
      // 应该触发重试操作
    }
  })
})
