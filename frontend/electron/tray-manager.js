/**
 * 系统托盘管理器 - P1-5深度优化
 * 功能：5秒实时刷新，智能告警，动态统计
 */

const { Tray, Menu, nativeImage, app } = require('electron');
const path = require('path');
const axios = require('axios');

class TrayManager {
  constructor(mainWindow) {
    this.mainWindow = mainWindow;
    this.tray = null;
    
    // 统计数据
    this.stats = {
      totalForwarded: 0,
      successRate: 0,
      queueSize: 0,
      status: 'stopped',  // stopped/running/error
      lastUpdate: null
    };
    
    // 告警状态
    this.alerts = {
      queueBacklog: false,    // 队列堆积
      lowSuccessRate: false,  // 成功率低
      serviceError: false     // 服务异常
    };
    
    // 告警防骚扰：1分钟内同一告警只通知一次
    this.lastAlertTime = {};
    
    // 定时器
    this.statsInterval = null;
    this.animationInterval = null;
    
    // 初始化
    this.init();
  }
  
  /**
   * 初始化托盘
   */
  init() {
    try {
      // 创建托盘图标
      const iconPath = path.join(__dirname, '../public/icon.png');
      const icon = nativeImage.createFromPath(iconPath);
      this.tray = new Tray(icon.resize({ width: 16, height: 16 }));
      
      this.tray.setToolTip('KOOK消息转发系统');
      
      // 设置点击事件
      this.tray.on('click', () => {
        this.showMainWindow();
      });
      
      // 初始化菜单
      this.updateTrayMenu();
      
      // 启动定时刷新
      this.startStatsPolling();
      
      console.log('[TrayManager] 托盘管理器已初始化');
    } catch (error) {
      console.error('[TrayManager] 初始化失败:', error);
    }
  }
  
  /**
   * 启动统计轮询（5秒一次）
   */
  startStatsPolling() {
    // 立即执行一次
    this.fetchStats();
    
    // 每5秒刷新一次
    this.statsInterval = setInterval(() => {
      this.fetchStats();
    }, 5000);
    
    console.log('[TrayManager] 统计轮询已启动（5秒间隔）');
  }
  
  /**
   * 停止统计轮询
   */
  stopStatsPolling() {
    if (this.statsInterval) {
      clearInterval(this.statsInterval);
      this.statsInterval = null;
    }
    
    if (this.animationInterval) {
      clearInterval(this.animationInterval);
      this.animationInterval = null;
    }
  }
  
  /**
   * 获取统计数据
   */
  async fetchStats() {
    try {
      const response = await axios.get('http://localhost:9527/api/system/stats', {
        timeout: 3000
      });
      
      const data = response.data;
      
      // 更新统计数据
      this.stats = {
        totalForwarded: data.total_forwarded || 0,
        successRate: data.success_rate || 0,
        queueSize: data.queue_size || 0,
        status: data.status || 'running',
        lastUpdate: new Date()
      };
      
      // 检查告警条件
      this.checkAlerts();
      
      // 更新托盘菜单
      this.updateTrayMenu();
      
    } catch (error) {
      console.error('[TrayManager] 获取统计失败:', error.message);
      
      // 服务异常
      this.stats.status = 'error';
      this.updateTrayMenu();
      
      // 触发服务异常告警
      this.triggerAlert('serviceError', '⚠️ 服务异常', '无法连接到后端服务');
    }
  }
  
  /**
   * 检查告警条件
   */
  checkAlerts() {
    const { queueSize, successRate } = this.stats;
    
    // 1. 队列堆积告警（>100）
    if (queueSize > 100) {
      if (!this.alerts.queueBacklog) {
        this.triggerAlert(
          'queueBacklog',
          '⚠️ 队列堆积',
          `当前队列：${queueSize}条消息`
        );
      }
      this.alerts.queueBacklog = true;
    } else {
      this.alerts.queueBacklog = false;
    }
    
    // 2. 成功率下降告警（<80%）
    if (successRate < 0.8 && this.stats.totalForwarded > 0) {
      if (!this.alerts.lowSuccessRate) {
        this.triggerAlert(
          'lowSuccessRate',
          '⚠️ 成功率下降',
          `当前成功率：${(successRate * 100).toFixed(1)}%`
        );
      }
      this.alerts.lowSuccessRate = true;
    } else {
      this.alerts.lowSuccessRate = false;
    }
    
    // 3. 服务异常（由fetchStats设置）
    if (this.stats.status === 'error') {
      this.alerts.serviceError = true;
    } else {
      this.alerts.serviceError = false;
    }
  }
  
