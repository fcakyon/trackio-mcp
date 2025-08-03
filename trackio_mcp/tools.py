"""
Simplified MCP tools for trackio functionality.
"""

import traceback
from functools import wraps
from typing import Any, Dict, List, Optional, Union

try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False


def trackio_tool(func):
    """Decorator for trackio MCP tools with simplified error handling."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ImportError, ModuleNotFoundError) as e:
            return {"success": False, "error": f"trackio not available: {e}"}
        except (ValueError, KeyError, TypeError) as e:
            return {"success": False, "error": f"Invalid input: {e}"}
        except Exception as e:
            # Log unexpected errors but don't expose internals
            import logging
            logging.exception(f"Unexpected error in {func.__name__}")
            return {"success": False, "error": "Internal server error"}
    return wrapper


def register_trackio_tools() -> Optional[gr.Blocks]:
    """Register trackio-specific MCP tools as a Gradio interface."""
    
    if not GRADIO_AVAILABLE:
        return None
        
    try:
        from trackio.sqlite_storage import SQLiteStorage
        from trackio import ui as trackio_ui
    except ImportError:
        return None

    with gr.Blocks(title="Trackio MCP Tools") as trackio_tools:
        
        @gr.api
        @trackio_tool
        def get_projects() -> Dict[str, Any]:
            """Get list of all trackio projects."""
            projects = SQLiteStorage.get_projects()
            return {
                "success": True,
                "projects": projects,
                "count": len(projects)
            }

        @gr.api
        @trackio_tool 
        def get_runs(project: str) -> Dict[str, Any]:
            """Get list of all runs for a specific project."""
            if not project:
                raise ValueError("Project name is required")
                    
            runs = SQLiteStorage.get_runs(project)
            return {
                "success": True,
                "project": project,
                "runs": runs,
                "count": len(runs)
            }

        @gr.api
        @trackio_tool
        def filter_runs(project: str, filter_text: str = "") -> Dict[str, Any]:
            """Filter runs by text pattern."""
            if not project:
                raise ValueError("Project name is required")
                    
            all_runs = SQLiteStorage.get_runs(project)
            filtered_runs = [r for r in all_runs if filter_text.lower() in r.lower()] if filter_text else all_runs
                    
            return {
                "success": True,
                "project": project,
                "filter": filter_text,
                "runs": filtered_runs,
                "total_runs": len(all_runs),
                "filtered_count": len(filtered_runs)
            }

        @gr.api
        @trackio_tool
        def get_run_metrics(project: str, run: str) -> Dict[str, Any]:
            """Get metrics data for a specific run."""
            if not project or not run:
                raise ValueError("Both project and run names are required")
                    
            metrics = SQLiteStorage.get_metrics(project, run)
            return {
                "success": True,
                "project": project,
                "run": run,
                "metrics": metrics,
                "count": len(metrics)
            }

        @gr.api
        @trackio_tool
        def get_available_metrics(project: str, runs: Optional[str] = None) -> Dict[str, Any]:
            """Get all available metric names for a project."""
            if not project:
                raise ValueError("Project name is required")
            
            # Parse runs parameter
            run_list = []
            if runs:
                try:
                    import json
                    run_list = json.loads(runs) if isinstance(runs, str) else runs
                except json.JSONDecodeError:
                    run_list = [r.strip() for r in runs.split(",")]
            
            if not run_list:
                run_list = SQLiteStorage.get_runs(project)
            
            # Get available metrics
            if hasattr(trackio_ui, 'get_available_metrics'):
                available_metrics = trackio_ui.get_available_metrics(project, run_list)
            else:
                # Fallback implementation
                all_metrics = set()
                for run in run_list:
                    metrics = SQLiteStorage.get_metrics(project, run)
                    if metrics:
                        import pandas as pd
                        df = pd.DataFrame(metrics)
                        numeric_cols = df.select_dtypes(include="number").columns
                        numeric_cols = [c for c in numeric_cols if c not in ["step", "timestamp"]]
                        all_metrics.update(numeric_cols)
                available_metrics = sorted(list(all_metrics))
            
            return {
                "success": True,
                "project": project,
                "runs": run_list,
                "metrics": available_metrics,
                "count": len(available_metrics)
            }

        @gr.api
        @trackio_tool
        def load_run_data(project: str, run: str, smoothing: bool = False, x_axis: str = "step") -> Dict[str, Any]:
            """Load and process run data with optional smoothing."""
            if not project or not run:
                raise ValueError("Both project and run names are required")
            
            # Use trackio's function if available
            if hasattr(trackio_ui, 'load_run_data'):
                df = trackio_ui.load_run_data(project, run, smoothing, x_axis)
                if df is not None:
                    # Convert DataFrame to dict - Gradio handles serialization
                    data = df.to_dict('records')
                    return {
                        "success": True,
                        "project": project,
                        "run": run,
                        "x_axis": x_axis,
                        "smoothing": smoothing,
                        "data": data,
                        "rows": len(data)
                    }
                else:
                    raise ValueError("No data found for the specified run")
            else:
                # Fallback: return raw metrics
                metrics = SQLiteStorage.get_metrics(project, run)
                return {
                    "success": True,
                    "project": project,
                    "run": run,
                    "x_axis": x_axis,
                    "smoothing": smoothing,
                    "data": metrics,
                    "rows": len(metrics)
                }

        @gr.api
        @trackio_tool
        def get_project_summary(project: str) -> Dict[str, Any]:
            """Get comprehensive project summary including runs, metrics, and statistics."""
            if not project:
                raise ValueError("Project name is required")
            
            runs = SQLiteStorage.get_runs(project)
            if not runs:
                return {
                    "success": True,
                    "project": project,
                    "runs": [],
                    "metrics": [],
                    "summary": "No runs found in this project"
                }
            
            # Get metrics for all runs
            all_metrics = set()
            run_stats = {}
            
            for run in runs:
                metrics = SQLiteStorage.get_metrics(project, run)
                run_stats[run] = {
                    "metric_count": len(metrics),
                    "steps": len(set(m.get("step", 0) for m in metrics)) if metrics else 0
                }
                
                if metrics:
                    import pandas as pd
                    df = pd.DataFrame(metrics)
                    numeric_cols = df.select_dtypes(include="number").columns
                    numeric_cols = [c for c in numeric_cols if c not in ["step", "timestamp"]]
                    all_metrics.update(numeric_cols)
            
            return {
                "success": True,
                "project": project,
                "runs": runs,
                "run_count": len(runs),
                "metrics": sorted(list(all_metrics)),
                "metric_count": len(all_metrics),
                "run_stats": run_stats
            }

        # Simplified UI for testing
        gr.Markdown("# Trackio MCP Tools")
        gr.Markdown("This interface exposes trackio functionality as MCP tools.")
        
        with gr.Tab("Projects"):
            get_projects_btn = gr.Button("Get Projects")
            projects_output = gr.JSON(label="Projects")
            get_projects_btn.click(get_projects, outputs=projects_output)
            
        with gr.Tab("Runs"):
            with gr.Row():
                project_input = gr.Textbox(label="Project", placeholder="Enter project name")
                filter_input = gr.Textbox(label="Filter", placeholder="Filter runs (optional)")
            get_runs_btn = gr.Button("Get Runs")
            filter_runs_btn = gr.Button("Filter Runs")
            runs_output = gr.JSON(label="Runs")
            
            get_runs_btn.click(get_runs, inputs=project_input, outputs=runs_output)
            filter_runs_btn.click(filter_runs, inputs=[project_input, filter_input], outputs=runs_output)
            
        with gr.Tab("Summary"):
            summary_project_input = gr.Textbox(label="Project", placeholder="Enter project name")
            get_summary_btn = gr.Button("Get Project Summary")
            summary_output = gr.JSON(label="Project Summary")
            get_summary_btn.click(get_project_summary, inputs=summary_project_input, outputs=summary_output)

    return trackio_tools


def launch_trackio_mcp_server(port: int = 7861, share: bool = False) -> None:
    """Launch a standalone trackio MCP server."""
    
    trackio_tools = register_trackio_tools()
    if trackio_tools is None:
        print("Failed to create trackio MCP tools interface")
        return
        
    print(f"Launching Trackio MCP Server on port {port}")
    
    trackio_tools.launch(
        server_port=port,
        share=share,
        mcp_server=True,
        show_api=True,
        quiet=False
    )