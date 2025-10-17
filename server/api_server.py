"""
FastAPI Server for CampusConvo
Implements REST API and WebSocket endpoints for RAG-based Q&A
"""

import base64
import logging
from typing import List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from server import config
from server.rag_pipeline import RAGPipeline
from server.voice_pipeline import VoicePipeline

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CampusConvo API",
    description="Offline voice-based college assistant for Sunway College",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG pipeline
rag_pipeline: Optional[RAGPipeline] = None

# Initialize Voice pipeline
voice_pipeline: Optional[VoicePipeline] = None


class QueryRequest(BaseModel):
    """Request model for query endpoint"""

    query: str
    top_k: Optional[int] = None
    filter_tags: Optional[List[str]] = None


class QueryResponse(BaseModel):
    """Response model for query endpoint"""

    query: str
    response: str
    context_used: int
    sources: List[str]


class VoiceRequest(BaseModel):
    """Request model for voice transcription"""

    audio: str  # Base64 encoded audio


class VoiceResponse(BaseModel):
    """Response model for voice transcription"""

    status: str
    transcription: Optional[str] = None
    error: Optional[str] = None


class TTSRequest(BaseModel):
    """Request model for text-to-speech"""

    text: str


class TTSResponse(BaseModel):
    """Response model for text-to-speech"""

    status: str
    audio: Optional[str] = None  # Base64 encoded audio
    error: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global rag_pipeline, voice_pipeline
    logger.info("Starting CampusConvo server")

    try:
        rag_pipeline = RAGPipeline()
        logger.info("RAG pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {e}")
        logger.error("Please run 'python run_embeddings.py' to generate embeddings first")
        raise

    # Initialize voice pipeline
    try:
        voice_pipeline = VoicePipeline()
        if voice_pipeline.enabled:
            logger.info("Voice pipeline initialized successfully")
        else:
            logger.info("Voice features disabled")
    except Exception as e:
        logger.warning(f"Voice pipeline initialization failed: {e}")
        voice_pipeline = None


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down CampusConvo server")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CampusConvo API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {"query": "/query", "websocket": "/ws", "health": "/health"},
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")

    try:
        collection_count = rag_pipeline.collection.count()
        return {
            "status": "healthy",
            "embeddings_count": collection_count,
            "model": config.EMBEDDING_MODEL,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a query through RAG pipeline

    Args:
        request: Query request with text and optional parameters

    Returns:
        QueryResponse with answer and sources
    """
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")

    try:
        logger.info(f"Received query: {request.query}")

        result = rag_pipeline.process_query(
            query=request.query, top_k=request.top_k, filter_tags=request.filter_tags
        )

        # Ensure sources are strings (in case they're dicts)
        sources = result.get("sources", [])
        if sources and isinstance(sources[0], dict):
            # Convert dict sources to strings
            sources = [s.get("source", str(s)) for s in sources]
            result["sources"] = sources

        return QueryResponse(**result)

    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time query processing
    Supports streaming responses for voice interaction
    """
    await websocket.accept()
    logger.info("WebSocket connection established")

    if rag_pipeline is None:
        await websocket.send_json({"error": "RAG pipeline not initialized"})
        await websocket.close()
        return

    try:
        while True:
            # Receive query from client
            data = await websocket.receive_json()
            query = data.get("query", "")
            top_k = data.get("top_k", None)
            filter_tags = data.get("filter_tags", None)

            if not query:
                await websocket.send_json({"error": "Empty query"})
                continue

            logger.info(f"WebSocket query received: {query}")

            # Send processing status
            await websocket.send_json(
                {"status": "processing", "message": "Retrieving relevant context..."}
            )

            # Process query through RAG pipeline
            try:
                result = rag_pipeline.process_query(
                    query=query, top_k=top_k, filter_tags=filter_tags
                )

                # Send response
                await websocket.send_json(
                    {
                        "status": "complete",
                        "query": result["query"],
                        "response": result["response"],
                        "context_used": result["context_used"],
                        "sources": result["sources"],
                    }
                )

            except Exception as e:
                logger.error(f"Error processing WebSocket query: {e}", exc_info=True)
                await websocket.send_json({"status": "error", "error": str(e)})

    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass


@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")

    try:
        count = rag_pipeline.collection.count()
        return {
            "total_embeddings": count,
            "collection_name": config.COLLECTION_NAME,
            "embedding_model": config.EMBEDDING_MODEL,
            "top_k_default": config.TOP_K_RESULTS,
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ============ Voice Endpoints ============


@app.post("/voice/transcribe", response_model=VoiceResponse)
async def transcribe_audio(request: VoiceRequest):
    """
    Transcribe audio to text using Whisper STT

    Args:
        request: VoiceRequest with base64 encoded audio

    Returns:
        VoiceResponse with transcription
    """
    if voice_pipeline is None or not voice_pipeline.enabled:
        raise HTTPException(status_code=503, detail="Voice features not available")

    try:
        # Decode base64 audio
        audio_data = base64.b64decode(request.audio)
        logger.info(f"Received audio: {len(audio_data)} bytes")

        # Transcribe
        result = voice_pipeline.process_voice_query(audio_data)

        return VoiceResponse(
            status=result["status"],
            transcription=result.get("transcription"),
            error=result.get("error"),
        )
    except Exception as e:
        logger.error(f"Error in transcribe endpoint: {e}", exc_info=True)
        return VoiceResponse(status="error", error=str(e))


@app.post("/voice/query")
async def voice_query(request: VoiceRequest):
    """
    Complete voice pipeline: transcribe audio → query RAG → synthesize response

    Args:
        request: VoiceRequest with base64 encoded audio

    Returns:
        Dict with status, answer (text), and audio (base64)
    """
    if voice_pipeline is None or not voice_pipeline.enabled:
        raise HTTPException(status_code=503, detail="Voice features not available")
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")

    try:
        # Step 1: Transcribe audio
        audio_data = base64.b64decode(request.audio)
        logger.info(f"Voice query: Received audio ({len(audio_data)} bytes)")

        transcribe_result = voice_pipeline.process_voice_query(audio_data)
        if transcribe_result["status"] != "success":
            return {
                "status": "error",
                "error": transcribe_result.get("error", "Transcription failed"),
            }

        query_text = transcribe_result.get("transcription", "").strip()
        if not query_text:
            return {"status": "error", "error": "Empty transcription"}

        logger.info(f"Voice query: Transcribed: '{query_text}'")

        # Step 2: Query RAG pipeline
        rag_result = rag_pipeline.process_query(query=query_text)
        answer_text = rag_result.get("response", "")

        logger.info(f"Voice query: Generated answer ({len(answer_text)} chars)")

        # Step 3: Synthesize speech
        audio_data = voice_pipeline.synthesize_speech(answer_text)
        audio_b64 = base64.b64encode(audio_data).decode("utf-8")

        return {
            "status": "success",
            "query": query_text,
            "answer": answer_text,
            "audio": audio_b64,
            "sources": rag_result.get("sources", []),
        }

    except Exception as e:
        logger.error(f"Error in voice query endpoint: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}


@app.post("/voice/synthesize", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest):
    """
    Convert text to speech using gTTS

    Args:
        request: TTSRequest with text to synthesize

    Returns:
        TTSResponse with base64 encoded audio
    """
    if voice_pipeline is None or not voice_pipeline.enabled:
        raise HTTPException(status_code=503, detail="Voice features not available")

    try:
        # Synthesize speech
        audio_data = voice_pipeline.synthesize_speech(request.text)

        # Encode to base64
        audio_b64 = base64.b64encode(audio_data).decode("utf-8")

        return TTSResponse(status="success", audio=audio_b64)
    except Exception as e:
        logger.error(f"Error in synthesize endpoint: {e}", exc_info=True)
        return TTSResponse(status="error", error=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on {config.HOST}:{config.PORT}")
    uvicorn.run(app, host=config.HOST, port=config.PORT, log_level=config.LOG_LEVEL.lower())
