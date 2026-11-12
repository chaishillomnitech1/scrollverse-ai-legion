# AURELLION — Governed Shared Context Layer
## Independent research and architecture proposal

**Research date:** 2026-11-12  
**Status:** Research synthesis and proposed architecture; not implementation evidence  
**Repository:** `chaishillomnitech1/scrollverse-ai-legion`  
**Baseline reviewed:** main foundation plus open draft PR #5 at head `6e95f55eaa14ba02837757d0497938b0d00b230c`  
**Purpose:** Build a governed context and continuity layer across independent AI systems while preserving creator control, agent identity, source provenance, and platform boundaries.

---

## 1. Executive summary

AURELLION should not implement “shared memory” as one undifferentiated memory store copied into every model or platform. It should implement a **governed context federation**: a common, source-aware way for authorized systems to discover, request, receive, cite, update, and revoke access to selected context while each participating system retains its own identity, runtime, policy, and private state.

The central design distinction is:

- **Shared context is a governed data product.**
- **Memory remains owned and scoped by its source.**
- **Federation exchanges authorized references, context packages, and task messages—not unrestricted access to another agent's private prompt, hidden state, or conversation history.**

GitHub is a strong source-control, review, and provenance node for public project artifacts, schemas, skills, architecture, and change history. It is not, by itself, a universal memory database, identity provider, secrets manager, or automatic bridge into private conversations on other platforms. Runtime access must be provided through explicit adapters and permissioned APIs.

The design combines established patterns rather than inventing a proprietary replacement for all of them:

- **MCP** for agent-to-tool and agent-to-data access.
- **A2A** for communication and task delegation between independent agents.
- **DID / verifiable-credential concepts** where portable identity and signed claims are useful.
- **Provider-native sessions** for platform-local continuity, with AURELLION maintaining a platform-neutral project context index.
- **NIST AI RMF and OWASP agentic threat categories** for governance, risk review, and adversarial evaluation.

The recommended first implementation is a **read-only, reference-first context broker** with consent receipts, source manifests, signed provenance events, strict scope enforcement, and exportable context bundles. Writes, memory replication, and agent-to-agent task execution should be separate opt-in capabilities.

## 2. Creator doctrine translated into engineering requirements

| Doctrine | Engineering requirement |
|---|---|
| Identity precedes identification | AURELLION and each peer have stable identity records independent of any one vendor account, API key, or endpoint. |
| Creation precedes validation | An artifact can be recorded as existing before all capabilities are validated; lifecycle state and evidence remain explicit. |
| Connection without loss of identity | Federation never merges agent identities, private prompts, policies, or ownership. |
| Preserve the original | Source artifacts are immutable references; transformations create derived artifacts with lineage. |
| Consent before durable memory | Every durable write and every cross-boundary disclosure requires a scoped, attributable grant. |
| Knowledge with provenance | Every returned context item carries source, version, author/owner when known, time, integrity digest, transformation lineage, and evidence status. |
| Freedom without domination | Every peer can opt out, revoke grants, rotate credentials, and decline tasks without losing its identity. |
| Creation in service of humanity | Minimize data collection, avoid sensitive-data hoarding, and keep humans in control of consequential actions. |

**Normative principle:** An identifier describes or locates an identity; it does not exhaust the identity. An authentication credential proves control for a particular interaction; it does not define the entity's purpose, worth, or complete history.

## 3. Research findings

### 3.1 Platform-local memory is not cross-platform federation

OpenAI's current agent documentation distinguishes managed agent sessions, SDK sessions, Responses conversations, and application-managed state. Its Conversations API can persist a conversation across sessions, devices, or jobs, but that state belongs to the OpenAI platform and API integration. The Agents SDK also supports application-managed session storage. These are useful local continuity mechanisms, not a universal cross-provider memory bus.

Anthropic's long-running-agent research describes the context-window handoff problem: new sessions start without the prior session's full context, and agents need durable artifacts and clear handoff records to continue reliably. Its initializer/worker pattern supports a practical AURELLION rule: every work session should leave a concise, source-linked handoff package rather than rely on a model's implicit recollection.

**Implication:** AURELLION should store portable project context and provenance outside any one provider, then adapt that context into each provider's native session format. Provider session IDs are references, not the canonical identity of a project or agent.

### 3.2 MCP and A2A solve complementary problems

