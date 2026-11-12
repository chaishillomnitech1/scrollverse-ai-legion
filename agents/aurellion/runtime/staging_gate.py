"""Validate staging configuration without deploying or revealing secret values."""
from __future__ import annotations
import os
from urllib.parse import urlparse
from typing import Mapping

def validate_staging_environment(env: Mapping[str, str] | None = None) -> list[str]:
    values = os.environ if env is None else env
    errors: list[str] = []
    if not values.get("AURELLION_PROVIDER", "").strip():
        errors.append("AURELLION_PROVIDER is missing.")
    if not values.get("AURELLION_MODEL", "").strip():
        errors.append("AURELLION_MODEL is missing.")
    if not values.get("AURELLION_API_KEY", ""):
        errors.append("AURELLION_API_KEY is missing.")
    endpoint = urlparse(values.get("AURELLION_API_BASE_URL", ""))
    api_style = values.get("AURELLION_API_STYLE", "responses").strip().lower()
    if api_style not in {"responses", "chat_completions"}:
        errors.append("AURELLION_API_STYLE must be responses or chat_completions.")
    hosts = {h.strip().lower() for h in values.get("AURELLION_ALLOWED_PROVIDER_HOSTS", "").split(",") if h.strip()}
    if endpoint.scheme != "https" or not endpoint.hostname or endpoint.username or endpoint.password:
        errors.append("AURELLION_API_BASE_URL must be HTTPS and contain no embedded credentials.")
    elif endpoint.hostname.lower() not in hosts or "*" in hosts:
        errors.append("Provider endpoint host is not in the exact allowlist.")
    elif api_style == "responses" and endpoint.path.rstrip("/") != "/v1/responses":
        errors.append("Responses API style requires the /v1/responses endpoint.")
    elif api_style == "chat_completions" and endpoint.path.rstrip("/") != "/v1/chat/completions":
        errors.append("Chat Completions style requires the /v1/chat/completions endpoint.")
    origins = [item.strip() for item in values.get("AURELLION_ALLOWED_ORIGINS", "").split(",") if item.strip()]
    if not origins:
        errors.append("AURELLION_ALLOWED_ORIGINS is missing.")
    for origin in origins:
        parsed = urlparse(origin)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.path not in {"", "/"} or parsed.query or parsed.fragment or "*" in origin:
            errors.append("Every allowed origin must be an exact HTTPS origin without path, query, fragment, or wildcard.")
            break
    redis_url = urlparse(values.get("REDIS_URL", ""))
    if values.get("RATE_LIMIT_ENABLED", "").lower() != "true":
        errors.append("RATE_LIMIT_ENABLED must be true for staging.")
    if len(values.get("AURELLION_RATE_LIMIT_PEPPER", "")) < 32:
        errors.append("AURELLION_RATE_LIMIT_PEPPER must be provisioned in the secret manager.")
    if redis_url.scheme != "rediss" or not redis_url.hostname:
        errors.append("REDIS_URL must use TLS (rediss://) and have a hostname.")
    if values.get("TRUSTED_PROXY_HOPS", "") not in {"1", "2", "3"}:
        errors.append("TRUSTED_PROXY_HOPS must be explicitly set to 1, 2, or 3 after ingress verification.")
    if not values.get("AGENT25_PEER_ID", "").strip():
        errors.append("AGENT25_PEER_ID is missing.")
    if len(values.get("AGENT25_SHARED_SECRET", "")) < 32:
        errors.append("AGENT25_SHARED_SECRET must be provisioned as a per-peer secret of at least 32 characters.")
    return errors

def main() -> int:
    errors = validate_staging_environment()
    if errors:
        print("STAGING CONFIGURATION: BLOCKED")
        for error in errors:
            print("- " + error)
        return 1
    print("STAGING CONFIGURATION: VALIDATED (configuration only; no deployment performed)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
