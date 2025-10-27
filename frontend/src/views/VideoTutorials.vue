<template>
  <div class="video-tutorials">
    <!-- ✅ P0-6优化: 应用内视频教程播放器 -->
    
    <!-- 顶部导航 -->
    <div class="tutorials-header">
      <h1>📺 视频教程中心</h1>
      <p class="subtitle">观看视频教程，快速掌握KOOK消息转发系统</p>
    </div>

    <el-row :gutter="30">
      <!-- 左侧：播放器 -->
      <el-col :span="16">
        <el-card class="player-card" shadow="hover">
          <template #header>
            <div class="player-header">
              <h2>{{ currentVideo.title }}</h2>
              <div class="player-meta">
                <el-tag type="info">时长 {{ currentVideo.duration }}</el-tag>
                <el-tag type="success">
                  <el-icon><View /></el-icon>
                  {{ currentVideo.views }} 次观看
                </el-tag>
                <el-tag v-if="currentVideo.difficulty" :type="difficultyType(currentVideo.difficulty)">
                  难度: {{ currentVideo.difficulty }}
                </el-tag>
              </div>
            </div>
          </template>

          <!-- HTML5视频播放器 -->
          <div class="video-player-container">
            <video
              ref="videoPlayer"
              class="video-player"
              :src="currentVideo.url"
              :poster="currentVideo.poster"
              controls
              controlsList="nodownload"
              @ended="handleVideoEnded"
              @timeupdate="handleTimeUpdate"
              @loadedmetadata="handleMetadataLoaded"
            >
              <!-- 字幕支持 -->
              <track
                v-if="currentVideo.subtitle"
                kind="subtitles"
                :src="currentVideo.subtitle"
                srclang="zh-CN"
                label="中文"
                default
              />
              您的浏览器不支持视频播放
            </video>

            <!-- 自定义控制栏（可选） -->
            <div class="custom-controls">
              <!-- 播放/暂停 -->
              <el-button-group>
                <el-button @click="togglePlay" :icon="isPlaying ? 'VideoPause' : 'VideoPlay'">
                  {{ isPlaying ? '暂停' : '播放' }}
                </el-button>
                <el-button @click="rewind" icon="DArrowLeft">
                  -10秒
                </el-button>
                <el-button @click="forward" icon="DArrowRight">
                  +10秒
                </el-button>
              </el-button-group>

              <!-- 进度条 -->
              <div class="progress-container">
                <span class="time-display">{{ formatTime(currentTime) }}</span>
                <el-slider
                  v-model="progressPercent"
                  :show-tooltip="false"
                  @change="seekToPercent"
                  class="progress-slider"
                />
                <span class="time-display">{{ formatTime(duration) }}</span>
              </div>

              <!-- 速度和音量 -->
              <div class="extra-controls">
                <el-select v-model="playbackRate" size="small" style="width: 100px;" @change="changePlaybackRate">
                  <el-option label="0.5x" :value="0.5" />
                  <el-option label="0.75x" :value="0.75" />
                  <el-option label="1.0x" :value="1.0" />
                  <el-option label="1.25x" :value="1.25" />
                  <el-option label="1.5x" :value="1.5" />
                  <el-option label="2.0x" :value="2.0" />
                </el-select>

                <el-button @click="toggleMute" :icon="isMuted ? 'Mute' : 'Unmute'">
                  {{ isMuted ? '取消静音' : '静音' }}
                </el-button>

                <el-button @click="toggleFullscreen" icon="FullScreen">
                  全屏
                </el-button>
              </div>
            </div>
          </div>

          <!-- 视频描述 -->
          <div class="video-description">
            <h3>📝 教程介绍</h3>
            <p>{{ currentVideo.description }}</p>

            <!-- 章节列表（如果有） -->
            <div v-if="currentVideo.chapters && currentVideo.chapters.length > 0" class="video-chapters">
              <h4>📑 章节目录</h4>
              <div
                v-for="(chapter, index) in currentVideo.chapters"
                :key="index"
                class="chapter-item"
                :class="{ 'is-active': currentChapter === index }"
                @click="jumpToChapter(chapter)"
              >
                <span class="chapter-time">{{ formatTime(chapter.time) }}</span>
                <span class="chapter-title">{{ chapter.title }}</span>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="video-actions">
              <el-button @click="markAsWatched" :disabled="!canMarkWatched">
                <el-icon><Check /></el-icon>
                标记为已观看
              </el-button>
              <el-button @click="shareVideo">
                <el-icon><Share /></el-icon>
                分享
              </el-button>
              <el-button @click="reportIssue">
                <el-icon><Warning /></el-icon>
                报告问题
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：教程列表 -->
      <el-col :span="8">
        <el-card class="tutorials-list-card">
          <template #header>
            <div class="list-header">
              <h3>🎬 教程列表</h3>
              <el-input
                v-model="searchKeyword"
                placeholder="搜索教程"
                size="small"
                clearable
              >
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
            </div>
          </template>

          <!-- 教程分类 -->
          <el-tabs v-model="activeCategory">
            <el-tab-pane label="全部" name="all" />
            <el-tab-pane label="入门" name="beginner" />
            <el-tab-pane label="配置" name="config" />
            <el-tab-pane label="高级" name="advanced" />
          </el-tabs>

          <!-- 教程卡片列表 -->
          <div class="tutorials-list">
            <div
              v-for="video in filteredVideos"
              :key="video.id"
              class="tutorial-card"
              :class="{ 'is-current': video.id === currentVideo.id, 'is-watched': video.watched }"
              @click="playVideo(video)"
            >
              <!-- 缩略图 -->
              <div class="tutorial-thumbnail">
                <img :src="video.poster" :alt="video.title" />
                <div class="play-overlay">
                  <el-icon :size="40"><VideoPlay /></el-icon>
                </div>
                <div class="duration-badge">{{ video.duration }}</div>
                <div v-if="video.watched" class="watched-badge">
                  <el-icon><Check /></el-icon>
                </div>
              </div>

              <!-- 信息 -->
              <div class="tutorial-info">
                <h4 class="tutorial-title">{{ video.title }}</h4>
                <p class="tutorial-desc">{{ video.shortDesc }}</p>
                <div class="tutorial-meta">
                  <span><el-icon><View /></el-icon> {{ video.views }}</span>
                  <el-tag :type="difficultyType(video.difficulty)" size="small">
                    {{ video.difficulty }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 推荐教程 -->
        <el-card class="related-card" v-if="relatedVideos.length > 0">
          <template #header>
            <h3>🔗 相关推荐</h3>
          </template>
          
          <div class="related-list">
            <div
              v-for="video in relatedVideos"
              :key="video.id"
              class="related-item"
              @click="playVideo(video)"
            >
              <img :src="video.poster" :alt="video.title" class="related-thumb" />
              <div class="related-info">
                <h5>{{ video.title }}</h5>
                <p>{{ video.duration }}</p>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import {
  View, Check, Share, Warning, Search, VideoPlay
} from '@element-plus/icons-vue'
import api from '@/api'

// 当前播放的视频
const currentVideo = ref({
  id: 1,
  title: '01. 快速入门指南 - 5分钟上手',
  duration: '5:30',
  url: '/videos/01-quickstart.mp4',  // 实际应该是真实的视频URL
  poster: '/images/video-posters/01-quickstart.jpg',
  description: '本教程将带您快速了解KOOK消息转发系统的核心功能，5分钟即可完成首次配置。',
  shortDesc: '快速了解系统核心功能',
  category: 'beginner',
  difficulty: '⭐ 入门',
  views: 1234,
  watched: false,
  chapters: [
    { time: 0, title: '欢迎介绍' },
    { time: 30, title: 'Cookie导入' },
    { time: 120, title: '配置Bot' },
    { time: 240, title: '频道映射' },
    { time: 300, title: '启动服务' }
  ]
})

// 视频列表（8个教程）
const videos = ref([
  {
    id: 1,
    title: '01. 快速入门指南 - 5分钟上手',
    duration: '5:30',
    url: '/videos/01-quickstart.mp4',
    poster: '/images/video-posters/01-quickstart.jpg',
    description: '本教程将带您快速了解KOOK消息转发系统的核心功能，5分钟即可完成首次配置。',
    shortDesc: '快速了解系统核心功能',
    category: 'beginner',
    difficulty: '⭐ 入门',
    views: 1234,
    watched: false
  },
  {
    id: 2,
    title: '02. Cookie获取详细教程',
    duration: '3:15',
    url: '/videos/02-cookie.mp4',
    poster: '/images/video-posters/02-cookie.jpg',
    description: '详细演示如何从浏览器中获取KOOK的Cookie，支持Chrome、Firefox、Edge等浏览器。',
    shortDesc: '3种方法获取Cookie',
    category: 'beginner',
    difficulty: '⭐ 入门',
    views: 987,
    watched: false
  },
  {
    id: 3,
    title: '03. Discord Webhook配置',
    duration: '2:45',
    url: '/videos/03-discord.mp4',
    poster: '/images/video-posters/03-discord.jpg',
    description: '手把手教您创建Discord Webhook，包括权限设置和测试验证。',
    shortDesc: '创建Webhook，2分钟搞定',
    category: 'config',
    difficulty: '⭐ 入门',
    views: 856,
    watched: false
  },
  {
    id: 4,
    title: '04. Telegram Bot配置教程',
    duration: '4:20',
    url: '/videos/04-telegram.mp4',
    poster: '/images/video-posters/04-telegram.jpg',
    description: '详细讲解如何与BotFather创建Bot，获取Token和Chat ID。',
    shortDesc: '创建Bot，4分钟完成',
    category: 'config',
    difficulty: '⭐⭐ 简单',
    views: 765,
    watched: false
  },
  {
    id: 5,
    title: '05. 飞书自建应用配置',
    duration: '6:30',
    url: '/videos/05-feishu.mp4',
    poster: '/images/video-posters/05-feishu.jpg',
    description: '完整演示飞书开放平台创建自建应用的流程，包括权限配置和群组添加。',
    shortDesc: '自建应用，10分钟配置',
    category: 'config',
    difficulty: '⭐⭐ 简单',
    views: 543,
    watched: false
  },
  {
    id: 6,
    title: '06. 智能映射功能详解',
    duration: '5:50',
    url: '/videos/06-smart-mapping.mp4',
    poster: '/images/video-posters/06-smart-mapping.jpg',
    description: '详细介绍智能映射算法，如何使用60+映射规则自动匹配频道。',
    shortDesc: '自动匹配，效率提升500%',
    category: 'advanced',
    difficulty: '⭐⭐⭐ 中等',
    views: 432,
    watched: false
  },
  {
    id: 7,
    title: '07. 过滤规则使用技巧',
    duration: '4:15',
    url: '/videos/07-filter-rules.mp4',
    poster: '/images/video-posters/07-filter-rules.jpg',
    description: '讲解如何配置关键词过滤、用户过滤和消息类型过滤，实现精准转发。',
    shortDesc: '精准过滤，避免噪音',
    category: 'advanced',
    difficulty: '⭐⭐ 简单',
    views: 321,
    watched: false
  },
  {
    id: 8,
    title: '08. 常见问题排查指南',
    duration: '7:20',
    url: '/videos/08-troubleshooting.mp4',
    poster: '/images/video-posters/08-troubleshooting.jpg',
    description: '介绍常见问题的排查方法，包括登录失败、转发失败、性能问题等。',
    shortDesc: '问题排查，自助解决',
    category: 'advanced',
    difficulty: '⭐⭐⭐ 中等',
    views: 234,
    watched: false
  }
])

// UI状态
const activeCategory = ref('all')
const searchKeyword = ref('')

// 播放器状态
const videoPlayer = ref(null)
const isPlaying = ref(false)
const isMuted = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const playbackRate = ref(1.0)
const currentChapter = ref(0)

// 计算属性
const progressPercent = computed({
  get: () => {
    if (duration.value === 0) return 0
    return (currentTime.value / duration.value) * 100
  },
  set: (val) => {
    if (videoPlayer.value) {
      videoPlayer.value.currentTime = (val / 100) * duration.value
    }
  }
})

const filteredVideos = computed(() => {
  let result = videos.value

  // 分类过滤
  if (activeCategory.value !== 'all') {
    result = result.filter(v => v.category === activeCategory.value)
  }

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(v =>
      v.title.toLowerCase().includes(keyword) ||
      v.description.toLowerCase().includes(keyword)
    )
  }

  return result
})

