<template>
  <div class="wizard-simple-3steps">
    <!-- 进度指示器 -->
    <div class="progress-bar">
      <div class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
        <div class="step-number">1</div>
        <div class="step-title">欢迎</div>
      </div>
      <div class="step-line" :class="{ active: currentStep > 1 }"></div>
      <div class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
        <div class="step-number">2</div>
        <div class="step-title">登录KOOK</div>
      </div>
      <div class="step-line" :class="{ active: currentStep > 2 }"></div>
      <div class="step" :class="{ active: currentStep >= 3, completed: currentStep > 3 }">
        <div class="step-number">3</div>
        <div class="step-title">选择频道</div>
      </div>
      <div class="step-line" :class="{ active: currentStep > 3 }"></div>
      <div class="step" :class="{ active: currentStep >= 4 }">
        <div class="step-number">✓</div>
        <div class="step-title">完成</div>
      </div>
    </div>

    <!-- 步骤内容 -->
    <div class="wizard-content">
      <!-- 第1步：欢迎页 -->
      <div v-show="currentStep === 1" class="step-content">
        <div class="welcome-page">
          <img src="/icon.png" alt="Logo" class="logo" />
          <h1>🎉 欢迎使用KOOK消息转发系统</h1>
          <p class="subtitle">只需3步，即可开始自动转发消息</p>
          
          <div class="features">
            <div class="feature-item">
              <el-icon :size="40" color="#67C23A"><CircleCheck /></el-icon>
              <h3>零代码配置</h3>
              <p>图形化操作，无需任何编程知识</p>
            </div>
            <div class="feature-item">
              <el-icon :size="40" color="#409EFF"><Connection /></el-icon>
              <h3>多平台支持</h3>
              <p>支持Discord、Telegram、飞书等平台</p>
            </div>
            <div class="feature-item">
              <el-icon :size="40" color="#E6A23C"><Timer /></el-icon>
              <h3>3分钟上手</h3>
              <p>快速配置，立即开始使用</p>
            </div>
          </div>

          <div class="time-estimate">
            <el-icon><Clock /></el-icon>
            预计耗时：3-5分钟
          </div>

          <div class="action-buttons">
            <el-button type="primary" size="large" @click="nextStep">
              开始配置 <el-icon><ArrowRight /></el-icon>
            </el-button>
            <el-button size="large" @click="skipWizard">跳过向导</el-button>
          </div>
        </div>
      </div>

      <!-- 第2步：KOOK登录 -->
      <div v-show="currentStep === 2" class="step-content">
        <div class="login-page">
          <h2>📧 登录KOOK账号</h2>
          <p class="step-description">选择一种方式登录您的KOOK账号</p>

          <el-tabs v-model="loginMethod" class="login-tabs">
            <!-- Cookie导入（推荐） -->
            <el-tab-pane label="Cookie导入（推荐）" name="cookie">
              <div class="cookie-import-section">
                <el-alert 
                  title="最简单的方式：使用Chrome扩展一键导出" 
                  type="success" 
                  :closable="false"
                  show-icon
                >
                  <template #default>
                    <ol>
                      <li>安装Chrome扩展（点击下方按钮）</li>
                      <li>在KOOK网页版登录您的账号</li>
                      <li>点击扩展图标，Cookie会自动导入</li>
                    </ol>
                    <el-button type="success" size="small" @click="installExtension">
                      <el-icon><Download /></el-icon> 下载Chrome扩展
                    </el-button>
                  </template>
                </el-alert>

                <el-divider>或手动导入Cookie</el-divider>

                <!-- 拖拽上传区域 -->
                <div 
                  class="cookie-dropzone"
                  :class="{ 'is-dragover': isDragover }"
                  @dragover.prevent="isDragover = true"
                  @dragleave.prevent="isDragover = false"
                  @drop.prevent="handleCookieDrop"
                >
                  <el-icon :size="60" color="#909399"><UploadFilled /></el-icon>
                  <p>拖拽Cookie JSON文件到此处</p>
                  <p class="hint">或点击下方按钮选择文件</p>
                  <input 
                    type="file" 
                    ref="cookieFileInput" 
                    accept=".json,.txt"
                    style="display: none"
                    @change="handleCookieFileSelect"
                  />
                  <el-button @click="$refs.cookieFileInput.click()">
                    选择文件
                  </el-button>
                </div>

                <!-- 粘贴文本框 -->
                <el-input
                  v-model="cookieText"
                  type="textarea"
                  :rows="4"
                  placeholder="或直接粘贴Cookie JSON文本到这里"
                  class="cookie-textarea"
                />

                <!-- Cookie验证状态 -->
                <div v-if="cookieValidation" class="cookie-validation">
                  <el-alert 
                    :type="cookieValidation.valid ? 'success' : 'error'" 
                    :title="cookieValidation.message"
                    show-icon
                    :closable="false"
                  />
                </div>

                <el-button 
                  type="primary" 
                  :loading="isValidating"
                  :disabled="!cookieText"
                  @click="validateAndImportCookie"
                >
                  验证并导入Cookie
                </el-button>
              </div>
            </el-tab-pane>

            <!-- 账号密码登录 -->
            <el-tab-pane label="账号密码登录" name="password">
              <div class="password-login-section">
                <el-form :model="loginForm" label-width="100px">
                  <el-form-item label="邮箱地址">
                    <el-input 
                      v-model="loginForm.email" 
                      placeholder="请输入KOOK邮箱"
                      clearable
                    >
                      <template #prefix>
                        <el-icon><Message /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>

                  <el-form-item label="密码">
                    <el-input 
                      v-model="loginForm.password" 
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

                  <el-alert 
                    title="首次登录可能需要验证码" 
                    type="info" 
                    :closable="false"
                    show-icon
                  >
                    <template #default>
                      如果出现验证码，系统会自动弹窗让您输入
                    </template>
                  </el-alert>

                  <el-button 
                    type="primary" 
                    :loading="isLoggingIn"
                    :disabled="!loginForm.email || !loginForm.password"
                    @click="loginWithPassword"
                    style="width: 100%; margin-top: 20px;"
                  >
                    登录
                  </el-button>
                </el-form>
              </div>
            </el-tab-pane>
          </el-tabs>

          <!-- 帮助链接 -->
          <div class="help-links">
            <el-link type="primary" @click="showCookieHelp">
              <el-icon><QuestionFilled /></el-icon> 如何获取Cookie？
            </el-link>
            <el-link type="primary" @click="showVideoTutorial">
              <el-icon><VideoPlay /></el-icon> 观看视频教程
            </el-link>
          </div>
        </div>
      </div>

      <!-- 第3步：选择服务器和频道 -->
      <div v-show="currentStep === 3" class="step-content">
        <div class="server-selection-page">
          <h2>🏠 选择要监听的KOOK服务器</h2>
          <p class="step-description">勾选您想要转发消息的服务器和频道</p>

          <!-- 加载状态 -->
          <div v-if="isLoadingServers" class="loading-state">
            <el-icon class="is-loading" :size="40"><Loading /></el-icon>
            <p>正在获取您的服务器列表...</p>
          </div>

          <!-- 服务器列表 -->
          <div v-else class="server-list">
            <el-alert 
              v-if="servers.length === 0"
              title="未找到服务器" 
              type="warning"
              :closable="false"
            >
              您的账号似乎没有加入任何KOOK服务器，请先在KOOK中加入服务器后再配置。
            </el-alert>

            <div v-else class="server-tree">
              <!-- 快捷操作 -->
              <div class="quick-actions">
                <el-button size="small" @click="selectAll">全选</el-button>
                <el-button size="small" @click="unselectAll">全不选</el-button>
                <span class="selection-count">
                  已选择：{{ selectedChannelCount }} 个频道
                </span>
              </div>

              <!-- 服务器树形结构 -->
              <el-tree
                ref="serverTree"
                :data="servers"
                :props="treeProps"
                show-checkbox
                node-key="id"
                :default-checked-keys="defaultChecked"
                @check="handleTreeCheck"
                class="server-channel-tree"
              >
                <template #default="{ node, data }">
                  <span class="tree-node">
                    <el-icon v-if="data.type === 'server'">
                      <OfficeBuilding />
                    </el-icon>
                    <el-icon v-else-if="data.channel_type === 'text'">
                      <ChatDotRound />
                    </el-icon>
                    <el-icon v-else>
                      <Microphone />
                    </el-icon>
                    <span class="node-label">{{ data.name }}</span>
                    <el-tag v-if="data.type === 'server'" size="small" type="info">
                      {{ data.children?.length || 0 }} 个频道
                    </el-tag>
                  </span>
                </template>
              </el-tree>
            </div>

            <el-alert 
              v-if="selectedChannelCount > 20"
              title="提示：选择了较多频道" 
              type="warning"
              :closable="false"
              style="margin-top: 20px;"
            >
              您选择了 {{ selectedChannelCount }} 个频道，可能会产生大量消息。建议先从重要频道开始配置。
            </el-alert>
          </div>
        </div>
      </div>

      <!-- 第4步：完成 -->
      <div v-show="currentStep === 4" class="step-content">
        <div class="completion-page">
          <el-result icon="success" title="配置完成！" sub-title="您已成功完成基础配置">
            <template #extra>
              <div class="completion-info">
                <h3>✅ 已配置项</h3>
                <ul>
                  <li>✓ KOOK账号已登录</li>
                  <li>✓ 已选择 {{ selectedChannelCount }} 个频道进行监听</li>
                  <li>✓ 系统已就绪，可以开始监听消息</li>
                </ul>

                <el-divider />

                <h3>📋 接下来您可以：</h3>
                <div class="next-steps">
                  <el-card shadow="hover" @click="goToBotsConfig">
                    <div class="next-step-card">
                      <el-icon :size="40"><Connection /></el-icon>
                      <h4>配置转发Bot</h4>
                      <p>设置Discord/Telegram/飞书Bot，开始转发消息</p>
                      <el-button type="primary" size="small">立即配置</el-button>
                    </div>
                  </el-card>

                  <el-card shadow="hover" @click="goToMapping">
                    <div class="next-step-card">
                      <el-icon :size="40"><Connection /></el-icon>
                      <h4>设置频道映射</h4>
                      <p>配置KOOK频道与目标平台的对应关系</p>
                      <el-button type="primary" size="small">立即设置</el-button>
                    </div>
                  </el-card>

                  <el-card shadow="hover" @click="startListening">
                    <div class="next-step-card">
                      <el-icon :size="40"><VideoPlay /></el-icon>
                      <h4>仅监听消息</h4>
                      <p>先不转发，只监听和记录KOOK消息</p>
                      <el-button type="success" size="small">开始监听</el-button>
                    </div>
                  </el-card>
                </div>

                <el-alert 
                  title="💡 提示：您可以稍后在"设置"中随时修改这些配置" 
                  type="info"
                  :closable="false"
                  show-icon
                  style="margin-top: 20px;"
                />
              </div>
            </template>
          </el-result>

          <div class="completion-actions">
            <el-button type="primary" size="large" @click="goToHome">
              进入主界面
            </el-button>
            <el-button size="large" @click="restartWizard">
              重新配置
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 导航按钮 -->
    <div class="wizard-footer" v-if="currentStep < 4">
      <el-button 
        v-if="currentStep > 1" 
        @click="prevStep"
        :disabled="isLoading"
      >
        上一步
      </el-button>
      <div style="flex: 1"></div>
      <el-button 
        v-if="currentStep < 3"
        type="primary" 
        @click="nextStep"
        :disabled="!canProceed"
        :loading="isLoading"
      >
        下一步
      </el-button>
      <el-button 
        v-if="currentStep === 3"
        type="primary" 
        @click="finishWizard"
        :disabled="selectedChannelCount === 0"
        :loading="isSaving"
      >
        完成配置
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  CircleCheck, Connection, Timer, Clock, ArrowRight,
  Download, UploadFilled, Message, Lock, QuestionFilled,
  VideoPlay, Loading, OfficeBuilding, ChatDotRound,
  Microphone
} from '@element-plus/icons-vue';
import axios from 'axios';

