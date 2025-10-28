/**
 * KOOK Cookie导出扩展 - 后台脚本
 * 版本: v3.0.0 Ultimate
 * 功能: 3种格式导出 + 自动发送 + 历史记录
 */

// 配置
const CONFIG = {
  KOOK_DOMAINS: ['.kookapp.cn', 'www.kookapp.cn'],
  LOCAL_API_URL: 'http://localhost:9527/api/cookie/import',
  LOCAL_API_URL_ALT: 'http://127.0.0.1:9527/api/cookie/import',
  MAX_HISTORY: 20  // 最多保存20条历史记录
}

// 安装时初始化
chrome.runtime.onInstalled.addListener(() => {
  console.log('KOOK Cookie导出扩展已安装')
  
  // 创建右键菜单
  chrome.contextMenus.create({
    id: 'export-cookie-json',
    title: '导出Cookie (JSON格式)',
    contexts: ['page'],
    documentUrlPatterns: ['*://*.kookapp.cn/*']
  })
  
  chrome.contextMenus.create({
    id: 'export-cookie-netscape',
    title: '导出Cookie (Netscape格式)',
    contexts: ['page'],
    documentUrlPatterns: ['*://*.kookapp.cn/*']
  })
  
  chrome.contextMenus.create({
    id: 'export-cookie-header',
    title: '导出Cookie (HTTP Header格式)',
    contexts: ['page'],
    documentUrlPatterns: ['*://*.kookapp.cn/*']
  })
  
  chrome.contextMenus.create({
    id: 'separator',
    type: 'separator',
    contexts: ['page'],
    documentUrlPatterns: ['*://*.kookapp.cn/*']
  })
  
  chrome.contextMenus.create({
    id: 'auto-send',
    title: '自动发送到本地系统',
    contexts: ['page'],
    documentUrlPatterns: ['*://*.kookapp.cn/*']
  })
})

// 右键菜单点击
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'export-cookie-json') {
    exportCookies('json')
  } else if (info.menuItemId === 'export-cookie-netscape') {
    exportCookies('netscape')
  } else if (info.menuItemId === 'export-cookie-header') {
    exportCookies('header')
  } else if (info.menuItemId === 'auto-send') {
    exportAndSend()
  }
})

// 快捷键命令
chrome.commands.onCommand.addListener((command) => {
  if (command === 'export-cookie') {
    exportAndSend()
  }
})

/**
 * 导出Cookie
 * @param {string} format - 格式: json/netscape/header
 */
async function exportCookies(format = 'json') {
  try {
    // 1. 获取所有KOOK域名的Cookie
    const allCookies = []
    
    for (const domain of CONFIG.KOOK_DOMAINS) {
      const cookies = await chrome.cookies.getAll({ domain })
      allCookies.push(...cookies)
    }
    
    if (allCookies.length === 0) {
      showNotification('未找到Cookie', '请先登录KOOK网页版', 'error')
      return
    }
    
    // 2. 验证Cookie有效性
    const validation = validateCookies(allCookies)
    
    // 3. 格式转换
    let exportData
    let filename
    
    if (format === 'json') {
      exportData = JSON.stringify(allCookies, null, 2)
      filename = `kook_cookies_${Date.now()}.json`
    } else if (format === 'netscape') {
      exportData = convertToNetscape(allCookies)
      filename = `kook_cookies_${Date.now()}.txt`
    } else if (format === 'header') {
      exportData = convertToHttpHeader(allCookies)
      filename = `kook_cookies_${Date.now()}.txt`
    }
    
    // 4. 复制到剪贴板
    await copyToClipboard(exportData)
    
    // 5. 保存到历史记录
    await saveToHistory({
      format,
      cookies: allCookies,
      validation,
      timestamp: Date.now()
    })
    
    // 6. 显示通知
    showNotification(
      '导出成功！',
      `已复制${allCookies.length}个Cookie到剪贴板\n有效性: ${validation.isValid ? '✅ 有效' : '⚠️ 可能已过期'}`,
      validation.isValid ? 'success' : 'warning'
    )
    
  } catch (error) {
    console.error('导出失败:', error)
    showNotification('导出失败', error.message, 'error')
  }
}

/**
 * 导出并自动发送到本地系统
 */
