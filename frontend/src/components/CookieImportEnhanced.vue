<template>
  <!-- ✅ P0-3优化: 增强的Cookie导入组件 -->
  <div class="cookie-import-enhanced">
    <!-- 导入方式选择 -->
    <div class="import-methods">
      <el-segmented v-model="importMethod" :options="importOptions" block>
        <template #default="{ item }">
          <div class="method-option">
            <el-icon :size="20">
              <component :is="item.icon" />
            </el-icon>
            <span>{{ item.label }}</span>
            <el-tag v-if="item.recommended" size="small" type="success" effect="dark">
              推荐
            </el-tag>
          </div>
        </template>
      </el-segmented>
    </div>

    <!-- 方式1: 浏览器扩展（最推荐） -->
    <div v-if="importMethod === 'extension'" class="method-extension">
      <el-result 
        :icon="extensionConnected ? 'success' : 'warning'" 
        :title="extensionConnected ? '✅ 扩展已连接' : '⚠️ 扩展未安装或未启用'"
      >
        <template #sub-title>
          <div v-if="!extensionConnected">
            <p>安装浏览器扩展后，只需一键即可导入Cookie</p>
            <p style="color: #909399; font-size: 14px;">这是最简单、最安全的方式</p>
          </div>
          <div v-else>
            <p>扩展已就绪！请在KOOK网页版点击扩展图标导出Cookie</p>
          </div>
        </template>
        <template #extra>
          <div v-if="!extensionConnected" style="display: flex; gap: 12px; justify-content: center;">
            <el-button type="primary" size="large" @click="downloadExtension">
              <el-icon><Download /></el-icon>
              下载Chrome扩展
            </el-button>
            <el-button size="large" @click="showExtensionTutorial">
              <el-icon><Document /></el-icon>
              查看安装教程
            </el-button>
          </div>
          <div v-else>
            <el-alert type="info" :closable="false" show-icon>
              <template #title>
                <div style="display: flex; align-items: center; gap: 8px;">
                  <el-icon class="is-loading"><Loading /></el-icon>
                  <span>等待扩展发送Cookie...</span>
                </div>
              </template>
              <p>请在浏览器中打开KOOK网页版，点击扩展图标导出Cookie</p>
            </el-alert>
          </div>
        </template>
      </el-result>
    </div>

    <!-- 方式2: 拖拽上传 -->
    <div v-if="importMethod === 'file'" class="method-file">
      <el-upload
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :show-file-list="false"
        accept=".json,.txt"
        class="cookie-upload"
      >
        <el-icon class="el-icon--upload" :size="80">
          <UploadFilled />
        </el-icon>
        <div class="el-upload__text">
          将Cookie文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 .json 和 .txt 格式文件
          </div>
        </template>
      </el-upload>
    </div>

    <!-- 方式3: 粘贴文本 -->
    <div v-if="importMethod === 'paste'" class="method-paste">
      <el-input
        v-model="cookieText"
        type="textarea"
        :rows="10"
        placeholder="请粘贴Cookie内容（支持多种格式，会自动识别）"
        @input="validateCookieRealtime"
      />

      <!-- 实时验证反馈 -->
      <transition name="el-fade-in">
        <div v-if="validationResult.status" class="validation-feedback">
          <el-alert
            :type="validationResult.type"
            :closable="false"
            show-icon
          >
            <template #title>
              <div v-html="validationResult.message" />
            </template>
          </el-alert>
        </div>
      </transition>

      <!-- 格式帮助（默认展开） -->
      <el-card class="format-help" shadow="never">
        <template #header>
          <div class="help-header">
            <el-icon color="#409EFF"><QuestionFilled /></el-icon>
            <span>Cookie格式说明</span>
          </div>
        </template>

        <el-collapse v-model="activeFormatTab">
          <el-collapse-item title="✅ 格式1: JSON数组（推荐）" name="json">
            <el-input
              type="textarea"
              :rows="4"
              readonly
              :value="formatExamples.json"
              class="example-code"
            />
            <div class="example-actions">
              <el-button size="small" text @click="copyExample('json')">
                <el-icon><DocumentCopy /></el-icon>
                复制示例
              </el-button>
              <el-button size="small" text @click="useExample('json')">
                <el-icon><Check /></el-icon>
                使用此格式
              </el-button>
            </div>
          </el-collapse-item>

          <el-collapse-item title="✅ 格式2: Netscape格式" name="netscape">
            <el-input
              type="textarea"
              :rows="4"
              readonly
              :value="formatExamples.netscape"
              class="example-code"
            />
            <div class="example-actions">
              <el-button size="small" text @click="copyExample('netscape')">
                <el-icon><DocumentCopy /></el-icon>
                复制示例
              </el-button>
              <el-button size="small" text @click="useExample('netscape')">
                <el-icon><Check /></el-icon>
                使用此格式
              </el-button>
            </div>
          </el-collapse-item>

          <el-collapse-item title="✅ 格式3: 键值对格式" name="keyValue">
            <el-input
              type="textarea"
              :rows="2"
              readonly
              :value="formatExamples.keyValue"
              class="example-code"
            />
            <div class="example-actions">
              <el-button size="small" text @click="copyExample('keyValue')">
                <el-icon><DocumentCopy /></el-icon>
                复制示例
              </el-button>
              <el-button size="small" text @click="useExample('keyValue')">
                <el-icon><Check /></el-icon>
                使用此格式
              </el-button>
            </div>
          </el-collapse-item>
        </el-collapse>
      </el-card>
    </div>

    <!-- 导入按钮 -->
    <div class="import-actions">
      <el-button
        type="primary"
        size="large"
        :disabled="!canImport"
        :loading="importing"
        @click="handleImport"
      >
        <el-icon><Upload /></el-icon>
        确认导入
      </el-button>
      <el-button size="large" @click="handleCancel">
        取消
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Download, Document, UploadFilled, QuestionFilled,
  DocumentCopy, Check, Upload, Loading
} from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'import', 'cancel'])

