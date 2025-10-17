"""
Unified Configuration Loader for CampusConvo
Loads all settings from config.yaml as the single source of truth
"""

from pathlib import Path
from typing import Any, Dict

import yaml


class Config:
    """Unified configuration class"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Load configuration from YAML file

        Args:
            config_path: Path to config.yaml file
        """
        self.config_path = Path(config_path)
        
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please ensure config.yaml exists in the project root."
            )
        
        # Load YAML configuration
        with open(self.config_path, "r") as f:
            self._config: Dict[str, Any] = yaml.safe_load(f)
        
        # Initialize all settings
        self._load_all_settings()
    
    def _load_all_settings(self):
        """Load all configuration settings"""
        # SERVER SETTINGS
        self.HOST = self._config["server"]["host"]
        self.PORT = self._config["server"]["port"]
        self.LOG_LEVEL = self._config["server"]["log_level"]
        self.SERVER_IP = self._config["server"]["server_ip"]
        
        # GEMINI API
        self.GEMINI_API_KEY = self._config["gemini"]["api_key"]
        self.USE_LLM = self._config["gemini"]["use_llm"]
        
        # GPU
        self.USE_GPU = self._config["gpu"]["enabled"]
        
        # SPEECH-TO-TEXT
        self.STT_MODEL = self._config["stt"]["model"]
        self.STT_LANGUAGE = self._config["stt"]["language"]
        
        # TEXT-TO-SPEECH
        self.TTS_ENGINE = self._config["tts"]["engine"]
        self.TTS_LANGUAGE = self._config["tts"]["language"]
        self.TTS_ACCENT = self._config["tts"]["gtts"]["accent"]
        self.TTS_EDGE_VOICE = self._config["tts"]["edge"]["voice"]
        
        # RAG SETTINGS
        self.CHROMA_PATH = self._config["rag"]["chroma"]["path"]
        self.COLLECTION_NAME = self._config["rag"]["chroma"]["collection_name"]
        self.EMBEDDING_MODEL = self._config["rag"]["embedding_model"]
        self.DEFAULT_TOP_K = self._config["rag"]["default_top_k"]
        self.SIMILARITY_THRESHOLD = self._config["rag"]["similarity_threshold"]
        
        # AUDIO SETTINGS
        self.AUDIO_SAMPLE_RATE = self._config["audio"]["sample_rate"]
        self.VAD_AGGRESSIVENESS = self._config["audio"]["vad"]["aggressiveness"]
        self.SILENCE_THRESHOLD = self._config["audio"]["recording"]["silence_threshold"]
        self.MAX_RECORDING_DURATION = self._config["audio"]["recording"]["max_duration"]
        self.MIN_CONSECUTIVE_SPEECH = self._config["audio"]["recording"]["min_consecutive_speech"]
        
        # CLIENT AUDIO
        self.CLIENT_RATE = self._config["audio"]["client"]["rate"]
        self.CLIENT_CHUNK = self._config["audio"]["client"]["chunk"]
        self.CLIENT_CHANNELS = self._config["audio"]["client"]["channels"]
        self.CLIENT_FRAME_DURATION_MS = 20  # Fixed at 20ms for webrtcvad
        
        # WAKE WORD
        self.WAKE_WORD = self._config["wake_word"]["phrase"]
        self.WAKE_WORD_ALTERNATIVES = self._config["wake_word"]["alternatives"]
        self.EXIT_COMMANDS = self._config["wake_word"]["exit_commands"]
        self.PORCUPINE_ACCESS_KEY = self._config["wake_word"]["porcupine"]["access_key"]
        self.PORCUPINE_KEYWORDS = self._config["wake_word"]["porcupine"]["keywords"]
        
        # UI SETTINGS
        self.GREETING_MESSAGE = self._config["ui"]["greeting_message"]
        self.GOODBYE_MESSAGE = self._config["ui"]["goodbye_message"]
        self.ASSISTANT_NAME = self._config["ui"]["assistant_name"]
        self.MAX_CONSECUTIVE_ERRORS = self._config["ui"]["max_consecutive_errors"]
        self.REQUEST_TIMEOUT = self._config["ui"]["request_timeout"]
        
        # TEMPORARY FILES
        self.TEMP_AUDIO_DIR = self._config["temp"]["audio_dir"]
        self.TEMP_QUERY_FILE = self._config["temp"]["query_file"]
        self.TEMP_GREETING_FILE = self._config["temp"]["greeting_file"]
        self.TEMP_GOODBYE_FILE = self._config["temp"]["goodbye_file"]
        self.TEMP_RESPONSE_FILE = self._config["temp"]["response_file"]
        
        # DERIVED SETTINGS
        self.WEBSOCKET_URL = f"ws://{self.SERVER_IP}:{self.PORT}/ws"
        self.HTTP_SERVER_URL = f"http://{self.SERVER_IP}:{self.PORT}"
        self.ENABLE_VOICE = True  # Always enabled in this version
        
        # Wake word detection settings (derived)
        self.WAKE_WORD_SILENCE_THRESHOLD = 0.8
        self.WAKE_WORD_MAX_DURATION = 5
        self.QUERY_SILENCE_THRESHOLD = 1.0
        self.QUERY_MAX_DURATION = 10
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key

        Args:
            key: Configuration key (e.g., 'server.host')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def __repr__(self) -> str:
        """String representation"""
        return f"Config(config_path='{self.config_path}')"


