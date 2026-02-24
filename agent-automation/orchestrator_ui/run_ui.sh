#!/usr/bin/env bash
# Start the Orchestrator UI.
# Run from workspace root or agent-automation.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_AUTOMATION="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$AGENT_AUTOMATION"
export PYTHONPATH="$AGENT_AUTOMATION"
exec python "$SCRIPT_DIR/server.py"