const router = useRouter();

// 当前步骤
const currentStep = ref(1);

// 第2步：登录相关
const loginMethod = ref('cookie');
const cookieText = ref('');
const isDragover = ref(false);
const cookieValidation = ref(null);
const isValidating = ref(false);
const isLoggingIn = ref(false);
const loginForm = ref({
  email: '',
  password: ''
});
const accountId = ref(null); // 登录后的账号ID

// 第3步：服务器选择
const isLoadingServers = ref(false);
const servers = ref([]);
const defaultChecked = ref([]);
const selectedChannels = ref([]);
const treeProps = {
  children: 'children',
  label: 'name'
};

// 其他状态
const isLoading = ref(false);
const isSaving = ref(false);

// 计算属性
const canProceed = computed(() => {
  if (currentStep.value === 1) return true;
  if (currentStep.value === 2) return accountId.value !== null;
  if (currentStep.value === 3) return selectedChannelCount.value > 0;
  return true;
});

const selectedChannelCount = computed(() => {
  return selectedChannels.value.length;
});

// 方法：下一步
const nextStep = async () => {
  if (currentStep.value === 2 && !accountId.value) {
    ElMessage.warning('请先完成KOOK账号登录');
    return;
  }
  
  if (currentStep.value === 2) {
    // 进入第3步前，加载服务器列表
    await loadServers();
  }
  
  currentStep.value++;
};

