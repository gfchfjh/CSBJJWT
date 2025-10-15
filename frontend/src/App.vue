<template>
  <div class="app-container">
    <router-view />
    
    <!-- 免责声明对话框 -->
    <el-dialog
      v-model="disclaimerVisible"
      title="⚠️ 重要：免责声明"
      width="600px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <div class="disclaimer-content">
        <el-alert
          title="请仔细阅读以下条款"
          type="warning"
          :closable="false"
          style="margin-bottom: 20px"
        />
        
        <div class="disclaimer-text">
          <h3>使用本软件前，请您务必仔细阅读并理解以下条款：</h3>
          
          <ol>
            <li>
              <strong>技术实现风险</strong>
              <p>本软件通过浏览器自动化技术抓取KOOK消息，这种方式可能违反KOOK平台的服务条款。使用本软件可能导致您的KOOK账号被限制或封禁。</p>
            </li>
            
            <li>
              <strong>使用授权</strong>
              <p>请仅在已获得相关平台和内容创作者明确授权的场景下使用本软件。未经授权的消息转发可能侵犯他人的知识产权和隐私权。</p>
            </li>
            
            <li>
              <strong>法律合规</strong>
              <p>您在使用本软件时，应当遵守中华人民共和国相关法律法规，包括但不限于《网络安全法》《个人信息保护法》《著作权法》等。</p>
            </li>
            
            <li>
              <strong>内容责任</strong>
              <p>转发的消息内容可能涉及版权、隐私、敏感信息等问题。您应当对转发的内容承担完全责任。</p>
            </li>
            
            <li>
              <strong>免责条款</strong>
              <p>本软件仅供学习、研究和合法授权场景使用。因使用本软件导致的任何直接或间接损失（包括但不限于账号被封、数据丢失、法律纠纷等），开发者不承担任何责任。</p>
            </li>
            
            <li>
              <strong>数据安全</strong>
              <p>本软件会在本地存储您的账号信息和配置数据。虽然我们使用加密技术保护敏感信息，但您仍应妥善保管您的设备和数据。</p>
            </li>
          </ol>
          
          <div class="disclaimer-notice">
            <p><strong>重要提示：</strong></p>
            <ul>
              <li>本软件不收集或上传任何用户数据到远程服务器</li>
              <li>所有数据均存储在本地设备</li>
              <li>建议仅在测试环境或已获授权的场景下使用</li>
              <li>商业使用需自行承担法律责任</li>
            </ul>
          </div>
        </div>
        
        <el-checkbox v-model="agreedDisclaimer" style="margin-top: 20px">
          <strong>我已仔细阅读并完全理解上述条款，自愿承担使用本软件的一切风险和责任</strong>
        </el-checkbox>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="rejectDisclaimer">拒绝并退出</el-button>
          <el-button
            type="primary"
            :disabled="!agreedDisclaimer"
            @click="acceptDisclaimer"
          >
            同意并继续
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import { useSystemStore } from './store/system'

const systemStore = useSystemStore()

// 免责声明
const disclaimerVisible = ref(false)
const agreedDisclaimer = ref(false)

onMounted(() => {
  // 检查是否已同意免责声明
  const disclaimerAccepted = localStorage.getItem('disclaimer_accepted')
  
  if (!disclaimerAccepted) {
    disclaimerVisible.value = true
  }
  
  // 初始化系统状态
  systemStore.fetchSystemStatus()
})

const acceptDisclaimer = () => {
  localStorage.setItem('disclaimer_accepted', 'true')
  localStorage.setItem('disclaimer_accepted_time', new Date().toISOString())
  disclaimerVisible.value = false
}

const rejectDisclaimer = () => {
  ElMessageBox.confirm(
    '拒绝免责声明将无法使用本软件，确定要退出吗？',
    '提示',
    {
      confirmButtonText: '确定退出',
      cancelButtonText: '返回阅读',
      type: 'warning',
    }
  ).then(() => {
    // 退出应用
    if (window.electronAPI && window.electronAPI.quit) {
      window.electronAPI.quit()
    } else {
      window.close()
    }
  }).catch(() => {
    // 取消，继续显示免责声明
  })
}
</script>

<style scoped>
.app-container {
  width: 100%;
  height: 100%;
}

.disclaimer-content {
  max-height: 500px;
  overflow-y: auto;
}

.disclaimer-text {
  font-size: 14px;
  line-height: 1.8;
  color: #606266;
}

.disclaimer-text h3 {
  margin-bottom: 15px;
  color: #303133;
  font-size: 16px;
}

.disclaimer-text ol {
  padding-left: 20px;
}

.disclaimer-text li {
  margin-bottom: 15px;
}

.disclaimer-text li strong {
  color: #E6A23C;
  font-size: 15px;
}

.disclaimer-text li p {
  margin: 5px 0;
  color: #606266;
}

.disclaimer-notice {
  margin-top: 20px;
  padding: 15px;
  background: #FEF0F0;
  border-left: 4px solid #F56C6C;
  border-radius: 4px;
}

.disclaimer-notice p {
  margin: 0 0 10px 0;
  font-weight: bold;
  color: #F56C6C;
}

.disclaimer-notice ul {
  margin: 0;
  padding-left: 20px;
}

.disclaimer-notice li {
  margin: 5px 0;
  color: #606266;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
