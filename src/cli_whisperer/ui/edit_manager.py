"""
Edit Manager for CLI Whisperer.

This module provides the EditManager class which handles nvim integration
for editing transcript files directly from the TUI interface.
"""

import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import Optional, Callable


class EditManager:
    """Manages nvim integration for editing transcript files."""
    
    def __init__(self):
        """Initialize the edit manager."""
        self.current_editor_process = None
        self.file_watchers = {}
        
    def is_nvim_available(self) -> bool:
        """Check if nvim is available on the system."""
        try:
            result = subprocess.run(
                ["nvim", "--version"], 
                capture_output=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def edit_file_with_nvim(self, file_path: Path, callback: Optional[Callable] = None) -> bool:
        """
        Open a file with nvim for editing.
        
        Args:
            file_path (Path): Path to the file to edit.
            callback (Optional[Callable]): Function to call when editing is complete.
            
        Returns:
            bool: True if nvim was launched successfully, False otherwise.
        """
        if not self.is_nvim_available():
            return False
            
        if not file_path.exists():
            return False
            
        try:
            # Store original file modification time
            original_mtime = file_path.stat().st_mtime
            
            # Create a script to run nvim in a new terminal
            if self._is_macos():
                return self._edit_with_nvim_macos(file_path, callback, original_mtime)
            else:
                return self._edit_with_nvim_linux(file_path, callback, original_mtime)
                
        except Exception:
            return False
    
    def _is_macos(self) -> bool:
        """Check if running on macOS."""
        import platform
        return platform.system() == "Darwin"
    
    def _edit_with_nvim_macos(self, file_path: Path, callback: Optional[Callable], original_mtime: float) -> bool:
        """Launch nvim on macOS using osascript."""
        try:
            # Create AppleScript to open Terminal with nvim
            script = f'''
            tell application "Terminal"
                activate
                do script "nvim '{file_path}'"
            end tell
            '''
            
            subprocess.Popen([
                "osascript", "-e", script
            ], start_new_session=True)
            
            # Start file watcher if callback provided
            if callback:
                self._start_file_watcher(file_path, callback, original_mtime)
                
            return True
            
        except Exception:
            return False
    
    def _edit_with_nvim_linux(self, file_path: Path, callback: Optional[Callable], original_mtime: float) -> bool:
        """Launch nvim on Linux using available terminal emulator."""
        try:
            # Try different terminal emulators
            terminals = [
                ["gnome-terminal", "--", "nvim", str(file_path)],
                ["xterm", "-e", "nvim", str(file_path)],
                ["konsole", "-e", "nvim", str(file_path)],
                ["alacritty", "-e", "nvim", str(file_path)],
            ]
            
            for terminal_cmd in terminals:
                try:
                    subprocess.Popen(terminal_cmd, start_new_session=True)
                    
                    # Start file watcher if callback provided
                    if callback:
                        self._start_file_watcher(file_path, callback, original_mtime)
                        
                    return True
                except FileNotFoundError:
                    continue
                    
            return False
            
        except Exception:
            return False
    
    def _start_file_watcher(self, file_path: Path, callback: Callable, original_mtime: float):
        """Start watching a file for changes."""
        def watch_file():
            """Watch file for modifications."""
            try:
                while True:
                    time.sleep(1)  # Check every second
                    
                    if not file_path.exists():
                        break
                        
                    current_mtime = file_path.stat().st_mtime
                    if current_mtime > original_mtime:
                        # File was modified, call callback and stop watching
                        callback(file_path)
                        break
                        
            except Exception:
                pass  # Silently handle any errors
            finally:
                # Clean up watcher
                if str(file_path) in self.file_watchers:
                    del self.file_watchers[str(file_path)]
        
        # Start watcher thread
        watcher_thread = threading.Thread(target=watch_file, daemon=True)
        self.file_watchers[str(file_path)] = watcher_thread
        watcher_thread.start()
    
    def edit_text_in_nvim(self, text: str, file_extension: str = ".txt", callback: Optional[Callable] = None) -> Optional[Path]:
        """
        Edit text content in nvim using a temporary file.
        
        Args:
            text (str): Text content to edit.
            file_extension (str): File extension for the temporary file.
            callback (Optional[Callable]): Function to call when editing is complete.
            
        Returns:
            Optional[Path]: Path to the temporary file if successful, None otherwise.
        """
        if not self.is_nvim_available():
            return None
            
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                mode='w', 
                suffix=file_extension, 
                delete=False,
                encoding='utf-8'
            ) as temp_file:
                temp_file.write(text)
                temp_path = Path(temp_file.name)
            
            # Edit the temporary file
            if self.edit_file_with_nvim(temp_path, callback):
                return temp_path
            else:
                # Clean up if edit failed
                temp_path.unlink(missing_ok=True)
                return None
                
        except Exception:
            return None
    
    def stop_all_watchers(self):
        """Stop all file watchers."""
        for watcher in self.file_watchers.values():
            if watcher.is_alive():
                # Watchers are daemon threads, they'll stop when main thread exits
                pass
        self.file_watchers.clear()