// 方法：上一步
const prevStep = () => {
  currentStep.value--;
};

// 方法：跳过向导
const skipWizard = () => {
  ElMessageBox.confirm(
    '跳过配置向导后，您需要手动在各个页面配置。确定要跳过吗？',
    '确认跳过',
    {
      confirmButtonText: '确定跳过',
      cancelButtonText: '继续配置',
      type: 'warning'
    }
  ).then(() => {
    router.push('/');
  }).catch(() => {});
};

// 方法：Cookie导入
const handleCookieDrop = (e) => {
  isDragover.value = false;
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    readCookieFile(files[0]);
  }
};

const handleCookieFileSelect = (e) => {
  const files = e.target.files;
  if (files.length > 0) {
    readCookieFile(files[0]);
  }
};

const readCookieFile = (file) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    cookieText.value = e.target.result;
    ElMessage.success('文件读取成功，请点击"验证并导入"');
  };
  reader.onerror = () => {
    ElMessage.error('文件读取失败');
  };
  reader.readAsText(file);
};

const validateAndImportCookie = async () => {
  isValidating.value = true;
  cookieValidation.value = null;

  try {
    // 验证Cookie格式
    let cookieData;
    try {
      cookieData = JSON.parse(cookieText.value);
    } catch {
      cookieValidation.value = {
        valid: false,
        message: '❌ Cookie格式错误：不是有效的JSON格式。请从浏览器开发者工具复制正确的Cookie数据。'
      };
      return;
    }

    // 调用后端验证API
    const response = await axios.post('http://localhost:9527/api/cookie-import/validate', {
      cookie: cookieData
    });

    if (response.data.valid) {
      // Cookie有效，导入
      const importResponse = await axios.post('http://localhost:9527/api/accounts', {
        import_type: 'cookie',
        cookie: cookieData
      });

      accountId.value = importResponse.data.id;
      cookieValidation.value = {
        valid: true,
        message: '✅ Cookie验证成功！账号已导入。'
      };

      ElMessage.success('Cookie导入成功，可以进入下一步');
    } else {
      cookieValidation.value = {
        valid: false,
        message: `❌ Cookie验证失败：${response.data.error || '未知错误'}`
      };
    }
  } catch (error) {
    cookieValidation.value = {
      valid: false,
      message: `❌ 验证失败：${error.response?.data?.detail || error.message}`
    };
  } finally {
    isValidating.value = false;
  }
};

