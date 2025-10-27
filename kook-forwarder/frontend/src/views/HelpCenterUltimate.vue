<template>
  <div class="help-center-ultimate">
    <el-container>
      <!-- 侧边栏：教程目录 -->
      <el-aside width="280px">
        <el-card shadow="never" class="sidebar-card">
          <template #header>
            <span><el-icon><Reading /></el-icon> 教程目录</span>
          </template>
          
          <el-menu
            :default-active="activeSection"
            @select="handleSectionChange"
          >
            <el-menu-item index="quick-start">
              <el-icon><VideoPlay /></el-icon>
              <span>快速入门（5分钟）</span>
            </el-menu-item>
            
            <el-menu-item index="cookie">
              <el-icon><Key /></el-icon>
              <span>如何获取Cookie</span>
            </el-menu-item>
            
            <el-menu-item index="discord">
              <el-icon><Message /></el-icon>
              <span>Discord Webhook配置</span>
            </el-menu-item>
            
            <el-menu-item index="telegram">
              <el-icon><ChatLineSquare /></el-icon>
              <span>Telegram Bot配置</span>
            </el-menu-item>
            
            <el-menu-item index="feishu">
              <el-icon><ChatRound /></el-icon>
              <span>飞书应用配置</span>
            </el-menu-item>
            
            <el-menu-item index="mapping">
              <el-icon><Share /></el-icon>
              <span>频道映射配置</span>
            </el-menu-item>
            
            <el-menu-item index="filter">
              <el-icon><Filter /></el-icon>
              <span>过滤规则使用</span>
            </el-menu-item>
            
            <el-menu-item index="troubleshoot">
              <el-icon><Tools /></el-icon>
              <span>常见问题排查</span>
            </el-menu-item>
            
            <el-divider />
            
            <el-menu-item index="faq">
              <el-icon><QuestionFilled /></el-icon>
              <span>常见问题FAQ</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-main>
        <el-card shadow="never" class="content-card">
          <!-- 视频教程 -->
          <div v-if="currentTutorial.video" class="video-section">
            <h2>
              <el-icon><VideoCamera /></el-icon>
              {{ currentTutorial.title }}
            </h2>
            
            <!-- HTML5视频播放器 -->
            <div class="video-player-wrapper">
              <video
                ref="videoRef"
                class="video-player"
                controls
                :poster="currentTutorial.poster"
              >
                <source :src="currentTutorial.video" type="video/mp4" />
                您的浏览器不支持视频播放
              </video>
              
              <!-- 播放控制栏 -->
              <div class="video-controls">
                <el-button-group>
                  <el-button :icon="videoPlaying ? VideoPause : VideoPlay" @click="togglePlay">
                    {{ videoPlaying ? '暂停' : '播放' }}
                  </el-button>
                  <el-button :icon="RefreshLeft" @click="restartVideo">
                    重新播放
                  </el-button>
                </el-button-group>
                
                <!-- 速度调节 -->
                <el-select v-model="playbackSpeed" @change="changeSpeed" style="width: 100px">
                  <el-option label="0.5x" :value="0.5" />
                  <el-option label="0.75x" :value="0.75" />
                  <el-option label="1.0x" :value="1.0" />
                  <el-option label="1.25x" :value="1.25" />
                  <el-option label="1.5x" :value="1.5" />
                  <el-option label="2.0x" :value="2.0" />
                </el-select>
                
                <!-- 全屏 -->
                <el-button :icon="FullScreen" @click="toggleFullscreen">
                  全屏
                </el-button>
              </div>
              
              <!-- 章节导航 -->
              <div v-if="currentTutorial.chapters" class="chapters">
                <h4>📑 章节导航</h4>
                <div class="chapter-list">
                  <div
                    v-for="(chapter, index) in currentTutorial.chapters"
                    :key="index"
                    class="chapter-item"
                    @click="jumpToChapter(chapter.time)"
                  >
                    <span class="chapter-time">{{ formatTime(chapter.time) }}</span>
                    <span class="chapter-title">{{ chapter.title }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 图文教程 -->
          <div class="text-content" v-html="currentTutorial.content"></div>
          
          <!-- 相关推荐 -->
          <div v-if="relatedTutorials.length > 0" class="related-section">
            <h3><el-icon><Guide /></el-icon> 相关推荐</h3>
            <el-row :gutter="20">
              <el-col
                v-for="tutorial in relatedTutorials"
                :key="tutorial.id"
                :span="8"
              >
                <el-card
                  shadow="hover"
                  class="related-card"
                  @click="goToTutorial(tutorial.id)"
                >
                  <div class="related-content">
                    <el-icon :size="40"><Reading /></el-icon>
                    <h4>{{ tutorial.title }}</h4>
                    <p>{{ tutorial.description }}</p>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Reading,
  VideoPlay,
  VideoPause,
  VideoCamera,
  Key,
  Message,
  ChatLineSquare,
  ChatRound,
  Share,
  Filter,
  Tools,
  QuestionFilled,
  RefreshLeft,
  FullScreen,
  Guide
} from '@element-plus/icons-vue'