# Create global config instance
config = Config()

# For backwards compatibility, expose all settings at module level
HOST = config.HOST
PORT = config.PORT
LOG_LEVEL = config.LOG_LEVEL
SERVER_IP = config.SERVER_IP

GEMINI_API_KEY = config.GEMINI_API_KEY
USE_LLM = config.USE_LLM

USE_GPU = config.USE_GPU

STT_MODEL = config.STT_MODEL
STT_LANGUAGE = config.STT_LANGUAGE

TTS_ENGINE = config.TTS_ENGINE
TTS_LANGUAGE = config.TTS_LANGUAGE
TTS_ACCENT = config.TTS_ACCENT
TTS_EDGE_VOICE = config.TTS_EDGE_VOICE

CHROMA_PATH = config.CHROMA_PATH
COLLECTION_NAME = config.COLLECTION_NAME
EMBEDDING_MODEL = config.EMBEDDING_MODEL
DEFAULT_TOP_K = config.DEFAULT_TOP_K
SIMILARITY_THRESHOLD = config.SIMILARITY_THRESHOLD

AUDIO_SAMPLE_RATE = config.AUDIO_SAMPLE_RATE
VAD_AGGRESSIVENESS = config.VAD_AGGRESSIVENESS
SILENCE_THRESHOLD = config.SILENCE_THRESHOLD
MAX_RECORDING_DURATION = config.MAX_RECORDING_DURATION
MIN_CONSECUTIVE_SPEECH = config.MIN_CONSECUTIVE_SPEECH

CLIENT_RATE = config.CLIENT_RATE
CLIENT_CHUNK = config.CLIENT_CHUNK
CLIENT_CHANNELS = config.CLIENT_CHANNELS
CLIENT_FRAME_DURATION_MS = config.CLIENT_FRAME_DURATION_MS

WAKE_WORD = config.WAKE_WORD
WAKE_WORD_ALTERNATIVES = config.WAKE_WORD_ALTERNATIVES
EXIT_COMMANDS = config.EXIT_COMMANDS
PORCUPINE_ACCESS_KEY = config.PORCUPINE_ACCESS_KEY
PORCUPINE_KEYWORDS = config.PORCUPINE_KEYWORDS

GREETING_MESSAGE = config.GREETING_MESSAGE
GOODBYE_MESSAGE = config.GOODBYE_MESSAGE
ASSISTANT_NAME = config.ASSISTANT_NAME
MAX_CONSECUTIVE_ERRORS = config.MAX_CONSECUTIVE_ERRORS
REQUEST_TIMEOUT = config.REQUEST_TIMEOUT

TEMP_AUDIO_DIR = config.TEMP_AUDIO_DIR
TEMP_QUERY_FILE = config.TEMP_QUERY_FILE
TEMP_GREETING_FILE = config.TEMP_GREETING_FILE
TEMP_GOODBYE_FILE = config.TEMP_GOODBYE_FILE
TEMP_RESPONSE_FILE = config.TEMP_RESPONSE_FILE

WEBSOCKET_URL = config.WEBSOCKET_URL
HTTP_SERVER_URL = config.HTTP_SERVER_URL
ENABLE_VOICE = config.ENABLE_VOICE

WAKE_WORD_SILENCE_THRESHOLD = config.WAKE_WORD_SILENCE_THRESHOLD
WAKE_WORD_MAX_DURATION = config.WAKE_WORD_MAX_DURATION
QUERY_SILENCE_THRESHOLD = config.QUERY_SILENCE_THRESHOLD
QUERY_MAX_DURATION = config.QUERY_MAX_DURATION

# For backward compatibility with old code
LLM_MODEL = "tinyllama"
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 512
