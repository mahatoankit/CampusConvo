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


async def send_query_and_get_response(query: str, server_url: str = SERVER_URL) -> str:
    """
    Send query and return response text (for voice mode TTS)
    
    Args:
        query: User's question
        server_url: WebSocket server URL
        
    Returns:
        Response text from the bot
    """
    try:
        async with websockets.connect(server_url) as websocket:
            # Send query
            message = {"query": query, "top_k": 5}
            await websocket.send(json.dumps(message))
            
            response_text = ""
            
            # Receive responses
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                status = data.get("status")
                
                if status == "processing":
                    print(f"[PROCESSING] {data.get('message', 'Processing...')}")
                    
                elif status == "complete":
                    response_text = data.get('response', 'No response')
                    print(f"\n[OK] Answer:")
                    print(f"{response_text}")
                    
                    sources = data.get('sources', [])
                    if sources:
                        print(f"\n{'='*60}")
                        print(f" Retrieved {len(sources)} relevant documents:")
                        for i, source in enumerate(sources[:3], 1):
                            print(f"\n  [{i}] Similarity: {source.get('similarity', 0):.2%}")
                            print(f"      Title: {source.get('title', 'N/A')}")
                    print(f"\n{'='*60}")
                    break
                    
                elif status == "error":
                    print(f"\n[ERROR] Error: {data.get('error', 'Unknown error')}")
                    break
                else:
                    break
            
            return response_text
                
    except Exception as e:
        print(f"\nError: {e}")
        return ""


async def send_query(query: str, server_url: str = SERVER_URL):
    """
    Send query to server via WebSocket and display response
    
    Args:
        query: User's question
        server_url: WebSocket server URL
    """
    try:
        # Connect without timeout parameter (Termux compatibility)
        async with websockets.connect(server_url) as websocket:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print(f"{'='*60}")
            print("Waiting for response...")
            
            # Send query
            message = {"query": query, "top_k": 5}
            await websocket.send(json.dumps(message))
            
            # Receive responses (server sends status updates, then final response)
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                status = data.get("status")
                
                if status == "processing":
                    print(f"[PROCESSING] {data.get('message', 'Processing...')}")
                    continue
                    
                elif status == "complete":
                    # Final response
                    print(f"\n[OK] Answer:")
                    print(f"{data.get('response', 'No response')}")
                    
                    sources = data.get('sources', [])
                    if sources:
                        print(f"\n{'='*60}")
                        print(f" Retrieved {len(sources)} relevant documents:")
                        for i, source in enumerate(sources[:3], 1):
                            print(f"\n  [{i}] Similarity: {source.get('similarity', 0):.2%}")
                            print(f"      Title: {source.get('title', 'N/A')}")
                            content = source.get('content', '')[:200]
                            print(f"      {content}...")
                    print(f"\n{'='*60}")
                    break
                    
                elif status == "error":
                    print(f"\n[ERROR] Error: {data.get('error', 'Unknown error')}")
                    break
                    
                else:
                    # Unknown status, print and break
                    print(f"\n[WARNING]  Unexpected response: {data}")
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

def detect_audio_system():
    """Detect which audio recording system is available"""
    # Check for Termux
    if os.path.exists("/data/data/com.termux"):
        if subprocess.run("which termux-microphone-record", shell=True, capture_output=True).returncode == 0:
            return "termux"
    
    # Check for arecord (ALSA - most Linux systems)
    if subprocess.run("which arecord", shell=True, capture_output=True).returncode == 0:
        return "alsa"
    
    # Check for ffmpeg
    if subprocess.run("which ffmpeg", shell=True, capture_output=True).returncode == 0:
        return "ffmpeg"
    
    # Check for sox
    if subprocess.run("which sox", shell=True, capture_output=True).returncode == 0:
        return "sox"
    
    return None


