<!--
虚拟滚动列表组件
✅ P1-3优化: 支持10万+条数据流畅滚动
-->
<template>
  <div 
    ref="container"
    class="virtual-list-container"
    @scroll="handleScroll"
    :style="{ height: containerHeight + 'px', overflow: 'auto' }"
  >
    <!-- 占位div，撑开滚动高度 -->
    <div 
      class="virtual-list-phantom"
      :style="{ height: totalHeight + 'px', position: 'relative' }"
    >
      <!-- 可见项容器 -->
      <div
        class="virtual-list-content"
        :style="{ transform: `translateY(${offsetY}px)` }"
      >
        <div
          v-for="item in visibleItems"
          :key="item[keyField]"
          class="virtual-list-item"
          :style="{ height: itemHeight + 'px' }"
        >
          <slot :item="item" :index="item._index" />
        </div>
      </div>
    </div>
    
    <!-- 加载更多 -->
    <div 
      v-if="loading"
      class="virtual-list-loading"
    >
      <slot name="loading">
        <div class="loading-spinner">加载中...</div>
      </slot>
    </div>
    
    <!-- 空状态 -->
    <div
      v-if="!loading && items.length === 0"
      class="virtual-list-empty"
    >
      <slot name="empty">
        <div class="empty-state">暂无数据</div>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  // 数据列表
  items: {
    type: Array,
    required: true,
    default: () => []
  },
  // 单项高度（固定高度模式）
  itemHeight: {
    type: Number,
    default: 80
  },
  // 容器高度
  containerHeight: {
    type: Number,
    default: 600
  },
  // 缓冲区大小（上下各多渲染几条）
  bufferSize: {
    type: Number,
    default: 5
  },
  // 唯一键字段
  keyField: {
    type: String,
    default: 'id'
  },
  // 是否加载中
  loading: {
    type: Boolean,
    default: false
  },
  // 是否启用无限滚动
  infiniteScroll: {
    type: Boolean,
    default: false
  },
  // 触发加载更多的距离（距离底部多少px时触发）
  loadMoreThreshold: {
    type: Number,
    default: 100
  }
})

const emit = defineEmits(['load-more', 'scroll'])

// 响应式状态
const container = ref(null)
const scrollTop = ref(0)

// 计算属性
const totalHeight = computed(() => {
  return props.items.length * props.itemHeight
})

const visibleRange = computed(() => {
  // 计算可见范围的起始和结束索引
  const start = Math.max(0, Math.floor(scrollTop.value / props.itemHeight) - props.bufferSize)
  const end = Math.min(
    props.items.length,
    Math.ceil((scrollTop.value + props.containerHeight) / props.itemHeight) + props.bufferSize
  )
  return { start, end }
})

const visibleItems = computed(() => {
  const { start, end } = visibleRange.value
  
  // 为每个可见项添加索引信息
  return props.items.slice(start, end).map((item, index) => ({
    ...item,
    _index: start + index,
    _top: (start + index) * props.itemHeight
  }))
})

const offsetY = computed(() => {
  // 可见区域的偏移量
  return visibleRange.value.start * props.itemHeight
})

// 滚动处理
const handleScroll = (e) => {
  const newScrollTop = e.target.scrollTop
  scrollTop.value = newScrollTop
  
  // 触发scroll事件
  emit('scroll', {
    scrollTop: newScrollTop,
    scrollHeight: e.target.scrollHeight,
    clientHeight: e.target.clientHeight
  })
  
  // 无限滚动：检查是否接近底部
  if (props.infiniteScroll && !props.loading) {
    const distanceToBottom = e.target.scrollHeight - newScrollTop - e.target.clientHeight
    if (distanceToBottom < props.loadMoreThreshold) {
      emit('load-more')
    }
  }
}

// 滚动到指定位置
const scrollTo = (index) => {
  if (!container.value) return
  
  const targetScrollTop = index * props.itemHeight
  container.value.scrollTop = targetScrollTop
}

// 滚动到底部
const scrollToBottom = () => {
  if (!container.value) return
  
  container.value.scrollTop = container.value.scrollHeight
}

// 滚动到顶部
const scrollToTop = () => {
  if (!container.value) return
  
  container.value.scrollTop = 0
}

// 暴露方法给父组件
defineExpose({
  scrollTo,
  scrollToBottom,
  scrollToTop,
  getScrollTop: () => scrollTop.value,
  getVisibleRange: () => visibleRange.value
})

// 监听items变化，自动滚动到底部（可选）
const autoScrollToBottom = ref(false)

watch(() => props.items.length, (newLen, oldLen) => {
  if (autoScrollToBottom.value && newLen > oldLen) {
    // 新增数据时自动滚动到底部
    setTimeout(() => scrollToBottom(), 100)
  }
})

// 生命周期
onMounted(() => {
  // 初始化滚动位置
  if (container.value) {
    scrollTop.value = container.value.scrollTop
  }
})

onUnmounted(() => {
  // 清理
})
</script>

<style scoped>
.virtual-list-container {
  position: relative;
  width: 100%;
  overflow-y: auto;
  overflow-x: hidden;
}

.virtual-list-phantom {
  position: relative;
  width: 100%;
}

.virtual-list-content {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  will-change: transform;
}

.virtual-list-item {
  width: 100%;
  box-sizing: border-box;
}

.virtual-list-loading {
  padding: 20px;
  text-align: center;
}

.loading-spinner {
  color: #409eff;
  font-size: 14px;
}

.virtual-list-empty {
  padding: 40px 20px;
  text-align: center;
}

.empty-state {
  color: #909399;
  font-size: 14px;
}

/* 滚动条样式 */
.virtual-list-container::-webkit-scrollbar {
  width: 8px;
}

.virtual-list-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.virtual-list-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.virtual-list-container::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style>
