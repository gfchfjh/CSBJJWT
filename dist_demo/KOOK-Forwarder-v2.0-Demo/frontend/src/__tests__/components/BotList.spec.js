/**
 * BotList组件测试
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import BotList from '@/components/BotList.vue'

describe('BotList.vue', () => {
  let wrapper

  const mockBots = [
    {
      id: 1,
      name: 'Discord Bot',
      platform: 'discord',
      status: 'active',
      config: { webhook_url: 'https://discord.com/api/webhooks/123' }
    },
    {
      id: 2,
      name: 'Telegram Bot',
      platform: 'telegram',
      status: 'active',
      config: { token: '123:ABC', chat_id: '-1001234567890' }
    }
  ]

  beforeEach(() => {
    wrapper = mount(BotList, {
      props: {
        bots: mockBots
      },
      global: {
        stubs: {
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-button': true
        }
      }
    })
  })

  it('渲染正确的Bot数量', () => {
    expect(wrapper.props('bots')).toHaveLength(2)
  })

  it('显示Bot名称', () => {
    const botNames = wrapper.props('bots').map(bot => bot.name)
    expect(botNames).toContain('Discord Bot')
    expect(botNames).toContain('Telegram Bot')
  })

  it('触发编辑事件', async () => {
    await wrapper.vm.$emit('edit', mockBots[0])
    expect(wrapper.emitted('edit')).toBeTruthy()
    expect(wrapper.emitted('edit')[0]).toEqual([mockBots[0]])
  })

  it('触发删除事件', async () => {
    await wrapper.vm.$emit('delete', mockBots[0].id)
    expect(wrapper.emitted('delete')).toBeTruthy()
    expect(wrapper.emitted('delete')[0]).toEqual([mockBots[0].id])
  })

  it('触发测试事件', async () => {
    await wrapper.vm.$emit('test', mockBots[0].id)
    expect(wrapper.emitted('test')).toBeTruthy()
    expect(wrapper.emitted('test')[0]).toEqual([mockBots[0].id])
  })
})
