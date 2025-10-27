<template>
  <el-dialog
    v-model="visible"
    title="🍪 导入KOOK Cookie"
    width="700px"
    :close-on-click-modal="false"
    @closed="resetForm"
  >
    <!-- 导入方式选择 -->
    <el-radio-group v-model="importMethod" class="import-method-selector">
      <el-radio-button label="drag">
        <el-icon><Upload /></el-icon>
        拖拽上传
      </el-radio-button>
      <el-radio-button label="paste">
        <el-icon><DocumentCopy /></el-icon>
        粘贴文本
      </el-radio-button>
      <el-radio-button label="file">
        <el-icon><FolderOpened /></el-icon>
        选择文件
      </el-radio-button>
    </el-radio-group>

    <!-- 拖拽上传区域 -->
    <div
      v-if="importMethod === 'drag'"
      class="drag-upload-area"
      :class="{ 'is-dragover': isDragOver, 'has-file': cookieData }"
      @drop.prevent="handleDrop"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".txt,.json,.cookies"
        style="display: none"
        @change="handleFileSelect"
      />
      
      <div v-if="!cookieData" class="drag-placeholder">
        <div class="drag-icon-container">
          <el-icon :size="64" class="drag-icon">
            <UploadFilled />
          </el-icon>
          <div class="drag-animation-circle"></div>
        </div>
        <h3>拖拽Cookie文件到此处</h3>
        <p>或点击选择文件</p>
        <div class="supported-formats">
          <el-tag size="small" type="info">JSON格式</el-tag>
          <el-tag size="small" type="info">Netscape格式</el-tag>
          <el-tag size="small" type="info">TXT文本</el-tag>
        </div>
      </div>

      <div v-else class="file-info">
        <el-icon :size="48" color="#67C23A"><SuccessFilled /></el-icon>
        <h3>文件已加载</h3>
        <p>{{ fileName }}</p>
        <p class="file-size">{{ fileSize }}</p>
        <el-button size="small" @click.stop="clearFile">
          <el-icon><Delete /></el-icon>
          重新选择
        </el-button>
      </div>
    </div>

    <!-- 粘贴文本区域 -->
    <div v-if="importMethod === 'paste'" class="paste-area">
      <el-input
        v-model="cookieText"
        type="textarea"
        :rows="12"
        placeholder="请粘贴Cookie内容...
        
