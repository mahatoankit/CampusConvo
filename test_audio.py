#!/usr/bin/env python3
"""
Quick audio system test script
Tests if audio recording works on your system
"""

from client import detect_audio_system, record_audio
import os

print("="*60)
print("  Audio System Test")
print("="*60)

# Detect audio system
audio_system = detect_audio_system()
print(f"\n[OK] Detected audio system: {audio_system}")

if audio_system is None:
    print("\n[ERROR] No audio recording tool found!")
    print("\nInstall options:")
    print("  - Ubuntu/Debian: sudo apt install alsa-utils")
    print("  - Alternative: sudo apt install ffmpeg")
    print("  - Termux: pkg install termux-api")
    exit(1)

print(f"\n Using: {audio_system}")
print("\nThis will record 3 seconds of audio to test your microphone.")
input("Press Enter to start recording...")

# Test recording
output_file = "/tmp/campusconvo_test.wav"
result = record_audio(duration=3, output_file=output_file)

if result:
    print(f"\n[OK] Success! Audio saved to: {result}")
    
    # Check file size
    size = os.path.getsize(result)
    print(f" File size: {size:,} bytes")
    
    if size < 1000:
        print("[WARNING]  Warning: File is very small. Check your microphone.")
    else:
        print("[OK] File size looks good!")
    
    print(f"\nYou can play it with:")
    if audio_system == "alsa":
        print(f"  aplay {result}")
    elif audio_system == "ffmpeg":
        print(f"  ffplay {result}")
    
    # Cleanup option
    cleanup = input("\nDelete test file? (y/n): ").lower()
    if cleanup == 'y':
        os.remove(result)
        print("[OK] Test file deleted")
else:
    print("\n[ERROR] Recording failed!")
    exit(1)

print("\n" + "="*60)
print("[OK] Audio system is working! You can use voice mode.")
print("="*60)
