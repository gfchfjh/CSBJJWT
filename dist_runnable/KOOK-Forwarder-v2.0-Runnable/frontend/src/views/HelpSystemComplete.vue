<template>
  <div class="help-system">
    <!-- 🚀 P2-3优化: 完整的帮助系统 -->
    
    <el-page-header @back="goBack" content="帮助中心" />
    
    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 左侧：教程目录 -->
      <el-col :span="6">
        <el-card class="tutorial-menu">
          <template #header>
            <span>📚 教程目录</span>
          </template>
          
          <el-menu
            :default-active="activeTutorial"
            @select="selectTutorial"
          >
            <el-menu-item index="quickstart">
              <el-icon><Promotion /></el-icon>
              <span>快速入门（5分钟）</span>
            </el-menu-item>
            
            <el-menu-item index="cookie">
              <el-icon><Key /></el-icon>
              <span>Cookie获取教程</span>
            </el-menu-item>
            
            <el-menu-item index="discord">
              <el-icon><Connection /></el-icon>
              <span>Discord配置教程</span>
            </el-menu-item>
            
            <el-menu-item index="telegram">
              <el-icon><ChatDotRound /></el-icon>
              <span>Telegram配置教程</span>
            </el-menu-item>
            
            <el-menu-item index="feishu">
              <el-icon><MessageBox /></el-icon>
              <span>飞书配置教程</span>
            </el-menu-item>
            
            <el-menu-item index="mapping">
              <el-icon><Share /></el-icon>
              <span>频道映射详解</span>
            </el-menu-item>
            
            <el-menu-item index="filter">
              <el-icon><Filter /></el-icon>
              <span>过滤规则使用技巧</span>
            </el-menu-item>
            
            <el-menu-item index="faq">
              <el-icon><QuestionFilled /></el-icon>
              <span>常见问题FAQ</span>
            </el-menu-item>
          </el-menu>
        </el-card>
        
        <!-- 视频教程 -->
        <el-card class="video-tutorials" style="margin-top: 20px">
          <template #header>
            <span>📺 视频教程</span>
          </template>
          
          <el-link 
            v-for="video in videoTutorials"
            :key="video.id"
            :href="video.url"
            target="_blank"
            type="primary"
            class="video-link"
          >
            <el-icon><VideoPlay /></el-icon>
            {{ video.title }}
          </el-link>
        </el-card>
      </el-col>
      
      <!-- 右侧：教程内容 -->
      <el-col :span="18">
        <el-card class="tutorial-content">
          <!-- 快速入门 -->
          <div v-if="activeTutorial === 'quickstart'" class="tutorial">
            <h1>🚀 快速入门（5分钟上手）</h1>
            
            <el-alert type="success" :closable="false" show-icon>
              <template #title>
                <strong>欢迎使用KOOK消息转发系统！</strong>
              </template>
              本教程将帮助您在5分钟内完成基础配置并开始使用
            </el-alert>
            
            <h2>第1步：环境检测（1分钟）</h2>
            <ol>
              <li>首次启动会自动进行环境检测</li>
              <li>如果发现问题，点击"一键修复"自动解决</li>
              <li>所有检查通过后，点击"继续"</li>
            </ol>
            
            <el-image 
              src="/tutorials/env-check.png" 
              fit="contain"
              style="margin: 20px 0"
            />
            
            <h2>第2步：登录KOOK（1分钟）</h2>
            <ol>
              <li>选择"Chrome扩展"方式（推荐）</li>
              <li>安装Chrome扩展</li>
              <li>访问KOOK并登录</li>
              <li>点击扩展图标，一键导出Cookie</li>
              <li>Cookie会自动导入到系统中</li>
            </ol>
            
            <el-image 
              src="/tutorials/login.png" 
              fit="contain"
              style="margin: 20px 0"
            />
            
            <h2>第3步：配置Bot（2分钟）</h2>
            <ol>
              <li>选择要配置的平台（Discord/Telegram/飞书）</li>
              <li>填写Bot配置信息（Webhook URL、Token等）</li>
              <li>点击"测试连接"验证配置</li>
              <li>测试成功后，Bot自动保存</li>
            </ol>
            
            <el-image 
              src="/tutorials/bot-config.png" 
              fit="contain"
              style="margin: 20px 0"
            />
            
            <h2>第4步：智能映射（1分钟）</h2>
            <ol>
              <li>选择KOOK频道</li>
              <li>查看AI推荐的映射（按置信度排序）</li>
              <li>点击"一键应用高置信度推荐"</li>
              <li>完成配置！</li>
            </ol>
            
            <el-image 
              src="/tutorials/mapping.png" 
              fit="contain"
              style="margin: 20px 0"
            />
            
            <h2>第5步：启动服务</h2>
            <ol>
              <li>点击"完成配置"</li>
              <li>在主界面点击"启动服务"</li>
              <li>服务启动后，所有KOOK消息会自动转发</li>
              <li>在日志页面可以查看转发记录</li>
            </ol>
            
            <el-result
              icon="success"
              title="配置完成！"
              sub-title="现在您可以开始使用KOOK消息转发系统了"
            >
              <template #extra>
                <el-button type="primary" @click="startInteractiveTour">
                  🎯 开始交互式导览
                </el-button>
              </template>
            </el-result>
          </div>
          
          <!-- Cookie获取教程 -->
          <div v-else-if="activeTutorial === 'cookie'" class="tutorial">
            <h1>🍪 Cookie获取详细教程</h1>
            
            <h2>方法1：Chrome扩展（推荐）⭐</h2>
            <el-steps :active="3" finish-status="success" direction="vertical">
              <el-step title="安装扩展">
                <template #description>
                  <p>在配置向导中点击"安装Chrome扩展"</p>
                  <p>或手动加载chrome-extension目录</p>
                </template>
              </el-step>
              
              <el-step title="访问KOOK">
                <template #description>
                  <p>访问 <el-link href="https://www.kookapp.cn" target="_blank">https://www.kookapp.cn</el-link></p>
                  <p>使用您的账号登录</p>
                </template>
              </el-step>
              
              <el-step title="导出Cookie">
                <template #description>
                  <p>点击Chrome扩展图标</p>
                  <p>或按快捷键 <kbd>Ctrl+Shift+K</kbd></p>
                  <p>点击"一键导出Cookie"</p>
                  <p>Cookie已自动复制到剪贴板</p>
                </template>
              </el-step>
            </el-steps>
            
            <el-divider />
            
            <h2>方法2：浏览器开发者工具</h2>
            <el-tabs type="border-card">
              <el-tab-pane label="Chrome">
                <ol>
                  <li>访问KOOK并登录</li>
                  <li>按F12打开开发者工具</li>
                  <li>切换到"Application"标签</li>
                  <li>左侧选择"Cookies" > "https://www.kookapp.cn"</li>
                  <li>复制所有Cookie（右键 > Copy）</li>
                  <li>粘贴到配置向导的Cookie输入框</li>
                </ol>
              </el-tab-pane>
              
              <el-tab-pane label="Firefox">
                <ol>
                  <li>访问KOOK并登录</li>
                  <li>按F12打开开发者工具</li>
                  <li>切换到"存储"标签</li>
                  <li>左侧选择"Cookie" > "https://www.kookapp.cn"</li>
                  <li>复制所有Cookie</li>
                  <li>粘贴到配置向导的Cookie输入框</li>
                </ol>
              </el-tab-pane>
            </el-tabs>
            
            <el-divider />
            
            <h2>常见问题</h2>
            <el-collapse>
              <el-collapse-item title="Q: Cookie多久会过期？" name="expire">
                <p>KOOK的Cookie通常有效期为7-30天</p>
                <p>过期后需要重新获取</p>
                <p>系统会在Cookie即将过期时提醒您</p>
              </el-collapse-item>
              
              <el-collapse-item title="Q: Cookie安全吗？" name="security">
                <p>Cookie仅存储在您的本地设备</p>
                <p>使用AES-256加密存储</p>
                <p>不会上传到任何服务器</p>
              </el-collapse-item>
              
              <el-collapse-item title="Q: 可以在多台设备使用同一个Cookie吗？" name="multi-device">
                <p>不建议</p>
                <p>KOOK可能检测到异常登录</p>
                <p>建议每台设备使用独立的KOOK账号</p>
              </el-collapse-item>
            </el-collapse>
          </div>
          
          <!-- 其他教程内容... -->
          <div v-else-if="activeTutorial === 'faq'" class="tutorial">
            <h1>❓ 常见问题FAQ</h1>
            
            <el-collapse v-model="activeQuestions" accordion>
              <el-collapse-item title="Q: KOOK账号一直显示'离线'？" name="offline">
                <el-alert type="warning" :closable="false">
                  <strong>可能原因：</strong>
                </el-alert>
                <ol>
                  <li>
                    <strong>Cookie已过期</strong>
                    <p>→ 解决：重新登录或重新导出Cookie</p>
                  </li>
                  <li>
                    <strong>IP被限制</strong>
                    <p>→ 解决：更换网络或使用代理</p>
                  </li>
                  <li>
                    <strong>账号被封禁</strong>
                    <p>→ 解决：联系KOOK客服</p>
                  </li>
                </ol>
              </el-collapse-item>
              
              <el-collapse-item title="Q: 消息转发延迟很大（超过10秒）？" name="delay">
                <el-alert type="warning" :closable="false">
                  <strong>可能原因：</strong>
                </el-alert>
                <ol>
                  <li>
                    <strong>消息队列积压</strong>
                    <p>→ 解决：查看队列状态，等待消化或清空队列</p>
                  </li>
                  <li>
                    <strong>目标平台限流</strong>
                    <p>→ 解决：降低频道映射数量</p>
                  </li>
                  <li>
                    <strong>网络不稳定</strong>
                    <p>→ 解决：检查网络连接</p>
                  </li>
                </ol>
              </el-collapse-item>
              
              <el-collapse-item title="Q: 图片转发失败？" name="image">
                <el-alert type="warning" :closable="false">
                  <strong>可能原因：</strong>
                </el-alert>
                <ol>
                  <li>
                    <strong>图片被防盗链</strong>
                    <p>→ 解决：系统会自动处理，稍后重试</p>
                  </li>
                  <li>
                    <strong>图片过大</strong>
                    <p>→ 解决：程序会自动压缩</p>
                  </li>
                  <li>
                    <strong>目标平台限制</strong>
                    <p>→ 解决：使用图床模式（在设置中调整）</p>
                  </li>
                </ol>
              </el-collapse-item>
              
              <el-collapse-item title="Q: 如何卸载软件？" name="uninstall">
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="Windows">
                    控制面板 → 程序 → 卸载
                  </el-descriptions-item>
                  <el-descriptions-item label="macOS">
                    直接删除应用到废纸篓
                  </el-descriptions-item>
                  <el-descriptions-item label="Linux">
                    直接删除AppImage文件
                  </el-descriptions-item>
                </el-descriptions>
                
                <el-alert type="info" style="margin-top: 10px">
                  数据会保留在用户文档目录（Documents/KookForwarder），可手动删除
                </el-alert>
              </el-collapse-item>
              
              <el-collapse-item title="Q: 如何备份配置？" name="backup">
                <ol>
                  <li>进入"设置"页面</li>
                  <li>找到"备份与恢复"部分</li>
                  <li>点击"立即备份配置"</li>
                  <li>备份文件会保存到Documents/KookForwarder/backups/</li>
                </ol>
              </el-collapse-item>
              
              <el-collapse-item title="Q: 支持哪些平台？" name="platforms">
                <el-tag v-for="platform in supportedPlatforms" :key="platform" style="margin: 5px">
                  {{ platform }}
                </el-tag>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 底部：快捷入口 -->
    <el-card class="quick-links" style="margin-top: 20px">
      <template #header>
        <span>⚡ 快捷入口</span>
      </template>
      
      <el-row :gutter="10">
        <el-col :span="6">
          <el-button class="quick-link-btn" @click="startWizard">
            <el-icon><Guide /></el-icon>
            <span>重新运行配置向导</span>
          </el-button>
        </el-col>
        
        <el-col :span="6">
          <el-button class="quick-link-btn" @click="checkEnvironment">
            <el-icon><Setting /></el-icon>
            <span>环境检测</span>
          </el-button>
        </el-col>
        
        <el-col :span="6">
          <el-button class="quick-link-btn" @click="viewLogs">
            <el-icon><Document /></el-icon>
            <span>查看日志</span>
          </el-button>
        </el-col>
        
        <el-col :span="6">
          <el-button class="quick-link-btn" @click="contactSupport">
            <el-icon><Service /></el-icon>
            <span>联系支持</span>
          </el-button>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Promotion, Key, Connection, ChatDotRound, MessageBox,
  Share, Filter, QuestionFilled, VideoPlay, Guide,
  Setting, Document, Service, Folder
} from '@element-plus/icons-vue'