// 导入方式
const importMethod = ref('extension')
const importOptions = [
  { value: 'extension', label: '浏览器扩展', icon: 'ChromeFilled', recommended: true },
  { value: 'file', label: '上传文件', icon: 'UploadFilled' },
  { value: 'paste', label: '粘贴文本', icon: 'DocumentCopy' }
]

// Cookie文本
const cookieText = ref(props.modelValue)

// 扩展连接状态
const extensionConnected = ref(false)

// 导入状态
const importing = ref(false)

// 实时验证结果
const validationResult = reactive({
  status: false,
  type: 'info',
  message: ''
})

// 格式示例展开状态
const activeFormatTab = ref(['json'])

// 格式示例
const formatExamples = {
  json: `[
  {
    "name": "token",
    "value": "abc123def456",
    "domain": ".kookapp.cn",
    "path": "/",
    "expires": 1735689600
  }
]`,
  netscape: `# Netscape HTTP Cookie File
.kookapp.cn\tTRUE\t/\tFALSE\t1735689600\ttoken\tabc123def456
.kookapp.cn\tTRUE\t/\tFALSE\t1735689600\tsession\txyz789ghi012`,
  keyValue: `token=abc123def456; session=xyz789ghi012; user_id=12345`
}

// 是否可以导入
const canImport = computed(() => {
  if (importMethod.value === 'extension') {
    return extensionConnected.value
  }
  if (importMethod.value === 'paste') {
    return cookieText.value.trim().length > 0 && validationResult.type === 'success'
  }
  if (importMethod.value === 'file') {
    return cookieText.value.trim().length > 0
  }
  return false
})

// 检查扩展连接
const checkExtensionConnection = async () => {
  try {
    const response = await fetch('http://localhost:9527/api/cookie-import/health')
    extensionConnected.value = response.ok
  } catch (error) {
    extensionConnected.value = false
  }
}