const activeSection = ref('quick-start')
const videoRef = ref(null)
const videoPlaying = ref(false)
const playbackSpeed = ref(1.0)

// 教程数据
const tutorials = ref({
  'quick-start': {
    id: 'quick-start',
    title: '快速入门指南（5分钟上手）',
    video: '/videos/tutorials/01-quick-start.mp4',
    poster: '/images/tutorials/quick-start-poster.jpg',
    chapters: [
      { time: 0, title: '介绍' },
      { time: 60, title: '安装步骤' },
      { time: 180, title: '基础配置' },
      { time: 240, title: '启动服务' }
    ],
    content: `
      <h2>📖 快速入门指南</h2>
      <p><strong>预计阅读时间:</strong> 5分钟</p>
      
      <h3>1. 下载安装</h3>
      <ol>
        <li>访问 <a href="https://github.com/gfchfjh/CSBJJWT/releases">GitHub Releases</a></li>
        <li>下载对应平台的安装包</li>
        <li>双击安装，完全自动化</li>
      </ol>
      
      <h3>2. 首次配置（3步）</h3>
      <ol>
        <li><strong>欢迎页</strong>：阅读免责声明并同意</li>
        <li><strong>KOOK登录</strong>：导入Cookie或使用账号密码</li>
        <li><strong>选择服务器</strong>：选择要监听的服务器和频道</li>
      </ol>
      
      <h3>3. 配置Bot</h3>
      <p>参考其他教程配置Discord/Telegram/飞书Bot</p>
      
      <h3>4. 启动服务</h3>
      <p>点击"启动服务"按钮，开始自动转发消息</p>
    `
  },
  'cookie': {
    id: 'cookie',
    title: 'Cookie获取详细教程',
    video: '/videos/tutorials/02-cookie-tutorial.mp4',
    content: `
      <h2>🍪 Cookie获取教程</h2>
      
      <h3>方法1: Chrome扩展导出（推荐）</h3>
      <ol>
        <li>安装 <strong>EditThisCookie</strong> 扩展</li>
        <li>访问 <a href="https://www.kookapp.cn">KOOK网站</a> 并登录</li>
        <li>点击扩展图标 → 导出 → 复制JSON</li>
        <li>在软件中粘贴即可</li>
      </ol>
      
      <h3>方法2: 开发者工具（通用）</h3>
      <ol>
        <li>访问KOOK网站并登录</li>
        <li>按 <kbd>F12</kbd> 打开开发者工具</li>
        <li>切换到 <strong>Application</strong> 标签</li>
        <li>左侧选择 <strong>Cookies</strong> → <strong>https://www.kookapp.cn</strong></li>
        <li>复制所有Cookie（支持直接粘贴到软件）</li>
      </ol>
      
      <h3>方法3: 使用本软件的Chrome扩展</h3>
      <ol>
        <li>安装本软件附带的Chrome扩展（chrome-extension文件夹）</li>
        <li>访问KOOK网站</li>
        <li>点击扩展图标 → 一键导出</li>
      </ol>
    `
  },
  'faq': {
    id: 'faq',
    title: '常见问题FAQ',
    content: `
      <h2>❓ 常见问题FAQ</h2>
      
      <h3>Q1: KOOK账号一直显示"离线"？</h3>
      <p><strong>可能原因：</strong></p>
      <ul>
        <li>Cookie已过期 → <strong>解决：</strong>重新登录</li>
        <li>IP被限制 → <strong>解决：</strong>更换网络或使用代理</li>
        <li>账号被封禁 → <strong>解决：</strong>联系KOOK客服</li>
      </ul>
      
      <h3>Q2: 消息转发延迟很大（超过10秒）？</h3>
      <p><strong>可能原因：</strong></p>
      <ul>
        <li>消息队列积压 → <strong>解决：</strong>查看队列状态，等待消化</li>
        <li>目标平台限流 → <strong>解决：</strong>降低频道映射数量</li>
        <li>网络不稳定 → <strong>解决：</strong>检查网络连接</li>
      </ul>
      
      <h3>Q3: 图片转发失败？</h3>
      <p><strong>可能原因：</strong></p>
      <ul>
        <li>图片被防盗链 → <strong>解决：</strong>已自动处理，重试即可</li>
        <li>图片过大 → <strong>解决：</strong>程序会自动压缩</li>
        <li>目标平台限制 → <strong>解决：</strong>使用图床模式</li>
      </ul>
      
      <h3>Q4: 如何卸载软件？</h3>
      <ul>
        <li><strong>Windows:</strong> 控制面板 → 程序 → 卸载</li>
        <li><strong>macOS:</strong> 直接删除应用</li>
        <li><strong>数据清理:</strong> 手动删除 "用户文档/KookForwarder" 文件夹</li>
      </ul>
      
      <h3>Q5: 验证码识别失败？</h3>
      <p><strong>解决方案：</strong></p>
      <ul>
        <li>点击"看不清？刷新"按钮获取新验证码</li>
        <li>确保在120秒内输入完成</li>
        <li>如果多次失败，可能需要更换网络环境</li>
      </ul>
    `
  }
})

