"""
图片清理工具
✅ P0-4深度优化: 自动清理旧图片 + 磁盘空间监控
"""
import time
from pathlib import Path
from typing import Tuple
from ..utils.logger import logger
from ..config import settings


def clean_old_images(storage_path: Path, days: int) -> Tuple[int, str]:
    """
    清理指定天数前的图片
    
    Args:
        storage_path: 图片存储路径
        days: 天数阈值
    
    Returns:
        (删除文件数, 释放空间字符串)
    """
    try:
        cutoff_time = time.time() - (days * 86400)
        deleted_count = 0
        freed_bytes = 0
        
        logger.info(f"🧹 开始清理 {days} 天前的图片...")
        
        # 遍历所有图片文件
        for image_file in storage_path.glob("**/*"):
            if not image_file.is_file():
                continue
            
            # 跳过非图片文件
            if image_file.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                continue
            
            # 检查文件修改时间
            if image_file.stat().st_mtime < cutoff_time:
                try:
                    file_size = image_file.stat().st_size
                    image_file.unlink()
                    
                    deleted_count += 1
                    freed_bytes += file_size
                    
                    logger.debug(f"🗑️ 删除: {image_file.name} ({format_bytes(file_size)})")
                    
                except Exception as e:
                    logger.error(f"❌ 删除文件失败: {image_file} - {e}")
        
        # 格式化释放空间
        freed_space = format_bytes(freed_bytes)
        
        logger.info(f"✅ 清理完成: 删除 {deleted_count} 个文件，释放 {freed_space}")
        
        return deleted_count, freed_space
    
    except Exception as e:
        logger.error(f"❌ 清理图片失败: {e}")
        return 0, "0 B"


def check_disk_space(storage_path: Path, max_size_gb: int) -> dict:
    """
    检查磁盘空间使用情况
    
    Args:
        storage_path: 存储路径
        max_size_gb: 最大空间限制（GB）
    
    Returns:
        磁盘空间统计信息
    """
    try:
        total_size = 0
        total_files = 0
        
        # 计算总大小
        for file in storage_path.glob("**/*"):
            if file.is_file():
                total_size += file.stat().st_size
                total_files += 1
        
        max_bytes = max_size_gb * 1024 * 1024 * 1024
        used_percent = (total_size / max_bytes) * 100 if max_bytes > 0 else 0
        exceeds_limit = total_size > max_bytes
        
        return {
            "total_size": total_size,
            "total_size_formatted": format_bytes(total_size),
            "total_files": total_files,
            "used_percent": round(used_percent, 2),
            "exceeds_limit": exceeds_limit,
            "max_size_gb": max_size_gb,
            "max_size_bytes": max_bytes,
            "available_bytes": max(0, max_bytes - total_size),
            "available_formatted": format_bytes(max(0, max_bytes - total_size))
        }
    
    except Exception as e:
        logger.error(f"❌ 检查磁盘空间失败: {e}")
        return {
            "error": str(e),
            "total_size": 0,
            "total_files": 0
        }


def format_bytes(bytes: int) -> str:
    """
    格式化字节数
    
    Args:
        bytes: 字节数
    
    Returns:
        格式化的字符串（如 "1.23 MB"）
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} PB"


def get_largest_images(storage_path: Path, limit: int = 10) -> List[dict]:
    """
    获取最大的图片文件列表
    
    Args:
        storage_path: 存储路径
        limit: 返回数量限制
    
    Returns:
        图片信息列表
    """
    try:
        images = []
        
        for file in storage_path.glob("**/*"):
            if file.is_file() and file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                images.append({
                    "name": file.name,
                    "size": file.stat().st_size,
                    "size_formatted": format_bytes(file.stat().st_size),
                    "modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file.stat().st_mtime))
                })
        
        # 按大小降序排序
        images.sort(key=lambda x: x['size'], reverse=True)
        
        return images[:limit]
    
    except Exception as e:
        logger.error(f"❌ 获取最大图片列表失败: {e}")
        return []


def optimize_storage(storage_path: Path, target_size_gb: int) -> dict:
    """
    优化存储空间（删除最旧的文件直到满足目标大小）
    
    Args:
        storage_path: 存储路径
        target_size_gb: 目标大小（GB）
    
    Returns:
        优化结果
    """
    try:
        # 检查当前大小
        space_info = check_disk_space(storage_path, target_size_gb)
        
        if not space_info.get("exceeds_limit", False):
            logger.info("✅ 存储空间在限制内，无需优化")
            return {
                "optimized": False,
                "message": "存储空间充足",
                "current_size": space_info["total_size_formatted"]
            }
        
        logger.info(f"⚠️ 存储空间超限，开始优化...")
        
        # 获取所有文件，按修改时间排序（最旧的优先）
        files = []
        for file in storage_path.glob("**/*"):
            if file.is_file():
                files.append({
                    "path": file,
                    "size": file.stat().st_size,
                    "mtime": file.stat().st_mtime
                })
        
        files.sort(key=lambda x: x['mtime'])
        
        # 删除最旧的文件直到满足目标
        target_bytes = target_size_gb * 1024 * 1024 * 1024
        current_size = space_info["total_size"]
        deleted_count = 0
        freed_bytes = 0
        
        for file_info in files:
            if current_size <= target_bytes:
                break
            
            try:
                file_info["path"].unlink()
                current_size -= file_info["size"]
                freed_bytes += file_info["size"]
                deleted_count += 1
            except Exception as e:
                logger.error(f"❌ 删除文件失败: {file_info['path']} - {e}")
        
        logger.info(f"✅ 优化完成: 删除 {deleted_count} 个文件，释放 {format_bytes(freed_bytes)}")
        
        return {
            "optimized": True,
            "deleted_count": deleted_count,
            "freed_space": format_bytes(freed_bytes),
            "current_size": format_bytes(current_size)
        }
    
    except Exception as e:
        logger.error(f"❌ 优化存储失败: {e}")
        return {"error": str(e)}
