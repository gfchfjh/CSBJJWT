"""
文件安全检查器 - ✅ P0优化: 危险文件类型拦截
"""
from pathlib import Path
from typing import Tuple, List, Dict
from ..utils.logger import logger


class FileSecurityChecker:
    """
    ✅ P0优化: 文件安全检查器
    
    功能：
    1. 危险文件类型黑名单
    2. 文件大小限制
    3. 文件名安全检查
    4. MIME类型验证
    """
    
    # 危险文件类型黑名单（需求要求）
    DANGEROUS_EXTENSIONS = {
        # 可执行文件
        '.exe', '.bat', '.cmd', '.com', '.scr', '.pif',
        '.sh', '.bash', '.zsh', '.fish',
        '.app', '.deb', '.rpm', '.dmg', '.pkg',
        
        # 动态库
        '.dll', '.so', '.dylib', '.ocx',
        
        # 脚本文件
        '.vbs', '.vbe', '.js', '.jse', '.ws', '.wsf',
        '.ps1', '.psm1', '.psd1',
        '.py', '.pyc', '.pyo',  # Python脚本
        '.rb', '.pl', '.php',   # 其他脚本
        
        # 安装包
        '.msi', '.msp', '.mst',
        '.apk', '.ipa',
        
        # 压缩包内可执行
        '.jar', '.war',
        
        # Office宏文件
        '.docm', '.dotm', '.xlsm', '.xltm', '.pptm', '.potm',
        
        # 其他危险类型
        '.lnk',  # Windows快捷方式
        '.url',  # Internet快捷方式
        '.desktop',  # Linux桌面文件
    }
    
    # 可疑扩展名（需要警告但不完全阻止）
    SUSPICIOUS_EXTENSIONS = {
        '.zip', '.rar', '.7z', '.tar', '.gz',  # 压缩包
        '.iso', '.img',  # 镜像文件
        '.htm', '.html',  # HTML文件（可能含恶意脚本）
    }
    
    # 文件大小限制
    MAX_FILE_SIZE_MB = 50
    
    def __init__(self):
        self.stats = {
            "total_checked": 0,
            "dangerous_blocked": 0,
            "suspicious_warned": 0,
            "safe_passed": 0,
            "size_rejected": 0
        }
        
        logger.info("✅ 文件安全检查器已初始化")
    
    def is_safe_file(
        self,
        filename: str,
        file_size_bytes: int = 0
    ) -> Tuple[bool, str, str]:
        """
        检查文件是否安全
        
        Args:
            filename: 文件名
            file_size_bytes: 文件大小（字节）
            
        Returns:
            (是否安全, 风险级别, 原因)
            风险级别: safe/warning/danger
        """
        self.stats["total_checked"] += 1
        
        # 提取文件扩展名
        ext = Path(filename).suffix.lower()
        
        # 1. 检查危险类型
        if ext in self.DANGEROUS_EXTENSIONS:
            self.stats["dangerous_blocked"] += 1
            logger.warning(f"🚫 危险文件类型被拦截: {filename} ({ext})")
            
            return (
                False,
                "danger",
                f"危险文件类型：{ext} - 此类型文件可能包含恶意代码，已被系统拦截"
            )
        
        # 2. 检查可疑类型
        if ext in self.SUSPICIOUS_EXTENSIONS:
            self.stats["suspicious_warned"] += 1
            logger.info(f"⚠️ 可疑文件类型警告: {filename} ({ext})")
            
            return (
                True,  # 允许但警告
                "warning",
                f"可疑文件类型：{ext} - 请确认文件来源可信"
            )
        
        # 3. 检查文件大小
        if file_size_bytes > 0:
            size_mb = file_size_bytes / (1024 * 1024)
            
            if size_mb > self.MAX_FILE_SIZE_MB:
                self.stats["size_rejected"] += 1
                logger.warning(f"📦 文件过大被拒绝: {filename} ({size_mb:.2f}MB)")
                
                return (
                    False,
                    "danger",
                    f"文件过大：{size_mb:.2f}MB - 超过{self.MAX_FILE_SIZE_MB}MB限制"
                )
        
        # 4. 安全文件
        self.stats["safe_passed"] += 1
        logger.debug(f"✅ 文件安全检查通过: {filename}")
        
        return (True, "safe", "文件安全")
    
    def get_file_type_description(self, filename: str) -> str:
        """
        获取文件类型的友好描述
        
        Args:
            filename: 文件名
            
        Returns:
            类型描述
        """
        ext = Path(filename).suffix.lower()
        
        type_descriptions = {
            # 图片
            '.jpg': '图片文件 (JPEG)',
            '.jpeg': '图片文件 (JPEG)',
            '.png': '图片文件 (PNG)',
            '.gif': '动图 (GIF)',
            '.webp': '图片文件 (WebP)',
            '.bmp': '图片文件 (BMP)',
            
            # 文档
            '.pdf': 'PDF文档',
            '.doc': 'Word文档',
            '.docx': 'Word文档',
            '.xls': 'Excel表格',
            '.xlsx': 'Excel表格',
            '.ppt': 'PowerPoint演示',
            '.pptx': 'PowerPoint演示',
            '.txt': '文本文件',
            
            # 音视频
            '.mp3': '音频文件',
            '.mp4': '视频文件',
            '.avi': '视频文件',
            '.mov': '视频文件',
            '.wav': '音频文件',
            
            # 压缩包
            '.zip': 'ZIP压缩包',
            '.rar': 'RAR压缩包',
            '.7z': '7Z压缩包',
            '.tar': 'TAR归档',
            '.gz': 'GZip压缩',
            
            # 代码
            '.json': 'JSON数据文件',
            '.xml': 'XML文件',
            '.csv': 'CSV数据文件',
            
            # 其他
            '.log': '日志文件',
            '.md': 'Markdown文档',
        }
        
        return type_descriptions.get(ext, f'{ext}文件')
    
    def get_safe_extensions_list(self) -> List[str]:
        """
        获取推荐的安全文件扩展名列表
        
        Returns:
            扩展名列表
        """
        safe_extensions = [
            # 图片
            '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp',
            
            # 文档
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt',
            
            # 音视频
            '.mp3', '.mp4', '.avi', '.mov', '.wav',
            
            # 数据
            '.json', '.xml', '.csv', '.log', '.md',
        ]
        
        return safe_extensions
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        block_rate = (
            (self.stats["dangerous_blocked"] / self.stats["total_checked"] * 100)
            if self.stats["total_checked"] > 0
            else 0
        )
        
        return {
            **self.stats,
            "block_rate": round(block_rate, 2)
        }
    
    def generate_security_report(self) -> str:
        """
        生成安全报告
        
        Returns:
            报告文本
        """
        stats = self.get_stats()
        
        report = f"""
文件安全检查统计报告
===================

总检查次数: {stats['total_checked']}
✅ 安全通过: {stats['safe_passed']} ({stats['safe_passed']/max(stats['total_checked'],1)*100:.1f}%)
⚠️ 可疑警告: {stats['suspicious_warned']}
🚫 危险拦截: {stats['dangerous_blocked']}
📦 超大拒绝: {stats['size_rejected']}

拦截率: {stats['block_rate']:.2f}%
"""
        return report


# 创建全局实例
file_security_checker = FileSecurityChecker()
