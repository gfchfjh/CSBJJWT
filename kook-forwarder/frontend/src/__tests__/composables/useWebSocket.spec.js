/**
 * useWebSocket composable测试
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useWebSocket } from '@/composables/useWebSocket'

// Mock WebSocket
class MockWebSocket {
  constructor(url) {
    this.url = url
    this.readyState = 0
    this.onopen = null
    this.onmessage = null
    this.onerror = null
    this.onclose = null
    
    setTimeout(() => {
      this.readyState = 1
      if (this.onopen) this.onopen()
    }, 0)
  }

  send(data) {
    // Mock send
  }

  close() {
    this.readyState = 3
    if (this.onclose) this.onclose()
  }
}

global.WebSocket = MockWebSocket

describe('useWebSocket', () => {
  let ws

  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    if (ws && ws.close) {
      ws.close()
    }
    vi.useRealTimers()
  })

  it('创建WebSocket连接', () => {
    const { connect, isConnected } = useWebSocket('ws://localhost:9527/ws/test')
    connect()
    
    vi.runAllTimers()
    
    expect(isConnected.value).toBe(true)
  })

  it('接收消息', async () => {
    const { connect, messages } = useWebSocket('ws://localhost:9527/ws/test')
    const wsInstance = connect()
    
    vi.runAllTimers()
    
    // 模拟接收消息
    const testMessage = { type: 'test', data: 'hello' }
    if (wsInstance.onmessage) {
      wsInstance.onmessage({ data: JSON.stringify(testMessage) })
    }
    
    expect(messages.value).toHaveLength(1)
    expect(messages.value[0]).toEqual(testMessage)
  })

  it('断线自动重连', async () => {
    const { connect, isConnected } = useWebSocket('ws://localhost:9527/ws/test', {
      reconnect: true,
      reconnectInterval: 1000
    })
    
    const wsInstance = connect()
    vi.runAllTimers()
    
    expect(isConnected.value).toBe(true)
    
    // 模拟断线
    if (wsInstance.onclose) {
      wsInstance.onclose()
    }
    
    expect(isConnected.value).toBe(false)
    
    // 等待重连
    vi.advanceTimersByTime(1000)
    vi.runAllTimers()
    
    // 应该已重连
    expect(isConnected.value).toBe(true)
  })

  it('手动关闭连接', () => {
    const { connect, disconnect, isConnected } = useWebSocket('ws://localhost:9527/ws/test')
    connect()
    
    vi.runAllTimers()
    expect(isConnected.value).toBe(true)
    
    disconnect()
    expect(isConnected.value).toBe(false)
  })
})
