<!--
  新手引导触发组件
  在应用首次加载时自动触发引导
-->
<template>
  <div v-if="false"></div>
</template>

<script setup>
import { onMounted } from 'vue'
import { startFirstTimeOnboarding } from '@/utils/onboarding'

onMounted(() => {
  // 延迟启动引导，确保页面完全加载
  setTimeout(() => {
    startFirstTimeOnboarding()
  }, 1500)
})
</script>