// 方法：账号密码登录
const loginWithPassword = async () => {
  isLoggingIn.value = true;

  try {
    const response = await axios.post('http://localhost:9527/api/accounts/login', {
      email: loginForm.value.email,
      password: loginForm.value.password
    });

    accountId.value = response.data.id;
    ElMessage.success('登录成功！');
  } catch (error) {
    ElMessage.error(`登录失败：${error.response?.data?.detail || error.message}`);
  } finally {
    isLoggingIn.value = false;
  }
};

// 方法：加载服务器列表
const loadServers = async () => {
  isLoadingServers.value = true;

  try {
    const response = await axios.get(`http://localhost:9527/api/servers/discover/${accountId.value}`);
    
    // 转换为树形结构
    servers.value = response.data.servers.map(server => ({
      id: `server-${server.id}`,
      name: server.name,
      type: 'server',
      children: server.channels.map(channel => ({
        id: `channel-${channel.id}`,
        name: `#${channel.name}`,
        type: 'channel',
        channel_type: channel.type,
        server_id: server.id,
        channel_id: channel.id
      }))
    }));

    ElMessage.success(`成功获取 ${servers.value.length} 个服务器`);
  } catch (error) {
    ElMessage.error(`获取服务器列表失败：${error.response?.data?.detail || error.message}`);
    // 提供模拟数据（用于测试）
    servers.value = [
      {
        id: 'server-demo',
        name: '示例服务器（获取失败时的演示）',
        type: 'server',
        children: [
          { id: 'channel-1', name: '#公告频道', type: 'channel', channel_type: 'text' },
          { id: 'channel-2', name: '#技术讨论', type: 'channel', channel_type: 'text' }
        ]
      }
    ];
  } finally {
    isLoadingServers.value = false;
  }
};

