/**
 * Popup脚本
 */

// DOM元素
const elements = {
  cookieCount: document.getElementById('cookie-count'),
  cookieValidity: document.getElementById('cookie-validity'),
  systemStatus: document.getElementById('system-status'),
  autoSendBtn: document.getElementById('auto-send-btn'),
  sendLoading: document.getElementById('send-loading'),
  exportJsonBtn: document.getElementById('export-json-btn'),
  exportNetscapeBtn: document.getElementById('export-netscape-btn'),
  exportHeaderBtn: document.getElementById('export-header-btn'),
  historyList: document.getElementById('history-list'),
  clearHistory: document.getElementById('clear-history'),
  openSettings: document.getElementById('open-settings')
}

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
  await checkStatus()
  await loadHistory()
  bindEvents()
})

/**
 * 检查状态
 */
async function checkStatus() {
  try {
    // 1. 检查Cookie
    const allCookies = []
    const domains = ['.kookapp.cn', 'www.kookapp.cn']
    
    for (const domain of domains) {
      const cookies = await chrome.cookies.getAll({ domain })
      allCookies.push(...cookies)
    }
    
    elements.cookieCount.textContent = `${allCookies.length}个`
    
    // 2. 验证Cookie
    const requiredFields = ['token', 'session', 'user_id']
    const foundFields = allCookies.filter(c => requiredFields.includes(c.name))
    
    if (foundFields.length === requiredFields.length) {
      elements.cookieValidity.textContent = '✅ 有效'
      elements.cookieValidity.classList.add('success')
    } else {
      elements.cookieValidity.textContent = '⚠️ 部分缺失'
      elements.cookieValidity.classList.add('error')
    }
    
    // 3. 检查本地系统
    const isSystemOnline = await checkLocalSystem()
    
    if (isSystemOnline) {
      elements.systemStatus.textContent = '✅ 在线'
      elements.systemStatus.classList.add('success')
    } else {
      elements.systemStatus.textContent = '❌ 离线'
      elements.systemStatus.classList.add('error')
      elements.autoSendBtn.disabled = true
      elements.autoSendBtn.innerHTML = '<span>⚠️</span><span>本地系统未运行</span>'
    }
    
  } catch (error) {
    console.error('状态检查失败:', error)
  }
}

/**
 * 检查本地系统是否在线
 */
async function checkLocalSystem() {
  const urls = [
    'http://localhost:9527/health',
    'http://127.0.0.1:9527/health'
  ]
  
  for (const url of urls) {
    try {
      const response = await fetch(url, {
        method: 'GET',
        signal: AbortSignal.timeout(2000)  // 2秒超时
      })
      
      if (response.ok) {
        return true
      }
    } catch (error) {
      continue
    }
  }
  
  return false
}

/**
 * 加载历史记录
 */
async function loadHistory() {
  try {
    const result = await chrome.storage.local.get('history')
    const history = result.history || []
    
    if (history.length === 0) {
      elements.historyList.innerHTML = '<div class="history-item"><div class="time">暂无历史记录</div></div>'
      return
    }
    
    elements.historyList.innerHTML = history.slice(0, 5).map(record => {
      const date = new Date(record.timestamp)
      const timeStr = date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
      
      return `
        <div class="history-item">
          <div class="time">${timeStr}</div>
          <div>
            <span class="format">${formatName(record.format)}</span>
            · ${record.cookies.length}个Cookie
            · ${record.validation.isValid ? '✅' : '⚠️'}
          </div>
        </div>
      `
    }).join('')
    
  } catch (error) {
    console.error('加载历史失败:', error)
  }
}

/**
 * 格式名称
 */
function formatName(format) {
  const map = {
    'json': 'JSON',
    'netscape': 'Netscape',
    'header': 'Header',
    'auto-send': '自动发送'
  }
  return map[format] || format
}

/**
 * 绑定事件
 */
function bindEvents() {
  // 一键导入
  elements.autoSendBtn.addEventListener('click', async () => {
    elements.sendLoading.classList.remove('hidden')
    elements.autoSendBtn.disabled = true
    
    try {
      await chrome.runtime.sendMessage({ action: 'exportAndSend' })
      await loadHistory()
    } catch (error) {
      console.error('发送失败:', error)
    } finally {
      elements.sendLoading.classList.add('hidden')
      elements.autoSendBtn.disabled = false
    }
  })
  
  // 导出JSON
  elements.exportJsonBtn.addEventListener('click', async () => {
    await chrome.runtime.sendMessage({ action: 'exportCookies', format: 'json' })
    await loadHistory()
  })
  
  // 导出Netscape
  elements.exportNetscapeBtn.addEventListener('click', async () => {
    await chrome.runtime.sendMessage({ action: 'exportCookies', format: 'netscape' })
    await loadHistory()
  })
  
  // 导出Header
  elements.exportHeaderBtn.addEventListener('click', async () => {
    await chrome.runtime.sendMessage({ action: 'exportCookies', format: 'header' })
    await loadHistory()
  })
  
  // 清空历史
  elements.clearHistory.addEventListener('click', async (e) => {
    e.preventDefault()
    
    if (confirm('确定要清空所有历史记录吗？')) {
      await chrome.storage.local.set({ history: [] })
      await loadHistory()
    }
  })
  
  // 设置
  elements.openSettings.addEventListener('click', (e) => {
    e.preventDefault()
    chrome.runtime.openOptionsPage()
  })
}

// 监听来自background的消息
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'exportCookies') {
    exportCookies(message.format)
  } else if (message.action === 'exportAndSend') {
    exportAndSend()
  }
})

/**
 * 导出Cookie（调用background脚本）
 */
async function exportCookies(format) {
  // 实际导出逻辑在background.js中
  // 这里只是触发
  chrome.runtime.sendMessage({
    action: 'exportCookies',
    format: format
  })
}

/**
 * 导出并发送
 */
async function exportAndSend() {
  chrome.runtime.sendMessage({
    action: 'exportAndSend'
  })
}