def record_audio(duration=5, output_file=None):
    """
    Record audio using available system tools
    
    Args:
        duration: Recording duration in seconds
        output_file: Output file path (auto-generated if None)
    
    Returns:
        Path to recorded audio file or None on failure
    """
    audio_system = detect_audio_system()
    
    if audio_system is None:
        print("[ERROR] No audio recording tool found!")
        print("Install one of:")
        print("  - Termux: pkg install termux-api")
        print("  - Linux: sudo apt install alsa-utils")
        print("  - Alternative: sudo apt install ffmpeg")
        print("  - Alternative: sudo apt install sox")
        return None
    
    # Set output file based on system
    if output_file is None:
        if audio_system == "termux":
            output_file = "/sdcard/Download/query.wav"
        else:
            output_file = "/tmp/campusconvo_query.wav"
    
    print(f"  Recording for {duration} seconds...")
    print("Speak now!")
    
    try:
        if audio_system == "termux":
            cmd = f"termux-microphone-record -f {output_file} -l {duration}"
        elif audio_system == "alsa":
            # arecord: -d duration, -f format, -r rate
            cmd = f"arecord -d {duration} -f cd -t wav {output_file}"
        elif audio_system == "ffmpeg":
            # ffmpeg: -f alsa, -i device, -t duration
            cmd = f"ffmpeg -f alsa -i default -t {duration} -y {output_file} 2>/dev/null"
        elif audio_system == "sox":
            # sox/rec: -r rate, -c channels, -b bits
            cmd = f"rec -r 16000 -c 1 -b 16 {output_file} trim 0 {duration}"
        
        subprocess.run(cmd, shell=True, check=True)
        print("[OK] Recording complete")
        return output_file
    except Exception as e:
        print(f"[ERROR] Recording failed: {e}")
        return None


def play_audio(audio_file):
    """Play audio using available system tools"""
    if not os.path.exists(audio_file):
        print(f"[WARNING]  Audio file not found: {audio_file}")
        return
    
    try:
        # Detect file format
        is_mp3 = audio_file.endswith('.mp3')
        
        # Detect playback system - prefer MP3-capable players for MP3 files
        if is_mp3:
            # For MP3, try ffplay, mpg123, or mpv first
            if subprocess.run("which ffplay", shell=True, capture_output=True).returncode == 0:
                cmd = f"ffplay -nodisp -autoexit {audio_file} 2>/dev/null"
            elif subprocess.run("which mpg123", shell=True, capture_output=True).returncode == 0:
                cmd = f"mpg123 -q {audio_file}"
            elif subprocess.run("which mpv", shell=True, capture_output=True).returncode == 0:
                cmd = f"mpv --no-video --really-quiet {audio_file}"
            elif subprocess.run("which play", shell=True, capture_output=True).returncode == 0:
                cmd = f"play {audio_file}"
            elif os.path.exists("/data/data/com.termux"):
                cmd = f"termux-media-player play {audio_file}"
            else:
                print("[WARNING]  No MP3 player found. Install: sudo apt install ffmpeg")
                return
        else:
            # For WAV, use aplay or other players
            if os.path.exists("/data/data/com.termux"):
                cmd = f"termux-media-player play {audio_file}"
            elif subprocess.run("which aplay", shell=True, capture_output=True).returncode == 0:
                cmd = f"aplay {audio_file}"
            elif subprocess.run("which ffplay", shell=True, capture_output=True).returncode == 0:
                cmd = f"ffplay -nodisp -autoexit {audio_file} 2>/dev/null"
            elif subprocess.run("which play", shell=True, capture_output=True).returncode == 0:
                cmd = f"play {audio_file}"
            else:
                print("[WARNING]  No audio player found")
                return
        
        subprocess.run(cmd, shell=True)
    except Exception as e:
        print(f"[WARNING]  Could not play audio: {e}")


