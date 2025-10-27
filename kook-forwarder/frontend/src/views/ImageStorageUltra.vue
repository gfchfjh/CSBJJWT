<template>
  <div class="image-storage-ultra">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>🖼️ 图床存储管理</h1>
      <div class="header-actions">
        <el-button @click="refreshData" :loading="loading">
          <el-icon><RefreshRight /></el-icon>
          刷新数据
        </el-button>
        <el-button type="danger" @click="showCleanupDialog">
          <el-icon><Delete /></el-icon>
          清理旧图片
        </el-button>
      </div>
    </div>

    <!-- 统计卡片区域 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <div class="stat-card total-card">
          <div class="card-icon">
            <el-icon :size="48"><FolderOpened /></el-icon>
          </div>
          <div class="card-content">
            <h3>{{ stats.total_space_gb }} GB</h3>
            <p>总空间</p>
          </div>
          <div class="card-decoration"></div>
        </div>
      </el-col>

      <el-col :span="6">
        <div class="stat-card used-card">
          <div class="card-icon">
            <el-icon :size="48"><PieChart /></el-icon>
          </div>
          <div class="card-content">
            <h3>{{ stats.used_space_gb }} GB</h3>
            <p>已使用</p>
            <el-progress
              :percentage="usagePercentage"
              :color="progressColor"
              :show-text="false"
              :stroke-width="6"
              class="mini-progress"
            />
          </div>
          <div class="card-decoration"></div>
        </div>
      </el-col>

      <el-col :span="6">
        <div class="stat-card available-card">
          <div class="card-icon">
            <el-icon :size="48"><Box /></el-icon>
          </div>
          <div class="card-content">
            <h3>{{ stats.available_space_gb }} GB</h3>
            <p>剩余空间</p>
          </div>
          <div class="card-decoration"></div>
        </div>
      </el-col>

      <el-col :span="6">
        <div class="stat-card count-card">
          <div class="card-icon">
            <el-icon :size="48"><Picture /></el-icon>
          </div>
          <div class="card-content">
            <h3>{{ stats.total_images }}</h3>
            <p>图片数量</p>
          </div>
          <div class="card-decoration"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 使用率进度条 -->
    <el-card class="usage-card">
      <template #header>
        <span>📊 存储使用率</span>
      </template>
      <div class="usage-bar-container">
        <el-progress
          :percentage="usagePercentage"
          :color="progressColors"
          :stroke-width="20"
        >
          <template #default="{ percentage }">
            <span class="percentage-text">{{ percentage }}%</span>
          </template>
        </el-progress>
        <div class="usage-info">
          <span>{{ stats.used_space_gb }} GB / {{ stats.total_space_gb }} GB</span>
          <el-tag v-if="usagePercentage < 50" type="success">空间充足</el-tag>
          <el-tag v-else-if="usagePercentage < 80" type="warning">建议清理</el-tag>
          <el-tag v-else type="danger">空间不足</el-tag>
        </div>
      </div>
    </el-card>

    <!-- 图片列表 -->
    <el-card class="images-card">
      <template #header>
        <div class="images-header">
          <span>🖼️ 图片列表</span>
          <div class="view-switcher">
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button label="grid">
                <el-icon><Grid /></el-icon>
                网格视图
              </el-radio-button>
              <el-radio-button label="list">
                <el-icon><List /></el-icon>
                列表视图
              </el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>

      <!-- 筛选工具栏 -->
      <div class="filter-toolbar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索图片文件名..."
          clearable
          style="width: 300px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-model="sortBy"
          placeholder="排序方式"
          style="width: 150px"
        >
          <el-option label="最新上传" value="time_desc" />
          <el-option label="最早上传" value="time_asc" />
          <el-option label="文件最大" value="size_desc" />
          <el-option label="文件最小" value="size_asc" />
        </el-select>

        <span class="filter-info">
          显示 {{ filteredImages.length }} / {{ images.length }} 张图片
        </span>
      </div>

      <!-- 网格视图 -->
      <div v-if="viewMode === 'grid'" class="grid-view">
        <div
          v-for="image in paginatedImages"
          :key="image.filename"
          class="image-card"
          @click="previewImage(image)"
        >
          <div class="image-thumbnail">
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
                  <el-icon><PictureFilled /></el-icon>
                </div>
              </template>
            </el-image>
            <div class="image-overlay">
              <el-button
                circle
                type="primary"
                @click.stop="previewImage(image)"
              >
                <el-icon><ZoomIn /></el-icon>
              </el-button>
              <el-button
                circle
                type="success"
                @click.stop="copyImageUrl(image)"
              >
                <el-icon><CopyDocument /></el-icon>
              </el-button>
              <el-button
                circle
                type="danger"
                @click.stop="deleteImage(image)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
          <div class="image-info">
            <div class="image-name" :title="image.filename">
              {{ image.filename }}
            </div>
            <div class="image-meta">
              <span>{{ formatFileSize(image.size) }}</span>
              <span>{{ formatDate(image.upload_time) }}</span>
            </div>
          </div>
        </div>

        <el-empty
          v-if="filteredImages.length === 0"
          description="暂无图片"
          :image-size="120"
        />
      </div>

      <!-- 列表视图 -->
      <div v-else class="list-view">
        <el-table
          :data="paginatedImages"
          stripe
          style="width: 100%"
        >
          <el-table-column label="预览" width="100">
            <template #default="{ row }">
              <el-image
                :src="row.url"
                fit="cover"
                style="width: 60px; height: 60px; border-radius: 4px; cursor: pointer"
                @click="previewImage(row)"
              />
            </template>
          </el-table-column>

          <el-table-column
            prop="filename"
            label="文件名"
            min-width="200"
            show-overflow-tooltip
          />

          <el-table-column
            label="大小"
            width="100"
          >
            <template #default="{ row }">
              {{ formatFileSize(row.size) }}
            </template>
          </el-table-column>

          <el-table-column
            label="上传时间"
            width="180"
          >
            <template #default="{ row }">
              {{ formatDateTime(row.upload_time) }}
            </template>
          </el-table-column>

          <el-table-column
            label="操作"
            width="200"
            fixed="right"
          >
            <template #default="{ row }">
              <el-button
                size="small"
                type="primary"
                text
                @click="previewImage(row)"
              >
                <el-icon><View /></el-icon>
                预览
              </el-button>
              <el-button
                size="small"
                type="success"
                text
                @click="copyImageUrl(row)"
              >
                <el-icon><CopyDocument /></el-icon>
                复制链接
              </el-button>
              <el-button
                size="small"
                type="danger"
                text
                @click="deleteImage(row)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty
          v-if="filteredImages.length === 0"
          description="暂无图片"
        />
      </div>

      <!-- 分页 -->
      <div v-if="filteredImages.length > 0" class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[12, 24, 48, 96]"
          :total="filteredImages.length"
          layout="total, sizes, prev, pager, next, jumper"
          background
        />
      </div>
    </el-card>

    <!-- 图片预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="图片预览"
      width="80%"
      top="5vh"
    >
      <div class="preview-container">
        <el-image
          :src="previewImageData?.url"
          fit="contain"
          style="width: 100%; max-height: 70vh"
        />
        <div class="preview-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="文件名">
              {{ previewImageData?.filename }}
            </el-descriptions-item>
            <el-descriptions-item label="文件大小">
              {{ formatFileSize(previewImageData?.size) }}
            </el-descriptions-item>
            <el-descriptions-item label="上传时间">
              {{ formatDateTime(previewImageData?.upload_time) }}
            </el-descriptions-item>
            <el-descriptions-item label="图片链接">
              <el-input
                :value="previewImageData?.url"
                readonly
                size="small"
              >
                <template #append>
                  <el-button @click="copyImageUrl(previewImageData)">
                    <el-icon><CopyDocument /></el-icon>
                  </el-button>
                </template>
              </el-input>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>

    <!-- 清理对话框 -->
    <el-dialog
      v-model="cleanupDialogVisible"
      title="清理旧图片"
      width="500px"
    >
      <el-form label-width="120px">
        <el-form-item label="清理策略">
          <el-radio-group v-model="cleanupStrategy">
            <el-radio label="by_days">按天数清理</el-radio>
            <el-radio label="all">清空所有</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item
          v-if="cleanupStrategy === 'by_days'"
          label="清理天数"
        >
          <el-input-number
            v-model="cleanupDays"
            :min="1"
            :max="365"
          />
          <span style="margin-left: 10px">天前的图片</span>
        </el-form-item>

        <el-alert
          :title="cleanupEstimate"
          type="warning"
          :closable="false"
          show-icon
        />
      </el-form>

      <template #footer>
        <el-button @click="cleanupDialogVisible = false">取消</el-button>
        <el-button
          type="danger"
          :loading="cleaning"
          @click="executeCleanup"
        >
          确认清理
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

