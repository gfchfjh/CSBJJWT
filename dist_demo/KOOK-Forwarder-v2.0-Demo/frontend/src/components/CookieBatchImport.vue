<template>
  <el-dialog
    v-model="dialogVisible"
    title="批量导入Cookie"
    width="900px"
    :close-on-click-modal="false"
  >
    <el-alert
      title="批量导入说明"
      type="info"
      :closable="false"
      show-icon
      class="info-alert"
    >
      <p>支持同时导入多个KOOK账号的Cookie，提升配置效率</p>
      <ul>
        <li>格式1: 每行一个账号 → <code>邮箱|Cookie内容</code></li>
        <li>格式2: 直接粘贴多个Cookie JSON（用空行分隔）</li>
        <li>格式3: 拖拽上传多个Cookie文件（.json/.txt）</li>
      </ul>
    </el-alert>

    <el-tabs v-model="activeTab" class="import-tabs">
      <!-- Tab 1: 文本输入 -->
      <el-tab-pane label="文本输入" name="text">
        <el-form :model="form" label-width="100px">
          <el-form-item label="批量输入">
            <el-input
              v-model="form.batchInput"
              type="textarea"
              :rows="12"
              placeholder="示例格式1（推荐）:
user1@example.com|[{'name':'token','value':'xxx'}]
user2@example.com|[{'name':'token','value':'yyy'}]

示例格式2:
[{'name':'token','value':'xxx'}]

[{'name':'token','value':'yyy'}]"
              @input="handleTextInput"
            />
          </el-form-item>

          <el-form-item label="自动检测">
            <el-tag type="info">
              已识别 {{ parsedAccounts.length }} 个账号
            </el-tag>
            <el-button 
              type="primary" 
              size="small"
              style="margin-left: 10px"
              @click="validateAllCookies"
              :loading="validating"
            >
              验证所有Cookie
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- Tab 2: 文件上传 -->
      <el-tab-pane label="文件上传" name="file">
        <el-upload
          ref="uploadRef"
          class="upload-area"
          drag
          multiple
          :auto-upload="false"
          :on-change="handleFileChange"
          :file-list="fileList"
          accept=".json,.txt"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖拽多个Cookie文件到此处<br>
            或 <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 .json 和 .txt 格式，可一次上传多个文件
            </div>
          </template>
        </el-upload>

        <div v-if="uploadedAccounts.length > 0" class="uploaded-preview">
          <el-divider>已上传文件</el-divider>
          <el-tag 
            v-for="(file, index) in uploadedAccounts" 
            :key="index"
            closable
            @close="removeUploadedFile(index)"
            style="margin-right: 10px; margin-bottom: 10px"
          >
            {{ file.filename }} ({{ file.cookieCount }} cookies)
          </el-tag>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 账号列表预览 -->
    <el-divider>导入预览</el-divider>
    
    <div class="preview-stats">
      <el-statistic title="总计" :value="parsedAccounts.length">
        <template #prefix>
          <el-icon><User /></el-icon>
        </template>
      </el-statistic>
      
      <el-statistic title="有效" :value="validAccountsCount">
        <template #prefix>
          <el-icon color="#67C23A"><CircleCheck /></el-icon>
        </template>
      </el-statistic>
      
      <el-statistic title="无效" :value="invalidAccountsCount">
        <template #prefix>
          <el-icon color="#F56C6C"><CircleClose /></el-icon>
        </template>
      </el-statistic>
    </div>

    <el-table 
      :data="paginatedAccounts" 
      border 
      max-height="350"
      :row-class-name="tableRowClassName"
    >
      <el-table-column type="index" label="#" width="50" />
      <el-table-column prop="email" label="邮箱" width="220">
        <template #default="{ row }">
          <el-input 
            v-if="row.emailEditable"
            v-model="row.email"
            size="small"
            @blur="row.emailEditable = false"
          />
          <span v-else @dblclick="row.emailEditable = true">
            {{ row.email }}
          </span>
        </template>
      </el-table-column>
      
      <el-table-column label="Cookie状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="cookieCount" label="Cookie数" width="100" />
      
      <el-table-column label="过期时间" width="120">
        <template #default="{ row }">
          <span :class="getExpiresClass(row.expires)">
            {{ row.expires || '-' }}
          </span>
        </template>
      </el-table-column>
      
      <el-table-column prop="message" label="备注" show-overflow-tooltip />
      
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ $index }">
          <el-button 
            type="danger" 
            size="small" 
            link
            @click="removeAccount($index)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-if="parsedAccounts.length > pageSize"
      v-model:current-page="currentPage"
      :page-size="pageSize"
      :total="parsedAccounts.length"
      layout="total, prev, pager, next"
      style="margin-top: 15px; justify-content: center"
    />

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false" size="large">
          取消
        </el-button>
        <el-button 
          type="primary" 
          size="large"
          :loading="importing"
          :disabled="validAccountsCount === 0"
          @click="handleBatchImport"
        >
          <el-icon><Upload /></el-icon>
          导入 {{ validAccountsCount }} 个有效账号
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { 
  UploadFilled, 
  User, 
  CircleCheck, 
  CircleClose,
  Upload 
} from '@element-plus/icons-vue'
import api from '@/api'

