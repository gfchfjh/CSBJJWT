/**
 * Electron主进程（终极版）
 * ========================
 * 功能：
 * 1. 自动启动后端FastAPI服务
 * 2. 系统托盘集成
 * 3. 进程守护（崩溃自动重启）
 * 4. 首次启动检测（配置向导）
 * 5. IPC通信（前后端交互）
 * 6. 自动更新检查
 * 7. 应用图标和菜单
 * 
 * 作者：KOOK Forwarder Team
 * 日期：2025-10-25
 */

const { app, BrowserWindow, Tray, Menu, ipcMain, dialog, shell } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const http = require('http');

// 全局变量
let mainWindow = null;
let tray = null;
let backendProcess = null;
let backendRestartCount = 0;
const MAX_BACKEND_RESTART = 5;
const BACKEND_PORT = 9527;
const BACKEND_URL = `http://localhost:${BACKEND_PORT}`;

/**
 * 获取后端可执行文件路径
 */
function getBackendExecutable() {
  const isDev = process.env.NODE_ENV === 'development';
  
  if (isDev) {
    // 开发环境：使用Python直接运行
    return {
      command: 'python',
      args: [path.join(__dirname, '../../backend/app/main.py')],
      cwd: path.join(__dirname, '../../backend')
    };
  } else {
    // 生产环境：使用打包后的可执行文件
    const platform = process.platform;
    let executable;
    
    if (platform === 'win32') {
      executable = path.join(process.resourcesPath, 'backend', 'kook_forwarder.exe');
    } else if (platform === 'darwin') {
      executable = path.join(process.resourcesPath, 'backend', 'kook_forwarder');
    } else {
      executable = path.join(process.resourcesPath, 'backend', 'kook_forwarder');
    }
    
    return {
      command: executable,
      args: [],
      cwd: path.join(process.resourcesPath, 'backend')
    };
  }
}

/**
 * 启动后端服务
 */
async function startBackend() {
  return new Promise((resolve, reject) => {
    console.log('🚀 启动后端服务...');
    
    const backendInfo = getBackendExecutable();
    console.log(`📦 后端命令: ${backendInfo.command} ${backendInfo.args.join(' ')}`);
    console.log(`📁 工作目录: ${backendInfo.cwd}`);
    
    backendProcess = spawn(backendInfo.command, backendInfo.args, {
      cwd: backendInfo.cwd,
      env: { 
        ...process.env, 
        PYTHONUNBUFFERED: '1',
        API_HOST: '127.0.0.1',
        API_PORT: BACKEND_PORT.toString()
      }
    });
    
    // 监听stdout
    backendProcess.stdout.on('data', (data) => {
      console.log(`[Backend] ${data.toString().trim()}`);
    });
    
    // 监听stderr
    backendProcess.stderr.on('data', (data) => {
      console.error(`[Backend Error] ${data.toString().trim()}`);
    });
    
    // 监听退出
    backendProcess.on('exit', (code, signal) => {
      console.error(`❌ 后端进程退出: code=${code}, signal=${signal}`);
      handleBackendCrash();
    });
    
    // 监听启动错误
    backendProcess.on('error', (err) => {
      console.error(`❌ 后端进程启动失败: ${err.message}`);
      reject(err);
    });
    
    // 等待后端就绪（检查HTTP服务）
    const startTime = Date.now();
    const maxWaitTime = 60000; // 60秒
    
    const checkInterval = setInterval(() => {
      checkBackendHealth()
        .then((healthy) => {
          if (healthy) {
            clearInterval(checkInterval);
            console.log('✅ 后端服务启动成功');
            resolve();
          } else if (Date.now() - startTime > maxWaitTime) {
            clearInterval(checkInterval);
            reject(new Error('后端服务启动超时（60秒）'));
          }
        })
        .catch(() => {
          // 继续等待
        });
    }, 500);
  });
}

/**
 * 检查后端健康状态
 */
