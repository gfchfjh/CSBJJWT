/**
 * 系统托盘管理器
 * ✅ P2-3优化: 实时统计（5秒刷新）+ 智能通知
 */

const { Tray, Menu, nativeImage, Notification } = require('electron');
const path = require('path');
const axios = require('axios');

class TrayManager {
  constructor(mainWindow) {
    this.mainWindow = mainWindow;
    this.tray = null;
    
    // 统计数据
    this.stats = {
      total: 0,
      success: 0,
      failed: 0,
      successRate: 0,
      queue: 0,
      status: 'stopped'
    };
    
    // 刷新定时器
    this.refreshInterval = null;
    
    // 后端API配置
    this.apiUrl = 'http://localhost:9527';
    
    // 初始化托盘
    this.init();
  }
  
  /**
   * 初始化系统托盘
   */
  init() {
    // 创建托盘图标
    const iconPath = path.join(__dirname, '../build/icon.png');
    const icon = nativeImage.createFromPath(iconPath);
    const trayIcon = icon.resize({ width: 16, height: 16 });
    
    this.tray = new Tray(trayIcon);
    this.tray.setToolTip('KOOK消息转发系统');
    
    // 设置右键菜单
    this.updateMenu();
    
    // 双击托盘图标显示主窗口
    this.tray.on('double-click', () => {
      if (this.mainWindow) {
        if (this.mainWindow.isMinimized()) {
          this.mainWindow.restore();
        }
        this.mainWindow.show();
        this.mainWindow.focus();
      }
    });
    
    // 启动定时刷新（每5秒）
    this.startAutoRefresh();
    
    console.log('✅ 系统托盘已初始化');
  }
  
  /**
   * 启动自动刷新
   */
  startAutoRefresh() {
    // 立即刷新一次
    this.updateStats();
    
    // 每5秒刷新一次
    this.refreshInterval = setInterval(() => {
      this.updateStats();
    }, 5000);
    
    console.log('✅ 托盘统计自动刷新已启动（5秒间隔）');
  }
  
