<template>
  <el-card class="step-card">
    <template #header>
      <div class="card-header">
        <h2>🔗 连接KOOK账号</h2>
        <p>通过Cookie快速导入，无需输入密码</p>
      </div>
    </template>

    <div class="step-content">
      <!-- Cookie导入方式选择 -->
      <el-radio-group v-model="importMethod" class="import-methods">
        <el-radio-button value="extension">
          🔌 Chrome扩展（推荐）
        </el-radio-button>
        <el-radio-button value="paste">
          📋 粘贴Cookie
        </el-radio-button>
        <el-radio-button value="file">
          📁 上传文件
        </el-radio-button>
      </el-radio-group>

      <!-- Chrome扩展方式 -->
      <div v-if="importMethod === 'extension'" class="import-section">
        <el-alert
          title="使用Chrome扩展一键导出Cookie"
          type="success"
          :closable="false"
          show-icon
        >
          <ol class="guide-steps">
            <li>安装Chrome扩展：KOOK Cookie导出工具</li>
            <li>访问 <a href="https://www.kookapp.cn/app" target="_blank">www.kookapp.cn</a> 并登录</li>
            <li>点击扩展图标，一键复制Cookie</li>
            <li>返回此页面，Cookie会自动填充</li>
          </ol>
        </el-alert>

        <div class="extension-actions">
          <el-button 
            type="primary" 
            size="large"
            @click="openExtensionStore"
          >
            <el-icon><Download /></el-icon>
            安装Chrome扩展
          </el-button>

          <el-button 
            size="large"
            @click="checkClipboard"
            :loading="checkingClipboard"
          >
            <el-icon><DocumentCopy /></el-icon>
            从剪贴板导入
          </el-button>
        </div>
      </div>

      <!-- 粘贴Cookie方式 -->
      <div v-else-if="importMethod === 'paste'" class="import-section">
        <el-input
          v-model="cookieInput"
          type="textarea"
          :rows="8"
          placeholder="请粘贴Cookie内容（支持多种格式自动识别）&#10;&#10;支持格式：&#10;1. JSON数组: [{'name':'token', 'value':'xxx'}]&#10;2. JSON对象: {'cookies': [...]}&#10;3. Netscape格式&#10;4. HTTP Header格式&#10;5. 键值对格式"
          @input="handleCookieInput"
        />

        <div v-if="cookieValidation.status" class="validation-result">
          <el-alert
            :title="cookieValidation.message"
            :type="cookieValidation.status"
            :closable="false"
            show-icon
          >
            <div v-if="cookieValidation.details">
              <p>Cookie数量: {{ cookieValidation.details.count }}</p>
              <p v-if="cookieValidation.details.expires">
                过期时间: {{ cookieValidation.details.expires }}
              </p>
            </div>
          </el-alert>
        </div>
      </div>

      <!-- 文件上传方式 -->
      <div v-else-if="importMethod === 'file'" class="import-section">
        <el-upload
          ref="uploadRef"
          class="cookie-upload"
          drag
          :auto-upload="false"
          :on-change="handleFileChange"
          :file-list="fileList"
          accept=".json,.txt"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处或 <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 .json 和 .txt 格式的Cookie文件
            </div>
          </template>
        </el-upload>
      </div>

      <!-- 账号预览 -->
      <transition name="fade">
        <div v-if="accountPreview" class="account-preview">
          <el-divider>账号预览</el-divider>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="邮箱">
              {{ accountPreview.email || '自动识别中...' }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="accountPreview.status === 'valid' ? 'success' : 'warning'">
                {{ accountPreview.status === 'valid' ? '有效' : '待验证' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Cookie数量">
              {{ accountPreview.cookieCount }}
            </el-descriptions-item>
            <el-descriptions-item label="域名">
              {{ accountPreview.domain }}
            </el-descriptions-item>
          </el-descriptions>

          <div v-if="accountPreview.warnings.length > 0" class="warnings">
            <el-alert
              v-for="(warning, index) in accountPreview.warnings"
              :key="index"
              :title="warning"
              type="warning"
              :closable="false"
              show-icon
            />
          </div>
        </div>
      </transition>
    </div>

    <!-- 底部操作 -->
    <template #footer>
      <div class="step-footer">
        <el-button size="large" @click="handlePrev">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>

        <el-button 
          type="primary" 
          size="large"
          :loading="connecting"
          :disabled="!cookieInput && !fileList.length"
          @click="handleConnect"
        >
          验证并连接
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </template>
  </el-card>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { 
  Download, 
  DocumentCopy, 
  UploadFilled, 
  ArrowLeft, 
  ArrowRight 
} from '@element-plus/icons-vue'
import api from '@/api'

const emit = defineEmits(['next', 'prev', 'update-data'])

const importMethod = ref('extension')
const cookieInput = ref('')
const fileList = ref([])
const uploadRef = ref(null)
const connecting = ref(false)
const checkingClipboard = ref(false)

const cookieValidation = reactive({
  status: null,
  message: '',
  details: null
})

const accountPreview = ref(null)

// 打开Chrome扩展商店
const openExtensionStore = () => {
  // 这里应该是实际的扩展商店链接
  const extensionUrl = 'chrome://extensions/'  // 临时链接
  window.open(extensionUrl, '_blank')
  
  ElNotification({
    title: '安装扩展',
    message: '安装完成后，请访问KOOK网站并使用扩展导出Cookie',
    type: 'info',
    duration: 5000
  })
}

// 从剪贴板检查Cookie
const checkClipboard = async () => {
  try {
    checkingClipboard.value = true
    
    const text = await navigator.clipboard.readText()
    
    if (text && text.trim()) {
      cookieInput.value = text
      await validateCookie(text)
      
      ElMessage.success('已从剪贴板导入Cookie')
    } else {
      ElMessage.warning('剪贴板为空，请先复制Cookie')
    }
  } catch (error) {
    ElMessage.error('无法读取剪贴板，请手动粘贴Cookie')
  } finally {
    checkingClipboard.value = false
  }
}

// 处理Cookie输入
const handleCookieInput = async (value) => {
  if (value && value.length > 20) {
    await validateCookie(value)
  } else {
    cookieValidation.status = null
    accountPreview.value = null
  }
}

// 验证Cookie
const validateCookie = async (cookieStr) => {
  try {
    const result = await api.post('/api/wizard/validate-cookie', {
      cookie: cookieStr
    })

    if (result.valid) {
      cookieValidation.status = 'success'
      cookieValidation.message = 'Cookie格式有效'
      cookieValidation.details = {
        count: result.count,
        expires: result.expires
      }

      accountPreview.value = {
        email: result.email || 'auto@kook.com',
        status: 'valid',
        cookieCount: result.count,
        domain: result.domain || 'kookapp.cn',
        warnings: result.warnings || []
      }
    } else {
      cookieValidation.status = 'error'
      cookieValidation.message = result.message || 'Cookie无效'
      accountPreview.value = null
    }
  } catch (error) {
    cookieValidation.status = 'error'
    cookieValidation.message = error.response?.data?.detail || 'Cookie验证失败'
    accountPreview.value = null
  }
}

// 处理文件上传
const handleFileChange = (file) => {
  const reader = new FileReader()
  
  reader.onload = (e) => {
    cookieInput.value = e.target.result
    validateCookie(e.target.result)
  }
  
  reader.readAsText(file.raw)
}

// 连接账号
const handleConnect = async () => {
  if (!cookieInput.value) {
    ElMessage.warning('请先导入Cookie')
    return
  }

  try {
    connecting.value = true

    // 快速配置：验证+创建账号+启动抓取器
    const result = await api.post('/api/wizard/smart/quick-setup', {
      cookie: cookieInput.value,
      target_platforms: ['discord'],  // 默认Discord
      auto_mapping: true,
      skip_testing: false
    })

    if (result.success) {
      ElNotification({
        title: '✅ 连接成功',
        message: `已找到 ${result.servers_found} 个服务器，${result.channels_found} 个频道`,
        type: 'success',
        duration: 3000
      })

      // 更新向导数据
      emit('update-data', {
        accountId: result.account_id,
        accounts: [{ id: result.account_id, status: 'online' }],
        servers: result.servers || [],
        selectedChannels: result.channels || []
      })

      // 进入下一步
      emit('next', {
        accountId: result.account_id
      })
    } else {
      throw new Error(result.message || '连接失败')
    }
  } catch (error) {
    ElMessage.error('连接失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    connecting.value = false
  }
}

const handlePrev = () => {
  emit('prev')
}
</script>

<style scoped>
.step-card {
  max-width: 900px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
}

.card-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.card-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.step-content {
  padding: 20px 0;
}

.import-methods {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.import-methods .el-radio-button {
  flex: 1;
}

.import-section {
  margin-top: 20px;
}

.guide-steps {
  margin: 10px 0 0 20px;
  padding: 0;
}

.guide-steps li {
  margin: 8px 0;
  color: #606266;
}

.guide-steps a {
  color: #409EFF;
  text-decoration: none;
}

.extension-actions {
  display: flex;
  gap: 15px;
  margin-top: 20px;
  justify-content: center;
}

.validation-result {
  margin-top: 15px;
}

.cookie-upload {
  margin-top: 20px;
}

.account-preview {
  margin-top: 30px;
}

.warnings {
  margin-top: 15px;
}

.warnings .el-alert {
  margin-bottom: 10px;
}

.step-footer {
  display: flex;
  justify-content: space-between;
  padding: 20px 0 0 0;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
