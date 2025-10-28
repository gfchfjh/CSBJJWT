/**
 * 🚀 P0-3优化: Chrome扩展v2.0增强版
 * 
 * 新功能：
 * 1. 双域名Cookie获取（kookapp.cn + www.kookapp.cn）
 * 2. 智能验证关键Cookie（token/session等）
 * 3. 检测转发系统运行状态
 * 4. 快捷键支持（Ctrl+Shift+K）
 * 5. Cookie详情查看
 * 6. 错误重试机制
 * 7. 如果主程序在运行，直接发送Cookie
 * 
 * 作者: KOOK Forwarder Team
 * 版本: 2.0.0
 * 日期: 2025-10-28
 */

class KookCookieExporterV2 {
  constructor() {
    // KOOK的多个域名
    this.domains = [
      'www.kookapp.cn',
      'kookapp.cn',
      'www.kaiheila.cn',
      'kaiheila.cn'
    ];
    
    // 必需的关键Cookie
    this.requiredCookies = [
      'token',
      'session',
      'session_id',
      'user_id',
      'auth_token'
    ];
    
    // 转发系统API地址
    this.systemUrl = 'http://localhost:9527';
    
    // 状态
    this.isExporting = false;
    this.systemRunning = false;
    
    // DOM元素
    this.statusEl = null;
    this.exportBtn = null;
    this.detailsEl = null;
    this.copyBtn = null;
    this.sendBtn = null;
    
    // 导出的Cookie
    this.exportedCookies = null;
  }
  
  /**
   * 初始化
   */
  async init() {
    console.log('🚀 初始化KOOK Cookie导出器v2.0');
    
    // 获取DOM元素
    this.statusEl = document.getElementById('status');
    this.exportBtn = document.getElementById('exportBtn');
    this.detailsEl = document.getElementById('details');
    this.copyBtn = document.getElementById('copyBtn');
    this.sendBtn = document.getElementById('sendBtn');
    
    // 绑定事件
    this.exportBtn.addEventListener('click', () => this.exportCookies());
    this.copyBtn.addEventListener('click', () => this.copyCookies());
    this.sendBtn.addEventListener('click', () => this.sendToSystem());
    
    // 检测转发系统状态
    await this.checkSystemStatus();
    
    // 自动检测Cookie
    await this.autoDetectCookies();
  }
  
  /**
   * 导出Cookie（主流程）
   */
  async exportCookies() {
    if (this.isExporting) {
      return;
    }
    
    this.isExporting = true;
    this.showStatus('正在导出Cookie...', 'info');
    this.showLoading(true);
    
    try {
      // 1. 从多个域名获取Cookie
      const allCookies = await this.getCookiesFromAllDomains();
      
      if (allCookies.length === 0) {
        throw new Error('未检测到Cookie，请确保已登录KOOK');
      }
      
      // 2. 验证关键Cookie
      const validation = this.validateCookies(allCookies);
      
      if (!validation.valid) {
        throw new Error(`缺少关键Cookie: ${validation.missing.join(', ')}`);
      }
      
      // 3. 去重（同名Cookie取最新的）
      const uniqueCookies = this.deduplicateCookies(allCookies);
      
      // 4. 保存
      this.exportedCookies = uniqueCookies;
      
      // 5. 复制到剪贴板
      await this.copyToClipboard(uniqueCookies);
      
      // 6. 如果转发系统在运行，自动发送
      if (this.systemRunning) {
        await this.sendToSystemAuto(uniqueCookies);
      }
      
      // 7. 显示详情
      this.showDetails(uniqueCookies, validation);
      
      // 8. 成功提示
      this.showStatus(
        `✅ 成功导出${uniqueCookies.length}个Cookie${this.systemRunning ? '，已自动发送到转发系统' : ''}`,
        'success'
      );
      
    } catch (error) {
      console.error('导出Cookie失败:', error);
      this.showStatus(`❌ 导出失败: ${error.message}`, 'error');
      
      // 显示重试按钮
      this.showRetryButton();
      
    } finally {
      this.isExporting = false;
      this.showLoading(false);
    }
  }
  
  /**
   * 从所有域名获取Cookie
   */
  async getCookiesFromAllDomains() {
    console.log('📥 从多个域名获取Cookie...');
    
    const allCookies = [];
    
    for (const domain of this.domains) {
      try {
        const cookies = await chrome.cookies.getAll({ domain });
        
        console.log(`  ✅ ${domain}: ${cookies.length}个Cookie`);
        
        // 添加域名标记
        cookies.forEach(cookie => {
          cookie._source_domain = domain;
        });
        
        allCookies.push(...cookies);
        
      } catch (error) {
        console.warn(`  ⚠️  ${domain}获取失败:`, error);
      }
    }
    
    console.log(`📦 总计获取${allCookies.length}个Cookie`);
    
    return allCookies;
  }
  
