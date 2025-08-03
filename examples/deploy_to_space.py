"""
Example of deploying trackio with MCP server to Hugging Face Spaces.

This example shows how to create and deploy a trackio experiment tracking
setup to Hugging Face Spaces with MCP server functionality enabled.
"""

# Import trackio_mcp BEFORE trackio to enable MCP functionality
import trackio_mcp

# Import trackio as usual
import trackio as wandb
import random
import time
import os


def deploy_to_spaces_example():
    """
    Deploy trackio to Hugging Face Spaces with MCP server enabled.
    
    This will:
    1. Create a trackio experiment
    2. Deploy to HF Spaces automatically
    3. Enable MCP server on the Space
    4. Optionally sync to a dataset for persistence
    """
    
    # Configure your Space details
    SPACE_ID = "your-username/trackio-mcp-demo"  # Change this!
    DATASET_ID = "your-username/trackio-mcp-data"  # Optional: for persistence
    
    print("Deploying Trackio + MCP to Hugging Face Spaces")
    print(f"Space: {SPACE_ID}")
    if DATASET_ID:
        print(f"Dataset: {DATASET_ID}")
    
    # Initialize with Space deployment
    wandb.init(
        project="spaces-mcp-demo",
        name="deployment-test", 
        space_id=SPACE_ID,
        dataset_id=DATASET_ID,  # Optional: enables data persistence
        config={
            "model": "GPT-4",
            "temperature": 0.7,
            "max_tokens": 2048,
            "deployment": "production"
        }
    )
    
    print("\nLogging some example metrics...")
    
    # Log some example metrics
    for step in range(20):
        # Simulate model performance metrics
        perplexity = 50 * (0.95 ** step) + random.uniform(0, 2)
        bleu_score = min(0.85, 0.3 + step * 0.025 + random.uniform(0, 0.01))
        rouge_l = min(0.90, 0.4 + step * 0.02 + random.uniform(0, 0.01))
        
        # Simulate resource usage
        gpu_util = random.uniform(0.8, 0.95)
        memory_gb = random.uniform(15, 20)
        tokens_per_sec = random.uniform(50, 80)
        
        wandb.log({
            "step": step,
            "model/perplexity": perplexity,
            "model/bleu_score": bleu_score,
            "model/rouge_l": rouge_l,
            "system/gpu_utilization": gpu_util,
            "system/memory_gb": memory_gb,
            "system/tokens_per_second": tokens_per_sec,
            "cost/tokens_processed": step * 1000 + random.randint(0, 200),
        })
        
        print(f"Step {step}: BLEU={bleu_score:.3f}, ROUGE-L={rouge_l:.3f}")
        time.sleep(0.2)
    
    wandb.finish()
    
    # Space deployment info
    space_url = f"https://huggingface.co/spaces/{SPACE_ID}"
    mcp_url = f"https://{SPACE_ID.replace('/', '-')}.hf.space/gradio_api/mcp/sse"
    
    print(f"\nDeployment Complete!")
    print(f"Space URL: {space_url}")
    print(f"MCP Server: {mcp_url}")
    print(f"API Schema: {mcp_url.replace('/sse', '/schema')}")


def create_mcp_client_config(space_id: str, private: bool = False):
    """Generate MCP client configuration for the deployed Space."""
    
    mcp_url = f"https://{space_id.replace('/', '-')}.hf.space/gradio_api/mcp/sse"
    
    config = {
        "mcpServers": {
            "trackio": {
                "url": mcp_url
            }
        }
    }
    
    # Add authentication for private Spaces
    if private:
        config["mcpServers"]["trackio"]["headers"] = {
            "Authorization": "Bearer YOUR_HF_TOKEN"
        }
    
    print("\nMCP Client Configuration:")
    print("Add this to your MCP client (Claude Desktop, Cursor, etc.):")
    print("-" * 50)
    import json
    print(json.dumps(config, indent=2))
    
    if private:
        print("\nFor private Spaces:")
        print("1. Replace YOUR_HF_TOKEN with your actual Hugging Face token")
        print("2. Ensure your token has read access to the Space")


def standalone_mcp_server_on_spaces():
    """
    Example of launching a standalone MCP server on Spaces.
    
    This creates a dedicated Space just for MCP tools, separate from
    your main trackio tracking.
    """
    
    print("\n" + "="*50)
    print("STANDALONE MCP SERVER ON SPACES")
    print("="*50)
    
    # You can also deploy just the MCP tools without main trackio
    from trackio_mcp.tools import register_trackio_tools
    
    # Create the tools interface
    tools_app = register_trackio_tools()
    
    if tools_app:
        print("\nStandalone MCP tools interface created")
        print("   This can be deployed to its own Space for dedicated MCP access")
        
        # Example deployment (you would uncomment and customize this)
        # tools_app.launch(
        #     share=True,  # Creates temporary share link
        #     mcp_server=True,
        #     show_api=True
        # )


def private_space_example():
    """Example of working with private Spaces and authentication."""
    
    print("\n" + "="*50) 
    print("PRIVATE SPACE WITH AUTHENTICATION")
    print("="*50)
    
    # For private Spaces, you need to be authenticated
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("No HF_TOKEN found in environment")
        print("   Set HF_TOKEN for private Space deployment")
        return
    
    print("HF_TOKEN found, can deploy to private Spaces")
    
    # Example with private Space
    try:
        wandb.init(
            project="private-research",
            name="confidential-model",
            space_id="your-org/private-trackio",  # Private Space
            dataset_id="your-org/private-data",   # Private Dataset
            config={
                "model": "proprietary-llm",
                "privacy_level": "confidential",
                "data_source": "internal"
            }
        )
        
        # Log some metrics
        wandb.log({
            "accuracy": 0.95,
            "privacy_score": 0.99,
            "compliance_check": True
        })
        
        wandb.finish()
        
        print("Private Space deployment successful")
        
    except Exception as e:
        print(f"Private Space deployment failed: {e}")
        print("   Make sure you have write permissions to the Space")


if __name__ == "__main__":
    print("Trackio-MCP Spaces Deployment Example")
    print("="*50)
    
    # Main deployment example
    # NOTE: Change the SPACE_ID in the function before running!
    print("\n1. Deploying to Spaces...")
    try:
        deploy_to_spaces_example()
    except Exception as e:
        print(f"Deployment failed: {e}")
        print("Make sure to:")
        print("   • Change SPACE_ID to your username/space-name")
        print("   • Be logged in with huggingface-cli")
        print("   • Have write permissions to create Spaces")
    
    # Generate client configuration
    print("\n2. Client Configuration...")
    create_mcp_client_config("your-username/trackio-mcp-demo", private=False)
    
    # Standalone server example
    print("\n3. Standalone MCP Server...")
    standalone_mcp_server_on_spaces()
    
    # Private Space example
    print("\n4. Private Space Example...")
    private_space_example()
    
    print(f"\nExamples complete!")
    print(f"\nNext steps:")
    print(f"   1. Customize the SPACE_ID and DATASET_ID in the code")
    print(f"   2. Run the deployment")
    print(f"   3. Configure your MCP client (Claude Desktop, etc.)")
    print(f"   4. Ask your AI agent about your experiments!")
    
    print(f"\nTry asking your connected AI agent:")
    print(f'   "What experiments are running in my trackio setup?"')
    print(f'   "Show me the latest model performance metrics"')
    print(f'   "Compare the results between my last two training runs"')
