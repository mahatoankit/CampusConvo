"""
Generate embeddings from processed college data and store in ChromaDB
Implements TASK3 - Generate Embeddings and Vector DB
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import chromadb  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402
from tqdm import tqdm  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings from documents using sentence-transformers"""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        chroma_path: str = "./embeddings/chroma_db",
        batch_size: int = 32,
    ):
        """
        Initialize embedding generator

        Args:
            model_name: Name of sentence-transformer model
            chroma_path: Path to ChromaDB storage
            batch_size: Batch size for embedding generation
        """
        logger.info(f"Loading embedding model: {model_name}")

        # Auto-detect device: use GPU if available, otherwise CPU
        import torch

        if torch.cuda.is_available():
            device = "cuda"
            logger.info(f"Using device: {device} (GPU available)")
        else:
            device = "cpu"
            logger.info(f"Using device: {device} (GPU not available)")

        self.model = SentenceTransformer(model_name, device=device)
        self.batch_size = batch_size

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)

        # Create or get collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="college_documents", metadata={"hnsw:space": "cosine"}
        )

        logger.info(f"Initialized ChromaDB at {chroma_path}")

    def load_data(self, data_path: str) -> List[Dict]:
        """Load processed JSONL data"""
        data_path = Path(data_path)
        logger.info(f"Loading data from: {data_path}")
        data = []

        if not data_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")

        with open(data_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        data.append(entry)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON on line {line_num}: {e}")

        logger.info(f"Loaded {len(data)} entries")
        return data

    def prepare_text_for_embedding(self, entry: Dict) -> str:
        """
        Prepare text from entry for embedding
        Combines content with metadata for richer embeddings
        """
        text_parts = []

        # Add title if available
        if entry.get("title") and entry["title"] != "No Title":
            text_parts.append(f"Title: {entry['title']}")

        # Add main content
        content = entry.get("content", "").strip()
        if content:
            text_parts.append(content)

        # Add source information
        if entry.get("source"):
            text_parts.append(f"Source: {entry['source']}")

        # Add tags as context
        tags = entry.get("metadata", {}).get("tags", [])
        if tags:
            text_parts.append(f"Topics: {', '.join(tags)}")

        return " | ".join(text_parts)

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks

        Args:
            text: Text to chunk
            chunk_size: Approximate words per chunk
            overlap: Overlapping words between chunks

        Returns:
            List of text chunks
        """
        words = text.split()

        if len(words) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]
            chunks.append(" ".join(chunk_words))
            start = end - overlap

        return chunks

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text list"""
        logger.info(f"Generating embeddings for {len(texts)} texts")
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        return embeddings.tolist()

    def store_embeddings(self, data: List[Dict]):
        """Generate and store embeddings in ChromaDB"""
        logger.info("Processing entries and generating embeddings")

        ids = []
        embeddings_list = []
        documents = []
        metadatas = []

        for entry in tqdm(data, desc="Processing entries"):
            entry_id = entry.get("id", "unknown")

            # Prepare text for embedding
            text = self.prepare_text_for_embedding(entry)

            # Chunk text if too long
            chunks = self.chunk_text(text)

            # Generate embeddings for each chunk
            chunk_embeddings = self.generate_embeddings(chunks)

            # Store each chunk with metadata
            for idx, (chunk, embedding) in enumerate(zip(chunks, chunk_embeddings, strict=False)):
                chunk_id = f"{entry_id}_chunk{idx}" if len(chunks) > 1 else entry_id

                metadata = {
                    "entry_id": entry_id,
                    "source": entry.get("source", ""),
                    "title": entry.get("title", ""),
                    "source_type": entry.get("metadata", {}).get("source_type", ""),
                    "tags": json.dumps(entry.get("metadata", {}).get("tags", [])),
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                }

                ids.append(chunk_id)
                embeddings_list.append(embedding)
                documents.append(chunk)
                metadatas.append(metadata)

        # Batch insert into ChromaDB
        logger.info(f"Storing {len(ids)} embeddings in ChromaDB")
        batch_size = 100

        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i : i + batch_size]
            batch_embeddings = embeddings_list[i : i + batch_size]
            batch_documents = documents[i : i + batch_size]
            batch_metadatas = metadatas[i : i + batch_size]

            self.collection.add(
                ids=batch_ids,
                embeddings=batch_embeddings,
                documents=batch_documents,
                metadatas=batch_metadatas,
            )

            logger.info(f"Stored batch {i//batch_size + 1}/{(len(ids)-1)//batch_size + 1}")

        logger.info("Successfully stored all embeddings")

    def test_retrieval(self, query: str = "What courses are offered at Sunway?", top_k: int = 3):
        """Test retrieval with a sample query"""
        logger.info(f"Testing retrieval with query: '{query}'")

        query_embedding = self.model.encode([query])[0].tolist()

        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)

        logger.info(f"Retrieved {len(results['documents'][0])} results")
        print("\n" + "=" * 80)
        print(f"Query: {query}")
        print("=" * 80)

        for i, (doc, metadata, distance) in enumerate(
            zip(results["documents"][0], results["metadatas"][0], results["distances"][0], strict=False), 1
        ):
            print(f"\nResult {i} (distance: {distance:.4f})")
            print(f"Source: {metadata.get('source', 'N/A')}")
            print(f"Title: {metadata.get('title', 'N/A')}")
            print(f"Tags: {metadata.get('tags', '[]')}")
            print(f"Content: {doc[:200]}...")
            print("-" * 80)

    def get_collection_stats(self):
        """Display collection statistics"""
        count = self.collection.count()
        logger.info(f"Collection 'college_documents' contains {count} embeddings")
        return count


def main():
    """Main execution function"""
    logger.info("Starting embedding generation pipeline")

    try:
        generator = EmbeddingGenerator(
            model_name="all-MiniLM-L6-v2", chroma_path="./embeddings/chroma_db", batch_size=32
        )

        data = generator.load_data("data/processed/processed.jsonl")

        generator.store_embeddings(data)

        stats = generator.get_collection_stats()

        logger.info("Testing retrieval with sample queries")
        generator.test_retrieval("What courses are offered at Sunway?", top_k=3)
        generator.test_retrieval("Tell me about placements", top_k=3)
        generator.test_retrieval("Birmingham City University partnership", top_k=3)

        logger.info("Embedding generation completed successfully")
        logger.info(f"Total embeddings stored: {stats}")

    except Exception as e:
        logger.error(f"Error during embedding generation: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