const relatedVideos = computed(() => {
  // 推荐相同分类的其他视频
  return videos.value
    .filter(v => 
      v.id !== currentVideo.value.id && 
      v.category === currentVideo.value.category
    )
    .slice(0, 3)
})

const canMarkWatched = computed(() => {
  // 播放超过80%才能标记为已观看
  return progressPercent.value > 80
})

// 播放器控制
const togglePlay = () => {
  if (!videoPlayer.value) return
  
  if (isPlaying.value) {
    videoPlayer.value.pause()
  } else {
    videoPlayer.value.play()
  }
  isPlaying.value = !isPlaying.value
}

const rewind = () => {
  if (videoPlayer.value) {
    videoPlayer.value.currentTime = Math.max(0, videoPlayer.value.currentTime - 10)
  }
}

const forward = () => {
  if (videoPlayer.value) {
    videoPlayer.value.currentTime = Math.min(duration.value, videoPlayer.value.currentTime + 10)
  }
}

const toggleMute = () => {
  if (videoPlayer.value) {
    videoPlayer.value.muted = !videoPlayer.value.muted
    isMuted.value = videoPlayer.value.muted
  }
}

const toggleFullscreen = () => {
  if (videoPlayer.value) {
    if (videoPlayer.value.requestFullscreen) {
      videoPlayer.value.requestFullscreen()
    } else if (videoPlayer.value.webkitRequestFullscreen) {
      videoPlayer.value.webkitRequestFullscreen()
    }
  }
}

