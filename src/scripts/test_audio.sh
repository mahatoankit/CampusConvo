#!/bin/bash
# Test audio recording and playback

echo "Testing last recorded audio..."
echo

if [ -f "/tmp/last_recording.wav" ]; then
    echo "✓ Audio file exists: /tmp/last_recording.wav"
    echo "  Size: $(stat -c%s /tmp/last_recording.wav) bytes"
    echo
    echo "Playing audio (you should hear what you said)..."
    echo
    
    # Try different audio players
    if command -v ffplay &> /dev/null; then
        ffplay -nodisp -autoexit -hide_banner /tmp/last_recording.wav 2>/dev/null
    elif command -v aplay &> /dev/null; then
        aplay /tmp/last_recording.wav 2>/dev/null
    elif command -v mpg123 &> /dev/null; then
        mpg123 /tmp/last_recording.wav 2>/dev/null
    else
        echo "No audio player found. Install: sudo apt-get install ffmpeg"
    fi
    
    echo
    echo "If you heard your voice clearly, the recording is working!"
    echo "If not, check your microphone settings."
else
    echo "❌ No recording found at /tmp/last_recording.wav"
    echo "   Record something first with: python client.py"
fi
