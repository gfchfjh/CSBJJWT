"""
权限管理系统
✅ P1-7: 基于角色的访问控制(RBAC)
"""
from typing import List, Dict, Set, Optional
from enum import Enum
from functools import wraps
from fastapi import HTTPException, status
from ..utils.logger import logger


class Permission(str, Enum):
    """权限枚举"""
    # 账号管理
    ACCOUNT_VIEW = 'account:view'
    ACCOUNT_ADD = 'account:add'
    ACCOUNT_EDIT = 'account:edit'
    ACCOUNT_DELETE = 'account:delete'
    
    # Bot配置
    BOT_VIEW = 'bot:view'
    BOT_ADD = 'bot:add'
    BOT_EDIT = 'bot:edit'
    BOT_DELETE = 'bot:delete'
    
    # 频道映射
    MAPPING_VIEW = 'mapping:view'
    MAPPING_EDIT = 'mapping:edit'
    
    # 过滤规则
    FILTER_VIEW = 'filter:view'
    FILTER_EDIT = 'filter:edit'
    
    # 日志查看
    LOG_VIEW = 'log:view'
    LOG_EXPORT = 'log:export'
    LOG_DELETE = 'log:delete'
    
    # 统计分析
    STATS_VIEW = 'stats:view'
    
    # 系统设置
    SETTINGS_VIEW = 'settings:view'
    SETTINGS_EDIT = 'settings:edit'
    
    # 插件管理
    PLUGIN_VIEW = 'plugin:view'
    PLUGIN_INSTALL = 'plugin:install'
    PLUGIN_UNINSTALL = 'plugin:uninstall'
    PLUGIN_CONFIGURE = 'plugin:configure'
    
    # 系统管理
    SYSTEM_BACKUP = 'system:backup'
    SYSTEM_RESTORE = 'system:restore'
    SYSTEM_UPDATE = 'system:update'


class Role(str, Enum):
    """角色枚举"""
    ADMIN = 'admin'          # 管理员（所有权限）
    OPERATOR = 'operator'    # 操作员（大部分权限）
    VIEWER = 'viewer'        # 查看者（只读权限）


class PermissionManager:
    """权限管理器"""
    
    def __init__(self):
        # 角色权限映射
        self.role_permissions: Dict[str, Set[str]] = {
            Role.ADMIN: self._get_all_permissions(),
            Role.OPERATOR: self._get_operator_permissions(),
            Role.VIEWER: self._get_viewer_permissions()
        }
        
        # 用户角色映射
        self.user_roles: Dict[str, str] = {
            'admin': Role.ADMIN,
            'default': Role.OPERATOR
        }
    
    def _get_all_permissions(self) -> Set[str]:
        """获取所有权限"""
        return {perm.value for perm in Permission}
    
    def _get_operator_permissions(self) -> Set[str]:
        """获取操作员权限"""
        return {
            # 账号管理
            Permission.ACCOUNT_VIEW,
            Permission.ACCOUNT_ADD,
            Permission.ACCOUNT_EDIT,
            
            # Bot配置
            Permission.BOT_VIEW,
            Permission.BOT_ADD,
            Permission.BOT_EDIT,
            
            # 频道映射
            Permission.MAPPING_VIEW,
            Permission.MAPPING_EDIT,
            
            # 过滤规则
            Permission.FILTER_VIEW,
            Permission.FILTER_EDIT,
            
            # 日志查看
            Permission.LOG_VIEW,
            Permission.LOG_EXPORT,
            
            # 统计分析
            Permission.STATS_VIEW,
            
            # 系统设置（仅查看）
            Permission.SETTINGS_VIEW,
            
            # 插件管理（仅查看和配置）
            Permission.PLUGIN_VIEW,
            Permission.PLUGIN_CONFIGURE
        }
    
    def _get_viewer_permissions(self) -> Set[str]:
        """获取查看者权限"""
        return {
            Permission.ACCOUNT_VIEW,
            Permission.BOT_VIEW,
            Permission.MAPPING_VIEW,
            Permission.FILTER_VIEW,
            Permission.LOG_VIEW,
            Permission.STATS_VIEW,
            Permission.SETTINGS_VIEW,
            Permission.PLUGIN_VIEW
        }
    
    def has_permission(self, user: str, permission: str) -> bool:
        """
        检查用户是否有指定权限
        
        Args:
            user: 用户标识
            permission: 权限标识
            
        Returns:
            是否有权限
        """
        # 获取用户角色
        role = self.user_roles.get(user, Role.VIEWER)
        
        # 获取角色权限
        permissions = self.role_permissions.get(role, set())
        
        return permission in permissions
    
    def has_any_permission(self, user: str, permissions: List[str]) -> bool:
        """检查用户是否有任意一个权限"""
        return any(self.has_permission(user, perm) for perm in permissions)
    
    def has_all_permissions(self, user: str, permissions: List[str]) -> bool:
        """检查用户是否有所有权限"""
        return all(self.has_permission(user, perm) for perm in permissions)
    
    def get_user_role(self, user: str) -> str:
        """获取用户角色"""
        return self.user_roles.get(user, Role.VIEWER)
    
    def set_user_role(self, user: str, role: str):
        """设置用户角色"""
        if role not in [r.value for r in Role]:
            raise ValueError(f"Invalid role: {role}")
        
        self.user_roles[user] = role
        logger.info(f"用户角色已更新: {user} -> {role}")
    
    def get_user_permissions(self, user: str) -> List[str]:
        """获取用户的所有权限"""
        role = self.get_user_role(user)
        permissions = self.role_permissions.get(role, set())
        return list(permissions)
    
    def add_role_permission(self, role: str, permission: str):
        """为角色添加权限"""
        if role not in self.role_permissions:
            self.role_permissions[role] = set()
        
        self.role_permissions[role].add(permission)
        logger.info(f"权限已添加: {role} -> {permission}")
    
    def remove_role_permission(self, role: str, permission: str):
        """移除角色权限"""
        if role in self.role_permissions:
            self.role_permissions[role].discard(permission)
            logger.info(f"权限已移除: {role} -> {permission}")


# 全局权限管理器
permission_manager = PermissionManager()


# 权限装饰器
def require_permission(permission: str):
    """
    权限检查装饰器
    
    用法:
    @require_permission(Permission.ACCOUNT_ADD)
    async def add_account(...):
        ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从请求中获取用户
            # TODO: 实现用户身份认证
            user = 'default'
            
            # 检查权限
            if not permission_manager.has_permission(user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


# 角色装饰器
def require_role(role: str):
    """
    角色检查装饰器
    
    用法:
    @require_role(Role.ADMIN)
    async def delete_all_data(...):
        ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从请求中获取用户
            # TODO: 实现用户身份认证
            user = 'default'
            
            # 检查角色
            user_role = permission_manager.get_user_role(user)
            if user_role != role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: {role}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator
