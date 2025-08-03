"""
Basic example of using trackio-mcp.

This example shows how to use trackio with MCP server functionality enabled
automatically by importing trackio_mcp first.
"""

# Import trackio_mcp BEFORE trackio to enable MCP functionality
import trackio_mcp

# Now import trackio as usual (MCP server will be enabled automatically)
import trackio as wandb
import random
import time


def simulate_training_run():
    """Simulate a machine learning training run with metrics logging."""
    
    # Initialize trackio run (MCP server will be enabled automatically)
    wandb.init(
        project="mcp-example", 
        name="basic-training",
        config={
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 10,
            "model": "resnet50"
        }
    )
    
    print("Training started with MCP server enabled!")
    print("MCP Server: http://localhost:7860/gradio_api/mcp/sse")
    print("API Schema: http://localhost:7860/gradio_api/mcp/schema")
    
    # Simulate training loop
    for epoch in range(10):
        # Simulate training metrics
        train_loss = 2.0 * (0.8 ** epoch) + random.uniform(0, 0.1)
        train_acc = min(0.95, 0.5 + epoch * 0.05 + random.uniform(0, 0.02))
        
        # Simulate validation metrics  
        val_loss = train_loss - random.uniform(0.01, 0.05)
        val_acc = min(0.97, train_acc + random.uniform(0.01, 0.03))
        
        # Log metrics (these will be available via MCP tools)
        wandb.log({
            "epoch": epoch,
            "train/loss": train_loss,
            "train/accuracy": train_acc,
            "val/loss": val_loss, 
            "val/accuracy": val_acc,
            "learning_rate": 0.001 * (0.95 ** epoch),
            "gpu_memory": random.uniform(0.7, 0.9),
        })
        
        print(f"Epoch {epoch}: train_acc={train_acc:.3f}, val_acc={val_acc:.3f}")
        time.sleep(0.5)  # Simulate training time
    
    wandb.finish()
    print("Training completed!")


def demonstrate_mcp_tools():
    """Demonstrate the MCP tools that are now available."""
    
    print("\n" + "="*50)
    print("MCP TOOLS AVAILABLE FOR AI AGENTS")
    print("="*50)
    
    print("\nCore Trackio Tools (via Gradio API):")
    print("  • log - Log metrics to trackio")
    print("  • upload_db_to_space - Upload database to HF Space")
    
    print("\nExtended Tools (via trackio-mcp):")
    print("  • get_projects - List all trackio projects")
    print("  • get_runs - Get runs for a project")
    print("  • filter_runs - Filter runs by pattern")
    print("  • get_run_metrics - Get metrics for a specific run")
    print("  • get_available_metrics - Get available metric names")
    print("  • load_run_data - Load processed run data")
    print("  • get_project_summary - Get project statistics")
    
    print("\nExample AI Agent Usage:")
    print('  Human: "Show me the latest results from my training"')
    print('  Agent: [Uses get_projects, get_runs, get_run_metrics tools]')
    print('  Agent: "Your latest run achieved 94.7% validation accuracy!"')
    
    print("\nMCP Client Configuration:")
    print('  {')
    print('    "mcpServers": {')
    print('      "trackio": {')
    print('        "url": "http://localhost:7860/gradio_api/mcp/sse"')
    print('      }')
    print('    }')
    print('  }')


if __name__ == "__main__":
    print("Trackio-MCP Basic Example")
    print("This will create a trackio experiment with MCP server enabled")
    
    # Run the training simulation
    simulate_training_run()
    
    # Show available MCP tools
    demonstrate_mcp_tools()
    
    print(f"\nDone! The MCP server is running and AI agents can now:")
    print(f"   • Monitor your experiment progress")
    print(f"   • Query metrics and results")
    print(f"   • Get project summaries")
    print(f"   • Filter and analyze runs")
    
    print(f"\nTry asking an AI agent connected to the MCP server:")
    print(f'   "What experiments are available in my trackio setup?"')
    print(f'   "Show me the training progress for my latest run"')
    print(f'   "What metrics are being tracked in the mcp-example project?"')
