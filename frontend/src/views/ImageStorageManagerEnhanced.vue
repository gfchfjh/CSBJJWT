<template>
  <div class="image-storage-manager-enhanced">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🖼️ 图床存储管理</span>
          <el-button @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <!-- 空间使用概览 -->
      <div class="storage-overview">
        <div class="stat-card">
          <div class="stat-icon">💿</div>
          <h3>总空间</h3>
          <div class="value">{{ formatSize(storageInfo.total_space) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <h3>已使用</h3>
          <div class="value">{{ formatSize(storageInfo.used_space) }}</div>
          <div class="sub-value">{{ storageInfo.usage_percent }}%</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">✨</div>
          <h3>剩余空间</h3>
          <div class="value">{{ formatSize(storageInfo.free_space) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🖼️</div>
          <h3>图片数量</h3>
          <div class="value">{{ storageInfo.image_count }}</div>
        </div>
      </div>

      <!-- 使用率进度条 -->
      <div class="usage-progress">
        <div class="progress-label">
          <span>存储空间使用率</span>
          <span class="progress-value">{{ storageInfo.usage_percent }}%</span>
        </div>
        <el-progress
          :percentage="storageInfo.usage_percent"
          :color="getProgressColor(storageInfo.usage_percent)"
          :stroke-width="26"
          :show-text="false"
        />
        <el-alert
          v-if="storageInfo.usage_percent > 80"
          type="warning"
          :closable="false"
          style="margin-top: 15px"
        >
          <template #title>
            ⚠️ 存储空间使用率较高
          </template>
          建议清理{{ cleanupDays }}天前的旧图片，预计可释放约{{ estimateCleanupSize() }}
        </el-alert>
      </div>

      <el-divider />

      <!-- 操作按钮组 -->
      <div class="action-buttons">
        <el-button-group>
          <el-button type="primary" @click="openStorageFolder">
            <el-icon><FolderOpened /></el-icon>
            打开存储文件夹
          </el-button>
          <el-button @click="showCleanupDialog = true">
            <el-icon><Delete /></el-icon>
            清理旧图片
          </el-button>
          <el-button type="danger" @click="clearAllImages">
            <el-icon><DeleteFilled /></el-icon>
            清空所有图片
          </el-button>
        </el-button-group>
      </div>

      <el-divider />

      <!-- 图片列表 -->
      <div class="image-gallery-section">
        <div class="gallery-header">
          <h3>最近图片（最多显示100张）</h3>
          <el-radio-group v-model="viewMode" size="small">
            <el-radio-button value="grid">
              <el-icon><Grid /></el-icon>
              网格
            </el-radio-button>
            <el-radio-button value="list">
              <el-icon><List /></el-icon>
              列表
            </el-radio-button>
          </el-radio-group>
        </div>

        <!-- 网格视图 -->
        <el-row v-if="viewMode === 'grid'" :gutter="15" class="image-grid">
          <el-col
            :span="4"
            v-for="image in images"
            :key="image.filename"
          >
            <el-card
              class="image-card"
              :body-style="{ padding: '0px' }"
              shadow="hover"
            >
              <div class="image-preview-container">
                <img
                  :src="image.url"
                  class="image-preview"
                  @click="previewImage(image)"
                  @error="handleImageError"
                />
                <div class="image-overlay">
                  <el-button-group>
                    <el-button size="small" @click="previewImage(image)">
                      <el-icon><ZoomIn /></el-icon>
                    </el-button>
                    <el-button size="small" type="danger" @click="deleteImage(image.filename)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-button-group>
                </div>
              </div>
              <div class="image-info">
                <p class="filename" :title="image.filename">{{ truncateFilename(image.filename) }}</p>
                <div class="image-meta">
                  <el-tag size="small">{{ formatSize(image.size) }}</el-tag>
                  <span class="date">{{ formatDate(image.created_at) }}</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 列表视图 -->
        <el-table v-else :data="images" border style="width: 100%">
          <el-table-column prop="filename" label="文件名" width="300">
            <template #default="{ row }">
              <div class="filename-cell">
                <el-image
                  :src="row.url"
                  fit="cover"
                  style="width: 40px; height: 40px; border-radius: 4px"
                  @click="previewImage(row)"
                />
                <span>{{ row.filename }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="size" label="大小" width="120">
            <template #default="{ row }">
              {{ formatSize(row.size) }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at, 'full') }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button size="small" @click="previewImage(row)">
                <el-icon><View /></el-icon>
                预览
              </el-button>
              <el-button size="small" type="danger" @click="deleteImage(row.filename)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-if="images.length === 0" description="暂无图片" />
      </div>
    </el-card>

    <!-- 清理对话框 -->
    <el-dialog
      v-model="showCleanupDialog"
      title="清理旧图片"
      width="500px"
    >
      <el-form label-width="100px">
        <el-form-item label="清理范围">
          <el-select v-model="cleanupDays" placeholder="选择天数">
            <el-option label="1天前的图片" :value="1" />
            <el-option label="3天前的图片" :value="3" />
            <el-option label="7天前的图片" :value="7" />
            <el-option label="15天前的图片" :value="15" />
            <el-option label="30天前的图片" :value="30" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-alert type="info" :closable="false">
            <template #title>
              预计可释放空间：{{ estimateCleanupSize() }}
            </template>
          </el-alert>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCleanupDialog = false">取消</el-button>
        <el-button type="primary" @click="cleanupOldImages">
          确认清理
        </el-button>
      </template>
    </el-dialog>

    <!-- 图片预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="图片预览"
      width="80%"
      append-to-body
    >
      <div class="preview-container">
        <img
          :src="previewImageData.url"
          style="width: 100%; max-height: 70vh; object-fit: contain"
        />
      </div>
      <div class="preview-info">
        <p><strong>文件名：</strong>{{ previewImageData.filename }}</p>
        <p><strong>大小：</strong>{{ formatSize(previewImageData.size) }}</p>
        <p><strong>创建时间：</strong>{{ formatDate(previewImageData.created_at, 'full') }}</p>
      </div>
      <template #footer>
        <el-button @click="copyImageUrl">
          <el-icon><CopyDocument /></el-icon>
          复制图片链接
        </el-button>
        <el-button type="danger" @click="deleteCurrentImage">
          <el-icon><Delete /></el-icon>
          删除此图片
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  FolderOpened,
  Delete,
  DeleteFilled,
  Grid,
  List,
  ZoomIn,
  View,
  CopyDocument
} from '@element-plus/icons-vue'
import api from '@/api'

// 数据
const storageInfo = ref({
  total_space: 0,
  used_space: 0,
  free_space: 0,
  usage_percent: 0,
  image_count: 0
})

const images = ref([])
const viewMode = ref('grid')
const cleanupDays = ref(7)
const showCleanupDialog = ref(false)
const previewDialogVisible = ref(false)
const previewImageData = ref({})

// 加载数据
async function loadStorageInfo() {
  try {
    const response = await api.get('/api/image-storage/info')
    storageInfo.value = response.data
    images.value = response.data.recent_images || []
  } catch (error) {
    ElMessage.error('加载存储信息失败: ' + error.message)
  }
}

// 刷新数据
function refreshData() {
  loadStorageInfo()
}

// 格式化大小
function formatSize(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

// 格式化日期
function formatDate(dateStr, format = 'relative') {
  if (!dateStr) return ''
  
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  
  if (format === 'full') {
    return date.toLocaleString('zh-CN')
  }
  
  // 相对时间
  const seconds = Math.floor(diff / 1000)
  if (seconds < 60) return `${seconds}秒前`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

// 截断文件名
function truncateFilename(filename, maxLength = 15) {
  if (filename.length <= maxLength) return filename
  return filename.substring(0, maxLength - 3) + '...'
}

// 进度条颜色
function getProgressColor(percentage) {
  if (percentage < 60) return '#67C23A'
  if (percentage < 80) return '#E6A23C'
  return '#F56C6C'
}

// 估算清理大小
function estimateCleanupSize() {
  // 简单估算，假设图片均匀分布
  if (!storageInfo.value.image_count) return '0 B'
  
  const avgSize = storageInfo.value.used_space / storageInfo.value.image_count
  const estimatedCount = Math.floor(storageInfo.value.image_count * (cleanupDays.value / 30))
  const estimatedSize = avgSize * estimatedCount
  
  return formatSize(estimatedSize)
}

// 打开存储文件夹
async function openStorageFolder() {
  try {
    await api.post('/api/image-storage/open-folder')
    ElMessage.success('已打开存储文件夹')
  } catch (error) {
    ElMessage.error('打开失败: ' + error.message)
  }
}

// 清理旧图片
async function cleanupOldImages() {
  try {
    const response = await api.post('/api/image-storage/cleanup', {
      days: cleanupDays.value
    })
    
    ElMessage.success(`清理完成！删除了${response.data.deleted_count}个文件，释放了${formatSize(response.data.freed_space)}`)
    showCleanupDialog.value = false
    loadStorageInfo()
  } catch (error) {
    ElMessage.error('清理失败: ' + error.message)
  }
}

// 清空所有图片
async function clearAllImages() {
  try {
    await ElMessageBox.confirm(
      '确定清空所有缓存图片吗？此操作不可恢复！',
      '危险操作',
      {
        type: 'error',
        confirmButtonText: '确定清空',
        cancelButtonText: '取消'
      }
    )
    
    const response = await api.post('/api/image-storage/cleanup', { days: 0 })
    ElMessage.success(`已清空！删除了${response.data.deleted_count}个文件`)
    loadStorageInfo()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败: ' + error.message)
    }
  }
}

// 预览图片
function previewImage(image) {
  previewImageData.value = image
  previewDialogVisible.value = true
}

// 删除图片
async function deleteImage(filename) {
  try {
    await ElMessageBox.confirm(`确定删除图片 ${filename} 吗？`, '确认删除', {
      type: 'warning'
    })
    
    await api.delete(`/api/image-storage/image/${filename}`)
    ElMessage.success('删除成功')
    loadStorageInfo()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

// 删除当前预览的图片
async function deleteCurrentImage() {
  await deleteImage(previewImageData.value.filename)
  previewDialogVisible.value = false
}

// 复制图片URL
function copyImageUrl() {
  navigator.clipboard.writeText(previewImageData.value.url).then(() => {
    ElMessage.success('图片链接已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

// 图片加载错误
function handleImageError(event) {
  event.target.src = '/placeholder-image.png'
}

// 初始化
onMounted(() => {
  loadStorageInfo()
  // 每30秒自动刷新
  setInterval(loadStorageInfo, 30000)
})
</script>

<style scoped>
.image-storage-manager-enhanced {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.storage-overview {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  flex: 1;
  text-align: center;
  padding: 25px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.stat-card h3 {
  margin: 10px 0;
  font-size: 14px;
  opacity: 0.9;
}

.stat-card .value {
  font-size: 28px;
  font-weight: bold;
  margin: 10px 0;
}

.stat-card .sub-value {
  font-size: 16px;
  opacity: 0.8;
}

.usage-progress {
  margin-bottom: 30px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 16px;
  font-weight: 500;
}

.progress-value {
  color: #409EFF;
  font-weight: bold;
}

.action-buttons {
  text-align: center;
  margin-bottom: 30px;
}

.gallery-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.gallery-header h3 {
  margin: 0;
  font-size: 18px;
}

.image-grid {
  margin-top: 20px;
}

.image-card {
  margin-bottom: 15px;
  overflow: hidden;
}

.image-preview-container {
  position: relative;
  height: 150px;
  overflow: hidden;
}

.image-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.3s;
}

.image-preview:hover {
  transform: scale(1.1);
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
  opacity: 0;
  transition: opacity 0.3s;
}

.image-preview-container:hover .image-overlay {
  opacity: 1;
}

.image-info {
  padding: 10px;
}

.filename {
  font-size: 12px;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.date {
  font-size: 11px;
  color: #999;
}

.filename-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.preview-container {
  text-align: center;
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
}

.preview-info {
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.preview-info p {
  margin: 5px 0;
  font-size: 14px;
}
</style>
