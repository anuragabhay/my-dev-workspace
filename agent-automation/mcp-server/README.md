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
- `role`: Role name (e.g. "Lead Engineer", "Junior Engineer 1", "Junior Engineer 2", "Architect")

**Returns:**
- `tasks`: List of all tasks with status
- `current_status`: Current role status
- `blockers`: Role-specific blockers
- `next_action`: Next action for the role

### 5. get_pending_orchestrator_prompt()

Reads the pending orchestrator run-cycle prompt (written by the stop hook when a subagent chat stops). Returns the prompt and clears the file. Call at the start of an Orchestrator cycle; if non-empty, treat as the run-cycle instruction.

### 6. get_role_guidance(role: string)

Returns role guidance from `agent-automation/agents/<role>.md` (host-agnostic), or `.cursor/skills/<role>/SKILL.md`, or `.cursor/agents/<role>.md`. Use when deciding which role to delegate to.

**Parameters:**
- `role`: Role name (e.g. "Lead Engineer", "Junior Engineer 1", "Junior Engineer 2", "Reviewer", "Tester", "Architect")

**Returns:**
- `role`, `content` (text or summary), `source` (file path), `error` (if any)

### 7. list_roles()

Returns list of role names and one-line "when to use". Includes Lead Engineer, Junior Engineer 1, Junior Engineer 2, Reviewer, Tester, Architect, PM, CTO, CFO (no single "Junior Engineer" or "Intern"). Use when deciding which role to delegate to.

### 8. get_workflow_config(workspace_root?: string)

Reads `agent-automation/workflow.yml`, `roles.yml`, and `decisions.yml`. Returns workflow stages, role list with slash commands, and priority-ordered decision rules. Use for current-stage logic and when the Orchestrator needs the canonical role list.

**Returns:**
- `workflow`: name, description
- `stages`: list of stage id, name, description, next, roles, parallel_ok
- `roles`: list of role id, display_name, slash, when_to_use, concurrency_max, parallel_ok
- `decisions`: list of decision rules (priority, condition, action, target_role_from)
- `error`: if any file is missing or invalid

## Standalone MCP Server (Any Host)

The MCP server runs standalone and can be connected from **Cursor**, **Claude Code**, **Vertex AI**, **Augment**, or any MCP client.

### Workspace Configuration

Set the workspace root so paths resolve correctly:

- **Environment variable**: `WORKSPACE_ROOT=/path/to/your-workspace`
- **Config file**: Create `agent-automation/workspace_config.yaml` with `workspace_root: /path/to/your-workspace` (or `.` for current dir)
- **Default**: Parent of `agent-automation/` (when running from project root)

### Running the Server

```bash
cd agent-automation/mcp-server
pip install -r requirements.txt

# From project root, with PYTHONPATH so tools can import workspace_config, parser, etc.
WORKSPACE_ROOT=/path/to/your-workspace PYTHONPATH=/path/to/agent-automation python server.py
```

Or from the workspace root:

```bash
cd /path/to/your-workspace
PYTHONPATH=./agent-automation python agent-automation/mcp-server/server.py
```

### Cursor Integration

Add to Cursor's MCP configuration (`.cursor/mcp.json` or Cursor settings). Use `$WORKSPACE` or your actual workspace path:

```json
{
  "mcpServers": {
    "agent-automation": {
      "command": "python",
      "args": ["agent-automation/mcp-server/server.py"],
      "env": {
        "PYTHONPATH": "agent-automation",
        "WORKSPACE_ROOT": "."
      }
    }
  }
}
```

When Cursor opens the workspace, `WORKSPACE_ROOT` can be `.` (current dir) or omitted (defaults to agent-automation parent).

### Claude Code / Other MCP Clients

Configure your MCP client to run the server with:

- `command`: `python` (or path to venv python)
- `args`: `["agent-automation/mcp-server/server.py"]`
- `env`: `PYTHONPATH=agent-automation`, `WORKSPACE_ROOT=/path/to/workspace` (if needed)

### Usage

Agents can call MCP tools directly:

```
@check_my_pending_tasks role="Lead Engineer"
@get_workspace_status
@get_pending_orchestrator_prompt
```

The tools return structured JSON with pending tasks, workspace status, and role guidance.

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

