import sys
import os
import asyncio

# Windows Playwright 兼容性修复 - 全局设置
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print("✅ 已全局设置 WindowsSelectorEventLoopPolicy")

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=9527, reload=True)
