/**
 * KOOK Cookie导入 - Popup界面脚本
 */

const exportBtn = document.getElementById('exportBtn');
const statusDiv = document.getElementById('status');
const historyDiv = document.getElementById('history');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
  loadHistory();
  checkKookPage();
});

// 导出Cookie按钮点击
exportBtn.addEventListener('click', async () => {
  try {
    // 禁用按钮并显示加载状态
    exportBtn.disabled = true;
    exportBtn.innerHTML = '<div class="spinner"></div><span>导出中...</span>';
    
    // 发送消息给background
    const response = await chrome.runtime.sendMessage({ action: 'exportCookie' });
    
    if (response.success) {
      showStatus('success', '✅ Cookie导出成功！已自动发送到本地系统');
      loadHistory(); // 刷新历史记录
    } else {
      showStatus('error', '❌ 导出失败: ' + (response.error || '未知错误'));
    }
  } catch (error) {
    showStatus('error', '❌ 操作失败: ' + error.message);
  } finally {
    // 恢复按钮状态
    exportBtn.disabled = false;
    exportBtn.innerHTML = '<span>🚀</span><span>一键导出Cookie</span>';
  }
});

// 清空历史记录
clearHistoryBtn.addEventListener('click', async () => {
  if (confirm('确定要清空所有导出历史吗？')) {
    await chrome.storage.local.set({ cookieHistory: [] });
    loadHistory();
    showStatus('info', 'ℹ️ 历史记录已清空');
  }
});

/**
 * 显示状态消息
 */
function showStatus(type, message) {
  statusDiv.className = `status ${type} show`;
  statusDiv.textContent = message;
  
  // 3秒后自动隐藏
  setTimeout(() => {
    statusDiv.classList.remove('show');
  }, 3000);
}

/**
 * 加载导出历史
 */
async function loadHistory() {
  try {
    const response = await chrome.runtime.sendMessage({ action: 'getHistory' });
    const history = response.history || [];
    
    if (history.length === 0) {
      historyDiv.innerHTML = '<div class="history-empty">暂无导出记录</div>';
      clearHistoryBtn.disabled = true;
      return;
    }
    
    clearHistoryBtn.disabled = false;
    
    historyDiv.innerHTML = history.map(item => {
      const date = new Date(item.timestamp);
      const timeStr = date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
      
      return `
        <div class="history-item">
          <span>${timeStr}</span>
          <span>${item.cookies} 个Cookie</span>
        </div>
      `;
    }).join('');
  } catch (error) {
    console.error('加载历史失败:', error);
  }
}

/**
 * 检查当前是否在KOOK页面
 */
async function checkKookPage() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab.url.includes('kookapp.cn')) {
      showStatus('info', 'ℹ️ 请在KOOK网站（www.kookapp.cn）使用此扩展');
      exportBtn.disabled = true;
      exportBtn.innerHTML = '<span>⚠️</span><span>请访问KOOK网站</span>';
    }
  } catch (error) {
    console.error('检查页面失败:', error);
  }
}
