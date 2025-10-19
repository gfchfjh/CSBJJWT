<template>
  <div class="help-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>❓ 帮助中心</span>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索问题..."
            style="width: 300px"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </template>

      <el-tabs v-model="activeTab" type="border-card">
        <!-- 快速入门 -->
        <el-tab-pane label="📘 快速入门" name="quickstart">
          <el-card shadow="never" class="tutorial-card">
            <template #header>
              <div class="tutorial-header">
                <h3>🚀 5分钟快速开始</h3>
                <el-tag type="success">推荐新手</el-tag>
              </div>
            </template>

            <el-steps :active="currentStep" finish-status="success" align-center>
              <el-step title="添加KOOK账号" description="获取并导入Cookie" />
              <el-step title="配置机器人" description="设置目标平台Bot" />
              <el-step title="设置映射" description="选择要转发的频道" />
              <el-step title="启动服务" description="开始自动转发" />
            </el-steps>

            <el-divider />

            <div class="quick-actions">
              <el-button type="primary" size="large" @click="goToWizard">
                <el-icon><MagicStick /></el-icon>
                启动配置向导
              </el-button>
              <el-button size="large" @click="watchVideo('quickstart')">
                <el-icon><VideoPlay /></el-icon>
                观看视频教程（10分钟）
              </el-button>
            </div>
          </el-card>
        </el-tab-pane>

        <!-- 图文教程 -->
        <el-tab-pane label="📖 图文教程" name="tutorials">
          <el-row :gutter="20">
            <el-col :span="8" v-for="tutorial in filteredTutorials" :key="tutorial.id">
              <el-card shadow="hover" class="tutorial-item" @click="openTutorial(tutorial)">
                <div class="tutorial-icon">{{ tutorial.icon }}</div>
                <h4>{{ tutorial.title }}</h4>
                <p class="tutorial-desc">{{ tutorial.description }}</p>
                <el-divider />
                <div class="tutorial-meta">
                  <el-tag size="small" :type="tutorial.difficulty === 'easy' ? 'success' : 'warning'">
                    {{ tutorial.difficulty === 'easy' ? '简单' : '中等' }}
                  </el-tag>
                  <span class="tutorial-time">⏱️ {{ tutorial.duration }}</span>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- 视频教程 -->
        <el-tab-pane label="📺 视频教程" name="videos">
          <el-alert
            title="视频教程准备中"
            type="info"
            :closable="false"
            style="margin-bottom: 20px"
          >
            我们正在录制详细的视频教程，包括：
            <ul style="margin: 10px 0; padding-left: 20px;">
              <li>✅ 完整配置演示（10分钟）</li>
              <li>✅ Cookie获取教程（3分钟）</li>
              <li>✅ Discord配置教程（2分钟）</li>
              <li>✅ Telegram配置教程（4分钟）</li>
              <li>✅ 飞书配置教程（5分钟）</li>
            </ul>
            <p style="margin-top: 10px;">
              <strong>敬请期待！</strong> 在此期间，您可以查看图文教程。
            </p>
          </el-alert>

          <el-row :gutter="20">
            <el-col :span="12" v-for="video in videoList" :key="video.id">
              <el-card shadow="hover" class="video-card">
                <div class="video-thumbnail" :class="{ 'coming-soon': video.comingSoon }">
                  <el-icon size="60" color="#409EFF" v-if="video.comingSoon">
                    <VideoCamera />
                  </el-icon>
                  <span v-if="video.comingSoon" class="coming-soon-tag">即将推出</span>
                </div>
                <h4>{{ video.title }}</h4>
                <p class="video-desc">{{ video.description }}</p>
                <div class="video-footer">
                  <el-tag size="small">{{ video.duration }}</el-tag>
                  <el-button 
                    v-if="!video.comingSoon" 
                    size="small" 
                    type="primary" 
                    @click="watchVideo(video.id)"
                  >
                    观看
                  </el-button>
                  <el-tag v-else size="small" type="info">筹备中</el-tag>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- 常见问题FAQ -->
        <el-tab-pane label="💡 常见问题" name="faq">
          <el-collapse v-model="activeFaq" accordion>
            <el-collapse-item 
              v-for="faq in filteredFaqs" 
              :key="faq.id" 
              :name="faq.id"
            >
              <template #title>
                <div class="faq-title">
                  <el-icon :color="faq.priority === 'high' ? '#F56C6C' : '#409EFF'">
                    <QuestionFilled />
                  </el-icon>
                  <span>{{ faq.question }}</span>
                  <el-tag 
                    v-if="faq.priority === 'high'" 
                    type="danger" 
                    size="small" 
                    style="margin-left: 10px"
                  >
                    常见
                  </el-tag>
                </div>
              </template>
              <div class="faq-answer" v-html="faq.answer"></div>
            </el-collapse-item>
          </el-collapse>
        </el-tab-pane>

        <!-- 联系支持 -->
        <el-tab-pane label="📧 联系支持" name="contact">
          <el-card shadow="never">
            <template #header>
              <h3>需要更多帮助？</h3>
            </template>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-card shadow="hover" class="contact-card">
                  <div class="contact-icon">
                    <el-icon size="40" color="#409EFF"><Document /></el-icon>
                  </div>
                  <h4>查看完整文档</h4>
                  <p>包含详细的功能说明、配置指南和故障排查</p>
                  <el-button type="primary" @click="openDocs">
                    打开文档
                  </el-button>
                </el-card>
              </el-col>

              <el-col :span="12">
                <el-card shadow="hover" class="contact-card">
                  <div class="contact-icon">
                    <el-icon size="40" color="#67C23A"><MessageBox /></el-icon>
                  </div>
                  <h4>提交问题反馈</h4>
                  <p>在GitHub上提交Issue，我们会尽快回复</p>
                  <el-button type="success" @click="openGithubIssues">
                    GitHub Issues
                  </el-button>
                </el-card>
              </el-col>
            </el-row>

            <el-divider />

            <div class="system-info">
              <h4>系统信息（用于反馈时提供）</h4>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="应用版本">v{{ appVersion }}</el-descriptions-item>
                <el-descriptions-item label="操作系统">{{ systemOS }}</el-descriptions-item>
                <el-descriptions-item label="运行时长">{{ uptime }}</el-descriptions-item>
                <el-descriptions-item label="活跃账号">{{ activeAccounts }}</el-descriptions-item>
              </el-descriptions>
              <el-button 
                type="primary" 
                size="small" 
                @click="copySystemInfo"
                style="margin-top: 10px"
              >
                <el-icon><CopyDocument /></el-icon>
                复制系统信息
              </el-button>
            </div>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 教程详情对话框 -->
    <el-dialog
      v-model="showTutorialDialog"
      :title="currentTutorial?.title"
      width="900px"
      destroy-on-close
    >
      <div v-if="currentTutorial" class="tutorial-content">
        <el-alert
          :title="`难度：${currentTutorial.difficulty === 'easy' ? '简单' : '中等'} | 预计耗时：${currentTutorial.duration}`"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        />

        <div class="markdown-body" v-html="currentTutorial.content"></div>
      </div>

      <template #footer>
        <el-button @click="showTutorialDialog = false">关闭</el-button>
        <el-button type="primary" @click="openTutorialExternal">
          在新窗口打开
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()

