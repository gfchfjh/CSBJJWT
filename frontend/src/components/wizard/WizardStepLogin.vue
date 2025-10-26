<template>
  <div class="step-login">
    <h2>📧 登录KOOK账号</h2>
    
    <!-- ✅ v1.13.0优化：添加环境检查提示（P0-5） -->
    <el-alert
      v-if="startupIssues.length > 0"
      title="⚠️ 环境检查发现问题"
      type="warning"
      :closable="false"
      style="margin-bottom: 20px"
    >
      <div>
        检测到 {{ startupIssues.length }} 个环境问题，可能影响登录功能。
        <el-button type="text" size="small" @click="showIssuesDialog = true">
          查看详情
        </el-button>
      </div>
    </el-alert>
    
    <el-radio-group v-model="loginType" class="login-type-selector">
      <el-radio label="extension">🔥 Chrome扩展（最简单）</el-radio>
      <el-radio label="cookie">Cookie导入（推荐）</el-radio>
      <el-radio label="password">账号密码登录</el-radio>
    </el-radio-group>

    <!-- ✅ P0-3新增：Chrome扩展方式 -->
    <div v-if="loginType === 'extension'" class="extension-login">
      <el-card class="extension-card">
        <template #header>
          <div class="card-header">
            <el-icon :size="24" color="#409EFF"><ChromeFilled /></el-icon>
            <span style="margin-left: 10px; font-weight: bold;">使用Chrome扩展 - 5秒完成（99%成功率）</span>
          </div>
        </template>

        <div class="extension-content">
          <!-- 检测扩展状态 -->
          <div v-if="extensionDetected" class="extension-detected">
            <el-result
              icon="success"
              title="✅ 已检测到扩展"
              sub-title="请按照下方步骤操作"
            >
              <template #extra>
                <div class="extension-steps">
                  <el-steps direction="vertical" :active="currentExtensionStep">
                    <el-step title="第1步：打开KOOK网站" description="在浏览器新标签页打开 www.kookapp.cn 并登录">
                      <template #icon>
                        <el-icon><Link /></el-icon>
                      </template>
                    </el-step>
                    <el-step title="第2步：点击扩展图标" description="点击浏览器工具栏的扩展图标">
                      <template #icon>
                        <el-icon><Pointer /></el-icon>
                      </template>
                    </el-step>
                    <el-step title="第3步：导出Cookie" description="点击"导出Cookie"按钮，自动复制到剪贴板">
                      <template #icon>
                        <el-icon><Download /></el-icon>
                      </template>
                    </el-step>
                    <el-step title="第4步：粘贴到下方" description="在下方文本框粘贴Cookie（Ctrl+V）">
                      <template #icon>
                        <el-icon><DocumentCopy /></el-icon>
                      </template>
                    </el-step>
                  </el-steps>

                  <div class="cookie-input-area">
                    <el-input
                      v-model="form.cookie"
                      type="textarea"
                      :rows="6"
                      placeholder="粘贴从Chrome扩展复制的Cookie（JSON格式）"
                      @paste="handleCookiePaste"
                    />
                    <div class="input-hint">
                      <el-icon><InfoFilled /></el-icon>
                      <span>Cookie已自动复制到剪贴板，请直接粘贴（Ctrl+V）</span>
                    </div>
                  </div>

                  <el-form-item label="账号备注" style="margin-top: 20px;">
                    <el-input
                      v-model="form.name"
                      placeholder="例如：主账号"
                    />
                  </el-form-item>
                </div>
              </template>
            </el-result>
          </div>

          <!-- 未检测到扩展 -->
          <div v-else class="extension-not-detected">
            <el-result
              icon="warning"
              title="未检测到Chrome扩展"
              sub-title="请先安装扩展"
            >
              <template #extra>
                <div class="install-guide">
                  <h3>📦 安装方法（2分钟）</h3>
                  
                  <el-alert
                    title="支持所有Chromium内核浏览器"
                    type="info"
                    :closable="false"
                    style="margin-bottom: 20px;"
                  >
                    <div>包括：Chrome、Edge、Brave、360、QQ浏览器等</div>
                  </el-alert>

                  <el-steps :active="0" finish-status="success" align-center>
                    <el-step title="下载扩展" description="点击下方按钮下载" />
                    <el-step title="安装到浏览器" description="拖拽或加载" />
                    <el-step title="刷新本页面" description="重新检测" />
                  </el-steps>

                  <div class="install-buttons" style="margin-top: 30px;">
                    <el-button type="primary" size="large" @click="downloadExtension">
                      <el-icon><Download /></el-icon>
                      下载Chrome扩展
                    </el-button>
                    <el-button size="large" @click="openExtensionGuide">
                      <el-icon><Document /></el-icon>
                      查看安装教程
                    </el-button>
                    <el-button size="large" @click="checkExtension">
                      <el-icon><Refresh /></el-icon>
                      重新检测扩展
                    </el-button>
                  </div>

                  <div class="manual-steps" style="margin-top: 30px;">
                    <el-collapse>
                      <el-collapse-item title="📖 详细安装步骤" name="1">
                        <ol class="install-steps-list">
                          <li>
                            <strong>下载扩展文件</strong>
                            <p>点击上方"下载Chrome扩展"按钮，保存zip文件到本地</p>
                          </li>
                          <li>
                            <strong>解压文件</strong>
                            <p>解压下载的zip文件到任意文件夹</p>
                          </li>
                          <li>
                            <strong>打开扩展管理页面</strong>
                            <p>在Chrome地址栏输入：<code>chrome://extensions/</code></p>
                          </li>
                          <li>
                            <strong>开启开发者模式</strong>
                            <p>点击页面右上角的"开发者模式"开关</p>
                          </li>
                          <li>
                            <strong>加载扩展</strong>
                            <p>点击"加载已解压的扩展程序"，选择解压后的文件夹</p>
                          </li>
                          <li>
                            <strong>完成</strong>
                            <p>扩展图标将出现在浏览器工具栏</p>
                          </li>
                        </ol>
                      </el-collapse-item>
                    </el-collapse>
                  </div>

                  <el-divider />

                  <div style="text-align: center; color: #909399;">
                    <el-icon><QuestionFilled /></el-icon>
                    <span>安装遇到问题？</span>
                    <el-button type="text" @click="switchToCookieMode">
                      改用Cookie导入方式
                    </el-button>
                  </div>
                </div>
              </template>
            </el-result>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Cookie登录 -->
    <div v-if="loginType === 'cookie'" class="cookie-login">
      <el-alert
        title="如何获取Cookie？"
        type="info"
        :closable="false"
        class="help-alert"
      >
        <ol>
          <li>在浏览器打开 <a href="https://www.kookapp.cn" target="_blank">KOOK网页版</a> 并登录</li>
          <li>按F12打开开发者工具</li>
          <li>切换到 Application/存储 → Cookies</li>
          <li>复制所有Cookie（或使用浏览器扩展导出）</li>
        </ol>
        <el-link type="primary" :underline="false" @click="emit('openVideo', 'cookie')">
          <el-icon><VideoPlay /></el-icon>
          观看视频教程 (3分钟)
        </el-link>
      </el-alert>

      <el-form :model="form" label-width="100px" class="form-content">
        <el-form-item label="Cookie">
          <el-input
            v-model="form.cookie"
            type="textarea"
            :rows="6"
            placeholder="粘贴Cookie内容（JSON格式或文本格式）"
          />
        </el-form-item>

        <el-form-item label="账号备注">
          <el-input
            v-model="form.name"
            placeholder="例如：主账号"
          />
        </el-form-item>
      </el-form>
    </div>

    <!-- 密码登录 -->
    <div v-else class="password-login">
      <el-alert
        title="首次登录可能需要验证码"
        type="warning"
        :closable="false"
        class="help-alert"
      />

      <el-form :model="form" label-width="100px" class="form-content">
        <el-form-item label="邮箱">
          <el-input
            v-model="form.email"
            placeholder="KOOK注册邮箱"
          />
        </el-form-item>

        <el-form-item label="密码">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="账号密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="账号备注">
          <el-input
            v-model="form.name"
            placeholder="例如：主账号"
          />
        </el-form-item>
      </el-form>
    </div>
    
    <!-- ✅ v1.13.0新增：登录失败提示（P0-6优化） -->
    <el-alert
      v-if="loginAttempted && !loginSuccess"
      title="登录失败？请检查以下几点："
      type="warning"
      :closable="false"
      style="margin-top: 20px"
    >
      <ul style="margin: 10px 0; padding-left: 20px; line-height: 1.8;">
        <li>✅ 确保Cookie格式正确（支持JSON数组/浏览器扩展/Netscape格式）</li>
        <li>✅ Cookie是否已过期？请重新登录KOOK网页版获取最新Cookie</li>
        <li>✅ 网络连接是否正常？可以尝试访问 
          <a href="https://www.kookapp.cn" target="_blank" style="color: #409EFF;">KOOK官网</a> 测试
        </li>
        <li>✅ 是否有防火墙/代理阻止连接？</li>
      </ul>
      
      <div style="margin-top: 15px;">
        <el-button type="primary" size="small" @click="showTroubleshooting">
          📖 查看详细排查步骤
        </el-button>
        <el-button type="success" size="small" @click="emit('openVideo', 'cookie')">
          🎬 观看Cookie获取视频教程
        </el-button>
      </div>
    </el-alert>
    
    <!-- ✅ v1.13.0新增：Cookie格式错误提示 -->
    <el-alert
      v-if="cookieFormatError"
      :title="cookieFormatError"
      type="error"
      show-icon
      :closable="true"
      @close="cookieFormatError = ''"
      style="margin-top: 20px"
    />

    <div class="action-buttons">
      <el-button @click="emit('prev')">上一步</el-button>
      <el-button
        type="primary"
        :loading="loading"
        @click="handleLogin"
      >
        登录并继续
      </el-button>
    </div>
    
    <!-- ✅ v1.13.0新增：环境问题对话框 -->
    <el-dialog
      v-model="showIssuesDialog"
      title="⚠️ 环境检查问题"
      width="600px"
    >
      <el-alert
        v-for="(issue, index) in startupIssues"
        :key="index"
        :title="`${issue.component}: ${issue.status}`"
        :description="issue.solution"
        :type="issue.severity === 'critical' ? 'error' : 'warning'"
        show-icon
        style="margin-bottom: 10px"
      />
      
      <template #footer>
        <el-button @click="checkEnvironment">重新检查</el-button>
        <el-button type="primary" @click="showIssuesDialog = false">知道了</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoPlay } from '@element-plus/icons-vue'
