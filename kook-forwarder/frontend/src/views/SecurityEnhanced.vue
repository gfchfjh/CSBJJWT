<template>
  <div class="security-enhanced">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 密码管理 -->
      <el-tab-pane label="密码管理" name="password">
        <el-form label-width="140px">
          <el-divider content-position="left">
            <el-icon><Lock /></el-icon>
            主密码设置
          </el-divider>
          
          <el-form-item label="当前密码">
            <el-input
              v-model="passwordForm.currentPassword"
              type="password"
              show-password
              placeholder="输入当前密码"
              style="width: 300px"
            />
          </el-form-item>
          
          <el-form-item label="新密码">
            <el-input
              v-model="passwordForm.newPassword"
              type="password"
              show-password
              placeholder="输入新密码（6-20位）"
              style="width: 300px"
              @input="checkPasswordStrength"
            />
          </el-form-item>
          
          <!-- 密码强度指示器（✨ P2-3核心功能） -->
          <el-form-item label="密码强度">
            <div class="password-strength">
              <el-progress
                :percentage="passwordStrength.score"
                :color="passwordStrength.color"
                :format="() => passwordStrength.text"
              />
              <ul class="strength-hints">
                <li :class="{ valid: passwordStrength.hasLength }">
                  <el-icon v-if="passwordStrength.hasLength"><CircleCheck /></el-icon>
                  <el-icon v-else><CircleClose /></el-icon>
                  长度 6-20 位
                </li>
                <li :class="{ valid: passwordStrength.hasNumber }">
                  <el-icon v-if="passwordStrength.hasNumber"><CircleCheck /></el-icon>
                  <el-icon v-else><CircleClose /></el-icon>
                  包含数字
                </li>
                <li :class="{ valid: passwordStrength.hasLetter }">
                  <el-icon v-if="passwordStrength.hasLetter"><CircleCheck /></el-icon>
                  <el-icon v-else><CircleClose /></el-icon>
                  包含字母
                </li>
                <li :class="{ valid: passwordStrength.hasSpecial }">
                  <el-icon v-if="passwordStrength.hasSpecial"><CircleCheck /></el-icon>
                  <el-icon v-else><CircleClose /></el-icon>
                  包含特殊字符（推荐）
                </li>
              </ul>
            </div>
          </el-form-item>
          
          <el-form-item label="确认新密码">
            <el-input
              v-model="passwordForm.confirmPassword"
              type="password"
              show-password
              placeholder="再次输入新密码"
              style="width: 300px"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" :loading="changingPassword" @click="changePassword">
              <el-icon><Check /></el-icon>
              更改密码
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <!-- 设备管理 -->
      <el-tab-pane label="设备管理" name="devices">
        <el-form label-width="140px">
          <el-divider content-position="left">
            <el-icon><Monitor /></el-icon>
            设备Token管理（✨ P2-3核心功能）
          </el-divider>
          
          <el-form-item label="当前设备">
            <el-tag type="success" size="large">
              <el-icon><Cpu /></el-icon>
              {{ currentDevice.name }}
            </el-tag>
            <span style="margin-left: 15px; color: #909399">
              设备ID: {{ currentDevice.id }}
            </span>
          </el-form-item>
          
          <el-form-item label="信任的设备">
            <el-table :data="trustedDevices" stripe max-height="300">
              <el-table-column label="设备" width="200">
                <template #default="{ row }">
                  <div class="device-info">
                    <el-icon :size="20"><Monitor /></el-icon>
                    <span>{{ row.name }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="os" label="操作系统" width="120" />
              <el-table-column label="最后登录" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.last_login) }}
                </template>
              </el-table-column>
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.is_current ? 'success' : 'info'" size="small">
                    {{ row.is_current ? '当前设备' : '其他设备' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button
                    v-if="!row.is_current"
                    type="danger"
                    size="small"
                    :icon="Delete"
                    @click="revokeDevice(row.id)"
                  >
                    撤销信任
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-form-item>
          
          <el-form-item>
            <el-alert type="info" :closable="false" show-icon>
              <template #title>
                提示：撤销设备信任后，该设备将无法使用"记住我30天"功能
              </template>
            </el-alert>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <!-- 审计日志 -->
      <el-tab-pane label="审计日志" name="audit">
        <div class="audit-toolbar">
          <el-input
            v-model="auditSearch"
            placeholder="搜索操作..."
            :prefix-icon="Search"
            clearable
            style="width: 300px"
          />
          
          <el-select v-model="auditFilter" style="width: 150px">
            <el-option label="全部操作" value="all" />
            <el-option label="登录" value="login" />
            <el-option label="配置变更" value="config" />
            <el-option label="删除操作" value="delete" />
          </el-select>
          
          <el-button :icon="Download" @click="exportAuditLogs">导出</el-button>
        </div>
        
        <el-table :data="filteredAuditLogs" stripe max-height="500">
          <el-table-column label="时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.timestamp) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getActionType(row.action)" size="small">
                {{ getActionText(row.action) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="description" label="操作描述" />
          
          <el-table-column label="IP地址" width="150">
            <template #default="{ row }">
              {{ row.ip_address || '-' }}
            </template>
          </el-table-column>
          
          <el-table-column label="设备" width="150">
            <template #default="{ row }">
              {{ row.device_name || '-' }}
            </template>
          </el-table-column>
        </el-table>
        
        <el-pagination
          v-model:current-page="auditPage"
          :total="filteredAuditLogs.length"
          :page-size="20"
          layout="total, prev, pager, next"
          class="pagination"
        />
      </el-tab-pane>
      
      <!-- 数据加密 -->
      <el-tab-pane label="数据加密" name="encryption">
        <el-form label-width="140px">
          <el-divider content-position="left">
            <el-icon><Key /></el-icon>
            加密设置
          </el-divider>
          
          <el-form-item label="敏感信息加密">
            <el-tag type="success" size="large">
              <el-icon><Lock /></el-icon>
              已启用 AES-256 加密
            </el-tag>
          </el-form-item>
          
          <el-form-item label="加密内容">
            <el-checkbox-group v-model="encryptedData" disabled>
              <el-checkbox value="token" label="API Token" />
              <el-checkbox value="password" label="账号密码" />
              <el-checkbox value="cookie" label="Cookie" />
              <el-checkbox value="webhook" label="Webhook URL" />
            </el-checkbox-group>
          </el-form-item>
          
          <el-form-item label="加密密钥">
            <el-input
              value="●●●●●●●●●●●●●●●●"
              readonly
              style="width: 300px"
            >
              <template #append>
                <el-button @click="showRegenerateWarning">
                  重新生成
                </el-button>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item>
            <el-alert type="warning" :closable="false" show-icon>
              <template #title>
                <strong>警告：</strong>重新生成加密密钥将导致所有已加密的数据无法解密，需要重新输入所有密码和Token！
              </template>
            </el-alert>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Lock,
  Monitor,
  Cpu,
  Delete,
  Search,
  Download,
  Key,
  Check,
  CircleCheck,
  CircleClose
} from '@element-plus/icons-vue'
import api from '@/api'

const activeTab = ref('password')
const changingPassword = ref(false)

// 密码表单
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 密码强度（✨ P2-3核心功能）
const passwordStrength = ref({
  score: 0,
  text: '未输入',
  color: '#909399',
  hasLength: false,
  hasNumber: false,
  hasLetter: false,
  hasSpecial: false
})

// 设备管理
const currentDevice = ref({
  id: '',
  name: '未知设备'
})

const trustedDevices = ref([])

// 审计日志
const auditLogs = ref([])
const auditSearch = ref('')
const auditFilter = ref('all')
const auditPage = ref(1)

// 加密数据
const encryptedData = ref(['token', 'password', 'cookie', 'webhook'])

const filteredAuditLogs = computed(() => {
  let result = [...auditLogs.value]
  
  if (auditSearch.value) {
    result = result.filter(log =>
      log.description.toLowerCase().includes(auditSearch.value.toLowerCase())
    )
  }
  
  if (auditFilter.value !== 'all') {
    result = result.filter(log => log.action === auditFilter.value)
  }
  
  return result
})

// 方法
const checkPasswordStrength = () => {
  /**
   * 检查密码强度（✨ P2-3核心功能）
   * 
   * 规则:
   * - 6-20位: 20分
   * - 包含数字: 20分
   * - 包含字母: 20分
   * - 包含大小写: 20分
   * - 包含特殊字符: 20分
   */
  const pwd = passwordForm.value.newPassword
  let score = 0
  
  // 检查长度
  passwordStrength.value.hasLength = pwd.length >= 6 && pwd.length <= 20
  if (passwordStrength.value.hasLength) score += 20
  
  // 检查数字
  passwordStrength.value.hasNumber = /\d/.test(pwd)
  if (passwordStrength.value.hasNumber) score += 20
  
  // 检查字母
  passwordStrength.value.hasLetter = /[a-zA-Z]/.test(pwd)
  if (passwordStrength.value.hasLetter) score += 20
  
  // 检查大小写
  const hasUpperLower = /[a-z]/.test(pwd) && /[A-Z]/.test(pwd)
  if (hasUpperLower) score += 20
  
  // 检查特殊字符
  passwordStrength.value.hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pwd)
  if (passwordStrength.value.hasSpecial) score += 20
  
  passwordStrength.value.score = score
  
  // 分级
  if (score >= 80) {
    passwordStrength.value.text = '强'
    passwordStrength.value.color = '#67C23A'
  } else if (score >= 60) {
    passwordStrength.value.text = '中等'
    passwordStrength.value.color = '#E6A23C'
  } else if (score >= 40) {
    passwordStrength.value.text = '弱'
    passwordStrength.value.color = '#F56C6C'
  } else {
    passwordStrength.value.text = '非常弱'
    passwordStrength.value.color = '#F56C6C'
  }
}

const changePassword = async () => {
  if (!passwordForm.value.currentPassword) {
    ElMessage.warning('请输入当前密码')
    return
  }
  
  if (!passwordForm.value.newPassword) {
    ElMessage.warning('请输入新密码')
    return
  }
  
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  
  if (passwordStrength.value.score < 40) {
    ElMessage.warning('密码强度太弱，请设置更强的密码')
    return
  }
  
  changingPassword.value = true
  
  try {
    await api.post('/api/auth/change-password', {
      current_password: passwordForm.value.currentPassword,
      new_password: passwordForm.value.newPassword
    })
    
    ElMessage.success('密码修改成功')
    
    // 清空表单
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
    
    passwordStrength.value = {
      score: 0,
      text: '未输入',
      color: '#909399',
      hasLength: false,
      hasNumber: false,
      hasLetter: false,
      hasSpecial: false
    }
  } catch (error) {
    ElMessage.error('密码修改失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    changingPassword.value = false
  }
}

const loadTrustedDevices = async () => {
  try {
    const response = await api.get('/api/auth/devices')
    trustedDevices.value = response.data.devices
    currentDevice.value = response.data.current_device
  } catch (error) {
    console.error('加载设备列表失败:', error)
  }
}

const revokeDevice = async (deviceId) => {
  try {
    await ElMessageBox.confirm(
      '确定要撤销该设备的信任吗？该设备将需要重新登录。',
      '确认撤销',
      { type: 'warning' }
    )
    
    await api.delete(`/api/auth/devices/${deviceId}`)
    ElMessage.success('已撤销设备信任')
    await loadTrustedDevices()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('撤销失败')
    }
  }
}

const loadAuditLogs = async () => {
  try {
    const response = await api.get('/api/audit/logs')
    auditLogs.value = response.data
  } catch (error) {
    console.error('加载审计日志失败:', error)
  }
}

const exportAuditLogs = () => {
  const csv = [
    ['时间', '操作类型', '操作描述', 'IP地址', '设备'],
    ...filteredAuditLogs.value.map(log => [
      formatDate(log.timestamp),
      log.action,
      log.description,
      log.ip_address || '-',
      log.device_name || '-'
    ])
  ].map(row => row.join(',')).join('\n')
  
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `audit_logs_${Date.now()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('审计日志已导出')
}

const showRegenerateWarning = async () => {
  try {
    await ElMessageBox.confirm(
      `重新生成加密密钥将导致以下后果：
      
      1. 所有已保存的密码将无法解密
      2. 所有已保存的Token将无法解密
      3. 所有已保存的Cookie将无法解密
      4. 您需要重新输入所有敏感信息
      
      确定要继续吗？`,
      '危险操作警告',
      {
        confirmButtonText: '确定重新生成',
        cancelButtonText: '取消',
        type: 'error',
        dangerouslyUseHTMLString: true
      }
    )
    
    // 如果用户确认，执行重新生成
    await api.post('/api/auth/regenerate-key')
    
    ElMessage.success('加密密钥已重新生成，请重新配置所有敏感信息')
    
    // 刷新页面
    setTimeout(() => {
      window.location.reload()
    }, 2000)
  } catch {
    // 用户取消
  }
}

const getActionType = (action) => {
  const types = {
    login: 'success',
    logout: 'info',
    config: 'warning',
    delete: 'danger'
  }
  return types[action] || 'info'
}

const getActionText = (action) => {
  const texts = {
    login: '登录',
    logout: '登出',
    config: '配置变更',
    delete: '删除操作',
    add: '添加',
    edit: '编辑'
  }
  return texts[action] || action
}

const formatDate = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadTrustedDevices()
  loadAuditLogs()
})
</script>

<style scoped>
.security-enhanced {
  padding: 20px;
}

.password-strength {
  width: 100%;
}

.strength-hints {
  list-style: none;
  padding: 15px 0 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.strength-hints li {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
}

.strength-hints li.valid {
  color: #67C23A;
}

.device-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.audit-toolbar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>
