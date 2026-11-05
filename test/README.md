# Test clients

Run these commands from the repository root with a service listening on port 8080.

```bash
# Interactive streaming chat
python3 test/chat-completions.py

# Single chat prompt
python3 test/chat-completions.py "What is 2+2?"

# Batch transcription from a WAV file
python3 test/audio-batch.py recording.wav

# Record from the microphone, then transcribe
python3 test/audio-batch.py

# Realtime microphone transcription
python3 test/audio-websocket.py
```

Interactive chat accepts `/exit`, `/quit`, or Ctrl+C. Batch recording stops on Enter (Ctrl+C also works), then submits the audio for transcription. Audio uses 16 kHz mono 16-bit PCM. WAV transcription and chat use only the Python standard library; microphone input requires `pyaudio`, and WebSocket streaming also requires `websocket-client`.

Override audio settings with `--url`, `--api-key`, `--model`, and `--response-format`, or the corresponding `AUDIO_TRANSCRIPTION_*` environment variables.
