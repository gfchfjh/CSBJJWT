/**
 * KOOK Cookie导出工具 - 弹出窗口逻辑
 * 版本: v1.0.0
 */

const statusEl = document.getElementById('status')
const exportBtn = document.getElementById('exportBtn')
const buttonText = document.getElementById('buttonText')
const cookieInfoEl = document.getElementById('cookieInfo')
const cookieCountEl = document.getElementById('cookieCount')
const statsEl = document.getElementById('stats')
const exportCountEl = document.getElementById('exportCount')
const lastExportEl = document.getElementById('lastExport')

// 显示状态
function showStatus(message, type = 'success') {
  statusEl.textContent = message
  statusEl.className = `status ${type} show`
  setTimeout(() => {
    statusEl.classList.remove('show')
  }, 5000)
}

// 更新统计信息
async function updateStats() {
  try {
    const stats = await chrome.storage.local.get(['exportCount', 'lastExport'])
    
    if (stats.exportCount) {
      exportCountEl.textContent = stats.exportCount
      statsEl.style.display = 'grid'
    }
    
    if (stats.lastExport) {
      const date = new Date(stats.lastExport)
      const now = new Date()
      const diff = Math.floor((now - date) / 1000)
      
      if (diff < 60) {
        lastExportEl.textContent = `${diff}秒前`
      } else if (diff < 3600) {
        lastExportEl.textContent = `${Math.floor(diff / 60)}分钟前`
      } else if (diff < 86400) {
        lastExportEl.textContent = `${Math.floor(diff / 3600)}小时前`
      } else {
        lastExportEl.textContent = `${Math.floor(diff / 86400)}天前`
      }
    }
  } catch (error) {
    console.error('更新统计失败:', error)
  }
}

// 保存统计信息
async function saveStats() {
  try {
    const stats = await chrome.storage.local.get(['exportCount'])
    const newCount = (stats.exportCount || 0) + 1
    
    await chrome.storage.local.set({
      exportCount: newCount,
      lastExport: Date.now()
    })
    
    await updateStats()
  } catch (error) {
    console.error('保存统计失败:', error)
  }
}

// 验证Cookie
function validateCookies(cookies) {
  const warnings = []
  
  // 检查数量
  if (cookies.length === 0) {
    return { valid: false, error: '未找到Cookie，请先登录KOOK' }
  }
  
  if (cookies.length < 3) {
    warnings.push(`Cookie数量较少（${cookies.length}个）`)
  }
  
  // 检查域名
  const hasKookDomain = cookies.some(c => 
    c.domain && (c.domain.includes('kookapp.cn') || c.domain.includes('kaiheila.cn'))
  )
  
  if (!hasKookDomain) {
    warnings.push('Cookie域名可能不正确')
  }
  
  // 检查关键字段
  const requiredFields = ['name', 'value']
  const hasRequiredFields = cookies.every(c => 
    requiredFields.every(field => field in c && c[field])
  )
  
  if (!hasRequiredFields) {
    return { valid: false, error: 'Cookie格式不完整' }
  }
  
  return { valid: true, warnings }
}

// 导出Cookie
async function exportCookies() {
  try {
    exportBtn.disabled = true
    buttonText.textContent = '导出中...'
    
    // 获取当前标签页
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
    
    // 检查是否在KOOK页面
    if (!tab.url || (!tab.url.includes('kookapp.cn') && !tab.url.includes('kaiheila.cn'))) {
      showStatus('⚠️  请在KOOK网页版使用此扩展', 'warning')
      exportBtn.disabled = false
      buttonText.textContent = '导出Cookie到剪贴板'
      return
    }
    
    // 获取KOOK的所有Cookie
    const cookies = await chrome.cookies.getAll({
      domain: '.kookapp.cn'
    })
    
    // 如果没找到，尝试kaiheila.cn
    if (cookies.length === 0) {
      const cookies2 = await chrome.cookies.getAll({
        domain: '.kaiheila.cn'
      })
      cookies.push(...cookies2)
    }
    
    // 验证Cookie
    const validation = validateCookies(cookies)
    
    if (!validation.valid) {
      showStatus(`❌ ${validation.error}`, 'error')
      exportBtn.disabled = false
      buttonText.textContent = '导出Cookie到剪贴板'
      return
    }
    
    // 转换为JSON格式（格式化，方便阅读）
    const cookiesJSON = JSON.stringify(cookies, null, 2)
    
    // 复制到剪贴板
    await navigator.clipboard.writeText(cookiesJSON)
    
    // 保存统计
    await saveStats()
    
    // 成功提示
    let message = `✅ 成功导出 ${cookies.length} 个Cookie到剪贴板！`
    if (validation.warnings && validation.warnings.length > 0) {
      message += `\n⚠️  ${validation.warnings.join(', ')}`
    }
    
    showStatus(message, 'success')
    
    // 更新按钮
    buttonText.innerHTML = '<span class="icon">✓</span>已复制到剪贴板'
    
    // 3秒后恢复按钮
    setTimeout(() => {
      exportBtn.disabled = false
      buttonText.innerHTML = '<span class="icon">📋</span>导出Cookie到剪贴板'
    }, 3000)
    
  } catch (error) {
    console.error('导出失败:', error)
    showStatus(`❌ 导出失败: ${error.message}`, 'error')
    exportBtn.disabled = false
    buttonText.textContent = '导出Cookie到剪贴板'
  }
}

// 检查Cookie状态
async function checkCookieStatus() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
    
    if (!tab.url) {
      return
    }
    
    if (tab.url.includes('kookapp.cn') || tab.url.includes('kaiheila.cn')) {
      // 获取Cookie数量
      const cookies = await chrome.cookies.getAll({ domain: '.kookapp.cn' })
      const cookies2 = await chrome.cookies.getAll({ domain: '.kaiheila.cn' })
      const totalCookies = cookies.length + cookies2.length
      
      if (totalCookies > 0) {
        cookieCountEl.textContent = totalCookies
        cookieInfoEl.style.display = 'block'
        showStatus(`✓ 检测到 ${totalCookies} 个Cookie，可以导出`, 'info')
      } else {
        showStatus('⚠️  未检测到Cookie，请先登录KOOK', 'warning')
      }
    } else {
      showStatus('ℹ️  请在KOOK网页版使用此扩展', 'info')
    }
  } catch (error) {
    console.error('状态检查失败:', error)
  }
}

// 绑定事件
exportBtn.addEventListener('click', exportCookies)

// 页面加载时执行
window.addEventListener('load', async () => {
  await updateStats()
  await checkCookieStatus()
})

// 监听键盘快捷键
document.addEventListener('keydown', (e) => {
  // Ctrl+Enter 或 Cmd+Enter 快速导出
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    exportCookies()
  }
})
