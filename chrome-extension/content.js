// ✅ P0-2: 浏览器扩展 - Content脚本

// 检测应用是否在运行
async function checkAppRunning() {
  try {
    const response = await fetch('http://localhost:9527/health', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    return response.ok;
  } catch (error) {
    return false;
  }
}

// 在页面加载完成后，检查应用状态
window.addEventListener('load', async () => {
  const appRunning = await checkAppRunning();
  
  if (appRunning) {
    console.log('✅ KOOK消息转发系统正在运行');
    
    // 可以在页面上显示一个提示
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 15px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      z-index: 10000;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 14px;
      cursor: pointer;
      transition: all 0.3s ease;
    `;
    notification.innerHTML = `
      <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 20px;">🚀</span>
        <div>
          <div style="font-weight: bold;">KOOK消息转发系统</div>
          <div style="font-size: 12px; opacity: 0.9;">点击导出Cookie</div>
        </div>
      </div>
    `;
    
    notification.addEventListener('click', () => {
      // 触发扩展弹窗
      chrome.runtime.sendMessage({ action: 'openPopup' });
    });
    
    notification.addEventListener('mouseenter', () => {
      notification.style.transform = 'translateY(-2px)';
      notification.style.boxShadow = '0 6px 16px rgba(0, 0, 0, 0.2)';
    });
    
    notification.addEventListener('mouseleave', () => {
      notification.style.transform = 'translateY(0)';
      notification.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
    });
    
    document.body.appendChild(notification);
    
    // 5秒后淡出
    setTimeout(() => {
      notification.style.opacity = '0';
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, 5000);
  }
});
