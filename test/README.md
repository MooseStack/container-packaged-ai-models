# Test clients

Run these commands from the repository root with a service listening on port 8080.

```bash
# Interactive streaming chat
python3 test/chat-completions.py

# Single chat prompt
python3 test/chat-completions.py "What is 2+2?"

# Embeddings (one or more texts)
python3 test/embeddings.py "Embed this text!"
python3 test/embeddings.py "First text" "Second text"
python3 test/embeddings.py --show-all "Embed this text!"

# Batch transcription from a WAV file
python3 test/audio-batch.py test/sample-recording.wav

# Record from the microphone, then transcribe
python3 test/audio-batch.py

# Realtime microphone transcription
python3 test/audio-websocket.py
```

Interactive chat accepts `/exit`, `/quit`, or Ctrl+C. Batch recording stops on Enter (Ctrl+C also works), then submits the audio for transcription. Audio uses 16 kHz mono 16-bit PCM. WAV transcription and chat use only the Python standard library; microphone input requires `pyaudio`, and WebSocket streaming also requires `websocket-client`.

The embedding client uses only the Python standard library and validates that each input returns a finite vector of the same dimension. Override its endpoint, model, or API key with `--url`, `--model`, and `--api-key`, or `EMBEDDINGS_URL`, `EMBEDDINGS_MODEL`, and `EMBEDDINGS_API_KEY`.
It prints the first 32 values of each vector by default; pass `--show-all` to print the complete embedding.

Override audio settings with `--url`, `--api-key`, `--model`, and `--response-format`, or the corresponding `AUDIO_TRANSCRIPTION_*` environment variables.
