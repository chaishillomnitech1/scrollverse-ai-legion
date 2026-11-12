"""Shared Redis rate limiter with atomic sliding-window enforcement.

The Redis client is injected by the host. Use a TLS Redis URL and keep the
pepper in the secret manager. Raw visitor identifiers are never stored.
"""
from __future__ import annotations
import hashlib
import hmac
import uuid
from dataclasses import dataclass
from urllib.parse import urlparse

class RateLimitConfigurationError(ValueError):
    pass

@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    current_count: int
    limit: int
    window_seconds: int

class RedisSlidingWindowRateLimiter:
    LUA = """
    local key = KEYS[1]
    local window_ms = tonumber(ARGV[1])
    local limit = tonumber(ARGV[2])
    local request_id = ARGV[3]
    local clock = redis.call('TIME')
    local now_ms = (tonumber(clock[1]) * 1000) + math.floor(tonumber(clock[2]) / 1000)
    redis.call('ZREMRANGEBYSCORE', key, '-inf', now_ms - window_ms)
    local count = redis.call('ZCARD', key)
    if count >= limit then
      redis.call('PEXPIRE', key, window_ms)
      return {0, count}
    end
    redis.call('ZADD', key, now_ms, request_id .. ':' .. now_ms)
    redis.call('PEXPIRE', key, window_ms)
    return {1, count + 1}
    """

    def __init__(self, redis_client, *, redis_url: str, pepper: str,
                 namespace: str = "aurellion:visitor") -> None:
        parsed = urlparse(redis_url)
        if parsed.scheme != "rediss" or not parsed.hostname:
            raise RateLimitConfigurationError("A TLS Redis URL (rediss://) is required.")
        if len(pepper) < 32:
            raise RateLimitConfigurationError("Rate-limit subject pepper must be at least 32 characters.")
        if not namespace or any(ch.isspace() for ch in namespace):
            raise RateLimitConfigurationError("Rate-limit namespace is invalid.")
        self.client = redis_client
        self.pepper = pepper.encode("utf-8")
        self.namespace = namespace

    def check(self, subject: str, *, limit: int, window_seconds: int) -> RateLimitDecision:
        if not subject or not 1 <= limit <= 10000 or not 1 <= window_seconds <= 86400:
            raise ValueError("Rate-limit subject, limit, or window is invalid.")
        digest = hmac.new(self.pepper, subject.encode("utf-8"), hashlib.sha256).hexdigest()
        key = self.namespace + ":" + digest
        request_id = uuid.uuid4().hex
        result = self.client.eval(self.LUA, 1, key, window_seconds * 1000, limit, request_id)
        allowed, count = int(result[0]), int(result[1])
        return RateLimitDecision(bool(allowed), count, limit, window_seconds)
