"""
Tool: check_my_pending_tasks
Returns pending tasks for a specific role from the automation system.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path to import automation system
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from parser import WorkspaceParser
from router import AgentRouter
from state_tracker import StateTracker
from workspace_config import load_config


def check_my_pending_tasks(role: str, config_path: str = None) -> Dict[str, Any]:
    """
    Check for pending tasks for a specific role.
    
    Args:
        role: Role name (e.g., "CTO", "Lead Engineer", "Architect")
        config_path: Path to config.yaml (default: agent-automation/config.yaml)
    
    Returns:
        Dictionary with pending tasks, approvals, and context
    """
    config = load_config(config_path)
    
    # Initialize components
    parser = WorkspaceParser(config['workspace_path'])
    router = AgentRouter(config_path)
    state_tracker = StateTracker(
        db_path=config['state_db'],
        json_backup_path=config['json_backup']
    )
    
    # Parse workspace
    parsed_data = parser.parse_all()
    
    # Map role name to agent key
    role_mapping = {
        'CTO': 'cto',
        'Architect': 'architect',
        'Lead Engineer': 'lead_engineer',
        'CFO': 'cfo',
        'CEO': 'ceo',
        'Product Manager': 'product_manager',
        'PM': 'product_manager',
        'Junior Engineer 1': 'junior_engineer_1',
        'Junior Engineer 2': 'junior_engineer_2',
    }
    
    agent_key = role_mapping.get(role)
    if not agent_key:
        # e.g. "junior-engineer-1" -> junior_engineer_1
        agent_key = role.strip().lower().replace(' ', '_').replace('-', '_')
    
    # Get triggers for this agent
    agents_to_trigger = router.find_agents_to_trigger(parsed_data)
    agent_triggers = None
    for agent_info in agents_to_trigger:
        if agent_info['agent_key'] == agent_key:
            agent_triggers = agent_info
            break
    
    # Filter out already processed tasks
    pending_tasks = []
    if agent_triggers:
        for trigger in agent_triggers['triggers']:
            trigger_type = trigger['type']
            item_id = trigger.get('item_id', '')
            
            # Check if already processed
            if trigger_type == 'approval_request' and item_id:
                if state_tracker.is_approval_processed(item_id):
                    continue
            
            pending_tasks.append({
                'type': trigger_type,
                'item_id': item_id,
                'item': trigger.get('item', {}),
                'description': _get_task_description(trigger_type, trigger.get('item', {}))
            })
    
    # Get role status from workspace
    role_status = parser.parse_role_status(role)
    
    return {
        'role': role,
        'agent_key': agent_key,
        'pending_tasks': pending_tasks,
        'task_count': len(pending_tasks),
        'role_status': role_status,
        'workspace_path': config['workspace_path'],
        'has_tasks': len(pending_tasks) > 0
    }


def _get_task_description(trigger_type: str, item: Dict[str, Any]) -> str:
    """Generate human-readable task description."""
    if trigger_type == 'approval_request':
        approval = item
        return f"Review and respond to {approval.get('approval_id', 'approval')} from {approval.get('requested_by', 'unknown')}"
    elif trigger_type == 'architecture_review':
        approval = item
        return f"Review architecture design - {approval.get('approval_id', 'approval')}"
    elif trigger_type == 'architecture_approved':
        return "Start implementation planning - Architecture has been approved"
    elif trigger_type == 'requirements_ready':
        return "Start architecture design - Requirements are complete"
    elif trigger_type == 'implementation_ready':
        return "Proceed with implementation - Ready to start development"
    else:
        return f"Handle {trigger_type.replace('_', ' ')}"

