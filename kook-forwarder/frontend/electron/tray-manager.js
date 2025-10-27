/**
 * 系统托盘管理器 - 增强版
 * 功能：动态图标、实时状态、通知
 */

const { Tray, Menu, nativeImage, Notification } = require('electron');
const path = require('path');

class TrayManager {
  constructor(mainWindow) {
    this.mainWindow = mainWindow;
    this.tray = null;
    this.status = 'offline'; // online, connecting, error, offline
    this.stats = {
      messages_today: 0,
      success_rate: 0,
      avg_latency: 0,
      queue_size: 0,
      active_accounts: 0,
      configured_bots: 0,
      uptime_seconds: 0
    };
    
    // ✅ P1-1优化：添加统计刷新定时器
    this.statsUpdateInterval = null;
    this.backendUrl = 'http://localhost:9527';
    
    // 图标路径
    this.icons = {
      online: path.join(__dirname, '../build/icons/tray-online.png'),
      connecting: path.join(__dirname, '../build/icons/tray-connecting.png'),
      error: path.join(__dirname, '../build/icons/tray-error.png'),
      offline: path.join(__dirname, '../build/icons/tray-offline.png'),
    };
    
    // 检查图标是否存在，不存在则使用默认图标
    const fs = require('fs');
    Object.keys(this.icons).forEach(key => {
      if (!fs.existsSync(this.icons[key])) {
        this.icons[key] = path.join(__dirname, '../build/icon.png');
      }
    });
  }
  
  create() {
    try {
      // 创建托盘图标
      const icon = nativeImage.createFromPath(this.icons.offline);
      this.tray = new Tray(icon);
      
      // 设置初始tooltip
      this.tray.setToolTip('KOOK消息转发系统 - 已停止');
      
      // 设置上下文菜单
      this.updateContextMenu();
      
      // 双击显示主窗口
      this.tray.on('double-click', () => {
        this.showMainWindow();
      });
      
      // ✅ P1-1优化：启动统计自动刷新（每5秒）
      this.startStatsUpdate();
      
      console.log('[TrayManager] 系统托盘已创建');
    } catch (error) {
      console.error('[TrayManager] 创建托盘失败:', error);
    }
  }
  
  // ✅ P1-1新增：启动统计自动刷新
  startStatsUpdate() {
    // 立即获取一次
    this.fetchStats();
    
    // 每5秒自动刷新
    this.statsUpdateInterval = setInterval(() => {
      this.fetchStats();
    }, 5000);
    
    console.log('[TrayManager] 统计自动刷新已启动（每5秒）');
  }
  
  // ✅ P1-1新增：停止统计自动刷新
  stopStatsUpdate() {
    if (this.statsUpdateInterval) {
      clearInterval(this.statsUpdateInterval);
      this.statsUpdateInterval = null;
      console.log('[TrayManager] 统计自动刷新已停止');
    }
  }
  
  // ✅ P0-9优化：从后端获取增强的统计数据
  async fetchStats() {
    try {
      const fetch = require('node-fetch');
      const response = await fetch(`${this.backendUrl}/api/tray-stats/realtime`);
      
      if (response.ok) {
        const result = await response.json();
        
        if (result.success && result.stats) {
          const data = result.stats;
          
          // 更新统计数据（7项核心统计）
          this.stats = {
            messages_today: data.today_messages || 0,
            success_rate: parseFloat(data.success_rate_text) || 0,
            avg_latency: data.avg_latency_ms || 0,
            avg_latency_text: data.avg_latency_text || 'N/A',
            queue_size: data.queue_size || 0,
            queue_status: data.queue_status || '空闲',
            active_accounts: data.active_accounts || 0,
            total_accounts: data.total_accounts || 0,
            active_bots: data.active_bots || 0,
            total_bots: data.total_bots || 0,
            uptime_seconds: data.uptime_seconds || 0,
            uptime_text: data.uptime_text || '0分钟',
            last_message_time: data.last_message_time || '暂无',
            errors_today: data.errors_today || 0
          };
          
          // 更新系统状态
          if (data.status) {
            this.status = data.status;
          }
          
          // 更新上下文菜单
          this.updateContextMenu();
          
          console.log('[TrayManager] 统计数据已更新:', {
            status: data.status_text,
            messages: this.stats.messages_today,
            rate: this.stats.success_rate
          });
        }
      } else {
        console.warn('[TrayManager] 获取统计失败:', response.status);
      }
    } catch (error) {
      // 静默失败，避免频繁报错（但记录到控制台用于调试）
      console.debug('[TrayManager] 获取统计异常:', error.message);
    }
  }
  
