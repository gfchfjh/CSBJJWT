/**
 * 增强系统托盘管理器 - P1-3优化
 * 特性:
 * - 5秒自动刷新统计
 * - 实时消息通知
 * - 一键启动/停止
 * - 状态图标动态变化
 */
const { Tray, Menu, nativeImage, Notification } = require('electron');
const path = require('path');
const axios = require('axios');

class TrayManagerEnhanced {
    constructor(mainWindow) {
        this.mainWindow = mainWindow;
        this.tray = null;
        this.updateInterval = null;
        this.stats = {
            total_forwarded: 0,
            success_rate: 0,
            queue_size: 0,
            service_status: 'stopped',
            last_message_time: null
        };
        
        // 通知设置
        this.notificationSettings = {
            enabled: true,
            errorOnly: false,
            successNotify: false
        };
        
        // 上次通知时间（防止刷屏）
        this.lastNotificationTime = 0;
        this.notificationCooldown = 10000; // 10秒冷却
    }
    
    /**
     * 创建托盘
     */
    create() {
        try {
            // 创建托盘图标
            const iconPath = this.getIconPath('stopped');
            const icon = nativeImage.createFromPath(iconPath);
            
            this.tray = new Tray(icon.resize({ width: 16, height: 16 }));
            this.tray.setToolTip('KOOK消息转发系统');
            
            // 创建上下文菜单
            this.updateContextMenu();
            
            // 点击托盘图标显示/隐藏窗口
            this.tray.on('click', () => {
                if (this.mainWindow) {
                    if (this.mainWindow.isVisible()) {
                        this.mainWindow.hide();
                    } else {
                        this.mainWindow.show();
                        this.mainWindow.focus();
                    }
                }
            });
            
            console.log('✅ 托盘已创建');
            
            // 启动自动刷新（5秒间隔）
            this.startAutoUpdate();
            
        } catch (error) {
            console.error('❌ 创建托盘失败:', error);
        }
    }
    
    /**
     * 获取图标路径
     */
    getIconPath(status) {
        const iconMap = {
            'running': 'icon-running.png',
            'stopped': 'icon-stopped.png',
            'error': 'icon-error.png',
            'warning': 'icon-warning.png'
        };
        
        const iconFile = iconMap[status] || 'icon.png';
        
        // 尝试多个可能的路径
        const possiblePaths = [
            path.join(__dirname, '..', 'public', iconFile),
            path.join(__dirname, '..', '..', 'public', iconFile),
            path.join(process.resourcesPath, 'public', iconFile),
            path.join(__dirname, '..', 'build', iconFile),
        ];
        
        for (const iconPath of possiblePaths) {
            try {
                if (require('fs').existsSync(iconPath)) {
                    return iconPath;
                }
            } catch (e) {
                // ignore
            }
        }
        
        // 默认使用 icon.png
        return path.join(__dirname, '..', 'public', 'icon.png');
    }
    