async def voice_query(enable_audio_response=True):
    """
    Send voice query to server
    
    Args:
        enable_audio_response: Whether to play audio response
    """
    if not VOICE_AVAILABLE:
        print("[ERROR] Voice mode requires 'requests' library")
        print("Install with: pip install requests")
        return
    
    # Record audio
    audio_file = record_audio()
    if not audio_file or not os.path.exists(audio_file):
        return
    
    print("[PROCESSING] Transcribing audio...")
    
    try:
        # Read audio file
        with open(audio_file, 'rb') as f:
            audio_data = f.read()
        
        # Encode to base64
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Send to server for transcription
        response = requests.post(
            f"{HTTP_SERVER_URL}/voice/transcribe",
            json={"audio": audio_b64},  # Server expects "audio" not "audio_b64"
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"[ERROR] Server error: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Detail: {error_detail}")
            except:
                print(f"   Response: {response.text[:200]}")
            return
        
        result = response.json()
        
        if result.get("status") != "success":
            print(f"[ERROR] Transcription failed: {result.get('error')}")
            return
        
        transcription = result.get("transcription", "")
        print(f"\n You said: {transcription}\n")
        
        # Send text query to get response via WebSocket
        print("[PROCESSING] Getting response...")
        response_text = await send_query_and_get_response(transcription)
        
        # Text-to-Speech: Play audio response
        if enable_audio_response and response_text:
            print("\n Converting response to speech...")
            try:
                # Request TTS from server
                tts_response = requests.post(
                    f"{HTTP_SERVER_URL}/voice/synthesize",
                    json={"text": response_text},
                    timeout=30
                )
                
                if tts_response.status_code == 200:
                    tts_result = tts_response.json()
                    if tts_result.get("status") == "success":
                        # Decode base64 audio
                        audio_b64 = tts_result.get("audio", "")
                        audio_data = base64.b64decode(audio_b64)
                        
                        # Save to temporary file
                        temp_audio = "/tmp/campusconvo_response.mp3"
                        with open(temp_audio, 'wb') as f:
                            f.write(audio_data)
                        
                        print(" Playing audio response...")
                        # Play audio
                        play_audio(temp_audio)
                        
                        # Cleanup
                        try:
                            os.remove(temp_audio)
                        except:
                            pass
                    else:
                        print(f"[WARNING]  TTS failed: {tts_result.get('error')}")
                else:
                    print(f"[WARNING]  TTS request failed: {tts_response.status_code}")
            except Exception as e:
                print(f"[WARNING]  Could not play audio response: {e}")
        elif not response_text:
            print("[WARNING]  No response text to convert to speech")
        
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to server at {HTTP_SERVER_URL}")
        print("Make sure server is running: python run_server.py")
    except Exception as e:
        print(f"[ERROR] Error: {e}")


async def interactive_voice_mode():
    """Interactive voice mode"""
    print("="*60)
    print("  CampusConvo - Voice Mode")
    print("="*60)
    print(f"Server: {HTTP_SERVER_URL}")
    print("="*60)
    
    if not VOICE_AVAILABLE:
        print("\n[ERROR] Voice mode not available")
        print("Install requirements: pip install requests")
        return
    
    print("\nPress Enter to start recording, or 'quit' to exit")
    print("-"*60)
    
    while True:
        try:
            user_input = input("\n  Ready? (Enter to record / 'quit' to exit): ").strip().lower()
            
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
            print("[OK] Connected successfully!")
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
                            print(f"  [PROCESSING] {data.get('message', 'Processing...')}")
                            continue
                            
                        elif status == "complete":
                            # Show final response
                            print(f"\nBot: {data.get('response', 'No response')}")
                            
                            sources = data.get('sources', [])
                            if sources:
                                print(f"  (Retrieved {len(sources)} relevant documents)")
                            break
                            
                        elif status == "error":
                            print(f"\n[ERROR] Error: {data.get('error', 'Unknown error')}")
                            break
                            
                        else:
                            # Unknown status
                            print(f"\n[WARNING]  Unexpected response")
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
    print(" CampusConvo - Choose Your Mode")
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
                print("\n[WARNING]  Voice mode requires 'requests' library")
                print("Install with: pip install requests")
                retry = input("Try text mode instead? (y/n): ").strip().lower()
                if retry == 'y':
                    return 'text'
                continue
            return 'voice'
        else:
            print("[ERROR] Invalid choice. Enter 't' for text or 'v' for voice")


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
        mode = choose_mode()
        
        if mode == 'text':
            asyncio.run(interactive_mode(SERVER_URL))
        elif mode == 'voice':
            asyncio.run(interactive_voice_mode())


if __name__ == "__main__":
    main()
