/**
 * WebSocket智能连接管理器
 * 特性：
 * - 指数退避重连策略
 * - 心跳检测
 * - 自动重连（最多10次）
 * - 事件监听机制
 */

class WebSocketManager {
  constructor(url) {
    this.url = url
    this.ws = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 10
    this.reconnectDelay = 1000  // 初始1秒
    this.maxReconnectDelay = 30000  // 最大30秒
    this.heartbeatInterval = 30000  // 心跳间隔30秒
    this.heartbeatTimer = null
    this.reconnectTimer = null
    this.listeners = new Map()
    this.isManualClose = false
    this.isConnecting = false
    this.connectionStartTime = null
  }

  /**
   * 连接WebSocket
   */
  connect() {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      console.log('[WebSocket] 已经在连接或已连接')
      return Promise.resolve()
    }

    return new Promise((resolve, reject) => {
      try {
        this.isConnecting = true
        this.connectionStartTime = Date.now()
        
        console.log('[WebSocket] 正在连接...', this.url)
        this.ws = new WebSocket(this.url)
        
        this.ws.onopen = () => {
          const connectTime = Date.now() - this.connectionStartTime
          console.log(`[WebSocket] 连接成功 (耗时${connectTime}ms)`)
          
          this.isConnecting = false
          this.reconnectAttempts = 0
          this.reconnectDelay = 1000
          this.startHeartbeat()
          
          // 触发连接成功事件
          this.emit('connected', { 
            timestamp: Date.now(),
            connectTime: connectTime 
          })
          
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            
            // 处理心跳响应
            if (data.type === 'pong') {
              console.log('[WebSocket] ❤️ 心跳正常')
              return
            }

            // 触发消息事件
            this.emit('message', data)
            
            // 根据消息类型触发特定事件
            if (data.type) {
              this.emit(data.type, data)
            }
          } catch (error) {
            console.error('[WebSocket] 消息解析失败:', error)
            this.emit('parse_error', { error, raw: event.data })
          }
        }

        this.ws.onerror = (error) => {
          console.error('[WebSocket] 连接错误:', error)
          this.isConnecting = false
          this.emit('error', { error, timestamp: Date.now() })
          reject(error)
        }

        this.ws.onclose = (event) => {
          console.log('[WebSocket] 连接关闭:', event.code, event.reason)
          this.isConnecting = false
          this.stopHeartbeat()
          
          this.emit('disconnected', { 
            code: event.code, 
            reason: event.reason,
            timestamp: Date.now()
          })

          // 如果不是手动关闭，则自动重连
          if (!this.isManualClose) {
            this.scheduleReconnect()
          }
        }

        // 连接超时检测（10秒）
        setTimeout(() => {
          if (this.isConnecting) {
            console.error('[WebSocket] 连接超时')
            this.ws?.close()
            this.isConnecting = false
            reject(new Error('连接超时'))
          }
        }, 10000)

      } catch (error) {
        console.error('[WebSocket] 创建失败:', error)
        this.isConnecting = false
        reject(error)
      }
    })
  }

  /**
   * 调度重连
   */
  scheduleReconnect() {
    // 清除之前的重连定时器
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error(`[WebSocket] 达到最大重连次数(${this.maxReconnectAttempts})，停止重连`)
      this.emit('reconnect_failed', { 
        attempts: this.reconnectAttempts,
        timestamp: Date.now()
      })
      return
    }

    this.reconnectAttempts++
    
    // 指数退避算法: delay = min(1000 * 2^attempts, 30000)
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.maxReconnectDelay
    )

    console.log(`[WebSocket] 第${this.reconnectAttempts}次重连，${delay/1000}秒后尝试...`)
    
    this.emit('reconnecting', { 
      attempt: this.reconnectAttempts,
      delay: delay,
      timestamp: Date.now()
    })

    this.reconnectTimer = setTimeout(() => {
      this.reconnect()
    }, delay)
  }

  /**
   * 执行重连
   */
  reconnect() {
    console.log('[WebSocket] 开始重连...')
    
    // 清理旧连接
    if (this.ws) {
      this.ws.onclose = null
      this.ws.onerror = null
      this.ws.onmessage = null
      this.ws.onopen = null
      
      if (this.ws.readyState === WebSocket.OPEN || 
          this.ws.readyState === WebSocket.CONNECTING) {
        this.ws.close()
      }
      
      this.ws = null
    }

    // 重新连接
    this.connect().catch(error => {
      console.error('[WebSocket] 重连失败:', error)
      // 继续下一次重连
      this.scheduleReconnect()
    })
  }

  /**
   * 发送消息
   */
  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = typeof data === 'string' ? data : JSON.stringify(data)
      this.ws.send(message)
      return true
    } else {
      console.warn('[WebSocket] 连接未就绪，无法发送消息')
      return false
    }
  }

  /**
   * 启动心跳
   */
  startHeartbeat() {
    this.stopHeartbeat()
    
    console.log('[WebSocket] 启动心跳检测')
    
    this.heartbeatTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({ 
          type: 'ping', 
          timestamp: Date.now() 
        })
      } else {
        console.warn('[WebSocket] 心跳检测失败：连接未就绪')
        this.stopHeartbeat()
      }
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
   * 关闭连接
   */
  close() {
    console.log('[WebSocket] 手动关闭连接')
    
    this.isManualClose = true
    this.stopHeartbeat()
    
    // 清除重连定时器
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  /**
   * 重新打开连接（取消手动关闭标记）
   */
  reopen() {
    console.log('[WebSocket] 重新打开连接')
    
    this.isManualClose = false
    this.reconnectAttempts = 0
    
    return this.connect()
  }

  /**
   * 监听事件
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
    
    return () => this.off(event, callback)
  }

  /**
   * 取消监听
   */
  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  /**
   * 触发事件
   */
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`[WebSocket] 事件处理器错误 (${event}):`, error)
        }
      })
    }
    
    // 同时触发通配符监听器
    if (this.listeners.has('*')) {
      this.listeners.get('*').forEach(callback => {
        try {
          callback({ event, data })
        } catch (error) {
          console.error('[WebSocket] 通配符处理器错误:', error)
        }
      })
    }
  }

  /**
   * 获取连接状态
   */
  getState() {
    if (!this.ws) return 'CLOSED'
    
    const states = ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED']
    return states[this.ws.readyState] || 'UNKNOWN'
  }

  /**
   * 获取统计信息
   */
  getStats() {
    return {
      state: this.getState(),
      reconnectAttempts: this.reconnectAttempts,
      isManualClose: this.isManualClose,
      hasHeartbeat: !!this.heartbeatTimer,
      listenerCount: Array.from(this.listeners.values()).reduce((sum, arr) => sum + arr.length, 0)
    }
  }
}

// 创建全局WebSocket管理器实例
const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/ws/status`
export const wsManager = new WebSocketManager(wsUrl)

// 自动连接
wsManager.connect().catch(error => {
  console.error('[WebSocket] 初始连接失败:', error)
  // 会自动触发重连机制
})

// 调试：在开发环境打印所有WebSocket事件
if (process.env.NODE_ENV === 'development') {
  wsManager.on('*', ({ event, data }) => {
    console.log(`[WebSocket Event] ${event}:`, data)
  })
}

export default wsManager
