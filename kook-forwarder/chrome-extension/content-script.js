/**
 * KOOK Cookie导出工具 - 内容脚本
 * 注入到KOOK页面，可进行页面交互
 * 版本: v1.0.0
 */

// 检查是否在KOOK页面
const isKookPage = window.location.hostname.includes('kookapp.cn') || 
                   window.location.hostname.includes('kaiheila.cn')

if (isKookPage) {
  console.log('KOOK Cookie导出工具已加载')
  
  // 可以在页面上添加一个浮动按钮（可选）
  // createFloatingButton()
}

// 创建浮动按钮（可选功能）
function createFloatingButton() {
  const button = document.createElement('div')
  button.id = 'kook-cookie-export-btn'
  button.innerHTML = '🍪'
  button.title = '导出Cookie'
  button.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 50px;
    height: 50px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 24px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    z-index: 9999;
    transition: all 0.3s;
  `
  
  button.addEventListener('mouseenter', () => {
    button.style.transform = 'scale(1.1)'
  })
  
  button.addEventListener('mouseleave', () => {
    button.style.transform = 'scale(1)'
  })
  
  button.addEventListener('click', () => {
    // 发送消息给background script
    chrome.runtime.sendMessage({
      action: 'getCookies'
    }, (response) => {
      if (response.success) {
        // 复制到剪贴板
        const cookiesJSON = JSON.stringify(response.cookies, null, 2)
        navigator.clipboard.writeText(cookiesJSON).then(() => {
          showNotification('✅ Cookie已复制到剪贴板')
        })
      } else {
        showNotification('❌ 导出失败: ' + response.error)
      }
    })
  })
  
  document.body.appendChild(button)
}

// 显示通知
function showNotification(message) {
  const notification = document.createElement('div')
  notification.textContent = message
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 16px 24px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    z-index: 10000;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 14px;
    animation: slideIn 0.3s ease-out;
  `
  
  document.body.appendChild(notification)
  
  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease-out'
    setTimeout(() => {
      document.body.removeChild(notification)
    }, 300)
  }, 3000)
}

// 监听来自扩展的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'checkLogin') {
    // 检查是否已登录（根据页面元素判断）
    const isLoggedIn = !!document.querySelector('[data-user-info]') ||
                       !!document.cookie.includes('session')
    
    sendResponse({ loggedIn: isLoggedIn })
  }
  
  return true
})

// 添加CSS动画
const style = document.createElement('style')
style.textContent = `
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateX(100px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
  
  @keyframes slideOut {
    from {
      opacity: 1;
      transform: translateX(0);
    }
    to {
      opacity: 0;
      transform: translateX(100px);
    }
  }
`
document.head.appendChild(style)
