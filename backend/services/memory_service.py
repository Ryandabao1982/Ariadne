"""GraphRAG Memory service for intelligent context management."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for GraphRAG-based memory management."""
    
    def __init__(self):
        """Initialize memory service."""
        # In production, this would connect to Neo4j
        # For now, we'll use in-memory storage
        self.memory_graph = {
            "nodes": {},  # node_id -> {type, properties, created_at}
            "edges": {},  # edge_id -> {source, target, type, weight, created_at}
            "embeddings": {}  # node_id -> vector_embedding
        }
        self.query_cache = {}  # query_hash -> relevant_nodes
        logger.info("MemoryService initialized")
    
    async def store_context(self, query: str, context_data: Dict[str, Any], user_id: str) -> str:
        """Store research context in the memory graph."""
        context_id = f"context_{datetime.utcnow().timestamp()}"
        
        # Create context node
        context_node = {
            "id": context_id,
            "type": "research_context",
            "properties": {
                "query": query,
                "content": context_data.get("content", ""),
                "sources": context_data.get("sources", []),
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "relevance_score": context_data.get("relevance_score", 0.5)
            },
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Store node
        self.memory_graph["nodes"][context_id] = context_node
        
        # Connect to related concepts
        await self._create_concept_connections(context_id, query, context_data)
        
        logger.info(f"Stored context: {context_id} for query: {query[:50]}...")
        return context_id
    
    async def retrieve_context(self, query: str, user_id: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant context for a query."""
        # Simple semantic search (in production, use embeddings + vector search)
        query_terms = query.lower().split()
        relevant_contexts = []
        
        for node_id, node in self.memory_graph["nodes"].items():
            if node["type"] == "research_context":
                # Check if user has access to this context
                if node["properties"]["user_id"] != user_id:
                    continue
                
                # Calculate relevance score based on term overlap
                content = node["properties"]["content"].lower()
                node_query = node["properties"]["query"].lower()
                
                relevance_score = 0
                for term in query_terms:
                    if term in content:
                        relevance_score += 1
                    if term in node_query:
                        relevance_score += 2
                
                if relevance_score > 0:
                    relevant_contexts.append({
                        "context_id": node_id,
                        "query": node["properties"]["query"],
                        "content": node["properties"]["content"],
                        "sources": node["properties"]["sources"],
                        "relevance_score": relevance_score,
                        "timestamp": node["properties"]["timestamp"]
                    })
        
        # Sort by relevance and return top results
        relevant_contexts.sort(key=lambda x: x["relevance_score"], reverse=True)
        return relevant_contexts[:max_results]
    
    async def _create_concept_connections(self, context_id: str, query: str, context_data: Dict[str, Any]):
        """Create concept connections for the context."""
        # Extract concepts from query and content
        concepts = await self._extract_concepts(query, context_data.get("content", ""))
        
        for concept in concepts:
            concept_id = f"concept_{concept.lower().replace(' ', '_')}"
            
            # Create or get concept node
            if concept_id not in self.memory_graph["nodes"]:
                concept_node = {
                    "id": concept_id,
                    "type": "concept",
                    "properties": {
                        "name": concept,
                        "category": "extracted",
                        "frequency": 1
                    },
                    "created_at": datetime.utcnow().isoformat()
                }
                self.memory_graph["nodes"][concept_id] = concept_node
            else:
                # Increment frequency
                self.memory_graph["nodes"][concept_id]["properties"]["frequency"] += 1
            
            # Create edge between context and concept
            edge_id = f"edge_{context_id}_{concept_id}"
            edge = {
                "id": edge_id,
                "source": context_id,
                "target": concept_id,
                "type": "mentions",
                "weight": 1.0,
                "created_at": datetime.utcnow().isoformat()
            }
            self.memory_graph["edges"][edge_id] = edge
    
    async def _extract_concepts(self, query: str, content: str) -> List[str]:
        """Extract concepts from text (simplified)."""
        # In production, use NLP libraries like spaCy or NLTK
        # For now, simple keyword extraction
        text = f"{query} {content}".lower()
        
        # Remove common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should"}
        
        words = [word for word in text.split() if len(word) > 3 and word not in stop_words]
        
        # Return unique concepts (simplified)
        return list(set(words))[:10]  # Limit to 10 concepts
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        context_nodes = [n for n in self.memory_graph["nodes"].values() if n["type"] == "research_context"]
        concept_nodes = [n for n in self.memory_graph["nodes"].values() if n["type"] == "concept"]
        
        return {
            "total_contexts": len(context_nodes),
            "total_concepts": len(concept_nodes),
            "total_edges": len(self.memory_graph["edges"]),
            "most_common_concepts": sorted(
                [(n["properties"]["name"], n["properties"]["frequency"]) for n in concept_nodes],
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "recent_contexts": sorted(
                context_nodes,
                key=lambda x: x["properties"]["timestamp"],
                reverse=True
            )[:5]
        }
    
    async def build_knowledge_graph(self, user_id: str) -> Dict[str, Any]:
        """Build knowledge graph for visualization."""
        user_contexts = [
            node for node in self.memory_graph["nodes"].values()
            if node["type"] == "research_context" and node["properties"]["user_id"] == user_id
        ]
        
        concepts = {}
        connections = []
        
        # Collect all concepts for this user
        for context in user_contexts:
            context_id = context["id"]
            
            # Find concept connections
            for edge_id, edge in self.memory_graph["edges"].items():
                if edge["source"] == context_id:
                    target_node = self.memory_graph["nodes"].get(edge["target"])
                    if target_node and target_node["type"] == "concept":
                        concept_name = target_node["properties"]["name"]
                        if concept_name not in concepts:
                            concepts[concept_name] = {
                                "id": target_node["id"],
                                "name": concept_name,
                                "frequency": target_node["properties"]["frequency"],
                                "contexts": []
                            }
                        concepts[concept_name]["contexts"].append({
                            "query": context["properties"]["query"],
                            "timestamp": context["properties"]["timestamp"]
                        })
        
        return {
            "concepts": list(concepts.values()),
            "connections": connections,  # Can be expanded for concept-to-concept connections
            "stats": await self.get_memory_stats()
        }
