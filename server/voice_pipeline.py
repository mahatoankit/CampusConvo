"""
Voice Pipeline for CampusConvo
Handles Speech-to-Text (STT) and Text-to-Speech (TTS)
Server-side processing for minimal client load
"""

import io
import logging
import tempfile
from pathlib import Path

import torch
import whisper
from gtts import gTTS

from server import config

logger = logging.getLogger(__name__)

# Import TTS engines based on availability
TTS_ENGINES_AVAILABLE = {"gtts": True}

try:
    import edge_tts

    TTS_ENGINES_AVAILABLE["edge-tts"] = True
except ImportError:
    TTS_ENGINES_AVAILABLE["edge-tts"] = False

try:
    import piper  # noqa: F401

    TTS_ENGINES_AVAILABLE["piper"] = True
except ImportError:
    TTS_ENGINES_AVAILABLE["piper"] = False

try:
    from TTS.api import TTS as CoquiTTS

    TTS_ENGINES_AVAILABLE["coqui"] = True
except ImportError:
    TTS_ENGINES_AVAILABLE["coqui"] = False

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

        # Initialize TTS engine
        self.tts_engine = config.TTS_ENGINE.lower()
        self.tts_model = None

        if self.tts_engine not in TTS_ENGINES_AVAILABLE:
            logger.warning(f"⚠️  Unknown TTS engine '{self.tts_engine}', falling back to 'gtts'")
            self.tts_engine = "gtts"

        if not TTS_ENGINES_AVAILABLE.get(self.tts_engine, False):
            logger.warning(
                f"⚠️  TTS engine '{self.tts_engine}' not installed, falling back to 'gtts'"
            )
            self.tts_engine = "gtts"

        logger.info(f"Initializing TTS engine: {self.tts_engine}")

        # Load TTS model based on engine
        try:
            if self.tts_engine == "piper":
                # Piper requires model file download
                logger.info(f"  Loading Piper model: {config.TTS_PIPER_MODEL}")
                # Note: Piper models need to be pre-downloaded
                logger.info("  [OK] Piper TTS ready (neural voice)")

            elif self.tts_engine == "coqui":
                logger.info(f"  Loading Coqui model: {config.TTS_COQUI_MODEL}")
                self.tts_model = CoquiTTS(config.TTS_COQUI_MODEL, gpu=self.device == "cuda")
                logger.info("  [OK] Coqui TTS ready (neural voice)")

            elif self.tts_engine == "edge-tts":
                logger.info(f"  Voice: {config.TTS_EDGE_VOICE}")
                logger.info("  [OK] Edge TTS ready (Microsoft neural voice)")

            else:  # gtts
                logger.info(f"  Accent: {config.TTS_ACCENT}")
                logger.info("  [OK] Google TTS ready (basic quality)")

        except Exception as e:
            logger.warning(f"Failed to load {self.tts_engine} TTS: {e}, falling back to gtts")
            self.tts_engine = "gtts"

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
        Convert text to speech using configured TTS engine

        Args:
            text: Text to convert

        Returns:
            Audio file bytes (MP3 or WAV format depending on engine)
        """
        if not self.enabled:
            raise RuntimeError("Voice features not enabled")

        try:
            logger.info(f"🔊 Synthesizing speech ({self.tts_engine}): {text[:50]}...")

            audio_data = None

            if self.tts_engine == "edge-tts":
                # Microsoft Edge TTS (online, very natural)
                import asyncio

                async def _generate_edge_tts():
                    communicate = edge_tts.Communicate(text, config.TTS_EDGE_VOICE)
                    audio_buffer = io.BytesIO()
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            audio_buffer.write(chunk["data"])
                    return audio_buffer.getvalue()

                audio_data = asyncio.run(_generate_edge_tts())

            elif self.tts_engine == "piper":
                # Piper TTS (offline, fast, neural)
                # Note: Requires piper-tts and model files
                # For now, fallback to gTTS
                logger.warning("Piper TTS not fully implemented, falling back to gTTS")
                self.tts_engine = "gtts"
                return self.synthesize_speech(text)  # Recursive call with gtts

            elif self.tts_engine == "coqui":
                # Coqui TTS (offline, high quality neural)
                if self.tts_model:
                    # Generate to temporary file
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                        temp_path = tmp.name

                    self.tts_model.tts_to_file(text=text, file_path=temp_path)

                    # Read file
                    with open(temp_path, "rb") as f:
                        audio_data = f.read()

                    # Clean up
                    Path(temp_path).unlink()
                else:
                    raise RuntimeError("Coqui TTS model not loaded")

            else:  # gtts (default)
                # Google TTS (online, basic quality)
                tts = gTTS(text=text, lang=config.TTS_LANGUAGE, slow=False, tld=config.TTS_ACCENT)

                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                audio_data = audio_buffer.read()

            if audio_data:
                logger.info(f"[OK] Generated audio: {len(audio_data)} bytes")
                return audio_data
            else:
                raise RuntimeError("Failed to generate audio")

        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            # Fallback to gtts if other engines fail
            if self.tts_engine != "gtts":
                logger.warning("Falling back to gtts due to error")
                self.tts_engine = "gtts"
                return self.synthesize_speech(text)
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