  updateStatus(status, message) {
    if (!this.tray) return;
    
    this.status = status;
    
    try {
      // 更新托盘图标
      if (this.icons[status]) {
        const icon = nativeImage.createFromPath(this.icons[status]);
        this.tray.setImage(icon);
      }
      
      // 更新tooltip
      const tooltips = {
        online: `🟢 KOOK转发系统 - 运行中\n${message || '服务正常运行'}`,
        connecting: `🟡 KOOK转发系统 - 重连中\n${message || '正在尝试重新连接...'}`,
        error: `🔴 KOOK转发系统 - 异常\n${message || '服务出现异常'}`,
        offline: `⚪ KOOK转发系统 - 已停止`,
      };
      
      this.tray.setToolTip(tooltips[status] || tooltips.offline);
      
      // 如果是错误状态，显示通知
      if (status === 'error' && message) {
        this.showNotification('服务异常', message, 'error');
      }
      
      // 更新上下文菜单
      this.updateContextMenu();
      
      console.log(`[TrayManager] 状态更新: ${status} - ${message}`);
    } catch (error) {
      console.error('[TrayManager] 更新状态失败:', error);
    }
  }
  
  updateStats(stats) {
    if (!this.tray) return;
    
    // 更新统计数据
    Object.assign(this.stats, stats);
    
    // 更新上下文菜单（显示统计信息）
    this.updateContextMenu();
  }
  
  updateContextMenu() {
    if (!this.tray) return;
    
    try {
      // ✅ P1-1优化：格式化运行时长
      const formatUptime = (seconds) => {
        const hours = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        if (hours > 0) {
          return `${hours}小时${mins}分钟`;
        }
        return `${mins}分钟`;
      };
      
      const menu = Menu.buildFromTemplate([
        // ✅ P1-1优化：增强的统计信息区域（7项统计）
        {
          label: '📊 实时统计（每5秒刷新）',
          enabled: false,
        },
        {
          label: `  今日转发: ${this.stats.messages_today} 条`,
          enabled: false,
        },
        {
          label: `  成功率: ${this.stats.success_rate}%`,
          enabled: false,
        },
        {
          label: `  平均延迟: ${this.stats.avg_latency}ms`,
          enabled: false,
        },
        {
          label: `  队列中: ${this.stats.queue_size} 条`,
          enabled: false,
        },
        {
          label: `  活跃账号: ${this.stats.active_accounts} 个`,
          enabled: false,
        },
        {
          label: `  配置Bot: ${this.stats.configured_bots} 个`,
          enabled: false,
        },
        {
          label: `  运行时长: ${formatUptime(this.stats.uptime_seconds)}`,
          enabled: false,
        },
        { type: 'separator' },
        
        // 主要操作
        {
          label: '显示主窗口',
          icon: this.createMenuIcon('window'),
          click: () => {
            this.showMainWindow();
          },
        },
        { type: 'separator' },
        
        // 服务控制
        {
          label: '服务控制',
          submenu: [
            {
              label: '启动服务',
              icon: this.createMenuIcon('play'),
              enabled: this.status === 'offline',
              click: () => {
                this.sendToRenderer('tray-action', 'start-service');
              },
            },
            {
              label: '停止服务',
              icon: this.createMenuIcon('stop'),
              enabled: this.status === 'online',
              click: () => {
                this.sendToRenderer('tray-action', 'stop-service');
              },
            },
            {
              label: '重启服务',
              icon: this.createMenuIcon('restart'),
              enabled: this.status === 'online',
              click: () => {
                this.sendToRenderer('tray-action', 'restart-service');
              },
            },
          ],
        },
        { type: 'separator' },
        
        // 快捷操作
        {
          label: '快捷操作',
          submenu: [
            {
              label: '测试转发',
              click: () => {
                this.sendToRenderer('tray-action', 'test-forward');
              },
            },
            {
              label: '清空队列',
              enabled: this.stats.queue_size > 0,
              click: () => {
                this.sendToRenderer('tray-action', 'clear-queue');
              },
            },
            {
              label: '打开日志',
              click: () => {
                this.sendToRenderer('tray-action', 'open-logs');
              },
            },
          ],
        },
        { type: 'separator' },
        
        // 设置
        {
          label: '设置',
          icon: this.createMenuIcon('settings'),
          click: () => {
            this.sendToRenderer('tray-action', 'open-settings');
            this.showMainWindow();
          },
        },
        { type: 'separator' },
        
        // 退出
        {
          label: '退出',
          icon: this.createMenuIcon('quit'),
          click: () => {
            this.quitApp();
          },
        },
      ]);
      
      this.tray.setContextMenu(menu);
    } catch (error) {
      console.error('[TrayManager] 更新菜单失败:', error);
    }
  }
  
