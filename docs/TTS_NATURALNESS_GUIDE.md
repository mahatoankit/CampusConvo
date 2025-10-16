# TTS Voice Naturalness Guide

## 🎵 How to Make Voice Sound More Natural

### Current Setup: gTTS (Google Text-to-Speech)

**Pros:**
- ✅ Free and unlimited
- ✅ Natural-sounding (uses Google's voices)
- ✅ Multiple accents available
- ✅ No API keys needed

**Cons:**
- ❌ Requires internet connection
- ❌ Limited voice customization
- ❌ Fixed pitch/speed (can't fine-tune much)

---

## 🎯 Option 1: Change Accent (Easy - Already Added!)

### Edit `.env` file:

```bash
# Options: com, co.uk, co.in, com.au
TTS_ACCENT=com        # US English (clear, neutral)
TTS_ACCENT=co.uk      # British English (formal, clear)
TTS_ACCENT=co.in      # Indian English (familiar for Nepal)
TTS_ACCENT=com.au     # Australian English
```

**Test each accent:**
```bash
# Edit .env, then restart server
python run_server.py

# Test in voice mode
python client.py → v → ask question
```

### Recommended for Nepal/Kathmandu:
```bash
TTS_ACCENT=co.in      # Indian English - most familiar accent
```

---

## 🎯 Option 2: Use Piper TTS (Most Natural - Offline!)

**Piper** is a fast, local, neural TTS engine with very natural voices.

### Installation:
```bash
# Install piper-tts
pip install piper-tts

# Download a voice model (choose one):
# US English (female, high quality)
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

# Indian English (if available)
# Check: https://github.com/rhasspy/piper/blob/master/VOICES.md
```

### Implementation (I can add this if you want):
- Add `piper` option to `TTS_ENGINE`
- Much more natural than gTTS
- Works offline
- Faster than gTTS

---

## 🎯 Option 3: Use ElevenLabs API (Most Natural - Paid)

**ElevenLabs** has the most human-like voices but requires API key + costs money.

### Features:
- 🎭 Emotion/tone control
- 🎤 Voice cloning (your own voice!)
- 🌍 Multiple languages with natural accents
- ⚡ Very fast

### Pricing:
- Free tier: 10,000 characters/month
- Paid: $5-$99/month

### Setup:
```bash
pip install elevenlabs
```

Edit `.env`:
```bash
TTS_ENGINE=elevenlabs
ELEVENLABS_API_KEY=your_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Rachel (default)
```

---

## 🎯 Option 4: Improve Response Text (Free - Prompt Engineering!)

Sometimes the issue isn't the voice, it's the **text being spoken**.

### Make responses more conversational:

Edit `server/rag_pipeline.py` prompt:
```python
Instructions:
- Use natural, conversational language
- Avoid formal/robotic phrases like "Based on the information..."
- Use contractions (it's, don't, you'll)
- Add filler words occasionally (well, actually, you know)
- Speak like a friendly student advisor
```

**Example:**
```
❌ Robotic: "Sunway College is located at Behind Maitidevi Temple, Kathmandu."
✅ Natural: "Sure! Sunway College is right behind Maitidevi Temple in Kathmandu."
```

---

## 📊 Comparison Table

| TTS Engine | Naturalness | Speed | Offline | Cost | Setup |
|------------|-------------|-------|---------|------|-------|
| **gTTS** (current) | ⭐⭐⭐☆☆ | Medium | ❌ | Free | ✅ Easy |
| **gTTS + Indian accent** | ⭐⭐⭐⭐☆ | Medium | ❌ | Free | ✅ Very Easy |
| **Piper TTS** | ⭐⭐⭐⭐☆ | Fast | ✅ | Free | ⚠️ Moderate |
| **ElevenLabs** | ⭐⭐⭐⭐⭐ | Very Fast | ❌ | Paid | ⚠️ Moderate |
| **pyttsx3** (offline) | ⭐⭐☆☆☆ | Fast | ✅ | Free | ✅ Easy |

---

## 🚀 Quick Test: Try Different Accents NOW!

### 1. Edit `.env`:
```bash
nano .env
# Change TTS_ACCENT to different values
```

### 2. Test each:
```bash
# US English (neutral, clear)
TTS_ACCENT=com
python run_server.py
# Test voice mode

# Indian English (familiar for Nepal)
TTS_ACCENT=co.in
python run_server.py
# Test voice mode

# British English (formal, clear)
TTS_ACCENT=co.uk
python run_server.py
# Test voice mode
```

### 3. Pick your favorite!

---

## 🎯 My Recommendation

**For your use case (Nepal college assistant):**

1. **Start with:** `TTS_ACCENT=co.in` (Indian English)
   - Most familiar accent for Nepali students
   - Already implemented!
   - Just restart server

2. **If you want better quality:**
   - Try **Piper TTS** (offline, fast, natural)
   - I can help you set it up!

3. **If quality is CRITICAL:**
   - Use **ElevenLabs** (costs money but amazing)

---

## 🔧 Current Settings (Already Updated!)

In your `.env`:
```bash
TTS_ACCENT=com    # Change this to: co.in, co.uk, com.au
```

**Test it now:**
```bash
# Edit .env to try different accents
nano .env

# Restart server
python run_server.py

# Test voice mode
python client.py → v
```

---

## 💡 Want Even More Natural? Let Me Know!

I can implement:
- ✅ Piper TTS (offline, neural, very natural)
- ✅ ElevenLabs (cloud, most natural)
- ✅ Better prompt engineering (more conversational text)
- ✅ Speed/pitch adjustment with audio processing

Just say which one you want! 🎵
