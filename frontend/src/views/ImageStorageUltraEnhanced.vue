<template>
  <div class="image-storage-ultra">
    <!-- ✅ P0-8优化: 图床管理界面增强 - 双视图+Lightbox预览 -->
    
    <!-- 顶部操作栏 -->
    <div class="storage-header">
      <h1>🖼️ 图床存储管理</h1>
      
      <div class="header-actions">
        <!-- 视图切换 -->
        <el-radio-group v-model="viewMode" size="large">
          <el-radio-button value="grid">
            <el-icon><Grid /></el-icon>
            网格视图
          </el-radio-button>
          <el-radio-button value="list">
            <el-icon><List /></el-icon>
            列表视图
          </el-radio-button>
        </el-radio-group>

        <!-- 排序 -->
        <el-select v-model="sortBy" placeholder="排序" style="width: 150px;">
          <el-option label="时间（最新）" value="time_desc" />
          <el-option label="时间（最早）" value="time_asc" />
          <el-option label="大小（大到小）" value="size_desc" />
          <el-option label="大小（小到大）" value="size_asc" />
          <el-option label="名称（A-Z）" value="name_asc" />
        </el-select>

        <!-- 搜索 -->
        <el-input
          v-model="searchKeyword"
          placeholder="搜索文件名"
          clearable
          style="width: 250px;"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <!-- 刷新 -->
        <el-button @click="loadImages" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 统计卡片（4个彩色渐变卡片） -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <div class="stat-card gradient-blue">
          <div class="stat-icon">📦</div>
          <div class="stat-content">
            <div class="stat-value">{{ storageInfo.total_gb }}GB</div>
            <div class="stat-label">总空间</div>
          </div>
        </div>
      </el-col>

      <el-col :span="6">
        <div class="stat-card gradient-orange">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <div class="stat-value">{{ storageInfo.used_gb }}GB</div>
            <div class="stat-label">已使用</div>
          </div>
        </div>
      </el-col>

      <el-col :span="6">
        <div class="stat-card gradient-green">
          <div class="stat-icon">💾</div>
          <div class="stat-content">
            <div class="stat-value">{{ storageInfo.available_gb }}GB</div>
            <div class="stat-label">剩余空间</div>
          </div>
        </div>
      </el-col>

      <el-col :span="6">
        <div class="stat-card gradient-purple">
          <div class="stat-icon">🖼️</div>
          <div class="stat-content">
            <div class="stat-value">{{ storageInfo.image_count }}</div>
            <div class="stat-label">图片数量</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 动态进度条（根据使用率变色） -->
    <el-card class="usage-card">
      <div class="usage-header">
        <span>存储使用率</span>
        <span class="usage-percentage" :class="usageClass">
          {{ storageInfo.usage_percent }}%
        </span>
      </div>
      
      <el-progress
        :percentage="storageInfo.usage_percent"
        :color="usageColor"
        :stroke-width="24"
      >
        <template #default="{ percentage }">
          <span class="progress-text">{{ percentage }}%</span>
        </template>
      </el-progress>

      <div class="usage-tip" v-if="storageInfo.usage_percent > 80">
        <el-icon color="#F56C6C"><Warning /></el-icon>
        <span>存储空间紧张，建议清理旧图片</span>
      </div>
    </el-card>

    <!-- 清理操作卡片 -->
    <el-card class="cleanup-card">
      <template #header>
        <span>🗑️ 智能清理</span>
      </template>

      <el-row :gutter="15">
        <el-col :span="12">
          <div class="cleanup-option">
            <h4>按天数清理</h4>
            <el-input-number
              v-model="cleanupDays"
              :min="1"
              :max="30"
              controls-position="right"
            />
            <span class="cleanup-label">天前的图片</span>
            
            <p class="estimate-text" v-if="estimatedSpace > 0">
              预估释放: <strong>{{ estimatedSpace }}MB</strong>
            </p>

            <el-button
              type="warning"
              @click="cleanupByDays"
              :loading="cleanupLoading"
            >
              <el-icon><Delete /></el-icon>
              清理旧图片
            </el-button>
          </div>
        </el-col>

        <el-col :span="12">
          <div class="cleanup-option">
            <h4>清空所有</h4>
            <p class="cleanup-warning">
              ⚠️ 将删除所有缓存图片，此操作不可撤销
            </p>

            <el-button
              type="danger"
              @click="clearAllImages"
              :loading="cleanupLoading"
            >
              <el-icon><Delete /></el-icon>
              清空所有图片
            </el-button>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 图片列表 -->
    <el-card class="images-card">
      <template #header>
        <div class="images-header">
          <span>📷 图片列表 ({{ filteredImages.length }} / {{ totalImages }})</span>
          
          <div class="header-actions">
            <el-button-group>
              <el-button @click="selectAll" size="small">
                <el-icon><Select /></el-icon>
                全选
              </el-button>
              <el-button @click="unselectAll" size="small">
                <el-icon><Close /></el-icon>
                取消
              </el-button>
            </el-button-group>

            <el-button
              v-if="selectedImages.length > 0"
              type="danger"
              size="small"
              @click="deleteSelected"
            >
              <el-icon><Delete /></el-icon>
              删除选中 ({{ selectedImages.length }})
            </el-button>
          </div>
        </div>
      </template>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="5" animated />
      </div>

      <!-- 网格视图 -->
      <div v-else-if="viewMode === 'grid' && filteredImages.length > 0" class="grid-view">
        <div
          v-for="image in filteredImages"
          :key="image.filename"
          class="image-card"
          :class="{ 'is-selected': selectedImages.includes(image.filename) }"
        >
          <!-- 选择框 -->
          <el-checkbox
            v-model="selectedImages"
            :label="image.filename"
            :value="image.filename"
            class="image-checkbox"
          />

          <!-- 图片缩略图（点击打开Lightbox） -->
          <div class="image-thumbnail" @click="openLightbox(image)">
            <el-image
              :src="image.url"
              fit="cover"
              lazy
            >
              <template #placeholder>
                <div class="image-loading">
                  <el-icon class="is-loading"><Loading /></el-icon>
                </div>
              </template>
              <template #error>
                <div class="image-error">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>

            <!-- 悬停操作层 -->
            <div class="image-overlay">
              <el-button-group>
                <el-button size="small" @click.stop="previewImage(image)">
                  <el-icon><View /></el-icon>
                </el-button>
                <el-button size="small" @click.stop="copyUrl(image.url)">
                  <el-icon><CopyDocument /></el-icon>
                </el-button>
                <el-button 
                  size="small" 
                  type="danger"
                  @click.stop="deleteImage(image)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-button-group>
            </div>
          </div>

          <!-- 图片信息 -->
          <div class="image-info">
            <div class="image-name" :title="image.filename">
              {{ truncateName(image.filename) }}
            </div>
            <div class="image-meta">
              <span>{{ formatSize(image.size) }}</span>
              <span>{{ formatDate(image.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 列表视图 -->
      <el-table
        v-else-if="viewMode === 'list' && filteredImages.length > 0"
        :data="filteredImages"
        border
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        
        <el-table-column label="预览" width="100">
          <template #default="{ row }">
            <el-image
              :src="row.url"
              fit="cover"
              style="width: 60px; height: 60px; border-radius: 4px; cursor: pointer;"
              @click="openLightbox(row)"
            />
          </template>
        </el-table-column>

        <el-table-column prop="filename" label="文件名" min-width="200" show-overflow-tooltip />

        <el-table-column label="大小" width="120" sortable>
          <template #default="{ row }">
            {{ formatSize(row.size) }}
          </template>
        </el-table-column>

        <el-table-column label="创建时间" width="180" sortable>
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="URL" min-width="250">
          <template #default="{ row }">
            <div class="url-cell">
              <el-input
                :model-value="row.url"
                readonly
                size="small"
              >
                <template #append>
                  <el-button @click="copyUrl(row.url)">
                    <el-icon><CopyDocument /></el-icon>
                  </el-button>
                </template>
              </el-input>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button size="small" @click="previewImage(row)">
                <el-icon><View /></el-icon>
                预览
              </el-button>
              <el-button size="small" type="danger" @click="deleteImage(row)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty
        v-else-if="!loading"
        description="暂无图片"
        :image-size="120"
      >
        <el-button type="primary" @click="loadImages">
          <el-icon><Refresh /></el-icon>
          刷新列表
        </el-button>
      </el-empty>

      <!-- 分页 -->
      <el-pagination
        v-if="filteredImages.length > 0"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="totalImages"
        :page-sizes="[20, 50, 100, 200]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        style="margin-top: 20px; justify-content: center;"
      />
    </el-card>

    <!-- ✅ Lightbox图片预览对话框 -->
    <el-dialog
      v-model="showLightbox"
      :width="'80%'"
      :top="'5vh'"
      custom-class="lightbox-dialog"
      @close="closeLightbox"
    >
      <template #header>
        <div class="lightbox-header">
          <h3>{{ currentImage?.filename }}</h3>
          <div class="lightbox-actions">
            <el-button @click="prevImage" :disabled="currentImageIndex === 0">
              <el-icon><ArrowLeft /></el-icon>
              上一张
            </el-button>
            <span class="image-index">
              {{ currentImageIndex + 1 }} / {{ filteredImages.length }}
            </span>
            <el-button @click="nextImage" :disabled="currentImageIndex === filteredImages.length - 1">
              下一张
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>
      </template>

      <!-- 图片预览 -->
      <div class="lightbox-content">
        <el-image
          v-if="currentImage"
          :src="currentImage.url"
          fit="contain"
          class="lightbox-image"
        >
          <template #error>
            <div class="image-error-large">
              <el-icon :size="80"><Picture /></el-icon>
              <p>图片加载失败</p>
            </div>
          </template>
        </el-image>

        <!-- 图片详细信息 -->
        <div class="image-details">
          <h4>📋 图片详情</h4>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="文件名">
              {{ currentImage?.filename }}
            </el-descriptions-item>
            <el-descriptions-item label="文件大小">
              {{ formatSize(currentImage?.size) }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDateFull(currentImage?.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="图片尺寸">
              {{ currentImage?.width }} x {{ currentImage?.height }}
            </el-descriptions-item>
            <el-descriptions-item label="格式">
              {{ currentImage?.format || 'N/A' }}
            </el-descriptions-item>
            <el-descriptions-item label="访问次数">
              {{ currentImage?.access_count || 0 }} 次
            </el-descriptions-item>
          </el-descriptions>

          <div class="detail-actions">
            <el-button type="primary" @click="copyUrl(currentImage?.url)">
              <el-icon><CopyDocument /></el-icon>
              复制链接
            </el-button>
            <el-button @click="downloadImage(currentImage)">
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button type="danger" @click="deleteImage(currentImage)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Grid, List, Search, Refresh, Delete, View, CopyDocument, Download,
  Picture, Loading, Warning, ArrowLeft, ArrowRight, Select, Close
} from '@element-plus/icons-vue'
import api from '@/api'

// 视图模式
const viewMode = ref('grid')
const sortBy = ref('time_desc')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(50)

// 存储信息
const storageInfo = ref({
  total_gb: 0,
  used_gb: 0,
  available_gb: 0,
  usage_percent: 0,
  image_count: 0
})

// 图片列表
const images = ref([])
const selectedImages = ref([])
const loading = ref(false)
const cleanupLoading = ref(false)

// 清理设置
const cleanupDays = ref(7)
const estimatedSpace = ref(0)

// Lightbox
const showLightbox = ref(false)
const currentImage = ref(null)
const currentImageIndex = ref(0)

// 自动刷新定时器
let autoRefreshTimer = null

// 计算属性
const totalImages = computed(() => images.value.length)

const filteredImages = computed(() => {
  let result = images.value

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(img =>
      img.filename.toLowerCase().includes(keyword)
    )
  }

  // 排序
  result = [...result].sort((a, b) => {
    switch (sortBy.value) {
      case 'time_desc':
        return new Date(b.created_at) - new Date(a.created_at)
      case 'time_asc':
        return new Date(a.created_at) - new Date(b.created_at)
      case 'size_desc':
        return b.size - a.size
      case 'size_asc':
        return a.size - b.size
      case 'name_asc':
        return a.filename.localeCompare(b.filename)
      default:
        return 0
    }
  })

  return result
})

const usageColor = computed(() => {
  const usage = storageInfo.value.usage_percent
  if (usage < 50) return '#67C23A'  // 绿色
  if (usage < 80) return '#E6A23C'  // 黄色
  return '#F56C6C'  // 红色
})

const usageClass = computed(() => {
  const usage = storageInfo.value.usage_percent
  if (usage < 50) return 'usage-normal'
  if (usage < 80) return 'usage-warning'
  return 'usage-danger'
})

// 加载数据
const loadStorageInfo = async () => {
  try {
    const response = await api.get('/api/image-storage/info')
    if (response.data.success) {
      storageInfo.value = response.data.info
    }
  } catch (error) {
    console.error('加载存储信息失败:', error)
  }
}

const loadImages = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/image-storage/images', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    
    if (response.data.success) {
      images.value = response.data.images
    }
  } catch (error) {
    ElMessage.error('加载图片列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 清理操作
const cleanupByDays = async () => {
  ElMessageBox.confirm(
    `确定要删除 ${cleanupDays.value} 天前的所有图片吗？预估释放 ${estimatedSpace.value}MB 空间。`,
    '确认清理',
    {
      type: 'warning',
      confirmButtonText: '确定清理',
      cancelButtonText: '取消'
    }
  ).then(async () => {
    cleanupLoading.value = true
    try {
      const response = await api.post('/api/image-storage/cleanup', {
        days: cleanupDays.value
      })
      
      if (response.data.success) {
        ElMessage.success(`✅ 清理完成！删除了 ${response.data.deleted_count} 张图片，释放了 ${response.data.freed_space_mb}MB 空间`)
        await loadImages()
        await loadStorageInfo()
      }
    } catch (error) {
      ElMessage.error('清理失败: ' + error.message)
    } finally {
      cleanupLoading.value = false
    }
  })
}

const clearAllImages = async () => {
  ElMessageBox.confirm(
    '⚠️ 警告：此操作将删除所有缓存图片，且不可撤销！',
    '确认清空',
    {
      type: 'error',
      confirmButtonText: '确定清空',
      cancelButtonText: '取消',
      distinguishCancelAndClose: true
    }
  ).then(async () => {
    cleanupLoading.value = true
    try {
      const response = await api.post('/api/image-storage/clear-all')
      
      if (response.data.success) {
        ElMessage.success(`✅ 已清空所有图片！释放了 ${response.data.freed_space_mb}MB 空间`)
        await loadImages()
        await loadStorageInfo()
      }
    } catch (error) {
      ElMessage.error('清空失败: ' + error.message)
    } finally {
      cleanupLoading.value = false
    }
  })
}

// Lightbox操作
const openLightbox = (image) => {
  currentImage.value = image
  currentImageIndex.value = filteredImages.value.findIndex(img => img.filename === image.filename)
  showLightbox.value = true
}

const closeLightbox = () => {
  showLightbox.value = false
  currentImage.value = null
}

const prevImage = () => {
  if (currentImageIndex.value > 0) {
    currentImageIndex.value--
    currentImage.value = filteredImages.value[currentImageIndex.value]
  }
}

const nextImage = () => {
  if (currentImageIndex.value < filteredImages.value.length - 1) {
    currentImageIndex.value++
    currentImage.value = filteredImages.value[currentImageIndex.value]
  }
}

const previewImage = (image) => {
  openLightbox(image)
}

// 工具函数
const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

const formatDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  const now = new Date()
  const diff = now - d
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return d.toLocaleDateString()
}

const formatDateFull = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const truncateName = (name) => {
  if (name.length <= 20) return name
  return name.substring(0, 17) + '...'
}

const copyUrl = (url) => {
  navigator.clipboard.writeText(url).then(() => {
    ElMessage.success('URL已复制到剪贴板')
  })
}

const downloadImage = (image) => {
  const a = document.createElement('a')
  a.href = image.url
  a.download = image.filename
  a.click()
  ElMessage.success('下载已开始')
}

const deleteImage = async (image) => {
  ElMessageBox.confirm(
    `确定要删除图片 ${image.filename} 吗？`,
    '确认删除',
    {
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await api.delete(`/api/image-storage/image/${image.filename}`)
      if (response.data.success) {
        ElMessage.success('删除成功')
        await loadImages()
        await loadStorageInfo()
        
        // 如果Lightbox打开中，关闭或切换到下一张
        if (showLightbox.value) {
          if (filteredImages.value.length > 0) {
            nextImage()
          } else {
            closeLightbox()
          }
        }
      }
    } catch (error) {
      ElMessage.error('删除失败: ' + error.message)
    }
  })
}

// 批量操作
const selectAll = () => {
  selectedImages.value = filteredImages.value.map(img => img.filename)
}

const unselectAll = () => {
  selectedImages.value = []
}

const handleSelectionChange = (selection) => {
  selectedImages.value = selection.map(img => img.filename)
}

const deleteSelected = async () => {
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedImages.value.length} 张图片吗？`,
    '批量删除',
    {
      type: 'warning'
    }
  ).then(async () => {
    const promises = selectedImages.value.map(filename =>
      api.delete(`/api/image-storage/image/${filename}`)
    )
    
    try {
      await Promise.all(promises)
      ElMessage.success(`成功删除 ${selectedImages.value.length} 张图片`)
      selectedImages.value = []
      await loadImages()
      await loadStorageInfo()
    } catch (error) {
      ElMessage.error('批量删除失败: ' + error.message)
    }
  })
}

// 生命周期
onMounted(async () => {
  await loadStorageInfo()
  await loadImages()
  
  // 启动自动刷新（每30秒）
  autoRefreshTimer = setInterval(async () => {
    await loadStorageInfo()
  }, 30000)
})

onBeforeUnmount(() => {
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
  }
})
</script>

<style scoped lang="scss">
.image-storage-ultra {
  padding: 20px;
}

/* 顶部操作栏 */
.storage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  
  h1 {
    font-size: 28px;
    margin: 0;
  }
  
  .header-actions {
    display: flex;
    gap: 15px;
    align-items: center;
  }
}

/* 统计卡片 */
.stats-cards {
  margin-bottom: 30px;
}

.stat-card {
  padding: 25px;
  border-radius: 16px;
  color: white;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  }
  
  .stat-icon {
    font-size: 48px;
  }
  
  .stat-content {
    flex: 1;
    
    .stat-value {
      font-size: 32px;
      font-weight: 700;
      margin-bottom: 5px;
    }
    
    .stat-label {
      font-size: 14px;
      opacity: 0.9;
    }
  }
}

.gradient-blue {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.gradient-orange {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.gradient-green {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.gradient-purple {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

/* 使用率卡片 */
.usage-card {
  margin-bottom: 30px;
}

.usage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: 600;
  
  .usage-percentage {
    font-size: 24px;
    font-weight: 700;
    
    &.usage-normal {
      color: #67C23A;
    }
    
    &.usage-warning {
      color: #E6A23C;
    }
    
    &.usage-danger {
      color: #F56C6C;
    }
  }
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
}

.usage-tip {
  margin-top: 15px;
  padding: 12px;
  background: #FEF0F0;
  border-radius: 8px;
  color: #F56C6C;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 清理卡片 */
.cleanup-card {
  margin-bottom: 30px;
}

.cleanup-option {
  text-align: center;
  
  h4 {
    margin-bottom: 15px;
  }
  
  .cleanup-label {
    margin: 0 10px;
  }
  
  .estimate-text {
    margin: 15px 0;
    color: #67C23A;
  }
  
  .cleanup-warning {
    color: #F56C6C;
    font-size: 13px;
    margin-bottom: 15px;
  }
}

/* 网格视图 */
.grid-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.image-card {
  border: 2px solid #EBEEF5;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
  position: relative;
  
  &:hover {
    border-color: #409EFF;
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
    transform: translateY(-3px);
    
    .image-overlay {
      opacity: 1;
    }
  }
  
  &.is-selected {
    border-color: #409EFF;
    background: #ECF5FF;
  }
}

.image-checkbox {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10;
  
  :deep(.el-checkbox__label) {
    display: none;
  }
}

.image-thumbnail {
  position: relative;
  width: 100%;
  height: 200px;
  cursor: pointer;
  overflow: hidden;
  
  .el-image {
    width: 100%;
    height: 100%;
  }
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-info {
  padding: 12px;
  
  .image-name {
    font-weight: 600;
    margin-bottom: 8px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .image-meta {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #909399;
  }
}

/* Lightbox */
.lightbox-dialog {
  :deep(.el-dialog__body) {
    padding: 0;
  }
}

.lightbox-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  h3 {
    margin: 0;
  }
  
  .lightbox-actions {
    display: flex;
    gap: 10px;
    align-items: center;
    
    .image-index {
      color: #909399;
      font-size: 14px;
    }
  }
}

.lightbox-content {
  display: flex;
  gap: 30px;
  padding: 30px;
  
  .lightbox-image {
    flex: 2;
    max-height: 70vh;
    
    :deep(.el-image__inner) {
      max-height: 70vh;
    }
  }
  
  .image-details {
    flex: 1;
    
    h4 {
      margin-bottom: 20px;
    }
    
    .detail-actions {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-top: 20px;
    }
  }
}

.image-error-large {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
  
  p {
    margin-top: 15px;
  }
}
</style>
