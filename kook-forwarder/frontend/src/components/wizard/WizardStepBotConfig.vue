<template>
  <div class="wizard-bot-config">
    <el-alert type="info" :closable="false" class="step-info">
      <template #title>
        <div class="alert-title">
          <el-icon><Connection /></el-icon>
          <span>配置转发目标平台</span>
        </div>
      </template>
      选择您要转发到的平台，至少配置一个平台才能继续。
    </el-alert>

    <el-tabs v-model="activePlatform" class="platform-tabs">
      <!-- Discord -->
      <el-tab-pane label="Discord" name="discord">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Discord Webhook配置</span>
              <el-tag v-if="discordConfig.webhookUrl" type="success">已配置</el-tag>
            </div>
          </template>

          <el-form :model="discordConfig" label-width="120px">
            <el-form-item label="Webhook名称">
              <el-input 
                v-model="discordConfig.name" 
                placeholder="例如：游戏公告Bot"
              />
              <template #append>
                <el-text type="info" size="small">（备注用途）</el-text>
              </template>
            </el-form-item>

            <el-form-item label="Webhook URL" required>
              <el-input 
                v-model="discordConfig.webhookUrl" 
                placeholder="https://discord.com/api/webhooks/..."
                type="textarea"
                :rows="2"
              />
            </el-form-item>

            <el-form-item>
              <el-space>
                <el-button type="primary" @click="testDiscord" :loading="testing.discord">
                  <el-icon><CircleCheck /></el-icon>
                  测试连接
                </el-button>
                <el-link type="primary" @click="showDiscordTutorial">
                  <el-icon><QuestionFilled /></el-icon>
                  如何创建Discord Webhook？
                </el-link>
              </el-space>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- Telegram -->
      <el-tab-pane label="Telegram" name="telegram">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Telegram Bot配置</span>
              <el-tag v-if="telegramConfig.token" type="success">已配置</el-tag>
            </div>
          </template>

          <el-form :model="telegramConfig" label-width="120px">
            <el-form-item label="Bot名称">
              <el-input 
                v-model="telegramConfig.name" 
                placeholder="例如：游戏公告TG Bot"
              />
            </el-form-item>

            <el-form-item label="Bot Token" required>
              <el-input 
                v-model="telegramConfig.token" 
                placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
                type="password"
                show-password
              />
            </el-form-item>

            <el-form-item label="Chat ID" required>
              <el-input v-model="telegramConfig.chatId" placeholder="-1001234567890">
                <template #append>
                  <el-button @click="autoDetectChatId" :loading="detecting">
                    <el-icon><Search /></el-icon>
                    自动获取
                  </el-button>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item>
              <el-space>
                <el-button type="primary" @click="testTelegram" :loading="testing.telegram">
                  <el-icon><CircleCheck /></el-icon>
                  测试连接
                </el-button>
                <el-link type="primary" @click="showTelegramTutorial">
                  <el-icon><QuestionFilled /></el-icon>
                  如何创建Telegram Bot？
                </el-link>
              </el-space>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 飞书 -->
      <el-tab-pane label="飞书" name="feishu">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>飞书应用配置</span>
              <el-tag v-if="feishuConfig.appId" type="success">已配置</el-tag>
            </div>
          </template>

          <el-form :model="feishuConfig" label-width="120px">
            <el-form-item label="应用名称">
              <el-input 
                v-model="feishuConfig.name" 
                placeholder="例如：游戏公告飞书Bot"
              />
            </el-form-item>

            <el-form-item label="App ID" required>
              <el-input 
                v-model="feishuConfig.appId" 
                placeholder="cli_a1b2c3d4e5f6g7h8"
              />
            </el-form-item>

            <el-form-item label="App Secret" required>
              <el-input 
                v-model="feishuConfig.appSecret" 
                placeholder="ABCdefGHIjklMNOpqrs"
                type="password"
                show-password
              />
            </el-form-item>

            <el-form-item label="群组Webhook">
              <el-input 
                v-model="feishuConfig.webhookUrl" 
                placeholder="https://open.feishu.cn/open-apis/bot/v2/hook/..."
                type="textarea"
                :rows="2"
              />
              <template #append>
                <el-text type="info" size="small">（可选）</el-text>
              </template>
            </el-form-item>

            <el-form-item>
              <el-space>
                <el-button type="primary" @click="testFeishu" :loading="testing.feishu">
                  <el-icon><CircleCheck /></el-icon>
                  测试连接
                </el-button>
                <el-link type="primary" @click="showFeishuTutorial">
                  <el-icon><QuestionFilled /></el-icon>
                  如何创建飞书应用？
                </el-link>
              </el-space>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 已配置的Bot列表 -->
    <el-card v-if="configuredBots.length > 0" class="configured-bots" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>已配置的Bot</span>
          <el-tag type="success">{{ configuredBots.length }}个</el-tag>
        </div>
      </template>

      <el-space direction="vertical" style="width: 100%">
        <el-tag 
          v-for="bot in configuredBots" 
          :key="bot.platform"
          size="large"
          closable
          @close="removeBot(bot.platform)"
        >
          <el-icon><CircleCheckFilled /></el-icon>
          {{ bot.name }}
        </el-tag>
      </el-space>
    </el-card>

    <!-- 导航按钮 -->
    <div class="wizard-actions">
      <el-button @click="$emit('prev')">
        <el-icon><ArrowLeft /></el-icon>
        上一步
      </el-button>
      <el-button 
        type="primary" 
        @click="saveAndNext"
        :disabled="configuredBots.length === 0"
      >
        下一步：频道映射
        <el-icon><ArrowRight /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  Connection,
  CircleCheck,
  QuestionFilled,
  Search,
  CircleCheckFilled,
  ArrowLeft,
  ArrowRight
} from '@element-plus/icons-vue';
import api from '@/api';

