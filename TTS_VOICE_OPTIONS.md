# 🔊 Text-to-Speech (TTS) Voice Options

## Quick Start - Better Voice Quality

Your system is now configured to use **Microsoft Edge TTS** (much more natural than gTTS).

### Default Voice
- **en-US-AriaNeural** (Female, American, Very Natural)

### Popular Voice Options

#### English (US)
```bash
# Female voices
export TTS_EDGE_VOICE="en-US-AriaNeural"      # Default, warm and friendly
export TTS_EDGE_VOICE="en-US-JennyNeural"     # Clear, professional
export TTS_EDGE_VOICE="en-US-MichelleNeural"  # Energetic

# Male voices
export TTS_EDGE_VOICE="en-US-GuyNeural"       # Deep, mature
export TTS_EDGE_VOICE="en-US-ChristopherNeural" # Casual, friendly
export TTS_EDGE_VOICE="en-US-EricNeural"      # Professional
```

#### English (UK)
```bash
export TTS_EDGE_VOICE="en-GB-SoniaNeural"     # British female
export TTS_EDGE_VOICE="en-GB-RyanNeural"      # British male
```

#### English (India)
```bash
export TTS_EDGE_VOICE="en-IN-NeerjaNeural"    # Indian female
export TTS_EDGE_VOICE="en-IN-PrabhatNeural"   # Indian male
```

## How to Change Voice

### Method 1: Environment Variable (Temporary)
```bash
# Set voice before starting server
export TTS_EDGE_VOICE="en-US-GuyNeural"
make run-server
```

### Method 2: Edit config.py (Permanent)
Edit `server/config.py` line 64:
```python
TTS_EDGE_VOICE = os.getenv("TTS_EDGE_VOICE", "en-US-GuyNeural")  # Change this
```

## GPU Acceleration for Whisper

Your GPU (NVIDIA GeForce MX350) should be automatically detected. When you start the server, look for:

```
🚀 GPU detected: NVIDIA GeForce MX350
   CUDA version: 12.1
   Using GPU for Whisper acceleration
[OK] Whisper STT initialized successfully on CUDA
```

If you see **"⚠️ GPU requested but not available"**, restart your server:
```bash
# Kill any existing server processes
pkill -f run_server.py

# Start fresh
make run-server
```

## Performance Comparison

| TTS Engine | Quality | Speed | Internet | Notes |
|------------|---------|-------|----------|-------|
| **edge-tts** (current) | ⭐⭐⭐⭐⭐ | Fast | Required | Most natural, recommended |
| gtts (old) | ⭐⭐ | Fast | Required | Robotic, basic |
| piper | ⭐⭐⭐⭐ | Very Fast | Not needed | Offline, good quality |
| coqui | ⭐⭐⭐⭐⭐ | Slow | Not needed | Best quality, heavy |

## Test Voice Quality

Listen to samples at: https://speech.microsoft.com/portal/voicegallery

## Troubleshooting

### Still hearing robotic voice?
1. **Restart the server** - changes only apply on server restart
2. Check server logs - should say "Using TTS engine: edge-tts"
3. Verify edge-tts is installed: `./env/bin/pip show edge-tts`

### GPU not detected?
1. Restart server completely (Ctrl+C, then `make run-server`)
2. Check CUDA: `./env/bin/python -c "import torch; print(torch.cuda.is_available())"`
3. Should print `True`

### Want even faster responses?
Use a smaller Whisper model for STT:
```bash
export STT_MODEL="tiny"  # Fastest, less accurate
export STT_MODEL="base"  # Default, good balance
export STT_MODEL="small" # Better accuracy, slower
```

## Current Configuration

Check your active settings:
```bash
./env/bin/python -c "from server import config; print(f'TTS: {config.TTS_ENGINE}'); print(f'Voice: {config.TTS_EDGE_VOICE}'); print(f'GPU: {config.USE_GPU}')"
```
