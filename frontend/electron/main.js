/**
 * Electron 主进程
 * KOOK消息转发系统
 * 版本从根目录VERSION文件读取
 */

const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const AutoLaunch = require('auto-launch');
const fs = require('fs');

// 读取统一版本号
const VERSION = (() => {
  try {
    const versionFile = path.join(__dirname, '../../VERSION');
    return fs.readFileSync(versionFile, 'utf-8').trim();
  } catch (error) {
    console.error('Failed to read VERSION file:', error);
    return '7.0.0';  // 默认版本
  }
})();
const TrayManager = require('./tray-manager'); // ✅ 新增：导入托盘管理器

// 全局变量
let mainWindow = null;
let trayManager = null; // ✅ 新增：托盘管理器实例
let backendProcess = null;
let redisProcess = null; // ✅ P0-1优化：Redis进程
let isQuitting = false;

// 后端服务配置
const BACKEND_HOST = '127.0.0.1';
const BACKEND_PORT = 9527;
const BACKEND_URL = `http://${BACKEND_HOST}:${BACKEND_PORT}`;

// 应用路径
const isDev = !app.isPackaged;
const appPath = isDev ? __dirname : process.resourcesPath;

// 自动启动配置
const autoLauncher = new AutoLaunch({
  name: 'KOOK消息转发系统',
  path: app.getPath('exe'),
});

// 确保单实例运行
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    // 有人试图运行第二个实例，应该聚焦到我们的窗口
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

/**
 * 创建主窗口
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 1024,
    minHeight: 768,
    icon: path.join(__dirname, '../build/icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: true,
    },
    backgroundColor: '#ffffff',
    show: false, // 等待页面加载完成后再显示
  });

  // 加载前端页面
  if (isDev) {
    // 开发环境：加载 Vite 开发服务器
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    // 生产环境：加载打包后的文件
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  // 页面加载完成后显示窗口
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // 处理窗口关闭
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
      
      // 如果是 macOS，完全隐藏
      if (process.platform === 'darwin') {
        app.dock.hide();
      }
      
      return false;
    }
  });

  // 窗口关闭时清理
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // 阻止打开外部链接
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

// ✅ P1-1优化: 已删除旧版createTray函数，统一使用TrayManager

/**
 * ✅ P0-1优化：启动嵌入式Redis
 */
async function startRedis() {
  return new Promise((resolve, reject) => {
    // 开发环境跳过（使用系统Redis）
    if (isDev) {
      console.log('[Redis] 开发环境，跳过嵌入式Redis启动');
      resolve();
      return;
    }

    try {
      let redisExecutable;
      let redisConfig;

      if (process.platform === 'win32') {
        redisExecutable = path.join(appPath, 'redis', 'redis-server.exe');
        redisConfig = path.join(appPath, 'redis', 'redis.conf');
      } else {
        redisExecutable = path.join(appPath, 'redis', 'redis-server');
        redisConfig = path.join(appPath, 'redis', 'redis.conf');
      }

      // 检查Redis是否存在
      if (!fs.existsSync(redisExecutable)) {
        console.warn(`[Redis] 未找到嵌入式Redis: ${redisExecutable}`);
        console.warn('[Redis] 将使用系统Redis（需要手动启动）');
        resolve(); // 不算失败，允许继续
        return;
      }

      // 给予执行权限（Linux/macOS）
      if (process.platform !== 'win32') {
        try {
          fs.chmodSync(redisExecutable, '755');
        } catch (error) {
          console.error('[Redis] 设置执行权限失败:', error);
        }
      }

      console.log(`[Redis] 正在启动: ${redisExecutable}`);

      // 启动Redis进程
      const redisArgs = fs.existsSync(redisConfig) ? [redisConfig] : [];
      
      redisProcess = spawn(redisExecutable, redisArgs, {
        cwd: path.join(appPath, 'redis'),
        env: {
          ...process.env,
        },
      });

      // 监听输出
      redisProcess.stdout?.on('data', (data) => {
        const message = data.toString().trim();
        console.log(`[Redis] ${message}`);
        
        // 检测Redis启动成功的标志
        if (message.includes('Ready to accept connections') || 
            message.includes('The server is now ready')) {
          console.log('[Redis] 启动成功');
          if (!resolve._called) {
            resolve._called = true;
            resolve();
          }
        }
      });

      redisProcess.stderr?.on('data', (data) => {
        console.log(`[Redis] ${data.toString().trim()}`);
      });

      redisProcess.on('error', (error) => {
        console.error('[Redis] 启动失败:', error);
        redisProcess = null;
        // Redis启动失败不算致命错误
        if (!resolve._called) {
          resolve._called = true;
          resolve();
        }
      });

      redisProcess.on('exit', (code, signal) => {
        console.log(`[Redis] 进程退出，代码: ${code}, 信号: ${signal}`);
        redisProcess = null;
      });

      // 设置超时（Redis通常很快启动）
      setTimeout(() => {
        if (!resolve._called) {
          resolve._called = true;
          console.log('[Redis] 启动超时，假定成功');
          resolve();
        }
      }, 5000);

    } catch (error) {
      console.error('[Redis] 启动异常:', error);
      // Redis启动失败不阻止应用启动
      resolve();
    }
  });
}

