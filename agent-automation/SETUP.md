# Agent Automation System - Setup Guide

## Overview

The Agent Automation System monitors `PROJECT_WORKSPACE.md` and automatically triggers appropriate agents when their action is required. This eliminates the need for manual intervention in the multi-agent workflow.

## Prerequisites

- Python 3.8 or higher (tested with Python 3.13.3)
- pip (Python package manager)
- Access to `PROJECT_WORKSPACE.md` file

## Installation

### 1. Navigate to Project Directory

```bash
cd /Users/anuragabhay/my-dev-workspace/agent-automation
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
# Ensure virtual environment is activated
pip install -r requirements.txt
```

**Required packages:**
- `PyYAML>=6.0` - Configuration file parsing
- `watchdog>=3.0.0` - File system monitoring

### 4. Verify Installation

```bash
# Check Python version
python --version

# Verify packages installed
pip list

# Test system (single check)
python main.py --once
```

## Configuration

### Edit `config.yaml`

The main configuration file is `config.yaml`. Key settings:

```yaml
workspace_path: PROJECT_WORKSPACE.md  # Resolved via workspace_config (WORKSPACE_ROOT or workspace_config.yaml)
poll_interval: 30  # Polling interval in seconds (fallback mode)
prompt_dir: ./prompts  # Directory for generated prompt files
state_db: ./state.db  # SQLite database for state tracking
json_backup: ./state_backup.json  # JSON backup file
```

**Important:** Update `workspace_path` to point to your `PROJECT_WORKSPACE.md` file.

### Agent Configuration

Agents are configured in the `agents` section of `config.yaml`:

```yaml
agents:
  cto:
    trigger_on: ["approval_request", "architecture_review"]
    approval_types: ["Technical Decision", "Architecture Approval"]
    role_name: "CTO"
```

Each agent specifies:
- `trigger_on`: List of trigger types that activate this agent
- `role_name`: Display name for the agent
- `approval_types`: (Optional) Specific approval types for this agent

## Running the System

### Continuous Monitoring (Recommended)

Start the system to continuously monitor the workspace:

```bash
# Activate virtual environment
source venv/bin/activate

# Start monitoring
python main.py
```

The system will:
- Monitor `PROJECT_WORKSPACE.md` for changes
- Parse approval requests and task completions
- Generate prompt files for agents in `prompts/` directory
- Track processed items to prevent duplicates

**To stop:** Press `Ctrl+C`

### Single Check Mode

Run a one-time check without continuous monitoring:

```bash
python main.py --once
```

### Custom Config File

Use a different configuration file:

```bash
python main.py --config /path/to/custom-config.yaml
```

### Running in Background

**Option 1: Using nohup**

```bash
nohup python main.py > automation.log 2>&1 &
```

**Option 2: Using screen**

```bash
screen -S automation
source venv/bin/activate
python main.py
# Press Ctrl+A then D to detach
```

**Option 3: Using tmux**

```bash
tmux new-session -d -s automation 'cd agent-automation && source venv/bin/activate && python main.py'
```

## System Components

### File Structure

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
├── SETUP.md            # This file
├── README.md           # System documentation
├── state.db            # SQLite state database (auto-created)
├── state_backup.json   # JSON backup (auto-created)
└── prompts/            # Generated prompt files for agents
    ├── cto_action.md
    ├── architect_action.md
    └── ...
```

### How It Works

1. **File Monitoring**: Watches `PROJECT_WORKSPACE.md` using `watchdog` (falls back to polling if unavailable)
2. **Parsing**: Extracts approval requests, task statuses, blockers, and work log entries
3. **Routing**: Determines which agents should act based on workspace state
4. **Prompt Generation**: Creates detailed prompt files in `prompts/` directory
5. **State Tracking**: SQLite database tracks processed items to prevent duplicates

## Monitoring and Verification

### Check System Status

```bash
# Check if process is running
ps aux | grep "python main.py"

# View recent log output
tail -f automation.log  # If using nohup
```

### Verify Prompt Generation

```bash
# List generated prompts
ls -la prompts/

