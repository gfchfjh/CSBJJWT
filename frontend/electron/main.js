/**
 * Electron主进程
 */
const { app, BrowserWindow, ipcMain, Tray, Menu, dialog, shell } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const AutoLaunch = require('auto-launch')
const fs = require('fs')

let mainWindow = null
let backendProcess = null
let tray = null

// 配置开机自启（v1.12.0+ 优化：增强Linux兼容性）
const autoLauncher = new AutoLaunch({
  name: 'KOOK消息转发系统',
  path: app.getPath('exe'),
  // Linux特定配置
  ...(process.platform === 'linux' && {
    isHidden: false,  // Linux下不隐藏窗口
  })
})

// 检查并设置开机自启（v1.12.0+ 优化：增强错误处理）
async function setupAutoLaunch() {
  try {
    const isEnabled = await autoLauncher.isEnabled()
    
    // 可以通过配置文件控制
    const shouldEnable = app.getLoginItemSettings().openAtLogin
    
    if (shouldEnable && !isEnabled) {
      await autoLauncher.enable()
      console.log('✅ 开机自启已启用')
    } else if (!shouldEnable && isEnabled) {
      await autoLauncher.disable()
      console.log('✅ 开机自启已禁用')
    }
  } catch (error) {
    console.error('⚠️  设置开机自启失败:', error.message)
    
    // Linux平台特殊处理：尝试手动创建.desktop文件
    if (process.platform === 'linux') {
      try {
        await setupLinuxAutoStart()
      } catch (linuxError) {
        console.error('❌ Linux开机自启设置失败:', linuxError.message)
      }
    }
  }
}

// Linux平台特殊处理：手动创建.desktop文件
async function setupLinuxAutoStart() {
  if (process.platform !== 'linux') return
  
  const fs = require('fs')
  const os = require('os')
  const path = require('path')
  
  // 创建autostart目录
  const autostartDir = path.join(os.homedir(), '.config', 'autostart')
  if (!fs.existsSync(autostartDir)) {
    fs.mkdirSync(autostartDir, { recursive: true })
  }
  
  // .desktop文件路径
  const desktopFilePath = path.join(autostartDir, 'kook-forwarder.desktop')
  
  // 检查是否应该启用
  const shouldEnable = app.getLoginItemSettings().openAtLogin
  
  if (shouldEnable) {
    // 创建.desktop文件
    const desktopContent = `[Desktop Entry]
Type=Application
Name=KOOK消息转发系统
Comment=开机自动启动KOOK消息转发系统
Exec=${app.getPath('exe')}
Icon=kook-forwarder
Terminal=false
Categories=Network;
X-GNOME-Autostart-enabled=true
`
    
    fs.writeFileSync(desktopFilePath, desktopContent, 'utf8')
    console.log('✅ Linux开机自启已启用（.desktop文件）')
  } else {
    // 删除.desktop文件
    if (fs.existsSync(desktopFilePath)) {
      fs.unlinkSync(desktopFilePath)
      console.log('✅ Linux开机自启已禁用（删除.desktop文件）')
    }
  }
}

// 启动后端服务
function startBackend() {
  console.log('正在启动后端服务...')
  
  // 这里需要根据实际打包后的后端路径调整
  const backendPath = path.join(__dirname, '../../backend/app/main.py')
  
  backendProcess = spawn('python', [backendPath], {
    cwd: path.join(__dirname, '../../backend')
  })
  
  backendProcess.stdout.on('data', (data) => {
    console.log(`后端: ${data}`)
  })
  
  backendProcess.stderr.on('data', (data) => {
    console.error(`后端错误: ${data}`)
  })
  
  backendProcess.on('close', (code) => {
    console.log(`后端进程退出，代码: ${code}`)
  })
}

