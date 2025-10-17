<template>
  <div class="wizard-container">
    <el-card class="wizard-card">
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="欢迎" description="开始配置" />
        <el-step title="登录KOOK" description="添加账号" />
        <el-step title="选择服务器" description="监听频道" />
        <el-step title="配置机器人" description="选择平台" />
        <el-step title="完成" description="开始使用" />
      </el-steps>

      <div class="wizard-content">
        <!-- 步骤1: 欢迎页 -->
        <div v-if="currentStep === 0" class="step-welcome">
          <el-result
            icon="success"
            title="🎉 欢迎使用KOOK消息转发系统"
            sub-title="本向导将帮助您完成基础配置，预计耗时：3-5分钟"
          >
            <template #extra>
              <!-- 免责声明 -->
              <el-alert
                title="⚠️ 免责声明"
                type="warning"
                :closable="false"
                show-icon
                style="margin-bottom: 20px"
              >
                <div class="disclaimer-content">
                  <p><strong>使用本软件前，请仔细阅读以下声明：</strong></p>
                  <ol>
                    <li>本软件通过浏览器自动化抓取KOOK消息，<strong>可能违反KOOK服务条款</strong></li>
                    <li>使用本软件可能导致账号被封禁，<strong>请仅在已获授权的场景下使用</strong></li>
                    <li>转发的消息内容可能涉及版权，<strong>请遵守相关法律法规</strong></li>
                    <li>本软件仅供学习交流，<strong>开发者不承担任何法律责任</strong></li>
                    <li>使用本软件即表示您已了解并接受上述风险</li>
                  </ol>
                </div>
              </el-alert>

              <div class="welcome-tips">
                <el-alert
                  title="配置前准备"
                  type="info"
                  :closable="false"
                  show-icon
                >
                  <ul>
                    <li>您需要准备KOOK账号的Cookie或账号密码</li>
                    <li>至少配置一个转发目标（Discord/Telegram/飞书）</li>
                    <li>可以随时在设置中修改配置</li>
                  </ul>
                </el-alert>
              </div>

              <div class="agreement-section">
                <el-checkbox v-model="agreedToDisclaimer" size="large">
                  <strong>我已阅读并同意以上免责声明</strong>
                </el-checkbox>
              </div>

              <div class="action-buttons">
                <el-button
                  type="primary"
                  size="large"
                  :disabled="!agreedToDisclaimer"
                  @click="nextStep"
                >
                  同意并继续
                </el-button>
                <el-button size="large" @click="skipWizard">
                  拒绝并退出
                </el-button>
              </div>
            </template>
          </el-result>
        </div>

        <!-- 步骤2: KOOK账号登录 -->
        <div v-else-if="currentStep === 1" class="step-login">
          <h2>📧 登录KOOK账号</h2>
          
          <el-radio-group v-model="loginType" class="login-type-selector">
            <el-radio label="cookie">Cookie导入（推荐）</el-radio>
            <el-radio label="password">账号密码登录</el-radio>
          </el-radio-group>

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
            </el-alert>

            <el-form :model="accountForm" label-width="100px" class="form-content">
              <el-form-item label="Cookie">
                <el-input
                  v-model="accountForm.cookie"
                  type="textarea"
                  :rows="6"
                  placeholder="粘贴Cookie内容（JSON格式或文本格式）"
                />
              </el-form-item>

              <el-form-item label="账号备注">
                <el-input
                  v-model="accountForm.name"
                  placeholder="例如：主账号"
                />
              </el-form-item>
            </el-form>
          </div>

          <div v-else class="password-login">
            <el-alert
              title="首次登录可能需要验证码"
              type="warning"
              :closable="false"
              class="help-alert"
            />

            <el-form :model="accountForm" label-width="100px" class="form-content">
              <el-form-item label="邮箱">
                <el-input
                  v-model="accountForm.email"
                  placeholder="KOOK注册邮箱"
                />
              </el-form-item>

              <el-form-item label="密码">
                <el-input
                  v-model="accountForm.password"
                  type="password"
                  placeholder="账号密码"
                  show-password
                />
              </el-form-item>

              <el-form-item label="账号备注">
                <el-input
                  v-model="accountForm.name"
                  placeholder="例如：主账号"
                />
              </el-form-item>
            </el-form>
          </div>

          <div class="action-buttons">
            <el-button @click="prevStep">上一步</el-button>
            <el-button
              type="primary"
              :loading="adding"
              @click="addAccount"
            >
              登录并继续
            </el-button>
          </div>
        </div>

        <!-- 步骤3: 选择服务器和频道 -->
        <div v-else-if="currentStep === 2" class="step-servers">
          <h2>🏠 选择要监听的KOOK服务器</h2>
          
          <el-alert
            v-if="!accountAdded"
            title="请先在上一步添加KOOK账号"
            type="warning"
            :closable="false"
            class="help-alert"
          />

          <el-alert
            v-else-if="loadingServers"
            title="正在加载服务器列表，请稍候..."
            type="info"
            :closable="false"
            class="help-alert"
          />

          <div v-else-if="servers.length === 0 && !loadingServers" class="empty-servers">
            <el-empty description="未获取到服务器列表">
              <el-button type="primary" @click="loadServers">
                重新加载
              </el-button>
            </el-empty>
          </div>

          <div v-else class="servers-list">
            <el-alert
              title="请选择需要监听的服务器和频道"
              type="info"
              :closable="false"
              class="help-alert"
            >
              <p>提示：</p>
              <ul>
                <li>只有选中的频道才会被监听</li>
                <li>可以在后续的"频道映射"页面中设置转发规则</li>
                <li>支持全选或按需选择</li>
              </ul>
            </el-alert>

            <div class="server-selection">
              <div class="toolbar">
                <el-button size="small" @click="selectAll">全选</el-button>
                <el-button size="small" @click="unselectAll">全不选</el-button>
                <span class="selection-count">
                  已选择：{{ selectedChannelsCount }} 个频道
                </span>
              </div>

              <el-collapse v-model="activeServers" accordion>
                <el-collapse-item
                  v-for="server in servers"
                  :key="server.id"
                  :name="server.id"
                  :title="`${server.name} (${server.channels?.length || 0}个频道)`"
                >
                  <template #title>
                    <div class="server-header">
                      <el-checkbox
                        v-model="server.selected"
                        @change="toggleServer(server)"
                        @click.stop
                      />
                      <img
                        v-if="server.icon"
                        :src="server.icon"
                        class="server-icon"
                        alt="server icon"
                      />
                      <span class="server-name">{{ server.name }}</span>
                      <el-tag size="small" type="info">
                        {{ server.channels?.length || 0 }}个频道
                      </el-tag>
                    </div>
                  </template>

                  <div v-if="!server.channels" class="loading-channels">
                    <el-button
                      type="primary"
                      size="small"
                      :loading="loadingChannels[server.id]"
                      @click="loadChannels(server.id)"
                    >
                      加载频道列表
                    </el-button>
                  </div>

                  <el-checkbox-group
                    v-else
                    v-model="server.selectedChannels"
                    class="channels-list"
                  >
                    <el-checkbox
                      v-for="channel in server.channels"
                      :key="channel.id"
                      :label="channel.id"
                      class="channel-item"
                    >
                      <span class="channel-icon">
                        {{ channel.type === 'voice' ? '🔊' : '#' }}
                      </span>
                      {{ channel.name }}
                      <el-tag v-if="channel.type === 'voice'" size="small" type="warning">
                        语音
                      </el-tag>
                    </el-checkbox>
                  </el-checkbox-group>
                </el-collapse-item>
              </el-collapse>
            </div>
          </div>

          <div class="action-buttons">
            <el-button @click="prevStep">上一步</el-button>
            <el-button
              type="primary"
              :disabled="selectedChannelsCount === 0"
              @click="saveSelectedChannels"
            >
              继续（已选 {{ selectedChannelsCount }} 个频道）
            </el-button>
          </div>
        </div>

        <!-- 步骤4: 配置机器人 -->
        <div v-else-if="currentStep === 3" class="step-bots">
          <h2>🤖 配置转发机器人</h2>
          
          <el-alert
            title="至少配置一个平台的机器人才能继续"
            type="info"
            :closable="false"
            class="help-alert"
          />

          <el-tabs v-model="activePlatform" type="card">
            <!-- Discord -->
            <el-tab-pane label="Discord" name="discord">
              <div class="bot-config-form">
                <el-alert
                  title="如何创建Discord Webhook？"
                  type="info"
                  :closable="false"
                >
                  <ol>
                    <li>进入Discord服务器设置</li>
                    <li>集成 → Webhooks</li>
                    <li>新建Webhook并复制URL</li>
                  </ol>
                  <a href="https://support.discord.com/hc/zh-tw/articles/228383668" target="_blank">
                    查看详细教程 →
                  </a>
                </el-alert>

                <el-form :model="discordForm" label-width="120px" style="margin-top: 20px">
                  <el-form-item label="Bot名称">
                    <el-input v-model="discordForm.name" placeholder="例如：游戏公告Bot" />
                  </el-form-item>
                  <el-form-item label="Webhook URL">
                    <el-input
                      v-model="discordForm.webhook_url"
                      placeholder="https://discord.com/api/webhooks/..."
                    />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="addBot('discord')">
                      添加Discord Bot
                    </el-button>
                    <el-button @click="testBot('discord')">测试连接</el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>

            <!-- Telegram -->
            <el-tab-pane label="Telegram" name="telegram">
              <div class="bot-config-form">
                <el-alert
                  title="如何创建Telegram Bot？"
                  type="info"
                  :closable="false"
                >
                  <ol>
                    <li>与 @BotFather 对话</li>
                    <li>发送 /newbot 创建Bot</li>
                    <li>获取Bot Token</li>
                    <li>将Bot添加到目标群组</li>
                  </ol>
                </el-alert>

                <el-form :model="telegramForm" label-width="120px" style="margin-top: 20px">
                  <el-form-item label="Bot名称">
                    <el-input v-model="telegramForm.name" placeholder="例如：游戏公告TG Bot" />
                  </el-form-item>
                  <el-form-item label="Bot Token">
                    <el-input
                      v-model="telegramForm.token"
                      placeholder="1234567890:ABCdefGHI..."
                    />
                  </el-form-item>
                  <el-form-item label="Chat ID">
                    <div style="display: flex; gap: 10px">
                      <el-input
                        v-model="telegramForm.chat_id"
                        placeholder="-1001234567890"
                        style="flex: 1"
                      />
                      <el-button 
                        @click="autoGetChatId" 
                        :loading="gettingChatId"
                        :disabled="!telegramForm.token"
                      >
                        🔍 自动获取
                      </el-button>
                    </div>
                    <div style="color: #909399; font-size: 12px; margin-top: 5px">
                      提示：请先向Bot发送一条消息，然后点击"自动获取"
                    </div>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="addBot('telegram')">
                      添加Telegram Bot
                    </el-button>
                    <el-button @click="testBot('telegram')">测试连接</el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>

            <!-- 飞书 -->
            <el-tab-pane label="飞书" name="feishu">
              <div class="bot-config-form">
                <el-alert
                  title="如何创建飞书应用？"
                  type="info"
                  :closable="false"
                >
                  <ol>
                    <li>访问飞书开放平台</li>
                    <li>创建企业自建应用</li>
                    <li>开启机器人能力</li>
                    <li>获取App ID和App Secret</li>
                  </ol>
                </el-alert>

                <el-form :model="feishuForm" label-width="120px" style="margin-top: 20px">
                  <el-form-item label="Bot名称">
                    <el-input v-model="feishuForm.name" placeholder="例如：游戏公告飞书Bot" />
                  </el-form-item>
                  <el-form-item label="App ID">
                    <el-input
                      v-model="feishuForm.app_id"
                      placeholder="cli_..."
                    />
                  </el-form-item>
                  <el-form-item label="App Secret">
                    <el-input
                      v-model="feishuForm.app_secret"
                      placeholder="..."
                    />
                  </el-form-item>
                  <el-form-item label="Chat ID">
                    <el-input
                      v-model="feishuForm.chat_id"
                      placeholder="oc_..."
                    />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="addBot('feishu')">
                      添加飞书Bot
                    </el-button>
                    <el-button @click="testBot('feishu')">测试连接</el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>
          </el-tabs>

          <div v-if="addedBots.length > 0" class="added-bots">
            <h3>已添加的机器人（{{ addedBots.length }}个）</h3>
            <el-tag
              v-for="bot in addedBots"
              :key="bot.id"
              type="success"
              size="large"
              style="margin-right: 10px"
            >
              {{ bot.platform }} - {{ bot.name }}
            </el-tag>
          </div>

          <div class="action-buttons">
            <el-button @click="prevStep">上一步</el-button>
            <el-button @click="skipBotConfig" plain>
              跳过，稍后配置
            </el-button>
            <el-button
              type="primary"
              :disabled="addedBots.length === 0"
              @click="nextStep"
            >
              继续
            </el-button>
          </div>
        </div>

        <!-- 步骤5: 完成 -->
        <div v-else-if="currentStep === 4" class="step-complete">
          <el-result
            icon="success"
            title="✅ 配置完成！"
            sub-title="您已成功完成基础配置"
          >
            <template #extra>
              <div class="complete-summary">
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="KOOK账号">
                    {{ accountAdded ? '✅ 已添加' : '❌ 未添加' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="监听频道">
                    ✅ {{ selectedChannelsCount }}个频道
                  </el-descriptions-item>
                  <el-descriptions-item label="机器人配置">
                    ✅ {{ addedBots.length }}个平台
                  </el-descriptions-item>
                </el-descriptions>

                <el-alert
                  title="接下来您可以："
                  type="success"
                  :closable="false"
                  style="margin-top: 20px"
                >
                  <ul>
                    <li>在"频道映射"中设置转发规则</li>
                    <li>启动服务开始转发消息</li>
                    <li>在"日志"中查看转发状态</li>
                  </ul>
                </el-alert>
              </div>

              <div class="action-buttons">
                <el-button type="primary" size="large" @click="finishWizard">
                  进入主界面
                </el-button>
              </div>
            </template>
          </el-result>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'

const router = useRouter()

// 当前步骤
const currentStep = ref(0)

// 登录类型
const loginType = ref('cookie')

// 账号表单
const accountForm = ref({
  name: '',
  email: '',
  password: '',
  cookie: ''
})

// Bot表单
const discordForm = ref({ name: '', webhook_url: '' })
const telegramForm = ref({ name: '', token: '', chat_id: '' })
const feishuForm = ref({ name: '', app_id: '', app_secret: '', chat_id: '' })

// 当前选中的平台
const activePlatform = ref('discord')

// 是否正在添加
const adding = ref(false)

// 账号是否已添加
const accountAdded = ref(false)

// 已添加的Bots
const addedBots = ref([])

// 是否同意免责声明
const agreedToDisclaimer = ref(false)

// 是否正在获取Chat ID
const gettingChatId = ref(false)

// 服务器相关
const servers = ref([])
const loadingServers = ref(false)
const loadingChannels = ref({})
const activeServers = ref([])
const selectedChannelsCount = computed(() => {
  return servers.value.reduce((count, server) => {
    return count + (server.selectedChannels?.length || 0)
  }, 0)
})

// 下一步
const nextStep = () => {
  if (currentStep.value < 4) {
    currentStep.value++
    
    // 如果进入到服务器选择步骤，自动加载服务器列表
    if (currentStep.value === 2 && accountAdded.value && servers.value.length === 0) {
      loadServers()
    }
  }
}

// 上一步
const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 跳过Bot配置（步骤4）
const skipBotConfig = () => {
  ElMessage.info('已跳过机器人配置，您可以稍后在"机器人配置"页面添加')
  currentStep.value = 4  // 直接跳转到完成步骤
}

// 跳过向导（在第一步即退出应用）
const skipWizard = () => {
  if (currentStep.value === 0) {
    // 第一步拒绝则关闭应用
    if (confirm('您拒绝了免责声明，应用将关闭。')) {
      // 如果是Electron环境，关闭窗口
      if (window.electron && window.electron.closeWindow) {
        window.electron.closeWindow()
      } else {
        // 否则返回首页
        router.push('/')
      }
    }
  } else {
    // 其他步骤允许跳过
    if (confirm('确定跳过配置向导？您可以稍后在设置中手动配置。')) {
      router.push('/')
    }
  }
}

// 添加账号
const addAccount = async () => {
  try {
    adding.value = true

    const data = {
      name: accountForm.value.name || '默认账号'
    }

    if (loginType.value === 'cookie') {
      if (!accountForm.value.cookie) {
        ElMessage.error('请输入Cookie')
        return
      }
      data.cookie = accountForm.value.cookie
    } else {
      if (!accountForm.value.email || !accountForm.value.password) {
        ElMessage.error('请输入邮箱和密码')
        return
      }
      data.email = accountForm.value.email
      data.password = accountForm.value.password
    }

    await api.addAccount(data)
    ElMessage.success('账号添加成功')
    accountAdded.value = true
    nextStep()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '添加失败')
  } finally {
    adding.value = false
  }
}

// 添加Bot
const addBot = async (platform) => {
  try {
    let data = { platform }

    if (platform === 'discord') {
      if (!discordForm.value.name || !discordForm.value.webhook_url) {
        ElMessage.error('请填写完整信息')
        return
      }
      data.name = discordForm.value.name
      data.config = { webhook_url: discordForm.value.webhook_url }
    } else if (platform === 'telegram') {
      if (!telegramForm.value.name || !telegramForm.value.token || !telegramForm.value.chat_id) {
        ElMessage.error('请填写完整信息')
        return
      }
      data.name = telegramForm.value.name
      data.config = {
        token: telegramForm.value.token,
        chat_id: telegramForm.value.chat_id
      }
    } else if (platform === 'feishu') {
      if (!feishuForm.value.name || !feishuForm.value.app_id || !feishuForm.value.app_secret) {
        ElMessage.error('请填写完整信息')
        return
      }
      data.name = feishuForm.value.name
      data.config = {
        app_id: feishuForm.value.app_id,
        app_secret: feishuForm.value.app_secret,
        chat_id: feishuForm.value.chat_id
      }
    }

    const response = await api.addBot(data)
    ElMessage.success('Bot添加成功')
    addedBots.value.push(response.data)

    // 清空表单
    if (platform === 'discord') {
      discordForm.value = { name: '', webhook_url: '' }
    } else if (platform === 'telegram') {
      telegramForm.value = { name: '', token: '', chat_id: '' }
    } else if (platform === 'feishu') {
      feishuForm.value = { name: '', app_id: '', app_secret: '', chat_id: '' }
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '添加失败')
  }
}

// 自动获取Telegram Chat ID
const autoGetChatId = async () => {
  if (!telegramForm.value.token) {
    ElMessage.warning('请先输入Bot Token')
    return
  }

  try {
    gettingChatId.value = true
    const result = await api.getTelegramChatIds(telegramForm.value.token)
    
    if (!result.chat_ids || result.chat_ids.length === 0) {
      ElMessage.warning(result.message || '未找到任何Chat ID。请先在Telegram中向Bot发送一条消息，然后重试。')
      return
    }

    // 如果只有一个Chat ID，直接填入
    if (result.chat_ids.length === 1) {
      telegramForm.value.chat_id = result.chat_ids[0].id
      ElMessage.success(`已自动填入Chat ID: ${result.chat_ids[0].title}`)
    } else {
      // 如果有多个，让用户选择
      const options = result.chat_ids.map(chat => ({
        value: chat.id,
        label: `${chat.title || chat.id} (${chat.type})`
      }))
      
      // 这里简单起见，使用第一个
      // 实际应该弹出选择框让用户选
      telegramForm.value.chat_id = result.chat_ids[0].id
      ElMessage.success(`找到${result.chat_ids.length}个Chat，已自动填入第一个: ${result.chat_ids[0].title}`)
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '获取失败，请检查Token是否正确')
  } finally {
    gettingChatId.value = false
  }
}

// 测试Bot
const testBot = async (platform) => {
  ElMessage.info('测试功能开发中...')
}

// 加载服务器列表
const loadServers = async () => {
  try {
    loadingServers.value = true
    const accounts = await api.getAccounts()
    
    if (!accounts || accounts.length === 0) {
      ElMessage.warning('未找到KOOK账号')
      return
    }

    // 获取第一个在线账号的服务器列表
    const onlineAccount = accounts.find(a => a.status === 'online')
    if (!onlineAccount) {
      ElMessage.warning('账号未在线，请等待账号连接成功后重试')
      return
    }

    const result = await api.getServers(onlineAccount.id)
    servers.value = result.map(server => ({
      ...server,
      selected: false,
      selectedChannels: [],
      channels: null
    }))

    if (servers.value.length === 0) {
      ElMessage.warning('未获取到服务器列表，请确保账号已登录KOOK')
    }
  } catch (error) {
    ElMessage.error('加载服务器失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loadingServers.value = false
  }
}

// 加载频道列表
const loadChannels = async (serverId) => {
  try {
    loadingChannels.value[serverId] = true
    
    const accounts = await api.getAccounts()
    const onlineAccount = accounts.find(a => a.status === 'online')
    if (!onlineAccount) {
      ElMessage.warning('账号未在线')
      return
    }

    const channels = await api.getChannels(onlineAccount.id, serverId)
    
    const server = servers.value.find(s => s.id === serverId)
    if (server) {
      server.channels = channels
    }
  } catch (error) {
    ElMessage.error('加载频道失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loadingChannels.value[serverId] = false
  }
}

// 切换服务器选择状态
const toggleServer = (server) => {
  if (server.selected) {
    // 选中服务器时，加载其频道列表
    if (!server.channels) {
      loadChannels(server.id)
    } else {
      // 如果已加载，则全选频道
      server.selectedChannels = server.channels.map(c => c.id)
    }
  } else {
    // 取消选中服务器时，清空已选频道
    server.selectedChannels = []
  }
}

// 全选
const selectAll = () => {
  servers.value.forEach(server => {
    server.selected = true
    if (server.channels) {
      server.selectedChannels = server.channels.map(c => c.id)
    } else {
      loadChannels(server.id)
    }
  })
}

// 全不选
const unselectAll = () => {
  servers.value.forEach(server => {
    server.selected = false
    server.selectedChannels = []
  })
}

// 历史消息同步开关变化
const onSyncToggleChange = (value) => {
  if (value) {
    ElMessage.info('已启用历史消息同步，请选择合适的时间范围')
  } else {
    ElMessage.info('已关闭历史消息同步，仅转发新消息')
  }
}

// 保存选中的频道
const saveSelectedChannels = () => {
  // 保存历史消息同步设置
  const syncSettings = {
    enabled: syncHistoryMessages.value,
    timeRange: syncTimeRange.value
  }
  localStorage.setItem('kook_sync_settings', JSON.stringify(syncSettings))
  
  // 将选中的频道信息保存到localStorage供后续使用
  const selectedData = {
    servers: servers.value
      .filter(s => s.selectedChannels && s.selectedChannels.length > 0)
      .map(s => ({
        id: s.id,
        name: s.name,
        channels: s.channels
          .filter(c => s.selectedChannels.includes(c.id))
          .map(c => ({
            id: c.id,
            name: c.name,
            type: c.type
          }))
      }))
  }
  
  localStorage.setItem('wizard_selected_channels', JSON.stringify(selectedData))
  ElMessage.success(`已保存 ${selectedChannelsCount.value} 个频道`)
  nextStep()
}

// 完成向导
const finishWizard = () => {
  // 标记向导已完成
  localStorage.setItem('wizard_completed', 'true')
  ElMessage.success('配置完成，欢迎使用！')
  router.push('/')
}
</script>

<style scoped>
.wizard-container {
  padding: 20px;
  background: #f5f5f5;
  min-height: calc(100vh - 40px);
  display: flex;
  justify-content: center;
  align-items: center;
}

.wizard-card {
  width: 900px;
  max-width: 95%;
}

.wizard-content {
  margin-top: 40px;
  min-height: 500px;
}

.welcome-tips,
.complete-summary {
  margin: 30px 0;
}

.action-buttons {
  margin-top: 30px;
  text-align: center;
}

.action-buttons .el-button {
  margin: 0 10px;
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

.help-alert ol, .help-alert ul {
  margin: 10px 0;
  padding-left: 25px;
}

.help-alert li {
  margin: 5px 0;
}

.bot-config-form {
  padding: 20px;
}

.added-bots {
  margin-top: 30px;
  padding: 20px;
  background: #f0f9ff;
  border-radius: 4px;
}

.added-bots h3 {
  margin-bottom: 15px;
  color: #409eff;
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
}

.disclaimer-content {
  text-align: left;
}

.disclaimer-content p {
  margin-bottom: 10px;
}

.disclaimer-content ol {
  margin: 10px 0;
  padding-left: 25px;
}

.disclaimer-content li {
  margin: 8px 0;
  line-height: 1.6;
}

.agreement-section {
  margin: 25px 0;
  text-align: center;
  padding: 15px;
  background-color: #f0f9ff;
  border-radius: 4px;
}

/* 服务器选择相关样式 */
.step-servers {
  padding: 20px;
}

.empty-servers {
  padding: 60px 20px;
  text-align: center;
}

.servers-list {
  margin-top: 20px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.selection-count {
  margin-left: auto;
  color: #409eff;
  font-weight: bold;
}

.server-header {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.server-icon {
  width: 24px;
  height: 24px;
  border-radius: 4px;
}

.server-name {
  flex: 1;
  font-weight: 500;
}

.loading-channels {
  padding: 20px;
  text-align: center;
}

.channels-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 15px;
}

.channel-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.channel-item:hover {
  background-color: #f5f7fa;
}

.channel-icon {
  font-size: 16px;
  margin-right: 5px;
}

.server-selection {
  max-height: 500px;
  overflow-y: auto;
}
</style>
