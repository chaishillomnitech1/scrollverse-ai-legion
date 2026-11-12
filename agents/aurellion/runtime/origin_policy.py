"""Exact-origin policy for public visitor endpoints."""
from __future__ import annotations
from urllib.parse import urlparse

class OriginDenied(PermissionError):
    pass

class ExactOriginPolicy:
    def __init__(self, allowed_origins: set[str]) -> None:
        if not allowed_origins:
            raise ValueError("At least one exact origin is required.")
        normalized = set()
        for origin in allowed_origins:
            parsed = urlparse(origin)
            if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.path not in {"", "/"} or parsed.query or parsed.fragment or "*" in origin:
                raise ValueError("Origins must be exact HTTPS origins without path, query, fragment, or wildcard.")
            normalized.add(f"https://{parsed.netloc.lower()}")
        self.allowed_origins = normalized

    def require(self, origin: str | None) -> str:
        if not origin:
            raise OriginDenied("Origin header is required.")
        parsed = urlparse(origin)
        normalized = f"{parsed.scheme}://{parsed.netloc.lower()}"
        if parsed.scheme != "https" or parsed.username or parsed.password or parsed.path not in {"", "/"} or parsed.query or parsed.fragment or normalized not in self.allowed_origins:
            raise OriginDenied("Origin is not approved.")
        return normalized
