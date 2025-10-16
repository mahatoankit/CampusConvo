"""
Minimal CampusConvo Client for Termux
Usage: python client_minimal.py "your question"
Network: Update SERVER_IP in server/config.py when changing networks
"""
import asyncio
import json
import sys
import websockets

# Import server configuration
try:
    from server.config import WEBSOCKET_URL as SERVER_URL
except ImportError:
    # Fallback if config not available (standalone client)
    SERVER_URL = "ws://192.168.23.187:8000/ws"

async def query(question):
    try:
        # Connect without timeout parameter (Termux compatibility)
        async with websockets.connect(SERVER_URL) as ws:
            await ws.send(json.dumps({"query": question, "top_k": 5}))
            
            while True:
                data = json.loads(await ws.recv())
                
                if data.get("status") == "processing":
                    print(f"⏳ {data.get('message')}")
                elif data.get("status") == "complete":
                    print(f"\n✓ {data.get('response')}")
                    break
                elif data.get("status") == "error":
                    print(f"❌ {data.get('error')}")
                    break
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python client_minimal.py 'your question'")
    else:
        asyncio.run(query(" ".join(sys.argv[1:])))