const router = useRouter()

const activeTutorial = ref('quickstart')
const activeQuestions = ref([])

const videoTutorials = ref([
  {
    id: 1,
    title: '完整配置演示（10分钟）',
    url: 'https://www.youtube.com/watch?v=xxx'
  },
  {
    id: 2,
    title: 'Cookie获取教程（3分钟）',
    url: 'https://www.youtube.com/watch?v=xxx'
  },
  {
    id: 3,
    title: 'Discord Webhook配置（2分钟）',
    url: 'https://www.youtube.com/watch?v=xxx'
  },
  {
    id: 4,
    title: 'Telegram Bot配置（4分钟）',
    url: 'https://www.youtube.com/watch?v=xxx'
  }
])

const supportedPlatforms = ['Discord', 'Telegram', '飞书', 'QQ', '企业微信（计划中）']

function selectTutorial(index) {
  activeTutorial.value = index
}

function goBack() {
  router.back()
}

function startWizard() {
  router.push('/wizard')
}

function checkEnvironment() {
  router.push('/environment-check')
}

function viewLogs() {
  router.push('/logs')
}

function contactSupport() {
  window.open('https://github.com/gfchfjh/CSBJJWT/issues', '_blank')
}

function startInteractiveTour() {
  // 启动交互式导览（使用driver.js）
  // TODO: 实现交互式导览
}
</script>

<style scoped>
.help-system {
  padding: 20px;
}

.tutorial-menu {
  position: sticky;
  top: 20px;
}

.video-link {
  display: block;
  margin: 10px 0;
  padding: 10px;
  border-radius: 4px;
  transition: background 0.3s;
}

.video-link:hover {
  background: #f5f7fa;
}

.tutorial-content {
  min-height: 600px;
}

.tutorial h1 {
  font-size: 28px;
  margin-bottom: 20px;
  color: #303133;
}

.tutorial h2 {
  font-size: 20px;
  margin: 30px 0 15px;
  color: #409EFF;
  border-left: 4px solid #409EFF;
  padding-left: 10px;
}

.tutorial ol {
  padding-left: 20px;
  line-height: 1.8;
}

.tutorial li {
  margin: 10px 0;
}

kbd {
  padding: 2px 6px;
  background: #303133;
  color: white;
  border-radius: 4px;
  font-size: 12px;
  font-family: monospace;
}

.quick-links {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.quick-link-btn {
  width: 100%;
  height: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.quick-link-btn .el-icon {
  font-size: 32px;
}
</style>