// 方法：树形控件勾选
const handleTreeCheck = (data, checked) => {
  // 更新选中的频道列表
  const checkedNodes = checked.checkedNodes.filter(node => node.type === 'channel');
  selectedChannels.value = checkedNodes.map(node => ({
    server_id: node.server_id,
    channel_id: node.channel_id,
    channel_name: node.name
  }));
};

// 方法：全选/全不选
const selectAll = () => {
  const allChannelIds = [];
  servers.value.forEach(server => {
    server.children?.forEach(channel => {
      allChannelIds.push(channel.id);
    });
  });
  defaultChecked.value = allChannelIds;
  // 手动触发树的更新
  setTimeout(() => {
    const tree = document.querySelector('.server-channel-tree');
    if (tree) {
      const checkboxes = tree.querySelectorAll('.el-tree-node__content');
      checkboxes.forEach(cb => {
        const checkbox = cb.querySelector('.el-checkbox__input');
        if (checkbox && !checkbox.classList.contains('is-checked')) {
          cb.click();
        }
      });
    }
  }, 100);
};

const unselectAll = () => {
  defaultChecked.value = [];
  selectedChannels.value = [];
  // 手动触发树的更新
  setTimeout(() => {
    const tree = document.querySelector('.server-channel-tree');
    if (tree) {
      const checkboxes = tree.querySelectorAll('.el-tree-node__content');
      checkboxes.forEach(cb => {
        const checkbox = cb.querySelector('.el-checkbox__input');
        if (checkbox && checkbox.classList.contains('is-checked')) {
          cb.click();
        }
      });
    }
  }, 100);
};

// 方法：完成向导
const finishWizard = async () => {
  isSaving.value = true;

  try {
    // 保存选中的频道到数据库
    await axios.post('http://localhost:9527/api/accounts/channels', {
      account_id: accountId.value,
      channels: selectedChannels.value
    });

    // 标记向导已完成
    localStorage.setItem('wizard_completed', 'true');
    
    currentStep.value = 4;
    ElMessage.success('配置保存成功！');
  } catch (error) {
    ElMessage.error(`保存配置失败：${error.response?.data?.detail || error.message}`);
  } finally {
    isSaving.value = false;
  }
};

// 方法：帮助和教程
const installExtension = () => {
  window.open('/chrome-extension/manifest.json', '_blank');
  ElMessage.info('请按照说明安装Chrome扩展');
};

const showCookieHelp = () => {
  router.push('/help?topic=cookie');
};

const showVideoTutorial = () => {
  router.push('/help?topic=video');
};

// 方法：完成后的操作
const goToBotsConfig = () => {
  router.push('/bots');
};

const goToMapping = () => {
  router.push('/mapping');
};

const startListening = async () => {
  try {
    await axios.post(`http://localhost:9527/api/accounts/${accountId.value}/start`);
    ElMessage.success('已开始监听消息');
    router.push('/logs');
  } catch (error) {
    ElMessage.error(`启动失败：${error.response?.data?.detail || error.message}`);
  }
};

const goToHome = () => {
  router.push('/');
};

const restartWizard = () => {
  currentStep.value = 1;
  accountId.value = null;
  selectedChannels.value = [];
  cookieText.value = '';
  cookieValidation.value = null;
};

