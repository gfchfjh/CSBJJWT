<template>
  <div class="mapping-unified-container">
    <!-- 视图切换工具栏 -->
    <div class="view-switcher-toolbar">
      <div class="toolbar-left">
        <h2>
          <el-icon><Connection /></el-icon>
          频道映射配置
        </h2>
      </div>
      
      <div class="toolbar-center">
        <el-segmented v-model="currentView" :options="viewOptions" size="large" />
      </div>
      
      <div class="toolbar-right">
        <el-tooltip content="在表格和流程图视图间切换，选择您喜欢的方式" placement="bottom">
          <el-icon :size="20" color="#909399"><QuestionFilled /></el-icon>
        </el-tooltip>
      </div>
    </div>

    <!-- 视图说明 -->
    <el-alert
      v-if="showViewHint"
      :type="currentView === 'table' ? 'success' : 'info'"
      :closable="true"
      @close="showViewHint = false"
      class="view-hint"
    >
      <template #title>
        <strong v-if="currentView === 'table'">📊 表格视图</strong>
        <strong v-else>🎨 流程图视图</strong>
      </template>
      <div v-if="currentView === 'table'">
        <p>✅ 适合快速查看和编辑大量映射</p>
        <p>✅ 支持批量操作、筛选和排序</p>
        <p>✅ 清晰的列表展示，便于管理</p>
      </div>
      <div v-else>
        <p>✅ 直观展示映射关系和数据流向</p>
        <p>✅ 拖拽式操作，可视化编辑</p>
        <p>✅ 适合理解复杂的映射结构</p>
      </div>
    </el-alert>

    <!-- 视图内容 -->
    <div class="view-content">
      <!-- 表格视图 -->
      <transition name="fade">
        <MappingTableView v-if="currentView === 'table'" />
      </transition>
      
      <!-- 流程图视图 -->
      <transition name="fade">
        <!-- MappingVisualFlow v-if="currentView === 'flow'" / -->
        <div v-if="currentView === 'flow'" class="coming-soon">
          <el-empty description="流程图视图功能即将推出">
            <el-button type="primary" @click="currentView = 'table'">返回表格视图</el-button>
          </el-empty>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Connection, QuestionFilled } from '@element-plus/icons-vue'
import MappingTableView from './MappingTableView.vue'
// import MappingVisualFlow from './MappingVisualFlow.vue'

// 当前视图
const currentView = ref('table')  // 默认使用表格视图（更符合需求文档）

// 视图选项
const viewOptions = [
  {
    label: '📊 表格视图',
    value: 'table'
  },
  {
    label: '🎨 流程图视图',
    value: 'flow'
  }
]

// 是否显示视图提示
const showViewHint = ref(true)

onMounted(() => {
  // 从本地存储恢复用户偏好
  const savedView = localStorage.getItem('mapping_view_preference')
  if (savedView && ['table', 'flow'].includes(savedView)) {
    currentView.value = savedView
  }
  
  // 检查是否首次访问
  const firstVisit = localStorage.getItem('mapping_view_first_visit')
  if (firstVisit) {
    showViewHint.value = false
  } else {
    localStorage.setItem('mapping_view_first_visit', 'true')
  }
})

// 监听视图切换，保存用户偏好
const saveViewPreference = (view) => {
  localStorage.setItem('mapping_view_preference', view)
}

// 监听当前视图变化
import { watch } from 'vue'
watch(currentView, (newView) => {
  saveViewPreference(newView)
})
</script>

<style scoped>
.mapping-unified-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  padding: 20px;
}

.view-switcher-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.toolbar-left h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.toolbar-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.toolbar-right {
  display: flex;
  align-items: center;
}

.view-hint {
  margin-bottom: 20px;
}

.view-hint p {
  margin: 3px 0;
  font-size: 14px;
}

.view-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}

/* 视图切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .view-switcher-toolbar {
    flex-direction: column;
    gap: 15px;
  }
  
  .toolbar-center {
    width: 100%;
  }
  
  .toolbar-center :deep(.el-segmented) {
    width: 100%;
  }
}
</style>
