<template>
  <div class="message-search">
    <!-- ✅ P1-1深度优化：消息搜索组件 -->
    
    <el-card>
      <template #header>
        <span>🔍 消息搜索</span>
      </template>
      
      <!-- 搜索表单 -->
      <el-form :model="searchForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="关键词">
              <el-input
                v-model="searchForm.keyword"
                placeholder="搜索消息内容、发送者、频道..."
                clearable
                @keyup.enter="search"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          
          <el-col :span="6">
            <el-form-item label="平台">
              <el-select v-model="searchForm.platform" clearable placeholder="全部">
                <el-option label="Discord" value="discord" />
                <el-option label="Telegram" value="telegram" />
                <el-option label="飞书" value="feishu" />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="6">
            <el-form-item label="状态">
              <el-select v-model="searchForm.status" clearable placeholder="全部">
                <el-option label="成功" value="success" />
                <el-option label="失败" value="failed" />
                <el-option label="待处理" value="pending" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="时间范围">
              <el-date-picker
                v-model="dateRange"
                type="datetimerange"
                range-separator="至"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="6">
            <el-form-item label="发送者">
              <el-input 
                v-model="searchForm.sender" 
                placeholder="发送者名称"
                clearable
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="6">
            <el-form-item label-width="0">
              <el-button type="primary" @click="search" :loading="searching">
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
              <el-button @click="reset">
                <el-icon><RefreshLeft /></el-icon>
                重置
              </el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      
      <el-divider />
      
      <!-- 搜索结果 -->
      <div class="search-results">
        <div class="results-header">
          <span>搜索结果: {{ searchResults.total }} 条</span>
        </div>
        
        <el-table
          :data="searchResults.messages"
          v-loading="searching"
          max-height="600"
        >
          <el-table-column prop="created_at" label="时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>
          
          <el-table-column prop="sender_name" label="发送者" width="120" />
          
          <el-table-column prop="content" label="内容" min-width="300">
            <template #default="{ row }">
              <div class="message-content" v-html="highlightKeyword(row.content)"></div>
            </template>
          </el-table-column>
          
          <el-table-column prop="target_platform" label="平台" width="100">
            <template #default="{ row }">
              <el-tag :type="getPlatformType(row.target_platform)">
                {{ row.target_platform }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <el-pagination
          v-if="searchResults.total > 0"
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="searchResults.total"
          :page-sizes="[20, 50, 100, 200]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="search"
          @size-change="search"
          style="margin-top: 20px; justify-content: center"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, RefreshLeft } from '@element-plus/icons-vue'
import api from '@/api'

const searching = ref(false)
const currentPage = ref(1)
const pageSize = ref(50)

const searchForm = ref({
  keyword: '',
  platform: null,
  status: null,
  sender: null
})

const dateRange = ref(null)

const searchResults = ref({
  messages: [],
  total: 0,
  page: 1,
  page_size: 50,
  total_pages: 0
})

// 搜索
const search = async () => {
  searching.value = true
  
  try {
    const filters = {
      keyword: searchForm.value.keyword || null,
      platform: searchForm.value.platform || null,
      status: searchForm.value.status || null,
      sender: searchForm.value.sender || null,
      date_from: dateRange.value ? dateRange.value[0].toISOString() : null,
      date_to: dateRange.value ? dateRange.value[1].toISOString() : null
    }
    
    const response = await api.post('/api/message-search/search', filters, {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    
    searchResults.value = response
    
    if (response.total === 0) {
      ElMessage.info('没有找到匹配的消息')
    }
    
  } catch (error) {
    ElMessage.error('搜索失败：' + error.message)
  } finally {
    searching.value = false
  }
}

// 重置
const reset = () => {
  searchForm.value = {
    keyword: '',
    platform: null,
    status: null,
    sender: null
  }
  dateRange.value = null
  currentPage.value = 1
  searchResults.value = {
    messages: [],
    total: 0,
    page: 1,
    page_size: 50,
    total_pages: 0
  }
}

// 高亮关键词
const highlightKeyword = (content) => {
  if (!searchForm.value.keyword || !content) return content
  
  const keyword = searchForm.value.keyword
  const regex = new RegExp(`(${keyword})`, 'gi')
  return content.replace(regex, '<mark>$1</mark>')
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleString('zh-CN')
}

// 获取平台标签类型
const getPlatformType = (platform) => {
  const types = {
    'discord': 'primary',
    'telegram': 'success',
    'feishu': 'warning'
  }
  return types[platform] || 'info'
}

// 获取状态标签类型
const getStatusType = (status) => {
  const types = {
    'success': 'success',
    'failed': 'danger',
    'pending': 'warning'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    'success': '成功',
    'failed': '失败',
    'pending': '待处理'
  }
  return texts[status] || status
}
</script>

<style scoped>
.message-search {
  padding: 20px;
}

.search-results {
  margin-top: 20px;
}

.results-header {
  margin-bottom: 15px;
  font-weight: 500;
  color: #606266;
}

.message-content {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.message-content :deep(mark) {
  background-color: #FFF3CD;
  color: #856404;
  padding: 2px 4px;
  border-radius: 2px;
}
</style>
