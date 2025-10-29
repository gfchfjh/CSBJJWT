"""
Cookie导入API - 终极版
✅ P0-3优化：支持Chrome扩展一键自动导入
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..database import db
from ..utils.logger import logger
from ..utils.crypto import CryptoManager
import json
from datetime import datetime

router = APIRouter(prefix="/api/cookie-import", tags=["Cookie导入"])

crypto_manager = CryptoManager()


class CookieItem(BaseModel):
    """单个Cookie项"""
    name: str
    value: str
    domain: Optional[str] = ""
    path: Optional[str] = "/"
    secure: Optional[bool] = False
    httpOnly: Optional[bool] = False
    sameSite: Optional[str] = "Lax"
    expirationDate: Optional[float] = None


class AutoImportRequest(BaseModel):
    """自动导入请求"""
    cookie: List[CookieItem]
    source: str = "chrome_extension"
    timestamp: int
    extension_version: Optional[str] = "unknown"


class CookieValidateRequest(BaseModel):
    """Cookie验证请求"""
    cookie: List[CookieItem] | Dict


@router.post("/auto-import")
async def auto_import_cookie(request: AutoImportRequest):
    """
    自动导入Cookie（来自Chrome扩展）
    
    ✅ P0-3优化：一键导入，自动创建账号
    
    Args:
        request: 包含Cookie和元数据的请求
        
    Returns:
        导入结果，包括账号信息
    """
    try:
        logger.info(f"[Cookie导入] 收到来自 {request.source} 的导入请求")
        
        # 1. 验证Cookie格式
        if not request.cookie or len(request.cookie) == 0:
            raise HTTPException(status_code=400, detail="Cookie数据为空")
        
        # 转换为标准格式
        cookie_list = [cookie.dict() for cookie in request.cookie]
        cookie_json = json.dumps(cookie_list, ensure_ascii=False)
        
        # 2. 尝试从Cookie提取用户信息
        user_info = extract_user_info_from_cookie(cookie_list)
        
        # 3. 检查是否已存在该账号
        existing_account = None
        if user_info.get('user_id'):
            existing_account = db.execute(
                """
                SELECT * FROM accounts 
                WHERE cookie LIKE ? OR email LIKE ?
                """,
                (f'%{user_info["user_id"]}%', f'%{user_info.get("email", "N/A")}%')
            ).fetchone()
        
        if existing_account:
            # 更新现有账号的Cookie
            logger.info(f"[Cookie导入] 更新现有账号: {existing_account['id']}")
            
            db.execute(
                """
                UPDATE accounts 
                SET cookie = ?,
                    last_active = CURRENT_TIMESTAMP,
                    status = 'online'
                WHERE id = ?
                """,
                (cookie_json, existing_account['id'])
            )
            db.commit()
            
            account_id = existing_account['id']
            email = existing_account['email']
            is_new = False
            
        else:
            # 创建新账号
            logger.info(f"[Cookie导入] 创建新账号")
            
            # 生成临时邮箱（如果无法从Cookie提取）
            email = user_info.get('email') or f"user_{user_info.get('user_id', 'unknown')}@kook.import"
            
            cursor = db.execute(
                """
                INSERT INTO accounts (email, cookie, status, import_source, import_time)
                VALUES (?, ?, 'online', ?, CURRENT_TIMESTAMP)
                """,
                (email, cookie_json, request.source)
            )
            db.commit()
            
            account_id = cursor.lastrowid
            is_new = True
        
        # 4. 记录导入日志
        log_cookie_import(
            account_id=account_id,
            source=request.source,
            extension_version=request.extension_version,
            cookie_count=len(cookie_list)
        )
        
        logger.info(f"✅ [Cookie导入] 成功导入账号: {account_id} ({'新建' if is_new else '更新'})")
        
        return {
            "success": True,
            "account": {
                "id": account_id,
                "email": email,
                "username": user_info.get('username', '未知用户'),
                "is_new": is_new
            },
            "message": "Cookie导入成功" if is_new else "Cookie已更新",
            "next_steps": [
                "前往主界面查看账号状态",
                "配置要监听的服务器和频道",
                "（可选）配置转发Bot"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [Cookie导入] 失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.post("/validate")
async def validate_cookie(request: CookieValidateRequest):
    """
    验证Cookie是否有效
    
    Args:
        request: Cookie数据
        
    Returns:
        验证结果
    """
    try:
        cookie_data = request.cookie
        
        # 转换格式
        if isinstance(cookie_data, list):
            cookie_list = cookie_data
        elif isinstance(cookie_data, dict):
            # 可能是 {name: value} 格式
            cookie_list = [
                {"name": k, "value": v}
                for k, v in cookie_data.items()
            ]
        else:
            raise HTTPException(status_code=400, detail="Cookie格式错误")
        
        # 基础验证
        if len(cookie_list) == 0:
            return {
                "valid": False,
                "error": "Cookie为空"
            }
        
        # 检查必要的Cookie
        cookie_names = [c.get('name') for c in cookie_list]
        required_cookies = ['token', 'session']  # KOOK可能需要的Cookie
        
        has_token = any(name in cookie_names for name in required_cookies)
        
        if not has_token:
            logger.warning(f"[Cookie验证] 缺少关键Cookie，但仍允许导入")
        
        # 尝试提取用户信息
        user_info = extract_user_info_from_cookie(cookie_list)
        
        return {
            "valid": True,
            "user_info": user_info,
            "cookie_count": len(cookie_list),
            "message": "Cookie格式正确"
        }
        
    except Exception as e:
        logger.error(f"[Cookie验证] 失败: {str(e)}")
        return {
            "valid": False,
            "error": str(e)
        }


@router.get("/import-history/{account_id}")
async def get_import_history(account_id: int, limit: int = 10):
    """
    获取Cookie导入历史
    
    Args:
        account_id: 账号ID
        limit: 返回记录数
        
    Returns:
        导入历史列表
    """
    try:
        # 创建导入历史表（如果不存在）
        db.execute("""
            CREATE TABLE IF NOT EXISTS cookie_import_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                import_source TEXT NOT NULL,
                extension_version TEXT,
                cookie_count INTEGER,
                import_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
            )
        """)
        
        results = db.execute(
            """
            SELECT * FROM cookie_import_log 
            WHERE account_id = ?
            ORDER BY import_time DESC
            LIMIT ?
            """,
            (account_id, limit)
        ).fetchall()
        
        history = [
            {
                "id": row['id'],
                "source": row['import_source'],
                "extension_version": row['extension_version'],
                "cookie_count": row['cookie_count'],
                "import_time": row['import_time']
            }
            for row in results
        ]
        
        return {
            "success": True,
            "history": history,
            "total": len(history)
        }
        
    except Exception as e:
        logger.error(f"[导入历史] 获取失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def extract_user_info_from_cookie(cookie_list: List[Dict]) -> Dict:
    """
    从Cookie中提取用户信息
    
    Args:
        cookie_list: Cookie列表
        
    Returns:
        用户信息字典
    """
    user_info = {
        'user_id': None,
        'username': None,
        'email': None
    }
    
    # 尝试从Cookie中提取信息
    for cookie in cookie_list:
        name = cookie.get('name', '')
        value = cookie.get('value', '')
        
        # 常见的用户ID Cookie
        if name in ['user_id', 'uid', 'kook_uid']:
            user_info['user_id'] = value
        
        # 尝试解析包含用户信息的Cookie（可能是JSON）
        if name in ['user_info', 'profile', 'user_data']:
            try:
                import json
                data = json.loads(value)
                user_info['username'] = data.get('username') or data.get('name')
                user_info['email'] = data.get('email')
                user_info['user_id'] = user_info['user_id'] or data.get('id')
            except:
                pass
    
    logger.debug(f"[Cookie解析] 提取到用户信息: {user_info}")
    
    return user_info


def log_cookie_import(account_id: int, source: str, extension_version: str, cookie_count: int):
    """
    记录Cookie导入日志
    
    Args:
        account_id: 账号ID
        source: 来源
        extension_version: 扩展版本
        cookie_count: Cookie数量
    """
    try:
        # 确保表存在
        db.execute("""
            CREATE TABLE IF NOT EXISTS cookie_import_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                import_source TEXT NOT NULL,
                extension_version TEXT,
                cookie_count INTEGER,
                import_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
            )
        """)
        
        db.execute(
            """
            INSERT INTO cookie_import_log 
            (account_id, import_source, extension_version, cookie_count)
            VALUES (?, ?, ?, ?)
            """,
            (account_id, source, extension_version, cookie_count)
        )
        db.commit()
        
    except Exception as e:
        logger.error(f"[导入日志] 记录失败: {str(e)}")


@router.delete("/clear-history/{account_id}")
async def clear_import_history(account_id: int):
    """
    清空导入历史
    
    Args:
        account_id: 账号ID
        
    Returns:
        清空结果
    """
    try:
        db.execute(
            "DELETE FROM cookie_import_log WHERE account_id = ?",
            (account_id,)
        )
        db.commit()
        
        return {
            "success": True,
            "message": "导入历史已清空"
        }
        
    except Exception as e:
        logger.error(f"[导入历史] 清空失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
