"""
Transcription module using OpenAI's Whisper model.

This module provides the WhisperTranscriber class which handles loading
Whisper models and transcribing audio data to text.
"""

import os
import tempfile
import time
from typing import Optional

import numpy as np
import scipy.io.wavfile as wav
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration

from ..utils.logger import get_logger

# Try to import whisper directly as fallback
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class WhisperTranscriber:
    """Handles speech-to-text transcription using Whisper models."""
    
    def __init__(self, model_name: str = "base"):
        """
        Initialize the Whisper transcriber.

        Args:
            model_name (str): Name of the Whisper model to use.
        """
        self.model_name = model_name
        self.model = None
        self.processor = None
        self.sample_rate = 16000
        
        print(f"🔄 Loading Whisper {model_name} model...")
        self._load_model()
        print(f"✅ Model loaded!")
    
    def _load_model(self) -> None:
        """Load Whisper model with fallback to base if needed."""
        try:
            print(f"🔄 Attempting to load Whisper model: {self.model_name}")
            model_mapping = {
                "tiny": "openai/whisper-tiny",
                "base": "openai/whisper-base",
                "small": "openai/whisper-small",
                "medium": "openai/whisper-medium",
                "large": "openai/whisper-large"
            }
            model_id = model_mapping.get(self.model_name, "openai/whisper-base")
            self.processor = WhisperProcessor.from_pretrained(model_id)
            self.model = WhisperForConditionalGeneration.from_pretrained(model_id)
        except Exception as e:
            print(f"⚠️  Failed to load {self.model_name}: {e}")
            print("🔄 Falling back to base model...")
            self.processor = WhisperProcessor.from_pretrained("openai/whisper-base")
            self.model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-base")
            self.model_name = "base"
        print(f"Using Whisper model: {self.model_name} (sample rate: {self.sample_rate} Hz)")
    
    def _estimate_processing_time(self, audio_duration: float) -> float:
        """
        Estimate processing time based on model and audio duration.

        Args:
            audio_duration (float): Duration of audio in seconds.

        Returns:
            float: Estimated processing time in seconds.
        """
        # These are rough estimates based on typical performance
        model_multipliers = {
            'tiny': 0.5,
            'base': 1.0,
            'small': 2.0,
            'medium': 5.0,
            'large': 10.0
        }
        multiplier = model_multipliers.get(self.model_name, 1.0)
        return audio_duration * multiplier * 0.2  # Rough estimate
    
    def transcribe_audio(self, audio_data: np.ndarray) -> Optional[str]:
        """
        Transcribe audio data using Whisper with detailed logging.

        Args:
            audio_data (np.ndarray): Audio data to transcribe.

        Returns:
            Optional[str]: Transcribed text, or None if transcription failed.
        """
        logger = get_logger()
        logger.info(f"Starting transcription of audio data", {
            "audio_shape": audio_data.shape,
            "audio_dtype": str(audio_data.dtype),
            "model_name": self.model_name
        })
        
        audio_duration = len(audio_data) / self.sample_rate
        print(f"🔄 Transcribing {int(audio_duration)} seconds of audio...")
        logger.info(f"Audio duration: {audio_duration:.2f} seconds")
        
        # Estimate processing time
        estimated_time = self._estimate_processing_time(audio_duration)
        print(f"⏱️  Estimated processing time: ~{int(estimated_time)} seconds")
        start_time = time.time()
        
        try:
            # Step 1: Audio preprocessing
            logger.info("Step 1: Starting audio preprocessing")
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
                logger.info("Converted audio to float32")
            
            # Normalize audio to [-1, 1] range
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val
                logger.info(f"Normalized audio data (max_val was {max_val})")
            else:
                logger.warning("Audio has zero amplitude - no normalization needed")
            
            # Step 2: Feature extraction
            logger.info("Step 2: Starting feature extraction")
            logger.info(f"Audio data shape before processing: {audio_data.shape}")
            logger.info(f"Audio data type: {audio_data.dtype}")
            logger.info(f"Audio data range: min={audio_data.min():.6f}, max={audio_data.max():.6f}")
            
            # Ensure audio is 1D for whisper processor
            if len(audio_data.shape) > 1:
                audio_data = audio_data.squeeze()
                logger.info(f"Squeezed audio data to shape: {audio_data.shape}")
            
            # Additional safety checks
            if audio_data.size == 0:
                logger.error("Audio data is empty - cannot process")
                return None
                
            if not np.isfinite(audio_data).all():
                logger.error("Audio data contains non-finite values")
                return None
                
            try:
                input_features = self.processor(
                    audio_data,
                    sampling_rate=self.sample_rate,
                    return_tensors="pt"
                ).input_features
                logger.info(f"Feature extraction completed - input_features shape: {input_features.shape}")
            except Exception as e:
                logger.error(f"Feature extraction failed: {str(e)}")
                logger.error(f"Error type: {type(e).__name__}")
                # Try with a smaller chunk of audio as fallback
                logger.info("Attempting fallback with truncated audio")
                try:
                    # Use only first 30 seconds max
                    max_samples = 30 * self.sample_rate
                    if len(audio_data) > max_samples:
                        audio_data = audio_data[:max_samples]
                        logger.info(f"Truncated audio to {len(audio_data)} samples ({len(audio_data)/self.sample_rate:.1f}s)")
                    
                    input_features = self.processor(
                        audio_data,
                        sampling_rate=self.sample_rate,
                        return_tensors="pt"
                    ).input_features
                    logger.info(f"Fallback feature extraction completed - input_features shape: {input_features.shape}")
                except Exception as e2:
                    logger.error(f"Fallback feature extraction also failed: {str(e2)}")
                    # Try using the direct whisper library as final fallback
                    if WHISPER_AVAILABLE:
                        logger.info("Attempting transcription with direct whisper library")
                        return self._transcribe_with_whisper_direct(audio_data)
                    return None
            
            # Step 3: Model inference 
            logger.info("Step 3: Starting model inference (this may take a while)")
            with torch.no_grad():
                predicted_ids = self.model.generate(input_features)
            logger.info(f"Model inference completed - predicted_ids shape: {predicted_ids.shape}")
            
            # Step 4: Decoding
            logger.info("Step 4: Starting text decoding")
            text = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
            logger.info(f"Text decoding completed - text length: {len(text)}")
            
            elapsed = time.time() - start_time
            print(f"✅ Transcription complete in {elapsed:.1f} seconds!")
            logger.info(f"Transcription successful", {
                "elapsed_time": elapsed,
                "text_length": len(text),
                "text_preview": text[:100] + "..." if len(text) > 100 else text
            })
            
            return text.strip()
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Transcription failed: {e}")
            logger.error(f"Transcription failed after {elapsed:.1f} seconds", {
                "error": str(e),
                "error_type": type(e).__name__
            }, exc_info=True)
            return None
    
    def _transcribe_with_whisper_direct(self, audio_data: np.ndarray) -> Optional[str]:
        """Fallback transcription using direct whisper library."""
        logger = get_logger()
        
        if not WHISPER_AVAILABLE:
            logger.error("Direct whisper library not available")
            return None
            
        try:
            logger.info("Loading whisper model directly")
            # Map model names to direct whisper
            model_name_mapping = {
                "tiny": "tiny",
                "base": "base", 
                "small": "small",
                "medium": "medium",
                "large": "large"
            }
            whisper_model_name = model_name_mapping.get(self.model_name, "base")
            
            # Load model
            model = whisper.load_model(whisper_model_name)
            logger.info(f"Direct whisper model loaded: {whisper_model_name}")
            
            # Ensure audio is 1D and normalized
            if len(audio_data.shape) > 1:
                audio_data = audio_data.squeeze()
                
            # Whisper expects audio in [-1, 1] range
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val
                
            logger.info("Starting direct whisper transcription")
            result = model.transcribe(audio_data)
            text = result["text"].strip()
            
            logger.info(f"Direct whisper transcription completed: {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"Direct whisper transcription failed: {str(e)}")
            return None