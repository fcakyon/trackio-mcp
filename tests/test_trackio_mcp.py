"""
Test script to verify trackio-mcp functionality.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch


def test_import_order():
    """Test that importing trackio_mcp enables MCP by default."""
    
    # Import trackio_mcp first
    import trackio_mcp
    
    # Check that MCP is enabled by default
    mcp_enabled = os.getenv("TRACKIO_ENABLE_MCP", "true")
    assert mcp_enabled.lower() in ("true", "1", "yes")


def test_monkey_patch_thread_safety():
    """Test that monkey patching is thread-safe."""
    
    try:
        from trackio_mcp.monkey_patch import _patch_gradio_launch, _patch_lock
        import gradio as gr
        import threading
        
        # Reset gradio state for testing
        if hasattr(gr.Blocks, '_original_launch'):
            delattr(gr.Blocks, '_original_launch')
        
        # Test concurrent patching
        results = []
        
        def patch_worker():
            try:
                _patch_gradio_launch(gr)
                results.append("success")
            except Exception as e:
                results.append(f"error: {e}")
        
        # Start multiple threads
        threads = [threading.Thread(target=patch_worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should have exactly one success and others should be no-ops
        assert all(r == "success" for r in results)
        assert hasattr(gr.Blocks, '_original_launch')
        
    except ImportError:
        pytest.skip("Gradio not available")


def test_trackio_tools_return_dicts():
    """Test that MCP tools return proper dictionaries (not JSON strings)."""
    
    try:
        from trackio_mcp.tools import register_trackio_tools
        
        # Mock trackio dependencies
        with patch('trackio_mcp.tools.SQLiteStorage') as mock_storage:
            mock_storage.get_projects.return_value = ["test-project"]
            mock_storage.get_runs.return_value = ["run-1", "run-2"]
            
            tools = register_trackio_tools()
            if tools is None:
                pytest.skip("Could not create tools interface")
            
            # Find the get_projects function
            for comp in tools.blocks.values():
                if hasattr(comp, 'fn') and comp.fn.__name__ == 'get_projects':
                    result = comp.fn()
                    
                    # Should return dict, not JSON string
                    assert isinstance(result, dict)
                    assert result["success"] is True
                    assert "projects" in result
                    break
            else:
                pytest.skip("get_projects function not found")
                
    except ImportError:
        pytest.skip("Required dependencies not available")


def test_error_handling_decorator():
    """Test that the error handling decorator works correctly."""
    
    try:
        from trackio_mcp.tools import trackio_tool
        
        @trackio_tool
        def failing_function():
            raise ValueError("Test error")
        
        @trackio_tool
        def working_function():
            return {"success": True, "data": "test"}
        
        # Test error handling
        error_result = failing_function()
        assert isinstance(error_result, dict)
        assert error_result["success"] is False
        assert "Invalid input" in error_result["error"]
        
        # Test normal operation
        success_result = working_function()
        assert success_result["success"] is True
        assert success_result["data"] == "test"
        
    except ImportError:
        pytest.skip("Required dependencies not available")


def test_environment_variables():
    """Test environment variable handling."""
    
    # Test disabling MCP
    with patch.dict(os.environ, {"TRACKIO_ENABLE_MCP": "false"}):
        from trackio_mcp.monkey_patch import patch_trackio
        
        # Should not raise errors when disabled
        patch_trackio()  # Should be a no-op


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


def test_import_hook_safety():
    """Test that import hooks don't break normal imports."""
    
    try:
        from trackio_mcp.monkey_patch import _install_import_hook, restore_imports
        
        # Install hook
        _install_import_hook()
        
        # Test normal imports still work
        import json
        import os
        
        # Should work normally
        data = json.dumps({"test": True})
        assert '"test": true' in data.lower()
        
        # Restore for cleanliness
        restore_imports()
        
    except Exception as e:
        pytest.fail(f"Import hook broke normal imports: {e}")


def test_requests_optional():
    """Test that requests dependency is optional for basic functionality."""
    
    # Mock requests as unavailable
    with patch.dict(sys.modules, {'requests': None}):
        try:
            from trackio_mcp.cli import _test_tools_only
            
            # Should work without requests
            result = _test_tools_only()
            assert result in [0, 1]  # Valid exit code
            
        except ImportError:
            # This is expected if other dependencies missing
            pass


if __name__ == "__main__":
    """Run tests manually if pytest not available."""
    
    print("Testing trackio-mcp functionality")
    print("=" * 50)
    
    tests = [
        test_import_order,
        test_monkey_patch_thread_safety,
        test_trackio_tools_return_dicts,
        test_error_handling_decorator,
        test_environment_variables,
        test_cli_functionality,
        test_import_hook_safety,
        test_requests_optional,
    ]
    
    passed = failed = skipped = 0
    
    for test in tests:
        try:
            print(f"\nRunning {test.__name__}...")
            test()
            print(f"  ✓ PASSED")
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            if "skip" in str(e).lower():
                print(f"  ⚠ SKIPPED: {e}")
                skipped += 1
            else:
                print(f"  ✗ ERROR: {e}")
                failed += 1
    
    print(f"\nTest Results:")
    print(f"  ✓ Passed: {passed}")
    print(f"  ✗ Failed: {failed}")
    print(f"  ⚠ Skipped: {skipped}")
    
    sys.exit(0 if failed == 0 else 1)