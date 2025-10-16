"""
Server Configuration
Centralized configuration for CampusConvo server
"""

import os
from pathlib import Path

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# ChromaDB settings
CHROMA_PATH = os.getenv("CHROMA_PATH", "embeddings/chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "college_documents")

# Embedding model
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# RAG settings
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", 5))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.3))  # Lowered from 0.5 to 0.3

# LLM settings (placeholder for TASK4)
LLM_MODEL = os.getenv("LLM_MODEL", "tinyllama")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.7))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 512))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