// 当前激活的标签
const activeTab = ref('quickstart')
const activeFaq = ref('')
const searchKeyword = ref('')
const currentStep = ref(0)

// 对话框
const showTutorialDialog = ref(false)
const currentTutorial = ref(null)

// 系统信息
const appVersion = ref('1.7.0')
const systemOS = ref('Loading...')
const uptime = ref('--')
const activeAccounts = ref(0)

// 教程列表
const tutorials = ref([
  {
    id: 'cookie-guide',
    icon: '🍪',
    title: 'Cookie获取详细教程',
    description: '三种方法获取KOOK Cookie，包括浏览器扩展、开发者工具等',
    difficulty: 'easy',
    duration: '3-5分钟',
    file: 'Cookie获取详细教程.md'
  },
  {
    id: 'discord-config',
    icon: '💬',
    title: 'Discord配置教程',
    description: '如何创建Discord Webhook并配置到系统',
    difficulty: 'easy',
    duration: '2-3分钟',
    file: 'Discord配置教程.md'
  },
  {
    id: 'telegram-config',
    icon: '✈️',
    title: 'Telegram配置教程',
    description: '创建Telegram Bot并获取Chat ID的完整指南',
    difficulty: 'easy',
    duration: '4-5分钟',
    file: 'Telegram配置教程.md'
  },
  {
    id: 'feishu-config',
    icon: '🚀',
    title: '飞书配置教程',
    description: '在飞书开放平台创建自建应用的详细步骤',
    difficulty: 'medium',
    duration: '5-8分钟',
    file: '飞书配置教程.md'
  },
  {
    id: 'user-manual',
    icon: '📚',
    title: '完整用户手册',
    description: '从安装到高级功能的完整使用指南',
    difficulty: 'easy',
    duration: '15-20分钟',
    file: '完整用户手册.md'
  },
  {
    id: 'dev-guide',
    icon: '💻',
    title: '开发指南',
    description: '面向开发者的技术文档和API说明',
    difficulty: 'medium',
    duration: '30分钟',
    file: '开发指南.md'
  }
])

