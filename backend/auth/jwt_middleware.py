"""JWT middleware for FastAPI."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from core.config import get_settings
from models.user import User

logger = logging.getLogger(__name__)

settings = get_settings()
security = HTTPBearer()


class JWTPayload:
    """JWT payload data structure."""
    
    def __init__(self, user_id: str, email: str, subscription_tier: str, exp: datetime):
        self.user_id = user_id
        self.email = email
        self.subscription_tier = subscription_tier
        self.exp = exp
    
    @classmethod
    def from_token(cls, token: str) -> 'JWTPayload':
        """Create payload from JWT token."""
        try:
            payload = jwt.decode(
                token, 
                settings.security.secret_key, 
                algorithms=[settings.security.algorithm]
            )
            return cls(
                user_id=payload.get("sub"),
                email=payload.get("email"),
                subscription_tier=payload.get("subscription_tier", "explorer"),
                exp=datetime.fromtimestamp(payload.get("exp"))
            )
        except JWTError as e:
            logger.error(f"JWT decode error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() >= self.exp


class JWTManager:
    """JWT token manager."""
    
    @staticmethod
    def create_access_token(user: User) -> str:
        """Create access token for user."""
        expire = datetime.utcnow() + timedelta(minutes=settings.security.access_token_expire_minutes)
        
        payload = {
            "sub": str(user.user_id),
            "email": user.email,
            "subscription_tier": user.subscription_tier,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(
            payload,
            settings.security.secret_key,
            algorithm=settings.security.algorithm
        )
    
    @staticmethod
    def create_refresh_token(user: User) -> str:
        """Create refresh token for user."""
        expire = datetime.utcnow() + timedelta(days=settings.security.refresh_token_expire_days)
        
        payload = {
            "sub": str(user.user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        return jwt.encode(
            payload,
            settings.security.secret_key,
            algorithm=settings.security.algorithm
        )
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> JWTPayload:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(
                token,
                settings.security.secret_key,
                algorithms=[settings.security.algorithm]
            )
            
            # Check token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type: expected {token_type}"
                )
            
            return JWTPayload.from_token(token)
            
        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )


class JWTMiddleware:
    """FastAPI middleware for JWT authentication."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """Process request through middleware."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Skip authentication for public endpoints
        if self._is_public_endpoint(request.url.path):
            await self.app(scope, receive, send)
            return
        
        # Get authorization header
        try:
            credentials: HTTPAuthorizationCredentials = await security(request)
            token = credentials.credentials
            
            # Verify token and add user to request state
            payload = JWTManager.verify_token(token)
            request.state.user = payload
            request.state.user_id = payload.user_id
            
        except HTTPException as e:
            # For protected endpoints, return 401 if no valid token
            if not self._is_public_endpoint(request.url.path):
                response = JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Not authenticated"}
                )
                await response(scope, receive, send)
                return
        
        await self.app(scope, receive, send)
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (doesn't require authentication)."""
        public_paths = [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/research/anonymous"  # Allow anonymous research queries
        ]
        
        return any(path.startswith(public_path) for public_path in public_paths)


async def get_current_user(request: Request = None) -> User:
    """Dependency to get current authenticated user."""
    if not hasattr(request.state, 'user'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # In a real implementation, fetch user from database
    # For now, create a minimal user object from JWT payload
    user = User(
        user_id=request.state.user.user_id,
        email=request.state.user.email,
        subscription_tier=request.state.user.subscription_tier
    )
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to get current active user."""
    # Add checks for active/verified status here
    return current_user


def create_user_tokens(user: User) -> Tuple[str, str]:
    """Create access and refresh tokens for user."""
    access_token = JWTManager.create_access_token(user)
    refresh_token = JWTManager.create_refresh_token(user)
    return access_token, refresh_token
