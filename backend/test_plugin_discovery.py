#!/usr/bin/env python3
"""Test script to verify plugin discovery works."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.registry import registry

def test_plugin_discovery():
    """Test plugin discovery functionality."""
    print("🔍 Testing Plugin Discovery...")
    
    # Clear any existing plugins
    registry.clear_all()
    
    # Discover plugins in our tools directory
    try:
        registry.discover_plugins('plugins.tools')
        print("✅ Plugin discovery completed")
        
        # Check what was discovered
        stats = registry.get_registry_stats()
        print(f"📊 Registry Stats: {stats}")
        
        # Test tool access
        tools = registry.list_tools()
        print(f"🛠️  Discovered tools: {tools}")
        
        for tool_name in tools:
            tool = registry.get_tool(tool_name)
            if tool:
                print(f"   - {tool.name}: {tool.description} (v{tool.version})")
                
                # Test the tool interface
                print(f"     ✅ Implements ToolInterface: {hasattr(tool, 'execute')}")
                print(f"     ✅ Has timeout: {tool.timeout_seconds}s")
        
        print("🎉 Plugin discovery test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Plugin discovery test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_plugin_discovery()
    sys.exit(0 if success else 1)
