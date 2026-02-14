"""
Workspace Monitor - Watches PROJECT_WORKSPACE.md for changes.
Uses file watcher (watchdog) with polling fallback.
"""

import time
import os
from pathlib import Path
from typing import Callable, Optional
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Warning: watchdog not available, using polling mode")


class WorkspaceMonitor:
    """Monitors workspace file for changes."""
    
    def __init__(self, workspace_path: str, poll_interval: int = 30, on_change: Optional[Callable] = None):
        self.workspace_path = Path(workspace_path)
        self.poll_interval = poll_interval
        self.on_change = on_change
        self.last_modified = self._get_file_mtime()
        self.observer: Optional[Observer] = None
        self.running = False
    
    def _get_file_mtime(self) -> float:
        """Get file modification time."""
        if self.workspace_path.exists():
            return os.path.getmtime(self.workspace_path)
        return 0.0
    
    def _has_changed(self) -> bool:
        """Check if file has been modified."""
        current_mtime = self._get_file_mtime()
        if current_mtime > self.last_modified:
            self.last_modified = current_mtime
            return True
        return False
    
    def _on_file_changed(self):
        """Handle file change event."""
        if self.on_change:
            try:
                self.on_change(self.workspace_path)
            except Exception as e:
                print(f"Error in change handler: {e}")
    
    def start_watcher(self):
        """Start file watcher (watchdog)."""
        if not WATCHDOG_AVAILABLE:
            print("watchdog not available, falling back to polling")
            return False
        
        if not self.workspace_path.exists():
            print(f"Workspace file not found: {self.workspace_path}")
            return False
        
        class WorkspaceHandler(FileSystemEventHandler):
            def __init__(self, monitor):
                self.monitor = monitor
            
            def on_modified(self, event):
                if not event.is_directory and Path(event.src_path) == self.monitor.workspace_path:
                    self.monitor._on_file_changed()
        
        try:
            self.observer = Observer()
            handler = WorkspaceHandler(self)
            # Watch the parent directory
            self.observer.schedule(handler, str(self.workspace_path.parent), recursive=False)
            self.observer.start()
            self.running = True
            print(f"File watcher started for {self.workspace_path}")
            return True
        except Exception as e:
            print(f"Failed to start file watcher: {e}")
            return False
    
    def start_polling(self):
        """Start polling mode (fallback)."""
        self.running = True
        print(f"Polling mode started (interval: {self.poll_interval}s) for {self.workspace_path}")
        
        while self.running:
            if self._has_changed():
                print(f"[{datetime.now()}] Workspace file changed")
                self._on_file_changed()
            time.sleep(self.poll_interval)
    
    def start(self):
        """Start monitoring (tries watcher first, falls back to polling)."""
        if WATCHDOG_AVAILABLE:
            if self.start_watcher():
                # Keep running
                try:
                    while self.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.stop()
                return
        
        # Fallback to polling
        self.start_polling()
    
    def stop(self):
        """Stop monitoring."""
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
            print("File watcher stopped")
    
    def check_once(self) -> bool:
        """Check once if file has changed (for manual checks)."""
        if self._has_changed():
            self._on_file_changed()
            return True
        return False

