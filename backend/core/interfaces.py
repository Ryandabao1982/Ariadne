"""Core interfaces for the Ariadne plugin system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolInput(BaseModel):
    """Input data for tool execution."""
    query: str
    context: Dict[str, Any] = Field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class ToolOutput(BaseModel):
    """Output data from tool execution."""
    success: bool
    data: Any
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LearningInput(BaseModel):
    """Input data for learning models."""
    user_id: str
    feedback_data: Dict[str, Any]
    context: Dict[str, Any] = Field(default_factory=dict)


class LearningOutput(BaseModel):
    """Output data from learning models."""
    predictions: Any
    confidence_score: Optional[float] = None
    model_version: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolInterface(ABC):
    """Abstract interface for all agent tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool does."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Version of the tool."""
        pass

    @property
    @abstractmethod
    def timeout_seconds(self) -> int:
        """Default timeout for tool execution."""
        pass

    @abstractmethod
    async def execute(self, tool_input: ToolInput) -> ToolOutput:
        """Execute the tool with the given input."""
        pass

    @abstractmethod
    async def validate_input(self, tool_input: ToolInput) -> bool:
        """Validate the input data for the tool."""
        pass


class LearningModelInterface(ABC):
    """Abstract interface for all learning models."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for the model."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the model does."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Version of the model."""
        pass

    @abstractmethod
    async def train(self, training_data: List[LearningInput]) -> None:
        """Train the model with the given data."""
        pass

    @abstractmethod
    async def predict(self, input_data: Any) -> LearningOutput:
        """Make predictions with the model."""
        pass

    @abstractmethod
    async def validate_input(self, input_data: Any) -> bool:
        """Validate input data for the model."""
        pass


class ContextProviderInterface(ABC):
    """Interface for providing context to tools and models."""
    
    @abstractmethod
    async def get_context(
        self,
        query: str,
        user_id: str,
        max_tokens: int = 50000,
        include_diversity: bool = True
    ) -> List[Dict[str, Any]]:
        """Get relevant context for a query."""
        pass

    @abstractmethod
    async def rank_context(
        self,
        query: str,
        context_items: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Rank context items by relevance."""
        pass


class OrchestratorInterface(ABC):
    """Interface for the main orchestrator."""
    
    @abstractmethod
    async def process_query(
        self,
        query: str,
        user_id: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a research query end-to-end."""
        pass

    @abstractmethod
    async def create_plan(self, query: str, user_id: str) -> Dict[str, Any]:
        """Create a research plan for a query."""
        pass

    @abstractmethod
    async def execute_plan(
        self,
        plan: Dict[str, Any],
        user_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """Execute a research plan."""
        pass
