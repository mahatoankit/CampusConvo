# Voice Mode Setup Guide

## ✅ What's Working

Your CampusConvo system now supports **two modes**:

1. **Text Mode** - Type your questions (WebSocket)
2. **Voice Mode** - Speak your questions (HTTP + Termux API)

## 🎯 How to Use

### On Server (Laptop)

```bash
# Start the server (same as before)
python run_server.py
```

The server will show:
- ✅ RAG pipeline initialized successfully
- ✅ Voice pipeline initialized successfully (if enabled in .env)

### On Client (Termux/Phone or Laptop)

```bash
# Run the client
python client.py
```

You'll see:
```
============================================================
🎯 CampusConvo - Choose Your Mode
============================================================

[T] Text Mode   - Type your questions
[V] Voice Mode  - Speak your questions (requires Termux API)

============================================================
Choose mode (T/V):
```

#### Text Mode (T)
- Works exactly as before
- Type your questions
- Get AI responses via Gemini

#### Voice Mode (V)
- **Termux only** (requires termux-api package)
- Records 5 seconds of audio when you press Enter
- Sends audio to server for transcription (Whisper STT)
- Gets AI response from RAG pipeline
- Displays text response (no audio playback yet)

## 📱 Termux Setup for Voice Mode

### Prerequisites
```bash
# Install Termux API app from F-Droid
# https://f-droid.org/en/packages/com.termux.api/

# Install termux-api package in Termux
pkg install termux-api

# Give microphone permissions to Termux:API app in Android settings
```

### Test Microphone
```bash
# Test recording (creates test.wav)
termux-microphone-record -f test.wav -d 3
# Wait 3 seconds
termux-microphone-record -q

# Check if file exists
ls -lh test.wav
```

## 🔧 Configuration

### Enable/Disable Voice Features

Edit `.env`:
```bash
ENABLE_VOICE=true    # Set to false to disable voice
STT_MODEL=base       # Whisper model: tiny, base, small, medium, large
TTS_ENGINE=gtts      # Text-to-speech (not used in client yet)
```

### Change Network IP

Edit `server/config.py`:
```python
SERVER_IP = os.getenv("SERVER_IP", "192.168.23.187")  # Change this
```

The client automatically imports this via `WEBSOCKET_URL` and `HTTP_SERVER_URL`.

## 🎙️ Voice Mode Flow

1. **Client**: Records 5 seconds of audio via termux-microphone-record
2. **Client**: Encodes audio to base64
3. **Client**: POSTs to `http://{SERVER_IP}:8000/voice/transcribe`
4. **Server**: Decodes audio, runs Whisper STT
5. **Server**: Returns transcription text
6. **Client**: Sends transcription to RAG pipeline (same as text query)
7. **Client**: Displays response

## 📊 System Status

### Models & Sizes
- **Whisper base**: ~150MB (server-side)
- **ChromaDB**: 760 embeddings, 180 documents
- **Gemini API**: gemini-2.0-flash-exp (cloud)

### Dependencies Installed
- ✅ openai-whisper (STT)
- ✅ gtts (TTS, not used yet)
- ✅ ffmpeg (audio processing)
- ✅ pydub (audio manipulation)
- ✅ soundfile (audio I/O)

## 🐛 Troubleshooting

### Voice mode not available
- Check `ENABLE_VOICE=true` in `.env`
- Restart server: `python run_server.py`
- Check server logs for "Voice pipeline initialized"

### Termux microphone not working
- Install termux-api: `pkg install termux-api`
- Install Termux:API app from F-Droid
- Grant microphone permission in Android settings
- Test: `termux-microphone-record -f test.wav -d 3`

### Client can't connect
- Update `SERVER_IP` in `server/config.py`
- Check laptop firewall (port 8000)
- Verify both devices on same network
- Test connection: `curl http://{SERVER_IP}:8000/health`

## 🚀 Next Steps

1. **Test text mode**: `python client.py` → Choose T
2. **Test voice mode in Termux**: `python client.py` → Choose V
3. **Optional**: Add audio response playback (TTS on client side)
4. **Optional**: Adjust Whisper model size (tiny/base/small) in `.env`

## 📝 Files Modified

- ✅ `client.py` - Unified client with mode selection
- ✅ `server/config.py` - Voice settings added
- ✅ `server/voice_pipeline.py` - Voice processing logic
- ✅ `server/api_server.py` - Voice endpoints (/voice/transcribe, /voice/synthesize)
- ✅ `.env` - Voice configuration
- ✅ `requirements.txt` - Voice dependencies

---

**Ready to use!** Start the server and run the client to choose your mode. 🎉
