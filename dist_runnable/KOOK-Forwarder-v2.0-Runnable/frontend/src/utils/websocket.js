/**
 * WebSocket客户端
 * 用于实时通信：验证码处理、系统状态推送、日志推送
 */

class WebSocketClient {
  constructor(url, channel = 'system') {
    this.url = url
    this.channel = channel
    this.ws = null
    this.listeners = new Map()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectInterval = 3000
    this.heartbeatInterval = 30000
    this.heartbeatTimer = null
  }

  /**
   * 连接WebSocket
   */
  connect() {
    try {
      this.ws = new WebSocket(this.url)

      this.ws.onopen = () => {
        console.log(`WebSocket连接成功: ${this.channel}`)
        this.reconnectAttempts = 0
        this.startHeartbeat()
        this.emit('connected')
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.handleMessage(data)
        } catch (error) {
          console.error('解析WebSocket消息失败:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket错误:', error)
        this.emit('error', error)
      }

      this.ws.onclose = () => {
        console.log(`WebSocket连接关闭: ${this.channel}`)
        this.stopHeartbeat()
        this.emit('disconnected')
        this.reconnect()
      }
    } catch (error) {
      console.error('WebSocket连接失败:', error)
      this.reconnect()
    }
  }

  /**
   * 处理接收到的消息
   */
  handleMessage(data) {
    const { type, ...payload } = data

    if (type === 'pong') {
      // 心跳响应
      return
    }

    // 触发对应类型的监听器
    this.emit(type, payload)
  }

  /**
   * 发送消息
   */
  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket未连接，无法发送消息')
    }
  }

  /**
   * 开始心跳
   */
  startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      this.send({ type: 'ping' })
    }, this.heartbeatInterval)
  }

  /**
   * 停止心跳
   */
  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  /**
   * 重新连接
   */
  reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('WebSocket重连次数已达上限')
      this.emit('reconnect_failed')
      return
    }

    this.reconnectAttempts++
    console.log(`WebSocket重连中... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

    setTimeout(() => {
      this.connect()
    }, this.reconnectInterval)
  }

  /**
   * 注册事件监听器
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  /**
   * 移除事件监听器
   */
  off(event, callback) {
    if (!this.listeners.has(event)) {
      return
    }

    const listeners = this.listeners.get(event)
    const index = listeners.indexOf(callback)
    if (index !== -1) {
      listeners.splice(index, 1)
    }
  }

  /**
   * 触发事件
   */
  emit(event, data) {
    if (!this.listeners.has(event)) {
      return
    }

    const listeners = this.listeners.get(event)
    listeners.forEach(callback => {
      try {
        callback(data)
      } catch (error) {
        console.error(`事件处理器错误 (${event}):`, error)
      }
    })
  }

  /**
   * 断开连接
   */
  disconnect() {
    this.stopHeartbeat()
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

// 创建WebSocket管理器
class WebSocketManager {
  constructor() {
    this.clients = {}
    this.baseUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:9527'
  }

  /**
   * 获取或创建WebSocket客户端
   */
  getClient(channel) {
    if (!this.clients[channel]) {
      const url = `${this.baseUrl}/ws/${channel}`
      this.clients[channel] = new WebSocketClient(url, channel)
      this.clients[channel].connect()
    }
    return this.clients[channel]
  }

  /**
   * 关闭指定频道的WebSocket
   */
  closeClient(channel) {
    if (this.clients[channel]) {
      this.clients[channel].disconnect()
      delete this.clients[channel]
    }
  }

  /**
   * 关闭所有WebSocket
   */
  closeAll() {
    Object.keys(this.clients).forEach(channel => {
      this.closeClient(channel)
    })
  }
}

// 导出全局实例
export const wsManager = new WebSocketManager()

// 便捷函数
export const getSystemWS = () => wsManager.getClient('system')
export const getCaptchaWS = () => wsManager.getClient('captcha')
export const getLogsWS = () => wsManager.getClient('logs')

export default wsManager