const emit = defineEmits(['refresh', 'success'])

const dialogVisible = ref(false)
const activeTab = ref('text')
const importing = ref(false)
const validating = ref(false)

const form = ref({
  batchInput: ''
})

const fileList = ref([])
const uploadRef = ref(null)
const uploadedAccounts = ref([])

const parsedAccounts = ref([])
const currentPage = ref(1)
const pageSize = ref(10)

// 分页数据
const paginatedAccounts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return parsedAccounts.value.slice(start, end)
})

// 有效账号数量
const validAccountsCount = computed(() => {
  return parsedAccounts.value.filter(a => a.status === 'valid').length
})

// 无效账号数量
const invalidAccountsCount = computed(() => {
  return parsedAccounts.value.filter(a => a.status === 'error').length
})

// 解析批量输入
const parseBatchInput = (text) => {
  if (!text || !text.trim()) {
    return []
  }

  const lines = text.split('\n')
  const accounts = []
  let currentCookie = ''
  let currentEmail = ''
  let index = 0

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()

    // 跳过空行
    if (!line) {
      // 如果有累积的Cookie，保存它
      if (currentCookie) {
        accounts.push({
          index: ++index,
          email: currentEmail || `auto_${index}@kook.com`,
          cookie: currentCookie,
          status: 'pending',
          cookieCount: 0,
          expires: null,
          message: '待验证',
          emailEditable: false
        })
        currentCookie = ''
        currentEmail = ''
      }
      continue
    }

    // 格式1: email|cookie
    if (line.includes('|')) {
      // 先保存之前累积的
      if (currentCookie) {
        accounts.push({
          index: ++index,
          email: currentEmail || `auto_${index}@kook.com`,
          cookie: currentCookie,
          status: 'pending',
          cookieCount: 0,
          expires: null,
          message: '待验证',
          emailEditable: false
        })
      }

      const [email, cookie] = line.split('|', 2)
      currentEmail = email.trim()
      currentCookie = cookie.trim()
      
    }
    // 格式2: JSON开头
    else if (line.startsWith('{') || line.startsWith('[')) {
      if (currentCookie && !currentCookie.endsWith('}') && !currentCookie.endsWith(']')) {
        // 继续累积多行JSON
        currentCookie += '\n' + line
      } else {
        // 新的Cookie开始
        if (currentCookie) {
          accounts.push({
            index: ++index,
            email: currentEmail || `auto_${index}@kook.com`,
            cookie: currentCookie,
            status: 'pending',
            cookieCount: 0,
            expires: null,
            message: '待验证',
            emailEditable: false
          })
        }
        currentCookie = line
        currentEmail = ''
      }
    }
    // 继续累积
    else if (currentCookie) {
      currentCookie += '\n' + line
    }
  }

  // 保存最后一个
  if (currentCookie) {
    accounts.push({
      index: ++index,
      email: currentEmail || `auto_${index}@kook.com`,
      cookie: currentCookie,
      status: 'pending',
      cookieCount: 0,
      expires: null,
      message: '待验证',
      emailEditable: false
    })
  }

  return accounts
}

// 处理文本输入
const handleTextInput = () => {
  parsedAccounts.value = parseBatchInput(form.value.batchInput)
  currentPage.value = 1
}

// 验证所有Cookie
const validateAllCookies = async () => {
  if (parsedAccounts.value.length === 0) {
    ElMessage.warning('没有可验证的账号')
    return
  }

  validating.value = true

  try {
    for (const account of parsedAccounts.value) {
      if (account.status !== 'pending') {
        continue
      }

      try {
        const result = await api.post('/api/wizard/smart/validate-cookie', {
          cookie: account.cookie
        })

        if (result.valid) {
          account.status = 'valid'
          account.cookieCount = result.count
          account.expires = result.expires
          account.message = '有效'
          
          if (result.email) {
            account.email = result.email
          }
        } else {
          account.status = 'error'
          account.message = result.message || '无效'
        }
      } catch (error) {
        account.status = 'error'
        account.message = error.response?.data?.detail || error.message
      }

      // 添加小延迟避免请求过快
      await new Promise(resolve => setTimeout(resolve, 200))
    }

    ElMessage.success(`验证完成！有效: ${validAccountsCount.value}, 无效: ${invalidAccountsCount.value}`)
  } catch (error) {
    ElMessage.error('验证失败: ' + error.message)
  } finally {
    validating.value = false
  }
}

