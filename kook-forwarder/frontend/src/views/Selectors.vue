<template>
  <div class="selectors-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <div>
            <span>🔍 选择器配置</span>
            <el-tag type="info" size="small" style="margin-left: 10px">高级功能</el-tag>
          </div>
          <div>
            <el-button @click="refreshSelectors" :loading="loading">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
            <el-button type="primary" @click="saveSelectors" :loading="saving">
              <el-icon><Check /></el-icon> 保存配置
            </el-button>
          </div>
        </div>
      </template>

      <!-- 说明提示 -->
      <el-alert
        title="什么是选择器配置？"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <p>选择器配置用于定位KOOK网页中的DOM元素。当KOOK网页结构发生变化时，您可以通过修改选择器来适配新的页面结构。</p>
        <p style="margin-top: 10px">
          <strong>注意：</strong>此功能面向技术用户。如果您不了解CSS选择器，建议使用默认配置，或等待官方更新。
        </p>
      </el-alert>

      <!-- 选择器分类标签页 -->
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 服务器相关选择器 -->
        <el-tab-pane label="🏠 服务器选择器" name="server">
          <el-form label-width="200px">
            <el-form-item label="服务器列表容器">
              <el-select
                v-model="selectors.server_container"
                multiple
                filterable
                allow-create
                placeholder="请输入CSS选择器"
                style="width: 100%"
              >
                <el-option
                  v-for="item in defaultSelectors.server_container"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
              <span class="help-text">
                用于定位服务器列表的容器元素，支持多个备选选择器
              </span>
            </el-form-item>

            <el-form-item label="服务器项">
              <el-select
                v-model="selectors.server_item"
                multiple
                filterable
                allow-create
                placeholder="请输入CSS选择器"
                style="width: 100%"
              >
                <el-option
                  v-for="item in defaultSelectors.server_item"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
              <span class="help-text">
                用于定位单个服务器项的选择器
              </span>
            </el-form-item>

            <el-form-item label="服务器名称">
              <el-select
                v-model="selectors.server_name"
                multiple
                filterable
                allow-create
                placeholder="请输入CSS选择器"
                style="width: 100%"
              >
                <el-option
                  v-for="item in defaultSelectors.server_name"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
              <span class="help-text">
                用于提取服务器名称的选择器
              </span>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 频道相关选择器 -->
        <el-tab-pane label="💬 频道选择器" name="channel">
          <el-form label-width="200px">
            <el-form-item label="频道列表容器">
              <el-select
                v-model="selectors.channel_container"
                multiple
                filterable
                allow-create
                placeholder="请输入CSS选择器"
                style="width: 100%"
              >
                <el-option
                  v-for="item in defaultSelectors.channel_container"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
              <span class="help-text">
                用于定位频道列表的容器元素
              </span>
            </el-form-item>

            <el-form-item label="频道项">
              <el-select
                v-model="selectors.channel_item"
                multiple
                filterable
                allow-create
                placeholder="请输入CSS选择器"
                style="width: 100%"
              >
                <el-option
                  v-for="item in defaultSelectors.channel_item"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
              <span class="help-text">
                用于定位单个频道项的选择器
              </span>
            </el-form-item>

            <el-form-item label="频道名称">
              <el-select
                v-model="selectors.channel_name"
                multiple
                filterable
                allow-create
                placeholder="请输入CSS选择器"
                style="width: 100%"
              >
                <el-option
                  v-for="item in defaultSelectors.channel_name"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
              <span class="help-text">
                用于提取频道名称的选择器
              </span>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 登录相关选择器 -->
        <el-tab-pane label="🔐 登录选择器" name="login">
          <el-form label-width="200px">
            <el-form-item label="邮箱输入框">
              <el-select
                v-model="selectors.login_email_input"
                multiple
                filterable
                allow-create
                placeholder="请输入CSS选择器"
                style="width: 100%"
              >
                <el-option
                  v-for="item in defaultSelectors.login_email_input"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
              <span class="help-text">
                用于定位登录页面的邮箱输入框
              </span>
            </el-form-item>

            <el-form-item label="密码输入框">
              <el-select
                v-model="selectors.login_password_input"
                multiple
                filterable
                allow-create
                placeholder="请输入CSS选择器"
                style="width: 100%"
              >
                <el-option
                  v-for="item in defaultSelectors.login_password_input"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
              <span class="help-text">
                用于定位登录页面的密码输入框
              </span>
            </el-form-item>

            <el-form-item label="登录按钮">
              <el-select
                v-model="selectors.login_submit_button"
                multiple
                filterable
                allow-create
                placeholder="请输入CSS选择器"
                style="width: 100%"
              >
                <el-option
                  v-for="item in defaultSelectors.login_submit_button"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
              <span class="help-text">
                用于定位登录按钮
              </span>
            </el-form-item>

            <el-form-item label="验证码输入框">
              <el-select
                v-model="selectors.captcha_input"
                multiple
                filterable
                allow-create
                placeholder="请输入CSS选择器"
                style="width: 100%"
              >
                <el-option
                  v-for="item in defaultSelectors.captcha_input"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
              <span class="help-text">
                用于定位验证码输入框
              </span>
            </el-form-item>

            <el-form-item label="验证码图片">
              <el-select
                v-model="selectors.captcha_image"
                multiple
                filterable
                allow-create
                placeholder="请输入CSS选择器"
                style="width: 100%"
              >
                <el-option
                  v-for="item in defaultSelectors.captcha_image"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
              <span class="help-text">
                用于定位验证码图片
              </span>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 用户信息选择器 -->
        <el-tab-pane label="👤 用户信息选择器" name="user">
          <el-form label-width="200px">
            <el-form-item label="用户面板">
              <el-select
                v-model="selectors.user_panel"
                multiple
                filterable
                allow-create
                placeholder="请输入CSS选择器"
                style="width: 100%"
              >
                <el-option
                  v-for="item in defaultSelectors.user_panel"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
              <span class="help-text">
                用于定位用户信息面板（检查登录状态）
              </span>
            </el-form-item>

            <el-form-item label="用户头像">
              <el-select
                v-model="selectors.user_avatar"
                multiple
                filterable
                allow-create
                placeholder="请输入CSS选择器"
                style="width: 100%"
              >
                <el-option
                  v-for="item in defaultSelectors.user_avatar"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
              <span class="help-text">
                用于定位用户头像元素
              </span>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <!-- 操作按钮区 -->
      <div style="margin-top: 20px; text-align: right">
        <el-button @click="resetToDefault">
          <el-icon><RefreshLeft /></el-icon> 恢复默认
        </el-button>
        <el-button type="warning" @click="testSelectors" :loading="testing">
          <el-icon><View /></el-icon> 测试选择器
        </el-button>
        <el-button type="primary" @click="saveSelectors" :loading="saving">
          <el-icon><Check /></el-icon> 保存配置
        </el-button>
      </div>
    </el-card>

    <!-- 帮助对话框 -->
    <el-dialog v-model="helpVisible" title="📖 选择器配置帮助" width="700px">
      <div class="help-content">
        <h3>什么是CSS选择器？</h3>
        <p>CSS选择器是用于在网页中定位HTML元素的模式。例如：</p>
        <ul>
          <li><code>.class-name</code> - 通过类名定位</li>
          <li><code>#element-id</code> - 通过ID定位</li>
          <li><code>div.container</code> - div元素且有container类</li>
          <li><code>[data-id="123"]</code> - 通过data属性定位</li>
        </ul>

        <h3>如何获取正确的选择器？</h3>
        <ol>
          <li>打开KOOK网页版（https://www.kookapp.cn/app）</li>
          <li>按F12打开开发者工具</li>
          <li>点击左上角的元素选择器图标</li>
          <li>点击要定位的网页元素</li>
          <li>在开发者工具中右键该元素 → Copy → Copy selector</li>
          <li>粘贴到本配置页面即可</li>
        </ol>

        <h3>为什么支持多个选择器？</h3>
        <p>
          当KOOK网页更新时，某些选择器可能失效。通过配置多个备选选择器，
          程序会依次尝试，提高适配成功率。
        </p>

        <h3>测试选择器功能</h3>
        <p>
          点击"测试选择器"按钮后，程序会在真实的KOOK页面中尝试使用您配置的选择器。
          测试结果会显示哪些选择器有效，哪些失效。
        </p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Check, RefreshLeft, View } from '@element-plus/icons-vue'
