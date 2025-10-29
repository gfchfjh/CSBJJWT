/**
 * KOOK Cookie导出扩展 - Popup脚本（增强版）
 */

// DOM元素
const exportBtn = document.getElementById('exportBtn');
const systemStatus = document.getElementById('systemStatus');
const historyList = document.getElementById('historyList');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');
const methodButtons = document.querySelectorAll('.method-btn');
const helpLink = document.getElementById('helpLink');
const feedbackLink = document.getElementById('feedbackLink');

// 当前导出方式
let exportMethod = 'auto';

// ========== 初始化 ==========

document.addEventListener('DOMContentLoaded', () => {
  checkSystemStatus();
  loadHistory();
  setupEventListeners();
});

// ========== 系统状态检查 ==========

async function checkSystemStatus() {
  try {
    const response = await chrome.runtime.sendMessage({
      action: 'checkSystemStatus'
    });

    updateSystemStatus(response.running);
  } catch (error) {
    console.error('检查系统状态失败:', error);
    updateSystemStatus(false);
  }
}

function updateSystemStatus(isRunning) {
  const dot = systemStatus.querySelector('.status-dot');
  const text = systemStatus.querySelector('.status-text');

  if (isRunning) {
    dot.className = 'status-dot online';
    text.textContent = '✅ 系统运行中 - 可自动导入';
  } else {
    dot.className = 'status-dot offline';
    text.textContent = '❌ 系统未运行 - 将复制到剪贴板';
    
    // 如果系统未运行，强制切换到剪贴板模式
    if (exportMethod === 'auto') {
      exportMethod = 'clipboard';
      updateMethodButtons();
    }
  }
}

// ========== 事件监听 ==========

function setupEventListeners() {
  // 导出按钮
  exportBtn.addEventListener('click', handleExport);

  // 导出方式切换
  methodButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      exportMethod = btn.dataset.method;
      updateMethodButtons();
    });
  });

  // 清空历史
  clearHistoryBtn.addEventListener('click', handleClearHistory);

  // 帮助链接
  helpLink.addEventListener('click', (e) => {
    e.preventDefault();
    chrome.tabs.create({
      url: 'https://github.com/gfchfjh/CSBJJWT/blob/main/docs/tutorials/02-Cookie获取详细教程.md'
    });
  });

  // 反馈链接
  feedbackLink.addEventListener('click', (e) => {
    e.preventDefault();
    chrome.tabs.create({
      url: 'https://github.com/gfchfjh/CSBJJWT/issues'
    });
  });
}

function updateMethodButtons() {
  methodButtons.forEach(btn => {
    if (btn.dataset.method === exportMethod) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
}

// ========== 导出Cookie ==========

async function handleExport() {
  // 禁用按钮
  exportBtn.disabled = true;
  exportBtn.innerHTML = '<div class="spinner"></div><span>导出中...</span>';

  try {
    // 发送导出请求到后台脚本
    const response = await chrome.runtime.sendMessage({
      action: 'exportCookies'
    });

    if (response.success) {
      // 导出成功
      showSuccess(response);
      
      // 刷新历史记录
      await loadHistory();
      
      // 重新检查系统状态
      await checkSystemStatus();
    } else {
      // 导出失败
      showError(response.error || '导出失败');
    }
  } catch (error) {
    console.error('导出Cookie失败:', error);
    showError(error.message);
  } finally {
    // 恢复按钮
    exportBtn.disabled = false;
    exportBtn.innerHTML = '<span>🚀</span><span>一键导出Cookie</span>';
  }
}

function showSuccess(response) {
  const message = response.method === 'auto' 
    ? '✅ Cookie已自动导入到系统！'
    : '📋 Cookie已复制到剪贴板！\n请在系统中手动粘贴导入。';
  
  // 临时改变按钮文本
  exportBtn.innerHTML = `<span>✅</span><span>${message.split('\n')[0]}</span>`;
  exportBtn.style.background = 'linear-gradient(135deg, #67c23a 0%, #5daf34 100%)';
  
  setTimeout(() => {
    exportBtn.innerHTML = '<span>🚀</span><span>一键导出Cookie</span>';
    exportBtn.style.background = '';
  }, 3000);
}

function showError(message) {
  exportBtn.innerHTML = `<span>❌</span><span>导出失败</span>`;
  exportBtn.style.background = 'linear-gradient(135deg, #f56c6c 0%, #f44336 100%)';
  
  setTimeout(() => {
    exportBtn.innerHTML = '<span>🚀</span><span>一键导出Cookie</span>';
    exportBtn.style.background = '';
  }, 3000);
  
  console.error('导出错误:', message);
}

// ========== 历史记录 ==========

async function loadHistory() {
  try {
    const response = await chrome.runtime.sendMessage({
      action: 'getHistory'
    });

    if (response.success && response.history.length > 0) {
      renderHistory(response.history);
    } else {
      historyList.innerHTML = '<div class="empty-history">暂无导出记录</div>';
    }
  } catch (error) {
    console.error('加载历史记录失败:', error);
  }
}

function renderHistory(history) {
  historyList.innerHTML = history.map(item => {
    const time = new Date(item.timestamp).toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
    
    const methodClass = item.method === 'auto' ? 'auto' : 'clipboard';
    const methodText = item.method === 'auto' ? '自动导入' : '剪贴板';
    
    return `
      <div class="history-item">
        <div class="time">${time}</div>
        <span class="method ${methodClass}">${methodText}</span>
        <span>${item.cookieCount} 个Cookie</span>
      </div>
    `;
  }).join('');
}

async function handleClearHistory() {
  if (!confirm('确定要清空所有导出记录吗？')) {
    return;
  }

  try {
    await chrome.runtime.sendMessage({
      action: 'clearHistory'
    });

    historyList.innerHTML = '<div class="empty-history">暂无导出记录</div>';
  } catch (error) {
    console.error('清空历史失败:', error);
  }
}

// ========== 定时刷新系统状态 ==========

setInterval(checkSystemStatus, 10000); // 每10秒检查一次
