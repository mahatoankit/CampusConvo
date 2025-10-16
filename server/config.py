"""
Server Configuration
Centralized configuration for CampusConvo server
"""

import os
from pathlib import Path

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

# STT (Speech-to-Text) settings
STT_MODEL = os.getenv("STT_MODEL", "base")  # Options: tiny, base, small, medium, large
STT_LANGUAGE = os.getenv("STT_LANGUAGE", "en")

# TTS (Text-to-Speech) settings
TTS_ENGINE = os.getenv("TTS_ENGINE", "gtts")  # Options: gtts, pyttsx3
TTS_LANGUAGE = os.getenv("TTS_LANGUAGE", "en")

# Audio settings
AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", 16000))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
