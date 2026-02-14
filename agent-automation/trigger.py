"""
Agent Trigger System - Generates context-rich prompt files for agents.
Creates prompt files in prompts/ directory for agents to read and act on.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class AgentTrigger:
    """Generates prompts for agents to act on workspace changes."""
    
    def __init__(self, config_path: str, workspace_path: str):
        self.config = self._load_config(config_path)
        self.workspace_path = Path(workspace_path)
        self.prompt_dir = Path(self.config.get('prompt_dir', './prompts'))
        self.prompt_dir.mkdir(exist_ok=True)
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def generate_approval_prompt(self, agent_key: str, role_name: str, approval: Dict[str, Any], workspace_path: str) -> str:
        """Generate prompt for approval request."""
        approval_id = approval.get('approval_id', '')
        requested_by = approval.get('requested_by', '')
        approval_type = approval.get('type', '')
        request_text = approval.get('request', '')
        priority = approval.get('priority', '')
        
        prompt = f"""# {role_name} Review Task

**Role**: {role_name}
**Action Required**: Review and respond to {approval_id}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## Approval Request Details

- **Approval ID**: {approval_id}
- **Requested By**: {requested_by}
- **Requested From**: {role_name}
- **Type**: {approval_type}
- **Priority**: {priority}
- **Request**: {request_text}

## Your Task

1. Read PROJECT_WORKSPACE.md (especially relevant sections mentioned in the request)
2. Review the work that requires your approval
3. Make decision: ✅ Approved | ❌ Rejected | 🔄 Needs Revision
4. Update {approval_id} in workspace with your response:
   - Add your response in the **Response** field
   - Update **Decision** field with your decision
   - Update **Status** field (e.g., "✅ Approved by {role_name}")
5. Update Work Log with your decision:
   - Add entry: `[TIMESTAMP] [{role_name}] [Review {approval_id}] [✅ COMPLETED]`
   - Include decision and rationale
6. If approved, mark requester's task as "✅ APPROVED" in their Role section
7. If rejected or needs revision, provide clear feedback

## Workspace Location
{workspace_path}

## Approval Content
```
{approval.get('content', '')[:500]}
```

## Important Notes

- Check the workspace before starting to ensure no one else has already responded
- Be thorough in your review
- Provide clear, actionable feedback if revision is needed
- Update timestamps when making changes
"""
        return prompt
    
    def generate_task_completion_prompt(self, agent_key: str, role_name: str, trigger_item: Dict[str, Any], trigger_type: str, workspace_path: str) -> str:
        """Generate prompt for task completion trigger."""
        prompt = f"""# {role_name} Action Required

**Role**: {role_name}
**Trigger Type**: {trigger_type}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## Context

A task has been completed that unblocks your work or requires your action.

## Trigger Details

**Type**: {trigger_type}
**Item**: {trigger_item.get('item_id', 'N/A')}

## Your Task

1. Read PROJECT_WORKSPACE.md to understand current state
2. Check your Role Status section for pending tasks
3. Review what was completed that triggered this action
4. Proceed with your next task:
   - Mark task as "🟡 IN PROGRESS" in your Role section
   - Add Work Log entry: `[TIMESTAMP] [{role_name}] [TASK_NAME] [🟡 IN PROGRESS]`
   - Complete the work
   - Update status when done

## Workspace Location
{workspace_path}

## Recent Work Log Entry
```
{str(trigger_item.get('item', {}))[:500]}
```

## Important Notes