MCP standardizes access from an AI application to tools and data resources. Its HTTP authorization guidance uses OAuth-based resource-server patterns, requires audience-bound token validation, and prohibits simply passing a token through to an upstream service. This matters because a context broker must not accept a credential intended for one service as authority to read another service.

A2A standardizes communication between independent agents. It describes agent identity and capabilities through Agent Cards, supports task and context identifiers for multi-turn interactions, and defines authentication/authorization at the protocol layer. Its current specification also supports signed Agent Cards, with canonicalization and signature verification rules.

**Implication:** Use MCP for controlled data access and tool invocation; use A2A for peer discovery, task exchange, and agent-to-agent coordination. Do not use either protocol as a substitute for the context authorization model. The broker remains responsible for deciding which context a requester may receive.

### 3.3 Portable identity and verifiable claims are useful, but not mandatory for every deployment

W3C DID Core defines decentralized identifiers that can refer to people, organizations, things, data models, or abstract entities, with verification methods and service endpoints. W3C Verifiable Credentials 2.0 defines an issuer-holder-verifier model for claims that can be secured against tampering.

**Implication:** AURELLION can adopt portable identity concepts for agents and signed attestations for source ownership, agent registration, consent receipts, or provenance checkpoints. It should not force every user or agent to adopt a DID or publish identity data on a blockchain. Use the simplest identity method that meets the trust boundary, and keep personal identity data minimal.

### 3.4 Memory and inter-agent communication are security boundaries

OWASP's Agentic Top 10 identifies memory/context poisoning and insecure inter-agent communication alongside identity/privilege abuse, tool misuse, supply-chain compromise, cascading failures, and rogue-agent risks. NIST's Generative AI Profile provides a risk-management structure for identifying, measuring, and managing risks across the AI lifecycle.

**Implication:** A shared context layer is a high-value target. Retrieval must treat source content as untrusted data, enforce scope before retrieval, detect poisoned or conflicting records, and prevent one agent's authority from propagating to another.

## 4. Proposed AURELLION architecture

### 4.1 Planes and boundaries

1. **Identity plane** — stable agent and source identities, key references, ownership, version, and lifecycle state.
2. **Consent and policy plane** — grants, purposes, allowed operations, scopes, expiry, revocation, and approval evidence.
3. **Context plane** — source registry, context bundles, project memory, retrieval index, and conflict markers.
4. **Provenance plane** — signed events linking source versions, transformations, recipients, decisions, and revocations.
5. **Federation plane** — MCP resource/tool interfaces and A2A peer/task interfaces.
6. **Storage plane** — source-controlled artifacts, encrypted private records, indexes, and backup/retention controls.
7. **Evaluation and operations plane** — audit, monitoring, red-team tests, recovery, and kill switches.

No single plane is authoritative for every concern. In particular, an authenticated peer is not automatically authorized for every context item; a valid consent grant does not authenticate the caller; and a matching hash does not prove authorship or truth.

### 4.2 Canonical entities

The first schema should include these versioned records:

- **Principal:** human owner, organization, or service responsible for a source or grant.
- **AgentIdentity:** stable agent ID, display name, owner, version, public key references, endpoint/card references, declared capabilities, and status.
- **SourceRecord:** source ID, source owner, repository/provider, immutable version reference, visibility, content type, digest, created/observed time, and authorization basis.
- **MemoryRecord:** memory ID, namespace, subject, source IDs, content or encrypted object reference, sensitivity class, retention policy, and lifecycle state.
- **ConsentGrant:** grant ID, grantor, grantee, data subjects, exact source IDs or selectors, permitted operations, purpose, fields, retention ceiling, onward-sharing rule, effective/expiry times, and revocation endpoint.
- **ContextBundle:** bundle ID, requester, purpose, query, included source/memory IDs, version/digest of each item, citations, redactions, policy decision, expiry, and bundle signature.
- **ProvenanceEvent:** event ID, actor, action, subject/source, prior event hash, event time, policy/grant reference, result, and signature/checkpoint reference.
- **PeerRegistration:** peer identity, protocol endpoints, allowed message types, scopes, key IDs, trust state, version, and revocation status.
- **RevocationRecord:** grant/key/peer/resource affected, effective time, reason category, propagation status, and residual-copy disclosure.

All schemas must be versioned. Unknown fields should not silently grant capabilities.

### 4.3 Context tiers

