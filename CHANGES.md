# Changelog

All notable changes to CampusConvo will be documented in this file.

## [2.0.0] - 2025-10-16

### BREAKING CHANGES
- **Complete transformation to voice-only assistant**
- Client now launches directly into wake word listening mode
- Text mode removed - ZYRA is now fully voice-based
- No more mode selection - voice is the only interface

### Added
- **Wake word activation:** "Hello Zyra" triggers conversation
- Continuous listening mode with automatic wake word detection
- Fuzzy wake word matching for transcription accuracy
- Alternative wake word pronunciations (helo zyra, hello zira, hey zyra)
- Query extraction after wake word detection
- 6-second recording window to capture wake word + question
- Automatic error recovery with retry logic
- Enhanced audio system validation on startup
- Comprehensive help messages for missing audio tools

### Changed
- Client is now a dedicated voice assistant, not a general chat client
- Removed text/voice mode selection menu
- Removed test mode and single query mode
- Simplified main() function to launch wake word assistant directly
- Updated all documentation to reflect voice-only design
- README now highlights wake word functionality
- Improved user feedback with clear status messages

### Technical Details

**Wake Word System:**
- Primary wake word: "hello zyra"
- Alternatives for robustness: ["helo zyra", "hello zira", "hello zera", "hey zyra"]
- Case-insensitive matching
- Automatic query extraction after wake word
- Handles wake word + question in single utterance

**Continuous Listening:**
- 6-second recording windows
- Background error recovery (max 3 consecutive errors)
- Graceful handling of empty/no-speech recordings
- Automatic cleanup of temporary audio files

## [1.0.0] - 2025-10-16

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
- Wake word detection with fuzzy matching

### Performance
- Average query time: <2 seconds
- Voice transcription: 3-5 seconds
- Wake word detection: <1 second
- Embedding model: ~90MB
- Whisper model: ~150MB

## Migration Notes

If upgrading from version 1.x:
- **The client is now voice-only** - no text mode available
- Launch with `python client.py` - it will start listening immediately
- Say "Hello Zyra" followed by your question to interact
- Press Ctrl+C to exit
- Ensure audio recording system is properly configured

If upgrading from an earlier version:
1. Update .env with new TTS_ACCENT configuration
2. Restart server to apply prompt changes
3. Test audio system with: python test_audio.py
