"""
Ultra-simple direct monkey patching for trackio MCP functionality.
No import hooks, no threading, no complexity. Just direct patching.
"""

import os
from functools import wraps


def patch_trackio() -> None:
    """Apply monkey patches to enable MCP server functionality."""
    
    # Check if MCP should be disabled (default: enabled)
    if os.getenv("TRACKIO_DISABLE_MCP", "false").lower() in ("true", "1", "yes"):
        return
    
    # Simple direct patches
    _patch_gradio()
    _patch_trackio_ui()


def _patch_gradio() -> None:
    """Patch Gradio launch method to enable MCP by default."""
    try:
        import gradio as gr
        
        # Skip if already patched
        if hasattr(gr.Blocks.launch, '_mcp_patched'):
            return
            
        # Store original method
        original_launch = gr.Blocks.launch
        
        @wraps(original_launch)
        def mcp_enabled_launch(self, *args, **kwargs):
            """Launch with MCP server enabled by default."""
            # Set MCP defaults
            kwargs.setdefault('mcp_server', True)
            kwargs.setdefault('show_api', True)
                
            # Call original method
            result = original_launch(self, *args, **kwargs)
            
            # Show MCP URL (if not quiet)
            if (kwargs.get('mcp_server') and 
                not kwargs.get('quiet') and 
                hasattr(self, 'local_url') and self.local_url):
                print(f"🔗 MCP Server: {self.local_url.rstrip('/')}/gradio_api/mcp/sse")
                
            return result
        
        # Apply patch
        gr.Blocks.launch = mcp_enabled_launch
        mcp_enabled_launch._mcp_patched = True
        print("✅ trackio-mcp: Gradio patched for MCP support")
        
    except ImportError:
        # Gradio not installed - that's okay
        pass


def _patch_trackio_ui() -> None:
    """Patch trackio UI demo launch if it exists."""
    try:
        import trackio.ui
        
        # Patch demo.launch if it exists
        if (hasattr(trackio.ui, 'demo') and 
            hasattr(trackio.ui.demo, 'launch') and
            not hasattr(trackio.ui.demo.launch, '_mcp_patched')):
            
            original_demo_launch = trackio.ui.demo.launch
            
            @wraps(original_demo_launch)
            def mcp_demo_launch(*args, **kwargs):
                kwargs.setdefault('mcp_server', True)
                kwargs.setdefault('show_api', True)
                return original_demo_launch(*args, **kwargs)
            
            trackio.ui.demo.launch = mcp_demo_launch
            mcp_demo_launch._mcp_patched = True
            
    except ImportError:
        # trackio UI not available - that's okay
        pass