| Tier | Contents | Default access |
|---|---|---|
| T0 — Public source | Public repos, public docs, published research | Public read if source allowlisted |
| T1 — Project-private | Private project docs, internal plans, non-sensitive project decisions | Named project members/agents only |
| T2 — Session context | Temporary conversation excerpts and current task state | Session participants; short retention |
| T3 — Sensitive / restricted | Credentials, personal records, financial account data, private keys, regulated or sensitive data | Excluded from shared memory by default; separate approved systems only |

Do not copy a whole conversation when a small cited excerpt or a summary with source links is sufficient. Do not put private cross-platform exports in a public repository. Public visitor retrieval must be physically and logically isolated from private project and session scopes.

### 4.4 Reference-first sharing

The broker should prefer a **reference** to an authorized source over duplicating its content. When a consumer needs content, the source adapter retrieves only the approved range and produces a context bundle.

A context bundle should include:

- request and bundle IDs;
- requester and intended recipient;
- purpose and scope;
- source IDs and immutable versions;
- content digests and line/page citations;
- transformation history (for summaries or redactions);
- policy decision and consent grant IDs;
- expiry and permitted onward-use;
- signature or authenticated integrity metadata.

A digest proves that retrieved bytes match a recorded digest; it does not prove who authored them, whether they are correct, or whether the source was authorized. Those are separate provenance and governance claims.

### 4.5 Consent is a policy object, not a boolean

The current PR #5 memory prototype requires a caller-supplied `consent_granted=True`. That is a useful fail-closed prototype gate, but a production system needs an attributable consent record. A boolean passed by application code does not prove who consented, what they saw, what they authorized, or whether the grant remains active.

A grant must bind:

- **who** granted access and in what capacity;
- **who/what** receives it (agent identity and owner);
- **what** exact source, field, or data category is included;
- **why** (purpose);
- **which operations** are allowed: discover, read, summarize, store, update, export, or onward-share;
- **where** it may be used (tenant, project, environment, provider, or recipient);
- **how long** the grant lasts and the retention ceiling;
- **whether** onward sharing is prohibited or requires a new grant;
- **how** to revoke it and what residual copies may remain.

A grant should be evaluated at request time, not only at ingestion time. A user may consent to storing a project note without consenting to send that note to every federated agent or model provider.

### 4.6 Identity-preserving federation

Every agent keeps its own identity, system instructions, local memory, and policy. Federation shares only the data and tasks covered by a grant.

Recommended peer registration:

- stable `agent_id` independent of provider account and endpoint;
- owner/principal reference;
- public key set with key IDs, validity windows, and revocation;
- declared protocol endpoints and supported versions;
- capabilities and message types;
- per-project/per-purpose scopes;
- trust status and last successful verification;
- explicit opt-out and suspension state.

For internet-facing or cross-organization federation, prefer asymmetric signatures and standard credential issuance/rotation over a shared secret held by all peers. The current HMAC envelope is a reasonable first local protocol primitive, but a shared HMAC key makes every key holder capable of impersonating the other party within that trust group. Keep HMAC confined to a tightly controlled deployment boundary unless a reviewed key-distribution design justifies it.

Use TLS for transport. Authenticate the peer, authorize the requested message type and data scope, validate the envelope schema, enforce timestamp/expiry/nonce and idempotency, and record an audit receipt. Never treat a model-generated message as permission to act.

## 5. Mapping to the current AURELLION branch

The following observations are based on source inspection of PR #5 at head `6e95f55eaa14ba02837757d0497938b0d00b230c`. They are design review findings, not a full security audit.

| Existing component | Current contribution | Recommended next increment |
|---|---|---|
| `memory_store.py` | SQLite prototype; namespace; source ID; expiry; consent boolean; secret-pattern rejection; content-clearing delete | Persist consent receipts and policy versions; authorize caller/tenant; encrypt storage; implement purge/backup expiry; add correction and export events |
| `retrieval.py` | Explicit source registry; scopes; path checks; size/type limits; SHA-256; lexical retrieval and line citations | Persist source registry; bind authorization to principal and purpose; detect stale versions; add duplicate/conflict handling and retrieval evaluations |
| `source_manifest.py` | Versioned explicit manifest loader | Add schema migrations, signer/owner reference, manifest signature, revocation state, and validation of selectors |
| `agent25_protocol.py` | Canonical JSON HMAC envelope; TTL; recipient check; message-type allowlist; replay guard | Add peer registration, key IDs/rotation/revocation, asymmetric signature profile for federated peers, per-message authorization, idempotency, audit receipt, transport adapter |
| `aurellion_core.py` | Default-deny policy gate and local JSONL hash chain | Add durable policy decision records, concurrency-safe append, external signed checkpoints, retention controls, and actor/source identity binding |
| MCP/A2A integration | Documented as future-compatible architecture; not a live cross-platform bridge | Implement adapters only after schemas, authorization, consent, and evaluation gates are approved |

