import json
import tempfile
import unittest
from pathlib import Path

from aurellion_core import PolicyGate, ProvenanceLedger


class PolicyGateTests(unittest.TestCase):
    def test_side_effect_is_denied_by_default(self):
        self.assertFalse(PolicyGate().authorize("publish", "site:production").allowed)

    def test_allowlisted_read_only_action(self):
        self.assertTrue(PolicyGate({"read_repo"}).authorize("read_repo", "repo:sample").allowed)

    def test_approval_must_match_exact_scope(self):
        gate = PolicyGate()
        denied = gate.authorize("write_file", "repo:alpha", explicit_approval=True,
                                approval_scope="repo:beta")
        allowed = gate.authorize("write_file", "repo:alpha", explicit_approval=True,
                                 approval_scope="repo:alpha")
        self.assertFalse(denied.allowed)
        self.assertTrue(allowed.allowed)


class ProvenanceLedgerTests(unittest.TestCase):
    def test_records_form_a_valid_chain(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = ProvenanceLedger(Path(folder) / "events.jsonl")
            ledger.append("human", "project_named", {"name": "AURELLION"})
            ledger.append("assistant", "blueprint_drafted", {"edition": "0.1"})
            self.assertTrue(ledger.verify())
            self.assertEqual(len(ledger.records()), 2)

    def test_modified_record_fails_verification(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "events.jsonl"
            ledger = ProvenanceLedger(path)
            ledger.append("human", "note", {"text": "original"})
            row = json.loads(path.read_text(encoding="utf-8"))
            row["payload"]["text"] = "changed"
            path.write_text(json.dumps(row) + "\n", encoding="utf-8")
            self.assertFalse(ledger.verify())


if __name__ == "__main__":
    unittest.main()
