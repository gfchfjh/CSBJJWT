/**
 * KOOK Cookie导出助手 - 弹窗脚本（完整版）
 * v17.0.0深度优化：完善的Cookie导出功能
 */

const LOCAL_API_URL = 'http://localhost:9527';
const KOOK_DOMAIN = '.kookapp.cn';

// 全局状态
let currentCookies = [];
let isSystemOnline = false;

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
  console.log('[KOOK Extension] 弹窗已加载');
  
  // 绑定事件
  document.getElementById('autoExportBtn').addEventListener('click', handleAutoExport);
  document.getElementById('copyBtn').addEventListener('click', handleCopyToClipboard);
  document.getElementById('downloadBtn').addEventListener('click', handleDownloadJSON);
  document.getElementById('refreshBtn').addEventListener('click', refreshStatus);
  document.getElementById('tutorialLink').addEventListener('click', openTutorial);
  document.getElementById('settingsLink').addEventListener('click', openSettings);
  
  // 初始检测
  await refreshStatus();
  
  // 加载历史记录
  await loadHistory();
});

/**
 * 刷新状态
 */
async function refreshStatus() {
  try {
    showMessage('正在检测...', 'info');
    
    // 1. 检查当前标签页
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab.url.includes('kookapp.cn')) {
      updateStatus(false, '请访问KOOK网站');
      document.getElementById('cookieCount').textContent = '未在KOOK网站';
      hideMessage();
      return;
    }
    
    // 2. 提取Cookie
    currentCookies = await extractKookCookies();
    
    if (currentCookies.length === 0) {
      updateStatus(false, '未检测到Cookie');
      document.getElementById('cookieCount').textContent = '请先登录';
      showMessage('未检测到Cookie，请先登录KOOK网站', 'error');
      return;
    }
    
    // 3. 显示Cookie信息
    displayCookieInfo(currentCookies);
    
    // 4. 检测本地系统
    isSystemOnline = await checkLocalSystem();
    
    if (isSystemOnline) {
      updateStatus(true, '本地系统在线');
      showMessage(`检测成功！找到 ${currentCookies.length} 个Cookie`, 'success');
    } else {
      updateStatus(false, '本地系统离线');
      showMessage('Cookie已就绪，但本地系统未启动（可手动复制）', 'info');
    }
    
    // 隐藏消息
    setTimeout(hideMessage, 3000);
    
  } catch (error) {
    console.error('[KOOK Extension] 刷新状态失败:', error);
    showMessage('刷新状态失败: ' + error.message, 'error');
  }
}

/**
 * 提取KOOK Cookie
 */
async function extractKookCookies() {
  try {
    const cookies = await chrome.cookies.getAll({ domain: KOOK_DOMAIN });
    
    // 重要Cookie键名
    const importantKeys = [
      'token', 'session', 'user_id', 'sid', 'uid',
      'auth', 'jwt', 'access_token', 'refresh_token'
    ];
    
    // 优先返回重要Cookie
    const important = cookies.filter(cookie =>
      importantKeys.some(key => cookie.name.toLowerCase().includes(key.toLowerCase()))
    );
    
    // 如果有重要Cookie，返回所有Cookie（包括GA等）
    return important.length > 0 ? cookies : [];
    
  } catch (error) {
    console.error('[KOOK Extension] 提取Cookie失败:', error);
    return [];
  }
}

/**
 * 显示Cookie信息
 */
function displayCookieInfo(cookies) {
  const cookieInfo = document.getElementById('cookieInfo');
  const cookieList = document.getElementById('cookieList');
  const cookieCount = document.getElementById('cookieCount');
  
  if (cookies.length === 0) {
    cookieInfo.style.display = 'none';
    return;
  }
  
  cookieInfo.style.display = 'block';
  cookieCount.textContent = `${cookies.length} 个Cookie`;
  
  // 显示前5个重要Cookie
  const displayCookies = cookies.slice(0, 5);
  
  cookieList.innerHTML = displayCookies.map(cookie => `
    <div class="cookie-item">
      <span class="cookie-key">${cookie.name}</span>
      <span class="cookie-value">${cookie.value.substring(0, 20)}...</span>
    </div>
  `).join('');
  
  if (cookies.length > 5) {
    cookieList.innerHTML += `
      <div class="cookie-item">
        <span class="cookie-key">...</span>
        <span class="cookie-value">还有 ${cookies.length - 5} 个</span>
      </div>
    `;
  }
}

/**
 * 检测本地系统
 */
async function checkLocalSystem() {
  try {
    const response = await fetch(`${LOCAL_API_URL}/api/health`, {
      method: 'GET',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      signal: AbortSignal.timeout(2000) // 2秒超时
    });
    
    return response.ok;
  } catch (error) {
    return false;
  }
}

/**
 * 一键自动导出
 */