    /**
     * 更新上下文菜单
     */
    updateContextMenu() {
        if (!this.tray) return;
        
        const { total_forwarded, success_rate, queue_size, service_status } = this.stats;
        
        // 构建菜单
        const contextMenu = Menu.buildFromTemplate([
            {
                label: '📊 实时统计',
                type: 'normal',
                enabled: false
            },
            {
                label: `  转发总数: ${total_forwarded}`,
                type: 'normal',
                enabled: false
            },
            {
                label: `  成功率: ${(success_rate * 100).toFixed(1)}%`,
                type: 'normal',
                enabled: false
            },
            {
                label: `  队列消息: ${queue_size}`,
                type: 'normal',
                enabled: false
            },
            { type: 'separator' },
            {
                label: service_status === 'running' ? '⏸️  停止服务' : '▶️  启动服务',
                type: 'normal',
                click: () => this.toggleService()
            },
            {
                label: '🔄 重启服务',
                type: 'normal',
                click: () => this.restartService()
            },
            { type: 'separator' },
            {
                label: '🔔 通知设置',
                type: 'submenu',
                submenu: [
                    {
                        label: '启用通知',
                        type: 'checkbox',
                        checked: this.notificationSettings.enabled,
                        click: (item) => {
                            this.notificationSettings.enabled = item.checked;
                        }
                    },
                    {
                        label: '仅错误通知',
                        type: 'checkbox',
                        checked: this.notificationSettings.errorOnly,
                        click: (item) => {
                            this.notificationSettings.errorOnly = item.checked;
                        }
                    },
                    {
                        label: '成功通知',
                        type: 'checkbox',
                        checked: this.notificationSettings.successNotify,
                        click: (item) => {
                            this.notificationSettings.successNotify = item.checked;
                        }
                    }
                ]
            },
            { type: 'separator' },
            {
                label: '📁 打开主窗口',
                type: 'normal',
                click: () => {
                    if (this.mainWindow) {
                        this.mainWindow.show();
                        this.mainWindow.focus();
                    }
                }
            },
            {
                label: '📋 查看日志',
                type: 'normal',
                click: () => this.openLogs()
            },
            { type: 'separator' },
            {
                label: '❌ 退出',
                type: 'normal',
                click: () => {
                    this.destroy();
                    if (this.mainWindow) {
                        this.mainWindow.close();
                    }
                }
            }
        ]);
        
        this.tray.setContextMenu(contextMenu);
    }
    
    /**
     * 启动自动更新
     */
    startAutoUpdate() {
        console.log('🔄 启动托盘自动刷新（5秒间隔）');
        
        // 立即更新一次
        this.updateStats();
        
        // 每5秒更新一次
        this.updateInterval = setInterval(() => {
            this.updateStats();
        }, 5000);
    }
    
    /**
     * 更新统计数据
     */
    async updateStats() {
        try {
            // 请求后端API获取实时统计
            const response = await axios.get('http://localhost:9527/api/stats/realtime', {
                timeout: 3000
            });
            
            if (response.data) {
                const newStats = response.data;
                
                // 检测变化并触发通知
                this.checkAndNotify(newStats);
                
                // 更新本地统计
                this.stats = {
                    total_forwarded: newStats.total_forwarded || 0,
                    success_rate: newStats.success_rate || 0,
                    queue_size: newStats.queue_size || 0,
                    service_status: newStats.service_status || 'stopped',
                    last_message_time: newStats.last_message_time
                };
                
                // 更新托盘图标和菜单
                this.updateTrayIcon();
                this.updateContextMenu();
                this.updateTooltip();
            }
            
        } catch (error) {
            // 连接失败，可能服务未启动
            if (this.stats.service_status !== 'stopped') {
                this.stats.service_status = 'stopped';
                this.updateTrayIcon();
                this.updateContextMenu();
            }
        }
    }
    
    /**
     * 检测变化并发送通知
     */
    checkAndNotify(newStats) {
        if (!this.notificationSettings.enabled) return;
        
        // 防止通知刷屏
        const now = Date.now();
        if (now - this.lastNotificationTime < this.notificationCooldown) {
            return;
        }
        
        // 队列堆积警告（超过100条）
        if (newStats.queue_size > 100 && this.stats.queue_size <= 100) {
            this.showNotification('⚠️ 队列堆积', `队列中有 ${newStats.queue_size} 条消息待处理`, 'warning');
            this.lastNotificationTime = now;
        }
        
        // 成功率下降警告（低于80%）
        if (newStats.success_rate < 0.8 && this.stats.success_rate >= 0.8) {
            this.showNotification('⚠️ 成功率下降', `当前成功率: ${(newStats.success_rate * 100).toFixed(1)}%`, 'warning');
            this.lastNotificationTime = now;
        }
        
        // 服务状态变化通知
        if (newStats.service_status !== this.stats.service_status) {
            if (newStats.service_status === 'running') {
                this.showNotification('✅ 服务已启动', 'KOOK消息转发服务正在运行', 'info');
            } else if (newStats.service_status === 'error') {
                this.showNotification('❌ 服务异常', '服务运行出现错误', 'error');
            }
            this.lastNotificationTime = now;
        }
        
        // 新消息通知（如果启用）
        if (this.notificationSettings.successNotify) {
            if (newStats.total_forwarded > this.stats.total_forwarded) {
                const newCount = newStats.total_forwarded - this.stats.total_forwarded;
                this.showNotification('✉️ 新消息', `成功转发 ${newCount} 条消息`, 'info');
                this.lastNotificationTime = now;
            }
        }
    }
    