  /**
   * 验证关键Cookie
   */
  validateCookies(cookies) {
    const cookieNames = cookies.map(c => c.name.toLowerCase());
    
    // 检查是否包含任一关键Cookie
    const foundRequired = this.requiredCookies.filter(
      required => cookieNames.includes(required.toLowerCase())
    );
    
    const missing = this.requiredCookies.filter(
      required => !cookieNames.includes(required.toLowerCase())
    );
    
    return {
      valid: foundRequired.length > 0,  // 至少有一个关键Cookie即可
      found: foundRequired,
      missing,
      total: cookies.length
    };
  }
  
  /**
   * 去重（同名Cookie取最新的）
   */
  deduplicateCookies(cookies) {
    const cookieMap = new Map();
    
    for (const cookie of cookies) {
      const key = cookie.name;
      
      if (!cookieMap.has(key)) {
        cookieMap.set(key, cookie);
      } else {
        // 如果已存在，比较时间，取最新的
        const existing = cookieMap.get(key);
        if (cookie.expirationDate > existing.expirationDate) {
          cookieMap.set(key, cookie);
        }
      }
    }
    
    return Array.from(cookieMap.values());
  }
  
  /**
   * 复制到剪贴板
   */
  async copyToClipboard(cookies) {
    const formatted = JSON.stringify(cookies, null, 2);
    
    try {
      await navigator.clipboard.writeText(formatted);
      console.log('✅ 已复制到剪贴板');
    } catch (error) {
      console.error('复制失败:', error);
      
      // 降级方案：使用textarea
      const textarea = document.createElement('textarea');
      textarea.value = formatted;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
    }
  }
  
  /**
   * 检测转发系统状态
   */
  async checkSystemStatus() {
    console.log('🔍 检测转发系统状态...');
    
    try {
      const response = await fetch(`${this.systemUrl}/health`, {
        method: 'GET',
        timeout: 3000
      });
      
      this.systemRunning = response.ok;
      
      if (this.systemRunning) {
        console.log('✅ 转发系统正在运行');
        this.showSystemStatus(true);
      } else {
        console.log('⚠️  转发系统未运行');
        this.showSystemStatus(false);
      }
      
    } catch (error) {
      console.log('⚠️  转发系统未运行:', error.message);
      this.systemRunning = false;
      this.showSystemStatus(false);
    }
    
    return this.systemRunning;
  }
  
  /**
   * 发送到转发系统（自动）
   */
  async sendToSystemAuto(cookies) {
    try {
      await this.sendCookiesToSystem(cookies);
      console.log('✅ 已自动发送到转发系统');
    } catch (error) {
      console.warn('自动发送失败:', error);
    }
  }
  
  /**
   * 发送到转发系统（手动）
   */
  async sendToSystem() {
    if (!this.exportedCookies) {
      this.showStatus('❌ 请先导出Cookie', 'error');
      return;
    }
    
    if (!this.systemRunning) {
      // 重新检测
      await this.checkSystemStatus();
      
      if (!this.systemRunning) {
        this.showStatus('❌ 转发系统未运行', 'error');
        return;
      }
    }
    
    this.showStatus('正在发送到转发系统...', 'info');
    
    try {
      await this.sendCookiesToSystem(this.exportedCookies);
      this.showStatus('✅ 已发送到转发系统', 'success');
    } catch (error) {
      this.showStatus(`❌ 发送失败: ${error.message}`, 'error');
    }
  }
  
