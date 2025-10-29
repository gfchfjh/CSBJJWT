/**
 * Electron自动更新模块
 * ✅ P2-2优化：完整的自动更新功能
 */

const { autoUpdater } = require('electron-updater');
const { dialog, BrowserWindow } = require('electron');
const log = require('electron-log');

// 配置日志
log.transports.file.level = 'info';
autoUpdater.logger = log;

// 配置更新服务器
autoUpdater.setFeedURL({
  provider: 'github',
  owner: 'your-github-username',
  repo: 'CSBJJWT'
});

// 禁用自动下载
autoUpdater.autoDownload = false;

// 更新状态
let updateDownloaded = false;

/**
 * 初始化自动更新
 */
function initAutoUpdater(mainWindow) {
  // 检查更新时
  autoUpdater.on('checking-for-update', () => {
    log.info('正在检查更新...');
    sendStatusToWindow(mainWindow, 'checking');
  });

  // 有可用更新时
  autoUpdater.on('update-available', (info) => {
    log.info('发现新版本:', info.version);
    
    const dialogOpts = {
      type: 'info',
      buttons: ['立即下载', '稍后提醒'],
      title: '发现新版本',
      message: `发现新版本 v${info.version}`,
      detail: `当前版本: v${autoUpdater.currentVersion}\n新版本: v${info.version}\n\n更新内容:\n${info.releaseNotes || '暂无更新说明'}`
    };

    dialog.showMessageBox(mainWindow, dialogOpts).then((returnValue) => {
      if (returnValue.response === 0) {
        // 用户选择立即下载
        autoUpdater.downloadUpdate();
        sendStatusToWindow(mainWindow, 'downloading');
      }
    });
  });

  // 没有可用更新时
  autoUpdater.on('update-not-available', (info) => {
    log.info('已是最新版本:', info.version);
    sendStatusToWindow(mainWindow, 'up-to-date');
  });

  // 下载进度
  autoUpdater.on('download-progress', (progressObj) => {
    let message = `下载速度: ${progressObj.bytesPerSecond}`;
    message += ` - 已下载 ${progressObj.percent.toFixed(2)}%`;
    message += ` (${progressObj.transferred}/${progressObj.total})`;
    
    log.info(message);
    sendStatusToWindow(mainWindow, 'download-progress', progressObj);
  });

  // 更新下载完成
  autoUpdater.on('update-downloaded', (info) => {
    updateDownloaded = true;
    log.info('更新下载完成:', info.version);
    
    const dialogOpts = {
      type: 'info',
      buttons: ['立即重启', '稍后重启'],
      title: '更新已下载',
      message: '新版本已下载完成',
      detail: `版本 v${info.version} 已下载完成。\n重启应用以安装更新。`
    };

    dialog.showMessageBox(mainWindow, dialogOpts).then((returnValue) => {
      if (returnValue.response === 0) {
        // 用户选择立即重启
        autoUpdater.quitAndInstall(false, true);
      }
    });
    
    sendStatusToWindow(mainWindow, 'downloaded');
  });

  // 更新错误
  autoUpdater.on('error', (error) => {
    log.error('自动更新错误:', error);
    
    dialog.showMessageBox(mainWindow, {
      type: 'error',
      title: '更新失败',
      message: '检查更新时发生错误',
      detail: error.message
    });
    
    sendStatusToWindow(mainWindow, 'error', { message: error.message });
  });
}

/**
 * 发送状态到渲染进程
 */
function sendStatusToWindow(mainWindow, status, data = {}) {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('update-status', {
      status,
      ...data
    });
  }
}

/**
 * 检查更新（手动触发）
 */
function checkForUpdates(mainWindow) {
  log.info('手动检查更新');
  autoUpdater.checkForUpdates();
}

/**
 * 下载更新（手动触发）
 */
function downloadUpdate() {
  log.info('开始下载更新');
  autoUpdater.downloadUpdate();
}

/**
 * 安装更新（重启应用）
 */
function quitAndInstall() {
  if (updateDownloaded) {
    autoUpdater.quitAndInstall(false, true);
  } else {
    log.warn('没有可安装的更新');
  }
}

/**
 * 获取当前版本
 */
function getCurrentVersion() {
  return autoUpdater.currentVersion.version;
}

module.exports = {
  initAutoUpdater,
  checkForUpdates,
  downloadUpdate,
  quitAndInstall,
  getCurrentVersion
};
