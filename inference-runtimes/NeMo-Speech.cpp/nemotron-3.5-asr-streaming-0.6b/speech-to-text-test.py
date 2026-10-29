import json
import os
import threading
from contextlib import contextmanager

import pyaudio
import websocket

# --- Configuration ---
WS_URL = os.getenv("NEMO_SPEECH_WS_URL", "ws://127.0.0.1:8080/v1/realtime")
API_KEY = os.getenv("NEMO_SPEECH_API_KEY")

# Audio formatting (16kHz Mono is best for ASR)
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000 


@contextmanager
def suppress_alsa_output():
    saved_stderr = os.dup(2)
    null_device = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(null_device, 2)
        yield
    finally:
        os.dup2(saved_stderr, 2)
        os.close(null_device)
        os.close(saved_stderr)


def receive_events(ws, finished):
    try:
        while not finished.is_set():
            event = json.loads(ws.recv())
            event_type = event.get("type")

            if event_type == "conversation.item.input_audio_transcription.delta":
                print(event.get("delta", ""), end="", flush=True)
            elif event_type == "conversation.item.input_audio_transcription.completed":
                print(f"\n📝 {event.get('text', '')}", flush=True)
            elif event_type == "error":
                print(f"\n❌ Server error: {event.get('error', event)}", flush=True)
            elif event_type == "input_audio_buffer.committed":
                finished.set()
    except (websocket.WebSocketConnectionClosedException, websocket.WebSocketBadStatusException):
        if not finished.is_set():
            print("\n❌ The speech server connection closed.", flush=True)

def stream_audio():
    headers = [f"Authorization: Bearer {API_KEY}"] if API_KEY else []
    ws = websocket.create_connection(WS_URL, header=headers)
    finished = threading.Event()
    receiver = threading.Thread(target=receive_events, args=(ws, finished), daemon=True)
    receiver.start()

    ws.send(json.dumps({
        "type": "session.update",
        "session": {
            "sample_rate": RATE,
            "language": "en",
            "automatic_punctuation": True,
        },
    }))

    with suppress_alsa_output():
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

    print("\n🎤 Streaming... Press Ctrl+C to stop.\n", flush=True)
    try:
        while True:
            ws.send(stream.read(CHUNK), opcode=websocket.ABNF.OPCODE_BINARY)
    except KeyboardInterrupt:
        print("\n⏹ Stopping stream and waiting for the final transcription...", flush=True)
        ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
        receiver.join(timeout=5)
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        finished.set()
        ws.close()

if __name__ == "__main__":
    try:
        stream_audio()
    except (OSError, websocket.WebSocketException) as error:
        print(f"❌ Could not stream audio: {error}")