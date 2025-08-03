# trackio-mcp

**MCP (Model Context Protocol) server support for trackio experiment tracking**

This package enables AI agents to observe and interact with [trackio](https://github.com/gradio-app/trackio) experiments through the Model Context Protocol (MCP). Simply import `trackio_mcp` before `trackio` to automatically enable MCP server functionality.

## Features

- **Zero-code integration**: Just import `trackio_mcp` before `trackio` 
- **Automatic MCP server**: Enables MCP server on all trackio deployments (local & Spaces)
- **Rich tool set**: Exposes trackio functionality as MCP tools for AI agents
- **Spaces compatible**: Works seamlessly with Hugging Face Spaces deployments
- **Drop-in replacement**: No changes needed to existing trackio code

## Installation

```bash
pip install trackio-mcp
```

Or with development dependencies:

```bash
pip install trackio-mcp[dev]
```

## Quick Start

### Basic Usage

Simply import `trackio_mcp` before importing `trackio`:

```python
import trackio_mcp  # This enables MCP server functionality
import trackio as wandb

# Your existing trackio code works unchanged
wandb.init(project="my-experiment")
wandb.log({"loss": 0.1, "accuracy": 0.95})
wandb.finish()
```

The MCP server will be automatically available at:
- **Local**: `http://localhost:7860/gradio_api/mcp/sse` 
- **Spaces**: `https://your-space.hf.space/gradio_api/mcp/sse`

### Deploy to Hugging Face Spaces with MCP

```python
import trackio_mcp
import trackio as wandb

# Deploy to Spaces with MCP enabled automatically
wandb.init(
    project="my-experiment", 
    space_id="username/my-trackio-space"
)

wandb.log({"loss": 0.1})
wandb.finish()
```

### Standalone MCP Server

Launch a dedicated MCP server for trackio tools:

```python
from trackio_mcp.tools import launch_trackio_mcp_server

# Launch standalone MCP server on port 7861
launch_trackio_mcp_server(port=7861, share=False)
```

## MCP Client Configuration

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "trackio": {
      "url": "http://localhost:7860/gradio_api/mcp/sse"
    }
  }
}
```

For Hugging Face Spaces:

```json
{
  "mcpServers": {
    "trackio": {
      "url": "https://your-space.hf.space/gradio_api/mcp/sse"
    }
  }
}
```

For private Spaces, add authentication:

```json
{
  "mcpServers": {
    "trackio": {
      "url": "https://your-space.hf.space/gradio_api/mcp/sse",
      "headers": {
        "Authorization": "Bearer YOUR_HF_TOKEN"
      }
    }
  }
}
```

### Cursor/Windsurf/Cline

For clients that support SSE directly, use the same URLs as above.

### For stdio clients

```json
{
  "mcpServers": {
    "trackio": {
      "command": "npx",
      "args": [
        "mcp-remote", 
        "http://localhost:7860/gradio_api/mcp/sse"
      ]
    }
  }
}
```

## Available MCP Tools

Once connected, AI agents can use these trackio tools:

### Core Tools (via Gradio API)
- **log**: Log metrics to a trackio run
- **upload_db_to_space**: Upload local database to a Space

### Extended Tools (via trackio-mcp)
- **get_projects**: List all trackio projects
- **get_runs**: Get runs for a specific project  
- **filter_runs**: Filter runs by name pattern
- **get_run_metrics**: Get metrics data for a specific run
- **get_available_metrics**: Get all available metric names for a project
- **load_run_data**: Load and process run data with optional smoothing
- **get_project_summary**: Get comprehensive project statistics

### Example Agent Interaction

```
Human: "Show me the latest results from my 'image-classification' project"

Agent: I'll check your trackio projects and get the latest results.

[Tool: get_projects] → finds "image-classification" project
[Tool: get_runs] → gets runs for "image-classification" 
[Tool: get_run_metrics] → gets metrics for latest run
[Tool: get_available_metrics] → gets metric names

Agent: Your latest image-classification run achieved 94.2% accuracy with a final loss of 0.18. The model trained for 50 epochs with best validation accuracy of 94.7% at epoch 45.
```

## Configuration

### Environment Variables

- `TRACKIO_ENABLE_MCP`: Set to `"false"` to disable MCP functionality (default: `"true"`)
- `GRADIO_MCP_SERVER`: Alternative way to enable MCP server
- `TRACKIO_MCP_ENABLED`: Set automatically when MCP is enabled

### Programmatic Control

```python
import os
os.environ["TRACKIO_ENABLE_MCP"] = "false"  # Disable MCP
import trackio_mcp  # MCP won't be enabled
import trackio
```

## How It Works

`trackio-mcp` uses monkey-patching to automatically:

1. **Enable MCP server**: Sets `mcp_server=True` on all Gradio launches
2. **Enable API**: Sets `show_api=True` to expose Gradio API endpoints  
3. **Add tools**: Registers additional trackio-specific MCP tools
4. **Preserve compatibility**: No changes needed to existing trackio code

The package patches:
- `gradio.Blocks.launch()` - Core Gradio launch method
- `trackio.ui.demo.launch()` - Trackio dashboard launches
- Adds new MCP endpoints at `/gradio_api/mcp/sse`

## Deployment Examples

### Local Development

```python
import trackio_mcp
import trackio

# Start local tracking with MCP enabled
trackio.show()  # Dashboard + MCP server at http://localhost:7860
```

### Production Spaces Deployment

```python
import trackio_mcp
import trackio as wandb

# Deploy to production with MCP support
wandb.init(
    project="production-model",
    space_id="company/model-tracking",
    dataset_id="company/model-metrics"  # Persistent storage
)

# Your training loop
for epoch in range(100):
    wandb.log({"epoch": epoch, "loss": loss, "accuracy": acc})

wandb.finish()
```

## CLI Interface

```bash
# Launch standalone MCP server
trackio-mcp server --port 7861

# Check status and configuration
trackio-mcp status

# Test MCP server functionality
trackio-mcp test --url http://localhost:7860
```

## Security Considerations

- **Private Spaces**: Use HF tokens for authentication
- **Access Control**: MCP server inherits trackio's access controls
- **Network Security**: Consider firewall rules for production deployments
- **Token Management**: Store HF tokens securely, use environment variables

## Troubleshooting

### MCP Server Not Available

```python
import trackio_mcp
import trackio

# Check if MCP was enabled
import os
print("MCP Enabled:", os.getenv("TRACKIO_MCP_ENABLED"))

# Manual verification
trackio.show()  # Look for MCP server URL in output
```

### Connection Issues

1. **Check URL**: Ensure correct `/gradio_api/mcp/sse` endpoint
2. **Authentication**: Add Bearer token for private Spaces
3. **Network**: Verify firewall/proxy settings
4. **Dependencies**: Ensure `gradio[mcp]` is installed

### Tool Discovery Issues

```python
# Test tools manually
from trackio_mcp.tools import register_trackio_tools

tools = register_trackio_tools()
tools.launch(mcp_server=True)  # Test tools interface
```

## Contributing

1. Fork the repository
2. Install development dependencies: `pip install -e .[dev]`
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file.

## Acknowledgments

- [trackio](https://github.com/gradio-app/trackio) - The excellent experiment tracking library
- [Gradio](https://gradio.app) - For built-in MCP server support
- [Model Context Protocol](https://modelcontextprotocol.io) - For the standardized AI tool protocol

---

**Made with care for the AI research community**