async function handleAutoExport() {
  if (currentCookies.length === 0) {
    showMessage('未检测到Cookie，请刷新状态', 'error');
    return;
  }
  
  const btn = document.getElementById('autoExportBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="loading"></span><span>导出中...</span>';
  
  try {
    if (isSystemOnline) {
      // 尝试自动发送
      const result = await sendToLocalSystem(currentCookies);
      
      if (result.success) {
        showMessage('✅ Cookie已自动导入到系统！', 'success');
        await saveHistory('auto', true);
      } else {
        throw new Error(result.error || '导入失败');
      }
    } else {
      // 系统离线，复制到剪贴板
      await copyToClipboard(currentCookies);
      showMessage('📋 系统离线，已复制到剪贴板。请在系统设置中手动粘贴', 'info');
      await saveHistory('clipboard', true);
    }
  } catch (error) {
    console.error('[KOOK Extension] 自动导出失败:', error);
    showMessage('导出失败: ' + error.message, 'error');
    await saveHistory('auto', false, error.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span class="btn-icon">🚀</span><span>一键导出并自动导入</span>';
  }
}

/**
 * 复制到剪贴板
 */
async function handleCopyToClipboard() {
  if (currentCookies.length === 0) {
    showMessage('未检测到Cookie，请刷新状态', 'error');
    return;
  }
  
  try {
    await copyToClipboard(currentCookies);
    showMessage('✅ Cookie已复制到剪贴板！', 'success');
    await saveHistory('clipboard', true);
  } catch (error) {
    showMessage('复制失败: ' + error.message, 'error');
  }
}

/**
 * 下载JSON文件
 */
async function handleDownloadJSON() {
  if (currentCookies.length === 0) {
    showMessage('未检测到Cookie，请刷新状态', 'error');
    return;
  }
  
  try {
    const cookieData = {
      domain: KOOK_DOMAIN,
      exported_at: new Date().toISOString(),
      cookies: currentCookies.map(cookie => ({
        name: cookie.name,
        value: cookie.value,
        domain: cookie.domain,
        path: cookie.path,
        secure: cookie.secure,
        httpOnly: cookie.httpOnly,
        expirationDate: cookie.expirationDate
      }))
    };
    
    const blob = new Blob([JSON.stringify(cookieData, null, 2)], {
      type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const filename = `kook-cookies-${Date.now()}.json`;
    
    // 使用Chrome下载API
    chrome.downloads.download({
      url: url,
      filename: filename,
      saveAs: true
    });
    
    showMessage('✅ Cookie文件已保存！', 'success');
    await saveHistory('download', true);
    
  } catch (error) {
    showMessage('下载失败: ' + error.message, 'error');
  }
}

/**
 * 发送到本地系统
 */
async function sendToLocalSystem(cookies) {
  try {
    const response = await fetch(`${LOCAL_API_URL}/api/cookie-import/import`, {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        cookies: cookies.map(c => ({
          name: c.name,
          value: c.value,
          domain: c.domain,
          path: c.path,
          secure: c.secure,
          httpOnly: c.httpOnly,
          expirationDate: c.expirationDate
        })),
        source: 'chrome-extension',
        imported_at: new Date().toISOString()
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      return { success: true, data };
    } else {
      const error = await response.text();
      return { success: false, error };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * 复制到剪贴板
 */
async function copyToClipboard(cookies) {
  const cookieText = JSON.stringify(cookies, null, 2);
  await navigator.clipboard.writeText(cookieText);
}

/**
 * 保存历史记录
 */
async function saveHistory(method, success, error = null) {
  const history = await chrome.storage.local.get('exportHistory') || { exportHistory: [] };
  const historyList = history.exportHistory || [];
  
  historyList.unshift({
    timestamp: Date.now(),
    method,
    success,
    error,
    cookieCount: currentCookies.length
  });
  
  // 只保留最近10条
  if (historyList.length > 10) {
    historyList.length = 10;
  }
  
  await chrome.storage.local.set({ exportHistory: historyList });
  await loadHistory();
}

/**
 * 加载历史记录
 */
async function loadHistory() {
  const result = await chrome.storage.local.get('exportHistory');
  const historyList = result.exportHistory || [];
  
  if (historyList.length === 0) {
    document.getElementById('history').style.display = 'none';
    return;
  }
  
  document.getElementById('history').style.display = 'block';
  
  const historyHTML = historyList.slice(0, 3).map(item => {
    const time = new Date(item.timestamp).toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
    
    const methodText = {
      auto: '自动导入',
      clipboard: '剪贴板',
      download: '下载文件'
    }[item.method] || item.method;
    
    const badge = item.success
      ? '<span class="history-badge success">成功</span>'
      : '<span class="history-badge failed">失败</span>';
    
    return `
      <div class="history-item">
        <div>
          <div>${methodText} · ${item.cookieCount}个</div>
          <div class="history-time">${time}</div>
        </div>
        ${badge}
      </div>
    `;
  }).join('');
  
  document.getElementById('historyList').innerHTML = historyHTML;
}

/**
 * 更新状态显示
 */
function updateStatus(online, text) {
  const indicator = document.getElementById('statusIndicator');
  const statusText = document.getElementById('statusText');
  
  if (online) {
    indicator.classList.add('online');
    indicator.classList.remove('offline');
  } else {
    indicator.classList.add('offline');
    indicator.classList.remove('online');
  }
  
  statusText.textContent = text;
}

/**
 * 显示消息
 */
function showMessage(text, type = 'info') {
  const message = document.getElementById('message');
  message.textContent = text;
  message.className = `message ${type} show`;
}

/**
 * 隐藏消息
 */
function hideMessage() {
  const message = document.getElementById('message');
  message.classList.remove('show');
}

/**
 * 打开教程
 */
function openTutorial(e) {
  e.preventDefault();
  chrome.tabs.create({
    url: 'https://github.com/gfchfjh/CSBJJWT/blob/main/docs/tutorials/chrome-extension-installation.md'
  });
}

/**
 * 打开设置
 */
function openSettings(e) {
  e.preventDefault();
  window.open('http://localhost:9527/', '_blank');
}
