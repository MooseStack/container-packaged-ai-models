#!/usr/bin/env python3
"""Smoke-test a realtime audio transcription WebSocket with microphone input."""

import argparse
import json
import os
import threading

from _audio import CHUNK, RATE, microphone


def receive_events(ws, finished, websocket):
    try:
        while not finished.is_set():
            event = json.loads(ws.recv())
            event_type = event.get("type")
            if event_type == "conversation.item.input_audio_transcription.delta":
                print(event.get("delta", ""), end="", flush=True)
            elif event_type == "conversation.item.input_audio_transcription.completed":
                print(f"\n{event.get('text', '')}", flush=True)
                finished.set()
            elif event_type == "error":
                print(f"\nServer error: {event.get('error', event)}", flush=True)
                finished.set()
    except (websocket.WebSocketException, ValueError) as error:
        if not finished.is_set():
            print(f"\nSpeech server connection closed: {error}", flush=True)
            finished.set()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=os.getenv("NEMO_SPEECH_WS_URL", "ws://127.0.0.1:8080/v1/realtime"))
    parser.add_argument("--api-key", default=os.getenv("NEMO_SPEECH_API_KEY"))
    args = parser.parse_args()

    try:
        import websocket
    except ImportError:
        parser.error("WebSocket streaming requires websocket-client: python3 -m pip install websocket-client")

    headers = [f"Authorization: Bearer {args.api_key}"] if args.api_key else []
    try:
        ws = websocket.create_connection(args.url, header=headers)
        finished = threading.Event()
        receiver = threading.Thread(target=receive_events, args=(ws, finished, websocket), daemon=True)
        receiver.start()
        try:
            ws.send(json.dumps({
                "type": "session.update",
                "session": {"sample_rate": RATE, "language": "en", "automatic_punctuation": True},
            }))
            with microphone() as stream:
                print("Streaming... Press Ctrl+C to stop.", flush=True)
                try:
                    while not finished.is_set():
                        ws.send(stream.read(CHUNK), opcode=websocket.ABNF.OPCODE_BINARY)
                except KeyboardInterrupt:
                    print("Stopping stream and waiting for the final transcription...", flush=True)
                    ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
                    finished.wait(timeout=5)
        finally:
            finished.set()
            ws.close()
            receiver.join(timeout=1)
    except (OSError, RuntimeError, websocket.WebSocketException) as error:
        print(f"Could not stream audio: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
