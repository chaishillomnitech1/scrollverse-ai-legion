# AURELLION Capability and Autonomy Matrix

| Capability | Foundation status | Permission boundary | Evidence required to advance |
|---|---|---|---|
| Conversation and reasoning | DOCUMENTED | User-provided context | Evaluation set and quality review |
| Source-aware summarization | DESIGNED | Authorized sources only | Provenance accuracy tests |
| Original-preserving archive | DESIGNED | Read-only originals; work copies | Restore and integrity tests |
| GitHub repository reading | CONNECTOR-DEPENDENT | Repository scopes | Read receipt and source commit |
| GitHub drafting | DESIGNED | Branch/PR proposal only | Human review |
| Model provider adapter | INTERFACE DESIGNED | Secret manager; provider terms | Provider contract, integration tests |
| Long-term memory | DESIGNED | User-governed retention and deletion | Privacy review and controls |
| Inter-agent messaging | DESIGNED | Authenticated, scoped channels | Identity, replay, injection, and isolation tests |
| Tool execution | DISABLED BY DEFAULT | Allowlisted tools only | Server-side policy gate and audit |
| Production deployment | NOT AUTHORIZED | Separate explicit approval | Staging acceptance and release approval |
| Financial / wallet actions | OUT OF SCOPE | Human-led | Legal, security, and transaction-specific approval |
| NFT minting / token issuance | CONCEPT ONLY | Not enabled | Rights review, contract audit, explicit launch approval |

## Autonomy levels

- **L0 — Offline:** reason over content explicitly supplied to the session.
- **L1 — Read-only:** query specifically connected sources with scoped access.
- **L2 — Draft:** prepare changes but do not apply them.
- **L3 — Reversible write:** apply only after explicit approval of exact target and change.
- **L4 — High impact:** production, public release, funds, legal, credentials, or on-chain operations remain human-led and require a separate approval.

No model response can grant itself a higher autonomy level.
