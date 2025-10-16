"""
Voice Pipeline for CampusConvo
Handles Speech-to-Text (STT) and Text-to-Speech (TTS)
Server-side processing for minimal client load
"""

import logging
import io
import base64
import whisper
from gtts import gTTS
import tempfile
from pathlib import Path

from server import config

logger = logging.getLogger(__name__)


class VoicePipeline:
    """Voice processing pipeline for STT and TTS"""
    
    def __init__(self):
        """Initialize voice pipeline"""
        logger.info("Initializing Voice Pipeline")
        
        if not config.ENABLE_VOICE:
            logger.info("Voice features disabled")
            self.enabled = False
            return
        
        self.enabled = True
        
        # Load Whisper model for STT
        try:
            logger.info(f"Loading Whisper model: {config.STT_MODEL}")
            logger.info("This may take a while on first run (downloading model)...")
            self.whisper_model = whisper.load_model(config.STT_MODEL)
            logger.info("✓ Whisper STT initialized successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper: {e}")
            self.enabled = False
            return
        
        logger.info("✓ Voice Pipeline initialization complete")
    
    def transcribe_audio(self, audio_data: bytes) -> str:
        """
        Convert speech to text using Whisper
        
        Args:
            audio_data: Audio file bytes (WAV, MP3, etc.)
            
        Returns:
            Transcribed text
        """
        if not self.enabled:
            raise RuntimeError("Voice features not enabled")
        
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name
            
            # Transcribe with Whisper
            logger.info(f"🎙️  Transcribing audio ({len(audio_data)} bytes)...")
            result = self.whisper_model.transcribe(
                temp_audio_path,
                language=config.STT_LANGUAGE
            )
            
            # Clean up temporary file
            Path(temp_audio_path).unlink()
            
            transcription = result["text"].strip()
            logger.info(f"✓ Transcription: {transcription}")
            
            return transcription
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    def synthesize_speech(self, text: str) -> bytes:
        """
        Convert text to speech using gTTS
        
        Args:
            text: Text to convert
            
        Returns:
            Audio file bytes (MP3 format)
        """
        if not self.enabled:
            raise RuntimeError("Voice features not enabled")
        
        try:
            logger.info(f"🔊 Synthesizing speech: {text[:50]}...")
            
            # Generate speech with gTTS
            tts = gTTS(text=text, lang=config.TTS_LANGUAGE, slow=False)
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            audio_data = audio_buffer.read()
            logger.info(f"✓ Generated audio: {len(audio_data)} bytes")
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            raise
    
    def process_voice_query(self, audio_data: bytes) -> dict:
        """
        Process voice query: audio → text transcription
        
        Args:
            audio_data: Input audio bytes
            
        Returns:
            Dictionary with transcription
        """
        try:
            # STT: Convert audio to text
            transcription = self.transcribe_audio(audio_data)
            
            return {
                "status": "success",
                "transcription": transcription
            }
            
        except Exception as e:
            logger.error(f"Error processing voice query: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
