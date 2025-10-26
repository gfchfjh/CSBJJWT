/**
 * 系统相关 IPC 通信处理
 */

const { ipcMain, shell, app } = require('electron');
const os = require('os');
const fs = require('fs').promises;
const path = require('path');

/**
 * 注册系统相关的IPC处理器
 */
function registerSystemHandlers() {
  // 获取系统信息
  ipcMain.handle('system:getInfo', async () => {
    return {
      platform: process.platform,
      arch: process.arch,
      hostname: os.hostname(),
      cpus: os.cpus().length,
      totalMemory: os.totalmem(),
      freeMemory: os.freemem(),
      uptime: os.uptime(),
      nodeVersion: process.versions.node,
      electronVersion: process.versions.electron,
      chromeVersion: process.versions.chrome,
      v8Version: process.versions.v8,
    };
  });

  // 打开文件所在目录
  ipcMain.handle('system:showItemInFolder', async (event, fullPath) => {
    shell.showItemInFolder(fullPath);
  });

  // 打开路径
  ipcMain.handle('system:openPath', async (event, fullPath) => {
    await shell.openPath(fullPath);
  });

  // 读取文件
  ipcMain.handle('system:readFile', async (event, filePath, encoding = 'utf-8') => {
    try {
      const content = await fs.readFile(filePath, encoding);
      return { success: true, content };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });

  // 写入文件
  ipcMain.handle('system:writeFile', async (event, filePath, content, encoding = 'utf-8') => {
    try {
      await fs.writeFile(filePath, content, encoding);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });

  // 检查文件是否存在
  ipcMain.handle('system:fileExists', async (event, filePath) => {
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  });

  // 创建目录
  ipcMain.handle('system:mkdir', async (event, dirPath, recursive = true) => {
    try {
      await fs.mkdir(dirPath, { recursive });
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });

  // 删除文件
  ipcMain.handle('system:deleteFile', async (event, filePath) => {
    try {
      await fs.unlink(filePath);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });

  // 获取目录内容
  ipcMain.handle('system:readDir', async (event, dirPath) => {
    try {
      const files = await fs.readdir(dirPath, { withFileTypes: true });
      const result = files.map(file => ({
        name: file.name,
        isDirectory: file.isDirectory(),
        isFile: file.isFile(),
      }));
      return { success: true, files: result };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });

  // 获取文件信息
  ipcMain.handle('system:getFileStats', async (event, filePath) => {
    try {
      const stats = await fs.stat(filePath);
      return {
        success: true,
        stats: {
          size: stats.size,
          created: stats.birthtime,
          modified: stats.mtime,
          isFile: stats.isFile(),
          isDirectory: stats.isDirectory(),
        },
      };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });

  // 复制文件
  ipcMain.handle('system:copyFile', async (event, src, dest) => {
    try {
      await fs.copyFile(src, dest);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });

  // 移动文件
  ipcMain.handle('system:moveFile', async (event, src, dest) => {
    try {
      await fs.rename(src, dest);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });

  // 获取应用数据路径
  ipcMain.handle('system:getAppDataPath', () => {
    return app.getPath('userData');
  });

  // 获取临时目录
  ipcMain.handle('system:getTempPath', () => {
    return app.getPath('temp');
  });

  // 获取用户文档目录
  ipcMain.handle('system:getDocumentsPath', () => {
    return app.getPath('documents');
  });

  // 获取下载目录
  ipcMain.handle('system:getDownloadsPath', () => {
    return app.getPath('downloads');
  });

  console.log('[IPC] 系统相关处理器已注册');
}

module.exports = { registerSystemHandlers };
