#!/usr/bin/env python3
"""Smoke-test or interactively chat with an OpenAI-style completions endpoint."""

import argparse
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def request_completion(url, model, messages, max_tokens, stream=False):
    body = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": stream,
    }).encode()
    request = Request(
        f"{url.rstrip('/')}/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    return urlopen(request)


def print_stream(response):
    """Print SSE content deltas and return the complete assistant message."""
    parts = []
    for raw_line in response:
        line = raw_line.decode(errors="replace").strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        try:
            event = json.loads(data)
        except json.JSONDecodeError:
            continue
        choices = event.get("choices") or []
        delta = (choices[0].get("delta") or {}).get("content") if choices else None
        if delta:
            print(delta, end="", flush=True)
            parts.append(delta)
    print()
    return "".join(parts)


def interactive(url, model, max_tokens):
    messages = []
    print("Interactive chat. Press Ctrl+D or type /exit to quit.")
    try:
        while True:
            try:
                prompt = input("You: ").strip()
            except EOFError:
                print()
                break
            if not prompt:
                continue
            if prompt.lower() in {"/exit", "/quit"}:
                break

            messages.append({"role": "user", "content": prompt})
            try:
                with request_completion(url, model, messages, max_tokens, stream=True) as response:
                    print("Assistant: ", end="", flush=True)
                    answer = print_stream(response)
            except HTTPError as error:
                print(f"Server error ({error.code}): {error.read().decode(errors='replace')}")
                messages.pop()
                continue
            except (URLError, OSError, json.JSONDecodeError) as error:
                print(f"Request failed: {error}")
                messages.pop()
                continue
            messages.append({"role": "assistant", "content": answer})
    except KeyboardInterrupt:
        print("\nExiting.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", nargs="?", help="Prompt for a single completion; omit for interactive chat")
    parser.add_argument("--url", default=os.getenv("ONNX_GENAI_URL", "http://127.0.0.1:8080"), help="Server base URL")
    parser.add_argument("--model", default=os.getenv("ONNX_GENAI_MODEL", "qwen3-0.6b"))
    parser.add_argument("--max-tokens", type=int, default=64)
    args = parser.parse_args()

    if args.prompt is None:
        interactive(args.url, args.model, args.max_tokens)
        return 0

    try:
        with request_completion(args.url, args.model, [{"role": "user", "content": args.prompt}], args.max_tokens) as response:
            result = json.loads(response.read().decode())
    except HTTPError as error:
        print(f"Server error ({error.code}): {error.read().decode(errors='replace')}")
        return 1
    except (URLError, OSError, json.JSONDecodeError) as error:
        print(f"Request failed: {error}")
        return 1

    choices = result.get("choices") or []
    content = (choices[0].get("message") or {}).get("content") if choices else None
    print(content or json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
