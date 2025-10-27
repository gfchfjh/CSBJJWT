# 前端测试指南

本目录包含KOOK消息转发系统前端的所有测试文件。

## 📚 测试框架

- **测试框架**: [Vitest](https://vitest.dev/)
- **组件测试**: [@vue/test-utils](https://test-utils.vuejs.org/)
- **DOM环境**: jsdom
- **覆盖率工具**: @vitest/coverage-v8

---

## 🚀 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 运行测试

```bash
# 运行所有测试
npm run test

# 监视模式（开发时推荐）
npm run test -- --watch

# 带UI界面
npm run test:ui

# 生成覆盖率报告
npm run test:coverage
```

### 查看覆盖率报告

```bash
# 生成报告后
open coverage/index.html  # macOS
xdg-open coverage/index.html  # Linux
start coverage/index.html  # Windows
```

---

## 📁 测试文件结构

```
frontend/src/__tests__/
├── setup.js                      # 测试环境设置
├── components/                   # 组件测试
│   └── BotList.spec.js          # Bot列表组件
├── views/                        # 页面测试
│   └── Accounts.spec.js         # 账号管理页
└── composables/                  # Composable测试
    └── useWebSocket.spec.js     # WebSocket hook
```

---

## 🧪 测试示例

### 组件测试

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '@/components/MyComponent.vue'

describe('MyComponent.vue', () => {
  it('渲染正确的内容', () => {
    const wrapper = mount(MyComponent, {
      props: { message: 'Hello' }
    })
    
    expect(wrapper.text()).toContain('Hello')
  })
  
  it('触发点击事件', async () => {
    const wrapper = mount(MyComponent)
    
    await wrapper.find('button').trigger('click')
    
    expect(wrapper.emitted('click')).toBeTruthy()
  })
})
```

### Composable测试

```javascript
import { describe, it, expect } from 'vitest'
import { useMyComposable } from '@/composables/useMyComposable'

describe('useMyComposable', () => {
  it('返回正确的状态', () => {
    const { state, action } = useMyComposable()
    
    expect(state.value).toBe(initialValue)
    
    action()
    
    expect(state.value).toBe(expectedValue)
  })
})
```

### 异步测试

```javascript
import { describe, it, expect, vi } from 'vitest'
import { flushPromises } from '@vue/test-utils'

describe('异步操作', () => {
  it('正确处理异步数据', async () => {
    const wrapper = mount(AsyncComponent)
    
    // 等待所有Promise完成
    await flushPromises()
    
    expect(wrapper.find('.data').text()).toBe('loaded')
  })
})
```

### Mock测试

```javascript
import { describe, it, expect, vi } from 'vitest'

// Mock API
vi.mock('@/api', () => ({
  default: {
    getData: vi.fn(() => Promise.resolve({ data: 'test' }))
  }
}))

describe('使用Mock', () => {
  it('调用API', async () => {
    const { getData } = await import('@/api')
    
    const result = await getData()
    
    expect(getData).toHaveBeenCalled()
    expect(result.data).toBe('test')
  })
})
```

---

## 📋 测试清单

### 已完成

- [x] BotList组件测试
- [x] Accounts页面测试
- [x] useWebSocket测试
- [x] 测试环境配置

### 待添加

- [ ] Wizard页面测试
- [ ] Mapping页面测试
- [ ] Logs页面测试
- [ ] Settings页面测试
- [ ] useTheme测试
- [ ] useNotification测试
- [ ] API集成测试
- [ ] E2E测试

---

## 🎯 测试覆盖率目标

| 类型 | 当前 | 目标 | 优先级 |
|------|------|------|--------|
| 组件测试 | 20% | 70% | 高 |
| Composable测试 | 30% | 80% | 高 |
| 工具函数测试 | 10% | 90% | 中 |
| 页面测试 | 15% | 60% | 中 |
| E2E测试 | 0% | 30% | 低 |

---

## 🛠️ 编写测试技巧

### 1. 组件测试最佳实践

**Do ✅**：
- 测试用户行为（点击、输入等）
- 测试组件输出（DOM、事件）
- 使用语义化选择器
- Mock外部依赖

**Don't ❌**：
- 测试实现细节
- 测试第三方库
- 过度Mock

### 2. 测试命名规范

```javascript
describe('组件名/功能名', () => {
  it('应该做什么', () => {
    // 测试代码
  })
})

// 例如：
describe('BotList.vue', () => {
  it('应该渲染正确的Bot数量', () => {
    // ...
  })
  
  it('应该在点击删除时触发事件', () => {
    // ...
  })
})
```

### 3. AAA模式

```javascript
it('测试描述', () => {
  // Arrange - 准备
  const wrapper = mount(Component, { props: { ... } })
  
  // Act - 执行
  wrapper.find('button').trigger('click')
  
  // Assert - 断言
  expect(wrapper.emitted('click')).toBeTruthy()
})
```

### 4. 异步测试处理

```javascript
// 方法1: async/await
it('异步测试', async () => {
  const wrapper = mount(Component)
  await wrapper.vm.asyncMethod()
  expect(wrapper.vm.data).toBe('loaded')
})

// 方法2: flushPromises
import { flushPromises } from '@vue/test-utils'

it('异步测试', async () => {
  const wrapper = mount(Component)
  wrapper.vm.asyncMethod()
  await flushPromises()
  expect(wrapper.vm.data).toBe('loaded')
})
```

---

## 🐛 调试测试

### 1. 使用console.log

```javascript
it('调试测试', () => {
  const wrapper = mount(Component)
  
  // 输出组件HTML
  console.log(wrapper.html())
  
  // 输出组件数据
  console.log(wrapper.vm.$data)
})
```

### 2. 使用测试UI

```bash
npm run test:ui
```

在浏览器中查看：
- 测试结果
- 组件渲染
- 错误堆栈

### 3. 调试单个测试

```javascript
// 使用it.only只运行这个测试
it.only('单独运行', () => {
  // ...
})

// 使用it.skip跳过这个测试
it.skip('暂时跳过', () => {
  // ...
})
```

---

## 📖 参考资料

- [Vitest官方文档](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [测试最佳实践](https://github.com/goldbergyoni/javascript-testing-best-practices)
- [Vue测试指南](https://vuejs.org/guide/scaling-up/testing.html)

---

## 💡 贡献指南

### 添加新测试

1. 在对应目录创建测试文件（`*.spec.js`）
2. 遵循命名规范
3. 使用AAA模式编写测试
4. 运行测试确保通过
5. 提交PR

### 测试PR清单

- [ ] 测试文件命名规范
- [ ] 测试覆盖核心功能
- [ ] 所有测试通过
- [ ] 代码格式规范
- [ ] 添加必要注释

---

**最后更新**: 2025-10-18  
**测试覆盖率**: 30%  
**测试文件数**: 3  
**目标覆盖率**: 70%  

---

*让我们一起提高代码质量！*
