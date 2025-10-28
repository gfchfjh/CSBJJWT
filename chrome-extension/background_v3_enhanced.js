/**
 * KOOK Cookie导出器 - Chrome扩展 v3.0 Enhanced
 * 
 * 功能：
 * - 一键导出KOOK Cookie（JSON、Netscape、Header格式）
 * - 自动检测KOOK网站并提示导出
 * - 支持快捷键导出（Ctrl+Shift+K）
 * - 导出历史记录和管理
 * - Cookie有效性验证
 */

// 扩展版本
const EXTENSION_VERSION = '3.0.0'

// KOOK域名
const KOOK_DOMAINS = [
  'kookapp.cn',
  'kaiheila.cn',
  'kaihei.co'
]

// 监听扩展安装/更新
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('KOOK Cookie导出器已安装')
    // 打开欢迎页
    chrome.tabs.create({
      url: chrome.runtime.getURL('welcome.html')
    })
  } else if (details.reason === 'update') {
    console.log(`KOOK Cookie导出器已更新至 v${EXTENSION_VERSION}`)
  }
  
  // 创建右键菜单
  createContextMenus()
})

// 创建右键菜单
function createContextMenus() {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: 'export-kook-cookie',
      title: '导出KOOK Cookie',
      contexts: ['page'],
      documentUrlPatterns: KOOK_DOMAINS.map(domain => `*://*.${domain}/*`)
    })
    
    chrome.contextMenus.create({
      id: 'export-json',
      title: '导出为JSON格式',
      contexts: ['page'],
      parentId: 'export-kook-cookie',
      documentUrlPatterns: KOOK_DOMAINS.map(domain => `*://*.${domain}/*`)
    })
    
    chrome.contextMenus.create({
      id: 'export-netscape',
      title: '导出为Netscape格式',
      contexts: ['page'],
      parentId: 'export-kook-cookie',
      documentUrlPatterns: KOOK_DOMAINS.map(domain => `*://*.${domain}/*`)
    })
    
    chrome.contextMenus.create({
      id: 'export-header',
      title: '导出为HTTP Header格式',
      contexts: ['page'],
      parentId: 'export-kook-cookie',
      documentUrlPatterns: KOOK_DOMAINS.map(domain => `*://*.${domain}/*`)
    })
    
    chrome.contextMenus.create({
      id: 'verify-cookie',
      title: '验证Cookie有效性',
      contexts: ['page'],
      parentId: 'export-kook-cookie',
      documentUrlPatterns: KOOK_DOMAINS.map(domain => `*://*.${domain}/*`)
    })
  })
}

// 监听右键菜单点击
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId.startsWith('export-')) {
    const format = info.menuItemId.replace('export-', '')
    exportCookies(tab, format)
  } else if (info.menuItemId === 'verify-cookie') {
    verifyCookies(tab)
  }
})

// 监听来自popup的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'exportCookies') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        exportCookies(tabs[0], request.format || 'json')
      }
    })
  } else if (request.action === 'verifyCookies') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        verifyCookies(tabs[0])
      }
    })
  } else if (request.action === 'getHistory') {
    getExportHistory().then(history => {
      sendResponse({ history })
    })
    return true
  } else if (request.action === 'clearHistory') {
    clearExportHistory().then(() => {
      sendResponse({ success: true })
    })
    return true
  }
})

// 导出Cookie
async function exportCookies(tab, format) {
  try {
    // 获取KOOK的所有Cookie
    const cookies = await getAllKookCookies()
    
    if (!cookies || cookies.length === 0) {
      showNotification('错误', '未找到KOOK Cookie，请先登录KOOK网站', 'error')
      return
    }
    
    // 转换为指定格式
    let exportData = ''
    let filename = ''
    let mimeType = 'text/plain'
    
    switch (format) {
      case 'json':
        exportData = JSON.stringify(cookies, null, 2)
        filename = `kook_cookies_${Date.now()}.json`
        mimeType = 'application/json'
        break
        
      case 'netscape':
        exportData = convertToNetscape(cookies)
        filename = `kook_cookies_${Date.now()}.txt`
        break
        
      case 'header':
        exportData = convertToHeader(cookies)
        filename = `kook_cookies_${Date.now()}.txt`
        break
        
      default:
        exportData = JSON.stringify(cookies, null, 2)
        filename = `kook_cookies_${Date.now()}.json`
        mimeType = 'application/json'
    }
    
    // 下载文件
    downloadFile(exportData, filename, mimeType)
    
    // 保存到历史记录
    await saveToHistory({
      timestamp: Date.now(),
      format: format,
      cookieCount: cookies.length,
      filename: filename
    })
    
    // 显示成功通知
    showNotification(
      '导出成功',
      `已导出${cookies.length}个Cookie (${format.toUpperCase()}格式)`,
      'success'
    )
    
  } catch (error) {
    console.error('导出Cookie失败:', error)
    showNotification('导出失败', error.message, 'error')
  }
}

