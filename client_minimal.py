"""
Minimal CampusConvo Client for Termux
Usage: python client_minimal.py "your question"
"""
import asyncio
import json
import sys
import websockets

SERVER_URL = "ws://localhost:8000/ws"  # Change to your server IP

async def query(question):
    try:
        async with websockets.connect(SERVER_URL, timeout=30) as ws:
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
