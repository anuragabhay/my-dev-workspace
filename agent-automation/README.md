# Agent Automation System

Automated system that monitors `PROJECT_WORKSPACE.md` and triggers appropriate agents when their action is required, eliminating the need for manual intervention.

## Overview

This system watches the multi-agent workspace file for changes and automatically:
- Detects pending approval requests
- Identifies task completions that unblock other agents
- Generates context-rich prompt files for agents to read and act on
- Tracks processed items to prevent duplicate triggers

## Features

- **File Monitoring**: Watches `PROJECT_WORKSPACE.md` for changes using file watcher (with polling fallback)
- **Status Parsing**: Extracts approval requests, task statuses, blockers, and work log entries
- **Agent Routing**: Determines which agent should act based on workspace state
- **Prompt Generation**: Creates detailed prompt files for agents with context and instructions
- **State Tracking**: SQLite database tracks processed items (with JSON backup)

## Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure**:
   - Edit `config.yaml` to set workspace path and agent configurations
   - Ensure `PROJECT_WORKSPACE.md` path is correct

3. **Run**:
```bash
# Continuous monitoring (default)
python main.py

# Single check
python main.py --once

# Custom config file
python main.py --config /path/to/config.yaml
```

## Project Structure

```
agent-automation/
├── main.py              # Main entry point
├── monitor.py           # File watcher with polling fallback
├── parser.py            # Workspace markdown parser
├── router.py            # Agent routing logic
├── trigger.py           # Prompt generation system
├── state_tracker.py     # State tracking (SQLite + JSON backup)
├── config.yaml          # Configuration
├── requirements.txt     # Python dependencies
├── state.db             # SQLite state database (created automatically)
├── state_backup.json    # JSON backup (created automatically)
└── prompts/             # Generated prompt files for agents
    ├── cto_action.md
    ├── architect_action.md
    └── ...
```

## Configuration

Edit `config.yaml` to configure:

- **workspace_path**: Path to `PROJECT_WORKSPACE.md`
- **poll_interval**: Polling interval in seconds (fallback mode)
- **prompt_dir**: Directory for generated prompts
- **state_db**: SQLite database path
- **agents**: Agent configurations with trigger conditions

## How It Works

### 1. File Monitoring
- Uses `watchdog` library for file system events (with polling fallback)
- Detects when `PROJECT_WORKSPACE.md` is modified

### 2. Parsing
- Extracts approval requests with `[OPEN]` status
- Parses role status sections for task states
- Analyzes work log for completion events
- Identifies blockers and their resolution

### 3. Routing
- Maps approval requests to appropriate responder (e.g., CTO for architecture approvals)
- Detects task completions that unblock other agents
- Checks trigger conditions for each agent

### 4. Prompt Generation
- Creates markdown prompt files in `prompts/` directory
- Includes:
  - Role and context
  - What needs to be done
  - Relevant workspace sections
  - Expected output format
  - Instructions for updating workspace

### 5. State Tracking
- Tracks processed approvals and tasks in SQLite
- Prevents duplicate triggers
- Maintains trigger history
- Backs up to JSON file

## Agent Prompt Files

Prompt files are generated in `prompts/{agent_key}_action.md` format. Agents should:
1. Check `prompts/` directory for their prompt file
2. Read the prompt to understand what action is needed
3. Act on the workspace according to instructions
4. The system will track that the prompt was processed

## Example Workflow

1. **Architect completes architecture design** → Updates workspace
2. **System detects change** → Parses workspace
3. **System finds Approval #001** → Routes to CTO
4. **System generates `prompts/cto_action.md`** → CTO reads prompt
5. **CTO reviews and approves** → Updates workspace
6. **System detects approval** → Routes to Lead Engineer
7. **System generates `prompts/lead_engineer_action.md`** → Lead Engineer starts implementation

## State Management

The system maintains state in:
- **SQLite database** (`state.db`): Primary storage for processed items
- **JSON backup** (`state_backup.json`): Backup of recent state

State includes:
- Processed approval IDs
- Processed task hashes
- Trigger history
- Last check timestamp

## Error Handling

- File lock issues: Retries with backoff
- Parse errors: Logs and continues (doesn't crash)
- State DB errors: Falls back to JSON file
- Agent trigger failures: Logs for manual review

## Troubleshooting

**No prompts generated:**
- Check if items are already processed (in state.db)
- Verify workspace parsing is working (check console output)
- Ensure agent configurations match role names in workspace

**File watcher not working:**
- System automatically falls back to polling mode
- Check if `watchdog` is installed: `pip install watchdog`

**State database issues:**
- System will use JSON backup if SQLite fails
- Delete `state.db` to reset state (will lose history)

## Development

To extend the system:

1. **Add new trigger types**: Update `router.py` → `check_trigger_conditions()`
2. **Add new agent roles**: Update `config.yaml` → `agents` section
3. **Customize prompts**: Modify `trigger.py` → `generate_prompt()`
4. **Add parsing logic**: Extend `parser.py` with new extraction methods

## License

Part of the Multi-Agent Autonomous Development Workspace system.