/**
 * ✅ P0-1优化：启动后端服务（完善版）
 */
async function startBackend() {
  return new Promise((resolve, reject) => {
    try {
      let backendExecutable;
      let backendCwd;
      
      if (isDev) {
        // 开发环境：直接运行 Python
        backendExecutable = 'python';
        const backendScript = path.join(__dirname, '../../backend/app/main.py');
        backendCwd = path.join(__dirname, '../../backend');
        
        backendProcess = spawn(backendExecutable, [backendScript], {
          cwd: backendCwd,
          env: {
            ...process.env,
            PYTHONUNBUFFERED: '1',
          },
        });
      } else {
        // 生产环境：运行打包后的可执行文件
        if (process.platform === 'win32') {
          backendExecutable = path.join(appPath, 'backend', 'kook-forwarder-backend.exe');
        } else {
          backendExecutable = path.join(appPath, 'backend', 'kook-forwarder-backend');
        }
        
        backendCwd = path.join(appPath, 'backend');

        // 检查后端文件是否存在
        if (!fs.existsSync(backendExecutable)) {
          const error = new Error(`后端可执行文件不存在: ${backendExecutable}`);
          console.error('[Backend]', error.message);
          
          dialog.showErrorBox(
            '启动失败',
            `后端服务未找到。\n路径: ${backendExecutable}\n\n请重新安装应用程序。`
          );
          
          reject(error);
          return;
        }

        // 给予执行权限（Linux/macOS）
        if (process.platform !== 'win32') {
          try {
            fs.chmodSync(backendExecutable, '755');
          } catch (error) {
            console.error('[Backend] 设置执行权限失败:', error);
          }
        }

        console.log(`[Backend] 启动路径: ${backendExecutable}`);
        
        backendProcess = spawn(backendExecutable, [], {
          cwd: backendCwd,
          env: {
            ...process.env,
            // 设置数据目录到用户目录
            DATA_DIR: path.join(app.getPath('userData'), 'data'),
          },
        });
      }

      // 监听后端输出
      backendProcess.stdout?.on('data', (data) => {
        const message = data.toString().trim();
        console.log(`[Backend] ${message}`);
      });

      backendProcess.stderr?.on('data', (data) => {
        const message = data.toString().trim();
        // 过滤掉一些正常的警告
        if (!message.includes('WARNING') && !message.includes('DEBUG')) {
          console.error(`[Backend Error] ${message}`);
        } else {
          console.log(`[Backend] ${message}`);
        }
      });

      backendProcess.on('error', (error) => {
        console.error('[Backend] 启动失败:', error);
        backendProcess = null;
        reject(error);
      });

      backendProcess.on('exit', (code, signal) => {
        console.log(`[Backend] 进程退出，代码: ${code}, 信号: ${signal}`);
        backendProcess = null;
        
        // 如果不是正常退出且不是在退出应用，尝试重启
        if (code !== 0 && !isQuitting) {
          console.warn('[Backend] 异常退出，5秒后尝试重启...');
          setTimeout(() => {
            if (!isQuitting && !backendProcess) {
              console.log('[Backend] 尝试自动重启...');
              startBackend().catch(err => {
                console.error('[Backend] 重启失败:', err);
              });
            }
          }, 5000);
        }
      });

      // 等待后端启动并检查健康状态
      setTimeout(() => {
        checkBackendHealth()
          .then(() => {
            console.log('[Backend] 启动成功');
            resolve();
          })
          .catch((error) => {
            console.error('[Backend] 健康检查失败:', error);
            reject(error);
          });
      }, 3000);

    } catch (error) {
      console.error('[Backend] 启动异常:', error);
      reject(error);
    }
  });
}

/**
 * 检查后端健康状态
 */
async function checkBackendHealth() {
  const maxRetries = 10;
  const retryDelay = 1000;

  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(`${BACKEND_URL}/health`);
      if (response.ok) {
        return true;
      }
    } catch (error) {
      if (i === maxRetries - 1) {
        throw error;
      }
      await new Promise(resolve => setTimeout(resolve, retryDelay));
    }
  }
  throw new Error('后端服务启动超时');
}

/**
 * ✅ P0-1优化：停止后端服务和Redis
 */