  /**
   * 停止自动刷新
   */
  stopAutoRefresh() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
      console.log('托盘统计自动刷新已停止');
    }
  }
  
  /**
   * 更新统计数据
   */
  async updateStats() {
    try {
      // 调用后端API获取统计
      const response = await axios.get(`${this.apiUrl}/api/system/stats`, {
        timeout: 3000
      });
      
      if (response.data && response.data.success) {
        const data = response.data.data;
        
        // 更新统计数据
        const oldStats = { ...this.stats };
        
        this.stats = {
          total: data.total_messages || 0,
          success: data.success_count || 0,
          failed: data.failed_count || 0,
          successRate: data.success_rate || 0,
          queue: data.queue_size || 0,
          status: data.service_status || 'stopped',
          activeAccounts: data.active_accounts || 0,
          activeBots: data.active_bots || 0
        };
        
        // 更新菜单
        this.updateMenu();
        
        // 检查是否需要通知
        this.checkAlerts(oldStats, this.stats);
      }
      
    } catch (error) {
      console.error('获取统计失败:', error.message);
      
      // 标记为离线状态
      if (this.stats.status !== 'offline') {
        this.stats.status = 'offline';
        this.updateMenu();
      }
    }
  }
  
  /**
   * 更新托盘菜单
   */
  updateMenu() {
    const statusIcon = this.getStatusIcon(this.stats.status);
    const statusText = this.getStatusText(this.stats.status);
    
    const menu = Menu.buildFromTemplate([
      // 标题
      {
        label: '📊 KOOK消息转发系统',
        enabled: false
      },
      { type: 'separator' },
      
      // 运行状态
      {
        label: `${statusIcon} 状态: ${statusText}`,
        enabled: false
      },
      { type: 'separator' },
      
      // 统计信息
      {
        label: '📈 实时统计',
        enabled: false
      },
      {
        label: `   转发总数: ${this.formatNumber(this.stats.total)}`,
        enabled: false
      },
      {
        label: `   成功: ${this.formatNumber(this.stats.success)} | 失败: ${this.stats.failed}`,
        enabled: false
      },
      {
        label: `   成功率: ${this.stats.successRate}%`,
        enabled: false
      },
      {
        label: `   队列消息: ${this.stats.queue}`,
        enabled: false,
        // 队列堆积时高亮显示
        ...(this.stats.queue > 50 && { icon: this.getWarningIcon() })
      },
      { type: 'separator' },
      
      // 服务控制
      {
        label: '⚙️ 服务控制',
        enabled: false
      },
      {
        label: '   ▶️ 启动服务',
        enabled: this.stats.status === 'stopped',
        click: () => this.startService()
      },
      {
        label: '   ⏸️ 停止服务',
        enabled: this.stats.status === 'running',
        click: () => this.stopService()
      },
      {
        label: '   🔄 重启服务',
        enabled: this.stats.status === 'running',
        click: () => this.restartService()
      },
      { type: 'separator' },
      
      // 快捷操作
      {
        label: '📁 打开主窗口',
        click: () => {
          if (this.mainWindow) {
            this.mainWindow.show();
            this.mainWindow.focus();
          }
        }
      },
      {
        label: '📋 查看日志',
        click: () => this.openLogs()
      },
      {
        label: '⚙️ 设置',
        click: () => this.openSettings()
      },
      { type: 'separator' },
      
      // 退出
      {
        label: '❌ 退出',
        click: () => {
          if (this.mainWindow) {
            this.mainWindow.destroy();
          }
          process.exit(0);
        }
      }
    ]);
    
    this.tray.setContextMenu(menu);
    
    // 更新Tooltip
    const tooltip = `KOOK消息转发系统\n状态: ${statusText}\n转发: ${this.stats.total} | 成功率: ${this.stats.successRate}%`;
    this.tray.setToolTip(tooltip);
  }
  
  /**
   * 检查告警条件
   */
  checkAlerts(oldStats, newStats) {
    // 1. 队列堆积告警（超过100条）
    if (newStats.queue > 100 && oldStats.queue <= 100) {
      this.showNotification(
        '⚠️ 队列堆积',
        `当前有${newStats.queue}条消息等待发送，可能存在网络问题`,
        'warning'
      );
    }
    
    // 2. 成功率下降告警（低于80%且总数>100）
    if (newStats.total > 100 && newStats.successRate < 80 && oldStats.successRate >= 80) {
      this.showNotification(
        '⚠️ 成功率下降',
        `当前成功率${newStats.successRate}%，请检查目标平台连接`,
        'warning'
      );
    }
    
    // 3. 服务停止告警
    if (newStats.status === 'stopped' && oldStats.status === 'running') {
      this.showNotification(
        '❌ 服务已停止',
        'KOOK消息转发服务已停止运行',
        'error'
      );
    }
    
    // 4. 服务启动通知
    if (newStats.status === 'running' && oldStats.status !== 'running') {
      this.showNotification(
        '✅ 服务已启动',
        'KOOK消息转发服务正在运行',
        'success'
      );
    }
  }
  
  /**
   * 显示系统通知
   */
  showNotification(title, body, type = 'info') {
    const notification = new Notification({
      title: title,
      body: body,
      icon: path.join(__dirname, '../build/icon.png'),
      silent: false
    });
    
    notification.show();
  }
  
  /**
   * 启动服务
   */
  async startService() {
    try {
      await axios.post(`${this.apiUrl}/api/system/start`);
      
      // 立即刷新状态
      await this.updateStats();
      
      this.showNotification('✅ 服务启动', '消息转发服务已启动', 'success');
      
    } catch (error) {
      console.error('启动服务失败:', error);
      this.showNotification('❌ 启动失败', error.message, 'error');
    }
  }
  
  /**
   * 停止服务
   */
  async stopService() {
    try {
      await axios.post(`${this.apiUrl}/api/system/stop`);
      
      // 立即刷新状态
      await this.updateStats();
      
      this.showNotification('⏸️ 服务停止', '消息转发服务已停止', 'info');
      
    } catch (error) {
      console.error('停止服务失败:', error);
      this.showNotification('❌ 停止失败', error.message, 'error');
    }
  }
  
  /**
   * 重启服务
   */
  async restartService() {
    try {
      await this.stopService();
      
      // 等待2秒
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      await this.startService();
      
    } catch (error) {
      console.error('重启服务失败:', error);
      this.showNotification('❌ 重启失败', error.message, 'error');
    }
  }
  
  /**
   * 打开日志
   */
  openLogs() {
    if (this.mainWindow) {
      this.mainWindow.show();
      this.mainWindow.focus();
      
      // 发送消息到渲染进程，切换到日志页面
      this.mainWindow.webContents.send('navigate-to', '/logs');
    }
  }
  
  /**
   * 打开设置
   */
  openSettings() {
    if (this.mainWindow) {
      this.mainWindow.show();
      this.mainWindow.focus();
      
      // 发送消息到渲染进程，切换到设置页面
      this.mainWindow.webContents.send('navigate-to', '/settings');
    }
  }
  
  /**
   * 获取状态图标
   */
  getStatusIcon(status) {
    const icons = {
      'running': '🟢',
      'stopped': '🔴',
      'offline': '⚫',
      'error': '🔴'
    };
    return icons[status] || '⚪';
  }
  
  /**
   * 获取状态文本
   */
  getStatusText(status) {
    const texts = {
      'running': '运行中',
      'stopped': '已停止',
      'offline': '离线',
      'error': '错误'
    };
    return texts[status] || '未知';
  }
  
  /**
   * 获取警告图标
   */
  getWarningIcon() {
    // 返回一个小的警告图标（可选）
    return null;
  }
  
  /**
   * 格式化数字（添加千位分隔符）
   */
  formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }
  
  /**
   * 销毁托盘
   */
  destroy() {
    this.stopAutoRefresh();
    
    if (this.tray) {
      this.tray.destroy();
      this.tray = null;
    }
    
    console.log('✅ 系统托盘已销毁');
  }
}

module.exports = TrayManager;
