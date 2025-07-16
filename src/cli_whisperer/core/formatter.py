"""
Text formatting module using OpenAI's chat models.

This module provides the OpenAIFormatter class which enhances raw
transcriptions using AI to create well-structured markdown documents.
"""

import os
import threading
from typing import Optional

from openai import OpenAI


class OpenAIFormatter:
    """Handles AI-powered text formatting using OpenAI's chat models."""
    
    def __init__(self, model: str = "gpt-4.1-nano", api_key: Optional[str] = None,
                 disabled: bool = False):
        """
        Initialize the OpenAI formatter.

        Args:
            model (str): OpenAI model to use for formatting.
            api_key (Optional[str]): OpenAI API key. If None, uses environment variable.
            disabled (bool): Whether formatting is disabled.
        """
        self.model = model
        self.disabled = disabled
        self.client = None
        
        if not self.disabled:
            self._setup_client(api_key)
    
    def _setup_client(self, api_key: Optional[str]) -> None:
        """
        Set up OpenAI client with API key.

        Args:
            api_key (Optional[str]): OpenAI API key.
        """
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            # Try to get from environment variable
            env_api_key = os.getenv("OPENAI_API_KEY")
            if env_api_key:
                self.client = OpenAI(api_key=env_api_key)
            else:
                print("⚠️  OpenAI API key not found. Set OPENAI_API_KEY environment variable or use --openai-key")
                self.disabled = True
    
    def format_text(self, text: str, cleanup_callback: Optional[callable] = None) -> Optional[str]:
        """
        Use OpenAI to format the transcription into structured markdown.

        Args:
            text (str): Raw transcription text to format.
            cleanup_callback (Optional[callable]): Optional cleanup function to run in background.

        Returns:
            Optional[str]: Formatted markdown text, or None if formatting failed/disabled.
        """
        if self.disabled or not self.client:
            return None
        
        print("🤖 Formatting with OpenAI...")
        
        # Start cleanup in background while AI processes
        cleanup_thread = None
        if cleanup_callback:
            cleanup_thread = threading.Thread(target=cleanup_callback)
            cleanup_thread.start()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful assistant that converts voice transcriptions into well-structured markdown documents. 
                        Your task is to:
                        1. Parse the transcribed text and understand its intent
                        2. Format it into clear, well-organized markdown
                        3. Add appropriate headers, lists, code blocks, etc.
                        4. Fix any obvious transcription errors
                        5. Maintain the original meaning while improving clarity
                        
                        If the text appears to be instructions for creating issues, code, or documentation, 
                        format it appropriately with sections and clear action items."""
                    },
                    {
                        "role": "user",
                        "content": f"Please format this voice transcription into a well-structured markdown document to be given to an AI agent:\n\n<speechToText>{text}</speechToText>"
                    }
                ],
                temperature=0.3,
            )
            
            formatted_text = response.choices[0].message.content
            print("✅ OpenAI formatting complete!")
            
            # Wait for cleanup to finish
            if cleanup_thread:
                cleanup_thread.join()
            
            return formatted_text
            
        except Exception as e:
            print(f"❌ OpenAI formatting failed: {e}")
            if cleanup_thread:
                cleanup_thread.join()
            return None