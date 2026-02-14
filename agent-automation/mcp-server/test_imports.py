#!/usr/bin/env python3
"""Test script to verify all imports work correctly."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Testing imports...")
print(f"Python path: {sys.path[:3]}")

# Test automation system imports
try:
    from parser import WorkspaceParser
    print("✓ WorkspaceParser imported")
except ImportError as e:
    print(f"✗ WorkspaceParser import failed: {e}")

try:
    from router import AgentRouter
    print("✓ AgentRouter imported")
except ImportError as e:
    print(f"✗ AgentRouter import failed: {e}")

try:
    from state_tracker import StateTracker
    print("✓ StateTracker imported")
except ImportError as e:
    print(f"✗ StateTracker import failed: {e}")

# Test tool imports
try:
    from tools.task_checker import check_my_pending_tasks
    print("✓ task_checker imported")
except ImportError as e:
    print(f"✗ task_checker import failed: {e}")

try:
    from tools.workspace_status import get_workspace_status
    print("✓ workspace_status imported")
except ImportError as e:
    print(f"✗ workspace_status import failed: {e}")

# Test MCP imports
print("\nTesting MCP SDK...")
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    print("✓ MCP SDK imported successfully")
except ImportError as e:
    print(f"✗ MCP SDK import failed: {e}")
    print("\nTo install MCP SDK, try:")
    print("  pip install mcp")
    print("  or")
    print("  pip install anthropic-mcp")

print("\nAll import tests complete.")

