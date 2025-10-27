/**
 * 系统托盘管理模块
 * 独立的托盘功能模块，提供更灵活的托盘管理
 */

const { Tray, Menu, nativeImage } = require('electron');
const path = require('path');

class TrayManager {
  constructor() {
    this.tray = null;
    this.mainWindow = null;
    this.serviceStatus = 'stopped'; // stopped, running, error
    this.stats = {
      todayCount: 0,
      successRate: 0,
      queueSize: 0,
    };
  }

  /**
   * 初始化托盘
   */
  init(mainWindow, iconPath) {
    this.mainWindow = mainWindow;

    // 创建托盘图标
    const icon = nativeImage.createFromPath(iconPath);
    this.tray = new Tray(icon.resize({ width: 16, height: 16 }));

    // 设置初始菜单
    this.updateMenu();

    // 设置工具提示
    this.updateTooltip();

    // 双击事件
    this.tray.on('double-click', () => {
      this.showWindow();
    });

    console.log('[Tray] 系统托盘已初始化');
  }

  /**
   * 更新托盘菜单
   */
  updateMenu() {
    if (!this.tray) return;

    const serviceItems = [];
    
    if (this.serviceStatus === 'running') {
      serviceItems.push({
        label: '✅ 服务运行中',
        enabled: false,
      });
      serviceItems.push({
        label: '停止服务',
        click: () => this.emit('stop-service'),
      });
      serviceItems.push({
        label: '重启服务',
        click: () => this.emit('restart-service'),
      });
    } else if (this.serviceStatus === 'stopped') {
      serviceItems.push({
        label: '⏹️  服务已停止',
        enabled: false,
      });
      serviceItems.push({
        label: '启动服务',
        click: () => this.emit('start-service'),
      });
    } else {
      serviceItems.push({
        label: '❌ 服务异常',
        enabled: false,
      });
      serviceItems.push({
        label: '重启服务',
        click: () => this.emit('restart-service'),
      });
    }

    // 构建菜单
    const contextMenu = Menu.buildFromTemplate([
      {
        label: '显示主窗口',
        click: () => this.showWindow(),
      },
      { type: 'separator' },
      ...serviceItems,
      { type: 'separator' },
      {
        label: '📊 今日统计',
        enabled: false,
      },
      {
        label: `   转发消息: ${this.stats.todayCount}`,
        enabled: false,
      },
      {
        label: `   成功率: ${this.stats.successRate}%`,
        enabled: false,
      },
      {
        label: `   队列: ${this.stats.queueSize}`,
        enabled: false,
      },
      { type: 'separator' },
      {
        label: '快捷操作',
        submenu: [
          {
            label: '账号管理',
            click: () => this.emit('open-accounts'),
          },
          {
            label: 'Bot配置',
            click: () => this.emit('open-bots'),
          },
          {
            label: '频道映射',
            click: () => this.emit('open-mapping'),
          },
          {
            label: '查看日志',
            click: () => this.emit('open-logs'),
          },
        ],
      },
      { type: 'separator' },
      {
        label: '设置',
        click: () => this.emit('open-settings'),
      },
      {
        label: '帮助',
        click: () => this.emit('open-help'),
      },
      { type: 'separator' },
      {
        label: '退出',
        click: () => this.emit('quit'),
      },
    ]);

    this.tray.setContextMenu(contextMenu);
  }

  /**
   * 更新工具提示
   */
  updateTooltip() {
    if (!this.tray) return;

    let tooltip = 'KOOK消息转发系统\n';
    
    if (this.serviceStatus === 'running') {
      tooltip += `状态: 运行中\n`;
      tooltip += `今日转发: ${this.stats.todayCount} 条\n`;
      tooltip += `成功率: ${this.stats.successRate}%\n`;
      tooltip += `队列: ${this.stats.queueSize} 条`;
    } else if (this.serviceStatus === 'stopped') {
      tooltip += '状态: 已停止';
    } else {
      tooltip += '状态: 异常';
    }

    this.tray.setToolTip(tooltip);
  }

  /**
   * 更新服务状态
   */
  updateServiceStatus(status) {
    this.serviceStatus = status;
    this.updateMenu();
    this.updateTooltip();
  }

  /**
   * 更新统计信息
   */
  updateStats(stats) {
    this.stats = { ...this.stats, ...stats };
    this.updateMenu();
    this.updateTooltip();
  }

  /**
   * 显示主窗口
   */
  showWindow() {
    if (this.mainWindow) {
      if (this.mainWindow.isMinimized()) {
        this.mainWindow.restore();
      }
      this.mainWindow.show();
      this.mainWindow.focus();
      
      // macOS 显示 Dock 图标
      if (process.platform === 'darwin') {
        const { app } = require('electron');
        app.dock.show();
      }
    }
  }

  /**
   * 发送事件到渲染进程
   */
  emit(action) {
    if (this.mainWindow) {
      this.mainWindow.webContents.send('tray-action', action);
    }
  }

  /**
   * 显示通知
   */
  showNotification(title, message, type = 'info') {
    // 可以在这里添加系统通知
    console.log(`[Tray] 通知: ${title} - ${message}`);
  }

  /**
   * 闪烁托盘图标（用于提醒）
   */
  flash(count = 3) {
    if (!this.tray) return;

    let flashCount = 0;
    const interval = setInterval(() => {
      if (flashCount >= count * 2) {
        clearInterval(interval);
        return;
      }
      
      // TODO: 实现图标闪烁效果（需要两个图标：正常和高亮）
      flashCount++;
    }, 500);
  }

  /**
   * 销毁托盘
   */
  destroy() {
    if (this.tray) {
      this.tray.destroy();
      this.tray = null;
      console.log('[Tray] 系统托盘已销毁');
    }
  }
}

module.exports = TrayManager;
