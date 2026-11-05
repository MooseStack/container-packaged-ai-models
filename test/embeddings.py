#!/usr/bin/env python3
"""Smoke-test an OpenAI-compatible embeddings endpoint (standard library only)."""

import argparse
import json
import math
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def embeddings_url(base_url):
    base_url = base_url.rstrip("/")
    if base_url.endswith("/v1"):
        return f"{base_url}/embeddings"
    return f"{base_url}/v1/embeddings"


def request_embeddings(url, model, inputs, api_key, timeout):
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = Request(
        embeddings_url(url),
        data=json.dumps({"model": model, "input": inputs}).encode(),
        headers=headers,
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def validate_embeddings(result, inputs):
    if not isinstance(result, dict):
        raise ValueError("Response is not a JSON object")
    data = result.get("data")
    if not isinstance(data, list) or len(data) != len(inputs):
        raise ValueError(f"Expected {len(inputs)} embeddings, got {len(data) if isinstance(data, list) else 'no data'}")

    if not all(isinstance(item, dict) and isinstance(item.get("index"), int) for item in data):
        raise ValueError("Embedding data has missing or invalid indices")
    vectors = []
    for expected_index, item in enumerate(sorted(data, key=lambda item: item.get("index", -1))):
        if item.get("index") != expected_index:
            raise ValueError(f"Missing embedding at index {expected_index}")
        vector = item.get("embedding")
        if not isinstance(vector, list) or not vector:
            raise ValueError(f"Embedding {expected_index} is empty or invalid")
        if not all(isinstance(value, (int, float)) and math.isfinite(value) for value in vector):
            raise ValueError(f"Embedding {expected_index} contains non-finite or non-numeric values")
        if vectors and len(vector) != len(vectors[0]):
            raise ValueError("Embeddings have different dimensions")
        vectors.append(vector)
    return vectors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("texts", nargs="*", help="Texts to embed (default: one sample text)")
    parser.add_argument("--url", default=os.getenv("EMBEDDINGS_URL", "http://127.0.0.1:8080"), help="Server base URL, with or without /v1")
    parser.add_argument("--model", default=os.getenv("EMBEDDINGS_MODEL", "qwen3-embedding-0.6b"))
    parser.add_argument("--api-key", default=os.getenv("EMBEDDINGS_API_KEY", ""))
    parser.add_argument("--timeout", type=float, default=60, help="Request timeout in seconds")
    parser.add_argument("--show-all", action="store_true", help="Print every value in each embedding")
    args = parser.parse_args()
    inputs = args.texts or ["Embed this text!"]

    try:
        result = request_embeddings(args.url, args.model, inputs, args.api_key, args.timeout)
        vectors = validate_embeddings(result, inputs)
    except HTTPError as error:
        print(f"Server error ({error.code}): {error.read().decode(errors='replace')}", file=sys.stderr)
        return 1
    except (URLError, OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        print(f"Embedding request failed: {error}", file=sys.stderr)
        return 1

    print(f"Model: {result.get('model', args.model)}")
    print(f"Embeddings: {len(vectors)}; dimensions: {len(vectors[0])}")
    for index, (text, vector) in enumerate(zip(inputs, vectors)):
        shown = vector if args.show_all else vector[:32]
        preview = ", ".join(f"{value:.6f}" for value in shown)
        print(f"[{index}] {text!r}: [{preview}{', ...' if len(shown) < len(vector) else ''}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
