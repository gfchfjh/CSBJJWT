/**
 * Background Script for KOOK Cookie Exporter v2.0
 * 支持快捷键触发
 */

// 监听扩展安装
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        console.log('KOOK Cookie导出器 v2.0 已安装');
        
        // 打开欢迎页面
        chrome.tabs.create({
            url: 'https://github.com/gfchfjh/CSBJJWT/blob/main/docs/tutorials/02-Cookie获取详细教程.md'
        });
    } else if (details.reason === 'update') {
        console.log('KOOK Cookie导出器 v2.0 已更新');
    }
});

// 监听快捷键命令
chrome.commands.onCommand.addListener((command) => {
    console.log('快捷键触发:', command);
    
    if (command === 'export-cookie') {
        // 查询当前活动标签页
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const currentTab = tabs[0];
            
            // 检查是否为KOOK页面
            if (currentTab.url && currentTab.url.includes('kookapp.cn')) {
                // 发送消息到popup（如果打开）或content script
                chrome.runtime.sendMessage({ action: 'exportCookie' }, (response) => {
                    if (chrome.runtime.lastError) {
                        console.log('Popup未打开，尝试通过content script导出');
                        
                        // 尝试通过content script导出
                        chrome.tabs.sendMessage(currentTab.id, { action: 'exportCookie' });
                    }
                });
            } else {
                // 不是KOOK页面，显示通知
                chrome.notifications.create({
                    type: 'basic',
                    iconUrl: 'icons/icon-128.png',
                    title: 'KOOK Cookie导出器',
                    message: '请先打开KOOK网页版（www.kookapp.cn）再使用快捷键'
                });
            }
        });
    }
});

// 监听来自content script的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'cookieExported') {
        console.log('Cookie导出成功:', request.count, '个');
        
        // 显示成功通知
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon-128.png',
            title: '✅ Cookie导出成功',
            message: `已成功导出 ${request.count} 个Cookie`
        });
        
        sendResponse({ success: true });
    }
    
    return true; // 保持消息通道打开
});

// 监听标签页更新（检测KOOK页面）
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.includes('kookapp.cn')) {
        console.log('检测到KOOK页面:', tab.url);
        
        // 可以在这里注入content script或显示提示
        chrome.action.setBadgeText({ tabId, text: '✓' });
        chrome.action.setBadgeBackgroundColor({ tabId, color: '#28a745' });
    }
});
