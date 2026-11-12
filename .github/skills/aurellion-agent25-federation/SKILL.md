---
name: aurellion-agent25-federation
description: Design and validate authenticated, least-privilege communication between AURELLION and Agent 25 or other independent Legion agents.
---

# AURELLION / Agent 25 Federation

## Workflow
1. Register each peer with an owner, immutable identity, endpoint, version, allowed message types, scopes, and revocation status.
2. Use unique per-peer keys or stronger public-key identities; never use one shared ambient credential for the whole Legion.
3. Authenticate canonical message envelopes with sender, recipient, type, timestamp, expiry, nonce, payload, and signature.
4. Reject invalid signatures, wrong recipients, unknown message types, stale/future timestamps, oversized payloads, and replayed nonces.
5. Use TLS for transport; message signatures do not replace transport security.
6. Authorize every message type and requested capability at the receiver. Model output is not permission.
7. Provide key rotation, revocation, opt-out, bounded retries, circuit breakers, and audit receipts.
8. Test impersonation, replay, tampering, scope escalation, malformed payloads, key rotation, and peer revocation.

## Boundaries
- AURELLION does not inherit Agent 25's credentials or authority.
- Protocol code is not a live network integration.
- Do not establish peer keys or connect endpoints without explicit owner approval and secure provisioning.
