"""Plugin registry system for dynamic tool and model discovery."""

import importlib
import pkgutil
import logging
from typing import Dict, Type, Any, List, Optional
from .interfaces import ToolInterface, LearningModelInterface

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Central registry for all plugins (tools and models)."""
    
    def __init__(self):
        self._tools: Dict[str, ToolInterface] = {}
        self._learning_models: Dict[str, LearningModelInterface] = {}
        self._tool_metadata: Dict[str, Dict[str, Any]] = {}
        self._model_metadata: Dict[str, Dict[str, Any]] = {}
    
    def register_tool(self, tool: ToolInterface, metadata: Optional[Dict[str, Any]] = None):
        """Register a tool plugin."""
        if not isinstance(tool, ToolInterface):
            raise TypeError(f"Expected ToolInterface, got {type(tool)}")
        
        if tool.name in self._tools:
            logger.warning(f"Tool '{tool.name}' is already registered. Overwriting.")
        
        self._tools[tool.name] = tool
        self._tool_metadata[tool.name] = metadata or {}
        logger.info(f"Registered tool: {tool.name} (version: {tool.version})")
    
    def register_learning_model(self, model: LearningModelInterface, metadata: Optional[Dict[str, Any]] = None):
        """Register a learning model plugin."""
        if not isinstance(model, LearningModelInterface):
            raise TypeError(f"Expected LearningModelInterface, got {type(model)}")
        
        if model.name in self._learning_models:
            logger.warning(f"Model '{model.name}' is already registered. Overwriting.")
        
        self._learning_models[model.name] = model
        self._model_metadata[model.name] = metadata or {}
        logger.info(f"Registered learning model: {model.name} (version: {model.version})")
    
    def get_tool(self, name: str) -> Optional[ToolInterface]:
        """Get a registered tool by name."""
        return self._tools.get(name)
    
    def get_learning_model(self, name: str) -> Optional[LearningModelInterface]:
        """Get a registered learning model by name."""
        return self._learning_models.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    def list_learning_models(self) -> List[str]:
        """List all registered learning model names."""
        return list(self._learning_models.keys())
    
    def get_tool_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a tool."""
        return self._tool_metadata.get(name)
    
    def get_model_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a model."""
        return self._model_metadata.get(name)
    
    def get_all_tools(self) -> Dict[str, ToolInterface]:
        """Get all registered tools."""
        return self._tools.copy()
    
    def get_all_models(self) -> Dict[str, LearningModelInterface]:
        """Get all registered learning models."""
        return self._learning_models.copy()
    
    def discover_plugins(self, package_name: str, exclude_patterns: Optional[List[str]] = None):
        """Auto-discover plugins in a package and its sub-packages.
        
        Args:
            package_name: Python package name to search (e.g., 'plugins.tools')
            exclude_patterns: List of patterns to exclude from discovery
        """
        exclude_patterns = exclude_patterns or ['test', 'tests', '__pycache__']
        
        try:
            package = importlib.import_module(package_name)
            package_path = package.__path__
        except ImportError as e:
            logger.warning(f"Could not import package {package_name}: {e}")
            return
        
        for finder, name, is_package in pkgutil.iter_modules(package_path):
            # Skip excluded patterns
            if any(pattern in name.lower() for pattern in exclude_patterns):
                continue
            
            try:
                module_name = f'{package_name}.{name}'
                module = importlib.import_module(module_name)
                
                # Look for ToolInterface implementations
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, ToolInterface) and 
                        attr is not ToolInterface):
                        try:
                            # Instantiate the tool
                            tool_instance = attr()
                            self.register_tool(tool_instance)
                        except Exception as e:
                            logger.error(f"Failed to instantiate tool {attr_name}: {e}")
                
                # Look for LearningModelInterface implementations
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, LearningModelInterface) and 
                        attr is not LearningModelInterface):
                        try:
                            # Instantiate the model
                            model_instance = attr()
                            self.register_learning_model(model_instance)
                        except Exception as e:
                            logger.error(f"Failed to instantiate model {attr_name}: {e}")
                            
            except Exception as e:
                logger.warning(f"Could not import module {module_name}: {e}")
    
    def unregister_tool(self, name: str) -> bool:
        """Unregister a tool by name."""
        if name in self._tools:
            del self._tools[name]
            del self._tool_metadata[name]
            logger.info(f"Unregistered tool: {name}")
            return True
        return False
    
    def unregister_model(self, name: str) -> bool:
        """Unregister a learning model by name."""
        if name in self._learning_models:
            del self._learning_models[name]
            del self._model_metadata[name]
            logger.info(f"Unregistered learning model: {name}")
            return True
        return False
    
    def clear_all(self):
        """Clear all registered plugins."""
        self._tools.clear()
        self._learning_models.clear()
        self._tool_metadata.clear()
        self._model_metadata.clear()
        logger.info("Cleared all registered plugins")
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get statistics about the registry."""
        return {
            "total_tools": len(self._tools),
            "total_models": len(self._learning_models),
            "tool_names": list(self._tools.keys()),
            "model_names": list(self._learning_models.keys()),
            "tools_with_metadata": len([k for k in self._tool_metadata.keys() if self._tool_metadata[k]]),
            "models_with_metadata": len([k for k in self._model_metadata.keys() if self._model_metadata[k]])
        }


# Global registry instance
registry = PluginRegistry()


def get_registry() -> PluginRegistry:
    """Get the global plugin registry instance."""
    return registry


def register_tool(tool: ToolInterface, metadata: Optional[Dict[str, Any]] = None):
    """Convenience function to register a tool in the global registry."""
    registry.register_tool(tool, metadata)


def register_learning_model(model: LearningModelInterface, metadata: Optional[Dict[str, Any]] = None):
    """Convenience function to register a learning model in the global registry."""
    registry.register_learning_model(model, metadata)


def discover_plugins(package_name: str, exclude_patterns: Optional[List[str]] = None):
    """Convenience function to discover plugins in the global registry."""
    registry.discover_plugins(package_name, exclude_patterns)
