"""Consent-controlled SQLite memory for ordinary project knowledge only.

Do not store credentials, secrets, highly sensitive personal data, or private records.
Use encrypted storage at the host layer before production deployment.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
import re
import sqlite3
from pathlib import Path
from typing import Any
import uuid
from aurellion_core import ProvenanceLedger

class MemoryPolicyError(PermissionError):
    pass

_SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I),
    re.compile(r"\b(?:sk|pk)_(?:live|test)_[A-Za-z0-9]{12,}\b"),
    re.compile(r"\b(?:seed phrase|recovery phrase|mnemonic phrase)\b", re.I),
)

class ControlledMemory:
    def __init__(self, database_path: str | Path, ledger: ProvenanceLedger) -> None:
        self.database_path = str(database_path)
        self.ledger = ledger
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    memory_id TEXT PRIMARY KEY, namespace TEXT NOT NULL,
                    content TEXT NOT NULL, source_id TEXT NOT NULL,
                    created_at TEXT NOT NULL, expires_at TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            """)

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.database_path)
        db.row_factory = sqlite3.Row
        return db

    def save(self, namespace: str, content: str, source_id: str, *,
             consent_granted: bool = False, retention_days: int = 30,
             sensitivity: str = "ordinary") -> str:
        if not consent_granted:
            raise MemoryPolicyError("Explicit consent is required for durable memory writes.")
        if sensitivity != "ordinary":
            raise MemoryPolicyError("Only ordinary, non-sensitive project knowledge may be stored.")
        if not namespace or not source_id or not content.strip():
            raise ValueError("Namespace, source ID, and content are required.")
        if retention_days < 1 or retention_days > 365:
            raise ValueError("Retention must be between 1 and 365 days.")
        if any(pattern.search(content) for pattern in _SECRET_PATTERNS):
            raise MemoryPolicyError("Content resembles a secret or credential and cannot be stored.")
        now = datetime.now(timezone.utc)
        memory_id = str(uuid.uuid4())
        created_at = now.isoformat()
        expires_at = (now + timedelta(days=retention_days)).isoformat()
        with self._connect() as db:
            db.execute("INSERT INTO memories VALUES (?, ?, ?, ?, ?, ?, 'active')",
                       (memory_id, namespace, content, source_id, created_at, expires_at))
        self.ledger.append("aurellion-memory", "memory_saved", {
            "memory_id": memory_id, "namespace": namespace,
            "source_id": source_id, "expires_at": expires_at,
        })
        return memory_id

    def recall(self, namespace: str, *, limit: int = 20) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            db.execute("UPDATE memories SET status='expired' WHERE status='active' AND expires_at <= ?", (now,))
            rows = db.execute(
                "SELECT memory_id, content, source_id, created_at, expires_at "
                "FROM memories WHERE namespace=? AND status='active' AND expires_at>? "
                "ORDER BY created_at DESC LIMIT ?",
                (namespace, now, max(1, min(limit, 100))),
            ).fetchall()
        return [dict(row) for row in rows]

    def delete(self, memory_id: str, *, explicit_request: bool = False) -> bool:
        if not explicit_request:
            raise MemoryPolicyError("An explicit deletion request is required.")
        with self._connect() as db:
            cursor = db.execute("UPDATE memories SET status='deleted', content='' WHERE memory_id=? AND status='active'", (memory_id,))
        if cursor.rowcount:
            self.ledger.append("aurellion-memory", "memory_deleted", {"memory_id": memory_id})
            return True
        return False
