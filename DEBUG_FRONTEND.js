// ========================================
// 前端调试脚本
// 请在浏览器Console中执行此脚本
// ========================================

console.log('=== 开始前端调试 ===');

// 1. 检查Vue实例
console.log('\n[1] 检查Vue实例...');
if (typeof window.__VUE_DEVTOOLS_GLOBAL_HOOK__ !== 'undefined') {
    console.log('✅ Vue DevTools已安装');
} else {
    console.log('⚠️ Vue DevTools未安装');
}

// 2. 检查后端连接
console.log('\n[2] 检查后端API连接...');
fetch('http://localhost:9527/api/system/status')
    .then(res => res.json())
    .then(data => {
        console.log('✅ 后端连接正常');
        console.log('后端状态:', data);
    })
    .catch(err => {
        console.error('❌ 后端连接失败:', err);
        console.log('请确认后端服务是否运行在 http://localhost:9527');
    });

// 3. 检查账号列表
console.log('\n[3] 检查账号列表...');
fetch('http://localhost:9527/api/accounts/')
    .then(res => res.json())
    .then(accounts => {
        console.log('✅ 账号列表获取成功');
        console.log(`账号数量: ${accounts.length}`);
        accounts.forEach(acc => {
            console.log(`  - ID:${acc.id}, 邮箱:${acc.email}, 状态:${acc.status}`);
        });
        
        // 如果有账号，测试启动API
        if (accounts.length > 0) {
            const testAccountId = accounts[0].id;
            console.log(`\n[4] 测试启动API (账号ID: ${testAccountId})...`);
            
            fetch(`http://localhost:9527/api/accounts/${testAccountId}/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(res => {
                console.log('API响应状态码:', res.status);
                return res.json();
            })
            .then(data => {
                console.log('✅ 启动API调用成功');
                console.log('响应数据:', data);
            })
            .catch(err => {
                console.error('❌ 启动API调用失败:', err);
            });
        }
    })
    .catch(err => {
        console.error('❌ 获取账号列表失败:', err);
    });

// 4. 检查Element Plus
console.log('\n[5] 检查Element Plus...');
if (typeof ElMessage !== 'undefined') {
    console.log('✅ Element Plus已加载');
} else {
    console.log('❌ Element Plus未加载');
}

// 5. 检查axios
console.log('\n[6] 检查axios...');
if (typeof axios !== 'undefined') {
    console.log('✅ axios已加载');
} else {
    console.log('⚠️ axios未在全局，应该在模块中');
}

console.log('\n=== 调试完成 ===');
console.log('\n请复制上面的所有输出发给我！');