import api from '@/api'

const activeTab = ref('server')
const loading = ref(false)
const saving = ref(false)
const testing = ref(false)
const helpVisible = ref(false)

// 当前选择器配置
const selectors = reactive({
  // 服务器相关
  server_container: [],
  server_item: [],
  server_name: [],
  
  // 频道相关
  channel_container: [],
  channel_item: [],
  channel_name: [],
  
  // 登录相关
  login_email_input: [],
  login_password_input: [],
  login_submit_button: [],
  captcha_input: [],
  captcha_image: [],
  
  // 用户信息
  user_panel: [],
  user_avatar: []
})

// 默认选择器（用于选项提示和重置）
const defaultSelectors = {
  server_container: [
    '.guild-list',
    '[class*="guild-list"]',
    '[class*="GuildList"]',
    '[data-guild-list]'
  ],
  server_item: [
    '.guild-item',
    '[class*="guild-item"]',
    '[class*="GuildItem"]',
    '[data-guild-id]'
  ],
  server_name: [
    '.guild-name',
    '[class*="guild-name"]',
    '[class*="name"]'
  ],
  channel_container: [
    '.channel-list',
    '[class*="channel-list"]',
    '[class*="ChannelList"]',
    'nav[class*="channel"]'
  ],
  channel_item: [
    '.channel-item',
    '[class*="channel-item"]',
    '[class*="ChannelItem"]',
    '[data-channel-id]'
  ],
  channel_name: [
    '.channel-name',
    '[class*="channel-name"]',
    '[class*="name"]'
  ],
  login_email_input: [
    'input[type="email"]',
    'input[name="email"]',
    'input[placeholder*="邮箱"]'
  ],
  login_password_input: [
    'input[type="password"]',
    'input[name="password"]'
  ],
  login_submit_button: [
    'button[type="submit"]',
    'button[class*="login"]',
    '.login-button'
  ],
  captcha_input: [
    'input[name="captcha"]',
    'input[placeholder*="验证码"]',
    '.captcha-input'
  ],
  captcha_image: [
    'img.captcha-image',
    'img[alt*="验证码"]',
    '.captcha-container img'
  ],
  user_panel: [
    '.user-panel',
    '[data-user-info]',
    '.current-user',
    '.user-avatar'
  ],
  user_avatar: [
    '.user-avatar img',
    '[class*="avatar"] img',
    '.current-user img'
  ]
}

