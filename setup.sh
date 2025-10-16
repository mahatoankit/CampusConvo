#!/bin/bash
# Quick setup script for CampusConvo

echo "======================================================"
echo "CampusConvo - Quick Setup"
echo "======================================================"

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Warning: Virtual environment not activated"
    echo "Please run: source env/bin/activate"
    exit 1
fi

echo "Step 1: Installing dependencies..."
pip install -q fastapi uvicorn websockets chromadb sentence-transformers python-dotenv tqdm

echo ""
echo "Step 2: Checking data file..."
if [ ! -f "data/processed/processed.jsonl" ]; then
    echo "Error: data/processed/processed.jsonl not found"
    echo "Please ensure your processed data is available"
    exit 1
fi

echo "Data file found: $(wc -l < data/processed/processed.jsonl) entries"

echo ""
echo "Step 3: Generating embeddings..."
python run_embeddings.py

if [ $? -ne 0 ]; then
    echo "Error: Failed to generate embeddings"
    exit 1
fi

echo ""
echo "======================================================"
echo "Setup Complete!"
echo "======================================================"
echo ""
echo "To start the server:"
echo "  python run_server.py"
echo ""
echo "To start the client (in another terminal):"
echo "  python run_client.py"
echo ""
echo "For test mode:"
echo "  python run_client.py test"
echo "======================================================"
