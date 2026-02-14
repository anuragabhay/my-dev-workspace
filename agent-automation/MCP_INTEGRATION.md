# MCP Integration Guide

## Overview

The Agent Automation System now includes an MCP (Model Context Protocol) server that enables agents to automatically check for tasks and workspace status via Cursor's MCP integration.

## Benefits

- **True Automation**: Agents can call tools instead of manually checking files
- **Structured Responses**: JSON responses instead of parsing markdown
- **Real-time**: No file polling needed
- **Native Cursor Integration**: Works seamlessly with Cursor

## Setup

### 1. Install MCP Dependencies

**Create virtual environment and install dependencies:**

```bash
cd /Users/anuragabhay/my-dev-workspace/agent-automation/mcp-server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Note**: The virtual environment is required to ensure all dependencies (MCP SDK, PyYAML) are available.

### 2. Configure Cursor

Cursor MCP configuration is set up at `/Users/anuragabhay/my-dev-workspace/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "agent-automation": {
      "command": "/Users/anuragabhay/my-dev-workspace/agent-automation/mcp-server/venv/bin/python",
      "args": ["/Users/anuragabhay/my-dev-workspace/agent-automation/mcp-server/server.py"],
      "env": {
        "PYTHONPATH": "/Users/anuragabhay/my-dev-workspace/agent-automation"
      }
    }
  }
}
```

**Important**: The configuration uses the virtual environment Python to ensure dependencies are available.

### 3. Test MCP Server

**Before restarting Cursor, test the server:**

```bash
cd /Users/anuragabhay/my-dev-workspace/agent-automation/mcp-server
source venv/bin/activate
PYTHONPATH=/Users/anuragabhay/my-dev-workspace/agent-automation python test_server.py
```

This should output "✅ All tests passed! MCP server is ready."

### 4. Restart Cursor

After configuration and testing, completely quit and restart Cursor to load the MCP server.

## Usage

### For Agents

Agents can now use MCP tools directly in Cursor:

**Check for pending tasks:**
```
@check_my_pending_tasks role="Lead Engineer"
```

**Get workspace status:**
```
@get_workspace_status
```

**Mark task complete:**
```
@mark_task_complete task_id="#001" role="CTO"
```

**Get all role tasks:**
```
@get_my_role_tasks role="Architect"
```

### Tool Responses

All tools return structured JSON:

```json
{
  "role": "Lead Engineer",
  "pending_tasks": [
    {
      "type": "architecture_approved",
      "item_id": "work_log_2026-02-14",
      "description": "Start implementation planning - Architecture has been approved"
    }
  ],
  "task_count": 1,
  "has_tasks": true
}
```

## Available Tools

### 1. check_my_pending_tasks

**Purpose**: Get pending tasks that need action for a specific role

**Parameters**:
- `role` (required): Role name (e.g., "CTO", "Lead Engineer", "Architect")

**Returns**:
- Pending tasks with descriptions
- Task count
- Role status from workspace
- Workspace path

### 2. get_workspace_status

**Purpose**: Get overall workspace status

**Parameters**: None

**Returns**:
- Project status (phase, overall status)
- Pending approvals count and list
- Blockers count and list
- Recent work log entries
- Next actions

### 3. mark_task_complete

**Purpose**: Mark a task as complete in state tracker

**Parameters**:
- `task_id` (required): Task identifier (approval ID, work log timestamp, etc.)
- `role` (required): Role name completing the task

**Returns**:
- Success status
- Task type (approval or task)
- Confirmation message

### 4. get_my_role_tasks

**Purpose**: Get all tasks for a role from workspace

**Parameters**:
- `role` (required): Role name

**Returns**:
- All tasks with status (completed, in_progress, pending)
- Current role status
- Blockers
- Next action

## Workflow

### Recommended Agent Workflow

1. **Start of work session**: Call `@check_my_pending_tasks role="Your Role"`
2. **Review tasks**: Examine returned tasks and descriptions
3. **Get context**: Call `@get_workspace_status` if needed for overall context
4. **Execute tasks**: Complete tasks and update PROJECT_WORKSPACE.md
5. **Mark complete**: Call `@mark_task_complete task_id="..." role="Your Role"` when done

### Example Session

```
Agent: @check_my_pending_tasks role="Lead Engineer"
MCP: Returns pending tasks including "Start implementation planning"

