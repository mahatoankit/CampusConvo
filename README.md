# CampusConvo

**Description:**
CampusConvo is an **offline, real-time, voice-based college assistant**. It allows students and faculty to interact with college resources via **speech-to-speech**, providing instant, accurate answers to queries about courses, lectures, exams, and campus information.

The system uses a **RAG-based architecture**: a **vector database** stores course materials, and an **LLM** generates responses based on retrieved context. It supports **interruptible responses (barge-in)** and **real-time streaming**, giving a human-like conversational experience.

---

## **Table of Contents**

1. [Features](#features)
2. [Architecture Overview](#architecture-overview)
3. [Components & Technologies](#components--technologies)
4. [Setup Instructions](#setup-instructions)
5. [Development vs Production Models](#development-vs-production-models)
6. [Client Options](#client-options)
7. [Usage](#usage)
8. [Data Preparation](#data-preparation)
9. [License](#license)

---

## **Features**

* Fully offline operation (LAN-based)
* Real-time voice interaction (streaming STT → LLM → TTS)
* Interruptible responses (barge-in support)
* RAG-based retrieval for accurate answers
* Modular architecture: easily swap LLMs or vector DBs
* Supports lightweight testing on laptop or phone

---

## **Architecture Overview**

```
           [Client Device (Pi / Mobile)]
 ┌──────────────────────────────────┐
 │ Mic → STT (Whisper.cpp / Vosk)  │
 │ → WebSocket → FastAPI Server     │
 │ ← streaming text ←               │
 │ TTS (Piper or Platform TTS)     │
 └──────────────────────────────────┘
                 │
        LAN (WebSocket)
                 │
        [GPU Server / Inference]
 ┌──────────────────────────────────────┐
 │ FastAPI + RAG                        │
 │ ├─ ChromaDB (vector store)           │
 │ ├─ Embeddings (MiniLM / MPNet)       │
 │ ├─ LLM (Ollama / Llama.cpp)          │
 │ └─ Streaming token output            │
 └──────────────────────────────────────┘
```

---

## **Components & Technologies**

| Function                     | Tool / Model / Notes                                                                     |
| ---------------------------- | ---------------------------------------------------------------------------------------- |
| **LLM (Dev)**                | TinyLLaMA 1.1B (llama.cpp) — lightweight for laptop testing                              |
| **LLM (Production)**         | Mistral 7B or Phi-3 7B (Ollama / llama.cpp) — full-quality GPU inference                 |
| **Vector Database**          | ChromaDB (local) — stores course documents, lecture notes, etc.                          |
| **Embeddings**               | `sentence-transformers/all-MiniLM-L6-v2` (light) or `all-mpnet-base-v2` (higher quality) |
| **STT**                      | Whisper.cpp (streaming) / Vosk for offline transcription                                 |
| **TTS**                      | Piper TTS or mobile platform-native TTS                                                  |
| **Communication**            | WebSocket / FastAPI — bidirectional streaming between client and server                  |
| **Wake Word (Optional)**     | Porcupine — local wake-word detection                                                    |
| **Voice Activity Detection** | WebRTC VAD or energy-based threshold for barge-in                                        |

---

## **Setup Instructions**

### **GPU Server**

1. Install Python 3.10+
2. Install LLM framework (Ollama or llama.cpp)
3. Install ChromaDB and sentence-transformers
4. Setup FastAPI server with WebSocket streaming endpoints
5. Load your chosen LLM model (dev or prod)
6. Precompute embeddings for documents and store in ChromaDB

### **Client Device (Raspberry Pi / Phone / Termux)**

1. Install Python 3.10+ (or Termux Python environment)
2. Install STT library (Whisper.cpp or Vosk)
3. Install TTS (Piper or platform-native TTS)
4. Setup WebSocket client to send STT audio/text and receive streaming LLM tokens

### **Networking**

* Ensure client and GPU server are on the **same LAN**
* Configure FastAPI to accept connections from the client
* Use WebSocket streaming to allow real-time query/response

---

## **Development vs Production Models**

| Stage           | Model / Framework          | Notes                                                                     |
| --------------- | -------------------------- | ------------------------------------------------------------------------- |
| **Development** | TinyLLaMA 1.1B (llama.cpp) | Fast, low VRAM, test pipeline locally                                     |
| **Production**  | Mistral 7B / Phi-3 7B      | High-quality answers, GPU inference, use quantized weights for efficiency |

**Tip:** Keep the model interface abstract so you can **swap models without touching the rest of the code**.

---

## **Client Options**

| Option                                 | Description                                              | Best Use                                                  |
| -------------------------------------- | -------------------------------------------------------- | --------------------------------------------------------- |
| **Termux + Python**                    | Run client scripts on Android CLI, minimal setup         | Rapid testing, debugging                                  |
| **Web-based Interface**                | Mobile-friendly web page using MediaRecorder + WebSocket | Quick cross-device demos, testing without installing apps |
| **Native Android App (Kivy / Native)** | Full-featured app with mic + TTS                         | Production-ready, smooth audio playback, polished UI      |

---

## **Usage**

1. Start GPU server:

```bash
python server.py
```

2. Start client (Pi, Termux, or Web interface):

```bash
python client.py
```

3. Speak into the microphone.
4. Assistant responds via TTS in real time.
5. Interrupting speech triggers barge-in — current response stops and your new query is processed immediately.

---

## **Data Preparation**

1. Collect course materials: lecture notes, PDFs, syllabi, FAQs
2. Clean and preprocess text: remove headers, footers, OCR errors
3. Chunk documents: 200–500 tokens per chunk
4. Save as `.jsonl` for ingestion into ChromaDB:

```json
{"id": "lecture1_chunk1", "text": "Newton's first law ...", "metadata": {"course": "Physics101", "lecture": 1}}
```

5. Generate embeddings using `sentence-transformers` and store in vector DB

> **Tip:** High-quality, clean, and well-chunked data is the single most important factor in accurate RAG responses.

---

## **License**

[MIT License] - free to use and modify for educational purposes

---