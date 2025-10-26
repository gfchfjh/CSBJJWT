/**
 * KOOK Cookie 导出器 - 后台服务
 * 监听Cookie变化，提供通知等功能
 */

// 监听Cookie变化
chrome.cookies.onChanged.addListener((changeInfo) => {
  // 只关注KOOK相关Cookie
  if (changeInfo.cookie.domain.includes('kookapp.cn') || 
      changeInfo.cookie.domain.includes('kaiheila.cn')) {
    
    console.log('KOOK Cookie变化:', changeInfo);
    
    // 如果是关键Cookie被删除，发送通知
    if (changeInfo.removed && 
        (changeInfo.cookie.name === 'token' || 
         changeInfo.cookie.name === 'sid' ||
         changeInfo.cookie.name === 'session')) {
      
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon-128.png',
        title: 'KOOK Cookie已失效',
        message: '检测到关键Cookie被删除，请重新登录KOOK并导出Cookie'
      });
    }
  }
});

// 监听扩展安装/更新
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    // 首次安装
    console.log('KOOK Cookie导出器已安装');
    
    // 打开欢迎页面
    chrome.tabs.create({
      url: 'welcome.html'
    });
    
    // 初始化统计数据
    chrome.storage.local.set({
      exportCount: 0,
      installDate: new Date().toISOString()
    });
    
  } else if (details.reason === 'update') {
    // 更新
    console.log('KOOK Cookie导出器已更新到', chrome.runtime.getManifest().version);
  }
});

// 监听来自content script的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getCookies') {
    // 获取Cookie
    getCookies().then(cookies => {
      sendResponse({ cookies });
    });
    return true; // 异步响应
  }
  
  if (request.action === 'notify') {
    // 发送通知
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon-128.png',
      title: request.title || 'KOOK Cookie导出器',
      message: request.message
    });
  }
});

// 获取所有KOOK Cookie
async function getCookies() {
  const domains = ['.kookapp.cn', '.kaiheila.cn'];
  let allCookies = [];
  
  for (const domain of domains) {
    const cookies = await chrome.cookies.getAll({ domain });
    allCookies = allCookies.concat(cookies);
  }
  
  return allCookies;
}

// 定期检查Cookie健康状态（每小时）
setInterval(async () => {
  const cookies = await getCookies();
  
  if (cookies.length === 0) {
    console.warn('未检测到KOOK Cookie');
  } else {
    console.log(`当前KOOK Cookie数量: ${cookies.length}`);
    
    // 检查是否有即将过期的Cookie
    const now = Date.now() / 1000;
    const expiringCookies = cookies.filter(c => {
      if (c.expirationDate) {
        const timeLeft = c.expirationDate - now;
        return timeLeft > 0 && timeLeft < 86400; // 24小时内过期
      }
      return false;
    });
    
    if (expiringCookies.length > 0) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon-128.png',
        title: 'Cookie即将过期',
        message: `有 ${expiringCookies.length} 个Cookie将在24小时内过期，建议重新登录`
      });
    }
  }
}, 3600000); // 1小时

// 响应外部消息（来自网页）
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
  if (request.action === 'exportCookies') {
    getCookies().then(cookies => {
      const formatted = JSON.stringify(cookies, null, 2);
      sendResponse({ success: true, cookies: formatted });
    }).catch(error => {
      sendResponse({ success: false, error: error.message });
    });
    return true;
  }
});

console.log('KOOK Cookie导出器后台服务已启动');
