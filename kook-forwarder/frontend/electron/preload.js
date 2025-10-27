/**
 * Electron 预加载脚本
 * 在渲染进程中提供安全的 Node.js API 访问
 */

const { contextBridge, ipcRenderer } = require('electron');

/**
 * 暴露安全的API到渲染进程
 */
contextBridge.exposeInMainWorld('electronAPI', {
  // 应用相关
  app: {
    getVersion: () => ipcRenderer.invoke('app:getVersion'),
    getPath: (name) => ipcRenderer.invoke('app:getPath', name),
    openExternal: (url) => ipcRenderer.invoke('app:openExternal', url),
    quit: () => ipcRenderer.invoke('app:quit'),
    relaunch: () => ipcRenderer.invoke('app:relaunch'),
  },

  // 窗口控制
  window: {
    minimize: () => ipcRenderer.invoke('window:minimize'),
    maximize: () => ipcRenderer.invoke('window:maximize'),
    close: () => ipcRenderer.invoke('window:close'),
  },

  // 对话框
  dialog: {
    openFile: (options) => ipcRenderer.invoke('dialog:openFile', options),
    saveFile: (options) => ipcRenderer.invoke('dialog:saveFile', options),
    showMessage: (options) => ipcRenderer.invoke('dialog:showMessage', options),
  },

  // 自动启动
  autoLaunch: {
    isEnabled: () => ipcRenderer.invoke('autoLaunch:isEnabled'),
    enable: () => ipcRenderer.invoke('autoLaunch:enable'),
    disable: () => ipcRenderer.invoke('autoLaunch:disable'),
  },

  // 后端服务
  backend: {
    getURL: () => ipcRenderer.invoke('backend:getURL'),
    checkHealth: () => ipcRenderer.invoke('backend:checkHealth'),
  },

  // 系统托盘事件监听
  onTrayAction: (callback) => {
    ipcRenderer.on('tray-action', (event, action) => {
      callback(action);
    });
  },

  // 移除托盘事件监听
  removeTrayActionListener: () => {
    ipcRenderer.removeAllListeners('tray-action');
  },
});

/**
 * 环境信息
 */
contextBridge.exposeInMainWorld('env', {
  platform: process.platform,
  arch: process.arch,
  versions: process.versions,
  isElectron: true,
});

/**
 * 性能监控
 */
contextBridge.exposeInMainWorld('performance', {
  memory: () => process.memoryUsage(),
  cpuUsage: () => process.cpuUsage(),
});

console.log('[Preload] Electron API 已注入到渲染进程');