  /**
   * 发送Cookie到转发系统
   */
  async sendCookiesToSystem(cookies) {
    const response = await fetch(`${this.systemUrl}/api/accounts/import-cookies`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ cookies })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '发送失败');
    }
    
    return await response.json();
  }
  
  /**
   * 自动检测Cookie
   */
  async autoDetectCookies() {
    console.log('🔍 自动检测Cookie...');
    
    try {
      const cookies = await this.getCookiesFromAllDomains();
      
      if (cookies.length > 0) {
        const validation = this.validateCookies(cookies);
        
        if (validation.valid) {
          this.showAutoDetectResult(validation);
        }
      }
    } catch (error) {
      console.warn('自动检测失败:', error);
    }
  }
  
  /**
   * 显示自动检测结果
   */
  showAutoDetectResult(validation) {
    const infoEl = document.getElementById('autoDetectInfo');
    infoEl.style.display = 'block';
    infoEl.innerHTML = `
      <div class="info-box">
        <span class="icon">✅</span>
        <span>检测到${validation.total}个Cookie，其中关键Cookie: ${validation.found.join(', ')}</span>
      </div>
    `;
  }
  
  /**
   * 显示详情
   */
  showDetails(cookies, validation) {
    this.detailsEl.style.display = 'block';
    
    // 关键Cookie
    const requiredHtml = validation.found.map(name => {
      const cookie = cookies.find(c => c.name.toLowerCase() === name.toLowerCase());
      return `
        <div class="cookie-item">
          <span class="cookie-name">${name}</span>
          <span class="cookie-value">${cookie?.value?.substring(0, 20)}...</span>
          <span class="cookie-expires">过期: ${this.formatExpires(cookie?.expirationDate)}</span>
        </div>
      `;
    }).join('');
    
    // 所有Cookie统计
    const statsHtml = `
      <div class="stats">
        <div class="stat-item">
          <span class="stat-label">总计</span>
          <span class="stat-value">${cookies.length}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">关键</span>
          <span class="stat-value">${validation.found.length}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">域名</span>
          <span class="stat-value">${new Set(cookies.map(c => c._source_domain)).size}</span>
        </div>
      </div>
    `;
    
    document.getElementById('cookieList').innerHTML = requiredHtml;
    document.getElementById('cookieStats').innerHTML = statsHtml;
    
    // 显示操作按钮
    this.copyBtn.style.display = 'inline-block';
    
    if (this.systemRunning) {
      this.sendBtn.style.display = 'inline-block';
    }
  }
  
  /**
   * 显示系统状态
   */
  showSystemStatus(running) {
    const systemStatusEl = document.getElementById('systemStatus');
    systemStatusEl.style.display = 'block';
    
    if (running) {
      systemStatusEl.innerHTML = `
        <div class="status-box success">
          <span class="icon">🟢</span>
          <span>转发系统正在运行</span>
        </div>
      `;
    } else {
      systemStatusEl.innerHTML = `
        <div class="status-box warning">
          <span class="icon">🔴</span>
          <span>转发系统未运行</span>
        </div>
      `;
    }
  }
  
  /**
   * 显示状态
   */
  showStatus(message, type = 'info') {
    this.statusEl.textContent = message;
    this.statusEl.className = `status ${type}`;
    this.statusEl.style.display = 'block';
  }
  
  /**
   * 显示加载动画
   */
  showLoading(show) {
    const loadingEl = document.getElementById('loading');
    loadingEl.style.display = show ? 'block' : 'none';
    
    this.exportBtn.disabled = show;
    this.exportBtn.textContent = show ? '导出中...' : '🍪 一键导出Cookie';
  }
  
  /**
   * 显示重试按钮
   */
  showRetryButton() {
    const retryBtn = document.createElement('button');
    retryBtn.textContent = '🔄 重试';
    retryBtn.className = 'retry-btn';
    retryBtn.onclick = () => {
      retryBtn.remove();
      this.exportCookies();
    };
    
    this.statusEl.appendChild(retryBtn);
  }
  
  /**
   * 复制Cookie（按钮）
   */
  async copyCookies() {
    if (!this.exportedCookies) {
      return;
    }
    
    await this.copyToClipboard(this.exportedCookies);
    
    this.copyBtn.textContent = '✅ 已复制';
    setTimeout(() => {
      this.copyBtn.textContent = '📋 复制Cookie';
    }, 2000);
  }
  
  /**
   * 格式化过期时间
   */
  formatExpires(timestamp) {
    if (!timestamp) {
      return '会话结束';
    }
    
    const date = new Date(timestamp * 1000);
    const now = Date.now();
    const diff = date - now;
    
    if (diff < 0) {
      return '已过期';
    }
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days > 365) {
      return '长期有效';
    } else if (days > 0) {
      return `${days}天后过期`;
    } else {
      const hours = Math.floor(diff / (1000 * 60 * 60));
      return `${hours}小时后过期`;
    }
  }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
  const exporter = new KookCookieExporterV2();
  exporter.init();
});

// 快捷键支持（Ctrl+Shift+K）
chrome.commands.onCommand.addListener((command) => {
  if (command === 'export-cookies') {
    // 打开popup
    chrome.action.openPopup();
  }
});
