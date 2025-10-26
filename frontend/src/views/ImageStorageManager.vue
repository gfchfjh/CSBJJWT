<template>
  <div class="image-storage-manager">
    <!-- ✅ P0-3深度优化：图床管理界面 -->
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🖼️ 图床存储管理</span>
          <el-button type="primary" @click="loadStorageInfo" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <!-- 存储空间概览 -->
      <div class="storage-overview">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="已用空间" :value="storageInfo.used_gb" suffix="GB" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="总空间" :value="storageInfo.max_gb" suffix="GB" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="图片数量" :value="storageInfo.image_count" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="使用率" :value="storageInfo.usage_percentage" suffix="%" />
          </el-col>
        </el-row>
        
        <el-progress 
          :percentage="storageInfo.usage_percentage" 
          :status="getProgressStatus(storageInfo.usage_percentage)"
          :stroke-width="24"
          :text-inside="true"
          style="margin-top: 20px"
        />
      </div>
      
      <el-divider />
      
      <!-- 存储路径设置 -->
      <el-form label-width="120px">
        <el-form-item label="存储路径">
          <el-input 
            v-model="storageInfo.storage_path" 
            readonly
            style="width: 500px"
          >
            <template #append>
              <el-button @click="openStorageFolder" :loading="openingFolder">
                <el-icon><Folder /></el-icon>
                打开文件夹
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="自动清理">
          <el-input-number 
            v-model="storageInfo.auto_clean_days" 
            :min="1" 
            :max="30"
            :disabled="true"
          />
          <span style="margin-left: 10px">天前的图片</span>
          <el-tooltip content="自动清理功能由后端定时任务执行" placement="top">
            <el-icon style="margin-left: 10px; color: #909399;">
              <QuestionFilled />
            </el-icon>
          </el-tooltip>
        </el-form-item>
      </el-form>
      
      <el-divider />
      
      <!-- 手动清理 -->
      <div class="manual-cleanup">
        <h3>🧹 手动清理</h3>
        <div class="cleanup-buttons">
          <el-input-number 
            v-model="cleanupDays" 
            :min="1" 
            :max="30"
            style="margin-right: 10px"
          />
          <el-button 
            type="danger" 
            @click="cleanupOldImages"
            :loading="cleaning"
          >
            <el-icon><Delete /></el-icon>
            清理 {{ cleanupDays }} 天前的图片
          </el-button>
          
          <el-button 
            type="warning" 
            @click="cleanupAllImages"
            :disabled="cleaning"
          >
            <el-icon><Warning /></el-icon>
            清空所有图片
          </el-button>
        </div>
      </div>
      
      <el-divider />
      
      <!-- 图片列表 -->
      <h3>📸 最近上传的图片</h3>
      <el-table 
        :data="storageInfo.recent_images" 
        max-height="500"
        v-loading="loading"
      >
        <el-table-column prop="filename" label="文件名" min-width="200">
          <template #default="{ row }">
            <el-tooltip :content="row.filename" placement="top">
              <span class="filename-text">{{ row.filename }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        
        <el-table-column prop="size" label="大小" width="120" />
        
        <el-table-column prop="upload_time" label="上传时间" width="180" />
        
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button 
              size="small" 
              @click="previewImage(row)"
              link
            >
              <el-icon><View /></el-icon>
              预览
            </el-button>
            <el-button 
              size="small" 
              type="danger"
              @click="deleteImage(row)"
              link
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 图片预览对话框 -->
    <el-dialog
      v-model="previewVisible"
      title="图片预览"
      width="60%"
      center
    >
      <div class="preview-container">
        <img :src="previewImageUrl" alt="预览" class="preview-image" />
      </div>
      <template #footer>
        <el-button @click="previewVisible = false">关闭</el-button>
        <el-button type="danger" @click="deleteCurrentPreviewImage">
          删除此图片
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Folder,
  Delete,
  Warning,
  QuestionFilled,
  View
} from '@element-plus/icons-vue'
import api from '@/api'

const loading = ref(false)
const cleaning = ref(false)
const openingFolder = ref(false)
const cleanupDays = ref(7)