const changePlaybackRate = () => {
  if (videoPlayer.value) {
    videoPlayer.value.playbackRate = playbackRate.value
  }
}

const seekToPercent = (percent) => {
  if (videoPlayer.value) {
    videoPlayer.value.currentTime = (percent / 100) * duration.value
  }
}

// 事件处理
const handleTimeUpdate = (e) => {
  currentTime.value = e.target.currentTime
  
  // 更新当前章节
  if (currentVideo.value.chapters) {
    const chapters = currentVideo.value.chapters
    for (let i = chapters.length - 1; i >= 0; i--) {
      if (currentTime.value >= chapters[i].time) {
        currentChapter.value = i
        break
      }
    }
  }
}

const handleMetadataLoaded = (e) => {
  duration.value = e.target.duration
}

const handleVideoEnded = async () => {
  isPlaying.value = false
  
  // 标记为已观看
  currentVideo.value.watched = true
  const video = videos.value.find(v => v.id === currentVideo.value.id)
  if (video) {
    video.watched = true
  }
  
  // 增加观看次数
  await incrementViews(currentVideo.value.id)
  
  // 询问是否播放下一个
  ElMessageBox.confirm(
    '本教程已播放完毕，是否继续播放下一个？',
    '播放完成',
    {
      type: 'success',
      confirmButtonText: '播放下一个',
      cancelButtonText: '返回列表'
    }
  ).then(() => {
    playNextVideo()
  }).catch(() => {
    // 用户选择不播放
  })
}