// 视频教程列表
const videoList = ref([
  {
    id: 'quickstart',
    title: '完整配置演示',
    description: '从零开始，完整演示如何配置和使用KOOK消息转发系统',
    duration: '10分钟',
    comingSoon: true
  },
  {
    id: 'cookie',
    title: 'Cookie获取教程',
    description: '演示如何使用浏览器开发者工具和扩展获取Cookie',
    duration: '3分钟',
    comingSoon: true
  },
  {
    id: 'discord',
    title: 'Discord配置教程',
    description: 'Discord Webhook的创建和配置全流程',
    duration: '2分钟',
    comingSoon: true
  },
  {
    id: 'telegram',
    title: 'Telegram配置教程',
    description: '如何创建Telegram Bot并获取必要的配置信息',
    duration: '4分钟',
    comingSoon: true
  },
  {
    id: 'feishu',
    title: '飞书配置教程',
    description: '在飞书开放平台创建应用并配置到系统',
    duration: '5分钟',
    comingSoon: true
  },
  {
    id: 'troubleshooting',
    title: '故障排查指南',
    description: '常见问题的诊断和解决方法演示',
    duration: '8分钟',
    comingSoon: true
  }
])

// FAQ列表
const faqs = ref([
  {
    id: 'faq1',
    question: 'KOOK账号一直显示"离线"？',
    priority: 'high',
    answer: `
      <p><strong>可能原因及解决方法：</strong></p>
      <ol>
        <li><strong>Cookie已过期</strong> → 重新登录KOOK网页版获取新Cookie</li>
        <li><strong>IP被限制</strong> → 更换网络或使用代理</li>
        <li><strong>账号被封禁</strong> → 联系KOOK客服确认账号状态</li>
        <li><strong>浏览器进程异常</strong> → 在系统设置中重启服务</li>
      </ol>
      <p><strong>快速检查：</strong></p>
      <p>1. 访问 <a href="https://www.kookapp.cn/" target="_blank">KOOK网页版</a> 确认能正常登录</p>
      <p>2. 在账号管理页面点击"重新登录"</p>
      <p>3. 查看日志页面的详细错误信息</p>
    `
  },
  {
    id: 'faq2',
    question: '消息转发延迟很大（超过10秒）？',
    priority: 'high',
    answer: `
      <p><strong>可能原因及解决方法：</strong></p>
      <ol>
        <li><strong>消息队列积压</strong> → 查看日志页面的队列状态，等待消化完毕</li>
        <li><strong>目标平台限流</strong> → 降低频道映射数量，或调整转发频率</li>
        <li><strong>网络不稳定</strong> → 检查网络连接，考虑使用代理</li>
        <li><strong>Redis性能问题</strong> → 重启Redis服务（系统设置中）</li>
      </ol>
      <p><strong>优化建议：</strong></p>
      <ul>
        <li>避免同时监听过多频道</li>
        <li>使用"智能模式"的图片处理策略</li>
        <li>定期清理日志和图片缓存</li>
      </ul>
    `
  },
  {
    id: 'faq3',
    question: '图片转发失败？',
    priority: 'high',
    answer: `
      <p><strong>可能原因及解决方法：</strong></p>
      <ol>
        <li><strong>图片被防盗链</strong> → 已自动处理Cookie和Referer，重试即可</li>
        <li><strong>图片过大</strong> → 程序会自动压缩，检查"图片处理"设置中的压缩质量</li>
        <li><strong>目标平台限制</strong> → 切换到"图床模式"</li>
        <li><strong>网络超时</strong> → 检查网络连接，增加超时时间（开发者设置）</li>
      </ol>
      <p><strong>图片处理策略对比：</strong></p>
      <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr>
          <th>策略</th>
          <th>优点</th>
          <th>缺点</th>
        </tr>
        <tr>
          <td>智能模式</td>
          <td>自动选择最优方式</td>
          <td>-</td>
        </tr>
        <tr>
          <td>直传模式</td>
          <td>速度快</td>
          <td>失败率稍高</td>
        </tr>
        <tr>
          <td>图床模式</td>
          <td>稳定性高</td>
          <td>占用本地空间</td>
        </tr>
      </table>
    `
  },
  {
    id: 'faq4',
    question: 'Redis连接失败？',
    priority: 'medium',
    answer: `
      <p><strong>解决步骤：</strong></p>
      <ol>
        <li><strong>检查Redis服务</strong> → 确认Redis进程是否在运行</li>
        <li><strong>重启Redis</strong> → 在系统设置中点击"重启服务"</li>
        <li><strong>检查端口占用</strong> → 确认6379端口未被其他程序占用</li>
        <li><strong>查看日志</strong> → 检查Redis日志文件（用户文档/KookForwarder/data/redis/）</li>
      </ol>
      <p><strong>Windows用户注意：</strong></p>
      <p>如果Redis无法启动，可能是被杀毒软件拦截，请将程序添加到白名单。</p>
    `
  },
  {
    id: 'faq5',
    question: '如何卸载软件？',
    priority: 'low',
    answer: `
      <p><strong>卸载步骤：</strong></p>
      <p><strong>Windows：</strong></p>
      <ol>
        <li>控制面板 → 程序和功能</li>
        <li>找到"KOOK消息转发系统"</li>
        <li>点击"卸载"</li>
      </ol>
      <p><strong>macOS：</strong></p>
      <ol>
        <li>打开"应用程序"文件夹</li>
        <li>将"KOOK消息转发系统"拖到废纸篓</li>
      </ol>
      <p><strong>Linux：</strong></p>
      <ol>
        <li>删除AppImage文件</li>
      </ol>
      <p><strong>数据清理：</strong></p>
      <p>用户数据保存在：<code>用户文档/KookForwarder/</code></p>
      <p>如需彻底删除数据，请手动删除此文件夹。</p>
    `
  },
  {
    id: 'faq6',
    question: '使用Cookie会被KOOK封号吗？',
    priority: 'medium',
    answer: `
      <p><strong>安全性说明：</strong></p>
      <p>✅ <strong>正常使用不会被封号</strong></p>
      <ul>
        <li>Cookie登录与浏览器登录效果完全相同</li>
        <li>KOOK无法区分Cookie登录和正常登录</li>
        <li>只要不频繁异常操作，就是安全的</li>
      </ul>
      <p><strong>注意事项：</strong></p>
      <ol>
        <li>不要在短时间内频繁切换IP</li>
        <li>不要同时登录过多账号（建议≤5个）</li>
        <li>遵守KOOK使用条款和社区规范</li>
        <li>不要使用本工具进行恶意行为（刷屏、骚扰等）</li>
      </ol>
      <p><strong>免责声明：</strong></p>
      <p>本软件仅供学习交流使用，使用者应自行承担使用风险。</p>
    `
  },
  {
    id: 'faq7',
    question: '为什么推荐Cookie登录而不是账号密码？',
    priority: 'low',
    answer: `
      <p><strong>优势对比：</strong></p>
      <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr>
          <th>方式</th>
          <th>优点</th>
          <th>缺点</th>
        </tr>
        <tr>
          <td><strong>Cookie</strong></td>
          <td>
            • 无需验证码<br>
            • 更稳定<br>
            • 不易触发安全检测<br>
            • 可以随时撤销
          </td>
          <td>
            • 需要手动获取<br>
            • 定期更新（通常30天）
          </td>
        </tr>
        <tr>
          <td><strong>账号密码</strong></td>
          <td>
            • 操作简单<br>
            • 自动登录
          </td>
          <td>
            • 可能遇到验证码<br>
            • 易触发风控<br>
            • 需要保存密码（安全风险）
          </td>
        </tr>
      </table>
      <p><strong>建议：</strong></p>
      <p>新手可以先使用账号密码快速体验，熟悉后切换到Cookie方式以获得更好的稳定性。</p>
    `
  },
  {
    id: 'faq8',
    question: '如何更新到最新版本？',
    priority: 'medium',
    answer: `
      <p><strong>自动更新（推荐）：</strong></p>
      <ol>
        <li>进入"系统设置" → "其他设置"</li>
        <li>设置"自动更新"为"自动检查并安装"</li>
        <li>系统会在后台检查更新，发现新版本时自动提示</li>
      </ol>
      <p><strong>手动更新：</strong></p>
      <ol>
        <li>访问 <a href="https://github.com/gfchfjh/CSBJJWT/releases" target="_blank">GitHub Releases</a></li>
        <li>下载最新版本的安装包</li>
        <li>运行安装包，覆盖原有版本</li>
        <li>配置和数据会自动保留</li>
      </ol>
      <p><strong>注意：</strong></p>
      <p>更新前建议先备份配置（系统设置 → 备份配置）</p>
    `
  }
])

