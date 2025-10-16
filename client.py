"""
CampusConvo WebSocket Client
Simple client for querying the CampusConvo server

Usage:
    python client.py                    # Interactive mode (choose text or voice)
    python client.py test               # Test mode with predefined queries
    python client.py "your question"    # Single query mode
    
Network Usage:
    Update SERVER_IP in server/config.py when changing networks
"""

import asyncio
import json
import sys
import websockets
from websockets.exceptions import ConnectionClosed
import subprocess
import os
import base64

# Import server configuration
try:
    from server.config import WEBSOCKET_URL as SERVER_URL, SERVER_IP
    HTTP_SERVER_URL = f"http://{SERVER_IP}:8000"
except ImportError:
    # Fallback if config not available (standalone client)
    SERVER_URL = "ws://192.168.23.187:8000/ws"
    HTTP_SERVER_URL = "http://192.168.23.187:8000"

# Try to import requests for voice mode
try:
    import requests
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False


async def send_query(query: str, server_url: str = SERVER_URL, top_k: int = 5):
    """
    Send a single query and print response
    
    Args:
        query: Question to ask
        server_url: WebSocket server URL
        top_k: Number of documents to retrieve
    """
    try:
        # Connect without timeout parameter (Termux compatibility)
        async with websockets.connect(server_url) as websocket:
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


# ==================== VOICE MODE FUNCTIONS ====================

def record_audio(duration=5, output_file="/sdcard/Download/query.wav"):
    """Record audio using Termux API"""
    print(f"🎙️  Recording for {duration} seconds...")
    print("Speak now!")
    
    try:
        cmd = f"termux-microphone-record -f {output_file} -l {duration}"
        subprocess.run(cmd, shell=True, check=True)
        print("✓ Recording complete")
        return output_file
    except Exception as e:
        print(f"❌ Recording failed: {e}")
        print("Make sure termux-api is installed: pkg install termux-api")
        return None


def play_audio(audio_file):
    """Play audio using Termux API"""
    try:
        print("🔊 Playing response...")
        cmd = f"termux-media-player play {audio_file}"
        subprocess.run(cmd, shell=True)
    except Exception as e:
        print(f"⚠️  Could not play audio: {e}")


async def voice_query(enable_audio_response=True):
    """
    Send voice query to server
    
    Args:
        enable_audio_response: Whether to play audio response
    """
    if not VOICE_AVAILABLE:
        print("❌ Voice mode requires 'requests' library")
        print("Install with: pip install requests")
        return
    
    # Record audio
    audio_file = record_audio()
    if not audio_file or not os.path.exists(audio_file):
        return
    
    print("⏳ Transcribing audio...")
    
    try:
        # Read audio file
        with open(audio_file, 'rb') as f:
            audio_data = f.read()
        
        # Encode to base64
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Send to server for transcription
        response = requests.post(
            f"{HTTP_SERVER_URL}/voice/transcribe",
            json={"audio_b64": audio_b64},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Server error: {response.status_code}")
            return
        
        result = response.json()
        
        if result.get("status") != "success":
            print(f"❌ Transcription failed: {result.get('error')}")
            return
        
        transcription = result.get("transcription", "")
        print(f"\n📝 You said: {transcription}\n")
        
        # Send text query to get response via WebSocket
        print("⏳ Getting response...")
        await send_query(transcription)
        
        # Get the response text for TTS (we'll need to modify send_query to return it)
        # For now, we'll skip audio response
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {HTTP_SERVER_URL}")
        print("Make sure server is running: python run_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")


async def interactive_voice_mode():
    """Interactive voice mode"""
    print("="*60)
    print("🎙️  CampusConvo - Voice Mode")
    print("="*60)
    print(f"Server: {HTTP_SERVER_URL}")
    print("="*60)
    
    if not VOICE_AVAILABLE:
        print("\n❌ Voice mode not available")
        print("Install requirements: pip install requests")
        return
    
    print("\nPress Enter to start recording, or 'quit' to exit")
    print("-"*60)
    
    while True:
        try:
            user_input = input("\n🎙️  Ready? (Enter to record / 'quit' to exit): ").strip().lower()
            
            if user_input in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            await voice_query()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


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
        # Connect without timeout parameter (Termux compatibility)
        async with websockets.connect(server_url) as websocket:
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
    python client.py                    # Interactive mode (choose text/voice)
    python client.py test               # Test mode
    python client.py "your question"    # Single query
    
Network Usage:
    Edit SERVER_IP in server/config.py when changing networks
    
Examples:
    python client.py
    python client.py test
    python client.py "What courses are available?"
    """)


def choose_mode():
    """Let user choose between text and voice mode"""
    print("\n" + "="*60)
    print("🎯 CampusConvo - Choose Your Mode")
    print("="*60)
    print("\n[T] Text Mode   - Type your questions")
    print("[V] Voice Mode  - Speak your questions (requires Termux API)")
    print("\n" + "="*60)
    
    while True:
        choice = input("\nChoose mode (t/v): ").strip().lower()
        
        if choice in ['t', 'text']:
            return 'text'
        elif choice in ['v', 'voice']:
            if not VOICE_AVAILABLE:
                print("\n⚠️  Voice mode requires 'requests' library")
                print("Install with: pip install requests")
                retry = input("Try text mode instead? (y/n): ").strip().lower()
                if retry == 'y':
                    return 'text'
                continue
            return 'voice'
        else:
            print("❌ Invalid choice. Enter 't' for text or 'v' for voice")


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
        # Interactive mode - let user choose text or voice
        print("DEBUG: Entering mode selection...")  # Debug line
        mode = choose_mode()
        print(f"DEBUG: Selected mode = {mode}")  # Debug line
        
        if mode == 'text':
            asyncio.run(interactive_mode(SERVER_URL))
        elif mode == 'voice':
            asyncio.run(interactive_voice_mode())


if __name__ == "__main__":
    main()
