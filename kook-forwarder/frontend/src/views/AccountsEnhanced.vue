<template>
  <div class="accounts-enhanced">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2><el-icon><User /></el-icon> KOOK账号管理</h2>
      <el-button type="primary" :icon="Plus" @click="showAddAccountDialog">
        添加账号
      </el-button>
    </div>
    
    <!-- 账号卡片列表 -->
    <div class="account-cards" v-loading="loading">
      <el-card
        v-for="account in accounts"
        :key="account.id"
        class="account-card"
        :class="{ online: account.status === 'online', offline: account.status === 'offline' }"
        shadow="hover"
      >
        <!-- 状态指示器 -->
        <div class="status-indicator" :class="account.status">
          <span class="status-dot"></span>
        </div>
        
        <!-- 账号信息 -->
        <div class="account-header">
          <el-avatar :size="60" :src="account.avatar">
            <el-icon :size="30"><User /></el-icon>
          </el-avatar>
          
          <div class="account-info">
            <h3 class="account-email">{{ account.email }}</h3>
            <el-tag :type="account.status === 'online' ? 'success' : 'danger'" size="small">
              {{ account.status === 'online' ? '🟢 在线' : '🔴 离线' }}
            </el-tag>
          </div>
        </div>
        
        <!-- 统计信息 -->
        <el-divider />
        
        <div class="account-stats">
          <div class="stat-item">
            <el-icon><OfficeBuilding /></el-icon>
            <span>监听服务器: <strong>{{ account.server_count || 0 }}</strong> 个</span>
          </div>
          
          <div class="stat-item">
            <el-icon><ChatLineSquare /></el-icon>
            <span>监听频道: <strong>{{ account.channel_count || 0 }}</strong> 个</span>
          </div>
          
          <div class="stat-item">
            <el-icon><Timer /></el-icon>
            <span>最后活跃: <strong>{{ formatLastActive(account.last_active) }}</strong></span>
          </div>
          
          <div class="stat-item">
            <el-icon><Message /></el-icon>
            <span>今日消息: <strong>{{ account.today_messages || 0 }}</strong> 条</span>
          </div>
        </div>
        
        <!-- 警告信息 -->
        <el-alert
          v-if="account.status === 'offline'"
          type="warning"
          :closable="false"
          show-icon
          class="warning-alert"
        >
          <template #title>
            {{ account.offline_reason || 'Cookie已过期，请重新登录' }}
          </template>
        </el-alert>
        
        <!-- 操作按钮 -->
        <div class="account-actions">
          <el-button
            v-if="account.status === 'offline'"
            type="primary"
            :icon="RefreshRight"
            @click="relogin(account.id)"
          >
            重新登录
          </el-button>
          
          <el-button :icon="Edit" @click="editAccount(account)">
            编辑
          </el-button>
          
          <el-button
            type="danger"
            :icon="Delete"
            @click="deleteAccount(account.id)"
          >
            删除
          </el-button>
        </div>
      </el-card>
      
      <!-- 空状态 -->
      <el-empty v-if="accounts.length === 0" description="暂无账号，请添加KOOK账号" />
    </div>
    
    <!-- 添加账号对话框 -->
    <el-dialog
      v-model="addDialogVisible"
      title="添加KOOK账号"
      width="600px"
    >
      <el-form :model="newAccount" label-width="120px">
        <el-form-item label="登录方式">
          <el-radio-group v-model="newAccount.loginMethod">
            <el-radio value="password">账号密码登录</el-radio>
            <el-radio value="cookie">Cookie导入</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <template v-if="newAccount.loginMethod === 'password'">
          <el-form-item label="邮箱">
            <el-input v-model="newAccount.email" placeholder="your-email@example.com" />
          </el-form-item>
          
          <el-form-item label="密码">
            <el-input v-model="newAccount.password" type="password" show-password />
          </el-form-item>
        </template>
        
        <template v-else>
          <el-form-item label="Cookie">
            <CookieImportDragDropUltra
              @cookies-parsed="handleCookiesParsed"
              @cookies-validated="handleCookiesValidated"
            />
          </el-form-item>
        </template>
        
        <el-form-item>
          <el-alert type="info" :closable="false" show-icon>
            <template #title>
              首次登录可能需要验证码，请注意查看弹窗
            </template>
          </el-alert>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="adding"
          @click="addAccount"
        >
          添加账号
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User,
  Plus,
  OfficeBuilding,
  ChatLineSquare,
  Timer,
  Message,
  RefreshRight,
  Edit,
  Delete
} from '@element-plus/icons-vue'
import CookieImportDragDropUltra from '@/components/CookieImportDragDropUltra.vue'
import api from '@/api'

const loading = ref(false)
const accounts = ref([])
const addDialogVisible = ref(false)
const adding = ref(false)

const newAccount = ref({
  loginMethod: 'cookie',
  email: '',
  password: '',
  cookies: []
})

const loadAccounts = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/accounts/list')
    accounts.value = response.data
  } catch (error) {
    ElMessage.error('加载账号列表失败')
  } finally {
    loading.value = false
  }
}

const showAddAccountDialog = () => {
  addDialogVisible.value = true
  newAccount.value = {
    loginMethod: 'cookie',
    email: '',
    password: '',
    cookies: []
  }
}

const handleCookiesParsed = (cookies) => {
  newAccount.value.cookies = cookies
}

const handleCookiesValidated = (validation) => {
  // 验证结果处理
}

const addAccount = async () => {
  adding.value = true
  
  try {
    await api.post('/api/accounts/add', newAccount.value)
    ElMessage.success('账号添加成功')
    addDialogVisible.value = false
    await loadAccounts()
  } catch (error) {
    ElMessage.error('添加失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    adding.value = false
  }
}

const relogin = async (accountId) => {
  try {
    await api.post(`/api/accounts/${accountId}/relogin`)
    ElMessage.success('重新登录请求已发送')
    setTimeout(() => loadAccounts(), 2000)
  } catch (error) {
    ElMessage.error('重新登录失败')
  }
}

const editAccount = (account) => {
  // 编辑账号逻辑
}

const deleteAccount = async (accountId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个账号吗？', '确认删除', {
      type: 'warning'
    })
    
    await api.delete(`/api/accounts/${accountId}`)
    ElMessage.success('删除成功')
    await loadAccounts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const formatLastActive = (timestamp) => {
  if (!timestamp) return '从未活跃'
  
  const now = Date.now()
  const diff = now - new Date(timestamp).getTime()
  const minutes = Math.floor(diff / 60000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  
  const days = Math.floor(hours / 24)
  return `${days}天前`
}

onMounted(() => {
  loadAccounts()
})
</script>

<style scoped>
.accounts-enhanced {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}

.account-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.account-card {
  position: relative;
  border-radius: 16px;
  transition: all 0.3s;
}

.account-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.account-card.online {
  border-left: 4px solid #67C23A;
}

.account-card.offline {
  border-left: 4px solid #F56C6C;
}

.status-indicator {
  position: absolute;
  top: 20px;
  right: 20px;
}

.status-dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-indicator.online .status-dot {
  background: #67C23A;
}

.status-indicator.offline .status-dot {
  background: #F56C6C;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.account-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.account-info {
  flex: 1;
}

.account-email {
  margin: 0 0 10px;
  font-size: 18px;
}

.account-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin: 15px 0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 14px;
}

.warning-alert {
  margin: 15px 0;
}

.account-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 15px;
}

/* 暗黑模式 */
.dark .stat-item {
  background: #2c2c2c;
}
</style>