支持的格式：
1. JSON数组格式：[{&quot;name&quot;: &quot;xxx&quot;, &quot;value&quot;: &quot;xxx&quot;, ...}]
2. Netscape格式：.kookapp.cn  TRUE  /  FALSE  xxx  cookie_name  cookie_value
3. 请求头格式：Cookie: name1=value1; name2=value2; ..."
        class="cookie-textarea"
        @input="parseCookieText"
      />
      
      <div v-if="parseError" class="parse-error">
        <el-alert
          :title="parseError"
          type="error"
          :closable="false"
          show-icon
        />
      </div>
    </div>

    <!-- 选择文件 -->
    <div v-if="importMethod === 'file'" class="file-select-area">
      <el-button
        type="primary"
        size="large"
        @click="triggerFileInput"
      >
        <el-icon><FolderOpened /></el-icon>
        选择Cookie文件
      </el-button>
      <p class="file-hint">支持 .txt、.json、.cookies 格式</p>
      
      <div v-if="fileName" class="selected-file">
        <el-icon><Document /></el-icon>
        <span>{{ fileName }}</span>
        <el-button
          type="danger"
          size="small"
          text
          @click="clearFile"
        >
          <el-icon><Delete /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- Cookie预览 -->
    <el-collapse v-if="parsedCookies.length > 0" class="cookie-preview">
      <el-collapse-item>
        <template #title>
          <span class="preview-title">
            <el-icon><View /></el-icon>
            Cookie预览（{{parsedCookies.length}}条）
          </span>
        </template>
        <el-table
          :data="parsedCookies.slice(0, 10)"
          size="small"
          max-height="200"
          stripe
        >
          <el-table-column prop="name" label="名称" width="150" />
          <el-table-column prop="value" label="值" show-overflow-tooltip />
          <el-table-column prop="domain" label="域名" width="150" />
        </el-table>
        <div v-if="parsedCookies.length > 10" class="more-cookies">
          还有 {{ parsedCookies.length - 10 }} 条Cookie未显示...
        </div>
      </el-collapse-item>
    </el-collapse>

    <!-- 验证结果 -->
    <div v-if="validationResult" class="validation-result">
      <el-alert
        :type="validationResult.success ? 'success' : 'warning'"
        :closable="false"
        show-icon
      >
        <template #title>
          <span v-if="validationResult.success">
            ✅ Cookie验证成功！找到 {{ parsedCookies.length }} 条有效Cookie
          </span>
          <span v-else>
            ⚠️ {{ validationResult.message }}
          </span>
        </template>
        <div v-if="validationResult.details" class="validation-details">
          <ul>
            <li v-for="(detail, index) in validationResult.details" :key="index">
              {{ detail }}
            </li>
          </ul>
        </div>
      </el-alert>
    </div>

    <!-- 操作按钮 -->
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="close">取消</el-button>
        <el-button
          type="info"
          @click="showHelp"
        >
          <el-icon><QuestionFilled /></el-icon>
          如何获取Cookie？
        </el-button>
        <el-button
          type="primary"
          :disabled="!cookieData || parsedCookies.length === 0"
          :loading="importing"
          @click="importCookie"
        >
          <el-icon><Check /></el-icon>
          确认导入
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'imported'])

const router = useRouter()

// 状态
const importMethod = ref('drag') // drag, paste, file
const isDragOver = ref(false)
const cookieData = ref(null)
const cookieText = ref('')
const fileName = ref('')
const fileSize = ref('')
const parsedCookies = ref([])
const parseError = ref('')
const validationResult = ref(null)
const importing = ref(false)

const fileInput = ref(null)

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 拖拽处理
const handleDragOver = () => {
  isDragOver.value = true
}

const handleDragLeave = () => {
  isDragOver.value = false
}