const emit = defineEmits(['next', 'prev']);

// 数据
const activePlatform = ref('discord');
const testing = ref({
  discord: false,
  telegram: false,
  feishu: false
});
const detecting = ref(false);

const discordConfig = ref({
  name: '',
  webhookUrl: ''
});

const telegramConfig = ref({
  name: '',
  token: '',
  chatId: ''
});

const feishuConfig = ref({
  name: '',
  appId: '',
  appSecret: '',
  webhookUrl: ''
});

// 计算已配置的Bot
const configuredBots = computed(() => {
  const bots = [];
  
  if (discordConfig.value.webhookUrl) {
    bots.push({
      platform: 'discord',
      name: discordConfig.value.name || 'Discord Bot'
    });
  }
  
  if (telegramConfig.value.token && telegramConfig.value.chatId) {
    bots.push({
      platform: 'telegram',
      name: telegramConfig.value.name || 'Telegram Bot'
    });
  }
  
  if (feishuConfig.value.appId && feishuConfig.value.appSecret) {
    bots.push({
      platform: 'feishu',
      name: feishuConfig.value.name || '飞书Bot'
    });
  }
  
  return bots;
});

// 测试Discord连接
const testDiscord = async () => {
  if (!discordConfig.value.webhookUrl) {
    ElMessage.warning('请先填写Webhook URL');
    return;
  }
  
  testing.value.discord = true;
  
  try {
    const response = await api.post('/api/bots/test/discord', {
      webhook_url: discordConfig.value.webhookUrl
    });
    
    if (response.success) {
      ElMessage.success('Discord连接测试成功！');
    } else {
      ElMessage.error(`测试失败：${response.error}`);
    }
  } catch (error) {
    ElMessage.error('测试失败，请检查Webhook URL是否正确');
  } finally {
    testing.value.discord = false;
  }
};

// 测试Telegram连接
const testTelegram = async () => {
  if (!telegramConfig.value.token || !telegramConfig.value.chatId) {
    ElMessage.warning('请先填写Bot Token和Chat ID');
    return;
  }
  
  testing.value.telegram = true;
  
  try {
    const response = await api.post('/api/bots/test/telegram', {
      token: telegramConfig.value.token,
      chat_id: telegramConfig.value.chatId
    });
    
    if (response.success) {
      ElMessage.success('Telegram连接测试成功！');
    } else {
      ElMessage.error(`测试失败：${response.error}`);
    }
  } catch (error) {
    ElMessage.error('测试失败，请检查Token和Chat ID是否正确');
  } finally {
    testing.value.telegram = false;
  }
};

// 自动获取Telegram Chat ID
const autoDetectChatId = async () => {
  if (!telegramConfig.value.token) {
    ElMessage.warning('请先填写Bot Token');
    return;
  }
  
  detecting.value = true;
  
  ElMessage.info('请在Telegram群组中发送任意消息...');
  
  try {
    const response = await api.post('/api/telegram/detect-chat-id', {
      token: telegramConfig.value.token
    });
    
    if (response.chat_id) {
      telegramConfig.value.chatId = response.chat_id;
      ElMessage.success(`已自动获取Chat ID: ${response.chat_id}`);
    } else {
      ElMessage.warning('未检测到新消息，请确保Bot已加入群组并在群组中发送消息');
    }
  } catch (error) {
    ElMessage.error('自动获取失败，请手动输入Chat ID');
  } finally {
    detecting.value = false;
  }
};

