<template>
  <div class="account-login-step">
    <div class="step-header">
      <h2>🔑 第1步：连接KOOK账号</h2>
      <p>选择您喜欢的登录方式</p>
    </div>

    <el-tabs v-model="loginMethod" @tab-change="handleTabChange">
      <!-- Cookie导入（推荐） -->
      <el-tab-pane name="cookie">
        <template #label>
          <span class="custom-tab-label">
            <el-icon><Key /></el-icon>
            Cookie导入（推荐）
          </span>
        </template>

        <div class="tab-content">
          <el-alert
            title="📌 为什么推荐Cookie导入？"
            type="success"
            :closable="false"
            show-icon
          >
            <ul>
              <li>更安全：无需输入密码</li>
              <li>更快速：Chrome扩展一键导入</li>
              <li>更稳定：不会触发验证码</li>
            </ul>
          </el-alert>

          <!-- Chrome扩展导入 -->
          <div class="import-method">
            <h3>方式1：Chrome扩展自动导入（最简单）</h3>
            <el-steps :active="extensionStep" direction="vertical">
              <el-step title="安装Chrome扩展">
                <template #description>
                  <div class="step-desc">
                    <p>从Chrome网上应用店安装 "KOOK Cookie导出器"</p>
                    <el-button 
                      type="primary" 
                      size="small" 
                      @click="openExtensionStore"
                    >
                      前往安装
                    </el-button>
                    <el-button 
                      size="small" 
                      link
                      @click="showExtensionHelp"
                    >
                      查看图文教程
                    </el-button>
                  </div>
                </template>
              </el-step>

              <el-step title="登录KOOK网页版">
                <template #description>
                  <div class="step-desc">
                    <p>访问 <a href="https://www.kookapp.cn" target="_blank">www.kookapp.cn</a> 并登录</p>
                  </div>
                </template>
              </el-step>

              <el-step title="一键导出Cookie">
                <template #description>
                  <div class="step-desc">
                    <p>点击浏览器右上角的扩展图标，点击"导出Cookie"</p>
                    <p class="tip">💡 如果系统正在运行，Cookie会自动导入；否则会复制到剪贴板</p>
                  </div>
                </template>
              </el-step>
            </el-steps>

            <div class="auto-import-status" v-if="waitingForCookie">
              <el-alert
                title="🔄 等待Cookie导入中..."
                type="info"
                :closable="false"
              >
                <p>请在Chrome扩展中点击"导出Cookie"</p>
                <p>系统会自动检测并导入</p>
              </el-alert>
              <el-button @click="waitingForCookie = false">取消等待</el-button>
            </div>
            
            <el-button 
              v-else
              type="primary" 
              @click="startWaitingForCookie"
              :loading="checking"
            >
              开始等待自动导入
            </el-button>
          </div>

          <el-divider>或</el-divider>

          <!-- 手动粘贴Cookie -->
          <div class="import-method">
            <h3>方式2：手动粘贴Cookie</h3>
            <el-input
              v-model="cookieText"
              type="textarea"
              :rows="6"
              placeholder="请粘贴从Chrome扩展导出的Cookie（JSON格式）&#10;&#10;示例：&#10;[&#10;  { &quot;name&quot;: &quot;token&quot;, &quot;value&quot;: &quot;...&quot; },&#10;  { &quot;name&quot;: &quot;session&quot;, &quot;value&quot;: &quot;...&quot; }&#10;]"
            />
            
            <el-button 
              type="primary" 
              @click="handleCookieImport"
              :loading="importing"
              :disabled="!cookieText"
              style="margin-top: 15px;"
            >
              导入Cookie
            </el-button>
          </div>
        </div>
      </el-tab-pane>

      <!-- 账号密码登录 -->
      <el-tab-pane name="password">
        <template #label>
          <span class="custom-tab-label">
            <el-icon><UserFilled /></el-icon>
            账号密码登录
          </span>
        </template>

        <div class="tab-content">
          <el-alert
            title="⚠️ 注意事项"
            type="warning"
            :closable="false"
            show-icon
          >
            <ul>
              <li>首次登录可能需要验证码</li>
              <li>密码将加密存储，仅用于自动登录</li>
              <li>推荐使用Cookie导入方式</li>
            </ul>
          </el-alert>

          <el-form 
            ref="loginFormRef" 
            :model="loginForm" 
            :rules="loginRules"
            label-width="100px"
            style="margin-top: 20px;"
          >
            <el-form-item label="邮箱" prop="email">
              <el-input 
                v-model="loginForm.email" 
                placeholder="请输入KOOK账号邮箱"
                prefix-icon="Message"
              />
            </el-form-item>

            <el-form-item label="密码" prop="password">
              <el-input 
                v-model="loginForm.password" 
                type="password"
                placeholder="请输入密码"
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                @click="handlePasswordLogin"
                :loading="logging"
                style="width: 100%;"
              >
                登录
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 底部按钮 -->
    <div class="step-footer">
      <el-button @click="handlePrev">
        <el-icon><ArrowLeft /></el-icon>
        上一步
      </el-button>
      
      <el-button 
        type="primary" 
        @click="handleNext"
        :disabled="!accountConnected"
      >
        下一步
        <el-icon><ArrowRight /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Key, UserFilled, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import api from '@/api'

