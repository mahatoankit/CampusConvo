"""
Run CampusConvo FastAPI Server
"""

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import uvicorn  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

# Load environment variables from .env file FIRST
load_dotenv()

from server import config  # noqa: E402

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Run the FastAPI server"""
    logger.info("=" * 60)
    logger.info("Starting CampusConvo Server")
    logger.info("=" * 60)
    logger.info(f"Host: {config.HOST}")
    logger.info(f"Port: {config.PORT}")
    logger.info(f"Embedding Model: {config.EMBEDDING_MODEL}")
    logger.info(f"Collection: {config.COLLECTION_NAME}")
    logger.info("=" * 60)

    uvicorn.run(
        "server.api_server:app",
        host=config.HOST,
        port=config.PORT,
        log_level=config.LOG_LEVEL.lower(),
        reload=False,
    )


if __name__ == "__main__":
    main()