// 实时验证Cookie格式
const validateCookieRealtime = (value) => {
  if (!value || value.trim().length === 0) {
    validationResult.status = false
    return
  }

  try {
    // 格式1: JSON数组
    if (value.trim().startsWith('[')) {
      const parsed = JSON.parse(value)
      if (Array.isArray(parsed) && parsed.length > 0) {
        if (parsed[0].name && parsed[0].value) {
          validationResult.status = true
          validationResult.type = 'success'
          validationResult.message = `✅ 识别为JSON格式，包含 ${parsed.length} 个Cookie`
          return
        }
      }
    }

    // 格式2: Netscape格式
    if (value.includes('\t') || value.includes('# Netscape')) {
      const lines = value.split('\n').filter(l => l && !l.startsWith('#'))
      if (lines.length > 0) {
        validationResult.status = true
        validationResult.type = 'success'
        validationResult.message = `✅ 识别为Netscape格式，包含 ${lines.length} 个Cookie`
        return
      }
    }

    // 格式3: 键值对
    if (value.includes('=')) {
      const pairs = value.split(';').filter(p => p.includes('='))
      if (pairs.length > 0) {
        validationResult.status = true
        validationResult.type = 'success'
        validationResult.message = `✅ 识别为键值对格式，包含 ${pairs.length} 个Cookie`
        return
      }
    }

    // 无法识别
    validationResult.status = true
    validationResult.type = 'warning'
    validationResult.message = `
      ⚠️ 格式可能不正确，请检查：<br/>
      <ul style="margin: 5px 0; padding-left: 20px;">
        <li>是否为空白或不完整</li>
        <li>是否包含 Cookie 数据</li>
        <li>参考下方的格式示例</li>
      </ul>
    `
  } catch (error) {
    validationResult.status = true
    validationResult.type = 'error'
    validationResult.message = `❌ 格式错误：${error.message}<br/>请参考格式示例重新输入`
  }
}

// 处理文件上传
const handleFileChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    cookieText.value = e.target.result
    validateCookieRealtime(cookieText.value)
    ElMessage.success('文件已加载')
  }
  reader.onerror = () => {
    ElMessage.error('文件读取失败')
  }
  reader.readAsText(file.raw)
}

// 复制示例
const copyExample = async (type) => {
  try {
    await navigator.clipboard.writeText(formatExamples[type])
    ElMessage.success('已复制示例到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败: ' + error.message)
  }
}

// 使用示例
const useExample = (type) => {
  cookieText.value = formatExamples[type]
  validateCookieRealtime(cookieText.value)
  ElMessage.info('已填充示例，请替换为您的实际Cookie')
}

// 下载扩展
const downloadExtension = () => {
  // 触发下载
  window.open('/chrome-extension.zip', '_blank')
  ElMessage.info('扩展文件准备中...')
}

// 显示扩展教程
const showExtensionTutorial = () => {
  window.open('/docs/cookie-extension-tutorial.html', '_blank')
}

// 处理导入
const handleImport = () => {
  if (!canImport.value) {
    ElMessage.warning('请先输入有效的Cookie')
    return
  }

  importing.value = true

  // 触发导入事件
  emit('import', cookieText.value)

  setTimeout(() => {
    importing.value = false
  }, 1000)
}

// 取消
const handleCancel = () => {
  emit('cancel')
}

// 轮询检查扩展连接
let checkInterval = null

onMounted(() => {
  checkExtensionConnection()
  checkInterval = setInterval(checkExtensionConnection, 5000)
})

onUnmounted(() => {
  if (checkInterval) {
    clearInterval(checkInterval)
  }
})
</script>

<style scoped>
.cookie-import-enhanced {
  padding: 20px;
}

.import-methods {
  margin-bottom: 30px;
}

.method-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
}

.method-extension,
.method-file,
.method-paste {
  min-height: 300px;
}

.cookie-upload {
  width: 100%;
}

.validation-feedback {
  margin-top: 15px;
}

.format-help {
  margin-top: 20px;
}

.help-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.example-code {
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.example-actions {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}

.import-actions {
  margin-top: 30px;
  text-align: center;
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
