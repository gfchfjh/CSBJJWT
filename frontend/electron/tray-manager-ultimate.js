/**
 * 🚀 P1-3优化: 系统托盘实时统计（终极版）
 * 
 * 功能：
 * 1. 每5秒刷新统计数据
 * 2. 显示今日消息数、成功率、队列、在线账号
 * 3. 快捷控制菜单
 * 4. 桌面通知集成
 * 
 * 作者: KOOK Forwarder Team
 * 版本: 11.0.0
 * 日期: 2025-10-28
 */

const { Tray, Menu, nativeImage, Notification } = require('electron');
const path = require('path');
const axios = require('axios');

class TrayManager {
  constructor(mainWindow) {
    this.mainWindow = mainWindow;
    this.tray = null;
    this.stats = {
      todayMessages: 0,
      successRate: 0,
      queueSize: 0,
      onlineAccounts: 0,
      totalAccounts: 0,
      serviceRunning: false
    };
    
    // API地址
    this.apiUrl = 'http://localhost:9527';
    
    // 刷新定时器
    this.refreshTimer = null;
    
    // 上一次的状态（用于检测变化）
    this.lastStats = { ...this.stats };
    
    this.init();
  }
  
  /**
   * 初始化托盘
   */
  init() {
    // 创建托盘图标
    const iconPath = path.join(__dirname, '../../build/icon.png');
    const icon = nativeImage.createFromPath(iconPath);
    
    this.tray = new Tray(icon.resize({ width: 16, height: 16 }));
    this.tray.setToolTip('KOOK消息转发系统');
    
    // 设置上下文菜单
    this.updateMenu();
    
    // 点击托盘图标显示主窗口
    this.tray.on('click', () => {
      this.showMainWindow();
    });
    
    // 开始定时刷新
    this.startRefresh();
    
    console.log('✅ 托盘管理器已初始化');
  }
  
  /**
   * 开始定时刷新统计
   */
  startRefresh() {
    // 立即刷新一次
    this.refreshStats();
    
    // 每5秒刷新一次
    this.refreshTimer = setInterval(() => {
      this.refreshStats();
    }, 5000);
    
    console.log('✅ 托盘统计刷新已启动（每5秒）');
  }
  
