/**
 * KOOK Cookie自动导入 - 后台服务
 * 功能：监听扩展点击，自动提取Cookie并发送到本地系统
 */

const LOCAL_API_URL = 'http://localhost:9527';
const KOOK_DOMAIN = '.kookapp.cn';

// 监听扩展图标点击
chrome.action.onClicked.addListener(async (tab) => {
  await exportAndSendCookie();
});

// 监听快捷键
chrome.commands.onCommand.addListener(async (command) => {
  if (command === 'export-cookie') {
    await exportAndSendCookie();
  }
});

/**
 * 主函数：导出Cookie并发送
 */
async function exportAndSendCookie() {
  try {
    console.log('[KOOK Extension] 开始导出Cookie...');
    
    // 1. 获取当前标签页
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // 2. 检查是否在KOOK网站
    if (!tab.url.includes('kookapp.cn')) {
      showNotification('请在KOOK网站使用', '请先访问 www.kookapp.cn', 'warning');
      return;
    }
    
    // 3. 提取Cookie
    const cookies = await extractKookCookies();
    
    if (!cookies || cookies.length === 0) {
      showNotification('未找到Cookie', '请先登录KOOK网站', 'error');
      return;
    }
    
    console.log(`[KOOK Extension] 提取到 ${cookies.length} 个Cookie`);
    
    // 4. 验证Cookie完整性
    const validation = validateCookies(cookies);
    if (!validation.valid) {
      showNotification('Cookie不完整', validation.message, 'warning');
      return;
    }
    
    // 5. 尝试自动发送到本地系统
    const sendResult = await sendToLocalSystem(cookies);
    
    if (sendResult.success) {
      // 成功：显示成功通知
      showNotification(
        '✅ Cookie导入成功！',
        `已自动导入 ${cookies.length} 个Cookie到系统`,
        'success'
      );
      
      // 保存到本地存储（历史记录）
      await saveCookieHistory(cookies);
    } else {
      // 失败：降级到剪贴板
      await copyToClipboard(cookies);
      showNotification(
        '📋 已复制到剪贴板',
        '系统未启动，请手动粘贴到设置页',
        'info'
      );
    }
    
  } catch (error) {
    console.error('[KOOK Extension] 错误:', error);
    showNotification('导出失败', error.message, 'error');
  }
}

/**
 * 提取KOOK Cookie
 */
async function extractKookCookies() {
  try {
    const cookies = await chrome.cookies.getAll({ domain: KOOK_DOMAIN });
    
    // 过滤出关键Cookie
    const importantKeys = ['token', 'session', 'user_id', '_ga', '_gid'];
    const filtered = cookies.filter(cookie => 
      importantKeys.some(key => cookie.name.toLowerCase().includes(key.toLowerCase()))
    );
    
    return filtered.length > 0 ? filtered : cookies;
  } catch (error) {
    console.error('[KOOK Extension] 提取Cookie失败:', error);
    return [];
  }
}

/**
 * 验证Cookie完整性
 */
function validateCookies(cookies) {
  const requiredKeys = ['token', 'session'];
  const foundKeys = cookies.map(c => c.name.toLowerCase());
  
  const missingKeys = requiredKeys.filter(key => 
    !foundKeys.some(name => name.includes(key))
  );
  
  if (missingKeys.length > 0) {
    return {
      valid: false,
      message: `缺少关键Cookie: ${missingKeys.join(', ')}`
    };
  }
  
  return { valid: true };
}

/**
 * 发送Cookie到本地系统
 */
async function sendToLocalSystem(cookies) {
  try {
    const response = await fetch(`${LOCAL_API_URL}/api/cookie/import`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        cookies: cookies,
        source: 'chrome_extension',
        timestamp: Date.now()
      }),
      // 设置较短超时，避免长时间等待
      signal: AbortSignal.timeout(3000)
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('[KOOK Extension] 发送成功:', data);
      return { success: true, data };
    } else {
      console.warn('[KOOK Extension] 服务器返回错误:', response.status);
      return { success: false, error: `HTTP ${response.status}` };
    }
  } catch (error) {
    console.warn('[KOOK Extension] 无法连接到本地系统:', error.message);
    return { success: false, error: error.message };
  }
}

/**
 * 复制到剪贴板（降级方案）
 */
async function copyToClipboard(cookies) {
  const cookieJson = JSON.stringify(cookies, null, 2);
  
  try {
    // 使用Clipboard API
    await navigator.clipboard.writeText(cookieJson);
    console.log('[KOOK Extension] 已复制到剪贴板');
  } catch (error) {
    console.error('[KOOK Extension] 复制失败:', error);
    // 降级：使用旧方法
    const textarea = document.createElement('textarea');
    textarea.value = cookieJson;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
  }
}

/**
 * 显示通知
 */
function showNotification(title, message, type = 'info') {
  const iconMap = {
    success: 'icons/icon128.png',
    error: 'icons/icon128.png',
    warning: 'icons/icon128.png',
    info: 'icons/icon128.png'
  };
  
  chrome.notifications.create({
    type: 'basic',
    iconUrl: iconMap[type],
    title: title,
    message: message,
    priority: 2
  });
}

/**
 * 保存Cookie历史记录
 */
async function saveCookieHistory(cookies) {
  try {
    const history = await chrome.storage.local.get('cookieHistory') || { cookieHistory: [] };
    const historyList = history.cookieHistory || [];
    
    // 添加新记录（最多保留20条）
    historyList.unshift({
      cookies: cookies.length,
      timestamp: Date.now(),
      domain: KOOK_DOMAIN
    });
    
    if (historyList.length > 20) {
      historyList.pop();
    }
    
    await chrome.storage.local.set({ cookieHistory: historyList });
    console.log('[KOOK Extension] Cookie历史已保存');
  } catch (error) {
    console.error('[KOOK Extension] 保存历史失败:', error);
  }
}

// 监听来自popup的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'exportCookie') {
    exportAndSendCookie().then(() => {
      sendResponse({ success: true });
    }).catch(error => {
      sendResponse({ success: false, error: error.message });
    });
    return true; // 保持消息通道开启
  }
  
  if (request.action === 'getHistory') {
    chrome.storage.local.get('cookieHistory').then(data => {
      sendResponse({ history: data.cookieHistory || [] });
    });
    return true;
  }
});

console.log('[KOOK Extension] 后台服务已启动');
