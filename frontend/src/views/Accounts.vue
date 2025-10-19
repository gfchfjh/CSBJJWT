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
                  <span :title="formatDate(account.last_active, 'datetime')">
                    {{ formatDate(account.last_active, 'relative') }}
                  </span>
                </div>
                
                <div class="info-item">
                  <label>📅 创建时间：</label>
                  <span :title="formatDate(account.created_at, 'datetime')">
                    {{ formatDate(account.created_at, 'datetime') }}
                  </span>
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

    <!-- 添加账号对话框（v1.7.2增强版 - 带表单验证） -->
    <el-dialog
      v-model="showAddDialog"
      title="添加KOOK账号"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="accountForm" :rules="accountFormRules" ref="accountFormRef" label-width="100px">
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="accountForm.email" 
            placeholder="请输入KOOK邮箱"
            clearable
          />
          <div class="form-help-text">
            💡 这是您的KOOK注册邮箱
          </div>
        </el-form-item>
        
        <el-form-item label="登录方式">
          <el-radio-group v-model="accountForm.loginType">
            <el-radio label="cookie">Cookie导入（推荐）</el-radio>
            <el-radio label="password">账号密码</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item v-if="accountForm.loginType === 'password'" label="密码" prop="password">
          <el-input
            v-model="accountForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item v-if="accountForm.loginType === 'cookie'" label="Cookie" prop="cookie">
          <el-input
            v-model="accountForm.cookie"
            type="textarea"
            :rows="6"
            placeholder='请粘贴Cookie JSON数组，格式如：
[{"name":"token","value":"xxx","domain":".kookapp.cn"}]'
          />
          <div class="form-help-text">
            💡 <el-link type="primary" @click="openCookieTutorial">
              如何获取Cookie？查看详细教程
            </el-link>
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="handleCancelAdd">取消</el-button>
        <el-button type="primary" :loading="isAdding" @click="addAccount">
          <el-icon v-if="!isAdding"><Check /></el-icon>
          确定添加
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAccountsStore } from '../store/accounts'
import CaptchaDialog from '../components/CaptchaDialog.vue'
import { formatDate, formatRelativeTime } from '../utils/date'
import { createLoadingHelper } from '../utils/loading'
import { handleApiError, showSuccess, confirmDangerousAction } from '../utils/error'
import api from '../api'

const accountsStore = useAccountsStore()

const showAddDialog = ref(false)
const showCaptchaDialog = ref(false)
const isAdding = ref(false)
const accountFormRef = ref(null)

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

// v1.7.2新增：表单验证规则
const accountFormRules = computed(() => {
  const rules = {
    email: [
      { required: true, message: '请输入邮箱地址', trigger: 'blur' },
      { 
        type: 'email', 
        message: '请输入有效的邮箱地址', 
        trigger: ['blur', 'change'] 
      }
    ]
  }
  
  // 根据登录方式动态添加验证
  if (accountForm.value.loginType === 'password') {
    rules.password = [
      { required: true, message: '请输入密码', trigger: 'blur' },
      { min: 6, message: '密码长度至少6个字符', trigger: 'blur' }
    ]
  } else if (accountForm.value.loginType === 'cookie') {
    rules.cookie = [
      { required: true, message: '请粘贴Cookie内容', trigger: 'blur' },
      { 
        validator: (rule, value, callback) => {
          if (!value) {
            callback(new Error('Cookie不能为空'))
            return
          }
          
          // 尝试解析JSON
          try {
            const parsed = JSON.parse(value)
            
            // 检查是否为数组
            if (!Array.isArray(parsed)) {
              callback(new Error('Cookie必须是JSON数组格式'))
              return
            }
            
            // 检查是否为空数组
            if (parsed.length === 0) {
              callback(new Error('Cookie数组不能为空'))
              return
            }
            
            // 检查每个Cookie是否有name和value字段
            for (let i = 0; i < parsed.length; i++) {
              if (!parsed[i].name || !parsed[i].value) {
                callback(new Error(`Cookie[${i}]缺少name或value字段`))
                return
              }
            }
            
            callback()
          } catch (e) {
            callback(new Error('Cookie格式错误，必须是有效的JSON数组'))
          }
        },
        trigger: 'blur'
      }
    ]
  }
  
  return rules
})

const loader = createLoadingHelper()

const addAccount = async () => {
  // v1.7.2增强：先验证表单
  if (!accountFormRef.value) return
  
  try {
    await accountFormRef.value.validate()
  } catch (error) {
    ElMessage.warning('请检查表单填写是否正确')
    return
  }
  
  try {
    isAdding.value = true
    
    const data = {
      email: accountForm.value.email
    }
    
    if (accountForm.value.loginType === 'password') {
      data.password = accountForm.value.password
    } else {
      data.cookie = accountForm.value.cookie
    }
    
    await loader.wrap(
      accountsStore.addAccount(data),
      '正在添加账号...'
    )
    
    showSuccess('✅ 账号添加成功，正在连接...')
    showAddDialog.value = false
    
    // 重置表单
    accountFormRef.value?.resetFields()
    accountForm.value = {
      email: '',
      loginType: 'cookie',
      password: '',
      cookie: ''
    }
  } catch (error) {
    handleApiError(error, {
      title: '添加账号失败',
      showSolution: true
    })
  } finally {
    isAdding.value = false
  }
}

// 取消添加
const handleCancelAdd = () => {
  showAddDialog.value = false
  accountFormRef.value?.resetFields()
}

// 打开Cookie教程
const openCookieTutorial = () => {
  ElMessageBox.alert(
    '请查看帮助中心的"Cookie获取详细教程"了解如何获取KOOK Cookie',
    'Cookie获取教程',
    {
      confirmButtonText: '前往帮助中心',
      callback: () => {
        window.open('#/help', '_blank')
      }
    }
  )
}

const startAccount = async (accountId) => {
  try {
    await loader.wrap(
      accountsStore.startAccount(accountId),
      '正在启动账号...'
    )
    showSuccess('账号已启动')
  } catch (error) {
    handleApiError(error, {
      title: '启动账号失败',
      showSolution: true
    })
  }
}

const stopAccount = async (accountId) => {
  try {
    await loader.wrap(
      accountsStore.stopAccount(accountId),
      '正在停止账号...'
    )
    showSuccess('账号已停止')
  } catch (error) {
    handleApiError(error, {
      title: '停止账号失败'
    })
  }
}

const deleteAccount = async (accountId) => {
  // 确认删除
  const confirmed = await confirmDangerousAction(
    '确定要删除此账号吗？删除后无法恢复',
    {
      title: '确认删除',
      confirmButtonText: '删除',
      type: 'warning'
    }
  )
  
  if (!confirmed) return
  
  try {
    await loader.wrap(
      accountsStore.deleteAccount(accountId),
      '正在删除账号...'
    )
    showSuccess('账号已删除')
  } catch (error) {
    handleApiError(error, {
      title: '删除账号失败'
    })
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

.form-help-text {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}
</style>