  /**
   * 停止刷新
   */
  stopRefresh() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
      console.log('✅ 托盘统计刷新已停止');
    }
  }
  
  /**
   * 刷新统计数据
   */
  async refreshStats() {
    try {
      // 获取统计数据
      const response = await axios.get(`${this.apiUrl}/api/stats/realtime`, {
        timeout: 3000
      });
      
      const newStats = response.data;
      
      // 更新stats
      this.stats = {
        todayMessages: newStats.today_messages || 0,
        successRate: newStats.success_rate || 0,
        queueSize: newStats.queue_size || 0,
        onlineAccounts: newStats.online_accounts || 0,
        totalAccounts: newStats.total_accounts || 0,
        serviceRunning: newStats.service_running || false
      };
      
      // 检测变化并发送通知
      this.detectChanges();
      
      // 更新菜单
      this.updateMenu();
      
      // 更新工具提示
      this.updateTooltip();
      
      // 更新图标（可选）
      this.updateIcon();
      
    } catch (error) {
      // 连接失败，标记为离线
      this.stats.serviceRunning = false;
      this.updateMenu();
    }
  }
  
  /**
   * 检测变化并发送通知
   */
  detectChanges() {
    // 服务状态变化
    if (this.stats.serviceRunning !== this.lastStats.serviceRunning) {
      if (this.stats.serviceRunning) {
        this.sendNotification('success', '服务已启动', '转发服务正在运行');
      } else {
        this.sendNotification('warning', '服务已停止', '转发服务已停止运行');
      }
    }
    
    // 账号掉线
    if (this.stats.onlineAccounts < this.lastStats.onlineAccounts) {
      const offlineCount = this.lastStats.onlineAccounts - this.stats.onlineAccounts;
      this.sendNotification(
        'warning',
        '账号掉线',
        `${offlineCount}个账号已离线`
      );
    }
    
    // 队列积压
    if (this.stats.queueSize > 100 && this.lastStats.queueSize <= 100) {
      this.sendNotification(
        'warning',
        '队列积压',
        `当前队列中有${this.stats.queueSize}条消息等待发送`
      );
    }
    
    // 成功率下降
    if (this.stats.successRate < 90 && this.lastStats.successRate >= 90) {
      this.sendNotification(
        'error',
        '成功率下降',
        `当前成功率: ${this.stats.successRate.toFixed(1)}%`
      );
    }
    
    // 保存当前状态
    this.lastStats = { ...this.stats };
  }
  
  /**
   * 更新菜单
   */
  updateMenu() {
    const { serviceRunning, todayMessages, successRate, queueSize, onlineAccounts, totalAccounts } = this.stats;
    
    const contextMenu = Menu.buildFromTemplate([
      // 标题
      {
        label: 'KOOK消息转发系统',
        enabled: false
      },
      { type: 'separator' },
      
      // 统计信息
      {
        label: `状态: ${serviceRunning ? '🟢 运行中' : '🔴 已停止'}`,
        enabled: false
      },
      {
        label: `今日: ${todayMessages} 条`,
        enabled: false
      },
      {
        label: `成功率: ${successRate.toFixed(1)}%`,
        enabled: false
      },
      {
        label: `队列: ${queueSize} 条`,
        enabled: false
      },
      {
        label: `账号: ${onlineAccounts}/${totalAccounts} 在线`,
        enabled: false
      },
      { type: 'separator' },
      
      // 服务控制
      {
        label: serviceRunning ? '⏸️  停止服务' : '▶️  启动服务',
        click: () => {
          if (serviceRunning) {
            this.stopService();
          } else {
            this.startService();
          }
        }
      },
      {
        label: '🔄 重启服务',
        enabled: serviceRunning,
        click: () => this.restartService()
      },
      { type: 'separator' },
      
      // 快捷操作
      {
        label: '🧪 测试转发',
        click: () => this.testForward()
      },
      {
        label: '🗑️  清空队列',
        enabled: queueSize > 0,
        click: () => this.clearQueue()
      },
      { type: 'separator' },
      
      // 快捷导航
      {
        label: '🏠 显示主窗口',
        click: () => this.showMainWindow()
      },
      {
        label: '快捷导航',
        submenu: [
          {
            label: '👤 账号管理',
            click: () => this.navigate('/accounts')
          },
          {
            label: '🤖 Bot配置',
            click: () => this.navigate('/bots')
          },
          {
            label: '🔀 频道映射',
            click: () => this.navigate('/mapping')
          },
          {
            label: '📋 日志查看',
            click: () => this.navigate('/logs')
          },
          {
            label: '⚙️  系统设置',
            click: () => this.navigate('/settings')
          }
        ]
      },
      { type: 'separator' },
      
      // 退出
      {
        label: '❌ 退出程序',
        click: () => this.quitApp()
      }
    ]);
    
    this.tray.setContextMenu(contextMenu);
  }
  
  /**
   * 更新工具提示
   */
  updateTooltip() {
    const { serviceRunning, todayMessages, successRate, queueSize, onlineAccounts, totalAccounts } = this.stats;
    
    const tooltip = [
      'KOOK消息转发系统',
      '━━━━━━━━━━━━━━━',
      `状态: ${serviceRunning ? '运行中' : '已停止'}`,
      `今日: ${todayMessages} 条`,
      `成功率: ${successRate.toFixed(1)}%`,
      `队列: ${queueSize} 条`,
      `账号: ${onlineAccounts}/${totalAccounts} 在线`
    ].join('\n');
    
    this.tray.setToolTip(tooltip);
  }
  
  /**
   * 更新图标
   */
  updateIcon() {
    // 根据状态更改图标（可选）
    // 例如：服务运行时使用彩色图标，停止时使用灰色图标
    const iconPath = path.join(__dirname, '../../build/icon.png');
    const icon = nativeImage.createFromPath(iconPath);
    
    // 如果服务停止，可以添加一个覆盖层
    if (!this.stats.serviceRunning) {
      // 这里可以添加灰度处理或覆盖层
    }
    
    this.tray.setImage(icon.resize({ width: 16, height: 16 }));
  }
  
  /**
   * 发送通知
   */
  sendNotification(type, title, body) {
    // 检查是否启用通知
    const notificationSettings = this.getNotificationSettings();
    
    if (!notificationSettings[type]) {
      return;
    }
    
    // 检查是否在静默时段
    if (this.isQuietTime()) {
      console.log(`静默时段，通知已抑制: ${title}`);
      return;
    }
    
    const notification = new Notification({
      title,
      body,
      icon: path.join(__dirname, '../../build/icon.png'),
      urgency: type === 'error' ? 'critical' : 'normal'
    });
    
    notification.on('click', () => {
      this.showMainWindow();
    });
    
    notification.show();
    
    console.log(`📢 通知: ${title} - ${body}`);
  }
  
  /**
   * 获取通知设置
   */
  getNotificationSettings() {
    // 从配置读取
    // 这里使用默认值
    return {
      success: false,  // 成功通知默认关闭
      warning: true,   // 警告通知默认开启
      error: true      // 错误通知默认开启
    };
  }
  
  /**
   * 是否在静默时段
   */
  isQuietTime() {
    const now = new Date();
    const hour = now.getHours();
    
    // 默认静默时段: 22:00-8:00
    return hour >= 22 || hour < 8;
  }
  
  /**
   * 显示主窗口
   */
  showMainWindow() {
    if (this.mainWindow) {
      if (this.mainWindow.isMinimized()) {
        this.mainWindow.restore();
      }
      this.mainWindow.show();
      this.mainWindow.focus();
    }
  }
  
  /**
   * 导航到指定页面
   */
  navigate(path) {
    this.showMainWindow();
    
    // 通知主窗口导航
    if (this.mainWindow && this.mainWindow.webContents) {
      this.mainWindow.webContents.send('navigate', path);
    }
  }
  
  /**
   * 启动服务
   */
  async startService() {
    try {
      await axios.post(`${this.apiUrl}/api/system/start`);
      this.sendNotification('success', '服务已启动', '转发服务正在运行');
      this.refreshStats();
    } catch (error) {
      this.sendNotification('error', '启动失败', error.message);
    }
  }
  
  /**
   * 停止服务
   */
  async stopService() {
    try {
      await axios.post(`${this.apiUrl}/api/system/stop`);
      this.sendNotification('warning', '服务已停止', '转发服务已停止运行');
      this.refreshStats();
    } catch (error) {
      this.sendNotification('error', '停止失败', error.message);
    }
  }
  
  /**
   * 重启服务
   */
  async restartService() {
    try {
      await axios.post(`${this.apiUrl}/api/system/restart`);
      this.sendNotification('success', '服务已重启', '转发服务正在重新启动');
      this.refreshStats();
    } catch (error) {
      this.sendNotification('error', '重启失败', error.message);
    }
  }
  
  /**
   * 测试转发
   */
  async testForward() {
    try {
      const response = await axios.post(`${this.apiUrl}/api/system/test-forward`);
      const { success, failed } = response.data;
      
      if (failed === 0) {
        this.sendNotification('success', '测试成功', `成功发送${success}条测试消息`);
      } else {
        this.sendNotification('warning', '测试完成', `成功${success}条，失败${failed}条`);
      }
    } catch (error) {
      this.sendNotification('error', '测试失败', error.message);
    }
  }
  
  /**
   * 清空队列
   */
  async clearQueue() {
    try {
      await axios.post(`${this.apiUrl}/api/system/clear-queue`);
      this.sendNotification('success', '队列已清空', '所有待发送消息已清空');
      this.refreshStats();
    } catch (error) {
      this.sendNotification('error', '清空失败', error.message);
    }
  }
  
  /**
   * 退出应用
   */
  quitApp() {
    this.stopRefresh();
    
    if (this.mainWindow) {
      this.mainWindow.destroy();
    }
    
    if (this.tray) {
      this.tray.destroy();
    }
    
    require('electron').app.quit();
  }
  
  /**
   * 销毁
   */
  destroy() {
    this.stopRefresh();
    
    if (this.tray) {
      this.tray.destroy();
      this.tray = null;
    }
  }
}

module.exports = TrayManager;
