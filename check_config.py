#!/usr/bin/env python3
"""
Quick configuration checker for CampusConvo
"""
import sys
sys.path.insert(0, '.')

from server import config
import torch

print("=" * 60)
print("CAMPUSCONVO CONFIGURATION")
print("=" * 60)
print()
print("🔊 TEXT-TO-SPEECH (TTS)")
print(f"   Engine: {config.TTS_ENGINE}")
print(f"   Voice:  {config.TTS_EDGE_VOICE}")
print()
print("🎤 SPEECH-TO-TEXT (STT)")
print(f"   Model:  {config.STT_MODEL}")
print()
print("🖥️  GPU ACCELERATION")
print(f"   Enabled in config: {config.USE_GPU}")
print(f"   CUDA available:    {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   GPU name:          {torch.cuda.get_device_name(0)}")
    print(f"   CUDA version:      {torch.version.cuda}")
else:
    print("   ⚠️  No GPU detected")
print()
print("=" * 60)
print()

if config.TTS_ENGINE == "edge-tts":
    print("✅ GOOD: Using edge-tts (natural voice)")
elif config.TTS_ENGINE == "gtts":
    print("⚠️  WARNING: Using gtts (robotic voice)")
    print("   To fix: Edit server/config.py and change TTS_ENGINE to 'edge-tts'")
print()

if torch.cuda.is_available() and config.USE_GPU:
    print("✅ GOOD: GPU will be used for Whisper")
elif torch.cuda.is_available() and not config.USE_GPU:
    print("⚠️  WARNING: GPU available but disabled in config")
else:
    print("ℹ️  INFO: Running on CPU (no GPU)")
print()
