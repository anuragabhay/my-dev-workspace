"""
Main entry point for Agent Automation System.
Monitors PROJECT_WORKSPACE.md and triggers agents when action is needed.
Uses workspace_config for path resolution (WORKSPACE_ROOT env or workspace_config.yaml).
"""

import sys
import hashlib
from pathlib import Path
from typing import Dict, Any

from monitor import WorkspaceMonitor
from parser import WorkspaceParser
from router import AgentRouter
from trigger import AgentTrigger
from state_tracker import StateTracker
from workspace_config import load_config


class AgentAutomationSystem:
    """Main automation system that coordinates all components."""
    
    def __init__(self, config_path: str = None):
        self.config = load_config(str(config_path) if config_path else None)
        config_path = Path(self.config.get("_config_path", "config.yaml"))
        
        # Initialize components
        self.state_tracker = StateTracker(
            db_path=self.config['state_db'],
            json_backup_path=self.config['json_backup']
        )
        self.parser = WorkspaceParser(self.config['workspace_path'])
        self.router = AgentRouter(config=self.config)
        self.trigger = AgentTrigger(
            config=self.config,
            workspace_path=self.config['workspace_path']
        )
        
        self.workspace_path = Path(self.config['workspace_path'])
    
    def _generate_task_hash(self, item: Dict[str, Any], trigger_type: str) -> str:
        """Generate a hash for a task/item to track if processed."""
        content = f"{trigger_type}_{item.get('item_id', '')}_{str(item)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def process_workspace_change(self, workspace_path: Path):
        """Process workspace file change."""
        print(f"\n[{self._get_timestamp()}] Processing workspace change...")
        
        try:
            # Parse workspace
            parsed_data = self.parser.parse_all()
            
            # Find agents to trigger
            agents_to_trigger = self.router.find_agents_to_trigger(parsed_data)
            
            if not agents_to_trigger:
                print("  No agents need to be triggered at this time.")
                return
            
            print(f"  Found {len(agents_to_trigger)} agent(s) to trigger")
            
            # Process each agent
            for agent_info in agents_to_trigger:
                agent_key = agent_info['agent_key']
                role_name = agent_info['role_name']
                triggers = agent_info['triggers']
                
                print(f"\n  Processing {role_name} ({agent_key})...")
                
                # Check each trigger
                valid_triggers = []
                for trigger in triggers:
                    trigger_type = trigger['type']
                    item_id = trigger.get('item_id', '')
                    
                    # Check if already processed
                    if trigger_type == 'approval_request' and item_id:
                        if self.state_tracker.is_approval_processed(item_id):
                            print(f"    Skipping {item_id} (already processed)")
                            continue
                    
                    # Generate task hash for other triggers
                    task_hash = self._generate_task_hash(trigger, trigger_type)
                    if self.state_tracker.is_task_processed(task_hash):
                        print(f"    Skipping {trigger_type} (already processed)")
                        continue
                    
                    valid_triggers.append(trigger)
                
                if not valid_triggers:
                    print(f"    No new triggers for {role_name}")
                    continue
                
                # Generate prompt file
                prompt_path = self.trigger.create_prompt_file(
                    agent_key=agent_key,
                    role_name=role_name,
                    triggers=valid_triggers,
                    workspace_path=str(self.workspace_path)
                )
                
                if prompt_path:
                    print(f"    ✓ Created prompt: {prompt_path}")
                    
                    # Mark as processed
                    for trigger in valid_triggers:
                        trigger_type = trigger['type']
                        item_id = trigger.get('item_id', '')
                        
                        if trigger_type == 'approval_request' and item_id:
                            self.state_tracker.mark_approval_processed(
                                approval_id=item_id,
                                role=role_name
                            )
                        else:
                            task_hash = self._generate_task_hash(trigger, trigger_type)
                            self.state_tracker.mark_task_processed(
                                task_hash=task_hash,
                                role=role_name,
                                task_description=f"{trigger_type}: {item_id}"
                            )
                        
                        # Log trigger
                        self.state_tracker.log_trigger(
                            role=role_name,
                            trigger_type=trigger_type,
                            item_id=item_id,
                            prompt_file=str(prompt_path)
                        )
                else:
                    print(f"    ⚠ No prompt generated for {role_name}")
            
            # Update last check time
            self.state_tracker.update_last_check()
            
            # Cleanup old prompts
            self.trigger.cleanup_old_prompts(keep_recent=10)
            
            print(f"\n[{self._get_timestamp()}] Processing complete.")
        
        except Exception as e:
            print(f"  ✗ Error processing workspace: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def run_once(self):
        """Run a single check of the workspace."""
        print(f"[{self._get_timestamp()}] Running single check...")
        self.process_workspace_change(self.workspace_path)
    
    def run_continuous(self):
        """Run continuous monitoring."""
        print(f"[{self._get_timestamp()}] Starting continuous monitoring...")
        print(f"  Workspace: {self.workspace_path}")
        print(f"  Prompt directory: {self.trigger.prompt_dir}")
        print(f"  State database: {self.state_tracker.db_path}")
        print("\n  Monitoring workspace for changes...")
        print("  Press Ctrl+C to stop\n")
        
        # Initial check
        self.run_once()
        
        # Start monitor
        monitor = WorkspaceMonitor(
            workspace_path=str(self.workspace_path),
            poll_interval=self.config.get('poll_interval', 30),
            on_change=self.process_workspace_change
        )
        
        try:
            monitor.start()
        except KeyboardInterrupt:
            print("\n\nStopping monitor...")
            monitor.stop()
            print("Monitor stopped.")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Agent Automation System - Monitors PROJECT_WORKSPACE.md and triggers agents'
    )
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to config.yaml file'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run a single check instead of continuous monitoring'
    )
    
    args = parser.parse_args()
    
    # Check if config exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        print("Please create config.yaml or specify path with --config")
        sys.exit(1)
    
    # Initialize and run system
    system = AgentAutomationSystem(config_path=str(config_path))
    
    if args.once:
        system.run_once()
    else:
        system.run_continuous()


if __name__ == '__main__':
    main()

