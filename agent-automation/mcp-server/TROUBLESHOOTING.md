# MCP Server Troubleshooting Guide

## Quick Diagnosis

Run the test script to identify issues:

```bash
cd agent-automation/mcp-server
source venv/bin/activate
PYTHONPATH=../.. python test_server.py
```

## Common Issues

### Issue 1: "Error: MCP SDK not installed"

**Symptoms:**
- Server exits immediately
- Error message: "Error: MCP SDK not installed"

**Solution:**
```bash
cd agent-automation/mcp-server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Verify:**
```bash
source venv/bin/activate
python -c "from mcp.server import Server; print('OK')"
```

### Issue 2: "ModuleNotFoundError: No module named 'yaml'"

**Symptoms:**
- Import error when loading tools
- Error in Cursor MCP output

**Solution:**
```bash
cd agent-automation/mcp-server
source venv/bin/activate
pip install PyYAML
```

**Verify:**
```bash
source venv/bin/activate
python -c "import yaml; print('OK')"
```

### Issue 3: "ModuleNotFoundError: No module named 'parser'"

**Symptoms:**
- Import error for automation system modules
- Tools can't import parser, router, etc.

**Solution:**
1. Verify PYTHONPATH in `.cursor/mcp.json`:
   ```json
   "env": {
     "PYTHONPATH": "agent-automation"
   }
   ```

2. Verify parent directory structure:
   ```bash
   ls agent-automation/parser.py
   ls agent-automation/router.py
   ```

### Issue 4: Cursor Shows "Error" Status

**Symptoms:**
- MCP server shows "Error" in Cursor Settings
- Tools not available in agent chat

**Diagnosis Steps:**

1. **Check Cursor Output:**
   - Cursor Settings → Tools & MCP → agent-automation → "Show Output"
   - Look for error messages

2. **Test Server Manually:**
   ```bash
   cd /Users/anuragabhay/my-dev-workspace/agent-automation/mcp-server
   source venv/bin/activate
   PYTHONPATH=/Users/anuragabhay/my-dev-workspace/agent-automation python test_server.py
   ```

3. **Verify Configuration:**
   ```bash
   cat .cursor/mcp.json
   ```
   
   Should show:
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

4. **Check Virtual Environment:**
   ```bash
   ls -la /Users/anuragabhay/my-dev-workspace/agent-automation/mcp-server/venv/bin/python
   ```
   
   Should exist and be executable.

### Issue 5: Tools Return Errors

**Symptoms:**
- MCP server connects but tools fail
- Error messages in tool responses

**Diagnosis:**

1. **Test Tool Directly:**
   ```bash
   cd /Users/anuragabhay/my-dev-workspace/agent-automation/mcp-server
   source venv/bin/activate
   PYTHONPATH=/Users/anuragabhay/my-dev-workspace/agent-automation python -c "from tools.task_checker import check_my_pending_tasks; print(check_my_pending_tasks('Lead Engineer'))"
   ```

2. **Check Config File:**
   ```bash
   ls /Users/anuragabhay/my-dev-workspace/agent-automation/config.yaml
   cat /Users/anuragabhay/my-dev-workspace/agent-automation/config.yaml | head -5
   ```

3. **Check Workspace File:**
   ```bash
   ls /Users/anuragabhay/my-dev-workspace/PROJECT_WORKSPACE.md
   ```

## Verification Checklist

- [ ] Virtual environment created: `ls mcp-server/venv/bin/python`
- [ ] Dependencies installed: `source venv/bin/activate && pip list | grep mcp`
- [ ] Test script passes: `python test_server.py`
- [ ] Cursor config correct: `cat .cursor/mcp.json`
- [ ] PYTHONPATH set in config
- [ ] Cursor restarted completely
- [ ] Check Cursor Settings → Tools & MCP for status

## Getting Help

If issues persist:

1. **Collect Information:**
   - Cursor MCP output (Settings → Tools & MCP → Show Output)
   - Test script output
   - Python version: `python --version`
   - Virtual environment path

2. **Check Logs:**
   - Cursor logs (if available)
   - Test script output
   - Manual tool execution output

3. **Fallback:**
   - Use prompt files manually: `/Users/anuragabhay/my-dev-workspace/agent-automation/prompts/{role}_action.md`
   - Automation system still works without MCP

## Test Commands

**Full test sequence:**
```bash
cd agent-automation/mcp-server
source venv/bin/activate
PYTHONPATH=../.. python test_server.py
```

**Individual component tests:**
```bash
# Test MCP SDK
source venv/bin/activate
python -c "from mcp.server import Server; print('MCP OK')"

# Test tool imports
PYTHONPATH=/Users/anuragabhay/my-dev-workspace/agent-automation python -c "from tools.task_checker import check_my_pending_tasks; print('Tools OK')"

# Test tool execution
PYTHONPATH=/Users/anuragabhay/my-dev-workspace/agent-automation python -c "from tools.task_checker import check_my_pending_tasks; result = check_my_pending_tasks('Lead Engineer'); print(f'Execution OK: {result.get(\"task_count\", 0)} tasks')"
```
