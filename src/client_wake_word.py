"""
CampusConvo Voice Assistant with Wake Word
Voice-only assistant with continuous local wake word detection (like Alexa/Siri)

Usage:
    python src/client_wake_word.py    # Start voice assistant (say "Hello Zyra" to activate)
    
Wake Word:
    Say "Hello Zyra" to start a conversation
    Say "Bye Zyra" to exit
    
Network Usage:
    Update SERVER_IP in server/config.py when changing networks
"""

import asyncio
import base64
import json
import os
import struct
import subprocess
import sys
import threading
import time
import warnings
import wave
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pyaudio  # noqa: E402
import webrtcvad  # noqa: E402
import websockets  # noqa: E402

# Optional Porcupine import (requires API key)
try:
    import pvporcupine

    PORCUPINE_AVAILABLE = True
except ImportError:
    PORCUPINE_AVAILABLE = False

# Suppress ALSA warnings
warnings.filterwarnings("ignore")
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

try:
    import ctypes

    ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(
        None, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p
    )

    def py_error_handler(filename, line, function, err, fmt):
        pass

    c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
    try:
        asound = ctypes.cdll.LoadLibrary("libasound.so.2")
        asound.snd_lib_error_set_handler(c_error_handler)
    except Exception:
        pass
except Exception:
    pass

# Import all configuration from server/config.py
try:
    from server.config import (
        CLIENT_CHANNELS as CHANNELS,
    )
    from server.config import (
        EXIT_COMMANDS,
        GOODBYE_MESSAGE,
        GREETING_MESSAGE,
        HTTP_SERVER_URL,
        # MAX_CONSECUTIVE_ERRORS,  # unused
        MAX_RECORDING_DURATION,
        PORCUPINE_ACCESS_KEY,
        PORCUPINE_KEYWORDS,
        QUERY_MAX_DURATION,
        QUERY_SILENCE_THRESHOLD,
        REQUEST_TIMEOUT,
        SILENCE_THRESHOLD,
        TEMP_GOODBYE_FILE,
        TEMP_GREETING_FILE,
        TEMP_QUERY_FILE,
        TEMP_RESPONSE_FILE,
        VAD_AGGRESSIVENESS,
    )
    from server.config import (
        WEBSOCKET_URL as SERVER_URL,
    )
except ImportError as e:
    print(f"[ERROR] Failed to import configuration: {e}")
    print("Please ensure server/config.py exists and contains all required settings")
    sys.exit(1)

try:
    import requests

    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("[ERROR] Voice mode requires 'requests' library")
    print("Install with: pip install requests")
    sys.exit(1)

# PyAudio format constant
FORMAT = pyaudio.paInt16

# Porcupine wake word detection settings
PORCUPINE_RATE = 16000
PORCUPINE_FRAME_LENGTH = 512

# Recording settings for user queries
RECORDING_RATE = 16000
RECORDING_CHUNK = 320


