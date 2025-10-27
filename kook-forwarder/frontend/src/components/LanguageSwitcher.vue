<template>
  <el-dropdown @command="changeLanguage" trigger="click" placement="bottom-end">
    <el-button text>
      <el-icon><Operation /></el-icon>
      <span style="margin-left: 5px">{{ currentLanguageName }}</span>
    </el-button>
    
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item
          v-for="lang in languages"
          :key="lang.value"
          :command="lang.value"
          :divided="lang.value !== languages[0].value"
        >
          <span style="margin-right: 8px">{{ lang.icon }}</span>
          <span :style="{ fontWeight: currentLocale === lang.value ? 'bold' : 'normal' }">
            {{ lang.label }}
          </span>
          <el-icon v-if="currentLocale === lang.value" style="margin-left: 8px">
            <Check />
          </el-icon>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Operation, Check } from '@element-plus/icons-vue'
import { setLanguage, getSupportedLanguages } from '@/i18n'

const { locale } = useI18n()

// 获取支持的语言列表
const languages = getSupportedLanguages()

// 当前语言代码
const currentLocale = computed(() => locale.value)

// 当前语言显示名称
const currentLanguageName = computed(() => {
  const current = languages.find(lang => lang.value === locale.value)
  return current ? `${current.icon} ${current.label}` : '简体中文'
})

// 切换语言
const changeLanguage = (lang) => {
  if (lang === locale.value) {
    return
  }
  
  setLanguage(lang)
  
  const langName = languages.find(l => l.value === lang)?.label || lang
  ElMessage.success(`语言已切换为：${langName} / Language changed to: ${langName}`)
  
  // 可选：刷新页面以确保所有组件都使用新语言
  // setTimeout(() => {
  //   window.location.reload()
  // }, 500)
}
</script>

<style scoped>
:deep(.el-button) {
  color: var(--el-text-color-regular);
}

:deep(.el-button:hover) {
  color: var(--el-color-primary);
}
</style>
