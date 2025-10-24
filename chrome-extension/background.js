// ✅ P0-2: 浏览器扩展 - 后台脚本

chrome.runtime.onInstalled.addListener(() => {
  console.log('KOOK Cookie导出助手已安装');
});

// 监听来自content script的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'exportCookies') {
    // 导出Cookie
    chrome.cookies.getAll({ domain: '.kookapp.cn' }, (cookies) => {
      if (chrome.runtime.lastError) {
        sendResponse({ 
          success: false, 
          error: chrome.runtime.lastError.message 
        });
        return;
      }

      if (!cookies || cookies.length === 0) {
        sendResponse({ 
          success: false, 
          error: '未找到Cookie' 
        });
        return;
      }

      // 格式化Cookie
      const formattedCookies = cookies.map(c => ({
        name: c.name,
        value: c.value,
        domain: c.domain,
        path: c.path,
        expires: c.expirationDate,
        httpOnly: c.httpOnly,
        secure: c.secure
      }));

      sendResponse({ 
        success: true, 
        cookies: formattedCookies 
      });
    });

    // 返回true表示会异步调用sendResponse
    return true;
  }
});
