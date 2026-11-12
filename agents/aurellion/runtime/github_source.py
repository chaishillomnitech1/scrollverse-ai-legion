"""Read-only GitHub Contents API adapter for explicitly allowlisted repositories."""
from __future__ import annotations
from dataclasses import dataclass
import base64
import hashlib
import json
from typing import Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

class GitHubSourceError(RuntimeError):
    """Sanitized source adapter error; never includes tokens or response secrets."""

@dataclass(frozen=True)
class GitHubSourceDocument:
    repository: str
    path: str
    ref: str
    scope: str
    content: str
    git_blob_sha: str
    raw_sha256: str
    html_url: str

class GitHubReadOnlyAdapter:
    API_ROOT = "https://api.github.com"
    MAX_BYTES = 2_000_000

    def __init__(self, token: str, allowlist: Mapping[str, Mapping[str, object]], timeout_seconds: int = 20) -> None:
        if not token:
            raise ValueError("A read-only GitHub token must be injected by the host.")
        if timeout_seconds < 1 or timeout_seconds > 60:
            raise ValueError("Timeout must be between 1 and 60 seconds.")
        self._token = token
        self._allowlist = dict(allowlist)
        self.timeout_seconds = timeout_seconds

    def _authorized(self, repository: str, path: str, ref: str) -> str:
        entry = self._allowlist.get(repository)
        if not entry:
            raise GitHubSourceError("Repository is not in the explicit source allowlist.")
        candidate = path.strip("/")
        if not candidate or path.startswith("/") or ".." in candidate.split("/"):
            raise GitHubSourceError("Source path is invalid.")
        allowed_paths = tuple(str(x).strip("/") for x in entry.get("paths", ()))
        if not any(candidate == prefix or candidate.startswith(prefix + "/") for prefix in allowed_paths):
            raise GitHubSourceError("Source path is outside the registered path allowlist.")
        allowed_refs = tuple(str(x) for x in entry.get("refs", ("main",)))
        if ref not in allowed_refs:
            raise GitHubSourceError("Git ref is not allowlisted for this repository.")
        scope = str(entry.get("scope", ""))
        if scope not in {"public", "project-private"}:
            raise GitHubSourceError("Source scope is invalid.")
        return scope

    def fetch(self, repository: str, path: str, *, ref: str = "main") -> GitHubSourceDocument:
        scope = self._authorized(repository, path, ref)
        parts = repository.split("/")
        if len(parts) != 2 or not all(parts):
            raise GitHubSourceError("Repository must use owner/name form.")
        encoded_path = quote(path.strip("/"), safe="/")
        url = f"{self.API_ROOT}/repos/{quote(parts[0])}/{quote(parts[1])}/contents/{encoded_path}?ref={quote(ref, safe='')}"
        request = Request(url, headers={
            "Authorization": "Bearer " + self._token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "AURELLION-ReadOnly-Source-Adapter",
        }, method="GET")
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise GitHubSourceError("GitHub source request returned HTTP status " + str(exc.code) + ".") from None
        except (URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError):
            raise GitHubSourceError("GitHub source request failed or returned invalid JSON.") from None
        if payload.get("type") != "file" or payload.get("encoding") != "base64":
            raise GitHubSourceError("GitHub response is not a base64 file object.")
        encoded = "".join(str(payload.get("content", "")).split())
        try:
            raw = base64.b64decode(encoded, validate=True)
            content = raw.decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            raise GitHubSourceError("GitHub file content could not be decoded safely.") from None
        if len(raw) > self.MAX_BYTES:
            raise GitHubSourceError("GitHub source exceeds the configured size limit.")
        return GitHubSourceDocument(
            repository=repository, path=path, ref=ref, scope=scope,
            content=content, git_blob_sha=str(payload.get("sha", "")),
            raw_sha256=hashlib.sha256(raw).hexdigest(),
            html_url=str(payload.get("html_url", "")),
        )


def load_public_allowlist(manifest_path: str) -> dict[str, dict[str, object]]:
    """Load only public repository entries from the versioned JSON allowlist."""
    from pathlib import Path
    data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or data.get("scope") != "public-only":
        raise GitHubSourceError("Public GitHub allowlist schema or scope is invalid.")
    result: dict[str, dict[str, object]] = {}
    for item in data.get("repositories", []):
        if item.get("scope") != "public":
            continue
        full_name = str(item.get("full_name", ""))
        branch = str(item.get("default_branch", ""))
        if full_name.count("/") != 1 or not branch:
            raise GitHubSourceError("Public allowlist contains an invalid repository entry.")
        result[full_name] = {
            "scope": "public",
            "refs": [branch],
            "paths": [str(path) for path in item.get("paths", [])],
        }
    return result
