<template>
  <div class="image-storage-ultra">
    <!-- 统计卡片区 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card total-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="40" class="stat-icon"><FolderOpened /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.max_size_gb }}GB</div>
              <div class="stat-label">总空间</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card used-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="40" class="stat-icon"><PieChart /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_size_gb?.toFixed(2) }}GB</div>
              <div class="stat-label">已用</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card available-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="40" class="stat-icon"><Sunny /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ (stats.max_size_gb - (stats.total_size_gb || 0)).toFixed(2) }}GB</div>
              <div class="stat-label">可用</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card images-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="40" class="stat-icon"><Picture /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_images }}</div>
              <div class="stat-label">图片数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 动态进度条 -->
    <el-card class="progress-card" shadow="never">
      <el-progress
        :percentage="stats.usage_percentage || 0"
        :color="progressColor"
        :stroke-width="20"
        :format="formatProgress"
      />
    </el-card>
    
    <!-- 工具栏 -->
    <el-card class="toolbar-card" shadow="never">
      <div class="toolbar">
        <!-- 搜索框 -->
        <el-input
          v-model="searchQuery"
          placeholder="搜索图片文件名..."
          :prefix-icon="Search"
          clearable
          style="width: 300px"
          @input="handleSearch"
        />
        
        <!-- 排序选择 -->
        <el-select v-model="sortBy" placeholder="排序方式" style="width: 150px" @change="handleSort">
          <el-option label="时间排序" value="time" />
          <el-option label="大小排序" value="size" />
          <el-option label="名称排序" value="name" />
        </el-select>
        
        <!-- 视图切换 -->
        <el-radio-group v-model="viewMode" @change="handleViewChange">
          <el-radio-button value="grid">
            <el-icon><Grid /></el-icon>
            网格视图
          </el-radio-button>
          <el-radio-button value="list">
            <el-icon><List /></el-icon>
            列表视图
          </el-radio-button>
        </el-radio-group>
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button type="warning" :icon="Delete" @click="showCleanupDialog">
            智能清理
          </el-button>
          <el-button type="danger" :icon="Delete" @click="deleteSelected" :disabled="selectedImages.size === 0">
            删除选中 ({{ selectedImages.size }})
          </el-button>
          <el-button :icon="Refresh" @click="loadImages">刷新</el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 图片展示区 -->
    <el-card class="images-card" shadow="never" v-loading="loading">
      <!-- 网格视图 -->
      <div v-if="viewMode === 'grid'" class="grid-view">
        <div
          v-for="image in filteredImages"
          :key="image.id"
          class="image-item"
          :class="{ selected: selectedImages.has(image.id) }"
          @click="handleImageClick(image)"
        >
          <div class="image-wrapper">
            <el-image
              :src="image.url"
              fit="cover"
              class="image-thumbnail"
              lazy
            >
              <template #error>
                <div class="image-error">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
            
            <!-- 选择框 -->
            <el-checkbox
              v-model="selectedImages"
              :value="image.id"
              class="image-checkbox"
              @click.stop
            />
            
            <!-- 悬浮信息 -->
            <div class="image-overlay">
              <div class="image-info">
                <p class="image-name">{{ image.filename }}</p>
                <p class="image-size">{{ formatSize(image.size) }}</p>
              </div>
              <div class="image-actions">
                <el-button
                  type="primary"
                  size="small"
                  :icon="ZoomIn"
                  circle
                  @click.stop="openLightbox(image)"
                />
                <el-button
                  type="danger"
                  size="small"
                  :icon="Delete"
                  circle
                  @click.stop="deleteImage(image.id)"
                />
              </div>
            </div>
          </div>
        </div>
        
        <!-- 空状态 -->
        <el-empty v-if="filteredImages.length === 0" description="暂无图片" />
      </div>
      
      <!-- 列表视图 -->
      <el-table v-else :data="filteredImages" stripe @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column label="预览" width="80">
          <template #default="{ row }">
            <el-image
              :src="row.url"
              fit="cover"
              style="width: 50px; height: 50px; border-radius: 4px; cursor: pointer"
              @click="openLightbox(row)"
            >
              <template #error>
                <div style="display: flex; align-items: center; justify-content: center; height: 100%">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
          </template>
        </el-table-column>
        <el-table-column prop="filename" label="文件名" show-overflow-tooltip />
        <el-table-column label="大小" width="120">
          <template #default="{ row }">{{ formatSize(row.size) }}</template>
        </el-table-column>
        <el-table-column label="上传时间" width="180">
          <template #default="{ row }">{{ formatDate(row.upload_time) }}</template>
        </el-table-column>
        <el-table-column label="最后访问" width="180">
          <template #default="{ row }">{{ formatDate(row.last_access) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :icon="ZoomIn"
              @click="openLightbox(row)"
            >
              预览
            </el-button>
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click="deleteImage(row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-if="filteredImages.length > 0"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="filteredImages.length"
        :page-sizes="[20, 50, 100, 200]"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
      />
    </el-card>
    
    <!-- Lightbox 大图预览 -->
    <el-dialog
      v-model="lightboxVisible"
      :title="currentImage?.filename"
      width="80%"
      destroy-on-close
      class="lightbox-dialog"
    >
      <div class="lightbox-content">
        <el-image
          :src="currentImage?.url"
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
      </div>
      
      <template #footer>
        <div class="lightbox-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="文件名">{{ currentImage?.filename }}</el-descriptions-item>
            <el-descriptions-item label="大小">{{ formatSize(currentImage?.size) }}</el-descriptions-item>
            <el-descriptions-item label="上传时间">{{ formatDate(currentImage?.upload_time) }}</el-descriptions-item>
            <el-descriptions-item label="最后访问">{{ formatDate(currentImage?.last_access) }}</el-descriptions-item>
            <el-descriptions-item label="URL" :span="2">
              <el-input :value="currentImage?.url" readonly>
                <template #append>
                  <el-button :icon="CopyDocument" @click="copyUrl(currentImage?.url)">复制</el-button>
                </template>
              </el-input>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </template>
    </el-dialog>
    
    <!-- 智能清理对话框 -->
    <el-dialog v-model="cleanupDialogVisible" title="智能清理" width="500px">
      <el-form :model="cleanupForm" label-width="120px">
        <el-form-item label="清理策略">
          <el-radio-group v-model="cleanupForm.strategy">
            <el-radio value="days">按天数清理</el-radio>
            <el-radio value="all">清空全部</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item v-if="cleanupForm.strategy === 'days'" label="保留天数">
          <el-input-number v-model="cleanupForm.days" :min="1" :max="365" />
          <span class="form-hint">将删除 {{ cleanupForm.days }} 天前的图片</span>
        </el-form-item>
        
        <el-form-item>
          <el-alert type="warning" :closable="false" show-icon>
            <template #title>
              <span v-if="cleanupForm.strategy === 'days'">
                即将删除 {{ cleanupForm.days }} 天前的所有图片，此操作不可恢复！
              </span>
              <span v-else>
                即将清空所有图片，此操作不可恢复！
              </span>
            </template>
          </el-alert>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="cleanupDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="performCleanup" :loading="cleaning">
          确认清理
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  FolderOpened,
  PieChart,
  Sunny,
  Picture,
  Search,
  Grid,
  List,
  Delete,
  Refresh,
  ZoomIn,
  CopyDocument
} from '@element-plus/icons-vue'
import api from '@/api'

