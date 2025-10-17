# 🔊 Text-to-Speech (TTS) Configuration Guide

CampusConvo supports multiple TTS engines with different quality levels and characteristics.

## 🎯 Quick Comparison

| Engine | Quality | Speed | Online/Offline | GPU Support | Installation |
|--------|---------|-------|----------------|-------------|--------------|
| **gTTS** | ⭐⭐⭐ Basic | Fast | Online | No | ✅ Built-in |
| **Edge TTS** | ⭐⭐⭐⭐⭐ Excellent | Fast | Online | No | `pip install edge-tts` |
| **Coqui TTS** | ⭐⭐⭐⭐⭐ Excellent | Slow | Offline | Yes | `pip install TTS` |
| **Piper** | ⭐⭐⭐⭐ Very Good | Very Fast | Offline | No | Complex setup |

---

## 📋 Configuration Options

### 1. **gTTS (Google TTS)** - Default, Basic Quality

**Best for:** Quick demos, don't care about voice quality  
**Pros:** No setup, works immediately, reliable  
**Cons:** Robotic voice, requires internet

```bash
# In .env or config
TTS_ENGINE=gtts
TTS_ACCENT=com  # Options: com (US), co.uk (British), co.in (Indian), com.au (Australian)
```

**No installation needed** - already included!

---

### 2. **Edge TTS (Microsoft Edge)** - ⭐ RECOMMENDED for Best Quality

**Best for:** Production, natural-sounding voices  
**Pros:** Extremely natural, many voices, fast, free  
**Cons:** Requires internet

```bash
# Install
pip install edge-tts

# Configure in .env
TTS_ENGINE=edge-tts
TTS_EDGE_VOICE=en-US-AriaNeural  # Female US voice
```

#### Popular Voices:
- **Female US:** `en-US-AriaNeural` (friendly), `en-US-JennyNeural` (professional)
- **Male US:** `en-US-GuyNeural` (deep), `en-US-DavisNeural` (warm)
- **British Female:** `en-GB-SoniaNeural`
- **British Male:** `en-GB-RyanNeural`
- **Indian:** `en-IN-NeerjaNeural` (female), `en-IN-PrabhatNeural` (male)

[Full voice list](https://speech.microsoft.com/portal/voicegallery)

---

### 3. **Coqui TTS** - High Quality, Offline

**Best for:** Offline deployments, custom voices  
**Pros:** Works offline, high quality, open-source  
**Cons:** Slow inference, large models, complex setup

```bash
# Install
pip install TTS

# Configure in .env
TTS_ENGINE=coqui
TTS_COQUI_MODEL=tts_models/en/ljspeech/tacotron2-DDC
USE_GPU=true  # Enable GPU for faster inference
```

#### Popular Models:
- `tts_models/en/ljspeech/tacotron2-DDC` - Good quality, faster
- `tts_models/en/ljspeech/glow-tts` - Very natural
- `tts_models/en/vctk/vits` - Multi-speaker

List all models:
```bash
./env/bin/tts --list_models
```

---

### 4. **Piper TTS** - Fast Neural, Offline

**Best for:** Low-latency offline applications  
**Pros:** Very fast, good quality, works offline  
**Cons:** Complex setup, requires model downloads

```bash
# Install piper-tts (requires manual setup)
# See: https://github.com/rhasspy/piper

TTS_ENGINE=piper
TTS_PIPER_MODEL=en_US-lessac-medium
```

---

## 🚀 Quick Start Examples

### Switch to Edge TTS (Best Quality):
```bash
# Install edge-tts
./env/bin/pip install edge-tts

# Add to .env file
echo "TTS_ENGINE=edge-tts" >> .env
echo "TTS_EDGE_VOICE=en-US-AriaNeural" >> .env

# Restart server
make run-server
```

### Switch to Coqui TTS (Offline, GPU-accelerated):
```bash
# Install Coqui TTS
./env/bin/pip install TTS

# Add to .env file
echo "TTS_ENGINE=coqui" >> .env
echo "TTS_COQUI_MODEL=tts_models/en/ljspeech/tacotron2-DDC" >> .env
echo "USE_GPU=true" >> .env

# Restart server
make run-server
```

---

## 🎛️ Fine-Tuning Tips

### For gTTS:
- Use `TTS_ACCENT=co.in` for Indian accent
- Use `TTS_ACCENT=co.uk` for British accent

### For Edge TTS:
- Try different voices for personality:
  - `en-US-AriaNeural` - Friendly, casual
  - `en-US-JennyNeural` - Professional, clear
  - `en-US-GuyNeural` - Deep, authoritative

### For Coqui:
- Enable GPU for 5-10x speed improvement
- Use `tacotron2` for faster inference
- Use `vits` for better quality (slower)

---

## 🐛 Troubleshooting

### Edge TTS fails with "asyncio" error:
- Restart the server, it auto-handles async

### Coqui TTS is too slow:
- Enable GPU: `USE_GPU=true`
- Use smaller model: `tts_models/en/ljspeech/tacotron2-DDC`

### Voice sounds robotic:
- Switch from `gtts` to `edge-tts`
- Or use Coqui with a `vits` model

---

## 📊 Benchmark (Approximate)

Generating "Hello there, how may I assist you today?" (10 words):

| Engine | Time | Quality | Size |
|--------|------|---------|------|
| gTTS | 0.5s | 3/5 | 25 KB |
| Edge TTS | 0.8s | 5/5 | 30 KB |
| Coqui (CPU) | 3.0s | 5/5 | 80 KB |
| Coqui (GPU) | 0.6s | 5/5 | 80 KB |

---

## 💡 Recommendations

1. **For Demos/Hackathons:** Use `edge-tts` (best quality, easy setup)
2. **For Production (online):** Use `edge-tts`
3. **For Production (offline):** Use `coqui` with GPU
4. **For Quick Testing:** Use `gtts` (default)

**Winner:** `edge-tts` - Best balance of quality, speed, and ease of use! 🏆
