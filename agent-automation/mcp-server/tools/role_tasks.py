"""
Tool: get_my_role_tasks
Gets all tasks for a specific role from the workspace.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path to import automation system
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from parser import WorkspaceParser
from workspace_config import load_config


def get_my_role_tasks(role: str, config_path: str = None) -> Dict[str, Any]:
    """
    Get all tasks for a specific role from the workspace.
    
    Args:
        role: Role name (e.g., "CTO", "Lead Engineer", "Architect")
        config_path: Path to config.yaml (default: agent-automation/config.yaml)
    
    Returns:
        Dictionary with all tasks, status, dependencies, and blockers
    """
    config = load_config(config_path)
    
    # Initialize parser
    parser = WorkspaceParser(config['workspace_path'])
    
    # Get role status
    role_status = parser.parse_role_status(role)
    
    # Parse tasks from role section
    tasks = []
    if 'tasks' in role_status:
        for task_line in role_status.get('tasks', []):
            # Parse task line format: - [x] Task description (✅ date) or - [ ] Task description
            if task_line.strip().startswith('- ['):
                # Extract status and description
                if '[x]' in task_line or '✅' in task_line:
                    status = 'completed'
                elif '🟡' in task_line:
                    status = 'in_progress'
                elif '⏳' in task_line or '⏸️' in task_line:
                    status = 'pending'
                elif '🔄' in task_line:
                    status = 'pending_approval'
                else:
                    status = 'pending'
                
                # Extract description
                description = task_line.split(']', 1)[1].strip() if ']' in task_line else task_line.strip()
                tasks.append({
                    'description': description,
                    'status': status,
                    'raw': task_line.strip()
                })
    
    return {
        'role': role,
        'current_status': role_status.get('current_status', ''),
        'last_updated': role_status.get('last_updated', ''),
        'tasks': tasks,
        'task_count': len(tasks),
        'blockers': role_status.get('blockers', 'None'),
        'next_action': role_status.get('next_action', ''),
        'workspace_path': config['workspace_path']
    }

