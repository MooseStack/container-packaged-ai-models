#!/usr/bin/env python3
"""Smoke-test oBeaver chat completions for the ONNX Runtime GenAI model."""

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = os.getenv("ONNX_GENAI_URL", "http://127.0.0.1:8080").rstrip("/")
MODEL = os.getenv("ONNX_GENAI_MODEL", "qwen3-0.6b")
PROMPT = sys.argv[1] if len(sys.argv) > 1 else "Tell me a joke."

body = json.dumps({
    "model": MODEL,
    "messages": [{"role": "user", "content": PROMPT}],
    "max_tokens": 64,
}).encode()

request = Request(
    f"{BASE_URL}/v1/chat/completions",
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST",
)

try:
    with urlopen(request) as response:
        result = json.loads(response.read().decode())
except HTTPError as error:
    print(f"Server error ({error.code}): {error.read().decode(errors='replace')}")
    raise SystemExit(1)
except (URLError, OSError, json.JSONDecodeError) as error:
    print(f"Request failed: {error}")
    raise SystemExit(1)

choices = result.get("choices") or []
text = (choices[0].get("message") or {}).get("content") if choices else None
print(text or json.dumps(result, indent=2))
