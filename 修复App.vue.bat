@echo off
chcp 65001 >nul
cd /d "%~dp0frontend\src"

echo 正在恢复并修复 App.vue...

(
echo ^<template^>
echo   ^<div class="app-container"^>
echo     ^<!-- ✅ v17.0.0深度优化: 免责声明弹窗（首次启动强制显示） --^>
echo     ^<DisclaimerDialog
echo       v-model="disclaimerVisible"
echo       @accepted="onDisclaimerAccepted"
echo       @declined="onDisclaimerDeclined"
echo     /^>
echo     
echo     ^<!-- ✅ P0-2优化: 首次运行检测器 --^>
echo     ^<FirstRunDetector /^>
echo     
echo     ^<router-view /^>
echo     
echo     ^<!-- ✅ P0-5优化：友好错误提示对话框（全局） --^>
echo     ^<ErrorDialog
echo       v-model="errorDialog.visible"
echo       :error-data="errorDialog.data"
echo       @fixed="onErrorFixed"
echo     /^>
echo   ^</div^>
echo ^</template^>
echo.
echo ^<script setup^>
echo import { ref, onMounted, reactive, watch } from 'vue'
echo import { ElMessage, ElMessageBox } from 'element-plus'
echo import { useSystemStore } from './store/system'
echo import ErrorDialog from './components/ErrorDialog.vue'
echo import DisclaimerDialog from './views/DisclaimerDialog.vue'
echo import { useGlobalErrorHandler } from './composables/useErrorHandler'
echo import FirstRunDetector from './components/FirstRunDetector.vue'
echo.
echo const systemStore = useSystemStore(^)
echo const globalErrorHandler = useGlobalErrorHandler(^)
echo.
echo // ✅ P0-5优化：全局错误对话框状态
echo const errorDialog = reactive({
echo   visible: false,
echo   data: {}
echo }^)
echo.
echo // 监听全局错误处理器
echo watch(^(^) =^> globalErrorHandler?.showErrorDialog?.value, ^(show^) =^> {
echo   if ^(show^) {
echo     errorDialog.visible = show
echo     errorDialog.data = globalErrorHandler.currentError.value ^|^| {}
echo   }
echo }^)
echo.
echo // 错误修复完成回调
echo const onErrorFixed = ^(result^) =^> {
echo   console.log^('✅ 错误已修复:', result^)
echo }
echo.
echo // ✅ v17.0.0深度优化: 免责声明状态
echo const disclaimerVisible = ref^(false^)
echo.
echo onMounted(^(^) =^> {
echo   // ✅ v17.0.0深度优化: 检查免责声明
echo   checkDisclaimer(^)
echo   
echo   // 初始化系统状态
echo   systemStore.fetchSystemStatus(^)
echo }^)
echo.
echo // ✅ v17.0.0深度优化: 检查免责声明状态
echo const checkDisclaimer = async ^(^) =^> {
echo   try {
echo     const response = await fetch^('/api/disclaimer/status'^)
echo     if ^(response.ok^) {
echo       const data = await response.json(^)
echo       
echo       // 如果未同意过，显示免责声明
echo       if ^(data.needs_accept^) {
echo         // 延迟显示，确保页面已加载
echo         setTimeout^(^(^) =^> {
echo           disclaimerVisible.value = true
echo         }, 500^)
echo       }
echo     } else {
echo       // API失败时，检查本地存储作为备选
echo       const accepted = localStorage.getItem^('disclaimer_accepted'^)
echo       if ^(!accepted^) {
echo         setTimeout^(^(^) =^> {
echo           disclaimerVisible.value = true
echo         }, 500^)
echo       }
echo     }
echo   } catch ^(error^) {
echo     console.error^('检查免责声明状态失败:', error^)
echo     // 出错时，仍然显示免责声明（安全起见）
echo     setTimeout^(^(^) =^> {
echo       disclaimerVisible.value = true
echo     }, 500^)
echo   }
echo }
echo.
echo // ✅ v17.0.0深度优化: 用户同意免责声明
echo const onDisclaimerAccepted = ^(^) =^> {
echo   // 本地也保存一份（备份）
echo   localStorage.setItem^('disclaimer_accepted', 'true'^)
echo   localStorage.setItem^('disclaimer_accepted_at', new Date^(^).toISOString^(^)^)
echo   
echo   ElMessage.success^({
echo     message: '感谢您的理解和支持，欢迎使用KOOK消息转发系统',
echo     duration: 3000
echo   }^)
echo }
echo.
echo // ✅ v17.0.0深度优化: 用户拒绝免责声明
echo const onDisclaimerDeclined = ^(^) =^> {
echo   ElMessage.warning^('您已拒绝免责声明，应用将退出'^)
echo }
echo ^</script^>
echo.
echo ^<style scoped^>
echo .app-container {
echo   width: 100%%;
echo   height: 100%%;
echo }
echo ^</style^>
) > App.vue

echo ✅ App.vue 已修复！

timeout /t 2 /nobreak >nul
