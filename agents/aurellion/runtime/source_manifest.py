"""Load an explicit, versioned source manifest into SourceRegistry."""
from __future__ import annotations
import json
from pathlib import Path
from retrieval import SourceRecord, SourceRegistry, SourceAccessError

def load_registry(root: str | Path, manifest_path: str | Path) -> SourceRegistry:
    root_path = Path(root).resolve(strict=True)
    manifest_file = (root_path / manifest_path).resolve(strict=True)
    if root_path not in manifest_file.parents or not manifest_file.is_file():
        raise SourceAccessError("Manifest must be inside the authorized project root.")
    data = json.loads(manifest_file.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("sources"), list):
        raise SourceAccessError("Source manifest schema is unsupported.")
    registry = SourceRegistry(root_path)
    seen: set[str] = set()
    for item in data["sources"]:
        if not isinstance(item, dict):
            raise SourceAccessError("Manifest entries must be objects.")
        source_id = item.get("source_id")
        if source_id in seen:
            raise SourceAccessError("Duplicate source ID in manifest.")
        seen.add(source_id)
        registry.register(SourceRecord(
            source_id=source_id,
            relative_path=item.get("path", ""),
            scope=item.get("scope", ""),
            authorized_by=item.get("authorized_by", ""),
            expected_sha256=item.get("expected_sha256"),
        ))
    return registry
