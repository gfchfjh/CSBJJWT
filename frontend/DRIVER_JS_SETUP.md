# Driver.js 集成指南

## 📦 安装依赖

新手引导系统使用 `driver.js` 库实现分步高亮引导。

### 安装方法

```bash
cd frontend
npm install driver.js
```

或

```bash
cd frontend
npm install driver.js@1.3.1
```

## 🎯 使用方式

### 方法1：自动引导（推荐）

在 `App.vue` 或主页面中添加：

```vue
<script setup>
import { onMounted } from 'vue'
import { useGlobalGuide } from '@/composables/useGuide'

const { shouldShowGuide, showGuideChoice } = useGlobalGuide()

onMounted(() => {
  // 首次使用自动显示引导
  if (shouldShowGuide()) {
    setTimeout(() => {
      showGuideChoice()
    }, 1000)
  }
})
</script>
```

### 方法2：手动触发

在任何页面中触发引导：

```vue
<template>
  <el-button @click="startGuide">开始新手引导</el-button>
</template>

<script setup>
import { useGlobalGuide } from '@/composables/useGuide'

const { startFullGuide, startQuickGuide, startFeatureGuide } = useGlobalGuide()

const startGuide = () => {
  // 完整引导（8步）
  startFullGuide()
  
  // 或快速引导（3步）
  // startQuickGuide()
  
  // 或功能演示
  // startFeatureGuide('cookie-import')
}
</script>
```

## 🎨 自定义样式

引导样式已在 `useGuide.js` 中注入，如需自定义：

```javascript
// 在 useGuide.js 中修改 injectGuideStyles() 函数
```

## 📝 添加新的引导步骤

在 `useGuide.js` 中修改 `startFullGuide` 或 `startQuickGuide` 函数：

```javascript
{
  element: '#your-element-id',
  popover: {
    title: '步骤标题',
    description: '步骤描述',
    position: 'bottom' // top, bottom, left, right, center
  },
  onHighlightStarted: () => {
    // 高亮前执行（如跳转路由）
    router.push('/some-page')
  }
}
```

## 🔧 可用的引导类型

1. **完整引导** - 8步覆盖所有核心功能
2. **快速引导** - 3步快速上手
3. **功能演示** - 针对特定功能的详细引导
   - `cookie-import` - Cookie导入演示
   - `smart-mapping` - 智能映射演示
   - `filter-rules` - 过滤规则演示

## 📌 元素ID约定

为了引导系统正常工作，请确保关键元素有正确的ID：

```html
<!-- 导航菜单 -->
<router-link to="/accounts" id="nav-accounts">账号管理</router-link>
<router-link to="/bots" id="nav-bots">机器人配置</router-link>
<router-link to="/mapping" id="nav-mapping">频道映射</router-link>
<router-link to="/logs" id="nav-logs">实时日志</router-link>

<!-- 操作按钮 -->
<el-button id="add-account-btn">添加账号</el-button>
<el-button id="add-bot-btn">添加Bot</el-button>
<el-button id="smart-mapping-btn">智能映射</el-button>
<el-button id="start-service-btn">启动服务</el-button>

<!-- Cookie导入 -->
<div class="drag-upload-area" id="cookie-import-area">...</div>
<el-input class="cookie-textarea" id="cookie-paste-area">...</el-input>
```

## 🎬 示例截图

(引导效果示例图片应放在此处)

## ⚙️ 当前状态

✅ 引导系统已完整实现
✅ 支持完整/快速/功能演示三种模式
✅ 自动记录完成状态，避免重复显示
⚠️ 需要安装 driver.js 库才能使用真实的高亮效果

## 🔄 后备方案

如果未安装 driver.js，系统会使用简化版本（基于Element Plus Message），功能有限但可用。

建议在生产环境安装完整的 driver.js 以获得最佳体验。
