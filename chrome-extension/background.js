// KOOK Cookie Exporter - Background Script

console.log('KOOK Cookie Exporter background script loaded');

// 安装时的欢迎消息
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('KOOK Cookie Exporter installed!');
    
    // 可选：打开欢迎页面
    // chrome.tabs.create({
    //   url: 'welcome.html'
    // });
  }
});

// 监听来自popup的消息（如果需要后台处理）
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'exportCookies') {
    // 处理Cookie导出
    handleCookieExport().then(sendResponse);
    return true; // 异步响应
  }
});

async function handleCookieExport() {
  try {
    const cookies = await chrome.cookies.getAll({
      domain: '.kookapp.cn'
    });
    
    return {
      success: true,
      cookies: cookies
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}