onMounted(() => {
  // 检查是否已有账号
  axios.get('http://localhost:9527/api/accounts').then(response => {
    if (response.data.length > 0) {
      ElMessageBox.confirm(
        '检测到您已经配置过账号，是否跳过向导直接进入主界面？',
        '提示',
        {
          confirmButtonText: '进入主界面',
          cancelButtonText: '重新配置',
          type: 'info'
        }
      ).then(() => {
        router.push('/');
      }).catch(() => {});
    }
  });
});
</script>

<style scoped>
.wizard-simple-3steps {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

/* 进度条 */
.progress-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 800px;
  margin: 0 auto 40px;
  padding: 30px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  opacity: 0.5;
  transition: all 0.3s;
}

.step.active {
  opacity: 1;
}

.step.completed .step-number {
  background: #67C23A;
  color: white;
}

.step-number {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  color: #666;
  transition: all 0.3s;
}

.step.active .step-number {
  background: #409EFF;
  color: white;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

.step-title {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.step.active .step-title {
  color: #409EFF;
  font-weight: 600;
}

.step-line {
  flex: 1;
  height: 3px;
  background: #e0e0e0;
  margin: 0 10px;
  transition: all 0.3s;
}

.step-line.active {
  background: #67C23A;
}

/* 步骤内容 */
.wizard-content {
  max-width: 900px;
  margin: 0 auto;
  background: white;
  border-radius: 15px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  min-height: 500px;
}

.step-content {
  animation: fadeIn 0.5s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 欢迎页 */
.welcome-page {
  text-align: center;
}

.logo {
  width: 100px;
  height: 100px;
  margin-bottom: 20px;
}

.welcome-page h1 {
  font-size: 32px;
  color: #333;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 18px;
  color: #666;
  margin-bottom: 40px;
}

.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  margin-bottom: 40px;
}

.feature-item {
  text-align: center;
}

.feature-item h3 {
  margin: 15px 0 10px;
  color: #333;
}

.feature-item p {
  color: #666;
  font-size: 14px;
}

.time-estimate {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #E6A23C;
  font-size: 16px;
  margin-bottom: 30px;
}

.action-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
}

/* 登录页 */
.login-page h2 {
  text-align: center;
  margin-bottom: 10px;
  color: #333;
}

.step-description {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
}

.login-tabs {
  margin-bottom: 20px;
}

.cookie-dropzone {
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  margin: 20px 0;
}

.cookie-dropzone:hover,
.cookie-dropzone.is-dragover {
  border-color: #409EFF;
  background: #ecf5ff;
}

.cookie-dropzone p {
  margin: 10px 0;
  color: #666;
}

.cookie-dropzone .hint {
  font-size: 12px;
  color: #999;
}

.cookie-textarea {
  margin: 20px 0;
}

.cookie-validation {
  margin: 20px 0;
}

.help-links {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

/* 服务器选择页 */
.server-selection-page h2 {
  text-align: center;
  margin-bottom: 10px;
  color: #333;
}

.loading-state {
  text-align: center;
  padding: 60px 0;
  color: #666;
}

.server-tree {
  margin-top: 20px;
}

.quick-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.selection-count {
  margin-left: auto;
  color: #409EFF;
  font-weight: 600;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.node-label {
  flex: 1;
}

.server-channel-tree {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 10px;
}

/* 完成页 */
.completion-page {
  text-align: center;
}

.completion-info {
  text-align: left;
  max-width: 600px;
  margin: 0 auto;
}

.completion-info h3 {
  color: #333;
  margin-bottom: 15px;
}

.completion-info ul {
  list-style: none;
  padding: 0;
}

.completion-info ul li {
  padding: 8px 0;
  color: #666;
  font-size: 15px;
}

.next-steps {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin: 20px 0;
}

.next-step-card {
  text-align: center;
  cursor: pointer;
  padding: 10px;
}

.next-step-card h4 {
  margin: 15px 0 10px;
  color: #333;
}

.next-step-card p {
  color: #666;
  font-size: 13px;
  margin-bottom: 15px;
  min-height: 40px;
}

.completion-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 40px;
}

/* 底部导航 */
.wizard-footer {
  display: flex;
  gap: 20px;
  max-width: 900px;
  margin: 30px auto 0;
  padding: 20px;
}
</style>
