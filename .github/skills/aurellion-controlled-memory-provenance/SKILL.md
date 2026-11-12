---
name: aurellion-controlled-memory-provenance
description: Design, implement, audit, or operate AURELLION memory with explicit consent, scoped retention, user control, and verifiable provenance.
---

# AURELLION Controlled Memory and Provenance

## Workflow
1. Determine whether the information is a source record, temporary session context, or durable memory.
2. Require explicit consent for durable memory writes and store the source reference with every memory.
3. Restrict persistent memory to ordinary, non-sensitive project knowledge; reject secrets, private keys, seed phrases, and sensitive personal information.
4. Enforce namespace isolation, retention expiry, explicit deletion, and correction events.
5. Log metadata and hashes rather than copying unnecessary content into audit logs.
6. Keep originals immutable; represent corrections as new events with references to the earlier record.
7. Verify ledger chains and test consent denial, expiry, deletion, tampering, and cross-namespace access.
8. Document storage encryption, backups, recovery, and deletion behavior before production.

## Boundaries
- Do not claim memory is permanent or synchronized across systems unless storage and replication are implemented and tested.
- Do not treat an append-only ledger as tamper-proof.
- Do not store sensitive material in plaintext SQLite for production.
- Deletion must remove or render inaccessible the stored content while retaining only the minimum lawful audit metadata.
