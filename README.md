# CampusConvo (Zyra) - Offline Voice-Based College Assistant

**Description**
CampusConvo is an **offline, real-time, voice-based college assistant** for Sunway College. It allows students and faculty to interact with college resources via **speech-to-speech**, providing instant, accurate answers to queries about courses, lectures, exams, and campus information.

The system uses a **Retrieval-Augmented Generation (RAG) architecture**, where a **vector database stores course materials**, and an **LLM generates responses based on retrieved context**. The assistant is equipped with **wake word detection** and supports **interruptible responses** for a natural, conversational experience.

The project features a **mascot named Zyra**, representing a smart, approachable AI companion tailored for Sunway College.

---

## Table of Contents

1. [Features](#features)
2. [Architecture Overview](#architecture-overview)
3. [Components and Technologies](#components-and-technologies)
4. [Setup Instructions](#setup-instructions)
5. [Development vs Production Models](#development-vs-production-models)
6. [Client Options](#client-options)
7. [Wake Word Integration](#wake-word-integration)
8. [Usage](#usage)
9. [Data Preparation](#data-preparation)
10. [License](#license)

---

## Features

* Fully offline operation with LAN-based client-server communication
* Real-time voice interaction (streaming STT → LLM → TTS)
* Interruptible responses (barge-in support)
* RAG-based retrieval for accurate, context-aware answers
* Modular architecture: swap LLMs or vector DBs easily
* Supports lightweight testing on laptops, Termux, or mobile devices
* Wake word detection with local processing for efficiency and privacy

---

## Architecture Overview

```
[Client Device (Raspberry Pi / Mobile / Termux)]
 ┌────────────────────────────────────────────┐
 │ Mic → Wake Word Detector → STT (Whisper)   │
 │ → WebSocket → FastAPI Server               │
 │ ← streaming text/audio ←                   │
 │ TTS (Piper or Platform TTS)                │
 └────────────────────────────────────────────┘
                  │
           LAN / Local Network
                  │
[GPU Server / Inference]
 ┌────────────────────────────────────────────┐
 │ FastAPI + RAG Pipeline                     │
 │ ├─ ChromaDB (Vector Store)                │
 │ ├─ Embeddings (MiniLM / MPNet)            │
 │ ├─ LLM (TinyLLaMA / Mistral / Phi-3)     │
 │ └─ Streaming Token Output                 │
 └────────────────────────────────────────────┘
```

---

## Components and Technologies

| Function                 | Tool / Model / Notes                                                         |
| ------------------------ | ---------------------------------------------------------------------------- |
| LLM (Development)        | TinyLLaMA 1.1B (llama.cpp)                                                   |
| LLM (Production)         | Mistral 7B or Phi-3 7B (GPU inference, quantized weights)                    |
| Vector Database          | ChromaDB (local)                                                             |
| Embeddings               | `sentence-transformers/all-MiniLM-L6-v2` (dev) or `all-mpnet-base-v2` (prod) |
| STT                      | Whisper.cpp / Vosk (offline transcription)                                   |
| TTS                      | Piper TTS or platform-native TTS                                             |
| Communication            | WebSocket / FastAPI streaming                                                |
| Wake Word Detection      | Porcupine (offline)                                                          |
| Voice Activity Detection | WebRTC VAD or energy threshold                                               |

---

## Setup Instructions

### GPU Server

1. Install Python 3.10+
2. Install LLM framework (Ollama or llama.cpp)
3. Install ChromaDB and sentence-transformers
4. Setup FastAPI server with WebSocket streaming endpoints
5. Load your chosen LLM model (dev or prod)
6. Precompute embeddings for documents and store in ChromaDB

### Client Device (Raspberry Pi / Mobile / Termux)

1. Install Python 3.10+ or Termux environment
2. Install STT library (Whisper.cpp / Vosk)
3. Install TTS library (Piper or platform-native TTS)
4. Setup WebSocket client to stream audio/text to server and receive responses

### Networking

* Ensure client and GPU server are on the **same LAN**
* Configure FastAPI to accept client connections
* Use **WebSocket streaming** for low-latency query/response

---

## Development vs Production Models

| Stage       | Model / Framework     | Notes                                                         |
| ----------- | --------------------- | ------------------------------------------------------------- |
| Development | TinyLLaMA 1.1B        | Fast, low VRAM, ideal for testing pipeline locally            |
| Production  | Mistral 7B / Phi-3 7B | High-quality answers, GPU inference, quantized for efficiency |

---

## Client Options

| Option              | Description                                                 | Use Case                              |
| ------------------- | ----------------------------------------------------------- | ------------------------------------- |
| Termux + Python     | Run client scripts directly on Android CLI                  | Rapid testing and debugging           |
| Web-based Interface | Mobile-friendly web page with MediaRecorder + WebSocket     | Quick demos, cross-device testing     |
| Native Android App  | Kivy or Android Studio app with full audio capture/playback | Production-ready, polished experience |

---

## Wake Word Integration

* **Wake word:** “Zyra”
* **Function:** Activates STT pipeline only when detected, reducing CPU load and preserving privacy
* **Implementation Flow:**

```
Audio Input → Wake Word Detector → STT → GPU Server / RAG → LLM → TTS → Speaker Output
```

* **Key Benefits:**

  * Efficient CPU usage (STT runs only after wake word)
  * Privacy-friendly (audio processed locally until activated)
  * Supports interruptible responses / barge-in

---

## Usage

1. Start GPU server:

```bash
python server.py
```

2. Start client (Pi, Termux, or mobile/web interface):

```bash
python client.py
```

3. Say the wake word: “Zyra”
4. Speak your query after wake word detection
5. Assistant responds via TTS in real time
6. Interrupting speech triggers barge-in and immediate response to new query

---

## Data Preparation

1. Collect course materials: lecture notes, PDFs, syllabi, FAQs
2. Clean and preprocess text (remove headers, footers, OCR errors)
3. Chunk documents (200–500 tokens per chunk)
4. Save as `.jsonl` for ingestion into ChromaDB:

```json
{"id": "lecture1_chunk1", "text": "Newton's first law ...", "metadata": {"course": "Physics101", "lecture": 1}}
```

5. Generate embeddings with `sentence-transformers` and store in vector database

**Note:** High-quality, clean, and well-chunked data is the most critical factor for accurate RAG responses.

---

## License

[MIT License] – free for educational and research purposes

---