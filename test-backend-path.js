const path = require('path');

// 模拟打包后的环境
const process = { resourcesPath: '/workspace/frontend/dist-electron/linux-unpacked/resources' };
const appPath = process.resourcesPath;

const backendExecutable = path.join(appPath, 'backend', 'KOOKForwarder', 'KOOKForwarder');
const backendCwd = path.join(appPath, 'backend', 'KOOKForwarder');

console.log('appPath:', appPath);
console.log('backendExecutable:', backendExecutable);
console.log('backendCwd:', backendCwd);

const fs = require('fs');
console.log('\n检查文件是否存在:');
console.log('backendExecutable exists:', fs.existsSync(backendExecutable));
console.log('backendCwd exists:', fs.existsSync(backendCwd));

if (fs.existsSync(backendCwd)) {
  console.log('\nbackendCwd目录内容:');
  console.log(fs.readdirSync(backendCwd));
}