const handleDrop = (event) => {
  isDragOver.value = false
  const files = event.dataTransfer.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

// 触发文件选择
const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

// 文件选择处理
const handleFileSelect = (event) => {
  const files = event.target.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

// 处理文件
const processFile = async (file) => {
  fileName.value = file.name
  fileSize.value = formatFileSize(file.size)
  
  try {
    const text = await file.text()
    cookieData.value = text
    await parseCookie(text)
  } catch (error) {
    ElMessage.error('文件读取失败：' + error.message)
  }
}

// 解析Cookie文本
const parseCookieText = () => {
  parseError.value = ''
  if (cookieText.value.trim()) {
    parseCookie(cookieText.value)
  } else {
    parsedCookies.value = []
  }
}

// 解析Cookie（支持多种格式）
const parseCookie = async (text) => {
  parseError.value = ''
  parsedCookies.value = []
  validationResult.value = null
  
  if (!text || !text.trim()) {
    return
  }

  try {
    // 尝试JSON格式
    if (text.trim().startsWith('[') || text.trim().startsWith('{')) {
      try {
        let cookies = JSON.parse(text)
        if (!Array.isArray(cookies)) {
          cookies = [cookies]
        }
        parsedCookies.value = cookies.map(c => ({
          name: c.name || '',
          value: c.value || '',
          domain: c.domain || '.kookapp.cn',
          path: c.path || '/',
          expires: c.expires || c.expirationDate,
          httpOnly: c.httpOnly !== undefined ? c.httpOnly : false,
          secure: c.secure !== undefined ? c.secure : true
        }))
        await validateCookies()
        return
      } catch (jsonError) {
        console.log('不是有效的JSON格式，尝试其他格式...')
      }
    }

    // 尝试Netscape格式
    if (text.includes('\t') || text.includes('# ')) {
      const lines = text.split('\n')
      const cookies = []
      for (const line of lines) {
        if (line.trim() && !line.startsWith('#')) {
          const parts = line.split('\t')
          if (parts.length >= 7) {
            cookies.push({
              domain: parts[0],
              path: parts[2],
              secure: parts[3] === 'TRUE',
              expires: parseInt(parts[4]),
              name: parts[5],
              value: parts[6]
            })
          }
        }
      }
      if (cookies.length > 0) {
        parsedCookies.value = cookies
        await validateCookies()
        return
      }
    }

    // 尝试请求头格式（Cookie: name1=value1; name2=value2）
    const cookieHeaderMatch = text.match(/Cookie:\s*(.+)/i)
    const cookieString = cookieHeaderMatch ? cookieHeaderMatch[1] : text
    
    if (cookieString.includes('=')) {
      const cookies = []
      const pairs = cookieString.split(';')
      for (const pair of pairs) {
        const [name, value] = pair.trim().split('=')
        if (name && value) {
          cookies.push({
            name: name.trim(),
            value: value.trim(),
            domain: '.kookapp.cn',
            path: '/',
            secure: true,
            httpOnly: false
          })
        }
      }
      if (cookies.length > 0) {
        parsedCookies.value = cookies
        await validateCookies()
        return
      }
    }

    // 所有格式都不匹配
    parseError.value = '无法识别Cookie格式。请确保使用支持的格式：JSON数组、Netscape或请求头格式'
    
  } catch (error) {
    console.error('解析Cookie失败:', error)
    parseError.value = '解析失败：' + error.message
  }
}

// 验证Cookie
const validateCookies = async () => {
  if (parsedCookies.value.length === 0) {
    validationResult.value = {
      success: false,
      message: 'Cookie为空'
    }
    return
  }

  // 检查必需的Cookie
  const requiredCookies = ['kook_token', 'session', 'user_id']
  const foundCookies = parsedCookies.value.map(c => c.name)
  const missingCookies = requiredCookies.filter(name => 
    !foundCookies.some(found => found.includes(name.toLowerCase()))
  )

  if (missingCookies.length > 0) {
    validationResult.value = {
      success: false,
      message: '可能缺少必需的Cookie',
      details: [
        `缺少: ${missingCookies.join(', ')}`,
        '这可能导致登录失败',
        '请确保从已登录的KOOK页面导出完整Cookie'
      ]
    }
  } else {
    validationResult.value = {
      success: true,
      message: 'Cookie看起来是有效的'
    }
  }
}

// 导入Cookie
const importCookie = async () => {
  if (parsedCookies.value.length === 0) {
    ElMessage.warning('请先导入有效的Cookie')
    return
  }

  try {
    importing.value = true
    
    // 调用API导入Cookie
    const response = await api.post('/api/cookie-import-enhanced/import', {
      cookies: parsedCookies.value,
      format: 'json'
    })

    if (response.success) {
      ElMessage.success('✅ Cookie导入成功！')
      emit('imported', response.data)
      close()
    } else {
      ElMessage.error('导入失败：' + (response.message || '未知错误'))
    }
  } catch (error) {
    console.error('导入Cookie失败:', error)
    ElMessage.error('导入失败：' + (error.response?.data?.detail || error.message))
  } finally {
    importing.value = false
  }
}

// 清除文件
const clearFile = () => {
  cookieData.value = null
  fileName.value = ''
  fileSize.value = ''
  parsedCookies.value = []
  parseError.value = ''
  validationResult.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 重置表单
const resetForm = () => {
  importMethod.value = 'drag'
  cookieText.value = ''
  clearFile()
}

// 关闭对话框
const close = () => {
  visible.value = false
}

// 显示帮助
const showHelp = () => {
  ElMessageBox.alert(
    `<h3>如何获取KOOK Cookie？</h3>
    <p><strong>方法一：使用浏览器插件（推荐）</strong></p>
    <ol>
      <li>安装"Cookie Editor"或"EditThisCookie"插件</li>
      <li>登录KOOK网页版</li>
      <li>点击插件图标，选择"导出"</li>
      <li>复制导出的JSON格式Cookie</li>
      <li>粘贴到本对话框</li>
    </ol>
    <p><strong>方法二：使用浏览器开发者工具</strong></p>
    <ol>
      <li>登录KOOK网页版</li>
      <li>按F12打开开发者工具</li>
      <li>切换到"Application"或"存储"标签</li>
      <li>展开"Cookies" → "https://www.kookapp.cn"</li>
      <li>复制所有Cookie（可使用工具导出）</li>
    </ol>
    <p><strong>注意事项：</strong></p>
    <ul>
      <li>Cookie包含敏感信息，请勿分享给他人</li>
      <li>Cookie有时效性，过期需要重新获取</li>
      <li>建议从无痕模式登录后导出，避免干扰</li>
    </ul>`,
    '获取Cookie教程',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '我知道了',
      type: 'info'
    }
  )
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}
</script>

<style scoped>
.import-method-selector {
  margin-bottom: 20px;
  width: 100%;
  display: flex;
}

.import-method-selector :deep(.el-radio-button) {
  flex: 1;
}

.import-method-selector :deep(.el-radio-button__inner) {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.drag-upload-area {
  min-height: 300px;
  border: 2px dashed #dcdfe6;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  position: relative;
  overflow: hidden;
}

.drag-upload-area:hover {
  border-color: #409eff;
  background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
}

.drag-upload-area.is-dragover {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #c6f6d5 100%);
  transform: scale(1.02);
}

.drag-upload-area.has-file {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #e1f3d8 100%);
}

.drag-placeholder {
  text-align: center;
  padding: 40px 20px;
}

.drag-icon-container {
  position: relative;
  display: inline-block;
  margin-bottom: 20px;
}

.drag-icon {
  color: #409eff;
  z-index: 1;
  position: relative;
}

.drag-animation-circle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  border: 3px solid #409eff;
  border-radius: 50%;
  opacity: 0.3;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.3;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.3);
    opacity: 0;
  }
}