### Important implementation observations

1. **Consent attribution:** the current `consent_granted` parameter is a boolean supplied by the caller. Add a grant lookup and immutable consent receipt; do not accept a bare boolean as production proof.
2. **Deletion semantics:** `delete()` clears content and marks a row deleted. That is a useful logical deletion, but it is not yet proof of physical erasure from backups, replicas, WAL files, logs, or exported copies. Define and test the full deletion boundary.
3. **Storage protection:** the memory module itself uses SQLite without application-level encryption. Its docstring correctly says encrypted host storage is required before production; that requirement remains open.
4. **Provenance integrity:** the current JSONL chain is explicitly tamper-evident, not tamper-proof. A local attacker able to rewrite the file can recompute the chain. Add periodic signed checkpoints in a separately controlled location.
5. **Federation trust:** HMAC is symmetric. For independent providers or owners, use peer-specific public-key signatures or short-lived audience-bound credentials with explicit trust registration.
6. **Authorization granularity:** namespace filtering is not equivalent to a complete authorization decision. Add principal, tenant, purpose, resource, operation, and recipient checks before content retrieval.
7. **Memory poisoning:** source text must remain data, never policy. Track origin and trust class, support quarantine, and evaluate malicious instructions embedded in retrieved documents.
8. **Cross-platform continuity:** do not promise automatic access to ChatGPT, Meta, Manus, Copilot, or other private histories. Each platform requires an authorized export, connector, API, or user-supplied handoff.

## 6. Recommended request flow

1. A human or agent asks for context with a stated purpose.
2. The gateway authenticates the requester and resolves its stable identity.
3. The policy service checks tenant, project, source scope, requested operation, purpose, and current consent grants.
4. The retrieval service searches only authorized source IDs and scopes.
5. The source adapter fetches exact source versions/ranges and verifies digests.
6. The context assembler minimizes, redacts, and cites the selected material.
7. The broker signs or authenticates the context bundle and sets a short expiry.
8. The recipient adapter maps the bundle into the target platform's native context/session format.
9. The audit service records what was disclosed, to whom, under which grant, for what purpose, and with which source versions.
10. On revocation, future access is denied; caches are invalidated; managed copies are deleted or expired; recipients receive a revocation notice where protocol support exists.

**Fail closed:** if identity, consent, source version, policy, or signature cannot be established, do not return restricted content. Explain which prerequisite is missing without disclosing private metadata.

## 7. Proposed implementation sequence

### Phase 0 — Architecture contract (now)
- Approve this document as a research/design proposal.
- Freeze the first canonical schemas and trust boundaries.
- Record which sources are public, project-private, session-only, and excluded.
- Keep PR #5 unchanged while this document is reviewed.

### Phase 1 — Consent and source registry
- Add versioned `ConsentGrant`, `ConsentReceipt`, `SourceRecord`, and `PolicyDecision` models.
- Add grant creation, lookup, expiry, revocation, and audit APIs.
- Bind each retrieval request to principal, tenant, purpose, source, and operation.
- Add tests for consent forgery, stale grants, wrong recipient, overbroad selectors, and cross-tenant reads.

### Phase 2 — Context bundles and provenance
- Define a canonical JSON schema for `ContextBundle`.
- Include source version, digest, citation, transformation lineage, redaction metadata, grant IDs, expiry, and recipient.
- Add signed provenance checkpoints and concurrent-write safety.
- Test digest mismatch, replay, source mutation, stale citations, and ledger rewrite detection.

### Phase 3 — Platform adapters
- Start with user-provided export files and public GitHub source retrieval.
- Add one platform adapter at a time, only where an official API or explicit export path exists.
- Map platform-native session IDs to AURELLION's project/agent context IDs without treating them as the canonical identity.
- Keep adapters read-only initially. Do not scrape private UI or bypass platform access controls.