// 测试飞书连接
const testFeishu = async () => {
  if (!feishuConfig.value.appId || !feishuConfig.value.appSecret) {
    ElMessage.warning('请先填写App ID和App Secret');
    return;
  }
  
  testing.value.feishu = true;
  
  try {
    const response = await api.post('/api/bots/test/feishu', {
      app_id: feishuConfig.value.appId,
      app_secret: feishuConfig.value.appSecret
    });
    
    if (response.success) {
      ElMessage.success('飞书连接测试成功！');
    } else {
      ElMessage.error(`测试失败：${response.error}`);
    }
  } catch (error) {
    ElMessage.error('测试失败，请检查App ID和App Secret是否正确');
  } finally {
    testing.value.feishu = false;
  }
};

// 移除Bot配置
const removeBot = (platform) => {
  ElMessageBox.confirm(
    '确定要移除此Bot配置吗？',
    '确认删除',
    {
      type: 'warning'
    }
  ).then(() => {
    if (platform === 'discord') {
      discordConfig.value = { name: '', webhookUrl: '' };
    } else if (platform === 'telegram') {
      telegramConfig.value = { name: '', token: '', chatId: '' };
    } else if (platform === 'feishu') {
      feishuConfig.value = { name: '', appId: '', appSecret: '', webhookUrl: '' };
    }
    ElMessage.success('已移除Bot配置');
  }).catch(() => {});
};

// 保存并进入下一步
const saveAndNext = async () => {
  const botConfigs = [];
  
  if (discordConfig.value.webhookUrl) {
    botConfigs.push({
      platform: 'discord',
      name: discordConfig.value.name || 'Discord Bot',
      config: {
        webhook_url: discordConfig.value.webhookUrl
      }
    });
  }
  
  if (telegramConfig.value.token && telegramConfig.value.chatId) {
    botConfigs.push({
      platform: 'telegram',
      name: telegramConfig.value.name || 'Telegram Bot',
      config: {
        token: telegramConfig.value.token,
        chat_id: telegramConfig.value.chatId
      }
    });
  }
  
  if (feishuConfig.value.appId && feishuConfig.value.appSecret) {
    botConfigs.push({
      platform: 'feishu',
      name: feishuConfig.value.name || '飞书Bot',
      config: {
        app_id: feishuConfig.value.appId,
        app_secret: feishuConfig.value.appSecret,
        webhook_url: feishuConfig.value.webhookUrl
      }
    });
  }
  
  try {
    // 保存到后端
    await api.post('/api/bots/batch', { bots: botConfigs });
    ElMessage.success(`已保存${botConfigs.length}个Bot配置`);
    emit('next', { botConfigs });
  } catch (error) {
    ElMessage.error('保存失败，请重试');
  }
};

// 显示教程
const showDiscordTutorial = () => {
  ElMessageBox.alert(
    '<ol><li>打开Discord服务器设置</li><li>选择"整合" → "Webhook"</li><li>点击"新建Webhook"</li><li>设置名称和频道</li><li>复制Webhook URL</li></ol>',
    'Discord Webhook创建教程',
    { dangerouslyUseHTMLString: true }
  );
};

const showTelegramTutorial = () => {
  ElMessageBox.alert(
    '<ol><li>在Telegram中搜索 @BotFather</li><li>发送 /newbot 命令</li><li>按提示设置Bot名称和用户名</li><li>复制Bot Token</li><li>将Bot添加到群组</li><li>在群组中发送消息，点击"自动获取"Chat ID</li></ol>',
    'Telegram Bot创建教程',
    { dangerouslyUseHTMLString: true }
  );
};

const showFeishuTutorial = () => {
  ElMessageBox.alert(
    '<ol><li>访问飞书开放平台</li><li>创建自建应用</li><li>开启机器人能力</li><li>获取App ID和App Secret</li><li>将机器人添加到群组</li></ol>',
    '飞书应用创建教程',
    { dangerouslyUseHTMLString: true }
  );
};
</script>

<style scoped>
.wizard-bot-config {
  max-width: 900px;
  margin: 0 auto;
}

.step-info {
  margin-bottom: 24px;
}

.alert-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.platform-tabs {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.configured-bots {
  margin-bottom: 24px;
}

.wizard-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #EBEEF5;
}
</style>
