# GOD MODE AGENT 25 OMNI — Architecture & Integration Blueprint

**Status:** Design and pilot scaffold. This document does not claim that 25 independent autonomous services are deployed.

## Purpose
A human-directed multi-agent architecture for the ScrollVerse ecosystem. Agent 00 is the master orchestrator; Agents 01–25 are specialist roles. A shared model endpoint can execute a selected role in the visitor pilot. That is a role-based pilot, not 25 independently running model processes.

## Six operating pillars
1. COMPLETE — discover and progress unfinished work.
2. PRESERVE — retain original files, conversations, and provenance.
3. CONNECT — map sites, repositories, and artifacts.
4. VERIFY — distinguish claims from reproducible evidence.
5. ACTIVATE — create useful visitor, creator, and learning experiences.
6. PROTECT — preserve production, privacy, IP, and credentials.

## Architecture
Human owner → Agent 00 → permission and task gateway → specialist registry (01–25) → evidence/knowledge registry → approved connectors → reports and visitor responses.

### Agent execution model
- Every task carries an agent ID, task ID, permitted sources, allowed tools, and expected output.
- Visitor chat is read-only and informational.
- Specialist selection is deterministic in the first pilot. Each visitor turn invokes one specialist role through a server-side, OpenAI-compatible model endpoint.
- No agent can execute arbitrary shell commands, write to repositories, deploy, spend money, sign transactions, or access private archives.
- Multi-agent deliberation, durable jobs, and independent workers are later phases requiring separate evaluation and explicit resource approval.

## Existing AI Legion compatibility
The existing `agents/legion-manifest.json` describes 12 legacy AI entities. This new `agents/agent25-omni/manifest.json` adds a separate 25-role operations architecture. It does not overwrite, rename, or silently reclassify the 12 legacy entities. The two catalogs can be mapped later with owner review.

## Visitor-facing experience
The pilot lives in `chaishillomnitech1/scrollverse-platform` on branch `agent25/visitor-pilot`. It adds a floating chat interface and an embeddable iframe loader. It requires a separately configured server-side model endpoint and key:
- `AGENT25_API_URL`
- `AGENT25_API_KEY`
- `AGENT25_MODEL`

The pilot deliberately does not fall back to the existing Manus Forge key or consume Manus credits. Without these settings, the chat reports that it is not configured.

## Initial public site registry
See `registry/empire-sites.json`. It is a starting index, not a complete list of every site, route, artifact, or repository. Site ownership and live status are owner-reported unless separately verified.

## Production safety
- Production write access: disabled.
- Automatic deployments: disabled.
- Manus commands: disabled.
- Visitor-triggered tools: disabled.
- Visitor access to private files, credentials, wallet data, or account records: prohibited.
- New code stays on feature branches and is proposed by pull request.
- No DNS, domain, production database, wallet, contract, payment, or deployment changes.
- No public release before human review and configuration of allowed embed origins.

## Evidence labels
`USER_REPORTED`, `SOURCE_OBSERVED`, `INDEPENDENTLY_VERIFIED`, `BLUEPRINT`, `IN_PROGRESS`, `UNKNOWN`.

## Phased rollout
1. Preserve and review the existing 12-entity catalog.
2. Merge the 25-role registry and architecture docs after review.
3. Configure a separate model provider key outside Git.
4. Run local tests and security checks.
5. Deploy only to a staging environment.
6. Validate the visitor widget on one pilot domain.
7. Expand the site registry and add embed snippets to each approved site.
8. Add artifact retrieval only from an explicitly indexed, public-safe catalog.
9. Conduct owner-approved production rollout.

## Definition of "active"
An agent role is **defined** when its manifest and task contract exist; **runnable** when the runtime can invoke it; **connected** when it has approved source access; **verified** when reproducible tests pass; and **production-active** only after authorized deployment and live checks. These states must never be conflated.
