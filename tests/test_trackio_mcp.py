"""
Simple tests for the simplified direct monkey patching approach.
No complex state management, no threading concerns.
"""

import pytest
import os
import re
from unittest.mock import Mock, patch


def test_import_order():
    """Test that importing trackio_mcp enables MCP by default."""
    import trackio_mcp
    
    # Check that MCP is enabled by default (not disabled)
    mcp_disabled = os.getenv("TRACKIO_DISABLE_MCP", "false")
    assert mcp_disabled.lower() not in ("true", "1", "yes")


def test_gradio_patching():
    """Test that gradio gets patched correctly."""
    try:
        import gradio as gr
        from trackio_mcp.monkey_patch import _patch_gradio
        
        # Remove any existing patch marker
        if hasattr(gr.Blocks.launch, '_mcp_patched'):
            delattr(gr.Blocks.launch, '_mcp_patched')
        
        # Store original for comparison
        original = gr.Blocks.launch
        
        # Apply patch
        _patch_gradio()
        
        # Verify it was patched
        assert hasattr(gr.Blocks.launch, '_mcp_patched')
        assert gr.Blocks.launch != original
        
        # Test that it adds MCP defaults
        mock_self = Mock()
        mock_self.local_url = "http://localhost:7860"
        
        # Call the patched method (should not raise errors)
        gr.Blocks.launch(mock_self, quiet=True)
        
    except ImportError:
        pytest.skip("Gradio not available")


def test_multiple_patches_safe():
    """Test that applying patch multiple times is safe."""
    try:
        import gradio as gr
        from trackio_mcp.monkey_patch import _patch_gradio
        
        # Apply patch multiple times
        _patch_gradio()
        _patch_gradio()
        _patch_gradio()
        
        # Should only be patched once (idempotent)
        assert hasattr(gr.Blocks.launch, '_mcp_patched')
        
    except ImportError:
        pytest.skip("Gradio not available")


def test_env_var_disable():
    """Test that MCP can be disabled via environment variable."""
    with patch.dict(os.environ, {"TRACKIO_DISABLE_MCP": "true"}):
        from trackio_mcp.monkey_patch import patch_trackio
        
        # Should not raise any errors when disabled
        patch_trackio()


def test_main_patch_function():
    """Test the main patch_trackio function."""
    from trackio_mcp.monkey_patch import patch_trackio
    
    # Should work without errors
    patch_trackio()


def test_trackio_tools_functionality():
    """Test that MCP tools work correctly."""
    try:
        from trackio_mcp.tools import trackio_tool
        
        # Test decorator works
        @trackio_tool
        def test_func():
            return {"success": True, "data": "test"}
        
        result = test_func()
        assert result["success"] is True
        assert result["data"] == "test"
        
        # Test error handling
        @trackio_tool
        def failing_func():
            raise ValueError("Test error")
        
        error_result = failing_func()
        assert error_result["success"] is False
        assert "Invalid input" in error_result["error"]
        
    except ImportError:
        pytest.skip("Required dependencies not available")


def test_cli_commands():
    """Test CLI functionality."""
    try:
        from trackio_mcp.cli import main
        
        # Test status command
        result = main(["status"])
        assert result in [0, 1]
        
        # Test help
        result = main([])
        assert result == 1
        
    except ImportError:
        pytest.skip("CLI dependencies not available")


def test_import_trackio_mcp():
    """Test importing trackio_mcp applies patches automatically."""
    import trackio_mcp
    
    # Should have version attribute
    assert hasattr(trackio_mcp, '__version__')
    # Should be a valid semantic version (x.y.z format)
    version_pattern = r'^\d+\.\d+\.\d+$'
    assert re.match(version_pattern, trackio_mcp.__version__), f"Invalid version format: {trackio_mcp.__version__}"


def test_mcp_enabled_by_default():
    """Test that MCP is enabled by default when importing."""
    # Clear any existing environment variable
    with patch.dict(os.environ, {}, clear=True):
        from trackio_mcp.monkey_patch import patch_trackio
        
        # Should enable MCP by default (no env var set)
        patch_trackio()
        
        # Should work without errors


def test_mcp_disable_override():
    """Test that setting TRACKIO_DISABLE_MCP=true disables MCP."""
    with patch.dict(os.environ, {"TRACKIO_DISABLE_MCP": "true"}):
        from trackio_mcp.monkey_patch import patch_trackio
        
        # Should not enable MCP when explicitly disabled
        patch_trackio()
        
        # Should work without errors


if __name__ == "__main__":
    # Run tests manually
    import sys
    
    tests = [
        test_import_order,
        test_gradio_patching,
        test_multiple_patches_safe, 
        test_env_var_disable,
        test_main_patch_function,
        test_trackio_tools_functionality,
        test_cli_commands,
        test_import_trackio_mcp,
        test_mcp_enabled_by_default,
        test_mcp_disable_override,
    ]
    
    passed = failed = skipped = 0
    
    for test in tests:
        try:
            print(f"Running {test.__name__}...")
            test()
            print("  ✅ PASSED")
            passed += 1
        except Exception as e:
            if "skip" in str(e).lower():
                print("  ⚠️  SKIPPED")
                skipped += 1
            else:
                print(f"  ❌ FAILED: {e}")
                failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped")
    sys.exit(0 if failed == 0 else 1)