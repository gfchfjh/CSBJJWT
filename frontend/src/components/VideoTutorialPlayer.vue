<!--
  视频教程播放器
  ✅ P1-3优化：完整的视频播放控制
-->
<template>
  <div class="video-player-wrapper" :class="{ fullscreen: isFullscreen }" ref="playerWrapper">
    <div class="video-container">
      <!-- 视频元素 -->
      <video
        ref="videoRef"
        :src="videoUrl"
        :poster="poster"
        class="video-element"
        @loadedmetadata="onVideoLoaded"
        @timeupdate="onTimeUpdate"
        @ended="onVideoEnded"
        @play="isPlaying = true"
        @pause="isPlaying = false"
        @volumechange="onVolumeChange"
        @click="togglePlay"
      >
        您的浏览器不支持视频播放
      </video>
      
      <!-- 播放/暂停按钮（中央大按钮） -->
      <div
        v-if="!isPlaying && !loading"
        class="play-overlay"
        @click="togglePlay"
      >
        <el-icon :size="80" color="white" class="play-icon">
          <VideoPlay />
        </el-icon>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-overlay">
        <el-icon class="is-loading" :size="60" color="white">
          <Loading />
        </el-icon>
        <p>正在加载视频...</p>
      </div>
      
      <!-- 控制栏 -->
      <div class="controls-bar" :class="{ visible: showControls || !isPlaying }">
        <!-- 进度条 -->
        <div class="progress-container" @click="seek">
          <div class="progress-bar">
            <div class="progress-buffered" :style="{ width: bufferedPercent + '%' }"></div>
            <div class="progress-played" :style="{ width: playedPercent + '%' }"></div>
            <div class="progress-thumb" :style="{ left: playedPercent + '%' }"></div>
          </div>
        </div>
        
        <!-- 控制按钮 -->
        <div class="controls-buttons">
          <!-- 左侧：播放/暂停、音量 -->
          <div class="controls-left">
            <el-button
              text
              @click="togglePlay"
              size="large"
              class="control-btn"
            >
              <el-icon :size="24" color="white">
                <VideoPause v-if="isPlaying" />
                <VideoPlay v-else />
              </el-icon>
            </el-button>
            
            <div class="volume-control">
              <el-button
                text
                @click="toggleMute"
                size="large"
                class="control-btn"
              >
                <el-icon :size="22" color="white">
                  <Mute v-if="isMuted || volume === 0" />
                  <component :is="getVolumeIcon()" v-else />
                </el-icon>
              </el-button>
              
              <div class="volume-slider" v-show="showVolumeSlider">
                <el-slider
                  v-model="volume"
                  :min="0"
                  :max="100"
                  :show-tooltip="false"
                  @input="onVolumeSliderChange"
                  vertical
                  height="80px"
                />
              </div>
            </div>
            
            <span class="time-display">
              {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
            </span>
          </div>
          
          <!-- 中间：章节导航（如果有） -->
          <div class="controls-center" v-if="chapters && chapters.length > 0">
            <el-dropdown trigger="click">
              <el-button text class="control-btn">
                <el-icon :size="22" color="white"><Menu /></el-icon>
                <span style="color: white; margin-left: 5px;">章节</span>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    v-for="(chapter, index) in chapters"
                    :key="index"
                    @click="jumpToChapter(chapter)"
                  >
                    {{ chapter.title }} ({{ formatTime(chapter.time) }})
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          
          <!-- 右侧：播放速度、字幕、画质、全屏 -->
          <div class="controls-right">
            <!-- 播放速度 -->
            <el-dropdown trigger="click" @command="changeSpeed">
              <el-button text class="control-btn">
                <span style="color: white; font-size: 14px;">{{ playbackSpeed }}x</span>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="0.5">0.5x</el-dropdown-item>
                  <el-dropdown-item :command="0.75">0.75x</el-dropdown-item>
                  <el-dropdown-item :command="1.0">1.0x（正常）</el-dropdown-item>
                  <el-dropdown-item :command="1.25">1.25x</el-dropdown-item>
                  <el-dropdown-item :command="1.5">1.5x</el-dropdown-item>
                  <el-dropdown-item :command="2.0">2.0x</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            
            <!-- 画质选择 -->
            <el-dropdown v-if="qualities.length > 1" trigger="click" @command="changeQuality">
              <el-button text class="control-btn">
                <span style="color: white; font-size: 14px;">{{ currentQuality }}</span>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    v-for="quality in qualities"
                    :key="quality.label"
                    :command="quality"
                  >
                    {{ quality.label }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            
            <!-- 字幕 -->
            <el-button
              v-if="hasSubtitles"
              text
              @click="toggleSubtitles"
              class="control-btn"
              :class="{ active: showSubtitles }"
            >
              <el-icon :size="22" color="white"><Document /></el-icon>
            </el-button>
            
            <!-- 画中画 -->
            <el-button
              text
              @click="togglePictureInPicture"
              class="control-btn"
              v-if="supportsPip"
            >
              <el-icon :size="22" color="white"><CopyDocument /></el-icon>
            </el-button>
            
            <!-- 全屏 -->
            <el-button
              text
              @click="toggleFullscreen"
              class="control-btn"
            >
              <el-icon :size="22" color="white">
                <component :is="isFullscreen ? 'CloseFull' : 'FullScreen'" />
              </el-icon>
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 字幕显示 -->
      <div v-if="showSubtitles && currentSubtitle" class="subtitles">
        {{ currentSubtitle }}
      </div>
    </div>
    
    <!-- 视频信息 -->
    <div class="video-info" v-if="title">
      <h3>{{ title }}</h3>
      <p v-if="description">{{ description }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  VideoPlay,
  VideoPause,
  Loading,
  Mute,
  FullScreen,
  CloseFull,
  Menu,
  Document,
  CopyDocument
} from '@element-plus/icons-vue'

const props = defineProps({
  // 视频URL（支持多个画质）
  videoUrl: {
    type: [String, Array],
    required: true
  },
  // 海报图
  poster: {
    type: String,
    default: ''
  },
  // 标题
  title: {
    type: String,
    default: ''
  },
  // 描述
  description: {
    type: String,
    default: ''
  },
  // 章节列表
  chapters: {
    type: Array,
    default: () => []
  },
  // 字幕文件（WebVTT格式）
  subtitles: {
    type: String,
    default: ''
  },
  // 自动播放
  autoplay: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['ended', 'timeupdate', 'error'])

const playerWrapper = ref(null)
const videoRef = ref(null)

// 播放状态
const isPlaying = ref(false)
const loading = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const bufferedPercent = ref(0)

// 音量
const volume = ref(80)
const isMuted = ref(false)
const showVolumeSlider = ref(false)

// 播放速度
const playbackSpeed = ref(1.0)

// 全屏
const isFullscreen = ref(false)

// 控制栏显示
const showControls = ref(false)
let hideControlsTimer = null

// 字幕
const showSubtitles = ref(false)
const currentSubtitle = ref('')
const hasSubtitles = computed(() => !!props.subtitles)

// 画中画支持
const supportsPip = computed(() => {
  return document.pictureInPictureEnabled && videoRef.value
})

// 画质列表
const qualities = computed(() => {
  if (typeof props.videoUrl === 'string') {
    return [{ label: '标清', url: props.videoUrl }]
  } else if (Array.isArray(props.videoUrl)) {
    return props.videoUrl
  }
  return []
})

const currentQuality = ref('标清')

// 计算播放进度
const playedPercent = computed(() => {
  if (duration.value === 0) return 0
  return (currentTime.value / duration.value) * 100
})

// 视频加载完成
const onVideoLoaded = () => {
  if (!videoRef.value) return
  
  duration.value = videoRef.value.duration
  loading.value = false
  
  // 设置音量
  videoRef.value.volume = volume.value / 100
  
  // 自动播放
  if (props.autoplay) {
    play()
  }
}

// 时间更新
const onTimeUpdate = () => {
  if (!videoRef.value) return
  currentTime.value = videoRef.value.currentTime
  
  // 更新缓冲进度
  if (videoRef.value.buffered.length > 0) {
    const bufferedEnd = videoRef.value.buffered.end(videoRef.value.buffered.length - 1)
    bufferedPercent.value = (bufferedEnd / duration.value) * 100
  }
  
  emit('timeupdate', currentTime.value)
}

// 视频结束
const onVideoEnded = () => {
  isPlaying.value = false
  emit('ended')
}

// 音量改变
const onVolumeChange = () => {
  if (!videoRef.value) return
  isMuted.value = videoRef.value.muted
}

// 播放/暂停
const togglePlay = () => {
  if (!videoRef.value) return
  
  if (isPlaying.value) {
    pause()
  } else {
    play()
  }
}

const play = async () => {
  if (!videoRef.value) return
  
  try {
    await videoRef.value.play()
    isPlaying.value = true
  } catch (error) {
    console.error('播放失败:', error)
    ElMessage.error('播放失败: ' + error.message)
    emit('error', error)
  }
}

const pause = () => {
  if (!videoRef.value) return
  videoRef.value.pause()
  isPlaying.value = false
}

// 音量控制
const toggleMute = () => {
  if (!videoRef.value) return
  videoRef.value.muted = !videoRef.value.muted
  isMuted.value = videoRef.value.muted
}

const onVolumeSliderChange = (value) => {
  if (!videoRef.value) return
  videoRef.value.volume = value / 100
  if (value > 0) {
    isMuted.value = false
    videoRef.value.muted = false
  }
}

const getVolumeIcon = () => {
  if (volume.value > 60) return 'MostlyCloudy'
  if (volume.value > 30) return 'PartlyCloudy'
  return 'Sunny'
}

// 进度跳转
const seek = (event) => {
  if (!videoRef.value) return
  
  const progressBar = event.currentTarget
  const rect = progressBar.getBoundingClientRect()
  const percent = (event.clientX - rect.left) / rect.width
  const newTime = percent * duration.value
  
  videoRef.value.currentTime = newTime
  currentTime.value = newTime
}

// 播放速度
const changeSpeed = (speed) => {
  if (!videoRef.value) return
  videoRef.value.playbackRate = speed
  playbackSpeed.value = speed
}

// 画质切换
const changeQuality = (quality) => {
  if (!videoRef.value) return
  
  const currentTimeBackup = currentTime.value
  const wasPlaying = isPlaying.value
  
  // 切换视频源
  videoRef.value.src = quality.url
  currentQuality.value = quality.label
  
  // 恢复播放位置
  videoRef.value.addEventListener('loadedmetadata', () => {
    videoRef.value.currentTime = currentTimeBackup
    if (wasPlaying) {
      play()
    }
  }, { once: true })
  
  ElMessage.success(`已切换到 ${quality.label}`)
}

// 全屏
const toggleFullscreen = async () => {
  if (!playerWrapper.value) return
  
  try {
    if (!isFullscreen.value) {
      // 进入全屏
      if (playerWrapper.value.requestFullscreen) {
        await playerWrapper.value.requestFullscreen()
      } else if (playerWrapper.value.webkitRequestFullscreen) {
        await playerWrapper.value.webkitRequestFullscreen()
      } else if (playerWrapper.value.mozRequestFullScreen) {
        await playerWrapper.value.mozRequestFullScreen()
      }
      isFullscreen.value = true
    } else {
      // 退出全屏
      if (document.exitFullscreen) {
        await document.exitFullscreen()
      } else if (document.webkitExitFullscreen) {
        await document.webkitExitFullscreen()
      } else if (document.mozCancelFullScreen) {
        await document.mozCancelFullScreen()
      }
      isFullscreen.value = false
    }
  } catch (error) {
    console.error('全屏切换失败:', error)
  }
}

// 画中画
const togglePictureInPicture = async () => {
  if (!videoRef.value) return
  
  try {
    if (document.pictureInPictureElement) {
      await document.exitPictureInPicture()
    } else {
      await videoRef.value.requestPictureInPicture()
    }
  } catch (error) {
    console.error('画中画切换失败:', error)
    ElMessage.error('您的浏览器不支持画中画功能')
  }
}

// 字幕
const toggleSubtitles = () => {
  showSubtitles.value = !showSubtitles.value
}

// 跳转到章节
const jumpToChapter = (chapter) => {
  if (!videoRef.value) return
  videoRef.value.currentTime = chapter.time
  play()
}

// 格式化时间
const formatTime = (seconds) => {
  if (isNaN(seconds) || seconds === Infinity) return '00:00'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

// 控制栏自动隐藏
const showControlsTemporarily = () => {
  showControls.value = true
  
  if (hideControlsTimer) {
    clearTimeout(hideControlsTimer)
  }
  
  if (isPlaying.value) {
    hideControlsTimer = setTimeout(() => {
      showControls.value = false
    }, 3000)
  }
}

// 监听全屏变化
const onFullscreenChange = () => {
  isFullscreen.value = !!(
    document.fullscreenElement ||
    document.webkitFullscreenElement ||
    document.mozFullScreenElement
  )
}

// 键盘快捷键
const onKeyDown = (event) => {
  if (!videoRef.value) return
  
  switch (event.key) {
    case ' ':
    case 'k':
      event.preventDefault()
      togglePlay()
      break
    case 'f':
      event.preventDefault()
      toggleFullscreen()
      break
    case 'm':
      event.preventDefault()
      toggleMute()
      break
    case 'ArrowLeft':
      event.preventDefault()
      videoRef.value.currentTime = Math.max(0, currentTime.value - 5)
      break
    case 'ArrowRight':
      event.preventDefault()
      videoRef.value.currentTime = Math.min(duration.value, currentTime.value + 5)
      break
    case 'ArrowUp':
      event.preventDefault()
      volume.value = Math.min(100, volume.value + 10)
      onVolumeSliderChange(volume.value)
      break
    case 'ArrowDown':
      event.preventDefault()
      volume.value = Math.max(0, volume.value - 10)
      onVolumeSliderChange(volume.value)
      break
  }
}

onMounted(() => {
  // 监听全屏变化
  document.addEventListener('fullscreenchange', onFullscreenChange)
  document.addEventListener('webkitfullscreenchange', onFullscreenChange)
  document.addEventListener('mozfullscreenchange', onFullscreenChange)
  
  // 监听键盘
  document.addEventListener('keydown', onKeyDown)
  
  // 监听鼠标移动（显示控制栏）
  if (playerWrapper.value) {
    playerWrapper.value.addEventListener('mousemove', showControlsTemporarily)
  }
  
  // 设置初始画质
  if (qualities.value.length > 0) {
    currentQuality.value = qualities.value[0].label
  }
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', onFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', onFullscreenChange)
  document.removeEventListener('mozfullscreenchange', onFullscreenChange)
  document.removeEventListener('keydown', onKeyDown)
  
  if (hideControlsTimer) {
    clearTimeout(hideControlsTimer)
  }
})
</script>

<style scoped>
.video-player-wrapper {
  width: 100%;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-player-wrapper.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  border-radius: 0;
}

.video-container {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 比例 */
  background: #000;
}

.video-element {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

/* 播放按钮覆盖层 */
.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: background 0.3s;
}

.play-overlay:hover {
  background: rgba(0, 0, 0, 0.5);
}

.play-icon {
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.5));
  transition: transform 0.3s;
}

.play-overlay:hover .play-icon {
  transform: scale(1.1);
}

/* 加载状态 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  gap: 15px;
}

/* 控制栏 */
.controls-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
  padding: 15px;
  opacity: 0;
  transition: opacity 0.3s;
}

