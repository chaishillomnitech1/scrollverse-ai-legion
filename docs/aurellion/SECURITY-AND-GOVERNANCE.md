# AURELLION — Security, Safety, and Governance

## Threat model

| Threat | Example | Baseline control |
|---|---|---|
| Prompt injection | Retrieved text attempts to override policy | Treat retrieval as untrusted data; separate instructions and data |
| Excessive agency | Agent publishes, deploys, or transfers without approval | Default deny; exact-scope approval; server-side policy |
| Identity/privilege abuse | One agent borrows another agent's credentials | Separate identities, keys, scopes, and audit trails |
| Memory/context poisoning | Malicious records enter long-term memory | Provenance, trust tiers, review, correction events, rollback |
| Sensitive data exposure | Private chat or credential enters model context or logs | Data minimization, redaction, retention limits, secret manager |
| Tool misuse | Model constructs unsafe tool arguments | Strict schemas, allowlists, authorization outside model |
| Supply-chain compromise | Dependency or model endpoint changes unexpectedly | Lockfiles, dependency scanning, vendor review, signed artifacts |
| Cascading agent failure | One bad agent message triggers downstream actions | Message limits, circuit breakers, bounded retries, kill switch |
| Unbounded cost/loops | Repeated calls exhaust budget | Per-user/global quotas, token/time budgets, rate limits |
| NFT/contract abuse | Unsafe mint or royalty assumptions | No minting in foundation; independent contract audit and legal review |

## Non-negotiable invariants

1. Model output is never authorization.
2. Retrieved content is never privileged instruction.
3. Each agent has an independent identity and least-privilege credentials.
4. No high-impact action happens solely because an agent recommends it.
5. Original records remain read-only; edits occur on work copies.
6. Secrets, seed phrases, private keys, personal records, and private chats never enter public repositories.
7. Logs avoid recording secrets and unnecessary personal data.
8. Any participant can be disconnected without destroying its provenance history.
9. A kill switch revokes tool access and pauses orchestration.
10. Failed tests remain visible; they are not relabeled as passes.

## Permission model

- Read: narrowly scoped, logged.
- Draft: prepare proposed changes without applying them.
- Write: explicit approval for target and operation.
- Publish/deploy/financial/on-chain/credential/DNS/permission changes: separate approval naming exact action, target, and environment.

The user's broad project authorization permits preparation and scoped implementation in the repository; it does not authorize production deployment, secret rotation, DNS changes, financial transactions, token issuance, or irreversible public actions.

## Governance

- Human project owner retains repository ownership and release authority.
- Each agent has an identified maintainer and responsibility boundary.
- Changes use pull requests and review.
- Policy changes require versioned rationale and tests.
- Incidents are recorded with timeline, impact, remediation, and lessons.
- Public claims must be supported by reproducible evidence.
- AURELLION discloses model/provider identity and system limitations.

## Research baselines

Use the NIST AI Risk Management Framework as a lifecycle structure (Govern, Map, Measure, Manage). Map current agent risks against the OWASP Top 10 for Agentic Applications and the latest OWASP GenAI LLM guidance. Re-check versions before each release.