// 状态
const loading = ref(false)
const stats = ref({
  total_space_gb: 10,
  used_space_gb: 2.3,
  available_space_gb: 7.7,
  total_images: 1234
})

const images = ref([])
const viewMode = ref('grid') // grid | list
const searchKeyword = ref('')
const sortBy = ref('time_desc')
const currentPage = ref(1)
const pageSize = ref(24)

const previewDialogVisible = ref(false)
const previewImageData = ref(null)

const cleanupDialogVisible = ref(false)
const cleanupStrategy = ref('by_days')
const cleanupDays = ref(7)
const cleaning = ref(false)

// 使用率百分比
const usagePercentage = computed(() => {
  if (stats.value.total_space_gb === 0) return 0
  return Math.min(
    Math.round((stats.value.used_space_gb / stats.value.total_space_gb) * 100),
    100
  )
})

// 进度条颜色
const progressColor = computed(() => {
  const percentage = usagePercentage.value
  if (percentage < 50) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
})

// 进度条颜色数组（渐变）
const progressColors = [
  { color: '#67c23a', percentage: 50 },
  { color: '#e6a23c', percentage: 80 },
  { color: '#f56c6c', percentage: 100 }
]

// 筛选后的图片
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
        return new Date(b.upload_time) - new Date(a.upload_time)
      case 'time_asc':
        return new Date(a.upload_time) - new Date(b.upload_time)
      case 'size_desc':
        return b.size - a.size
      case 'size_asc':
        return a.size - b.size
      default:
        return 0
    }
  })

  return result
})

