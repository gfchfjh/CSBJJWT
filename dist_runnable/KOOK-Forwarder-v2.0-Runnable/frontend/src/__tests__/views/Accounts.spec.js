/**
 * Accounts页面测试
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Accounts from '@/views/Accounts.vue'

// Mock API
vi.mock('@/api', () => ({
  default: {
    getAccounts: vi.fn(() => Promise.resolve([
      {
        id: 1,
        email: 'test@example.com',
        status: 'online',
        last_active: '2025-10-18T12:00:00',
        created_at: '2025-10-18T10:00:00'
      }
    ])),
    addAccount: vi.fn(() => Promise.resolve({ id: 2 })),
    deleteAccount: vi.fn(() => Promise.resolve()),
    updateAccountStatus: vi.fn(() => Promise.resolve())
  }
}))

describe('Accounts.vue', () => {
  let wrapper
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    wrapper = mount(Accounts, {
      global: {
        plugins: [pinia],
        stubs: {
          'el-card': true,
          'el-table': true,
          'el-table-column': true,
          'el-button': true,
          'el-dialog': true,
          'el-form': true,
          'el-form-item': true,
          'el-input': true,
          'el-radio-group': true,
          'el-radio': true,
          'el-tag': true
        }
      }
    })
  })

  it('组件正确挂载', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('初始化时加载账号列表', async () => {
    await flushPromises()
    expect(wrapper.vm.accounts).toHaveLength(1)
    expect(wrapper.vm.accounts[0].email).toBe('test@example.com')
  })

  it('打开添加账号对话框', async () => {
    await wrapper.vm.openAddDialog()
    expect(wrapper.vm.addDialogVisible).toBe(true)
    expect(wrapper.vm.accountForm.email).toBe('')
  })

  it('添加账号成功', async () => {
    wrapper.vm.accountForm = {
      email: 'new@example.com',
      cookie: '[]'
    }
    wrapper.vm.loginType = 'cookie'

    await wrapper.vm.addAccount()
    await flushPromises()

    expect(wrapper.vm.addDialogVisible).toBe(false)
    expect(wrapper.vm.accounts.length).toBeGreaterThan(0)
  })

  it('删除账号需要确认', async () => {
    global.ElMessageBox.confirm = vi.fn(() => Promise.resolve())
    
    await wrapper.vm.deleteAccount({ id: 1, email: 'test@example.com' })
    
    expect(global.ElMessageBox.confirm).toHaveBeenCalled()
  })

  it('显示账号状态标签', () => {
    expect(wrapper.vm.accounts[0].status).toBe('online')
  })
})
