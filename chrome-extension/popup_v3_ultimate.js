/**
 * KOOK Cookie导出器 - Popup脚本
 */

// DOM元素
const statusIcon = document.getElementById('statusIcon')
const statusText = document.getElementById('statusText')
const btnExportJson = document.getElementById('btnExportJson')
const btnExportNetscape = document.getElementById('btnExportNetscape')
const btnExportHeader = document.getElementById('btnExportHeader')
const btnVerify = document.getElementById('btnVerify')
const historyList = document.getElementById('historyList')
const clearHistory = document.getElementById('clearHistory')

// KOOK域名
const KOOK_DOMAINS = ['kookapp.cn', 'kaiheila.cn', 'kaihei.co']

// 初始化
async function init() {
  // 检查当前标签页是否为KOOK网站
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
  
  if (tab && tab.url) {
    const url = new URL(tab.url)
    const isKookSite = KOOK_DOMAINS.some(domain => url.hostname.includes(domain))
    
    if (isKookSite) {
      updateStatus('success', '✅ 已检测到KOOK网站')
      enableButtons()
    } else {
      updateStatus('error', '⚠️ 请在KOOK网站上使用')
      disableButtons()
    }
  } else {
    updateStatus('error', '⚠️ 无法获取当前页面')
    disableButtons()
  }
  
  // 加载历史记录
  loadHistory()
}

// 更新状态
function updateStatus(type, text) {
  statusIcon.className = `status-icon ${type}`
  statusText.textContent = text
}

// 启用按钮
function enableButtons() {
  btnExportJson.disabled = false
  btnExportNetscape.disabled = false
  btnExportHeader.disabled = false
  btnVerify.disabled = false
}

// 禁用按钮
function disableButtons() {
  btnExportJson.disabled = true
  btnExportNetscape.disabled = true
  btnExportHeader.disabled = true
  btnVerify.disabled = true
}

// 加载历史记录
async function loadHistory() {
  const response = await chrome.runtime.sendMessage({ action: 'getHistory' })
  const history = response.history || []
  
  if (history.length === 0) {
    historyList.innerHTML = '<div class="history-empty">暂无导出记录</div>'
    return
  }
  
  historyList.innerHTML = history.map(record => {
    const date = new Date(record.timestamp)
    const timeStr = `${date.getMonth() + 1}/${date.getDate()} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
    
    return `
      <div class="history-item">
        <div class="history-item-time">🕐 ${timeStr}</div>
        <div class="history-item-info">
          ${record.format.toUpperCase()} 格式 · ${record.cookieCount} 个Cookie
        </div>
      </div>
    `
  }).join('')
}

// 导出Cookie
function exportCookies(format) {
  chrome.runtime.sendMessage({
    action: 'exportCookies',
    format: format
  })
  
  // 延迟刷新历史记录
  setTimeout(loadHistory, 500)
}

// 验证Cookie
function verifyCookies() {
  chrome.runtime.sendMessage({ action: 'verifyCookies' })
}

// 清空历史
async function clearHistoryRecords() {
  if (confirm('确定要清空所有导出历史吗？')) {
    await chrome.runtime.sendMessage({ action: 'clearHistory' })
    loadHistory()
  }
}

// 事件监听
btnExportJson.addEventListener('click', () => exportCookies('json'))
btnExportNetscape.addEventListener('click', () => exportCookies('netscape'))
btnExportHeader.addEventListener('click', () => exportCookies('header'))
btnVerify.addEventListener('click', verifyCookies)
clearHistory.addEventListener('click', clearHistoryRecords)

// 页面加载时初始化
init()
