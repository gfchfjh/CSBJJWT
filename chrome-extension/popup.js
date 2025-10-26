/**
 * KOOK Cookie 导出器 - Popup 脚本
 * 完善版 v2.0
 */

// 当前选择的格式
let selectedFormat = 'json';
let cookies = [];

// DOM元素
const elements = {
  exportBtn: document.getElementById('exportBtn'),
  copyBtn: document.getElementById('copyBtn'),
  downloadBtn: document.getElementById('downloadBtn'),
  sendToAppBtn: document.getElementById('sendToAppBtn'),
  result: document.getElementById('result'),
  statusIcon: document.getElementById('statusIcon'),
  statusText: document.getElementById('statusText'),
  cookieCount: document.getElementById('cookieCount'),
  exportCount: document.getElementById('exportCount'),
  formatButtons: document.querySelectorAll('.format-button')
};

// 初始化
async function init() {
  // 检查KOOK连接状态
  await checkKookStatus();
  
  // 加载统计信息
  await loadStats();
  
  // 绑定事件
  bindEvents();
  
  // 自动检测Cookie
  await detectCookies();
}

// 检查KOOK连接状态
async function checkKookStatus() {
  try {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    const currentTab = tabs[0];
    
    if (currentTab.url.includes('kookapp.cn') || currentTab.url.includes('kaiheila.cn')) {
      updateStatus('success', '✅', '已连接到KOOK');
    } else {
      updateStatus('warning', '⚠️', '请先打开KOOK网页');
    }
  } catch (error) {
    updateStatus('error', '❌', '检测失败');
  }
}

// 更新状态显示
function updateStatus(type, icon, text) {
  elements.statusIcon.textContent = icon;
  elements.statusText.textContent = text;
}

// 加载统计信息
async function loadStats() {
  try {
    const stats = await chrome.storage.local.get(['exportCount']);
    elements.exportCount.textContent = stats.exportCount || 0;
  } catch (error) {
    console.error('加载统计失败:', error);
  }
}

// 绑定事件
function bindEvents() {
  // 格式选择
  elements.formatButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      elements.formatButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selectedFormat = btn.dataset.format;
    });
  });
  
  // 导出按钮
  elements.exportBtn.addEventListener('click', exportCookies);
  
  // 复制按钮
  elements.copyBtn.addEventListener('click', copyToClipboard);
  
  // 下载按钮
  elements.downloadBtn.addEventListener('click', downloadAsFile);
  
  // 发送到应用按钮
  elements.sendToAppBtn.addEventListener('click', sendToApp);
}

// 自动检测Cookie
async function detectCookies() {
  try {
    cookies = await chrome.cookies.getAll({
      domain: '.kookapp.cn'
    });
    
    // 同时获取kaiheila.cn的Cookie
    const cookies2 = await chrome.cookies.getAll({
      domain: '.kaiheila.cn'
    });
    
    cookies = [...cookies, ...cookies2];
    elements.cookieCount.textContent = cookies.length;
    
    if (cookies.length > 0) {
      showMessage('success', `✅ 检测到 ${cookies.length} 个Cookie`);
    }
  } catch (error) {
    console.error('检测Cookie失败:', error);
    showMessage('error', '❌ 检测失败：' + error.message);
  }
}

// 导出Cookie
async function exportCookies() {
  try {
    elements.exportBtn.disabled = true;
    elements.exportBtn.innerHTML = '<span class="btn-icon">⏳</span>导出中...';
    
    // 获取最新Cookie
    await detectCookies();
    
    if (cookies.length === 0) {
      throw new Error('未找到Cookie，请确保已登录KOOK');
    }
    
    // 转换格式
    const formatted = formatCookies(cookies, selectedFormat);
    
    // 保存到storage
    await chrome.storage.local.set({ 
      lastExport: formatted,
      lastExportFormat: selectedFormat,
      lastExportTime: new Date().toISOString()
    });
    
    // 更新统计
    const stats = await chrome.storage.local.get(['exportCount']);
    const newCount = (stats.exportCount || 0) + 1;
    await chrome.storage.local.set({ exportCount: newCount });
    elements.exportCount.textContent = newCount;
    
    showMessage('success', `✅ 导出成功！共 ${cookies.length} 个Cookie`);
    
    // 启用其他按钮
    elements.copyBtn.disabled = false;
    elements.downloadBtn.disabled = false;
    elements.sendToAppBtn.disabled = false;
    
  } catch (error) {
    console.error('导出失败:', error);
    showMessage('error', '❌ 导出失败：' + error.message);
  } finally {
    elements.exportBtn.disabled = false;
    elements.exportBtn.innerHTML = '<span class="btn-icon">⬇️</span>一键导出Cookie';
  }
}