// 获取所有KOOK Cookie
async function getAllKookCookies() {
  const allCookies = []
  
  for (const domain of KOOK_DOMAINS) {
    const cookies = await chrome.cookies.getAll({ domain: domain })
    allCookies.push(...cookies)
  }
  
  // 去重
  const uniqueCookies = []
  const seen = new Set()
  
  for (const cookie of allCookies) {
    const key = `${cookie.name}_${cookie.domain}`
    if (!seen.has(key)) {
      seen.add(key)
      uniqueCookies.push(cookie)
    }
  }
  
  return uniqueCookies
}

// 转换为Netscape格式
function convertToNetscape(cookies) {
  let result = '# Netscape HTTP Cookie File\n'
  result += '# This file was generated by KOOK Cookie Exporter\n'
  result += '# Edit at your own risk.\n\n'
  
  for (const cookie of cookies) {
    const domain = cookie.domain.startsWith('.') ? cookie.domain : `.${cookie.domain}`
    const flag = cookie.domain.startsWith('.') ? 'TRUE' : 'FALSE'
    const path = cookie.path || '/'
    const secure = cookie.secure ? 'TRUE' : 'FALSE'
    const expiration = cookie.expirationDate ? Math.floor(cookie.expirationDate) : 0
    const name = cookie.name
    const value = cookie.value
    
    result += `${domain}\t${flag}\t${path}\t${secure}\t${expiration}\t${name}\t${value}\n`
  }
  
  return result
}

// 转换为HTTP Header格式
function convertToHeader(cookies) {
  const cookieStrings = cookies.map(cookie => `${cookie.name}=${cookie.value}`)
  return cookieStrings.join('; ')
}

// 下载文件
function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  
  chrome.downloads.download({
    url: url,
    filename: filename,
    saveAs: true
  }, (downloadId) => {
    if (chrome.runtime.lastError) {
      console.error('下载失败:', chrome.runtime.lastError)
    } else {
      console.log('下载成功, ID:', downloadId)
      // 下载完成后释放URL
      setTimeout(() => URL.revokeObjectURL(url), 60000)
    }
  })
}

// 显示通知
function showNotification(title, message, type = 'info') {
  const iconMap = {
    success: 'icon-128.png',
    error: 'icon-128.png',
    warning: 'icon-128.png',
    info: 'icon-128.png'
  }
  
  chrome.notifications.create({
    type: 'basic',
    iconUrl: chrome.runtime.getURL(iconMap[type]),
    title: title,
    message: message,
    priority: 1
  })
}

// 验证Cookie有效性
async function verifyCookies(tab) {
  try {
    const cookies = await getAllKookCookies()
    
    if (!cookies || cookies.length === 0) {
      showNotification('验证失败', '未找到KOOK Cookie', 'error')
      return
    }
    
    // 检查是否包含关键Cookie
    const tokenCookie = cookies.find(c => c.name === 'token' || c.name === 'kook_token')
    const uidCookie = cookies.find(c => c.name === 'uid' || c.name === 'user_id')
    
    if (!tokenCookie) {
      showNotification(
        '验证失败',
        'Cookie中缺少token字段，请重新登录KOOK',
        'error'
      )
      return
    }
    
    // 检查Cookie是否过期
    const now = Date.now() / 1000
    const expiredCookies = cookies.filter(c => 
      c.expirationDate && c.expirationDate < now
    )
    
    if (expiredCookies.length > 0) {
      showNotification(
        '验证警告',
        `有${expiredCookies.length}个Cookie已过期，建议重新登录`,
        'warning'
      )
    } else {
      showNotification(
        '验证成功',
        `Cookie有效，包含${cookies.length}个字段`,
        'success'
      )
    }
    
  } catch (error) {
    console.error('验证Cookie失败:', error)
    showNotification('验证失败', error.message, 'error')
  }
}

// 保存到历史记录
async function saveToHistory(record) {
  const history = await getExportHistory()
  history.unshift(record)
  
  // 只保留最近20条
  if (history.length > 20) {
    history.splice(20)
  }
  
  await chrome.storage.local.set({ exportHistory: history })
}

// 获取历史记录
async function getExportHistory() {
  const result = await chrome.storage.local.get('exportHistory')
  return result.exportHistory || []
}

// 清空历史记录
async function clearExportHistory() {
  await chrome.storage.local.remove('exportHistory')
}

// 监听快捷键（Ctrl+Shift+K）
chrome.commands.onCommand.addListener((command) => {
  if (command === 'export-kook-cookie') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        const url = new URL(tabs[0].url)
        const isKookSite = KOOK_DOMAINS.some(domain => url.hostname.includes(domain))
        
        if (isKookSite) {
          exportCookies(tabs[0], 'json')
        } else {
          showNotification(
            '错误',
            '请在KOOK网站上使用此功能',
            'error'
          )
        }
      }
    })
  }
})

// 监听标签页更新（检测KOOK网站）
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    const url = new URL(tab.url)
    const isKookSite = KOOK_DOMAINS.some(domain => url.hostname.includes(domain))
    
    if (isKookSite) {
      // 向content script发送消息，显示浮动按钮
      chrome.tabs.sendMessage(tabId, {
        action: 'showExportButton'
      }).catch(() => {
        // 忽略错误（content script可能还没注入）
      })
    }
  }
})

console.log(`KOOK Cookie导出器 v${EXTENSION_VERSION} 已启动`)
