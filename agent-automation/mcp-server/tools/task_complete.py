"""
Tool: mark_task_complete
Marks a task as processed in the state tracker.
"""

import sys
from pathlib import Path
from typing import Dict, Any
import hashlib

# Add parent directory to path to import automation system
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from state_tracker import StateTracker
import yaml


def mark_task_complete(task_id: str, role: str, config_path: str = None) -> Dict[str, Any]:
    """
    Mark a task as complete in the state tracker.
    
    Args:
        task_id: Task identifier (approval ID, work log timestamp, etc.)
        role: Role name (e.g., "CTO", "Lead Engineer")
        config_path: Path to config.yaml (default: ../config.yaml)
    
    Returns:
        Dictionary with completion status
    """
    if config_path is None:
        config_path = str(Path(__file__).parent.parent.parent / "config.yaml")
    
    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize state tracker
    state_tracker = StateTracker(
        db_path=config['state_db'],
        json_backup_path=config['json_backup']
    )
    
    # Determine if it's an approval or task
    if task_id.startswith('#'):
        # It's an approval ID
        state_tracker.mark_approval_processed(
            approval_id=task_id,
            role=role,
            status="completed"
        )
        task_type = "approval"
    else:
        # It's a task hash
        state_tracker.mark_task_processed(
            task_hash=task_id,
            role=role,
            task_description=f"Completed by {role}"
        )
        task_type = "task"
    
    # Log trigger completion
    state_tracker.log_trigger(
        role=role,
        trigger_type="task_completion",
        item_id=task_id,
        prompt_file=None
    )
    
    return {
        'success': True,
        'task_id': task_id,
        'role': role,
        'task_type': task_type,
        'message': f'Task {task_id} marked as complete for {role}'
    }

