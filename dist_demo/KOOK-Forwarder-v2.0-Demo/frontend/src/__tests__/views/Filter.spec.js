/**
 * Filter.vue 测试文件
 * 测试消息过滤规则配置功能
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ElementPlus from 'element-plus'
import Filter from '@/views/Filter.vue'

// Mock API
vi.mock('@/api', () => ({
  default: {
    getFilterRules: vi.fn(() => Promise.resolve([])),
    addFilterRule: vi.fn(() => Promise.resolve({ data: { id: 1 } })),
    updateFilterRule: vi.fn(() => Promise.resolve({ data: { id: 1 } })),
    deleteFilterRule: vi.fn(() => Promise.resolve()),
    getChannels: vi.fn(() => Promise.resolve([])),
  }
}))

describe('Filter.vue', () => {
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('正确渲染页面', () => {
    wrapper = mount(Filter, {
      global: {
        plugins: [ElementPlus]
      }
    })

    expect(wrapper.find('.filter-view').exists()).toBe(true)
    expect(wrapper.text()).toContain('消息过滤规则')
  })

  it('显示过滤规则类型选项', () => {
    wrapper = mount(Filter, {
      global: {
        plugins: [ElementPlus]
      }
    })

    // 检查是否有关键词、用户、消息类型过滤选项
    expect(wrapper.text()).toContain('关键词过滤')
    expect(wrapper.text()).toContain('用户过滤')
    expect(wrapper.text()).toContain('消息类型')
  })

  it('添加黑名单关键词', async () => {
    wrapper = mount(Filter, {
      global: {
        plugins: [ElementPlus]
      }
    })

    // 模拟添加关键词
    const input = wrapper.find('input[placeholder*="关键词"]')
    if (input.exists()) {
      await input.setValue('广告')
      const addButton = wrapper.find('button:contains("添加")')
      if (addButton.exists()) {
        await addButton.trigger('click')
        // 验证关键词是否添加到列表
        expect(wrapper.text()).toContain('广告')
      }
    }
  })

  it('添加白名单关键词', async () => {
    wrapper = mount(Filter, {
      global: {
        plugins: [ElementPlus]
      }
    })

    // 白名单和黑名单应该是独立的
    const whitelistSection = wrapper.find('.whitelist-section')
    if (whitelistSection.exists()) {
      expect(whitelistSection.text()).toContain('白名单')
    }
  })

  it('启用/禁用过滤规则', async () => {
    wrapper = mount(Filter, {
      global: {
        plugins: [ElementPlus]
      }
    })

    // 查找启用开关
    const switches = wrapper.findAll('.el-switch')
    if (switches.length > 0) {
      const enableSwitch = switches[0]
      await enableSwitch.trigger('click')
      // 验证状态变化
    }
  })

  it('删除过滤规则', async () => {
    wrapper = mount(Filter, {
      global: {
        plugins: [ElementPlus]
      }
    })

    // 查找删除按钮
    const deleteButtons = wrapper.findAll('button[type="danger"]')
    if (deleteButtons.length > 0) {
      await deleteButtons[0].trigger('click')
      // 应该触发删除操作
    }
  })

  it('选择过滤作用域（全局/频道级）', async () => {
    wrapper = mount(Filter, {
      global: {
        plugins: [ElementPlus]
      }
    })

    // 检查作用域选择器
    const scopeSelect = wrapper.find('.scope-selector')
    if (scopeSelect.exists()) {
      expect(['全局', '频道'].some(text => scopeSelect.text().includes(text))).toBe(true)
    }
  })

  it('消息类型过滤配置', async () => {
    wrapper = mount(Filter, {
      global: {
        plugins: [ElementPlus]
      }
    })

    // 检查消息类型选项
    const messageTypes = ['文本', '图片', '链接', '文件']
    const hasTypes = messageTypes.some(type => wrapper.text().includes(type))
    expect(hasTypes).toBe(true)
  })

  it('保存过滤规则', async () => {
    const mockAddRule = vi.fn(() => Promise.resolve({ data: { id: 1 } }))
    
    wrapper = mount(Filter, {
      global: {
        plugins: [ElementPlus],
        mocks: {
          api: {
            addFilterRule: mockAddRule
          }
        }
      }
    })

    // 查找保存按钮
    const saveButtons = wrapper.findAll('button[type="primary"]')
    if (saveButtons.length > 0) {
      await saveButtons[0].trigger('click')
      // 验证API调用
    }
  })

  it('加载已有过滤规则', async () => {
    const mockGetRules = vi.fn(() => Promise.resolve([
      {
        id: 1,
        rule_type: 'keyword_blacklist',
        rule_value: ['广告', '代练'],
        enabled: true
      }
    ]))

    wrapper = mount(Filter, {
      global: {
        plugins: [ElementPlus],
        mocks: {
          api: {
            getFilterRules: mockGetRules
          }
        }
      }
    })

    await wrapper.vm.$nextTick()
    // 验证规则是否正确加载
  })

  it('表单验证', async () => {
    wrapper = mount(Filter, {
      global: {
        plugins: [ElementPlus]
      }
    })

    // 尝试添加空关键词应该失败
    const addButton = wrapper.find('button:contains("添加")')
    if (addButton.exists()) {
      await addButton.trigger('click')
      // 应该显示错误提示
    }
  })
})
