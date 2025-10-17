"""
Voice Pipeline for CampusConvo
Handles Speech-to-Text (STT) and Text-to-Speech (TTS)
Server-side processing for minimal client load
"""

import io
import logging
import tempfile
from pathlib import Path

import whisper
from gtts import gTTS

from server import config

logger = logging.getLogger(__name__)

# Domain-specific word corrections for Whisper transcription
WORD_CORRECTIONS = {
    # Sunway variations
    "some way": "sunway",
    "summary": "sunway",
    "someday": "sunway",
    "sun way": "sunway",
    "son way": "sunway",
    "summit": "sunway",
    # Other common college terms
    "petaling jaya": "petaling jaya",
    "petaling java": "petaling jaya",
    "bandar sunway": "bandar sunway",
    "bandar summary": "bandar sunway",
    # Degree/program names (add more as needed)
    "i t": "IT",
    "business administration": "business administration",
}


def correct_transcription(text: str) -> str:
    """
    Apply domain-specific corrections to transcription

    Args:
        text: Raw transcription from Whisper

    Returns:
        Corrected text
    """
    corrected = text
    text_lower = text.lower()

    for wrong, correct in WORD_CORRECTIONS.items():
        # Case-insensitive replacement
        if wrong.lower() in text_lower:
            # Replace while preserving original case pattern
            import re

            pattern = re.compile(re.escape(wrong), re.IGNORECASE)
            corrected = pattern.sub(correct, corrected)

    return corrected


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

        # Detect device (GPU vs CPU)
        import torch

        if config.USE_GPU and torch.cuda.is_available():
            self.device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"🚀 GPU detected: {gpu_name}")
            logger.info(f"   CUDA version: {torch.version.cuda}")
            logger.info("   Using GPU for Whisper acceleration")
        else:
            self.device = "cpu"
            if config.USE_GPU:
                logger.warning("⚠️  GPU requested but not available, falling back to CPU")
            else:
                logger.info("Using CPU for Whisper (GPU disabled in config)")

        # Load Whisper model for STT
        try:
            logger.info(f"Loading Whisper model: {config.STT_MODEL} on {self.device}")
            self.whisper_model = whisper.load_model(config.STT_MODEL, device=self.device)
            logger.info(f"[OK] Whisper STT initialized successfully on {self.device.upper()}")
        except Exception as e:
            logger.error(f"Failed to load Whisper: {e}")
            self.enabled = False
            return

        logger.info("[OK] Voice Pipeline initialization complete")

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

            logger.info(f"  Saved audio to: {temp_audio_path}")
            logger.info(f"  Audio size: {len(audio_data)} bytes")

            # Transcribe with Whisper
            logger.info(f"  Transcribing audio ({len(audio_data)} bytes)...")
            # Use FP16 on GPU for faster inference, FP32 on CPU
            fp16 = self.device == "cuda"
            result = self.whisper_model.transcribe(
                temp_audio_path, language=config.STT_LANGUAGE, fp16=fp16
            )

            # Clean up temporary file
            Path(temp_audio_path).unlink()

            transcription = result["text"].strip()

            # Debug: Log full result
            logger.info(f"  Whisper raw result: {result}")
            logger.info(f"  Detected language: {result.get('language', 'unknown')}")

            if not transcription:
                logger.warning(f"  Empty transcription! Full result: {result}")
                return transcription

            logger.info(f"  Raw transcription: '{transcription}'")

            # Apply domain-specific corrections
            corrected_transcription = correct_transcription(transcription)

            if corrected_transcription != transcription:
                logger.info(f"  ✓ Corrected: '{corrected_transcription}'")
            else:
                logger.info("  (no corrections needed)")

            return corrected_transcription

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
            logger.info(f" Synthesizing speech: {text[:50]}...")

            # Generate speech with gTTS
            # Use accent from config (com = US, co.in = Indian, co.uk = British)
            tts = gTTS(text=text, lang=config.TTS_LANGUAGE, slow=False, tld=config.TTS_ACCENT)

            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            audio_data = audio_buffer.read()
            logger.info(f"[OK] Generated audio: {len(audio_data)} bytes")

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

            return {"status": "success", "transcription": transcription}

        except Exception as e:
            logger.error(f"Error processing voice query: {e}")
            return {"status": "error", "error": str(e)}
