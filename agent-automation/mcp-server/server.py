#!/usr/bin/env python3
"""
MCP Server for Agent Automation System.
Exposes tools for agents to check tasks, workspace status, and mark tasks complete.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Sequence

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: MCP SDK not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Import tools
from tools.task_checker import check_my_pending_tasks
from tools.workspace_status import get_workspace_status
from tools.task_complete import mark_task_complete
from tools.role_tasks import get_my_role_tasks
from tools.pending_prompt import get_pending_orchestrator_prompt


# Initialize MCP server
server = Server("agent-automation")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="check_my_pending_tasks",
            description="Check for pending tasks for a specific role. Returns tasks that need action, including approvals and work items.",
            inputSchema={
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "description": "Role name (e.g., 'CTO', 'Lead Engineer', 'Architect', 'CFO', 'CEO', 'Product Manager', 'Intern')"
                    }
                },
                "required": ["role"]
            }
        ),
        Tool(
            name="get_workspace_status",
            description="Get current workspace status including pending approvals, blockers, project phase, and recent work log entries.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="mark_task_complete",
            description="Mark a task as complete in the state tracker. Prevents duplicate triggers and logs completion.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task identifier (approval ID like '#001', work log timestamp, or task hash)"
                    },
                    "role": {
                        "type": "string",
                        "description": "Role name completing the task"
                    }
                },
                "required": ["task_id", "role"]
            }
        ),
        Tool(
            name="get_my_role_tasks",
            description="Get all tasks for a specific role from the workspace, including status, dependencies, and blockers.",
            inputSchema={
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "description": "Role name (e.g., 'CTO', 'Lead Engineer', 'Architect')"
                    }
                },
                "required": ["role"]
            }
        ),
        Tool(
            name="get_pending_orchestrator_prompt",
            description="Read the pending orchestrator run-cycle prompt (written by the stop hook when a subagent chat stops). Returns the prompt and clears the file. Call this at the start of an Orchestrator cycle; if prompt is non-empty, treat it as the run-cycle instruction so the loop continues without the user pasting.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Handle tool calls."""
    try:
        if name == "check_my_pending_tasks":
            role = arguments.get("role", "")
            if not role:
                return [TextContent(
                    type="text",
                    text='{"error": "role parameter is required"}'
                )]
            
            result = check_my_pending_tasks(role)
            import json
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        elif name == "get_workspace_status":
            result = get_workspace_status()
            import json
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        elif name == "mark_task_complete":
            task_id = arguments.get("task_id", "")
            role = arguments.get("role", "")
            
            if not task_id or not role:
                return [TextContent(
                    type="text",
                    text='{"error": "task_id and role parameters are required"}'
                )]
            
            result = mark_task_complete(task_id, role)
            import json
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        elif name == "get_my_role_tasks":
            role = arguments.get("role", "")
            if not role:
                return [TextContent(
                    type="text",
                    text='{"error": "role parameter is required"}'
                )]
            
            result = get_my_role_tasks(role)
            import json
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        elif name == "get_pending_orchestrator_prompt":
            result = get_pending_orchestrator_prompt()
            import json
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f'{{"error": "Unknown tool: {name}"}}'
            )]
    
    except Exception as e:
        import traceback
        error_msg = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        import json
        return [TextContent(
            type="text",
            text=json.dumps(error_msg, indent=2)
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

