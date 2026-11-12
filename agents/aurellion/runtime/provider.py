"""Provider-neutral model interface with a replaceable OpenAI-compatible adapter.

No credentials are stored here. Configuration is read from environment variables.
The adapter makes no request until generate() is explicitly called by its host.
"""
from __future__ import annotations
from dataclasses import dataclass
import json
import os
from typing import Any, Mapping, Protocol, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

class ProviderConfigurationError(ValueError):
    pass

class ProviderRequestError(RuntimeError):
    """Sanitized provider error; never includes request headers or secret values."""

@dataclass(frozen=True)
class ProviderConfig:
    provider: str
    endpoint: str
    model: str
    api_key: str
    allowed_hosts: tuple[str, ...]
    timeout_seconds: int = 30
    api_style: str = "responses"

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "ProviderConfig":
        values = os.environ if env is None else env
        config = cls(
            provider=values.get("AURELLION_PROVIDER", "").strip(),
            endpoint=values.get("AURELLION_API_BASE_URL", "").strip(),
            model=values.get("AURELLION_MODEL", "").strip(),
            api_key=values.get("AURELLION_API_KEY", ""),
            allowed_hosts=tuple(host.strip().lower() for host in values.get("AURELLION_ALLOWED_PROVIDER_HOSTS", "").split(",") if host.strip()),
            timeout_seconds=int(values.get("AURELLION_PROVIDER_TIMEOUT", "30")),
            api_style=values.get("AURELLION_API_STYLE", "responses").strip().lower(),
        )
        config.validate()
        return config

    def validate(self) -> None:
        if not self.provider or not self.model or not self.api_key:
            raise ProviderConfigurationError("Provider name, model, and API credential are required.")
        parsed = urlparse(self.endpoint)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ProviderConfigurationError("Provider endpoint must be an HTTPS URL without embedded credentials.")
        if not self.allowed_hosts or parsed.hostname.lower() not in self.allowed_hosts:
            raise ProviderConfigurationError("Provider endpoint hostname is not in the exact allowlist.")
        if "*" in self.allowed_hosts or self.timeout_seconds < 1 or self.timeout_seconds > 120:
            raise ProviderConfigurationError("Wildcard hosts are forbidden and timeout must be between 1 and 120 seconds.")
        if self.api_style not in {"responses", "chat_completions"}:
            raise ProviderConfigurationError("AURELLION_API_STYLE must be responses or chat_completions.")

@dataclass(frozen=True)
class ModelResponse:
    provider: str
    model: str
    response: str
    request_id: str | None
    usage: Mapping[str, Any]
    finish_reason: str | None

class ModelProvider(Protocol):
    def generate(self, messages: Sequence[Mapping[str, str]], *, temperature: float = 0.2, max_tokens: int = 1200) -> ModelResponse:
        ...

class OpenAICompatibleProvider:
    """Adapter for OpenAI-compatible Chat Completions endpoints."""
    def __init__(self, config: ProviderConfig) -> None:
        config.validate()
        self.config = config

    def generate(self, messages: Sequence[Mapping[str, str]], *, temperature: float = 0.2, max_tokens: int = 1200) -> ModelResponse:
        if not messages:
            raise ValueError("At least one message is required.")
        if not 0 <= temperature <= 2 or not 1 <= max_tokens <= 8192:
            raise ValueError("Generation limits are outside the allowed range.")
        safe_messages = []
        for message in messages:
            role, content = message.get("role"), message.get("content")
            if role not in {"system", "user", "assistant"} or not isinstance(content, str):
                raise ValueError("Messages must contain an allowed role and string content.")
            safe_messages.append({"role": role, "content": content})
        body = json.dumps({
            "model": self.config.model,
            "messages": safe_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }).encode("utf-8")
        request = Request(
            self.config.endpoint, data=body,
            headers={"Authorization": "Bearer " + self.config.api_key, "Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.config.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise ProviderRequestError("Provider returned HTTP status " + str(exc.code) + ".") from None
        except (URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError):
            raise ProviderRequestError("Provider request failed or returned invalid JSON.") from None
        try:
            choice = payload["choices"][0]
            text = choice["message"]["content"]
            if not isinstance(text, str):
                raise TypeError
        except (KeyError, IndexError, TypeError):
            raise ProviderRequestError("Provider response did not match the expected chat-completion schema.") from None
        return ModelResponse(
            provider=self.config.provider, model=str(payload.get("model", self.config.model)),
            response=text, request_id=payload.get("id"), usage=payload.get("usage") or {},
            finish_reason=choice.get("finish_reason"),
        )


class OpenAIResponsesProvider:
    """OpenAI Responses API adapter for new OpenAI integrations.

    Application-managed history is sent as input. store=False avoids creating
    provider-side response state for this request.
    """
    def __init__(self, config: ProviderConfig) -> None:
        config.validate()
        if config.api_style != "responses":
            raise ProviderConfigurationError("OpenAIResponsesProvider requires api_style=responses.")
        self.config = config

    def generate(self, messages: Sequence[Mapping[str, str]], *,
                 temperature: float = 0.2, max_tokens: int = 1200) -> ModelResponse:
        if not messages:
            raise ValueError("At least one message is required.")
        if not 1 <= max_tokens <= 8192:
            raise ValueError("Output token limit is outside the allowed range.")
        safe_input = []
        for message in messages:
            role, content = message.get("role"), message.get("content")
            if role not in {"system", "user", "assistant"} or not isinstance(content, str):
                raise ValueError("Messages must contain an allowed role and string content.")
            safe_input.append({"role": role, "content": content})
        body = json.dumps({
            "model": self.config.model,
            "input": safe_input,
            "max_output_tokens": max_tokens,
            "store": False,
        }).encode("utf-8")
        request = Request(
            self.config.endpoint, data=body,
            headers={"Authorization": "Bearer " + self.config.api_key,
                     "Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.config.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise ProviderRequestError("Provider returned HTTP status " + str(exc.code) + ".") from None
        except (URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError):
            raise ProviderRequestError("Provider request failed or returned invalid JSON.") from None

        output_text = payload.get("output_text")
        if not isinstance(output_text, str):
            parts = []
            for item in payload.get("output", []):
                if item.get("type") == "message":
                    for part in item.get("content", []):
                        if part.get("type") == "output_text" and isinstance(part.get("text"), str):
                            parts.append(part["text"])
            output_text = "".join(parts)
        if not output_text:
            raise ProviderRequestError("Provider response did not contain output text.")
        return ModelResponse(
            provider=self.config.provider, model=str(payload.get("model", self.config.model)),
            response=output_text, request_id=payload.get("id"),
            usage=payload.get("usage") or {}, finish_reason=payload.get("status"),
        )


def build_provider(config: ProviderConfig) -> ModelProvider:
    """Select an adapter from explicit configuration; never infer an endpoint style."""
    if config.api_style == "responses":
        return OpenAIResponsesProvider(config)
    if config.api_style == "chat_completions":
        return OpenAICompatibleProvider(config)
    raise ProviderConfigurationError("Unsupported provider API style.")
