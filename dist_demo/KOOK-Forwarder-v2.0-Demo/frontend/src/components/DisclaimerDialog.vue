<template>
  <!-- 🚀 P1-1优化: 免责声明弹窗 -->
  <el-dialog
    v-model="visible"
    title="⚠️ 免责声明"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
    width="600px"
    center
  >
    <div class="disclaimer-content">
      <el-alert type="warning" :closable="false" show-icon>
        <template #title>
          <strong>请仔细阅读以下条款</strong>
        </template>
        使用本软件即表示您同意以下所有条款
      </el-alert>
      
      <div class="terms-list">
        <ol>
          <li class="term-item">
            <div class="term-title">
              <el-icon color="#f59e0b"><Warning /></el-icon>
              <strong>技术风险</strong>
            </div>
            <p>
              本软件通过浏览器自动化技术抓取KOOK消息，
              可能违反KOOK服务条款，存在账号被封禁的风险。
            </p>
          </li>
          
          <li class="term-item">
            <div class="term-title">
              <el-icon color="#ef4444"><Lock /></el-icon>
              <strong>使用授权</strong>
            </div>
            <p>
              请仅在已获得授权的场景下使用本软件，
              未经授权转发他人消息可能侵犯隐私权。
            </p>
          </li>
          
          <li class="term-item">
            <div class="term-title">
              <el-icon color="#3b82f6"><Document /></el-icon>
              <strong>法律合规</strong>
            </div>
            <p>
              请遵守所在地区的法律法规，
              不得将本软件用于非法用途。
            </p>
          </li>
          
          <li class="term-item">
            <div class="term-title">
              <el-icon color="#8b5cf6"><CopyDocument /></el-icon>
              <strong>版权声明</strong>
            </div>
            <p>
              转发的消息内容可能涉及版权，
              请尊重原作者的知识产权。
            </p>
          </li>
          
          <li class="term-item">
            <div class="term-title">
              <el-icon color="#10b981"><Shield /></el-icon>
              <strong>数据安全</strong>
            </div>
            <p>
              本软件会在本地存储Cookie和配置信息，
              请妥善保管您的设备，避免数据泄露。
            </p>
          </li>
          
          <li class="term-item">
            <div class="term-title">
              <el-icon color="#64748b"><InfoFilled /></el-icon>
              <strong>免责条款</strong>
            </div>
            <p>
              本软件仅供学习交流使用，
              开发者不承担任何因使用本软件而产生的法律责任。
            </p>
          </li>
        </ol>
      </div>
      
      <el-divider />
      
      <el-checkbox v-model="agreed" size="large" class="agreement-checkbox">
        <strong>我已阅读并同意以上所有条款</strong>
      </el-checkbox>
      
      <div class="additional-info">
        <el-alert type="info" :closable="false">
          <p><strong>温馨提示：</strong></p>
          <ul>
            <li>本软件开源免费，请勿用于商业用途</li>
            <li>建议仅在测试环境或已获授权的生产环境使用</li>
            <li>如遇到账号被封等问题，请自行承担后果</li>
          </ul>
        </el-alert>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="reject" size="large">
          拒绝并退出
        </el-button>
        <el-button 
          type="primary" 
          @click="accept" 
          :disabled="!agreed"
          size="large"
        >
          同意并继续
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Warning, Lock, Document, CopyDocument, 
  Shield, InfoFilled 
} from '@element-plus/icons-vue'

const visible = ref(false)
const agreed = ref(false)

onMounted(() => {
  checkDisclaimer()
})

function checkDisclaimer() {
  const accepted = localStorage.getItem('disclaimer_accepted')
  
  if (!accepted) {
    // 首次启动，显示免责声明
    visible.value = true
  }
}

function accept() {
  if (!agreed.value) {
    ElMessage.warning('请勾选同意条款')
    return
  }
  
  // 保存到LocalStorage
  localStorage.setItem('disclaimer_accepted', 'true')
  localStorage.setItem('disclaimer_accepted_at', new Date().toISOString())
  localStorage.setItem('disclaimer_version', '11.0.0')
  
  visible.value = false
  
  ElMessage.success({
    message: '感谢您的同意，祝使用愉快！',
    duration: 3000
  })
}

async function reject() {
  try {
    await ElMessageBox.confirm(
      '拒绝免责声明将无法使用本软件，确定要退出吗？',
      '确认退出',
      {
        type: 'warning',
        confirmButtonText: '确定退出',
        cancelButtonText: '返回阅读',
        distinguishCancelAndClose: true
      }
    )
    
    // 退出应用
    if (window.electron && window.electron.quit) {
      window.electron.quit()
    } else if (window.close) {
      window.close()
    } else {
      ElMessage.error('无法退出应用，请手动关闭窗口')
    }
    
  } catch (action) {
    // 用户点击取消或关闭，继续显示弹窗
    if (action === 'cancel') {
      // 返回阅读
    }
  }
}

// 暴露方法供父组件调用
defineExpose({
  show: () => {
    visible.value = true
    agreed.value = false
  }
})
</script>

<style scoped>
.disclaimer-content {
  max-height: 600px;
  overflow-y: auto;
  padding: 10px;
}

.terms-list {
  margin: 20px 0;
}

.terms-list ol {
  list-style: none;
  counter-reset: term-counter;
  padding: 0;
}

.term-item {
  counter-increment: term-counter;
  margin: 20px 0;
  padding: 15px;
  border-left: 4px solid #e5e7eb;
  background: #f9fafb;
  border-radius: 4px;
  transition: all 0.3s;
}

.term-item:hover {
  border-left-color: #667eea;
  background: #f3f4f6;
}

.term-item::before {
  content: counter(term-counter);
  display: inline-block;
  width: 30px;
  height: 30px;
  line-height: 30px;
  text-align: center;
  background: #667eea;
  color: white;
  border-radius: 50%;
  font-weight: bold;
  margin-right: 10px;
  float: left;
}

.term-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  margin-bottom: 8px;
  margin-left: 40px;
}

.term-item p {
  margin-left: 40px;
  line-height: 1.6;
  color: #4b5563;
}

.agreement-checkbox {
  display: flex;
  justify-content: center;
  margin: 20px 0;
  padding: 15px;
  background: #fef3c7;
  border-radius: 8px;
}

.agreement-checkbox :deep(.el-checkbox__label) {
  font-size: 16px;
  color: #92400e;
}

.additional-info {
  margin-top: 20px;
}

.additional-info ul {
  margin: 10px 0 0 20px;
  padding: 0;
}

.additional-info li {
  margin: 5px 0;
  line-height: 1.6;
  color: #4b5563;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.dialog-footer .el-button {
  flex: 1;
}

/* 滚动条美化 */
.disclaimer-content::-webkit-scrollbar {
  width: 8px;
}

.disclaimer-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.disclaimer-content::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.disclaimer-content::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