// 创建系统托盘
function createTray() {
  // 修复：根据环境选择正确的图标路径
  const iconPath = app.isPackaged
    ? path.join(process.resourcesPath, 'icon.png')  // 生产环境
    : path.join(__dirname, '../public/icon.png')     // 开发环境
  
  // 检查图标文件是否存在
  if (!fs.existsSync(iconPath)) {
    console.warn('⚠️ 托盘图标文件不存在:', iconPath)
    console.log('📍 尝试备用路径...')
    
    // 尝试多个可能的路径
    const fallbackPaths = [
      path.join(__dirname, '../public/icon.png'),
      path.join(__dirname, '../../build/icon.png'),
      path.join(app.getAppPath(), 'public/icon.png'),
      path.join(app.getAppPath(), '../icon.png')
    ]
    
    let found = false
    for (const fallbackPath of fallbackPaths) {
      if (fs.existsSync(fallbackPath)) {
        console.log('✅ 找到图标:', fallbackPath)
        tray = new Tray(fallbackPath)
        found = true
        break
      }
    }
    
    if (!found) {
      console.error('❌ 所有图标路径都失败，跳过创建托盘')
      return null  // 返回 null 表示托盘创建失败，但不影响主应用
    }
  } else {
    tray = new Tray(iconPath)
  }
  
  const updateTrayMenu = (stats = null) => {
    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'KOOK消息转发系统',
        enabled: false,
        icon: iconPath
      },
      { type: 'separator' },
      {
        label: stats ? `📊 今日转发: ${stats.total || 0} 条` : '📊 统计信息',
        enabled: !!stats,
        click: () => {
          if (mainWindow) {
            mainWindow.show()
            mainWindow.focus()
            mainWindow.webContents.send('navigate-to', '/')
          }
        }
      },
      {
        label: stats ? `✅ 成功率: ${stats.success_rate || 0}%` : '⏸️ 服务未启动',
        enabled: !!stats
      },
      { type: 'separator' },
      {
        label: '📱 显示主窗口',
        click: () => {
          if (mainWindow) {
            mainWindow.show()
            mainWindow.focus()
          } else {
            createWindow()
          }
        }
      },
      {
        label: '📋 查看日志',
        click: () => {
          if (mainWindow) {
            mainWindow.show()
            mainWindow.focus()
            mainWindow.webContents.send('navigate-to', '/logs')
          }
        }
      },
      { type: 'separator' },
      {
        label: '⚙️ 设置',
        submenu: [
          {
            label: '开机自启',
            type: 'checkbox',
            checked: app.getLoginItemSettings().openAtLogin,
            click: async (menuItem) => {
              app.setLoginItemSettings({
                openAtLogin: menuItem.checked
              })
              
              // v1.12.0+ 优化：更新AutoLauncher，增强错误处理
              try {
                if (menuItem.checked) {
                  await autoLauncher.enable()
                  console.log('✅ 开机自启已启用')
                } else {
                  await autoLauncher.disable()
                  console.log('✅ 开机自启已禁用')
                }
              } catch (error) {
                console.error('⚠️  AutoLauncher操作失败:', error.message)
                
                // Linux平台特殊处理
                if (process.platform === 'linux') {
                  try {
                    await setupLinuxAutoStart()
                  } catch (linuxError) {
                    console.error('❌ Linux开机自启设置失败:', linuxError.message)
                    // 通知用户
                    if (mainWindow && !mainWindow.isDestroyed()) {
                      mainWindow.webContents.send('show-error', {
                        title: '开机自启设置失败',
                        message: '请检查系统权限或手动配置开机自启'
                      })
                    }
                  }
                }
              }
            }
          },
          {
            label: '启动时最小化',
            type: 'checkbox',
            checked: app.getLoginItemSettings().openAsHidden,
            click: (menuItem) => {
              app.setLoginItemSettings({
                openAsHidden: menuItem.checked
              })
            }
          }
        ]
      },
      { type: 'separator' },
      {
        label: '🚪 退出程序',
        click: () => {
          app.isQuiting = true
          app.quit()
        }
      }
    ])
    
    tray.setContextMenu(contextMenu)
  }
  
  // 初始化托盘菜单
  updateTrayMenu()
  
  tray.setToolTip('KOOK消息转发系统 - 运行中')
  
  // 双击托盘图标显示窗口
  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show()
      mainWindow.focus()
    } else {
      createWindow()
    }
  })
  
  // 单击显示菜单（Windows/Linux）
  tray.on('click', () => {
    if (process.platform !== 'darwin') {
      tray.popUpContextMenu()
    }
  })
  
  // 定期更新统计信息（每10秒）
  setInterval(async () => {
    try {
      const response = await fetch('http://127.0.0.1:9527/api/logs/stats')
      if (response.ok) {
        const stats = await response.json()
        updateTrayMenu(stats)
        
        // 更新tooltip
        tray.setToolTip(
          `KOOK消息转发系统\n` +
          `今日转发: ${stats.total || 0} 条\n` +
          `成功率: ${stats.success_rate || 0}%`
        )
      }
    } catch (error) {
      // 后端未就绪或出错，保持默认菜单
    }
  }, 10000)
  
  // 返回更新函数，供外部调用
  return { updateMenu: updateTrayMenu }
}

