<template>
  <div class="bot-config-container">
    <el-row :gutter="20">
      <!-- 左侧：Bot配置 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Connection /></el-icon>
                Bot配置
              </span>
              <el-button-group size="small">
                <el-button :icon="Plus" type="primary" @click="showAddBotDialog">
                  添加Bot
                </el-button>
                <el-button :icon="Refresh" @click="refreshBots">
                  刷新
                </el-button>
              </el-button-group>
            </div>
          </template>
          
          <!-- Bot列表 -->
          <div class="bot-list" v-loading="loading">
            <el-empty 
              v-if="bots.length === 0 && !loading"
              description="还没有配置任何Bot"
            >
              <el-button type="primary" :icon="Plus" @click="showAddBotDialog">
                添加第一个Bot
              </el-button>
            </el-empty>
            
            <div v-else class="bots-grid">
              <el-card 
                v-for="bot in bots" 
                :key="bot.id"
                class="bot-card"
                shadow="hover"
              >
                <template #header>
                  <div class="bot-card-header">
                    <el-icon :size="24" :color="getPlatformColor(bot.platform)">
                      <component :is="getPlatformIcon(bot.platform)" />
                    </el-icon>
                    
                    <div class="bot-info">
                      <div class="bot-name">{{ bot.name }}</div>
                      <el-tag :type="getPlatformTagType(bot.platform)" size="small">
                        {{ bot.platform }}
                      </el-tag>
                    </div>
                    
                    <el-tag 
                      :type="bot.status === 'active' ? 'success' : 'danger'"
                      size="small"
                    >
                      {{ bot.status === 'active' ? '正常' : '异常' }}
                    </el-tag>
                  </div>
                </template>
                
                <el-descriptions :column="1" size="small" border>
                  <el-descriptions-item label="类型">
                    {{ getBotTypeLabel(bot.platform) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="创建时间">
                    {{ formatTime(bot.created_at) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="最后测试">
                    {{ bot.last_test ? formatTime(bot.last_test) : '未测试' }}
                  </el-descriptions-item>
                </el-descriptions>
                
                <template #footer>
                  <el-button-group size="small">
                    <el-button :icon="Connection" @click="testBot(bot)" :loading="bot.testing">
                      测试
                    </el-button>
                    <el-button :icon="Edit" @click="editBot(bot)">
                      编辑
                    </el-button>
                    <el-button :icon="Delete" type="danger" @click="deleteBot(bot)">
                      删除
                    </el-button>
                  </el-button-group>
                </template>
              </el-card>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧：教程面板 -->
      <el-col :span="8">
        <el-card class="tutorial-card" sticky>
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Reading /></el-icon>
                配置教程
              </span>
            </div>
          </template>
          
          <el-tabs v-model="activeTutorial" class="tutorial-tabs">
            <!-- Discord教程 -->
            <el-tab-pane label="Discord" name="discord">
              <div class="tutorial-content">
                <el-steps direction="vertical" :active="discordStep">
                  <el-step title="创建Webhook">
                    <template #description>
                      <div class="step-description">
                        <p>1. 打开Discord服务器设置</p>
                        <p>2. 进入 整合 → Webhook</p>
                        <p>3. 点击 "新建Webhook"</p>
                        <el-image 
                          src="/docs/images/discord-webhook-1.png"
                          fit="contain"
                          style="width: 100%; margin-top: 8px;"
                          preview-src-list="['/docs/images/discord-webhook-1.png']"
                        />
                      </div>
                    </template>
                  </el-step>
                  
                  <el-step title="配置Webhook">
                    <template #description>
                      <div class="step-description">
                        <p>1. 设置Webhook名称和头像</p>
                        <p>2. 选择目标频道</p>
                        <p>3. 点击 "复制Webhook URL"</p>
                        <el-image 
                          src="/docs/images/discord-webhook-2.png"
                          fit="contain"
                          style="width: 100%; margin-top: 8px;"
                          preview-src-list="['/docs/images/discord-webhook-2.png']"
                        />
                      </div>
                    </template>
                  </el-step>
                  
                  <el-step title="在本系统配置">
                    <template #description>
                      <div class="step-description">
                        <p>1. 点击上方 "添加Bot"</p>
                        <p>2. 选择平台：Discord</p>
                        <p>3. 粘贴Webhook URL</p>
                        <p>4. 点击 "测试连接"</p>
                      </div>
                    </template>
                  </el-step>
                </el-steps>
                
                <el-divider />
                
                <div class="tutorial-actions">
                  <el-button type="primary" @click="showAddBotDialog('discord')">
                    立即配置Discord
                  </el-button>
                  <el-button :icon="VideoPlay" @click="watchVideo('discord')">
                    观看视频教程
                  </el-button>
                </div>
              </div>
            </el-tab-pane>
            
            <!-- Telegram教程 -->
            <el-tab-pane label="Telegram" name="telegram">
              <div class="tutorial-content">
                <el-steps direction="vertical" :active="telegramStep">
                  <el-step title="创建Bot">
                    <template #description>
                      <div class="step-description">
                        <p>1. 在Telegram中搜索 @BotFather</p>
                        <p>2. 发送 /newbot 命令</p>
                        <p>3. 按提示设置Bot名称和用户名</p>
                        <p>4. 保存Bot Token</p>
                        <el-alert 
                          type="info"
                          :closable="false"
                          show-icon
                          style="margin-top: 8px;"
                        >
                          <template #title>
                            Token格式：123456789:ABCdefGHIjklMNO
                          </template>
                        </el-alert>
                      </div>
                    </template>
                  </el-step>
                  
                  <el-step title="将Bot添加到群组">
                    <template #description>
                      <div class="step-description">
                        <p>1. 创建或打开Telegram群组</p>
                        <p>2. 点击群组名称→添加成员</p>
                        <p>3. 搜索并添加您的Bot</p>
                        <p>4. 确保Bot有管理员权限（推荐）</p>
                      </div>
                    </template>
                  </el-step>
                  
                  <el-step title="获取Chat ID">
                    <template #description>
                      <div class="step-description">
                        <p>方法1：使用本系统自动获取</p>
                        <el-button 
                          size="small" 
                          type="primary"
                          @click="autoGetChatId"
                          style="margin-top: 8px;"
                        >
                          自动获取Chat ID
                        </el-button>
                        
                        <el-divider>或</el-divider>
                        
                        <p>方法2：手动获取</p>
                        <p>1. 在群组中发送任意消息</p>
                        <p>2. 访问：api.telegram.org/bot{token}/getUpdates</p>
                        <p>3. 查找 chat.id 字段</p>
                      </div>
                    </template>
                  </el-step>
                  
                  <el-step title="在本系统配置">
                    <template #description>
                      <div class="step-description">
                        <p>1. 点击上方 "添加Bot"</p>
                        <p>2. 选择平台：Telegram</p>
                        <p>3. 填入Bot Token和Chat ID</p>
                        <p>4. 点击 "测试连接"</p>
                      </div>
                    </template>
                  </el-step>
                </el-steps>
                
                <el-divider />
                
                <div class="tutorial-actions">
                  <el-button type="primary" @click="showAddBotDialog('telegram')">
                    立即配置Telegram
                  </el-button>
                  <el-button :icon="VideoPlay" @click="watchVideo('telegram')">
                    观看视频教程
                  </el-button>
                </div>
              </div>
            </el-tab-pane>
            
            <!-- 飞书教程 -->
            <el-tab-pane label="飞书" name="feishu">
              <div class="tutorial-content">
                <el-steps direction="vertical" :active="feishuStep">
                  <el-step title="创建飞书应用">
                    <template #description>
                      <div class="step-description">
                        <p>1. 访问 open.feishu.cn</p>
                        <p>2. 创建企业自建应用</p>
                        <p>3. 设置应用名称和描述</p>
                        <p>4. 获取App ID和App Secret</p>
                      </div>
                    </template>
                  </el-step>
                  
                  <el-step title="配置机器人权限">
                    <template #description>
                      <div class="step-description">
                        <p>1. 在应用设置中开启机器人能力</p>
                        <p>2. 配置以下权限：</p>
                        <ul>
                          <li>获取与发送单聊、群组消息</li>
                          <li>读取群组信息</li>
                          <li>上传图片</li>
                        </ul>
                        <p>3. 发布应用版本</p>
                      </div>
                    </template>
                  </el-step>
                  
                  <el-step title="添加机器人到群组">
                    <template #description>
                      <div class="step-description">
                        <p>1. 创建或打开飞书群组</p>
                        <p>2. 点击群设置→机器人</p>
                        <p>3. 搜索并添加您的机器人</p>
                        <p>4. 或使用Webhook URL</p>
                      </div>
                    </template>
                  </el-step>
                  
                  <el-step title="在本系统配置">
                    <template #description>
                      <div class="step-description">
                        <p>1. 点击上方 "添加Bot"</p>
                        <p>2. 选择平台：飞书</p>
                        <p>3. 填入App ID和App Secret</p>
                        <p>4. （可选）填入Webhook URL</p>
                        <p>5. 点击 "测试连接"</p>
                      </div>
                    </template>
                  </el-step>
                </el-steps>
                
                <el-divider />
                
                <div class="tutorial-actions">
                  <el-button type="primary" @click="showAddBotDialog('feishu')">
                    立即配置飞书
                  </el-button>
                  <el-button :icon="VideoPlay" @click="watchVideo('feishu')">
                    观看视频教程
                  </el-button>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
          
          <!-- 常见问题 -->
          <el-divider />
          
          <div class="faq-section">
            <h4>
              <el-icon><QuestionFilled /></el-icon>
              常见问题
            </h4>
            
            <el-collapse accordion>
              <el-collapse-item title="Webhook URL格式是什么？" name="1">
                <p>Discord Webhook URL格式：</p>
                <code>https://discord.com/api/webhooks/[ID]/[TOKEN]</code>
              </el-collapse-item>
              
              <el-collapse-item title="如何测试Bot是否配置成功？" name="2">
                <p>点击Bot卡片上的 "测试" 按钮，系统会发送一条测试消息。如果能在目标平台看到消息，说明配置成功。</p>
              </el-collapse-item>
              
              <el-collapse-item title="为什么Bot无法发送消息？" name="3">
                <p>可能的原因：</p>
                <ul>
                  <li>Token或Webhook URL错误</li>
                  <li>Bot权限不足</li>
                  <li>目标频道不存在</li>
                  <li>网络连接问题</li>
                </ul>
                <p>请检查配置并重新测试。</p>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 添加Bot对话框 -->
    <el-dialog
      v-model="addBotDialogVisible"
      title="添加Bot"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="botForm" label-width="120px">
        <el-form-item label="平台">
          <el-select v-model="botForm.platform" placeholder="选择平台" @change="onPlatformChange">
            <el-option label="Discord" value="discord">
              <span style="display: flex; align-items: center; gap: 8px;">
                <el-icon><ChatDotRound /></el-icon>
                Discord
              </span>
            </el-option>
            <el-option label="Telegram" value="telegram">
              <span style="display: flex; align-items: center; gap: 8px;">
                <el-icon><ChatLineRound /></el-icon>
                Telegram
              </span>
            </el-option>
            <el-option label="飞书" value="feishu">
              <span style="display: flex; align-items: center; gap: 8px;">
                <el-icon><Message /></el-icon>
                飞书
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="Bot名称">
          <el-input v-model="botForm.name" placeholder="给Bot起个名字（备注用）" />
        </el-form-item>
        
        <!-- Discord配置 -->
        <template v-if="botForm.platform === 'discord'">
          <el-form-item label="Webhook URL">
            <el-input 
              v-model="botForm.webhook_url" 
              placeholder="https://discord.com/api/webhooks/..."
              type="textarea"
              :rows="3"
            />
          </el-form-item>
        </template>
        
        <!-- Telegram配置 -->
        <template v-if="botForm.platform === 'telegram'">
          <el-form-item label="Bot Token">
            <el-input 
              v-model="botForm.bot_token" 
              placeholder="123456789:ABCdefGHIjklMNO..."
            />
          </el-form-item>
          
          <el-form-item label="Chat ID">
            <el-input v-model="botForm.chat_id" placeholder="-1001234567890">
              <template #append>
                <el-button @click="autoGetChatId">自动获取</el-button>
              </template>
            </el-input>
          </el-form-item>
        </template>
        
        <!-- 飞书配置 -->
        <template v-if="botForm.platform === 'feishu'">
          <el-form-item label="App ID">
            <el-input v-model="botForm.app_id" placeholder="cli_xxxxxxxxxxxxx" />
          </el-form-item>
          
          <el-form-item label="App Secret">
            <el-input 
              v-model="botForm.app_secret" 
              type="password"
              placeholder="xxxxxxxxxxxxx"
              show-password
            />
          </el-form-item>
          
          <el-form-item label="Webhook URL">
            <el-input 
              v-model="botForm.webhook_url" 
              placeholder="https://open.feishu.cn/open-apis/bot/v2/hook/... (可选)"
            />
          </el-form-item>
        </template>
      </el-form>
      
      <template #footer>
        <el-button @click="addBotDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAddBot" :loading="submitting">
          添加
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Connection, Plus, Refresh, Edit, Delete, Reading, VideoPlay,
  QuestionFilled, ChatDotRound, ChatLineRound, Message
} from '@element-plus/icons-vue'
import axios from 'axios'

// 状态
const loading = ref(false)
const bots = ref([])
const addBotDialogVisible = ref(false)
const submitting = ref(false)
const activeTutorial = ref('discord')
const discordStep = ref(0)
const telegramStep = ref(0)
const feishuStep = ref(0)

// 表单
const botForm = ref({
  platform: 'discord',
  name: '',
  webhook_url: '',
  bot_token: '',
  chat_id: '',
  app_id: '',
  app_secret: ''
})

// 加载Bots
async function loadBots() {
  loading.value = true
  try {
    const response = await axios.get('/api/bots')
    bots.value = response.data.map(bot => ({
      ...bot,
      testing: false
    }))
  } catch (error) {
    ElMessage.error('加载Bot失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 刷新
async function refreshBots() {
  await loadBots()
  ElMessage.success('已刷新')
}

// 显示添加对话框
function showAddBotDialog(platform = 'discord') {
  addBotDialogVisible.value = true
  botForm.value = {
    platform,
    name: '',
    webhook_url: '',
    bot_token: '',
    chat_id: '',
    app_id: '',
    app_secret: ''
  }
  activeTutorial.value = platform
}

// 平台变化
function onPlatformChange(platform) {
  activeTutorial.value = platform
}

// 提交添加
async function submitAddBot() {
  submitting.value = true
  
  try {
    const response = await axios.post('/api/bots', botForm.value)
    
    if (response.data.success) {
      ElMessage.success('Bot添加成功')
      addBotDialogVisible.value = false
      await loadBots()
    } else {
      ElMessage.error(response.data.message || '添加失败')
    }
  } catch (error) {
    ElMessage.error('添加失败: ' + error.message)
  } finally {
    submitting.value = false
  }
}

// 测试Bot
async function testBot(bot) {
  bot.testing = true
  
  try {
    const response = await axios.post(`/api/bots/${bot.id}/test`)
    
    if (response.data.success) {
      ElMessage.success('测试消息已发送，请检查目标平台')
      bot.last_test = Date.now()
    } else {
      ElMessage.error(response.data.message || '测试失败')
    }
  } catch (error) {
    ElMessage.error('测试失败: ' + error.message)
  } finally {
    bot.testing = false
  }
}

// 编辑Bot
function editBot(bot) {
  // 实现编辑逻辑
  ElMessage.info('编辑功能开发中...')
}

// 删除Bot
function deleteBot(bot) {
  ElMessageBox.confirm(
    `确定要删除Bot "${bot.name}" 吗？`,
    '删除Bot',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await axios.delete(`/api/bots/${bot.id}`)
      ElMessage.success('删除成功')
      await loadBots()
    } catch (error) {
      ElMessage.error('删除失败: ' + error.message)
    }
  }).catch(() => {})
}

// 自动获取Chat ID
async function autoGetChatId() {
  if (!botForm.value.bot_token) {
    ElMessage.warning('请先填入Bot Token')
    return
  }
  
  try {
    const response = await axios.post('/api/telegram/get-chat-id', {
      bot_token: botForm.value.bot_token
    })
    
    if (response.data.success) {
      botForm.value.chat_id = response.data.chat_id
      ElMessage.success('Chat ID获取成功')
    } else {
      ElMessage.error(response.data.message || '获取失败')
    }
  } catch (error) {
    ElMessage.error('获取失败: ' + error.message)
  }
}

// 观看视频
function watchVideo(platform) {
  const videos = {
    discord: 'https://www.youtube.com/watch?v=xxx',
    telegram: 'https://www.youtube.com/watch?v=yyy',
    feishu: 'https://www.bilibili.com/video/BVzzz'
  }
  
  window.open(videos[platform], '_blank')
}

// 获取平台图标
function getPlatformIcon(platform) {
  const icons = {
    discord: 'ChatDotRound',
    telegram: 'ChatLineRound',
    feishu: 'Message'
  }
  return icons[platform] || 'Connection'
}

// 获取平台颜色
function getPlatformColor(platform) {
  const colors = {
    discord: '#5865F2',
    telegram: '#0088cc',
    feishu: '#00b96b'
  }
  return colors[platform] || '#409EFF'
}

// 获取平台标签类型
function getPlatformTagType(platform) {
  const types = {
    discord: 'primary',
    telegram: 'success',
    feishu: 'warning'
  }
  return types[platform] || 'info'
}

// 获取Bot类型标签
function getBotTypeLabel(platform) {
  const labels = {
    discord: 'Discord Webhook',
    telegram: 'Telegram Bot',
    feishu: '飞书应用'
  }
  return labels[platform] || platform
}

// 格式化时间
function formatTime(timestamp) {
  if (!timestamp) return 'N/A'
  return new Date(timestamp).toLocaleString('zh-CN')
}

// 初始化
onMounted(() => {
  loadBots()
})
</script>

<style scoped>
.bot-config-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bot-list {
  min-height: 400px;
}

.bots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.bot-card {
  transition: all 0.3s;
}

.bot-card:hover {
  transform: translateY(-4px);
}

.bot-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bot-info {
  flex: 1;
}

.bot-name {
  font-weight: 600;
  font-size: 16px;
}

.tutorial-card {
  position: sticky;
  top: 20px;
}

.tutorial-content {
  padding: 16px 0;
}

.step-description {
  padding: 8px 0;
}

.step-description p {
  margin: 4px 0;
}

.step-description ul {
  margin: 8px 0;
  padding-left: 20px;
}

.tutorial-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.faq-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
</style>
