/**
 * Electron主进程
 */
const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')
const { spawn } = require('child_process')

let mainWindow = null
let backendProcess = null

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
      enableRemoteModule: true
    },
    title: 'KOOK消息转发系统',
    icon: path.join(__dirname, '../public/icon.png')
  })

  // 开发环境加载开发服务器
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    // 生产环境加载打包后的文件
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// 应用启动
app.whenReady().then(() => {
  // 启动后端服务
  startBackend()
  
  // 等待后端启动
  setTimeout(() => {
    createWindow()
  }, 3000)

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

// 所有窗口关闭
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// 应用退出
app.on('quit', () => {
  // 停止后端服务
  if (backendProcess) {
    backendProcess.kill()
  }
})

// IPC通信
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