// 创建主窗口
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 1024,
    minHeight: 768,
    webPreferences: {
      nodeIntegration: false,  // 改为false，提高安全性
      contextIsolation: true,   // 改为true，使用contextBridge
      preload: path.join(__dirname, 'preload.js'),  // 使用preload脚本
      webSecurity: false  // 允许加载本地资源
    },
    title: 'KOOK消息转发系统',
    icon: path.join(__dirname, '../public/icon.png'),
    show: false  // 初始隐藏，等待加载完成
  })

  // 开发环境加载开发服务器
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    // 生产环境加载打包后的文件
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  // 窗口加载完成后显示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
  })

  // 关闭窗口时最小化到托盘
  mainWindow.on('close', (event) => {
    if (!app.isQuiting) {
      event.preventDefault()
      mainWindow.hide()
      
      // 首次最小化时提示
      if (!app.hasShownTrayTip) {
        const { Notification } = require('electron')
        
        if (Notification.isSupported()) {
          new Notification({
            title: 'KOOK消息转发系统',
            body: '程序已最小化到系统托盘，双击托盘图标可恢复窗口',
            icon: path.join(__dirname, '../public/icon.png')
          }).show()
        }
        
        app.hasShownTrayTip = true
      }
    }
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// 应用启动
app.whenReady().then(async () => {
  // 设置开机自启
  await setupAutoLaunch()
  
  // 创建系统托盘
  createTray()
  
  // 启动后端服务
  startBackend()
  
  // 等待后端启动（检测后端是否ready）
  let retries = 0
  const maxRetries = 30
  
  const checkBackend = setInterval(async () => {
    try {
      const response = await fetch('http://127.0.0.1:9527/health')
      if (response.ok) {
        clearInterval(checkBackend)
        createWindow()
      }
    } catch (error) {
      retries++
      if (retries >= maxRetries) {
        clearInterval(checkBackend)
        dialog.showErrorBox('启动失败', '后端服务启动超时，请检查Python环境')
        app.quit()
      }
    }
  }, 1000)

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

// 所有窗口关闭
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    // 不退出，最小化到托盘
    // app.quit()
  }
})

// 应用退出前
app.on('before-quit', () => {
  app.isQuiting = true
})

// 应用退出
app.on('quit', () => {
  // 停止后端服务
  if (backendProcess) {
    backendProcess.kill('SIGTERM')
    
    // 强制结束（5秒后）
    setTimeout(() => {
      if (backendProcess) {
        backendProcess.kill('SIGKILL')
      }
    }, 5000)
  }
})

// ========== IPC通信 ==========

// 窗口控制
ipcMain.on('minimize-window', () => {
  if (mainWindow) {
    mainWindow.minimize()
  }
})

ipcMain.on('maximize-window', () => {
  if (mainWindow) {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize()
    } else {
      mainWindow.maximize()
    }
  }
})

