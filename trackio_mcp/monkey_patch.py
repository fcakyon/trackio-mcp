"""
Monkey-patch trackio to enable MCP server functionality automatically.
"""

import os
from functools import wraps
from typing import Any, Callable


def patch_trackio() -> None:
    """Apply monkey patches to enable MCP server functionality in trackio."""
    
    # Check if MCP should be enabled (can be controlled via env var)
    enable_mcp = os.getenv("TRACKIO_ENABLE_MCP", "true").lower() in ("true", "1", "yes")
    
    if not enable_mcp:
        return
        
    try:
        import gradio as gr
        _patch_gradio_launch(gr)
        print("trackio-mcp: Enabled MCP server functionality")
    except ImportError:
        print("trackio-mcp: gradio not found, MCP functionality not enabled")


def _patch_gradio_launch(gr_module) -> None:
    """Patch Gradio's launch method to enable MCP server by default."""
    
    # Store original launch methods
    if hasattr(gr_module.Blocks, '_original_launch'):
        # Already patched
        return
        
    original_blocks_launch = gr_module.Blocks.launch
    
    @wraps(original_blocks_launch)
    def patched_blocks_launch(self, *args, **kwargs):
        """Patched launch method that enables MCP server and API by default."""
        
        # Enable MCP server if not explicitly disabled
        if 'mcp_server' not in kwargs:
            kwargs['mcp_server'] = True
            
        # Enable API if not explicitly disabled (needed for MCP)
        if 'show_api' not in kwargs:
            kwargs['show_api'] = True
            
        # Store MCP server status for reference
        if kwargs.get('mcp_server', False):
            os.environ['TRACKIO_MCP_ENABLED'] = 'true'
            
        result = original_blocks_launch(self, *args, **kwargs)
        
        # Print MCP server info if enabled
        if kwargs.get('mcp_server', False) and not kwargs.get('quiet', False):
            if hasattr(self, 'local_url'):
                mcp_url = f"{self.local_url.rstrip('/')}/gradio_api/mcp/sse"
                print(f"MCP Server available at: {mcp_url}")
                print(f"MCP Tools schema: {self.local_url.rstrip('/')}/gradio_api/mcp/schema")
                
        return result
    
    # Apply the patch
    gr_module.Blocks.launch = patched_blocks_launch
    gr_module.Blocks._original_launch = original_blocks_launch


def _patch_trackio_imports() -> None:
    """Patch trackio imports to ensure compatibility."""
    
    try:
        # Import trackio modules to trigger any initialization
        import trackio.ui
        import trackio.deploy
        
        # Patch specific trackio demo launches if needed
        if hasattr(trackio.ui, 'demo'):
            demo = trackio.ui.demo
            if hasattr(demo, 'launch') and not hasattr(demo, '_mcp_patched'):
                original_demo_launch = demo.launch
                
                @wraps(original_demo_launch)
                def patched_demo_launch(*args, **kwargs):
                    if 'mcp_server' not in kwargs:
                        kwargs['mcp_server'] = True
                    if 'show_api' not in kwargs:
                        kwargs['show_api'] = True
                    return original_demo_launch(*args, **kwargs)
                
                demo.launch = patched_demo_launch
                demo._mcp_patched = True
                
    except ImportError:
        # trackio not yet imported, patches will be applied when it is
        pass


# Apply trackio-specific patches when this module loads
_patch_trackio_imports()
