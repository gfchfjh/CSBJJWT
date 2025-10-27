<template>
  <div class="cookie-import-enhanced">
    <!-- ✅ P0-3优化: Cookie拖拽导入增强组件 -->
    
    <!-- 300px大型拖拽区域 -->
    <div 
      class="cookie-drop-zone"
      :class="{ 
        'is-dragover': isDragover,
        'has-cookies': parsedCookies.length > 0 
      }"
      @drop="handleDrop"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @click="triggerFileSelect"
    >
      <!-- 拖拽指示器 -->
      <div class="drop-indicator">
        <div class="pulse-circle">
          <el-icon :size="80" color="#409EFF">
            <Upload />
          </el-icon>
        </div>
        
        <h2 class="drop-title">拖拽Cookie文件到此处</h2>
        <p class="drop-subtitle">或点击此处选择文件</p>
        
        <!-- 支持的格式 -->
        <div class="supported-formats">
          <el-tag type="info">JSON</el-tag>
          <el-tag type="success">Netscape</el-tag>
          <el-tag type="warning">Header String</el-tag>
        </div>
      </div>

      <!-- 隐藏的文件输入 -->
      <input 
        ref="fileInput" 
        type="file" 
        accept=".json,.txt,.cookies" 
        style="display: none"
        @change="handleFileSelect"
        multiple
      />
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button 
        type="primary" 
        @click="triggerFileSelect"
        size="large"
      >
        <el-icon><FolderOpened /></el-icon>
        选择文件
      </el-button>

      <el-button 
        @click="showPasteDialog"
        size="large"
      >
        <el-icon><Document /></el-icon>
        粘贴Cookie文本
      </el-button>

      <el-button 
        @click="showFormatHelp"
        size="large"
      >
        <el-icon><QuestionFilled /></el-icon>
        格式说明
      </el-button>
    </div>

    <!-- Cookie实时预览（表格形式） -->
    <el-collapse v-if="parsedCookies.length > 0" v-model="activePreview" class="cookie-preview-section">
      <el-collapse-item name="1">
        <template #title>
          <div class="preview-title">
            <el-icon color="#67C23A"><SuccessFilled /></el-icon>
            <span>✅ 成功解析 {{ parsedCookies.length }} 条Cookie</span>
            <el-tag type="success" size="small">有效</el-tag>
          </div>
        </template>

        <!-- Cookie验证结果 -->
        <el-alert 
          v-if="validationResult"
          :type="validationResult.isValid ? 'success' : 'warning'"
          :closable="false"
          show-icon
          style="margin-bottom: 15px;"
        >
          <template #title>
            {{ validationResult.isValid ? '✅ Cookie验证通过' : '⚠️ Cookie可能不完整' }}
          </template>
          <div v-if="!validationResult.isValid">
            <p>缺少以下必需字段：</p>
            <ul>
              <li v-for="field in validationResult.missing" :key="field">
                • {{ field }}
              </li>
            </ul>
            <p class="warning-tip">💡 提示：建议重新获取完整的Cookie</p>
          </div>
          <div v-else>
            <p>包含所有必需的认证信息，可以正常使用</p>
          </div>
        </el-alert>

        <!-- Cookie表格 -->
        <el-table 
          :data="displayedCookies" 
          border 
          size="small"
          max-height="400"
          style="width: 100%"
        >
          <el-table-column type="index" label="#" width="50" />
          
          <el-table-column prop="name" label="名称" width="180">
            <template #default="{ row }">
              <el-tag 
                :type="isImportantCookie(row.name) ? 'danger' : 'info'"
                size="small"
              >
                {{ row.name }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="value" label="值" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="cookie-value">{{ maskValue(row.value) }}</span>
              <el-button 
                link 
                type="primary" 
                size="small"
                @click="copyValue(row.value)"
              >
                <el-icon><CopyDocument /></el-icon>
              </el-button>
            </template>
          </el-table-column>

          <el-table-column prop="domain" label="域名" width="180" />

          <el-table-column label="过期时间" width="150">
            <template #default="{ row }">
              <span v-if="row.expires">
                {{ formatExpireTime(row.expires) }}
              </span>
              <el-tag v-else type="info" size="small">会话</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="secure" label="安全" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.secure ? 'success' : 'info'" size="small">
                {{ row.secure ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <!-- 显示更多 -->
        <div v-if="parsedCookies.length > displayLimit" class="show-more">
          <el-button 
            link 
            type="primary"
            @click="displayLimit = parsedCookies.length"
          >
            显示全部 {{ parsedCookies.length }} 条Cookie
          </el-button>
        </div>

        <!-- 操作按钮 -->
        <div class="preview-actions">
          <el-button 
            type="success" 
            @click="importCookies"
            :loading="isImporting"
          >
            <el-icon><Check /></el-icon>
            导入这些Cookie
          </el-button>

          <el-button @click="clearCookies">
            <el-icon><Delete /></el-icon>
            清空
          </el-button>

          <el-button @click="exportCookies">
            <el-icon><Download /></el-icon>
            导出为JSON
          </el-button>
        </div>
      </el-collapse-item>
    </el-collapse>

    <!-- 帮助链接 -->
    <div class="help-links">
      <el-link 
        type="primary" 
        @click="openTutorial('cookie-get')"
      >
        <el-icon><Reading /></el-icon>
        如何获取Cookie？查看图文教程
      </el-link>

      <el-link 
        type="success" 
        @click="openVideoTutorial"
      >
        <el-icon><VideoPlay /></el-icon>
        观看视频教程（3分钟）
      </el-link>

      <el-link 
        type="warning" 
        href="https://chrome.google.com/webstore/detail/cookie-editor/..." 
        target="_blank"
      >
        <el-icon><ChromeFilled /></el-icon>
        安装Chrome扩展（推荐）
      </el-link>
    </div>

    <!-- 粘贴Cookie对话框 -->
    <el-dialog 
      v-model="showPaste" 
      title="粘贴Cookie内容" 
      width="700px"
    >
      <el-input
        v-model="pasteText"
        type="textarea"
        :rows="12"
        placeholder="请粘贴Cookie内容，支持以下格式：&#10;&#10;1. JSON格式（从开发者工具导出）&#10;2. Netscape格式（EditThisCookie等扩展导出）&#10;3. Header String格式（直接复制Request Headers）&#10;&#10;示例：&#10;[{&quot;name&quot;: &quot;token&quot;, &quot;value&quot;: &quot;xxx&quot;, ...}]"
        @paste="handlePaste"
      />

      <el-alert 
        type="info" 
        :closable="false"
        show-icon
        style="margin-top: 15px;"
      >
        <template #title>
          💡 提示
        </template>
        <ul style="margin: 5px 0 0 15px; line-height: 1.6;">
          <li>支持直接粘贴，会自动识别格式</li>
          <li>如果是JSON，请确保是数组格式</li>
          <li>Header格式会自动转换</li>
        </ul>
      </el-alert>

      <template #footer>
        <el-button @click="showPaste = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="parsePastedCookie"
          :disabled="!pasteText.trim()"
        >
          <el-icon><Check /></el-icon>
          解析并预览
        </el-button>
      </template>
    </el-dialog>

    <!-- 格式说明对话框 -->
    <el-dialog 
      v-model="showFormatHelpDialog" 
      title="支持的Cookie格式" 
      width="800px"
    >
      <el-tabs>
        <el-tab-pane label="JSON格式">
          <el-alert type="success" :closable="false" show-icon>
            <template #title>最推荐的格式</template>
            从Chrome开发者工具 → Application → Cookies 导出
          </el-alert>

          <h4>示例：</h4>
          <pre class="format-example">{{ jsonExample }}</pre>

          <h4>如何获取：</h4>
          <ol>
            <li>按F12打开开发者工具</li>
            <li>切换到 Application 标签</li>
            <li>左侧找到 Cookies → https://www.kookapp.cn</li>
            <li>使用扩展导出为JSON</li>
          </ol>
        </el-tab-pane>

        <el-tab-pane label="Netscape格式">
          <el-alert type="info" :closable="false" show-icon>
            EditThisCookie等扩展的导出格式
          </el-alert>

          <h4>示例：</h4>
          <pre class="format-example">{{ netscapeExample }}</pre>
        </el-tab-pane>

        <el-tab-pane label="Header String格式">
          <el-alert type="warning" :closable="false" show-icon>
            直接复制请求头的Cookie字段
          </el-alert>

          <h4>示例：</h4>
          <pre class="format-example">{{ headerExample }}</pre>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button type="primary" @click="showFormatHelpDialog = false">
          我知道了
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, defineEmits, defineProps } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload, FolderOpened, Document, QuestionFilled, SuccessFilled,
  CopyDocument, Check, Delete, Download, Reading, VideoPlay,
  ChromeFilled
} from '@element-plus/icons-vue'
import api from '@/api'

const props = defineProps({
  accountId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['success', 'error'])

// 拖拽状态
const isDragover = ref(false)
const fileInput = ref(null)

// Cookie数据
const parsedCookies = ref([])
const activePreview = ref(['1'])
const displayLimit = ref(20)
const validationResult = ref(null)

// 对话框状态
const showPaste = ref(false)
const pasteText = ref('')
const showFormatHelpDialog = ref(false)

// 导入状态
const isImporting = ref(false)

// 格式示例
const jsonExample = ref(`[
  {
    "name": "token",
    "value": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "domain": ".kookapp.cn",
    "path": "/",
    "expires": 1735660800,
    "httpOnly": true,
    "secure": true,
    "sameSite": "Lax"
  },
  {
    "name": "session_id",
    "value": "abc123def456...",
    "domain": ".kookapp.cn",
    "path": "/",
    "secure": true
  }
]`)

const netscapeExample = ref(`# Netscape HTTP Cookie File
.kookapp.cn	TRUE	/	TRUE	1735660800	token	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
.kookapp.cn	TRUE	/	FALSE	0	session_id	abc123def456...`)

const headerExample = ref(`token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...; session_id=abc123def456...; user_id=12345; lang=zh-CN`)

// 显示的Cookie（限制数量）
const displayedCookies = computed(() => {
  return parsedCookies.value.slice(0, displayLimit.value)
})

// 重要Cookie列表（用于高亮）
const importantCookieNames = ['token', 'access_token', 'session_id', 'auth', 'jwt']

const isImportantCookie = (name) => {
  return importantCookieNames.some(keyword => 
    name.toLowerCase().includes(keyword.toLowerCase())
  )
}

// 拖拽处理
const handleDragOver = (e) => {
  e.preventDefault()
  isDragover.value = true
}

const handleDragLeave = () => {
  isDragover.value = false
}

const handleDrop = (e) => {
  e.preventDefault()
  isDragover.value = false
  
  const files = e.dataTransfer.files
  if (files.length > 0) {
    handleFiles(files)
  }
}

// 文件选择
const triggerFileSelect = () => {
  fileInput.value.click()
}

const handleFileSelect = (e) => {
  const files = e.target.files
  if (files.length > 0) {
    handleFiles(files)
  }
}

// 处理文件
const handleFiles = async (files) => {
  const allCookies = []
  
  for (let file of files) {
    try {
      const text = await file.text()
      const cookies = await parseCookieText(text)
      allCookies.push(...cookies)
    } catch (error) {
      ElMessage.error(`文件 ${file.name} 解析失败: ${error.message}`)
    }
  }
  
  if (allCookies.length > 0) {
    parsedCookies.value = allCookies
    await validateCookies(allCookies)
    ElMessage.success(`✅ 成功解析 ${allCookies.length} 条Cookie`)
  }
}

// 粘贴处理
const handlePaste = (e) => {
  // 粘贴时自动解析
  setTimeout(() => {
    if (pasteText.value.trim()) {
      // 自动识别格式提示
      let format = 'JSON'
      if (pasteText.value.includes('# Netscape')) {
        format = 'Netscape'
      } else if (!pasteText.value.trim().startsWith('[') && !pasteText.value.trim().startsWith('{')) {
        format = 'Header String'
      }
      
      ElMessage.info(`检测到 ${format} 格式`)
    }
  }, 100)
}

const showPasteDialog = () => {
  pasteText.value = ''
  showPaste.value = true
}

const parsePastedCookie = async () => {
  if (!pasteText.value.trim()) {
    ElMessage.warning('请粘贴Cookie内容')
    return
  }
  
  try {
    const cookies = await parseCookieText(pasteText.value)
    parsedCookies.value = cookies
    await validateCookies(cookies)
    showPaste.value = false
    ElMessage.success(`✅ 成功解析 ${cookies.length} 条Cookie`)
  } catch (error) {
    ElMessage.error('Cookie解析失败: ' + error.message)
  }
}

// 解析Cookie文本
const parseCookieText = async (text) => {
  try {
    // 调用后端API解析（支持多种格式）
    const response = await api.post('/api/cookie-import-enhanced/parse', {
      cookie: text
    })
    
    if (response.data.success) {
      return response.data.cookies
    } else {
      throw new Error(response.data.message || 'Cookie解析失败')
    }
  } catch (error) {
    throw new Error(error.response?.data?.message || error.message)
  }
}

// 验证Cookie
const validateCookies = async (cookies) => {
  try {
    const response = await api.post('/api/cookie-import-enhanced/validate', {
      cookies: cookies
    })
    
    validationResult.value = response.data
  } catch (error) {
    console.error('Cookie验证失败:', error)
  }
}

// 值脱敏显示
const maskValue = (value) => {
  if (!value || value.length < 10) return value
  return value.substring(0, 8) + '***' + value.substring(value.length - 8)
}

// 复制值
const copyValue = (value) => {
  navigator.clipboard.writeText(value).then(() => {
    ElMessage.success('已复制到剪贴板')
  })
}

// 格式化过期时间
const formatExpireTime = (expires) => {
  if (!expires) return '-'
  
  const date = typeof expires === 'number' 
    ? new Date(expires * 1000) 
    : new Date(expires)
  
  const now = new Date()
  const diff = date - now
  
  if (diff < 0) {
    return '已过期'
  }
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  return days > 0 ? `${days}天后` : '今天'
}

// 清空Cookie
const clearCookies = () => {
  ElMessageBox.confirm('确定要清空已解析的Cookie吗？', '确认清空', {
    type: 'warning'
  }).then(() => {
    parsedCookies.value = []
    validationResult.value = null
    ElMessage.success('已清空')
  }).catch(() => {})
}

// 导入Cookie
const importCookies = async () => {
  if (parsedCookies.value.length === 0) {
    ElMessage.warning('没有可导入的Cookie')
    return
  }
  
  isImporting.value = true
  
  try {
    const response = await api.post('/api/accounts/add', {
      cookie: JSON.stringify(parsedCookies.value),
      login_method: 'cookie'
    })
    
    if (response.data.success) {
      ElMessage.success('✅ Cookie导入成功！')
      emit('success', response.data)
      
      // 清空已导入的Cookie
      parsedCookies.value = []
      validationResult.value = null
    } else {
      ElMessage.error('导入失败: ' + response.data.message)
      emit('error', response.data)
    }
  } catch (error) {
    ElMessage.error('导入失败: ' + error.message)
    emit('error', error)
  } finally {
    isImporting.value = false
  }
}

// 导出Cookie为JSON
const exportCookies = () => {
  const json = JSON.stringify(parsedCookies.value, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `cookies_${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('Cookie已导出')
}

// 打开教程
const openTutorial = (topic) => {
  window.open(`/help?topic=${topic}`, '_blank')
}

const openVideoTutorial = () => {
  window.open('/help/videos?id=cookie-import', '_blank')
}

// 显示格式帮助
const showFormatHelp = () => {
  showFormatHelpDialog.value = true
}
</script>

<style scoped lang="scss">
.cookie-import-enhanced {
  width: 100%;
}

/* 拖拽区域 */
.cookie-drop-zone {
  border: 3px dashed #DCDFE6;
  border-radius: 16px;
  padding: 60px 40px;
  text-align: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e3e8ef 100%);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(64, 158, 255, 0.1);
    transform: translate(-50%, -50%);
    transition: all 0.6s;
  }
  
  &:hover {
    border-color: #409EFF;
    background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(64, 158, 255, 0.2);
    
    &::before {
      width: 500px;
      height: 500px;
    }
    
    .pulse-circle {
      animation: pulse 2s infinite;
    }
  }
  
  &.is-dragover {
    border-color: #67C23A;
    background: linear-gradient(135deg, #f0f9ff 0%, #e1f3d8 100%);
    transform: scale(1.02);
    box-shadow: 0 12px 32px rgba(103, 194, 58, 0.3);
    animation: shake 0.5s;
    
    .drop-indicator {
      animation: bounce 0.6s;
    }
  }
  
  &.has-cookies {
    border-color: #67C23A;
    background: linear-gradient(135deg, #f0f9ff 0%, #e1f3d8 100%);
  }
}

.drop-indicator {
  position: relative;
  z-index: 1;
}

.pulse-circle {
  display: inline-block;
  animation: float 3s ease-in-out infinite;
}

.drop-title {
  font-size: 28px;
  margin: 30px 0 15px;
  color: #303133;
  font-weight: 600;
}

.drop-subtitle {
  font-size: 16px;
  color: #909399;
  margin-bottom: 25px;
}

.supported-formats {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin: 30px 0;
  flex-wrap: wrap;
}

/* Cookie预览 */
.cookie-preview-section {
  margin: 30px 0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.preview-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
}

.cookie-value {
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 12px;
  color: #606266;
}

.warning-tip {
  margin-top: 10px;
  font-weight: 600;
  color: #E6A23C;
}

.show-more {
  text-align: center;
  padding: 15px;
  border-top: 1px solid #EBEEF5;
}

.preview-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}

/* 帮助链接 */
.help-links {
  display: flex;
  gap: 30px;
  justify-content: center;
  margin-top: 30px;
  flex-wrap: wrap;
}

/* 格式示例 */
.format-example {
  background: #F5F7FA;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
  overflow-x: auto;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  margin: 15px 0;
}

/* 动画 */
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}
</style>
