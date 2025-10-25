# KOOK转发系统 - P1级别完整优化实施手册

**优先级**: P1 - 高（第二阶段执行）  
**总工作量**: 225小时  
**预期完成**: 6-7周（2-3人团队）

---

## 📋 目录

- [优化4: 增强验证码处理能力](#优化4-增强验证码处理能力)
- [优化5: 完善消息类型支持](#优化5-完善消息类型支持)
- [优化6: 图床功能安全性和性能优化](#优化6-图床功能安全性和性能优化)
- [优化7: 多账号管理界面重构](#优化7-多账号管理界面重构)
- [优化8: 智能频道映射算法优化](#优化8-智能频道映射算法优化)

---

## 优化4: 增强验证码处理能力

### 📊 优化概览

**当前问题**:
- 仅支持2Captcha自动识别
- 缺少手动输入回退机制
- 无智能策略切换
- 识别状态反馈不足

**目标**:
- 实现3种验证码处理方案
- 自动智能切换策略
- 提升登录成功率到95%+

**工作量**: 25小时

---

### 🎯 实施步骤

#### 步骤4.1: 实现手动验证码输入对话框（6小时）

**文件**: `frontend/src/components/CaptchaDialog.vue`

```vue
<template>
  <el-dialog
    v-model="visible"
    title="验证码识别"
    width="500px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @close="handleClose"
  >
    <!-- 验证码显示 -->
    <div class="captcha-container">
      <el-card shadow="never" class="captcha-card">
        <template #header>
          <div class="card-header">
            <span>请输入图中的验证码</span>
            <el-tag :type="getStatusType()">
              {{ getStatusText() }}
            </el-tag>
          </div>
        </template>

        <!-- 验证码图片 -->
        <div class="captcha-image-wrapper">
          <el-image
            :src="captchaImage"
            fit="contain"
            class="captcha-image"
            @load="handleImageLoad"
            @error="handleImageError"
          >
            <template #placeholder>
              <div class="image-loading">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>加载中...</span>
              </div>
            </template>
            <template #error>
              <div class="image-error">
                <el-icon><PictureFilled /></el-icon>
                <span>加载失败</span>
              </div>
            </template>
          </el-image>

          <!-- 刷新按钮 -->
          <el-button
            class="refresh-button"
            circle
            :icon="Refresh"
            @click="handleRefresh"
            :loading="refreshing"
          />
        </div>

        <!-- 验证码输入 -->
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          class="captcha-form"
        >
          <el-form-item prop="code">
            <el-input
              ref="inputRef"
              v-model="form.code"
              placeholder="请输入验证码"
              clearable
              autofocus
              maxlength="6"
              show-word-limit
              @keyup.enter="handleSubmit"
            >
              <template #prefix>
                <el-icon><Key /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-form>

        <!-- 提示信息 -->
        <el-alert
          v-if="hint"
          :type="hintType"
          :title="hint"
          :closable="false"
          show-icon
          class="hint-alert"
        />

        <!-- 倒计时 -->
        <div class="countdown" v-if="countdown > 0">
          <el-progress
            :percentage="(countdown / 60) * 100"
            :color="getCountdownColor()"
            :show-text="false"
          />
          <span class="countdown-text">
            剩余时间: {{ countdown }}秒
          </span>
        </div>

        <!-- 自动识别进度 -->
        <transition name="el-fade-in">
          <div v-if="autoRecognizing" class="auto-recognizing">
            <el-steps :active="autoStep" finish-status="success" align-center>
              <el-step title="上传图片" />
              <el-step title="AI识别" />
              <el-step title="验证结果" />
            </el-steps>
            <el-progress
              :percentage="autoProgress"
              :status="autoStatus"
              class="auto-progress"
            />
            <p class="auto-message">{{ autoMessage }}</p>
          </div>
        </transition>
      </el-card>
    </div>

    <!-- 操作按钮 -->
    <template #footer>
      <el-space>
        <!-- 策略切换 -->
        <el-dropdown @command="handleStrategyChange">
          <el-button>
            切换策略
            <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="auto" :disabled="!canUseAuto">
                <el-icon><MagicStick /></el-icon>
                自动识别 (2Captcha)
              </el-dropdown-item>
              <el-dropdown-item command="local" :disabled="!canUseLocal">
                <el-icon><Monitor /></el-icon>
                本地OCR (ddddocr)
              </el-dropdown-item>
              <el-dropdown-item command="manual">
                <el-icon><Edit /></el-icon>
                手动输入 (当前)
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <el-button @click="handleCancel">
          取消
        </el-button>

        <el-button
          type="primary"
          @click="handleSubmit"
          :loading="submitting"
          :disabled="!form.code"
        >
          提交 ({{ form.code.length }}/4-6)
        </el-button>
      </el-space>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Loading,
  PictureFilled,
  Refresh,
  Key,
  MagicStick,
  Monitor,
  Edit,
  ArrowDown
} from '@element-plus/icons-vue'
import api from '@/api'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  captchaImage: {
    type: String,
    required: true
  },
  strategy: {
    type: String,
    default: 'manual' // manual | auto | local
  }
})

const emit = defineEmits(['update:modelValue', 'submit', 'cancel', 'refresh', 'strategy-change'])

// 响应式状态
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const inputRef = ref(null)
const formRef = ref(null)
const form = reactive({
  code: ''
})

const rules = {
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { min: 4, max: 6, message: '验证码长度为4-6位', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z0-9]+$/,
      message: '验证码只能包含字母和数字',
      trigger: 'blur'
    }
  ]
}

// 状态
const refreshing = ref(false)
const submitting = ref(false)
const countdown = ref(60)
const countdownTimer = ref(null)

const hint = ref('')
const hintType = ref('info')

const autoRecognizing = ref(false)
const autoStep = ref(0)
const autoProgress = ref(0)
const autoStatus = ref('')
const autoMessage = ref('')

// 能力检测
const canUseAuto = ref(false)
const canUseLocal = ref(false)

// 监听对话框打开
watch(visible, async (newVal) => {
  if (newVal) {
    // 重置状态
    form.code = ''
    hint.value = ''
    countdown.value = 60
    startCountdown()

    // 聚焦输入框
    await nextTick()
    inputRef.value?.focus()

    // 检测能力
    await detectCapabilities()

    // 根据策略自动处理
    if (props.strategy === 'auto' && canUseAuto.value) {
      handleAutoRecognize()
    } else if (props.strategy === 'local' && canUseLocal.value) {
      handleLocalRecognize()
    }
  } else {
    // 清理倒计时
    stopCountdown()
  }
})

// 检测验证码识别能力
const detectCapabilities = async () => {
  try {
    const result = await api.detectCaptchaCapabilities()
    canUseAuto.value = result.auto_available
    canUseLocal.value = result.local_available

    if (!canUseAuto.value) {
      hint.value = '2Captcha未配置，使用手动输入模式'
      hintType.value = 'warning'
    }
  } catch (error) {
    console.error('检测能力失败:', error)
  }
}

// 倒计时
const startCountdown = () => {
  stopCountdown()
  countdownTimer.value = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      stopCountdown()
      ElMessage.warning('验证码已超时，请刷新')
      handleRefresh()
    }
  }, 1000)
}

const stopCountdown = () => {
  if (countdownTimer.value) {
    clearInterval(countdownTimer.value)
    countdownTimer.value = null
  }
}

// 获取倒计时颜色
const getCountdownColor = () => {
  if (countdown.value > 40) return '#67C23A'
  if (countdown.value > 20) return '#E6A23C'
  return '#F56C6C'
}

// 获取状态文本
const getStatusText = () => {
  if (autoRecognizing.value) return '自动识别中'
  if (props.strategy === 'auto') return '2Captcha模式'
  if (props.strategy === 'local') return '本地OCR模式'
  return '手动输入模式'
}

const getStatusType = () => {
  if (autoRecognizing.value) return 'warning'
  if (props.strategy === 'auto') return 'success'
  if (props.strategy === 'local') return 'info'
  return 'primary'
}

// 图片加载完成
const handleImageLoad = () => {
  console.log('验证码图片加载成功')
}

// 图片加载失败
const handleImageError = () => {
  ElMessage.error('验证码图片加载失败，请刷新')
  hint.value = '图片加载失败，请点击刷新按钮'
  hintType.value = 'error'
}

// 刷新验证码
const handleRefresh = async () => {
  refreshing.value = true

  try {
    emit('refresh')
    
    // 重置状态
    form.code = ''
    hint.value = ''
    countdown.value = 60
    startCountdown()

    await nextTick()
    inputRef.value?.focus()

  } finally {
    refreshing.value = false
  }
}

// 自动识别
const handleAutoRecognize = async () => {
  if (!canUseAuto.value) {
    ElMessage.warning('2Captcha服务不可用')
    return
  }

  autoRecognizing.value = true
  autoStep.value = 0
  autoProgress.value = 0
  autoStatus.value = ''
  autoMessage.value = '正在上传验证码图片...'

  try {
    // 步骤1: 上传图片
    autoStep.value = 1
    autoProgress.value = 30
    await new Promise(resolve => setTimeout(resolve, 500))

    // 步骤2: AI识别
    autoStep.value = 2
    autoMessage.value = '正在使用AI识别验证码...'
    autoProgress.value = 60

    const result = await api.recognizeCaptcha({
      image: props.captchaImage,
      method: '2captcha'
    })

    if (result.success) {
      // 步骤3: 验证结果
      autoStep.value = 3
      autoProgress.value = 100
      autoStatus.value = 'success'
      autoMessage.value = `识别成功: ${result.code}`

      form.code = result.code
      hint.value = `自动识别结果: ${result.code}，请确认后提交`
      hintType.value = 'success'

      ElMessage.success('自动识别成功')

      // 3秒后自动提交
      setTimeout(() => {
        if (visible.value && form.code === result.code) {
          handleSubmit()
        }
      }, 3000)

    } else {
      throw new Error(result.message || '识别失败')
    }

  } catch (error) {
    autoStatus.value = 'exception'
    autoMessage.value = `识别失败: ${error.message}`
    hint.value = '自动识别失败，请手动输入'
    hintType.value = 'error'
    
    ElMessage.error('自动识别失败，请手动输入')

  } finally {
    setTimeout(() => {
      autoRecognizing.value = false
    }, 2000)
  }
}

// 本地OCR识别
const handleLocalRecognize = async () => {
  if (!canUseLocal.value) {
    ElMessage.warning('本地OCR服务不可用')
    return
  }

  autoRecognizing.value = true
  autoStep.value = 0
  autoProgress.value = 0
  autoMessage.value = '正在使用本地OCR识别...'

  try {
    autoStep.value = 1
    autoProgress.value = 50

    const result = await api.recognizeCaptcha({
      image: props.captchaImage,
      method: 'ddddocr'
    })

    if (result.success) {
      autoStep.value = 2
      autoProgress.value = 100
      autoStatus.value = 'success'
      autoMessage.value = `识别成功: ${result.code}`

      form.code = result.code
      hint.value = `本地OCR识别结果: ${result.code}，准确率约70%，请确认`
      hintType.value = 'warning'

      ElMessage.success('本地识别完成，请确认')

    } else {
      throw new Error(result.message || '识别失败')
    }

  } catch (error) {
    autoStatus.value = 'exception'
    autoMessage.value = `识别失败: ${error.message}`
    hint.value = '本地识别失败，请手动输入'
    hintType.value = 'error'
    
  } finally {
    setTimeout(() => {
      autoRecognizing.value = false
    }, 2000)
  }
}

// 切换策略
const handleStrategyChange = (command) => {
  emit('strategy-change', command)

  if (command === 'auto' && canUseAuto.value) {
    handleAutoRecognize()
  } else if (command === 'local' && canUseLocal.value) {
    handleLocalRecognize()
  }
}

// 提交
const handleSubmit = async () => {
  try {
    await formRef.value.validate()

    submitting.value = true

    emit('submit', form.code)

  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    // 由父组件控制loading状态
    setTimeout(() => {
      submitting.value = false
    }, 1000)
  }
}

// 取消
const handleCancel = () => {
  emit('cancel')
  visible.value = false
}

// 关闭
const handleClose = () => {
  stopCountdown()
}

// 组件卸载时清理
onUnmounted(() => {
  stopCountdown()
})
</script>

<style scoped lang="scss">
.captcha-container {
  .captcha-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .captcha-image-wrapper {
      position: relative;
      width: 100%;
      height: 150px;
      border: 2px dashed #DCDFE6;
      border-radius: 4px;
      overflow: hidden;
      background: #F5F7FA;
      margin-bottom: 20px;

      .captcha-image {
        width: 100%;
        height: 100%;

        :deep(.el-image__inner) {
          object-fit: contain;
        }
      }

      .image-loading,
      .image-error {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: #909399;

        .el-icon {
          font-size: 40px;
          margin-bottom: 10px;
        }
      }

      .refresh-button {
        position: absolute;
        top: 10px;
        right: 10px;
        background: rgba(255, 255, 255, 0.9);
      }
    }

    .captcha-form {
      margin-bottom: 15px;

      :deep(.el-form-item) {
        margin-bottom: 0;
      }

      :deep(.el-input__inner) {
        font-size: 18px;
        letter-spacing: 5px;
        text-align: center;
        font-weight: bold;
      }
    }

    .hint-alert {
      margin-bottom: 15px;
    }

    .countdown {
      text-align: center;

      .countdown-text {
        display: block;
        margin-top: 10px;
        font-size: 14px;
        color: #606266;
      }
    }

    .auto-recognizing {
      margin-top: 20px;
      padding: 20px;
      background: #F5F7FA;
      border-radius: 4px;

      .auto-progress {
        margin: 20px 0;
      }

      .auto-message {
        text-align: center;
        color: #606266;
        margin: 10px 0 0;
      }
    }
  }
}
</style>
```

---

#### 步骤4.2: 增强后端验证码处理策略（8小时）

**文件**: `backend/app/utils/captcha_solver_enhanced.py`

```python
"""
增强验证码求解器 - 支持多种策略
"""
import asyncio
import base64
import aiohttp
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from ..utils.logger import logger
from ..config import settings


class CaptchaSolverEnhanced:
    """增强的验证码求解器"""
    
    def __init__(self):
        self.twocaptcha_api_key = settings.captcha_2captcha_api_key
        self.ddddocr_available = False
        self.strategy = 'auto'  # auto | manual | 2captcha | ddddocr
        
        # 尝试导入ddddocr
        try:
            import ddddocr
            self.ocr = ddddocr.DdddOcr()
            self.ddddocr_available = True
            logger.info("✅ ddddocr本地OCR已加载")
        except ImportError:
            logger.warning("⚠️ ddddocr未安装，无法使用本地OCR识别")
    
    async def detect_capabilities(self) -> Dict[str, bool]:
        """
        检测可用的验证码识别能力
        
        Returns:
            {
                'auto_available': bool,  # 2Captcha可用
                'local_available': bool,  # 本地OCR可用
                'manual_available': bool  # 手动输入可用（总是True）
            }
        """
        capabilities = {
            'manual_available': True,
            'local_available': self.ddddocr_available,
            'auto_available': False
        }
        
        # 检测2Captcha余额
        if self.twocaptcha_api_key:
            try:
                balance = await self._check_2captcha_balance()
                capabilities['auto_available'] = balance > 0
                logger.info(f"2Captcha余额: ${balance}")
            except Exception as e:
                logger.error(f"检测2Captcha失败: {str(e)}")
        
        return capabilities
    
    async def solve(
        self,
        image_base64: str,
        method: Optional[str] = None,
        callback: Optional[callable] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        智能求解验证码
        
        Args:
            image_base64: Base64编码的图片
            method: 指定方法 ('2captcha' | 'ddddocr' | 'manual')，None则自动选择
            callback: 回调函数（用于手动输入）
            
        Returns:
            (成功, 验证码, 错误信息)
        """
        # 如果指定了方法，直接使用
        if method:
            return await self._solve_with_method(image_base64, method, callback)
        
        # 自动选择策略
        capabilities = await self.detect_capabilities()
        
        # 优先级: 2Captcha > ddddocr > 手动输入
        if capabilities['auto_available']:
            logger.info("使用2Captcha自动识别")
            success, code, error = await self._solve_with_2captcha(image_base64)
            
            if success:
                return True, code, None
            else:
                logger.warning(f"2Captcha识别失败: {error}，切换到本地OCR")
        
        if capabilities['local_available']:
            logger.info("使用本地OCR识别")
            success, code, error = await self._solve_with_ddddocr(image_base64)
            
            if success:
                return True, code, None
            else:
                logger.warning(f"本地OCR识别失败: {error}，切换到手动输入")
        
        # 最后使用手动输入
        logger.info("使用手动输入模式")
        return await self._solve_with_manual(image_base64, callback)
    
    async def _solve_with_method(
        self,
        image_base64: str,
        method: str,
        callback: Optional[callable] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """使用指定方法求解"""
        if method == '2captcha':
            return await self._solve_with_2captcha(image_base64)
        elif method == 'ddddocr':
            return await self._solve_with_ddddocr(image_base64)
        elif method == 'manual':
            return await self._solve_with_manual(image_base64, callback)
        else:
            return False, None, f"未知方法: {method}"
    
    async def _solve_with_2captcha(
        self,
        image_base64: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """使用2Captcha求解"""
        if not self.twocaptcha_api_key:
            return False, None, "2Captcha API Key未配置"
        
        try:
            from twocaptcha import TwoCaptcha
            
            solver = TwoCaptcha(self.twocaptcha_api_key)
            
            # 提交任务
            logger.info("提交验证码到2Captcha...")
            result = await asyncio.to_thread(
                solver.normal,
                image_base64
            )
            
            code = result['code']
            logger.info(f"✅ 2Captcha识别成功: {code}")
            
            return True, code, None
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ 2Captcha识别失败: {error_msg}")
            
            # 检查是否是余额不足
            if 'insufficient' in error_msg.lower() or 'balance' in error_msg.lower():
                return False, None, "2Captcha余额不足"
            
            return False, None, error_msg
    
    async def _solve_with_ddddocr(
        self,
        image_base64: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """使用ddddocr本地OCR求解"""
        if not self.ddddocr_available:
            return False, None, "ddddocr未安装"
        
        try:
            # 解码图片
            image_bytes = base64.b64decode(image_base64)
            
            # OCR识别
            logger.info("使用ddddocr识别验证码...")
            code = await asyncio.to_thread(
                self.ocr.classification,
                image_bytes
            )
            
            # 清理结果（去除空格、特殊字符）
            code = ''.join(filter(str.isalnum, code))
            
            if not code or len(code) < 4:
                return False, None, f"识别结果不合法: {code}"
            
            logger.info(f"✅ ddddocr识别成功: {code}")
            return True, code, None
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ ddddocr识别失败: {error_msg}")
            return False, None, error_msg
    
    async def _solve_with_manual(
        self,
        image_base64: str,
        callback: Optional[callable] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """手动输入模式"""
        if not callback:
            return False, None, "未提供手动输入回调函数"
        
        try:
            logger.info("等待用户手动输入验证码...")
            
            # 调用回调函数（通常是弹出对话框）
            code = await callback(image_base64)
            
            if not code:
                return False, None, "用户取消输入"
            
            logger.info(f"✅ 用户输入验证码: {code}")
            return True, code, None
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ 手动输入失败: {error_msg}")
            return False, None, error_msg
    
    async def _check_2captcha_balance(self) -> float:
        """检查2Captcha余额"""
        if not self.twocaptcha_api_key:
            return 0.0
        
        url = f"https://2captcha.com/res.php?key={self.twocaptcha_api_key}&action=getbalance"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    text = await response.text()
                    return float(text)
        except Exception as e:
            logger.error(f"检查2Captcha余额失败: {str(e)}")
            return 0.0
    
    def set_strategy(self, strategy: str):
        """
        设置验证码求解策略
        
        Args:
            strategy: 'auto' | '2captcha' | 'ddddocr' | 'manual'
        """
        valid_strategies = ['auto', '2captcha', 'ddddocr', 'manual']
        if strategy not in valid_strategies:
            raise ValueError(f"无效策略，可选: {valid_strategies}")
        
        self.strategy = strategy
        logger.info(f"验证码求解策略已设置为: {strategy}")


# 全局实例
captcha_solver_enhanced = CaptchaSolverEnhanced()
```

---

#### 步骤4.3: 创建验证码处理API（4小时）

**文件**: `backend/app/api/captcha_api.py`

```python
"""
验证码处理API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..utils.captcha_solver_enhanced import captcha_solver_enhanced
from ..utils.logger import logger

router = APIRouter(prefix="/api/captcha", tags=["验证码"])


class CaptchaRecognizeRequest(BaseModel):
    """验证码识别请求"""
    image: str  # Base64编码的图片
    method: Optional[str] = None  # 指定方法: 2captcha | ddddocr | manual


class CaptchaRecognizeResponse(BaseModel):
    """验证码识别响应"""
    success: bool
    code: Optional[str] = None
    message: Optional[str] = None
    method_used: Optional[str] = None


@router.get("/capabilities")
async def get_captcha_capabilities():
    """
    获取验证码识别能力
    
    Returns:
        {
            "auto_available": bool,  # 2Captcha可用
            "local_available": bool,  # 本地OCR可用
            "manual_available": bool  # 手动输入可用
        }
    """
    try:
        capabilities = await captcha_solver_enhanced.detect_capabilities()
        return capabilities
    except Exception as e:
        logger.error(f"检测验证码能力失败: {str(e)}")
        raise HTTPException(status_code=500, detail="检测失败")


@router.post("/recognize")
async def recognize_captcha(request: CaptchaRecognizeRequest) -> CaptchaRecognizeResponse:
    """
    识别验证码
    
    Args:
        request: 包含验证码图片和可选的识别方法
        
    Returns:
        识别结果
    """
    try:
        logger.info(f"收到验证码识别请求，方法: {request.method or 'auto'}")
        
        # 调用求解器
        success, code, error = await captcha_solver_enhanced._solve_with_method(
            image_base64=request.image,
            method=request.method or 'auto',
            callback=None  # API模式不支持手动输入回调
        )
        
        return CaptchaRecognizeResponse(
            success=success,
            code=code,
            message=error if not success else "识别成功",
            method_used=request.method or 'auto'
        )
        
    except Exception as e:
        logger.error(f"验证码识别异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategy")
async def set_strategy(strategy: str):
    """
    设置验证码求解策略
    
    Args:
        strategy: 'auto' | '2captcha' | 'ddddocr' | 'manual'
    """
    try:
        captcha_solver_enhanced.set_strategy(strategy)
        return {"success": True, "strategy": strategy}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/balance")
async def get_2captcha_balance():
    """
    查询2Captcha余额
    
    Returns:
        {"balance": float}
    """
    try:
        balance = await captcha_solver_enhanced._check_2captcha_balance()
        return {
            "balance": balance,
            "available": balance > 0,
            "warning": balance < 1.0  # 余额低于$1时警告
        }
    except Exception as e:
        logger.error(f"查询2Captcha余额失败: {str(e)}")
        raise HTTPException(status_code=500, detail="查询失败")
```

由于内容非常庞大，我将继续创建剩余的优化手册...

