<template>
  <div class="cookie-import-container">
    <!-- 300px超大拖拽区 -->
    <div
      class="drag-drop-zone-ultra"
      :class="{ 'is-dragging': isDragging, 'has-cookies': parsedCookies.length > 0 }"
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @click="selectFile"
    >
      <div class="drag-icon-pulse">
        <el-icon :size="80"><Upload /></el-icon>
      </div>
      <h2>拖拽Cookie文件到此</h2>
      <p class="format-hint">支持 .json / .txt / .cookies 格式</p>
      
      <el-divider>或</el-divider>
      
      <div class="action-buttons">
        <el-button type="primary" size="large" @click.stop="selectFile">
          <el-icon><FolderOpened /></el-icon>
          选择文件
        </el-button>
        <el-button size="large" @click.stop="showPasteDialog">
          <el-icon><Document /></el-icon>
          粘贴文本
        </el-button>
      </div>
      
      <!-- 隐藏的文件输入 -->
      <input
        ref="fileInputRef"
        type="file"
        accept=".json,.txt,.cookies"
        style="display: none"
        @change="handleFileSelect"
      />
    </div>
    
    <!-- Cookie预览表格（导入后显示） -->
    <el-card v-if="parsedCookies.length > 0" class="cookie-preview-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>
            <el-icon><List /></el-icon>
            Cookie预览（共 {{ parsedCookies.length }} 条）
          </span>
          <el-button size="small" text @click="clearCookies">
            <el-icon><Delete /></el-icon>
            清除
          </el-button>
        </div>
      </template>
      
      <el-table
        :data="paginatedCookies"
        max-height="300"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="name" label="名称" width="150" show-overflow-tooltip />
        <el-table-column prop="value" label="值" show-overflow-tooltip>
          <template #default="{ row }">
            <el-text truncated>{{ maskValue(row.value) }}</el-text>
          </template>
        </el-table-column>
        <el-table-column prop="domain" label="域名" width="150" />
        <el-table-column label="过期时间" width="180">
          <template #default="{ row }">
            {{ row.expires ? formatDate(row.expires) : '会话Cookie' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getStatusType(row.expires)"
              size="small"
            >
              {{ getStatusText(row.expires) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-if="parsedCookies.length > pageSize"
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="parsedCookies.length"
        layout="prev, pager, next"
        class="pagination"
      />
    </el-card>
    
    <!-- 智能验证结果 -->
    <el-alert
      v-if="validationResult.type"
      :type="validationResult.type"
      :title="validationResult.title"
      :closable="false"
      show-icon
      class="validation-alert"
    >
      <template v-if="validationResult.description">
        {{ validationResult.description }}
      </template>
      <template v-if="validationResult.missing_fields && validationResult.missing_fields.length > 0">
        <p>缺少必需字段：</p>
        <ul>
          <li v-for="field in validationResult.missing_fields" :key="field">
            {{ field }}
          </li>
        </ul>
      </template>
    </el-alert>
    
    <!-- 帮助链接 -->
    <div class="help-section">
      <el-divider />
      <el-link type="primary" :underline="false" @click="showCookieHelp">
        <el-icon><QuestionFilled /></el-icon>
        如何获取KOOK Cookie？（3种方法图文教程）
      </el-link>
    </div>
    
    <!-- 粘贴对话框 -->
    <el-dialog
      v-model="pasteDialogVisible"
      title="粘贴Cookie文本"
      width="600px"
    >
      <el-input
        v-model="pasteText"
        type="textarea"
        :rows="10"
        placeholder="请粘贴Cookie内容...&#10;&#10;支持格式：&#10;1. JSON格式（推荐）&#10;2. Netscape格式（每行一个Cookie）&#10;3. Header String格式"
      />
      <template #footer>
        <el-button @click="pasteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePaste">解析</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload,
  FolderOpened,
  Document,
  List,
  Delete,
  QuestionFilled
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const isDragging = ref(false)
const parsedCookies = ref([])
const validationResult = ref({})
const fileInputRef = ref(null)
const pasteDialogVisible = ref(false)
const pasteText = ref('')
const currentPage = ref(1)
const pageSize = 10

const emit = defineEmits(['cookies-parsed', 'cookies-validated'])

// 计算属性
const paginatedCookies = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return parsedCookies.value.slice(start, end)
})

// Cookie解析器
class CookieParser {
  parse(content) {
    // 尝试3种格式
    
    // 格式1: JSON数组
    try {
      const json = JSON.parse(content)
      if (Array.isArray(json)) {
        return this.normalizeJsonCookies(json)
      }
    } catch (e) {
      // 继续尝试其他格式
    }
    
    // 格式2: Netscape格式
    if (content.includes('\t') || content.includes('#')) {
      return this.parseNetscape(content)
    }
    
    // 格式3: Header String格式
    if (content.includes('=') && (content.includes(';') || content.includes(','))) {
      return this.parseHeaderString(content)
    }
    
    throw new Error('无法识别Cookie格式，请检查内容是否正确')
  }
  
  normalizeJsonCookies(cookies) {
    return cookies.map(cookie => ({
      name: cookie.name || cookie.key,
      value: cookie.value,
      domain: cookie.domain || '.kookapp.cn',
      path: cookie.path || '/',
      expires: cookie.expires || cookie.expirationDate,
      httpOnly: cookie.httpOnly !== false,
      secure: cookie.secure !== false,
      sameSite: cookie.sameSite || 'None'
    }))
  }
  
  parseNetscape(content) {
    const lines = content.split('\n')
    const cookies = []
    
    for (const line of lines) {
      if (line.startsWith('#') || !line.trim()) continue
      
      const parts = line.split('\t')
      if (parts.length >= 7) {
        cookies.push({
          name: parts[5],
          value: parts[6],
          domain: parts[0],
          path: parts[2],
          expires: parseInt(parts[4]) || null,
          httpOnly: parts[1] === 'TRUE',
          secure: parts[3] === 'TRUE'
        })
      }
    }
    
    return cookies
  }
  
  parseHeaderString(content) {
    const cookies = []
    const pairs = content.split(/[;,]\s*/)
    
    for (const pair of pairs) {
      const [name, ...valueParts] = pair.split('=')
      if (name && valueParts.length > 0) {
        cookies.push({
          name: name.trim(),
          value: valueParts.join('=').trim(),
          domain: '.kookapp.cn',
          path: '/',
          expires: null,
          httpOnly: true,
          secure: true
        })
      }
    }
    
    return cookies
  }
  
  validate(cookies) {
    // 检查必需字段
    const requiredFields = ['_ga', '_gid', 'sid', 'token']
    const cookieNames = cookies.map(c => c.name)
    const missingFields = requiredFields.filter(field => !cookieNames.includes(field))
    
    const hasRequired = missingFields.length === 0
    
    // 检查过期Cookie
    const now = Date.now() / 1000
    const expiredCount = cookies.filter(c => c.expires && c.expires < now).length
    
    return {
      valid: hasRequired && expiredCount === 0,
      has_required: hasRequired,
      missing_fields: missingFields,
      expired_count: expiredCount,
      total_count: cookies.length
    }
  }
}

const parser = new CookieParser()

// 方法
const handleDrop = async (e) => {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  
  if (!file) return
  
  await processFile(file)
}

const selectFile = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  
  await processFile(file)
}

const processFile = async (file) => {
  try {
    const content = await file.text()
    await parseCookies(content)
    
    ElMessage.success('文件读取成功')
  } catch (error) {
    console.error('文件读取失败:', error)
    ElMessage.error('文件读取失败: ' + error.message)
  }
}

const parseCookies = async (content) => {
  try {
    const cookies = parser.parse(content)
    parsedCookies.value = cookies
    
    // 验证Cookie
    const validation = parser.validate(cookies)
    
    if (validation.valid) {
      validationResult.value = {
        type: 'success',
        title: '✅ Cookie有效',
        description: `已成功解析 ${cookies.length} 条Cookie，所有必需字段完整`
      }
    } else if (validation.has_required) {
      validationResult.value = {
        type: 'warning',
        title: '⚠️ Cookie部分有效',
        description: `已解析 ${cookies.length} 条Cookie，但有 ${validation.expired_count} 条已过期`
      }
    } else {
      validationResult.value = {
        type: 'error',
        title: '❌ Cookie可能无效',
        description: '缺少必需字段，可能无法正常登录',
        missing_fields: validation.missing_fields
      }
    }
    
    emit('cookies-parsed', cookies)
    emit('cookies-validated', validation)
  } catch (error) {
    console.error('解析Cookie失败:', error)
    validationResult.value = {
      type: 'error',
      title: '❌ 解析失败',
      description: error.message
    }
    ElMessage.error('解析失败: ' + error.message)
  }
}

const showPasteDialog = () => {
  pasteDialogVisible.value = true
  pasteText.value = ''
}

const handlePaste = async () => {
  if (!pasteText.value.trim()) {
    ElMessage.warning('请粘贴Cookie内容')
    return
  }
  
  await parseCookies(pasteText.value)
  pasteDialogVisible.value = false
}

const clearCookies = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清除已导入的Cookie吗？',
      '确认清除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    parsedCookies.value = []
    validationResult.value = {}
    ElMessage.info('已清除')
  } catch {
    // 用户取消
  }
}

