<template>
  <div class="cookie-import-drag-drop">
    <h3>🍪 导入 Cookie</h3>

    <!-- 导入方式选择 -->
    <el-radio-group v-model="importMethod" class="import-method">
      <el-radio label="paste">📋 粘贴文本</el-radio>
      <el-radio label="file">📁 上传文件</el-radio>
      <el-radio label="extension">🔌 浏览器扩展</el-radio>
    </el-radio-group>

    <!-- 粘贴文本方式 -->
    <div v-if="importMethod === 'paste'" class="paste-area">
      <el-input
        v-model="cookieText"
        type="textarea"
        :rows="8"
        placeholder="请粘贴 Cookie 内容（支持 JSON、Netscape、键值对等多种格式）"
        @input="handlePaste"
      />
      
      <!-- 实时预览 -->
      <div v-if="parsedCookies && parsedCookies.length > 0" class="preview">
        <h4>✅ 解析成功（{{ parsedCookies.length }} 条 Cookie）</h4>
        <el-table :data="parsedCookies.slice(0, 5)" size="small" max-height="200">
          <el-table-column prop="name" label="名称" width="150" />
          <el-table-column prop="value" label="值" show-overflow-tooltip />
          <el-table-column prop="domain" label="域名" width="150" />
        </el-table>
        <p v-if="parsedCookies.length > 5" class="more-info">
          还有 {{ parsedCookies.length - 5 }} 条...
        </p>
      </div>

      <!-- 错误提示 -->
      <el-alert
        v-if="parseError"
        type="error"
        :closable="false"
        show-icon
      >
        <template #title>
          ❌ Cookie 格式错误
        </template>
        <p>{{ parseError }}</p>
        <p>
          <el-button type="text" @click="showFormatHelp">
            查看支持的格式
          </el-button>
        </p>
      </el-alert>
    </div>

    <!-- 文件上传方式 -->
    <div v-if="importMethod === 'file'" class="file-upload">
      <el-upload
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".json,.txt"
        :show-file-list="false"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持格式：JSON 文件（.json）、文本文件（.txt）
          </div>
        </template>
      </el-upload>

      <!-- 文件解析结果 -->
      <div v-if="uploadedFileName" class="upload-result">
        <el-alert type="success" :closable="false">
          <p>📄 文件：{{ uploadedFileName }}</p>
          <p>✅ 解析成功：{{ parsedCookies?.length || 0 }} 条 Cookie</p>
        </el-alert>
      </div>
    </div>

    <!-- 浏览器扩展方式 -->
    <div v-if="importMethod === 'extension'" class="extension-guide">
      <el-steps :active="extensionStep" align-center>
        <el-step title="安装扩展" description="Chrome 商店搜索 EditThisCookie" />
        <el-step title="登录 KOOK" description="在浏览器中登录 www.kookapp.cn" />
        <el-step title="导出 Cookie" description="点击扩展图标 → 导出" />
        <el-step title="粘贴导入" description="复制 JSON 内容到本系统" />
      </el-steps>

      <el-carousel height="300px" class="tutorial-carousel">
        <el-carousel-item v-for="i in 4" :key="i">
          <div class="carousel-content">
            <img :src="`/help-images/cookie-ext-step${i}.png`" alt=`步骤 ${i}`>
            <p>{{ getExtensionStepText(i) }}</p>
          </div>
        </el-carousel-item>
      </el-carousel>

      <el-button type="primary" @click="openExtensionDownload">
        下载 EditThisCookie 扩展
      </el-button>

      <el-divider />

      <p>导出 Cookie 后，切换到"粘贴文本"方式导入。</p>
    </div>

    <!-- Cookie 验证信息 -->
    <div v-if="parsedCookies && parsedCookies.length > 0" class="validation-info">
      <h4>🔍 Cookie 验证</h4>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Cookie 数量">
          {{ parsedCookies.length }} 条
        </el-descriptions-item>
        <el-descriptions-item label="域名">
          {{ getCookieDomains() }}
        </el-descriptions-item>
        <el-descriptions-item label="过期时间">
          {{ getExpiryInfo() }}
        </el-descriptions-item>
        <el-descriptions-item label="验证状态">
          <el-tag :type="isValid ? 'success' : 'danger'">
            {{ isValid ? '✅ 有效' : '❌ 无效' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <!-- 操作按钮 -->
    <div class="actions">
      <el-button @click="$emit('cancel')">
        取消
      </el-button>
      <el-button
        type="primary"
        :disabled="!parsedCookies || parsedCookies.length === 0 || !isValid"
        @click="handleConfirm"
      >
        ✅ 确认导入
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

const emit = defineEmits(['confirm', 'cancel'])

// 状态
const importMethod = ref('paste')
const cookieText = ref('')
const parsedCookies = ref(null)
const parseError = ref('')
const uploadedFileName = ref('')
const extensionStep = ref(0)
const isValid = ref(false)

// 计算属性
const getCookieDomains = () => {
  if (!parsedCookies.value) return ''
  const domains = [...new Set(parsedCookies.value.map(c => c.domain))]
  return domains.join(', ')
}

const getExpiryInfo = () => {
  if (!parsedCookies.value) return ''
  
  const now = Date.now() / 1000
  const withExpiry = parsedCookies.value.filter(c => c.expirationDate)
  
  if (withExpiry.length === 0) return '会话 Cookie'
  
  const minExpiry = Math.min(...withExpiry.map(c => c.expirationDate))
  const days = Math.floor((minExpiry - now) / 86400)
  
  if (days < 0) return '⚠️ 已过期'
  if (days < 7) return `⚠️ 即将过期（${days} 天）`
  return `✅ 有效（${days} 天）`
}

// 方法
const handlePaste = async () => {
  try {
    parseError.value = ''
    parsedCookies.value = null
    
    if (!cookieText.value.trim()) {
      return
    }

    // 调用后端解析 Cookie
    const response = await fetch('/api/cookie/parse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cookie_text: cookieText.value })
    })

    const data = await response.json()

    if (data.success) {
      parsedCookies.value = data.cookies
      isValid.value = data.valid
      ElMessage.success(`✅ 解析成功：${data.cookies.length} 条 Cookie`)
    } else {
      parseError.value = data.error || '解析失败'
    }

  } catch (error) {
    parseError.value = error.message
  }
}

const handleFileChange = (file) => {
  const reader = new FileReader()
  
  reader.onload = (e) => {
    cookieText.value = e.target.result
    uploadedFileName.value = file.name
    handlePaste()
  }
  
  reader.readAsText(file.raw)
}

const showFormatHelp = () => {
  ElMessage.info({
    message: '支持的格式：JSON 数组、Netscape 格式、键值对（key=value）',
    duration: 5000,
    showClose: true
  })
}

const openExtensionDownload = () => {
  window.open('https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg', '_blank')
}

const getExtensionStepText = (step) => {
  const texts = [
    '在 Chrome 商店搜索并安装 EditThisCookie',
    '在浏览器中打开 www.kookapp.cn 并登录',
    '点击 EditThisCookie 图标，选择"导出"',
    '复制 JSON 内容，粘贴到本系统'
  ]
  return texts[step - 1] || ''
}

const handleConfirm = () => {
  if (!parsedCookies.value || !isValid.value) {
    ElMessage.error('Cookie 无效，无法导入')
    return
  }

  emit('confirm', {
    cookies: parsedCookies.value,
    raw: cookieText.value
  })
}
</script>

<style scoped>
.cookie-import-drag-drop {
  padding: 20px;
}

h3 {
  margin-bottom: 20px;
}

.import-method {
  margin-bottom: 20px;
  display: flex;
  gap: 20px;
}

.paste-area,
.file-upload,
.extension-guide {
  margin: 20px 0;
}

.preview {
  margin-top: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.preview h4 {
  margin-bottom: 10px;
  color: #67c23a;
}

.more-info {
  margin-top: 10px;
  color: #666;
  font-size: 14px;
}

.upload-result {
  margin-top: 20px;
}

.tutorial-carousel {
  margin: 20px 0;
}

.carousel-content {
  text-align: center;
  padding: 20px;
}

.carousel-content img {
  max-width: 100%;
  max-height: 220px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.carousel-content p {
  margin-top: 10px;
  color: #666;
}

.validation-info {
  margin: 30px 0;
  padding: 20px;
  background: #f0f9ff;
  border-radius: 4px;
}

.validation-info h4 {
  margin-bottom: 15px;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

.el-upload {
  width: 100%;
}

.el-icon--upload {
  font-size: 67px;
  color: #409eff;
  margin: 40px 0 16px;
}
</style>
