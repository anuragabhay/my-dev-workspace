"""
Workspace Parser - Parses PROJECT_WORKSPACE.md to extract actionable items.
Extracts: approval requests, task statuses, blockers, work log entries.
"""

import re
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime


class WorkspaceParser:
    """Parses workspace markdown to extract actionable items."""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.content = ""
    
    def load(self) -> str:
        """Load workspace content."""
        if not self.workspace_path.exists():
            raise FileNotFoundError(f"Workspace file not found: {self.workspace_path}")
        
        with open(self.workspace_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
        return self.content
    
    def parse_approval_requests(self) -> List[Dict[str, Any]]:
        """Parse approval requests section."""
        approvals = []
        seen_approval_ids = set()  # Track approval IDs to prevent duplicates
        
        # Find approval requests section
        approval_section_match = re.search(
            r'## ✅ Approval Requests & Responses\s*\n(.*?)(?=\n## |\Z)',
            self.content,
            re.DOTALL
        )
        
        if not approval_section_match:
            return approvals
        
        approval_section = approval_section_match.group(1)
        
        # Find all approval blocks
        approval_pattern = r'### \[OPEN\] Approval #(\d+)\s*\n(.*?)(?=\n### |\Z)'
        for match in re.finditer(approval_pattern, approval_section, re.DOTALL):
            approval_id = f"#{match.group(1)}"
            
            # Skip if we've already seen this approval ID
            if approval_id in seen_approval_ids:
                continue
            
            approval_content = match.group(2)
            
            # Extract approval details
            requested_by_match = re.search(r'\*\*Requested By\*\*:\s*(.+)', approval_content)
            requested_from_match = re.search(r'\*\*Requested From\*\*:\s*(.+)', approval_content)
            date_match = re.search(r'\*\*Date\*\*:\s*(.+)', approval_content)
            type_match = re.search(r'\*\*Type\*\*:\s*(.+)', approval_content)
            request_match = re.search(r'\*\*Request\*\*:\s*"(.+)"', approval_content)
            priority_match = re.search(r'\*\*Priority\*\*:\s*(.+)', approval_content)
            status_match = re.search(r'\*\*Status\*\*:\s*(.+)', approval_content)
            
            # Check if status indicates pending
            status_text = status_match.group(1) if status_match else ""
            if "⏳ Pending" in status_text or "[OPEN]" in approval_content:
                approvals.append({
                    "approval_id": approval_id,
                    "requested_by": requested_by_match.group(1).strip() if requested_by_match else "",
                    "requested_from": requested_from_match.group(1).strip() if requested_from_match else "",
                    "date": date_match.group(1).strip() if date_match else "",
                    "type": type_match.group(1).strip() if type_match else "",
                    "request": request_match.group(1).strip() if request_match else "",
                    "priority": priority_match.group(1).strip() if priority_match else "",
                    "status": status_text.strip(),
                    "content": approval_content
                })
                seen_approval_ids.add(approval_id)
        
        return approvals
    
    def parse_role_status(self, role_name: str) -> Dict[str, Any]:
        """Parse a specific role's status section."""
        # Find role section
        role_pattern = rf'## .*{role_name}.*Status\s*\n(.*?)(?=\n## |\Z)'
        match = re.search(role_pattern, self.content, re.DOTALL | re.IGNORECASE)
        
        if not match:
            return {}
        
        role_section = match.group(1)
        
        # Extract current status
        status_match = re.search(r'\*\*Current Status\*\*:\s*(.+)', role_section)
        last_updated_match = re.search(r'\*\*Last Updated\*\*:\s*(.+)', role_section)
        
        # Extract tasks
        tasks = []
        task_section_match = re.search(r'\*\*Tasks:\*\*\s*\n(.*?)(?=\*\*|$)', role_section, re.DOTALL)
        if task_section_match:
            task_lines = task_section_match.group(1).strip().split('\n')
            for line in task_lines:
                if line.strip().startswith('- ['):
                    tasks.append(line.strip())
        
        # Extract blockers
        blockers_match = re.search(r'\*\*Blockers\*\*:\s*(.+)', role_section)
        blockers = blockers_match.group(1).strip() if blockers_match else "None"
        
        # Extract next action
        next_action_match = re.search(r'\*\*Next Action\*\*:\s*(.+)', role_section)
        next_action = next_action_match.group(1).strip() if next_action_match else ""
        
        return {
            "current_status": status_match.group(1).strip() if status_match else "",
            "last_updated": last_updated_match.group(1).strip() if last_updated_match else "",
            "tasks": tasks,
            "blockers": blockers,
            "next_action": next_action,
            "section_content": role_section
        }
    
    def parse_work_log(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Parse recent work log entries."""
        entries = []
        
        # Find work log section
        work_log_match = re.search(
            r'## 📝 Work Log \(Latest First\)\s*\n(.*?)(?=\n## |\Z)',
            self.content,
            re.DOTALL
        )
        
        if not work_log_match:
            return entries
        
        work_log_section = work_log_match.group(1)
        
        # Find all work log entries
        entry_pattern = r'### \[([^\]]+)\] \[([^\]]+)\] \[([^\]]+)\] \[([^\]]+)\]\s*\n(.*?)(?=\n### |\Z)'
        for match in re.finditer(entry_pattern, work_log_section, re.DOTALL):
            timestamp = match.group(1)
            role = match.group(2)
            task = match.group(3)
            status = match.group(4)
            content = match.group(5)
            
            entries.append({
                "timestamp": timestamp,
                "role": role,
                "task": task,
                "status": status,
                "content": content.strip()
            })
            
            if len(entries) >= limit:
                break
        
        return entries
    
    def parse_blockers(self) -> List[Dict[str, Any]]:
        """Parse blockers section."""
        blockers = []
        
        # Find blockers section
        blockers_match = re.search(
            r'## ⚠️ Blockers & Issues\s*\n(.*?)(?=\n## |\Z)',
            self.content,
            re.DOTALL
        )
        
        if not blockers_match:
            return blockers
        
        blockers_section = blockers_match.group(1)
        
        # Check for active blockers (not resolved)
        if "No active blockers" in blockers_section or "*No active blockers*" in blockers_section:
            return blockers
        
        # Find blocker entries (format: ### Blocker #XXX)
        blocker_pattern = r'### (?:\[ACTIVE\]|\[RESOLVED\])?.*Blocker #(\d+)\s*\n(.*?)(?=\n### |\Z)'
        for match in re.finditer(blocker_pattern, blockers_section, re.DOTALL):
            blocker_id = match.group(1)
            blocker_content = match.group(2)
            
            # Check if resolved
            if "RESOLVED" in blocker_content or "✅ Resolved" in blocker_content:
                continue
            
            blockers.append({
                "blocker_id": blocker_id,
                "content": blocker_content.strip()
            })
        
        return blockers
    
    def parse_project_status(self) -> Dict[str, Any]:
        """Parse project status dashboard."""
        status = {}
        
        # Find project status section
        status_match = re.search(
            r'## 📊 Project Status Dashboard\s*\n(.*?)(?=\n---|\n## )',
            self.content,
            re.DOTALL
        )
        
        if not status_match:
            return status
        
        status_section = status_match.group(1)
        
        # Extract key fields
        overall_status_match = re.search(r'\*\*Overall Status\*\*:\s*(.+)', status_section)
        current_phase_match = re.search(r'\*\*Current Phase\*\*:\s*(.+)', status_section)
        last_updated_match = re.search(r'\*\*Last Updated\*\*:\s*(.+)', status_section)
        active_agents_match = re.search(r'\*\*Active Agents\*\*:\s*(.+)', status_section)
        pending_approvals_match = re.search(r'\*\*Pending Approvals\*\*:\s*(\d+)', status_section)
        blockers_match = re.search(r'\*\*Blockers\*\*:\s*(.+)', status_section)
        next_actions_match = re.search(r'\*\*Next Actions\*\*:\s*(.+)', status_section)
        
        status = {
            "overall_status": overall_status_match.group(1).strip() if overall_status_match else "",
            "current_phase": current_phase_match.group(1).strip() if current_phase_match else "",
            "last_updated": last_updated_match.group(1).strip() if last_updated_match else "",
            "active_agents": active_agents_match.group(1).strip() if active_agents_match else "",
            "pending_approvals_count": int(pending_approvals_match.group(1)) if pending_approvals_match else 0,
            "blockers": blockers_match.group(1).strip() if blockers_match else "None",
            "next_actions": next_actions_match.group(1).strip() if next_actions_match else ""
        }
        
        return status
    
    def extract_relevant_section(self, section_name: str) -> Optional[str]:
        """Extract a specific section from workspace for context."""
        # Try to find section by heading
        pattern = rf'## .*{re.escape(section_name)}.*\s*\n(.*?)(?=\n## |\Z)'
        match = re.search(pattern, self.content, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        return None
    
    def parse_all(self) -> Dict[str, Any]:
        """Parse all actionable items from workspace."""
        self.load()
        
        return {
            "approval_requests": self.parse_approval_requests(),
            "project_status": self.parse_project_status(),
            "blockers": self.parse_blockers(),
            "recent_work_log": self.parse_work_log(limit=5),
            "parsed_at": datetime.now().isoformat()
        }

