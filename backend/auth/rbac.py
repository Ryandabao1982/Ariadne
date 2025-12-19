"""Role-Based Access Control (RBAC) system for Ariadne."""

import logging
from enum import Enum
from typing import Dict, List, Set
from functools import wraps

from fastapi import HTTPException, Request, status

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """User roles in the system."""
    EXPLORER = "explorer"        # Free tier
    RESEARCHER = "researcher"     # Paid individual
    TEAM_MEMBER = "team_member"   # Team plan member
    TEAM_ADMIN = "team_admin"     # Team plan admin
    SUPER_ADMIN = "super_admin"   # System admin


class Permission(Enum):
    """System permissions."""
    # Research permissions
    RUN_RESEARCH = "run_research"
    SAVE_RESEARCH = "save_research"
    EDIT_RESEARCH = "edit_research"
    DELETE_RESEARCH = "delete_research"
    
    # Tapestry permissions
    CREATE_TAPESTRY = "create_tapestry"
    EDIT_TAPESTRY = "edit_tapestry"
    DELETE_TAPESTRY = "delete_tapestry"
    SHARE_TAPESTRY = "share_tapestry"
    EXPORT_TAPESTRY = "export_tapestry"
    
    # Loom permissions
    VIEW_LOOM = "view_loom"
    CREATE_LOOM = "create_loom"
    EDIT_LOOM = "edit_loom"
    SHARE_LOOM = "share_loom"
    
    # User management permissions
    VIEW_PROFILE = "view_profile"
    EDIT_PROFILE = "edit_profile"
    DELETE_ACCOUNT = "delete_account"
    
    # Team permissions
    VIEW_TEAM = "view_team"
    INVITE_TEAM = "invite_team"
    MANAGE_TEAM = "manage_team"
    REMOVE_TEAM = "remove_team"
    
    # Admin permissions
    MANAGE_USERS = "manage_users"
    MANAGE_SYSTEM = "manage_system"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_BILLING = "manage_billing"


# Role-permission mapping
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.EXPLORER: {
        # Basic research
        Permission.RUN_RESEARCH,
        Permission.SAVE_RESEARCH,
        Permission.EDIT_RESEARCH,
        
        # Basic tapestries
        Permission.CREATE_TAPESTRY,
        Permission.EDIT_TAPESTRY,
        Permission.DELETE_TAPESTRY,
        Permission.EXPORT_TAPESTRY,
        
        # Basic loom
        Permission.VIEW_LOOM,
        Permission.CREATE_LOOM,
        Permission.EDIT_LOOM,
        
        # Profile
        Permission.VIEW_PROFILE,
        Permission.EDIT_PROFILE,
    },
    
    UserRole.RESEARCHER: {
        # All explorer permissions
        *ROLE_PERMISSIONS[UserRole.EXPLORER],
        
        # Additional research permissions
        Permission.DELETE_RESEARCH,
        
        # Advanced tapestries
        Permission.SHARE_TAPESTRY,
        
        # Advanced loom
        Permission.SHARE_LOOM,
        
        # Analytics
        Permission.VIEW_ANALYTICS,
    },
    
    UserRole.TEAM_MEMBER: {
        # All researcher permissions
        *ROLE_PERMISSIONS[UserRole.RESEARCHER],
        
        # Team permissions
        Permission.VIEW_TEAM,
        Permission.INVITE_TEAM,
    },
    
    UserRole.TEAM_ADMIN: {
        # All team member permissions
        *ROLE_PERMISSIONS[UserRole.TEAM_MEMBER],
        
        # Admin team permissions
        Permission.MANAGE_TEAM,
        Permission.REMOVE_TEAM,
        
        # Billing
        Permission.MANAGE_BILLING,
    },
    
    UserRole.SUPER_ADMIN: {
        # All permissions
        *set(Permission),
    }
}


class RBACError(HTTPException):
    """RBAC-related HTTP exception."""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


def has_permission(user_role: UserRole, permission: Permission) -> bool:
    """Check if user role has specific permission."""
    return permission in ROLE_PERMISSIONS.get(user_role, set())


def has_any_permission(user_role: UserRole, permissions: List[Permission]) -> bool:
    """Check if user role has any of the specified permissions."""
    user_permissions = ROLE_PERMISSIONS.get(user_role, set())
    return any(perm in user_permissions for perm in permissions)


def has_all_permissions(user_role: UserRole, permissions: List[Permission]) -> bool:
    """Check if user role has all of the specified permissions."""
    user_permissions = ROLE_PERMISSIONS.get(user_role, set())
    return all(perm in user_permissions for perm in permissions)


