<template>
  <div class="accounts-enhanced-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>
          <el-icon><User /></el-icon>
          KOOK账号管理
        </h1>
        <el-tag type="info">{{ accounts.length }}个账号</el-tag>
      </div>
      
      <div class="header-right">
        <el-button-group>
          <el-button :icon="Refresh" @click="refreshAll" :loading="refreshing">
            刷新全部
          </el-button>
          <el-button :icon="Plus" type="primary" @click="showAddAccountDialog">
            添加账号
          </el-button>
        </el-button-group>
      </div>
    </div>
    
    <!-- 快速统计 -->
    <el-row :gutter="16" class="stats-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="总账号数" :value="accounts.length">
            <template #prefix>
              <el-icon color="#409EFF"><User /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="在线账号" :value="onlineCount">
            <template #prefix>
              <el-icon color="#67C23A"><CircleCheck /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="监听服务器" :value="totalServers">
            <template #prefix>
              <el-icon color="#E6A23C"><OfficeBuilding /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="监听频道" :value="totalChannels">
            <template #prefix>
              <el-icon color="#909399"><ChatDotRound /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 账号卡片列表 -->
    <div class="accounts-grid" v-loading="loading">
      <el-empty 
        v-if="accounts.length === 0 && !loading"
        description="还没有添加任何KOOK账号"
        :image-size="200"
      >
        <el-button type="primary" :icon="Plus" @click="showAddAccountDialog">
          添加第一个账号
        </el-button>
      </el-empty>
      
      <el-row :gutter="16" v-else>
        <el-col 
          v-for="account in accounts" 
          :key="account.id" 
          :span="8"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="8"
          :xl="6"
        >
          <el-card 
            class="account-card"
            :class="{ 'is-online': account.online, 'is-offline': !account.online }"
            shadow="hover"
          >
            <!-- 卡片头部 -->
            <template #header>
              <div class="card-header">
                <el-avatar 
                  :src="account.avatar" 
                  :size="50"
                  class="account-avatar"
                >
                  {{ account.email[0].toUpperCase() }}
                </el-avatar>
                
                <div class="account-info">
                  <div class="account-name">{{ account.nickname || account.username }}</div>
                  <div class="account-email">{{ account.email }}</div>
                </div>
                
                <el-tag 
                  :type="account.online ? 'success' : 'danger'"
                  size="small"
                  class="status-tag"
                >
                  {{ account.online ? '在线' : '离线' }}
                </el-tag>
              </div>
            </template>
            
            <!-- 卡片内容 -->
            <el-descriptions :column="1" border size="small" class="account-details">
              <el-descriptions-item label="用户ID">
                <el-text size="small">{{ account.user_id || 'N/A' }}</el-text>
                <el-button 
                  :icon="CopyDocument" 
                  size="small" 
                  text
                  @click="copyText(account.user_id)"
                />
              </el-descriptions-item>
              
              <el-descriptions-item label="服务器">
                <el-tag size="small" type="info">
                  {{ account.server_count || 0 }}个
                </el-tag>
              </el-descriptions-item>
              
              <el-descriptions-item label="最后活跃">
                <el-tooltip :content="formatFullTime(account.last_active)">
                  <span>{{ formatRelativeTime(account.last_active) }}</span>
                </el-tooltip>
              </el-descriptions-item>
              
              <el-descriptions-item label="连接质量">
                <el-progress
                  :percentage="account.connection_quality || 0"
                  :color="getQualityColor(account.connection_quality)"
                  :stroke-width="6"
                />
              </el-descriptions-item>
            </el-descriptions>
            
            <!-- 卡片底部操作 -->
            <template #footer>
              <div class="card-actions">
                <el-button-group size="small">
                  <el-button 
                    :icon="Refresh" 
                    @click="reconnect(account)"
                    :loading="account.reconnecting"
                    :disabled="account.online"
                  >
                    {{ account.online ? '已连接' : '重连' }}
                  </el-button>
                  
                  <el-button 
                    :icon="View" 
                    @click="viewServers(account)"
                  >
                    查看
                  </el-button>
                  
                  <el-button 
                    :icon="Edit" 
                    @click="editAccount(account)"
                  >
                    编辑
                  </el-button>
                  
                  <el-button 
                    :icon="Delete" 
                    type="danger"
                    @click="deleteAccount(account)"
                  >
                    删除
                  </el-button>
                </el-button-group>
              </div>
            </template>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 添加账号对话框 -->
    <el-dialog
      v-model="addDialogVisible"
      title="添加KOOK账号"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-tabs v-model="loginMethod" class="login-tabs">
        <!-- Cookie导入 -->
        <el-tab-pane label="Cookie导入" name="cookie">
          <el-alert
            type="info"
            :closable="false"
            show-icon
            class="method-alert"
          >
            <template #title>
              推荐使用Chrome扩展一键导入Cookie
            </template>
          </el-alert>
          
          <el-form :model="cookieForm" label-width="100px" class="login-form">
            <el-form-item label="Cookie">
              <el-input
                v-model="cookieForm.cookie"
                type="textarea"
                :rows="6"
                placeholder="粘贴完整的Cookie字符串或拖拽JSON文件"
                @drop.prevent="handleFileDrop"
                @dragover.prevent
              />
            </el-form-item>
            
            <el-form-item>
              <el-space>
                <el-button :icon="ChromeFilled" @click="useExtension">
                  使用Chrome扩展
                </el-button>
                <el-button :icon="Upload" @click="uploadCookieFile">
                  上传JSON文件
                </el-button>
                <el-button :icon="QuestionFilled" type="info" text @click="showCookieTutorial">
                  如何获取Cookie？
                </el-button>
              </el-space>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 账号密码登录 -->
        <el-tab-pane label="账号密码登录" name="password">
          <el-alert
            type="warning"
            :closable="false"
            show-icon
            class="method-alert"
          >
            <template #title>
              首次登录可能需要验证码
            </template>
          </el-alert>
          
          <el-form :model="passwordForm" label-width="100px" class="login-form">
            <el-form-item label="邮箱">
              <el-input
                v-model="passwordForm.email"
                placeholder="your@email.com"
                :prefix-icon="Message"
              />
            </el-form-item>
            
            <el-form-item label="密码">
              <el-input
                v-model="passwordForm.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="验证码" v-if="needsCaptcha">
              <el-space>
                <el-image 
                  :src="captchaImage" 
                  style="width: 150px; height: 50px; cursor: pointer;"
                  @click="refreshCaptcha"
                />
                <el-input
                  v-model="passwordForm.captcha"
                  placeholder="验证码"
                  style="width: 150px;"
                />
                <el-button :icon="Refresh" @click="refreshCaptcha">刷新</el-button>
              </el-space>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="submitAddAccount"
          :loading="submitting"
        >
          {{ loginMethod === 'cookie' ? '验证并添加' : '登录并添加' }}
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 服务器查看对话框 -->
    <el-dialog
      v-model="serversDialogVisible"
      :title="`${currentAccount?.email} 的服务器列表`"
      width="800px"
    >
      <ServerChannelTree 
        v-if="currentAccount"
        :account-id="currentAccount.id"
        :selectable="false"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User, Refresh, Plus, CircleCheck, OfficeBuilding, ChatDotRound,
  CopyDocument, View, Edit, Delete, ChromeFilled, Upload, QuestionFilled,
  Message, Lock
} from '@element-plus/icons-vue'
import { useClipboard } from '@vueuse/core'
import ServerChannelTree from '@/components/ServerChannelTree.vue'
import axios from 'axios'

