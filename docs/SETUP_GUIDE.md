# CampusConvo Setup and Usage Guide

## Project Status

### Completed Tasks

- TASK1: Project Setup (Complete)
- TASK2: Data Collection and Preprocessing (Complete - using processed.jsonl)
- TASK3: Generate Embeddings and Vector DB (Complete)
- TASK5: FastAPI Server & RAG Pipeline (Complete)

### Pending Tasks

- TASK4: LLM Setup (Pending - placeholder implemented)
- TASK6-9: Wake Word, STT, TTS, Client Implementation (Pending)
- TASK10: End-to-End Testing (Pending)

## Installation

### 1. Prerequisites

- Python 3.10+
- Virtual environment activated

### 2. Install Dependencies

```bash
pip install fastapi uvicorn websockets chromadb sentence-transformers python-dotenv tqdm
```

Or use requirements.txt:

```bash
pip install -r requirements.txt
```

## Usage Instructions

### Step 1: Generate Embeddings

Before starting the server, generate embeddings from the processed data:

```bash
python run_embeddings.py
```

This will:
- Load data from `data/processed/processed.jsonl`
- Generate embeddings using sentence-transformers
- Store embeddings in ChromaDB at `embeddings/`
- Run test queries to verify setup

Expected output:
- Embeddings stored in `embeddings/` directory
- Console output showing progress and test results

### Step 2: Start the Server

Start the FastAPI server with WebSocket support:

```bash
python run_server.py
```

Server will start on `http://localhost:8000`

Available endpoints:
- `GET /` - API information
- `GET /health` - Health check
- `GET /stats` - Database statistics
- `POST /query` - REST API query endpoint
- `WebSocket /ws` - WebSocket endpoint for real-time queries

### Step 3: Test with Client

#### Interactive Mode

Run the client in interactive mode:

```bash
python client_simple.py
```

Type your questions and get responses. Type 'quit' or 'exit' to close.

#### Test Mode

Run pre-defined test queries:

```bash
python client_simple.py test
```

#### Single Query

Send a single query without entering interactive mode:

```bash
python client_simple.py "What courses are offered?"
```

#### Remote Connection (Termux/Other Devices)

Connect from another device on the same network:

```bash
python client_simple.py --server ws://SERVER_IP:8000/ws
```

Replace SERVER_IP with your server's IP address.

### Step 4: API Testing

#### REST API Example

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What courses are offered?"}'
```

#### Health Check

```bash
curl http://localhost:8000/health
```

#### Statistics

```bash
curl http://localhost:8000/stats
```

## Project Structure

```
CampusConvo/
├── server/
│   ├── __init__.py
│   ├── config.py           # Server configuration
│   ├── rag_pipeline.py     # RAG implementation
│   └── api_server.py       # FastAPI server with WebSocket
├── data/
│   ├── raw/
│   │   └── raw.jsonl
│   └── processed/
│       └── processed.jsonl # Cleaned data (179 entries)
├── embeddings/             # ChromaDB storage (generated)
├── scripts/                # Data processing scripts
├── docs/                   # Documentation
├── tasks/                  # Task definitions
├── run_embeddings.py       # Generate embeddings
├── run_server.py          # Start server
├── client_simple.py       # WebSocket client
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables

```

## Configuration

Edit `.env` file for configuration:

```bash
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO
```

Or modify `server/config.py` directly.

## Troubleshooting

### Issue: "Collection not found" error

Solution: Run `python run_embeddings.py` first to generate embeddings.

### Issue: Import errors

Solution: Make sure you're in the project root directory and virtual environment is activated.

### Issue: Connection refused

Solution: Ensure the server is running before starting the client.

### Issue: No embeddings found

Solution: Check that `data/processed/processed.jsonl` exists and contains data.

## Development Workflow

1. Generate embeddings (one-time setup):
   ```bash
   python run_embeddings.py
   ```

2. Start server (in one terminal):
   ```bash
   python run_server.py
   ```

3. Start client (in another terminal):
   ```bash
   python client_simple.py
   ```

## Next Steps

### TASK4: LLM Integration

Current implementation uses a placeholder response. To integrate an actual LLM:

1. Choose LLM (TinyLLaMA for dev, Mistral/Phi-3 for prod)
2. Update `server/rag_pipeline.py` `generate_response()` method
3. Add LLM inference code
4. Implement streaming support

### TASK6-9: Voice Interface

1. Implement wake word detection (Porcupine)
2. Add STT support (Whisper)
3. Add TTS support (Piper)
4. Create voice client interface

## Performance Notes

- Embedding generation: ~2-5 minutes for 179 entries
- Query latency: <100ms for retrieval
- WebSocket: Real-time bidirectional communication
- ChromaDB: Persistent storage, no rebuild needed

## API Documentation

Once server is running, visit:
- http://localhost:8000/docs - Swagger UI
- http://localhost:8000/redoc - ReDoc documentation

## Support

For issues or questions:
1. Check logs in console output
2. Verify all dependencies are installed
3. Ensure data files exist in correct locations
4. Check server is accessible on configured port
