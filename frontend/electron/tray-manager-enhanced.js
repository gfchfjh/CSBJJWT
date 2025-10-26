/**
 * 增强版托盘管理器
 * ✅ P0-3优化：7项实时统计 + 6个快捷操作 + 4种状态图标
 */

const { Tray, Menu, nativeImage } = require('electron');
const path = require('path');
const axios = require('axios');

class EnhancedTrayManager {
  constructor(mainWindow) {
    this.mainWindow = mainWindow;
    this.tray = null;
    this.stats = {
      running: false,
      today_total: 0,
      success_rate: 0,
      avg_latency: 0,
      queue_size: 0,
      account_count: 0,
      bot_count: 0,
      uptime: 0
    };
    this.updateInterval = null;
    this.currentStatus = 'offline'; // offline | running | reconnecting | error
  }

  /**
   * 创建托盘
   */
  create() {
    const iconPath = this.getStatusIcon('offline');
    this.tray = new Tray(iconPath);
    
    this.tray.setToolTip('KOOK消息转发系统');
    
    // 单击显示主窗口
    this.tray.on('click', () => {
      this.showMainWindow();
    });
    
    // 创建初始菜单
    this.updateMenu();
    
    // 启动自动更新（每5秒）
    this.startAutoUpdate();
    
    return this.tray;
  }

  /**
   * 获取状态图标
   */
  getStatusIcon(status) {
    const iconsDir = path.join(__dirname, '../build/icons/tray');
    const iconMap = {
      'offline': 'tray-offline.png',      // ⚪ 离线
      'running': 'tray-running.png',      // 🟢 运行中
      'reconnecting': 'tray-warning.png', // 🟡 重连中
      'error': 'tray-error.png'           // 🔴 错误
    };
    
    const iconFile = iconMap[status] || iconMap['offline'];
    const iconPath = path.join(iconsDir, iconFile);
    
    // 如果图标文件不存在，使用默认图标
    try {
      const icon = nativeImage.createFromPath(iconPath);
      if (!icon.isEmpty()) {
        return icon;
      }
    } catch (error) {
      console.error('加载托盘图标失败:', error);
    }
    
    // 返回默认图标
    return path.join(__dirname, '../build/icon.png');
  }

  /**
   * 更新菜单
   */
  updateMenu() {
    const menu = Menu.buildFromTemplate([
      {
        label: '📊 系统状态',
        enabled: false,
        type: 'normal'
      },
      {
        label: `${this.getStatusEmoji()} 状态：${this.getStatusText()}`,
        enabled: false
      },
      { type: 'separator' },
      
      {
        label: '📈 今日统计',
        enabled: false
      },
      {
        label: `  转发消息：${this.stats.today_total} 条`,
        enabled: false
      },
      {
        label: `  成功率：${this.stats.success_rate}%`,
        enabled: false
      },
      {
        label: `  平均延迟：${this.stats.avg_latency} ms`,
        enabled: false
      },
      {
        label: `  队列消息：${this.stats.queue_size} 条`,
        enabled: false
      },
      { type: 'separator' },
      
      {
        label: '🔢 配置统计',
        enabled: false
      },
      {
        label: `  账号数：${this.stats.account_count} 个`,
        enabled: false
      },
      {
        label: `  Bot数：${this.stats.bot_count} 个`,
        enabled: false
      },
      {
        label: `  运行时长：${this.formatUptime(this.stats.uptime)}`,
        enabled: false
      },
      { type: 'separator' },
      
      {
        label: '⚡ 快捷操作',
        enabled: false
      },
      {
        label: this.stats.running ? '⏸️  停止服务' : '▶️  启动服务',
        click: () => this.toggleService()
      },
      {
        label: '🔄 重启服务',
        click: () => this.restartService(),
        enabled: this.stats.running
      },
      {
        label: '🧪 测试转发',
        click: () => this.testForwarding()
      },
      { type: 'separator' },
      
      {
        label: '📺 显示主窗口',
        click: () => this.showMainWindow()
      },
      {
        label: '⚙️  设置',
        click: () => this.openSettings()
      },
      {
        label: '📋 日志',
        click: () => this.openLogs()
      },
      { type: 'separator' },
      
      {
        label: '❌ 退出',
        click: () => this.quitApp()
      }
    ]);

    this.tray.setContextMenu(menu);
  }

  /**
   * 获取状态表情符号
   */
  getStatusEmoji() {
    const emojiMap = {
      'offline': '⚪',
      'running': '🟢',
      'reconnecting': '🟡',
      'error': '🔴'
    };
    return emojiMap[this.currentStatus] || '⚪';
  }