// 处理文件上传
const handleFileChange = (file, fileList) => {
  const reader = new FileReader()
  
  reader.onload = (e) => {
    const content = e.target.result
    const accounts = parseBatchInput(content)
    
    if (accounts.length > 0) {
      uploadedAccounts.value.push({
        filename: file.name,
        cookieCount: accounts.length,
        accounts: accounts
      })

      // 合并到主列表
      parsedAccounts.value.push(...accounts)
      
      ElMessage.success(`文件 ${file.name} 已解析，找到 ${accounts.length} 个账号`)
    } else {
      ElMessage.warning(`文件 ${file.name} 解析失败`)
    }
  }
  
  reader.onerror = () => {
    ElMessage.error(`文件 ${file.name} 读取失败`)
  }
  
  reader.readAsText(file.raw)
}

// 移除上传的文件
const removeUploadedFile = (index) => {
  const removed = uploadedAccounts.value.splice(index, 1)[0]
  
  // 从主列表中移除相关账号
  if (removed.accounts) {
    parsedAccounts.value = parsedAccounts.value.filter(
      account => !removed.accounts.some(a => a.index === account.index)
    )
  }
}

// 移除账号
const removeAccount = (index) => {
  const realIndex = (currentPage.value - 1) * pageSize.value + index
  parsedAccounts.value.splice(realIndex, 1)
}

// 批量导入
const handleBatchImport = async () => {
  if (validAccountsCount.value === 0) {
    ElMessage.warning('没有有效的账号可导入')
    return
  }

  try {
    importing.value = true
    
    const validAccounts = parsedAccounts.value.filter(a => a.status === 'valid')
    let successCount = 0
    let failCount = 0
    const errors = []

    for (const account of validAccounts) {
      try {
        await api.post('/api/accounts/add', {
          email: account.email,
          cookie: account.cookie
        })
        
        successCount++
        account.message = '导入成功'
        account.status = 'success'
        
      } catch (error) {
        failCount++
        const errorMsg = error.response?.data?.detail || error.message
        account.message = `导入失败: ${errorMsg}`
        account.status = 'error'
        errors.push(`${account.email}: ${errorMsg}`)
      }

      // 添加延迟
      await new Promise(resolve => setTimeout(resolve, 300))
    }

    // 显示结果
    if (successCount > 0) {
      ElNotification({
        title: '批量导入完成',
        message: `成功导入 ${successCount} 个账号${failCount > 0 ? `，失败 ${failCount} 个` : ''}`,
        type: successCount === validAccounts.length ? 'success' : 'warning',
        duration: 5000
      })

      emit('success', { successCount, failCount })
      emit('refresh')

      if (failCount === 0) {
        dialogVisible.value = false
      }
    } else {
      ElMessage.error('全部导入失败')
    }

    // 如果有错误，显示详情
    if (errors.length > 0 && errors.length <= 5) {
      console.error('导入错误详情:', errors)
    }

  } catch (error) {
    ElMessage.error('批量导入失败: ' + error.message)
  } finally {
    importing.value = false
  }
}

// 表格行样式
const tableRowClassName = ({ row }) => {
  if (row.status === 'valid' || row.status === 'success') {
    return 'success-row'
  } else if (row.status === 'error') {
    return 'error-row'
  }
  return ''
}

// 状态类型
const getStatusType = (status) => {
  if (status === 'valid' || status === 'success') return 'success'
  if (status === 'error') return 'danger'
  return 'info'
}

// 状态文本
const getStatusText = (status) => {
  const map = {
    pending: '待验证',
    valid: '有效',
    success: '已导入',
    error: '无效'
  }
  return map[status] || status
}

// 过期时间样式
const getExpiresClass = (expires) => {
  if (!expires) return ''
  
  const expiresDate = new Date(expires)
  const daysLeft = Math.floor((expiresDate - new Date()) / (1000 * 60 * 60 * 24))
  
  if (daysLeft < 0) return 'expires-past'
  if (daysLeft < 7) return 'expires-soon'
  return 'expires-ok'
}

// 打开对话框
const open = () => {
  dialogVisible.value = true
  // 重置状态
  form.value.batchInput = ''
  fileList.value = []
  uploadedAccounts.value = []
  parsedAccounts.value = []
  currentPage.value = 1
}

defineExpose({ open })
</script>

<style scoped>
.info-alert {
  margin-bottom: 20px;
}

.info-alert ul {
  margin: 10px 0 0 20px;
  padding: 0;
}

.info-alert li {
  margin: 5px 0;
}

.info-alert code {
  padding: 2px 6px;
  background: #f0f0f0;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

.import-tabs {
  margin-bottom: 20px;
}

.upload-area {
  margin-top: 20px;
}

.uploaded-preview {
  margin-top: 20px;
}

.preview-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

:deep(.success-row) {
  background: #f6ffed !important;
}

:deep(.error-row) {
  background: #fff1f0 !important;
}

.expires-past {
  color: #ff4d4f;
  font-weight: bold;
}

.expires-soon {
  color: #fa8c16;
  font-weight: bold;
}

.expires-ok {
  color: #52c41a;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
