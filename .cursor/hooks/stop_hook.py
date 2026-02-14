#!/usr/bin/env python3
"""
Cursor stop hook. Does NOT inject followup_message into any chat.
Orchestrator loop runs only when the user is in the Orchestrator chat and sends the prompt.
"""
import json
import sys


def main() -> None:
    # Never return followup_message—do not auto-inject into Main Creator Discussion or any chat.
    # Orchestrator runs only when user is in the Orchestrator chat and invokes it.
    print(json.dumps({}))


if __name__ == "__main__":
    main()
