"""
Clipboard integration module for system clipboard operations.

This module provides the ClipboardManager class which handles copying
transcribed text to the system clipboard.
"""

import pyperclip


class ClipboardManager:
    """Handles clipboard operations for transcribed text."""
    
    def __init__(self):
        """Initialize the clipboard manager."""
        pass
    
    def copy_to_clipboard(self, text: str) -> bool:
        """
        Copy text to system clipboard.

        Args:
            text (str): Text to copy to clipboard.

        Returns:
            bool: True if copy succeeded, False otherwise.
        """
        try:
            pyperclip.copy(text)
            print("📋 Copied to clipboard!")
            return True
        except Exception as e:
            print(f"❌ Failed to copy to clipboard: {e}")
            return False