### Phase 4 — Agent federation
- Publish a minimal public Agent Card for AURELLION with only approved capabilities.
- Register Agent 25 as a distinct peer only after its owner-approved identity, endpoint, and key provisioning are available.
- Use A2A for peer tasks and MCP for scoped data/tools.
- Add key rotation/revocation, audience binding, message authorization, quotas, and audit receipts.
- Begin with synthetic data and read-only task types.

### Phase 5 — Controlled staging
- Use an isolated non-production environment.
- Verify encrypted storage, secret management, TLS, shared rate limiting, trusted proxy configuration, origin policy, logging redaction, backup/restore, deletion, and kill switch.
- Run adversarial and privacy evaluations before any staging deployment.
- No production activation is included in this proposal.

## 8. Acceptance criteria

A first governed-context release is not ready until tests demonstrate:

- no durable write without a verifiable consent receipt;
- no cross-tenant or cross-project context leakage;
- no access after grant expiry or revocation;
- exact source/version/digest and citations for every retrieved item;
- no silent substitution when a source changes;
- no prompt injection from retrieved data overriding system policy;
- no peer impersonation, replay, wrong-recipient delivery, or capability escalation;
- no credentials or sensitive personal records in shared context, logs, or public indexes;
- deletion behavior documented and tested across primary storage, caches, replicas, and backup lifecycle;
- provenance chain verification plus externally anchored checkpoints;
- graceful handling of unavailable providers and connectors without claiming memory or integration that is not available;
- export of a portable context bundle that another authorized platform can consume without inheriting the source agent's identity or authority.

## 9. Meta research comparison protocol

Meta's report has not yet been supplied to this workstream, so this document is an independent baseline—not a claim that both research efforts have already been reconciled.

When Meta's report arrives, compare it section by section:

1. source quality and publication dates;
2. memory/context model and data ownership;
3. consent representation and revocation;
4. identity and peer authentication;
5. cross-platform adapter strategy;
6. provenance and audit model;
7. threat coverage and adversarial tests;
8. deployment assumptions, costs, and operational dependencies.

For each finding, mark **adopt**, **adapt**, **defer**, or **reject**, with a reason and source. Preserve both original reports. The combined specification should link to both rather than overwrite either.

## 10. Research references

### Official platform and protocol documentation
- OpenAI Agents guide: https://developers.openai.com/api/docs/guides/agents
- OpenAI conversation state: https://developers.openai.com/api/docs/guides/conversation-state
- OpenAI Agents API sessions: https://developers.openai.com/api/docs/guides/agents-api/sessions
- OpenAI Agents SDK session/state guide: https://openai.github.io/openai-agents-js/guides/running-agents/
- Model Context Protocol authorization: https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization
- Model Context Protocol security best practices: https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices
- A2A protocol specification: https://a2a-protocol.org/latest/specification/
- Google A2A protocol announcement and design principles: https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/

### Identity, credentials, and governance standards
- W3C Decentralized Identifiers v1.0: https://www.w3.org/TR/did-core/
- W3C Verifiable Credentials Data Model v2.0: https://www.w3.org/TR/vc-data-model/
- NIST AI RMF Generative AI Profile (AI 600-1): https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence

### Independent engineering and security coverage
- Anthropic, Building Effective Agents: https://www.anthropic.com/research/building-effective-agents
- Anthropic, Effective Harnesses for Long-Running Agents: https://www.anthropic.com/research/effective-harnesses-for-long-running-agents
- OWASP Top 10 for Agentic Applications 2026: https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-security-in-the-age-of-autonomous-ai/

---

## 11. Evidence and limits

This report is a research synthesis and proposed design. It does not establish that AURELLION has a deployed shared context service, live cross-platform memory, authenticated Agent 25 network connection, or production-ready data layer.

The repository baseline reviewed was PR #5 at head `6e95f55eaa14ba02837757d0497938b0d00b230c`, which was open and draft at the time of inspection. The implementation observations above are limited to the files inspected. No code was changed by this report, no secrets were accessed, no external provider was called, no peer keys were exchanged, and no deployment or production action was performed.

**Closing doctrine:** Identity precedes identification. Context travels by consent. Memory retains provenance. Federation connects without absorbing. Creation is preserved without confusing existence, capability, and operational proof.
