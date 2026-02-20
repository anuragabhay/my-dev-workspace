"""
Agent Router - Determines which agent should act based on workspace state.
Maps roles to actions and trigger conditions.
"""

import yaml
from typing import List, Dict, Optional, Any
from pathlib import Path


class AgentRouter:
    """Routes workspace events to appropriate agents."""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.agent_configs = self.config.get('agents', {})
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def determine_agent_for_approval(self, approval: Dict[str, Any]) -> Optional[str]:
        """Determine which agent should respond to an approval request."""
        requested_from = approval.get('requested_from', '').strip()
        
        # Map role names to agent keys
        role_mapping = {
            'CTO': 'cto',
            'Architect': 'architect',
            'Lead Engineer': 'lead_engineer',
            'CFO': 'cfo',
            'CEO': 'ceo',
            'Product Manager': 'product_manager',
            'Junior Engineer 1': 'junior_engineer_1',
            'Junior Engineer 2': 'junior_engineer_2',
        }
        
        # Try exact match first
        for role_name, agent_key in role_mapping.items():
            if role_name.lower() in requested_from.lower():
                if agent_key in self.agent_configs:
                    return agent_key
        
        # Try partial match
        requested_lower = requested_from.lower()
        if 'cto' in requested_lower:
            return 'cto'
        elif 'architect' in requested_lower:
            return 'architect'
        elif 'lead engineer' in requested_lower or 'engineer' in requested_lower:
            return 'lead_engineer'
        elif 'cfo' in requested_lower:
            return 'cfo'
        elif 'ceo' in requested_lower:
            return 'ceo'
        elif 'product manager' in requested_lower or 'pm' in requested_lower:
            return 'product_manager'
        elif 'junior engineer 1' in requested_lower or 'junior-engineer-1' in requested_lower:
            return 'junior_engineer_1'
        elif 'junior engineer 2' in requested_lower or 'junior-engineer-2' in requested_lower:
            return 'junior_engineer_2'
        elif 'junior engineer' in requested_lower or 'junior-engineer' in requested_lower:
            return 'junior_engineer_1'  # default to first when ambiguous
        
        return None
    
    def determine_agent_for_task_completion(self, work_log_entry: Dict[str, Any], parsed_data: Dict[str, Any]) -> Optional[str]:
        """Determine which agent should act after a task completion."""
        role = work_log_entry.get('role', '')
        status = work_log_entry.get('status', '')
        task = work_log_entry.get('task', '')
        
        # Check if task is completed
        if '✅ COMPLETED' not in status and '✅' not in status:
            return None
        
        # Architecture approved -> Lead Engineer can start
        if 'Architect' in role and 'architecture' in task.lower() and 'approved' in task.lower():
            return 'lead_engineer'
        
        # Architecture design complete -> CTO should review
        if 'Architect' in role and 'architecture' in task.lower() and 'design' in task.lower():
            return 'cto'
        
        # Requirements complete -> Architect can start
        if 'Product Manager' in role and 'requirements' in task.lower():
            return 'architect'
        
        # CTO approved architecture -> Lead Engineer can start
        if 'CTO' in role and 'approve' in task.lower() and 'architecture' in task.lower():
            return 'lead_engineer'
        
        # Technology stack approved -> Architect can start
        if 'CTO' in role and 'technology stack' in task.lower():
            return 'architect'
        
        return None
    
    def determine_agent_for_blocker_resolution(self, blocker: Dict[str, Any], parsed_data: Dict[str, Any]) -> Optional[str]:
        """Determine which agent should act when a blocker is resolved."""
        # This would analyze blocker content to determine next agent
        # For now, return None (can be enhanced)
        return None
    
    def check_trigger_conditions(self, agent_key: str, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check if trigger conditions are met for an agent."""
        if agent_key not in self.agent_configs:
            return []
        
        agent_config = self.agent_configs[agent_key]
        trigger_on = agent_config.get('trigger_on', [])
        triggers = []
        seen_approval_ids = set()  # Track approval IDs to prevent duplicates
        
        # Check approval requests (general)
        if 'approval_request' in trigger_on:
            approvals = parsed_data.get('approval_requests', [])
            for approval in approvals:
                agent_for_approval = self.determine_agent_for_approval(approval)
                if agent_for_approval == agent_key:
                    approval_id = approval.get('approval_id')
                    if approval_id not in seen_approval_ids:
                        triggers.append({
                            'type': 'approval_request',
                            'item': approval,
                            'item_id': approval_id
                        })
                        seen_approval_ids.add(approval_id)
        
        # Check architecture review (specific - takes precedence over general)
        if 'architecture_review' in trigger_on:
            approvals = parsed_data.get('approval_requests', [])
            for approval in approvals:
                if 'architecture' in approval.get('type', '').lower():
                    agent_for_approval = self.determine_agent_for_approval(approval)
                    if agent_for_approval == agent_key:
                        approval_id = approval.get('approval_id')
                        if approval_id in seen_approval_ids:
                            # Replace general trigger with specific one
                            triggers = [t for t in triggers if t.get('item_id') != approval_id]
                        triggers.append({
                            'type': 'architecture_review',
                            'item': approval,
                            'item_id': approval_id
                        })
                        seen_approval_ids.add(approval_id)
        
        # Check requirements ready
        if 'requirements_ready' in trigger_on:
            work_log = parsed_data.get('recent_work_log', [])
            for entry in work_log:
                if 'Product Manager' in entry.get('role', '') and 'requirements' in entry.get('task', '').lower():
                    if '✅' in entry.get('status', ''):
                        triggers.append({
                            'type': 'requirements_ready',
                            'item': entry,
                            'item_id': f"work_log_{entry.get('timestamp', '')}"
                        })
                        break
        
        # Check architecture approved
        if 'architecture_approved' in trigger_on:
            work_log = parsed_data.get('recent_work_log', [])
            for entry in work_log:
                if 'CTO' in entry.get('role', '') and 'approve' in entry.get('task', '').lower():
                    if 'architecture' in entry.get('task', '').lower() and '✅' in entry.get('status', ''):
                        triggers.append({
                            'type': 'architecture_approved',
                            'item': entry,
                            'item_id': f"work_log_{entry.get('timestamp', '')}"
                        })
                        break
        
        # Check CTO feedback
        if 'cto_feedback' in trigger_on:
            work_log = parsed_data.get('recent_work_log', [])
            for entry in work_log:
                if 'CTO' in entry.get('role', ''):
                    content = entry.get('content', '')
                    if '✅' in entry.get('status', '') or '🔄' in entry.get('status', ''):
                        triggers.append({
                            'type': 'cto_feedback',
                            'item': entry,
                            'item_id': f"work_log_{entry.get('timestamp', '')}"
                        })
                        break
        
        # Check implementation ready
        if 'implementation_ready' in trigger_on:
            project_status = parsed_data.get('project_status', {})
            current_phase = project_status.get('current_phase', '')
            if 'implementation' in current_phase.lower() or 'planning' in current_phase.lower():
                triggers.append({
                    'type': 'implementation_ready',
                    'item': project_status,
                    'item_id': 'project_status'
                })
        
        # Final deduplication: remove any duplicate triggers by item_id
        # Keep first occurrence (more specific types should already be prioritized above)
        seen_ids = set()
        deduplicated_triggers = []
        for trigger in triggers:
            item_id = trigger.get('item_id')
            # Only deduplicate if item_id exists and is not None
            if item_id:
                if item_id in seen_ids:
                    continue  # Skip duplicate
                seen_ids.add(item_id)
            deduplicated_triggers.append(trigger)
        
        return deduplicated_triggers
    
    def find_agents_to_trigger(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find all agents that should be triggered based on workspace state."""
        agents_to_trigger = []
        
        # Check each agent's trigger conditions
        for agent_key in self.agent_configs.keys():
            triggers = self.check_trigger_conditions(agent_key, parsed_data)
            
            if triggers:
                agent_config = self.agent_configs[agent_key]
                agents_to_trigger.append({
                    'agent_key': agent_key,
                    'role_name': agent_config.get('role_name', agent_key),
                    'triggers': triggers
                })
        
        return agents_to_trigger
    
    def get_agent_config(self, agent_key: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific agent."""
        return self.agent_configs.get(agent_key)