class SimpleWakeWordDetector:
    """
    Simple wake word detector using continuous speech recognition.
    No API key required! Uses local VAD + server's Whisper STT.
    """

    def __init__(self, wake_words=None, on_wake_word_detected=None):
        if wake_words is None:
            wake_words = ["hello zyra"]
        self.pa = None
        self.audio_stream = None
        self.is_running = False
        self.thread = None
        self.on_wake_word_detected = on_wake_word_detected
        self.wake_words = [w.lower() for w in wake_words]
        self.vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)

    def start(self):
        if self.is_running:
            return

        try:
            self.pa = pyaudio.PyAudio()
            self.audio_stream = self.pa.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RECORDING_RATE,
                input=True,
                frames_per_buffer=RECORDING_CHUNK,
            )

            self.is_running = True
            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()

        except Exception as e:
            print(f"[ERROR] Failed to start wake word detector: {e}")
            self.cleanup()

    def _listen_loop(self):
        """Continuously listen for speech and check for wake words"""
        while self.is_running:
            try:
                # Record a short audio snippet when voice is detected
                frames = []
                speech_detected = False
                silence_frames = 0
                max_frames = int(3 * RECORDING_RATE / RECORDING_CHUNK)  # 3 seconds max

                # Wait for speech
                for _ in range(max_frames):
                    if not self.is_running:
                        return

                    audio_chunk = self.audio_stream.read(
                        RECORDING_CHUNK, exception_on_overflow=False
                    )
                    is_speech = self.vad.is_speech(audio_chunk, RECORDING_RATE)

                    if is_speech:
                        speech_detected = True
                        frames.append(audio_chunk)
                        silence_frames = 0
                    elif speech_detected:
                        frames.append(audio_chunk)
                        silence_frames += 1

                        # Stop after 0.5 seconds of silence
                        if silence_frames > int(0.5 * RECORDING_RATE / RECORDING_CHUNK):
                            break

                # If we got speech, check if it's a wake word
                if speech_detected and len(frames) > 5:
                    print("🎤 Speech detected, checking for wake word...", end=" ", flush=True)

                    # Save audio to temp file
                    temp_file = "/tmp/wake_word_check.wav"
                    with wave.open(temp_file, "wb") as wf:
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(self.pa.get_sample_size(FORMAT))
                        wf.setframerate(RECORDING_RATE)
                        wf.writeframes(b"".join(frames))

                    # Send to server for transcription
                    try:
                        with open(temp_file, "rb") as f:
                            audio_data = f.read()
                            audio_b64 = base64.b64encode(audio_data).decode("utf-8")

                        response = requests.post(
                            f"{HTTP_SERVER_URL}/voice/transcribe",
                            json={"audio": audio_b64},
                            timeout=5,
                        )

                        if response.status_code == 200:
                            result = response.json()
                            if result.get("status") == "success":
                                text = result.get("text", "").lower().strip()
                                print(f"heard: '{text}'")

                                # Check if any wake word is in the transcription
                                for wake_word in self.wake_words:
                                    if wake_word in text:
                                        print(f"✓ Wake word '{wake_word}' detected!")
                                        if self.on_wake_word_detected:
                                            self.on_wake_word_detected()
                                        break
                            else:
                                print("(no speech)")
                        else:
                            print("(server error)")

                        # Clean up
                        try:
                            os.remove(temp_file)
                        except Exception:
                            pass

                    except Exception:
                        pass  # Silently continue listening

            except Exception as e:
                if self.is_running:
                    print(f"[WARNING] Wake word detection error: {e}")
                time.sleep(0.1)

    def pause(self):
        self.is_running = False

    def resume(self):
        if not self.is_running and self.audio_stream:
            self.is_running = True
            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()

    def cleanup(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.audio_stream:
            try:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            except Exception:
                pass
        if self.pa:
            try:
                self.pa.terminate()
            except Exception:
                pass


class WakeWordDetector:
    """Porcupine-based wake word detector (requires API key)"""

    def __init__(self, keywords=None, on_wake_word_detected=None, access_key=None):
        if keywords is None:
            keywords = ["hey google"]
        self.porcupine = None
        self.pa = None
        self.audio_stream = None
        self.is_running = False
        self.thread = None
        self.on_wake_word_detected = on_wake_word_detected
        self.keywords = keywords
        self.access_key = access_key

    def start(self):
        if self.is_running:
            return

        try:
            # Check if access key is provided
            if not self.access_key:
                raise ValueError(
                    "Porcupine access_key is required. Get a free key at https://console.picovoice.ai/"
                )

            self.porcupine = pvporcupine.create(access_key=self.access_key, keywords=self.keywords)
            self.pa = pyaudio.PyAudio()
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length,
            )

            self.is_running = True
            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()

        except Exception as e:
            print(f"[ERROR] Failed to start wake word detector: {e}")
            self.cleanup()

    def _listen_loop(self):
        while self.is_running:
            try:
                pcm = self.audio_stream.read(
                    self.porcupine.frame_length, exception_on_overflow=False
                )
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

                keyword_index = self.porcupine.process(pcm)

                if keyword_index >= 0:
                    if self.on_wake_word_detected:
                        self.on_wake_word_detected()

            except Exception as e:
                if self.is_running:
                    print(f"[WARNING] Wake word detection error: {e}")
                break

    def pause(self):
        self.is_running = False

    def resume(self):
        if not self.is_running and self.audio_stream:
            self.is_running = True
            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()

    def cleanup(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        if self.porcupine:
            self.porcupine.delete()
        if self.pa:
            self.pa.terminate()


def record_audio_continuous(output_file=None, silence_threshold=None, max_duration=None):
    if output_file is None:
        output_file = TEMP_QUERY_FILE

    if silence_threshold is None:
        silence_threshold = SILENCE_THRESHOLD

    if max_duration is None:
        max_duration = MAX_RECORDING_DURATION

    vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
    audio = pyaudio.PyAudio()

    try:
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RECORDING_RATE,
            input=True,
            frames_per_buffer=RECORDING_CHUNK,
        )

        print("🎤 Listening... (speak now)")

        frames = []
        speech_detected = False
        silence_frames = 0
        silence_frames_threshold = int(silence_threshold * RECORDING_RATE / RECORDING_CHUNK)
        max_frames = int(max_duration * RECORDING_RATE / RECORDING_CHUNK)

        while len(frames) < max_frames:
            frame = stream.read(RECORDING_CHUNK, exception_on_overflow=False)

            is_speech = vad.is_speech(frame, RECORDING_RATE)

            if is_speech:
                if not speech_detected:
                    print("🗣️  Speech detected...")
                    speech_detected = True
                frames.append(frame)
                silence_frames = 0
            elif speech_detected:
                frames.append(frame)
                silence_frames += 1

                if silence_frames >= silence_frames_threshold:
                    print("✓ Speech ended (silence detected)")
                    break

        stream.stop_stream()
        stream.close()

        if not speech_detected:
            print("[INFO] No speech detected")
            return None

        wf = wave.open(output_file, "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RECORDING_RATE)
        wf.writeframes(b"".join(frames))
        wf.close()

        print(f"[OK] Recording saved ({len(frames) * RECORDING_CHUNK / RECORDING_RATE:.1f}s)")
        return output_file

    except Exception as e:
        print(f"[ERROR] Recording failed: {e}")
        return None
    finally:
        audio.terminate()


def play_audio(audio_file):
    if not os.path.exists(audio_file):
        print(f"[WARNING] Audio file not found: {audio_file}")
        return

    try:
        is_mp3 = audio_file.endswith(".mp3")

        if is_mp3:
            if subprocess.run("which mpg123", shell=True, capture_output=True).returncode == 0:
                cmd = f"mpg123 -q {audio_file} 2>/dev/null"
            else:
                print("[WARNING] MP3 player not found. Install: sudo apt install mpg123")
                return
        else:
            if subprocess.run("which aplay", shell=True, capture_output=True).returncode == 0:
                cmd = f"aplay -q {audio_file} 2>/dev/null"
            else:
                print("[WARNING] WAV player not found. Install: sudo apt install alsa-utils")
                return

        subprocess.run(cmd, shell=True)
    except Exception as e:
        print(f"[WARNING] Could not play audio: {e}")


async def send_query_and_get_response(query: str, server_url: str = SERVER_URL) -> str:
    try:
        async with websockets.connect(server_url) as websocket:
            message = {"query": query, "top_k": 5}
            await websocket.send(json.dumps(message))

            response_text = ""

            while True:
                response = await websocket.recv()
                data = json.loads(response)
                status = data.get("status")

                if status == "processing":
                    print(f"[PROCESSING] {data.get('message', 'Processing...')}")

                elif status == "complete":
                    response_text = data.get("response", "No response")
                    print("\n[OK] Answer:")
                    print(f"{response_text}")

                    sources = data.get("sources", [])
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


wake_word_event = threading.Event()


async def wake_word_voice_assistant(use_simple_detector=False):
    print("=" * 60)
    print("  ZYRA - Your Campus Voice Assistant")
    print("=" * 60)
    print(f"Server: {HTTP_SERVER_URL}")

    if use_simple_detector:
        print("Wake Word: 'Hello Zyra' (simple mode - no API key needed)")
    else:
        print("Wake Word: 'Hey Google' (Porcupine mode)")

    print("Exit Command: 'Bye Zyra'")
    print("=" * 60)
    print("\n[OK] Assistant ready!")

    if use_simple_detector:
        print("\n  • Say 'Hello Zyra' to start a conversation")
    else:
        print("\n  • Say 'Hey Google' to start a conversation")

    print("  • After activation, speak your question")
    print("  • Say 'Bye Zyra' to exit")
    print("\n  Example conversation:")

    if use_simple_detector:
        print("    You:  'Hello Zyra'")
    else:
        print("    You:  'Hey Google'")

    print("    Zyra: 'Hello there, how may I assist you today?'")
    print("    You:  'Where is Sunway College located?'")
    print("    Zyra: [answers your question]")
    print("    You:  'Bye Zyra'")
    print("    Zyra: 'Goodbye! Have a great day!'")
    print("\n  Press Ctrl+C to force exit")
    print("-" * 60)

    def on_wake_word():
        wake_word_event.set()

    # Create appropriate detector
    if use_simple_detector:
        detector = SimpleWakeWordDetector(
            wake_words=["hello zyra", "hey zyra"], on_wake_word_detected=on_wake_word
        )
    else:
        detector = WakeWordDetector(
            keywords=PORCUPINE_KEYWORDS,
            on_wake_word_detected=on_wake_word,
            access_key=PORCUPINE_ACCESS_KEY,
        )

    detector.start()

    print("\n🎧 Listening for wake word in background...")

    # Track consecutive errors if needed (not used currently)

    try:
        while True:
            wake_word_event.wait()
            wake_word_event.clear()

            detector.pause()

            print("\n✓ [ACTIVATED] Wake word detected!")

            print(f"[ZYRA] {GREETING_MESSAGE}")

            try:
                greeting_tts_response = requests.post(
                    f"{HTTP_SERVER_URL}/voice/synthesize",
                    json={"text": GREETING_MESSAGE},
                    timeout=REQUEST_TIMEOUT,
                )

                if greeting_tts_response.status_code == 200:
                    greeting_tts_result = greeting_tts_response.json()
                    if greeting_tts_result.get("status") == "success":
                        greeting_audio_b64 = greeting_tts_result.get("audio", "")
                        greeting_audio_data = base64.b64decode(greeting_audio_b64)

                        with open(TEMP_GREETING_FILE, "wb") as f:
                            f.write(greeting_audio_data)

                        play_audio(TEMP_GREETING_FILE)

                        try:
                            os.remove(TEMP_GREETING_FILE)
                        except Exception:
                            pass
            except Exception as e:
                print(f"[WARNING] Could not play greeting: {e}")

            print("\n🎤 Now listening for your question...")

            query_audio = record_audio_continuous(
                silence_threshold=QUERY_SILENCE_THRESHOLD, max_duration=QUERY_MAX_DURATION
            )

            if not query_audio or not os.path.exists(query_audio):
                print("[WARNING] Could not record question. Resuming wake word detection...")
                detector.resume()
                continue

            print("[PROCESSING] Transcribing your question...")

            try:
                with open(query_audio, "rb") as f:
                    query_audio_data = f.read()
                query_audio_b64 = base64.b64encode(query_audio_data).decode("utf-8")

                query_response = requests.post(
                    f"{HTTP_SERVER_URL}/voice/transcribe",
                    json={"audio": query_audio_b64},
                    timeout=REQUEST_TIMEOUT,
                )

                if query_response.status_code != 200:
                    print(f"[WARNING] Question transcription failed: {query_response.status_code}")
                    detector.resume()
                    continue

                query_result = query_response.json()
                if query_result.get("status") != "success":
                    print(f"[WARNING] Question transcription error: {query_result.get('error')}")
                    detector.resume()
                    continue

                query = query_result.get("transcription", "").strip()

                if not query or len(query) < 3:
                    print("[INFO] No question detected. Resuming wake word detection...")
                    detector.resume()
                    continue

                print(f"[QUERY] {query}")

                query_lower = query.lower()
                if any(cmd in query_lower for cmd in EXIT_COMMANDS):
                    print(f"[ZYRA] {GOODBYE_MESSAGE}")

                    try:
                        goodbye_tts_response = requests.post(
                            f"{HTTP_SERVER_URL}/voice/synthesize",
                            json={"text": GOODBYE_MESSAGE},
                            timeout=REQUEST_TIMEOUT,
                        )

                        if goodbye_tts_response.status_code == 200:
                            goodbye_tts_result = goodbye_tts_response.json()
                            if goodbye_tts_result.get("status") == "success":
                                goodbye_audio_b64 = goodbye_tts_result.get("audio", "")
                                goodbye_audio_data = base64.b64decode(goodbye_audio_b64)

                                with open(TEMP_GOODBYE_FILE, "wb") as f:
                                    f.write(goodbye_audio_data)

                                play_audio(TEMP_GOODBYE_FILE)

                                try:
                                    os.remove(TEMP_GOODBYE_FILE)
                                except Exception:
                                    pass
                    except Exception as e:
                        print(f"[WARNING] Could not play goodbye message: {e}")

                    print("\n[SHUTDOWN] Exiting assistant...")
                    detector.cleanup()
                    return

                print("[PROCESSING] Getting response...")
                response_text = await send_query_and_get_response(query)

                if response_text:
                    print("\n[SPEAKING] Converting to speech...")
                    try:
                        tts_response = requests.post(
                            f"{HTTP_SERVER_URL}/voice/synthesize",
                            json={"text": response_text},
                            timeout=REQUEST_TIMEOUT,
                        )

                        if tts_response.status_code == 200:
                            tts_result = tts_response.json()
                            if tts_result.get("status") == "success":
                                audio_b64 = tts_result.get("audio", "")
                                audio_data = base64.b64decode(audio_b64)

                                with open(TEMP_RESPONSE_FILE, "wb") as f:
                                    f.write(audio_data)

                                play_audio(TEMP_RESPONSE_FILE)

                                try:
                                    os.remove(TEMP_RESPONSE_FILE)
                                except Exception:
                                    pass
                            else:
                                print(f"[WARNING] TTS failed: {tts_result.get('error')}")
                        else:
                            print(f"[WARNING] TTS request failed: {tts_response.status_code}")
                    except Exception as e:
                        print(f"[WARNING] Audio playback error: {e}")

                print("\n🎧 Resuming wake word detection...")
                detector.resume()

            except requests.exceptions.ConnectionError:
                print(f"[ERROR] Cannot connect to server at {HTTP_SERVER_URL}")
                print("        Make sure server is running: python run_server.py")
                detector.resume()
                time.sleep(2)
            except Exception as e:
                print(f"[ERROR] Processing error: {e}")
                detector.resume()
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[SHUTDOWN] Goodbye!")
        detector.cleanup()
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        detector.cleanup()


def main():
    print("\n" + "=" * 60)
    print("  Starting ZYRA Voice Assistant...")
    print("=" * 60)

    use_simple_detector = False

    # Check if we should use simple detector (no API key needed)
    if not PORCUPINE_AVAILABLE:
        print("\n[INFO] Porcupine not installed, using simple wake word detector")
        use_simple_detector = True
    elif not PORCUPINE_ACCESS_KEY:
        print("\n[INFO] No Porcupine API key configured")
        print("[INFO] Using simple wake word detector (no API key needed)")
        print("\n💡 Want faster wake word detection?")
        print("   Get a FREE Porcupine key at: https://console.picovoice.ai/")
        use_simple_detector = True
    else:
        # Try to test Porcupine
        try:
            porcupine_test = pvporcupine.create(
                access_key=PORCUPINE_ACCESS_KEY, keywords=PORCUPINE_KEYWORDS
            )
            porcupine_test.delete()
            print("\n[OK] Wake word engine: Picovoice Porcupine")
            print(f"[OK] Wake word keywords: {', '.join(PORCUPINE_KEYWORDS)}")
        except Exception as e:
            print(f"\n[WARNING] Porcupine initialization failed: {e}")
            print("[INFO] Falling back to simple wake word detector")
            use_simple_detector = True

    if use_simple_detector:
        print("[OK] Wake word engine: Simple STT-based detector")
        print("[OK] Wake words: 'Hello Zyra', 'Hey Zyra'")

    print("[OK] Starting voice assistant...\n")

    asyncio.run(wake_word_voice_assistant(use_simple_detector=use_simple_detector))


if __name__ == "__main__":
    main()