  createMenuIcon(type) {
    // 为菜单项创建小图标（可选）
    // 这里返回null，实际可以创建小的16x16图标
    return null;
  }
  
  showMainWindow() {
    if (this.mainWindow) {
      if (this.mainWindow.isMinimized()) {
        this.mainWindow.restore();
      }
      this.mainWindow.show();
      this.mainWindow.focus();
      
      // macOS特殊处理
      if (process.platform === 'darwin') {
        const { app } = require('electron');
        app.dock.show();
      }
    }
  }
  
  sendToRenderer(channel, data) {
    if (this.mainWindow && this.mainWindow.webContents) {
      this.mainWindow.webContents.send(channel, data);
    }
  }
  
  showNotification(title, body, type = 'info') {
    try {
      const notification = new Notification({
        title,
        body,
        icon: this.icons[this.status] || this.icons.offline,
        urgency: type === 'error' ? 'critical' : 'normal',
        silent: false,
      });
      
      notification.on('click', () => {
        this.showMainWindow();
      });
      
      notification.show();
      
      console.log(`[TrayManager] 通知已显示: ${title}`);
    } catch (error) {
      console.error('[TrayManager] 显示通知失败:', error);
    }
  }
  
  quitApp() {
    const { dialog, app } = require('electron');
    
    dialog.showMessageBox(this.mainWindow, {
      type: 'question',
      buttons: ['取消', '退出'],
      defaultId: 0,
      cancelId: 0,
      title: '确认退出',
      message: '确定要退出KOOK消息转发系统吗？',
      detail: '正在进行的消息转发将被中断。',
    }).then(result => {
      if (result.response === 1) {
        app.quit();
      }
    });
  }
  
  destroy() {
    // ✅ P1-1优化：停止统计刷新
    this.stopStatsUpdate();
    
    if (this.tray) {
      this.tray.destroy();
      this.tray = null;
      console.log('[TrayManager] 系统托盘已销毁');
    }
  }
  
  // 闪烁图标（吸引注意）
  flashIcon(times = 3, interval = 500) {
    let count = 0;
    const originalIcon = this.icons[this.status];
    
    const flashInterval = setInterval(() => {
      if (count >= times * 2) {
        clearInterval(flashInterval);
        // 恢复原图标
        if (this.tray) {
          const icon = nativeImage.createFromPath(originalIcon);
          this.tray.setImage(icon);
        }
        return;
      }
      
      if (this.tray) {
        const icon = count % 2 === 0
          ? nativeImage.createFromPath(this.icons.error)
          : nativeImage.createFromPath(originalIcon);
        this.tray.setImage(icon);
      }
      
      count++;
    }, interval);
  }
}

module.exports = TrayManager;
