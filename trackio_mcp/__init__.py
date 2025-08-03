"""
trackio-mcp: Monkey-patch trackio to enable MCP server functionality

Import this package before importing trackio to automatically enable MCP server support.
"""

from .monkey_patch import patch_trackio
from .tools import register_trackio_tools

__version__ = "0.1.0"
__all__ = ["patch_trackio", "register_trackio_tools"]

# Auto-apply patches when imported
patch_trackio()
