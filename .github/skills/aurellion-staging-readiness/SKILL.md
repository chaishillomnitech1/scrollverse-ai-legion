---
name: aurellion-staging-readiness
description: Assess or prepare an isolated AURELLION and Agent 25 staging environment with fail-closed configuration, rate limiting, trusted-proxy checks, and origin restrictions.
---

# AURELLION Isolated Staging Readiness

## Prerequisites
- Dedicated non-production hosting project and environment.
- Selected provider, model, HTTPS endpoint, exact provider-host allowlist, and secret-manager credential.
- Shared TLS-enabled Redis/Upstash rate-limit store.
- Exact staging hostname and approved embed-origin allowlist.
- Trusted proxy hop count verified from the actual ingress path.
- Agent 25 peer identity and unique peer secret provisioned securely.
- CI and adversarial evaluation results accepted.
- Synthetic or minimized test data and a documented rollback/kill switch.

## Workflow
1. Inspect current code and environment metadata without reading secret values.
2. Run unit, integration, adversarial, type, build, and visitor smoke tests as applicable.
3. Validate configuration using agents/aurellion/runtime/staging_gate.py.
4. Confirm shared rate limiting, exact CORS/embed origins, CSP, proxy trust, and abuse controls.
5. Deploy only to isolated staging after explicit approval naming the target project and environment.
6. Test visitor behavior, isolation, errors, rate limits, provider failure, key revocation, and rollback.
7. Record deployment ID, URL, commit, environment, test evidence, and reviewer.

## Boundaries
- No production activation.
- Never print or commit secrets.
- Do not infer correct proxy hops without observing the ingress path.
- A configuration pass is not a deployment or runtime test.
