/**
 * 虚拟滚动组合函数
 * 用于优化大数据列表渲染性能
 * 版本: v6.0.0
 * 
 * 使用方法:
 *   const { visibleItems, scrollHandler } = useVirtualScroll(items, options)
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'

export function useVirtualScroll(items, options = {}) {
  const {
    itemHeight = 60,       // 每项高度（px）
    visibleCount = 20,     // 可见项数量
    bufferCount = 5,       // 缓冲项数量（上下各加载bufferCount项）
    scrollContainer = null // 滚动容器（默认window）
  } = options
  
  // 状态
  const scrollTop = ref(0)
  const containerHeight = ref(0)
  
  // 计算可见范围
  const visibleRange = computed(() => {
    const start = Math.floor(scrollTop.value / itemHeight)
    const end = Math.min(
      start + visibleCount + bufferCount * 2,
      items.value.length
    )
    
    return {
      start: Math.max(0, start - bufferCount),
      end
    }
  })
  
  // 可见项
  const visibleItems = computed(() => {
    const { start, end } = visibleRange.value
    return items.value.slice(start, end).map((item, index) => ({
      ...item,
      _index: start + index,
      _offsetTop: (start + index) * itemHeight
    }))
  })
  
  // 总高度
  const totalHeight = computed(() => {
    return items.value.length * itemHeight
  })
  
  // 偏移量
  const offsetY = computed(() => {
    return visibleRange.value.start * itemHeight
  })
  
  // 滚动处理
  const scrollHandler = (event) => {
    const target = event.target
    
    if (target === document || target === window) {
      scrollTop.value = window.pageYOffset || document.documentElement.scrollTop
      containerHeight.value = window.innerHeight
    } else {
      scrollTop.value = target.scrollTop
      containerHeight.value = target.clientHeight
    }
  }
  
  // 挂载时添加监听
  onMounted(() => {
    const target = scrollContainer || window
    target.addEventListener('scroll', scrollHandler, { passive: true })
    
    // 初始化容器高度
    if (target === window) {
      containerHeight.value = window.innerHeight
    } else {
      containerHeight.value = target.clientHeight
    }
  })
  
  // 卸载时移除监听
  onUnmounted(() => {
    const target = scrollContainer || window
    target.removeEventListener('scroll', scrollHandler)
  })
  
  return {
    visibleItems,
    totalHeight,
    offsetY,
    scrollHandler,
    visibleRange
  }
}

/**
 * 虚拟表格滚动（用于表格场景）
 */
export function useVirtualTable(rows, options = {}) {
  const {
    rowHeight = 48,
    headerHeight = 40,
    ...restOptions
  } = options
  
  const virtualScroll = useVirtualScroll(rows, {
    ...restOptions,
    itemHeight: rowHeight
  })
  
  return {
    ...virtualScroll,
    rowHeight,
    headerHeight
  }
}

/**
 * 虚拟网格滚动（用于网格布局）
 */
export function useVirtualGrid(items, options = {}) {
  const {
    itemWidth = 200,
    itemHeight = 200,
    columns = 4,
    gap = 16,
    ...restOptions
  } = options
  
  // 计算行数
  const rows = computed(() => {
    return Math.ceil(items.value.length / columns)
  })
  
  // 计算每行高度
  const rowHeight = itemHeight + gap
  
  const virtualScroll = useVirtualScroll(rows, {
    ...restOptions,
    itemHeight: rowHeight
  })
  
  // 转换为网格项
  const visibleGridItems = computed(() => {
    const { start, end } = virtualScroll.visibleRange.value
    const result = []
    
    for (let rowIndex = start; rowIndex < end; rowIndex++) {
      for (let colIndex = 0; colIndex < columns; colIndex++) {
        const itemIndex = rowIndex * columns + colIndex
        
        if (itemIndex < items.value.length) {
          result.push({
            ...items.value[itemIndex],
            _index: itemIndex,
            _row: rowIndex,
            _col: colIndex,
            _offsetTop: rowIndex * rowHeight,
            _offsetLeft: colIndex * (itemWidth + gap)
          })
        }
      }
    }
    
    return result
  })
  
  return {
    visibleItems: visibleGridItems,
    totalHeight: computed(() => rows.value * rowHeight),
    offsetY: virtualScroll.offsetY,
    scrollHandler: virtualScroll.scrollHandler,
    itemWidth,
    itemHeight,
    columns,
    gap
  }
}