  /**
   * 获取状态文本
   */
  getStatusText() {
    const textMap = {
      'offline': '已停止',
      'running': '运行中',
      'reconnecting': '重连中',
      'error': '错误'
    };
    return textMap[this.currentStatus] || '未知';
  }

  /**
   * 格式化运行时长
   */
  formatUptime(seconds) {
    if (seconds < 60) {
      return `${seconds}秒`;
    } else if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60);
      return `${minutes}分钟`;
    } else if (seconds < 86400) {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      return `${hours}小时${minutes}分钟`;
    } else {
      const days = Math.floor(seconds / 86400);
      const hours = Math.floor((seconds % 86400) / 3600);
      return `${days}天${hours}小时`;
    }
  }

  /**
   * 更新统计信息
   */
  async updateStats() {
    try {
      // 调用后端API获取统计信息
      const response = await axios.get('http://localhost:9527/api/system/stats', {
        timeout: 3000
      });
      
      const data = response.data;
      
      this.stats = {
        running: data.service_running || false,
        today_total: data.today_total || 0,
        success_rate: data.success_rate || 0,
        avg_latency: data.avg_latency || 0,
        queue_size: data.queue_size || 0,
        account_count: data.account_count || 0,
        bot_count: data.bot_count || 0,
        uptime: data.uptime || 0
      };
      
      // 更新状态
      if (data.service_running) {
        if (data.has_errors) {
          this.updateStatus('error');
        } else if (data.reconnecting) {
          this.updateStatus('reconnecting');
        } else {
          this.updateStatus('running');
        }
      } else {
        this.updateStatus('offline');
      }
      
      // 更新菜单
      this.updateMenu();
      
    } catch (error) {
      console.error('更新统计信息失败:', error);
      // 如果无法连接，设置为离线状态
      this.updateStatus('offline');
      this.updateMenu();
    }
  }

  /**
   * 更新状态
   */
  updateStatus(status) {
    if (this.currentStatus !== status) {
      this.currentStatus = status;
      
      // 更新托盘图标
      const icon = this.getStatusIcon(status);
      this.tray.setImage(icon);
      
      // 更新提示文本
      const tooltip = `KOOK消息转发系统 - ${this.getStatusText()}`;
      this.tray.setToolTip(tooltip);
    }
  }

  /**
   * 启动自动更新
   */
  startAutoUpdate() {
    // 立即更新一次
    this.updateStats();
    
    // 每5秒更新一次
    this.updateInterval = setInterval(() => {
      this.updateStats();
    }, 5000);
  }

  /**
   * 停止自动更新
   */
  stopAutoUpdate() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
  }

  /**
   * 切换服务状态
   */
  async toggleService() {
    try {
      const action = this.stats.running ? 'stop' : 'start';
      await axios.post(`http://localhost:9527/api/system/service/${action}`, {}, {
        timeout: 5000
      });
      
      // 立即更新统计
      setTimeout(() => this.updateStats(), 1000);
    } catch (error) {
      console.error('切换服务状态失败:', error);
    }
  }

  /**
   * 重启服务
   */
  async restartService() {
    try {
      await axios.post('http://localhost:9527/api/system/service/restart', {}, {
        timeout: 5000
      });
      
      // 立即更新统计
      setTimeout(() => this.updateStats(), 1000);
    } catch (error) {
      console.error('重启服务失败:', error);
    }
  }

  /**
   * 测试转发
   */
  async testForwarding() {
    try {
      await axios.post('http://localhost:9527/api/system/test-forwarding', {}, {
        timeout: 10000
      });
    } catch (error) {
      console.error('测试转发失败:', error);
    }
  }

  /**
   * 显示主窗口
   */
  showMainWindow() {
    if (this.mainWindow) {
      this.mainWindow.show();
      this.mainWindow.focus();
      
      if (process.platform === 'darwin') {
        const { app } = require('electron');
        app.dock.show();
      }
    }
  }

  /**
   * 打开设置
   */
  openSettings() {
    this.showMainWindow();
    this.mainWindow?.webContents.send('navigate-to', '/settings');
  }

  /**
   * 打开日志
   */
  openLogs() {
    this.showMainWindow();
    this.mainWindow?.webContents.send('navigate-to', '/logs');
  }

  /**
   * 退出应用
   */
  quitApp() {
    const { app } = require('electron');
    app.quit();
  }

  /**
   * 销毁托盘
   */
  destroy() {
    this.stopAutoUpdate();
    
    if (this.tray) {
      this.tray.destroy();
      this.tray = null;
    }
  }
}

module.exports = EnhancedTrayManager;
