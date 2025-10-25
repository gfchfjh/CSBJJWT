"""
Redis 准备脚本（完整版）
P0-16: Redis 嵌入式集成优化

功能：
1. 下载/准备 Redis 二进制文件（跨平台）
2. 生成 redis.conf 配置文件
3. 验证 Redis 可用性
4. 准备打包所需的 Redis 文件
"""
import os
import sys
import subprocess
import shutil
import urllib.request
import zipfile
import tarfile
from pathlib import Path


class RedisPreparer:
    """Redis 准备器"""
    
    def __init__(self):
        self.redis_dir = Path(__file__).parent.parent / "redis"
        self.redis_dir.mkdir(parents=True, exist_ok=True)
        
        self.build_redis_dir = Path(__file__).parent.parent / "dist/redis"
        self.build_redis_dir.mkdir(parents=True, exist_ok=True)
        
        # Redis 版本
        self.redis_version = "7.2.5"
        
    def get_redis_download_url(self) -> tuple[str, str]:
        """获取 Redis 下载 URL"""
        if sys.platform == "win32":
            # Windows: 使用 Memurai 或 Redis for Windows
            url = "https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip"
            filename = "redis-windows.zip"
        elif sys.platform == "darwin":
            # macOS: 从官方源码编译或使用预编译版本
            url = f"https://download.redis.io/releases/redis-{self.redis_version}.tar.gz"
            filename = f"redis-{self.redis_version}.tar.gz"
        else:
            # Linux: 官方源码
            url = f"https://download.redis.io/releases/redis-{self.redis_version}.tar.gz"
            filename = f"redis-{self.redis_version}.tar.gz"
        
        return url, filename
    
    def download_redis(self) -> bool:
        """下载 Redis"""
        try:
            url, filename = self.get_redis_download_url()
            download_path = self.redis_dir / filename
            
            if download_path.exists():
                print(f"✅ Redis 文件已存在: {download_path}")
                return True
            
            print(f"📥 下载 Redis: {url}")
            print(f"   保存到: {download_path}")
            
            urllib.request.urlretrieve(url, download_path)
            
            print(f"✅ Redis 下载完成: {download_path}")
            return True
            
        except Exception as e:
            print(f"❌ Redis 下载失败: {e}")
            return False
    
    def extract_redis(self) -> bool:
        """解压 Redis"""
        try:
            _, filename = self.get_redis_download_url()
            download_path = self.redis_dir / filename
            
            if not download_path.exists():
                print(f"❌ Redis 文件不存在: {download_path}")
                return False
            
            print(f"📦 解压 Redis: {download_path}")
            
            if filename.endswith('.zip'):
                # Windows ZIP
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    zip_ref.extractall(self.redis_dir)
            else:
                # Linux/macOS tar.gz
                with tarfile.open(download_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(self.redis_dir)
            
            print(f"✅ Redis 解压完成")
            return True
            
        except Exception as e:
            print(f"❌ Redis 解压失败: {e}")
            return False
    
    def compile_redis(self) -> bool:
        """编译 Redis（Linux/macOS）"""
        if sys.platform == "win32":
            print("⏭️  Windows 跳过编译")
            return True
        
        try:
            redis_source_dir = self.redis_dir / f"redis-{self.redis_version}"
            if not redis_source_dir.exists():
                print(f"❌ Redis 源码目录不存在: {redis_source_dir}")
                return False
            
            print(f"🔨 编译 Redis（源码目录: {redis_source_dir}）")
            
            # 执行 make
            result = subprocess.run(
                ["make"],
                cwd=redis_source_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                print("✅ Redis 编译成功")
                return True
            else:
                print(f"❌ Redis 编译失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Redis 编译超时（5分钟）")
            return False
        except Exception as e:
            print(f"❌ Redis 编译异常: {e}")
            return False
    
    def copy_redis_binaries(self) -> bool:
        """复制 Redis 二进制文件到构建目录"""
        try:
            if sys.platform == "win32":
                # Windows: 复制 exe 文件
                source_dir = self.redis_dir / "Redis-x64-5.0.14.1"
                if not source_dir.exists():
                    # 尝试其他可能的目录
                    possible_dirs = list(self.redis_dir.glob("Redis-*"))
                    if possible_dirs:
                        source_dir = possible_dirs[0]
                    else:
                        print(f"❌ 未找到 Redis Windows 目录")
                        return False
                
                files_to_copy = [
                    "redis-server.exe",
                    "redis-cli.exe",
                    "redis-check-aof.exe",
                    "redis-check-rdb.exe"
                ]
            else:
                # Linux/macOS: 复制编译后的文件
                source_dir = self.redis_dir / f"redis-{self.redis_version}/src"
                files_to_copy = [
                    "redis-server",
                    "redis-cli",
                    "redis-check-aof",
                    "redis-check-rdb"
                ]
            
            print(f"📦 复制 Redis 二进制文件: {source_dir} -> {self.build_redis_dir}")
            
            for filename in files_to_copy:
                source_file = source_dir / filename
                target_file = self.build_redis_dir / filename
                
                if source_file.exists():
                    shutil.copy2(source_file, target_file)
                    
                    # Linux/macOS: 添加执行权限
                    if sys.platform != "win32":
                        os.chmod(target_file, 0o755)
                    
                    print(f"  ✅ {filename}")
                else:
                    print(f"  ⚠️  {filename} 不存在，跳过")
            
            print(f"✅ Redis 二进制文件已复制")
            return True
            
        except Exception as e:
            print(f"❌ 复制 Redis 失败: {e}")
            return False
    
    def generate_redis_config(self):
        """生成 redis.conf 配置文件"""
        config_content = """# Redis 配置文件（嵌入式版本）
# 自动生成，请勿手动修改

# 基础配置
port 6379
bind 127.0.0.1
protected-mode yes
timeout 0
tcp-keepalive 300

# 数据持久化
dir ./data/redis
dbfilename dump.rdb
save 900 1
save 300 10
save 60 10000

# 日志
loglevel notice
logfile "./data/redis/redis.log"

# 内存管理
maxmemory 256mb
maxmemory-policy allkeys-lru

# 安全
# requirepass your_password_here

# 禁用危险命令
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command KEYS ""
rename-command CONFIG ""

# 客户端
maxclients 100

# 慢查询日志
slowlog-log-slower-than 10000
slowlog-max-len 128
"""
        
        config_path = self.build_redis_dir / "redis.conf"
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"✅ Redis 配置文件已生成: {config_path}")
    
    def test_redis(self) -> bool:
        """测试 Redis 是否可用"""
        try:
            if sys.platform == "win32":
                redis_server = self.build_redis_dir / "redis-server.exe"
            else:
                redis_server = self.build_redis_dir / "redis-server"
            
            if not redis_server.exists():
                print(f"❌ Redis 服务器文件不存在: {redis_server}")
                return False
            
            print(f"🧪 测试 Redis: {redis_server} --version")
            
            result = subprocess.run(
                [str(redis_server), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ Redis 版本: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ Redis 测试失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Redis 测试异常: {e}")
            return False
    
    def prepare(self) -> bool:
        """准备 Redis（完整流程）"""
        print("=" * 60)
        print("🚀 开始准备 Redis")
        print("=" * 60)
        
        # 1. 下载 Redis
        print("\n📥 下载 Redis...")
        if not self.download_redis():
            return False
        
        # 2. 解压 Redis
        print("\n📦 解压 Redis...")
        if not self.extract_redis():
            return False
        
        # 3. 编译 Redis（Linux/macOS）
        if sys.platform != "win32":
            print("\n🔨 编译 Redis...")
            if not self.compile_redis():
                return False
        
        # 4. 复制二进制文件
        print("\n📦 复制 Redis 二进制文件...")
        if not self.copy_redis_binaries():
            return False
        
        # 5. 生成配置文件
        print("\n⚙️  生成 Redis 配置文件...")
        self.generate_redis_config()
        
        # 6. 测试 Redis
        print("\n🧪 测试 Redis...")
        if not self.test_redis():
            print("⚠️  Redis 测试失败，但继续...")
        
        print("\n" + "=" * 60)
        print("✅ Redis 准备完成！")
        print("=" * 60)
        
        return True


def main():
    """主函数"""
    preparer = RedisPreparer()
    success = preparer.prepare()
    
    if success:
        print("\n✅ 可以继续进行打包流程")
        sys.exit(0)
    else:
        print("\n❌ 准备失败，请检查错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()
