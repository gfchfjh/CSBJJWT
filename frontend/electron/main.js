/**
 * Electron主进程
 */
const { app, BrowserWindow, ipcMain, Tray, Menu, dialog } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const AutoLaunch = require('auto-launch')

let mainWindow = null
let backendProcess = null
let tray = null

// 配置开机自启
const autoLauncher = new AutoLaunch({
  name: 'KOOK消息转发系统',
  path: app.getPath('exe'),
})

// 检查并设置开机自启
async function setupAutoLaunch() {
  const isEnabled = await autoLauncher.isEnabled()
  
  // 可以通过配置文件控制
  const shouldEnable = app.getLoginItemSettings().openAtLogin
  
  if (shouldEnable && !isEnabled) {
    await autoLauncher.enable()
  } else if (!shouldEnable && isEnabled) {
    await autoLauncher.disable()
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
  const iconPath = path.join(__dirname, '../public/icon.png')
  tray = new Tray(iconPath)
  
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
            click: (menuItem) => {
              app.setLoginItemSettings({
                openAtLogin: menuItem.checked
              })
              // 更新AutoLauncher
              if (menuItem.checked) {
                autoLauncher.enable().catch(console.error)
              } else {
                autoLauncher.disable().catch(console.error)
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
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true,
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

// 显示通知
ipcMain.on('show-notification', (event, { title, body }) => {
  const { Notification } = require('electron')
  
  if (Notification.isSupported()) {
    new Notification({
      title,
      body,
      icon: path.join(__dirname, '../public/icon.png')
    }).show()
  }
})

// 获取应用信息
ipcMain.handle('get-app-info', () => {
  return {
    version: app.getVersion(),
    name: app.getName(),
    path: app.getPath('userData')
  }
})
