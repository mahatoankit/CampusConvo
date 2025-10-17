#!/usr/bin/env python3
"""
Test microphone input and audio recording
Helps diagnose audio issues with CampusConvo
"""

import sys
import wave
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pyaudio  # noqa: E402
import webrtcvad  # noqa: E402

# Audio settings (match client settings)
FORMAT = pyaudio.paInt16
RECORDING_RATE = 16000
RECORDING_CHUNK = 320
CHANNELS = 1


def list_audio_devices():
    """List all available audio input devices"""
    print("\n" + "=" * 60)
    print("Available Audio Input Devices:")
    print("=" * 60)

    pa = pyaudio.PyAudio()

    for i in range(pa.get_device_count()):
        try:
            info = pa.get_device_info_by_index(i)
            max_inputs = info.get("maxInputChannels", 0)
            if max_inputs > 0:
                name = info.get("name", "Unknown")
                print(f"\n  Device #{i}: {name}")
                print(f"    Max Input Channels: {max_inputs}")
                print(f"    Default Sample Rate: {info.get('defaultSampleRate', 'N/A')}")
        except Exception as e:
            print(f"  Device #{i}: Error - {e}")

    pa.terminate()
    print("\n" + "=" * 60 + "\n")


def test_recording(device_index=None, duration=3):
    """Test recording from microphone"""
    print(f"\nTesting {duration}s recording...")
    if device_index is not None:
        print(f"Using device #{device_index}")
    else:
        print("Using default device")

    pa = pyaudio.PyAudio()

    try:
        stream = pa.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RECORDING_RATE,
            input=True,
            frames_per_buffer=RECORDING_CHUNK,
            input_device_index=device_index,
        )

        print("\n🎤 Recording... SPEAK NOW!")

        frames = []
        num_chunks = int(RECORDING_RATE / RECORDING_CHUNK * duration)

        for i in range(num_chunks):
            data = stream.read(RECORDING_CHUNK, exception_on_overflow=False)
            frames.append(data)

            # Show progress
            if (i + 1) % 50 == 0:
                print(".", end="", flush=True)

        print("\n✓ Recording complete!")

        stream.stop_stream()
        stream.close()

        # Save to file
        output_file = "/tmp/mic_test.wav"
        with wave.open(output_file, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(pa.get_sample_size(FORMAT))
            wf.setframerate(RECORDING_RATE)
            wf.writeframes(b"".join(frames))

        print(f"✓ Saved to: {output_file}")
        print(f"  File size: {len(b''.join(frames))} bytes")
        print(f"\nTest playback with: aplay {output_file}")

    except Exception as e:
        print(f"❌ Recording failed: {e}")
    finally:
        pa.terminate()


def test_vad(device_index=None, duration=5):
    """Test Voice Activity Detection"""
    print(f"\nTesting VAD for {duration}s...")
    print("Speak to see voice activity detection in action!")

    pa = pyaudio.PyAudio()
    vad = webrtcvad.Vad(3)  # Max aggressiveness

    try:
        stream = pa.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RECORDING_RATE,
            input=True,
            frames_per_buffer=RECORDING_CHUNK,
            input_device_index=device_index,
        )

        print("\n🎤 Listening...")

        num_chunks = int(RECORDING_RATE / RECORDING_CHUNK * duration)
        speech_count = 0

        for i in range(num_chunks):
            data = stream.read(RECORDING_CHUNK, exception_on_overflow=False)
            is_speech = vad.is_speech(data, RECORDING_RATE)

            if is_speech:
                print("🗣️ ", end="", flush=True)
                speech_count += 1
            else:
                print("_ ", end="", flush=True)

            if (i + 1) % 20 == 0:
                print()

        print("\n\n✓ VAD test complete!")
        print(
            f"  Speech detected in {speech_count}/{num_chunks} chunks ({speech_count/num_chunks*100:.1f}%)"
        )

        if speech_count == 0:
            print("\n⚠️  WARNING: No speech detected!")
            print("  - Try speaking louder")
            print("  - Check microphone volume settings")
            print("  - Try a different device with: MIC_DEVICE_INDEX=N")

        stream.stop_stream()
        stream.close()

    except Exception as e:
        print(f"❌ VAD test failed: {e}")
    finally:
        pa.terminate()


def main():
    """Main test menu"""
    print("\n" + "=" * 60)
    print("  CampusConvo Microphone Test Utility")
    print("=" * 60)

    # List devices
    list_audio_devices()

    # Get device choice
    device_str = input("Enter device number to test (or press Enter for default): ").strip()
    device_index = int(device_str) if device_str else None

    print("\n" + "=" * 60)
    print("Select Test:")
    print("=" * 60)
    print("  1. Simple Recording Test (3s)")
    print("  2. Voice Activity Detection Test (5s)")
    print("  3. Both")
    print("=" * 60)

    choice = input("\nYour choice [1-3]: ").strip()

    if choice == "1":
        test_recording(device_index)
    elif choice == "2":
        test_vad(device_index)
    elif choice == "3":
        test_recording(device_index)
        print("\n")
        test_vad(device_index)
    else:
        print("Invalid choice")

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
