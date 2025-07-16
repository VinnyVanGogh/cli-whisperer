"""
History management module for tracking transcription sessions.

This module provides the HistoryManager class which maintains a JSON
history of transcription sessions with metadata for easy retrieval.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class HistoryManager:
    """Manages transcription history tracking and display."""
    
    def __init__(self, history_file: Path):
        """
        Initialize the history manager.

        Args:
            history_file (Path): Path to the history JSON file.
        """
        self.history_file = history_file
    
    def save_to_history(self, text: str, txt_path: Path, model_name: str,
                       md_path: Optional[Path] = None, working_dir: Optional[str] = None) -> None:
        """
        Save transcription to history.

        Args:
            text (str): Transcribed text.
            txt_path (Path): Path to saved text file.
            model_name (str): Name of Whisper model used.
            md_path (Optional[Path]): Path to saved markdown file, if any.
            working_dir (Optional[str]): Working directory when transcript was created.
        """
        try:
            history = []
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
            
            # Add new entry
            entry = {
                'timestamp': datetime.now().isoformat(),
                'text': text[:200] + "..." if len(text) > 200 else text,
                'model': model_name,
                'txt_file': str(txt_path),
                'md_file': str(md_path) if md_path else None,
                'working_dir': working_dir or os.getcwd()
            }
            history.insert(0, entry)
            
            # Keep only last 50 entries
            history = history[:50]
            
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Failed to save history: {e}")
    
    def show_history(self, n: int = 10) -> None:
        """
        Show recent transcriptions.

        Args:
            n (int): Number of recent transcriptions to show.
        """
        if not self.history_file.exists():
            print("📜 No history found")
            return
        
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            
            print(f"\n📜 Recent transcriptions (showing last {n}):")
            print("-" * 80)
            
            for i, entry in enumerate(history[:n]):
                timestamp = entry['timestamp']
                text = entry['text']
                txt_file = Path(entry['txt_file']).name
                md_file = Path(entry['md_file']).name if entry.get('md_file') else "N/A"
                
                print(f"{i+1}. [{timestamp}]")
                print(f"   Text: {text}")
                print(f"   Files: {txt_file} | {md_file}")
                print()
                
        except Exception as e:
            print(f"❌ Failed to read history: {e}")
    
    def get_history(self, working_dir_filter: Optional[str] = None) -> list:
        """
        Get history entries, optionally filtered by working directory.
        
        Args:
            working_dir_filter (Optional[str]): Filter by working directory path.
            
        Returns:
            list: List of history entries.
        """
        if not self.history_file.exists():
            return []
            
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
                
            # Filter by working directory if specified
            if working_dir_filter:
                history = [entry for entry in history 
                          if entry.get('working_dir') == working_dir_filter]
                
            return history
        except Exception as e:
            print(f"❌ Failed to read history: {e}")
            return []
    
    def get_unique_directories(self) -> list:
        """
        Get a list of unique working directories from history.
        
        Returns:
            list: List of unique directory paths.
        """
        if not self.history_file.exists():
            return []
            
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
                
            directories = set()
            for entry in history:
                working_dir = entry.get('working_dir')
                if working_dir:
                    directories.add(working_dir)
                    
            return sorted(list(directories))
        except Exception as e:
            print(f"❌ Failed to read history: {e}")
            return []