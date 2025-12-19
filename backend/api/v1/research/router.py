"""Research API router for Ariadne backend."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from services.research_service import ResearchService

router = APIRouter()
research_service = ResearchService()


@router.get("/")
async def get_research_status():
    """Get research service status."""
    return {"status": "ok", "service": "research"}


@router.get("/tools")
async def get_available_tools():
    """Get list of available research tools."""
    tools = research_service.get_available_tools()
    return {"tools": tools, "count": len(tools)}


@router.post("/search")
async def search_research(query: Dict[str, Any]):
    """Perform research search."""
    query_text = query.get("query", "")
    user_id = query.get("user_id")
    
    if not query_text:
        raise HTTPException(status_code=400, detail="Query is required")
    
    # Use research service to process query
    results = await research_service.process_query(query_text, user_id)
    return results


@router.post("/analyze")
async def analyze_content(content: Dict[str, Any]):
    """Analyze research content."""
    content_text = content.get("content", "")
    user_id = content.get("user_id")
    
    if not content_text:
        raise HTTPException(status_code=400, detail="Content is required")
    
    # Use research service to analyze content
    results = await research_service.analyze_content(content_text, user_id)
    return results