.drag-upload-area:hover .drag-icon {
  animation: bounce 1s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.drag-placeholder h3 {
  font-size: 20px;
  color: #303133;
  margin: 0 0 10px 0;
}

.drag-placeholder p {
  font-size: 14px;
  color: #909399;
  margin: 0 0 20px 0;
}

.supported-formats {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.file-info {
  text-align: center;
  padding: 40px 20px;
}

.file-info h3 {
  font-size: 18px;
  color: #67c23a;
  margin: 16px 0 8px 0;
}

.file-info p {
  font-size: 14px;
  color: #606266;
  margin: 4px 0;
}

.file-size {
  color: #909399;
  font-size: 12px;
}

.paste-area {
  margin: 20px 0;
}

.cookie-textarea :deep(.el-textarea__inner) {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  line-height: 1.5;
}

.parse-error {
  margin-top: 12px;
}

.file-select-area {
  text-align: center;
  padding: 60px 20px;
}

.file-hint {
  margin-top: 12px;
  font-size: 13px;
  color: #909399;
}

.selected-file {
  margin-top: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.cookie-preview {
  margin: 20px 0;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
}

.preview-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.more-cookies {
  padding: 12px;
  text-align: center;
  color: #909399;
  font-size: 13px;
  background-color: #f5f7fa;
  border-top: 1px solid #e4e7ed;
}

.validation-result {
  margin: 20px 0;
}

.validation-details ul {
  margin: 12px 0 0 20px;
  padding: 0;
}

.validation-details li {
  font-size: 13px;
  line-height: 1.8;
  color: #606266;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}
</style>
