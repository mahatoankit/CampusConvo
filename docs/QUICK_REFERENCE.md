# CampusConvo - Quick Reference

## Quick Start

```bash
# 1. Setup (one-time)
source env/bin/activate
./setup.sh

# 2. Start server (terminal 1)
python run_server.py

# 3. Start client (terminal 2)
python client_simple.py
```

## Commands

### Embedding Generation
```bash
python run_embeddings.py
```
Generates embeddings and stores in `embeddings/` directory.

### Server
```bash
python run_server.py
```
Starts FastAPI server on http://localhost:8000

### Client
```bash
# Interactive mode
python client_simple.py

# Test mode
python client_simple.py test

# Single query
python client_simple.py "What are the admission requirements?"

# Remote connection
python client_simple.py --server ws://SERVER_IP:8000/ws
```

## API Endpoints

### REST API
```bash
# Health check
curl http://localhost:8000/health

# Statistics
curl http://localhost:8000/stats

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What courses are offered?"}'
```

### WebSocket
```javascript
ws://localhost:8000/ws
```

## Project Structure

```
CampusConvo/
├── server/              # Server components
│   ├── config.py        # Configuration
│   ├── rag_pipeline.py  # RAG logic
│   └── api_server.py    # FastAPI server
├── data/
│   └── processed/
│       └── processed.jsonl  # 180 documents
├── embeddings/          # ChromaDB storage
├── client_simple.py     # WebSocket client
├── run_embeddings.py    # Generate embeddings
└── run_server.py        # Start server
```

## Common Issues

### "Collection not found"
```bash
python run_embeddings.py
```

### Port already in use
```bash
# Change port in .env or config.py
SERVER_PORT=8001
```

### Import errors
```bash
# Ensure you're in project root
cd /path/to/CampusConvo
source env/bin/activate
```

## Configuration

### .env File
```bash
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO
GEMINI_API_KEY=your-key-here
```

### Config Variables
- `TOP_K_RESULTS` - Number of documents to retrieve (default: 5)
- `SIMILARITY_THRESHOLD` - Minimum similarity score (default: 0.5)
- `EMBEDDING_MODEL` - Model name (default: all-MiniLM-L6-v2)

## Example Queries

```
What courses are offered at Sunway?
Tell me about placement opportunities
What is the partnership with Birmingham City University?
How can I apply for scholarships?
What are the entry requirements?
Who are the faculty members?
What is the class schedule?
```

## Files to Know

### Core Implementation
- `server/rag_pipeline.py` - RAG logic
- `server/api_server.py` - Server endpoints
- `client/websocket_client.py` - Client implementation
- `run_embeddings.py` - Embedding generation

### Configuration
- `server/config.py` - Server settings
- `.env` - Environment variables
- `requirements.txt` - Dependencies

### Documentation
- `docs/SETUP_GUIDE.md` - Detailed setup instructions
- `docs/IMPLEMENTATION_SUMMARY.md` - Technical details
- `README.md` - Project overview

## Performance

- Embedding generation: ~2-5 minutes
- Query response: <200ms
- Database size: ~50MB for 180 docs
- Memory usage: ~500MB

## Task Status

### Completed
- [x] TASK3: Embeddings & Vector DB
- [x] TASK5: FastAPI Server & RAG

### Pending
- [ ] TASK4: LLM Integration
- [ ] TASK6-9: Voice Interface
- [ ] TASK10: Testing & Optimization

## Useful Links

- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health
- Stats: http://localhost:8000/stats

## Logs

Server logs show:
- Incoming queries
- Retrieval results
- Response generation
- Errors and warnings

Check console output or configure file logging in `server/config.py`.

## Development

### Add New Endpoint
Edit `server/api_server.py`:
```python
@app.get("/new-endpoint")
async def new_endpoint():
    return {"message": "Hello"}
```

### Modify RAG Logic
Edit `server/rag_pipeline.py`:
```python
def retrieve_context(self, query, top_k):
    # Custom retrieval logic
    pass
```

### Change Embedding Model
Edit `server/config.py`:
```python
EMBEDDING_MODEL = "all-mpnet-base-v2"
```
Then regenerate embeddings:
```bash
python run_embeddings.py
```

## Testing

```bash
# Test embeddings
python run_embeddings.py

# Test server
curl http://localhost:8000/health

# Test client
python run_client.py test
```

## Support

For issues:
1. Check logs
2. Verify dependencies installed
3. Ensure data files exist
4. Check server is running
5. Review documentation in `docs/`
