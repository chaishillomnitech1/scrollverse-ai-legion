# Agent 25 Omni — Evolution Roadmap

**Version:** 0.2.0  
**Status:** Architecture plan; implementation and production activation are not yet verified.  
**Change policy:** Additive-only. Preserve the 12 legacy AI Legion entities and all original ScrollVerse artifacts.

## Mission

Build a reliable, evidence-grounded intelligence layer for the ScrollVerse ecosystem: one owner-directed command interface, 25 specialist capabilities, a secure public visitor experience, and a governed knowledge graph connecting approved sites, repositories, and artifacts.

The goal is not to maximize autonomy. The goal is to maximize useful capability while preserving truth, privacy, owner control, and operational reliability.

## Current verified baseline

- The 25-role manifest and architecture documentation are present on the default branch of `scrollverse-ai-legion`.
- The role registry, visitor API router, visitor chat UI, embed loader, and pilot documentation are present on the default branch of `scrollverse-platform`.
- The visitor pilot uses one configured model endpoint and selects one specialist role per turn. This is a role-routed single-model pilot, not 25 independent autonomous services.
- The public site registry is explicitly partial.
- Production deployment, provider credentials, cross-site embed rollout, full artifact indexing, and live visitor operation are not established by repository files alone.

## Target architecture

```
Owner / Visitor
      |
Identity + Consent + Rate Limits
      |
Agent 00 — Command & Policy Gateway
      |
Task Planner + Specialist Router (01–25)
      |
Evidence & Knowledge Layer
  |         |          |
Public    Private     Project
Catalog   Owner Vault  Metadata
  |         |          |
Permissioned Connectors (read/write scopes per task)
      |
Isolated Task Runtime + Durable Queue
      |
Evaluation / Audit / Approval Gate
      |
Answer, Report, PR, or Approved Action
```

## Core subsystems to build

### 1. Agent runtime and orchestration
- Convert the current keyword selector into a tested intent router with confidence scores and explicit fallback.
- Support bounded multi-specialist workflows: planner → specialists → verifier → synthesizer.
- Give every task a durable ID, owner, status, timeout, budget, source list, permission set, and audit record.
- Use a durable queue and isolated workers for long-running work; never run arbitrary visitor-provided code.
- Add cancellation, retries with idempotency keys, dead-letter handling, and per-task resource ceilings.
- Keep specialist roles as capability contracts. Deploy separate workers only when workload and isolation justify them.

### 2. Evidence-first knowledge layer
- Build a canonical catalog for sites, routes, repositories, files, conversations, media, and releases.
- Store source URL or repository path, content hash, observed timestamp, owner/source attribution, access classification, and verification state.
- Separate public knowledge from private owner knowledge at storage and retrieval layers.
- Retrieve only from approved sources; attach source references to answers and show when evidence is missing or stale.
- Preserve originals. Use versioned derivatives and never silently rewrite source artifacts.
- Use incremental indexing and deletion/tombstone propagation for revoked or removed public material.

### 3. Security and privacy
- Keep provider credentials in hosting secret storage, never in browser bundles, Git, logs, or prompts.
- Require a production provider-host allowlist to prevent arbitrary outbound requests and SSRF.
- Replace process-local rate limits with a shared store before multi-instance production.
- Add abuse controls: per-IP and per-session quotas, request-size limits, concurrency caps, timeouts, and circuit breakers.
- Treat visitor messages and retrieved documents as untrusted data; defend against prompt injection and data exfiltration.
- Use least-privilege, short-lived connector credentials and per-tool allowlists.
- No public visitor access to private repositories, conversations, owner vaults, wallets, payment rails, secrets, or admin operations.
- Do not retain visitor chat by default. If analytics or retention is later introduced, publish a clear notice and obtain required consent.

### 4. Human governance
- Public visitor mode is read-only.
- Owner mode requires authentication and explicit scoped authorization.
- Require human approval for production writes, deployments, publishing, payments, wallet/contract actions, credential changes, and private archive access.
- Use a preview/diff step before every write and retain an immutable audit event.
- Provide a kill switch for visitor chat, provider calls, individual connectors, and each specialist capability.

### 5. Evaluation and observability
- Unit, integration, contract, security, and end-to-end tests.
- Golden question sets for public site discovery, archive retrieval, provenance, and refusal boundaries.
- Measure grounded-answer rate, citation correctness, task completion, latency, cost per task, refusal correctness, and escalation rate.
- Add red-team suites for prompt injection, cross-tenant retrieval, secret requests, unsafe tool invocation, and false status claims.
- Use structured logs with request IDs and redacted metadata; never log API keys or unnecessary personal data.
- Maintain a versioned model/provider evaluation matrix before changing models.

### 6. Public experience and ecosystem integration
- Complete the approved site and artifact registry before broad rollout.
- Pilot on one staging origin first; configure exact `frame-ancestors` and CORS rules.
- Add the embed only to approved domains after staging checks.
- Give each site a verified site ID and a public-safe knowledge scope.
- Provide accessible keyboard navigation, mobile layout, loading/error states, and a visible privacy/read-only notice.
- Expand to other sites only after a successful owner-reviewed pilot.

## Delivery gates

| Gate | Deliverable | Exit evidence |
|---|---|---|
| G0 — Preserve | Baseline inventory and backup references | Original 12-entity manifest and source artifacts retained |
| G1 — Harden | Provider allowlist, distributed limits, input/output validation | Security tests and reviewed configuration |
| G2 — Verify | Typecheck, unit tests, build, integration tests | Green CI run with commit SHA |
| G3 — Knowledge | Public catalog + provenance metadata | Sample retrievals with source references and access tests |
| G4 — Orchestrate | Durable task runtime and bounded specialist workflows | Replayable task traces and timeout/retry tests |
| G5 — Stage | One staging deployment and one approved embed origin | Live smoke test, CSP validation, accessibility check |
| G6 — Expand | Additional approved sites and artifact scopes | Per-site sign-off and registry evidence |
| G7 — Production | Owner-approved release | Deployment SHA, rollback plan, health checks, and incident owner |

## Definition of operational states

- **DEFINED:** role and task contract exist.
- **IMPLEMENTED:** executable code exists.
- **TESTED:** reproducible tests pass on a named commit.
- **CONNECTED:** approved data or service scope is configured and verified.
- **STAGED:** running in a non-production environment with smoke-test evidence.
- **PRODUCTION-ACTIVE:** authorized live deployment passes health checks.
- **AUTONOMOUS:** only used for a worker with bounded permissions, durable state, observability, and tested safety controls.

Never promote a capability to a higher state without evidence.

## Immediate engineering priorities

1. Harden the visitor API before any public launch: strict provider host allowlist, shared rate limiting, request validation, bounded provider response parsing, and robust timeout handling.
2. Add tests for routing, malicious inputs, missing configuration, provider errors, rate limiting, and site-context isolation.
3. Establish CI evidence for typecheck, tests, and production build.
4. Build a public-safe artifact catalog with provenance and retrieval citations.
5. Implement authenticated owner mode separately from the public visitor widget.
6. Only then add durable multi-agent orchestration and approved connector tools.

## Non-goals

- No claim that all 25 roles are independent deployed agents.
- No autonomous production modification or self-deployment.
- No private archive exposure to public visitors.
- No unverified claims about uptime, financial value, token balances, partnerships, or impact.
- No Manus commands, credit-consuming operations, or automatic payments.
