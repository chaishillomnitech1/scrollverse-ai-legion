# AURELLION — System Architecture and Build Plan

**Version:** Foundation 0.1  
**State:** Design + minimal provider-neutral runtime code on feature branch; no provider or deployment connected.

## 1. Architectural fit

The existing `scrollverse-ai-legion` repository is the central AI foundation. Its README documents twelve distinct Legion entities and their separate domains. AURELLION is additive: it receives its own profile and runtime path; the twelve existing identities and histories are not renamed or overwritten.

Agent 25 remains a separate coordination layer for the specialist federation. It may coordinate approved workflows, but it does not own every agent, inherit every credential, or absorb their identities. AURELLION is one independent intelligence profile, not a replacement for Agent 25.

OMNITECH1 remains independent of Vercel. Vercel can remain a deployment option for services already using it, but core identity, source, build, orchestration, and recovery must not depend on a single hosting vendor.

## 2. System layers

1. **Identity and doctrine:** AURELLION charter, version, identity, and boundaries.
2. **Model adapter:** provider-neutral interface; provider/model/version disclosed; credentials in a secret manager.
3. **Conversation runtime:** session context, input validation, token/cost/time budgets, refusal and escalation paths.
4. **Knowledge and memory:** retrieval from authorized sources; original-preserving archive; scoped memory; user-governed retention and deletion.
5. **Provenance ledger:** source IDs, content hashes, transformation events, commit references, reviewer and verification state.
6. **Policy gateway:** default deny; tool allowlists; schema validation; least privilege; explicit confirmation for side effects.
7. **Federation bridge:** authenticated message envelopes between independent worlds; per-agent identity and scopes; no shared ambient credentials.
8. **Evaluation and observability:** tests, red-team cases, metrics, audit events, incident response, rollback.
9. **Interfaces:** API, chat, visitor layer, and optional site integrations. Visitor-facing routes remain distinct from internal orchestration.

## 3. Existing project boundaries

- `scrollverse-ai-legion`: canonical Legion identity and agent architecture.
- `scrollverse-platform`: visitor-facing pilot and public interaction layer; not the owner of agent identities.
- `OmniBuilderZero`: Omnitech1/OTAP implementation work; preserve its own lifecycle and repository.
- `omniversal-kernel`: existing multi-domain integration concept; inspect and reconcile components before reuse.
- `OmniMind-OSS`: potential reusable open-source core; inspect licensing, tests, dependency health, and implementation before adopting.
- `scrollverse-web-app`: portal and visitor experience; do not expose internal credentials or unrestricted tools.
- GitHub is source and review infrastructure, not automatic access to every external AI platform's private conversation history.

No repository is merged, moved, centralized, or made a dependency merely by being listed here. Each integration needs a scoped adapter, explicit permission, and test evidence.

## 4. Build sequence

### Stage A — Foundation (this branch)
- Independent identity profile and system-instruction baseline.
- Capability/autonomy matrix.
- Default-deny policy gate.
- Hash-linked provenance ledger.
- Unit tests.
- Research, case study, manuscript, podcast, and digital collectible concept.
- No model calls, production changes, external side effects, or minting.

### Stage B — Private local prototype
- Add a provider adapter behind an interface.
- Use synthetic data and local-only memory.
- Add retrieval with source citations.
- Add input/output schemas, cost limits, timeout, and rate limits.
- Run evaluation suite and prompt-injection tests.

### Stage C — Controlled staging
- Separate staging credentials and environment.
- Shared rate limiting and trusted-proxy validation.
- Strict CORS/origin allowlist.
- Approved embed origins.
- Visitor experience tests.
- No production activation.

### Stage D — Federated pilot
- Register each participating agent with owner, endpoint, public identity key, capabilities, scopes, home repository, and version.
- Use signed messages, timestamps, nonce/replay protection, and correlation IDs.
- Permit only named message types and explicitly mapped data.
- Preserve independent opt-out and revocation.

### Stage E — Production candidate
- Independent security review, privacy review, accessibility review, disaster recovery exercise, and human sign-off.
- Deployment is a separate authorization and must have a release receipt.


