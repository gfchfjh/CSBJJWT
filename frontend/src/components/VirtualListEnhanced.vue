<template>
  <div
    ref="containerRef"
    class="virtual-list-enhanced"
    @scroll="handleScroll"
  >
    <div :style="{ height: `${totalHeight}px`, position: 'relative' }">
      <div
        :style="{
          transform: `translateY(${offsetY}px)`,
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0
        }"
      >
        <slot
          v-for="item in visibleItems"
          :key="item[itemKey]"
          name="item"
          :item="item"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 虚拟滚动列表组件（增强版）
 * P2-4: 日志虚拟滚动
 * 
 * 性能优化：
 * - 仅渲染可见区域的元素（+buffer）
 * - 支持 10000+ 条数据流畅显示
 * - 内存占用恒定
 */
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    required: true
  },
  itemHeight: {
    type: Number,
    default: 60
  },
  itemKey: {
    type: String,
    default: 'id'
  },
  buffer: {
    type: Number,
    default: 5
  }
})

// 状态
const containerRef = ref(null)
const scrollTop = ref(0)
const containerHeight = ref(0)

// 计算属性
const totalHeight = computed(() => {
  return props.items.length * props.itemHeight
})

const visibleCount = computed(() => {
  return Math.ceil(containerHeight.value / props.itemHeight)
})

const startIndex = computed(() => {
  const index = Math.floor(scrollTop.value / props.itemHeight) - props.buffer
  return Math.max(0, index)
})

const endIndex = computed(() => {
  const index = startIndex.value + visibleCount.value + props.buffer * 2
  return Math.min(props.items.length, index)
})

const visibleItems = computed(() => {
  return props.items.slice(startIndex.value, endIndex.value)
})

const offsetY = computed(() => {
  return startIndex.value * props.itemHeight
})

// 方法
const handleScroll = (event) => {
  scrollTop.value = event.target.scrollTop
}

const updateContainerHeight = () => {
  if (containerRef.value) {
    containerHeight.value = containerRef.value.clientHeight
  }
}

// 生命周期
onMounted(() => {
  updateContainerHeight()
  window.addEventListener('resize', updateContainerHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateContainerHeight)
})
</script>

<style scoped>
.virtual-list-enhanced {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
}
</style>
