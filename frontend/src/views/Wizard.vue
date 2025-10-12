<template>
  <div class="wizard-container">
    <el-card class="wizard-card">
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="欢迎" description="开始配置" />
        <el-step title="登录KOOK" description="添加账号" />
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
              <div class="welcome-tips">
                <el-alert
                  title="提示"
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
              <div class="action-buttons">
                <el-button type="primary" size="large" @click="nextStep">
                  开始配置
                </el-button>
                <el-button size="large" @click="skipWizard">
                  跳过向导
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

        <!-- 步骤3: 配置机器人 -->
        <div v-else-if="currentStep === 2" class="step-bots">
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
                    <el-input
                      v-model="telegramForm.chat_id"
                      placeholder="-1001234567890"
                    />
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
            <el-button
              type="primary"
              :disabled="addedBots.length === 0"
              @click="nextStep"
            >
              继续
            </el-button>
          </div>
        </div>

        <!-- 步骤4: 完成 -->
        <div v-else-if="currentStep === 3" class="step-complete">
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

// 下一步
const nextStep = () => {
  if (currentStep.value < 3) {
    currentStep.value++
  }
}

// 上一步
const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 跳过向导
const skipWizard = () => {
  if (confirm('确定跳过配置向导？您可以稍后在设置中手动配置。')) {
    router.push('/')
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

// 测试Bot
const testBot = async (platform) => {
  ElMessage.info('测试功能开发中...')
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
</style>