const emit = defineEmits(['next', 'prev'])

const loginMethod = ref('cookie')
const extensionStep = ref(0)
const waitingForCookie = ref(false)
const checking = ref(false)
const importing = ref(false)
const logging = ref(false)
const accountConnected = ref(false)

const cookieText = ref('')
const loginFormRef = ref(null)

const loginForm = reactive({
  email: '',
  password: ''
})

const loginRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

const accountData = ref(null)

const handleTabChange = (name) => {
  console.log('切换到:', name)
}

const openExtensionStore = () => {
  window.open('https://chrome.google.com/webstore', '_blank')
}

const showExtensionHelp = () => {
  // TODO: 打开教程对话框
  ElMessage.info('查看Chrome扩展安装教程')
}

const startWaitingForCookie = async () => {
  waitingForCookie.value = true
  checking.value = true
  
  // 轮询检查Cookie是否已导入
  const checkInterval = setInterval(async () => {
    try {
      const response = await api.get('/api/cookie/check-import-status')
      
      if (response.data.imported) {
        clearInterval(checkInterval)
        waitingForCookie.value = false
        checking.value = false
        accountConnected.value = true
        accountData.value = response.data.account
        ElMessage.success('✅ Cookie导入成功！')
      }
    } catch (error) {
      console.error('检查Cookie导入状态失败:', error)
    }
  }, 2000)
  
  // 60秒超时
  setTimeout(() => {
    if (waitingForCookie.value) {
      clearInterval(checkInterval)
      waitingForCookie.value = false
      checking.value = false
      ElMessage.warning('未检测到Cookie导入，请重试')
    }
  }, 60000)
}

const handleCookieImport = async () => {
  if (!cookieText.value) {
    ElMessage.error('请粘贴Cookie内容')
    return
  }
  
  importing.value = true
  
  try {
    // 验证Cookie格式
    let cookies
    try {
      cookies = JSON.parse(cookieText.value)
    } catch (e) {
      throw new Error('Cookie格式错误，请确保是有效的JSON')
    }
    
    // 导入Cookie
    const response = await api.post('/api/cookie/import', { cookies })
    
    if (response.data.success) {
      accountConnected.value = true
      accountData.value = response.data.account
      ElMessage.success('✅ Cookie导入成功！')
    } else {
      throw new Error(response.data.error || '导入失败')
    }
  } catch (error) {
    ElMessage.error('Cookie导入失败：' + error.message)
  } finally {
    importing.value = false
  }
}

const handlePasswordLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    logging.value = true
    
    try {
      const response = await api.post('/api/accounts/login', {
        email: loginForm.email,
        password: loginForm.password
      })
      
      if (response.data.success) {
        accountConnected.value = true
        accountData.value = response.data.account
        ElMessage.success('✅ 登录成功！')
      } else {
        throw new Error(response.data.error || '登录失败')
      }
    } catch (error) {
      ElMessage.error('登录失败：' + error.message)
    } finally {
      logging.value = false
    }
  })
}

const handlePrev = () => {
  emit('prev')
}

const handleNext = () => {
  if (!accountConnected.value) {
    ElMessage.warning('请先完成账号连接')
    return
  }
  
  emit('next', accountData.value)
}
</script>

<style scoped>
.account-login-step {
  max-width: 800px;
  margin: 0 auto;
}

.step-header {
  text-align: center;
  margin-bottom: 30px;
}

.step-header h2 {
  font-size: 24px;
  color: #303133;
  margin: 0 0 10px 0;
}

.step-header p {
  color: #909399;
  font-size: 14px;
}

.custom-tab-label {
  display: flex;
  align-items: center;
  gap: 5px;
}

.tab-content {
  padding: 20px;
}

.tab-content :deep(.el-alert) {
  margin-bottom: 20px;
}

.tab-content ul {
  margin: 10px 0 0 0;
  padding-left: 20px;
}

.tab-content li {
  margin: 5px 0;
  color: #606266;
}

.import-method {
  margin: 30px 0;
}

.import-method h3 {
  font-size: 16px;
  color: #303133;
  margin-bottom: 15px;
}

.step-desc {
  padding: 10px 0;
}

.step-desc p {
  margin: 5px 0;
  color: #606266;
}

.step-desc a {
  color: #409EFF;
  text-decoration: none;
}

.step-desc .tip {
  font-size: 13px;
  color: #909399;
}

.auto-import-status {
  margin: 20px 0;
  text-align: center;
}

.auto-import-status :deep(.el-alert) {
  margin-bottom: 15px;
}

.step-footer {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #DCDFE6;
  display: flex;
  justify-content: space-between;
}
</style>
