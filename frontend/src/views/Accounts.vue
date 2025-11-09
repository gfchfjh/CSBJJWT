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
                
                <!-- ✅ P1-6优化: 监听服务器数量显示 -->
                <div class="info-item">
                  <label>📡 监听服务器：</label>
                  <span>
                    <el-tag type="info" size="small">
                      {{ account.monitored_servers || 0 }} 个
                    </el-tag>
                    <el-button
                      v-if="account.monitored_servers > 0"
                      link
                      type="primary"
                      size="small"
                      @click="viewServerDetails(account.id)"
                      style="margin-left: 5px;"
                    >
                      查看详情
                    </el-button>
                  </span>
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
            v-if="account.status === 'offline'"
            type="warning"
            size="small"
            @click="showUpdateCookieDialog(account)"
          >
            更新Cookie
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
          <!-- Cookie导入方式选择 -->
          <el-radio-group v-model="cookieImportMethod" size="small" style="margin-bottom: 10px">
            <el-radio-button label="paste">粘贴文本</el-radio-button>
            <el-radio-button label="file">上传文件</el-radio-button>
          </el-radio-group>
          
          <!-- 方式1：粘贴文本 -->
          <el-input
            v-if="cookieImportMethod === 'paste'"
            v-model="accountForm.cookie"
            type="textarea"
            :rows="8"
            :placeholder="cookiePlaceholder"
          />
          
          <!-- v1.12.0+ 新增：Cookie格式帮助 -->
          <el-collapse v-if="cookieImportMethod === 'paste'" style="margin-top: 10px">
            <el-collapse-item title="📖 支持的Cookie格式说明（点击展开）" name="1">
              <div class="format-examples">
                <el-alert
                  title="✨ v1.12.0新特性：自动识别多种Cookie格式"
                  type="success"
                  :closable="false"
                  show-icon
                  style="margin-bottom: 15px"
                >
                  无需担心格式，程序会自动识别并转换！
                </el-alert>
                
                <h4>✅ 格式1: JSON数组（推荐）</h4>
                <el-input
                  type="textarea"
                  :rows="2"
                  readonly
                  value='[{"name":"token","value":"abc123","domain":".kookapp.cn"}]'
                />
                
                <h4>✅ 格式2: Netscape格式（浏览器扩展导出）</h4>
                <el-input
                  type="textarea"
                  :rows="3"
                  readonly
                  value='# Netscape HTTP Cookie File
.kookapp.cn	TRUE	/	FALSE	1234567890	token	abc123
.kookapp.cn	TRUE	/	FALSE	1234567890	session	xyz789'
                />
                
                <h4>✅ 格式3: 键值对格式（最简单）</h4>
                <el-input
                  type="textarea"
                  :rows="1"
                  readonly
                  value='token=abc123; session=xyz789; user_id=12345'
                />
                
                <h4>✅ 格式4: 开发者工具格式（制表符分隔）</h4>
                <el-input
                  type="textarea"
                  :rows="2"
                  readonly
                  value='token	abc123	.kookapp.cn	/