// 剪贴板
const { copy } = useClipboard()

// 状态
const loading = ref(false)
const refreshing = ref(false)
const accounts = ref([])
const addDialogVisible = ref(false)
const serversDialogVisible = ref(false)
const loginMethod = ref('cookie')
const submitting = ref(false)
const needsCaptcha = ref(false)
const captchaImage = ref('')
const currentAccount = ref(null)

// 表单
const cookieForm = ref({
  cookie: ''
})

const passwordForm = ref({
  email: '',
  password: '',
  captcha: ''
})

// 统计
const onlineCount = computed(() => {
  return accounts.value.filter(a => a.online).length
})

const totalServers = computed(() => {
  return accounts.value.reduce((sum, a) => sum + (a.server_count || 0), 0)
})

const totalChannels = computed(() => {
  return accounts.value.reduce((sum, a) => sum + (a.channel_count || 0), 0)
})

// 加载账号列表
async function loadAccounts() {
  loading.value = true
  try {
    const response = await axios.get('/api/accounts')
    accounts.value = response.data.map(account => ({
      ...account,
      reconnecting: false
    }))
  } catch (error) {
    ElMessage.error('加载账号失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 刷新全部
async function refreshAll() {
  refreshing.value = true
  try {
    await axios.post('/api/accounts/refresh-all')
    await loadAccounts()
    ElMessage.success('已刷新所有账号')
  } catch (error) {
    ElMessage.error('刷新失败: ' + error.message)
  } finally {
    refreshing.value = false
  }
}

// 显示添加对话框
function showAddAccountDialog() {
  addDialogVisible.value = true
  loginMethod.value = 'cookie'
  cookieForm.value = { cookie: '' }
  passwordForm.value = { email: '', password: '', captcha: '' }
}

// 提交添加账号
async function submitAddAccount() {
  submitting.value = true
  
  try {
    let response
    
    if (loginMethod.value === 'cookie') {
      // Cookie方式
      if (!cookieForm.value.cookie) {
        ElMessage.warning('请输入Cookie')
        return
      }
      
      response = await axios.post('/api/accounts/add-by-cookie', {
        cookie: cookieForm.value.cookie
      })
    } else {
      // 密码方式
      if (!passwordForm.value.email || !passwordForm.value.password) {
        ElMessage.warning('请填写邮箱和密码')
        return
      }
      
      response = await axios.post('/api/accounts/add-by-password', passwordForm.value)
    }
    
    if (response.data.success) {
      ElMessage.success('账号添加成功')
      addDialogVisible.value = false
      await loadAccounts()
    } else {
      ElMessage.error(response.data.message || '添加失败')
      
      // 检查是否需要验证码
      if (response.data.needs_captcha) {
        needsCaptcha.value = true
        captchaImage.value = response.data.captcha_image
      }
    }
  } catch (error) {
    ElMessage.error('添加失败: ' + error.message)
  } finally {
    submitting.value = false
  }
}

// 重连账号
async function reconnect(account) {
  account.reconnecting = true
  
  try {
    const response = await axios.post(`/api/accounts/${account.id}/reconnect`)
    
    if (response.data.success) {
      ElMessage.success(`${account.email} 重连成功`)
      await loadAccounts()
    } else {
      ElMessage.error(response.data.message || '重连失败')
    }
  } catch (error) {
    ElMessage.error('重连失败: ' + error.message)
  } finally {
    account.reconnecting = false
  }
}

// 查看服务器
function viewServers(account) {
  currentAccount.value = account
  serversDialogVisible.value = true
}

// 编辑账号
function editAccount(account) {
  ElMessageBox.prompt('修改账号备注', '编辑账号', {
    confirmButtonText: '保存',
    cancelButtonText: '取消',
    inputValue: account.nickname || account.username
  }).then(async ({ value }) => {
    try {
      await axios.put(`/api/accounts/${account.id}`, {
        nickname: value
      })
      
      ElMessage.success('修改成功')
      await loadAccounts()
    } catch (error) {
      ElMessage.error('修改失败: ' + error.message)
    }
  }).catch(() => {})
}

// 删除账号
function deleteAccount(account) {
  ElMessageBox.confirm(
    `确定要删除账号 ${account.email} 吗？此操作不可恢复。`,
    '删除账号',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await axios.delete(`/api/accounts/${account.id}`)
      ElMessage.success('删除成功')
      await loadAccounts()
    } catch (error) {
      ElMessage.error('删除失败: ' + error.message)
    }
  }).catch(() => {})
}

// 复制文本
async function copyText(text) {
  await copy(text)
  ElMessage.success('已复制到剪贴板')
}

// 格式化时间
function formatRelativeTime(timestamp) {
  if (!timestamp) return '从未'
  
  const now = Date.now()
  const diff = now - timestamp
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${Math.floor(diff / 86400000)}天前`
}

function formatFullTime(timestamp) {
  if (!timestamp) return 'N/A'
  return new Date(timestamp).toLocaleString('zh-CN')
}

// 连接质量颜色
function getQualityColor(quality) {
  if (quality >= 80) return '#67C23A'
  if (quality >= 50) return '#E6A23C'
  return '#F56C6C'
}

// 文件拖放
function handleFileDrop(event) {
  const file = event.dataTransfer.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      cookieForm.value.cookie = e.target.result
    }
    reader.readAsText(file)
  }
}

// 上传Cookie文件
function uploadCookieFile() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json,.txt'
  input.onchange = (e) => {
    const file = e.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        cookieForm.value.cookie = e.target.result
      }
      reader.readAsText(file)
    }
  }
  input.click()
}

// 使用Chrome扩展
function useExtension() {
  ElMessageBox.alert(
    '请点击Chrome扩展图标，然后点击"导出Cookie"按钮。系统会自动检测并填入。',
    '使用Chrome扩展',
    {
      confirmButtonText: '知道了'
    }
  )
  
  // 监听WebSocket消息
  // 实际实现需要连接WebSocket
}

// 显示Cookie教程
function showCookieTutorial() {
  window.open('/docs/tutorials/01-quick-start.md#cookie导入', '_blank')
}

// 刷新验证码
async function refreshCaptcha() {
  try {
    const response = await axios.post('/api/auth/refresh-captcha')
    captchaImage.value = response.data.image
  } catch (error) {
    ElMessage.error('刷新验证码失败')
  }
}

// 初始化
onMounted(() => {
  loadAccounts()
  
  // 定时刷新状态
  setInterval(() => {
    loadAccounts()
  }, 30000) // 30秒刷新一次
})
</script>

<style scoped>
.accounts-enhanced-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h1 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 24px;
}

.stats-cards {
  margin-bottom: 24px;
}

.accounts-grid {
  min-height: 400px;
}

.account-card {
  margin-bottom: 16px;
  transition: all 0.3s;
}

.account-card.is-online {
  border-left: 4px solid #67C23A;
}

.account-card.is-offline {
  border-left: 4px solid #909399;
}

.account-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.account-avatar {
  flex-shrink: 0;
}

.account-info {
  flex: 1;
  min-width: 0;
}

.account-name {
  font-weight: 600;
  font-size: 16px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.account-email {
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-tag {
  flex-shrink: 0;
}

.account-details {
  margin: 16px 0;
}

.card-actions {
  display: flex;
  justify-content: center;
}

.login-tabs {
  margin: 20px 0;
}

.method-alert {
  margin-bottom: 20px;
}

.login-form {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .header-left, .header-right {
    width: 100%;
  }
}
</style>
