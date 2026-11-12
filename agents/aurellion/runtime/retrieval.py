"""Source-aware retrieval over an explicit local allowlist.

This baseline uses deterministic lexical ranking rather than embeddings.
Only sources registered with an authorization reference can be searched.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
from typing import Iterable

class SourceAccessError(PermissionError):
    pass

@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    relative_path: str
    scope: str
    authorized_by: str
    expected_sha256: str | None = None

@dataclass(frozen=True)
class SourceHit:
    source_id: str
    path: str
    sha256: str
    line_start: int
    line_end: int
    score: int
    excerpt: str

    @property
    def citation(self) -> str:
        return f"{self.path}:L{self.line_start}-L{self.line_end} (sha256:{self.sha256})"

class SourceRegistry:
    ALLOWED_SUFFIXES = {".md", ".txt", ".json", ".py", ".yaml", ".yml"}
    MAX_BYTES = 2_000_000

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve(strict=True)
        self._sources: dict[str, SourceRecord] = {}

    def register(self, record: SourceRecord) -> None:
        if not record.source_id or not record.authorized_by:
            raise SourceAccessError("A source ID and explicit authorization reference are required.")
        if record.scope not in {"public", "project-private", "session"}:
            raise SourceAccessError("Unknown source scope.")
        self._resolve(record.relative_path)
        self._sources[record.source_id] = record

    def _resolve(self, relative_path: str) -> Path:
        candidate = Path(relative_path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise SourceAccessError("Absolute paths and traversal are forbidden.")
        resolved = (self.root / candidate).resolve(strict=True)
        if self.root not in resolved.parents or not resolved.is_file():
            raise SourceAccessError("Source must be a regular file inside the authorized root.")
        if resolved.suffix.lower() not in self.ALLOWED_SUFFIXES:
            raise SourceAccessError("File type is not enabled for retrieval.")
        if resolved.stat().st_size > self.MAX_BYTES:
            raise SourceAccessError("Source exceeds the configured size limit.")
        return resolved

    def search(self, query: str, *, scopes: Iterable[str] = ("public",), limit: int = 5, chunk_lines: int = 35) -> list[SourceHit]:
        terms = {term for term in re.findall(r"[a-zA-Z0-9_-]{2,}", query.lower())}
        if not terms:
            return []
        if not 1 <= limit <= 20 or not 5 <= chunk_lines <= 100:
            raise ValueError("Retrieval limits are outside the allowed range.")
        allowed_scopes = set(scopes)
        hits: list[SourceHit] = []
        for record in self._sources.values():
            if record.scope not in allowed_scopes:
                continue
            path = self._resolve(record.relative_path)
            raw = path.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            if record.expected_sha256 and digest != record.expected_sha256:
                raise SourceAccessError("Source hash does not match the registered version.")
            try:
                lines = raw.decode("utf-8").splitlines()
            except UnicodeDecodeError:
                continue
            for start in range(0, len(lines), chunk_lines):
                end = min(start + chunk_lines, len(lines))
                excerpt = "\n".join(lines[start:end])
                tokens = set(re.findall(r"[a-zA-Z0-9_-]{2,}", excerpt.lower()))
                score = len(terms & tokens)
                if score:
                    hits.append(SourceHit(record.source_id, record.relative_path, digest, start + 1, end, score, excerpt[:4000]))
        hits.sort(key=lambda hit: (-hit.score, hit.path, hit.line_start))
        return hits[:limit]
