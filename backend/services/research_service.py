"""Research service for orchestrating research workflows."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.interfaces import ToolInterface, ToolInput
from core.registry import get_registry
from services.user_service import UserService

logger = logging.getLogger(__name__)


class ResearchService:
    """Service for orchestrating research workflows."""
    
    def __init__(self):
        """Initialize research service."""
        self.registry = get_registry()
        self.user_service = UserService()
        logger.info("ResearchService initialized")
    
    async def process_query(self, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a research query end-to-end."""
        start_time = datetime.utcnow()
        
        logger.info(f"Processing research query: {query}")
        
        # Create tool input
        tool_input = ToolInput(
            query=query,
            context={"user_id": user_id, "timestamp": start_time.isoformat()}
        )
        
        results = {
            "query": query,
            "user_id": user_id,
            "start_time": start_time.isoformat(),
            "results": [],
            "errors": [],
            "tools_used": [],
            "status": "completed"
        }
        
        # Use available tools for research
        available_tools = self.registry.list_tools()
        logger.info(f"Available tools: {available_tools}")
        
        # Execute web search if available
        if "web_search" in available_tools:
            web_search_tool = self.registry.get_tool("web_search")
            if web_search_tool:
                try:
                    logger.info("Executing web search...")
                    search_result = await web_search_tool.execute(tool_input)
                    results["results"].append({
                        "tool": "web_search",
                        "data": search_result.data,
                        "success": search_result.success,
                        "metadata": search_result.metadata
                    })
                    results["tools_used"].append("web_search")
                except Exception as e:
                    error_msg = f"Web search failed: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
        
        # Execute document ingestion if available
        if "document_ingestion" in available_tools:
            doc_tool = self.registry.get_tool("document_ingestion")
            if doc_tool:
                try:
                    logger.info("Executing document ingestion...")
                    # For now, use the query as document path for testing
                    tool_input.query = f"document_{query[:20]}"
                    doc_result = await doc_tool.execute(tool_input)
                    results["results"].append({
                        "tool": "document_ingestion", 
                        "data": doc_result.data,
                        "success": doc_result.success,
                        "metadata": doc_result.metadata
                    })
                    results["tools_used"].append("document_ingestion")
                except Exception as e:
                    error_msg = f"Document ingestion failed: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
        
        # Calculate execution time
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        results["end_time"] = end_time.isoformat()
        results["execution_time_seconds"] = execution_time
        
        logger.info(f"Research query completed in {execution_time:.2f}s")
        return results
    
    async def analyze_content(self, content: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Analyze research content."""
        logger.info(f"Analyzing content: {content[:100]}...")
        
        # For now, return mock analysis
        return {
            "content": content,
            "analysis": {
                "summary": "Content analysis not yet implemented",
                "key_topics": [],
                "sentiment": "neutral",
                "word_count": len(content.split())
            },
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available research tools."""
        tools = []
        for tool_name in self.registry.list_tools():
            tool = self.registry.get_tool(tool_name)
            if tool:
                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "version": tool.version,
                    "timeout_seconds": tool.timeout_seconds
                })
        return tools
