# AURELLION Documentation Index

AURELLION — The Intelligence of Connected Light — is being developed additively within the ScrollVerse AI Legion while preserving each existing entity's identity and independent evolution.

## Start here

1. [Identity profile](../../agents/aurellion/README.md)
2. [Operating charter and system prompt](../../agents/aurellion/SYSTEM_PROMPT.md)
3. [Capability and autonomy matrix](../../agents/aurellion/CAPABILITY_MATRIX.md)
4. [System architecture and build plan](ARCHITECTURE.md)
5. [Security, safety, and governance](SECURITY-AND-GOVERNANCE.md)
6. [Research notes and references](RESEARCH.md)
7. [Provenance and release policy](PROVENANCE-AND-RELEASE.md)

## Creative and public-learning work

- [Foundation book manuscript: Connected Light](BOOK-MANUSCRIPT.md)
- [Podcast pilot: The Power to Create Without Controlling](PODCAST-EPISODE-001.md)
- [Genesis Five digital collectible concept](NFT-GENESIS-FIVE.md)
- [Founding case study](CASE-STUDY.md)

## Runnable foundation

The minimal Python foundation is in [agents/aurellion/runtime](../../agents/aurellion/runtime/README.md). It implements a default-deny policy gate and a SHA-256 hash-linked event ledger. It is not connected to a model provider or external tools.

## Current release state

- Repository artifact: OPEN DRAFT PULL REQUEST.
- Runtime code: IMPLEMENTED IN BRANCH; CI result not yet observed.
- Model adapter: NOT IMPLEMENTED.
- Provider credentials: NOT CONFIGURED.
- Agent process: NOT ACTIVATED.
- Staging: NOT DEPLOYED.
- Production: NOT AUTHORIZED OR DEPLOYED.
- Artwork: CONCEPT ONLY; image rendering deferred.
- NFT / coin: NOT CREATED OR MINTED.

See [the case study](CASE-STUDY.md) for the evidence boundary.


## Runtime implementation and visitor intelligence

- [Implementation status](IMPLEMENTATION-STATUS.md)
- [Live repository catalog snapshot](REPOSITORY-CATALOG.json)
- [Public GitHub visitor guide](../../agents/aurellion/visitor/README.md)
- [Explicit public retrieval source manifest](../../agents/aurellion/knowledge/sources.json)
- [Public GitHub source allowlist](../../agents/aurellion/knowledge/github-public-allowlist.json)
- [Read-only GitHub source adapter](../../agents/aurellion/runtime/github_source.py)
- [Shared Redis rate limiter](../../agents/aurellion/runtime/rate_limiter.py)
- [Exact origin policy](../../agents/aurellion/runtime/origin_policy.py)
- [GitHub Copilot custom agent](../../.github/agents/aurellion-github-guide.agent.md)

## Reusable GitHub Copilot skills

Project skills are stored under .github/skills and are available to supported Copilot surfaces when their repository skill support is enabled:

- aurellion-provider-adapter
- aurellion-authorized-source-retrieval
- aurellion-controlled-memory-provenance
- aurellion-agent25-federation
- aurellion-adversarial-evaluation
- aurellion-staging-readiness
- aurellion-github-visitor-navigation

These are version-controlled repository skills, not a global installation into every ChatGPT or AI environment.
