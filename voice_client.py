"""
CampusConvo Voice Client for Termux
Uses Termux API for recording, sends to server for processing

Prerequisites:
    pkg install termux-api python
    pip install websockets requests
    
Usage:
    python voice_client.py              # Interactive voice mode
    python voice_client.py "question"   # Text query with voice response
"""

import asyncio
import json
import base64
import sys
import subprocess
import os
from pathlib import Path
import requests

# Import server config
try:
    from server.config import WEBSOCKET_URL as SERVER_URL
except ImportError:
    SERVER_URL = "ws://192.168.23.187:8000/ws"

# Extract base URL for HTTP endpoints
HTTP_BASE_URL = SERVER_URL.replace("ws://", "http://").replace("/ws", "")


def record_audio(duration=5, output_file="query.wav"):
    """
    Record audio using Termux API
    
    Args:
        duration: Recording duration in seconds
        output_file: Output file path
    """
    print(f"🎙️  Recording for {duration} seconds... (speak now)")
    
    # Use termux-microphone-record
    result = subprocess.run([
        "termux-microphone-record",
        "-f", output_file,
        "-l", str(duration)
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"Recording failed: {result.stderr}")
    
    print("✓ Recording complete")
    return output_file


def play_audio(audio_file):
    """
    Play audio using Termux API
    
    Args:
        audio_file: Path to audio file
    """
    print("🔊 Playing audio...")
    
    subprocess.run([
        "termux-media-player",
        "play", audio_file
    ], check=True)


def transcribe_audio(audio_file):
    """
    Send audio to server for transcription
    
    Args:
        audio_file: Path to audio file
        
    Returns:
        Transcribed text
    """
    print("⏳ Transcribing audio...")
    
    # Read audio file
    with open(audio_file, 'rb') as f:
        audio_data = f.read()
    
    # Encode to base64
    audio_b64 = base64.b64encode(audio_data).decode('utf-8')
    
    # Send to server
    response = requests.post(
        f"{HTTP_BASE_URL}/voice/transcribe",
        json={"audio": audio_b64},
        timeout=30
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"Transcription failed: {response.text}")
    
    result = response.json()
    
    if result["status"] != "success":
        raise RuntimeError(f"Transcription error: {result.get('error')}")
    
    return result["transcription"]


def synthesize_speech(text, output_file="response.mp3"):
    """
    Get speech audio from server
    
    Args:
        text: Text to convert to speech
        output_file: Output audio file path
        
    Returns:
        Path to audio file
    """
    print("⏳ Generating speech...")
    
    # Send to server
    response = requests.post(
        f"{HTTP_BASE_URL}/voice/synthesize",
        json={"text": text},
        timeout=30
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"Speech synthesis failed: {response.text}")
    
    result = response.json()
    
    if result["status"] != "success":
        raise RuntimeError(f"Synthesis error: {result.get('error')}")
    
    # Decode base64 audio
    audio_data = base64.b64decode(result["audio"])
    
    # Save to file
    with open(output_file, 'wb') as f:
        f.write(audio_data)
    
    return output_file


async def query_rag(query_text):
    """
    Send text query to RAG pipeline via WebSocket
    
    Args:
        query_text: Question text
        
    Returns:
        Response text
    """
    import websockets
    
    print("⏳ Getting answer...")
    
    async with websockets.connect(SERVER_URL) as websocket:
        # Send query
        await websocket.send(json.dumps({
            "query": query_text,
            "top_k": 5
        }))
        
        # Wait for response
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get("status") == "processing":
                print(f"  ⏳ {data.get('message', 'Processing...')}")
                
            elif data.get("status") == "complete":
                return data.get("response")
                
            elif data.get("status") == "error":
                raise RuntimeError(data.get("error", "Unknown error"))


async def voice_query_interactive():
    """Interactive voice query mode"""
    print("="*60)
    print("🎙️  CampusConvo Voice Client")
    print("="*60)
    print(f"Server: {HTTP_BASE_URL}")
    print("="*60)
    
    # Temporary files
    audio_dir = Path("/sdcard/Download")
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    query_audio = audio_dir / "query.wav"
    response_audio = audio_dir / "response.mp3"
    
    while True:
        try:
            input("\nPress Enter to record (or Ctrl+C to quit)...")
            
            # Record audio
            record_audio(duration=5, output_file=str(query_audio))
            
            # Transcribe
            transcription = transcribe_audio(str(query_audio))
            print(f"\n📝 You said: {transcription}")
            
            # Get answer from RAG
            answer = await query_rag(transcription)
            print(f"\n🤖 Bot: {answer}")
            
            # Synthesize speech
            audio_file = synthesize_speech(answer, str(response_audio))
            
            # Play audio
            play_audio(audio_file)
            
            print("\n✓ Done!")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


async def text_query_with_voice(query_text):
    """Text query with voice response"""
    print(f"\n📝 Query: {query_text}")
    
    # Get answer from RAG
    answer = await query_rag(query_text)
    print(f"\n🤖 Bot: {answer}")
    
    # Synthesize speech
    audio_file = synthesize_speech(answer, "/sdcard/Download/response.mp3")
    
    # Play audio
    play_audio(audio_file)
    
    print("\n✓ Done!")


def main():
    """Main entry point"""
    
    # Check Termux API
    result = subprocess.run(["which", "termux-microphone-record"], 
                          capture_output=True)
    if result.returncode != 0:
        print("❌ Termux API not installed!")
        print("Install with: pkg install termux-api")
        return
    
    # Run appropriate mode
    if len(sys.argv) > 1:
        # Text query with voice response
        query = " ".join(sys.argv[1:])
        asyncio.run(text_query_with_voice(query))
    else:
        # Interactive voice mode
        asyncio.run(voice_query_interactive())


if __name__ == "__main__":
    main()