# View a prompt file
cat prompts/cto_action.md
```

### Check State Database

```bash
# View state database (requires sqlite3)
sqlite3 state.db "SELECT * FROM processed_approvals;"
sqlite3 state.db "SELECT * FROM trigger_history ORDER BY triggered_at DESC LIMIT 10;"
```

### Test Parsing

```bash
# Test workspace parsing
python -c "from workspace_config import load_config; c = load_config(); from parser import WorkspaceParser; p = WorkspaceParser(c['workspace_path']); data = p.parse_all(); print(f'Found {len(data[\"approval_requests\"])} approval requests')"
```

## Troubleshooting

### Issue: "Config file not found"

**Solution:** Ensure `config.yaml` exists in the project directory, or specify path with `--config` flag.

### Issue: "watchdog not available, using polling mode"

**Solution:** This is not an error - the system automatically falls back to polling. To use file watcher:
```bash
pip install watchdog
```

### Issue: "Workspace file not found"

**Solution:** Update `workspace_path` in `config.yaml` to the correct path to `PROJECT_WORKSPACE.md`.

### Issue: No prompts generated

**Possible causes:**
1. Items already processed (check `state.db`)
2. No matching trigger conditions
3. Workspace parsing issues

**Debug steps:**
```bash
# Check if items are already processed
python -c "from state_tracker import StateTracker; st = StateTracker('./state.db', './state_backup.json'); print('Recent triggers:', st.get_recent_triggers(5))"

# Test parsing
python main.py --once
```

### Issue: Virtual environment not activating

**Solution:**
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Permission errors

**Solution:**
```bash
# Ensure write permissions for prompts directory
chmod -R 755 prompts/

# Ensure write permissions for state database
chmod 644 state.db
```

### Issue: State database locked

**Solution:** This usually resolves automatically. If persistent:
```bash
# Stop the automation system
# Delete and recreate state database (WARNING: loses history)
rm state.db
python main.py --once  # Recreates database
```

## Maintenance

### Reset State (Clear Processing History)

**WARNING:** This will delete all processing history.

```bash
# Stop the automation system first
rm state.db state_backup.json
python main.py --once  # Recreates empty database
```

### Cleanup Old Prompts

The system automatically keeps the 10 most recent prompt files. To manually clean:

```bash
# Keep only last 5 prompts
ls -t prompts/*_action.md | tail -n +6 | xargs rm
```

### Backup State

State is automatically backed up to `state_backup.json`. To manually backup:

```bash
# Copy state database
cp state.db state.db.backup
cp state_backup.json state_backup.json.backup
```

## Integration with Agents

### How Agents Use the System

1. **Check for prompts**: Agents should check `prompts/{agent_key}_action.md` for new tasks
2. **Read prompt**: Prompt contains context, instructions, and what needs to be done
3. **Act on workspace**: Update `PROJECT_WORKSPACE.md` according to prompt instructions
4. **System detects change**: Automation system detects workspace update
5. **Next agent triggered**: System routes to next agent if needed

### Prompt File Format

Prompt files are generated in markdown format with:
- Role and action required
- Approval request details (if applicable)
- Task instructions
- Workspace location
- Important notes

## Advanced Configuration

### Custom Trigger Conditions

Edit `router.py` to add custom trigger logic in `check_trigger_conditions()` method.

### Custom Prompt Templates

Edit `trigger.py` to customize prompt generation in `generate_prompt()` method.

### Polling Interval

Adjust `poll_interval` in `config.yaml` (in seconds). Lower values = more frequent checks but higher CPU usage.

## Support

For issues or questions:
1. Check this SETUP.md guide
2. Review README.md for system architecture
3. Check system logs for error messages
4. Verify configuration in `config.yaml`

## Version Information

- **Python**: 3.13.3 (tested)
- **PyYAML**: 6.0.3
- **watchdog**: 6.0.0
- **System Version**: 1.0

---

**Last Updated**: 2026-02-14
**Maintained By**: CTO

