<template>
  <div class="cookie-import-enhanced">
    <!-- 大文件拖拽区域 -->
    <div
      class="cookie-dropzone"
      :class="{ 'is-dragover': isDragover, 'is-success': uploadSuccess }"
      @dragover.prevent="handleDragover"
      @dragleave="handleDragleave"
      @drop.prevent="handleDrop"
      @click="selectFile"
    >
      <transition name="fade" mode="out-in">
        <!-- 初始状态 -->
        <div v-if="!uploading && !uploadSuccess" key="initial" class="dropzone-content">
          <el-icon class="upload-icon" :size="100">
            <Upload />
          </el-icon>
          <div class="upload-text">
            <p class="primary-text">拖拽Cookie文件到此处</p>
            <p class="secondary-text">
              或点击选择文件
              <el-button text type="primary" style="padding: 0 5px">浏览...</el-button>
            </p>
            <p class="hint-text">
              支持格式：JSON / Netscape / 浏览器复制文本
            </p>
          </div>
          
          <!-- 支持格式图标 -->
          <div class="format-icons">
            <el-tag size="small" type="info">JSON</el-tag>
            <el-tag size="small" type="info">TXT</el-tag>
            <el-tag size="small" type="info">浏览器复制</el-tag>
          </div>
        </div>
        
        <!-- 上传中 -->
        <div v-else-if="uploading" key="uploading" class="dropzone-content">
          <el-icon class="upload-icon spin" :size="100">
            <Loading />
          </el-icon>
          <p class="primary-text">正在解析Cookie...</p>
          <el-progress
            :percentage="uploadProgress"
            :stroke-width="8"
            style="width: 80%; margin-top: 20px"
          />
        </div>
        
        <!-- 成功状态 -->
        <div v-else-if="uploadSuccess" key="success" class="dropzone-content success-content">
          <el-icon class="success-icon bounce" :size="100" color="#67C23A">
            <CircleCheck />
          </el-icon>
          <p class="success-text">Cookie导入成功！</p>
          <p class="success-details">
            共 {{ cookieCount }} 条Cookie，已成功解析
          </p>
          <el-button
            type="primary"
            @click="resetUpload"
            style="margin-top: 20px"
          >
            导入其他Cookie
          </el-button>
        </div>
      </transition>
    </div>
    
    <!-- 隐藏的文件输入 -->
    <input
      ref="fileInput"
      type="file"
      accept=".json,.txt,.cookies"
      style="display: none"
      @change="handleFileSelect"
    />
    
    <!-- 或者直接粘贴 -->
    <el-divider>或</el-divider>
    
    <el-input
      v-model="cookieText"
      type="textarea"
      :rows="6"
      placeholder="直接粘贴Cookie文本到这里..."
      :disabled="uploading"
    />
    
    <div class="action-buttons">
      <el-button
        type="primary"
        :loading="uploading"
        :disabled="!cookieText"
        @click="handlePasteImport"
      >
        导入粘贴的Cookie
      </el-button>
      
      <el-button @click="openChromeExtension">
        使用Chrome扩展一键导出
      </el-button>
    </div>
    
    <!-- 帮助链接 -->
    <div class="help-links">
      <el-link type="primary" @click="showTutorial('cookie-guide')">
        <el-icon><QuestionFilled /></el-icon>
        如何获取Cookie？
      </el-link>
      <el-link type="primary" @click="showTutorial('video')">
        <el-icon><VideoPlay /></el-icon>
        观看视频教程
      </el-link>
    </div>
    
    <!-- 错误提示对话框 -->
    <el-dialog
      v-model="showError"
      title="Cookie导入失败"
      width="500px"
    >
      <el-result
        icon="error"
        :title="errorInfo.title"
        :sub-title="errorInfo.message"
      >
        <template #extra>
          <div class="error-solutions">
            <p class="solutions-title">💡 解决方案：</p>
            <ul>
              <li v-for="(solution, index) in errorInfo.solutions" :key="index">
                {{ solution }}
              </li>
            </ul>
          </div>
        </template>
      </el-result>
      
      <template #footer>
        <el-button @click="showError = false">关闭</el-button>
        <el-button
          v-if="errorInfo.action"
          type="primary"
          @click="handleErrorAction"
        >
          {{ errorInfo.action.text }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload,
  Loading,
  CircleCheck,
  QuestionFilled,
  VideoPlay,
} from '@element-plus/icons-vue'
import api from '@/api'

const emit = defineEmits(['success'])

const isDragover = ref(false)
const uploading = ref(false)
const uploadSuccess = ref(false)
const uploadProgress = ref(0)
const cookieCount = ref(0)
const cookieText = ref('')
const fileInput = ref(null)

const showError = ref(false)
const errorInfo = ref({
  title: '',
  message: '',
  solutions: [],
  action: null,
})

const handleDragover = (e) => {
  isDragover.value = true
}

const handleDragleave = (e) => {
  isDragover.value = false
}

const handleDrop = async (e) => {
  isDragover.value = false
  
  const files = e.dataTransfer.files
  if (files.length > 0) {
    await processFile(files[0])
  }
}

const selectFile = () => {
  fileInput.value?.click()
}

const handleFileSelect = async (e) => {
  const files = e.target.files
  if (files.length > 0) {
    await processFile(files[0])
  }
}

const processFile = async (file) => {
  try {
    uploading.value = true
    uploadProgress.value = 0
    
    // 读取文件
    const text = await file.text()
    uploadProgress.value = 30
    
    // 解析Cookie
    await importCookie(text)
    
  } catch (error) {
    handleImportError(error)
  } finally {
    uploading.value = false
  }
}