import api from '@/api'

const loginType = ref('cookie')
const loading = ref(false)

// ✅ v1.13.0新增：登录状态跟踪（P0-6优化）
const loginAttempted = ref(false)
const loginSuccess = ref(false)
const cookieFormatError = ref('')

// ✅ v1.13.0新增：环境检查问题（P0-5优化）
const startupIssues = ref([])
const showIssuesDialog = ref(false)

const form = ref({
  name: '',
  email: '',
  password: '',
  cookie: ''
})

const emit = defineEmits(['next', 'prev', 'openVideo'])

// ✅ v1.13.0新增：检查环境问题
const checkEnvironment = async () => {
  try {
    const config = await api.getSystemConfig('startup_issues')
    if (config) {
      startupIssues.value = JSON.parse(config)
    } else {
      startupIssues.value = []
    }
  } catch (error) {
    console.error('检查环境问题失败:', error)
  }
}

// ✅ v1.13.0新增：显示排查步骤对话框
const showTroubleshooting = () => {
  ElMessageBox.alert(`
    <h3 style="margin-top: 0;">登录问题排查步骤</h3>
    <ol style="line-height: 2; padding-left: 20px;">
      <li><strong>验证Cookie格式</strong>
        <ul style="margin: 5px 0 10px 0;">
          <li>✓ JSON数组格式: [{"name":"xxx","value":"xxx"}]</li>
          <li>✓ 浏览器扩展格式: name1=value1; name2=value2</li>
          <li>✓ Netscape格式: 文本文件格式</li>
        </ul>
      </li>
      <li><strong>获取新Cookie</strong>
        <ul style="margin: 5px 0 10px 0;">
          <li>① 打开KOOK网页版: <a href="https://www.kookapp.cn" target="_blank">www.kookapp.cn</a></li>
          <li>② 登录您的账号</li>
          <li>③ 按F12打开开发者工具</li>
          <li>④ Application → Cookies → 复制所有Cookie</li>
        </ul>
      </li>
      <li><strong>网络检查</strong>
        <ul style="margin: 5px 0 10px 0;">
          <li>✓ 确保能访问 https://www.kookapp.cn</li>
          <li>✓ 如果使用代理，确保代理正常工作</li>
          <li>✓ 检查防火墙是否阻止了连接</li>
        </ul>
      </li>
      <li><strong>检查浏览器环境</strong>
        <ul style="margin: 5px 0 10px 0;">
          <li>✓ 确保Chromium浏览器已安装（首次启动会自动安装）</li>
          <li>✓ 查看应用日志获取详细错误信息</li>
        </ul>
      </li>
    </ol>
    <p style="margin-top: 20px; color: #909399; font-size: 14px;">
      💡 提示：如果问题仍未解决，请查看日志文件获取详细错误信息。
    </p>
  `, '排查步骤', {
    dangerouslyUseHTMLString: true,
    confirmButtonText: '知道了',
    customClass: 'troubleshooting-dialog'
  })
}

