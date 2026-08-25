"""Provider-agnostic LLM client. Credentials come from the environment only."""

from __future__ import annotations

import json
import os
import re
import time
from abc import ABC, abstractmethod
from typing import Any

import requests

JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(\{.*\})\s*```", re.DOTALL)


class LLMError(RuntimeError):
    pass


class LLMProvider(ABC):
    def __init__(self, model: str) -> None:
        self.model = model

    @abstractmethod
    def generate(self, prompt: str, *, system: str | None = None, max_tokens: int = 4000) -> str:
        raise NotImplementedError

    def generate_structured(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int = 4000,
    ) -> dict[str, Any]:
        body = prompt.rstrip() + "\n\nRespond with a single JSON object and no other text."
        text = self.generate(body, system=system, max_tokens=max_tokens)
        return parse_json_object(text)


class OpenAIProvider(LLMProvider):
    def generate(self, prompt: str, *, system: str | None = None, max_tokens: int = 4000) -> str:
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise LLMError("OPENAI_API_KEY is not set")
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "response_format": {"type": "json_object"} if "json" in prompt.lower() else None,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        data = _post(
            "https://api.openai.com/v1/chat/completions",
            payload,
            {"Authorization": f"Bearer {key}"},
        )
        return data["choices"][0]["message"]["content"]


class AnthropicProvider(LLMProvider):
    def generate(self, prompt: str, *, system: str | None = None, max_tokens: int = 4000) -> str:
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise LLMError("ANTHROPIC_API_KEY is not set")
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            payload["system"] = system
        data = _post(
            "https://api.anthropic.com/v1/messages",
            payload,
            {
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
            },
        )
        parts = data.get("content") or []
        return "".join(part.get("text", "") for part in parts if part.get("type") == "text")


class GeminiProvider(LLMProvider):
    def generate(self, prompt: str, *, system: str | None = None, max_tokens: int = 4000) -> str:
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise LLMError("GEMINI_API_KEY is not set")
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
            f"?key={key}"
        )
        contents = []
        if system:
            contents.append({"role": "user", "parts": [{"text": f"System instructions:\n{system}"}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})
        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.2,
            },
        }
        data = _post(url, payload, {})
        candidates = data.get("candidates") or []
        if not candidates:
            raise LLMError(f"Gemini returned no candidates: {data}")
        parts = (candidates[0].get("content") or {}).get("parts") or []
        return "".join(part.get("text", "") for part in parts)


class MockProvider(LLMProvider):
    """Deterministic stand-in for tests. Never talks to a network."""

    def __init__(self, model: str = "mock", canned: dict[str, Any] | None = None) -> None:
        super().__init__(model)
        self.canned = canned or {}
        self.calls: list[str] = []

    def generate(self, prompt: str, *, system: str | None = None, max_tokens: int = 4000) -> str:
        self.calls.append(prompt)
        if "json" in prompt.lower() or "JSON" in (system or ""):
            return json.dumps(self.canned.get("structured") or {"ok": True})
        return str(self.canned.get("text") or "mock generation")

    def generate_structured(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int = 4000,
    ) -> dict[str, Any]:
        self.calls.append(prompt)
        value = self.canned.get("structured")
        if isinstance(value, list):
            if not value:
                return {}
            return value.pop(0)
        if isinstance(value, dict):
            return value
        return parse_json_object(self.generate(prompt, system=system, max_tokens=max_tokens))


def parse_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    match = JSON_FENCE_RE.search(text)
    if match:
        text = match.group(1)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise LLMError(f"Expected a JSON object, got: {text[:300]}")
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise LLMError(f"Invalid JSON from model: {exc}") from exc
    if not isinstance(data, dict):
        raise LLMError("Structured response was not an object")
    return data


def _post(url: str, payload: dict[str, Any], headers: dict[str, str]) -> Any:
    hdrs = {"Content-Type": "application/json", **headers}
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            response = requests.post(url, json=payload, headers=hdrs, timeout=120)
        except requests.RequestException as exc:
            last_error = exc
            time.sleep(2**attempt)
            continue
        if response.status_code in {429, 502, 503, 504}:
            last_error = LLMError(f"{response.status_code} {response.text[:200]}")
            time.sleep(2**attempt)
            continue
        if response.status_code >= 400:
            raise LLMError(f"LLM HTTP {response.status_code}: {response.text[:400]}")
        return response.json()
    raise LLMError(str(last_error) if last_error else "LLM request failed")


def get_provider(name: str | None = None, model: str | None = None) -> LLMProvider:
    provider = (name or os.environ.get("LLM_PROVIDER") or "openai").strip().lower()
    model_name = model or os.environ.get("LLM_MODEL") or _default_model(provider)
    if provider == "openai":
        return OpenAIProvider(model_name)
    if provider == "anthropic":
        return AnthropicProvider(model_name)
    if provider in {"gemini", "google"}:
        return GeminiProvider(model_name)
    if provider == "mock":
        return MockProvider(model_name)
    raise LLMError(f"Unknown LLM_PROVIDER: {provider}")


def _default_model(provider: str) -> str:
    return {
        "openai": "gpt-4o",
        "anthropic": "claude-sonnet-4-5",
        "gemini": "gemini-2.0-flash",
        "google": "gemini-2.0-flash",
        "mock": "mock",
    }.get(provider, "gpt-4o")
