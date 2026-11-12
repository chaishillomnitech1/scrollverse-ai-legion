"""Minimal AURELLION governance primitives.

No model provider, network client, shell execution, or external tool is invoked.
The JSONL hash chain is tamper-evident, not tamper-proof.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str
    action: str
    scope: str


class PolicyGate:
    """Default-deny gate; approval must match the exact requested scope."""

    def __init__(self, read_only_actions: Iterable[str] = ()) -> None:
        self._read_only_actions = frozenset(read_only_actions)

    def authorize(self, action: str, scope: str, *, explicit_approval: bool = False,
                  approval_scope: str | None = None) -> Decision:
        if not action or not scope:
            return Decision(False, "Action and scope are required.", action, scope)
        if action in self._read_only_actions:
            return Decision(True, "Read-only action is allowlisted.", action, scope)
        if explicit_approval and approval_scope == scope:
            return Decision(True, "Approval matches the exact requested scope.", action, scope)
        return Decision(False, "Denied by default: explicit approval for this exact scope is required.",
                        action, scope)


def _canonical(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class ProvenanceLedger:
    """JSONL event chain; protect and externally anchor its latest hash."""

    GENESIS = "0" * 64

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def _read(self) -> list[dict[str, Any]]:
        rows = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows

    def append(self, actor: str, event: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not actor or not event:
            raise ValueError("actor and event are required")
        rows = self._read()
        prior = rows[-1]["record_hash"] if rows else self.GENESIS
        body = {"sequence": len(rows) + 1,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": actor, "event": event, "payload": payload,
                "previous_hash": prior}
        record = dict(body)
        record["record_hash"] = _digest(_canonical(body))
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(_canonical(record) + "\n")
        return record

    def verify(self) -> bool:
        prior = self.GENESIS
        try:
            for sequence, row in enumerate(self._read(), start=1):
                body = {key: value for key, value in row.items() if key != "record_hash"}
                if body.get("sequence") != sequence or body.get("previous_hash") != prior:
                    return False
                current = _digest(_canonical(body))
                if row.get("record_hash") != current:
                    return False
                prior = current
            return True
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            return False

    def records(self) -> list[dict[str, Any]]:
        return self._read()
