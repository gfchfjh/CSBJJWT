/**
 * KOOK Cookie导出器 v2.0 - Enhanced
 * 特性：
 * - 双域名支持（kookapp.cn + www.kookapp.cn）
 * - 智能验证关键Cookie
 * - 自动发送到转发系统
 * - 美化界面
 * - 快捷键支持
 */

let exportedCookies = null;

// 关键Cookie名称（必须存在）
const REQUIRED_COOKIES = ['token', 'session', 'user_id'];

// 支持的域名
const SUPPORTED_DOMAINS = ['.kookapp.cn', '.www.kookapp.cn', 'kookapp.cn', 'www.kookapp.cn'];

// 转发系统API地址
const FORWARDER_API = 'http://localhost:9527/api/cookie-import/from-extension';

/**
 * 导出Cookie
 */
async function exportCookies() {
    const exportBtn = document.getElementById('exportBtn');
    const statusCard = document.getElementById('statusCard');
    const statusText = document.getElementById('statusText');
    const stats = document.getElementById('stats');
    const cookieList = document.getElementById('cookieList');
    const copyBtn = document.getElementById('copyBtn');
    const sendToSystemBtn = document.getElementById('sendToSystemBtn');
    
    try {
        // 显示加载状态
        exportBtn.disabled = true;
        exportBtn.innerHTML = '<span class="loading"></span>正在导出...';
        statusText.textContent = '正在从双域名获取Cookie...';
        
        // 从所有支持的域名获取Cookie
        let allCookies = [];
        let domainCount = 0;
        
        for (const domain of SUPPORTED_DOMAINS) {
            try {
                const cookies = await chrome.cookies.getAll({ domain });
                if (cookies && cookies.length > 0) {
                    allCookies.push(...cookies);
                    domainCount++;
                    console.log(`从 ${domain} 获取到 ${cookies.length} 个Cookie`);
                }
            } catch (error) {
                console.warn(`从 ${domain} 获取Cookie失败:`, error);
            }
        }
        
        // 去重（按name+domain）
        const uniqueCookies = Array.from(
            new Map(allCookies.map(c => [`${c.name}@${c.domain}`, c])).values()
        );
        
        console.log(`总共获取到 ${uniqueCookies.length} 个唯一Cookie`);
        
        if (uniqueCookies.length === 0) {
            throw new Error('未找到Cookie，请确保已登录KOOK');
        }
        
        // 验证关键Cookie
        const cookieNames = uniqueCookies.map(c => c.name);
        const missingCookies = REQUIRED_COOKIES.filter(name => !cookieNames.includes(name));
        
        if (missingCookies.length > 0) {
            statusCard.className = 'status-card error';
            statusText.innerHTML = `⚠️ 缺少关键Cookie: <strong>${missingCookies.join(', ')}</strong><br>请确保已登录KOOK网页版`;
            exportBtn.disabled = false;
            exportBtn.textContent = '🍪 重新导出';
            return;
        }
        
        // 格式化Cookie为系统需要的格式
        exportedCookies = uniqueCookies.map(cookie => ({
            name: cookie.name,
            value: cookie.value,
            domain: cookie.domain,
            path: cookie.path || '/',
            secure: cookie.secure || false,
            httpOnly: cookie.httpOnly || false,
            sameSite: cookie.sameSite || 'Lax',
            expirationDate: cookie.expirationDate || null
        }));
        
        // 显示成功状态
        statusCard.className = 'status-card success';
        statusText.innerHTML = `✅ 成功导出 <strong>${exportedCookies.length}</strong> 个Cookie，包含所有关键Cookie`;
        
        // 显示统计
        stats.style.display = 'grid';
        document.getElementById('cookieCount').textContent = exportedCookies.length;
        document.getElementById('domainCount').textContent = domainCount;
        
        // 显示Cookie列表（仅显示关键Cookie）
        cookieList.style.display = 'block';
        cookieList.innerHTML = '';
        
        REQUIRED_COOKIES.forEach(name => {
            const cookie = exportedCookies.find(c => c.name === name);
            if (cookie) {
                const item = document.createElement('div');
                item.className = 'cookie-item';
                item.innerHTML = `
                    <span class="cookie-name">${cookie.name}</span>
                    <span class="cookie-value">${cookie.value.substring(0, 20)}...</span>
                `;
                cookieList.appendChild(item);
            }
        });
        
        // 显示操作按钮
        copyBtn.style.display = 'block';
        sendToSystemBtn.style.display = 'block';
        
        exportBtn.textContent = '✅ 导出成功';
        
        // 尝试自动发送到转发系统
        setTimeout(() => {
            sendToSystem(true); // 自动发送
        }, 500);
        
    } catch (error) {
        console.error('导出Cookie失败:', error);
        statusCard.className = 'status-card error';
        statusText.textContent = `❌ 导出失败: ${error.message}`;
        exportBtn.disabled = false;
        exportBtn.textContent = '🔄 重试';
    }
}

