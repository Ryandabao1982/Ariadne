"""Users API router for Ariadne backend."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter()


@router.get("/")
async def get_users_status():
    """Get users service status."""
    return {"status": "ok", "service": "users"}


@router.get("/profile")
async def get_user_profile():
    """Get user profile."""
    return {"user": {"id": "demo", "name": "Demo User"}, "status": "ok"}


@router.post("/update")
async def update_user_profile(data: Dict[str, Any]):
    """Update user profile."""
    return {"message": "Profile updated", "data": data, "status": "ok"}