Agent: Reviews architecture approval, starts implementation

Agent: Updates PROJECT_WORKSPACE.md with progress

Agent: @mark_task_complete task_id="work_log_2026-02-14" role="Lead Engineer"
MCP: Confirms task marked as complete
```

## Integration with Existing System

The MCP server integrates seamlessly with existing automation components:

- **Parser**: Uses `WorkspaceParser` to read PROJECT_WORKSPACE.md
- **Router**: Uses `AgentRouter` to determine pending tasks
- **State Tracker**: Uses `StateTracker` to prevent duplicate triggers
- **Trigger System**: Can still generate prompt files as fallback

## Troubleshooting

### MCP Server Shows "Error" in Cursor

**Common causes and fixes:**

1. **Missing Dependencies**
   ```bash
   cd /Users/anuragabhay/my-dev-workspace/agent-automation/mcp-server
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Virtual Environment Not Created**
   ```bash
   cd /Users/anuragabhay/my-dev-workspace/agent-automation/mcp-server
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Wrong Python Path in Config**
   - Verify `.cursor/mcp.json` uses: `/Users/anuragabhay/my-dev-workspace/agent-automation/mcp-server/venv/bin/python`
   - Check that the venv exists: `ls -la /Users/anuragabhay/my-dev-workspace/agent-automation/mcp-server/venv/bin/python`

4. **Import Errors**
   - Test server manually: `cd mcp-server && source venv/bin/activate && PYTHONPATH=/Users/anuragabhay/my-dev-workspace/agent-automation python test_server.py`
   - Check for missing modules in error output

5. **PYTHONPATH Not Set**
   - Verify `.cursor/mcp.json` includes: `"PYTHONPATH": "/Users/anuragabhay/my-dev-workspace/agent-automation"` in env

6. **Cursor Not Restarted**
   - Completely quit Cursor (not just close window)
   - Restart Cursor
   - Check Cursor Settings → Tools & MCP → agent-automation → "Show Output" for errors

### MCP Server Not Available

If MCP tools are not available after fixing errors:
1. Check Cursor Settings → Tools & MCP → agent-automation status
2. Review "Show Output" for error messages
3. Run test script: `python test_server.py` in mcp-server directory
4. Use fallback: Check prompt files manually at `/Users/anuragabhay/my-dev-workspace/agent-automation/prompts/`

### Tool Errors

If tools return errors:
1. Check that `config.yaml` exists and is valid
2. Verify PROJECT_WORKSPACE.md path is correct
3. Ensure state database is accessible
4. Check tool logs for detailed error messages

### State Tracking Issues

If tasks are not being tracked:
1. Verify state database exists: `./state.db`
2. Check database permissions
3. Review state tracker logs

## Development

### Testing MCP Server

Test the server manually:
```bash
cd /Users/anuragabhay/my-dev-workspace/agent-automation/mcp-server
python server.py
```

The server uses stdio for MCP communication.

### Adding New Tools

1. Create tool function in `mcp-server/tools/`
2. Add tool definition to `server.py` → `list_tools()`
3. Add handler to `server.py` → `call_tool()`
4. Update documentation

## Migration from Prompt Files

Agents can gradually migrate from prompt files to MCP:

1. **Phase 1**: Use MCP tools for checking tasks
2. **Phase 2**: Use MCP for all task operations
3. **Phase 3**: Prompt files become fallback only

Prompt files will continue to be generated for compatibility.

## Support

For issues or questions:
- Check MCP server logs
- Review automation system logs
- Refer to PROJECT_WORKSPACE.md for agent coordination