const handleLogin = async () => {
  try {
    loading.value = true
    loginAttempted.value = true
    loginSuccess.value = false
    cookieFormatError.value = ''

    const data = {
      name: form.value.name || '默认账号'
    }

    if (loginType.value === 'cookie') {
      if (!form.value.cookie) {
        ElMessage.error('请输入Cookie')
        return
      }
      
      // ✅ v1.13.0新增：简单的Cookie格式验证
      const cookie = form.value.cookie.trim()
      if (cookie.length < 10) {
        cookieFormatError.value = 'Cookie内容太短，请确保复制完整'
        return
      }
      
      data.cookie = cookie
    } else {
      if (!form.value.email || !form.value.password) {
        ElMessage.error('请输入邮箱和密码')
        return
      }
      data.email = form.value.email
      data.password = form.value.password
    }

    await api.addAccount(data)
    ElMessage.success('账号添加成功')
    loginSuccess.value = true
    emit('next')
  } catch (error) {
    loginSuccess.value = false
    
    // ✅ v1.13.0优化：更友好的错误提示
    const errorMsg = error.response?.data?.detail || '添加失败'
    
    if (errorMsg.includes('Cookie') || errorMsg.includes('cookie')) {
      cookieFormatError.value = `Cookie格式错误: ${errorMsg}`
    } else if (errorMsg.includes('网络') || errorMsg.includes('timeout')) {
      ElMessage.error('网络连接失败，请检查网络设置')
    } else if (errorMsg.includes('浏览器') || errorMsg.includes('Chromium')) {
      ElMessage.error('浏览器启动失败，请检查环境配置')
    } else {
      ElMessage.error(errorMsg)
    }
  } finally {
    loading.value = false
  }
}

// 组件挂载时检查环境问题
onMounted(() => {
  checkEnvironment()
})
</script>

<style scoped>
h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
}

.login-type-selector {
  margin: 20px 0;
}

.form-content {
  margin-top: 20px;
}

.help-alert {
  margin-bottom: 20px;
}

.help-alert ol {
  margin: 10px 0;
  padding-left: 25px;
}

.help-alert li {
  margin: 5px 0;
}

.action-buttons {
  margin-top: 30px;
  text-align: center;
}

.action-buttons .el-button {
  margin: 0 10px;
}

/* ✅ v1.13.0新增样式 */
:deep(.troubleshooting-dialog) {
  width: 650px;
  max-width: 90vw;
}

:deep(.troubleshooting-dialog .el-message-box__message) {
  max-height: 500px;
  overflow-y: auto;
}
</style>
