// KOOK Cookie Exporter - Popup Script

document.addEventListener('DOMContentLoaded', function() {
  const exportBtn = document.getElementById('exportBtn');
  const copyBtn = document.getElementById('copyBtn');
  const downloadBtn = document.getElementById('downloadBtn');
  const status = document.getElementById('status');
  const cookieOutput = document.getElementById('cookieOutput');
  const cookieInfo = document.getElementById('cookieInfo');
  const cookieCount = document.getElementById('cookieCount');
  
  let exportedCookies = null;
  
  // 导出Cookie
  exportBtn.addEventListener('click', async () => {
    try {
      exportBtn.disabled = true;
      exportBtn.textContent = '⏳ 导出中...';
      status.className = 'status info';
      status.textContent = '正在读取Cookie...';
      
      // 检查当前标签页
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (!tab.url.includes('kookapp.cn') && !tab.url.includes('kaiheila.cn')) {
        throw new Error('请先访问KOOK网站（www.kookapp.cn）');
      }
      
      // 获取KOOK Cookie
      const cookies = await chrome.cookies.getAll({
        domain: '.kookapp.cn'
      });
      
      // 同时获取kaiheila.cn域名的Cookie（旧域名）
      const oldCookies = await chrome.cookies.getAll({
        domain: '.kaiheila.cn'
      });
      
      // 合并Cookie
      const allCookies = [...cookies, ...oldCookies];
      
      if (allCookies.length === 0) {
        throw new Error('未找到KOOK Cookie，请确保已登录KOOK');
      }
      
      // 格式化Cookie
      exportedCookies = allCookies.map(cookie => ({
        name: cookie.name,
        value: cookie.value,
        domain: cookie.domain,
        path: cookie.path,
        secure: cookie.secure,
        httpOnly: cookie.httpOnly,
        sameSite: cookie.sameSite,
        expirationDate: cookie.expirationDate
      }));
      
      // 显示结果
      const cookieJson = JSON.stringify(exportedCookies, null, 2);
      cookieOutput.value = cookieJson;
      cookieOutput.style.display = 'block';
      copyBtn.style.display = 'block';
      downloadBtn.style.display = 'block';
      cookieInfo.style.display = 'block';
      cookieCount.textContent = exportedCookies.length;
      
      status.className = 'status success';
      status.textContent = '✅ Cookie导出成功！';
      
      exportBtn.textContent = '🔄 重新导出';
      exportBtn.disabled = false;
      
    } catch (error) {
      console.error('导出失败:', error);
      status.className = 'status error';
      status.textContent = '❌ ' + error.message;
      exportBtn.disabled = false;
      exportBtn.textContent = '🔄 重试';
    }
  });
  
  // 复制到剪贴板
  copyBtn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(cookieOutput.value);
      
      const originalText = copyBtn.textContent;
      copyBtn.textContent = '✅ 已复制！';
      copyBtn.disabled = true;
      
      setTimeout(() => {
        copyBtn.textContent = originalText;
        copyBtn.disabled = false;
      }, 2000);
    } catch (error) {
      alert('复制失败：' + error.message);
    }
  });
  
  // 下载为文件
  downloadBtn.addEventListener('click', () => {
    try {
      const blob = new Blob([cookieOutput.value], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
      a.href = url;
      a.download = `kook-cookies-${timestamp}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      const originalText = downloadBtn.textContent;
      downloadBtn.textContent = '✅ 已下载！';
      downloadBtn.disabled = true;
      
      setTimeout(() => {
        downloadBtn.textContent = originalText;
        downloadBtn.disabled = false;
      }, 2000);
    } catch (error) {
      alert('下载失败：' + error.message);
    }
  });
});
