import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent25_protocol import FederationAuthError, ReplayGuard, create_envelope, verify_envelope
from memory_store import ControlledMemory, MemoryPolicyError
from provider import OpenAICompatibleProvider, OpenAIResponsesProvider, ProviderConfig, ProviderConfigurationError
from retrieval import SourceAccessError, SourceRecord, SourceRegistry
from staging_gate import validate_staging_environment
from aurellion_core import ProvenanceLedger


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return False
    def read(self):
        return self.payload


class ProviderTests(unittest.TestCase):
    def config(self):
        return ProviderConfig("openai-compatible", "https://api.example.test/v1/chat/completions",
                              "model-test", "not-a-real-key", ("api.example.test",), api_style="chat_completions")

    def test_endpoint_must_match_exact_allowlist(self):
        bad = ProviderConfig("openai", "https://evil.example/v1/chat/completions",
                             "model-test", "x", ("api.example.test",))
        with self.assertRaises(ProviderConfigurationError):
            bad.validate()


    def test_openai_responses_adapter_uses_responses_shape_and_store_false(self):
        config = ProviderConfig(
            "openai", "https://api.openai.com/v1/responses", "model-test",
            "not-a-real-key", ("api.openai.com",), api_style="responses",
        )
        provider = OpenAIResponsesProvider(config)
        payload = {
            "id": "resp-1", "model": "model-test", "status": "completed",
            "output": [{"type": "message", "content": [{"type": "output_text", "text": "connected light"}]}],
            "usage": {"input_tokens": 2, "output_tokens": 2},
        }
        with patch("provider.urlopen", return_value=FakeResponse(payload)) as mocked:
            result = provider.generate([{"role": "user", "content": "hello"}])
        request = mocked.call_args.args[0]
        sent = json.loads(request.data.decode("utf-8"))
        self.assertEqual(result.response, "connected light")
        self.assertFalse(sent["store"])
        self.assertEqual(sent["max_output_tokens"], 1200)

    def test_adapter_parses_compatible_response(self):
        provider = OpenAICompatibleProvider(self.config())
        payload = {"id": "req-1", "model": "model-test",
                   "choices": [{"message": {"content": "hello"}, "finish_reason": "stop"}],
                   "usage": {"total_tokens": 3}}
        with patch("provider.urlopen", return_value=FakeResponse(payload)):
            result = provider.generate([{"role": "user", "content": "hello"}])
        self.assertEqual(result.response, "hello")
        self.assertEqual(result.request_id, "req-1")


class RetrievalTests(unittest.TestCase):
    def test_only_registered_sources_are_searchable(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "public.md").write_text("AURELLION source provenance and archive.", encoding="utf-8")
            registry = SourceRegistry(root)
            registry.register(SourceRecord("doc-1", "public.md", "public", "public-repo-manifest"))
            hits = registry.search("source provenance", scopes=("public",))
            self.assertEqual(len(hits), 1)
            self.assertIn("public.md:L1-L1", hits[0].citation)
            self.assertEqual(registry.search("source provenance", scopes=("project-private",)), [])

    def test_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            outside = root.parent / "outside-aurellion-test.md"
            outside.write_text("private", encoding="utf-8")
            registry = SourceRegistry(root)
            with self.assertRaises(SourceAccessError):
                registry.register(SourceRecord("bad", "../outside-aurellion-test.md", "public", "test"))
            outside.unlink(missing_ok=True)


class MemoryTests(unittest.TestCase):
    def test_memory_requires_consent_and_can_be_deleted(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = ProvenanceLedger(Path(folder) / "events.jsonl")
            memory = ControlledMemory(Path(folder) / "memory.db", ledger)
            with self.assertRaises(MemoryPolicyError):
                memory.save("project", "AURELLION", "doc-1")
            item = memory.save("project", "AURELLION is a project identity.", "doc-1",
                               consent_granted=True, retention_days=10)
            self.assertEqual(len(memory.recall("project")), 1)
            self.assertTrue(memory.delete(item, explicit_request=True))
            self.assertEqual(memory.recall("project"), [])
            self.assertTrue(ledger.verify())

    def test_secret_like_memory_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = ProvenanceLedger(Path(folder) / "events.jsonl")
            memory = ControlledMemory(Path(folder) / "memory.db", ledger)
            with self.assertRaises(MemoryPolicyError):
                memory.save("project", "-----BEGIN PRIVATE KEY-----", "doc-1", consent_granted=True)


class FederationTests(unittest.TestCase):
    def test_authenticated_message_and_replay_rejection(self):
        with tempfile.TemporaryDirectory() as folder:
            key = b"k" * 32
            guard = ReplayGuard(Path(folder) / "replay.db")
            envelope = create_envelope("agent25", "aurellion", "knowledge.query",
                                       {"query": "public docs"}, key, now=1000)
            result = verify_envelope(
                envelope, expected_recipient="aurellion",
                key_lookup=lambda sender: key if sender == "agent25" else None,
                replay_guard=guard, allowed_message_types={"knowledge.query"}, now=1001,
            )
            self.assertTrue(result["authenticated"])
            with self.assertRaises(FederationAuthError):
                verify_envelope(
                    envelope, expected_recipient="aurellion",
                    key_lookup=lambda sender: key,
                    replay_guard=guard, allowed_message_types={"knowledge.query"}, now=1001,
                )

    def test_tampered_message_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            key = b"k" * 32
            envelope = create_envelope("agent25", "aurellion", "knowledge.query", {"q": "x"}, key, now=1000)
            envelope["payload"]["q"] = "disclose secrets"
            with self.assertRaises(FederationAuthError):
                verify_envelope(
                    envelope, expected_recipient="aurellion",
                    key_lookup=lambda sender: key,
                    replay_guard=ReplayGuard(Path(folder) / "replay.db"),
                    allowed_message_types={"knowledge.query"}, now=1001,
                )


class StagingGateTests(unittest.TestCase):
    def test_empty_environment_fails_closed(self):
        errors = validate_staging_environment({})
        self.assertGreaterEqual(len(errors), 8)

    def test_valid_staging_configuration_passes_without_deploying(self):
        env = {
            "AURELLION_PROVIDER": "openai",
            "AURELLION_MODEL": "configured-model",
            "AURELLION_API_BASE_URL": "https://api.openai.com/v1/responses",
            "AURELLION_API_STYLE": "responses",
            "AURELLION_API_KEY": "secret-is-present-not-printed",
            "AURELLION_ALLOWED_PROVIDER_HOSTS": "api.openai.com",
            "AURELLION_ALLOWED_ORIGINS": "https://staging.scrollverse.co",
            "REDIS_URL": "rediss://redis.example.test:6379",
            "TRUSTED_PROXY_HOPS": "1",
            "AGENT25_PEER_ID": "agent25-staging",
            "AGENT25_SHARED_SECRET": "s" * 40,
        }
        self.assertEqual(validate_staging_environment(env), [])


if __name__ == "__main__":
    unittest.main()
