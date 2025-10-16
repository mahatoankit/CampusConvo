"""
RAG Pipeline for CampusConvo
Retrieval-Augmented Generation using ChromaDB and Google Gemini
"""

import logging
from typing import List, Dict, Optional
import json
import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from server import config

logger = logging.getLogger(__name__)


class RAGPipeline:
    """RAG pipeline for context retrieval and response generation"""
    
    def __init__(self):
        """Initialize RAG pipeline components"""
        logger.info("Initializing RAG Pipeline")
        
        # Force CPU usage
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        device = "cpu"
        logger.info(f"Using device: {device} (CUDA disabled)")
        
        # Load embedding model
        logger.info(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL, device=device)
        
        # Initialize ChromaDB client
        logger.info(f"Connecting to ChromaDB at: {config.CHROMA_PATH}")
        self.client = chromadb.PersistentClient(
            path=str(config.CHROMA_PATH),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get collection
        try:
            self.collection = self.client.get_collection(name=config.COLLECTION_NAME)
            count = self.collection.count()
            logger.info(f"Connected to collection '{config.COLLECTION_NAME}' with {count} embeddings")
        except Exception as e:
            logger.error(f"Failed to connect to collection: {e}")
            raise RuntimeError(
                f"ChromaDB collection '{config.COLLECTION_NAME}' not found. "
                "Please run 'python run_embeddings.py' first to generate embeddings."
            )
        
        # Initialize Google Gemini for response generation
        self.use_llm = os.environ.get("USE_LLM", "true").lower() == "true"
        self.llm = None
        
        if self.use_llm:
            try:
                import google.generativeai as genai
                
                api_key = os.environ.get("GEMINI_API_KEY")
                if not api_key:
                    logger.warning("GEMINI_API_KEY not found in environment")
                    logger.warning("Get your free API key from: https://makersuite.google.com/app/apikey")
                    logger.warning("Using context-only responses")
                    self.use_llm = False
                else:
                    genai.configure(api_key=api_key)
                    self.llm = genai.GenerativeModel('gemini-2.0-flash-exp')
                    logger.info("[OK] Google Gemini initialized successfully - GENERATIVE RESPONSES ENABLED")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                logger.warning("Falling back to context-only responses")
                self.use_llm = False
        else:
            logger.info("LLM disabled. Using context-only responses")
        
        logger.info("RAG Pipeline initialization complete")
    
    def retrieve_context(
        self,
        query: str,
        top_k: int = None,
        filter_tags: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Retrieve relevant context from vector database
        
        Args:
            query: User query text
            top_k: Number of results to retrieve
            filter_tags: Optional list of tags to filter results
            
        Returns:
            List of relevant documents with metadata
        """
        if top_k is None:
            top_k = config.DEFAULT_TOP_K
        
        logger.info(f"Retrieving context for query: '{query[:50]}...'")
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Prepare where clause for filtering
        where_clause = None
        if filter_tags:
            where_clause = {"tags": {"$contains": filter_tags[0]}}
        
        # Query ChromaDB
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause
            )
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return []
        
        # Format results
        retrieved_docs = []
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            # Filter by similarity threshold
            similarity = 1 - distance
            if similarity < config.SIMILARITY_THRESHOLD:
                continue
            
            retrieved_docs.append({
                "rank": i + 1,
                "content": doc,
                "metadata": metadata,
                "similarity": round(similarity, 4),
                "distance": round(distance, 4)
            })
        
        logger.info(f"Retrieved {len(retrieved_docs)} relevant documents")
        return retrieved_docs
    
    def format_context(self, retrieved_docs: List[Dict]) -> str:
        """
        Format retrieved documents into context string for LLM
        
        Args:
            retrieved_docs: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        if not retrieved_docs:
            return "No relevant information found in the database."
        
        context_parts = []
        context_parts.append("Relevant Information from Sunway College Database:\n")
        
        for doc in retrieved_docs:
            context_parts.append(f"\n[Source {doc['rank']}]")
            context_parts.append(f"Title: {doc['metadata'].get('title', 'N/A')}")
            context_parts.append(f"Source: {doc['metadata'].get('source', 'N/A')}")
            
            tags = doc['metadata'].get('tags', '[]')
            try:
                tags_list = json.loads(tags) if isinstance(tags, str) else tags
                if tags_list:
                    context_parts.append(f"Topics: {', '.join(tags_list)}")
            except:
                pass
            
            context_parts.append(f"Content: {doc['content']}")
            context_parts.append(f"Relevance: {doc['similarity']:.2%}\n")
        
        return "\n".join(context_parts)
    
    def generate_response(
        self,
        query: str,
        retrieved_docs: List[Dict],
        stream: bool = False
    ) -> str:
        """
        Generate response using Google Gemini with retrieved context
        
        Args:
            query: User query
            retrieved_docs: Retrieved context documents
            stream: Whether to stream response
            
        Returns:
            Generated response text
        """
        if not retrieved_docs:
            return "I couldn't find relevant information in the Sunway College database to answer your question. Please try rephrasing or ask about courses, admissions, placements, or facilities at Sunway College."
        
        # Format context from retrieved documents
        context_text = ""
        for i, doc in enumerate(retrieved_docs[:5], 1):
            context_text += f"\n[Source {i}]:\n{doc['content']}\n"
        
        # If LLM is not available, return formatted context
        if not self.use_llm or not self.llm:
            logger.info("Returning context-based response (LLM disabled)")
            return f"Based on the information from Sunway College:\n\n{context_text}"
        
        # Create prompt for Gemini
        prompt = f"""You are a helpful college assistant for Sunway College in Kathmandu, Nepal. Answer the student's question based ONLY on the provided context below.

Context from Sunway College database:
{context_text}

Student Question: {query}

Instructions:
- Answer ONLY what the student asked - no extra information
- If they ask for location, give ONLY the address
- If they ask for contact, give ONLY contact details
- If they ask for a specific detail, provide ONLY that detail
- Use ONLY information from the context above
- Be direct and concise (1-2 sentences)
- If the context doesn't contain the answer, say "I don't have that specific information in my database."
- Don't add unrequested details like phone numbers, addresses, or other information unless specifically asked

Answer:"""
        
        try:
            logger.info(" Generating GENERATIVE response with Google Gemini...")
            
            response = self.llm.generate_content(prompt)
            generated_text = response.text
            
            logger.info(f"[OK] Generated response: {generated_text[:100]}...")
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            logger.warning("Falling back to context-based response")
            return f"Based on the information from Sunway College:\n\n{context_text}"
    
    def process_query(
        self,
        query: str,
        top_k: int = None,
        filter_tags: Optional[List[str]] = None,
        stream: bool = False
    ) -> Dict:
        """
        Complete RAG pipeline: retrieve context and generate response
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            filter_tags: Optional tags for filtering
            stream: Whether to stream response
            
        Returns:
            Dictionary with response and metadata
        """
        logger.info(f"Processing query: '{query}'")
        
        # Retrieve relevant context
        retrieved_docs = self.retrieve_context(query, top_k, filter_tags)
        
        # Generate response
        response = self.generate_response(query, retrieved_docs, stream)
        
        return {
            "query": query,
            "response": response,
            "context_used": len(retrieved_docs),
            "sources": [
                {
                    "title": doc['metadata'].get('title', ''),
                    "source": doc['metadata'].get('source', ''),
                    "similarity": doc['similarity']
                }
                for doc in retrieved_docs
            ]
        }