// 加载选择器配置
const loadSelectors = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/selectors')
    if (response.data.success) {
      Object.assign(selectors, response.data.data)
    }
  } catch (error) {
    console.error('加载选择器配置失败:', error)
    ElMessage.error('加载选择器配置失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 刷新配置
const refreshSelectors = () => {
  loadSelectors()
}

// 保存选择器配置
const saveSelectors = async () => {
  // 验证至少每个类别有一个选择器
  const requiredFields = [
    'server_container',
    'server_item',
    'channel_container',
    'channel_item'
  ]
  
  for (const field of requiredFields) {
    if (!selectors[field] || selectors[field].length === 0) {
      ElMessage.warning(`请至少为"${getFieldLabel(field)}"配置一个选择器`)
      return
    }
  }

  saving.value = true
  try {
    const response = await api.post('/api/selectors', selectors)
    if (response.data.success) {
      ElMessage.success('选择器配置已保存')
    }
  } catch (error) {
    console.error('保存选择器配置失败:', error)
    ElMessage.error('保存失败: ' + (error.response?.data?.message || error.message))
  } finally {
    saving.value = false
  }
}

// 恢复默认配置
const resetToDefault = () => {
  ElMessageBox.confirm(
    '确定要恢复默认选择器配置吗？当前配置将被覆盖。',
    '确认恢复',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    Object.keys(defaultSelectors).forEach(key => {
      selectors[key] = [...defaultSelectors[key]]
    })
    ElMessage.success('已恢复为默认配置，请点击"保存配置"按钮')
  }).catch(() => {
    // 取消操作
  })
}

// 测试选择器
const testSelectors = async () => {
  testing.value = true
  try {
    const response = await api.post('/api/selectors/test', selectors)
    if (response.data.success) {
      const results = response.data.data
      
      // 显示测试结果
      let successCount = 0
      let failCount = 0
      let details = []
      
      Object.keys(results).forEach(key => {
        const result = results[key]
        if (result.success) {
          successCount++
          details.push(`✅ ${getFieldLabel(key)}: ${result.matched_selector}`)
        } else {
          failCount++
          details.push(`❌ ${getFieldLabel(key)}: ${result.error}`)
        }
      })
      
      ElMessageBox.alert(
        `<div style="max-height: 400px; overflow-y: auto;">
          <p><strong>测试完成！</strong></p>
          <p>成功: ${successCount}个，失败: ${failCount}个</p>
          <hr>
          <div style="text-align: left; font-family: monospace; font-size: 12px;">
            ${details.join('<br>')}
          </div>
        </div>`,
        '选择器测试结果',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '关闭'
        }
      )
    }
  } catch (error) {
    console.error('测试选择器失败:', error)
    ElMessage.error('测试失败: ' + (error.response?.data?.message || error.message))
  } finally {
    testing.value = false
  }
}

// 获取字段标签（用于提示）
const getFieldLabel = (field) => {
  const labels = {
    server_container: '服务器列表容器',
    server_item: '服务器项',
    server_name: '服务器名称',
    channel_container: '频道列表容器',
    channel_item: '频道项',
    channel_name: '频道名称',
    login_email_input: '邮箱输入框',
    login_password_input: '密码输入框',
    login_submit_button: '登录按钮',
    captcha_input: '验证码输入框',
    captcha_image: '验证码图片',
    user_panel: '用户面板',
    user_avatar: '用户头像'
  }
  return labels[field] || field
}

onMounted(() => {
  loadSelectors()
})
</script>

<style scoped>
.selectors-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.help-text {
  display: block;
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}

.help-content h3 {
  margin-top: 20px;
  margin-bottom: 10px;
  color: #303133;
}

.help-content p {
  margin: 10px 0;
  line-height: 1.6;
  color: #606266;
}

.help-content ul,
.help-content ol {
  margin: 10px 0;
  padding-left: 30px;
  color: #606266;
}

.help-content li {
  margin: 5px 0;
}

.help-content code {
  padding: 2px 6px;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #e6a23c;
}
</style>
