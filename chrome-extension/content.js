/**
 * KOOK Cookie 导出器 - Content Script
 * 注入到KOOK页面，提供快捷导出功能
 */

(function() {
  'use strict';
  
  // 避免重复注入
  if (window.__KOOK_COOKIE_EXPORTER_LOADED__) {
    return;
  }
  window.__KOOK_COOKIE_EXPORTER_LOADED__ = true;
  
  console.log('🍪 KOOK Cookie导出器已加载');
  
  // 创建浮动按钮
  function createFloatingButton() {
    const button = document.createElement('div');
    button.id = 'kook-cookie-export-btn';
    button.innerHTML = `
      <style>
        #kook-cookie-export-btn {
          position: fixed;
          bottom: 20px;
          right: 20px;
          width: 60px;
          height: 60px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 50%;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
          cursor: pointer;
          z-index: 999999;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 28px;
          transition: all 0.3s;
          animation: pulse 2s infinite;
        }
        
        #kook-cookie-export-btn:hover {
          transform: scale(1.1);
          box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
        }
        
        #kook-cookie-export-btn:active {
          transform: scale(0.95);
        }
        
        @keyframes pulse {
          0%, 100% {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
          }
          50% {
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.6);
          }
        }
        
        #kook-cookie-export-tooltip {
          position: absolute;
          bottom: 70px;
          right: 0;
          background: rgba(0, 0, 0, 0.9);
          color: white;
          padding: 8px 12px;
          border-radius: 8px;
          font-size: 13px;
          white-space: nowrap;
          opacity: 0;
          pointer-events: none;
          transition: opacity 0.3s;
        }
        
        #kook-cookie-export-btn:hover #kook-cookie-export-tooltip {
          opacity: 1;
        }
      </style>
      <span>🍪</span>
      <div id="kook-cookie-export-tooltip">点击导出Cookie</div>
    `;
    
    button.addEventListener('click', handleExport);
    document.body.appendChild(button);
  }
  
  // 处理导出
  async function handleExport() {
    try {
      // 显示加载状态
      showNotification('⏳ 正在导出Cookie...', 'info');
      
      // 通知background script获取Cookie
      const response = await chrome.runtime.sendMessage({ 
        action: 'getCookies' 
      });
      
      if (response && response.cookies) {
        const cookies = response.cookies;
        const formatted = JSON.stringify(cookies, null, 2);
        
        // 复制到剪贴板
        await navigator.clipboard.writeText(formatted);
        
        // 显示成功通知
        showNotification(`✅ 导出成功！\n已复制 ${cookies.length} 个Cookie到剪贴板`, 'success');
        
        // 通知background script
        chrome.runtime.sendMessage({
          action: 'notify',
          title: 'Cookie导出成功',
          message: `已复制 ${cookies.length} 个Cookie到剪贴板`
        });
        
      } else {
        throw new Error('无法获取Cookie');
      }
      
    } catch (error) {
      console.error('导出失败:', error);
      showNotification('❌ 导出失败：' + error.message, 'error');
    }
  }
  
  // 显示通知
  function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 16px 20px;
      background: ${type === 'success' ? '#67C23A' : type === 'error' ? '#F56C6C' : '#409EFF'};
      color: white;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      z-index: 999999;
      font-size: 14px;
      max-width: 300px;
      white-space: pre-wrap;
      animation: slideIn 0.3s;
    `;
    
    notification.innerHTML = message;
    document.body.appendChild(notification);
    
    // 3秒后自动移除
    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s';
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 300);
    }, 3000);
  }
  
  // 添加动画样式
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from {
        transform: translateX(400px);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
    
    @keyframes slideOut {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(400px);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(style);
  
  // 页面加载完成后创建按钮
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createFloatingButton);
  } else {
    createFloatingButton();
  }
  
  // 监听来自页面的消息（用于网页直接调用）
  window.addEventListener('message', (event) => {
    if (event.data.action === 'kook-export-cookie') {
      handleExport();
    }
  });
  
})();