const storageInfo = ref({
  used_gb: 0,
  max_gb: 10,
  image_count: 0,
  storage_path: '',
  auto_clean_days: 7,
  recent_images: [],
  usage_percentage: 0
})

const previewVisible = ref(false)
const previewImageUrl = ref('')
const currentPreviewImage = ref(null)

// 获取存储信息
const loadStorageInfo = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/image-storage/info')
    storageInfo.value = response
  } catch (error) {
    ElMessage.error('加载失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 获取进度条状态
const getProgressStatus = (percentage) => {
  if (percentage < 60) return 'success'
  if (percentage < 80) return 'warning'
  return 'exception'
}

// 打开存储文件夹
const openStorageFolder = async () => {
  openingFolder.value = true
  try {
    const response = await api.post('/api/image-storage/open-folder')
    ElMessage.success('已打开文件夹')
  } catch (error) {
    ElMessage.error('打开失败：' + (error.response?.data?.detail || error.message))
  } finally {
    openingFolder.value = false
  }
}

// 清理旧图片
const cleanupOldImages = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要清理 ${cleanupDays.value} 天前的图片吗？此操作不可恢复！`,
      '确认清理',
      {
        confirmButtonText: '确定清理',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    cleaning.value = true
    
    const response = await api.post(`/api/image-storage/cleanup?days=${cleanupDays.value}`)
    
    ElMessage.success({
      message: `已清理 ${response.deleted_count} 个文件，释放 ${response.freed_mb}MB 空间`,
      duration: 5000
    })
    
    // 刷新信息
    await loadStorageInfo()
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清理失败：' + (error.response?.data?.detail || error.message))
    }
  } finally {
    cleaning.value = false
  }
}

// 清空所有图片
const cleanupAllImages = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有图片吗？此操作不可恢复！将删除所有缓存的图片文件。',
      '⚠️ 危险操作',
      {
        confirmButtonText: '确定清空',
        cancelButtonText: '取消',
        type: 'error',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    // 再次确认
    await ElMessageBox.confirm(
      '这是最后的确认。点击确定后将立即删除所有图片！',
      '⚠️ 最后确认',
      {
        confirmButtonText: '立即删除',
        cancelButtonText: '我再想想',
        type: 'error'
      }
    )
    
    cleaning.value = true
    
    const response = await api.post('/api/image-storage/cleanup-all')
    
    ElMessage.success({
      message: `已清空 ${response.deleted_count} 个文件，释放 ${response.freed_gb}GB 空间`,
      duration: 5000
    })
    
    // 刷新信息
    await loadStorageInfo()
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败：' + (error.response?.data?.detail || error.message))
    }
  } finally {
    cleaning.value = false
  }
}

// 预览图片
const previewImage = (row) => {
  // 构建图片URL
  // 注意：这里需要根据实际的图床服务地址调整
  previewImageUrl.value = `/api/images/${row.filename}`
  currentPreviewImage.value = row
  previewVisible.value = true
}

// 删除图片
const deleteImage = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除图片 "${row.filename}" 吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.delete(`/api/image-storage/image/${row.filename}`)
    
    ElMessage.success('图片已删除')
    
    // 刷新列表
    await loadStorageInfo()
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.detail || error.message))
    }
  }
}

// 删除当前预览的图片
const deleteCurrentPreviewImage = async () => {
  if (currentPreviewImage.value) {
    previewVisible.value = false
    await deleteImage(currentPreviewImage.value)
  }
}

onMounted(() => {
  loadStorageInfo()
})
</script>

<style scoped>
.image-storage-manager {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.storage-overview {
  margin-bottom: 20px;
}

.manual-cleanup {
  margin: 20px 0;
}

.manual-cleanup h3 {
  margin-bottom: 15px;
  color: #303133;
}

.cleanup-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filename-text {
  display: inline-block;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background: #f5f7fa;
  border-radius: 4px;
}

.preview-image {
  max-width: 100%;
  max-height: 600px;
  object-fit: contain;
}
</style>