    /**
     * 显示通知
     */
    showNotification(title, body, type = 'info') {
        try {
            // 检查通知设置
            if (type === 'error' && !this.notificationSettings.errorOnly) {
                // 如果设置了仅错误通知，但当前不是错误，跳过
                if (this.notificationSettings.errorOnly && type !== 'error') {
                    return;
                }
            }
            
            const notification = new Notification({
                title: title,
                body: body,
                icon: this.getIconPath('running'),
                silent: type !== 'error'
            });
            
            notification.show();
            
            console.log(`📢 通知: ${title} - ${body}`);
            
        } catch (error) {
            console.error('显示通知失败:', error);
        }
    }
    
    /**
     * 更新托盘图标
     */
    updateTrayIcon() {
        if (!this.tray) return;
        
        try {
            let status = 'stopped';
            
            if (this.stats.service_status === 'running') {
                if (this.stats.success_rate < 0.8) {
                    status = 'warning';
                } else {
                    status = 'running';
                }
            } else if (this.stats.service_status === 'error') {
                status = 'error';
            }
            
            const iconPath = this.getIconPath(status);
            const icon = nativeImage.createFromPath(iconPath);
            this.tray.setImage(icon.resize({ width: 16, height: 16 }));
            
        } catch (error) {
            console.error('更新托盘图标失败:', error);
        }
    }
    
    /**
     * 更新工具提示
     */
    updateTooltip() {
        if (!this.tray) return;
        
        const { total_forwarded, success_rate, queue_size, service_status } = this.stats;
        
        const statusText = {
            'running': '运行中',
            'stopped': '已停止',
            'error': '错误'
        }[service_status] || '未知';
        
        const tooltip = `KOOK消息转发系统
状态: ${statusText}
转发: ${total_forwarded} 条
成功率: ${(success_rate * 100).toFixed(1)}%
队列: ${queue_size} 条`;
        
        this.tray.setToolTip(tooltip);
    }
    
    /**
     * 切换服务状态
     */
    async toggleService() {
        try {
            const action = this.stats.service_status === 'running' ? 'stop' : 'start';
            
            await axios.post(`http://localhost:9527/api/service/${action}`, {}, {
                timeout: 5000
            });
            
            this.showNotification(
                action === 'start' ? '✅ 服务已启动' : '⏸️ 服务已停止',
                action === 'start' ? '开始转发消息' : '停止转发消息',
                'info'
            );
            
            // 立即更新统计
            setTimeout(() => this.updateStats(), 1000);
            
        } catch (error) {
            console.error('切换服务失败:', error);
            this.showNotification('❌ 操作失败', '无法连接到后端服务', 'error');
        }
    }
    
    /**
     * 重启服务
     */
    async restartService() {
        try {
            await axios.post('http://localhost:9527/api/service/restart', {}, {
                timeout: 10000
            });
            
            this.showNotification('🔄 服务重启中', '正在重启服务...', 'info');
            
            // 3秒后更新统计
            setTimeout(() => this.updateStats(), 3000);
            
        } catch (error) {
            console.error('重启服务失败:', error);
            this.showNotification('❌ 重启失败', '无法连接到后端服务', 'error');
        }
    }
    
    /**
     * 打开日志
     */
    openLogs() {
        // 发送IPC消息到主窗口
        if (this.mainWindow) {
            this.mainWindow.webContents.send('navigate-to', '/logs');
            this.mainWindow.show();
            this.mainWindow.focus();
        }
    }
    
    /**
     * 销毁托盘
     */
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        
        if (this.tray) {
            this.tray.destroy();
            this.tray = null;
        }
        
        console.log('🗑️ 托盘已销毁');
    }
}

module.exports = TrayManagerEnhanced;
