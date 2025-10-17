# 🎛️ Unified Configuration System

## Overview

All CampusConvo settings are now managed through a **single configuration file**: `config.yaml`

This eliminates configuration conflicts, makes settings easy to find and modify, and provides a clear source of truth.

---

## 📍 Quick Start

### 1. **Edit Settings**
Open `config.yaml` and modify any settings you want:

```yaml
# Example: Change voice to male British accent
tts:
  engine: "edge-tts"
  edge:
    voice: "en-GB-RyanNeural"  # British male voice

# Example: Use smaller/faster STT model
stt:
  model: "base"  # Faster than medium, still accurate

# Example: Change server IP when network changes
server:
  server_ip: "192.168.1.100"  # Update this
```

### 2. **Test Configuration**
```bash
./env/bin/python test_config.py
```

### 3. **Restart Server**
Changes take effect on server restart:
```bash
make run-server
```

---

## 📁 Configuration Structure

### 🔧 **Server Settings**
```yaml
server:
  host: "0.0.0.0"              # Listen address
  port: 8000                   # Server port
  server_ip: "192.168.254.135" # Your IP (UPDATE WHEN NETWORK CHANGES!)
```

### 🎤 **Speech-to-Text (Whisper)**
```yaml
stt:
  model: "medium"  # tiny, base, small, medium, large
  language: "en"
```

**Model Comparison:**
| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| tiny | 39MB | ⚡⚡⚡⚡⚡ | ⭐⭐ | Testing only |
| base | 74MB | ⚡⚡⚡⚡ | ⭐⭐⭐ | Demos, fast response |
| small | 244MB | ⚡⚡⚡ | ⭐⭐⭐⭐ | Good balance |
| medium | 769MB | ⚡⚡ | ⭐⭐⭐⭐⭐ | **Production (recommended)** |
| large | 1550MB | ⚡ | ⭐⭐⭐⭐⭐⭐ | Best accuracy, slow |

### 🔊 **Text-to-Speech**
```yaml
tts:
  engine: "edge-tts"  # gtts (robotic) or edge-tts (natural)
  edge:
    voice: "en-US-AriaNeural"  # See voice list below
```

**Popular Voices:**
- **Female US**: en-US-AriaNeural (default), en-US-JennyNeural, en-US-MichelleNeural
- **Male US**: en-US-GuyNeural, en-US-ChristopherNeural, en-US-EricNeural
- **British**: en-GB-SoniaNeural (F), en-GB-RyanNeural (M)
- **Indian**: en-IN-NeerjaNeural (F), en-IN-PrabhatNeural (M)

[Full voice list](https://speech.microsoft.com/portal/voicegallery)

### 🖥️ **GPU Acceleration**
```yaml
gpu:
  enabled: true  # Auto-detect CUDA GPU
```

### 🎧 **Audio/Microphone Settings**
```yaml
audio:
  vad:
    aggressiveness: 3  # 0-3 (higher = stricter speech detection)
  recording:
    silence_threshold: 2.0  # Seconds of silence to stop recording
```

**If microphone isn't detecting your voice:**
- Lower `aggressiveness` to `1` or `2`
- Increase `silence_threshold` to `3.0` or `4.0`

---

## 🔄 Migration from Old System

### ❌ **Old Way** (DON'T USE)
- Settings scattered across multiple files:
  - `.env` file
  - `server/config.py` (hardcoded defaults)
  - Environment variables
- Conflicts and overrides were confusing

### ✅ **New Way** (USE THIS)
- **ONE FILE**: `config.yaml`
- Clear, organized, easy to edit
- No more conflicts or hidden overrides

### 📦 **Backed Up Files**
The old configuration files have been backed up:
- `.env` → `.env.backup`
- `server/config.py` → `server/config_old.py.backup`

**Don't edit these!** They're just backups.

---

## 🛠️ Advanced Usage

### Custom Configuration File
```python
from unified_config import Config

# Load from custom location
custom_config = Config("path/to/custom_config.yaml")
```

### Access Nested Values
```python
from unified_config import config

# Direct attribute access
print(config.TTS_ENGINE)  # "edge-tts"

# Dictionary-style access
print(config.get("tts.engine"))  # "edge-tts"
print(config.get("tts.edge.voice"))  # "en-US-AriaNeural"
```

---

## 📝 Common Configuration Tasks

### Change Voice to Male
```yaml
tts:
  edge:
    voice: "en-US-GuyNeural"
```

### Speed Up STT (Use Smaller Model)
```yaml
stt:
  model: "base"  # Much faster than medium
```

### Update Network IP
```yaml
server:
  server_ip: "192.168.1.150"  # Your new IP
```

### Fix Microphone Detection Issues
```yaml
audio:
  vad:
    aggressiveness: 1  # More lenient (try 1 or 2)
  recording:
    silence_threshold: 3.0  # Wait longer for silence
```

### Disable GPU (Force CPU)
```yaml
gpu:
  enabled: false
```

---

## ✅ Validation

After making changes, always test:

```bash
# Test configuration loading
./env/bin/python test_config.py

# Start server and check logs
make run-server
```

Look for:
```
✅ Configuration loaded from: config.yaml
✅ Using TTS engine: edge-tts
✅ GPU detected: NVIDIA GeForce MX350  (if GPU enabled)
```

---

## 🐛 Troubleshooting

### "Configuration file not found"
- Make sure `config.yaml` is in the project root
- Check you're running commands from project directory

### "KeyError" when loading config
- config.yaml might be malformed
- Check YAML syntax (indentation matters!)
- Compare with backup if needed

### Settings not taking effect
- Did you restart the server after editing?
- Check `test_config.py` output to verify values

---

## 📚 Files Reference

| File | Purpose | Edit? |
|------|---------|-------|
| `config.yaml` | **Main configuration** | ✅ YES - Edit this! |
| `unified_config.py` | Configuration loader | ❌ No (internal code) |
| `server/config.py` | Compatibility wrapper | ❌ No (auto-generated) |
| `test_config.py` | Test script | ℹ️ Run to verify settings |
| `.env.backup` | Old config backup | ❌ No (archived) |

---

**🎉 That's it! Edit `config.yaml`, restart server, and you're good to go!**
