# Porcupine Wake Word Setup Guide

## Quick Start

### 1. Get a FREE Porcupine Access Key

1. Go to https://console.picovoice.ai/
2. Sign up for a free account (it takes 30 seconds)
3. Copy your Access Key from the dashboard

### 2. Configure Your Access Key

**Option A: Set in config file (Recommended)**
```bash
# Edit server/config.py and add your key:
nano server/config.py
```

Find this line:
```python
PORCUPINE_ACCESS_KEY = os.getenv("PORCUPINE_ACCESS_KEY", "")
```

Replace with:
```python
PORCUPINE_ACCESS_KEY = os.getenv("PORCUPINE_ACCESS_KEY", "YOUR-ACCESS-KEY-HERE")
```

**Option B: Set as environment variable**
```bash
export PORCUPINE_ACCESS_KEY="YOUR-ACCESS-KEY-HERE"
```

### 3. Run the Client

```bash
python client.py
```

## Available Wake Words

Built-in keywords you can use (configured in `server/config.py`):
- `alexa`
- `americano`
- `blueberry`
- `bumblebee`
- `computer`
- `grapefruit`
- `grasshopper`
- `hey google` (default)
- `hey siri`
- `jarvis`
- `ok google`
- `picovoice`
- `porcupine`
- `terminator`

### 4. Customize Wake Words

Edit `server/config.py`:
```python
PORCUPINE_KEYWORDS = ["jarvis", "computer"]  # Use multiple wake words!
```

## Troubleshooting

### Error: "access_key is required"
- Make sure you've set `PORCUPINE_ACCESS_KEY` in `server/config.py` or as environment variable

### Error: "Invalid access key"
- Double-check your key at https://console.picovoice.ai/
- Make sure there are no extra spaces or quotes

### Error: "Keyword not found"
- Only use built-in keywords from the list above
- For custom wake words, you need to train them on the Picovoice Console

## Free Tier Limits

- Porcupine free tier allows unlimited local wake word detection
- No cloud calls needed - all processing is local
- Perfect for personal projects and hackathons!