async function exportAndSend() {
  try {
    // 1. 获取Cookie
    const allCookies = []
    
    for (const domain of CONFIG.KOOK_DOMAINS) {
      const cookies = await chrome.cookies.getAll({ domain })
      allCookies.push(...cookies)
    }
    
    if (allCookies.length === 0) {
      showNotification('未找到Cookie', '请先登录KOOK网页版', 'error')
      return
    }
    
    // 2. 验证Cookie
    const validation = validateCookies(allCookies)
    
    if (!validation.isValid) {
      showNotification(
        '⚠️ Cookie可能无效',
        `缺少关键字段: ${validation.missingFields.join(', ')}\n是否继续发送？`,
        'warning'
      )
    }
    
    // 3. 发送到本地API
    const success = await sendToLocalAPI(allCookies)
    
    if (success) {
      // 保存到历史
      await saveToHistory({
        format: 'auto-send',
        cookies: allCookies,
        validation,
        timestamp: Date.now()
      })
      
      showNotification(
        '✅ 导入成功！',
        `已自动导入${allCookies.length}个Cookie到KOOK转发系统`,
        'success'
      )
    } else {
      // 降级：复制到剪贴板
      const jsonData = JSON.stringify(allCookies, null, 2)
      await copyToClipboard(jsonData)
      
      showNotification(
        '⚠️ 自动发送失败',
        '已复制到剪贴板，请手动粘贴到系统中',
        'warning'
      )
    }
    
  } catch (error) {
    console.error('发送失败:', error)
    showNotification('发送失败', error.message, 'error')
  }
}

/**
 * 验证Cookie有效性
 */
function validateCookies(cookies) {
  const requiredFields = ['token', 'session', 'user_id']
  const foundFields = new Set()
  
  for (const cookie of cookies) {
    if (requiredFields.includes(cookie.name)) {
      foundFields.add(cookie.name)
    }
  }
  
  const missingFields = requiredFields.filter(f => !foundFields.has(f))
  
  return {
    isValid: missingFields.length === 0,
    foundFields: Array.from(foundFields),
    missingFields: missingFields
  }
}

/**
 * 转换为Netscape格式
 */
function convertToNetscape(cookies) {
  let netscape = '# Netscape HTTP Cookie File\n'
  netscape += '# This is a generated file! Do not edit.\n\n'
  
  for (const cookie of cookies) {
    const domain = cookie.domain.startsWith('.') ? cookie.domain : '.' + cookie.domain
    const flag = cookie.domain.startsWith('.') ? 'TRUE' : 'FALSE'
    const path = cookie.path || '/'
    const secure = cookie.secure ? 'TRUE' : 'FALSE'
    const expiration = cookie.expirationDate ? Math.floor(cookie.expirationDate) : 0
    const name = cookie.name
    const value = cookie.value
    
    netscape += `${domain}\t${flag}\t${path}\t${secure}\t${expiration}\t${name}\t${value}\n`
  }
  
  return netscape
}

/**
 * 转换为HTTP Header格式
 */
function convertToHttpHeader(cookies) {
  const cookieStrings = cookies.map(c => `${c.name}=${c.value}`)
  return 'Cookie: ' + cookieStrings.join('; ')
}

/**
 * 复制到剪贴板
 */
async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text)
  } catch (error) {
    // 降级方案：使用document.execCommand
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
  }
}

/**
 * 发送到本地API
 */
async function sendToLocalAPI(cookies) {
  const urls = [CONFIG.LOCAL_API_URL, CONFIG.LOCAL_API_URL_ALT]
  
  for (const url of urls) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          cookies: cookies,
          format: 'json',
          source: 'chrome-extension',
          version: '3.0.0'
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        return data.success === true
      }
    } catch (error) {
      console.warn(`发送到${url}失败:`, error)
      continue
    }
  }
  
  return false
}

/**
 * 保存到历史记录
 */
async function saveToHistory(record) {
  try {
    const result = await chrome.storage.local.get('history')
    let history = result.history || []
    
    // 添加新记录
    history.unshift(record)
    
    // 保留最近N条
    if (history.length > CONFIG.MAX_HISTORY) {
      history = history.slice(0, CONFIG.MAX_HISTORY)
    }
    
    await chrome.storage.local.set({ history })
  } catch (error) {
    console.error('保存历史失败:', error)
  }
}

/**
 * 显示通知
 */
function showNotification(title, message, type = 'info') {
  const iconMap = {
    success: 'icons/icon-128.png',
    warning: 'icons/icon-128.png',
    error: 'icons/icon-128.png',
    info: 'icons/icon-128.png'
  }
  
  chrome.notifications.create({
    type: 'basic',
    iconUrl: iconMap[type],
    title: title,
    message: message,
    priority: 2
  })
}

// 导出供popup使用
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    exportCookies,
    exportAndSend
  }
}