const handlePasteImport = async () => {
  try {
    uploading.value = true
    await importCookie(cookieText.value)
  } catch (error) {
    handleImportError(error)
  } finally {
    uploading.value = false
  }
}

const importCookie = async (cookieData) => {
  try {
    uploadProgress.value = 50
    
    // 调用API导入
    const response = await api.importCookie({
      cookie: cookieData,
      auto_parse: true,
    })
    
    uploadProgress.value = 100
    
    // 成功
    uploadSuccess.value = true
    cookieCount.value = response.cookie_count || 0
    
    ElMessage.success('Cookie导入成功！')
    
    // 通知父组件
    emit('success', response)
    
  } catch (error) {
    throw error
  }
}

const handleImportError = (error) => {
  const errorType = error.response?.data?.error_type || 'unknown'
  
  const errorMessages = {
    invalid_format: {
      title: '❌ Cookie格式错误',
      message: 'Cookie格式不正确，请检查',
      solutions: [
        '确保复制了完整的Cookie（不要漏掉任何字符）',
        '如果是JSON格式，确保是有效的JSON',
        '推荐使用Chrome扩展一键导出',
      ],
      action: {
        text: '查看Cookie获取教程',
        callback: () => showTutorial('cookie-guide'),
      },
    },
    expired: {
      title: '⚠️ Cookie已过期',
      message: '您导入的Cookie已失效',
      solutions: [
        '请重新登录KOOK获取新Cookie',
        '使用账号密码登录（推荐）',
      ],
      action: {
        text: '切换到账号密码登录',
        callback: () => emit('switch-to-password'),
      },
    },
    invalid_domain: {
      title: '⚠️ Cookie域名错误',
      message: '这不是KOOK的Cookie',
      solutions: [
        '确保Cookie来自 kookapp.cn 或 kaiheila.cn',
        '不要复制其他网站的Cookie',
      ],
    },
    network_error: {
      title: '🌐 网络错误',
      message: '无法连接到服务器',
      solutions: [
        '检查网络连接',
        '确保后端服务正在运行',
        '尝试重启应用',
      ],
    },
  }
  
  errorInfo.value = errorMessages[errorType] || {
    title: '❌ 导入失败',
    message: error.message || '未知错误',
    solutions: ['请检查Cookie格式', '或联系技术支持'],
  }
  
  showError.value = true
}

const handleErrorAction = () => {
  showError.value = false
  if (errorInfo.value.action?.callback) {
    errorInfo.value.action.callback()
  }
}

const resetUpload = () => {
  uploadSuccess.value = false
  cookieText.value = ''
  uploadProgress.value = 0
}

const openChromeExtension = () => {
  ElMessageBox.confirm(
    '使用Chrome扩展可以快速导出Cookie。是否要打开扩展安装页面？',
    '使用Chrome扩展',
    {
      confirmButtonText: '打开扩展页面',
      cancelButtonText: '取消',
      type: 'info',
    }
  ).then(() => {
    // 打开Chrome扩展页面
    window.open('chrome-extension://...', '_blank')
  })
}

const showTutorial = (type) => {
  // 打开教程
  emit('show-tutorial', type)
}
</script>

<style scoped>
.cookie-import-enhanced {
  padding: 20px;
}

.cookie-dropzone {
  border: 3px dashed #d9d9d9;
  border-radius: 12px;
  padding: 60px 40px;
  text-align: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
  position: relative;
  overflow: hidden;
}

.cookie-dropzone::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 50% 50%, rgba(64, 158, 255, 0.05) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s;
}

.cookie-dropzone:hover {
  border-color: #409EFF;
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.cookie-dropzone:hover::before {
  opacity: 1;
}

.cookie-dropzone.is-dragover {
  border-color: #409EFF;
  background: linear-gradient(135deg, #ecf5ff 0%, #e1f0ff 100%);
  transform: scale(1.02);
  box-shadow: 0 12px 24px rgba(64, 158, 255, 0.2);
}

.cookie-dropzone.is-success {
  border-color: #67C23A;
  background: linear-gradient(135deg, #f0f9ff 0%, #e8f8f5 100%);
}

.dropzone-content {
  position: relative;
  z-index: 1;
}

.upload-icon {
  color: #909399;
  transition: all 0.3s;
}

.cookie-dropzone:hover .upload-icon {
  color: #409EFF;
  transform: scale(1.1);
}

.spin {
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.upload-text {
  margin-top: 20px;
}

.primary-text {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 10px 0;
}

.secondary-text {
  font-size: 14px;
  color: #606266;
  margin: 0 0 5px 0;
}

.hint-text {
  font-size: 12px;
  color: #909399;
  margin: 0;
}

.format-icons {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
}

.success-content {
  animation: successBounce 0.6s ease-out;
}

@keyframes successBounce {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.bounce {
  animation: bounce 0.6s ease;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.success-text {
  font-size: 20px;
  font-weight: 600;
  color: #67C23A;
  margin: 15px 0 5px 0;
}

.success-details {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
}

.help-links {
  margin-top: 15px;
  display: flex;
  gap: 20px;
  justify-content: center;
}

.error-solutions {
  text-align: left;
  margin-top: 20px;
}

.solutions-title {
  font-weight: 600;
  margin-bottom: 10px;
  color: #303133;
}

.error-solutions ul {
  padding-left: 20px;
  margin: 0;
}

.error-solutions li {
  margin-bottom: 8px;
  color: #606266;
  line-height: 1.6;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from {
  opacity: 0;
  transform: scale(0.9);
}

.fade-leave-to {
  opacity: 0;
  transform: scale(1.1);
}
</style>
