#!/usr/bin/env python3
"""
Orchestrator client - run one orchestrator cycle without Cursor.

Usage:
  python -m orchestrator_client.main
  # or from agent-automation:
  PYTHONPATH=./agent-automation python -m orchestrator_client.main

Requires:
  - ANTHROPIC_API_KEY or ORCHESTRATOR_LLM_API_KEY
  - WORKSPACE_ROOT (optional; defaults to agent-automation parent)
"""

import sys
from pathlib import Path

# Ensure agent-automation is on path when run as __main__
_client_dir = Path(__file__).resolve().parent
_agent_automation = _client_dir.parent
if str(_agent_automation) not in sys.path:
    sys.path.insert(0, str(_agent_automation))

from orchestrator_client.cycle_runner import main as run_cycle

if __name__ == "__main__":
    sys.exit(run_cycle())