  /**
   * 触发告警（带防骚扰）
   */
  triggerAlert(alertType, title, message) {
    const now = Date.now();
    const lastTime = this.lastAlertTime[alertType] || 0;
    
    // 1分钟内不重复通知
    if (now - lastTime < 60000) {
      return;
    }
    
    this.lastAlertTime[alertType] = now;
    
    // 显示系统通知
    if (this.mainWindow) {
      this.mainWindow.webContents.send('notification', {
        type: 'warning',
        title: title,
        message: message
      });
    }
    
    console.log(`[TrayManager] 告警: ${title} - ${message}`);
  }
  
  /**
   * 更新托盘菜单
   */
  updateTrayMenu() {
    const { totalForwarded, successRate, queueSize, status } = this.stats;
    
    // 状态图标
    const statusIcon = {
      running: '🟢',
      stopped: '🔴',
      error: '⚠️'
    }[status] || '⚪';
    
    // 构建菜单
    const menuTemplate = [
      // 标题
      {
        label: '📊 KOOK消息转发系统',
        enabled: false
      },
      { type: 'separator' },
      
      // 实时统计
      {
        label: '📈 实时统计',
        enabled: false
      },
      {
        label: `   转发总数: ${totalForwarded.toLocaleString()}`,
        enabled: false
      },
      {
        label: `   成功率: ${(successRate * 100).toFixed(1)}%`,
        enabled: false
      },
      {
        label: `   队列消息: ${queueSize}`,
        enabled: false
      },
      {
        label: `   状态: ${statusIcon} ${this.getStatusText(status)}`,
        enabled: false
      },
      { type: 'separator' },
      
      // 告警（如果有）
      ...(this.hasAlerts() ? [
        {
          label: '⚠️ 告警',
          enabled: false
        },
        ...(this.alerts.queueBacklog ? [{
          label: `   ⚠️ 队列堆积 (${queueSize}条)`,
          enabled: false
        }] : []),
        ...(this.alerts.lowSuccessRate ? [{
          label: `   ⚠️ 成功率下降 (${(successRate * 100).toFixed(1)}%)`,
          enabled: false
        }] : []),
        ...(this.alerts.serviceError ? [{
          label: '   ⚠️ 服务异常',
          enabled: false
        }] : []),
        { type: 'separator' }
      ] : []),
      
      // 操作按钮
      {
        label: status === 'running' ? '⏸️  停止服务' : '▶️  启动服务',
        click: () => this.toggleService()
      },
      {
        label: '🔄 重启服务',
        click: () => this.restartService()
      },
      { type: 'separator' },
      
      // 窗口控制
      {
        label: '📁 打开主窗口',
        click: () => this.showMainWindow()
      },
      {
        label: '📋 查看日志',
        click: () => this.showLogs()
      },
      { type: 'separator' },
      
      // 退出
      {
        label: '❌ 退出',
        click: () => this.quit()
      }
    ];
    
    const contextMenu = Menu.buildFromTemplate(menuTemplate);
    this.tray.setContextMenu(contextMenu);
  }
  
  /**
   * 检查是否有告警
   */
  hasAlerts() {
    return this.alerts.queueBacklog || 
           this.alerts.lowSuccessRate || 
           this.alerts.serviceError;
  }
  
  /**
   * 获取状态文本
   */
  getStatusText(status) {
    const statusMap = {
      running: '运行中',
      stopped: '已停止',
      error: '异常'
    };
    return statusMap[status] || '未知';
  }
  
  /**
   * 切换服务状态
   */
  async toggleService() {
    try {
      const action = this.stats.status === 'running' ? 'stop' : 'start';
      
      await axios.post(`http://localhost:9527/api/system/${action}`, {}, {
        timeout: 10000
      });
      
      // 立即刷新状态
      await this.fetchStats();
      
    } catch (error) {
      console.error('[TrayManager] 切换服务失败:', error);
      
      if (this.mainWindow) {
        this.mainWindow.webContents.send('notification', {
          type: 'error',
          title: '操作失败',
          message: '无法切换服务状态'
        });
      }
    }
  }
  
  /**
   * 重启服务
   */
  async restartService() {
    try {
      await axios.post('http://localhost:9527/api/system/restart', {}, {
        timeout: 10000
      });
      
      // 等待3秒让服务重启
      setTimeout(() => {
        this.fetchStats();
      }, 3000);
      
    } catch (error) {
      console.error('[TrayManager] 重启服务失败:', error);
    }
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
   * 显示日志
   */
  showLogs() {
    if (this.mainWindow) {
      this.mainWindow.show();
      this.mainWindow.webContents.send('navigate-to', '/logs');
    }
  }
  
  /**
   * 退出应用
   */
  quit() {
    // 停止轮询
    this.stopStatsPolling();
    
    // 销毁托盘
    if (this.tray) {
      this.tray.destroy();
    }
    
    // 退出应用
    app.quit();
  }
  
  /**
   * 销毁托盘管理器
   */
  destroy() {
    this.stopStatsPolling();
    
    if (this.tray) {
      this.tray.destroy();
      this.tray = null;
    }
  }
}

module.exports = TrayManager;