function stopBackend() {
  // 1. 停止后端
  if (backendProcess) {
    console.log('[Backend] 正在停止...');
    try {
      if (process.platform === 'win32') {
        // Windows: 使用taskkill强制终止
        spawn('taskkill', ['/pid', backendProcess.pid, '/f', '/t']);
      } else {
        // Unix: 发送SIGTERM
        backendProcess.kill('SIGTERM');
      }
    } catch (error) {
      console.error('[Backend] 停止失败:', error);
    }
    backendProcess = null;
  }

  // 2. 停止Redis
  if (redisProcess) {
    console.log('[Redis] 正在停止...');
    try {
      if (process.platform === 'win32') {
        spawn('taskkill', ['/pid', redisProcess.pid, '/f', '/t']);
      } else {
        redisProcess.kill('SIGTERM');
      }
    } catch (error) {
      console.error('[Redis] 停止失败:', error);
    }
    redisProcess = null;
  }
}

/**
 * IPC 通信处理
 */
function setupIPC() {
  // 获取应用版本
  ipcMain.handle('app:getVersion', () => {
    return app.getVersion();
  });

  // 获取应用路径
  ipcMain.handle('app:getPath', (event, name) => {
    return app.getPath(name);
  });

  // 打开外部链接
  ipcMain.handle('app:openExternal', async (event, url) => {
    await shell.openExternal(url);
  });

  // 打开文件对话框
  ipcMain.handle('dialog:openFile', async (event, options) => {
    const result = await dialog.showOpenDialog(mainWindow, options);
    return result;
  });

  // 打开保存对话框
  ipcMain.handle('dialog:saveFile', async (event, options) => {
    const result = await dialog.showSaveDialog(mainWindow, options);
    return result;
  });

  // 显示消息框
  ipcMain.handle('dialog:showMessage', async (event, options) => {
    const result = await dialog.showMessageBox(mainWindow, options);
    return result;
  });

  // 最小化窗口
  ipcMain.handle('window:minimize', () => {
    mainWindow?.minimize();
  });

  // 最大化/还原窗口
  ipcMain.handle('window:maximize', () => {
    if (mainWindow?.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow?.maximize();
    }
  });

  // 关闭窗口（最小化到托盘）
  ipcMain.handle('window:close', () => {
    mainWindow?.hide();
  });

  // 退出应用
  ipcMain.handle('app:quit', () => {
    isQuitting = true;
    app.quit();
  });

  // 重启应用
  ipcMain.handle('app:relaunch', () => {
    app.relaunch();
    app.quit();
  });

  // 获取自动启动状态
  ipcMain.handle('autoLaunch:isEnabled', async () => {
    return await autoLauncher.isEnabled();
  });

  // 设置自动启动
  ipcMain.handle('autoLaunch:enable', async () => {
    await autoLauncher.enable();
  });

  // 禁用自动启动
  ipcMain.handle('autoLaunch:disable', async () => {
    await autoLauncher.disable();
  });

  // 获取后端URL
  ipcMain.handle('backend:getURL', () => {
    return BACKEND_URL;
  });

  // 检查后端状态
  ipcMain.handle('backend:checkHealth', async () => {
    try {
      await checkBackendHealth();
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });
}

/**
 * 应用启动
 */
app.whenReady().then(async () => {
  console.log('='.repeat(60));
  console.log(`KOOK消息转发系统 v${VERSION}`);
  console.log('='.repeat(60));

  try {
    // ✅ P0-1优化：先启动Redis，再启动后端
    console.log('[Main] 正在启动Redis服务...');
    await startRedis();

    // 启动后端服务
    console.log('[Main] 正在启动后端服务...');
    await startBackend();

    // 创建窗口
    console.log('[Main] 正在创建主窗口...');
    createWindow();

    // 创建托盘（使用新的托盘管理器）
    console.log('[Main] 正在创建系统托盘...');
    trayManager = new TrayManager(mainWindow);
    trayManager.create();
    trayManager.updateStatus('online', '服务运行中');

    // 设置IPC通信
    setupIPC();

    console.log('[Main] 应用启动完成！');
  } catch (error) {
    console.error('[Main] 启动失败:', error);
    
    dialog.showErrorBox(
      '启动失败',
      `无法启动应用：${error.message}\n\n请检查日志文件或联系技术支持。`
    );
    
    app.quit();
  }

  // macOS 特定处理
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

/**
 * 应用退出前清理
 */
app.on('before-quit', () => {
  isQuitting = true;
});

/**
 * 所有窗口关闭
 */
app.on('window-all-closed', () => {
  // macOS 上除非用户明确退出，否则保持应用运行
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

/**
 * 应用退出
 */
app.on('will-quit', () => {
  console.log('[Main] 正在关闭应用...');
  stopBackend();
});

/**
 * 捕获未处理的异常
 */
process.on('uncaughtException', (error) => {
  console.error('[Main] 未捕获的异常:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('[Main] 未处理的Promise拒绝:', reason);
});
