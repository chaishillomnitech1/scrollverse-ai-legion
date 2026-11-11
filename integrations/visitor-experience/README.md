# Agent 25 Omni — Visitor Integration

The visitor pilot is being developed in the ScrollVerse Platform repository on branch `agent25/visitor-pilot`.

## Embed after staging approval
Once the platform is deployed to a staging host and frame policy is configured, add this to an approved public page:

```html
<script
  src="https://YOUR-STAGING-HOST/agent25-embed.js"
  data-site-id="scrollverse"
  defer
></script>
```

Use `scrollatlas` or `omnitech1` for the other registered site IDs. Do not use a production host until the owner approves the staging test and deployment.

## Required server-side environment
- `AGENT25_API_URL`: HTTPS OpenAI-compatible chat-completions endpoint.
- `AGENT25_API_KEY`: secret stored only in the hosting provider's environment settings.
- `AGENT25_MODEL`: provider-supported model identifier.
- `AGENT25_ALLOWED_EMBED_ORIGINS`: comma-separated exact HTTPS origins approved for iframe embedding (configure CSP/frame-ancestors at the host).

The pilot never reads `BUILT_IN_FORGE_API_KEY` and does not call the Manus Forge endpoint.

## Current limitations
- Visitor Q&A is informational and stateless.
- It has no access to private files, private repositories, visitor accounts, wallets, payment systems, or production controls.
- The initial site registry is partial; artifact retrieval is not yet connected.
- The runtime selects one specialist role per turn. It does not represent 25 independent always-on model processes.
- A memory-backed rate limiter is suitable only for a single-process pilot; use a shared rate limiter before scaling horizontally.
- Test one staging domain first. Add the remaining site embeds only after explicit owner approval.
