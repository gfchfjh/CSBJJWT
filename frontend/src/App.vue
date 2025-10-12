<template>
  <div class="app-container">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useSystemStore } from './store/system'

const systemStore = useSystemStore()

onMounted(() => {
  // 初始化系统状态
  systemStore.fetchSystemStatus()
})
</script>

<style scoped>
.app-container {
  width: 100%;
  height: 100%;
}
</style>