// 筛选后的教程
const filteredTutorials = computed(() => {
  if (!searchKeyword.value) return tutorials.value
  
  const keyword = searchKeyword.value.toLowerCase()
  return tutorials.value.filter(t => 
    t.title.toLowerCase().includes(keyword) ||
    t.description.toLowerCase().includes(keyword)
  )
})

// 筛选后的FAQ
const filteredFaqs = computed(() => {
  if (!searchKeyword.value) return faqs.value
  
  const keyword = searchKeyword.value.toLowerCase()
  return faqs.value.filter(f => 
    f.question.toLowerCase().includes(keyword) ||
    f.answer.toLowerCase().includes(keyword)
  )
})

// 去配置向导
const goToWizard = () => {
  router.push('/wizard')
}

// 观看视频
const watchVideo = (videoId) => {
  ElMessage.info('视频教程正在录制中，敬请期待！')
}

// 打开教程
const openTutorial = async (tutorial) => {
  try {
    // 尝试加载教程内容
    const response = await fetch(`/docs/${tutorial.file}`)
    if (response.ok) {
      const content = await response.text()
      currentTutorial.value = {
        ...tutorial,
        content: content // 这里应该用markdown渲染器处理
      }
      showTutorialDialog.value = true
    } else {
      // 如果文件不存在，提供外部链接
      ElMessageBox.confirm(
        `教程文档位于项目的 docs 目录中。<br/><br/>` +
        `<strong>文件路径：</strong><code>docs/${tutorial.file}</code><br/><br/>` +
        `是否在文件管理器中打开文档文件夹？`,
        '教程文档',
        {
          confirmButtonText: '打开文件夹',
          cancelButtonText: '取消',
          type: 'info',
          dangerouslyUseHTMLString: true
        }
      ).then(() => {
        openDocsFolder()
      })
    }
  } catch (error) {
    console.error('加载教程失败:', error)
    ElMessage.error('加载教程失败')
  }
}

