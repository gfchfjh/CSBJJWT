// ========================================
// 检查按钮点击事件
// 在浏览器Console中执行
// ========================================

console.log('=== 检查启动按钮 ===');

// 查找所有启动按钮
const startButtons = document.querySelectorAll('button');
console.log(`页面上共有 ${startButtons.length} 个按钮`);

let foundStartButton = false;

startButtons.forEach((btn, index) => {
    const text = btn.textContent.trim();
    if (text.includes('启动') || text.includes('start')) {
        console.log(`\n找到启动按钮 #${index}:`);
        console.log('  文本:', text);
        console.log('  是否禁用:', btn.disabled);
        console.log('  类名:', btn.className);
        console.log('  父元素:', btn.parentElement.className);
        
        foundStartButton = true;
        
        // 尝试手动触发点击
        console.log('\n尝试手动触发点击事件...');
        btn.addEventListener('click', function(e) {
            console.log('✅ 点击事件已触发！');
            console.log('事件对象:', e);
        }, { once: true });
        
        // 模拟点击
        setTimeout(() => {
            console.log('执行模拟点击...');
            btn.click();
        }, 100);
    }
});

if (!foundStartButton) {
    console.log('\n❌ 未找到启动按钮！');
    console.log('可能原因：');
    console.log('  1. 账号状态不是"offline"');
    console.log('  2. 按钮被v-if隐藏');
    console.log('  3. 页面未正确渲染');
}

// 检查account状态
console.log('\n=== 检查账号状态 ===');
fetch('http://localhost:9527/api/accounts/')
    .then(res => res.json())
    .then(accounts => {
        accounts.forEach(acc => {
            console.log(`账号 ${acc.email}:`);
            console.log(`  - 状态: ${acc.status}`);
            console.log(`  - 应该显示的按钮: ${acc.status === 'offline' ? '启动' : '停止'}`);
        });
    });

console.log('\n=== 检查完成 ===');