session	xyz789	.kookapp.cn	/'
                />
              </div>
            </el-collapse-item>
          </el-collapse>
          
          <!-- 方式2：上传文件 -->
          <el-upload
            v-if="cookieImportMethod === 'file'"
            class="cookie-upload"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleCookieFileChange"
            :file-list="cookieFileList"
            accept=".json,.txt"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将Cookie文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 .json 和 .txt 文件，文件大小不超过1MB
              </div>
            </template>
          </el-upload>
          
          <!-- Cookie格式检测结果 -->
          <el-alert
            v-if="cookieValidationResult"
            :title="cookieValidationResult.title"
            :type="cookieValidationResult.type"
            :closable="false"
            style="margin-top: 10px"
          >
            <div v-if="cookieValidationResult.details">
              <p>{{ cookieValidationResult.details }}</p>
              <ul v-if="cookieValidationResult.items" style="margin: 5px 0; padding-left: 20px;">
                <li v-for="(item, index) in cookieValidationResult.items" :key="index">
                  {{ item }}
                </li>
              </ul>
            </div>
          </el-alert>
          
          <div class="form-help-text">
            💡 <el-link type="primary" @click="openCookieTutorial">
              如何获取Cookie？查看详细教程
            </el-link>
            <el-divider direction="vertical" />
            <el-link type="primary" @click="showCookieFormatHelp">
              支持的Cookie格式说明
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

  <!-- 更新Cookie对话框 -->
  <el-dialog
    v-model="updateCookieDialogVisible"
    title="更新Cookie"
    width="600px"
  >
    <el-form :model="updateCookieForm" label-width="100px">
      <el-form-item label="账号">
        <el-input v-model="updateCookieForm.email" disabled />
      </el-form-item>
      <el-form-item label="Cookie">
        <el-input
          v-model="updateCookieForm.cookie"
          type="textarea"
          :rows="6"
          placeholder="请粘贴从浏览器导出的Cookie（JSON格式）"
        />
      </el-form-item>
      <el-form-item>
        <el-alert
          title="提示：在KOOK网页登录后，在浏览器Console执行以下代码获取Cookie"
          type="info"
          :closable="false"
        >
          <template #default>
            <pre style="font-size: 12px; margin: 10px 0;">copy(JSON.stringify(document.cookie.split("; ").map(c => {
  let [name, ...v] = c.split("=");
  return {name, value: v.join("="), domain: ".kookapp.cn", 
          path: "/", secure: true, sameSite: "None"};
})))</pre>
          </template>
        </el-alert>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="updateCookieDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="updateCookie" :loading="updating">
        更新Cookie
      </el-button>
    </template>
  </el-dialog>

</template>

<script setup>
import axios from 'axios'
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

// Cookie导入相关
const cookieImportMethod = ref('paste') // 'paste' | 'file'
const cookieFileList = ref([])
const cookieValidationResult = ref(null)

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

// Cookie文件上传处理
const handleCookieFileChange = (file, fileList) => {
  cookieFileList.value = fileList
  
  if (file.raw) {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const content = e.target.result
        const parsed = parseCookieContent(content)
        
        if (parsed.success) {
          accountForm.value.cookie = JSON.stringify(parsed.cookies, null, 2)
          cookieValidationResult.value = {
            type: 'success',
            title: '✅ Cookie文件解析成功',
            details: `共解析出 ${parsed.cookies.length} 个Cookie`,
            items: parsed.cookies.map(c => `${c.name} (${c.domain || '无域名'})`)
          }
        } else {
          cookieValidationResult.value = {
            type: 'error',
            title: '❌ Cookie文件解析失败',
            details: parsed.error
          }
        }
      } catch (error) {
        cookieValidationResult.value = {
          type: 'error',
          title: '❌ 文件读取失败',
          details: error.message
        }
      }
    }
    reader.readAsText(file.raw)
  }
}

// 解析Cookie内容（支持多种格式）
const parseCookieContent = (content) => {
  try {
    // 尝试JSON格式
    const jsonParsed = JSON.parse(content)
    
    // 如果是数组，直接返回
    if (Array.isArray(jsonParsed)) {
      return { success: true, cookies: jsonParsed }
    }
    
    // 如果是对象，看看是否是浏览器扩展格式
    if (jsonParsed.cookies && Array.isArray(jsonParsed.cookies)) {
      return { success: true, cookies: jsonParsed.cookies }
    }
    
    return {
      success: false,
      error: 'JSON格式不正确，应该是Cookie数组'
    }
  } catch (e) {
    // 尝试Netscape格式（每行一个Cookie）
    const lines = content.split('\n')
    const cookies = []
    
    for (const line of lines) {
      const trimmed = line.trim()
      // 跳过注释和空行
      if (!trimmed || trimmed.startsWith('#')) continue
      
      // Netscape格式：domain\tflag\tpath\tsecure\texpiration\tname\tvalue
      const parts = trimmed.split('\t')
      if (parts.length >= 7) {
        cookies.push({
          name: parts[5],
          value: parts[6],
          domain: parts[0],
          path: parts[2],
          secure: parts[3] === 'TRUE',
          httpOnly: false
        })
      }
    }
    
    if (cookies.length > 0) {
      return { success: true, cookies }
    }
    
    return {
      success: false,
      error: '无法识别的Cookie格式。支持的格式：JSON数组、Netscape格式'
    }
  }
}

