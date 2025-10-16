# CampusConvo

An AI-powered conversational assistant for Sunway College, Kathmandu. Built with RAG (Retrieval-Augmented Generation) architecture using ChromaDB for vector storage and Google Gemini for response generation.

## Features

- **Text-based chat interface** - WebSocket-based real-time communication
- **Voice interaction** - Speech-to-text (Whisper) and text-to-speech (gTTS)
- **RAG pipeline** - Context-aware responses using vector similarity search
- **Multi-platform support** - Works on Linux desktop, Termux (Android), and WSL
- **Offline-first design** - Core functionality works without internet (except LLM generation)

## Architecture

```
Client (WebSocket/HTTP) → Server (FastAPI)
                           ├── RAG Pipeline (ChromaDB + Gemini)
                           └── Voice Pipeline (Whisper + gTTS)
```

## Quick Start

### Prerequisites

- Python 3.10+
- Virtual environment (recommended)
- Google Gemini API key (free tier available)

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

7. Run the client:
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

## Usage

### Text Mode

```bash
python client.py
# Select: t (text mode)
# Type your questions about Sunway College
```

### Voice Mode

```bash
python client.py
# Select: v (voice mode)
# Speak your questions (5-second recording)
```

## Project Structure

```
CampusConvo/
├── client.py              # Client application
├── run_server.py          # Server entry point
├── run_embeddings.py      # Embedding generation script
├── test_audio.py          # Audio system test utility
├── server/
│   ├── api_server.py      # FastAPI server
│   ├── rag_pipeline.py    # RAG implementation
│   ├── voice_pipeline.py  # Voice processing
│   └── config.py          # Configuration
├── data/
│   ├── raw/               # Raw data files
│   └── processed/         # Processed data
├── embeddings/            # ChromaDB vector store
├── docs/                  # Documentation
└── requirements.txt       # Python dependencies
```

## Technology Stack

- **Backend:** FastAPI, Python 3.10+
- **Vector DB:** ChromaDB
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **LLM:** Google Gemini 2.0 Flash
- **Speech-to-Text:** OpenAI Whisper
- **Text-to-Speech:** gTTS (Google Text-to-Speech)
- **Client:** WebSockets, requests

## Documentation

- `docs/SETUP_GUIDE.md` - Detailed setup instructions
- `docs/PROMPT_ENGINEERING.md` - Customizing AI responses
- `docs/TTS_NATURALNESS_GUIDE.md` - Voice quality improvement

## License

MIT License

## Contact

- **Repository:** https://github.com/mahatoankit/CampusConvo
- **Issues:** https://github.com/mahatoankit/CampusConvo/issues
