// KOOK Cookie导出工具 - Enhanced Version

const loginStatusEl = document.getElementById('loginStatus')
const cookieCountEl = document.getElementById('cookieCount')
const exportBtn = document.getElementById('exportBtn')
const openKookBtn = document.getElementById('openKookBtn')
const resultBox = document.getElementById('resultBox')
const guideBox = document.getElementById('guideBox')

// 检测KOOK登录状态
async function checkLoginStatus() {
  try {
    loginStatusEl.textContent = '检测中...'
    loginStatusEl.className = 'status-value info'
    exportBtn.disabled = true

    // 获取KOOK域名的所有Cookie
    const cookies = await chrome.cookies.getAll({ 
      domain: '.kookapp.cn' 
    })

    if (cookies.length === 0) {
      // 未登录
      loginStatusEl.textContent = '🔴 未登录'
      loginStatusEl.className = 'status-value offline'
      cookieCountEl.textContent = '0'
      exportBtn.disabled = true
      
      showResult('请先登录KOOK网站，然后重新打开此扩展', 'error')
      return
    }

    // 检查是否有认证Cookie
    const hasAuthCookie = cookies.some(c => {
      const name = c.name.toLowerCase()
      return name.includes('token') || 
             name.includes('session') || 
             name.includes('auth')
    })

    if (hasAuthCookie && cookies.length >= 3) {
      // 已登录
      loginStatusEl.textContent = '🟢 已登录'
      loginStatusEl.className = 'status-value online'
      cookieCountEl.textContent = cookies.length
      exportBtn.disabled = false
    } else {
      // Cookie不完整
      loginStatusEl.textContent = '🟡 Cookie不完整'
      loginStatusEl.className = 'status-value offline'
      cookieCountEl.textContent = cookies.length
      exportBtn.disabled = true
      
      showResult('检测到部分Cookie，但可能不完整。请尝试退出登录后重新登录', 'error')
    }
  } catch (error) {
    console.error('检测登录状态失败:', error)
    showResult('检测失败: ' + error.message, 'error')
  }
}

// 导出Cookie到剪贴板
async function exportCookie() {
  try {
    showResult('正在导出Cookie...', 'loading')
    exportBtn.disabled = true
    exportBtn.innerHTML = '<span class="loading-spinner"></span> 导出中...'

    // 获取所有KOOK Cookie
    const cookies = await chrome.cookies.getAll({ 
      domain: '.kookapp.cn' 
    })

    if (cookies.length === 0) {
      throw new Error('未找到KOOK Cookie，请先登录')
    }

    // 格式化为标准JSON格式
    const cookieData = cookies.map(cookie => ({
      name: cookie.name,
      value: cookie.value,
      domain: cookie.domain,
      path: cookie.path,
      expires: cookie.expirationDate || null,
      httpOnly: cookie.httpOnly,
      secure: cookie.secure,
      sameSite: cookie.sameSite || 'lax'
    }))

    // 转换为JSON字符串（美化格式）
    const cookieJson = JSON.stringify(cookieData, null, 2)

    // 复制到剪贴板
    await navigator.clipboard.writeText(cookieJson)

    // 显示成功提示
    showResult(
      `✅ 成功导出 ${cookies.length} 个Cookie到剪贴板！<br>` +
      `Cookie已自动复制，请按照下方指引完成配置。`,
      'success'
    )

    // 显示使用指南
    guideBox.classList.add('show')

    // 恢复按钮
    exportBtn.disabled = false
    exportBtn.innerHTML = '<span class="icon">✅</span> 已复制到剪贴板'

    // 3秒后恢复按钮文本
    setTimeout(() => {
      exportBtn.innerHTML = '<span class="icon">📋</span> 导出Cookie到剪贴板'
    }, 3000)

    // 记录导出事件（用于统计）
    chrome.storage.local.get(['exportCount'], (result) => {
      const count = (result.exportCount || 0) + 1
      chrome.storage.local.set({ exportCount: count })
    })

  } catch (error) {
    console.error('导出Cookie失败:', error)
    showResult('❌ 导出失败: ' + error.message, 'error')
    
    // 恢复按钮
    exportBtn.disabled = false
    exportBtn.innerHTML = '<span class="icon">📋</span> 导出Cookie到剪贴板'
  }
}

// 打开KOOK网站
function openKookWebsite() {
  chrome.tabs.create({ 
    url: 'https://www.kookapp.cn/app'
  })

  showResult('已在新标签页打开KOOK，登录后请重新打开此扩展', 'loading')
}

// 显示结果提示
function showResult(message, type) {
  resultBox.innerHTML = message
  resultBox.className = `result-box show ${type}`
}

// 绑定事件
exportBtn.addEventListener('click', exportCookie)
openKookBtn.addEventListener('click', openKookWebsite)

// 页面加载时检查登录状态
checkLoginStatus()

// 每5秒自动刷新状态
setInterval(checkLoginStatus, 5000)
