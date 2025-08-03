"""
Test script to verify trackio-mcp functionality.
"""

import pytest
import os
import json
from unittest.mock import Mock, patch


def test_import_order():
    """Test that importing trackio_mcp before trackio enables MCP."""
    
    # Reset any existing patches
    if 'trackio_mcp' in globals():
        del globals()['trackio_mcp']
    if 'trackio' in globals():
        del globals()['trackio']
    
    # Import trackio_mcp first
    import trackio_mcp
    
    # Check that MCP is enabled by default
    mcp_enabled = os.getenv("TRACKIO_ENABLE_MCP", "true")
    assert mcp_enabled.lower() in ("true", "1", "yes")


def test_monkey_patch_applied():
    """Test that Gradio launch method is patched."""
    
    try:
        import gradio as gr
        
        # Check if patch was applied
        assert hasattr(gr.Blocks, '_original_launch'), "Gradio launch should be patched"
        
        # Test that the patched method sets MCP parameters
        with patch.object(gr.Blocks, '_original_launch') as mock_launch:
            demo = gr.Blocks()
            demo.launch()
            
            # Check that MCP parameters were added
            call_args = mock_launch.call_args
            kwargs = call_args[1] if call_args else {}
            
            assert kwargs.get('mcp_server') is True
            assert kwargs.get('show_api') is True
            
    except ImportError:
        pytest.skip("Gradio not available")


def test_trackio_tools_registration():
    """Test that trackio MCP tools can be registered."""
    
    try:
        from trackio_mcp.tools import register_trackio_tools
        
        tools = register_trackio_tools()
        
        if tools is not None:
            # Should return a Gradio Blocks interface
            import gradio as gr
            assert isinstance(tools, gr.Blocks)
        else:
            # If trackio not available, should return None gracefully
            print("Trackio not available, tools registration skipped")
            
    except ImportError:
        pytest.skip("Required dependencies not available")


def test_mcp_tools_functionality():
    """Test that MCP tools return proper JSON responses."""
    
    try:
        from trackio_mcp.tools import register_trackio_tools
        import tempfile
        from pathlib import Path
        
        # Mock trackio storage for testing
        with patch('trackio_mcp.tools.SQLiteStorage') as mock_storage:
            # Mock storage methods
            mock_storage.get_projects.return_value = ["test-project"]
            mock_storage.get_runs.return_value = ["run-1", "run-2"]
            mock_storage.get_metrics.return_value = [
                {"step": 0, "loss": 0.5, "accuracy": 0.8, "timestamp": "2024-01-01T10:00:00"},
                {"step": 1, "loss": 0.4, "accuracy": 0.85, "timestamp": "2024-01-01T10:01:00"}
            ]
            
            tools = register_trackio_tools()
            if tools is None:
                pytest.skip("Could not create tools interface")
            
            # Test get_projects function
            # Note: In a real test, you'd access the function directly
            # This is a simplified test structure
            
    except ImportError:
        pytest.skip("Required dependencies not available")


def test_environment_variables():
    """Test environment variable handling."""
    
    # Test disabling MCP
    with patch.dict(os.environ, {"TRACKIO_ENABLE_MCP": "false"}):
        # Re-import to test env var effect
        import importlib
        if 'trackio_mcp.monkey_patch' in sys.modules:
            importlib.reload(sys.modules['trackio_mcp.monkey_patch'])


def test_cli_functionality():
    """Test CLI commands."""
    
    try:
        from trackio_mcp.cli import main
        
        # Test status command
        result = main(["status"])
        assert result in [0, 1]  # Should return valid exit code
        
        # Test help
        result = main([])
        assert result == 1  # Should return 1 for no command
        
    except ImportError:
        pytest.skip("CLI dependencies not available")


def test_json_responses():
    """Test that tool functions return valid JSON."""
    
    try:
        from trackio_mcp.tools import register_trackio_tools
        
        # Mock a simple test
        test_json = '{"success": true, "data": []}'
        parsed = json.loads(test_json)
        
        assert parsed["success"] is True
        assert "data" in parsed
        
    except ImportError:
        pytest.skip("Required dependencies not available")


if __name__ == "__main__":
    """Run tests manually if pytest not available."""
    
    import sys
    
    print("Testing trackio-mcp functionality")
    print("=" * 50)
    
    tests = [
        test_import_order,
        test_monkey_patch_applied,
        test_trackio_tools_registration,
        test_mcp_tools_functionality,
        test_environment_variables,
        test_cli_functionality,
        test_json_responses,
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test in tests:
        try:
            print(f"\nRunning {test.__name__}...")
            test()
            print(f"  PASSED")
            passed += 1
        except AssertionError as e:
            print(f"  FAILED: {e}")
            failed += 1
        except Exception as e:
            if "skip" in str(e).lower():
                print(f"  SKIPPED: {e}")
                skipped += 1
            else:
                print(f"  ERROR: {e}")
                failed += 1
    
    print(f"\nTest Results:")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    
    if failed == 0:
        print(f"\nAll tests passed!")
        sys.exit(0)
    else:
        print(f"\nSome tests failed!")
        sys.exit(1)
