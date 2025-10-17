"""
CampusConvo Voice Assistant - Simple Mode
Just run and start talking! No wake word needed.

Usage:
    python src/client_simple.py
    
Commands:
    Just speak your question naturally
    Say "bye" or "exit" to quit
"""

import base64
import os
import sys
import time
import warnings
import wave
from pathlib import Path

# Suppress ALSA warnings
warnings.filterwarnings("ignore")
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

try:
    import ctypes

    ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(
        None, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p
    )

    def _alsa_error_handler(filename, line, function, err, fmt):
        pass

    _c_error_handler = ERROR_HANDLER_FUNC(_alsa_error_handler)
    try:
        _asound = ctypes.cdll.LoadLibrary("libasound.so.2")
        _asound.snd_lib_error_set_handler(_c_error_handler)
    except Exception:
        pass
except Exception:
    pass

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pyaudio  # noqa: E402
import webrtcvad  # noqa: E402

# Import configuration
try:
    from server.config import (
        CLIENT_CHANNELS as CHANNELS,
    )
    from server.config import (
        HTTP_SERVER_URL,
        MAX_RECORDING_DURATION,
        REQUEST_TIMEOUT,
        SILENCE_THRESHOLD,
        TEMP_QUERY_FILE,
        TEMP_RESPONSE_FILE,
        VAD_AGGRESSIVENESS,
    )
except ImportError as e:
    print(f"[ERROR] Failed to import configuration: {e}")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("[ERROR] Voice mode requires 'requests' library")
    print("Install with: pip install requests")
    sys.exit(1)

# Audio settings
FORMAT = pyaudio.paInt16
RECORDING_RATE = 16000
RECORDING_CHUNK = 320


def _get_input_device_index(pa: pyaudio.PyAudio):
    """Pick a reasonable input device index (prefer PulseAudio/default)."""
    env_idx = os.getenv("MIC_DEVICE_INDEX")
    if env_idx is not None:
        try:
            idx = int(env_idx)
            info = pa.get_device_info_by_index(idx)
            if info.get("maxInputChannels", 0) > 0:
                return idx
        except Exception:
            pass

    best = None
    try:
        count = pa.get_device_count()
        for i in range(count):
            info = pa.get_device_info_by_index(i)
            if info.get("maxInputChannels", 0) > 0:
                name = str(info.get("name", "")).lower()
                if "pulse" in name or "default" in name:
                    return i
                if best is None:
                    best = i
    except Exception:
        return None
    return best


def record_audio(output_file=TEMP_QUERY_FILE):
    """Record audio until silence is detected"""
    vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
    audio = pyaudio.PyAudio()

    try:
        device_index = _get_input_device_index(audio)
        if device_index is not None:
            try:
                dinfo = audio.get_device_info_by_index(device_index)
                print(f"[AUDIO] Using input device #{device_index}: {dinfo.get('name')}")
            except Exception:
                print(f"[AUDIO] Using input device #{device_index}")

        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RECORDING_RATE,
            input=True,
            frames_per_buffer=RECORDING_CHUNK,
            input_device_index=device_index if device_index is not None else None,
        )

        print("🎤 Listening... (speak now)")

        frames = []
        speech_detected = False
        silence_frames = 0
        silence_frames_threshold = int(SILENCE_THRESHOLD * RECORDING_RATE / RECORDING_CHUNK)
        max_frames = int(MAX_RECORDING_DURATION * RECORDING_RATE / RECORDING_CHUNK)

        while len(frames) < max_frames:
            try:
                audio_chunk = stream.read(RECORDING_CHUNK, exception_on_overflow=False)
                is_speech = vad.is_speech(audio_chunk, RECORDING_RATE)

                if is_speech:
                    speech_detected = True
                    silence_frames = 0
                    frames.append(audio_chunk)
                elif speech_detected:
                    frames.append(audio_chunk)
                    silence_frames += 1

                    if silence_frames >= silence_frames_threshold:
                        break

            except Exception as e:
                print(f"[WARNING] Audio read error: {e}")
                break

        stream.stop_stream()
        stream.close()
        audio.terminate()

        if not speech_detected or len(frames) < 10:
            print("❌ No speech detected")
            return False

        # Save to WAV file
        with wave.open(output_file, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RECORDING_RATE)
            wf.writeframes(b"".join(frames))

        print(f"✓ Recording complete ({len(frames)} frames)")
        return True

    except Exception as e:
        print(f"[ERROR] Recording failed: {e}")
        audio.terminate()
        return False


def play_audio(audio_file):
    """Play audio file using system player"""
    try:
        if sys.platform == "linux":
            os.system(
                f"mpg123 -q '{audio_file}' 2>/dev/null || ffplay -nodisp -autoexit -hide_banner -loglevel quiet '{audio_file}' 2>/dev/null"
            )
        elif sys.platform == "darwin":
            os.system(f"afplay '{audio_file}'")
        else:
            os.system(f"start {audio_file}")
    except Exception as e:
        print(f"[WARNING] Could not play audio: {e}")


