# MCP Server for Agent Automation System

MCP (Model Context Protocol) server that exposes tools for agents to automatically check tasks, workspace status, and manage state.

## Overview

This MCP server integrates with the existing agent automation system to provide programmatic access to:
- Pending tasks for specific roles
- Workspace status and approvals
- Task completion tracking
- Role-specific task lists

## Installation

```bash
cd mcp-server
pip install -r requirements.txt
```

## Tools

### 1. check_my_pending_tasks(role: string)

Returns pending tasks for a specific role that need action.

**Parameters:**
- `role`: Role name (e.g., "CTO", "Lead Engineer", "Architect")

**Returns:**
- `pending_tasks`: List of tasks with type, item_id, and description
- `task_count`: Number of pending tasks
- `role_status`: Current role status from workspace
- `has_tasks`: Boolean indicating if tasks exist

**Example:**
```json
{
  "role": "CTO",
  "pending_tasks": [
    {
      "type": "approval_request",
      "item_id": "#001",
      "description": "Review and respond to #001 from Architect"
    }
  ],
  "task_count": 1,
  "has_tasks": true
}
```

### 2. get_workspace_status()

Returns current workspace state.

**Returns:**
- `project_status`: Overall project status
- `pending_approvals`: List of open approval requests
- `blockers`: List of active blockers
- `recent_work_log`: Recent work log entries
- `current_phase`: Current project phase
- `next_actions`: Next actions from dashboard

### 3. mark_task_complete(task_id: string, role: string)

Marks a task as complete in the state tracker.

**Parameters:**
- `task_id`: Task identifier (approval ID, work log timestamp, etc.)
- `role`: Role name completing the task

**Returns:**
- `success`: Boolean indicating success
- `task_type`: Type of task (approval or task)
- `message`: Confirmation message

### 4. get_my_role_tasks(role: string)

Gets all tasks for a specific role from the workspace.

**Parameters:**
- `role`: Role name

**Returns:**
- `tasks`: List of all tasks with status
- `current_status`: Current role status
- `blockers`: Role-specific blockers
- `next_action`: Next action for the role

## Cursor Integration

### Configuration

Add to Cursor's MCP configuration (`.cursor/mcp.json` or Cursor settings):

```json
{
  "mcpServers": {
    "agent-automation": {
      "command": "python",
      "args": ["/Users/anuragabhay/my-dev-workspace/agent-automation/mcp-server/server.py"],
      "env": {}
    }
  }
}
```

### Usage in Cursor

Agents can now call MCP tools directly:

```
@check_my_pending_tasks role="Lead Engineer"
```

The tool will return structured JSON with pending tasks, eliminating the need to manually check prompt files.

## Integration

The MCP server integrates with existing automation system components:
- **Parser**: Reads and parses PROJECT_WORKSPACE.md
- **Router**: Determines which agents should be triggered
- **State Tracker**: Tracks processed tasks and prevents duplicates

## Benefits

- **True Automation**: Agents automatically discover tasks via MCP
- **Structured Responses**: JSON instead of parsing markdown
- **Real-time**: No file polling needed
- **Native Integration**: Works seamlessly with Cursor MCP

## Development

### Testing

Test the server manually:
```bash
python server.py
```

The server uses stdio for communication, so it's designed to be called by MCP clients.

### Adding New Tools

1. Create tool function in `tools/` directory
2. Add tool definition to `list_tools()`
3. Add handler to `call_tool()`
4. Update this README

## License

Part of the Agent Automation System for Multi-Agent Autonomous Development Workspace.

