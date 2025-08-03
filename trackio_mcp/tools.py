"""
Additional MCP tools for trackio functionality.
"""

import json
import traceback
from typing import Any, Dict, List, Optional

try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False


def register_trackio_tools() -> Optional[gr.Blocks]:
    """
    Register additional trackio-specific MCP tools as a Gradio interface.
    Returns a Gradio Blocks interface that can be launched as an MCP server.
    """
    
    if not GRADIO_AVAILABLE:
        print("trackio-mcp: gradio not available, cannot register tools")
        return None
        
    try:
        from trackio.sqlite_storage import SQLiteStorage
        from trackio import ui as trackio_ui
    except ImportError as e:
        print(f"trackio-mcp: trackio not available: {e}")
        return None

    with gr.Blocks(title="Trackio MCP Tools") as trackio_tools:
        
        @gr.api
        def get_projects() -> str:
            """Get list of all trackio projects."""
            try:
                projects = SQLiteStorage.get_projects()
                return json.dumps({
                    "success": True,
                    "projects": projects,
                    "count": len(projects)
                })
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })

        @gr.api 
        def get_runs(project: str) -> str:
            """Get list of all runs for a specific project."""
            try:
                if not project:
                    return json.dumps({
                        "success": False,
                        "error": "Project name is required"
                    })
                    
                runs = SQLiteStorage.get_runs(project)
                return json.dumps({
                    "success": True,
                    "project": project,
                    "runs": runs,
                    "count": len(runs)
                })
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })

        @gr.api
        def filter_runs(project: str, filter_text: str = "") -> str:
            """Filter runs by text pattern."""
            try:
                if not project:
                    return json.dumps({
                        "success": False,
                        "error": "Project name is required"
                    })
                    
                all_runs = SQLiteStorage.get_runs(project)
                if filter_text:
                    filtered_runs = [r for r in all_runs if filter_text.lower() in r.lower()]
                else:
                    filtered_runs = all_runs
                    
                return json.dumps({
                    "success": True,
                    "project": project,
                    "filter": filter_text,
                    "runs": filtered_runs,
                    "total_runs": len(all_runs),
                    "filtered_count": len(filtered_runs)
                })
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })

        @gr.api
        def get_run_metrics(project: str, run: str) -> str:
            """Get metrics data for a specific run."""
            try:
                if not project or not run:
                    return json.dumps({
                        "success": False,
                        "error": "Both project and run names are required"
                    })
                    
                metrics = SQLiteStorage.get_metrics(project, run)
                return json.dumps({
                    "success": True,
                    "project": project,
                    "run": run,
                    "metrics": metrics,
                    "count": len(metrics)
                })
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })

        @gr.api
        def get_available_metrics(project: str, runs: Optional[str] = None) -> str:
            """Get all available metrics across runs for a project."""
            try:
                if not project:
                    return json.dumps({
                        "success": False,
                        "error": "Project name is required"
                    })
                
                # Parse runs parameter if provided
                run_list = []
                if runs:
                    try:
                        run_list = json.loads(runs) if isinstance(runs, str) else runs
                    except json.JSONDecodeError:
                        # Treat as comma-separated string
                        run_list = [r.strip() for r in runs.split(",")]
                
                if not run_list:
                    run_list = SQLiteStorage.get_runs(project)
                
                # Use trackio's existing function if available
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
                
                return json.dumps({
                    "success": True,
                    "project": project,
                    "runs": run_list,
                    "metrics": available_metrics,
                    "count": len(available_metrics)
                })
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })

        @gr.api
        def load_run_data(project: str, run: str, smoothing: bool = False, x_axis: str = "step") -> str:
            """Load and process run data with optional smoothing."""
            try:
                if not project or not run:
                    return json.dumps({
                        "success": False,
                        "error": "Both project and run names are required"
                    })
                
                # Use trackio's existing function if available
                if hasattr(trackio_ui, 'load_run_data'):
                    df = trackio_ui.load_run_data(project, run, smoothing, x_axis)
                    if df is not None:
                        # Convert DataFrame to JSON-serializable format
                        data = df.to_dict('records')
                        return json.dumps({
                            "success": True,
                            "project": project,
                            "run": run,
                            "x_axis": x_axis,
                            "smoothing": smoothing,
                            "data": data,
                            "rows": len(data)
                        })
                    else:
                        return json.dumps({
                            "success": False,
                            "error": "No data found for the specified run"
                        })
                else:
                    # Fallback: just return raw metrics
                    metrics = SQLiteStorage.get_metrics(project, run)
                    return json.dumps({
                        "success": True,
                        "project": project,
                        "run": run,
                        "x_axis": x_axis,
                        "smoothing": smoothing,
                        "data": metrics,
                        "rows": len(metrics)
                    })
                    
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })

        @gr.api
        def get_project_summary(project: str) -> str:
            """Get a comprehensive summary of a project including runs, metrics, and statistics."""
            try:
                if not project:
                    return json.dumps({
                        "success": False,
                        "error": "Project name is required"
                    })
                
                runs = SQLiteStorage.get_runs(project)
                if not runs:
                    return json.dumps({
                        "success": True,
                        "project": project,
                        "runs": [],
                        "metrics": [],
                        "summary": "No runs found in this project"
                    })
                
                # Get metrics for all runs
                all_metrics = set()
                run_stats = {}
                
                for run in runs:
                    metrics = SQLiteStorage.get_metrics(project, run)
                    run_stats[run] = {
                        "metric_count": len(metrics),
                        "steps": len(set(m.get("step", 0) for m in metrics))
                    }
                    
                    if metrics:
                        import pandas as pd
                        df = pd.DataFrame(metrics)
                        numeric_cols = df.select_dtypes(include="number").columns
                        numeric_cols = [c for c in numeric_cols if c not in ["step", "timestamp"]]
                        all_metrics.update(numeric_cols)
                
                return json.dumps({
                    "success": True,
                    "project": project,
                    "runs": runs,
                    "run_count": len(runs),
                    "metrics": sorted(list(all_metrics)),
                    "metric_count": len(all_metrics),
                    "run_stats": run_stats
                })
                
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })

        # Add interface components for testing (optional)
        gr.Markdown("# Trackio MCP Tools")
        gr.Markdown("This interface exposes trackio functionality as MCP tools.")
        
        with gr.Tab("Projects"):
            get_projects_btn = gr.Button("Get Projects")
            projects_output = gr.Textbox(label="Projects", lines=5)
            get_projects_btn.click(get_projects, outputs=projects_output)
            
        with gr.Tab("Runs"):
            with gr.Row():
                project_input = gr.Textbox(label="Project", placeholder="Enter project name")
                filter_input = gr.Textbox(label="Filter", placeholder="Filter runs (optional)")
            get_runs_btn = gr.Button("Get Runs")
            filter_runs_btn = gr.Button("Filter Runs")
            runs_output = gr.Textbox(label="Runs", lines=5)
            
            get_runs_btn.click(get_runs, inputs=project_input, outputs=runs_output)
            filter_runs_btn.click(filter_runs, inputs=[project_input, filter_input], outputs=runs_output)
            
        with gr.Tab("Metrics"):
            with gr.Row():
                metrics_project_input = gr.Textbox(label="Project", placeholder="Enter project name")
                run_input = gr.Textbox(label="Run", placeholder="Enter run name")
            
            get_metrics_btn = gr.Button("Get Run Metrics")
            get_available_metrics_btn = gr.Button("Get Available Metrics")
            metrics_output = gr.Textbox(label="Metrics", lines=10)
            
            get_metrics_btn.click(get_run_metrics, inputs=[metrics_project_input, run_input], outputs=metrics_output)
            get_available_metrics_btn.click(get_available_metrics, inputs=metrics_project_input, outputs=metrics_output)

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
