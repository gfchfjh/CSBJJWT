# KOOK转发系统 - P2级别完整优化实施手册

**优先级**: P2 - 中（第三阶段执行）  
**总工作量**: 115小时  
**预期完成**: 3-4周（2-3人团队）

---

## 📋 目录

- [优化9: 实现系统托盘功能](#优化9-实现系统托盘功能)
- [优化10: 过滤规则UI重构](#优化10-过滤规则ui重构)
- [优化11: 日志页面性能优化](#优化11-日志页面性能优化)
- [优化12: 设置页面分类重构](#优化12-设置页面分类重构)

---

## 优化9: 实现系统托盘功能

### 📊 优化概览

**当前问题**:
- Electron应用未实现系统托盘
- 缺少后台运行能力
- 开机自启代码未集成

**目标**:
- 实现完整系统托盘功能
- 支持后台运行
- 实现开机自启动

**工作量**: 15小时

---

### 🎯 实施步骤

#### 步骤9.1: 实现Electron系统托盘（8小时）

**文件**: `frontend/electron/tray.js`

```javascript
/**
 * 系统托盘管理器
 */
const { app, Tray, Menu, nativeImage, dialog } = require('electron')
const path = require('path')
const AutoLaunch = require('auto-launch')

class TrayManager {
  constructor(mainWindow) {
    this.mainWindow = mainWindow
    this.tray = null
    this.autoLauncher = null
    
    this.initAutoLaunch()
  }

  /**
   * 初始化开机自启
   */
  initAutoLaunch() {
    this.autoLauncher = new AutoLaunch({
      name: 'KOOK消息转发系统',
      path: app.getPath('exe')
    })
  }

  /**
   * 创建系统托盘
   */
  create() {
    // 创建托盘图标
    const iconPath = this.getIconPath()
    const trayIcon = nativeImage.createFromPath(iconPath)
    
    // 创建托盘
    this.tray = new Tray(trayIcon.resize({ width: 16, height: 16 }))
    
    // 设置工具提示
    this.tray.setToolTip('KOOK消息转发系统')
    
    // 设置上下文菜单
    this.updateContextMenu()
    
    // 双击托盘图标显示/隐藏窗口
    this.tray.on('double-click', () => {
      this.toggleWindow()
    })
    
    // macOS: 单击显示窗口
    if (process.platform === 'darwin') {
      this.tray.on('click', () => {
        this.showWindow()
      })
    }
    
    console.log('✅ 系统托盘已创建')
  }

  /**
   * 获取图标路径
   */
  getIconPath() {
    const platform = process.platform
    let iconName

    if (platform === 'darwin') {
      iconName = 'icon-tray-mac.png'
    } else if (platform === 'win32') {
      iconName = 'icon-tray-win.ico'
    } else {
      iconName = 'icon-tray-linux.png'
    }

    return path.join(__dirname, '../build/icons', iconName)
  }

  /**
   * 更新状态图标
   */
  updateIcon(status) {
    if (!this.tray) return

    let iconName
    switch (status) {
      case 'running':
        iconName = 'icon-tray-running.png'
        this.tray.setImage(this.getStatusIconPath(iconName))
        this.tray.setToolTip('KOOK消息转发系统 - 运行中')
        break
      case 'paused':
        iconName = 'icon-tray-paused.png'
        this.tray.setImage(this.getStatusIconPath(iconName))
        this.tray.setToolTip('KOOK消息转发系统 - 已暂停')
        break
      case 'error':
        iconName = 'icon-tray-error.png'
        this.tray.setImage(this.getStatusIconPath(iconName))
        this.tray.setToolTip('KOOK消息转发系统 - 错误')
        break
      default:
        iconName = 'icon-tray.png'
        this.tray.setImage(this.getStatusIconPath(iconName))
        this.tray.setToolTip('KOOK消息转发系统')
    }
  }

  getStatusIconPath(iconName) {
    return path.join(__dirname, '../build/icons', iconName)
  }

  /**
   * 更新上下文菜单
   */
  updateContextMenu(serviceStatus = null) {
    if (!this.tray) return

    const isRunning = serviceStatus?.running || false
    const isPaused = serviceStatus?.paused || false

    const menuTemplate = [
      {
        label: '显示主界面',
        click: () => this.showWindow(),
        icon: this.getMenuIcon('show')
      },
      { type: 'separator' },
      {
        label: isRunning ? '暂停转发' : '开始转发',
        click: () => this.toggleService(),
        icon: this.getMenuIcon(isRunning ? 'pause' : 'start'),
        enabled: true
      },
      {
        label: '重启服务',
        click: () => this.restartService(),
        icon: this.getMenuIcon('restart'),
        enabled: isRunning
      },
      { type: 'separator' },
      {
        label: '统计信息',
        submenu: [
          {
            label: `今日转发: ${serviceStatus?.todayCount || 0} 条`,
            enabled: false
          },
          {
            label: `成功率: ${serviceStatus?.successRate || 0}%`,
            enabled: false
          },
          {
            label: `队列消息: ${serviceStatus?.queueSize || 0} 条`,
            enabled: false
          }
        ]
      },
      {
        label: '快捷操作',
        submenu: [
          {
            label: '查看日志',
            click: () => this.showLogs()
          },
          {
            label: '清空队列',
            click: () => this.clearQueue()
          },
          {
            label: '测试转发',
            click: () => this.testForwarding()
          }
        ]
      },
      { type: 'separator' },
      {
        label: '设置',
        submenu: [
          {
            label: '开机自启',
            type: 'checkbox',
            checked: this.getAutoLaunchStatus(),
            click: (item) => this.toggleAutoLaunch(item.checked)
          },
          {
            label: '关闭时最小化到托盘',
            type: 'checkbox',
            checked: this.getMinimizeOnClose(),
            click: (item) => this.toggleMinimizeOnClose(item.checked)
          },
          { type: 'separator' },
          {
            label: '打开设置',
            click: () => this.openSettings()
          }
        ]
      },
      { type: 'separator' },
      {
        label: '关于',
        click: () => this.showAbout()
      },
      {
        label: '退出',
        click: () => this.quitApp(),
        role: 'quit'
      }
    ]

    const contextMenu = Menu.buildFromTemplate(menuTemplate)
    this.tray.setContextMenu(contextMenu)
  }

  /**
   * 获取菜单图标
   */
  getMenuIcon(name) {
    // 根据平台返回相应图标
    // Windows/Linux 不支持菜单图标，返回 null
    if (process.platform !== 'darwin') {
      return null
    }

    const iconPath = path.join(__dirname, '../build/icons/menu', `${name}.png`)
    return nativeImage.createFromPath(iconPath).resize({ width: 16, height: 16 })
  }

  /**
   * 切换窗口显示/隐藏
   */
  toggleWindow() {
    if (this.mainWindow.isVisible()) {
      this.mainWindow.hide()
    } else {
      this.showWindow()
    }
  }

  /**
   * 显示主窗口
   */
  showWindow() {
    if (this.mainWindow.isMinimized()) {
      this.mainWindow.restore()
    }
    this.mainWindow.show()
    this.mainWindow.focus()
  }

  /**
   * 切换服务状态
   */
  async toggleService() {
    try {
      const { ipcMain } = require('electron')
      
      // 通知渲染进程切换服务状态
      this.mainWindow.webContents.send('toggle-service')
      
      // 显示通知
      this.showNotification('服务状态已切换')
    } catch (error) {
      console.error('切换服务失败:', error)
      this.showNotification('切换服务失败', 'error')
    }
  }

  /**
   * 重启服务
   */
  async restartService() {
    const response = await dialog.showMessageBox(this.mainWindow, {
      type: 'question',
      title: '确认重启',
      message: '确定要重启转发服务吗？',
      detail: '当前队列中的消息将保留',
      buttons: ['取消', '重启'],
      defaultId: 1,
      cancelId: 0
    })

    if (response.response === 1) {
      this.mainWindow.webContents.send('restart-service')
      this.showNotification('服务正在重启...')
    }
  }

  /**
   * 查看日志
   */
  showLogs() {
    this.showWindow()
    this.mainWindow.webContents.send('navigate-to', '/logs')
  }

  /**
   * 清空队列
   */
  async clearQueue() {
    const response = await dialog.showMessageBox(this.mainWindow, {
      type: 'warning',
      title: '确认清空',
      message: '确定要清空消息队列吗？',
      detail: '队列中的所有未处理消息将被删除，此操作不可恢复！',
      buttons: ['取消', '清空'],
      defaultId: 0,
      cancelId: 0
    })

    if (response.response === 1) {
      this.mainWindow.webContents.send('clear-queue')
      this.showNotification('队列已清空')
    }
  }

  /**
   * 测试转发
   */
  testForwarding() {
    this.showWindow()
    this.mainWindow.webContents.send('test-forwarding')
  }

  /**
   * 打开设置
   */
  openSettings() {
    this.showWindow()
    this.mainWindow.webContents.send('navigate-to', '/settings')
  }

  /**
   * 显示关于
   */
  showAbout() {
    dialog.showMessageBox(this.mainWindow, {
      type: 'info',
      title: '关于',
      message: 'KOOK消息转发系统',
      detail: `版本: ${app.getVersion()}\n\n一键部署 · 图形化配置 · 零代码门槛\n\n© 2025 KOOK Forwarder Team`,
      buttons: ['确定']
    })
  }

  /**
   * 退出应用
   */
  async quitApp() {
    const response = await dialog.showMessageBox(this.mainWindow, {
      type: 'question',
      title: '确认退出',
      message: '确定要退出应用吗？',
      detail: '退出后消息转发将停止',
      buttons: ['取消', '退出'],
      defaultId: 0,
      cancelId: 0
    })

    if (response.response === 1) {
      app.quit()
    }
  }

  /**
   * 获取开机自启状态
   */
  getAutoLaunchStatus() {
    // 从本地存储或配置读取
    const Store = require('electron-store')
    const store = new Store()
    return store.get('autoLaunch', false)
  }

  /**
   * 切换开机自启
   */
  async toggleAutoLaunch(enabled) {
    try {
      if (enabled) {
        await this.autoLauncher.enable()
        this.showNotification('已开启开机自启')
      } else {
        await this.autoLauncher.disable()
        this.showNotification('已关闭开机自启')
      }

      // 保存到本地存储
      const Store = require('electron-store')
      const store = new Store()
      store.set('autoLaunch', enabled)

      // 更新菜单
      this.updateContextMenu()
    } catch (error) {
      console.error('设置开机自启失败:', error)
      this.showNotification('设置失败', 'error')
    }
  }

  /**
   * 获取关闭时最小化设置
   */
  getMinimizeOnClose() {
    const Store = require('electron-store')
    const store = new Store()
    return store.get('minimizeOnClose', true)
  }

  /**
   * 切换关闭时最小化
   */
  toggleMinimizeOnClose(enabled) {
    const Store = require('electron-store')
    const store = new Store()
    store.set('minimizeOnClose', enabled)
    
    this.showNotification(
      enabled ? '关闭窗口时将最小化到托盘' : '关闭窗口时将退出应用'
    )
    
    this.updateContextMenu()
  }

  /**
   * 显示通知
   */
  showNotification(message, type = 'info') {
    const { Notification } = require('electron')
    
    if (Notification.isSupported()) {
      const notification = new Notification({
        title: 'KOOK消息转发系统',
        body: message,
        icon: this.getIconPath(),
        silent: type === 'info'
      })

      notification.show()
    }
  }

  /**
   * 销毁托盘
   */
  destroy() {
    if (this.tray) {
      this.tray.destroy()
      this.tray = null
      console.log('✅ 系统托盘已销毁')
    }
  }
}

module.exports = TrayManager
```

---

#### 步骤9.2: 集成托盘到主进程（4小时）

**文件**: `frontend/electron/main.js` (修改)

```javascript
const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')
const TrayManager = require('./tray')

let mainWindow = null
let trayManager = null

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, '../build/icon.png'),
    show: false  // 先不显示，等待ready-to-show
  })

  // 加载应用
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  // 窗口准备好后显示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
    mainWindow.focus()
  })

  // 窗口关闭事件
  mainWindow.on('close', (event) => {
    const Store = require('electron-store')
    const store = new Store()
    const minimizeOnClose = store.get('minimizeOnClose', true)

    if (minimizeOnClose && !app.isQuitting) {
      event.preventDefault()
      mainWindow.hide()
      
      // 显示通知
      trayManager.showNotification('应用已最小化到系统托盘')
    }
  })

  // 创建系统托盘
  trayManager = new TrayManager(mainWindow)
  trayManager.create()

  // 注册IPC监听器
  registerIpcHandlers()

  return mainWindow
}

/**
 * 注册IPC事件处理器
 */
function registerIpcHandlers() {
  // 更新托盘状态
  ipcMain.on('update-tray-status', (event, status) => {
    trayManager.updateIcon(status)
  })

  // 更新托盘菜单
  ipcMain.on('update-tray-menu', (event, serviceStatus) => {
    trayManager.updateContextMenu(serviceStatus)
  })

  // 显示通知
  ipcMain.on('show-notification', (event, { message, type }) => {
    trayManager.showNotification(message, type)
  })

  // 处理托盘发起的操作
  ipcMain.on('toggle-service', () => {
    // 渲染进程处理实际逻辑
    mainWindow.webContents.send('toggle-service')
  })

  ipcMain.on('restart-service', () => {
    mainWindow.webContents.send('restart-service')
  })

  ipcMain.on('clear-queue', () => {
    mainWindow.webContents.send('clear-queue')
  })

  ipcMain.on('test-forwarding', () => {
    mainWindow.webContents.send('test-forwarding')
  })

  ipcMain.on('navigate-to', (event, route) => {
    mainWindow.webContents.send('navigate-to', route)
  })
}

// 应用准备就绪
app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    } else {
      mainWindow.show()
    }
  })
})

// 所有窗口关闭
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    // Windows/Linux: 窗口全关闭时不退出应用（托盘运行）
    // macOS: 保持标准行为
  }
})

// 应用退出前
app.on('before-quit', () => {
  app.isQuitting = true
})

// 应用退出
app.on('quit', () => {
  if (trayManager) {
    trayManager.destroy()
  }
})
```

---

#### 步骤9.3: 前端集成托盘事件（3小时）

**文件**: `frontend/src/utils/tray.js`

```javascript
/**
 * 托盘事件处理
 */

// 更新托盘状态
export function updateTrayStatus(status) {
  if (window.electronAPI && window.electronAPI.updateTrayStatus) {
    window.electronAPI.updateTrayStatus(status)
  }
}

// 更新托盘菜单
export function updateTrayMenu(serviceStatus) {
  if (window.electronAPI && window.electronAPI.updateTrayMenu) {
    window.electronAPI.updateTrayMenu(serviceStatus)
  }
}

// 显示托盘通知
export function showTrayNotification(message, type = 'info') {
  if (window.electronAPI && window.electronAPI.showNotification) {
    window.electronAPI.showNotification({ message, type })
  }
}

// 监听托盘事件
export function setupTrayListeners(handlers) {
  if (!window.electronAPI) return

  // 切换服务
  if (handlers.onToggleService) {
    window.electronAPI.onToggleService(handlers.onToggleService)
  }

  // 重启服务
  if (handlers.onRestartService) {
    window.electronAPI.onRestartService(handlers.onRestartService)
  }

  // 清空队列
  if (handlers.onClearQueue) {
    window.electronAPI.onClearQueue(handlers.onClearQueue)
  }

  // 测试转发
  if (handlers.onTestForwarding) {
    window.electronAPI.onTestForwarding(handlers.onTestForwarding)
  }

  // 导航
  if (handlers.onNavigateTo) {
    window.electronAPI.onNavigateTo(handlers.onNavigateTo)
  }
}
```

**文件**: `frontend/src/App.vue` (修改)

```vue
<template>
  <router-view />
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSystemStore } from './store/system'
import { setupTrayListeners, updateTrayStatus, updateTrayMenu } from './utils/tray'
import api from './api'

const router = useRouter()
const systemStore = useSystemStore()

// 设置托盘事件监听
onMounted(() => {
  setupTrayListeners({
    // 切换服务
    onToggleService: async () => {
      try {
        if (systemStore.status.service_running) {
          await api.stopService()
        } else {
          await api.startService()
        }
      } catch (error) {
        console.error('切换服务失败:', error)
      }
    },

    // 重启服务
    onRestartService: async () => {
      try {
        await api.restartService()
      } catch (error) {
        console.error('重启服务失败:', error)
      }
    },

    // 清空队列
    onClearQueue: async () => {
      try {
        await api.clearQueue()
      } catch (error) {
        console.error('清空队列失败:', error)
      }
    },

    // 测试转发
    onTestForwarding: async () => {
      router.push('/logs')
      try {
        await api.testForwarding()
      } catch (error) {
        console.error('测试转发失败:', error)
      }
    },

    // 导航
    onNavigateTo: (route) => {
      router.push(route)
    }
  })

  // 定时更新托盘状态
  const updateInterval = setInterval(() => {
    updateTrayStatus(systemStore.status.service_running ? 'running' : 'paused')
    updateTrayMenu({
      running: systemStore.status.service_running,
      paused: !systemStore.status.service_running,
      todayCount: systemStore.stats.total || 0,
      successRate: systemStore.stats.success_rate || 0,
      queueSize: systemStore.status.queue_size || 0
    })
  }, 3000)

  onUnmounted(() => {
    clearInterval(updateInterval)
  })
})
</script>
```

---

## 优化10: 过滤规则UI重构

### 📊 优化概览

**当前问题**:
- 使用textarea输入关键词（不直观）
- 缺少标签式添加
- 缺少实时预览
- 缺少过滤统计

**目标**:
- 实现标签式关键词输入
- 增强用户选择器
- 实现实时预览功能
- 添加过滤统计信息

**工作量**: 25小时

---

### 🎯 实施步骤

#### 步骤10.1: 重构过滤规则页面（12小时）

**文件**: `frontend/src/views/Filter.vue` (完全重写)

```vue
<template>
  <div class="filter-view">
    <el-page-header @back="$router.back()">
      <template #content>
        <span class="page-title">🔧 消息过滤规则</span>
      </template>
      <template #extra>
        <el-space>
          <el-button @click="handleImport" :icon="Upload">
            导入配置
          </el-button>
          <el-button @click="handleExport" :icon="Download">
            导出配置
          </el-button>
          <el-button type="primary" @click="handleSave" :loading="saving">
            <el-icon><Select /></el-icon>
            保存规则
          </el-button>
        </el-space>
      </template>
    </el-page-header>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 左侧：规则配置 -->
      <el-col :span="16">
        <el-card shadow="never" class="rules-card">
          <template #header>
            <div class="card-header">
              <span>规则配置</span>
              <el-radio-group v-model="activeScope" size="small">
                <el-radio-button label="global">全局规则</el-radio-button>
                <el-radio-button label="channel">频道规则</el-radio-button>
              </el-radio-group>
            </div>
          </template>

          <!-- 频道选择（仅频道规则） -->
          <transition name="el-fade-in">
            <div v-if="activeScope === 'channel'" class="channel-selector">
              <el-alert type="info" :closable="false">
                <template #title>
                  选择要应用规则的频道
                </template>
              </el-alert>

              <el-select
                v-model="selectedChannels"
                multiple
                placeholder="选择频道"
                style="width: 100%; margin-top: 10px"
                filterable
              >
                <el-option
                  v-for="channel in availableChannels"
                  :key="channel.id"
                  :label="`${channel.server_name} / ${channel.channel_name}`"
                  :value="channel.id"
                >
                  <span style="float: left">{{ channel.channel_name }}</span>
                  <span style="float: right; color: #8492a6; font-size: 13px">
                    {{ channel.server_name }}
                  </span>
                </el-option>
              </el-select>
            </div>
          </transition>

          <!-- 关键词过滤 -->
          <el-divider content-position="left">
            <el-icon><Key /></el-icon>
            关键词过滤
          </el-divider>

          <div class="keyword-section">
            <!-- 黑名单 -->
            <el-form-item label="黑名单（包含以下词不转发）">
              <div class="tag-input-wrapper">
                <el-tag
                  v-for="tag in rules.keyword_blacklist"
                  :key="tag"
                  closable
                  @close="removeKeyword('blacklist', tag)"
                  type="danger"
                  size="large"
                  class="keyword-tag"
                >
                  {{ tag }}
                </el-tag>

                <el-input
                  v-model="keywordInput.blacklist"
                  placeholder="输入关键词后按回车添加"
                  class="keyword-input"
                  @keyup.enter="addKeyword('blacklist')"
                  @blur="addKeyword('blacklist')"
                  clearable
                >
                  <template #append>
                    <el-button @click="addKeyword('blacklist')" :icon="Plus">
                      添加
                    </el-button>
                  </template>
                </el-input>
              </div>

              <div class="quick-add">
                <span class="quick-add-label">快速添加：</span>
                <el-space wrap :size="5">
                  <el-tag
                    v-for="preset in keywordPresets.blacklist"
                    :key="preset"
                    @click="addPresetKeyword('blacklist', preset)"
                    style="cursor: pointer"
                    size="small"
                  >
                    <el-icon><Plus /></el-icon>
                    {{ preset }}
                  </el-tag>
                </el-space>
              </div>
            </el-form-item>

            <!-- 白名单 -->
            <el-form-item label="白名单（仅转发包含以下词）" style="margin-top: 20px">
              <div class="tag-input-wrapper">
                <el-tag
                  v-for="tag in rules.keyword_whitelist"
                  :key="tag"
                  closable
                  @close="removeKeyword('whitelist', tag)"
                  type="success"
                  size="large"
                  class="keyword-tag"
                >
                  {{ tag }}
                </el-tag>

                <el-input
                  v-model="keywordInput.whitelist"
                  placeholder="输入关键词后按回车添加"
                  class="keyword-input"
                  @keyup.enter="addKeyword('whitelist')"
                  @blur="addKeyword('whitelist')"
                  clearable
                >
                  <template #append>
                    <el-button @click="addKeyword('whitelist')" :icon="Plus">
                      添加
                    </el-button>
                  </template>
                </el-input>
              </div>

              <div class="quick-add">
                <span class="quick-add-label">快速添加：</span>
                <el-space wrap :size="5">
                  <el-tag
                    v-for="preset in keywordPresets.whitelist"
                    :key="preset"
                    @click="addPresetKeyword('whitelist', preset)"
                    style="cursor: pointer"
                    size="small"
                  >
                    <el-icon><Plus /></el-icon>
                    {{ preset }}
                  </el-tag>
                </el-space>
              </div>
            </el-form-item>

            <el-checkbox v-model="rules.keyword_enabled" style="margin-top: 10px">
              启用关键词过滤
            </el-checkbox>
          </div>

          <!-- 用户过滤 -->
          <el-divider content-position="left">
            <el-icon><User /></el-icon>
            用户过滤
          </el-divider>

          <div class="user-section">
            <!-- 黑名单用户 -->
            <el-form-item label="黑名单用户（不转发以下用户的消息）">
              <div class="user-list">
                <el-card
                  v-for="user in rules.user_blacklist"
                  :key="user.id"
                  shadow="hover"
                  class="user-card"
                >
                  <div class="user-info">
                    <el-avatar :src="user.avatar" :size="32">
                      {{ user.name.charAt(0) }}
                    </el-avatar>
                    <div class="user-details">
                      <div class="user-name">{{ user.name }}</div>
                      <div class="user-id">ID: {{ user.id }}</div>
                    </div>
                  </div>
                  <el-button
                    type="danger"
                    text
                    @click="removeUser('blacklist', user.id)"
                    :icon="Delete"
                  >
                    删除
                  </el-button>
                </el-card>

                <el-button
                  @click="showUserSelector('blacklist')"
                  :icon="Plus"
                  style="width: 100%"
                >
                  添加用户
                </el-button>
              </div>
            </el-form-item>

            <!-- 白名单用户 -->
            <el-form-item label="白名单用户（仅转发以下用户的消息）" style="margin-top: 20px">
              <div class="user-list">
                <el-card
                  v-for="user in rules.user_whitelist"
                  :key="user.id"
                  shadow="hover"
                  class="user-card"
                >
                  <div class="user-info">
                    <el-avatar :src="user.avatar" :size="32">
                      {{ user.name.charAt(0) }}
                    </el-avatar>
                    <div class="user-details">
                      <div class="user-name">{{ user.name }}</div>
                      <div class="user-id">ID: {{ user.id }}</div>
                    </div>
                  </div>
                  <el-button
                    type="danger"
                    text
                    @click="removeUser('whitelist', user.id)"
                    :icon="Delete"
                  >
                    删除
                  </el-button>
                </el-card>

                <el-button
                  @click="showUserSelector('whitelist')"
                  :icon="Plus"
                  style="width: 100%"
                >
                  添加用户
                </el-button>
              </div>
            </el-form-item>

            <el-checkbox v-model="rules.user_enabled" style="margin-top: 10px">
              启用用户过滤
            </el-checkbox>
          </div>

          <!-- 消息类型过滤 -->
          <el-divider content-position="left">
            <el-icon><DocumentCopy /></el-icon>
            消息类型过滤
          </el-divider>

          <div class="message-type-section">
            <el-checkbox-group v-model="rules.message_types">
              <el-checkbox label="text">
                <el-icon><ChatLineRound /></el-icon>
                文本消息
              </el-checkbox>
              <el-checkbox label="image">
                <el-icon><Picture /></el-icon>
                图片消息
              </el-checkbox>
              <el-checkbox label="link">
                <el-icon><Link /></el-icon>
                链接消息
              </el-checkbox>
              <el-checkbox label="file">
                <el-icon><Document /></el-icon>
                文件附件
              </el-checkbox>
              <el-checkbox label="video">
                <el-icon><VideoPlay /></el-icon>
                视频消息
              </el-checkbox>
              <el-checkbox label="audio">
                <el-icon><Microphone /></el-icon>
                音频消息
              </el-checkbox>
              <el-checkbox label="reaction">
                <el-icon><Medal /></el-icon>
                表情反应
              </el-checkbox>
              <el-checkbox label="mention">
                <el-icon><Bell /></el-icon>
                @提及消息
              </el-checkbox>
            </el-checkbox-group>

            <el-alert type="info" :closable="false" style="margin-top: 15px">
              <template #title>
                仅转发勾选的消息类型
              </template>
            </el-alert>
          </div>

          <!-- 高级选项 -->
          <el-divider content-position="left">
            <el-icon><Setting /></el-icon>
            高级选项
          </el-divider>

          <div class="advanced-section">
            <el-form label-width="150px">
              <el-form-item label="消息长度限制">
                <el-slider
                  v-model="rules.max_message_length"
                  :min="0"
                  :max="10000"
                  :step="100"
                  show-input
                  :marks="{ 0: '不限', 2000: '2000', 5000: '5000', 10000: '10000' }"
                />
                <div class="form-tip">
                  0表示不限制，超过长度的消息将被丢弃
                </div>
              </el-form-item>

              <el-form-item label="最小消息间隔">
                <el-input-number
                  v-model="rules.min_message_interval"
                  :min="0"
                  :max="60"
                  :step="1"
                />
                <span style="margin-left: 10px">秒</span>
                <div class="form-tip">
                  同一用户在间隔时间内的消息将被忽略（防刷屏）
                </div>
              </el-form-item>

              <el-form-item label="正则表达式">
                <el-input
                  v-model="rules.regex_pattern"
                  placeholder="例如：^【.*】.*（匹配标题格式）"
                  clearable
                />
                <div class="form-tip">
                  高级用户可使用正则表达式进行更精确的过滤
                </div>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：预览和统计 -->
      <el-col :span="8">
        <!-- 实时预览 -->
        <el-card shadow="never" class="preview-card">
          <template #header>
            <div class="card-header">
              <span>实时预览</span>
              <el-switch
                v-model="previewEnabled"
                active-text="开启"
                inactive-text="关闭"
              />
            </div>
          </template>

          <div v-if="previewEnabled" class="preview-content">
            <el-alert type="info" :closable="false">
              <template #title>
                显示最近50条消息的过滤结果
              </template>
            </el-alert>

            <el-scrollbar height="400px" style="margin-top: 15px">
              <div class="preview-messages">
                <div
                  v-for="(msg, index) in previewMessages"
                  :key="index"
                  class="preview-message"
                  :class="{
                    'message-allowed': msg.allowed,
                    'message-blocked': !msg.allowed
                  }"
                >
                  <div class="message-header">
                    <el-tag :type="msg.allowed ? 'success' : 'danger'" size="small">
                      {{ msg.allowed ? '✅ 允许' : '❌ 拦截' }}
                    </el-tag>
                    <span class="message-time">{{ msg.time }}</span>
                  </div>
                  <div class="message-content">
                    <b>{{ msg.sender }}:</b> {{ msg.content }}
                  </div>
                  <div v-if="!msg.allowed" class="message-reason">
                    <el-icon><WarningFilled /></el-icon>
                    拦截原因: {{ msg.reason }}
                  </div>
                </div>
              </div>
            </el-scrollbar>
          </div>

          <el-empty v-else description="预览已关闭" :image-size="100" />
        </el-card>

        <!-- 过滤统计 -->
        <el-card shadow="never" class="stats-card" style="margin-top: 20px">
          <template #header>
            📊 过滤统计
          </template>

          <el-descriptions :column="1" border>
            <el-descriptions-item label="今日拦截">
              <el-tag type="danger">{{ stats.todayBlocked }} 条</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="今日通过">
              <el-tag type="success">{{ stats.todayAllowed }} 条</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="拦截率">
              <el-progress
                :percentage="stats.blockRate"
                :color="getBlockRateColor(stats.blockRate)"
              />
            </el-descriptions-item>
            <el-descriptions-item label="命中最多规则">
              {{ stats.topRule || '暂无数据' }}
            </el-descriptions-item>
          </el-descriptions>

          <el-button
            @click="viewFullStats"
            type="primary"
            style="width: 100%; margin-top: 15px"
          >
            查看详细统计
          </el-button>
        </el-card>

        <!-- 快捷操作 -->
        <el-card shadow="never" class="actions-card" style="margin-top: 20px">
          <template #header>
            ⚡ 快捷操作
          </template>

          <el-space direction="vertical" fill style="width: 100%">
            <el-button @click="handleReset" :icon="RefreshRight">
              重置为默认
            </el-button>
            <el-button @click="handleTestRule" :icon="Tools">
              测试规则
            </el-button>
            <el-button @click="handleCopyFrom" :icon="DocumentCopy">
              从其他频道复制
            </el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>

    <!-- 用户选择器对话框 -->
    <UserSelectorDialog
      v-model="userSelectorVisible"
      :type="userSelectorType"
      @confirm="handleUserSelected"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload,
  Download,
  Select,
  Key,
  User,
  DocumentCopy,
  ChatLineRound,
  Picture,
  Link,
  Document,
  VideoPlay,
  Microphone,
  Medal,
  Bell,
  Setting,
  Plus,
  Delete,
  WarningFilled,
  RefreshRight,
  Tools
} from '@element-plus/icons-vue'
import api from '@/api'
import UserSelectorDialog from '@/components/UserSelectorDialog.vue'

// 状态
const activeScope = ref('global')
const selectedChannels = ref([])
const availableChannels = ref([])
const saving = ref(false)

// 规则
const rules = reactive({
  keyword_blacklist: [],
  keyword_whitelist: [],
  keyword_enabled: true,
  user_blacklist: [],
  user_whitelist: [],
  user_enabled: false,
  message_types: ['text', 'image', 'link', 'file'],
  max_message_length: 0,
  min_message_interval: 0,
  regex_pattern: ''
})

// 关键词输入
const keywordInput = reactive({
  blacklist: '',
  whitelist: ''
})

// 预设关键词
const keywordPresets = {
  blacklist: ['广告', '代练', '外挂', '刷屏', '骚扰'],
  whitelist: ['官方公告', '版本更新', '重要通知', '活动']
}

// 用户选择器
const userSelectorVisible = ref(false)
const userSelectorType = ref('blacklist')

// 预览
const previewEnabled = ref(true)
const previewMessages = ref([])

// 统计
const stats = reactive({
  todayBlocked: 0,
  todayAllowed: 0,
  blockRate: 0,
  topRule: ''
})

// 添加关键词
const addKeyword = (type) => {
  const input = keywordInput[type].trim()
  if (!input) return

  const list = type === 'blacklist' ? rules.keyword_blacklist : rules.keyword_whitelist

  if (list.includes(input)) {
    ElMessage.warning('关键词已存在')
    return
  }

  list.push(input)
  keywordInput[type] = ''
  
  ElMessage.success(`已添加到${type === 'blacklist' ? '黑' : '白'}名单`)
  updatePreview()
}

// 添加预设关键词
const addPresetKeyword = (type, keyword) => {
  const list = type === 'blacklist' ? rules.keyword_blacklist : rules.keyword_whitelist

  if (list.includes(keyword)) {
    ElMessage.warning('关键词已存在')
    return
  }

  list.push(keyword)
  updatePreview()
}

// 移除关键词
const removeKeyword = (type, keyword) => {
  const list = type === 'blacklist' ? rules.keyword_blacklist : rules.keyword_whitelist
  const index = list.indexOf(keyword)
  if (index > -1) {
    list.splice(index, 1)
    updatePreview()
  }
}

// 显示用户选择器
const showUserSelector = (type) => {
  userSelectorType.value = type
  userSelectorVisible.value = true
}

// 用户选择确认
const handleUserSelected = (users) => {
  const list = userSelectorType.value === 'blacklist'
    ? rules.user_blacklist
    : rules.user_whitelist

  users.forEach(user => {
    if (!list.find(u => u.id === user.id)) {
      list.push(user)
    }
  })

  ElMessage.success(`已添加 ${users.length} 个用户`)
  updatePreview()
}

// 移除用户
const removeUser = (type, userId) => {
  const list = type === 'blacklist' ? rules.user_blacklist : rules.user_whitelist
  const index = list.findIndex(u => u.id === userId)
  if (index > -1) {
    list.splice(index, 1)
    updatePreview()
  }
}

// 更新预览
const updatePreview = async () => {
  if (!previewEnabled.value) return

  try {
    const result = await api.previewFilterRules(rules)
    previewMessages.value = result.messages
  } catch (error) {
    console.error('更新预览失败:', error)
  }
}

// 监听规则变化
watch(
  () => [rules.keyword_blacklist, rules.keyword_whitelist, rules.message_types],
  () => {
    updatePreview()
  },
  { deep: true }
)

// 获取拦截率颜色
const getBlockRateColor = (rate) => {
  if (rate < 20) return '#67C23A'
  if (rate < 50) return '#E6A23C'
  return '#F56C6C'
}

// 保存规则
const handleSave = async () => {
  saving.value = true

  try {
    await api.saveFilterRules({
      scope: activeScope.value,
      channels: selectedChannels.value,
      rules: rules
    })

    ElMessage.success('过滤规则已保存')
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  } finally {
    saving.value = false
  }
}

// 导入配置
const handleImport = () => {
  // 实现导入逻辑
}

// 导出配置
const handleExport = () => {
  // 实现导出逻辑
}

// 重置为默认
const handleReset = async () => {
  const confirmed = await ElMessageBox.confirm(
    '确定要重置为默认配置吗？所有自定义规则将被清除。',
    '确认重置',
    {
      type: 'warning'
    }
  ).catch(() => false)

  if (confirmed) {
    // 重置规则
    Object.assign(rules, {
      keyword_blacklist: [],
      keyword_whitelist: [],
      keyword_enabled: true,
      user_blacklist: [],
      user_whitelist: [],
      user_enabled: false,
      message_types: ['text', 'image', 'link', 'file'],
      max_message_length: 0,
      min_message_interval: 0,
      regex_pattern: ''
    })

    ElMessage.success('已重置为默认配置')
  }
}

// 测试规则
const handleTestRule = () => {
  // 实现测试逻辑
}

// 从其他频道复制
const handleCopyFrom = () => {
  // 实现复制逻辑
}

// 查看详细统计
const viewFullStats = () => {
  // 跳转到统计页面
}

// 加载数据
onMounted(async () => {
  try {
    // 加载可用频道
    availableChannels.value = await api.getAvailableChannels()

    // 加载现有规则
    const existingRules = await api.getFilterRules(activeScope.value)
    if (existingRules) {
      Object.assign(rules, existingRules)
    }

    // 加载统计数据
    const statsData = await api.getFilterStats()
    Object.assign(stats, statsData)

    // 更新预览
    updatePreview()
  } catch (error) {
    console.error('加载数据失败:', error)
  }
})
</script>

<style scoped lang="scss">
.filter-view {
  padding: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tag-input-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 10px;

  .keyword-tag {
    margin: 0;
  }

  .keyword-input {
    flex: 1;
    min-width: 300px;
  }
}

.quick-add {
  margin-top: 10px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;

  .quick-add-label {
    color: #606266;
    font-size: 14px;
  }
}

.user-list {
  display: grid;
  gap: 10px;

  .user-card {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .user-info {
      display: flex;
      align-items: center;
      gap: 12px;

      .user-details {
        .user-name {
          font-weight: bold;
          margin-bottom: 2px;
        }

        .user-id {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }
}

.message-type-section {
  :deep(.el-checkbox) {
    display: flex;
    align-items: center;
    margin: 10px 0;

    .el-checkbox__label {
      display: flex;
      align-items: center;
      gap: 5px;
    }
  }
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.preview-content {
  .preview-messages {
    .preview-message {
      padding: 12px;
      border-radius: 4px;
      margin-bottom: 10px;
      border-left: 3px solid;

      &.message-allowed {
        background: #F0F9FF;
        border-color: #67C23A;
      }

      &.message-blocked {
        background: #FEF0F0;
        border-color: #F56C6C;
      }

      .message-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 5px;

        .message-time {
          font-size: 12px;
          color: #909399;
        }
      }

      .message-content {
        font-size: 14px;
        margin-bottom: 5px;
      }

      .message-reason {
        display: flex;
        align-items: center;
        gap: 5px;
        font-size: 12px;
        color: #F56C6C;
      }
    }
  }
}
</style>
```

---

由于篇幅限制，我将创建一个总的索引文档来总结所有优化手册：

