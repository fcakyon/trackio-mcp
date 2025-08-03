"""
Thread-safe monkey-patch for trackio to enable MCP server functionality automatically.
"""

import os
import sys
import threading
from functools import wraps
from typing import Any, Callable, Optional

# Global state
_patch_lock = threading.Lock()
_gradio_patched = False
_original_import = None


def patch_trackio() -> None:
    """Apply monkey patches to enable MCP server functionality in trackio."""
    
    # Check if MCP should be enabled
    enable_mcp = os.getenv("TRACKIO_ENABLE_MCP", "true").lower() in ("true", "1", "yes")
    if not enable_mcp:
        return
    
    # Install import hook for lazy patching
    _install_import_hook()
    
    # Try immediate patching if gradio is already available
    try:
        import gradio as gr
        _patch_gradio_launch(gr)
    except ImportError:
        pass  # Will be handled by import hook


def _install_import_hook() -> None:
    """Install import hook to patch gradio when it's imported."""
    global _original_import
    
    if _original_import is not None:
        return  # Already installed
    
    # Handle both dict and module forms of __builtins__
    if isinstance(__builtins__, dict):
        _original_import = __builtins__['__import__']
    else:
        _original_import = __builtins__.__import__
    
    def patched_import(name: str, *args, **kwargs):
        """Import hook that patches gradio when imported."""
        result = _original_import(name, *args, **kwargs)
        
        # Patch gradio when it becomes available
        if name == "gradio" or (name.startswith("gradio.") and "gradio" in sys.modules):
            try:
                import gradio as gr
                _patch_gradio_launch(gr)
            except (ImportError, AttributeError):
                pass
        
        # Patch trackio UI when available
        if name.startswith("trackio") and "trackio.ui" in sys.modules:
            _patch_trackio_ui()
                
        return result
    
    # Set the patched import function
    if isinstance(__builtins__, dict):
        __builtins__['__import__'] = patched_import
    else:
        __builtins__.__import__ = patched_import


def _patch_gradio_launch(gr_module) -> None:
    """Thread-safe patch of Gradio's launch method."""
    global _gradio_patched
    
    with _patch_lock:
        if _gradio_patched or hasattr(gr_module.Blocks, '_original_launch'):
            return
            
        original_blocks_launch = gr_module.Blocks.launch
        
        @wraps(original_blocks_launch)
        def patched_blocks_launch(self, *args, **kwargs):
            """Patched launch method that enables MCP server and API by default."""
            
            # Enable MCP server if not explicitly disabled
            kwargs.setdefault('mcp_server', True)
            kwargs.setdefault('show_api', True)
            
            # Store MCP server status for reference
            if kwargs.get('mcp_server', False):
                os.environ['TRACKIO_MCP_ENABLED'] = 'true'
                
            result = original_blocks_launch(self, *args, **kwargs)
            
            # Print MCP server info if enabled and not quiet
            if (kwargs.get('mcp_server', False) and 
                not kwargs.get('quiet', False) and 
                hasattr(self, 'local_url') and self.local_url):
                
                mcp_url = f"{self.local_url.rstrip('/')}/gradio_api/mcp/sse"
                print(f"MCP Server: {mcp_url}")
                print(f"MCP Schema: {self.local_url.rstrip('/')}/gradio_api/mcp/schema")
                
            return result
        
        # Apply the patch atomically
        gr_module.Blocks._original_launch = original_blocks_launch
        gr_module.Blocks.launch = patched_blocks_launch
        _gradio_patched = True
        print("trackio-mcp: MCP functionality enabled")


def _patch_trackio_ui() -> None:
    """Patch trackio UI components when available."""
    try:
        import trackio.ui
        
        # Patch trackio demo if it exists and hasn't been patched
        if hasattr(trackio.ui, 'demo') and not hasattr(trackio.ui.demo, '_mcp_patched'):
            demo = trackio.ui.demo
            if hasattr(demo, 'launch'):
                original_demo_launch = demo.launch
                
                @wraps(original_demo_launch)
                def patched_demo_launch(*args, **kwargs):
                    kwargs.setdefault('mcp_server', True)
                    kwargs.setdefault('show_api', True)
                    return original_demo_launch(*args, **kwargs)
                
                demo.launch = patched_demo_launch
                demo._mcp_patched = True
                
    except (ImportError, AttributeError):
        pass  # trackio UI not available or no demo


def restore_imports() -> None:
    """Restore original import behavior (mainly for testing)."""
    global _original_import, _gradio_patched
    
    if _original_import is not None:
        # Restore based on builtins type
        if isinstance(__builtins__, dict):
            __builtins__['__import__'] = _original_import
        else:
            __builtins__.__import__ = _original_import
        _original_import = None
        _gradio_patched = False