/**
 * 自动更新模块
 * ✅ P2-4: Electron自动更新机制
 */
const { autoUpdater } = require('electron-updater')
const { dialog } = require('electron')
const log = require('electron-log')

// 配置日志
autoUpdater.logger = log
autoUpdater.logger.transports.file.level = 'info'

class AutoUpdater {
  constructor(mainWindow) {
    this.mainWindow = mainWindow
    this.setupListeners()
  }

  setupListeners() {
    // 检查更新出错
    autoUpdater.on('error', (error) => {
      log.error('更新出错:', error)
      this.sendStatusToWindow('update-error', error)
    })

    // 检查更新
    autoUpdater.on('checking-for-update', () => {
      log.info('正在检查更新...')
      this.sendStatusToWindow('checking-for-update')
    })

    // 有可用更新
    autoUpdater.on('update-available', (info) => {
      log.info('发现新版本:', info.version)
      this.sendStatusToWindow('update-available', info)
      
      dialog.showMessageBox(this.mainWindow, {
        type: 'info',
        title: '发现新版本',
        message: `发现新版本 ${info.version}，是否立即更新？`,
        buttons: ['立即更新', '稍后提醒'],
        defaultId: 0,
        cancelId: 1
      }).then(result => {
        if (result.response === 0) {
          autoUpdater.downloadUpdate()
        }
      })
    })

    // 没有可用更新
    autoUpdater.on('update-not-available', (info) => {
      log.info('当前已是最新版本')
      this.sendStatusToWindow('update-not-available', info)
    })

    // 下载进度
    autoUpdater.on('download-progress', (progressObj) => {
      let logMessage = `下载速度: ${progressObj.bytesPerSecond}`
      logMessage += ` - 已下载 ${progressObj.percent}%`
      logMessage += ` (${progressObj.transferred}/${progressObj.total})`
      
      log.info(logMessage)
      this.sendStatusToWindow('download-progress', progressObj)
    })

    // 下载完成
    autoUpdater.on('update-downloaded', (info) => {
      log.info('更新下载完成')
      this.sendStatusToWindow('update-downloaded', info)
      
      dialog.showMessageBox(this.mainWindow, {
        type: 'info',
        title: '更新下载完成',
        message: '新版本已下载完成，是否立即重启应用进行更新？',
        buttons: ['立即重启', '稍后重启'],
        defaultId: 0,
        cancelId: 1
      }).then(result => {
        if (result.response === 0) {
          autoUpdater.quitAndInstall(false, true)
        }
      })
    })
  }

  sendStatusToWindow(event, data) {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.webContents.send('update-status', {
        event,
        data
      })
    }
  }

  checkForUpdates() {
    autoUpdater.checkForUpdates()
  }

  checkForUpdatesAndNotify() {
    autoUpdater.checkForUpdatesAndNotify()
  }

  setFeedURL(url) {
    autoUpdater.setFeedURL(url)
  }

  downloadUpdate() {
    autoUpdater.downloadUpdate()
  }

  quitAndInstall() {
    autoUpdater.quitAndInstall(false, true)
  }
}

module.exports = AutoUpdater
