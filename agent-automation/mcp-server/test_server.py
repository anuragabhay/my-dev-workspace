#!/usr/bin/env python3
"""
Test script to verify MCP server can start without errors.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    # Test imports
    print("Testing MCP SDK import...")
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    print("✓ MCP SDK imports OK")
    
    # Test tool imports
    print("Testing tool imports...")
    from tools.task_checker import check_my_pending_tasks
    from tools.workspace_status import get_workspace_status
    from tools.task_complete import mark_task_complete
    from tools.role_tasks import get_my_role_tasks
    print("✓ Tool imports OK")
    
    # Test server initialization
    print("Testing server initialization...")
    server = Server("agent-automation")
    print("✓ Server initialization OK")
    
    # Test tool execution
    print("Testing tool execution...")
    result = check_my_pending_tasks("Lead Engineer")
    print(f"✓ Tool execution OK (found {result.get('task_count', 0)} tasks)")
    
    print("\n✅ All tests passed! MCP server is ready.")
    sys.exit(0)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nPlease install dependencies:")
    print("  cd agent-automation/mcp-server")
    print("  source venv/bin/activate")
    print("  pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

