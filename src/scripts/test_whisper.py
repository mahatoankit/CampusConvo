#!/usr/bin/env python3
"""
Direct test of Whisper transcription
Tests if Whisper can transcribe the recorded audio
"""


import whisper

audio_file = "/tmp/last_recording.wav"

print("=" * 60)
print("Testing Whisper STT directly")
print("=" * 60)

try:
    print("\n1. Loading Whisper model (base)...")
    model = whisper.load_model("base")
    print("   ✓ Model loaded")

    print(f"\n2. Transcribing: {audio_file}")
    result = model.transcribe(audio_file, language="en")

    print("\n3. Results:")
    print(f"   Detected language: {result.get('language', 'unknown')}")
    print(f"   Text: '{result['text'].strip()}'")
    print(f"\n   Full result: {result}")

    if not result["text"].strip():
        print("\n⚠️  WARNING: Transcription is EMPTY!")
        print("    Possible issues:")
        print("    - Audio too quiet")
        print("    - Background noise")
        print("    - Microphone not working properly")
    else:
        print(f"\n✓ SUCCESS! Transcription: '{result['text'].strip()}'")

except FileNotFoundError:
    print(f"\n❌ ERROR: Audio file not found: {audio_file}")
    print("   Record something first: python client.py")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback

    traceback.print_exc()
