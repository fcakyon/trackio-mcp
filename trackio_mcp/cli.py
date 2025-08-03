"""
Command-line interface for trackio-mcp.
"""

import argparse
import sys
from typing import Optional


def main(argv: Optional[list] = None) -> int:
    """Main CLI entry point."""
    
    parser = argparse.ArgumentParser(
        prog="trackio-mcp",
        description="MCP server support for trackio experiment tracking"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Server command
    server_parser = subparsers.add_parser(
        "server", 
        help="Launch standalone trackio MCP server"
    )
    server_parser.add_argument("--port", type=int, default=7861, help="Port for MCP server (default: 7861)")
    server_parser.add_argument("--share", action="store_true", help="Create public Gradio share link")
    server_parser.add_argument("--host", type=str, default="127.0.0.1", help="Host for MCP server (default: 127.0.0.1)")
    
    # Status command
    subparsers.add_parser("status", help="Check trackio-mcp status and configuration")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test MCP server functionality")
    test_parser.add_argument("--url", type=str, help="MCP server URL to test (default: auto-detect)")
    
    args = parser.parse_args(argv)
    
    if args.command == "server":
        return _run_server(args)
    elif args.command == "status":
        return _show_status()
    elif args.command == "test":
        return _test_server(args)
    else:
        parser.print_help()
        return 1


def _run_server(args) -> int:
    """Launch standalone MCP server."""
    try:
        from .tools import launch_trackio_mcp_server
        
        print(f"Starting trackio MCP server on {args.host}:{args.port}")
        if args.share:
            print("Creating public share link...")
            
        launch_trackio_mcp_server(port=args.port, share=args.share)
        return 0
        
    except ImportError as e:
        print(f"Failed to import required modules: {e}")
        print("Make sure trackio and gradio[mcp] are installed")
        return 1
    except Exception as e:
        print(f"Failed to start server: {e}")
        return 1


def _show_status() -> int:
    """Show current status and configuration."""
    import os
    
    print("trackio-mcp Status")
    print("=" * 50)
    
    # Check environment variables
    print("\nEnvironment Variables:")
    mcp_disabled = os.getenv("TRACKIO_DISABLE_MCP", "false")
    
    print(f"  TRACKIO_DISABLE_MCP: {mcp_disabled}")
    print(f"  MCP Status: {'Disabled' if mcp_disabled.lower() in ('true', '1', 'yes') else 'Enabled (default)'}")
    
    # Check imports
    print("\nPackage Status:")
    try:
        import trackio_mcp
        print(f"  trackio-mcp: {trackio_mcp.__version__}")
    except ImportError as e:
        print(f"  trackio-mcp: {e}")
    
    try:
        import trackio
        print(f"  trackio: {trackio.__version__}")
    except ImportError as e:
        print(f"  trackio: {e}")
        
    try:
        import gradio as gr
        print(f"  gradio: {gr.__version__}")
        
        # Check MCP patches
        if hasattr(gr.Blocks.launch, '_mcp_patched'):
            print("  MCP patches: Applied")
        else:
            print("  MCP patches: Not applied")
            
    except ImportError as e:
        print(f"  gradio: {e}")
    
    # Check trackio projects
    print("\nTrackio Projects:")
    try:
        from trackio.sqlite_storage import SQLiteStorage
        projects = SQLiteStorage.get_projects()
        if projects:
            print(f"  Found {len(projects)} projects:")
            for project in projects[:5]:
                runs = SQLiteStorage.get_runs(project)
                print(f"    • {project} ({len(runs)} runs)")
            if len(projects) > 5:
                print(f"    ... and {len(projects) - 5} more")
        else:
            print("  No projects found")
    except Exception as e:
        print(f"  Error checking projects: {e}")
    
    print("\nUsage:")
    print("  Local MCP URL: http://localhost:7860/gradio_api/mcp/sse")
    print("  Tools schema: http://localhost:7860/gradio_api/mcp/schema")
    print("  Start server: trackio-mcp server")
    
    return 0


def _test_server(args) -> int:
    """Test MCP server functionality."""
    url = args.url or "http://localhost:7860"
    mcp_url = f"{url.rstrip('/')}/gradio_api/mcp/sse"
    schema_url = f"{url.rstrip('/')}/gradio_api/mcp/schema"
    
    print(f"Testing MCP server at {url}")
    print("=" * 50)
    
    # Test basic connectivity
    print("\n1. Testing basic connectivity...")
    try:
        import requests
        response = requests.get(url, timeout=5)
        print(f"  Server status: {response.status_code}")
    except ImportError:
        print("  requests not available - skipping HTTP tests")
        return _test_tools_only()
    except Exception as e:
        print(f"  Server not reachable: {e}")
        return 1
    
    # Test MCP endpoint
    print("\n2. Testing MCP endpoint...")
    try:
        response = requests.get(mcp_url, timeout=5)
        print(f"  MCP endpoint status: {response.status_code}")
    except Exception as e:
        print(f"  MCP endpoint error: {e}")
    
    # Test schema endpoint
    print("\n3. Testing schema endpoint...")
    try:
        response = requests.get(schema_url, timeout=5)
        if response.status_code == 200:
            schema = response.json()
            tools = schema.get("paths", {})
            print(f"  Schema available with {len(tools)} endpoints")
        else:
            print(f"  Schema endpoint status: {response.status_code}")
    except Exception as e:
        print(f"  Schema endpoint error: {e}")
    
    return _test_tools_only()


def _test_tools_only() -> int:
    """Test trackio tools without HTTP requests."""
    print("\n4. Testing trackio tools...")
    try:
        from .tools import register_trackio_tools
        tools = register_trackio_tools()
        if tools:
            print("  ✓ Trackio MCP tools available")
            return 0
        else:
            print("  ✗ Trackio MCP tools could not be created")
            return 1
    except Exception as e:
        print(f"  ✗ Trackio tools error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())