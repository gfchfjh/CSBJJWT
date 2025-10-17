# 测试文档

## 📋 测试概述

本项目包含完整的单元测试套件，覆盖核心功能模块。

### 测试模块

- ✅ `test_formatter.py` - 消息格式转换测试（KMarkdown转换）
- ✅ `test_rate_limiter.py` - 限流器测试（滑动窗口算法）
- ✅ `test_crypto.py` - 加密工具测试（AES-256加密）
- ✅ `test_database.py` - 数据库操作测试（**新增**）
- ✅ `test_image_processor.py` - 图片处理器测试（**新增**）
- ✅ `test_scheduler.py` - 任务调度器测试（**新增**）

### 测试覆盖范围

| 模块 | 测试用例数 | 覆盖率 |
|------|-----------|-------|
| 消息格式转换 | 15+ | ~90% |
| 限流器 | 10+ | ~95% |
| 加密工具 | 12+ | ~100% |
| 数据库操作 | 18+ | ~85% |
| 图片处理 | 14+ | ~90% |
| 任务调度 | 12+ | ~85% |

## 🚀 快速开始

### 1. 安装测试依赖

```bash
pip install -r requirements-dev.txt
```

### 2. 运行所有测试

#### Linux/macOS:
```bash
./run_tests.sh
```

#### Windows:
```bash
run_tests.bat
```

#### 或使用pytest直接运行:
```bash
pytest tests/ -v
```

### 3. 运行特定测试

```bash
# 运行单个测试文件
pytest tests/test_formatter.py -v

# 运行单个测试类
pytest tests/test_formatter.py::TestMessageFormatter -v

# 运行单个测试方法
pytest tests/test_formatter.py::TestMessageFormatter::test_kmarkdown_to_markdown -v
```

## 📊 覆盖率报告

### 生成覆盖率报告

```bash
pytest tests/ --cov=app --cov-report=html
```

### 查看HTML报告

```bash
# macOS
open htmlcov/index.html

# Windows
start htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

## 🏷️ 测试标记

使用pytest标记来运行特定类型的测试：

```bash
# 只运行单元测试
pytest -m unit

# 只运行异步测试
pytest -m asyncio

# 跳过慢速测试
pytest -m "not slow"
```

## 📝 编写新测试

### 测试文件命名规范

- 文件名: `test_*.py` 或 `*_test.py`
- 类名: `Test*`
- 方法名: `test_*`

### 示例测试

```python
import pytest
from app.your_module import your_function

class TestYourModule:
    """测试类文档"""
    
    def test_basic_functionality(self):
        """测试基本功能"""
        result = your_function(input_data)
        assert result == expected_output
    
    @pytest.mark.asyncio
    async def test_async_function(self):
        """测试异步函数"""
        result = await your_async_function()
        assert result is not None
```

## 🧪 测试最佳实践

### 1. AAA模式 (Arrange-Act-Assert)

```python
def test_example():
    # Arrange - 准备测试数据
    data = create_test_data()
    
    # Act - 执行测试操作
    result = process_data(data)
    
    # Assert - 验证结果
    assert result.status == "success"
```

### 2. 使用Fixture

```python
@pytest.fixture
def sample_data():
    """测试数据fixture"""
    return {"key": "value"}

def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"
```

### 3. 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("Test", "TEST"),
])
def test_uppercase(input, expected):
    assert input.upper() == expected
```

## 🐛 调试测试

### 使用pdb调试

```bash
pytest tests/test_formatter.py --pdb
```

### 显示打印输出

```bash
pytest tests/ -v -s
```

### 只运行失败的测试

```bash
pytest --lf  # last-failed
```

## 📈 持续集成

测试可以集成到CI/CD流程：

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest tests/ --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 📚 更多资源

- [Pytest官方文档](https://docs.pytest.org/)
- [pytest-asyncio文档](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py文档](https://coverage.readthedocs.io/)