/**
 * 复制到剪贴板
 */
async function copyToClipboard() {
    const copyBtn = document.getElementById('copyBtn');
    const statusText = document.getElementById('statusText');
    
    if (!exportedCookies) {
        return;
    }
    
    try {
        const jsonText = JSON.stringify(exportedCookies, null, 2);
        await navigator.clipboard.writeText(jsonText);
        
        // 显示反馈
        copyBtn.textContent = '✅ 已复制！';
        statusText.textContent = '✅ Cookie已复制到剪贴板，可以粘贴到转发系统中';
        
        setTimeout(() => {
            copyBtn.textContent = '📋 复制到剪贴板';
        }, 2000);
        
    } catch (error) {
        console.error('复制失败:', error);
        statusText.textContent = '❌ 复制失败: ' + error.message;
    }
}

/**
 * 发送到转发系统
 */
async function sendToSystem(isAuto = false) {
    const sendBtn = document.getElementById('sendToSystemBtn');
    const statusCard = document.getElementById('statusCard');
    const statusText = document.getElementById('statusText');
    
    if (!exportedCookies) {
        return;
    }
    
    try {
        if (!isAuto) {
            sendBtn.disabled = true;
            sendBtn.innerHTML = '<span class="loading"></span>正在发送...';
        }
        
        statusText.textContent = '正在发送到转发系统...';
        
        // 发送到转发系统API
        const response = await fetch(FORWARDER_API, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                cookies: exportedCookies,
                source: 'chrome_extension_v2',
                timestamp: Date.now()
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // 显示成功
        statusCard.className = 'status-card success';
        statusText.innerHTML = `🚀 <strong>Cookie已自动导入转发系统！</strong><br>账号ID: ${result.account_id || 'N/A'}`;
        
        if (!isAuto) {
            sendBtn.textContent = '✅ 发送成功！';
            sendBtn.disabled = false;
        }
        
        // 如果是自动发送，提示用户
        if (isAuto) {
            console.log('✅ Cookie已自动发送到转发系统');
        }
        
    } catch (error) {
        console.error('发送失败:', error);
        
        // 如果是自动发送失败（转发系统未运行），显示友好提示
        if (isAuto) {
            statusText.innerHTML = `ℹ️ Cookie已导出，但转发系统未运行<br>您可以手动复制或稍后发送`;
        } else {
            statusCard.className = 'status-card error';
            statusText.innerHTML = `❌ 发送失败: ${error.message}<br>请确保转发系统正在运行（端口9527）`;
            sendBtn.disabled = false;
            sendBtn.textContent = '🔄 重试发送';
        }
    }
}

/**
 * 初始化
 */
document.addEventListener('DOMContentLoaded', () => {
    // 绑定事件
    document.getElementById('exportBtn').addEventListener('click', exportCookies);
    document.getElementById('copyBtn').addEventListener('click', copyToClipboard);
    document.getElementById('sendToSystemBtn').addEventListener('click', () => sendToSystem(false));
    
    // 帮助链接
    document.getElementById('helpLink').addEventListener('click', (e) => {
        e.preventDefault();
        chrome.tabs.create({
            url: 'https://github.com/gfchfjh/CSBJJWT/blob/main/docs/tutorials/02-Cookie%E8%8E%B7%E5%8F%96%E8%AF%A6%E7%BB%86%E6%95%99%E7%A8%8B.md'
        });
    });
    
    // 反馈链接
    document.getElementById('feedbackLink').addEventListener('click', (e) => {
        e.preventDefault();
        chrome.tabs.create({
            url: 'https://github.com/gfchfjh/CSBJJWT/issues'
        });
    });
    
    // 检查当前标签页是否为KOOK
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const currentTab = tabs[0];
        const url = currentTab.url || '';
        
        if (!url.includes('kookapp.cn')) {
            document.getElementById('statusText').innerHTML = 
                '⚠️ 当前页面不是KOOK<br>请切换到 <strong>www.kookapp.cn</strong> 后再导出';
            document.getElementById('statusCard').className = 'status-card error';
        }
    });
});

/**
 * 监听来自background script的消息（快捷键触发）
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'exportCookie') {
        exportCookies();
    }
});
