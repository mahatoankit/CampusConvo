"""
CampusConvo WebSocket Client
Simple client for querying the CampusConvo server

Usage:
    python client_simple.py                    # Interactive mode
    python client_simple.py test               # Test mode with predefined queries
    python client_simple.py "your question"    # Single query mode
    
Network Usage (change SERVER_URL):
    SERVER_URL = "ws://192.168.1.100:8000/ws"  # Remote server
"""

import asyncio
import json
import sys
import websockets
from websockets.exceptions import ConnectionClosed

# Server configuration
SERVER_URL = "ws://192.168.254.135:8000/ws"


async def send_query(query: str, server_url: str = SERVER_URL, top_k: int = 5):
    """
    Send a single query and print response
    
    Args:
        query: Question to ask
        server_url: WebSocket server URL
        top_k: Number of documents to retrieve
    """
    try:
        async with websockets.connect(server_url, timeout=30) as websocket:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print(f"{'='*60}")
            print("Waiting for response...")
            
            # Send query
            message = {"query": query, "top_k": top_k}
            await websocket.send(json.dumps(message))
            
            # Receive responses (server sends status updates, then final response)
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                
                status = data.get("status")
                
                if status == "processing":
                    # Processing status message
                    print(f"⏳ {data.get('message', 'Processing...')}")
                    continue
                    
                elif status == "complete":
                    # Final response
                    print(f"\n✓ Answer:")
                    print(f"{data.get('response', 'No response')}")
                    
                    sources = data.get('sources', [])
                    if sources:
                        print(f"\n{'='*60}")
                        print(f"📚 Retrieved {len(sources)} relevant documents:")
                        for i, source in enumerate(sources[:3], 1):
                            print(f"\n  [{i}] Similarity: {source.get('similarity', 0):.2%}")
                            print(f"      Title: {source.get('title', 'N/A')}")
                            content = source.get('content', '')[:200]
                            print(f"      {content}...")
                    print(f"\n{'='*60}")
                    break
                    
                elif status == "error":
                    print(f"\n❌ Error: {data.get('error', 'Unknown error')}")
                    break
                    
                else:
                    # Unknown status, print and break
                    print(f"\n⚠️  Unexpected response: {data}")
                    break
                
    except ConnectionClosed:
        print("\nConnection closed by server")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("  1. Check if server is running: python run_server.py")
        print("  2. Check server URL is correct")
        print("  3. Check network connectivity")


async def interactive_mode(server_url: str = SERVER_URL):
    """
    Interactive mode - chat with the assistant
    
    Args:
        server_url: WebSocket server URL
    """
    print("="*60)
    print("CampusConvo - Interactive Client")
    print("="*60)
    print(f"Server: {server_url}")
    print("="*60)
    print("Connecting to server...")
    
    try:
        async with websockets.connect(server_url, timeout=10) as websocket:
            print("✓ Connected successfully!")
            print("\nType your questions (or 'quit' to exit)")
            print("-"*60)
            
            while True:
                try:
                    query = input("\nYou: ").strip()
                    
                    if not query:
                        continue
                    
                    if query.lower() in ['quit', 'exit', 'q']:
                        print("\nGoodbye!")
                        break
                    
                    # Send query
                    message = {"query": query, "top_k": 5}
                    await websocket.send(json.dumps(message))
                    
                    # Receive responses (handle status updates and final response)
                    while True:
                        response = await websocket.recv()
                        data = json.loads(response)
                        
                        status = data.get("status")
                        
                        if status == "processing":
                            # Show processing message
                            print(f"  ⏳ {data.get('message', 'Processing...')}")
                            continue
                            
                        elif status == "complete":
                            # Show final response
                            print(f"\nBot: {data.get('response', 'No response')}")
                            
                            sources = data.get('sources', [])
                            if sources:
                                print(f"  (Retrieved {len(sources)} relevant documents)")
                            break
                            
                        elif status == "error":
                            print(f"\n❌ Error: {data.get('error', 'Unknown error')}")
                            break
                            
                        else:
                            # Unknown status
                            print(f"\n⚠️  Unexpected response")
                            break
                        
                except KeyboardInterrupt:
                    print("\n\nGoodbye!")
                    break
                except ConnectionClosed:
                    print("\nConnection lost. Exiting...")
                    break
                except Exception as e:
                    print(f"\nError: {e}")
                    
    except Exception as e:
        print(f"\n✗ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check if server is running: python run_server.py")
        print("  2. Check server URL is correct")
        print("  3. Check network connectivity")


async def test_mode(server_url: str = SERVER_URL):
    """
    Test mode with predefined queries
    
    Args:
        server_url: WebSocket server URL
    """
    print("="*60)
    print("CampusConvo - Test Mode")
    print("="*60)
    print(f"Server: {server_url}")
    print("="*60)
    
    test_queries = [
        "What courses are offered at Sunway College?",
        "Tell me about placement opportunities",
        "What is the partnership with Birmingham City University?",
        "How can I apply for scholarships?",
        "What are the class timings?",
        "Where is Sunway College located?"
    ]
    
    for query in test_queries:
        await send_query(query, server_url)
        await asyncio.sleep(1)  # Small delay between queries


def print_usage():
    """Print usage information"""
    print("""
CampusConvo WebSocket Client

Usage:
    python client_simple.py                    # Interactive mode
    python client_simple.py test               # Test mode
    python client_simple.py "your question"    # Single query
    
Network Usage:
    Edit SERVER_URL in the script:
    SERVER_URL = "ws://192.168.1.100:8000/ws"  # Your server IP
    
Examples:
    python client_simple.py
    python client_simple.py test
    python client_simple.py "What courses are available?"
    """)


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['help', '-h', '--help']:
            print_usage()
        elif arg == 'test':
            print("Running test queries...")
            asyncio.run(test_mode(SERVER_URL))
        else:
            # Single query mode
            query = " ".join(sys.argv[1:])
            asyncio.run(send_query(query, SERVER_URL))
    else:
        # Interactive mode (default)
        asyncio.run(interactive_mode(SERVER_URL))


if __name__ == "__main__":
    main()
