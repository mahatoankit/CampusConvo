# CampusConvo - ZYRA Voice Assistant

An AI-powered voice assistant for Sunway College, Kathmandu. Built with RAG (Retrieval-Augmented Generation) architecture using ChromaDB for vector storage and Google Gemini for response generation. Features wake word activation with "Hello Zyra".

## Features

- **Wake Word Activation** - Say "Hello Zyra" to start conversations
- **Voice-only Interface** - Completely hands-free interaction
- **Speech-to-text** - Powered by OpenAI Whisper
- **Text-to-speech** - Natural voice responses using Edge TTS
- **RAG pipeline** - Context-aware responses using vector similarity search
- **Multi-platform support** - Works on Linux desktop and WSL

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
- Audio system with microphone (ALSA/PulseAudio)

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

4. Configure settings in `config.yaml`:
   - Add your GEMINI_API_KEY
   - Adjust TTS engine (edge-tts or gtts)
   - Set STT model size (base, small, medium)

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

All configuration is managed through `config.yaml`. Key settings:

```yaml
# Server
server:
  host: "0.0.0.0"
  port: 8000
  server_ip: "192.168.x.x"  # Your laptop's IP

# Text-to-Speech
tts:
  engine: "edge-tts"  # or "gtts"
  voice: "en-US-AriaNeural"

# Speech-to-Text
stt:
  model: "medium"  # tiny, base, small, medium, large
  language: "en"

# Google Gemini API
gemini:
  api_key: "your-api-key-here"
  use_llm: true
```

## Usage

### Voice Assistant with Wake Word

```bash
python src/client.py
```

**How it works:**
1. Say "Hello Zyra" followed by your question
2. ZYRA responds with voice output
3. Press Ctrl+C to exit

**Tips:**
- Speak clearly after "Hello Zyra"
- Wait for the beep sounds (recording start/stop)
- The system auto-detects when you stop speaking

### Audio System Requirements

**Linux:**
```bash
sudo apt install alsa-utils ffmpeg portaudio19-dev
```

## Project Structure

```
CampusConvo/
├── src/
│   ├── client.py          # Voice assistant with wake word
│   └── client_simple.py   # Simple client without wake word
├── server/
│   ├── api_server.py      # FastAPI server
│   ├── rag_pipeline.py    # RAG implementation
│   └── voice_pipeline.py  # Voice processing (Whisper + TTS)
├── config.yaml            # Unified configuration
├── unified_config.py      # Configuration loader
├── run_server.py          # Server entry point
├── run_embeddings.py      # Embedding generation script
├── data/                  # Data files
└── embeddings/            # ChromaDB vector store
```

## Technology Stack

- **Backend:** FastAPI, Python 3.10+
- **Vector DB:** ChromaDB
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **LLM:** Google Gemini 2.0 Flash
- **Speech-to-Text:** OpenAI Whisper
- **Text-to-Speech:** Edge TTS / gTTS
- **Wake Word:** Custom detection with fuzzy matching
- **Audio:** PyAudio, webrtcvad

## Documentation

See `config.yaml` for all available configuration options.

## License

MIT License

## Contact

- **Repository:** https://github.com/mahatoankit/CampusConvo
- **Issues:** https://github.com/mahatoankit/CampusConvo/issues
