"""
trackio-mcp: MCP server support for trackio experiment tracking

Simple, direct monkey patching approach. Import this before trackio to 
automatically enable MCP server functionality.
"""

__version__ = "0.2.0"

# Apply patches immediately on import - simple and direct
try:
    from .monkey_patch import patch_trackio
    from .tools import register_trackio_tools
    
    __all__ = ["patch_trackio", "register_trackio_tools"]
    
    # Auto-patch when imported
    patch_trackio()
    
except Exception:
    # Fail gracefully if dependencies missing
    __all__ = []