// 在新窗口打开教程
const openTutorialExternal = () => {
  if (currentTutorial.value) {
    const url = `https://github.com/gfchfjh/CSBJJWT/blob/main/docs/${currentTutorial.value.file}`
    window.open(url, '_blank')
  }
}

// 打开文档
const openDocs = () => {
  window.open('https://github.com/gfchfjh/CSBJJWT/tree/main/docs', '_blank')
}

// 打开文档文件夹
const openDocsFolder = async () => {
  try {
    if (window.electronAPI && window.electronAPI.openPath) {
      await window.electronAPI.openPath('./docs')
    } else {
      ElMessage.info('请在项目目录的 docs 文件夹中查看教程文档')
    }
  } catch (error) {
    ElMessage.error('打开文件夹失败')
  }
}

// 打开GitHub Issues
const openGithubIssues = () => {
  window.open('https://github.com/gfchfjh/CSBJJWT/issues', '_blank')
}

// 复制系统信息
const copySystemInfo = async () => {
  const info = `
KOOK消息转发系统 - 系统信息

应用版本: v${appVersion.value}
操作系统: ${systemOS.value}
运行时长: ${uptime.value}
活跃账号: ${activeAccounts.value}

---
生成时间: ${new Date().toLocaleString('zh-CN')}
`.trim()

  try {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(info)
      ElMessage.success('系统信息已复制到剪贴板')
    } else {
      // Fallback
      const textarea = document.createElement('textarea')
      textarea.value = info
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
      ElMessage.success('系统信息已复制到剪贴板')
    }
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 加载系统信息
const loadSystemInfo = async () => {
  try {
    // 获取系统信息
    const sysInfo = await api.getSystemInfo()
    if (sysInfo) {
      systemOS.value = sysInfo.os || 'Unknown'
      uptime.value = sysInfo.uptime || '--'
    }
    
    // 获取账号数量
    const accounts = await api.getAccounts()
    activeAccounts.value = accounts?.filter(a => a.status === 'online').length || 0
  } catch (error) {
    console.error('加载系统信息失败:', error)
  }
}

onMounted(() => {
  loadSystemInfo()
})
</script>

<style scoped>
.help-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tutorial-card {
  margin-bottom: 20px;
}

.tutorial-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tutorial-header h3 {
  margin: 0;
}

.quick-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin: 30px 0;
}

