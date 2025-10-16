# Changelog

All notable changes to CampusConvo will be documented in this file.

## [Latest] - 2025-10-16

### Added
- Voice interaction support (Speech-to-Text with Whisper, Text-to-Speech with gTTS)
- Multi-platform audio recording (ALSA, FFmpeg, SoX, Termux)
- Google Gemini 2.0 Flash integration for AI responses
- Configurable TTS accents (US, UK, Indian, Australian English)
- Unified client with text/voice mode selection
- Automatic audio system detection

### Changed
- Improved prompt engineering for more focused responses
- Centralized network configuration in server/config.py
- Enhanced error handling and logging
- Optimized RAG pipeline for better context retrieval

### Fixed
- MP3 audio playback using ffplay instead of aplay
- Voice API request format (field name mismatch)
- Over-verbose AI responses with stricter prompts
- WebSocket timeout compatibility for Termux

### Removed
- Redundant documentation files
- TinyLlama local model (replaced with Gemini)
- Development task files
- Emoji characters from codebase

## Technical Details

### Architecture
- RAG pipeline with ChromaDB (760 embeddings, 180 documents)
- Google Gemini API for response generation
- FastAPI WebSocket server for real-time communication
- Whisper base model for speech recognition
- gTTS for text-to-speech synthesis

### Performance
- Average query time: <2 seconds
- Voice transcription: 3-5 seconds
- Embedding model: ~90MB
- Whisper model: ~150MB

## Migration Notes

If upgrading from an earlier version:
1. Update .env with new TTS_ACCENT configuration
2. Restart server to apply prompt changes
3. Test audio system with: python test_audio.py
