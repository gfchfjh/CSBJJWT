// ✅ P0-2: 浏览器扩展 - Popup脚本

let exportedCookies = null;

document.addEventListener('DOMContentLoaded', () => {
  const exportBtn = document.getElementById('exportBtn');
  const copyBtn = document.getElementById('copyBtn');
  const sendBtn = document.getElementById('sendBtn');
  const statusDiv = document.getElementById('status');
  const cookieInfoDiv = document.getElementById('cookieInfo');

  // 导出Cookie
  exportBtn.addEventListener('click', async () => {
    try {
      showStatus('正在导出Cookie...', 'warning');
      exportBtn.disabled = true;

      // 获取当前标签页
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

      // 检查是否在KOOK网站
      if (!tab.url.includes('kookapp.cn')) {
        showStatus('❌ 请在KOOK网页版页面使用此扩展', 'error');
        exportBtn.disabled = false;
        return;
      }

      // 获取所有KOOK相关的Cookie
      const cookies = await chrome.cookies.getAll({ 
        domain: '.kookapp.cn' 
      });

      if (!cookies || cookies.length === 0) {
        showStatus('❌ 未找到Cookie，请确保已登录KOOK', 'error');
        exportBtn.disabled = false;
        return;
      }

      // 格式化Cookie为JSON数组
      exportedCookies = cookies.map(cookie => ({
        name: cookie.name,
        value: cookie.value,
        domain: cookie.domain,
        path: cookie.path,
        expires: cookie.expirationDate,
        httpOnly: cookie.httpOnly,
        secure: cookie.secure,
        sameSite: cookie.sameSite || 'no_restriction'
      }));

      // 显示成功状态
      showStatus(`✅ 成功导出 ${cookies.length} 个Cookie`, 'success');
      
      // 显示Cookie信息
      cookieInfoDiv.style.display = 'block';
      cookieInfoDiv.innerHTML = `
        <div style="margin-bottom: 8px;">
          <span class="cookie-count">${cookies.length}</span> 个Cookie已导出
        </div>
        <div style="font-size: 11px; color: #999;">
          包含: ${cookies.map(c => c.name).slice(0, 3).join(', ')}${cookies.length > 3 ? '...' : ''}
        </div>
      `;

      // 显示操作按钮
      copyBtn.style.display = 'block';
      sendBtn.style.display = 'block';
      exportBtn.style.display = 'none';

    } catch (error) {
      console.error('导出Cookie失败:', error);
      showStatus('❌ 导出失败: ' + error.message, 'error');
      exportBtn.disabled = false;
    }
  });

  // 复制到剪贴板
  copyBtn.addEventListener('click', async () => {
    try {
      const jsonString = JSON.stringify(exportedCookies, null, 2);
      
      // 复制到剪贴板
      await navigator.clipboard.writeText(jsonString);
      
      showStatus('✅ 已复制到剪贴板！请粘贴到应用中', 'success');
      
      // 3秒后重置
      setTimeout(() => {
        resetUI();
      }, 3000);
      
    } catch (error) {
      console.error('复制失败:', error);
      showStatus('❌ 复制失败: ' + error.message, 'error');
    }
  });

  // 发送到应用
  sendBtn.addEventListener('click', async () => {
    try {
      showStatus('正在发送到应用...', 'warning');
      sendBtn.disabled = true;

      const jsonString = JSON.stringify(exportedCookies);

      // ✅ P0-2优化：通过本地HTTP发送到Electron应用
      const response = await fetch('http://localhost:9527/api/cookie-import/extension', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Extension-Version': '1.0.0',  // 扩展版本
        },
        body: JSON.stringify({
          cookies: exportedCookies,
          source: 'chrome-extension',
          auto_login: true,  // 自动登录
          timestamp: Date.now()
        })
      });

      if (response.ok) {
        showStatus('✅ 成功发送到应用！', 'success');
        
        // 3秒后重置
        setTimeout(() => {
          resetUI();
          window.close(); // 关闭弹窗
        }, 2000);
      } else {
        throw new Error('应用未响应，请确保应用正在运行');
      }

    } catch (error) {
      console.error('发送失败:', error);
      showStatus('❌ 发送失败: ' + error.message + '<br>请改用"复制到剪贴板"方式', 'error');
      sendBtn.disabled = false;
    }
  });
});

// 显示状态信息
function showStatus(message, type = 'success') {
  const statusDiv = document.getElementById('status');
  statusDiv.className = `status ${type}`;
  statusDiv.innerHTML = message;
  statusDiv.style.display = 'block';
}

// 重置UI
function resetUI() {
  const exportBtn = document.getElementById('exportBtn');
  const copyBtn = document.getElementById('copyBtn');
  const sendBtn = document.getElementById('sendBtn');
  const statusDiv = document.getElementById('status');
  const cookieInfoDiv = document.getElementById('cookieInfo');

  exportBtn.style.display = 'block';
  exportBtn.disabled = false;
  copyBtn.style.display = 'none';
  sendBtn.style.display = 'none';
  statusDiv.style.display = 'none';
  cookieInfoDiv.style.display = 'none';
  exportedCookies = null;
}