.tutorial-item {
  cursor: pointer;
  margin-bottom: 20px;
  transition: transform 0.2s;
}

.tutorial-item:hover {
  transform: translateY(-5px);
}

.tutorial-icon {
  font-size: 48px;
  text-align: center;
  margin: 20px 0;
}

.tutorial-item h4 {
  margin: 10px 0;
  text-align: center;
}

.tutorial-desc {
  color: #606266;
  font-size: 14px;
  text-align: center;
  min-height: 40px;
}

.tutorial-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tutorial-time {
  color: #909399;
  font-size: 12px;
}

.video-card {
  margin-bottom: 20px;
}

.video-thumbnail {
  height: 180px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 15px;
  border-radius: 4px;
  position: relative;
}

.video-thumbnail.coming-soon {
  background: #909399;
}

.coming-soon-tag {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 12px;
}

.video-card h4 {
  margin: 10px 0;
}

.video-desc {
  color: #606266;
  font-size: 14px;
  min-height: 40px;
  margin-bottom: 15px;
}

.video-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.faq-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
}

.faq-answer {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
  line-height: 1.8;
}

.faq-answer :deep(ol),
.faq-answer :deep(ul) {
  margin: 10px 0;
  padding-left: 25px;
}

.faq-answer :deep(table) {
  margin: 15px 0;
}

.faq-answer :deep(th),
.faq-answer :deep(td) {
  padding: 8px 12px;
}

.faq-answer :deep(code) {
  background: #e6effb;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

.faq-answer :deep(a) {
  color: #409EFF;
  text-decoration: none;
}

.faq-answer :deep(a:hover) {
  text-decoration: underline;
}

.contact-card {
  text-align: center;
  padding: 20px;
}

.contact-icon {
  margin: 20px 0;
}

.contact-card h4 {
  margin: 15px 0;
}

.contact-card p {
  color: #606266;
  margin-bottom: 20px;
  min-height: 40px;
}

.system-info {
  margin-top: 30px;
}

.system-info h4 {
  margin-bottom: 15px;
}

.tutorial-content {
  max-height: 600px;
  overflow-y: auto;
}

.markdown-body {
  padding: 20px;
  line-height: 1.8;
}

:deep(.el-tabs__content) {
  padding: 20px;
}
</style>
