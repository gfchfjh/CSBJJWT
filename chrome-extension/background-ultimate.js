/**
 * KOOK Cookie导出扩展 - 终极版后台脚本
 * ✅ P0-3优化：一键自动导入到本地软件
 * 版本：4.0.0
 */

// 配置
const CONFIG = {
  LOCAL_ENDPOINTS: [
    'http://localhost:9527',
    'http://127.0.0.1:9527',
    'http://localhost:9528',
  ],
  KOOK_DOMAINS: [
    'www.kookapp.cn',
    'kookapp.cn',
    '.kookapp.cn'
  ],
  TIMEOUT: 5000,
  RETRY_TIMES: 3
};

// 状态管理
let connectionStatus = {
  connected: false,
  endpoint: null,
  lastCheck: null
};

/**
 * 提取KOOK Cookie
 */
async function extractKookCookies() {
  try {
    const cookies = await chrome.cookies.getAll({
      domain: '.kookapp.cn'
    });
    
    if (cookies.length === 0) {
      throw new Error('未找到KOOK Cookie，请先登录KOOK网站');
    }
    
    console.log(`[Cookie] 提取到 ${cookies.length} 个Cookie`);
    
    return cookies.map(cookie => ({
      name: cookie.name,
      value: cookie.value,
      domain: cookie.domain,
      path: cookie.path,
      secure: cookie.secure,
      httpOnly: cookie.httpOnly,
      sameSite: cookie.sameSite,
      expirationDate: cookie.expirationDate
    }));
  } catch (error) {
    console.error('[Cookie] 提取失败:', error);
    throw error;
  }
}

/**
 * 测试本地软件连接
 */
async function testConnection() {
  for (const endpoint of CONFIG.LOCAL_ENDPOINTS) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      
      const response = await fetch(`${endpoint}/health`, {
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        console.log(`[Connection] 连接成功: ${endpoint}`);
        connectionStatus = {
          connected: true,
          endpoint: endpoint,
          lastCheck: Date.now()
        };
        return endpoint;
      }
    } catch (error) {
      console.log(`[Connection] ${endpoint} 失败:`, error.message);
    }
  }
  
  connectionStatus.connected = false;
  return null;
}

/**
 * 发送Cookie到本地软件
 */
async function sendToLocal(cookies) {
  // 先测试连接
  let endpoint = connectionStatus.connected ? connectionStatus.endpoint : null;
  
  if (!endpoint) {
    endpoint = await testConnection();
  }
  
  if (!endpoint) {
    throw new Error('CONNECTION_FAILED');
  }
  
  // 尝试发送
  for (let i = 0; i < CONFIG.RETRY_TIMES; i++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUT);
      
      const response = await fetch(`${endpoint}/api/cookie-import/auto-import`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cookie: cookies,
          source: 'chrome_extension',
          timestamp: Date.now(),
          extension_version: chrome.runtime.getManifest().version
        }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const result = await response.json();
        console.log('[Send] 发送成功:', result);
        return result;
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }
    } catch (error) {
      console.error(`[Send] 尝试 ${i + 1}/${CONFIG.RETRY_TIMES} 失败:`, error);
      
      if (i === CONFIG.RETRY_TIMES - 1) {
        throw error;
      }
      
      // 等待后重试
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
}

/**
 * 下载Cookie文件
 */
async function downloadCookieFile(cookies) {
  const cookieJSON = JSON.stringify(cookies, null, 2);
  const blob = new Blob([cookieJSON], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  
  const now = new Date();
  const filename = `KOOK_Cookie_${now.toISOString().split('T')[0]}.json`;
  
  return new Promise((resolve) => {
    chrome.downloads.download({
      url: url,
      filename: filename,
      saveAs: true
    }, (downloadId) => {
      console.log('[Download] Cookie文件下载:', filename);
      setTimeout(() => URL.revokeObjectURL(url), 60000);
      resolve(downloadId);
    });
  });
}

/**
 * 显示通知
 */
function showNotification(title, message, type = 'info') {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icons/icon-128.png',
    title: title,
    message: message,
    priority: type === 'error' ? 2 : 1
  });
}

/**
 * 主导出流程
 */
async function exportCookie() {
  try {
    console.log('[Export] 开始导出Cookie...');
    
    // 1. 提取Cookie
    const cookies = await extractKookCookies();
    
    // 2. 尝试自动发送
    try {
      const result = await sendToLocal(cookies);
      
      showNotification(
        '✅ Cookie已自动导入！',
        `账号已成功导入到KOOK转发系统\n用户名: ${result.account?.username || '未知'}`,
        'success'
      );
      
      return { success: true, method: 'auto' };
      
    } catch (error) {
      // 3. 发送失败，下载文件
      if (error.message === 'CONNECTION_FAILED') {
        console.log('[Export] 无法连接本地软件，下载Cookie文件');
        
        await downloadCookieFile(cookies);
        
        showNotification(
          '📥 Cookie已下载',
          'KOOK转发系统未运行，Cookie已保存为文件\n请启动软件后手动导入',
          'warning'
        );
        
        return { success: true, method: 'download' };
      } else {
        throw error;
      }
    }
    
  } catch (error) {
    console.error('[Export] 导出失败:', error);
    
    showNotification(
      '❌ Cookie导出失败',
      error.message || '未知错误',
      'error'
    );
    
    return { success: false, error: error.message };
  }
}

// ==================== 事件监听 ====================

// 扩展图标点击
chrome.action.onClicked.addListener(async (tab) => {
  if (!tab.url.includes('kookapp.cn')) {
    showNotification(
      '⚠️ 请在KOOK网站使用',
      '请打开 www.kookapp.cn 后再点击扩展图标',
      'warning'
    );
    return;
  }
  
  await exportCookie();
});

// 快捷键
chrome.commands.onCommand.addListener(async (command) => {
  if (command === 'export-cookie') {
    await exportCookie();
  }
});

// 消息监听
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'export_cookie') {
    exportCookie().then(sendResponse);
    return true;
  } else if (request.action === 'test_connection') {
    testConnection().then(endpoint => {
      sendResponse({
        connected: !!endpoint,
        endpoint: endpoint
      });
    });
    return true;
  } else if (request.action === 'get_status') {
    sendResponse(connectionStatus);
    return false;
  }
});

// 扩展安装
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    showNotification(
      '🎉 安装成功！',
      'KOOK Cookie助手已就绪\n在KOOK网站点击扩展图标即可导出\n快捷键: Ctrl+Shift+K',
      'success'
    );
    
    chrome.tabs.create({ url: 'popup-enhanced.html' });
  } else if (details.reason === 'update') {
    console.log('[Install] 扩展已更新到', chrome.runtime.getManifest().version);
  }
});

// 定期检查连接
chrome.alarms.create('checkConnection', { periodInMinutes: 5 });

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === 'checkConnection') {
    await testConnection();
  }
});

console.log('[Background] KOOK Cookie扩展后台脚本已加载');