// 格式化Cookie
function formatCookies(cookies, format) {
  switch (format) {
    case 'json':
      // JSON数组格式（最常用）
      return JSON.stringify(cookies, null, 2);
    
    case 'json-object':
      // JSON对象格式 {name: value}
      const obj = {};
      cookies.forEach(c => {
        obj[c.name] = c.value;
      });
      return JSON.stringify(obj, null, 2);
    
    case 'netscape':
      // Netscape Cookie格式
      let netscape = '# Netscape HTTP Cookie File\n';
      cookies.forEach(c => {
        netscape += `${c.domain}\t`;
        netscape += `TRUE\t`;
        netscape += `${c.path}\t`;
        netscape += `${c.secure ? 'TRUE' : 'FALSE'}\t`;
        netscape += `${Math.floor(c.expirationDate || Date.now() / 1000 + 86400)}\t`;
        netscape += `${c.name}\t`;
        netscape += `${c.value}\n`;
      });
      return netscape;
    
    case 'header':
      // HTTP Header格式
      return cookies.map(c => `${c.name}=${c.value}`).join('; ');
    
    default:
      return JSON.stringify(cookies, null, 2);
  }
}

// 复制到剪贴板
async function copyToClipboard() {
  try {
    const data = await chrome.storage.local.get(['lastExport']);
    if (!data.lastExport) {
      throw new Error('请先导出Cookie');
    }
    
    await navigator.clipboard.writeText(data.lastExport);
    showMessage('success', '✅ 已复制到剪贴板！');
    
    // 通知
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon-128.png',
      title: 'Cookie已复制',
      message: '已复制到剪贴板，可以直接粘贴到应用中'
    });
  } catch (error) {
    showMessage('error', '❌ 复制失败：' + error.message);
  }
}

// 下载为文件
async function downloadAsFile() {
  try {
    const data = await chrome.storage.local.get(['lastExport', 'lastExportFormat']);
    if (!data.lastExport) {
      throw new Error('请先导出Cookie');
    }
    
    const format = data.lastExportFormat || 'json';
    const extension = format === 'netscape' ? 'txt' : 
                     format === 'header' ? 'txt' : 'json';
    const filename = `kook-cookies-${Date.now()}.${extension}`;
    
    // 创建Blob
    const blob = new Blob([data.lastExport], { 
      type: 'text/plain;charset=utf-8' 
    });
    
    // 下载
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    
    showMessage('success', `✅ 已下载：${filename}`);
  } catch (error) {
    showMessage('error', '❌ 下载失败：' + error.message);
  }
}

// 发送到应用
async function sendToApp() {
  try {
    const data = await chrome.storage.local.get(['lastExport']);
    if (!data.lastExport) {
      throw new Error('请先导出Cookie');
    }
    
    elements.sendToAppBtn.disabled = true;
    elements.sendToAppBtn.innerHTML = '<span class="btn-icon">⏳</span>发送中...';
    
    // 尝试连接本地应用（默认端口9527）
    const response = await fetch('http://localhost:9527/api/cookie/import', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        cookie: data.lastExport,
        source: 'chrome_extension'
      })
    });
    
    if (response.ok) {
      const result = await response.json();
      showMessage('success', '🚀 发送成功！应用已收到Cookie');
      
      // 通知
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon-128.png',
        title: '发送成功',
        message: 'Cookie已发送到KOOK消息转发系统'
      });
    } else {
      throw new Error('应用返回错误：' + response.status);
    }
  } catch (error) {
    console.error('发送失败:', error);
    showMessage('error', '❌ 发送失败：' + error.message + '\n\n请确保应用正在运行（端口9527）');
  } finally {
    elements.sendToAppBtn.disabled = false;
    elements.sendToAppBtn.innerHTML = '<span class="btn-icon">🚀</span>发送到应用';
  }
}

// 显示消息
function showMessage(type, text) {
  elements.result.textContent = text;
  elements.result.className = `result show ${type}`;
  
  // 3秒后自动隐藏
  setTimeout(() => {
    elements.result.classList.remove('show');
  }, 3000);
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', init);
