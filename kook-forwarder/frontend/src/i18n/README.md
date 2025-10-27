# 国际化 (i18n) 使用指南

本项目使用 `vue-i18n` 实现多语言支持。

## 📁 目录结构

```
src/i18n/
├── index.js                 # i18n 配置入口
├── locales/                 # 语言包目录
│   ├── zh-CN.json          # 简体中文
│   └── en-US.json          # 英文
└── README.md               # 本文件
```

## 🚀 使用方法

### 1. 在 main.js 中引入

```javascript
import { createApp } from 'vue'
import i18n from './i18n'
import App from './App.vue'

const app = createApp(App)
app.use(i18n)
app.mount('#app')
```

### 2. 在组件中使用

#### 在模板中使用
```vue
<template>
  <div>
    <!-- 基础用法 -->
    <h1>{{ $t('app.title') }}</h1>
    
    <!-- 带参数 -->
    <p>{{ $t('common.welcome', { name: 'User' }) }}</p>
    
    <!-- 复数形式 -->
    <p>{{ $t('common.items', { count: 5 }) }}</p>
  </div>
</template>
```

#### 在脚本中使用
```vue
<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// 使用翻译
const title = t('app.title')

// 带参数
const message = t('common.welcome', { name: 'User' })
</script>
```

### 3. 切换语言

```vue
<script setup>
import { setLanguage } from '@/i18n'

// 切换到英文
setLanguage('en-US')

// 切换到中文
setLanguage('zh-CN')
</script>
```

### 4. 使用语言切换组件

```vue
<template>
  <LanguageSwitcher />
</template>

<script setup>
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
</script>
```

## 📝 添加新的翻译

### 1. 在语言包中添加键值对

**zh-CN.json**:
```json
{
  "myModule": {
    "title": "我的模块",
    "description": "这是一个新模块"
  }
}
```

**en-US.json**:
```json
{
  "myModule": {
    "title": "My Module",
    "description": "This is a new module"
  }
}
```

### 2. 在组件中使用

```vue
<template>
  <div>
    <h2>{{ $t('myModule.title') }}</h2>
    <p>{{ $t('myModule.description') }}</p>
  </div>
</template>
```

## 🌍 添加新语言

### 1. 创建新的语言包文件

在 `locales/` 目录下创建新文件，例如 `ja-JP.json`（日语）：

```json
{
  "app": {
    "title": "KOOKメッセージ転送システム"
  }
}
```

### 2. 在 index.js 中导入并注册

```javascript
import jaJP from './locales/ja-JP.json'

const i18n = createI18n({
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS,
    'ja-JP': jaJP  // 添加新语言
  }
})
```

### 3. 更新语言列表

在 `index.js` 的 `getSupportedLanguages` 函数中添加：

```javascript
export function getSupportedLanguages() {
  return [
    { value: 'zh-CN', label: '简体中文', icon: '🇨🇳' },
    { value: 'en-US', label: 'English', icon: '🇺🇸' },
    { value: 'ja-JP', label: '日本語', icon: '🇯🇵' }  // 添加
  ]
}
```

## 💡 最佳实践

### 1. 使用嵌套结构组织翻译

```json
{
  "user": {
    "profile": {
      "name": "姓名",
      "email": "邮箱"
    },
    "settings": {
      "privacy": "隐私设置"
    }
  }
}
```

### 2. 使用有意义的键名

❌ 不推荐：
```json
{
  "text1": "保存",
  "text2": "取消"
}
```

✅ 推荐：
```json
{
  "common": {
    "save": "保存",
    "cancel": "取消"
  }
}
```

### 3. 复用公共翻译

```json
{
  "common": {
    "save": "保存",
    "cancel": "取消",
    "delete": "删除"
  }
}
```

在组件中：
```vue
<el-button>{{ $t('common.save') }}</el-button>
<el-button>{{ $t('common.cancel') }}</el-button>
```

### 4. 带参数的翻译

语言包：
```json
{
  "message": {
    "greeting": "你好，{name}！",
    "itemCount": "你有 {count} 个项目"
  }
}
```

使用：
```vue
<p>{{ $t('message.greeting', { name: '张三' }) }}</p>
<p>{{ $t('message.itemCount', { count: 5 }) }}</p>
```

## 🔧 与 Element Plus 集成

确保 Element Plus 的语言也跟随切换：

```javascript
// main.js
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import en from 'element-plus/es/locale/lang/en'

const elementLocale = computed(() => {
  return i18n.global.locale.value === 'zh-CN' ? zhCn : en
})

app.use(ElementPlus, { locale: elementLocale })
```

## 📚 更多资源

- [Vue I18n 官方文档](https://vue-i18n.intlify.dev/)
- [Element Plus 国际化](https://element-plus.org/zh-CN/guide/i18n.html)

## 🎯 当前状态

- ✅ 框架已集成
- ✅ 中文语言包完整
- ⚠️ 英文语言包基础完成（需要完善）
- ❌ 其他语言待添加

## 📋 TODO

- [ ] 完善英文翻译（覆盖所有页面）
- [ ] 添加日语支持
- [ ] 添加繁体中文支持
- [ ] 与 Element Plus 语言同步切换
- [ ] 添加语言切换动画效果
