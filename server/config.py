"""
Server Configuration
Centralized configuration for CampusConvo server
"""

import os

# Network settings - UPDATE THIS WHEN YOU CHANGE NETWORKS
SERVER_IP = os.getenv("SERVER_IP", "192.168.254.135")  # Change this to your laptop's IP

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# WebSocket URL for clients (automatically generated from SERVER_IP)
WEBSOCKET_URL = f"ws://{SERVER_IP}:{PORT}/ws"

# ChromaDB settings
CHROMA_PATH = os.getenv("CHROMA_PATH", "embeddings/chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "college_documents")

# Embedding model
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# RAG settings
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", 5))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.3))

# LLM settings
LLM_MODEL = os.getenv("LLM_MODEL", "tinyllama")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.7))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 512))

# Voice settings
ENABLE_VOICE = os.getenv("ENABLE_VOICE", "true").lower() == "true"

# Device settings (GPU support)
USE_GPU = os.getenv("USE_GPU", "true").lower() == "true"  # Auto-detect and use GPU if available

# STT (Speech-to-Text) settings
# Model sizes: tiny (39MB), base (74MB), small (244MB), medium (769MB), large (1550MB)
# Recommended: 'base' for demos/hackathons (fast + accurate enough)
STT_MODEL = os.getenv("STT_MODEL", "base")  # Options: tiny, base, small, medium, large
STT_LANGUAGE = os.getenv("STT_LANGUAGE", "en")

# TTS (Text-to-Speech) settings
TTS_ENGINE = os.getenv("TTS_ENGINE", "gtts")  # Options: gtts, pyttsx3
TTS_LANGUAGE = os.getenv("TTS_LANGUAGE", "en")
TTS_ACCENT = os.getenv(
    "TTS_ACCENT", "com"
)  # Options: com (US), co.uk (British), co.in (Indian), com.au (Australian)

# Audio settings
AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", 16000))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============================================================================
# CLIENT CONFIGURATION
# ============================================================================

# HTTP Server URL for client
HTTP_SERVER_URL = f"http://{SERVER_IP}:{PORT}"

# Wake word configuration
WAKE_WORD = "hello zyra"
WAKE_WORD_ALTERNATIVES = ["helo zyra", "hello zira", "hello zera", "hey zyra"]
EXIT_COMMANDS = ["bye zyra", "goodbye zyra", "exit"]

# Porcupine wake word settings (OPTIONAL - leave empty to use simple STT-based detection)
# Get free key at https://console.picovoice.ai/
PORCUPINE_ACCESS_KEY = os.getenv("PORCUPINE_ACCESS_KEY", "")
PORCUPINE_KEYWORDS = ["hey google"]  # Built-in keywords: alexa, computer, jarvis, etc.

# Client audio configuration (continuous listening with VAD)
CLIENT_RATE = 16000  # Sample rate in Hz (16kHz for speech)
CLIENT_CHUNK = 320  # 20ms at 16kHz (webrtcvad requires 10, 20, or 30 ms)
CLIENT_CHANNELS = 1  # Mono audio
CLIENT_FRAME_DURATION_MS = 20  # Duration of each frame in milliseconds

# Voice Activity Detection (VAD) settings
VAD_AGGRESSIVENESS = 3  # 0 (least aggressive) to 3 (most aggressive)
SILENCE_THRESHOLD = 2.0  # Seconds of silence before stopping recording
MAX_RECORDING_DURATION = 10  # Maximum recording duration in seconds
MIN_CONSECUTIVE_SPEECH = 0.2  # Seconds of consecutive speech needed to start recording

# Wake word detection settings
WAKE_WORD_SILENCE_THRESHOLD = 0.8  # Shorter silence for wake word
WAKE_WORD_MAX_DURATION = 5  # Max duration for wake word detection

# Query recording settings
QUERY_SILENCE_THRESHOLD = 1.0  # Longer silence for full questions
QUERY_MAX_DURATION = 10  # Max duration for query recording

# Error handling
MAX_CONSECUTIVE_ERRORS = 3  # Exit after this many consecutive errors
REQUEST_TIMEOUT = 30  # HTTP request timeout in seconds

# Display messages
GREETING_MESSAGE = "Hello there, how may I assist you today?"
GOODBYE_MESSAGE = "Goodbye! Have a great day!"

# Temporary files
TEMP_AUDIO_DIR = "/tmp"
TEMP_QUERY_FILE = f"{TEMP_AUDIO_DIR}/campusconvo_query.wav"
TEMP_GREETING_FILE = f"{TEMP_AUDIO_DIR}/campusconvo_greeting.mp3"
TEMP_GOODBYE_FILE = f"{TEMP_AUDIO_DIR}/campusconvo_goodbye.mp3"
TEMP_RESPONSE_FILE = f"{TEMP_AUDIO_DIR}/campusconvo_response.mp3"