- Verify the workspace state before starting
- Follow the Agent Communication Protocol in the workspace
- Request approvals if needed (check your decision authority)
- Update timestamps when making changes
"""
        return prompt
    
    def generate_prompt(self, agent_key: str, role_name: str, triggers: List[Dict[str, Any]], workspace_path: str) -> str:
        """Generate comprehensive prompt for an agent."""
        if not triggers:
            return ""
        
        # Group triggers by type
        approval_triggers = [t for t in triggers if t['type'] in ['approval_request', 'architecture_review']]
        task_triggers = [t for t in triggers if t['type'] not in ['approval_request', 'architecture_review']]
        
        # Deduplicate approval triggers by approval_id (safeguard)
        seen_approval_ids = set()
        deduplicated_approval_triggers = []
        for trigger in approval_triggers:
            approval = trigger['item']
            approval_id = approval.get('approval_id', '')
            if approval_id and approval_id not in seen_approval_ids:
                deduplicated_approval_triggers.append(trigger)
                seen_approval_ids.add(approval_id)
        
        prompt_parts = []
        prompt_parts.append(f"# {role_name} Action Required")
        prompt_parts.append("")
        prompt_parts.append(f"**Role**: {role_name}")
        prompt_parts.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        prompt_parts.append("")
        
        # Approval requests
        if deduplicated_approval_triggers:
            prompt_parts.append("## Approval Requests Requiring Your Response")
            prompt_parts.append("")
            for trigger in deduplicated_approval_triggers:
                approval = trigger['item']
                approval_id = approval.get('approval_id', '')
                requested_by = approval.get('requested_by', '')
                request_text = approval.get('request', '')
                
                prompt_parts.append(f"### {approval_id}")
                prompt_parts.append(f"- **Requested By**: {requested_by}")
                prompt_parts.append(f"- **Request**: {request_text}")
                prompt_parts.append(f"- **Priority**: {approval.get('priority', 'N/A')}")
                prompt_parts.append("")
                prompt_parts.append("**Your Action**:")
                prompt_parts.append("1. Review the work in PROJECT_WORKSPACE.md")
                prompt_parts.append("2. Make decision: ✅ Approved | ❌ Rejected | 🔄 Needs Revision")
                prompt_parts.append(f"3. Update {approval_id} in workspace with your response")
                prompt_parts.append("4. Update Work Log with your decision")
                prompt_parts.append("")
        
        # Task completion triggers
        if task_triggers:
            prompt_parts.append("## Tasks Ready for Your Action")
            prompt_parts.append("")
            for trigger in task_triggers:
                trigger_type = trigger['type']
                item = trigger.get('item', {})
                
                prompt_parts.append(f"### {trigger_type.replace('_', ' ').title()}")
                prompt_parts.append(f"- **Trigger**: {trigger_type}")
                prompt_parts.append("")
                
                if isinstance(item, dict):
                    if 'timestamp' in item:
                        prompt_parts.append(f"- **Work Log Entry**: {item.get('timestamp', '')}")
                        prompt_parts.append(f"- **Role**: {item.get('role', '')}")
                        prompt_parts.append(f"- **Task**: {item.get('task', '')}")
                
                prompt_parts.append("**Your Action**:")
                prompt_parts.append("1. Check PROJECT_WORKSPACE.md for current state")
                prompt_parts.append("2. Review your Role Status section")
                prompt_parts.append("3. Proceed with your next task")
                prompt_parts.append("4. Update workspace as you work")
                prompt_parts.append("")
        
        # Common instructions
        prompt_parts.append("## Workspace Location")
        prompt_parts.append(f"{workspace_path}")
        prompt_parts.append("")
        prompt_parts.append("## Important Instructions")
        prompt_parts.append("")
        prompt_parts.append("1. **Read First**: Always read the entire PROJECT_WORKSPACE.md before starting")
        prompt_parts.append("2. **Check Status**: Verify current state and check for conflicts")
        prompt_parts.append("3. **Follow Protocol**: Follow the Agent Communication Protocol in the workspace")
        prompt_parts.append("4. **Update Timestamps**: Always update 'Last Updated' when making changes")
        prompt_parts.append("5. **Request Approvals**: If your decision requires approval, create an Approval Request")
        prompt_parts.append("6. **Log Work**: Add Work Log entries for all significant actions")
        prompt_parts.append("")
        prompt_parts.append("## Decision Authority")
        prompt_parts.append("")
        prompt_parts.append("Check the workspace for your decision authority matrix.")
        prompt_parts.append("Remember: ALL budget decisions require User approval (not just CFO).")
        prompt_parts.append("")
        
        return "\n".join(prompt_parts)
    
    def create_prompt_file(self, agent_key: str, role_name: str, triggers: List[Dict[str, Any]], workspace_path: str) -> Optional[Path]:
        """Create a prompt file for an agent."""
        prompt_content = self.generate_prompt(agent_key, role_name, triggers, workspace_path)
        
        if not prompt_content:
            return None
        
        # Create prompt file
        prompt_filename = f"{agent_key}_action.md"
        prompt_path = self.prompt_dir / prompt_filename
        
        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write(prompt_content)
        
        return prompt_path
    
    def cleanup_old_prompts(self, keep_recent: int = 5):
        """Clean up old prompt files, keeping only recent ones."""
        prompt_files = sorted(self.prompt_dir.glob("*_action.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if len(prompt_files) > keep_recent:
            for old_file in prompt_files[keep_recent:]:
                try:
                    old_file.unlink()
                except Exception as e:
                    print(f"Warning: Failed to delete old prompt {old_file}: {e}")