def get_user_permissions(user_role: UserRole) -> Set[Permission]:
    """Get all permissions for a user role."""
    return ROLE_PERMISSIONS.get(user_role, set()).copy()


def get_available_roles() -> List[UserRole]:
    """Get all available user roles."""
    return list(UserRole)


def get_available_permissions() -> List[Permission]:
    """Get all available permissions."""
    return list(Permission)


def check_permission_or_403(user_role: UserRole, permission: Permission) -> None:
    """Check permission and raise 403 if not granted."""
    if not has_permission(user_role, permission):
        raise RBACError(f"Insufficient permissions: {permission.value}")


def require_permission(permission: Permission):
    """Decorator to require specific permission for endpoint."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from request (first argument should be request)
            request = None
            for arg in args:
                if hasattr(arg, 'state') and hasattr(arg.state, 'user'):
                    request = arg
                    break
            
            if not request or not hasattr(request.state, 'user'):
                raise RBACError("User context not found")
            
            user_role = UserRole(request.state.user.subscription_tier)
            check_permission_or_403(user_role, permission)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(permissions: List[Permission]):
    """Decorator to require any of the specified permissions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from request
            request = None
            for arg in args:
                if hasattr(arg, 'state') and hasattr(arg.state, 'user'):
                    request = arg
                    break
            
            if not request or not hasattr(request.state, 'user'):
                raise RBACError("User context not found")
            
            user_role = UserRole(request.state.user.subscription_tier)
            
            if not has_any_permission(user_role, permissions):
                raise RBACError(
                    f"Insufficient permissions: need any of {[p.value for p in permissions]}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_all_permissions(permissions: List[Permission]):
    """Decorator to require all of the specified permissions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from request
            request = None
            for arg in args:
                if hasattr(arg, 'state') and hasattr(arg.state, 'user'):
                    request = arg
                    break
            
            if not request or not hasattr(request.state, 'user'):
                raise RBACError("User context not found")
            
            user_role = UserRole(request.state.user.subscription_tier)
            
            if not has_all_permissions(user_role, permissions):
                missing = [p.value for p in permissions if not has_permission(user_role, p)]
                raise RBACError(
                    f"Insufficient permissions: missing {missing}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role_or_higher(required_role: UserRole):
    """Decorator to require user role or higher."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from request
            request = None
            for arg in args:
                if hasattr(arg, 'state') and hasattr(arg.state, 'user'):
                    request = arg
                    break
            
            if not request or not hasattr(request.state, 'user'):
                raise RBACError("User context not found")
            
            user_role = UserRole(request.state.user.subscription_tier)
            
            # Define role hierarchy (higher roles have all permissions of lower roles)
            role_hierarchy = [
                UserRole.EXPLORER,
                UserRole.RESEARCHER,
                UserRole.TEAM_MEMBER,
                UserRole.TEAM_ADMIN,
                UserRole.SUPER_ADMIN
            ]
            
            try:
                user_role_index = role_hierarchy.index(user_role)
                required_role_index = role_hierarchy.index(required_role)
                
                if user_role_index < required_role_index:
                    raise RBACError(
                        f"Insufficient role: need {required_role.value} or higher"
                    )
            except ValueError:
                raise RBACError("Invalid user role")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class PermissionChecker:
    """Utility class for permission checking."""
    
    def __init__(self, user_role: UserRole):
        self.user_role = user_role
        self.permissions = get_user_permissions(user_role)
    
    def can(self, permission: Permission) -> bool:
        """Check if user can perform permission."""
        return has_permission(self.user_role, permission)
    
    def can_any(self, permissions: List[Permission]) -> bool:
        """Check if user can perform any of the permissions."""
        return has_any_permission(self.user_role, permissions)
    
    def can_all(self, permissions: List[Permission]) -> bool:
        """Check if user can perform all of the permissions."""
        return has_all_permissions(self.user_role, permissions)
    
    def can_role_or_higher(self, required_role: UserRole) -> bool:
        """Check if user has role or higher."""
        role_hierarchy = [
            UserRole.EXPLORER,
            UserRole.RESEARCHER,
            UserRole.TEAM_MEMBER,
            UserRole.TEAM_ADMIN,
            UserRole.SUPER_ADMIN
        ]
        
        try:
            user_role_index = role_hierarchy.index(self.user_role)
            required_role_index = role_hierarchy.index(required_role)
            return user_role_index >= required_role_index
        except ValueError:
            return False
