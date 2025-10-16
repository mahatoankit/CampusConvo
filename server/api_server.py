"""
FastAPI Server for CampusConvo
Implements REST API and WebSocket endpoints for RAG-based Q&A
"""

import logging
from typing import Optional, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from server.rag_pipeline import RAGPipeline
from server import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CampusConvo API",
    description="Offline voice-based college assistant for Sunway College",
    version="1.0.0"
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


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global rag_pipeline
    logger.info("Starting CampusConvo server")
    
    try:
        rag_pipeline = RAGPipeline()
        logger.info("RAG pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {e}")
        logger.error("Please run 'python run_embeddings.py' to generate embeddings first")
        raise


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
        "endpoints": {
            "query": "/query",
            "websocket": "/ws",
            "health": "/health"
        }
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
            "model": config.EMBEDDING_MODEL
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))


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
            query=request.query,
            top_k=request.top_k,
            filter_tags=request.filter_tags
        )
        
        return QueryResponse(**result)
    
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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
            await websocket.send_json({
                "status": "processing",
                "message": "Retrieving relevant context..."
            })
            
            # Process query through RAG pipeline
            try:
                result = rag_pipeline.process_query(
                    query=query,
                    top_k=top_k,
                    filter_tags=filter_tags
                )
                
                # Send response
                await websocket.send_json({
                    "status": "complete",
                    "query": result["query"],
                    "response": result["response"],
                    "context_used": result["context_used"],
                    "sources": result["sources"]
                })
                
            except Exception as e:
                logger.error(f"Error processing WebSocket query: {e}", exc_info=True)
                await websocket.send_json({
                    "status": "error",
                    "error": str(e)
                })
    
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({"error": str(e)})
        except:
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
            "top_k_default": config.TOP_K_RESULTS
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {config.HOST}:{config.PORT}")
    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        log_level=config.LOG_LEVEL.lower()
    )
