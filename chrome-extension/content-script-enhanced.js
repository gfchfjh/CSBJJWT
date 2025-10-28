/**
 * Content Script for KOOK Cookie Exporter v2.0
 * 在KOOK页面注入，支持快捷键导出
 */

console.log('KOOK Cookie导出器 v2.0 已加载');

// 监听来自background script的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'exportCookie') {
        console.log('接收到导出Cookie请求（通过快捷键）');
        
        // 显示页面通知
        showPageNotification('正在导出Cookie...', 'info');
        
        // 这里不能直接访问chrome.cookies API（需要在background或popup中）
        // 所以我们通知用户打开扩展弹窗
        setTimeout(() => {
            showPageNotification('请点击浏览器工具栏的扩展图标完成导出', 'success', 3000);
        }, 1000);
        
        sendResponse({ success: true });
    }
    
    return true;
});

/**
 * 在页面上显示通知
 */
function showPageNotification(message, type = 'info', duration = 2000) {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#667eea'};
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 999999;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 14px;
        max-width: 300px;
        animation: slideIn 0.3s ease;
    `;
    
    notification.textContent = `🍪 ${message}`;
    
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
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 自动移除
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, duration);
}

// 检测页面是否为KOOK
if (window.location.hostname.includes('kookapp.cn')) {
    console.log('✅ KOOK页面检测成功');
    
    // 可以在这里添加页面增强功能
    // 例如：显示一个浮动按钮，点击快速导出Cookie
}