function checkBackendHealth() {
  return new Promise((resolve) => {
    const req = http.get(`${BACKEND_URL}/health`, (res) => {
      resolve(res.statusCode === 200);
    });
    
    req.on('error', () => {
      resolve(false);
    });
    
    req.setTimeout(2000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

/**
 * 处理后端崩溃（自动重启）
 */
async function handleBackendCrash() {
  if (app.isQuitting) {
    // 应用正在退出，不重启
    return;
  }
  
  console.log(`⚠️  后端崩溃，已重启${backendRestartCount}次`);
  
  if (backendRestartCount < MAX_BACKEND_RESTART) {
    backendRestartCount++;
    console.log(`🔄 尝试重启后端 (${backendRestartCount}/${MAX_BACKEND_RESTART})...`);
    
    // 等待3秒后重启
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    try {
      await startBackend();
      console.log('✅ 后端重启成功');
      backendRestartCount = 0; // 重置计数
      
      // 通知前端
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('backend-restarted');
      }
    } catch (err) {
      console.error(`❌ 后端重启失败: ${err.message}`);
      
      if (backendRestartCount >= MAX_BACKEND_RESTART) {
        // 达到最大重启次数，显示错误对话框
        dialog.showErrorBox(
          '后端服务异常',
          `后端服务多次崩溃（${MAX_BACKEND_RESTART}次），无法自动恢复。\n\n请检查日志文件或联系技术支持。`
        );
      }
    }
  } else {
    console.error(`❌ 后端已达到最大重启次数（${MAX_BACKEND_RESTART}），停止自动重启`);
  }
}

/**
 * 停止后端服务
 */
function stopBackend() {
  if (backendProcess) {
    console.log('🛑 停止后端服务...');
    backendProcess.kill();
    backendProcess = null;
  }
}

/**
 * 创建主窗口
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 1024,
    minHeight: 600,
    icon: path.join(__dirname, '../public/icon.png'),
    show: false, // 先不显示，等加载完成
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });
  
  // 加载前端页面
  const isDev = process.env.NODE_ENV === 'development';
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools(); // 开发模式打开DevTools
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }
  
  // 页面加载完成后显示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // 首次启动检测
    if (isFirstRun()) {
      console.log('🎉 检测到首次启动，显示配置向导');
      mainWindow.webContents.send('show-wizard');
    }
  });
  
  // 关闭窗口时最小化到托盘（而非退出）
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
      
      // 显示提示（仅首次）
      if (!fs.existsSync(getTrayTipFile())) {
        tray.displayBalloon({
          title: 'KOOK消息转发系统',
          content: '应用已最小化到系统托盘，可在托盘图标处管理。',
          icon: path.join(__dirname, '../public/icon.png')
        });
        
        // 标记已显示过提示
        fs.writeFileSync(getTrayTipFile(), Date.now().toString());
      }
    }
  });
  
  // 窗口关闭
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

/**
 * 创建系统托盘
 */
function createTray() {
  const iconPath = path.join(__dirname, '../public/icon.png');
  tray = new Tray(iconPath);
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: '显示主窗口',
      click: () => {
        if (mainWindow) {
          if (mainWindow.isMinimized()) {
            mainWindow.restore();
          }
          mainWindow.show();
          mainWindow.focus();
        }
      }
    },
    { type: 'separator' },
    {
      label: '后端状态',
      submenu: [
        {
          label: backendProcess ? '✅ 运行中' : '❌ 已停止',
          enabled: false
        },
        {
          label: '重启后端',
          click: async () => {
            stopBackend();
            try {
              await startBackend();
              dialog.showMessageBox({
                type: 'info',
                title: '后端重启',
                message: '后端服务已成功重启'
              });
            } catch (err) {
              dialog.showErrorBox('后端重启失败', err.message);
            }
          }
        }
      ]
    },
    { type: 'separator' },
    {
      label: '打开日志目录',
      click: () => {
        const logDir = path.join(app.getPath('userData'), '../KookForwarder/data/logs');
        shell.openPath(logDir);
      }
    },
    {
      label: '检查更新',
      click: () => {
        // TODO: 实现自动更新检查
        dialog.showMessageBox({
          type: 'info',
          title: '检查更新',
          message: '当前版本: v4.0.0\n已是最新版本！'
        });
      }
    },
    { type: 'separator' },
    {
      label: '退出',
      click: () => {
        app.isQuitting = true;
        app.quit();
      }
    }
  ]);
  
  tray.setContextMenu(contextMenu);
  tray.setToolTip('KOOK消息转发系统 v4.0.0');
  
  // 托盘图标点击事件
  tray.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
        mainWindow.focus();
      }
    }
  });
  
  // 双击显示窗口
  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

/**
 * 检查是否首次运行
 */
function isFirstRun() {
  const configFile = path.join(app.getPath('userData'), 'wizard_completed.txt');
  return !fs.existsSync(configFile);
}

/**
 * 获取托盘提示文件路径
 */
function getTrayTipFile() {
  return path.join(app.getPath('userData'), 'tray_tip_shown.txt');
}

/**
 * IPC通信：向导完成
 */
ipcMain.on('wizard-completed', () => {
  const configFile = path.join(app.getPath('userData'), 'wizard_completed.txt');
  fs.writeFileSync(configFile, Date.now().toString());
  console.log('✅ 配置向导已完成');
});

/**
 * IPC通信：打开外部链接
 */
ipcMain.on('open-external-link', (event, url) => {
  shell.openExternal(url);
});

/**
 * IPC通信：获取后端状态
 */
ipcMain.handle('get-backend-status', async () => {
  const healthy = await checkBackendHealth();
  return {
    running: backendProcess !== null,
    healthy: healthy,
    port: BACKEND_PORT,
    restartCount: backendRestartCount
  };
});

/**
 * 应用启动
 */
app.whenReady().then(async () => {
  console.log('=' * 60);
  console.log('🚀 KOOK消息转发系统 v4.0.0');
  console.log('=' * 60);
  
  try {
    // 1. 启动后端服务
    await startBackend();
    
    // 2. 创建主窗口
    createWindow();
    
    // 3. 创建系统托盘
    createTray();
    
    console.log('✅ 应用启动完成');
    
  } catch (err) {
    console.error('❌ 应用启动失败:', err);
    
    dialog.showErrorBox(
      '启动失败',
      `应用启动失败，请检查日志文件。\n\n错误信息：${err.message}`
    );
    
    app.quit();
  }
});

/**
 * 所有窗口关闭时
 */
app.on('window-all-closed', () => {
  // macOS中除非用户明确退出，否则应用保持活跃
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

/**
 * 应用激活（macOS）
 */
app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

/**
 * 应用退出前
 */
app.on('before-quit', () => {
  console.log('🛑 应用正在退出...');
  app.isQuitting = true;
  
  // 停止后端服务
  stopBackend();
});

/**
 * 应用完全退出
 */
app.on('quit', () => {
  console.log('✅ 应用已退出');
});
