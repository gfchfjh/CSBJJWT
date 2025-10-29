/**
 * KOOK Cookie导出扩展 - 增强版后台脚本
 * 支持自动POST到本地系统
 */

// 配置
const CONFIG = {
  API_URL: 'http://localhost:9527/api/cookie/import',
  KOOK_DOMAINS: [
    'www.kookapp.cn',
    'kookapp.cn',
    '.kookapp.cn'
  ],
  REQUIRED_COOKIES: ['token', 'session', 'user_id'],
  TIMEOUT: 10000, // 10秒超时
  RETRY_TIMES: 2 // 重试次数
};

/**
 * 提取KOOK Cookie
 */
async function extractKookCookies() {
  const cookies = [];
  
  for (const domain of CONFIG.KOOK_DOMAINS) {
    const domainCookies = await chrome.cookies.getAll({ domain });
    cookies.push(...domainCookies);
  }
  
  // 去重
  const uniqueCookies = Array.from(
    new Map(cookies.map(c => [c.name, c])).values()
  );
  
  return uniqueCookies;
}

/**
 * 验证Cookie完整性
 */
function validateCookies(cookies) {
  const cookieNames = cookies.map(c => c.name);
  const missingCookies = CONFIG.REQUIRED_COOKIES.filter(
    name => !cookieNames.includes(name)
  );
  
  if (missingCookies.length > 0) {
    return {
      valid: false,
      missing: missingCookies,
      message: `缺少必要的Cookie: ${missingCookies.join(', ')}`
    };
  }
  
  // 检查Cookie是否过期
  const now = Date.now() / 1000;
  const expiredCookies = cookies.filter(c => 
    c.expirationDate && c.expirationDate < now
  );
  
  if (expiredCookies.length > 0) {
    return {
      valid: false,
      expired: expiredCookies.map(c => c.name),
      message: '部分Cookie已过期，请重新登录KOOK'
    };
  }
  
  return {
    valid: true,
    message: 'Cookie验证通过'
  };
}

/**
 * 自动发送Cookie到本地系统
 */
async function sendCookiesToLocalSystem(cookies, retryCount = 0) {
  try {
    console.log('正在发送Cookie到本地系统...');
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUT);
    
    const response = await fetch(CONFIG.API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        cookies: cookies,
        source: 'chrome_extension',
        timestamp: Date.now(),
        version: chrome.runtime.getManifest().version
      }),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (result.success) {
      console.log('✅ Cookie自动导入成功');
      return {
        success: true,
        method: 'auto',
        message: 'Cookie已自动导入到系统'
      };
    } else {
      throw new Error(result.error || '导入失败');
    }
    
  } catch (error) {
    console.error('发送Cookie失败:', error);
    
    // 判断是否为连接错误
    const isConnectionError = 
      error.name === 'AbortError' ||
      error.message.includes('Failed to fetch') ||
      error.message.includes('NetworkError');
    
    // 如果是连接错误且还有重试次数，则重试
    if (isConnectionError && retryCount < CONFIG.RETRY_TIMES) {
      console.log(`重试中... (${retryCount + 1}/${CONFIG.RETRY_TIMES})`);
      await new Promise(resolve => setTimeout(resolve, 1000)); // 等待1秒
      return sendCookiesToLocalSystem(cookies, retryCount + 1);
    }
    
    // 降级处理：复制到剪贴板
    return {
      success: false,
      method: 'clipboard',
      error: error.message,
      message: '系统未运行，已复制到剪贴板'
    };
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
    console.log('✅ Cookie已复制到剪贴板');
    return true;
  } catch (error) {
    console.error('复制到剪贴板失败:', error);
    
    // 降级方案：使用传统方法
    const textarea = document.createElement('textarea');
    textarea.value = cookieJson;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    
    try {
      document.execCommand('copy');
      document.body.removeChild(textarea);
      console.log('✅ Cookie已复制到剪贴板（降级方案）');
      return true;
    } catch (e) {
      document.body.removeChild(textarea);
      console.error('降级方案也失败:', e);
      return false;
    }
  }
}

/**
 * 显示通知
 */
function showNotification(title, message, type = 'success') {
  const iconUrl = type === 'success' 
    ? 'icons/icon-128.png' 
    : 'icons/icon-error-128.png';
  
  chrome.notifications.create({
    type: 'basic',
    iconUrl: iconUrl,
    title: title,
    message: message,
    priority: 2
  });
}

/**
 * 导出Cookie（主函数）
 */
