"""
Tool: get_workspace_status
Returns current workspace state including approvals, blockers, and project status.
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path to import automation system
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from parser import WorkspaceParser
import yaml


def get_workspace_status(config_path: str = None) -> Dict[str, Any]:
    """
    Get current workspace status.
    
    Args:
        config_path: Path to config.yaml (default: ../config.yaml)
    
    Returns:
        Dictionary with workspace status, approvals, blockers, etc.
    """
    if config_path is None:
        config_path = str(Path(__file__).parent.parent.parent / "config.yaml")
    
    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize parser
    parser = WorkspaceParser(config['workspace_path'])
    
    # Parse workspace
    parsed_data = parser.parse_all()
    
    # Get project status
    project_status = parsed_data.get('project_status', {})
    
    # Get recent work log
    recent_work_log = parsed_data.get('recent_work_log', [])[:5]
    
    return {
        'workspace_path': config['workspace_path'],
        'project_status': project_status,
        'pending_approvals': parsed_data.get('approval_requests', []),
        'approval_count': len(parsed_data.get('approval_requests', [])),
        'blockers': parsed_data.get('blockers', []),
        'blocker_count': len(parsed_data.get('blockers', [])),
        'recent_work_log': recent_work_log,
        'last_updated': project_status.get('last_updated', ''),
        'current_phase': project_status.get('current_phase', ''),
        'overall_status': project_status.get('overall_status', ''),
        'active_agents': project_status.get('active_agents', ''),
        'next_actions': project_status.get('next_actions', '')
    }

