"""Tapestries API router for Ariadne backend."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter()


@router.get("/")
async def get_tapestries_status():
    """Get tapestries service status."""
    return {"status": "ok", "service": "tapestries"}


@router.get("/list")
async def list_tapestries():
    """List user tapestries."""
    return {"tapestries": [], "status": "ok"}


@router.post("/create")
async def create_tapestry(data: Dict[str, Any]):
    """Create a new tapestry."""
    return {"message": "Tapestry created", "data": data, "status": "ok"}


@router.get("/{tapestry_id}")
async def get_tapestry(tapestry_id: str):
    """Get a specific tapestry."""
    return {"tapestry": {"id": tapestry_id, "title": "Demo Tapestry"}, "status": "ok"}
