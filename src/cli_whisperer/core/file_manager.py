"""
File management module for transcript storage, rotation, and cleanup.

This module provides the TranscriptManager class which handles intelligent
file management including automatic rotation of transcript files and cleanup
of old files based on configurable retention policies.
"""

import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple


class TranscriptManager:
    """Manages transcript files with rotation and cleanup."""
    
    def __init__(self, base_dir: Path = Path("transcripts"), max_recent: int = 5, 
                 cleanup_days: int = 7):
        """
        Initialize the transcript manager.

        Args:
            base_dir (Path): Base directory for storing transcripts.
            max_recent (int): Maximum number of recent files to keep.
            cleanup_days (int): Number of days after which old files are deleted.
        """
        self.base_dir = base_dir
        self.max_recent = max_recent
        self.cleanup_days = cleanup_days
        
        # Create directory structure
        self.dirs = {
            'normal': base_dir / 'normal',
            'ai': base_dir / 'ai',
            'old_normal': base_dir / 'old' / 'original',
            'old_ai': base_dir / 'old' / 'ai'
        }
        
        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_timestamp_filename(self, base_name: str, extension: str) -> str:
        """
        Generate a filename with timestamp in mm-dd-yyyy_HH-MM-SS format.

        Args:
            base_name (str): Base name for the file.
            extension (str): File extension without the dot.

        Returns:
            str: Timestamped filename.
        """
        now = datetime.now()
        date_stamp = now.strftime("%m-%d-%Y")
        time_stamp = now.strftime("%H-%M-%S")
        return f"{base_name}_{date_stamp}_{time_stamp}.{extension}"
    
    def rename_current_file(self, directory: Path, extension: str) -> None:
        """
        Rename the current file to include a timestamp.

        Args:
            directory (Path): Directory containing the current file.
            extension (str): File extension without the dot.
        """
        current_file = directory / f"current_transcription.{extension}"
        if current_file.exists():
            # Get the modification time of the current file for the timestamp
            mtime = datetime.fromtimestamp(current_file.stat().st_mtime)
            date_stamp = mtime.strftime("%m-%d-%Y")
            time_stamp = mtime.strftime("%H-%M-%S")
            new_name = f"transcription_{date_stamp}_{time_stamp}.{extension}"
            new_path = directory / new_name
            current_file.rename(new_path)
            print(f"📝 Renamed current file to: {new_name}")
    
    def get_timestamped_files(self, directory: Path, extension: str) -> List[Tuple[datetime, Path]]:
        """
        Get all timestamped transcript files sorted by creation time.

        Args:
            directory (Path): Directory to search for files.
            extension (str): File extension without the dot.

        Returns:
            List[Tuple[datetime, Path]]: List of (timestamp, filepath) tuples sorted by newest first.
        """
        files = []
        # Look for files with timestamps (exclude current_transcription)
        for f in directory.glob(f"transcription_*-*-*_*-*-*.{extension}"):
            # Get file creation time
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            files.append((mtime, f))
        
        # Sort by timestamp (newest first)
        files.sort(key=lambda x: x[0], reverse=True)
        return files
    
    def rotate_files(self, directory: Path, old_directory: Path, extension: str) -> None:
        """
        Rotate files, keeping only the most recent max_recent files (including current).

        Args:
            directory (Path): Directory containing active files.
            old_directory (Path): Directory for archived files.
            extension (str): File extension without the dot.
        """
        # Get all timestamped files (not including current_transcription)
        files = self.get_timestamped_files(directory, extension)
        
        # Count current file if it exists
        current_file = directory / f"current_transcription.{extension}"
        current_exists = 1 if current_file.exists() else 0
        
        # Calculate how many timestamped files to keep
        # We want max_recent total, so if current exists, keep max_recent - 1 timestamped files
        timestamped_to_keep = self.max_recent - current_exists
        
        # Move old files if we have more than we should keep
        if len(files) > timestamped_to_keep:
            files_to_move = files[timestamped_to_keep:]
            for _, file_path in files_to_move:
                destination = old_directory / file_path.name
                shutil.move(str(file_path), str(destination))
                print(f"📁 Moved {file_path.name} to old directory")
    
    def cleanup_old_files(self) -> None:
        """Delete files older than cleanup_days from old directories."""
        cutoff_date = datetime.now() - timedelta(days=self.cleanup_days)
        
        for old_dir in [self.dirs['old_normal'], self.dirs['old_ai']]:
            for file_path in old_dir.iterdir():
                if file_path.is_file():
                    # Get file modification time
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff_date:
                        file_path.unlink()
                        print(f"🗑️  Deleted old file: {file_path.name}")
    
    def save_transcript(self, text: str, is_ai: bool = False) -> Path:
        """
        Save a transcript as 'current_transcription' with rotation of previous files.

        Args:
            text (str): The transcript text to save.
            is_ai (bool): Whether this is an AI-formatted transcript.

        Returns:
            Path: Path to the saved file.
        """
        extension = 'md' if is_ai else 'txt'
        directory = self.dirs['ai'] if is_ai else self.dirs['normal']
        old_directory = self.dirs['old_ai'] if is_ai else self.dirs['old_normal']
        
        # First, rename the existing current file if it exists
        self.rename_current_file(directory, extension)
        
        # Then rotate files to maintain max_recent limit
        self.rotate_files(directory, old_directory, extension)
        
        # Save new file as current_transcription
        filename = f"current_transcription.{extension}"
        file_path = directory / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return file_path