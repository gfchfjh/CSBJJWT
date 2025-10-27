/**
 * KOOK Cookie导出工具 - 后台服务
 * 版本: v1.0.0
 */

// 监听扩展安装/更新
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('KOOK Cookie导出工具已安装')
    
    // 初始化存储
    chrome.storage.local.set({
      exportCount: 0,
      installTime: Date.now()
    })
    
    // 打开欢迎页面（可选）
    // chrome.tabs.create({ url: 'welcome.html' })
  } else if (details.reason === 'update') {
    console.log('KOOK Cookie导出工具已更新到', chrome.runtime.getManifest().version)
  }
})

// 监听扩展图标点击（备用，主要使用popup）
chrome.action.onClicked.addListener((tab) => {
  console.log('扩展图标被点击:', tab.url)
})

// 监听消息（来自content script或popup）
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('收到消息:', request)
  
  if (request.action === 'getCookies') {
    // 获取Cookie
    chrome.cookies.getAll({
      domain: '.kookapp.cn'
    }).then(cookies => {
      sendResponse({ success: true, cookies })
    }).catch(error => {
      sendResponse({ success: false, error: error.message })
    })
    
    return true  // 保持消息通道打开
  }
  
  if (request.action === 'checkStatus') {
    // 检查当前页面状态
    sendResponse({
      success: true,
      isKookPage: sender.tab && (
        sender.tab.url.includes('kookapp.cn') ||
        sender.tab.url.includes('kaiheila.cn')
      )
    })
  }
})

// 监听Cookie变化（可选：用于实时监控）
chrome.cookies.onChanged.addListener((changeInfo) => {
  // 只关注KOOK相关的Cookie
  if (changeInfo.cookie.domain.includes('kookapp.cn') || 
      changeInfo.cookie.domain.includes('kaiheila.cn')) {
    console.log('KOOK Cookie变化:', changeInfo.removed ? '删除' : '添加', changeInfo.cookie.name)
  }
})

// 定期清理过期数据（每24小时）
setInterval(() => {
  chrome.storage.local.get(['installTime', 'exportCount'], (data) => {
    const daysSinceInstall = (Date.now() - data.installTime) / (1000 * 60 * 60 * 24)
    
    console.log(`使用统计: 安装${Math.floor(daysSinceInstall)}天，导出${data.exportCount}次`)
  })
}, 24 * 60 * 60 * 1000)