// 显示Cookie格式帮助
const showCookieFormatHelp = () => {
  ElMessageBox.alert(`
    <div style="text-align: left;">
      <h3>支持的Cookie格式</h3>
      
      <h4>1. JSON数组格式（推荐）</h4>
      <pre style="background: #f5f7fa; padding: 10px; border-radius: 4px;">
[
  {
    "name": "token",
    "value": "your_token_value",
    "domain": ".kookapp.cn",
    "path": "/",
    "secure": true
  }
]</pre>
      
      <h4>2. 浏览器扩展导出格式</h4>
      <pre style="background: #f5f7fa; padding: 10px; border-radius: 4px;">
{
  "cookies": [
    {"name": "token", "value": "xxx", ...}
  ]
}</pre>
      
      <h4>3. Netscape格式</h4>
      <pre style="background: #f5f7fa; padding: 10px; border-radius: 4px;">
# Netscape HTTP Cookie File
.kookapp.cn  TRUE  /  TRUE  0  token  value</pre>
      
      <p style="color: #909399; margin-top: 15px;">
        💡 推荐使用浏览器扩展（如EditThisCookie）直接导出JSON格式
      </p>
    </div>
  `, 'Cookie格式说明', {
    dangerouslyUseHTMLString: true,
    confirmButtonText: '关闭'
  })
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

// ✅ P1-6优化: 查看服务器详情
const viewServerDetails = async (accountId) => {
  try {
    const response = await axios.get(`/api/accounts/${accountId}/servers`)
    
    if (response.data.success) {
      const servers = response.data.servers || []
      const serverNames = servers.map(s => s.name).join('、')
      
      ElMessageBox.alert(
        `<div style="max-height: 400px; overflow-y: auto;">
          <p><strong>监听的服务器列表：</strong></p>
          <ul style="margin: 10px 0; padding-left: 20px;">
            ${servers.map(s => `
              <li style="margin: 5px 0;">
                <strong>${s.name}</strong> 
                (${s.channels?.length || 0} 个频道)
              </li>
            `).join('')}
          </ul>
        </div>`,
        '服务器详情',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '知道了'
        }
      )
    }
  } catch (error) {
    console.error('获取服务器详情失败:', error)
    ElMessage.error('获取服务器详情失败')
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

const updateCookieDialogVisible = ref(false)
const updateCookieForm = ref({ accountId: null, email: '', cookie: '' })
const updating = ref(false)

const showUpdateCookieDialog = (account) => {
  console.log('Update Cookie clicked', account)
  updateCookieForm.value = { accountId: account.id, email: account.email, cookie: '' }
  updateCookieDialogVisible.value = true
}

const updateCookie = async () => {
  if (!updateCookieForm.value.cookie) { ElMessage.warning('请输入Cookie'); return }
  try {
    updating.value = true
    await axios.put('http://localhost:9527/api/accounts/' + updateCookieForm.value.accountId + '/cookie', { 
      email: updateCookieForm.value.email,
      cookie: updateCookieForm.value.cookie 
    })
    ElMessage.success('Cookie更新成功')
    updateCookieDialogVisible.value = false
    // 刷新页面以显示更新
    setTimeout(() => window.location.reload(), 500)
  } catch (error) {
    console.error(error)
    ElMessage.error(error.response?.data?.detail || '更新失败')
  } finally {
    updating.value = false
  }
}

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
