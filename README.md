# CampusConvo - ZYRA Voice Assistant

An AI-powered voice assistant for Sunway College, Kathmandu. Built with RAG (Retrieval-Augmented Generation) architecture using ChromaDB for vector storage and Google Gemini for response generation. Features wake word activation with "Hello Zyra".

## Features

- **Wake Word Activation** - Say "Hello Zyra" to start conversations
- **Voice-only Interface** - Completely hands-free interaction
- **Speech-to-text** - Powered by OpenAI Whisper
- **Text-to-speech** - Natural voice responses using gTTS
- **RAG pipeline** - Context-aware responses using vector similarity search
- **Multi-platform support** - Works on Linux desktop, Termux (Android), and WSL
- **Offline-first design** - Core functionality works without internet (except LLM generation)

## Architecture

```
Client (Voice) → Wake Word Detection → Server (FastAPI)
                                         ├── RAG Pipeline (ChromaDB + Gemini)
                                         └── Voice Pipeline (Whisper + gTTS)
```

## Quick Start

### Prerequisites

- Python 3.10+
- Virtual environment (recommended)
- Google Gemini API key (free tier available)
- Audio recording system (ALSA, FFmpeg, or Termux API)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/mahatoankit/CampusConvo.git
cd CampusConvo
```

2. Create and activate virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

5. Generate embeddings:
```bash
python run_embeddings.py
```

6. Start the server:
```bash
python run_server.py
```

7. Run ZYRA voice assistant:
```bash
python client.py
```

## Configuration

### Network Setup

Edit `server/config.py` to update the server IP address:
```python
SERVER_IP = "192.168.x.x"  # Your laptop's IP
```

### Voice Settings

Configure voice features in `.env`:
```bash
ENABLE_VOICE=true
STT_MODEL=base              # Whisper model: tiny, base, small, medium, large
TTS_ENGINE=gtts             # TTS engine: gtts, pyttsx3
TTS_LANGUAGE=en             # Language code
TTS_ACCENT=com              # Accent: com (US), co.uk (UK), co.in (India)
```

### Wake Word Configuration

The wake word "Hello Zyra" is configured in `client.py`. Alternative pronunciations are automatically handled for transcription accuracy.

## Usage

### Voice Assistant with Wake Word

```bash
python client.py
```

**How it works:**
1. The assistant starts listening continuously
2. Say "Hello Zyra" followed by your question
   - Example: *"Hello Zyra, what courses are available?"*
   - Example: *"Hello Zyra, tell me about placements"*
3. ZYRA will respond with voice output
4. Wait for the next wake word to ask another question
5. Press Ctrl+C to exit

**Tips:**
- Speak clearly and include your question right after "Hello Zyra"
- If wake word isn't detected, try speaking louder or closer to the mic
- The system listens for 6 seconds to capture both wake word and question

### Audio System Requirements

**Linux:**
```bash
sudo apt install alsa-utils ffmpeg
```

**Termux (Android):**
1. Install Termux:API package:
```bash
pkg install termux-api
```
2. Install Termux:API app from F-Droid:
   - Download: https://f-droid.org/en/packages/com.termux.api/
   - Grant microphone permission in Android settings
3. See `docs/TERMUX_SETUP.md` for detailed setup

## Project Structure

```
CampusConvo/
├── client.py              # Voice assistant with wake word
├── run_server.py          # Server entry point
├── run_embeddings.py      # Embedding generation script
├── test_audio.py          # Audio system test utility
├── termux_diagnostic.py   # Termux setup diagnostic tool
├── server/
│   ├── api_server.py      # FastAPI server
│   ├── rag_pipeline.py    # RAG implementation
│   ├── voice_pipeline.py  # Voice processing (Whisper + gTTS)
│   └── config.py          # Configuration
├── data/
│   ├── raw/               # Raw data files
│   └── processed/         # Processed data
├── embeddings/            # ChromaDB vector store
├── docs/                  # Documentation
│   └── TERMUX_SETUP.md   # Termux setup guide
└── requirements.txt       # Python dependencies
```

## Technology Stack

- **Backend:** FastAPI, Python 3.10+
- **Vector DB:** ChromaDB
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **LLM:** Google Gemini 2.0 Flash
- **Speech-to-Text:** OpenAI Whisper (base model)
- **Text-to-Speech:** gTTS (Google Text-to-Speech)
- **Wake Word:** Custom detection with fuzzy matching
- **Audio:** ALSA, FFmpeg, SoX, or Termux API

## Documentation

- `docs/SETUP_GUIDE.md` - Detailed setup instructions
- `docs/PROMPT_ENGINEERING.md` - Customizing AI responses
- `docs/TTS_NATURALNESS_GUIDE.md` - Voice quality improvement

## License

MIT License

## Contact

- **Repository:** https://github.com/mahatoankit/CampusConvo
- **Issues:** https://github.com/mahatoankit/CampusConvo/issues
