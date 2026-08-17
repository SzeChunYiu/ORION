#!/usr/bin/env python3
"""
Protocol adapter: OpenAI chat-completions API → Anthropic messages API.

Translates POST /v1/chat/completions requests to POST /v1/messages format
for the glm-5.3 judge endpoint at api.z.ai. Reads ANTHROPIC_AUTH_TOKEN at runtime.
"""
import asyncio
import json
import logging
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from typing import Any, Dict, Optional
import urllib.parse

import aiohttp


LOGGER = logging.getLogger(__name__)
KEY_PATH = os.path.expanduser("~/.claude-cn/settings.json")


def load_anthropic_key() -> str:
    """Load ANTHROPIC_AUTH_TOKEN from Claude-CN settings.json at runtime."""
    try:
        with open(KEY_PATH, "r") as f:
            settings = json.load(f)
        key = settings.get("env", {}).get("ANTHROPIC_AUTH_TOKEN", "")
        if not key:
            raise ValueError("ANTHROPIC_AUTH_TOKEN not found in settings.json")
        return key
    except Exception as e:
        raise RuntimeError(f"Failed to load ANTHROPIC_AUTH_TOKEN: {e}")


async def translate_to_anthropic(openai_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert OpenAI chat-completions request to Anthropic messages format.

    OpenAI: {"messages": [{"role": "system", "content": "..."}, ...], "model": "...", ...}
    Anthropic: {"model": "...", "max_tokens": ..., "system": "...", "messages": [{"role": "...", "content": "..."}]}
    """
    messages = openai_request.get("messages", [])
    model = openai_request.get("model", "glm-5.3")
    temperature = openai_request.get("temperature", 0.0)
    max_tokens = openai_request.get("max_tokens", openai_request.get("max_completion_tokens", 512))

    # Extract system message (Anthropic separates it from messages array)
    system_content = ""
    anthropic_messages = []

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if role == "system":
            system_content = content
        else:
            anthropic_messages.append({"role": role, "content": content})

    return {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system_content,
        "messages": anthropic_messages,
    }


async def translate_from_anthropic(anthropic_response: Dict[str, Any], model: str) -> Dict[str, Any]:
    """
    Convert Anthropic messages response to OpenAI chat-completions format.

    Anthropic: {"id": "...", "type": "message", "content": [{"type": "text", "text": "..."}], ...}
    OpenAI: {"id": "...", "object": "chat.completion", "choices": [{"index": 0, "message": {"role": "assistant", "content": "..."}, ...}]}
    """
    content_text = ""
    if anthropic_response.get("type") == "message":
        for block in anthropic_response.get("content", []):
            if block.get("type") == "text":
                content_text += block.get("text", "")

    return {
        "id": anthropic_response.get("id", "msg-adapter"),
        "object": "chat.completion",
        "created": anthropic_response.get("stop_reason", "end_turn"),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content_text,
                },
                "finish_reason": anthropic_response.get("stop_reason", "end_turn"),
            }
        ],
        "usage": {
            "prompt_tokens": anthropic_response.get("usage", {}).get("input_tokens", 0),
            "completion_tokens": anthropic_response.get("usage", {}).get("output_tokens", 0),
            "total_tokens": (
                anthropic_response.get("usage", {}).get("input_tokens", 0)
                + anthropic_response.get("usage", {}).get("output_tokens", 0)
            ),
        },
    }


async def call_anthropic_api(anthropic_request: Dict[str, Any]) -> Dict[str, Any]:
    """Call the Anthropic messages API endpoint."""
    key = load_anthropic_key()
    url = "https://api.z.ai/api/anthropic/v1/messages"

    headers = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=anthropic_request, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                raise RuntimeError(f"Anthropic API error {response.status}: {error_text}")
            return await response.json()


class AdapterHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the adapter."""

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress default request logging."""
        pass

    async def handle_post(self) -> None:
        """Handle POST request."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        try:
            openai_request = json.loads(body)
        except json.JSONDecodeError as e:
            self.send_error(400, f"Invalid JSON: {e}")
            return

        try:
            # Translate OpenAI → Anthropic
            anthropic_request = await translate_to_anthropic(openai_request)
            LOGGER.debug(f"Translated request: {anthropic_request}")

            # Call Anthropic API
            anthropic_response = await call_anthropic_api(anthropic_request)
            LOGGER.debug(f"Anthropic response: {anthropic_response}")

            # Translate Anthropic → OpenAI
            model = openai_request.get("model", "glm-5.3")
            openai_response = await translate_from_anthropic(anthropic_response, model)

            # Send response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(openai_response).encode("utf-8"))

        except Exception as e:
            LOGGER.error(f"Error handling request: {e}", exc_info=True)
            self.send_error(500, str(e))

    def do_POST(self) -> None:
        """Handle POST request synchronously."""
        asyncio.run(self.handle_post())

    def do_GET(self) -> None:
        """Handle GET request (health check)."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "service": "anthropic-openai-adapter"}).encode("utf-8"))


def run_adapter(host: str = "127.0.0.1", port: int = 8765) -> None:
    """Run the adapter server."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    server = HTTPServer((host, port), AdapterHandler)
    LOGGER.info(f"Adapter running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("Adapter stopped")
        server.shutdown()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Anthropic → OpenAI protocol adapter")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind to")
    args = parser.parse_args()

    run_adapter(args.host, args.port)
