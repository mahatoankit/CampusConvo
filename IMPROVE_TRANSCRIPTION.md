# Improving Speech Recognition Accuracy

## Problem: Whisper mishears domain-specific words

Examples:
- "Sunway" → "summary", "some way", "someday"
- "Petaling Jaya" → "petaling java"

## Solutions Implemented

### 1. ✅ Word Correction (Already Active!)

Added automatic word correction in `server/voice_pipeline.py`:
- Automatically fixes common mishearings
- "summary" → "sunway"
- "some way" → "sunway"
- "bandar summary" → "bandar sunway"

**To add more corrections:**
Edit `server/voice_pipeline.py` and add to `WORD_CORRECTIONS` dictionary:
```python
WORD_CORRECTIONS = {
    "wrong word": "correct word",
    "another wrong": "correct",
}
```

### 2. 🎯 Upgrade Whisper Model (Optional)

**Current:** `base` (74MB, fast, decent accuracy)

**Better options:**

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| tiny | 39MB | ⚡⚡⚡ | ⭐⭐ | Testing only |
| base | 74MB | ⚡⚡ | ⭐⭐⭐ | Current (good) |
| **small** | 244MB | ⚡ | ⭐⭐⭐⭐ | **Recommended** |
| medium | 769MB | 🐌 | ⭐⭐⭐⭐⭐ | Best accuracy |
| large | 1550MB | 🐌🐌 | ⭐⭐⭐⭐⭐ | Overkill |

**To upgrade to `small` (recommended):**

1. Edit `.env` file:
   ```bash
   nano .env
   ```

2. Change this line:
   ```
   STT_MODEL=base
   ```
   to:
   ```
   STT_MODEL=small
   ```

3. Restart server:
   ```bash
   # Stop current server (Ctrl+C)
   python run_server.py
   ```

4. First run will download the model (~244MB), then it's cached

### 3. 📝 Prompt-based Hints (Advanced)

Whisper supports initial prompts to improve accuracy. Add to `server/voice_pipeline.py`:

```python
result = self.whisper_model.transcribe(
    temp_audio_path,
    language=config.STT_LANGUAGE,
    initial_prompt="Sunway College, Bandar Sunway, Petaling Jaya, Selangor, Malaysia."
)
```

This gives Whisper context about expected words.

## Quick Fix Recommendation

**For best results with minimal effort:**

1. ✅ Use word corrections (already active!)
2. ✅ Upgrade to `small` model (edit `.env`, restart server)

This combo gives excellent accuracy for demos!

## Testing

After making changes:

1. Restart server: `python run_server.py`
2. Run client: `python client.py`
3. Say: "Where is Sunway College located?"
4. Check server logs - you should see:
   ```
   Raw transcription: 'Where is summary college located?'
   ✓ Corrected: 'Where is sunway college located?'
   ```

## Add Your Own Corrections

Common patterns to add:
- Campus names: "campus" → "specific campus name"
- Professor names: "mishearing" → "correct name"
- Course codes: "see s 101" → "CS101"
- Building names: etc.

Just edit `WORD_CORRECTIONS` in `server/voice_pipeline.py`!
