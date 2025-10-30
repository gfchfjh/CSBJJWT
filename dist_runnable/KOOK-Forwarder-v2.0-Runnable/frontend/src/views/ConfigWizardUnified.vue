<template>
  <div class="wizard-unified">
    <!-- 🚀 P0-2优化: 统一的3步配置向导 -->
    
    <!-- 进度指示器 -->
    <el-card class="wizard-header">
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="登录KOOK" description="1分钟">
          <template #icon>
            <el-icon><User /></el-icon>
          </template>
        </el-step>
        <el-step title="配置Bot" description="2分钟">
          <template #icon>
            <el-icon><Robot /></el-icon>
          </template>
        </el-step>
        <el-step title="智能映射" description="2分钟">
          <template #icon>
            <el-icon><Connection /></el-icon>
          </template>
        </el-step>
      </el-steps>
      
      <!-- 进度追踪 -->
      <div class="progress-tracker">
        <el-progress
          :percentage="overallProgress"
          :stroke-width="8"
          :color="progressColor"
        >
          <template #default="{ percentage }">
            <span class="progress-text">{{ Math.floor(percentage) }}%</span>
          </template>
        </el-progress>
        <p class="progress-hint">{{ progressHint }}</p>
      </div>
    </el-card>
    
    <!-- 步骤1: 登录KOOK -->
    <el-card v-show="currentStep === 0" class="wizard-step">
      <template #header>
        <div class="step-header">
          <h2>📧 第1步：登录KOOK账号</h2>
          <el-tag>预计1分钟</el-tag>
        </div>
      </template>
      
      <el-tabs v-model="loginMethod" @tab-change="handleLoginMethodChange">
        <!-- Chrome扩展方式（推荐） -->
        <el-tab-pane label="Chrome扩展（推荐）" name="extension">
          <div class="login-method-content">
            <el-alert type="success" :closable="false" show-icon>
              <template #title>
                <strong>最简单的方式！</strong>
              </template>
              2步完成，无需手动复制粘贴
            </el-alert>
            
            <ol class="instruction-list">
              <li>
                <span class="step-number">1</span>
                <div class="step-content">
                  <strong>安装Chrome扩展</strong>
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="installExtension"
                    :loading="installingExtension"
                  >
                    {{ extensionInstalled ? '✅ 已安装' : '📥 安装扩展' }}
                  </el-button>
                </div>
              </li>
              <li>
                <span class="step-number">2</span>
                <div class="step-content">
                  <strong>访问KOOK并登录</strong>
                  <el-button 
                    type="primary" 
                    link 
                    @click="openKook"
                  >
                    🔗 打开KOOK
                  </el-button>
                </div>
              </li>
              <li>
                <span class="step-number">3</span>
                <div class="step-content">
                  <strong>点击扩展图标，一键导出</strong>
                  <p class="hint">快捷键: <kbd>Ctrl+Shift+K</kbd></p>
                </div>
              </li>
              <li>
                <span class="step-number">4</span>
                <div class="step-content">
                  <strong>自动检测到Cookie</strong>
                  <el-alert 
                    v-if="cookieDetected" 
                    type="success" 
                    :closable="false"
                  >
                    ✅ 检测到Cookie（{{ cookieCount }}个），点击"下一步"继续
                  </el-alert>
                  <el-alert 
                    v-else 
                    type="info" 
                    :closable="false"
                  >
                    ⏳ 等待导出Cookie...
                  </el-alert>
                </div>
              </li>
            </ol>
          </div>
        </el-tab-pane>
        
        <!-- 账号密码方式 -->
        <el-tab-pane label="账号密码" name="password">
          <div class="login-method-content">
            <el-alert type="info" :closable="false" show-icon>
              输入KOOK账号密码，自动登录
            </el-alert>
            
            <el-form 
              ref="passwordFormRef"
              :model="passwordForm"
              :rules="passwordRules"
              label-width="80px"
              style="margin-top: 20px"
            >
              <el-form-item label="邮箱" prop="email">
                <el-input 
                  v-model="passwordForm.email"
                  placeholder="your@email.com"
                  clearable
                >
                  <template #prefix>
                    <el-icon><Message /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item label="密码" prop="password">
                <el-input 
                  v-model="passwordForm.password"
                  type="password"
                  placeholder="请输入密码"
                  show-password
                  clearable
                >
                  <template #prefix>
                    <el-icon><Lock /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="loginWithPassword"
                  :loading="loggingIn"
                  style="width: 100%"
                >
                  🔐 登录
                </el-button>
              </el-form-item>
            </el-form>
            
            <el-alert 
              v-if="loginError"
              type="error"
              :closable="false"
              show-icon
            >
              {{ loginError }}
            </el-alert>
          </div>
        </el-tab-pane>
        
        <!-- Cookie导入方式 -->
        <el-tab-pane label="导入Cookie" name="cookie">
          <div class="login-method-content">
            <el-alert type="warning" :closable="false" show-icon>
              适合高级用户，需要手动获取Cookie
            </el-alert>
            
            <div class="cookie-import-area">
              <el-input
                v-model="cookieInput"
                type="textarea"
                :rows="8"
                placeholder="粘贴Cookie JSON数据或浏览器Cookie字符串..."
                @input="validateCookieInput"
              />
              
              <div class="cookie-import-actions">
                <el-button @click="pasteFromClipboard">
                  📋 从剪贴板粘贴
                </el-button>
                <el-upload
                  :auto-upload="false"
                  :show-file-list="false"
                  accept=".json,.txt"
                  @change="handleCookieFileUpload"
                >
                  <el-button>
                    📁 从文件导入
                  </el-button>
                </el-upload>
              </div>
              
              <el-alert 
                v-if="cookieValidation.valid"
                type="success"
                :closable="false"
              >
                ✅ Cookie格式正确（{{ cookieValidation.count }}个）
              </el-alert>
              <el-alert 
                v-else-if="cookieInput && !cookieValidation.valid"
                type="error"
                :closable="false"
              >
                ❌ {{ cookieValidation.error }}
              </el-alert>
              
              <el-button 
                v-if="cookieValidation.valid"
                type="primary"
                @click="importCookie"
                :loading="importingCookie"
                style="width: 100%; margin-top: 10px"
              >
                ✅ 导入Cookie
              </el-button>
            </div>
            
            <el-divider />
            
            <div class="cookie-help">
              <h4>📖 如何获取Cookie？</h4>
              <el-collapse>
                <el-collapse-item title="Chrome浏览器" name="chrome">
                  <ol>
                    <li>访问KOOK并登录</li>
                    <li>按F12打开开发者工具</li>
                    <li>切换到"Application"标签</li>
                    <li>左侧选择"Cookies" > "https://www.kookapp.cn"</li>
                    <li>复制所有Cookie</li>
                  </ol>
                </el-collapse-item>
                <el-collapse-item title="使用Chrome扩展（推荐）" name="extension-help">
                  <p>使用"Chrome扩展"方式更简单快捷</p>
                </el-collapse-item>
              </el-collapse>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
      
      <!-- 底部按钮 -->
      <div class="wizard-actions">
        <el-button @click="skipWizard">跳过向导</el-button>
        <el-button 
          type="primary" 
          @click="nextStep"
          :disabled="!canProceedFromStep1"
        >
          下一步 →
        </el-button>
      </div>
    </el-card>
    
    <!-- 步骤2: 配置Bot -->
    <el-card v-show="currentStep === 1" class="wizard-step">
      <template #header>
        <div class="step-header">
          <h2>🤖 第2步：配置Bot</h2>
          <el-tag>预计2分钟</el-tag>
        </div>
      </template>
      
      <el-tabs v-model="botPlatform">
        <!-- Discord -->
        <el-tab-pane label="Discord" name="discord">
          <div class="bot-config-content">
            <el-alert type="info" :closable="false" show-icon>
              配置Discord Webhook，用于接收KOOK消息
            </el-alert>
            
            <el-form 
              :model="discordBot"
              label-width="100px"
              style="margin-top: 20px"
            >
              <el-form-item label="Bot名称">
                <el-input 
                  v-model="discordBot.name"
                  placeholder="例如：游戏公告Bot"
                />
              </el-form-item>
              
              <el-form-item label="Webhook URL">
                <el-input 
                  v-model="discordBot.webhookUrl"
                  placeholder="https://discord.com/api/webhooks/..."
                  clearable
                />
              </el-form-item>
              
              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="testDiscordBot"
                  :loading="testingBot"
                >
                  🧪 测试连接
                </el-button>
                <el-button @click="viewDiscordTutorial">
                  📖 查看教程
                </el-button>
              </el-form-item>
              
              <el-alert 
                v-if="botTestResult.discord"
                :type="botTestResult.discord.success ? 'success' : 'error'"
                :closable="false"
              >
                {{ botTestResult.discord.message }}
              </el-alert>
            </el-form>
          </div>
        </el-tab-pane>
        
        <!-- Telegram -->
        <el-tab-pane label="Telegram" name="telegram">
          <div class="bot-config-content">
            <el-alert type="info" :closable="false" show-icon>
              配置Telegram Bot，用于接收KOOK消息
            </el-alert>
            
            <el-form 
              :model="telegramBot"
              label-width="100px"
              style="margin-top: 20px"
            >
              <el-form-item label="Bot名称">
                <el-input 
                  v-model="telegramBot.name"
                  placeholder="例如：游戏公告TG Bot"
                />
              </el-form-item>
              
              <el-form-item label="Bot Token">
                <el-input 
                  v-model="telegramBot.token"
                  placeholder="1234567890:ABCdefGHI..."
                  clearable
                />
              </el-form-item>
              
              <el-form-item label="Chat ID">
                <el-input 
                  v-model="telegramBot.chatId"
                  placeholder="-1001234567890"
                  clearable
                >
                  <template #append>
                    <el-button @click="autoGetChatId">🔍 自动获取</el-button>
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="testTelegramBot"
                  :loading="testingBot"
                >
                  🧪 测试连接
                </el-button>
                <el-button @click="viewTelegramTutorial">
                  📖 查看教程
                </el-button>
              </el-form-item>
              
              <el-alert 
                v-if="botTestResult.telegram"
                :type="botTestResult.telegram.success ? 'success' : 'error'"
                :closable="false"
              >
                {{ botTestResult.telegram.message }}
              </el-alert>
            </el-form>
          </div>
        </el-tab-pane>
        
        <!-- 飞书 -->
        <el-tab-pane label="飞书" name="feishu">
          <div class="bot-config-content">
            <el-alert type="info" :closable="false" show-icon>
              配置飞书自建应用，用于接收KOOK消息
            </el-alert>
            
            <el-form 
              :model="feishuBot"
              label-width="100px"
              style="margin-top: 20px"
            >
              <el-form-item label="应用名称">
                <el-input 
                  v-model="feishuBot.name"
                  placeholder="例如：游戏公告飞书Bot"
                />
              </el-form-item>
              
              <el-form-item label="App ID">
                <el-input 
                  v-model="feishuBot.appId"
                  placeholder="cli_a1b2c3d4..."
                  clearable
                />
              </el-form-item>
              
              <el-form-item label="App Secret">
                <el-input 
                  v-model="feishuBot.appSecret"
                  type="password"
                  placeholder="ABCdefGHI..."
                  show-password
                  clearable
                />
              </el-form-item>
              
              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="testFeishuBot"
                  :loading="testingBot"
                >
                  🧪 测试连接
                </el-button>
                <el-button @click="viewFeishuTutorial">
                  📖 查看教程
                </el-button>
              </el-form-item>
              
              <el-alert 
                v-if="botTestResult.feishu"
                :type="botTestResult.feishu.success ? 'success' : 'error'"
                :closable="false"
              >
                {{ botTestResult.feishu.message }}
              </el-alert>
            </el-form>
          </div>
        </el-tab-pane>
      </el-tabs>
      
      <!-- 已配置的Bot列表 -->
      <el-divider />
      
      <div v-if="configuredBots.length > 0" class="configured-bots">
        <h3>已配置的Bot ({{ configuredBots.length }})</h3>
        <el-table :data="configuredBots" stripe>
          <el-table-column label="平台" width="100">
            <template #default="{ row }">
              <el-tag>{{ row.platform }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="名称" prop="name" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.tested ? 'success' : 'info'">
                {{ row.tested ? '✅ 已测试' : '⏳ 未测试' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button 
                link 
                type="danger" 
                size="small"
                @click="removeBot(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 底部按钮 -->
      <div class="wizard-actions">
        <el-button @click="prevStep">← 上一步</el-button>
        <el-button 
          type="primary" 
          @click="nextStep"
          :disabled="!canProceedFromStep2"
        >
          下一步 →
        </el-button>
      </div>
    </el-card>
    
    <!-- 步骤3: 智能映射 -->
    <el-card v-show="currentStep === 2" class="wizard-step">
      <template #header>
        <div class="step-header">
          <h2>🔀 第3步：智能映射</h2>
          <el-tag>预计2分钟</el-tag>
        </div>
      </template>
      
      <el-alert type="success" :closable="false" show-icon>
        <template #title>
          <strong>AI智能推荐</strong>
        </template>
        基于频道名称相似度，自动推荐映射关系
      </el-alert>
      
      <div class="mapping-content">
        <!-- KOOK频道列表 -->
        <div class="channels-section">
          <h3>KOOK频道</h3>
          <el-tree
            ref="kookChannelTreeRef"
            :data="kookChannels"
            node-key="id"
            @node-click="selectKookChannel"
            highlight-current
          >
            <template #default="{ node, data }">
              <span class="tree-node">
                <el-icon v-if="data.type === 'server'"><Folder /></el-icon>
                <el-icon v-else><ChatDotRound /></el-icon>
                <span>{{ node.label }}</span>
              </span>
            </template>
          </el-tree>
        </div>
        
        <!-- AI推荐映射 -->
        <div v-if="selectedKookChannel" class="recommendations-section">
          <h3>{{ selectedKookChannel.name }} → AI推荐映射</h3>
          
          <el-table 
            :data="mappingRecommendations"
            style="width: 100%"
            @selection-change="handleMappingSelection"
          >
            <el-table-column type="selection" width="55" />
            
            <el-table-column label="平台" width="100">
              <template #default="{ row }">
                <el-tag>{{ row.platform }}</el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="频道名称" prop="name" />
            
            <el-table-column label="置信度" width="150">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.confidence * 100"
                  :color="getConfidenceColor(row.confidence)"
                  :show-text="false"
                  style="width: 80px"
                />
                <span style="margin-left: 10px">
                  {{ (row.confidence * 100).toFixed(0) }}%
                </span>
              </template>
            </el-table-column>
            
            <el-table-column label="推荐原因" prop="reason" />
          </el-table>
          
          <div class="mapping-actions">
            <el-button 
              v-if="highConfidenceCount > 0"
              type="primary"
              @click="applyAllHighConfidence"
            >
              ⚡ 一键应用高置信度推荐（{{ highConfidenceCount }}个）
            </el-button>
            <el-button 
              v-if="selectedMappings.length > 0"
              type="primary"
              @click="applySelectedMappings"
            >
              ✅ 应用选中的映射（{{ selectedMappings.length }}个）
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 已创建的映射 -->
      <el-divider />
      
      <div v-if="createdMappings.length > 0" class="created-mappings">
        <h3>已创建的映射 ({{ createdMappings.length }})</h3>
        <el-table :data="createdMappings" stripe>
          <el-table-column label="KOOK频道" prop="kook_channel_name" />
          <el-table-column label="目标平台" width="100">
            <template #default="{ row }">
              <el-tag>{{ row.target_platform }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="目标频道" prop="target_channel_name" />
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button 
                link 
                type="danger" 
                size="small"
                @click="removeMapping(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 底部按钮 -->
      <div class="wizard-actions">
        <el-button @click="prevStep">← 上一步</el-button>
        <el-button 
          type="success" 
          @click="completeWizard"
          :disabled="!canCompleteWizard"
        >
          完成配置 🎉
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
// 由于长度限制，脚本部分将在下一个文件中继续
</script>

<style scoped>
/* 样式将在单独的CSS文件中 */
</style>
