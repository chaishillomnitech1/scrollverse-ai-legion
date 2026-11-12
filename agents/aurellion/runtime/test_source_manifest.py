import unittest
from pathlib import Path

from source_manifest import load_registry


class SourceManifestTests(unittest.TestCase):
    def test_public_manifest_loads_and_returns_cited_source_hits(self):
        repository_root = Path(__file__).resolve().parents[3]
        registry = load_registry(repository_root, "agents/aurellion/knowledge/sources.json")
        hits = registry.search("AURELLION provenance", scopes=("public",), limit=5)
        self.assertTrue(hits)
        self.assertTrue(all(hit.sha256 and hit.line_start > 0 for hit in hits))

    def test_manifest_does_not_make_project_private_sources_public(self):
        repository_root = Path(__file__).resolve().parents[3]
        registry = load_registry(repository_root, "agents/aurellion/knowledge/sources.json")
        self.assertEqual(registry.search("private conversations", scopes=("project-private",)), [])


if __name__ == "__main__":
    unittest.main()
