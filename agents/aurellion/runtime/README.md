# AURELLION Runtime Foundation

This provider-neutral Python foundation demonstrates:
- default-deny authorization for side-effecting actions;
- exact-scope approval matching;
- a JSONL provenance chain;
- verification of sequence, previous hash, and record hash.

It does **not** call an LLM, access a network, read private data, execute shell commands, or perform external actions.

## Test

Requires Python 3.11+.

```bash
cd agents/aurellion/runtime
python -m unittest -v
```

The ledger is tamper-evident, not tamper-proof. For production, anchor hashes in separately controlled storage, authenticate event writers, encrypt sensitive payloads, and define retention/deletion rules. Do not put secrets or personal data into ledger payloads.
