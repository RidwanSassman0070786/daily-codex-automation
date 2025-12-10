#!/usr/bin/env python3
"""
Daily Codex Automation Script
Runs automated tasks using OpenAI Codex Agents SDK
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Check if required packages are available
try:
    from agents import Agent, Runner, set_default_openai_api
    from agents.mcp import MCPServerStdio
except ImportError:
    print("Error: Required packages not installed. Run: pip install openai openai-agents")
    sys.exit(1)

# Configuration
OUTPUT_DIR = Path("./daily-automation-output")
OUTPUT_DIR.mkdir(exist_ok=True)
DATE_STR = datetime.now().strftime("%Y%m%d_%H%M%S")

# Get API key from environment
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("Error: OPENAI_API_KEY environment variable not set")
    sys.exit(1)

set_default_openai_api(API_KEY)


async def run_daily_automation():
    """Execute daily automation tasks"""
    
    print(f"Starting daily automation at {datetime.now()}")
    
    try:
        # Initialize Codex MCP Server  
        async with MCPServerStdio(
            name="Codex CLI",
            params={"command": "npx", "args": ["-y", "codex", "mcp"]},
            client_session_timeout_seconds=360000,
        ) as codex_mcp_server:
            
            print("✓ Codex MCP server started")
            
            # Create automation agent
            automation_agent = Agent(
                name="Daily Automation Agent",
                instructions=(
                    f"""You are a daily automation agent running on {datetime.now().strftime('%Y-%m-%d')}.
                    
                    Execute these tasks:
                    1. Analyze the repository structure and create a summary
                    2. Generate a daily status report
                    3. List any TODOs or issues found
                    4. Create recommendations for improvements
                    
                    Save all outputs to ./daily-automation-output/report-{DATE_STR}.md
                    
                    Always call Codex MCP with {{"approval-policy":"never","sandbox":"workspace-write"}}.
                    """
                ),
                model="gpt-5",
                mcp_servers=[codex_mcp_server],
            )
            
            # Run automation
            print("⚙️  Running daily automation tasks...")
            
            result = await Runner.run(
                automation_agent,
                "Execute daily automation and generate comprehensive report",
                max_turns=20
            )
            
            print(f"✓ Daily automation completed")
            print(f"\nFinal Output:\n{result.final_output}")
            
            # Save summary
            summary_file = OUTPUT_DIR / f"summary-{DATE_STR}.txt"
            summary_file.write_text(result.final_output)
            print(f"\n✓ Summary saved to {summary_file}")
            
            return result
            
    except Exception as e:
        error_msg = f"Error in daily automation: {str(e)}"
        print(error_msg, file=sys.stderr)
        
        # Save error log
        error_file = OUTPUT_DIR / f"error-{DATE_STR}.log"
        error_file.write_text(f"{datetime.now()}: {error_msg}\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    print("="*60)
    print("Daily Codex Automation")
    print("="*60)
    asyncio.run(run_daily_automation())
    print("="*60)
