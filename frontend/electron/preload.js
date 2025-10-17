/**
 * Electron Preload 脚本
 * 为渲染进程暴露安全的API
 */
const { contextBridge, ipcRenderer } = require('electron')

// 暴露Electron API到渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 应用信息
  getAppInfo: () => ipcRenderer.invoke('get-app-info'),
  
  // 文件系统操作
  openPath: (path) => ipcRenderer.invoke('open-path', path),
  
  // 应用控制
  relaunch: () => ipcRenderer.invoke('relaunch-app'),
  
  // 对话框
  showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),
  showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),
  showMessageBox: (options) => ipcRenderer.invoke('show-message-box', options),
  
  // 通知
  showNotification: (title, body, type) => {
    ipcRenderer.send('show-notification', { title, body, type })
  },
  
  // 监听后端通知
  onBackendNotification: (callback) => {
    ipcRenderer.on('backend-notification', (event, data) => callback(data))
  },
  
  // 监听导航请求
  onNavigateTo: (callback) => {
    ipcRenderer.on('navigate-to', (event, path) => callback(path))
  },
  
  // 移除监听器
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel)
  }
})

// 暴露Node.js相关API（可选）
contextBridge.exposeInMainWorld('nodeAPI', {
  platform: process.platform,
  env: process.env.NODE_ENV
})