const currentTutorial = computed(() => {
  return tutorials.value[activeSection.value] || {}
})

const relatedTutorials = computed(() => {
  // 根据当前教程推荐相关教程
  const related = {
    'quick-start': ['cookie', 'discord', 'telegram'],
    'cookie': ['quick-start', 'troubleshoot'],
    'discord': ['telegram', 'feishu', 'mapping'],
    'telegram': ['discord', 'feishu', 'mapping'],
    'feishu': ['discord', 'telegram', 'mapping'],
    'mapping': ['filter', 'quick-start'],
    'filter': ['mapping', 'troubleshoot']
  }
  
  const relatedIds = related[activeSection.value] || []
  return relatedIds.map(id => ({
    id,
    title: tutorials.value[id]?.title || '',
    description: tutorials.value[id]?.description || ''
  }))
})

const handleSectionChange = (section) => {
  activeSection.value = section
  // 重置视频状态
  videoPlaying.value = false
}

const togglePlay = () => {
  if (videoRef.value) {
    if (videoPlaying.value) {
      videoRef.value.pause()
    } else {
      videoRef.value.play()
    }
    videoPlaying.value = !videoPlaying.value
  }
}

const restartVideo = () => {
  if (videoRef.value) {
    videoRef.value.currentTime = 0
    videoRef.value.play()
    videoPlaying.value = true
  }
}

const changeSpeed = () => {
  if (videoRef.value) {
    videoRef.value.playbackRate = playbackSpeed.value
  }
}

const toggleFullscreen = () => {
  if (videoRef.value) {
    if (videoRef.value.requestFullscreen) {
      videoRef.value.requestFullscreen()
    }
  }
}

const jumpToChapter = (time) => {
  if (videoRef.value) {
    videoRef.value.currentTime = time
    videoRef.value.play()
    videoPlaying.value = true
  }
}

const goToTutorial = (tutorialId) => {
  activeSection.value = tutorialId
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

onMounted(() => {
  // 记录观看历史
  if (videoRef.value) {
    videoRef.value.addEventListener('play', () => {
      videoPlaying.value = true
    })
    
    videoRef.value.addEventListener('pause', () => {
      videoPlaying.value = false
    })
  }
})
</script>

<style scoped>
.help-center-ultimate {
  height: 100%;
  padding: 20px;
}

.el-container {
  height: 100%;
}

.sidebar-card {
  height: 100%;
}

.content-card {
  height: 100%;
  overflow-y: auto;
}

.video-section {
  margin-bottom: 30px;
}

.video-section h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.video-player-wrapper {
  background: #000;
  border-radius: 12px;
  overflow: hidden;
}

.video-player {
  width: 100%;
  max-height: 500px;
}

.video-controls {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #1a1a1a;
}

.chapters {
  padding: 20px;
  background: #2c2c2c;
}

.chapters h4 {
  color: white;
  margin: 0 0 15px;
}

.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chapter-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 15px;
  background: #3a3a3a;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  color: white;
}

.chapter-item:hover {
  background: #4a4a4a;
  transform: translateX(5px);
}

.chapter-time {
  font-family: monospace;
  color: #409EFF;
  font-weight: bold;
}

.chapter-title {
  flex: 1;
}

.text-content {
  line-height: 1.8;
  font-size: 15px;
}

.text-content h2 {
  color: #303133;
  margin: 30px 0 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #dcdfe6;
}

.text-content h3 {
  color: #409EFF;
  margin: 25px 0 15px;
}

.text-content ul,
.text-content ol {
  padding-left: 25px;
}

.text-content li {
  margin: 10px 0;
}

.text-content code {
  background: #f5f7fa;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: monospace;
}

.text-content kbd {
  background: #606266;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
}

.related-section {
  margin-top: 50px;
  padding-top: 30px;
  border-top: 2px solid #dcdfe6;
}

.related-section h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.related-card {
  cursor: pointer;
  transition: all 0.3s;
}

.related-card:hover {
  transform: translateY(-5px);
}

.related-content {
  text-align: center;
  padding: 20px;
}

.related-content h4 {
  margin: 15px 0 10px;
  color: #303133;
}

.related-content p {
  color: #909399;
  font-size: 13px;
}

/* 暗黑模式 */
.dark .text-content h2 {
  color: #e5eaf3;
  border-bottom-color: #4c4d4f;
}

.dark .text-content code {
  background: #2c2c2c;
}

.dark .related-content h4 {
  color: #e5eaf3;
}
</style>