async function exportCookies() {
  try {
    // 1. 提取Cookie
    console.log('正在提取KOOK Cookie...');
    const cookies = await extractKookCookies();
    
    if (cookies.length === 0) {
      throw new Error('未找到KOOK Cookie，请先登录 www.kookapp.cn');
    }
    
    console.log(`找到 ${cookies.length} 个Cookie`);
    
    // 2. 验证Cookie
    const validation = validateCookies(cookies);
    
    if (!validation.valid) {
      throw new Error(validation.message);
    }
    
    console.log('Cookie验证通过');
    
    // 3. 尝试自动发送到本地系统
    const sendResult = await sendCookiesToLocalSystem(cookies);
    
    if (sendResult.success) {
      // 自动导入成功
      showNotification(
        '✅ Cookie导入成功',
        'Cookie已自动导入到KOOK消息转发系统',
        'success'
      );
      
      // 保存导出记录
      await saveExportHistory({
        timestamp: Date.now(),
        method: 'auto',
        cookieCount: cookies.length,
        success: true
      });
      
      return {
        success: true,
        method: 'auto',
        cookies: cookies
      };
      
    } else {
      // 自动导入失败，降级到剪贴板
      console.log('降级处理：复制到剪贴板');
      
      const copied = await copyToClipboard(cookies);
      
      if (copied) {
        showNotification(
          '📋 已复制到剪贴板',
          '系统未运行，Cookie已复制到剪贴板。\n请启动系统后手动粘贴导入。',
          'info'
        );
        
        // 保存导出记录
        await saveExportHistory({
          timestamp: Date.now(),
          method: 'clipboard',
          cookieCount: cookies.length,
          success: true
        });
        
        return {
          success: true,
          method: 'clipboard',
          cookies: cookies,
          copied: true
        };
      } else {
        throw new Error('复制到剪贴板失败');
      }
    }
    
  } catch (error) {
    console.error('导出Cookie失败:', error);
    
    showNotification(
      '❌ 导出失败',
      error.message,
      'error'
    );
    
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * 保存导出历史记录
 */
async function saveExportHistory(record) {
  const { history = [] } = await chrome.storage.local.get('history');
  
  // 保留最近20条记录
  const newHistory = [record, ...history].slice(0, 20);
  
  await chrome.storage.local.set({ history: newHistory });
}

/**
 * 获取导出历史
 */
async function getExportHistory() {
  const { history = [] } = await chrome.storage.local.get('history');
  return history;
}

/**
 * 清空历史记录
 */
async function clearHistory() {
  await chrome.storage.local.remove('history');
  return { success: true };
}

// ========== 消息监听 ==========

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('收到消息:', request);
  
  if (request.action === 'exportCookies') {
    // 异步处理
    exportCookies().then(result => {
      sendResponse(result);
    });
    return true; // 保持消息通道打开
  }
  
  if (request.action === 'getHistory') {
    getExportHistory().then(history => {
      sendResponse({ success: true, history });
    });
    return true;
  }
  
  if (request.action === 'clearHistory') {
    clearHistory().then(result => {
      sendResponse(result);
    });
    return true;
  }
  
  if (request.action === 'checkSystemStatus') {
    // 检查本地系统是否运行
    fetch(CONFIG.API_URL.replace('/cookie/import', '/health'), {
      method: 'GET',
      signal: AbortSignal.timeout(3000)
    })
      .then(response => response.json())
      .then(data => {
        sendResponse({
          success: true,
          running: data.status === 'healthy'
        });
      })
      .catch(error => {
        sendResponse({
          success: false,
          running: false,
          error: error.message
        });
      });
    return true;
  }
});

// ========== 右键菜单 ==========

chrome.runtime.onInstalled.addListener(() => {
  // 创建右键菜单项
  chrome.contextMenus.create({
    id: 'export-cookies',
    title: '导出KOOK Cookie',
    contexts: ['page'],
    documentUrlPatterns: [
      'https://www.kookapp.cn/*',
      'https://kookapp.cn/*'
    ]
  });
  
  console.log('KOOK Cookie导出扩展已安装');
});

// 右键菜单点击事件
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'export-cookies') {
    exportCookies();
  }
});

// ========== 快捷键 ==========

chrome.commands.onCommand.addListener((command) => {
  if (command === 'export-cookies') {
    exportCookies();
  }
});

// ========== 图标点击（触发Popup）==========

chrome.action.onClicked.addListener((tab) => {
  // Popup会自动打开，这里不需要额外处理
  console.log('扩展图标被点击');
});

console.log('KOOK Cookie导出扩展 - 增强版已加载');
