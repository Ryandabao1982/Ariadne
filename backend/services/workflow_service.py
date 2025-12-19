"""Workflow orchestration service for complex research processes."""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import json

from services.memory_service import MemoryService
from core.registry import get_registry

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service for orchestrating research workflows."""
    
    def __init__(self):
        """Initialize workflow service."""
        self.registry = get_registry()
        self.memory_service = MemoryService()
        self.active_workflows = {}  # workflow_id -> workflow_state
        self.workflow_templates = {}
        logger.info("WorkflowService initialized")
    
    async def create_research_plan(self, query: str, user_id: str) -> str:
        """Create a research plan for a query."""
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        
        # Analyze query to determine research steps
        plan = await self._analyze_query_and_create_plan(query, user_id)
        
        workflow_state = {
            "plan_id": plan_id,
            "query": query,
            "user_id": user_id,
            "status": "planning",
            "steps": plan,
            "current_step": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "results": {},
            "errors": []
        }
        
        self.active_workflows[plan_id] = workflow_state
        
        logger.info(f"Created research plan: {plan_id} for query: {query[:50]}...")
        return plan_id
    
    async def execute_research_plan(self, plan_id: str, user_id: str) -> Dict[str, Any]:
        """Execute a research plan."""
        if plan_id not in self.active_workflows:
            raise ValueError(f"Plan {plan_id} not found")
        
        workflow = self.active_workflows[plan_id]
        if workflow["user_id"] != user_id:
            raise ValueError("Unauthorized access to workflow")
        
        workflow["status"] = "executing"
        workflow["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Executing research plan: {plan_id}")
        
        try:
            # Execute each step
            for i, step in enumerate(workflow["steps"]):
                workflow["current_step"] = i
                step_result = await self._execute_workflow_step(step, workflow, user_id)
                
                workflow["results"][step["id"]] = step_result
                
                # Check for errors
                if step_result.get("status") == "error":
                    workflow["errors"].append(f"Step {step['id']}: {step_result.get('error')}")
                    workflow["status"] = "failed"
                    break
                
                # Update progress
                progress = (i + 1) / len(workflow["steps"])
                logger.info(f"Step {i+1}/{len(workflow['steps'])} completed: {progress:.1%}")
            
            # Check if completed successfully
            if workflow["status"] != "failed":
                workflow["status"] = "completed"
                
                # Store results in memory
                await self._store_workflow_results(workflow, user_id)
            
        except Exception as e:
            workflow["status"] = "error"
            workflow["errors"].append(f"Workflow execution failed: {str(e)}")
            logger.error(f"Workflow execution failed: {plan_id}: {e}")
        
        workflow["updated_at"] = datetime.utcnow().isoformat()
        return workflow
    
    async def _analyze_query_and_create_plan(self, query: str, user_id: str) -> List[Dict[str, Any]]:
        """Analyze query and create research plan."""
        # Simple query analysis (in production, use NLP)
        query_lower = query.lower()
        
        # Determine required steps based on query
        steps = []
        
        # Step 1: Initial web search
        if any(word in query_lower for word in ["what", "how", "why", "when", "where", "who"]):
            steps.append({
                "id": "web_search",
                "type": "search",
                "name": "Web Search",
                "description": "Search for relevant information",
                "depends_on": [],
                "estimated_time": 30,
                "tool_required": "web_search"
            })
        
        # Step 2: Document analysis (if query suggests documents)
        if any(word in query_lower for word in ["document", "paper", "article", "study", "research"]):
            steps.append({
                "id": "document_analysis",
                "type": "analysis",
                "name": "Document Analysis",
                "description": "Analyze and extract insights from documents",
                "depends_on": ["web_search"],
                "estimated_time": 60,
                "tool_required": "document_ingestion"
            })
        
        # Step 3: Context retrieval
        steps.append({
            "id": "context_retrieval",
            "type": "retrieval",
            "name": "Context Retrieval",
            "description": "Retrieve relevant context from memory",
            "depends_on": [],
            "estimated_time": 10,
            "tool_required": "memory_service"
        })
        
        # Step 4: Synthesis
        steps.append({
            "id": "synthesis",
            "type": "synthesis",
            "name": "Synthesis",
            "description": "Synthesize findings into coherent answer",
            "depends_on": ["web_search", "document_analysis", "context_retrieval"],
            "estimated_time": 30,
            "tool_required": "research_service"
        })
        
        return steps
    
    async def _execute_workflow_step(self, step: Dict[str, Any], workflow: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute a single workflow step."""
        step_id = step["id"]
        step_type = step["type"]
        
        try:
            if step_type == "search":
                return await self._execute_search_step(step, workflow, user_id)
            elif step_type == "analysis":
                return await self._execute_analysis_step(step, workflow, user_id)
            elif step_type == "retrieval":
                return await self._execute_retrieval_step(step, workflow, user_id)
            elif step_type == "synthesis":
                return await self._execute_synthesis_step(step, workflow, user_id)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown step type: {step_type}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": f"Step execution failed: {str(e)}"
            }
    
    async def _execute_search_step(self, step: Dict[str, Any], workflow: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute web search step."""
        # Check dependencies
        if not await self._check_dependencies(step, workflow):
            return {"status": "skipped", "reason": "Dependencies not met"}
        
        # Get web search tool
        web_search_tool = self.registry.get_tool("web_search")
        if not web_search_tool:
            return {"status": "error", "error": "Web search tool not available"}
        
        # Execute search
        from core.interfaces import ToolInput
        tool_input = ToolInput(
            query=workflow["query"],
            context={"step_id": step["id"], "user_id": user_id}
        )
        
        result = await web_search_tool.execute(tool_input)
        
        return {
            "status": "completed",
            "result": result.data,
            "timestamp": datetime.utcnow().isoformat(),
            "tool_used": "web_search"
        }
    
    async def _execute_analysis_step(self, step: Dict[str, Any], workflow: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute document analysis step."""
        # Check dependencies
        if not await self._check_dependencies(step, workflow):
            return {"status": "skipped", "reason": "Dependencies not met"}
        
        # Get document ingestion tool
        doc_tool = self.registry.get_tool("document_ingestion")
        if not doc_tool:
            return {"status": "error", "error": "Document ingestion tool not available"}
        
        # For now, analyze the workflow query as content
        from core.interfaces import ToolInput
        tool_input = ToolInput(
            query=f"analysis_{workflow['query'][:50]}",
            context={"step_id": step["id"], "user_id": user_id}
        )
        
        result = await doc_tool.execute(tool_input)
        
        return {
            "status": "completed",
            "result": result.data,
            "timestamp": datetime.utcnow().isoformat(),
            "tool_used": "document_ingestion"
        }
    
    async def _execute_retrieval_step(self, step: Dict[str, Any], workflow: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute context retrieval step."""
        # Retrieve relevant context from memory
        context_results = await self.memory_service.retrieve_context(
            workflow["query"],
            user_id,
            max_results=5
        )
        
        return {
            "status": "completed",
            "result": {
                "contexts": context_results,
                "count": len(context_results)
            },
            "timestamp": datetime.utcnow().isoformat(),
            "tool_used": "memory_service"
        }
    
    async def _execute_synthesis_step(self, step: Dict[str, Any], workflow: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute synthesis step."""
        # Collect results from all previous steps
        search_result = workflow["results"].get("web_search", {}).get("result", {})
        analysis_result = workflow["results"].get("document_analysis", {}).get("result", {})
        retrieval_result = workflow["results"].get("context_retrieval", {}).get("result", {})
        
        # Synthesize results
        synthesis = {
            "query": workflow["query"],
            "sources": {
                "web_search": search_result,
                "document_analysis": analysis_result,
                "retrieved_contexts": retrieval_result.get("contexts", [])
            },
            "synthesis_timestamp": datetime.utcnow().isoformat(),
            "status": "completed"
        }
        
        return {
            "status": "completed",
            "result": synthesis,
            "timestamp": datetime.utcnow().isoformat(),
            "tool_used": "workflow_synthesis"
        }
    
    async def _check_dependencies(self, step: Dict[str, Any], workflow: Dict[str, Any]) -> bool:
        """Check if step dependencies are met."""
        dependencies = step.get("depends_on", [])
        
        for dep_id in dependencies:
            dep_result = workflow["results"].get(dep_id, {})
            if dep_result.get("status") != "completed":
                return False
        
        return True
    
    async def _store_workflow_results(self, workflow: Dict[str, Any], user_id: str):
        """Store workflow results in memory."""
        synthesis_result = workflow["results"].get("synthesis", {}).get("result", {})
        
        if synthesis_result:
            await self.memory_service.store_context(
                workflow["query"],
                {
                    "content": json.dumps(synthesis_result),
                    "sources": synthesis_result.get("sources", {}),
                    "workflow_id": workflow["plan_id"],
                    "relevance_score": 1.0
                },
                user_id
            )
    
    async def get_workflow_status(self, plan_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow execution status."""
        if plan_id not in self.active_workflows:
            return None
        
        workflow = self.active_workflows[plan_id]
        if workflow["user_id"] != user_id:
            return None
        
        return {
            "plan_id": plan_id,
            "query": workflow["query"],
            "status": workflow["status"],
            "progress": (workflow["current_step"] + 1) / len(workflow["steps"]) if workflow["steps"] else 0,
            "current_step": workflow["current_step"],
            "total_steps": len(workflow["steps"]),
            "created_at": workflow["created_at"],
            "updated_at": workflow["updated_at"],
            "has_errors": len(workflow["errors"]) > 0,
            "error_count": len(workflow["errors"])
        }
    
    async def get_workflow_results(self, plan_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed workflow results."""
        if plan_id not in self.active_workflows:
            return None
        
        workflow = self.active_workflows[plan_id]
        if workflow["user_id"] != user_id:
            return None
        
        return {
            "plan_id": plan_id,
            "query": workflow["query"],
            "results": workflow["results"],
            "errors": workflow["errors"],
            "status": workflow["status"],
            "execution_summary": await self._create_execution_summary(workflow)
        }
    
    async def _create_execution_summary(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Create execution summary."""
        completed_steps = sum(1 for step_result in workflow["results"].values() if step_result.get("status") == "completed")
        total_steps = len(workflow["steps"])
        
        return {
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "success_rate": completed_steps / total_steps if total_steps > 0 else 0,
            "tools_used": list(set(
                step_result.get("tool_used") 
                for step_result in workflow["results"].values() 
                if step_result.get("tool_used")
            )),
            "duration": datetime.utcnow().isoformat()
        }
