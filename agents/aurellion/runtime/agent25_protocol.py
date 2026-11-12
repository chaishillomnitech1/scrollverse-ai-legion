"""Authenticated Agent 25 federation envelopes.

This module signs/verifies messages; it does not open sockets or bypass the host
policy gateway. Use TLS for transport and unique per-peer shared keys.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import sqlite3
import time
from pathlib import Path
import secrets
from typing import Any, Callable

class FederationAuthError(PermissionError):
    pass

def _canonical(envelope: dict[str, Any]) -> bytes:
    return json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def create_envelope(sender: str, recipient: str, message_type: str, payload: dict[str, Any],
                    shared_key: bytes, *, ttl_seconds: int = 120, now: int | None = None) -> dict[str, Any]:
    current = int(time.time()) if now is None else int(now)
    if len(shared_key) < 32:
        raise ValueError("Federation shared key must contain at least 32 bytes.")
    if not sender or not recipient or not message_type or not isinstance(payload, dict):
        raise ValueError("Sender, recipient, message type, and object payload are required.")
    if not 1 <= ttl_seconds <= 300:
        raise ValueError("Message TTL must be between 1 and 300 seconds.")
    envelope = {
        "version": 1, "sender": sender, "recipient": recipient,
        "message_type": message_type, "issued_at": current,
        "expires_at": current + ttl_seconds, "nonce": secrets.token_urlsafe(24),
        "payload": payload,
    }
    envelope["signature"] = hmac.new(shared_key, _canonical(envelope), hashlib.sha256).hexdigest()
    return envelope

class ReplayGuard:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.database_path) as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS used_nonces (
                    sender TEXT NOT NULL, nonce TEXT NOT NULL, expires_at INTEGER NOT NULL,
                    PRIMARY KEY(sender, nonce)
                )
            """)

    def consume(self, sender: str, nonce: str, expires_at: int, now: int) -> None:
        with sqlite3.connect(self.database_path) as db:
            db.execute("DELETE FROM used_nonces WHERE expires_at < ?", (now,))
            try:
                db.execute("INSERT INTO used_nonces(sender, nonce, expires_at) VALUES (?, ?, ?)", (sender, nonce, expires_at))
            except sqlite3.IntegrityError:
                raise FederationAuthError("Message replay detected.") from None

def verify_envelope(envelope: dict[str, Any], *, expected_recipient: str,
                    key_lookup: Callable[[str], bytes | None], replay_guard: ReplayGuard,
                    allowed_message_types: set[str], now: int | None = None,
                    max_clock_skew_seconds: int = 30) -> dict[str, Any]:
    current = int(time.time()) if now is None else int(now)
    required = {"version", "sender", "recipient", "message_type", "issued_at",
                "expires_at", "nonce", "payload", "signature"}
    if not isinstance(envelope, dict) or set(envelope) != required:
        raise FederationAuthError("Message envelope schema is invalid.")
    sender = envelope["sender"]
    if envelope["version"] != 1 or envelope["recipient"] != expected_recipient:
        raise FederationAuthError("Protocol version or recipient is invalid.")
    if envelope["message_type"] not in allowed_message_types:
        raise FederationAuthError("Message type is not permitted.")
    if not isinstance(envelope["payload"], dict) or len(_canonical(envelope)) > 65536:
        raise FederationAuthError("Payload type or size is invalid.")
    issued, expires = envelope["issued_at"], envelope["expires_at"]
    if not isinstance(issued, int) or not isinstance(expires, int):
        raise FederationAuthError("Message timestamps are invalid.")
    if issued > current + max_clock_skew_seconds or issued < current - 300 or expires < current or expires - issued > 300:
        raise FederationAuthError("Message is expired or outside the permitted clock window.")
    nonce = envelope["nonce"]
    if not isinstance(nonce, str) or len(nonce) < 16:
        raise FederationAuthError("Message nonce is invalid.")
    key = key_lookup(sender)
    if not key or len(key) < 32:
        raise FederationAuthError("Sender identity has no configured peer key.")
    unsigned = {key_name: value for key_name, value in envelope.items() if key_name != "signature"}
    expected = hmac.new(key, _canonical(unsigned), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, str(envelope["signature"])):
        raise FederationAuthError("Message authentication failed.")
    replay_guard.consume(sender, nonce, expires, current)
    return {"sender": sender, "recipient": envelope["recipient"],
            "message_type": envelope["message_type"], "payload": envelope["payload"],
            "authenticated": True}