### Stage C — Agent 25 staging configuration already selected

Carry forward the previously selected staging choices without changing production:
- Hosting target: Vercel for the isolated Agent 25 staging environment only.
- AI provider: OpenAI.
- Store provider key, selected model, provider endpoint, and production hostname allowlist in the hosting secret manager; never commit values to Git.
- Enforce shared rate limiting across instances and validate trusted-proxy configuration before trusting forwarded client IP headers.
- Enforce strict CORS and origin restrictions; allow only approved embed origins and the exact staging hostnames.
- Test the visitor experience in isolated staging with synthetic or minimized data.
- Production activation remains disabled.

The endpoint, model identifier, exact hostname allowlist, approved embed origins, and secret values were not present in the reviewed project context. Keep these as configuration prerequisites rather than inventing them. This staging choice does not make Vercel a dependency of OMNITECH1's independent core architecture.

## 5. Model adapter contract

```text
generate(messages, context, limits) -> ModelResponse
ModelResponse:
  provider
  model
  model_version
  response
  usage
  finish_reason
  request_id
```

Never bind project identity to one model provider. Provider selection must be configurable, observable, and replaceable.

## 6. Evidence states

Use separate labels: DOCUMENTED, IMPLEMENTED, TESTED, VERIFIED, STAGED, DEPLOYED, ACTIVE. A branch commit establishes a repository artifact, not a running AI. A successful CI job establishes only the checks actually run. A preview is not production.


## 7. Implemented runtime modules — follow-on foundation

The next implementation branch adds the following provider-neutral primitives:

- Model adapter: configurable OpenAI-compatible endpoint/model, exact hostname allowlist, HTTPS enforcement, bounded request size/temperature/token settings, sanitized errors, and no credential persistence.
- Source retrieval: explicit source manifest, public/private/session scope labels, local allowlist, path traversal protection, file-size/type restrictions, content hashes, lexical ranking, and line-level citations.
- Controlled memory: explicit consent for durable writes, ordinary project knowledge only, namespace separation, retention expiry, explicit deletion event, and provenance metadata.
- Agent 25 federation: canonical HMAC-authenticated envelopes, per-peer key lookup, recipient/type/time/size validation, persistent nonce replay guard, and TLS-required transport boundary.
- Staging gate: validates required provider, origin, Redis TLS, trusted-proxy and peer configuration without deploying or printing secret values.
- Adversarial tests: provider allowlist, retrieval scope/path traversal, memory consent/deletion/secret rejection, message authentication/replay/tampering, and staging fail-closed behavior.

These modules are implemented on the follow-on feature branch. Their GitHub Actions result is pending until the pull request workflow completes. No provider credentials, Agent 25 peer key, network endpoint, or hosting environment has been connected.


### GitHub source adapter

The follow-on runtime also includes a read-only GitHub Contents API adapter. It accepts a host-injected token, restricts requests to an explicit repository/ref/path allowlist, fetches only individual file contents, and returns the Git blob SHA separately from the raw-file SHA-256. The public visitor allowlist is a snapshot of 95 public repositories; the one private repository returned by the connected owner inventory is excluded. The current default path prefixes are README.md, docs, agents, and .github. This is a navigation/source adapter, not a bulk mirror of every repository or a claim that all files have been indexed.

For private owner knowledge, use a separate private deployment manifest and credentials with read-only scopes. Never place private repository names, private conversation exports, or secrets in the public catalog.


### Shared visitor edge controls

- Shared rate limiting is implemented as an atomic Redis sliding-window limiter. It hashes visitor identifiers with a secret pepper before creating Redis keys.
- Exact HTTPS origin matching is implemented as a reusable origin policy. Wildcards, credential-bearing origins, non-HTTPS origins, paths, queries, and fragments are rejected.
- Staging validation requires a TLS Redis URL, explicit rate-limit enablement, a secret pepper, exact origins, and an observed trusted-proxy hop count.
- The host application must still wire these controls into the visitor request path and configure Redis securely. Unit tests do not establish a deployed Redis service or runtime enforcement.
