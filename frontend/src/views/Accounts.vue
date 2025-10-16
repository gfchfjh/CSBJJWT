<template>
  <div class="accounts-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>👤 KOOK账号管理</span>
          <el-button type="primary" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon>
            添加账号
          </el-button>
        </div>
      </template>
      
      <div class="accounts-list">
        <el-empty v-if="accountsStore.accounts.length === 0" description="暂无账号，请添加" />
        
        <el-row :gutter="20" v-else>
          <el-col :span="12" v-for="account in accountsStore.accounts" :key="account.id">
            <el-card class="account-card">
              <div class="account-header">
                <el-tag :type="account.status === 'online' ? 'success' : 'danger'" size="large">
                  {{ account.status === 'online' ? '🟢 在线' : '🔴 离线' }}
                </el-tag>
              </div>
              
              <div class="account-info">
                <div class="info-item">
                  <label>📧 邮箱：</label>
                  <span>{{ account.email }}</span>
                </div>
                
                <div class="info-item">
                  <label>🕐 最后活跃：</label>
                  <span>{{ account.last_active || '从未' }}</span>
                </div>
                
                <div class="info-item">
                  <label>📅 创建时间：</label>
                  <span>{{ account.created_at }}</span>
                </div>
              </div>
              
              <div class="account-actions">
                <el-button
                  v-if="account.status === 'offline'"
                  type="success"
                  size="small"
                  @click="startAccount(account.id)"
                >
                  <el-icon><VideoPlay /></el-icon>
                  启动
                </el-button>
                
                <el-button
                  v-else
                  type="warning"
                  size="small"
                  @click="stopAccount(account.id)"
                >
                  <el-icon><VideoPause /></el-icon>
                  停止
                </el-button>
                
                <el-button
                  type="danger"
                  size="small"
                  @click="deleteAccount(account.id)"
                >
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>
    
    <!-- 验证码输入对话框 -->
    <CaptchaDialog
      v-model:visible="showCaptchaDialog"
      :account-id="captchaData.accountId"
      :image-url="captchaData.imageUrl"
      :timestamp="captchaData.timestamp"
      @submit="handleCaptchaSubmit"
    />

    <!-- 添加账号对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="添加KOOK账号"
      width="500px"
    >
      <el-form :model="accountForm" label-width="100px">
        <el-form-item label="邮箱">
          <el-input v-model="accountForm.email" placeholder="请输入KOOK邮箱" />
        </el-form-item>
        
        <el-form-item label="登录方式">
          <el-radio-group v-model="accountForm.loginType">
            <el-radio label="cookie">Cookie导入</el-radio>
            <el-radio label="password">账号密码</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item v-if="accountForm.loginType === 'password'" label="密码">
          <el-input
            v-model="accountForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item v-if="accountForm.loginType === 'cookie'" label="Cookie">
          <el-input
            v-model="accountForm.cookie"
            type="textarea"
            :rows="4"
            placeholder="请粘贴Cookie JSON或文本"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addAccount">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAccountsStore } from '../store/accounts'
import { ElMessage, ElMessageBox } from 'element-plus'
import CaptchaDialog from '../components/CaptchaDialog.vue'
import api from '../api'

const accountsStore = useAccountsStore()

const showAddDialog = ref(false)
const showCaptchaDialog = ref(false)

const accountForm = ref({
  email: '',
  loginType: 'cookie',
  password: '',
  cookie: ''
})

const captchaData = ref({
  accountId: 0,
  imageUrl: '',
  timestamp: 0
})

const addAccount = async () => {
  try {
    const data = {
      email: accountForm.value.email
    }
    
    if (accountForm.value.loginType === 'password') {
      data.password = accountForm.value.password
    } else {
      data.cookie = accountForm.value.cookie
    }
    
    await accountsStore.addAccount(data)
    ElMessage.success('账号添加成功')
    showAddDialog.value = false
    
    // 重置表单
    accountForm.value = {
      email: '',
      loginType: 'cookie',
      password: '',
      cookie: ''
    }
  } catch (error) {
    ElMessage.error('添加失败: ' + error.message)
  }
}

const startAccount = async (accountId) => {
  try {
    await accountsStore.startAccount(accountId)
    ElMessage.success('账号已启动')
  } catch (error) {
    ElMessage.error('启动失败: ' + error.message)
  }
}

const stopAccount = async (accountId) => {
  try {
    await accountsStore.stopAccount(accountId)
    ElMessage.success('账号已停止')
  } catch (error) {
    ElMessage.error('停止失败: ' + error.message)
  }
}

const deleteAccount = async (accountId) => {
  try {
    await ElMessageBox.confirm('确定要删除此账号吗？', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await accountsStore.deleteAccount(accountId)
    ElMessage.success('账号已删除')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

const handleCaptchaSubmit = (code) => {
  console.log('验证码已提交:', code)
  ElMessage.success('验证码已提交，请等待登录完成')
}

// 验证码轮询
let captchaCheckInterval = null

// 检查验证码状态
const checkCaptchaStatus = async () => {
  try {
    // 遍历所有账号，检查是否需要验证码
    for (const account of accountsStore.accounts) {
      try {
        const response = await api.getCaptchaStatus(account.id)
        
        if (response && response.required) {
          // 显示验证码对话框
          captchaData.value = {
            accountId: account.id,
            imageUrl: response.image_url,
            timestamp: response.timestamp
          }
          showCaptchaDialog.value = true
          break // 一次只处理一个验证码
        }
      } catch (error) {
        // 单个账号检查失败不影响其他账号
        console.debug(`账号${account.id}验证码检查失败:`, error)
      }
    }
  } catch (error) {
    console.error('检查验证码状态失败:', error)
  }
}

onMounted(async () => {
  await accountsStore.fetchAccounts()
  
  // 开始轮询验证码状态（每3秒检查一次）
  captchaCheckInterval = setInterval(checkCaptchaStatus, 3000)
  
  // 立即检查一次
  await checkCaptchaStatus()
})

onUnmounted(() => {
  // 清理轮询
  if (captchaCheckInterval) {
    clearInterval(captchaCheckInterval)
  }
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.accounts-list {
  min-height: 300px;
}

.account-card {
  margin-bottom: 20px;
}

.account-header {
  margin-bottom: 16px;
}

.account-info {
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  margin-bottom: 8px;
}

.info-item label {
  min-width: 100px;
  color: #909399;
}

.account-actions {
  display: flex;
  gap: 8px;
}
</style>
