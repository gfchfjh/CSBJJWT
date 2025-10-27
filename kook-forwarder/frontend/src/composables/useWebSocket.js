/**
 * WebSocket连接管理 Composable
 * 提供可靠的实时通信
 */
import { ref, onMounted, onUnmounted } from 'vue'
import { useNotification } from './useNotification'

export function useWebSocket(url, options = {}) {
  const { notifyWarning, notifyError } = useNotification()

  const ws = ref(null)
  const isConnected = ref(false)
  const reconnectTimer = ref(null)
  const heartbeatTimer = ref(null)
  const messageHandlers = ref(new Map())
  
  // 配置
  const config = {
    reconnectInterval: options.reconnectInterval || 3000,
    maxReconnectAttempts: options.maxReconnectAttempts || 5,
    heartbeatInterval: options.heartbeatInterval || 30000,
    autoReconnect: options.autoReconnect !== false,
    showNotifications: options.showNotifications !== false,
    debug: options.debug || false
  }

  let reconnectAttempts = 0
  let manualClose = false

  /**
   * 连接WebSocket
   */
  const connect = () => {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      log('WebSocket已连接，跳过重复连接')
      return
    }

    try {
      log(`正在连接WebSocket: ${url}`)
      ws.value = new WebSocket(url)

      ws.value.onopen = handleOpen
      ws.value.onmessage = handleMessage
      ws.value.onerror = handleError
      ws.value.onclose = handleClose
    } catch (error) {
      logError('WebSocket连接失败', error)
      if (config.showNotifications) {
        notifyError('连接失败', error.message)
      }
    }
  }

  /**
   * 断开连接
   */
  const disconnect = () => {
    log('手动断开WebSocket连接')
    manualClose = true
    stopHeartbeat()
    stopReconnect()

    if (ws.value) {
      ws.value.close()
      ws.value = null
    }

    isConnected.value = false
  }

  /**
   * 发送消息
   */
  const send = (data) => {
    if (!isConnected.value) {
      logError('WebSocket未连接，无法发送消息')
      return false
    }

    try {
      const message = typeof data === 'string' ? data : JSON.stringify(data)
      ws.value.send(message)
      log('发送消息:', message)
      return true
    } catch (error) {
      logError('发送消息失败', error)
      return false
    }
  }

  /**
   * 订阅消息类型
   */
  const on = (type, handler) => {
    if (!messageHandlers.value.has(type)) {
      messageHandlers.value.set(type, [])
    }
    messageHandlers.value.get(type).push(handler)
    log(`订阅消息类型: ${type}`)

    // 返回取消订阅函数
    return () => off(type, handler)
  }

  /**
   * 取消订阅
   */
  const off = (type, handler) => {
    if (messageHandlers.value.has(type)) {
      const handlers = messageHandlers.value.get(type)
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
        log(`取消订阅消息类型: ${type}`)
      }
    }
  }

  /**
   * 处理连接打开
   */
  const handleOpen = () => {
    log('WebSocket连接成功')
    isConnected.value = true
    reconnectAttempts = 0

    // 启动心跳
    startHeartbeat()

    // 触发连接成功回调
    if (options.onConnected) {
      options.onConnected()
    }
  }

  /**
   * 处理接收消息
   */
  const handleMessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      log('收到消息:', data)

      // 心跳响应
      if (data.type === 'pong') {
        return
      }

      // 分发消息到订阅者
      const type = data.type || 'message'
      if (messageHandlers.value.has(type)) {
        const handlers = messageHandlers.value.get(type)
        handlers.forEach(handler => {
          try {
            handler(data)
          } catch (error) {
            logError(`消息处理器执行失败 [${type}]`, error)
          }
        })
      }

      // 通用消息处理器
      if (options.onMessage) {
        options.onMessage(data)
      }
    } catch (error) {
      logError('解析消息失败', error)
    }
  }

  /**
   * 处理错误
   */
  const handleError = (error) => {
    logError('WebSocket错误', error)

    if (config.showNotifications && reconnectAttempts === 0) {
      notifyError('连接错误', 'WebSocket连接出现错误')
    }

    if (options.onError) {
      options.onError(error)
    }
  }

  /**
   * 处理连接关闭
   */
  const handleClose = (event) => {
    log(`WebSocket连接关闭: code=${event.code}, reason=${event.reason}`)
    isConnected.value = false
    stopHeartbeat()

    if (options.onDisconnected) {
      options.onDisconnected(event)
    }

    // 自动重连
    if (config.autoReconnect && !manualClose) {
      reconnect()
    }
  }

  /**
   * 重新连接
   */
  const reconnect = () => {
    if (reconnectAttempts >= config.maxReconnectAttempts) {
      logError(`达到最大重连次数(${config.maxReconnectAttempts})，停止重连`)
      
      if (config.showNotifications) {
        notifyError(
          '连接失败',
          `无法连接到服务器，已重试${config.maxReconnectAttempts}次`
        )
      }
      return
    }

    reconnectAttempts++
    log(`准备第${reconnectAttempts}次重连（${config.reconnectInterval}ms后）`)

    if (config.showNotifications && reconnectAttempts === 1) {
      notifyWarning('连接断开', '正在尝试重新连接...')
    }

    reconnectTimer.value = setTimeout(() => {
      log(`执行第${reconnectAttempts}次重连`)
      connect()
    }, config.reconnectInterval)
  }

  /**
   * 停止重连
   */
  const stopReconnect = () => {
    if (reconnectTimer.value) {
      clearTimeout(reconnectTimer.value)
      reconnectTimer.value = null
    }
  }

  /**
   * 启动心跳
   */
  const startHeartbeat = () => {
    stopHeartbeat()

    heartbeatTimer.value = setInterval(() => {
      if (isConnected.value) {
        send({ type: 'ping' })
        log('发送心跳')
      }
    }, config.heartbeatInterval)
  }

  /**
   * 停止心跳
   */
  const stopHeartbeat = () => {
    if (heartbeatTimer.value) {
      clearInterval(heartbeatTimer.value)
      heartbeatTimer.value = null
    }
  }

  /**
   * 日志输出
   */
  const log = (...args) => {
    if (config.debug) {
      console.log('[WebSocket]', ...args)
    }
  }

  const logError = (...args) => {
    console.error('[WebSocket]', ...args)
  }

  /**
   * 生命周期钩子
   */
  onMounted(() => {
    if (options.autoConnect !== false) {
      connect()
    }
  })

  onUnmounted(() => {
    disconnect()
  })

  return {
    // 状态
    isConnected,
    ws,

    // 方法
    connect,
    disconnect,
    send,
    on,
    off,
    reconnect
  }
}
