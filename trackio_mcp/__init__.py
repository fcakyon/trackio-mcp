"""
trackio-mcp: Automatic MCP server functionality for trackio

Import this package before importing trackio to automatically enable MCP server support.
The patching is thread-safe and uses lazy imports for maximum compatibility.
"""

import os
from .monkey_patch import patch_trackio
from .tools import register_trackio_tools

__version__ = "0.1.0"
__all__ = ["patch_trackio", "register_trackio_tools"]

# Auto-apply patches when imported (safe and thread-safe)
# This provides the best user experience - completely automatic
try:
    patch_trackio()
except Exception:
    # Silently fail if patching fails - better to have working trackio than broken import
    pass