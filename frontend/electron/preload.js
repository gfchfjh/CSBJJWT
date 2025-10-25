/**
 * Electron Preload脚本
 * ====================
 * 功能：安全地桥接Electron主进程和渲染进程
 * 
 * 作者：KOOK Forwarder Team
 * 日期：2025-10-25
 */

const { contextBridge, ipcRenderer } = require('electron');

// 暴露安全的API给渲染进程
contextBridge.exposeInMainWorld('electron', {
  // 监听首次启动事件
  onShowWizard: (callback) => {
    ipcRenderer.on('show-wizard', callback);
  },
  
  // 监听后端重启事件
  onBackendRestarted: (callback) => {
    ipcRenderer.on('backend-restarted', callback);
  },
  
  // 通知主进程配置向导已完成
  wizardCompleted: () => {
    ipcRenderer.send('wizard-completed');
  },
  
  // 打开外部链接
  openExternalLink: (url) => {
    ipcRenderer.send('open-external-link', url);
  },
  
  // 获取后端状态
  getBackendStatus: () => {
    return ipcRenderer.invoke('get-backend-status');
  },
  
  // 获取应用版本
  getAppVersion: () => {
    return '4.0.0';
  },
  
  // 判断是否在Electron环境
  isElectron: () => {
    return true;
  }
});