def main():
    print("\n" + "=" * 60)
    print("  ZYRA - Campus Voice Assistant (Simple Mode)")
    print("=" * 60)
    print(f"Server: {HTTP_SERVER_URL}")
    print("=" * 60)
    print("\n[OK] Assistant ready!")
    print("\n  • Just speak your question when prompted")
    print("  • Say 'bye' or 'exit' to quit")
    print("\n  Starting conversation...")
    print("=" * 60)

    # Initial greeting
    print("\n[ZYRA] Hello there, how may I assist you today?\n")

    try:
        greeting_response = requests.post(
            f"{HTTP_SERVER_URL}/voice/synthesize",
            json={"text": "Hello there, how may I assist you today?"},
            timeout=REQUEST_TIMEOUT,
        )

        if greeting_response.status_code == 200:
            result = greeting_response.json()
            if result.get("status") == "success":
                audio_b64 = result.get("audio", "")
                audio_data = base64.b64decode(audio_b64)
                with open(TEMP_RESPONSE_FILE, "wb") as f:
                    f.write(audio_data)
                play_audio(TEMP_RESPONSE_FILE)
    except Exception as e:
        print(f"[WARNING] Could not play greeting: {e}")

    conversation_count = 0

    while True:
        try:
            conversation_count += 1
            print(f"\n{'─'*60}")
            print(f"Question #{conversation_count}")
            print(f"{'─'*60}")

            # Record user query
            if not record_audio(TEMP_QUERY_FILE):
                print("No speech detected, please try again...")
                continue

            # Transcribe audio
            print("📝 Transcribing...")
            with open(TEMP_QUERY_FILE, "rb") as f:
                audio_data = f.read()
                audio_b64 = base64.b64encode(audio_data).decode("utf-8")

            transcribe_response = requests.post(
                f"{HTTP_SERVER_URL}/voice/transcribe",
                json={"audio": audio_b64},
                timeout=REQUEST_TIMEOUT,
            )

            if transcribe_response.status_code != 200:
                print("[ERROR] Transcription failed")
                continue

            transcribe_result = transcribe_response.json()
            if transcribe_result.get("status") != "success":
                print("[ERROR] Transcription failed")
                continue

            query_text = transcribe_result.get("text", "").strip()
            print(f"\n[YOU] {query_text}")

            # Check for exit commands
            if any(
                exit_word in query_text.lower() for exit_word in ["bye", "exit", "goodbye", "quit"]
            ):
                print("\n[ZYRA] Goodbye! Have a great day!")

                goodbye_response = requests.post(
                    f"{HTTP_SERVER_URL}/voice/synthesize",
                    json={"text": "Goodbye! Have a great day!"},
                    timeout=REQUEST_TIMEOUT,
                )

                if goodbye_response.status_code == 200:
                    result = goodbye_response.json()
                    if result.get("status") == "success":
                        audio_b64 = result.get("audio", "")
                        audio_data = base64.b64decode(audio_b64)
                        with open(TEMP_RESPONSE_FILE, "wb") as f:
                            f.write(audio_data)
                        play_audio(TEMP_RESPONSE_FILE)

                print("\n" + "=" * 60)
                print("  Session ended. Thank you!")
                print("=" * 60 + "\n")
                break

            # Get answer from server
            print("🤔 Thinking...")
            query_response = requests.post(
                f"{HTTP_SERVER_URL}/voice/query", json={"audio": audio_b64}, timeout=REQUEST_TIMEOUT
            )

            if query_response.status_code != 200:
                print("[ERROR] Query failed")
                continue

            query_result = query_response.json()
            if query_result.get("status") != "success":
                print(f"[ERROR] {query_result.get('error', 'Unknown error')}")
                continue

            answer_text = query_result.get("answer", "")
            print(f"\n[ZYRA] {answer_text}\n")

            # Play response audio
            audio_b64 = query_result.get("audio", "")
            if audio_b64:
                audio_data = base64.b64decode(audio_b64)
                with open(TEMP_RESPONSE_FILE, "wb") as f:
                    f.write(audio_data)
                play_audio(TEMP_RESPONSE_FILE)

            # Clean up temp files
            try:
                os.remove(TEMP_QUERY_FILE)
                os.remove(TEMP_RESPONSE_FILE)
            except Exception:
                pass

        except KeyboardInterrupt:
            print("\n\n[SHUTDOWN] Goodbye!")
            break
        except requests.exceptions.ConnectionError:
            print(f"\n[ERROR] Cannot connect to server at {HTTP_SERVER_URL}")
            print("        Make sure server is running: python run_server.py")
            time.sleep(2)
        except Exception as e:
            print(f"\n[ERROR] {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()
