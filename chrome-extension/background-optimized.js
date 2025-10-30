/**
 * KOOK Cookie自动导入 - 深度优化版
 * 功能：
 * 1. 监听扩展点击，自动提取Cookie并发送
 * 2. 支持WebSocket实时通信
 * 3. 自动检测系统连接状态
 * 4. 提供详细的错误诊断
 */

const LOCAL_API_URL = 'http://localhost:9527';
const KOOK_DOMAIN = '.kookapp.cn';
const WEBSOCKET_URL = 'ws://localhost:9527/ws/cookie-import';

let ws = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

// 初始化WebSocket连接
function initWebSocket() {
  if (ws && ws.readyState === WebSocket.OPEN) {
    return;
  }
  
  try {
    ws = new WebSocket(WEBSOCKET_URL);
    
    ws.onopen = () => {
      console.log('[KOOK Extension] WebSocket connected');
      reconnectAttempts = 0;
      
      // 发送心跳
      sendHeartbeat();
      setInterval(sendHeartbeat, 30000); // 每30秒发送心跳
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('[KOOK Extension] WebSocket message:', data);
      
      if (data.type === 'pong') {
        console.log('[KOOK Extension] Heartbeat acknowledged');
      }
    };
    
    ws.onerror = (error) => {
      console.error('[KOOK Extension] WebSocket error:', error);
    };
    
    ws.onclose = () => {
      console.log('[KOOK Extension] WebSocket closed');
      
      // 尝试重连
      if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++;
        console.log(`[KOOK Extension] Reconnecting... (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
        setTimeout(initWebSocket, 3000);
      }
    };
  } catch (error) {
    console.error('[KOOK Extension] Failed to create WebSocket:', error);
  }
}

function sendHeartbeat() {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: 'ping',
      timestamp: Date.now()
    }));
  }
}

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
    
    // 显示加载通知
    const loadingNotificationId = await showNotification(
      '正在导出Cookie...',
      '请稍候，正在提取KOOK Cookie',
      'info'
    );
    
    // 1. 获取当前标签页
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // 2. 检查是否在KOOK网站
    if (!tab.url.includes('kookapp.cn')) {
      await clearNotification(loadingNotificationId);
      showNotification(
        '请在KOOK网站使用',
        '请先访问 www.kookapp.cn 并登录',
        'warning'
      );
      return;
    }
    
    // 3. 提取Cookie
    const cookies = await extractKookCookies();
    
    if (!cookies || cookies.length === 0) {
      await clearNotification(loadingNotificationId);
      showNotification(
        '未找到Cookie',
        '请先登录KOOK网站',
        'error'
      );
      return;
    }
    
    console.log(`[KOOK Extension] 提取到 ${cookies.length} 个Cookie`);
    
    // 4. 验证Cookie完整性
    const validation = validateCookies(cookies);
    if (!validation.valid) {
      await clearNotification(loadingNotificationId);
      showNotification(
        'Cookie不完整',
        validation.message,
        'warning'
      );
      return;
    }
    
    // 5. 检查系统连接状态
    const systemStatus = await checkSystemStatus();
    
    if (!systemStatus.online) {
      await clearNotification(loadingNotificationId);
      showNotification(
        '系统未运行',
        '请先启动KOOK消息转发系统',
        'error'
      );
      
      // 降级：复制到剪贴板
      await copyToClipboard(cookies);
      setTimeout(() => {
        showNotification(
          '已复制到剪贴板',
          'Cookie已复制，请手动粘贴到系统中',
          'info'
        );
      }, 2000);
      return;
    }
    
    // 6. 发送到本地系统
    const sendResult = await sendToLocalSystem(cookies);
    
    await clearNotification(loadingNotificationId);
    
    if (sendResult.success) {
      // 成功：显示成功通知
      showNotification(
        '✅ Cookie导入成功！',
        `已自动导入到账号：${sendResult.email || '未知'}`,
        'success',
        [
          { title: '查看详情', iconUrl: 'icons/icon-48.png' }
        ]
      );
      
      // 保存到本地存储（历史记录）
      await saveCookieHistory(cookies, sendResult);
      
      // 通过WebSocket通知
      notifyWebSocket({
        type: 'cookie_import_success',
        cookieCount: cookies.length,
        accountEmail: sendResult.email
      });
    } else {
      // 失败：降级到剪贴板
      await copyToClipboard(cookies);
      showNotification(
        '📋 已复制到剪贴板',
        sendResult.error || '请手动粘贴到设置页',
        'info'
      );
    }
    
  } catch (error) {
    console.error('[KOOK Extension] 错误:', error);
    showNotification(
      '导出失败',
      error.message || '发生未知错误',
      'error'
    );
  }
}

/**
 * 提取KOOK Cookie
 */
async function extractKookCookies() {
  try {
    const cookies = await chrome.cookies.getAll({ domain: KOOK_DOMAIN });
    
    // 优先提取关键Cookie
    const importantKeys = ['token', 'session', 'user_id', 'refresh_token', '_ga', '_gid'];
    const filtered = cookies.filter(cookie => 
      importantKeys.some(key => cookie.name.toLowerCase().includes(key.toLowerCase()))
    );
    
    // 如果关键Cookie不足，返回所有Cookie
    return filtered.length >= 2 ? filtered : cookies;
  } catch (error) {
    console.error('[KOOK Extension] 提取Cookie失败:', error);
    return [];
  }
}

/**
 * 验证Cookie完整性
 */
function validateCookies(cookies) {
  const requiredKeys = ['token'];  // 最低要求
  const recommendedKeys = ['token', 'session'];
  
  const foundKeys = cookies.map(c => c.name.toLowerCase());
  
  // 检查必需Cookie
  const missingRequired = requiredKeys.filter(key => 
    !foundKeys.some(name => name.includes(key))
  );
  
  if (missingRequired.length > 0) {
    return {
      valid: false,
      message: `缺少必需Cookie: ${missingRequired.join(', ')}`
    };
  }
  
  // 检查推荐Cookie
  const missingRecommended = recommendedKeys.filter(key => 
    !foundKeys.some(name => name.includes(key))
  );
  
  if (missingRecommended.length > 0) {
    return {
      valid: true,
      warning: `建议完整登录以获取更多Cookie: ${missingRecommended.join(', ')}`
    };
  }
  
  return { valid: true };
}

/**
 * 检查系统连接状态
 */
async function checkSystemStatus() {
  try {
    const response = await fetch(`${LOCAL_API_URL}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(2000)
    });
    
    if (response.ok) {
      const data = await response.json();
      return { online: true, status: data.status };
    }
    
    return { online: false, error: 'Health check failed' };
  } catch (error) {
    console.warn('[KOOK Extension] 无法连接到系统:', error);
    return { online: false, error: error.message };
  }
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
        source: 'chrome_extension_optimized',
        timestamp: Date.now(),
        browser: 'Chrome',
        version: chrome.runtime.getManifest().version
      }),
      signal: AbortSignal.timeout(5000)
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('[KOOK Extension] 发送成功:', data);
      return { 
        success: true, 
        data,
        email: data.email
      };
    } else {
      const errorData = await response.json().catch(() => ({}));
      console.warn('[KOOK Extension] 服务器返回错误:', response.status, errorData);
      return { 
        success: false, 
        error: errorData.message || `HTTP ${response.status}` 
      };
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
async function showNotification(title, message, type = 'info', buttons = []) {
  const iconMap = {
    success: 'icons/icon-128.png',
    error: 'icons/icon-128.png',
    warning: 'icons/icon-128.png',
    info: 'icons/icon-128.png'
  };
  
  return chrome.notifications.create({
    type: 'basic',
    iconUrl: iconMap[type],
    title: title,
    message: message,
    priority: 2,
    buttons: buttons
  });
}

/**
 * 清除通知
 */
async function clearNotification(notificationId) {
  try {
    await chrome.notifications.clear(notificationId);
  } catch (error) {
    console.error('[KOOK Extension] 清除通知失败:', error);
  }
}

/**
 * 保存Cookie历史记录
 */
async function saveCookieHistory(cookies, result) {
  try {
    const history = await chrome.storage.local.get('cookieHistory') || { cookieHistory: [] };
    const historyList = history.cookieHistory || [];
    
    // 添加新记录（最多保留20条）
    historyList.unshift({
      cookies: cookies.length,
      timestamp: Date.now(),
      domain: KOOK_DOMAIN,
      success: result.success,
      email: result.email || null
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

/**
 * 通过WebSocket通知
 */
function notifyWebSocket(data) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(data));
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
  
  if (request.action === 'checkSystemStatus') {
    checkSystemStatus().then(status => {
      sendResponse(status);
    });
    return true;
  }
});

// 启动时初始化WebSocket
initWebSocket();

console.log('[KOOK Extension] 后台服务已启动（深度优化版）');
