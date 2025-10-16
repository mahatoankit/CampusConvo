# 🎙️ Universal Audio Recording - Cross-Platform Support

## ✅ What Changed

The client now **automatically detects** and uses the available audio system on **any Linux machine**:

| System | Tool Used | Installation |
|--------|-----------|--------------|
| **Linux Desktop** | arecord (ALSA) | `sudo apt install alsa-utils` |
| **Termux/Android** | termux-microphone-record | `pkg install termux-api` |
| **Alternative 1** | ffmpeg | `sudo apt install ffmpeg` |
| **Alternative 2** | sox | `sudo apt install sox` |

## 🚀 Quick Start

### 1. Test Your Audio System

```bash
# Check what's available
python -c "from client import detect_audio_system; print(f'Audio: {detect_audio_system()}')"

# Test recording (3 seconds)
python test_audio.py
```

### 2. Run the Client

```bash
# Start server (laptop)
python run_server.py

# Start client (any machine)
python client.py
# Choose: T for text, V for voice
```

## 🎯 How It Works

### Automatic Detection Flow

1. **Checks for Termux** → Uses termux-microphone-record
2. **Checks for arecord** → Uses ALSA (most Linux)
3. **Checks for ffmpeg** → Uses ffmpeg audio capture
4. **Checks for sox** → Uses rec command
5. **None found** → Shows installation instructions

### Recording Commands by System

**ALSA (Linux Desktop):**
```bash
arecord -d 5 -f cd -t wav /tmp/query.wav
```

**Termux (Android):**
```bash
termux-microphone-record -f /sdcard/Download/query.wav -l 5
```

**FFmpeg (Alternative):**
```bash
ffmpeg -f alsa -i default -t 5 /tmp/query.wav
```

**SoX (Alternative):**
```bash
rec -r 16000 -c 1 -b 16 /tmp/query.wav trim 0 5
```

## 📱 Platform-Specific Setup

### Ubuntu/Debian Desktop (Your Laptop)

**Already Installed!** ✅ You have `arecord` and `ffmpeg`

Test it:
```bash
python test_audio.py
```

### Termux (Android Phone)

1. **Install Termux:API app** from F-Droid:
   - https://f-droid.org/en/packages/com.termux.api/

2. **Install termux-api package:**
   ```bash
   pkg install termux-api
   ```

3. **Grant microphone permission:**
   - Android Settings → Apps → Termux:API → Permissions → Microphone

4. **Test:**
   ```bash
   python test_audio.py
   ```

### Other Linux Distributions

**Fedora/RHEL:**
```bash
sudo dnf install alsa-utils
```

**Arch:**
```bash
sudo pacman -S alsa-utils
```

**Alpine:**
```bash
apk add alsa-utils
```

## 🔧 Voice Mode Usage

### Server Side (Laptop)
```bash
python run_server.py
# ✓ Voice pipeline initialized successfully
```

### Client Side (Any Machine)

**Text Mode:**
```bash
python client.py
Choose mode (T/V): t
# Type your questions
```

**Voice Mode:**
```bash
python client.py
Choose mode (T/V): v
# Speak your questions (5-second recording each)
```

## 📊 Audio File Locations

| System | Recording Path |
|--------|----------------|
| Linux Desktop | `/tmp/campusconvo_query.wav` |
| Termux | `/sdcard/Download/query.wav` |

Temporary files are automatically cleaned up after transcription.

## 🐛 Troubleshooting

### No Audio Tool Found

**Error:**
```
❌ No audio recording tool found!
```

**Fix:**
```bash
# Install ALSA (recommended)
sudo apt install alsa-utils

# OR install ffmpeg
sudo apt install ffmpeg
```

### Recording Returns Empty File

**Possible causes:**
1. Microphone not plugged in
2. Wrong audio device selected
3. Microphone muted in system settings

**Test manually:**
```bash
# Test with arecord
arecord -d 3 test.wav
aplay test.wav
```

### Permission Denied (Termux)

**Fix:**
1. Check Termux:API app is installed
2. Grant microphone permission in Android settings
3. Restart Termux

## ✨ Benefits of Universal Support

✅ **Same client code** works on laptop and phone  
✅ **Automatic detection** - no configuration needed  
✅ **Fallback options** - tries multiple tools  
✅ **Clear error messages** with installation instructions  
✅ **Cross-platform** - Linux, Termux, WSL compatible  

## 🎯 What's Next?

- ✅ Audio recording works on any Linux machine
- ✅ Server-side Whisper transcription
- ✅ Automatic audio system detection
- 🔄 Optional: Add audio response playback (TTS)
- 🔄 Optional: Real-time streaming audio

---

**Ready to test!** Run `python test_audio.py` to verify your setup. 🚀