// 视频切换
const playVideo = (video) => {
  currentVideo.value = video
  currentTime.value = 0
  currentChapter.value = 0
  isPlaying.value = false
  
  // 滚动到播放器
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const playNextVideo = () => {
  const currentIndex = videos.value.findIndex(v => v.id === currentVideo.value.id)
  if (currentIndex < videos.value.length - 1) {
    playVideo(videos.value[currentIndex + 1])
    
    // 自动播放
    setTimeout(() => {
      togglePlay()
    }, 500)
  } else {
    ElMessage.info('已经是最后一个教程了')
  }
}

const jumpToChapter = (chapter) => {
  if (videoPlayer.value) {
    videoPlayer.value.currentTime = chapter.time
  }
}

// 操作
const markAsWatched = async () => {
  try {
    currentVideo.value.watched = true
    const video = videos.value.find(v => v.id === currentVideo.value.id)
    if (video) {
      video.watched = true
    }
    
    await api.post('/api/videos/mark-watched', {
      video_id: currentVideo.value.id
    })
    
    ElMessage.success('已标记为观看')
  } catch (error) {
    ElMessage.error('标记失败: ' + error.message)
  }
}

const incrementViews = async (videoId) => {
  try {
    await api.post('/api/videos/increment-views', { video_id: videoId })
  } catch (error) {
    console.error('增加观看次数失败:', error)
  }
}

const shareVideo = () => {
  const url = window.location.origin + `/help/videos?id=${currentVideo.value.id}`
  navigator.clipboard.writeText(url).then(() => {
    ElMessage.success('视频链接已复制到剪贴板')
  })
}

const reportIssue = () => {
  ElMessage.info('请通过GitHub Issues报告问题')
}

// 工具函数
const formatTime = (seconds) => {
  if (!seconds || isNaN(seconds)) return '0:00'
  
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const difficultyType = (difficulty) => {
  if (!difficulty) return 'info'
  if (difficulty.includes('入门')) return 'success'
  if (difficulty.includes('简单')) return 'primary'
  if (difficulty.includes('中等')) return 'warning'
  return 'danger'
}

// 生命周期
onMounted(() => {
  // 加载视频观看记录
  loadWatchedVideos()
})

const loadWatchedVideos = async () => {
  try {
    const response = await api.get('/api/videos/watched')
    if (response.data.success) {
      const watchedIds = response.data.watched_ids
      videos.value.forEach(v => {
        v.watched = watchedIds.includes(v.id)
      })
    }
  } catch (error) {
    console.error('加载观看记录失败:', error)
  }
}
</script>

<style scoped lang="scss">
.video-tutorials {
  padding: 30px;
  background: #F5F7FA;
  min-height: 100vh;
}

.tutorials-header {
  text-align: center;
  margin-bottom: 40px;
  
  h1 {
    font-size: 36px;
    margin-bottom: 10px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  
  .subtitle {
    font-size: 16px;
    color: #909399;
  }
}

/* 播放器卡片 */
.player-card {
  margin-bottom: 20px;
}

.player-header {
  h2 {
    margin: 0 0 10px 0;
    font-size: 22px;
  }
  
  .player-meta {
    display: flex;
    gap: 10px;
    align-items: center;
  }
}

.video-player-container {
  margin-bottom: 20px;
  
  .video-player {
    width: 100%;
    max-height: 500px;
    border-radius: 8px;
    background: #000;
  }
  
  .custom-controls {
    margin-top: 15px;
    display: flex;
    flex-direction: column;
    gap: 15px;
    
    .progress-container {
      display: flex;
      align-items: center;
      gap: 15px;
      
      .time-display {
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 14px;
        color: #606266;
        min-width: 50px;
      }
      
      .progress-slider {
        flex: 1;
      }
    }
    
    .extra-controls {
      display: flex;
      gap: 10px;
      justify-content: flex-end;
    }
  }
}

.video-description {
  h3 {
    margin: 0 0 15px 0;
    font-size: 18px;
  }
  
  p {
    line-height: 1.8;
    color: #606266;
    margin-bottom: 20px;
  }
}

.video-chapters {
  margin: 20px 0;
  
  h4 {
    margin-bottom: 15px;
    font-size: 16px;
  }
  
  .chapter-item {
    display: flex;
    gap: 15px;
    padding: 12px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
    
    &:hover {
      background: #ECF5FF;
    }
    
    &.is-active {
      background: #409EFF;
      color: white;
    }
    
    .chapter-time {
      font-family: 'Monaco', 'Menlo', monospace;
      font-size: 12px;
      color: #909399;
      min-width: 50px;
    }
    
    .chapter-title {
      flex: 1;
      font-size: 14px;
    }
  }
}

.video-actions {
  display: flex;
  gap: 15px;
  margin-top: 20px;
}

/* 教程列表 */
.tutorials-list-card {
  margin-bottom: 20px;
}

.list-header {
  h3 {
    margin: 0 0 15px 0;
    font-size: 18px;
  }
}

.tutorials-list {
  max-height: 600px;
  overflow-y: auto;
}

.tutorial-card {
  cursor: pointer;
  margin-bottom: 15px;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
  border: 2px solid transparent;
  
  &:hover {
    border-color: #409EFF;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
  }
  
  &.is-current {
    border-color: #409EFF;
    background: #ECF5FF;
  }
  
  &.is-watched {
    opacity: 0.7;
  }
  
  .tutorial-thumbnail {
    position: relative;
    height: 120px;
    overflow: hidden;
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .play-overlay {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      color: white;
      background: rgba(0, 0, 0, 0.6);
      width: 60px;
      height: 60px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity 0.3s;
    }
    
    &:hover .play-overlay {
      opacity: 1;
    }
    
    .duration-badge {
      position: absolute;
      bottom: 10px;
      right: 10px;
      background: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
      font-family: 'Monaco', 'Menlo', monospace;
    }
    
    .watched-badge {
      position: absolute;
      top: 10px;
      right: 10px;
      background: #67C23A;
      color: white;
      width: 30px;
      height: 30px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
  
  .tutorial-info {
    padding: 15px;
    
    .tutorial-title {
      margin: 0 0 8px 0;
      font-size: 15px;
      font-weight: 600;
      color: #303133;
    }
    
    .tutorial-desc {
      margin: 0 0 10px 0;
      font-size: 13px;
      color: #606266;
      line-height: 1.5;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }
    
    .tutorial-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      color: #909399;
      
      span {
        display: flex;
        align-items: center;
        gap: 3px;
      }
    }
  }
}

/* 相关推荐 */
.related-card {
  .related-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .related-item {
    display: flex;
    gap: 12px;
    cursor: pointer;
    padding: 10px;
    border-radius: 8px;
    transition: all 0.3s;
    
    &:hover {
      background: #ECF5FF;
    }
    
    .related-thumb {
      width: 80px;
      height: 60px;
      border-radius: 6px;
      object-fit: cover;
    }
    
    .related-info {
      flex: 1;
      
      h5 {
        margin: 0 0 5px 0;
        font-size: 13px;
        color: #303133;
      }
      
      p {
        margin: 0;
        font-size: 12px;
        color: #909399;
      }
    }
  }
}
</style>
