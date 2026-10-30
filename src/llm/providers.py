"""Small adapters for Groq and a local Ollama server."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Protocol
from urllib.error import URLError
from urllib.request import Request, urlopen


class ChatProvider(Protocol):
    def complete(self, messages: list[dict[str, str]]) -> str: ...


@dataclass
class GroqProvider:
    api_key: str
    # Groq retired its Llama chat models; the project's Llama 3.1 runs through Ollama instead.
    model: str = "openai/gpt-oss-120b"

    def complete(self, messages: list[dict[str, str]]) -> str:
        from groq import Groq

        response = Groq(api_key=self.api_key, timeout=45.0).chat.completions.create(
            model=self.model, messages=messages, temperature=0
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Groq returned an empty response")
        return content


@dataclass
class OllamaProvider:
    model: str = "llama3.1"
    base_url: str = "http://localhost:11434"
    # CPU-only machines need ~3 min for the report task with llama3.1 8B.
    timeout: float = 600.0

    def complete(self, messages: list[dict[str, str]]) -> str:
        payload = json.dumps({"model": self.model, "messages": messages, "stream": False}).encode()
        request = Request(
            f"{self.base_url.rstrip('/')}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                content = json.load(response)["message"]["content"]
        except (URLError, TimeoutError, KeyError, ValueError) as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc
        if not content:
            raise RuntimeError("Ollama returned an empty response")
        return content


@dataclass
class FallbackProvider:
    primary: ChatProvider
    fallback: ChatProvider

    def complete(self, messages: list[dict[str, str]]) -> str:
        try:
            return self.primary.complete(messages)
        except Exception as primary_error:
            try:
                return self.fallback.complete(messages)
            except Exception as fallback_error:
                raise RuntimeError(
                    f"Both LLM providers failed: Groq ({primary_error}); Ollama ({fallback_error})"
                ) from fallback_error


def make_provider(choice: str = "auto") -> ChatProvider:
    """Auto uses Groq when configured and falls back to Ollama on an API failure."""
    if choice not in {"auto", "groq", "ollama"}:
        raise ValueError(f"Unknown provider: {choice}")
    ollama = OllamaProvider(
        model=os.getenv("OLLAMA_MODEL", "llama3.1"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        timeout=float(os.getenv("OLLAMA_TIMEOUT", "600")),
    )
    if choice == "ollama":
        return ollama
    api_key = os.getenv("GROQ_API_KEY", "")
    if choice == "groq" and not api_key:
        raise RuntimeError("GROQ_API_KEY is required for --provider groq")
    if not api_key:
        return ollama
    groq = GroqProvider(api_key=api_key, model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"))
    return groq if choice == "groq" else FallbackProvider(groq, ollama)