// 状态
const loading = ref(false)
const viewMode = ref('grid')
const searchQuery = ref('')
const sortBy = ref('time')
const images = ref([])
const stats = ref({
  total_images: 0,
  total_size: 0,
  total_size_mb: 0,
  total_size_gb: 0,
  max_size_gb: 10,
  usage_percentage: 0
})

const selectedImages = ref(new Set())
const currentPage = ref(1)
const pageSize = ref(20)

// Lightbox
const lightboxVisible = ref(false)
const currentImage = ref(null)

// 清理对话框
const cleanupDialogVisible = ref(false)
const cleaning = ref(false)
const cleanupForm = ref({
  strategy: 'days',
  days: 7
})

// 计算属性
const progressColor = computed(() => {
  const percentage = stats.value.usage_percentage || 0
  if (percentage >= 90) return '#F56C6C'
  if (percentage >= 70) return '#E6A23C'
  return '#67C23A'
})

const filteredImages = computed(() => {
  let result = [...images.value]
  
  // 搜索过滤
  if (searchQuery.value) {
    result = result.filter(img =>
      img.filename.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }
  
  // 排序
  result.sort((a, b) => {
    if (sortBy.value === 'time') {
      return b.upload_time - a.upload_time
    } else if (sortBy.value === 'size') {
      return b.size - a.size
    } else if (sortBy.value === 'name') {
      return a.filename.localeCompare(b.filename)
    }
    return 0
  })
  
  return result
})

// 方法
const loadImages = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/image-storage/list')
    images.value = response.data.images
    stats.value = response.data.stats
  } catch (error) {
    console.error('加载图片列表失败:', error)
    ElMessage.error('加载图片列表失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleSort = () => {
  currentPage.value = 1
}

const handleViewChange = () => {
  selectedImages.value.clear()
}

const handleImageClick = (image) => {
  if (selectedImages.value.has(image.id)) {
    selectedImages.value.delete(image.id)
  } else {
    selectedImages.value.add(image.id)
  }
}

const handleSelectionChange = (selection) => {
  selectedImages.value = new Set(selection.map(item => item.id))
}

const openLightbox = (image) => {
  currentImage.value = image
  lightboxVisible.value = true
}

const deleteImage = async (imageId) => {
  try {
    await ElMessageBox.confirm('确定要删除这张图片吗？', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.delete(`/api/image-storage/delete`, {
      data: { image_ids: [imageId] }
    })
    
    ElMessage.success('删除成功')
    await loadImages()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

const deleteSelected = async () => {
  if (selectedImages.value.size === 0) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedImages.value.size} 张图片吗？`,
      '批量删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.delete('/api/image-storage/delete', {
      data: { image_ids: Array.from(selectedImages.value) }
    })
    
    ElMessage.success('批量删除成功')
    selectedImages.value.clear()
    await loadImages()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

const showCleanupDialog = () => {
  cleanupDialogVisible.value = true
}

const performCleanup = async () => {
  cleaning.value = true
  
  try {
    await api.post('/api/image-storage/cleanup', cleanupForm.value)
    
    ElMessage.success('清理完成')
    cleanupDialogVisible.value = false
    await loadImages()
  } catch (error) {
    console.error('清理失败:', error)
    ElMessage.error('清理失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    cleaning.value = false
  }
}

const copyUrl = (url) => {
  navigator.clipboard.writeText(url)
  ElMessage.success('URL已复制到剪贴板')
}

const formatProgress = (percentage) => {
  return `${percentage.toFixed(1)}% 已使用`
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
}

const formatDate = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadImages()
})
</script>

<style scoped>
.image-storage-ultra {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 12px;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.total-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.used-card {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.available-card {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.images-card {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  opacity: 0.8;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.progress-card {
  margin-bottom: 20px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.action-buttons {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

.images-card {
  margin-top: 20px;
  min-height: 400px;
}

/* 网格视图 */
.grid-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 20px;
}

.image-item {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.image-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.image-item.selected {
  outline: 3px solid #409eff;
}

.image-wrapper {
  position: relative;
  width: 100%;
  padding-top: 100%; /* 1:1 比例 */
}

.image-thumbnail {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.image-checkbox {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 2;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 15px;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-item:hover .image-overlay {
  opacity: 1;
}

.image-info {
  color: white;
}

.image-name {
  font-size: 14px;
  margin: 0 0 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.image-size {
  font-size: 12px;
  margin: 0;
  opacity: 0.8;
}

.image-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.image-error {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
}

/* Lightbox */
.lightbox-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.lightbox-content {
  height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000;
}

.lightbox-image {
  max-width: 100%;
  max-height: 100%;
}

.image-error-large {
  text-align: center;
  color: #909399;
}

.lightbox-info {
  padding: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: center;
}

.form-hint {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

/* 暗黑模式 */
.dark .stat-card {
  color: white;
}

.dark .image-error {
  background: #2c2c2c;
}
</style>
