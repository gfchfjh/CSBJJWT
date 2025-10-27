# API认证使用指南

## 概述

API认证已添加到后端，但默认**未强制启用**。你可以通过环境变量启用它。

## 启用认证

### 1. 生成Token

```bash
# 方法1：自动生成（Python）
python -c "import secrets; print(secrets.token_urlsafe(48))"

# 方法2：通过API（仅开发环境）
curl http://localhost:9527/api/auth/generate-token

# 方法3：使用OpenSSL
openssl rand -base64 48
```

### 2. 配置Token

创建或编辑 `.env` 文件：

```env
# 必须设置此环境变量以启用API认证
API_TOKEN=your-generated-token-here

# 可选：自定义Token请求头名称（默认X-API-Token）
API_TOKEN_HEADER=X-API-Token
```

### 3. 重启后端

```bash
cd backend
python -m app.main
```

启动时会显示：
```
✅ API认证已启用（Token: xxxxxxxxxx...）
```

## 在路由中使用认证

### 方式1：保护整个路由（推荐）

```python
from fastapi import APIRouter, Depends
from ..utils.auth import verify_api_token

router = APIRouter(
    prefix="/api/protected",
    tags=["受保护的API"],
    dependencies=[Depends(verify_api_token)]  # 整个路由需要认证
)

@router.get("/data")
async def get_protected_data():
    """所有该路由下的接口都需要Token"""
    return {"data": "protected"}
```

### 方式2：保护单个接口

```python
from fastapi import APIRouter, Depends
from ..utils.auth import verify_api_token

router = APIRouter(prefix="/api/mixed", tags=["混合API"])

@router.get("/public")
async def public_endpoint():
    """无需Token"""
    return {"message": "public"}

@router.get("/private", dependencies=[Depends(verify_api_token)])
async def private_endpoint():
    """需要Token"""
    return {"message": "private"}
```

### 方式3：可选认证

```python
from fastapi import APIRouter, Depends
from typing import Optional
from ..utils.auth import optional_api_token

router = APIRouter(prefix="/api/optional", tags=["可选认证"])

@router.get("/data")
async def get_data(token: Optional[str] = Depends(optional_api_token)):
    """
    如果提供Token则验证，否则返回受限数据
    """
    if token:
        return {"data": "full_data", "user": "authenticated"}
    else:
        return {"data": "limited_data", "user": "guest"}
```

## 前端集成

### Axios配置

```javascript
// frontend/src/api/index.js
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:9527',
  timeout: 30000
})

// 添加Token拦截器
api.interceptors.request.use(config => {
  const token = localStorage.getItem('api_token')
  if (token) {
    config.headers['X-API-Token'] = token
  }
  return config
})

export default api
```

### Vue组件中使用

```vue
<script setup>
import api from '@/api'
import { ref } from 'vue'

const token = ref(localStorage.getItem('api_token') || '')

async function saveToken() {
  localStorage.setItem('api_token', token.value)
  // 测试Token
  try {
    await api.get('/api/system/status')
    alert('Token有效')
  } catch (error) {
    alert('Token无效')
  }
}
</script>

<template>
  <div>
    <input v-model="token" placeholder="输入API Token" />
    <button @click="saveToken">保存Token</button>
  </div>
</template>
```

## 当前认证状态

### 已保护的路由（需要Token）

**当前：暂无（所有路由默认公开）**

建议保护以下路由：
- ❌ `/api/accounts/*` - 账号管理
- ❌ `/api/bots/*` - Bot配置
- ❌ `/api/mappings/*` - 频道映射
- ❌ `/api/system/*` - 系统管理

### 公开路由（无需Token）

- ✅ `/` - 根路径
- ✅ `/health` - 健康检查
- ✅ `/api/auth/check` - 检查认证状态
- ✅ `/api/auth/generate-token` - 生成Token（仅开发环境）

## 添加认证到现有路由

### 示例：保护accounts路由

编辑 `backend/app/api/accounts.py`：

```python
# 在文件开头导入
from fastapi import Depends
from ..utils.auth import verify_api_token

# 修改router定义
router = APIRouter(
    prefix="/api/accounts",
    tags=["账号管理"],
    dependencies=[Depends(verify_api_token)]  # 添加这行
)
```

## 测试认证

### 1. 检查认证状态

```bash
curl http://localhost:9527/api/auth/check
```

### 2. 无Token访问（应该成功，因为暂未强制）

```bash
curl http://localhost:9527/api/system/status
```

### 3. 启用认证后，无Token访问（应该401）

```bash
curl http://localhost:9527/api/accounts
# {"detail":"Missing API Token"}
```

### 4. 有Token访问（应该成功）

```bash
curl -H "X-API-Token: your-token-here" http://localhost:9527/api/accounts
```

## 生产环境建议

1. **必须启用认证**：设置`API_TOKEN`环境变量
2. **定期轮换Token**：每月更换一次
3. **使用HTTPS**：避免Token在传输中泄露
4. **限制CORS来源**：不要使用`allow_origins=["*"]`
5. **监控失败登录**：记录Token验证失败的IP

## 常见问题

### Q: 为什么默认不启用认证？

A: 为了方便开发和部署。生产环境**强烈建议**启用。

### Q: Token泄露了怎么办？

A: 立即生成新Token，更新`.env`文件，重启应用。

### Q: 可以使用JWT吗？

A: 当前使用简单的Token认证。如需JWT，可以修改`utils/auth.py`实现。

### Q: 前端如何存储Token？

A: 建议使用`localStorage`或`sessionStorage`，不要硬编码。

## 下一步

1. 决定哪些路由需要保护
2. 在相应路由添加`dependencies=[Depends(verify_api_token)]`
3. 更新前端代码，添加Token管理界面
4. 测试所有受保护的端点

---

*最后更新：2025-10-16*
