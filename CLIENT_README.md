# CampusConvo - Simple Voice Client

## Quick Start

1. **Start the server** (in one terminal):
   ```bash
   python run_server.py
   ```

2. **Run the client** (in another terminal):
   ```bash
   python client.py
   ```

3. **Just start talking!**
   - Wait for the greeting
   - Speak your question clearly
   - Wait for the answer
   - Repeat!

4. **To exit**: Say "bye", "exit", "goodbye", or "quit"

## How It Works

1. Greets you automatically
2. Listens for your question (uses Voice Activity Detection)
3. Sends audio to server for transcription (Whisper)
4. Gets answer from RAG pipeline
5. Speaks the answer back to you
6. Repeats!

## No Wake Word Needed!

This version is simple:
- ✅ No wake word detection
- ✅ No API keys needed
- ✅ Just run and talk
- ✅ Perfect for demos and quick testing

## Example Conversation

```
[ZYRA] Hello there, how may I assist you today?

🎤 Listening... (speak now)
✓ Recording complete

[YOU] Where is Sunway College located?

[ZYRA] Sunway College is located in Bandar Sunway, Petaling Jaya, Selangor, Malaysia...

🎤 Listening... (speak now)
[YOU] What courses do they offer?

[ZYRA] Sunway College offers various programs including...

🎤 Listening... (speak now)
[YOU] Bye

[ZYRA] Goodbye! Have a great day!
```

## Troubleshooting

**No speech detected:**
- Speak louder or closer to the microphone
- Check your microphone is working
- Adjust VAD_AGGRESSIVENESS in server/config.py (try 1 for more sensitive)

**Server connection error:**
- Make sure server is running: `python run_server.py`
- Check SERVER_IP in server/config.py matches your network

**Audio doesn't play:**
- Install mpg123: `sudo apt-get install mpg123`
- Or install ffplay: `sudo apt-get install ffmpeg`

## Files

- `client.py` - Simple voice client (this one!)
- `client_wake_word.py` - Wake word version (with Porcupine)
- `client.py.backup` - Original backup

To use wake word version:
```bash
python client_wake_word.py
```