.controls-bar.visible {
  opacity: 1;
}

/* 进度条 */
.progress-container {
  margin-bottom: 10px;
  cursor: pointer;
  padding: 5px 0;
}

.progress-bar {
  position: relative;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  overflow: visible;
}

.progress-buffered {
  position: absolute;
  height: 100%;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 2px;
  transition: width 0.3s;
}

.progress-played {
  position: absolute;
  height: 100%;
  background: #409EFF;
  border-radius: 2px;
  transition: width 0.1s linear;
}

.progress-thumb {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 12px;
  height: 12px;
  background: white;
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  transition: left 0.1s linear;
}

.progress-container:hover .progress-bar {
  height: 6px;
}

.progress-container:hover .progress-thumb {
  width: 14px;
  height: 14px;
}

/* 控制按钮 */
.controls-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.controls-left,
.controls-center,
.controls-right {
  display: flex;
  align-items: center;
  gap: 5px;
}

.control-btn {
  padding: 5px;
  min-width: auto;
}

.control-btn.active {
  background: rgba(255, 255, 255, 0.2);
}

.time-display {
  color: white;
  font-size: 14px;
  font-weight: 500;
  margin-left: 5px;
}

/* 音量控制 */
.volume-control {
  position: relative;
}

.volume-slider {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  padding: 10px;
  background: rgba(0, 0, 0, 0.9);
  border-radius: 6px;
  margin-bottom: 10px;
}

/* 字幕 */
.subtitles {
  position: absolute;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  font-size: 16px;
  border-radius: 4px;
  max-width: 80%;
  text-align: center;
}

/* 视频信息 */
.video-info {
  padding: 15px;
  background: white;
}

.video-info h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
  font-weight: 600;
}

.video-info p {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

/* 响应式 */
@media (max-width: 768px) {
  .controls-buttons {
    flex-wrap: wrap;
  }
  
  .time-display {
    font-size: 12px;
  }
}
</style>