ipcMain.on('close-window', () => {
  if (mainWindow) {
    mainWindow.close()
  }
})

// 开机自启设置
ipcMain.handle('get-auto-launch', async () => {
  return app.getLoginItemSettings().openAtLogin
})

ipcMain.handle('set-auto-launch', async (event, enabled) => {
  app.setLoginItemSettings({
    openAtLogin: enabled
  })
  return true
})

// 打开文件夹
ipcMain.handle('open-folder', async (event, folderPath) => {
  const { shell } = require('electron')
  shell.openPath(folderPath)
})

// 选择文件夹
ipcMain.handle('select-folder', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  })
  
  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0]
  }
  return null
})

// 显示通知（增强版）
ipcMain.on('show-notification', (event, options) => {
  const { Notification } = require('electron')
  
  if (Notification.isSupported()) {
    const { title, body, type = 'info', urgency = 'normal', silent = false } = options
    
    // 根据类型设置不同的图标和紧急程度
    const notification = new Notification({
      title,
      body,
      icon: path.join(__dirname, '../public/icon.png'),
      urgency,  // 'normal', 'critical', 'low'
      silent,
      timeoutType: type === 'error' ? 'never' : 'default'  // 错误通知不自动消失
    })
    
    // 点击通知时显示主窗口
    notification.on('click', () => {
      if (mainWindow) {
        mainWindow.show()
        mainWindow.focus()
      } else {
        createWindow()
      }
    })
    
    notification.show()
    
    // 记录通知日志
    console.log(`[通知] ${type.toUpperCase()}: ${title} - ${body}`)
  }
})

// 显示系统通知（后端可调用）
function showSystemNotification(title, body, type = 'info') {
  const { Notification } = require('electron')
  
  if (Notification.isSupported()) {
    const urgency = type === 'error' ? 'critical' : 'normal'
    
    const notification = new Notification({
      title: `🤖 ${title}`,
      body,
      icon: path.join(__dirname, '../public/icon.png'),
      urgency
    })
    
    notification.on('click', () => {
      if (mainWindow) {
        mainWindow.show()
        mainWindow.focus()
      }
    })
    
    notification.show()
  }
}

// IPC监听后端通知请求
ipcMain.on('backend-notification', (event, { title, body, type }) => {
  showSystemNotification(title, body, type)
})

// 获取应用信息
ipcMain.handle('get-app-info', () => {
  return {
    version: app.getVersion(),
    name: app.getName(),
    path: app.getPath('userData')
  }
})

// 打开文件夹/文件
ipcMain.handle('open-path', async (event, filePath) => {
  try {
    // 确保路径存在
    if (fs.existsSync(filePath)) {
      // 使用shell打开文件夹
      await shell.openPath(filePath)
      return { success: true }
    } else {
      // 如果路径不存在，尝试创建目录
      const isDirectory = !path.extname(filePath)
      if (isDirectory) {
        fs.mkdirSync(filePath, { recursive: true })
        await shell.openPath(filePath)
        return { success: true }
      } else {
        return { success: false, error: '文件不存在' }
      }
    }
  } catch (error) {
    console.error('打开路径失败:', error)
    return { success: false, error: error.message }
  }
})

// 重启应用
ipcMain.handle('relaunch-app', () => {
  app.relaunch()
  app.exit(0)
})

// 选择文件对话框
ipcMain.handle('show-open-dialog', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, options)
  return result
})

// 选择保存位置对话框
ipcMain.handle('show-save-dialog', async (event, options) => {
  const result = await dialog.showSaveDialog(mainWindow, options)
  return result
})

// 显示消息对话框
ipcMain.handle('show-message-box', async (event, options) => {
  const result = await dialog.showMessageBox(mainWindow, options)
  return result
})