// 分页后的图片
const paginatedImages = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredImages.value.slice(start, end)
})

// 清理估算
const cleanupEstimate = computed(() => {
  if (cleanupStrategy.value === 'all') {
    return `将删除所有 ${stats.value.total_images} 张图片，释放 ${stats.value.used_space_gb} GB 空间`
  } else {
    const cutoffDate = new Date()
    cutoffDate.setDate(cutoffDate.getDate() - cleanupDays.value)
    const oldImages = images.value.filter(
      img => new Date(img.upload_time) < cutoffDate
    )
    const totalSize = oldImages.reduce((sum, img) => sum + img.size, 0)
    const sizeGB = (totalSize / (1024 * 1024 * 1024)).toFixed(2)
    return `将删除 ${oldImages.length} 张图片（${cleanupDays.value}天前），预计释放 ${sizeGB} GB 空间`
  }
})

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    
    // 获取统计信息
    const statsRes = await api.get('/api/image-storage-manager/info')
    if (statsRes.success) {
      stats.value = {
        total_space_gb: statsRes.max_size_gb || 10,
        used_space_gb: statsRes.used_gb || 0,
        available_space_gb: (statsRes.max_size_gb || 10) - (statsRes.used_gb || 0),
        total_images: statsRes.total_images || 0
      }
    }

    // 获取图片列表
    const imagesRes = await api.get('/api/image-storage-manager/images')
    if (imagesRes.success) {
      images.value = imagesRes.images || []
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = () => {
  loadData()
}

// 预览图片
const previewImage = (image) => {
  previewImageData.value = image
  previewDialogVisible.value = true
}

// 复制图片链接
const copyImageUrl = async (image) => {
  try {
    await navigator.clipboard.writeText(image.url)
    ElMessage.success('图片链接已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 删除图片
const deleteImage = async (image) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除图片"${image.filename}"吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await api.delete(`/api/image-storage-manager/image/${image.filename}`)
    
    if (response.success) {
      ElMessage.success('删除成功')
      await loadData()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.detail || error.message))
    }
  }
}

// 显示清理对话框
const showCleanupDialog = () => {
  cleanupDialogVisible.value = true
}

// 执行清理
const executeCleanup = async () => {
  try {
    cleaning.value = true

    const response = await api.post('/api/image-storage-manager/cleanup', {
      strategy: cleanupStrategy.value,
      days: cleanupStrategy.value === 'by_days' ? cleanupDays.value : null
    })

    if (response.success) {
      ElMessage.success(
        `清理完成！删除了 ${response.deleted_count} 张图片，释放 ${response.freed_space_gb} GB 空间`
      )
      cleanupDialogVisible.value = false
      await loadData()
    }
  } catch (error) {
    ElMessage.error('清理失败：' + (error.response?.data?.detail || error.message))
  } finally {
    cleaning.value = false
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 格式化日期（相对时间）
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  if (days < 30) return `${Math.floor(days / 7)}周前`
  if (days < 365) return `${Math.floor(days / 30)}个月前`
  return `${Math.floor(days / 365)}年前`
}

// 格式化日期时间（完整）
const formatDateTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.image-storage-ultra {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 统计卡片 */
.stats-cards {
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  padding: 24px;
  border-radius: 16px;
  color: white;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.total-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.used-card {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.available-card {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.count-card {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.card-icon {
  opacity: 0.9;
}

.card-content {
  flex: 1;
}

.card-content h3 {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 4px 0;
}

.card-content p {
  font-size: 14px;
  margin: 0;
  opacity: 0.9;
}

.mini-progress {
  margin-top: 8px;
}

.card-decoration {
  position: absolute;
  right: -20px;
  bottom: -20px;
  width: 120px;
  height: 120px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}

/* 使用率卡片 */
.usage-card {
  margin-bottom: 24px;
}

.usage-bar-container {
  padding: 20px 0;
}

.percentage-text {
  font-size: 14px;
  font-weight: 600;
}

.usage-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  font-size: 14px;
  color: #606266;
}

/* 图片列表 */
.images-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-info {
  margin-left: auto;
  font-size: 14px;
  color: #909399;
}

/* 网格视图 */
.grid-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  min-height: 400px;
}

.image-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
  cursor: pointer;
  background: white;
}

.image-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
  transform: translateY(-4px);
}

.image-thumbnail {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: #f5f7fa;
}

.image-thumbnail .el-image {
  width: 100%;
  height: 100%;
}

.image-loading,
.image-error {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: #c0c4cc;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-card:hover .image-overlay {
  opacity: 1;
}

.image-info {
  padding: 12px;
}

.image-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

/* 列表视图 */
.list-view {
  min-height: 400px;
}

/* 分页 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e4e7ed;
}

/* 预览 */
.preview-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.preview-info {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}
</style>