const maskValue = (value) => {
  if (!value || value.length <= 10) return value
  return value.substring(0, 10) + '...'
}

const formatDate = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}

const getStatusType = (expires) => {
  if (!expires) return 'info'
  const now = Date.now() / 1000
  if (expires < now) return 'danger'
  if (expires < now + 86400) return 'warning' // 24小时内过期
  return 'success'
}

const getStatusText = (expires) => {
  if (!expires) return '会话'
  const now = Date.now() / 1000
  if (expires < now) return '已过期'
  if (expires < now + 86400) return '即将过期'
  return '有效'
}

const showCookieHelp = () => {
  router.push('/help?section=cookie')
}
</script>

<style scoped>
.cookie-import-container {
  width: 100%;
}

.drag-drop-zone-ultra {
  height: 300px;
  border: 3px dashed #dcdfe6;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-size: 200% 200%;
  animation: gradient-pulse 3s ease infinite;
  position: relative;
  overflow: hidden;
}

@keyframes gradient-pulse {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.drag-drop-zone-ultra.is-dragging {
  border-color: #409eff;
  border-width: 4px;
  transform: scale(1.02);
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.4);
}

.drag-drop-zone-ultra.has-cookies {
  border-color: #67C23A;
  background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);
}

.drag-drop-zone-ultra h2 {
  color: white;
  font-size: 24px;
  margin: 15px 0 5px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.format-hint {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  margin: 5px 0 15px;
}

.drag-icon-pulse {
  color: white;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

.action-buttons {
  display: flex;
  gap: 15px;
  margin-top: 10px;
}

.cookie-preview-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination {
  margin-top: 15px;
  justify-content: center;
}

.validation-alert {
  margin-top: 15px;
}

.validation-alert ul {
  margin: 10px 0 0 20px;
}

.validation-alert li {
  margin: 5px 0;
}

.help-section {
  margin-top: 20px;
  text-align: center;
}

/* 暗黑模式 */
.dark .drag-drop-zone-ultra {
  border-color: #4c4d4f;
}

.dark .drag-drop-zone-ultra.is-dragging {
  border-color: #409eff;
}

.dark .drag-drop-zone-ultra.has-cookies {
  border-color: #67C23A;
}
</style>
