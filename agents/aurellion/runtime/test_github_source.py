import base64
import json
import tempfile
import unittest
from unittest.mock import patch

from github_source import GitHubReadOnlyAdapter, GitHubSourceError, load_public_allowlist


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return False
    def read(self):
        return self.payload


class GitHubReadOnlyAdapterTests(unittest.TestCase):
    def adapter(self):
        return GitHubReadOnlyAdapter(
            "fake-read-only-token",
            {
                "chaishillomnitech1/scrollverse-ai-legion": {
                    "scope": "public",
                    "refs": ["main"],
                    "paths": ["README.md", "docs/aurellion"],
                }
            },
        )

    def test_fetch_returns_content_and_separate_hashes(self):
        raw = b"# AURELLION public guide"
        payload = {
            "type": "file", "encoding": "base64",
            "content": base64.b64encode(raw).decode("ascii"),
            "sha": "git-blob-sha",
            "html_url": "https://github.com/chaishillomnitech1/scrollverse-ai-legion/blob/main/README.md",
        }
        with patch("github_source.urlopen", return_value=FakeResponse(payload)):
            result = self.adapter().fetch("chaishillomnitech1/scrollverse-ai-legion", "README.md")
        self.assertEqual(result.content, raw.decode("utf-8"))
        self.assertEqual(result.git_blob_sha, "git-blob-sha")
        self.assertEqual(result.scope, "public")
        self.assertEqual(len(result.raw_sha256), 64)


    def test_public_allowlist_loader_excludes_private_entries(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "allowlist.json"
            path.write_text(json.dumps({
                "schema_version": 1, "scope": "public-only",
                "repositories": [
                    {"full_name": "owner/public", "default_branch": "main", "scope": "public",
                     "refs": ["main"], "paths": ["README.md"]},
                    {"full_name": "owner/private", "default_branch": "main", "scope": "project-private",
                     "refs": ["main"], "paths": ["README.md"]},
                ],
            }), encoding="utf-8")
            result = load_public_allowlist(str(path))
            self.assertIn("owner/public", result)
            self.assertNotIn("owner/private", result)

    def test_unlisted_repository_and_path_are_denied(self):
        adapter = self.adapter()
        with self.assertRaises(GitHubSourceError):
            adapter.fetch("someone/private-repo", "README.md")
        with self.assertRaises(GitHubSourceError):
            adapter.fetch("chaishillomnitech1/scrollverse-ai-legion", "../secrets.txt")

    def test_unlisted_ref_is_denied(self):
        with self.assertRaises(GitHubSourceError):
            self.adapter().fetch("chaishillomnitech1/scrollverse-ai-legion", "README.md", ref="feature/other")


if __name__ == "__main__":
    unittest.main()
