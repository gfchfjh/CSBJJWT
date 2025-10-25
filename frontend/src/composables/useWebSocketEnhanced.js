/**
 * WebSocket 增强版 Composable
 * P2-5: WebSocket 替代轮询
 * 
 * 功能：
 * - 自动重连
 * - 心跳保持
 * - 频道订阅
 * - 错误处理
 */
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

export function useWebSocketEnhanced(url) {
  const ws = ref(null)
  const connected = ref(false)
  const reconnecting = ref(false)
  const reconnectCount = ref(0)
  const maxReconnectAttempts = 5
  
  // 事件处理器
  const handlers = {
    log: [],
    status: [],
    notification: [],
  }
  
  // 连接 WebSocket
  const connect = () => {
    if (ws.value) {
      return
    }
    
    try {
      ws.value = new WebSocket(url)
      
      ws.value.onopen = () => {
        connected.value = true
        reconnecting.value = false
        reconnectCount.value = 0
        console.log('✅ WebSocket 已连接')
        
        // 启动心跳
        startHeartbeat()
      }
      
      ws.value.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          handleMessage(message)
        } catch (error) {
          console.error('WebSocket 消息解析失败:', error)
        }
      }
      
      ws.value.onerror = (error) => {
        console.error('❌ WebSocket 错误:', error)
        connected.value = false
      }
      
      ws.value.onclose = () => {
        console.log('🔌 WebSocket 已断开')
        connected.value = false
        ws.value = null
        
        // 自动重连
        handleReconnect()
      }
      
    } catch (error) {
      console.error('WebSocket 连接失败:', error)
      handleReconnect()
    }
  }
  
  // 处理消息
  const handleMessage = (message) => {
    const { type, data } = message
    
    if (type === 'pong') {
      // 心跳响应
      return
    }
    
    if (type === 'subscribed') {
      console.log(`✅ 已订阅频道: ${data.channel}`)
      return
    }
    
    if (type === 'unsubscribed') {
      console.log(`🔕 已取消订阅: ${data.channel}`)
      return
    }
    
    // 触发对应的处理器
    if (handlers[type]) {
      handlers[type].forEach(handler => {
        try {
          handler(data)
        } catch (error) {
          console.error(`处理器执行失败 (${type}):`, error)
        }
      })
    }
  }
  
  // 自动重连
  const handleReconnect = () => {
    if (reconnecting.value) {
      return
    }
    
    if (reconnectCount.value >= maxReconnectAttempts) {
      ElMessage.error(`WebSocket 重连失败（${maxReconnectAttempts} 次），请刷新页面`)
      return
    }
    
    reconnecting.value = true
    reconnectCount.value++
    
    const delay = Math.min(1000 * Math.pow(2, reconnectCount.value - 1), 30000)
    
    console.log(`🔄 WebSocket 重连中... (${reconnectCount.value}/${maxReconnectAttempts}，${delay}ms 后重试)`)
    
    setTimeout(() => {
      reconnecting.value = false
      connect()
    }, delay)
  }
  
  // 心跳
  let heartbeatInterval = null
  
  const startHeartbeat = () => {
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval)
    }
    
    heartbeatInterval = setInterval(() => {
      if (connected.value && ws.value) {
        ws.value.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000) // 每 30 秒心跳
  }
  
  const stopHeartbeat = () => {
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval)
      heartbeatInterval = null
    }
  }
  
  // 订阅频道
  const subscribe = (channel) => {
    if (connected.value && ws.value) {
      ws.value.send(JSON.stringify({
        type: 'subscribe',
        channel
      }))
    }
  }
  
  // 取消订阅
  const unsubscribe = (channel) => {
    if (connected.value && ws.value) {
      ws.value.send(JSON.stringify({
        type: 'unsubscribe',
        channel
      }))
    }
  }
  
  // 监听事件
  const on = (type, handler) => {
    if (!handlers[type]) {
      handlers[type] = []
    }
    handlers[type].push(handler)
  }
  
  // 移除监听
  const off = (type, handler) => {
    if (handlers[type]) {
      const index = handlers[type].indexOf(handler)
      if (index > -1) {
        handlers[type].splice(index, 1)
      }
    }
  }
  
  // 断开连接
  const disconnect = () => {
    stopHeartbeat()
    
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    
    connected.value = false
  }
  
  // 生命周期
  onMounted(() => {
    connect()
  })
  
  onUnmounted(() => {
    disconnect()
  })
  
  return {
    connected,
    reconnecting,
    subscribe,
    unsubscribe,
    on,
    off,
    disconnect
  }
}
